"""The Lineage Drawer's model: the chain behind an event, and what depends on it.

Tier 1 is the chain, walked back over parents_json with WITH RECURSIVE:
sentence, cluster or tombstone, LINK, claim, item, RUN_START, COLLECT PERMITTED,
then the authorization's GRANT, EXTEND and REVOKE (amendment 9.9). Tier 2 is
the decoded envelope. Tier 3 is RAW, which reads "not held" on LOCAL.

A missing link renders "▨ chain broken at <event_id>" and the walk stops on that
branch; it never skips. A link is missing when the parent is not in the log, or
when the projection row the chain passes through (claim, item, run) is gone.

Flags render as consequences and never refuse, because chain rules belong to
the gate (VA-U1): a decision recorded after its authorization was revoked, an
authorization past its expires_on, and a chain that cites a cluster or a
proposal an ADJUDICATE REVOKE has withdrawn. A withdrawn cluster or LINK also
carries its REVOKED line in its own entry, so the tombstone names who asserted
and who revoked (design section 5.6).

RAW carries raw_vouch beside its text. It is true only when the item's bytes are
not held, which is the one RAW state the system does not vouch for; the client
paints red and the hatch from that flag and never from the text.

The drawer shows argv_template and never a filled argv (contract section 6).
"""

from __future__ import annotations

from app.model import reads
from app.refusals import Refusal
from app.store import blobs, envelope

BROKEN = "▨ chain broken at {}"
MAX_DEPTH = 12

WALK_BACK = """
WITH RECURSIVE walk(event_id, depth, child) AS (
    SELECT ?, 0, NULL
    UNION
    SELECT j.value, w.depth + 1, w.event_id
    FROM walk w
    JOIN event_skeleton s ON s.event_id = w.event_id AND s.case_id = ?
    JOIN json_each(COALESCE(s.parents_json, '[]')) j
    WHERE w.depth < ?
)
SELECT event_id, MIN(depth) AS depth, MIN(child) AS child FROM walk GROUP BY event_id ORDER BY depth, event_id
"""

WALK_FORWARD = """
WITH RECURSIVE walk(event_id, depth) AS (
    SELECT ?, 0
    UNION
    SELECT s.event_id, w.depth + 1
    FROM walk w
    JOIN event_skeleton s ON s.case_id = ? AND s.parents_json IS NOT NULL
    WHERE w.depth < ? AND EXISTS (SELECT 1 FROM json_each(s.parents_json) j WHERE j.value = w.event_id)
)
SELECT event_id, MIN(depth) AS depth FROM walk GROUP BY event_id ORDER BY depth, event_id
"""


def _summary(conn, e: dict, revoked: dict | None = None) -> list[str]:
    """Closed fields of one chain entry, rendered as text. No payload value is quoted here."""
    out = _fields(conn, e)
    withdrawn = (revoked or {}).get(e["event_id"])
    if withdrawn is not None:
        what = "this proposal" if e["type"] == "LINK_EVENT" else "this assertion"
        out.append(reads.revoked_text(withdrawn, what))
    return out


def _fields(conn, e: dict) -> list[str]:
    p = e["payload"] or {}
    kind = (e["type"], e["subtype"])
    if kind == ("PROBE_EVENT", "RUN_START"):
        egress = p.get("egress") or {}
        return [
            f"connector {p.get('connector_id')} {p.get('connector_version')} ({p.get('connector_kind')})",
            f"argv_template {p.get('argv_template')}",
            f"egress {egress.get('environment')} as {egress.get('egress_identity')}",
            "credential " + (p.get("credential_id") or "none: no credential was used"),
            "motivated_by " + (p.get("motivated_by") or "none: a seed run"),
        ]
    if kind == ("PROBE_EVENT", "ITEM"):
        item = conn.execute("SELECT blob_state FROM item WHERE event_id = ?", (e["event_id"],)).fetchone()
        raw = "raw bytes held" if item and item["blob_state"] == "held" else "raw bytes not held"
        return [f"outcome {p.get('outcome')}", raw]
    if kind == ("EXTRACT_EVENT", "CLAIM"):
        ext = p.get("extractor") or {}
        return [
            f"claim {p.get('selector_type')}",
            f"extracted by {ext.get('name')} {ext.get('version')} at {(p.get('source_ref') or {}).get('source_path')}",
            f"time {((p.get('temporal') or {}).get('time_provenance'))}",
        ]
    if e["type"] == "COLLECT_EVENT":
        return [reads.decision_text(e), f"authorization {p.get('authorization_ref') or 'none'}"]
    if e["type"] == "AUTHORIZE_EVENT":
        out = [f"{p.get('act')} by {p.get('authorized_by')}"]
        if p.get("expires_on"):
            out.append(f"expires_on {p['expires_on']} · pivot_depth_max {p.get('pivot_depth_max')}")
        return out
    if kind == ("IDENTITY_EVENT", "CLUSTER"):
        return [f"asserted {p.get('asserted_by')} · {p.get('band')} · rationale {','.join(p.get('rationale_codes') or [])}"]
    if e["type"] == "LINK_EVENT":
        model = p.get("model") or {}
        return [f"PROPOSED {str(p.get('link_type')).lower()} by {model.get('name')} {model.get('version')}, not accepted"]
    if kind == ("ADJUDICATE_EVENT", "PROMOTE"):
        return [f"promoted {p.get('promotion_kind')} to {p.get('entity_type')} by {p.get('analyst')}"]
    if e["type"] == "ADJUDICATE_EVENT":
        return [f"{e['subtype']} by {p.get('analyst') or e['producer']}"]
    if kind == ("ASSESS_EVENT", "SENTENCE"):
        return [f"sentence by {p.get('author')}"]
    return []


_PROJECTION_CHECK = {
    ("EXTRACT_EVENT", "CLAIM"): "SELECT 1 FROM claim WHERE claim_id = ?",
    ("PROBE_EVENT", "ITEM"): "SELECT 1 FROM item WHERE event_id = ?",
    ("PROBE_EVENT", "RUN_START"): "SELECT 1 FROM run WHERE start_event_id = ?",
}


def _projection_present(conn, e: dict) -> bool:
    sql = _PROJECTION_CHECK.get((e["type"], e["subtype"]))
    return sql is None or conn.execute(sql, (e["event_id"],)).fetchone() is not None


def chain(conn, case_id: str, event_id: str) -> dict:
    """The chain behind one event, with breaks marked and the two flags."""
    head = reads.event(conn, case_id, event_id)
    if head is None:
        raise Refusal("EVENT_NOT_IN_CASE", "route: lineage")
    walked = list(conn.execute(WALK_BACK, (event_id, case_id, MAX_DEPTH)))
    revoked = reads.revocations(conn, case_id)
    entries, breaks, seen = [], [], set()
    blocked: set[str] = set()
    for row in walked:
        eid = row["event_id"]
        if row["child"] in blocked:
            blocked.add(eid)
            continue
        e = reads.event(conn, case_id, eid)
        if e is None or not _projection_present(conn, e):
            breaks.append({"event_id": eid, "text": BROKEN.format(eid), "below": row["child"]})
            blocked.add(eid)
            continue
        seen.add(eid)
        entries.append(_entry(conn, e, row["depth"], revoked))
    flags, auth_entries = _authorization(conn, case_id, entries, seen)
    flags = _revocation_flags(entries, revoked) + flags
    entries.extend(auth_entries)
    raw_text, raw_vouch = _raw(conn, case_id, head)
    return {
        "event_id": event_id,
        "dir": "back",
        "chain": entries,
        "breaks": breaks,
        "flags": flags,
        "envelope": _envelope(conn, case_id, event_id),
        "raw": raw_text,
        "raw_vouch": raw_vouch,
    }


def _revocation_flags(entries: list[dict], revoked: dict) -> list[str]:
    """One flag per withdrawn cluster or proposal the chain passes through."""
    out = []
    for x in entries:
        if revoked.get(x["event_id"]) is None:
            continue
        if x["type"] == "LINK_EVENT":
            out.append(f"cites withdrawn proposal {x['event_id'][:8]}: that inference no longer stands")
        elif (x["type"], x["subtype"]) == ("IDENTITY_EVENT", "CLUSTER"):
            out.append(f"cites revoked cluster {x['event_id'][:8]}: that assertion no longer stands")
    return out


def _entry(conn, e: dict, depth: int, revoked: dict | None = None) -> dict:
    payload_state = "held" if e["payload"] is not None else "swept: the payload is gone, the skeleton remains"
    return {
        "event_id": e["event_id"],
        "type": e["type"],
        "subtype": e["subtype"],
        "ts": e["ts"],
        "producer": e["producer"],
        "depth": depth,
        "payload": payload_state,
        "summary": _summary(conn, e, revoked) if e["payload"] is not None else [],
    }


def _authorization(conn, case_id: str, entries: list[dict], seen: set) -> tuple[list[str], list[dict]]:
    """The authorization acts above the chain's decisions, and the two render-only flags."""
    auths = reads.authorizations(conn, case_id)
    flags: list[str] = []
    extra: list[dict] = []
    depth = max((x["depth"] for x in entries), default=0) + 1
    refs = []
    for x in entries:
        if x["type"] in ("COLLECT_EVENT", "AUTHORIZE_EVENT"):
            p = (reads.event(conn, case_id, x["event_id"]) or {}).get("payload") or {}
            ref = p.get("authorization_ref")
            if ref and ref not in refs:
                refs.append(ref)
    for ref in refs:
        acts = auths.get(ref, [])
        for act in acts:
            if act["event_id"] not in seen:
                seen.add(act["event_id"])
                extra.append(_entry(conn, act, depth))
        state = reads.authorization_state(acts)
        revoked = state["revoked"]
        for x in entries:
            if x["type"] != "COLLECT_EVENT" or revoked is None:
                continue
            if x["ts"] > revoked["ts"]:
                flags.append(
                    f"decision recorded after its authorization was revoked "
                    f"({x['subtype']} {x['ts'][11:16]} after REVOKE {revoked['ts'][11:16]})"
                )
        if state["expired"]:
            flags.append(f"authorization expired {state['expires_on']}")
    return flags, extra


def _envelope(conn, case_id: str, event_id: str) -> dict | None:
    row = conn.execute("SELECT * FROM event_skeleton WHERE event_id = ? AND case_id = ?", (event_id, case_id)).fetchone()
    e = reads.event(conn, case_id, event_id)
    if row is None or e is None or e["payload"] is None:
        return None
    return envelope.compose(row, e["payload"])


def _raw(conn, case_id: str, head: dict) -> tuple[str, bool]:
    """(the RAW tier's text, whether the system does not vouch for it)."""
    if head["type"] == "EXTRACT_EVENT":
        claim = conn.execute("SELECT item_id FROM claim WHERE claim_id = ?", (head["event_id"],)).fetchone()
        item = conn.execute("SELECT blob_state FROM item WHERE item_id = ?", (claim["item_id"],)).fetchone() if claim else None
    elif (head["type"], head["subtype"]) == ("PROBE_EVENT", "ITEM"):
        item = conn.execute("SELECT blob_state FROM item WHERE event_id = ?", (head["event_id"],)).fetchone()
    else:
        return "no raw bytes belong to this event", False
    if item is not None and item["blob_state"] == "held":
        return "raw bytes held in the case store; this server has no Encryptor and does not decrypt them", False
    reg = conn.execute("SELECT synthetic FROM case_registry WHERE case_id = ?", (case_id,)).fetchone()
    return "not held: " + blobs.not_held_line(reg["synthetic"] if reg else 0), True


def forward(conn, case_id: str, event_id: str) -> dict:
    """What depends on an event: the clusters, sentences, runs and claims built on it."""
    if reads.event(conn, case_id, event_id) is None:
        raise Refusal("EVENT_NOT_IN_CASE", "route: lineage")
    entries = []
    revoked = reads.revocations(conn, case_id)
    for row in conn.execute(WALK_FORWARD, (event_id, case_id, MAX_DEPTH)):
        if row["event_id"] == event_id:
            continue
        e = reads.event(conn, case_id, row["event_id"])
        entries.append(_entry(conn, e, row["depth"], revoked))
    return {"event_id": event_id, "dir": "forward", "chain": entries, "breaks": [], "flags": []}
