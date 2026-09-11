#!/usr/bin/env python3
"""Layer model self-lint: the one file the schema and policy are generated from.

`spec/layer-model.yaml` is rank 3 and Class B. Everything the PSE schema and the
policy pack say about event types, subtypes, discriminators, confidence,
lineage, producer authority, required fields and denylists is generated from
it at Step 7. A defect here is a defect in every generated artifact at once, and
a defect the generated artifacts cannot detect because they agree with their
source by construction. This tool is the check that sits upstream of them.

Each check guards a defect that has either already occurred in a precedent or
is one edit away in this file:

  L-01  The type count drifts from D6's stamped nine. A tenth type is a Class D
        change wearing a Class B diff.
  L-02  The version label or the derived_from label changes without the bump
        D7 and AGENTS.md section 3 require, or the envelope consts disagree
        with the header.
  L-03  A type omits a governed section, so the generator emits a schema branch
        with no denylist, no lineage rule, or no producer authority for it.
  L-04  A subtype's discriminator const differs from its name, two subtypes
        share a const, or one type uses two discriminator paths. That is the
        zmeta-event-1.0 eventSubtypeConsistency mechanism failing silently.
  L-05  A layer is named by a type but not defined, defined but unused, or
        states a never_carries rule that a type in that layer does not prohibit.
  L-06  A field is both required and prohibited for the same subtype, which
        makes every event of that subtype unwritable.
  L-07  A type omits a credential-value name from its denylist. CR-3 says the
        value never appears in a log, and the event log is a log.
  L-08  The global confidence decision and a per-type rule disagree, which is
        how a half-reversed decision ships.
  L-09  A lineage parent names a type or subtype that does not exist, or a
        required parent is outside the allowed set.
  L-10  PROBE_EVENT RUN_START stops requiring a COLLECT_EVENT PERMITTED parent.
        That single line is what makes D5's gate structural, and this check
        exists so deleting it fails the gate.
  L-11  A subtype is its own only required parent, so no first event can exist.
  L-12  A wildcard producer appears on a human-only type. zmeta-spec: an
        unnamed authoritative track is an injection path. Here an unnamed
        identity assertion is.
  L-13  COLLECT_EVENT gains a second producer, which is a second gate.
  L-14  A code is referenced and never declared, or declared and never
        referenced. Free-text diagnostics are the failure the vocabulary exists
        to prevent, and a dead code is a check nobody wrote.
  L-15  One of the sixteen named fixtures has no mapping to the rule that
        fires it, or the mapping points at a rule that does not exist.
  L-16  A stratum is outside RT-1's set, or a payload that carries subject
        values sits in a surviving stratum. RT-2 calls that a defect, not a
        judgment call.
  L-17  A payload's egress declaration disagrees with EG-5's rule for its
        stratum.
  L-18  The compatibility claim AGENTS.md section 1 forbids appears in the file.
  L-19  The lineage matrix or the producer index restates the per-type source
        and drifts from it. Restating without reconciling is the ZMeta habit
        Step 5 exists to avoid.
  L-20  A pinned invariant moves. Each row of PINNED is a declaration that is
        load-bearing somewhere downstream and that nothing else in this file
        reads, which is the shape a 2026-09-03 review found on every one of
        them: envelope.required, the closure flag, the reserved key, LINK's
        accepted const, IDENTITY's member minimum, cross-case lineage, the
        shred receipt, and the credential state enum.
  L-21  A type's required_envelope_fields stops being a superset of
        envelope.required, so a type drops a field D4 or gate 7 depends on
        while the envelope still claims it.
  L-22  The payload denylist stops being recursive. One word makes every
        denylist in the file recursive and it is generated into
        policy/semantics.yaml, so nothing else would notice.
  L-23  The egress rule widens. strata_crossing_to_local was checked against
        itself, so widening it plus the flags it governs passed clean and would
        have generated a policy letting stratum-1 case material cross to LOCAL
        (EG-2). The environments list and the run environment are pinned for
        the same reason (EG-6).
  L-24  An enum this file names as Class F by effect widens. `retain` on
        bystander_disposition and S5 on subject_class are the two one-line
        diffs CLAUDE.md gate 2 names by example.
  L-25  One prohibited name appears in two groups of one type under different
        codes. The group's code is what the generated policy emits and what a
        must-fail fixture asserts, and a name firing two codes cannot satisfy
        a fixture's expect_only.
  L-26  A rule states a condition in English and carries no machine-readable
        `when` and `requires`, so the schema generator has to invent the
        condition. Or `requires` names a field the type does not declare, or
        names a field absent from payload.required for the subtypes an
        unconditional `when` selects.
  L-27  A fixture reaches no code at all, so it can be mapped to any code and
        pass, or a D2 or D5 fixture omits expect_only (THE-GAMEPLAN 2.4).
  L-28  The generation map names a source path that resolves to nothing, or
        omits one of the five Step 7 outputs. The map is the second half of
        Step 5's done-condition and was entirely unread.
  L-29  A layer's may_carry drifts from the payload fields of the types in that
        layer, in either direction. policy/semantics.yaml is generated from
        this section, so a token that is not a field is a token the generator
        cannot use.
  L-30  ADJUDICATE_EVENT's allowed_targets and required_parents disagree about
        which parent types a disposition may act on, or a type whose rules cite
        allowed_targets has none. LM-R11 records what the file has not decided;
        this check is what stops it shipping undecided.
  L-31  A rule the doctrine turns on is missing by name. The D5 pair on
        PROBE_EVENT and the reason constraint on the two stratum-2 payloads
        that carry free text.
  L-32  A type's violation_codes lists a code no rule of that type fires. The
        check ran in one direction only, so three types carried a code they
        never emit and six carried the same relationships without listing it.
  L-33  lineage.policy_shape is absent or stops requiring subtype granularity,
        so a generator following the precedent's type-granular shape drops
        required_parents and the D5 line lands in no policy.
  L-34  A violation_codes entry carries a key outside the five, or no
        fires_when. Both are the signature of an unquoted flow mapping whose
        sentence contains a comma: YAML ends the value at the comma and turns
        the rest into keys. The file still parses, so every other check passes
        and the compiled policy documents the code with half a sentence. This
        was found on 2026-09-08 with 17 of 57 entries truncated.

`--self-test` breaks the loaded model in memory once per direction a check
guards and asserts the refusal. doctrine/HYGIENE.md section 2: when a check is
written, break the corpus deliberately and confirm the check refuses.

The assertion is that the expected code fired AND, for a mutation whose damage
does not cascade, that it was the only code that fired. Membership alone is the
fixture-runner defect THE-GAMEPLAN section 2.4 says PSE fixes on day one, and it
let eight of an earlier nineteen mutations pass on codes they never claimed to
exercise. A mutation that genuinely cascades sets expect_only False and states
why, which is a sentence a reader can check rather than a silence.

Exit codes: 0 clean, 1 violations found, 2 the model could not be read.
"""

from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print(
        "REFUSED LAYER_MODEL_UNREADABLE\n"
        "  what:  PyYAML is not installed, so the model cannot be parsed\n"
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
MODEL = ROOT / "spec" / "layer-model.yaml"
GATE = "layer-model"

#: D6, stamped 2026-08-27 in doctrine/DOCTRINE_STATUS.md.
EXPECTED_TYPE_COUNT = 9
#: D7.
EXPECTED_VERSION = "pse-event-0.1"
EXPECTED_STATUS = "Unlocked"
#: D1.
EXPECTED_DERIVED_FROM = "zmeta-event-1.0"

#: Every type declares each of these.
TYPE_SECTIONS = (
    "layer",
    "subtypes",
    "required_envelope_fields",
    "payload",
    "confidence",
    "lineage",
    "producer_authority",
    "retention",
    "egress",
    "violation_codes",
)
PAYLOAD_SECTIONS = ("required", "fields", "prohibited", "rules")

#: CR-3. Names a credential value travels under, and the argv family a filled
#: command line travels under. Prohibited on every type. The argv four were on
#: PROBE_EVENT alone until 2026-09-03, while CREDENTIAL_VALUE_IN_PAYLOAD's own
#: declaration covered every payload, so eight of nine types would have generated
#: a schema branch that accepts a filled argv. CR-3 is one sentence and this is
#: the whole of it.
CREDENTIAL_VALUE_NAMES = (
    "sessionid", "session_id", "cookie", "token", "password", "secret",
    "argv", "command", "credential", "credential_value",
)

#: Types that accept only a named human identity. No wildcard, ever.
HUMAN_ONLY_TYPES = ("AUTHORIZE_EVENT", "IDENTITY_EVENT", "ADJUDICATE_EVENT", "ASSESS_EVENT")

#: The gate's single producer.
COLLECT_PRODUCER = "runner-subject-guard"

#: RT-1 strata.
STRATA = {0, 1, 2, 3, 4, "T"}
#: RT-2: a surviving stratum may not hold a subject-derived value.
SURVIVING_STRATA = {2, 3}
#: EG-5's table, pinned here rather than read from the model. L-17 checked every
#: per-type egress flag against egress.strata_crossing_to_local, and that list was
#: itself unchecked, so widening the rule and the flags it governs together passed
#: clean. EG-2 has no later date on which it can be decided.
CROSSING_STRATA = {2, 3, 4}
#: EG-1's two environments. The FOUNDATION draft's three roles are LM-R3's
#: rejected alternative and DV-04 records the replacement.
ENVIRONMENTS = ["LOCAL", "ISOLATED"]
#: EG-6. A run executes from ISOLATED and a run from LOCAL is refused, not
#: annotated, so this enum has one member.
RUN_ENVIRONMENT = ["ISOLATED"]

#: SS-10, R8. Closed at v0.1. SS-10 defines `retain` and refuses it, and reaching
#: it is a Class F ratification with a dated stamp.
BYSTANDER_DISPOSITIONS = ["count_only", "refuse"]
#: SS-1's set minus S5, which SS-1 marks not authorizable.
AUTHORIZABLE_CLASSES = ["S0", "S1", "S2", "S3", "S4", "N0", "L0"]
#: CR-2's table. LM-R9 records the fourth value an earlier draft of the model
#: wrote here and the stamp that would be needed to add it.
CREDENTIAL_STATES = ["active", "quarantined", "burned"]
#: RT-9's five checks, each once. A receipt of [1, 1, 1, 1, 1] is one check
#: counted five times, which RT-9 says is not a check.
SHRED_CHECKS = [1, 2, 3, 4, 5]

#: The only keys a violation_codes entry may carry. Anything else means the
#: entry was written as an unquoted YAML flow mapping whose fires_when sentence
#: contains a comma: in flow context the comma starts a new mapping entry, so
#: the sentence is truncated at it and the remainder becomes null-valued keys.
#: The parse succeeds, so nothing else notices, and the compiled policy carries
#: a code documented by half a sentence.
CODE_ENTRY_KEYS = {"code", "severity", "since", "fires_when", "emitted_by"}
#: The envelope's required set. D4 keys the crypto-shred on case_id.
ENVELOPE_REQUIRED = ["pse_version", "derived_from", "case_id", "event", "source", "payload"]

#: The five Step 7 outputs. pse.generates names every one or the generation map,
#: which is the second half of Step 5's done-condition, is incomplete.
EXPECTED_GENERATED = (
    "schema/pse-event-0.1.schema.json",
    "policy/semantics.yaml",
    "policy/lineage.yaml",
    "policy/producer-authority.yaml",
    "policy/violation-codes.yaml",
)

#: THE-GAMEPLAN section 2.4: all D2 and D5 fixtures set expect_only.
EXPECT_ONLY_FIXTURES = (
    "hint-cited-as-email",
    "generated-permutation-cited-as-observed",
    "account-anchored-on-handle",
    "run-against-unauthorized-subject",
    "scope-drift-three-hops",
    "run-without-purpose-binding",
)

#: Rules named here because doctrine turns on them and a rename or a deletion
#: would otherwise leave a generic gap. (type, rule name, the code it fires).
REQUIRED_RULES = (
    ("PROBE_EVENT", "run_permitted", "SUBJECT_NOT_AUTHORIZED"),
    ("PROBE_EVENT", "run_matches_its_decision", "SUBJECT_NOT_AUTHORIZED"),
    ("COLLECT_EVENT", "purpose_bound", "CASE_PURPOSE_UNBOUND"),
    ("AUTHORIZE_EVENT", "reason_names_no_subject", "REASON_NAMES_SUBJECT"),
    ("SYSTEM_EVENT", "reason_names_no_subject", "REASON_NAMES_SUBJECT"),
)

#: Keys a node may carry the code it fires under.
CODE_KEYS = ("code", "violation_code", "nested_hit_code")

#: Legal `when` forms on a payload rule. Documented beside the notation
#: paragraph in the model.
WHEN_FIELD_KEYS = ({"field", "equals"}, {"field", "contains"}, {"field", "present"})

#: Pinned invariants: (dotted path, expected value, code, what, moves, only_when).
#: A row is here where the declaration is load-bearing downstream and nothing
#: else in this file reads it, so it could be changed or deleted without a
#: refusal. `only_when` is a (path, value) pair or None; a row with one is
#: checked only while that condition holds, which is how the reserved key moves
#: with the confidence mode rather than against it.
PINNED = (
    (
        "envelope.required", ENVELOPE_REQUIRED, "LM_PINNED_INVARIANT",
        "the envelope's required-field list is what every type's "
        "required_envelope_fields is measured against, and D4 keys the crypto-shred "
        "on case_id: an event without one is an event the sweep cannot reach",
        "restore the list. Adding or removing a field is a Class D change needing a "
        "version bump and a divergence-register entry, and this tool's "
        "ENVELOPE_REQUIRED moves in the same commit",
        None,
    ),
    (
        "envelope.additional_properties", False, "LM_PINNED_INVARIANT",
        "additionalProperties false at every level is what makes an unknown key a "
        "refusal rather than a silent extension. It is also the half of the name "
        "denylist's residual that keeps a re-keyed field from arriving at all",
        "set it back to false, or state the new shape as a divergence and carry the "
        "residual it opens in envelope.payload_denylist_recursion",
        None,
    ),
    (
        "envelope.reserved_refused", ["confidence"], "LM_CONFIDENCE_INCONSISTENT",
        "confidence.mode is prohibited_everywhere and the reserved key list does not "
        "say so. The generator emits the confidence key as false from this list, and an "
        "empty list lets it in as an unknown property on a permissive validator",
        "restore [confidence], or reverse the decision at all five sites the confidence "
        "section names, in the order it names them",
        ("confidence.mode", "prohibited_everywhere"),
    ),
    (
        "event_types.LINK_EVENT.payload.fields.accepted.const", False, "LM_PINNED_INVARIANT",
        "a LINK is always a proposal. accepted is required and const false so a "
        "proposal cannot be read as accepted by omission, and fixture 12 asserts it",
        "set const back to false. Acceptance is an IDENTITY_EVENT by a named human "
        "(design section 8.2 item 4)",
        None,
    ),
    (
        "event_types.IDENTITY_EVENT.payload.fields.members.min_items", 2, "LM_PINNED_INVARIANT",
        "one account is not an identity assertion. The members_min_two rule asserts "
        "this number and read it from nowhere",
        "set min_items back to 2, or change the rule and its fixture in the same commit",
        None,
    ),
    (
        "lineage.based_on.same_case_required", True, "LM_PINNED_INVARIANT",
        "cross-case lineage does not exist, because the shred is per case. A parent in "
        "another case is a pointer the sweep will not follow and will not clear",
        "set it back to true. LINEAGE_CROSS_CASE is the code that fires when an event "
        "breaks it at runtime",
        None,
    ),
    (
        "event_types.SYSTEM_EVENT.payload.fields.checks_passed.const", SHRED_CHECKS,
        "LM_PINNED_INVARIANT",
        "the shred receipt proves all five RT-9 checks ran. min_items 5 over an enum of "
        "1 to 5 accepts [1, 1, 1, 1, 1], which is one check counted five times, and RT-9 "
        "says a check that can pass for a reason other than the one claimed is not a check",
        "set const back to [1, 2, 3, 4, 5]. RT-10 makes this receipt the proof the shred "
        "happened, so a weaker shape is a weaker proof",
        None,
    ),
    (
        "event_types.SYSTEM_EVENT.payload.fields.state.enum_by_subtype.CREDENTIAL_STATE",
        CREDENTIAL_STATES, "LM_PINNED_INVARIANT",
        "CR-2's table fixes the credential state enum at three values and this file is "
        "rank 3. Writing a value rank 1 does not carry inverts the rank order",
        "restore CR-2's three, or add the value to CR-2 first with a dated stamp in "
        "doctrine/DOCTRINE_STATUS.md and move CREDENTIAL_STATES here in the same commit. "
        "LM-R9 holds the open question",
        None,
    ),
    (
        "event_types.COLLECT_EVENT.payload.fields.bystander_disposition.enum",
        BYSTANDER_DISPOSITIONS, "LM_CLASS_F_ENUM_WIDENED",
        "the bystander disposition set is closed at v0.1. SS-10 defines `retain` and "
        "refuses it, and the model names widening this enum as Class F by effect. "
        "CLAUDE.md gate 2 names this exact diff as one that reads as Class B",
        "restore [count_only, refuse]. A wider set needs a Class F ratification with a "
        "dated stamp in doctrine/DOCTRINE_STATUS.md, authored by the ratifier, and this "
        "tool's BYSTANDER_DISPOSITIONS moves in that same commit",
        None,
    ),
    (
        "event_types.AUTHORIZE_EVENT.payload.fields.subject_class.enum",
        AUTHORIZABLE_CLASSES, "LM_CLASS_F_ENUM_WIDENED",
        "SS-1 marks S5 not authorizable, so an authorization naming it is an "
        "authorization for a class no authorization reaches. Widening this enum is "
        "Class F by effect whatever the diff looks like",
        "restore SS-1's authorizable set. A wider set needs a Class F ratification with "
        "a dated stamp in doctrine/DOCTRINE_STATUS.md, authored by the ratifier, and "
        "this tool's AUTHORIZABLE_CLASSES moves in that same commit",
        None,
    ),
    (
        "event_types.ASSESS_EVENT.payload.fields.subject_class.enum",
        AUTHORIZABLE_CLASSES, "LM_CLASS_F_ENUM_WIDENED",
        "SS-18 puts the class on the finding itself, and a finding cannot have come "
        "from a class SS-1 marks not authorizable",
        "restore SS-1's authorizable set, and keep it equal to AUTHORIZE_EVENT's. A "
        "wider set needs a Class F ratification with a dated stamp",
        None,
    ),
    (
        "egress.environments", ENVIRONMENTS, "LM_EGRESS_PINNED",
        "EG-1 defines two environments and the boundary between them is which one may "
        "execute a connector. The FOUNDATION draft's three roles are LM-R3's rejected "
        "alternative, and restoring them here reverses a rank-1 criterion silently",
        "restore [LOCAL, ISOLATED]. A third environment is a doctrine change to EG-1 "
        "before it is an edit here",
        None,
    ),
    (
        "egress.strata_crossing_to_local", [2, 3, 4], "LM_EGRESS_PINNED",
        "EG-2: the case store lives in ISOLATED and no stratum-0 or stratum-1 object "
        "crosses to LOCAL. This list was the only source L-17 read, so widening it and "
        "the per-type flags it governs together passed clean and would have generated a "
        "policy that lets case material cross",
        "restore [2, 3, 4]. EG-2 has no later date on which it can be decided, so "
        "widening it is a doctrine change first. RT-18's disclosure export is the named "
        "exception and goes to an agency rather than to LOCAL",
        None,
    ),
    (
        "envelope.fields.source.fields.environment.enum", ENVIRONMENTS, "LM_EGRESS_PINNED",
        "every event names the environment it was written in, out of EG-1's two. A "
        "wider enum lets an event claim an environment the doctrine does not define",
        "restore [LOCAL, ISOLATED], and keep it equal to egress.environments",
        None,
    ),
    (
        "event_types.PROBE_EVENT.payload.fields.egress.fields.environment.enum",
        RUN_ENVIRONMENT, "LM_EGRESS_PINNED",
        "EG-6: a run from the wrong environment is refused rather than logged, because "
        "a run that already reached a platform cannot be un-run. LOCAL in this enum "
        "turns the refusal into an annotation",
        "restore [ISOLATED]. The refusal is EGRESS_ENVIRONMENT_REFUSED and "
        "environment_is_isolated is the rule that fires it",
        None,
    ),
)

#: docs/THE-GAMEPLAN.md section 2.3, fourteen plus the two added when the
#: shapes exist.
REQUIRED_FIXTURES = (
    "hint-cited-as-email",
    "generated-permutation-cited-as-observed",
    "account-anchored-on-handle",
    "run-against-unauthorized-subject",
    "scope-drift-three-hops",
    "absence-claimed-without-canary",
    "extract-carries-confidence",
    "extract-carries-review-state",
    "nested-layer-collapse",
    "unregistered-selector-type",
    "cluster-minted-by-connector",
    "link-arrives-accepted",
    "extract-no-lineage",
    "run-without-purpose-binding",
    "cluster-carries-rollup-confidence",
    "merge-circularity",
)

DIVERGENCE_DISPOSITIONS = {"INVERT", "REPLACE", "DROP", "NEW"}

#: AGENTS.md section 1. Assembled so this file does not itself carry the string.
FORBIDDEN_CLAIM = "ZMeta-" + "compatible"

#: Token standing for "a named human identity from the session" when producer
#: sets are compared.
HUMAN = "<human identity>"


class Finding:
    __slots__ = ("code", "where", "detail", "moves")

    def __init__(self, code: str, where: str, detail: str, moves: str):
        self.code = code
        self.where = where
        self.detail = detail
        self.moves = moves

    def render(self) -> str:
        return (
            f"REFUSED {self.code}\n"
            f"  where: {self.where}\n"
            f"  what:  {self.detail}\n"
            f"  moves: {self.moves}"
        )


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _as_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _per_subtype(value, subtypes: list[str]) -> dict:
    """Expand a scalar-or-map declaration to one value per subtype."""
    if isinstance(value, dict):
        return {s: value.get(s) for s in subtypes}
    return {s: value for s in subtypes}


def _field_names(fields) -> set[str]:
    """Every key under a `fields` map, at any depth."""
    out: set[str] = set()
    if not isinstance(fields, dict):
        return out
    for name, spec in fields.items():
        out.add(name)
        if isinstance(spec, dict):
            out |= _field_names(spec.get("fields"))
            items = spec.get("items")
            if isinstance(items, dict):
                out |= _field_names(items.get("fields"))
    return out


def _prohibited_names(type_def: dict) -> set[str]:
    out: set[str] = set()
    for group in _as_list(type_def.get("payload", {}).get("prohibited")):
        if isinstance(group, dict):
            out |= set(_as_list(group.get("names")))
    return out


def _resolve(model: dict, dotted: str):
    node = model
    for part in dotted.split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            return None
    return node


def _resolve_glob(model: dict, dotted: str) -> list:
    """Every node a dotted path reaches, with `*` standing for every key."""
    nodes = [model]
    for part in dotted.split("."):
        nxt = []
        for node in nodes:
            if part == "*":
                if isinstance(node, dict):
                    nxt.extend(node.values())
            elif isinstance(node, dict) and part in node:
                nxt.append(node[part])
        nodes = nxt
        if not nodes:
            return []
    return nodes


def _node_codes(node) -> set[str]:
    """Codes a node declares, under any of the keys a code travels under."""
    out: set[str] = set()
    if isinstance(node, str):
        out.add(node)
    elif isinstance(node, dict):
        for key in CODE_KEYS:
            if node.get(key):
                out.add(node[key])
    elif isinstance(node, list):
        for item in node:
            out |= _node_codes(item)
    return out


def _when_valid(when) -> bool:
    """Whether a rule's `when` is one of the forms the notation paragraph names."""
    if when in ("always", "runtime"):
        return True
    if not isinstance(when, dict):
        return False
    keys = set(when.keys())
    if keys == {"subtype"}:
        return bool(_as_list(when["subtype"]))
    if keys == {"all_of"}:
        alts = _as_list(when["all_of"])
        return bool(alts) and all(_when_valid(a) for a in alts)
    if keys in WHEN_FIELD_KEYS:
        return isinstance(when.get("field"), str)
    return False


def _when_subtypes(when, subtype_names: list[str]):
    """Subtypes a `when` selects unconditionally, or None when it is conditional.

    Only `always` and a bare `subtype` form select unconditionally. A field
    condition or `runtime` depends on a value, so `requires` under one of those
    cannot be checked against the unconditional required-field list.
    """
    if when == "always":
        return list(subtype_names)
    if isinstance(when, dict) and set(when.keys()) == {"subtype"}:
        return _as_list(when["subtype"])
    return None


def _producer_sets(type_name: str, type_def: dict) -> dict[str, set[str]]:
    """(subtype -> set of producers) from a type's producer_authority block.

    Type-level wildcards, named and human_identity_only apply to every subtype
    unless by_subtype names that subtype, in which case the by_subtype entry
    is the whole authority for it. human_identity_only in a by_subtype entry
    defaults to the type-level value.
    """
    pa = type_def.get("producer_authority", {}) or {}
    subtypes = list((type_def.get("subtypes") or {}).keys())
    base = set(_as_list(pa.get("wildcards"))) | set(_as_list(pa.get("named")))
    if pa.get("human_identity_only"):
        base.add(HUMAN)
    out = {s: set(base) for s in subtypes}
    for s, entry in (pa.get("by_subtype") or {}).items():
        if s not in out:
            continue
        entry = entry or {}
        producers = set(_as_list(entry.get("wildcards"))) | set(_as_list(entry.get("named")))
        human = entry.get("human_identity_only", pa.get("human_identity_only", False))
        if human:
            producers.add(HUMAN)
        out[s] = producers
    return out


def _expand_index(refs: list, event_types: dict) -> set[tuple[str, str]]:
    """TYPE or TYPE.SUBTYPE references into a set of (type, subtype) pairs."""
    out: set[tuple[str, str]] = set()
    for ref in _as_list(refs):
        if not isinstance(ref, str):
            continue
        if "." in ref:
            t, s = ref.split(".", 1)
            out.add((t, s))
        else:
            for s in (event_types.get(ref, {}).get("subtypes") or {}):
                out.add((ref, s))
    return out


# ---------------------------------------------------------------------------
# the checks
# ---------------------------------------------------------------------------


def check(model: dict, text: str) -> list[Finding]:
    f: list[Finding] = []
    pse = model.get("pse") or {}
    envelope = model.get("envelope") or {}
    layers = model.get("layers") or {}
    types = model.get("event_types") or {}
    conf = model.get("confidence") or {}
    lineage = model.get("lineage") or {}
    producers = model.get("producer_authority") or {}
    egress = model.get("egress") or {}
    codes_section = model.get("violation_codes") or {}

    # L-18. Checked first and on the raw text, because the claim can hide in a
    # comment where no structural check reaches.
    if FORBIDDEN_CLAIM in text:
        f.append(
            Finding(
                "LM_FORBIDDEN_STRING",
                "spec/layer-model.yaml",
                "the file claims upstream compatibility. PSE is a private dialect and "
                "AGENTS.md section 1 forbids the claim",
                "remove the claim; describe PSE as derived from zmeta-event-1.0",
            )
        )

    # L-01
    if len(types) != EXPECTED_TYPE_COUNT:
        f.append(
            Finding(
                "LM_TYPE_COUNT",
                f"event_types ({len(types)} declared)",
                f"D6 stamps the event-type set at {EXPECTED_TYPE_COUNT}. A different count "
                "is a Class D change and needs a version bump and a divergence entry",
                f"restore the set to {EXPECTED_TYPE_COUNT}, or ratify a new count in "
                "doctrine/DOCTRINE_STATUS.md and bump pse.version",
            )
        )

    # L-02
    if pse.get("version") != EXPECTED_VERSION:
        f.append(
            Finding(
                "LM_VERSION",
                f"pse.version = {pse.get('version')!r}",
                f"D7 stamps the label as {EXPECTED_VERSION}",
                "restore the label, or ratify the bump in doctrine/DOCTRINE_STATUS.md "
                "and update this tool's EXPECTED_VERSION in the same change",
            )
        )
    if pse.get("derived_from") != EXPECTED_DERIVED_FROM:
        f.append(
            Finding(
                "LM_VERSION",
                f"pse.derived_from = {pse.get('derived_from')!r}",
                f"D1 forks {EXPECTED_DERIVED_FROM} and nothing else",
                "restore the value",
            )
        )
    if pse.get("status") != EXPECTED_STATUS:
        f.append(
            Finding(
                "LM_VERSION",
                f"pse.status = {pse.get('status')!r}",
                f"D7 says {EXPECTED_STATUS}, so a matching number is not read as a "
                "matching commitment",
                "restore the status, or ratify the lock",
            )
        )
    env_fields = envelope.get("fields") or {}
    for field, expected in (("pse_version", pse.get("version")), ("derived_from", pse.get("derived_from"))):
        const = (env_fields.get(field) or {}).get("const")
        if const != expected:
            f.append(
                Finding(
                    "LM_VERSION",
                    f"envelope.fields.{field}.const = {const!r}",
                    f"disagrees with pse.{'version' if field == 'pse_version' else 'derived_from'} "
                    f"= {expected!r}, so the generated schema would refuse every event",
                    "make the two agree",
                )
            )
    readings = {r.get("id") for r in _as_list(pse.get("readings")) if isinstance(r, dict)}
    if "LM-R1" not in readings:
        f.append(
            Finding(
                "LM_READING_MISSING",
                "pse.readings",
                "the header does not record that the nine-type enumeration is an agent "
                "reading of D6 awaiting confirmation",
                "add the LM-R1 reading, or replace it with the operator's confirmation stamp",
            )
        )

    layer_names = set(layers.keys())
    used_layers: set[str] = set()
    all_subtypes = 0

    for tname, tdef in types.items():
        where = f"event_types.{tname}"
        if not isinstance(tdef, dict):
            f.append(Finding("LM_TYPE_SECTION_MISSING", where, "the type is not a mapping", "declare the type's sections"))
            continue

        # L-03
        missing = [s for s in TYPE_SECTIONS if s not in tdef]
        if missing:
            f.append(
                Finding(
                    "LM_TYPE_SECTION_MISSING",
                    where,
                    f"missing governed section(s): {', '.join(missing)}. The generator "
                    "would emit this type with no rule for what is missing",
                    "declare every section in TYPE_SECTIONS, even if a list is empty",
                )
            )
            continue
        payload = tdef.get("payload") or {}
        missing_p = [s for s in PAYLOAD_SECTIONS if s not in payload]
        if missing_p:
            f.append(
                Finding(
                    "LM_TYPE_SECTION_MISSING",
                    f"{where}.payload",
                    f"missing payload section(s): {', '.join(missing_p)}",
                    "declare required, fields, prohibited and rules, even if empty",
                )
            )

        subtypes = tdef.get("subtypes") or {}
        subtype_names = list(subtypes.keys())
        all_subtypes += len(subtype_names)
        if not subtype_names:
            f.append(Finding("LM_SUBTYPE_DISCRIMINATOR", where, "the type declares no subtypes", "declare at least one subtype with a discriminator"))

        # L-04
        consts: dict[str, str] = {}
        paths: set[str] = set()
        for sname, sdef in subtypes.items():
            disc = (sdef or {}).get("discriminator") or {}
            path, const = disc.get("path"), disc.get("const")
            swhere = f"{where}.subtypes.{sname}"
            if not isinstance(path, str) or not path.startswith("payload."):
                f.append(
                    Finding(
                        "LM_SUBTYPE_DISCRIMINATOR",
                        swhere,
                        f"discriminator.path is {path!r}; it must be a payload path",
                        "set discriminator.path to payload.<field>",
                    )
                )
            else:
                paths.add(path)
            if const != sname:
                f.append(
                    Finding(
                        "LM_SUBTYPE_DISCRIMINATOR",
                        swhere,
                        f"discriminator.const is {const!r} and the subtype is {sname!r}. The "
                        "subtype in the envelope and the discriminator in the payload must "
                        "agree, which is the zmeta-event-1.0 mechanism this file keeps",
                        "set const equal to the subtype name",
                    )
                )
            if const in consts:
                f.append(
                    Finding(
                        "LM_SUBTYPE_DISCRIMINATOR",
                        swhere,
                        f"discriminator.const {const!r} is also used by subtype {consts[const]!r}, "
                        "so the two are indistinguishable on the wire",
                        "give each subtype its own const",
                    )
                )
            consts[const] = sname
        if len(paths) > 1:
            f.append(
                Finding(
                    "LM_SUBTYPE_DISCRIMINATOR",
                    f"{where}.subtypes",
                    f"subtypes use {len(paths)} discriminator paths: {sorted(paths)}. A type has one",
                    "use one payload field as the discriminator for every subtype of the type",
                )
            )
        disc_field = next(iter(paths)).split(".", 1)[1] if len(paths) == 1 else None
        fields = payload.get("fields") or {}
        if disc_field:
            enum = set(_as_list((fields.get(disc_field) or {}).get("enum")))
            if enum != set(subtype_names):
                f.append(
                    Finding(
                        "LM_DISCRIMINATOR_ENUM_DRIFT",
                        f"{where}.payload.fields.{disc_field}.enum",
                        f"the discriminator field's enum {sorted(enum)} differs from the subtype "
                        f"set {sorted(subtype_names)}",
                        "make the enum equal to the subtype names",
                    )
                )

        # required per subtype
        required = payload.get("required") or {}
        if isinstance(required, dict):
            for s in subtype_names:
                if s not in required:
                    f.append(
                        Finding(
                            "LM_REQUIRED_SUBTYPE_MISSING",
                            f"{where}.payload.required",
                            f"no required-field list for subtype {s}",
                            "add the list, even if it only names the discriminator",
                        )
                    )
                elif disc_field and disc_field not in _as_list(required.get(s)):
                    f.append(
                        Finding(
                            "LM_REQUIRED_SUBTYPE_MISSING",
                            f"{where}.payload.required.{s}",
                            f"does not require the discriminator field {disc_field!r}, so the "
                            "subtype match cannot fire",
                            "add the discriminator field to the required list",
                        )
                    )
            for s in required:
                if s not in subtype_names:
                    f.append(
                        Finding(
                            "LM_REQUIRED_SUBTYPE_MISSING",
                            f"{where}.payload.required.{s}",
                            "names a subtype the type does not declare",
                            "remove the entry or declare the subtype",
                        )
                    )
        else:
            f.append(Finding("LM_REQUIRED_SUBTYPE_MISSING", f"{where}.payload.required", "must be a map of subtype to field list", "restructure as a map"))
            required = {}

        # L-05 layer membership
        layer = tdef.get("layer")
        if layer not in layer_names:
            f.append(
                Finding(
                    "LM_LAYER_UNKNOWN",
                    f"{where}.layer = {layer!r}",
                    "names a layer that `layers` does not define, so the layer is open on one side",
                    "define the layer, or move the type to a defined one",
                )
            )
        else:
            used_layers.add(layer)
        prohibited = _prohibited_names(tdef)
        if layer in layers:
            for name in _as_list((layers[layer] or {}).get("never_carries")):
                if name not in prohibited:
                    f.append(
                        Finding(
                            "LM_LAYER_NEVER_CARRIES_UNENFORCED",
                            f"{where}.payload.prohibited",
                            f"layer {layer!r} says it never carries {name!r} and this type does "
                            "not prohibit it, so the layer rule is a sentence for this type",
                            f"add {name!r} to a prohibited group on the type, or remove it from "
                            f"layers.{layer}.never_carries",
                        )
                    )

        # L-06
        declared_names = _field_names(fields)
        for s, req in required.items():
            for name in _as_list(req):
                if name in prohibited:
                    f.append(
                        Finding(
                            "LM_REQUIRED_PROHIBITED_OVERLAP",
                            f"{where}.payload.required.{s}",
                            f"{name!r} is required and also prohibited, so no event of this "
                            "subtype can be written",
                            "drop it from one of the two lists",
                        )
                    )
        overlap = declared_names & prohibited
        if overlap:
            f.append(
                Finding(
                    "LM_REQUIRED_PROHIBITED_OVERLAP",
                    f"{where}.payload.fields",
                    f"declares field(s) {sorted(overlap)} that the type prohibits at any depth",
                    "rename the field or remove it from the denylist",
                )
            )

        # L-07
        missing_cred = [n for n in CREDENTIAL_VALUE_NAMES if n not in prohibited]
        if missing_cred:
            f.append(
                Finding(
                    "LM_CREDENTIAL_NAMES_MISSING",
                    f"{where}.payload.prohibited",
                    f"does not prohibit credential-value name(s) {missing_cred}. CR-3: a "
                    "credential value never appears in a log, and the event log is a log",
                    "add a prohibited group naming every entry of CREDENTIAL_VALUE_NAMES "
                    "with code CREDENTIAL_VALUE_IN_PAYLOAD",
                )
            )

        # L-21
        env_required = set(_as_list(envelope.get("required")))
        env_known = env_required | set(_as_list(envelope.get("optional")))
        declared_env = _as_list(tdef.get("required_envelope_fields"))
        short = sorted(env_required - set(declared_env))
        if short:
            f.append(
                Finding(
                    "LM_ENVELOPE_FIELDS_NOT_SUPERSET",
                    f"{where}.required_envelope_fields",
                    f"omits {short}, which envelope.required makes mandatory on every event. "
                    "The generator would emit a branch for this type that accepts an event "
                    "the envelope refuses, and for case_id that is an event D4's sweep cannot "
                    "reach",
                    "list every name in envelope.required, plus any optional field this type "
                    "makes mandatory, such as lineage",
                )
            )
        unknown_env = sorted(set(declared_env) - env_known)
        if unknown_env:
            f.append(
                Finding(
                    "LM_ENVELOPE_FIELDS_NOT_SUPERSET",
                    f"{where}.required_envelope_fields",
                    f"names {unknown_env}, which the envelope neither requires nor allows, so "
                    "the requirement can never be met",
                    "correct the name, or declare the field under envelope.fields and list it "
                    "in envelope.required or envelope.optional",
                )
            )

        # prohibited groups well-formed, and L-25
        name_codes: dict[str, set[str]] = {}
        for i, group in enumerate(_as_list(payload.get("prohibited"))):
            if not isinstance(group, dict) or not group.get("names") or not group.get("code"):
                f.append(
                    Finding(
                        "LM_PROHIBITED_GROUP_MALFORMED",
                        f"{where}.payload.prohibited[{i}]",
                        "a prohibited group needs names and the code a hit fires",
                        "add names and code",
                    )
                )
                continue
            for name in _as_list(group.get("names")):
                name_codes.setdefault(name, set()).add(group["code"])
        for name, codes_for_name in sorted(name_codes.items()):
            if len(codes_for_name) > 1:
                f.append(
                    Finding(
                        "LM_DENYLIST_CODE_AMBIGUOUS",
                        f"{where}.payload.prohibited",
                        f"{name!r} appears in two groups under different codes "
                        f"{sorted(codes_for_name)}. The group's code is what the generated "
                        "policy emits and what a must-fail fixture asserts, and a name firing "
                        "two codes cannot satisfy the expect_only THE-GAMEPLAN section 2.4 "
                        "requires on the D2 and D5 fixtures",
                        f"keep {name!r} in one group, and pick the code whose own fires_when "
                        "declaration names this case",
                    )
                )

        # L-26
        for rname, rdef in (payload.get("rules") or {}).items():
            rwhere = f"{where}.payload.rules.{rname}"
            if not isinstance(rdef, dict):
                f.append(Finding("LM_RULE_CONDITION_MISSING", rwhere, "a rule is a mapping", "give the rule statement, code, when, requires and cites"))
                continue
            when = rdef.get("when")
            if "when" not in rdef or not _when_valid(when):
                f.append(
                    Finding(
                        "LM_RULE_CONDITION_MISSING",
                        rwhere,
                        f"carries no machine-readable condition, or {when!r} is not one of the "
                        "forms the model's notation paragraph names. Without one, a rule whose "
                        "requirement depends on another field's value exists only as English "
                        "and the schema generator has to invent the condition, which fails "
                        "Step 5's done-condition on the required-field list",
                        "add `when`, one of always, runtime, { subtype: NAME }, "
                        "{ field: NAME, equals: VALUE }, { field: NAME, contains: VALUE }, "
                        "{ field: NAME, present: true } or { all_of: [...] }",
                    )
                )
                continue
            if when == "runtime" and not rdef.get("runtime_reason"):
                f.append(
                    Finding(
                        "LM_RULE_CONDITION_MISSING",
                        rwhere,
                        "is `when: runtime` and states no runtime_reason, so nothing records "
                        "which fact about the case the wire cannot carry",
                        "add runtime_reason naming the fact, or give the rule a condition the "
                        "event's own fields express",
                    )
                )
            req = rdef.get("requires")
            if not isinstance(req, list):
                f.append(
                    Finding(
                        "LM_RULE_CONDITION_MISSING",
                        rwhere,
                        f"requires is {req!r} and must be a list of field names, empty when the "
                        "rule constrains a value rather than requiring a field",
                        "add `requires`, using [] where the rule requires no field",
                    )
                )
                continue
            unknown = sorted(set(req) - declared_names)
            if unknown:
                f.append(
                    Finding(
                        "LM_RULE_CONDITION_MISSING",
                        rwhere,
                        f"requires {unknown}, which this type does not declare under "
                        "payload.fields at any depth, so the requirement names nothing",
                        "correct the field name, or declare the field",
                    )
                )
            sel = _when_subtypes(when, subtype_names)
            for s in sel or []:
                if s not in subtype_names:
                    f.append(Finding("LM_RULE_CONDITION_MISSING", rwhere, f"when names subtype {s!r}, which the type does not declare", "correct the subtype name"))
                    continue
                unmet = sorted(set(req) - set(_as_list(required.get(s))))
                if unmet:
                    f.append(
                        Finding(
                            "LM_RULE_REQUIRES_UNMET",
                            f"{where}.payload.required.{s}",
                            f"the rule {rname} applies to {s} unconditionally and requires "
                            f"{unmet}, which the subtype's required-field list omits. The rule "
                            "would claim a field the schema does not make mandatory",
                            f"add {unmet} to payload.required.{s}, or narrow the rule's `when` "
                            "to the condition under which it actually applies",
                        )
                    )

        # L-08 per-type half
        rule = (tdef.get("confidence") or {}).get("rule")
        permitted = set(_as_list(conf.get("permitted_types")))
        if (rule == "prohibited") == (tname in permitted):
            f.append(
                Finding(
                    "LM_CONFIDENCE_INCONSISTENT",
                    f"{where}.confidence.rule = {rule!r}",
                    f"the global confidence.permitted_types {'includes' if tname in permitted else 'excludes'} "
                    f"{tname} and the type says {rule!r}. A half-reversed decision cannot ship",
                    "change both the global list and the type's rule, in one edit",
                )
            )
        if rule not in ("prohibited", "required", "optional"):
            f.append(Finding("LM_CONFIDENCE_INCONSISTENT", f"{where}.confidence.rule", f"{rule!r} is not prohibited, required or optional", "use one of the three"))
        if not (tdef.get("confidence") or {}).get("violation_code"):
            f.append(Finding("LM_CONFIDENCE_INCONSISTENT", f"{where}.confidence", "no violation_code", "name the code a numeric confidence fires"))

        # L-09, L-10, L-11
        lin = tdef.get("lineage") or {}
        allowed = lin.get("allowed_parents") or {}
        for ptype, psubs in allowed.items():
            if ptype not in types:
                f.append(Finding("LM_LINEAGE_PARENT_UNRESOLVED", f"{where}.lineage.allowed_parents.{ptype}", "names a type that does not exist", "correct the type name"))
                continue
            for ps in _as_list(psubs):
                if ps not in (types[ptype].get("subtypes") or {}):
                    f.append(Finding("LM_LINEAGE_PARENT_UNRESOLVED", f"{where}.lineage.allowed_parents.{ptype}", f"names subtype {ps!r}, which {ptype} does not declare", "correct the subtype name"))
        rbs = lin.get("required_by_subtype") or {}
        if set(rbs.keys()) != set(subtype_names):
            f.append(
                Finding(
                    "LM_LINEAGE_INCONSISTENT",
                    f"{where}.lineage.required_by_subtype",
                    f"covers {sorted(rbs.keys())} and the type declares {sorted(subtype_names)}",
                    "state true or false for every subtype",
                )
            )
        req_parents = lin.get("required_parents") or {}
        for s in subtype_names:
            needs = bool(rbs.get(s))
            entry = req_parents.get(s)
            if needs and not (entry and _as_list((entry or {}).get("any_of"))):
                f.append(
                    Finding(
                        "LM_LINEAGE_INCONSISTENT",
                        f"{where}.lineage.required_parents.{s}",
                        "lineage is required for this subtype and no required parent is named, "
                        "so any parent at all would satisfy it",
                        "name the any_of set, or set required_by_subtype false",
                    )
                )
            if not needs and entry:
                f.append(
                    Finding(
                        "LM_LINEAGE_INCONSISTENT",
                        f"{where}.lineage.required_parents.{s}",
                        "names required parents while required_by_subtype says lineage is optional",
                        "make the two agree",
                    )
                )
        for s, entry in req_parents.items():
            if s not in subtype_names:
                f.append(Finding("LM_LINEAGE_PARENT_UNRESOLVED", f"{where}.lineage.required_parents.{s}", "names a subtype the type does not declare", "correct the subtype name"))
                continue
            any_of = _as_list((entry or {}).get("any_of"))
            non_self = 0
            for alt in any_of:
                pt, ps = (alt or {}).get("type"), (alt or {}).get("subtype")
                if pt not in types or ps not in (types.get(pt, {}).get("subtypes") or {}):
                    f.append(Finding("LM_LINEAGE_PARENT_UNRESOLVED", f"{where}.lineage.required_parents.{s}", f"required parent {pt}.{ps} does not exist", "correct the reference"))
                    continue
                if pt not in allowed or ps not in _as_list(allowed.get(pt)):
                    f.append(
                        Finding(
                            "LM_LINEAGE_PARENT_UNRESOLVED",
                            f"{where}.lineage.required_parents.{s}",
                            f"requires {pt}.{ps}, which allowed_parents does not permit, so the "
                            "requirement can never be met",
                            "add it to allowed_parents or drop the requirement",
                        )
                    )
                # A subtype may name itself as one alternative (an EXTEND based
                # on a prior EXTEND, a CLUSTER refining a CLUSTER). It may not
                # be the only alternative, because then no first event exists.
                if (pt, ps) != (tname, s):
                    non_self += 1
            if any_of and non_self == 0:
                f.append(
                    Finding(
                        "LM_SELF_REQUIRED_PARENT",
                        f"{where}.lineage.required_parents.{s}",
                        "every required parent is the subtype itself, so no first event can exist",
                        "add a parent of another type or subtype",
                    )
                )

        # L-30
        cites_targets = any(
            isinstance(rdef, dict) and "allowed_targets" in str(rdef.get("statement") or "")
            for rdef in (payload.get("rules") or {}).values()
        )
        targets = lin.get("allowed_targets")
        if cites_targets and not targets:
            f.append(
                Finding(
                    "LM_ALLOWED_TARGETS_MISSING",
                    f"{where}.lineage.allowed_targets",
                    "a rule of this type cites allowed_targets and the block is absent or "
                    "empty, so the rule points at nothing and the gate is silent. That is the "
                    "shape SS-5 records as a field declared, listed, printed, and never read",
                    "restore the block with one entry per subtype, or remove the rule that "
                    "cites it",
                )
            )
        elif targets:
            if set(targets.keys()) != set(subtype_names):
                f.append(
                    Finding(
                        "LM_ALLOWED_TARGETS_DRIFT",
                        f"{where}.lineage.allowed_targets",
                        f"covers {sorted(targets.keys())} and the type declares "
                        f"{sorted(subtype_names)}",
                        "name every subtype, even where the target set repeats",
                    )
                )
            for s in subtype_names:
                if s not in targets:
                    continue
                allowed_t = set(_as_list(targets.get(s)))
                required_t = {
                    (alt or {}).get("type")
                    for alt in _as_list((req_parents.get(s) or {}).get("any_of"))
                }
                required_t.discard(None)
                only_targets = sorted(allowed_t - required_t)
                only_required = sorted(required_t - allowed_t)
                if only_targets or only_required:
                    f.append(
                        Finding(
                            "LM_ALLOWED_TARGETS_DRIFT",
                            f"{where}.lineage.allowed_targets.{s}",
                            f"allows targets {only_targets} that required_parents does not name, "
                            f"and required_parents names {only_required} that allowed_targets "
                            "does not allow. Two blocks in one lineage section give different "
                            "answers for the same disposition, and the generated policy would "
                            "carry both",
                            "make the two agree, in whichever direction LM-R11 records as the "
                            "operator's. Widening allowed_targets makes every parent type a "
                            "target; narrowing required_parents removes a capability",
                        )
                    )

        # L-12, L-13
        pa = tdef.get("producer_authority") or {}
        by_sub = pa.get("by_subtype") or {}
        if tname in HUMAN_ONLY_TYPES:
            wild = list(_as_list(pa.get("wildcards")))
            for s, entry in by_sub.items():
                wild += list(_as_list((entry or {}).get("wildcards")))
            if wild or not pa.get("human_identity_only") or _as_list(pa.get("named")):
                f.append(
                    Finding(
                        "LM_WILDCARD_ON_HUMAN_TYPE",
                        f"{where}.producer_authority",
                        f"{tname} accepts only a named human identity and declares wildcards "
                        f"{wild}, named {_as_list(pa.get('named'))}, human_identity_only "
                        f"{pa.get('human_identity_only')}. An unnamed identity assertion is "
                        "the injection path (design section 8.2 item 4)",
                        "empty wildcards and named, set human_identity_only true",
                    )
                )
        if tname == "COLLECT_EVENT":
            named = list(_as_list(pa.get("named")))
            wild = list(_as_list(pa.get("wildcards")))
            if named != [COLLECT_PRODUCER] or wild or by_sub or pa.get("human_identity_only"):
                f.append(
                    Finding(
                        "LM_COLLECT_PRODUCER",
                        f"{where}.producer_authority",
                        f"the gate has exactly one producer, {COLLECT_PRODUCER}, and this declares "
                        f"named {named}, wildcards {wild}. A second producer is a second gate (SS-6)",
                        f"set named to [{COLLECT_PRODUCER}] and wildcards to []",
                    )
                )

        # L-16, L-17
        ret = tdef.get("retention") or {}
        eg = tdef.get("egress") or {}
        env_stratum = ret.get("envelope_stratum")
        if env_stratum not in STRATA:
            f.append(Finding("LM_STRATUM_INVALID", f"{where}.retention.envelope_stratum", f"{env_stratum!r} is not an RT-1 stratum", "use 0, 1, 2, 3, 4 or T"))
        # EG-5's table comes from CROSSING_STRATA rather than from the model's own
        # egress.strata_crossing_to_local, which this check used to read. Reading it
        # made the rule derived from itself, so widening the list and the per-type
        # flags it governs in one commit agreed with itself and passed. L-20 pins
        # the list separately, and EG-2 is what both are holding.
        crossing = set(CROSSING_STRATA)
        if env_stratum in STRATA and bool(eg.get("envelope_crosses_to_local")) != (env_stratum in crossing):
            f.append(
                Finding(
                    "LM_EGRESS_INCONSISTENT",
                    f"{where}.egress.envelope_crosses_to_local",
                    f"stratum {env_stratum} {'crosses' if env_stratum in crossing else 'does not cross'} "
                    "under EG-5 and the declaration says otherwise",
                    "derive the flag from the stratum",
                )
            )
        pstrata = _per_subtype(ret.get("payload_stratum"), subtype_names)
        carries = _per_subtype(ret.get("carries_subject_values"), subtype_names)
        pcross = _per_subtype(eg.get("payload_crosses_to_local"), subtype_names)
        for s in subtype_names:
            st = pstrata.get(s)
            if st not in STRATA:
                f.append(Finding("LM_STRATUM_INVALID", f"{where}.retention.payload_stratum[{s}]", f"{st!r} is not an RT-1 stratum", "use 0, 1, 2, 3, 4 or T"))
                continue
            if carries.get(s) is None:
                f.append(Finding("LM_STRATUM_INVALID", f"{where}.retention.carries_subject_values[{s}]", "not declared", "state true or false; RT-1 declares it at write time"))
            if carries.get(s) and st in SURVIVING_STRATA:
                f.append(
                    Finding(
                        "LM_RT2_VIOLATION",
                        f"{where}.retention.payload_stratum[{s}] = {st}",
                        "a payload that carries subject-derived values sits in a stratum that "
                        "survives the shred. RETENTION.md RT-2 calls this a defect, not a "
                        "judgment call",
                        "move the payload to stratum 0 or 1, or prohibit every subject-carrying "
                        "field and set carries_subject_values false",
                    )
                )
            if bool(pcross.get(s)) != (st in crossing):
                f.append(
                    Finding(
                        "LM_EGRESS_INCONSISTENT",
                        f"{where}.egress.payload_crosses_to_local[{s}]",
                        f"stratum {st} {'crosses' if st in crossing else 'does not cross'} under "
                        "EG-5 and the declaration says otherwise",
                        "derive the flag from the stratum",
                    )
                )

        # per-type code list is complete for the type's own rules
        own = set(_as_list(tdef.get("violation_codes")))
        used: set[str] = set()
        for group in _as_list(payload.get("prohibited")):
            if isinstance(group, dict) and group.get("code"):
                used.add(group["code"])
        for rname, rdef in (payload.get("rules") or {}).items():
            if isinstance(rdef, dict) and rdef.get("code"):
                used.add(rdef["code"])
        vc = (tdef.get("confidence") or {}).get("violation_code")
        if vc:
            used.add(vc)
        # L-14 per type, L-32. The convention is exact: a type's violation_codes
        # names the codes its own prohibited groups, rules and confidence entry
        # fire, and nothing else. The check ran in one direction only until
        # 2026-09-03, so three types listed a code no rule of theirs fires while
        # six carried the same relationships without listing it.
        gap = used - own
        if gap:
            f.append(
                Finding(
                    "LM_PER_TYPE_CODES_INCOMPLETE",
                    f"{where}.violation_codes",
                    f"the type's rules fire {sorted(gap)} and its code list omits them",
                    "add the codes to the type's violation_codes list",
                )
            )
        extra = own - used
        if extra:
            f.append(
                Finding(
                    "LM_PER_TYPE_CODES_EXTRA",
                    f"{where}.violation_codes",
                    f"lists {sorted(extra)} and no prohibited group, rule or confidence entry "
                    "of this type fires them. A type's code list is what a reader takes for the "
                    "set of ways this type can refuse, and a code listed here and fired "
                    "elsewhere sends a diagnostic to the wrong type",
                    "remove the codes, or name the rule on this type that fires them. A code "
                    "fired by lineage, producer authority or a chain rule belongs to that "
                    "section's list rather than to a type's",
                )
            )

    # L-05 unused layers, and layer shape
    for lname, ldef in layers.items():
        if lname not in used_layers:
            f.append(
                Finding(
                    "LM_LAYER_UNUSED",
                    f"layers.{lname}",
                    "defined and used by no type, so the layer set is open on the other side",
                    "remove the layer, or assign a type to it",
                )
            )
        if not isinstance(ldef, dict) or "never_carries" not in ldef or "may_carry" not in ldef:
            f.append(Finding("LM_LAYER_UNUSED", f"layers.{lname}", "a layer declares may_carry and never_carries", "add both lists"))

    # L-10. Named, so deleting the line fails here and not somewhere generic, and
    # an exact set rather than a membership test, because any_of means one
    # alternative suffices. An earlier draft asserted only that the pair was
    # present, so the gate could be removed by addition: appending
    # { AUTHORIZE_EVENT, GRANT } satisfied the check and gave a RUN_START a second
    # dispatch path, and appending { COLLECT_EVENT, REFUSED } gave it a parent the
    # gate declined. SS-7 renders `refused` as "REFUSED. This selector is in a class
    # this case may not collect on. No authorization file unlocks it."
    probe = types.get("PROBE_EVENT") or {}
    d5 = _as_list((((probe.get("lineage") or {}).get("required_parents") or {}).get("RUN_START") or {}).get("any_of"))
    d5_set = {((a or {}).get("type"), (a or {}).get("subtype")) for a in d5}
    if d5_set != {("COLLECT_EVENT", "PERMITTED")}:
        f.append(
            Finding(
                "LM_D5_PARENT_MISSING",
                "event_types.PROBE_EVENT.lineage.required_parents.RUN_START",
                f"the required-parent set is {sorted(d5_set)} and D5 makes it exactly "
                "COLLECT_EVENT PERMITTED. A second alternative is a second dispatch path, "
                "which is Class F by effect whatever the diff looks like, and an absent one "
                "means a run no longer needs a gate decision at all. That single line is "
                "what makes the subject gate a structural boundary rather than a function "
                "call (FOUNDATION D5, SUBJECT_SELECTION.md SS-6)",
                "make any_of exactly [{ type: COLLECT_EVENT, subtype: PERMITTED }]. Widening "
                "or removing it is Class F and needs a dated stamp in "
                "doctrine/DOCTRINE_STATUS.md, authored by the ratifier",
            )
        )

    # L-31. The D5 parent binds a run to a decision; run_matches_its_decision binds
    # it to *its* decision. Without the second, one PERMITTED authorizes unlimited
    # runs against connectors and selectors it never evaluated, which passes every
    # lineage check because a PERMITTED does resolve.
    for tname_r, rule_name, rule_code in REQUIRED_RULES:
        rdef = _resolve(model, f"event_types.{tname_r}.payload.rules.{rule_name}")
        if not isinstance(rdef, dict):
            f.append(
                Finding(
                    "LM_REQUIRED_RULE_MISSING",
                    f"event_types.{tname_r}.payload.rules.{rule_name}",
                    "a rule the doctrine turns on is gone by name. Deleting it leaves the "
                    "constraint stated in prose and enforced by nothing, and no generic check "
                    "would notice",
                    f"restore the rule firing {rule_code}, or take it out of REQUIRED_RULES in "
                    "this tool with the ratification that permits its removal",
                )
            )
        elif rdef.get("code") != rule_code:
            f.append(
                Finding(
                    "LM_REQUIRED_RULE_MISSING",
                    f"event_types.{tname_r}.payload.rules.{rule_name}.code",
                    f"fires {rdef.get('code')!r} and this rule's refusal is {rule_code}. The "
                    "code is what the generated policy emits and what the fixture asserts",
                    f"set the code to {rule_code}, or change both this tool and the fixture map "
                    "in the same commit",
                )
            )

    # L-08 global half
    if conf.get("mode") == "prohibited_everywhere" and _as_list(conf.get("permitted_types")):
        f.append(Finding("LM_CONFIDENCE_INCONSISTENT", "confidence", "mode is prohibited_everywhere and permitted_types is not empty", "make the two agree"))
    if not conf.get("violation_code"):
        f.append(Finding("LM_CONFIDENCE_INCONSISTENT", "confidence.violation_code", "missing", "name the code"))

    # L-19 lineage matrix
    matrix = lineage.get("matrix") or {}
    for tname, tdef in types.items():
        src = set(((tdef.get("lineage") or {}).get("allowed_parents") or {}).keys())
        if set(_as_list(matrix.get(tname))) != src:
            f.append(
                Finding(
                    "LM_LINEAGE_MATRIX_DRIFT",
                    f"lineage.matrix.{tname}",
                    f"says {sorted(_as_list(matrix.get(tname)))} and the type's allowed_parents "
                    f"say {sorted(src)}",
                    "regenerate the matrix row from event_types.<type>.lineage.allowed_parents",
                )
            )
    for tname in matrix:
        if tname not in types:
            f.append(Finding("LM_LINEAGE_MATRIX_DRIFT", f"lineage.matrix.{tname}", "names a type that does not exist", "remove the row"))
    modes = lineage.get("modes") or {}
    for mode in ("parent_type_mismatch_mode", "payload_based_on_subset_mode", "unresolved_parent_mode"):
        if modes.get(mode) != "reject":
            f.append(
                Finding(
                    "LM_LINEAGE_MODE",
                    f"lineage.modes.{mode} = {modes.get(mode)!r}",
                    "one store, one consumer, no profiles: every lineage mode is reject",
                    "set the mode to reject",
                )
            )
    if modes.get("profiles") not in ("none", None) or lineage.get("profiles"):
        f.append(Finding("LM_LINEAGE_MODE", "lineage.modes.profiles", "profiles never un-defer (THE-GAMEPLAN section 2.2)", "set profiles to none"))

    # L-19 producer index
    global_pairs: dict[tuple[str, str], set[str]] = {}
    for w, refs in (producers.get("wildcards") or {}).items():
        for pair in _expand_index(refs, types):
            global_pairs.setdefault(pair, set()).add(w)
    for n, refs in (producers.get("named") or {}).items():
        for pair in _expand_index(refs, types):
            global_pairs.setdefault(pair, set()).add(n)
    for pair in _expand_index(producers.get("human_identity_only"), types):
        global_pairs.setdefault(pair, set()).add(HUMAN)
    for tname, tdef in types.items():
        local = _producer_sets(tname, tdef)
        for s, have in local.items():
            want = global_pairs.get((tname, s), set())
            if have != want:
                f.append(
                    Finding(
                        "LM_PRODUCER_INDEX_DRIFT",
                        f"producer_authority index for {tname}.{s}",
                        f"the global index grants {sorted(want)} and the type grants {sorted(have)}",
                        "regenerate the index from event_types.<type>.producer_authority",
                    )
                )
            if not have:
                f.append(Finding("LM_PRODUCER_INDEX_DRIFT", f"event_types.{tname}.producer_authority[{s}]", "no producer may emit this subtype at all", "grant a wildcard, a named producer, or human identity"))
    for (t, s) in global_pairs:
        if t not in types or s not in (types[t].get("subtypes") or {}):
            f.append(Finding("LM_PRODUCER_INDEX_DRIFT", f"producer_authority index {t}.{s}", "names a type or subtype that does not exist", "correct the reference"))
    if set(_as_list(producers.get("require_match_for_event_types"))) != set(types.keys()):
        f.append(Finding("LM_PRODUCER_INDEX_DRIFT", "producer_authority.require_match_for_event_types", "does not name exactly the declared types", "list every type"))
    for t in HUMAN_ONLY_TYPES:
        if t not in _as_list(producers.get("human_identity_only")):
            f.append(Finding("LM_WILDCARD_ON_HUMAN_TYPE", "producer_authority.human_identity_only", f"omits {t}", "add it"))

    # L-14 code vocabulary, both directions
    declared: dict[str, dict] = {}
    for i, entry in enumerate(_as_list(codes_section.get("codes"))):
        if not isinstance(entry, dict) or not entry.get("code"):
            f.append(Finding("LM_CODE_MALFORMED", f"violation_codes.codes[{i}]", "an entry needs code, severity and since", "complete the entry"))
            continue
        code = entry["code"]
        if code in declared:
            f.append(Finding("LM_CODE_DUPLICATE", f"violation_codes.codes[{i}] {code}", "declared twice", "remove one"))
        declared[code] = entry
        if entry.get("severity") not in _as_list(codes_section.get("severities")):
            f.append(Finding("LM_CODE_MALFORMED", f"violation_codes.codes {code}", f"severity {entry.get('severity')!r} is not in violation_codes.severities", "use a declared severity"))
        if entry.get("since") != pse.get("version"):
            f.append(Finding("LM_CODE_MALFORMED", f"violation_codes.codes {code}", f"since is {entry.get('since')!r}; every code at this version was minted at {pse.get('version')}", "set since to the minting version"))
        # L-34. The entry parsed, so no other check sees anything wrong.
        extra = sorted(set(entry) - CODE_ENTRY_KEYS)
        if extra:
            f.append(Finding(
                "LM_CODE_ENTRY_KEYS",
                f"violation_codes.codes {code}",
                f"carries {extra}, which are not entry keys. An unquoted flow mapping ends "
                "fires_when at its first comma and turns the rest of the sentence into keys, so "
                "the compiled policy would document this code with a truncated sentence",
                "quote the fires_when value, then regenerate",
            ))
        if not str(entry.get("fires_when") or "").strip():
            f.append(Finding(
                "LM_CODE_ENTRY_KEYS",
                f"violation_codes.codes {code}",
                "has no fires_when, so the compiled policy would document the code with nothing",
                "state when the code fires, as a quoted sentence",
            ))

    referenced: dict[str, str] = {}

    def ref(code, where):
        if code:
            referenced.setdefault(code, where)

    for c in _as_list(envelope.get("violation_codes")):
        ref(c, "envelope.violation_codes")
    ref((envelope.get("payload_denylist_recursion") or {}).get("nested_hit_code"), "envelope.payload_denylist_recursion")
    ref(conf.get("violation_code"), "confidence.violation_code")
    for c in _as_list(lineage.get("violation_codes")):
        ref(c, "lineage.violation_codes")
    for rname, rdef in (lineage.get("chain_rules") or {}).items():
        ref((rdef or {}).get("code"), f"lineage.chain_rules.{rname}")
    ref(producers.get("violation_code"), "producer_authority.violation_code")
    for c in _as_list(egress.get("violation_codes")):
        ref(c, "egress.violation_codes")
    for tname, tdef in types.items():
        for c in _as_list(tdef.get("violation_codes")):
            ref(c, f"event_types.{tname}.violation_codes")
        for group in _as_list((tdef.get("payload") or {}).get("prohibited")):
            if isinstance(group, dict):
                ref(group.get("code"), f"event_types.{tname}.payload.prohibited")
        for rname, rdef in ((tdef.get("payload") or {}).get("rules") or {}).items():
            if isinstance(rdef, dict):
                ref(rdef.get("code"), f"event_types.{tname}.payload.rules.{rname}")
        ref((tdef.get("confidence") or {}).get("violation_code"), f"event_types.{tname}.confidence")
    fixtures = codes_section.get("fixtures") or {}
    for fname, fdef in fixtures.items():
        ref((fdef or {}).get("code"), f"violation_codes.fixtures.{fname}")

    for code, where in sorted(referenced.items()):
        if code not in declared:
            f.append(
                Finding(
                    "LM_CODE_UNDECLARED",
                    f"{where} -> {code}",
                    "a rule fires a code the vocabulary does not declare, so the diagnostic "
                    "would be free text",
                    "declare the code under violation_codes.codes with severity and since",
                )
            )
    for code in sorted(declared):
        if code not in referenced:
            f.append(
                Finding(
                    "LM_CODE_UNREFERENCED",
                    f"violation_codes.codes {code}",
                    "declared and fired by no rule in this file, so it is a check nobody wrote",
                    "name the rule that fires it, or remove the code",
                )
            )

    # L-15 fixtures
    for fname in REQUIRED_FIXTURES:
        fdef = fixtures.get(fname)
        if not isinstance(fdef, dict) or not fdef.get("code") or not fdef.get("rule"):
            f.append(
                Finding(
                    "LM_FIXTURE_MISSING",
                    f"violation_codes.fixtures.{fname}",
                    "one of the sixteen named must-fail fixtures has no mapping to a code and "
                    "the rule that fires it (THE-GAMEPLAN section 2.3)",
                    "add the entry with code, rule and corpus",
                )
            )
            continue
        node = _resolve(model, fdef["rule"])
        if node is None:
            f.append(
                Finding(
                    "LM_FIXTURE_RULE_UNRESOLVED",
                    f"violation_codes.fixtures.{fname}.rule = {fdef['rule']}",
                    "the rule path resolves to nothing in this file",
                    "point the fixture at the rule that fires its code",
                )
            )
            continue
        expected = fdef["code"]
        # The code sources are widened to every key a code travels under, and the
        # guard is inverted: an entry that reaches no code at all is refused rather
        # than passed. Four entries reached none before 2026-09-03, including the D5
        # one, so any code at all satisfied them. RT-9 states the standard: a check
        # that can pass for a reason other than the one claimed is not a check.
        pname = fdef.get("prohibited_name")
        node_codes: set[str] = set()
        if pname:
            groups = [g for g in _as_list(node) if isinstance(g, dict) and pname in _as_list(g.get("names"))]
            if not groups:
                f.append(
                    Finding(
                        "LM_FIXTURE_RULE_UNRESOLVED",
                        f"violation_codes.fixtures.{fname}.prohibited_name = {pname}",
                        f"no prohibited group at {fdef['rule']} names that field, so the fixture "
                        "exercises a denylist entry the type does not carry",
                        "correct the name, or point the fixture at the type that prohibits it",
                    )
                )
                continue
            for g in groups:
                node_codes |= _node_codes(g)
        else:
            node_codes = _node_codes(node)
        if fdef.get("code_source"):
            src = _resolve(model, fdef["code_source"])
            if src is None:
                f.append(
                    Finding(
                        "LM_FIXTURE_CODE_UNCHECKABLE",
                        f"violation_codes.fixtures.{fname}.code_source = {fdef['code_source']}",
                        "the code source resolves to nothing, so the fixture's code is again "
                        "checked against nothing",
                        "point code_source at the rule, the confidence entry, or the section "
                        "list that declares the code this fixture asserts",
                    )
                )
                continue
            node_codes |= _node_codes(src)
        if not node_codes:
            f.append(
                Finding(
                    "LM_FIXTURE_CODE_UNCHECKABLE",
                    f"violation_codes.fixtures.{fname}.rule = {fdef['rule']}",
                    "the node this fixture points at carries no code under any key, so the "
                    "fixture could be mapped to any code in the vocabulary and pass. A check "
                    "that can pass for a reason other than the one claimed is not a check "
                    "(RETENTION.md RT-9)",
                    "add code_source naming the path that declares the code, or "
                    "prohibited_name naming the denylist entry, or point rule at a node that "
                    "carries the code itself",
                )
            )
        elif expected not in node_codes:
            f.append(
                Finding(
                    "LM_FIXTURE_RULE_UNRESOLVED",
                    f"violation_codes.fixtures.{fname}",
                    f"maps to {expected} and the rule at {fdef['rule']} fires {sorted(node_codes)}",
                    "correct the code or the rule path",
                )
            )
        if fname in EXPECT_ONLY_FIXTURES and fdef.get("expect_only") is not True:
            f.append(
                Finding(
                    "LM_FIXTURE_EXPECT_ONLY_MISSING",
                    f"violation_codes.fixtures.{fname}",
                    "a D2 or D5 fixture does not set expect_only. THE-GAMEPLAN section 2.4 "
                    "makes it mandatory on all of them, because a fixture that passes on any "
                    "failing code proves the corpus rejects the event and not that the named "
                    "rule is what rejected it",
                    "add expect_only: true. If the expected code cannot be the sole failure, "
                    "the rule or the fixture is wrong rather than the requirement",
                )
            )
    for fname in fixtures:
        if fname not in REQUIRED_FIXTURES:
            f.append(Finding("LM_FIXTURE_MISSING", f"violation_codes.fixtures.{fname}", "not one of the sixteen named fixtures. New fixtures are added to REQUIRED_FIXTURES in this tool and to THE-GAMEPLAN section 2.3 together", "add it to both, or remove it"))

    # L-20
    for path, expected, code, what, moves, only_when in PINNED:
        if only_when is not None:
            gate_path, gate_value = only_when
            if _resolve(model, gate_path) != gate_value:
                continue
        actual = _resolve(model, path)
        if actual != expected:
            f.append(Finding(code, f"{path} = {actual!r}", f"{what}. Expected {expected!r}", moves))

    # L-22. One word makes every denylist in this file recursive, it is generated
    # into policy/semantics.yaml, and nothing read it. Fixture 9 points at this
    # node and asserts the nested code, which is a different claim.
    recursion = envelope.get("payload_denylist_recursion") or {}
    if recursion.get("mode") != "recursive":
        f.append(
            Finding(
                "LM_DENYLIST_NOT_RECURSIVE",
                f"envelope.payload_denylist_recursion.mode = {recursion.get('mode')!r}",
                "the payload denylist stops being recursive, so nesting a prohibited name one "
                "level down launders a layer violation. Every never_carries rule and every "
                "prohibited group in this file is only as strong as this word",
                "set mode to recursive. The nested-layer-collapse fixture puts cluster_id at "
                "payload.extensions.notes.cluster_id and expects LAYER_COLLAPSE_NESTED, so a "
                "shallow denylist fails the corpus as well as this gate",
            )
        )

    # L-28. The generation map is the second half of Step 5's done-condition and
    # was entirely unread: deleting pse.generates passed clean.
    gens = _as_list(pse.get("generates"))
    gen_paths = [g.get("path") for g in gens if isinstance(g, dict)]
    for expected_path in EXPECTED_GENERATED:
        if expected_path not in gen_paths:
            f.append(
                Finding(
                    "LM_GENERATES_INCOMPLETE",
                    "pse.generates",
                    f"does not name {expected_path}, which is one of the five Step 7 outputs "
                    "generated from this file. An unnamed output is one a generator writes by "
                    "hand, which is the ZMeta restatement habit Step 5 exists to end",
                    "add the entry with its path and its from list",
                )
            )
    for i, g in enumerate(gens):
        gwhere = f"pse.generates[{i}]"
        if not isinstance(g, dict) or not g.get("path") or not _as_list(g.get("from")):
            f.append(Finding("LM_GENERATES_INCOMPLETE", gwhere, "an entry needs a path and a non-empty from list", "complete the entry"))
            continue
        if g["path"] not in EXPECTED_GENERATED:
            f.append(
                Finding(
                    "LM_GENERATES_INCOMPLETE",
                    f"{gwhere} {g['path']}",
                    "names an output this tool does not know about, so nothing holds the map "
                    "and the Step 7 output list to the same set",
                    "add the path to EXPECTED_GENERATED in this tool and to THE-GAMEPLAN "
                    "section 2.1 together, or remove the entry",
                )
            )
        for src in _as_list(g.get("from")):
            if not _resolve_glob(model, str(src)):
                f.append(
                    Finding(
                        "LM_GENERATES_UNRESOLVED",
                        f"{gwhere}.from -> {src}",
                        "the source path resolves to nothing in this file, so the generator "
                        "would read an empty node and emit an artifact with that rule missing",
                        "correct the path. `*` stands for every key at that level, as in "
                        "event_types.*.payload.prohibited",
                    )
                )

    # L-29. policy/semantics.yaml is generated from `layers`, so may_carry has to
    # be field names. An earlier draft mixed in six English phrases ("pivot depth",
    # "gate decision", "heartbeat fields") and omitted three real fields, which is
    # a generator input nobody could use in either direction.
    layer_fields: dict[str, set[str]] = {}
    for tname, tdef in types.items():
        layer_fields.setdefault(tdef.get("layer"), set()).update(
            ((tdef.get("payload") or {}).get("fields") or {}).keys()
        )
    for lname, ldef in layers.items():
        declared_may = set(_as_list((ldef or {}).get("may_carry")))
        actual_may = layer_fields.get(lname, set())
        not_a_field = sorted(declared_may - actual_may)
        unlisted = sorted(actual_may - declared_may)
        if not_a_field or unlisted:
            f.append(
                Finding(
                    "LM_LAYER_MAY_CARRY_DRIFT",
                    f"layers.{lname}.may_carry",
                    f"names {not_a_field} that no type in this layer declares as a top-level "
                    f"payload field, and omits {unlisted} that a type in this layer does "
                    "declare. may_carry is generator input and closed both ways, the treatment "
                    "never_carries already gets",
                    "use field names, one per top-level payload field of every type in the "
                    "layer. A nested field belongs to the field that carries it and is not "
                    "listed",
                )
            )

    # L-33
    shape = lineage.get("policy_shape") or {}
    if not shape:
        f.append(
            Finding(
                "LM_POLICY_SHAPE_MISSING",
                "lineage.policy_shape",
                "policy/lineage.yaml is generated from this section and from the per-type "
                "blocks, and the precedent's policy has one type-granular parent structure "
                "with no subtype key anywhere. Without this block a generator follows the "
                "precedent, emits the matrix, drops required_parents, and the D5 line is in "
                "this file and in no policy",
                "restore the block naming the target, its keys, and which of them need "
                "subtype granularity",
            )
        )
    else:
        if shape.get("target") != "policy/lineage.yaml":
            f.append(Finding("LM_POLICY_SHAPE_MISSING", "lineage.policy_shape.target", f"names {shape.get('target')!r} and the generated lineage policy is policy/lineage.yaml", "correct the target"))
        sub_gran = _as_list(shape.get("subtype_granularity_required_for"))
        if "required_parents" not in sub_gran:
            f.append(
                Finding(
                    "LM_POLICY_SHAPE_MISSING",
                    "lineage.policy_shape.subtype_granularity_required_for",
                    "does not require subtype granularity for required_parents. D5's "
                    "requirement is a subtype pair, COLLECT_EVENT PERMITTED, and a "
                    "type-granular policy cannot express it",
                    "add required_parents to the list",
                )
            )
        for key in ("allowed_parents", "required_parents"):
            if key not in _as_list(shape.get("keys")):
                f.append(Finding("LM_POLICY_SHAPE_MISSING", "lineage.policy_shape.keys", f"omits {key}, which the generated policy needs to carry the per-type source", "name every key the generator emits"))

    # divergences
    seen_dv: set[str] = set()
    for i, dv in enumerate(_as_list(model.get("divergences_from_zmeta"))):
        dwhere = f"divergences_from_zmeta[{i}]"
        if not isinstance(dv, dict) or not dv.get("id") or not dv.get("path") or not dv.get("rationale"):
            f.append(Finding("LM_DIVERGENCE_MALFORMED", dwhere, "an entry needs id, path, disposition and rationale", "complete the entry"))
            continue
        if dv.get("disposition") not in DIVERGENCE_DISPOSITIONS:
            f.append(Finding("LM_DIVERGENCE_MALFORMED", f"{dwhere} {dv['id']}", f"disposition {dv.get('disposition')!r} is not INVERT, REPLACE, DROP or NEW", "use one of the four"))
        if dv["id"] in seen_dv:
            f.append(Finding("LM_DIVERGENCE_MALFORMED", f"{dwhere} {dv['id']}", "duplicate id", "renumber"))
        seen_dv.add(dv["id"])

    return f


# ---------------------------------------------------------------------------
# self-test: break the model deliberately
# ---------------------------------------------------------------------------


def _mutations() -> list[tuple[str, callable, str, bool, str]]:
    """(description, mutator(model) -> optional new text, expected code, expect_only, why).

    `expect_only` False means the mutation's damage genuinely reaches more than
    one check, and the fifth field says how. Every False here is a sentence a
    reader can check against the model, which is the point of the flag: the
    earlier suite asserted membership alone, and eight of its nineteen mutations
    were passing on codes they never claimed to exercise.
    """

    def truncate_fires_when(m):
        # Exactly what an unquoted flow mapping does to a sentence with a comma:
        # the value ends at the first comma and the remainder becomes keys.
        entry = m["violation_codes"]["codes"][0]
        entry["fires_when"] = "the envelope violates the generated schema in a way no narrower code"
        entry["names"] = None

    def blank_fires_when(m):
        m["violation_codes"]["codes"][0]["fires_when"] = ""

    def drop_type(m):
        del m["event_types"]["SYSTEM_EVENT"]

    def add_tenth(m):
        m["event_types"]["TENTH_EVENT"] = copy.deepcopy(m["event_types"]["SYSTEM_EVENT"])

    def remove_d5(m):
        lin = m["event_types"]["PROBE_EVENT"]["lineage"]
        del lin["required_parents"]["RUN_START"]
        lin["required_by_subtype"]["RUN_START"] = False

    def widen_d5_same_type(m):
        m["event_types"]["PROBE_EVENT"]["lineage"]["required_parents"]["RUN_START"]["any_of"].append(
            {"type": "PROBE_EVENT", "subtype": "RUN_START"}
        )

    def widen_d5_grant(m):
        m["event_types"]["PROBE_EVENT"]["lineage"]["required_parents"]["RUN_START"]["any_of"].append(
            {"type": "AUTHORIZE_EVENT", "subtype": "GRANT"}
        )

    def widen_d5_refused(m):
        m["event_types"]["PROBE_EVENT"]["lineage"]["required_parents"]["RUN_START"]["any_of"].append(
            {"type": "COLLECT_EVENT", "subtype": "REFUSED"}
        )

    def drop_d5_rule(m):
        del m["event_types"]["PROBE_EVENT"]["payload"]["rules"]["run_matches_its_decision"]

    def wildcard_identity(m):
        m["event_types"]["IDENTITY_EVENT"]["producer_authority"]["wildcards"] = ["connector-*"]

    def undeclared_code(m):
        m["event_types"]["EXTRACT_EVENT"]["violation_codes"].append("NOT_A_DECLARED_CODE")

    def allow_confidence(m):
        m["event_types"]["LINK_EVENT"]["confidence"]["rule"] = "required"

    def drop_credential_name(m):
        for group in m["event_types"]["ASSESS_EVENT"]["payload"]["prohibited"]:
            group["names"] = [n for n in group["names"] if n != "sessionid"]

    def declare_argv(m):
        m["event_types"]["ASSESS_EVENT"]["payload"]["fields"]["argv"] = {"type": "string"}

    def surviving_stratum(m):
        m["event_types"]["EXTRACT_EVENT"]["retention"]["payload_stratum"] = 2
        m["event_types"]["EXTRACT_EVENT"]["egress"]["payload_crosses_to_local"] = True

    def layer_unenforced(m):
        groups = m["event_types"]["PROBE_EVENT"]["payload"]["prohibited"]
        m["event_types"]["PROBE_EVENT"]["payload"]["prohibited"] = [
            g for g in groups if g["names"] != ["confidence"]
        ]

    def bump_version(m):
        m["pse"]["version"] = "pse-event-1.0"

    def forbidden_string(m):
        return f"# {FORBIDDEN_CLAIM}\n"

    def duplicate_const(m):
        m["event_types"]["IDENTITY_EVENT"]["subtypes"]["EXCLUDE"]["discriminator"]["const"] = "CLUSTER"

    def drop_fixture(m):
        del m["violation_codes"]["fixtures"]["merge-circularity"]

    def second_gate(m):
        m["event_types"]["COLLECT_EVENT"]["producer_authority"]["named"].append("runner-*")

    def self_parent(m):
        m["event_types"]["PROBE_EVENT"]["lineage"]["required_parents"]["ITEM"]["any_of"] = [
            {"type": "PROBE_EVENT", "subtype": "ITEM"}
        ]
        m["event_types"]["PROBE_EVENT"]["lineage"]["allowed_parents"]["PROBE_EVENT"] = ["RUN_START", "ITEM"]

    def dead_code(m):
        # Well formed in every respect except that no rule fires it, so the
        # mutation isolates LM_CODE_UNREFERENCED. The entry carries fires_when
        # because L-34 refuses an entry without one, and a mutation that trips
        # two checks cannot claim expect_only.
        m["violation_codes"]["codes"].append({
            "code": "DEAD_CODE",
            "severity": "fail",
            "since": "pse-event-0.1",
            "fires_when": "never, which is the defect this mutation exists to prove",
        })

    def matrix_drift(m):
        m["lineage"]["matrix"]["LINK_EVENT"] = ["EXTRACT_EVENT", "PROBE_EVENT"]

    def index_drift(m):
        m["producer_authority"]["wildcards"]["connector-*"].append("LINK_EVENT")

    def required_and_prohibited(m):
        m["event_types"]["ASSESS_EVENT"]["payload"]["required"]["SENTENCE"].append("raw")

    # --- the checks a 2026-09-03 review measured as passing clean -------------

    def shallow_denylist(m):
        m["envelope"]["payload_denylist_recursion"]["mode"] = "shallow"

    def delete_denylist_mode(m):
        del m["envelope"]["payload_denylist_recursion"]["mode"]

    def widen_crossing(m):
        m["egress"]["strata_crossing_to_local"] = [1, 2, 3, 4]

    def widen_environments(m):
        m["egress"]["environments"] = ["LOCAL", "RUNNER", "CLOUD"]

    def widen_envelope_environment(m):
        m["envelope"]["fields"]["source"]["fields"]["environment"]["enum"] = ["LOCAL", "RUNNER", "CLOUD"]

    def run_from_local(m):
        m["event_types"]["PROBE_EVENT"]["payload"]["fields"]["egress"]["fields"]["environment"]["enum"] = ["ISOLATED", "LOCAL"]

    def bystander_retain(m):
        m["event_types"]["COLLECT_EVENT"]["payload"]["fields"]["bystander_disposition"]["enum"].append("retain")

    def authorize_s5(m):
        m["event_types"]["AUTHORIZE_EVENT"]["payload"]["fields"]["subject_class"]["enum"].append("S5")

    def drop_case_id(m):
        m["envelope"]["required"] = [x for x in m["envelope"]["required"] if x != "case_id"]

    def open_envelope(m):
        m["envelope"]["additional_properties"] = True

    def empty_reserved(m):
        m["envelope"]["reserved_refused"] = []

    def link_accepted(m):
        m["event_types"]["LINK_EVENT"]["payload"]["fields"]["accepted"]["const"] = True

    def one_member_cluster(m):
        m["event_types"]["IDENTITY_EVENT"]["payload"]["fields"]["members"]["min_items"] = 1

    def cross_case_lineage(m):
        m["lineage"]["based_on"]["same_case_required"] = False

    def one_check_five_times(m):
        m["event_types"]["SYSTEM_EVENT"]["payload"]["fields"]["checks_passed"]["const"] = [1, 1, 1, 1, 1]

    def fourth_credential_state(m):
        m["event_types"]["SYSTEM_EVENT"]["payload"]["fields"]["state"]["enum_by_subtype"]["CREDENTIAL_STATE"].append("retired")

    def narrow_envelope_fields(m):
        m["event_types"]["ASSESS_EVENT"]["required_envelope_fields"] = ["payload"]

    def drop_citations(m):
        m["event_types"]["ASSESS_EVENT"]["payload"]["required"]["SENTENCE"] = [
            x for x in m["event_types"]["ASSESS_EVENT"]["payload"]["required"]["SENTENCE"] if x != "citations"
        ]

    def drop_rule_when(m):
        del m["event_types"]["ASSESS_EVENT"]["payload"]["rules"]["citation_present"]["when"]

    def ambiguous_denylist(m):
        for group in m["event_types"]["ADJUDICATE_EVENT"]["payload"]["prohibited"]:
            if group["names"] == ["confidence"]:
                group["names"] = ["confidence", "review_state"]

    def extra_type_code(m):
        m["event_types"]["ASSESS_EVENT"]["violation_codes"].append("MERGE_CIRCULAR")

    def delete_generates(m):
        del m["pse"]["generates"]

    def break_generates_source(m):
        m["pse"]["generates"][1]["from"] = ["not_a_section"]

    def phrase_in_may_carry(m):
        m["layers"]["authorization"]["may_carry"].append("pivot depth")

    def delete_policy_shape(m):
        del m["lineage"]["policy_shape"]

    def delete_allowed_targets(m):
        del m["event_types"]["ADJUDICATE_EVENT"]["lineage"]["allowed_targets"]

    def drift_allowed_targets(m):
        m["event_types"]["ADJUDICATE_EVENT"]["lineage"]["allowed_targets"]["VERIFY"] = [
            "IDENTITY_EVENT", "ASSESS_EVENT", "SYSTEM_EVENT"
        ]

    def drop_expect_only(m):
        del m["violation_codes"]["fixtures"]["run-against-unauthorized-subject"]["expect_only"]

    def drop_code_source(m):
        del m["violation_codes"]["fixtures"]["run-against-unauthorized-subject"]["code_source"]

    def remap_fixture_code(m):
        m["violation_codes"]["fixtures"]["nested-layer-collapse"]["code"] = "MERGE_CIRCULAR"

    # --- the six checks no mutation reached -----------------------------------

    def drop_governed_section(m):
        # EXTRACT_EVENT rather than LINK_EVENT, because the observation layer has a
        # second type in it. Dropping a section from the only type in a layer also
        # orphans the layer, which is a second refusal for one edit.
        del m["event_types"]["EXTRACT_EVENT"]["egress"]

    def unresolvable_parent(m):
        m["event_types"]["LINK_EVENT"]["lineage"]["allowed_parents"]["EXTRACT_EVENT"] = ["CLAIM", "NOT_A_SUBTYPE"]

    def lineage_inconsistent(m):
        m["event_types"]["LINK_EVENT"]["lineage"]["required_by_subtype"]["CONTROLS"] = False

    def egress_flag_wrong(m):
        m["event_types"]["ASSESS_EVENT"]["egress"]["envelope_crosses_to_local"] = False

    def fixture_rule_missing(m):
        m["violation_codes"]["fixtures"]["merge-circularity"]["rule"] = "event_types.NO_SUCH_TYPE.payload.rules.none"

    def orphan_layer(m):
        m["layers"]["orphan"] = {"purpose": "none", "may_carry": [], "never_carries": []}

    return [
        ("drop a type", drop_type, "LM_TYPE_COUNT", False,
         "removing a type orphans its layer, its lineage matrix row, its producer index "
         "entries and the codes only it fired"),
        ("add a tenth type", add_tenth, "LM_TYPE_COUNT", False,
         "a tenth type appears in no matrix row, no producer index entry and no "
         "require_match_for_event_types list"),
        ("remove the COLLECT PERMITTED parent from RUN_START", remove_d5, "LM_D5_PARENT_MISSING", False,
         "the D5 fixture points at the entry this deletes, so the fixture map loses its "
         "rule path in the same edit"),
        ("widen RUN_START's parents with a second PROBE alternative", widen_d5_same_type, "LM_D5_PARENT_MISSING", True, ""),
        ("widen RUN_START's parents with AUTHORIZE GRANT", widen_d5_grant, "LM_D5_PARENT_MISSING", False,
         "the added alternative is outside PROBE_EVENT's allowed_parents, which refuses "
         "separately. Widening allowed_parents to match would drift the lineage matrix, so "
         "this widening cannot be made to refuse only once"),
        ("widen RUN_START's parents with COLLECT REFUSED", widen_d5_refused, "LM_D5_PARENT_MISSING", False,
         "allowed_parents grants COLLECT_EVENT only its PERMITTED subtype, so the added "
         "alternative is an unresolvable parent as well as a second dispatch path"),
        ("delete the rule binding a run to its own decision", drop_d5_rule, "LM_REQUIRED_RULE_MISSING", True, ""),
        ("add a connector-* wildcard to IDENTITY_EVENT", wildcard_identity, "LM_WILDCARD_ON_HUMAN_TYPE", False,
         "a producer granted on a type and absent from the global index is index drift too"),
        ("reference an undeclared code", undeclared_code, "LM_CODE_UNDECLARED", False,
         "a code on a type's list that no rule of that type fires is also a per-type list error"),
        ("allow confidence on LINK_EVENT", allow_confidence, "LM_CONFIDENCE_INCONSISTENT", True, ""),
        ("drop sessionid from ASSESS_EVENT's denylist", drop_credential_name, "LM_CREDENTIAL_NAMES_MISSING", False,
         "every layer's never_carries names the credential values, so dropping one from a "
         "type breaks that layer's rule in the same edit"),
        ("declare argv as a field on ASSESS_EVENT", declare_argv, "LM_REQUIRED_PROHIBITED_OVERLAP", False,
         "a new top-level payload field is also absent from its layer's may_carry, which is "
         "the other half of the same closure"),
        ("move EXTRACT_EVENT's payload to stratum 2", surviving_stratum, "LM_RT2_VIOLATION", True, ""),
        ("stop PROBE_EVENT prohibiting confidence", layer_unenforced, "LM_LAYER_NEVER_CARRIES_UNENFORCED", True, ""),
        ("bump the version without ratification", bump_version, "LM_VERSION", False,
         "every code's `since` is pinned to pse.version, so an unratified bump unpins all "
         "of them at once"),
        ("inject the forbidden compatibility claim", forbidden_string, "LM_FORBIDDEN_STRING", True, ""),
        ("give two subtypes one discriminator const", duplicate_const, "LM_SUBTYPE_DISCRIMINATOR", True, ""),
        ("delete a named fixture", drop_fixture, "LM_FIXTURE_MISSING", True, ""),
        ("give COLLECT_EVENT a second producer", second_gate, "LM_COLLECT_PRODUCER", False,
         "a producer granted on a type and absent from the global index is index drift too"),
        ("make PROBE ITEM its own only required parent", self_parent, "LM_SELF_REQUIRED_PARENT", True, ""),
        ("declare a code no rule fires", dead_code, "LM_CODE_UNREFERENCED", True, ""),
        ("drift the lineage matrix from the per-type source", matrix_drift, "LM_LINEAGE_MATRIX_DRIFT", True, ""),
        ("drift the producer index from the per-type source", index_drift, "LM_PRODUCER_INDEX_DRIFT", True, ""),
        ("require a field the type prohibits", required_and_prohibited, "LM_REQUIRED_PROHIBITED_OVERLAP", True, ""),
        ("make the payload denylist shallow", shallow_denylist, "LM_DENYLIST_NOT_RECURSIVE", True, ""),
        ("delete the denylist recursion mode", delete_denylist_mode, "LM_DENYLIST_NOT_RECURSIVE", True, ""),
        ("let stratum 1 cross to LOCAL", widen_crossing, "LM_EGRESS_PINNED", True, ""),
        ("restore the FOUNDATION draft's three environments", widen_environments, "LM_EGRESS_PINNED", True, ""),
        ("widen the envelope's environment enum", widen_envelope_environment, "LM_EGRESS_PINNED", True, ""),
        ("let a run execute from LOCAL", run_from_local, "LM_EGRESS_PINNED", True, ""),
        ("add retain to the bystander dispositions", bystander_retain, "LM_CLASS_F_ENUM_WIDENED", True, ""),
        ("add S5 to the authorizable classes", authorize_s5, "LM_CLASS_F_ENUM_WIDENED", True, ""),
        ("drop case_id from the envelope's required list", drop_case_id, "LM_PINNED_INVARIANT", False,
         "every type's required_envelope_fields still names case_id, so dropping it from "
         "the envelope leaves nine types requiring a field the envelope no longer knows"),
        ("open the envelope to unknown properties", open_envelope, "LM_PINNED_INVARIANT", True, ""),
        ("empty the reserved-key list", empty_reserved, "LM_CONFIDENCE_INCONSISTENT", True, ""),
        ("let a LINK arrive accepted", link_accepted, "LM_PINNED_INVARIANT", True, ""),
        ("lower the cluster member minimum to one", one_member_cluster, "LM_PINNED_INVARIANT", True, ""),
        ("permit cross-case lineage", cross_case_lineage, "LM_PINNED_INVARIANT", True, ""),
        ("count one shred check five times", one_check_five_times, "LM_PINNED_INVARIANT", True, ""),
        ("add a fourth credential state", fourth_credential_state, "LM_PINNED_INVARIANT", True, ""),
        ("narrow a type's required envelope fields", narrow_envelope_fields, "LM_ENVELOPE_FIELDS_NOT_SUPERSET", True, ""),
        ("drop citations from ASSESS_EVENT's required list", drop_citations, "LM_RULE_REQUIRES_UNMET", True, ""),
        ("take the condition off a rule", drop_rule_when, "LM_RULE_CONDITION_MISSING", True, ""),
        ("put one prohibited name in two groups under different codes", ambiguous_denylist, "LM_DENYLIST_CODE_AMBIGUOUS", True, ""),
        ("list a code on a type no rule of it fires", extra_type_code, "LM_PER_TYPE_CODES_EXTRA", True, ""),
        ("delete the generation map", delete_generates, "LM_GENERATES_INCOMPLETE", True, ""),
        ("point a generation source at nothing", break_generates_source, "LM_GENERATES_UNRESOLVED", True, ""),
        ("write an English phrase into a layer's may_carry", phrase_in_may_carry, "LM_LAYER_MAY_CARRY_DRIFT", True, ""),
        ("delete the lineage policy shape", delete_policy_shape, "LM_POLICY_SHAPE_MISSING", True, ""),
        ("delete ADJUDICATE_EVENT's allowed_targets", delete_allowed_targets, "LM_ALLOWED_TARGETS_MISSING", True, ""),
        ("point a disposition at targets its parents do not allow", drift_allowed_targets, "LM_ALLOWED_TARGETS_DRIFT", True, ""),
        ("take expect_only off a D5 fixture", drop_expect_only, "LM_FIXTURE_EXPECT_ONLY_MISSING", True, ""),
        ("take the code source off the D5 fixture", drop_code_source, "LM_FIXTURE_CODE_UNCHECKABLE", True, ""),
        ("remap a fixture to an unrelated code", remap_fixture_code, "LM_FIXTURE_RULE_UNRESOLVED", True, ""),
        ("drop a governed section from a type", drop_governed_section, "LM_TYPE_SECTION_MISSING", True, ""),
        ("name a parent subtype that does not exist", unresolvable_parent, "LM_LINEAGE_PARENT_UNRESOLVED", True, ""),
        ("make lineage optional for a subtype that requires parents", lineage_inconsistent, "LM_LINEAGE_INCONSISTENT", True, ""),
        ("flip an egress flag against its stratum", egress_flag_wrong, "LM_EGRESS_INCONSISTENT", True, ""),
        ("point a fixture at a rule path that does not exist", fixture_rule_missing, "LM_FIXTURE_RULE_UNRESOLVED", True, ""),
        ("define a layer no type uses", orphan_layer, "LM_LAYER_UNUSED", True, ""),
        ("truncate a code's fires_when at a comma, as an unquoted flow mapping does",
         truncate_fires_when, "LM_CODE_ENTRY_KEYS", True, ""),
        ("blank a code's fires_when", blank_fires_when, "LM_CODE_ENTRY_KEYS", True, ""),
    ]


def self_test(model: dict, text: str) -> int:
    baseline = check(model, text)
    if baseline:
        print("self-test cannot run: the unmutated model is not clean", file=sys.stderr)
        for fnd in baseline:
            print(fnd.render(), file=sys.stderr)
        return 1
    failures = 0
    cascading = 0
    exercised: set[str] = set()
    muts = _mutations()
    for desc, mutate, expected, only, why in muts:
        m = copy.deepcopy(model)
        t = text
        new_text = mutate(m)
        if isinstance(new_text, str):
            t = text + new_text
        fired = {fnd.code for fnd in check(m, t)}
        exercised |= fired
        if expected not in fired:
            ok, note = False, f", fired {sorted(fired)}"
        elif only and fired != {expected}:
            ok, note = False, f", also fired {sorted(fired - {expected})} and claims expect_only"
        else:
            ok, note = True, ""
        if ok and not only:
            cascading += 1
        failures += 0 if ok else 1
        mark = "refused" if ok else "PASSED  "
        print(f"  {mark}  {desc:62} expected {expected}{note}")
        if ok and not only:
            print(f"              cascades, and that is expected: {why}")
    print()
    if failures:
        print(
            f"validate_layer_model --self-test: {failures} mutation(s) were not refused as "
            "claimed. A gate nobody has watched fail is an assumption (HYGIENE.md section 2).",
            file=sys.stderr,
        )
        return 1
    print(
        f"validate_layer_model --self-test ok: {len(muts)} deliberate breaks, {len(muts)} refused, "
        f"{len(muts) - cascading} of them by the expected code alone, {cascading} cascading with a "
        f"stated reason. {len(exercised)} distinct codes exercised."
    )
    return 0


# ---------------------------------------------------------------------------
# entry
# ---------------------------------------------------------------------------


def load() -> tuple[dict, str]:
    text = MODEL.read_text(encoding="utf-8")
    model = yaml.safe_load(text)
    if not isinstance(model, dict):
        raise ValueError("the model did not parse to a mapping")
    return model, text


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Layer model self-lint.")
    ap.add_argument("--quiet", action="store_true", help="Print only on failure.")
    ap.add_argument("--self-test", action="store_true", help="Break the model in memory and assert each break is refused.")
    args = ap.parse_args(argv)

    try:
        model, text = load()
    except FileNotFoundError:
        print(
            "REFUSED LAYER_MODEL_UNREADABLE\n"
            f"  where: {MODEL.relative_to(ROOT)}\n"
            "  what:  the layer model does not exist, so nothing can be generated from it\n"
            "  moves: write spec/layer-model.yaml, or move the schema gate to PENDING in "
            "tools/validate_conformance.py",
            file=sys.stderr,
        )
        return 2
    except (yaml.YAMLError, ValueError) as exc:
        print(
            "REFUSED LAYER_MODEL_UNREADABLE\n"
            f"  where: {MODEL.relative_to(ROOT)}\n"
            f"  what:  the file is not parseable YAML: {exc}\n"
            "  moves: fix the syntax; the generator and this gate read the same parse",
            file=sys.stderr,
        )
        return 2

    if args.self_test:
        return self_test(model, text)

    findings = check(model, text)

    if gate_log:
        if findings:
            for fnd in findings:
                gate_log.record(GATE, "refuse", code=fnd.code, where=fnd.where)
        else:
            gate_log.record(GATE, "pass")

    if findings:
        for fnd in findings:
            print(fnd.render(), file=sys.stderr)
            print(file=sys.stderr)
        print(
            f"validate_layer_model: {len(findings)} violation(s). "
            "rule: spec/layer-model.yaml is rank 3 and generates the schema and policy; "
            "CLAUDE.md design gate 1.",
            file=sys.stderr,
        )
        return 1

    if not args.quiet:
        types = model.get("event_types") or {}
        n_sub = sum(len(t.get("subtypes") or {}) for t in types.values())
        n_codes = len((model.get("violation_codes") or {}).get("codes") or [])
        n_fx = len((model.get("violation_codes") or {}).get("fixtures") or {})
        print(
            f"validate_layer_model ok: {len(types)} types, {n_sub} subtypes, {n_codes} codes, "
            f"{n_fx} fixtures mapped, D5 parent present, {model['pse']['version']} {model['pse']['status']}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
