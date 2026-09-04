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
| Versioning | `spec/pse-semantics-contract.md` | rank 2, Class B | Does not exist. `docs/THE-GAMEPLAN.md` Step 7, unblocked since `d99f213` delivered Steps 5 and 6, and written last of the three so it explains rules that already exist rather than inventing rules nothing enforces. |
| Documentation of the delta | `spec/divergence-register.yaml` | rank 3, Class B | Does not exist. Step 9. `spec/layer-model.yaml`'s `divergences_from_zmeta` block, eight entries, DV-01 through DV-08, is the current input a Step 9 generator will read. It is prose in a Class B file, not yet a governed register with its own validator. |
| Conformance evidence | `conformance/` | rank 3 for the corpora, Class B and F | Nothing under `conformance/` is tracked. The three planned subdirectories, `connector-harness/`, `gate/`, and `retention/`, are empty on the machine that cut the repository and absent from any clone, because git does not record an empty directory. Steps 7, 8, and 9 fill them. |
| Release governance | `AGENTS.md` | rank 4, Class A | Exists, committed. Change classes A through F, the required local workflow, and the documentation matrix are in force today. |

Three of the four conditions do not exist yet. The license is conditional on
all four together, so today none of the four conditions is satisfied as a set,
and no statement stronger than section 1's claim is honest.

## 3. What a connector conformance claim contains

`docs/PLAINSIGHT-FOUNDATION.md` section 4.4 defines the adapter contract as
DECLARE, IMPLEMENT, PROVE, and PROVE is a five-rung ladder, narrowest check
first. A connector conformance claim is the conjunction of all five rungs
passing, never any one of them read alone.

| Rung | Tool | Exists today | Proves | Does not prove |
|---|---|---|---|---|
| 1 | `pytest connectors/<id>` | No. `connectors/` is empty. | The adapter's own `translate_<subject>` functions behave as the author intended, against inputs the author chose. | Anything this repository checks independently. The author wrote the code and the test. |
| 2 | `tools/validate.py --file <events>.jsonl --strict` | No. Depends on `schema/pse-event-0.1.schema.json` and `policy/*.yaml`, both empty, Step 7. | The adapter's sample output is schema-valid and passes every layer denylist, lineage rule, and producer-authority check. | That the selectors used are registered, which is rung 3, or that the sample represents the connector's full output range. |
| 3 | `tools/validate_ontology.py --corpus` | The tool and `ontology/selectors.yaml` both exist since `d99f213`. The `--corpus` mode this rung needs is deferred and says so rather than passing, because no corpus exists for it to read. The default `--registry` mode lints the registry itself and is what the kernel gate runs. | Every `selector_type` the sample emits is a member of the closed vocabulary. | Schema or policy conformance, which is rung 2. Registry self-consistency, which is not a claim about any connector. |
| 4 | `tools/validate_connector_conformance.py --fixtures ...` | No. Depends on `conformance/connector-harness/fixture.schema.json`, empty, Step 12, and on a connector to write fixtures against, which does not exist. | The adapter, called against a pinned cassette set including `event_count: 0`, returns output matching each fixture's pinned expectation for math, presence, absence, and lineage. | Behavior against a live target on the day it actually runs. A cassette is frozen at capture time and a platform can change under it. |
| 5 | `tools/validate_conformance.py --kernel-gate` | Yes. | Nothing an implemented gate would refuse regressed anywhere in the repository. | Anything about this connector specifically. It is a whole-repository regression gate, not a connector claim. |

Rungs 1, 2 and 4 name a directory or a tool that does not exist, and rung 3's
tool exists with the mode this rung needs deferred until a corpus does. No
connector can honestly claim conformance today, because rungs 1, 2 and 4
cannot run and rung 3 checks nothing until the corpus exists. Rung 5 is the
only rung that checks anything today, and it says nothing about a connector
because none exists for it to say anything about.

One naming gap between two rank-7 drafts: `docs/PLAINSIGHT-FOUNDATION.md`
section 4.4 names rung 3 with a `check_ontology` script name, while
`docs/THE-GAMEPLAN.md` section 2.1 registers the same artifact as
`tools/validate_ontology.py`. This file uses the registered name, which is the
one that exists since `d99f213`. Nothing exists under the FOUNDATION name, and
FOUNDATION is voice-exempt as a record of intent, so the discrepancy is
reported here rather than edited there.

## 4. What the kernel gate covers today, and what it does not

`tools/validate_conformance.py --kernel-gate` is the one rung that exists.
Its `KERNEL_GATE` list carries twelve entries. Six are implemented: doctrine,
hygiene, layer-model, ontology, cast, and telemetry. One is a wired stub:
retention-repo-scan, which is D-001, exits 0, and checks nothing, scheduled
for Step 8. Five are pending, and each names the artifact that does not
exist: schema (Step 7), authorization (Step 8), retention-policy (Step 8),
divergence-register (Step 9), and connector-conformance (Step 12).

`validate_conformance.py`'s own docstring states the rule this file repeats: a
check that is not implemented is reported as PENDING and never as a pass,
because the alternative already happened once in this program. The stubbed
retention-repo-scan check is wired into the pre-commit hook and returns 0
while checking nothing, and it stays honest only because it says so on every
run. Counting a stub or a pending entry as green would turn a known gap into a
silent one.

A green kernel-gate run today means six implemented checks passed, one stub
exited 0 while checking nothing, and five checks did not run at all because
the schema, the authorization and retention policy, the divergence register,
and every connector do not exist. That is a regression gate on the
checks that exist. It is not a conformance claim about PSE's semantics, and it
is not a conformance claim about any connector, because none exists.

## 5. Two requirements on the future fixture runner

`docs/THE-GAMEPLAN.md` section 2.4 names two improvements PSE takes over
ZMeta's fixture runner on day one, for whichever tool grades
`conformance/must-fail.jsonl` and `conformance/gate/*.jsonl` against the
violation-code vocabulary, expected to be `tools/validate.py --strict` at
rung 2. Both are requirements on that runner, not yet exercised because the
corpora and the runner both remain to be built.

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
