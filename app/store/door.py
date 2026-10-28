"""The ingest door: every check a batch passes before the store writes anything.

The order is the one docs/PLAINSIGHT-design.md amendment 9.12 records.

1. Source. On LOCAL the path must be one of SYNTHETIC_SOURCES, tracked, and
   unmodified against HEAD, or STORE_LOCAL_SYNTHETIC_ONLY.
2. Freshness. tools/generate_pse.py --check must pass, or
   GENERATED_ARTIFACTS_STALE.
3. Shape. Rows are wrappers or bare envelopes, and the batch carries one case,
   or ROW_SHAPE_INVALID and CASE_MISMATCH.
4. Validation by the existing tool. tools/validate.py is loaded by path and its
   check_event runs on every event against an Index of the case's stored
   envelopes plus the batch. Any fired code refuses the whole batch
   (VALIDATION_REFUSED), in the form validate_file prints.
5. Store checks the validator cannot make: EVENT_ID_CONFLICT,
   SYNTHETIC_VALUE_SHAPE, PAYLOAD_STRATUM_UNDECLARED, ENVELOPE_ROUND_TRIP_FAILED,
   and the Run, Item, Claim integrity codes.

Nothing in this module writes. A refusal's detail names lines, event ids and
codes, never a value.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from app import config
from app.refusals import Refusal
from app.store import envelope

VALIDATE_TOOL = config.REPO_ROOT / "tools" / "validate.py"
GENERATE_TOOL = config.REPO_ROOT / "tools" / "generate_pse.py"

#: The shape every EXTRACT value must have on a synthetic store (RT-15 defence in depth).
SYNTHETIC_VALUE_RE = re.compile(r"^<[a-z0-9-]+>$")

_validator = None


# ---------------------------------------------------------------------------
# the tool, by path
# ---------------------------------------------------------------------------


def validator():
    """tools/validate.py, loaded by path once per process. tools/ never imports app/."""
    global _validator
    if _validator is None:
        try:
            _validator = envelope.load_tool("plainsight_tools_validate", VALIDATE_TOOL)
        except BaseException:  # noqa: BLE001 - the tool exits 2 when a dependency is missing
            raise Refusal("VALIDATOR_UNAVAILABLE", "tools/validate.py could not be imported") from None
    return _validator


def load_policy():
    try:
        return validator().load_policy()
    except SystemExit:
        raise Refusal("VALIDATOR_UNAVAILABLE", "load_policy() exited; the generated artifacts are unreadable") from None


def check_event(e, pol, index, humans):
    """The door's one binding to the tool's check_event. Returns the fired codes."""
    codes, _reached = validator().check_event(e, pol, index, humans)
    return codes


def make_index(events):
    return validator().Index(events)


# ---------------------------------------------------------------------------
# 1. source
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SourceRecord:
    """A source file the door checked.

    path is the repository-relative path of a file inside the repository and
    None otherwise: case_registry is stratum 2 and survives the shred, so a
    file name chosen outside the repository is never recorded there.
    """

    path: str | None
    sha256: str
    synthetic: bool
    checked: bool


def _git(args: list[str]) -> int:
    return subprocess.run(
        ["git", *args], cwd=config.REPO_ROOT, capture_output=True
    ).returncode


def git_tracked(rel: str) -> bool:
    return _git(["ls-files", "--error-unmatch", "--", rel]) == 0


def git_unmodified(rel: str) -> bool:
    return _git(["diff", "--quiet", "HEAD", "--", rel]) == 0


def relative_source(path) -> str | None:
    """The repository-relative POSIX path of `path`, or None when it is outside the repository."""
    resolved = Path(path).resolve()
    repo = config.REPO_ROOT.resolve()
    try:
        return resolved.relative_to(repo).as_posix()
    except ValueError:
        return None


def is_allowed_source(rel: str | None) -> bool:
    return rel is not None and rel in config.SYNTHETIC_SOURCES


def check_source(path, environment: str | None = None) -> SourceRecord:
    """Step 1. On LOCAL: allowlisted, tracked and unmodified, or STORE_LOCAL_SYNTHETIC_ONLY."""
    environment = environment or config.environment()
    rel = relative_source(path)
    try:
        data = Path(path).read_bytes()
    except OSError:
        raise Refusal("STORE_LOCAL_SYNTHETIC_ONLY", "source: the file could not be read") from None
    digest = hashlib.sha256(data).hexdigest()
    allowed = is_allowed_source(rel)
    if environment == "LOCAL":
        if not allowed:
            raise Refusal("STORE_LOCAL_SYNTHETIC_ONLY", "source: the path is not in SYNTHETIC_SOURCES")
        if not git_tracked(rel):
            raise Refusal("STORE_LOCAL_SYNTHETIC_ONLY", "source: the file is not tracked by git")
        if not git_unmodified(rel):
            raise Refusal("STORE_LOCAL_SYNTHETIC_ONLY", "source: the file differs from HEAD")
    return SourceRecord(path=rel, sha256=digest, synthetic=allowed, checked=True)


# ---------------------------------------------------------------------------
# 2. freshness
# ---------------------------------------------------------------------------


def generated_current() -> bool:
    """True when tools/generate_pse.py --check finds the generated artifacts current."""
    proc = subprocess.run(
        [sys.executable, str(GENERATE_TOOL), "--check", "--quiet"],
        cwd=config.REPO_ROOT,
        capture_output=True,
    )
    return proc.returncode == 0


def check_fresh() -> None:
    if not generated_current():
        raise Refusal("GENERATED_ARTIFACTS_STALE")


# ---------------------------------------------------------------------------
# 3. shape
# ---------------------------------------------------------------------------


def read_rows(path) -> list[tuple[int, object]]:
    """(line number, parsed object) for each non-blank line, or ROW_SHAPE_INVALID."""
    out = []
    with open(path, "r", encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                out.append((n, json.loads(line)))
            except ValueError:
                raise Refusal("ROW_SHAPE_INVALID", f"line={n}: not JSON") from None
    return out


def unwrap(row):
    """A bare envelope from a {name, description, event} wrapper, or the row itself."""
    if isinstance(row, dict) and "payload" not in row and isinstance(row.get("event"), dict) and "payload" in row["event"]:
        return row["event"]
    return row


def normalize(rows) -> list[tuple[int, object]]:
    """(line, envelope) pairs. Rows may be given bare or as (line, row) pairs."""
    out = []
    for i, row in enumerate(rows, 1):
        line, obj = row if isinstance(row, tuple) and len(row) == 2 and isinstance(row[0], int) else (i, row)
        env = unwrap(obj)
        if not isinstance(env, dict):
            raise Refusal("ROW_SHAPE_INVALID", f"line={line}: not a JSON object")
        out.append((line, env))
    return out


def batch_case(envs, store_case: str | None = None) -> str | None:
    ids = {e.get("case_id") for _, e in envs if isinstance(e.get("case_id"), str)}
    if len(ids) > 1 or (store_case is not None and ids and ids != {store_case}):
        raise Refusal("CASE_MISMATCH", f"case ids in the batch: {len(ids)}")
    return next(iter(ids)) if ids else None


# ---------------------------------------------------------------------------
# 4. validation by the tool
# ---------------------------------------------------------------------------


def _eid(e) -> str | None:
    ev = (e or {}).get("event") if isinstance(e, dict) else None
    eid = ev.get("event_id") if isinstance(ev, dict) else None
    return eid if isinstance(eid, str) else None


def validate(envs, stored: dict, pol, humans) -> dict:
    """Run check_event on every batch event. Returns {line: (envelope, codes)} for each failure."""
    index = make_index(list(stored.values()) + [e for _, e in envs])
    failures = {}
    for line, e in envs:
        codes = check_event(e, pol, index, set(humans))
        if codes:
            failures[line] = (e, set(codes))
    return failures


def render_failures(failures: dict) -> str:
    lines = []
    for line in sorted(failures):
        e, codes = failures[line]
        for c in sorted(codes):
            lines.append(f"FAIL {c} line={line} event_id={_eid(e)}")
    lines.append(f"total={len(failures)} refused; nothing was written")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 5. store checks
# ---------------------------------------------------------------------------


def classify(stored_sha: str | None, new_sha: str) -> str:
    """new, held (identical bytes, a no-op) or conflict."""
    if stored_sha is None:
        return "new"
    return "held" if stored_sha == new_sha else "conflict"


def prior_sha(stored_sha: dict, batch_sha: dict, eid) -> str | None:
    """The canonical sha an event id already has: in the store, or earlier in this batch.

    A repeat inside one batch is classified like a repeat of a stored event, so
    identical bytes are a no-op and changed bytes are EVENT_ID_CONFLICT. Without
    this, both copies reach the write and the second fails on the UNIQUE event_id.
    """
    found = stored_sha.get(eid)
    return found if found is not None else batch_sha.get(eid)


def value_shape_ok(value) -> bool:
    return isinstance(value, str) and bool(SYNTHETIC_VALUE_RE.match(value))


def store_checks(envs, stored: dict, stored_sha: dict, synthetic: bool) -> tuple[list[dict], int, list[str]]:
    """(new envelopes in write order, count already held, refusal lines)."""
    problems: list[str] = []
    index = dict(stored)
    for _, e in envs:
        index[_eid(e)] = e
    runs = {
        (x.get("payload") or {}).get("run_id")
        for x in index.values()
        if ((x.get("event") or {}).get("event_type"), (x.get("event") or {}).get("event_subtype")) == ("PROBE_EVENT", "RUN_START")
    }
    new, held = [], 0
    batch_sha: dict = {}
    for line, e in envs:
        eid = _eid(e)
        ev = e.get("event") or {}
        etype, esub = ev.get("event_type"), ev.get("event_subtype")
        p = e.get("payload") or {}
        sha = envelope.sha256(envelope.canonical(e))
        state = classify(prior_sha(stored_sha, batch_sha, eid), sha)
        batch_sha.setdefault(eid, sha)
        if state == "held":
            held += 1
            continue
        if state == "conflict":
            problems.append(f"EVENT_ID_CONFLICT line={line} event_id={eid}")
            continue
        if not envelope.round_trips(e):
            problems.append(f"ENVELOPE_ROUND_TRIP_FAILED line={line} event_id={eid}")
        if envelope.payload_stratum(etype, esub) is None:
            problems.append(f"PAYLOAD_STRATUM_UNDECLARED line={line} event_id={eid} type={etype}.{esub}")
        if synthetic and (etype, esub) == ("EXTRACT_EVENT", "CLAIM") and not value_shape_ok(p.get("value")):
            problems.append(f"SYNTHETIC_VALUE_SHAPE line={line} event_id={eid} field=payload.value")
        if (etype, esub) == ("PROBE_EVENT", "ITEM") and p.get("run_id") not in runs:
            problems.append(f"ITEM_RUN_UNRESOLVED line={line} event_id={eid}")
        if (etype, esub) == ("EXTRACT_EVENT", "CLAIM"):
            parents = (e.get("lineage") or {}).get("based_on") or []
            parent = index.get(parents[0]) if parents else None
            parent_item = (parent or {}).get("payload", {}).get("item_id") if parent else None
            if (p.get("source_ref") or {}).get("item_id") != parent_item or parent_item is None:
                problems.append(f"CLAIM_ITEM_MISMATCH line={line} event_id={eid}")
        motivated = p.get("motivated_by")
        if motivated is not None:
            target = index.get(motivated)
            tev = (target or {}).get("event") or {}
            if (tev.get("event_type"), tev.get("event_subtype")) != ("EXTRACT_EVENT", "CLAIM"):
                problems.append(f"MOTIVATED_BY_UNRESOLVED line={line} event_id={eid}")
        new.append(e)
    return _write_order(new), held, problems


def _write_order(events: list[dict]) -> list[dict]:
    """Parents before children within the batch, otherwise the batch's own order."""
    ids = {_eid(e) for e in events}
    placed: set[str] = set()
    out: list[dict] = []
    pending = list(events)
    while pending:
        progressed = False
        for e in list(pending):
            parents = [p for p in ((e.get("lineage") or {}).get("based_on") or []) if p in ids]
            if all(p in placed for p in parents):
                out.append(e)
                placed.add(_eid(e))
                pending.remove(e)
                progressed = True
                break
        if not progressed:
            out.extend(pending)
            break
    return out
