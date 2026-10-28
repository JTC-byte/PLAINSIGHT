"""A minimal, read-only DOSSIER: the four layer bands about one focus node.

The bands are stacked as docs/PLAINSIGHT-design.md section 3.1 stacks them,
STATE at the top and OBSERVATION at the bottom, so reading down walks the
lineage backwards. Every row carries the event its lineage starts from.

- STATE: the sentences that cite the focus or a cluster it is a member of.
  Each sentence carries a consequence line for every event its lineage cites
  that no longer stands as it did: a cluster or proposal an ADJUDICATE REVOKE
  withdrew, a claim an analyst disputed, and a proposal no analyst accepted.
- FUSION: for a focus that is a cluster, the cluster itself; otherwise the
  clusters the focus is a member of. Each member's seams are printed per member
  and never rolled up, and a revoked cluster is kept as a tombstone.
- INFERENCE: the proposals touching the focus, every one unaccepted.
- OBSERVATION: the claims observed about the focus, each with a provenance line
  of facts only: selector type, extractor, time provenance, review state, and
  the "does not vouch" tokens.

No count, score or band is computed here. A band word is printed as the
analyst recorded it.
"""

from __future__ import annotations

from app.model import reads
from app.model.web import describe_edges, describe_nodes
from app.refusals import Refusal


def build(conn, case_id: str, focus: str | None) -> dict:
    if not focus:
        raise Refusal("FOCUS_REQUIRED")
    focus_row = reads.node(conn, focus)
    if focus_row is None:
        raise Refusal("NODE_NOT_IN_CASE", "route: dossier")
    edges = [dict(r) for r in conn.execute(
        "SELECT * FROM edge WHERE src_id = ? OR dst_id = ? ORDER BY edge_id", (focus, focus)
    )]
    ids = {focus} | {e["src_id"] for e in edges} | {e["dst_id"] for e in edges}
    rows = reads.nodes(conn, ids)
    described = {n["node_id"]: n for n in describe_nodes(conn, case_id, rows, edges)}
    edge_text = {e["edge_id"]: e for e in describe_edges(conn, case_id, edges, rows)}
    reviews = reads.review_states(conn, case_id)

    fusion = []
    cluster_ids = clusters_for(focus_row, edges)
    for cid in cluster_ids:
        members = [dict(r) for r in conn.execute(
            "SELECT * FROM edge WHERE kind = 'member_of' AND dst_id = ? ORDER BY edge_id", (cid,)
        )]
        fusion.append({
            "cluster_id": cid,
            "lineage": rows[cid]["created_by_event_id"],
            "lines": described[cid]["lines"],
            "tombstone": bool(rows[cid]["revoked_by_event_id"]),
            "members": [
                {"node_id": m["src_id"], "seams": m["label"] or "none recorded", "edge_id": m["edge_id"]}
                for m in members
            ],
        })

    inference = [
        {
            "edge_id": e["edge_id"],
            "other": e["dst_id"] if e["src_id"] == focus else e["src_id"],
            "text": edge_text[e["edge_id"]]["text"],
            "lineage": e["event_id"],
        }
        for e in edges
        if e["kind"] == "proposes"
    ]

    observation = []
    for e in edges:
        if e["kind"] != "observed_about" or e["dst_id"] != focus:
            continue
        claim = conn.execute("SELECT * FROM claim WHERE claim_id = ?", (e["event_id"],)).fetchone()
        if claim is None:
            observation.append({"claim_id": e["event_id"], "text": f"▨ chain broken at {e['event_id']}", "lineage": e["event_id"]})
            continue
        sel = described.get(e["src_id"]) or {}
        prefix = "~" if claim["provenance_state"] == "GENERATED" else ""
        observation.append({
            "claim_id": claim["claim_id"],
            "node_id": e["src_id"],
            "selector_type": claim["selector_type"],
            "value": prefix + claim["value"],
            "generated": bool(prefix),
            "provenance": " · ".join([
                f"extracted by {claim['extractor']}",
                f"time {claim['time_provenance']}",
                reads.review_text(reviews.get(claim["claim_id"])),
                RELATION_LINE,
            ]),
            "vouch_tokens": sel.get("vouch_tokens", []),
            "lineage": claim["claim_id"],
        })

    sentences = reads.sentences_by_node(conn, case_id)
    state_ids = list(dict.fromkeys(sentences.get(focus, []) + [s for c in cluster_ids for s in sentences.get(c, [])]))
    revoked = reads.revocations(conn, case_id)
    state = []
    for sid in state_ids:
        e = reads.event(conn, case_id, sid)
        p = (e or {}).get("payload") or {}
        state.append({
            "sentence_id": sid,
            "text": p.get("text"),
            "author": f"asserted {p.get('author') or (e or {}).get('producer')} {(e or {}).get('ts', '')[:10]}",
            "consequences": cited_consequences(conn, case_id, e, revoked, reviews),
            "lineage": sid,
        })

    return {
        "case_id": case_id,
        "focus": focus,
        "focus_lines": described[focus]["lines"],
        "focus_tokens": described[focus]["vouch_tokens"],
        "bands": [
            {"band": "STATE", "rows": state, "empty": "no sentence cites this focus"},
            {"band": "FUSION", "rows": fusion, "empty": "no analyst has asserted a cluster holding this focus"},
            {"band": "INFERENCE", "rows": inference, "empty": "no proposal touches this focus"},
            {"band": "OBSERVATION", "rows": observation, "empty": "no claim is observed about this focus"},
        ],
    }


RELATION_LINE = "relation unstated: EXTRACT CLAIM carries no predicate"


def clusters_for(focus_row, edges: list[dict]) -> list[str]:
    """The clusters FUSION shows: the focus itself when it is a cluster, else those it is a member of."""
    focus = focus_row["node_id"]
    if focus_row["kind"] == "cluster":
        return [focus]
    return [e["dst_id"] for e in edges if e["kind"] == "member_of" and e["src_id"] == focus]


def cited_consequences(conn, case_id: str, sentence: dict | None, revoked: dict, reviews: dict) -> list[str]:
    """One line per event a sentence's lineage cites that no longer stands as it did."""
    if sentence is None:
        return []
    p = sentence.get("payload") or {}
    refs = list(sentence.get("parents") or [])
    refs += [c.get("ref") for c in p.get("citations") or [] if isinstance(c, dict)]
    out = []
    for ref in dict.fromkeys(r for r in refs if reads.is_uuid(r)):
        cited = reads.event(conn, case_id, ref)
        if cited is None:
            continue
        short = ref[:8]
        withdrawn = revoked.get(ref)
        if withdrawn is not None and cited["type"] == "LINK_EVENT":
            out.append(f"cites withdrawn proposal {short}: " + reads.revoked_text(withdrawn, "that inference"))
        elif withdrawn is not None:
            out.append(f"cites revoked {cited['subtype'].lower()} {short}: " + reads.revoked_text(withdrawn, "that assertion"))
        elif cited["type"] == "LINK_EVENT":
            out.append(f"cites proposal {short}, which no analyst has accepted")
        review = reviews.get(ref)
        if review is not None and review["subtype"] == "DISPUTE":
            out.append(f"cites claim {short}, which is " + reads.review_text(review))
    return out
