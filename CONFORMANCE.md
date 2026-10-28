# CONFORMANCE.md: The Negative Claim and the Conformance Ladder

This file is advisory, Class A, and sits at rank 5 in the authority order
(`CLAUDE.md` section 2, `AGENTS.md` section 2), below the schemas, the policy
pack, `spec/layer-model.yaml`, and `spec/divergence-register.yaml` at rank 3,
and above the validators and tests at rank 6. `docs/THE-GAMEPLAN.md` section
2.1 gives it two jobs: state the honest negative claim that PSE is not ZMeta,
and state what a connector conformance claim contains. It states neither more
strongly than the tree currently supports.

## 1. The negative claim

PSE is a private dialect derived from `zmeta-event-1.0`. It is not ZMeta. It
does not claim upstream compatibility, and no artifact in this repository may
be described as ZMeta-conformant. `AGENTS.md` section 1 states this and quotes
the license it operates under, from `ZMeta/zmeta-spec/AGENTS.md`:

> "If you change those surfaces locally, treat the result as a private fork or
> dialect. Do not claim upstream compatibility unless the change has
> versioning, documentation, conformance evidence, and release governance."

`tools/validate_layer_model.py` check L-18 enforces the letter of this inside
`spec/layer-model.yaml`: it refuses if that one file contains the two-word
compatibility claim the license forbids, built there as a concatenation so the
check's own source does not trip it. That check reads one file. Step 9 added
the whole-tree version: `tools/validate_divergence_register.py` refuses the
claim in every tracked file and every untracked file git does not ignore,
without regard to case and whether its hyphen is a hyphen-minus, a hyphen or a
non-breaking hyphen, and assembles the string at run time for the same reason. It passes over one line, the quoted description of
the check in `docs/THE-GAMEPLAN.md` Step 9, which states the rule rather than
making the claim. The register exempts that line by its file and the sha256 of
its text, so an edit to the line, or the claim anywhere else, refuses, and
whether the exemption should stand is reading DR-R2 in
`spec/divergence-register.yaml`, awaiting the operator. This file does not
repeat the claim.

## 2. The four licensing conditions, and their current state

`AGENTS.md` section 1 names where each of the license's four conditions is
discharged. This is the honest state of each, named without hedging where the
artifact does not yet exist.

| Condition | Artifact | Rank, class | Current state |
|---|---|---|---|
| Versioning | `spec/pse-semantics-contract.md` | rank 2, Class B | Exists as of the commit that lands Step 7, carrying `pse-event-0.1`, Unlocked, and UNRATIFIED. Written last of the Step 7 artifacts so it explains rules that already exist rather than inventing rules nothing enforces. Its sections 5 and 12 are two of the stamp targets `doctrine/SUBJECT_SELECTION.md` SS-14 item 6 names, and neither is stamped. |
| Documentation of the delta | `spec/divergence-register.yaml` | rank 3, Class B | Exists as of Step 9, drafted by an agent and not reviewed by the operator. Its entries cover every pointer a JSON-pointer diff of the PSE schema and zmeta-event-1.0 produces, and `tools/validate_divergence_register.py` refuses the register when it and the diff disagree, so it does not rest on the prose in `spec/layer-model.yaml`'s `divergences_from_zmeta` block. It cites all eleven of that block's entries, DV-01 through DV-11, and the three the contract's section 13.2 says surfaced in generation, as G-1 to G-3. The readings it records are questions the contract does not settle, and they await the operator. |
| Conformance evidence | `conformance/` | rank 3 for the corpora, Class B and F | `conformance/must-pass.jsonl` and `conformance/must-fail.jsonl` exist as of the commit that lands Step 7, written by `tools/build_corpus.py` and graded by `tools/validate.py`. Step 8 filled `conformance/gate/` and `conformance/retention/`, and both are drafted UNRATIFIED, so the checks that read them refuse until the operator stamps them. Step 12 put `conformance/connector-harness/fixture.schema.json` and a README in `conformance/connector-harness/`, and then the first connector, `connectors/sherlock/`, with six fixtures on three cassettes hand-built in Sherlock's recorded shape and never captured, and the rung 4 runner, `tools/validate_connector_conformance.py`. No connector claim holds: rung 3 checks nothing, and the live canaries have not been performed. The Sherlock manifest refused at DECLARE on reading SH-R5 until the `platform_from_item` move of 2026-10-28 (MF-R17, amendment 9.14 of `docs/PLAINSIGHT-design.md`), and it passes DECLARE on this tree; the maintainer decides whether that move stands. |
| Release governance | `AGENTS.md` | rank 4, Class A | Exists, committed. Change classes A through F, the required local workflow, and the documentation matrix are in force today. |

The connector half of the conformance evidence exists for one connector, on
hand-built cassettes that were never captured, and that connector's claim
is withheld; the divergence register that discharges another condition exists and
is unreviewed. The license is conditional on all four together, so today
the four conditions are not satisfied as a set, and no statement stronger than
section 1's claim is honest.

## 3. What a connector conformance claim contains

`docs/PLAINSIGHT-FOUNDATION.md` section 4.4 defines the adapter contract as
DECLARE, IMPLEMENT, PROVE, and PROVE is a five-rung ladder, narrowest check
first. A connector conformance claim is the conjunction of all five rungs
passing, never any one of them read alone.

DECLARE is a precondition of the ladder rather than a rung of it. A claim
names a manifest that `tools/validate_manifest.py` passes in full: shape against
`schema/connector-manifest.schema.json`, every selector a key in
`ontology/selectors.yaml`, both canaries with placeholder inputs and a
`canary_subject_class`, one refusal fixture per required input linted against
`conformance/connector-harness/fixture.schema.json`, a bystander declaration
SS-10 accepts, and `interaction_class` while R7 carries its dated row. A manifest
that passes only `--shape` supports no claim, and the tool says so when it runs
in that mode.

| Rung | Tool | Exists today | Proves | Does not prove |
|---|---|---|---|---|
| 1 | `python -m pytest connectors/<id>` | Yes, for one connector as of Step 12: `connectors/sherlock/tests/`, replay only, against cassettes hand-built in a recorded shape. `make prove` runs it, and so does CI's connector adapter tests step. | The adapter's own `translate_<subject>` functions behave as the author intended, against inputs the author chose. | Anything this repository checks independently. The author wrote the code and the test. |
| 2 | `tools/validate.py --file <events>.jsonl --strict` | Yes, as of the commit that lands Step 7. `--kernel` also refuses a generated artifact that differs from what `spec/layer-model.yaml` generates, grades both corpora, and runs the runner's own self-test. | The adapter's sample output is schema-valid and passes every layer denylist, lineage rule, and producer-authority check. | That the sample represents the connector's full output range, or anything about behaviour against a live target. |
| 3 | `tools/validate_ontology.py --corpus` | The tool and `ontology/selectors.yaml` both exist since `f4e00e1`. The `--corpus` mode this rung needs is still deferred, and its trigger has now fired: `conformance/must-pass.jsonl` is a corpus it could read. Until the mode lands, rung 2 enforces the same property, because the generated schema inlines the registry's keys as the enum of every registry-bound field (the contract's S7-R4). The default `--registry` mode lints the registry itself and is what the kernel gate runs. | Every `selector_type` the sample emits is a member of the closed vocabulary. | Schema or policy conformance, which is rung 2. Registry self-consistency, which is not a claim about any connector. |
| 4 | `tools/validate_connector_conformance.py --connector <id>`, or `--all` | Yes, as of Step 12. It runs DECLARE first, then replays each fixture's cassette through the adapter and grades every emitted event with rung 2's `check_event`. It asserts the exact `event_count`, each refusal fixture's code and the input it withholds, the known negative's zero hits in its class, the known positive's hits, and the golden replay, and that `invoke()` refuses without a permit. `connectors/sherlock/` holds 6 of 6 fixtures, all on hand-built cassettes. It refused at DECLARE on reading SH-R5 until the move of 2026-10-28, which the maintainer decides, and it passes DECLARE on this tree, which is not a claim, because rung 3 checks nothing and the live canaries have not run. | The adapter, called against a pinned cassette set including `event_count: 0`, returns output matching each fixture's pinned result: an exact `event_count`, zero included, or a refusal with its declared code. The presence, absence, lineage and `forbidden_paths` expectations `docs/PLAINSIGHT-FOUNDATION.md` section 4.4 names have no key in the fixture schema yet (reading MF-R15), so no runner can prove them until the schema carries them. | Behavior against a live target on the day it actually runs. A cassette is frozen at capture time and a platform can change under it. |
| 5 | `tools/validate_conformance.py --kernel-gate` | Yes. | Nothing an implemented gate would refuse regressed anywhere in the repository. | Anything about this connector specifically. It is a whole-repository regression gate, not a connector claim. |

Rung 3's tool exists with the mode this rung needs still deferred. One
connector exists, `connectors/sherlock/`, and rungs 1, 2 and 4 run for it
against cassettes hand-built in Sherlock's recorded shape and never captured,
so they prove the adapter against shapes its author chose. No connector can
honestly claim conformance today: rung 3 checks nothing, and the live canaries
have not run. The Sherlock manifest passes DECLARE since the `platform_from_item`
move of 2026-10-28, which the maintainer decides, and before that move it
refused there on reading SH-R5. Rung 5 says nothing about a connector by design.

One naming gap between two rank-7 drafts: `docs/PLAINSIGHT-FOUNDATION.md`
section 4.4 names rung 3 with a `check_ontology` script name, while
`docs/THE-GAMEPLAN.md` section 2.1 registers the same artifact as
`tools/validate_ontology.py`. This file uses the registered name, which is the
one that exists since `f4e00e1`. Nothing exists under the FOUNDATION name, and
FOUNDATION is voice-exempt as a record of intent, so the discrepancy is
reported here rather than edited there.

## 4. What the kernel gate covers today, and what it does not

`tools/validate_conformance.py --kernel-gate` is rung 5 of section 3.
Its `KERNEL_GATE` list carries thirty-two entries in four states, and
`python tools/validate_conformance.py --list` prints the live list with the
note each entry carries.

Twenty-four entries are implemented: doctrine, hygiene, layer-model, cast,
telemetry, retention-repo-scan, schema, ontology, divergence-register,
connector-manifest, connector-conformance, subject-guard-tests and app-tests,
plus eleven self-test entries. app-tests joined on 2026-10-28 and runs the
application's pytest suite with its paired negative controls inside it. Six, one each for hygiene,
layer-model, cast, retention, ontology and authorization, joined the list on
2026-09-28; the doctrine self-test and the self-test of `tools/pin_of_record.py`,
the pin-of-record reader the doctrine, authorization and retention gates share,
joined on 2026-10-01; at Step 9 the divergence register's gate and its
self-test replaced the entry that had held the register as pending; and at Step
12 the manifest gate and its self-test joined; and at Step 10
subject-guard-tests joined, which runs `runner/tests/test_subject_guard.py` as a
script on this path and under pytest by hand; and with the first connector,
`connectors/sherlock/`, the connector conformance runner and its self-test
joined. The manifest gate and the conformance runner refused while
`connectors/sherlock/manifest.yaml` refused under `MANIFEST_SELECTOR_PLATFORM`,
which is reading SH-R5 in that connector's README, until the
`platform_from_item` move of 2026-10-28 (MF-R17, amendment 9.14), which the
maintainer kept the same day on his click on the offered action in the
PLAINSIGHT chat; reverting it would return both entries to refusing. The
retention-self-test entry refused with
`RETENTION_POLICY_ENFORCEMENT_MISSTATED` while `policy/retention.yaml` recorded
RT-15's `canary_subject_class` part as absent and the Sherlock manifest
declared it. On the maintainer's instruction of 2026-10-28 that flag reads
present, a one-word edit of that flag, Class B as a statement of enforcement
state by the operator's decision of the same day (his click on the offered
action in the PLAINSIGHT chat), and the self-test's mutation for that
part now flips the flag rather than setting it. The
divergence-register entry reads the upstream schema from the sibling checkout
`../ZMeta/zmeta-spec`, which CI clones at the pinned release, and exits 2 where
that checkout is absent, which the aggregator reports as a failure rather than
a pass. A self-test
breaks its governed artifact in memory and asserts each break is refused, so it
grades the check rather than the artifact. Before 2026-09-28 five of the first
six ran on no automated path. `tools/validate.py` runs its own self-test inside
`--kernel`, so the schema entry already carried it.

Two entries are STUB: `tools/validate_ontology.py --matchers` and `--corpus`.
Both print DEFERRED, check nothing, and exit 0, and nothing called either until
they joined the list on 2026-09-28. The `--corpus` trigger has fired, as rung 3
in section 3 records. Step 8 replaced the D-001 stub with
`tools/validate_retention.py`, so retention-repo-scan left the STUB state
before these two entered it. That check reads every tracked file in the working
tree for a filled selector in its typed form, or written as a type beside a
value in a JSON line, a .json file or a .yaml file, against thirteen shapes
reconciled with `ontology/selectors.yaml` in both directions. Three of RT-15's four
enforcement parts are in place: the AGENTS.md clause, this scan in the hook,
and `canary_subject_class`, required by `schema/connector-manifest.schema.json`
since Step 12 and declared on `connectors/sherlock/manifest.yaml`. The violation
code is not in the vocabulary, and git history cannot be read by a check that
runs at commit time.

Four entries are UNRATIFIED, which is a state Step 8 added to the list. An
UNRATIFIED check is implemented and refuses, because the artifact it grades
carries no dated row in `doctrine/DOCTRINE_STATUS.md`. That is a different thing
from a check that does not exist. The code is written, the aggregator runs it on
every invocation, and the aggregator asserts the refusal, so an exit 0 from one
of these four is refused as a gate-list inconsistency rather than counted as a
pass. The four are authorization, authorization-dispatch-paths, retention-policy,
and retention-shred-roundtrip. Each one clears when the operator stamps the
artifact it reads, and not before. authorization-dispatch-paths joined at Step
10 and refuses because `runner/dispatch_allowlist.yaml`, item 8 of SS-14 item 6,
does not exist, so the bypass check has nothing to compare against; the
allowlist is Class F and its draft waits outside the tree for the operator.
Reading VA-R6 in `tools/validate_authorization.py`, of 2026-10-28, reads a
patch target, an attribute assigned over and a patch's kept original as no
site, in a test module under `tests/` only. It narrows what the bypass check
reports; the session applied it as a Class B precision rule of the scanner,
and the operator decided it Class B on 2026-10-28, on his click on the offered
action in the PLAINSIGHT chat, so it stands and the allowlist draft keeps its
four sites.

Two entries are pending, and each names what does not exist:
authorization-disjointness, which needs a credential pool that no inventory
artifact describes; and retention-finding, which is Step 11 and reads a case
store that does not exist.

`validate_conformance.py`'s own docstring states the rule this file repeats: a
check that is not implemented is reported as PENDING and never as a pass,
because the alternative already happened once in this program. The Wave 0
retention stub was wired into the pre-commit hook and returned 0 while checking
nothing, and it stayed honest only because it said so on every run. Counting a
stub, a pending entry, or an unratified refusal as green would turn a known gap
into a silent one.

No implemented entry is red on this working tree, and `--kernel-gate` exits 0.
From Step 12 until 2026-10-28 three were: connector-manifest and
connector-conformance, which refused on reading SH-R5, and retention-self-test,
which refused on the `canary_subject_class` flag above. The two moves that
cleared them were built on 2026-10-28, and each is the maintainer's to keep or
revert. Before Step 12 the gate ran green from the commit that replaced two
values. Until that commit `--kernel-gate` refused on
retention-repo-scan alone, which found two filled
selectors that predate Step 8: one in `docs/PLAINSIGHT-FOUNDATION.md` at line
87, introduced in `1abb354`, a worked example inside a rank-7 record of intent,
and one in `tools/validate_ontology.py` at line 894, introduced in `f4e00e1`,
inside that validator's own negative fixture. Both were true on shape and false
in substance. Adding `repo_scan.document_exemptions` rows for them was proposed
during Step 8 and refuted, because narrowing an RT-15 scan is a reach decision
that belongs to the operator, and that route stays closed. Under the operator's
overnight grant of 2026-09-30 the scan's first legal move was taken instead. The
worked example now reads in the registry's placeholder form, and the fixture
keeps its platform segment a placeholder, so the line no longer carries a
complete typed handle while the ontology check it exercises still fires. Neither
change narrows the scan. Both values remain in git history, which no
commit-time check reaches.

A green kernel-gate run means twenty-four implemented checks passed and four
unratified checks refused in the way the list says they refuse, while two stubs
checked nothing and two checks did not run at all because the credential pool
and the case store do not exist. That is a regression gate on the checks that
exist. It is not a conformance claim about PSE's semantics beyond what the two
corpora exercise, and it is not a conformance claim about any connector, which
only DECLARE and the five rungs of section 3 together make.

## 5. Two requirements on the future fixture runner

`docs/THE-GAMEPLAN.md` section 2.4 names two improvements PSE takes over
ZMeta's fixture runner on day one, for the tool that grades
`conformance/must-fail.jsonl` and `conformance/gate/*.jsonl` against the
violation-code vocabulary. That tool is `tools/validate.py`, and both
requirements are exercised on every kernel-gate run as of the commit that lands
Step 7: the grader refuses a must-fail corpus in which a fixture the model marks
`expect_only` does not set it, and it does not short-circuit on a schema failure
at all, running every check it can and naming the checks it could not reach when
an expected code was never reachable. The gate corpus is Step 8's and is graded
by `tools/validate_authorization.py`, which exists as of Step 8 and refuses,
because `doctrine/DOCTRINE_STATUS.md` carries no dated row for the artifacts it
reads.

- **`expect_only`.** ZMeta's runner passes a must-fail fixture when the
  expected violation code appears anywhere in the output. For the fixtures
  that assert an analyst would believe a false thing rather than see an error,
  that is not enough: a fixture that passes because of incidental schema noise
  alongside the real failure proves nothing about the policy guard it was
  written to test. A PSE fixture may set `expect_only: true`, requiring the
  expected code to be the sole failing code, and every D2 and D5 fixture sets
  it.
- **Short-circuit disclosure.** ZMeta's `validate_bad_events.py` returns early
  on a schema violation, so a fixture that is both schema-invalid and
  policy-invalid never reaches the policy check and reports the schema code
  instead of the one the fixture was written to prove. PSE's runner records
  when it short-circuited and fails any fixture whose expected code belongs to
  a check the run never reached, rather than reporting a pass for the wrong
  reason.

## 6. What would have to be true before an external conformance statement

Nothing in this repository today meets the bar for a conformance statement
made to anyone outside this project. That bar is:

1. `spec/pse-semantics-contract.md` exists and carries a version number, so
   the versioning condition in section 2 above is more than a planned path.
2. `spec/divergence-register.yaml` exists, and `tools/validate_divergence_register.py`
   passes, deriving the required entry list from a diff of the two schemas
   rather than trusting the prose in `spec/layer-model.yaml`'s
   `divergences_from_zmeta` block.
3. The five-rung ladder in section 3 runs end to end for at least one real
   connector, against a real cassette, and rung 4 is implemented rather than
   pending.
4. `conformance/must-pass.jsonl` and `conformance/must-fail.jsonl` are
   populated, green, and graded by a runner that implements both requirements
   in section 5.
5. `tools/validate_conformance.py --kernel-gate` reports zero pending entries.

Until all five hold, the correct external statement is the one in section 1
and nothing stronger: PSE is a private, ZMeta-derived dialect with no
conformance program yet. `docs/THE-GAMEPLAN.md` section 2.2 defers
`spec/conformance-classes.md` and `conformance/claims/`, the documents that
would define conformance classes, profile levels, or a certification process,
until a connector is written by someone who cannot ask the maintainer a
question. This file names that trigger and does not pre-empt it. There is no
conformance class, no profile level, and no certification process at v0.1.
