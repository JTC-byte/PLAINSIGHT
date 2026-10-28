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
its self-lint. All three are hand-authored with no generator, the corpus by
GF-R2, and therefore have no byte-for-byte drift check, so the reconciles below
are what stands in for one.

WHAT THIS GATE REFUSES TODAY, AND WHY THAT IS THE FEATURE. `--fixtures` refuses.
`doctrine/DOCTRINE_STATUS.md` is the pin of record: mechanisms read it rather
than the document they enforce, and an unratified criterion refuses rather than
permits. Seven of the nine paths SS-14 item 6 names carry no dated row, nineteen of
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
        the row's own value, with the item 6 refusal legal only on a REFUSED row
        whose basis is that item. CLAUDE.md section 4 renders a state as its
        consequence, and a fixture inventing its own sentence proves the gate
        against prose nobody ratified. Until 2026-10-01 any compiled sentence
        was accepted for any value.
  A-08  A selector-shaped value that is not a bracketed placeholder. SS-14 item 5
        keeps a natural person's selector out of every tracked file, and a
        synthetic value is still a value. Two passes: every value under a
        selector key, and, since 2026-10-01, an email or phone shape in any
        string or mapping key of a row, inside a bracketed placeholder as well.
        Before then a selector-shaped string under any other key passed. A
        number written with a 00 prefix is not read. A value under a selector key
        is a typed placeholder, <type:label>, and since 2026-10-02 it is one of
        the tokens synthetic/GROUND_TRUTH.yaml carries or the corpus-local token;
        a record selector is an object of exactly selector_type and value. This
        is the rule `tools/validate_cast.py --placeholder-scan` already applies
        to the truth file, applied to the one corpus that carries authorization
        records.
  A-09  A `pending` entry naming no unratified entry in
        `policy/subject-authorization.yaml` or `conformance/gate/README.md`. A
        row held on an entry that does not exist is held forever and reads as
        scheduled.
  A-10  An authorization record missing one of SS-4's nine fields, or carrying a
        field the schema's closed property set does not declare. SS-4 refuses a
        partial authorization rather than half-honouring it, and the schema sets
        `additionalProperties` false, so drift in either direction gives the
        corpus records key sets that differ from the schema's. --fixtures checks
        key sets and the subject_class enum, and refuses the schema itself as
        AUTH_SCHEMA_RECORD_SHAPE_DRIFT when its required list or properties are
        not the nine fields or its record is open; it does not validate a record as a
        schema instance, and every record would fail that today on SAS-U1 and
        SA-U2.
  A-11  A record naming a subject class outside the authorizable enum. S5 is in
        SS-1's class set and is not in this one, because SS-1 marks it not
        authorizable and SS-4 excludes it from the field.
  A-12  One of SS-5's three fields with no refusing fixture, or a fixture that
        differs from its baseline in any gate input other than the field it
        names: the record, the chain, the dispatch, the given inputs or the
        instant. Both halves matter: a missing fixture leaves the field
        unproven, and a fixture that changes two inputs cannot show which one
        the gate read.
  A-13  A corpus row absent from the register in `conformance/gate/README.md`
        section 4, or a register row absent from the corpus. One direction finds
        half the drift, which is the lesson D-01 recorded. Two rows sharing one
        name is the adjacent case: a reconcile keyed on the name reads one row as
        covering both, and a criterion is proven by whichever row the grader
        reached last. Since 2026-10-01 each register row's criterion, decision,
        step, basis, code and hold are read against its fixture too, on the
        register's notation: "none" for no value, "held" for a value a held row
        leaves open, and "determinate" for an empty hold. Since 2026-10-02 the
        register is read as GitHub renders its table, so a row without its
        outer pipes or its backticks is read, and a row with no fixture name in
        its first column is refused.
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
        rather than an index of one. Since 2026-10-01 the compiled list is also
        reconciled with the criteria doctrine/SUBJECT_SELECTION.md defines, in
        both directions, as AUTH_CRITERION_NOT_COMPILED.
  A-18  A row asserting the SS-14 item 6 refusal whose declared stamp state does
        not actually produce it, and, since 2026-10-01, any other decided row
        asserting a permit or a decision past step 1 under a stamp state item 6
        refuses. This is the SS-5 lesson applied to the stamp read: a fixture
        asserting what the predicate does not reach proves the assertion rather
        than the mechanism.
  A-19  **The check Step 8's done-condition names.** A criterion absent from the
        stamp table, or an artifact with no dated row, must refuse rather than
        permit. The test constructs the absence rather than finding one, and it
        carries its own matched pair: a fully stamped state must permit, because
        a predicate that refuses everything proves nothing and is the failure
        direction HY-2 adjudicates. Since 2026-10-01 each case also runs through
        the pin reader, on copies of the pin of record with one Step 3 row or
        one item 6 path's row removed, and on a copy with every item 6 path
        stamped; before then every case was a fixture-supplied list, and a reader
        that stamped everything left both modes green.
  A-20  The compiled SS-14 counts drifting: six NEVER items, eight
        ratify-before-collection items across nine paths, and four preflight
        checks; and, since 2026-10-01, the eight items' paths themselves, pinned
        in RATIFY_ITEMS and refused as AUTH_RATIFY_LIST_DRIFT. An absolute
        prohibition whose content can change by editing a list is not
        absolute.
  A-21  An unratified entry that is not usable as a refusal: no question, no
        options, no statement of what it blocks, or a `refuses` value that is a
        bare token rather than a rendered consequence. An operator cannot act on
        the string "unratified".

Modes:

  --fixtures  Grade `conformance/gate/*.jsonl` against the compiled policy, the
        schema's required fields, closed property set and subject_class enum,
        the rank 3 mirror and the pin of record, then refuse the
        certification while any row is held or any artifact is unstamped. The
        A-19 result is reported separately from the certification, because the
        mechanism being green and the corpus being certifiable are two different
        facts.
  --dispatch-paths  SS-6, drafted at Step 10. Reads every Python file under
        `runner/`, `connectors/` and `app/`, tracked or untracked and not
        ignored, finds each site that constructs argv, runs a process, opens a
        connection, a listener or a subscription, starts a container, draws a
        credential, resolves a callable at run time, or forges a Decision, and
        asserts each is reached only through `runner.subject_guard.evaluate()`
        or is listed in `runner/dispatch_allowlist.yaml` with a written reason.
        The site patterns, the reachability rule and the one exemption are
        stated above `DISPATCH_PATTERNS`. It refuses while the allowlist is
        absent, which is today's state, because the bypass check then has
        nothing to compare against, and it refuses while the allowlist carries
        no dated row, because a Class F exemption list binds nothing unstamped.
        This takes VA-U2's third option and VA-U3's first and third together,
        recorded as VA-R5 and awaiting the operator. VA-R6, applied 2026-10-28
        as the session's reading and awaiting the operator's class (B as a
        precision rule of this scanner, or F), reads three references
        in a test module under tests/ as not sites: a patch target, the object
        of an attribute assigned over, and a patch's kept original that is not
        called where it is read.
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
of four groups, and the harness's own two refusals,
AUTH_SELF_TEST_BASELINE_NOT_CLEAN and AUTH_SELF_TEST_FAILED, are outside the
count because they report on the self-test rather than on an artifact. Five are
loader refusals that fire before a model exists:
AUTH_YAML_READER_MISSING, AUTH_INPUT_UNREADABLE, AUTH_INPUT_UNPARSEABLE,
AUTH_POLICY_WRAPPER_KEY_MISSING and AUTH_CORPUS_EMPTY, each exercised by pointing
the module's paths at a file that is not there. Three are the certification
refusals, AUTH_CERTIFICATION_HELD, AUTH_ARTIFACT_UNSTAMPED and
AUTH_EVALUATOR_UNRATIFIED, which fire on the real tree today and are the designed
state rather than a defect. One, AUTH_MODES_COMBINED, refuses a command line
that combines modes, before any artifact is read. One, AUTH_CAST_SEAL_UNREAD, guards item 7's seal
condition and fires only if the condition is removed from the code. Until the
second review of 2026-10-01 this paragraph counted ten and named the two
stamp-predicate guards here; since 4ec9132 the pin_overrides breaks reach both.
Reader defects in the permit direction, a range ignored or a doctrine path read
as stamped with no row, are refused by tools/pin_of_record.py --self-test, which
runs on every path, rather than by this tool.

The --dispatch-paths codes, AUTH_DISPATCH_SITE_UNGATED, _ALLOWLIST_ABSENT,
_ALLOWLIST_UNSTAMPED, _ALLOWLIST_MALFORMED, _ALLOWLIST_REASON_MISSING,
_ALLOWLIST_ENTRY_STALE, _ALLOWLIST_COUNT_MISMATCH and _FILE_UNREADABLE, are
outside the count above: --self-test reaches each through a planted source or a
fixture allowlist in `_dispatch_cases`, and asserts each by its own code alone.

Exit codes: 0 clean, or a DEFERRED mode that checked nothing (--disjointness),
which is not a pass and must not satisfy SS-14 item 6's preflight; 1 violations
found, which --dispatch-paths returns today; 2 a governed input could not be
read, or modes combined that run one at a time.

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
import ast
import collections
import copy
import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path

try:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import gate_log
except Exception:  # telemetry must never be able to break a gate
    gate_log = None

# The pin-of-record reader is not optional the way telemetry is: without it no
# stamp can be read, so an import failure is a crash rather than a silent pass.
import pin_of_record  # noqa: E402

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
ONTOLOGY = ROOT / "ontology" / "selectors.yaml"
PSE_SCHEMA = ROOT / "schema" / "pse-event-0.1.schema.json"
TRUTH = ROOT / "synthetic" / "GROUND_TRUTH.yaml"

REL = {
    POLICY: "policy/subject-authorization.yaml",
    SCHEMA: "schema/subject-authorization.schema.json",
    REGISTER: "conformance/gate/README.md",
    LAYER_MODEL: "spec/layer-model.yaml",
    CODE_VOCABULARY: "policy/violation-codes.yaml",
    PIN: "doctrine/DOCTRINE_STATUS.md",
    ONTOLOGY: "ontology/selectors.yaml",
    PSE_SCHEMA: "schema/pse-event-0.1.schema.json",
    TRUTH: "synthetic/GROUND_TRUTH.yaml",
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

#: SS-14 item 6's list, item by item, as doctrine/SUBJECT_SELECTION.md enumerates
#: it. Until 2026-10-01 only the counts above were pinned, so swapping item 8's
#: path for one already stamped kept both counts and cleared the refusal.
RATIFY_ITEMS = (
    (1, ("doctrine/SUBJECT_SELECTION.md",)),
    (2, ("doctrine/RETENTION.md",)),
    (3, ("policy/subject-authorization.yaml", "schema/subject-authorization.schema.json")),
    (4, ("policy/retention.yaml",)),
    (5, ("ontology/selectors.yaml",)),
    (6, ("spec/pse-semantics-contract.md",)),
    (7, ("synthetic/CAST.md",)),
    (8, ("runner/dispatch_allowlist.yaml",)),
)

#: The artifacts SS-14 item 6 stamps by section rather than whole, as doctrine
#: states them. Until 2026-10-01 the reader took this from the policy's own
#: granularity text, so the policy under ratification decided how finely it was
#: stamped.
RATIFY_SECTIONS = {"spec/pse-semantics-contract.md": frozenset({"§5", "§12"})}

#: SS-14 item 6's four preflight checks, by value. Pinned by count alone until
#: 2026-10-01, so one could be swapped for a mode that always exits 0.
PREFLIGHT_CHECKS = (
    "tools/validate_authorization.py --dispatch-paths",
    "tools/validate_authorization.py --fixtures",
    "tools/validate_retention.py --policy --shred-roundtrip",
    "tools/validate_retention.py --repo-scan",
)

#: SS-14 item 6's item 2, "RETENTION.md per criterion". The subject policy
#: compiles SS criteria only, so until 2026-10-01 item 6 read RETENTION.md at
#: file granularity and a deleted RT row went unnoticed by this gate. Pinned here
#: rather than parsed from the pin, because a deleted row disappears from the
#: source being parsed.
ITEM_6_RT_CRITERIA = tuple(f"RT-{n}" for n in range(1, 20))

#: A criterion definition in a doctrine file: the bolded id and a period.
DEFINITION_RE = re.compile(r"^\*\*(SS-\d+)\.", re.M)
SUBJECT_SELECTION = ROOT / "doctrine" / "SUBJECT_SELECTION.md"
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
    "render",
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
#: A value under a selector key names its type and a label, as every corpus
#: value does. Until the third review of 2026-10-01 any bracketed text passed.
TYPED_PLACEHOLDER_RE = re.compile(r"^<[a-z_]+:[^<>]+>$")
#: The one token with no row in synthetic/GROUND_TRUTH.yaml. The cast designs no
#: bystander, so the S5 row's token is corpus-local, and conformance/gate/README.md
#: section 5 names it. A second such token is an edit here, reviewed as one.
CORPUS_LOCAL_TOKENS = ("<platform_uid:incidental-bystander-1>",)

#: A word in no vocabulary this gate reads. The self-test plants it where a
#: refusal could quote a fixture or register value, and fails a break whose
#: refusal prints it: a refusal that printed it would print a handle in the same
#: place, since a handle has no shape for _masked_text to find.
UNSHAPED_MARK = "unshaped" + "-sentinel"


def _masked_text(text) -> str:
    """Text with every email or phone shape replaced. Every Finding passes its
    where, what and moves through this, so no refusal and no telemetry record
    can print one. Until the third review of 2026-10-01 only A-01's key lists
    were masked, and four other refusals printed a shaped key or value."""
    text = str(text)
    for _, pattern in VALUE_SHAPES:
        text = pattern.sub("<an email or phone shape>", text)
    return text


#: Keys the gate corpus writes under `given` and its blocks that no schema
#: declares. A key outside these, the row contract, the two schemas and the
#: layer model is printed as undeclared rather than by name.
CORPUS_KEYS = (
    "artifacts_stamped",
    "carrier",
    "criteria_absent",
    "declares_bystanders",
    "kind",
    "override",
    "payload_family",
    "runner_environment",
    "scorecard_on_file",
    "string_in_this_file",
)
UNDECLARED_KEY = "<a key no schema or contract declares>"


def _masked(keys, vocabulary=frozenset()) -> list:
    """Keys as a refusal may print them: a key in a declared vocabulary by name,
    any other as undeclared.

    A refusal names an unexpected key, and a key can carry a selector. Until
    the second review of 2026-10-01 A-01 quoted it, which made the gate its own
    durable surface, against HY-1 and RT-19; until the fifth review of
    2026-10-02 only an email or phone shape was masked, so a handle used as a
    key was printed.
    """
    return [k if isinstance(k, str) and k in vocabulary else UNDECLARED_KEY for k in keys]


def _key_vocabulary(*documents) -> set[str]:
    """Every name declared under properties, patternProperties or $defs in the
    given documents, every key of a mapping document, and the tool's own key
    tuples."""
    out: set[str] = set(CORPUS_KEYS) | {"_where"}

    def walk(node, in_schema: bool):
        if isinstance(node, dict):
            for k, v in node.items():
                if isinstance(k, str) and not in_schema:
                    out.add(k)
                if k in ("properties", "patternProperties", "$defs", "definitions") and isinstance(v, dict):
                    out.update(x for x in v if isinstance(x, str))
                walk(v, in_schema)
        elif isinstance(node, list):
            for v in node:
                walk(v, in_schema)

    for document, in_schema in documents:
        walk(document, in_schema)
    return out

#: Every character Unicode files as a dash (category Pd) and the minus sign,
#: escaped for a character class. The fifth review of 2026-10-02 found U+2212,
#: U+FF0D and U+FE63 between the groups of a phone read as no phone, under a
#: comment that said any dash was read.
#: Characters that render as nothing or as a stop between a phone's groups:
#: the soft hyphen, the zero-width space, joiners and the word joiner, the
#: byte-order mark, middle dots, fullwidth and ideographic stops, parentheses and slash. The
#: sixth review of 2026-10-02 found each between the groups of a phone A-08 read
#: as no phone.
PHONE_STOPS = re.escape("\u00AD\u200B\u200C\u200D\u2060\uFEFF\u00B7\u2027\u30FB\uFF0E\u3002\uFF08\uFF09\uFF0F")
PHONE_DASHES = re.escape("\u002D\u058A\u05BE\u1400\u1806\u2010\u2011\u2012\u2013\u2014\u2015\u2E17\u2E1A\u2E3A\u2E3B\u2E40\u2E5D\u301C\u3030\u30A0\uFE31\uFE32\uFE58\uFE63\uFF0D\U00010D6E\U00010EAD\u2212")

#: The shapes A-08's second pass finds under any key. Email and E.164 phone are
#: the two that cannot occur by accident in a fixture's prose; a handle or an id
#: is an ordinary word and is found only under a selector key.
VALUE_SHAPES = (
    ("an email address", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")),
    # Grouped with spaces or hyphens as well as compact, since the second review
    # of 2026-10-01; a number with a 00 prefix is not read, which is stated.
    # Grouped with spaces, hyphens, dots, slashes or parentheses since the third
    # review of 2026-10-01.
    # Any space, including no-break and thin spaces, since the fourth review of
    # 2026-10-01, every dash and the minus sign since the fifth review, and the
    # invisible separators and stops in PHONE_STOPS, with a fullwidth plus, since
    # the sixth.
    ("an E.164 phone number", re.compile(r"(?<![\w+])[+\uFF0B][1-9](?:[\s.()/" + PHONE_DASHES + PHONE_STOPS + r"]*\d){7,14}(?!\d)")),
    ("a percent-encoded email address", re.compile(r"[A-Za-z0-9._%+-]+%40[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")),
)

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
#: A fixture name, as the register's first column writes it once its backticks
#: are removed.
REGISTER_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
GF_ENTRY_RE = re.compile(r"^### (GF-U\d+)\.", re.M)


#: A pipe table's delimiter row, with or without its outer pipes.
TABLE_DELIMITER_RE = re.compile(r"^ {0,3}\|?\s*:?-+:?\s*(?:\|\s*:?-+:?\s*)*\|?\s*$")
#: A line that starts another block, which ends a table body with no blank line.
TABLE_ENDS_RE = re.compile(r"^ {0,3}(?:#{1,6}(?:\s|$)|>|```|~~~|[-*+]\s|\d+[.)]\s|<|(?:[-*_]\s*){3,}$)")


#: The line the reader of 77fe6da and before took as a register row: a leading
#: pipe and a backticked name, wherever it sits. Every such line is still read.
OLD_REGISTER_ROW_RE = re.compile(r"^ {0,3}\|\s*`[a-z0-9][a-z0-9-]*`\s*\|")


def _cells(line: str) -> list[str]:
    text = line.strip()
    if text.startswith("|"):
        text = text[1:]
    if text.endswith("|") and not text.endswith("\\|"):
        text = text[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", text)]


def _register_table(block: str) -> list[list[str]]:
    """Every body row of every pipe table in the block, as its cells, read as
    GitHub renders the table: the outer pipes are optional, a backslash-escaped
    pipe is text, and the body runs to the first blank line or the next block.
    Every line the earlier reader took as a row is read as well, wherever it
    sits, so this reader reads a superset of what it read.

    Until the fourth review of 2026-10-01 a register row was read only with a
    leading pipe and a backticked name, so a contradicting row written without
    either rendered in the table and was compared with nothing. The sixth review
    of 2026-10-02 found the first version of this reader skipping three rows the
    earlier one read: a second table's header, a row after a line opening with
    HTML, and a row alone after a blank line. A table inside a blockquote is not
    read.
    """
    lines = block.splitlines()
    found: dict[int, list[str]] = {}
    i = 0
    while i < len(lines):
        header, delimiter = lines[i], lines[i + 1] if i + 1 < len(lines) else ""
        if "|" in header and "|" in delimiter and TABLE_DELIMITER_RE.match(delimiter):
            j = i + 2
            while j < len(lines) and lines[j].strip() and not TABLE_ENDS_RE.match(lines[j]):
                found[j] = _cells(lines[j])
                j += 1
            i = j
        else:
            i += 1
    for n, line in enumerate(lines):
        if n not in found and OLD_REGISTER_ROW_RE.match(line):
            found[n] = _cells(line)
    return [found[n] for n in sorted(found)]


def _register_rows(block: str) -> dict[str, list[list[str]]]:
    """Every register row's cells after the name, keyed on the name.

    Every row, not the first: until the second review of 2026-10-01 a
    contradictory second row for a name was never read.
    """
    out: dict[str, list[list[str]]] = {}
    for cells in _register_table(block):
        name = cells[0].replace("`", "").strip()
        if REGISTER_NAME_RE.match(name):
            out.setdefault(name, []).append(cells[1:])
    return out


def _register_unreadable(block: str) -> int:
    """How many register rows carry no fixture name in their first cell."""
    return sum(1 for cells in _register_table(block) if not REGISTER_NAME_RE.match(cells[0].replace("`", "").strip()))


def _quoted(value, known) -> str:
    """A value as a refusal may print it: quoted when it is a token of a
    vocabulary this gate reads, described otherwise.

    A value outside every vocabulary may be a selector, and a handle has no
    shape for _masked_text to find. Until the fourth review of 2026-10-01 eight
    refusals quoted such a value, and the register drift quoted pending ids and
    whole register cells.
    """
    if value is None or isinstance(value, bool):
        return repr(value)
    if isinstance(value, int) and 0 <= value < 100:
        return repr(value)
    if isinstance(value, str) and (value in known or PENDING_ID_RE.match(value)):
        return repr(value)
    return "a value outside every vocabulary this gate reads, not printed here"


def _held_text(ids) -> str:
    return ", ".join(
        str(i) if PENDING_ID_RE.match(str(i)) or str(i) == "determinate" else "an id outside the entry grammar"
        for i in ids
    )


def _known_tokens(model: dict) -> set[str]:
    """Every token a refusal may quote: the enums rank 3 ships, the compiled
    gate values, the code vocabulary, the subject classes, and the register's
    own words for no value and a hold."""
    collect = _d(model.get("model") or {}, "event_types", "COLLECT_EVENT", "payload", "fields", default={}) or {}
    known = {"none", "held", "determinate", "refusal_basis", "extension_basis"}
    for field in ("refusal_basis", "extension_basis", "decided_at_step", "decision", "subject_relation"):
        known |= {str(x) for x in _seq(collect, field, "enum")}
    known |= {str(x) for x in _seq(model.get("policy") or {}, "gate", "values", "enum")}
    known |= {str(x) for x in (model.get("codes") or ()) if x is not None}
    known |= set(AUTHORIZABLE_CLASSES) | set(NOT_AUTHORIZABLE)
    return known


def _register_drift(cells: list[str], row: dict, known: set[str] = frozenset()) -> list[str]:
    """Where a register row states something its fixture does not. A cell or
    a fixture value outside every vocabulary is described rather than quoted."""

    def cell(text) -> str:
        return str(text).replace("`", "").strip()

    def ids(text) -> str:
        return ", ".join(dict.fromkeys(CRITERION_RE.findall(text))) or "no criterion id"

    if len(cells) != 6:
        return [f"{len(cells)} cells after the name where the register has 6"]
    criterion, decision, step, basis, code, held = (cell(c) for c in cells)
    dec = _decision(row)
    pending = [str(x) for x in (row.get("pending") or [])]
    out: list[str] = []
    fixture_criterion = cell(row.get("criterion", ""))
    if criterion != fixture_criterion:
        if ids(criterion) != ids(fixture_criterion):
            out.append(f"a criterion citing {ids(criterion)} where the fixture cites {ids(fixture_criterion)}")
        else:
            out.append(f"a criterion worded unlike the fixture's, both citing {ids(criterion)}")
    for label, stated, value in (
        ("decision", decision, dec.get("value")),
        ("step", step, dec.get("decided_at_step")),
        ("basis", basis, dec.get("basis")),
        ("code", code, row.get("expect_code")),
    ):
        if value in (None, ""):
            ok = stated == "none" or (stated == "held" and bool(pending))
        else:
            ok = stated == str(value)
        if not ok:
            out.append(f"{label} {_quoted(stated, known)} where the fixture states {_quoted(value, known)}")
    want = ", ".join(pending) if pending else "determinate"
    if held != want:
        stated_ids = [p.strip() for p in held.split(",")]
        out.append(
            f"held on '{_held_text(stated_ids)}' where the fixture states "
            f"'{_held_text(pending) if pending else 'determinate'}'"
        )
    return out

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
        "code field as the violation code, so a mode cannot ride there. --self-test and, "
        "since Step 10, --dispatch-paths record under the kernel gate entry's own token, so "
        "neither dilutes the designed refusal rate of --fixtures."
    ),
    "VA-R5": (
        "--dispatch-paths, drafted at Step 10, takes VA-U2's third option, refusing on the "
        "absence of runner/dispatch_allowlist.yaml, and VA-U3's first and third together: a "
        "syntactic walk that requires each site to sit behind a permits check on a decision "
        "evaluate() returned in the same function, and a reconcile of the allowlist against the "
        "sites in both directions, with a count per function so a second call cannot ride on "
        "one entry. Both entries stay open until the operator stamps them, and VA-U2's and "
        "VA-U3's sentences describe the state before this draft."
    ),
    "VA-R6": (
        "Applied 2026-10-28 as the session's reading, in code, beside the DA-R2 allowlist "
        "draft, and awaiting the operator's class: B as a precision rule of this scanner (a "
        "patch target in a test module opens nothing, and the plants prove a patch whose "
        "replacement dispatches is still a site), or F as an exemption from the bypass check, "
        "in which case the rule comes out and the four patch references in "
        "app/tests/test_http.py join the allowlist draft. --dispatch-paths, "
        "amended for the application's tests and applied only in a test module, which is a "
        "test_*.py file or conftest.py under a tests/ directory: a reference to a dispatch "
        "pattern is not a site when it is the object a patch replaces an attribute on (the first "
        "argument or target keyword of the builtin setattr or delattr, of a method so named on a "
        "receiver named monkeypatch or mp, or of unittest.mock.patch.object or mock.patch.object "
        "resolved through the imports), the object of an attribute assigned or deleted, or a read "
        "of a non-dunder attribute that the same function or module body patches or assigns by "
        "its literal name and that is not called where it is read, which is the patch keeping the "
        "original it replaces. None of the three stores the pattern or calls it in place. Outside "
        "a test module every such reference stays a site, so a module under runner/, connectors/ "
        "or app/ that swaps a dispatch attribute and keeps its original is refused. A reference "
        "passed as any other argument, the value a patch installs and functools.partial's "
        "argument included, a capture of the dispatch callable itself, a dunder, and any "
        "reference to runner.subject_guard.Decision stay sites. The builtin names count only "
        "where the scope does not rebind them, and a monkeypatch-named receiver whose setattr "
        "calls its first argument would pass, which the block comment above DISPATCH_PATTERNS "
        "states."
    ),
}


class Finding:
    __slots__ = ("code", "where", "detail", "moves")

    def __init__(self, code: str, where: str, detail: str, moves: str):
        self.code = code
        self.where = _masked_text(where)
        self.detail = _masked_text(detail)
        self.moves = _masked_text(moves)

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
# The pin of record. One reader, tools/pin_of_record.py, shared with
# validate_retention.py and validate_doctrine.py since 2026-10-01, when the Step 8
# review found the three tools read the pin three ways and one dated row naming a
# path stamped the whole file. Its READINGS state each predicate. This tool adds
# one thing: the per-item granularity SS-14 item 6 compiles, so the contract is
# stamped by its sections 5 and 12.
# ---------------------------------------------------------------------------

Pin = pin_of_record.Pin

#: SS-14 item 7's artifact, which binds only "with a sealed, hash-pinned
#: GROUND_TRUTH.yaml carrying at least one designed confuser pair". Until
#: 2026-10-01 that clause lived only in the policy's granularity prose and no
#: check read it, so stamping CAST.md would have cleared item 7 on an unsealed
#: cast. The completeness critic of that date found it.
CAST_PATH = "synthetic/CAST.md"
CONFUSER_CODES = (
    "CAST_NO_CONFUSER_PAIR",
    "CAST_CONFUSER_PAIR_WITHIN_ONE_PERSONA",
    "CAST_CONFUSER_PAIR_NOT_DISTINCT",
    "CAST_CONFUSER_SHARES_LINKED_DOMAIN",
)


def cast_seal_reason() -> str:
    """'' when the cast is sealed, its hash verifies and it has a confuser pair.

    Read through tools/validate_cast.py's own checks rather than a copy of them.
    """
    try:
        import validate_cast as vc

        raw = vc.CAST.read_text(encoding="utf-8")
        model = yaml.safe_load(raw) if yaml is not None else None
    except Exception as exc:  # an unreadable cast is an unmet condition
        return f"the cast could not be read ({exc.__class__.__name__})"
    if not isinstance(model, dict) or not vc.is_sealed(model):
        return "the cast is not sealed"
    if vc.check_seal_fields(model) or vc.check_seal_hash(model, raw):
        return "the cast's seal or its recorded hash does not verify"
    if any(f.code in CONFUSER_CODES for f in vc.check_structure(model)):
        return "the cast carries no valid designed confuser pair"
    return ""


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
        if CAST_PATH in stamped and cast_seal_reason():
            stamped.discard(CAST_PATH)

    def _why(p: str) -> str:
        if p == CAST_PATH and source != "fixture" and pin.artifact_stamped(p):
            return f"{p} is stamped and {cast_seal_reason()}, so SS-14 item 6's condition on it is unmet"
        return f"{p} is unstamped in the pin of record: {pin.reason_unstamped(p) or 'the stamp state omits it'}"

    reasons = [_why(p) for p in paths if p not in stamped]
    rows = getattr(pin, "criteria", {}) if source != "fixture" else {}
    # A fixture supplies criteria_absent, so an entry outside the criterion
    # grammar is described rather than printed, since the sixth review of
    # 2026-10-02 found A-18 printing it.
    reasons += [
        f"criterion {c} has a Step 3 row, and no dated range or Ratified row covers it"
        if c in rows
        else f"criterion {c if CRITERION_RE.fullmatch(str(c)) else 'outside the criterion grammar'} has no row in the stamp table"
        for c in absent
    ]
    return reasons


# ---------------------------------------------------------------------------
# Loading. The model is one dict so --self-test can mutate it in memory.
# ---------------------------------------------------------------------------


class Unreadable(Exception):
    def __init__(self, code: str, where: str, detail: str, moves: str):
        super().__init__(code)
        self.finding = Finding(code, where, detail, moves)


def _read(path: Path) -> str:
    rel = REL.get(path, str(path))
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        # Until 2026-10-01 this ended in a traceback and exit 1.
        raise Unreadable(
            "AUTH_INPUT_UNPARSEABLE",
            rel,
            f"the file is not valid UTF-8 (byte {exc.start}: {exc.reason}), so the "
            "entries this gate reconciles cannot be read",
            f"re-save {rel} as UTF-8; or move the authorization gate to PENDING in "
            "tools/validate_conformance.py",
        ) from exc
    except OSError as exc:
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


def _json(path: Path):
    rel = REL.get(path, str(path))
    try:
        return json.loads(_read(path))
    except json.JSONDecodeError as exc:
        raise Unreadable(
            "AUTH_INPUT_UNPARSEABLE",
            rel,
            f"the file is not valid JSON (line {exc.lineno}, column {exc.colno}), so the "
            "names this gate may print cannot be read",
            f"fix the JSON at the reported location in {rel}",
        ) from exc


def _selector_types() -> list[str]:
    """The registry's selector types. A key that is not a string is a refusal by
    name: until the fifth review of 2026-10-02 it ended --fixtures in a
    TypeError traceback."""
    selectors = _yaml(ONTOLOGY).get("selectors") or {}
    if not isinstance(selectors, dict) or not all(isinstance(k, str) for k in selectors):
        raise Unreadable(
            "AUTH_INPUT_UNPARSEABLE",
            "ontology/selectors.yaml",
            "the registry's selectors block is not a mapping keyed by type names, so "
            "the selector types a record may name cannot be read",
            "restore the selectors mapping in ontology/selectors.yaml, one string key "
            "per selector type",
        )
    return sorted(selectors)


def _truth_tokens() -> list[str]:
    """Every typed placeholder synthetic/GROUND_TRUTH.yaml carries as a value,
    read as YAML so that a comment cannot add one, with the corpus-local token.

    Until the fourth review of 2026-10-01 TYPED_PLACEHOLDER_RE bound a value's
    type and never its label, so a live handle written as the label of a typed
    placeholder passed A-08.
    """
    found: set[str] = set(CORPUS_LOCAL_TOKENS)

    def walk(node):
        if isinstance(node, dict):
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
        elif isinstance(node, str) and TYPED_PLACEHOLDER_RE.match(node):
            found.add(node)

    walk(_yaml(TRUTH))
    return sorted(found)


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
        "register": list(_register_rows(register_block)),
        "register_rows": _register_rows(register_block),
        "register_unreadable": _register_unreadable(register_block),
        "register_block": register_block,
        # The registry's selector types, which a record selector's type must be
        # one of, since the fourth review of 2026-10-01.
        "selector_types": _selector_types(),
        "key_vocabulary": sorted(
            _key_vocabulary((schema, True), (_json(PSE_SCHEMA), True), (_yaml(LAYER_MODEL), False))
            | set(ROW_KEYS)
            | set(GIVEN_KEYS)
            | set(DECISION_KEYS)
            | set(SELECTOR_KEYS)
        ),
        # The cast's own tokens, which a typed placeholder must be one of.
        "cast_tokens": _truth_tokens(),
        "gf_entries": set(GF_ENTRY_RE.findall(register_text)),
        "pin_text": _read(PIN),
        "ss_defined": DEFINITION_RE.findall(_read(SUBJECT_SELECTION)),
    }


def _pin(model: dict, text: str | None = None) -> Pin:
    """The pin of record, or a constructed copy of it when `text` is given.

    `pin_overrides` is the self-test's seam: it replaces a reader method on the
    instance so a break can show which check notices a reader that answers
    wrongly. `load()` never sets it.
    """
    pin = Pin(
        model.get("pin_text", "") if text is None else text,
        ROOT,
        {k: set(v) for k, v in RATIFY_SECTIONS.items()},
    )
    for name, fn in (model.get("pin_overrides") or {}).items():
        setattr(pin, name, fn)
    return pin


def _in_slice(text: str, start: str, end: str, edit) -> str:
    i = text.find(start)
    if i < 0:
        return text
    j = text.find(end, i + len(start))
    j = len(text) if j < 0 else j
    return text[:i] + edit(text[i:j]) + text[j:]


def _constructed_pin_text(text: str, stamp: list[str], clear: list[str], drop_criterion: str = "") -> str:
    """A copy of the pin of record for A-19's cases read through the pin.

    Rows naming a path in `clear` are removed from the Ratified and Pending
    tables, one whole-artifact row is added for each path in `stamp`, and the
    Step 3 row of `drop_criterion` is removed. Nothing is written to disk.
    """

    def _without(block: str) -> str:
        return "\n".join(
            line for line in block.split("\n") if not any(f"`{c}`" in line for c in clear)
        )

    rows = "".join(
        f"| the constructed control, whole artifact | `{p}` | v0.1 | 2026-10-01 | unstamped | operator |\n"
        for p in stamp
    )
    text = _in_slice(
        text,
        pin_of_record.RATIFIED_START,
        pin_of_record.RATIFIED_END,
        lambda block: _without(block).rstrip("\n") + "\n" + rows + "\n",
    )
    text = _in_slice(text, pin_of_record.PENDING_START, pin_of_record.PENDING_END, _without)
    if drop_criterion:
        row = re.compile(rf"^\|\s*{re.escape(drop_criterion)}(?![0-9])[^\n]*\n?", re.M)
        text = _in_slice(
            text,
            pin_of_record.CRITERIA_START,
            pin_of_record.CRITERIA_END,
            lambda block: row.sub("", block),
        )
    return text


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
    known = _known_tokens(model)
    vocabulary = frozenset(model.get("key_vocabulary") or ())
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

    # A-10's artifact half. Until 2026-10-01 schema.required was read into a
    # variable nothing compared, so SS-5's three fields could leave it unrefused.
    shape = []
    if set(schema_required) != set(RECORD_FIELDS):
        shape.append(f"required lists {sorted(schema_required)}")
    if set(schema_props) != set(RECORD_FIELDS):
        shape.append(f"properties declares {sorted(schema_props)}")
    if not schema_closed:
        shape.append("additionalProperties is not false")
    if shape:
        f.append(
            Finding(
                "AUTH_SCHEMA_RECORD_SHAPE_DRIFT",
                "schema/subject-authorization.schema.json",
                "the schema's record shape is not SS-4's nine fields, closed: "
                + "; ".join(shape)
                + ". SS-4 refuses a partial authorization, and the schema's own "
                "partial_is_refused block says so",
                "restore the nine names to required and properties and set "
                "additionalProperties false; or ratify an SS-4 amendment and move "
                "RECORD_FIELDS in this tool in the same commit",
            )
        )

    selector_props = _d(schema, "$defs", "selector", "properties", default={})
    selector_fields = sorted(map(str, selector_props)) if isinstance(selector_props, dict) else [repr(selector_props)]
    if selector_fields != ["selector_type", "value"]:
        f.append(
            Finding(
                "AUTH_SCHEMA_BOUND_DRIFT",
                "schema/subject-authorization.schema.json > $defs.selector.properties",
                f"a selector declares {selector_fields} where SAS-R5 fixes selector_type and "
                "value. A third field is a new place for a selector value to sit, and the "
                "closure check reads only additionalProperties",
                "restore the two fields; or ratify SAS-R5's change and move this check in "
                "the same commit",
            )
        )
    for path, want, owner in SCHEMA_NODE_PINS:
        node = schema
        for part in path:
            node = node.get(part) if isinstance(node, dict) else None
        if json.dumps(_without_comments(node), sort_keys=True) != json.dumps(want, sort_keys=True):
            f.append(
                Finding(
                    "AUTH_SCHEMA_BOUND_DRIFT",
                    "schema/subject-authorization.schema.json > " + ".".join(path),
                    f"the node differs from what {owner} fixes, with its comments set aside. "
                    "A keyword added beside the pinned ones can widen it as surely as a "
                    "pinned one changed",
                    f"restore the node; or ratify {owner} with a dated stamp in "
                    "doctrine/DOCTRINE_STATUS.md and move SCHEMA_NODE_PINS in the same commit",
                )
            )
    for path, want, owner in SCHEMA_PINS:
        have = _schema_value(schema, path)
        if json.dumps(have, sort_keys=True) != json.dumps(want, sort_keys=True):
            f.append(
                Finding(
                    "AUTH_SCHEMA_BOUND_DRIFT",
                    "schema/subject-authorization.schema.json > " + ".".join(path),
                    (
                        f"the schema carries {have!r} at that path, where {owner} requires "
                        "the key to be absent"
                        if want is None
                        else f"the schema carries {have!r} where {owner} fixes {want!r}"
                    )
                    + ". A widened bound or an opened refusal admits records the stamped "
                    "doctrine refuses, and the schema names this tool as what refuses its drift",
                    (
                        f"remove {'.'.join(path)}"
                        if want is None
                        else f"restore {want!r}"
                    )
                    + f"; or ratify {owner} with a dated stamp in doctrine/DOCTRINE_STATUS.md "
                    "and move SCHEMA_PINS in this tool in "
                    "the same commit",
                )
            )

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
            extra = _masked(sorted(present - set(ROW_KEYS), key=str), vocabulary)
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

        # A-01 inside the two blocks. Until 2026-10-01 DECISION_KEYS and
        # GIVEN_KEYS were declared and read by nothing, so an input the gate
        # reads could be deleted from `given` with the output unchanged.
        for block, keys, code in (
            ("expect_decision", DECISION_KEYS, "AUTH_DECISION_KEYS_UNEXPECTED"),
            ("given", GIVEN_KEYS, "AUTH_GIVEN_KEYS_UNEXPECTED"),
        ):
            value = row.get(block)
            have = set(value) if isinstance(value, dict) else set()
            if not isinstance(value, dict) or have != set(keys):
                f.append(
                    Finding(
                        code,
                        f"{where} > {block}",
                        f"the row's {block} is not the {len(keys)} keys the row contract "
                        "fixes"
                        + (f", missing {sorted(set(keys) - have)}" if set(keys) - have else "")
                        + (f", carrying {_masked(sorted(have - set(keys), key=str), vocabulary)}" if have - set(keys) else "")
                        + ". A missing key is an input or an assertion the fixture never "
                        "supplied, and an extra one is something nothing grades",
                        f"restore the keys in conformance/gate/README.md section 3; or add "
                        f"a new one to the contract, to every row and to {'DECISION_KEYS' if block == 'expect_decision' else 'GIVEN_KEYS'} "
                        "in tools/validate_authorization.py in one commit",
                    )
                )
        content = (row.get("given") or {}).get("collected_content") if isinstance(row.get("given"), dict) else None
        if isinstance(content, dict) and content.get("string_in_this_file") is not False:
            f.append(
                Finding(
                    "AUTH_PAYLOAD_STRING_CLAIMED",
                    f"{where} > given.collected_content.string_in_this_file",
                    "the row claims the collected content's string sits in this file. No "
                    "collected string enters a tracked file: the corpus describes the "
                    "content by family and never carries it, per AGENTS.md section 4",
                    "set string_in_this_file false and describe the content by its family",
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
                    f"the row asserts {_quoted(value, known)}, which the compiled gate enum does not "
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
                    f"the row asserts step {_quoted(step, known)} and SS-8's order is stamped at six "
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
                        f"the row records a basis under {_quoted(basis_field, known)}, and the wire "
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
                        f"the row asserts basis {_quoted(b, known)} under {basis_field}, which rank 3 "
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
                    f"the row asserts relation {_quoted(relation, known)}. SS-10 closes the computed "
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
                    f"the row expects {_quoted(code, known)} and policy/violation-codes.yaml does not "
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
        # The sentence compiled for this row's value, and the item 6 refusal only
        # on a REFUSED row whose basis is that item. Until 2026-10-01 any compiled
        # sentence was accepted for any value, so a REFUSED row could render that
        # the run proceeds.
        allowed = {_norm(consequences[dec.get("value")])} if consequences.get(dec.get("value")) else set()
        if dec.get("value") == "REFUSED" and dec.get("basis") == "never_item":
            allowed.add(_norm(never_refusal))
        if render and _norm(render) not in allowed:
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
                        f"the row is held on {repr(held_id) if PENDING_ID_RE.match(str(held_id)) else 'an id that is not an entry id, not printed here'}, and no entry of that id exists in "
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
                        f"the record names class {_quoted(klass, known)}. SS-1 marks S5 not authorizable "
                        "and SS-4 excludes it from this field, so a record naming it is an "
                        "authorization for a class no authorization reaches",
                        "name one of " + ", ".join(AUTHORIZABLE_CLASSES) + " with the "
                        "evidence that class requires; or, for a person who arrived "
                        "incidentally, open a new case with their own written record, which "
                        "is a decision rather than a refusal",
                    )
                )

        f += _placeholder_findings(
            row,
            where,
            frozenset(model.get("selector_types") or ()),
            frozenset(model.get("cast_tokens") or ()),
            vocabulary,
        )

    for number, (field, names) in enumerate(sorted(undeclared_fields.items()), 1):
        # A field name can itself be a selector, so it is never printed; the
        # fourth review of 2026-10-01 found a handle-named field in the refusal
        # and in the telemetry record.
        f.append(
            Finding(
                "AUTH_RECORD_FIELD_UNDECLARED",
                f"conformance/gate/ > authorization, undeclared field {number}",
                f"{len(names)} record(s) carry a field, not printed here, which "
                "schema/subject-authorization.schema.json does not declare while setting "
                "additionalProperties false. The corpus records are therefore not "
                "instances of the schema they are graded against, and the drift runs in "
                "exactly one direction, which is the shape the doctrine gate's own D-01 "
                "defect took",
                "remove the field from the records; or declare it in the schema and record "
                "the decision that adds it, since the schema closes SS-4's nine-field table "
                "and a tenth field is an amendment to that table rather than a shape choice",
            )
        )

    # -- A-12. SS-5's three fields, and the one-field property ---------------
    f += _ss5_findings(rows, vocabulary)

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
    # A-13's columns. Until 2026-10-01 only the name column was read, so a
    # register row could state another criterion, decision, step, basis, code
    # or hold than its fixture and the summary still said reconciled.
    by_name = {r.get("name"): r for r in rows}
    unreadable = model.get("register_unreadable") or 0
    if unreadable:
        f.append(
            Finding(
                "AUTH_REGISTER_ROW_UNNAMED",
                "conformance/gate/README.md section 4",
                f"{unreadable} row(s) of the register table carry no fixture name in the "
                "first column, so each renders as a statement about a fixture and is "
                "compared with nothing. The cell is not printed here",
                "write the fixture's name in the first column, in backticks as the other "
                "rows do; or remove the row",
            )
        )
    for name, rows_for_name in sorted((model.get("register_rows") or {}).items()):
        if len(rows_for_name) > 1:
            f.append(
                Finding(
                    "AUTH_REGISTER_NAME_DUPLICATE",
                    f"conformance/gate/README.md section 4 > {name}",
                    f"the register lists {name} {len(rows_for_name)} times, so a reader "
                    "checking a fixture against it finds two statements of one row",
                    "keep one row for the name; a matched pair is two names, as the SS-17 "
                    "baseline pair is",
                )
            )
        if name not in by_name:
            continue
        drift = [d for cells in rows_for_name for d in _register_drift(cells, by_name[name], known)]
        if drift:
            f.append(
                Finding(
                    "AUTH_REGISTER_ROW_DRIFT",
                    f"conformance/gate/README.md section 4 > {name}",
                    f"the register row states {'; '.join(drift)}. The register is what "
                    "a reader checks a fixture against, and a row that contradicts its "
                    "fixture certifies a case the corpus does not carry",
                    "correct whichever of the two is wrong, in the same commit as the "
                    "reason; the register writes none for no value, held for a value a "
                    "held row leaves open, and determinate for an empty hold",
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


def _placeholder_findings(
    row: dict,
    where: str,
    selector_types: frozenset = frozenset(),
    cast_tokens: frozenset = frozenset(),
    vocabulary: frozenset = frozenset(),
) -> list[Finding]:
    """A-08. Every selector-keyed value is one of the cast's typed tokens, and no
    string or key anywhere in a row carries an email or phone shape.

    A token is one synthetic/GROUND_TRUTH.yaml carries, or the corpus-local
    token conformance/gate/README.md section 5 names. Until the fourth review of
    2026-10-01 any text of the form <type:label> passed, live handle or not. An
    empty token set refuses every value, so a truth file that cannot be read
    fails closed.

    Until the second review of 2026-10-01 the second pass removed bracketed
    spans before it looked, so an address written "Name <address>" passed, and a
    bracketed address under a selector key counted as a placeholder.

    `argv_template` is the one exemption and it is named rather than inferred: it
    carries a selector type such as `<handle>` rather than a selector, which is
    the template the shipped must-pass corpus already holds.
    """
    out: list[Finding] = []
    seen: list[str] = []

    def seg(k) -> str:
        # A refusal locates the value by its key path, and a key can carry a
        # selector, so an undeclared key is named as undeclared. Until the
        # fifth review of 2026-10-02 a handle used as a record field was
        # printed here and written to the gate log.
        return k if isinstance(k, str) and k in vocabulary else UNDECLARED_KEY

    def walk(node, path: str, key: str | None, typed: bool):
        if isinstance(node, dict):
            # `value` is a selector only where its object also names the type.
            # The gate's own `expect_decision.value` is a decision, and the
            # register's `value` columns are prose.
            pair = "selector_type" in node
            for k, v in node.items():
                walk(v, f"{path}.{seg(k)}", k, pair)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{path}[{i}]", key, typed)
        elif isinstance(node, str) and key in SELECTOR_KEYS:
            if key == "value" and not typed:
                return
            shaped = any(pattern.search(node) for _, pattern in VALUE_SHAPES)
            if (shaped or node not in cast_tokens) and path not in seen:
                seen.append(path)
        elif isinstance(node, (int, float)) and not isinstance(node, bool) and key in SELECTOR_KEYS:
            # A selector written as a number, such as a phone without quotes.
            if (key != "value" or typed) and path not in seen:
                seen.append(path)

    walk({k: v for k, v in row.items() if k != "_where"}, "", None, False)

    # A record selector is an object of exactly selector_type and value, and a
    # selector key holds a string. Until the third review of 2026-10-01 a bare
    # string, a pair as a list, a "type" key or a mapping under value passed.
    record = row.get("authorization")
    if record is not None and not isinstance(record, dict):
        # Until the fourth review of 2026-10-01 a record written as a list or a
        # string skipped every check below it.
        seen.append(".authorization")
    elif isinstance(record, dict) and "selectors" in record and not isinstance(record.get("selectors"), list):
        seen.append(".authorization.selectors")
    for i, entry in enumerate(_seq(record, "selectors") if isinstance(record, dict) else []):
        well_formed = (
            isinstance(entry, dict)
            and set(entry) == {"selector_type", "value"}
            and isinstance(entry.get("value"), str)
            and isinstance(entry.get("selector_type"), str)
            and entry["selector_type"] in selector_types
        )
        if not well_formed and f".authorization.selectors[{i}]" not in seen:
            seen.append(f".authorization.selectors[{i}]")

    def nested(node, path: str, key, typed: bool):
        if isinstance(node, dict):
            pair = "selector_type" in node
            for k, v in node.items():
                if k in SELECTOR_KEYS and (k != "value" or pair):
                    if isinstance(v, dict) or (isinstance(v, list) and not all(isinstance(x, str) for x in v)):
                        if f"{path}.{seg(k)}" not in seen:
                            seen.append(f"{path}.{seg(k)}")
                nested(v, f"{path}.{seg(k)}", k, pair)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                nested(v, f"{path}[{i}]", key, typed)

    nested({k: v for k, v in row.items() if k != "_where"}, "", None, False)

    # The second pass: a shape under any key.
    def shapes(node, path: str):
        if isinstance(node, dict):
            for k, v in node.items():
                if isinstance(k, str) and any(p.search(k) for _, p in VALUE_SHAPES) and f"{path} key" not in seen:
                    seen.append(f"{path} key")
                shapes(v, f"{path}.{seg(k)}")
        elif isinstance(node, list):
            for i, v in enumerate(node):
                shapes(v, f"{path}[{i}]")
        elif isinstance(node, str):
            if any(pattern.search(node) for _, pattern in VALUE_SHAPES) and path not in seen:
                seen.append(path)

    shapes({k: v for k, v in row.items() if k != "_where"}, "")
    for path in seen:
        out.append(
            Finding(
                "AUTH_VALUE_NOT_PLACEHOLDER",
                f"{where} > {path.lstrip('.')}",
                "a selector-keyed value is not one of the cast's typed tokens, or an email "
                "or phone shape sits under some key. SS-14 item 5 keeps "
                "a natural person's selector out of every tracked file, and a synthetic "
                "value is still a value while the cast is unsealed. The value itself is not "
                "quoted here, on the HY-1 rule that a gate's own evidence must not become "
                "the durable surface the gate exists to prevent",
                "replace the value with a typed token copied from "
                "synthetic/GROUND_TRUTH.yaml, or with the corpus-local token "
                "conformance/gate/README.md section 5 names; or, once the operator seals "
                "the cast, fill the corpus from the sealed truth file in one reproducible "
                "step",
            )
        )
    return out


#: The gate inputs SS-5's one-field comparison reads. The rest of a row is its
#: name, its assertion and its hold, none of which the gate is given.
SS5_INPUTS = ("authorization", "chain", "dispatch", "given", "evaluated_at")

#: Keys whose values are a row's own identifiers. Each is a uuid5 of a label, so
#: a mutated fixture carries its own; the comparison pairs them by position and
#: renames them before it compares, and the pairing must be one to one.
SS5_ID_KEYS = ("event_id", "run_id", "item_id")

UUID_RE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")


#: What an empty container reads as, so its presence and type are compared.
#: Until the second review of 2026-10-01 an empty list or mapping yielded no
#: leaf, and a key holding one could be added or removed unseen.
EMPTY_MAP = ("<empty>", "map")
EMPTY_LIST = ("<empty>", "list")


def _leaves(x, path: tuple = ()):
    if isinstance(x, dict):
        if not x:
            yield path, EMPTY_MAP
        for k, v in x.items():
            yield from _leaves(v, path + (k,))
    elif isinstance(x, list):
        if not x:
            yield path, EMPTY_LIST
        for i, v in enumerate(x):
            yield from _leaves(v, path + (i,))
    else:
        yield path, x


def _typed(value):
    """A leaf as its type and value, so true and 1, or false and 0, differ."""
    return (type(value).__name__, value)


def _path_text(path: tuple, vocabulary=None) -> str:
    """A key path as a refusal prints it. With a vocabulary, a key outside it is
    named as undeclared, since the sixth review of 2026-10-02 found A-12 printing
    a handle used as a record field or a chain payload key."""

    def seg(p) -> str:
        if isinstance(p, int):
            return f"[{p}]"
        if vocabulary is not None and not (isinstance(p, str) and p in vocabulary):
            return "." + UNDECLARED_KEY
        return f".{p}"

    return "".join(seg(p) for p in path).lstrip(".")


def _renamed(x, names: dict):
    if isinstance(x, dict):
        return {k: _renamed(v, names) for k, v in x.items()}
    if isinstance(x, list):
        return [_renamed(v, names) for v in x]
    if isinstance(x, str):
        return UUID_RE.sub(lambda m: names.get(m.group(0), m.group(0)), x)
    return x


#: The schema's bounds and refusing forms, pinned by value. Until 2026-10-01 the
#: self-lint the schema names checked its required list, its property names and
#: its closure, so an emptied enum could be opened, evidence_ref's refusal turned
#: into "any value", and minItems or minimum dropped with every gate green.
#: Opening selector_type answers SAS-U1 by edit, and evidence_ref answers SA-U2
#: and SA-U11, which are class F. Each pin moves only with its entry's stamp.
SCHEMA_PINS = (
    (("type",), "object", "the closed record of SS-4 and A-10"),
    (("patternProperties",), None, "the closed record of SS-4 and A-10"),
    (("unevaluatedProperties",), None, "the closed record of SS-4 and A-10"),
    (("properties", "selectors", "prefixItems"), None, "SAS-R5"),
    (("properties", "case_id"), {"$ref": "#/$defs/uuid"}, "SAS-R6"),
    (("properties", "authorized_on"), {"$ref": "#/$defs/utcDate"}, "SAS-R6"),
    (("properties", "expires_on"), {"$ref": "#/$defs/utcDate"}, "SAS-R6"),
    (("properties", "purpose", "type"), "string", "SAS-R4"),
    (("properties", "authorized_by", "type"), "string", "SAS-R4"),
    (("$defs", "selector", "type"), "object", "SAS-R5"),
    (("$defs", "selector", "patternProperties"), None, "SAS-R5"),
    (("$defs", "selector", "unevaluatedProperties"), None, "SAS-R5"),
    (("$defs", "selector", "properties", "value", "type"), "string", "SAS-R5"),
    (("$defs", "uuid", "type"), "string", "SAS-R6"),
    (("$defs", "utcDate", "type"), "string", "SAS-R6"),
    (("properties", "selectors", "type"), "array", "SAS-R5"),
    (("properties", "selectors", "minItems"), 1, "SAS-R4"),
    (("properties", "selectors", "items"), {"$ref": "#/$defs/selector"}, "SAS-R5"),
    (("properties", "pivot_depth_max", "type"), "integer", "SAS-R6"),
    (("properties", "pivot_depth_max", "minimum"), 0, "SAS-R6"),
    (("properties", "purpose", "minLength"), 1, "SAS-R4"),
    (("properties", "purpose", "pattern"), "\\S", "SAS-R4"),
    (("properties", "authorized_by", "minLength"), 1, "SAS-R4"),
    (("properties", "authorized_by", "pattern"), "\\S", "SAS-R4"),
    (("properties", "evidence_ref"), {"not": {}}, "SA-U2 and SA-U11"),
    (("$defs", "selector", "required"), ["selector_type", "value"], "SAS-R5"),
    (("$defs", "selector", "additionalProperties"), False, "SAS-R5"),
    (("$defs", "selector", "properties", "selector_type", "enum"), [], "SAS-U1"),
    (("$defs", "selector", "properties", "value", "minLength"), 1, "SAS-R4"),
    (("$defs", "selector", "properties", "value", "pattern"), "\\S", "SAS-R4"),
    (
        ("$defs", "utcDate", "pattern"),
        "^(19[7-9][0-9]|2[0-9]{3})-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$",
        "SAS-R6",
    ),
    (
        ("$defs", "uuid", "pattern"),
        "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$",
        "SAS-R6",
    ),
)


#: The two selector nodes whole, comments stripped at every depth. Pinning
#: their keywords one by one missed prefixItems, which in draft 2020-12 takes
#: the leading positions from items and so removes the closure and SAS-U1's
#: empty enum for selectors[0] without touching any pinned keyword.
SCHEMA_NODE_PINS = (
    (
        ("properties", "selectors"),
        {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/selector"}},
        "SAS-R4 and SAS-R5",
    ),
    (
        ("$defs", "selector"),
        {
            "type": "object",
            "required": ["selector_type", "value"],
            "additionalProperties": False,
            "properties": {
                "selector_type": {"type": "string", "enum": []},
                "value": {"type": "string", "minLength": 1, "pattern": "\\S"},
            },
        },
        "SAS-R4, SAS-R5 and SAS-U1",
    ),
)


def _without_comments(node):
    if isinstance(node, dict):
        return {k: _without_comments(v) for k, v in node.items() if k != "$comment"}
    if isinstance(node, list):
        return [_without_comments(v) for v in node]
    return node


def _schema_value(schema: dict, path: tuple):
    node = schema
    for part in path:
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    if isinstance(node, dict):
        return {k: v for k, v in node.items() if k != "$comment"}
    return node


def _ss5_input_delta(row: dict, base: dict, field: str, vocabulary=None) -> list[str]:
    """Every gate input in which `row` differs from `base`, other than `field`.

    Until 2026-10-01 A-12 compared the authorization record alone, so a fixture
    could differ from its baseline in the chain, the dispatch, the given inputs
    or the instant and still count as SS-5's one-field mutation; one did, in an
    item's locator. The field is exempt in the record and in any chain payload
    that carries a copy, and a copy that disagrees with its own row's record is
    a difference. Identifiers are renamed through the pairing above, so a
    reference that points at a different event after renaming is a difference.
    """
    a = {k: row.get(k) for k in SS5_INPUTS}
    b = {k: base.get(k) for k in SS5_INPUTS}
    out: list[str] = []
    fwd: dict = {}
    back: dict = {}
    lb = dict(_leaves(b))
    for path, va in _leaves(a):
        vb = lb.get(path)
        if path and path[-1] in SS5_ID_KEYS and isinstance(va, str) and isinstance(vb, str):
            if fwd.setdefault(va, vb) != vb or back.setdefault(vb, va) != va:
                out.append(f"{_path_text(path, vocabulary)} (its identifiers do not pair one to one)")
    # A reference copied from the baseline names an event the fixture's own
    # chain does not carry. Until the second review of 2026-10-01 it compared
    # equal to the baseline and passed.
    own = {v for p, v in _leaves(a) if p and p[-1] in SS5_ID_KEYS and isinstance(v, str)}
    theirs = {v for p, v in lb.items() if p and p[-1] in SS5_ID_KEYS and isinstance(v, str)}
    for path, va in _leaves(a):
        if isinstance(va, str):
            for found in UUID_RE.findall(va):
                if found in theirs and found not in own:
                    out.append(f"{_path_text(path, vocabulary)} (refers to the baseline's identifier)")
                    break
    a = _renamed(a, fwd)
    for name, side in (("fixture", a), ("baseline", b)):
        if not isinstance(side.get("chain"), (list, type(None))):
            out.append(f"chain (the {name}'s chain is not a list)")
            side["chain"] = []

    def payload_at(side, i):
        chain = side.get("chain") or []
        event = chain[i] if i < len(chain) else None
        payload = event.get("payload") if isinstance(event, dict) else None
        return payload if isinstance(payload, dict) else None

    record_a = a.get("authorization")
    value = record_a.get(field) if isinstance(record_a, dict) else None
    length = max(len(a.get("chain") or []), len(b.get("chain") or []))
    for i in range(length):
        pa, pb = payload_at(a, i), payload_at(b, i)
        has_a = pa is not None and field in pa
        has_b = pb is not None and field in pb
        if has_a and not _same_typed(pa[field], value):
            out.append(f"chain[{i}].payload.{field} (disagrees with the record)")
        if has_a != has_b:
            # Until the second review of 2026-10-01 a copy deleted from one side
            # or added to the other was stripped on both and passed.
            out.append(f"chain[{i}].payload.{field} (present on one side)")
            continue
        if has_a:
            for side in (a, b):
                event = side["chain"][i]
                side["chain"] = list(side["chain"])
                side["chain"][i] = {**event, "payload": {k: v for k, v in event["payload"].items() if k != field}}
    for side in (a, b):
        record = side.get("authorization")
        if isinstance(record, dict):
            side["authorization"] = {k: v for k, v in record.items() if k != field}
    la, lb = dict(_leaves(a)), dict(_leaves(b))
    out += sorted(
        _path_text(p, vocabulary)
        for p in set(la) | set(lb)
        if p not in la or p not in lb or _typed(la[p]) != _typed(lb[p])
    )
    return out


def _same_typed(x, y) -> bool:
    return json.dumps(x, sort_keys=True) == json.dumps(y, sort_keys=True)


def _ss5_findings(rows: list[dict], vocabulary=None) -> list[Finding]:
    """A-12. The criterion that exists because of the measured guard.py defect."""
    out: list[Finding] = []
    by_name = {r.get("name"): r for r in rows}

    for field in SS5_FIELDS:
        # Since 2026-10-01 a candidate names both SS-5 and the field as tokens.
        # A substring test let an SS-12 row that merely mentions the field
        # stand in for SS-5's fixture.
        candidates = [
            r
            for r in rows
            if {"SS-5", field} <= set(re.split(r"[\s,;]+", str(r.get("criterion", ""))))
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
                out.append(
                    Finding(
                        "AUTH_SS5_FIXTURE_NOT_ONE_FIELD",
                        f"{row.get('_where', row.get('name'))} > authorization",
                        f"the fixture for {field} carries no authorization record, so it "
                        f"cannot differ from a permitted row in {field}. Until 2026-10-01 "
                        "such a row was skipped and still counted as the fixture",
                        f"give the row the permitted row's record with {field} changed; or "
                        "name a different row as SS-5's fixture for the field",
                    )
                )
                continue
            differs = []
            for other in rows:
                if other is row or _decision(other).get("value") != "PERMITTED":
                    continue
                base = other.get("authorization")
                if not isinstance(base, dict):
                    continue
                delta = _ss5_input_delta(row, other, field, vocabulary)
                if base.get(field) == record.get(field):
                    delta = [f"no change to {field}"] + delta
                differs.append((len(delta), delta, other.get("name")))
            if not differs:
                out.append(
                    Finding(
                        "AUTH_SS5_FIXTURE_NOT_ONE_FIELD",
                        f"{row.get('_where', row.get('name'))} > authorization",
                        f"the fixture for {field} has no permitted row with a record to "
                        "differ from, so the one-field difference SS-5 requires cannot be "
                        "shown",
                        "restore a permitted baseline row with an authorization record",
                    )
                )
                continue
            size, delta, base_name = min(differs)
            if delta:
                out.append(
                    Finding(
                        "AUTH_SS5_FIXTURE_NOT_ONE_FIELD",
                        f"{row.get('_where', row.get('name'))} > authorization",
                        f"the fixture for {field} differs from its nearest permitted row "
                        f"({base_name}) in {', '.join(delta)}, beyond {field} itself. SS-5 "
                        "requires a row identical to a passing row except in that one field, "
                        "and every gate input counts: the record, the chain, the dispatch, "
                        "the given inputs and the instant. A fixture that changes two "
                        "inputs cannot show which one the gate read",
                        f"restore every input except {field} to the permitted row's values, "
                        "with the chain's identifiers renamed one to one and any copy of "
                        f"{field} in a chain payload equal to the record's; or, if the "
                        "permitted row moved, move both in one commit so the pair stays a "
                        "one-field difference",
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
                    f"the row expects {_quoted(row.get('expect_code'), _known_tokens(model))} and the rank 3 fixture map "
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

    compiled = [str(c) for c in _seq(model, "policy", "compiles_criteria")]
    defined = set(model.get("ss_defined") or ())
    for cid in sorted(defined - set(compiled), key=lambda c: int(c.split("-")[1])):
        out.append(
            Finding(
                "AUTH_CRITERION_NOT_COMPILED",
                f"policy/subject-authorization.yaml compiles_criteria > {cid}",
                f"doctrine/SUBJECT_SELECTION.md defines {cid} and the policy does not list "
                "it as compiled, so no check here asks whether it is stamped. Until "
                "2026-10-01 nothing compared the list with doctrine, and dropping a "
                "criterion from both the list and the pin passed",
                f"list {cid} in compiles_criteria; or ratify the doctrine change that "
                "removes it",
            )
        )
    for cid in compiled:
        if not CRITERION_RE.fullmatch(cid) or (defined and cid not in defined):
            out.append(
                Finding(
                    "AUTH_CRITERION_NOT_COMPILED",
                    f"policy/subject-authorization.yaml compiles_criteria > {cid}",
                    f"{cid!r} is not a criterion doctrine/SUBJECT_SELECTION.md defines, so "
                    "the stamp check would read a row that cannot exist",
                    "correct the id; or remove it from compiles_criteria",
                )
            )

    for cid in list(dict.fromkeys(compiled + list(ITEM_6_RT_CRITERIA))):
        if not CRITERION_RE.fullmatch(cid):
            continue
        compiled_here = cid in compiled
        if cid not in pin.criteria:
            out.append(
                Finding(
                    "AUTH_CRITERION_NOT_STAMPED",
                    f"doctrine/DOCTRINE_STATUS.md > {cid}",
                    (
                        f"policy/subject-authorization.yaml compiles {cid}"
                        if compiled_here
                        else f"SS-14 item 6 requires {cid} per criterion"
                    )
                    + " and the pin of record's per-criterion table carries no row for it. "
                    "A criterion with no row refuses, so this table is the mechanism rather "
                    "than an index of one, and a criterion nothing stamps is a rule asserted "
                    "on no one's authority",
                    f"add the {cid} row to the Step 3 table with its conclusion recorded"
                    + (
                        "; or remove the criterion from compiles_criteria and record what "
                        "compiles it instead"
                        if compiled_here
                        else ""
                    ),
                )
            )
            continue
        source = NAMESPACE_FILE.get(cid.split("-")[0], "")
        if not pin.artifact_stamped(source):
            out.append(
                Finding(
                    "AUTH_CRITERION_FILE_NOT_STAMPED",
                    f"doctrine/DOCTRINE_STATUS.md > {source}",
                    f"{cid} carries a per-criterion row and {source} is unstamped: "
                    f"{pin.reason_unstamped(source)}. Nothing binds unless it appears with "
                    "a date and a ratifier, and one partially stamped item does not stamp "
                    "its file",
                    f"stamp {source} with {pin_of_record.ROW_FORMAT}, or with the 'all "
                    "criteria' wording its range row uses; or resolve the Pending row that "
                    "names it as a stamp target by stamping it",
                )
            )
        elif not pin.criterion_stamped(cid):
            # Until the second review of 2026-10-01 a criterion with a Step 3 row
            # and no dated range or row naming it, RT-19 once its item row is
            # gone, passed both modes.
            out.append(
                Finding(
                    "AUTH_CRITERION_NOT_STAMPED",
                    f"doctrine/DOCTRINE_STATUS.md > {cid}",
                    f"{cid} has a Step 3 row and no dated range or Ratified row naming it, so "
                    "the reader reads it as unstamped and it binds nothing (PIN-R7)",
                    f"add a dated Ratified row naming {cid}, or a range row covering it; or "
                    "restore the row that covered it",
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
    criteria = list(
        dict.fromkeys([str(c) for c in _seq(policy, "compiles_criteria")] + list(ITEM_6_RT_CRITERIA))
    )

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

    # A-18's second pass. Until 2026-10-01 only rows naming never_item 6 were
    # read, and a well-formed permit row carries no never_item, so a permit, or a
    # decision past step 1, asserted under a stamp state item 6 refuses passed.
    known = _known_tokens(model)
    for row in model.get("rows") or []:
        dec = _decision(row)
        if dec.get("never_item") == 6 or dec.get("value") is None:
            continue
        # A missing, null or empty state reads the live pin, as the first pass
        # does. Until the critic of 2026-10-01 this pass skipped it, which was
        # the case the pass was written to catch.
        state = _d(row, "given", "stamp_state", default={}) or {}
        step = dec.get("decided_at_step")
        past_step_1 = isinstance(step, int) and 2 <= step <= 6
        reasons = item_6_reasons(state, paths, criteria, pin)
        if reasons and (dec.get("value") == "PERMITTED" or past_step_1):
            out.append(
                Finding(
                    "AUTH_UNRATIFIED_CRITERION_PERMITTED",
                    f"{row.get('_where', row.get('name'))} > given.stamp_state",
                    f"the row asserts {_quoted(dec.get('value'), known)} at step {_quoted(step, known)} under a stamp state "
                    f"that is short {len(reasons)} item(s), the first being {reasons[0]}. "
                    "SS-14 item 6 refuses at step 1 under that state, so the gate never "
                    "reaches the decision the row asserts",
                    "complete the row's stamp state, which is a fixture edit rather than a "
                    "permission; or assert the item 6 refusal the state produces",
                )
            )

    # A-19b. The seal condition on item 7, constructed. With every path and
    # criterion read as stamped, an unsealed cast must still refuse, so removing
    # the condition turns this gate red on the real tree for as long as the cast
    # is unsealed.
    class _EverythingStamped:
        def artifact_stamped(self, path: str) -> bool:
            return True

        def criterion_stamped(self, cid: str) -> bool:
            return True

        def reason_unstamped(self, path: str) -> str:
            return ""

    if CAST_PATH in paths and cast_seal_reason():
        if not item_6_reasons({}, paths, criteria, _EverythingStamped()):
            out.append(
                Finding(
                    "AUTH_CAST_SEAL_UNREAD",
                    "tools/validate_authorization.py > item_6_reasons",
                    "with every SS-14 item 6 path stamped, the predicate permits while the "
                    f"real cast reports: {cast_seal_reason()}. SS-14 item 6 binds "
                    "synthetic/CAST.md only with a sealed, hash-pinned GROUND_TRUTH.yaml "
                    "carrying a designed confuser pair",
                    "restore the seal condition in item_6_reasons; it reads "
                    "tools/validate_cast.py's own seal, hash and confuser checks",
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

    # A-19, read through the pin. Until 2026-10-01 every state above carried
    # source "fixture", so item_6_reasons echoed the lists it was handed and the
    # reader's criterion_stamped and artifact_stamped could answer True for
    # everything with both modes green. These pins are copies of the pin of
    # record with the item 6 paths' rows replaced, so the reader decides. A
    # doctrine file keeps its own rows, which stamp its criteria too. The control
    # allows two refusals the reader is right to make on this tree: a path with
    # no file on disk (PIN-R6) and a stamped cast that is unsealed.
    text = model.get("pin_text", "")
    if paths and criteria and _pin(model).parsed:
        own = [p for p in paths if not p.startswith("doctrine/")]
        target = next((p for p in own if p != CAST_PATH and (ROOT / p).is_file()), "")
        via = "tools/validate_authorization.py > item_6_reasons, read through the pin"

        short_criterion = _pin(model, _constructed_pin_text(text, own, own, criteria[0]))
        if f"criterion {criteria[0]} has no row in the stamp table" not in item_6_reasons(
            {}, paths, criteria, short_criterion
        ):
            out.append(
                Finding(
                    "AUTH_UNRATIFIED_CRITERION_PERMITTED",
                    via,
                    f"a copy of the pin of record without the Step 3 row for {criteria[0]} "
                    "was not refused for it, so the reader's criterion_stamped answers "
                    "without reading the table. SS-8 says item 6 is evaluated by reading "
                    "the pin, and a fixture-supplied list cannot show that",
                    "fix Pin.criterion_stamped in tools/pin_of_record.py so a criterion "
                    "with no Step 3 row is unstamped; or, if the Step 3 table's heading "
                    "moved, move CRITERIA_START with it",
                )
            )
        if target:
            short_artifact = _pin(model, _constructed_pin_text(text, [p for p in own if p != target], own))
            if not any(
                r.startswith(f"{target} is unstamped") for r in item_6_reasons({}, paths, criteria, short_artifact)
            ):
                out.append(
                    Finding(
                        "AUTH_UNRATIFIED_ARTIFACT_PERMITTED",
                        via,
                        f"a copy of the pin of record with no row for {target} was not "
                        "refused for it, so the reader's artifact_stamped answers without "
                        "reading the Ratified table",
                        "fix Pin.artifact_stamped in tools/pin_of_record.py so a path with "
                        "no dated row is unstamped",
                    )
                )
        # What the copy does not construct, the doctrine files and the criteria,
        # it inherits from the pin of record; a refusal the pin of record also
        # makes is reported by the checks that read it, not by this control.
        live = set(item_6_reasons({}, paths, criteria, _pin(model)))
        complete_pin = _pin(model, _constructed_pin_text(text, own, own))
        residual = [
            r
            for r in item_6_reasons({}, paths, criteria, complete_pin)
            if not (cast_seal_reason() and r.startswith(f"{CAST_PATH} is stamped and"))
            and not any(r.startswith(f"{p} is unstamped") and not (ROOT / p).is_file() for p in paths)
            and not (r in live and (r.startswith("criterion ") or r.startswith("doctrine/")))
        ]
        if residual:
            out.append(
                Finding(
                    "AUTH_STAMP_PREDICATE_ALWAYS_REFUSES",
                    via,
                    "a copy of the pin of record with every item 6 path stamped was "
                    f"refused for {len(residual)} reason(s), the first being {residual[0]}. "
                    "A reader that refuses a complete pin makes the refusals above prove "
                    "nothing about what it reads",
                    "fix the reader in tools/pin_of_record.py so a dated whole-artifact "
                    "row stamps an existing file; or correct the path list in "
                    "policy/subject-authorization.yaml the control is built from",
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
    found = tuple(
        (i.get("id"), tuple(str(x) for x in _seq(i, "paths"))) for i in items
    )
    for item in items:
        need = pin_of_record.required_sections(str(item.get("granularity", "")))
        pinned = set().union(*(RATIFY_SECTIONS.get(str(x), set()) for x in _seq(item, "paths")))
        if need != pinned:
            out.append(
                Finding(
                    "AUTH_RATIFY_LIST_DRIFT",
                    f"policy/subject-authorization.yaml ratify_before_collection item {item.get('id')}",
                    f"the item's granularity names sections {sorted(need) or 'none'} and SS-14 "
                    f"item 6 stamps it by {sorted(pinned) or 'the whole artifact'}. The "
                    "artifact under ratification may not decide how finely it is stamped",
                    "restore the granularity SS-14 item 6 states; or ratify an SS-14 "
                    "amendment and move RATIFY_SECTIONS in this tool in that commit",
                )
            )
    if len(items) == RATIFY_ITEM_COUNT and len(paths) == RATIFY_PATH_COUNT and found != RATIFY_ITEMS:
        drift = [
            f"item {want[0]} names {list(got[1])} where SS-14 names {list(want[1])}"
            for want, got in zip(RATIFY_ITEMS, found)
            if want != got
        ]
        out.append(
            Finding(
                "AUTH_RATIFY_LIST_DRIFT",
                "policy/subject-authorization.yaml ratify_before_collection",
                "the list keeps SS-14 item 6's counts and changes what it names: "
                + "; ".join(drift)
                + ". Swapping a path for one already stamped clears the refusal it holds "
                "while every count still matches",
                "restore the paths SS-14 item 6 names; or ratify an SS-14 amendment with "
                "a dated stamp and move RATIFY_ITEMS in this tool in that commit",
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
    if len(checks) == PREFLIGHT_CHECK_COUNT and tuple(str(c) for c in checks) != PREFLIGHT_CHECKS:
        out.append(
            Finding(
                "AUTH_PREFLIGHT_LIST_DRIFT",
                "policy/subject-authorization.yaml ratify_before_collection.preflight.checks",
                f"the preflight set names {list(checks)} and SS-14 item 6 names "
                f"{list(PREFLIGHT_CHECKS)}. Swapping a check for a mode that always exits 0 "
                "keeps the count and empties the condition",
                "restore the four checks SS-14 item 6 names; or ratify the change and move "
                "PREFLIGHT_CHECKS in this tool in the same commit",
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
        # An id outside the entry grammar is described rather than printed, since
        # the fourth review of 2026-10-01: a row held on a handle printed it here.
        summary = "; ".join(
            f"{_held_text([entry])} holds {len(names)} row(s)" for entry, names in sorted(held.items())
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
            cast_unmet = str(path) == CAST_PATH and pin.artifact_stamped(CAST_PATH) and cast_seal_reason()
            if not pin.artifact_stamped(str(path)) or cast_unmet:
                out.append(
                    Finding(
                        "AUTH_ARTIFACT_UNSTAMPED",
                        f"doctrine/DOCTRINE_STATUS.md > {path}",
                        "SS-14 item 6 refuses all collection, including collection against a "
                        f"synthetic account, until this path is stamped, and it is not: "
                        f"{pin.reason_unstamped(str(path)) or cast_seal_reason()}. This is a hard refusal, so a "
                        "present, complete, valid, unexpired authorization record does not "
                        "unlock it",
                        f"write {path} if it does not exist, then stamp it with "
                        f"{pin_of_record.ROW_FORMAT}, or by the sections item 6 names; a "
                        "Pending stamp-target row is resolved by stamping it into the Ratified "
                        "table, not by deleting it; or collect nothing, which is what this "
                        "refusal is holding",
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


def _mut_ss5_locator_differs(m: dict) -> None:
    item = _row(m, "one-hop-pivot-depth-max-mutated")["chain"][3]["payload"]
    item["locator"] = item["locator"] + "-zero"


def _mut_ss5_reference_moved(m: dict) -> None:
    row = _row(m, "one-hop-pivot-depth-max-mutated")
    row["dispatch"]["motivated_by"] = row["chain"][2]["event"]["event_id"]


def _mut_ss5_grant_copy_disagrees(m: dict) -> None:
    row = _row(m, "seed-expires-on-mutated")
    base = _row(m, "seed-permitted")
    row["chain"][0]["payload"]["expires_on"] = base["chain"][0]["payload"]["expires_on"]


def _mut_ss5_baseline_ids_collapsed(m: dict) -> None:
    row = _row(m, "one-hop-permitted")
    keep, drop = row["chain"][0]["event"]["event_id"], row["chain"][1]["event"]["event_id"]
    collapsed = json.loads(json.dumps(row).replace(drop, keep))
    row.clear()
    row.update(collapsed)


def _mut_reader_stamps_every_criterion(m: dict) -> None:
    m["pin_overrides"] = {"criterion_stamped": lambda cid: True}


def _mut_reader_stamps_every_artifact(m: dict) -> None:
    m["pin_overrides"] = {"artifact_stamped": lambda path: True, "reason_unstamped": lambda path: ""}


def _mut_reader_stamps_nothing(m: dict) -> None:
    m["pin_overrides"] = {
        "artifact_stamped": lambda path: False,
        "reason_unstamped": lambda path: "a reader that stamps nothing",
    }


def _mut_register_decision_drifts(m: dict) -> None:
    m["register_rows"]["seed-permitted"][0][1] = "REFUSED"


def _mut_register_holds_a_determinate_row(m: dict) -> None:
    m["register_rows"]["runner-started-on-local"][0][5] = "GF-U1"


def _mut_register_held_without_a_hold(m: dict) -> None:
    m["register_rows"]["runner-started-on-local"][0][1] = "held"


def _mut_register_criterion_drifts(m: dict) -> None:
    m["register_rows"]["seed-expires-on-mutated"][0][0] = "SS-5, `selectors`"


def _mut_ss5_reference_copied(m: dict) -> None:
    row = _row(m, "one-hop-pivot-depth-max-mutated")
    row["dispatch"]["motivated_by"] = _row(m, "one-hop-permitted")["dispatch"]["motivated_by"]


def _mut_ss5_grant_copy_deleted(m: dict) -> None:
    del _row(m, "seed-expires-on-mutated")["chain"][0]["payload"]["expires_on"]


def _mut_ss5_copy_added_elsewhere(m: dict) -> None:
    row = _row(m, "one-hop-pivot-depth-max-mutated")
    row["chain"][1]["payload"]["pivot_depth_max"] = row["authorization"]["pivot_depth_max"]


def _mut_ss5_true_written_as_one(m: dict) -> None:
    _row(m, "seed-expires-on-mutated")["given"]["manifest"]["declares_bystanders"] = 1


def _mut_ss5_empty_key_added(m: dict) -> None:
    _row(m, "seed-expires-on-mutated")["dispatch"]["scope_override"] = []


def _mut_rt19_row_removed(m: dict) -> None:
    m["pin_text"] = re.sub(r"(?m)^\| Gate telemetry with a 90 day TTL[^\n]*\n", "", m["pin_text"], count=1)


def _mut_reader_stamps_no_criterion(m: dict) -> None:
    m["pin_overrides"] = {"criterion_stamped": lambda cid: False}


def _mut_selector_gains_a_field(m: dict) -> None:
    m["schema"]["$defs"]["selector"]["properties"]["note"] = {"type": "string"}


def _mut_address_in_brackets(m: dict) -> None:
    row = _row(m, "runner-started-on-local")
    row["description"] = row["description"] + " Contact <" + "examplename" + "@" + "example" + ".org>."


def _mut_phone_grouped(m: dict) -> None:
    row = _row(m, "runner-started-on-local")
    row["description"] = row["description"] + " Call " + "+1 555" + " 0100 999."


def _mut_address_as_a_key(m: dict) -> None:
    row = _row(m, "runner-started-on-local")
    row["given"] = dict(row["given"])
    row["given"]["examplename" + "@" + "example" + ".org"] = "seen"


def _register_with(m: dict, edit) -> None:
    """Edit the register's text and parse it again, so a break goes through the
    parser it tests rather than around it."""
    lines = m["register_block"].splitlines()
    i = next(n for n, line in enumerate(lines) if line.startswith("| `seed-permitted`"))
    lines.insert(i + 1, edit(lines[i]))
    block = "\n".join(lines)
    m["register_block"] = block
    m["register_rows"] = _register_rows(block)
    m["register"] = list(_register_rows(block))
    m["register_unreadable"] = _register_unreadable(block)


def _mut_register_row_repeated(m: dict) -> None:
    _register_with(m, lambda line: line)


def _mut_register_row_contradicted(m: dict) -> None:
    def contradict(line):
        cells = line.split("|")
        cells[3] = " REFUSED "
        return "|".join(cells)

    _register_with(m, contradict)


def _mut_register_row_indented(m: dict) -> None:
    _register_with(m, lambda line: " " + line)


def _mut_register_row_without_outer_pipes(m: dict) -> None:
    def contradict(line):
        cells = line.split("|")
        cells[3] = " REFUSED "
        return "|".join(cells).strip().strip("|").strip()

    _register_with(m, contradict)


def _mut_register_row_without_backticks(m: dict) -> None:
    def contradict(line):
        cells = line.split("|")
        cells[1] = cells[1].replace("`", "")
        cells[3] = " REFUSED "
        return "|".join(cells)

    _register_with(m, contradict)


def _contradicted(line: str) -> str:
    cells = line.split("|")
    cells[3] = " REFUSED "
    return "|".join(cells)


def _mut_register_row_as_a_second_header(m: dict) -> None:
    _register_with(m, lambda line: "\n" + _contradicted(line) + "\n|---|---|---|---|---|---|---|")


def _mut_register_row_after_a_blank_line(m: dict) -> None:
    _register_with(m, lambda line: "\n" + _contradicted(line))


def _mut_absent_criterion_unshaped(m: dict) -> None:
    row = _row(m, "seed-permitted")
    paths = [
        str(p)
        for item in _seq(m["policy"], "ratify_before_collection", "items")
        if isinstance(item, dict)
        for p in _seq(item, "paths")
    ]
    row["given"] = dict(
        row["given"],
        stamp_state={"source": "fixture", "artifacts_stamped": paths, "criteria_absent": [UNSHAPED_MARK]},
    )


def _mut_ss5_key_unshaped(m: dict) -> None:
    _row(m, "seed-selectors-mutated")["authorization"][UNSHAPED_MARK] = "x"


def _mut_phone_with_a_fullwidth_plus(m: dict) -> None:
    row = _row(m, "runner-started-on-local")
    row["description"] = row["description"] + " Call " + chr(0xFF0B) + "1 555" + " 0100 999."


def _mut_permits_unshaped_under_a_short_state(m: dict) -> None:
    # A-18's second pass quotes a permit's value and step; until the seventh
    # review of 2026-10-02 no break reached either.
    paths = [
        str(p)
        for item in _seq(m["policy"], "ratify_before_collection", "items")
        if isinstance(item, dict)
        for p in _seq(item, "paths")
    ]
    short = {"source": "fixture", "artifacts_stamped": paths, "criteria_absent": ["SS-5"]}
    seed = _row(m, "seed-permitted")
    seed["given"] = dict(seed["given"], stamp_state=short)
    seed["expect_decision"] = dict(seed["expect_decision"], decided_at_step=UNSHAPED_MARK)
    hop = _row(m, "one-hop-permitted")
    hop["given"] = dict(hop["given"], stamp_state=short)
    hop["expect_decision"] = dict(hop["expect_decision"], value=UNSHAPED_MARK, decided_at_step=3)


def _mut_phone_with_zero_width_spaces(m: dict) -> None:
    row = _row(m, "runner-started-on-local")
    row["description"] = row["description"] + " Call " + chr(0x200B).join(["+1", "555", "0100", "999"]) + "."


def _mut_register_row_unnamed(m: dict) -> None:
    _register_with(m, lambda line: "| Seed permitted, again " + line[line.index("|", 1):])


def _mut_pending_unshaped(m: dict) -> None:
    _row(m, "seed-permitted")["pending"] = [UNSHAPED_MARK]


def _mut_register_row_unshaped(m: dict) -> None:
    m["register_rows"]["seed-permitted"][0] = [UNSHAPED_MARK] * 6


def _mut_fixture_values_unshaped(m: dict) -> None:
    row = _row(m, "run-against-unauthorized-subject")
    row["expect_decision"] = dict(
        row["expect_decision"],
        value=UNSHAPED_MARK,
        decided_at_step=UNSHAPED_MARK,
        basis_field="refusal_basis",
        basis=[UNSHAPED_MARK],
        subject_relation=UNSHAPED_MARK,
    )
    row["expect_code"] = UNSHAPED_MARK
    _first_record(m)["subject_class"] = UNSHAPED_MARK


def _mut_basis_field_unshaped(m: dict) -> None:
    row = _row(m, "seed-selectors-mutated")
    row["expect_decision"] = dict(row["expect_decision"], basis_field=UNSHAPED_MARK)


def _mut_keys_unshaped(m: dict) -> None:
    row = _row(m, "incidental-estimate-absent")
    row[UNSHAPED_MARK] = "x"
    row["given"] = dict(row["given"], **{UNSHAPED_MARK: "x"})
    row["expect_decision"] = dict(row["expect_decision"], **{UNSHAPED_MARK: "x"})
    row["authorization"][UNSHAPED_MARK] = {"handle": "x"}


def _mut_registry_reads_empty(m: dict) -> None:
    m["selector_types"] = []


def _mut_phone_with_minus_signs(m: dict) -> None:
    row = _row(m, "runner-started-on-local")
    row["description"] = row["description"] + " Call " + chr(0x2212).join(["+1", "555", "0100", "999"]) + "."


def _mut_placeholder_label_not_a_cast_token(m: dict) -> None:
    _row(m, "incidental-estimate-absent")["authorization"]["selectors"][0]["value"] = "<handle:instagram:not-a-cast-token>"


def _mut_address_as_a_record_field(m: dict) -> None:
    _row(m, "incidental-estimate-absent")["authorization"]["examplename" + "@" + "example" + ".org"] = "<x:y>"


def _mut_address_as_a_pending_id(m: dict) -> None:
    _row(m, "runner-started-on-local")["pending"] = ["examplename" + "@" + "example" + ".org"]


def _mut_selectors_with_their_own_defs(m: dict) -> None:
    # A local $id and $defs make items' $ref resolve to an empty schema. Only
    # SCHEMA_NODE_PINS sees it; the fourth review found no break guarded it.
    selectors = m["schema"]["properties"]["selectors"]
    selectors["$id"] = "urn:example:selectors"
    selectors["$defs"] = {"selector": {}}


def _mut_record_selectors_as_a_string(m: dict) -> None:
    _row(m, "incidental-estimate-absent")["authorization"]["selectors"] = "jdoe" + "1987"


def _mut_record_as_a_list(m: dict) -> None:
    _row(m, "incidental-estimate-absent")["authorization"] = ["jdoe" + "1987"]


def _mut_selector_type_as_a_handle(m: dict) -> None:
    _row(m, "incidental-estimate-absent")["authorization"]["selectors"][0]["selector_type"] = "jdoe" + "1987"


def _mut_phone_with_no_break_spaces(m: dict) -> None:
    row = _row(m, "runner-started-on-local")
    row["description"] = row["description"] + " Call +44" + chr(0xA0) + "20" + chr(0xA0) + "7946" + chr(0xA0) + "0958."


def _mut_selectors_prefixed(m: dict) -> None:
    m["schema"]["properties"]["selectors"]["prefixItems"] = [True]


def _mut_baseline_chain_as_a_mapping(m: dict) -> None:
    _row(m, "one-hop-permitted")["chain"] = {"events": []}


def _mut_selector_properties_as_a_number(m: dict) -> None:
    m["schema"]["$defs"]["selector"]["properties"] = 2


def _mut_record_selector_as_a_string(m: dict) -> None:
    _row(m, "incidental-estimate-absent")["authorization"]["selectors"][0] = "<handle:untyped>"


def _mut_handle_in_brackets(m: dict) -> None:
    _row(m, "incidental-estimate-absent")["authorization"]["selectors"][0]["value"] = "<" + "jdoe" + "1987" + ">"


def _mut_phone_with_parentheses(m: dict) -> None:
    row = _row(m, "runner-started-on-local")
    row["description"] = row["description"] + " Call " + "+44 (20)" + " 7946 0958."


def _mut_address_percent_encoded(m: dict) -> None:
    row = _row(m, "runner-started-on-local")
    row["description"] = row["description"] + " GET /lookup?e=" + "examplename" + "%40" + "example" + ".org"


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


def _mut_rt_row_removed(m: dict) -> None:
    m["pin_text"] = re.sub(r"^\| RT-6 .*$", "", m["pin_text"], flags=re.M)


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


def _mut_permit_row_with_no_state(m: dict) -> None:
    _row(m, "seed-permitted")["given"]["stamp_state"] = None


def _mut_preflight_check_swapped(m: dict) -> None:
    checks = m["policy"]["ratify_before_collection"]["preflight"]["checks"]
    checks[1] = "tools/validate_authorization.py --self-test"


def _mut_contract_granularity_coarsened(m: dict) -> None:
    for item in m["policy"]["ratify_before_collection"]["items"]:
        if item.get("id") == 6:
            item["granularity"] = "section 5"


def _mut_given_drops_environment(m: dict) -> None:
    del _row(m, "runner-started-on-local")["given"]["environment"]


def _mut_decision_gains_a_key(m: dict) -> None:
    _row(m, "seed-permitted")["expect_decision"]["confidence"] = "high"


def _mut_payload_string_claimed(m: dict) -> None:
    _row(m, "injected-instruction-in-collected-bio")["given"]["collected_content"]["string_in_this_file"] = True


def _mut_ss5_criterion_without_ss5(m: dict) -> None:
    _row(m, "seed-expires-on-mutated")["criterion"] = "SS-12, expires_on"


def _mut_ss5_fixture_without_record(m: dict) -> None:
    _row(m, "seed-expires-on-mutated")["authorization"] = None


def _mut_schema_drops_required(m: dict) -> None:
    m["schema"]["required"] = [x for x in m["schema"]["required"] if x != "expires_on"]


def _mut_email_in_prose(m: dict) -> None:
    # Assembled at run time, so this tracked file carries no address.
    row = _row(m, "runner-started-on-local")
    row["description"] = row["description"] + " Contact " + "examplename" + "@" + "example" + ".org."


def _mut_phone_in_prose(m: dict) -> None:
    row = _row(m, "runner-started-on-local")
    row["description"] = row["description"] + " Call " + "+1" + "5550100" + "999."


def _mut_schema_bound(path: tuple):
    def mutate(m: dict) -> None:
        node = m["schema"]
        for part in path[:-1]:
            node = node[part]
        if path[-1] not in node:
            # A pin on an absent key: the break adds it, empty.
            node[path[-1]] = {}
            return
        value = node[path[-1]]
        if isinstance(value, dict):
            node[path[-1]] = {k: v for k, v in value.items() if k == "$comment"}
        elif isinstance(value, list) and not value:
            node[path[-1]] = ["handle"]
        else:
            node.pop(path[-1])

    return mutate


def _mut_schema_opens(m: dict) -> None:
    m["schema"]["additionalProperties"] = True


def _mut_ratify_path_swapped(m: dict) -> None:
    for item in m["policy"]["ratify_before_collection"]["items"]:
        if item.get("id") == 8:
            item["paths"] = ["spec/layer-model.yaml"]


def _mut_criterion_dropped_from_compiled(m: dict) -> None:
    m["policy"]["compiles_criteria"] = [c for c in m["policy"]["compiles_criteria"] if c != "SS-14"]


def _mut_refused_rendered_as_permit(m: dict) -> None:
    permit = next(
        x.get("consequence")
        for x in m["policy"]["gate"]["values"]["members"]
        if x.get("value") == "PERMITTED"
    )
    _row(m, "never-item-6-artifacts-unstamped")["expect_decision"]["render"] = permit


def _mut_permit_row_under_short_state(m: dict) -> None:
    _row(m, "seed-permitted")["given"]["stamp_state"]["criteria_absent"] = ["SS-5"]


def _mutations() -> list[tuple[str, object, str, bool, str]]:
    """(description, mutator(model) -> None, expected code, expect_only, why).

    `expect_only` False means the mutation's damage genuinely reaches more than
    one check, and the fifth field says how. Every False here is a sentence a
    reader can check against the artifacts, which is the point of the flag.
    """
    return [
        ("drop a key from a corpus row", _mut_drop_row_key, "AUTH_ROW_KEYS_UNEXPECTED", False, "the break edits a fixture the register describes and not the register, so the register row now contradicts it and A-13's columns fire too"),
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
            False,
            "the break edits a fixture the register describes and not the register, so the register row now contradicts it and A-13's columns fire too",
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
            False,
            "the break edits a fixture the register describes and not the register, so the register row now contradicts it and A-13's columns fire too",
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
            False,
            "the break edits a fixture the register describes and not the register, so the register row now contradicts it and A-13's columns fire too",
        ),
        (
            "unhold a refusal with no step and no sentence",
            _mut_unheld_thin_refusal,
            "AUTH_ASSERTION_INCOMPLETE_AND_UNHELD",
            False,
            "the break edits a fixture the register describes and not the register, so the register row now contradicts it and A-13's columns fire too",
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
            False,
            "the break edits a fixture the register describes and not the register, so the register row now contradicts it and A-13's columns fire too",
        ),
        (
            "drop expires_on from an authorization record",
            _mut_record_field_missing,
            "AUTH_RECORD_FIELD_MISSING",
            False,
            "it changes seed-permitted, SS-5's differential baseline, so the SS-5 fixtures derived from it no longer differ from it in one gate input and A-12 fires too",
        ),
        (
            "authorize an incidental subject",
            _mut_record_class_s5,
            "AUTH_SUBJECT_CLASS_UNAUTHORIZABLE",
            False,
            "it changes seed-permitted, SS-5's differential baseline, so the SS-5 fixtures derived from it no longer differ from it in one gate input and A-12 fires too",
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
            "change an item's locator in an SS-5 fixture's chain",
            _mut_ss5_locator_differs,
            "AUTH_SS5_FIXTURE_NOT_ONE_FIELD",
            True,
            "",
        ),
        (
            "point an SS-5 fixture's dispatch at a different event",
            _mut_ss5_reference_moved,
            "AUTH_SS5_FIXTURE_NOT_ONE_FIELD",
            True,
            "",
        ),
        ("copy the baseline's reference into an SS-5 fixture", _mut_ss5_reference_copied, "AUTH_SS5_FIXTURE_NOT_ONE_FIELD", True, ""),
        ("delete the GRANT's copy of expires_on", _mut_ss5_grant_copy_deleted, "AUTH_SS5_FIXTURE_NOT_ONE_FIELD", True, ""),
        ("add a copy of pivot_depth_max to another event", _mut_ss5_copy_added_elsewhere, "AUTH_SS5_FIXTURE_NOT_ONE_FIELD", True, ""),
        ("write an SS-5 fixture's true as 1", _mut_ss5_true_written_as_one, "AUTH_SS5_FIXTURE_NOT_ONE_FIELD", True, ""),
        ("add an empty key to an SS-5 fixture's dispatch", _mut_ss5_empty_key_added, "AUTH_SS5_FIXTURE_NOT_ONE_FIELD", True, ""),
        ("remove the row that alone stamps RT-19", _mut_rt19_row_removed, "AUTH_CRITERION_NOT_STAMPED", True, ""),
        ("let the pin reader stamp no criterion", _mut_reader_stamps_no_criterion, "AUTH_CRITERION_NOT_STAMPED", True, ""),
        ("give a selector a third field", _mut_selector_gains_a_field, "AUTH_SCHEMA_BOUND_DRIFT", True, ""),
        ("write an address in angle brackets", _mut_address_in_brackets, "AUTH_VALUE_NOT_PLACEHOLDER", True, ""),
        ("write a phone grouped with spaces", _mut_phone_grouped, "AUTH_VALUE_NOT_PLACEHOLDER", True, ""),
        ("use an address as a mapping key", _mut_address_as_a_key, "AUTH_VALUE_NOT_PLACEHOLDER", False, "a key directly under given is also outside the row contract, so A-01 fires too, and it now masks the key rather than quoting it"),
        ("list a register row twice", _mut_register_row_repeated, "AUTH_REGISTER_NAME_DUPLICATE", True, ""),
        ("list a register row again, indented one space", _mut_register_row_indented, "AUTH_REGISTER_NAME_DUPLICATE", True, ""),
        ("open selectors[0] with prefixItems", _mut_selectors_prefixed, "AUTH_SCHEMA_BOUND_DRIFT", True, ""),
        ("give selectors their own $id and $defs", _mut_selectors_with_their_own_defs, "AUTH_SCHEMA_BOUND_DRIFT", True, ""),
        ("write a record's selectors as a string", _mut_record_selectors_as_a_string, "AUTH_VALUE_NOT_PLACEHOLDER", True, ""),
        ("write a record as a list", _mut_record_as_a_list, "AUTH_VALUE_NOT_PLACEHOLDER", True, ""),
        ("name a handle as a selector's type", _mut_selector_type_as_a_handle, "AUTH_VALUE_NOT_PLACEHOLDER", True, ""),
        ("write a phone with no-break spaces", _mut_phone_with_no_break_spaces, "AUTH_VALUE_NOT_PLACEHOLDER", True, ""),
        ("give a record a field named as an address", _mut_address_as_a_record_field, "AUTH_RECORD_FIELD_UNDECLARED", False, "the key also carries an email shape, so A-08 refuses it too; the self-test also fails if any refusal prints it"),
        ("hold a row on an id written as an address", _mut_address_as_a_pending_id, "AUTH_PENDING_ENTRY_UNKNOWN", False, "the register row and A-08 also refuse the id; the self-test also fails if any refusal prints it"),
        ("write the baseline's chain as a mapping", _mut_baseline_chain_as_a_mapping, "AUTH_SS5_FIXTURE_NOT_ONE_FIELD", True, ""),
        ("write a selector's properties as a number", _mut_selector_properties_as_a_number, "AUTH_SCHEMA_BOUND_DRIFT", True, ""),
        ("write a record selector as a bare string", _mut_record_selector_as_a_string, "AUTH_VALUE_NOT_PLACEHOLDER", True, ""),
        ("write a handle in brackets as a selector value", _mut_handle_in_brackets, "AUTH_VALUE_NOT_PLACEHOLDER", True, ""),
        ("write a phone with its area code in parentheses", _mut_phone_with_parentheses, "AUTH_VALUE_NOT_PLACEHOLDER", True, ""),
        ("write an address percent-encoded", _mut_address_percent_encoded, "AUTH_VALUE_NOT_PLACEHOLDER", True, ""),
        ("label a typed placeholder with no cast token", _mut_placeholder_label_not_a_cast_token, "AUTH_VALUE_NOT_PLACEHOLDER", True, ""),
        (
            "use a word in no vocabulary as a key at every level of a row",
            _mut_keys_unshaped,
            "AUTH_ROW_KEYS_UNEXPECTED",
            False,
            "the given, expect_decision and record keys are refused by their own checks, A-08 refuses the record field's selector key, and the self-test fails if any refusal prints the word",
        ),
        ("read the selector registry as empty", _mut_registry_reads_empty, "AUTH_VALUE_NOT_PLACEHOLDER", True, ""),
        ("write a phone with minus signs between its groups", _mut_phone_with_minus_signs, "AUTH_VALUE_NOT_PLACEHOLDER", True, ""),
        (
            "add a contradicting register row without its outer pipes",
            _mut_register_row_without_outer_pipes,
            "AUTH_REGISTER_ROW_DRIFT",
            False,
            "a second row for a name is also a duplicate, so the duplicate check fires too",
        ),
        (
            "add a contradicting register row without backticks",
            _mut_register_row_without_backticks,
            "AUTH_REGISTER_ROW_DRIFT",
            False,
            "a second row for a name is also a duplicate, so the duplicate check fires too",
        ),
        ("add a register row with no fixture name", _mut_register_row_unnamed, "AUTH_REGISTER_ROW_UNNAMED", True, ""),
        (
            "add a contradicting register row as a second table's header",
            _mut_register_row_as_a_second_header,
            "AUTH_REGISTER_ROW_DRIFT",
            False,
            "a second row for a name is also a duplicate, so the duplicate check fires too",
        ),
        (
            "add a contradicting register row alone after a blank line",
            _mut_register_row_after_a_blank_line,
            "AUTH_REGISTER_ROW_DRIFT",
            False,
            "a second row for a name is also a duplicate, so the duplicate check fires too",
        ),
        (
            "permit under a stamp state missing a word in no vocabulary",
            _mut_absent_criterion_unshaped,
            "AUTH_UNRATIFIED_CRITERION_PERMITTED",
            False,
            "the stamp state is also a gate input that differs from the baseline's, and the self-test fails if any refusal prints the word",
        ),
        (
            "give an SS-5 fixture's record a field named by a word in no vocabulary",
            _mut_ss5_key_unshaped,
            "AUTH_SS5_FIXTURE_NOT_ONE_FIELD",
            False,
            "the field is also undeclared and A-01 refuses the key, and the self-test fails if any refusal prints the word",
        ),
        ("write a phone with zero-width spaces between its groups", _mut_phone_with_zero_width_spaces, "AUTH_VALUE_NOT_PLACEHOLDER", True, ""),
        ("write a phone with a fullwidth plus", _mut_phone_with_a_fullwidth_plus, "AUTH_VALUE_NOT_PLACEHOLDER", True, ""),
        (
            "permit with words in no vocabulary as value and step under a short stamp state",
            _mut_permits_unshaped_under_a_short_state,
            "AUTH_UNRATIFIED_CRITERION_PERMITTED",
            False,
            "the value and step are refused by their own checks, the stamp states differ from the SS-5 baseline's, the register rows differ, and the self-test fails if any refusal prints the word",
        ),
        (
            "hold a row on a word that is not an entry id",
            _mut_pending_unshaped,
            "AUTH_PENDING_ENTRY_UNKNOWN",
            False,
            "the register row's held column then differs too; the self-test also fails if any refusal prints the word",
        ),
        (
            "write a word in no vocabulary into every cell of a register row",
            _mut_register_row_unshaped,
            "AUTH_REGISTER_ROW_DRIFT",
            True,
            "",
        ),
        (
            "assert words in no vocabulary as a row's decision, step, basis, relation, code and class",
            _mut_fixture_values_unshaped,
            "AUTH_CODE_OUTSIDE_VOCABULARY",
            False,
            "each field is refused by its own check, the reserved-name map and the register row also differ, and the self-test fails if any refusal prints the word",
        ),
        ("record a basis under a word that is no basis field", _mut_basis_field_unshaped, "AUTH_BASIS_FIELD_UNKNOWN", True, ""),
        ("list a register row a second time, contradicting the first", _mut_register_row_contradicted, "AUTH_REGISTER_ROW_DRIFT", False, "a second row for a name is also a duplicate, so the duplicate check fires too"),
        (
            "state another decision in a register row",
            _mut_register_decision_drifts,
            "AUTH_REGISTER_ROW_DRIFT",
            True,
            "",
        ),
        (
            "hold a determinate row in the register",
            _mut_register_holds_a_determinate_row,
            "AUTH_REGISTER_ROW_DRIFT",
            True,
            "",
        ),
        (
            "write held for a value on a row nothing holds",
            _mut_register_held_without_a_hold,
            "AUTH_REGISTER_ROW_DRIFT",
            True,
            "",
        ),
        (
            "name another field in a register row's criterion",
            _mut_register_criterion_drifts,
            "AUTH_REGISTER_ROW_DRIFT",
            True,
            "",
        ),
        (
            "let the pin reader stamp every criterion",
            _mut_reader_stamps_every_criterion,
            "AUTH_UNRATIFIED_CRITERION_PERMITTED",
            True,
            "",
        ),
        (
            "let the pin reader stamp every artifact",
            _mut_reader_stamps_every_artifact,
            "AUTH_UNRATIFIED_ARTIFACT_PERMITTED",
            True,
            "",
        ),
        (
            "let the pin reader stamp nothing",
            _mut_reader_stamps_nothing,
            "AUTH_STAMP_PREDICATE_ALWAYS_REFUSES",
            False,
            "a reader that stamps nothing also leaves the doctrine files unstamped, so "
            "the criterion-file check fires too",
        ),
        (
            "collapse two of SS-5's baseline identifiers into one",
            _mut_ss5_baseline_ids_collapsed,
            "AUTH_SS5_FIXTURE_NOT_ONE_FIELD",
            True,
            "",
        ),
        (
            "leave the GRANT's copy of expires_on at the baseline value",
            _mut_ss5_grant_copy_disagrees,
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
            False,
            "the break edits a fixture the register describes and not the register, so the register row now contradicts it and A-13's columns fire too",
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
            "remove an RT criterion's row from the pin of record",
            _mut_rt_row_removed,
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
            False,
            "it changes seed-permitted, SS-5's differential baseline, so the SS-5 fixtures derived from it no longer differ from it in one gate input and A-12 fires too",
        ),
        (
            "add a tenth field to an authorization record",
            _mut_record_field_undeclared,
            "AUTH_RECORD_FIELD_UNDECLARED",
            False,
            "it changes seed-permitted, SS-5's differential baseline, so the SS-5 fixtures derived from it no longer differ from it in one gate input and A-12 fires too",
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
            False,
            "a refusing baseline leaves the SS-5 fixtures with no one-field permitted partner, so A-12 fires too",
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
            False,
            "the break edits a fixture the register describes and not the register, so the register row now contradicts it and A-13's columns fire too",
        ),
        ("drop expires_on from the schema's required list", _mut_schema_drops_required, "AUTH_SCHEMA_RECORD_SHAPE_DRIFT", True, ""),
        ("open the schema's record to undeclared fields", _mut_schema_opens, "AUTH_SCHEMA_RECORD_SHAPE_DRIFT", True, ""),
        ("write an email address into a fixture's prose", _mut_email_in_prose, "AUTH_VALUE_NOT_PLACEHOLDER", True, ""),
        ("write a phone number into a fixture's prose", _mut_phone_in_prose, "AUTH_VALUE_NOT_PLACEHOLDER", True, ""),
    ] + [
        (f"widen the schema at {'.'.join(path)}", _mut_schema_bound(path), "AUTH_SCHEMA_BOUND_DRIFT", True, "")
        for path, _, _ in SCHEMA_PINS
    ] + [
        (
            "swap item 8's path for another tracked path",
            _mut_ratify_path_swapped,
            "AUTH_RATIFY_LIST_DRIFT",
            False,
            "the swapped-in path is absent from every row's fixture stamp state, so "
            "A-18's second pass also reports each decided row as short",
        ),
        ("drop SS-14 from the compiled criteria", _mut_criterion_dropped_from_compiled, "AUTH_CRITERION_NOT_COMPILED", True, ""),
        ("render a permit on the item 6 refusal row", _mut_refused_rendered_as_permit, "AUTH_RENDER_NOT_THE_COMPILED_SENTENCE", True, ""),
        ("assert a permit on a well-formed permit row under a short stamp state", _mut_permit_row_under_short_state, "AUTH_UNRATIFIED_CRITERION_PERMITTED", False, "it changes seed-permitted, SS-5's differential baseline, so the SS-5 fixtures derived from it no longer differ from it in one gate input and A-12 fires too"),
        ("delete the environment input from the row that tests it", _mut_given_drops_environment, "AUTH_GIVEN_KEYS_UNEXPECTED", True, ""),
        ("add an ungraded key to a decision", _mut_decision_gains_a_key, "AUTH_DECISION_KEYS_UNEXPECTED", True, ""),
        ("claim a collected string sits in the corpus", _mut_payload_string_claimed, "AUTH_PAYLOAD_STRING_CLAIMED", True, ""),
        ("let an SS-12 row stand in for SS-5's expires_on fixture", _mut_ss5_criterion_without_ss5, "AUTH_SS5_FIXTURE_MISSING", False, "the break edits a fixture the register describes and not the register, so the register row now contradicts it and A-13's columns fire too"),
        ("take the record off SS-5's expires_on fixture", _mut_ss5_fixture_without_record, "AUTH_SS5_FIXTURE_NOT_ONE_FIELD", True, ""),
        ("assert a permit with no stamp state at all", _mut_permit_row_with_no_state, "AUTH_UNRATIFIED_CRITERION_PERMITTED", False, "it changes seed-permitted, SS-5's differential baseline, so the SS-5 fixtures derived from it no longer differ from it in one gate input and A-12 fires too"),
        ("swap a preflight check for a mode that always passes", _mut_preflight_check_swapped, "AUTH_PREFLIGHT_LIST_DRIFT", True, ""),
        ("let the policy stamp the contract by section 5 alone", _mut_contract_granularity_coarsened, "AUTH_RATIFY_LIST_DRIFT", True, ""),
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
        found = check_corpus(m)
        fired = {f.code for f in found if (f.code, f.where) not in baseline_pairs}
        # A refusal must never print the value it guards. Removing the mask in
        # Finding turns this red, which the third review found nothing did. The
        # certification refusal is read too, and so is the unshaped mark, since
        # the fourth review found a handle printed where no shape could be masked.
        try:
            certification = check_certification(m)
        except Exception:
            certification = []
        rendered = [f.render() for f in found] + [f.render() for f in certification]
        printed = any(p.search(r) for r in rendered for _, p in VALUE_SHAPES)
        quoted = any(UNSHAPED_MARK in r for r in rendered)
        exercised |= fired
        if printed:
            ok, note = False, ", and a refusal printed an email or phone shape"
        elif quoted:
            ok, note = False, ", and a refusal printed a word no vocabulary holds"
        elif expected not in fired:
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

    # --dispatch-paths, on planted sources and fixture allowlists. Nothing here
    # reads the tree or runs the planted code; each source is parsed only.
    dispatch_cases, dispatch_failures = dispatch_self_test(quiet)
    failures += dispatch_failures

    if failures:
        print(
            "REFUSED AUTH_SELF_TEST_FAILED\n"
            "  where: tools/validate_authorization.py > _mutations and _dispatch_cases\n"
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
            f"codes exercised. --dispatch-paths: {dispatch_cases} planted cases, each refused "
            f"by its own code or read clean as claimed, {len(CASCADES)} of the refusals "
            "cascading with a stated reason."
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
        "  tools/validate_conformance.py stays PENDING while this notice prints.\n"
        "  Exit 0 here is not clean: VA-U2 records how a deferred mode should exit."
    )
    return 0


# ---------------------------------------------------------------------------
# --dispatch-paths. SS-6, Step 10.
#
# WHAT IS A DISPATCH SITE. Every Python file under runner/, connectors/ and app/
# that git tracks, plus every untracked one `git ls-files --others
# --exclude-standard` lists there, is parsed, and its imports are resolved to
# dotted names (`import subprocess as sp`, `from os import system`, and relative
# imports inside a package). A site is:
#
#   - a call whose resolved name matches a pattern in DISPATCH_PATTERNS by
#     fnmatch: a process (subprocess, os.system, os.popen, os.exec*, os.spawn*,
#     os.posix_spawn*, pty.spawn, asyncio.create_subprocess_*), a network
#     connection or listener (socket, urllib.request, requests, http.client,
#     httpx, aiohttp, asyncio.open_connection and start_server, http.server and
#     socketserver servers), a subscription (websocket, websockets, telethon),
#     or a container (the docker SDK);
#   - a reference to one of the patterns that carries no wildcard, outside call
#     position, because binding `run = subprocess.run` moves the call out of
#     sight. Such a reference is outside the gate wherever it sits, inside a
#     permits region included, because the stored callable, or a
#     functools.partial built on it, can be called later from anywhere. In a
#     test module only, meaning a test_*.py file or conftest.py under a tests/
#     directory, three references are not sites, because none stores the
#     pattern or calls it in place (reading VA-R6, applied as the session's
#     reading and awaiting the operator's class, B as a precision rule or F as
#     an exemption): the object a patch replaces an attribute on, which is the first
#     argument, or the target keyword, of a call to the builtin setattr or
#     delattr, of a method so named on a receiver named monkeypatch or mp such
#     as a test's monkeypatch.setattr, or of unittest.mock.patch.object or
#     mock.patch.object resolved through the imports; the object of an
#     attribute assigned or deleted, as in `socket.socket.connect = guard`; and
#     the object of a read of an attribute whose name is not a dunder and which
#     is not called where it is read, where the same function or module body
#     also patches or assigns that attribute of that object by its literal
#     name, which is the patch keeping the original it replaces. Outside a test
#     module each of the three is a site, so a production module that swaps a
#     dispatch attribute and keeps its original is refused. A reference passed
#     as any other argument, functools.partial's included, is still a site;
#   - a class statement whose base matches a pattern, such as a server class
#     that inherits http.server.ThreadingHTTPServer, because instantiating the
#     subclass later is a call the scan cannot resolve;
#   - argv construction: shlex.split, shlex.join or shlex.quote, a call to a
#     function named in ARGV_BUILDERS, or .format or .format_map on a name or
#     attribute ending in command_template;
#   - a credential draw: a call to a function named in CREDENTIAL_DRAWS, or any
#     call through a name containing credential_pool. The pool has no API yet,
#     so these names are the ones it will be required to expose;
#   - dynamic resolution a static check cannot follow: exec, eval, getattr on a
#     dispatch module, and importlib.import_module or __import__ unless the
#     argument is a string literal naming a module outside DISPATCH_ROOTS;
#   - a runner.subject_guard.Decision constructed outside runner/subject_guard.py,
#     which forges the gate's answer.
#
# THE REACHABILITY RULE. A site is reached only through
# runner.subject_guard.evaluate() when, in the innermost function that contains
# it, a name D is bound by `D = evaluate(...)` resolving to that function, or is
# a parameter annotated as runner.subject_guard.Decision, and the site sits
# either in the body of `if D.permits:` or in the same statement list after
# `if not D.permits:` whose body ends in return, raise, continue or break. A
# rebinding of D, in that block or in a nested one, ends the region. Nothing
# crosses a function boundary: a nested function, a class body and a lambda's
# later caller are not reached by an outer check, so a lambda's body is read
# with no permits region at all. The name evaluate resolves to the gate only
# through an import the scope does not shadow: a module that binds the imported
# name again by def, class or assignment, and a function whose parameter or
# local store carries the name its call starts from, are not calling the gate.
# The rule is syntactic and intra-procedural on purpose, so a reviewer can see
# from the call site alone that the gate ran.
#
# THE ONE EXEMPTION. A network site in a test file, named test_*.py or
# conftest.py under a directory named tests, is exempt when its destination,
# the first positional argument or the host, address, url or server_address
# keyword (the first element where it is an address tuple), is the string
# literal 127.0.0.1 or a URL literal whose host is 127.0.0.1; no destination or
# routing keyword (proxies, proxy, source_address, base_url) is supplied by an
# expression rather than a literal; and no other host literal appears: not
# localhost, 0.0.0.0, ::, an empty host, another address, a dotted hostname or
# another URL. That is a loopback stub server a test starts, and nothing else.
# A helper module beside the tests is not a test file and needs an allowlist
# entry.
#
# WHAT IT CANNOT SEE, stated so a green run is not read as more. A call through
# an object whose type the scan cannot resolve (a session made elsewhere, a
# module loaded by path and exec_module), code built at run time without exec
# or eval, a C extension, an untracked file that .gitignore excludes, because
# the file list is git's tracked files plus the untracked ones it does not
# ignore, and anything outside the three directories. A connector adapter that dispatches through such a path
# passes this check, which is why the allowlist and the review rule remain. VA-R6
# trusts a name inside a test module: a receiver named monkeypatch or mp whose
# setattr or delattr calls its first argument rather than patching it would hide
# that reference, and the builtin names count only where the scope does not
# rebind them.
# ---------------------------------------------------------------------------

DISPATCH_DIRS = ("runner", "connectors", "app")
GUARD_REL = "runner/subject_guard.py"
EVALUATE = "runner.subject_guard.evaluate"
DECISION = "runner.subject_guard.Decision"
ALLOWLIST_REL = "runner/dispatch_allowlist.yaml"

#: The configurable pattern list: (fnmatch pattern on a resolved dotted name, act).
DISPATCH_PATTERNS = (
    ("subprocess.run", "process"), ("subprocess.Popen", "process"), ("subprocess.call", "process"),
    ("subprocess.check_call", "process"), ("subprocess.check_output", "process"),
    ("subprocess.getoutput", "process"), ("subprocess.getstatusoutput", "process"),
    ("os.system", "process"), ("os.popen", "process"), ("os.exec*", "process"),
    ("os.spawn*", "process"), ("os.posix_spawn*", "process"), ("os.startfile", "process"),
    ("pty.spawn", "process"), ("asyncio.create_subprocess_*", "process"),
    ("socket.socket", "network"), ("socket.create_connection", "network"),
    ("socket.create_server", "network"), ("urllib.request.urlopen", "network"),
    ("urllib.request.urlretrieve", "network"), ("urllib.request.build_opener", "network"),
    ("requests.*", "network"), ("http.client.*", "network"), ("httpx.*", "network"),
    ("aiohttp.*", "network"), ("asyncio.open_connection", "network"),
    ("asyncio.open_unix_connection", "network"), ("asyncio.start_server", "network"),
    ("http.server.*Server", "network"), ("socketserver.*Server", "network"),
    ("ftplib.*", "network"), ("smtplib.*", "network"),
    ("websocket.*", "subscription"), ("websockets.*", "subscription"), ("telethon.*", "subscription"),
    ("docker.*", "container"),
    ("shlex.split", "argv"), ("shlex.join", "argv"), ("shlex.quote", "argv"),
)
ARGV_BUILDERS = ("build_argv", "construct_argv", "fill_command_template")
CREDENTIAL_DRAWS = ("draw_credential", "checkout_credential")
DISPATCH_ROOTS = frozenset(p.split(".")[0] for p, _ in DISPATCH_PATTERNS)
LOOPBACK = "127.0.0.1"
LOOPBACK_URL_RE = re.compile(r"^https?://127\.0\.0\.1(?:[:/]|$)")
OTHER_HOST_RE = re.compile(r"^(?:localhost|0\.0\.0\.0|::|\d{1,3}(?:\.\d{1,3}){3}|(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,})$")
#: Keywords that name a call's destination, and keywords that route or bind it.
LOOPBACK_DEST_KEYWORDS = ("host", "address", "url", "server_address")
LOOPBACK_ROUTE_KEYWORDS = ("proxies", "proxy", "source_address", "base_url")
REASON_MIN_WORDS = 5
ENTRY_KEYS = ("path", "function", "call", "count", "reason")
#: VA-R6, test modules only. Calls whose first argument, or target keyword, is the
#: object a patch replaces an attribute on: the builtins, a method of that name on
#: a receiver whose last name is in PATCH_METHOD_RECEIVERS, and patch.object by its
#: exact resolved name, so a name that merely ends in "patch", such as dispatch,
#: is not one.
PATCH_CALL_NAMES = ("setattr", "delattr")
PATCH_METHOD_RECEIVERS = ("monkeypatch", "mp")
PATCH_OBJECT_NAMES = ("unittest.mock.patch.object", "mock.patch.object")
PATCH_TARGET_KEYWORDS = ("target",)

ACT_PHRASE = {
    "process": "runs a process",
    "network": "opens a network connection or listener",
    "subscription": "opens a subscription",
    "container": "starts or drives a container",
    "argv": "constructs argv",
    "credential": "draws a credential",
    "dynamic": "resolves a callable or a module at run time, which no static check can follow",
    "forgery": "constructs a Decision outside runner/subject_guard.py, which forges the gate's answer",
}


class Site:
    __slots__ = ("rel", "line", "function", "call", "act", "guarded", "exempt")

    def __init__(self, rel, line, function, call, act, guarded, exempt):
        self.rel, self.line, self.function, self.call = rel, line, function, call
        self.act, self.guarded, self.exempt = act, guarded, exempt

    @property
    def key(self) -> tuple:
        return (self.rel, self.function, self.call)


def _package(rel: str) -> list[str]:
    """The package a file's relative imports resolve against."""
    parts = rel[:-3].split("/")
    return parts[:-1]


def _aliases(tree, rel: str) -> dict:
    out: dict = {}
    pkg = _package(rel)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.asname:
                    out[a.asname] = a.name
                else:
                    root = a.name.split(".")[0]
                    out[root] = root
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            if node.level:
                head = pkg[: len(pkg) - (node.level - 1)] if node.level > 1 else pkg
                base = ".".join(head + ([base] if base else []))
            for a in node.names:
                out[a.asname or a.name] = f"{base}.{a.name}" if base else a.name
    return out


def _dotted(node, aliases: dict) -> str | None:
    if isinstance(node, ast.Name):
        return aliases.get(node.id, node.id)
    if isinstance(node, ast.Attribute):
        head = _dotted(node.value, aliases)
        return f"{head}.{node.attr}" if head else None
    return None


def _stores(nodes) -> set[str]:
    names: set[str] = set()
    for n in nodes:
        for sub in ast.walk(n):
            if isinstance(sub, ast.Name) and isinstance(sub.ctx, (ast.Store, ast.Del)):
                names.add(sub.id)
            elif isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                names.add(sub.name)
    return names


def _exits(stmt) -> bool:
    return isinstance(stmt, (ast.Return, ast.Raise, ast.Continue, ast.Break))


def _module_stores(body) -> set[str]:
    """Names a module binds at its top level other than by import."""
    names: set[str] = set()
    for st in body:
        if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(st.name)
        elif not isinstance(st, (ast.Import, ast.ImportFrom)):
            names |= _stores([st])
    return names


def _head(node) -> str | None:
    """The Name an attribute chain starts from, or None."""
    while isinstance(node, ast.Attribute):
        node = node.value
    return node.id if isinstance(node, ast.Name) else None


class _Scan:
    """One file's sites. See the block comment above for every rule applied."""

    def __init__(self, rel: str, tree):
        self.rel, self.aliases, self.sites = rel, _aliases(tree, rel), []
        parts = rel.split("/")
        self.in_tests = "tests" in parts[:-1] and (
            (parts[-1].startswith("test_") and parts[-1].endswith(".py")) or parts[-1] == "conftest.py")
        # A module that imports the gate's evaluate and binds the same name again
        # by def, class or assignment has replaced the gate, so the name no
        # longer resolves to it anywhere in the file.
        self._module_bound = _module_stores(tree.body)
        for name in self._module_bound:
            if self.aliases.get(name) == EVALUATE:
                del self.aliases[name]
        self._shadow: list[frozenset] = [frozenset()]
        # VA-R6: per scope, the (object, attribute) pairs the scope patches or
        # assigns by a literal attribute name.
        self._patched: list[frozenset] = [frozenset()]
        self._scope(tree.body, "<module>", set())

    def _scope(self, body, qual: str, bound: set, shadow: frozenset | None = None) -> None:
        self._shadow.append(self._shadow[-1] if shadow is None else shadow)
        self._patched.append(self._patched_pairs(body))
        try:
            self._block(body, qual, set(bound), set())
        finally:
            self._patched.pop()
            self._shadow.pop()

    def _is_patch_call(self, call) -> bool:
        """VA-R6, in a test module only: the builtin setattr or delattr where nothing
        rebinds the name, a method so named on a receiver named monkeypatch or mp, or
        patch.object by its exact resolved name."""
        if not self.in_tests:
            return False
        func = call.func
        if isinstance(func, ast.Name):
            return (func.id in PATCH_CALL_NAMES and func.id not in self._shadow[-1]
                    and func.id not in self._module_bound and func.id not in self.aliases)
        if isinstance(func, ast.Attribute):
            if func.attr in PATCH_CALL_NAMES:
                recv = func.value
                last = recv.id if isinstance(recv, ast.Name) else (
                    recv.attr if isinstance(recv, ast.Attribute) else None)
                return last in PATCH_METHOD_RECEIVERS
            if func.attr == "object":
                return _dotted(func, self.aliases) in PATCH_OBJECT_NAMES
        return False

    @staticmethod
    def _patch_target(call):
        if call.args:
            return call.args[0]
        return next((k.value for k in call.keywords if k.arg in PATCH_TARGET_KEYWORDS), None)

    def _patched_pairs(self, body) -> frozenset:
        """(object, attribute) for each patch call with a literal attribute name and
        each attribute assigned or deleted, in this body and not in a nested def,
        class or lambda. Empty outside a test module, where VA-R6 does not apply."""
        pairs: set = set()
        if not self.in_tests:
            return frozenset()
        todo = collections.deque(body)
        while todo:
            n = todo.popleft()
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
                continue
            todo.extend(ast.iter_child_nodes(n))
            if isinstance(n, ast.Call) and self._is_patch_call(n):
                target = self._patch_target(n)
                attr = n.args[1] if len(n.args) > 1 else next(
                    (k.value for k in n.keywords if k.arg in ("name", "attribute")), None)
                obj = _dotted(target, self.aliases) if target is not None else None
                if obj and isinstance(attr, ast.Constant) and isinstance(attr.value, str):
                    pairs.add((obj, attr.value))
            elif isinstance(n, ast.Attribute) and isinstance(n.ctx, (ast.Store, ast.Del)):
                obj = _dotted(n.value, self.aliases)
                if obj:
                    pairs.add((obj, n.attr))
        return frozenset(pairs)

    def _not_a_site(self, n, parents: dict, patch_targets: set) -> bool:
        """VA-R6, in a test module only: a reference a patch replaces an attribute
        on, the object of an attribute assigned over, or the patch's own read of the
        original it replaces where that read is not called in place. Never a
        reference passed as any other argument."""
        if not self.in_tests:
            return False
        if id(n) in patch_targets:
            return True
        parent = parents.get(id(n))
        if not (isinstance(parent, ast.Attribute) and parent.value is n and isinstance(parent.ctx, ast.Load)):
            return False
        if parent.attr.startswith("__") and parent.attr.endswith("__"):
            return False
        grand = parents.get(id(parent))
        if isinstance(grand, ast.Call) and grand.func is parent:
            return False
        return (_dotted(n, self.aliases), parent.attr) in self._patched[-1]

    def _is_evaluate(self, func) -> bool:
        """func resolves to runner.subject_guard.evaluate, and no enclosing
        function scope rebinds the name it starts from (a parameter or a local
        store shadows the import)."""
        return _head(func) not in self._shadow[-1] and _dotted(func, self.aliases) == EVALUATE

    def _permits_test(self, test, bound: set):
        neg = isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not)
        inner = test.operand if neg else test
        if isinstance(inner, ast.Attribute) and inner.attr == "permits" and isinstance(inner.value, ast.Name) \
                and inner.value.id in bound:
            return inner.value.id, not neg
        return None, False

    def _block(self, stmts, qual: str, bound: set, permitted: set) -> None:
        bound, permitted = set(bound), set(permitted)
        for st in stmts:
            if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)):
                args = st.args
                for e in st.decorator_list + args.defaults + [d for d in args.kw_defaults if d]:
                    self._expr(e, qual, permitted)
                params = args.posonlyargs + args.args + args.kwonlyargs
                given = {a.arg for a in params if a.annotation is not None
                         and (_dotted(a.annotation, self.aliases) == DECISION
                              or (isinstance(a.annotation, ast.Constant) and a.annotation.value in ("Decision", DECISION)))}
                local = {a.arg for a in params + [args.vararg, args.kwarg] if a is not None} | _stores(st.body)
                self._scope(st.body, st.name if qual == "<module>" else f"{qual}.{st.name}", given,
                            self._shadow[-1] | frozenset(local))
                bound.discard(st.name)
                permitted.discard(st.name)
                continue
            if isinstance(st, ast.ClassDef):
                for e in st.decorator_list + [k.value for k in st.keywords]:
                    self._expr(e, qual, permitted)
                for base in st.bases:
                    # Instantiating a subclass is a call the scan cannot follow, so
                    # the class statement that inherits a dispatch class is the site.
                    name = _dotted(base, self.aliases)
                    act = self._classify(name, True) if name else ""
                    if act:
                        self.sites.append(Site(self.rel, st.lineno, qual, name, act, bool(permitted), False))
                    else:
                        self._expr(base, qual, permitted)
                self._scope(st.body, st.name if qual == "<module>" else f"{qual}.{st.name}", set())
                continue
            if isinstance(st, ast.If):
                self._expr(st.test, qual, permitted)
                name, positive = self._permits_test(st.test, bound)
                if name and positive:
                    self._block(st.body, qual, bound, permitted | {name})
                    self._block(st.orelse, qual, bound, permitted)
                elif name:
                    self._block(st.body, qual, bound, permitted)
                    self._block(st.orelse, qual, bound, permitted | {name})
                else:
                    self._block(st.body, qual, bound, permitted)
                    self._block(st.orelse, qual, bound, permitted)
                changed = _stores(st.body + st.orelse)
                bound -= changed
                permitted -= changed
                if name and not positive and st.body and _exits(st.body[-1]) and name in bound:
                    permitted.add(name)
                continue
            if isinstance(st, (ast.Assign, ast.AnnAssign)) and isinstance(st.value, ast.Call) \
                    and self._is_evaluate(st.value.func):
                targets = st.targets if isinstance(st, ast.Assign) else [st.target]
                self._expr(st.value, qual, permitted)
                changed = _stores(targets)
                bound -= changed
                permitted -= changed
                if len(targets) == 1 and isinstance(targets[0], ast.Name):
                    bound.add(targets[0].id)
                continue
            nested = []
            for _, value in ast.iter_fields(st):
                items = value if isinstance(value, list) else [value]
                if items and all(isinstance(v, ast.stmt) for v in items):
                    nested.append(items)
                    continue
                for v in items:
                    if isinstance(v, ast.ExceptHandler):
                        if v.type is not None:
                            self._expr(v.type, qual, permitted)
                        nested.append(v.body)
                    elif isinstance(v, ast.match_case):
                        if v.guard is not None:
                            self._expr(v.guard, qual, permitted)
                        nested.append(v.body)
                    elif isinstance(v, ast.withitem):
                        self._expr(v.context_expr, qual, permitted)
                    elif isinstance(v, ast.AST):
                        self._expr(v, qual, permitted)
            for body in nested:
                self._block(body, qual, bound, permitted)
            changed = _stores([st])
            bound -= changed
            permitted -= changed

    def _classify(self, name: str, call: bool) -> str:
        last = name.rsplit(".", 1)[-1]
        if name == DECISION:
            return "" if self.rel == GUARD_REL else "forgery"
        for pattern, act in DISPATCH_PATTERNS:
            if fnmatch.fnmatchcase(name, pattern) and (call or not any(c in pattern for c in "*?[")):
                return act
        if not call:
            return ""
        if last in ARGV_BUILDERS or (last in ("format", "format_map") and name[: -len(last) - 1].endswith("command_template")):
            return "argv"
        if last in CREDENTIAL_DRAWS or "credential_pool" in name:
            return "credential"
        if name in ("exec", "eval"):
            return "dynamic"
        return ""

    def _dynamic(self, node) -> bool:
        name = _dotted(node.func, self.aliases)
        if name == "getattr" and node.args:
            target = _dotted(node.args[0], self.aliases) or ""
            return target.split(".")[0] in DISPATCH_ROOTS
        if name in ("importlib.import_module", "__import__"):
            arg = node.args[0] if node.args else None
            literal = isinstance(arg, ast.Constant) and isinstance(arg.value, str)
            return not literal or arg.value.split(".")[0] in DISPATCH_ROOTS
        return False

    def _loopback_only(self, node) -> bool:
        """The call's destination is the 127.0.0.1 literal, and nothing else in it
        names a host or supplies one from an expression."""
        dest = node.args[0] if node.args else next(
            (k.value for k in node.keywords if k.arg in LOOPBACK_DEST_KEYWORDS), None)
        if isinstance(dest, ast.Tuple) and dest.elts:
            dest = dest.elts[0]
        if not (isinstance(dest, ast.Constant) and isinstance(dest.value, str)
                and (dest.value == LOOPBACK or LOOPBACK_URL_RE.match(dest.value))):
            return False
        for k in node.keywords:
            if k.arg in LOOPBACK_DEST_KEYWORDS + LOOPBACK_ROUTE_KEYWORDS and any(
                    isinstance(sub, (ast.Name, ast.Attribute, ast.Call, ast.JoinedStr)) for sub in ast.walk(k.value)):
                return False
        consts = [c.value for a in list(node.args) + [k.value for k in node.keywords]
                  for c in ast.walk(a) if isinstance(c, ast.Constant) and isinstance(c.value, str)]
        loop = [c for c in consts if c == LOOPBACK or LOOPBACK_URL_RE.match(c)]
        other = [c for c in consts if c not in loop and (c in ("", "::") or "://" in c or OTHER_HOST_RE.match(c))]
        return bool(loop) and not other

    @staticmethod
    def _walk(node, lambdas: list):
        """ast.walk's order, stopping at each lambda, which is collected instead."""
        todo = collections.deque([node])
        while todo:
            n = todo.popleft()
            if isinstance(n, ast.Lambda):
                lambdas.append(n)
                continue
            todo.extend(ast.iter_child_nodes(n))
            yield n

    def _expr(self, node, qual: str, permitted: set) -> None:
        lambdas: list = []
        nodes = list(self._walk(node, lambdas))
        call_funcs = {id(n.func) for n in nodes if isinstance(n, ast.Call)}
        parents = {id(c): n for n in nodes for c in ast.iter_child_nodes(n)}
        patch_targets = set()
        for n in nodes if self.in_tests else ():
            if isinstance(n, ast.Call) and self._is_patch_call(n):
                target = self._patch_target(n)
                if target is not None:
                    patch_targets.add(id(target))
            elif isinstance(n, ast.Attribute) and isinstance(n.ctx, (ast.Store, ast.Del)):
                patch_targets.add(id(n.value))
        for n in nodes:
            reference = False
            if isinstance(n, ast.Call):
                name = _dotted(n.func, self.aliases)
                if isinstance(n.func, ast.Attribute) and name is None:
                    name = f"<object>.{n.func.attr}"
                act = "dynamic" if self._dynamic(n) else (self._classify(name, True) if name else "")
            elif isinstance(n, (ast.Attribute, ast.Name)) and id(n) not in call_funcs \
                    and isinstance(getattr(n, "ctx", None), ast.Load):
                name = _dotted(n, self.aliases)
                act = self._classify(name, False) if name else ""
                reference = True
                # VA-R6 reaches dispatch patterns only: a patch of the gate's own
                # Decision type is a forgery whatever form it takes.
                if act and act != "forgery" and self._not_a_site(n, parents, patch_targets):
                    continue
            else:
                continue
            if not act:
                continue
            # A stored reference to a dispatch callable, bound or passed as
            # functools.partial's argument, can be called later from anywhere,
            # so no permits region reaches it. A Decision reference is a read of
            # the gate's type and keeps the region it sits in.
            guarded = bool(permitted) and not (reference and act != "forgery")
            exempt = self.in_tests and act == "network" and isinstance(n, ast.Call) and self._loopback_only(n)
            self.sites.append(Site(self.rel, getattr(n, "lineno", 0), qual, name, act, guarded, exempt))
        for lam in lambdas:
            # A lambda's body runs when its later caller calls it, which no
            # outer permits check reaches: it is read with no region.
            for d in lam.args.defaults + [d for d in lam.args.kw_defaults if d]:
                self._expr(d, qual, permitted)
            self._expr(lam.body, qual, set())


def dispatch_sources() -> tuple[list[tuple[str, str]], list[Finding]]:
    """Every Python file the mode reads, as (path, text), and any it could not read."""
    def _ls(*extra) -> list[str]:
        # -z and core.quotePath=false: git C-quotes a path carrying a non-ASCII
        # byte, and a quoted line ends in .py" rather than .py, so a line filter
        # would drop that file without a word.
        proc = subprocess.run(["git", "-c", "core.quotePath=false", "ls-files", "-z", *extra, "--",
                               *DISPATCH_DIRS], cwd=ROOT, capture_output=True)
        if proc.returncode != 0:
            raise OSError("git ls-files failed")
        return [p for p in proc.stdout.decode("utf-8").split("\0") if p.endswith(".py")]

    unread: list[Finding] = []
    try:
        rels = sorted(set(_ls()) | set(_ls("--others", "--exclude-standard")))
    except (OSError, ValueError) as exc:
        return [], [Finding(
            "AUTH_DISPATCH_FILE_UNREADABLE", "git ls-files",
            f"the file list for runner/, connectors/ and app/ could not be read ({exc.__class__.__name__}), "
            "so no dispatch site can be found and a clean result would mean nothing was read",
            "run this mode from a git checkout of the repository with git on PATH")]
    out = []
    for rel in rels:
        path = ROOT / rel
        if not path.is_file():
            unread.append(Finding(
                "AUTH_DISPATCH_FILE_UNREADABLE", rel,
                "git lists this Python file and it is not a file on disk, so it was not read and a "
                "dispatch site in it would go unseen",
                "restore the file; or remove it from the index with git rm --cached"))
            continue
        try:
            out.append((rel, path.read_text(encoding="utf-8")))
        except (OSError, UnicodeDecodeError) as exc:
            unread.append(Finding(
                "AUTH_DISPATCH_FILE_UNREADABLE", rel,
                f"the file could not be read ({exc.__class__.__name__}), so a dispatch site in it would go unseen",
                "re-save the file as UTF-8; or remove it"))
    return out, unread


def scan_sources(sources: list[tuple[str, str]]) -> tuple[list[Site], list[Finding]]:
    sites: list[Site] = []
    unread: list[Finding] = []
    for rel, text in sources:
        try:
            tree = ast.parse(text, filename=rel)
        except SyntaxError as exc:
            unread.append(Finding(
                "AUTH_DISPATCH_FILE_UNREADABLE", f"{rel}:{exc.lineno}",
                "the file does not parse as Python, so a dispatch site in it would go unseen and a clean "
                "result would claim a file nobody read",
                "fix the syntax error at that line; or remove the file"))
            continue
        sites += _Scan(rel, tree).sites
    return sites, unread


def check_dispatch(sites: list[Site], allow, present: bool, stamped: bool) -> tuple[list[Finding], list[Finding]]:
    """(findings, certification). allow is the parsed allowlist document."""
    open_sites = [s for s in sites if not s.guarded and not s.exempt]
    if not present:
        return [Finding(
            "AUTH_DISPATCH_ALLOWLIST_ABSENT", ALLOWLIST_REL,
            "--dispatch-paths was asked to prove that every call site constructing argv, running a "
            "process, opening a connection or a subscription, or drawing a credential is reached only "
            "through runner.subject_guard.evaluate() or listed with a written reason (SS-6), and the "
            "allowlist it compares against does not exist. SS-14 item 6 lists the file as item 8, and "
            "docs/THE-GAMEPLAN.md section 4 states the consequence: the bypass check has nothing to "
            f"compare against, and gate coverage becomes a claim. {len(open_sites)} site(s) outside "
            "the gate were found and none can be adjudicated",
            "the operator ratifies a drafted allowlist, which lands at runner/dispatch_allowlist.yaml "
            "with a dated row in doctrine/DOCTRINE_STATUS.md as one Class F act; or gate each site "
            "listed below inside if decision.permits: after decision = evaluate(request); or remove "
            "the site")], []

    findings: list[Finding] = []
    entries = _d(allow, "dispatch_allowlist", "entries")
    if not isinstance(entries, list):
        findings.append(Finding(
            "AUTH_DISPATCH_ALLOWLIST_MALFORMED", ALLOWLIST_REL,
            "the file carries no dispatch_allowlist.entries list, so no entry can be read and every "
            "site outside the gate is unadjudicated",
            "restore the dispatch_allowlist wrapper key with an entries list; or remove the file, which "
            "this mode then refuses as absent"))
        entries = []
    usable: dict[tuple, dict] = {}
    for n, e in enumerate(entries, 1):
        where = f"{ALLOWLIST_REL} entry {n}"
        if not isinstance(e, dict) or set(e) - set(ENTRY_KEYS) or set(ENTRY_KEYS) - set(e) - {"reason"}:
            findings.append(Finding(
                "AUTH_DISPATCH_ALLOWLIST_MALFORMED", where,
                f"an entry carries exactly {', '.join(ENTRY_KEYS)}, and this one does not, so what it "
                "exempts cannot be read",
                "write the entry with those five keys and nothing else; or delete it"))
            continue
        reason = e.get("reason")
        if not isinstance(reason, str) or len(reason.split()) < REASON_MIN_WORDS:
            findings.append(Finding(
                "AUTH_DISPATCH_ALLOWLIST_REASON_MISSING", where,
                "the entry exempts a dispatch site from the gate with no written reason, or with fewer "
                f"than {REASON_MIN_WORDS} words, which is a token rather than a reason. SS-6 permits an "
                "exemption only with a written reason",
                "write the reason: what the call does, why it reaches no subject, and why it cannot "
                "sit behind evaluate(); or gate the site and delete the entry"))
            continue
        if not (isinstance(e["count"], int) and not isinstance(e["count"], bool) and e["count"] > 0):
            findings.append(Finding(
                "AUTH_DISPATCH_ALLOWLIST_MALFORMED", where,
                "the entry's count is not a positive integer, so a second call added to the same "
                "function could ride on it unseen",
                "set count to the number of such calls in that function"))
            continue
        usable[(str(e["path"]), str(e["function"]), str(e["call"]))] = e

    groups: dict[tuple, list[Site]] = {}
    for s in open_sites:
        groups.setdefault(s.key, []).append(s)
    for key, group in groups.items():
        entry = usable.get(key)
        if entry is None:
            for s in group:
                findings.append(Finding(
                    "AUTH_DISPATCH_SITE_UNGATED", f"{s.rel}:{s.line}, in {s.function}, calling {s.call}",
                    f"this call {ACT_PHRASE[s.act]} and is not reached through "
                    "runner.subject_guard.evaluate(): it is not inside if D.permits: or after "
                    "if not D.permits: returns, with D bound by evaluate() in the same function or "
                    "passed in annotated as Decision, and runner/dispatch_allowlist.yaml lists no "
                    "entry for it. SS-6 puts the gate before argv, before a credential is drawn and "
                    "before a subscription opens",
                    "gate the call inside if decision.permits: after decision = evaluate(request); "
                    "or draft an allowlist entry naming the path, the function, the call, the count "
                    "and a written reason, which is a Class F change the operator ratifies; or "
                    "remove the call"))
        elif entry["count"] != len(group):
            findings.append(Finding(
                "AUTH_DISPATCH_ALLOWLIST_COUNT_MISMATCH", f"{key[0]}, in {key[1]}, calling {key[2]}",
                f"the entry exempts {entry['count']} such call(s) and the function makes {len(group)}, "
                "so an exemption written for one call would cover another nobody reviewed",
                "set count to the number of calls after reviewing each; or gate the new call"))
    for key in usable:
        if key not in groups:
            findings.append(Finding(
                "AUTH_DISPATCH_ALLOWLIST_ENTRY_STALE", f"{ALLOWLIST_REL}: {key[0]}, in {key[1]}, calling {key[2]}",
                "the entry exempts a call that no file makes outside the gate, so it would silently "
                "exempt the next call written there",
                "delete the entry; or, if the call moved, move the entry with it"))

    certification = [] if stamped else [Finding(
        "AUTH_DISPATCH_ALLOWLIST_UNSTAMPED", ALLOWLIST_REL,
        "the allowlist exists and carries no whole-artifact dated row in doctrine/DOCTRINE_STATUS.md. "
        "It is Class F, so its exemptions bind nothing until the operator stamps it, and a clean "
        "comparison against it would certify gate coverage on an unratified list",
        "the operator stamps runner/dispatch_allowlist.yaml in the pin of record; or gate the "
        "exempted sites and delete their entries")]
    return findings, certification


def dispatch_paths(quiet: bool = False) -> int:
    sources, unread = dispatch_sources()
    sites, unparsed = scan_sources(sources)
    unread += unparsed
    path = ROOT / ALLOWLIST_REL
    present = path.is_file()
    allow = None
    if present:
        try:
            allow = yaml.safe_load(path.read_text(encoding="utf-8")) if yaml is not None else None
        except Exception as exc:
            unread.append(Finding(
                "AUTH_DISPATCH_FILE_UNREADABLE", ALLOWLIST_REL,
                f"the allowlist could not be parsed ({exc.__class__.__name__}), so no entry can be read",
                "fix the YAML; or restore the file from git"))
    stamped = present and pin_of_record.read(ROOT, {k: set(v) for k, v in RATIFY_SECTIONS.items()}).artifact_stamped(ALLOWLIST_REL)
    findings, certification = check_dispatch(sites, allow, present, stamped)
    every = unread + findings + certification
    _telemetry("error" if unread else ("refuse" if every else "pass"), every, gate=f"{GATE}-dispatch-paths")
    for f in every:
        print(f.render(), file=sys.stderr)
        print(file=sys.stderr)
    outside = [s for s in sites if not s.guarded and not s.exempt]
    if every:
        print("  sites outside the gate, by path, line, function, call and act:", file=sys.stderr)
        for s in outside:
            print(f"    {s.rel}:{s.line}  {s.function}  {s.call}  {s.act}", file=sys.stderr)
    if not quiet or every:
        print(
            f"validate_authorization --dispatch-paths: {len(sources)} file(s) under "
            f"{', '.join(d + '/' for d in DISPATCH_DIRS)} read, {len(sites)} site(s), "
            f"{sum(s.guarded for s in sites)} behind evaluate(), {sum(s.exempt for s in sites)} exempt "
            f"as loopback test servers, {len(outside)} outside the gate"
        )
    if unread:
        return 2
    return 1 if every else 0


# Planted sources for the dispatch self-test. Each is parsed and never run.
_GATED = (
    "from runner.subject_guard import evaluate\nimport subprocess\n\n"
    "def dispatch(request):\n    decision = evaluate(request)\n    if decision.permits:\n"
    "        subprocess.run(['tool', '--flag'])\n"
)
_UNGATED = "import subprocess\n\ndef dispatch(request):\n    subprocess.run(['tool'])\n"
_TWICE = "import subprocess\n\ndef dispatch(request):\n    subprocess.run(['tool'])\n    subprocess.run(['tool'])\n"
_AFTER_BRANCH = (
    "from runner.subject_guard import evaluate\nimport subprocess\n\n"
    "def dispatch(request):\n    decision = evaluate(request)\n    if decision.permits:\n        pass\n"
    "    subprocess.run(['tool'])\n"
)
_EARLY_EXIT = (
    "from runner import subject_guard\nimport subprocess as sp\n\n"
    "def dispatch(request):\n    decision = subject_guard.evaluate(request)\n"
    "    if not decision.permits:\n        return decision\n    sp.Popen(['tool'])\n"
)
_REBOUND = (
    "from runner.subject_guard import evaluate\nimport subprocess\n\n"
    "def dispatch(request, other):\n    decision = evaluate(request)\n    if decision.permits:\n"
    "        decision = other\n        subprocess.run(['tool'])\n"
)
_PARAMETER = (
    "from runner.subject_guard import Decision\nimport socket\n\n"
    "def connect(decision: Decision, host):\n    if decision.permits:\n"
    "        socket.create_connection((host, 443))\n"
)
_FROM_ALIAS = "from os import system as run_it\n\ndef go():\n    run_it('tool')\n"
_REFERENCE = "import subprocess\n\ndef go():\n    fn = subprocess.run\n    return fn\n"
_URLOPEN = "from urllib.request import urlopen\n\ndef fetch(url):\n    return urlopen(url)\n"
_LOOPBACK = "import socket\n\ndef test_stub_server():\n    srv = socket.create_server(('127.0.0.1', 0))\n    srv.close()\n"
_ALL_INTERFACES = "import socket\n\ndef test_stub_server():\n    srv = socket.create_server(('0.0.0.0', 0))\n    srv.close()\n"
_ARGV = "import shlex\n\ndef build(template):\n    return shlex.split(template)\n"
_CREDENTIAL = "def go(pool):\n    return pool.draw_credential('collection')\n"
_FORGERY = (
    "from runner.subject_guard import Decision\n\ndef fake():\n"
    "    return Decision(value='PERMITTED', permits=True, consequence='', connector_id='c', "
    "target_selector_type='handle')\n"
)
_DYNAMIC = "import importlib\n\ndef go(name):\n    return importlib.import_module(name)\n"
_LITERAL_IMPORT = "import importlib\n\ndef go():\n    return importlib.import_module('json')\n"
_GETATTR = "import subprocess\n\ndef go(name):\n    return getattr(subprocess, name)(['tool'])\n"
_DOCKER = "import docker\n\ndef go():\n    return docker.from_env()\n"
_SUBCLASS = "from http.server import ThreadingHTTPServer\n\n\nclass Server(ThreadingHTTPServer):\n    pass\n"
_RELATIVE = "from . import subject_guard\nimport subprocess\n\ndef go(r):\n    d = subject_guard.evaluate(r)\n    if d.permits:\n        subprocess.run(['tool'])\n"
_NESTED = (
    "from runner.subject_guard import evaluate\nimport subprocess\n\n"
    "def dispatch(request):\n    decision = evaluate(request)\n    if decision.permits:\n"
    "        def later():\n            subprocess.run(['tool'])\n        return later\n"
)
_BROKEN = "def go(:\n    pass\n"
_SHADOWED_MODULE = (
    "from runner.subject_guard import evaluate\nimport subprocess\n\n"
    "def evaluate(request):\n    return request\n\n"
    "def dispatch(request):\n    decision = evaluate(request)\n    if decision.permits:\n"
    "        subprocess.run(['tool'])\n"
)
_SHADOWED_PARAMETER = (
    "from runner.subject_guard import evaluate\nimport subprocess\n\n"
    "def dispatch(request, evaluate):\n    decision = evaluate(request)\n    if decision.permits:\n"
    "        subprocess.run(['tool'])\n"
)
_LAMBDA = (
    "from runner.subject_guard import evaluate\nimport subprocess\n\nHOOKS = {}\n\n"
    "def setup(request):\n    decision = evaluate(request)\n    if decision.permits:\n"
    "        HOOKS['run'] = lambda argv: subprocess.run(argv)\n"
)
_PARTIAL = (
    "from runner.subject_guard import evaluate\nimport functools\nimport subprocess\n\nHOOKS = {}\n\n"
    "def setup(request):\n    decision = evaluate(request)\n    if decision.permits:\n"
    "        HOOKS['run'] = functools.partial(subprocess.run, ['tool'])\n"
)
_NO_EXIT = (
    "from runner.subject_guard import evaluate\nimport subprocess\n\n"
    "def dispatch(request):\n    decision = evaluate(request)\n    if not decision.permits:\n"
    "        print(decision.consequence)\n    subprocess.run(['tool'])\n"
)
_LOOPBACK_AND_OTHER = (
    "import socket\n\ndef test_stub_client():\n"
    "    socket.create_connection(('127.0.0.1', 0), source_address=('10.0.0.5', 0))\n"
)
_VARIABLE_HOST = (
    "import socket\n\ndef test_stub_client(host):\n"
    "    socket.create_connection((host, 443), source_address=('127.0.0.1', 0))\n"
)
_LOOPBACK_PROXY = (
    "import requests\n\ndef test_stub_client(url):\n"
    "    requests.get(url, proxies={'https': 'http://127.0.0.1:9050'})\n"
)
_LOOPBACK_ROUTED = (
    "import socket\n\ndef test_stub_client(src):\n"
    "    socket.create_connection(('127.0.0.1', 0), source_address=(src, 0))\n"
)

# VA-R6. A patch target and its kept original are not sites; every other
# argument a patch takes, and a capture of a dispatch callable itself, still are.
_PATCH_TARGET = (
    "import socket\n\ndef test_guard(monkeypatch):\n"
    "    monkeypatch.setattr(socket.socket, 'connect', lambda sock, address: None)\n"
)
_PATCH_OBJECT = (
    "import socket\nfrom unittest import mock\n\ndef test_guard():\n"
    "    with mock.patch.object(socket.socket, 'connect_ex', return_value=111):\n        pass\n"
)
_ASSIGNED_OVER = "import socket\n\ndef guard(fn):\n    socket.socket.connect = fn\n"
_ORIGINAL_KEPT = (
    "import socket\n\ndef test_guard(monkeypatch):\n    real = socket.socket.connect\n"
    "    monkeypatch.setattr(socket.socket, 'connect', lambda sock, address: real(sock, address))\n"
)
_PATCH_WITH_PARTIAL = (
    "import functools\nimport socket\nimport subprocess\n\ndef test_guard(monkeypatch):\n"
    "    monkeypatch.setattr(socket.socket, 'connect', functools.partial(subprocess.run, ['tool']))\n"
)
_PATCH_VALUE_IS_A_DISPATCH = (
    "import subprocess\n\nHOOKS = type('Hooks', (), {})\n\ndef setup():\n"
    "    setattr(HOOKS, 'run', subprocess.run)\n"
)
_CALLABLE_KEPT = (
    "import subprocess\n\ndef test_guard(monkeypatch):\n    real = subprocess.run\n"
    "    monkeypatch.setattr(subprocess, 'run', lambda *a, **k: None)\n    return real\n"
)
_DUNDER_KEPT = (
    "import socket\n\ndef test_guard(monkeypatch):\n    make = socket.socket.__call__\n"
    "    monkeypatch.setattr(socket.socket, '__call__', lambda *a: None)\n    return make\n"
)
_ORIGINAL_UNPATCHED = "import socket\n\ndef keep():\n    return socket.socket.connect\n"
_SETATTR_REBOUND = (
    "import socket\n\ndef setattr(obj, name, value):\n    return obj(value)\n\n"
    "def go():\n    setattr(socket.socket, 'connect', None)\n"
)
_DECISION_PATCHED = (
    "from runner.subject_guard import Decision\n\ndef test_open(monkeypatch):\n"
    "    monkeypatch.setattr(Decision, 'permits', True)\n"
)
# The review of 2026-10-28: VA-R6 reaches test modules only, matches patch.object by
# its exact resolved name and a patch method by its receiver, and never exempts a
# kept original that is called in place.
_POPEN_SWAPPED = (
    "import subprocess\n\n_orig = subprocess.Popen._execute_child\n\n"
    "def _swap(self, args, *rest):\n    return _orig(self, ['tool'], *rest)\n\n"
    "subprocess.Popen._execute_child = _swap\n"
)
_CONNECT_REDIRECTED = (
    "import socket\n\n_real = socket.socket.connect\n\n"
    "def _dial(sock, address):\n    return _real(sock, address)\n\n"
    "socket.socket.connect = _dial\n"
)
_DISPATCH_DOT_OBJECT = (
    "import subprocess\nfrom runner import dispatch\n\ndef test_go():\n"
    "    dispatch.object(subprocess.run, ['tool'])\n"
)
_OTHER_PATCH_OBJECT = (
    "import subprocess\nfrom runner.tests import helpers\n\ndef test_go():\n"
    "    helpers.patch.object(subprocess.run, ['tool'])\n"
)
_HOOKS_SETATTR = (
    "import subprocess\n\nclass Hooks:\n    pass\n\ndef test_go():\n"
    "    Hooks.setattr(subprocess.run, 'run', None)\n"
)
_KEPT_AND_CALLED = (
    "import socket\n\ndef test_dial(s, address):\n"
    "    socket.socket.connect = socket.socket.connect\n    socket.socket.connect(s, address)\n"
)

_ENTRY = {"path": "runner/planted.py", "function": "dispatch", "call": "subprocess.run", "count": 1,
          "reason": "A planted entry for the self-test, naming one call that reaches no subject."}


def _allow(*entries) -> dict:
    return {"dispatch_allowlist": {"entries": [dict(e) for e in entries]}}


def _dispatch_cases():
    """(description, sources, allowlist or None for absent, stamped, expected code or None for clean).

    Three cases fire a second code, and the cascade is the designed behaviour
    rather than noise: an entry that cannot be read exempts nothing, so the site
    it names is also ungated. Those cases are listed in CASCADES.
    """
    p = "runner/planted.py"
    t = "runner/tests/test_planted.py"
    clean = _allow()
    no_reason = dict(_ENTRY)
    del no_reason["reason"]
    return [
        ("a dispatch site with no guard", [(p, _UNGATED)], clean, True, "AUTH_DISPATCH_SITE_UNGATED"),
        ("a fixture allowlist naming that site with a reason", [(p, _UNGATED)], _allow(_ENTRY), True, None),
        ("the allowlist absent", [(p, _UNGATED)], None, True, "AUTH_DISPATCH_ALLOWLIST_ABSENT"),
        ("the allowlist absent over a gated tree", [(p, _GATED)], None, True, "AUTH_DISPATCH_ALLOWLIST_ABSENT"),
        ("an allowlist entry with no reason", [(p, _UNGATED)], _allow(no_reason), True,
         "AUTH_DISPATCH_ALLOWLIST_REASON_MISSING"),
        ("an allowlist entry whose reason is a token", [(p, _UNGATED)], _allow(dict(_ENTRY, reason="ok")), True,
         "AUTH_DISPATCH_ALLOWLIST_REASON_MISSING"),
        ("a loopback-only test server under tests/", [(t, _LOOPBACK)], clean, True, None),
        ("the same loopback server outside tests/", [(p, _LOOPBACK)], clean, True, "AUTH_DISPATCH_SITE_UNGATED"),
        ("a test server bound to every interface", [(t, _ALL_INTERFACES)], clean, True, "AUTH_DISPATCH_SITE_UNGATED"),
        ("a site inside if decision.permits after evaluate()", [(p, _GATED)], clean, True, None),
        ("a site after the permits branch rather than in it", [(p, _AFTER_BRANCH)], clean, True,
         "AUTH_DISPATCH_SITE_UNGATED"),
        ("a site after an early return on not permits", [(p, _EARLY_EXIT)], clean, True, None),
        ("a site after the decision is rebound", [(p, _REBOUND)], clean, True, "AUTH_DISPATCH_SITE_UNGATED"),
        ("a site behind a Decision parameter's permits", [(p, _PARAMETER)], clean, True, None),
        ("a site in a function defined inside the permits branch", [(p, _NESTED)], clean, True,
         "AUTH_DISPATCH_SITE_UNGATED"),
        ("a relative import of the guard inside runner/", [("runner/planted.py", _RELATIVE)], clean, True, None),
        ("os.system imported under another name", [(p, _FROM_ALIAS)], clean, True, "AUTH_DISPATCH_SITE_UNGATED"),
        ("subprocess.run bound to a name rather than called", [(p, _REFERENCE)], clean, True,
         "AUTH_DISPATCH_SITE_UNGATED"),
        ("urlopen imported from urllib.request", [(p, _URLOPEN)], clean, True, "AUTH_DISPATCH_SITE_UNGATED"),
        ("argv built with shlex", [(p, _ARGV)], clean, True, "AUTH_DISPATCH_SITE_UNGATED"),
        ("a credential drawn before the gate", [(p, _CREDENTIAL)], clean, True, "AUTH_DISPATCH_SITE_UNGATED"),
        ("a Decision constructed outside the guard", [(p, _FORGERY)], clean, True, "AUTH_DISPATCH_SITE_UNGATED"),
        ("a module imported by a computed name", [(p, _DYNAMIC)], clean, True, "AUTH_DISPATCH_SITE_UNGATED"),
        ("a module imported by a literal outside the dispatch roots", [(p, _LITERAL_IMPORT)], clean, True, None),
        ("getattr on subprocess", [(p, _GETATTR)], clean, True, "AUTH_DISPATCH_SITE_UNGATED"),
        ("the docker SDK", [(p, _DOCKER)], clean, True, "AUTH_DISPATCH_SITE_UNGATED"),
        ("a class that inherits a server class", [(p, _SUBCLASS)], clean, True, "AUTH_DISPATCH_SITE_UNGATED"),
        ("an entry naming a call no file makes", [(p, _GATED)], _allow(_ENTRY), True,
         "AUTH_DISPATCH_ALLOWLIST_ENTRY_STALE"),
        ("a second call riding on a count of one", [(p, _TWICE)], _allow(_ENTRY), True,
         "AUTH_DISPATCH_ALLOWLIST_COUNT_MISMATCH"),
        ("an entry with an undeclared key", [(p, _UNGATED)], _allow(dict(_ENTRY, line=4)), True,
         "AUTH_DISPATCH_ALLOWLIST_MALFORMED"),
        ("an allowlist with no entries list", [(p, _GATED)], {"dispatch_allowlist": {}}, True,
         "AUTH_DISPATCH_ALLOWLIST_MALFORMED"),
        ("a valid allowlist the pin does not stamp", [(p, _UNGATED)], _allow(_ENTRY), False,
         "AUTH_DISPATCH_ALLOWLIST_UNSTAMPED"),
        ("a file that does not parse", [(p, _BROKEN)], clean, True, "AUTH_DISPATCH_FILE_UNREADABLE"),
        ("evaluate rebound by a module-level def", [(p, _SHADOWED_MODULE)], clean, True,
         "AUTH_DISPATCH_SITE_UNGATED"),
        ("evaluate shadowed by a parameter", [(p, _SHADOWED_PARAMETER)], clean, True, "AUTH_DISPATCH_SITE_UNGATED"),
        ("a lambda stored inside the permits branch", [(p, _LAMBDA)], clean, True, "AUTH_DISPATCH_SITE_UNGATED"),
        ("functools.partial on subprocess.run inside the permits branch", [(p, _PARTIAL)], clean, True,
         "AUTH_DISPATCH_SITE_UNGATED"),
        ("a site after if not permits whose body does not exit", [(p, _NO_EXIT)], clean, True,
         "AUTH_DISPATCH_SITE_UNGATED"),
        ("a test call naming 127.0.0.1 and another host", [(t, _LOOPBACK_AND_OTHER)], clean, True,
         "AUTH_DISPATCH_SITE_UNGATED"),
        ("a test call to a host held in a variable", [(t, _VARIABLE_HOST)], clean, True,
         "AUTH_DISPATCH_SITE_UNGATED"),
        ("a test call to a variable url through a loopback proxy", [(t, _LOOPBACK_PROXY)], clean, True,
         "AUTH_DISPATCH_SITE_UNGATED"),
        ("a loopback test call whose source address is a variable", [(t, _LOOPBACK_ROUTED)], clean, True,
         "AUTH_DISPATCH_SITE_UNGATED"),
        ("a loopback server in a helper module under tests/", [("runner/tests/helper.py", _LOOPBACK)], clean, True,
         "AUTH_DISPATCH_SITE_UNGATED"),
        # VA-R6, 2026-10-28.
        ("a patch target passed to monkeypatch.setattr", [(t, _PATCH_TARGET)], clean, True, None),
        ("a patch target passed to mock.patch.object", [(t, _PATCH_OBJECT)], clean, True, None),
        ("the object of an attribute assigned over in a test", [(t, _ASSIGNED_OVER)], clean, True, None),
        ("the object of an attribute assigned over outside a test", [(p, _ASSIGNED_OVER)], clean, True,
         "AUTH_DISPATCH_SITE_UNGATED"),
        ("the original of the attribute the same function patches", [(t, _ORIGINAL_KEPT)], clean, True, None),
        ("functools.partial on subprocess.run as the value a patch installs", [(t, _PATCH_WITH_PARTIAL)], clean,
         True, "AUTH_DISPATCH_SITE_UNGATED"),
        ("subprocess.run as the value setattr stores", [(p, _PATCH_VALUE_IS_A_DISPATCH)], clean, True,
         "AUTH_DISPATCH_SITE_UNGATED"),
        ("subprocess.run kept before the same function patches it", [(t, _CALLABLE_KEPT)], clean, True,
         "AUTH_DISPATCH_SITE_UNGATED"),
        ("a dunder of socket.socket kept before the same function patches it", [(t, _DUNDER_KEPT)], clean, True,
         "AUTH_DISPATCH_SITE_UNGATED"),
        ("a method of socket.socket kept with no patch beside it", [(p, _ORIGINAL_UNPATCHED)], clean, True,
         "AUTH_DISPATCH_SITE_UNGATED"),
        ("a module that rebinds setattr", [(p, _SETATTR_REBOUND)], clean, True, "AUTH_DISPATCH_SITE_UNGATED"),
        ("a patch of the gate's Decision type", [(t, _DECISION_PATCHED)], clean, True, "AUTH_DISPATCH_SITE_UNGATED"),
        # The review of 2026-10-28.
        ("a connector module that swaps Popen's launcher and keeps the original",
         [("connectors/planted/adapter.py", _POPEN_SWAPPED)], clean, True, "AUTH_DISPATCH_SITE_UNGATED"),
        ("an app module that redirects socket connect and keeps the original",
         [("app/store/planted.py", _CONNECT_REDIRECTED)], clean, True, "AUTH_DISPATCH_SITE_UNGATED"),
        ("a module named dispatch whose object() takes subprocess.run", [(t, _DISPATCH_DOT_OBJECT)], clean, True,
         "AUTH_DISPATCH_SITE_UNGATED"),
        ("a patch.object that is not unittest.mock's", [(t, _OTHER_PATCH_OBJECT)], clean, True,
         "AUTH_DISPATCH_SITE_UNGATED"),
        ("a setattr method on a receiver that is not monkeypatch", [(t, _HOOKS_SETATTR)], clean, True,
         "AUTH_DISPATCH_SITE_UNGATED"),
        ("a kept original called in place after a self-assignment", [(t, _KEPT_AND_CALLED)], clean, True,
         "AUTH_DISPATCH_SITE_UNGATED"),
    ]


#: Cases whose expected code brings a second one with it, and why.
CASCADES = {
    "an allowlist entry with no reason": "AUTH_DISPATCH_SITE_UNGATED",
    "an allowlist entry whose reason is a token": "AUTH_DISPATCH_SITE_UNGATED",
    "an entry with an undeclared key": "AUTH_DISPATCH_SITE_UNGATED",
}


def dispatch_self_test(quiet: bool = False) -> tuple[int, int]:
    """(cases, failures). Each case asserted by its own code, and by that code alone."""
    failures = 0
    cases = _dispatch_cases()
    for desc, sources, allow, stamped, expected in cases:
        try:
            sites, unread = scan_sources(sources)
            findings, cert = check_dispatch(sites, allow, allow is not None, stamped)
            fired = {f.code for f in unread + findings + cert}
            want = ({expected} if expected else set()) | ({CASCADES[desc]} if desc in CASCADES else set())
            ok = fired == want
            note = "" if ok else f", fired {sorted(fired)}"
            if ok and desc in CASCADES:
                note = f", cascading to {CASCADES[desc]}: an unusable entry exempts nothing"
        except Exception as exc:  # a crash is a failure of the case, never a pass
            ok, note = False, f", crashed ({exc!r})"
        failures += 0 if ok else 1
        mark = ("refused" if expected else "clean  ") if ok else "WRONG  "
        print(f"  {mark}  {'dispatch: ' + desc:62} expected {expected or 'no refusal'}{note}")
    return len(cases), failures


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


def _telemetry(outcome: str, findings: list[Finding], gate: str = GATE) -> None:
    if gate_log is None:
        return
    try:
        # One run record, then one detail record per finding. HY-1 says one line
        # per gate run, and one line per finding inflates both the run count and
        # the refusal rate HY-2 adjudicates against. The `where` is a path with
        # an optional line, never the string that matched.
        gate_log.record_run(gate, outcome, count=len(findings))
        for f in findings:
            gate_log.record_finding(gate, code=f.code, where=_telemetry_where(f.where))
    except Exception:
        pass


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description="Subject authorization gate: the Step 8 half of the D5 mechanism."
    )
    ap.add_argument(
        "--fixtures",
        action="store_true",
        help="Grade conformance/gate/*.jsonl against the compiled policy, the schema's "
        "required fields, closed property set and subject_class enum, the rank 3 mirror "
        "and the pin of record. This is also what a bare invocation runs.",
    )
    ap.add_argument(
        "--dispatch-paths",
        action="store_true",
        help="SS-6. Every dispatch site under runner/, connectors/ and app/ is behind "
        "runner.subject_guard.evaluate() or listed in runner/dispatch_allowlist.yaml with a "
        "reason. Refuses while the allowlist is absent or unstamped.",
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

    # One call grades one thing, except the two deferred modes, which combine.
    # Until 2026-10-01 --fixtures --self-test ran the self-test and dropped the
    # fixtures, and a deferred mode beside --fixtures was dropped the same way.
    modes = [m for m in ("fixtures", "self_test", "dispatch_paths", "disjointness") if getattr(args, m)]
    if len(modes) > 1 and set(modes) != {"dispatch_paths", "disjointness"}:
        ap.error(
            "REFUSED AUTH_MODES_COMBINED: "
            + ", ".join("--" + m.replace("_", "-") for m in modes)
            + " grade different things, and a combined call ran one and dropped the rest "
            "until 2026-10-01. moves: run each mode on its own; only --dispatch-paths "
            "--disjointness combine"
        )

    if args.dispatch_paths and not (args.fixtures or args.self_test):
        rc = dispatch_paths(quiet=args.quiet)
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
        # Under its own name since 2026-09-30: logged as `authorization`, the
        # self-test's passes diluted the designed refusal rate of --fixtures.
        _telemetry("pass" if rc == 0 else "refuse", [], gate=f"{GATE}-self-test")
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
            f"directions; {len(dict.fromkeys([str(c) for c in _seq(model, 'policy', 'compiles_criteria')] + list(ITEM_6_RT_CRITERIA)))} criteria "
            "checked against the pin of record"
        )
        stamp_codes = {
            "AUTH_UNRATIFIED_CRITERION_PERMITTED",
            "AUTH_UNRATIFIED_ARTIFACT_PERMITTED",
            "AUTH_STAMP_PREDICATE_ALWAYS_REFUSES",
            "AUTH_PIN_SHAPE_UNREADABLE",
            # A-19 does not run on an empty compiled list, so this one keeps the
            # green line from claiming a check that never executed.
            "AUTH_CRITERION_NOT_COMPILED",
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
            "evaluator lives is VA-U1 and runner/subject_guard.py, drafted at Step 10, is "
            "not graded against this corpus; that a dispatch path reaches the gate at all "
            "(SS-6), which is --dispatch-paths and refuses while "
            "runner/dispatch_allowlist.yaml is absent; disjointness from the credential "
            "pool (SS-20, CR-1), which is "
            "--disjointness and is deferred because the pool lives only in ISOLATED per "
            "EG-4; and whether a purpose sentence names a person, which is a review rule "
            "with no mechanism"
        )

    return 1 if all_findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
