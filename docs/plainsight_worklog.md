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

## 2026-09-04, the tense rule becomes a gate, and the worklog archive opens.

**Class:** C (`tools/validate_hygiene.py`, the aggregator's description, the
`Makefile` target and help line, the CI step) plus A (`AGENTS.md` sections 5
and 8, the handoff, the worklog, `CHANGELOG.md`, the archive, and its row in
`docs/THE-GAMEPLAN.md` section 2.2).

The entry above landed a rule in `AGENTS.md` section 8 and said in place that no
gate enforced it. Design gate 1 says a rule that lives in a README is not a
rule, and the reason the check was not in that commit was ordering: landing it
before the handoff rewrite would have refused the file being repaired. The
handoff is clean and committed in `377d7d4`, so the ordering reason is gone and
the check lands now.

### The check

`tools/validate_hygiene.py` gains `HYGIENE_HANDOFF_PRE_COMMIT_TENSE`: a
case-insensitive substring test for "untracked" and "uncommitted", scoped to
`docs/plainsight_handoff.md` alone, in the shape of the em dash check. The
refusal names the word, says why the tense is wrong, notes that three commits
shipped it, names the rule, and offers the two legal moves: state what the artifact is in
the tree the commit creates, or say where it lives if it lives outside the
repository. The check is factored into `handoff_tense_findings()` so it can run
on text that is not on disk.

**Measured reach, re-derived rather than carried forward.**
`git show 533da17:docs/plainsight_handoff.md` has thirteen lines containing one
of the two words and one line reading "Neither has been committed": fourteen
wrong lines, thirteen reached. The fourteenth is caught at the closeout or not
at all, and `AGENTS.md` section 8 now says exactly that, as the half of the rule
that stays a sentence.

**The test that fails when the constraint is removed.** `--self-test` plants
each word in four handoff-shaped lines, one of them upper-cased, and asserts one
refusal with the expected code per line; then it runs a clean sample containing
"Neither has been committed" and asserts no finding, so the test also documents
the reach limit. Deleting the body of `handoff_tense_findings()` was tried
before this entry was written: the four planted cases passed and the self-test
exited 1. Restored, four refused, one clean, exit 0. The `validate-hygiene`
target and the CI Housekeeping step both run it.

**One consequence of scoping the check to the handoff.** The handoff can no
longer quote either word, including to describe this check, which is why its
section 4 bullet says "the two pre-commit words" rather than naming them. That
is a cost of a lexical rule and it is accepted; the words belong in this file
and in `AGENTS.md`, not in the one current-state record.

### The archive

The worklog held ten live entries against a ten-entry cap, so this entry could
not be added without moving one. `docs/plainsight_worklog_archive.md` opens
with the Wave 0 entry of 2026-08-26, moved without edit, and the header states
that rule. The cap check counts `## YYYY-MM-DD` headings in the live file only,
so the live count is ten again with this entry. The archive's row in
`docs/THE-GAMEPLAN.md` section 2.2 deferred it until the worklog passed 1,500
lines; it is marked delivered at the cap instead, and the row says so.

### Validation

The five preflight validators, the four self-test suites (60, 16 and 6
deliberate breaks refused, plus the four hygiene breaks), the twelve-case
telemetry suite, the hook, `git diff HEAD --check`, and the kernel gate at six
implemented, zero failed, one stubbed, five pending. The kernel gate's hygiene
line now names the handoff's tense among what it covers.

### Agent involvement, stated precisely

No subagent wrote or drafted the check, the test, or this entry; the parent
session did, reading each file before editing it. A verification pass then
ran over the staged change: three lenses, code and test, record facts, and
voice with cross-file consistency, each with a refuter behind it, six agents.
Twenty-four findings raised, ten above minor; five confirmed, five downgraded,
none refuted.

**What it caught is the rule this change enforces, one level up.** Relabelling
the previous section 0 block as `377d7d4` moved what "the commit that carries
this file" refers to, and three sentences elsewhere in the handoff kept the
old referent: the resume pointer said patch 1 was applied in this commit, the
previous-session block said this commit changes three lines of
`doctrine/DOCTRINE_STATUS.md`, and the state header said the closeout commits
moved records and fact corrections only. A relabel is a tense change, and no
lexical check reaches a pronoun. The pass also found that the archive ended
with a blank line at end of file, which `git diff --check` in the unstaged
form did not see because everything was staged and `git diff --cached --check`
refused; the archive body is now lines 18 to 80 of the old worklog rather
than 18 to 81, and the entry text is unchanged. Smaller: "both process
records" was used to mean three files where the repository uses it for two,
the hygiene footer named one rule for every code where the new code has a
different one, two strings claimed no lexical rule reaches the fourteenth line
where the true claim is that this check does not, the archive header said the
worklog exceeded a cap it never exceeded, and the `Makefile` help line and the
gameplan's deferred row had not moved with the target. All of it is corrected
in this change.

**Refused this session:** nothing collected, no connector executed, no platform
touched, no doctrine criterion amended or stamped, no Class F change proposed.

**Not done:** patches 2 through 4 are still unapplied and the operator decides
patch 4. The hook still does not run the telemetry test, a mechanism choice the
operator has not made. `doctrine/RETENTION_LEDGER.md` and
`doctrine/DISCLOSURE.md` are still owed, the D-001 repo scan is still a stub,
and every basis stamp is still unstamped.

---

## 2026-09-05, closeout checkpoint. The committed tree verified from a fresh clone.

**Class:** A (the handoff, this worklog, the archive). No governed artifact.

`AGENTS.md` section 8 defines a closeout as the battery, the records, and the
commit in one act. Both commits this session, `377d7d4` and `7c14888`, were
closed out that way against the working tree. This checkpoint adds the check a
working tree cannot give: the committed tree, cloned fresh into a scratch
directory, run through every CI step and the whole battery.

### What the fresh clone showed

Every step `.github/workflows/ci.yml` runs passes on the clone: PyYAML present,
doctrine integrity, housekeeping with its new self-test, the twelve-case
telemetry suite, the kernel gate at six implemented, zero failed, one stubbed,
five pending, the hook executable and running, and zero commits in the history
carrying an agent trailer. The remaining preflight validators and the three
older self-test suites pass there too. `conformance/` is absent in the clone,
which is what `CONFORMANCE.md` has said since `377d7d4` and had not said before.

### What was persisted outside the tree

`Z-ISR/_session-artifacts/2026-09-04-plainsight-record-repair/` now holds the
three verification passes behind the two commits as full JSON, every finding
with its quoted text and every verdict with the quote that decided it; the seven
scripts that applied every edit, each of which asserted every anchor unique
before writing; the three workflow definitions with their lens and refuter
prompts; both commit messages; and a README that indexes them and restates what
this session got wrong. A scan of the copied files for the operator's identity
returned nothing. The handoff's section 6 points there, beside the previous
session's review directory, whose `DECISIONS.md` amendment gained a pointer and
a correction: its Part 1 puts the authorization schema at Step 7, and the
register puts it at Step 8.

### The archive, again

The worklog was at ten live entries, so the 2026-08-26 Step 3 entry moved to
`docs/plainsight_worklog_archive.md` without edit, after the Wave 0 entry, and
this entry took its place. Two entries are archived; ten are live.

### The handoff

Section 0 answers the five questions for this commit and relabels the previous
block as `7c14888`. Every phrase whose referent the relabel could move was
grepped for and read, because the previous relabel moved three and a verifier
caught them. The date line now states this session's span and that the clock
rolled to 2026-09-05 during `7c14888`, whose records carry the day they were
written.

### Validation

The five preflight validators, the four self-test suites, the twelve-case
telemetry suite, the hook, `git diff HEAD --check` and `git diff --cached
--check`, and the kernel gate at six implemented, zero failed, one stubbed, five
pending, on the working tree; the same battery on the fresh clone of `7c14888`.

### Agent involvement, stated precisely

No subagent ran for this checkpoint. The parent session did the clone, the
battery, the copying, and the edits.

**Refused this session:** nothing collected, no connector executed, no platform
touched, no doctrine criterion amended or stamped, no Class F change proposed.

**Not done:** patches 2 through 4 are still unapplied and the operator decides
patch 4. The hook still does not run the telemetry test. Step 7 is unblocked and
not started. `doctrine/RETENTION_LEDGER.md` and `doctrine/DISCLOSURE.md` are
still owed, the D-001 repo scan is still a stub, and every basis stamp is still
unstamped.

---

## 2026-09-07, the example persona made fictional, the voice pass harvested, and a stale patch hunk found.

**Class:** A (four advisory documents, `.gitignore`, the three records) plus C
for one fixture string in `tools/tests/test_gate_log.py`, the class this worklog
gave that file when it was created. No doctrine, spec,
schema, policy, or runtime artifact changed.

On 2026-09-05 the operator concurred with the previous rundown's
recommendation to start Step 7 and added two instructions to run first: replace
every variant of their own name in the documents with a made-up one, and pass
every document through the ZMeta Register 1 voice standard, so that Step 7 does
not produce documents that need the same pass. That session applied the
replacement, launched a voice-pass workflow, started two mapping agents for
Step 7, and ended on a usage limit at 20:04 UTC with nothing committed. This
session recovered what it left, verified it, and committed the half that was
finished.

### The replacement

Four documents in `docs/` carried a worked example, the subject in the design
mockups, the persona in the tool review, one line each in the foundation and
the gameplan, whose name and handles belonged to a real person. One fixture
string in `tools/tests/test_gate_log.py` reused the handle. Every value was
replaced with a fictional one of identical length: fifty-five removed lines,
fifty-five added, no length difference in any pair, checked by a script over
the diff, so the fixed-width mockups in the design document kept their
alignment. Six masked email hints, five in the design document and one in the
tool review, still carried the last letter of the old surname, and the tool
review paired one with a candidate it no longer matched; the records verifier
described below found them, and they were corrected, same length, before the
commit. A tree-wide case-insensitive search for every variant returns nothing. The
battery is green on the result. This entry, the handoff and the changelog name
neither the old values nor the new ones; the diff carries them.

The old handle remains in `5d53973` and `d99f213`. A history rewrite is the only
thing that removes it, there is no remote yet so a rewrite is feasible, and every
record here cites hashes a rewrite would change. That is the operator's decision
and it falls due before the first push.

`.gitignore` gains `_voice-pass/`, the directory the voice pass writes its
survivor files into, so that working material cannot enter a commit.

### The harvest

The voice-pass workflow cut sixteen files into 58 chunks of about 1,500 words:
`README.md`, `CLAUDE.md`, `AGENTS.md`, `CONFORMANCE.md`, the five doctrine
files, `synthetic/CAST.md`, the handoff, and the five rank-7 documents in
`docs/`. The worklog, its archive, the changelog and the doctrine status pin were
excluded by rule. Each chunk had a lens that drafted paragraph-level edits with
the exact original text and a refuter, default REJECT, that checked anchors and
meaning and wrote the survivors to `_voice-pass/`. Doctrine chunks carried extra
rules: no criterion paragraph, no enforcement pointer, no counted phrase, no
table.

| Stage | Count |
|---|---|
| Lens agents that returned | 57 of 58 |
| Edits proposed | 814 |
| Refuter agents that returned a verdict | 6 of 56 started |
| Refuter agents that failed on the session limit | 50 |
| Survivor files written | 9, three of them without a returned verdict |
| Drafts passing the applier's mechanical checks | 719 of 814 |

Of the 95 mechanical refusals, 69 changed a number, 14 kept an em dash in the
replacement, 12 compressed, and one has an anchor that is not unique; one draft
carries two of those reasons. All 556
em dashes in tracked markdown sit in the five `docs/` files the hygiene gate
exempts, so the governed files already pass the mechanical half and the lenses
on them hunted the unchecked half. Nothing is applied. The drafts, the six
verdicts, the survivors, the workflow script and journal, the applier with its
chunk table, and the two Step 7 mapping reports are copied to
`Z-ISR/_session-artifacts/2026-09-05-plainsight-voice-pass/` with a README,
because the previous session's scratchpad is a temp directory. A scan of that
directory for the operator's identity returned nothing.

One tension surfaced. The handoff records `docs/PLAINSIGHT-FOUNDATION.md` as
voice-exempt, a record of intent. The pass drafted 114 edits for it across five
chunks, because the operator asked for all documentation. Which of the two
holds is the operator's call and is recorded in the handoff.

### The stale hunk

The handoff and the 2026-09-04 amendment to `DECISIONS.md` both said patches 2,
3 and 4 still applied in order. Measured on a fresh clone of `2d406db`: patch 2
applies clean; patch 3 fails on its second `doctrine/HYGIENE.md` hunk, which
anchors on a sentence `377d7d4` rewrote when patch 1 landed with the docstring
correction, and the tree already carries the corrected claim that hunk was
drafted to add, so the hunk is stale in intent as well as anchor. Patch 3 has
thirteen hunks, two in HYGIENE.md: `git apply --exclude` lands the eleven
outside that file, the first HYGIENE.md hunk applies alone and is saved beside
the patches as `patch-3b-hygiene-first-hunk-only.patch`, so twelve of thirteen
land, and patch 4 applies on top. The fully patched tree passes the kernel gate
and `tools/validate_doctrine.py` counts 59 criteria there. The handoff is corrected in this commit and `DECISIONS.md`
gains a dated amendment. The claim had been false since `377d7d4`.

### The archive

The worklog was at ten live entries, so the 2026-08-26 entry that begins "Step
3 continued" moved to `docs/plainsight_worklog_archive.md` without edit, after
the two already there, and this entry took its place. Three entries are
archived; ten are live.

### Validation

The five preflight validators, the twelve-case telemetry suite, `git diff
--check` and `git diff --cached --check`, the hook at commit, and the kernel
gate at six implemented, zero failed, one stubbed, five pending, on the working
tree before staging and on the staged tree. Three Sonnet verifiers, each told to
run the command and quote the output, re-derived the 22 state claims in the
rundown given to the operator: 21 confirmed, one refuted for how a transcript
filter was described, a detail no fact depended on. A second pass over these
records before the commit, one Sonnet lens for the mechanical checks and one
Opus lens for the five questions, tense, voice and consistency, returned 20
verdicts: 18 confirmed and 2 refuted. One refutation was of the brief rather
than the record, a heading count the parent stated wrong in the prompt. The
other was the class of the fixture change, B in the draft and C by `AGENTS.md`
section 3 and this worklog's own precedent, corrected above. The Opus lens also
found two things outside its questions: a hunk count of twelve that the exclude
command alone does not deliver, corrected above with the hunk-level route, and
the six masked hints described under the replacement. Both passes are in this
session's workflow journals.

### Agent involvement, stated precisely

The 2026-09-05 session ran 114 workflow agents, a lens and a refuter for each of
58 chunks: the 29 chunks over the rank-7 documents on Opus, the 29 over governed
files and the handoff inheriting the session model. It ran two Explore agents on
Opus for the Step 7 maps. Its parent applied the replacement with a script that
asserted every count before writing. This session's parent did the harvest with
Python over the workflow journal, wrote the artifacts directory, and wrote these
records; no subagent edited a tracked file. Three Sonnet verifiers spent about
198,000 tokens on the state claims, and a Sonnet lens and an Opus lens about
201,000 on these records. The commit was executed by
the agent on the operator's instruction of 2026-09-07 for this act, with the
operator as author, per R6 as amended.

**Refused this session:** nothing collected, no connector executed, no platform
touched, no doctrine criterion amended or stamped, no Class F change proposed,
no voice edit applied.

**Not done:** the refuter pass over 50 chunks and the application of any
survivor; patches 2 through 4; the history decision; Step 7;
`doctrine/RETENTION_LEDGER.md` and `doctrine/DISCLOSURE.md`; the D-001 repo
scan; every basis stamp.

**Next:** the operator stands up the remote. Then, in the operator's stated
order: patch 2 and the twelve applying hunks of patch 3 before any doctrine
voice edit, the refuter continuation and the application of survivors, then
Step 7.

---

## 2026-09-07, the history rewritten before the first push, and the public-facing files added.

**Class:** A for the records, `README.md`, the new `LICENSE`, `NOTICE` and
`.gitattributes`, `.gitignore`, the CI permissions block, and hash strings in
`AGENTS.md`, `CONFORMANCE.md` and the status lines of six doctrine files, one
added sentence in `AGENTS.md` section 4, plus C for six hash strings in `tools/validate_hygiene.py`, one of them inside the
self-test fixture, the class the previous entry gave a fixture string. No
criterion, no stamp, no schema, policy, connector, or validator logic. The push that follows is Class E,
publication outside the team, and is executed on the operator's instruction.

Later on 2026-09-07 the operator created a public repository for this project
at `github.com/JTC-byte/PLAINSIGHT`, chose the Apache License 2.0 there, and
asked for the repository to be cleaned up and locked down so that it could be
pushed clean, with the working copy kept as a local instance where experiments
run and the public repository updated from their results. Three things in the
history were not publishable. The two earliest commits carried the example
persona's real name and handles in five files, which the previous entry's commit
had replaced only at the tip. Every commit carried the operator's personal email
address as author and committer, an address that contains their name. Four
documents carried absolute paths from the operator's machine. The remote itself
already held one commit, GitHub's own license file, authored with that same
address, so the first push replaces it by force; that commit is no ancestor of
`main`.

### The rewrite

`git filter-repo` 2.47.0, installed into the user site for the purpose, ran on
a fresh clone with two inputs, both persisted in
`Z-ISR/_session-artifacts/2026-09-07-plainsight-history-rewrite/`. The
replacement map carries the fourteen literal and two word-bounded rules that
reproduce the previous commit's persona replacement, proven first by applying
them to the five files as they stood before that commit and comparing the
result byte for byte with the files as that commit left them, plus four rules
that turn the machine paths into `<Z-ISR>` and `<wave-0-scratchpad>`. The
mailmap turns the author and committer address into the GitHub no-reply address
for the account. Nine commits went in and nine came out. A bundle of the complete pre-rewrite history was
written beside the inputs before the real repository was touched.

Verification on the rewritten clone: the tip tree compared to the pre-rewrite
tip blob by blob differs in four files, `docs/DOCUMENT_STANDARD.md`,
`docs/OSINT-COP-tool-review.md`, `docs/THE-GAMEPLAN.md` and the handoff, and
in each only in the lines that carried a path; a search of every rewritten
commit for the old persona values, the old address, and the machine paths found
nothing; all nine commits carry the no-reply address; the five validators, the
hygiene self-test, the telemetry suite and the kernel gate pass on the tip.
`git filter-repo` also translated the hash references inside commit messages,
so a message that cited an earlier commit cites its rewritten form.

One consequence is recorded rather than hidden. The previous entry's commit
described replacing fifty-five line pairs; in the rewritten history those
values were already fictional in the first commit, so that commit's diff now
carries only its records and `.gitignore` changes while its message still
describes the replacement. The message is true of what was done on 2026-09-05
and 2026-09-07 and is left as written.

### The hash translation

Every hash cited in a current-state file was translated: 4 tokens in
`AGENTS.md`, 3 in `CONFORMANCE.md`, 1 in `README.md`, 6 in
`tools/validate_hygiene.py`, and 15 across six doctrine files, all in status
lines or prose about which commit landed what, none in a criterion. The
handoff was rewritten with the new hashes. The worklog, its archive, and every
changelog entry below this one keep the hashes they were written with,
because a process record is never restyled; the changelog entry for this commit
carries the table.

| Before | After | Subject |
|---|---|---|
| `5d53973` | `1abb354` | Wave 0: governed repository, doctrine foundation, and the doctrine gates |
| `a54061b` | `4c5cd25` | Hardening: rank 1 grows to four files, plus gate telemetry |
| `d99f213` | `f4e00e1` | Review wave: two blockers, Steps 4 through 6, and the first test |
| `8a856b3` | `98f3433` | Closeout: the changelog this repository owed, and the handoff standard |
| `533da17` | `d803213` | Record 8a856b3 in the changelog, and end the entry regress by rule |
| `377d7d4` | `89c68a3` | Separate the two records by tense, and clear the pre-commit tense from every file that carried it |
| `7c14888` | `f907a7a` | Make the handoff tense rule a gate, and open the worklog archive |
| `2d406db` | `7c0e278` | Closeout checkpoint: the committed tree verified from a fresh clone, and the session's records persisted |
| `b6d0bb2` | `595cc06` | Make the example persona fictional, and correct the records' patch state |

### The public-facing files

`LICENSE` is the Apache License 2.0 text as GitHub generated it in the remote's
initial commit, byte-identical: blob `261eeb9`, recorded in the rewrite
directory's README so the claim can be checked without the remote. `NOTICE` names the copyright holder and states
the ZMeta derivation in the words ZMeta's own trademark guidance accepts, a
private ZMeta-derived dialect with no upstream compatibility claim, and links
the public `zmeta-spec` repository. `.gitattributes` puts LF in the index and on
every checkout, which ends the CRLF churn the records of the last three sessions
kept noting. `.gitignore` gains editor, OS and agent residue. The CI workflow
declares a read-only token. `README.md` gains a section on the license and on
the model by which the public repository is updated. The branch is renamed from
`master` to `main`, which is the remote's default.

### The archive

The worklog was at ten live entries, so the 2026-08-26 entry that begins "Step
2. The operator decided twelve items" moved to
`docs/plainsight_worklog_archive.md` without edit, after the three already
there, and this entry took its place. Four entries are archived; ten are live.

### Validation

On the rewritten clone with this commit staged: the five preflight validators,
the hygiene self-test, the twelve-case telemetry suite, `git diff --cached
--check`, the hook, and the kernel gate at six implemented, zero failed, one
stubbed, five pending. A verifier pass over the staged package, one Sonnet lens
for the mechanical checks and one Opus lens for the five questions, tense,
voice, consistency and class, returned 30 verdicts: 23 confirmed and 7 refuted.
One refutation was of the brief, a `check-ignore` invocation without the
trailing slash the directory-only rules need. One was a reasoned view rather
than a defect: the repository URL contains the account login, which a literal
reading of `AGENTS.md` section 4 calls a handle, and the lens argued the rule
does not reach the repository's own coordinates and proposed a one-clause
carve-out; the operator decided it, and `AGENTS.md` section 4 gains that
sentence in this commit. Five were corrected before the commit:
the scratch clone still resolved the author identity from the global
configuration, which the apply order now sets before any commit; the handoff
read pre-rewrite hashes by date where the persona entry of the same day also
carries them, now read by position; the handoff credited the hook with a
selector refusal it does not perform, now stated as the D-001 stub; one
fragment in the commit message; and this class line, which understated the
`tools/validate_hygiene.py` change.

### Agent involvement, stated precisely

The parent session did the scouting, the map, the rewrite, the comparisons and
the record writing; it installed `git-filter-repo` into the user site. No
subagent edited a tracked file. A Sonnet lens and an Opus lens spent about
202,000 tokens on the staged package. The commit and the push that
follows it are executed by the agent on the operator's instruction of
2026-09-07 for those acts, with the operator as author, per R6 as amended.

**Refused this session:** nothing collected, no connector executed, no platform
touched, no doctrine criterion amended or stamped, no Class F change proposed,
no voice edit applied.

**Not done:** the repository settings that lock the remote down after the push;
the refuter pass over 50 voice-pass chunks and the application of any survivor;
patches 2 through 4; Step 7; `doctrine/RETENTION_LEDGER.md` and
`doctrine/DISCLOSURE.md`; the D-001 repo scan; every basis stamp.

**Next:** the push, then the remote settings. Then, in the operator's stated
order: patch 2 and the twelve applying hunks of patch 3 before any doctrine
voice edit, the refuter continuation and the application of survivors, then
Step 7.

### Postscript, 2026-09-08: the first CI run failed on the hook

The push went through late on 2026-09-07, replacing GitHub's initial commit by
force, and the CI run on the publication commit failed at the step "Pre-commit hook is executable
and runs". `.githooks/pre-commit` has had mode 100644 in every commit since
Wave 0, and the bundle of the pre-rewrite history confirms the rewrite did not
change it. Every record that reported the hook executable, including this
worklog's 2026-08-27 and 2026-09-05 entries, described a Git Bash check on
Windows, where `test -x` is true for any file with a shebang line. This was the
first time the check ran on Linux. The closeout checkpoint after the
publication commit sets the mode to 100755, records it in the changelog and in
this postscript, and rewrites the handoff to the state after the push.

Two more things observed after the push. GitHub still serves the replaced
initial commit by hash, as expected for an unreachable commit until GitHub
collects it; a support request can remove it sooner. The repository showed as
private when the lockdown settings ran, so branch protection was refused on the
free plan and secret scanning reports disabled; wiki and projects are off, and
Dependabot alerts and security updates are on. The visibility is the operator's
setting and is recorded here as found.

---

## 2026-09-08, the repository goes public, the review's patches land, and Step 7 is built.

**Class:** B for the schema, the four policy files, the two corpora and the
contract, all new and all generated or written from the layer model; B for the
doctrine text of patches 2, 3c and 3b, of which patch 2's change to SS-4's
table is Class F by effect, decided by the operator as R4 on 2026-08-26 and
instructed for landing today; C for three new tools, the `schema` entry in the
aggregator, the hook's seventh command and the Makefile targets; A for
`CONFORMANCE.md`, `docs/THE-GAMEPLAN.md`, the pin of record's pending and
readings rows, and the records. No stamp. Patch 4 is not applied. The commit is
executed by the agent on the operator's instruction of 2026-09-08 for that act,
with the operator as author, per R6 as amended.

### The harvest

The previous session ended at `6247953` and nothing followed it. Its three
verification workflow results, the edit lists that applied each record, the
three commit messages and the rewrite script lived only in the session directory
and are now under `verification/` in
`Z-ISR/_session-artifacts/2026-09-07-plainsight-history-rewrite/`, indexed in
that README. CI on `6247953` is green on every step, which the handoff could not
record. A dry run of the patches against the tree refuted one sentence in the
handoff: the hash rewrite did move a patch-3 anchor, the status line in
`doctrine/CREDENTIAL_LIFECYCLE.md` whose `a54061b` became `4c5cd25`, so patch 3
with the HYGIENE.md exclusion no longer applied. `patch-3c` is patch 3 with
that one token translated, and DECISIONS.md gained a dated amendment.

### The repository goes public

The operator flipped it during the session. Branch protection on `main` now
refuses force-pushes and deletions, requires linear history, includes admins,
and sets no required status check, because required checks would reject every
direct closeout push. Secret scanning and push protection are on. Non-provider
pattern scanning would not enable through the API on this plan.

### Three decisions

The operator asked for a first full investigation against consenting subjects
and, after the distance to it was laid out, decided three things: the voice
pass is parked, since it is not on the path to a run; patches 2, 3c and 3b land;
Step 7 starts. The patches applied cleanly to the working tree, the battery
stayed green with doctrine at 58, and patch 4 was regenerated against the
result as `patch-4b`, six hunks, which a scratch clone shows applying with
`tools/validate_doctrine.py` counting 59 there. It is not applied.

### Step 7

`tools/generate_pse.py` reads the layer model and the registry and writes the
schema and the four policy files; `--check` regenerates in memory and refuses
drift. The generation contract left about twenty things unstated, and the
generator takes seven readings rather than inventing rules, recorded as S7-R1 to
S7-R7 in the schema's `$comment`, in `policy/semantics.yaml`, in the contract
and in the pin. The first run of S7-R1, the rule for which optional fields a
subtype may carry, put `exit_criterion` on every SYSTEM_EVENT subtype including
the heartbeats; the rule was tightened so a field a rule requires is not a free
optional and a condition's value narrows to the subtypes whose enum carries it,
and the second run put it on CREDENTIAL_STATE alone.

`tools/validate.py` is rung 2. Schema failures are named through a code map
rather than reported as keywords; producer authority runs before any semantic
check; the denylist walks the payload recursively; a rule that requires a field
owns that field's shape failures, which is how a missing `purpose_hash` fires
`CASE_PURPOSE_UNBOUND` rather than the generic code; lineage is checked at
subtype granularity with the D5 line bound to `SUBJECT_NOT_AUTHORIZED`; the
citation, promotion, adjudication and circularity rules resolve against a case
index. It does not short-circuit on a schema failure at all, and records the
checks it could not reach when a type is unknown. Its self-test removes five
things and asserts the matching fixture stops failing each time.

`tools/build_corpus.py` writes one synthetic case of 44 events covering all 37
subtypes in one lineage chain, and 98 must-fail fixtures: the thirteen the
model's map names for this corpus, the D5 shape twice, one per prohibited group
of every type, and one per envelope, lineage, producer and rule code. Every
value is a bracketed placeholder and every id is a uuid of a label. The first
grading run failed 13 fixtures for two causes, a null `motivated_by` on a seed
run read as a missing field and the producer check running against a subtype
the schema had already refused, plus one `false`-schema error that jsonschema
reports with no validator and an empty path. All three are fixed in the runner
and the second run graded clean. Five codes have no fixture and the builder
prints them on every run.

`spec/pse-semantics-contract.md` was written last, after everything above was
green: thirteen sections, an enforcement label on every rule, sections 5 and 12
marked as the stamp targets SS-14 item 6 names, and the seven readings and the
one promised-but-absent fixture stated in section 13. The `schema` entry in
`KERNEL_GATE` turned implemented, the hook and `make preflight` gained
`tools/validate.py --kernel`, and the gate reports seven implemented, one stub,
four pending. Hygiene governs the contract as its twentieth file and found no
voice or citation defect.

### The provisioning question

The operator asked where to host the ISOLATED environment, which SIMs to buy,
and what to stand up in Cloudflare or DigitalOcean. The answer is
`Z-ISR/_session-artifacts/2026-09-08-plainsight-provisioning-plan/PROVISIONING_PLAN.md`,
outside the repository because it names providers and hardware the doctrine
deliberately does not. A follow-up on routers and carriers ran as a workflow of
36 agents on Opus, seven research lenses and one refuter per decision-bearing
claim under a refute-by-default brief with a fetched page required: 18 confirmed,
10 refuted. The refutations mattered. Dual SIM is not dual modem; the topology
lens's primary router pick, the RUTX50, has no FCC grant; the cheap MVNO phone
plans that would do both jobs in one SIM forbid a SIM in a router in their own
terms; the plans that permit a router are data-only, so two lines per persona
is what the ToS-clean shape costs; and the premise that a consumer prepaid
line's public address is stable for a session's life is unverified anywhere.
The plan's section 10 carries the recommendation, one single-modem router per
persona with a one-router test before a fleet, and the research is persisted
beside it.

### Agent involvement, stated precisely

The parent session did the harvest, the patch dry runs, the lockdown calls, the
provisioning plan, the generator, the validator, the corpus builder, the
contract, the record edits and this entry. The only workflow was the research
one, on Opus throughout, and no subagent edited a tracked file. The operator
decided the three items, instructed the patches, and instructed the closeout
commit. No push has been instructed at the time of writing.

**Refused this session:** nothing collected, no connector executed, no platform
touched, no doctrine conclusion amended or stamped, patch 4 not applied, no
voice edit applied, no generated file edited by hand.

**Not done:** Step 8 onward; the patch 4b decision; the review this step is
owed, on the 2026-09-04 method; `tools/validate_ontology.py --corpus`, whose
trigger has fired; the `AGENTS.md` section 5 command count; `RETENTION_LEDGER.md`
and `DISCLOSURE.md`; the cast; every basis stamp; the one-router test, which is
the operator's.

**Next:** Step 8, compiling the doctrine to policy, beginning with the
authorization schema from SS-4's corrected table. In parallel, the operator's
track from the provisioning plan.

---

## 2026-09-11, the harvest closes a gap, the fires_when fix lands, and Step 8 is drafted unratified.

**Class:** B for the Step 8 policy, schema and conformance artifacts, every one
hand-authored, drafted UNRATIFIED, and refusing until a doctrine stamp exists;
B for quoting every `fires_when` value in `spec/layer-model.yaml` and
regenerating `policy/violation-codes.yaml`; C for
`tools/validate_authorization.py`, `tools/validate_retention.py`, check L-34 in
`tools/validate_layer_model.py`, the aggregator's three new entries, the hook
and the Makefile; A for the sibling repoint, the `.gitignore` line, the CI
action pins and the records. No doctrine file was edited, no conclusion was
amended, and no basis was stamped. The pushes of `4e6abda` and `38c93cc` are
Class E, publication outside the team, executed by the agent on the operator's
instruction for those acts, with the operator as author, per R6 as amended.

### The harvest

This session refreshed and harvested seven Claude app sessions across two
accounts. One of them had never been read. Team-account session `83d21a8e` was
worked on 2026-09-09 from 22:33 to 22:44, after that day's harvest session had
closed at 17:40, so no record written that day could have seen it. It produced
a cost rollup and a request for a visualizer, and it changed nothing in the
repository.

The rollup prices four shapes: the test kit at 244 dollars non-recurring and 59
a month, three personas at 732 and 153, five personas at 1,220 and 199, and six
personas at 1,464 and 222. With the unpriced items estimated, five personas is
about 1,720 non-recurring and 205 a month. The rollup also puts the SS-14 item
6 fork at about 1,040 dollars in year one.

The desktop app's session metadata has moved. It now sits under
`AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude-code-sessions\`,
which is where the next harvest looks first.

### The fires_when fix, and the hole it exposed

`38c93cc` quotes all 57 `fires_when` values in `spec/layer-model.yaml`,
regenerates `policy/violation-codes.yaml`, and adds check L-34,
`CODE_ENTRY_KEYS`, to `tools/validate_layer_model.py`. The numstat is 25 added
and 17 removed in the policy file, 57 and 57 in the layer model, and 55 and 1
in the validator, which carries the check and the fixture correction together.

Two prior sessions recorded that fix as green. It was not.
`tools/validate_layer_model.py --self-test` exited 1: the `dead_code` fixture
appended a code entry with no `fires_when`, so L-34 fired alongside
`LM_CODE_UNREFERENCED` and broke that row's `expect_only`. This session gave
the fixture a `fires_when` value, and the self-test now reports 62 deliberate
breaks, 62 refused, 50 by the expected code alone, 12 cascading, and 44
distinct codes exercised.

The reason two sessions missed it is worth recording, because it is a hole in
the gate battery rather than a lapse of attention. No gate in the repository
runs that self-test. `tools/validate_conformance.py` invokes the validator with
`--quiet`, `.githooks/pre-commit` runs seven plain commands, `make preflight`
runs eight, and `.github/workflows/ci.yml` runs one self-test, hygiene's. Only
`make validate-layer-model` runs it. A self-test that no gate runs is
documentation rather than a mechanism, which is design gate 1 failing in the
place it is hardest to see, inside a tool whose other modes are green.

### The sibling repoint, the ignore line, and the action pins

`../zisr-recon/` ceased to exist on 2026-09-10, when four producer repositories
were consolidated into `../zisr-producers/`. PLAINSIGHT was not in scope and
did not move. Nineteen citations across eight files named the old path.
`ff016af` repoints the three that describe the current tree, `README.md` and
two `AGENTS.md` pointers, to `../zisr-producers/recon/`. The dated measurements
in `doctrine/` and `docs/` and the worklog archive keep the old path, because
rewriting a record falsifies what was true when it was written.

`tools/validate_hygiene.py` cannot see this class of breakage. Its
`PATH_REF_RE` is anchored to in-repo prefixes and skips sibling paths by
design, so a sibling citation that moves is invisible to the whole battery. The
missing mechanism is the real item, and `ff016af` does not close it.

The same commit carries three smaller corrections. `LOCAL_*.md` is now in
`.gitignore`, because the operator's account and provisioning checklist lives
in the working tree and carries operator identity that no existing rule
covered. CI pinned `actions/checkout@v4` and `actions/setup-python@v5`, both of
which run on Node 20, and GitHub removes Node 20 from the runners on
2026-09-16; they are now v5 and v6. `AGENTS.md` said the pre-commit hook runs
six commands, and it runs seven. `ff016af` is one commit ahead of `origin/main`
and its push has not been instructed.

### Step 8, eight artifacts, all of them refusing

Step 8 compiles doctrine to policy. It is drafted, every artifact is marked
UNRATIFIED, and every artifact refuses until a doctrine stamp exists. Eight
artifacts, 9,342 lines:

| Path | Lines |
|---|---|
| `policy/subject-authorization.yaml` | 1,403 |
| `policy/retention.yaml` | 1,617 |
| `schema/subject-authorization.schema.json` | 393 |
| `conformance/gate/decisions.jsonl` | 21 |
| `conformance/gate/README.md` | 548 |
| `conformance/retention/shred-roundtrip.yaml` | 542 |
| `tools/validate_authorization.py` | 2,713 |
| `tools/validate_retention.py` | 2,105 |

Both policy files are hand-authored. `tools/generate_pse.py` owns exactly five
outputs and neither of these is among them, so each file carries a header
saying so; a policy file that looks generated and is not is the kind of thing a
later session regenerates over. `tools/validate_retention.py` replaces the
D-001 stub.

The kernel gate now holds sixteen entries: eight implemented, three unratified,
five pending. Implemented are doctrine, hygiene, layer-model, cast, telemetry,
retention-repo-scan, schema and ontology. Unratified are authorization,
retention-policy and retention-shred-roundtrip. Pending are
authorization-dispatch-paths, authorization-disjointness, retention-finding,
divergence-register and connector-conformance.

`retention-repo-scan` moved out of STUB. It enforces three of RT-15's four
parts. The code RT-15 names, `FIXTURE_CONTAINS_LIVE_SELECTOR`, is not in the
wire vocabulary, and git history is out of reach of any commit-time check, so
the fourth part stays open and is recorded as open rather than counted as done.

### Step 8's done-when is not met

`docs/THE-GAMEPLAN.md` Step 8's done-when asks that
`tools/validate_authorization.py --fixtures` and
`tools/validate_retention.py --policy --shred-roundtrip` be green, including
the check that an unratified criterion refuses rather than permits. All three
modes exit 1. Step 8 is not done by its own criterion, and nothing in this
entry writes around that.

Every refusal is the designed one. `doctrine/DOCTRINE_STATUS.md` carries no
dated row for any of the eight artifacts, so the gates that read the stamp
table find nothing to permit on and refuse. That is the posture the design
asks for rather than a defect in the artifacts. The one part that is green is
the part the criterion names: a criterion absent from the stamp table refuses,
a missing artifact refuses, and a fully stamped state permits, exercised both
ways by `--self-test`. Closing the done-when is the operator's stamp, and no
agent edit reaches it.

### The kernel gate is red on one check

`tools/validate_conformance.py --kernel-gate` is red, on `retention-repo-scan`
alone. `tools/validate_retention.py --repo-scan` refuses on two filled handle
selectors that predate Step 8: a worked example at line 87 of
`docs/PLAINSIGHT-FOUNDATION.md`, introduced in `1abb354`, which is a rank-7
record of intent, and a designed value at line 894 of
`tools/validate_ontology.py`, introduced in `f4e00e1`, inside that validator's
own negative fixture. Both are true on shape and false in
substance. `docs/PLAINSIGHT-design.md` and `docs/THE-GAMEPLAN.md` already carry
`repo_scan.document_exemptions` rows of exactly this kind, and
`docs/PLAINSIGHT-FOUNDATION.md` does not.

Adding those two rows was proposed and refuted. The proposal cited a rank-1
document above its lane, and narrowing an RT-15 scan is a reach decision, which
belongs to the operator. The question is open at this closeout. The pre-commit
hook is unaffected, because it runs the same mode over the index rather than
over the working tree.

### The decision register

66 unratified placeholders were compiled from the stack. They collapse to 51
distinct decisions, because 15 entries are second or third copies of a question
asked elsewhere. Twenty-two of the 51 are grounded in the stack's own
documentation. Twenty-nine are the operator's, and 25 of those arrive with at
least one option already foreclosed.

The grading was adversarial by construction, and it needed to be. Eight lenses
claimed grounded on 45 entries and the refuters overturned 15, a 33 per cent
over-report. Every overturn ran one direction: a lens produced a real rank-1
quote that settled a neighbouring question, or eliminated two options and
declared the survivor grounded. The register is at
`Z-ISR/_session-artifacts/2026-09-11-plainsight-step8/DECISION_REGISTER.md`,
outside the repository.

### Defects found and not fixed

- **`tools/validate_conformance.py`, lines 137 to 139.** The comment says "six
  of the nine paths" where the tool prints seven refusals.
- **`schema/subject-authorization.schema.json`, `evidence_ref`.** It admits
  only the three pre-R4 evidence kinds, which is what SA-U2 and SA-U11 both
  land on.
- **SA-U16's `decided_at_step` placement.** It is not wire-legal. Line 607 of
  `spec/layer-model.yaml` requires the field on every REFUSED.

### Patch 4b no longer applies

`patch-4b-obligation-drafts-CLASS-F.post-patch-3.patch` does not apply. `git
apply --check` exits 1 on `doctrine/DOCTRINE_STATUS.md`. The cause is a
fifteen-minute race: the patch was regenerated at 2026-09-08 18:40:19 and
`4e6abda` was committed at 18:55:58, adding three rows to the table the patch
anchors on. `git apply --3way` applies the CREDENTIAL_LIFECYCLE.md and
EGRESS.md hunks cleanly and the DOCTRINE_STATUS.md hunk with conflicts, and
union-resolving that one table conflict yields 59 criteria. Line 192 of
`docs/plainsight_handoff.md` asserted that the patch applies, which this
session measured as false.

### The gate battery at the closeout

Green: doctrine at 58 criteria, hygiene and its self-test, layer-model and its
self-test, ontology and its self-test, cast and its self-test, the validator's
self-test, `tools/validate.py --kernel` with 44 must-pass clean and 98
must-fail refused, `tools/generate_pse.py --check`, `tools/build_corpus.py`
with `--check`, the gate-log tests, both forms of `git diff --check`, and the
pre-commit hook.

Red: `tools/validate_conformance.py --kernel-gate`, on `retention-repo-scan`
alone, for the reason given above. The battery is not green at this closeout,
and calling it green would hide the one decision this session leaves open.

Doctrine stands at 58 criteria, every conclusion recorded and every basis
unstamped, unchanged this session.

### The archive

The worklog was at ten live entries, so the 2026-08-27 entry titled "the
doctrine gates. Written before the first commit." moved to
`docs/plainsight_worklog_archive.md` without edit, after the five already
there, and this entry took its place. Six entries are archived; ten are live.

### Agent involvement, stated precisely

The Step 8 artifacts were written by subagents in a workflow. The parent
session ran every gate itself. The parent also did the harvest, the `dead_code`
fixture fix, the two commits and the two pushes, the sibling repoint, the
record edits and this entry.

The grading in the decision register ran eight lenses and eight refuters. Four
of the refuters failed on exhausted Fable usage credits and were re-run on
Opus, and the re-run is the reason the grading can be trusted: before it, the
same groups reported 31 entries grounded; after it, 17. A refuter that cannot
run returns the same silence as a refuter that found nothing, which is the
failure mode the re-run caught.

Step 8 has had no adversarial review. No lens has been run over the eight
artifacts, and nothing in this entry says one has.

**Refused this session:** nothing collected, no connector executed, no platform
touched, no doctrine file edited, no conclusion amended or stamped, patch 4b
not applied, no generated file edited by hand, and no `document_exemptions` row
added to narrow the RT-15 scan.

**Not done:** Step 8's done-when, which only the operator's stamp reaches; the
adversarial review of Step 8, which has not happened; the three defects above;
the patch 4b decision; the repo-scan exemption decision; the push of `ff016af`;
the five pending kernel gate entries; `doctrine/RETENTION_LEDGER.md` and
`doctrine/DISCLOSURE.md`; `tools/validate_ontology.py --corpus`; a gate that
runs the layer-model self-test; a check that sees a moved sibling path; every
basis stamp.

**Next:** the review Step 8 is owed, on the 2026-09-04 method, which is lenses
that run the mechanism and quote the result, each paired with a refuter. Then
Step 9, the divergence register and its validator.

### Postscript, 2026-09-12: the pre-push review, the push, and a CI failure nobody had looked at

The operator asked for a full closeout checkpoint: review what is about to be
pushed, push it, then record everything. This postscript is the record, written
after the push because the push is part of what it records.

**The review.** Six lenses over `ff016af` and `0e0c840` before either left the
machine, each finding paired with a refuter whose default was REFUTED. Fourteen
agents. The lenses were permanence and disclosure, Class F by effect, record
accuracy re-measured from scratch, commit messages against their commits, what
CI would do, and reversibility. Five findings survived refutation, all MINOR,
none a blocker.

Two lenses returned clean. The permanence lens found no selector value, no
credential, no absolute machine path and no personal datum in either commit. The
Class F lens answered the question AGENTS.md section 8 raises, whether a closeout
may carry these artifacts at all: it may, because section 3 rule 2 defines Class
F by effect and nothing can be reached after these commits that could not be
reached before. No doctrine file moved, no stamp was added, the authorization
gate refuses every run, and `retention-repo-scan` became stricter rather than
looser. Compiling doctrine into refusing policy narrows reach.

**Four corrections landed as `132eef0` before the push.** The handoff said five
of SS-14 item 6's eight artifacts exist where seven do, an error inherited from
the previous handoff's counting basis rather than introduced here. The
over-report statistic read 44 claimed and 14 overturned across three records
where the grading artifact measures 45 and 15, a rate of 33 per cent rather than
32; one bad intermediate in the session's fact sheet reached all three records,
and its arithmetic closed against a correct survivor count, which is why it read
as sound. The sibling citation count was eighteen and is nineteen. The worklog
and the changelog cited different lines for the same superseded sentence.

The fifth finding is a defect rather than a figure and is recorded in the
handoff's known gaps: bare `--repo-scan` catches `UnicodeDecodeError` and
continues, so it silently skips any tracked file it cannot decode as UTF-8, and
its own disclosure block does not name that gap. The count is zero today and the
staged mode the hook runs does not share it.

**The push.** `38c93cc..132eef0`, three commits, on the operator's instruction.
`origin/main` and `main` agree. Every commit is authored to the operator and the
history carries no `Co-Authored-By` trailer, which CI refuses.

**What the push found, which is the part worth keeping.** CI had already failed
on `4e6abda` and on `38c93cc`, both pushed earlier the same day, and nobody had
looked. The cause is not the red kernel gate this session documented at length.
It is `DEPENDENCY_MISSING` on `tools/validate.py`: Step 7 introduced a
`jsonschema` import and the workflow's install step names only PyYAML, so that
one check has failed on every run since Step 7 landed. `AGENTS.md` stated the
dependency set as PyYAML alone, so the document and the workflow agreed with each
other and both were wrong.

The lesson is narrow and worth stating plainly. This session verified the battery
locally more thoroughly than any before it, ran a six-lens review before pushing,
and still pushed twice into a red build, because local green and CI green are
different measurements and only one of them was taken. A CI-fetching lens was in
the review and reported what the workflow would do from a fresh clone, which is
how the gap surfaced at all, one push too late. Check the runs after a push, not
only the battery before one.

**Corrected here:** the workflow installs `jsonschema`, and `AGENTS.md` names
both dependencies. The kernel gate stays red on `retention-repo-scan` by design,
so this commit does not turn CI green; it removes a failure that was never
intended and leaves the one that is disclosed.

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
