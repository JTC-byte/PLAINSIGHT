# PLAINSIGHT worklog

Chronological record of what was done, in order, with dates. **Never restyled.**
Rewriting a process record falsifies what was true when it was written.

Live entries are capped at the ten most recent. Older entries move to
`plainsight_worklog_archive.md` without edit.

**This worklog is a PII surface, and it diverges from ZMeta's on one rule.**
ZMeta's worklog may quote anything in its repository. This one may not quote a
case, a selector value, a handle, a subject name, or a finding about a person.
An entry says that case `c7f2` shredded on schedule with 41 blobs verified. It
never says whose case it was. That rule is what keeps good record-keeping habits
from defeating the shred mechanism.

---

## 2026-09-28, every validator self-test joins every automated path, and CI stops skipping the steps after a red one.

**Class:** B and C, and not F. The corrected count in the docstring of
`tools/validate_authorization.py` is B. The aggregator entries, the hook, the
preflight target and the CI workflow are C, by the precedent the 2026-09-11
entry and `4a5c788` set for exactly those files; the operator's brief called the
change B, and the difference moves no rule. No doctrine file, stamp, allowlist,
NEVER list, authorization file or `retain_until` value moved. Every change adds
a refusal or runs one that was being skipped, and none removes one, so under
`AGENTS.md` section 3 rule 2 nothing can be reached after this change that could
not be reached before. No runtime exists, so the Class C design-record rule has
nothing to move.

**Agent involvement.** An agent in a Claude Code session wrote, ran and verified
every change below on the operator's instruction of 2026-09-28, on the worktree
branch `claude/hopeful-maxwell-69bb46` cut from `main` at `4a5c788`. The first
instruction withheld the commit and the push. The operator's second instruction,
the same day in the same session, was to have the plainsight session review the
work and, if all of it checked out, to commit, merge to `main` and push. The
review and what followed from it are the last section of this entry, which is
written before the commit.

**The finding the work started from** was measured on 2026-09-17 outside this
repository, by enumerating every validator mode and tracing it against the four
automated paths: the pre-commit hook through `core.hooksPath`, `make preflight`,
`.github/workflows/ci.yml`, and `tools/validate_conformance.py --kernel-gate`.
Five of the six validator self-tests, layer-model, ontology, cast, authorization
and retention, ran on none of them. Each was reachable only through its own
`make validate-X` target, which nothing calls. The hygiene self-test ran only
inside one CI step. This is the hole the handoff's known gaps named after the
fires_when fix was reported green in two sessions while the layer-model
self-test exited 1. The worklog carries no entry between 2026-09-11 and this
one, and this entry does not backfill that gap.

**Measured before any edit, at `4a5c788`.** All six self-tests exit 0:
layer-model at 62 breaks, ontology at 16, cast at 6, authorization at 41,
retention at 34, and hygiene at 4. Together they take about 1.3 seconds, against
1.8 for the whole hook. The kernel gate reports 8 implemented, 1 failed, 3
unratified and 5 pending, red on `retention-repo-scan` alone, which is the
disclosed state.

**Found on the way, and worse than the brief.** CI has not run its last two
steps on any push after 2026-09-08. A step's default condition is `success()`,
and the kernel gate step was red on the runs for `4e6abda`, `38c93cc`,
`132eef0` and `4a5c788`, so on all four the step that proves the pre-commit hook
runs and the check that refuses an agent co-authorship trailer were skipped.
`CLAUDE.md` section 5 calls the trailer check a mechanism rather than a habit,
and it had not run for four pushes. Run locally over all seventeen commits, it
passes.

**What changed.**

- `.github/workflows/ci.yml` gains five named steps, one per unwired self-test,
  placed before the kernel gate so a self-test that breaks turns its own step
  red rather than joining a gate that is already red. Every gate step now
  carries `if: ${{ !cancelled() }}`, so each reports its own result, and the job
  still fails if any does.
- `KERNEL_GATE` in `tools/validate_conformance.py` gains six IMPLEMENTED
  self-test entries, and two STUB entries for `tools/validate_ontology.py
  --matchers` and `--corpus`, which print DEFERRED, check nothing, exit 0, and
  were called by nothing. The list grows from sixteen entries to twenty-four.
  The authorization note's "six of the nine paths" becomes seven of the nine,
  dated, which is what the tool prints, and the docstring of
  `tools/validate_authorization.py` carried the same count and is corrected too.
- `.githooks/pre-commit` runs all six self-tests after the schema check and
  before the index scan, and prints a self-test's output only when it refuses.
  `make preflight` runs the same six, so the hook stays preflight less the
  telemetry test, at thirteen commands against fourteen.
- `AGENTS.md` section 5, `CONFORMANCE.md` section 4, the comments in the
  Makefile and the hook, `CHANGELOG.md`, this worklog, its archive and the
  handoff move to match. The oldest live entry, 2026-08-27 hardening, moved to
  the archive unedited, because this one would otherwise have been the eleventh.

**The decision to put the self-tests in the hook.** The hook's header records
why Step 8's artifact modes are absent from it: they refuse by design, so wiring
one in would block every commit, including the commit that records a stamp. The
self-tests differ, because they grade the checks rather than the stamps, and
that claim was measured rather than assumed. A scratch copy of the tree, outside
the repository, received dated rows in its copy of the pin of record for eight
paths: the seven SS-14 item 6 paths the authorization gate reported unstamped,
and the shred round-trip fixture. An earlier draft of this sentence called them
the eight Step 8 paths, which they are not. All six self-tests stayed green on
it, and `--policy` and `--shred-roundtrip` flipped to exit 0, which shows the
simulated stamps took effect. No file in this repository's pin of record was
touched. The review below showed that the conclusion drawn here reached further
than this measurement did.

**Design gate 1, run.** Two deliberate breaks, each applied to this worktree and
to an export of `4a5c788`, with every path run on both and each file restored
byte for byte afterwards. The first reintroduces the 2026-09-08 regression
exactly: a `dead_code` fixture with no `fires_when`. The second removes a
constraint rather than a fixture, by making the shred round-trip's no-canary
check unreachable.

| Path | `4a5c788`, layer-model break | This tree, layer-model break | `4a5c788`, retention break | This tree, retention break |
|---|---|---|---|---|
| The plain validator the old battery runs | exit 0 | exit 0 | exit 1, the designed UNRATIFIED refusal | exit 1, the same |
| Pre-commit hook | exit 0 | exit 1, naming the self-test | exit 0 | exit 1, naming the self-test |
| `make preflight`, recipe replayed | exit 0, eight lines | exit 1 at line 8 | exit 0, eight lines | exit 1 at line 12 |
| Kernel gate | exit 1, `retention-repo-scan` only | exit 1, adding `layer-model-self-test` | exit 1, `retention-repo-scan` only | exit 1, adding `retention-self-test` |
| CI job, run steps replayed | kernel gate red, last two skipped | `Layer-model self-test` red, every step ran | kernel gate red, last two skipped | `Retention self-test` red, every step ran |

The kernel gate row is the argument for the named CI steps. Its exit code was 1
before each break and 1 after it, because `retention-repo-scan` holds it red,
and only its entry line changed. After both restores, the clean tree runs the
hook green, preflight green at fourteen lines, the kernel gate red on
`retention-repo-scan` alone, and every CI step green except the kernel gate.

**Not verified.** No run on GitHub, because nothing is pushed. The CI row replays
the workflow's `run` steps locally under Git Bash on Windows, honouring each
step's `if`, and skips checkout, Python setup and the pip install; it is not
`ubuntu-latest`. `make` is not on this machine's PATH, so preflight was replayed
line by line with make's stop-on-first-failure rule. The first push after this
change is the first real measurement, and its run should be read step by step.

**Observed and left alone.** The cast and authorization self-tests record their
runs to `tools/gate_log.py` under the gate's own token, so a self-test run counts
in that gate's telemetry as a run of the gate, and this change runs both more
often; the other four record nothing. `tools/validate_doctrine.py` has no
self-test at all. In this worktree `core.hooksPath` names the main checkout's
`.githooks`, so a commit made here runs the hook as it stands on `main` rather
than the edited one. The `--corpus` mode stays owed, and its STUB entry makes the
debt visible on every kernel-gate run rather than paying it.

**The review, and what it overturned.** The plainsight session reviewed the
staged tree with seven lenses, each running the mechanism and each followed by a
refuter. Its verdict was to commit after three fixes. Its record is at
`Z-ISR/_session-artifacts/2026-09-28-plainsight-selftest-wiring-review/REVIEW.md`.
Each finding below was reproduced here before it was fixed.

- **Major: sealing the cast would have been refused.** Two cast self-test
  mutations assumed an unsealed file. `_mut_seal_without_hash` set `sealed` true,
  which changes nothing on a file already sealed with a hash, and
  `_mut_real_handle` filled a handle that the placeholder scan ignores once the
  file is sealed. Reproduced against a really sealed copy of
  `synthetic/GROUND_TRUTH.yaml`: the `4a5c788` self-test exits 1, missing
  exactly those two. The defect predates this change, and this change is what
  would have made it refuse the operator's sealing commit on all four paths.
  Fixed: the first mutation also nulls the hash, the second also unseals, and
  the self-test runs every mutation against a sealed in-memory copy as well.
  The fixed self-test exits 0 on the sealed copy, and reverting the two lines
  fails the sealed-copy pass on today's unsealed file.
- **Minor: the stamping claim was wider than its measurement.** The eight-row
  simulation never completed item 6, because the contract's two stamp-target
  rows in the Pending table keep its path unstamped whatever the Ratified table
  says. With those two rows resolved as well, `--fixtures` names no unstamped
  path, and the authorization self-test exits 1 on
  `AUTH_SELF_TEST_BASELINE_NOT_CLEAN`: row 8 of
  `conformance/gate/decisions.jsonl` takes the real pin as its source and
  asserts a refusal that no longer arises. All 41 breaks are still refused, and
  the other five self-tests stay green. The claim is narrowed in the hook, the
  Makefile, the changelog and the gate note, and the handoff records that the
  commit completing item 6 edits that row too.
- **Minor: the hook's refusal text misdiagnosed exit 1**, reading it as an
  unrefused break when these self-tests also exit 1 on a baseline that is not
  clean, which is what both scenarios above produce. The text now names both
  causes and a move for each.
- **Nits:** the CI comment claimed every validator self-test had a named step,
  and the aggregator docstring said the two stubs had gone unnoticed when the
  handoff and `CONFORMANCE.md` recorded `--corpus` and `docs/THE-GAMEPLAN.md`
  recorded `--matchers`. Both are corrected. The first review said the handoff
  and `CONFORMANCE.md` recorded both, the re-review corrected that, and the
  corrected reading is the one measured with `git show HEAD:<file>`.

Five follow-ups the review raised, none blocking, recorded here and counted in
the handoff.
Nothing fails if a later edit drops a self-test from one of the four paths, so
the instance is fixed and the class is not; a reconcile that every tool exposing
`--self-test` appears in `KERNEL_GATE` and in the hook would close it. The
attribution step prints its ok line when checkout produced no history, a case
`!cancelled()` makes reachable, so it should capture the status of `git log`
before grepping. Nothing enforces `!cancelled()` on a future gate step. STUB
entries discard their command's exit code and output. The two self-tests that
write telemetry now add a run to their gate's record on every commit.

The review also disclosed two touches of shared state: a `git write-tree` in this
worktree stored the index's tree object in the shared object store, and one of
its lenses ran a stamping simulation in the scratch clone the lenses shared
rather than its own, adding eight unstaged rows to that clone's pin of record
for a few minutes. The rows were removed, both review clones were confirmed back
at the reviewed tree, and neither of this repository's checkouts was otherwise
touched.

**The re-review.** The fix delta was re-reviewed at tree `3045ad6f` with four
lenses, the mutating ones each in a clone of their own and each followed by a
refuter, and the verdict was commit. Its record is at
`Z-ISR/_session-artifacts/2026-09-28-plainsight-selftest-wiring-review/RE-REVIEW.md`.
It confirmed the cast fix independently: reverting either line fails the
self-test on today's unsealed file, removing the sealed pass with both lines
reverted goes green, and a cast filled and sealed in one commit passes all three
cast modes, all six self-tests and the hook, where `4a5c788` exits 1. It also
confirmed the item 6 remedy: with all nine paths stamped, switching row 8 of
`conformance/gate/decisions.jsonl` to a fixture stamp state, or flipping its
expected decision to PERMITTED together with its register row in
`conformance/gate/README.md`, returns the authorization self-test and the hook to
exit 0, and the obvious edits to `artifacts_stamped` or `criteria_absent` do not.

Applied after the re-review, and so not inside the tree it read: the two text
corrections it recommended, the `--matchers` sentence above and this paragraph;
the guard it offered for a regression the fix introduced, where a seal block
that is not a mapping crashed `--self-test` with a traceback because the sealed
copy is built outside the per-mutation try; and two comment nits it listed, the
CI comment's "schema check", which is not a CI step, and a handoff "last ran
there" that read as Windows. The re-review cleared the guard on condition that
the cast self-test, the non-mapping seal case and the hook be re-run, and all
three were.

New follow-ups from the re-review, none blocking. After a real fill and seal,
the filled-handle case goes vacuous in both passes, because unsealing exposes
every real value to the placeholder scan and the expected code arises whatever
the mutation does; matching the finding by location as well as by code would
close it. Nothing asserts that the sealed copy is itself a valid sealed cast, and
the success line is a literal. The hook's refusal text lists a baseline cause
that two of the six self-tests lack, and omits a third cause of hygiene's.

Three findings for the operator rather than this change. `synthetic/CAST.md`
section 8 describes fill and seal as two commits, but the placeholder-scan step
of the hook already refuses a filled unsealed cast, so the one working route is
to fill and seal in one commit, which passes the hook after this change. The
commit that completes SS-14 item 6 also edits `KERNEL_GATE`, because
`retention-policy` then exits 0 and an UNRATIFIED entry that permits is refused
as `GATE_LIST_UNRATIFIED_PERMITTED`. Every gate accepts a dated stamp row for a
path that does not exist, such as `runner/dispatch_allowlist.yaml`.

---

## 2026-09-29, checkpoint closeout. Two defects measured outside the tree are recorded, and the handoff is corrected to match `b378cd8`.

**Class:** A. Records only: this entry, the oldest live entry moved to the
archive unedited, and the handoff. No doctrine file, stamp, schema, policy file,
generated artifact, corpus, fixture, validator, hook, workflow or README changed,
so `CHANGELOG.md` carries no entry.

**Agent involvement.** An agent in the plainsight session wrote this entry and
the handoff at the checkpoint closeout the operator called on 2026-09-29, which
the parent-folder session relayed. The relay authorized nothing, and no
instruction to commit these records had been given when they were written. Under
`CLAUDE.md` section 5, R6, the commit waits for the operator's instruction for
that act, and its message names that instruction.

**The battery, at `b378cd8`, before these records.** All fourteen preflight
commands exit 0, the six self-tests among them. Both forms of `git diff --check`
are clean. The kernel gate exits 1 on `retention-repo-scan` alone, with fourteen
implemented entries, that one failing, three unratified and refusing, two stubbed
and five pending. That is the disclosed state, and nothing else in the battery is
red.

**CI on GitHub confirmed the wiring.** Run 36501081165 on `b378cd8` ran every
step the workflow defines. The five named self-test steps passed, the kernel gate
failed on `retention-repo-scan` alone, and the hook step and the co-authorship
trailer check both ran after it and passed. That is the first run since
2026-09-08 in which those two steps ran. The handoff's known gap saying the
wiring had not run on GitHub is closed, and so is its instruction to read that
run.

**Two defects measured outside the repository and never recorded here.**

- The public README says a schema and a policy pack do not exist.
  `README.md:10-11` reads "No schema, no policy pack, and no collection mechanism
  exists." `git log --diff-filter=A` dates `schema/pse-event-0.1.schema.json` and
  `policy/semantics.yaml` to `4e6abda` on 2026-09-08, and
  `schema/subject-authorization.schema.json`, `policy/subject-authorization.yaml`
  and `policy/retention.yaml` to `0e0c840` on 2026-09-11. The README was last
  edited in `ff016af` on 2026-09-11, kept the sentence, and stands unchanged at
  `b378cd8`. Its "Next action" section also still describes Step 7 as future
  work. The collection-mechanism and connector clauses are still true. A
  different plainsight session first recorded the defect on 2026-09-14, in the
  crossings reply named below, and this session dated the additions with
  `git log` on 2026-09-15.
- The pin of record has three independent readers, and two of them disagree.
  `tools/validate_authorization.py` parses `doctrine/DOCTRINE_STATUS.md` with its
  `Pin` class and `tools/validate_retention.py` with `stamped_path()`, and
  `tools/validate_doctrine.py` checks that each criterion has a row and that its
  marker agrees, and reads no artifact path. No parser is shared. Instantiating
  the first two against the live file at `b378cd8` gives opposite answers for
  `spec/pse-semantics-contract.md`. `Pin.artifact_stamped` returns false, because
  the Pending table lists that path as a stamp target. `stamped_path` returns
  true, because it counts only the Ratified section and never subtracts the
  Pending table's stamp-target rows. The other paths tested all agree. The
  disagreement is latent, because `stamped_path` has two call sites, at
  `tools/validate_retention.py:1041` and `:1290`, and they pass the retention
  policy and the shred fixture, never the contract. This session first measured
  it on 2026-09-17 at `4a5c788`.

**Session context kept outside this repository.** This session answered three
fact requests from the ecosystem research sessions, on 2026-09-15, 2026-09-16 and
2026-09-17, and reviewed and re-reviewed the self-test wiring on 2026-09-28,
which the entry above records. The replies are kept under
`Z-ISR/_session-artifacts/2026-09-15-plainsight-harvest-of-c45e1214/` and the
reviews under `Z-ISR/_session-artifacts/2026-09-28-plainsight-selftest-wiring-review/`.
The crossings classing of 2026-09-14, which a different plainsight session made
and then corrected by erratum, is kept at
`Z-ISR/_session-artifacts/2026-09-14-plainsight-harvest-c45e1214/CLASS_F_CROSSINGS_REPLY.md`.
Its durable finding is that EG-1 defines exactly two environments, and no
criterion defines a third environment or a holder for this repository's material
in a shared picture. The one outside destination doctrine names is RT-18's
disclosure export to an agency. A crossing into a shared picture is therefore
unadjudicated until a rank-1 EGRESS decision defines one. The ecosystem register
states its own boundary, that person-centric outputs do not enter the ISR
picture, and that boundary appears nowhere in this tree. None of this changed a
file here, and none of it is a ruling.

**The worktree is left in place.** The branch `claude/hopeful-maxwell-69bb46`
stands at `b378cd8`, merged into `main`, and its worktree under
`.claude/worktrees/` is clean. It was not removed, for three reasons. The session
working in it is still open. Removing it also deletes its ignored `.gate-log/`,
the record of the gate runs made there, which RT-19 gives a 90-day lifetime so
that `doctrine/HYGIENE.md` can adjudicate the checks. A delete is an act this
closeout has no instruction for. `git worktree remove` and then `git branch -d`
are safe once that session is archived and the telemetry is kept or its loss is
accepted.

---

## 2026-09-30, the stale documentation the handoff and the 2026-09-30 harvest listed is corrected, and the records catch up with the worktree.

**Class:** A. `README.md`, `docs/THE-GAMEPLAN.md`, the handoff, this entry, and
the oldest live entry moved to the archive unedited. No doctrine file, stamp,
schema, policy file, generated artifact, corpus, fixture, validator, hook or
workflow changed, so `CHANGELOG.md` carries no entry.

**Agent involvement.** An agent in a personal-account PLAINSIGHT session drafted
every edit in this commit and ran the battery. The personal-account
parent-folder session dispatched the work with the operator's concurrence of
2026-09-30 17:50 quoted: "I concur with all your recommendations, so lets do
that first. Lets make sure everything is clean and up to date across the board
and then we will hold and discuss up next priorities." The dispatch named this
bundle and said the commit waits on the operator's word in this session, per
`CLAUDE.md` section 5. The operator gave it in this session on 2026-09-30,
answering "Commit and push" when asked whether to commit the staged bundle as
the operator with no agent trailer, push it to GitHub `main`, and read every CI
step. The agent executes the commit and the push on that instruction.

**What changed.**

- `README.md`. The status paragraph stops saying no schema and no policy pack
  exist. Both landed in `4e6abda` and `0e0c840`, and the false sentence survived
  the `ff016af` edit. The Next action section described patch 2 and Step 7 as
  future work, and both are done. It now names the next work in outline and
  points at the handoff, which is rewritten at every closeout, so the section
  restates less that can go stale. The closing paragraph called the repo scan a
  stub tracked as D-001, which Step 8 closed. The ZISR COP pointer named
  `../ZISR COP/`, which no longer exists beside this repository; the sibling is
  `../zisr-cop/`. The 2026-09-29 handoff listed the first two of these; the last
  two were found while correcting them.
- `docs/THE-GAMEPLAN.md`. Step 8 was tagged "BLOCKED on Step 3 ratification"
  although it was built in `0e0c840` on 2026-09-11. The tag now says built and
  unratified, and that the done-when is unmet by design.
- `docs/plainsight_handoff.md`. Its last line carried the app's
  session-metadata directory, a machine path, in a public file, and now says the
  path stays out. The second Resume path gains the `Z-ISR/` prefix every other
  citation uses. Section 4 loses the README gap and the worktree gap, and its
  sibling-citation gap names the two doctrine citations below. Section 6 names
  the 2026-09-20 and 2026-09-30 records, and its Sherlock row, which cited
  `../Sherlock/`, now names `Z-ISR/Sherlock/`. The file is 399 lines against its
  cap of 400.

**Facts this tree did not know, measured outside it.**

- On 2026-09-14 the repository moved with its siblings under a new parent folder
  by a same-volume rename, with git intact at `4a5c788`. No tracked file recorded
  the move until this entry. The sibling citations to `../ZMeta/` and
  `../zisr-producers/` resolve from the new place. Others did not. The
  README's ZISR COP pointer and the handoff's Sherlock row are repointed in this
  commit. `doctrine/RETENTION.md:381` and `doctrine/CREDENTIAL_LIFECYCLE.md:138`
  still cite `../ZISR COP/docs/OPERATIONAL_CONTRACT.md`, which exists at
  `../zisr-cop/docs/OPERATIONAL_CONTRACT.md`. Repointing them is a rank-1 edit
  outside this Class A commit, so they stay open in the handoff's section 4.
- On 2026-09-30 a team-account session harvested and archived two PLAINSIGHT
  sessions, one of them the session that built `b378cd8` in the worktree
  `claude/hopeful-maxwell-69bb46`. On the
  operator's answers in that session, the worktree's 751 gate-log records,
  spanning 2026-09-28T19:58:06Z to 2026-09-29T21:15:28Z, were appended byte for
  byte to this checkout's ignored `.gate-log/gates.jsonl`, which went from 3,188
  records to 3,939. The worktree was then removed and its branch deleted.
  `b378cd8` is on `main`, so nothing in git was lost. The log has no field naming
  the checkout that wrote a row, so this entry is the repository's record that
  those 751 rows came from the worktree. They include the self-test wiring's
  deliberate-break runs, and that session measured how they move the refusal
  rates `tools/gate_log.py --summary` reports: authorization from 147 runs at 82
  per cent to 220 at 65 per cent, and `retention-repo-scan` from 101 at 76 per
  cent to 136 at 72 per cent. The overdue telemetry review reads its rates with
  that in mind. The record is
  `Z-ISR/_session-artifacts/2026-09-30-plainsight-harvest-and-archive/HARVEST.md`.
- On 2026-09-28 and again on 2026-09-30 the operator named a parent-folder
  session, one on each of the operator's two accounts, whose relayed decision
  quoting the operator's dated concurrence is the operator's word for this
  repository. Neither delegation has yet carried an act on its own.

**Battery.** All fourteen preflight commands passed on the staged tree, among
them the six validator self-tests and the repo scan over the index. Both forms
of `git diff --check` were clean. The kernel gate was red on
`retention-repo-scan` alone, with 14 implemented, 1 failed, 3 unratified and
refusing, 2 stubbed and 5 pending, the disclosed state.

**Not done, and held.** The operator held the rest for a priorities discussion:
the adversarial review Step 8 is owed, the repo-scan exemption and the cast
seal, the shared pin-of-record reader, and the overdue telemetry review. Whether
GitHub still serves the pre-rewrite initial commit by hash has not been
re-measured.

**Refused this session:** nothing collected, no connector executed, no platform
touched, no doctrine landed.

---

## 2026-09-30, overnight, under the operator's grant of 23:28.

**The grant.** At 23:28:09 local on 2026-09-30 the operator wrote this in the
parent-folder session, and the parent's dispatch and its WORKLOG carry it
verbatim: "merge it on 9 and go for M0 dispatch and get me that prompt. Once the
prompt is in and I hand it over, I want you to run completely uninterrupted and
make decisions per your recommendation as you have a good grasp of the intent
and I will be going to bed and having you crash on this stuff while I sleep so I
can wake up at a reasonable time and continue to get after it with you as we get
to the demo time. also instruct the other sessions to do the same". The
personal-account parent-folder session relayed it here at about 23:31 with this
repository's items: the adversarial review Step 8 has owed since 2026-09-12; the
retention-scan exemption and the cast seal, on this session's own
recommendation; the two doctrine citations of the old COP folder name; the
pin-of-record reader; and the telemetry review. Earlier the same day the operator
named that session's relays, when they quote a dated concurrence, the operator's
word for this repository. This relay meets the four tests that delegation sets:
it came from that session, it quotes a dated concurrence, the words are verbatim
in the parent's records, and the items fall inside them. Every decision taken
under it is recorded here as revertible.

The grant does not reach what this repository reserves to the operator's own
hand, and nothing below works around that: a Class F decision, which needs a
per-item dated stamp (`AGENTS.md` section 3); an entry in an allowlist, NEVER
list, authorization file or `retain_until` value (section 4); and any doctrine
stamp.

**Agent involvement.** An agent in the personal-account PLAINSIGHT session made
every change in this entry, ran every check, and executes the commits, pushes,
pull requests and merges under the grant, with the operator as author and no
agent trailer.

**First change: the repo-scan values, Class B, decided under the grant.**
`tools/validate_retention.py --repo-scan` refused two filled handle selectors
that predate Step 8, a worked example in `docs/PLAINSIGHT-FOUNDATION.md` and a
value in `tools/validate_ontology.py`'s `value_in_a_form` fixture. The scan's
refusal names three moves. An exemption row narrows an RT-15 scan, which Step 8
refuted as the operator's reach decision, and an agent may not add one. A
synthetic value waits on the cast seal. The first move needs neither, and it is
the one taken: the worked example now reads in the registry's form,
`handle:<platform>/<string>`, and the fixture keeps its platform segment a
placeholder, so the line carries no complete typed handle while
`ONT_VALUE_IN_FILE` still fires on its filled segment. Whether the worked
example's value named a real account was not checked, because checking means
looking it up on a platform. Both values remain in git history, which is RT-15's
fourth part. Reverting is restoring the two lines.

**Second: the ZISR COP citations, Class A, decided under the grant.**
`doctrine/RETENTION.md:381` and `doctrine/CREDENTIAL_LIFECYCLE.md:138` cite
`../ZISR COP/docs/OPERATIONAL_CONTRACT.md`, and the repository is now
`../zisr-cop/`. The quote RETENTION.md places at lines 315 to 316 now sits at
lines 315 to 317 of that file, so the citations are dated measurements rather
than live pointers. `AGENTS.md` section 7 already treats the `../zisr-recon/`
measurements that way, keeping the old path and translating it elsewhere, so the
doctrine files keep theirs and `README.md` translates the path. No doctrine file
changed. Reverting is removing the README sentence.

**Third: the cast seal, not taken.** Filling `synthetic/CAST.md` needs the
personas, the SIMs and section 9's six decisions, which are the operator's acts,
and an agent filling it would invent the ground truth the seal exists to fix.
The recommendation is unchanged from the handoff: the operator decides the fork
between provisioning the cast alongside the collection pool and a Class F
amendment to SS-14 item 6.

**Battery for the first change.** All fourteen preflight commands passed on the
staged tree, the ontology self-test refusing the edited break by
`ONT_VALUE_IN_FILE` alone, and both forms of `git diff --check` were clean. The
kernel gate exited 0, with 14 implemented checks passing, 3 unratified and
refusing, 2 stubbed and 5 pending, the first exit 0 since `0e0c840`.

**Fourth: the telemetry review, Class A for the record and Class B for the
recording fix.** The first review under `doctrine/HYGIENE.md` HY-2 was overdue
since 2026-09-11. The snapshot was taken at 2026-10-01T03:45:10Z over 4,078
records, 2026-08-27T07:43:47Z to 2026-10-01T03:41:36Z, by a read-only script
kept with the overnight records outside this repository, because the log has no
field naming the checkout or the caller and the segments can only be cut by
position. The segments: records 1 to 3,188 before 2026-09-03, when a refusing
validator wrote one refuse record per finding; records 1 to 3,188 from that date;
records 3,189 to 3,939, the 751 rows appended from the removed worktree on
2026-09-30, many of them the self-test wiring's deliberate breaks; and the
records written since. Audit runs made to verify claims cannot be filtered out
and are in every segment.

The adjudication, gate by gate, against HY-2's four rows:

- `authorization`, 233 runs and 147 refusals over the window, 82 per cent on
  main before the worktree and 30 per cent in it. The rate means nothing since
  2026-09-28: the self-test, which passes, logs under the same name as
  `--fixtures`, which refuses by design, and the self-test now runs on every
  path. This commit gives the self-test its own name. The designed refusal is
  HY-2's second row, accepted with its reason stated: the artifacts carry no
  dated row, the kernel gate asserts the refusal, and a stamp clears it. Kept.
- `retention-policy` and `retention-shred-roundtrip`, 108 and 102 runs, every
  one refused, for the same stated reason. Kept.
- `retention-repo-scan`, 146 runs and 101 refusals, every refusal one of the two
  values replaced in the first change. The working-tree scan and the hook's
  staged scan shared the name, which is why 45 runs passed. This commit gives
  the staged scan its own name. Kept.
- `cast`, 390 runs, and `ontology`, 279 runs, with no refusal. HY-2's first row
  asks for a deliberate break. Both self-tests break the artifact on every hook,
  preflight, kernel-gate and CI run since 2026-09-28 and assert each break is
  refused, and both passed tonight. Kept.
- `doctrine`, 348 runs and one refusal, on 2026-08-27, and no self-test, so HY-2's
  first row applies in full. Nine deliberate breaks were made in a scratch copy.
  Six refused: a duplicate criterion, an emptied rank-1 file, a stripped
  conclusion marker, a dangling criterion reference, a deleted status row for
  RT-19, and a status row for an undefined criterion. Three did not, for two
  reasons. Deleting
  SS-1's per-criterion row passes, because the check reads every table row that
  opens with a criterion id, and the Ratified row "SS-1 to SS-21, all criteria"
  stands in for it. For SS-1 the check cannot fire, which HY-2 calls no check.
  Deleting that Ratified row, or blanking its date, also passes, because nothing reconciles
  a doctrine file's inline conclusion marker with the Ratified table. The
  mechanisms downstream fail closed on that one, since the authorization gate
  reads the Ratified row. The first is a defect and the shared pin-of-record
  reader closes it; the second is recorded as open.
- `hygiene`, 406 runs and 40 refusals, led by `HYGIENE_TOOL_NOT_IN_ANY_GATE` at
  19 and `HYGIENE_HANDOFF_OVER_CAP` at 18. Each was a real catch answered by a
  fix, and neither code dominates. Kept.
- `layer-model`, 22 refuse records, 17 of them `LM_CODE_ENTRY_KEYS`. HY-2's third
  row would read that as two rules. It is one run: all 17 carry the timestamp
  2026-09-09T01:32:43Z and are the 17 truncated `fires_when` sentences the Step 7
  review found, counted once per finding because this gate never moved to the
  run-record convention of 2026-09-03. Read per run, these are rare catches.
  Kept.

**The recording fix.** `tools/validate_layer_model.py` and
`tools/validate_cast.py` still wrote one refuse record per finding and no run
record, so their refusal counts were per finding against HY-1. Both now write one
run record and one detail record per finding, as the other five validators do.
The authorization and cast self-tests record as `authorization-self-test` and
`cast-self-test`, and the staged repo scan as `retention-repo-scan-staged`, so
each name carries one mode with one designed outcome. Records already written
are left as they are, because rewriting a telemetry history to look consistent
is what design gate 6 forbids. No check, threshold or refusal changed.

**Records this session added to the log by mistake.** While exercising the
recording fix, a scratch-copy extraction failed and the test script that
followed it ran in the main checkout. It wrote 21 records between
2026-10-01T03:48:18Z and 03:48:20Z, records 4,079 to 4,099, including one
deliberate layer-model break that refused with four findings. It also rewrote
`spec/layer-model.yaml` with CRLF line endings and identical content, which
`git checkout` restored byte for byte before anything was staged. The records
stay in the log and a review excludes them by that window.

HY-2's basis stamp falls due at this review and stays the operator's.

**Battery for the fourth change.** All fourteen preflight commands passed on the
staged tree and both forms of `git diff --check` were clean. The kernel gate
exited 0, with 14 implemented checks passing, 3 unratified and refusing, 2
stubbed and 5 pending.

**Fifth: the Step 8 adversarial review, owed since 2026-09-12.** Run against
`de9e754` as one workflow. Eight lenses, each required to execute the check it
reviewed in its own scratch copy with telemetry off and to quote the output: the
authorization mechanism, the retention mechanism, the stamped state, the schema
and the gate corpus on Opus 5.5, the two doctrine-fidelity lenses on Fable 5.1,
and self-description on Sonnet 5.5. One refuter per finding reproduced it in a
fresh copy, defaulting to refuted, on Fable 5.1 for the doctrine-fidelity
findings and Opus 5.5 for the rest. Of 89 findings, 88 stand: three
ratification blockers, 53 class B defects, two class F defects, 18 drift
findings and 12 notes. The refuters overturned one, against the three-to-one
over-report of the prose reviews of 2026-09-04 and 2026-09-20, because a lens
here could not make a finding without running the mechanism. The workflow was
stopped before its completeness critic, under the operator's machine-load rule
of 2026-09-30 23:49, and resuming it with a changed script re-ran agents rather
than replaying them, so it was stopped again and the results were rebuilt from
its journal. The critic has not run. The record, each finding with its status,
is `Z-ISR/_session-artifacts/2026-09-30-plainsight-overnight/REVIEW.md`, with the
claims, commands and outputs beside it.

**Sixth: one reader of the pin of record, Class B, decided under the grant.**
The largest cluster in the review was the pin. `tools/validate_authorization.py`
parsed the Ratified table's cells, `tools/validate_retention.py` accepted any
dated line naming a path anywhere under the Ratified heading, and
`tools/validate_doctrine.py` read every table row that opens with a criterion id.
On the unmodified pin the first two disagreed about
`spec/pse-semantics-contract.md`. Two of the three ratification blockers lived
here: one dated row naming a path stamped the whole file, so the dated row the
policy prescribes for resolving one of its sixteen entries would have stamped the
policy, and the D7 version-label row would have stamped the contract once its two
Pending rows were removed. `tools/pin_of_record.py` is now the one reader the
three import, and on every axis it takes the stricter of the readings they took.
Only the Ratified table stamps. The Conclusion stamped cell must be a calendar
date and nothing else, and the ratifier a declared one. A whole-artifact stamp
needs an Item cell saying "whole artifact" or "all criteria" and a File cell
naming the path alone, and any other row stamps the item it names. The contract
is stamped by its §5 and §12 rows together, as SS-14 item 6 compiles it. A
Pending stamp-target row still holds a path, a stamp for an absent file stamps
nothing, and criterion rows are read from the per-criterion table alone, which
closes the SS-1 blind spot the telemetry review found. Its eight predicates are
assistant readings, PIN-R1 to PIN-R8, recorded in the module and awaiting the
operator's confirmation. PIN-R8 keeps the old header heuristic that skips a row
whose Item cell begins with "Item", because accepting such rows would widen what
stamps, which is class F.

No current outcome changed. The same seven SS-14 item 6 paths refuse, the
retention policy and the shred fixture refuse, and the five doctrine files bind
through their range rows. The refusals now state why a path is unstamped rather
than saying "no dated row" when one exists, and they quote the row format that
stamps. The reader's self-test plants 21 cases, and each of its eleven rules
was deleted in a scratch copy, which turned the self-test red every time.
`tools/validate_doctrine.py` gains its first self-test, ten planted defects, and
restoring its old whole-pin read turns the SS-1 case red. The retention
self-test gains two cases: an entry row in house format must not clear the
policy refusal, and withdrawing the retention range row must refuse. Both new
self-tests run on the hook, preflight, the kernel gate and CI.

This closes 13 of the review's findings and part of a fourteenth. It leaves the
third blocker, the RT-11 override `policy/retention.yaml` compiles against the
pin's RT-11 row, 55 other class B findings and 17 class A ones, which the review
record lists.
Binding a stamp to its artifact's content is a change to the pin's format and is
the operator's.

**Battery for the sixth change.** All sixteen preflight commands passed on the
staged tree, the eight self-tests among them, and both forms of
`git diff --check` were clean. The kernel gate exited 0, with 16 implemented
checks passing, 3 unratified and refusing, 2 stubbed and 5 pending.

**Seventh: the third ratification blocker and two dropped modes, Class B,
decided under the grant.** `policy/retention.yaml` compiled RT-11's halt
override as permitted, with a `permitted_when`, beside a `clears_when` that names
only a passing verify_shred. The pin of record's RT-11 row reads "Cleared only by
a passing verify_shred, logged. No override", and RT-11's body describes an
override entry, so the compilation had picked the body without recording the
conflict and never said whether an override lifts the dispatch block. Both
copies, `halt.override` and the ledger's `halt_override` act, now defer to
U-17, a class F entry whose three legal options each need a doctrine or pin
amendment and whose refusal renders "CONNECTOR DISPATCH REMAINS BLOCKED". Nothing
read the halt block before, so `tools/validate_retention.py` grades it as R-10,
`RETENTION_POLICY_HALT_DRIFT`, and its self-test gains three breaks: an override
that lifts the halt, a per-case halt cleared on a ledger entry, and a deleted
halt. The decision is the operator's, and U-17 joins the open entries.

The same commit fixes two defects that dropped a mode. SS-14 item 6's preflight
line, `tools/validate_retention.py --policy --shred-roundtrip`, ran the round
trip and dropped `--policy`, so a drifted or unstamped policy passed the
preflight it names. That pair now runs both and records each under its own
name. `tools/validate_authorization.py --fixtures --self-test` ran the
self-test and dropped the fixtures. Every other combination of modes in either
tool now refuses with exit 2, except the two deferred authorization modes,
which combine as before. With these, 17 of the review's 88 findings are closed.

**Battery for the seventh change.** All sixteen preflight commands passed on the
staged tree and both forms of `git diff --check` were clean. The kernel gate
exited 0, with 16 implemented checks passing, 3 unratified and refusing, 2
stubbed and 5 pending.

**Eighth: five robustness findings, Class B, decided under the grant.** The
repo scan, RT-15's mechanism, skipped files and still reported ok. git quotes a
path with a non-ASCII character unless asked for NUL-separated output, so the
quoted name opened nothing in either mode; the working-tree mode also skipped
any file that is not valid UTF-8, and a staged file git could not show vanished.
Both modes now take names NUL-separated and decode every file with replacement,
so a selector in its ASCII typed form is still found, and an unshowable staged
file refuses. A synthetic handle planted in a file with a non-ASCII name and in a
non-UTF-8 file was found by both modes in a scratch repository. When
`tools/validate_layer_model.py` could not be imported, the retention policy check
fell back to empty strata sets, and R-01, RT-2's own refusal, passed with nothing
to compare; it now refuses as `RETENTION_LAYER_MODEL_UNREADABLE` and keeps no
copy of the sets. A policy or fixture of the wrong shape ended in a traceback
and exit 1, which a caller cannot tell from violations found; it is now
`RETENTION_INPUT_MALFORMED` with exit 2, and the authorization gate's reader
refuses a non-UTF-8 input as `AUTH_INPUT_UNPARSEABLE` with exit 2. The retention
self-test gains four breaks and refuses all 43. With these, 22 of the review's 88
findings are closed.

**Battery for the eighth change.** All sixteen preflight commands passed on the
staged tree and both forms of `git diff --check` were clean. The kernel gate
exited 0, with 16 implemented checks passing, 3 unratified and refusing, 2
stubbed and 5 pending.

**Ninth: 17 statements the Step 8 artifacts made about themselves, Class A and
B, decided under the grant.** The review's self-description, gate-corpus and
doctrine-fidelity lenses found statements in the Step 8 artifacts that are false
when the tools run, nearly all because the artifacts were written before the
tools they describe were finished. `conformance/retention/shred-roundtrip.yaml`
called `tools/validate_retention.py` the Wave 0 stub that ignores its
arguments, in four places, and listed RT-13 among the criteria it exercises
while its own reading SR-R2 puts RT-13 out of scope. `conformance/gate/README.md`
said no gate reads it, that nothing enforces its six-part contract, that a held
row asserts nothing, and that the reconcile GF-R2 relies on does not exist.
`policy/retention.yaml` listed its aggregator entry as PENDING, its repo scan as
tracked under D-001 and as checking nothing, its renewal refusal under "and"
where the machine field says "either", and U-05's refusal as replacing four
mappings where it has three. Three rows of `conformance/gate/decisions.jsonl`
named GF-U6, which does not exist, in their descriptions, where their pending
lists say GF-U4. The schema and the authorization tool said `--fixtures`
validates each record as a schema instance; it checks key sets and the class
enum, and every record would fail full validation today on SAS-U1 and SA-U2. The
schema cited SA-U4 where its own list says SAS-U4. `policy/subject-authorization.yaml`
had a comma where doctrine's N0 and L0 definitions have a colon, which read as
one more member of each class; both are now quoted scalars equal to doctrine's
text. The deferred authorization modes now say that their exit 0 is not clean,
and the cast gate names `--disjointness` as deferred rather than built.

Three findings are fixed in part. The VA-U2 option that a deferred mode exit
with a distinct code is not added, because adding an option to an open entry
shapes a decision that is the operator's; `credentials.disjointness` does not
gain the `mechanism_exists: false` key the review proposed, because that adds a
field to the compiled policy rather than correcting a sentence, and this batch
changes text only; and the item 6 row's own description is unchanged. Left alone and
recorded in the review record: `doctrine/SUBJECT_SELECTION.md`'s enforcement-state
paragraph, which is rank 1, and the generated lineage policy's `evaluated_by`
text, which changes only through the generator. No check, value, row assertion
or refusal changed. With these, 39 of the review's 88 findings are closed and
three are closed in part.

**Battery for the ninth change.** All sixteen preflight commands passed on the
staged tree and both forms of `git diff --check` were clean. The kernel gate
exited 0, with 16 implemented checks passing, 3 unratified and refusing, 2
stubbed and 5 pending.

**Tenth: five holes in what the authorization gate checks, Class B, decided
under the grant.** Each was a value `tools/validate_authorization.py` read and
never compared, and each fix adds a refusal and removes none. The schema's
required list sat in a variable nothing used, so dropping `expires_on` from it
let a partial SS-4 record validate; the schema's record shape is now compared
with SS-4's nine fields, closed, as `AUTH_SCHEMA_RECORD_SHAPE_DRIFT`. SS-14 item
6's list was pinned by count alone, so swapping item 8's absent allowlist for a
tracked path kept both counts and cleared item 8; the eight items' paths are now
pinned in `RATIFY_ITEMS`, as `AUTH_RATIFY_LIST_DRIFT`. The compiled criteria were
never compared with doctrine, so dropping SS-14 from the list and its row from
the pin passed; the list is now reconciled with the SS ids
`doctrine/SUBJECT_SELECTION.md` defines, in both directions, as
`AUTH_CRITERION_NOT_COMPILED`, which also keeps the "check Step 8 names is green"
line from printing when A-19 did not run. A-07 accepted any compiled sentence for
any value, so a REFUSED row could render that the run proceeds; it now accepts
only the sentence compiled for the row's own value. A-18 read only rows naming
item 6, and a well-formed permit row names none, so a permit asserted under a
stamp state item 6 refuses passed; a second pass now reads every decided row.
The self-test gains six breaks and refuses all 47, five of them with a stated
cascade. Each new check was confirmed not to fire on the real corpus before it
was written: every decided row but the two item 6 rows carries a complete
fixture stamp state. With these, 46 of the review's 88 findings are closed and
three are closed in part.

**Battery for the tenth change.** All sixteen preflight commands passed on the
staged tree and both forms of `git diff --check` were clean. The kernel gate
exited 0, with 16 implemented checks passing, 3 unratified and refusing, 2
stubbed and 5 pending.

**Eleventh: five holes in what the retention gate checks, Class B, decided under
the grant.** The strata table was pinned by its row count alone, so replacing
the authorization row with a second skeleton row, or setting gate telemetry's
lifetime to permanent, kept seven rows and passed; each of RT-1's seven rows is
now pinned by name with its stratum, subject values, lifetime and boundary, as
`RETENTION_POLICY_STRATA_ROW_DRIFT`, and the pin was checked against doctrine's
RT-1 table before it was written. R-01 refused a subject value only in strata 2
and 3, so declaring the synthetic corpus or gate telemetry to carry subject
values passed, against RT-1's "Synthetic only" and "None, by construction"; it
now reaches every stratum outside the shred boundary. Three rules that bound how
long data is held were read by no tool: a case extension does not extend
incidental content, either way round, and the case ceiling is an absolute
deadline. They are pinned beside the durations and refuse as
`RETENTION_POLICY_TTL_DRIFT`. The criteria check iterated the policy's own list,
so deleting RT-2 from it removed the check; it now runs over RT-1 to RT-19
pinned in the tool, and the list is refused as `RETENTION_CRITERIA_LIST_DRIFT`
when it differs. The self-test only asserted that the stamp mutations cleared a
refusal, which held trivially when the refusal never fired, so a stamp reader
that always said stamped passed it; two cases now remove the artifact's rows
from the pin and assert the refusal is there. The self-test refuses all 51
breaks, three older ones now with the strata pin as a stated cascade.

Two of the five are fixed in part. The undeclared-placeholder reconcile still
filters by each file's own prefix, and the layer model's `LM_RT2_VIOLATION`
still reaches strata 2 and 3 only, because widening it changes a second tool.

A correction to the seventh change above: it called the halt check R-10, an id
this tool's docstring already gives the repo scan. The check is R-18, and the
docstring now carries it. With these, 49 of the review's 88 findings are closed
and five are closed in part.

**Battery for the eleventh change.** All sixteen preflight commands passed on
the staged tree and both forms of `git diff --check` were clean. The kernel gate
exited 0, with 16 implemented checks passing, 3 unratified and refusing, 2
stubbed and 5 pending.

**Twelfth: the completeness critic, and a batch of row-contract and scan
holes, Class B, decided under the grant.** The review's completeness critic,
stopped earlier under the machine-load rule, ran as one Opus 5.5 agent against
`8bedba1` with its refuters three at a time, and found 11 more findings, none
refuted. Most are holes in the night's own fixes, and two are ratification
blockers. The shared reader's whole-artifact test is a substring match on the
Item cell, so an entry row worded "not the whole artifact", or a struck or
withdrawn whole-artifact row, stamps the whole file and clears both retention
refusals end to end, which brings back the blocker `c552d13` closed. And
nothing reads SS-14 item 6's seal condition for the cast, so stamping
`synthetic/CAST.md` would clear item 7 while the cast is unsealed. Both are
next. The record is `critic_result.json` beside `REVIEW.md`.

This commit closes three of the critic's findings and three of the review's.
The new A-18 pass skipped a row with no stamp state, which is the case it was
written for; a missing or empty state now reads the live pin, as the first pass
does. The reader took the contract's section granularity from the policy's own
text, so the policy under ratification decided how finely it was stamped; the
sections are now pinned in the tool as `RATIFY_SECTIONS`, and a policy
granularity that differs refuses. SS-14 item 6's four preflight checks were
pinned by count only, so one could be swapped for a mode that always exits 0;
they are pinned by value as `PREFLIGHT_CHECKS`. From the review: the decision
and input keys of every row are now checked, and a row that claims a collected
string sits in the corpus refuses; SS-5's fixture for a field must name both
SS-5 and the field as tokens, and a candidate with no record, or no permitted
baseline to differ from, refuses rather than being skipped; and the repo scan
tests every match on a line, so an allowlisted match no longer hides a live one.
The self-tests gain eleven breaks and refuse 55 and 52. The SS-5 whole-row
comparison and A-10's handling of a null record are left open, because the
first needs a corpus edit and the second an exemption for the rows that have no
record by design.

**Battery for the twelfth change.** All sixteen preflight commands passed on the
staged tree and both forms of `git diff --check` were clean. The kernel gate
exited 0, with 16 implemented checks passing, 3 unratified and refusing, 2
stubbed and 5 pending.

**Thirteenth: the blocker the critic found in the shared reader, Class B,
decided under the grant.** `tools/pin_of_record.py` tested the whole-artifact
wording as a substring of the Item cell. The critic showed an entry row worded
"SA-U4 only, not the whole artifact", a struck whole-artifact row, and one marked
WITHDRAWN each stamping the whole policy, and three such rows clearing both
retention refusals end to end. This is the blocker `c552d13` closed, back
through the pin's own sentence, which invites exactly that wording. The Item
cell is now a closed grammar: exactly "<what>, whole artifact" with no "not" in
<what>, or a doctrine range "<NS>-1 to <NS>-<n>, all criteria". Any cell carrying
a strike or the word withdrawn, struck, superseded or revoked makes the row
stamp nothing, so a row is withdrawn by a later dated row. Three neighbouring
holes closed with it. A range row stamped every criterion of its file, so RT-19
bound with no dated row covering it and any criterion added later bound under
the old range; a criterion now binds only inside a stated range or a row naming
it after the file's path. The reader had dropped the 19xx or 20xx year bound the
old authorization reader held, so a year-2199 stamp counted; the bound is back.
PIN-R6 claimed a file written after its stamp arrives unratified, which the
reader does not enforce; PIN-R6 now states the limit, and a case keeps it
visible until the operator decides content binding. On the real pin the same
five files and all 58 criteria bind. The reader's self-test gains ten cases and
holds 31, and the retention self-test gains a case where deleting RT-19's own
row refuses.

**Battery for the thirteenth change.** All sixteen preflight commands passed on
the staged tree and both forms of `git diff --check` were clean. The kernel
gate exited 0, with 16 implemented checks passing, 3 unratified and refusing,
2 stubbed and 5 pending.

**Fourteenth: SS-14 item 7's seal condition, the critic's second blocker, Class
B, decided under the grant.** SS-14 item 6 refuses collection until
`synthetic/CAST.md` is stamped "with a sealed, hash-pinned GROUND_TRUTH.yaml
carrying at least one designed confuser pair". The compiled policy kept that
clause only as item 7's granularity text, which no function reads, and none of
the four preflight checks reads the seal; so a stamp row for CAST.md would have
cleared item 7 on an unsealed cast. `tools/validate_authorization.py` now counts
CAST.md as met on the live pin only when `tools/validate_cast.py`'s own checks
pass: the cast is sealed, its seal fields and recorded hash verify, and no
confuser-pair code fires. The refusal says which of those failed. A constructed
check in the shape of A-19, `AUTH_CAST_SEAL_UNREAD`, reads every item 6 path as
stamped and asserts the unsealed cast still refuses; with the condition removed
in a scratch copy, the self-test's baseline and `--fixtures` both refused. Two
limits are stated rather than closed. A fixture-supplied stamp state still lists
the cast as it chooses, because whether a fixture may supply the table at all is
GF-U1, which is open. And once the cast is sealed for real, the constructed
check has nothing left to observe.

**Battery for the fourteenth change.** All sixteen preflight commands passed on
the staged tree and both forms of `git diff --check` were clean. The kernel
gate exited 0, with 16 implemented checks passing, 3 unratified and refusing,
2 stubbed and 5 pending.

**Fifteenth: the critic's three retention findings, Class B, decided under the
grant.** R-18, the RT-11 halt check `722b367` added, matched substrings: a halt
that "blocks nothing; connector dispatch continues", one that also clears on an
operator's ledger entry, a dispatch runner added to the exemptions, a trigger
narrowed to flagged cases, and an answer written into U-17's deferral all
passed, which repeats the weakness the review found in RT-9's guards. The halt is
now pinned by value as `HALT_PIN`, with the ledger's halt acts, and the
self-test gains a break for each of the five widenings, each of which the old
check passed. The repo scan decoded every file as UTF-8 with replacement, which
turns a UTF-16 file into text no shape matches while counting it read and clean;
UTF-16 with a byte-order mark is what Windows PowerShell 5.1's `Out-File` writes
by default. A file with a UTF-16 or UTF-32 mark is now decoded by it, and bytes
carrying NUL without a mark, a binary or BOM-less UTF-16, refuse as
`RETENTION_REPO_SCAN_SOURCE_UNREADABLE`; other bytes are still read as UTF-8 with
replacement, because the typed shapes are ASCII and an ASCII-compatible file
reads them the same. That is less strict than the critic proposed, which
refused every non-UTF-8 file, and the difference is a judgment recorded here.
The not-reached notice now names compressed and binary containers, and the
self-test gains two decode cases that fail if the decode reverts. A clean
combined `--policy --shred-roundtrip` run reported only the round trip; it now
reports both. With these the critic's eleven are closed, three in part.

**Battery for the fifteenth change.** All sixteen preflight commands passed on
the staged tree and both forms of `git diff --check` were clean. The kernel
gate exited 0, with 16 implemented checks passing, 3 unratified and refusing,
2 stubbed and 5 pending.

**Sixteenth: compiled rules and RT-9's guards by value, and item 6 per
criterion, Class B, decided under the grant.** Three review findings.
`tools/validate_retention.py` pinned eight durations and nothing else the policy
compiles, so RT-7's index inside the boundary, RT-8's case-level text rule,
RT-4's encryption from first write and its plaintext prohibition, RT-3's two
shred mechanisms, RT-13's pre-shred finding check, RT-17's renewal fields and
refusal, RT-18's freeze-only disclosure, RT-9's all-checks rule and RT-19's
untracked, value-free telemetry could each be flipped with `--policy` still
green once stamped. Thirteen are now pinned by value in `PINNED_RULES` and
refuse as `RETENTION_POLICY_RULE_DRIFT`, each with a generated break that flips
it; the review's cassette-rule path does not exist in the policy and is left
out. RT-9's guards were substring tests in both artifacts: check 1 needed only
the word "key", the witness needed only "enumerable delete path" somewhere in
its text, and checks 4 and 5 had no guard. Check 1's passing condition, its
required failures including a successful decrypt, the witness's place, and
checks 4 and 5's passing conditions are now pinned per artifact, and the
fixture's shred step must act on the target and leave the canary. The
authorization gate read SS-14 item 6's "RETENTION.md per criterion" at file
granularity, because the subject policy compiles SS criteria only; RT-1 to
RT-19 are pinned in the tool as `ITEM_6_RT_CRITERIA` and checked per criterion,
and the summary now counts 40. The self-tests refuse 77 and 56 breaks. With
these, 53 of the review's 88 findings are closed and seven in part.

**Battery for the sixteenth change.** All sixteen preflight commands passed on
the staged tree and both forms of `git diff --check` were clean. The kernel
gate exited 0, with 16 implemented checks passing, 3 unratified and refusing,
2 stubbed and 5 pending.

**Seventeenth: how RT-15's enforcement is stated, Class B, decided under the
grant.** RT-15 lists four enforcement parts and requires all four: the
Execution Limits clause in `AGENTS.md`, `canary_subject_class` as a required
connector manifest field, the violation code `FIXTURE_CONTAINS_LIVE_SELECTOR`,
and the scan in the pre-commit hook. The policy's own table records two present
and two absent. `AGENTS.md`, `README.md`, `CONFORMANCE.md`, the kernel gate's
note and the handoff said three of four were enforced, and the scan printed the
same on every run; each counted git history as the fourth part, which RT-15 does
not list. Git history is a reach limit of any commit-time check, and that is now
stated apart from the four. The scan measures the four parts on every run, from
`AGENTS.md`, the connector manifests, the code vocabulary and the hook, and names
the two not in place; the self-test fails if that measure disagrees with the
policy's table. VR-U3's recorded consequence is updated to match. The earlier
records that say three, this worklog's entry of 2026-09-11 and the CHANGELOG
entry of Step 8, stay as written. With this, 54 of the review's 88 findings are
closed and seven in part.

**Battery for the seventeenth change.** All sixteen preflight commands passed
on the staged tree and both forms of `git diff --check` were clean. The kernel
gate exited 0, with 16 implemented checks passing, 3 unratified and refusing, 2
stubbed and 5 pending.

**Eighteenth: SS-5's one-field check reads every gate input, Class B, decided
under the grant as renewed at 01:26.** The maintainer's handover at 01:26 on
2026-10-01, relayed by the parent session and recorded verbatim in the parent
folder's dispatch record of that date, renews the grant to a natural stopping
point and adds no authority it did not give. Three review findings, one defect.
A-12 compared each SS-5 fixture with its nearest permitted row on the
authorization record alone, so a fixture could also differ in its chain, its
dispatch, its given inputs or its instant and still count as a one-field
mutation. One did: `one-hop-pivot-depth-max-mutated` named its item's locator
differently from `one-hop-permitted`. A-12 now compares all five inputs. Each
row's identifiers are uuid5 of labels, so they are paired by position and renamed
before the comparison, and a pairing that is not one to one, or a reference that
points at a different event after renaming, is a difference. A chain payload's
copy of the field must equal its own record's value. The fixture's locator is
restored to the baseline's, which leaves `--fixtures` output byte-identical to
`8352e4b`. Four self-test breaks are new, the locator, a moved reference, a
GRANT copy left at the baseline value and two baseline identifiers collapsed
into one, and removing the pairing's reverse direction lets the last one pass.
Seven existing breaks that change `seed-permitted`, the differential baseline,
now also fire A-12, and each says so. With this, 57 of the review's 88 findings
are closed and seven in part.

**Battery for the eighteenth change.** All sixteen preflight commands passed
on the staged tree, the authorization self-test with 60 breaks, and both forms
of `git diff --check` were clean. The kernel gate exited 0, with 16 implemented
checks passing, 3 unratified and refusing, 2 stubbed and 5 pending.

**Nineteenth: A-19 reads the pin, Class B, decided under the grant as renewed
at 01:26.** One review finding. Every stamp state A-19 constructed carried
`source: fixture`, so `item_6_reasons` echoed the lists it was handed and never
called the reader; replacing `Pin.criterion_stamped` with one that answers True
left `--fixtures` and `--self-test` unchanged. A-19 now also builds three copies
of the pin of record in memory. The copies replace the Ratified and Pending rows
for the item 6 paths outside `doctrine/` with whole-artifact rows. One copy drops
the Step 3 row of the first compiled criterion and must refuse it; one leaves out
the first existing path's row and must refuse it; one stamps every path and must
permit, apart from two refusals the reader is right to make on this tree, a path
with no file and a stamped cast that is unsealed. A refusal the pin of record
itself makes for a doctrine file or a criterion is left to the checks that read
it. `_pin` takes a `pin_overrides` seam that only the self-test sets, and three
new breaks replace a reader method; disabling the new block lets all three pass.
`--fixtures` output is byte-identical to `7802659`. With this, 58 of the
review's 88 findings are closed and seven in part.

**Battery for the nineteenth change.** All sixteen preflight commands passed
on the staged tree, the authorization self-test with 63 breaks, and both forms
of `git diff --check` were clean. The kernel gate exited 0, with 16 implemented
checks passing, 3 unratified and refusing, 2 stubbed and 5 pending.

**Twentieth: the repo scan reads the pair form, Class B, decided under the
grant as renewed at 01:26.** One review finding. RT-15's scan compiled one
pattern per type in the registry's typed string form, while every CLAIM
payload, every subject-authorization record and the gate fixtures' dispatch
write a selector as a `selector_type` beside a `value`, or a
`target_selector_type` beside a `target_selector`. A live record committed in
that shape carried its type and was not found, and the scan's own "did not
reach" notice did not say so. The scan now parses each JSON line, each .json
file and each .yaml file and pairs the two keys within one mapping, never
across a line, because a gate fixture's line also carries
`expect_decision.value` and pairing that with a type elsewhere on the line
would refuse an ordinary word. A mapping key that names a shape-detectable type
is read the same way. The fqdn shape is case-insensitive. The notice names what
the scan still does not reach: a pair quoted in a markdown block or in a file
that does not parse, and a typed value with spaces, quotes or URL encoding
inside it, or one character long. Over the tree the scan reads 482 pairs and
finds nothing, and its summary line now reports the pair count. Four self-test
breaks are new; emptying the pair pass and reverting the fqdn shape lets the
three that refuse pass. With this, 59 of the review's 88 findings are closed and
seven in part.

**Battery for the twentieth change.** All sixteen preflight commands passed on
the staged tree, the retention self-test with 81 breaks, and both forms of `git
diff --check` were clean. The kernel gate exited 0, with 16 implemented checks
passing, 3 unratified and refusing, 2 stubbed and 5 pending.

**Twenty-first: the register is reconciled column by column, Class B, decided
under the grant as renewed at 01:26.** One review finding. A-13 compared the set
of fixture names in `conformance/gate/README.md` section 4 with the corpus and
read nothing else, so rewriting a register row's criterion, decision, step,
basis and code produced no finding and the summary still said reconciled. Each
row's six remaining cells are now read against its fixture and refuse as
`AUTH_REGISTER_ROW_DRIFT`. The register's notation is read as written: "none"
for no value, "held" for a value a held row leaves open, which refuses on a row
nothing holds, and "determinate" for an empty hold. Four Criterion cells were
shortened forms of the fixture's field and now carry it whole; the README
states the notation under the table. Four self-test breaks are new and pass
when the column check is disabled. Nine existing breaks edit a fixture the
register describes without editing the register, so they now also fire A-13's
columns and each says so. `--fixtures` output is byte-identical to `d0b1984`.
With this, 60 of the review's 88 findings are closed and seven in part.

**Battery for the twenty-first change.** All sixteen preflight commands passed
on the staged tree, the authorization self-test with 67 breaks, and both forms
of `git diff --check` were clean. The kernel gate exited 0, with 16 implemented
checks passing, 3 unratified and refusing, 2 stubbed and 5 pending.

**Twenty-second: the checkpoint closeout, at a natural stopping point.** The
handover of 01:26 asked for a closeout at a natural stopping point or a
tactical pause, named as one or the other. This is a natural stopping point.
What remains of the Step 8 review is either reserved to the operator, waits on
the evaluator VA-U1 holds until Step 10, or needs fixture semantics that only a
ratified entry decides; the eight findings an agent can still take are listed
in the handoff's section 5. Since the summary of 01:35, PRs 15 to 18 landed
`7802659`, `4ec9132`, `d0b1984` and `3e54101`, each fast-forwarded after both
CI runs passed on every step. **A count correction.** The running review count
in the seventeenth to twenty-first paragraphs and in the session's reports ran
one high. The review table carries 59 findings closed and eight in part, one
of those the class B half of retention-mechanism:6, a class F finding, plus
twenty open and one, stamped-state:12, the operator's. The paragraphs above
stay as written, and the handoff and the review record carry the corrected
figures.

**Battery for the closeout.** All sixteen preflight commands passed on the
staged tree and both forms of `git diff --check` were clean. The kernel gate
exited 0, with 16 implemented checks passing, 3 unratified and refusing, 2
stubbed and 5 pending.

## 2026-10-01, resumed at 12:24 after the hold, under the grant as renewed.

**The authority this entry acts on.** The maintainer stopped the overnight work
at about 01:56 ("we are actually about to hit usage limits to find a stopping
point and hold") and resumed it at 12:24: "alright, game on. lets get back
after it. Full send, I am back on". Both were relayed by the parent session and
are recorded verbatim in the parent folder's `WORKLOG.md`. This session reads the
resume as lifting the hold and continuing under the grant of 2026-09-30 23:28 as
renewed at the 01:26 handover: stricter-only class B fixes, each on its own
branch and pull request, fast-forwarded only when green. That reading was sent
to the parent at the start so it could be corrected. No class F item, stamp or
rank-1 edit moves without the maintainer's named answer. The tree was found as
the closeout left it: `6decf30` everywhere, clean, one worktree.

This entry could not be added at ten live entries, so the 2026-09-04 entry
"the tense rule becomes a gate" moved to `plainsight_worklog_archive.md` without
edit. No tracked file cites the worklog by line number.

**First: every enforcement entry states whether it exists, Class B.** Two review
findings, doctrine-fidelity-retention:10 and 11. The compiled crossing rule,
`strata.crossing_to_local`, is EG-5's table, and the policy cited RT-1 and RT-2
only; `strata` and `disclosure_export` now cite EG-5, and a comment names RT-18
as the exception EG-5 states. RT-16's reconcile entry in
`connector_floor.enforcement` carried no `present` flag and read as implemented,
while the tool printed on every run that it does not exist. It now says
`present: false`, and `--policy` refuses any enforcement entry that does not
state its presence (`RETENTION_POLICY_ENFORCEMENT_UNSTATED`), RT-16's reconcile
flag that disagrees with `RT16_RECONCILE_WRITTEN` in the tool, and any of
RT-15's four flags that disagrees with the parts measured in the tree
(`RETENTION_POLICY_ENFORCEMENT_MISSTATED`). The RT-15 comparison ran only inside
the self-test before. RT-16 reads pinned versions from the ledger, and RT-10's
six columns carry none; the policy now says so in a note, and the question goes
to the maintainer as plainsight-21 rather than into U-08's wording. Three
self-test breaks are new and pass when the checks are disabled; `--policy`
output is byte-identical to `6decf30`. The review table now carries 61 findings
closed, eight in part, eighteen open and one the operator's, recounted from the
table.

**Battery for the first change.** All sixteen preflight commands passed on the
staged tree, the retention self-test with 84 breaks, and both forms of `git
diff --check` were clean. The kernel gate exited 0, with 16 implemented checks
passing, 3 unratified and refusing, 2 stubbed and 5 pending.

**Second: the authorization schema's bounds and refusing forms are pinned,
Class B.** Three review findings, schema:2, 4 and 6. The schema's governance
block names `tools/validate_authorization.py` as the self-lint that refuses its
drift, and the tool compared the required list, the property names and the
closure and nothing else. Opening `selector_type`'s empty enum would answer
SAS-U1 by edit, replacing `evidence_ref`'s `not {}` with any value would answer
SA-U2 and SA-U11, and dropping `minItems` or `minimum` would admit what SAS-R4
and SS-4 refuse, each with every gate green and, once stamped, still stamped.
`SCHEMA_PINS` now holds seventeen of them by value and refuses a difference as
`AUTH_SCHEMA_BOUND_DRIFT`, each with a generated break; disabling the check lets
all seventeen pass. SAS-R4 reads "Blank is a refusal", and `minLength 1` admitted
a string of spaces, so purpose, authorized_by and the selector value carry a
pattern requiring one character that is not white space, and SAS-R4's reading
says so. SAS-R4's cost sentence said a corpus row carries the empty-selectors
refusal; none does, and it now says what holds instead, that the bound is pinned
in the tool and no row exercises it until something validates a record against
the schema. That validation is schema:1, held with the evaluator, and the
calendar half of schema:6, a date such as the 31st of February, waits on it, so
schema:6 is closed in part. `--fixtures` output is byte-identical to `559ef06`.
Recounted from the review table: 63 closed, nine in part, fifteen open and one
the operator's.

**Battery for the second change.** All sixteen preflight commands passed on the
staged tree, the authorization self-test with 84 breaks, and both forms of `git
diff --check` were clean. The kernel gate exited 0, with 16 implemented checks
passing, 3 unratified and refusing, 2 stubbed and 5 pending.

**Third: A-08 finds a selector shape under any key, Class B.** One review
finding, authorization-mechanism:12. A-08's docstring said it refuses "a
selector-shaped value that is not a bracketed placeholder", and its walk read
only the values of ten selector keys, so an email-shaped string in
`dispatch.motivated_by` or in a row's description passed. A second pass now
reads every string in a row, removes bracketed placeholders, and refuses an
email or E.164 phone shape that remains, as `AUTH_VALUE_NOT_PLACEHOLDER`. Those
two shapes cannot occur by accident in a fixture's prose; a handle or an id is
an ordinary word, so those are still found only under a selector key, and the
docstring now says both. Two self-test breaks are new, assembled at run time so
this tracked file carries no address, and both pass when the second pass is
disabled. `--fixtures` output is byte-identical to `69b182d`. Recounted from the
review table: 64 closed, nine in part, fourteen open and one the operator's.

**Battery for the third change.** All sixteen preflight commands passed on the
staged tree, the authorization self-test with 86 breaks, and both forms of `git
diff --check` were clean. The kernel gate exited 0, with 16 implemented checks
passing, 3 unratified and refusing, 2 stubbed and 5 pending.

**Fourth: the generated policies stop naming an evaluator that does not exist,
Class A.** One review finding, self-description:11. `policy/lineage.yaml`'s two
chain rules carried `evaluated_by: tools/validate_authorization.py at Step 8,
over the composed chain`, `policy/violation-codes.yaml` described the gate
category the same way, and `tools/validate.py`'s header said the chain rules
belong to that tool at Step 8. `--fixtures` grades wire form, enums and the stamp
read and produces no gate decision, and every chain row is held. The sentences
come from `tools/generate_pse.py`, not from `spec/layer-model.yaml`, so the
generator's two sentences were corrected and both files regenerated; the other
three generated artifacts and both corpora are byte-identical, which both
`--check` modes confirm. The header now says that rows in `conformance/gate/`
assert the rules, that the rows are held, and that no tool evaluates a chain
until VA-U1 decides where the evaluator lives and Step 10 delivers it. No rule,
code or fixture changed. Recounted from the review table: 65 closed, nine in
part, thirteen open and one the operator's.

**Battery for the fourth change.** All sixteen preflight commands passed on the
staged tree, both drift checks among them, and both forms of `git diff
--check` were clean. The kernel gate exited 0, with 16 implemented checks
passing, 3 unratified and refusing, 2 stubbed and 5 pending.

**Fifth: the retention policy's last unpinned rules, Class B.** One review
finding, retention-mechanism:1, closed now in full; most of it was closed
overnight by `8bedba1`'s `STRATA_ROWS` and `INVARIANTS` and `b24ae5d`'s
`PINNED_RULES`. Nine compiled values were still read by no tool:
`strata.cassette_rule`'s live-subject stratum 0, persisting stratum 4, capture
targets S2 and N0, and its statement that a cassette cannot satisfy RT-16's
floor; `strata.permanent`; `encryption.per_case_data_key`; and
`full_text_index`'s stratum 1, `per_case` and `shared_across_cases`. Each was
checked against RT-1, RT-2, RT-4 and RT-7 and pinned by value in `PINNED_RULES`,
with a generated break each. Flipping each of the nine in memory, the tool at
`9e17ec9` refused none and this one refuses all nine. **A correction.** The
sixteenth paragraph of the overnight entry says the review's cassette-rule path
does not exist in the policy. It does, under `strata`; that paragraph looked for
it at the top level. It stays as written. `--policy` output is byte-identical to
`9e17ec9`. Recounted from the review table: 66 closed, nine in part, twelve open
and one the operator's, and none of the twelve is work an agent can take alone.

**Battery for the fifth change.** All sixteen preflight commands passed on the
staged tree, the retention self-test with 93 breaks, and both forms of `git
diff --check` were clean. The kernel gate exited 0, with 16 implemented checks
passing, 3 unratified and refusing, 2 stubbed and 5 pending.

**The maintainer's word at 12:37.** Relayed by the parent session and recorded
verbatim in its dispatch record of 2026-09-30, line 58: "you have my grant on
the merges. Demo is 1630 EDT so lets do as much as we possibly can up to it".
The parent's limit with it: from 16:15 local until the demo is over, no test
runs, builds or agents on this workstation. A commit runs the hook's validators,
so the last commit lands before 16:15.

**The second adversarial pass.** The closeout said nothing reviewed PRs 13 to
19. Four lenses ran over PRs 13 to 24, each paired with an Opus 5.5 refuter that
defaults to refuted and must reproduce: retention mechanism on Opus 5.5 in
memory, doctrine fidelity of every pinned value on Fable 5.1 read-only, and
self-description on Sonnet 5.5 read-only, with authorization mechanism to
follow. The record is `REVIEW2.md` in the overnight artifacts folder. Doctrine
fidelity found no pinned value that disagrees with rank 1 and three refusals
that name the wrong criterion, all confirmed. The retention lens found eleven
defects, nine confirmed and two downgraded, none refuted, most of them in this
session's own work of today. The lens created four temporary directories in the
repository root and removed them at once; they were never staged.

**Sixth: the retention enforcement checks keyed and measured, Class B.** RT-15's
table was compared with the measured parts by position and only at length four,
so the canary entry moved first could claim the clause's measurement, and a
fifth entry or a deleted table turned the comparison off; it is now keyed by the
four clauses in `RT15_PART_CLAUSES`, each once. RT-16's reconcile could be
reworded past a substring test, hidden behind a decoy deferral, or deleted with
its block, and the AGENTS.md clause entry was never read; the three entries are
now pinned by key in `RT16_ENFORCEMENT`, with `RT16_CLAUSE_WRITTEN` false, and a
deferral excuses an entry only when it is the whole entry. `rt15_parts` counted
the words "Execution Limits" anywhere, a commented hook line and a commented
manifest field; it now reads the section 4 sentence, an uncommented hook command
not swallowed by `|| true`, and parsed manifests, and the canary part also
needs a manifest validator that requires the field, which does not exist. It
read a manifests/ directory and a non-UTF-8 file into an uncaught traceback, and
now measures them as absent. RT-9 checks 2 and 3 are pinned in both artifacts.
The pins compare type as well as value, so a stratum of `true` refuses. The pair
walk visits each node once, so a self-referential YAML anchor no longer recurses
without end. The halt refusal names RET-R5, U-03 and U-17 where it said RT-11,
and the cassette pins cite RT-1. Twelve self-test breaks and two measured cases
are new. `--policy` and `--repo-scan` output are byte-identical to `78131d7`.

**Battery for the sixth change.** All sixteen preflight commands passed on the
staged tree, the retention self-test with 105 breaks, and both forms of `git
diff --check` were clean. The kernel gate exited 0, with 16 implemented checks
passing, 3 unratified and refusing, 2 stubbed and 5 pending.

**Seventh: the rest of the second review's retention findings, and this
session's records corrected, Class B.** Second-review findings rm2:5, rm2:6,
sd2:3 and sd2:10, and the handoff halves of sd2:1, 2, 6, 7, 12 and 14. **A
correction to the fifth paragraph above.** It and its CHANGELOG entry say the
retention policy's last nine unpinned rules were pinned, and that
retention-mechanism:1 closed in full. Both statements were false: the second
review flipped twenty more compiled rules with `--policy` green. Those
statements stay as written, and this paragraph and the handoff carry the
correction. Twenty-three more rules are now pinned, each checked against RT-1,
RT-2, RT-4, RT-5, RT-8, RT-9, RT-10, RT-13, RT-14, RT-17, RT-18 or the pin of
record. These include RT-17's seven freeze booleans and the ledger's stratum
and subject-value flag. More to the point, "the last" is now a fact a check
holds. `UNPINNED_BY_NAME` names the twenty-eight booleans and strata that remain
unpinned, each because it has not been checked against doctrine by value or
because it states a fact about the tree. `--policy` refuses any compiled boolean
or stratum that is neither pinned nor named, and any named one that no longer
exists, as `RETENTION_POLICY_RULE_UNCLASSIFIED`. The pair reader now:
- reads YAML with every scalar a string, so a phone written by hand is no
  longer an int;
- keeps every value of a repeated key;
- drops a UTF-8 byte-order mark;
- reads the strings in a list;
- reads a `.json` file of JSON lines line by line;
- reads keys in any case.

The handoff's Step 8 sizes are labelled at `0e0c840`, its case count reads 31,
two doctrine items are stated as stamped, its review heading and row are in
the right tense, and its hash note and SAS-U1 sentence are exact. The
second-review findings the refuters refuted or downgraded on the README, the
kernel-gate note and the layer-model comment are left as they stand. The
contract's stale sentence is the operator's (rank 2), and the schema's citation
waits on plainsight-22. Thirty self-test breaks are new. `--policy` and
`--repo-scan` output are byte-identical to `c82ed28`.

**Battery for the seventh change.** All sixteen preflight commands passed on
the staged tree, the retention self-test with 135 breaks, and both forms of
`git diff --check` were clean. The kernel gate exited 0, with 16 implemented
checks passing, 3 unratified and refusing, 2 stubbed and 5 pending.

**Eighth: the second review's authorization findings, Class B.** The
authorization lens on Opus 5.5 found thirteen, and its refuter confirmed all
thirteen and found one more. The changes, by check:
- **A-12.** It flags a reference copied from the baseline that names no event
  in the fixture's own chain. It flags a field copy present in one chain payload
  and absent from the other. It compares each leaf with its type, so true and 1
  differ. It reads an empty list or mapping as a value, so a key holding one
  cannot be added or removed unseen.
- **A-17.** It now refuses a criterion that has a Step 3 row and no dated range
  or row naming it. RT-19 was that case once its item row was removed, and both
  modes passed. That also closes the matched-pair gap: a reader that stamps no
  criterion refuses here. The item 6 reason names the cause.
- **SCHEMA_PINS.** It holds the root type, the three references, the string
  types, and the absence of patternProperties and unevaluatedProperties at the
  root and in a selector. A separate check refuses a selector field beyond
  selector_type and value. Five owners now name SAS-R5 and SAS-R6, not SS-4.
- **A-08.** It reads the raw string, so an address in angle brackets refuses. A
  bracketed placeholder that carries a shape refuses too. The pass also reads
  mapping keys, a phone grouped with spaces or hyphens, and a selector written as
  a number. A number with a 00 prefix is not read, and the docstring says so.
- **A-13.** It keeps every register row and refuses a repeated name as
  `AUTH_REGISTER_NAME_DUPLICATE`.
- **The refuter's extra finding.** A-01's refusals quoted an unexpected key,
  which could print an address in the gate's own output. They now mask a key
  that carries a shape.
- **Docstrings and messages.** The docstring counts nine unreachable codes and
  says that reader defects in the permit direction rest on
  `tools/pin_of_record.py --self-test`. The criterion refusal no longer tells an
  RT id's author that the subject policy compiles it.

Two findings go to the maintainer: the register notation (am2:13) and the
contract's stale evaluator sentence (sd2:11). Thirteen self-test breaks are new,
each one a mutation the refuter showed passed the previous tool. `--fixtures`
output is byte-identical to `53da6ce`.

**Battery for the eighth change.** All sixteen preflight commands passed on the
staged tree, the authorization self-test with 113 breaks, and both forms of
`git diff --check` were clean. The kernel gate exited 0, with 16 implemented
checks passing, 3 unratified and refusing, 2 stubbed and 5 pending.

**Ninth: a third pass over this afternoon's retention fixes, Class B.** Each
review has found holes in the previous round's fixes, so a third lens on Opus
5.5 ran over `c82ed28` and `53da6ce` before the 16:15 stop. It found twelve, and
its refuter confirmed all twelve. Two corrections to the seventh paragraph above
belong here.
- "The last" was still false, because the classification walk skipped lists.
  It now reads list items by index and reads a boolean spelled as a string.
  List items read by a name-keyed check are recognized as read; the rest are
  pinned or named. The case narrative's `survives: false` (RT-13, RT-2) and
  RT-9's cached-read flag in the cadence are among the nine new pins.
  `gate_telemetry.stratum` moves from named to pinned.
- 53da6ce's YAML reader regressed. On a self-referential anchor and on a "<<"
  merge key it read the whole file as nothing, where `c82ed28` read both. On a
  sequence used as a key it crashed, and the crash was reported against the
  wrong file. The reader now builds a mapping before filling it, so an anchor
  constructs. It flattens merge keys at the node level, routes a tagged mapping
  through the same constructor, keeps repeated keys across case variants and
  nested lists, and falls back to the safe loader when its own read fails.

The other fixes:
- RT-15's clause is measured as a rendered, unwithdrawn bullet under a
  level-two "## 4. Execution Limits" heading. HTML comments and fenced blocks
  are stripped first.
- RT-15's hook part is measured as the scan stanza at the start of a line whose
  failure block ends in `exit 1`, with no `exit 0` before it.
- RT-16's code entry must be exactly the U-07 deferral.
- STRATA_ROWS and DURATIONS compare type.
- A recursion in the governed policy is reported as malformed rather than as a
  traceback.
- The self-test's synthetic tree now carries a real section 4 heading with the
  bullet commented out. It measures the canary field by parse, with the
  validator flag set for the case. Its anchor case puts a live pair beside the
  anchor and requires it to be read.

Twenty self-test breaks are new, each a mutation the refuter showed passed the
previous tool, and one measured case is new and two are reworked. `--policy` and `--repo-scan` output are byte-identical
to `9fad18e`.

**Battery for the ninth change.** All sixteen preflight commands passed on the
staged tree, the retention self-test with 155 breaks, and both forms of `git
diff --check` were clean. The kernel gate exited 0, with 16 implemented checks
passing, 3 unratified and refusing, 2 stubbed and 5 pending.

**Tenth: the third pass over the authorization fixes and the records, Class B.**
Two more lenses ran before the stop: the authorization fixes of `9fad18e` on
Opus 5.5, in memory, and the records of PRs 25 to 27 on Sonnet 5.5, read-only.
Each was paired with an Opus 5.5 refuter. The authorization lens found eleven,
ten confirmed and one downgraded; the records lens found sixteen, fifteen
confirmed and one downgraded. **Corrections to the eighth paragraph above, and
to records of this afternoon, left as written where they stand:**
- the eighth paragraph says thirteen self-test breaks were new; twenty-seven
  were, fourteen of them generated by the new schema pins;
- its CHANGELOG entry counts fourteen findings decided; seventeen were;
- the sixth paragraph says a non-UTF-8 file now measures as absent; it is
  decoded with replacement and measured by its text, and only a directory or
  an unreadable path measures as absent;
- the second-pass paragraph says the retention lens found eleven defects; it
  found eleven findings, seven of them defects.

What changed:
- **Masking at the source.** "A refusal no longer echoes a shaped key" was true
  of A-01 alone: an undeclared record field, a pending id, a register cell and
  an SS-5 delta could still print an address, and the gate log would have kept
  it with "@" turned into ".". Every Finding now passes its where, what and
  moves through `_masked_text`. The self-test fails any break whose refusal
  prints an email or phone shape; with the masking removed, the two new leak
  breaks fail.
- **Whole selector nodes.** Pinning keywords one by one missed `prefixItems`,
  which in draft 2020-12 takes `selectors[0]` out of the selector's closure and
  SAS-U1's empty enum. `SCHEMA_NODE_PINS` holds `properties.selectors` and
  `$defs.selector` whole, comments stripped at every depth.
- **A-08.** A record selector must be an object of exactly selector_type and
  value. A mapping, or a list of non-strings, under a selector key refuses. A
  value under a selector key must be a typed placeholder `<type:label>`, which
  every corpus value already is; `conformance/gate/README.md` section 5 now
  states that rule. The phone shape reads dots, slashes and parentheses, and a
  percent-encoded address is read.
- **Crashes.** A chain that is not a list, and selector properties that are not
  a mapping, are named refusals rather than tracebacks.
- **The register.** The two register breaks edit the register's text and parse
  it again, so they test the parser. A row indented by up to three spaces is
  read.
- **Prose.** A pin that requires a key to be absent says so, and the item 6
  reason reads plainly. The docstring counts ten unreachable codes, adding
  AUTH_MODES_COMBINED, and states the 00-prefix limit. The root type's owner is
  the closed record of SS-4 and A-10.
- **The retention tool's comments.** The cassette pins cite RT-1, the
  PINNED_RULES comments sit over the entries they describe, the
  UNPINNED_BY_NAME comment counts forty-eight, and the `selector_pairs`
  docstring states the `.json` fallback.

`--fixtures` output is byte-identical to `23d041a`. No further pass ran on
this commit or on `23d041a` before the stop, which the closeout states.

**Battery for the tenth change.** All sixteen preflight commands passed on the
staged tree, the authorization self-test with 124 breaks and the retention
self-test with 155, and both forms of `git diff --check` were clean. The kernel
gate exited 0, with 16 implemented checks passing, 3 unratified and refusing, 2
stubbed and 5 pending.

**Eleventh: the fourth pass, and the checkpoint closeout before the 16:15 stop,
Class B.** One combined lens on Opus 5.5 ran over `23d041a` and `46beb98`; it
found twelve. Its refuter ran as a one-agent workflow under the ultracode
setting the operator turned on, and confirmed eleven and downgraded one (f4:3).
Eight are closed here:
- **f4:1.** The indexed survivability and cadence pins now name their item, so
  swapping two labels refuses.
- **f4:2.** A self-referential sequence anchor sent the whole file to the safe
  reader. Sequences now build lazily, and a file only the safe reader can read
  refuses rather than being read under its weaker semantics.
- **f4:3.** A merged value overridden by an explicit one is kept as a repeat.
- **f4:5.** A record written as a list, selectors written as a string, and a
  selector type outside the registry refuse.
- **f4:6, in part.** An undeclared field name and a pending id outside the id
  grammar are no longer printed, and the phone shape reads any space or dash.
- **f4:8 and f4:9.** Each now has a break of its own: the whole-node pins are
  the only check that refuses a selectors node given its own $id and $defs, and
  a live pair beside a sequence key is read only because of the hash guard.
- **f4:12.** Every YAML 1.1 boolean spelling is a leaf. That surfaced RT-1's
  text "No" in the skeleton row, which is now named as unpinned.

**Open, for the next session**, each confirmed and recorded in `REVIEW2.md`:
- **f4:4.** A typed placeholder's label is not yet bound to a cast id.
- **f4:7.** RT-15's clause and hook measures still miss a tilde fence and a
  never-taken conditional.
- **f4:10.** A register row without its leading pipe is not read.
- **f4:11.** The pair scan does not read a value nested in a mapping.
- **f4:6, the other half.** The register-drift and certification texts can
  still quote a pending id.

**This commit is the checkpoint closeout.** The pattern held at every round:
each pass found holes in the previous round's fixes, one of them a regression.
This last commit, reviewed by nobody, is therefore the one most likely to hold
a defect. `--policy`, `--repo-scan` and `--fixtures` output are
byte-identical to `46beb98`.

**Battery for the closeout.** All sixteen preflight commands passed on the
staged tree, the authorization self-test with 129 breaks and the retention
self-test with 163, and both forms of `git diff --check` were clean. The kernel
gate exited 0, with 16 implemented checks passing, 3 unratified and refusing, 2
stubbed and 5 pending.

## 2026-10-02, morning, under the maintainer's words of 10:14.

The maintainer at 10:14 EDT, in the parent session, as the parent relayed it and
recorded it in its own records: "same deal as before, I am stepping for a bit so
go ahead and orchestrate the other sessions and get their work items complete.
If they complete all their work items (whether that be all of them or all they
can do without need for my direct input) before I get back, go ahead and have
that session run a full closeout checkpoint. ZMeta is final authority of Zmeta
stuff, you have the conn". The parent's list for this session: one review pass
over `77fe6da`, the fourth review's open findings, Step 7's owed review and the
next telemetry review where neither needs a stamp, a queue item for anything
that needs him, and a closeout checkpoint.

**The review record repaired.** On 2026-10-01 a helper that set refuter verdicts
in `REVIEW2.md`, beside the overnight records, wrote the verdict into the
finding column of 28 rows. The finding texts were restored from the session
transcript, and the verdicts moved to their own column.

**The fifth pass, over `77fe6da`.** One lens on Opus 5.5 ran the checks in
memory with telemetry off and found ten. Its refuter on Opus 5.5 confirmed nine
and downgraded one: r5:1, an unpinned rule rewritten as the string "no", is a
note, because flipping those rules to true is accepted by design and no Python
reader consumes them. For about one minute at 10:30 the main checkout's
`tools/validate_authorization.py` held an unreviewed draft of this change,
written there in error while the lens was running. It was restored, the lens
was told and re-ran every authorization result from the `77fe6da` blob with a
hash check, and the drafting moved to a separate worktree.

**One claim of `77fe6da` was false.** Its commit message, its CHANGELOG entry and
the eleventh paragraph of the 2026-10-01 entry say the phone shape reads any
space or dash. It read seven of the 28 characters Unicode files as a dash or a
minus sign, and a phone separated by U+2212, U+FF0D or U+FE63 passed A-08 (r5:5).
It now reads all 28.

**What this commit closes**, each with a break that the code at `77fe6da`
lets pass:
- **f4:4.** A typed placeholder is one of the tokens `synthetic/GROUND_TRUTH.yaml`
  carries as a value, or the corpus-local token README section 5 names.
- **f4:6, the rest, with r5:3 and r5:4.** A refusal prints a key, a pending id,
  a register cell or a fixture value only when a vocabulary the gate reads holds
  it: the two schemas, the layer model, the row contract or the code and enum
  vocabularies. The self-test plants a word in no vocabulary and fails any break
  whose refusal, certification refusal included, prints it.
- **f4:7.** The clause measure removes tilde fences and a comment or fence left
  open, and reads a withdrawal anywhere in section 4. The hook measure is
  described under the sixth pass below, in the form this commit carries.
- **f4:10.** The register is read as GitHub renders its table, and a row with no
  fixture name is refused as `AUTH_REGISTER_ROW_UNNAMED`.
- **f4:11.** A pair's value is read inside a mapping, as a key, in a set and
  without its padding.
- **r5:1 and r5:8.** A rule leaf is written as a boolean, refused otherwise as
  `RETENTION_POLICY_RULE_NOT_A_BOOLEAN`, and a 0 or 1 is a leaf. Five such
  values are not rules and are named with their types.
- **r5:2.** The six cadence steps are pinned by when, and the sweep by its act.
- **r5:6 and r5:7.** An empty selector registry refuses every record selector,
  and a registry key that is not a string is a named refusal.
- **r5:9.** A scan row whose sample cannot be read fails as that row rather than
  ending the self-test.
- **r5:10.** The handoff now says that `77fe6da` left half of f4:6 open.

**The sixth pass, over the first version of these fixes, before any merge.**
One lens on Opus 5.5 ran over the staged change and found nineteen, two of them
regressions against `77fe6da`. Its refuter on Opus 5.5 ran over the same staged
tree, which nobody edited while it worked; the drafting moved to a second
worktree. Closed here:
- **r6:1, a regression, with r6:2, r6:3 and r6:15.** The first shell-aware hook
  measure accepted an exit 0 inside an always-true if or a called function
  before the stanza, and exit 256, exit 1 & and exit 1 | cat in its block, all
  of which the line test of `77fe6da` refused. The measure now walks every word
  in command position. Before the stanza it refuses an exit with any status but
  a literal 1 to 255, any exit at the top level, exec, trap, alias, hash, eval,
  source, a PATH assignment, a function named python, and a command named
  through quotes or an escape. In the block it refuses exec, return and any
  other exit status, and it counts an exit only when nothing pipes or
  backgrounds it. It also refuses a shebang whose interpreter is not a shell and
  reads a here-document opened with an escaped or digit delimiter. Fifteen
  measure cases were added, one of them guarding the exec rule.
- **r6:4, a regression.** The first GitHub-style register reader skipped a
  contradicting row written as a second table's header, after a line opening
  with HTML, or alone after a blank line, all of which `77fe6da` read. Every
  line the earlier reader took as a row is now read as well, so this reader
  reads a superset of what it read.
- **r6:6 and r6:7.** A-18 no longer prints a fixture's decision value, step or
  absent criterion, and A-12 names a key path only from the key vocabulary.
- **r6:9 and r6:10.** The phone shape reads the soft hyphen, the zero-width
  space and joiners, the byte-order mark, middle dots, fullwidth and
  ideographic stops, parentheses and slash, and a fullwidth plus. The pair scan drops format
  characters from a value before matching it.
- **r6:11.** Every cadence step is pinned by its act as well as its when.
- **r6:16.** The withdrawal phrases gain eight more; the list stays closed.
- **r6:19.** A measure case that cannot find its anchor is a named failure
  rather than a traceback.
- **r6:12, r6:13 and r6:17.** The telemetry review's count of merges, the
  description of the hook measure, and the handoff's account of this review are
  corrected below and in the handoff.

**Open from the sixth pass**, each recorded in `REVIEW2.md`:
- **r6:5.** `tools/validate_cast.py --placeholder-scan` accepts any bracketed
  text under a persona key, so a live handle written as a typed token in the
  truth file would pass it and be admitted as a cast token.
- **r6:8.** A fixture or register name is printed in refusals and written to the
  gate log. A name is how a reader finds the row, so masking it is a trade the
  operator may want to weigh.
- **r6:14.** A cast token of the wrong type for its key is accepted.
- **r6:18.** In a chain payload, a capitalised pair key or a registry type
  outside SELECTOR_KEYS is not read by A-08, as at `77fe6da`.
- **r6:4's other half and r6:11's.** A register table inside a blockquote
  is not read, and a seventh cadence step is not refused.

**The seventh pass, over the sixth pass's fixes, before any merge.** One lens on
Opus 5.5 read the delta and found twenty, six of them regressions. Four were in
the shell-aware hook measure: a "<<" in a comment or an arithmetic shift read as
a here-document, a closing brace piped or backgrounded, a here-document body the
shell runs, and a second stanza. The fifth was the alias form the sixth version
dropped from SHADOWS_PYTHON_RE. The last was a fullwidth plus added to the phone
lookbehind, which hid a phone `77fe6da` found. The parent's rule stops a round
where its fixes would go unreviewed, so the regressions were backed out rather
than fixed with new logic. The hook measure now also requires the line test of
`77fe6da`, restored verbatim as `_stanza_lines_in_place`, so whatever either
refuses is refused. The alias alternative and the lookbehind of the earlier
versions are restored. Each regression shape was then checked and refused, and
two measure cases that only the line test refuses guard the composition. The
condition that counted a block's exit only as the first word of its command
guarded nothing a defect needs and was dropped. Seven rules the lens found
unguarded each gained a case or a break: return and a quoted name in the block,
eval, source and "." before the stanza, the digit-led delimiter, A-18's value
and step, and the fullwidth plus. These last changes were checked by the
self-tests and by hand, and no eighth pass reviewed them. The refuter's verdicts
are in `REVIEW2.md`.

**Open from the seventh pass**, r7:7 to r7:17: a wrapper such as command or
builtin, or an assignment or redirection prefix, hides an exit before the
stanza; trap or eval in the block; an exit continued from the line before or
inside a subshell; set -n and a shebang flag; a quoted PATH assignment; a
here-document delimiter with a space; a subshell around the stanza; a "#" after
a brace; invisible characters outside category Cf in the pair scan; and the
bidirectional and other format characters PHONE_STOPS does not list. The hook
measure reads a shell script with a line reader, and every pass has found more
that it misses. It is a stricter heuristic than the line test it extends, and it
is not a shell parser.

**A false positive caught before the commit.** The first draft of f4:11 read
into mappings on both sides of a pair and under keys named for a type. The
working-tree scan then refused `ontology/selectors.yaml` and
`schema/pse-event-0.1.schema.json`, which write each type as a key over its
definition and write selector_type as a schema property. The type side and
type-named keys now read strings and lists only, which the pair-scan docstring
states, and `--repo-scan` output is byte-identical to `77fe6da`.

**The second telemetry review, under HY-2.** The first review read records 1 to
4,078. This one reads the 1,430 records written after it, from
2026-10-01T03:50Z to 18:36Z, and leaves out records 4,079 to 4,099, the 21 a
mistaken test run wrote that night. The window covers the 28 pull requests,
#2 to #29, merged in it.
- `authorization`, 50 runs, every one refused, with `AUTH_ARTIFACT_UNSTAMPED`
  seven times a run. HY-2's second row, accepted for its stated reason: the
  artifacts carry no dated row and a stamp clears it. The third row does not
  apply, since the code is one rule read once for each of seven paths. Kept.
- `retention-policy`, 45 runs, and `retention-shred-roundtrip`, 31 runs, every
  one refused by design. `RETENTION_POLICY_RULE_UNCLASSIFIED` fired twice while
  rules were being named, each a real catch answered in the same change. Kept.
- `authorization-self-test`, 115 runs and 12 refusals, each a break drafted
  that day that failed until its claim was corrected, before any commit. Kept.
- `hygiene`, 103 runs and two refusals, both `HYGIENE_CADENCE_OPENER` on a
  worklog sentence and both answered. HY-2's fourth row. Kept.
- `cast`, `cast-self-test`, `doctrine`, `layer-model` and `ontology`, 91 runs
  each, and the two repo-scan modes, 41 and 60 runs, with no refusal. HY-2's
  first row asks for a deliberate break, and each gate's self-test breaks it on
  every hook, preflight, kernel-gate and CI run. Kept.

**One gap the review found.** Six self-tests, those of the layer model, the
ontology, hygiene, retention, doctrine and the pin-of-record reader, run on
every path and write no record. Only the authorization and cast self-tests do.
The log therefore cannot show the deliberate breaks that HY-2's first row rests
on for five gates with no refusal. Recording them is Class B work and is open.
HY-2's basis stamp stays the operator's.

**Battery.** All sixteen preflight commands passed on the staged tree, the
authorization self-test with 147 breaks and the retention self-test with 184,
and both forms of `git diff --check` were clean. The kernel gate exited 0, with
16 implemented checks passing, 3 unratified and refusing, 2 stubbed and 5
pending.

---

## 2026-10-12, six false passages corrected and two delegations recorded, under the maintainer's words of 17:02.

**Class:** A (`README.md`, `docs/THE-GAMEPLAN.md`, the handoff and the two
process records). No doctrine, spec, schema, policy, ontology, runtime or other
governed artifact changed, so `CHANGELOG.md` takes no entry.

**The words this commit acts on.** The maintainer at 17:02:01 EDT on
2026-10-12, in the personal-account parent-folder session: "go ahead and make
sure everything needing to be finished is taken care of so we are moving forward
cleanly. Any commits, merges and pushes along with finishing up any threads on
work that was in swing then lets engage the weeks efforts". That session,
`local_ac773541`, relayed them here at about 19:52, after a messaging limit held
the copy, and they are verbatim in the parent's
`research/inputs/dispatches_2026-09-30/decisions_queue_2026-10-01.md`. The relay
meets the four tests the delegations below set. This session read "in swing" as
the corrections the two harvests found, which waited only on a commit, the one
this commit's own reading found, the queue brought level, and the two
delegations no commit had carried. The Step 7 fixes, plan item 0.7 and the queue
answers were never started, and they stay held.

**Two delegations, recorded here because no commit had carried them.** Each
names a parent-folder session whose relays of the maintainer's dated words are
his word in this repository, as the 2026-09-30 overnight entry records for the
sentences of 2026-09-28 and 2026-09-30.

- Typed at 23:17:08 EDT on 2026-10-05 in the team-account PLAINSIGHT session:
  "Delegation, 2026-10-05: the team-account parent-folder session
  local_5f1148fb-244a-4c91-b2ca-8c1b812c21f5 (titled "Harvest closed ecosystem
  project session") is my parent session for this repository and for this
  project from today and going forward; a decision it relays with my dated words
  quoted is my word here, the same as my sentences of 2026-09-28 and 2026-09-30;
  anything that pushes, merges, deploys, deletes or mints still names the words
  it acts on; record this in your notes."
- Typed at 15:30:56 EDT on 2026-10-11 in the personal-account PLAINSIGHT session:
  "Delegation, 2026-10-11: the personal-account parent-folder session
  local_ac773541-f864-4080-900a-f80fea7aaa5d (titled "Ecosystem project") is my
  parent session for this repository and for this project from today and going
  forward, in place of the team-account parent session
  local_5f1148fb-244a-4c91-b2ca-8c1b812c21f5 while I work on this account; a
  decision it relays with my dated words quoted is my word here, the same as my
  sentences of 2026-09-28, 2026-09-30 and 2026-10-05; anything that pushes,
  merges, deploys, deletes or mints still names the words it acts on; record
  this in your notes."

A relay qualifies only when it comes from the named session, quotes his dated
words, those words are found verbatim in the parent folder's records, and the
act falls inside them. It reaches no Class F decision and no stamp, which stay
his own hand per item. The session's reading of "in place of ... while I work on
this account", labelled as a reading: while he works on the personal account, a
relay from the team parent is held and he is asked first.

**Between 2026-10-02 and this commit, nothing touched the tree.**

- On 2026-10-05 the team-account session harvested the closed personal session
  `f8d7cd3b`, in `Z-ISR/_session-artifacts/2026-10-05-plainsight-harvest-of-f8d7cd3b/`.
  It found four of the six passages below, one confirmed class F review finding
  with no queue item (rm2:9, drafted as plainsight-28), and one held finding
  missing from plainsight-22's Blocks line (sd2:13).
- From 2026-10-06 to 2026-10-09 that session stood by under relayed words that
  asked for no act here, and closed out on 2026-10-09 at 20:06 as report 13.
- On 2026-10-11 the personal-account session harvested it, in
  `.../2026-10-11-plainsight-harvest-of-12c08cc1/`: four Sonnet 5.5 readers, four
  Opus 5.5 refuters and an Opus 5.5 critic, 70 items, none refuted. It found the
  Resume here passage, item 3 below, and that the parent had put plainsight-28
  into its answer sheet on 2026-10-05.
- At 15:45:56 EDT on 2026-10-11 the maintainer's "maintain direction till map is
  done" held this repository while the COP's map work ran.

**What this commit corrects**, each false at `064fa27`:

1. The handoff's section 1 said Step 7's owed review was never run. It ran on
   2026-10-02, and `STEP7_REVIEW.md` in the overnight folder records it.
2. The handoff's section 5 said no second pass had read the generator against
   the model. That is the same review: twenty findings, eighteen confirmed and
   two downgraded, all open.
3. The handoff's Resume here named Step 8's open class B findings as the next
   work, while its own section 5 said all twelve wait on the maintainer's queue
   or on Step 10. It now names the queue and the held agent work.
4. The handoff's section 7 said `main` is the only branch that goes to `origin`.
   Every pull request since 2026-09-30 pushed its branch there, and the 31
   merged branches remain. This commit's own reading found it.
5. `docs/THE-GAMEPLAN.md` Step 8 said no adversarial review has run. It ran on
   2026-10-01.
6. `README.md`'s Next action said the next work, as of 2026-09-30, was the
   review Step 8 was owed.

The handoff stays at its 400-line cap. Section 5's Step 8 paragraph lost its
ragged line breaks and its sentence on method, which the 2026-09-30 overnight
entry carries, and section 6 gained the overnight folder and the two harvests.

**Outside the tree, as part of the same act.** The session-artifact queue,
`MAINTAINER_QUEUE.md` in the overnight folder, gains plainsight-28 in full, and
plainsight-22's Blocks line reads "rm2:8 and sd2:13", matching the parent's
answer sheet of 2026-10-05. The queue holds 28 items, and none is answered.

**Two notes from the parent, checked against this tree.** The parent's TMN
instance design of 2026-10-12 uses "managed attribution" for an instance's
disposable outward identity; the term appeared nowhere in this repository at
`064fa27`. The
design reuses this repository's shred verification as a pattern only, and
nothing crosses between the two. This repository's isolated collection
environment is ISOLATED in `doctrine/EGRESS.md`. The doctrine never calls it a
DMZ, and the handoff's "DMZ compartment" is the 2026-09-02 design that ISOLATED
inherits, not ZMeta's admission DMZ. CR-7's burn retires one credential, not an
instance.

**Battery.** All sixteen preflight commands passed on the staged tree, the
authorization self-test with 147 breaks and the retention self-test with 184,
and both forms of `git diff --check` were clean. The kernel gate exited 0, with
16 implemented checks passing, 3 unratified and refusing, 2 stubbed and 5
pending.

**Open.** Unchanged from `064fa27`. Every item waits on the maintainer's words
for that act: the 28 queue items, plan item 0.7, the Step 7 fixes and the rest
of the held agent work the handoff's Resume here lists. The 31 merged branches
stay on `origin` and in this checkout; deleting them needs his words naming that
act.

---

## 2026-10-18, the standing words of 2026-10-16 and 2026-10-17 recorded, under the maintainer's words of 2026-10-18.

**Class:** A (the handoff, this record and its archive). No doctrine, spec,
schema, policy, ontology, runtime or other governed artifact changed, so
`CHANGELOG.md` takes no entry.

**The words this entry acts on.** The maintainer at 15:23:29 EDT on 2026-10-18,
first-hand in the personal-account PLAINSIGHT session: "Draft the records
commit now: the worklog entry with the 2026-10-16 delegation, the ZMeta rule,
the negative-control rule, the order of work and the credentials plan, plus the
line-neutral handoff edit. Do not commit or push until I say so." The draft is
this entry, the archive move under the ten-entry cap, and the handoff edit. The
commit is his separate word for that act, and the paragraph after the battery
records it when it is given.

**The delegation of 2026-10-16, recorded because no commit had carried it.**
Typed at 00:08:36 EDT on 2026-10-16 in the team-account PLAINSIGHT session:
"Delegation, 2026-10-16: the team-account parent-folder session
local_305e02ed-244e-4017-b953-57f2e469985c (titled "Ecosystem Project") is my
parent session for this repository and for this project from today and going
forward; a decision it relays with my dated words quoted is my word here, the
same as my sentences of 2026-10-05 and 2026-10-11; anything that pushes, merges,
deploys, deletes or mints still names the words it acts on; record this in your
notes." A relay qualifies on the four tests the 2026-10-12 entry states: it
comes from the named session, quotes his dated words, those words are found
verbatim in the parent folder's records, and the act falls inside them. The
session's reading of the two live parents, labelled as a reading: while he works
on the team account, a relay from the personal parent of 2026-10-11 is held and
he is asked first, the mirror of that delegation's own clause. On 2026-10-18 he
archived the personal parent of 2026-10-11 and opened a new personal parent,
which he named for reporting and did not delegate, so on the personal account
every act takes his own words in the PLAINSIGHT chat; the team parent reached
its weekly limit at 00:02 EDT on 2026-10-18 and runs again after the reset of
2026-10-19 at noon. Words he types in the PLAINSIGHT chat outrank a relay that
differs, and the conflict goes to him: the TAK plane session applied that on
2026-10-17 when a relay's clause conflicted with his words in its chat, and the
team parent accepted the reading.

**The ZMeta rule, 00:17:30 EDT on 2026-10-16.** Typed in the team parent's chat,
relayed to the team PLAINSIGHT session at 00:19 as information only, and
verbatim in the parent folder's
`research/inputs/dispatches_2026-09-30/decisions_queue_2026-10-01.md` under its
00:18 heading. His words, after the model words that open the message: "Also,
as stated before but ZMeta is the most important repo of any of the repos as it
is the data foundation for the entire project so its integrity needs to be
maintained no matter what and its foundational semantics must not be changed
unless substantial evidence is presented. Stuff like new adapters and fixing
current adapters and other things that do not damage the canonical schema or
its tools that check conformance, mutations etc can be touched a bit more
freely but that core semantics, canonical schema and all the tools that
validate zmeta must be maintained explicitly based off the documentation
written to define it. ZMeta is the ultimate authority when it comes to zmeta
related work. Make sure anything touching the standard or tools for validation
go through me first." What it reaches here, measured on 2026-10-16 and again on
2026-10-18: no tool in this repository writes into ZMeta's; the ZMeta mentions
in `tools/`, `policy/` and `spec/` are comments and citations; no queue item,
Step 7 finding or open review row touches ZMeta's standard; and PSE is a private
dialect that never claims upstream compatibility (`CLAUDE.md` section 1), so
its validators are its own and take his word under this repository's authority
order, which is also the team parent's standing reading since 09:54 on
2026-10-16. A change this repository ever wants upstream is a request to him
through the ZMeta session and never an edit from here. The message opened with
model words: he set the team parent, ZMeta and the COP to Mythos 5.1 and kept
model diversity; the parent's relay said this repository's main loop and agent
split were unchanged.

**The hard rule on negative controls, 01:09:06 EDT on 2026-10-16.** Typed in
the parent's chat and verbatim in the decisions record: "dont forget the hard
rule of nothing counts until its negative control has seen failing because a
positive test is no good if a negative test does not also pass, or more
appropriately fail". The parent carries it into every brief and report as a
standing rule for every check in every repository: a check is green only when
its positive condition passed and its negative control has been observed to
fail, and a check without a runnable control is marked so and does not count as
green. Gate 1 of `CLAUDE.md` section 3 already requires every constraint to be
covered by a test that fails when the constraint is removed, and the validator
self-tests record 147 and 184 breaks. What the rule adds here: every report
that calls a check green names the control seen failing, and the kernel gate's
sixteen implemented and passing entries are owed an audit that lists, per
entry, the control that was seen to fail and marks the rest as not counted
green. That audit ran as its own session on 2026-10-18, started on his click at
about 15:23 EDT and finished by 15:56: every one of the sixteen implemented
entries was seen failing under a control run in a clone, eight of them for the
first time on any record (the cast, ontology, schema and telemetry gate entries
and the doctrine, pin-of-record, hygiene and ontology self-tests had only ever
been seen passing); an Opus 5.5 refuter re-ran all 26 controls and confirmed 24,
and the two it qualified or refuted were re-run with its corrections. It also
found that the aggregator cannot tell a crash in an unratified mode from the
designed refusal, a finding for the maintainer and not acted on. Its record is
`Z-ISR/_session-artifacts/2026-10-18-plainsight-negative-control-audit/AUDIT.md`
with the forty run logs beside it; it is outside this commit and changed no
file.

**The order of work, 00:36:57 EDT on 2026-10-16.** Typed in the parent's chat
and verbatim in the decisions record under its 00:38 heading: "lets make sure
we have a fully built out TMN and we agree on before we then worry about the
quick deploy and tear down, but that is my end goal for this current work
effort is to fully establish a TMN in the cloud that can also be operated
completely on edge hardware like laptops and phones and Pi's and protectli's
etc that can be deployed with one script (with all your accounts like VM's and
Cloudflare assumed to be logged in and connected for the stuff to deploy onto),
configured any way an edge operator would want, and then torn down with one
script as well. It needs to be simple and easy and quick and a solid and fully
functional default so tweaking isn't too much work either. That is what I want
up, then we can work the zisr cop UI/UX redesign based off the deep research
pass and then I want to dive into plainsight and actually get that OSINT "COP"
up in a domain that connects to VM's to run everything and a nice social web
interface to control it all and visualize all the collected data, as well as
work the zmeta dialect for OSINT normalization." This repository is fourth: a
TMN "we agree on", the one-script deploy and tear-down, the COP redesign, then
PLAINSIGHT. The parent's TMN definition adds "validated" and "he opens it" as
gates and says this session holds with its queue; those are the parent's gates,
labelled here as such. His sentence names four pieces that each have a home in
this tree: a domain, which is the deployment; VMs that run the collection, which
is ISOLATED in `doctrine/EGRESS.md` and `doctrine/CREDENTIAL_LIFECYCLE.md`; a
social web interface to control and visualize, which is SS-16's web map and the
usable-hub plan of Steps 10 to 12; and the ZMeta dialect, which is PSE. Nothing
in it widens who may be a subject. The hold of 2026-10-11 ("6. maintain
direction till map is done") stands on its own terms as well: the COP's map
merged its M10 increment on 2026-10-16 and holds at M10 until the TMN is
validated, and its promotion to the project domain on 2026-10-18 is not his mark
on the map. His words of 2026-10-17 tighten the hold. At 19:00:39 EDT: "I
concur: when the Status increment merges and the plane's third control lands,
every session holds and I will give the word for the credentials session." At
19:11:09: "once the checkpoints finish, lets hold and knock out this
presentation stuff with the remaining usage we have since we should have just
enough to take care of this before the refresh in a day and a half anyways". No
word since 2026-10-13 answers a queue item or releases plan item 0.7 or any held
agent work.

**The credentials plan, 23:12:04 EDT on 2026-10-16.** Typed in the parent's chat
and verbatim in the decisions record: "one thing I would like to do is set up
all my logins and authentications into stuff like my Git, Cloudflare and Digital
Ocean environments on that Kingston drive and encrypt it so in order for you to
log into my stuff, the drive has to be plugged in and mounted. We did an initial
mapping of where all my authentication stuff is like keys and logins, but I
would actually like to work that as a dedicated session. We will keep working
this stuff till we get to a good checkpoint, but then I would like to remap
where everything is within all the different sessions and go ahead and just
knock that out at some point". At 23:16:03 he set the procedure: the parent
names a checkpoint, he concurs or defers, and the session starts on his word.
The parent's prepared brief asks every repository session for a names-only
inventory of the credentials it uses, where each lives and which tool reads it,
with the negative control that the tool fails when the drive is absent. This
repository's inventory, names only, measured 2026-10-18: the GitHub CLI's token
for the account that owns the public remote, in the Windows keyring, read by
`gh`; Git Credential Manager in the Windows credential store, read by `git` for
https pushes to `origin`; CI's default read-only token. Nothing else exists on
the workstation, because CR-4 and EG-4 keep every collection credential in
ISOLATED only, no cast is sealed and no persona exists. Both live credentials
sit in a store the brief says cannot be moved without exposing values, so the
drive-out control is not designed for an in-place store, and rotate-or-move is
his choice. No value is written anywhere.

**Between 2026-10-12 and this entry, nothing touched the tree.**

- On 2026-10-15 the team-account session harvested the personal session
  `b994d03c`, in
  `Z-ISR/_session-artifacts/2026-10-15-plainsight-harvest-of-b994d03c/`: three
  Sonnet 5.5 readers, three Opus 5.5 refuters and an Opus 5.5 critic, 104 items,
  86 confirmed, 16 qualified, 2 refuted. It found that session's closeout
  stamped at 20:55 for a report written at 20:51:37, and nothing after it; its
  section 5 orders the queue by what each item blocks. Problem, recorded there:
  it ran three agents at once while the parent's harvest ran three, against the
  estate cap of three; the fix is one agent at a time, or a slot from the
  parent. The delegation above was typed in that session's chat, and the ZMeta
  rule was relayed to it there.
- On 2026-10-18 the personal-account session harvested that session and the
  team parent since 2026-10-16, in
  `.../2026-10-18-plainsight-harvest-of-b4c6ae3c/`: four Sonnet 5.5 readers,
  four Opus 5.5 refuters, an Opus 5.5 critic and a Haiku 5.5 formatter, one
  agent at a time, 140 items, 89 confirmed, 49 qualified, 2 refuted, with Fable
  5.1 in the main loop. Every decision-bearing word he typed in the parent since
  2026-10-16 is verbatim in the decisions record. The 2026-10-15 record's own
  stamps ran ahead of its clock (18:25 and about 18:26 for a send made at
  18:18:36), and dated notes now say so there, in the overnight queue's header
  (main is `bf6d5d4`, not `064fa27`) and in `REPORTS.md`. The team account hit
  its weekly limit at 00:02 EDT on 2026-10-18.

**The handoff** is brought level with this entry at its 400-line cap: the Date
paragraph and section 0 describe this commit; Resume here states the hold and
what waits; section 6 adds the two harvest folders; section 7 adds the order of
2026-10-16, the negative-control rule and the relay rule, and five lines of
section 0 were shortened to make room.

**Battery, run on the staged tree, finished at 15:33 EDT on 2026-10-18.** All sixteen
preflight commands passed, the authorization self-test with 147 breaks and the
retention self-test with 184, and both forms of `git diff --check` were clean.
The kernel gate exited 0, with 16 implemented checks passing, 3 unratified and
refusing, 2 stubbed and 5 pending, which is the gate's own count; the audit of
the same afternoon saw each of the sixteen fail under its control. The hygiene
gate read this entry and the handoff at their caps. The commit waits on his
word for that act.

**The commit, on his words of 16:06:27 EDT on 2026-10-18**, typed first-hand in
the PLAINSIGHT session: "Commit the staged records draft now as me with no
agent trailer, push it on a records branch, open the pull request, and read
every CI step; report back before any merge." The commit is authored as the
maintainer with no trailer, on a records branch named for the date; the push
and the pull request follow on the same words, and the merge waits on his
further word after every CI step is read.

**Open.** Unchanged from `bf6d5d4`: the 28 queue items, none answered; plan
item 0.7, trimmed to its synthesis step; the Step 7 fixes and the rest of the
held agent work the handoff's Resume here lists; the aggregator finding the
negative-control audit raised, in section 8 of its record; the 32 merged
branches on `origin` and in this checkout, deleted only on his words naming
that act.

---

## 2026-10-23, the records' wording about the 2026-10-18 acts corrected, and the harvest of the personal session recorded, under the maintainer's click of 2026-10-23.

**Class:** A (the handoff, this record and its archive). No doctrine, spec,
schema, policy, ontology, runtime or other governed artifact changed, so
`CHANGELOG.md` takes no entry.

**The words this entry acts on.** The maintainer at 20:19:16 EDT on
2026-10-23, in the team-account PLAINSIGHT session, by his click on the action
the session had offered in its wrap-up, whose message the app delivered cut at
300 characters: "Draft the Class A records commit now: fold in the 2026-10-23
corrections (the four 2026-10-18 messages were clicks on offered actions, 33
merged branches, pointers by name to CLOSEOUT_2026-10-20.md and the 2026-10-22
harvest record), a line-neutral handoff edit, no agent trailer. Do not commit
or pu". The button's message continued "push until I say so", and the cut is
recorded here so the quotation stays what arrived. The session reads a click on
an offered action in this chat as his decision for that act, with the wording
the session's and accepted by him; that reading is his to confirm, since his
message of 20:05 below says words typed, and this entry labels it as a reading
wherever it records a click. The draft is this entry, the archive move under
the ten-entry cap, and the handoff edit. The commit is his separate word for
that act, and the paragraph after the battery records it, and how it arrived,
when it is given. The commit, on that word, is authored as the maintainer
(Incept.IO) with no Co-Authored-By trailer, which CI refuses, whatever the
app's attribution reminder asks.

**The correction this entry carries.** The 2026-10-18 entry above calls the two
messages it records typed, "first-hand" for the draft at 15:23:29 and the
commit at 16:06:27, and the `d51ce06` message and the handoff's Date paragraph
say the same; the out-of-tree records call the merge word at 16:23:15 and the
archive word at 16:32:35 typed too. Each of the four is word for word the
message of a button that session had offered in the wrap-up call just before
it (its transcript at L478, L687, L789 and L838), so he clicked session-authored
text rather than composing it. On the session's reading the acts stand: a
click on an offered action in his chat is his decision for that act, and R6 as
amended asks for his instruction per act; whether a click meets it is his to
confirm, and the commit paragraph below records how his word for this commit
arrives. What changes now is the records' word for how the instruction was
given, and the scope lists in those four messages (the five worklog passages,
"no agent trailer", "read every CI step") are the session's wording that he
accepted. The 2026-10-18 entry is a process record and stays as written; this
entry is the correction. The session's own check
that produced "typed" scanned the user records for the text and never compared
the assistant's button messages, which is where the word entered. The same
entry's Open paragraph counts 32 merged branches; the records branch of
2026-10-18 made 33, so `origin` holds 34 heads, `main` and 33 merged branches,
and this checkout 34 local branches each equal to its origin ref.

**The harvest that found it.** On his words typed in this session at 23:01:22
EDT on 2026-10-22, "refresh yourself, then reach over to my personal account
and harvest the context from the open plainsight session over there and give
me the roll up on what is next. Also, make sure to abide by proper model
diversity and use the right models for the appropriate efforts, so we are
efficiently managing our usage and getting full benefits from the higher
models.", the team-account session read the personal session of 2026-10-18 to
2026-10-20 from disk and compared it with its records. Twelve agents, one at a
time because six sibling sessions had opened in the same five minutes under
the estate cap of three: a Mythos 5.1 probe, which measured for the first time
that a Mythos id works in the workflow tool; four Sonnet 5.5 readers; four Opus
5.5 refuters; an Opus 5.5 critic; one Fable 5.1 judge, the decisive leg, which
read the records independently and reached the same roll-up; a Haiku 5.5
formatter, which declined the 249-row table rather than drop rows, so a script
wrote it. The account hit its five-hour limit at 23:26 EDT by the parent
session's notice, this run was cut at 23:28:48, and it resumed the next
afternoon on his "Try again". Of 249 items, 224 from the readers and 25 added
by the refuters, 147 were confirmed, 74 qualified, 2 refuted and 1 unverified.
The records were complete on substance; the
wording errors found were filed as dated notes out of tree on 2026-10-23: the
clicks above; the personal parent's two titles recorded in reverse order, which
the 2026-10-18 report to that parent had corrected the wrong way round; "of the
31 messages the maintainer typed" counting two usage notices, so 29; "none of
them was relayed to PLAINSIGHT" wrong by one, the ZMeta rule having been relayed
as information on 2026-10-16; the negative-control audit session of 2026-10-18
having run 112 of its 115 assistant records on Fable 5.1 although it was started on Opus 5.5
with a brief that excluded Fable, with its stated window off by about twenty
minutes; and several stamps ahead of the clock, the folder's recurring error.
The record is `Z-ISR/_session-artifacts/2026-10-22-plainsight-harvest-of-dc310f2c/HARVEST.md`,
section 5 the roll-up and section 7 his decision below; its item table and the
workflow's output and journal sit beside it. The closeout record of 2026-10-20,
`Z-ISR/_session-artifacts/2026-10-18-plainsight-harvest-of-b4c6ae3c/CLOSEOUT_2026-10-20.md`,
reports that session's checkpoint of that night: `main` equal to `origin/main`
and GitHub at `d51ce06`, the battery green, no commit because nothing in the
tree had changed and the closeout word had reached it through a parent with no
delegation here. No commit before this one names either file.

**Delegation, and his decision of 2026-10-23.** The team parent his 2026-10-16
delegation names, local_305e02ed, was archived at 22:52 EDT on 2026-10-22, four
minutes before he opened the new team sessions; its last activity is still
00:02 on 2026-10-18, so it never ran after its weekly limit. The new team
parent, local_36039452 ("Ecosystem Project"), is named for reporting by his
opening words to it and by no delegation line; the personal parent of
2026-10-18 was never delegated. Asked whether to type a line naming the new
parent, he answered at about 20:05 EDT on 2026-10-23 by his click on the
offered action "Keep acts here", whose message reads: "Keep every PLAINSIGHT act
on my words typed in this chat; no delegation line for the new team parent for
now." No relay binds in this repository. Every commit, push, merge, archive,
deletion or mint takes his own words in the PLAINSIGHT chat, per act; "for now"
leaves him free to type a delegation line later on the 2026-10-16 pattern.

**The repository between `d51ce06` and this entry.** Nothing touched the tree.
`main` equal to `origin/main` and GitHub at `d51ce06` after fetches at 23:04 on
2026-10-22 and 15:01 on 2026-10-23; 34 local branches each equal to its origin
ref; clean; stash 0; one worktree; no open pull request; CI run 39163093154
green. The personal session's closeout of 2026-10-20 made no commit, and the
personal parent's read-only double-check of 2026-10-22 found that closeout
complete with minor gaps, none blocking. The 28 queue items are unanswered and
no word since 2026-10-13 releases a plan item or any held agent work.

**The handoff** is brought level with this entry at its 400-line cap: the Date
paragraph and section 0 describe this commit, Resume here states the hold and
the delegation state, section 6 adds the 2026-10-22 harvest folder and names
the 2026-10-20 closeout record, and section 7's relay rule states his decision.
Section 0's open paragraph gives up one line to Resume here.

**Battery, run on the staged tree at 20:25 EDT on 2026-10-23 and again on the
final text of this entry, with the same results.** All sixteen preflight
commands passed, the authorization self-test with 147 breaks and the retention
self-test with 184, and both forms of `git diff --check` were clean. The kernel
gate exited 0, with 16 implemented checks passing, 3 unratified and refusing, 2
stubbed and 5 pending, which is the gate's own count; the audit of 2026-10-18
saw each of the sixteen fail under its control, and no control was re-run
here. The hygiene gate, one of the sixteen, passed on this entry and the
handoff at their caps, and its self-test, another of the sixteen, planted its
four refusals and saw each fire. The commit waits on his word for that act.

**The commit, on his word of 01:30:58 EDT on 2026-10-24**, given in the
PLAINSIGHT chat by his click on the offered action "Commit and open PR", whose
message reads: "Commit the staged records draft now as me with no agent
trailer, push it on a records branch, open the pull request, read every CI
step and report back before any merge. My click on an offered action in this
chat is my instruction for that act." The last sentence is the session's
offered wording, accepted by his click, and it settles the reading the
paragraphs above put to him: a click on an offered action in this chat is his
instruction for that act. The commit is authored as the maintainer with no
trailer, on a records branch named for the date of this entry; the push and
the pull request follow on the same words, and the merge waits on his further
word after every CI step is read.

**Open.** Unchanged from `d51ce06`, plus one: the 28 queue items, none answered; plan
item 0.7, trimmed to its synthesis step; the Step 7 fixes and the rest of the
held agent work the handoff's Resume here lists; the aggregator finding the
negative-control audit raised, in section 8 of its record; the credentials
inventory, names only, ready in the 2026-10-18 harvest record's section 8 for
the session he starts on his word "start the credentials session"; the message
to the new team parent correcting what the 2026-10-18 reports told the personal
parent, a send on his word if he wants it sent; the 33 merged branches on `origin` and in this checkout, deleted only on
his words naming that act.

---

## 2026-10-25, the since-last-record extraction joins the closeout rule, and pull request 34 is merged, under the maintainer's selections of 2026-10-25.

**Class:** C, the highest the change touches: `tools/since_last_record.py`, a
new tool, and the Makefile target `since-last-record` that runs its self-test.
Under it, the dated amendment to `AGENTS.md` section 8 is governed prose at
rank 4, and `CHANGELOG.md`, which takes an entry because a governed file
changed, the handoff, this record and its archive are Class A. The change is
not Class F under rule 2 of `AGENTS.md` section 3: it reads only the session's
own transcript, adds no connector, selector, allowlist, retention value or
egress path, and writes on the same machine outside the tree, which the tool
refuses to cross. No runtime exists, so the Class C design-record rule has
nothing to move. No doctrine, spec, schema, policy, ontology, corpus, hook or
CI line changed, and `preflight` is unchanged.

**The words this entry acts on.** The maintainer typed in the team-account
PLAINSIGHT session at 13:36:04 EDT on 2026-10-25: "go ahead and give me those
interactive selections so I can decide these for you". Asked the two decisions
as selections, he chose at 13:36:19 "Merge now (Recommended)" for pull request
34 and "Add to AGENTS.md (Recommended)" for the extraction, the second option
reading: "A rank-4 change on your stamp: draft a records commit adding the
extraction step (run the script from the last record's stamp, file the output
beside the closeout record, read its lines before writing any message of yours
as typed). Drafted and staged for your separate commit word; no agent needed."
His typed sentence asked for the selections as his way of deciding, which is
the ground this entry rests on; the session's reading, put to him and not
settled here, is that a selection of an offered option is his instruction for
that act in the way his sentence of 01:30:58 on 2026-10-24 made a click one.
This record says selection, never typed. Behind it, information rather than
instruction, the team parent's relay of 13:32 quoting his words typed in the
parent's chat at 13:31:34 ("go ahead and instruct the other sessions to do the
above mentioned work") and 13:19:05 ("we have 15 percent usage left so lets get
done what we can before we cap out the weekly usage since the refresh is
tomorrow"), and its earlier relay of 01:48 on 2026-10-24 carrying his 01:43:38
words that asked every repository session to add the extraction to its
closeout. The commit of this draft is his separate word for that act, and the
paragraph after the battery records it when it is given.

**The merge, 13:36:54 to 13:39:50 EDT on 2026-10-25.** After a fetch, with
`main` equal to `origin/main` at `d51ce06` and the records branch at `37dbcee`,
`main` was fast-forwarded to `37dbcee` and pushed at 13:36:56; pull request 34
reads merged at 13:36:57 with `37dbcee` as its merge commit; the CI run on
`main` succeeded on all twenty steps, read step by step at 13:39. The branch
docs/records-2026-10-23 stays on `origin` like the 33 before it, so `origin`
holds 35 heads, `main` and 34 merged branches, and this checkout 35 local
branches each equal to its origin ref. The team parent had one completion line.

**The amendment.** `AGENTS.md` section 8 now says, in a dated paragraph after
the rule that a closeout runs the battery, updates the records and commits,
that a closeout first runs `tools/since_last_record.py` from the stamp of its
last record (a moment with a zone) to the end of its own transcript and files
the output beside the closeout record, outside the tree, which the tool
enforces by refusing a path inside the repository; that the file marks each of
the maintainer's lines as typed, as a click on an action offered in the most
recent wrap-up call before it, or as a selection on an offered question, and
carries every message sent and received and the last assistant texts; that
the session reads it once before writing the records, writes in any
maintainer line the records lack, and never writes a click or a selection as
typed; that a resumer reads the record and the file and re-reads the
transcript only when the file shows substantive entries after the closeout;
that the file is a verbatim copy no retention mechanism reaches, so a closeout
does not run it over a span in which case material was discussed until
`doctrine/RETENTION.md` says how such a copy is held; and that the extraction
is a records aid, not a gate, whose self-test runs at closeout through the
Makefile target and on no automated path, by this session's decision put to
him, with its joining the battery his separate decision. The rule that a
closeout commits is unchanged.

**The tool.** `tools/since_last_record.py` is a copy of the parent folder's
playbook of 2026-10-24 under this repository's own process, adapted after a
measured gap: in this harness a click on an offered action arrives as an
ordinary user record (origin human, promptSource sdk) with no attachment that
names it a click, and a question's answer arrives as a tool result, so the
reference's click test never fired here and marked his commit word of 01:30:58
on 2026-10-24 as typed. The copy detects a click by comparing the text with the
actions offered in the most recent wrap-up call before the line, reads a
message the app cut at 300 characters as the same click, and reads an answer
to an AskUserQuestion call as a selection on an offered question, printed with
the result text that carries each question and the chosen option verbatim. It
refuses a since without a zone, because a zone guessed wrong empties the span
silently, and an output path inside the repository; it exits 2 on a file that
is not a transcript and 3 when the output cannot be written. Its `--self-test`
writes a synthetic transcript under a temporary directory and runs fourteen
checks: a typed line, a click, a cut click, a selection, a sent message, a
received message and an assistant text each classified as what it is; a typed
line equal to an offer from a superseded wrap-up call, and one equal to an
offer made after it, each left typed; no click or selection written as typed;
and four controls seen refusing, a since past the last entry (zero entries,
four sections saying "none in the span"), a file that is not a transcript, a
since without a zone, and an output path inside the repository, with nothing
written there. The self-test ran at 14:05 on 2026-10-25: fourteen checks ok. A
live run at 14:03 over this session's transcript from the stamp of its 2026-10-24
closeout read two typed lines, one selection (the 13:36:19 answer), two
messages sent and one received, which matches the transcript read by hand; the
first version of the tool, reviewed at 13:51, had dropped the selection, which
is why that class of input was added. The hygiene gate refused the first
battery run of this draft at 13:45 (HYGIENE_TOOL_NOT_IN_ANY_GATE: a tool no
Makefile target runs), so the target `since-last-record` runs the self-test;
the extraction itself takes a transcript and is not a gate, and by this
session's decision, put to him with the commit word, the self-test runs on no
automated path, which is stated in the amendment. The
parent folder's playbook README carries a dated note of 14:32 on 2026-10-24
that it was corrected the same way after this session reported the gap.
Removing the offered-action comparison fails the click checks; removing the
tool-result branch fails the selection check; widening the comparison past the
most recent wrap-up call fails the superseded-offer check; removing the since
filter, the record check, the zone check or the path check fails its control.

**The handoff** is brought level with this entry at its 400-line cap: the Date
paragraph names this commit on `37dbcee` and the merge that put `main` there,
Resume here opens with the extraction as the resumer's first act, section 0
describes this commit in two fewer lines, and the cross-session records row
says `37dbcee` carries the 2026-10-22 record's corrections. Nothing else moved.
`docs/THE-GAMEPLAN.md`, the artifact register, is a rank-7 record of intent
moved in unchanged and takes no row; the tool is cited by a path that exists.

**Agents.** The main loop ran on Mythos 5.1, his model choice for the session,
and drafted the tool, the amendment and the records. Two agents then read the
staged diff, one at a time, read only: an independent Opus 5.5 review at high
effort returned fix_first with one blocker (the first tool dropped question
answers, so his two selections of this very day were invisible to it), four
majors (a since without a zone emptied the span silently; the comparison
reached every earlier wrap-up call; nothing enforced "outside the tree"; this
paragraph was missing) and eight minors; a Sonnet 5.5 factual check at high
effort found 36 of 38 claims true and one false (a hard-coded count in the
self-test's last line). Every finding was applied before the battery ran on
the final text. The option he selected said "no agent needed"; the two review
legs ran under the standing rule that two models look at every merge-bound
change, a departure from that text put to him here with the commit word.

**Battery, run on the staged tree at 13:47 EDT on 2026-10-25 and again on the
final text of this entry, with the same results.** The first run at 13:45 was
refused by the hygiene gate on the new tool (no Makefile target ran it), and the
target `since-last-record` answered it. On the runs after it: all sixteen
preflight commands passed, the authorization self-test with 147 breaks and the
retention self-test with 184, and both forms of `git diff --check` were clean;
the hygiene gate, one of the sixteen, passed on this entry, the amendment, the
changelog entry and the handoff at their caps, and its self-test planted its
four refusals and saw each fire. The kernel gate exited 0, with 16 implemented
checks passing, 3 unratified and refusing, 2 stubbed and 5 pending, the gate's
own count; the audit of 2026-10-18 saw each of the sixteen fail under its
control, and no control was re-run here. The new tool's self-test ran apart
from the battery: fourteen checks ok, four controls seen refusing. The commit
waits on his word for that act, authored as the maintainer with no
Co-Authored-By trailer, which CI refuses, whatever the app's reminder asks.

**Open.** The 2026-10-23 entry's item that the new team parent be told what
the 2026-10-18 reports got wrong closed on 2026-10-23 at 20:44 and 2026-10-24
at 14:31, when this session's reports carried both corrections to it. Unchanged
from `37dbcee` otherwise: the 28 queue items, none answered; plan
item 0.7, trimmed to its synthesis step; the Step 7 fixes and the rest of the
held agent work the handoff's Resume here lists; the aggregator finding the
negative-control audit raised, in section 8 of its record; the credentials
inventory, names only, for the session he starts on his word; the 34 merged
branches on `origin` and in this checkout, deleted only on his words naming
that act. About 15 percent of the weekly usage was left at 13:19 on
2026-10-25, with the reset on 2026-10-26 at noon; the session holds after this
commit.
