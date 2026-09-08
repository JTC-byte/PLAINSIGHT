#!/usr/bin/env python3
"""Rung 2 of the conformance ladder: schema plus policy over a JSONL corpus.

`CONFORMANCE.md` section 3 names this tool as the check that an event corpus is
schema-valid and passes every layer denylist, lineage rule, and producer-
authority check. It reads the generated schema and the four generated policy
files, never the layer model directly, so what it enforces is what the
generated artifacts say, and `tools/generate_pse.py --check` is what keeps
those current against the model.

Two requirements from `CONFORMANCE.md` section 5 shape the grading loop.

`expect_only`. A must-fail fixture may require its expected code to be the sole
failing code. ZMeta's runner passes a fixture when the expected code appears
anywhere, and a fixture that passes on incidental schema noise proves nothing
about the guard it was written for. Every D2 and D5 fixture in the model's
fixture map carries `expect_only: true`, and this tool refuses a corpus where
one of them does not.

Short-circuit disclosure. This runner does not short-circuit on a schema
failure: every check that can run still runs, and the codes are the union. The
one place it cannot continue is an envelope that names no known event type,
because every later check is per type. In that case the run records which
checks it did not reach, and a fixture whose expected code belongs to an
unreached check fails for that stated reason rather than passing on a code it
never had a chance to emit.

What this tool does not evaluate, stated so a green run is not read as more.
Rules the model marks `runtime` are conditions about the case rather than the
event and are listed under `runtime_rules` in `policy/semantics.yaml`; the
runner at Step 10 evaluates them. Two exceptions are evaluated here because a
corpus-aware runner can resolve them: a citation of a possible-band cluster
needs a caveat, and a citation of a gestalt-rationale cluster needs a note.
`REASON_NAMES_SUBJECT` is a review rule with no mechanism and is never emitted
here. The chain rules in `policy/lineage.yaml` are the gate's and belong to
`tools/validate_authorization.py` at Step 8. `ABSENCE_CLAIMED_WITHOUT_CANARY`
fires on every `attempted_and_absent` until a connector's canary proves a field
`always_present`, which is Step 12 input; today there is no proof, so there is
no exemption.

Exit codes: 0 clean, 1 a violation or a failed fixture, 2 the schema, the
policy, or a corpus could not be read.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import deque
from pathlib import Path

try:
    import yaml
    from jsonschema import Draft202012Validator
except ImportError as exc:  # pragma: no cover
    print(
        "REFUSED DEPENDENCY_MISSING\n"
        "  where: tools/validate.py\n"
        f"  what:  {exc}\n"
        "  moves: pip install pyyaml jsonschema",
        file=sys.stderr,
    )
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schema" / "pse-event-0.1.schema.json"
POLICY = ROOT / "policy"
REGISTRY = ROOT / "ontology" / "selectors.yaml"
MUST_PASS = ROOT / "conformance" / "must-pass.jsonl"
MUST_FAIL = ROOT / "conformance" / "must-fail.jsonl"

#: The corpus's human identities. Producer authority names "<human identity>"
#: for the types a named person emits, and the model says the identity list is
#: deployment configuration that never lives in a tracked file. The conformance
#: corpus is not a deployment, so it declares its synthetic analyst here.
#: A deployment passes its own list with --human-identity.
DEFAULT_HUMANS = ("analyst-example",)

CHECKS = ("schema", "producer", "denylist", "rules", "lineage", "cross_event")

REQUIRED_RE = re.compile(r"'([^']+)' is a required property")


# ---------------------------------------------------------------------------
# loading
# ---------------------------------------------------------------------------


def _refuse(code: str, where: str, what: str, moves: str) -> None:
    print(f"REFUSED {code}\n  where: {where}\n  what:  {what}\n  moves: {moves}", file=sys.stderr)


def _load_yaml(path: Path, wrapper: str) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or wrapper not in data:
        raise ValueError(f"{path.relative_to(ROOT).as_posix()} has no top-level `{wrapper}` key")
    return data[wrapper]


class Policy:
    """The generated artifacts, loaded once."""

    def __init__(self):
        self.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(self.schema)
        self.validator = Draft202012Validator(self.schema)
        self.semantics = _load_yaml(POLICY / "semantics.yaml", "semantics")
        self.lineage = _load_yaml(POLICY / "lineage.yaml", "lineage")
        self.producer = _load_yaml(POLICY / "producer-authority.yaml", "producer_authority")
        self.codes = _load_yaml(POLICY / "violation-codes.yaml", "violation_codes")
        self.registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
        self.types = self.semantics["event_types"]
        self.declared = {c["code"] for c in self.codes["codes"]}
        self.emitted_by = {c["code"]: set(c.get("emitted_by") or []) for c in self.codes["codes"]}
        self.generated_selectors = {
            k for k, v in (self.registry.get("selectors") or {}).items()
            if isinstance(v, dict) and v.get("provenance_state") == "GENERATED"
        }
        self.must_not_cite = {}
        for p in self.registry.get("prohibitions") or []:
            if p.get("must_not_satisfy_citation_for"):
                self.must_not_cite[p["selector"]] = p["must_not_satisfy_citation_for"]
        self.anchor_ok = {
            k for k, v in (self.registry.get("selectors") or {}).items()
            if isinstance(v, dict) and v.get("may_anchor_entity") is True
        }

    def denylist(self, tname: str) -> dict[str, str]:
        """name -> group code for a type."""
        out = {}
        for g in self.types.get(tname, {}).get("payload_must_not_contain") or []:
            for n in g.get("names") or []:
                out.setdefault(n, g.get("code"))
        return out


def load_policy() -> Policy:
    try:
        return Policy()
    except Exception as exc:  # noqa: BLE001
        _refuse(
            "GENERATED_ARTIFACTS_UNREADABLE",
            "schema/, policy/",
            f"{exc}",
            "run `python tools/generate_pse.py`, then `python tools/generate_pse.py --check`",
        )
        sys.exit(2)


# ---------------------------------------------------------------------------
# one event
# ---------------------------------------------------------------------------


class Index:
    """Events of one case by id, so lineage and citations resolve."""

    def __init__(self, events: list[dict]):
        self.by_id: dict[str, dict] = {}
        for e in events:
            eid = (((e or {}).get("event") or {}).get("event_id"))
            if isinstance(eid, str):
                self.by_id[eid] = e

    def get(self, eid) -> dict | None:
        return self.by_id.get(eid) if isinstance(eid, str) else None


def _ts(e: dict) -> tuple[str, str]:
    ev = (e or {}).get("event") or {}
    return ev.get("event_type"), ev.get("event_subtype")


def _payload(e: dict) -> dict:
    p = (e or {}).get("payload")
    return p if isinstance(p, dict) else {}


def _parents(e: dict) -> list[str]:
    lin = (e or {}).get("lineage")
    if isinstance(lin, dict) and isinstance(lin.get("based_on"), list):
        return [x for x in lin["based_on"] if isinstance(x, str)]
    return []


def _leaves(err) -> list:
    """The leaf errors under an anyOf/oneOf, preferring the non-type failure."""
    if err.validator in ("anyOf", "oneOf") and err.context:
        leaves = []
        for sub in err.context:
            leaves.extend(_leaves(sub))
        non_type = [l for l in leaves if l.validator != "type"]
        return non_type or leaves[:1]
    return [err]


def _when_holds(when, subtype: str, payload: dict) -> bool:
    if when == "always":
        return True
    if when == "runtime":
        return False
    if not isinstance(when, dict):
        return False
    if "all_of" in when:
        return all(_when_holds(c, subtype, payload) for c in when["all_of"])
    if "subtype" in when:
        subs = when["subtype"] if isinstance(when["subtype"], list) else [when["subtype"]]
        return subtype in subs
    field = when.get("field")
    if "equals" in when:
        return payload.get(field) == when["equals"]
    if "contains" in when:
        v = payload.get(field)
        return isinstance(v, (list, str)) and when["contains"] in v
    if when.get("present"):
        return field in payload and payload.get(field) is not None
    return False


def check_event(e: dict, pol: Policy, index: Index, humans: set[str]) -> tuple[set[str], set[str]]:
    """Codes fired for one event, and the checks that were reached."""
    codes: set[str] = set()
    reached: set[str] = set()

    if not isinstance(e, dict):
        codes.add("SCHEMA_INVALID")
        return codes, {"schema"}

    tname, sub = _ts(e)
    tdef = pol.types.get(tname)
    payload = _payload(e)
    disc = None
    if tdef:
        disc = tdef["discriminator"].split(".", 1)[1]
    denylist = pol.denylist(tname) if tdef else {}
    conf_code = (tdef or {}).get("confidence", {}).get("code") or "CONFIDENCE_PROHIBITED"
    registry_fields = set((tdef or {}).get("registry_fields") or [])

    # active rules, for the field-ownership mapping (a rule that requires a
    # field owns that field's shape failures)
    active_rules = []
    if tdef:
        for rule in tdef.get("rules") or []:
            if _when_holds(rule.get("when"), sub, payload):
                active_rules.append(rule)
    field_owner: dict[str, str] = {}
    for rule in active_rules:
        for f in rule.get("requires") or []:
            field_owner.setdefault(f, rule["code"])

    # 1. schema
    reached.add("schema")
    for err in pol.validator.iter_errors(e):
        for leaf in _leaves(err):
            path = list(leaf.absolute_path)
            kw = leaf.validator
            codes.add(_name_schema_error(path, kw, leaf, e, tdef, denylist, conf_code, registry_fields, field_owner, disc))

    if not tdef:
        codes.add("EVENT_TYPE_UNKNOWN")
        return codes, reached

    # 2. producer authority, before any semantic check. Authority is per type
    # and subtype, so a subtype outside the type's set has no authority to
    # check; the schema has already named that EVENT_SUBTYPE_MISMATCH.
    reached.add("producer")
    if sub in (tdef.get("subtypes") or []):
        producer = ((e.get("source") or {}).get("producer"))
        key = f"{tname}.{sub}"
        allowed = set(pol.producer.get("effective", {}).get(key) or [])
        if not _producer_allowed(producer, allowed, humans):
            codes.add(pol.producer.get("violation_code") or "PRODUCER_NOT_ALLOWED")

    # 3. recursive denylist
    reached.add("denylist")
    nested_code = (pol.semantics.get("payload_denylist") or {}).get("nested_hit_code")
    for depth, name in _walk_keys(payload):
        if name in denylist:
            codes.add(denylist[name])
            if depth > 0 and nested_code:
                codes.add(nested_code)
    if "confidence" in e:
        codes.add(conf_code)

    # 4. payload rules with a machine-readable condition. A required field the
    # subtype already lists is the schema's to shape, and null is legal there
    # when its shape allows it (a seed run's motivated_by). A field a rule adds
    # beyond the subtype's list has to be present and non-null, because null
    # exit_criterion on a quarantine is no exit criterion (CR-6).
    reached.add("rules")
    subtype_required = set((tdef.get("required") or {}).get(sub) or [])
    for rule in active_rules:
        for f in rule.get("requires") or []:
            missing = f not in payload or (f not in subtype_required and payload.get(f) is None)
            if missing:
                codes.add(rule["code"])
        codes |= _special_rule(rule["name"], e, tname, sub, payload, pol, index)

    # 5. lineage
    reached.add("lineage")
    codes |= _lineage(e, tname, sub, payload, pol, index)

    # 6. cross-event rules that need the case
    reached.add("cross_event")
    codes |= _cross_event(e, tname, sub, payload, pol, index)

    codes.discard(None)
    return codes, reached


def _name_schema_error(path, kw, leaf, e, tdef, denylist, conf_code, registry_fields, field_owner, disc) -> str:
    """The code a schema failure is named by (policy/semantics.yaml schema_error_map)."""
    if path and path[0] == "confidence":
        return conf_code
    if kw is None and "False schema" in (leaf.message or ""):
        # jsonschema reports a `false` subschema with no validator and an empty
        # path. The only false subschemas in the generated schema are the
        # reserved envelope key, so this is the confidence refusal.
        return conf_code
    if path in (["pse_version"], ["derived_from"]) and kw == "const":
        return "VERSION_MISMATCH"
    if path == ["case_id"]:
        return "CASE_ID_MISSING"
    if path == ["event", "event_type"]:
        return "EVENT_TYPE_UNKNOWN"
    if path == ["event", "event_subtype"]:
        return "EVENT_SUBTYPE_MISMATCH"
    if kw == "required":
        m = REQUIRED_RE.search(leaf.message or "")
        missing = m.group(1) if m else None
        if not path:
            if missing == "case_id":
                return "CASE_ID_MISSING"
            if missing == "lineage":
                return "LINEAGE_MISSING"
            return "SCHEMA_INVALID"
        if path == ["payload"]:
            if missing in field_owner:
                return field_owner[missing]
            return "PAYLOAD_FIELD_MISSING"
        if path and path[0] == "payload" and len(path) >= 2 and path[1] in field_owner:
            return field_owner[path[1]]
        return "PAYLOAD_FIELD_MISSING" if path and path[0] == "payload" else "SCHEMA_INVALID"
    if kw == "additionalProperties" and path == ["payload"] and tdef:
        allowed_props = set((leaf.schema or {}).get("properties") or {})
        unexpected = [k for k in (leaf.instance or {}) if k not in allowed_props]
        for k in unexpected:
            if k in denylist:
                return denylist[k]
        return "SCHEMA_INVALID"
    if path and path[0] == "payload" and len(path) >= 2:
        field = path[1]
        if field == disc and kw in ("const", "enum"):
            return "EVENT_SUBTYPE_MISMATCH"
        if field in field_owner and kw in ("const", "enum", "minItems", "minimum", "type", "pattern", "minLength"):
            return field_owner[field]
        if kw == "enum" and (field in registry_fields or path[-1] in ("cited_as", "anchor_selector_type")):
            return "SELECTOR_TYPE_UNREGISTERED"
        if kw in ("enum", "const"):
            return "ENUM_VALUE_INVALID"
    if kw in ("enum", "const") and path and path[0] == "source":
        return "ENUM_VALUE_INVALID"
    return "SCHEMA_INVALID"


def _producer_allowed(producer, allowed: set[str], humans: set[str]) -> bool:
    if not isinstance(producer, str) or not producer:
        return False
    for a in allowed:
        if a == "<human identity>":
            if producer in humans:
                return True
        elif a.endswith("*"):
            if producer.startswith(a[:-1]):
                return True
        elif a == producer:
            return True
    return False


def _walk_keys(obj, depth: int = 0):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield depth, k
            yield from _walk_keys(v, depth + 1)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk_keys(v, depth + 1)


def _first_parent(e: dict, index: Index) -> dict | None:
    parents = _parents(e)
    return index.get(parents[0]) if parents else None


def _special_rule(name: str, e, tname, sub, payload, pol: Policy, index: Index) -> set[str]:
    """Rules whose `requires` is empty constrain a value; each is named here."""
    out: set[str] = set()
    if name == "accepted_const_false":
        if payload.get("accepted") is not False:
            out.add("LINK_HAS_ACCEPTANCE")
    elif name == "anchor_selector_may_anchor":
        # The registry's may_anchor_entity decides. An Account anchored on a
        # handle renders a handle-owner change as drift (fixture 3).
        anchor = payload.get("anchor_selector_type")
        if anchor is not None and anchor not in pol.anchor_ok:
            out.add("SELECTOR_ANCHOR_PROHIBITED")
    elif name == "absence_requires_canary":
        # No canary proof exists before Step 12, so every attempted_and_absent refuses.
        out.add("ABSENCE_CLAIMED_WITHOUT_CANARY")
    elif name == "almost_certain_needs_two_classes":
        classes = (pol.types[tname].get("evidence_classes") or {})
        seen = {cls for cls, members in classes.items() for c in (payload.get("rationale_codes") or []) if c in members}
        if len(seen) < 2:
            out.add("BAND_UNSUPPORTED")
    elif name == "rationale_present":
        seams = payload.get("member_seams")
        members = payload.get("members") or []
        if not isinstance(seams, dict) or any(m not in seams or not seams.get(m) for m in members):
            out.add("RATIONALE_MISSING")
    elif name == "target_matches_disposition":
        targets = (pol.lineage.get("allowed_targets") or {}).get(tname, {}).get(sub)
        parent = _first_parent(e, index)
        if targets is not None and parent is not None:
            ptype, _ = _ts(parent)
            if ptype not in targets:
                out.add("LINEAGE_PARENT_TYPE_INVALID")
    elif name == "environment_is_isolated":
        env = ((e.get("source") or {}).get("environment"))
        egress_env = ((payload.get("egress") or {}).get("environment")) if isinstance(payload.get("egress"), dict) else None
        if env != "ISOLATED" or egress_env != "ISOLATED":
            out.add("EGRESS_ENVIRONMENT_REFUSED")
    return out


def _lineage(e, tname, sub, payload, pol: Policy, index: Index) -> set[str]:
    out: set[str] = set()
    lin = pol.lineage
    required = (lin.get("required_by_subtype") or {}).get(tname, {}).get(sub)
    parents = _parents(e)
    has_lineage = isinstance(e.get("lineage"), dict)
    if required and not parents:
        rp = (lin.get("required_parents") or {}).get(tname, {}).get(sub) or {}
        out.add(rp.get("code") or "LINEAGE_MISSING")
        return out
    if not has_lineage:
        return out
    allowed = (lin.get("allowed_parents") or {}).get(tname, {})
    resolved_pairs = []
    for pid in parents:
        parent = index.get(pid)
        if parent is None:
            out.add("LINEAGE_PARENT_UNRESOLVED")
            continue
        if parent.get("case_id") != e.get("case_id"):
            out.add("LINEAGE_CROSS_CASE")
        ptype, psub = _ts(parent)
        resolved_pairs.append((ptype, psub))
        if psub not in (allowed.get(ptype) or []):
            out.add("LINEAGE_PARENT_TYPE_INVALID")
    rp = (lin.get("required_parents") or {}).get(tname, {}).get(sub)
    if rp:
        any_of = {(a.get("type"), a.get("subtype")) for a in rp.get("any_of") or []}
        if not any(pair in any_of for pair in resolved_pairs):
            out.add(rp.get("code") or "LINEAGE_MISSING")
    for key in ("based_on", "basis_claims"):
        v = payload.get(key)
        if isinstance(v, list) and not set(x for x in v if isinstance(x, str)) <= set(parents):
            out.add("LINEAGE_PAYLOAD_BASED_ON_NOT_SUBSET")
    return out


def _cross_event(e, tname, sub, payload, pol: Policy, index: Index) -> set[str]:
    out: set[str] = set()
    if tname == "PROBE_EVENT" and sub == "RUN_START":
        decision = None
        for pid in _parents(e):
            p = index.get(pid)
            if p is not None and _ts(p) == ("COLLECT_EVENT", "PERMITTED"):
                decision = p
                break
        if decision is not None:
            dp = _payload(decision)
            for f in ("connector_id", "target_selector_type", "motivated_by"):
                if payload.get(f) != dp.get(f):
                    out.add("SUBJECT_NOT_AUTHORIZED")
    if tname == "COLLECT_EVENT" and sub == "PERMITTED":
        grant = None
        for pid in _parents(e):
            p = index.get(pid)
            if p is not None and _ts(p)[0] == "AUTHORIZE_EVENT":
                grant = p
                break
        if grant is not None and _ts(grant)[1] == "GRANT" and not _payload(grant).get("purpose_hash"):
            out.add("CASE_PURPOSE_UNBOUND")
    if tname == "IDENTITY_EVENT" and sub == "CLUSTER":
        members = set(payload.get("members") or [])
        override = payload.get("circularity_override")
        overridden = isinstance(override, dict) and bool(override.get("note"))
        for cid in payload.get("basis_claims") or []:
            claim = index.get(cid)
            if claim is None or _ts(claim)[0] != "EXTRACT_EVENT":
                continue
            cp = _payload(claim)
            circular = cp.get("selector_type") in pol.generated_selectors
            item = _first_parent(claim, index)
            run = _first_parent(item, index) if item else None
            motivating = index.get(_payload(run).get("motivated_by")) if run else None
            if motivating is not None and _payload(motivating).get("subject_ref") in members:
                circular = True
            if circular and not overridden:
                out.add("MERGE_CIRCULAR")
    if tname == "ASSESS_EVENT":
        parents = set(_parents(e))
        for cit in payload.get("citations") or []:
            if not isinstance(cit, dict):
                continue
            ref = cit.get("ref")
            if ref not in parents or index.get(ref) is None:
                out.add("CITATION_MISSING")
                continue
            cited = index.get(ref)
            ctype, csub = _ts(cited)
            cp = _payload(cited)
            if ctype == "EXTRACT_EVENT":
                st = cp.get("selector_type")
                cited_as = cit.get("cited_as")
                if cited_as is not None and cited_as != st:
                    out.add("HINT_CITED_AS_VALUE")
                if cited_as is not None and pol.must_not_cite.get(st) == cited_as:
                    out.add("HINT_CITED_AS_VALUE")
                if st in pol.generated_selectors and not _has_adjudication(ref, index, "PROMOTE", {"promotion_kind": "generated_to_observed"}):
                    out.add("GENERATED_CITED_AS_OBSERVED")
                if not _has_adjudication(ref, index, "VERIFY"):
                    out.add("CITATION_UNADJUDICATED")
            if ctype == "IDENTITY_EVENT" and csub == "CLUSTER":
                if cp.get("band") == "possible" and not cit.get("caveat"):
                    out.add("CITATION_CAVEAT_MISSING")
                if "g" in (cp.get("rationale_codes") or []) and not cit.get("note"):
                    out.add("RATIONALE_NOTE_MISSING")
    return out


def _has_adjudication(target: str, index: Index, disposition: str, fields: dict | None = None) -> bool:
    for ev in index.by_id.values():
        if _ts(ev) == ("ADJUDICATE_EVENT", disposition):
            p = _payload(ev)
            if p.get("target_ref") == target and all(p.get(k) == v for k, v in (fields or {}).items()):
                return True
    return False


# ---------------------------------------------------------------------------
# corpora
# ---------------------------------------------------------------------------


def iter_jsonl(path: Path):
    with open(path, "r", encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            line = line.strip()
            if line:
                yield n, json.loads(line)


def grade_must_pass(path: Path, pol: Policy, humans: set[str], quiet: bool) -> int:
    rows = list(iter_jsonl(path))
    if not rows:
        _refuse("CORPUS_EMPTY", path.relative_to(ROOT).as_posix(), "contains no fixtures; an empty file proves nothing", "restore the corpus")
        return 1
    index = Index([r.get("event") for _, r in rows])
    failures = 0
    for n, row in rows:
        codes, _ = check_event(row.get("event"), pol, index, humans)
        if codes:
            failures += 1
            print(f"FAIL pass line={n} name={row.get('name')} codes={','.join(sorted(codes))}")
    if not quiet:
        print(f"must-pass: {len(rows)} events, {failures} failed")
    return 1 if failures else 0


def grade_must_fail(path: Path, pol: Policy, humans: set[str], quiet: bool) -> int:
    rows = list(iter_jsonl(path))
    if not rows:
        _refuse("CORPUS_EMPTY", path.relative_to(ROOT).as_posix(), "contains no fixtures; an empty file proves nothing", "restore the corpus")
        return 1
    failures = 0
    names = {r.get("name") for _, r in rows}
    # the model's fixture map: every must-fail fixture present, expect_only where mandated
    for fname, fx in (pol.codes.get("fixtures") or {}).items():
        if str(fx.get("corpus", "")).endswith("must-fail.jsonl"):
            if fname not in names:
                failures += 1
                print(f"FAIL fixture-map name={fname} the model names this fixture and the corpus does not carry it")
            elif fx.get("expect_only"):
                row = next(r for _, r in rows if r.get("name") == fname)
                if not row.get("expect_only"):
                    failures += 1
                    print(f"FAIL fixture-map name={fname} the model requires expect_only and the fixture does not set it")
    for n, row in rows:
        expected = row.get("expect_code")
        if expected not in pol.declared:
            failures += 1
            print(f"FAIL fail line={n} name={row.get('name')} expect_code={expected} is not a declared code")
            continue
        index = Index(list(row.get("context") or []) + [row.get("event")])
        codes, reached = check_event(row.get("event"), pol, index, humans)
        owners = pol.emitted_by.get(expected, set())
        if expected not in codes:
            unreached = _owner_checks(owners) - reached
            reason = f" (checks not reached: {','.join(sorted(unreached))})" if unreached else ""
            failures += 1
            print(f"FAIL fail line={n} name={row.get('name')} expected={expected} got={','.join(sorted(codes)) or 'none'}{reason}")
        elif row.get("expect_only") and codes != {expected}:
            failures += 1
            print(f"FAIL fail line={n} name={row.get('name')} expected only {expected}, got={','.join(sorted(codes))}")
    if not quiet:
        print(f"must-fail: {len(rows)} fixtures, {failures} failed")
    return 1 if failures else 0


def _owner_checks(owners: set[str]) -> set[str]:
    m = {"schema": "schema", "denylist": "denylist", "semantics": "rules", "lineage": "lineage", "producer": "producer"}
    return {m[o] for o in owners if o in m}


def validate_file(path: Path, pol: Policy, humans: set[str], strict: bool, quiet: bool) -> int:
    rows = list(iter_jsonl(path))
    if not rows:
        _refuse("CORPUS_EMPTY", path.as_posix(), "contains no events", "supply a non-empty JSONL file")
        return 1
    events = [r.get("event", r) for _, r in rows]
    index = Index(events)
    failed = 0
    for (n, _), e in zip(rows, events):
        codes, _ = check_event(e, pol, index, humans)
        if codes:
            failed += 1
            eid = (((e or {}).get("event") or {}).get("event_id"))
            for c in sorted(codes):
                print(f"FAIL {c} line={n} event_id={eid}")
    if not quiet:
        print(f"total={len(events)} passed={len(events) - failed} failed={failed}")
    return 1 if failed else 0


# ---------------------------------------------------------------------------
# self-test
# ---------------------------------------------------------------------------


def self_test(pol: Policy, humans: set[str]) -> int:
    """Break the runner in memory and assert each break is caught.

    Design gate 1: a constraint is not done until a test fails when it is
    removed. Each case removes one check's input and asserts the fixture that
    check protects stops failing.
    """
    import copy

    rows = list(iter_jsonl(MUST_FAIL))
    by_name = {r.get("name"): r for _, r in rows}

    def fires(name: str, p: Policy) -> set[str]:
        row = by_name[name]
        index = Index(list(row.get("context") or []) + [row.get("event")])
        codes, _ = check_event(row.get("event"), p, index, humans)
        return codes

    cases = []
    # 1. dropping a denylist group stops the group's code
    p = copy.deepcopy(pol)
    p.types["EXTRACT_EVENT"]["payload_must_not_contain"] = [
        g for g in p.types["EXTRACT_EVENT"]["payload_must_not_contain"] if g["code"] != "EXTRACT_HAS_REVIEW_STATE"
    ]
    cases.append(("drop the review_state denylist group", "extract-carries-review-state", "EXTRACT_HAS_REVIEW_STATE", p))
    # 2. emptying producer authority for IDENTITY lets a connector mint a cluster
    p = copy.deepcopy(pol)
    p.producer["effective"]["IDENTITY_EVENT.CLUSTER"] = ["connector-*"]
    cases.append(("grant connector-* IDENTITY_EVENT.CLUSTER", "cluster-minted-by-connector", "PRODUCER_NOT_ALLOWED", p))
    # 3. removing the D5 required parent stops SUBJECT_NOT_AUTHORIZED
    p = copy.deepcopy(pol)
    p.lineage["required_parents"]["PROBE_EVENT"].pop("RUN_START", None)
    p.lineage["required_by_subtype"]["PROBE_EVENT"]["RUN_START"] = False
    cases.append(("drop the RUN_START required parent", "run-start-without-permitted", "SUBJECT_NOT_AUTHORIZED", p))
    # 4. forgetting the GENERATED provenance stops GENERATED_CITED_AS_OBSERVED
    p = copy.deepcopy(pol)
    p.generated_selectors = set()
    cases.append(("forget GENERATED provenance", "generated-permutation-cited-as-observed", "GENERATED_CITED_AS_OBSERVED", p))
    # 5. dropping the nested hit code stops LAYER_COLLAPSE_NESTED
    p = copy.deepcopy(pol)
    p.semantics["payload_denylist"]["nested_hit_code"] = None
    cases.append(("drop the nested hit code", "nested-layer-collapse", "LAYER_COLLAPSE_NESTED", p))

    failures = 0
    for label, fixture, code, broken in cases:
        if fixture not in by_name:
            print(f"SELF-TEST FAIL {label}: fixture {fixture} not in corpus")
            failures += 1
            continue
        before = fires(fixture, pol)
        after = fires(fixture, broken)
        if code not in before:
            print(f"SELF-TEST FAIL {label}: {code} does not fire on the intact runner")
            failures += 1
        elif code in after:
            print(f"SELF-TEST FAIL {label}: {code} still fires after the break, so the check is not load-bearing")
            failures += 1
    if failures:
        return 1
    print(f"validate --self-test ok: {len(cases)} deliberate breaks, {len(cases)} caught")
    return 0


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Validate PSE events against the generated schema and policy.")
    ap.add_argument("--file", help="a JSONL file of events, or of {event: ...} rows, treated as one case")
    ap.add_argument("--must-pass", nargs="?", const=str(MUST_PASS), help="grade the must-pass corpus")
    ap.add_argument("--must-fail", nargs="?", const=str(MUST_FAIL), help="grade the must-fail corpus")
    ap.add_argument("--kernel", action="store_true", help="generated artifacts current, both corpora graded, self-test")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--strict", action="store_true", help="accepted for parity with the precedent; every code here is a failure")
    ap.add_argument("--human-identity", action="append", default=[], help="a named human producer; repeatable")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    humans = set(args.human_identity) or set(DEFAULT_HUMANS)

    if args.kernel:
        import subprocess

        rc = subprocess.run([sys.executable, "tools/generate_pse.py", "--check", "--quiet"], cwd=ROOT).returncode
        if rc:
            return rc
        rc = subprocess.run([sys.executable, "tools/build_corpus.py", "--check", "--quiet"], cwd=ROOT).returncode
        if rc:
            return rc
        pol = load_policy()
        rc = grade_must_pass(MUST_PASS, pol, humans, True) | grade_must_fail(MUST_FAIL, pol, humans, True)
        if rc:
            return rc
        rc = self_test(pol, humans)
        if rc:
            return rc
        n_pass = sum(1 for _ in iter_jsonl(MUST_PASS))
        n_fail = sum(1 for _ in iter_jsonl(MUST_FAIL))
        if not args.quiet:
            print(
                f"validate ok: generated artifacts current, {n_pass} must-pass events clean, "
                f"{n_fail} must-fail fixtures refused for the expected reason"
            )
        return 0

    pol = load_policy()
    if args.self_test:
        return self_test(pol, humans)
    rc = 0
    if args.file:
        rc |= validate_file(Path(args.file), pol, humans, args.strict, args.quiet)
    if args.must_pass:
        rc |= grade_must_pass(Path(args.must_pass), pol, humans, args.quiet)
    if args.must_fail:
        rc |= grade_must_fail(Path(args.must_fail), pol, humans, args.quiet)
    if not (args.file or args.must_pass or args.must_fail):
        ap.print_help()
        return 2
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
