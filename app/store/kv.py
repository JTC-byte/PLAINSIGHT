"""workspace_kv: the only table a UI gesture writes.

Keys come from a closed set, and a value is a number, a boolean, a closed token
or a uuid, or a list of those. Any other string is refused (KV_VALUE_REFUSED),
so no case material reaches per-viewer state (doctrine/EGRESS.md EG-3). An
analyst act is always a PSE event and never a workspace row.
"""

from __future__ import annotations

import datetime as dt
import json

from app.model import sectors
from app.refusals import Refusal
from app.store import db

KEYS = ("scroll", "sort", "columns", "collapsed", "focus", "hops", "drawer")

#: Closed tokens a workspace value may hold: view names, lineage directions,
#: drawer states, sort orders and sector tokens.
TOKENS = frozenset(
    {"dossier", "web", "paths", "lineage", "stream", "collection", "draft"}
    | {"back", "forward"}
    | {"open", "closed"}
    | {"ts", "selector_type", "kind", "node_id", "asc", "desc"}
    | set(sectors.SECTORS)
)


def legal_value(value) -> bool:
    if isinstance(value, bool):
        return True
    if isinstance(value, (int, float)):
        return value == value and value not in (float("inf"), float("-inf"))
    if isinstance(value, str):
        return value in TOKENS or bool(db.UUID_RE.match(value))
    if isinstance(value, list):
        return all(not isinstance(v, list) and legal_value(v) for v in value)
    return False


def put(store, case_id: str, analyst: str, view: str, key: str, value) -> None:
    if key not in KEYS:
        raise Refusal("KV_KEY_REFUSED")
    if view not in TOKENS or not legal_value(value):
        raise Refusal("KV_VALUE_REFUSED", f"key={key}")
    store.attach_case(case_id)
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    store.conn.execute(
        "INSERT INTO workspace_kv (analyst, view, key, value_json, updated_at) VALUES (?, ?, ?, ?, ?) "
        "ON CONFLICT (analyst, view, key) DO UPDATE SET value_json = excluded.value_json, updated_at = excluded.updated_at",
        (analyst, view, key, json.dumps(value), now),
    )


def get(store, case_id: str, analyst: str, view: str) -> dict:
    if not store.attach_case(case_id, create=False):
        return {}
    rows = store.conn.execute(
        "SELECT key, value_json FROM workspace_kv WHERE analyst = ? AND view = ? ORDER BY key", (analyst, view)
    )
    return {r["key"]: json.loads(r["value_json"]) for r in rows}
