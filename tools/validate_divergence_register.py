#!/usr/bin/env python3
"""The divergence register gate: where PSE departs from zmeta-event-1.0, read from the schemas.

`spec/divergence-register.yaml` is rank 3 and Class B. It is the documentation
condition of the license `AGENTS.md` section 1 quotes: the governed record of
every place `schema/pse-event-0.1.schema.json` departs from
`zmeta-event-1.0.schema.json`. A register written from prose goes stale within
two releases (`docs/THE-GAMEPLAN.md` section 2.1). This tool does not read the
prose. It derives the required entry list from a JSON-pointer diff of the two
schemas and refuses a register that disagrees with it, which is what Step 9
means by a register that is non-stale by construction.

The path model. Both schemas bind a payload's shape by event type and subtype
through if/then branches, so a raw diff of the two documents compares two
unrelated layouts and finds nothing in common. This tool evaluates each schema
once per branch, taking the branch's event type, its subtype and the payload
discriminator the branch pins as known, and records every place an event can
carry a value as an RFC 6901 pointer into the event. A payload pointer names
the branch it is read under, as in `/payload[SYSTEM_EVENT.SCHEMA_VIOLATION]/state`,
and the segment `*` is every item of an array or every value of an open map.
Envelope pointers are merged across branches. Their required-ness is compared
twice: merged as always, in some branches, or never; and per branch on the
type and subtype pairs both schemas bind, which today is SYSTEM_EVENT
SCHEMA_VIOLATION alone. The two schemas share one pair, so the per-branch
comparison is narrow, and it is not empty. Every branch's required-ness also
enters the diff fingerprint, so a change to which subtypes require an
envelope field moves the pin even where the merged value stays some. Six
attribute groups are compared at each pointer: type, with refusal by a false
schema; enum, with const; required-ness; format and pattern; bounds; and
closure. The first three are the gameplan's. The other three are compared so
that `identical:` means both schemas accept the same values at that pointer,
and so that the date-time pattern and the closed payloads the contract names in
section 13.2 come out of the diff rather than out of prose. A closed enum makes
format, pattern and bounds redundant at its pointer, so they are not compared
there. Each anyOf or oneOf alternative is read on its own: a name an
alternative requires is required in some cases rather than always, a child an
alternative declares is read under that alternative alone, and an alternative
that says more than a type is recorded with its enum, format and pattern,
bounds, closure and required names, so a change inside one alternative moves
the diff.

The six checks, each refused under its own code:

  1. DR_PATH_UNCOVERED. Every pointer the diff produces that is present in one
     schema only, or present in both with a differing attribute, is covered by
     exactly one entry, and every pointer the two schemas agree on is covered
     by a KEEP entry or listed once under `identical:`. An entry covers the
     pointers it names. A pointer present in one schema only also covers every
     pointer below it, all of which are on the same side; a pointer present in
     both covers itself alone, so a shared parent cannot carry a child through.
     Where two entries reach one pointer, the longer pointer covers it.
  2. DR_POINTER_STALE. Every pointer the register names resolves to a pointer
     the diff produces, no pointer is named twice, `identical:` names only
     pointers the schemas agree on, a policy-surface pointer resolves in its
     file, every compatibility-claim exemption matches a line in the tree, and
     the two pins hold: the sha256 of the upstream schema the diff reads, and
     the sha256 of the diff the register was last reviewed against. The second
     pin is the mechanism for the Schema row of `AGENTS.md` section 6: a
     change to either schema that moves the diff refuses until the register is
     reviewed in the same change.
  3. DR_DISPOSITION_INVALID. Every disposition is one of NEW, DROP, REPLACE,
     INVERT and KEEP; the register states exactly that set; each disposition
     fits the side of every pointer it names (DROP names pointers in
     zmeta-event-1.0 only, NEW pointers in pse-event-0.1 only, INVERT a pointer
     one schema refuses everywhere and the other accepts, REPLACE pointers on
     both sides or a pointer whose attributes differ, KEEP a pointer the two
     schemas agree on); and for every divergence `spec/layer-model.yaml`
     records, an entry citing it carries the disposition the model gives it.
  4. DR_ENTRY_INCOMPLETE. Every entry carries an id, a title, a disposition,
     pointers, a rationale, a mechanism_preserved, a test_ref and the contract
     sections it derives from, and no key outside those and the optional
     divergence, surface, test_gap and reading. Every cited contract section is
     a heading of `spec/pse-semantics-contract.md`, every reading is a
     question, and every divergence the contract's section 13.2 names is cited
     by an entry: DV-01 to DV-11 as `spec/layer-model.yaml` records them, and
     G-1 to G-3, the three that surfaced in generation, in the order 13.2
     lists them.
  5. DR_TEST_REF_UNRESOLVED. Every test_ref names exactly one fixture, by the
     fixture's `name`, in `conformance/must-pass.jsonl` or
     `conformance/must-fail.jsonl`, and the fixture's event carries a pointer
     the entry covers, or omits one the entry covers that pse-event-0.1
     requires in the fixture's own branch or, for an envelope pointer, in some
     branch. A ref that resolves and touches nothing its entry names passes
     only where the entry states a test_gap, because design gate 3 says a claim
     that was not scored says so in those words. A policy-surface entry names
     no schema pointer, so for it the ref is resolved and not matched.
  6. DR_COMPAT_CLAIM. The compatibility claim `AGENTS.md` section 1 forbids
     appears in no tracked file and in no untracked file git does not ignore,
     matched without regard to case, with the hyphen written as a
     hyphen-minus, a hyphen or a non-breaking hyphen. The string is
     assembled at run time so that this file does not carry it. A line the
     register exempts by file and sha256 is passed over, and the register
     exempts one: the Step 9 done-when sentence that states the rule, recorded
     there as a reading awaiting the operator.

One currency check sits beside the six and grades the rendering rather than the
register. DR_RENDER_STALE refuses when `spec/divergence-register.md` differs
from what `tools/render_divergence_register.py` renders from the register,
which is the check `tools/validate.py --kernel` runs for the generated schema.

`--self-test` breaks the register, the two derived tables, the corpora and the
tree in memory, at least once per check, and asserts each break is refused by
its own code and, where the break does not cascade, by that code alone. Two of
the breaks are negative controls for the done-when's first two sentences: an
entry deleted, and a test_ref pointed at a fixture that does not exist. Four
breaks edit the PSE schema itself and derive the diff again, so the path model
is tested as well as the checks: a lineage requirement moved on one subtype, a
lineage requirement added on the shared pair, an enum changed inside one
alternative, and a bound added to an alternative at a pointer listed under
`identical:`. One break builds a scratch git repository and asserts that the
compatibility-claim scan reads its tracked and untracked files and never a file
under an ignored directory. The self-test also refuses if any of the seven
codes is the expected code of no break.

The upstream schema is read from the path the register names, relative to the
repository root, which on the maintainer's machine is the sibling checkout
`../ZMeta/zmeta-spec`. `PSE_ZMETA_SCHEMA` overrides the path; a relative value
resolves against the repository root, not the shell's directory. CI clones the
pinned release beside the checkout so the same path resolves there.

Exit codes: 0 clean, 1 refused, 2 an input could not be read: the register, a
schema, the upstream schema, a corpus, the contract, the layer model, or the
tree through git.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print(
        "REFUSED DR_INPUT_UNREADABLE\n"
        "  where: tools/validate_divergence_register.py\n"
        "  what:  PyYAML is not installed, and the register is YAML\n"
        "  rule:  docs/THE-GAMEPLAN.md section 3.1 Step 9; a gate that cannot read an input refuses rather than passing on nothing\n"
        "  moves: pip install pyyaml",
        file=sys.stderr,
    )
    sys.exit(2)

try:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import gate_log
except Exception:  # telemetry must never be able to break a gate
    gate_log = None

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "spec" / "divergence-register.yaml"
RENDERED = ROOT / "spec" / "divergence-register.md"
PSE_SCHEMA = ROOT / "schema" / "pse-event-0.1.schema.json"
CONTRACT = ROOT / "spec" / "pse-semantics-contract.md"
MODEL = ROOT / "spec" / "layer-model.yaml"
CORPORA = ("conformance/must-pass.jsonl", "conformance/must-fail.jsonl")
REGISTER_REL = "spec/divergence-register.yaml"
GATE = "divergence-register"
UPSTREAM_ENV = "PSE_ZMETA_SCHEMA"

#: The closed disposition set. The register states the same five under
#: register.dispositions, and check 3 refuses a register that states another.
#: Step 9 names the first four; KEEP is this register's, and reading DR-R4 asks
#: the operator whether it stands.
DISPOSITIONS = ("NEW", "DROP", "REPLACE", "INVERT", "KEEP")

#: The three divergences the contract's section 13.2 says surfaced in
#: generation, in the order it lists them, with the label the register uses.
#: The contract gives them no id, so the label is the register's.
GENERATION_DIVERGENCES = {
    "G-1": "the date-time pattern taken from the 1.1.0 lane rather than 1.0's",
    "G-2": "additionalProperties false on every payload where ZMeta leaves its payloads open",
    "G-3": "the producer-authority policy keyed by producer with an effective table",
}

ENTRY_REQUIRED = (
    "id", "title", "disposition", "pointers", "rationale",
    "mechanism_preserved", "test_ref", "contract",
)
ENTRY_OPTIONAL = ("divergence", "surface", "test_gap", "reading")
ENTRY_ID_RE = re.compile(r"^DR-\d{2,3}$")
READING_ID_RE = re.compile(r"^DR-R\d+$")

#: AGENTS.md section 1. Assembled, so this file does not carry the claim.
CLAIM_RE = re.compile("zmeta" + "[-\u2010\u2011]" + "compatible", re.I)

CHECK_CODES = (
    "DR_PATH_UNCOVERED",
    "DR_POINTER_STALE",
    "DR_DISPOSITION_INVALID",
    "DR_ENTRY_INCOMPLETE",
    "DR_TEST_REF_UNRESOLVED",
    "DR_COMPAT_CLAIM",
)
RENDER_CODE = "DR_RENDER_STALE"

ZSIDE = "zmeta-event-1.0"
PSIDE = "pse-event-0.1"

RULES = {
    "DR_PATH_UNCOVERED": "docs/THE-GAMEPLAN.md section 3.1 Step 9, the first done-when sentence",
    "DR_POINTER_STALE": "docs/THE-GAMEPLAN.md section 3.1 Step 9, a register non-stale by construction; AGENTS.md section 6, the Schema row",
    "DR_DISPOSITION_INVALID": "the closed set in spec/divergence-register.yaml register.dispositions: the four docs/THE-GAMEPLAN.md section 3.1 Step 9 names, and KEEP, which reading DR-R4 puts to the operator; spec/layer-model.yaml divergences_from_zmeta",
    "DR_ENTRY_INCOMPLETE": "docs/THE-GAMEPLAN.md section 3.1 Step 9, the second done-when sentence; spec/pse-semantics-contract.md section 13.2",
    "DR_TEST_REF_UNRESOLVED": "docs/THE-GAMEPLAN.md section 3.1 Step 9, the second done-when sentence; CLAUDE.md design gate 3",
    "DR_COMPAT_CLAIM": "AGENTS.md section 1; docs/THE-GAMEPLAN.md section 3.1 Step 9, the third done-when sentence",
    "DR_RENDER_STALE": "docs/THE-GAMEPLAN.md section 2.1, the rendering is generated and never hand-edited",
    "DR_INPUT_UNREADABLE": "docs/THE-GAMEPLAN.md section 3.1 Step 9, a register derived from the diff of the two schemas; a gate that cannot read an input refuses rather than passing on nothing",
}


class Finding:
    __slots__ = ("code", "where", "what", "moves", "log_where")

    def __init__(self, code: str, where: str, what: str, moves: str, log_where: str = REGISTER_REL):
        self.code = code
        self.where = where
        self.what = what
        self.moves = moves
        self.log_where = log_where

    def render(self) -> str:
        return (
            f"REFUSED {self.code}\n"
            f"  where: {self.where}\n"
            f"  what:  {self.what}\n"
            f"  rule:  {RULES.get(self.code, '')}\n"
            f"  moves: {self.moves}"
        )


class Unreadable(Exception):
    def __init__(self, where: str, what: str, moves: str):
        super().__init__(what)
        self.where = where
        self.what = what
        self.moves = moves

    def render(self) -> str:
        return (
            "REFUSED DR_INPUT_UNREADABLE\n"
            f"  where: {self.where}\n"
            f"  what:  {self.what}\n"
            f"  rule:  {RULES['DR_INPUT_UNREADABLE']}\n"
            f"  moves: {self.moves}"
        )


# ---------------------------------------------------------------------------
# the path model: one table of pointers and attributes per schema
# ---------------------------------------------------------------------------

BOUND_KEYS = (
    "minLength", "maxLength", "minimum", "maximum", "exclusiveMinimum",
    "exclusiveMaximum", "minItems", "maxItems", "multipleOf",
    "minProperties", "maxProperties", "uniqueItems",
)
NOTE_KEYS = ("$comment", "description", "title")
MAX_DEPTH = 60


def _deref(root: dict, ref: str):
    if not isinstance(ref, str) or not ref.startswith("#"):
        raise ValueError(f"the schema carries a $ref this tool does not follow: {ref!r}")
    node = root
    for part in ref[1:].split("/")[1:]:
        part = part.replace("~1", "/").replace("~0", "~")
        if not isinstance(node, dict) or part not in node:
            raise ValueError(f"the schema's $ref {ref!r} resolves to nothing")
        node = node[part]
    return node


def _combine(results: list) -> bool | None:
    if any(r is False for r in results):
        return False
    if all(r is True for r in results):
        return True
    return None


def _known_present(loc: tuple, pins: dict) -> bool:
    return any(key[: len(loc)] == loc for key in pins)


def _evaluate(root: dict, node, loc: tuple, pins: dict, depth: int = 0) -> bool | None:
    """Whether the value at `loc` satisfies `node`: True, False, or None when unknown.

    Only the keywords an if-clause in either schema uses are evaluated, against
    the values the branch pins. Anything else is unknown, and an unknown
    condition makes its then-clause conditional rather than applied or dropped.
    """
    if depth > MAX_DEPTH:
        raise ValueError("the schema nests deeper than this tool follows")
    if node is True:
        return True
    if node is False:
        return False
    if not isinstance(node, dict):
        return None
    results = []
    for key, value in node.items():
        if key == "$ref":
            results.append(_evaluate(root, _deref(root, value), loc, pins, depth + 1))
        elif key == "required":
            for name in value or []:
                results.append(True if _known_present(loc + (name,), pins) else None)
        elif key == "properties":
            for name, sub in (value or {}).items():
                results.append(_evaluate(root, sub, loc + (name,), pins, depth + 1))
        elif key == "const":
            results.append((pins[loc] == value) if loc in pins else None)
        elif key == "enum":
            results.append((pins[loc] in value) if loc in pins else None)
        elif key in NOTE_KEYS:
            continue
        else:
            results.append(None)
    return _combine(results)


_ALTERNATIVE_IDS = itertools.count(1)


def _flatten(root: dict, node, loc: tuple, pins: dict, cond, out: list, depth: int = 0) -> None:
    """Every subschema that applies at `loc`, each with its condition.

    The condition is False for a subschema that always applies, True for one
    under an if-clause this tool cannot decide, and an ("alternative", n) tag
    for one that applies only when the nth anyOf or oneOf alternative is the
    one taken. A tag travels to the children an alternative declares, so a
    child named in two alternatives is read as one or the other and never as
    both at once.
    """
    if depth > MAX_DEPTH:
        raise ValueError("the schema nests deeper than this tool follows")
    if isinstance(node, bool):
        out.append((node, cond))
        return
    if not isinstance(node, dict):
        return
    if "$ref" in node:
        _flatten(root, _deref(root, node["$ref"]), loc, pins, cond, out, depth + 1)
    out.append((node, cond))
    for sub in node.get("allOf") or []:
        _flatten(root, sub, loc, pins, cond, out, depth + 1)
    if "if" in node:
        verdict = _evaluate(root, node["if"], loc, pins)
        then_cond = True if (cond is True or verdict is None) else cond
        if verdict is not False and "then" in node:
            _flatten(root, node["then"], loc, pins, then_cond, out, depth + 1)
        if verdict is not True and "else" in node:
            _flatten(root, node["else"], loc, pins, then_cond, out, depth + 1)
    for alt in list(node.get("anyOf") or []) + list(node.get("oneOf") or []):
        alt_cond = True if cond is True else ("alternative", next(_ALTERNATIVE_IDS))
        _flatten(root, alt, loc, pins, alt_cond, out, depth + 1)


def _types_of(node: dict) -> set | None:
    t = node.get("type")
    if t is None:
        return None
    return {t} if isinstance(t, str) else set(t)


def _enum_of(node: dict) -> set | None:
    if "const" in node:
        return {json.dumps(node["const"], sort_keys=True)}
    if "enum" in node:
        return {json.dumps(v, sort_keys=True) for v in node["enum"]}
    return None


def _json_type(value) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    return "object"


def _constraints(nodes: list) -> dict:
    """What a set of subschemas that all apply together says about one value:
    types and enum intersected, format and pattern, bounds and closure
    collected, and whether any of them is a false schema."""
    out: dict = {"false": False, "types": None, "enum": None, "lexical": set(), "bounds": set(), "closure": set(), "required": set()}
    for n in nodes:
        if n is False:
            out["false"] = True
        if not isinstance(n, dict):
            continue
        nt = _types_of(n)
        if nt is not None:
            out["types"] = nt if out["types"] is None else out["types"] & nt
        ne = _enum_of(n)
        if ne is not None:
            out["enum"] = ne if out["enum"] is None else out["enum"] & ne
        if "format" in n:
            out["lexical"].add(("format", n["format"]))
        if "pattern" in n:
            out["lexical"].add(("pattern", n["pattern"]))
        names = n.get("propertyNames")
        if isinstance(names, dict) and "pattern" in names:
            out["lexical"].add(("propertyNames", names["pattern"]))
        for key in BOUND_KEYS:
            if key in n:
                out["bounds"].add((key, json.dumps(n[key])))
        if "additionalProperties" in n:
            ap = n["additionalProperties"]
            out["closure"].add("closed" if ap is False else ("map" if isinstance(ap, dict) else "open"))
        out["required"] |= set(n.get("required") or [])
    return out


def _descriptor(k: dict) -> str:
    """One alternative's constraints as a sorted, comparable string."""
    d: dict = {"type": sorted(k["types"]) if k["types"] is not None else ["any"]}
    if k["enum"] is not None:
        d["enum"] = sorted(k["enum"])
    for key in ("lexical", "bounds"):
        if k[key]:
            d[key] = sorted([list(x) for x in k[key]])
    for key in ("closure", "required"):
        if k[key]:
            d[key] = sorted(k[key])
    return json.dumps(d, sort_keys=True, separators=(",", ":"))


def _describe(root: dict, applicable: list, loc: tuple, pins: dict):
    """Attributes at one location, and what applies at each of its children.

    Subschemas that always apply are intersected. Each anyOf or oneOf
    alternative is read on its own, its constraints intersected within it and
    the alternatives united, and every alternative that says more than a type
    is recorded under `alternatives`, so a change to an enum, a bound, a
    pattern or a closure inside one alternative changes the attributes and
    the diff fingerprint. Alternatives that say only a type are the type list
    a single subschema would write, and are recorded as that list alone.
    """
    refused = any(n is False for n, c in applicable if not c)
    children: dict = {}
    child_required: dict = {}
    items: list = []

    def structure(n: dict, c) -> None:
        for name, sub in (n.get("properties") or {}).items():
            _flatten(root, sub, loc + (name,), pins, c, children.setdefault(name, []))
        for name in n.get("required") or []:
            state = "some" if c else "always"
            if child_required.get(name) != "always":
                child_required[name] = state
        for deps in (n.get("dependentRequired") or {}).values():
            for name in deps:
                child_required.setdefault(name, "some")
        if isinstance(n.get("items"), (dict, bool)):
            _flatten(root, n["items"], loc + ("*",), pins, c, items)
        if isinstance(n.get("additionalProperties"), dict):
            _flatten(root, n["additionalProperties"], loc + ("*",), pins, c, items)

    base: list = []
    groups: dict = {}
    for n, c in applicable:
        if isinstance(n, dict):
            structure(n, c)
        if c is False:
            base.append(n)
        elif isinstance(c, tuple):
            groups.setdefault(c, []).append(n)

    k = _constraints(base)
    types, enum = k["types"], k["enum"]
    lexical, bounds, closure = k["lexical"], k["bounds"], k["closure"]
    descriptors: list = []
    if groups:
        live = [g for g in (_constraints(nodes) for nodes in groups.values()) if not g["false"]]
        alt_types: set | None = set()
        alt_enum: set | None = set()
        alt_closure: set = set()
        for g in live:
            if g["types"] is None or alt_types is None:
                alt_types = None
            else:
                alt_types |= g["types"]
            if g["enum"] is not None and alt_enum is not None:
                alt_enum |= g["enum"]
            elif g["types"] == {"null"} and alt_enum is not None:
                alt_enum.add("null")
            else:
                alt_enum = None
            alt_closure |= g["closure"]
            descriptors.append(_descriptor(g))
        if live and alt_types is not None:
            types = alt_types if types is None else types & alt_types
        if live and alt_enum:
            enum = alt_enum if enum is None else enum & alt_enum
        if not closure:
            closure = alt_closure
        if all(json.loads(d).keys() == {"type"} for d in descriptors):
            descriptors = []

    if refused:
        attrs = {"type": ["refused"]}
    else:
        if types is None and enum is not None:
            types = {_json_type(json.loads(v)) for v in enum}
        type_list = sorted(types) if types is not None else ["any"]
        attrs = {"type": type_list}
        if enum is not None:
            attrs["enum"] = sorted(enum)
        else:
            if lexical:
                attrs["lexical"] = sorted([list(x) for x in lexical])
            if bounds:
                attrs["bounds"] = sorted([list(x) for x in bounds])
        if "object" in type_list:
            attrs["closure"] = sorted(closure) if closure else ["open"]
        if descriptors:
            attrs["alternatives"] = sorted(descriptors)
    return attrs, children, child_required, items


def _walk(root: dict, applicable: list, loc: tuple, pins: dict, required: str, out: dict, pointer: str) -> None:
    if len(loc) > MAX_DEPTH:
        raise ValueError("the schema nests deeper than this tool follows")
    attrs, children, child_required, items = _describe(root, applicable, loc, pins)
    attrs["required"] = required
    out[pointer] = attrs
    if attrs["type"] == ["refused"]:
        return
    for name in sorted(children):
        segment = name.replace("~", "~0").replace("/", "~1")
        _walk(root, children[name], loc + (name,), pins, child_required.get(name, "never"), out, pointer + "/" + segment)
    if items:
        _walk(root, items, loc + ("*",), pins, "item", out, pointer + "/*")


def _subschemas_at(root: dict, top: list, name: str, loc: tuple, pins: dict) -> list:
    out: list = []
    for n, c in top:
        if isinstance(n, dict) and name in (n.get("properties") or {}):
            _flatten(root, n["properties"][name], loc, pins, c, out)
    return out


def branches(root: dict) -> list[tuple[str, str]]:
    """Every (event type, subtype) pair the schema binds, read from the schema."""
    top: list = []
    _flatten(root, root, (), {}, False, top)
    event = _subschemas_at(root, top, "event", ("event",), {})
    types: list = []
    for n, c in event:
        if c or not isinstance(n, dict) or "event_type" not in (n.get("properties") or {}):
            continue
        flat: list = []
        _flatten(root, n["properties"]["event_type"], ("event", "event_type"), {}, False, flat)
        for sn, _ in flat:
            if isinstance(sn, dict) and "enum" in sn:
                types = list(sn["enum"])
    if not types:
        raise ValueError("the schema declares no closed event_type enum, so it has no branches to evaluate")
    out = []
    for t in types:
        pins = {("event", "event_type"): t}
        top = []
        _flatten(root, root, (), pins, False, top)
        subtypes: set = set()
        for n, c in _subschemas_at(root, top, "event", ("event",), pins):
            if c or not isinstance(n, dict):
                continue
            st = (n.get("properties") or {}).get("event_subtype")
            if isinstance(st, dict):
                subtypes |= set(st.get("enum") or [])
                if "const" in st:
                    subtypes.add(st["const"])
        if not subtypes:
            raise ValueError(f"event type {t} binds no subtype, so its payload cannot be read")
        out.extend((t, s) for s in sorted(subtypes))
    return out


def _branch_table(root: dict, t: str, s: str) -> dict:
    pins = {("event", "event_type"): t, ("event", "event_subtype"): s}
    # The payload discriminator is pinned by the branch, in ZMeta through
    # subtypePayloadMatch and in PSE by a const on each payload definition, so
    # the payload's own if-clauses keyed on it can be decided.
    for _ in range(4):
        top: list = []
        _flatten(root, root, (), pins, False, top)
        added = False
        for n, c in _subschemas_at(root, top, "payload", ("payload",), pins):
            if c or not isinstance(n, dict):
                continue
            for name, sub in (n.get("properties") or {}).items():
                flat: list = []
                _flatten(root, sub, ("payload", name), pins, False, flat)
                for sn, sc in flat:
                    key = ("payload", name)
                    if isinstance(sn, dict) and "const" in sn and not sc and key not in pins:
                        pins[key] = sn["const"]
                        added = True
        if not added:
            break
    top = []
    _flatten(root, root, (), pins, False, top)
    out: dict = {}
    _walk(root, top, (), pins, "always", out, "")
    return out


#: The key under which an envelope pointer keeps its required-ness per branch.
BY_BRANCH = "required_by_branch"


def derive_table(root: dict) -> dict:
    """Every pointer an event can carry a value at, with its attributes.

    An envelope pointer's attributes are merged across the branches, and its
    required-ness is kept twice: merged as always, some or never, and per
    branch under `required_by_branch`, with never for a branch that does not
    carry the pointer. `classify` compares the per-branch values on the pairs
    both schemas bind, and `fingerprint` hashes all of them, so a change to
    which subtypes require an envelope field moves the pin even where the
    merged value stays some.
    """
    found = branches(root)
    envelope: dict = {}
    by_branch: dict = {}
    payload: dict = {}
    for t, s in found:
        for pointer, attrs in _branch_table(root, t, s).items():
            if pointer == "":
                continue
            if pointer == "/payload" or pointer.startswith("/payload/"):
                payload[f"/payload[{t}.{s}]{pointer[len('/payload'):]}"] = attrs
                if pointer != "/payload":
                    continue
            envelope.setdefault(pointer, []).append(attrs)
            by_branch.setdefault(pointer, {})[f"{t}.{s}"] = attrs["required"]
    merged: dict = {}
    for pointer, per_branch in envelope.items():
        types: set = set()
        enums: set = set()
        open_enum = False
        lexical: set = set()
        bounds: set = set()
        closure: set = set()
        alternatives: set = set()
        required = {a["required"] for a in per_branch}
        if len(per_branch) < len(found):
            required.add("never")
        for a in per_branch:
            types |= set(a["type"])
            if "enum" in a:
                enums |= set(a["enum"])
            else:
                open_enum = True
            lexical |= {tuple(x) for x in a.get("lexical", [])}
            bounds |= {tuple(x) for x in a.get("bounds", [])}
            closure |= set(a.get("closure", []))
            alternatives |= set(a.get("alternatives", []))
        attrs: dict = {"type": sorted(types)}
        if not open_enum:
            attrs["enum"] = sorted(enums)
        else:
            if lexical:
                attrs["lexical"] = sorted([list(x) for x in lexical])
            if bounds:
                attrs["bounds"] = sorted([list(x) for x in bounds])
        if closure:
            attrs["closure"] = sorted(closure)
        if alternatives:
            attrs["alternatives"] = sorted(alternatives)
        attrs["required"] = required.pop() if len(required) == 1 else "some"
        attrs[BY_BRANCH] = {f"{t}.{s}": by_branch[pointer].get(f"{t}.{s}", "never") for t, s in found}
        merged[pointer] = attrs
    merged.update(payload)
    return dict(sorted(merged.items()))


def fingerprint(zmeta: dict, pse: dict) -> str:
    blob = json.dumps({"zmeta": zmeta, "pse": pse}, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def comparable(zattrs: dict, pattrs: dict) -> tuple[dict, dict]:
    """The two sides' attributes as the diff compares them: an envelope
    pointer's per-branch required-ness is compared on the branches both
    schemas bind and on no other, since a branch one schema lacks has nothing
    to be compared with."""
    zb, pb = zattrs.get(BY_BRANCH), pattrs.get(BY_BRANCH)
    shared = sorted(set(zb) & set(pb)) if isinstance(zb, dict) and isinstance(pb, dict) else []
    out = []
    for attrs, per in ((zattrs, zb), (pattrs, pb)):
        a = {k: v for k, v in attrs.items() if k != BY_BRANCH}
        if shared:
            a["required_on_shared_branches"] = {b: per[b] for b in shared}
        out.append(a)
    return out[0], out[1]


def classify(zmeta: dict, pse: dict) -> dict:
    """Each pointer's class: in one schema only, in both and differing, or identical."""
    out = {}
    for pointer in set(zmeta) | set(pse):
        if pointer not in pse:
            out[pointer] = "zmeta"
        elif pointer not in zmeta:
            out[pointer] = "pse"
        else:
            za, pa = comparable(zmeta[pointer], pse[pointer])
            out[pointer] = "differs" if za != pa else "identical"
    return out


def is_inversion(zattrs: dict, pattrs: dict) -> bool:
    """One schema refuses the pointer in every branch and the other accepts a value there."""
    zt, pt = zattrs.get("type", []), pattrs.get("type", [])
    zr, pr = zt == ["refused"], pt == ["refused"]
    return (pr and any(t != "refused" for t in zt)) or (zr and any(t != "refused" for t in pt))


# ---------------------------------------------------------------------------
# pointers
# ---------------------------------------------------------------------------

QUALIFIER_RE = re.compile(r"^payload\[([A-Z0-9_]+|\*)\.([A-Z0-9_]+|\*)\]$")


def segments(pointer: str) -> tuple:
    return tuple(pointer[1:].split("/")) if pointer.startswith("/") else ()


def expand(pointer: str, universe: set, segs: dict) -> list:
    """The pointers of the diff a register pointer names. `*` is a wildcard
    only inside a payload branch qualifier; anywhere else it is the literal
    items segment the diff writes."""
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        return []
    parts = segments(pointer)
    match = QUALIFIER_RE.match(parts[0]) if parts else None
    if not match or "*" not in match.groups():
        return [pointer] if pointer in universe else []
    want_t, want_s = match.groups()
    out = []
    for candidate in universe:
        cs = segs[candidate]
        if len(cs) != len(parts) or cs[1:] != parts[1:]:
            continue
        cm = QUALIFIER_RE.match(cs[0])
        if not cm:
            continue
        t, s = cm.groups()
        if want_t in ("*", t) and want_s in ("*", s):
            out.append(candidate)
    return sorted(out)


def _json_pointer(doc, pointer: str):
    """Resolve an RFC 6901 pointer in a parsed document, or raise KeyError."""
    if pointer == "":
        return doc
    if not pointer.startswith("/"):
        raise KeyError(pointer)
    node = doc
    for part in pointer[1:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        if isinstance(node, dict) and part in node:
            node = node[part]
        elif isinstance(node, list) and part.isdigit() and int(part) < len(node):
            node = node[int(part)]
        else:
            raise KeyError(pointer)
    return node


def _as_list(value) -> list:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _entry_label(entry, index: int) -> str:
    if isinstance(entry, dict) and isinstance(entry.get("id"), str) and entry.get("id"):
        return entry["id"]
    return f"entries[{index}]"


def resolve(ctx: dict) -> dict:
    """Expand every register pointer against the diff and work out coverage.

    Returns the classes, the concrete pointers each entry names, every
    pointer's owners, and the one owner that covers each pointer of the diff.
    An owner is an entry's index, or the string "identical".
    """
    zmeta, pse = ctx["zmeta"], ctx["pse"]
    classes = classify(zmeta, pse)
    universe = set(classes)
    segs = {p: segments(p) for p in universe}
    register = ctx["register"]
    entries = register.get("entries") if isinstance(register.get("entries"), list) else []
    named: dict = {}
    unresolved: list = []
    owners: dict = {}
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict) or entry.get("surface"):
            continue
        concrete: list = []
        for pointer in _as_list(entry.get("pointers")):
            hits = expand(pointer, universe, segs)
            if not hits:
                unresolved.append((i, pointer))
            concrete.extend(hits)
        named[i] = concrete
        for c in concrete:
            owners.setdefault(c, []).append(i)
    identical = register.get("identical") if isinstance(register.get("identical"), list) else []
    for pointer in identical:
        if isinstance(pointer, str) and pointer in universe:
            owners.setdefault(pointer, []).append("identical")
    by_first: dict = {}
    for p in universe:
        by_first.setdefault(segs[p][:1], []).append(p)
    best: dict = {}
    for c, owner_list in owners.items():
        for owner in owner_list:
            if owner == "identical" and classes.get(c) != "identical":
                continue
            reach = [c]
            if classes[c] in ("zmeta", "pse"):
                n = len(segs[c])
                reach = [p for p in by_first.get(segs[c][:1], []) if segs[p][:n] == segs[c]]
            depth = len(segs[c])
            for p in reach:
                if p not in best or best[p][0] < depth:
                    best[p] = (depth, owner)
    cover = {p: owner for p, (_, owner) in best.items()}
    return {
        "classes": classes,
        "universe": universe,
        "segs": segs,
        "named": named,
        "unresolved": unresolved,
        "owners": owners,
        "cover": cover,
        "entries": entries,
    }


# ---------------------------------------------------------------------------
# corpora and the tree
# ---------------------------------------------------------------------------


def instance_pointers(event: dict) -> set:
    """Every pointer a fixture's event carries a value at, in the diff's form."""
    out: set = set()
    if not isinstance(event, dict):
        return out
    meta = event.get("event") if isinstance(event.get("event"), dict) else {}
    branch = f"/payload[{meta.get('event_type')}.{meta.get('event_subtype')}]"

    def walk(node, prefix: str) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                pointer = prefix + "/" + str(key).replace("~", "~0").replace("/", "~1")
                out.add(pointer)
                walk(value, pointer)
        elif isinstance(node, list):
            for value in node:
                out.add(prefix + "/*")
                walk(value, prefix + "/*")

    for key, value in event.items():
        if key == "payload":
            out.add("/payload")
            out.add(branch)
            walk(value, branch)
        else:
            pointer = "/" + str(key).replace("~", "~0").replace("/", "~1")
            out.add(pointer)
            walk(value, pointer)
    return out


def touches(event: dict, covered: set, pse: dict) -> bool:
    """Whether a fixture's event exercises what an entry covers: it carries a
    covered pointer, or it omits a covered pointer pse-event-0.1 requires in
    its own branch or, for an envelope pointer, in some branch."""
    carried = instance_pointers(event)
    if carried & covered:
        return True
    meta = event.get("event") if isinstance(event.get("event"), dict) else {}
    branch = f"payload[{meta.get('event_type')}.{meta.get('event_subtype')}]"
    for c in covered:
        attrs = pse.get(c)
        if not attrs or attrs.get("required") not in ("always", "some") or c in carried:
            continue
        first = segments(c)[0] if segments(c) else ""
        if not first.startswith("payload[") or first == branch:
            return True
    return False


def _decode(data: bytes) -> str:
    for bom, codec in ((b"\xff\xfe", "utf-16-le"), (b"\xfe\xff", "utf-16-be")):
        if data.startswith(bom):
            try:
                return data[len(bom):].decode(codec)
            except UnicodeDecodeError:
                break
    return data.decode("utf-8", errors="replace").lstrip("\ufeff")


def tree_files(root: Path = ROOT) -> list:
    """Every tracked file, and every untracked file git does not ignore, with its text."""
    names: list = []
    for args in (["ls-files", "-z"], ["ls-files", "-z", "--others", "--exclude-standard"]):
        proc = subprocess.run(["git"] + args, cwd=root, capture_output=True)
        if proc.returncode != 0:
            raise Unreadable(
                "git",
                f"git {' '.join(args)} failed, so the compatibility-claim scan has no file set",
                "run the gate inside the repository's git working tree",
            )
        names.extend(n for n in proc.stdout.decode("utf-8", errors="replace").split("\0") if n.strip())
    out = []
    for name in sorted(set(names)):
        path = root / name
        if not path.is_file():
            continue
        try:
            out.append((name, _decode(path.read_bytes())))
        except OSError:
            continue
    return out


def line_sha256(line: str) -> str:
    return hashlib.sha256(line.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# loading
# ---------------------------------------------------------------------------


def _read_text(path: Path, what: str, moves: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise Unreadable(_rel(path), f"{what} could not be read: {exc.strerror or exc}", moves) from None


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def upstream_path(register: dict) -> Path:
    override = os.environ.get(UPSTREAM_ENV)
    if override:
        p = Path(override)
        return p if p.is_absolute() else ROOT / p
    header = register.get("register") if isinstance(register.get("register"), dict) else {}
    upstream = header.get("upstream") if isinstance(header.get("upstream"), dict) else {}
    rel = upstream.get("path")
    if not isinstance(rel, str) or not rel:
        raise Unreadable(
            f"{REGISTER_REL} register.upstream.path",
            "the register names no upstream schema, so there is nothing to diff against",
            "restore register.upstream.path to the zmeta-event-1.0 schema's path relative to the repository root",
        )
    return ROOT / rel


def load_context() -> dict:
    text = _read_text(REGISTER, "the register", "write spec/divergence-register.yaml, or move the divergence-register gate to PENDING in tools/validate_conformance.py")
    try:
        register = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise Unreadable(REGISTER_REL, f"the register is not parseable YAML: {exc}", "fix the syntax") from None
    if not isinstance(register, dict) or not isinstance(register.get("register"), dict) or not isinstance(register.get("entries"), list):
        raise Unreadable(
            REGISTER_REL,
            "the register does not parse to a mapping with a register header and an entries list",
            "restore the top-level keys register, entries and identical",
        )

    up = upstream_path(register)
    try:
        up_bytes = up.read_bytes()
    except OSError:
        if os.environ.get(UPSTREAM_ENV):
            raise Unreadable(
                up.as_posix(),
                f"{UPSTREAM_ENV} is set and names this path, which is not there, so no diff can be "
                "derived and no check below it can run. A relative value resolves against the "
                "repository root, not the shell's directory",
                f"correct {UPSTREAM_ENV} to the path of a copy of zmeta-event-1.0.schema.json whose "
                f"sha256 matches register.upstream.sha256; or unset {UPSTREAM_ENV} so the gate reads "
                "register.upstream.path",
            ) from None
        raise Unreadable(
            up.as_posix(),
            "the upstream schema the register diffs against is not there, so no diff can be derived "
            "and no check below it can run",
            "check out zmeta-spec beside this repository as ../ZMeta/zmeta-spec (CI clones the pinned "
            f"release tag); or set {UPSTREAM_ENV} to a copy of zmeta-event-1.0.schema.json whose sha256 "
            "matches register.upstream.sha256",
        ) from None
    try:
        upstream = json.loads(up_bytes.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Unreadable(up.as_posix(), f"the upstream schema is not JSON: {exc}", "restore the file from the pinned release") from None
    pse_text = _read_text(PSE_SCHEMA, "the PSE schema", "run python tools/generate_pse.py, which is its only writer")
    try:
        pse = json.loads(pse_text)
    except json.JSONDecodeError as exc:
        raise Unreadable(_rel(PSE_SCHEMA), f"the PSE schema is not JSON: {exc}", "run python tools/generate_pse.py") from None
    try:
        zmeta_table = derive_table(upstream)
        zmeta_branches = branches(upstream)
    except (ValueError, KeyError, TypeError, RecursionError) as exc:
        raise Unreadable(up.as_posix(), f"the upstream schema could not be evaluated: {exc}", "restore the file from the pinned release") from None
    try:
        pse_table = derive_table(pse)
        pse_branches = branches(pse)
    except (ValueError, KeyError, TypeError, RecursionError) as exc:
        raise Unreadable(_rel(PSE_SCHEMA), f"the PSE schema could not be evaluated: {exc}", "run python tools/generate_pse.py") from None

    corpora: dict = {}
    for rel in CORPORA:
        lines = []
        body = _read_text(ROOT / rel, "a conformance corpus", "run python tools/build_corpus.py, which is its only writer")
        for n, line in enumerate(body.splitlines(), 1):
            if not line.strip():
                continue
            try:
                lines.append((n, json.loads(line)))
            except json.JSONDecodeError as exc:
                raise Unreadable(f"{rel}:{n}", f"the line is not JSON: {exc}", "run python tools/build_corpus.py") from None
        corpora[rel] = lines

    contract_text = _read_text(CONTRACT, "the semantics contract", "restore spec/pse-semantics-contract.md")
    sections = set(re.findall(r"^#{2,3} (\d+(?:\.\d+)?)\.? ", contract_text, re.M))

    model_text = _read_text(MODEL, "the layer model", "restore spec/layer-model.yaml")
    try:
        model = yaml.safe_load(model_text)
    except yaml.YAMLError as exc:
        raise Unreadable(_rel(MODEL), f"the layer model is not parseable YAML: {exc}", "fix the syntax") from None
    divergences = {}
    for dv in _as_list((model or {}).get("divergences_from_zmeta")):
        if isinstance(dv, dict) and dv.get("id"):
            divergences[str(dv["id"])] = dv.get("disposition")

    surfaces: dict = {}
    for entry in register["entries"]:
        if isinstance(entry, dict) and isinstance(entry.get("surface"), str):
            rel = entry["surface"]
            path = ROOT / rel
            doc = None
            if path.is_file() and ROOT in path.resolve().parents:
                try:
                    raw = path.read_text(encoding="utf-8")
                    doc = json.loads(raw) if rel.endswith(".json") else yaml.safe_load(raw)
                except (OSError, ValueError, yaml.YAMLError):
                    doc = None
            surfaces[rel] = doc

    rendered = RENDERED.read_text(encoding="utf-8") if RENDERED.is_file() else None

    return {
        "register": register,
        "upstream_path": up,
        "upstream_sha256": hashlib.sha256(up_bytes.replace(b"\r\n", b"\n")).hexdigest(),
        "zmeta": zmeta_table,
        "pse": pse_table,
        "pse_root": pse,
        "zmeta_branches": zmeta_branches,
        "pse_branches": pse_branches,
        "corpora": corpora,
        "sections": sections,
        "divergences": divergences,
        "surfaces": surfaces,
        "files": tree_files(),
        "rendered": rendered,
    }


# ---------------------------------------------------------------------------
# the checks
# ---------------------------------------------------------------------------


def _side_name(cls: str) -> str:
    return {
        "zmeta": f"in {ZSIDE} only",
        "pse": f"in {PSIDE} only",
        "differs": "in both, differing",
        "identical": "in both, identical",
    }.get(cls, "in neither schema")


def check(ctx: dict) -> list[Finding]:
    f: list[Finding] = []
    register = ctx["register"]
    header = register.get("register") if isinstance(register.get("register"), dict) else {}
    zmeta, pse = ctx["zmeta"], ctx["pse"]
    r = resolve(ctx)
    classes, universe, segs = r["classes"], r["universe"], r["segs"]
    entries = r["entries"]
    identical = register.get("identical") if isinstance(register.get("identical"), list) else []

    # 1. DR_PATH_UNCOVERED, folded so a missing branch is one finding rather
    # than one per pointer below it.
    uncovered = sorted(p for p in universe if p not in r["cover"])
    unset = set(uncovered)
    for p in uncovered:
        parent = "/" + "/".join(segs[p][:-1]) if len(segs[p]) > 1 else None
        if parent in unset and classes.get(parent) in ("zmeta", "pse"):
            continue
        below = sum(1 for q in uncovered if q != p and segs[q][: len(segs[p])] == segs[p])
        extra = f", and {below} pointer(s) below it" if below else ""
        if classes[p] == "identical":
            f.append(Finding(
                "DR_PATH_UNCOVERED", f"{p} ({_side_name(classes[p])})",
                "the two schemas agree at this pointer and the register neither lists it under "
                "identical: nor covers it with a KEEP entry, so a reader cannot tell a pointer that "
                "was compared from one nobody looked at",
                "list the pointer under identical:; or cover it with a KEEP entry that says what the "
                "agreement hides",
            ))
        else:
            f.append(Finding(
                "DR_PATH_UNCOVERED", f"{p} ({_side_name(classes[p])}{extra})",
                "the diff of the two schemas produces this pointer and no register entry covers it, "
                "so the register is silent on a place PSE departs from zmeta-event-1.0",
                "add an entry naming the pointer, with its disposition, rationale, "
                "mechanism_preserved, test_ref and contract sections; or add the pointer to the entry "
                "whose divergence it belongs to; or, for a pointer in one schema only, name its parent "
                "in that entry",
            ))

    # 2. DR_POINTER_STALE.
    for i, pointer in r["unresolved"]:
        label = _entry_label(entries[i], i)
        f.append(Finding(
            "DR_POINTER_STALE", f"{label} pointers: {pointer}",
            "the pointer resolves to nothing the diff produces, so the entry describes a place that "
            "is not in either schema",
            "correct the pointer to the form the diff writes, /payload[TYPE.SUBTYPE]/field for a "
            "payload; or remove it if the schema no longer carries it",
            log_where=f"{REGISTER_REL} :: {label}",
        ))
    for c, owner_list in sorted(r["owners"].items()):
        if len(owner_list) > 1:
            names = ", ".join("identical:" if o == "identical" else _entry_label(entries[o], o) for o in owner_list)
            f.append(Finding(
                "DR_POINTER_STALE", f"{c} (named by {names})",
                "the pointer is named twice, so two dispositions claim one place and a reader cannot "
                "tell which holds",
                "keep the pointer in one entry, or in identical: alone",
            ))
    for pointer in identical:
        if not isinstance(pointer, str) or pointer not in universe:
            f.append(Finding(
                "DR_POINTER_STALE", f"identical: {pointer}",
                "the pointer resolves to nothing the diff produces",
                "remove it, or correct it to the form the diff writes",
            ))
        elif classes[pointer] != "identical":
            f.append(Finding(
                "DR_POINTER_STALE", f"identical: {pointer} ({_side_name(classes[pointer])})",
                "identical: lists a pointer the two schemas do not agree on, so the list claims an "
                "agreement the diff refutes",
                "move the pointer into an entry with the disposition the diff supports",
            ))
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict) or not entry.get("surface"):
            continue
        label = _entry_label(entry, i)
        surface = entry.get("surface")
        doc = ctx["surfaces"].get(surface)
        if doc is None:
            f.append(Finding(
                "DR_POINTER_STALE", f"{label} surface: {surface}",
                "the policy surface the entry names is not a readable file in this repository",
                "correct the surface to the repository-relative path of the policy file",
                log_where=f"{REGISTER_REL} :: {label}",
            ))
            continue
        for pointer in _as_list(entry.get("pointers")):
            try:
                _json_pointer(doc, pointer)
            except (KeyError, TypeError, AttributeError):
                f.append(Finding(
                    "DR_POINTER_STALE", f"{label} pointers: {surface}#{pointer}",
                    "the pointer resolves to nothing in the policy file the entry names",
                    "correct the pointer, or regenerate the policy if the key moved",
                    log_where=f"{REGISTER_REL} :: {label}",
                ))
    upstream = header.get("upstream") if isinstance(header.get("upstream"), dict) else {}
    if upstream.get("sha256") != ctx["upstream_sha256"]:
        f.append(Finding(
            "DR_POINTER_STALE", f"register.upstream.sha256 against {ctx['upstream_path'].as_posix()}",
            f"the upstream schema read sha256 {ctx['upstream_sha256']} with line endings normalized, and "
            "the register pins another, so the register was derived from a different file",
            "point the gate at the pinned zmeta-event-1.0 schema; or, if upstream changed a Locked "
            "schema, review every entry against the new diff before moving the pin",
        ))
    current = fingerprint(zmeta, pse)
    if header.get("diff_sha256") != current:
        f.append(Finding(
            "DR_POINTER_STALE", "register.diff_sha256",
            f"the diff of the two schemas now fingerprints as {current}, and the register was last "
            "reviewed against another, so a schema changed and the register did not move with it",
            "review every entry against the new diff, including each rationale and test_ref, then set "
            "register.diff_sha256 to the value above in the same change as the schema",
        ))
    exemptions = (register.get("compat_claim") or {}).get("exemptions") if isinstance(register.get("compat_claim"), dict) else []
    files = dict(ctx["files"])
    for i, ex in enumerate(_as_list(exemptions)):
        if not isinstance(ex, dict):
            continue
        text = files.get(ex.get("file"))
        hit = text is not None and any(
            CLAIM_RE.search(line) and line_sha256(line) == ex.get("line_sha256") for line in text.splitlines()
        )
        if not hit:
            f.append(Finding(
                "DR_POINTER_STALE", f"compat_claim.exemptions[{i}] {ex.get('file')}",
                "the exemption matches no line that carries the claim, so it exempts nothing and "
                "would exempt whatever line next hashes to it",
                "remove the exemption, or re-pin it to the line it was written for after reading "
                "that line",
            ))

    # 3. DR_DISPOSITION_INVALID.
    stated = header.get("dispositions")
    if not isinstance(stated, dict) or set(stated) != set(DISPOSITIONS):
        f.append(Finding(
            "DR_DISPOSITION_INVALID", "register.dispositions",
            f"the register states {sorted(stated) if isinstance(stated, dict) else stated!r} and the "
            f"closed set this gate enforces is {', '.join(DISPOSITIONS)}",
            "state exactly the five; a new disposition is a change to this tool and the register "
            "together, made deliberately",
        ))
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            continue
        label = _entry_label(entry, i)
        lw = f"{REGISTER_REL} :: {label}"
        d = entry.get("disposition")
        if d not in DISPOSITIONS:
            f.append(Finding(
                "DR_DISPOSITION_INVALID", f"{label} disposition: {d!r}",
                f"the disposition is outside the closed set {', '.join(DISPOSITIONS)}",
                "use one of the five, chosen by the side of the pointers the entry names",
                log_where=lw,
            ))
            continue
        if entry.get("surface"):
            if d not in ("REPLACE", "NEW"):
                f.append(Finding(
                    "DR_DISPOSITION_INVALID", f"{label} disposition: {d}",
                    "a policy-surface entry points into a file in this repository, so the PSE side "
                    "exists and only REPLACE or NEW can describe it",
                    "use REPLACE where a ZMeta policy shape is replaced, or NEW where none existed",
                    log_where=lw,
                ))
            continue
        named = r["named"].get(i, [])
        if not named:
            continue
        cls = {c: classes[c] for c in named}
        inverted = [c for c in named if cls[c] == "differs" and is_inversion(zmeta[c], pse[c])]
        problem = None
        if d == "NEW" and any(v != "pse" for v in cls.values()):
            problem = f"NEW names only pointers {_side_name('pse')}"
        elif d == "DROP" and any(v != "zmeta" for v in cls.values()):
            problem = f"DROP names only pointers {_side_name('zmeta')}"
        elif d == "KEEP" and any(v != "identical" for v in cls.values()):
            problem = "KEEP names only pointers the two schemas agree on"
        elif d == "INVERT" and (len(inverted) != len(named)):
            problem = "INVERT names only pointers one schema refuses in every branch and the other accepts"
        elif d == "REPLACE":
            values = set(cls.values())
            if "identical" in values:
                problem = "REPLACE names no pointer the two schemas agree on"
            elif inverted:
                problem = "a pointer one schema refuses and the other accepts is an inversion, so its disposition is INVERT"
            elif "differs" not in values and not ({"zmeta", "pse"} <= values):
                problem = "REPLACE names a pointer whose attributes differ, or pointers on both sides"
        if problem:
            sides = "; ".join(f"{c} is {_side_name(v)}" for c, v in sorted(cls.items())[:6])
            more = f"; and {len(cls) - 6} more" if len(cls) > 6 else ""
            f.append(Finding(
                "DR_DISPOSITION_INVALID", f"{label} disposition: {d}",
                f"the disposition does not fit the diff: {problem}, and {sides}{more}",
                "choose the disposition the sides support; or split the entry so each disposition "
                "names the pointers it fits",
                log_where=lw,
            ))
    for dv, model_disp in sorted(ctx["divergences"].items()):
        citing = [e for e in entries if isinstance(e, dict) and dv in _as_list(e.get("divergence"))]
        if citing and not any(e.get("disposition") == model_disp for e in citing):
            f.append(Finding(
                "DR_DISPOSITION_INVALID", f"{dv} (spec/layer-model.yaml says {model_disp})",
                f"no entry citing {dv} carries the disposition the layer model records for it, so the "
                "register and the model disagree about what the divergence is",
                "give the entry that describes the divergence the model's disposition; or change the "
                "model's account first, which is a Class B edit to spec/layer-model.yaml",
            ))

    # 4. DR_ENTRY_INCOMPLETE.
    seen_ids: dict = {}
    known_divergences = set(ctx["divergences"]) | set(GENERATION_DIVERGENCES)
    cited: set = set()
    for i, entry in enumerate(entries):
        label = _entry_label(entry, i)
        lw = f"{REGISTER_REL} :: {label}"
        if not isinstance(entry, dict):
            f.append(Finding("DR_ENTRY_INCOMPLETE", label, "the entry is not a mapping", "write the entry as a mapping of its fields", log_where=lw))
            continue
        for key in ENTRY_REQUIRED:
            value = entry.get(key)
            if value is None or value == "" or value == []:
                f.append(Finding(
                    "DR_ENTRY_INCOMPLETE", f"{label} {key}",
                    f"the entry carries no {key}, and an entry without one documents a divergence "
                    "nobody can check",
                    f"write the {key}; the field list is at the top of the register",
                    log_where=lw,
                ))
        extra = sorted(set(entry) - set(ENTRY_REQUIRED) - set(ENTRY_OPTIONAL))
        if extra:
            f.append(Finding(
                "DR_ENTRY_INCOMPLETE", f"{label} {', '.join(map(str, extra))}",
                "the entry carries a key outside the field list, which is how a misspelled required "
                "field reads as present",
                "correct the key to one of the fields the register's header names, or remove it",
                log_where=lw,
            ))
        eid = entry.get("id")
        if eid is not None and (not isinstance(eid, str) or not ENTRY_ID_RE.match(eid)):
            f.append(Finding("DR_ENTRY_INCOMPLETE", f"{label} id", f"the id {eid!r} is not of the form DR-NN", "renumber the entry", log_where=lw))
        if isinstance(eid, str):
            if eid in seen_ids:
                f.append(Finding(
                    "DR_ENTRY_INCOMPLETE", f"{label} id",
                    f"the id is also carried by entries[{seen_ids[eid]}], so a citation of it names two entries",
                    "renumber one of them; ids are never reused",
                    log_where=lw,
                ))
            seen_ids.setdefault(eid, i)
        pointers = entry.get("pointers")
        if pointers is not None and (not isinstance(pointers, list) or not all(isinstance(p, str) and p for p in pointers)):
            f.append(Finding("DR_ENTRY_INCOMPLETE", f"{label} pointers", "pointers is not a list of pointer strings", "write each pointer as a string in a list", log_where=lw))
        for key in ("title", "rationale", "mechanism_preserved"):
            if entry.get(key) is not None and not isinstance(entry.get(key), str):
                f.append(Finding("DR_ENTRY_INCOMPLETE", f"{label} {key}", f"{key} is not a sentence", f"write {key} as text", log_where=lw))
        refs = entry.get("test_ref")
        if refs is not None and not all(isinstance(x, str) and x for x in _as_list(refs)):
            f.append(Finding("DR_ENTRY_INCOMPLETE", f"{label} test_ref", "a test_ref is not a fixture reference string", "write each as conformance/<corpus>.jsonl#<fixture name>", log_where=lw))
        for section in _as_list(entry.get("contract")):
            if str(section) not in ctx["sections"]:
                f.append(Finding(
                    "DR_ENTRY_INCOMPLETE", f"{label} contract: {section}",
                    "the cited section is not a heading of spec/pse-semantics-contract.md, so the "
                    "entry derives from nothing a reader can open",
                    "cite the section number as the contract's heading writes it, such as 4 or 12.4",
                    log_where=lw,
                ))
        for dv in _as_list(entry.get("divergence")):
            cited.add(dv)
            if dv not in known_divergences:
                f.append(Finding(
                    "DR_ENTRY_INCOMPLETE", f"{label} divergence: {dv}",
                    "the entry cites a divergence neither spec/layer-model.yaml nor the contract's "
                    "section 13.2 names",
                    "cite a DV id the model records, or G-1, G-2 or G-3",
                    log_where=lw,
                ))
        reading = entry.get("reading")
        if reading is not None and (not isinstance(reading, str) or not reading.strip().endswith("?")):
            f.append(Finding(
                "DR_ENTRY_INCOMPLETE", f"{label} reading",
                "the reading is not a question, so it reads as a decision taken rather than one "
                "awaiting the operator",
                "state the reading as the question the operator answers, ending in a question mark",
                log_where=lw,
            ))
        gap = entry.get("test_gap")
        if gap is not None and (not isinstance(gap, str) or not gap.strip()):
            f.append(Finding("DR_ENTRY_INCOMPLETE", f"{label} test_gap", "the test_gap is empty", "say what no fixture scores, or remove the key", log_where=lw))
        if entry.get("surface") is not None and not isinstance(entry.get("surface"), str):
            f.append(Finding("DR_ENTRY_INCOMPLETE", f"{label} surface", "the surface is not a path", "write the policy file's repository-relative path", log_where=lw))
    for dv in sorted(known_divergences - cited):
        source = "spec/layer-model.yaml divergences_from_zmeta" if dv in ctx["divergences"] else "spec/pse-semantics-contract.md section 13.2"
        f.append(Finding(
            "DR_ENTRY_INCOMPLETE", f"{dv} ({source})",
            "the contract's section 13.2 names this divergence and no register entry cites it, so the "
            "register omits a departure the contract says belongs in it",
            "cite it from the entry that describes it; or add that entry",
        ))
    readings = register.get("readings")
    for i, rd in enumerate(_as_list(readings)):
        ok = isinstance(rd, dict) and isinstance(rd.get("id"), str) and READING_ID_RE.match(rd["id"]) and isinstance(rd.get("question"), str) and rd["question"].strip().endswith("?")
        if not ok:
            f.append(Finding(
                "DR_ENTRY_INCOMPLETE", f"readings[{i}]",
                "a register reading needs an id of the form DR-RN and a question ending in a question mark",
                "complete the reading, or remove it once the operator has answered it",
            ))

    # 5. DR_TEST_REF_UNRESOLVED.
    by_owner: dict = {}
    for p, owner in r["cover"].items():
        by_owner.setdefault(owner, set()).add(p)
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            continue
        label = _entry_label(entry, i)
        lw = f"{REGISTER_REL} :: {label}"
        covered = by_owner.get(i, set())
        for ref in _as_list(entry.get("test_ref")):
            if not isinstance(ref, str):
                continue
            rel, _, name = ref.partition("#")
            if rel not in ctx["corpora"]:
                f.append(Finding(
                    "DR_TEST_REF_UNRESOLVED", f"{label} test_ref: {ref}",
                    f"the ref names {rel!r}, which is not one of the two corpora, so it resolves to no "
                    "fixture line",
                    f"name a fixture in {' or '.join(CORPORA)}, as <corpus>#<fixture name>",
                    log_where=lw,
                ))
                continue
            hits = [(n, obj) for n, obj in ctx["corpora"][rel] if isinstance(obj, dict) and obj.get("name") == name]
            if len(hits) != 1:
                f.append(Finding(
                    "DR_TEST_REF_UNRESOLVED", f"{label} test_ref: {ref}",
                    f"{len(hits)} lines of {rel} carry the fixture name {name!r}, so the ref resolves to "
                    "no single fixture line. A regenerated corpus that renamed the fixture reads the same",
                    "correct the name to the fixture's name field; or, if the fixture is gone, name the "
                    "fixture that now scores the entry",
                    log_where=lw,
                ))
                continue
            if entry.get("surface") or entry.get("test_gap"):
                continue
            event = hits[0][1].get("event")
            if not isinstance(event, dict) or not touches(event, covered, pse):
                f.append(Finding(
                    "DR_TEST_REF_UNRESOLVED", f"{label} test_ref: {ref}",
                    f"the fixture at {rel}:{hits[0][0]} resolves and its event neither carries a pointer "
                    "the entry covers nor omits one PSE requires, so the ref names a test of something else",
                    "name a fixture whose event exercises the entry; or state a test_gap saying in so many "
                    "words what no fixture scores",
                    log_where=lw,
                ))

    # 6. DR_COMPAT_CLAIM.
    exempt = {
        (ex.get("file"), ex.get("line_sha256"))
        for ex in _as_list(exemptions)
        if isinstance(ex, dict)
    }
    for rel, text in ctx["files"]:
        for n, line in enumerate(text.splitlines(), 1):
            if CLAIM_RE.search(line) and (rel, line_sha256(line)) not in exempt:
                f.append(Finding(
                    "DR_COMPAT_CLAIM", f"{rel}:{n}",
                    "the line carries the upstream compatibility claim. PSE is a private dialect, and "
                    "the license AGENTS.md section 1 quotes forbids the claim without versioning, "
                    "documentation, conformance evidence and release governance as a set",
                    "remove the claim and describe PSE as a private dialect derived from "
                    "zmeta-event-1.0; or, for a line that states the prohibition rather than the claim, "
                    "add an exemption by file and line sha256 to compat_claim in the register with its "
                    "reason, which is a reviewed change",
                    log_where=f"{rel}:{n}",
                ))
    return f


def check_render(ctx: dict) -> list[Finding]:
    import render_divergence_register as renderer

    expected = renderer.render(ctx)
    if ctx.get("rendered") is None:
        what = "the rendering does not exist"
    elif ctx["rendered"] != expected:
        what = "the rendering differs from what the register renders, so the register changed or the file was edited by hand"
    else:
        return []
    return [Finding(
        RENDER_CODE, "spec/divergence-register.md", what,
        "run python tools/render_divergence_register.py to re-render, and never edit the rendering directly",
        log_where="spec/divergence-register.md",
    )]


# ---------------------------------------------------------------------------
# self-test: break the register deliberately
# ---------------------------------------------------------------------------


def _entry(ctx: dict, eid: str) -> dict:
    for entry in ctx["register"]["entries"]:
        if isinstance(entry, dict) and entry.get("id") == eid:
            return entry
    raise KeyError(f"the self-test names {eid}, which the register does not carry")


def _entry_citing(ctx: dict, dv: str) -> dict:
    for entry in ctx["register"]["entries"]:
        if isinstance(entry, dict) and dv in _as_list(entry.get("divergence")):
            return entry
    raise KeyError(f"no entry cites {dv}")


def _entry_naming(ctx: dict, pointer: str) -> dict:
    for entry in ctx["register"]["entries"]:
        if isinstance(entry, dict) and pointer in _as_list(entry.get("pointers")):
            return entry
    raise KeyError(f"no entry names {pointer}")


def _repin(ctx: dict) -> None:
    ctx["register"]["register"]["diff_sha256"] = fingerprint(ctx["zmeta"], ctx["pse"])


class ControlFailed(Exception):
    """A break whose planting is itself the assertion, and the assertion failed."""


def _pse_branch_then(ctx: dict, t: str, s: str) -> dict:
    """The then-clause of the PSE schema's branch that pins one type and subtype."""
    for clause in ctx["pse_root"].get("allOf") or []:
        props = (((clause.get("if") or {}).get("properties") or {}).get("event") or {}).get("properties") or {}
        if (props.get("event_type") or {}).get("const") == t and (props.get("event_subtype") or {}).get("const") == s:
            return clause["then"]
    raise KeyError(f"the PSE schema binds no branch {t} {s}")


def _rederive(ctx: dict) -> None:
    ctx["pse"] = derive_table(ctx["pse_root"])


def _scratch_repository() -> list:
    """Enumerate a throwaway git repository holding the claim three times:
    in a tracked file, in an untracked file, and in a file under an ignored
    cases/ directory. Returns what tree_files reads there, prefixed, or raises
    ControlFailed when the enumeration is not the tracked and the untracked
    file without the ignored one."""
    import tempfile

    claim = "Draft: PSE is " + "ZMeta" + "-compatible.\n"
    with tempfile.TemporaryDirectory(prefix="dr-selftest-") as tmp:
        root = Path(tmp)
        env = dict(os.environ, GIT_CEILING_DIRECTORIES=str(root.parent))
        proc = subprocess.run(["git", "init", "-q"], cwd=root, capture_output=True, env=env)
        if proc.returncode != 0:
            raise ControlFailed("git init failed in a scratch directory, so the enumeration cannot be tested")
        (root / ".gitignore").write_text("cases/\n", encoding="utf-8")
        (root / "tracked.md").write_text(claim, encoding="utf-8")
        subprocess.run(["git", "add", "tracked.md", ".gitignore"], cwd=root, capture_output=True, env=env)
        (root / "untracked.md").write_text(claim, encoding="utf-8")
        (root / "cases").mkdir()
        (root / "cases" / "held.md").write_text(claim, encoding="utf-8")
        found = tree_files(root)
    names = {name for name, _ in found}
    if not {"tracked.md", "untracked.md"} <= names or "cases/held.md" in names:
        raise ControlFailed(
            f"tree_files read {sorted(names)} from a scratch repository, and the scan must read the "
            "tracked and the untracked file and never the ignored cases/held.md"
        )
    return [("scratch-repository/" + name, text) for name, text in found]


def _mutations() -> list:
    """(description, mutator(ctx), expected code, expect_only, why).

    `expect_only` False means the break reaches a second check, and the fifth
    field says how, so a reader can check the cascade against the code.
    """

    def delete_uncited_entry(c):
        c["register"]["entries"].remove(_entry_naming(c, "/event/event_id"))

    def delete_cited_entry(c):
        c["register"]["entries"].remove(_entry_citing(c, "DV-04"))

    def unlist_identical(c):
        c["register"]["identical"].remove("/source/producer")

    def add_pse_field(c):
        c["pse"]["/event/received_at"] = {"type": ["string"], "required": "never"}
        _repin(c)

    def name_missing_pointer(c):
        _entry_citing(c, "DV-09")["pointers"].append("/event/not_a_field")

    def list_differing_as_identical(c):
        c["register"]["identical"].append("/event/ts")

    def change_schema_under_pin(c):
        c["pse"]["/event/ts"] = dict(c["pse"]["/event/ts"], lexical=[["format", "date-time"]])

    def unrequire_lineage_on_claim(c):
        _pse_branch_then(c, "EXTRACT_EVENT", "CLAIM")["required"].remove("lineage")
        _rederive(c)

    def require_lineage_on_shared_pair(c):
        _pse_branch_then(c, "SYSTEM_EVENT", "SCHEMA_VIOLATION")["required"].append("lineage")
        _rederive(c)
        _repin(c)

    def change_enum_in_alternative(c):
        alts = c["pse_root"]["$defs"]["payload_COLLECT_EVENT_PERMITTED"]["properties"]["incidental_estimate"]["oneOf"]
        next(a for a in alts if "enum" in a)["enum"] = ["other"]
        _rederive(c)

    def bound_identical_alternative(c):
        alts = c["pse_root"]["properties"]["source"]["properties"]["sw_version"]["anyOf"]
        next(a for a in alts if a.get("type") == "string")["maxLength"] = 3
        _rederive(c)
        _repin(c)

    def read_other_upstream(c):
        c["upstream_sha256"] = "0" * 64

    def empty_wildcard(c):
        _entry_citing(c, "DV-09")["pointers"].append("/payload[NO_SUCH_EVENT.*]")

    def stale_policy_pointer(c):
        _entry_citing(c, "DV-11")["pointers"] = ["/lineage/no_such_key"]

    def stale_exemption(c):
        c["register"]["compat_claim"]["exemptions"][0]["line_sha256"] = "0" * 64

    def disposition_outside_set(c):
        _entry_citing(c, "DV-01")["disposition"] = "RENAME"

    def drop_on_pse_only(c):
        _entry_citing(c, "DV-02")["disposition"] = "DROP"

    def replace_an_inversion(c):
        _entry_citing(c, "DV-06")["disposition"] = "REPLACE"

    def keep_a_difference(c):
        _entry_citing(c, "G-1")["disposition"] = "KEEP"

    def sixth_disposition(c):
        c["register"]["register"]["dispositions"]["MERGE"] = "a sixth disposition nobody enforces"

    def delete_rationale(c):
        del _entry_citing(c, "DV-03")["rationale"]

    def delete_mechanism(c):
        del _entry_citing(c, "DV-10")["mechanism_preserved"]

    def missing_contract_section(c):
        _entry_citing(c, "DV-01")["contract"] = ["99"]

    def uncite_dv(c):
        _entry_citing(c, "DV-07")["divergence"] = []

    def unknown_dv(c):
        e = _entry_citing(c, "DV-01")
        e["divergence"] = ["DV-01", "DV-99"]

    def uncite_generation(c):
        e = _entry_citing(c, "G-2")
        e["divergence"] = [d for d in e["divergence"] if d != "G-2"]

    def reading_not_question(c):
        e = next(x for x in c["register"]["entries"] if isinstance(x, dict) and x.get("reading"))
        e["reading"] = e["reading"].rstrip(" ?") + "."

    def misspelled_field(c):
        e = _entry_citing(c, "DV-01")
        e["mechanism_preserve"] = e.pop("mechanism_preserved")

    def duplicate_id(c):
        _entry_citing(c, "DV-02")["id"] = _entry_citing(c, "DV-01")["id"]

    def dangling_test_ref(c):
        _entry_citing(c, "DV-07")["test_ref"] = ["conformance/must-fail.jsonl#no-such-fixture"]

    def test_ref_outside_corpora(c):
        _entry_citing(c, "DV-07")["test_ref"] = ["conformance/gate/decisions.jsonl#row-1"]

    def irrelevant_test_ref(c):
        e = _entry_citing(c, "DV-07")
        e["test_ref"] = ["conformance/must-pass.jsonl#authorize-grant"]
        e.pop("test_gap", None)

    def renamed_fixture(c):
        e = _entry_citing(c, "DV-01")
        rel, _, name = _as_list(e["test_ref"])[0].partition("#")
        for _, obj in c["corpora"][rel]:
            if obj.get("name") == name:
                obj["name"] = name + "-renamed"

    def plant_claim(c):
        c["files"].append(("README.md", "PSE is " + "ZMeta" + "-compatible at the envelope.\n"))

    def plant_claim_lower(c):
        c["files"].append(("docs/plainsight_worklog.md", "an entry calling it " + "zmeta" + "-compatible\n"))

    def plant_claim_nbhyphen(c):
        c["files"].append(("notes/draft.md", "Draft: " + "ZMeta" + "\u2011compatible, see section 2.\n"))

    def enumerate_scratch_repository(c):
        c["files"].extend(_scratch_repository())

    def edit_exempted_line(c):
        ex = c["register"]["compat_claim"]["exemptions"][0]
        out = []
        for rel, text in c["files"]:
            if rel == ex["file"]:
                lines = text.splitlines()
                for k, line in enumerate(lines):
                    if CLAIM_RE.search(line) and line_sha256(line) == ex["line_sha256"]:
                        lines[k] = line + " Edited."
                text = "\n".join(lines) + "\n"
            out.append((rel, text))
        c["files"] = out

    def hand_edit_rendering(c):
        c["rendered"] = (c["rendered"] or "") + "\nA line added by hand.\n"

    return [
        ("delete the entry for the identifier pattern (a missing entry)", delete_uncited_entry, "DR_PATH_UNCOVERED", True, ""),
        ("delete the entry that cites DV-04", delete_cited_entry, "DR_PATH_UNCOVERED", False,
         "that entry is the only one citing DV-04, so check 4 refuses the uncited divergence too"),
        ("drop a pointer from identical:", unlist_identical, "DR_PATH_UNCOVERED", True, ""),
        ("add a PSE field no entry names, with the pin moved", add_pse_field, "DR_PATH_UNCOVERED", True, ""),
        ("name a pointer neither schema has", name_missing_pointer, "DR_POINTER_STALE", True, ""),
        ("list a differing pointer under identical:", list_differing_as_identical, "DR_POINTER_STALE", True, ""),
        ("change the PSE schema under the diff pin", change_schema_under_pin, "DR_POINTER_STALE", True, ""),
        ("stop requiring lineage on EXTRACT_EVENT CLAIM in the PSE schema", unrequire_lineage_on_claim, "DR_POINTER_STALE", True, ""),
        ("require lineage on the shared pair in the PSE schema, with the pin moved", require_lineage_on_shared_pair, "DR_DISPOSITION_INVALID", True, ""),
        ("change the enum inside one alternative of incidental_estimate", change_enum_in_alternative, "DR_POINTER_STALE", True, ""),
        ("bound the string alternative of /source/sw_version, with the pin moved", bound_identical_alternative, "DR_POINTER_STALE", False,
         "identical: covers only a pointer the schemas agree on, so check 1 finds the now-differing pointer uncovered"),
        ("read an upstream schema other than the pinned one", read_other_upstream, "DR_POINTER_STALE", True, ""),
        ("a wildcard pointer that expands to nothing", empty_wildcard, "DR_POINTER_STALE", True, ""),
        ("a policy pointer that resolves to nothing", stale_policy_pointer, "DR_POINTER_STALE", True, ""),
        ("an exemption that matches no line", stale_exemption, "DR_POINTER_STALE", False,
         "the line it exempted is no longer exempt, so check 6 refuses that line as a claim"),
        ("a disposition outside the closed set", disposition_outside_set, "DR_DISPOSITION_INVALID", True, ""),
        ("DROP on a pointer in pse-event-0.1 only", drop_on_pse_only, "DR_DISPOSITION_INVALID", True, ""),
        ("REPLACE where the diff shows a refusal reversed", replace_an_inversion, "DR_DISPOSITION_INVALID", True, ""),
        ("KEEP on a pointer whose attributes differ", keep_a_difference, "DR_DISPOSITION_INVALID", True, ""),
        ("state a sixth disposition in the register", sixth_disposition, "DR_DISPOSITION_INVALID", True, ""),
        ("delete a rationale", delete_rationale, "DR_ENTRY_INCOMPLETE", True, ""),
        ("delete a mechanism_preserved", delete_mechanism, "DR_ENTRY_INCOMPLETE", True, ""),
        ("cite a contract section that does not exist", missing_contract_section, "DR_ENTRY_INCOMPLETE", True, ""),
        ("drop the only citation of DV-07", uncite_dv, "DR_ENTRY_INCOMPLETE", True, ""),
        ("cite a divergence the model does not record", unknown_dv, "DR_ENTRY_INCOMPLETE", True, ""),
        ("drop the only citation of G-2", uncite_generation, "DR_ENTRY_INCOMPLETE", True, ""),
        ("write a reading as a statement", reading_not_question, "DR_ENTRY_INCOMPLETE", True, ""),
        ("misspell a required field", misspelled_field, "DR_ENTRY_INCOMPLETE", True, ""),
        ("give two entries one id", duplicate_id, "DR_ENTRY_INCOMPLETE", True, ""),
        ("point a test_ref at a fixture that does not exist (a dangling ref)", dangling_test_ref, "DR_TEST_REF_UNRESOLVED", True, ""),
        ("point a test_ref outside the two corpora", test_ref_outside_corpora, "DR_TEST_REF_UNRESOLVED", True, ""),
        ("point a test_ref at a fixture that touches nothing the entry names", irrelevant_test_ref, "DR_TEST_REF_UNRESOLVED", True, ""),
        ("regenerate a corpus that renames a cited fixture", renamed_fixture, "DR_TEST_REF_UNRESOLVED", True, ""),
        ("plant the claim in a tracked file", plant_claim, "DR_COMPAT_CLAIM", True, ""),
        ("plant the claim in lower case", plant_claim_lower, "DR_COMPAT_CLAIM", True, ""),
        ("plant the claim with a non-breaking hyphen", plant_claim_nbhyphen, "DR_COMPAT_CLAIM", True, ""),
        ("scan a scratch git repo: tracked and untracked read, ignored not", enumerate_scratch_repository, "DR_COMPAT_CLAIM", True, ""),
        ("edit the exempted line by one word", edit_exempted_line, "DR_COMPAT_CLAIM", False,
         "the exemption's hash now matches no line, so check 2 refuses the exemption as stale"),
        ("hand-edit the rendering", hand_edit_rendering, RENDER_CODE, True, ""),
    ]


def self_test(ctx: dict, quiet: bool) -> int:
    baseline = check(ctx) + check_render(ctx)
    if baseline:
        print("validate_divergence_register --self-test cannot run: the unbroken register is not clean", file=sys.stderr)
        for fnd in baseline:
            print(fnd.render(), file=sys.stderr)
        return 1
    failures = 0
    cascading = 0
    lines = []
    muts = _mutations()
    for desc, mutate, expected, only, why in muts:
        m = copy.deepcopy(ctx)
        try:
            mutate(m)
        except (KeyError, IndexError, StopIteration, ValueError, ControlFailed, Unreadable) as exc:
            failures += 1
            lines.append(f"  BROKEN   {desc:72} the break could not be planted: {exc}")
            continue
        found = check(m)
        if expected == RENDER_CODE:
            found += check_render(m)
        fired = {fnd.code for fnd in found}
        if expected not in fired:
            ok, note = False, f", fired {sorted(fired)}"
        elif only and fired != {expected}:
            ok, note = False, f", also fired {sorted(fired - {expected})} and claims expect_only"
        else:
            ok, note = True, ""
        failures += 0 if ok else 1
        if ok and not only:
            cascading += 1
        lines.append(f"  {'refused' if ok else 'PASSED '}  {desc:72} expected {expected}{note}")
        if ok and not only:
            lines.append(f"            cascades, and that is expected: {why}")
    planned = {exp for _, _, exp, _, _ in muts}
    unexercised = [code for code in CHECK_CODES + (RENDER_CODE,) if code not in planned]
    if unexercised:
        failures += 1
        lines.append(f"  MISSING  no break expects {', '.join(unexercised)}, so that check has never been seen to refuse")
    if failures or not quiet:
        print("\n".join(lines))
        print()
    if failures:
        print(
            f"validate_divergence_register --self-test: {failures} break(s) were not refused as claimed. "
            "A gate nobody has watched fail is an assumption (doctrine/HYGIENE.md section 2).",
            file=sys.stderr,
        )
        return 1
    if not quiet:
        print(
            f"validate_divergence_register --self-test ok: {len(muts)} deliberate breaks, {len(muts)} refused, "
            f"{len(muts) - cascading} by the expected code alone, {cascading} cascading with a stated reason. "
            f"All six checks and the rendering refused at least once, among them the negative controls for "
            f"the done-when's first two sentences, a deleted entry and a dangling test_ref."
        )
    return 0


# ---------------------------------------------------------------------------
# entry
# ---------------------------------------------------------------------------


def summary(ctx: dict) -> dict:
    classes = classify(ctx["zmeta"], ctx["pse"])
    counts = {k: sum(1 for v in classes.values() if v == k) for k in ("zmeta", "pse", "differs", "identical")}
    entries = [e for e in ctx["register"]["entries"] if isinstance(e, dict)]
    readings = sum(1 for e in entries if e.get("reading")) + len(_as_list(ctx["register"].get("readings")))
    return {"counts": counts, "entries": len(entries), "identical": len(_as_list(ctx["register"].get("identical"))), "readings": readings}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Divergence register gate: the register against a diff of the two schemas.")
    ap.add_argument("--quiet", action="store_true", help="Print only on failure.")
    ap.add_argument("--self-test", action="store_true", help="Break the register in memory and assert each break is refused.")
    args = ap.parse_args(argv)

    try:
        ctx = load_context()
    except Unreadable as exc:
        print(exc.render(), file=sys.stderr)
        return 2

    if args.self_test:
        return self_test(ctx, args.quiet)

    findings = check(ctx) + check_render(ctx)

    if gate_log:
        try:
            gate_log.record_run(GATE, "refuse" if findings else "pass", count=len(findings))
            for fnd in findings:
                gate_log.record_finding(GATE, code=fnd.code, where=fnd.log_where)
        except Exception:
            pass

    if findings:
        for fnd in findings:
            print(fnd.render(), file=sys.stderr)
            print(file=sys.stderr)
        print(
            f"validate_divergence_register: {len(findings)} refusal(s). The register is rank 3 and Class B, "
            "and its entry list is derived from the diff of the two schemas (docs/THE-GAMEPLAN.md Step 9).",
            file=sys.stderr,
        )
        return 1

    if not args.quiet:
        s = summary(ctx)
        c = s["counts"]
        print(
            f"validate_divergence_register ok: {s['entries']} entries and {s['identical']} identical pointers "
            f"cover a diff of {c['zmeta']} pointers in {ZSIDE} only, {c['pse']} in {PSIDE} only, "
            f"{c['differs']} in both and differing, and {c['identical']} identical; "
            f"{s['readings']} reading(s) await the operator."
        )
        print(
            "  checks: path coverage, stale pointers and pins, closed dispositions that fit the diff, "
            "complete entries citing the contract, test_refs that resolve and touch, no compatibility "
            "claim in the tree; and the rendering current"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
