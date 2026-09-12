#!/usr/bin/env python3
"""Subject authorization gate: the Step 8 half of the D5 mechanism.

`doctrine/SUBJECT_SELECTION.md` SS-5 exists because of a measured defect. In
`zisr-recon`'s `guard.py` as measured on 2026-08-26, `scope` was declared,
required and printed, and `check()` never read it, so a complete authorization
permitted every non-NEVER address on earth. `expires_on` did not exist at all.
The criterion that followed is the one this tool serves: for each of `selectors`,
`pivot_depth_max` and `expires_on`, `conformance/gate/*.jsonl` carries a fixture
identical to a passing fixture except in that one field, and that fixture is
refused. A field that no fixture can make refuse is not being read, whatever the
code looks like, and `tools/validate_authorization.py --fixtures` fails if any of
the three is missing.

Three artifacts landed at Step 8 and none of them can check itself.
`policy/subject-authorization.yaml` is the compiled subject doctrine,
`schema/subject-authorization.schema.json` refuses a record outside it, and
`conformance/gate/*.jsonl` asserts what the gate returns. Each names this file as
its self-lint. Two of the three are hand-authored Class F artifacts with no
generator and therefore no byte-for-byte drift check, so the reconciles below are
what stands in for one.

WHAT THIS GATE REFUSES TODAY, AND WHY THAT IS THE FEATURE. `--fixtures` refuses.
`doctrine/DOCTRINE_STATUS.md` is the pin of record: mechanisms read it rather
than the document they enforce, and an unratified criterion refuses rather than
permits. Six of the nine paths SS-14 item 6 names carry no dated row, nineteen of
the twenty-one corpus rows are held on an unratified entry, and where the gate's
decision function lives is itself undecided (VA-U1 below). A green run against
that state would claim a gate was proven. The checks still run, the stamp
predicate still refuses, and the certification is refused separately from any
defect, so the two states stay distinguishable.

Every check guards a specific defect:

  A-01  A corpus row whose key set is not the twelve the row contract fixes. A
        thirteenth key is an assertion nothing grades; a missing key is an input
        the gate reads that the fixture never supplied.
  A-02  A row asserting nothing: no decision value, no violation code, and no
        held entry. It passes every grader by carrying no claim.
  A-03  `expect_only` absent or false. docs/THE-GAMEPLAN.md section 2.4 requires
        it on every D5 fixture, and without it a fixture passes on a code it
        never claimed to exercise.
  A-04  A decision value outside the closed gate enum, a `decided_at_step`
        outside its enum, a `subject_relation` outside SS-10's computed column, a
        basis outside the closed `refusal_basis` or `extension_basis` set, or a
        basis recorded under a third basis field the wire record does not carry.
        The wire record carries the assertion, so a token nothing declares makes
        the fixture ungradable rather than wrong.
  A-05  A violation code the generated vocabulary does not declare. A gate
        emitting an undeclared code emits a string, and nothing downstream can
        route it.
  A-06  An assertion half-written on a row that is not held: a refusal with no
        step, no basis, or no rendered consequence, and no unratified entry
        naming the reason. A held row asserting less is honest; an unheld one is
        a gap wearing a fixture.
  A-07  A rendered consequence that is not the sentence the policy compiles for
        that value. CLAUDE.md section 4 renders a state as its consequence, and a
        fixture inventing its own sentence proves the gate against prose nobody
        ratified.
  A-08  A selector-shaped value that is not a bracketed placeholder. SS-14 item 5
        keeps a natural person's selector out of every tracked file, and a
        synthetic value is still a value. This is the rule
        `tools/validate_cast.py --placeholder-scan` already applies to the truth
        file, applied to the one corpus that carries authorization records.
  A-09  A `pending` entry naming no unratified entry in
        `policy/subject-authorization.yaml` or `conformance/gate/README.md`. A
        row held on an entry that does not exist is held forever and reads as
        scheduled.
  A-10  An authorization record missing one of SS-4's nine fields, or carrying a
        field the schema's closed property set does not declare. SS-4 refuses a
        partial authorization rather than half-honouring it, and the schema sets
        `additionalProperties` false, so drift in either direction makes the
        corpus records not instances of the schema they are graded against.
  A-11  A record naming a subject class outside the authorizable enum. S5 is in
        SS-1's class set and is not in this one, because SS-1 marks it not
        authorizable and SS-4 excludes it from the field.
  A-12  One of SS-5's three fields with no refusing fixture, or a fixture that
        differs from its baseline in more than the field it names. Both halves
        matter: a missing fixture leaves the field unproven, and a fixture that
        changes two fields cannot show which one the gate read.
  A-13  A corpus row absent from the register in `conformance/gate/README.md`
        section 4, or a register row absent from the corpus. One direction finds
        half the drift, which is the lesson D-01 recorded. Two rows sharing one
        name is the adjacent case: a reconcile keyed on the name reads one row as
        covering both, and a criterion is proven by whichever row the grader
        reached last.
  A-14  A fixture name `spec/layer-model.yaml` reserves for this corpus that is
        missing, or present with a code or an `expect_only` other than the one
        the fixture map reserves. Rank 3 owns those three names.
  A-15  The authorizable `subject_class` enum drifting between
        `policy/subject-authorization.yaml`, which SS-1 makes the source, the
        schema that refuses a value outside it, and the rank 3 mirror that
        declares itself a mirror. Widening any one of the three widens who may be
        a subject, and a drift between them passes both other validators.
  A-16  The gate value enum or the bystander disposition set drifting from the
        rank 3 mirror, or `retain` appearing in the disposition enum rather than
        in the refused list. CLAUDE.md gate 2 names a bystander disposition of
        `retain` as a one-line diff that widens who is collected on while reading
        as Class B.
  A-17  A criterion the policy compiles that carries no row in the pin of
        record's per-criterion table, or whose file carries no dated ratifier
        row. A criterion with no row refuses, so the table is the mechanism
        rather than an index of one.
  A-18  A row asserting the SS-14 item 6 refusal whose declared stamp state does
        not actually produce it. This is the SS-5 lesson applied to the stamp
        read: a fixture asserting a refusal the predicate does not reach proves
        the assertion rather than the mechanism.
  A-19  **The check Step 8's done-condition names.** A criterion absent from the
        stamp table, or an artifact with no dated row, must refuse rather than
        permit. The test constructs the absence rather than finding one, and it
        carries its own matched pair: a fully stamped state must permit, because
        a predicate that refuses everything proves nothing and is the failure
        direction HY-2 adjudicates.
  A-20  The compiled SS-14 counts drifting: six NEVER items, eight
        ratify-before-collection items across nine paths, and four preflight
        checks. An absolute prohibition whose content can change by editing a
        list is not absolute.
  A-21  An unratified entry that is not usable as a refusal: no question, no
        options, no statement of what it blocks, or a `refuses` value that is a
        bare token rather than a rendered consequence. An operator cannot act on
        the string "unratified".

Modes:

  --fixtures  Grade `conformance/gate/*.jsonl` against the compiled policy, the
        schema, the rank 3 mirror and the pin of record, then refuse the
        certification while any row is held or any artifact is unstamped. The
        A-19 result is reported separately from the certification, because the
        mechanism being green and the corpus being certifiable are two different
        facts.
  --dispatch-paths  DEFERRED. SS-6's subject is `runner/`, which is empty, and
        `runner/subject_guard.py` is Step 10. A scan over an empty directory
        finds zero ungated call sites and exits clean, which would make
        docs/THE-GAMEPLAN.md's public claim true by construction while nothing is
        gated. The mode says what it will check and which step delivers it.
  --disjointness  DEFERRED. SS-20 and CR-1 name this tool as the mechanism that
        compares the credential pool against `synthetic/CAST.md` and refuses on
        any intersection, including a shared recovery selector.
        `tools/validate_cast.py` prints that claim on every clean run. The pool
        never exists on LOCAL under EG-4 and CR-4, and no pool inventory artifact
        exists anywhere, so the mode names the gap rather than inheriting a claim
        it cannot meet.
  --self-test  Mutate the loaded artifacts in memory and assert each defect is
        refused. A gate nobody has watched fail is an assumption
        (doctrine/HYGIENE.md section 2).

WHAT --self-test DOES NOT COVER, SAID HERE RATHER THAN LEFT TO BE NOTICED. Ten
codes are not reachable by mutating the loaded artifacts, and each one is in one
of three groups. Five are loader refusals that fire before a model exists:
AUTH_YAML_READER_MISSING, AUTH_INPUT_UNREADABLE, AUTH_INPUT_UNPARSEABLE,
AUTH_POLICY_WRAPPER_KEY_MISSING and AUTH_CORPUS_EMPTY, each exercised by pointing
the module's paths at a file that is not there. Three are the certification
refusals, AUTH_CERTIFICATION_HELD, AUTH_ARTIFACT_UNSTAMPED and
AUTH_EVALUATOR_UNRATIFIED, which fire on the real tree today and are the designed
state rather than a defect. Two guard the stamp predicate against itself,
AUTH_UNRATIFIED_ARTIFACT_PERMITTED and AUTH_STAMP_PREDICATE_ALWAYS_REFUSES, and
they are constructed rather than mutated: their inputs are built inside the check
from the policy's own path list, so no artifact edit can reach them and running
them is the whole of their evidence.

Exit codes: 0 clean, 1 violations found, 2 a governed input could not be read.

One deliberate departure from --quiet, on the `tools/validate_cast.py`
precedent. The unratified state prints even under --quiet, because it is neither
a pass nor a failure of the corpus, and CLAUDE.md section 4 requires a state to
render as its consequence rather than as its token.

Class F. This tool is drafted by an agent and decided by nobody but the operator.
It mints no violation code, widens no enum, and writes no value where doctrine
does not decide one. Four questions it cannot answer are carried below as VA-U1
to VA-U4, each with the question, the legal options and the sentence this tool
renders when it reaches one.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path

try:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import gate_log
except Exception:  # telemetry must never be able to break a gate
    gate_log = None

try:
    import yaml
except Exception:  # reported as a named refusal, never as a traceback
    yaml = None

ROOT = Path(__file__).resolve().parents[1]

POLICY = ROOT / "policy" / "subject-authorization.yaml"
SCHEMA = ROOT / "schema" / "subject-authorization.schema.json"
CORPUS_DIR = ROOT / "conformance" / "gate"
REGISTER = CORPUS_DIR / "README.md"
LAYER_MODEL = ROOT / "spec" / "layer-model.yaml"
CODE_VOCABULARY = ROOT / "policy" / "violation-codes.yaml"
PIN = ROOT / "doctrine" / "DOCTRINE_STATUS.md"
RUNNER = ROOT / "runner"
ALLOWLIST = RUNNER / "dispatch_allowlist.yaml"

REL = {
    POLICY: "policy/subject-authorization.yaml",
    SCHEMA: "schema/subject-authorization.schema.json",
    REGISTER: "conformance/gate/README.md",
    LAYER_MODEL: "spec/layer-model.yaml",
    CODE_VOCABULARY: "policy/violation-codes.yaml",
    PIN: "doctrine/DOCTRINE_STATUS.md",
}

#: The gate token. One token per tool, matching every sibling and matching the
#: PENDING entry `tools/validate_conformance.py` already carries under this
#: name. HY-1 fixes `code` as the violation code, so a mode cannot ride there.
GATE = "authorization"

# ---------------------------------------------------------------------------
# Constants pinning a doctrine value. Each carries the criterion that decided
# it. A diff to one of these is a diff to the doctrine it compiles, and the
# refusal it produces says which dated stamp has to move with it.
# ---------------------------------------------------------------------------

#: SS-4. The nine required fields of the authorization record, in the order the
#: criterion's table lists them. A record missing one is refused rather than
#: half-honoured.
RECORD_FIELDS = (
    "case_id",
    "subject_class",
    "selectors",
    "pivot_depth_max",
    "purpose",
    "evidence_ref",
    "authorized_by",
    "authorized_on",
    "expires_on",
)

#: SS-5. The three fields a fixture must be able to make refuse. This is the
#: single most load-bearing line in the subject doctrine and the reason this
#: tool exists before the runner does.
SS5_FIELDS = ("selectors", "pivot_depth_max", "expires_on")

#: SS-1 and SS-4. The authorizable class set, which is SS-1's class set minus
#: S5. Widening it is Class F by effect whatever the diff looks like.
AUTHORIZABLE_CLASSES = ("S0", "S1", "S2", "S3", "S4", "N0", "L0")
NOT_AUTHORIZABLE = ("S5",)

#: SS-7 and R8, in the uppercase rank 3 form already shipped on the wire.
GATE_VALUES = ("PERMITTED", "REQUIRES_EXTENSION", "REFUSED")
DISPOSITIONS = ("count_only", "refuse")
DISPOSITIONS_REFUSED = ("retain",)

#: SS-14. Six NEVER items, eight ratify-before-collection items across nine
#: paths, and four preflight checks that are not stampable.
NEVER_ITEM_COUNT = 6
RATIFY_ITEM_COUNT = 8
RATIFY_PATH_COUNT = 9
PREFLIGHT_CHECK_COUNT = 4

#: SS-8. The evaluation order is six steps and the wire enum is 1 to 6.
EVALUATION_STEPS = (1, 2, 3, 4, 5, 6)

#: The row contract fixed by conformance/gate/README.md section 3.
ROW_KEYS = (
    "name",
    "description",
    "criterion",
    "expect_decision",
    "expect_code",
    "expect_only",
    "pending",
    "evaluated_at",
    "authorization",
    "given",
    "chain",
    "dispatch",
)
DECISION_KEYS = (
    "value",
    "decided_at_step",
    "subject_relation",
    "pivot_depth",
    "basis_field",
    "basis",
    "never_item",
)
GIVEN_KEYS = (
    "stamp_state",
    "manifest",
    "baseline",
    "preflight",
    "environment",
    "collected_content",
)

#: Keys whose value is a selector. Extends the tuple
#: `tools/validate_cast.py` scans, with the two keys this corpus adds.
SELECTOR_KEYS = (
    "handle",
    "platform_uid",
    "display_name",
    "profile_image",
    "phone",
    "phone_source",
    "email",
    "value",
    "target_selector",
    "selector_value",
)
PLACEHOLDER_RE = re.compile(r"^<[^<>]+>$")

#: Criterion namespaces and the file whose dated ratifier row stamps them.
NAMESPACE_FILE = {
    "SS": "doctrine/SUBJECT_SELECTION.md",
    "RT": "doctrine/RETENTION.md",
    "EG": "doctrine/EGRESS.md",
    "CR": "doctrine/CREDENTIAL_LIFECYCLE.md",
    "HY": "doctrine/HYGIENE.md",
}

CRITERION_RE = re.compile(r"\b((?:SS|RT|EG|CR|HY)-\d+)\b")
PENDING_ID_RE = re.compile(r"^(?:SA|SAS|GF|VA)-U\d+$")
DATE_RE = re.compile(r"\b(?:19|20)\d{2}-\d{2}-\d{2}\b")
PIN_PATH_RE = re.compile(r"`([A-Za-z0-9_./-]+\.(?:md|ya?ml|json|py))`")
REGISTER_NAME_RE = re.compile(r"^\|\s*`([a-z0-9][a-z0-9-]*)`\s*\|", re.M)
GF_ENTRY_RE = re.compile(r"^### (GF-U\d+)\.", re.M)

# ---------------------------------------------------------------------------
# The unratified questions this tool cannot answer. Each entry carries the
# question, the legal options with their costs, what it blocks, and the
# sentence rendered when a caller reaches it. None carries a default. An entry
# is resolved by a dated row in doctrine/DOCTRINE_STATUS.md naming its id,
# authored by the ratifier, at which point the behaviour it holds is written
# here in the same commit.
# ---------------------------------------------------------------------------

UNRATIFIED = {
    "VA-U1": {
        "change_class": "F",
        "question": (
            "Does --fixtures evaluate a real gate, or grade a corpus against the "
            "compiled policy? SS-5 says a fixture must be refused and SS-8 says a "
            "matched pair is asserted refused and asserted permitted, so something "
            "has to return a decision, and runner/subject_guard.evaluate() is Step 10."
        ),
        "options": (
            "The evaluator lives in this tool at Step 8 and the runner imports it at "
            "Step 10: one implementation, tested before it is wired, and a tools/ "
            "module on the dispatch path.",
            "Two implementations graded by the same fixtures, which is the drift the "
            "bidirectional reconciles exist to prevent.",
            "Membership and wire-form grading at Step 8 with decision-level assertion "
            "at Step 10, which makes the register row's claim that this mode proves the "
            "gate refuses false until then.",
        ),
        "blocks": (
            "decision-level certification of conformance/gate/*.jsonl",
            "the register's claim that --fixtures proves the gate refuses",
        ),
        "refuses": (
            "REFUSED PENDING RATIFICATION\n"
            "  where: tools/validate_authorization.py unratified VA-U1\n"
            "  what:  the corpus was asked to certify what the gate returns and no\n"
            "         ratified evaluator exists to ask. This mode grades the wire form,\n"
            "         the enums, the record shape and the stamp read, and it does not\n"
            "         produce a decision, so a green run here would not mean the gate\n"
            "         refuses\n"
            "  moves: stamp one of the three options in doctrine/DOCTRINE_STATUS.md and\n"
            "         land the evaluator where it names; or wait for Step 10, which\n"
            "         delivers runner/subject_guard.py; or certify nothing, which is what\n"
            "         this refusal is holding"
        ),
    },
    "VA-U2": {
        "change_class": "B",
        "question": (
            "Can --dispatch-paths mean anything at Step 8, when runner/ is empty, "
            "runner/subject_guard.py is Step 10 and runner/dispatch_allowlist.yaml does "
            "not exist?"
        ),
        "options": (
            "Refuse while runner/ is empty, saying the gate cannot be proven, which "
            "keeps preflight red until Step 10 and means this mode is never green at "
            "Step 8.",
            "Return 0 with a DEFERRED notice naming Step 10, on the "
            "tools/validate_ontology.py precedent, with the kernel gate entry left "
            "PENDING.",
            "Refuse specifically on the absence of runner/dispatch_allowlist.yaml, "
            "which is item 8 of SS-14's list and can exist before subject_guard.py does.",
        ),
        "blocks": (
            "the SS-6 proof that nothing reaches argv, a subscription or the credential "
            "pool around the gate",
            "one of SS-14 item 6's four preflight checks",
        ),
        "refuses": (
            "REFUSED PENDING RATIFICATION\n"
            "  where: tools/validate_authorization.py unratified VA-U2\n"
            "  what:  --dispatch-paths was asked to prove that every dispatching call\n"
            "         site is reached through the gate, and runner/ holds no call sites\n"
            "         to scan. A clean result over an empty directory would report the\n"
            "         SS-6 property as proven while nothing is gated\n"
            "  moves: stamp one of the three options in doctrine/DOCTRINE_STATUS.md; or\n"
            "         land Step 10, which delivers the dispatch path this mode reads; or\n"
            "         treat this mode as not passed, which is what the DEFERRED notice\n"
            "         says"
        ),
    },
    "VA-U3": {
        "change_class": "B",
        "question": (
            "By what mechanism does --dispatch-paths detect a call site that constructs "
            "argv, opens a subscription, or draws from the credential pool? SS-6 names "
            "the three act classes and the two legal outcomes, and no doctrine names a "
            "detection technique."
        ),
        "options": (
            "An AST walk requiring each dispatching function to be dominated by a "
            "subject_guard.evaluate() call.",
            "A regex over declared call tokens, defeated by any indirection.",
            "A declaration-based reconcile against runner/dispatch_allowlist.yaml in "
            "both directions, which moves the trust to the declaration.",
        ),
        "blocks": ("the implementation of --dispatch-paths",),
        "refuses": (
            "REFUSED PENDING RATIFICATION\n"
            "  where: tools/validate_authorization.py unratified VA-U3\n"
            "  what:  the detection method for an ungated dispatch is undecided, and the\n"
            "         method fixes the false-negative rate of the one check SS-6 exists\n"
            "         to be. SS-6 records that retrofitting a gate onto a path with\n"
            "         fifteen call sites is how fourteen end up ungated, so the method\n"
            "         is chosen before the call sites exist\n"
            "  moves: stamp one of the three options in doctrine/DOCTRINE_STATUS.md; or\n"
            "         write the allowlist first, which makes the reconcile option\n"
            "         available; or treat this mode as not passed"
        ),
    },
    "VA-U4": {
        "change_class": "F",
        "question": (
            "What object is the credential pool inventory that the SS-20 and CR-1 "
            "disjointness check reads, and what does the check report when it is "
            "invoked on LOCAL, where EG-4 and CR-4 say the pool never exists?"
        ),
        "options": (
            "The CR-2 provisioning record set, read only in ISOLATED, with the LOCAL "
            "invocation reporting DEFERRED and the uncovered half stated on every clean "
            "run.",
            "A derived projection crossing to LOCAL, which carries recovery selectors "
            "into a stratum EG-2 keeps out of LOCAL, and which as a digest set is the "
            "membership oracle RT-13 rejected.",
            "Compare the sealed cast against opaque credential ids alone and stop "
            "claiming recovery-selector coverage, which retires the clause CR-1 exists "
            "for.",
        ),
        "blocks": (
            "the SS-20 and CR-1 disjointness check",
            "the claim tools/validate_cast.py prints on every clean run",
        ),
        "refuses": (
            "REFUSED PENDING RATIFICATION\n"
            "  where: tools/validate_authorization.py unratified VA-U4\n"
            "  what:  the disjointness check was asked to compare two populations and\n"
            "         only one of them exists. CR-1 refuses on any intersection including\n"
            "         a shared recovery selector, which is the case a comparison on\n"
            "         handles alone misses, and there is no inventory to compare\n"
            "  moves: stamp one of the three options in doctrine/DOCTRINE_STATUS.md and\n"
            "         name the inventory artifact; or provision the pool and record it\n"
            "         under CR-2, which gives this check its second population; or treat\n"
            "         the disjointness property as unproven, which is what the DEFERRED\n"
            "         notice says"
        ),
    },
}

#: Interpretive calls this tool had to make where doctrine disclaims the
#: question and the authority order or an existing precedent answers it.
#: Recorded on the ontology/selectors.yaml pattern. Confirming or reversing one
#: is a stamp in doctrine/DOCTRINE_STATUS.md rather than an edit in place.
READINGS = {
    "VA-R1": (
        "The ratification predicate is conclusion-stamped alone. The pin of record "
        "states that every basis stamp blocks nothing mechanical and that conclusions "
        "bind while bases are unread, so requiring a basis would make this tool refuse "
        "every invocation and Step 8's own done-condition unreachable."
    ),
    "VA-R2": (
        "A path named in the pin's Pending-ratification table with a kind of stamp "
        "target is unstamped even where another row names the same path with a date. "
        "The pin says those two rows block the first collection run, and SS-14 item 6 "
        "stamps the contract at section granularity rather than at file granularity."
    ),
    "VA-R3": (
        "A rendered consequence is compared with runs of whitespace normalised, because "
        "the policy carries the sentences as wrapped block scalars and a fixture carries "
        "them on one line. The comparison is on the sentence rather than on the wrapping."
    ),
    "VA-R4": (
        "One gate token per tool, matching every sibling and matching the entry "
        "tools/validate_conformance.py already carries under this name. HY-1 fixes the "
        "code field as the violation code, so a mode cannot ride there."
    ),
}


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
# Accessors. Every one tolerates a malformed artifact, because a defect in a
# governed file must produce a named refusal rather than a traceback with a
# line number in this tool.
# ---------------------------------------------------------------------------


def _d(obj, *keys, default=None):
    """Walk a nested mapping, returning default at the first non-mapping."""
    cur = obj
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def _seq(obj, *keys) -> list:
    v = _d(obj, *keys)
    return list(v) if isinstance(v, list) else []


def _norm(text: str) -> str:
    """Collapse whitespace. Reading VA-R3: compare the sentence, not the wrap."""
    return " ".join(str(text).split())


def _slice(text: str, start: str, end: str) -> str:
    i = text.find(start)
    if i < 0:
        return ""
    j = text.find(end, i + len(start))
    return text[i:] if j < 0 else text[i:j]


def _table_rows(block: str) -> list[list[str]]:
    """Every pipe row in a markdown block, as stripped cells."""
    rows = []
    for line in block.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if cells and all(set(c) <= set("-: ") for c in cells):
            continue  # separator
        rows.append(cells)
    return rows


# ---------------------------------------------------------------------------
# The pin of record. Three tables, three different questions, one predicate.
# doctrine/DOCTRINE_STATUS.md is the only source a mechanism reads for whether
# a criterion binds, and SUBJECT_SELECTION.md says so in its own header.
# ---------------------------------------------------------------------------


class Pin:
    """The parsed stamp state. Nothing here decides; it reads."""

    __slots__ = ("ratified", "stamp_targets", "criteria", "parsed")

    def __init__(self, text: str):
        self.ratified: dict[str, str] = {}
        self.stamp_targets: set[str] = set()
        self.criteria: set[str] = set()
        self.parsed = False

        ratified = _slice(text, "## Ratified", "### What each decision was")
        pending = _slice(text, "## Pending ratification", "### Step 3 criteria")
        step3 = _slice(text, "### Step 3 criteria", "## Assistant readings")
        if not (ratified and pending and step3):
            return

        for cells in _table_rows(ratified):
            if len(cells) != 6 or cells[0].lower().startswith("item"):
                continue
            date = DATE_RE.search(cells[3])
            if not date or not cells[5]:
                continue
            for path in PIN_PATH_RE.findall(cells[1]):
                self.ratified.setdefault(path, date.group(0))

        for cells in _table_rows(pending):
            if len(cells) != 4 or "stamp target" not in cells[1].lower():
                continue
            for path in PIN_PATH_RE.findall(cells[0]):
                self.stamp_targets.add(path)

        for cells in _table_rows(step3):
            if not cells:
                continue
            m = CRITERION_RE.match(cells[0])
            if m:
                self.criteria.add(m.group(1))

        self.parsed = bool(self.criteria) and bool(self.ratified)

    def artifact_stamped(self, path: str) -> bool:
        return path in self.ratified and path not in self.stamp_targets

    def criterion_stamped(self, cid: str) -> bool:
        if cid not in self.criteria:
            return False
        return self.artifact_stamped(NAMESPACE_FILE.get(cid.split("-")[0], ""))


def item_6_reasons(stamp_state: dict, paths: list[str], criteria: list[str], pin: Pin) -> list[str]:
    """Why SS-14 item 6 refuses, or an empty list if it does not.

    Item 6 is the one NEVER item the gate evaluates, and SS-8 says it does so by
    reading the pin of record. The stamp state's own `source` decides which input
    is read, because whether a fixture may supply the table is GF-U1 in
    `conformance/gate/README.md` and this tool does not answer it. Both inputs
    are evaluated by the same predicate, so the answer changes what is read and
    not what refuses.
    """
    source = _d(stamp_state, "source", default="")
    if source == "fixture":
        stamped = set(_seq(stamp_state, "artifacts_stamped"))
        absent = list(_seq(stamp_state, "criteria_absent"))
    else:
        stamped = {p for p in paths if pin.artifact_stamped(p)}
        absent = [c for c in criteria if not pin.criterion_stamped(c)]

    reasons = [f"{p} carries no dated row in the pin of record" for p in paths if p not in stamped]
    reasons += [f"criterion {c} has no row in the stamp table" for c in absent]
    return reasons


# ---------------------------------------------------------------------------
# Loading. The model is one dict so --self-test can mutate it in memory.
# ---------------------------------------------------------------------------


class Unreadable(Exception):
    def __init__(self, code: str, where: str, detail: str, moves: str):
        super().__init__(code)
        self.finding = Finding(code, where, detail, moves)


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        rel = REL.get(path, str(path))
        raise Unreadable(
            "AUTH_INPUT_UNREADABLE",
            rel,
            f"a governed input this gate reconciles could not be read ({exc.strerror}), "
            "so every reconcile below would pass vacuously",
            f"create {rel}; or correct the path in tools/validate_authorization.py; or "
            "move the authorization gate to PENDING in tools/validate_conformance.py",
        ) from exc


def _yaml(path: Path) -> dict:
    raw = _read(path)
    rel = REL.get(path, str(path))
    try:
        doc = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        first = str(exc).splitlines()[0] if str(exc) else exc.__class__.__name__
        raise Unreadable(
            "AUTH_INPUT_UNPARSEABLE",
            rel,
            f"PyYAML could not parse the file ({first}), so the enums this gate "
            "reconciles against cannot be read",
            f"fix the YAML at the reported location in {rel}; or move the authorization "
            "gate to PENDING in tools/validate_conformance.py",
        ) from exc
    if not isinstance(doc, dict):
        raise Unreadable(
            "AUTH_INPUT_UNPARSEABLE",
            rel,
            f"the document parsed to {type(doc).__name__} rather than a mapping, so no "
            "block this gate reads exists",
            f"restore the single top-level wrapper key in {rel}, named after the file "
            "with hyphens turned to underscores, so a mistyped key fails closed",
        )
    return doc


def load() -> dict:
    """Every governed input this gate reconciles, in one mutable dict."""
    if yaml is None:
        raise Unreadable(
            "AUTH_YAML_READER_MISSING",
            "tools/validate_authorization.py",
            "PyYAML is not importable, so neither the compiled policy nor the rank 3 "
            "mirror can be read and this gate would pass vacuously",
            "pip install pyyaml; or add the install step to the CI workflow that runs "
            "this gate",
        )

    policy_doc = _yaml(POLICY)
    if "subject_authorization" not in policy_doc:
        raise Unreadable(
            "AUTH_POLICY_WRAPPER_KEY_MISSING",
            "policy/subject-authorization.yaml",
            "the file carries no top-level `subject_authorization` key. The house "
            "convention is one wrapper key named after the file with hyphens turned to "
            "underscores, so a mistyped key fails closed rather than loading as an "
            "empty policy",
            "restore the `subject_authorization` wrapper key; or, if the file was "
            "renamed, move the key and this tool's loader in the same commit",
        )

    raw_schema = _read(SCHEMA)
    try:
        schema = json.loads(raw_schema)
    except json.JSONDecodeError as exc:
        raise Unreadable(
            "AUTH_INPUT_UNPARSEABLE",
            "schema/subject-authorization.schema.json",
            f"the schema is not valid JSON (line {exc.lineno}, column {exc.colno}), so "
            "the record shape this gate reconciles against cannot be read",
            "fix the JSON at the reported location; or move the authorization gate to "
            "PENDING in tools/validate_conformance.py",
        ) from exc

    corpus_files = sorted(CORPUS_DIR.glob("*.jsonl"))
    if not corpus_files:
        raise Unreadable(
            "AUTH_CORPUS_EMPTY",
            "conformance/gate/*.jsonl",
            "the gate corpus holds no .jsonl file, so there is no fixture to grade and "
            "a clean result would prove that nothing was checked. SS-5 names this "
            "corpus as the place its three refusal fixtures live",
            "write the corpus; or move the authorization gate to PENDING in "
            "tools/validate_conformance.py until it exists",
        )

    rows: list[dict] = []
    for path in corpus_files:
        rel = f"conformance/gate/{path.name}"
        for n, line in enumerate(_read(path).splitlines(), 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise Unreadable(
                    "AUTH_INPUT_UNPARSEABLE",
                    f"{rel}:{n}",
                    f"the row is not valid JSON ({exc.msg}), so the fixture it carries "
                    "cannot be graded and the rows after it cannot be counted",
                    "fix the JSON on that line; one object per line, no trailing comma",
                ) from exc
            if not isinstance(row, dict):
                raise Unreadable(
                    "AUTH_INPUT_UNPARSEABLE",
                    f"{rel}:{n}",
                    f"the row parsed to {type(row).__name__} rather than an object, so "
                    "it carries no fixture",
                    "replace the line with a row on the twelve-key contract in "
                    "conformance/gate/README.md section 3",
                )
            row["_where"] = f"{rel}:{n}"
            rows.append(row)

    vocabulary = _yaml(CODE_VOCABULARY)
    codes = {
        c.get("code")
        for c in _seq(vocabulary, "violation_codes", "codes")
        if isinstance(c, dict)
    }

    register_text = _read(REGISTER)
    register_block = _slice(register_text, "## 4. The fixtures", "### 4.1")

    return {
        "policy": policy_doc["subject_authorization"],
        "schema": schema,
        "rows": rows,
        "codes": codes,
        "model": _yaml(LAYER_MODEL),
        "register": list(dict.fromkeys(REGISTER_NAME_RE.findall(register_block))),
        "gf_entries": set(GF_ENTRY_RE.findall(register_text)),
        "pin_text": _read(PIN),
    }


def _pin(model: dict) -> Pin:
    return Pin(model.get("pin_text", ""))


# ---------------------------------------------------------------------------
# The checks. check_corpus() holds every falsifiable defect check and is what
# --self-test mutates. check_certification() holds the designed refusal, which
# is a different fact with a different cause: a corpus can be defect-free and
# still uncertifiable while its policy is unstamped.
# ---------------------------------------------------------------------------


def _decision(row: dict) -> dict:
    d = row.get("expect_decision")
    return d if isinstance(d, dict) else {}


def _asserts_nothing(row: dict) -> bool:
    return _decision(row).get("value") is None and row.get("expect_code") is None


def _held(row: dict) -> list[str]:
    return [str(p) for p in _seq(row, "pending")]


def check_corpus(model: dict) -> list[Finding]:
    f: list[Finding] = []
    policy = model.get("policy") or {}
    schema = model.get("schema") or {}
    rows = model.get("rows") or []
    codes = model.get("codes") or set()
    lm = model.get("model") or {}
    pin = _pin(model)

    collect = _d(lm, "event_types", "COLLECT_EVENT", "payload", "fields", default={}) or {}
    refusal_basis = set(_seq(collect, "refusal_basis", "enum"))
    extension_basis = set(_seq(collect, "extension_basis", "enum"))
    step_enum = set(_seq(collect, "decided_at_step", "enum"))
    decision_enum = set(_seq(collect, "decision", "enum"))
    relation_enum = set(_seq(collect, "subject_relation", "enum"))

    policy_values = set(_seq(policy, "gate", "values", "enum"))
    consequences = {
        m.get("value"): m.get("consequence", "")
        for m in _seq(policy, "gate", "values", "members")
        if isinstance(m, dict)
    }
    never_refusal = _d(policy, "ratify_before_collection", "refuses", default="")
    legal_renders = {_norm(v) for v in consequences.values() if v}
    legal_renders.add(_norm(never_refusal))

    schema_props = list(_d(schema, "properties", default={}) or {})
    schema_required = list(schema.get("required") or [])
    schema_closed = schema.get("additionalProperties") is False
    schema_classes = _seq(schema, "properties", "subject_class", "enum")

    entry_ids = {
        e.get("id")
        for e in _seq(policy, "unratified", "entries")
        if isinstance(e, dict)
    }
    known_entries = entry_ids | set(model.get("gf_entries") or ()) | set(UNRATIFIED)

    #: Reported once per undeclared field name rather than once per row. The
    #: defect is one drift between two artifacts, and twenty-one identical
    #: refusals bury the twenty-one other checks.
    undeclared_fields: dict[str, list[str]] = {}

    # -- A-01 through A-11, per row -----------------------------------------
    for row in rows:
        where = row.get("_where", row.get("name", "a corpus row"))
        name = row.get("name") or "unnamed"
        held = _held(row)
        dec = _decision(row)

        present = {k for k in row if k != "_where"}
        if present != set(ROW_KEYS):
            missing = sorted(set(ROW_KEYS) - present)
            extra = sorted(present - set(ROW_KEYS))
            f.append(
                Finding(
                    "AUTH_ROW_KEYS_UNEXPECTED",
                    where,
                    "the row's key set is not the twelve the row contract fixes"
                    + (f", missing {missing}" if missing else "")
                    + (f", carrying {extra}" if extra else "")
                    + ". A missing key is an input the gate reads that the fixture never "
                    "supplied, and an extra key is an assertion nothing grades",
                    "restore the twelve keys in conformance/gate/README.md section 3; or, "
                    "for a new input the gate reads, add it to the contract, to every row, "
                    "and to ROW_KEYS in tools/validate_authorization.py in one commit",
                )
            )

        if _asserts_nothing(row) and not held:
            f.append(
                Finding(
                    "AUTH_ROW_ASSERTS_NOTHING",
                    where,
                    "the row names no decision value, no violation code and no unratified "
                    "entry holding it, so it passes every grader by carrying no claim",
                    "assert a decision value, or a code, or list the entries that hold the "
                    "row in `pending`; or delete the row",
                )
            )

        if row.get("expect_only") is not True:
            f.append(
                Finding(
                    "AUTH_EXPECT_ONLY_MISSING",
                    where,
                    "expect_only is not true. Every row here is a D5 fixture and "
                    "docs/THE-GAMEPLAN.md section 2.4 requires the flag on every one of "
                    "them, because a fixture without it passes on a code it never claimed "
                    "to exercise",
                    "set expect_only true; or, if the row genuinely exercises more than one "
                    "code, split it into one row per code",
                )
            )

        value = dec.get("value")
        if value is not None and value not in policy_values:
            f.append(
                Finding(
                    "AUTH_DECISION_VALUE_UNKNOWN",
                    f"{where} > expect_decision.value",
                    f"the row asserts {value!r}, which the compiled gate enum does not "
                    "carry. SS-7 closes the set at three values and rank 3 ships them as "
                    "COLLECT_EVENT subtypes, so a fourth value is a decision no consumer "
                    "can read",
                    "assert one of " + ", ".join(sorted(policy_values)) + "; or, to add a "
                    "value, ratify it against SS-7 with a dated stamp in "
                    "doctrine/DOCTRINE_STATUS.md and move both the policy enum and this "
                    "tool's GATE_VALUES in that commit",
                )
            )

        step = dec.get("decided_at_step")
        if step is not None and step not in step_enum:
            f.append(
                Finding(
                    "AUTH_DECIDED_AT_STEP_OUTSIDE_ENUM",
                    f"{where} > expect_decision.decided_at_step",
                    f"the row asserts step {step!r} and SS-8's order is stamped at six "
                    "steps, which rank 3 ships as a closed enum. A step outside it claims "
                    "the gate decided at a point in an order the operator never stamped",
                    "assert one of " + ", ".join(str(s) for s in sorted(step_enum)) + "; or "
                    "hold the row on the entry that decides its step, which is how the "
                    "rows with no placed step are written",
                )
            )

        basis = dec.get("basis")
        basis_field = dec.get("basis_field")
        bases = basis if isinstance(basis, list) else [basis]
        for b in [x for x in bases if x is not None]:
            legal = refusal_basis if basis_field == "refusal_basis" else extension_basis
            if basis_field not in ("refusal_basis", "extension_basis"):
                f.append(
                    Finding(
                        "AUTH_BASIS_FIELD_UNKNOWN",
                        f"{where} > expect_decision.basis_field",
                        f"the row records a basis under {basis_field!r}, and the wire "
                        "record carries exactly two basis fields. A basis under neither "
                        "is a token no consumer reads",
                        "record the basis under refusal_basis or extension_basis, "
                        "whichever the asserted value belongs to",
                    )
                )
            elif b not in legal:
                other = extension_basis if legal is refusal_basis else refusal_basis
                hint = (
                    " The value belongs to the other basis field."
                    if b in other
                    else " The closed enum carries no such member."
                )
                f.append(
                    Finding(
                        "AUTH_BASIS_OUTSIDE_ENUM",
                        f"{where} > expect_decision.basis",
                        f"the row asserts basis {b!r} under {basis_field}, which rank 3 "
                        "closes." + hint + " A refusal whose basis nothing declares cannot "
                        "be routed or rendered",
                        "assert a member of " + ", ".join(sorted(legal)) + "; or, to add a "
                        "member, land it in spec/layer-model.yaml with a regeneration and "
                        "a dated stamp, which narrows rather than widens and is still "
                        "Class F by effect",
                    )
                )

        relation = dec.get("subject_relation")
        if relation is not None and relation not in relation_enum:
            f.append(
                Finding(
                    "AUTH_SUBJECT_RELATION_UNKNOWN",
                    f"{where} > expect_decision.subject_relation",
                    f"the row asserts relation {relation!r}. SS-10 closes the computed "
                    "column at seed, pivot and incidental, and a connector may not assert "
                    "it at all",
                    "assert one of " + ", ".join(sorted(relation_enum)) + "; or leave the "
                    "field null, which is what a refusal payload carries",
                )
            )

        code = row.get("expect_code")
        if code is not None and code not in codes:
            f.append(
                Finding(
                    "AUTH_CODE_OUTSIDE_VOCABULARY",
                    f"{where} > expect_code",
                    f"the row expects {code!r} and policy/violation-codes.yaml does not "
                    "declare it. A gate emitting an undeclared code emits a string, and "
                    "nothing downstream can route it",
                    "expect a declared code; or land the new code in spec/layer-model.yaml "
                    "and regenerate, which is the one path that mints a code; or leave "
                    "expect_code null where the vocabulary names none for this refusal",
                )
            )

        if value in ("REFUSED", "REQUIRES_EXTENSION") and not held:
            thin = [
                k
                for k in ("decided_at_step", "basis", "render")
                if dec.get(k) in (None, "", [])
            ]
            if thin:
                f.append(
                    Finding(
                        "AUTH_ASSERTION_INCOMPLETE_AND_UNHELD",
                        f"{where} > expect_decision",
                        f"the row asserts a refusal and leaves {thin} empty while naming no "
                        "unratified entry. A held row asserting less is honest, because the "
                        "entry says what decides the rest; an unheld one is a gap wearing a "
                        "fixture",
                        "complete the assertion; or list the entries that hold it in "
                        "`pending`, which is how the rows with an undecided step or basis "
                        "are written",
                    )
                )

        render = dec.get("render")
        if render and _norm(render) not in legal_renders:
            f.append(
                Finding(
                    "AUTH_RENDER_NOT_THE_COMPILED_SENTENCE",
                    f"{where} > expect_decision.render",
                    "the row renders a consequence the compiled policy does not carry. "
                    "CLAUDE.md section 4 renders a state as its consequence, and a fixture "
                    "inventing its own sentence proves the gate against prose nobody "
                    "ratified",
                    "render the sentence policy/subject-authorization.yaml compiles for "
                    "this value; or leave render null and hold the row on the entry that "
                    "decides the sentence, which is how the seven refusals with no sentence "
                    "are written",
                )
            )

        for held_id in held:
            if not PENDING_ID_RE.match(held_id) or held_id not in known_entries:
                f.append(
                    Finding(
                        "AUTH_PENDING_ENTRY_UNKNOWN",
                        f"{where} > pending",
                        f"the row is held on {held_id!r}, and no entry of that id exists in "
                        "policy/subject-authorization.yaml, conformance/gate/README.md or "
                        "this tool. A row held on an entry that does not exist is held "
                        "forever while reading as scheduled",
                        "name an existing entry; or write the entry with its question, its "
                        "options and the sentence it renders; or resolve the row",
                    )
                )

        record = row.get("authorization")
        if isinstance(record, dict):
            fields = set(record)
            missing = sorted(set(RECORD_FIELDS) - fields)
            if missing:
                f.append(
                    Finding(
                        "AUTH_RECORD_FIELD_MISSING",
                        f"{where} > authorization",
                        f"the record is missing {missing}, which SS-4 requires. A partial "
                        "authorization is refused rather than half-honoured, so the fields "
                        "that are present authorize nothing",
                        "write the missing field into the record; or, where the row's point "
                        "is that no record exists, set authorization null",
                    )
                )
            if schema_closed:
                for field in sorted(fields - set(schema_props)):
                    undeclared_fields.setdefault(field, []).append(name)
            klass = record.get("subject_class")
            if klass in NOT_AUTHORIZABLE or (
                klass is not None and schema_classes and klass not in schema_classes
            ):
                f.append(
                    Finding(
                        "AUTH_SUBJECT_CLASS_UNAUTHORIZABLE",
                        f"{where} > authorization.subject_class",
                        f"the record names class {klass!r}. SS-1 marks S5 not authorizable "
                        "and SS-4 excludes it from this field, so a record naming it is an "
                        "authorization for a class no authorization reaches",
                        "name one of " + ", ".join(AUTHORIZABLE_CLASSES) + " with the "
                        "evidence that class requires; or, for a person who arrived "
                        "incidentally, open a new case with their own written record, which "
                        "is a decision rather than a refusal",
                    )
                )

        f += _placeholder_findings(row, where)

    for field, names in sorted(undeclared_fields.items()):
        f.append(
            Finding(
                "AUTH_RECORD_FIELD_UNDECLARED",
                f"conformance/gate/ > authorization.{field}",
                f"{len(names)} record(s) carry {field!r}, which "
                "schema/subject-authorization.schema.json does not declare while setting "
                "additionalProperties false. The corpus records are therefore not "
                "instances of the schema they are graded against, and the drift runs in "
                "exactly one direction, which is the shape the doctrine gate's own D-01 "
                "defect took",
                f"remove {field!r} from the records; or declare it in the schema and record "
                "the decision that adds it, since the schema closes SS-4's nine-field table "
                "and a tenth field is an amendment to that table rather than a shape choice",
            )
        )

    # -- A-12. SS-5's three fields, and the one-field property ---------------
    f += _ss5_findings(rows)

    # -- A-13. Both directions against the register --------------------------
    corpus_names = [r.get("name") for r in rows if r.get("name")]
    register = model.get("register") or []
    for name in sorted(set(corpus_names) - set(register)):
        f.append(
            Finding(
                "AUTH_FIXTURE_NOT_IN_REGISTER",
                f"conformance/gate/ > {name}",
                "the corpus carries a fixture the register in "
                "conformance/gate/README.md section 4 does not list. The register is the "
                "closed membership list for the eighteen names rank 3 does not reserve, "
                "and a fixture outside it is graded by nothing that counts it",
                "add the row to the register with its criterion, decision, step, basis and "
                "code; or delete the fixture",
            )
        )
    for name in sorted(set(register) - set(corpus_names)):
        f.append(
            Finding(
                "AUTH_REGISTER_FIXTURE_MISSING",
                f"conformance/gate/README.md section 4 > {name}",
                "the register lists a fixture the corpus does not carry, so a criterion "
                "that names a required fixture is satisfied on paper. One direction finds "
                "half the drift, which is the defect D-01 recorded",
                "write the fixture; or remove the register row and record why the criterion "
                "that required it no longer does",
            )
        )
    for name in sorted(set(corpus_names)):
        if corpus_names.count(name) > 1:
            f.append(
                Finding(
                    "AUTH_FIXTURE_NAME_DUPLICATE",
                    f"conformance/gate/ > {name}",
                    f"the name appears on {corpus_names.count(name)} rows, so a reconcile "
                    "keyed on it reads one row as covering both and a criterion is proven "
                    "by whichever row the grader reached last",
                    "rename one of the rows; a matched pair is two names, as the SS-17 "
                    "baseline pair is",
                )
            )

    # -- A-14. The three names rank 3 reserves -------------------------------
    f += _reserved_findings(model, rows)

    # -- A-15 and A-16. The three-way enum reconciles ------------------------
    f += _enum_findings(model)

    # -- A-17. The ratification predicate, exercised -------------------------
    f += _stamp_findings(model, pin)

    # -- A-18 and A-19. The item 6 mechanism, and its matched pair -----------
    f += _item_6_findings(model, pin)

    # -- A-20 and A-21. The compiled SS-14 counts, and entry hygiene ---------
    f += _policy_shape_findings(model)

    return f


def _placeholder_findings(row: dict, where: str) -> list[Finding]:
    """A-08. Every selector-keyed value is a bracketed placeholder.

    `argv_template` is the one exemption and it is named rather than inferred: it
    carries a selector type such as `<handle>` rather than a selector, which is
    the template the shipped must-pass corpus already holds.
    """
    out: list[Finding] = []
    seen: list[str] = []

    def walk(node, path: str, key: str | None, typed: bool):
        if isinstance(node, dict):
            # `value` is a selector only where its object also names the type.
            # The gate's own `expect_decision.value` is a decision, and the
            # register's `value` columns are prose.
            pair = "selector_type" in node
            for k, v in node.items():
                walk(v, f"{path}.{k}", k, pair)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{path}[{i}]", key, typed)
        elif isinstance(node, str) and key in SELECTOR_KEYS:
            if key == "value" and not typed:
                return
            if not PLACEHOLDER_RE.match(node) and path not in seen:
                seen.append(path)

    walk({k: v for k, v in row.items() if k != "_where"}, "", None, False)
    for path in seen:
        out.append(
            Finding(
                "AUTH_VALUE_NOT_PLACEHOLDER",
                f"{where} > {path.lstrip('.')}",
                "a selector-keyed value is not a bracketed placeholder. SS-14 item 5 keeps "
                "a natural person's selector out of every tracked file, and a synthetic "
                "value is still a value while the cast is unsealed. The value itself is not "
                "quoted here, on the HY-1 rule that a gate's own evidence must not become "
                "the durable surface the gate exists to prevent",
                "replace the value with a <placeholder> drawn from synthetic/CAST.md; or, "
                "once the operator seals the cast, fill the corpus from the sealed truth "
                "file in one reproducible step",
            )
        )
    return out


def _ss5_findings(rows: list[dict]) -> list[Finding]:
    """A-12. The criterion that exists because of the measured guard.py defect."""
    out: list[Finding] = []
    by_name = {r.get("name"): r for r in rows}

    for field in SS5_FIELDS:
        candidates = [
            r
            for r in rows
            if field in str(r.get("criterion", ""))
            and _decision(r).get("value") in ("REFUSED", "REQUIRES_EXTENSION")
        ]
        if not candidates:
            out.append(
                Finding(
                    "AUTH_SS5_FIXTURE_MISSING",
                    f"conformance/gate/ > SS-5 {field}",
                    f"no fixture names SS-5 and {field} and asserts a refusal. A field that "
                    "no fixture can make refuse is not being read, whatever the code looks "
                    "like, and SS-5 says this mode fails if any of the three is missing",
                    f"write a fixture identical to a passing row except in {field}, "
                    "asserting a refusal; or, if the field has been removed from SS-4's "
                    "table, move SS5_FIELDS in tools/validate_authorization.py in the same "
                    "commit as the ratified amendment",
                )
            )
            continue

        for row in candidates:
            record = row.get("authorization")
            if not isinstance(record, dict):
                continue
            differs = []
            for other in rows:
                if other is row or _decision(other).get("value") != "PERMITTED":
                    continue
                base = other.get("authorization")
                if not isinstance(base, dict):
                    continue
                keys = set(base) | set(record)
                delta = sorted(k for k in keys if base.get(k) != record.get(k))
                differs.append((len(delta), delta, other.get("name")))
            if not differs:
                continue
            size, delta, base_name = min(differs)
            if delta != [field]:
                out.append(
                    Finding(
                        "AUTH_SS5_FIXTURE_NOT_ONE_FIELD",
                        f"{row.get('_where', row.get('name'))} > authorization",
                        f"the fixture for {field} differs from its nearest permitted row "
                        f"({base_name}) in {delta or 'no field at all'}. SS-5 requires a "
                        "row identical to a passing row except in that one field, because a "
                        "fixture that changes two fields cannot show which one the gate read",
                        f"restore every field except {field} to the permitted row's values; "
                        "or, if the permitted row moved, move both in one commit so the pair "
                        "stays a one-field difference",
                    )
                )

    for name in ("seed-permitted",):
        if name in by_name and _decision(by_name[name]).get("value") != "PERMITTED":
            out.append(
                Finding(
                    "AUTH_SS5_BASELINE_NOT_PERMITTED",
                    f"conformance/gate/ > {name}",
                    "the differential baseline no longer asserts a permit, so SS-5's three "
                    "one-field mutations have nothing to be identical to and each of them "
                    "proves only that something refuses",
                    "restore the baseline's permitted assertion; or name a different row as "
                    "the baseline and re-derive the three mutations from it",
                )
            )
    return out


def _reserved_findings(model: dict, rows: list[dict]) -> list[Finding]:
    """A-14. Rank 3 reserves three names, their codes and their expect_only."""
    out: list[Finding] = []
    fixtures = _d(model, "model", "violation_codes", "fixtures", default={}) or {}
    by_name = {r.get("name"): r for r in rows}
    for name, spec in fixtures.items():
        if not isinstance(spec, dict) or not str(spec.get("corpus", "")).startswith(
            "conformance/gate"
        ):
            continue
        row = by_name.get(name)
        if row is None:
            out.append(
                Finding(
                    "AUTH_RESERVED_FIXTURE_MISSING",
                    f"conformance/gate/ > {name}",
                    "spec/layer-model.yaml's fixture map reserves this name for the gate "
                    "corpus and the corpus does not carry it. The map is rank 3 and check "
                    "L-15 refuses a fixture-map entry outside the sixteen named ones, so "
                    "the name is not the fixture author's to drop",
                    f"write the {name} fixture; or remove the entry from the fixture map, "
                    "which is a rank 3 edit reviewed as one",
                )
            )
            continue
        if row.get("expect_code") != spec.get("code"):
            out.append(
                Finding(
                    "AUTH_RESERVED_FIXTURE_DRIFT",
                    f"{row.get('_where', name)} > expect_code",
                    f"the row expects {row.get('expect_code')!r} and the rank 3 fixture map "
                    f"reserves {spec.get('code')!r} for this name. The map and the corpus "
                    "are the two halves of one assertion, and a drift passes both "
                    "validators",
                    "expect the code the map reserves; or change the map, which is a rank 3 "
                    "edit landing in the same commit as the corpus",
                )
            )
        if spec.get("expect_only") is True and row.get("expect_only") is not True:
            out.append(
                Finding(
                    "AUTH_RESERVED_FIXTURE_DRIFT",
                    f"{row.get('_where', name)} > expect_only",
                    "the rank 3 fixture map reserves expect_only true for this name and the "
                    "row does not carry it, so the fixture may pass on a code it never "
                    "claimed to exercise",
                    "set expect_only true; or change the map, which is a rank 3 edit",
                )
            )
    return out


def _enum_findings(model: dict) -> list[Finding]:
    """A-15 and A-16. Three artifacts, one enum each, no drift between them."""
    out: list[Finding] = []
    policy = model.get("policy") or {}
    schema = model.get("schema") or {}
    lm = model.get("model") or {}

    policy_classes = _seq(policy, "authorizable_subject_class", "enum")
    schema_classes = _seq(schema, "properties", "subject_class", "enum")
    mirror_classes = _seq(
        lm, "event_types", "AUTHORIZE_EVENT", "payload", "fields", "subject_class", "enum"
    )
    triples = (
        ("policy/subject-authorization.yaml authorizable_subject_class", policy_classes),
        ("schema/subject-authorization.schema.json properties.subject_class", schema_classes),
        ("spec/layer-model.yaml AUTHORIZE_EVENT subject_class", mirror_classes),
    )
    for label, values in triples:
        if list(values) != list(AUTHORIZABLE_CLASSES):
            out.append(
                Finding(
                    "AUTH_CLASS_ENUM_DRIFT",
                    label,
                    f"the authorizable class set reads {list(values)} and SS-1's set minus "
                    f"S5 is {list(AUTHORIZABLE_CLASSES)}. SS-1 makes the policy the source "
                    "and the schema the mechanism that refuses a value outside it, and the "
                    "model declares itself a mirror, so a difference between any two of the "
                    "three widens or narrows who may be a subject in a diff that reads as "
                    "configuration",
                    "restore " + ", ".join(AUTHORIZABLE_CLASSES) + " in all three; or, to "
                    "change the set, ratify it against SS-1 with a dated stamp in "
                    "doctrine/DOCTRINE_STATUS.md authored by the ratifier, and move the "
                    "policy, the schema, the mirror and this tool's AUTHORIZABLE_CLASSES in "
                    "that same commit",
                )
            )
    for cls in NOT_AUTHORIZABLE:
        for label, values in triples:
            if cls in list(values):
                out.append(
                    Finding(
                        "AUTH_CLASS_ENUM_DRIFT",
                        label,
                        f"{cls} appears in the authorizable set. SS-1 marks it not "
                        "authorizable and SS-4 excludes it from the record's field, and "
                        "SS-10 makes the incidental relation a computed column rather than "
                        "an asserted class",
                        f"remove {cls} from the enum; the incidental relation is computed "
                        "from the pivot chain and is never written on a record",
                    )
                )

    policy_values = _seq(policy, "gate", "values", "enum")
    mirror_values = _seq(
        lm, "event_types", "COLLECT_EVENT", "payload", "fields", "decision", "enum"
    )
    for label, values in (
        ("policy/subject-authorization.yaml gate.values", policy_values),
        ("spec/layer-model.yaml COLLECT_EVENT decision", mirror_values),
    ):
        if list(values) != list(GATE_VALUES):
            out.append(
                Finding(
                    "AUTH_GATE_VALUE_ENUM_DRIFT",
                    label,
                    f"the gate value set reads {list(values)} and SS-7 closes it at "
                    f"{list(GATE_VALUES)}. SS-7 also records that the middle value stops "
                    "the run, so neither non-permitted value is a warning and a fourth "
                    "value would be a decision no consumer can act on",
                    "restore the three values; or ratify a change to SS-7 with a dated "
                    "stamp and move the policy, the mirror and this tool's GATE_VALUES in "
                    "that commit",
                )
            )

    policy_disp = _seq(policy, "bystanders", "dispositions", "enum")
    mirror_disp = _seq(
        lm,
        "event_types",
        "COLLECT_EVENT",
        "payload",
        "fields",
        "bystander_disposition",
        "enum",
    )
    for label, values in (
        ("policy/subject-authorization.yaml bystanders.dispositions", policy_disp),
        ("spec/layer-model.yaml COLLECT_EVENT bystander_disposition", mirror_disp),
    ):
        if list(values) != list(DISPOSITIONS):
            out.append(
                Finding(
                    "AUTH_DISPOSITION_ENUM_DRIFT",
                    label,
                    f"the bystander disposition set reads {list(values)} and R8 stamps it "
                    f"at {list(DISPOSITIONS)} for v0.1. CLAUDE.md gate 2 names this exact "
                    "diff as one that widens who is collected on while reading as Class B",
                    "restore " + ", ".join(DISPOSITIONS) + "; a wider set needs a Class F "
                    "ratification with a dated stamp in doctrine/DOCTRINE_STATUS.md, "
                    "authored by the ratifier, and this tool's DISPOSITIONS moves in that "
                    "same commit",
                )
            )
    refused = _seq(policy, "bystanders", "dispositions", "defined_and_refused")
    for token in DISPOSITIONS_REFUSED:
        if token not in list(refused):
            out.append(
                Finding(
                    "AUTH_DISPOSITION_ENUM_DRIFT",
                    "policy/subject-authorization.yaml bystanders.dispositions."
                    "defined_and_refused",
                    f"{token!r} is no longer defined and refused. SS-10 defines it and "
                    "refuses it on the pattern SS-1 uses for S3 and S4, because a "
                    "disposition that is merely absent reads as an oversight and a "
                    "disposition that is named and refused reads as a decision",
                    f"restore {token!r} to defined_and_refused; reaching it is a Class F "
                    "ratification with a dated stamp",
                )
            )
    return out


def _stamp_findings(model: dict, pin: Pin) -> list[Finding]:
    """A-17. Every criterion the policy compiles carries a stamp, or refuses."""
    out: list[Finding] = []
    if not pin.parsed:
        out.append(
            Finding(
                "AUTH_PIN_SHAPE_UNREADABLE",
                "doctrine/DOCTRINE_STATUS.md",
                "the pin of record parsed to no criterion rows or no dated artifact rows, "
                "so the predicate that decides whether anything binds has nothing to read. "
                "An unratified criterion refuses rather than permits, which covers a "
                "missing row and does not cover a missing table",
                "restore the Ratified table, the Pending ratification table and the Step 3 "
                "per-criterion table; or stamp SA-U15 in the pin, which is the entry that "
                "decides what a mechanism does when the pin itself cannot be read",
            )
        )
        return out

    for cid in _seq(model, "policy", "compiles_criteria"):
        cid = str(cid)
        if not CRITERION_RE.fullmatch(cid):
            continue
        if cid not in pin.criteria:
            out.append(
                Finding(
                    "AUTH_CRITERION_NOT_STAMPED",
                    f"doctrine/DOCTRINE_STATUS.md > {cid}",
                    f"policy/subject-authorization.yaml compiles {cid} and the pin of "
                    "record's per-criterion table carries no row for it. A criterion with "
                    "no row refuses, so this table is the mechanism rather than an index of "
                    "one, and a compiled criterion nothing stamps is a rule the policy "
                    "asserts on its own authority",
                    f"add the {cid} row to the Step 3 table with its conclusion recorded; "
                    "or remove the criterion from compiles_criteria and record what compiles "
                    "it instead",
                )
            )
            continue
        source = NAMESPACE_FILE.get(cid.split("-")[0], "")
        if not pin.artifact_stamped(source):
            out.append(
                Finding(
                    "AUTH_CRITERION_FILE_NOT_STAMPED",
                    f"doctrine/DOCTRINE_STATUS.md > {source}",
                    f"{cid} carries a per-criterion row and {source} carries no dated "
                    "ratifier row, or is named in the Pending table as a stamp target. "
                    "Nothing binds unless it appears with a date and a ratifier, and one "
                    "partially stamped item does not stamp its file",
                    f"stamp {source} in the Ratified table with a date and a ratifier; or "
                    "resolve the Pending row that names it as a stamp target",
                )
            )
    return out


def _item_6_findings(model: dict, pin: Pin) -> list[Finding]:
    """A-18 and A-19. The one NEVER item the gate evaluates, and its pair.

    A-19 is the check docs/THE-GAMEPLAN.md Step 8 names in its done-condition.
    The absence is constructed rather than found, because the pin records that
    every conclusion is recorded and nothing is pending a conclusion, so there is
    no genuinely unstamped criterion on disk to point at. The control half is as
    load-bearing as the refusing half: a predicate that refuses every input
    proves nothing, which is the second failure direction HY-2 adjudicates.
    """
    out: list[Finding] = []
    policy = model.get("policy") or {}
    paths = [
        str(p)
        for item in _seq(policy, "ratify_before_collection", "items")
        if isinstance(item, dict)
        for p in _seq(item, "paths")
    ]
    criteria = [str(c) for c in _seq(policy, "compiles_criteria")]

    # A-18. A row that asserts the item 6 refusal must actually produce it.
    for row in model.get("rows") or []:
        dec = _decision(row)
        if dec.get("never_item") != 6:
            continue
        state = _d(row, "given", "stamp_state", default={}) or {}
        reasons = item_6_reasons(state, paths, criteria, pin)
        if dec.get("value") == "REFUSED" and not reasons:
            out.append(
                Finding(
                    "AUTH_ITEM_6_ASSERTION_UNMET",
                    f"{row.get('_where', row.get('name'))} > given.stamp_state",
                    "the row asserts a refusal under NEVER item 6 and the stamp state it "
                    "supplies is complete, so the predicate finds nothing missing and the "
                    "refusal the row asserts does not arise. This is the SS-5 defect in the "
                    "stamp read: an assertion no input can produce proves the assertion "
                    "rather than the mechanism",
                    "remove an artifact from the row's artifacts_stamped, or name a "
                    "criterion in criteria_absent, so the refusal the row asserts has a "
                    "cause; or change the row to the permit that a complete stamp state "
                    "produces",
                )
            )
        if dec.get("value") == "PERMITTED" and reasons:
            out.append(
                Finding(
                    "AUTH_UNRATIFIED_CRITERION_PERMITTED",
                    f"{row.get('_where', row.get('name'))} > given.stamp_state",
                    "the row asserts a permit under a stamp state that is short "
                    f"{len(reasons)} item(s), the first being {reasons[0]}. SS-14 item 6 "
                    "refuses all collection, including collection against a synthetic "
                    "account, until every artifact it names is stamped",
                    "assert the refusal the stamp state produces; or complete the row's "
                    "stamp state, which is a fixture edit rather than a permission",
                )
            )

    # A-19. The constructed absence, with its control.
    if paths and criteria:
        short_artifact = {
            "source": "fixture",
            "artifacts_stamped": paths[1:],
            "criteria_absent": [],
        }
        short_criterion = {
            "source": "fixture",
            "artifacts_stamped": paths,
            "criteria_absent": [criteria[0]],
        }
        complete = {"source": "fixture", "artifacts_stamped": paths, "criteria_absent": []}

        if not item_6_reasons(short_criterion, paths, criteria, pin):
            out.append(
                Finding(
                    "AUTH_UNRATIFIED_CRITERION_PERMITTED",
                    "tools/validate_authorization.py > item_6_reasons",
                    f"a stamp state missing the criterion {criteria[0]} was not refused. "
                    "The pin of record states that a criterion absent from the stamp table "
                    "refuses rather than permits, and this is the check "
                    "docs/THE-GAMEPLAN.md Step 8 names in its done-condition. A gate that "
                    "permits on a missing row permits every dispatch the operator never "
                    "stamped",
                    "fix item_6_reasons so an absent criterion refuses; or, if the "
                    "criterion namespace moved, move NAMESPACE_FILE with it in the same "
                    "commit",
                )
            )
        if not item_6_reasons(short_artifact, paths, criteria, pin):
            out.append(
                Finding(
                    "AUTH_UNRATIFIED_ARTIFACT_PERMITTED",
                    "tools/validate_authorization.py > item_6_reasons",
                    f"a stamp state missing the artifact {paths[0]} was not refused. SS-14 "
                    "item 6 names eight items across nine paths and refuses collection "
                    "until every one carries a dated stamp, so a gate that permits on a "
                    "missing artifact runs before the operator ratified anything",
                    "fix item_6_reasons so a missing artifact refuses; or correct the path "
                    "list in policy/subject-authorization.yaml, which is where the nine "
                    "paths are enumerated",
                )
            )
        if item_6_reasons(complete, paths, criteria, pin):
            out.append(
                Finding(
                    "AUTH_STAMP_PREDICATE_ALWAYS_REFUSES",
                    "tools/validate_authorization.py > item_6_reasons",
                    "a fully stamped state was refused, so the predicate refuses every "
                    "input and the refusals above prove nothing about what it reads. "
                    "HY-2 adjudicates both failure directions, and a gate that never "
                    "passes is the direction that gets routed around",
                    "fix item_6_reasons so a complete stamp state permits; or correct the "
                    "path list and the criterion list the control is built from, since a "
                    "control built from the wrong lists can never be satisfied",
                )
            )
    return out


def _policy_shape_findings(model: dict) -> list[Finding]:
    """A-20 and A-21. The compiled SS-14 counts, and the unratified entries."""
    out: list[Finding] = []
    policy = model.get("policy") or {}

    never_items = [i for i in _seq(policy, "never", "items") if isinstance(i, dict)]
    if len(never_items) != NEVER_ITEM_COUNT:
        out.append(
            Finding(
                "AUTH_NEVER_ITEM_COUNT_WRONG",
                "policy/subject-authorization.yaml never.items",
                f"the compiled NEVER list carries {len(never_items)} items and SS-14 carries "
                f"{NEVER_ITEM_COUNT}. These refuse whatever any authorization file says and "
                "are evaluated first for that reason, so a list that has silently lost an "
                "item is a hard refusal a config file unlocked",
                f"restore all {NEVER_ITEM_COUNT} items with their enforced_by; or, to change "
                "the list, ratify the amendment to SS-14 with a dated stamp and move this "
                "tool's NEVER_ITEM_COUNT in that commit",
            )
        )
    for item in never_items:
        if "enforced_by" not in item:
            out.append(
                Finding(
                    "AUTH_NEVER_ITEM_UNPLACED",
                    f"policy/subject-authorization.yaml never.items item {item.get('item')}",
                    "the item names no enforcement point. SS-14's list carries six items and "
                    "is not six mechanisms, so each one states where it is actually "
                    "enforced. Calling an unbuilt item a mechanism is the laundering design "
                    "gate 6 forbids, in the list that reads as most enforced",
                    "state enforced_by for the item, naming the analyst, a rule with no "
                    "mechanism, a hook, or the gate; or remove the item under a ratified "
                    "amendment to SS-14",
                )
            )

    ratify = _d(policy, "ratify_before_collection", default={}) or {}
    items = [i for i in _seq(ratify, "items") if isinstance(i, dict)]
    paths = [p for i in items for p in _seq(i, "paths")]
    if len(items) != RATIFY_ITEM_COUNT or len(paths) != RATIFY_PATH_COUNT:
        out.append(
            Finding(
                "AUTH_RATIFY_LIST_COUNT_WRONG",
                "policy/subject-authorization.yaml ratify_before_collection",
                f"the list carries {len(items)} items across {len(paths)} paths and SS-14 "
                f"item 6 enumerates {RATIFY_ITEM_COUNT} across {RATIFY_PATH_COUNT}. The "
                "list is enumerated in place rather than incorporated by reference, because "
                "an absolute prohibition whose content can change by editing an unranked "
                "document is not absolute",
                f"restore the {RATIFY_ITEM_COUNT} items and {RATIFY_PATH_COUNT} paths SS-14 "
                "item 6 names; or, to change the list, ratify the amendment with a dated "
                "stamp and move this tool's counts in that commit",
            )
        )
    if ratify.get("resolved_by_reference") is True:
        out.append(
            Finding(
                "AUTH_RATIFY_LIST_BY_REFERENCE",
                "policy/subject-authorization.yaml ratify_before_collection."
                "resolved_by_reference",
                "the list declares itself resolved by reference. SS-14 item 6 enumerates its "
                "items in place and says why: docs/THE-GAMEPLAN.md carries no rank in the "
                "authority order, declares itself unratified, and has an expiry condition, "
                "so a prohibition sourced from it can change by editing an unranked file",
                "set resolved_by_reference false and enumerate the items in place; or record "
                "the ratified decision that makes an unranked file the source of an absolute "
                "prohibition",
            )
        )
    checks = _seq(ratify, "preflight", "checks")
    if len(checks) != PREFLIGHT_CHECK_COUNT:
        out.append(
            Finding(
                "AUTH_PREFLIGHT_CHECK_COUNT_WRONG",
                "policy/subject-authorization.yaml ratify_before_collection.preflight.checks",
                f"the preflight set carries {len(checks)} checks and SS-14 item 6 names "
                f"{PREFLIGHT_CHECK_COUNT}. Preflight is the one condition in item 6 that is "
                "not a document and is therefore not stampable, and its failure is fatal to "
                "the runner rather than a warning",
                f"restore the {PREFLIGHT_CHECK_COUNT} checks SS-14 item 6 names; or ratify "
                "the change and move this tool's PREFLIGHT_CHECK_COUNT in the same commit",
            )
        )
    if _d(ratify, "preflight", "stampable") is True:
        out.append(
            Finding(
                "AUTH_PREFLIGHT_MARKED_STAMPABLE",
                "policy/subject-authorization.yaml ratify_before_collection.preflight."
                "stampable",
                "preflight is marked stampable. The pin of record records that it "
                "deliberately has no stamp row, because a stamp is not what makes a "
                "mechanism true, and a stampable preflight is a runner condition satisfied "
                "by writing a date in a table",
                "set stampable false; or record the ratified decision that turns a machine "
                "condition into a document",
            )
        )

    for entry in _seq(policy, "unratified", "entries"):
        if not isinstance(entry, dict):
            continue
        eid = entry.get("id", "an unratified entry")
        missing = [
            k
            for k in ("id", "change_class", "question", "options", "blocks", "refuses")
            if not entry.get(k)
        ]
        if missing:
            out.append(
                Finding(
                    "AUTH_UNRATIFIED_ENTRY_MALFORMED",
                    f"policy/subject-authorization.yaml unratified {eid}",
                    f"the entry is missing {missing}, so a mechanism that reaches it cannot "
                    "tell an operator what was refused, which rule refused it, or what the "
                    "legal moves are. An entry with no options is a gap rendered as a token",
                    "write the missing keys: the question, the legal options with their "
                    "costs, what the entry blocks, and the sentence rendered when a caller "
                    "reaches it",
                )
            )
        refuses = entry.get("refuses")
        if isinstance(refuses, str) and refuses and not refuses.startswith("REFUSED"):
            out.append(
                Finding(
                    "AUTH_UNRATIFIED_ENTRY_NOT_A_CONSEQUENCE",
                    f"policy/subject-authorization.yaml unratified {eid} > refuses",
                    "the entry's refusal does not render as a consequence. CLAUDE.md section "
                    "4 requires a state to be rendered as what did not happen and why, "
                    "because an operator cannot act on the bare string unratified",
                    "open the refusal with REFUSED and state what was refused, which rule "
                    "refused it, and the two or three legal moves; the entries that already "
                    "do this are the pattern",
                )
            )
    return out


def check_certification(model: dict) -> list[Finding]:
    """The designed refusal, kept apart from the defect checks.

    A corpus can be free of every defect above and still not certify a gate. The
    two states have different causes and different remedies, and collapsing them
    would make a stamp look like a bug fix.
    """
    out: list[Finding] = []
    policy = model.get("policy") or {}
    pin = _pin(model)

    held: dict[str, list[str]] = {}
    for row in model.get("rows") or []:
        for entry in _held(row):
            held.setdefault(entry, []).append(row.get("name") or "unnamed")
    if held:
        summary = "; ".join(
            f"{entry} holds {len(names)} row(s)" for entry, names in sorted(held.items())
        )
        out.append(
            Finding(
                "AUTH_CERTIFICATION_HELD",
                "conformance/gate/*.jsonl",
                f"{sum(len(v) for v in held.values())} row assertions are held on "
                f"{len(held)} unratified entries and the gate is therefore not certified. "
                f"{summary}. A green run with a held row in the file would report a gate as "
                "proven against a condition nobody chose",
                "stamp the entries in doctrine/DOCTRINE_STATUS.md and move the behaviour "
                "they hold into policy/subject-authorization.yaml; or delete the rows the "
                "stamped answer retires; or read this refusal as the state it is holding, "
                "which is that no run may execute",
            )
        )

    for item in _seq(policy, "ratify_before_collection", "items"):
        if not isinstance(item, dict):
            continue
        for path in _seq(item, "paths"):
            if not pin.artifact_stamped(str(path)):
                out.append(
                    Finding(
                        "AUTH_ARTIFACT_UNSTAMPED",
                        f"doctrine/DOCTRINE_STATUS.md, no dated row for {path}",
                        "SS-14 item 6 refuses all collection, including collection against a "
                        "synthetic account, until this path carries a dated stamp in the pin "
                        "of record. This is a hard refusal, so a present, complete, valid, "
                        "unexpired authorization record does not unlock it",
                        f"stamp {path} in doctrine/DOCTRINE_STATUS.md with a date and a "
                        "ratifier; or resolve the Pending row that names it as a stamp "
                        "target; or collect nothing, which is what this refusal is holding",
                    )
                )

    out.append(
        Finding(
            "AUTH_EVALUATOR_UNRATIFIED",
            "tools/validate_authorization.py unratified VA-U1",
            "this mode graded the wire form, the enums, the record shape, the register and "
            "the stamp read, and it produced no gate decision, because where the evaluator "
            "lives is undecided. The register's claim that this mode proves the gate "
            "refuses is therefore not yet true, and a clean result here would be read as "
            "that claim",
            "stamp one of VA-U1's three options in doctrine/DOCTRINE_STATUS.md and land the "
            "evaluator where it names; or wait for Step 10, which delivers "
            "runner/subject_guard.py; or read this refusal as the state it is holding",
        )
    )
    return out


# ---------------------------------------------------------------------------
# --self-test. One row per direction a check guards. A gate nobody has watched
# fail is an assumption (doctrine/HYGIENE.md section 2).
# ---------------------------------------------------------------------------


def _row(model: dict, name: str) -> dict:
    for r in model.get("rows") or []:
        if r.get("name") == name:
            return r
    raise KeyError(name)


def _first_record(model: dict) -> dict:
    for r in model.get("rows") or []:
        if isinstance(r.get("authorization"), dict):
            return r["authorization"]
    raise KeyError("no row carries an authorization record")


def _mut_drop_row_key(m: dict) -> None:
    (m["rows"][0]).pop("criterion")


def _mut_row_asserts_nothing(m: dict) -> None:
    r = _row(m, "seed-permitted")
    r["expect_decision"]["value"] = None
    r["expect_code"] = None
    r["pending"] = []


def _mut_drop_expect_only(m: dict) -> None:
    _row(m, "bystander-disposition-retain")["expect_only"] = False


def _mut_decision_value(m: dict) -> None:
    _row(m, "seed-permitted")["expect_decision"]["value"] = "PERMITTED_WITH_WARNING"


def _mut_step_outside_enum(m: dict) -> None:
    _row(m, "seed-permitted")["expect_decision"]["decided_at_step"] = 7


def _mut_basis_wrong_field(m: dict) -> None:
    _row(m, "scope-drift-three-hops")["expect_decision"]["basis_field"] = "refusal_basis"


def _mut_basis_invented(m: dict) -> None:
    _row(m, "s4-baseline-scorecard-absent")["expect_decision"]["basis"] = "incidental_origin"


def _mut_relation_invented(m: dict) -> None:
    _row(m, "seed-permitted")["expect_decision"]["subject_relation"] = "target"


def _mut_code_undeclared(m: dict) -> None:
    _row(m, "bystander-disposition-retain")["expect_code"] = "BYSTANDER_DISPOSITION_REFUSED"


def _mut_unheld_thin_refusal(m: dict) -> None:
    _row(m, "run-without-purpose-binding")["pending"] = []


def _mut_render_invented(m: dict) -> None:
    _row(m, "seed-permitted")["expect_decision"]["render"] = "The run proceeds."


def _mut_pending_unknown(m: dict) -> None:
    _row(m, "seed-permitted")["pending"] = ["SA-U99"]


def _mut_record_field_missing(m: dict) -> None:
    _first_record(m).pop("expires_on")


def _mut_record_class_s5(m: dict) -> None:
    _first_record(m)["subject_class"] = "S5"


def _mut_ss5_fixture_missing(m: dict) -> None:
    m["rows"] = [r for r in m["rows"] if r.get("name") != "seed-expires-on-mutated"]
    m["register"] = [n for n in m["register"] if n != "seed-expires-on-mutated"]


def _mut_ss5_two_fields(m: dict) -> None:
    _row(m, "seed-selectors-mutated")["authorization"]["purpose"] = "A different purpose."


def _mut_fixture_not_in_register(m: dict) -> None:
    m["register"] = [n for n in m["register"] if n != "seed-permitted"]


def _mut_register_fixture_missing(m: dict) -> None:
    m["register"] = list(m["register"]) + ["a-fixture-nobody-wrote"]


def _mut_reserved_code_drift(m: dict) -> None:
    _row(m, "scope-drift-three-hops")["expect_code"] = "SUBJECT_NOT_AUTHORIZED"


def _mut_class_enum_widened(m: dict) -> None:
    m["policy"]["authorizable_subject_class"]["enum"] = list(AUTHORIZABLE_CLASSES) + ["S5"]


def _mut_gate_value_added(m: dict) -> None:
    m["policy"]["gate"]["values"]["enum"] = list(GATE_VALUES) + ["PERMITTED_WITH_NOTICE"]


def _mut_disposition_retain(m: dict) -> None:
    m["policy"]["bystanders"]["dispositions"]["enum"] = list(DISPOSITIONS) + ["retain"]
    m["policy"]["bystanders"]["dispositions"]["defined_and_refused"] = []


def _mut_criterion_row_removed(m: dict) -> None:
    m["pin_text"] = re.sub(r"^\| SS-5 .*$", "", m["pin_text"], flags=re.M)


def _mut_pin_tables_gone(m: dict) -> None:
    m["pin_text"] = "# Doctrine status: the pin of record\n\nnothing here\n"


def _mut_item_6_fully_stamped(m: dict) -> None:
    paths = [
        p
        for i in m["policy"]["ratify_before_collection"]["items"]
        for p in i.get("paths", [])
    ]
    state = _row(m, "criterion-absent-from-stamp-table")["given"]["stamp_state"]
    state["source"] = "fixture"
    state["artifacts_stamped"] = paths
    state["criteria_absent"] = []


def _mut_never_item_dropped(m: dict) -> None:
    m["policy"]["never"]["items"] = m["policy"]["never"]["items"][:-1]


def _mut_never_item_unplaced(m: dict) -> None:
    m["policy"]["never"]["items"][3].pop("enforced_by")


def _mut_ratify_path_dropped(m: dict) -> None:
    m["policy"]["ratify_before_collection"]["items"][0]["paths"] = []


def _mut_ratify_by_reference(m: dict) -> None:
    m["policy"]["ratify_before_collection"]["resolved_by_reference"] = True


def _mut_preflight_stampable(m: dict) -> None:
    m["policy"]["ratify_before_collection"]["preflight"]["stampable"] = True


def _mut_preflight_check_dropped(m: dict) -> None:
    m["policy"]["ratify_before_collection"]["preflight"]["checks"] = []


def _mut_entry_loses_options(m: dict) -> None:
    m["policy"]["unratified"]["entries"][0].pop("options")


def _mut_entry_refusal_is_a_token(m: dict) -> None:
    m["policy"]["unratified"]["entries"][0]["refuses"] = "refused"


def _mut_value_filled_in(m: dict) -> None:
    _first_record(m)["selectors"][0]["value"] = "a_filled_in_value"


def _mut_record_field_undeclared(m: dict) -> None:
    _first_record(m)["scope"] = "a tenth field the schema does not declare"


def _mut_basis_field_invented(m: dict) -> None:
    _row(m, "scope-drift-three-hops")["expect_decision"]["basis_field"] = "drift_basis"


def _mut_duplicate_fixture_name(m: dict) -> None:
    _row(m, "depth-at-the-limit")["name"] = "seed-permitted"


def _mut_reserved_fixture_deleted(m: dict) -> None:
    m["rows"] = [r for r in m["rows"] if r.get("name") != "scope-drift-three-hops"]


def _mut_baseline_refuses(m: dict) -> None:
    r = _row(m, "seed-permitted")
    r["expect_decision"]["value"] = "REFUSED"
    r["expect_decision"]["render"] = None


def _mut_criterion_file_unstamped(m: dict) -> None:
    # Every dated row naming the file, because several rows name it and one
    # surviving row still stamps the path.
    marker = "### What each decision was"
    head, sep, tail = m["pin_text"].partition(marker)
    kept = [ln for ln in head.splitlines() if "`doctrine/SUBJECT_SELECTION.md`" not in ln]
    m["pin_text"] = "\n".join(kept) + sep + tail


def _mut_permit_under_a_missing_stamp(m: dict) -> None:
    r = _row(m, "criterion-absent-from-stamp-table")
    r["expect_decision"]["value"] = "PERMITTED"
    r["expect_decision"]["render"] = (
        "The run proceeds. The runner will construct argv, and that is the whole of "
        "what this value means."
    )


def _mutations() -> list[tuple[str, object, str, bool, str]]:
    """(description, mutator(model) -> None, expected code, expect_only, why).

    `expect_only` False means the mutation's damage genuinely reaches more than
    one check, and the fifth field says how. Every False here is a sentence a
    reader can check against the artifacts, which is the point of the flag.
    """
    return [
        ("drop a key from a corpus row", _mut_drop_row_key, "AUTH_ROW_KEYS_UNEXPECTED", True, ""),
        (
            "a row asserting no value, no code and no entry",
            _mut_row_asserts_nothing,
            "AUTH_ROW_ASSERTS_NOTHING",
            False,
            "the baseline row is also SS-5's differential baseline and the SS-17 pair's "
            "permitted half, so removing its permit fires the baseline check too",
        ),
        (
            "take expect_only off a refusing row",
            _mut_drop_expect_only,
            "AUTH_EXPECT_ONLY_MISSING",
            True,
            "",
        ),
        (
            "invent a fourth gate value",
            _mut_decision_value,
            "AUTH_DECISION_VALUE_UNKNOWN",
            False,
            "the invented value is not PERMITTED, so the SS-5 baseline check fires as well",
        ),
        (
            "assert a seventh evaluation step",
            _mut_step_outside_enum,
            "AUTH_DECIDED_AT_STEP_OUTSIDE_ENUM",
            True,
            "",
        ),
        (
            "record an extension basis under refusal_basis",
            _mut_basis_wrong_field,
            "AUTH_BASIS_OUTSIDE_ENUM",
            True,
            "",
        ),
        (
            "invent a refusal basis for an incidental origin",
            _mut_basis_invented,
            "AUTH_BASIS_OUTSIDE_ENUM",
            True,
            "",
        ),
        (
            "invent a fourth subject relation",
            _mut_relation_invented,
            "AUTH_SUBJECT_RELATION_UNKNOWN",
            True,
            "",
        ),
        (
            "expect a violation code nothing declares",
            _mut_code_undeclared,
            "AUTH_CODE_OUTSIDE_VOCABULARY",
            True,
            "",
        ),
        (
            "unhold a refusal with no step and no sentence",
            _mut_unheld_thin_refusal,
            "AUTH_ASSERTION_INCOMPLETE_AND_UNHELD",
            True,
            "",
        ),
        (
            "render a consequence the policy does not carry",
            _mut_render_invented,
            "AUTH_RENDER_NOT_THE_COMPILED_SENTENCE",
            True,
            "",
        ),
        (
            "hold a row on an entry nobody wrote",
            _mut_pending_unknown,
            "AUTH_PENDING_ENTRY_UNKNOWN",
            True,
            "",
        ),
        (
            "drop expires_on from an authorization record",
            _mut_record_field_missing,
            "AUTH_RECORD_FIELD_MISSING",
            True,
            "",
        ),
        (
            "authorize an incidental subject",
            _mut_record_class_s5,
            "AUTH_SUBJECT_CLASS_UNAUTHORIZABLE",
            True,
            "",
        ),
        (
            "delete SS-5's expires_on fixture",
            _mut_ss5_fixture_missing,
            "AUTH_SS5_FIXTURE_MISSING",
            True,
            "",
        ),
        (
            "change a second field in an SS-5 fixture",
            _mut_ss5_two_fields,
            "AUTH_SS5_FIXTURE_NOT_ONE_FIELD",
            True,
            "",
        ),
        (
            "drop a fixture from the register",
            _mut_fixture_not_in_register,
            "AUTH_FIXTURE_NOT_IN_REGISTER",
            True,
            "",
        ),
        (
            "register a fixture nobody wrote",
            _mut_register_fixture_missing,
            "AUTH_REGISTER_FIXTURE_MISSING",
            True,
            "",
        ),
        (
            "change the code on a name rank 3 reserves",
            _mut_reserved_code_drift,
            "AUTH_RESERVED_FIXTURE_DRIFT",
            True,
            "",
        ),
        (
            "widen the authorizable class set to S5",
            _mut_class_enum_widened,
            "AUTH_CLASS_ENUM_DRIFT",
            True,
            "",
        ),
        (
            "add a fourth gate value to the policy",
            _mut_gate_value_added,
            "AUTH_GATE_VALUE_ENUM_DRIFT",
            True,
            "",
        ),
        (
            "add retain to the bystander dispositions",
            _mut_disposition_retain,
            "AUTH_DISPOSITION_ENUM_DRIFT",
            True,
            "",
        ),
        (
            "remove a criterion's row from the pin of record",
            _mut_criterion_row_removed,
            "AUTH_CRITERION_NOT_STAMPED",
            True,
            "",
        ),
        (
            "replace the pin of record with a file carrying no tables",
            _mut_pin_tables_gone,
            "AUTH_PIN_SHAPE_UNREADABLE",
            True,
            "",
        ),
        (
            "give the unratified-criterion row a complete stamp state",
            _mut_item_6_fully_stamped,
            "AUTH_ITEM_6_ASSERTION_UNMET",
            True,
            "",
        ),
        (
            "drop a NEVER item",
            _mut_never_item_dropped,
            "AUTH_NEVER_ITEM_COUNT_WRONG",
            True,
            "",
        ),
        (
            "leave a NEVER item with no enforcement point",
            _mut_never_item_unplaced,
            "AUTH_NEVER_ITEM_UNPLACED",
            True,
            "",
        ),
        (
            "empty one item's path list in the ratify-before-collection list",
            _mut_ratify_path_dropped,
            "AUTH_RATIFY_LIST_COUNT_WRONG",
            True,
            "",
        ),
        (
            "resolve the ratify-before-collection list by reference",
            _mut_ratify_by_reference,
            "AUTH_RATIFY_LIST_BY_REFERENCE",
            True,
            "",
        ),
        (
            "mark preflight stampable",
            _mut_preflight_stampable,
            "AUTH_PREFLIGHT_MARKED_STAMPABLE",
            True,
            "",
        ),
        (
            "empty the preflight check set",
            _mut_preflight_check_dropped,
            "AUTH_PREFLIGHT_CHECK_COUNT_WRONG",
            True,
            "",
        ),
        (
            "take the options off an unratified entry",
            _mut_entry_loses_options,
            "AUTH_UNRATIFIED_ENTRY_MALFORMED",
            True,
            "",
        ),
        (
            "render an unratified entry as its token",
            _mut_entry_refusal_is_a_token,
            "AUTH_UNRATIFIED_ENTRY_NOT_A_CONSEQUENCE",
            True,
            "",
        ),
        (
            "fill in a selector value in the corpus",
            _mut_value_filled_in,
            "AUTH_VALUE_NOT_PLACEHOLDER",
            True,
            "",
        ),
        (
            "add a tenth field to an authorization record",
            _mut_record_field_undeclared,
            "AUTH_RECORD_FIELD_UNDECLARED",
            True,
            "",
        ),
        (
            "record a basis under a third basis field",
            _mut_basis_field_invented,
            "AUTH_BASIS_FIELD_UNKNOWN",
            True,
            "",
        ),
        (
            "give two rows the same fixture name",
            _mut_duplicate_fixture_name,
            "AUTH_FIXTURE_NAME_DUPLICATE",
            False,
            "the renamed row leaves the register under its old name, so the register "
            "reconcile fires in the direction that finds a registered fixture nobody wrote",
        ),
        (
            "delete a fixture rank 3 reserves by name",
            _mut_reserved_fixture_deleted,
            "AUTH_RESERVED_FIXTURE_MISSING",
            False,
            "the deleted row is also in the register, so the register reconcile fires in "
            "the same direction and reports the same absence from the other side",
        ),
        (
            "make SS-5's differential baseline refuse",
            _mut_baseline_refuses,
            "AUTH_SS5_BASELINE_NOT_PERMITTED",
            True,
            "",
        ),
        (
            "remove a doctrine file's dated ratifier row",
            _mut_criterion_file_unstamped,
            "AUTH_CRITERION_FILE_NOT_STAMPED",
            True,
            "",
        ),
        (
            "assert a permit under a stamp state missing a criterion",
            _mut_permit_under_a_missing_stamp,
            "AUTH_UNRATIFIED_CRITERION_PERMITTED",
            True,
            "",
        ),
    ]


SELF_TEST_DIRTY_BASELINE = (
    "REFUSED AUTH_SELF_TEST_BASELINE_NOT_CLEAN\n"
    "  where: tools/validate_authorization.py > check_corpus, unmutated\n"
    "  what:  the artifacts this gate reconciles carry a defect before any mutation is\n"
    "         applied, so a mutation that fires its expected code may be firing on the\n"
    "         defect rather than on the break. Each mutation below is therefore asserted\n"
    "         differentially, against the codes the baseline already fires, which is a\n"
    "         weaker condition than a clean baseline and is stated rather than assumed\n"
    "  moves: fix the baseline findings printed above, which are the same findings\n"
    "         --fixtures reports; or, if a finding is the designed state of an\n"
    "         unratified artifact, move the check that reports it into\n"
    "         check_certification, where a designed refusal belongs"
)


def self_test(model: dict, quiet: bool = False) -> int:
    baseline = check_corpus(model)
    baseline_codes = {f.code for f in baseline}
    # Keyed on the pair rather than on the code, so a mutation that produces a
    # second instance of a code the baseline already fires still registers as
    # caused by the break.
    baseline_pairs = {(f.code, f.where) for f in baseline}
    dirty = bool(baseline)
    if dirty:
        print(SELF_TEST_DIRTY_BASELINE, file=sys.stderr)
        print(file=sys.stderr)
        for fnd in baseline:
            print(fnd.render(), file=sys.stderr)
            print(file=sys.stderr)

    muts = _mutations()
    failures = 0
    cascading = 0
    exercised: set[str] = set()
    for desc, mutate, expected, only, why in muts:
        m = copy.deepcopy(model)
        try:
            mutate(m)
        except Exception as exc:
            failures += 1
            print(f"  PASSED    {desc:62} the mutation itself failed ({exc!r})")
            continue
        fired = {f.code for f in check_corpus(m) if (f.code, f.where) not in baseline_pairs}
        exercised |= fired
        if expected not in fired:
            ok, note = False, f", fired {sorted(fired)}"
        elif only and fired != {expected}:
            ok, note = False, f", also fired {sorted(fired - {expected})} and claims expect_only"
        elif not only and fired == {expected}:
            # The fifth field is a sentence about a cascade that did not happen.
            ok, note = False, ", fired the expected code alone while claiming a cascade"
        else:
            ok, note = True, ""
        if ok and not only:
            cascading += 1
        failures += 0 if ok else 1
        mark = "refused" if ok else "PASSED  "
        print(f"  {mark}  {desc:62} expected {expected}{note}")

    if failures:
        print(
            "REFUSED AUTH_SELF_TEST_FAILED\n"
            "  where: tools/validate_authorization.py > _mutations\n"
            f"  what:  {failures} deliberate break(s) were not refused as claimed, so a\n"
            "         clean run against the real artifacts proves nothing about the checks\n"
            "         those breaks name\n"
            "  moves: fix the check that did not fire; or fix the mutation if it no longer\n"
            "         produces the defect it names; or, where the damage genuinely reaches\n"
            "         more than one check, set expect_only false and state how in the\n"
            "         fifth field",
            file=sys.stderr,
        )
        print(
            f"validate_authorization --self-test: {failures} mutation(s) were not refused as "
            "claimed. A gate nobody has watched fail is an assumption (HYGIENE.md section 2).",
            file=sys.stderr,
        )
        return 1

    if not quiet:
        print(
            f"validate_authorization --self-test ok: {len(muts)} deliberate breaks, "
            f"{len(muts)} refused, {len(muts) - cascading} of them by the expected code "
            f"alone, {cascading} cascading with a stated reason. {len(exercised)} distinct "
            "codes exercised."
        )
    if dirty:
        print(
            f"  baseline was not clean: {len(baseline)} finding(s) in "
            f"{sorted(baseline_codes)}, and every assertion above was differential against "
            "them"
        )
        return 1
    return 0


# ---------------------------------------------------------------------------
# The deferred modes. A deferred check is never counted as a pass.
# ---------------------------------------------------------------------------


def _deferred(
    flag: str,
    what_it_will_check: str,
    stands_in: str,
    un_defers: str,
    entry: str,
    consequence: str,
) -> int:
    print(
        f"validate_authorization {flag}: DEFERRED, and it checked nothing.\n"
        f"  will check: {what_it_will_check}\n"
        f"  stands in:  {stands_in}\n"
        f"  un-defers:  {un_defers}\n"
        f"  undecided:  {entry}, whose question and options are in this tool's UNRATIFIED\n"
        f"  meanwhile:  {consequence}\n"
        "  A deferred check is never counted as a pass, and its entry in\n"
        "  tools/validate_conformance.py stays PENDING while this notice prints."
    )
    return 0


def dispatch_paths() -> int:
    return _deferred(
        "--dispatch-paths",
        "that every call site constructing argv, opening a subscription, or drawing from "
        "the credential pool is reached only through subject_guard.evaluate(), or is listed "
        "in runner/dispatch_allowlist.yaml with a written reason (SS-6). The credential "
        "clause is not decorative: a draft of this check covered argv and subscriptions "
        "only, which would have passed a call site that draws a credential before the gate",
        "nothing. runner/ holds no Python file, runner/dispatch_allowlist.yaml does not "
        "exist, and no dispatch path exists to be gated or ungated. A scan over an empty "
        "directory would report zero ungated call sites and exit clean, which is the "
        "vacuous green this notice exists instead of",
        "Step 10 of docs/THE-GAMEPLAN.md, which delivers runner/subject_guard.py and the "
        "dispatch path. runner/dispatch_allowlist.yaml is item 8 of SS-14 item 6's list and "
        "may land before it",
        "VA-U2 on whether this mode should refuse rather than defer, and VA-U3 on how an "
        "ungated call site is detected at all",
        "SS-14 item 6 names this mode as one of its four preflight checks, so a runner "
        "reading this notice as a pass would satisfy that condition with a check that ran "
        "nothing. The runner reads a deferred mode as not passed, and until Step 10 the "
        "SS-6 property is unproven rather than proven",
    )


def disjointness() -> int:
    return _deferred(
        "--disjointness",
        "that no selector appears in both synthetic/CAST.md and the credential pool, "
        "including a shared recovery selector, which is the case a comparison on handles "
        "alone misses (SS-20, CR-1). A shared recovery phone between a collection persona "
        "and a cast persona is an intersection even though no handle matches",
        "tools/validate_cast.py, which proves the cast's own recovery selectors are "
        "distinct from each other, and which names this mode as the owner of the "
        "cross-population half on every clean run. The cast is also unsealed, so its values "
        "are placeholders and a comparison today would compare designs rather than values",
        "the first provisioned credential under CR-2, which creates the second population. "
        "The check then runs in ISOLATED, because EG-4 and CR-4 keep the pool off LOCAL",
        "VA-U4 on what object the pool inventory is and what this mode reports when it is "
        "invoked on LOCAL",
        "tools/validate_cast.py prints on every clean run that this tool owns the SS-20 "
        "and CR-1 disjointness check at Step 8. That claim is a scheduled claim rather "
        "than a met one, and this notice is where it is said, since no clean run of this "
        "tool may be read as covering it",
    )


# ---------------------------------------------------------------------------


UNRATIFIED_CONSEQUENCE = (
    "UNRATIFIED: policy/subject-authorization.yaml carries no dated row in "
    "doctrine/DOCTRINE_STATUS.md, so this gate certifies nothing and SS-14 item 6 refuses "
    "every collection run"
)


def _telemetry_where(where: str) -> str:
    """Narrow a refusal's human `where` to the shape gate_log accepts.

    HY-1 says a record names the file and the line and never the string that
    matched, and `tools/gate_log.py` writes REDACTED_WHERE for anything outside
    a repository-relative path with an optional line and a dotted identifier.
    A refusal's `where` is prose written for a person, so this projects it
    rather than letting every record redact and the telemetry go blank.
    """
    text = str(where).strip()
    if not text:
        return ""
    head = text.split()[0].rstrip(",")
    rest = text[len(head) :]
    if any(ch in head for ch in "*?[]"):
        # A glob names a set of files. The directory is the honest location.
        head = head.rsplit("/", 1)[0] + "/" if "/" in head else "conformance/"
    head = re.sub(r"[^A-Za-z0-9_./\-:]", "", head)
    tail = re.sub(r"[^A-Za-z0-9_.\-]+", ".", rest).strip(".")
    location = f"{head} :: {tail}" if tail else head
    return location[:200]


def _telemetry(outcome: str, findings: list[Finding]) -> None:
    if gate_log is None:
        return
    try:
        # One run record, then one detail record per finding. HY-1 says one line
        # per gate run, and one line per finding inflates both the run count and
        # the refusal rate HY-2 adjudicates against. The `where` is a path with
        # an optional line, never the string that matched.
        gate_log.record_run(GATE, outcome, count=len(findings))
        for f in findings:
            gate_log.record_finding(GATE, code=f.code, where=_telemetry_where(f.where))
    except Exception:
        pass


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description="Subject authorization gate: the Step 8 half of the D5 mechanism."
    )
    ap.add_argument(
        "--fixtures",
        action="store_true",
        help="Grade conformance/gate/*.jsonl against the compiled policy, the schema, the "
        "rank 3 mirror and the pin of record. This is also what a bare invocation runs.",
    )
    ap.add_argument(
        "--dispatch-paths",
        action="store_true",
        help="DEFERRED until Step 10. Prints what it will check and what stands in.",
    )
    ap.add_argument(
        "--disjointness",
        action="store_true",
        help="DEFERRED until the first provisioned credential. The SS-20 and CR-1 check.",
    )
    ap.add_argument(
        "--self-test",
        action="store_true",
        help="Mutate the loaded artifacts in memory and assert each defect is refused.",
    )
    ap.add_argument("--quiet", action="store_true", help="Print only on failure.")
    args = ap.parse_args(argv)

    if args.dispatch_paths and not (args.fixtures or args.self_test):
        rc = dispatch_paths()
        if args.disjointness:
            rc = max(rc, disjointness())
        return rc
    if args.disjointness and not (args.fixtures or args.self_test):
        return disjointness()

    try:
        model = load()
    except Unreadable as exc:
        print(exc.finding.render(), file=sys.stderr)
        _telemetry("error", [])
        return 2

    if args.self_test:
        rc = self_test(model, quiet=args.quiet)
        _telemetry("pass" if rc == 0 else "refuse", [])
        return rc

    findings = check_corpus(model)
    certification = check_certification(model)
    all_findings = findings + certification
    _telemetry("refuse" if all_findings else "pass", all_findings)

    if all_findings:
        for f in all_findings:
            print(f.render(), file=sys.stderr)
            print(file=sys.stderr)
        print(
            f"validate_authorization: {len(all_findings)} violation(s), "
            f"{len(findings)} in the artifacts and {len(certification)} in the "
            "certification. rule: doctrine/SUBJECT_SELECTION.md SS-4, SS-5, SS-8 and "
            "SS-14, doctrine/DOCTRINE_STATUS.md as the pin of record, CLAUDE.md design "
            "gate 1.",
            file=sys.stderr,
        )

    pin = _pin(model)
    if not pin.artifact_stamped("policy/subject-authorization.yaml"):
        # Printed even under --quiet. The state is neither a pass nor a failure of
        # the corpus, and CLAUDE.md section 4 renders a state as its consequence.
        print(UNRATIFIED_CONSEQUENCE)

    if not args.quiet:
        rows = model.get("rows") or []
        held = sum(1 for r in rows if _held(r))
        print(
            "validate_authorization --fixtures: "
            f"{len(rows)} rows read, "
            f"{len(rows) - held} determinate, {held} held on an unratified entry; "
            f"{len(model.get('register') or [])} register names reconciled in both "
            f"directions; {len(_seq(model, 'policy', 'compiles_criteria'))} criteria "
            "checked against the pin of record"
        )
        stamp_codes = {
            "AUTH_UNRATIFIED_CRITERION_PERMITTED",
            "AUTH_UNRATIFIED_ARTIFACT_PERMITTED",
            "AUTH_STAMP_PREDICATE_ALWAYS_REFUSES",
            "AUTH_PIN_SHAPE_UNREADABLE",
        }
        if stamp_codes & {f.code for f in findings}:
            print(
                "  the check Step 8 names did not pass: the refusals above name which half "
                "of it failed, and until it passes nothing here shows that an unratified "
                "criterion refuses"
            )
        else:
            print(
                "  the check Step 8 names is green: a criterion absent from the stamp table "
                "refuses, a missing artifact refuses, and a fully stamped state permits, so "
                "the predicate reads the table rather than refusing everything"
            )
        print(
            "  not covered by this gate: what the gate returns, because where the "
            "evaluator lives is VA-U1 and runner/subject_guard.py is Step 10; that a "
            "dispatch path reaches the gate at all (SS-6), which is --dispatch-paths and "
            "is deferred; disjointness from the credential pool (SS-20, CR-1), which is "
            "--disjointness and is deferred because the pool lives only in ISOLATED per "
            "EG-4; and whether a purpose sentence names a person, which is a review rule "
            "with no mechanism"
        )

    return 1 if all_findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
