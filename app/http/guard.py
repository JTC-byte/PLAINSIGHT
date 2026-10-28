"""The egress guard: case values never reach a URL, a header, a title, a log line,
an error body or a notice frame.

The guard holds, in memory, the value set of every case the store holds: claim
values and their bracket-stripped forms, item locators, and the analyst prose a
payload carries (text, note, reason, basis, caveat). It never writes the set
anywhere and never hashes it.

The server passes every response header, the page title, every Location, every
error body and every notice frame through scan(). A hit is replaced by a
refusal and counted by location; the count is the only thing recorded about it.
A request whose path or query carries a held value is refused before routing,
without echoing the value (REQUEST_VALUE_REFUSED).

The guard matches values literally. An encoded or truncated value passes it,
which is a known risk; the closed route shapes and query validators are the
second layer, because a URL may carry only uuids and fixed words.

The value set follows the log, whichever process appends to it. The guard
records a mark of the store's files when it loads (each database file's size
and modification time), and the server compares the mark on every request and
on every poll of a notice stream, reloading when it has moved. An ingest by
python -m app ingest beside a live server therefore reaches the guard before
the next request is routed.
"""

from __future__ import annotations

import json
import threading
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, unquote_plus

from app.store import db

#: Payload keys whose string values are case material.
VALUE_KEYS = frozenset({"value", "locator", "text", "note", "reason", "basis", "caveat"})

#: The shortest bracket-stripped form or prose string the guard holds. A shorter
#: string would match ordinary words in headers; the full placeholder form, with
#: its brackets, is held at any length of three or more.
MIN_BARE = 6


def _walk(obj, out: set[str]) -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in VALUE_KEYS and isinstance(value, str):
                _add(value, out)
            else:
                _walk(value, out)
    elif isinstance(obj, list):
        for value in obj:
            _walk(value, out)


def _add(value: str, out: set[str]) -> None:
    if value.startswith("<") and value.endswith(">") and len(value) >= 3:
        out.add(value)
        if len(value) - 2 >= MIN_BARE:
            out.add(value[1:-1])
    elif len(value) >= MIN_BARE:
        out.add(value)


def store_mark(root) -> tuple:
    """A cheap fingerprint of the store's database files: (name, size, mtime_ns) each.

    Any commit rewrites a database file, so the mark moves whenever any process
    appends to the log. It names files and numbers only, never a value.
    """
    root = Path(root)
    files = [root / db.PLANE_FILE] + sorted((root / db.CASES_DIR).glob("*.sqlite"))
    out = []
    for f in files:
        try:
            st = f.stat()
        except OSError:
            continue
        out.append((f.name, st.st_size, st.st_mtime_ns))
    return tuple(out)


def case_values(conn, case_id: str) -> set[str]:
    """The value set of one attached case."""
    out: set[str] = set()
    for row in conn.execute(
        "SELECT s.payload_stratum, s.payload_inline, p.payload_json FROM event_skeleton s "
        "LEFT JOIN event_payload p ON p.event_id = s.event_id WHERE s.case_id = ?",
        (case_id,),
    ):
        raw = row["payload_inline"] if row["payload_stratum"] == 2 else row["payload_json"]
        if raw:
            _walk(json.loads(raw), out)
    for row in conn.execute("SELECT value FROM claim"):
        _add(row["value"], out)
    for row in conn.execute("SELECT locator FROM item WHERE locator IS NOT NULL"):
        _add(row["locator"], out)
    return out


class Guard:
    def __init__(self, values: set[str] | None = None):
        self._values = frozenset(values or ())
        self._lock = threading.Lock()
        self.replaced: Counter = Counter()
        self.stale = False
        self.mark: tuple | None = None

    @classmethod
    def from_store(cls, root) -> "Guard":
        guard = cls()
        guard.reload(root)
        return guard

    def reload(self, root) -> None:
        mark = store_mark(root)
        values: set[str] = set()
        store = db.Store.open(root)
        try:
            for case_id in store.cases():
                if store.attach_case(case_id, create=False):
                    values |= case_values(store.conn, case_id)
        finally:
            store.close()
        with self._lock:
            self._values = frozenset(values)
            self.stale = False
            self.mark = mark

    def current(self, root) -> bool:
        """True when the guard was loaded from the store as it now stands."""
        return not self.stale and self.mark == store_mark(root)

    def scan(self, text) -> bool:
        """True when `text` carries a held value."""
        if text is None:
            return False
        if isinstance(text, bytes):
            text = text.decode("utf-8", "replace")
        values = self._values
        return any(v in text for v in values)

    def scan_request(self, target: str) -> bool:
        """True when a request target carries a held value, raw or percent-decoded."""
        return self.scan(target) or self.scan(unquote(target)) or self.scan(unquote_plus(target))

    def count(self, location: str) -> None:
        with self._lock:
            self.replaced[location] += 1

    def counts(self) -> dict[str, int]:
        with self._lock:
            return dict(sorted(self.replaced.items()))

    def held(self) -> int:
        """How many strings the guard holds. A number about the guard, never about a person."""
        return len(self._values)


def is_uuid(value) -> bool:
    return isinstance(value, str) and bool(db.UUID_RE.match(value))
