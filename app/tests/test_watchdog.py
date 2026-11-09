"""runner/watchdog.py: an interval a collector left open is closed by event, at its
last verification, only after three poll intervals, and never in place."""

from __future__ import annotations

import datetime as dt
import uuid

from app.model import reads
from app.store import ingest
from app.tests.helpers import CASE, sql_error
from runner import watchdog

T0 = dt.datetime(2026, 1, 15, 11, 0, 0, tzinfo=dt.timezone.utc)


def _at(seconds: int) -> dt.datetime:
    return T0 + dt.timedelta(seconds=seconds)


def _iso(when: dt.datetime) -> str:
    return when.isoformat().replace("+00:00", "Z")


def plant_open(store, target_ref: str, poll: int = 60, verified_at: dt.datetime | None = None) -> str:
    """An open working row: started at T0, last verified at T0+120 unless given, polled every `poll` seconds."""
    interval_id = str(uuid.uuid5(uuid.UUID(CASE), f"open interval {target_ref} {poll}"))
    store.conn.execute(
        "INSERT INTO coverage_interval (interval_id, case_id, target_ref, t_start, last_verified_at, poll_interval_s, "
        "state, verified, method) VALUES (?, ?, ?, ?, ?, ?, 'open', 1, 'poll')",
        (interval_id, CASE, target_ref, _iso(T0), _iso(verified_at or _at(120)), poll),
    )
    store.conn.commit()
    return interval_id


def _row(store, interval_id: str):
    return store.conn.execute("SELECT * FROM coverage_interval WHERE interval_id = ?", (interval_id,)).fetchone()


def check_watchdog_closes_by_event_after_three_polls(ctx):
    s = ctx.built()
    target = s.conn.execute("SELECT target_ref FROM coverage_interval").fetchone()["target_ref"]
    open_id = plant_open(s, target)
    closed, refused = watchdog.sweep(s, now=_at(299))
    assert closed == [] and refused == [], "a sweep at 299 s closed something: three polls of 60 s had not passed"
    assert _row(s, open_id)["state"] == "open"
    closed, refused = watchdog.sweep(s, now=_at(301))
    assert refused == [], refused
    assert len(closed) == 1, "a sweep at 301 s did not close the one overdue interval"
    eid = closed[0]
    assert _row(s, open_id) is None, "the working row was kept beside the closed row"
    row = s.conn.execute("SELECT * FROM coverage_interval WHERE closed_by_event_id = ?", (eid,)).fetchone()
    assert row is not None, "no closed row names the closing event"
    assert row["state"] == "closed" and row["t_end"] == _iso(_at(120)), "t_end is not the last verification"
    assert row["closed_by_producer"] == watchdog.PRODUCER and row["interval_id"] == eid
    event = reads.event(s.conn, CASE, eid)
    assert event is not None and (event["type"], event["subtype"]) == ("SYSTEM_EVENT", "COVERAGE_INTERVAL")
    assert event["producer"] == watchdog.PRODUCER and event["payload"]["t_end"] == _iso(_at(120))
    msg = sql_error(s.conn, "UPDATE coverage_interval SET t_end = t_start WHERE interval_id = ?", (eid,))
    assert msg.startswith("COVERAGE_CLOSED_IMMUTABLE")
    again, _ = watchdog.sweep(s, now=_at(10_000))
    assert again == [], "a closed interval was closed again"


def break_multiplier_four(ctx):
    ctx.mp.setattr(watchdog, "MULTIPLIER", 4)


def break_closes_in_place_without_an_event(ctx):
    def in_place(store, env, humans=None):
        p = env["payload"]
        store.conn.execute(
            "UPDATE coverage_interval SET state = 'closed', t_end = ?, closed_by_event_id = ?, closed_by_producer = ? "
            "WHERE case_id = ? AND target_ref = ? AND t_start = ? AND state = 'open'",
            (p["t_end"], env["event"]["event_id"], watchdog.PRODUCER, env["case_id"], p["target_ref"], p["t_start"]),
        )
        store.conn.commit()
        return ingest.IngestResult(env["case_id"], 1, 0)

    ctx.mp.setattr(watchdog, "_emit", in_place)


def test_watchdog_closes_by_event_after_three_polls(ctx):
    check_watchdog_closes_by_event_after_three_polls(ctx)


def check_watchdog_refuses_a_local_case_that_is_not_synthetic(ctx):
    s = ctx.built()
    target = s.conn.execute("SELECT target_ref FROM coverage_interval").fetchone()["target_ref"]
    open_id = plant_open(s, target)
    s.conn.execute("UPDATE case_registry SET synthetic = 0 WHERE case_id = ?", (CASE,))
    s.conn.commit()
    closed, refused = watchdog.sweep(s, now=_at(301))
    assert closed == [] and len(refused) == 1 and refused[0].endswith("ACT_LOCAL_SYNTHETIC_CASE_ONLY"), refused
    assert _row(s, open_id)["state"] == "open", "the row closed although the door refused"
    assert s.conn.execute(
        "SELECT COUNT(*) FROM event_skeleton WHERE case_id = ? AND producer = ?", (CASE, watchdog.PRODUCER)
    ).fetchone()[0] == 1, "a second COVERAGE_INTERVAL under runner-watchdog landed on a LOCAL case not marked synthetic"


def break_origin_rule_removed(ctx):
    ctx.mp.setattr(ingest, "origin_allowed", lambda store, case_id, origin: None)


def test_watchdog_refuses_a_local_case_that_is_not_synthetic(ctx):
    check_watchdog_refuses_a_local_case_that_is_not_synthetic(ctx)


def check_watchdog_leaves_a_row_with_no_verification_state_open(ctx):
    """A working row that never recorded whether its coverage was verified carries no
    fact a closing event could state, so it is reported and left open (gate 6)."""
    s = ctx.built()
    target = s.conn.execute("SELECT target_ref FROM coverage_interval").fetchone()["target_ref"]
    open_id = plant_open(s, target)
    s.conn.execute("UPDATE coverage_interval SET verified = NULL WHERE interval_id = ?", (open_id,))
    s.conn.commit()
    closed, refused = watchdog.sweep(s, now=_at(301))
    assert closed == [] and len(refused) == 1 and "VERIFICATION_STATE_UNKNOWN" in refused[0], (closed, refused)
    assert _row(s, open_id)["state"] == "open", "a row with no verification state was closed"
    assert s.conn.execute(
        "SELECT COUNT(*) FROM event_skeleton WHERE case_id = ? AND producer = ?", (CASE, watchdog.PRODUCER)
    ).fetchone()[0] == 1, "a closing event invented a verification state"


def break_unknown_state_read_as_verified(ctx):
    ctx.mp.setattr(watchdog, "state_unknown", lambda row: None)


def test_watchdog_leaves_a_row_with_no_verification_state_open(ctx):
    check_watchdog_leaves_a_row_with_no_verification_state_open(ctx)


CONTROLS = [
    ("the multiplier patched to 4", check_watchdog_closes_by_event_after_three_polls, break_multiplier_four),
    ("the closer updates the row in place", check_watchdog_closes_by_event_after_three_polls, break_closes_in_place_without_an_event),
    ("the origin rule removed", check_watchdog_refuses_a_local_case_that_is_not_synthetic, break_origin_rule_removed),
    ("an unknown verification state read as verified", check_watchdog_leaves_a_row_with_no_verification_state_open, break_unknown_state_read_as_verified),
]
