"""Act requests from the interface. This slice carries one: the deep dive.

A deep dive takes exactly one node and one motivating claim per act
(doctrine/SUBJECT_SELECTION.md SS-16, amendment 9.11). A body naming two nodes is
refused with DEEP_DIVE_ONE_NODE_PER_ACT.

In this change the route always refuses, writes nothing, and imports nothing
from runner/. While runner/subject_guard.py does not exist it returns "NOT
DISPATCHED, no subject gate exists yet (Step 10): nothing was collected" with
the legal moves. If the gate file appears, the route still refuses, saying the
gate is not connected to it: connecting them is a separate change, Class F by
effect, decided by the operator. The legal moves name only keys this slice
builds (l, v and 8) and the operator's act; app/tests/test_static.py fails when
a refusal names a key the keymap marks as not built.

The app never emits a COLLECT_EVENT, never mints an AUTHORIZE_EVENT GRANT or an
SS-4 record, and p mints no VERIFY. app/tests/test_http.py scans app/ for any
constructor of either event type and for any import of runner.

The analyst acts (VERIFY, DISPUTE, NOTE, QUESTION, IGNORE, EXCLUDE, PROMOTE,
CLUSTER on POST /acts) are slice 3 and are not built.
"""

from __future__ import annotations

from app import config
from app.model import reads
from app.refusals import REFUSALS, Refusal

GATE = config.REPO_ROOT / "runner" / "subject_guard.py"

BODY_KEYS = frozenset({"node_id", "motivating_claim"})
PLURAL_KEYS = frozenset({"node_ids", "nodes", "targets"})


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
