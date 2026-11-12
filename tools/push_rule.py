#!/usr/bin/env python3
"""Rule 1 of AGENTS.md section 5 as a mechanism: no push without a written case.

The maintainer set the rule for every lane on 2026-11-11: local commits only,
until he lifts it, and a push only on his word in the PLAINSIGHT chat on a
written case, a major release or a major bug fix, naming what it is, why it
cannot wait, and what it will cost. Until 2026-11-12 the rule lived in
AGENTS.md alone, which design gate 1 says is not yet a rule. The maintainer
asked for this hook on 2026-11-12, by his click "Yes, build it" in the
PLAINSIGHT chat.

`.githooks/pre-push` runs this file for every push from a checkout whose
`core.hooksPath` is `.githooks`, and from every worktree of one whose tree
holds the hook: git resolves the relative hooks path from the root of the
tree it runs in, so a worktree at a commit older than the hook runs none
(measured on 2026-11-12 with `git hook run`). Git hands the hook the remote's name
and address as arguments and one line per ref the push would update on stdin:
the local ref, the local object, the remote ref and the remote object. The push
is admitted only when the environment variable PLAINSIGHT_PUSH_CASE names a
file that exists and names the new tip of every ref the push updates, as a hex
prefix of at least seven characters, and every remote ref it deletes, by its
full name standing alone. A tip carries its history, so a case need not list
the commits beneath it. For an annotated tag the tip is the tag object, whose
id the refusal prints. Anything else is refused after git has read the
remote's refs and before it sends anything, and so is a ref line this file
cannot read.

What it does not do. It cannot see his word: the case file is where the
session writes his line and the commits, and this file checks only that the
case exists and names what is pushed, not who wrote it. `git push --no-verify`
skips every pre-push hook, and a checkout whose `core.hooksPath` is unset runs
none, so the hook makes an accidental push impossible and a deliberate one
explicit; it is not a lock against a person. The remote's address is read and
never printed. Lifting the rule removes `.githooks/pre-push` in the commit that
edits rule 1.

`--self-test` first plants each refusal in memory, then pushes from a scratch
repository through the real `.githooks/pre-push` into a scratch bare
repository, with every GIT_ variable of the calling process removed and the
user's git configuration replaced by an empty file. It asserts each refusal
and each admission, so it fails when the refusal, the case check, the deletion
check or the hook's wiring is removed. It contacts no network remote. On Linux
it also fails when the hook file loses its executable mode, because git then
ignores the hook and the first push lands.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOOK_DIR = ROOT / ".githooks"
CASE_VAR = "PLAINSIGHT_PUSH_CASE"

#: The shortest hex prefix a case may name a commit by. Seven is git's own
#: default abbreviation, and a shorter prefix matches too much to mean a commit.
MIN_PREFIX = 7
HEX = re.compile(r"(?<![0-9a-f])[0-9a-f]{%d,64}(?![0-9a-f])" % MIN_PREFIX)

RULE_LINES = (
    "  rule:  AGENTS.md section 5 rule 1: local commits only, until the maintainer lifts it,",
    "         and a push only on his word in the PLAINSIGHT chat on a written case.",
)
MOVES_LINES = (
    "  moves: keep the commit local; work is saved by a local commit, never by a push.",
    "         Or write the case (a major release or a major bug fix: what it is, why it",
    "         cannot wait, what it will cost), take his word on it in the PLAINSIGHT chat,",
    "         name in it the new tip of every ref the push updates and every ref it deletes, and push",
    "         again with PLAINSIGHT_PUSH_CASE set to the case file's path.",
    "         Or, once he lifts the rule, remove .githooks/pre-push in the commit that",
    "         edits rule 1.",
)

DETAIL = {
    "PUSH_REFUSED_LOCAL_ONLY": "no written case is named for this push",
    "PUSH_CASE_NOT_FOUND": "PLAINSIGHT_PUSH_CASE does not name an existing file",
    "PUSH_CASE_DOES_NOT_NAME_COMMIT": "the case does not name everything this push carries",
    "PUSH_REF_LINE_UNREADABLE": "git handed the hook a ref line this tool cannot read, so it refuses rather than guess",
}


def parse_updates(text: str) -> tuple[list[tuple[str, str, str, str]], bool]:
    """The ref lines git hands a pre-push hook, and whether every line read."""
    updates = []
    readable = True
    for line in text.splitlines():
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) != 4 or not all(re.fullmatch(r"[0-9a-f]+", p) for p in (parts[1], parts[3])):
            readable = False
            continue
        updates.append((parts[0], parts[1], parts[2], parts[3]))
    return updates, readable


def _is_zero(obj: str) -> bool:
    return set(obj) == {"0"}


def _names_ref(text: str, ref: str) -> bool:
    """Whether the case names the ref as a whole token.

    A substring test admitted the deletion of refs/heads/main under a case that
    named refs/heads/maintenance, found by the second-model read of 2026-11-12.
    The ref must stand alone: preceded by the start of a line, a space, a quote,
    a backtick or an opening bracket, and followed by the end of a line, a
    space, a quote, a backtick, a closing bracket, a comma, a semicolon, a
    colon, or a full stop that ends the sentence.
    """
    pattern = (
        r"(?:^|(?<=[\s`'\"(\[]))"
        + re.escape(ref)
        + r"(?=$|[\s`'\",;:)\]]|[.](?:$|\s))"
    )
    return re.search(pattern, text, re.MULTILINE) is not None


def decide(updates, readable: bool, case_value: str | None, cwd: Path) -> tuple[str | None, list[str]]:
    """(code, what is missing). A code of None admits the push."""
    if not readable:
        return "PUSH_REF_LINE_UNREADABLE", []
    if not updates:
        return None, []
    if not case_value:
        return "PUSH_REFUSED_LOCAL_ONLY", []
    path = Path(case_value)
    if not path.is_absolute():
        path = cwd / path
    if not path.is_file():
        return "PUSH_CASE_NOT_FOUND", []
    text = path.read_text(encoding="utf-8", errors="replace")
    prefixes = set(HEX.findall(text.lower()))
    missing = []
    for _local_ref, local_obj, remote_ref, _remote_obj in updates:
        if _is_zero(local_obj):
            if not _names_ref(text, remote_ref):
                missing.append(f"the deletion of {remote_ref}")
        elif not any(local_obj.startswith(p) for p in prefixes):
            missing.append(f"the object {local_obj[:12]} for {remote_ref}")
    if missing:
        return "PUSH_CASE_DOES_NOT_NAME_COMMIT", missing
    return None, []


def refusal_text(code: str, missing: list[str]) -> str:
    lines = ["", f"push refused: {code}, {DETAIL[code]}."]
    for item in missing:
        lines.append(f"  missing: {item}")
    lines.extend(RULE_LINES)
    lines.extend(MOVES_LINES)
    return "\n".join(lines) + "\n"


def run_hook(argv: list[str]) -> int:
    updates, readable = parse_updates(sys.stdin.read())
    case_value = os.environ.get(CASE_VAR)
    code, missing = decide(updates, readable, case_value, Path.cwd())
    if code:
        sys.stderr.write(refusal_text(code, missing))
        return 1
    if updates:
        sys.stderr.write(
            f"push admitted under AGENTS.md section 5 rule 1: the case {Path(case_value).name} "
            f"names all {len(updates)} ref update(s) this push carries.\n"
        )
    return 0


# -- self-test ---------------------------------------------------------------


class _Checks:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.count = 0

    def expect(self, label: str, ok: bool, detail: str = "") -> None:
        self.count += 1
        if not ok:
            self.failures.append(f"{label}{': ' + detail if detail else ''}")


def _memory_checks(checks: _Checks, tmp: Path) -> None:
    obj = "4f" * 20
    other = "a1" * 20
    zero = "0" * 40
    line = f"refs/heads/main {obj} refs/heads/main {zero}\n"
    case = tmp / "case-memory.md"

    updates, readable = parse_updates(line)
    checks.expect("no case refuses", decide(updates, readable, None, tmp)[0] == "PUSH_REFUSED_LOCAL_ONLY")
    checks.expect("an empty case refuses", decide(updates, readable, "", tmp)[0] == "PUSH_REFUSED_LOCAL_ONLY")
    checks.expect(
        "an absent case file refuses",
        decide(updates, readable, str(tmp / "absent.md"), tmp)[0] == "PUSH_CASE_NOT_FOUND",
    )
    case.write_text(f"His word on {other[:12]}.\n", encoding="utf-8")
    checks.expect(
        "a case naming another commit refuses",
        decide(updates, readable, str(case), tmp)[0] == "PUSH_CASE_DOES_NOT_NAME_COMMIT",
    )
    # Literal lengths rather than MIN_PREFIX, so that lowering the constant
    # fails this check instead of moving it.
    case.write_text(f"His word on {obj[:6]}.\n", encoding="utf-8")
    checks.expect(
        "a prefix shorter than seven refuses",
        decide(updates, readable, str(case), tmp)[0] == "PUSH_CASE_DOES_NOT_NAME_COMMIT",
    )
    case.write_text(f"His word on {obj[:7]}.\n", encoding="utf-8")
    checks.expect("a seven-character prefix admits", decide(updates, readable, str(case), tmp)[0] is None)
    case.write_text(f"His word on {obj[:9].upper()}.\n", encoding="utf-8")
    checks.expect("an upper-case prefix admits", decide(updates, readable, str(case), tmp)[0] is None)

    two, readable = parse_updates(line + f"refs/heads/b {other} refs/heads/b {zero}\n")
    case.write_text(f"His word on {obj[:12]} only.\n", encoding="utf-8")
    checks.expect(
        "the first of two tips named refuses",
        decide(two, readable, str(case), tmp)[0] == "PUSH_CASE_DOES_NOT_NAME_COMMIT",
    )
    case.write_text(f"His word on {other[:12]} only.\n", encoding="utf-8")
    checks.expect(
        "the second of two tips named refuses",
        decide(two, readable, str(case), tmp)[0] == "PUSH_CASE_DOES_NOT_NAME_COMMIT",
    )
    case.write_text(f"His word on {obj[:12]} and {other[:12]}.\n", encoding="utf-8")
    checks.expect("both tips named admits", decide(two, readable, str(case), tmp)[0] is None)

    deletion, readable = parse_updates(f"(delete) {zero} refs/heads/old {obj}\n")
    case.write_text(f"His word on {obj[:12]}.\n", encoding="utf-8")
    checks.expect(
        "a deletion whose ref the case does not name refuses",
        decide(deletion, readable, str(case), tmp)[0] == "PUSH_CASE_DOES_NOT_NAME_COMMIT",
    )
    case.write_text("His word to delete refs/heads/old.\n", encoding="utf-8")
    checks.expect("a deletion whose ref the case names admits", decide(deletion, readable, str(case), tmp)[0] is None)
    case.write_text("His word to delete `refs/heads/old`, and nothing else\n", encoding="utf-8")
    checks.expect("a deletion named in backticks admits", decide(deletion, readable, str(case), tmp)[0] is None)
    case.write_text("His word to delete refs/heads/old-x, refs/heads/oldest and refs/heads/old.x.\n", encoding="utf-8")
    checks.expect(
        "a deletion whose ref the case names only inside longer names refuses",
        decide(deletion, readable, str(case), tmp)[0] == "PUSH_CASE_DOES_NOT_NAME_COMMIT",
    )
    deletion64, readable64 = parse_updates(f"(delete) {'0' * 64} refs/heads/old {'5e' * 32}\n")
    case.write_text("His word to delete refs/heads/old.\n", encoding="utf-8")
    checks.expect(
        "a deletion in a sha256 repository whose ref the case names admits",
        decide(deletion64, readable64, str(case), tmp)[0] is None,
    )

    garbled, readable = parse_updates("refs/heads/main not-an-object\n")
    checks.expect(
        "an unreadable ref line refuses even with a case",
        decide(garbled, readable, str(case), tmp)[0] == "PUSH_REF_LINE_UNREADABLE",
    )
    nothing, readable = parse_updates("")
    checks.expect("a push that updates nothing admits", decide(nothing, readable, None, tmp)[0] is None)


def _end_to_end_checks(checks: _Checks, tmp: Path) -> None:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_") and k != CASE_VAR}
    empty_config = tmp / "empty.gitconfig"
    empty_config.write_text("", encoding="utf-8")
    env.update(
        GIT_CONFIG_NOSYSTEM="1",
        GIT_CONFIG_GLOBAL=str(empty_config),
        GIT_CEILING_DIRECTORIES=str(tmp),
        GIT_TERMINAL_PROMPT="0",
    )
    remote = tmp / "remote.git"
    work = tmp / "work"
    work.mkdir()

    def git(*args: str, cwd: Path = work, case: str | None = None):
        run_env = dict(env)
        if case is not None:
            run_env[CASE_VAR] = case
        return subprocess.run(["git", *args], cwd=cwd, env=run_env, capture_output=True, text=True)

    setup = [
        git("init", "-q", "--bare", str(remote), cwd=tmp),
        git("init", "-q"),
        git("config", "user.name", "push-rule-self-test"),
        git("config", "user.email", "push-rule-self-test"),
        git("remote", "add", "origin", remote.as_posix()),
    ]
    (work / "note.txt").write_text("a scratch commit for the push rule's self-test\n", encoding="utf-8")
    setup += [git("add", "note.txt"), git("commit", "-q", "-m", "scratch")]
    setup.append(git("commit", "-q", "--allow-empty", "-m", "scratch, second"))
    # The hooks path is set after the scratch commit, so that commit runs no
    # hook of this repository and every push below runs the real pre-push.
    setup.append(git("config", "core.hooksPath", HOOK_DIR.as_posix()))
    broken = [p for p in setup if p.returncode != 0]
    if broken:
        raise RuntimeError("the scratch repositories could not be set up: " + broken[0].stderr.strip())
    head = git("rev-parse", "HEAD").stdout.strip()
    first = git("rev-parse", "HEAD~1").stdout.strip()

    def remote_has(ref: str) -> bool:
        return git("rev-parse", "--verify", "-q", ref, cwd=remote).returncode == 0

    target = "HEAD:refs/heads/main"
    p = git("push", "-q", "origin", target)
    checks.expect(
        "the real hook refuses a push that names no case",
        p.returncode != 0 and "PUSH_REFUSED_LOCAL_ONLY" in p.stderr and not remote_has("refs/heads/main"),
        f"exit {p.returncode}, the remote holds main: {remote_has('refs/heads/main')}",
    )
    p = git("push", "-q", "origin", target, case=str(tmp / "absent.md"))
    checks.expect(
        "the real hook refuses a case file that does not exist",
        p.returncode != 0 and "PUSH_CASE_NOT_FOUND" in p.stderr and not remote_has("refs/heads/main"),
        f"exit {p.returncode}",
    )
    wrong = tmp / "case-wrong.md"
    wrong.write_text("His word on " + ("b2" * 20)[:12] + ".\n", encoding="utf-8")
    p = git("push", "-q", "origin", target, case=str(wrong))
    checks.expect(
        "the real hook refuses a case that names another commit",
        p.returncode != 0 and "PUSH_CASE_DOES_NOT_NAME_COMMIT" in p.stderr and not remote_has("refs/heads/main"),
        f"exit {p.returncode}",
    )
    right = tmp / "case-right.md"
    right.write_text(f"His word on {head[:12]}.\n", encoding="utf-8")
    p = git("push", "-q", "origin", target, case=str(right))
    landed = git("rev-parse", "refs/heads/main", cwd=remote).stdout.strip()
    checks.expect(
        "the real hook admits a case that names the commit",
        p.returncode == 0 and landed == head,
        f"exit {p.returncode}, {p.stderr.strip()[:200]}",
    )
    p = git("push", "-q", "origin", ":refs/heads/main", case=str(right))
    checks.expect(
        "the real hook refuses a deletion the case does not name",
        p.returncode != 0 and "PUSH_CASE_DOES_NOT_NAME_COMMIT" in p.stderr and remote_has("refs/heads/main"),
        f"exit {p.returncode}",
    )
    deletion = tmp / "case-delete.md"
    deletion.write_text("His word to delete refs/heads/main.\n", encoding="utf-8")
    p = git("push", "-q", "origin", ":refs/heads/main", case=str(deletion))
    checks.expect(
        "the real hook admits a deletion the case names",
        p.returncode == 0 and not remote_has("refs/heads/main"),
        f"exit {p.returncode}, {p.stderr.strip()[:200]}",
    )
    pair = (f"{first}:refs/heads/a", f"{head}:refs/heads/b")
    one = tmp / "case-one-of-two.md"
    one.write_text(f"His word on {head[:12]}.\n", encoding="utf-8")
    p = git("push", "-q", "origin", *pair, case=str(one))
    checks.expect(
        "the real hook refuses a two-ref push whose case names one tip",
        p.returncode != 0 and "PUSH_CASE_DOES_NOT_NAME_COMMIT" in p.stderr
        and not remote_has("refs/heads/a") and not remote_has("refs/heads/b"),
        f"exit {p.returncode}",
    )
    both = tmp / "case-both.md"
    both.write_text(f"His word on {first[:12]} and {head[:12]}.\n", encoding="utf-8")
    p = git("push", "-q", "origin", *pair, case=str(both))
    checks.expect(
        "the real hook admits a two-ref push whose case names both tips",
        p.returncode == 0 and remote_has("refs/heads/a") and remote_has("refs/heads/b"),
        f"exit {p.returncode}, {p.stderr.strip()[:200]}",
    )


def self_test(quiet: bool) -> int:
    if not (HOOK_DIR / "pre-push").is_file():
        print("push-rule self-test: .githooks/pre-push does not exist, so no push runs this rule", file=sys.stderr)
        return 1
    checks = _Checks()
    with tempfile.TemporaryDirectory(prefix="push-rule-self-test-", ignore_cleanup_errors=True) as name:
        tmp = Path(name)
        _memory_checks(checks, tmp)
        memory = checks.count
        try:
            _end_to_end_checks(checks, tmp)
        except FileNotFoundError:
            print("push-rule self-test: git is not on PATH, so the hook cannot be exercised", file=sys.stderr)
            return 2
        except RuntimeError as exc:
            print(f"push-rule self-test: {exc}", file=sys.stderr)
            return 2
    if checks.failures:
        print(f"push-rule self-test: {len(checks.failures)} of {checks.count} checks failed", file=sys.stderr)
        for failure in checks.failures:
            print(f"  FAILED  {failure}", file=sys.stderr)
        return 1
    if not quiet:
        print(f"push-rule self-test: all {checks.count} checks held, {checks.count - memory} of them through the real hook")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("remote", nargs="?", help="the remote's name, as git hands it to the hook")
    ap.add_argument("url", nargs="?", help="the remote's address, as git hands it to the hook; read, never printed")
    ap.add_argument("--self-test", action="store_true", help="plant each refusal and push through the real hook")
    ap.add_argument("--quiet", action="store_true", help="print nothing when the self-test holds")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test(args.quiet)
    return run_hook(argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
