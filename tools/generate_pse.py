#!/usr/bin/env python3
"""Generate the Step 7 artifacts from spec/layer-model.yaml, and refuse drift.

The layer model is the single source for the event schema, the semantics policy,
the lineage policy, the producer-authority policy, and the violation-code
vocabulary (spec/layer-model.yaml header, pse.generates). This tool reads that
file and ontology/selectors.yaml and writes the five generated artifacts. It is
the only writer of those five files. A hand edit to any of them is drift, and
`--check` regenerates every artifact in memory, compares it byte for byte with
the file on disk, and refuses on any difference, so a generated file cannot
quietly stop matching its source. That check is what makes "generated, never
hand-edited" a gate rather than a sentence (CLAUDE.md design gate 1).

What the generator decides, and where it says so. The model leaves a small
number of shapes unstated, listed in docs/THE-GAMEPLAN.md section 2.1's
generation contract and in the Step 7 mapping report. Each decision this tool
takes is a reading rather than a rule: it is recorded under READINGS below, is
written into the schema's `$comment`, and is restated in
spec/pse-semantics-contract.md, where the operator confirms or reverses it.
The tool never invents a field, a code, or a producer. Where the model is
silent on which subtypes may carry an optional field, S7-R1 states the rule
applied.

Exit codes: 0 written or current, 1 a generated artifact is stale or missing
under --check, 2 the model or the registry could not be read.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print(
        "REFUSED DEPENDENCY_MISSING\n"
        "  where: tools/generate_pse.py\n"
        "  what:  PyYAML is not installed, and the layer model is YAML\n"
        "  moves: pip install pyyaml, which AGENTS.md section 5 names as the one dependency",
        file=sys.stderr,
    )
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "spec" / "layer-model.yaml"
REGISTRY = ROOT / "ontology" / "selectors.yaml"
TOOL = "tools/generate_pse.py"

#: The five generated artifacts, keyed by the token the layer model's
#: pse.generates block names each by. The path is read from the model, so a
#: renamed target there is picked up here rather than diverging.
GENERATED_KEYS = ("schema", "semantics", "lineage", "producer-authority", "violation-codes")

#: Readings the generator had to take where the model is silent. Each is stated
#: in the schema's $comment and in the contract. Confirming one is the operator's
#: act; changing one is an edit here and a regeneration, never a hand edit to
#: an output.
READINGS = {
    "S7-R1": (
        "Which optional payload fields a subtype may carry. The model states "
        "required fields per subtype and field shapes per type, and with "
        "additionalProperties false on every branch the generator needs a rule. "
        "The rule: a field is legal on a subtype when it is required there; or "
        "when no subtype of the type requires it (a free optional, legal on every "
        "subtype of the type); or when a rule whose `when` names a field condition "
        "requires it, on the subtypes where that field is legal; or when a runtime "
        "rule requires it, on every subtype of the type, because a runtime condition "
        "cannot be bound to a subtype by the model. Enum-by-subtype fields follow "
        "their enum."
    ),
    "S7-R2": (
        "The shape of IDENTITY_EVENT member_seams. The model declares an object and "
        "says in a comment it maps a member id to the rationale codes that hold for "
        "that member. The generator emits an object whose property names are uuids "
        "and whose values are non-empty arrays drawn from the rationale-code enum."
    ),
    "S7-R3": (
        "ASSESS_EVENT geo and the two raw_span arrays have no declared shape and are "
        "emitted open: geo as an object with no property constraint, raw_span as an "
        "array with no item constraint. The model owns their shape and does not "
        "state it, so the generator does not narrow it."
    ),
    "S7-R4": (
        "A field with `registry: ontology/selectors.yaml` is emitted as a closed "
        "enum of the registry's selector keys, so the vocabulary is closed at the "
        "corpus boundary in the schema itself. A value outside it fails an enum "
        "keyword at a registry-bound path, which the runner names "
        "SELECTOR_TYPE_UNREGISTERED rather than ENUM_VALUE_INVALID. A registry "
        "change therefore stales the schema, and --check catches it."
    ),
    "S7-R5": (
        "A prohibited name at depth zero is refused twice: the schema refuses it as an "
        "unknown property, and the denylist refuses it by name. The runner maps the "
        "schema failure at a prohibited name to the prohibiting group's own code, so "
        "the group's code is the sole code and expect_only can hold. A prohibited name "
        "below depth zero can only arrive inside an open object, and there the "
        "denylist fires the group's code and LAYER_COLLAPSE_NESTED together."
    ),
    "S7-R6": (
        "Lineage requiredness is taken from lineage.required_by_subtype at subtype "
        "granularity, not from required_envelope_fields, where the two disagree "
        "(AUTHORIZE EXTEND and REVOKE, COLLECT PERMITTED and REQUIRES_EXTENSION, "
        "SYSTEM RETENTION_RENEWAL). The finer statement wins."
    ),
    "S7-R7": (
        "A required_parents entry whose fixture names a code_source rule emits that "
        "rule's code instead of LINEAGE_MISSING. PROBE_EVENT RUN_START without a "
        "COLLECT_EVENT PERMITTED parent therefore fires SUBJECT_NOT_AUTHORIZED, which "
        "is the D5 fixture's expectation and the model's own mapping."
    ),
}

#: RFC 4122 and RFC 9562, any version 1 to 8. The model says `format: uuid` and
#: does not pin a version; the pattern is what the stack checks, because
#: jsonschema's format checker is annotation-only without extra packages
#: (zmeta-spec schema/README.md records the same gotcha).
UUID_PATTERN = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$"
#: zmeta-event-1.1.0's utcDateTime pattern, not 1.0's, whose pattern is `Z$` alone
#: and accepts `garbageZ`. Recorded as a divergence against the 1.0 lane.
DATETIME_PATTERN = (
    r"^(19[7-9][0-9]|2[0-9]{3})-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])"
    r"T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](\.[0-9]+)?Z$"
)
DATE_PATTERN = r"^(19[7-9][0-9]|2[0-9]{3})-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$"

HUMAN = "<human identity>"


# ---------------------------------------------------------------------------
# loading
# ---------------------------------------------------------------------------


def _refuse(code: str, where: str, what: str, moves: str) -> None:
    print(f"REFUSED {code}\n  where: {where}\n  what:  {what}\n  moves: {moves}", file=sys.stderr)


def load() -> tuple[dict, dict]:
    try:
        model = yaml.safe_load(MODEL.read_text(encoding="utf-8"))
        registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        _refuse(
            "SOURCE_UNREADABLE",
            "spec/layer-model.yaml, ontology/selectors.yaml",
            f"{exc}",
            "fix the YAML, or run tools/validate_layer_model.py and tools/validate_ontology.py first",
        )
        sys.exit(2)
    if not isinstance(model, dict) or "event_types" not in model:
        _refuse("SOURCE_UNREADABLE", "spec/layer-model.yaml", "no event_types section", "restore the model")
        sys.exit(2)
    if not isinstance(registry, dict) or not registry.get("selectors"):
        _refuse("SOURCE_UNREADABLE", "ontology/selectors.yaml", "no selectors section", "restore the registry")
        sys.exit(2)
    return model, registry


def _as_list(value) -> list:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def generated_paths(model: dict) -> dict[str, Path]:
    """Token to path, read from pse.generates so the two cannot diverge."""
    out: dict[str, Path] = {}
    for entry in _as_list((model.get("pse") or {}).get("generates")):
        path = entry.get("path", "")
        if path.startswith("schema/"):
            out["schema"] = ROOT / path
        elif path.endswith("semantics.yaml"):
            out["semantics"] = ROOT / path
        elif path.endswith("lineage.yaml"):
            out["lineage"] = ROOT / path
        elif path.endswith("producer-authority.yaml"):
            out["producer-authority"] = ROOT / path
        elif path.endswith("violation-codes.yaml"):
            out["violation-codes"] = ROOT / path
    missing = [k for k in GENERATED_KEYS if k not in out]
    if missing:
        _refuse(
            "GENERATES_BLOCK_INCOMPLETE",
            "spec/layer-model.yaml pse.generates",
            f"no path for {', '.join(missing)}",
            "restore the five entries the layer model header names",
        )
        sys.exit(2)
    return out


# ---------------------------------------------------------------------------
# shape translation
# ---------------------------------------------------------------------------


class Ctx:
    def __init__(self, model: dict, registry: dict):
        self.model = model
        self.registry = registry
        self.type_names = list(model["event_types"].keys())
        self.codes = [c["code"] for c in (model["violation_codes"].get("codes") or [])]
        self.selector_keys = list(registry["selectors"].keys())


def _string_with_format(fmt: str | None) -> dict:
    out: dict = {"type": "string"}
    if fmt == "uuid":
        out["format"] = "uuid"
        out["pattern"] = UUID_PATTERN
    elif fmt == "date-time":
        out["format"] = "date-time"
        out["pattern"] = DATETIME_PATTERN
    elif fmt == "date":
        out["format"] = "date"
        out["pattern"] = DATE_PATTERN
    elif fmt:
        out["format"] = fmt
    return out


def shape(spec: dict, ctx: Ctx, path: str) -> dict:
    """One field shape from the model's notation to JSON Schema 2020-12."""
    if not isinstance(spec, dict):
        return {}
    t = spec.get("type")
    types = _as_list(t)
    nullable = "null" in types
    base_types = [x for x in types if x != "null"]
    out: dict = {}

    # registry-bound string: a closed enum of selector keys (S7-R4)
    if spec.get("registry"):
        enum_shape = {
            "type": "string",
            "enum": list(ctx.selector_keys),
            "$comment": f"registry: {spec['registry']}. Closed at the corpus boundary (S7-R4). "
            "An enum failure here is SELECTOR_TYPE_UNREGISTERED.",
        }
        return {"anyOf": [enum_shape, {"type": "null"}]} if nullable else enum_shape

    if spec.get("enum_from") == "event_types":
        return {"type": "string", "enum": list(ctx.type_names)}
    if spec.get("enum_from") == "violation_codes":
        return {"type": "string", "enum": list(ctx.codes)}

    # union with a closed string set: integer, or one of the named strings
    if spec.get("enum_when_string") is not None and len(base_types) == 2:
        non_string = [x for x in base_types if x != "string"]
        alts = [{"type": x} for x in non_string] + [
            {"type": "string", "enum": list(_as_list(spec["enum_when_string"]))}
        ]
        return {"oneOf": alts}

    if base_types == ["string"] and spec.get("format") in ("uuid", "date-time", "date"):
        s = _string_with_format(spec["format"])
        if "enum" in spec:
            s["enum"] = list(spec["enum"])
        return {"anyOf": [s, {"type": "null"}]} if nullable else s

    if base_types == ["object"]:
        obj: dict = {"type": "object"}
        fields = spec.get("fields")
        if isinstance(fields, dict) and fields:
            obj["properties"] = {k: shape(v, ctx, f"{path}.{k}") for k, v in fields.items()}
            obj["additionalProperties"] = False
            if spec.get("required"):
                obj["required"] = list(spec["required"])
        elif path.endswith(".member_seams"):
            # S7-R2
            obj["propertyNames"] = {"pattern": UUID_PATTERN}
            obj["additionalProperties"] = {
                "type": "array",
                "minItems": 1,
                "items": {"type": "string", "enum": ["h", "e", "n", "b", "i", "t", "g", "k"]},
            }
            obj["$comment"] = "S7-R2: member id to the rationale codes that hold for that member."
        else:
            obj["$comment"] = "S7-R3: no declared shape in the model; left open."
        return {"anyOf": [obj, {"type": "null"}]} if nullable else obj

    if base_types == ["array"]:
        arr: dict = {"type": "array"}
        if "min_items" in spec:
            arr["minItems"] = spec["min_items"]
        if "const" in spec:
            arr["const"] = list(spec["const"])
        items = spec.get("items")
        if isinstance(items, dict):
            arr["items"] = shape(items, ctx, f"{path}[]")
        elif path.endswith(".raw_span"):
            arr["$comment"] = "S7-R3: no item shape in the model; left open."
        return {"anyOf": [arr, {"type": "null"}]} if nullable else arr

    # scalars
    if len(base_types) == 1:
        out["type"] = base_types[0]
    elif base_types:
        out["type"] = list(base_types)
    if "enum" in spec:
        out["enum"] = list(spec["enum"])
    if "const" in spec:
        out["const"] = spec["const"]
    if "min_length" in spec:
        out["minLength"] = spec["min_length"]
    if "minimum" in spec:
        out["minimum"] = spec["minimum"]
    if spec.get("format") and "pattern" not in out:
        out["format"] = spec["format"]
    if nullable:
        return {"anyOf": [out, {"type": "null"}]} if out else {"type": "null"}
    return out


# ---------------------------------------------------------------------------
# per-type derivations
# ---------------------------------------------------------------------------


def subtypes_of(tdef: dict) -> list[str]:
    return list((tdef.get("subtypes") or {}).keys())


def discriminator_field(tdef: dict) -> str:
    """The payload field the subtype discriminator const lives in."""
    for sub in (tdef.get("subtypes") or {}).values():
        path = (sub.get("discriminator") or {}).get("path", "")
        if path.startswith("payload."):
            return path.split(".", 1)[1]
    return ""


def required_per_subtype(tdef: dict) -> dict[str, list[str]]:
    req = (tdef.get("payload") or {}).get("required") or {}
    return {s: list(req.get(s) or []) for s in subtypes_of(tdef)}


def _conditions(when) -> list[dict]:
    """The field conditions inside a `when`, flattened through all_of."""
    if isinstance(when, dict) and "all_of" in when:
        out = []
        for cond in _as_list(when["all_of"]):
            out.extend(_conditions(cond))
        return out
    if isinstance(when, dict) and "field" in when:
        return [when]
    return []


def _subtype_scope(when, subs: list[str]) -> list[str]:
    """The subtypes a `when` names, or every subtype when it names none."""
    if isinstance(when, dict) and "subtype" in when:
        return [s for s in subs if s in _as_list(when["subtype"])]
    if isinstance(when, dict) and "all_of" in when:
        scope = list(subs)
        for cond in _as_list(when["all_of"]):
            if isinstance(cond, dict) and "subtype" in cond:
                scope = [s for s in scope if s in _as_list(cond["subtype"])]
        return scope
    return list(subs)


def allowed_per_subtype(tdef: dict) -> dict[str, list[str]]:
    """S7-R1. Which declared fields each subtype may carry.

    A field is legal on a subtype when the model requires it there. A field no
    subtype requires and no rule names is a free optional, legal on every
    subtype of the type. A field named in a rule's condition is legal on the
    subtypes that rule is scoped to. A field a rule requires is legal where the
    rule can hold: for a field condition, on the subtypes where the condition's
    field is legal and, when the condition names a value and the field's enum
    is split by subtype, where that value is in the subtype's enum; for a
    runtime condition, on every subtype, because the model cannot bind a runtime
    fact to a subtype.
    """
    payload = tdef.get("payload") or {}
    fields_map = payload.get("fields") or {}
    fields = list(fields_map.keys())
    subs = subtypes_of(tdef)
    required = required_per_subtype(tdef)
    rules = list((payload.get("rules") or {}).values())

    required_somewhere = {f for s in subs for f in required[s]}
    named_by_rules: set[str] = set()
    for rule in rules:
        named_by_rules |= {f for f in _as_list(rule.get("requires")) if f in fields}
        named_by_rules |= {c["field"] for c in _conditions(rule.get("when")) if c.get("field") in fields}
    free = [f for f in fields if f not in required_somewhere and f not in named_by_rules]

    allowed = {s: list(required[s]) for s in subs}
    for s in subs:
        for f in free:
            if f not in allowed[s]:
                allowed[s].append(f)

    # a condition's field is legal where the rule is scoped
    for rule in rules:
        scope = _subtype_scope(rule.get("when"), subs)
        for cond in _conditions(rule.get("when")):
            f = cond.get("field")
            if f in fields:
                for s in scope:
                    if f not in allowed[s]:
                        allowed[s].append(f)

    # a required field is legal where the rule can hold
    changed = True
    while changed:
        changed = False
        for rule in rules:
            when = rule.get("when")
            requires = [f for f in _as_list(rule.get("requires")) if f in fields]
            if not requires:
                continue
            if when == "runtime":
                targets = list(subs)
            else:
                targets = _subtype_scope(when, subs)
                for cond in _conditions(when):
                    f = cond.get("field")
                    targets = [s for s in targets if f in allowed[s]]
                    spec = fields_map.get(f) or {}
                    by = spec.get("enum_by_subtype") if isinstance(spec, dict) else None
                    if isinstance(by, dict) and "equals" in cond:
                        targets = [s for s in targets if cond["equals"] in _as_list(by.get(s))]
            for s in targets:
                for f in requires:
                    if f not in allowed[s]:
                        allowed[s].append(f)
                        changed = True
    return allowed


def prohibited_groups(tdef: dict) -> list[dict]:
    out = []
    for g in _as_list((tdef.get("payload") or {}).get("prohibited")):
        if isinstance(g, dict):
            out.append({"names": list(_as_list(g.get("names"))), "code": g.get("code"), "why": g.get("why", "")})
    return out


def producer_sets(tdef: dict) -> dict[str, list[str]]:
    """by_subtype replaces, it does not augment (layer model producer_authority header)."""
    pa = tdef.get("producer_authority") or {}
    subs = subtypes_of(tdef)
    base = list(_as_list(pa.get("wildcards"))) + list(_as_list(pa.get("named")))
    if pa.get("human_identity_only"):
        base = base + [HUMAN]
    out = {s: list(base) for s in subs}
    for s, entry in (pa.get("by_subtype") or {}).items():
        if s not in out:
            continue
        entry = entry or {}
        producers = list(_as_list(entry.get("wildcards"))) + list(_as_list(entry.get("named")))
        if entry.get("human_identity_only", pa.get("human_identity_only", False)):
            producers.append(HUMAN)
        out[s] = producers
    return out


def per_subtype_map(value, subs: list[str]) -> dict:
    if isinstance(value, dict):
        return {s: value.get(s) for s in subs}
    return {s: value for s in subs}


def required_parent_codes(model: dict) -> dict[tuple[str, str], str]:
    """(type, subtype) -> code, for required_parents entries a fixture rebinds (S7-R7)."""
    out: dict[tuple[str, str], str] = {}
    for fx in ((model.get("violation_codes") or {}).get("fixtures") or {}).values():
        rule = fx.get("rule", "")
        parts = rule.split(".")
        if len(parts) == 5 and parts[0] == "event_types" and parts[2] == "lineage" and parts[3] == "required_parents":
            if fx.get("code_source", "").startswith("event_types."):
                out[(parts[1], parts[4])] = fx["code"]
    return out


# ---------------------------------------------------------------------------
# the schema
# ---------------------------------------------------------------------------


def build_schema(ctx: Ctx) -> dict:
    model = ctx.model
    env = model["envelope"]
    pse = model["pse"]

    props: dict = {}
    for name, spec in (env.get("fields") or {}).items():
        props[name] = shape(spec, ctx, f"envelope.{name}")
    # the envelope's event, source and lineage carry their own required lists
    for name in ("event", "source", "lineage"):
        spec = env["fields"][name]
        props[name]["required"] = list(spec.get("required") or [])
        props[name]["additionalProperties"] = False
    props["payload"] = {"type": "object", "$comment": "Shape bound per type and subtype under allOf."}
    for reserved in _as_list(env.get("reserved_refused")):
        props[reserved] = False

    defs: dict = {
        "uuid": {"type": "string", "format": "uuid", "pattern": UUID_PATTERN},
        "utcDateTime": {"type": "string", "format": "date-time", "pattern": DATETIME_PATTERN},
        "utcDate": {"type": "string", "format": "date", "pattern": DATE_PATTERN},
    }
    all_of: list = []

    for tname, tdef in model["event_types"].items():
        subs = subtypes_of(tdef)
        disc = discriminator_field(tdef)
        fields = (tdef.get("payload") or {}).get("fields") or {}
        required = required_per_subtype(tdef)
        allowed = allowed_per_subtype(tdef)
        lineage_req = per_subtype_map((tdef.get("lineage") or {}).get("required_by_subtype"), subs)
        env_required = list(_as_list(tdef.get("required_envelope_fields")))
        conf_code = (tdef.get("confidence") or {}).get("violation_code", "CONFIDENCE_PROHIBITED")

        # type arm: subtype enum, confidence refused with the type's own code
        all_of.append(
            {
                "$comment": f"{tname}: event_subtype is one of the type's subtypes; confidence refused ({conf_code}).",
                "if": {
                    "required": ["event"],
                    "properties": {"event": {"required": ["event_type"], "properties": {"event_type": {"const": tname}}}},
                },
                "then": {
                    "properties": {
                        "event": {"properties": {"event_subtype": {"enum": list(subs)}}},
                        "confidence": False,
                    }
                },
            }
        )

        for s in subs:
            def_name = f"payload_{tname}_{s}"
            properties: dict = {}
            for f in allowed[s]:
                spec = fields.get(f)
                if spec is None:
                    continue
                if isinstance(spec, dict) and spec.get("enum_by_subtype") is not None:
                    by = spec["enum_by_subtype"]
                    narrowed = dict(spec)
                    narrowed.pop("enum_by_subtype", None)
                    if s in by:
                        narrowed["enum"] = list(by[s])
                    properties[f] = shape(narrowed, ctx, f"{tname}.{s}.{f}")
                else:
                    properties[f] = shape(spec, ctx, f"{tname}.{s}.{f}")
                if f == disc:
                    properties[f] = {"type": "string", "const": s}
            defs[def_name] = {
                "type": "object",
                "$comment": f"{tname} {s}. Required per the model; optional per S7-R1. "
                f"Discriminator {disc} const {s}.",
                "required": list(required[s]),
                "additionalProperties": False,
                "properties": properties,
            }
            env_req_here = list(env_required)
            if lineage_req.get(s) and "lineage" not in env_req_here:
                env_req_here.append("lineage")
            if not lineage_req.get(s) and "lineage" in env_req_here:
                env_req_here.remove("lineage")
            all_of.append(
                {
                    "$comment": f"{tname} {s}: payload shape and envelope requiredness (S7-R6 for lineage).",
                    "if": {
                        "required": ["event"],
                        "properties": {
                            "event": {
                                "required": ["event_type", "event_subtype"],
                                "properties": {"event_type": {"const": tname}, "event_subtype": {"const": s}},
                            }
                        },
                    },
                    "then": {
                        "required": env_req_here,
                        "properties": {"payload": {"$ref": f"#/$defs/{def_name}"}},
                    },
                }
            )

    comment = (
        f"GENERATED by {TOOL} from spec/layer-model.yaml and ontology/selectors.yaml. "
        "Do not edit by hand; edit the model and regenerate. `--check` refuses drift. "
        "PSE is a private dialect derived from zmeta-event-1.0 and is not ZMeta "
        "(AGENTS.md section 1). Readings the generator took where the model is silent: "
        + " ".join(f"{k}: {v}" for k, v in READINGS.items())
    )

    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"urn:plainsight:{pse['version']}.schema.json",
        "title": f"PLAINSIGHT Semantic Envelope {pse['version']}",
        "description": (
            f"{pse['version']}, {pse['status']}, derived from {pse['derived_from']}. "
            "Every event is inside a case, carries no numeric confidence, and binds its "
            "payload shape to its event type and subtype."
        ),
        "$comment": comment,
        "type": "object",
        "required": list(env["required"]),
        "additionalProperties": bool(env.get("additional_properties", False)),
        "properties": props,
        "allOf": all_of,
        "$defs": defs,
    }


# ---------------------------------------------------------------------------
# the policies
# ---------------------------------------------------------------------------


def _header(title: str, source_keys: str) -> str:
    return (
        f"# {title}\n"
        f"#\n"
        f"# GENERATED by {TOOL} from spec/layer-model.yaml ({source_keys}).\n"
        f"# Do not edit by hand. Edit the model and regenerate; `{TOOL} --check`\n"
        f"# refuses any difference between this file and what the model generates.\n"
        f"# One top-level wrapper key, named after the file, as in zmeta-spec's policy\n"
        f"# files, so a loader unwraps it by name and a mistyped key fails closed.\n"
        f"#\n"
    )


def build_semantics(ctx: Ctx) -> dict:
    model = ctx.model
    env = model["envelope"]
    types: dict = {}
    for tname, tdef in model["event_types"].items():
        payload = tdef.get("payload") or {}
        machine, runtime, rendering = [], [], []
        for rname, rule in (payload.get("rules") or {}).items():
            entry = {
                "name": rname,
                "code": rule.get("code"),
                "when": rule.get("when"),
                "requires": list(_as_list(rule.get("requires"))),
                "cites": list(_as_list(rule.get("cites"))),
                "statement": " ".join(str(rule.get("statement", "")).split()),
            }
            if rule.get("open_reading"):
                entry["open_reading"] = rule["open_reading"]
            if rule.get("code") is None:
                entry.pop("code", None)
                rendering.append(entry)
            elif rule.get("when") == "runtime":
                entry["runtime_reason"] = " ".join(str(rule.get("runtime_reason", "")).split())
                runtime.append(entry)
            else:
                machine.append(entry)
        fields = payload.get("fields") or {}
        registry_fields = sorted(
            f for f, spec in fields.items() if isinstance(spec, dict) and spec.get("registry")
        )
        types[tname] = {
            "layer": tdef.get("layer"),
            "discriminator": f"payload.{discriminator_field(tdef)}",
            "subtypes": subtypes_of(tdef),
            "required": required_per_subtype(tdef),
            "allowed": allowed_per_subtype(tdef),
            "payload_must_not_contain": prohibited_groups(tdef),
            "confidence": {
                "rule": (tdef.get("confidence") or {}).get("rule"),
                "code": (tdef.get("confidence") or {}).get("violation_code"),
            },
            "rules": machine,
            "runtime_rules": runtime,
            "rendering_rules": rendering,
            "registry_fields": registry_fields,
            "retention": tdef.get("retention"),
            "egress": tdef.get("egress"),
        }
        if isinstance(payload.get("evidence_classes"), dict):
            types[tname]["evidence_classes"] = payload["evidence_classes"]

    layers = {}
    for lname, ldef in (model.get("layers") or {}).items():
        layers[lname] = {
            "purpose": ldef.get("purpose"),
            "may_carry": list(_as_list(ldef.get("may_carry"))),
            "never_carries": list(_as_list(ldef.get("never_carries"))),
        }

    # How a schema failure is named. The runner reads this table rather than
    # inventing one (generation contract, ambiguity 7).
    schema_error_map = [
        {"where": "/pse_version or /derived_from", "keyword": "const", "code": "VERSION_MISMATCH"},
        {"where": "/case_id", "keyword": "required or pattern", "code": "CASE_ID_MISSING"},
        {"where": "/event/event_type", "keyword": "enum", "code": "EVENT_TYPE_UNKNOWN"},
        {"where": "/event/event_subtype, or the payload discriminator", "keyword": "enum or const", "code": "EVENT_SUBTYPE_MISMATCH"},
        {"where": "/payload, a required field of the subtype", "keyword": "required", "code": "PAYLOAD_FIELD_MISSING"},
        {"where": "/payload, a name in the type's payload_must_not_contain", "keyword": "additionalProperties", "code": "the group's code (S7-R5)"},
        {"where": "/confidence", "keyword": "false", "code": "the type's confidence code"},
        {"where": "a registry-bound field", "keyword": "enum", "code": "SELECTOR_TYPE_UNREGISTERED"},
        {"where": "any other closed-set field", "keyword": "enum or const", "code": "ENUM_VALUE_INVALID"},
        {"where": "anywhere else", "keyword": "any", "code": "SCHEMA_INVALID"},
    ]

    return {
        "semantics": {
            "version": model["pse"]["version"],
            "generated_from": "spec/layer-model.yaml",
            "generated_by": TOOL,
            "payload_denylist": {
                "mode": (env.get("payload_denylist_recursion") or {}).get("mode", "recursive"),
                "nested_hit_code": (env.get("payload_denylist_recursion") or {}).get("nested_hit_code"),
                "residual": "A name denylist. A prohibited value re-keyed under a name the list does not "
                "carry passes the denylist; additionalProperties false at every level is what "
                "narrows that residual, and it is stated rather than claimed away.",
            },
            "envelope_violation_codes": list(_as_list(env.get("violation_codes"))),
            "schema_error_map": schema_error_map,
            "readings": dict(READINGS),
            "layers": layers,
            "event_types": types,
        }
    }


def build_lineage(ctx: Ctx) -> dict:
    model = ctx.model
    lin = model["lineage"]
    codes_override = required_parent_codes(model)
    required_by, allowed, required_parents, allowed_targets = {}, {}, {}, {}
    for tname, tdef in model["event_types"].items():
        subs = subtypes_of(tdef)
        tl = tdef.get("lineage") or {}
        required_by[tname] = per_subtype_map(tl.get("required_by_subtype"), subs)
        allowed[tname] = {p: list(_as_list(v)) for p, v in (tl.get("allowed_parents") or {}).items()}
        rp = {}
        for s, spec in (tl.get("required_parents") or {}).items():
            rp[s] = {
                "any_of": [
                    {"type": a.get("type"), "subtype": a.get("subtype")} for a in _as_list((spec or {}).get("any_of"))
                ],
                "code": codes_override.get((tname, s), "LINEAGE_MISSING"),
            }
        required_parents[tname] = rp
        if tl.get("allowed_targets"):
            allowed_targets[tname] = {s: list(_as_list(v)) for s, v in tl["allowed_targets"].items()}

    chain = {}
    for name, rule in (lin.get("chain_rules") or {}).items():
        chain[name] = {
            "code": rule.get("code"),
            "corpus": rule.get("corpus"),
            "fixture": rule.get("fixture"),
            "cites": list(_as_list(rule.get("cites"))),
            "statement": " ".join(str(rule.get("statement", "")).split()),
            "evaluated_by": "tools/validate_authorization.py at Step 8, over the composed chain",
        }

    return {
        "lineage": {
            "version": model["pse"]["version"],
            "generated_from": "spec/layer-model.yaml",
            "generated_by": TOOL,
            "divergence": (lin.get("policy_shape") or {}).get("divergence"),
            "modes": dict(lin.get("modes") or {}),
            "based_on": dict(lin.get("based_on") or {}),
            "violation_codes": list(_as_list(lin.get("violation_codes"))),
            "required_by_subtype": required_by,
            "allowed_parents": allowed,
            "required_parents": required_parents,
            "allowed_targets": allowed_targets,
            "chain_rules": chain,
            "matrix": {k: list(v) for k, v in (lin.get("matrix") or {}).items()},
            "required_summary": list(_as_list(lin.get("required_summary"))),
        }
    }


def build_producer(ctx: Ctx) -> dict:
    model = ctx.model
    pa = model["producer_authority"]
    effective: dict[str, list[str]] = {}
    producers: dict[str, dict] = {}
    human_only: list[str] = []
    for tname, tdef in model["event_types"].items():
        for s, plist in producer_sets(tdef).items():
            key = f"{tname}.{s}"
            effective[key] = list(plist)
            for p in plist:
                if p == HUMAN:
                    human_only.append(key)
                else:
                    producers.setdefault(p, {"allowed": []})["allowed"].append(key)
    return {
        "producer_authority": {
            "version": model["pse"]["version"],
            "generated_from": "spec/layer-model.yaml",
            "generated_by": TOOL,
            "require_match_for_event_types": list(_as_list(pa.get("require_match_for_event_types"))),
            "violation_code": pa.get("violation_code"),
            "fail_closed": True,
            "checked_before": "any semantic check",
            "human_identity_marker": HUMAN,
            "human_identity_source": "deployment configuration read by the runner; never a wildcard and never in a tracked file",
            "producers": producers,
            "human_identity_only": human_only,
            "effective": effective,
            "composition": "type-level wildcards, named and human_identity_only apply to every subtype "
            "unless by_subtype names it, in which case the by_subtype entry replaces them",
        }
    }


def build_codes(ctx: Ctx) -> dict:
    model = ctx.model
    vc = model["violation_codes"]
    env_codes = set(_as_list(model["envelope"].get("violation_codes")))
    lineage_codes = set(_as_list(model["lineage"].get("violation_codes")))
    egress_codes = set(_as_list(model["egress"].get("violation_codes")))
    producer_code = model["producer_authority"].get("violation_code")
    chain_codes = {r.get("code") for r in (model["lineage"].get("chain_rules") or {}).values()}
    rule_codes: dict[str, set[str]] = {}
    group_codes: set[str] = set()
    conf_codes: set[str] = set()
    for tdef in model["event_types"].values():
        for g in prohibited_groups(tdef):
            group_codes.add(g["code"])
        conf_codes.add((tdef.get("confidence") or {}).get("violation_code"))
        for rule in ((tdef.get("payload") or {}).get("rules") or {}).values():
            code = rule.get("code")
            if code:
                kind = "runtime" if rule.get("when") == "runtime" else "semantics"
                rule_codes.setdefault(code, set()).add(kind)

    entries = []
    for c in vc.get("codes") or []:
        code = c["code"]
        emitted: list[str] = []
        if code in env_codes:
            emitted.append("schema")
        if code in group_codes or code in conf_codes:
            emitted.append("denylist")
        if code in rule_codes:
            emitted.extend(sorted(rule_codes[code]))
        if code in lineage_codes:
            emitted.append("lineage")
        if code == producer_code:
            emitted.append("producer")
        if code in chain_codes:
            emitted.append("gate")
        if code in egress_codes:
            emitted.append("egress")
        entries.append(
            {
                "code": code,
                "severity": c.get("severity"),
                "since": c.get("since"),
                "emitted_by": sorted(set(emitted)) or ["runtime"],
                "fires_when": " ".join(str(c.get("fires_when", "")).split()),
            }
        )
    fixtures = {}
    for name, fx in (vc.get("fixtures") or {}).items():
        fixtures[name] = {k: fx[k] for k in ("code", "rule", "corpus", "expect_only", "code_source", "prohibited_name") if k in fx}
    return {
        "violation_codes": {
            "version": model["pse"]["version"],
            "generated_from": "spec/layer-model.yaml",
            "generated_by": TOOL,
            "append_only_once_shipped": True,
            "severities": list(_as_list(vc.get("severities"))),
            "emitted_by_vocabulary": {
                "schema": "the generated schema, named through semantics.schema_error_map",
                "denylist": "a payload_must_not_contain group or the type's confidence rule",
                "semantics": "a machine-readable payload rule with a field or subtype condition",
                "runtime": "a rule whose condition is a fact about the case; the runner, not the corpus validator",
                "lineage": "the lineage policy",
                "producer": "the producer-authority policy, checked before any semantic check",
                "gate": "tools/validate_authorization.py over the composed chain, Step 8",
                "egress": "the crossing check at the environment boundary",
            },
            "codes": entries,
            "fixtures": fixtures,
        }
    }


# ---------------------------------------------------------------------------
# rendering, writing, checking
# ---------------------------------------------------------------------------


def render_json(obj: dict) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def render_yaml(obj: dict, title: str, source_keys: str) -> str:
    body = yaml.safe_dump(obj, sort_keys=False, allow_unicode=True, width=100, default_flow_style=False)
    return _header(title, source_keys) + body


def render_all(model: dict, registry: dict) -> dict[str, str]:
    ctx = Ctx(model, registry)
    return {
        "schema": render_json(build_schema(ctx)),
        "semantics": render_yaml(
            build_semantics(ctx), "Semantics policy: layers, denylists, and payload rules",
            "layers, event_types.*.payload.prohibited, event_types.*.payload.rules",
        ),
        "lineage": render_yaml(
            build_lineage(ctx), "Lineage policy: typed parents at subtype granularity, D5 included",
            "lineage, event_types.*.lineage",
        ),
        "producer-authority": render_yaml(
            build_producer(ctx), "Producer authority: who may emit which type and subtype",
            "producer_authority, event_types.*.producer_authority",
        ),
        "violation-codes": render_yaml(
            build_codes(ctx), "Violation codes: the closed diagnostic vocabulary", "violation_codes"
        ),
    }


def write_all(rendered: dict[str, str], paths: dict[str, Path], quiet: bool) -> int:
    for key, text in rendered.items():
        path = paths[key]
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        if not quiet:
            print(f"wrote {path.relative_to(ROOT).as_posix()} ({len(text.splitlines())} lines)")
    return 0


def check_all(rendered: dict[str, str], paths: dict[str, Path], quiet: bool) -> int:
    stale = []
    for key, text in rendered.items():
        path = paths[key]
        rel = path.relative_to(ROOT).as_posix()
        if not path.is_file():
            stale.append((rel, "missing"))
            continue
        on_disk = path.read_text(encoding="utf-8")
        if on_disk != text:
            stale.append((rel, "differs from what the model generates"))
    if stale:
        for rel, why in stale:
            _refuse(
                "GENERATED_ARTIFACT_STALE",
                rel,
                f"{why}. The layer model or the registry changed, or the file was edited by hand",
                f"run `python {TOOL}` to regenerate, and never edit a generated file directly",
            )
        return 1
    if not quiet:
        print(f"generate_pse ok: {len(rendered)} generated artifacts current against spec/layer-model.yaml")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Generate the Step 7 artifacts from the layer model.")
    ap.add_argument("--check", action="store_true", help="regenerate in memory and refuse drift; write nothing")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    model, registry = load()
    paths = generated_paths(model)
    rendered = render_all(model, registry)
    if args.check:
        return check_all(rendered, paths, args.quiet)
    return write_all(rendered, paths, args.quiet)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
