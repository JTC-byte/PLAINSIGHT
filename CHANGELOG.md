# Changelog

Advisory, Class A. One entry per commit that changed a governed artifact, newest
first, in the shape `ZMeta/zmeta-spec/CHANGELOG.md` uses: what changed, which
surfaces moved, what validation ran, and what did **not** change. The last of
those is the half a reader needs most, because an entry that only lists additions
leaves them guessing about the rest.

**Backfilled 2026-09-04.** `docs/THE-GAMEPLAN.md` section 2.1 registers this file
at v0.1 and it did not exist until the fourth commit, so the first three entries
were written after their commits rather than at the time. Each says so.

**From the next change onward an entry rides in the same commit as the work it
describes, and cites no hash**, because it cannot know its own. That is the
convention `ZMeta/zmeta-spec/CHANGELOG.md` follows, where a hash appears only
when an entry refers to some other commit. It also terminates a regress the first
four entries walked into: an entry added after the fact needs a commit, which
needs an entry, which needs a commit.

## [Unreleased]

Nothing is released. PSE has no version, no tag, and no published artifact, and
`CONFORMANCE.md` states the bar that would have to be met first.

- **2026-09-08. The pre-commit hook gains its executable bit, after the first
  CI run on GitHub found it unset.**

  `.githooks/pre-commit` had mode 100644 in every commit since Wave 0, and the
  bundle of the pre-rewrite history confirms the rewrite did not change it.
  Every verification that reported the hook executable, including the
  fresh-clone check of 2026-09-05, ran in Git Bash on Windows, where `test -x`
  reports true for any file with a shebang line. The defect stayed invisible
  until the publication commit reached GitHub and the CI step "Pre-commit hook
  is executable and runs" failed on Linux. This commit sets the mode to 100755,
  adds this entry, appends a postscript to the worklog entry for the
  publication commit, and rewrites the handoff to the state after the push; no
  other file changes.

  Validation: the local battery is unchanged, because a file mode does not
  affect a Windows checkout. The check that matters is the CI step on this
  commit, which runs after the push and cannot be recorded here.

  **What did not change.** No tooling content; the hook changes in mode only. No
  doctrine, no criterion, no stamp, no schema, no policy, no connector, no
  validator logic.

- **2026-09-07. The history is rewritten before the first push, and the
  public-facing files land.**

  The operator created a public repository at `github.com/JTC-byte/PLAINSIGHT`.
  Three things in the history were not publishable: the two earliest commits
  carried the example persona's real name and handles, which the entry below
  had replaced only at the tip; every commit carried the operator's personal
  email address as author and committer; and four documents carried absolute
  paths from the operator's machine. The whole history was rewritten with
  `git filter-repo` on a fresh clone before anything was pushed. The persona
  values were replaced in every historical blob by the map the entry below
  used, the address became the GitHub no-reply address for the account, and the
  paths became `<Z-ISR>` and `<wave-0-scratchpad>`. Nine commits in, nine out;
  the rewritten tip differs from the pre-rewrite tip in four files, path lines
  only; no rewritten commit contains the old values, the old address, or a
  machine path.

  Every hash changed. Current-state files cite the new hashes as of this
  commit: `AGENTS.md`, `CONFORMANCE.md`, `README.md`, `tools/validate_hygiene.py`,
  six doctrine files in their status lines, and the handoff. The worklog, its
  archive, and every entry below this one keep the hashes they were written
  with, and this table translates them.

  | Before | After |
  |---|---|
  | `5d53973` | `1abb354` |
  | `a54061b` | `4c5cd25` |
  | `d99f213` | `f4e00e1` |
  | `8a856b3` | `98f3433` |
  | `533da17` | `d803213` |
  | `377d7d4` | `89c68a3` |
  | `7c14888` | `f907a7a` |
  | `2d406db` | `7c0e278` |
  | `b6d0bb2` | `595cc06` |

  `LICENSE` carries the Apache License 2.0 text as GitHub generated it in the
  remote's initial commit. `NOTICE` names the copyright holder and the ZMeta
  derivation with no compatibility claim. `.gitattributes` normalizes line
  endings to LF. `.gitignore` gains editor, OS and agent residue. The CI
  workflow declares a read-only token. `AGENTS.md` section 4 gains one
  sentence: the repository's own coordinates, its remote, its account and the
  upstream projects it cites, are not handles under the rule against writing a
  handle into a tracked file, and the D-001 scan is written not to refuse them.
  `README.md` states the license and the model by which the public repository
  is updated. The branch is `main`. The
  worklog moves its oldest entry to the archive without edit and gains this
  commit's entry, which records the rewrite in full.

  Validation: the five preflight validators, the hygiene self-test, the
  twelve-case telemetry suite, `git diff --cached --check`, the hook, and the
  kernel gate at 6 implemented, 0 failed, 1 stubbed, 5 pending, on the
  rewritten clone with this commit staged; a blob-level comparison of the two
  tips; a search of every rewritten commit for the removed values.

  **What did not change.** No doctrine criterion, no stamp, and no doctrine
  text beyond the hash tokens in six status lines; `doctrine/DOCTRINE_STATUS.md`
  changed in two hash tokens and nothing else. No schema, no policy, no
  connector, no validator logic. No voice edit is applied. Patches 2 through 4
  are still unapplied and patch 4 is still the operator's Class F decision. The
  D-001 repo scan is still a stub. Nothing collected, no connector executed, no
  platform touched.

- **2026-09-07. The example persona in the documents becomes fictional, and the
  records correct the patch state.**

  `docs/PLAINSIGHT-design.md`, `docs/PLAINSIGHT-FOUNDATION.md`,
  `docs/OSINT-COP-tool-review.md` and `docs/THE-GAMEPLAN.md` carried a worked
  example whose name and handles belonged to a real person, and one fixture
  string in `tools/tests/test_gate_log.py` reused the handle. On the operator's
  instruction of 2026-09-05 every value is replaced with a fictional one of the
  same length, fifty-five line pairs with no length difference, so the
  fixed-width mockups keep their alignment; six of the values are masked email
  hints that still carried the last letter of the old surname. A tree-wide search for every variant of the old
  values returns nothing. The values remain in `5d53973` and `d99f213`, which
  only a history rewrite removes.

  `.gitignore` gains `_voice-pass/`, where the 2026-09-05 voice pass writes its
  survivor files, so working material cannot enter a commit. The handoff
  corrects its statement that patches 2 through 4 still apply in order: since
  `377d7d4` one of patch 3's two `doctrine/HYGIENE.md` hunks anchors on a
  sentence that commit rewrote, and the other twelve hunks and patch 4 apply
  without it.
  The worklog moves its oldest entry to the archive without edit and gains this
  commit's entry, which records the voice pass harvest.

  Validation: the five preflight validators, the twelve-case telemetry suite,
  both forms of `git diff --check`, the hook, and the kernel gate at 6
  implemented, 0 failed, 1 stubbed, 5 pending, on the working tree and on the
  staged tree.

  **What did not change.** No doctrine file. No criterion, no stamp,
  `doctrine/DOCTRINE_STATUS.md` untouched. No schema, no policy, no connector,
  no validator logic. No voice edit is applied. Patches 2 through 4 are still
  unapplied and patch 4 is still the operator's Class F decision. The D-001
  repo scan is still a stub. Nothing collected, no connector executed, no
  platform touched.

- **2026-09-04. The tense rule becomes a gate, and the worklog archive opens.**

  `377d7d4` stated in `AGENTS.md` section 8 that the handoff is written in the
  tense of the tree the commit will create, and said in place that no gate
  enforced it. `tools/validate_hygiene.py` now does, for the checkable half:
  `HYGIENE_HANDOFF_PRE_COMMIT_TENSE` refuses "untracked" and "uncommitted" in
  `docs/plainsight_handoff.md`, case-insensitively, and offers the two legal
  moves in its refusal. Re-measured against `533da17`, that reaches thirteen of
  the fourteen lines that were wrong; the fourteenth had neither word, and
  `AGENTS.md` now says so as the half of the rule that stays a sentence.

  `--self-test` plants each word in four handoff-shaped lines and asserts the
  refusal, then asserts a clean sample passes, so deleting the check fails the
  test and widening it fails the test, which is design gate 1. The
  `validate-hygiene` target and the CI Housekeeping step both run it, and the
  kernel gate's description of the hygiene entry names the tense among what it
  covers. The check was not in `377d7d4` because landing it before the handoff
  rewrite would have refused the file being repaired; that ordering reason is
  gone.

  The worklog was at its ten-entry cap, so `docs/plainsight_worklog_archive.md`
  opens with the Wave 0 entry moved into it without edit, and the worklog gains
  this commit's entry. `AGENTS.md` section 5 names the tense among what the
  gates cover, and the handoff's section 0 answers the five questions for this
  commit. The archive's deferred row in `docs/THE-GAMEPLAN.md` section 2.2 is
  marked delivered, and the `Makefile` help line for `validate-hygiene` names
  the tense.

  Validation: the five preflight validators, the four self-test suites, the
  twelve-case telemetry suite, the hook, `git diff --check`, and the kernel gate
  at 6 implemented, 0 failed, 1 stubbed, 5 pending. The self-test was also run
  with the check's body removed and failed as designed.

  **What did not change.** No doctrine file. No criterion, no stamp,
  `doctrine/DOCTRINE_STATUS.md` untouched. No schema, no policy, no connector.
  The hook still does not run the telemetry test. Patches 2 through 4 are still
  unapplied and patch 4 is still the operator's Class F decision. The D-001 repo
  scan is still a stub. Nothing collected, no connector executed, no platform
  touched.

- **2026-09-04. The two process records are separated by tense, and the
  pre-commit tense is cleared from every file that carried it.**

  `docs/plainsight_handoff.md` described the tree as it stood before `d99f213`.
  Its state header read "the first build artifacts exist uncommitted", nine rows
  of its section 2 table marked artifacts written and untracked, and two more
  described already-committed files as carrying uncommitted edits. `d99f213`
  tracked the nine and committed the four edits, so a reader arriving at that
  table would have taken nine files git already held for work still to be
  committed.

  The cause is the closeout order rather than carelessness. Section 8 of
  `AGENTS.md` puts the battery first, then the records, then the commit, for a
  stated reason, and a handoff written in that order necessarily describes a
  tree the commit is about to change. Nothing is wrong with the order. What was
  missing is the instruction about tense, which section 8 now carries: the
  worklog describes the moment it was written, and the handoff describes the
  tree the commit will create. Two records written in one act at one moment
  differ by which tree each is true of, and each now says which. The rule also
  names the staging step that makes `git diff --cached --name-only` answer the
  question at the moment a maintainer is told to ask it, and it states in place
  that no gate enforces it, with the mechanism that would, its measured reach,
  and why that mechanism is a later change rather than this one.

  Section 8's opener claimed one local addition, and ZMeta's Handoff Standard is
  the five questions and nothing else, so the count was wrong before this change
  added to it. The opener now says what ZMeta contributes, which never needs
  recounting. Section 6's preamble gained a pointer, because it named both
  process records in one sentence, which is the conflation the new rule breaks.

  The same class of stale statement stood in four other places, and on the
  operator's instruction all four are corrected here. Patch 1 of the
  2026-09-03 review is applied whole: eighteen hunks across six doctrine
  files, each read and classed by effect before it landed. Fourteen are
  status-header, citation, or count corrections, and the five doctrine status
  headers no longer say NOT YET COMMITTED eight days after `5d53973` and
  `a54061b` landed them. Two reword a mechanism description without moving
  its obligation. One adds an enforcement-state paragraph to SS-14 item 6, the
  NEVER list, and that hunk was already stale when drafted: it named five
  preflight commands where the target ran seven, omitting the ontology
  validator and the telemetry test, and it is corrected in place. One hunk is named here
  rather than folded into the count. `doctrine/EGRESS.md`'s environment table
  changes what LOCAL reaches from "Nothing outside itself", which git, pip
  and CI already falsified, to "No third-party platform through a
  connector". No refusal moves, because EG-6 and the Execution Limits are
  what refuse and the row is descriptive, and it is named because a change to
  a rank-1 sentence about reach is the kind `CLAUDE.md` gate 2 says rarely
  looks like one. Patches 2 through 4 were re-verified to apply in order on
  top of the corrected tree.

  `README.md` no longer says nothing is built and nothing is committed, and
  its next action is the operator's four decisions and then Step 7 rather
  than a first commit that landed on 2026-08-27. `CONFORMANCE.md` counts six
  implemented and five pending as the aggregator does, and its rung 3 row
  says the ontology tool exists with its corpus mode deferred rather than
  that the tool does not exist. The `Makefile` and pre-commit comments each
  claimed the other ran the same battery; both now state that the hook runs
  six commands and preflight runs those six plus the telemetry test, which
  CI runs as a step of its own.

  A verification pass over the whole change before commit, seven lenses and
  six refuters, found the same tense in six more places, all corrected here:
  `AGENTS.md` section 5 said preflight and the hook run the same battery; the
  `Makefile` header named the ontology gate as pending;
  `.github/workflows/ci.yml` said two gates were the whole battery;
  `CONFORMANCE.md` section 2 said Step 7 was blocked on Steps 5 and 6 and
  described subdirectories a clone does not have; `doctrine/DOCTRINE_STATUS.md`
  marked `spec/layer-model.yaml` as to be written; and `docs/THE-GAMEPLAN.md`
  marked Step 7 BLOCKED, corrected there as the previous session corrected
  Step 6. The same pass corrected this entry's own arithmetic, its naming of
  the criterion patch 1 added a paragraph to, which is SS-14 item 6 and not
  SS-17, and the step the authorization schema belongs to, which is Step 8 and
  not Step 7, an error carried in from the review's `DECISIONS.md`.

  `docs/plainsight_worklog.md` gains the entry that `8a856b3` and `533da17`
  owed. `8a856b3` moved `AGENTS.md`, this file, `docs/THE-GAMEPLAN.md` and the
  handoff, and `533da17` corrected two honesty defects in this file. Neither got
  a worklog entry, which is the same section 8 obligation missed from the other
  side. `533da17` has no entry in this file either, and by the rule its own
  commit added it cannot be given one. The 2026-09-03 worklog entry is
  untouched, closing line included. It was true when it was written, and a
  process record is added to rather than restyled. The worklog now holds ten
  live entries against its ten-entry cap, so the next closeout archives the
  oldest before it adds one.

  Validation: the full battery at `533da17` and again after these edits. The
  five validators in the preflight battery are green. The three self-test suites
  are green, with 60 deliberate layer-model breaks all refused, 48 of them by
  the expected code alone, 16 ontology breaks refused, and 6 cast breaks
  refused. The twelve-case telemetry suite is green, and the kernel gate reports
  6 implemented, 0 failed, 1 stubbed, 5 pending.

  One measurement this commit records that no file in the tree carried before
  it: the four review patches in
  `Z-ISR/_session-artifacts/2026-09-03-plainsight-doctrine-review-2/` were
  applied in sequence onto a scratch clone, all four went in clean, and the
  patched tree returned the same kernel-gate line. One figure differs, which is
  the doctrine criterion count at 59 against 58 here, because patch 4 defines
  EG-7. Knowing that a patch applies is not a reason to apply it. Patch 1
  landed because the operator instructed it, and patch 4 remains the
  operator's decision.

  **What did not change.** No criterion's obligation, and no stamp.
  `doctrine/DOCTRINE_STATUS.md` changed in three lines of fact: which commits
  its rows landed in, how the unstamped items are counted, and that the D6
  file now exists. Its stamps are as they were on 2026-08-27. Rank 1 changed in wording only. Patches 2
  through 4 are still unapplied, and patch 4 is still the operator's Class F
  decision. The hook still does not run the telemetry test, because adding it
  is a mechanism change the operator has not made. The tense rule is a
  sentence and its check is owed. The D-001 repo scan in
  `tools/validate_retention.py` is still a stub. No schema, no policy, no
  connector. Nothing collected, no connector executed, no platform touched.

- **2026-09-04, `8a856b3`. The changelog this repository owed, and the handoff
  standard.** *(Written in the commit after, which is the last entry to do so.)*

  This file did not exist, and the register had listed it since Wave 0. It was
  missed because this repository named it in one row of its own documentation
  matrix, the Schema row, for an artifact that does not exist yet, while
  `ZMeta/zmeta-spec/AGENTS.md` names it first among the surfaces that move when
  any governed artifact changes. The matrix now states that inheritance on every
  row rather than in one.

  `AGENTS.md` gained section 8, a handoff standard carrying the five questions a
  completed change leaves answerable, and the rule that a closeout is one act:
  the battery, then the records, then the commit, in that order. One clause there
  is not inherited and is the reason the four doctrine patches from `d99f213` are
  still unapplied: a closeout commit carries no Class F change the operator has
  not decided, because a closeout that quietly includes a doctrine amendment has
  made the ratification a formality.

  `docs/plainsight_handoff.md` gained section 0, answering those five questions
  for `d99f213`.

  Validation: the hygiene gate refused this change three times before it passed,
  on em dash connectors copied from the parent repository's changelog, which its
  voice standard permits and this one forbids. That is the gate working on a file
  it had never seen.

  **What did not change.** No governed artifact. No doctrine criterion amended,
  nothing stamped, `doctrine/DOCTRINE_STATUS.md` as it was on 2026-08-27.

- **2026-09-04, `d99f213`. The owed review runs, Steps 4 through 6 land, and
  the repository gets its first test.** *(Written in `8a856b3`, the commit after.)*

  The 2026-08-27 entry below closed with an obligation: four of the five doctrine
  files and five of the criteria had no adversarial review. That review ran as
  five lenses paired with five verifiers instructed to refute, and a second
  review ran over the layer model this session produced. **92 doctrine findings:
  21 confirmed, 35 downgraded, 27 refuted, deduplicating to two blockers and six
  majors. 31 layer-model findings: three blockers, 29 repaired, two recorded as
  readings.** Both records, with every verdict and its quoted evidence, are in
  `Z-ISR/_session-artifacts/2026-09-03-plainsight-doctrine-review-2/`.

  Both doctrine blockers are one defect: SS-4's required-field table and SS-1's
  N0 promotion clause still carried the S0-to-S2 reading the operator overrode on
  2026-08-26, and SS-4's table is what the Step 7 authorization schema compiles
  from. **Neither is fixed in this commit.** They are drafted as patch 2 of four
  in the review directory, because doctrine is amended by ratified item and an
  agent may draft a Class F change and never decide one.

  New governed artifacts: `spec/layer-model.yaml` enumerates the nine event types
  D6 stamped, which no governed file had listed, and is the single source the
  Step 7 schema and policy generate from; `ontology/selectors.yaml` is D2 in one
  file at nineteen selectors, five of them marked PROPOSED because an addition to
  a closed vocabulary is the operator's to ratify; `synthetic/CAST.md` and
  `synthetic/GROUND_TRUTH.yaml` are the Step 4 cast, DRAFT and UNSEALED;
  `CONFORMANCE.md` states the not-ZMeta claim and marks three of the four
  licensing conditions absent rather than pending.

  New mechanisms: `tools/validate_layer_model.py` (33 checks, 60 self-test
  breaks), `tools/validate_ontology.py` (16 breaks), `tools/validate_cast.py`
  (6 breaks plus a placeholder scan that refuses a filled selector while the cast
  is unsealed), and `tools/tests/test_gate_log.py`, the first test in this
  repository, whose twelve cases exercise HY-1 and RT-19 against the recorder.
  Seven of the recorder's constraints were deliberately broken and all seven
  refused; three of those breaks were corrections rather than confirmations,
  because the rule that a telemetry record never carries the matched value rested
  on caller convention, the tuple both criteria credit as the mechanism dropped
  nothing, and the TTL swept only on write.

  Surfaces that moved: spec, ontology, synthetic, tools, the gate battery
  (`Makefile`, `.githooks/pre-commit`, `.github/workflows/ci.yml`,
  `tools/validate_conformance.py`), the register in `docs/THE-GAMEPLAN.md`,
  `AGENTS.md` section 5, `README.md`, and both process records.

  Validation: all six implemented kernel-gate checks green, all three self-test
  suites green, the twelve-case test suite green, the pre-commit hook green, and
  `git diff --check` clean. The kernel gate goes from two implemented checks to
  six, with one stub and five pending, and a stub is still not counted as a pass.

  **What did not change.** No doctrine criterion was amended. No conclusion or
  basis was stamped. `doctrine/DOCTRINE_STATUS.md` is untouched, so every
  mechanism that reads it sees what it saw on 2026-08-27. The D-001 repo scan is
  still a stub. Nothing collected, no connector executed, no platform was
  touched, and no account exists.

- **2026-08-27, `a54061b`. Rank 1 grows to four files, and the gates get a
  pattern of life.** *(Backfilled 2026-09-04 from the commit and the worklog.)*

  `doctrine/EGRESS.md` (EG-1 to EG-6) and `doctrine/CREDENTIAL_LIFECYCLE.md`
  (CR-1 to CR-8) joined rank 1, answering what may leave from two directions:
  which environment case material may exist in, and which identity a third party
  permanently records as having looked. `doctrine/HYGIENE.md` (HY-1 to HY-4) is
  advisory and owns adjudicating the gates themselves. SS-19, SS-20, SS-21 and
  RT-19 were added, with SS-20 the finding of that session: the accounts that
  authenticate are a separate population from the accounts collected on, and most
  audited connectors cannot run without the former.

  Surfaces that moved: five doctrine files, `doctrine/DOCTRINE_STATUS.md`,
  `tools/gate_log.py` as a new mechanism, both validators, `Makefile`,
  `.gitignore`, `AGENTS.md`, `CLAUDE.md`, the register, and both process records.

  **What did not change.** No schema, no policy, no ontology, no connector. The
  kernel gate stayed at two implemented checks.

- **2026-08-27, `5d53973`. The governed repository, the doctrine foundation,
  and the doctrine gates.** *(Backfilled 2026-09-04 from the commit and the worklog.)*

  The repository was cut with `CLAUDE.md` advisory and `AGENTS.md` normative,
  change classes A through F with F defined by effect rather than by path, and the
  Execution Limits that keep an agent off a live platform.
  `doctrine/SUBJECT_SELECTION.md` (SS-1 to SS-18) and `doctrine/RETENTION.md`
  (RT-1 to RT-18) landed with every conclusion recorded and every basis
  deliberately unstamped. `doctrine/DOCTRINE_STATUS.md` is the pin of record, and
  mechanisms read it rather than the document they enforce, so an unstamped
  criterion refuses rather than permits.

  Three gates were written before the first commit rather than after:
  `tools/validate_doctrine.py`, `tools/validate_hygiene.py`, and
  `tools/validate_conformance.py`, whose `--kernel-gate` reports an unimplemented
  check as PENDING and never as a pass.

  **What did not change.** Nothing existed before this commit.
