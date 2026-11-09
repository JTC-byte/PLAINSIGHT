"""POST /api/cases/{case}/acts: every analyst act is minted by the server under the
session's identity, passes the same door as a corpus row, lands in one transaction
and reaches a second tab through a notice alone. Each check claims coverage of a
mechanism on the corpus, never the correctness of an identity (design gate 3)."""

from __future__ import annotations

import uuid

from app import config
from app.http import acts, routes
from app.store import door, ingest
from app.store.project import Projector, selector_node_id
from app.tests.helpers import CASE, eid_of, files_digest
from app.tests.served import FOCUS, Client, open_case, stream_collect, stream_open

API = f"/api/cases/{CASE}"
ACTS = f"{API}/acts"
HANDLE_CLAIM = "94746128-88d7-58f3-8e87-31794f06cd25"
UNVERIFIED_CLAIM = "dcedb60a-37bb-592d-811e-c7e540569735"
ITEM_TWO = "e7abb53a-40bb-584c-99ce-619c8d4e1667"
REFERENCED_SECOND = "584e2e90-328f-537c-9f00-5527f9dab8c2"
REFERENCED_THIRD = "33c6ba89-16a7-5a0e-8e6d-540e4290a3fa"
SAME_ENTITY_LINK = "1de4148d-e492-5bf6-8124-c02167dc8236"


def _client(ctx, local_acts: bool = True) -> Client:
    """A served corpus copy. LOCAL_ACTS is set in memory so the mechanism can be
    exercised on LOCAL; the shipped value is False (reading APP-R31)."""
    ctx.mp.setattr(config, "LOCAL_ACTS", local_acts)
    c = Client(ctx)
    c.login()
    return c


# -- on LOCAL an act lands nowhere until the operator sets LOCAL_ACTS ------------------------------


def check_local_acts_refuse_until_decided(ctx):
    assert config.LOCAL_ACTS is False, "the shipped value admits acts to LOCAL before the operator decided"
    c = _client(ctx, local_acts=False)
    before = files_digest(c.root)
    r = c.send("POST", ACTS, {"act": "VERIFY", "target": UNVERIFIED_CLAIM, "in_course_of": "pivot_motivation"})
    assert r.status == 403 and r.json()["refused"] == "ACT_LOCAL_PENDING_DECISION", r.body
    assert "APP-R31" in r.json()["text"]
    assert files_digest(c.root) == before, "an act landed on LOCAL before the operator decided"


def break_local_acts_flag_ignored(ctx):
    ctx.mp.setattr(ingest, "local_acts_enabled", lambda: True)


def test_local_acts_refuse_until_decided(ctx):
    check_local_acts_refuse_until_decided(ctx)


def _node(c: Client, node_id: str) -> dict:
    r = c.get(f"{API}/node/{node_id}")
    assert r.status == 200, r.body
    return r.json()


# -- a VERIFY lands through the door and a second tab learns of it by a notice alone --------------


def check_verify_lands_and_notifies_a_second_tab(ctx):
    c = _client(ctx)
    before = files_digest(c.root)
    node = selector_node_id(UNVERIFIED_CLAIM)
    assert _node(c, node)["claims"][0]["review"].startswith("unreviewed"), "the corpus claim is already reviewed"
    sock, _head, rest = stream_open(c, f"{API}/notices")
    r = c.send("POST", ACTS, {"act": "VERIFY", "target": UNVERIFIED_CLAIM, "in_course_of": "pivot_motivation"})
    assert r.status == 201, r.body
    out = r.json()
    assert uuid.UUID(out["recorded"]) and out["act"] == "VERIFY" and out["landed"] == 1
    assert out["consequence"].startswith("verified analyst-example"), out["consequence"]
    frames = stream_collect(sock, rest, 1.5)
    assert any("data: " in f for f in frames), "the second tab received no notice of the act"
    assert files_digest(c.root) != before, "the act changed no file of the store"
    assert _node(c, node)["claims"][0]["review"].startswith("verified analyst-example"), "the review did not project"
    s = open_case(c.root)
    try:
        row = s.conn.execute("SELECT producer, event_type, event_subtype FROM event_skeleton WHERE event_id = ?", (out["recorded"],)).fetchone()
        assert row is not None and tuple(row) == ("analyst-example", "ADJUDICATE_EVENT", "VERIFY")
    finally:
        s.close()


def break_acts_handler_records_nothing(ctx):
    def silent(app, params, query, body):
        return routes.json_response({"recorded": str(uuid.uuid4()), "act": body["act"], "landed": 1,
                                     "consequence": "verified analyst-example"}, status=201)

    ctx.mp.setitem(routes.HANDLERS, "acts", silent)


def test_verify_lands_and_notifies_a_second_tab(ctx):
    check_verify_lands_and_notifies_a_second_tab(ctx)


# -- the model's refusals reach the interface with their codes, and nothing is written -------------


def _cluster_body(members, seams, band="likely", **extra) -> dict:
    body = {"act": "CLUSTER", "members": members, "member_seams": seams, "band": band, "basis_claims": [HANDLE_CLAIM]}
    body.update(extra)
    return body


def check_model_refusals_reach_the_interface(ctx):
    c = _client(ctx)
    before = files_digest(c.root)
    cases = [
        (_cluster_body([FOCUS], {FOCUS: ["h"]}), "CLUSTER_MEMBERS_INSUFFICIENT"),
        (_cluster_body([FOCUS, REFERENCED_SECOND], {FOCUS: ["h"], REFERENCED_SECOND: ["e"]}, band="almost_certain"), "BAND_UNSUPPORTED"),
        (_cluster_body([FOCUS, REFERENCED_SECOND], {FOCUS: ["k"], REFERENCED_SECOND: ["k"]}), "RATIONALE_NOTE_MISSING"),
        ({"act": "VERIFY", "target": eid_of("identity-cluster-possible"), "in_course_of": "citation"}, "LINEAGE_PARENT_TYPE_INVALID"),
    ]
    for body, code in cases:
        r = c.send("POST", ACTS, body)
        assert r.status == 422, (code, r.status, r.body)
        out = r.json()
        assert out["refused"] == "ACT_REFUSED_BY_MODEL" and code in out.get("detail", ""), (code, out)
    ctx.mp.setattr(c.app, "analyst", "connector-example")
    r = c.send("POST", ACTS, {"act": "NOTE", "target": HANDLE_CLAIM, "text": "a note under a connector's name"})
    assert r.status == 422 and "PRODUCER_NOT_ALLOWED" in r.json().get("detail", ""), "a non-human producer minted an act"
    assert files_digest(c.root) == before, "a refused act wrote to the store"


def break_validator_removed(ctx):
    ctx.mp.setattr(door, "validate", lambda envs, stored, pol, humans: {})


def test_model_refusals_reach_the_interface(ctx):
    check_model_refusals_reach_the_interface(ctx)


# -- a CLUSTER draws brackets with per-member seams, and x revokes it ----------------------------


def check_cluster_minted_and_revoked(ctx):
    c = _client(ctx)
    seams = {FOCUS: ["h", "b"], REFERENCED_SECOND: ["b"]}
    r = c.send("POST", ACTS, _cluster_body([FOCUS, REFERENCED_SECOND], seams, note="the bio links to the account", proposals=[SAME_ENTITY_LINK]))
    assert r.status == 201, r.body
    recorded = r.json()["recorded"]
    s = open_case(c.root)
    try:
        node = s.conn.execute("SELECT * FROM node WHERE created_by_event_id = ?", (recorded,)).fetchone()
        assert node is not None and node["kind"] == "cluster", "no cluster node was projected"
        edges = {e["src_id"]: e["label"] for e in s.conn.execute("SELECT src_id, label FROM edge WHERE dst_id = ? AND kind = 'member_of'", (node["node_id"],))}
        assert edges == {FOCUS: "h,b", REFERENCED_SECOND: "b"}, edges
        env = s.conn.execute("SELECT parents_json FROM event_skeleton WHERE event_id = ?", (recorded,)).fetchone()
        assert HANDLE_CLAIM in env["parents_json"] and SAME_ENTITY_LINK in env["parents_json"], "the accepted proposal is not in the cluster's lineage"
    finally:
        s.close()
    described = _node(c, node["node_id"])["node"]
    assert described["kind"] == "cluster" and not described["revoked"]
    r = c.send("POST", ACTS, {"act": "REVOKE", "target": recorded, "reason": "a member was shown to be a namesake"})
    assert r.status == 201, r.body
    assert _node(c, node["node_id"])["node"]["revoked"], "the revoked cluster is not struck"
    r = c.send("POST", ACTS, {"act": "REVOKE", "target": recorded, "reason": "again"})
    assert r.status == 409 and r.json()["refused"] == "ACT_TARGET_ALREADY_REVOKED"


def break_cluster_projection_removed(ctx):
    ctx.mp.setattr(Projector, "_cluster", lambda self, env, p: None)


def test_cluster_minted_and_revoked(ctx):
    check_cluster_minted_and_revoked(ctx)


# -- on LOCAL an act lands only in a case the registry marks synthetic -----------------------------


def check_local_acts_only_in_a_synthetic_case(ctx):
    c = _client(ctx)
    s = open_case(c.root)
    try:
        s.conn.execute("UPDATE case_registry SET synthetic = 0 WHERE case_id = ?", (CASE,))
        s.conn.commit()
    finally:
        s.close()
    before = files_digest(c.root)
    r = c.send("POST", ACTS, {"act": "NOTE", "target": HANDLE_CLAIM, "text": "compare against item 2 before citing"})
    assert r.status == 403 and r.json()["refused"] == "ACT_LOCAL_SYNTHETIC_CASE_ONLY", r.body
    assert files_digest(c.root) == before, "an act landed on a LOCAL case not marked synthetic"


def break_origin_rule_removed(ctx):
    ctx.mp.setattr(ingest, "origin_allowed", lambda store, case_id, origin: None)


def test_local_acts_only_in_a_synthetic_case(ctx):
    check_local_acts_only_in_a_synthetic_case(ctx)


# -- IGNORE needs a reason only when the target is load-bearing (design 4.4) -----------------------


def check_ignore_reason_rule(ctx):
    c = _client(ctx)
    r = c.send("POST", ACTS, {"act": "IGNORE", "target": HANDLE_CLAIM})
    assert r.status == 400 and r.json()["refused"] == "ACT_REASON_REQUIRED", "a basis claim of a live cluster was ignored without a reason"
    assert "live cluster" in r.json().get("detail", "")
    r = c.send("POST", ACTS, {"act": "IGNORE", "target": HANDLE_CLAIM, "reason": "the cluster rests on the other member"})
    assert r.status == 201, r.body
    r = c.send("POST", ACTS, {"act": "IGNORE", "target": ITEM_TWO})
    assert r.status == 201, "an item supporting nothing needed a reason"
    assert r.json()["consequence"].startswith("ignored by analyst-example")


def break_ignore_rule_removed(ctx):
    ctx.mp.setattr(acts, "ignore_needs_reason", lambda conn, case_id, target, analyst: None)


def test_ignore_reason_rule(ctx):
    check_ignore_reason_rule(ctx)


# -- PROMOTE makes an entity once, and an Account never anchors on a handle ------------------------


def check_promote_item_to_entity(ctx):
    c = _client(ctx)
    body = {"act": "PROMOTE", "target": ITEM_TWO, "entity_type": "PersonCandidate", "anchor_claim": UNVERIFIED_CLAIM}
    r = c.send("POST", ACTS, body)
    assert r.status == 201, r.body
    recorded = r.json()["recorded"]
    s = open_case(c.root)
    try:
        node = s.conn.execute("SELECT * FROM node WHERE created_by_event_id = ?", (recorded,)).fetchone()
        assert node is not None and node["kind"] == "entity" and node["entity_type"] == "PersonCandidate"
        assert node["anchor_selector_type"] == "handle" and node["anchor_vouched"] == 1, dict(node)
    finally:
        s.close()
    r = c.send("POST", ACTS, body)
    assert r.status == 409 and r.json()["refused"] == "ACT_TARGET_ALREADY_PROMOTED", "an item was promoted twice"
    r = c.send("POST", ACTS, {"act": "REVOKE", "target": recorded, "reason": "promoted the wrong item"})
    assert r.status == 201, r.body
    r = c.send("POST", ACTS, dict(body, entity_type="Account"))
    assert r.status == 422 and "SELECTOR_ANCHOR_PROHIBITED" in r.json().get("detail", ""), "an Account anchored on a handle"


def break_promoted_check_removed(ctx):
    ctx.mp.setattr(acts, "promoted_by", lambda conn, case_id, item_event: None)


def test_promote_item_to_entity(ctx):
    check_promote_item_to_entity(ctx)


# -- EXCLUDE, NOTE and QUESTION land; the body is a closed shape ---------------------------------


def check_exclude_notes_and_closed_body(ctx):
    c = _client(ctx)
    r = c.send("POST", ACTS, {"act": "EXCLUDE", "target": REFERENCED_THIRD, "basis": "the declared location contradicts the anchor", "based_on": [HANDLE_CLAIM]})
    assert r.status == 201, r.body
    assert _node(c, REFERENCED_THIRD)["node"]["kind"] == "candidate", "the excluded node is not struck in place"
    node = selector_node_id(HANDLE_CLAIM)
    r = c.send("POST", ACTS, {"act": "NOTE", "target": HANDLE_CLAIM, "text": "compare against item 2 before citing"})
    assert r.status == 201, r.body
    r = c.send("POST", ACTS, {"act": "QUESTION", "target": HANDLE_CLAIM, "text": "is the platform id stable across the rename"})
    assert r.status == 201, r.body
    texts = [a["text"] for a in _node(c, node)["adjudications"]]
    assert any(t.startswith("note by analyst-example") for t in texts) and any(t.startswith("question by analyst-example") for t in texts), texts
    before = files_digest(c.root)
    r = c.send("POST", ACTS, {"act": "NOTE", "target": HANDLE_CLAIM, "text": "x", "confidence": 0.9})
    assert r.status == 400 and r.json()["refused"] == "BODY_REFUSED", "an unknown key reached the door"
    r = c.send("POST", ACTS, {"act": "DELETE", "target": HANDLE_CLAIM})
    assert r.status == 400 and r.json()["refused"] == "ACT_UNKNOWN"
    r = c.send("POST", ACTS, {"act": ["NOTE"], "target": HANDLE_CLAIM, "text": "x"})
    assert r.status == 400 and r.json()["refused"] == "ACT_UNKNOWN", "a non-string act was not refused as unknown"
    r = c.send("POST", ACTS, {"act": "NOTE", "target": HANDLE_CLAIM, "text": "y" * (acts.TEXT_MAX + 1)})
    assert r.status == 400 and r.json()["refused"] == "BODY_REFUSED"
    r = c.send("POST", ACTS, {"act": "NOTE", "target": HANDLE_CLAIM, "text": "z"}, cookie=False)
    assert r.status == 403 and r.json()["refused"] == "TOKEN_REFUSED"
    assert files_digest(c.root) == before, "a refused body wrote to the store"


def break_closed_keys_removed(ctx):
    ctx.mp.setattr(acts, "check_keys", lambda body, act: acts.ACTS[act])


def test_exclude_notes_and_closed_body(ctx):
    check_exclude_notes_and_closed_body(ctx)


CONTROLS = [
    ("the LOCAL_ACTS flag ignored", check_local_acts_refuse_until_decided, break_local_acts_flag_ignored),
    ("the acts handler records nothing", check_verify_lands_and_notifies_a_second_tab, break_acts_handler_records_nothing),
    ("the validator removed", check_model_refusals_reach_the_interface, break_validator_removed),
    ("the cluster projection removed", check_cluster_minted_and_revoked, break_cluster_projection_removed),
    ("the origin rule removed", check_local_acts_only_in_a_synthetic_case, break_origin_rule_removed),
    ("the ignore reason rule removed", check_ignore_reason_rule, break_ignore_rule_removed),
    ("the already-promoted check removed", check_promote_item_to_entity, break_promoted_check_removed),
    ("the closed-key check removed", check_exclude_notes_and_closed_body, break_closed_keys_removed),
]
