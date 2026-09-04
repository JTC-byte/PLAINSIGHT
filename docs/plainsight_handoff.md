# PLAINSIGHT handoff: current state

Current state only. Rewritten every wave. History lives in
`plainsight_worklog.md` and is never restyled.

Capped at roughly 400 lines. Superseded sections move to the archive on the next
session rather than accumulating here. ZMeta's handoff reached 2,080 lines
carrying eleven superseded state sections, which is the failure mode this cap
exists to prevent.

**Wave:** 0 committed, and the first build artifacts exist uncommitted.
**Date:** 2026-09-04, closing out a session that began 2026-09-03. The worklog
entry and the review directory carry 2026-09-03 because that is what was true
when each was written, and a process record is added to rather than restyled.
**Doctrine:** 58 criteria across four rank-1 files plus advisory HYGIENE.md, all
committed in `5d53973` and `a54061b`. **Every conclusion is stamped. Every basis
is unstamped.** A ninth criterion, EG-7, is drafted and unratified in a patch.
**Kernel gate:** 6 implemented, 1 stubbed, 5 pending. Green.

**Resume here. Read `_session-artifacts/2026-09-03-plainsight-doctrine-review-2/DECISIONS.md`
first.** It is four patches, four Class F criteria, twenty-one recorded readings
across the two rank-3 artifacts, and four live questions. Nothing else in this
file is blocked on any of them, and the readings are places where an agent had to
choose rather than defects.

---

## 1. Where the project is

The doctrine is committed and has now been adversarially reviewed twice. The
first two rank-1 files went through fourteen agents on 2026-08-26; the four newer
files and the five newer criteria went through five lenses and five verifiers on
2026-09-03. Two blockers were confirmed, both the same defect, and both are
drafted as a patch rather than applied.

Two build steps landed as untracked files: Step 5's layer model, which is the
single source the schema and policy are generated from, and Step 4's cast draft.
Neither has been committed and the cast is unsealed, so nothing can be scored and
SS-14 item 6 still refuses all collection.

Nothing has touched a platform. No account exists. No connector exists.

## 2. What exists

| Path | State |
|---|---|
| `CLAUDE.md` | Committed. Advisory. R6 amended 2026-08-27. |
| `AGENTS.md` | Committed, plus an uncommitted section 5 edit adding the new gates and the PyYAML dependency. |
| `doctrine/DOCTRINE_STATUS.md` | The pin of record. 58 conclusions stamped, 0 bases. |
| `doctrine/SUBJECT_SELECTION.md` | SS-1 to SS-21. Reviewed twice. Two confirmed blockers, patched not applied. |
| `doctrine/RETENTION.md` | RT-1 to RT-19. Reviewed twice. |
| `doctrine/EGRESS.md` | EG-1 to EG-6. Reviewed 2026-09-03. One real gap, drafted as EG-7. |
| `doctrine/CREDENTIAL_LIFECYCLE.md` | CR-1 to CR-8. Reviewed 2026-09-03. |
| `doctrine/HYGIENE.md` | HY-1 to HY-4. Reviewed 2026-09-03. Three claims about the recorder were false and the recorder was fixed. |
| `doctrine/RETENTION_LEDGER.md` | **Missing.** Required at v0.1. Shape in RT-10. |
| `doctrine/DISCLOSURE.md` | **Missing, owed.** Trigger fired when RT-18 created a second egress path. |
| `CONFORMANCE.md` | **Written, untracked.** The not-ZMeta claim, the four licensing conditions with three of four honestly marked absent, the five-rung ladder with four rungs that cannot run, and what the kernel gate does not cover. |
| `spec/layer-model.yaml` | **Written, untracked, and reviewed.** 2,280 lines. Nine event types, 37 subtypes, 57 violation codes, 16 fixtures mapped. Eleven readings await confirmation. 31 review findings applied, including three blockers. |
| `synthetic/CAST.md` | **Written, untracked.** DRAFT, UNRATIFIED. Three personas, four confuser pairs. Six decisions for the operator in its section 9. |
| `synthetic/GROUND_TRUTH.yaml` | **Written, untracked, UNSEALED.** Placeholders only. |
| `ontology/selectors.yaml` | **Written, untracked.** 19 selectors, 5 of them proposed and unstamped. Ten readings await confirmation. Relationship selectors refused, with the reason recorded. |
| `schema/`, `policy/`, `conformance/` | Empty. Steps 7 through 9. |
| `tools/validate_doctrine.py` | Committed. Docstring corrected to cover all nine codes. |
| `tools/validate_hygiene.py` | Committed. Caller split for the telemetry fix. |
| `tools/validate_conformance.py` | Committed, plus three new `KERNEL_GATE` entries. |
| `tools/validate_layer_model.py` | **Written, untracked, and hardened after review.** 33 checks, 60 self-test breaks, all refused, 48 by the expected code alone. |
| `tools/validate_ontology.py` | **Written, untracked.** 16 self-test breaks, all refused. The corpus-coverage mode waits on a corpus. |
| `tools/validate_cast.py` | **Written, untracked.** 6 self-test breaks, all refused. Plus `--placeholder-scan`. |
| `tools/validate_retention.py` | Stub. Exits 0, checks nothing. D-001. |
| `tools/gate_log.py` | Committed, then corrected in three places the review found. |
| `tools/tests/test_gate_log.py` | **Written, untracked.** The first test in the repository. 12 tests, 7 deliberate breaks all refused. |
| `Makefile`, `ci.yml`, `.githooks/pre-commit` | Committed, plus uncommitted edits wiring the three new gates, the PyYAML install, and `fetch-depth: 0`. |
| `connectors/`, `runner/`, `app/` | Empty. Later steps. |

## 3. What blocks

**Nothing blocks a build.** The two blockers block a *schema*, which is Step 7,
and they are one patch away.

Three constraints on ordering rather than blocks:

- **EG-2 and RT-4 both have no later date.** The case store lives in ISOLATED and
  every blob is encrypted with a per-case key from the first write. The DMZ
  environment therefore has to exist before the first blob does, and the
  operator has said that environment is being stood up.
- **The cast is unsealed, so nothing is scoreable.** SS-14 item 6 refuses all
  collection until the cast is sealed and stamped, and sealing needs the accounts,
  which need the SIMs.
- **Live execution stays an operator act.** `AGENTS.md` §4's first Execution Limit
  is unchanged. An agent builds and analyzes; the operator runs anything that
  reaches a platform.

## 4. Known gaps

- **D-001.** `tools/validate_retention.py --repo-scan` is a stub. The pre-commit
  hook calls a mechanism that performs no check. Real implementation is Step 8.
  The 2026-09-03 review confirmed that EG-5 and RT-19 both cite the scan as
  though it were live, and patch 3 corrects them to state the stub in place.
- **Every basis stamp is unstamped**, all 58 criteria and the 16 D and R decision
  rows. This is now the oldest open item in the program. The conclusions bind;
  the reasoning in `docs/PLAINSIGHT-FOUNDATION.md` §3 and `docs/THE-GAMEPLAN.md`
  §3.0 has never been read.
- **`PLAINSIGHT-FOUNDATION.md` line 4 still reads DRAFT** and says nothing is
  operator-ratified, while D1 through D5 are. Clearing it is the operator's act.
- **AR-1 awaits a decision**: whether publishing a roster of accounts carrying
  injection payloads is a public good or an accusation this system cannot verify.
- **The ratification ladder terminates in one person.** The operator is the
  ratifier, the maintainer and the analyst, so every operator-approval gate is
  the operator approving their own request. Stated rather than left implicit,
  because a control whose bypass is undocumented gets bypassed silently.
- **The compatibility-claim check reads one file, not the tree.**
  `tools/validate_layer_model.py` refuses the forbidden claim inside
  `spec/layer-model.yaml` only. `docs/THE-GAMEPLAN.md` Step 9 states the
  whole-tree version as a done-condition of `tools/validate_divergence_register.py`,
  which does not exist. A tree scan needs two deliberate exemptions, since the
  gameplan's own done-condition and the validator's source both quote the
  string, so it is a small design question rather than a one-line addition.
- **A naming drift between two rank-7 drafts.** `docs/PLAINSIGHT-FOUNDATION.md`
  §4.4 names rung 3 of the adapter ladder `check_ontology`; the register in
  `docs/THE-GAMEPLAN.md` §2.1 registers it as `tools/validate_ontology.py`. The
  register is the authority and Step 6 uses that name. FOUNDATION is
  voice-exempt as a record of intent and was left unedited.
- **Two review findings were refuted on grounds worth remembering**, so they are
  not re-raised next session. `count_only` is defined nowhere in doctrine, so the
  social web of named nodes is permitted rather than refused. And doctrine
  deliberately has no sensitivity axis for a category of data: RT-1 puts a
  criminal record on the same case clock as a follower count, which is a live
  question and not a defect.

## 5. The two 2026-09-03 reviews, and why their numbers differ

**The doctrine review.** Five lenses raised 92 findings; five verifiers
instructed to refute confirmed 21, downgraded 35 and refuted 27. Deduplicated: 2
blockers, 6 majors. The refutation rate is the useful number, and its cause is
consistent: a reviewer reads one criterion, does not find the answer, and does
not check the sibling file that has it. SS-16 alone answered three findings that
declared doctrine silent.

**The layer-model review.** 31 findings, 3 blockers, 18 majors, all applied and
none refuted. The difference is method rather than luck: that reviewer mutated
the model and called the validator, so it reported what a check does rather than
what it appears to do, and a measured result has nothing to refute. Read that
way, its eighteen majors are one finding said eighteen times, that a check which
cannot refuse is not a check, which is RT-9's rule turned on the tooling.

The lesson for the next review is to make the reviewer run the mechanism wherever
one exists, and to reserve the refute-by-default verifier pass for findings about
prose, where a reader can be wrong about what a document says.

Full record, including every verdict with its quoted evidence, in
`Z-ISR/_session-artifacts/2026-09-03-plainsight-doctrine-review-2/`.

## 6. Session context that lives outside this repository

**Durable, on disk:**

| What | Where | Why it matters |
|---|---|---|
| Both doctrine review records | `Z-ISR/_session-artifacts/2026-08-26-plainsight-doctrine-review/` and `.../2026-09-03-plainsight-doctrine-review-2/` | Findings, verdicts, and the four patches. The second directory is what the next session reads. |
| Measured Sherlock review | `../Sherlock/sherlock/CAPABILITIES.md` | 64 KB. Source of the 481/429/414 site counts and the 78.8 percent false-positive measurement. |
| Sherlock clone and image | `../Sherlock/sherlock/`, `sherlock-local:0.16.1` | Commit `9100f9d`, 477 MB image, rebuildable. |
| DMZ compartment design | `Z-ISR/_session-artifacts/2026-09-02-dmz-design/` | The operator's wider compartmentalization work. Its dead-drop shape is the contrast EG-3 is measured against. |
| Tool clones and workflow journals | The Wave 0 session scratchpad under `<wave-0-scratchpad>/` | All six audited tools plus nine more, with git history, and 202 agent transcripts. In a temp directory any cleanup can remove. Copy before relying on them. |

**Published briefings, on claude.ai:** the Sherlock Field Manual, PLAINSIGHT
audit and system design, and PLAINSIGHT Foundation. Renderings of the three
`docs/` files. Nothing is in them that is not in the repository.

**One measurement worth re-running rather than trusting.** Tool liveness in
`docs/OSINT-COP-tool-review.md` reflects 2026-08-26 and rots fast. Four of the
six tools were already dead at audit time. Re-probe before relying on any verdict
there.

## 7. Standing rules a new session should not have to rediscover

- No agent executes a connector against a live platform. `AGENTS.md` §4.
- No agent lands a Class F change. Drafting is expected, and four drafts are
  waiting.
- No selector belonging to a natural person enters a tracked file, including
  worklog entries and commit messages. A synthetic value is still a value, which
  is why the cast is placeholders and `--placeholder-scan` refuses a filled one.
- Unratified binds nothing, and mechanisms read `DOCTRINE_STATUS.md` rather than
  the document they enforce.
- Repo prose follows Register 1 in `CLAUDE.md` §4. Published briefings follow
  `docs/DOCUMENT_STANDARD.md`. Doctrine never becomes a briefing.
- The gates need PyYAML. `make preflight` runs the five that exist. `make test`
  runs the one test suite.
- Two harness facts that cost this session time: a subagent cannot write a report
  file outside the repository, so a review agent returns findings as text and the
  parent persists them; and a Bash heredoc breaks on an apostrophe, so prose
  files are written with the Write tool.
