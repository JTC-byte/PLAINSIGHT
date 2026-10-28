"""The subject gate: D5, SS-6 to SS-9, and SS-14 item 6, on the dispatch path.

`evaluate(request)` answers one question for one dispatch: may the runner
construct argv for this selector, on this connector, in this case. It returns a
`Decision` whose value is one of the three SS-7 values, read by name from
`policy/subject-authorization.yaml` rather than written here, with the basis and
the violation code the compiled policy assigns to the step that decided, and the
consequence sentence the interface renders. `doctrine/SUBJECT_SELECTION.md`
says what a permitted value means: the runner will construct argv, and it means
nothing else.

DRAFT, UNRATIFIED, AND IT REFUSES. This module is Class F by effect, drafted by
an agent at Step 10 of docs/THE-GAMEPLAN.md. It reads the pin of record,
`doctrine/DOCTRINE_STATUS.md`, through `tools/pin_of_record.py`, and while the
compiled policy, its schema and the rest of SS-14 item 6's list carry no
whole-artifact dated row, every request it is given returns REFUSED. Only a
fully stamped pin permits, and a fully stamped pin includes a dated row for
every unratified entry the permit path passes through.

HOW THE ORDER RUNS. SS-8 is rank 1 and fixes it, and the order below is that
order with the two rules SS-8 does not place written where they fall:

  1. The NEVER list. Item 6, the one item the gate can evaluate, reads the pin:
     every path SS-14 item 6 names stamped, every SS and RT criterion bound, the
     cast sealed with a confuser pair, and preflight passed in this process.
     Items 1 to 5 are not gate-evaluable, as the policy's never.items record.
  -  The incidental rule (SS-10): a selector whose per-case class is S5, or a
     chain with an incidental hop, is refused. SS-8 does not place it and the
     closed refusal_basis enum has no member for it, which GF-U2 holds.
  2. The record: present, for this case, for the class claimed, complete, and
     unexpired. A record with no purpose is refused as purpose_unbound, whose
     step GF-U3 holds.
  3. The class: in the authorizable set, and for S3 or S4 the SS-17 baseline.
     No object can satisfy the baseline while SA-U6 is open, so this draft
     refuses S3 and S4 unconditionally. It also refuses N0, L0 and S1
     unconditionally, because their permits wait on SA-U2 or SA-U5 and this
     draft implements no option of either (SG-R17).
  4. The selector: a seed inside the record's set, or a pivot whose chain
     starts at one and whose depth is inside pivot_depth_max.
  5. The chain: every hop after the seed, and the hop to this selector, carries
     an analyst's adjudication. An unadjudicated hop is scope drift.
  6. The bystander declaration: the connector's manifest `bystanders` block,
     with every disposition inside the closed set.
  -  The pre-flight estimate (SS-12), required on every dispatch while SA-U13
     leaves "reaches beyond its named selector" undefined.
  -  The binding read: every unratified entry the compiled policy lists against
     an element the permit path passed through carries a dated row.

Every check before the binding read refuses whatever the record says, so a
present, complete, valid, unexpired authorization record unlocks none of them.
`runner/tests/test_subject_guard.py` proves that, and proves that a pin missing
one row refuses.

HOW THE APP'S DEEP-DIVE ROUTE CALLS IT. An analyst selecting a node for a deep
dive is SS-16's separate authorized act. The route builds a `Request` from the
case store: the case id, the GRANT's authorization_ref and the SS-4 record read
inside the case boundary, the node's selector type and value, the per-case class
the case records for that selector, the chain from the case's seed to the node
as `Hop`s carrying each hop's motivating claim id and adjudication id, the
analyst's selection as the adjudication of the final hop, the chosen
connector's id and its manifest's `bystanders` block, the pre-flight estimate,
and the clock. It leaves `preflight_passed` False, because the app process is
not the runner and runs no preflight, so the route can never receive the
permitted value. It calls `evaluate(request)` and renders
`decision.consequence`. It constructs no argv and opens nothing.

HOW THE RUNNER CALLS IT. At startup the runner runs SS-14 item 6's four
preflight checks in its own process and sets `preflight_passed` True on its
requests only when all four passed; a failure is fatal to the runner. For each
dispatch, after pivot selection, it builds the same `Request` and calls:

    decision = evaluate(request)
    if decision.permits:
        ...  # argv construction, the credential draw, the subscription

or returns early on `if not decision.permits:` before any of the three. It
writes `decision.to_collect_event(...)` to the case and names that event as the
lineage parent of the run's PROBE_EVENT RUN_START, which spec/layer-model.yaml
requires of every run. No dispatch may construct argv, draw a credential or
open a subscription before `evaluate()` has returned a decision whose `permits`
is True. `tools/validate_authorization.py --dispatch-paths` checks that shape
statically over runner/, connectors/ and app/, and a call site that does not
have it must be listed in runner/dispatch_allowlist.yaml with a reason.

WHAT THE GUARD NEVER DOES. It writes nothing anywhere, opens no connection, runs
no process, and holds no state between calls. It never reads collected content
(SS-19): a `Hop` carries a selector, a claim id and an adjudication id, and no
field of a collected item. It never logs, prints or returns a selector value:
`Request`, `Hop` and `Decision` withhold it from their repr, and a decision and
its payload carry the selector's registered type alone. Importing this module
reads no file; the policy, the pin and the cast are read inside `evaluate()`.

Readings SG-R1 to SG-R14, SG-R17 and SG-R18 are the calls this draft made where
doctrine leaves the question open. They are listed in `READINGS` and await the
operator. SG-R15 and SG-R16 are wiring decisions about the kernel gate and the
Makefile, recorded with the build rather than here.
"""

from __future__ import annotations

import datetime as _dt
import importlib.util
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "policy" / "subject-authorization.yaml"
RETENTION_POLICY = ROOT / "policy" / "retention.yaml"
PIN_READER = ROOT / "tools" / "pin_of_record.py"
CAST_READER = ROOT / "tools" / "validate_cast.py"

POLICY_REL = "policy/subject-authorization.yaml"
REGISTER_REL = "conformance/gate/README.md"
CAST_PATH = "synthetic/CAST.md"

#: The one producer spec/layer-model.yaml names for COLLECT_EVENT.
PRODUCER = "runner-subject-guard"

#: SS-8's order has six steps and the wire's decided_at_step enum is 1 to 6. A
#: policy carrying any other set refuses, so a dropped step cannot be skipped.
EVALUATION_STEPS = (1, 2, 3, 4, 5, 6)

#: SS-14 item 6 stamps the contract by its sections 5 and 12. Pinned here, as
#: tools/validate_authorization.py pins it, so the policy under ratification
#: does not decide how finely it is stamped.
RATIFY_SECTIONS = {"spec/pse-semantics-contract.md": frozenset({"§5", "§12"})}

#: The cast's confuser codes, read through tools/validate_cast.py's own checks.
CONFUSER_CODES = (
    "CAST_NO_CONFUSER_PAIR",
    "CAST_CONFUSER_PAIR_WITHIN_ONE_PERSONA",
    "CAST_CONFUSER_PAIR_NOT_DISTINCT",
    "CAST_CONFUSER_SHARES_LINKED_DOMAIN",
)

#: An unratified entry id, and the file that holds each family (SG-R9).
ENTRY_RE = re.compile(r"^((?:SA|GF)-U\d+)\s")
ENTRY_HOLDER = {"SA": POLICY_REL, "GF": REGISTER_REL}

#: Entries this module adds to a permit path because the policy cannot list
#: them: GF-U4 lives in conformance/gate/README.md (SG-R6).
PIVOT_ENTRIES = ("GF-U4",)

#: Classes whose permit waits on an entry whose options this guard does not
#: implement, refused at step 3 whatever the pin says (SG-R17). The binding read
#: sees only that an entry carries a dated row and not which option the row
#: ratified, so a stamp of SA-U2's hold option, or of an SA-U5 option that needs a
#: consent-expiry comparison this module does not make, would otherwise unlock
#: the class. The values are the class's own unratified_dependencies.
OPTION_BLIND_CLASSES = {"N0": ("SA-U2",), "L0": ("SA-U2",), "S1": ("SA-U5", "SA-U8")}

READINGS = {
    "SG-R1": "SS-8 is rank 1 and puts the NEVER list first, and SS-14 item 6 is a NEVER "
    "item, so the stamp read is step 1 rather than the last check. The brief for this "
    "draft placed it after the record checks; rank 1 wins. The compiled policy, its "
    "schema and both doctrine files are on item 6's list, so the read that decides "
    "whether the policy binds and item 6 are one read.",
    "SG-R2": "The incidental rule is evaluated immediately after step 1. SS-10 makes it "
    "absolute, SS-8 does not place it, and the refusal carries no step and no basis on "
    "the wire while GF-U2 is open; its code is SUBJECT_NOT_AUTHORIZED, as "
    "spec/pse-semantics-contract.md section 5.3 states.",
    "SG-R3": "A claimed class that differs from the record's class is refused as "
    "authorization_missing at step 2. SS-1 says the gate reads the class from the record "
    "and refuses when no record covers the selector, and a record for another class does "
    "not cover it.",
    "SG-R4": "Expiry is compared on the UTC date of the clock, which both SA-U3 options "
    "share. A record whose expires_on precedes that date is refused as expired. A record "
    "expiring on that date is refused and held on SA-U3, because inclusivity is the open "
    "half. The guard evaluates at dispatch; whether a run in flight is re-evaluated is "
    "SA-U3's and the runner's.",
    "SG-R5": "No object satisfies SS-17's baseline while SA-U6 is open, so S3 and S4 are "
    "refused at step 3 whatever the request carries, rendered with SA-U6's sentence.",
    "SG-R6": "A pivot's depth is the number of hops from a seed. A depth beyond "
    "pivot_depth_max is pivot_depth_exceeded. A depth equal to it is also returned as "
    "REQUIRES_EXTENSION and held on GF-U4, which is the reading that refuses one hop "
    "sooner; both values stop the run (GF-R5). Every pivot permit also waits on GF-U4.",
    "SG-R7": "Scope drift is an unadjudicated hop: GF-U4's second option, the most "
    "restrictive of the three. The analyst's selection of a node for a deep dive is the "
    "adjudication of the final hop.",
    "SG-R8": "SS-12's estimate is required on every dispatch, the conservative move "
    "SA-U13 names, and unestimable requires a non-blank reason, the restrictive half of "
    "SA-U12. The refusal's step is held on SA-U16.",
    "SG-R9": "An unratified entry is resolved when a Ratified-table row passing PIN-R2, "
    "not withdrawn under PIN-R3, opens its Item cell with the entry id and a space and "
    "names in its File cell the file that holds the entry. This is PIN-R9's form for "
    "decisions applied to entries, and it belongs in tools/pin_of_record.py once the "
    "operator confirms it.",
    "SG-R10": "Entries are read at the granularity the policy lists them: a step's "
    "unratified_dependencies hold every permit that passes the step, including entries "
    "whose question does not arise for the class at hand.",
    "SG-R11": "A PERMITTED payload carries one bystander_disposition. A connector that "
    "reaches only its named selector records refuse. A connector with several classes "
    "records count_only if any class is count_only, so the record never understates "
    "what was kept.",
    "SG-R12": "preflight_passed is the runner process's own state, passed on each request "
    "and False by default. The guard cannot verify it, and the app's route never sets it.",
    "SG-R13": "schema/subject-authorization.schema.json says evaluate() validates the record "
    "against it before reading a field. This draft checks SS-4's nine fields by presence and "
    "the shapes it reads (a list of typed selectors, a non-negative integer depth, an ISO "
    "date) and does not run the schema, because the guard is held to the standard library "
    "and PyYAML. tools/validate_authorization.py records that every corpus record fails the "
    "schema today on SAS-U1 and SA-U2, so running it would refuse every request at step 2; "
    "that is a stricter answer this draft does not give, and the operator decides it.",
    "SG-R14": "SS-19's refusal of a selector that does not match its registered matcher sits "
    "at argv construction, which the policy places after the gate, so it is not in this "
    "module. ontology/selectors.yaml names runner/subject_guard.py as its reader for that "
    "rule. One argv builder exists today: invoke() in connectors/sherlock/adapter.py builds "
    "argv from the manifest's command template after a permitting decision, and its "
    "check_argv_value is the interim shape gate there, because shape.username.v1 carries no "
    "grammar in the registry (reading SH-R16). Supplying that grammar is the operator's.",
    "SG-R17": "The binding read counts an entry resolved when a dated row names it, and it "
    "cannot read which option the row ratified. SA-U2 offers a hold option whose purpose is "
    "to keep N0 and L0 refused, and SA-U5's options need a consent-expiry comparison this "
    "module does not make, so a stamp of either would unlock a class the stamped option does "
    "not permit. N0, L0 and S1 are therefore refused at step 3 whatever the pin says, as S3 "
    "and S4 are under SG-R5. The move that lifts this is an option-aware read: the guard "
    "returns the ratified option and refuses any option it does not implement.",
    "SG-R18": "Steps 4 and 6 take their violation code from the compiled policy's "
    "gate.evaluation_order, and three held corpus rows in conformance/gate/decisions.jsonl "
    "expect otherwise. Step 4 carries no code, so seed-selectors-mutated and "
    "one-hop-pivot-depth-max-mutated emit none where the corpus expects "
    "SUBJECT_NOT_AUTHORIZED. Step 6 carries BYSTANDER_DISPOSITION_OUT_OF_SET for both of its "
    "bases, so bystander-declaration-absent emits it where the corpus expects none, and "
    "policy/violation-codes.yaml fires that code only for a disposition outside the set. "
    "The guard follows the rank-3 policy. The conflict is the operator's: a per-basis code "
    "map in the policy, or a corpus change. Part 2 grading will report these three rows "
    "when VA-U1 lands.",
}

# ---------------------------------------------------------------------------
# Governed sentences this module renders where the compiled policy carries none.
# Each says what was refused, which rule refused it, and the legal moves.
# ---------------------------------------------------------------------------

POLICY_UNREADABLE = (
    "REFUSED\n"
    "  where: runner/subject_guard.py, reading policy/subject-authorization.yaml\n"
    "  what:  the compiled policy the gate reads could not be loaded, or it no longer\n"
    "         carries a value, step, basis or sentence this module reads by name. The\n"
    "         gate cannot say what a step returns without it, so nothing dispatches\n"
    "  moves: restore policy/subject-authorization.yaml from git; or run\n"
    "         python tools/validate_authorization.py --fixtures, which names the\n"
    "         drift; or dispatch nothing, which is what this refusal is holding"
)

GUARD_FAULT = (
    "REFUSED\n"
    "  where: runner/subject_guard.py\n"
    "  what:  the gate raised while evaluating this request, so it returned no decision\n"
    "         it can stand behind. A dispatch without a decision is the bypass SS-6\n"
    "         exists to stop, so nothing dispatches\n"
    "  moves: run python -m pytest runner -q and fix what it names; or check the\n"
    "         request against the Request docstring; or dispatch nothing, which is\n"
    "         what this refusal is holding"
)

INCIDENTAL_ORIGIN = (
    "REFUSED PENDING RATIFICATION\n"
    "  where: conformance/gate/README.md unratified GF-U2\n"
    "  what:  this selector, or a selector in the chain that reached it, arrived as an\n"
    "         incidental person. SS-10 says an incidental person never becomes a pivot\n"
    "         origin and an S5 selector is not a seed for anything, and no\n"
    "         authorization record unlocks that. The refusal carries no step and no\n"
    "         basis on the wire, because SS-8 does not place it and the closed\n"
    "         refusal_basis enum has no member for it\n"
    "  moves: open a new case with that person's own authorization record under S3 or\n"
    "         S4, which is a decision rather than a refusal; or drop the selector; or\n"
    "         stamp GF-U2 so the refusal carries a basis"
)

PIVOT_HELD = (
    "REFUSED PENDING RATIFICATION\n"
    "  where: conformance/gate/README.md unratified GF-U4\n"
    "  what:  this pivot is inside the depth bound and every hop in its chain carries an\n"
    "         adjudication, and no ratified predicate separates a chain that has left\n"
    "         the authorized set from a pivot the bound permits. Permitting it would\n"
    "         decide how far a chain may walk without a new decision\n"
    "  moves: stamp one of GF-U4's options in doctrine/DOCTRINE_STATUS.md; or authorize\n"
    "         this selector as a seed in its own record, which SS-16 describes and which\n"
    "         is always legal; or dispatch nothing"
)

#: SS-7's refused row describes a class refusal that no corrected file unlocks.
#: These four bases are not that, and GF-U5 holds which sentence renders them.
UNCOMPILED = {
    "bystander_undeclared": (
        "the connector's manifest declares no bystanders block, or one outside the\n"
        "         shape schema/connector-manifest.schema.json closes (SS-10)",
        "declare the bystanders block in the connector's manifest and pass\n"
        "         python tools/validate_manifest.py --all; or stamp GF-U5 so a compiled\n"
        "         sentence renders here; or dispatch nothing",
    ),
    "disposition_out_of_set": (
        "a bystander disposition outside count_only and refuse, the set R8 closed at\n"
        "         v0.1 (SS-10)",
        "declare count_only or refuse for every bystander class; or ratify a wider set\n"
        "         under R8, which is a Class F act; or dispatch nothing",
    ),
    "incidental_estimate_missing": (
        "a pre-flight record with no incidental estimate, or with unestimable and no\n"
        "         reason, and SS-12 says a blank field is a refusal",
        "supply an integer estimate, or unestimable with a reason; or stamp SA-U12,\n"
        "         SA-U13 and SA-U16; or dispatch nothing",
    ),
    "purpose_unbound": (
        "an authorization record that carries no bound purpose, and SS-4 binds the\n"
        "         purpose to the case at creation",
        "bind a one-sentence purpose to the case at creation and issue a new GRANT; or\n"
        "         stamp GF-U3, which places the refusal in SS-8's order; or dispatch\n"
        "         nothing",
    ),
}


def uncompiled_sentence(basis: str) -> str:
    what, moves = UNCOMPILED[basis]
    return (
        "REFUSED PENDING RATIFICATION\n"
        "  where: conformance/gate/README.md unratified GF-U5\n"
        f"  what:  the gate refused this dispatch on {what}. The compiled policy carries\n"
        "         no consequence sentence for this basis, and SS-7's refused row\n"
        "         describes a class refusal no corrected file unlocks, which is not\n"
        "         what happened here, so it is not rendered\n"
        f"  moves: {moves}"
    )


# ---------------------------------------------------------------------------
# The request and the decision.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Hop:
    """One selector on the chain from a seed. chain[0] is the seed.

    `relation` is the case's computed subject_relation for this selector (SS-10):
    seed, pivot or incidental. `motivated_by` is the EXTRACT_EVENT claim id that
    surfaced it and `adjudication_ref` the analyst's adjudication of that hop;
    both are None on the seed. A hop carries no collected content (SS-19).
    """

    selector_type: str
    selector: str = field(repr=False)
    relation: str = "pivot"
    motivated_by: str | None = None
    adjudication_ref: str | None = None

    def __repr__(self) -> str:
        return (
            f"Hop(selector_type={self.selector_type!r}, selector=<withheld>, "
            f"relation={self.relation!r}, motivated_by={self.motivated_by!r}, "
            f"adjudicated={bool(self.adjudication_ref)})"
        )


@dataclass(frozen=True)
class Request:
    """Everything the gate reads for one dispatch, and nothing collected.

    `authorization` is the SS-4 record, stratum 1, read inside the case
    boundary; `authorization_ref` is the GRANT's opaque id for it. `selector` is
    a value or a placeholder and is never echoed. `subject_class` is the class
    the case records for this selector. `bystanders` is the connector
    manifest's `bystanders` block. `clock` must carry a zone.
    """

    case_id: str
    authorization_ref: str | None
    authorization: Mapping | None = field(repr=False)
    connector_id: str
    selector_type: str
    selector: str = field(repr=False)
    subject_class: str
    clock: _dt.datetime
    chain: tuple = ()
    motivated_by: str | None = None
    adjudication_ref: str | None = None
    bystanders: Mapping | None = None
    incidental_estimate: object = None
    incidental_estimate_reason: str | None = None
    preflight_passed: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.clock, _dt.datetime) or self.clock.utcoffset() is None:
            raise ValueError(
                "REFUSED: the request's clock carries no zone, and the expiry comparison "
                "is on the UTC date (SA-U3). moves: pass an aware datetime, such as "
                "datetime.now(timezone.utc)"
            )
        object.__setattr__(self, "chain", tuple(self.chain))
        if not all(isinstance(h, Hop) for h in self.chain):
            raise ValueError("REFUSED: every chain element must be a Hop. moves: build the chain from Hop objects")
        if _blank(self.connector_id) or _blank(self.selector_type) or _blank(self.case_id):
            raise ValueError(
                "REFUSED: the request names no case, no connector or no selector type, and a "
                "COLLECT_EVENT carries all three. moves: read them from the case and the "
                "connector's manifest before calling evaluate()"
            )

    def __repr__(self) -> str:
        return (
            f"Request(case_id={self.case_id!r}, authorization_ref={self.authorization_ref!r}, "
            f"authorization=<withheld>, connector_id={self.connector_id!r}, "
            f"selector_type={self.selector_type!r}, selector=<withheld>, "
            f"subject_class={self.subject_class!r}, chain={len(self.chain)} hop(s))"
        )


@dataclass(frozen=True)
class Decision:
    """The gate's answer. `permits` is True on the one permit path and nowhere else.

    `consequence` is the sentence the interface renders: CLAUDE.md section 4
    renders a state as its consequence, never as its token. `held_on` names the
    unratified entries that decide part of this answer. `reasons` says which
    rows or conditions refused, and never carries a value.
    """

    value: str
    permits: bool
    consequence: str
    connector_id: str
    target_selector_type: str
    decided_at_step: int | None = None
    basis_field: str | None = None
    basis: str | None = None
    never_item: int | None = None
    code: str | None = None
    held_on: tuple = ()
    reasons: tuple = ()
    authorization_ref: str | None = None
    subject_relation: str | None = None
    pivot_depth: int | None = None
    motivated_by: str | None = None
    incidental_estimate: object = None
    incidental_estimate_reason: str | None = None
    bystander_disposition: str | None = None

    def to_collect_payload(self) -> dict:
        """The COLLECT_EVENT payload, per spec/layer-model.yaml. Never a value.

        A refusal whose step or basis is held on an unratified entry omits the
        field, so its payload does not validate until that entry is stamped,
        which is the honest state rather than a token chosen here.
        """
        p: dict = {"decision": self.value, "connector_id": self.connector_id,
                   "target_selector_type": self.target_selector_type}
        # A REFUSED payload is closed without authorization_ref: a step 2
        # refusal has no record to point at, and the layer model types every
        # refusal the same way.
        if self.authorization_ref and self.subject_relation is not None:
            p["authorization_ref"] = self.authorization_ref
        if self.decided_at_step is not None:
            p["decided_at_step"] = self.decided_at_step
        if self.basis_field and self.basis:
            p[self.basis_field] = self.basis
        if self.never_item is not None:
            p["never_item"] = self.never_item
        if self.subject_relation is not None:
            p["subject_relation"] = self.subject_relation
            p["pivot_depth"] = self.pivot_depth
            p["motivated_by"] = self.motivated_by
        if self.permits:
            p["incidental_estimate"] = self.incidental_estimate
            if self.incidental_estimate == "unestimable":
                p["incidental_estimate_reason"] = self.incidental_estimate_reason
            p["bystander_disposition"] = self.bystander_disposition
        return p

    def to_collect_event(self, *, case_id: str, event_id: str, ts: str, platform_id: str,
                         sw_version: str, grant_event_id: str | None,
                         environment: str = "ISOLATED") -> dict:
        """The whole COLLECT_EVENT, ready for the case store. The guard writes nothing."""
        event = {
            "pse_version": "pse-event-0.1",
            "derived_from": "zmeta-event-1.0",
            "case_id": case_id,
            "event": {"event_id": event_id, "event_type": "COLLECT_EVENT",
                      "event_subtype": self.value, "ts": ts},
            "source": {"platform_id": platform_id, "environment": environment,
                       "producer": PRODUCER, "sw_version": sw_version},
            "payload": self.to_collect_payload(),
        }
        parents = [p for p in (grant_event_id, self.motivated_by) if p]
        if parents:
            event["lineage"] = {"based_on": parents, "transform": None}
        return event


# ---------------------------------------------------------------------------
# The compiled policy, read by name. Any name it no longer carries refuses.
# ---------------------------------------------------------------------------


class PolicyUnreadable(Exception):
    pass


def _yaml_load(path: Path):
    import yaml  # PyYAML; imported here so importing this module reads nothing

    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


class Policy:
    """policy/subject-authorization.yaml, with the accessors evaluate() uses."""

    def __init__(self, doc: Mapping, rt_criteria: list):
        try:
            sa = doc["subject_authorization"]
            gate = sa["gate"]
            self.values = list(gate["values"]["enum"])
            self.members = {m["value"]: m for m in gate["values"]["members"]}
            permits = [v for v, m in self.members.items() if m.get("stops_the_run") is False]
            if len(permits) != 1 or set(self.members) != set(self.values):
                raise PolicyUnreadable("the gate's values do not name exactly one permitting value")
            self.permit = permits[0]
            self.steps = {int(s["step"]): s for s in gate["evaluation_order"]["steps"]}
            if sorted(self.steps) != list(EVALUATION_STEPS) or any(
                    s.get("returns") not in self.values for s in self.steps.values()):
                raise PolicyUnreadable("the evaluation order is not SS-8's six steps, each returning a gate value")
            self.out_of_band = list(gate["evaluation_order"].get("out_of_band") or [])
            self.classes = {c["id"]: c for c in sa["classes"]["members"]}
            self.authorizable = list(sa["authorizable_subject_class"]["enum"])
            self.dispositions = list(sa["bystanders"]["dispositions"]["enum"])
            self.record_fields = [f["field"] for f in sa["record"]["required_fields"]]
            self.record_deps = {f["field"]: list(f.get("unratified_dependencies") or [])
                                for f in sa["record"]["required_fields"]}
            self.never6 = next(i for i in sa["never"]["items"] if i["item"] == 6)
            rbc = sa["ratify_before_collection"]
            self.ratify_paths = [p for item in rbc["items"] for p in item["paths"]]
            self.ratify_refuses = rbc["refuses"]
            self.entries = {e["id"]: e for e in sa["unratified"]["entries"]}
            self.ss_criteria = [str(c) for c in sa["compiles_criteria"]]
            self.rt_criteria = [str(c) for c in rt_criteria]
            if len(self.ratify_paths) != int(rbc["path_count"]) or not self.rt_criteria:
                raise PolicyUnreadable("the ratify-before-collection list or the RT criteria do not read")
        except PolicyUnreadable:
            raise
        except (KeyError, TypeError, ValueError, StopIteration, AttributeError) as exc:
            raise PolicyUnreadable(exc.__class__.__name__) from None

    def value_of(self, step: int) -> str:
        v = self.steps[step]["returns"]
        if v not in self.values:
            raise PolicyUnreadable(f"step {step} returns a value outside the gate enum")
        return v

    def basis_for(self, step: int, basis: str) -> tuple[str, str]:
        s = self.steps[step]
        allowed = s["basis"] if isinstance(s["basis"], list) else [s["basis"]]
        if basis not in allowed:
            raise PolicyUnreadable(f"step {step} no longer carries the basis this module reads")
        return s["basis_field"], basis

    def deps(self, step: int) -> list:
        return list(self.steps[step].get("unratified_dependencies") or [])

    def entry_sentence(self, entry_id: str) -> str:
        """The entry's own refusal sentence: the policy's, or this module's for GF-U2 and GF-U4."""
        local = {"GF-U2": INCIDENTAL_ORIGIN, "GF-U4": PIVOT_HELD}
        if entry_id in local:
            return local[entry_id]
        try:
            return self.entries[entry_id]["refuses"]
        except (KeyError, TypeError):
            raise PolicyUnreadable(f"no unratified entry {entry_id} to render") from None


def load_policy() -> Policy:
    """Read both compiled policies. Raises PolicyUnreadable on any defect."""
    try:
        doc = _yaml_load(POLICY)
        rt = _yaml_load(RETENTION_POLICY)["retention"]["ratification"]["criteria_compiled_here"]
    except PolicyUnreadable:
        raise
    except Exception as exc:  # a missing reader, file or key is a refusal, never a pass
        raise PolicyUnreadable(exc.__class__.__name__) from None
    return Policy(doc, rt)


# ---------------------------------------------------------------------------
# The pin of record, read through the one reader the gates share.
# ---------------------------------------------------------------------------


def _load_by_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LivePin:
    """doctrine/DOCTRINE_STATUS.md as tools/pin_of_record.py reads it."""

    def __init__(self, text: str | None = None, root: Path = ROOT):
        self.reader = _load_by_path("plainsight_pin_of_record", PIN_READER)
        self.text = self.reader.PIN.read_text(encoding="utf-8") if text is None else text
        self.pin = self.reader.Pin(self.text, root, {k: set(v) for k, v in RATIFY_SECTIONS.items()})
        self.readable = bool(self.pin.parsed)

    def item_6_reasons(self, paths: list, criteria: list) -> list:
        """Why SS-14 item 6 refuses, value-free, or an empty list."""
        out = [f"{p} is unstamped: {self.pin.reason_unstamped(p)}" for p in paths
               if not self.pin.artifact_stamped(p)]
        if CAST_PATH in paths and self.pin.artifact_stamped(CAST_PATH):
            seal = cast_seal_reason()
            if seal:
                out.append(f"{CAST_PATH} is stamped and {seal}")
        out += [f"criterion {c} does not bind in the pin of record" for c in criteria
                if not self.pin.criterion_stamped(c)]
        return out

    def entry_resolved(self, entry_id: str) -> bool:
        """SG-R9. A dated, unwithdrawn Ratified row naming the entry and its file."""
        r = self.reader
        holder = ENTRY_HOLDER.get(entry_id.split("-")[0], "")
        for cells in r._table_rows(r._slice(self.text, r.RATIFIED_START, r.RATIFIED_END)):
            if len(cells) != 6 or any(r.WITHDRAWN_RE.search(c) for c in cells):
                continue
            m = ENTRY_RE.match(cells[0].strip())
            if not m or m.group(1) != entry_id:
                continue
            if f"`{holder}`" not in cells[1]:
                continue
            if r._conclusion_date(cells[3]) and cells[5].strip().lower() in r.RATIFIERS:
                return True
        return False


def cast_seal_reason() -> str:
    """'' when the cast is sealed, its hash verifies and it carries a confuser pair."""
    try:
        vc = _load_by_path("plainsight_validate_cast", CAST_READER)
        raw = vc.CAST.read_text(encoding="utf-8")
        import yaml

        model = yaml.safe_load(raw)
    except Exception as exc:
        return f"the cast could not be read ({exc.__class__.__name__})"
    if not isinstance(model, dict) or not vc.is_sealed(model):
        return "the cast is not sealed"
    if vc.check_seal_fields(model) or vc.check_seal_hash(model, raw):
        return "the cast's seal or its recorded hash does not verify"
    if any(f.code in CONFUSER_CODES for f in vc.check_structure(model)):
        return "the cast carries no valid designed confuser pair"
    return ""


def read_stamps():
    """The live pin. The test suite replaces this function; a caller never does."""
    return LivePin()


# ---------------------------------------------------------------------------
# evaluate()
# ---------------------------------------------------------------------------


def _selectors(record: Mapping) -> list | None:
    sels = record.get("selectors")
    if not isinstance(sels, list) or not sels:
        return None
    out = []
    for s in sels:
        if not isinstance(s, Mapping) or set(s) != {"selector_type", "value"}:
            return None
        out.append((s["selector_type"], s["value"]))
    return out


def _disposition(block) -> tuple[str | None, str]:
    """(payload disposition, '') or (None, refusal basis). SS-10, SG-R11."""
    if not isinstance(block, Mapping) or "reach" not in block:
        return None, "bystander_undeclared"
    reach, classes = block.get("reach"), block.get("classes")
    if reach == "named_selector_only" and classes is None:
        return "refuse", ""
    if reach != "declared" or not isinstance(classes, list) or not classes:
        return None, "bystander_undeclared"
    found = []
    for c in classes:
        if not isinstance(c, Mapping) or "disposition" not in c or "class" not in c:
            return None, "bystander_undeclared"
        found.append(c["disposition"])
    return found, ""


def _blank(v) -> bool:
    return v is None or (isinstance(v, str) and not v.strip())


def evaluate(request: Request) -> Decision:
    """The gate. Never raises for a well-formed Request; every failure refuses."""
    common = {"connector_id": request.connector_id or "",
              "target_selector_type": request.selector_type or "",
              "authorization_ref": request.authorization_ref or None}

    def refuse(consequence, **kw) -> Decision:
        return Decision(value=kw.pop("value", "REFUSED"), permits=False,
                        consequence=consequence, **common, **kw)

    try:
        pol = load_policy()
    except PolicyUnreadable as exc:
        return refuse(POLICY_UNREADABLE, reasons=(f"policy unreadable: {exc}",))

    try:
        return _evaluate(request, pol, common)
    except PolicyUnreadable as exc:
        return refuse(POLICY_UNREADABLE, reasons=(f"policy drift: {exc}",))
    except Exception as exc:  # a gate that raises has decided nothing, so it refuses
        return refuse(GUARD_FAULT, reasons=(f"the gate raised {exc.__class__.__name__}",))


def _evaluate(rq: Request, pol: Policy, common: dict) -> Decision:
    refused_value = pol.value_of(1)

    def stop(step, basis, consequence, *, code=None, held=(), reasons=(), never_item=None,
             relation=None, depth=None):
        value = pol.value_of(step) if step is not None else refused_value
        basis_field = None
        if basis is not None and step is not None:
            basis_field, basis = pol.basis_for(step, basis)
        elif basis is not None:
            basis_field = "refusal_basis"
        kw = {}
        if value != refused_value:
            kw = {"subject_relation": relation, "pivot_depth": depth, "motivated_by": rq.motivated_by}
        return Decision(value=value, permits=False, consequence=consequence,
                        decided_at_step=step, basis_field=basis_field, basis=basis,
                        never_item=never_item, code=code, held_on=tuple(held),
                        reasons=tuple(reasons), **common, **kw)

    sa_u1 = pol.entry_sentence("SA-U1")

    # 1. The NEVER list: item 6, read from the pin of record.
    try:
        stamps = read_stamps()
        readable = bool(stamps.readable)
    except Exception as exc:  # SA-U15: a pin that cannot be read refuses
        stamps, readable = None, False
        unread = exc.__class__.__name__
    else:
        unread = "the pin did not parse into its three tables"
    if not readable:
        return stop(1, "never_item", pol.entry_sentence("SA-U15"), never_item=6,
                    held=("SA-U15",), reasons=(f"pin of record unreadable: {unread}",))
    reasons = list(stamps.item_6_reasons(pol.ratify_paths, pol.ss_criteria + pol.rt_criteria))
    if not rq.preflight_passed:
        reasons.append("preflight has not passed in this runner process")
    if reasons:
        return stop(1, "never_item", pol.ratify_refuses, never_item=6, reasons=reasons,
                    code=pol.steps[1].get("code"))

    # The incidental rule (SS-10), unplaced by SS-8 (GF-U2, SG-R2).
    if rq.subject_class in pol.classes and pol.classes[rq.subject_class].get("authorizable") is False \
            or any(h.relation == "incidental" for h in rq.chain):
        return stop(None, None, INCIDENTAL_ORIGIN, code="SUBJECT_NOT_AUTHORIZED", held=("GF-U2",),
                    reasons=("an incidental selector reached the dispatch",))

    # 2. The record: present, this case, this class, complete, unexpired.
    rec = rq.authorization
    code2 = pol.steps[2].get("code")
    held2 = ("SA-U1",)
    if not isinstance(rec, Mapping) or _blank(rq.authorization_ref):
        return stop(2, "authorization_missing", sa_u1, code=code2, held=held2,
                    reasons=("no authorization record reached the gate",))
    if rec.get("case_id") != rq.case_id or rec.get("subject_class") != rq.subject_class:
        return stop(2, "authorization_missing", sa_u1, code=code2, held=held2,
                    reasons=("no record covers this selector for this case and the class claimed (SG-R3)",))
    missing = [f for f in pol.record_fields if f not in rec]
    if missing:
        return stop(2, "authorization_incomplete", sa_u1, code=code2, held=held2,
                    reasons=(f"the record lacks {', '.join(missing)}",))
    if _blank(rec.get("purpose")):
        return stop(None, "purpose_unbound", uncompiled_sentence("purpose_unbound"),
                    code="CASE_PURPOSE_UNBOUND", held=("GF-U3", "GF-U5"),
                    reasons=("the record carries no bound purpose",))
    seeds = _selectors(rec)
    depth_max = rec.get("pivot_depth_max")
    try:
        expires = _dt.date.fromisoformat(str(rec.get("expires_on")))
    except ValueError:
        expires = None
    blanks = [f for f in pol.record_fields if _blank(rec.get(f))]
    if seeds is None or expires is None or blanks or isinstance(depth_max, bool) \
            or not isinstance(depth_max, int) or depth_max < 0:
        return stop(2, "authorization_incomplete", sa_u1, code=code2, held=held2,
                    reasons=("a required field is blank or malformed",))
    today = rq.clock.astimezone(_dt.timezone.utc).date()
    if expires < today:
        return stop(2, "authorization_expired", sa_u1, code=code2, held=held2,
                    reasons=("expires_on precedes the UTC date of the clock",))
    if expires == today:
        return stop(2, "authorization_expired", pol.entry_sentence("SA-U3"), code=code2,
                    held=("SA-U3", "SA-U1"), reasons=("expires_on is the UTC date of the clock (SG-R4)",))

    # 3. The class, and SS-17's baseline.
    member = pol.classes.get(rq.subject_class)
    if rq.subject_class not in pol.authorizable or member is None \
            or not str(member.get("v0_1", "")).startswith("available"):
        return stop(3, "class_unavailable", pol.members[refused_value]["consequence"],
                    code=pol.steps[3].get("code"), reasons=("the class is not available at v0.1",))
    if "baseline_scorecard_exists" in (member.get("conditions") or []):
        return stop(3, "baseline_missing", pol.entry_sentence("SA-U6"), code=pol.steps[3].get("code"),
                    held=("SA-U6", "SA-U7", "SA-U1"), reasons=("no object satisfies SS-17 while SA-U6 is open (SG-R5)",))
    if rq.subject_class in OPTION_BLIND_CLASSES:
        held3 = OPTION_BLIND_CLASSES[rq.subject_class]
        return stop(3, "class_unavailable", pol.entry_sentence(held3[0]), code=pol.steps[3].get("code"),
                    held=held3, reasons=(f"this guard implements no option of {', '.join(held3)}, so a dated row "
                                         "for it cannot unlock the class (SG-R17)",))

    # 4. The selector: a seed in the set, or a pivot inside pivot_depth_max.
    target = (rq.selector_type, rq.selector)
    extension = pol.members[pol.value_of(4)]["consequence"]
    if not rq.chain:
        relation, depth = "seed", 0
        if target not in seeds:
            return stop(4, "selector_outside_set", extension, code=pol.steps[4].get("code"),
                        relation=relation, depth=depth, reasons=("the seed is not in the record's selectors",))
    else:
        relation, depth = "pivot", len(rq.chain)
        origin = rq.chain[0]
        if (origin.selector_type, origin.selector) not in seeds:
            return stop(4, "selector_outside_set", extension, code=pol.steps[4].get("code"),
                        relation=relation, depth=depth, reasons=("the chain does not start at an authorized seed",))
        if depth >= depth_max:
            return stop(4, "pivot_depth_exceeded", extension, code=pol.steps[4].get("code"),
                        relation=relation, depth=depth, held=("GF-U4",) if depth == depth_max else (),
                        reasons=("the pivot is at or beyond pivot_depth_max (SG-R6)",))

        # 5. The composed chain: every hop after the seed is adjudicated.
        hops = [(h.adjudication_ref, h.motivated_by) for h in rq.chain[1:]]
        hops.append((rq.adjudication_ref, rq.motivated_by))
        if any(_blank(adj) or _blank(claim) for adj, claim in hops):
            return stop(5, "chain_scope_drift", pol.members[pol.value_of(5)]["consequence"],
                        code=pol.steps[5].get("code"), relation=relation, depth=depth, held=("GF-U4",),
                        reasons=("a hop in the chain carries no adjudication or no motivating claim (SG-R7)",))

    # 6. The bystander declaration, against the closed disposition set.
    found, why = _disposition(rq.bystanders)
    if why:
        return stop(6, why, uncompiled_sentence(why), code=pol.steps[6].get("code"), held=("GF-U5",),
                    reasons=("the connector declares no bystanders block",))
    if isinstance(found, list):
        if any(d not in pol.dispositions for d in found):
            return stop(6, "disposition_out_of_set", uncompiled_sentence("disposition_out_of_set"),
                        code=pol.steps[6].get("code"), held=("GF-U5",),
                        reasons=("a bystander disposition is outside the closed set",))
        disposition = "count_only" if "count_only" in found else found[0]
    else:
        disposition = found
    if disposition not in pol.dispositions:
        raise PolicyUnreadable("the disposition SG-R11 records is outside the compiled set")

    # SS-12, out of band: the estimate on every dispatch (SG-R8).
    est, why_est = rq.incidental_estimate, rq.incidental_estimate_reason
    estimate_ok = (isinstance(est, int) and not isinstance(est, bool) and est >= 0) or (
        est == "unestimable" and not _blank(why_est))
    oob = next((o for o in pol.out_of_band if o.get("basis") == "incidental_estimate_missing"), None)
    if oob is None:
        raise PolicyUnreadable("the out-of-band estimate check is gone")
    if not estimate_ok:
        return stop(None, "incidental_estimate_missing", uncompiled_sentence("incidental_estimate_missing"),
                    code=oob.get("code"), held=tuple(oob.get("unratified_dependencies") or ()),
                    reasons=("the pre-flight record carries no usable estimate",))

    # The binding read: every entry the permit path passed through is stamped.
    deps: list = list(pol.never6.get("unratified_dependencies") or [])
    for step in sorted(pol.steps):
        if step >= 2:
            deps += pol.deps(step)
    deps += list(oob.get("unratified_dependencies") or [])
    deps += list(member.get("unratified_dependencies") or [])
    for f in pol.record_fields:
        deps += pol.record_deps.get(f, [])
    if relation == "pivot":
        deps += list(PIVOT_ENTRIES)
    open_entries = [e for e in dict.fromkeys(deps) if not stamps.entry_resolved(e)]
    if open_entries:
        return stop(None, None, pol.entry_sentence(open_entries[0]), held=open_entries,
                    reasons=tuple(f"{e} carries no dated row in the pin of record" for e in open_entries))

    return Decision(value=pol.permit, permits=True, consequence=pol.members[pol.permit]["consequence"],
                    decided_at_step=max(pol.steps), subject_relation=relation, pivot_depth=depth,
                    motivated_by=rq.motivated_by, incidental_estimate=est,
                    incidental_estimate_reason=why_est if est == "unestimable" else None,
                    bystander_disposition=disposition, **common)
