#!/usr/bin/env python3
"""The first test in this repository, and it exists for one reason.

`CLAUDE.md` design gate 1: a constraint is not done "until the constraint is a
schema `false`, a policy denylist, a gate that refuses, or a job that runs,
covered by a test that fails when the constraint is removed." Until 2026-09-03
no test of any kind was tracked here, so every mechanism on disk was an
assumption in exactly the sense `doctrine/HYGIENE.md` section 2 warns about: "A
gate nobody has watched fail is an assumption."

`tools/gate_log.py` is the mechanism `doctrine/HYGIENE.md` HY-1 and
`doctrine/RETENTION.md` RT-19 both point at, and it makes four checkable claims.
Each has a test below, and each test fails if the constraint is removed:

  1. A record never carries the string that matched (HY-1, RT-19). Removing
     `_location()` fails `test_matched_value_is_redacted`.
  2. A caller cannot widen the record (HY-1's fixed tuple). Removing the
     `ALLOWED` filter fails `test_unknown_field_is_dropped`.
  3. Records past the TTL are gone, on write and on read (RT-19). Removing
     either `_sweep()` call fails `test_ttl_sweeps_on_write` or
     `test_ttl_sweeps_on_read`.
  4. Telemetry never blocks a gate (HY-1). Making the log unwritable fails
     `test_recorder_never_raises`.

Plus one property of the repository rather than the module: the log is untracked
(RT-19), which `test_log_dir_is_gitignored` asserts through git itself.

Run with `python tools/tests/test_gate_log.py`, or `make test`. Stdlib only, no
pytest, because CI installs nothing that a gate depends on except PyYAML and a
test that needs a runner nobody has is a test that does not run.

Every test redirects the module's log path into a temporary directory, so
running this suite never writes to the repository's own `.gate-log/`.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import gate_log  # noqa: E402


class Redirected:
    """Point gate_log at a throwaway log for the duration of one test."""

    def __enter__(self) -> Path:
        self._tmp = tempfile.TemporaryDirectory()
        self._saved = (gate_log.LOG_DIR, gate_log.LOG)
        gate_log.LOG_DIR = Path(self._tmp.name) / ".gate-log"
        gate_log.LOG = gate_log.LOG_DIR / "gates.jsonl"
        return gate_log.LOG

    def __exit__(self, *exc: object) -> None:
        gate_log.LOG_DIR, gate_log.LOG = self._saved
        self._tmp.cleanup()


def _records(log: Path) -> list[dict]:
    if not log.is_file():
        return []
    return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_aged(log: Path, days: int, gate: str = "aged") -> None:
    """Plant a record dated `days` in the past, bypassing record()."""
    ts = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat(timespec="seconds")
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"ts": ts, "gate": gate, "outcome": "pass", "count": 0}) + "\n")


# --------------------------------------------------------------------------
# 1. A record never carries the string that matched.
# --------------------------------------------------------------------------


def test_location_shapes_are_accepted() -> None:
    """A path, a path with a line, and a criterion id are all locations."""
    for good in ("doctrine/RETENTION.md", "doctrine/RETENTION.md:412", "RT-19", "SS-14",
                 "event_types.PROBE_EVENT.lineage", "tools/gate_log.py:64"):
        assert gate_log._location(good) == good, f"rejected a real location: {good!r}"


def test_matched_value_is_redacted() -> None:
    """A caller that passes something other than a location writes a redaction.

    The values below are the shapes a `--repo-scan` refusal would be tempted to
    pass: a quoted match, a value with spaces, a value with an at sign, a
    sentence. None of them is a location and none of them reaches the log.
    """
    with Redirected() as log:
        for bad in ('"a matched string"', "a value with spaces", "name@example.test",
                    "found j_voss_88 in line", "+1 555 0100"):
            gate_log.record("scan", "finding", code="FIXTURE_CONTAINS_LIVE_SELECTOR", where=bad)
        wheres = [r["where"] for r in _records(log)]
        assert wheres, "nothing was written"
        assert all(w == gate_log.REDACTED for w in wheres), f"a value survived: {wheres}"
        # The refusal is still counted, which is the reason for redacting rather
        # than dropping the record.
        assert len(wheres) == 5


def test_redaction_does_not_lose_the_code() -> None:
    """A redacted location keeps the violation code, so HY-2 can still read it."""
    with Redirected() as log:
        gate_log.record("scan", "finding", code="FIXTURE_CONTAINS_LIVE_SELECTOR", where="a match")
        rec = _records(log)[0]
        assert rec["code"] == "FIXTURE_CONTAINS_LIVE_SELECTOR"
        assert rec["where"] == gate_log.REDACTED


def test_malformed_code_is_named_not_written() -> None:
    """A code that is not upper snake case is replaced rather than recorded."""
    with Redirected() as log:
        gate_log.record("scan", "finding", code="a selector value posing as a code")
        assert _records(log)[0]["code"] == "CODE_MALFORMED"


# --------------------------------------------------------------------------
# 2. A caller cannot widen the record.
# --------------------------------------------------------------------------


def test_unknown_field_is_dropped() -> None:
    """An invented field is discarded, and the record is still written.

    HY-1 credits `ALLOWED` with this. Before 2026-09-03 the filter ran over a
    dict built from exactly those keys and an extra keyword raised outside the
    recorder's try, so the claim was true by accident of the signature. Now the
    tuple is what refuses it.
    """
    with Redirected() as log:
        gate_log.record("doctrine", "pass", offending_value="a selector", extra=1)
        rec = _records(log)[0]
        assert set(rec) <= set(gate_log.ALLOWED), f"record widened: {sorted(rec)}"
        assert "offending_value" not in rec
        assert rec["gate"] == "doctrine"


# --------------------------------------------------------------------------
# 3. Records past the TTL are gone, on write and on read.
# --------------------------------------------------------------------------


def test_ttl_sweeps_on_write() -> None:
    with Redirected() as log:
        _write_aged(log, gate_log.TTL_DAYS + 1)
        assert len(_records(log)) == 1
        gate_log.record("doctrine", "pass")
        gates = [r["gate"] for r in _records(log)]
        assert "aged" not in gates, "a record past the TTL survived a write"
        assert gates == ["doctrine"]


def test_ttl_sweeps_on_read() -> None:
    """RT-19: inaction is deletion. An idle log must not render expired records."""
    with Redirected() as log:
        _write_aged(log, gate_log.TTL_DAYS + 10)
        assert len(_records(log)) == 1
        gate_log.summary()
        assert _records(log) == [], "summary() rendered a record past the TTL"


def test_ttl_keeps_a_record_inside_the_window() -> None:
    with Redirected() as log:
        _write_aged(log, gate_log.TTL_DAYS - 1)
        gate_log.summary()
        assert len(_records(log)) == 1, "a record inside the window was swept"


# --------------------------------------------------------------------------
# 4. Telemetry never blocks a gate.
# --------------------------------------------------------------------------


def test_recorder_never_raises() -> None:
    """An unwritable log costs a gap in the pattern of life, never a gate."""
    with Redirected() as log:
        # A file where the directory must go, so mkdir and open both fail.
        log.parent.parent.mkdir(parents=True, exist_ok=True)
        log.parent.write_text("not a directory", encoding="utf-8")
        gate_log.record("doctrine", "pass")  # must not raise
        gate_log.record_run("doctrine", "refuse", count=2)
        gate_log.record_finding("doctrine", code="X", where="a/b.md:1")


def test_opt_out_is_honoured_and_is_the_only_one(monkeypatch_env: object = None) -> None:
    """PLAINSIGHT_NO_GATE_LOG suppresses the record. HY-1 names it as legal."""
    import os

    with Redirected() as log:
        os.environ["PLAINSIGHT_NO_GATE_LOG"] = "1"
        try:
            gate_log.record("doctrine", "pass")
            assert _records(log) == [], "the opt-out did not suppress the record"
        finally:
            del os.environ["PLAINSIGHT_NO_GATE_LOG"]
        gate_log.record("doctrine", "pass")
        assert len(_records(log)) == 1, "recording did not resume once the opt-out cleared"


# --------------------------------------------------------------------------
# The run and finding split, which is what HY-1 describes.
# --------------------------------------------------------------------------


def test_summary_counts_runs_not_findings() -> None:
    """Ten clean runs plus one refusing run with three findings is 11 runs, 1 refusal.

    Before the split this rendered as 13 runs and 3 refusals, a 23 percent
    refusal rate against a true 9 percent, and HY-2's "Refuses on nearly every
    run" reading is exactly what that distorts.
    """
    with Redirected():
        for _ in range(10):
            gate_log.record_run("doctrine", "pass")
        gate_log.record_run("doctrine", "refuse", count=3)
        for code in ("DOCTRINE_REF_DANGLING", "DOCTRINE_COUNT_DRIFT", "DOCTRINE_COUNT_DRIFT"):
            gate_log.record_finding("doctrine", code=code, where="doctrine/RETENTION.md:1")
        s = gate_log.summary()["doctrine"]
        assert s["runs"] == 11, s
        assert s["refusals"] == 1, s
        assert s["codes"]["DOCTRINE_COUNT_DRIFT"] == 2, s


# --------------------------------------------------------------------------
# A property of the repository, not of the module.
# --------------------------------------------------------------------------


def test_log_dir_is_gitignored() -> None:
    """RT-19: the log is untracked, and a telemetry file in git is permanent."""
    proc = subprocess.run(
        ["git", "check-ignore", "-q", ".gate-log/gates.jsonl"],
        cwd=ROOT,
        capture_output=True,
    )
    assert proc.returncode == 0, ".gate-log/ is not ignored, so telemetry can reach git"


def main() -> int:
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    failed = []
    for name, fn in tests:
        try:
            fn()
            print(f"  ok       {name}")
        except AssertionError as exc:
            failed.append((name, str(exc)))
            print(f"  FAILED   {name}\n           {exc}")
        except Exception as exc:  # a test that errors is a failed test
            failed.append((name, repr(exc)))
            print(f"  ERROR    {name}\n           {exc!r}")
    print()
    if failed:
        print(f"test_gate_log: {len(failed)} of {len(tests)} failed", file=sys.stderr)
        print(
            "  rule:  CLAUDE.md design gate 1, doctrine/HYGIENE.md HY-1, "
            "doctrine/RETENTION.md RT-19",
            file=sys.stderr,
        )
        print(
            "  moves: fix tools/gate_log.py, or amend the criterion and this test together",
            file=sys.stderr,
        )
        return 1
    print(f"test_gate_log ok: {len(tests)} tests, HY-1 and RT-19 exercised against the code")
    return 0


if __name__ == "__main__":
    sys.exit(main())
