"""The invalidation stream: one Server-Sent Events stream per case.

After an ingest commits, app/store/ingest.py hands each notice to its LISTENERS.
The hub is one of them. It validates the notice against notice.schema.json
(additionalProperties false, uuid pattern, at most 50 ids) and passes it through
the egress guard; a notice that fails either is dropped and counted, never sent.
A valid notice goes to every open stream of its case, and the client refetches
the view it affects. The frame carries a sequence number, a kind, the case id and
opaque ids, never a payload or a value (amendment 9.3).

A stream resumes from Last-Event-ID, or ?after=, which is a case_seq. Notices are
not stored, so a resume sends one "case" frame at the current case_seq when the
log has moved past the client's, and the client refetches everything. The same
frame is sent when a poll finds the log advanced by another process, such as
python -m app ingest run beside a live server, and that poll reloads the egress
guard before the frame goes out.
"""

from __future__ import annotations

import json
import queue
import threading
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator

SCHEMA_PATH = Path(__file__).resolve().parent / "notice.schema.json"
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
VALIDATOR = Draft202012Validator(SCHEMA)


def valid(notice) -> bool:
    return VALIDATOR.is_valid(notice)


def frame(notice: dict) -> bytes:
    data = json.dumps(notice, sort_keys=True, separators=(",", ":"))
    return f"id: {notice['seq']}\nevent: notice\ndata: {data}\n\n".encode("utf-8")


def resume_notice(case_id: str, seq: int) -> dict:
    return {"seq": seq, "kind": "case", "case_id": case_id, "ids": [case_id]}


class Hub:
    """The open streams of every case, and the notices dropped by reason."""

    def __init__(self, guard):
        self.guard = guard
        self._subs: dict[str, set[queue.Queue]] = {}
        self._lock = threading.Lock()
        self.dropped: Counter = Counter()
        self.closed = False

    def check(self, notice) -> str | None:
        """The reason a notice may not be sent, or None."""
        if not valid(notice):
            return "schema"
        if self.guard.scan(json.dumps(notice)):
            self.guard.count("notice frame")
            return "guard"
        return None

    def publish(self, notice) -> bool:
        reason = self.check(notice)
        if reason is not None:
            with self._lock:
                self.dropped[reason] += 1
            return False
        self.guard.stale = True
        with self._lock:
            targets = list(self._subs.get(notice["case_id"], ()))
        for q in targets:
            q.put(notice)
        return True

    def subscribe(self, case_id: str) -> queue.Queue:
        q: queue.Queue = queue.Queue()
        with self._lock:
            self._subs.setdefault(case_id, set()).add(q)
        return q

    def unsubscribe(self, case_id: str, q: queue.Queue) -> None:
        with self._lock:
            self._subs.get(case_id, set()).discard(q)

    def close(self) -> None:
        self.closed = True
        with self._lock:
            queues = [q for qs in self._subs.values() for q in qs]
        for q in queues:
            q.put(None)

    def drop_counts(self) -> dict[str, int]:
        with self._lock:
            return dict(sorted(self.dropped.items()))
