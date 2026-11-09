"""Analyst acts from the interface, and the deep dive.

POST /api/cases/{case}/acts (slice 3, docs/PLAINSIGHT-design.md amendment 9.16)
mints one ADJUDICATE_EVENT or IDENTITY_EVENT per request from a closed body and
sends it through the same door every corpus row passes (app/store/ingest.py):
tools/validate.py loaded by path, the store checks, one transaction, then the
notice. The body states the act, its target and the fields the layer model
requires of that subtype, and nothing else; an unknown key or act is refused
before the door is reached. The server fills what no body may state: event_id,
ts, producer (the session's --analyst, never a form field), source and lineage.
A code the validator fires comes back as ACT_REFUSED_BY_MODEL with the codes
in its detail, so the interface can say what the model refused.

Where an act lands (reading APP-R31). On ISOLATED, any held case. On LOCAL the
route refuses to land any act (ACT_LOCAL_PENDING_DECISION) until the operator
sets app.config.LOCAL_ACTS, because an act's payload is stratum 1 by the layer
model and its prose is typed at run time rather than read from a tracked,
reviewed synthetic file: admitting it would widen what LOCAL may hold under
EGRESS.md EG-2, which is his decision and not this change's. With that value
set, an act still lands only in a case whose registry row says synthetic
(ACT_LOCAL_SYNTHETIC_CASE_ONLY), and the tests set the value to exercise the
mechanism. Both rules are ingest_batch's, under the origin "act".

The runtime half of ADJUDICATION_REASON_MISSING (reading APP-R32). The layer
model marks it `when: runtime`: IGNORE needs a reason when the target supports
a live cluster or was promoted by another analyst, which is a fact about the
case and not a field. The server reads the case here (ACT_REASON_REQUIRED).
DISPUTE and REVOKE carry reason in payload.required, and the validator refuses
them without it.

What the server adds and what it refuses to add (reading APP-R33). For a
CLUSTER, rationale_codes is the union of the per-member seams and
last_supporting_ts the latest ts among the basis claims; cluster_id and a
PROMOTE's entity_id are uuid4. Every rule of the model (two members, a seam per
member, k needs a note, almost_certain needs two evidence classes, the
circularity walk) is the validator's, and the server copies none of them: it
checks shapes, closed keys and facts about the case the validator cannot see
(an item already promoted, a target already revoked, a member that is not an
entity or a referenced-only node).

The deep dive (slice 2) is unchanged. A deep dive takes exactly one node and
one motivating claim per act (doctrine/SUBJECT_SELECTION.md SS-16, amendment
9.11). The route always refuses, writes nothing, and imports nothing from
runner/. While runner/subject_guard.py does not exist it returns "NOT
DISPATCHED, no subject gate exists yet (Step 10): nothing was collected" with
the legal moves; while the gate file exists and is not connected, it says so.
The app never emits a COLLECT_EVENT, never mints an AUTHORIZE_EVENT GRANT or an
SS-4 record, and p mints no VERIFY. app/tests/test_http.py scans app/ for any
constructor of either event type and for any import of runner.
"""

from __future__ import annotations

import datetime as dt
import uuid

from app import __version__, config
from app.model import reads
from app.refusals import REFUSALS, Refusal
from app.store import door, ingest

GATE = config.REPO_ROOT / "runner" / "subject_guard.py"

BODY_KEYS = frozenset({"node_id", "motivating_claim"})
PLURAL_KEYS = frozenset({"node_ids", "nodes", "targets"})

#: The longest analyst prose field the route accepts, in characters. A body is
#: capped at 8 KiB by the server; this keeps one field from being most of it.
TEXT_MAX = 2000

#: Each act: its event type and subtype, the body keys it requires, and the
#: body keys it may carry. `act` and `target` are read first and are not listed.
ACTS: dict[str, dict] = {
    "VERIFY": {"type": "ADJUDICATE_EVENT", "required": ("in_course_of",), "optional": ()},
    "DISPUTE": {"type": "ADJUDICATE_EVENT", "required": ("reason",), "optional": ()},
    "NOTE": {"type": "ADJUDICATE_EVENT", "required": ("text",), "optional": ()},
    "QUESTION": {"type": "ADJUDICATE_EVENT", "required": ("text",), "optional": ()},
    "IGNORE": {"type": "ADJUDICATE_EVENT", "required": (), "optional": ("reason",)},
    "REVOKE": {"type": "ADJUDICATE_EVENT", "required": ("reason",), "optional": ()},
    "PROMOTE": {"type": "ADJUDICATE_EVENT", "required": ("entity_type", "anchor_claim"), "optional": ("anchor_selector_type",)},
    "EXCLUDE": {"type": "IDENTITY_EVENT", "required": ("basis", "based_on"), "optional": ()},
    "CLUSTER": {
        "type": "IDENTITY_EVENT",
        "required": ("members", "member_seams", "band", "basis_claims"),
        "optional": ("note", "proposals", "circularity_override"),
        "no_target": True,
    },
}

#: The fields that carry analyst prose. Each is a string of 1 to TEXT_MAX characters.
TEXT_FIELDS = frozenset({"in_course_of", "reason", "text", "basis", "note", "entity_type", "anchor_selector_type", "band"})

#: Node kinds a CLUSTER may hold as members (design section 5.6: a cluster references accounts).
MEMBER_KINDS = frozenset({"entity", "referenced"})


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


# ---------------------------------------------------------------------------
# the deep dive (slice 2)
# ---------------------------------------------------------------------------


def gate_exists() -> bool:
    return GATE.is_file()


def not_dispatched_text(environment: str, gate_present: bool | None = None) -> str:
    """The consequence the route returns, with its legal moves."""
    present = gate_exists() if gate_present is None else gate_present
    code = REFUSALS["DEEP_DIVE_NOT_DISPATCHED"]
    if present:
        what = (
            "NOT DISPATCHED, the subject gate is not connected to this route (a Class F change the "
            "operator decides): nothing was collected"
        )
    else:
        what = code.what
    moves = list(code.moves)
    text = f"{what}. Legal moves: {', '.join(moves[:-1])}, or {moves[-1]}."
    if environment == "LOCAL":
        text += " LOCAL executes no connector (EG-1), so nothing is dispatched from this machine in any case."
    return text


def deep_dive(conn, case_id: str, body, environment: str) -> dict:
    """Validate one deep-dive request and refuse it with its consequence. Writes nothing."""
    if not isinstance(body, dict):
        raise Refusal("BODY_REFUSED", "route: deep-dives")
    if PLURAL_KEYS & set(body) or isinstance(body.get("node_id"), list):
        raise Refusal("DEEP_DIVE_ONE_NODE_PER_ACT")
    if set(body) != BODY_KEYS:
        raise Refusal("BODY_REFUSED", "route: deep-dives takes node_id and motivating_claim")
    node_id, claim_id = body["node_id"], body["motivating_claim"]
    if not reads.is_uuid(node_id) or not reads.is_uuid(claim_id):
        raise Refusal("BODY_REFUSED", "route: deep-dives takes uuids")
    if reads.node(conn, node_id) is None:
        raise Refusal("NODE_NOT_IN_CASE", "route: deep-dives")
    if conn.execute("SELECT 1 FROM claim WHERE claim_id = ?", (claim_id,)).fetchone() is None:
        raise Refusal("CLAIM_NOT_IN_CASE", "route: deep-dives")
    refusal = Refusal("DEEP_DIVE_NOT_DISPATCHED")
    return {
        "refused": refusal.code,
        "state": "NOT DISPATCHED",
        "text": not_dispatched_text(environment),
        "rule": REFUSALS[refusal.code].rule,
        "node_id": node_id,
        "motivating_claim": claim_id,
        "recorded": "nothing: no event was appended and no row was written",
    }


# ---------------------------------------------------------------------------
# the analyst acts (slice 3)
# ---------------------------------------------------------------------------


def _text(body: dict, key: str) -> str:
    value = body.get(key)
    if not isinstance(value, str) or not value.strip() or len(value) > TEXT_MAX:
        raise Refusal("BODY_REFUSED", f"route: acts, field {key} is a string of 1 to {TEXT_MAX} characters")
    return value.strip()


def _uuid(body: dict, key: str) -> str:
    value = body.get(key)
    if not reads.is_uuid(value):
        raise Refusal("BODY_REFUSED", f"route: acts, field {key} is a uuid")
    return value


def _uuid_list(body: dict, key: str, minimum: int) -> list[str]:
    value = body.get(key)
    if not isinstance(value, list) or len(value) < minimum or not all(reads.is_uuid(v) for v in value):
        raise Refusal("BODY_REFUSED", f"route: acts, field {key} is a list of at least {minimum} uuids")
    if len(set(value)) != len(value):
        raise Refusal("BODY_REFUSED", f"route: acts, field {key} repeats an id")
    return list(value)


def check_keys(body, act: str) -> dict:
    """The act's closed key set: `act`, `target` (unless the act takes none), its
    required keys and its optional keys. Anything else is refused before the door."""
    spec = ACTS[act]
    allowed = {"act"} | set(spec["required"]) | set(spec["optional"])
    if not spec.get("no_target"):
        allowed.add("target")
    required = {"act"} | set(spec["required"]) | (set() if spec.get("no_target") else {"target"})
    keys = set(body)
    if keys - allowed:
        raise Refusal("BODY_REFUSED", f"route: acts, {act} does not take {', '.join(sorted(keys - allowed))}")
    if required - keys:
        raise Refusal("BODY_REFUSED", f"route: acts, {act} needs {', '.join(sorted(required - keys))}")
    return spec


def event_in_case(conn, case_id: str, event_id: str):
    row = conn.execute(
        "SELECT event_id, event_type, event_subtype, ts FROM event_skeleton WHERE case_id = ? AND event_id = ?",
        (case_id, event_id),
    ).fetchone()
    if row is None:
        raise Refusal("EVENT_NOT_IN_CASE", "route: acts, the target")
    return row


def _item_event(conn, case_id: str, ref: str) -> str:
    """The ITEM event id for a PROMOTE target given as an item id or its event id."""
    row = conn.execute("SELECT event_id FROM item WHERE item_id = ? OR event_id = ?", (ref, ref)).fetchone()
    if row is None:
        raise Refusal("ITEM_NOT_IN_CASE", "route: acts, PROMOTE targets an item")
    event_in_case(conn, case_id, row["event_id"])
    return row["event_id"]


def ignore_needs_reason(conn, case_id: str, target: str, analyst: str) -> str | None:
    """Why an IGNORE of `target` needs a reason, or None (design 4.4, reading APP-R32)."""
    revoked = reads.revocations(conn, case_id)
    for e in reads.events(conn, case_id, "IDENTITY_EVENT", ("CLUSTER",)):
        if e["event_id"] in revoked:
            continue
        if target in ((e["payload"] or {}).get("basis_claims") or []):
            return f"the target is a basis claim of live cluster {e['event_id'][:8]}"
    item = conn.execute("SELECT event_id FROM item WHERE item_id = ? OR event_id = ?", (target, target)).fetchone()
    item_event = item["event_id"] if item else None
    for e in reads.events(conn, case_id, "ADJUDICATE_EVENT", ("PROMOTE",)):
        if e["event_id"] in revoked:
            continue
        p = e["payload"] or {}
        if p.get("target_ref") in (target, item_event) or p.get("anchor_claim_ref") == target:
            if p.get("analyst") != analyst:
                return f"the target was promoted by {p.get('analyst')} in {e['event_id'][:8]}"
    return None


def promoted_by(conn, case_id: str, item_event: str) -> str | None:
    """The standing PROMOTE of an item, or None."""
    revoked = reads.revocations(conn, case_id)
    for e in reads.events(conn, case_id, "ADJUDICATE_EVENT", ("PROMOTE",)):
        if e["event_id"] not in revoked and (e["payload"] or {}).get("target_ref") == item_event:
            return e["event_id"]
    return None


def envelope(store, case_id: str, analyst: str, etype: str, esub: str, payload: dict, based_on: list[str]) -> dict:
    """The envelope the server mints: constants from the generated schema, the
    session's identity as producer, and lineage with the target first."""
    props = door.load_policy().schema["properties"]
    return {
        "pse_version": props["pse_version"]["const"],
        "derived_from": props["derived_from"]["const"],
        "case_id": case_id,
        "event": {"event_id": str(uuid.uuid4()), "event_type": etype, "event_subtype": esub, "ts": _now()},
        "source": {
            "platform_id": ingest.STORE_PLATFORM_ID,
            "environment": store.environment,
            "producer": analyst,
            "sw_version": __version__,
        },
        "payload": payload,
        "lineage": {"based_on": based_on, "transform": None},
    }


def build(store, case_id: str, analyst: str, body) -> tuple[dict, str]:
    """(the envelope, its consequence text) for one act body. Reads the case, writes nothing."""
    if not isinstance(body, dict):
        raise Refusal("BODY_REFUSED", "route: acts takes a JSON object")
    act = body.get("act")
    if not isinstance(act, str) or act not in ACTS:
        raise Refusal("ACT_UNKNOWN")
    spec = check_keys(body, act)
    conn = store.conn
    etype = spec["type"]
    if act == "CLUSTER":
        # One member is a shape the model refuses (CLUSTER_MEMBERS_INSUFFICIENT), so the
        # shape check here asks for a list and lets the validator say why one is not enough.
        members = _uuid_list(body, "members", 1)
        basis = _uuid_list(body, "basis_claims", 1)
        seams = body.get("member_seams")
        if not isinstance(seams, dict) or set(seams) != set(members) or not all(
            isinstance(v, list) and v and all(isinstance(c, str) and len(c) == 1 for c in v) for v in seams.values()
        ):
            raise Refusal("BODY_REFUSED", "route: acts, member_seams maps every member to its rationale codes")
        band = _text(body, "band")
        note = body.get("note")
        if note is not None:
            note = _text(body, "note")
        proposals = _uuid_list(body, "proposals", 0) if "proposals" in body else []
        override = body.get("circularity_override")
        if override is not None:
            if not isinstance(override, dict) or set(override) != {"note"}:
                raise Refusal("BODY_REFUSED", "route: acts, circularity_override carries a note and nothing else")
            override = {"note": _text(override, "note")}
        nodes = reads.nodes(conn, members)
        for m in members:
            row = nodes.get(m)
            if row is None or row["kind"] not in MEMBER_KINDS:
                raise Refusal("ACT_MEMBER_KIND_REFUSED", f"member {m[:8]}")
        latest = None
        for cid in basis:
            row = event_in_case(conn, case_id, cid)
            latest = row["ts"] if latest is None or row["ts"] > latest else latest
        for pid in proposals:
            event_in_case(conn, case_id, pid)
        codes = sorted({c for v in seams.values() for c in v})
        payload = {
            "assertion": "CLUSTER",
            "cluster_id": str(uuid.uuid4()),
            "members": members,
            "asserted_by": analyst,
            "rationale_codes": codes,
            "band": band,
            "last_supporting_ts": latest,
            "member_seams": {m: list(seams[m]) for m in members},
            "basis_claims": basis,
        }
        if note is not None:
            payload["note"] = note
        if override is not None:
            payload["circularity_override"] = override
        based_on = basis + [p for p in proposals if p not in basis]
        text = (
            f"CLUSTER asserted by {analyst}: {len(members)} members, band {band}, seams shown per member and "
            "never rolled up; x revokes it and leaves a tombstone"
        )
        return envelope(store, case_id, analyst, etype, "CLUSTER", payload, based_on), text

    target = _uuid(body, "target")
    if act == "PROMOTE":
        item_event = _item_event(conn, case_id, target)
        standing = promoted_by(conn, case_id, item_event)
        if standing is not None:
            raise Refusal("ACT_TARGET_ALREADY_PROMOTED", f"PROMOTE {standing[:8]} stands")
        anchor = _uuid(body, "anchor_claim")
        claim = conn.execute(
            "SELECT c.claim_id, c.selector_type FROM claim c JOIN item i ON i.item_id = c.item_id "
            "WHERE c.claim_id = ? AND i.event_id = ?",
            (anchor, item_event),
        ).fetchone()
        if claim is None:
            raise Refusal("CLAIM_NOT_IN_CASE", "route: acts, anchor_claim is a claim of the promoted item")
        anchor_type = _text(body, "anchor_selector_type") if "anchor_selector_type" in body else claim["selector_type"]
        payload = {
            "disposition": "PROMOTE",
            "target_ref": item_event,
            "analyst": analyst,
            "promotion_kind": "item_to_entity",
            "entity_type": _text(body, "entity_type"),
            "entity_id": str(uuid.uuid4()),
            "anchor_selector_type": anchor_type,
            "anchor_claim_ref": anchor,
        }
        text = (
            f"PROMOTED by {analyst}: item {item_event[:8]} becomes a {payload['entity_type']} anchored on "
            f"{anchor_type}; the anchor is vouched only when a claim of that type holds it"
        )
        return envelope(store, case_id, analyst, etype, "PROMOTE", payload, [item_event]), text

    if act == "EXCLUDE":
        based_on = _uuid_list(body, "based_on", 1)
        if reads.node(conn, target) is None:
            raise Refusal("NODE_NOT_IN_CASE", "route: acts, EXCLUDE targets a node")
        for pid in based_on:
            event_in_case(conn, case_id, pid)
        payload = {"assertion": "EXCLUDE", "candidate_ref": target, "asserted_by": analyst, "basis": _text(body, "basis")}
        text = f"EXCLUDED by {analyst}: candidate {target[:8]} is affirmatively not the subject; it stays in place, struck through"
        return envelope(store, case_id, analyst, etype, "EXCLUDE", payload, based_on), text

    row = event_in_case(conn, case_id, target)
    payload = {"disposition": act, "target_ref": target, "analyst": analyst}
    day = _now()[:10]
    if act == "VERIFY":
        payload["in_course_of"] = _text(body, "in_course_of")
        text = f"verified {analyst} {day}, in the course of {payload['in_course_of']}"
    elif act == "DISPUTE":
        payload["reason"] = _text(body, "reason")
        text = f"disputed {analyst} {day}: do not cite without resolving the dispute"
    elif act in ("NOTE", "QUESTION"):
        payload["text"] = _text(body, "text")
        text = f"{act.lower()} recorded by {analyst} {day} on {row['event_type']} {target[:8]}"
    elif act == "REVOKE":
        if target in reads.revocations(conn, case_id):
            raise Refusal("ACT_TARGET_ALREADY_REVOKED")
        payload["reason"] = _text(body, "reason")
        text = f"REVOKED by {analyst} {day}: {row['event_subtype']} {target[:8]} no longer stands; the tombstone stays walkable"
    elif act == "IGNORE":
        why = ignore_needs_reason(conn, case_id, target, analyst)
        if "reason" in body:
            payload["reason"] = _text(body, "reason")
        elif why is not None:
            raise Refusal("ACT_REASON_REQUIRED", why)
        text = f"ignored by {analyst} {day}: soft and reversible, the target stays in the log and in lineage"
    return envelope(store, case_id, analyst, etype, act, payload, [target]), text


def mint(store, case_id: str, analyst: str, body, humans=None) -> dict:
    """Build one act, run it through the door, and return what was recorded.

    The door runs the validator once more inside ingest_batch; the first run
    here is to return the fired codes rather than the batch refusal's prose."""
    env, text = build(store, case_id, analyst, body)
    humans = set(config.deployment_humans() if humans is None else humans)
    stored, _ = ingest.replay.stored_envelopes(store, case_id)
    store.attach_case(case_id, create=False)
    failures = door.validate([(1, env)], stored, door.load_policy(), humans)
    if failures:
        codes = sorted(set().union(*(c for _, c in failures.values())))
        raise Refusal("ACT_REFUSED_BY_MODEL", "codes: " + ", ".join(codes))
    result = ingest.ingest_batch(store, [env], humans, origin="act")
    return {
        "recorded": env["event"]["event_id"],
        "act": body["act"],
        "event_type": env["event"]["event_type"],
        "consequence": text,
        "landed": result.landed,
        "notices": sorted({n["kind"] for n in result.notices}),
    }
