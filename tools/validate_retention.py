#!/usr/bin/env python3
"""Retention validator.

STUB. Wired into .githooks/pre-commit at Step 1 so the mechanism exists and is
called. The repo-scan check itself is implemented at Step 8.

A stubbed job that is wired is a mechanism. A comment describing a future job is
not. This file exits 0 and says plainly that it checked nothing, so the gap is a
known gap rather than a silent pass.
"""
import sys

STUB_NOTICE = (
    "validate_retention.py: STUB, no check performed.\n"
    "  scheduled: Step 8 of docs/THE-GAMEPLAN.md\n"
    "  tracked:   D-001 in docs/plainsight_worklog.md\n"
    "  meanwhile: the pre-commit hook is a wired mechanism with no check behind it."
)


def main(argv):
    print(STUB_NOTICE, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
