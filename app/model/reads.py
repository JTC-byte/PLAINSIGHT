"""Reads of one attached case that the views share. Nothing here writes.

Every function takes a connection with the case database attached (app.store.db
Store.attach_case) and reads the log and the projections. A payload is read from
event_payload when its stratum is 1 and from the skeleton's payload_inline when
it is 2. A stratum-1 event whose payload a sweep removed reads as payload None,
and the views render that as its consequence rather than skipping the event.

Review state is projected here at read time from the latest VERIFY or DISPUTE
(spec/pse-semantics-contract.md section 8, D3). No column stores it.
"""

from __future__ import annotations

import collections
import datetime as dt
import json

from app.store import db, retention

#: Each adjudication rendered as its consequence, never as its token (CLAUDE.md section 4).
ADJUDICATION_TEXT = {
    "VERIFY": "verified by {who} {day} in the course of {in_course_of}",
    "DISPUTE": "disputed by {who} {day}: {reason}",
    "PROMOTE": "promoted by {who} {day}: {promotion_kind} to {entity_type}",
    "IGNORE": "ignored by {who} {day}: soft and reversible, the target stays in the log",
    "REVOKE": "revoked by {who} {day}: {reason}",
    "ACKNOWLEDGE": "acknowledged by {who} {day}: {note}",
    "OVERRIDE": "override by {who} {day} ({override_kind}): {note}",
    "NOTE": "note by {who} {day}: {text}",
    "QUESTION": "question by {who} {day}: {text}",
}

SKELETON_SELECT = (
    "SELECT s.seq, s.event_id, s.event_type, s.event_subtype, s.ts, s.producer, s.parents_json, "
    "s.payload_stratum, s.payload_inline, p.payload_json "
    "FROM event_skeleton s LEFT JOIN event_payload p ON p.event_id = s.event_id "
)


def now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def is_uuid(value) -> bool:
    return isinstance(value, str) and bool(db.UUID_RE.match(value))


def _shape(row) -> dict:
    raw = row["payload_inline"] if row["payload_stratum"] == 2 else row["payload_json"]
    return {
        "seq": row["seq"],
        "event_id": row["event_id"],
        "type": row["event_type"],
        "subtype": row["event_subtype"],
        "ts": row["ts"],
        "producer": row["producer"],
        "parents": json.loads(row["parents_json"]) if row["parents_json"] else [],
        "payload": json.loads(raw) if raw else None,
    }


def event(conn, case_id: str, event_id: str) -> dict | None:
    row = conn.execute(SKELETON_SELECT + "WHERE s.case_id = ? AND s.event_id = ?", (case_id, event_id)).fetchone()
    return _shape(row) if row else None


def events(conn, case_id: str, event_type: str, subtypes=None) -> list[dict]:
    """Every event of one type, optionally limited to subtypes, in seq order."""
    rows = conn.execute(
        SKELETON_SELECT + "WHERE s.case_id = ? AND s.event_type = ? ORDER BY s.seq", (case_id, event_type)
    )
    out = [_shape(r) for r in rows]
    if subtypes is not None:
        out = [e for e in out if e["subtype"] in subtypes]
    return out


def children(conn, case_id: str, event_id: str) -> list[dict]:
    """Events whose lineage names `event_id` as a parent, in seq order."""
    rows = conn.execute(
        SKELETON_SELECT
        + "WHERE s.case_id = ? AND s.parents_json IS NOT NULL "
        "AND EXISTS (SELECT 1 FROM json_each(s.parents_json) j WHERE j.value = ?) ORDER BY s.seq",
        (case_id, event_id),
    )
    return [_shape(r) for r in rows]


def max_seq(conn, case_id: str) -> int:
    return conn.execute("SELECT COALESCE(MAX(case_seq), 0) FROM event_skeleton WHERE case_id = ?", (case_id,)).fetchone()[0]


def node(conn, node_id: str):
    return conn.execute("SELECT * FROM node WHERE node_id = ?", (node_id,)).fetchone()


def nodes(conn, ids) -> dict[str, dict]:
    out: dict[str, dict] = {}
    ids = list(ids)
    for i in range(0, len(ids), 500):
        chunk = ids[i:i + 500]
        marks = ", ".join("?" for _ in chunk)
        for r in conn.execute(f"SELECT * FROM node WHERE node_id IN ({marks})", chunk):
            out[r["node_id"]] = dict(r)
    return out


def claims_holding(conn, node_row) -> list[dict]:
    """The claims that hold a node: for a selector node, every claim carrying its exact
    (selector_type, value); for any other node, the claims observed_about it."""
    if node_row["kind"] == "selector":
        anchor = conn.execute(
            "SELECT selector_type, value FROM claim WHERE claim_id = ?", (node_row["created_by_event_id"],)
        ).fetchone()
        if anchor is None:
            return []
        rows = conn.execute(
            "SELECT * FROM claim WHERE selector_type = ? AND value = ? ORDER BY observed_at, claim_id",
            (anchor["selector_type"], anchor["value"]),
        )
        return [dict(r) for r in rows]
    rows = conn.execute(
        "SELECT c.* FROM edge e JOIN claim c ON c.claim_id = e.event_id "
        "WHERE e.kind = 'observed_about' AND e.dst_id = ? ORDER BY c.observed_at, c.claim_id",
        (node_row["node_id"],),
    )
    return [dict(r) for r in rows]


def review_states(conn, case_id: str) -> dict[str, dict]:
    """{target event id: the latest VERIFY or DISPUTE}, projected at read time (D3)."""
    out: dict[str, dict] = {}
    for e in events(conn, case_id, "ADJUDICATE_EVENT", ("VERIFY", "DISPUTE")):
        target = (e["payload"] or {}).get("target_ref")
        if target:
            out[target] = e
    return out


def adjudications(conn, case_id: str, targets) -> list[dict]:
    """Every ADJUDICATE event naming one of `targets`, each rendered as its consequence, in seq order."""
    targets = set(targets)
    out = []
    for e in events(conn, case_id, "ADJUDICATE_EVENT"):
        p = e["payload"] or {}
        if p.get("target_ref") not in targets:
            continue
        # Closed tokens read as words (item_to_entity as "item to entity"); prose fields are prose.
        fields = collections.defaultdict(str, {
            k: (v.replace("_", " ") if k in ("in_course_of", "promotion_kind", "override_kind") else v)
            for k, v in p.items() if isinstance(v, str)
        })
        fields["who"] = p.get("analyst") or e["producer"]
        fields["day"] = e["ts"][:10]
        fields["subtype"] = e["subtype"].lower()
        text = ADJUDICATION_TEXT.get(e["subtype"], "{subtype} by {who} {day}").format_map(fields)
        out.append({"event_id": e["event_id"], "subtype": e["subtype"], "target_ref": p.get("target_ref"), "text": text})
    return out


def revocations(conn, case_id: str) -> dict[str, dict]:
    """{target event id: the latest ADJUDICATE REVOKE naming it}, projected at read time (D3).

    A REVOKE may target an IDENTITY_EVENT, a LINK_EVENT or an ADJUDICATE_EVENT
    (policy/lineage.yaml). The views read this map so a withdrawn cluster or a
    withdrawn proposal is never drawn as standing.
    """
    out: dict[str, dict] = {}
    for e in events(conn, case_id, "ADJUDICATE_EVENT", ("REVOKE",)):
        target = (e["payload"] or {}).get("target_ref")
        if target:
            out[target] = e
    return out


def revoked_text(revoke: dict, what: str) -> str:
    """A revocation rendered as its consequence: who withdrew `what`, and when."""
    who = (revoke["payload"] or {}).get("analyst") or revoke["producer"]
    return f"REVOKED by {who} {revoke['ts'][:10]}: {what} no longer stands"


def review_text(review: dict | None) -> str:
    """A review state rendered as its consequence."""
    if review is None:
        return "unreviewed: no analyst has verified or disputed this claim"
    who = (review["payload"] or {}).get("analyst") or review["producer"]
    day = review["ts"][:10]
    if review["subtype"] == "VERIFY":
        return f"verified {who} {day}"
    return f"disputed {who} {day}: do not cite without resolving the dispute"


def item_of_claim(conn, claim_row):
    return conn.execute("SELECT * FROM item WHERE item_id = ?", (claim_row["item_id"],)).fetchone()


def past(expires_at: str | None, at: dt.datetime | None = None) -> bool:
    if not expires_at:
        return False
    return retention.parse_ts(expires_at) <= (at or now())


def authorizations(conn, case_id: str) -> dict[str, list[dict]]:
    """{authorization_ref: its AUTHORIZE events in seq order}."""
    out: dict[str, list[dict]] = {}
    for e in events(conn, case_id, "AUTHORIZE_EVENT"):
        ref = (e["payload"] or {}).get("authorization_ref")
        if ref:
            out.setdefault(ref, []).append(e)
    return out


def authorization_state(acts: list[dict], at: dt.datetime | None = None) -> dict:
    """The state of one authorization: its last pivot_depth_max and expires_on, and its revocation."""
    depth_max = None
    expires_on = None
    revoked = None
    for e in acts:
        p = e["payload"] or {}
        if p.get("act") in ("GRANT", "EXTEND"):
            depth_max = p.get("pivot_depth_max", depth_max)
            expires_on = p.get("expires_on", expires_on)
        elif p.get("act") == "REVOKE":
            revoked = e
    expired = False
    if expires_on:
        expired = dt.date.fromisoformat(expires_on) < (at or now()).date()
    return {"pivot_depth_max": depth_max, "expires_on": expires_on, "revoked": revoked, "expired": expired}


def instant(value) -> dt.datetime | None:
    """A wire timestamp as an instant, or None when the value is not one. A time with no zone is not an instant."""
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, TypeError, AttributeError):
        return None
    return parsed.astimezone(dt.timezone.utc) if parsed.tzinfo is not None else None


NOT_ENFORCED = "retain_until is not being enforced (RT-12)"


def ran_by(beat: dict, at: dt.datetime) -> dt.datetime | None:
    """The instant a heartbeat records a run at, or None when it carries no ts, its ts is after `at`, or its ts
    is not an instant."""
    ts = instant(beat.get("ts"))
    return ts if ts is not None and ts <= at else None


def arrival(beat: dict) -> int:
    """A heartbeat's arrival order, 0 when it carries none."""
    seq = beat.get("seq")
    return seq if isinstance(seq, int) else 0


def next_due_of(beat: dict):
    """The next_due a heartbeat's payload carries, or None when the payload is not an object or carries none."""
    payload = beat.get("payload")
    return payload.get("next_due") if isinstance(payload, dict) else None


def latest_run(runs: list[tuple]) -> dict:
    """The latest of the heartbeats that read as a run: by ts, then by arrival."""
    return max(runs, key=lambda run: run[:2])[2]


def overdue(due: dt.datetime, at: dt.datetime) -> bool:
    """Whether a sweep whose heartbeat names `due` is overdue at `at`: at the due time itself, with no grace
    (policy/retention.yaml RET-R7)."""
    return due <= at


def sweep_state(conn, case_id: str, at: dt.datetime | None = None) -> dict:
    """RT-12 for one case: the case's SWEEP_HEARTBEAT events read by sweep_line against `at`, or against now."""
    return sweep_line(events(conn, case_id, "SYSTEM_EVENT", ("SWEEP_HEARTBEAT",)), at or now())


def sweep_line(beats: list[dict], at: dt.datetime) -> dict:
    """RT-12, rendered as its consequence: the latest SWEEP_HEARTBEAT that reads as a run, against its own next_due.

    A heartbeat reads as a run when its ts is an instant at or before `at`. One dated after `at`, or carrying
    no readable time, records no run that has happened, so the line never stands on it, and the line says how
    many were set aside. The latest run is the latest by ts, then by arrival. A next_due that cannot be read
    is a degraded state, because the line would otherwise vouch for a threshold it never compared
    (policy/retention.yaml RET-R7: the heartbeat's own next due time decides, with no grace). A heartbeat
    row that lacks a ts, a seq or an object payload reads as carrying none, and none of the three makes this
    raise.

    The text carries no mark of its own. The header gives a line whose vouch is true the class that
    app/static/app.css marks, as it does for the retention line, so a mark written here would render twice."""
    if not beats:
        return {"ran": None, "next_due": None, "vouch": True, "not_read": 0,
                "text": f"RETENTION SWEEP HAS NEVER RUN HERE · {NOT_ENFORCED}"}
    runs = []
    for beat in beats:
        ts = ran_by(beat, at)
        if ts is not None:
            runs.append((ts, arrival(beat), beat))
    not_read = len(beats) - len(runs)
    if not runs:
        return {"ran": None, "next_due": None, "vouch": True, "not_read": not_read,
                "text": f"NO RETENTION SWEEP RUN IS ON RECORD HERE · {not_read} heartbeat(s) carry a time after now "
                        f"or no readable time · {NOT_ENFORCED}"}
    last = latest_run(runs)
    next_due = next_due_of(last)
    due = instant(next_due)
    if due is None:
        vouch = True
        text = (f"RETENTION SWEEP RAN {last['ts']} AND ITS NEXT DUE TIME CANNOT BE READ · whether retain_until "
                "is being enforced cannot be told (RT-12)")
    elif overdue(due, at):
        vouch = True
        text = f"RETENTION SWEEP HAS NOT RUN SINCE {last['ts']} · {NOT_ENFORCED}"
    else:
        vouch = False
        text = f"retention sweep ran {last['ts']}, next due {next_due} · this draft of the sweep deletes nothing"
    if not_read:
        vouch = True
        text += f" · {not_read} heartbeat(s) carrying a time after now or no readable time are not read as a run"
    return {"ran": last["ts"], "next_due": next_due, "vouch": vouch, "not_read": not_read, "text": text}


def halt_line(conn) -> str | None:
    """RT-11, rendered as its consequence: a SHRED_FAILED with halt_system_wide in any case held."""
    for e in conn.execute(
        SKELETON_SELECT + "WHERE s.event_type = 'SYSTEM_EVENT' AND s.event_subtype = 'SHRED_FAILED' ORDER BY s.seq"
    ):
        p = _shape(e)["payload"] or {}
        if p.get("halt_system_wide"):
            return "HALTED, a shred failed: no new run will dispatch system-wide (RT-11)"
    return None


def seed_focus(conn, case_id: str) -> str | None:
    """The node esc esc returns to: the earliest entity a human promoted, else the earliest node."""
    row = conn.execute(
        "SELECT n.node_id FROM node n JOIN event_skeleton s ON s.event_id = n.created_by_event_id "
        "WHERE n.kind = 'entity' ORDER BY s.seq, n.node_id LIMIT 1"
    ).fetchone()
    if row is None:
        row = conn.execute(
            "SELECT n.node_id FROM node n JOIN event_skeleton s ON s.event_id = n.created_by_event_id "
            "ORDER BY s.seq, n.node_id LIMIT 1"
        ).fetchone()
    return row["node_id"] if row else None


def resolve_ref(conn, case_id: str, ref: str) -> str | None:
    """The node an id stands for: a node id itself, or the node an event created or names."""
    if node(conn, ref) is not None:
        return ref
    e = event(conn, case_id, ref)
    if e is None:
        return None
    p = e["payload"] or {}
    kind = (e["type"], e["subtype"])
    if kind == ("EXTRACT_EVENT", "CLAIM"):
        row = conn.execute(
            "SELECT n.node_id FROM node n JOIN claim c ON c.claim_id = n.created_by_event_id "
            "WHERE n.kind = 'selector' AND c.selector_type = ? AND c.value = ?",
            (p.get("selector_type"), p.get("value")),
        ).fetchone()
        return row["node_id"] if row else None
    if kind == ("IDENTITY_EVENT", "CLUSTER"):
        return p.get("cluster_id")
    if kind == ("IDENTITY_EVENT", "EXCLUDE"):
        return p.get("candidate_ref")
    if kind == ("ADJUDICATE_EVENT", "PROMOTE"):
        return p.get("entity_id")
    return None


def sentences_by_node(conn, case_id: str) -> dict[str, list[str]]:
    """{node id: sentence event ids citing it}. A sentence is a badge, never a node."""
    out: dict[str, list[str]] = {}
    for e in events(conn, case_id, "ASSESS_EVENT", ("SENTENCE",)):
        p = e["payload"] or {}
        refs = [c.get("ref") for c in p.get("citations") or [] if isinstance(c, dict)]
        refs += [p.get("subject_ref")] + list(e["parents"])
        targets = []
        for ref in refs:
            if is_uuid(ref):
                nid = resolve_ref(conn, case_id, ref)
                if nid and nid not in targets:
                    targets.append(nid)
        for nid in targets:
            out.setdefault(nid, []).append(e["event_id"])
    return out


def collect_decisions(conn, case_id: str) -> list[dict]:
    return events(conn, case_id, "COLLECT_EVENT")


def decision_text(e: dict) -> str:
    """A gate decision rendered as its consequence, from closed fields only."""
    p = e["payload"] or {}
    target = p.get("target_selector_type") or "an unstated selector type"
    if e["subtype"] == "PERMITTED":
        return f"PERMITTED, the gate allowed one run against {target} at pivot_depth {p.get('pivot_depth')}"
    if e["subtype"] == "REQUIRES_EXTENSION":
        return (
            f"REQUIRES_EXTENSION, the gate held a pivot to {target} at pivot_depth {p.get('pivot_depth')} "
            f"({p.get('extension_basis')}): nothing was collected until an EXTEND is recorded"
        )
    if e["subtype"] == "REFUSED":
        return f"REFUSED, the gate refused {target} ({p.get('refusal_basis')}): nothing was collected"
    return f"{e['subtype']}, a gate decision this view does not render"
