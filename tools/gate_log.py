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
"""

from __future__ import annotations

import json
import os
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
#: written, so a caller cannot widen the record by accident.
ALLOWED = ("ts", "gate", "outcome", "code", "where", "count")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def record(gate: str, outcome: str, code: str = "", where: str = "", count: int = 0) -> None:
    """Append one gate record. Never raises, and never blocks a gate.

    Telemetry that can fail a gate is worse than no telemetry, so every failure
    path here is swallowed. A missing log is a gap in the pattern of life. A
    crashed gate is a gap in the enforcement.
    """
    if os.environ.get("PLAINSIGHT_NO_GATE_LOG"):
        return
    try:
        rec = {
            "ts": _now(),
            "gate": gate,
            "outcome": outcome,
            "code": code,
            "where": where,
            "count": count,
        }
        rec = {k: v for k, v in rec.items() if k in ALLOWED}
        LOG_DIR.mkdir(exist_ok=True)
        with LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        _sweep()
    except Exception:
        pass


def _sweep() -> None:
    """Drop records past the TTL. Inaction is deletion, per RETENTION.md."""
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
    """Per-gate counts over the retained window, for adjudication."""
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
        g["runs"] += 1
        if r.get("outcome") == "refuse":
            g["refusals"] += 1
            code = r.get("code") or "?"
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
        return 0
    print(__doc__.strip().splitlines()[0])
    print("usage: python tools/gate_log.py --summary")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
