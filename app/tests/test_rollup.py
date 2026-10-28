"""case_rollup: maintained on write, equal to a recount, bucketed by closed tokens only."""

from __future__ import annotations

from collections import Counter

from app.refusals import Refusal
from app.store import db, rollup
from app.tests.helpers import CASE, corpus_events, named, sql_error


def recount(store) -> Counter:
    """The test-only recount. No read path in app/ counts with COUNT(*)."""
    c: Counter = Counter()
    for r in store.conn.execute("SELECT event_type, event_subtype FROM event_skeleton WHERE case_id = ?", (CASE,)):
        c[("event_type", r[0])] += 1
        c[("event_subtype", f"{r[0]}.{r[1]}")] += 1
    for r in store.conn.execute("SELECT selector_type FROM claim"):
        c[("selector_type", r[0])] += 1
    for r in store.conn.execute("SELECT outcome FROM item"):
        c[("item_outcome", r[0])] += 1
    for r in store.conn.execute("SELECT kind, sector, entity_type FROM node"):
        c[("node_kind", r[0])] += 1
        if r[1]:
            c[("sector", r[1])] += 1
        if r[0] == "entity" and r[2]:
            c[("entity_type", r[2])] += 1
    for r in store.conn.execute("SELECT kind FROM edge"):
        c[("edge_kind", r[0])] += 1
    return c


def check_rollup_equals_recount(ctx):
    s = ctx.built()
    counted = recount(s)
    held = {(r["dimension"], r["bucket"]): r["n"] for r in s.conn.execute("SELECT * FROM case_rollup")}
    assert counted, "the recount saw rows"
    for key, n in counted.items():
        assert held.get(key) == n, f"rollup {key[0]} disagrees with the recount"
    for key, n in held.items():
        assert counted.get(key, 0) == n


def break_writer_disabled(ctx):
    ctx.mp.setattr(rollup, "increment", lambda conn, dimension, bucket, delta=1: None)


def test_rollup_equals_recount(ctx):
    check_rollup_equals_recount(ctx)


def check_value_bucket_refused(ctx):
    s = ctx.built()
    value = named(corpus_events(), "extract-claim-handle")["payload"]["value"]
    msg = sql_error(s.conn, "INSERT INTO case_rollup (dimension, bucket, n) VALUES ('selector_type', ?, 1)", (value,))
    assert msg.startswith("ROLLUP_BUCKET_REFUSED")
    msg = sql_error(s.conn, "UPDATE case_rollup SET bucket = ? WHERE dimension = 'selector_type'", (value[1:-1],))
    assert msg.startswith("ROLLUP_BUCKET_REFUSED")
    try:
        s.conn.execute("BEGIN")
        rollup.increment(s.conn, "selector_type", value)
    except Exception as exc:  # noqa: BLE001
        refusal = db.refusal_from(exc)
        assert isinstance(refusal, Refusal) and refusal.code == "ROLLUP_BUCKET_REFUSED"
    else:
        raise AssertionError("a value-shaped bucket was counted")
    finally:
        s.conn.execute("ROLLBACK")


def break_trigger_dropped(ctx):
    ctx.mp.setattr(db, "install_rollup_guard", lambda conn: None)


def test_value_bucket_refused(ctx):
    check_value_bucket_refused(ctx)


def test_vocabulary_is_closed_tokens():
    pairs = rollup.vocabulary()
    assert len(pairs) == len(set(pairs))
    dims = {d for d, _ in pairs}
    assert dims == set(rollup.DIMENSIONS)
    assert all(b and "<" not in b and " " not in b for _, b in pairs)


CONTROLS = [
    ("rollup writer disabled", check_rollup_equals_recount, break_writer_disabled),
    ("rollup_vocab trigger dropped", check_value_bucket_refused, break_trigger_dropped),
]
