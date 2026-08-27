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

Exit codes: 0 clean, 1 violations found, 2 the tree could not be read.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

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
        n = len(handoff.read_text(encoding="utf-8").splitlines())
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


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Housekeeping gate.")
    ap.add_argument("--quiet", action="store_true", help="Print only on failure.")
    args = ap.parse_args(argv)

    try:
        findings = check()
    except FileNotFoundError as exc:
        print(f"REFUSED HYGIENE_TREE_UNREADABLE\n  what: {exc}", file=sys.stderr)
        return 2

    if findings:
        for f in findings:
            print(f.render(), file=sys.stderr)
            print(file=sys.stderr)
        print(
            f"validate_hygiene: {len(findings)} violation(s). rule: CLAUDE.md section 4.",
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
