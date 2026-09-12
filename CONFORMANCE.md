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
check's own source does not trip it. That check reads one file. A whole-tree
version of the same rule is stated as one of `tools/validate_divergence_register.py`'s
done-when conditions in `docs/THE-GAMEPLAN.md` Step 9, and that validator does
not exist yet. A manual search of the tree today finds the forbidden claim
nowhere except as the split string inside `validate_layer_model.py` and as a
quoted description of the check in `docs/THE-GAMEPLAN.md` itself. This file
does not repeat the claim, so that manual finding stays true without leaning on
a whole-tree mechanism that has not been built. Section 6 below returns to
this gap.

## 2. The four licensing conditions, and their current state

`AGENTS.md` section 1 names where each of the license's four conditions is
discharged. This is the honest state of each, named without hedging where the
artifact does not yet exist.

| Condition | Artifact | Rank, class | Current state |
|---|---|---|---|
| Versioning | `spec/pse-semantics-contract.md` | rank 2, Class B | Exists as of the commit that lands Step 7, carrying `pse-event-0.1`, Unlocked, and UNRATIFIED. Written last of the Step 7 artifacts so it explains rules that already exist rather than inventing rules nothing enforces. Its sections 5 and 12 are two of the stamp targets `doctrine/SUBJECT_SELECTION.md` SS-14 item 6 names, and neither is stamped. |
| Documentation of the delta | `spec/divergence-register.yaml` | rank 3, Class B | Does not exist. Step 9. `spec/layer-model.yaml`'s `divergences_from_zmeta` block, eleven entries, DV-01 through DV-11, is the current input a Step 9 generator will read, and the contract's section 13.2 names three more that surfaced in generation. It is prose in a Class B file, not yet a governed register with its own validator. |
| Conformance evidence | `conformance/` | rank 3 for the corpora, Class B and F | `conformance/must-pass.jsonl` and `conformance/must-fail.jsonl` exist as of the commit that lands Step 7, written by `tools/build_corpus.py` and graded by `tools/validate.py`. Step 8 filled `conformance/gate/` and `conformance/retention/`, and both are drafted UNRATIFIED, so the checks that read them refuse until the operator stamps them. `conformance/connector-harness/` is still empty and absent from any clone, because git does not record an empty directory, and Step 12 fills it. |
| Release governance | `AGENTS.md` | rank 4, Class A | Exists, committed. Change classes A through F, the required local workflow, and the documentation matrix are in force today. |

Two of the four conditions, the divergence register and the connector half of
the conformance evidence, do not exist yet. The license is conditional on all
four together, so today the four conditions are not satisfied as a set, and no
statement stronger than section 1's claim is honest.

## 3. What a connector conformance claim contains

`docs/PLAINSIGHT-FOUNDATION.md` section 4.4 defines the adapter contract as
DECLARE, IMPLEMENT, PROVE, and PROVE is a five-rung ladder, narrowest check
first. A connector conformance claim is the conjunction of all five rungs
passing, never any one of them read alone.

| Rung | Tool | Exists today | Proves | Does not prove |
|---|---|---|---|---|
| 1 | `pytest connectors/<id>` | No. `connectors/` is empty. | The adapter's own `translate_<subject>` functions behave as the author intended, against inputs the author chose. | Anything this repository checks independently. The author wrote the code and the test. |
| 2 | `tools/validate.py --file <events>.jsonl --strict` | Yes, as of the commit that lands Step 7. `--kernel` also refuses a generated artifact that differs from what `spec/layer-model.yaml` generates, grades both corpora, and runs the runner's own self-test. | The adapter's sample output is schema-valid and passes every layer denylist, lineage rule, and producer-authority check. | That the sample represents the connector's full output range, or anything about behaviour against a live target. |
| 3 | `tools/validate_ontology.py --corpus` | The tool and `ontology/selectors.yaml` both exist since `f4e00e1`. The `--corpus` mode this rung needs is still deferred, and its trigger has now fired: `conformance/must-pass.jsonl` is a corpus it could read. Until the mode lands, rung 2 enforces the same property, because the generated schema inlines the registry's keys as the enum of every registry-bound field (the contract's S7-R4). The default `--registry` mode lints the registry itself and is what the kernel gate runs. | Every `selector_type` the sample emits is a member of the closed vocabulary. | Schema or policy conformance, which is rung 2. Registry self-consistency, which is not a claim about any connector. |
| 4 | `tools/validate_connector_conformance.py --fixtures ...` | No. Depends on `conformance/connector-harness/fixture.schema.json`, empty, Step 12, and on a connector to write fixtures against, which does not exist. | The adapter, called against a pinned cassette set including `event_count: 0`, returns output matching each fixture's pinned expectation for math, presence, absence, and lineage. | Behavior against a live target on the day it actually runs. A cassette is frozen at capture time and a platform can change under it. |
| 5 | `tools/validate_conformance.py --kernel-gate` | Yes. | Nothing an implemented gate would refuse regressed anywhere in the repository. | Anything about this connector specifically. It is a whole-repository regression gate, not a connector claim. |

Rungs 1 and 4 name a directory or a tool that does not exist, and rung 3's
tool exists with the mode this rung needs still deferred. No connector can
honestly claim conformance today, because rungs 1 and 4 cannot run and no
connector exists for rung 2 to read. Rungs 2 and 5 are the rungs that check
anything today, and each says nothing about a connector because none exists
for it to say anything about.

One naming gap between two rank-7 drafts: `docs/PLAINSIGHT-FOUNDATION.md`
section 4.4 names rung 3 with a `check_ontology` script name, while
`docs/THE-GAMEPLAN.md` section 2.1 registers the same artifact as
`tools/validate_ontology.py`. This file uses the registered name, which is the
one that exists since `f4e00e1`. Nothing exists under the FOUNDATION name, and
FOUNDATION is voice-exempt as a record of intent, so the discrepancy is
reported here rather than edited there.

## 4. What the kernel gate covers today, and what it does not

`tools/validate_conformance.py --kernel-gate` is the one rung that exists.
Its `KERNEL_GATE` list carries sixteen entries in four states, and
`python tools/validate_conformance.py --list` prints the live list with the
note each entry carries.

Eight entries are implemented: doctrine, hygiene, layer-model, cast, telemetry,
retention-repo-scan, schema, and ontology. Step 8 replaced the D-001 stub with
`tools/validate_retention.py`, so retention-repo-scan left the STUB state and no
entry carries STUB today. That check reads every tracked file in the working
tree for a filled selector in its typed form, against thirteen shapes reconciled
with `ontology/selectors.yaml` in both directions, and it enforces three of
RT-15's four parts. The fourth part is out of reach for two separate reasons:
the violation code RT-15 names is not in the wire vocabulary, and git history
cannot be read by a check that runs at commit time.

Three entries are UNRATIFIED, which is a state Step 8 added to the list. An
UNRATIFIED check is implemented and refuses, because the artifact it grades
carries no dated row in `doctrine/DOCTRINE_STATUS.md`. That is a different thing
from a check that does not exist. The code is written, the aggregator runs it on
every invocation, and the aggregator asserts the refusal, so an exit 0 from one
of these three is refused as a gate-list inconsistency rather than counted as a
pass. The three are authorization, retention-policy, and
retention-shred-roundtrip. Each one clears when the operator stamps the artifact
it reads, and not before.

Five entries are pending, and each names what does not exist:
authorization-dispatch-paths, which is Step 10 and whose subject `runner/` is
empty; authorization-disjointness, which needs a credential pool that no
inventory artifact describes; retention-finding, which is Step 11 and reads a
case store that does not exist; divergence-register, which is Step 9; and
connector-conformance, which is Step 12.

`validate_conformance.py`'s own docstring states the rule this file repeats: a
check that is not implemented is reported as PENDING and never as a pass,
because the alternative already happened once in this program. The Wave 0
retention stub was wired into the pre-commit hook and returned 0 while checking
nothing, and it stayed honest only because it said so on every run. Counting a
stub, a pending entry, or an unratified refusal as green would turn a known gap
into a silent one.

The gate does not run green today. `--kernel-gate` refuses on
retention-repo-scan, and on that check alone. The scan finds two filled
selectors that predate Step 8: one in `docs/PLAINSIGHT-FOUNDATION.md` at line
87, introduced in `1abb354`, a worked example inside a rank-7 record of intent,
and one in `tools/validate_ontology.py` at line 894, introduced in `f4e00e1`,
inside that validator's own negative fixture. Both are true on shape and false in
substance. `docs/PLAINSIGHT-design.md` and `docs/THE-GAMEPLAN.md` already carry
`repo_scan.document_exemptions` rows of exactly this kind, and
`docs/PLAINSIGHT-FOUNDATION.md` does not. Adding the two rows was proposed
during Step 8 and refuted, because narrowing an RT-15 scan is a reach decision
that belongs to the operator. That decision is open. The pre-commit hook is
unaffected, because it runs the same mode over the index rather than over the
working tree.

A green kernel-gate run, once that decision is settled, would mean eight
implemented checks passed and three unratified checks refused in the way the
list says they refuse, while five checks did not run at all because the dispatch
paths, the credential pool, the case store, the divergence register, and every
connector do not exist. That is a regression gate on the checks that exist. It
is not a conformance claim about PSE's semantics beyond what the two corpora
exercise, and it is not a conformance claim about any connector, because none
exists.

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
