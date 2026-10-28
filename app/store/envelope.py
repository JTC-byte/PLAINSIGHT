"""An envelope split into its skeleton columns and its payload, and put back.

The artifact is event_skeleton plus event_payload (docs/PLAINSIGHT-design.md
amendment 9.2). The
split is exact: compose(decompose(e)) is byte-equal to e in canonical JSON, and
the door refuses an envelope for which that does not hold
(ENVELOPE_ROUND_TRIP_FAILED), so a replay never rebuilds something other than
what arrived.

Three envelope keys are optional on the wire: lineage, lineage.transform and
source.sw_version. A null and an absent key are different bytes, so the
skeleton records which optional keys were present in optional_keys. This and
the pse_version and derived_from columns are columns of event_skeleton, the
table docs/PLAINSIGHT-design.md amendment 9.2 names, and they exist so the split
is exact.

The payload stratum is read at runtime from spec/layer-model.yaml, and the
stratum set it is checked against comes from layer_model_strata() in
tools/validate_retention.py, loaded by path. Nothing here hard-codes a
type's stratum.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import yaml

from app import config

LAYER_MODEL = config.REPO_ROOT / "spec" / "layer-model.yaml"
RETENTION_TOOL = config.REPO_ROOT / "tools" / "validate_retention.py"

OPTIONAL_KEYS = ("lineage", "lineage.transform", "source.sw_version")


def canonical(obj) -> bytes:
    """Canonical JSON: sorted keys, no whitespace, UTF-8."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def decompose(env: dict) -> dict:
    """The skeleton columns of one envelope, and its payload under 'payload'."""
    ev = env["event"]
    src = env["source"]
    lin = env.get("lineage") if "lineage" in env else None
    present = []
    if "lineage" in env:
        present.append("lineage")
        if isinstance(lin, dict) and "transform" in lin:
            present.append("lineage.transform")
    if "sw_version" in src:
        present.append("source.sw_version")
    parents = None
    transform = None
    if isinstance(lin, dict):
        parents = lin.get("based_on")
        transform = lin.get("transform")
    return {
        "event_id": ev["event_id"],
        "case_id": env["case_id"],
        "pse_version": env["pse_version"],
        "derived_from": env["derived_from"],
        "event_type": ev["event_type"],
        "event_subtype": ev["event_subtype"],
        "ts": ev["ts"],
        "producer": src["producer"],
        "environment": src["environment"],
        "platform_id": src["platform_id"],
        "sw_version": src.get("sw_version"),
        "parents_json": None if parents is None else json.dumps(parents, separators=(",", ":")),
        "transform": transform,
        "optional_keys": json.dumps(present, separators=(",", ":")),
        "envelope_sha256": sha256(canonical(env)),
        "payload": env["payload"],
    }


def compose(row, payload) -> dict:
    """An envelope from a skeleton row (a mapping) and its payload object."""
    present = set(json.loads(row["optional_keys"]))
    source = {
        "platform_id": row["platform_id"],
        "environment": row["environment"],
        "producer": row["producer"],
    }
    if "source.sw_version" in present:
        source["sw_version"] = row["sw_version"]
    env = {
        "pse_version": row["pse_version"],
        "derived_from": row["derived_from"],
        "case_id": row["case_id"],
        "event": {
            "event_id": row["event_id"],
            "event_type": row["event_type"],
            "event_subtype": row["event_subtype"],
            "ts": row["ts"],
        },
        "source": source,
        "payload": payload,
    }
    if "lineage" in present:
        lineage = {"based_on": json.loads(row["parents_json"]) if row["parents_json"] is not None else None}
        if "lineage.transform" in present:
            lineage["transform"] = row["transform"]
        env["lineage"] = lineage
    return env


def round_trips(env: dict) -> bool:
    """True when the skeleton columns and the payload rebuild the envelope exactly."""
    try:
        cols = decompose(env)
    except (KeyError, TypeError, AttributeError):
        return False
    return canonical(compose(cols, cols["payload"])) == canonical(env)


# ---------------------------------------------------------------------------
# strata
# ---------------------------------------------------------------------------

#: Read caches keyed on the source file's size and mtime, so an edited model or
#: tool is read again rather than served stale.
_cache: dict = {}


def _stamp(path: Path) -> tuple:
    st = path.stat()
    return (st.st_mtime_ns, st.st_size)


def load_tool(name: str, path: Path):
    """Load a tools/ module by path, so tools/ never imports app/ and is not edited."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def layer_model_strata():
    """(STRATA, SURVIVING_STRATA, CROSSING_STRATA) from the retention tool, or None."""
    try:
        key = _stamp(RETENTION_TOOL)
    except OSError:
        return None
    cached = _cache.get("strata")
    if cached and cached[0] == key:
        return cached[1]
    try:
        value = load_tool("plainsight_tools_validate_retention", RETENTION_TOOL).layer_model_strata()
    except Exception:  # noqa: BLE001 - reported by the caller as an undeclared stratum
        return None
    _cache["strata"] = (key, value)
    return value


def _model_strata() -> dict:
    key = _stamp(LAYER_MODEL)
    cached = _cache.get("model")
    if cached and cached[0] == key:
        return cached[1]
    model = yaml.safe_load(LAYER_MODEL.read_text(encoding="utf-8")) or {}
    out = {}
    for tname, tdef in (model.get("event_types") or {}).items():
        declared = ((tdef or {}).get("retention") or {}).get("payload_stratum")
        for sname in (tdef or {}).get("subtypes") or {}:
            out[(tname, sname)] = declared.get(sname) if isinstance(declared, dict) else declared
    _cache["model"] = (key, out)
    return out


def payload_stratum(event_type: str, event_subtype: str):
    """The stored stratum (1 or 2) of a payload, or None when the store has no home for it.

    Stratum 1 goes to the per-case event_payload table. A surviving stratum goes
    inline on the skeleton, and the only surviving stratum a payload declares
    today is 2. Anything else, or a type the model does not declare, is None and
    the door refuses it as PAYLOAD_STRATUM_UNDECLARED.
    """
    strata = layer_model_strata()
    if strata is None:
        return None
    _all, surviving, _crossing = strata
    try:
        declared = _model_strata().get((event_type, event_subtype))
    except (OSError, yaml.YAMLError):
        return None
    if declared == 1 and 1 in _all:
        return 1
    if declared == 2 and 2 in surviving:
        return 2
    return None
