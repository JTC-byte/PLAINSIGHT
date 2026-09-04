#!/usr/bin/env python3
"""Gate telemetry: what fired, what refused, and what never does either.

A gate nobody measures is a gate nobody can adjudicate. This records one line per
gate run so that keeping, tightening, loosening or retiring a check becomes a
decision made against a pattern of life rather than against a memory of the last
time it was annoying.

**The one rule that makes this safe: a telemetry record never carries the
offending value.** A `--repo-scan` refusal records the file and the line number
and the violation code. It does not record the selector-shaped string it matched.
Without that rule this log becomes the exact PII surface the gate exists to
prevent, and it would be a durable one, which is worse than the thing it was
watching for. `doctrine/RETENTION.md` RT-19 states it normatively.

The log is untracked and local by design. It rotates on a TTL rather than
growing, because a permanent record of tool behaviour is an archive and this is
telemetry.

Three things here were corrected on 2026-09-03 after the doctrine review found
each of them, and each fix is the one the review confirmed:

  T-01  `where` was an unconstrained string, so the rule above rested on every
        caller passing a location rather than a match. `_location()` now refuses
        anything that is not a repository-relative path with an optional line
        number, or a criterion or dotted identifier, and writes REDACTED_WHERE
        instead. The forthcoming `--repo-scan` is the caller with the strongest
        temptation to pass the matched string, and it now cannot.
  T-02  `ALLOWED` was credited by HY-1 and RT-19 as the mechanism preventing a
        widened record, and it filtered a dict built from exactly those keys, so
        it dropped nothing. `record()` now accepts and discards unknown keyword
        arguments, which makes the tuple load-bearing and the doctrine's
        sentence true.
  T-03  RT-19 says inaction is deletion, and the sweep ran only on write, so an
        idle repository retained records past the TTL and `--summary` rendered
        them. The sweep now runs on read as well.

One caller behaviour is also corrected here rather than in each validator:
HY-1 says one line per gate run, and a refusing validator wrote one line per
finding, which inflated both the run count and the refusal rate that HY-2
adjudicates against. `record_run()` writes the single run record and
`record_finding()` writes the per-finding detail, and `summary()` counts runs
from run records only.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / ".gate-log"
LOG = LOG_DIR / "gates.jsonl"

#: RT-19. Long enough for a pattern across several waves, short enough that it
#: is telemetry rather than an archive.
TTL_DAYS = 90

#: Fields a record may carry. Anything not listed is dropped rather than
#: written, so a caller cannot widen the record by accident. T-02: `record()`
#: swallows unknown keywords into `_ignored`, so this filter is the thing that
#: refuses them rather than a comprehension over a dict that never held them.
ALLOWED = ("ts", "gate", "outcome", "code", "where", "count")

#: T-01. What a location may look like. A repository-relative path with an
#: optional `:line`, a criterion id, or a dotted identifier such as a YAML path.
#: Deliberately narrow: a selector value, a bio, a display name and a quoted
#: match all fail it, which is the property HY-1 and RT-19 assert.
LOCATION_RE = re.compile(r"^[A-Za-z0-9_./\-]+(?::\d+)?(?: :: [A-Za-z0-9_.\-]+)?$")

#: Violation codes are upper snake case by convention across every validator.
CODE_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")

#: What is written when a caller passes something that is not a location. The
#: refusal is still counted, because losing the count would trade one silence
#: for another.
REDACTED = "REDACTED_WHERE"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _location(where: str) -> str:
    """Return `where` if it is shaped like a location, else the redaction.

    T-01. HY-1 says a record names the file and the line and never the string
    that matched, and before this check that rule was a caller convention. A
    caller that passes a matched value now writes a redaction rather than the
    value, and `doctrine/RETENTION.md` RT-19's reason is the whole point: a
    record quoting the match would turn the gate's own evidence into the durable
    surface the gate exists to prevent.
    """
    if not where:
        return ""
    return where if LOCATION_RE.match(where) and len(where) <= 200 else REDACTED


def record(
    gate: str,
    outcome: str,
    code: str = "",
    where: str = "",
    count: int = 0,
    **_ignored: object,
) -> None:
    """Append one gate record. Never raises, and never blocks a gate.

    Telemetry that can fail a gate is worse than no telemetry, so every failure
    path here is swallowed. A missing log is a gap in the pattern of life. A
    crashed gate is a gap in the enforcement.

    `_ignored` exists so `ALLOWED` is load-bearing rather than decorative. A
    caller that invents a field writes the six allowed keys and loses the
    seventh, instead of raising a TypeError outside this function's try.
    """
    if os.environ.get("PLAINSIGHT_NO_GATE_LOG"):
        return
    try:
        rec = {
            "ts": _now(),
            "gate": gate,
            "outcome": outcome,
            "code": code if CODE_RE.match(code or "") or not code else "CODE_MALFORMED",
            "where": _location(where),
            "count": count,
        }
        for key in _ignored:
            rec[str(key)] = None
        rec = {k: v for k, v in rec.items() if k in ALLOWED}
        LOG_DIR.mkdir(exist_ok=True)
        with LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        _sweep()
    except Exception:
        pass


def record_run(gate: str, outcome: str, count: int = 0) -> None:
    """Write the one record per gate run that HY-1 actually describes.

    `outcome` is `pass` or `refuse`, and `count` is the number of findings. A
    refusing run writes this once and then one `record_finding()` per finding,
    so the run count and the refusal rate HY-2 reads are the true ones.
    """
    record(gate, outcome, count=count)


def record_finding(gate: str, code: str = "", where: str = "") -> None:
    """Write one detail record for one finding inside a refusing run."""
    record(gate, "finding", code=code, where=where)


def _sweep() -> None:
    """Drop records past the TTL.

    T-03. Called on every write and on every read. RT-19 chose a write-triggered
    sweep over a scheduled job because the writer is already running, and a
    write-only sweep left an idle repository retaining records past the TTL and
    rendering them, which inverts the rule it was chosen to serve.
    """
    try:
        if not LOG.is_file():
            return
        cutoff = datetime.now(timezone.utc) - timedelta(days=TTL_DAYS)
        kept: list[str] = []
        dropped = 0
        for line in LOG.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                ts = datetime.fromisoformat(json.loads(line)["ts"])
            except Exception:
                dropped += 1
                continue
            if ts >= cutoff:
                kept.append(line)
            else:
                dropped += 1
        if dropped:
            LOG.write_text("\n".join(kept) + ("\n" if kept else ""), encoding="utf-8")
    except Exception:
        pass


def summary() -> dict:
    """Per-gate counts over the retained window, for adjudication.

    A run is a record whose outcome is `pass` or `refuse`. A `finding` record is
    detail inside a refusing run and is counted only in the code breakdown, so
    the run count and the refusal rate are the numbers HY-2 asks the operator to
    read rather than the number of findings that happened to be raised.

    Records written before 2026-09-03 carry no `finding` outcome, so their
    per-finding refuse records still count as runs. That over-counts refusals in
    the older window and is left visible rather than corrected, because
    rewriting a telemetry history to look consistent is the laundering design
    gate 6 forbids.
    """
    _sweep()
    out: dict[str, dict] = {}
    if not LOG.is_file():
        return out
    for line in LOG.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        g = out.setdefault(
            r.get("gate", "?"), {"runs": 0, "refusals": 0, "codes": {}, "first": None, "last": None}
        )
        outcome = r.get("outcome")
        if outcome in ("pass", "refuse"):
            g["runs"] += 1
        if outcome == "refuse":
            g["refusals"] += 1
        if outcome in ("refuse", "finding"):
            code = r.get("code") or "?"
            if code != "?":
                g["codes"][code] = g["codes"].get(code, 0) + 1
        ts = r.get("ts")
        if ts:
            g["first"] = min(g["first"] or ts, ts)
            g["last"] = max(g["last"] or ts, ts)
    return out


def main(argv: list[str]) -> int:
    if argv and argv[0] == "--summary":
        s = summary()
        if not s:
            print("gate_log: no records retained. Nothing to adjudicate yet.")
            return 0
        print(f"gate telemetry, retained window {TTL_DAYS}d, {LOG.relative_to(ROOT)}")
        print()
        for gate, g in sorted(s.items()):
            rate = (g["refusals"] / g["runs"] * 100) if g["runs"] else 0
            print(f"  {gate:24} runs={g['runs']:<5} refusals={g['refusals']:<5} ({rate:.0f}%)")
            for code, n in sorted(g["codes"].items(), key=lambda kv: -kv[1]):
                print(f"      {n:>4}  {code}")
            print(f"      window {g['first']} .. {g['last']}")
        print()
        print("Adjudication thresholds are in doctrine/HYGIENE.md HY-2.")
        print("A gate that never refuses and a gate that always refuses are both suspect.")
        print(
            "Telemetry is suppressed entirely while PLAINSIGHT_NO_GATE_LOG is set, "
            "which is the one legal opt-out and exists for test isolation."
        )
        return 0
    print(__doc__.strip().splitlines()[0])
    print("usage: python tools/gate_log.py --summary")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
