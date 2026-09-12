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
measured once: the Wave 0 `tools/validate_retention.py` was wired into the
pre-commit hook and returned 0 while checking nothing, and it stayed harmless
only because it said so on every run. An aggregator that counted it as green
would have converted a known gap into a silent one. Step 8 replaced that stub
with a tool that reads the tree, so no entry carries STUB today, and the state
stays in the list because the next stub is easier to declare than to notice.

A fourth state joined the list at Step 8, because two mechanisms landed that are
implemented and refuse. `policy/subject-authorization.yaml`,
`policy/retention.yaml` and the two conformance artifacts beside them are Class F
and carry no dated row in `doctrine/DOCTRINE_STATUS.md`, and an unratified
criterion refuses rather than permits. **An UNRATIFIED entry runs its command and
asserts the refusal.** Exit 1 is the state the entry describes. Exit 2 means a
governed input could not be read, which is a failure of the tool rather than the
state, so it is reported as one. Exit 0 means the entry itself is now wrong,
because the check permits and the list still says it refuses, and that is refused
as a gate-list inconsistency. The inversion is what keeps a designed refusal
distinguishable from a broken tree, which is the distinction the PENDING rule
protects at the other end.

Exit codes: 0 every implemented check passed and every unratified check refused,
1 an implemented check failed, 2 the gate list itself is inconsistent with the
tree.
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
UNRATIFIED = "unratified"

#: THE ONE AUTHORITATIVE GATE LIST.
#:
#: A new check joins the gate here and nowhere else. Every entry is
#: (token, argv, state, note). `note` on a pending entry names the step that
#: delivers it, so the gap is a scheduled gap rather than an unexplained one.
#: `note` on an unratified entry names what the check reads and which artifact
#: has no dated row, so the refusal is a state an operator can clear rather than
#: a failure somebody has to diagnose.
#:
#: A token is the token the tool itself declares to `tools/gate_log.py`, so the
#: telemetry in `make gate-telemetry` and the list below name the same thing.
#: `tools/validate_retention.py` declares one token per mode and
#: `tools/validate_authorization.py` declares one for the tool, and the entries
#: follow each tool rather than imposing one shape on both.
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
        [PY, "tools/validate_retention.py", "--repo-scan", "--quiet"],
        IMPLEMENTED,
        "RT-15, and D-001 closed at Step 8. Every tracked file in the working "
        "tree read for a filled selector in its typed form, against thirteen "
        "shapes reconciled with ontology/selectors.yaml in both directions. "
        "Three of RT-15's four parts: the code the criterion names is not in the "
        "wire vocabulary, and git history is out of reach of any commit-time "
        "check. The pre-commit hook runs the same mode over the index",
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
        [PY, "tools/validate_authorization.py", "--fixtures", "--quiet"],
        UNRATIFIED,
        "--fixtures. SS-4's nine-field record against the schema's closed "
        "property set, SS-5's three differential fixtures, the gate value, "
        "basis, relation and disposition enums reconciled against rank 3, the "
        "register in both directions, and SS-14's stamp read. It refuses because "
        "six of the nine paths SS-14 item 6 names carry no dated row, so no run "
        "may execute. --self-test is green and is a Makefile target of its own",
    ),
    (
        "authorization-dispatch-paths",
        None,
        PENDING,
        "Step 10. SS-6's subject is runner/, which is empty, so the scan would "
        "find zero ungated call sites and exit clean while nothing is gated",
    ),
    (
        "authorization-disjointness",
        None,
        PENDING,
        "SS-20 and CR-1. The credential pool never exists on LOCAL under EG-4 "
        "and CR-4 and no pool inventory artifact exists anywhere, so the "
        "comparison against synthetic/CAST.md runs in ISOLATED once a pool is "
        "provisioned",
    ),
    (
        "retention-policy",
        [PY, "tools/validate_retention.py", "--policy", "--quiet"],
        UNRATIFIED,
        "--policy. RT-1's seven strata rows across five numbered levels plus "
        "telemetry, RT-2's subject-carrying fields against the surviving strata, "
        "the stamped durations, and RT-9's five verification checks with their "
        "false-pass guards. It refuses because policy/retention.yaml carries no "
        "dated row, which for a retention mechanism means the sweep refuses to "
        "run rather than running with an unratified TTL",
    ),
    (
        "retention-shred-roundtrip",
        [PY, "tools/validate_retention.py", "--shred-roundtrip", "--quiet"],
        UNRATIFIED,
        "--shred-roundtrip. conformance/retention/shred-roundtrip.yaml graded as "
        "a document: five checks, each once, each with its passing condition, "
        "the witness designated at first write, and check 1 asserting failure on "
        "the key. It proves the fixture is honest and proves nothing about a "
        "shred, because the store lands at Step 11. It refuses because the "
        "fixture carries no dated row",
    ),
    (
        "retention-finding",
        None,
        PENDING,
        "Step 11. RT-13's pre-close scan reads the case's selector set from a "
        "case store that does not exist, and EG-2 puts that store in ISOLATED. "
        "The mode ships and refuses rather than returning 0",
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
            print(f"  {state.upper():12} {token:29} {note}")
        return 0

    if not args.kernel_gate:
        ap.error("nothing to do: pass --kernel-gate or --list")

    # The gate list must agree with the tree, in both directions.
    for token, cmd, state, _ in KERNEL_GATE:
        if state in (IMPLEMENTED, STUB, UNRATIFIED) and cmd is not None:
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
        if state == UNRATIFIED and cmd is None:
            print(
                f"REFUSED GATE_LIST_INCONSISTENT\n"
                f"  where: {token}\n"
                f"  what:  marked unratified and carries no command, so nothing runs "
                f"and nothing asserts the refusal this entry claims\n"
                f"  moves: give the entry the argv that refuses, or mark it {PENDING} "
                f"with the step that delivers it",
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
    refusing: list[str] = []
    ran = stubbed = pending = 0

    for token, cmd, state, note in KERNEL_GATE:
        if state == PENDING:
            pending += 1
            print(f"  PENDING      {token:29} {note}")
            continue
        code, out = run(cmd)
        if state == STUB:
            stubbed += 1
            print(f"  STUB         {token:29} {note}")
            continue
        if state == UNRATIFIED:
            if code == 0:
                print(
                    f"REFUSED GATE_LIST_UNRATIFIED_PERMITTED\n"
                    f"  where: {token}\n"
                    f"  what:  the list marks this unratified and the check returned 0, "
                    f"so either the operator stamped the artifact and this entry still "
                    f"reports a refusal nobody would see, or the check permitted under an "
                    f"unratified criterion, which is the one thing the pin of record "
                    f"exists to stop\n"
                    f"  moves: move the entry to {IMPLEMENTED} if the artifact now "
                    f"carries a dated row in doctrine/DOCTRINE_STATUS.md; or fix the "
                    f"check, which is permitting where doctrine refuses",
                    file=sys.stderr,
                )
                return 2
            if code != 1:
                failed.append(token)
                print(f"  FAILED       {token:29} {note}")
                for line in out.strip().splitlines():
                    print(f"               | {line}")
                continue
            refusing.append(token)
            print(f"  UNRATIFIED   {token:29} {note}")
            continue
        ran += 1
        if code == 0:
            print(f"  ok           {token:29} {note}")
        else:
            failed.append(token)
            print(f"  FAILED       {token:29} {note}")
            for line in out.strip().splitlines():
                print(f"               | {line}")

    print()
    print(
        f"kernel-gate: {ran} implemented, {len(failed)} failed, "
        f"{len(refusing)} unratified and refusing, {stubbed} stubbed, "
        f"{pending} pending"
    )
    if refusing:
        print(
            "  An unratified check refused, which is the state it is holding rather "
            "than a defect: no run may execute and no case may open until "
            "doctrine/DOCTRINE_STATUS.md carries a dated row for each artifact the "
            "entry names. Run the mode directly to read which rows are missing."
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
