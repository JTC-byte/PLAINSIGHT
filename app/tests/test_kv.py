"""workspace_kv refuses any value that could carry case material."""

from __future__ import annotations

import uuid

from app.store import kv
from app.tests.helpers import CASE, corpus_events, eid_of, named, refusal_of


def check_free_string_refused(ctx):
    s = ctx.built()
    prose = named(corpus_events(), "adjudicate-note")["payload"]["text"]
    assert refusal_of(kv.put, s, CASE, "analyst-example", "web", "focus", prose).code == "KV_VALUE_REFUSED"
    assert refusal_of(kv.put, s, CASE, "analyst-example", "web", "query", 1).code == "KV_KEY_REFUSED"
    assert refusal_of(kv.put, s, CASE, "analyst-example", "web", "collapsed", ["emails", prose]).code == "KV_VALUE_REFUSED"
    assert refusal_of(kv.put, s, CASE, "analyst-example", "web", "columns", [["web"]]).code == "KV_VALUE_REFUSED"
    focus = eid_of("extract-claim-handle")
    kv.put(s, CASE, "analyst-example", "web", "focus", focus)
    kv.put(s, CASE, "analyst-example", "web", "hops", 2)
    kv.put(s, CASE, "analyst-example", "web", "drawer", "open")
    kv.put(s, CASE, "analyst-example", "web", "collapsed", ["emails", str(uuid.uuid5(uuid.UUID(CASE), "x"))])
    got = kv.get(s, CASE, "analyst-example", "web")
    assert got["focus"] == focus and got["hops"] == 2 and got["drawer"] == "open"


def break_kv_validator_removed(ctx):
    ctx.mp.setattr(kv, "legal_value", lambda value: True)


def break_kv_list_branch_open(ctx):
    real = kv.legal_value
    ctx.mp.setattr(kv, "legal_value", lambda value: True if isinstance(value, list) else real(value))


def test_free_string_refused(ctx):
    check_free_string_refused(ctx)


CONTROLS = [
    ("the kv value check removed", check_free_string_refused, break_kv_validator_removed),
    ("the kv list branch accepts anything", check_free_string_refused, break_kv_list_branch_open),
]
