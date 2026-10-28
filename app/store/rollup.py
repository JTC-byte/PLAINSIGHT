"""The closed rollup vocabulary, and the increment the ingest transaction makes.

Counts come from case_rollup, maintained on write, never from COUNT(*) on a read
path (docs/PLAINSIGHT-design.md section 8.3). Every (dimension, bucket) pair a
count may use is listed in rollup_vocab, loaded at init from the generated
policy, the generated schema and ontology/selectors.yaml, plus the store's own
closed node and edge kinds. A trigger refuses any other pair, so a count can
never be bucketed by a value (ROLLUP_BUCKET_REFUSED).

A recount exists in the tests only (app/tests/test_rollup.py).
"""

from __future__ import annotations

import json

import yaml

from app import config
from app.model import sectors

SEMANTICS = config.REPO_ROOT / "policy" / "semantics.yaml"
SCHEMA = config.REPO_ROOT / "schema" / "pse-event-0.1.schema.json"
REGISTRY = config.REPO_ROOT / "ontology" / "selectors.yaml"

NODE_KINDS = ("entity", "referenced", "selector", "cluster", "candidate")
EDGE_KINDS = ("observed_about", "proposes", "member_of", "excludes")

DIMENSIONS = (
    "event_type",
    "event_subtype",
    "selector_type",
    "entity_type",
    "item_outcome",
    "node_kind",
    "edge_kind",
    "sector",
)


def vocabulary() -> list[tuple[str, str]]:
    """Every legal (dimension, bucket) pair, each a closed token."""
    semantics = yaml.safe_load(SEMANTICS.read_text(encoding="utf-8"))["semantics"]
    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    pairs: list[tuple[str, str]] = []
    for tname, tdef in semantics["event_types"].items():
        pairs.append(("event_type", tname))
        for sub in tdef.get("subtypes") or []:
            pairs.append(("event_subtype", f"{tname}.{sub}"))
    for key in registry["selectors"]:
        pairs.append(("selector_type", key))
    for key in registry["entities"]:
        pairs.append(("entity_type", key))
    outcome = schema["$defs"]["payload_PROBE_EVENT_ITEM"]["properties"]["outcome"]["enum"]
    for token in outcome:
        pairs.append(("item_outcome", token))
    pairs.extend(("node_kind", k) for k in NODE_KINDS)
    pairs.extend(("edge_kind", k) for k in EDGE_KINDS)
    pairs.extend(("sector", s) for s in sectors.SECTORS)
    return pairs


def load_vocab(conn) -> int:
    """Insert every vocabulary pair not yet listed. Returns the vocabulary size."""
    pairs = vocabulary()
    conn.executemany(
        "INSERT INTO rollup_vocab (dimension, bucket) VALUES (?, ?) ON CONFLICT DO NOTHING",
        pairs,
    )
    return len(pairs)


def increment(conn, dimension: str, bucket: str, delta: int = 1) -> None:
    """Add `delta` to one count, inside the caller's transaction."""
    conn.execute(
        "INSERT INTO case_rollup (dimension, bucket, n) VALUES (?, ?, ?) "
        "ON CONFLICT (dimension, bucket) DO UPDATE SET n = n + excluded.n",
        (dimension, bucket, delta),
    )
