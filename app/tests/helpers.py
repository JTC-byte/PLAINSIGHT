"""Shared helpers for the app tests.

The only input is conformance/must-pass.jsonl. Variants are mutated in memory,
and where a non-placeholder value is needed it is derived as value[1:-1], so no
new value literal enters the tree. Every store lives under pytest's tmp_path.

A check is a function of a Ctx that raises AssertionError when the property it
names does not hold. Each test module calls its checks from ordinary tests and
lists them in CONTROLS with a breaker, a function that removes the mechanism or
breaks the input. app/tests/test_controls.py applies each breaker and fails the
suite if the paired check stays green.
"""

from __future__ import annotations

import copy
import hashlib
import json
import sqlite3
from pathlib import Path

from app import config
from app.refusals import Refusal
from app.store import db, door, ingest, replay

CORPUS = config.REPO_ROOT / "conformance" / "must-pass.jsonl"

#: The corpus's one case. A case id is an opaque uuid, not a selector.
CASE = json.loads(CORPUS.read_text(encoding="utf-8").splitlines()[0])["event"]["case_id"]


def corpus_rows() -> list[dict]:
    return [json.loads(line) for line in CORPUS.read_text(encoding="utf-8").splitlines() if line.strip()]


def corpus_events() -> list[dict]:
    return [copy.deepcopy(r["event"]) for r in corpus_rows()]


def named(events: list[dict], name: str) -> dict:
    """The event in `events` whose corpus row carries `name`."""
    eid = next(r["event"]["event"]["event_id"] for r in corpus_rows() if r["name"] == name)
    return next(e for e in events if e["event"]["event_id"] == eid)


def eid_of(name: str) -> str:
    return next(r["event"]["event"]["event_id"] for r in corpus_rows() if r["name"] == name)


def corpus_strings() -> set[str]:
    """Every value-bearing string in the corpus: claim values and their bracket-stripped
    forms, locators, and analyst prose. None may reach a refusal, a log line or a filename."""
    out: set[str] = set()
    for e in corpus_events():
        p = e.get("payload") or {}
        if isinstance(p.get("value"), str):
            out.add(p["value"])
            out.add(p["value"][1:-1])
        for key in ("locator", "text", "basis", "reason", "note"):
            if isinstance(p.get(key), str):
                out.add(p[key])
    return {s for s in out if len(s) >= 6}


def value_hashes() -> set[str]:
    return {hashlib.sha256(s.encode("utf-8")).hexdigest() for s in corpus_strings()}


def refusal_of(fn, *args, **kwargs) -> Refusal:
    """The Refusal `fn` raises. A call that returns, or crashes instead of refusing, is an AssertionError."""
    try:
        fn(*args, **kwargs)
    except Refusal as refusal:
        return refusal
    except Exception as exc:  # noqa: BLE001 - a crash where a refusal belongs fails the check
        raise AssertionError(f"expected a refusal and the call raised {type(exc).__name__}") from exc
    raise AssertionError("expected a refusal and the call returned")


def sql_error(conn, sql: str, params=()) -> str:
    """The message of the error a statement raises. A statement that succeeds is an AssertionError."""
    try:
        conn.execute(sql, params)
    except sqlite3.DatabaseError as exc:
        return str(exc)
    raise AssertionError("expected the statement to be refused and it ran")


def files_digest(root: Path) -> dict[str, str]:
    root = Path(root)
    return {
        p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def count(store, sql: str, params=()) -> int:
    return store.conn.execute(sql, params).fetchone()[0]


class Ctx:
    """One test's stores, monkeypatch and scratch directory."""

    def __init__(self, tmp_path: Path, monkeypatch):
        self.tmp = tmp_path
        self.mp = monkeypatch
        self.extra_roots: list[Path] = []
        self._stores: list = []
        self._source = None

    def store(self, name: str = "store"):
        s = db.Store.init(self.tmp / name)
        self._stores.append(s)
        return s

    def source(self):
        if self._source is None:
            self._source = door.check_source(CORPUS)
        return self._source

    def ingest(self, store, events=None):
        rows = corpus_events() if events is None else events
        return ingest.ingest_batch(store, rows, None, source=self.source())

    def built(self, name: str = "store", events=None):
        s = self.store(name)
        self.ingest(s, events)
        s.attach_case(CASE, create=False)
        return s

    def stored(self, store) -> dict:
        envs, _ = replay.stored_envelopes(store, CASE)
        store.attach_case(CASE, create=False)
        return envs

    def close(self) -> None:
        for s in self._stores:
            try:
                s.close()
            except Exception:  # noqa: BLE001 - a test may have closed it
                pass
