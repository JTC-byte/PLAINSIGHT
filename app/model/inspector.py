"""The INSPECTOR for one node, and the Pivot Bar's read-only pre-flight.

Selecting a node fills the INSPECTOR and nothing else happens: every node is
inert (doctrine/SUBJECT_SELECTION.md SS-16). The pre-flight that p opens shows
what a deep dive on this one node would be, as consequences:

- the target selector type, which for an entity is its anchor's type only when
  the anchor is vouched; an unproven anchor names no target and says so;
- the motivating claim, and a line saying so when that claim is disputed;
- the proposed pivot_depth against the pivot_depth_max of the authorization in
  force, or why no authorization is in force;
- the capability rows connector manifests declare for that selector type;
- for a person who is not yet a subject, the SS-16 line that their own
  authorization record must exist before anything is collected.

The pre-flight records nothing. Dispatch is the deep-dive route's, and that
route refuses until the subject gate is connected to it (app/http/acts.py).
"""

from __future__ import annotations

import yaml

from app import config
from app.model import reads, sectors
from app.model.web import describe_edges, describe_nodes
from app.refusals import Refusal
from app.store import retention

CONNECTORS = config.REPO_ROOT / "connectors"

SS16_LINE = (
    "SS-16: this person is not yet a subject, so their own authorization record and class must "
    "exist before anything is collected against them"
)


def _consumed(manifest: dict) -> set[str]:
    out = set()
    consumes = manifest.get("consumes") or {}
    for part in ("required", "optional"):
        for item in consumes.get(part) or []:
            if isinstance(item, str):
                out.add(item)
            elif isinstance(item, dict):
                for key in ("selector", "selector_type", "type"):
                    if isinstance(item.get(key), str):
                        out.add(item[key])
    return out


def capability_rows(selector_type: str | None) -> list[str]:
    """One row per capability that a manifest under connectors/ declares for the selector type."""
    if not selector_type:
        return []
    rows: dict[str, list[str]] = {}
    for path in sorted(CONNECTORS.glob("*/manifest.yaml")):
        try:
            manifest = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except (OSError, yaml.YAMLError):
            continue
        if selector_type in _consumed(manifest):
            rows.setdefault(str(manifest.get("capability")), []).append(str(manifest.get("id")))
    return [f"{cap}: {', '.join(sorted(ids))}" for cap, ids in sorted(rows.items())]


NOT_DISPATCHED_LINE = "NOT DISPATCHED until the subject gate is connected to this route: this pre-flight records nothing"


def preflight(conn, case_id: str, row, claims: list[dict]) -> dict:
    lines = []
    if row["kind"] == "selector":
        target = row["selector_type"]
    elif row["kind"] == "entity" and row["anchor_vouched"]:
        target = row["anchor_selector_type"]
    elif row["kind"] == "entity":
        target = None
        lines.append(
            f"anchor unproven: the declared type {row['anchor_selector_type']} is not held on this node, "
            "so a deep dive has no target until a claim of that type anchors it"
        )
    else:
        target = None
    motivating = claims[0] if claims else None
    if target is None and row["kind"] != "entity":
        lines.append("no selector type is held on this node, so a deep dive has nothing to run against yet")
    if motivating is not None:
        review = reads.review_states(conn, case_id).get(motivating["claim_id"])
        if review is not None and review["subtype"] == "DISPUTE":
            lines.append(
                f"motivating claim {motivating['claim_id'][:8]} is disputed: resolve the dispute before a deep dive cites it"
            )
    authorization = None
    if motivating is not None:
        run = conn.execute("SELECT authorization_ref FROM run WHERE run_id = ?", (motivating["run_id"],)).fetchone()
        authorization = run["authorization_ref"] if run else None
    acts = reads.authorizations(conn, case_id).get(authorization, []) if authorization else []
    proposed = (motivating["pivot_depth"] or 0) + 1 if motivating is not None else None
    if motivating is None:
        lines.append("no claim holds this node, so no motivating claim can be named")
    elif not acts:
        lines.append("no authorization is recorded for the run behind this claim, so nothing may be collected")
    else:
        state = reads.authorization_state(acts)
        ref = authorization[:8]
        if state["revoked"] is not None:
            lines.append(
                f"proposed pivot_depth {proposed}; authorization {ref} was revoked {state['revoked']['ts']}, "
                f"so no authorization is in force for this pivot (its last pivot_depth_max was {state['pivot_depth_max']})"
            )
        elif state["expired"]:
            lines.append(f"proposed pivot_depth {proposed}; authorization {ref} expired {state['expires_on']}, so none is in force")
        elif state["pivot_depth_max"] is not None and proposed > state["pivot_depth_max"]:
            lines.append(
                f"proposed pivot_depth {proposed} exceeds pivot_depth_max {state['pivot_depth_max']} of "
                f"authorization {ref}: an EXTEND is needed first"
            )
        else:
            lines.append(f"proposed pivot_depth {proposed} is within pivot_depth_max {state['pivot_depth_max']} of authorization {ref}")
    caps = capability_rows(target)
    if target is not None and not caps:
        lines.append(f"no manifest declares a capability for selector type {target}")
    if row["kind"] in ("referenced", "candidate"):
        lines.append(SS16_LINE)
    lines.append(NOT_DISPATCHED_LINE)
    return {
        "target_selector_type": target,
        "motivating_claim": motivating["claim_id"] if motivating else None,
        "proposed_pivot_depth": proposed,
        "capabilities": caps,
        "lines": lines,
    }


def inspect(conn, case_id: str, node_id: str) -> dict:
    row = reads.node(conn, node_id)
    if row is None:
        raise Refusal("NODE_NOT_IN_CASE", "route: node")
    edges = [dict(r) for r in conn.execute(
        "SELECT * FROM edge WHERE src_id = ? OR dst_id = ? ORDER BY edge_id", (node_id, node_id)
    )]
    ids = {node_id} | {e["src_id"] for e in edges} | {e["dst_id"] for e in edges}
    rows = reads.nodes(conn, ids)
    described = describe_nodes(conn, case_id, {node_id: dict(row)}, edges)[0]
    claims = reads.claims_holding(conn, row)
    reviews = reads.review_states(conn, case_id)
    claim_rows = []
    for c in claims:
        item = reads.item_of_claim(conn, c)
        expiry = (
            f"past retain_until: this claim's reading expired {c['expires_at']}"
            if reads.past(c["expires_at"])
            else f"expires {c['expires_at']}, a reading: policy/retention.yaml is unratified"
        )
        claim_rows.append({
            "claim_id": c["claim_id"],
            "selector_type": c["selector_type"],
            "value": ("~" if c["provenance_state"] == "GENERATED" else "") + c["value"],
            "generated": c["provenance_state"] == "GENERATED",
            "item_id": c["item_id"],
            "run_id": c["run_id"],
            "relation": f"subject_relation {c['subject_relation']} at pivot_depth {c['pivot_depth']}, copied from the gate's decision",
            "review": reads.review_text(reviews.get(c["claim_id"])),
            "raw": "raw bytes held" if item is not None and item["blob_state"] == "held" else "raw bytes not held",
            "expiry": expiry,
        })
    unattached = [
        {"event_id": e["event_id"], "text": reads.decision_text(e)}
        for e in reads.collect_decisions(conn, case_id)
        if e["subtype"] in ("REQUIRES_EXTENSION", "REFUSED") and not (e["payload"] or {}).get("motivated_by")
    ]
    reg = conn.execute("SELECT * FROM case_registry WHERE case_id = ?", (case_id,)).fetchone()
    return {
        "case_id": case_id,
        "node": described,
        "sector_label": sectors.LABELS.get(row["sector"]) if row["sector"] else "FUSION",
        "edges": describe_edges(conn, case_id, edges, rows),
        "claims": claim_rows,
        "pivot": preflight(conn, case_id, row, claims),
        "unattached_decisions": unattached,
        "retention": retention.retention_line(reg) if reg else None,
    }
