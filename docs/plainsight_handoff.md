# PLAINSIGHT handoff: current state

Current state only. Rewritten every wave. History lives in
`plainsight_worklog.md` and is never restyled.

Capped at roughly 400 lines. Superseded sections move to the archive on the next
session rather than accumulating here. ZMeta's handoff reached 2,080 lines
carrying eleven superseded state sections, which is the failure mode this cap
exists to prevent.

**Wave:** 0 committed, and Step 7 committed in the commit that carries this
file. The first build artifacts landed in `f4e00e1`; the publication commit
`ac60ac4` rewrote the history and pushed it; `6247953` fixed the hook mode. This
commit lands the 2026-09-03 review's patches 2, 3c and 3b in doctrine, the
schema, the policy pack, the two conformance corpora, the semantics contract,
and the three tools that generate and grade them. The tree is clean at this
commit.
**Date:** 2026-09-08, closing a session that began the same afternoon. The
repository went public during it, and the operator decided three things: the
voice pass is parked, the patches land, and Step 7 is built. Every hash in this
file is post-rewrite; section 7 says how to read the ones in the process
records.
**Doctrine:** 58 criteria across four rank-1 files plus advisory HYGIENE.md,
every conclusion stamped, every basis unstamped. Patches 2, 3c and 3b are in
the tree. Patch 4b, the four Class F items with EG-7, is regenerated against
this tree and waits on the operator.
**Kernel gate:** 7 implemented, 1 stubbed, 4 pending. Green.

**Resume here.** Two files first:
`_session-artifacts/2026-09-03-plainsight-doctrine-review-2/DECISIONS.md`,
whose 2026-09-08 amendment says one patch remains, and
`_session-artifacts/2026-09-08-plainsight-provisioning-plan/PROVISIONING_PLAN.md`,
which is what the operator is buying and standing up in parallel. The next
build step is Step 8, compiling the doctrine to policy, and its first artifact
is `schema/subject-authorization.schema.json` from SS-4's table, which patch 2
made correct. Nothing in Step 8 waits on patch 4b except EG-7's own compiled
form.

---

## 0. The five questions, for the commit that carries this file

`AGENTS.md` section 8 sets the handoff standard, inherited from
`ZMeta/zmeta-spec/AGENTS.md`: a completed change leaves the next maintainer
able to answer five questions. This section answers them for the commit that
carries this file. For every earlier commit they are answered in
`CHANGELOG.md`, one entry per commit that changed a governed artifact, and in
the worklog. Two facts from those earlier answers still bind a reader: no
doctrine criterion's conclusion has been amended and nothing has been stamped
since 2026-08-27; and no release baseline has ever changed, because PSE has no
tag and no published artifact.

**What changed and why.** Three decisions the operator made on 2026-09-08 after
the repository went public and a first investigation became the goal. Patches
2, 3c and 3b from the 2026-09-03 review land in five doctrine files: patch 2
restores to SS-4's required-field table the seven subject classes R4 decided on
2026-08-26, which is the table Step 8's authorization schema compiles from;
patch 3c is patch 3's twelve sound hunks with one hash translated; patch 3b is
the one sound HYGIENE.md hunk. Step 7 is built: `tools/generate_pse.py` writes
the schema and the four policy files from `spec/layer-model.yaml`,
`tools/build_corpus.py` writes the two corpora, `tools/validate.py` grades them
and refuses drift in any generated file, and `spec/pse-semantics-contract.md`
was written last, UNRATIFIED, with an enforcement label on every rule. The
voice pass is parked because it is not on the path to a first run.

**Which surfaces moved.** Doctrine text in `SUBJECT_SELECTION.md`,
`RETENTION.md`, `EGRESS.md`, `CREDENTIAL_LIFECYCLE.md` and `HYGIENE.md`, none
of it a conclusion; `DOCTRINE_STATUS.md` in its pending and readings tables
only. Schema, policy and conformance, all new. The contract, new. Three tools,
new, plus the `schema` entry in `KERNEL_GATE`, the Makefile, and the pre-commit
hook. `CONFORMANCE.md`, `docs/THE-GAMEPLAN.md`, `CHANGELOG.md`, the worklog,
its archive, and this file. No stamp, no connector, no runtime.

**What validation ran and what passed.** The five validators and their
self-tests, the twelve-case telemetry suite, `tools/validate.py --kernel` at 44
must-pass events clean and 98 must-fail fixtures refused for the expected code
with five self-test breaks caught, `git diff --cached --check`, the hook, and
the kernel gate at 7 implemented, 0 failed, 1 stubbed, 4 pending. The CI run on
`6247953` passed every step, which the previous handoff could not record.

**Whether a release baseline changed.** No. `main` moves.

**What remains open or deferred.** Patch 4b and its four Class F decisions.
Every stamp in section 4. The provisioning the operator is doing in parallel,
section 3. Step 8 onward. The parked voice pass. Everything in section 4.

---

## 1. Where the project is

The doctrine is committed, twice reviewed, and now carries the review's fact
corrections and precision edits. One patch remains, and it is the one an agent
may draft and never decide.

Steps 4, 5, 6 and 7 are committed. The layer model is the single source; the
schema, the four policy files and both corpora are generated from it and
nothing else writes them; a hand edit to any of them refuses at the hook, at
`make preflight`, and at the kernel gate. Rung 2 of the conformance ladder
exists and runs. The contract exists with a version and explains, with a label
on every rule, which surface enforces it and which rules nothing enforces yet.

The operator's goal, stated 2026-09-08, is a first full investigation against
consenting subjects who will confirm the findings. Those subjects are S1
CONSENTING, the best class the program has. The gate between here and that run
is `doctrine/SUBJECT_SELECTION.md` SS-14 item 6: eight artifacts stamped and a
four-check preflight passing in the runner process. Two of the eight now exist
as the contract's sections 5 and 12, unstamped. Steps 8 through 12 build the
rest on LOCAL. The operator provisions the ISOLATED environment, the collection
personas, the SIMs, the mobile egress and the consent records in parallel, per
the provisioning plan outside this repository, and the two tracks rejoin at the
first live run.

The repository is public at `github.com/JTC-byte/PLAINSIGHT` with the lockdown
applied. Nothing has touched a platform. No account exists. No connector
exists.

## 2. What exists

| Path | State |
|---|---|
| `LICENSE`, `NOTICE`, `.gitattributes` | Committed in `ac60ac4`. |
| `CLAUDE.md` | Committed. Advisory. R6 amended 2026-08-27. |
| `AGENTS.md` | Committed. Section 5 names the gate commands; section 8 the handoff standard. Section 5's stated command list predates the seventh hook command and is corrected at the next touch. |
| `CHANGELOG.md` | Committed. One entry per governed commit, newest first. Every entry below the 2026-09-07 rewrite entry cites pre-rewrite hashes; that entry translates them. |
| `doctrine/DOCTRINE_STATUS.md` | The pin of record. 58 conclusions stamped, 0 bases. Two pending rows for the contract's stamp targets and one readings row for S7-R1 to S7-R7, both from the commit that carries this file. |
| `doctrine/SUBJECT_SELECTION.md` | SS-1 to SS-21. Patches 1, 2, 3c in. SS-4's table gives `subject_class` R4's seven classes. |
| `doctrine/RETENTION.md` | RT-1 to RT-19. Patches 1, 2, 3c in. |
| `doctrine/EGRESS.md` | EG-1 to EG-6. Patches 1, 3c in. EG-7 is drafted in patch 4b, not applied. |
| `doctrine/CREDENTIAL_LIFECYCLE.md` | CR-1 to CR-8. Patches 1, 2, 3c in. |
| `doctrine/HYGIENE.md` | HY-1 to HY-4. Patches 1, 3b in. |
| `doctrine/RETENTION_LEDGER.md` | **Missing.** Required at v0.1. Shape in RT-10. Step 11. |
| `doctrine/DISCLOSURE.md` | **Missing, owed.** Trigger fired when RT-18 created a second egress path. |
| `CONFORMANCE.md` | Committed. Rewritten in the commit that carries this file to the state with rung 2 existing, seven implemented gates, eleven divergences, and both runner requirements exercised. |
| `spec/layer-model.yaml` | Committed in `f4e00e1`, reviewed. Unchanged in content since; the generator reads it. Eleven readings await confirmation. |
| `spec/pse-semantics-contract.md` | **Committed in the commit that carries this file. UNRATIFIED.** `pse-event-0.1`, Unlocked. Thirteen sections; every rule labelled schema, policy, runner, gate, review, rendering, or unratified. Sections 5 and 12 are SS-14 item 6 stamp targets. |
| `spec/divergence-register.yaml` | Empty. Step 9. The contract's section 13.2 lists eleven divergences plus three that surfaced in generation. |
| `schema/pse-event-0.1.schema.json` | **Committed in the commit that carries this file. Generated.** Draft 2020-12, one closed payload per subtype, registry keys inlined as the selector enum, confidence refused as `false`. |
| `policy/semantics.yaml`, `policy/lineage.yaml`, `policy/producer-authority.yaml`, `policy/violation-codes.yaml` | **Committed in the commit that carries this file. Generated.** Lineage at subtype granularity with the D5 line bound to `SUBJECT_NOT_AUTHORIZED`; producer authority composed per type and subtype under `effective`; 57 codes each naming its emitter. |
| `conformance/must-pass.jsonl`, `conformance/must-fail.jsonl` | **Committed in the commit that carries this file. Generated.** 44 events in one synthetic case covering all 37 subtypes; 98 fixtures, one break each, 52 of 57 codes covered and the five uncovered named with their reason. No value appears in either. |
| `conformance/gate/`, `conformance/retention/`, `conformance/connector-harness/` | Empty. Steps 8 and 12. |
| `ontology/selectors.yaml` | Committed in `f4e00e1`. 19 selectors, 5 proposed and unstamped. Ten readings await confirmation. |
| `synthetic/CAST.md`, `synthetic/GROUND_TRUTH.yaml` | Committed in `f4e00e1`. DRAFT, UNSEALED, placeholders only. Six decisions for the operator in CAST.md section 9. |
| `tools/generate_pse.py` | **Committed in the commit that carries this file.** The only writer of the five generated artifacts. `--check` refuses drift. Seven readings recorded. |
| `tools/build_corpus.py` | **Committed in the commit that carries this file.** The only writer of the two corpora. `--check` refuses drift. Prints the codes with no fixture on every build. |
| `tools/validate.py` | **Committed in the commit that carries this file.** Rung 2. `--kernel` runs both drift checks, grades both corpora with `expect_only` and no short-circuit, and runs its self-test. |
| `tools/validate_doctrine.py`, `validate_hygiene.py`, `validate_layer_model.py`, `validate_ontology.py`, `validate_cast.py`, `gate_log.py`, `tests/test_gate_log.py` | Committed earlier, unchanged. Hygiene now governs 20 files. |
| `tools/validate_conformance.py` | Committed. `KERNEL_GATE` carries twelve entries: seven implemented, one stub, four pending, as of the commit that carries this file. |
| `tools/validate_retention.py` | Stub. Exits 0, checks nothing. D-001. Step 8. |
| `Makefile`, `ci.yml`, `.githooks/pre-commit` | Committed. The Makefile gains `generate` and `validate-schema` and `preflight` runs eight commands; the hook runs seven, adding `tools/validate.py --kernel --quiet`; CI runs the kernel gate, which now includes it. |
| `connectors/`, `runner/`, `app/` | Empty. Steps 10 to 13. |

## 3. What blocks

**Nothing blocks Step 8.** Its authorization schema compiles from SS-4's table,
which patch 2 corrected. Its retention policy compiles from RETENTION.md, whose
conclusions are stamped. Its gate fixtures are the three the model's map
assigns to `conformance/gate/`, whose shapes the must-fail corpus already
exercises. EG-7's compiled form waits on patch 4b.

**What blocks the first live run is SS-14 item 6**, and it is a list rather
than a step: SUBJECT_SELECTION.md and RETENTION.md per criterion, stamped;
`policy/subject-authorization.yaml` and `schema/subject-authorization.schema.json`;
`policy/retention.yaml`; `ontology/selectors.yaml` with its five proposed rows
stamped; the contract's sections 5 and 12; `synthetic/CAST.md` sealed and
hash-pinned with a confuser pair; `runner/dispatch_allowlist.yaml`; and the
four-check preflight passing in the runner process. The sealed cast is a
precondition for every run, consenting subjects included. The operator has been
told the fork: provision the cast alongside the collection pool, or decide a
Class F amendment to SS-14 item 6. Neither is decided.

**Three constraints on ordering rather than blocks.** EG-2 and RT-4 have no
later date: the ISOLATED environment exists before the first blob. Live
execution stays an operator act under `AGENTS.md` section 4. Accounts age, so
the personas the operator creates now are worth more at the first run than any
created then.

**The operator's parallel track**, from the provisioning plan: a DigitalOcean
account separate from the estate and the DMZ compartment, one host to start,
administered through a separate Cloudflare account's Access tunnel; physical
prepaid SIMs from a retail carrier, one per persona, provenance recorded; mobile
egress per session-bearing persona and no commercial proxy pool; the collection
personas on Instagram, Telegram and Discord; the consent records; a paid search
API only if org-to-person bootstrapping is wanted, which needs EG-7 stamped. A
research pass on the router and carrier choices ran during this session and is
persisted outside the repository once it completes.

## 4. Known gaps

- **Patch 4b is the one remaining Class F draft.** EG-7 third-party host
  declaration, CR-3's environment-variable item, CR-6's clearing act, EG-2's
  vault-key custody sentence. Each lands unratified and refuses until stamped.
  Six hunks; applies to this tree; the clone with it applied counts 59
  criteria.
- **Seven generation readings await confirmation, S7-R1 to S7-R7.** S7-R1 is the
  consequential one: which optional payload fields a subtype may carry, decided
  by a stated rule because the model is silent. Its cost is visible in
  `policy/semantics.yaml` under each type's `allowed`: a probe's six free
  optionals on all three phases, an adjudication's `entity_id` on all nine
  dispositions. The remedy is an optional list per subtype in the model,
  Class B.
- **Two layer-model readings shape the schema and are unstamped.** LM-R1, which
  nine types; LM-R2, that no numeric confidence exists. Reversing LM-R2 is five
  edits in a stated order and the validator refuses any proper subset.
- **Five codes have no fixture, by design.** `SCOPE_DRIFT_UNADJUDICATED` is a
  gate chain rule, Step 8. `EGRESS_STRATUM_REFUSED` fires at the crossing.
  `INCIDENTAL_ESTIMATE_MISSING` and `ADJUDICATION_REASON_MISSING` are runner
  rules. `REASON_NAMES_SUBJECT` is a review rule with no mechanism.
  `tools/build_corpus.py` prints the list on every build.
- **One promised fixture does not exist.** The model's `temporal_never_repaired`
  rule says the corpus carries a fixture for a producer that fills
  `asserted_at` from `observed_at`; the fixture map names none, and L-15 refuses
  a name outside the tool's list, so adding it edits
  `tools/validate_layer_model.py` and `docs/THE-GAMEPLAN.md` section 2.3
  together.
- **`ABSENCE_CLAIMED_WITHOUT_CANARY` fires on every `attempted_and_absent`.** No
  canary proof exists before Step 12, so there is no exemption, and the
  must-pass corpus avoids the value rather than pretending a proof.
- **`tools/validate_ontology.py --corpus` is owed.** Its deferral said until a
  corpus exists; `conformance/must-pass.jsonl` is one. Rung 2 enforces the same
  property meanwhile, because the schema inlines the registry keys.
- **`AGENTS.md` section 5 lists six hook commands and the hook runs seven.** A
  one-paragraph correction at the next touch of that file.
- **The voice pass is parked.** 814 drafts, 6 refuter verdicts, nothing
  applied, harvested in `_session-artifacts/2026-09-05-plainsight-voice-pass/`.
  The 16 drafts on this file are dead, this file having been rewritten three
  times since. Doctrine anchors moved again with patches 2 and 3c, so any
  resumption re-checks anchors first. Not on the path to a first run.
- **The public repository's non-provider secret scanning would not enable** on
  this plan. Branch protection, secret scanning and push protection are on.
  The replaced initial commit is still served by hash until GitHub collects it.
- **D-001.** `tools/validate_retention.py --repo-scan` is a stub. Step 8. The
  corpora carry only bracketed placeholders so the real scan finds nothing to
  refuse there.
- **The cast is unsealed**, so nothing is scoreable and SS-14 item 6 refuses all
  collection. Sealing needs the operator's SIMs and accounts and the six
  decisions in CAST.md section 9.
- **Every basis stamp is unstamped**, the oldest open item in the program.
- **`PLAINSIGHT-FOUNDATION.md` line 4 still reads DRAFT.** The operator's act.
- **AR-1 awaits a decision.**
- **The ratification ladder terminates in one person**, stated so the bypass is
  documented.
- **The compatibility-claim check reads one file, not the tree.** Step 9.
- **Two review findings were refuted on grounds worth remembering**: `count_only`
  is defined nowhere in doctrine, so the social web of named nodes is permitted;
  and doctrine has no per-category clock, which is a live question in
  DECISIONS.md part 6 rather than a defect.

## 5. How Step 7 was verified, and what it did not verify

The generated artifacts are checked three ways. `tools/generate_pse.py --check`
and `tools/build_corpus.py --check` prove the files on disk are what the model
and the fixture tables generate. `tools/validate.py` proves the schema and
policy refuse what the corpus says they refuse, for the stated code and, where
the model requires it, for that code alone. Its self-test removes a denylist
group, grants a connector authority over clusters, drops the D5 required parent,
forgets a selector's GENERATED provenance, and drops the nested-hit code, and
asserts the matching fixture stops failing each time, so the runner is
load-bearing rather than coincident.

What this does not verify. The corpus was authored by the same session that
wrote the generator, and the systematic denylist fixtures are derived from the
model the schema is derived from, so a misreading shared by both would be
self-consistent. The thirteen named fixtures and the code-specific ones are
explicit mutations and do not share that weakness. No second pass has read the
generator against the model; that is the review this step is owed, on the
2026-09-04 method: lenses that run the mechanism and quote the result.

## 6. Session context that lives outside this repository

| What | Where | Why it matters |
|---|---|---|
| Both doctrine review records, the patches, `patch-3c` and `patch-4b` | `Z-ISR/_session-artifacts/2026-08-26-plainsight-doctrine-review/` and `.../2026-09-03-plainsight-doctrine-review-2/` | DECISIONS.md's 2026-09-08 amendment states what landed and what remains. |
| The 2026-09-04 verification records | `Z-ISR/_session-artifacts/2026-09-04-plainsight-record-repair/` | The method every later review copies. Pre-rewrite hashes. |
| The 2026-09-05 voice pass and Step 7 maps | `Z-ISR/_session-artifacts/2026-09-05-plainsight-voice-pass/` | The parked drafts, and the two mapping reports the generator was built from. |
| The 2026-09-07 history rewrite and its verification records | `Z-ISR/_session-artifacts/2026-09-07-plainsight-history-rewrite/` | The pre-rewrite bundle, the only copy of the old history, and under `verification/` the three workflow results, edit lists and commit messages of that session. Carries the removed values; unshared. |
| The provisioning plan | `Z-ISR/_session-artifacts/2026-09-08-plainsight-provisioning-plan/PROVISIONING_PLAN.md` | Track B: what the operator buys and stands up, what the agent builds, and the critical path to a first S1 run. |
| DMZ compartment design | `Z-ISR/_session-artifacts/2026-09-02-dmz-design/` | The compartmentalization invariants the ISOLATED environment inherits. |
| Measured Sherlock review, clone and image | `../Sherlock/sherlock/CAPABILITIES.md`, `../Sherlock/sherlock/`, `sherlock-local:0.16.1` | Sherlock is the one audited tool that works and plugs in behind a wrapper. |
| Tool clones and workflow journals | The Wave 0 session scratchpad | Fifteen clones with history and 202 agent transcripts. Temp; copy before relying on them. |

**One measurement worth re-running rather than trusting.** Tool liveness in
`docs/OSINT-COP-tool-review.md` reflects 2026-08-26. Re-probing is an operator
act.

## 7. Standing rules a new session should not have to rediscover

- No agent executes a connector against a live platform. `AGENTS.md` section 4.
- No agent lands a Class F change. Patch 4b is the draft that is waiting.
- No selector belonging to a natural person enters a tracked file, including the
  corpora, which carry bracketed placeholders only.
- **Never edit a generated file by hand.** `schema/`, `policy/`, and the two
  corpora are written by `tools/generate_pse.py` and `tools/build_corpus.py`
  alone; edit the model or the fixture tables and regenerate. The hook, `make
  preflight` and the kernel gate refuse drift.
- Unratified binds nothing, and mechanisms read `DOCTRINE_STATUS.md` rather than
  the document they enforce. The contract's sections 5 and 12 bind nothing until
  their rows carry a stamp.
- Repo prose follows Register 1 in `CLAUDE.md` section 4; the contract is
  governed prose and the hygiene gate checks it.
- The operator's order of work, decided 2026-09-08: Step 8 onward toward a first
  run; the voice pass is parked.
- **The public repository is `origin`, and `main` is the only branch that goes
  there.** A push is an operator-instructed act and follows a closeout. Commits
  carry the GitHub no-reply address.
- **Hashes in the worklog, its archive, and every changelog entry below the
  2026-09-07 rewrite entry are pre-rewrite.** That entry translates them.
- The gates need PyYAML and jsonschema. `make preflight` runs eight commands; the
  hook runs seven, leaving the telemetry test to CI.
- **The worklog holds ten live entries against its ten-entry cap.** The archive
  holds five. The next closeout moves the oldest live entry there first.
- Write the handoff in the tense of the tree the commit will create, per
  `AGENTS.md` section 8.
- Only CI on Linux checks a file mode. The Edit tool on Windows writes CRLF into
  an existing file; `.gitattributes` normalizes the index, and the working copy
  is normalized before the battery so the hook parses.
- Two harness facts: a subagent cannot write outside the repository, so the
  parent persists its reports; and a Bash heredoc breaks on an apostrophe, so
  prose files are written with the Write tool.
