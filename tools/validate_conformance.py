#!/usr/bin/env python3
"""The aggregator. One authoritative gate list, and an honest pending set.

`ZMeta/zmeta-spec/tools/validate_conformance.py` keeps `KERNEL_GATE_CHECKS` as
the single list its `--kernel-gate` flag expands to, so a new sub-check joins the
gate in one place instead of in every document that quotes the command. That is
the pattern carried here.

One thing is added, because this repository is at a different stage. ZMeta's
checks all exist. Most of PLAINSIGHT's do not, because the artifacts they would
check are not built. **A check that is not implemented is reported as PENDING and
never as a pass.** The failure this prevents is the one the program has already
measured once: `tools/validate_retention.py` is wired into the pre-commit hook
and returns 0 while checking nothing, and it is only harmless because it says so
on every run. An aggregator that counted it as green would convert a known gap
into a silent one.

Exit codes: 0 every implemented check passed, 1 an implemented check failed,
2 the gate list itself is inconsistent with the tree.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable

IMPLEMENTED = "implemented"
STUB = "stub"
PENDING = "pending"

#: THE ONE AUTHORITATIVE GATE LIST.
#:
#: A new check joins the gate here and nowhere else. Every entry is
#: (token, argv, state, note). `note` on a pending entry names the step that
#: delivers it, so the gap is a scheduled gap rather than an unexplained one.
KERNEL_GATE = (
    (
        "doctrine",
        [PY, "tools/validate_doctrine.py", "--quiet"],
        IMPLEMENTED,
        "criterion definitions, stamps, cross-references, and the pin of record",
    ),
    (
        "hygiene",
        [PY, "tools/validate_hygiene.py", "--quiet"],
        IMPLEMENTED,
        "voice, table structure, citations against the artifact register, caps, and the handoff's tense",
    ),
    (
        "layer-model",
        [PY, "tools/validate_layer_model.py", "--quiet"],
        IMPLEMENTED,
        "the nine types, discriminators, denylists, lineage, producer authority, "
        "strata, and the D5 parent on RUN_START",
    ),
    (
        "cast",
        [PY, "tools/validate_cast.py", "--placeholder-scan", "--quiet"],
        IMPLEMENTED,
        "the checkable half of SS-3, the confuser pair, the partition, the seal, "
        "and no filled value while unsealed",
    ),
    (
        "telemetry",
        [PY, "tools/tests/test_gate_log.py"],
        IMPLEMENTED,
        "HY-1 and RT-19 exercised against tools/gate_log.py: never the matched "
        "value, no widened record, the TTL on write and on read, and a gate a "
        "crashed recorder cannot block",
    ),
    (
        "retention-repo-scan",
        [PY, "tools/validate_retention.py", "--repo-scan"],
        STUB,
        "D-001. Wired into .githooks/pre-commit and checks nothing. Step 8",
    ),
    (
        "schema",
        [PY, "tools/validate.py", "--kernel", "--quiet"],
        IMPLEMENTED,
        "the generated schema, policy pack and corpora current against "
        "spec/layer-model.yaml; every must-pass event clean; every must-fail "
        "fixture refused for its expected code, and for that code alone where "
        "the model requires it; and the runner's own self-test",
    ),
    (
        "ontology",
        [PY, "tools/validate_ontology.py", "--quiet"],
        IMPLEMENTED,
        "the closed selector vocabulary: required fields, the constraint rule, "
        "anchor agreement with the entity types, prohibitions, matchers, and "
        "the code vocabulary reconciled against the layer model",
    ),
    (
        "authorization",
        None,
        PENDING,
        "Step 8. policy/subject-authorization.yaml does not exist. This is the "
        "D5 mechanism and no run may execute before it does",
    ),
    (
        "retention-policy",
        None,
        PENDING,
        "Step 8. policy/retention.yaml does not exist",
    ),
    (
        "divergence-register",
        None,
        PENDING,
        "Step 9. spec/divergence-register.yaml does not exist",
    ),
    (
        "connector-conformance",
        None,
        PENDING,
        "Step 12. No connector exists",
    ),
)


def run(argv: list[str]) -> tuple[int, str]:
    proc = subprocess.run(
        argv, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Aggregate conformance gate.")
    ap.add_argument(
        "--kernel-gate",
        action="store_true",
        help="Run every implemented check in KERNEL_GATE. This is the single "
        "named form of the gate, so the battery is one stable token rather than "
        "a hand-copied list of commands.",
    )
    ap.add_argument(
        "--list",
        action="store_true",
        help="Print the gate list with each check's state and exit.",
    )
    args = ap.parse_args(argv)

    if args.list:
        for token, _, state, note in KERNEL_GATE:
            print(f"  {state.upper():12} {token:24} {note}")
        return 0

    if not args.kernel_gate:
        ap.error("nothing to do: pass --kernel-gate or --list")

    # The gate list must agree with the tree, in both directions.
    for token, cmd, state, _ in KERNEL_GATE:
        if state in (IMPLEMENTED, STUB) and cmd is not None:
            if not (ROOT / cmd[1]).is_file():
                print(
                    f"REFUSED GATE_LIST_INCONSISTENT\n"
                    f"  where: {token}\n"
                    f"  what:  the gate list marks this {state} and names {cmd[1]}, "
                    f"which does not exist, so the gate would fail for the wrong reason\n"
                    f"  moves: write the tool, or move the entry to {PENDING}",
                    file=sys.stderr,
                )
                return 2
        if state == PENDING and cmd is not None:
            print(
                f"REFUSED GATE_LIST_INCONSISTENT\n"
                f"  where: {token}\n"
                f"  what:  marked pending but carries a command, which would run "
                f"while being reported as not implemented\n"
                f"  moves: mark it {IMPLEMENTED}, or drop the command",
                file=sys.stderr,
            )
            return 2

    failed: list[str] = []
    ran = stubbed = pending = 0

    for token, cmd, state, note in KERNEL_GATE:
        if state == PENDING:
            pending += 1
            print(f"  PENDING      {token:24} {note}")
            continue
        code, out = run(cmd)
        if state == STUB:
            stubbed += 1
            print(f"  STUB         {token:24} {note}")
            continue
        ran += 1
        if code == 0:
            print(f"  ok           {token:24} {note}")
        else:
            failed.append(token)
            print(f"  FAILED       {token:24} {note}")
            for line in out.strip().splitlines():
                print(f"               | {line}")

    print()
    print(
        f"kernel-gate: {ran} implemented, {len(failed)} failed, "
        f"{stubbed} stubbed, {pending} pending"
    )
    if stubbed or pending:
        print(
            "  A stubbed or pending check is not a passing check. "
            "See docs/plainsight_handoff.md section 4."
        )
    if failed:
        print(f"  failing: {', '.join(failed)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
