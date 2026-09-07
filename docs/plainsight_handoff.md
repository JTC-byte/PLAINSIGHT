# PLAINSIGHT handoff: current state

Current state only. Rewritten every wave. History lives in
`plainsight_worklog.md` and is never restyled.

Capped at roughly 400 lines. Superseded sections move to the archive on the next
session rather than accumulating here. ZMeta's handoff reached 2,080 lines
carrying eleven superseded state sections, which is the failure mode this cap
exists to prevent.

**Wave:** 0 committed. The first build artifacts are committed too, in
`f4e00e1`, and the closeout commits after it moved records, `AGENTS.md`
rules, fact corrections, and one hygiene check with its self-test. The commit
that carries this file is the one prepared for the first push to the public
repository: it follows a rewrite of the whole history, adds the license and
notice files, and translates every hash in a current-state file. The tree is
clean at that commit.
**Date:** 2026-09-07, the session that landed `595cc06`, the persona
replacement, and then this commit once the operator had created the public
repository at `github.com/JTC-byte/PLAINSIGHT`. The session before, 2026-09-04
into 2026-09-05, landed `89c68a3`, `f907a7a` and `7c0e278`. Every hash in this
file is post-rewrite; section 7 says how to read the ones in the process
records.
**Doctrine:** 58 criteria across four rank-1 files plus advisory HYGIENE.md, all
committed in `1abb354` and `4c5cd25`. **Every conclusion is stamped. Every basis
is unstamped.** A seventh EGRESS criterion, EG-7, is drafted and
unratified in patch 4, with amendments to EG-2, CR-3 and CR-6 beside it.
**Kernel gate:** 6 implemented, 1 stubbed, 5 pending. Green.

**Resume here. Read `_session-artifacts/2026-09-03-plainsight-doctrine-review-2/DECISIONS.md`
first, including its 2026-09-04 and 2026-09-07 amendments.** It is three
remaining patches, four Class F criteria, twenty-one recorded readings across
the two rank-3 artifacts, and four live questions. Nothing else in this file is
blocked on any of them, and the readings are places where an agent had to
choose rather than defects. Patch 1 is applied in `89c68a3`. Measured on
2026-09-07 on a fresh clone of the commit now `7c0e278`: patch 2 applies clean;
patch 3 no longer applies whole, because its second `doctrine/HYGIENE.md` hunk
anchors on a sentence `89c68a3` rewrote, and the tree already carries the
corrected claim that hunk was drafted to add. Patch 3 has thirteen hunks, two
of them in HYGIENE.md: `git apply --exclude=doctrine/HYGIENE.md` lands the
eleven outside that file, the first HYGIENE.md hunk applies alone from
`patch-3b-hygiene-first-hunk-only.patch` beside the patches, so twelve of
thirteen land, and patch 4 then applies on top. That tree passes the same
kernel gate, and `tools/validate_doctrine.py` counts 59 criteria there against
58 here, because patch 4 adds EG-7. The rewrite changed no doctrine blob, and this
commit changes only the commit hashes in six status blocks, so the measurement
holds on the rewritten history.

---

## 0. The five questions, for the commit that carries this file

`AGENTS.md` section 8 sets the handoff standard, inherited from
`ZMeta/zmeta-spec/AGENTS.md`: a completed change leaves the next maintainer
able to answer five questions. This section answers them for the commit that
carries this file. For every earlier commit they are answered in
`CHANGELOG.md`, one entry per commit that changed a governed artifact, and in
the worklog entries dated 2026-09-03 to 2026-09-07. Two facts from those
earlier answers still bind a reader: no doctrine criterion has been amended and
nothing has been stamped since 2026-08-27, `89c68a3` having changed three lines
of fact in `doctrine/DOCTRINE_STATUS.md` and no stamp; and no release baseline
has ever changed, because PSE has no version, no tag, and no published artifact.

### The commit that carries this file, 2026-09-07

**What changed and why.** The operator created a public repository for this
project, so the history had to be publishable before its first push. Three
things in it were not. The two earliest commits carried the example persona's
real name and handles in five files, which `595cc06` had replaced only at the
tip. Every commit carried the operator's personal email address as author and
committer. Four documents carried absolute paths from the operator's machine.
The whole history was therefore rewritten with `git filter-repo` on a fresh
clone, before anything was pushed: the persona values were replaced in every
historical blob by the same map `595cc06` used, the author and committer
address became the GitHub no-reply address, and the machine paths became the
placeholders `<Z-ISR>` and `<wave-0-scratchpad>`. Nine commits in, nine out,
and the rewritten tip differs from the pre-rewrite tip in four files, path
lines only. Every hash changed. The current-state files cite the new hashes as
of this commit; the process records keep the hashes they were written with,
and the `CHANGELOG.md` entry for this commit carries the translation table.
The branch is `main`. `LICENSE` carries the Apache License 2.0 text, `NOTICE`
names the copyright holder and the ZMeta derivation, `.gitattributes`
normalizes line endings, `.gitignore` covers editor and agent residue, the CI
workflow token is read-only, `README.md` states the license and the model by
which the public repository is updated, and `AGENTS.md` section 4 gains one
sentence: the repository's own coordinates are not handles under its rule, so
the D-001 scan is written not to refuse them. The worklog had ten live entries,
so its oldest moved to the archive without edit before this commit's entry was
added.

**Which surfaces moved.** Every commit in the history, through the rewrite.
In this commit: `AGENTS.md` in hash strings and one added sentence in section
4, `CONFORMANCE.md`, `README.md`, six doctrine files and
`tools/validate_hygiene.py` in hash strings only, `.github/workflows/ci.yml`
in its permissions block, `.gitignore`, and the new `LICENSE`, `NOTICE` and
`.gitattributes`, plus `CHANGELOG.md`, this file, the worklog, and the archive.
No criterion, no stamp, no schema, no policy, no connector, no validator logic.
The six doctrine files changed in the hash tokens of their status lines and
nowhere else.

**What validation ran and what passed.** On the rewritten clone: the five
implemented validators, the hygiene self-test, the twelve-case telemetry suite,
`git diff --cached --check`, the hook, and the kernel gate at 6 implemented, 0
failed, 1 stubbed, 5 pending. The rewritten tip was compared to the pre-rewrite
tip blob by blob, and four files differ, in path lines only. Every rewritten
commit was searched for the old persona values, the old address, and the
machine paths, and nothing was found. The hash map was applied to the
current-state files and the worklog entry records the count. A verifier pass
read this commit before it was made; the worklog entry states what it found.

**Whether a release baseline changed.** No release baseline changed. `main`
moved, and this commit is the first prepared for `origin`, the public
repository at `github.com/JTC-byte/PLAINSIGHT`. The push is an
operator-instructed act under `AGENTS.md` section 4, a force push because the
remote holds one commit that is not an ancestor of `main`, and it is recorded
in the worklog entry that follows it.

**What remains open or deferred.** The push itself, and the repository
settings that lock the remote down after it: branch protection on `main`,
Dependabot alerts, and the wiki and projects tabs. The pre-rewrite history
survives as a bundle in `Z-ISR/_session-artifacts/2026-09-07-plainsight-history-rewrite/`,
outside the repository, and whether to keep it is the operator's call. The
voice pass: 50 chunks have drafts and no refuter verdict, nothing is applied,
and whether `docs/PLAINSIGHT-FOUNDATION.md` is in scope is the operator's call,
section 4. Patches 2 through 4 as stated above. Everything in sections 3 and 4.

---

## 1. Where the project is

The doctrine is committed and has now been adversarially reviewed twice. The
first two rank-1 files went through fourteen agents on 2026-08-26; the four newer
files and the five newer criteria went through five lenses and five verifiers on
2026-09-03. Two blockers were confirmed, both the same defect, and both are
drafted as a patch rather than applied. Patch 1, the review's fact
corrections, is applied. Patches 2 through 4 wait on the operator.

Three build steps are committed in `f4e00e1`: Step 5's layer model, which is
the single source the schema and policy are generated from, Step 6's selector
registry, and Step 4's cast draft. The cast is unsealed, so nothing can be
scored and SS-14 item 6 still refuses all collection.

The operator's order of work, stated 2026-09-05, is the documentation pass first
and then Step 7, so that Step 7 does not produce documents that need the same
pass. The persona replacement half of that pass is committed. The voice half is
drafted, harvested to
`Z-ISR/_session-artifacts/2026-09-05-plainsight-voice-pass/`, and applied
nowhere; section 4 states its numbers. Step 7 is unblocked and not started, and
two mapping reports for it sit in the same directory.

The repository is public from its first push. The model, stated by the operator
on 2026-09-07, is one local instance where experiments run and one public
repository that receives `main` at closeouts. Nothing about that model is new
to the repository: case material never enters git under `doctrine/RETENTION.md`
RT-15 and the ignore rules, selectors never enter a tracked file under
`AGENTS.md` section 4, and the values that were in the history are now removed
from every commit, so the history is publishable and the local instance holds
its private material on the filesystem rather than in git. The commit-time scan
that would enforce RT-15 is the D-001 stub and checks nothing until Step 8.

Nothing has touched a platform. No account exists. No connector exists.

## 2. What exists

| Path | State |
|---|---|
| `LICENSE`, `NOTICE` | Committed in the commit that carries this file. Apache License 2.0, and the notice naming the copyright holder and the ZMeta derivation without a compatibility claim. |
| `.gitattributes` | Committed in the commit that carries this file. LF in the index and on every checkout. |
| `CLAUDE.md` | Committed. Advisory. R6 amended 2026-08-27. |
| `AGENTS.md` | Committed. Section 5 carries the gate commands and the PyYAML dependency, both from `f4e00e1`. Section 8, the handoff standard and the closeout rule, landed in `98f3433`, which also added the section 6 rule that every matrix row moves the changelog and both process records. Section 4 states, as of the commit that carries this file, that the repository's own coordinates are not handles under its rule. |
| `CHANGELOG.md` | **Committed in `98f3433`**, backfilled across the first three commits. From the next change onward an entry rides in the commit it describes and cites no hash. `d803213` has no entry of its own, by that rule. Every entry below the 2026-09-07 rewrite entry cites pre-rewrite hashes; that entry translates them. |
| `doctrine/DOCTRINE_STATUS.md` | The pin of record. 58 conclusions stamped, 0 bases. |
| `doctrine/SUBJECT_SELECTION.md` | SS-1 to SS-21. Reviewed twice. Two confirmed blockers, drafted as patch 2, not applied. Patch 1 applied 2026-09-04. |
| `doctrine/RETENTION.md` | RT-1 to RT-19. Reviewed twice. |
| `doctrine/EGRESS.md` | EG-1 to EG-6. Reviewed 2026-09-03. One real gap, drafted as EG-7. |
| `doctrine/CREDENTIAL_LIFECYCLE.md` | CR-1 to CR-8. Reviewed 2026-09-03. |
| `doctrine/HYGIENE.md` | HY-1 to HY-4. Reviewed 2026-09-03. Three claims about the recorder were false and the recorder was fixed. |
| `doctrine/RETENTION_LEDGER.md` | **Missing.** Required at v0.1. Shape in RT-10. |
| `doctrine/DISCLOSURE.md` | **Missing, owed.** Trigger fired when RT-18 created a second egress path. |
| `CONFORMANCE.md` | **Committed in `f4e00e1`.** The not-ZMeta claim, the four licensing conditions with three of four honestly marked absent, the five-rung ladder with four rungs it marks as unable to run, and what the kernel gate does not cover. Its section 3 and 4 counts were reconciled against the aggregator on 2026-09-04, having been written inside `f4e00e1` before the ontology entry flipped in that same commit. |
| `spec/layer-model.yaml` | **Committed in `f4e00e1`, and reviewed.** 2,280 lines. Nine event types, 37 subtypes, 57 violation codes, 16 fixtures mapped. Eleven readings await confirmation. 31 review findings, three of them blockers: 29 repaired and two recorded as readings. |
| `synthetic/CAST.md` | **Committed in `f4e00e1`.** DRAFT, UNRATIFIED. Three personas, four confuser pairs. Six decisions for the operator in its section 9. |
| `synthetic/GROUND_TRUTH.yaml` | **Committed in `f4e00e1`, UNSEALED.** Placeholders only. |
| `ontology/selectors.yaml` | **Committed in `f4e00e1`.** 19 selectors, 5 of them proposed and unstamped. Ten readings await confirmation. Relationship selectors refused, with the reason recorded. |
| `schema/`, `policy/`, `conformance/` | Empty. Steps 7 through 9. |
| `tools/validate_doctrine.py` | Committed. Docstring corrected to cover all nine codes. |
| `tools/validate_hygiene.py` | Committed. Caller split for the telemetry fix. Gained the handoff tense check, `HYGIENE_HANDOFF_PRE_COMMIT_TENSE`, and a `--self-test` on 2026-09-04. |
| `tools/validate_conformance.py` | Committed. `KERNEL_GATE` carries twelve entries: six implemented, one stub, five pending. |
| `tools/validate_layer_model.py` | **Committed in `f4e00e1`, and hardened after review.** 33 checks, 60 self-test breaks, all refused, 48 by the expected code alone. |
| `tools/validate_ontology.py` | **Committed in `f4e00e1`.** 16 self-test breaks, all refused. The corpus-coverage mode waits on a corpus. |
| `tools/validate_cast.py` | **Committed in `f4e00e1`.** 6 self-test breaks, all refused. Plus `--placeholder-scan`. |
| `tools/validate_retention.py` | Stub. Exits 0, checks nothing. D-001. |
| `tools/gate_log.py` | Committed, then corrected in three places the review found. |
| `tools/tests/test_gate_log.py` | **Committed in `f4e00e1`.** The first test in the repository. 12 tests, 7 deliberate breaks all refused. One fixture string became fictional in `595cc06`. |
| `Makefile`, `ci.yml`, `.githooks/pre-commit` | Committed. The layer-model, ontology and cast gates, the PyYAML install and `fetch-depth: 0` landed in `f4e00e1`. The workflow token is read-only as of the commit that carries this file. The hook runs six commands, one of them the D-001 stub that checks nothing; `make preflight` runs those six plus the telemetry test. Both files' comments state that difference. Whether the hook should run the test too is a mechanism choice the operator has not made. |
| `connectors/`, `runner/`, `app/` | Empty. Later steps. |

## 3. What blocks

**Nothing blocks a build.** The two blockers block a *schema*, which is Step 8,
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

- **Hashes in the process records refer to the pre-rewrite history.** The
  worklog, its archive, and every `CHANGELOG.md` entry below the 2026-09-07
  rewrite entry cite the hashes they were written with, because a process
  record is never restyled. The 2026-09-07 rewrite entry in `CHANGELOG.md` carries the table
  that translates each of the nine. Every other tracked file cites post-rewrite
  hashes as of the commit that carries this file.
- **The voice pass is drafted and applied nowhere.** The 2026-09-05 workflow cut
  sixteen files into 58 chunks and ran a lens and a refute-by-default verifier
  per chunk. 57 lenses returned 814 edits; 6 refuters returned verdicts before
  the session limit ended the run, and 50 did not. Nine survivor files sit in
  `_voice-pass/`, three of them written by refuters whose verdicts never
  returned. The applier's own checks pass 719 of the 814 drafts and refuse 95,
  69 of those for changing a number. All 556 em dashes in tracked markdown sit
  in the five `docs/` files the hygiene gate exempts. The continuation is a new
  workflow, since resume is same-session only, with the refuters reading the
  harvested drafts. The rewrite changed four of the sixteen files in path
  lines, so the drafts anchored on those lines need re-checking before use.
- **Whether `docs/PLAINSIGHT-FOUNDATION.md` is in scope for the voice pass is
  undecided.** The naming-drift bullet below records that it is voice-exempt as
  a record of intent; the pass drafted 114 edits for it across five chunks,
  because the operator asked for all documentation. One of the two has to give.
- **The patch set has one stale hunk**, stated at the top of this file. The
  `DECISIONS.md` amendments of 2026-09-04 and 2026-09-07 record it.
- **D-001.** `tools/validate_retention.py --repo-scan` is a stub. The pre-commit
  hook calls a mechanism that performs no check. Real implementation is Step 8.
  The 2026-09-03 review confirmed that EG-5 and RT-19 both cite the scan as
  though it were live, and patch 3 corrects them to state the stub in place.
- **The pre-commit hook does not run the telemetry test.** `make preflight` runs
  seven commands and the hook runs six; CI runs the test as a step of its own.
  Both comments now say so. Adding the test to the hook is a mechanism change
  the operator has not made.
- **The tense rule in `AGENTS.md` section 8 is a gate for two words and a
  sentence for the rest.** `tools/validate_hygiene.py` refuses the two
  pre-commit words in this file, and its `--self-test` plants each and proves
  the refusal. That reached thirteen of the fourteen lines that were wrong at
  `d803213`; the fourteenth had neither word, and this check does not reach it.
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
  voice-exempt as a record of intent, and no voice edit has been applied to it.
- **Two review findings were refuted on grounds worth remembering**, so they are
  not re-raised next session. `count_only` is defined nowhere in doctrine, so the
  social web of named nodes is permitted rather than refused, and doctrine
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
| Both doctrine review records | `Z-ISR/_session-artifacts/2026-08-26-plainsight-doctrine-review/` and `.../2026-09-03-plainsight-doctrine-review-2/` | Findings, verdicts, and the four patches plus the split `patch-3b`. The second directory is what the next session reads. |
| The 2026-09-04 verification records | `Z-ISR/_session-artifacts/2026-09-04-plainsight-record-repair/` | The three draft-and-verify passes behind `89c68a3` and `f907a7a` with every finding and verdict, the scripts that applied each edit, the workflow scripts, both commit messages, and a README that indexes them. Its hashes are pre-rewrite. |
| The 2026-09-05 voice pass and Step 7 maps | `Z-ISR/_session-artifacts/2026-09-05-plainsight-voice-pass/` | 57 lens drafts and 6 refuter returns as JSON, the nine survivor files, the workflow script and journal, the applier with its chunk table and mechanical check, and the two Opus mapping reports for Step 7. A README indexes them. |
| The 2026-09-07 history rewrite | `Z-ISR/_session-artifacts/2026-09-07-plainsight-history-rewrite/` | The replacement map and mailmap the rewrite ran with, the commit map from old to new hashes, and a bundle of the complete pre-rewrite history, which is the only copy of it and still carries the values the rewrite removed. |
| Measured Sherlock review | `../Sherlock/sherlock/CAPABILITIES.md` | 64 KB. Source of the 481/429/414 site counts and the 78.8 percent false-positive measurement. |
| Sherlock clone and image | `../Sherlock/sherlock/`, `sherlock-local:0.16.1` | Commit `9100f9d`, 477 MB image, rebuildable. |
| DMZ compartment design | `Z-ISR/_session-artifacts/2026-09-02-dmz-design/` | The operator's wider compartmentalization work. Its dead-drop shape is the contrast EG-3 is measured against. |
| Tool clones and workflow journals | The Wave 0 session scratchpad, `<wave-0-scratchpad>/` in the documents that cite it | All six audited tools plus nine more, with git history, and 202 agent transcripts. In a temp directory any cleanup can remove. Copy before relying on them. |

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
- The operator's order of work is the documentation pass, then Step 7.
- **The public repository is `origin`, `github.com/JTC-byte/PLAINSIGHT`, and
  `main` is the only branch that goes there.** A push is an operator-instructed
  act under `AGENTS.md` §4 and follows a closeout. Experiments run in the local
  instance and reach `main` only through the closeout. Commits carry the GitHub
  no-reply address as author, and the repository-local `user.email` is set to
  that address.
- **Hashes in the worklog, its archive, and every changelog entry below the
  2026-09-07 rewrite entry are pre-rewrite.** That entry translates them. A hash in any other tracked file is post-rewrite.
- The gates need PyYAML. `make preflight` runs the five implemented
  validators, the telemetry test and the D-001 stub. `make test` runs the
  test suite alone. The pre-commit hook runs the same set less the telemetry
  test, which CI runs as a step of its own.
- **The worklog holds ten live entries against its ten-entry cap.** The archive
  at `docs/plainsight_worklog_archive.md` holds the four oldest, and the next
  closeout moves the oldest live entry there before it adds one. The hygiene
  gate refuses an eleventh.
- `_voice-pass/` is ignored by `.gitignore`. Nothing in it is applied, and it is
  deleted once the voice pass lands.
- Write the handoff in the tense of the tree the commit will create, per
  `AGENTS.md` section 8. This file was wrong about that in three commits.
- Two harness facts that cost earlier sessions time: a subagent cannot write a
  report file outside the repository, so a review agent returns findings as text
  and the parent persists them; and a Bash heredoc breaks on an apostrophe, so
  prose files are written with the Write tool.
