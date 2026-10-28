# PLAINSIGHT handoff: current state

Current state only. Rewritten every wave. History lives in
`plainsight_worklog.md` and is never restyled.

Capped at roughly 400 lines, superseded detail moved out rather than accumulated.
ZMeta's handoff reached 2,080 lines carrying eleven superseded state sections,
which is the failure mode this cap prevents.

**Wave:** 0 committed, Step 7 committed in `4e6abda`, Step 8 built in
`0e0c840` and still UNRATIFIED, and the build night of 2026-10-28 committed in
`8583132`: Step 9, Step 12's manifest schema and harness, Step 10 drafted, the
first connector on cassettes, and the application's first slice. Section 1
states which done-whens hold and which are unmet by design.
**Date:** 2026-10-28. `main` == `origin/main` == `356c1f7`: the build night's
commit `8583132` (106 files, built under his typed release of 01:47, reviewed
adversarially phase by phase, Class C) merged on his click at 15:00:34, then
its records commit `356c1f7` merged on his click at 16:29:45, each with CI
green on every step; this file's commit is the closeout's Class A commit.
**Doctrine:** 58 criteria across four rank-1 files plus advisory HYGIENE.md,
every conclusion stamped, every basis unstamped. No doctrine file has changed
since `4e6abda`. Patch 4b, the four Class F items with EG-7, no longer applies to
this tree; section 3 says whose decision it is.
**Kernel gate:** 32 entries: 24 implemented and passing, 11 of them self-tests;
4 unratified and refusing as designed; 2 stubbed; 2 pending. `--kernel-gate`
exits 0 on this tree and the pre-commit hook passes. `CONFORMANCE.md` section 4
applies.

**Resume here.** Run `tools/since_last_record.py` from the last record's stamp
over the session's own transcript and read its typed and clicked lines first.
The maintainer's release of 2026-10-28 01:47 stands for building; every commit,
push, merge and Class F decision takes his own typed word in the PLAINSIGHT
chat, per act, and no parent is delegated (his decision of 2026-10-23). The
record of the build night, with every lens finding, refuter verdict, fixer and
verifier report, the DA-R2 allowlist draft and the design brief for the
application, is `Z-ISR/_session-artifacts/2026-10-28-plainsight-build/`. His
queue is `MAINTAINER_QUEUE.md` in
`Z-ISR/_session-artifacts/2026-09-30-plainsight-overnight/`, 28 items, none
answered.

---

## 0. The five questions, for the commit that carries this file

**What changed and why.** The closeout entry in the worklog (the records
commit's merge and CI run, his go word of 17:07:57, the checkpoint) and this
file's header. `356c1f7` recorded the commit, push, merge and CI runs of
`8583132`, which carried five pieces of the gameplan built under his release
of 2026-10-28: the divergence register and its validator (Step 9), the
connector manifest schema, its validator and the harness fixture schema (Step
12 part one), the subject guard and the dispatch-path check (Step 10, drafted),
the Sherlock connector on hand-built cassettes with the rung-4 harness (Step 12
part two), the application's store, ingest, server and social web view (the
first slice of Step 13), and on his click of 12:09 the three pieces that
cleared the two designed refusals and wired the application in (section 3).
Every agent reading awaits him in the artifact that carries it.

**Which surfaces moved.** In this commit: the worklog and its archive, and this
file; the same three in `356c1f7`. In `8583132`: `spec/`, `schema/`, `conformance/connector-harness/`,
`runner/`, `connectors/`, `app/`, eight tools, the Makefile, the hook, CI,
`.gitattributes`, `AGENTS.md` section 5, `CONFORMANCE.md` sections 1 to 4,
`docs/PLAINSIGHT-design.md` section 9 (appended, never edited), one word of
`policy/retention.yaml` on his instruction, `CHANGELOG.md`, the records. No
doctrine, ontology, synthetic, generated or corpus file in either.

**What validation ran and what passed.** On the clean tree at `356c1f7`, the
whole battery of 33 commands, then on this commit's staged tree hygiene and
its self-test, the repo scan, the kernel gate, the hook, both diff checks. On
`8583132`: each phase's battery one command at a time with every negative
control seen failing (the record folder has each), the whole battery on the
staged tree, and three CI runs green on every step.

**Whether a release baseline changed.** No. `main` gained `8583132` by pull
request 35 and `356c1f7` by pull request 36 on 2026-10-28; this commit follows
by the same route under his go word, and PSE still has no tag.

**What remains open or deferred.** Section 3: the classes he confirms (the
emit's platform move, VA-R6, the line 870 edit), DA-R2's stamp, the readings;
the queue.

---

## 1. Where the project is

Steps 4 to 9 are committed. Step 8 and Step 10 are drafted UNRATIFIED and refuse
until stamped. Step 12 has its schema, its harness and one connector that
passes DECLARE and rungs 1, 2 and 4 on hand-built cassettes. The application's first slice runs
on the workstation against the synthetic corpus and nothing else.

**Step 8 does not meet its own done-when, and that is the designed posture.**
`tools/validate_authorization.py --fixtures` and
`tools/validate_retention.py --policy --shred-roundtrip` exit 1 because
`doctrine/DOCTRINE_STATUS.md` carries no dated row for any Step 8 artifact.
A criterion absent from the stamp table refuses, a missing artifact refuses, and
a fully stamped state permits, exercised both ways by `--self-test`. Clearing
the exit code is a stamping act and the operator's.

**Step 9 meets its done-when.** Every pointer present in one schema and absent
in the other, or differing in type, enum or required-ness, has a register entry
or sits under `identical:`; every entry carries its rationale, its
`mechanism_preserved` and a `test_ref` that resolves; the forbidden
compatibility string appears nowhere in the tree (one historical line in
`docs/THE-GAMEPLAN.md` is exempted by its hash, reading DR-R2). The register is
drafted by an agent and unreviewed by him, which `CONFORMANCE.md` section 2
states.

**Step 10 does not meet its done-when, by design.** `evaluate()` refuses every
request at step 1 while the SS-14 item 6 artifacts carry no dated row, and
`--dispatch-paths` refuses because `runner/dispatch_allowlist.yaml` does not
exist; its re-measured draft, DA-R2, waits in the record folder for his stamp
(section 3).

**Step 12 is two thirds built.** The manifest schema and validator, the fixture
schema and the rung-4 harness exist and run. The Sherlock connector replays
hand-built cassettes through rungs 1, 2 and 4 (6 of 6 fixtures held, 30 events
graded, none refused, `invoke()` refusing without a permit and reaching no
process or network call) and passes DECLARE since the `platform_from_item`
move of 2026-10-28 (MF-R17, his to confirm). The live
canaries, which `docs/PLAINSIGHT-design.md` calls Prove It, are an operator act
never performed; no connector is registered for live use.

**The application's first slice** holds the store, the ingest door, rebuild and
replay, the loopback server, the social web view, the Lineage Drawer, PATHS,
DOSSIER and the SSE stream; 195 tests with 91 paired negative controls, in the
kernel gate, `make test` and CI and not in the hook or preflight (APP-R30). Its
design departures from `docs/PLAINSIGHT-design.md` are amendments 9.1 to 9.15 at
the end of that file, each dated, each his to decide.

The operator's goal, stated 2026-09-08, is a first full investigation against
consenting subjects who will confirm the findings, who are S1 CONSENTING. The
gate is SS-14 item 6: eight artifacts stamped and a four-check preflight passing
in the runner process. Every one of the eight now exists in some form; only the
two doctrine files are stamped, and `runner/dispatch_allowlist.yaml` exists only
as DA-R2 outside the tree. `synthetic/CAST.md` is present but unsealed. The
operator provisions ISOLATED, the personas, the SIMs, the egress and the consent
records in parallel.

The repository is public at `github.com/JTC-byte/PLAINSIGHT` with the lockdown
applied. Nothing has touched a platform. No account exists. One connector
exists and has never run.

## 2. What exists

| Path | State |
|---|---|
| `LICENSE`, `NOTICE`, `.gitattributes` | Committed in `ac60ac4`; `.gitattributes` gains one line in `8583132` so connector cassettes keep their recorded bytes. |
| `CLAUDE.md` | Committed. Advisory. R6 amended 2026-08-27. |
| `AGENTS.md` | Committed. Section 5 names the gate commands, the twenty-one hook commands, the twenty-two preflight commands and the paths every validator self-test runs on; section 8 sets the handoff standard and the closeout extraction. |
| `CHANGELOG.md` | Committed. One entry per governed commit, newest first. Entries below the 2026-09-07 rewrite entry cite pre-rewrite hashes; that entry translates them. |
| `doctrine/DOCTRINE_STATUS.md` | The pin of record. 58 conclusions stamped, 0 bases. No row for any Step 8 or Step 10 artifact. The R8 row's Item cell carries an escaped pipe that makes the shared reader skip it (section 4). |
| `doctrine/SUBJECT_SELECTION.md`, `doctrine/RETENTION.md` | SS-1 to SS-21 and RT-1 to RT-19. Patches 1, 2 and 3c in. Sentences at SS-14 items 3, 5 and 6 describe mechanisms as unwritten that now exist (section 4). |
| `doctrine/EGRESS.md`, `doctrine/CREDENTIAL_LIFECYCLE.md`, `doctrine/HYGIENE.md` | EG-1 to EG-6, CR-1 to CR-8, HY-1 to HY-4. EG-7 is drafted in patch 4b, not applied. |
| `doctrine/RETENTION_LEDGER.md`, `doctrine/DISCLOSURE.md` | **Both missing.** The ledger is required at v0.1 (RT-10) and Step 11 delivers it. DISCLOSURE.md is owed since RT-18 created a second egress path. |
| `CONFORMANCE.md` | Committed; sections 1 to 4 rewritten in `8583132` to the tree as it is: the register exists and is unreviewed, one connector passes DECLARE and rungs 1, 2 and 4 with the live canaries unperformed, the gate exits 0. |
| `spec/layer-model.yaml` | Committed in `f4e00e1`. Eleven readings await confirmation. |
| `spec/pse-semantics-contract.md` | Committed in `4e6abda`. **UNRATIFIED.** `pse-event-0.1`, Unlocked. Its sections 5 and 12 are SS-14 item 6 stamp targets. Lines 33 to 34, 65 to 66, 695 to 696 and 732 to 736 now describe the register, the store and the connector in a tense the tree has passed; rank 2, his to amend. |
| `spec/divergence-register.yaml`, `spec/divergence-register.md` | **Committed in `8583132`.** 30 entries (REPLACE 16, NEW 7, DROP 5, INVERT 1, KEEP 1), 8 identical pointers, readings DR-R1 to DR-R4 and entry readings on DR-10, DR-22 and DR-23; the Markdown is generated by `tools/render_divergence_register.py` and checked for drift. |
| `schema/pse-event-0.1.schema.json` | Committed in `4e6abda`. **Generated.** |
| `schema/subject-authorization.schema.json` | Committed in `0e0c840`. Hand-authored, UNRATIFIED. Its `read_by` sentence says `evaluate()` validates the record against it, which the draft guard does not (SG-R13). |
| `schema/connector-manifest.schema.json` | **Committed in `8583132`.** Hand-authored, draft 2020-12, every object closed; five kinds, emits at layer observation only, both canaries required with placeholder inputs, `canary_subject_class` from {synthetic, institutional}, a bystanders block with SS-10's three classes and dispositions {count_only, refuse}, lineage with a stratum and no duration, render strings refusing markup, `interaction_class` closed to R7's two values. Readings MF-R1 to MF-R17 in the validator's docstring; `platform_from_item` on an endpoint-unit connector since 2026-10-28. |
| `policy/semantics.yaml`, `policy/lineage.yaml`, `policy/producer-authority.yaml`, `policy/violation-codes.yaml` | Committed in `4e6abda`. **Generated.** 57 codes. |
| `policy/subject-authorization.yaml`, `policy/retention.yaml` | Committed in `0e0c840`. Hand-authored, UNRATIFIED. `policy/retention.yaml` line 870 reads `present: true` for `canary_subject_class` since 2026-10-28, on his instruction (section 3). `policy/subject-authorization.yaml` lines 121 to 123 and 469 call `--dispatch-paths` deferred. |
| `conformance/must-pass.jsonl`, `conformance/must-fail.jsonl` | Committed in `4e6abda`. **Generated.** 44 events, 98 fixtures. No value appears in either. |
| `conformance/gate/`, `conformance/retention/` | Committed in `0e0c840`. The gate corpus uses the pre-Step-12 bystander shape while the guard reads the Step 12 block (VA-U1 open). |
| `conformance/connector-harness/fixture.schema.json`, `README.md` | **Committed in `8583132`.** The fixture shape: `event_count` and `cassette` on an events fixture, `refusal_code` on a refusal, the fixed adapter-state enum, placeholder-only inputs. |
| `ontology/selectors.yaml` | Committed in `f4e00e1`. 19 selectors, 5 proposed and unstamped. Lines 89 to 90 and 96 to 99 describe the guard and `interaction_class` in a tense the tree has passed. |
| `synthetic/CAST.md`, `synthetic/GROUND_TRUTH.yaml` | Committed in `f4e00e1`. DRAFT, UNSEALED, placeholders only. |
| `runner/subject_guard.py`, `runner/tests/` | **Committed in `8583132`, drafted UNRATIFIED.** `evaluate()` returns a Decision that serializes as a COLLECT_EVENT; the live pin refuses at step 1; 22 tests under pytest and as a script; readings SG-R1 to SG-R18 in the docstring. `runner/dispatch_allowlist.yaml` does not exist. |
| `connectors/sherlock/` | **Committed in `8583132`.** `manifest.yaml`, `adapter.py` (parse, emit, permit-gated invoke), `site_facts.json` (481 sites from `data.json` at 9100f9d), three hand-built cassettes, `fixtures.jsonl`, 51 tests, `README.md` with SH-R1 to SH-R18. Never run. |
| `app/` | **Committed in `8583132`.** 59 files: the store, the ingest door, projections, rebuild and replay, the loopback server, the social web view, the Lineage Drawer, PATHS, DOSSIER, INSPECTOR, SSE, the static front end, `README.md`, and 195 tests with 91 paired controls. Readings APP-R1 to APP-R30. In the kernel gate, `make test` and CI. |
| `tools/generate_pse.py`, `tools/build_corpus.py`, `tools/validate.py`, `tools/validate_layer_model.py`, `tools/validate_doctrine.py`, `tools/validate_hygiene.py`, `tools/validate_ontology.py`, `tools/validate_cast.py`, `tools/since_last_record.py`, `gate_log.py` | Committed earlier, unchanged in `8583132`. |
| `tools/validate_authorization.py` | **Extended in `8583132`** to 5,767 lines: `--dispatch-paths` implemented with 61 planted self-test cases; VA-R5 recorded; VA-R6 applied as the session's reading (section 3); VA-U2 and VA-U3 stay open. |
| `tools/validate_retention.py` | **Touched in :** `MANIFEST_VALIDATOR_REQUIRES_CANARY` is now true, the RT-15 comment says the part measures present, and the self-test's mutation flips the flag. Its self-test passes. |
| `tools/pin_of_record.py` | **Extended in `8583132`** with PIN-R9 (`Pin.decisions`, `decision_stamped`); 35 self-test cases. |
| `tools/validate_manifest.py`, `tools/validate_divergence_register.py`, `tools/render_divergence_register.py`, `tools/validate_connector_conformance.py` | **New in `8583132`.** Self-tests of 103 cases, 39 breaks, a drift check, and 26 plants. |
| `tools/validate_conformance.py` | **Extended in `8583132`.** `KERNEL_GATE` carries thirty-two entries, `app-tests` among them. |
| `Makefile`, `ci.yml`, `.githooks/pre-commit` | **All three touched in `8583132`.** `make preflight` runs twenty-two commands and the hook twenty-one, the eleven self-tests among them. CI runs ten self-tests as named steps before the kernel gate, clones the public `zmeta-spec` at v1.1.27 for the register's diff, installs pytest, runs the guard tests in its Mechanism tests step and the adapter and application tests as named steps. |

## 3. What blocks

Everything in this section is the operator's, and none of it is an agent act.

**Three classes he confirms, each applied on his click of 2026-10-28 as the
session's reading.** First, the emit's platform: a handle's registry form is
`handle:<platform>/<string>` and Sherlock's platform differs per site, so an
emit of a platform-bound key may declare `platform_from_item` on an
endpoint-unit connector, the shape `docs/PLAINSIGHT-design.md` section 6.2
draws (MF-R17, amendment 9.14), with the claim's platform token derived from
the site name alone (SH-R18, amendment 9.15; nine sites give no token and a hit
there is ambiguous with no claim). Second, VA-R6: the dispatch scanner reads a
patch target, a patched attribute's kept original and an attribute assigned
over as no site, in test modules only, with plants proving a patch whose
replacement dispatches is still a site; the session applies it as a Class B
precision rule, the widening lens read it as a Class F exemption, and if he
reads it so the rule comes out and the four `test_http.py` references join the
allowlist draft. Third, the one-word edit at `policy/retention.yaml` line 870,
which he instructed: a statement of enforcement state reaching no subject,
retention period or egress path (Class B by the session's reading), or Class F,
which would need his dated row in the pin.

**DA-R2, the dispatch allowlist.** Class F by `AGENTS.md` section 3. The
re-measured draft is in the record folder beside DA-R1 and its argument, never
in the tree. It covers the four sites `--dispatch-paths` finds outside the gate:
two `subprocess.run` calls in the ingest door (git and the generator check), the
loopback listener's class statement, and the operator-gated docker test. A
stamp is a whole-artifact dated row he authors, and any change to the list
after it is a new Class F act.

**CI on Python 3.12 is unverified until a push.** `app/` compiles under 3.12 and
every standard-library attribute it names resolves there, and the suite could
not run on 3.12 locally (no pytest, PyYAML or jsonschema), so CI-R1 was not
taken. Three test files still mention the design brief outside the repository
(`app/tests/test_corpus.py` line 3, `test_http.py` line 321, `test_store.py`
line 105); the five production docstrings cite the design amendments.

**The 29 decisions in the register** of Step 8, plus U-17, the readings of
Steps 9, 10 and 12 and the application (DR, MF, PIN-R9, SG, VA, DA, SH, CC,
APP), and the design amendments 9.1 to 9.15. Each is recorded where its artifact is
and in the record folder.

**Patch 4b.** Four Class F items: EG-7, CR-3's environment-variable item, CR-6's
clearing act, EG-2's vault-key custody sentence. It no longer applies cleanly;
section 4 says what that costs.

**What blocks the first live run is SS-14 item 6**, a list rather than a step:
the two doctrine files per criterion; `policy/subject-authorization.yaml` and
its schema; `policy/retention.yaml`; `ontology/selectors.yaml` with its five
proposed rows; the contract's sections 5 and 12; `synthetic/CAST.md` sealed and
hash-pinned; `runner/dispatch_allowlist.yaml`; and the four-check preflight in
the runner process. Only the two doctrine files are stamped. The commit that
completes item 6 also edits row 8 of `conformance/gate/decisions.jsonl` and
moves the entries that then permit out of UNRATIFIED. The cast is filled and
sealed in one commit, and an agent filling it would fabricate the ground truth
the seal exists to fix. EG-2 and RT-4 have no later date: the ISOLATED
environment exists before the first blob, and the application's SQLite engine
refuses ISOLATED outright until the Postgres engine exists.

**The operator's parallel track**, from the provisioning plan and the 2026-09-09
checklist: a DigitalOcean account separate from the estate, a mailbox at an
outside provider first, physical prepaid SIMs one per persona, mobile egress per
session-bearing persona, the consent records, and a paid search API only if
org-to-person bootstrapping is wanted (EG-7). Five personas is about 1,720
dollars non-recurring and 205 a month.

## 4. Known gaps

- **Three sentences in rank-1 doctrine and five in rank-3 files describe
  mechanisms as unwritten that now exist:** `doctrine/SUBJECT_SELECTION.md`
  lines 760, 782 to 783 and 813 to 818 (SS-14 items 3, 5 and 6), the two policy
  passages, the schema's `read_by` sentence and two ontology passages named in
  section 2. Each file is his to amend.
- **The R8 row of `doctrine/DOCTRINE_STATUS.md` carries an escaped pipe** in its
  Item cell, so the shared reader splits it into seven cells and skips it, and
  SS-10 never reaches the pin. A one-character doctrine edit, drafted in the
  Phase B record; or a reader change with a PIN reading.
- **No bystander class exists for people inside an area**, so no geo connector
  can pass manifest validation until one is ratified (MF-R2, Class F).
- **`--dispatch-paths` is syntactic and intra-procedural.** It cannot see a call
  through an unresolvable object, a module loaded by path and executed, or code
  generated at run time; the credential-draw patterns name an API the pool does
  not have. VA-U2 and VA-U3 remain open.
- **The RT-15 repo scan does not see a bare username in a CSV** (no selector
  type beside it); the harness placeholder rule is the check that does. Hygiene
  voice-checks its fixed governed set, so the new Markdown under `app/`,
  `connectors/` and `conformance/connector-harness/` is checked for em dashes
  and citations by hand only.
- **The guard's step-3 class clause has one half with no discriminating test**
  (the verifier's note), because no class outside the authorizable set exists in
  the policy.
- **Patch 4b no longer applies to this tree.** `git apply --3way` applies two
  files cleanly and `DOCTRINE_STATUS.md` with one table conflict.
- **`tools/validate_hygiene.py` cannot see a broken sibling citation.** Two
  rank-1 citations name `../ZISR COP/`, now `../zisr-cop/`, kept as dated
  measurements; `README.md` translates it.
- **The doctrine gate does not reconcile a criterion's inline marker with the
  Ratified table**; the gates downstream fail closed on it.
- **Two defects found on 2026-09-11 and not fixed:** `evidence_ref` in the
  authorization schema admits no value (`"not": {}`), and SA-U16's
  `decided_at_step` placement is not wire-legal. Changing either is Class F.
- **Three of RT-15's four enforcement parts are in place.** The one absent is
  the code `FIXTURE_CONTAINS_LIVE_SELECTOR` in the wire vocabulary; git history
  is out of reach of any commit-time check.
- **Seven generation readings (S7-R1 to S7-R7) and two layer-model readings
  (LM-R1, LM-R2) await confirmation.** Reversing LM-R2 is five edits in a stated
  order.
- **Five codes have no fixture, by design**, and the `temporal_never_repaired`
  fixture does not exist. `ABSENCE_CLAIMED_WITHOUT_CANARY` fires on every
  `attempted_and_absent`, which is why the Sherlock adapter emits no claim for a
  non-claimed row.
- **`tools/validate_ontology.py --corpus` and `--matchers` are STUB entries**,
  and every kernel run prints the debt.
- **The application** is checked by static string tests and the served JSON and
  SVG after the fixer, not by a browser pass; the corpus web lays out at about
  2048 by 1143 pixels with edge labels overlapping near the centre; the Postgres
  DDL has never been applied to a server (parity is names only); the
  `rollup_vocab` guard on SQLite is a connection-scoped trigger; the pin reads
  EG-2 and RT-4 as stamped through whole-artifact rows, so only ISOLATED and an
  Encryptor stand between a caller and a blob write on the Postgres engine
  (APP-R13).
- **The voice pass is parked.** Not on the path to a first run.
- **The cast is unsealed**, so nothing is scoreable and SS-14 item 6 refuses all
  collection.
- **Every basis stamp is unstamped**, the oldest open item.

## 5. The reviews

Step 7's generated artifacts are checked three ways (the two `--check` modes and
`tools/validate.py` with its self-test); a second pass read the generator
against the model on 2026-10-02 and returned twenty findings, all open and all
class B or A, queued as plainsight-26 where they touch the contract. Step 8 was
reviewed adversarially on 2026-10-01 and in six later passes; the records are
`REVIEW.md`, `REVIEW2.md` and `STEP7_REVIEW.md` in the overnight folder.
Every implemented gate entry of that time was seen failing under a negative
control on 2026-10-18 (the audit folder).

**The build night of 2026-10-28** reviewed each phase the same way: read-only
lenses, three refuters per finding, one fixer with a control per fix, one
verifier. Step 9: 56 findings, 25 confirmed, 9 defects fixed. The manifest
schema: 65 findings, 16 fixes, 7 skipped as widening. The application: 78
findings, 33 confirmed and fixed. Step 10 and the connector: 91 findings, 57
standing, 38 defects fixed, the last 35 agents run after the usage limit of
06:30 reset. The morning's three builds: 51 findings, 32 standing, 8 fixes
applied. The six new gate entries and the three that changed state have not
been through a negative-control audit of the 2026-10-18 kind; their self-test
controls were seen failing in each run.

## 6. Session context that lives outside this repository

| What | Where | Why it matters |
|---|---|---|
| The build night of 2026-10-28 | `Z-ISR/_session-artifacts/2026-10-28-plainsight-build/` | `README.md` (his release verbatim), one record per phase, the application's design brief, DA-R1 with its argument, the since-last-record extraction, and every lens finding, refuter verdict, fixer and verifier report. |
| The Step 8 decision register | `Z-ISR/_session-artifacts/2026-09-11-plainsight-step8/DECISION_REGISTER.md` | The 51 distinct decisions, 29 of them the operator's. |
| Both doctrine review records and the patches | `Z-ISR/_session-artifacts/2026-08-26-plainsight-doctrine-review/` and `.../2026-09-03-plainsight-doctrine-review-2/` | Patch 4b lives here and no longer applies cleanly. |
| The 2026-09-04 verification records | `Z-ISR/_session-artifacts/2026-09-04-plainsight-record-repair/` | The method every later review copies. |
| The 2026-09-07 history rewrite records | `Z-ISR/_session-artifacts/2026-09-07-plainsight-history-rewrite/` | The pre-rewrite bundle, the only copy of the old history. Unshared. |
| The provisioning plan | `Z-ISR/_session-artifacts/2026-09-08-plainsight-provisioning-plan/PROVISIONING_PLAN.md` | Track B and the critical path to a first S1 run. |
| The overnight records | `Z-ISR/_session-artifacts/2026-09-30-plainsight-overnight/` | The Step 8 and Step 7 reviews, `MAINTAINER_QUEUE.md` with the 28 items, `REPORTS.md`. |
| The cross-session records | The harvest folders of 2026-09-14 through 2026-10-22 and the negative-control audit of 2026-10-18 under `Z-ISR/_session-artifacts/` | The corrected crossings classing, the harvests behind `bf6d5d4` and `37dbcee`, the closeout records of 2026-10-20 and 2026-10-27, and the audit under which all sixteen implemented entries of that time were seen failing. |
| The 2026-09-09 harvest and operator checklist | `Z-ISR/_session-artifacts/2026-09-09-plainsight-harvest-and-operator-checklist/` | The verified shopping list and the identity sequence. |
| DMZ compartment design | `Z-ISR/_session-artifacts/2026-09-02-dmz-design/` | The invariants the ISOLATED environment inherits. |
| Measured Sherlock review, clone and image | `Z-ISR/Sherlock/sherlock/CAPABILITIES.md`, `Z-ISR/Sherlock/sherlock/`, `sherlock-local:0.16.1` | The measured facts the connector's manifest and `site_facts.json` cite, at commit 9100f9d. |

**Worth re-running rather than trusting.** Tool liveness in
`docs/OSINT-COP-tool-review.md` reflects 2026-08-26 and re-probing is an operator
act. The parked voice pass is in `.../2026-09-05-plainsight-voice-pass/`.

## 7. Standing rules a new session should not have to rediscover

- No agent executes a connector against a live platform. `AGENTS.md` section 4.
  `connectors/sherlock/adapter.py` `invoke()` is the one live path, and it runs
  only on a permitted decision from `runner.subject_guard.evaluate()`, which the
  live pin never returns.
- No agent lands a Class F change. Patch 4b and DA-R2 are the drafts waiting.
- No selector belonging to a natural person enters a tracked file; the corpora
  and the cassettes carry bracketed placeholders only.
- **Never edit a generated file by hand.** The schema, the four generated policy
  files and the two corpora are written by `tools/generate_pse.py` and
  `tools/build_corpus.py` alone; `spec/divergence-register.md` is written by
  `tools/render_divergence_register.py` alone.
- Unratified binds nothing, and mechanisms read `DOCTRINE_STATUS.md` through
  `tools/pin_of_record.py` rather than the document they enforce.
- **An UNRATIFIED gate entry asserts a refusal.** Exit 1 is the state the entry
  describes, exit 2 is a tool failure, and exit 0 means the gate list is wrong.
- Repo prose follows Register 1 in `CLAUDE.md` section 4; the contract is
  governed prose and the hygiene gate checks it; a state renders as its
  consequence, never its token, in every refusal string and every view.
- His order of work: 2026-09-08, Step 8 onward toward a first run; 2026-10-16,
  PLAINSIGHT fourth after the TMN, the deploy script and the COP redesign;
  2026-10-28, build everything that needs nothing from him while he provides
  the VMs, domains and SIMs.
- A check is green only when its negative control has been seen to fail, his
  rule of 2026-10-16; a report names the control, or marks the check unproven.
- A parent's relay binds only under a delegation line he typed naming that
  parent; his words typed in the PLAINSIGHT chat outrank a relay that differs.
- His machine-load rule of 2026-09-30: one workstation, one test run at a time,
  three agents across the estate at most.
- **The public repository is `origin`, and work reaches `main` by a pull request
  fast-forwarded after its CI passes**; a push is an operator-instructed act that
  follows a closeout, and every step conclusion of its CI run is read afterwards.
  Commits carry the no-reply address and no agent trailer.
- **Hashes in worklog entries above the 2026-09-07 rewrite entry, in the
  archive, and in every changelog entry below the rewrite entry are
  pre-rewrite.** That entry translates them.
- The gates need PyYAML and jsonschema; the guard tests, the adapter tests and
  the application's tests need pytest, which CI now installs. `make preflight`
  runs twenty-two commands; the hook twenty-one.
- **The worklog is capped at ten live entries and the hygiene gate refuses an
  eleventh.** Each closeout moves the oldest live entry into
  `plainsight_worklog_archive.md` unedited before adding its own.
- Write the handoff in the tense of the tree the commit will create, per
  `AGENTS.md` section 8; stage first and reconcile against the staged list.
- Only CI on Linux checks a file mode. The Edit tool on Windows writes CRLF into
  an existing file; `.gitattributes` normalizes the index, and
  `docs/PLAINSIGHT-design.md` is appended in CRLF to match its working copy.
- Harness facts: a subagent cannot write outside the repository or its own
  scratchpad; a Bash heredoc breaks on an apostrophe; a worktree's
  `core.hooksPath` names the main checkout's `.githooks`; a tree copied under the
  scratchpad passes MAX_PATH; a workflow's task output file is often empty, so
  its `journal.jsonl` is the record to read; a run cut by the usage limit is
  finished from its saved findings rather than by retyping its arguments.
