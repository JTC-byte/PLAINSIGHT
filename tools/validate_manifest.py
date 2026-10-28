#!/usr/bin/env python3
"""Connector manifest gate: one manifest, or every manifest under connectors/.

A connector contributes declarations and the platform owns every pixel
(`docs/PLAINSIGHT-design.md` section 6). The manifest is where a connector says
what it consumes, what it emits, what a zero result means, how its health is
proven, which people it reaches beyond its named selector, and how it touches a
platform. This tool is the one CI check section 6.4 keeps, plus the doctrine
checks a schema cannot express.

Modes:

  <path>        one manifest, every check below
  --all         every connectors/*/manifest.yaml, every check below. With zero
                manifests it says that nothing was validated and exits 0 (MF-R3)
  --shape <path>  the schema gate only, for authoring feedback. It prints that no
                conformance claim is made and exits 0 when the shape holds
  --self-test   breaks a manifest in memory and on a scratch disk outside the
                repository, and asserts each break is refused by its own code or
                permitted as stated, plus the controls named in self_test()
  --quiet       prints nothing on a pass, with two exceptions that are states
                rather than passes and print regardless: --all over zero
                manifests says that no manifest was validated, and --shape says
                that no conformance claim is made

--all reads every directory under connectors/. A directory whose name starts
with . or _ is not a connector, because the id pattern admits neither; one that
holds a manifest file is refused (MANIFEST_DIRECTORY_HIDDEN) rather than passed
over, and one that holds none is ignored.

Every mode but --shape first checks both schemas against the draft 2020-12
metaschema and reconciles the enums they copy against their sources, so a run
with zero manifests still checks something real.

The checks, each with its code:

  shape        schema/connector-manifest.schema.json. A schema error is reported
               under the narrowest code that names it: MANIFEST_KIND_UNKNOWN,
               MANIFEST_KIND_DISAGREES, MANIFEST_EMIT_LAYER,
               BYSTANDER_DISPOSITION_OUT_OF_SET, MANIFEST_BYSTANDER_UNDECLARED,
               MANIFEST_BYSTANDER_CLASS_UNKNOWN, MANIFEST_CANARY_MISSING,
               MANIFEST_CANARY_NEGATIVE_UNSOUND, MANIFEST_CANARY_SUBJECT_CLASS,
               MANIFEST_CANARY_INPUT_VALUE, MANIFEST_RENDER_MARKUP,
               MANIFEST_LINEAGE_DURATION, MANIFEST_INTERACTION_CLASS_INVALID,
               MANIFEST_INTERACTION_EXCLUDED, MANIFEST_AUTH_NOT_A_REFERENCE,
               MANIFEST_PARAM_DEFAULT_INVALID, or MANIFEST_SHAPE_INVALID where no
               narrower code applies. A key the YAML repeats is refused before
               the schema reads the file (MANIFEST_DUPLICATE_KEY), because the
               parser keeps only the last value and the first is never checked
  params       an enum parameter's default is one of its values
               (MANIFEST_PARAM_DEFAULT_INVALID); the schema ties every other
               default's type to its parameter's type
  registry     every consumed and emitted selector is a key in
               ontology/selectors.yaml (MANIFEST_SELECTOR_UNREGISTERED); a key the
               registry lists as proposed may be consumed and may not be emitted
               until the pin of record stamps the registry
               (MANIFEST_SELECTOR_UNSTAMPED); a platform qualifier is present
               exactly where the key's registry form binds a platform, and an
               emit may name it instead by platform_from_item on a manifest
               whose probe_unit is endpoint, never both (MANIFEST_SELECTOR_PLATFORM,
               MF-R17); an entity is a registry entity
               (MANIFEST_ENTITY_UNKNOWN) and none of its fields is named for a
               registry key (MANIFEST_ENTITY_FIELD_IS_SELECTOR); an emit's
               constraint_semantics, generation_method and requires_validation_by
               agree with the registry (MANIFEST_EMIT_DISAGREES_WITH_REGISTRY)
  canaries     the known_negative names a declared negative class, and every
               canary input is keyed by a consumed input with every required one
               present (MANIFEST_CANARY_NEGATIVE_UNSOUND,
               MANIFEST_CANARY_INPUT_MISMATCH); every canary input is a slot-name
               placeholder or a typed token synthetic/GROUND_TRUTH.yaml carries
               (MANIFEST_CANARY_INPUT_VALUE, MF-R8); the golden fixture exists
               (MANIFEST_GOLDEN_FIXTURE_ABSENT)
  refusals     one refusal fixture per required input, each present, linted
               against conformance/connector-harness/fixture.schema.json with no
               repeated key and every input a placeholder by the same rule as a
               canary's, of this connector and version, a refusal, withholding
               the input it names and supplying every other required input, named
               by one entry only, with a declared code
               (MANIFEST_REFUSAL_FIXTURE_MISSING, _ABSENT, _SHAPE, _MISMATCH,
               MANIFEST_REFUSAL_CODE_UNDECLARED)
  targeting    consumes names a selector, and the command template names a
               consumed input, a required one where any is declared
               (MANIFEST_TARGETING_NO_SELECTOR); kind agrees with emits and
               blocks (MANIFEST_KIND_DISAGREES); an expansion, continuous or geo
               connector, or one taking a geo_area as a consumed input or a
               parameter, declares its bystanders (MANIFEST_BYSTANDER_UNDECLARED);
               a connector that reaches the people inside an area declares a
               class for them, and none is ratified, so every such connector
               refuses (MANIFEST_BYSTANDER_CLASS_UNKNOWN, MF-R2)
  slots        the command template and render slots name declared inputs, and
               render columns name emitted fields (MANIFEST_COMMAND_TEMPLATE_SLOT,
               MANIFEST_RENDER_SLOT_UNKNOWN)
  honesty      an authenticating connector declares logged exposure and an
               authenticated read (MANIFEST_EXPOSURE_UNDERSTATED,
               MANIFEST_INTERACTION_DISAGREES)
  R7           interaction_class binds only while the pin of record stamps R7,
               read through tools/pin_of_record.py (MANIFEST_INTERACTION_UNRATIFIED)
  layout       connectors/<id>/manifest.yaml, with id equal to the directory
               (MANIFEST_ABSENT, MANIFEST_ID_DISAGREES_WITH_DIRECTORY), and no
               manifest file under a directory --all does not read
               (MANIFEST_DIRECTORY_HIDDEN)
  drift        the schemas' copied enums equal their sources (MANIFEST_SCHEMA_DRIFT)

Readings this tool and the two schemas took, each an agent reading awaiting the
operator:

  MF-R1  interaction_class. docs/THE-GAMEPLAN.md section 3.0 lists R7 as
         undrafted, and the Step 12 brief read R7 as carrying no dated row. The
         pin of record carries R7's conclusion row dated 2026-08-26, and
         doctrine/SUBJECT_SELECTION.md section 11 says R7 is stamped. The check
         reads that row through pin_of_record (PIN-R9) and permits while it
         stands. The two tokens are FOUNDATION section 4.3's draft, and whether
         they encode R7's line, which refuses a view the platform surfaces to the
         subject, is open.
  MF-R2  The bystander class vocabulary. Doctrine names populations in prose and
         closes no list. The schema takes SS-10's three, channel_members,
         followers and organization_staff, and nothing else. None of the three
         is a class for the people inside an area, so AREA_CLASSES below is
         empty, and a connector of kind geo, or one taking a geo_area as a
         consumed input or a parameter, is refused under
         MANIFEST_BYSTANDER_CLASS_UNKNOWN whatever class it declares. A geo
         connector passes only after a class for people inside an area is
         ratified and added both to the schema enum and to AREA_CLASSES, which
         is Class F.
  MF-R3  --all with zero manifests exits 0 and the kernel gate counts it as a
         pass of what it checked, the two schemas and the drift reconciliation,
         never of any manifest. The alternative is a distinct printed state such
         as EMPTY, which the aggregator does not have.
  MF-R4  induces_disclosure is absent from the interaction_class enum, because
         FOUNDATION section 4.3 marks it excluded rather than unimplemented and R7
         refuses anything the subject can observe. It is refused by schema under
         its own code.
  MF-R5  canary_subject_class is synthetic or institutional. doctrine/RETENTION.md
         RT-15 cuts consented, and docs/THE-GAMEPLAN.md section 5.1 and the Step
         12 brief list it; rank 1 wins. The field is top level because
         tools/validate_retention.py measures RT-15's second part there.
  MF-R6  Registry membership is checked here rather than inlined as a schema
         enum, so ontology/selectors.yaml stays the one place a selector type is
         defined. A proposed key counts as stamped only through a whole-artifact
         row for ontology/selectors.yaml, because the pin has no per-key stamp;
         a per-key stamp is a pin-format change and the operator's.
  MF-R7  An entity field such as a display name is not a registry key, and
         EXTRACT_EVENT CLAIM requires selector_type to be one, so entity fields
         are recorded and have no wire form in pse-event-0.1. A field named for
         a registry key is refused, so a proposed or registered datum is emitted
         as a selector, where the stamp and the registry semantics apply. Every
         other field name is open: the registry's entities block declares no
         field list, so a datum renamed away from its key passes, and closing
         the field vocabulary is a registry decision and the operator's.
  MF-R8  Canary and fixture inputs are placeholders only, resolved at run time.
         The schema pattern is tools/validate_cast.py PLACEHOLDER_RE, which any
         text in angle brackets matches, so this tool also requires each input
         to be a slot name, a lowercase word in angle brackets, or a typed
         token synthetic/GROUND_TRUTH.yaml carries, with no trailing newline.
         That refuses a bracketed address, phone, URL or at-sign handle. It
         cannot refuse a bare handle written as a slot name, because the two
         have one shape; the inputs are a narrowed selector surface, not a
         closed one.
  MF-R9  Vocabularies the design leaves open are closed narrow: cardinality,
         cost.class, exposure.level, rate_limit.scope and backoff, cadence, and
         render.shape. Each schema description names its source.
  MF-R10 refusal_code is read from spec/layer-model.yaml violation_codes. No
         declared code names an adapter refusing its input; the self-test uses
         PAYLOAD_FIELD_MISSING as the nearest, and a narrower code is a layer
         model change.
  MF-R11 A retain or other out-of-set disposition takes the declared code
         BYSTANDER_DISPOSITION_OUT_OF_SET; an absent declaration takes the
         tool-local MANIFEST_BYSTANDER_UNDECLARED, so the two breaks are told
         apart although SS-10 speaks of one code for both.
  MF-R12 A reference connector executes nothing, so it carries no health,
         lineage, auth, rate_limit, params or negative semantics, and no canary
         is required of it.
  MF-R13 upstream is not a manifest key, and the schema refuses it as unknown.
         docs/PLAINSIGHT-design.md line 490 keeps a declared upstream as a prior
         for the first 20 co-runs and line 839 warns when it is absent, while
         line 1036 cuts upstream as authoritative independence and the section
         6.1 manifest carries no such key. Nothing reads a declared upstream
         until measured concordance is built, so the key is left out rather than
         admitted with no reader; adding it is a schema change.
  MF-R14 A parameter of type geo_area reaches the people inside an area exactly
         as a consumed geo_area does, so it counts as reach. A parameter of type
         selector_ref passes a selector outside consumes, where neither the
         registry, the canary nor the refusal-fixture check reads it; it is not
         refused, because the design freezes the eight parameter types, and
         whether it should route through consumes is open.
  MF-R15 The fixture schema pins an event count or a refusal code and nothing
         else. docs/PLAINSIGHT-FOUNDATION.md section 4.4 also names presence,
         absence, lineage and forbidden_paths, which have no key yet; an expect
         block is a schema addition left for the runner that reads it.
  MF-R16 The command template names at least one consumed input, a required
         one where any is declared, so argv carries the selector the gate
         evaluated. consumes.required may still be empty, because a connector
         whose inputs are alternatives declares them all optional. A slot check
         cannot prove the argv does not also sweep beyond that input; the
         bystander declaration and the dispatch estimate own that.
  MF-R17 An emit of a key whose registry form binds a platform may declare
         platform_from_item: true in place of platform, meaning that each
         emitted claim's platform is the one the PROBE_EVENT ITEM locator of
         its item names. docs/PLAINSIGHT-design.md section 6.2 draws a sweep
         that emits one selector across about 120 endpoints with probe_unit
         endpoint, and the schema took one platform per emit, so the first
         sweep connector refused here (reading SH-R5 in
         connectors/sherlock/README.md). The field is permitted only where
         health.probe_unit is endpoint, because only there is each item one
         endpoint on one platform. Exactly one of platform and
         platform_from_item is required where the key's form binds a
         platform, and neither is permitted where it binds none. Nothing here
         checks that the token the adapter writes names a real platform; the
         connector's own reading states its rule (SH-R18 for Sherlock), and
         amendment 9.14 of the design records the change for the maintainer.

What this tool does not catch: SS-14 item 3's check of read verbs against an
adapter's methods waits for an adapter. A repeated key in a YAML manifest or a
JSON fixture line is refused, under MANIFEST_DUPLICATE_KEY and
MANIFEST_REFUSAL_FIXTURE_SHAPE.

Exit codes: 0 pass, 1 refusal, 2 a file this tool reads could not be read: the
manifest is absent or not YAML, or a schema, the registry, the layer model, the
retention policy, the cast draft or the pin of record is absent or unreadable.
"""

from __future__ import annotations

import argparse
import contextlib
import copy
import io
import json
import os
import re
import sys
import tempfile
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print(
        "REFUSED MANIFEST_TOOL_INPUT_UNREADABLE\n"
        "  what:  PyYAML is not installed, so no manifest can be parsed\n"
        "  moves: pip install pyyaml",
        file=sys.stderr,
    )
    sys.exit(2)

try:
    from jsonschema import Draft202012Validator
    from jsonschema.exceptions import SchemaError
except ImportError:  # pragma: no cover
    print(
        "REFUSED MANIFEST_TOOL_INPUT_UNREADABLE\n"
        "  what:  jsonschema is not installed, so the shape gate cannot run\n"
        "  moves: pip install jsonschema",
        file=sys.stderr,
    )
    sys.exit(2)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pin_of_record  # noqa: E402  the one reader of a stamp
import validate_cast  # noqa: E402  the placeholder grammar
import validate_ontology  # noqa: E402  the registry loader and the code vocabulary

try:
    import gate_log
except Exception:  # telemetry must never be able to break a gate
    gate_log = None

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schema" / "connector-manifest.schema.json"
FIXTURE_SCHEMA = ROOT / "conformance" / "connector-harness" / "fixture.schema.json"
LAYER_MODEL = ROOT / "spec" / "layer-model.yaml"
RETENTION_POLICY = ROOT / "policy" / "retention.yaml"
CONNECTORS = ROOT / "connectors"
REGISTRY_REL = "ontology/selectors.yaml"
GATE = "connector-manifest"

#: The decision whose row the interaction_class check reads (MF-R1).
R7 = "R7"

#: Kinds that collect on populations by construction (SS-10).
WIDENING_KINDS = ("expansion", "continuous", "geo")

#: Bystander classes that name the people inside an area (MF-R2). Empty: no
#: such class is ratified, so every connector that reaches an area refuses. A
#: class enters here only with the same ratified Class F change that adds it to
#: the schema's class enum.
AREA_CLASSES: tuple[str, ...] = ()

#: A canary or fixture input beyond the schema's pattern (MF-R8): a slot name,
#: or a typed token the cast draft carries. fullmatch, so no trailing newline.
SLOT_PLACEHOLDER_RE = re.compile(r"<[a-z][a-z0-9_]*>")
TYPED_TOKEN_RE = re.compile(r"<[a-z_]+:[^<>\n]+>")

#: Keys and values that carry a retention duration. RT-1 sets lifetime by
#: stratum, so none of them belongs in a manifest.
DURATION_KEYS = {
    "retain", "retention", "retain_until", "ttl", "duration", "expires",
    "expires_after", "expires_after_days", "keep", "lifetime", "retention_days",
}
DURATION_VALUE_RE = re.compile(
    r"^\s*(forever|permanent|\d+\s*(s|m|h|d|w|y|mo|days?|weeks?|months?|years?))\s*$", re.I
)
SLOT_RE = re.compile(r"\{([^{}]*)\}")
SAFE_KEY_RE = re.compile(r"^[a-z_][a-z0-9_]{0,40}$")
MISSING_RE = re.compile(r"^'([^']+)' is a required property$")


class ToolFailure(Exception):
    """A file this tool reads could not be read. Exit 2, never a refusal."""

    def __init__(self, where: str, what: str, moves: str):
        super().__init__(what)
        self.where, self.what, self.moves = where, what, moves

    def render(self) -> str:
        return (
            "REFUSED MANIFEST_TOOL_INPUT_UNREADABLE\n"
            f"  where: {self.where}\n"
            f"  what:  {self.what}\n"
            f"  moves: {self.moves}"
        )


#: Governed prose. Each code: the rule that refuses it, and the legal moves.
CODES: dict[str, tuple[str, str]] = {
    "MANIFEST_SHAPE_INVALID": (
        "schema/connector-manifest.schema.json, the one CI check docs/PLAINSIGHT-design.md section 6.4 keeps",
        "correct the key or value named above; run python tools/validate_manifest.py --shape <path> "
        "for structure-only feedback while authoring; or change the schema in a reviewed change, "
        "which is Class F where it widens reach",
    ),
    "MANIFEST_KIND_UNKNOWN": (
        "docs/PLAINSIGHT-design.md section 6: five shapes, and new shapes are a platform release "
        "(CLAUDE.md design gate 8)",
        "declare one_shot, expansion, continuous, reference or geo; or fit the output to an existing "
        "shape in the adapter; or propose a new shape as a platform release, which changes this "
        "schema and spec/layer-model.yaml together",
    ),
    "MANIFEST_KIND_DISAGREES": (
        "the kind conditionals in schema/connector-manifest.schema.json and docs/PLAINSIGHT-design.md "
        "section 6.1",
        "add what the kind requires (continuous with a coverage_proof for continuous, routing roster "
        "for expansion, executable false and methods for reference, a consumed geo_area for geo, a "
        "ManualTask only on reference, probe_unit subscription exactly on continuous); or remove what "
        "it forbids; or change kind to the shape the connector has",
    ),
    "MANIFEST_EMIT_LAYER": (
        "docs/PLAINSIGHT-design.md section 6.1: a connector emits layer observation only, structurally",
        "set layer to observation; to propose an identity, declare an inference_hint, which the "
        "platform materializes as a proposed, unaccepted LINK_EVENT; or move the logic to a matcher, "
        "which emits LINK_EVENT as matcher-*",
    ),
    "BYSTANDER_DISPOSITION_OUT_OF_SET": (
        "doctrine/SUBJECT_SELECTION.md SS-10, with R8's v0.1 pair count_only and refuse stamped "
        "2026-08-27; spec/layer-model.yaml declares this code",
        "declare count_only or refuse, the pair R8 stamped for v0.1, whose meaning "
        "doctrine/SUBJECT_SELECTION.md governs and this tool does not restate; retain is reachable "
        "only by a dated Class F row in doctrine/DOCTRINE_STATUS.md followed by a schema change, "
        "never by a manifest edit",
    ),
    "MANIFEST_BYSTANDER_UNDECLARED": (
        "doctrine/SUBJECT_SELECTION.md SS-10: an undeclared bystander class is refused at manifest "
        "validation, because bystanders never pass through the gate",
        "set bystanders.reach to declared and list each class reached with an estimate method and a "
        "disposition; named_selector_only is legal only for a one_shot or reference connector that "
        "consumes no geo_area; or narrow the connector so it reaches no one else",
    ),
    "MANIFEST_BYSTANDER_CLASS_UNKNOWN": (
        "doctrine/SUBJECT_SELECTION.md SS-10, closed narrow by reading MF-R2; no class for the "
        "people inside an area is ratified",
        "use channel_members, followers or organization_staff where one fits a connector that "
        "reaches no area; or narrow the connector so it does not reach that population, which for "
        "an area means dropping kind geo and every geo_area input and parameter; or put a new "
        "class to the operator, which is Class F because it widens who can be collected on",
    ),
    "MANIFEST_CANARY_MISSING": (
        "docs/PLAINSIGHT-design.md sections 6.1 and 7.2: no manifest merges without both canaries, "
        "and the known_negative is the one that catches precision drift",
        "declare health.canaries.known_positive and known_negative with placeholder inputs; or, for "
        "a connector that executes nothing, declare kind reference",
    ),
    "MANIFEST_CANARY_NEGATIVE_UNSOUND": (
        "docs/PLAINSIGHT-design.md section 7.2: a guaranteed-nonexistent input returns zero, in a "
        "negative class the source can tell apart",
        "set expect.result_count to 0 and expect.negative_class to one of distinguishable_negatives; "
        "or add the class to distinguishable_negatives if the source genuinely tells it apart",
    ),
    "MANIFEST_CANARY_SUBJECT_CLASS": (
        "doctrine/RETENTION.md RT-15: canary_subject_class is required, synthetic or institutional, "
        "and consented is deliberately absent",
        "declare synthetic for a cast persona, or institutional for an account that is not a natural "
        "person (N0); a consented canary needs a separately ratified indirection, never a value here",
    ),
    "MANIFEST_CANARY_INPUT_VALUE": (
        "doctrine/RETENTION.md RT-15 and AGENTS.md section 4: no selector value in a tracked file; "
        "the <...> grammar tools/validate_cast.py enforces",
        "replace the value with a slot name in angle brackets, a lowercase word such as "
        "<cast_linked_handle>, or with a typed token copied from synthetic/GROUND_TRUTH.yaml, which "
        "the canary runner resolves from the sealed cast at run time; and keep the value out of any "
        "commit, because git history is the one store a crypto-shred cannot reach",
    ),
    "MANIFEST_CANARY_INPUT_MISMATCH": (
        "docs/PLAINSIGHT-design.md section 6.5 step 3: a canary exercises the inputs the manifest "
        "declares",
        "key each canary input by a consumes as name, and give every required input a placeholder",
    ),
    "MANIFEST_GOLDEN_FIXTURE_ABSENT": (
        "docs/PLAINSIGHT-design.md section 6.4: the golden fixture replays green",
        "capture the golden fixture during onboarding against an S2 or N0 target and place it at the "
        "named path; or correct the path",
    ),
    "MANIFEST_RENDER_MARKUP": (
        "docs/PLAINSIGHT-design.md section 6: no connector may contribute UI, and render is slot "
        "declarations only",
        "remove the markup and declare the slot; map the field to a renderer the platform has through "
        "columns or title_template; or park the field in the raw pane",
    ),
    "MANIFEST_RENDER_SLOT_UNKNOWN": (
        "docs/PLAINSIGHT-design.md section 6.2: a renderer shows declared fields",
        "name an emitted selector key or entity field in columns, and a consumes as name or a params "
        "key in a template slot; or emit the field first",
    ),
    "MANIFEST_LINEAGE_DURATION": (
        "doctrine/RETENTION.md RT-1 and RT-2: lifetime is set by stratum in policy/retention.yaml, "
        "and RT-8 scopes a text blob by retain_until",
        "delete the duration and keep lineage.retention_stratum raw_capture; a retention duration "
        "changes only in policy/retention.yaml, which is Class F and needs a dated row",
    ),
    "MANIFEST_INTERACTION_CLASS_INVALID": (
        "doctrine/SUBJECT_SELECTION.md SS-14 item 3 under R7",
        "declare passive_unauthenticated or passive_authenticated_read",
    ),
    "MANIFEST_INTERACTION_EXCLUDED": (
        "doctrine/SUBJECT_SELECTION.md SS-14 item 3 under R7: anything the subject can observe "
        "happened is refused; docs/PLAINSIGHT-FOUNDATION.md section 4.3 marks induces_disclosure "
        "excluded, not unimplemented",
        "remove the interaction so the connector only reads; or drop the connector; no manifest edit "
        "and no authorization file unlocks it",
    ),
    "MANIFEST_INTERACTION_DISAGREES": (
        "CLAUDE.md design gate 6, and doctrine/SUBJECT_SELECTION.md SS-13 on whose account looks",
        "declare passive_authenticated_read on a connector with an auth pool and "
        "passive_unauthenticated on one without; or add or remove the auth block so it says what the "
        "connector does",
    ),
    "MANIFEST_INTERACTION_UNRATIFIED": (
        "doctrine/DOCTRINE_STATUS.md is the pin of record and an unratified criterion refuses rather "
        "than permits; interaction_class resolves against R7",
        "the operator ratifies R7 with a dated row in doctrine/DOCTRINE_STATUS.md; or run "
        "python tools/validate_manifest.py --shape <path> for authoring feedback, which makes no "
        "conformance claim",
    ),
    "MANIFEST_SELECTOR_UNREGISTERED": (
        "docs/PLAINSIGHT-FOUNDATION.md D2: a selector type not in ontology/selectors.yaml is refused "
        "at manifest validation",
        "map the field to an existing registry key; or propose a registry addition, reviewed once "
        "for every connector; or park the output in the raw pane (docs/PLAINSIGHT-design.md section "
        "6.5 step 4)",
    ),
    "MANIFEST_SELECTOR_UNSTAMPED": (
        "ontology/selectors.yaml ontology.proposed: a proposed key binds nothing until the operator "
        "stamps it",
        "consume the key, which is permitted, and emit a key that is not proposed; or the operator "
        "stamps the registry with a dated whole-artifact row in doctrine/DOCTRINE_STATUS.md",
    ),
    "MANIFEST_ENTITY_UNKNOWN": (
        "ontology/selectors.yaml entities, a closed set",
        "name one of the registry's entity types; or emit the field as a registered selector",
    ),
    "MANIFEST_ENTITY_FIELD_IS_SELECTOR": (
        "ontology/selectors.yaml: a registry key is a selector, emitted as one so its stamp and its "
        "registry semantics apply; an entity field has no wire form (reading MF-R7)",
        "emit the datum as a selector emit under its registry key, where a proposed key waits for "
        "its stamp; or, where the field is an attribute and not that selector, rename it to say "
        "what it holds",
    ),
    "MANIFEST_SELECTOR_PLATFORM": (
        "ontology/selectors.yaml: a key's form says whether it binds a platform, and a handle with "
        "no platform is not a handle; an emit names that platform once, by platform or, where "
        "health.probe_unit is endpoint, by platform_from_item (reading MF-R17)",
        "where the form binds a platform and none is named, add platform, or on an emit of an "
        "endpoint sweep declare platform_from_item: true; where both are named, keep one; where the "
        "form binds none, remove platform and platform_from_item, or use a key whose form binds "
        "none; where platform_from_item sits on a manifest whose probe_unit is not endpoint, name "
        "the platform with platform, or set probe_unit to endpoint only if each item is one endpoint",
    ),
    "MANIFEST_PARAM_DEFAULT_INVALID": (
        "docs/PLAINSIGHT-design.md section 6.1: the run form is generated from params and nothing "
        "else, so a default holds a value its parameter can take",
        "give the default the type its parameter names, a boolean for bool, an integer for int and "
        "a string for string and enum, and an enum default one of its values; or remove the "
        "default so the run form starts empty",
    ),
    "MANIFEST_DUPLICATE_KEY": (
        "YAML keeps only the last of two equal keys, so the first value is never checked by any "
        "gate and still sits in a tracked file",
        "delete the repeated key and keep the one value the manifest means; and keep any selector "
        "value out of every commit",
    ),
    "MANIFEST_DIRECTORY_HIDDEN": (
        "docs/THE-GAMEPLAN.md section 1.2: connectors/<id>/manifest.yaml, and the id pattern admits "
        "no leading . or _, so --all reads no directory so named; a manifest no gate reads is "
        "refused rather than reported absent",
        "rename the directory to the manifest's id; or move the manifest out of connectors/; or "
        "delete the draft",
    ),
    "MANIFEST_EMIT_DISAGREES_WITH_REGISTRY": (
        "docs/PLAINSIGHT-FOUNDATION.md D2: the registry is the one place a selector's semantics are "
        "defined",
        "remove the field so the registry's value applies, or copy the registry's value exactly; a "
        "change of semantics is a registry change",
    ),
    "MANIFEST_REFUSAL_FIXTURE_MISSING": (
        "docs/PLAINSIGHT-FOUNDATION.md section 4.3, the ZMeta harness rule: one refusal fixture per "
        "required input field; docs/THE-GAMEPLAN.md Step 12",
        "add a health.refusal_fixtures entry for the input and a fixture line that withholds it; or "
        "move the input to consumes.optional if the adapter runs without it",
    ),
    "MANIFEST_REFUSAL_FIXTURE_ABSENT": (
        "docs/PLAINSIGHT-FOUNDATION.md section 4.3: a refusal fixture is a file, not a declaration",
        "write the fixture line in the named file; or correct the path or the id",
    ),
    "MANIFEST_REFUSAL_FIXTURE_SHAPE": (
        "conformance/connector-harness/fixture.schema.json: an unknown expectation key is a caught "
        "typo, and event_count is required whenever result is events",
        "correct the line against the fixture schema",
    ),
    "MANIFEST_REFUSAL_FIXTURE_MISMATCH": (
        "docs/PLAINSIGHT-FOUNDATION.md section 4.3 and the ZMeta harness rule: one refusal fixture "
        "per required field, which withholds that field alone and asserts a refusal",
        "point the entry at a fixture of this connector and version whose result is refusal, whose "
        "input omits or nulls the named field, and which supplies every other required input as a "
        "placeholder; give each required input its own fixture; or correct input_field to a "
        "required input",
    ),
    "MANIFEST_REFUSAL_CODE_UNDECLARED": (
        "spec/layer-model.yaml violation_codes is the one code vocabulary (reading MF-R10)",
        "use a declared code; or declare a code in spec/layer-model.yaml and regenerate",
    ),
    "MANIFEST_TARGETING_NO_SELECTOR": (
        "docs/PLAINSIGHT-FOUNDATION.md D2 and doctrine/SUBJECT_SELECTION.md SS-10 and SS-19: a "
        "connector names what it targets, and argv carries the selector the gate evaluated "
        "(reading MF-R16)",
        "declare at least one consumed selector by registry key and name its as in "
        "lineage.command_template, a required one where the connector has any; or declare kind "
        "reference if the connector executes nothing",
    ),
    "MANIFEST_COMMAND_TEMPLATE_SLOT": (
        "doctrine/SUBJECT_SELECTION.md SS-19 and doctrine/CREDENTIAL_LIFECYCLE.md CR-3: argv is built "
        "only from declared inputs and a credential reference",
        "name a consumes as name, a params key, or credential_ref in each slot; a credential_ref slot "
        "needs an auth block",
    ),
    "MANIFEST_EXPOSURE_UNDERSTATED": (
        "doctrine/SUBJECT_SELECTION.md SS-13: an authenticated read is attributable to the account "
        "that made it",
        "set exposure.level to logged; or remove auth if the connector does not authenticate",
    ),
    "MANIFEST_AUTH_NOT_A_REFERENCE": (
        "docs/PLAINSIGHT-design.md section 6.3 and doctrine/CREDENTIAL_LIFECYCLE.md CR-3: auth is a "
        "credential_pool reference and nothing else",
        "keep auth to credential_pool alone; acquisition lives in the credential admin tool; keep any "
        "credential value out of the file and out of every commit",
    ),
    "MANIFEST_ID_DISAGREES_WITH_DIRECTORY": (
        "docs/THE-GAMEPLAN.md section 1.2: connectors/<id>/manifest.yaml",
        "rename the directory or the id so they match",
    ),
    "MANIFEST_ABSENT": (
        "docs/THE-GAMEPLAN.md section 1.2: every connector directory carries manifest.yaml",
        "write connectors/<id>/manifest.yaml; or remove the directory",
    ),
    "MANIFEST_SCHEMA_DRIFT": (
        "the manifest and fixture schemas copy enums from spec/layer-model.yaml, policy/retention.yaml, "
        "ontology/selectors.yaml and tools/validate_cast.py, and a copy that disagrees is drift",
        "change the schema to match its source; or change the source and the schema together in one "
        "reviewed change",
    ),
}


class Finding:
    __slots__ = ("code", "where", "what")

    def __init__(self, code: str, where: str, what: str):
        if code not in CODES:
            raise KeyError(f"undeclared code {code}")
        self.code, self.where, self.what = code, where, what

    def key(self) -> tuple[str, str, str]:
        return (self.code, self.where, self.what)

    def render(self) -> str:
        rule, moves = CODES[self.code]
        return (
            f"REFUSED {self.code}\n"
            f"  where: {self.where}\n"
            f"  what:  {self.what}\n"
            f"  rule:  {rule}\n"
            f"  moves: {moves}"
        )


# ---------------------------------------------------------------------------
# inputs
# ---------------------------------------------------------------------------


def rel_of(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def at(rel: str, dotted: str) -> str:
    return f"{rel} :: {dotted}" if dotted else rel


def _read_json(path: Path, what: str) -> dict:
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ToolFailure(rel_of(path), f"{what} does not exist, so the gate has nothing to grade against",
                          "restore the file from git")
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ToolFailure(rel_of(path), f"{what} could not be read as JSON ({exc.__class__.__name__})",
                          "fix the syntax, or restore the file from git")
    try:
        Draft202012Validator.check_schema(doc)
    except SchemaError as exc:
        raise ToolFailure(rel_of(path), f"{what} is not a valid draft 2020-12 schema: {exc.message}",
                          "fix the schema against the draft 2020-12 metaschema")
    return doc


def _read_yaml(path: Path, what: str) -> dict:
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ToolFailure(rel_of(path), f"{what} does not exist", "restore the file from git")
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise ToolFailure(rel_of(path), f"{what} could not be parsed ({exc.__class__.__name__})",
                          "fix the syntax, or restore the file from git")
    if not isinstance(doc, dict):
        raise ToolFailure(rel_of(path), f"{what} did not parse to a mapping", "restore the file from git")
    return doc


def _cast_tokens(doc) -> frozenset[str]:
    """Every typed token the cast draft carries as a value, read as YAML so a
    comment cannot add one."""
    found: set[str] = set()

    def walk(node):
        if isinstance(node, dict):
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
        elif isinstance(node, str) and TYPED_TOKEN_RE.fullmatch(node):
            found.add(node)

    walk(doc)
    return frozenset(found)


def placeholder_ok(value, ctx: dict) -> bool:
    """MF-R8: a slot name or a typed token the cast carries, and nothing else."""
    return isinstance(value, str) and (SLOT_PLACEHOLDER_RE.fullmatch(value) is not None
                                       or value in ctx["cast_tokens"])


def duplicate_keys(text: str) -> list[str]:
    """Dotted paths of every mapping key the YAML text repeats. Raises
    yaml.YAMLError as safe_load would."""
    out: list[str] = []

    def label(node) -> str:
        v = getattr(node, "value", None)
        return v if isinstance(v, str) and SAFE_KEY_RE.match(v) else "a key"

    def walk(node, path: str) -> None:
        if isinstance(node, yaml.MappingNode):
            seen: set = set()
            for k, v in node.value:
                key = (k.tag, k.value) if isinstance(k, yaml.ScalarNode) else None
                here = f"{path}.{label(k)}" if path else label(k)
                if key is not None and key in seen:
                    out.append(here)
                if key is not None:
                    seen.add(key)
                walk(v, here)
        elif isinstance(node, yaml.SequenceNode):
            for i, v in enumerate(node.value):
                walk(v, f"{path}.{i}" if path else str(i))

    root = yaml.compose(text, Loader=yaml.SafeLoader)
    if root is not None:
        walk(root, "")
    return out


def load_context(pin_text: str | None = None) -> dict:
    """Everything a check reads, read once. Raises ToolFailure for exit 2."""
    ctx: dict = {
        "schema": _read_json(SCHEMA, "the manifest schema"),
        "fixture_schema": _read_json(FIXTURE_SCHEMA, "the harness fixture schema"),
    }
    try:
        ctx["registry"], _ = validate_ontology.load()
    except (OSError, yaml.YAMLError, ValueError) as exc:
        raise ToolFailure(REGISTRY_REL, f"the selector registry could not be read ({exc.__class__.__name__})",
                          "fix ontology/selectors.yaml, or run python tools/validate_ontology.py first")
    try:
        ctx["codes"] = validate_ontology.declared_codes()
    except (OSError, yaml.YAMLError, ValueError) as exc:
        raise ToolFailure("spec/layer-model.yaml", f"the violation-code vocabulary could not be read "
                          f"({exc.__class__.__name__})", "fix spec/layer-model.yaml")
    ctx["layer_model"] = _read_yaml(LAYER_MODEL, "the layer model")
    ctx["retention"] = _read_yaml(RETENTION_POLICY, "the retention policy")
    ctx["cast_tokens"] = _cast_tokens(_read_yaml(validate_cast.CAST, "the cast draft"))
    try:
        text = pin_text if pin_text is not None else pin_of_record.PIN.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ToolFailure("doctrine/DOCTRINE_STATUS.md", f"the pin of record could not be read "
                          f"({exc.__class__.__name__}), so no stamp can be told from its absence",
                          "restore the file from git")
    ctx["pin_text"] = text
    ctx["pin"] = pin_of_record.Pin(text, ROOT)
    if not ctx["pin"].parsed:
        raise ToolFailure("doctrine/DOCTRINE_STATUS.md", "the pin of record could not be parsed into its "
                          "three tables, so no stamp can be read", "restore the file from git")
    return ctx


# ---------------------------------------------------------------------------
# drift: the schemas' copied enums against their sources
# ---------------------------------------------------------------------------


def _dig(node, *keys):
    for k in keys:
        if not isinstance(node, dict):
            return None
        node = node.get(k)
    return node


def drift_findings(ctx: dict) -> list[Finding]:
    s, fx, lm = ctx["schema"], ctx["fixture_schema"], ctx["layer_model"]
    et = lm.get("event_types") or {}
    rows = _dig(ctx["retention"], "retention", "strata", "rows") or []
    parts = _dig(ctx["retention"], "retention", "repo_scan", "enforcement_parts_all_required") or []
    canary_part = next((p for p in parts if isinstance(p, dict)
                        and str(p.get("clause", "")).startswith("canary_subject_class")), {})
    defs = s.get("$defs") or {}
    pairs = [
        ("kind", _dig(s, "properties", "kind", "enum"),
         _dig(et, "PROBE_EVENT", "payload", "fields", "connector_kind", "enum"),
         "spec/layer-model.yaml PROBE_EVENT connector_kind"),
        ("health.probe_unit", _dig(s, "properties", "health", "properties", "probe_unit", "enum"),
         _dig(et, "SYSTEM_EVENT", "payload", "fields", "probe_unit", "enum"),
         "spec/layer-model.yaml SYSTEM_EVENT probe_unit"),
        ("emit.inference_hint.proposes",
         _dig(defs, "emit", "properties", "inference_hint", "properties", "proposes", "enum"),
         [str(k).lower() for k in (_dig(et, "LINK_EVENT", "subtypes") or {})],
         "spec/layer-model.yaml LINK_EVENT subtypes, lower-cased"),
        ("bystander_class.disposition", _dig(defs, "bystander_class", "properties", "disposition", "enum"),
         _dig(et, "COLLECT_EVENT", "payload", "fields", "bystander_disposition", "enum"),
         "spec/layer-model.yaml COLLECT_EVENT bystander_disposition"),
        ("emit.fp_mode_basis", _dig(defs, "emit", "properties", "fp_mode_basis", "enum"),
         list((ctx["registry"].get("fp_mode_bases") or {}).keys()),
         "ontology/selectors.yaml fp_mode_bases"),
        ("canary_subject_class", _dig(s, "properties", "canary_subject_class", "enum"),
         canary_part.get("values"), "policy/retention.yaml RT-15 canary_subject_class values"),
        ("fixture canary_subject_class", _dig(fx, "properties", "canary_subject_class", "enum"),
         _dig(s, "properties", "canary_subject_class", "enum"), "the manifest schema's canary_subject_class"),
        ("fixture adapter_state", _dig(fx, "properties", "adapter_state", "enum"),
         _dig(et, "PROBE_EVENT", "payload", "fields", "error_class", "enum"),
         "spec/layer-model.yaml PROBE_EVENT error_class"),
        ("placeholder_input pattern", [_dig(defs, "placeholder_input", "additionalProperties", "pattern")],
         [validate_cast.PLACEHOLDER_RE.pattern], "tools/validate_cast.py PLACEHOLDER_RE"),
        ("fixture input pattern",
         [(_dig(fx, "properties", "input", "additionalProperties", "anyOf") or [{}])[0].get("pattern")],
         [validate_cast.PLACEHOLDER_RE.pattern], "tools/validate_cast.py PLACEHOLDER_RE"),
    ]
    out: list[Finding] = []
    for name, ours, theirs, source in pairs:
        if not ours or not theirs or sorted(map(str, ours)) != sorted(map(str, theirs)):
            out.append(Finding("MANIFEST_SCHEMA_DRIFT", f"schema :: {name.replace(' ', '_')}",
                               f"the schema's {name} is {ours} and its source, {source}, is {theirs}"))
    stratum = _dig(s, "properties", "lineage", "properties", "retention_stratum", "const")
    zero = [r.get("name") for r in rows if isinstance(r, dict) and r.get("stratum") == 0]
    if stratum not in zero:
        out.append(Finding("MANIFEST_SCHEMA_DRIFT", "schema :: lineage.retention_stratum",
                           f"the schema names the stratum row {stratum!r}, and the stratum-0 rows "
                           f"policy/retention.yaml declares are {zero}"))
    return out


# ---------------------------------------------------------------------------
# shape: the schema gate, each error under the narrowest code that names it
# ---------------------------------------------------------------------------


def _lineage_has_duration(lineage) -> bool:
    if not isinstance(lineage, dict):
        return False

    def walk(node, key=""):
        if isinstance(node, dict):
            for k, v in node.items():
                if str(k).lower() in DURATION_KEYS or walk(v, str(k)):
                    return True
        elif isinstance(node, list):
            return any(walk(v, key) for v in node)
        elif isinstance(node, str) and key != "command_template":
            return bool(DURATION_VALUE_RE.match(node))
        return False

    return walk(lineage)


def _missing(err) -> str:
    m = MISSING_RE.match(err.message) if err.validator == "required" else None
    return m.group(1) if m else ""


def classify(err, manifest) -> str:
    path = [str(p) for p in err.absolute_path]
    head = path[0] if path else ""
    schema_path = [str(p) for p in err.absolute_schema_path]
    missing = _missing(err)
    if missing:
        if missing == "bystanders" or (head == "bystanders" and missing in ("classes", "reach")):
            return "MANIFEST_BYSTANDER_UNDECLARED"
        if missing == "interaction_class":
            return "MANIFEST_INTERACTION_CLASS_INVALID"
        if missing == "canary_subject_class" and not path:
            return "MANIFEST_CANARY_SUBJECT_CLASS"
        if missing in ("health", "canaries", "known_positive", "known_negative"):
            return "MANIFEST_CANARY_MISSING"
        if missing in ("continuous", "routing", "executable", "methods", "coverage_proof"):
            return "MANIFEST_KIND_DISAGREES"
        if head == "health" and "known_negative" in path:
            return "MANIFEST_CANARY_NEGATIVE_UNSOUND"
    if err.validator is None and schema_path[:1] == ["allOf"]:
        return "MANIFEST_KIND_DISAGREES"
    if head == "kind":
        return "MANIFEST_KIND_UNKNOWN"
    if head == "emits" and len(path) >= 3 and path[2] == "layer":
        return "MANIFEST_EMIT_LAYER"
    if head == "bystanders":
        if path[-1] == "disposition":
            return "BYSTANDER_DISPOSITION_OUT_OF_SET"
        if path[-1] == "class":
            return "MANIFEST_BYSTANDER_CLASS_UNKNOWN"
        if path in (["bystanders"], ["bystanders", "reach"], ["bystanders", "classes"]):
            return "MANIFEST_BYSTANDER_UNDECLARED"
    if head == "canary_subject_class":
        return "MANIFEST_CANARY_SUBJECT_CLASS"
    if head == "health" and "known_negative" in path and "expect" in path:
        return "MANIFEST_CANARY_NEGATIVE_UNSOUND"
    if head == "health" and "canaries" in path and "input" in path:
        return "MANIFEST_CANARY_INPUT_VALUE"
    if head == "render":
        return "MANIFEST_RENDER_MARKUP"
    if head == "lineage" and isinstance(manifest, dict) and _lineage_has_duration(manifest.get("lineage")):
        return "MANIFEST_LINEAGE_DURATION"
    if head == "interaction_class":
        value = manifest.get("interaction_class") if isinstance(manifest, dict) else None
        return "MANIFEST_INTERACTION_EXCLUDED" if value == "induces_disclosure" else "MANIFEST_INTERACTION_CLASS_INVALID"
    if head == "auth":
        return "MANIFEST_AUTH_NOT_A_REFERENCE"
    if head == "params" and path[-1:] == ["default"]:
        return "MANIFEST_PARAM_DEFAULT_INVALID"
    return "MANIFEST_SHAPE_INVALID"


def _schema_at(root, schema_path) -> object:
    """The subschema an error's schema path names. jsonschema leaves $ref and if
    out of the path, so a missing key is retried through the node's $ref."""
    node = root
    for p in schema_path:
        if isinstance(node, dict) and p not in node and isinstance(node.get("$ref"), str):
            target = root
            for part in node["$ref"].lstrip("#/").split("/"):
                target = target[part]
            node = target
        if isinstance(node, dict):
            node = node[p]
        elif isinstance(node, list):
            node = node[int(p)]
        else:
            raise KeyError(p)
    return node


def _instance_at(doc, path):
    node = doc
    for p in path:
        node = node[p]
    return node


def _false_keys(err, root, doc) -> list[str]:
    """The keys a boolean-false subschema refused. jsonschema reports such an
    error at the parent object, so the keys are read from the schema's false
    properties that the parent instance carries."""
    try:
        props = _schema_at(root, list(err.absolute_schema_path))
        parent = _instance_at(doc, list(err.absolute_path))
    except (KeyError, IndexError, TypeError, ValueError):
        return []
    if not isinstance(props, dict) or not isinstance(parent, dict):
        return []
    return sorted(k for k, v in props.items() if v is False and k in parent and SAFE_KEY_RE.match(k))


def _false_reason(err, doc, subject: str, keys: list[str]) -> str:
    sp = [str(p) for p in err.absolute_schema_path]
    if "dependentSchemas" in sp:
        branch = sp[sp.index("dependentSchemas") + 1]
        return f"which {'an' if branch[:1] in 'aeiou' else 'a'} {branch} emit may not carry"
    if sp[:2] == ["properties", "params"]:
        if keys == ["values"]:
            return "which only an enum parameter carries"
        return ("which a selector_ref, geo_area, time_window or secret_ref parameter may not carry, "
                "because its default would be a value in a tracked file")
    if "bystanders" in sp and "else" in sp:
        return "which reach named_selector_only forbids"
    if sp[:1] == ["allOf"] and isinstance(doc, dict):
        if subject == "fixture":
            return f"which a fixture whose result is {doc.get('result')} may not carry"
        kind = doc.get("kind")
        return f"which kind {kind} forbids" if isinstance(kind, str) and SAFE_KEY_RE.match(kind) \
            else "which this kind forbids"
    return "which this position does not permit"


def describe(err, root=None, doc=None, subject: str = "manifest") -> str:
    """What the schema refused, without echoing the refused value (RT-19, HY-1)."""
    v, vv = err.validator, err.validator_value
    if v == "required":
        return f"the required key {_missing(err) or 'named by the schema'} is absent"
    if v == "enum":
        return f"a value outside the closed set {vv}"
    if v == "const":
        return f"a value other than the constant {vv!r}"
    if v == "pattern":
        if vv == "^[^<>]*$":
            return "a string carrying < or >, which is markup"
        if vv == validate_cast.PLACEHOLDER_RE.pattern:
            return "a value that is not a <...> placeholder"
        return f"a string that does not match {vv}"
    if v == "additionalProperties":
        known = set((err.schema or {}).get("properties") or {})
        extra = [k for k in (err.instance or {}) if k not in known] if isinstance(err.instance, dict) else []
        named = [k for k in extra if isinstance(k, str) and SAFE_KEY_RE.match(k)]
        shown = ", ".join(named) if named and len(named) == len(extra) else "a key"
        return f"a key the schema does not define here ({shown})"
    if v is None:
        keys = _false_keys(err, root, doc) if root is not None else []
        if not keys:
            return "a key this position does not permit"
        noun = "the key" if len(keys) == 1 else "the keys"
        return f"{noun} {', '.join(keys)}, {_false_reason(err, doc, subject, keys)}"
    if v == "type":
        return f"a value of the wrong type, where {vv} is required"
    if v == "minItems":
        return f"fewer than {vv} item(s)"
    if v == "oneOf":
        return "an entry that is neither one selector emit nor one entity emit"
    if v == "dependentRequired":
        return f"a key that needs {vv} beside it"
    if v == "uniqueItems":
        return "a repeated item"
    if v in ("minimum", "minLength", "minProperties"):
        return f"a value below the {v} of {vv}"
    if v == "propertyNames":
        return "an input name outside the pattern ^[a-z][a-z0-9_]*$"
    return f"a value the schema refuses under {v}"


def shape_findings(manifest, schema: dict, rel: str) -> list[Finding]:
    out: dict[tuple, Finding] = {}
    for err in Draft202012Validator(schema).iter_errors(manifest):
        dotted = ".".join(str(p) for p in err.absolute_path) or "manifest"
        f = Finding(classify(err, manifest), at(rel, dotted), f"{dotted}: {describe(err, schema, manifest)}")
        out.setdefault(f.key(), f)
    if isinstance(manifest, dict) and _lineage_has_duration(manifest.get("lineage")):
        f = Finding("MANIFEST_LINEAGE_DURATION", at(rel, "lineage"),
                    "lineage carries a retention duration or a key that holds one")
        out.setdefault(f.key(), f)
    return list(out.values())


# ---------------------------------------------------------------------------
# the checks a schema cannot express. Each runs only on a shape-clean manifest.
# ---------------------------------------------------------------------------


def _consumed(m: dict) -> list[tuple[str, dict]]:
    c = m.get("consumes") or {}
    return [(f"consumes.{lst}.{i}", e) for lst in ("required", "optional")
            for i, e in enumerate(c.get(lst) or [])]


def _as_names(m: dict, required_only: bool = False) -> set[str]:
    return {e["as"] for path, e in _consumed(m) if not required_only or ".required." in path}


def platform_bound(registry: dict, key: str) -> bool:
    """Whether the key's registry form binds a platform, as handle:<platform>/<string> does."""
    form = ((registry.get("selectors") or {}).get(key) or {}).get("form")
    return isinstance(form, str) and form.startswith(f"{key}:<platform>/")


def check_registry(m: dict, ctx: dict, rel: str) -> list[Finding]:
    reg = ctx["registry"]
    selectors = reg.get("selectors") or {}
    proposed = set(validate_ontology._as_list((reg.get("ontology") or {}).get("proposed")))
    stamped = ctx["pin"].artifact_stamped(REGISTRY_REL)
    out: list[Finding] = []

    def unregistered(where: str, key: str, role: str) -> None:
        out.append(Finding("MANIFEST_SELECTOR_UNREGISTERED", at(rel, where),
                           f"{role} the selector key {key}, which is not a key in {REGISTRY_REL}"))

    unit = (m.get("health") or {}).get("probe_unit")

    def platform_check(where: str, ref: dict, role: str) -> None:
        key = ref["selector"]
        if key not in selectors:
            return
        form = (selectors.get(key) or {}).get("form")
        bound = platform_bound(reg, key)
        named, from_item = "platform" in ref, ref.get("platform_from_item") is True
        if bound and not named and not from_item:
            out.append(Finding("MANIFEST_SELECTOR_PLATFORM", at(rel, where),
                               f"MISSING: {role} {key} with no platform and no platform_from_item, and its "
                               f"registry form {form} binds one"))
        elif bound and named and from_item:
            out.append(Finding("MANIFEST_SELECTOR_PLATFORM", at(rel, f"{where}.platform_from_item"),
                               f"BOTH: {role} {key} with a platform and platform_from_item, so the claim's "
                               "platform is named twice and the two can disagree (MF-R17)"))
        elif not bound and (named or from_item):
            field = "platform" if named else "platform_from_item"
            out.append(Finding("MANIFEST_SELECTOR_PLATFORM", at(rel, f"{where}.{field}"),
                               f"UNBOUND KEY: {role} {key} with {field}, and its registry form {form} binds "
                               "no platform"))
        if from_item and unit != "endpoint":
            out.append(Finding("MANIFEST_SELECTOR_PLATFORM", at(rel, f"{where}.platform_from_item"),
                               f"PROBE UNIT NOT ENDPOINT: {role} {key} with platform_from_item on a manifest "
                               f"whose health.probe_unit is {unit if unit is not None else 'absent'}, so an "
                               "item is not one endpoint and its locator names no one platform (MF-R17)"))

    for path, e in _consumed(m):
        if e["selector"] not in selectors:
            unregistered(f"{path}.selector", e["selector"], "consumes")
        platform_check(path, e, "consumes")
    for i, meth in enumerate(m.get("methods") or []):
        for j, ref in enumerate(meth.get("applies_to") or []):
            if ref["selector"] not in selectors:
                unregistered(f"methods.{i}.applies_to.{j}", ref["selector"], "a method applies to")
            platform_check(f"methods.{i}.applies_to.{j}", ref, "a method applies to")
    for i, e in enumerate(m.get("emits") or []):
        if "selector" in e:
            platform_check(f"emits.{i}", e, "emits")
        for j, field in enumerate(e.get("fields") or []):
            if field["name"] in selectors:
                out.append(Finding("MANIFEST_ENTITY_FIELD_IS_SELECTOR", at(rel, f"emits.{i}.fields.{j}.name"),
                                   f"an entity field is named {field['name']}, which is a key in "
                                   f"{REGISTRY_REL}, so the datum would be emitted outside the registry's "
                                   "stamp and semantics"))
    emitted = [(f"emits.{i}.selector", e["selector"]) for i, e in enumerate(m.get("emits") or []) if "selector" in e]
    emitted += [(f"methods.{i}.output_selectors.{j}", k) for i, meth in enumerate(m.get("methods") or [])
                for j, k in enumerate(meth.get("output_selectors") or [])]
    for where, key in emitted:
        if key not in selectors:
            unregistered(where, key, "emits")
        elif key in proposed and not stamped:
            out.append(Finding("MANIFEST_SELECTOR_UNSTAMPED", at(rel, where),
                               f"emits {key}, which {REGISTRY_REL} lists as proposed, and the pin of record "
                               "carries no whole-artifact row for the registry. A proposed key may be "
                               "consumed and may not be emitted until it is stamped (MF-R6)"))
    entities = reg.get("entities") or {}
    for i, e in enumerate(m.get("emits") or []):
        if "entity" in e and e["entity"] not in entities:
            out.append(Finding("MANIFEST_ENTITY_UNKNOWN", at(rel, f"emits.{i}.entity"),
                               f"emits an entity type outside the registry's closed set {sorted(entities)}"))
        if "selector" not in e or e["selector"] not in selectors:
            continue
        entry = selectors[e["selector"]] or {}
        for key in ("constraint_semantics", "generation_method", "requires_validation_by"):
            if key not in e:
                continue
            ours, theirs = e[key], entry.get(key)
            same = sorted(ours) == sorted(theirs or []) if isinstance(ours, list) else ours == theirs
            if not same:
                out.append(Finding("MANIFEST_EMIT_DISAGREES_WITH_REGISTRY", at(rel, f"emits.{i}.{key}"),
                                   f"declares {key} {ours!r} for {e['selector']}, and the registry "
                                   f"declares {theirs!r}"))
    return out


def check_params(m: dict, rel: str) -> list[Finding]:
    out: list[Finding] = []
    for i, p in enumerate(m.get("params") or []):
        if p["type"] == "enum" and "default" in p and p["default"] not in (p.get("values") or []):
            out.append(Finding("MANIFEST_PARAM_DEFAULT_INVALID", at(rel, f"params.{i}.default"),
                               f"the enum parameter {p['key']} has a default outside its values"))
    return out


def check_canaries(m: dict, rel: str, mdir: Path, ctx: dict) -> list[Finding]:
    health = m.get("health")
    if not isinstance(health, dict):
        return []
    out: list[Finding] = []
    for which in ("known_positive", "known_negative"):
        for name, value in health["canaries"][which]["input"].items():
            if not placeholder_ok(value, ctx):
                out.append(Finding("MANIFEST_CANARY_INPUT_VALUE", at(rel, f"health.canaries.{which}.input.{name}"),
                                   "the input is neither a slot name in angle brackets nor a typed token "
                                   "synthetic/GROUND_TRUTH.yaml carries, so it may be a value (MF-R8)"))
    negatives = set(m.get("distinguishable_negatives") or [])
    neg = health["canaries"]["known_negative"]["expect"]["negative_class"]
    if neg not in negatives:
        out.append(Finding("MANIFEST_CANARY_NEGATIVE_UNSOUND",
                           at(rel, "health.canaries.known_negative.expect.negative_class"),
                           f"names the negative class {neg}, which distinguishable_negatives does not "
                           f"declare ({sorted(negatives)}), so the canary asserts a class the source "
                           "cannot tell apart"))
    names, required = _as_names(m), _as_names(m, required_only=True)
    for which in ("known_positive", "known_negative"):
        keys = set(health["canaries"][which]["input"])
        stray, absent = sorted(keys - names), sorted(required - keys)
        if stray or absent:
            out.append(Finding("MANIFEST_CANARY_INPUT_MISMATCH", at(rel, f"health.canaries.{which}.input"),
                               f"the canary input keys {stray} name no consumed input, and the required "
                               f"inputs {absent} are absent"))
    golden = mdir / health["golden_fixture"]
    if not golden.is_file():
        out.append(Finding("MANIFEST_GOLDEN_FIXTURE_ABSENT", at(rel, "health.golden_fixture"),
                           f"no file exists at {health['golden_fixture']} beside the manifest, so nothing "
                           "replays in CI"))
    return out


def _fixture_lines(path: Path, rel: str, ctx: dict, cache: dict) -> tuple[dict | None, list[Finding]]:
    """Every line of a fixtures file, linted. (by-id map or None if absent, findings)."""
    if path in cache:
        return cache[path], []
    if not path.is_file():
        cache[path] = None
        return None, []
    out: list[Finding] = []
    by_id: dict[str, dict] = {}
    validator = Draft202012Validator(ctx["fixture_schema"])
    frel = rel_of(path)
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        cache[path] = {}
        return {}, [Finding("MANIFEST_REFUSAL_FIXTURE_SHAPE", frel,
                            f"the fixtures file could not be read ({exc.__class__.__name__})")]
    for n, line in enumerate(lines, 1):
        if not line.strip():
            continue
        repeated: list[str] = []

        def pairs_hook(pairs, repeated=repeated):
            seen: set = set()
            for k, _ in pairs:
                if k in seen:
                    repeated.append(k if isinstance(k, str) and SAFE_KEY_RE.match(k) else "a key")
                seen.add(k)
            return dict(pairs)

        try:
            fx = json.loads(line, object_pairs_hook=pairs_hook)
        except json.JSONDecodeError:
            out.append(Finding("MANIFEST_REFUSAL_FIXTURE_SHAPE", f"{frel}:{n}", "the line is not one JSON object"))
            continue
        if repeated:
            out.append(Finding("MANIFEST_REFUSAL_FIXTURE_SHAPE", f"{frel}:{n}",
                               f"the line repeats the key(s) {', '.join(sorted(set(repeated)))} in one object, "
                               "and JSON keeps only the last, so the first value is never linted"))
            continue
        errs = list(validator.iter_errors(fx))
        for err in errs:
            dotted = ".".join(str(p) for p in err.absolute_path) or "fixture"
            out.append(Finding("MANIFEST_REFUSAL_FIXTURE_SHAPE", f"{frel}:{n}",
                               f"{dotted}: {describe(err, ctx['fixture_schema'], fx, 'fixture')}"))
        if errs:
            continue
        loose = sorted(k for k, v in fx["input"].items() if v is not None and not placeholder_ok(v, ctx))
        if loose:
            out.append(Finding("MANIFEST_REFUSAL_FIXTURE_SHAPE", f"{frel}:{n}",
                               f"input.{', input.'.join(loose)}: neither a slot name in angle brackets nor a "
                               "typed token synthetic/GROUND_TRUTH.yaml carries, so it may be a value (MF-R8)"))
            continue
        if fx["id"] in by_id:
            out.append(Finding("MANIFEST_REFUSAL_FIXTURE_SHAPE", f"{frel}:{n}",
                               f"the fixture id {fx['id']} appears twice in the file"))
            continue
        by_id[fx["id"]] = fx
    cache[path] = by_id
    return by_id, out


def check_refusal_fixtures(m: dict, ctx: dict, rel: str, mdir: Path) -> list[Finding]:
    health = m.get("health")
    if not isinstance(health, dict):
        return []
    out: list[Finding] = []
    required = [e["as"] for e in (m.get("consumes") or {}).get("required") or []]
    entries = health.get("refusal_fixtures") or []
    named = [e["input_field"] for e in entries]
    for field in required:
        if field not in named:
            out.append(Finding("MANIFEST_REFUSAL_FIXTURE_MISSING", at(rel, "health.refusal_fixtures"),
                               f"the required input {field} has no refusal fixture"))
    cache: dict = {}
    seen_files: set[Path] = set()
    named_by: dict[tuple, str] = {}
    for i, e in enumerate(entries):
        where = at(rel, f"health.refusal_fixtures.{i}")
        if e["input_field"] not in required:
            out.append(Finding("MANIFEST_REFUSAL_FIXTURE_MISMATCH", where,
                               f"names {e['input_field']}, which is not a required input"))
        path = mdir / e["fixtures"]
        ident = (path.resolve(), e["id"])
        if ident in named_by:
            out.append(Finding("MANIFEST_REFUSAL_FIXTURE_MISMATCH", where,
                               f"the fixture {e['id']} is already the refusal fixture for {named_by[ident]}, so "
                               f"one fixture would stand as the proof for {named_by[ident]} and "
                               f"{e['input_field']}"))
        else:
            named_by[ident] = e["input_field"]
        by_id, lint = _fixture_lines(path, rel, ctx, cache)
        if path not in seen_files:
            seen_files.add(path)
            out.extend(lint)
        if by_id is None:
            out.append(Finding("MANIFEST_REFUSAL_FIXTURE_ABSENT", where,
                               f"no fixtures file exists at {e['fixtures']} beside the manifest"))
            continue
        fx = by_id.get(e["id"])
        if fx is None:
            out.append(Finding("MANIFEST_REFUSAL_FIXTURE_ABSENT", where,
                               f"{e['fixtures']} carries no shape-clean fixture with the id {e['id']}"))
            continue
        problems = []
        if fx["connector"] != {"id": m["id"], "version": m["version"]}:
            problems.append("it belongs to another connector or version")
        if fx["result"] != "refusal":
            problems.append("its result is not refusal")
        if fx["input"].get(e["input_field"]) is not None:
            problems.append(f"it supplies {e['input_field']}, the input it claims to refuse on")
        for other in required:
            if other != e["input_field"] and fx["input"].get(other) is None:
                problems.append(f"it also withholds {other}, so the refusal cannot be attributed to "
                                f"{e['input_field']}")
        if problems:
            out.append(Finding("MANIFEST_REFUSAL_FIXTURE_MISMATCH", where,
                               f"the fixture {e['id']} cannot prove the refusal: " + "; ".join(problems)))
        if fx["result"] == "refusal" and fx.get("refusal_code") not in ctx["codes"]:
            out.append(Finding("MANIFEST_REFUSAL_CODE_UNDECLARED", where,
                               f"the fixture {e['id']} refuses under a code spec/layer-model.yaml does not declare"))
    return out


def check_targeting(m: dict, rel: str) -> list[Finding]:
    out: list[Finding] = []
    consumed = [e["selector"] for _, e in _consumed(m)]
    if not consumed:
        out.append(Finding("MANIFEST_TARGETING_NO_SELECTOR", at(rel, "consumes"),
                           "consumes names no selector, so nothing says what this connector targets"))
    kind = m["kind"]
    emits = m.get("emits") or []
    tasks = [i for i, e in enumerate(emits) if e.get("entity") == "ManualTask"]
    if kind == "reference" and len(tasks) != len(emits):
        out.append(Finding("MANIFEST_KIND_DISAGREES", at(rel, "emits"),
                           "a reference connector executes nothing and emits ManualTask entities only"))
    if kind != "reference" and tasks:
        out.append(Finding("MANIFEST_KIND_DISAGREES", at(rel, f"emits.{tasks[0]}"),
                           f"a {kind} connector emits a ManualTask, which only a reference connector emits"))
    for i, e in enumerate(emits):
        if "collector" in e and e.get("entity") != "ManualTask":
            out.append(Finding("MANIFEST_KIND_DISAGREES", at(rel, f"emits.{i}.collector"),
                               "collector human is declared on an emit that is not a ManualTask"))
    if kind == "geo" and "geo_area" not in consumed:
        out.append(Finding("MANIFEST_KIND_DISAGREES", at(rel, "consumes"),
                           "a geo connector consumes no geo_area"))
    unit = (m.get("health") or {}).get("probe_unit")
    if unit is not None and (kind == "continuous") != (unit == "subscription"):
        out.append(Finding("MANIFEST_KIND_DISAGREES", at(rel, "health.probe_unit"),
                           f"a {kind} connector declares probe_unit {unit}; health is per subscription on a "
                           "continuous connector and only there"))
    return out


def check_bystander_reach(m: dict, rel: str) -> list[Finding]:
    consumed = {e["selector"] for _, e in _consumed(m)}
    area_param = any(p["type"] == "geo_area" for p in m.get("params") or [])
    area = m["kind"] == "geo" or "geo_area" in consumed or area_param
    widening = m["kind"] in WIDENING_KINDS or area
    if widening and m["bystanders"]["reach"] == "named_selector_only":
        why = (f"kind {m['kind']}" if m["kind"] in WIDENING_KINDS
               else "a consumed geo_area" if "geo_area" in consumed else "a geo_area parameter")
        return [Finding("MANIFEST_BYSTANDER_UNDECLARED", at(rel, "bystanders.reach"),
                        f"declares named_selector_only on a connector that collects on a population by "
                        f"construction ({why}), so the people it reaches are undeclared")]
    declared = {c["class"] for c in m["bystanders"].get("classes") or []}
    if area and not declared & set(AREA_CLASSES):
        why = ("kind geo" if m["kind"] == "geo"
               else "a consumed geo_area" if "geo_area" in consumed else "a geo_area parameter")
        return [Finding("MANIFEST_BYSTANDER_CLASS_UNKNOWN", at(rel, "bystanders.classes"),
                        f"reaches the people inside an area ({why}), and declares no class for them; "
                        f"no such class is ratified, so the classes it declares, {sorted(declared)}, "
                        "describe other populations (MF-R2)")]
    return []


def check_slots(m: dict, rel: str) -> list[Finding]:
    out: list[Finding] = []
    names = _as_names(m) | {p["key"] for p in m.get("params") or []}
    lineage = m.get("lineage")
    if isinstance(lineage, dict):
        slots = set(SLOT_RE.findall(lineage["command_template"]))
        required, consumed = _as_names(m, required_only=True), _as_names(m)
        target = required or consumed
        if consumed and not slots & target:
            which = "required input" if required else "consumed input"
            out.append(Finding("MANIFEST_TARGETING_NO_SELECTOR", at(rel, "lineage.command_template"),
                               f"the command template names no {which} ({sorted(target)}), so argv carries no "
                               "selector the gate evaluated (MF-R16)"))
        for slot in SLOT_RE.findall(lineage["command_template"]):
            if slot == "credential_ref" and "auth" in m:
                continue
            if slot in names:
                continue
            why = ("credential_ref with no auth block" if slot == "credential_ref"
                   else "a slot that names no consumed input and no params key")
            out.append(Finding("MANIFEST_COMMAND_TEMPLATE_SLOT", at(rel, "lineage.command_template"), why))
    render = m["render"]
    for key in ("title_template", "timeline_lane"):
        for slot in SLOT_RE.findall(render.get(key) or ""):
            if slot not in names:
                out.append(Finding("MANIFEST_RENDER_SLOT_UNKNOWN", at(rel, f"render.{key}"),
                                   "a slot that names no consumed input and no params key"))
    fields = {e["selector"] for e in m.get("emits") or [] if "selector" in e}
    fields |= {f["name"] for e in m.get("emits") or [] for f in e.get("fields") or []}
    for i, col in enumerate(render.get("columns") or []):
        if col not in fields:
            out.append(Finding("MANIFEST_RENDER_SLOT_UNKNOWN", at(rel, f"render.columns.{i}"),
                               f"the column {col} is no emitted selector key and no entity field"))
    return out


def check_honesty(m: dict, rel: str) -> list[Finding]:
    out: list[Finding] = []
    if m["kind"] == "reference":
        return out
    authed = "auth" in m
    if authed and m["exposure"]["level"] == "none":
        out.append(Finding("MANIFEST_EXPOSURE_UNDERSTATED", at(rel, "exposure.level"),
                           "declares no exposure on a connector that authenticates from a credential pool"))
    ic = m["interaction_class"]
    if (ic == "passive_unauthenticated") == authed:
        out.append(Finding("MANIFEST_INTERACTION_DISAGREES", at(rel, "interaction_class"),
                           f"declares {ic} on a connector that {'does' if authed else 'does not'} "
                           "authenticate from a credential pool"))
    return out


def check_interaction(m: dict, ctx: dict, rel: str) -> list[Finding]:
    if ctx["pin"].decision_stamped(R7):
        return []
    return [Finding("MANIFEST_INTERACTION_UNRATIFIED", at(rel, "interaction_class"),
                    "UNRATIFIED, this manifest declares interaction_class against the R7 line, and the pin "
                    "of record carries no dated row for R7, so nothing this manifest declares may run")]


def check_manifest(manifest, ctx: dict, rel: str, mdir: Path, expect_id: str | None = None,
                   shape_only: bool = False) -> list[Finding]:
    findings = shape_findings(manifest, ctx["schema"], rel)
    if shape_only or findings:
        return findings
    m = manifest
    findings += check_params(m, rel)
    findings += check_registry(m, ctx, rel)
    findings += check_canaries(m, rel, mdir, ctx)
    findings += check_refusal_fixtures(m, ctx, rel, mdir)
    findings += check_targeting(m, rel)
    findings += check_bystander_reach(m, rel)
    findings += check_slots(m, rel)
    findings += check_honesty(m, rel)
    findings += check_interaction(m, ctx, rel)
    if expect_id is not None and m["id"] != expect_id:
        findings.append(Finding("MANIFEST_ID_DISAGREES_WITH_DIRECTORY", at(rel, "id"),
                                f"the id differs from its directory name, connectors/{expect_id}/"))
    return findings


# ---------------------------------------------------------------------------
# entry
# ---------------------------------------------------------------------------


def load_manifest(path: Path) -> tuple[object, list[Finding]]:
    """The parsed manifest and a finding for every key the YAML repeats. Raises
    ToolFailure when absent or not YAML."""
    rel = rel_of(path)
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise ToolFailure(rel, "no manifest exists at this path", "correct the path")
    except (OSError, UnicodeDecodeError) as exc:
        raise ToolFailure(rel, f"the manifest could not be read ({exc.__class__.__name__})",
                          "save the file as UTF-8 text")
    try:
        repeated = [Finding("MANIFEST_DUPLICATE_KEY", at(rel, p),
                            f"{p}: the key appears twice in one mapping, and only the last value is read")
                    for p in duplicate_keys(text)]
        return yaml.safe_load(text), repeated
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        line = f" near line {mark.line + 1}" if mark is not None else ""
        raise ToolFailure(rel, f"the manifest is not YAML{line}", "fix the syntax; a manifest is one YAML mapping")


def _expected_id(path: Path, connectors: Path) -> str | None:
    p = path.resolve()
    return p.parent.name if p.parent.parent == connectors.resolve() else None


def _telemetry(outcome: str, findings: list[Finding]) -> None:
    if not gate_log:
        return
    try:
        gate_log.record_run(GATE, outcome, count=len(findings))
        for f in findings:
            gate_log.record_finding(GATE, code=f.code, where=f.where)
    except Exception:
        pass


def _report(findings: list[Finding], label: str) -> int:
    for f in findings:
        print(f.render(), file=sys.stderr)
        print(file=sys.stderr)
    print(
        f"validate_manifest {label}: {len(findings)} refusal(s). A refused manifest registers nothing, "
        "and no connector it describes may run.",
        file=sys.stderr,
    )
    return 1


def run_all(ctx: dict, quiet: bool, connectors: Path) -> int:
    findings = drift_findings(ctx)
    dirs = sorted(p for p in connectors.iterdir() if p.is_dir()) if connectors.is_dir() else []
    checked = 0
    for d in dirs:
        if d.name.startswith((".", "_")):
            # Not a connector: the id pattern admits neither. One holding a
            # manifest file is refused, never passed over as if absent.
            held = [p for p in d.glob("manifest*") if p.is_file()]
            if held:
                findings.append(Finding("MANIFEST_DIRECTORY_HIDDEN", rel_of(d),
                                        f"a directory whose name starts with {d.name[0]} holds {len(held)} "
                                        "manifest file(s), and --all validates no directory so named"))
            continue
        path = d / "manifest.yaml"
        rel = rel_of(path)
        if not path.is_file():
            findings.append(Finding("MANIFEST_ABSENT", rel_of(d), "a connector directory carries no manifest.yaml"))
            continue
        manifest, repeated = load_manifest(path)
        findings += repeated
        findings += check_manifest(manifest, ctx, rel, d, expect_id=d.name)
        checked += 1
    _telemetry("refuse" if findings else "pass", findings)
    if findings:
        return _report(findings, "--all")
    if checked == 0:
        # MF-R3. Reached only when no manifest file exists under connectors/ at
        # all, since a hidden or absent one refuses above. Printed under --quiet
        # too: the state is not a failure and not a connector pass, and CLAUDE.md
        # section 4 renders a state as its consequence.
        print(
            "validate_manifest --all: no manifest exists under connectors/, so no manifest was validated "
            "and no connector is registered. The two schemas were checked against the draft 2020-12 "
            "metaschema and their copied enums reconciled against their sources."
        )
    elif not quiet:
        print(f"validate_manifest --all ok: {checked} manifest(s), every check passed")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Connector manifest gate.")
    ap.add_argument("path", nargs="?", help="One manifest to validate.")
    ap.add_argument("--all", action="store_true", help="Every connectors/*/manifest.yaml.")
    ap.add_argument("--shape", action="store_true", help="Schema gate only. Makes no conformance claim.")
    ap.add_argument("--self-test", action="store_true", help="Break a manifest in memory; assert each refusal.")
    ap.add_argument("--quiet", action="store_true",
                    help="Print only on refusal, except two states printed regardless: --all over zero "
                         "manifests says no manifest was validated, and --shape says no conformance "
                         "claim is made.")
    args = ap.parse_args(argv)

    modes = sum(bool(x) for x in (args.all, args.self_test, args.path))
    if modes != 1 or (args.shape and not args.path):
        ap.error("pass one of: a manifest path, --shape <path>, --all, or --self-test")

    if args.self_test:
        return self_test(quiet=args.quiet)

    try:
        if args.shape:
            schema = _read_json(SCHEMA, "the manifest schema")
            path = Path(args.path)
            manifest, repeated = load_manifest(path)
            findings = repeated + shape_findings(manifest, schema, rel_of(path))
            if findings:
                return _report(findings, "--shape")
            print(
                f"validate_manifest --shape: {rel_of(path)} has the shape schema/connector-manifest.schema.json "
                "requires. No conformance claim is made: registry agreement, canaries, refusal fixtures, "
                "targeting, bystander reach and the R7 line were not checked."
            )
            return 0
        ctx = load_context()
        if args.all:
            return run_all(ctx, args.quiet, CONNECTORS)
        path = Path(args.path)
        manifest, repeated = load_manifest(path)
        findings = drift_findings(ctx) + repeated
        findings += check_manifest(manifest, ctx, rel_of(path), path.resolve().parent,
                                   expect_id=_expected_id(path, CONNECTORS))
    except ToolFailure as fail:
        print(fail.render(), file=sys.stderr)
        return 2
    _telemetry("refuse" if findings else "pass", findings)
    if findings:
        return _report(findings, rel_of(path))
    if not args.quiet:
        print(f"validate_manifest ok: {rel_of(path)} passes every check, R7 stamped "
              f"{ctx['pin'].decision_stamped(R7)}")
    return 0


# ---------------------------------------------------------------------------
# --self-test. A manifest is built in memory with placeholders only, its
# fixtures are written to a scratch directory outside the repository, and each
# case breaks one thing and asserts the code it expects. The permits are as
# load-bearing as the refusals: a gate that refuses everything proves nothing.
# ---------------------------------------------------------------------------

SELFTEST_ID = "selftest_conn"
SELFTEST_VERSION = "0.1.0"


def _baseline() -> dict:
    return {
        "manifest_schema": "plainsight-connector-manifest-0.1",
        "id": SELFTEST_ID,
        "version": SELFTEST_VERSION,
        "capability": "selftest.account_profile",
        "kind": "one_shot",
        "cardinality": "one_to_one",
        "consumes": {
            "required": [{"selector": "handle", "platform": "synthplatform", "as": "username"}],
            "optional": [{"selector": "platform_uid", "platform": "synthplatform", "as": "user_id"}],
            "preconditions": [{"expr": "creds.selftest_sessions.available > 0",
                               "unmet_message": "No valid session in the credential pool"}],
        },
        "params": [{"key": "fetch_avatar", "type": "bool", "default": True,
                    "label": "Download the profile image, which enables the image hash pivot"}],
        "emits": [
            {"selector": "platform_uid", "platform": "synthplatform", "layer": "observation", "always_present": True},
            {"selector": "email_hint_recovery_masked", "layer": "observation", "always_present": True,
             "constraint_semantics": "prefix_suffix_mask",
             "fp_mode": "the platform returns the recovery hint for a linked account",
             "fp_mode_basis": "reported"},
            {"selector": "handle", "platform": "synthplatform", "layer": "observation",
             "inference_hint": {"proposes": "same_entity", "rationale_template": "handle string identical to {username}"}},
            {"entity": "Account", "layer": "observation",
             "fields": [{"name": "display_name", "always_present": True},
                        {"name": "follower_count", "volatile": True}]},
        ],
        "zero_means": "absence_evidence",
        "distinguishable_negatives": ["account_does_not_exist", "account_private"],
        "cost": {"class": "session", "units": "one authenticated request", "credits_per_call": 0},
        "exposure": {"level": "logged", "detail": "authenticated read, attributable to the session account"},
        "rate_limit": {"scope": "per_credential", "calls": 40, "per": "1h",
                       "on_429": {"backoff": "exponential", "cooldown": "15m", "quarantine_credential": True}},
        "auth": {"credential_pool": "selftest_sessions"},
        "health": {
            "probe_unit": "connector",
            "canaries": {
                "known_positive": {"input": {"username": "<cast_linked_handle>"},
                                   "expect": {"result_count_min": 1, "always_present_fields": "all"}},
                "known_negative": {"input": {"username": "<cast_negative_handle>"},
                                   "expect": {"result_count": 0, "negative_class": "account_does_not_exist"}},
            },
            "cadence": "round_robin",
            "golden_fixture": "fixtures/golden.json",
            "refusal_fixtures": [{"input_field": "username", "fixtures": "fixtures.jsonl", "id": "refuse-no-username"}],
        },
        "canary_subject_class": "synthetic",
        "lineage": {"command_template": "selftest-tool --credential {credential_ref} --user {username}",
                    "capture": ["stdout", "stderr", "exit_code", "duration_ms", "credential_id"],
                    "retention_stratum": "raw_capture"},
        "render": {"shape": "record", "title_template": "{username}",
                   "columns": ["display_name", "follower_count", "email_hint_recovery_masked"]},
        "interaction_class": "passive_authenticated_read",
        "bystanders": {"reach": "named_selector_only"},
    }


def _fixture(fid: str, **over) -> dict:
    fx = {"id": fid, "connector": {"id": SELFTEST_ID, "version": SELFTEST_VERSION}, "input": {},
          "result": "refusal", "adapter_state": "malformed", "refusal_code": "PAYLOAD_FIELD_MISSING",
          "canary_subject_class": "synthetic"}
    fx.update(over)
    return fx


def _baseline_fixtures() -> list[dict]:
    return [
        _fixture("refuse-no-username"),
        _fixture("refuse-null-username", input={"username": None}),
        _fixture("supplies-username", input={"username": "<cast_linked_handle>"}),
        _fixture("events-line", input={"username": "<cast_linked_handle>"}, result="events", event_count=1,
                 adapter_state="ok", cassette="cassettes/known_positive.yaml", refusal_code=None),
        _fixture("other-connector", connector={"id": "another_conn", "version": SELFTEST_VERSION}),
        _fixture("undeclared-code", refusal_code="NOT_A_DECLARED_CODE"),
        _fixture("refuse-no-username-uid2-given", input={"user_id2": "<cast_linked_uid>"}),
        _fixture("refuse-no-uid2", input={"username": "<cast_linked_handle>"}),
    ]


def _second_required(refusals: list[tuple[str, str]]):
    """A second required input, user_id2, keyed into both canaries, with the
    refusal_fixtures entries given as (input_field, fixture id)."""
    def mutate(m: dict) -> None:
        m["consumes"]["required"].append({"selector": "platform_uid", "platform": "synthplatform", "as": "user_id2"})
        for which in ("known_positive", "known_negative"):
            m["health"]["canaries"][which]["input"]["user_id2"] = "<cast_linked_uid>"
        m["health"]["refusal_fixtures"] = [{"input_field": f, "fixtures": "fixtures.jsonl", "id": i}
                                           for f, i in refusals]
    return mutate


def _write_case(base: Path, fixtures: list[dict], golden: bool = True) -> Path:
    mdir = base / "connectors" / SELFTEST_ID
    (mdir / "fixtures").mkdir(parents=True, exist_ok=True)
    lines = []
    for fx in fixtures:
        fx = {k: v for k, v in fx.items() if not (k == "refusal_code" and v is None)}
        lines.append(json.dumps(fx))
    (mdir / "fixtures.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    golden_path = mdir / "fixtures" / "golden.json"
    if golden:
        golden_path.write_text("{}\n", encoding="utf-8")
    elif golden_path.exists():
        golden_path.unlink()
    return mdir


def _set(path: str, value):
    def mutate(m: dict) -> None:
        keys = path.split(".")
        node = m
        for k in keys[:-1]:
            node = node[int(k)] if isinstance(node, list) else node[k]
        last = keys[-1]
        if isinstance(node, list):
            node[int(last)] = value
        else:
            node[last] = value
    return mutate


def _del(path: str):
    def mutate(m: dict) -> None:
        keys = path.split(".")
        node = m
        for k in keys[:-1]:
            node = node[int(k)] if isinstance(node, list) else node[k]
        del node[keys[-1]]
    return mutate


def _seq(*fns):
    def mutate(m: dict) -> None:
        for fn in fns:
            fn(m)
    return mutate


def _cases(pin_text: str, cast_tokens=frozenset()) -> list[tuple]:
    """(description, mutate manifest, mutate fixtures or None, pin text or None, golden, expected).

    expected is a code that must fire, or None for a case that must permit.
    """
    # Shapes a value could take inside brackets, built so this file carries none.
    at_sign = "<slot" + chr(64) + "shape>"
    area_param = {"key": "area", "type": "geo_area", "label": "Area"}
    with_area_param = _seq(lambda m: m["params"].append(dict(area_param)),
                           _set("lineage.command_template",
                                "selftest-tool --credential {credential_ref} --user {username} --area {area}"))
    geo_kind = _seq(_set("kind", "geo"),
                    lambda m: m["consumes"]["optional"].append({"selector": "geo_area", "as": "area"}))
    token_case = []
    if cast_tokens:
        token_case = [("a canary input naming a cast token permits",
                       _set("health.canaries.known_positive.input.username", min(cast_tokens)),
                       None, None, True, None)]
    no_r7 = re.sub(r"(?m)^\| R7 [^\n]*\n", "", pin_text, count=1)
    registry_stamped = pin_of_record._add(
        pin_text, pin_of_record._row("the selector registry, whole artifact", f"`{REGISTRY_REL}`"))
    declared_followers = {"reach": "declared", "classes": [
        {"class": "followers", "estimate": {"method": "platform_reported_count"}, "disposition": "count_only"}]}
    keep = None
    return [
        ("the baseline manifest permits under the real pin", lambda m: None, keep, None, True, None),
        ("a stamped-R7 pin permits", lambda m: None, keep, pin_text, True, None),
        ("an unstamped R7 pin refuses", lambda m: None, keep, no_r7, True, "MANIFEST_INTERACTION_UNRATIFIED"),
        ("an undeclared bystander block", _del("bystanders"), keep, None, True, "MANIFEST_BYSTANDER_UNDECLARED"),
        ("reach declared with no class", _set("bystanders", {"reach": "declared"}), keep, None, True,
         "MANIFEST_BYSTANDER_UNDECLARED"),
        ("an expansion claiming named_selector_only",
         _seq(_set("kind", "expansion"), _set("routing", "roster"), _set("cardinality", "one_to_many")),
         keep, None, True, "MANIFEST_BYSTANDER_UNDECLARED"),
        ("a disposition of retain",
         _set("bystanders", {"reach": "declared", "classes": [
             {"class": "followers", "estimate": {"method": "platform_reported_count"}, "disposition": "retain"}]}),
         keep, None, True, "BYSTANDER_DISPOSITION_OUT_OF_SET"),
        ("a bystander class outside the closed set",
         _set("bystanders", {"reach": "declared", "classes": [
             {"class": "co_appears_in_media", "estimate": {"method": "platform_reported_count"},
              "disposition": "refuse"}]}),
         keep, None, True, "MANIFEST_BYSTANDER_CLASS_UNKNOWN"),
        ("an unestimable class with no reason",
         _set("bystanders", {"reach": "declared", "classes": [
             {"class": "followers", "estimate": {"method": "unestimable"}, "disposition": "refuse"}]}),
         keep, None, True, "MANIFEST_SHAPE_INVALID"),
        ("a declared follower reach permits", _set("bystanders", declared_followers), keep, None, True, None),
        ("an emit at layer inference", _set("emits.0.layer", "inference"), keep, None, True, "MANIFEST_EMIT_LAYER"),
        ("an unregistered consumed selector", _set("consumes.required.0.selector", "not_a_registry_key"),
         keep, None, True, "MANIFEST_SELECTOR_UNREGISTERED"),
        ("an unregistered emitted selector", _set("emits.0.selector", "not_a_registry_key"), keep, None, True,
         "MANIFEST_SELECTOR_UNREGISTERED"),
        ("a proposed, unstamped key emitted", _set("emits.0", {"selector": "postal_address", "layer": "observation"}),
         keep, None, True, "MANIFEST_SELECTOR_UNSTAMPED"),
        ("a proposed key consumed permits",
         lambda m: m["consumes"]["optional"].append({"selector": "postal_address", "as": "address"}),
         keep, None, True, None),
        ("a proposed key emitted under a stamped registry permits",
         _set("emits.0", {"selector": "postal_address", "layer": "observation"}), keep, registry_stamped, True, None),
        ("an entity outside the registry", _set("emits.3.entity", "Dossier"), keep, None, True,
         "MANIFEST_ENTITY_UNKNOWN"),
        ("constraint semantics against the registry", _set("emits.1.constraint_semantics", "suffix_mask"),
         keep, None, True, "MANIFEST_EMIT_DISAGREES_WITH_REGISTRY"),
        ("no known_negative canary", _del("health.canaries.known_negative"), keep, None, True,
         "MANIFEST_CANARY_MISSING"),
        ("no health block on a one_shot", _del("health"), keep, None, True, "MANIFEST_CANARY_MISSING"),
        ("a known_negative expecting a result", _set("health.canaries.known_negative.expect.result_count", 1),
         keep, None, True, "MANIFEST_CANARY_NEGATIVE_UNSOUND"),
        ("a known_negative class the source does not declare",
         _set("health.canaries.known_negative.expect.negative_class", "account_suspended"), keep, None, True,
         "MANIFEST_CANARY_NEGATIVE_UNSOUND"),
        ("no canary_subject_class", _del("canary_subject_class"), keep, None, True, "MANIFEST_CANARY_SUBJECT_CLASS"),
        ("canary_subject_class consented", _set("canary_subject_class", "consented"), keep, None, True,
         "MANIFEST_CANARY_SUBJECT_CLASS"),
        ("a canary input that is not a placeholder",
         _set("health.canaries.known_positive.input.username", "not-a-placeholder"), keep, None, True,
         "MANIFEST_CANARY_INPUT_VALUE"),
        ("a canary input naming no consumed input",
         _set("health.canaries.known_positive.input", {"user_name": "<cast_linked_handle>"}), keep, None, True,
         "MANIFEST_CANARY_INPUT_MISMATCH"),
        ("no golden fixture on disk", lambda m: None, keep, None, False, "MANIFEST_GOLDEN_FIXTURE_ABSENT"),
        ("markup in render", _set("render.title_template", "<b>{username}</b>"), keep, None, True,
         "MANIFEST_RENDER_MARKUP"),
        ("a component key in render", _set("render.component", "CustomPanel"), keep, None, True,
         "MANIFEST_RENDER_MARKUP"),
        ("a render column nothing emits", _set("render.columns", ["display_name", "phone"]), keep, None, True,
         "MANIFEST_RENDER_SLOT_UNKNOWN"),
        ("a sixth kind", _set("kind", "stream"), keep, None, True, "MANIFEST_KIND_UNKNOWN"),
        ("a continuous kind with no coverage proof",
         _seq(_set("kind", "continuous"), _set("health.probe_unit", "subscription")), keep, None, True,
         "MANIFEST_KIND_DISAGREES"),
        ("routing on a one_shot", _set("routing", "roster"), keep, None, True, "MANIFEST_KIND_DISAGREES"),
        ("a ManualTask on a one_shot", _set("emits.3", {"entity": "ManualTask", "layer": "observation",
                                                        "collector": "human"}), keep, None, True,
         "MANIFEST_KIND_DISAGREES"),
        ("a geo kind with no geo_area", _seq(_set("kind", "geo"), _set("bystanders", declared_followers)),
         keep, None, True, "MANIFEST_KIND_DISAGREES"),
        ("a retention duration in lineage", _set("lineage.retain", {"text": "forever", "media": "90d"}),
         keep, None, True, "MANIFEST_LINEAGE_DURATION"),
        ("a duration for the stratum", _set("lineage.retention_stratum", "90d"), keep, None, True,
         "MANIFEST_LINEAGE_DURATION"),
        ("a command slot nobody declares",
         _set("lineage.command_template", "selftest-tool --user {username} --page {page}"), keep, None, True,
         "MANIFEST_COMMAND_TEMPLATE_SLOT"),
        ("a credential value key in auth", _set("auth.session", "x"), keep, None, True,
         "MANIFEST_AUTH_NOT_A_REFERENCE"),
        ("no exposure on an authenticated read", _set("exposure.level", "none"), keep, None, True,
         "MANIFEST_EXPOSURE_UNDERSTATED"),
        ("an unauthenticated class with an auth pool", _set("interaction_class", "passive_unauthenticated"),
         keep, None, True, "MANIFEST_INTERACTION_DISAGREES"),
        ("interaction_class induces_disclosure", _set("interaction_class", "induces_disclosure"), keep, None, True,
         "MANIFEST_INTERACTION_EXCLUDED"),
        ("no interaction_class", _del("interaction_class"), keep, None, True, "MANIFEST_INTERACTION_CLASS_INVALID"),
        ("a secret_ref parameter with a default",
         _set("params", [{"key": "session", "type": "secret_ref", "default": "x", "label": "Session"}]),
         keep, None, True, "MANIFEST_SHAPE_INVALID"),
        ("consumes naming no selector", _set("consumes", {"required": []}), keep, None, True,
         "MANIFEST_TARGETING_NO_SELECTOR"),
        ("a required input with no refusal fixture", _set("health.refusal_fixtures", []), keep, None, True,
         "MANIFEST_REFUSAL_FIXTURE_MISSING"),
        ("a refusal fixture id the file lacks", _set("health.refusal_fixtures.0.id", "refuse-nothing"), keep,
         None, True, "MANIFEST_REFUSAL_FIXTURE_ABSENT"),
        ("a refusal fixtures file that does not exist", _set("health.refusal_fixtures.0.fixtures", "absent.jsonl"),
         keep, None, True, "MANIFEST_REFUSAL_FIXTURE_ABSENT"),
        ("a refusal fixture that supplies its field", _set("health.refusal_fixtures.0.id", "supplies-username"),
         keep, None, True, "MANIFEST_REFUSAL_FIXTURE_MISMATCH"),
        ("a refusal fixture whose result is events", _set("health.refusal_fixtures.0.id", "events-line"), keep,
         None, True, "MANIFEST_REFUSAL_FIXTURE_MISMATCH"),
        ("a refusal fixture of another connector", _set("health.refusal_fixtures.0.id", "other-connector"), keep,
         None, True, "MANIFEST_REFUSAL_FIXTURE_MISMATCH"),
        ("a refusal fixture with an undeclared code", _set("health.refusal_fixtures.0.id", "undeclared-code"), keep,
         None, True, "MANIFEST_REFUSAL_CODE_UNDECLARED"),
        ("a null input refusal fixture permits", _set("health.refusal_fixtures.0.id", "refuse-null-username"), keep,
         None, True, None),
        ("an events fixture with no event_count", lambda m: None,
         lambda fxs: [dict(fx, event_count=None) if fx["id"] == "events-line" else fx for fx in fxs],
         None, True, "MANIFEST_REFUSAL_FIXTURE_SHAPE"),
        ("a fixture input that is not a placeholder", lambda m: None,
         lambda fxs: [dict(fx, input={"username": "not-a-placeholder"}) if fx["id"] == "supplies-username" else fx
                      for fx in fxs],
         None, True, "MANIFEST_REFUSAL_FIXTURE_SHAPE"),
        # The review of 2026-10-28.
        ("a consumed handle with no platform", _del("consumes.required.0.platform"), keep, None, True,
         "MANIFEST_SELECTOR_PLATFORM"),
        ("an emitted platform_uid with no platform", _del("emits.0.platform"), keep, None, True,
         "MANIFEST_SELECTOR_PLATFORM"),
        ("a platform on a key whose form binds none", _set("emits.1.platform", "synthplatform"), keep, None, True,
         "MANIFEST_SELECTOR_PLATFORM"),
        # MF-R17, reading SH-R5, 2026-10-28: a sweep's emit takes its platform from the item.
        ("platform_from_item in place of platform on an endpoint sweep permits",
         _seq(_del("emits.2.platform"), _set("emits.2.platform_from_item", True), _set("health.probe_unit", "endpoint")),
         keep, None, True, None),
        ("platform_from_item on a manifest whose probe_unit is connector",
         _seq(_del("emits.2.platform"), _set("emits.2.platform_from_item", True)), keep, None, True,
         "MANIFEST_SELECTOR_PLATFORM"),
        ("platform and platform_from_item both on one emit",
         _seq(_set("emits.2.platform_from_item", True), _set("health.probe_unit", "endpoint")), keep, None, True,
         "MANIFEST_SELECTOR_PLATFORM"),
        ("platform_from_item on a key whose form binds none",
         _seq(_set("emits.1.platform_from_item", True), _set("health.probe_unit", "endpoint")), keep, None, True,
         "MANIFEST_SELECTOR_PLATFORM"),
        ("platform_from_item on a consumed selector",
         _seq(_del("consumes.required.0.platform"), _set("consumes.required.0.platform_from_item", True),
              _set("health.probe_unit", "endpoint")), keep, None, True, "MANIFEST_SHAPE_INVALID"),
        ("platform_from_item written false",
         _seq(_del("emits.2.platform"), _set("emits.2.platform_from_item", False), _set("health.probe_unit", "endpoint")),
         keep, None, True, "MANIFEST_SHAPE_INVALID"),
        # The schema's entity branch is the only mechanism refusing this, so it has its own case.
        ("platform_from_item on an entity emit",
         _seq(_set("emits.3.platform_from_item", True), _set("health.probe_unit", "endpoint")), keep, None, True,
         "MANIFEST_SHAPE_INVALID"),
        ("a bool parameter with a string default", _set("params.0.default", "yes"), keep, None, True,
         "MANIFEST_PARAM_DEFAULT_INVALID"),
        ("an int parameter with a boolean default",
         _set("params", [{"key": "pages", "type": "int", "default": True, "label": "Pages"}]), keep, None, True,
         "MANIFEST_PARAM_DEFAULT_INVALID"),
        ("an enum parameter default outside its values",
         _set("params", [{"key": "mode", "type": "enum", "values": ["fast", "full"], "default": "slow",
                          "label": "Mode"}]), keep, None, True, "MANIFEST_PARAM_DEFAULT_INVALID"),
        ("an enum parameter default among its values permits",
         _set("params", [{"key": "mode", "type": "enum", "values": ["fast", "full"], "default": "full",
                          "label": "Mode"}]), keep, None, True, None),
        ("a geo connector declaring followers", _seq(geo_kind, _set("bystanders", declared_followers)), keep,
         None, True, "MANIFEST_BYSTANDER_CLASS_UNKNOWN"),
        ("a geo_area parameter on a named_selector_only one_shot", with_area_param, keep, None, True,
         "MANIFEST_BYSTANDER_UNDECLARED"),
        ("a geo_area parameter on a one_shot declaring followers",
         _seq(with_area_param, _set("bystanders", declared_followers)), keep, None, True,
         "MANIFEST_BYSTANDER_CLASS_UNKNOWN"),
        ("an entity field named for a proposed registry key",
         lambda m: m["emits"][3]["fields"].append({"name": "postal_address"}), keep, None, True,
         "MANIFEST_ENTITY_FIELD_IS_SELECTOR"),
        ("a command template naming no consumed input",
         _set("lineage.command_template", "selftest-tool --credential {credential_ref} --sweep"), keep, None, True,
         "MANIFEST_TARGETING_NO_SELECTOR"),
        ("a command template naming only an optional input beside a required one",
         _set("lineage.command_template", "selftest-tool --credential {credential_ref} --uid {user_id}"), keep,
         None, True, "MANIFEST_TARGETING_NO_SELECTOR"),
        ("a canary input with an at-sign inside brackets",
         _set("health.canaries.known_positive.input.username", at_sign), keep, None, True,
         "MANIFEST_CANARY_INPUT_VALUE"),
        ("a canary input with spaces inside brackets",
         _set("health.canaries.known_negative.input.username", "<two words>"), keep, None, True,
         "MANIFEST_CANARY_INPUT_VALUE"),
        ("a canary input with a trailing newline",
         _set("health.canaries.known_positive.input.username", "<cast_linked_handle>\n"), keep, None, True,
         "MANIFEST_CANARY_INPUT_VALUE"),
        ("a fixture input with an at-sign inside brackets", lambda m: None,
         lambda fxs: [dict(fx, input={"username": at_sign}) if fx["id"] == "supplies-username" else fx
                      for fx in fxs],
         None, True, "MANIFEST_REFUSAL_FIXTURE_SHAPE"),
        ("one empty fixture named for two required inputs",
         _second_required([("username", "refuse-no-username"), ("user_id2", "refuse-no-username")]), keep,
         None, True, "MANIFEST_REFUSAL_FIXTURE_MISMATCH"),
        ("a refusal fixture that also withholds a second required input",
         _second_required([("username", "refuse-no-username"), ("user_id2", "refuse-no-uid2")]), keep,
         None, True, "MANIFEST_REFUSAL_FIXTURE_MISMATCH"),
        ("two required inputs each with its own refusal fixture permits",
         _second_required([("username", "refuse-no-username-uid2-given"), ("user_id2", "refuse-no-uid2")]), keep,
         None, True, None),
    ] + token_case


def _structural_controls(ctx: dict) -> list[tuple[str, bool]]:
    """Controls that are not one manifest break."""
    out: list[tuple[str, bool]] = []
    for name, schema in (("manifest", ctx["schema"]), ("fixture", ctx["fixture_schema"])):
        try:
            Draft202012Validator.check_schema(schema)
            ok = True
        except SchemaError:
            ok = False
        out.append((f"the {name} schema is valid against the draft 2020-12 metaschema", ok))
    broken = copy.deepcopy(ctx["schema"])
    broken["properties"]["kind"]["enum"] = "five"
    try:
        Draft202012Validator.check_schema(broken)
        ok = False
    except SchemaError:
        ok = True
    out.append(("a schema with a malformed enum is refused by the metaschema", ok))
    out.append(("the copied enums agree with their sources", not drift_findings(ctx)))
    drifted = dict(ctx)
    drifted["fixture_schema"] = copy.deepcopy(ctx["fixture_schema"])
    drifted["fixture_schema"]["properties"]["adapter_state"]["enum"].append("maybe")
    out.append(("a fixture state the layer model lacks is drift",
                any(f.code == "MANIFEST_SCHEMA_DRIFT" for f in drift_findings(drifted))))
    drifted = dict(ctx)
    drifted["schema"] = copy.deepcopy(ctx["schema"])
    drifted["schema"]["$defs"]["bystander_class"]["properties"]["disposition"]["enum"].append("retain")
    out.append(("a disposition enum widened to retain is drift against the layer model",
                any(f.code == "MANIFEST_SCHEMA_DRIFT" for f in drift_findings(drifted))))
    return out


def _main_controls(base: Path) -> list[tuple[str, bool]]:
    """main() run against scratch files: the exit codes the docstring promises."""
    out: list[tuple[str, bool]] = []
    mdir = _write_case(base, _baseline_fixtures())
    good = mdir / "manifest.yaml"
    good.write_text(yaml.safe_dump(_baseline(), sort_keys=False), encoding="utf-8")
    bad = base / "not-yaml.yaml"
    bad.write_text("a: [1, 2\nb: }\n", encoding="utf-8")
    unregistered = base / "unregistered.yaml"
    m = _baseline()
    m["emits"][0]["selector"] = "not_a_registry_key"
    unregistered.write_text(yaml.safe_dump(m, sort_keys=False), encoding="utf-8")
    empty = base / "empty-connectors"
    empty.mkdir()
    connectors = base / "connectors"

    def captured(fn, *args) -> tuple[int, str]:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            rc = fn(*args)
        return rc, buf.getvalue()

    def refuses(fn, args, code: str) -> bool:
        rc, text = captured(fn, *args)
        return rc == 1 and f"REFUSED {code}\n" in text

    sink = io.StringIO()
    with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
        out.append(("a file that is not YAML exits 2", main([str(bad)]) == 2))
        out.append(("a missing file exits 2", main([str(base / "absent.yaml")]) == 2))
        out.append(("the baseline written to disk exits 0", main([str(good)]) == 0))
        out.append(("--shape passes an unregistered selector and claims nothing", main(["--shape", str(unregistered)]) == 0))
        out.append(("the full gate refuses the same file", main([str(unregistered)]) == 1))
        ctx = load_context()
        out.append(("--all over zero manifests exits 0", run_all(ctx, True, empty) == 0))
        out.append(("--all over the scratch connectors exits 0", run_all(ctx, True, connectors) == 0))
        (connectors / "__pycache__").mkdir()
        out.append(("--all ignores an underscore directory that holds no manifest",
                    run_all(ctx, True, connectors) == 0))
        for hidden in ("_draft_conn", ".wip_conn"):
            hdir = connectors / hidden
            hdir.mkdir()
            (hdir / "manifest.yaml").write_text(good.read_text(encoding="utf-8"), encoding="utf-8")
            out.append((f"--all refuses a manifest under a directory whose name starts with {hidden[0]}",
                        refuses(run_all, (ctx, True, connectors), "MANIFEST_DIRECTORY_HIDDEN")))
            (hdir / "manifest.yaml").unlink()
            hdir.rmdir()
        text = good.read_text(encoding="utf-8")
        dup = mdir / "manifest_duplicate_key.yaml"
        dup.write_text("interaction_class: induces_disclosure\n" + text, encoding="utf-8")
        out.append(("a manifest repeating a key is refused",
                    refuses(main, ([str(dup)],), "MANIFEST_DUPLICATE_KEY")))
        out.append(("--shape refuses a manifest repeating a key",
                    refuses(main, (["--shape", str(dup)],), "MANIFEST_DUPLICATE_KEY")))
        fx = dict(_fixture("refuse-no-username"))
        line = json.dumps(fx)
        (mdir / "fixtures_duplicate_key.jsonl").write_text(
            '{"input": {"username": "not-a-placeholder"}, ' + line[1:] + "\n", encoding="utf-8")
        m = _baseline()
        m["health"]["refusal_fixtures"][0]["fixtures"] = "fixtures_duplicate_key.jsonl"
        dupfx = mdir / "manifest_duplicate_fixture_key.yaml"
        dupfx.write_text(yaml.safe_dump(m, sort_keys=False), encoding="utf-8")
        out.append(("a fixture line repeating a key is refused",
                    refuses(main, ([str(dupfx)],), "MANIFEST_REFUSAL_FIXTURE_SHAPE")))
        (connectors / "no_manifest").mkdir()
        out.append(("--all refuses a connector directory with no manifest", run_all(ctx, True, connectors) == 1))
    return out


def self_test(quiet: bool = False) -> int:
    os.environ["PLAINSIGHT_NO_GATE_LOG"] = "1"
    try:
        ctx = load_context()
    except ToolFailure as fail:
        print(fail.render(), file=sys.stderr)
        return 2
    failures = 0

    def show(ok: bool, label: str, detail: str = "") -> None:
        if not quiet or not ok:
            print(f"  {'held   ' if ok else 'BROKEN '}  {label}{detail}")

    for label, ok in _structural_controls(ctx):
        failures += 0 if ok else 1
        show(ok, label)

    cases = _cases(ctx["pin_text"], ctx["cast_tokens"])
    main_results: list[tuple[str, bool]] = []
    with tempfile.TemporaryDirectory(prefix="plainsight-manifest-selftest-") as tmp:
        for n, (desc, mutate, fx_mutate, pin_text, golden, expected) in enumerate(cases):
            base = Path(tmp) / f"case{n:02d}"
            fixtures = _baseline_fixtures()
            if fx_mutate is not None:
                fixtures = [{k: v for k, v in fx.items() if v is not None or k == "input"}
                            for fx in fx_mutate(fixtures)]
            mdir = _write_case(base, fixtures, golden=golden)
            m = _baseline()
            try:
                mutate(m)
                case_ctx = ctx if pin_text is None else dict(ctx, pin=pin_of_record.Pin(pin_text, ROOT))
                fired = {f.code for f in check_manifest(m, case_ctx, f"selftest/{SELFTEST_ID}/manifest.yaml",
                                                        mdir, expect_id=SELFTEST_ID)}
                ok = (not fired) if expected is None else (expected in fired)
                detail = "" if ok else f"  expected {expected or 'no refusal'}, fired {sorted(fired)}"
            except Exception as exc:  # a crash is a failure of the case, never a pass
                ok, detail = False, f"  crashed: {exc.__class__.__name__}: {exc}"
            failures += 0 if ok else 1
            verb = "permitted" if expected is None else "refused  "
            show(ok, f"{verb} {desc}", detail)
        try:
            main_results = _main_controls(Path(tmp) / "controls")
        except Exception as exc:  # a crash is a failure, never a pass
            main_results = [(f"the main() controls crashed: {exc.__class__.__name__}", False)]
        for label, ok in main_results:
            failures += 0 if ok else 1
            show(ok, label)

    total = len(cases) + len(_structural_controls(ctx)) + len(main_results)
    if failures:
        print(
            f"validate_manifest --self-test: {failures} of {total} case(s) did not behave as claimed. A check "
            "nobody has watched refuse is an assumption (doctrine/HYGIENE.md section 2).\n"
            "  moves: fix the check that did not fire, or the case if it no longer plants the defect it "
            "names; a case that now permits where it refused is a widening and Class F by effect",
            file=sys.stderr,
        )
        return 1
    if not quiet:
        refusals = sum(1 for c in cases if c[-1] is not None)
        print(f"validate_manifest --self-test ok: {refusals} breaks refused by their own codes, "
              f"{len(cases) - refusals} permits held, {total - len(cases)} controls held")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
