#!/usr/bin/env python3
"""The pin of record, read once for every mechanism.

`doctrine/DOCTRINE_STATUS.md` is the only source a mechanism reads for whether an
artifact or a criterion binds. Until 2026-10-01 three tools read it three ways.
`tools/validate_authorization.py` parsed the Ratified table's cells,
`tools/validate_retention.py` accepted any dated line naming a path anywhere
under the Ratified heading, and `tools/validate_doctrine.py` read every table
row that opens with a criterion id. They disagreed on the unmodified pin about
`spec/pse-semantics-contract.md`. The Step 8 adversarial review of 2026-10-01
also found that one dated row naming a path stamped the whole file, so the first
entry the operator stamped in a policy would have stamped the policy, against the
pin's own sentence that one partially stamped item does not stamp its file.

This module is the one reader the three tools import. On every axis it takes the
stricter of the readings they took before, so it can turn a permit into a
refusal and never the reverse. Each reading is an assistant reading awaiting the
operator's confirmation, and `READINGS` states it.

Usage: python tools/pin_of_record.py --self-test [--quiet]
Exit codes: 0 every planted case read as claimed, 1 one did not, 2 the pin could
not be read.
"""
from __future__ import annotations

import argparse
import datetime
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIN = ROOT / "doctrine" / "DOCTRINE_STATUS.md"

RATIFIED_START = "## Ratified"
RATIFIED_END = "### What each decision was"
PENDING_START = "## Pending ratification"
PENDING_END = "### Step 3 criteria"
CRITERIA_START = "### Step 3 criteria"
CRITERIA_END = "## Assistant readings"

#: Who may ratify. The program has one ratifier, and every stamped row names it.
RATIFIERS = ("operator",)

#: The two Item-cell forms that stamp a whole artifact, as a closed grammar. A
#: substring test accepted "not the whole artifact" and a struck row until the
#: completeness critic of 2026-10-01 found it, which brought back the blocker
#: this module exists to close. Anything else is an item stamp.
WHOLE_RE = re.compile(r"^([^,~]+), whole artifact$")
RANGE_RE = re.compile(r"^(SS|RT|EG|CR|HY)-1 to \1-(\d+), all criteria$")
#: A row carrying any of these marks is withdrawn and stamps nothing at all. A
#: row is withdrawn by a later dated row, never by editing or striking it.
WITHDRAWN_RE = re.compile(r"~~|\b(withdrawn|struck|superseded|revoked)\b", re.I)

#: Criterion namespaces and the file whose whole-artifact stamp they need.
NAMESPACE_FILE = {
    "SS": "doctrine/SUBJECT_SELECTION.md",
    "RT": "doctrine/RETENTION.md",
    "EG": "doctrine/EGRESS.md",
    "CR": "doctrine/CREDENTIAL_LIFECYCLE.md",
    "HY": "doctrine/HYGIENE.md",
}

PATH_RE = re.compile(r"`([A-Za-z0-9_./-]+\.(?:md|ya?ml|json|py|jsonl))`")
CRITERION_RE = re.compile(r"((?:SS|RT|EG|CR|HY)-\d+)\b")
CONCLUSION_RE = re.compile(
    r"^((?:19|20)\d{2}-\d{2}-\d{2})(?:, amended ((?:19|20)\d{2}-\d{2}-\d{2}))?$"
)
SECTION_RE = re.compile(r"§\s*(\d+)")

#: How a whole-artifact stamp row is written, quoted in refusal moves.
ROW_FORMAT = (
    "a row in the Ratified table of doctrine/DOCTRINE_STATUS.md whose Item cell ends "
    "in ', whole artifact', whose File cell is the backticked path alone, whose "
    "Conclusion stamped cell is the date alone, and whose Ratifier cell is 'operator'"
)

READINGS = {
    "PIN-R1": "Only the Ratified table stamps: the rows between '## Ratified' and "
    "'### What each decision was'. A dated line in the prose under it, in the Pending "
    "table, or in either readings table is not a stamp.",
    "PIN-R2": "A stamp row has the table's six cells, a Conclusion stamped cell that is "
    "a calendar date in 19xx or 20xx and nothing else, optionally followed by ', "
    "amended <date>', and a Ratifier cell naming a declared ratifier. A date inside "
    "other words, such as a review date, is not a stamp, and neither is an impossible "
    "date.",
    "PIN-R3": "A row stamps a whole artifact only when its File cell names backticked "
    "paths and nothing else and its Item cell is exactly '<what>, whole artifact', "
    "with no 'not' in <what>, or a doctrine range '<NS>-1 to <NS>-<n>, all criteria'. "
    "A row carrying a strike or the word withdrawn, struck, superseded or revoked "
    "stamps nothing; a row is withdrawn by a later dated row. Every other dated row is "
    "an item stamp, recorded against each path it names with the qualifier that "
    "follows the path, and it does not stamp the file.",
    "PIN-R4": "An artifact stamped by sections, the contract's sections 5 and 12 under "
    "SS-14 item 6, is stamped when its item stamps name every required section, or when "
    "a whole-artifact row stamps it.",
    "PIN-R5": "A path the Pending table names as a stamp target is unstamped whatever "
    "the Ratified table says. This is VA-R2, kept.",
    "PIN-R6": "A stamp for a path with no file behind it stamps nothing while the path "
    "is absent. The stamp is not bound to content, so a file written there later reads "
    "as stamped by the same row, as an edit to a stamped file does. Binding a stamp to "
    "content is a pin-format change and is the operator's.",
    "PIN-R7": "A criterion has a row only in the per-criterion table, between "
    "'### Step 3 criteria' and '## Assistant readings', and binds only when its "
    "namespace file carries a whole-artifact stamp and a dated row covers it: a range "
    "row whose range includes it, or an item row that names it after the file's path. "
    "A Ratified row that opens with a criterion id, such as 'SS-1 to SS-21, all "
    "criteria', is not that criterion's row, and a criterion added later is not "
    "covered by an older range.",
    "PIN-R8": "A Ratified row whose Item cell begins with 'Item' is read as the table "
    "header, as validate_authorization.py read it before this module. Reading such a "
    "row as a stamp would accept rows this reader now refuses, which is class F, so "
    "the heuristic stays until the operator decides it.",
}


def _slice(text: str, start: str, end: str) -> str:
    i = text.find(start)
    if i < 0:
        return ""
    j = text.find(end, i + len(start))
    return text[i:] if j < 0 else text[i:j]


def _table_rows(block: str) -> list[list[str]]:
    """Every pipe row in a markdown block, as stripped cells."""
    rows = []
    for line in block.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if cells and all(set(c) <= set("-: ") for c in cells):
            continue
        rows.append(cells)
    return rows


def _conclusion_date(cell: str) -> str:
    """The stamp date if the cell is a well-formed conclusion stamp, else ''."""
    m = CONCLUSION_RE.match(cell.strip())
    if not m:
        return ""
    for d in m.groups():
        if d is None:
            continue
        try:
            datetime.date.fromisoformat(d)
        except ValueError:
            return ""
    return m.group(1)


def required_sections(granularity: str) -> set[str]:
    """{'§5', '§12'} from a granularity such as 'sections 5 and 12', else empty."""
    if not granularity.strip().lower().startswith("section"):
        return set()
    return {f"§{n}" for n in re.findall(r"\d+", granularity)}


class Pin:
    """The parsed stamp state. Nothing here decides; it reads."""

    def __init__(self, text: str, root: Path = ROOT, sections: dict[str, set[str]] | None = None):
        self.root = root
        self.sections = {k: set(v) for k, v in (sections or {}).items()}
        self.whole: dict[str, str] = {}
        self.qualified: dict[str, set[str]] = {}
        self.ranges: dict[str, list[tuple[str, int]]] = {}
        self.named: dict[str, set[str]] = {}
        self.stamp_targets: set[str] = set()
        self.criteria: dict[str, str] = {}
        self.parsed = False

        ratified = _slice(text, RATIFIED_START, RATIFIED_END)
        pending = _slice(text, PENDING_START, PENDING_END)
        step3 = _slice(text, CRITERIA_START, CRITERIA_END)
        if not (ratified and pending and step3):
            return

        for cells in _table_rows(ratified):
            if len(cells) != 6 or cells[0].lower().startswith("item"):
                continue
            item, file_cell, _, conclusion, _, ratifier = cells
            if any(WITHDRAWN_RE.search(c) for c in cells):
                continue
            date = _conclusion_date(conclusion)
            if not date or ratifier.strip().lower() not in RATIFIERS:
                continue
            paths = PATH_RE.findall(file_cell)
            if not paths:
                continue
            rest = PATH_RE.sub("", file_cell)
            pure = not re.sub(r"[\s,]|\band\b", "", rest)
            label = item.strip()
            whole = WHOLE_RE.match(label)
            span = RANGE_RE.match(label)
            if pure and ((whole and not re.search(r"\bnot\b", whole.group(1), re.I)) or span):
                for p in paths:
                    self.whole.setdefault(p, date)
                    if span and NAMESPACE_FILE.get(span.group(1)) == p:
                        self.ranges.setdefault(p, []).append((span.group(1), int(span.group(2))))
                continue
            # An item stamp. Each path takes the qualifier written after it.
            pieces = PATH_RE.split(file_cell)
            for k in range(1, len(pieces), 2):
                after = pieces[k + 1] if k + 1 < len(pieces) else ""
                self.qualified.setdefault(pieces[k], set()).update(
                    f"§{n}" for n in SECTION_RE.findall(after)
                )
                self.named.setdefault(pieces[k], set()).update(CRITERION_RE.findall(after))

        for cells in _table_rows(pending):
            if len(cells) != 4 or "stamp target" not in cells[1].lower():
                continue
            for p in PATH_RE.findall(cells[0]):
                self.stamp_targets.add(p)

        for cells in _table_rows(step3):
            if not cells:
                continue
            m = CRITERION_RE.match(cells[0])
            if m:
                self.criteria.setdefault(m.group(1), " | ".join(cells))

        self.parsed = bool(self.criteria) and bool(self.whole)

    def artifact_stamped(self, path: str) -> bool:
        return not self.reason_unstamped(path)

    def reason_unstamped(self, path: str) -> str:
        """Why the path is unstamped, rendered as its consequence, or '' if stamped."""
        if not self.parsed:
            return "the pin of record could not be parsed into its three tables"
        if path in self.stamp_targets:
            return "the Pending table names it as a stamp target"
        if not (self.root / path).is_file():
            return "no file exists at that path, so a stamp would ratify contents nobody has seen"
        if path in self.whole:
            return ""
        need = self.sections.get(path)
        if need and need <= self.qualified.get(path, set()):
            return ""
        if need:
            have = sorted(self.qualified.get(path, set()))
            return (
                f"it is stamped by sections and the Ratified table stamps {have or 'none'} "
                f"of {sorted(need)}"
            )
        if path in self.qualified:
            return (
                "the Ratified table stamps items in it and never the whole artifact, and "
                "one partially stamped item does not stamp its file"
            )
        return "the Ratified table carries no whole-artifact row for it"

    def criterion_stamped(self, cid: str) -> bool:
        if cid not in self.criteria:
            return False
        ns, n = cid.split("-")[0], int(cid.split("-")[1])
        path = NAMESPACE_FILE.get(ns, "")
        if not self.artifact_stamped(path):
            return False
        in_range = any(r_ns == ns and 1 <= n <= top for r_ns, top in self.ranges.get(path, []))
        return in_range or cid in self.named.get(path, set())


def read(root: Path = ROOT, sections: dict[str, set[str]] | None = None) -> Pin:
    return Pin((root / "doctrine" / "DOCTRINE_STATUS.md").read_text(encoding="utf-8"), root, sections)


# ---------------------------------------------------------------------------
# --self-test. Each case edits the real pin in memory and asserts how one path
# or criterion reads. The cases that must permit are as load-bearing as the
# ones that must refuse: a reader that refuses everything proves nothing.
# ---------------------------------------------------------------------------

POLICY = "policy/subject-authorization.yaml"
CONTRACT = "spec/pse-semantics-contract.md"
CONTRACT_SECTIONS = {CONTRACT: {"§5", "§12"}}


def _row(item: str, file_cell: str, conclusion: str = "2026-10-01", ratifier: str = "operator") -> str:
    return f"| {item} | {file_cell} | v0.1 | {conclusion} | unstamped | {ratifier} |"


def _add(text: str, row: str) -> str:
    """Append a row to the end of the Ratified table."""
    i = text.find(RATIFIED_END)
    head = text[:i].rstrip("\n")
    return head + "\n" + row + "\n\n" + text[i:]


def _drop_pending_targets(text: str) -> str:
    return "\n".join(
        ln for ln in text.splitlines()
        if not ("stamp target" in ln.lower() and CONTRACT in ln and ln.startswith("|"))
    ) + "\n"


def _cases():
    whole = _row("the compiled policy, whole artifact", f"`{POLICY}`")
    return [
        ("the real pin stamps every doctrine file", lambda t: t,
         lambda p: all(p.artifact_stamped(f) for f in NAMESPACE_FILE.values())),
        ("the real pin stamps no Step 8 policy", lambda t: t,
         lambda p: not p.artifact_stamped(POLICY) and not p.artifact_stamped("policy/retention.yaml")),
        ("the real pin leaves the contract unstamped", lambda t: t,
         lambda p: not p.artifact_stamped(CONTRACT)),
        ("the real pin reads every criterion as stamped", lambda t: t,
         lambda p: len(p.criteria) >= 58 and all(p.criterion_stamped(c) for c in p.criteria)),
        ("a whole-artifact row stamps the policy", lambda t: _add(t, whole),
         lambda p: p.artifact_stamped(POLICY)),
        ("an entry row in house format does not stamp the policy",
         lambda t: _add(t, _row("SA-U4 expires_on against retain_until", f"`{POLICY}`")),
         lambda p: not p.artifact_stamped(POLICY)),
        ("a qualified File cell does not stamp the policy",
         lambda t: _add(t, _row("the compiled policy, whole artifact", f"`{POLICY}` SA-U4")),
         lambda p: not p.artifact_stamped(POLICY)),
        ("a review date inside words is not a stamp",
         lambda t: _add(t, _row("the compiled policy, whole artifact", f"`{POLICY}`", "not stamped, reviewed 2026-10-15")),
         lambda p: not p.artifact_stamped(POLICY)),
        ("an impossible date is not a stamp",
         lambda t: _add(t, _row("the compiled policy, whole artifact", f"`{POLICY}`", "2026-13-45")),
         lambda p: not p.artifact_stamped(POLICY)),
        ("an undeclared ratifier is not a stamp",
         lambda t: _add(t, _row("the compiled policy, whole artifact", f"`{POLICY}`", ratifier="pending")),
         lambda p: not p.artifact_stamped(POLICY)),
        ("a stamp row in the prose under the table is not a stamp",
         lambda t: t.replace(RATIFIED_END, RATIFIED_END + "\n\n" + whole + "\n", 1),
         lambda p: not p.artifact_stamped(POLICY)),
        ("a stamp for an absent file stamps nothing while it is absent",
         lambda t: _add(t, _row("the dispatch allowlist, whole artifact", "`runner/dispatch_allowlist.yaml`")),
         lambda p: not p.artifact_stamped("runner/dispatch_allowlist.yaml")),
        ("a Pending stamp-target row holds a whole-artifact stamp",
         lambda t: _add(t, _row("the contract, whole artifact", f"`{CONTRACT}`")),
         lambda p: not p.artifact_stamped(CONTRACT)),
        ("the version-label row does not stamp the contract once the holds go",
         _drop_pending_targets,
         lambda p: not p.artifact_stamped(CONTRACT)),
        ("section 5 alone does not stamp the contract",
         lambda t: _add(_drop_pending_targets(t), _row("contract section 5", f"`{CONTRACT}` §5")),
         lambda p: not p.artifact_stamped(CONTRACT)),
        ("sections 5 and 12 stamp the contract",
         lambda t: _add(_add(_drop_pending_targets(t), _row("contract section 5", f"`{CONTRACT}` §5")),
                        _row("contract section 12", f"`{CONTRACT}` §12")),
         lambda p: p.artifact_stamped(CONTRACT)),
        ("the Ratified range row does not stand in for SS-1's row",
         lambda t: re.sub(r"(?m)^\| SS-1 closed class set[^\n]*\n", "", t, count=1),
         lambda p: "SS-1" not in p.criteria and not p.criterion_stamped("SS-1")),
        ("a criterion row moved into the rejected table does not count",
         lambda t: (lambda row: (t.replace(row + "\n", "", 1) + row + "\n"))(
             next(ln for ln in t.splitlines() if re.match(r"^\| RT-9\b", ln))),
         lambda p: not p.criterion_stamped("RT-9")),
        ("item rows do not stamp a doctrine file without its range row",
         lambda t: re.sub(r"(?m)^\| RT-1 to RT-18, all criteria[^\n]*\n", "", t, count=1),
         lambda p: not p.artifact_stamped("doctrine/RETENTION.md") and not p.criterion_stamped("RT-1")),
        ("a row labelled Item is read as the header (PIN-R8)",
         lambda t: _add(t, _row("Item 3 of SS-14 item 6, whole artifact", f"`{POLICY}`")),
         lambda p: not p.artifact_stamped(POLICY)),
        ("an entry row saying it is not the whole artifact does not stamp",
         lambda t: _add(t, _row("SA-U4 only, not the whole artifact", f"`{POLICY}`")),
         lambda p: not p.artifact_stamped(POLICY)),
        ("a negation before the comma does not stamp",
         lambda t: _add(t, _row("not the compiled policy, whole artifact", f"`{POLICY}`")),
         lambda p: not p.artifact_stamped(POLICY)),
        ("a row saying not all criteria does not stamp",
         lambda t: _add(t, _row("SA-U4 resolved, other criteria open (not all criteria)", f"`{POLICY}`")),
         lambda p: not p.artifact_stamped(POLICY)),
        ("a struck whole-artifact row stamps nothing",
         lambda t: _add(t, _row("~~the compiled policy, whole artifact~~", f"`{POLICY}`")),
         lambda p: not p.artifact_stamped(POLICY) and POLICY not in p.qualified),
        ("a withdrawn whole-artifact row stamps nothing",
         lambda t: _add(t, _row("the compiled policy, whole artifact (WITHDRAWN 2026-10-02)", f"`{POLICY}`")),
         lambda p: not p.artifact_stamped(POLICY)),
        ("whole artifact mid-cell does not stamp",
         lambda t: _add(t, _row("whole artifact review of the compiled policy", f"`{POLICY}`")),
         lambda p: not p.artifact_stamped(POLICY)),
        ("a year-2199 conclusion is not a stamp",
         lambda t: _add(t, _row("the compiled policy, whole artifact", f"`{POLICY}`", "2199-01-01")),
         lambda p: not p.artifact_stamped(POLICY)),
        ("a year-0001 conclusion is not a stamp",
         lambda t: _add(t, _row("the compiled policy, whole artifact", f"`{POLICY}`", "0001-01-01")),
         lambda p: not p.artifact_stamped(POLICY)),
        ("RT-19 binds only through the row that names it",
         lambda t: re.sub(r"(?m)^\| Gate telemetry with a 90 day TTL[^\n]*\n", "", t, count=1),
         lambda p: not p.criterion_stamped("RT-19") and p.criterion_stamped("RT-18")),
        ("a criterion added later is not covered by an older range",
         lambda t: re.sub(r"(?m)^(\| RT-19 [^\n]*\n)", r"\1| RT-20 a planted criterion | same | x | x |\n", t, count=1),
         lambda p: "RT-20" in p.criteria and not p.criterion_stamped("RT-20")),
        ("a pin without its Ratified heading stamps nothing",
         lambda t: t.replace(RATIFIED_START + "\n", "## Ratifed\n", 1),
         lambda p: not p.parsed and not p.artifact_stamped("doctrine/SUBJECT_SELECTION.md")),
    ]


def _written_later(text: str) -> bool:
    """PIN-R6's limit, kept visible: a file written after its stamp reads stamped."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "runner" / "dispatch_allowlist.yaml"
        target.parent.mkdir(parents=True)
        target.write_text("written after the stamp\n", encoding="utf-8")
        row = _row("the dispatch allowlist, whole artifact", "`runner/dispatch_allowlist.yaml`")
        return Pin(_add(text, row), Path(tmp)).whole.get("runner/dispatch_allowlist.yaml") is not None


def self_test(text: str, quiet: bool = False) -> int:
    failures = 0
    # PIN-R6 states this limit rather than claiming the reader closes it: a stamp
    # is not bound to content until the operator decides the pin's format.
    if not _written_later(text):
        failures += 1
        print("  BROKEN   PIN-R6's stated limit no longer holds; restate PIN-R6")
    elif not quiet:
        print("  held     a file written after its stamp reads stamped (PIN-R6's stated limit)")
    for desc, mutate, holds in _cases():
        try:
            ok = bool(holds(Pin(mutate(text), ROOT, CONTRACT_SECTIONS)))
        except Exception as exc:  # a crash is a failure of the case, not a pass
            ok = False
            desc = f"{desc} (crashed: {exc.__class__.__name__})"
        failures += 0 if ok else 1
        if not quiet or not ok:
            print(f"  {'held   ' if ok else 'BROKEN '}  {desc}")
    if failures:
        print(
            f"pin_of_record --self-test: {failures} case(s) did not read as claimed. "
            "The reader every gate uses to decide whether an artifact or a criterion "
            "binds no longer reads the pin the way READINGS states.\n"
            "  moves: fix Pin in tools/pin_of_record.py; or, if a reading changed on "
            "purpose, change READINGS and the case together and record the operator's "
            "decision; a reading that accepts a row it refused before is class F",
            file=sys.stderr,
        )
        return 1
    if not quiet:
        print(f"pin_of_record --self-test ok: {len(_cases())} cases read as claimed")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="The pin-of-record reader the gates share.")
    ap.add_argument("--self-test", action="store_true", help="Read planted pins and assert each reads as claimed.")
    ap.add_argument("--quiet", action="store_true", help="Print only on failure.")
    args = ap.parse_args(argv)
    try:
        text = PIN.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(
            "REFUSED PIN_UNREADABLE\n"
            "  where: doctrine/DOCTRINE_STATUS.md\n"
            f"  what:  the pin of record could not be read ({exc.__class__.__name__}), so no "
            "gate can tell a stamped artifact from an unstamped one\n"
            "  moves: restore the file from git",
            file=sys.stderr,
        )
        return 2
    if args.self_test:
        return self_test(text, quiet=args.quiet)
    print(__doc__.strip().splitlines()[0])
    print("usage: python tools/pin_of_record.py --self-test [--quiet]")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
