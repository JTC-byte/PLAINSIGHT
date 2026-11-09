#!/usr/bin/env python3
"""Selector registry self-lint: the closed vocabulary D2 is entirely about.

`ontology/selectors.yaml` is rank 3 and Class B. Every connector manifest
declares its `emits` and `consumes` against it, every EXTRACT_EVENT carries a
`selector_type` that must be a key in it, and every citation check reads its
prohibitions. A defect here is a defect an analyst reads as a fact, which is the
failure class docs/PLAINSIGHT-FOUNDATION.md D2 exists to remove: a value that is
present, well-formed and plausible passes every guard that keys on absence.

Each check guards a defect that is one edit away in that file:

  O-01  A selector omits form, datum_class, stability, may_anchor_entity or a
        note. A datum with no declared class is the exact thing D2 removes.
  O-02  A selector names a datum class, stability class, provenance state or
        false-positive basis that the file does not declare. A closed
        vocabulary with an unchecked member is an open one.
  O-03  A constraint selector is anchorable, or carries no matcher, or carries
        no constraint_semantics. This is Step 6's done-condition in
        docs/THE-GAMEPLAN.md, stated there in those words, so it holds its own
        code rather than being folded into O-01.
  O-04  The set of anchor-eligible selectors and the set of anchors the entity
        types declare disagree. Neither list is hard-coded here: the check is
        that the two agree, so an anchor cannot be granted in one place alone.
  O-05  An entity is anchored on a selector whose stability class does not
        permit anchoring. docs/PLAINSIGHT-design.md section 2.2 is the rule: a
        handle-owner change under handle-anchoring renders as ordinary drift
        when it is an identity catastrophe. Fixture 3 is the corpus half.
  O-06  A generated selector loses provenance_state GENERATED,
        requires_validation_by or circularity_class. The last of those is what
        the Merge Sheet's circularity check reads, so dropping it silently
        unblocks a self-confirming merge.
  O-07  A resolves_to, a must_not_satisfy_citation_for, a must_not_render_as or
        a prohibition names a selector that does not exist.
  O-08  A selector names a matcher the matchers block does not declare, or a
        selector carries no matcher at all. SS-19 refuses an argv interpolation
        whose value does not match its registered matcher, so a selector with
        no matcher cannot be refused at argv.
  O-09  A declared matcher is referenced by nothing. A dead matcher is a
        library nobody calls and a calibration nobody will ever run.
  O-10  A violation code named in the registry is not declared in
        spec/layer-model.yaml. The code vocabulary is read from that file rather
        than from a copy, so the two cannot drift.
  O-11  The entity set is not the closed set, an entity is anchored on an
        unregistered selector, or an entity declares neither an anchor nor a
        materialization act. An entity nothing can create is a table with no
        writer, and an entity anything can create is the identity-minting
        failure the design names.
  O-12  A selector value reached the file. Every variable part of every form and
        every example must be a placeholder, and the raw text must carry no
        address-shaped, handle-shaped or long-digit token. AGENTS.md section 4
        is the rule and this is the mechanism.
  O-13  A selector declares resolves_to and no prohibition covers it.
        resolves_to is what invites a renderer to follow the relation and print
        the thing on the far end, so the relation and the refusal ship together.
  O-14  The repo scan's three detectability lists do not partition the selector
        set, name an unregistered type, or exempt a document that is not in the
        tree. RT-15's scan is only implementable against a complete list.
  O-15  The registry stops declaring itself closed, or the matchers block claims
        a calibration that does not exist. An unscored matcher may not be an
        identity basis, and a file that says otherwise is the laundering
        CLAUDE.md design gate 6 forbids.
  O-16  A selector carries an fp_mode with no fp_mode_basis. CLAUDE.md design
        gate 3: a claim about a capability says how the answer was known.
  O-17  ontology.proposed and the selectors marked PROPOSED disagree. The
        operator ratifies additions, so the list they read has to be the list
        the file implements.

`--registry` is the default and runs every check above. It also runs O-M1 to
O-M3 below, so that a refusal of theirs reaches the kernel gate through the
IMPLEMENTED ontology entry while the ontology-matchers entry is STUB (reading
O-R6).

`--corpus` reads conformance/must-pass.jsonl and conformance/must-fail.jsonl at
every site spec/layer-model.yaml binds to this registry, which is every field
the layer model declares with `registry: ontology/selectors.yaml`. The sites are
read from the layer model rather than listed here, and every run prints them.

  O-C1  A selector type at a site is not a key in this registry. Rung 2 refuses
        the same thing first, because tools/validate.py's generated schema
        inlines the registry keys as the enum of every registry-bound field.
        The duplicate is deliberate: this mode reads the registry itself, so a
        stale generated schema cannot hide an unregistered type from it.
  O-C2  A selector value does not fit its key's form. The form is read as a
        pattern: separators are literal and each <slot> takes any text. A
        <placeholder> fits any slot, and a value that is one placeholder stands
        in for the whole value (reading O-R1). A form with a <platform> slot
        needs a platform token of the shape ^[a-z][a-z0-9_]*$ there, and an
        empty slot is refused. A filled value is the repo scan's business
        rather than this mode's, so a filled slot other than <platform> is not
        graded.
  O-C3  The vacuity guard. A must-fail row whose expected code is one this mode
        refuses is refused by this mode for that code and no other, and a
        must-fail row that expects only another code is not also refused here.
        A fixture this mode passes while claiming its code proves nothing.
  O-C4  A registry key is exercised by no must-pass row and its note does not
        say it is unexercised at this registry version, or its note says so
        while a must-pass row exercises it. A key that can be added and never
        proven is the closed vocabulary's own untested surface.

`--matchers` runs the structural half of the matcher check and says in its
output what it cannot check. No matcher is scored, because scoring needs
labelled ground truth and ground truth needs a sealed cast. It reruns O-08 and
O-09 rather than copying them, and adds three checks.

  O-M1  calibrated or identity_basis_permitted is anything but false while the
        file calibration_ref names does not exist. The flag is the only thing
        enforcing the identity-basis rule until a calibration file exists.
  O-M2  A connector's adapter.py or manifest.yaml names a matcher id the
        library does not declare. SS-19 refuses an argv value that does not
        match its registered matcher, so a name that resolves to nothing is a
        gate that cannot run.
  O-M3  A library entry carries no note, or a purpose outside the two the
        registry uses, argv_shape_gate and constraint_satisfaction (reading
        O-R7).

`--self-test` breaks the loaded registry in memory in sixteen directions, plants
each --corpus code in in-memory copies of the corpora and the registry, and
plants each --matchers code in in-memory copies of the registry and the
connector sources, and asserts each break is refused by its code, which is
doctrine/HYGIENE.md section 2's rule for a newly written check. It plants the
O-M codes a second time through the default mode, and plants an absent
corpus, an unparseable row and a layer model that binds no site, each of which
must refuse. Every refusal a plant draws is also read for its moves: a move
that offers to set a kernel gate entry to STUB, PENDING, UNRATIFIED or
DEFERRED recommends hiding the fault the gate found, and the plant fails.

READINGS below records the interpretive calls these modes make, on the
tools/validate_retention.py pattern. Confirming or reversing one is the
maintainer's decision rather than an edit in place.

Exit codes: 0 clean, 1 violations found, 2 the registry, the code vocabulary, the
layer model's sites or a corpus could not be read.
"""

from __future__ import annotations

import argparse
import ast
import copy
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print(
        "REFUSED ONTOLOGY_UNREADABLE\n"
        "  what:  PyYAML is not installed, so the registry cannot be parsed\n"
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
REGISTRY = ROOT / "ontology" / "selectors.yaml"
LAYER_MODEL = ROOT / "spec" / "layer-model.yaml"
REL = "ontology/selectors.yaml"
GATE = "ontology"

#: Fields every selector declares, whatever its class.
SELECTOR_REQUIRED = ("form", "datum_class", "stability", "may_anchor_entity", "note")

#: docs/THE-GAMEPLAN.md Step 6's done-condition, in its own words.
CONSTRAINT_REQUIRED = ("matcher", "constraint_semantics")

#: docs/PLAINSIGHT-design.md section 4.6 and section 5.5.
GENERATED_REQUIRED = ("provenance_state", "requires_validation_by", "circularity_class")

#: docs/PLAINSIGHT-FOUNDATION.md section 4.1's closed entity set, repeated in
#: spec/layer-model.yaml's ADJUDICATE_EVENT entity_type enum.
ENTITY_TYPES = (
    "Account",
    "PersonCandidate",
    "Org",
    "Channel",
    "Place",
    "Media",
    "ManualTask",
)

MATERIALIZATION_ACTS = ("analyst_act", "connector_emission")

#: A form's variable parts. Anything that is not a placeholder or a separator is
#: a value, and a value does not belong in a tracked file.
PLACEHOLDER = r"<[a-z0-9_|]+>"
SEPARATOR = r"[/\-.,+:| ]"
TEMPLATE_RE = re.compile(rf"^(?:{PLACEHOLDER}|{SEPARATOR})+$")

#: Shapes a live selector value takes in free text. Narrow on purpose: each one
#: is a shape no legitimate line of this registry can carry.
VALUE_SHAPES = (
    ("an address-shaped token", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("a handle-shaped token", re.compile(r"(?<![A-Za-z0-9_])@[A-Za-z0-9_]{3,}")),
    ("a digit run long enough to be a number or a uid", re.compile(r"(?<!\d)\d{7,}(?!\d)")),
)

#: A violation code mentioned in prose. Three or more underscore-separated
#: capitalised parts, which is the shape every declared code takes and which no
#: ordinary word in the file matches.
CODE_IN_TEXT_RE = re.compile(r"\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+){2,}\b")

#: --corpus. The two corpora Step 7 wrote, in the order they are read.
CORPORA = (
    ("must-pass", ROOT / "conformance" / "must-pass.jsonl", "conformance/must-pass.jsonl"),
    ("must-fail", ROOT / "conformance" / "must-fail.jsonl", "conformance/must-fail.jsonl"),
)

#: A form's slots, read the way tools/validate_retention.py reads them for the
#: repo scan, so the two modes split a form identically.
FORM_SLOT_RE = re.compile(r"<([^<>]+)>")

#: A slot or a whole value that is a placeholder. The corpora write
#: placeholders such as <synthetic-handle-1>, wider than a form's <slot> names.
VALUE_PLACEHOLDER_RE = re.compile(r"^<[^<>]+>$")

#: The slot a platform-bound form carries, and the token shape it needs there.
PLATFORM_SLOT = "platform"
PLATFORM_TOKEN_RE = re.compile(r"^[a-z][a-z0-9_]*$")

#: The layer-model codes --corpus refuses for itself, each with the finding code
#: that carries it. O-C3 holds a must-fail row expecting one of these to this
#: mode. Reading O-R3 says why the registry-driven codes are not here.
CORPUS_OWNED_CODES = {"SELECTOR_TYPE_UNREGISTERED": "ONT_CORPUS_SELECTOR_UNREGISTERED"}

#: The words a selector's note carries when no must-pass row exercises it. The
#: version is read from ontology.version, so a version change asks for the
#: declaration again rather than inheriting it (reading O-R4).
UNEXERCISED_WORDS = "unexercised at v{version}"

#: --matchers. The purposes the registry's matchers block uses. The registry
#: declares no vocabulary for them, so this pair is a reading (O-R7).
MATCHER_PURPOSES = ("argv_shape_gate", "constraint_satisfaction")

#: A matcher id as the library writes one: namespace, name, pinned version.
MATCHER_ID_RE = re.compile(r"\b[a-z][a-z0-9_]*\.[a-z0-9_]+\.v[0-9]+\b")

#: The files of a connector O-M2 reads for a matcher id (reading O-R8).
CONNECTORS = ROOT / "connectors"
CONNECTOR_FILES = ("adapter.py", "manifest.yaml")

#: A reading id as the connector READMEs and this repository's tools write one.
READING_ID_RE = re.compile(r"\b[A-Z]{1,4}-R[0-9]+\b")

#: --self-test. A move that sets a kernel gate entry's state. A refusal offering
#: one recommends hiding the fault the gate found, so a plant whose refusal
#: carries one of these words in its moves fails.
GATE_STATE_MOVE_RE = re.compile(r"\b(?:STUB|PENDING|UNRATIFIED|DEFERRED)\b")


# ---------------------------------------------------------------------------
# READINGS
#
# Interpretive calls --corpus and --matchers had to make where no governed
# source answers the question. Recorded on the tools/validate_retention.py
# pattern so the maintainer can confirm or reverse each one rather than find it
# in the code. Nothing here adds a registry key, changes a form or touches the
# cast.
# ---------------------------------------------------------------------------

#: (id, question, the reading taken, what would change it)
READINGS = (
    (
        "O-R1",
        "How a corpus value that is one placeholder is held to a form with two "
        "slots, such as <synthetic-handle-1> against handle:<platform>/<string>",
        "It stands in for the whole value, fits any form, and carries no platform "
        "token to check. On the corpora of 2026-11-02 every value at a site is one "
        "placeholder, so O-C2's form and token checks refuse nothing on the real "
        "rows and bite only on a value written with its separators. Every run "
        "counts these values and says so",
        "The corpora writing structured placeholders such as "
        "<platform>/<synthetic-handle-1>, a change to tools/build_corpus.py and "
        "conformance/, after which the token check bites on the real rows",
    ),
    (
        "O-R2",
        "Whether a CLAIM's value carries its type prefix, as in handle:<...>, or "
        "only the part after it",
        "Either is accepted. A value whose prefix names a different registered "
        "key is refused under O-C2, because the value then says it is a "
        "different type from the selector_type beside it",
        "spec/layer-model.yaml stating which of the two a CLAIM's value is, at "
        "which point the other is refused",
    ),
    (
        "O-R3",
        "Which codes are ontology codes for O-C3's vacuity guard",
        "Only SELECTOR_TYPE_UNREGISTERED, the one this mode refuses. "
        "SELECTOR_ANCHOR_PROHIBITED, HINT_CITED_AS_VALUE and "
        "GENERATED_CITED_AS_OBSERVED are driven by the registry and need an "
        "entity type or a citation's lineage to decide, and rung 2 refuses them "
        "for their fixtures. O-C3 also refuses a must-fail row with expect_only "
        "true that this mode refuses for a code the row does not expect, which is "
        "the same guard from the other side",
        "This mode taking over one of the registry-driven codes, which adds it to "
        "CORPUS_OWNED_CODES in the same change",
    ),
    (
        "O-R4",
        "Where a key that no must-pass row exercises is declared unexercised",
        "In the selector's own note, as the words 'unexercised at v' plus "
        "ontology.version. Thirteen notes in ontology/selectors.yaml carry the "
        "words since 2026-11-02, written by the builder of this mode. That is a "
        "rank-3 edit of words alone, with no key, form or field added",
        "A list under ontology naming the unexercised keys, which is a new field "
        "and so a shape change; or must-pass rows written for the thirteen, "
        "after which O-C4 refuses the words until they are removed",
    ),
    (
        "O-R5",
        "Whether a clean --corpus run is rung 3 of CONFORMANCE.md section 3 for "
        "a connector",
        "No. The mode reads the repository's two corpora and no connector's "
        "emitted events, so it proves the corpora's selectors against the "
        "registry and proves nothing about a connector. Rung 2's generated enum "
        "still carries registry membership for an emitted event",
        "A --file argument that reads a connector's sample output, which would "
        "make this mode the rung 3 tool the ladder names",
    ),
    (
        "O-R6",
        "Whether the ontology-matchers kernel gate entry moves from STUB to "
        "IMPLEMENTED now that the structural half runs",
        "Left to the maintainer, and the entry stays STUB with its note saying "
        "the structural half runs. The aggregator runs a STUB entry's command "
        "and does not read its exit code, so the fixer pass of 2026-11-02 made "
        "the default mode run O-M1 to O-M3 as well: a refusal of theirs now "
        "fails the IMPLEMENTED ontology entry and the pre-commit hook, and the "
        "self-test plants three of them through the default mode. O-15 also "
        "refuses a calibration flag there under its own code, so a flag fault "
        "can draw two refusals in that mode. CONFORMANCE.md has no rule on a "
        "mode that checks structure and says so",
        "The maintainer's decision. IMPLEMENTED for ontology-matchers adds the "
        "matchers report to the kernel gate and keeps the scoring half deferred "
        "in the mode's own output. Reversing the fixer's change is one line in "
        "main(), the default mode calling check() instead of registry_lint(), "
        "and the three default-mode plants then fail until they are removed",
    ),
    (
        "O-R7",
        "Which purposes a matcher library entry may carry, and the code that "
        "refuses one outside them",
        "argv_shape_gate and constraint_satisfaction, the two the registry uses "
        "and its matchers comment describes. The registry declares no vocabulary "
        "for purposes, so the pair is a constant here, and O-M3 is a code the "
        "brief for this mode did not name",
        "A purposes block in ontology/selectors.yaml that this mode reads instead, "
        "which is a registry shape change",
    ),
    (
        "O-R8",
        "What counts as a connector using a matcher by name for O-M2",
        "Any token of the shape namespace.name.vN in a connector's adapter.py or "
        "manifest.yaml, in code or in prose. connectors/sherlock/adapter.py names "
        "shape.username.v1 in a docstring only. A connector that applies a "
        "matcher without naming it is not found, and which purpose a connector "
        "uses a matcher for is not checked",
        "A manifest field naming the matchers a connector applies, which the "
        "manifest schema does not carry",
    ),
    (
        "O-R9",
        "Whether the context events of a must-fail row are held to O-C1 and O-C2",
        "Yes. A row's context is presented as the legal history its event is "
        "refused against, so a defect there is a second defect the fixture did "
        "not mean to carry. They do not count toward O-C4, which reads must-pass "
        "rows alone",
        "A must-fail row that needs an illegal context to be refused for its own "
        "code, which would move that row's context out of this check by name",
    ),
)


class Finding:
    __slots__ = ("code", "where", "detail", "moves", "rule")

    def __init__(self, code: str, where: str, detail: str, moves: str, rule: str = ""):
        self.code = code
        self.where = where
        self.detail = detail
        self.moves = moves
        self.rule = rule

    def render(self) -> str:
        return (
            f"REFUSED {self.code}\n"
            f"  where: {self.where}\n"
            f"  what:  {self.detail}\n"
            + (f"  rule:  {self.rule}\n" if self.rule else "")
            + f"  moves: {self.moves}"
        )


def at(path: str) -> str:
    """A location gate_log will accept: a repository path plus a dotted node."""
    return f"{REL} :: {path}"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _as_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _walk(node, key: str):
    """Every value stored under `key`, at any depth."""
    if isinstance(node, dict):
        for k, v in node.items():
            if k == key:
                yield v
            yield from _walk(v, key)
    elif isinstance(node, list):
        for item in node:
            yield from _walk(item, key)


def declared_codes() -> set[str]:
    """The event-type code vocabulary, read from the layer model itself.

    O-10. Copying the list here would give the repository two vocabularies that
    agree until the day one of them changes.
    """
    model = yaml.safe_load(LAYER_MODEL.read_text(encoding="utf-8"))
    if not isinstance(model, dict):
        raise ValueError("the layer model did not parse to a mapping")
    out: set[str] = set()
    for entry in _as_list((model.get("violation_codes") or {}).get("codes")):
        if isinstance(entry, dict) and entry.get("code"):
            out.add(str(entry["code"]))
        elif isinstance(entry, str):
            out.add(entry)
    if not out:
        raise ValueError("the layer model declares no violation codes")
    return out


# ---------------------------------------------------------------------------
# the checks
# ---------------------------------------------------------------------------


def check(reg: dict, text: str, codes: set[str]) -> list[Finding]:
    f: list[Finding] = []
    meta = reg.get("ontology") or {}
    selectors = reg.get("selectors") or {}
    entities = reg.get("entities") or {}
    matchers = reg.get("matchers") or {}
    library = matchers.get("library") or {}
    prohibitions = _as_list(reg.get("prohibitions"))
    scan = reg.get("repo_scan") or {}
    datum_classes = set((reg.get("datum_classes") or {}).keys())
    stability_classes = reg.get("stability_classes") or {}
    provenance_states = set((reg.get("provenance_states") or {}).keys())
    fp_bases = set((reg.get("fp_mode_bases") or {}).keys())

    f += check_selector_fields(selectors, datum_classes, stability_classes, provenance_states, fp_bases)
    f += check_constraints(selectors)
    f += check_generated(selectors)
    f += check_anchors(selectors, entities, stability_classes)
    f += check_entities(selectors, entities)
    f += check_relations(selectors, prohibitions)
    f += check_matchers(selectors, library)
    f += check_codes(reg, text, codes)
    f += check_no_values(selectors, reg, text)
    f += check_repo_scan(selectors, scan)
    f += check_claims(meta, matchers)
    f += check_proposed(meta, selectors)
    return f


def check_selector_fields(selectors, datum_classes, stability_classes, provenance_states, fp_bases) -> list[Finding]:
    """O-01, O-02, O-16."""
    out: list[Finding] = []
    stability_names = set(stability_classes.keys())
    for key, spec in selectors.items():
        node = f"selectors.{key}"
        if not isinstance(spec, dict):
            out.append(
                Finding(
                    "ONT_SELECTOR_FIELD_MISSING",
                    at(node),
                    "the selector is not a mapping, so it declares nothing a manifest or "
                    "an event can be checked against",
                    "write it as a mapping declaring " + ", ".join(SELECTOR_REQUIRED),
                )
            )
            continue
        missing = [name for name in SELECTOR_REQUIRED if spec.get(name) is None]
        if missing:
            out.append(
                Finding(
                    "ONT_SELECTOR_FIELD_MISSING",
                    at(node),
                    f"the selector omits {', '.join(missing)}. A datum with no declared "
                    "class is the datum-unlabeled plausible value D2 exists to remove",
                    "declare " + ", ".join(missing) + " on this selector",
                )
            )
        for field, allowed, label in (
            ("datum_class", datum_classes, "datum_classes"),
            ("stability", stability_names, "stability_classes"),
            ("provenance_state", provenance_states, "provenance_states"),
            ("fp_mode_basis", fp_bases, "fp_mode_bases"),
        ):
            value = spec.get(field)
            if value is not None and value not in allowed:
                out.append(
                    Finding(
                        "ONT_CLASS_UNDECLARED",
                        at(f"{node}.{field}"),
                        f"{field} is a value the {label} block does not declare, so a "
                        "closed vocabulary has an unchecked member",
                        f"use one of {', '.join(sorted(allowed))}, or declare the new "
                        f"value under {label} in the same change",
                    )
                )
        if spec.get("fp_mode") and not spec.get("fp_mode_basis"):
            out.append(
                Finding(
                    "ONT_FP_BASIS_MISSING",
                    at(f"{node}.fp_mode"),
                    "a false-positive mode is stated with no basis, so a reader cannot "
                    "tell a measured figure from an argument",
                    "add fp_mode_basis: measured, reported or reasoned. CLAUDE.md design gate 3",
                )
            )
    return out


def check_constraints(selectors) -> list[Finding]:
    """O-03. Step 6's done-condition, in the words docs/THE-GAMEPLAN.md uses."""
    out: list[Finding] = []
    for key, spec in selectors.items():
        if not isinstance(spec, dict) or spec.get("datum_class") != "constraint":
            continue
        faults = []
        if spec.get("may_anchor_entity") is not False:
            faults.append("may_anchor_entity is not false")
        for field in CONSTRAINT_REQUIRED:
            if not spec.get(field):
                faults.append(f"{field} is absent")
        if faults:
            out.append(
                Finding(
                    "ONT_CONSTRAINT_INCOMPLETE",
                    at(f"selectors.{key}"),
                    "a constraint selector constrains a space and names no value in it, and "
                    "here " + "; ".join(faults) + ". Step 6's done-condition requires "
                    "may_anchor_entity false, a matcher, and constraint_semantics on every one",
                    "set may_anchor_entity: false, name a matcher declared under "
                    "matchers.library, and state constraint_semantics",
                )
            )
    return out


def check_generated(selectors) -> list[Finding]:
    """O-06."""
    out: list[Finding] = []
    for key, spec in selectors.items():
        if not isinstance(spec, dict) or spec.get("datum_class") != "generated":
            continue
        missing = [name for name in GENERATED_REQUIRED if not spec.get(name)]
        if spec.get("provenance_state") != "GENERATED" and "provenance_state" not in missing:
            missing.append("provenance_state GENERATED")
        if missing:
            out.append(
                Finding(
                    "ONT_GENERATED_INCOMPLETE",
                    at(f"selectors.{key}"),
                    f"a generated selector omits {', '.join(missing)}. circularity_class is "
                    "the field the merge circularity check reads, so dropping it unblocks a "
                    "self-confirming merge without any diff that looks like one",
                    "declare provenance_state: GENERATED, requires_validation_by and "
                    "circularity_class",
                )
            )
    return out


def check_anchors(selectors, entities, stability_classes) -> list[Finding]:
    """O-04 and O-05.

    Neither side of this is a list this tool invents. The anchor-eligible set is
    read from the selectors, the declared anchors are read from the entity
    types, and the rule is that they agree and that each anchor is a selector
    whose stability class permits anchoring. That last clause is
    docs/PLAINSIGHT-design.md section 2.2's actual argument rather than a
    restatement of its conclusion.
    """
    out: list[Finding] = []
    flagged = {k for k, v in selectors.items() if isinstance(v, dict) and v.get("may_anchor_entity") is True}
    declared = {
        e.get("anchored_on")
        for e in entities.values()
        if isinstance(e, dict) and e.get("anchored_on")
    }
    if flagged != declared:
        only_flagged = sorted(flagged - declared)
        only_declared = sorted(declared - flagged)
        detail = (
            "the anchor-eligible selectors and the anchors the entity types declare "
            "disagree. Anchor eligibility granted in one place alone is an anchor no "
            "entity uses or an entity anchored on a selector that refuses it"
        )
        if only_flagged:
            detail += f". Flagged and unused: {', '.join(only_flagged)}"
        if only_declared:
            detail += f". Declared by an entity and not flagged: {', '.join(only_declared)}"
        out.append(
            Finding(
                "ONT_ANCHOR_SET_MISMATCH",
                at("selectors.may_anchor_entity"),
                detail,
                "either set may_anchor_entity on the selector an entity anchors on, or "
                "stop anchoring that entity on it",
            )
        )
    for entity, spec in entities.items():
        if not isinstance(spec, dict):
            continue
        anchor = spec.get("anchored_on")
        if not anchor:
            continue
        sel = selectors.get(anchor)
        if not isinstance(sel, dict):
            continue  # O-11 reports the unregistered anchor
        stab = sel.get("stability")
        rule = stability_classes.get(stab) or {}
        if rule.get("may_anchor") is not True:
            out.append(
                Finding(
                    "ONT_ANCHOR_NOT_STABLE",
                    at(f"entities.{entity}.anchored_on"),
                    f"{entity} is anchored on {anchor}, whose stability is {stab!r} and "
                    "which the stability_classes block does not permit as an anchor. A "
                    "reassignable anchor renders a handle-owner change as ordinary drift "
                    "when it is an identity catastrophe",
                    "anchor the entity on a stable identifier, or ratify a change to the "
                    "stability class in doctrine/DOCTRINE_STATUS.md first. Fixture 3, "
                    "account-anchored-on-handle, is the corpus half of this rule",
                )
            )
    return out


def check_entities(selectors, entities) -> list[Finding]:
    """O-11."""
    out: list[Finding] = []
    declared = set(entities.keys())
    expected = set(ENTITY_TYPES)
    if declared != expected:
        extra = sorted(declared - expected)
        missing = sorted(expected - declared)
        detail = "the entity set is not the closed set"
        if extra:
            detail += f". Undeclared elsewhere: {', '.join(extra)}"
        if missing:
            detail += f". Absent: {', '.join(missing)}"
        out.append(
            Finding(
                "ONT_ENTITY_SET_MISMATCH",
                at("entities"),
                detail + ". spec/layer-model.yaml's ADJUDICATE_EVENT entity_type enum "
                "carries the same seven, and a set that differs makes a promotion legal "
                "in one file and refused in the other",
                "restore the seven, or change both files and the schema in one ratified change",
            )
        )
    for entity, spec in entities.items():
        node = f"entities.{entity}"
        if not isinstance(spec, dict):
            spec = {}
        anchor = spec.get("anchored_on")
        act = spec.get("materialized_by")
        if anchor and anchor not in selectors:
            out.append(
                Finding(
                    "ONT_ENTITY_ANCHOR_UNREGISTERED",
                    at(f"{node}.anchored_on"),
                    f"the entity is anchored on {anchor!r}, which is not a key under "
                    "selectors, so the anchor refers to a type the vocabulary does not carry",
                    "anchor on a registered selector, or add the selector in the same change",
                )
            )
        if not act:
            out.append(
                Finding(
                    "ONT_ENTITY_UNMATERIALIZED",
                    at(node),
                    "the entity declares no materialization act. An entity nothing can "
                    "create is a table with no writer, and an entity anything can create "
                    "mints identities nothing observed",
                    "declare materialized_by: " + " or ".join(MATERIALIZATION_ACTS),
                )
            )
        elif act not in MATERIALIZATION_ACTS:
            out.append(
                Finding(
                    "ONT_ENTITY_UNMATERIALIZED",
                    at(f"{node}.materialized_by"),
                    f"materialized_by is {act!r}, which is outside the closed set, so the "
                    "act that creates this entity is not one any mechanism can check",
                    "use " + " or ".join(MATERIALIZATION_ACTS),
                )
            )
    return out


def check_relations(selectors, prohibitions) -> list[Finding]:
    """O-07 and O-13."""
    out: list[Finding] = []
    known = set(selectors.keys())
    for key, spec in selectors.items():
        if not isinstance(spec, dict):
            continue
        target = spec.get("resolves_to")
        if target and target not in known:
            out.append(
                Finding(
                    "ONT_RELATION_DANGLING",
                    at(f"selectors.{key}.resolves_to"),
                    f"resolves_to names {target!r}, which is not a registered selector, so "
                    "the relation points at a type nothing can carry",
                    "name a registered selector, or add it in the same change",
                )
            )
    covered = set()
    for i, entry in enumerate(prohibitions):
        if not isinstance(entry, dict):
            continue
        node = f"prohibitions.{i}"
        subject = entry.get("selector")
        covered.add(subject)
        for field in ("selector", "must_not_render_as", "must_not_satisfy_citation_for"):
            name = entry.get(field)
            if name and name not in known:
                out.append(
                    Finding(
                        "ONT_RELATION_DANGLING",
                        at(f"{node}.{field}"),
                        f"{field} names {name!r}, which is not a registered selector, so the "
                        "prohibition guards nothing",
                        "name a registered selector on both sides of the prohibition",
                    )
                )
    for key, spec in selectors.items():
        if not isinstance(spec, dict) or not spec.get("resolves_to"):
            continue
        if key not in covered:
            out.append(
                Finding(
                    "ONT_RESOLVES_TO_UNPROHIBITED",
                    at(f"selectors.{key}"),
                    "the selector declares resolves_to and no prohibition covers it. "
                    "resolves_to is what invites a renderer or a citation to follow the "
                    "relation and print the value on the far end, which is the D2 failure "
                    "in one hop",
                    "add a prohibitions entry naming must_not_satisfy_citation_for and the "
                    "violation code that refuses it",
                )
            )
    return out


def check_matchers(selectors, library) -> list[Finding]:
    """O-08 and O-09."""
    out: list[Finding] = []
    referenced: set[str] = set()
    for key, spec in selectors.items():
        if not isinstance(spec, dict):
            continue
        name = spec.get("matcher")
        if not name:
            out.append(
                Finding(
                    "ONT_MATCHER_MISSING",
                    at(f"selectors.{key}"),
                    "the selector declares no matcher, so its value cannot be refused at "
                    "argv construction. SS-19 makes interpolation a refusal point rather "
                    "than an escaping point, because escaping can be got wrong once and a "
                    "refusal cannot",
                    "name a matcher declared under matchers.library",
                )
            )
            continue
        referenced.add(name)
        if name not in library:
            out.append(
                Finding(
                    "ONT_MATCHER_UNDECLARED",
                    at(f"selectors.{key}.matcher"),
                    f"the selector names matcher {name!r}, which the matchers block does not "
                    "declare, so argv construction would resolve it to nothing",
                    "declare the matcher under matchers.library with a purpose and a note, "
                    "or point the selector at one that exists",
                )
            )
    for name in library:
        if name not in referenced:
            out.append(
                Finding(
                    "ONT_MATCHER_UNREFERENCED",
                    at(f"matchers.library.{name}"),
                    "the matcher is declared and no selector references it. A dead matcher "
                    "is a library nobody calls and a calibration nobody will run",
                    "reference it from a selector, or remove it",
                )
            )
    return out


def check_codes(reg, text, codes) -> list[Finding]:
    """O-10."""
    out: list[Finding] = []
    named: set[str] = set()
    for value in _walk(reg, "code"):
        if isinstance(value, str):
            named.add(value)
    named |= set(CODE_IN_TEXT_RE.findall(text))
    for name in sorted(named):
        if name not in codes:
            out.append(
                Finding(
                    "ONT_CODE_UNDECLARED",
                    at(f"code.{name}"),
                    f"the registry names {name}, which spec/layer-model.yaml does not "
                    "declare. Two vocabularies agree until the day one of them changes, "
                    "so this one is read from that file rather than copied",
                    "use a code the layer model declares, or declare the new code there "
                    "first with a severity, a since and what fires it",
                )
            )
    return out


def check_no_values(selectors, reg, text) -> list[Finding]:
    """O-12. AGENTS.md section 4, as a mechanism rather than a habit."""
    out: list[Finding] = []
    for key, spec in selectors.items():
        if not isinstance(spec, dict):
            continue
        form = spec.get("form")
        if not isinstance(form, str):
            continue
        node = f"selectors.{key}.form"
        prefix = f"{key}:"
        if not form.startswith(prefix):
            out.append(
                Finding(
                    "ONT_FORM_PREFIX",
                    at(node),
                    f"the form does not open with {prefix!r}, so a selector string cannot be "
                    "read back to its type without a lookup table",
                    f"write the form as {prefix}<placeholder>",
                )
            )
            continue
        remainder = form[len(prefix):]
        if not TEMPLATE_RE.match(remainder):
            out.append(
                Finding(
                    "ONT_VALUE_IN_FILE",
                    at(node),
                    "the form carries something that is not a <placeholder> or a separator. "
                    "A form is a shape and a shape is legal here; a worked example carrying "
                    "a real-looking handle, address or number is a value and is not",
                    "replace every variable part with a structural placeholder such as "
                    "<platform>/<opaque_id>",
                )
            )
    for group in ("example", "examples"):
        for value in _walk(reg, group):
            for item in _as_list(value):
                if not isinstance(item, str):
                    continue
                body = item.split(":", 1)[1] if ":" in item else item
                if not TEMPLATE_RE.match(body):
                    out.append(
                        Finding(
                            "ONT_VALUE_IN_FILE",
                            at(f"selectors.{group}"),
                            "an example carries something that is not a placeholder. An "
                            "example is where a value gets pasted in, which is why the scan "
                            "covers it",
                            "write the example in placeholder form, or delete it",
                        )
                    )
    for label, pattern in VALUE_SHAPES:
        match = pattern.search(text)
        if match:
            line = text[: match.start()].count("\n") + 1
            out.append(
                Finding(
                    "ONT_VALUE_IN_FILE",
                    f"{REL}:{line}",
                    f"the file carries {label}. AGENTS.md section 4 keeps a selector value, "
                    "handle, email, phone number or case subject name out of every tracked "
                    "file, and git is the one store a crypto-shred cannot reach",
                    "replace it with a structural placeholder. The refusal deliberately does "
                    "not quote what matched, per RETENTION.md RT-19",
                )
            )
    return out


def check_repo_scan(selectors, scan) -> list[Finding]:
    """O-14. RT-15's scan is implementable only against a complete list."""
    out: list[Finding] = []
    if not scan:
        return [
            Finding(
                "ONT_REPO_SCAN_INCOMPLETE",
                at("repo_scan"),
                "there is no repo_scan block, so RT-15's pre-commit scan has no list of "
                "what to look for and D-001 stays unimplementable",
                "declare repo_scan with shape_detectable, partially_detectable and "
                "not_shape_detectable covering every selector",
            )
        ]
    buckets = ("shape_detectable", "partially_detectable", "not_shape_detectable")
    listed: list[str] = []
    for bucket in buckets:
        for name in _as_list(scan.get(bucket)):
            listed.append(name)
            if name not in selectors:
                out.append(
                    Finding(
                        "ONT_REPO_SCAN_UNREGISTERED",
                        at(f"repo_scan.{bucket}"),
                        f"the scan lists {name!r}, which is not a registered selector, so the "
                        "scan would look for a type nothing can emit",
                        "name a registered selector, or remove the entry",
                    )
                )
    seen = set(listed)
    if len(listed) != len(seen):
        out.append(
            Finding(
                "ONT_REPO_SCAN_INCOMPLETE",
                at("repo_scan"),
                "a selector appears in more than one detectability bucket, so the scan's "
                "claim about what it can find is two different claims",
                "put each selector in exactly one of " + ", ".join(buckets),
            )
        )
    missing = sorted(set(selectors) - seen)
    if missing:
        out.append(
            Finding(
                "ONT_REPO_SCAN_INCOMPLETE",
                at("repo_scan"),
                f"the scan says nothing about {', '.join(missing)}. A selector in no bucket "
                "is one RT-15's scan silently ignores, which is the failure direction where "
                "the gate looks green",
                "add each to shape_detectable, partially_detectable or not_shape_detectable, "
                "and say plainly when the honest answer is that a regex cannot find it",
            )
        )
    for i, entry in enumerate(_as_list(scan.get("document_exemptions"))):
        if not isinstance(entry, dict):
            continue
        path = entry.get("path")
        if path and not (ROOT / path).is_file():
            out.append(
                Finding(
                    "ONT_REPO_SCAN_EXEMPTION_MISSING",
                    at(f"repo_scan.document_exemptions.{i}"),
                    f"the exemption names {path}, which is not in the tree. A stale exemption "
                    "is a hole nobody is watching",
                    "remove the exemption, or correct the path",
                )
            )
        for name in _as_list(entry.get("selector_types")):
            if name not in selectors:
                out.append(
                    Finding(
                        "ONT_REPO_SCAN_UNREGISTERED",
                        at(f"repo_scan.document_exemptions.{i}.selector_types"),
                        f"the exemption covers {name!r}, which is not a registered selector",
                        "name a registered selector, or remove the entry",
                    )
                )
    return out


def check_claims(meta, matchers) -> list[Finding]:
    """O-15. The two claims this file must not make untruthfully."""
    out: list[Finding] = []
    if meta.get("closed") is not True:
        out.append(
            Finding(
                "ONT_CLOSURE_CLAIM",
                at("ontology.closed"),
                "the registry no longer declares itself closed. D2's whole content is that a "
                "connector emitting an unregistered type is refused, and an open registry "
                "refuses nothing",
                "set closed: true, or take D2 back to the operator",
            )
        )
    calibrated = matchers.get("calibrated")
    ref = matchers.get("calibration_ref")
    if calibrated is True and ref and not (ROOT / str(ref)).is_file():
        out.append(
            Finding(
                "ONT_CALIBRATION_CLAIM",
                at("matchers.calibrated"),
                f"the block claims calibration and {ref} does not exist, so the claim rests "
                "on nothing a reader can open",
                "set calibrated: false until the calibration policy and its truth corpus "
                "exist. THE-GAMEPLAN section 2.2 defers both until before the first matcher merges",
            )
        )
    if matchers.get("identity_basis_permitted") is True and calibrated is not True:
        out.append(
            Finding(
                "ONT_CALIBRATION_CLAIM",
                at("matchers.identity_basis_permitted"),
                "an unscored matcher is permitted as an identity basis. A matcher nobody has "
                "scored produces a link with no measured error rate, and the analyst reads it "
                "as a link",
                "set identity_basis_permitted: false while calibrated is false",
            )
        )
    return out


def check_proposed(meta, selectors) -> list[Finding]:
    """O-17. The operator ratifies additions, so the two lists agree."""
    out: list[Finding] = []
    listed = set(_as_list(meta.get("proposed")))
    marked = {
        key
        for key, spec in selectors.items()
        if isinstance(spec, dict) and str(spec.get("note", "")).strip().startswith("PROPOSED")
    }
    for name in sorted(listed - marked):
        if name not in selectors:
            out.append(
                Finding(
                    "ONT_PROPOSED_MISMATCH",
                    at("ontology.proposed"),
                    f"{name} is listed as proposed and is not a selector in this file",
                    "add the selector, or remove it from the proposed list",
                )
            )
        else:
            out.append(
                Finding(
                    "ONT_PROPOSED_MISMATCH",
                    at(f"selectors.{name}.note"),
                    f"{name} is listed as proposed and its note does not say so, so a reader "
                    "of the entry cannot tell a ratified inheritance from an agent's proposal",
                    "open the note with PROPOSED, or remove the entry from ontology.proposed",
                )
            )
    for name in sorted(marked - listed):
        out.append(
            Finding(
                "ONT_PROPOSED_MISMATCH",
                at(f"selectors.{name}"),
                f"{name} is marked PROPOSED and is absent from ontology.proposed, which is "
                "the list the operator reads when ratifying additions",
                "add it to ontology.proposed, or drop the marking",
            )
        )
    return out


# ---------------------------------------------------------------------------
# --corpus
# ---------------------------------------------------------------------------


class Unreadable(Exception):
    """A governed input a mode needs could not be read. Exit 2."""

    def __init__(self, code: str, where: str, what: str, moves: str):
        super().__init__(what)
        self.finding = Finding(code, where, what, moves)


def load_layer_model() -> dict:
    model = yaml.safe_load(LAYER_MODEL.read_text(encoding="utf-8"))
    if not isinstance(model, dict):
        raise ValueError("the layer model did not parse to a mapping")
    return model


def registry_sites(model: dict) -> list[tuple[str, tuple, bool]]:
    """Every field the layer model binds to this registry, per event type.

    Each entry is (event type, path from the event root, whether the field's
    own mapping also declares `value`). A path segment `[]` steps into every
    item of an array. Nothing here names a field: the sites are what the layer
    model says they are, so a new registry-bound field is read on the next run.
    """
    out: list[tuple[str, tuple, bool]] = []

    def collect(event_type: str, fields, prefix: tuple) -> None:
        if not isinstance(fields, dict):
            return
        for name, spec in fields.items():
            if not isinstance(spec, dict):
                continue
            path = prefix + (str(name),)
            if spec.get("registry") == REL:
                out.append((event_type, path, "value" in fields))
            collect(event_type, spec.get("fields"), path)
            items = spec.get("items")
            if isinstance(items, dict):
                collect(event_type, items.get("fields"), path + ("[]",))

    for event_type, spec in (model.get("event_types") or {}).items():
        if isinstance(spec, dict) and isinstance(spec.get("payload"), dict):
            collect(str(event_type), spec["payload"].get("fields"), ("payload",))
    return out


def site_label(site: tuple[str, tuple, bool]) -> str:
    event_type, path, has_value = site
    text = ".".join(path).replace(".[]", "[]")
    return f"{event_type} {text}" + (" with its value" if has_value else "")


def require_sites(sites: list) -> list:
    """The registry-bound sites, refused when the layer model binds none."""
    if not sites:
        raise Unreadable(
            "ONT_CORPUS_SITES_UNREADABLE",
            "spec/layer-model.yaml",
            f"the layer model binds no field to {REL}, so --corpus would read no site "
            "and check nothing while exiting 0",
            f"restore the registry: {REL} annotation on the fields that carry a selector "
            "type and run python tools/validate_layer_model.py; or, if the binding moved "
            "on purpose, annotate the fields that now carry selector types",
        )
    return sites


def parse_corpus(text: str, rel: str) -> list[tuple[int, dict]]:
    """One corpus as (line number, row). Unreadable on any row that cannot be read."""
    rows: list[tuple[int, dict]] = []
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise Unreadable(
                "ONT_CORPUS_UNREADABLE",
                f"{rel}:{number}",
                f"the line is not JSON ({exc.msg}), so the row cannot be read and a "
                "row skipped silently is a row checked by nothing",
                "regenerate the corpus with python tools/build_corpus.py, or fix the line",
            )
        if not isinstance(row, dict) or not isinstance(row.get("event"), dict):
            raise Unreadable(
                "ONT_CORPUS_UNREADABLE",
                f"{rel}:{number}",
                "the row is not a mapping carrying an event, so there is nothing to "
                "read a selector from",
                "regenerate the corpus with python tools/build_corpus.py, or fix the row",
            )
        rows.append((number, row))
    return rows


def load_corpora(corpora=CORPORA) -> dict[str, list[tuple[int, dict]]]:
    """Both corpora as (line number, row). Exit 2 on anything unreadable."""
    out: dict[str, list[tuple[int, dict]]] = {}
    for label, path, rel in corpora:
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            raise Unreadable(
                "ONT_CORPUS_UNREADABLE",
                rel,
                "the corpus does not exist, so --corpus has nothing to read and checks nothing",
                "run python tools/build_corpus.py to regenerate both corpora, or restore the "
                "file from git; the ontology-corpus entry keeps failing until a corpus is read",
            )
        out[label] = parse_corpus(text, rel)
    return out


def _parents(node, path: tuple, trail: tuple):
    """Every mapping at `path` under `node`, with the dotted trail to it."""
    if not path:
        if isinstance(node, dict):
            yield trail, node
        return
    head, rest = path[0], path[1:]
    if head == "[]":
        if isinstance(node, list):
            for i, item in enumerate(node):
                yield from _parents(item, rest, trail + (str(i),))
    elif isinstance(node, dict) and head in node:
        yield from _parents(node[head], rest, trail + (head,))


_ABSENT = object()


def occurrences(event: dict, sites: list[tuple[str, tuple, bool]]):
    """(dotted path, selector type, value or _ABSENT) at every site the event's type has."""
    event_type = (event.get("event") or {}).get("event_type") if isinstance(event.get("event"), dict) else None
    for site_type, path, has_value in sites:
        if site_type != event_type:
            continue
        for trail, parent in _parents(event, path[:-1], ()):
            field = path[-1]
            if field not in parent or parent[field] is None:
                continue
            value = parent.get("value", _ABSENT) if has_value else _ABSENT
            yield ".".join(trail + (field,)), parent[field], value


def form_misfit(key: str, form: str, value, keys) -> tuple[str, bool]:
    """Why `value` does not fit `form`, or "" when it fits. The flag says the value
    was one whole-value placeholder, which fits by reading O-R1.

    The reason never quotes the value. RETENTION.md RT-15 keeps a selector value
    out of every tracked file, and a refusal is the text that gets pasted into a
    worklog entry, a handoff or an issue, so it names the row and the field and
    never the value.
    """
    if value is None:
        return "", False
    if not isinstance(value, str):
        return (
            f"the value is a {type(value).__name__}, and a selector value is a string in "
            "its key's form",
            False,
        )
    body = value
    head, colon, tail = value.partition(":")
    if colon and head in keys:
        if head != key:
            return (
                f"the value is written typed as {head} while the selector_type beside it is "
                f"{key}, so the value says it is a different selector (reading O-R2)",
                False,
            )
        body = tail
    if VALUE_PLACEHOLDER_RE.match(body):
        return "", True
    remainder = form[len(key) + 1:] if form.startswith(f"{key}:") else form
    parts = FORM_SLOT_RE.split(remainder)
    pattern = "".join(re.escape(p) if i % 2 == 0 else "(.*?)" for i, p in enumerate(parts))
    match = re.fullmatch(pattern, body, re.S)
    if not match:
        return (
            f"the value does not have the shape of the form {form}: its separators are "
            "not the form's, so the slots cannot be read",
            False,
        )
    for name, text in zip(parts[1::2], match.groups()):
        if text == "":
            return f"the <{name}> slot of the form {form} is empty", False
        if VALUE_PLACEHOLDER_RE.match(text):
            continue
        if name == PLATFORM_SLOT and not PLATFORM_TOKEN_RE.match(text):
            return (
                f"the form {form} is platform-bound and the <platform> slot does not hold a "
                "platform token of the shape ^[a-z][a-z0-9_]*$",
                False,
            )
    return "", False


def _event_findings(event: dict, sites, selectors: dict, file_where: str, prefix: str, row_name: str, stats: dict):
    """O-C1 and O-C2 for one event: the findings, plus the registered keys seen.

    `prefix` is the dotted path from the row to the event, empty for a row's own
    event, so every location is one path plus one dotted node, which is the
    shape tools/gate_log.py accepts.
    """
    out: list[Finding] = []
    seen: set[str] = set()
    keys = set(selectors)
    for path, key, value in occurrences(event, sites):
        stats["occurrences"] += 1
        path = prefix + path
        where = f"{file_where} :: {path}"
        if not isinstance(key, str) or key not in selectors:
            # A type is named only when it has a key's shape, so a value pasted
            # into a type field is never repeated into a terminal or a CI log.
            named = f"the selector type {key}" if isinstance(key, str) and PLATFORM_TOKEN_RE.match(key) else "a selector type"
            out.append(
                Finding(
                    "ONT_CORPUS_SELECTOR_UNREGISTERED",
                    where,
                    f"row {row_name} carries {named} at {path}, which is not a key in "
                    f"{REL}, so the event names a type the closed vocabulary does not carry",
                    "use a registered key; or propose the type as a registry addition under "
                    "ontology.proposed with a form, a datum_class and a matcher; or, if the row "
                    "is meant to fail, move it to must-fail.jsonl expecting SELECTOR_TYPE_UNREGISTERED",
                    rule="O-C1, docs/PLAINSIGHT-FOUNDATION.md D2. Rung 2's generated selector enum "
                    "refuses the same type first",
                )
            )
            continue
        seen.add(key)
        if value is _ABSENT:
            continue
        spec = selectors.get(key) or {}
        form = spec.get("form") if isinstance(spec, dict) else None
        if not isinstance(form, str):
            continue  # O-01 refuses a selector with no form in the registry mode
        stats["values"] += 1
        reason, opaque = form_misfit(key, form, value, keys)
        if opaque:
            stats["opaque"] += 1
        if value is None:
            stats["null"] += 1
        if reason:
            out.append(
                Finding(
                    "ONT_CORPUS_VALUE_OFF_FORM",
                    where.rsplit(".", 1)[0] + ".value",
                    f"row {row_name} carries a {key} value that does not fit its form: {reason}. "
                    "This refusal does not quote the value, because RETENTION.md RT-15 keeps a "
                    "selector value out of every tracked file and a refusal is the text that "
                    "gets pasted into one",
                    f"write the value as one <placeholder>, or in the form {form} with every "
                    "variable part a <placeholder> and any platform token in lowercase; or change "
                    "the selector_type to the key whose form the value has",
                    rule=f"O-C2, the form {REL} declares for {key}",
                )
            )
    return out, seen


def check_corpus(reg: dict, sites, corpora: dict) -> tuple[list[Finding], dict]:
    """O-C1 to O-C4 over both corpora. Returns the findings and the counts the
    output reports, so a clean run says what it read rather than only that it passed."""
    findings: list[Finding] = []
    selectors = reg.get("selectors") or {}
    version = (reg.get("ontology") or {}).get("version")
    words = UNEXERCISED_WORDS.format(version=version)
    stats = {
        "pass_rows": len(corpora.get("must-pass", [])),
        "fail_rows": len(corpora.get("must-fail", [])),
        "context_events": 0,
        "occurrences": 0,
        "values": 0,
        "opaque": 0,
        "null": 0,
        "owned_rows": 0,
        "words": words,
    }
    exercised: dict[str, str] = {}
    pass_rel = CORPORA[0][2]
    fail_rel = CORPORA[1][2]

    for number, row in corpora.get("must-pass", []):
        name = str(row.get("name") or f"line {number}")
        found, seen = _event_findings(row["event"], sites, selectors, f"{pass_rel}:{number}", "event.", name, stats)
        findings += found
        for key in seen:
            exercised.setdefault(key, name)

    for number, row in corpora.get("must-fail", []):
        name = str(row.get("name") or f"line {number}")
        base = f"{fail_rel}:{number}"
        for index, context in enumerate(_as_list(row.get("context"))):
            if not isinstance(context, dict):
                continue
            stats["context_events"] += 1
            found, _ = _event_findings(
                context, sites, selectors, base, f"context.{index}.", f"{name}, context event {index},", stats
            )
            findings += found
        found, _ = _event_findings(row["event"], sites, selectors, base, "event.", name, stats)
        fired = {f.code for f in found}
        expected = str(row.get("expect_code") or "")
        if expected in CORPUS_OWNED_CODES:
            stats["owned_rows"] += 1
            want = CORPUS_OWNED_CODES[expected]
            if want not in fired:
                findings.append(
                    Finding(
                        "ONT_CORPUS_FIXTURE_VACUOUS",
                        base,
                        f"must-fail row {name} expects {expected}, which this mode refuses as "
                        f"{want}, and this mode refuses nothing on the row's event. A fixture "
                        "that passes the check it claims to break proves nothing about it",
                        "break the row the way its expected code describes, such as a "
                        "selector_type that is not a registry key; or change expect_code to the "
                        "code the row does break",
                        rule="O-C3, the vacuity guard. CLAUDE.md design gate 1",
                    )
                )
            extra = sorted(fired - {want})
            if extra:
                findings.append(
                    Finding(
                        "ONT_CORPUS_FIXTURE_VACUOUS",
                        base,
                        f"must-fail row {name} expects {expected} and this mode also refuses its "
                        f"event as {', '.join(extra)}, so the row breaks more than the rule it names",
                        "remove the second defect from the row so it is refused for its expected "
                        "code alone",
                        rule="O-C3, the vacuity guard",
                    )
                )
        elif fired and row.get("expect_only") is True:
            findings.append(
                Finding(
                    "ONT_CORPUS_FIXTURE_VACUOUS",
                    base,
                    f"must-fail row {name} expects only {expected or 'its code'} and this mode "
                    f"refuses its event as {', '.join(sorted(fired))} too, so the row breaks a "
                    "selector rule it does not name and its refusal cannot be read as one rule",
                    "make the row's selectors legal, a registered key and a value in its form or "
                    "one <placeholder>, so the row is refused for its expected code alone",
                    rule="O-C3, the vacuity guard read from the other side (reading O-R3)",
                )
            )

    declared: list[str] = []
    for key, spec in selectors.items():
        note = str((spec or {}).get("note", "")) if isinstance(spec, dict) else ""
        says = words.lower() in note.lower()
        if says:
            declared.append(key)
        if key not in exercised and not says:
            findings.append(
                Finding(
                    "ONT_CORPUS_KEY_UNEXERCISED",
                    at(f"selectors.{key}.note"),
                    f"no must-pass row carries {key} at any site and its note does not say it "
                    f"is {words}, so the key can be added and never proven",
                    f"add a must-pass row that carries {key} through python "
                    f"tools/build_corpus.py; or add the words '{words}' to the key's note, which "
                    "is a statement the maintainer reads",
                    rule="O-C4, CLAUDE.md design gate 3",
                )
            )
        elif key in exercised and says:
            findings.append(
                Finding(
                    "ONT_CORPUS_KEY_UNEXERCISED",
                    at(f"selectors.{key}.note"),
                    f"the note says {key} is {words} and must-pass row {exercised[key]} "
                    "exercises it, so the note states something the corpus contradicts",
                    f"remove the words '{words}' from the note",
                    rule="O-C4, read from the other side",
                )
            )
    stats["exercised"] = sorted(k for k in exercised if k in selectors)
    stats["declared"] = sorted(declared)
    return findings, stats


def corpus_report(stats: dict, sites, reg: dict) -> str:
    prohibited = sorted({str(p.get("code")) for p in _as_list(reg.get("prohibitions")) if isinstance(p, dict) and p.get("code")})
    lines = [
        f"validate_ontology --corpus ok: {stats['pass_rows'] + stats['fail_rows']} rows read "
        f"({stats['pass_rows']} must-pass, {stats['fail_rows']} must-fail carrying "
        f"{stats['context_events']} context events).",
        f"  sites read from spec/layer-model.yaml ({len(sites)}): " + "; ".join(site_label(s) for s in sites),
        f"  selector occurrences: {stats['occurrences']}, every one a registry key except on a "
        "must-fail row that expects " + " or ".join(sorted(CORPUS_OWNED_CODES)) + ".",
        f"  values held to their form: {stats['values']}. {stats['opaque']} of them are one "
        "whole-value placeholder, which fits any form and carries no platform token to "
        "check (reading O-R1), and " + str(stats['null']) + " are null.",
        f"  keys: {len(stats['exercised'])} exercised by a must-pass row "
        f"({', '.join(stats['exercised'])}); {len(stats['declared'])} declared "
        f"{stats['words']} in their notes.",
        f"  must-fail rows expecting a code this mode refuses: {stats['owned_rows']} "
        f"({', '.join(sorted(CORPUS_OWNED_CODES))}), each refused for that code alone.",
        "  not checked here: a filled value, which tools/validate_retention.py --repo-scan "
        "refuses; a filled slot other than <platform>; and the registry-driven codes "
        f"SELECTOR_ANCHOR_PROHIBITED, {', '.join(prohibited)}, which rung 2 refuses. The rows "
        "are the repository's corpora and no connector's output, so this is no rung 3 claim "
        "for any connector (reading O-R5).",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# --matchers
# ---------------------------------------------------------------------------


def connector_sources() -> list[tuple[str, str]]:
    """(repository path, text) for each connector file O-M2 reads."""
    out: list[tuple[str, str]] = []
    if not CONNECTORS.is_dir():
        return out
    for folder in sorted(p for p in CONNECTORS.iterdir() if p.is_dir() and not p.name.startswith(("_", "."))):
        for name in CONNECTOR_FILES:
            path = folder / name
            if path.is_file():
                out.append((path.relative_to(ROOT).as_posix(), path.read_text(encoding="utf-8")))
    return out


def _stands_in(text: str, line: int) -> tuple[str, list[str]]:
    """The innermost function around `line` in a Python source, and the reading ids
    its docstring names. Empty when the line is outside every function or the
    source does not parse."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return "", []
    best = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end = getattr(node, "end_lineno", node.lineno)
            if node.lineno <= line <= end and (best is None or node.lineno >= best.lineno):
                best = node
    if best is None:
        return "", []
    doc = ast.get_docstring(best) or ""
    return best.name, sorted(set(READING_ID_RE.findall(doc)))


def check_matchers_mode(reg: dict, sources: list[tuple[str, str]]) -> tuple[list[Finding], dict]:
    """O-08 and O-09 rerun, then O-M1 to O-M3. Structure only: nothing is scored."""
    matchers = reg.get("matchers") or {}
    findings = check_matchers(reg.get("selectors") or {}, matchers.get("library") or {})
    structural, report = matcher_structure(reg, sources)
    return findings + structural, report


def registry_lint(reg: dict, text: str, codes: set[str], sources: list[tuple[str, str]]) -> list[Finding]:
    """What the default mode runs: every registry check, then O-M1 to O-M3.

    The ontology-matchers kernel gate entry is STUB, and the aggregator does not
    read a STUB entry's exit code. Running the structural matcher checks here puts
    their refusals behind the IMPLEMENTED ontology entry and the pre-commit hook
    instead (reading O-R6).
    """
    return check(reg, text, codes) + matcher_structure(reg, sources)[0]


def matcher_structure(reg: dict, sources: list[tuple[str, str]]) -> tuple[list[Finding], dict]:
    """O-M1 to O-M3 alone, with the report --matchers prints."""
    matchers = reg.get("matchers") or {}
    library = matchers.get("library") or {}
    findings: list[Finding] = []

    for name, spec in library.items():
        spec = spec if isinstance(spec, dict) else {}
        faults = []
        if spec.get("purpose") not in MATCHER_PURPOSES:
            faults.append("its purpose is not one of " + " or ".join(MATCHER_PURPOSES))
        if not spec.get("note"):
            faults.append("it carries no note")
        if faults:
            findings.append(
                Finding(
                    "ONT_MATCHER_ENTRY_INCOMPLETE",
                    at(f"matchers.library.{name}"),
                    "the library entry says less than a reader needs: " + "; ".join(faults)
                    + ". An argv shape gate may run uncalibrated and a constraint matcher may "
                    "not, so an entry whose purpose is unreadable is one nobody can place",
                    "set purpose to " + " or ".join(MATCHER_PURPOSES)
                    + " and write a note saying what the matcher accepts; or propose a third "
                    "purpose to the maintainer (reading O-R7)",
                    rule="O-M3",
                )
            )

    ref = matchers.get("calibration_ref")
    ref_exists = bool(ref) and (ROOT / str(ref)).is_file()
    if not ref_exists:
        for flag in ("calibrated", "identity_basis_permitted"):
            if matchers.get(flag) is not False:
                findings.append(
                    Finding(
                        "ONT_MATCHER_CALIBRATION_FLAG",
                        at(f"matchers.{flag}"),
                        f"{flag} is not false while {ref or 'calibration_ref'} does not exist. "
                        "Until a calibration file exists this flag is the only thing that keeps "
                        "an unscored matcher from being an identity basis",
                        f"set {flag}: false; or write the calibration policy and its truth corpus "
                        "first, which docs/THE-GAMEPLAN.md section 2.2 defers to before the first "
                        "matcher merges and which needs the sealed cast",
                        rule="O-M1, the semantics contract's rule that an unscored matcher may not "
                        "be an identity basis",
                    )
                )

    named: list[dict] = []
    for rel, text in sources:
        for number, line in enumerate(text.splitlines(), 1):
            for match in MATCHER_ID_RE.finditer(line):
                mid = match.group(0)
                entry = {"where": f"{rel}:{number}", "id": mid, "in_library": mid in library}
                if mid in library:
                    entry["purpose"] = (library.get(mid) or {}).get("purpose")
                    if rel.endswith(".py"):
                        entry["function"], entry["readings"] = _stands_in(text, number)
                else:
                    findings.append(
                        Finding(
                            "ONT_MATCHER_NAMED_UNDECLARED",
                            f"{rel}:{number}",
                            f"the connector names matcher {mid}, which matchers.library does not "
                            "declare, so SS-19's argv refusal would resolve it to nothing",
                            "name a matcher the library declares; or declare this one under "
                            f"matchers.library in {REL} with a purpose and a note and reference it "
                            "from the selector it gates",
                            rule="O-M2, doctrine/SUBJECT_SELECTION.md SS-19",
                        )
                    )
                named.append(entry)
    report = {
        "library": len(library),
        "ref": ref,
        "ref_exists": ref_exists,
        "named": named,
        "connectors": len({s[0].split("/")[1] for s in sources if s[0].count("/") >= 2}),
    }
    return findings, report


def matchers_report(report: dict) -> str:
    named = report["named"]
    lines = [
        "validate_ontology --matchers: the structural half ran and refused nothing. It scored nothing.",
        f"  checked: {report['library']} library entries, each referenced by a selector and each "
        "selector's matcher declared (O-08, O-09); each with a note and a purpose of "
        + " or ".join(MATCHER_PURPOSES) + " (O-M3); calibrated and identity_basis_permitted "
        f"false while {report['ref']} "
        + ("exists" if report["ref_exists"] else "does not exist")
        + f" (O-M1); {len(named)} matcher id(s) named across {report['connectors']} connector(s), "
        "each in the library (O-M2).",
    ]
    for entry in named:
        line = f"  {entry['where']} names {entry['id']} ({entry.get('purpose')})"
        if entry.get("function"):
            line += f", and {entry['function']} stands in for its grammar there"
            if entry.get("readings"):
                line += f" (reading {', '.join(entry['readings'])})"
        lines.append(line + ".")
    if report["ref_exists"]:
        lines.append(
            f"  {report['ref']} exists and this mode does not read it. The scoring half is owed."
        )
    lines.append(
        "  cannot check: no matcher is scored, no precision or recall is claimed, and the "
        "identity-basis rule is enforced by the flag alone until the cast is sealed and a "
        "calibration file exists."
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# self-test
# ---------------------------------------------------------------------------


def _mutations():
    """Deliberate breaks, one per direction the registry can fail in."""

    def anchor_a_hint(r):
        r["selectors"]["email_hint_recovery_masked"]["may_anchor_entity"] = True

    def drop_a_matcher(r):
        del r["matchers"]["library"]["hints.email.v1"]

    def undeclared_code(r):
        r["prohibitions"][0]["code"] = "NOT_A_DECLARED_CODE"

    def constraint_without_semantics(r):
        del r["selectors"]["phone_hint_recovery_masked"]["constraint_semantics"]

    def account_on_handle(r):
        r["entities"]["Account"]["anchored_on"] = "handle"
        r["selectors"]["handle"]["may_anchor_entity"] = True
        r["selectors"]["platform_uid"]["may_anchor_entity"] = False

    def unmaterialized_entity(r):
        r["entities"]["Account"].pop("materialized_by")

    def selector_without_datum_class(r):
        r["selectors"]["domain"].pop("datum_class")

    def dangling_resolves_to(r):
        r["selectors"]["email_hint_recovery_masked"]["resolves_to"] = "email_address"

    def generated_loses_circularity(r):
        del r["selectors"]["email_generated_permutation"]["circularity_class"]

    def unreferenced_matcher(r):
        r["matchers"]["library"]["shape.orphan.v1"] = {"purpose": "argv_shape_gate", "note": "nothing calls it"}

    def value_in_a_form(r):
        # One filled segment is enough for ONT_VALUE_IN_FILE to fire. The
        # platform segment stays a placeholder so this line never carries a
        # complete typed handle, which RT-15's repo scan refuses in any tracked
        # file, fixtures included.
        r["selectors"]["handle"]["form"] = "handle:<platform>/examplename"

    def prohibition_removed(r):
        r["prohibitions"] = [p for p in r["prohibitions"] if p.get("selector") != "email_generated_permutation"]

    def scan_forgets_a_selector(r):
        r["repo_scan"]["shape_detectable"] = [
            s for s in r["repo_scan"]["shape_detectable"] if s != "domain"
        ]

    def eighth_entity(r):
        r["entities"]["Household"] = {"anchored_on": None, "materialized_by": "analyst_act", "note": "not in the set"}

    def uncalibrated_identity_basis(r):
        r["matchers"]["identity_basis_permitted"] = True

    def unclosed_registry(r):
        r["ontology"]["closed"] = False

    return [
        ("make a hint selector anchorable", anchor_a_hint, "ONT_ANCHOR_SET_MISMATCH"),
        ("drop a matcher a selector names", drop_a_matcher, "ONT_MATCHER_UNDECLARED"),
        ("reference an undeclared violation code", undeclared_code, "ONT_CODE_UNDECLARED"),
        ("give a constraint selector no constraint_semantics", constraint_without_semantics, "ONT_CONSTRAINT_INCOMPLETE"),
        ("anchor an Account on a handle", account_on_handle, "ONT_ANCHOR_NOT_STABLE"),
        ("declare an entity with no materialization act", unmaterialized_entity, "ONT_ENTITY_UNMATERIALIZED"),
        ("add a selector with no datum_class", selector_without_datum_class, "ONT_SELECTOR_FIELD_MISSING"),
        ("make a resolves_to dangle", dangling_resolves_to, "ONT_RELATION_DANGLING"),
        ("drop circularity_class from the generated selector", generated_loses_circularity, "ONT_GENERATED_INCOMPLETE"),
        ("declare a matcher nothing references", unreferenced_matcher, "ONT_MATCHER_UNREFERENCED"),
        ("paste a value-shaped string into a form", value_in_a_form, "ONT_VALUE_IN_FILE"),
        ("remove the prohibition on a resolves_to selector", prohibition_removed, "ONT_RESOLVES_TO_UNPROHIBITED"),
        ("drop a selector from the repo scan's buckets", scan_forgets_a_selector, "ONT_REPO_SCAN_INCOMPLETE"),
        ("add an eighth entity type", eighth_entity, "ONT_ENTITY_SET_MISMATCH"),
        ("permit an unscored matcher as an identity basis", uncalibrated_identity_basis, "ONT_CALIBRATION_CLAIM"),
        ("stop declaring the registry closed", unclosed_registry, "ONT_CLOSURE_CLAIM"),
    ]


def _row(ctx: dict, corpus: str, name: str) -> dict:
    for _, row in ctx["corpora"][corpus]:
        if row.get("name") == name:
            return row
    raise KeyError(f"the self-test plants on {corpus} row {name}, which the corpus no longer carries")


#: A value with none of the form's separators and no brackets. It is no
#: selector of any shape, so this file never carries a filled value.
OFF_FORM = "synthetic_value_with_no_separator"


def _corpus_plants():
    """One break per --corpus code, on in-memory copies of the corpora and the registry.
    Every planted value is a placeholder or a string no selector shape matches."""

    def unregistered_key(c):
        _row(c, "must-pass", "collect-permitted")["event"]["payload"]["target_selector_type"] = "unregistered_type_plant"

    def value_off_form(c):
        _row(c, "must-pass", "extract-claim-handle")["event"]["payload"]["value"] = OFF_FORM

    def platform_slot_empty(c):
        _row(c, "must-pass", "extract-claim-handle")["event"]["payload"]["value"] = "/<synthetic-handle-1>"

    def platform_token_misshapen(c):
        _row(c, "must-pass", "extract-claim-handle")["event"]["payload"]["value"] = "Not-A-Token/<synthetic-handle-1>"

    def typed_as_another_key(c):
        _row(c, "must-pass", "extract-claim-handle")["event"]["payload"]["value"] = "email:<synthetic-handle-1>"

    def owned_code_refused_by_nothing(c):
        _row(c, "must-fail", "extract-carries-confidence")["expect_code"] = "SELECTOR_TYPE_UNREGISTERED"

    def other_code_also_off_form(c):
        _row(c, "must-fail", "extract-carries-confidence")["event"]["payload"]["value"] = OFF_FORM

    def context_off_form(c):
        for _, row in c["corpora"]["must-fail"]:
            for event in _as_list(row.get("context")):
                payload = event.get("payload") if isinstance(event, dict) else None
                if isinstance(payload, dict) and payload.get("selector_type") == "handle":
                    payload["value"] = OFF_FORM
                    return

    def key_with_no_row_and_no_note(c):
        words = UNEXERCISED_WORDS.format(version=c["reg"]["ontology"]["version"])
        spec = c["reg"]["selectors"]["domain"]
        spec["note"] = re.sub(re.escape(words), "", spec["note"], flags=re.I)

    def only_row_of_a_key_removed(c):
        c["corpora"]["must-pass"] = [
            (n, row) for n, row in c["corpora"]["must-pass"] if '"phone"' not in json.dumps(row)
        ]

    def exercised_key_declared_unexercised(c):
        words = UNEXERCISED_WORDS.format(version=c["reg"]["ontology"]["version"])
        c["reg"]["selectors"]["handle"]["note"] += f" Planted, {words}."

    return [
        ("put an unregistered type on a must-pass row", unregistered_key, "ONT_CORPUS_SELECTOR_UNREGISTERED"),
        ("write a must-pass value with none of its form's separators", value_off_form, "ONT_CORPUS_VALUE_OFF_FORM"),
        ("leave a platform-bound value's <platform> slot empty", platform_slot_empty, "ONT_CORPUS_VALUE_OFF_FORM"),
        ("fill a <platform> slot with a misshapen token", platform_token_misshapen, "ONT_CORPUS_VALUE_OFF_FORM"),
        ("type a handle value with another key's prefix", typed_as_another_key, "ONT_CORPUS_VALUE_OFF_FORM"),
        ("claim SELECTOR_TYPE_UNREGISTERED on a row nothing refuses", owned_code_refused_by_nothing, "ONT_CORPUS_FIXTURE_VACUOUS"),
        ("break a must-fail row's form beside its own code", other_code_also_off_form, "ONT_CORPUS_FIXTURE_VACUOUS"),
        ("break a value in a must-fail row's context", context_off_form, "ONT_CORPUS_VALUE_OFF_FORM"),
        ("drop the unexercised words from a key no row carries", key_with_no_row_and_no_note, "ONT_CORPUS_KEY_UNEXERCISED"),
        ("remove the only must-pass rows carrying a key", only_row_of_a_key_removed, "ONT_CORPUS_KEY_UNEXERCISED"),
        ("declare an exercised key unexercised", exercised_key_declared_unexercised, "ONT_CORPUS_KEY_UNEXERCISED"),
    ]


def _matcher_plants():
    """One break per --matchers code, on in-memory copies of the registry and the
    connector sources, plus the reused O-08 check firing inside the mode."""

    def calibrated_without_file(c):
        c["reg"]["matchers"]["calibrated"] = True

    def identity_basis_without_file(c):
        c["reg"]["matchers"]["identity_basis_permitted"] = True

    def connector_names_undeclared(c):
        c["sources"] = c["sources"] + [("connectors/plant/adapter.py", "# gated by shape.undeclared_plant.v1\n")]

    def purpose_outside_set(c):
        c["reg"]["matchers"]["library"]["shape.handle.v1"]["purpose"] = "identity_decision"

    def note_dropped(c):
        c["reg"]["matchers"]["library"]["shape.email.v1"].pop("note")

    def selector_matcher_undeclared(c):
        del c["reg"]["matchers"]["library"]["shape.domain.v1"]

    return [
        ("claim calibration while calibration_ref is absent", calibrated_without_file, "ONT_MATCHER_CALIBRATION_FLAG"),
        ("permit an identity basis while calibration_ref is absent", identity_basis_without_file, "ONT_MATCHER_CALIBRATION_FLAG"),
        ("name an undeclared matcher in a connector", connector_names_undeclared, "ONT_MATCHER_NAMED_UNDECLARED"),
        ("give a library entry a purpose outside the two", purpose_outside_set, "ONT_MATCHER_ENTRY_INCOMPLETE"),
        ("drop a library entry's note", note_dropped, "ONT_MATCHER_ENTRY_INCOMPLETE"),
        ("drop a matcher a selector names, under --matchers", selector_matcher_undeclared, "ONT_MATCHER_UNDECLARED"),
    ]


#: The --matchers plants run a second time through the default mode, one per
#: O-M code. O-15 refuses either calibration flag under its own code in the
#: default mode, so each plant asserts the O-M code itself and a lost O-M1 is
#: not hidden behind O-15.
DEFAULT_MODE_PLANTS = ("identity_basis_without_file", "connector_names_undeclared", "purpose_outside_set")


def _run_plants(label: str, plants, base: dict, run) -> tuple[int, int]:
    failures = 0
    for desc, mutate, expected in plants:
        ctx = copy.deepcopy(base)
        try:
            mutate(ctx)
            drawn = run(ctx)
            fired, hiding = {fnd.code for fnd in drawn}, _hiding_moves(drawn)
        except Exception as exc:  # a plant that cannot be applied is a failed plant
            fired, hiding = {f"PLANT_ERROR {type(exc).__name__}: {exc}"}, []
        failures += _judge(label, desc, expected, fired, hiding)
    return failures, len(plants)


def _hiding_moves(findings) -> list[str]:
    """The codes of refusals whose moves offer to set a kernel gate entry's state."""
    return sorted({fnd.code for fnd in findings if GATE_STATE_MOVE_RE.search(fnd.moves or "")})


def _judge(label: str, desc: str, expected: str, fired: set, hiding: list[str]) -> int:
    """Print one plant's line and return 1 when it was not refused cleanly: its code
    did not fire, or a refusal it drew offers a move that hides the fault."""
    ok = expected in fired and not hiding
    mark = "refused" if ok else ("HIDING  " if expected in fired else "PASSED  ")
    print(
        f"  {mark}  {label:10} {desc:60} expected {expected}"
        + ("" if expected in fired else f", fired {sorted(fired)}")
        + (f", and {', '.join(hiding)} offers a gate-state move" if hiding else "")
    )
    return 0 if ok else 1


def _unreadable_plants():
    """Inputs --corpus cannot read. Each must raise Unreadable with its code."""
    absent = (("must-pass", ROOT / "conformance" / "self-test-absent.jsonl", "conformance/self-test-absent.jsonl"),)
    rel = "conformance/must-pass.jsonl"
    return [
        ("a corpus file that does not exist", lambda: load_corpora(absent), "ONT_CORPUS_UNREADABLE"),
        ("a corpus line that is not JSON", lambda: parse_corpus("{not json", rel), "ONT_CORPUS_UNREADABLE"),
        ("a corpus row with no event", lambda: parse_corpus('{"name": "x"}', rel), "ONT_CORPUS_UNREADABLE"),
        ("a layer model that binds no field to the registry", lambda: require_sites([]), "ONT_CORPUS_SITES_UNREADABLE"),
    ]


def _run_unreadable(plants) -> tuple[int, int]:
    failures = 0
    for desc, act, expected in plants:
        findings: list[Finding] = []
        try:
            act()
        except Unreadable as exc:
            findings = [exc.finding]
        except Exception as exc:  # a plant that cannot be applied is a failed plant
            findings = [Finding(f"PLANT_ERROR {type(exc).__name__}: {exc}", "", "", "")]
        failures += _judge("unreadable", desc, expected, {f.code for f in findings}, _hiding_moves(findings))
    return failures, len(plants)


def self_test(reg: dict, text: str, codes: set[str], sites=None, corpora=None, sources=None) -> int:
    baseline = check(reg, text, codes)
    if baseline:
        print("self-test cannot run: the unmutated registry is not clean", file=sys.stderr)
        for fnd in baseline:
            print(fnd.render(), file=sys.stderr)
        return 1
    corpus_base, _ = check_corpus(reg, sites, corpora)
    matcher_base, _ = check_matchers_mode(reg, sources)
    matcher_base += registry_lint(reg, text, codes, sources)
    if corpus_base or matcher_base:
        print(
            "self-test cannot run: the unmutated corpora or matchers block is not clean, so a "
            "planted break cannot be told from the tree",
            file=sys.stderr,
        )
        for fnd in corpus_base + matcher_base:
            print(fnd.render(), file=sys.stderr)
        return 1
    failures = 0
    muts = _mutations()
    for desc, mutate, expected in muts:
        r = copy.deepcopy(reg)
        mutate(r)
        drawn = check(r, text, codes)
        failures += _judge("registry", desc, expected, {fnd.code for fnd in drawn}, _hiding_moves(drawn))
    corpus_failed, corpus_n = _run_plants(
        "--corpus",
        _corpus_plants(),
        {"reg": reg, "corpora": corpora},
        lambda c: check_corpus(c["reg"], sites, c["corpora"])[0],
    )
    matcher_failed, matcher_n = _run_plants(
        "--matchers",
        _matcher_plants(),
        {"reg": reg, "sources": sources},
        lambda c: check_matchers_mode(c["reg"], c["sources"])[0],
    )
    # The O-M codes again, through what the default mode runs, so a refusal of
    # theirs is proven to reach the IMPLEMENTED ontology entry (reading O-R6).
    lint_failed, lint_n = _run_plants(
        "default",
        [p for p in _matcher_plants() if p[1].__name__ in DEFAULT_MODE_PLANTS],
        {"reg": reg, "sources": sources},
        lambda c: registry_lint(c["reg"], text, codes, c["sources"]),
    )
    unread_failed, unread_n = _run_unreadable(_unreadable_plants())
    failures += corpus_failed + matcher_failed + lint_failed + unread_failed
    total = len(muts) + corpus_n + matcher_n + lint_n + unread_n
    print()
    if failures:
        print(
            f"validate_ontology --self-test: {failures} of {total} deliberate breaks were not "
            "refused, or were refused with a move that hides the fault (HIDING). A gate nobody "
            "has watched fail is an assumption (HYGIENE.md section 2).",
            file=sys.stderr,
        )
        return 1
    print(
        f"validate_ontology --self-test ok: {total} deliberate breaks, {total} refused "
        f"({len(muts)} registry, {corpus_n} --corpus, {matcher_n} --matchers, {lint_n} --matchers "
        f"through the default mode, {unread_n} unreadable), no refusal offering a gate-state "
        "move, and the unplanted registry, corpora and matchers block clean"
    )
    return 0


# ---------------------------------------------------------------------------
# entry
# ---------------------------------------------------------------------------


def load() -> tuple[dict, str]:
    text = REGISTRY.read_text(encoding="utf-8")
    reg = yaml.safe_load(text)
    if not isinstance(reg, dict):
        raise ValueError("the registry did not parse to a mapping")
    return reg, text


def _record(gate: str, findings: list[Finding]) -> None:
    if not gate_log:
        return
    try:
        gate_log.record_run(gate, "refuse" if findings else "pass", count=len(findings))
        for fnd in findings:
            gate_log.record_finding(gate, code=fnd.code, where=fnd.where)
    except Exception:
        pass


def _refuse(findings: list[Finding], flag: str, rule: str) -> int:
    for fnd in findings:
        print(fnd.render(), file=sys.stderr)
        print(file=sys.stderr)
    print(f"validate_ontology {flag}: {len(findings)} violation(s). rule: {rule}", file=sys.stderr)
    return 1


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Selector registry self-lint.")
    ap.add_argument("--registry", action="store_true", help="Registry self-lint. The default.")
    ap.add_argument(
        "--matchers",
        action="store_true",
        help="The structural half of the matcher check, O-M1 to O-M3. Scores nothing, and says so.",
    )
    ap.add_argument(
        "--corpus",
        action="store_true",
        help="Read both conformance corpora at every registry-bound site, O-C1 to O-C4.",
    )
    ap.add_argument(
        "--self-test",
        action="store_true",
        help="Break the registry, the corpora and the matchers block in memory and assert each break is refused.",
    )
    ap.add_argument("--quiet", action="store_true", help="Print only on failure.")
    args = ap.parse_args(argv)

    try:
        reg, text = load()
    except FileNotFoundError:
        print(
            "REFUSED ONTOLOGY_UNREADABLE\n"
            f"  where: {REL}\n"
            "  what:  the selector registry does not exist, so every connector invents its "
            "own field names and D2 is unenforced\n"
            "  moves: write ontology/selectors.yaml, or move the ontology gate to PENDING in "
            "tools/validate_conformance.py",
            file=sys.stderr,
        )
        return 2
    except (yaml.YAMLError, ValueError) as exc:
        print(
            "REFUSED ONTOLOGY_UNREADABLE\n"
            f"  where: {REL}\n"
            f"  what:  the file is not parseable YAML: {exc}\n"
            "  moves: fix the syntax; the manifest validator and this gate read the same parse",
            file=sys.stderr,
        )
        return 2

    try:
        codes = declared_codes()
    except (FileNotFoundError, yaml.YAMLError, ValueError) as exc:
        print(
            "REFUSED CODE_VOCABULARY_UNREADABLE\n"
            "  where: spec/layer-model.yaml\n"
            f"  what:  the violation-code vocabulary could not be read: {exc}. This gate reads "
            "the codes from the layer model rather than from a copy, so it cannot run without it\n"
            "  moves: fix spec/layer-model.yaml, or run tools/validate_layer_model.py first",
            file=sys.stderr,
        )
        return 2

    sites = corpora = sources = None
    if args.corpus or args.self_test:
        try:
            sites = require_sites(registry_sites(load_layer_model()))
            corpora = load_corpora()
        except Unreadable as exc:
            print(exc.finding.render(), file=sys.stderr)
            return 2
        except (FileNotFoundError, yaml.YAMLError, ValueError, UnicodeDecodeError) as exc:
            print(
                "REFUSED ONT_CORPUS_SITES_UNREADABLE\n"
                "  where: spec/layer-model.yaml\n"
                f"  what:  the layer model could not be read for its registry-bound sites: {exc}\n"
                "  moves: fix spec/layer-model.yaml, or run tools/validate_layer_model.py first",
                file=sys.stderr,
            )
            return 2
    if args.matchers or args.self_test or not args.corpus:
        try:
            sources = connector_sources()
        except (OSError, UnicodeDecodeError) as exc:
            print(
                "REFUSED ONT_MATCHER_SOURCES_UNREADABLE\n"
                "  where: connectors\n"
                f"  what:  a connector's adapter.py or manifest.yaml could not be read: {exc}. O-M2 "
                "reads every one, and a file skipped is a matcher name nobody checked\n"
                "  moves: fix the file's encoding or permissions and run again",
                file=sys.stderr,
            )
            return 2

    if args.self_test:
        return self_test(reg, text, codes, sites, corpora, sources)

    if args.corpus:
        findings, stats = check_corpus(reg, sites, corpora)
        _record("ontology-corpus", findings)
        if findings:
            return _refuse(
                findings,
                "--corpus",
                "every selector the corpora carry is a registry key in its form, every fixture "
                "claiming an ontology code is refused for it here, and every key is proven or "
                "declared unexercised; docs/PLAINSIGHT-FOUNDATION.md D2, CLAUDE.md design gates 1 and 3.",
            )
        if not args.quiet:
            print(corpus_report(stats, sites, reg))
        return 0

    if args.matchers:
        findings, report = check_matchers_mode(reg, sources)
        _record("ontology-matchers", findings)
        if findings:
            return _refuse(
                findings,
                "--matchers",
                "an unscored matcher may not be an identity basis, and every matcher a selector or "
                "a connector names is declared with its purpose; SS-19, CLAUDE.md design gate 6. "
                "No matcher is scored by this mode.",
            )
        if not args.quiet:
            print(matchers_report(report))
        return 0

    findings = registry_lint(reg, text, codes, sources)
    _record(GATE, findings)

    if findings:
        for fnd in findings:
            print(fnd.render(), file=sys.stderr)
            print(file=sys.stderr)
        print(
            f"validate_ontology: {len(findings)} violation(s). "
            "rule: ontology/selectors.yaml is rank 3 and closes the selector vocabulary at the "
            "manifest and the corpus; docs/PLAINSIGHT-FOUNDATION.md D2, CLAUDE.md design gate 1.",
            file=sys.stderr,
        )
        return 1

    if not args.quiet:
        selectors = reg.get("selectors") or {}
        anchors = sum(1 for v in selectors.values() if isinstance(v, dict) and v.get("may_anchor_entity") is True)
        constraints = sum(1 for v in selectors.values() if isinstance(v, dict) and v.get("datum_class") == "constraint")
        proposed = len(_as_list((reg.get("ontology") or {}).get("proposed")))
        lib = len((reg.get("matchers") or {}).get("library") or {})
        print(
            f"validate_ontology ok: {len(selectors)} selectors ({proposed} proposed), {anchors} "
            f"anchor-eligible, {constraints} constraint, {len(reg.get('entities') or {})} entity "
            f"types, {len(_as_list(reg.get('prohibitions')))} prohibitions, {lib} matchers, "
            f"none calibrated, and O-M1 to O-M3 clean across {len(sources)} connector file(s)"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
