"""The external watchdog that closes a coverage interval a collector did not close.

docs/PLAINSIGHT-design.md section 8.2 item 2: a crashed collector does not write
"I stopped", so an interval is closed by a watchdog when now minus
last_verified_at exceeds three times the poll interval, with its end at the
last verification. Amendment 9.6 records how that closes here: PSE's
COVERAGE_INTERVAL has no reason field, so the closer is the closing event's
producer, runner-watchdog, and an open interval is a working row that becomes
an artifact row, immutable by trigger, when its closing event is appended.

This module reads the open rows of every case the store holds, appends one
SYSTEM_EVENT COVERAGE_INTERVAL per overdue row through the same door every
corpus row passes (app/store/ingest.py, origin "system"), and updates nothing
in place. The projector replaces the working row with the closed row. On LOCAL
the door lands the event only in a case whose registry row says synthetic
(reading APP-R31), and a refusal is reported rather than swallowed.

Run as python -m runner.watchdog --store ROOT [--once] [--every SECONDS]
[--now ISO]. Amendment 9.18: the command lives here rather than under
python -m app, because app/ imports nothing from runner/ (app/tests/test_http.py
scans for such an import), and the design brief's "watchdog subcommand" is read
as this module's own command. --now is for tests and replays and names the
instant the sweep reads as now.

Exit codes: 0 swept (whether or not anything closed), 1 a refusal, 2 the
command line could not be read.
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
import time
import uuid

from app import __version__
from app.refusals import Refusal
from app.store import door, ingest, retention
from app.store.db import Store

#: Design 8.2 item 2: now - last_verified_at > MULTIPLIER × poll_interval closes the interval.
MULTIPLIER = 3

#: The producer the closing event is written under (amendment 9.6).
PRODUCER = "runner-watchdog"


def _now_iso(now: dt.datetime) -> str:
    return retention.format_ts(now.replace(microsecond=0))


def overdue(store, now: dt.datetime) -> list[dict]:
    """Open working rows whose last verification is older than MULTIPLIER poll intervals, across cases."""
    rows = store.conn.execute(
        "SELECT * FROM coverage_interval WHERE state = 'open' AND last_verified_at IS NOT NULL "
        "AND poll_interval_s IS NOT NULL ORDER BY case_id, t_start, interval_id"
    ).fetchall()
    out = []
    for r in rows:
        age = (now - retention.parse_ts(r["last_verified_at"])).total_seconds()
        if age > MULTIPLIER * int(r["poll_interval_s"]):
            out.append(dict(r))
    return out


def closing_event(store, row: dict, now: dt.datetime) -> dict:
    """The COVERAGE_INTERVAL that closes `row` at its last verification. SYSTEM_EVENT carries no lineage."""
    props = door.load_policy().schema["properties"]
    return {
        "pse_version": props["pse_version"]["const"],
        "derived_from": props["derived_from"]["const"],
        "case_id": row["case_id"],
        "event": {
            "event_id": str(uuid.uuid4()),
            "event_type": "SYSTEM_EVENT",
            "event_subtype": "COVERAGE_INTERVAL",
            "ts": _now_iso(now),
        },
        "source": {
            "platform_id": ingest.STORE_PLATFORM_ID,
            "environment": store.environment,
            "producer": PRODUCER,
            "sw_version": __version__,
        },
        "payload": {
            "system_type": "COVERAGE_INTERVAL",
            "target_ref": row["target_ref"],
            "t_start": row["t_start"],
            "t_end": row["last_verified_at"],
            "verified": bool(row["verified"]),
            "method": row["method"],
        },
    }


def state_unknown(row: dict) -> str | None:
    """Why `row` cannot be closed by this watchdog, or None.

    The closing event must state whether the coverage was verified and by what
    method (design section 6.1: a verified interval and an unverified one are
    different facts). A working row that recorded neither carries no fact to
    state, and inventing one would make silence look like watching (CLAUDE.md
    gate 6), so the row is left open and reported."""
    if row.get("verified") is None:
        return "the open row carries no verification state, so no closing event can state one; the row is left open"
    if not row.get("method"):
        return "the open row carries no method, so no closing event can state one; the row is left open"
    return None


def _emit(store, env: dict, humans=None) -> ingest.IngestResult:
    """One closing event through the door. Named so a test can show the row closes by event alone."""
    return ingest.ingest_batch(store, [env], humans, origin="system")


def sweep(store, now: dt.datetime | None = None, humans=None) -> tuple[list[str], list[str]]:
    """Close every overdue interval. Returns (closing event ids, refusal texts)."""
    now = now or dt.datetime.now(dt.timezone.utc)
    closed: list[str] = []
    refused: list[str] = []
    for row in overdue(store, now):
        why = state_unknown(row)
        if why is not None:
            refused.append(f"{row['case_id'][:8]} {row['interval_id'][:8]}: VERIFICATION_STATE_UNKNOWN, {why}")
            continue
        env = closing_event(store, row, now)
        try:
            result = _emit(store, env, humans)
        except Refusal as refusal:
            refused.append(f"{row['case_id'][:8]} {row['interval_id'][:8]}: {refusal.code}")
            continue
        if result.landed:
            closed.append(env["event"]["event_id"])
    return closed, refused


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m runner.watchdog", description="Close coverage intervals whose collector went quiet.")
    ap.add_argument("--store", help="store root; default $PLAINSIGHT_HOME, else %%LOCALAPPDATA%%\\plainsight")
    ap.add_argument("--once", action="store_true", help="one sweep, then exit")
    ap.add_argument("--every", type=int, default=60, help="seconds between sweeps when not --once (default 60)")
    ap.add_argument("--now", help="the instant read as now, ISO 8601 with a zone; for tests and replays")
    try:
        args = ap.parse_args(argv)
    except SystemExit as exit_:
        # argparse exits 0 after printing help and 2 when the line could not be read.
        return 0 if exit_.code == 0 else 2
    now = retention.parse_ts(args.now) if args.now else None
    try:
        with Store.open(args.store) as store:
            while True:
                closed, refused = sweep(store, now)
                for eid in closed:
                    print(f"closed one interval by COVERAGE_INTERVAL {eid[:8]} under {PRODUCER}")
                for line in refused:
                    print(f"refused: {line}", file=sys.stderr)
                if not closed and not refused:
                    print("nothing overdue: every open interval was verified within three poll intervals")
                if args.once or now is not None:
                    return 1 if refused else 0
                time.sleep(max(1, args.every))
    except Refusal as refusal:
        print(refusal.render(), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
