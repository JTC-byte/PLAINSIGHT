#!/usr/bin/env python3
"""Housekeeping gate: voice, structure, citations, and inventory reconciliation.

`CLAUDE.md` section 4 defines Register 1 for every tracked file, and until this
tool existed it was enforced by whoever remembered it. The README shipped in
Wave 0 with thirteen em-dash connectors in the same commit that codified the
rule forbidding them.

Not every rule in section 4 is mechanically checkable. Inversion for emphasis,
metaphor standing in for a checkable statement, and bolding used for rhythm need
a reader. This tool checks what a machine can check and says plainly which rules
it does not reach, rather than implying the file passed a full voice review.

One check here reads a single file for a single defect.
`docs/plainsight_handoff.md` shipped in three commits, `1abb354`, `4c5cd25` and
`f4e00e1`, describing the tree as it stood before each commit, calling
committed artifacts uncommitted and tracked files untracked. `AGENTS.md`
section 8 states the rule; this tool enforces the checkable half of it by
refusing either word in that file. It reaches thirteen of the fourteen lines
that were wrong at `d803213`, and the fourteenth, a sentence with neither word,
is caught at the closeout or not at all. `--self-test` plants each word and
asserts the refusal, so removing the check fails the test, which is design
gate 1.

Exit codes: 0 clean, 1 violations found, 2 the tree could not be read.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import gate_log
except Exception:  # telemetry must never be able to break a gate
    gate_log = None

ROOT = Path(__file__).resolve().parents[1]

#: Governed prose. Everything here is Register 1.
PROSE_GLOBS = ("*.md", "doctrine/*.md", "docs/*.md", "spec/*.md", "conformance/*.md")

#: Files exempt from the voice gate, with the reason. `docs/` carries four
#: documents moved in unchanged from before the repository existed, and
#: restyling them would falsify records of intent.
VOICE_EXEMPT = {
    "docs/DOCUMENT_STANDARD.md": "moved in unchanged; governs briefings, not repo prose",
    "docs/PLAINSIGHT-design.md": "moved in unchanged; rank 7 record of intent",
    "docs/PLAINSIGHT-FOUNDATION.md": "moved in unchanged; rank 7 record of intent",
    "docs/OSINT-COP-tool-review.md": "moved in unchanged; rank 7 record of intent",
    "docs/THE-GAMEPLAN.md": "moved in unchanged; rank 7 record of intent",
}

#: Register 1, the mechanically checkable half.
EM_DASH = "—"
CADENCE_RE = re.compile(r"^\s*(And|But|So)\b")
#: Policy-speak. CLAUDE.md section 4 warns that doctrine/ specifically attracts
#: this register and that a doctrine document written in it gets routed around.
POLICY_SPEAK_RE = re.compile(
    r"\b(shall not|shall be|must be deemed|hereinafter|aforementioned|"
    r"notwithstanding|pursuant to|for the avoidance of doubt)\b",
    re.I,
)

#: Rules this tool does not reach, printed on success so a green run is not
#: mistaken for a full voice review.
UNREACHED = (
    "inversion for emphasis",
    "metaphor standing in for a checkable statement",
    "mid-sentence bolding used for rhythm",
    "sentence fragments",
    "over-correction into passive voice, hedging, or padding",
)

#: Caps from the files' own headers.
HANDOFF_MAX_LINES = 400
WORKLOG_MAX_LIVE_ENTRIES = 10

#: The pre-commit tense. AGENTS.md section 8: the handoff is written in the tense
#: of the tree the commit will create, so neither word belongs in it. Matched
#: case-insensitively as a substring, in the shape of the em dash check above.
HANDOFF_TENSE_WORDS = ("untracked", "uncommitted")
HANDOFF_REL = "docs/plainsight_handoff.md"


PATH_REF_RE = re.compile(
    r"`((?:doctrine|docs|spec|schema|ontology|policy|tools|runner|conformance|"
    r"synthetic|connectors|app|release)/[A-Za-z0-9_./*-]+)`"
)


def registered_artifacts() -> set[str]:
    """Paths the artifact register plans, whether or not they exist yet.

    The register in `docs/THE-GAMEPLAN.md` is rank 7 and is a record of intent,
    which is the right authority for this question: it says what the program
    means to build. A citation to a planned artifact is legitimate. A citation
    to an unplanned one is a typo.
    """
    plan = ROOT / "docs" / "THE-GAMEPLAN.md"
    if not plan.is_file():
        return set()
    out: set[str] = set()
    for cited in PATH_REF_RE.findall(plan.read_text(encoding="utf-8")):
        out.add(cited)
        if "*" in cited:
            out.add(cited.split("*")[0].rstrip("/"))
    return out


class Finding:
    __slots__ = ("code", "where", "detail", "moves")

    def __init__(self, code, where, detail, moves):
        self.code, self.where, self.detail, self.moves = code, where, detail, moves

    def render(self) -> str:
        return (
            f"REFUSED {self.code}\n"
            f"  where: {self.where}\n"
            f"  what:  {self.detail}\n"
            f"  moves: {self.moves}"
        )


def governed_prose() -> list[Path]:
    seen: dict[Path, None] = {}
    for pattern in PROSE_GLOBS:
        for p in ROOT.glob(pattern):
            if p.is_file() and ".git" not in p.parts:
                seen[p] = None
    return sorted(seen)


def handoff_tense_findings(text: str, rel: str = HANDOFF_REL) -> list[Finding]:
    """Refuse the pre-commit tense in the handoff, one finding per line.

    Kept as its own function so ``--self-test`` can plant a word and assert the
    refusal without touching the file on disk.
    """
    out: list[Finding] = []
    for n, line in enumerate(text.splitlines(), 1):
        low = line.lower()
        for word in HANDOFF_TENSE_WORDS:
            if word in low:
                out.append(
                    Finding(
                        "HYGIENE_HANDOFF_PRE_COMMIT_TENSE",
                        f"{rel}:{n}",
                        f"describes something as {word!r}, which is the pre-commit tense. "
                        "The handoff is read next session against a tree in which the "
                        "commit exists, and three commits shipped one that called "
                        "committed artifacts uncommitted. AGENTS.md section 8 is the rule",
                        "state what the artifact is in the tree the commit creates, or "
                        "say where it lives if it lives outside the repository",
                    )
                )
                break
    return out


def check() -> list[Finding]:
    findings: list[Finding] = []
    files = governed_prose()
    if not files:
        raise FileNotFoundError("no governed prose found under the repository root")

    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()

        # Structure applies to every file, exempt or not: a broken table is a
        # broken table regardless of who wrote the prose.
        for n, line in enumerate(lines, 1):
            if line.startswith("|") and not line.rstrip().endswith("|"):
                findings.append(
                    Finding(
                        "HYGIENE_TABLE_ROW_UNTERMINATED",
                        f"{rel}:{n}",
                        "a markdown table row does not end with a pipe, so the "
                        "table renders as prose from here down",
                        "terminate the row, or escape a literal pipe inside a cell as \\|",
                    )
                )

        if rel in VOICE_EXEMPT:
            continue

        for n, line in enumerate(lines, 1):
            if EM_DASH in line:
                findings.append(
                    Finding(
                        "HYGIENE_EM_DASH_CONNECTOR",
                        f"{rel}:{n}",
                        "an em dash is used as a connector",
                        "use a comma, a colon, a semicolon, or a second sentence",
                    )
                )
            if CADENCE_RE.match(line):
                findings.append(
                    Finding(
                        "HYGIENE_CADENCE_OPENER",
                        f"{rel}:{n}",
                        "a sentence opens with And, But, or So to carry cadence",
                        "start from the subject, or join the previous sentence",
                    )
                )
            m = POLICY_SPEAK_RE.search(line)
            if m and rel.startswith("doctrine/"):
                findings.append(
                    Finding(
                        "HYGIENE_POLICY_SPEAK",
                        f"{rel}:{n}",
                        f"doctrine prose uses the policy-speak form {m.group(0)!r}. "
                        "CLAUDE.md section 4: a doctrine document written in that "
                        "register reads as someone else's requirement and gets routed around",
                        "name the mechanism that enforces the rule and the test that "
                        "proves it fired",
                    )
                )

    # Citations, reconciled against the artifact register rather than against
    # the filesystem alone. A governed file legitimately names an artifact that
    # is planned and unbuilt: the authority order in CLAUDE.md and AGENTS.md is
    # a list of ranks, not an inventory of what exists today. What is not
    # legitimate is naming a path that exists in no register and on no disk,
    # which is a typo nobody notices until someone tries to follow it.
    registered = registered_artifacts()
    if not registered:
        findings.append(
            Finding(
                "HYGIENE_REGISTER_UNREADABLE",
                "docs/THE-GAMEPLAN.md",
                "the artifact register parsed to zero paths, so every citation would "
                "be judged against an empty inventory and this check would pass "
                "vacuously. An empty inventory proves nothing",
                "check the register tables, or update registered_artifacts()",
            )
        )
    else:
        for path in files:
            rel = path.relative_to(ROOT).as_posix()
            # The moved-in rank-7 documents predate this repository and cite
            # paths inside its siblings: zisr-recon's docs/ENTRY_CRITERIA.md,
            # the COP's tools/bridge/README.md. Those are real files in a
            # different tree, and judging them against this tree's register
            # produces noise rather than findings. They are exempt for the same
            # reason they are voice-exempt: they are records of intent, and
            # editing them falsifies what was true when they were written.
            if rel in VOICE_EXEMPT:
                continue
            text = path.read_text(encoding="utf-8")
            for n, line in enumerate(text.splitlines(), 1):
                for cited in PATH_REF_RE.findall(line):
                    if cited.endswith("/") or "*" in cited:
                        continue
                    if (ROOT / cited).exists() or cited in registered:
                        continue
                    findings.append(
                        Finding(
                            "HYGIENE_CITATION_UNREGISTERED",
                            f"{rel}:{n}",
                            f"cites {cited}, which does not exist and is in no artifact "
                            "register, so it is a path nobody can follow and nobody "
                            "has planned",
                            "correct the path, add the artifact to the register in "
                            "docs/THE-GAMEPLAN.md section 2.1 or 2.2, or create it",
                        )
                    )

    # Caps the files set for themselves.
    handoff = ROOT / "docs" / "plainsight_handoff.md"
    if handoff.is_file():
        handoff_text = handoff.read_text(encoding="utf-8")
        findings.extend(handoff_tense_findings(handoff_text))
        n = len(handoff_text.splitlines())
        if n > HANDOFF_MAX_LINES:
            findings.append(
                Finding(
                    "HYGIENE_HANDOFF_OVER_CAP",
                    f"docs/plainsight_handoff.md ({n} lines)",
                    f"over its own {HANDOFF_MAX_LINES} line cap. ZMeta's handoff reached "
                    "2,080 lines carrying eleven superseded state sections, which is the "
                    "failure mode the cap exists to prevent",
                    "move superseded sections to the archive, or raise the cap in the "
                    "file's header and here together",
                )
            )

    worklog = ROOT / "docs" / "plainsight_worklog.md"
    if worklog.is_file():
        entries = re.findall(r"^## \d{4}-\d{2}-\d{2}", worklog.read_text(encoding="utf-8"), re.M)
        if len(entries) > WORKLOG_MAX_LIVE_ENTRIES:
            findings.append(
                Finding(
                    "HYGIENE_WORKLOG_OVER_CAP",
                    f"docs/plainsight_worklog.md ({len(entries)} live entries)",
                    f"over its own {WORKLOG_MAX_LIVE_ENTRIES} entry cap",
                    "move the oldest entries to plainsight_worklog_archive.md without "
                    "editing them; a process record is never restyled",
                )
            )

    # Inventory reconcile, both directions. One direction finds half the drift.
    makefile = ROOT / "Makefile"
    if makefile.is_file():
        mk = makefile.read_text(encoding="utf-8")
        called = set(re.findall(r"python tools/(\w+\.py)", mk))
        present = {p.name for p in (ROOT / "tools").glob("*.py")}
        for name in sorted(present - called):
            findings.append(
                Finding(
                    "HYGIENE_TOOL_NOT_IN_ANY_GATE",
                    f"tools/{name}",
                    "exists but no Makefile target runs it, so nothing makes it run",
                    "add it to a gate in the Makefile, or delete it",
                )
            )
        for name in sorted(called - present):
            findings.append(
                Finding(
                    "HYGIENE_GATE_CALLS_MISSING_TOOL",
                    f"tools/{name}",
                    "named by a Makefile target but does not exist, so the gate "
                    "fails for the wrong reason",
                    "write the tool, or remove it from the target",
                )
            )

    return findings


def self_test() -> int:
    """Break the tense constraint in memory and assert each break is refused.

    Design gate 1: a constraint is not done until a test fails when it is
    removed. Deleting the body of ``handoff_tense_findings`` fails the planted
    cases; widening it to refuse everything fails the clean case. The clean
    sample deliberately contains the opening clause of the one wrong line at
    ``d803213`` that carried neither word, so the test also records the reach
    limit.
    """
    planted = (
        "| `spec/layer-model.yaml` | **Written, untracked.** 2,280 lines. |",
        "**Wave:** 0 committed, and the first build artifacts exist uncommitted.",
        "Uncommitted edits to the Makefile wire the three new gates.",
        "| `AGENTS.md` | Committed, plus an UNTRACKED section 5 edit. |",
    )
    clean = (
        "| `spec/layer-model.yaml` | **Committed in `f4e00e1`, and reviewed.** |\n"
        "The tree is clean at the commit that carries this file.\n"
        "Neither has been committed.\n"
    )
    failures = 0
    for line in planted:
        got = handoff_tense_findings(line + "\n", rel="<planted>")
        if len(got) == 1 and got[0].code == "HYGIENE_HANDOFF_PRE_COMMIT_TENSE":
            print(f"  refused  {line[:60]}")
        else:
            failures += 1
            print(f"  PASSED   {line[:60]}  (expected one refusal, got {len(got)})")
    got = handoff_tense_findings(clean, rel="<clean>")
    if got:
        failures += 1
        print(f"  REFUSED  a clean sample, {len(got)} finding(s); the check is wider than its rule")
    else:
        print("  ok       clean sample passes, including the sentence this check does not reach")
    if failures:
        print(
            f"validate_hygiene --self-test: {failures} case(s) were not refused as claimed. A gate "
            "nobody has watched fail is an assumption (HYGIENE.md section 2)",
            file=sys.stderr,
        )
        return 1
    print(
        f"validate_hygiene --self-test ok: {len(planted)} deliberate breaks, {len(planted)} refused, "
        "and one clean sample passed"
    )
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Housekeeping gate.")
    ap.add_argument("--quiet", action="store_true", help="Print only on failure.")
    ap.add_argument(
        "--self-test",
        action="store_true",
        help="Plant each pre-commit-tense word in a handoff line and assert the refusal.",
    )
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()

    try:
        findings = check()
    except FileNotFoundError as exc:
        print(f"REFUSED HYGIENE_TREE_UNREADABLE\n  what: {exc}", file=sys.stderr)
        return 2

    if gate_log:
        # One run record, then one detail record per finding. See the note in
        # tools/validate_doctrine.py and doctrine/HYGIENE.md HY-1.
        gate_log.record_run("hygiene", "refuse" if findings else "pass", count=len(findings))
        for f in findings:
            gate_log.record_finding("hygiene", code=f.code, where=f.where)

    if findings:
        for f in findings:
            print(f.render(), file=sys.stderr)
            print(file=sys.stderr)
        print(
            f"validate_hygiene: {len(findings)} violation(s). Voice rules: CLAUDE.md "
            "section 4. The handoff tense rule: AGENTS.md section 8.",
            file=sys.stderr,
        )
        return 1

    if not args.quiet:
        n = len(governed_prose())
        print(f"validate_hygiene ok: {n} governed files, {len(VOICE_EXEMPT)} voice-exempt")
        print("  not checked by any machine, and still rules: " + "; ".join(UNREACHED))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
