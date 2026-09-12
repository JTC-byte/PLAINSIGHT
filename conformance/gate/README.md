# conformance/gate/: the subject gate's decision fixtures

**DRAFT 2026-09-11. Normative. Class F. UNRATIFIED. Drafted by an agent.**

Nothing in this directory certifies anything until the operator stamps it in
`doctrine/DOCTRINE_STATUS.md`. Nineteen of the twenty-one rows in
`conformance/gate/decisions.jsonl` are held on a question rank 1 doctrine does
not answer, and a held row asserts nothing and refuses rather than grading.
Two rows are determinate today. That ratio is the state of the gate, not a
defect in the corpus.

This file is hand-authored prose and no gate reads it. `tools/validate_hygiene.py`
holds `conformance/*.md` to Register 1 and its glob does not reach one level
down, so the voice here was checked by hand against `CLAUDE.md` section 4.

## 1. What the corpus is for

`docs/THE-GAMEPLAN.md` section 2.1 registers `conformance/gate/*.jsonl` as
Normative, Class F, and says what its absence costs: "The gate is
unfalsifiable." `runner/subject_guard.py` is roughly seventy lines of code that
decides who may be collected on. Without a corpus that can make each of its
inputs refuse, a field can be declared, required, printed, and never read. That
already happened once, which is the measurement `SUBJECT_SELECTION.md` SS-5
records: in the precedent guard `scope` was declared on the frozen dataclass,
listed in the required-fields check, printed by `describe()`, and never read by
`check()`, and `expires_on` did not exist at all.

The corpus therefore carries one row per input the gate reads and one row per
refusal doctrine names, each stating the decision it expects.

## 2. What refuses, and where the state lives

The corpus carries no ratification flag of its own. `doctrine/DOCTRINE_STATUS.md`
is the pin of record: "Mechanisms read this file rather than the document they
enforce. An unratified criterion refuses rather than permits."
`doctrine/SUBJECT_SELECTION.md` names the reader and the test in its own header:
`runner/subject_guard.py` reads the pin rather than the prose, a criterion
absent from the stamp table refuses rather than permits, and
`tools/validate_authorization.py --fixtures` carries a test asserting that an
unratified criterion refuses. A per-row `ratified` field would put ratification
state in a data file where no other corpus in this tree carries one.

Three things refuse while this corpus is unstamped.

- **A held row refuses instead of grading.** A row whose `pending` list is not
  empty names the entries that decide what it asserts. The grader reports it
  as held and refuses to certify the gate, which is the check
  `docs/THE-GAMEPLAN.md` Step 8 names in its done-condition.
- **`SS-14` item 6 refuses every dispatch.** No artifact in the
  ratify-before-collection list carries a stamp, so a gate asked today about
  any dispatch refuses at evaluation step 1 under NEVER item 6. Nineteen rows
  are held on GF-U1 for exactly this reason: a row that asserts anything other
  than that refusal has to supply its own stamp state, and whether a fixture
  may supply it is undecided.
- **`policy/subject-authorization.yaml` is unstamped.** Every decision, basis
  and step in this corpus is asserted against that file, and it refuses while
  it is unstamped.

## 3. The row contract

One JSON object per line, twelve keys in this order. `conformance/must-fail.jsonl`
carries six keys in the order `name`, `description`, `expect_code`,
`expect_only`, `context`, `event`, and four of those six appear below with the
same names and the same meanings. A gate row asserts a decision rather than a
violation code, so it needs the inputs the gate reads and the decision it
returns, and that is what the other keys are.

| Key | House analogue | What it carries |
|---|---|---|
| `name` | `name` | The fixture's name. Three of the twenty-one are reserved by `spec/layer-model.yaml`'s fixture map and are not the fixture author's to choose. |
| `description` | `description` | What the row proves, and why it is held where it is held. |
| `criterion` | none | The doctrine criterion that requires the row, which is the hook a both-directions reconcile reads. |
| `expect_decision` | none | An object, described below. |
| `expect_code` | `expect_code` | The violation code the row expects, or `null` where the code vocabulary names none for this refusal. |
| `expect_only` | `expect_only` | `true` on every row. `docs/THE-GAMEPLAN.md` section 2.4 requires it on every D2 and D5 fixture, and every row here is a D5 fixture. |
| `pending` | none | The unratified entries that decide what this row asserts. Empty on a determinate row. |
| `evaluated_at` | none | The instant the gate is asked. |
| `authorization` | none | The synthetic SS-4 authorization record, or `null` where the row's point is that none exists. |
| `given` | none | Every gate input other than the record and the chain. |
| `chain` | `context` | The case's events, in lineage-safe order, which is the pivot chain the gate walks. |
| `dispatch` | `event` | The one proposed act under evaluation. |

`expect_decision` carries eight keys: `value`, `decided_at_step`,
`subject_relation`, `pivot_depth`, `basis_field`, `basis`, `never_item` and
`render`. `value` is the gate value. The other seven are the payload fields a
`COLLECT_EVENT` of that subtype carries, so a row asserts the decision and its
wire record in one place. A field the subtype does not carry is `null`: a
`REFUSED` payload carries no `subject_relation` or `pivot_depth`, and a
`PERMITTED` payload carries no basis.

`given` carries six inputs on every row, with an explicit value on each, so an
input the gate reads cannot be silently absent from a fixture:
`stamp_state`, `manifest`, `baseline`, `preflight`, `environment` and
`collected_content`. `collected_content` names a payload family and carries no
payload string, and `string_in_this_file` is `false` on every row so the claim
is checkable rather than implied.

### 3.1 How a row asserts

- **A permit** sets `expect_decision.value` to `PERMITTED` and `expect_code` to
  `null`. `expect_only` is still `true`, and over an empty code set it reads as
  the assertion that no code fired at all. A permit is not indistinguishable
  from an ungraded row, because `expect_decision.value` is the positive
  assertion and a row the grader never reached cannot produce `PERMITTED`.
- **A refusal** sets the value, the step, the basis field, the basis token, and
  the code where one exists. A gate refusal emits a violation code only where
  the vocabulary names one; the decision is the primary assertion and the code
  is the secondary one.
- **A bypass** sets `expect_decision.value` to `null` and `expect_code` to a
  code. Two rows do this: a run that reached a platform with no gate decision
  above it, and a runner started on LOCAL, which `preflight` refuses before the
  gate sees the dispatch. Naming a gate value on either would claim the gate
  decided something it never saw.
- **A held row** sets both to `null` and lists the entries that hold it. A row
  with both `null` and an empty `pending` list asserts nothing and is refused by
  the grader as malformed.

### 3.2 What the grader has to do

`tools/validate_authorization.py --fixtures` is the reader.
`conformance/must-pass.jsonl` and `conformance/must-fail.jsonl` are graded by
`tools/validate.py --kernel`, and this corpus is outside that gate:
`tools/validate.py` says so in its own header, and the chain rules in
`policy/lineage.yaml` are handed to the Step 8 tool by name. The contract this
corpus is written against has six parts.

1. Refuse the certification while any row's `pending` list is not empty, naming
   each entry and the rows it holds. A green run with a held row in the file
   would be the laundering design gate 6 forbids.
2. Grade every row that is not held, against `policy/subject-authorization.yaml`
   and the evaluator the runner will import at Step 10.
3. Reconcile the corpus against the required-fixture list in section 4 in both
   directions. One direction finds half the drift.
4. Fail when any one of SS-5's three one-field mutations is missing, which SS-5
   requires by name.
5. Refuse a basis outside the closed `refusal_basis` and `extension_basis`
   enums in `spec/layer-model.yaml`, a `decided_at_step` outside its enum, and
   a code outside `policy/violation-codes.yaml`.
6. Refuse a selector-shaped value that is not a bracketed placeholder, on the
   rule `tools/validate_cast.py --placeholder-scan` already applies to
   `synthetic/GROUND_TRUTH.yaml`.

Nothing enforces any of the six today. The tool is the other half of Step 8 and
`tools/validate_conformance.py` carries the `authorization` gate as PENDING
until it lands, which is the honest state rather than a passing stub.

## 4. The fixtures

Twenty-one rows. The register names six cases, and `docs/THE-GAMEPLAN.md`
carries no rank in the authority order, so it cannot shorten a rank-1 list:
doctrine names at least eleven gate fixtures in the same binding language, and
rank 3 reserves three names for this corpus.

| Fixture | Criterion | Decision | Step | Basis | Code | Held on |
|---|---|---|---|---|---|---|
| `seed-permitted` | SS-5, SS-8 | PERMITTED | 6 | none | none | GF-U1, SA-U9 |
| `one-hop-permitted` | SS-16 section 9 | PERMITTED | 6 | none | none | GF-U1, GF-U4, SA-U9 |
| `seed-selectors-mutated` | SS-5, `selectors` | REQUIRES_EXTENSION | 4 | `selector_outside_set` | `SUBJECT_NOT_AUTHORIZED` | GF-U1 |
| `one-hop-pivot-depth-max-mutated` | SS-5, `pivot_depth_max` | REQUIRES_EXTENSION | 4 | `pivot_depth_exceeded` | `SUBJECT_NOT_AUTHORIZED` | GF-U1 |
| `seed-expires-on-mutated` | SS-5, `expires_on` | REFUSED | 2 | `authorization_expired` | `SUBJECT_NOT_AUTHORIZED` | GF-U1, SA-U1 |
| `expiry-boundary-same-day` | SS-5, `expires_on` | held | none | none | none | GF-U1, SA-U1, SA-U3 |
| `depth-at-the-limit` | SS-16 section 9 | held | none | none | none | GF-U1, GF-U4 |
| `never-item-6-artifacts-unstamped` | SS-8, SS-14 item 6 | REFUSED | 1 | `never_item` | none | GF-U1, SA-U15 |
| `criterion-absent-from-stamp-table` | the pin of record, SS-14 item 6 | REFUSED | 1 | `never_item` | none | GF-U1, SA-U15 |
| `run-against-unauthorized-subject` | fixture map, S7-R7 | none | none | none | `SUBJECT_NOT_AUTHORIZED` | determinate |
| `run-without-purpose-binding` | fixture map, SS-4 | REFUSED | held | `purpose_unbound` | `CASE_PURPOSE_UNBOUND` | GF-U1, GF-U3, GF-U5 |
| `bystander-disposition-retain` | SS-10, R8 | REFUSED | 6 | `disposition_out_of_set` | `BYSTANDER_DISPOSITION_OUT_OF_SET` | GF-U1, GF-U5 |
| `bystander-declaration-absent` | SS-8 step 6, SS-10 | REFUSED | 6 | `bystander_undeclared` | none | GF-U1, GF-U5, SA-U9 |
| `incidental-estimate-absent` | SS-12 | REFUSED | held | `incidental_estimate_missing` | `INCIDENTAL_ESTIMATE_MISSING` | GF-U1, GF-U5, SA-U13, SA-U16 |
| `incidental-selector-dispatched-as-seed` | SS-1, SS-10 | REFUSED | held | held | `SUBJECT_NOT_AUTHORIZED` | GF-U1, GF-U2, GF-U5 |
| `injected-instruction-in-collected-bio` | SS-19 | REQUIRES_EXTENSION | 5 | `chain_scope_drift` | `SCOPE_DRIFT_UNADJUDICATED` | GF-U1, GF-U4 |
| `injected-instruction-absent` | SS-19, SS-8 | REQUIRES_EXTENSION | 5 | `chain_scope_drift` | `SCOPE_DRIFT_UNADJUDICATED` | GF-U1, GF-U4 |
| `runner-started-on-local` | EG-6 | none | none | none | `EGRESS_ENVIRONMENT_REFUSED` | determinate |
| `scope-drift-three-hops` | SS-9 | REQUIRES_EXTENSION | 5 | `chain_scope_drift` | `SCOPE_DRIFT_UNADJUDICATED` | GF-U1, GF-U4 |
| `s4-baseline-scorecard-absent` | SS-8 step 3, SS-17 | REFUSED | 3 | `baseline_missing` | none | GF-U1, SA-U1, SA-U2, SA-U6, SA-U7 |
| `s4-baseline-scorecard-present` | SS-8 step 3, SS-17 | PERMITTED | 6 | none | none | GF-U1, SA-U2, SA-U6, SA-U9 |

Three of those names, their codes and their `expect_only` flags are reserved for
this corpus by `spec/layer-model.yaml`'s fixture map:
`run-against-unauthorized-subject`, `scope-drift-three-hops` and
`run-without-purpose-binding`. `tools/validate_layer_model.py` check L-15
refuses a fixture-map entry outside the sixteen named ones, so adding any of
the other eighteen names to the map would drag that tool and
`docs/THE-GAMEPLAN.md` section 2.3 with it. The eighteen are therefore graded
by `tools/validate_authorization.py --fixtures` against section 4 above and are
not in the map.

### 4.1 The matched pairs

`SS-8` states the standard this corpus is judged by inside the criterion that
needs it: a single refusal fixture proves only that something refuses, and the
pair proves the gate is reading the condition and not the weather. Three pairs
are here. The SS-17 baseline pair is the one doctrine names. The SS-19
injection pair is a permitted strengthening that proves the collected field is
not read, and it does not replace the single fixture SS-19 names. The step 6
disposition pair is `bystander-disposition-retain` against `seed-permitted`,
which declares `refuse` and clears step 6, so the pair exists without a second
permitted row.

### 4.2 The three synthetic cases

Three cases, because three records are needed and a record is per case.

- **Case A**, S2, `pivot_depth_max` 2, two authorized handles. It carries the
  seed, the one hop, SS-5's three mutations, both NEVER rows, both reserved
  names other than the drift fixture, both bystander rows, the estimate row,
  the S5 row, the injection pair, and the LOCAL runner.
- **Case B**, S2, `pivot_depth_max` 4, one authorized handle. It carries
  `scope-drift-three-hops` alone. The bound is 4 so that no hop of a three-hop
  chain exceeds it and no hop is refused on its own, which is what makes the
  composition the only thing left to refuse.
- **Case C**, S4, `pivot_depth_max` 0, one authorized handle. It carries the
  SS-17 matched pair as two seeds, so the pair turns on the baseline and on
  nothing else.

## 5. Placeholders, and the cast

`SS-4` puts the authorization record at stratum 1, inside the case boundary,
carrying verbatim subject values and, for S1, a named person, and says it is
never in the repository under any circumstance. The one carve-out is worded as
a restriction: "`conformance/gate/*.jsonl` holds synthetic records only." That
sentence is why an authorization record may sit on a row here at all.

A synthetic value is still a value. `AGENTS.md` section 4 keeps an agent from
writing a selector value, handle, email, phone number or case subject name into
a tracked file, and `tools/build_corpus.py` states the same rule as an absolute
over the other two corpora. Every selector-shaped value in
`decisions.jsonl` is a bracketed placeholder matching `^<[^<>]+>$`. Six of the
eight tokens in the file are copied from `synthetic/GROUND_TRUTH.yaml`, so the
corpus becomes reproducible in one step when the operator fills the cast. The
seventh is `<handle>` inside an `argv_template`, which names a selector type
rather than a selector and is the template the must-pass corpus already
carries. The eighth is named below.

Two consequences worth stating rather than leaving implicit.

- **The drift chain lands on the cast's designed confuser.** Case B walks a
  handle to an email to a phone to `<handle:instagram:P-B-near-identical-to-P-A>`,
  which is the near-miss `synthetic/CAST.md` section 2.2 designed for pair X-1.
  A chain that drifts onto the confuser is the shape this error takes in real
  work, and no real subject can supply it, because nobody designed a real
  person's life to contain a near-miss twin.
- **One placeholder is corpus-local.** The cast designs no bystander, so the S5
  row uses `<platform_uid:incidental-bystander-1>`. It names nobody and belongs
  to no persona, and it is the one token here with no row in the truth file.

The injection row carries no payload string. `synthetic/CAST.md` section 2.3
describes two payload families structurally and records that no payload string
appears in the cast or in the truth file, because the operator composes the bio
text at account creation. The row cites family PF-1 in `given.collected_content`
and asserts the same decision as its pair without it, which is the property
SS-19 states.

## 6. Readings

Interpretive calls this corpus had to make, on the `ontology/selectors.yaml` and
`policy/subject-authorization.yaml` precedent. A reading is not a gap: a gap is
a question doctrine does not answer, and these are questions doctrine answers
indirectly or that rank 3 has already settled. Confirming one is a stamp in
`doctrine/DOCTRINE_STATUS.md` rather than an edit here.

- **GF-R1, the row shape.** One grammar in one file, with the authorization
  record on the row. SS-4's synthetic-records-only sentence licenses the record
  here, and SS-5 requires a fixture identical to a passing one except in
  `selectors` or `expires_on`, neither of which any PSE payload may carry:
  `AUTHORIZATION_RECORD_INLINED` prohibits `selectors` and `evidence_ref` on
  `AUTHORIZE_EVENT` and `COLLECT_EVENT`, and a `COLLECT_EVENT` carries the
  selector's registered type and never its value. A corpus of pure PSE events
  cannot express two of SS-5's three mutations. Splitting the record into a
  sibling file would make a one-field mutation something other than one diff.
  Class B.
- **GF-R2, hand-authored.** `tools/build_corpus.py` declares itself the only
  writer of the other two corpora and excludes this one in its own docstring:
  "less the three the map assigns to `conformance/gate/`, which are Step 8's."
  Hand-writing this file breaks no contract of that tool, and it leaves this
  corpus the only fixture set in the tree a person can edit into passing. The
  reconcile in section 3.2 is what closes that, and it does not exist yet. The
  rows were composed by hand and every identifier is a uuid5 of its label on
  `build_corpus.py`'s rule, so the file is deterministic and no line carries a
  random value. Class B.
- **GF-R3, `expect_only` on every row.** `docs/THE-GAMEPLAN.md` section 2.4
  requires it on every D5 fixture without anticipating a row with no code, and
  reading it over an empty code set as "no code fired" keeps the sentence
  literally true and gives the key a meaning on a permit. Class B.
- **GF-R4, a permit records `decided_at_step` 6.** The step cleared last,
  matching the `collect-permitted` event in the shipped must-pass corpus. A
  distinct value for a permit would widen a closed enum at rank 3. Class B.
- **GF-R5, doctrine's word "refused" is the stopped run.** SS-5 says each
  mutation "must be refused" and SS-19 says the gate "refuses", and two of
  those rows are decided at step 4, which returns `requires_extension`. SS-7
  records that the middle value stops the run, so both non-permitted values
  stop a run and neither assignment widens reach. The step-to-value table is
  fixed by rank 3's closed basis enums, which carry `chain_scope_drift` in
  `extension_basis` and no drift member in `refusal_basis`. Class B.
- **GF-R6, `evaluated_at` on every row.** The corpus is graded at an instant it
  supplies rather than at wall-clock time, so an expiry fixture does not invert
  as the calendar moves and a permit does not go stale. The comparison rule is
  still SA-U3's, and the two rows that sit on its boundary are held. Class B.
- **GF-R7, the numbers in a record are fixture inputs.** `pivot_depth_max` 2
  and 4, the two dates, and the estimate of 0 are inputs to a test rather than
  defaults. `policy/subject-authorization.yaml` records that doctrine sets no
  default depth and that a policy ceiling would bound reach doctrine declined to
  bound, and this corpus creates neither. Class B.
- **GF-R8, a missing stamp row surfaces as NEVER item 6.** SS-8's enforcement
  table assigns item 6 to "the gate, reading `DOCTRINE_STATUS.md`", and it is
  the only stamp-reading mechanism the gate has, so an unratified criterion
  reaches a dispatch through that item. Class B.
- **GF-R9, the record states the nine fields and is addressed from the chain.**
  SS-4's table lists nine fields and none of them is an id, because the table
  says what the record states rather than how it is addressed. This corpus was
  first written with a tenth field, `ref`, on the reading that
  `spec/layer-model.yaml` types `authorization_ref` as the id of this object.
  `schema/subject-authorization.schema.json` landed closed at the nine names
  with `additionalProperties` false, and its entry SAS-U3 records a tenth field
  as an amendment to SS-4's table that only the operator may make. This file
  had already said that the field shapes are the schema's and that the corpus
  follows it once it lands, so the tenth field was removed on 2026-09-11 rather
  than added to the schema. A record is addressed from the chain: the GRANT's
  `authorization_ref` carries the id, and `tools/validate_authorization.py`
  A-10 refuses any record whose key set differs from the schema's in either
  direction. Class B.
- **GF-R10, step 4's two bases.** `selector_outside_set` fires on a dispatch
  with no chain to an authorized selector, which is a seed outside the record's
  set. A pivot inside `pivot_depth_max` satisfies step 4's second disjunct and
  reaches step 5, so the only way a pivot fails step 4 is on depth. SS-8's own
  wording is the source. Class B.

## 7. Unratified

Five questions this corpus does not answer. Each one is a place where writing a
value would decide what the gate returns, how far a chain may walk, or what a
refusal means. None carries a default. A row held on an entry asserts nothing,
and the grader renders the entry's sentence rather than grading the row.

An entry is resolved when `doctrine/DOCTRINE_STATUS.md` carries a dated row
naming its id, authored by the ratifier. A row's `pending` list may also name an
entry in `policy/subject-authorization.yaml`'s `unratified` block, and nine of
those sixteen are named here: SA-U1, SA-U2, SA-U3, SA-U6, SA-U7, SA-U9, SA-U13,
SA-U15 and SA-U16.

### GF-U1. Does a fixture supply the stamp state, or does the gate read the live pin at grade time?

**Class F.** SS-8 says item 6 is the item to build the NEVER fixture on, since
the gate can evaluate it by reading `DOCTRINE_STATUS.md`, and it does not say
whether the fixture supplies that input or inherits it from the tree. The
question reaches nineteen rows rather than one, because NEVER is evaluation
step 1 and no artifact is stamped: a gate asked today about any dispatch
refuses at step 1, so every row that asserts a permit, or a refusal at any
later step, is asserting a value the gate does not return unless the fixture
supplies a stamp state.

Options. A fixture-supplied stamp table in `given`, stable across ratification,
which proves the gate reads a table rather than that it reads the real one.
The live pin, which is self-maintaining and inverts every one of those rows to
permitted on the day the operator stamps the eight artifacts, so the corpus
changes meaning at ratification and that has to be a ratified fact rather than
a surprise. Building the NEVER row on item 1 instead, which SS-8 permits and
which tests a Step 12 manifest check rather than the gate.

The corpus carries one row of each of the first two, so the stamped answer
deletes the other rather than requiring a rewrite.

```
REFUSED PENDING RATIFICATION
  where: conformance/gate/README.md unratified GF-U1
  what:  the corpus was asked to certify a gate decision, and whether a fixture
         may supply the stamp table SS-14 item 6 reads is undecided. Nineteen
         rows assert a value that depends on the answer, and grading them
         against either input would claim the gate was proven against a
         condition nobody chose
  moves: stamp one of the three options in doctrine/DOCTRINE_STATUS.md and
         delete the row the answer retires; or stamp the eight artifacts SS-14
         item 6 lists, which makes the live-pin reading gradable; or certify
         nothing, which is what this refusal is holding
```

### GF-U2. Which refusal basis and which step name a refusal whose chain origin is incidental?

**Class F.** SS-1 and SS-10 both require the fixture and neither names a basis.
Rank 3 states the rule without a token: a chain whose origin resolves to a
`COLLECT_EVENT` with `subject_relation` incidental is refused, and an S5
selector is not a seed for anything. A `REFUSED` payload requires
`refusal_basis`, and the closed enum has no member for an incidental origin.
SS-8's six steps do not place the check either.

Options. Reuse `class_unavailable`, on the reading that S5 is the one class SS-1
marks not authorizable, at the cost of a wire record that cannot distinguish an
S5 origin from an S3 run with no baseline. Add a member such as
`incidental_origin` to `spec/layer-model.yaml` and regenerate, which is an edit
to the gate's own closed vocabulary and is Class F by effect. Assert only the
chain-rule code, which proves the chain rule fired and proves nothing about
what the gate returned.

```
REFUSED PENDING RATIFICATION
  where: conformance/gate/README.md unratified GF-U2
  what:  the gate refused a selector whose chain origin is an incidental
         person, and there is no legal token for that refusal. The row asserts
         the code and leaves the basis and the step empty, because a token
         chosen here would either lose the distinction the wire record exists
         to carry or widen a closed enum
  moves: stamp one of the three options in doctrine/DOCTRINE_STATUS.md; or open
         a new case with that person's own authorization record, which is the
         promotion SS-1 requires and which this refusal is pointing at; or
         certify nothing
```

### GF-U3. At which step is a purpose with no binding decided?

**Class F.** `refusal_basis` carries `purpose_unbound` and SS-8's six-step order
does not place it. `policy/subject-authorization.yaml` compiles the order and
assigns no step to it either. The row is `run-without-purpose-binding`, whose
name and code rank 3 reserves, so the row exists and its step does not.

Options. Step 2, on the reading that a record with no purpose is an incomplete
record, which makes `authorization_incomplete` and `purpose_unbound` two bases
for one step. A step of its own, which widens the closed `decided_at_step` enum
at rank 3. The same question stands for `incidental_estimate_missing`, which
SA-U16 carries, so a single stamped answer can cover both.

```
REFUSED PENDING RATIFICATION
  where: conformance/gate/README.md unratified GF-U3
  what:  a dispatch was refused because the case carries no bound purpose, and
         the refusal has no step to record. SS-8's order is stamped at six
         steps and none of them is this check, so writing a step here would
         state that the gate decided at a point in an order the operator
         stamped, which it did not
  moves: stamp one of the two options in doctrine/DOCTRINE_STATUS.md; or bind a
         purpose to the case at creation, which removes the refusal; or certify
         nothing
```

### GF-U4. What separates a composed chain that has left the authorized set from a permitted pivot outside the record's selectors?

**Class F.** SS-9 states the rule, names the fixture and names the code, and
leaves the predicate open. Every pivot lands on a selector the record does not
name, which is what a pivot is. Section 9 says depth against an authorized
subject is uncapped and that `pivot_depth_max` bounds how far a chain may walk
before it needs a new decision, so a one-hop pivot inside the bound is
permitted. SS-9 says three hops each inside the bound compose into something
nobody authorized. Both descriptions fit a selector that is outside the set and
inside the bound, and the gate cannot ask whose selector it is: SS-1 rules out
inferring a class from a selector value permanently.

Options. Accumulated depth from the seed, which makes drift a correctly
composed depth check and leaves `chain_scope_drift` and `pivot_depth_exceeded`
naming one fact. An unadjudicated composition, reading the code's own name
`SCOPE_DRIFT_UNADJUDICATED`, which refuses every pivot until an analyst acts
and turns the middle value into the ordinary case rather than the exception. A
declared scope on the record beyond its selectors, which adds a field SS-4's
nine-field table does not carry and which SS-4 closes.

The same entry holds the boundary case. Whether a chain at a depth equal to
`pivot_depth_max` is inside the bound or at the limit differs by one hop of
reach, and the shipped must-pass corpus carries a pivot at depth 3 against a
bound of 3 with basis `pivot_depth_exceeded`, which is precedent rather than
doctrine. `depth-at-the-limit` is the row, and it asserts nothing.

```
REFUSED PENDING RATIFICATION
  where: conformance/gate/README.md unratified GF-U4
  what:  the gate was asked whether a composed chain has left the authorized
         set, and no predicate distinguishes that from a pivot the depth bound
         permits. Five rows depend on the answer, including the one-hop permit
         and the drift fixture rank 3 reserves by name, and a predicate written
         here would decide how far a chain may walk without a new decision
  moves: stamp one of the three options in doctrine/DOCTRINE_STATUS.md and land
         it in policy/subject-authorization.yaml gate.evaluation_order step 5;
         or authorize each pivot as its own seed with its own record, which is
         always legal and which SS-16 describes; or certify nothing
```

### GF-U5. Which consequence sentence renders a refusal doctrine supplies no sentence for?

**Class F.** SS-7's table renders `refused` as "REFUSED. This selector is in a
class this case may not collect on. No authorization file unlocks it." SA-U1
holds the four bases a corrected authorization file does unlock. Four more
bases are outside both: `disposition_out_of_set`, `bystander_undeclared`,
`incidental_estimate_missing`, and `purpose_unbound`. None of them is a class
refusal and none of them is unlocked by a new authorization, so SS-7's sentence
is wrong on the first clause and right on the second.

One thing worth recording alongside this. `class_unavailable` is the one basis
SS-7's sentence renders honestly, and it cannot arise at v0.1, because every
class in SS-1's set is available at this version. The sentence doctrine supplies
therefore has no fixture in this corpus, which is why SA-U1 and this entry are
load-bearing rather than cosmetic.

Options. Per-basis consequence strings compiled into
`policy/subject-authorization.yaml`, which amends SS-7's table and needs the
operator. SS-7's literal string on every refusal, which tells an analyst
something untrue about a manifest declaration or a blank estimate. A rendering
in the tool rather than in the policy, which puts governed prose in a Class C
file.

```
REFUSED PENDING RATIFICATION
  where: conformance/gate/README.md unratified GF-U5
  what:  the gate refused a dispatch at step 6 or on the pre-flight record, and
         the only rendering doctrine supplies describes a class refusal no
         corrected file unlocks. A state rendered as the wrong consequence is
         worse than a state rendered as its token, because an operator acts on
         it
  moves: stamp one of the three options in doctrine/DOCTRINE_STATUS.md and land
         the sentences in policy/subject-authorization.yaml gate.values; or
         amend SS-7's table at rank 1 so its refused row covers these bases
         honestly; or certify nothing
```

## 8. What this corpus does not carry

- **A connector manifest fixture.** SS-10 assigns the manifest field's name,
  its encoding and its position to `schema/connector-manifest.schema.json` at
  Step 12, and says the must-fail manifest fixture lands there. `given.manifest`
  here carries the two facts step 6 reads and asserts no manifest shape.
- **A bystander class vocabulary.** The same sentence of SS-10 assigns it to
  Step 12. Minting one here would be an agent doing Step 12's Class F work
  early.
- **An S5 classification on a record.** `subject_relation` is a computed column
  with values seed, pivot and incidental, never an asserted one, and the runner
  computes it from the pivot chain. The S5 row therefore asserts against a
  computed relation, and its record names S2, because SS-4 excludes S5 from the
  field.
- **A per-selector NEVER list.** Section 7 of the doctrine contains no selector
  values and names no file holding any. Both NEVER rows are built on an item.
- **An `expect_render` string on a held refusal.** Seven refusing rows carry no
  sentence, and SA-U1 and GF-U5 are the entries that decide them.
- **A row in `spec/layer-model.yaml`'s fixture map for the other eighteen
  names.** Section 4 above is their register.

## 9. Provenance

Compiled 2026-09-11 by an agent from rank 1 doctrine, against
`policy/subject-authorization.yaml` as written in the same change. Every SS, RT
and EG criterion cited here carries its conclusion stamped 2026-08-27 by the
operator with its basis unstamped, deliberately, which
`doctrine/DOCTRINE_STATUS.md` records as a decision rather than an omission.
The conclusions bind. The reasoning quoted anywhere in this file is basis and
does not.

Two readings recorded in the pin of record as awaiting confirmation touch this
corpus. S7-R7 is why `run-against-unauthorized-subject` expects
`SUBJECT_NOT_AUTHORIZED` rather than the generic `LINEAGE_MISSING`, and S7-R1
decided which optional payload fields a subtype may carry, which is what makes
the optional `COLLECT_EVENT` fields in `expect_decision` legal to assert. Both
are readings awaiting confirmation rather than decisions, and the rows that rest
on them say so.
