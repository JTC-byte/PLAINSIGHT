"""The WEB view's model: one case, one focus, a bounded number of hops.

Every web is case-scoped and focused (docs/PLAINSIGHT-design.md section 8.4,
CUT LIST A: there is no global graph). The node set is every node reachable from
the focus over the edge table in at most `hops` steps, either direction, and the
edge set is every edge whose two ends are both in that node set.

WEB_MAX_NODES and WEB_MAX_EDGES are constants that no query parameter can raise
(section 8.5, amendment 9.7). They are checked before layout. Over either cap no
SVG is drawn, and the view serves the list twin and PATHS instead.

Nothing here computes a weight, a size, a thickness, an opacity, a score or a
percentage. A node's text is a set of facts, each rendered as its consequence
(CLAUDE.md section 4): "inert · nothing has been collected against this node",
"anchor unproven", "past retain_until".
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.model import reads, sectors
from app.refusals import Refusal

#: The canvas cap. A pin test asserts both values; nothing raises them.
WEB_MAX_NODES = 300
WEB_MAX_EDGES = 600

HOPS_DEFAULT = 2
HOPS_MIN = 1
HOPS_MAX = 3

#: Above this many nodes, sectors other than the expanded one collapse to cards.
#: The number compared is the length of the already-capped in-memory node list,
#: never a COUNT over the case.
SECTOR_COLLAPSE_AT = 50

#: Entity type chips: two characters, achromatic, beside the anchor line.
TYPE_CHIPS = {
    "Account": "ac",
    "Channel": "ch",
    "Org": "og",
    "Place": "pl",
    "Media": "md",
    "PersonCandidate": "pc",
    "ManualTask": "mt",
}

INERT = "inert · nothing has been collected against this node"
REFERENCED = "referenced, never promoted in this case: no observation held"
RELATION_UNSTATED = "relation unstated"


@dataclass
class Web:
    case_id: str
    focus: str
    hops: int
    sector: str | None
    ring: dict[str, int]
    nodes: list[dict] = field(default_factory=list)
    edges: list[dict] = field(default_factory=list)
    over_cap: bool = False
    collapsed: dict[str, int] = field(default_factory=dict)

    @property
    def n_nodes(self) -> int:
        return len(self.ring)


def over_cap(node_ids, edge_ids) -> bool:
    """True when either list passes its cap. Takes any sized collections."""
    return len(node_ids) > WEB_MAX_NODES or len(edge_ids) > WEB_MAX_EDGES


def cap_text(n_nodes: int, n_edges: int) -> str:
    """The cap sentence. The cap counts the whole hop neighbourhood, so only fewer hops
    bring the canvas under it; a sector narrows the list twin, never the canvas."""
    tail = "narrow by hop to draw the canvas; a sector narrows the list twin"
    if n_nodes > WEB_MAX_NODES:
        return f"this web has {n_nodes} nodes; the canvas draws at most {WEB_MAX_NODES}; {tail}"
    return f"this web has {n_edges} edges; the canvas draws at most {WEB_MAX_EDGES}; {tail}"


# ---------------------------------------------------------------------------
# the neighbourhood
# ---------------------------------------------------------------------------


def incident_edges(conn, ids) -> list[dict]:
    """Every edge with either end in `ids`, in edge_id order."""
    ids = list(ids)
    out: dict[str, dict] = {}
    for i in range(0, len(ids), 400):
        chunk = ids[i:i + 400]
        marks = ", ".join("?" for _ in chunk)
        for r in conn.execute(
            f"SELECT * FROM edge WHERE src_id IN ({marks}) OR dst_id IN ({marks})", chunk + chunk
        ):
            out[r["edge_id"]] = dict(r)
    return [out[k] for k in sorted(out)]


def neighbourhood(conn, focus: str, hops: int) -> tuple[dict[str, int], list[dict]]:
    """({node id: ring}, edges with both ends in the node set). Breadth first, both directions."""
    ring = {focus: 0}
    frontier = [focus]
    for depth in range(1, hops + 1):
        nxt = []
        for e in incident_edges(conn, frontier):
            for end in (e["src_id"], e["dst_id"]):
                if end not in ring:
                    ring[end] = depth
                    nxt.append(end)
        frontier = sorted(nxt)
        if not frontier:
            break
    edges = [e for e in incident_edges(conn, ring) if e["src_id"] in ring and e["dst_id"] in ring]
    return ring, edges


# ---------------------------------------------------------------------------
# node and edge text
# ---------------------------------------------------------------------------


def _cluster_text(conn, case_id, node_row) -> list[str]:
    created = reads.event(conn, case_id, node_row["created_by_event_id"])
    p = (created or {}).get("payload") or {}
    who = p.get("asserted_by") or (created or {}).get("producer") or "an unrecorded analyst"
    day = (created or {}).get("ts", "")[:10]
    lines = [f"asserted {who} {day} · {p.get('band') or 'no band recorded'}"]
    if node_row["revoked_by_event_id"]:
        rev = reads.event(conn, case_id, node_row["revoked_by_event_id"])
        rp = (rev or {}).get("payload") or {}
        rwho = rp.get("analyst") or (rev or {}).get("producer") or "an unrecorded analyst"
        lines.append(f"REVOKED by {rwho} {(rev or {}).get('ts', '')[:10]}: this assertion no longer stands")
    return lines


def _candidate_text(conn, case_id, node_row) -> list[str]:
    created = reads.event(conn, case_id, node_row["created_by_event_id"])
    p = (created or {}).get("payload") or {}
    who = p.get("asserted_by") or (created or {}).get("producer") or "an unrecorded analyst"
    lines = [f"EXCLUDED by {who} {(created or {}).get('ts', '')[:10]}: asserted not the subject"]
    if p.get("basis"):
        lines.append(f"basis: {p['basis']}")
    return lines


def describe_nodes(conn, case_id: str, rows: dict[str, dict], web_edges: list[dict]) -> list[dict]:
    """The text, tokens and lineage heads of each node, in node_id order."""
    collect = reads.collect_decisions(conn, case_id)
    sentences = reads.sentences_by_node(conn, case_id)
    controls_dst = {e["dst_id"] for e in web_edges if e["kind"] == "proposes" and e["label"] == "controls"}
    entity_ids = {nid for nid, r in rows.items() if r["kind"] == "entity"}
    out = []
    for nid in sorted(rows):
        r = rows[nid]
        claims = reads.claims_holding(conn, r)
        claim_ids = {c["claim_id"] for c in claims}
        lines: list[str] = []
        tokens: list[str] = []
        generated = False
        if r["kind"] == "selector":
            sel = r["selector_type"]
            generated = any(c["provenance_state"] == "GENERATED" for c in claims)
            value = claims[0]["value"] if claims else None
            lines.append(sel)
            if value is not None:
                lines.append(("~" if generated else "") + value)
            shared = {e["dst_id"] for e in web_edges if e["kind"] == "observed_about" and e["src_id"] == nid and e["dst_id"] in entity_ids}
            if len(shared) >= 2:
                lines.append(f"same value observed on {len(shared)} accounts")
            items = [reads.item_of_claim(conn, c) for c in claims]
            if any(i is None or i["blob_state"] != "held" for i in items):
                tokens.append("raw not held")
        elif r["kind"] == "entity":
            chip = TYPE_CHIPS.get(r["entity_type"], (r["entity_type"] or "??")[:2].lower())
            head = f"{chip} {r['entity_type']}"
            if r["entity_type"] == "Org" and nid in controls_dst:
                head = "org · CONTROLS proposed"
            lines.append(head)
            if r["anchor_vouched"]:
                lines.append(f"anchor {r['anchor_selector_type']}")
            else:
                anchor = conn.execute(
                    "SELECT selector_type FROM claim WHERE claim_id = ?", (r["anchor_claim_id"],)
                ).fetchone()
                found = anchor["selector_type"] if anchor else "absent"
                lines.append(
                    f"anchor declared {r['anchor_selector_type']}, anchor claim is a {found}, anchor unproven"
                )
                tokens.append("anchor unproven")
            promote = reads.event(conn, case_id, r["created_by_event_id"])
            target = ((promote or {}).get("payload") or {}).get("target_ref")
            item = conn.execute("SELECT blob_state FROM item WHERE event_id = ?", (target,)).fetchone()
            if item is None or item["blob_state"] != "held":
                tokens.append("raw not held")
        elif r["kind"] == "referenced":
            lines.append(REFERENCED)
        elif r["kind"] == "cluster":
            lines.extend(_cluster_text(conn, case_id, r))
        elif r["kind"] == "candidate":
            lines.extend(_candidate_text(conn, case_id, r))
        if reads.past(r["expires_at"]):
            tokens.append("past retain_until")
        dives = [e for e in collect if (e["payload"] or {}).get("motivated_by") in claim_ids]
        if dives:
            deep = "; ".join(reads.decision_text(e) for e in dives)
        else:
            deep = INERT
        heads = [c["claim_id"] for c in claims] if r["kind"] == "selector" else [r["created_by_event_id"]]
        out.append({
            "node_id": nid,
            "kind": r["kind"],
            "sector": r["sector"],
            "selector_type": r["selector_type"],
            "entity_type": r["entity_type"],
            "generated": generated,
            "revoked": bool(r["revoked_by_event_id"]),
            "lines": lines,
            "vouch_tokens": tokens,
            "deep_dive_state": deep,
            "sentences": sentences.get(nid, []),
            "lineage_heads": heads,
        })
    return out


def _proposal_text(conn, case_id, e, revoked: dict | None = None) -> str:
    """A proposal, consequence first, so a cut or a covered tail never hides "not accepted"."""
    link = reads.event(conn, case_id, e["event_id"])
    model = ((link or {}).get("payload") or {}).get("model") or {}
    who = f"{model.get('name') or e['actor']} {model.get('version') or ''}".strip()
    if revoked is not None:
        rwho = (revoked["payload"] or {}).get("analyst") or revoked["producer"]
        return (
            f"PROPOSAL WITHDRAWN by {rwho} {revoked['ts'][:10]}: this inference no longer stands "
            f"· was PROPOSED {e['label']} by {who}"
        )
    calibrated = "uncalibrated" if not model.get("calibration_ref") else "calibration recorded, not reviewed here"
    return f"NOT ACCEPTED, PROPOSED {e['label']} by {who}: no analyst has asserted this · {calibrated}"


def describe_edges(conn, case_id: str, edges: list[dict], rows: dict[str, dict]) -> list[dict]:
    out = []
    revoked = reads.revocations(conn, case_id) if any(e["kind"] == "proposes" for e in edges) else {}
    for e in sorted(edges, key=lambda x: x["edge_id"]):
        withdrawn = None
        if e["kind"] == "observed_about":
            text = f"{e['label']} · {RELATION_UNSTATED}"
        elif e["kind"] == "proposes":
            withdrawn = revoked.get(e["event_id"])
            text = _proposal_text(conn, case_id, e, withdrawn)
        elif e["kind"] == "member_of":
            text = f"member · seams {e['label'] or 'none recorded'}"
            cluster = rows.get(e["dst_id"])
            if cluster is not None and cluster["revoked_by_event_id"]:
                text += " · revoked with its cluster"
        else:
            text = "excludes: asserted not the subject"
        out.append({
            "edge_id": e["edge_id"],
            "kind": e["kind"],
            "layer": e["layer"],
            "label": e["label"],
            "src_id": e["src_id"],
            "dst_id": e["dst_id"],
            "actor": e["actor"],
            "ts": e["ts"],
            "event_id": e["event_id"],
            "withdrawn": withdrawn is not None,
            "text": text,
        })
    return out


# ---------------------------------------------------------------------------
# the web
# ---------------------------------------------------------------------------


def parse_hops(value) -> int:
    if value is None:
        return HOPS_DEFAULT
    hops = int(value)
    if not HOPS_MIN <= hops <= HOPS_MAX:
        raise ValueError("hops out of range")
    return hops


def build(conn, case_id: str, focus: str | None, hops: int = HOPS_DEFAULT, sector: str | None = None) -> Web:
    """The web around `focus`. Refuses an unfocused request and a focus the case does not hold."""
    if not focus:
        raise Refusal("FOCUS_REQUIRED")
    if reads.node(conn, focus) is None:
        raise Refusal("NODE_NOT_IN_CASE", "route: web")
    ring, edges = neighbourhood(conn, focus, hops)
    web = Web(case_id, focus, hops, sector, ring)
    if over_cap(ring, edges):
        web.over_cap = True
        web.edges = edges
        return web
    rows = reads.nodes(conn, ring)
    if len(rows) > SECTOR_COLLAPSE_AT:
        keep = {focus}
        for nid, r in rows.items():
            if r["sector"] is not None and r["sector"] == sector:
                keep.add(nid)
            elif r["sector"] is None:
                keep.add(nid)
        for nid, r in rows.items():
            if nid not in keep:
                web.collapsed[r["sector"]] = web.collapsed.get(r["sector"], 0) + 1
        rows = {k: v for k, v in rows.items() if k in keep}
        edges = [e for e in edges if e["src_id"] in rows and e["dst_id"] in rows]
    web.nodes = describe_nodes(conn, case_id, rows, edges)
    for n in web.nodes:
        n["ring"] = ring[n["node_id"]]
    web.edges = describe_edges(conn, case_id, edges, rows)
    return web


def collapsed_cards(web: Web) -> list[dict]:
    return [
        {"sector": s, "text": f"{sectors.LABELS.get(s, s)} {n} · open as list"}
        for s, n in sorted(web.collapsed.items())
    ]


def list_twin(conn, case_id: str, focus: str | None, hops: int, sector: str | None = None) -> dict:
    """The keyboard and screen-reader form of the web, and its fallback past the cap."""
    if not focus:
        raise Refusal("FOCUS_REQUIRED")
    if reads.node(conn, focus) is None:
        raise Refusal("NODE_NOT_IN_CASE", "route: web.list")
    ring, edges = neighbourhood(conn, focus, hops)
    rows = reads.nodes(conn, ring)
    if sector is not None:
        rows = {k: v for k, v in rows.items() if v["sector"] == sector or k == focus}
        edges = [e for e in edges if e["src_id"] in rows and e["dst_id"] in rows]
    nodes = describe_nodes(conn, case_id, rows, edges)
    for n in nodes:
        n["ring"] = ring[n["node_id"]]
    nodes.sort(key=lambda n: (n["ring"], n["sector"] or "~", n["selector_type"] or n["kind"], n["node_id"]))
    return {
        "mode": "list",
        "case_id": case_id,
        "focus": focus,
        "hops": hops,
        "sector": sector,
        "nodes": nodes,
        "edges": describe_edges(conn, case_id, edges, rows),
    }
