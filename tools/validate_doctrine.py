#!/usr/bin/env python3
"""Doctrine integrity gate.

The doctrine corpus is this repository's governed artifact at Wave 0, the way a
schema corpus is ZMeta's. It carries per-criterion stamps, a pin of record, and
cross-references between two rank-1 files, and until this tool existed every one
of those was checked by hand.

Every check here was written because the corresponding defect actually occurred
during Step 3 drafting and was caught by an adversarial review rather than by a
mechanism:

  D-01  SS-11 cited RT-4 as the criterion enforcing the incidental TTL. RT-4 is
        per-case blob encryption. RT-6 is the enforcer, and RT-6 named SS-11
        back correctly, so the pair was broken in exactly one direction. Four
        independent reviewers found it and no tool did.
  D-02  A criterion can be written with no stamp marker beneath it, which makes
        it unstampable while reading as governed. Enforced by
        DOCTRINE_CRITERION_UNMARKED, and DOCTRINE_CRITERION_DUPLICATE guards the
        adjacent case where two definitions share an id and one stamp is read as
        covering both.
  D-03  Both doctrine files declared their own tables to be an index into
        DOCTRINE_STATUS.md at a point when DOCTRINE_STATUS.md carried no rows
        for them at all, so no criterion was stampable and nothing said so.
        Enforced in both directions by DOCTRINE_NO_STATUS_ROW and
        DOCTRINE_ORPHAN_STATUS_ROW, because one direction finds half the drift.
  D-04  A reference to a criterion that is defined nowhere reads as a governed
        cross-reference and resolves to nothing. Enforced by
        DOCTRINE_REF_DANGLING. DOCTRINE_FILE_EMPTY is the degenerate case: a
        namespace file that defines no criteria at all proves nothing, on the
        same reasoning ZMeta's fixture runner refuses an empty must-pass corpus.
  D-06  A criterion's own marker and its row in the pin of record can disagree.
        The pin wins by rule, which means a disagreement is silent by default.
  D-07  Prose counts drift from the tables they count. "Five checks", "six
        items", "nine fields" were each correct when written.

D-02 and D-04 were added to this narrative on 2026-09-03, when the doctrine
review found that HYGIENE.md HY-3 claims every check here carries its defect in
the docstring and four of the nine codes did.

Exit codes: 0 clean, 1 violations found, 2 the corpus could not be read.
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
DOCTRINE = ROOT / "doctrine"
STATUS = DOCTRINE / "DOCTRINE_STATUS.md"

#: Criterion namespaces: prefix -> the file that defines them.
NAMESPACES = {
    "SS": DOCTRINE / "SUBJECT_SELECTION.md",
    "RT": DOCTRINE / "RETENTION.md",
    "EG": DOCTRINE / "EGRESS.md",
    "CR": DOCTRINE / "CREDENTIAL_LIFECYCLE.md",
    "HY": DOCTRINE / "HYGIENE.md",
}

#: A criterion definition: bolded id, a period, then its statement.
DEF_RE = re.compile(r"^\*\*((?:SS|RT|EG|CR|HY)-\d+)\.", re.M)
#: Any reference to a criterion anywhere in the corpus.
REF_RE = re.compile(r"\b((?:SS|RT|EG|CR|HY)-\d+)\b")
#: The per-criterion stamp marker that must follow every definition. DOTALL
#: because a marker recording a partial stamp wraps across lines, which is
#: exactly the shape SS-14 needs and the first version of this regex refused.
MARKER_RE = re.compile(r"^\*\[(.+?)\]\*", re.M | re.S)
#: A row in any DOCTRINE_STATUS table, keyed on the criterion it names.
STATUS_ROW_RE = re.compile(r"^\|\s*((?:SS|RT|EG|CR|HY)-\d+)\b", re.M)
#: Directed enforcement pointers. The target must name the source back.
ENFORCED_BY_RE = re.compile(r"Enforced in `([\w.]+)` ((?:SS|RT|EG|CR|HY)-\d+)")
ENFORCES_RE = re.compile(r"Enforces `([\w.]+)` ((?:SS|RT|EG|CR|HY)-\d+)")

#: Prose counts that must match a countable thing. Each entry is
#: (regex over the prose, a callable returning the true count, a label).
#: Kept small on purpose: a count check nobody can read is worse than none.
COUNT_CLAIMS = [
    (
        re.compile(r"comprises (five) checks", re.I),
        lambda texts: len(re.findall(r"^\| \d \| ", texts["RT"], re.M)),
        "RT-9 verification checks",
        5,
    ),
    (
        re.compile(r"NEVER list, (six) items", re.I),
        lambda texts: len(
            re.findall(r"^\d\. \*\*", _slice(texts["SS"], "**SS-14.", "## 8."), re.M)
        ),
        "SS-14 NEVER items",
        6,
    ),
]


class Finding:
    __slots__ = ("code", "where", "detail", "moves")

    def __init__(self, code: str, where: str, detail: str, moves: str):
        self.code = code
        self.where = where
        self.detail = detail
        self.moves = moves

    def render(self) -> str:
        return (
            f"REFUSED {self.code}\n"
            f"  where: {self.where}\n"
            f"  what:  {self.detail}\n"
            f"  moves: {self.moves}"
        )


def _slice(text: str, start: str, end: str) -> str:
    i = text.find(start)
    j = text.find(end, i + 1) if i >= 0 else -1
    if i < 0:
        return ""
    return text[i:j] if j > i else text[i:]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _blocks(text: str) -> dict[str, str]:
    """Split a doctrine file into {criterion_id: its text up to the next one}."""
    hits = list(DEF_RE.finditer(text))
    out: dict[str, str] = {}
    for n, m in enumerate(hits):
        end = hits[n + 1].start() if n + 1 < len(hits) else len(text)
        out[m.group(1)] = text[m.start() : end]
    return out


def check(strict: bool = False) -> list[Finding]:
    findings: list[Finding] = []

    missing = [p for p in list(NAMESPACES.values()) + [STATUS] if not p.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(str(p.relative_to(ROOT)) for p in missing))

    texts = {k: _read(v) for k, v in NAMESPACES.items()}
    status = _read(STATUS)

    defined: dict[str, str] = {}
    blocks: dict[str, str] = {}
    for prefix, path in NAMESPACES.items():
        text = texts[prefix]
        ids = DEF_RE.findall(text)

        # An empty corpus proves nothing. ZMeta's fixture runner refuses an
        # empty must-pass file for the same reason.
        if not ids:
            findings.append(
                Finding(
                    "DOCTRINE_FILE_EMPTY",
                    str(path.relative_to(ROOT)),
                    "the file defines no criteria at all",
                    "define at least one criterion, or remove the file from NAMESPACES",
                )
            )
            continue

        seen: set[str] = set()
        for cid in ids:
            if cid in seen:
                findings.append(
                    Finding(
                        "DOCTRINE_CRITERION_DUPLICATE",
                        f"{path.relative_to(ROOT)} :: {cid}",
                        "defined more than once in the same file",
                        "renumber the second definition, or merge the two",
                    )
                )
            seen.add(cid)
            defined[cid] = prefix
        blocks.update(_blocks(text))

    # D-02. Every criterion carries a stamp marker directly beneath it.
    for cid, block in blocks.items():
        head = block[: block.find("\n\n")] if "\n\n" in block else block
        if not MARKER_RE.search(head):
            findings.append(
                Finding(
                    "DOCTRINE_CRITERION_UNMARKED",
                    cid,
                    "no stamp marker follows the criterion statement",
                    "add a *[...]* marker recording conclusion and basis state",
                )
            )

    # D-04. Every reference resolves to a definition.
    corpus = "\n".join(texts.values()) + "\n" + status
    for ref in sorted(set(REF_RE.findall(corpus))):
        if ref not in defined:
            findings.append(
                Finding(
                    "DOCTRINE_REF_DANGLING",
                    ref,
                    "referenced in the corpus but defined nowhere",
                    "define the criterion, correct the reference, or delete it",
                )
            )

    # D-03. Bidirectional reconcile against the pin of record. One direction
    # finds only half the drift, which is the field-capture reconcile lesson.
    rows = set(STATUS_ROW_RE.findall(status))
    for cid in sorted(defined):
        if cid not in rows:
            findings.append(
                Finding(
                    "DOCTRINE_NO_STATUS_ROW",
                    cid,
                    "defined in doctrine but absent from DOCTRINE_STATUS.md, "
                    "so it cannot be stamped and therefore refuses",
                    "add a row to DOCTRINE_STATUS.md, or remove the criterion",
                )
            )
    for cid in sorted(rows):
        if cid not in defined:
            findings.append(
                Finding(
                    "DOCTRINE_ORPHAN_STATUS_ROW",
                    cid,
                    "has a row in DOCTRINE_STATUS.md but is defined in no doctrine file",
                    "define the criterion, or delete the row",
                )
            )

    # D-01. Reciprocal enforcement pointers. This is the check that would have
    # caught the SS-11 defect on the commit that introduced it.
    for prefix, text in texts.items():
        for pattern, direction in (
            (ENFORCED_BY_RE, "says it is enforced in"),
            (ENFORCES_RE, "says it enforces"),
        ):
            for m in pattern.finditer(text):
                target_file, target_id = m.group(1), m.group(2)
                source_block = None
                for cid, block in blocks.items():
                    if m.group(0) in block:
                        source_block = cid
                        break
                if source_block is None:
                    continue
                target_block = blocks.get(target_id)
                if target_block is None:
                    continue  # already reported as dangling
                if source_block not in target_block:
                    findings.append(
                        Finding(
                            "DOCTRINE_POINTER_NOT_RECIPROCAL",
                            f"{source_block} -> {target_id}",
                            f"{source_block} {direction} {target_file} {target_id}, "
                            f"but {target_id} never names {source_block} back",
                            f"correct the pointer in {source_block}, or name {source_block} "
                            f"in {target_id}",
                        )
                    )

    # D-06. A criterion's own marker and its status row must not disagree.
    for cid, block in blocks.items():
        marker = MARKER_RE.search(block)
        if not marker:
            continue
        says_unratified = "UNRATIFIED" in marker.group(1).upper()
        row = next(
            (ln for ln in status.splitlines() if re.match(rf"^\|\s*{re.escape(cid)}\b", ln)),
            "",
        )
        row_recorded = "recorded" in row.lower() or "conclusion recorded" in row.lower()
        if says_unratified and row_recorded:
            findings.append(
                Finding(
                    "DOCTRINE_STAMP_DISAGREEMENT",
                    cid,
                    "the criterion marker says UNRATIFIED while its row in the pin "
                    "of record says the conclusion is recorded. The pin wins by rule, "
                    "so this disagreement is silent by default",
                    "stamp the criterion marker, or clear the row",
                )
            )

    # D-07. Prose counts match the thing they count.
    for pattern, counter, label, expected in COUNT_CLAIMS:
        for text in texts.values():
            if pattern.search(text):
                actual = counter(texts)
                if actual != expected:
                    findings.append(
                        Finding(
                            "DOCTRINE_COUNT_DRIFT",
                            label,
                            f"prose claims {expected} and the corpus contains {actual}",
                            "correct the prose, or correct the list it counts",
                        )
                    )
                break

    return findings


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Doctrine integrity gate.")
    ap.add_argument("--strict", action="store_true", help="Reserved. No warnings exist yet.")
    ap.add_argument("--quiet", action="store_true", help="Print only on failure.")
    args = ap.parse_args(argv)

    try:
        findings = check(strict=args.strict)
    except FileNotFoundError as exc:
        print(
            "REFUSED DOCTRINE_CORPUS_UNREADABLE\n"
            f"  where: {exc}\n"
            "  what:  a governed doctrine file named in this tool does not exist\n"
            "  moves: create the file, or remove it from NAMESPACES in "
            "tools/validate_doctrine.py",
            file=sys.stderr,
        )
        return 2

    if gate_log:
        # One run record, then one detail record per finding. HY-1 says one line
        # per gate run, and writing one line per finding inflated both the run
        # count and the refusal rate HY-2 adjudicates against.
        gate_log.record_run("doctrine", "refuse" if findings else "pass", count=len(findings))
        for f in findings:
            gate_log.record_finding("doctrine", code=f.code, where=f.where)

    if findings:
        for f in findings:
            print(f.render(), file=sys.stderr)
            print(file=sys.stderr)
        print(
            f"validate_doctrine: {len(findings)} violation(s). "
            "rule: AGENTS.md > Documentation matrix, CLAUDE.md > design gate 1.",
            file=sys.stderr,
        )
        return 1

    if not args.quiet:
        total = sum(len(DEF_RE.findall(_read(p))) for p in NAMESPACES.values())
        print(f"validate_doctrine ok: {total} criteria, cross-references and pin reconciled")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
