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

## 2026-10-26, the extraction amendment committed and pushed, and the closeout, under the maintainer's typed words of 2026-10-26.

**Class:** A. This entry and the handoff header change no governed artifact. The
commit it records, `12e9d55`, was Class C as the 2026-10-25 entry classed it.

**Agent involvement.** A fresh personal-account PLAINSIGHT session on Sonnet 5.5
at medium, started by the parent folder session on his words of 2026-10-26, ran
every step below with no sub-agent. By his words of 20:05:08 on 2026-10-23 every
act here takes his words typed in this chat, and the parent's relays were read
as information.

**What was done, from his typed lines** (read from the since-last-record file
`SINCE_LAST_RECORD_2026-10-26_closeout.md`, which marks all four as typed and
none as a click or selection):

- 19:24 to 19:30, the refresh from records. After a fetch: `main` ==
  `origin/main` == `37dbcee`, 35 branches each equal to `origin`, one worktree,
  stash 0, no open pull request, seven files staged and untouched. The delta
  file of 2026-10-24 held only the parent's relay of 14:34. One report went to
  the parent.
- 19:33, "if all looks clean and matches our intent and philosophy, go for
  commit". The sixteen preflight commands and the extraction's self-test all
  exited 0 on the staged tree and `git diff --cached --check` was clean. The
  seven files were committed as `12e9d55` with the 2026-10-25 message, authored
  as the maintainer, no trailer. The report to the parent that followed stamped
  the commit 19:35, a minute after the clock read at the commit; the commit's
  own timestamp governs.
- 19:35, "go for push". `main` fast-forwarded from `37dbcee` to `12e9d55`; after
  a fetch `main` == `origin/main` == `12e9d55`. CI run 40420770198 on `main`
  concluded success, all twenty steps read one by one, the trailer refusal and
  the hook step included.
- 19:39, "closeout is good to work now". The extraction's self-test ran first
  (fourteen checks ok, four controls seen refusing), then the extraction over
  this session's transcript, filed outside the tree beside the 2026-10-24
  closeout record. The 2026-09-28 entry moved to the archive unedited, to keep
  the ten-entry cap. The handoff header was corrected to the committed state.

**What changed in state.** `main` gained `12e9d55`, and the amendment to
`AGENTS.md` section 8 is now in force on `main`. The extraction joins no
battery, as the amendment says. Pull request 34 was merged on 2026-10-25.

**Open.** The closeout records wait on his commit word for that act, a Class A
commit. Unchanged: the 28 queue items, none answered; plan item 0.7; the Step 7
fixes and the rest of the held agent work; the audit's section 8 finding; the
credentials inventory for the session he starts; the 34 merged branches, deleted
only on his words naming that act. The lane holds until he types a release here.
---

## 2026-10-28, the build night under the maintainer's typed release of 01:47: Step 9, Step 12's schema and harness, Step 10 drafted, the Sherlock connector on cassettes, and the application's first slice.

**Class:** C, the highest class touched: application and runner code, a
connector, validators and their wiring, the design record's appended section 9,
and the Class B artifacts beneath them (the divergence register, the manifest
schema, the harness fixture schema). No Class F change landed. The dispatch
allowlist exists only as a draft outside the tree, and no doctrine, policy,
ontology, synthetic or corpus file changed.

**Agent involvement.** This session was started by the parent folder session on
the evening of 2026-10-27 on Sonnet 5.5 at medium, measured the state (`main`
== `origin/main` == `41badf7`, 35 branches each equal to `origin`, one
worktree, stash 0, nothing staged, no open pull request), ran the extraction
over its own transcript (nothing substantive), reported to the parent and held.
At about 01:50 on 2026-10-28 his local `/model` command set it to Fable 5.1
with Ultracode on. Five Workflow runs followed, every agent Opus 5.5 at high,
each in the same shape: one or two builders on the working tree, read-only
lenses, three refuters per finding, one fixer with a negative control per fix,
one verifier. Phase A, Step 9: 176 agents. Phase B, the manifest schema and
validator: 205. Phase E, the application: 245, launched before the parent's
three-agent instruction reached this session and kept at its fan-out. Phase
C+D, Step 10 and the connector: 286, capped at three agents at once, cut at
about 06:30 by the account's usage limit with 35 agents unrun, and finished
after the 07:50 reset by a continuation of 35 agents from the saved findings so
that neither builder re-ran on the built tree. The session wrote the briefs,
the records and this entry and ran the battery; it wrote no code. The records
of every phase, the lens findings, every refuter verdict and the fixer and
verifier reports are in
`Z-ISR/_session-artifacts/2026-10-28-plainsight-build/`.

**His line in this chat**, read from the extraction filed beside that record,
which marks it as typed and marks no click and no selection. At 01:47:22:
"take any instructions from the parent, but while waiting go ahead and take
care of as much as you can for plainsight. From doctrine and semantics to
building what you can for the OSINT gathering tools (minus what you need me to
provide) and starting work on the social web operating picture all the data
will be visualized with and interacted with. Just get as much as you can done
while waiting for stuff from me like VMs, domains, SIM cards etc". Read here as
a release of the hold on work: parent instructions bind, and every commit,
push, merge and Class F decision still takes his own word in this chat, per
act. The parent's instruction of the night, his machine-load rule of
2026-09-30 (three agents across the estate at most), was followed from the
next launch on. His `/model` command is a local command the extraction does
not list. One problem with the extraction, found here and left for a Class B
fix with its own self-test case: it marks two further lines as typed that are
not his, the context-compaction summary of 05:14:45 and a classifier notice of
09:00:55, because both arrive in the user role and the tool reads every
user-role record it cannot match to an offered action as typed. A reader of
`SINCE_LAST_RECORD_2026-10-28.md` takes its first line only as his.

**What was done** (Eastern time):

- 02:00 to 03:20, Step 9. `spec/divergence-register.yaml` (30 entries, 8
  identical pointers, readings DR-R1 to DR-R4), its validator (seven codes, 39
  self-test breaks), its renderer and the rendering; wired into the Makefile,
  the hook, CI (which clones the public `zmeta-spec` at tag v1.1.27 beside the
  checkout) and the kernel gate. Review: 56 findings, 25 confirmed, 9 defects
  fixed, among them a per-branch required-ness fingerprint and a sound
  expansion of anyOf and oneOf alternatives.
- 03:25 to 04:30, Step 12 part one. `schema/connector-manifest.schema.json`,
  `conformance/connector-harness/fixture.schema.json` with its README,
  `tools/validate_manifest.py` (96 self-test cases), PIN-R9 in
  `tools/pin_of_record.py`. Review: 65 findings, 16 fixes, 7 proposed fixes
  skipped as widening and recorded as readings MF-R13 to MF-R16.
- 03:44 to 06:14, the application's first slice, `app/`, 59 files: the store
  (stdlib sqlite3, the Postgres DDL as the record, twelve tables, event log
  append-only by trigger), the ingest door through `tools/validate.py`, rebuild
  and replay, a server bound to 127.0.0.1 with an egress guard, the case-scoped
  social web as SVG with caps of 300 nodes and 600 edges and no weight
  anywhere, the Lineage Drawer, PATHS, DOSSIER, SSE with opaque ids, and
  amendments 9.1 to 9.12 appended to `docs/PLAINSIGHT-design.md`. Review: 78
  findings, 33 confirmed and fixed; 194 tests with 90 paired negative controls.
- 04:18 to 06:30 and 08:02 to 08:59, Step 10 and Step 12 part two.
  `runner/subject_guard.py` (22 tests; the live pin refuses every request at
  step 1), `--dispatch-paths` in `tools/validate_authorization.py` (43 planted
  cases; refuses while the allowlist is absent), `connectors/sherlock/` on
  hand-built cassettes with placeholders only (38 tests),
  `tools/validate_connector_conformance.py` (25 plants). Sherlock, Docker and
  the network were never run. Review: 91 findings, 57 stand, 38 defects fixed.
- 09:00 to 09:10, the closeout records. 100 files staged (26,187 insertions,
  160 deletions); hygiene, the repo scan over 148 tracked files and the kernel
  gate run on the staged tree; the 2026-09-29 entry moved to the archive
  unedited; this entry.

**Decisions taken here**, each an agent reading or a session choice he can
reverse: the fan-out cap at three after the parent's instruction; the
application's wiring into the gate battery and the SH-R5 schema move held for
his word, because the weekly usage line stood at 76 percent with four days to
its reset and PLAINSIGHT is fourth in his order of 2026-10-16; staging before
the records, per `AGENTS.md` section 8; every DR, MF, APP, SG, VA, DA, SH and
CC reading is recorded in the artifact that carries it and in the record
folder.

**What changed in state.** The tree carries the four phases, staged. The
kernel gate is red on three entries by design: `retention-self-test`, because
`policy/retention.yaml` line 870 still says `canary_subject_class` is absent
while the tree now requires and declares it; `connector-manifest` and
`connector-conformance`, because the Sherlock manifest's handle emit names no
platform (reading SH-R5: a handle's registry form binds a platform and
Sherlock's platform differs per site). The pre-commit hook refuses this tree at
`validate_manifest --all` for the same reason, so the commit waits on his SH-R5
decision as well as his commit word. `--dispatch-paths` refuses because the
allowlist is absent; its draft, DA-R1, is in the record folder and must be
re-measured before any stamp (11 sites outside the gate, all under `app/`).

**Open.** SH-R5 and the retention flag with its self-test mutation; DA-R1; the
application's wiring (kernel gate, Makefile, hook, CI); the sentences in rank 1
to 3 files the build made false, listed in the record folder; the 28 queue
items, none answered; plan item 0.7; the Step 7 fixes and the held agent work;
the audit's section 8 finding; the credentials inventory; the 34 merged
branches, deleted only on his words naming that act.

**Addendum, 12:09 to 14:5x: the three held builds, on his click.** At
12:09:52 he clicked the offered action labelled "Build them now"; the button
carried the session's message "Go ahead: build the SH-R5 schema move, the
retention flag with its self-test mutation, and the app wiring pass now, one
writer, reviewed; re-run the battery and re-stage; still no commit without my
word.", which he accepted by the click and did not compose, and his record
carries the label. A click on an offered action in this chat is his
instruction for that act, by his own words of 2026-10-24 01:30:58. The
extraction marks that line as typed, because the tool compares a record with
the offered action's message and this record carries its label: a second case
for the fix named above. One Workflow run (wf_faceb804-0b2, 12:13 to 14:34,
159 Opus agents, capped at three): one writer, six lenses, 150 refuter calls,
one fixer, one verifier.

- SH-R5 cleared by reading MF-R17: an emit of a key whose registry form binds
  a platform may declare `platform_from_item` in place of `platform`, only on
  a manifest whose `probe_unit` is endpoint; exactly one of the two where the
  form binds a platform, neither where it binds none, each case refused by
  name under MANIFEST_SELECTOR_PLATFORM. The Sherlock emit uses it, and the
  handle claim value carries a token derived from the site name alone
  (SH-R18: lower-cased, non-alphanumeric runs to one underscore; nine sites
  give no token, the four starting with a digit and the five with a
  parenthesised qualifier, and a Claimed row there is ambiguous with no
  claim). Amendments 9.14 and 9.15 appended. DECLARE passes; the kernel
  gate's two connector entries pass.
- The retention flag: `policy/retention.yaml` line 870 reads `present: true`,
  the one policy change, and the self-test mutation flips the flag rather
  than setting it. The retention self-test passes.
- The application's tests join the kernel gate (`app-tests`, IMPLEMENTED,
  `--tb=short`), `make test` and a named CI step, and stay out of the hook and
  preflight (APP-R30: about three minutes, and they guard runtime behaviour
  rather than what enters git history). CI stays on Python 3.12: `app/`
  compiles there and every standard-library attribute it names resolves, and
  the suite on 3.12 is unverified until a push (CI-R1 not taken).
- The dispatch scanner reads a patch target, a patched attribute's kept
  original and an attribute assigned over as no site, in test modules only
  (VA-R6, with eleven plants and seven more from the fixer, 61 dispatch cases).
  The test client's two loopback connections moved to `app/tests/conftest.py`
  naming 127.0.0.1 on the call. `--dispatch-paths` now finds four sites
  outside the gate, all covered by the re-measured draft DA-R2 in the record
  folder, never in the tree.
- Review: 51 findings, 150 refuter calls, 32 stand; the fixer applied eight
  (VA-R6 narrowed to test modules with the patch.object and receiver names
  exact; a kept original called in place is a site; the entity emit refuses
  `platform_from_item`; qualified site names give no token; CONFORMANCE.md,
  AGENTS.md and README.md brought to the present) and skipped the records,
  which this entry and the handoff carry. 13 controls seen failing in scratch
  copies. Verifier: every check passes, the kernel gate and the hook exit 0,
  every fix present by line.

**Two questions this build leaves him**, each recorded where the artifact is:
the class of VA-R6 (the session applies it as a Class B precision rule of the
scanner, in test modules only, with plants proving a patch whose replacement
dispatches is still a site; the widening lens read it as Class F; if he reads
it so, the rule comes out and the four `test_http.py` patch references join
DA-R2) and the class of the line 870 edit (the session reads it as Class B, a
statement of enforcement state reaching no subject, retention period or egress
path; the C+D fixer's comments had called it Class F; he instructed it either
way, and a Class F reading would need his dated row in the pin).

**State after the re-stage.** The index holds every file of the night with
these builds on top, 106 files. The battery of 33 commands ran 14:40:58 to
14:46:50 on the staged tree: 29 exit 0 and the four designed refusals of the
unratified modes (`--policy`, `--shred-roundtrip`, `--dispatch-paths`,
`--fixtures`); the kernel gate at 32 entries with 24 implemented and none
failed; the pre-commit hook passing; both diff checks clean. The commit waits
on his typed word.

---

## 2026-10-28, the build night's commit, push, merge and three CI runs, under the maintainer's clicks of 2026-10-28.

**Class:** A. This entry and the handoff's header and section 0 change no
governed artifact. The commit they record, `8583132`, was Class C as the
previous entry classed it.

**Agent involvement.** The same personal-account session as the previous
entry, on Fable 5.1, ran every act below itself with no sub-agent. Each act
took his click on an action the session offered in this chat, which is his
instruction for that act by his own words of 2026-10-24 01:30:58; the button
messages are the session's words that he accepted by clicking, not words he
composed, and his record carries each button's label. The extraction filed
beside the night's record marks the four labels as typed, because the tool
compares a record with the offered action's message and not its label; the
previous entry names that as a case for the tool's next fix.

**What was done, from his clicks** (stamps from the transcript):

- 12:09:52, "Build them now": the three held builds of the previous entry's
  addendum.
- 14:49:49, "Commit and open PR" (the button: commit the staged tree as him
  with no agent trailer, push it on a branch, open the pull request, read every
  CI step and report back before any merge). The identity read
  `Incept.IO <234959487+JTC-byte@users.noreply.github.com>`; `main` ==
  `origin/main` == `41badf7` after a fetch; 106 files staged; the cached diff
  check clean. Commit `8583132` on `build/2026-10-28-build-night` at 14:50:51,
  the hook running from 14:50:51 to 14:51:41 and passing, no trailer; pushed;
  pull request 35 opened against `main`. CI runs 40749046365 (push, 18:51:49Z
  to 18:58:36Z) and 40749053930 (pull_request, to 18:59:20Z): success on every
  step of each, the 23 named steps read one by one at 14:59, the application
  tests on Python 3.12 among them for the first time in CI, with the kernel
  gate, the hook step and the trailer check. The report went to him before
  any merge.
- 15:00:13, "Merge it" (the button: fast-forward `main` to `8583132`, push
  `main`, read every CI step on `main` and report back). `main` fast-forwarded
  from `41badf7` and pushed at 15:00:34; pull request 35 MERGED at 19:00:34Z;
  after a fetch `main` == `origin/main` == `8583132`. CI run 40750370333 on
  `main` (19:00:35Z to 19:11:00Z): success on every step, read one by one at
  15:11. The branch stays on `origin` like the 34 before it.
- 16:00:52, "Draft it" (the button: draft this entry with the push, the merge
  and the three CI runs and their step counts, his clicks named as clicks, no
  agent trailer; stage it and do not commit until he says so). The 2026-09-30
  checkpoint entry moved to the archive unedited, to keep the ten-entry cap;
  the handoff's header and section 0 brought to the committed state.

**What changed in state.** `main` gained `8583132`: Step 9, the manifest
schema and harness, Step 10 drafted, the Sherlock connector on cassettes
passing DECLARE, the application's first slice in the kernel gate, the one-word
policy edit of line 870, and the records of the night. The kernel gate exits 0
at 32 entries on `main`. Nothing else moved. State at this entry: `HEAD` ==
`main` == `origin/main` == GitHub `main` == `8583132`, clean, stash 0, one
worktree, no open pull request, 35 merged branches on `origin`.

**Open.** His: the three classes the handoff's section 3 names (the emit's
platform move, VA-R6, the line 870 edit), the DA-R2 stamp outside the tree,
the readings each artifact carries, the sentences in rank 1 to 3 files the
night made stale, the 28 queue items, plan item 0.7, the Step 7 fixes, the
audit's section 8 finding, the credentials inventory, the 35 merged branches.
This entry's commit waits on his word for that act, a Class A commit.

---

## 2026-10-28, the records commit merged, and the closeout checkpoint, under the maintainer's click of 16:00 and his go word of 17:07.

**Class:** A. This entry and the handoff's header and section 0 change no
governed artifact. The commit it records, `356c1f7`, was Class A as the
previous entry classed it.

**Agent involvement.** The same personal-account session as the two previous
entries, on Fable 5.1, ran every act below itself with no sub-agent, one test
run at a time.

**What was done.**

- 16:10:54 to 16:11:42, on his click "Commit and open PR" (the button: commit
  the staged records draft as him with no agent trailer, push it on a records
  branch, open the pull request, read every CI step and report back before any
  merge): commit `356c1f7` on the branch docs/records-2026-10-28, the hook passing, no
  trailer; pushed; pull request 36 opened. CI runs 40761076490 (push,
  20:11:46Z to 20:23:00Z) and 40761082594 (pull_request, to 20:23:03Z):
  success on every step of each, the 23 named steps read one by one at 16:24.
- 16:29:45, on his click "Merge it": `main` fast-forwarded from `8583132` and
  pushed; pull request 36 MERGED at 20:29:46Z; after a fetch `main` ==
  `origin/main` == `356c1f7`. CI run 40763787164 on `main` (20:29:47Z to
  20:41:03Z): success on every step, read one by one at 16:41. The branch
  stays on `origin`, the 36th merged branch.
- 17:07:57, his words typed in the parent session's chat, relayed by that
  session at about 17:10 and found verbatim in its transcript (1db10bc3, line
  6095): "go ahead and give the go word for all sessions to commit,
  push/deploy, merge, tag etc whatever is ready to do so. Then once all work
  is committed and pushed properly, have them all run a full closeout
  checkpoint for this session". The relay binds here under his delegation line
  of 01:47 ("take any instructions from the parent"). In this lane nothing was
  unpushed and nothing is ready to tag: PSE has no release, a tag is Class E,
  and `CONFORMANCE.md` section 6's bar is not met. The act is this closeout
  checkpoint under `AGENTS.md` section 8: the battery on the clean tree at
  `356c1f7` (33 commands one at a time: 29 exit 0 and the four designed
  refusals of the unratified modes, the kernel gate at 32 entries with 24
  implemented and none failed, the hook passing, both diff checks clean), this
  entry with the 2026-09-30 overnight entry moved to the archive unedited under
  the ten-entry cap, the handoff's header and section 0 brought to this commit,
  the checkpoint record and the since-last-record delta file with its hash in
  the record folder outside the tree, and this entry's Class A commit by the
  same route as the two before it. Negative controls seen failing and named:
  the hygiene self-test's four deliberate breaks refused, among them the two
  pre-commit words in the handoff; the extraction self-test's four controls
  refusing (a since past the last entry, a file that is not a transcript, a
  since without a zone, an output path inside the repository).

**What changed in state.** `main` gained `356c1f7`, the records of the build
night's commit, push, merge and CI runs, so nothing is owed to the worklog
for the night. State at this entry: `HEAD` == `main` == `origin/main` ==
GitHub `main` == `356c1f7`, clean, stash 0, one worktree, no open pull
request, 36 merged branches on `origin`.

**Open.** His, unchanged: the three classes the handoff's section 3 names (the
emit's platform move, VA-R6, the line 870 edit), the DA-R2 stamp outside the
tree, the readings each artifact carries, the sentences in rank 1 to 3 files
the night made stale, the 28 queue items, plan item 0.7, the Step 7 fixes, the
audit's section 8 finding, the credentials inventory, the 36 merged branches.
The extraction tool's two misreads named in the first 2026-10-28 entry await a
Class B fix with its own self-test cases.

---

## 2026-10-28, three classes decided, under the maintainer's clicks of 17:45 to 19:49.

**Class:** A. This entry records three decisions of his and changes the
sentences that said each was his to confirm; no governed value, gate, rule or
mechanism changes.

**Agent involvement.** The same personal-account session as the three previous
entries, on Fable 5.1, no sub-agent. Each decision arrived as his click on an
action the session offered in this chat after the closeout report, as the
parent's reading of his words of 17:30:21 allowed; each button's message is the
session's words he accepted, and his record carries the label.

**The decisions.**

- 17:45:23, "Class B, keep it": VA-R6, the dispatch scanner's rule that a
  patch target, a patched attribute's kept original and an attribute assigned
  over are no site in a test module, is Class B, a precision rule of the
  scanner and not an exemption from the bypass check; it stands as applied,
  and the allowlist draft DA-R2 keeps its four sites. Recorded in the scanner's
  docstring, READINGS entry and block comment, `AGENTS.md` section 5,
  `CONFORMANCE.md` section 4, `app/README.md` and the handoff.
- 18:00:28, "Class B": the one-word edit of `policy/retention.yaml` line 870
  (`present: true` for the `canary_subject_class` part), made on his
  instruction of 12:09, is Class B, a statement of enforcement state reaching
  no subject, retention period or egress path, needing no row in the pin.
  Recorded in `CONFORMANCE.md` section 4, the Makefile header, the hook's
  comment, `tools/validate_retention.py`'s comment, `AGENTS.md` section 5 and
  the handoff.
- 19:49:50, "Keep it": the emit's platform move stands, Class B with its
  design amendments 9.14 and 9.15: an emit of a platform-bound key may declare
  `platform_from_item` on an endpoint-unit connector (MF-R17), and the Sherlock
  claim's platform token is derived from the site name alone (SH-R18).
  Recorded in `tools/validate_manifest.py`'s MF-R17 reading, the kernel gate's
  connector-conformance note, the Makefile, `CONFORMANCE.md` section 4,
  `AGENTS.md` section 5, `connectors/sherlock/README.md` and the handoff.

**What changed in state.** Nothing in any gate, rule or value; the tree's
prose now states each class as decided rather than as his to confirm. Ground
for each: his click, which is his instruction for an act and his decision for
an item by his own words of 2026-10-24 01:30:58. Revert: his word, with the
same sentences rewritten.

**Open.** His, unchanged: the DA-R2 stamp outside the tree, the readings each
artifact carries (DR, MF, PIN-R9, SG, VA-R5, SH, CC, APP), the design
amendments 9.1 to 9.15 as records of departures, the R8-row pipe, the
sentences in rank 1 to 3 files the night made stale, the 28 queue items, plan
item 0.7, the Step 7 fixes, the audit's section 8 finding, the credentials
inventory, the 37 merged branches. This entry's commit follows his go word of
17:07:57 by the usual route.

## 2026-11-02, resumed on the personal account: pull request 38 merged on the maintainer's click, the second-model review of 8583132, and the extraction tool's three misreads corrected.

**Class:** B. `tools/since_last_record.py` changes behaviour (three misreads
corrected, each with a self-test case and a control) and `AGENTS.md` section
8's description of it follows; `CHANGELOG.md` takes an entry. No doctrine,
spec, schema, policy, ontology, runtime, gate or value changes.

**Agent involvement.** Personal-account session c941f6e6, started at about
17:35 EST by the parent of 11-02 (local_a7b08618) on his words of today, which
research/inputs/resume_briefs_2026-11-02/README.md section 1 in the parent
folder records verbatim; the refresh ran on Opus 5.5 from records with no
agent; Fable 5.1 in the main loop from the parent's go at 17:36. Every agent
slot of the estate was held by other lanes until 18:17 and the heavy-run lock
by zisr-producers from 17:41, so the review and the fix below were done in
the main loop; one Sonnet 5.5 verifier (agent-slot-2, 18:17 to 18:20,
read-only, then again 18:23 to 18:25 on the deltas) read the staged fix as
its second model, found every checked claim true with three controls seen
failing on a copy, named three weaknesses, each answered below, and on its
re-check found one defect the answer had introduced, closed below with a
plant and a control. One lapse, recorded as the 2026-10-08 rule asks: the kernel
gate ran once on the checkout at 17:5x before this session had the estate's
heavy-run rule in its loop; every later battery-sized run waits on the lock.

**His line of the day in this chat.** At about 17:44 EST, a click on the
offered action labelled "Merge it" (the button's message, the session's words
he accepted: fast-forward main from 069d483 to 0aac3b9, push main, read every
CI step on main and report back before anything else). The go word of
17:07:57 on 10-28 lived in the predecessor's chat and named that day's parent,
and under the brief of 11-02 a delegation naming an earlier parent does not
carry over, so the merge took his word here and not that go word.

**Pull request 38 merged.** Its two branch runs on 0aac3b9 (40790532704 push,
23:54:35Z to 00:01:14Z; 40790538481 pull_request, to 00:05:43Z), which the
predecessor never read because it ran out of usage at 20:06 EDT on 10-28, were
read step by step at about 17:40 today: success on every step of each. On his
click, main was fast-forwarded 069d483..0aac3b9 and pushed at 17:44:21 EST;
pull request 38 MERGED at 22:44:20Z; CI run 41539769592 on main (22:44:22Z to
22:52:27Z) concluded success on every step, the 23 named steps read one by one
at 17:55. State then: HEAD == main == origin/main == GitHub main == 0aac3b9,
clean, stash 0, one worktree, no open pull request, 38 merged branches on
origin. The addendum the predecessor owed is section 8 of
CLOSEOUT_2026-10-28.md in Z-ISR/_session-artifacts/2026-10-28-plainsight-build/,
with the delta re-run from 2026-10-28T21:40:40Z beside it
(SINCE_LAST_RECORD_2026-11-02_addendum.md, 263 entries, sha256
5de796155c9212cf), its self-test and two live controls seen refusing first.

**The second-model review of 8583132 (item 1 of the 10-28 list).** Record:
Z-ISR/_session-artifacts/2026-11-02-plainsight-resume/REVIEW_8583132.md.
Fable 5.1 read the six mechanisms the item names against their doctrine and
design sentences and ran each: the subject guard suite, 22 passed; the
Sherlock harness, 6 of 6 fixtures, 30 events graded, 0 refused; the manifest
validator refusing MANIFEST_SELECTOR_PLATFORM on a mutated copy of the real
manifest and passing the real one; the authorization, manifest and connector
conformance self-tests green; the application suite, 195 passed with its 91
paired controls; the kernel gate, 24 implemented, 0 failed. No defect found in
the six. Four readings for him, none a defect: the run's egress.environment is
a schema constant the adapter writes as a literal, so EG-6's enforcement is
preflight and not the field; no two of the 481 Sherlock sites collapse to one
platform token, a property no test asserts; the egress guard's six-character
bare-form floor is a design constant he has not read; one dead monkeypatch
line in a test. The review claims coverage of the six, not correctness of the
commit.

**The extraction tool's three misreads corrected (item 3).** Named in the
first 2026-10-28 entry and the closeout's section 3, and a third in the brief
of 11-02: (1) a click whose record carries the button's label rather than its
message read as TYPED, which every click of 10-28 did; (2) a harness record in
the user role, the context-compaction summary of 05:14:45 (its record carries
isCompactSummary) and the classifier notice of 09:00:55 (isMeta), read as
TYPED; (3) every stamp converted with the local offset of the day the tool
runs, so after the daylight-time change of 11-01 every stamp from before it
printed one hour early (the delta of today's addendum shows 16:45:23 for his
click of 17:45:23). The fix: the match against the most recent wrap-up call
also reads an action's label as the click, marked "by its label"; a user
record carrying either flag is listed under a new section by stamp and kind
and its text is never copied; each stamp converts with the operating system's
offset for that instant, written after the stamp. The verifier's three
weaknesses: a typed word equal to a label of the latest wrap-up call reads as
that click, and the record fields do not tell them apart (measured: his typed
release and his clicks carry the same promptSource and turnOrigin), so the
mark and the docstring now say so and a plant proves a superseded call's
label stays typed; the harness branch could have hidden a flagged record's
tool result, so tool results are now read before the flag is applied; stamps
carried no zone marker, so each now carries its offset. The re-check's
defect: the harness branch reused the name of the line kind, so a second text
block of an unflagged record was misfiled as a harness record and its text
dropped; the name is now the record's own, a record typed in two blocks is
planted, and the defect re-planted on a copy fails four checks. The self-test
has 21 checks over 15 planted lines (a label click, a superseded call's
label, a two-block record, a compaction summary and a harness notice among
them), a zone check against the
operating system's clock for two instants on either side of the change, its
reference read independently of the conversion, with the fixed-offset
conversion seen to differ on this machine, and the four controls refusing. Over the predecessor's transcript from
2026-10-28T05:00:00Z the fixed tool reads 1 typed line (his release of
01:47:22), 9 clicks by label, 7 harness records and 0 lines a reader would
take for his that are not. `tools/validate_hygiene.py` exits 0 over the edited
tree.

**Item 2, the negative-control audit, run (20:06 to 20:31 EST).** By the
2026-10-18 method in a clone at 0aac3b9 beside a clone of ZMeta/zmeta-spec,
under the estate's heavy-run lock taken with no waiting file present: the six
gate entries 8583132 added and the three it moved each exit 0 on the tree as
it stands (the unratified one refuses by design) and each was seen failing
under one planted break naming its refusal; the aggregator was seen red twice.
Two findings, neither a defect of 8583132: the harness's cut had a precedence
bug on a condition with `or`, fixed and the control re-run; and
`tools/pin_of_record.py --self-test` breaks when runner/dispatch_allowlist.yaml
exists, because its absent-file example is that real path, so the commit that
lands DA-R2 stamped must also move that example (Class B, owed then). The
kernel gate on this commit's staged tree, under the same lock: 24 implemented,
0 failed. Record: Z-ISR/_session-artifacts/2026-11-02-plainsight-resume/AUDIT_2026-11-02.md.

**Open.** Items 4 to 8 of the list follow, with briefs for 4 and 8 written. His, unchanged: the DA-R2 stamp outside the tree, the readings
each artifact carries, the 28 queue items, plan item 0.7, every stamp, the 38
merged branches. This entry's commit follows the usual route on his word in
this chat.

---

## 2026-11-08, item 4 recorded: the ontology validator's --corpus and --matchers modes, the merge of 04b358f, and the lane resumed on the maintainer's click of 2026-11-08.

**Class:** B. `tools/validate_ontology.py` gains two modes, `tools/validate_conformance.py` moves the `ontology-corpus` gate entry from STUB to IMPLEMENTED, and thirteen notes in `ontology/selectors.yaml` gain one sentence each (no key, form, field or matcher changed; reading O-R4, which he decided on 2026-11-02 with the click "Keep them"). `CONFORMANCE.md`, the Makefile comment, the gameplan's deferral row, the connector validator's rung 3 line, the handoff and `CHANGELOG.md` follow. No doctrine, spec, schema, policy, runtime, synthetic or corpus file changed, and no value.

**Merge and CI first.** `04b358f` (the extraction tool's three misreads corrected, class B) merged to `main` as pull request 39 at 20:53:40 EST on 2026-11-02 on his click "Merge it" of 20:53:32; the CI run on main, 41562667958, concluded success on its one job (gate). Measured again today: `main` == `origin/main` == `04b358f`.

**The words this commit acts on.** His click on the offered action "Yes, resume here" in this chat on 2026-11-08, which lifts the hold of his click "Leave it" (16:16:45 on 2026-11-03), and the earlier click "Keep them" (21:44:42 on 2026-11-02). Neither is a typed line. A commit takes his word here per act.

**Agent involvement.** Item 4 was built on 2026-11-02 by workflow wf_513195a4-7a0 in session c941f6e6 (Opus 5.5 builder, Sonnet 5.5 verifier, Opus 5.5 fixer, one at a time under an agent slot; the verifier found 11 of 12 claims true and four defects, all closed with plants and controls). The mode report is `Z-ISR/_session-artifacts/2026-11-02-plainsight-resume/PHASE_item4_report.md`. This entry and the other records were written on 2026-11-08 by the fresh session of that day on Sonnet 5.5 with no agent, then Fable 5.1 on the parent's switch.

**What the modes check.** `--corpus` reads the five sites `spec/layer-model.yaml` binds to the registry and refuses an unregistered type, a value off its key's form, a vacuous must-fail row and an unexercised key (ONT_CORPUS_SELECTOR_UNREGISTERED, _VALUE_OFF_FORM, _FIXTURE_VACUOUS, _KEY_UNEXERCISED). `--matchers` is its structural half only: calibration flags false, every matcher id a connector names declared, every library entry complete (ONT_MATCHER_CALIBRATION_FLAG, _NAMED_UNDECLARED, _ENTRY_INCOMPLETE). No matcher is scored and the output says so; scoring needs labelled ground truth, which needs the sealed cast. The aggregator runs a STUB entry's command and does not read its exit code, which `CONFORMANCE.md` section 4 now states.

**Held, not folded.** The extractor's list fix in `tools/since_last_record.py` (eight insertions, a prompt written as a list of blocks crashed the committed tool) stays unstaged for its own class B commit, so this commit carries item 4's eight files and the records only.

**Battery.** On the staged tree with the extractor fix stashed so the working tree equalled the index, under the estate's heavy-run lock taken at 02:36:05 EST on 2026-11-09 (released 02:42:13): the kernel gate, 02:36:46 to 02:41:12, 25 implemented, 0 failed, 4 unratified and refusing, 1 stubbed, 2 pending, exit 0; the pre-commit hook, 02:41:12 to 02:41:59, exit 0; hygiene exit 0 with its self-test refusing 4 of 4 and a planted pre-commit tense word in the handoff refused as HYGIENE_HANDOFF_PRE_COMMIT_TENSE then restored; both forms of `git diff --check` clean. The 2026-11-02 run on the same eight files read the same gate line.

**Open.** Items 5 to 8 of the 10-28 list; his DA-R2 stamp and, at that commit, the pin self-test's absent-file example; readings O-R1 to O-R9; the 28 queue items.

---

## 2026-11-09, item 4 merged as 8507464 with its CI runs read, and the closeout of the resumption, under the maintainer's line of 02:27:22.

**Class:** A (the handoff, this record and its archive). No governed artifact changed, so `CHANGELOG.md` takes no entry.

**The words this commit acts on.** His typed line of 02:27:22 EST on 2026-11-09 in the parent's chat, verified in the parent's transcript: "I am leaving you up to keep working while I head to bed. Just finish whatever efforts anyone is in the middle of, then run a checkpoint to capture what was done and we will pick back up when I am back on. You are good to adjudicate any commits, merges, pushes, deploys etc as needed so long as they pass repo documentation and established tests, conformance and validations". The parent (local_88a0656e, Parent 08NOV2026) gave item 4's commit its go on four conditions, each measured and met, and its go covers this closeout's commit and push once the checks pass. The reading under CLAUDE.md R6 and AGENTS.md section 4, that this line plus the parent's go is his per-act instruction for a Class B commit, is in the record folder; his click "Yes, resume here" of 15:45:31 EST on 2026-11-08 in this chat lifted the hold of 2026-11-03 and named that parent.

**Item 4 landed.** Committed as 66f1431 on branch item4-ontology-corpus-matchers at 02:42:35 EST (author Incept.IO, no agent trailer, 11 files, 1,436 insertions, 272 deletions); pull request 40; CI runs 42581128275 (push) and 42581134827 (pull_request) on 66f1431 read step by step, success on every one of 23 named steps; merged by rebase at 02:55:29 EST as 8507464 (tree identical to 66f1431), no auto-merge; CI run 42582372459 on main at 8507464, success, 26 steps, none other than success. The branch stays on origin as the 40 before it.

**Agent involvement.** None. This session ran on Sonnet 5.5 for the records turn of 2026-11-08 and on Fable 5.1 from his `/model` command at 02:3x on 2026-11-09, with no subagent and no workflow. The heavy-run lock was held 02:36:05 to 02:42:13 for the kernel gate and the hook, taken when zisr-tak released it with no waiting file present.

**Battery for this commit.** All twenty-two preflight commands exit 0 on the tree (02:58:05 to 02:58:59), the hook runs again at the commit, hygiene and both diff checks on the final text. The kernel gate was not re-run for this records-only change: the tree differs from 8507464 in the handoff, this record and its archive alone, which hygiene reads.

**Extraction.** SINCE_LAST_RECORD_2026-11-09_closeout.md beside the record in Z-ISR/_session-artifacts/2026-11-06-plainsight-resume/, over this session's whole transcript (30988045): 598 entries, 0 typed, 1 click (15:45:31 on 11-08, "Yes, resume here", read against the offer at 15:43:54), 2 harness notices (the parent's relays), 5 sent, 0 received. Controls first: the self-test's 22 checks with 4 controls refusing, a 2027 stamp giving 0 entries, a since without a zone refused.

**Open.** Items 5 to 8 of the 10-28 list, not started by the parent's reading of his line; the extractor's list fix, unstaged in the working tree for its own Class B commit; his: the DA-R2 stamp and the pin self-test's absent-file example at that commit, readings O-R1 to O-R9 and the rest, the 28 queue items, the mock-up adjustments, VMs, domains, SIMs and the Track B identity acts.

---

## 2026-11-09, the extraction tool's list-of-blocks fix committed, the closeout's CI run read, and the lane carried to the freeze of 2026-11-11, under the maintainer's clicks of 14:08:53 and 14:13:10.

**Class:** B. `tools/since_last_record.py` changes behaviour: a prompt or content the harness wrote as a list of blocks is read as its text blocks joined, where the committed tool stopped with a traceback (`AttributeError: 'list' object has no attribute 'strip'` in `_clean`, seen this afternoon on a planted record run against the committed tool before the fix was staged). The self-test gains a planted `queued_command` attachment whose prompt is a list of blocks and the check that it is read as its text, 21 checks to 22. `CHANGELOG.md` takes an entry. No doctrine, spec, schema, policy, ontology, runtime, gate or value changed, and no classification rule of the tool, so a transcript the committed tool could read gives the same counts.

**The words this commit acts on.** Two clicks of his in the parent's chat, verified in the parent's transcript (434c9ac5, user records at 2026-11-09T19:08:53Z and 19:13:10Z): "Yes, carry it" at 14:08:53 EST on 2026-11-09, answering "Carry your overnight line into these three days?", which carries his typed line of 02:27:22 ("You are good to adjudicate any commits, merges, pushes, deploys etc as needed so long as they pass repo documentation and established tests, conformance and validations") to 18:00 EST on 2026-11-11; and "Yes, resume it" at 14:13:10, answering "Resume PLAINSIGHT under the same line?", after the parent had told him the line would let this lane commit the extractor fix and work through items 5 to 8 with the TMN lanes first on heavy runs. The parent (local_88a0656e) relayed both at 14:14 and gave its go in advance for each commit and merge in that work meeting five conditions: the kernel gate 0 failed on the exact tree committed, the hook passing, hygiene passing, this repository's documentation allowing a delegate's word for the commit's class (no Class F decision is covered), and for a merge CI green on every step at the exact head, never with --auto. Read as the line was read last night: a click on an offered action is his word for the act the offer named, a relay found verbatim in the parent's record is his word here by the terms of his click of 15:45:31 on 11-08, and the parent's go, measured per act against the conditions, is the per-act instruction CLAUDE.md R6 and AGENTS.md section 4 ask for. No merge or push after 18:00 EST on 11-11.

**The closeout's CI run.** Run 42585302360 on main at 6bb3c16: success, 26 steps, none other than success, read at 03:32 EST on 2026-11-09 and owed to this entry by the record folder.

**Agent involvement.** None in this commit; Fable 5.1 in the main loop. Estate: the heavy-run lock was held by zisr-producers from 13:41 with zmeta-spec's waiting file of 13:54 ahead of this lane; waiting-plainsight.txt was written at 14:14:55, and the lock was taken for the kernel gate and the hook only after every TMN waiting file was gone, with the stamps in the battery paragraph.

**Battery.** On the staged tree, under the estate's heavy-run lock, the kernel gate ran twice. The first run (lock taken 14:38:34 EST, after zmeta-spec's waiting file was gone and the producers had released; gate 14:38:35 to 14:42:47) read 25 implemented, 1 failed, the telemetry entry alone, because the waiter's environment carried PLAINSIGHT_NO_GATE_LOG=1, which tools/gate_log.py honours by writing nothing, so two of that entry's twelve tests found no record; confirmed by running tools/tests/test_gate_log.py both ways on the checkout, 2 of 12 failing with the variable and 12 ok without it. The pre-commit hook on the same tree exited 0 (14:42:47 to 14:43:32), and the lock was released at 14:43:32. The second run, from a fresh script with the variable unset (lock 14:44:24, gate 14:44:24 to 14:48:39, released 14:48:39): 25 implemented, 0 failed, 4 unratified and refusing, 1 stubbed, 2 pending, exit 0. Nothing in the tree changed between the two runs; this paragraph was written after them, and the hook, which runs hygiene, ran again at the commit on the exact tree. Hygiene on the records: 21 governed files, 5 voice-exempt, exit 0; both diff checks clean; the self-test 22 checks, 15 planted lines, 4 controls refusing (the committed tool: 21 checks); the control seen first: the committed tool stopped with the traceback on the planted record (exit 1) and the fixed tool listed the line as QUEUED (exit 0). The worklog's oldest entry (2026-10-23) moved to the archive without edit, 149 lines out and 149 in.

**Open.** Items 5 to 8 of the 10-28 list, in number order under the same conditions, each its own commit and merge reported to the parent in one line: 5, the application's slices 2 and 3; 6, the UI/UX harvest synthesis of plan item 0.7; 7, Step 11 drafted refusing; 8, the two Class B manifest gaps (BRIEF_item8_manifest_gaps.md in the 2026-11-02 record folder). His: the DA-R2 stamp and the pin self-test's absent-file example at that commit, readings O-R1 to O-R9 and the rest, the 28 queue items, the mock-up adjustments, Patch 4b's Class F items, `synthetic/CAST.md`, VMs, domains, SIMs, accounts and the Track B identity acts, secrets, tags, mints and anything live.

---

## 2026-11-09, item 5 built: the application's slice 3 (analyst acts through the door, the Merge Sheet, the review strip) and the runner's watchdog, under the maintainer's clicks of 14:08:53 and 14:13:10.

**Class:** C, runtime code with a design amendment per departure (9.16, 9.17 and 9.18), as the 10-28 record set for item 5. No doctrine, spec, schema, policy, ontology, synthetic or corpus file changed; `CHANGELOG.md` takes an entry. One value the change adds is Class F by effect and ships refusing: `LOCAL_ACTS` in `app/config.py`, False until he sets it (reading APP-R31, below).

**The words this commit acts on.** His clicks of 14:08:53 and 14:13:10 EST on 2026-11-09 in the parent's chat, verified in the parent's transcript and recorded in this file's previous entry, carrying his line of 02:27:22 to 18:00 EST on 2026-11-11, with the parent's go given in advance for each commit and merge of items 5 to 8 that meets its five conditions; this commit's are measured in the battery below.

**What exists now.** POST `/api/cases/{case}/acts` (`app/http/acts.py`, `app/http/routes.py` h_acts) mints one ADJUDICATE_EVENT (VERIFY, DISPUTE, NOTE, QUESTION, IGNORE, REVOKE, PROMOTE) or IDENTITY_EVENT (CLUSTER, EXCLUDE) per request from a closed body of the act, its target and the fields the layer model requires, under the session's `--analyst`, and sends it through `ingest_batch` with the origin "act": `tools/validate.py` by path, the store checks, one transaction, the notice. The server fills event id, timestamp, producer, source and lineage, refuses an unknown key or act before the door, and returns a fired validator code as ACT_REFUSED_BY_MODEL with the codes named. It copies no rule of the model and checks the facts the validator cannot see: an item already promoted (ACT_TARGET_ALREADY_PROMOTED), a target already revoked (ACT_TARGET_ALREADY_REVOKED), a member that is not an entity or referenced-only node (ACT_MEMBER_KIND_REFUSED), and the runtime half of ADJUDICATION_REASON_MISSING for IGNORE (ACT_REASON_REQUIRED). `ingest_batch` gains an origin and `origin_allowed`: a minted event lands only in a held case; on LOCAL an act lands nowhere until `LOCAL_ACTS` is set (ACT_LOCAL_PENDING_DECISION) and then only in a case the registry marks synthetic (ACT_LOCAL_SYNTHETIC_CASE_ONLY), which also governs the watchdog's system event. `runner/watchdog.py` closes an open coverage interval whose last verification is older than three poll intervals by one SYSTEM_EVENT COVERAGE_INTERVAL through the door, t_end at the last verification, producer runner-watchdog, and leaves a row with no recorded verification state or method open, reported as VERIFICATION_STATE_UNKNOWN; it runs as `python -m runner.watchdog`. The INSPECTOR lists the adjudications of the selected node's events as consequences (`app/model/reads.py` adjudications, `app/model/inspector.py`), and the node description exposes its creating event. `app/static/views/acts.js` builds the eight slice-3 keys: undo as a ten-second cancel window that leaving the page also cancels, the inline act forms, the review strip in the Merge Sheet and the Pivot Bar, and the Merge Sheet itself, committing on its own button; `keymap.json`, `app.js` and `app.css` follow, and v now toggles marks so PATHS takes the first two and the sheet every mark. `app/README.md` gains the Acts and Watchdog sections; `app/__main__.py`'s docstring points the watchdog at the runner's command.

**Readings for him.** APP-R31, where an act lands: an act's payload is stratum 1 by the layer model and its prose is typed at run time, so admitting it to LOCAL widens what LOCAL may hold under EG-2 beyond the tracked, reviewed synthetic file the source rule admits; the route therefore refuses on LOCAL until he sets `LOCAL_ACTS`, and the tests set it in memory to exercise the mechanism. APP-R32, IGNORE's reason: the server reads whether the target is a basis claim of a live cluster or was promoted by another analyst, because the model marks that half runtime. APP-R33, what the server adds: rationale_codes as the union of the per-member seams, last_supporting_ts as the latest basis claim's ts, cluster_id and entity_id as uuid4; a PROMOTE's anchor_selector_type is the analyst's declaration, copied from the claim when absent, and a declared type the claim does not carry renders as the design's unvouched hatch rather than refusing. Amendments 9.16 to 9.18 each end with his decision.

**Agent involvement.** Fable 5.1 in the main loop designed and built it in a detached git worktree in the session's scratchpad (DESIGN_item5.md in the 2026-11-09 record folder, drafted before any edit) while the extractor commit waited on the heavy-run lock, so the checkout's tree stayed equal to the index its gate ran on. One Opus 5.5 verifier, read-only, in agent-slot-2 of the estate (14:45:47 to 14:56:33, no slot waiting file present), ran the new modules, the controls and its own probes: five claims held outright, four held with defects, three confirmed (the watchdog read an unknown verification state as verified; a non-string act gave a 500; help exited 2) and four likely (the Class F reading of acts landing on LOCAL; the Merge Sheet re-reading the wrong member after a review; a queued act reading the case id at send time and dying silently on reload; the toast without its consequence and raw tokens in the adjudication text). Every finding was fixed or accepted as recorded in VERIFIER_item5_opus.md beside the design note; the Class F reading produced `LOCAL_ACTS`. No workflow.

**Battery.** The application suite in the build worktree twice: 214 passed and 1 skipped before the verifier's fixes (248.57 s) and 218 passed and 1 skipped after them (242.79 s), the skip the docker DDL apply; the new modules and the changed static tests 18 passed and the controls 17 passed after the fixes, every new check seen failing under its control; hygiene exit 0 on the worktree and on this tree, after the handoff was brought under its 400-line cap (413 to 394 lines, three paragraphs compressed to pointers); both diff checks clean. The kernel gate on the staged tree under the estate's heavy-run lock, taken at 15:06:16 EST with no TMN waiting file present and no PLAINSIGHT_NO_GATE_LOG in the environment: 15:06:16 to 15:11:05, 25 implemented, 0 failed, 4 unratified and refusing, 1 stubbed, 2 pending, exit 0; the pre-commit hook on the same tree 15:11:05 to 15:11:53, exit 0; the lock released at 15:11:53, with zisr-tak's waiting file of 15:09 next. This paragraph was written after those runs, and the hook, which runs hygiene, ran again at the commit on the exact tree.

**Open.** Items 6, 7 and 8 in order under the carried line; slice 4 (the COLLECTION panel, the retention projection, the RT-11 banner); citation into DRAFT and the ARRIVALS rail; his: `LOCAL_ACTS`, readings APP-R31 to APP-R33 and amendments 9.16 to 9.18, with everything the previous entry lists.
