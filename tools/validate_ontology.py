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

`--registry` is the default and runs every check above. `--self-test` breaks the
loaded registry in memory in sixteen directions and asserts each break is
refused, which is doctrine/HYGIENE.md section 2's rule for a newly written
check. `--matchers` and `--corpus` are deferred and say so rather than passing.

Exit codes: 0 clean, 1 violations found, 2 the registry or the code vocabulary
could not be read.
"""

from __future__ import annotations

import argparse
import copy
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
        r["selectors"]["handle"]["form"] = "handle:acmegram/examplename"

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


def self_test(reg: dict, text: str, codes: set[str]) -> int:
    baseline = check(reg, text, codes)
    if baseline:
        print("self-test cannot run: the unmutated registry is not clean", file=sys.stderr)
        for fnd in baseline:
            print(fnd.render(), file=sys.stderr)
        return 1
    failures = 0
    muts = _mutations()
    for desc, mutate, expected in muts:
        r = copy.deepcopy(reg)
        mutate(r)
        fired = {fnd.code for fnd in check(r, text, codes)}
        ok = expected in fired
        failures += 0 if ok else 1
        print(
            f"  {'refused' if ok else 'PASSED  '}  {desc:56} expected {expected}"
            + ("" if ok else f", fired {sorted(fired)}")
        )
    print()
    if failures:
        print(
            f"validate_ontology --self-test: {failures} mutation(s) were not refused. A gate "
            "nobody has watched fail is an assumption (HYGIENE.md section 2).",
            file=sys.stderr,
        )
        return 1
    print(f"validate_ontology --self-test ok: {len(muts)} deliberate breaks, {len(muts)} refused")
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


def _deferred(flag: str, stands_in: str, un_defers: str) -> int:
    print(
        f"validate_ontology {flag}: DEFERRED, and it checked nothing.\n"
        f"  stands in:  {stands_in}\n"
        f"  un-defers:  {un_defers}\n"
        "  docs/THE-GAMEPLAN.md section 2.2 carries the trigger. A deferred check is "
        "never counted as a pass."
    )
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Selector registry self-lint.")
    ap.add_argument("--registry", action="store_true", help="Registry self-lint. The default.")
    ap.add_argument("--matchers", action="store_true", help="Deferred until the first matcher exists.")
    ap.add_argument("--corpus", action="store_true", help="Deferred until the conformance corpus exists.")
    ap.add_argument("--self-test", action="store_true", help="Break the registry in memory and assert each break is refused.")
    ap.add_argument("--quiet", action="store_true", help="Print only on failure.")
    args = ap.parse_args(argv)

    if args.matchers:
        return _deferred(
            "--matchers",
            "the contract's rule that an unscored matcher may not be an identity basis, "
            "declared in the registry's matchers block",
            "the first matcher exists. Scoring needs labelled ground truth, which needs a "
            "sealed cast",
        )
    if args.corpus:
        return _deferred(
            "--corpus",
            "the registry self-lint, which closes the vocabulary at the manifest boundary",
            "conformance/must-pass.jsonl and must-fail.jsonl exist. Step 7",
        )

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

    if args.self_test:
        return self_test(reg, text, codes)

    findings = check(reg, text, codes)

    if gate_log:
        try:
            gate_log.record_run(GATE, "refuse" if findings else "pass", count=len(findings))
            for fnd in findings:
                gate_log.record_finding(GATE, code=fnd.code, where=fnd.where)
        except Exception:
            pass

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
            "none calibrated"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
