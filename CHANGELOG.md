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

- **2026-10-01, overnight. The RT-11 halt is pinned by value, and the repo scan
  reads UTF-16 and refuses binary bytes.**

  **What changed.** R-18 compares the halt block and the ledger's halt acts
  with `HALT_PIN` by value, where it matched substrings. The repo scan decodes
  a file by its UTF-16 or UTF-32 byte-order mark, refuses NUL-bearing bytes
  without one as `RETENTION_REPO_SCAN_SOURCE_UNREADABLE`, and names compressed
  and binary containers as not read. A clean combined `--policy
  --shred-roundtrip` run reports both modes. From the Step 8 review's
  completeness critic, decided under the operator's overnight grant of
  2026-09-30 23:28, and revertible.

  **Which surfaces moved.** `tools/validate_retention.py` and its self-test,
  the worklog and the handoff.

  **What validation ran.** The retention self-test, 58 breaks and two decode
  cases; every retention mode refusing exactly as before; all sixteen preflight
  commands; both forms of `git diff --check`. The kernel gate exited 0.

  **What did not change.** No policy value, doctrine file or stamp. Every change
  makes the gate stricter.

- **2026-10-01, overnight. SS-14 item 7 counts the cast only when it is sealed,
  hash-verified and carries a confuser pair.**

  **What changed.** The authorization gate reads `tools/validate_cast.py`'s own
  seal, hash and confuser checks before it counts `synthetic/CAST.md` as met on
  the live pin, and the constructed check `AUTH_CAST_SEAL_UNREAD` refuses if that
  condition is removed while the cast is unsealed. From the Step 8 review's
  completeness critic, decided under the operator's overnight grant of
  2026-09-30 23:28, and revertible.

  **Which surfaces moved.** `tools/validate_authorization.py`, the worklog and
  the handoff.

  **What validation ran.** The authorization self-test and `--fixtures`, both
  unchanged on the real tree and both refusing with the condition removed in a
  scratch copy; all sixteen preflight commands; both forms of `git diff
  --check`. The kernel gate exited 0.

  **What did not change.** No policy, corpus row, cast file, doctrine file or
  stamp. A fixture-supplied stamp state is read as before, pending GF-U1.

- **2026-10-01, overnight. The pin-of-record reader reads the stamp wording as
  a closed grammar and binds a criterion only inside a stated range.**

  **What changed.** The whole-artifact Item cell is exactly "<what>, whole
  artifact" or a doctrine range "<NS>-1 to <NS>-<n>, all criteria"; a substring
  test let a row saying "not the whole artifact", or a struck or withdrawn row,
  stamp the whole file. A struck or withdrawn row stamps nothing. A criterion
  binds only inside a stated range or a row that names it. The 19xx or 20xx
  year bound is restored, and PIN-R6 states its limit. From the Step 8 review's
  completeness critic, decided under the operator's overnight grant of
  2026-09-30 23:28, and revertible.

  **Which surfaces moved.** `tools/pin_of_record.py`, the retention self-test,
  `AGENTS.md` section 7, the worklog and the handoff.

  **What validation ran.** The reader's self-test, 31 cases; the retention
  self-test, 53 breaks; the real pin binding the same five files and 58
  criteria; all sixteen preflight commands on the staged tree; both forms of
  `git diff --check`. The kernel gate exited 0.

  **What did not change.** No doctrine file, stamp, policy, schema or corpus.
  Every change makes the reader stricter.

- **2026-10-01, overnight. The authorization gate checks the whole row contract
  and pins its preflight and section stamps; the repo scan tests every match.**

  **What changed.** Every corpus row's decision and input keys are checked
  (`AUTH_DECISION_KEYS_UNEXPECTED`, `AUTH_GIVEN_KEYS_UNEXPECTED`) and a claimed
  collected string refuses (`AUTH_PAYLOAD_STRING_CLAIMED`). SS-5's fixtures must
  name SS-5 and the field and carry a record. A-18's second pass reads a row with
  no stamp state against the live pin. The contract's stamping sections and the
  four preflight checks are pinned in the tool (`RATIFY_SECTIONS`,
  `AUTH_PREFLIGHT_LIST_DRIFT`). The repo scan tests every match on a line. From
  the Step 8 review and its completeness critic, decided under the operator's
  overnight grant of 2026-09-30 23:28, and revertible.

  **Which surfaces moved.** `tools/validate_authorization.py`,
  `tools/validate_retention.py`, their self-tests, the worklog and the handoff.

  **What validation ran.** The authorization self-test, 55 breaks; the
  retention self-test, 52; `--fixtures` refusing exactly as before; all sixteen
  preflight commands on the staged tree; both forms of `git diff --check`. The
  kernel gate exited 0.

  **What did not change.** No policy, schema, corpus row, doctrine file or stamp.
  Every change makes a gate stricter.

- **2026-10-01, overnight. The retention gate pins RT-1's rows, its criteria and
  three non-numeric rules, and watches its own unratified refusal fire.**

  **What changed.** Each RT-1 strata row is pinned by name
  (`RETENTION_POLICY_STRATA_ROW_DRIFT`); R-01 refuses a subject value in any
  stratum outside the shred boundary, strata 4 and T included; the extension
  and ceiling rules are pinned beside the durations; the criteria check runs
  over RT-1 to RT-19 pinned in the tool (`RETENTION_CRITERIA_LIST_DRIFT`); and
  two self-test cases observe the unratified refusals fire. The halt check
  added earlier the same night as R-10 is R-18, because R-10 was taken. Five
  findings of the Step 8 adversarial review, decided under the operator's
  overnight grant of 2026-09-30 23:28, and revertible.

  **Which surfaces moved.** `tools/validate_retention.py` and its self-test, the
  worklog and the handoff.

  **What validation ran.** The retention self-test, 51 breaks; both retention
  modes refusing exactly as before; all sixteen preflight commands on the staged
  tree; both forms of `git diff --check`. The kernel gate exited 0.

  **What did not change.** No policy value, duration, stratum, doctrine file or
  stamp. Every change makes the gate stricter.

- **2026-10-01, overnight. The authorization gate compares five things it used
  to read and leave alone.**

  **What changed.** The schema's record shape against SS-4's nine fields
  (`AUTH_SCHEMA_RECORD_SHAPE_DRIFT`); SS-14 item 6's paths, not only its counts
  (`AUTH_RATIFY_LIST_DRIFT`); the compiled criteria against the ones
  `doctrine/SUBJECT_SELECTION.md` defines (`AUTH_CRITERION_NOT_COMPILED`); a
  row's render against the sentence compiled for its own value (A-07); and every
  decided row's assertion against its stamp state, not only the item 6 rows
  (A-18). Five findings of the Step 8 adversarial review, decided under the
  operator's overnight grant of 2026-09-30 23:28, and revertible.

  **Which surfaces moved.** `tools/validate_authorization.py` and its self-test,
  the worklog and the handoff.

  **What validation ran.** The authorization self-test, 47 breaks, six of them
  new; `--fixtures` refusing exactly as before; all sixteen preflight commands
  on the staged tree; both forms of `git diff --check`. The kernel gate exited
  0.

  **What did not change.** No policy, schema, corpus row, doctrine file or
  stamp. Every change makes the gate stricter.

- **2026-10-01, overnight. The Step 8 artifacts say what their tools do.**

  **What changed.** Seventeen findings of the Step 8 adversarial review:
  statements in the shred fixture, the gate README and corpus descriptions, both
  compiled policies, the authorization schema and three validators that were
  false when the tools run, mostly written before the tools were finished. The
  policy's N0 and L0 definitions are restored to doctrine's wording. Decided
  under the operator's overnight grant of 2026-09-30 23:28, and revertible.

  **Which surfaces moved.** `conformance/gate/README.md`,
  `conformance/gate/decisions.jsonl` (three description strings),
  `conformance/retention/shred-roundtrip.yaml`, `policy/retention.yaml`,
  `policy/subject-authorization.yaml`, `schema/subject-authorization.schema.json`
  (two descriptions), docstrings and help text in
  `tools/validate_authorization.py`, `tools/validate_retention.py` and
  `tools/validate_cast.py`, the worklog and the handoff.

  **What validation ran.** Each edited gate re-run to confirm it refuses exactly
  what it refused before; the parsed N0 and L0 definitions compared with
  doctrine's; all sixteen preflight commands on the staged tree; both forms of
  `git diff --check`. The kernel gate exited 0.

  **What did not change.** No check, value, duration, stratum, row assertion,
  pending list, unratified entry or refusal. No doctrine file, and no generated
  artifact.

- **2026-10-01, overnight. The repo scan reads every file, and a malformed or
  unreadable input refuses rather than passing or crashing.**

  **What changed.** Both repo-scan modes read names NUL-separated and decode
  every file with replacement, so a non-ASCII path or a non-UTF-8 file is no
  longer skipped, and an unshowable staged file refuses. The retention policy
  check refuses when the layer model's strata cannot be read, where it used to
  fall back to empty sets and pass RT-2's own refusal. A malformed policy or
  fixture refuses as `RETENTION_INPUT_MALFORMED` and a non-UTF-8 authorization
  input as `AUTH_INPUT_UNPARSEABLE`, both with exit 2, where each ended in a
  traceback. Five findings of the Step 8 adversarial review, decided under the
  operator's overnight grant of 2026-09-30 23:28, and revertible.

  **Which surfaces moved.** `tools/validate_retention.py` and its self-test,
  `tools/validate_authorization.py`, the worklog and the handoff.

  **What validation ran.** The retention self-test, 43 breaks; a planted handle
  in a non-ASCII-named and a non-UTF-8 file in a scratch repository, found by
  both modes; a malformed policy and a non-UTF-8 pin, each exit 2; all sixteen
  preflight commands on the staged tree; both forms of `git diff --check`. The
  kernel gate exited 0.

  **What did not change.** No doctrine file, stamp, policy, schema, corpus, or
  scan shape. Every change makes a gate stricter.

- **2026-10-01, overnight. RT-11's halt override refuses as U-17, the halt is
  graded, and no mode is dropped from a combined call.**

  **What changed.** `policy/retention.yaml` compiled an RT-11 halt override as
  permitted against the pin of record's RT-11 row, which reads "No override".
  `halt.override` and the ledger's `halt_override` act now defer to U-17, a
  class F entry the operator decides, and `tools/validate_retention.py` grades
  the halt as R-10 with three new self-test breaks. `--policy
  --shred-roundtrip` runs both modes, where it used to drop `--policy`, and
  every other combination of modes in the retention and authorization tools
  refuses rather than dropping one. Decided under the operator's overnight grant
  of 2026-09-30 23:28, and revertible.

  **Which surfaces moved.** `policy/retention.yaml`, `tools/validate_retention.py`,
  `tools/validate_authorization.py`, the worklog and the handoff.

  **What validation ran.** The retention self-test, 39 breaks; every mode
  combination by hand; all sixteen preflight commands on the staged tree; both
  forms of `git diff --check`. The kernel gate exited 0.

  **What did not change.** No doctrine file, stamp, schema or corpus. The
  question U-17 records is not decided: every option needs a doctrine or pin
  amendment, which is the operator's.

- **2026-10-01, overnight. One reader of the pin of record for every gate, and
  a self-test for it and for the doctrine gate.**

  **What changed.** The Step 8 adversarial review found that the doctrine,
  authorization and retention gates read `doctrine/DOCTRINE_STATUS.md` three
  ways, and that one dated row naming a path stamped the whole file.
  `tools/pin_of_record.py` is the one reader they now import, taking the
  stricter reading on every axis. A whole-artifact stamp needs an Item cell
  saying "whole artifact" or "all criteria" and a File cell naming the path
  alone; the Conclusion stamped cell must be a calendar date and nothing else;
  the ratifier must be declared; a stamp for an absent file stamps nothing;
  the contract is stamped by its sections 5 and 12; criterion rows come from the
  per-criterion table alone. Refusals state why a path is unstamped and quote
  the row format. `tools/validate_doctrine.py` gains a self-test, and the
  reader's self-test and the doctrine self-test join the hook, preflight, the
  kernel gate and CI. Decided under the operator's overnight grant of
  2026-09-30 23:28, and revertible.

  **Which surfaces moved.** `tools/pin_of_record.py`, new;
  `tools/validate_authorization.py`, `tools/validate_retention.py` and its
  self-test, `tools/validate_doctrine.py`, `tools/validate_conformance.py`;
  `.githooks/pre-commit`, the Makefile, CI; `AGENTS.md` sections 5 and 7;
  `CONFORMANCE.md` section 4; the worklog and the handoff.

  **What validation ran.** The reader's self-test, 21 cases, with each of its
  eleven rules deleted in a scratch copy and the self-test failing every time;
  the doctrine self-test, ten planted defects; the retention self-test, 36
  breaks; all sixteen preflight commands on the staged tree; both forms of
  `git diff --check`. The kernel gate exited 0 with 16 implemented checks
  passing.

  **What did not change.** No doctrine file, stamp, policy, schema, corpus,
  fixture or generated artifact. No current outcome: the same artifacts refuse
  and the same doctrine files bind. Every change makes a gate stricter or
  leaves it as it was. The header heuristic that skips a row whose Item cell
  begins with "Item" is kept, because accepting such rows would widen what
  stamps, which is class F.

- **2026-10-01, overnight. Four validators record their runs the way HY-1
  says, and the first gate-telemetry review is recorded.**

  **What changed.** `tools/validate_layer_model.py` and `tools/validate_cast.py`
  wrote one refuse record per finding and no run record, so their refusal counts
  were per finding; both now write one run record and one detail record per
  finding. The authorization and cast self-tests record as
  `authorization-self-test` and `cast-self-test`, and
  `tools/validate_retention.py --repo-scan --staged` as
  `retention-repo-scan-staged`, so no gate name mixes a mode that refuses by
  design with one that passes. The review that found these, the first under
  HY-2, ran under the operator's overnight grant of 2026-09-30 23:28 and is
  recorded in the worklog per HY-4.

  **Which surfaces moved.** The four validators' telemetry calls, the worklog,
  and the handoff.

  **What validation ran.** Every changed recording path exercised and its
  records read; `tools/tests/test_gate_log.py`; all fourteen preflight commands
  on the staged tree; both forms of `git diff --check`. The kernel gate exited
  0.

  **What did not change.** No check, refusal, exit code, threshold, gate entry,
  doctrine file, policy, schema or corpus. Records already in the log are left
  as written.

- **2026-09-30, overnight. The two values the repo scan refused are replaced
  with placeholders, and the kernel gate exits 0.**

  **What changed.** `tools/validate_retention.py --repo-scan` refused two
  filled handle selectors that predate Step 8, which held the kernel gate and CI
  red on every push since `0e0c840`. The worked example in
  `docs/PLAINSIGHT-FOUNDATION.md` now reads in the registry's form,
  `handle:<platform>/<string>`, and the `value_in_a_form` fixture in
  `tools/validate_ontology.py` keeps its platform segment a placeholder, so the
  line carries no complete typed handle while the check it exercises still
  fires. This is the first of the three moves the scan's refusal names. It was
  taken under the operator's overnight grant of 2026-09-30 23:28, relayed by the
  parent-folder session, and is revertible. `README.md` also translates the old
  `../ZISR COP/` path that two dated doctrine citations keep.

  **Which surfaces moved.** `docs/PLAINSIGHT-FOUNDATION.md` line 87,
  `tools/validate_ontology.py`, `README.md`, `AGENTS.md` section 5,
  `CONFORMANCE.md` section 4, the worklog, its archive, and the handoff.

  **What validation ran.** All fourteen preflight commands on the staged tree,
  with the ontology self-test refusing the edited break by `ONT_VALUE_IN_FILE`
  alone, and both forms of `git diff --check`. The kernel gate exited 0 with 14
  implemented checks passing, 3 unratified and refusing, 2 stubbed and 5
  pending.

  **What did not change.** No doctrine file, stamp, schema, policy file,
  generated artifact, corpus, or registry entry. `ontology/selectors.yaml` is
  untouched and no `repo_scan.document_exemptions` row was added, so the scan's
  reach is what it was. Both values remain in git history, which RT-15's fourth
  part names and no commit-time check reaches.

- **2026-09-28. Every validator self-test runs on the hook, preflight, the
  kernel gate and CI; CI stops skipping the steps after a red one; and the two
  ontology stubs nothing called are declared as STUB.**

  **What changed.** Five of the six validator self-tests, layer-model,
  ontology, cast, authorization and retention, ran on no automated path, and
  hygiene's ran only inside one CI step. All six now run in
  `.githooks/pre-commit`, in `make preflight`, as IMPLEMENTED entries in
  `KERNEL_GATE`, and in CI, where the five gain a named step each, placed before
  the kernel gate so a broken self-test turns its own step red. Every CI gate
  step now carries `if: ${{ !cancelled() }}`: the kernel gate was red on the
  runs for `4e6abda`, `38c93cc`, `132eef0` and `4a5c788`, and on all four the
  hook step and the co-authorship trailer check were skipped. `KERNEL_GATE` also
  gains STUB entries for `tools/validate_ontology.py --matchers` and `--corpus`,
  which print DEFERRED and exit 0, and grows from sixteen entries to
  twenty-four. The authorization note and the docstring of
  `tools/validate_authorization.py` said six of the nine SS-14 item 6 paths
  carry no dated row where the tool prints seven, and now say seven.

  **A cast self-test defect the wiring would have turned into a refusal.** The
  plainsight session's review found that two of the cast self-test's mutations
  assumed the file is unsealed: setting `sealed` true changes nothing on a
  sealed file, and the placeholder scan skips one. Sealing the cast, which is
  the operator's next ratifying act, would therefore have made the self-test
  exit 1 and the new hook refuse the sealing commit. Each mutation now
  constructs its own seal state, and the self-test runs every mutation against
  a sealed copy as well, so a mutation that leans on the file's current state
  fails at once.

  **Which surfaces moved.** `.github/workflows/ci.yml`, `.githooks/pre-commit`,
  the Makefile's preflight target and its comment,
  `tools/validate_conformance.py`, the cast self-test in
  `tools/validate_cast.py`, one docstring line in
  `tools/validate_authorization.py`, `AGENTS.md` section 5, `CONFORMANCE.md`
  section 4, the worklog, its archive, and the handoff.

  **What validation ran.** Before any edit, all six self-tests exited 0. After
  the edit, two deliberate breaks were applied to the tree and to an export of
  `4a5c788`: the 2026-09-08 `dead_code` regression in the layer-model
  self-test, and the shred round-trip's no-canary check made unreachable. On
  `4a5c788` the hook and preflight stayed green over both. On this tree the
  hook, preflight, the kernel gate's entry line and a named CI step each went
  red, and every file was restored byte for byte. A really sealed copy of the
  cast makes the `4a5c788` cast self-test exit 1 and the fixed one exit 0, and
  reverting the fix fails the sealed-copy pass on today's unsealed file. A
  scratch copy with dated rows for the seven unstamped SS-14 item 6 paths and
  the two contract stamp-target rows resolved turns the authorization self-test
  red, because row 8 of `conformance/gate/decisions.jsonl` asserts the item 6
  refusal from the real pin; the commit that completes item 6 edits that row
  too. The other five stayed green. CI was replayed locally rather than run on
  GitHub, and the worklog entry states what that replay does not cover. The
  plainsight session reviewed the change, asked for three fixes, and
  re-reviewed the fixed tree with the verdict commit; the worklog entry records
  both reviews and what was applied after the second.

  **What did not change.** No doctrine file, stamp, allowlist, NEVER list,
  authorization file, schema, policy file, generated artifact, corpus or
  fixture. No validator's checks: the edits to validators are the cast
  self-test's two mutations and its second pass, and one docstring count. The
  kernel gate stays red on `retention-repo-scan`, for the disclosed reason, and
  exits 1 exactly as before. `--corpus` stays owed.

- **2026-09-11. Step 8's eight artifacts are drafted, UNRATIFIED, and refuse
  until stamped; the kernel gate grows to sixteen entries and turns red on a
  live retention scan; a decision register and a patch reconciliation record
  what this session found and did not settle.**

  Two commits landed before this closeout act, `38c93cc` and `ff016af`, each
  recorded below under its own hash because this session committed them before
  reaching the point in `AGENTS.md` section 8's order, the battery, then the
  records, then the commit, where this entry and the two below it are written.
  This commit carries the third act: Step 8, and the records for all three.

  **Step 8.** Eight artifacts, 9,342 lines, all drafted by subagents in this
  session and all UNRATIFIED, refusing until `doctrine/DOCTRINE_STATUS.md`
  carries a dated row for each: `policy/subject-authorization.yaml` (1,403
  lines), `policy/retention.yaml` (1,617), `schema/subject-authorization.schema.json`
  (393), `conformance/gate/decisions.jsonl` (21), `conformance/gate/README.md`
  (548), `conformance/retention/shred-roundtrip.yaml` (542),
  `tools/validate_authorization.py` (2,713), and `tools/validate_retention.py`
  (2,105). Both policy files are hand-authored; `tools/generate_pse.py` owns
  exactly five outputs and neither is among them, and each carries a header
  saying so. `tools/validate_retention.py` replaces the D-001 stub.

  **The kernel gate.** Sixteen entries. Eight are IMPLEMENTED:
  doctrine, hygiene, layer-model, cast, telemetry, retention-repo-scan, schema,
  and ontology. Three are UNRATIFIED: authorization, retention-policy, and
  retention-shred-roundtrip. Five are PENDING: authorization-dispatch-paths,
  authorization-disjointness, retention-finding, divergence-register, and
  connector-conformance. `retention-repo-scan` moves out of STUB; it enforces
  three of RT-15's four parts. The fourth part is the code RT-15 names,
  `FIXTURE_CONTAINS_LIVE_SELECTOR`, which is not in the wire vocabulary, and
  git history, which is out of reach of any commit-time check.

  The kernel gate is red on one check. `tools/validate_retention.py
  --repo-scan` refuses on two filled handle selectors that predate Step 8:
  line 87 of `docs/PLAINSIGHT-FOUNDATION.md`, introduced in `1abb354`, a
  worked example in a rank-7 record of intent, and line 894 of
  `tools/validate_ontology.py`, introduced in `f4e00e1`, a designed value in
  that validator's own negative fixture. Neither value is reproduced here,
  because AGENTS.md section 4 refuses a selector value in a tracked file and
  the scan reads this file too. Both are true on shape and false in
  substance. `docs/PLAINSIGHT-design.md` and `docs/THE-GAMEPLAN.md` already
  carry `repo_scan.document_exemptions` rows of exactly this kind;
  `docs/PLAINSIGHT-FOUNDATION.md` does not. Adding those rows was proposed and
  refuted in this session: the proposal used a rank-1 citation above its lane,
  and narrowing an RT-15 scan is a reach decision. It is the operator's, and it
  is open. The pre-commit hook is unaffected, because it runs the same mode
  over the index rather than the working tree, and neither file this commit
  stages carries a selector.

  **CI fails on this commit when it is pushed.** Line 57 of
  `.github/workflows/ci.yml` runs `python tools/validate_conformance.py
  --kernel-gate`, which exits 1 while the scan refuses. The workflow goes red on
  the push and stays red until the operator decides the exemption. That is the
  gate reporting a true finding rather than a regression, and the alternative,
  leaving the scan a stub or pointing it at an empty index, would convert a true
  positive into a silent one.

  **Step 8 is not done.** `docs/THE-GAMEPLAN.md`'s done-when for Step 8 asks
  that `tools/validate_authorization.py --fixtures` and
  `tools/validate_retention.py --policy --shred-roundtrip` both be green,
  including the check that an unratified criterion refuses rather than
  permits. All three modes exit 1. Step 8 does not meet its own done-when.
  Every refusal is the designed one: `doctrine/DOCTRINE_STATUS.md` carries no
  dated row for any of the eight artifacts, so a criterion absent from the
  stamp table refuses, a missing artifact refuses, and a fully stamped state
  permits, the last two exercised by `--self-test`.

  **No review has run.** Step 8's artifacts have had no adversarial review.
  Compiling the decision register and finding the three defects below is
  drafting work, not a review of the artifacts against each other or against
  doctrine.

  **The decision register.** Sixty-six unratified placeholders in the
  artifacts were compiled and collapse to 51 distinct decisions, 15 entries
  being second or third copies. Twenty-two of the 51 are grounded in the
  stack's own documentation. Twenty-nine are the operator's, and 25 of those
  arrive with at least one option foreclosed. Eight lenses claimed 45 entries
  grounded and refuters overturned 15 of them, a 33 per cent over-report; every
  overturn ran one direction, a real rank-1 quote settling a neighbouring
  question, or two options eliminated and the survivor declared grounded. Four
  Fable refuters failed on exhausted usage credits and were re-run on Opus;
  before the re-run the same groups reported 31 grounded, and after it, 17. The
  register is at
  `Z-ISR/_session-artifacts/2026-09-11-plainsight-step8/DECISION_REGISTER.md`.

  **Defects found, not fixed.** Lines 137 to 139 of
  `tools/validate_conformance.py` say "six of the nine paths" where the tool
  prints seven refusals. The `evidence_ref` field in
  `schema/subject-authorization.schema.json` admits only the three pre-R4
  evidence kinds, which is what criteria SA-U2 and SA-U11 both land on.
  SA-U16's current `decided_at_step` placement is not wire-legal: line 607 of
  `spec/layer-model.yaml` requires that field on every REFUSED.

  **Patch 4b.** `patch-4b-obligation-drafts-CLASS-F.post-patch-3.patch` no
  longer applies; `git apply --check` exits 1 on `doctrine/DOCTRINE_STATUS.md`.
  The cause is a fifteen-minute race: the patch was regenerated at 2026-09-08
  18:40:19 and `4e6abda` was committed at 18:55:58, adding three rows to the
  table the patch anchors on. `git apply --3way` applies
  `CREDENTIAL_LIFECYCLE.md` and `EGRESS.md` cleanly and `DOCTRINE_STATUS.md`
  with conflicts; union-resolving that one table conflict yields 59 criteria.
  Line 192 of the handoff this commit replaces asserted the patch applies,
  which was false; the handoff no longer says it.

  **The push.** This session pushed `4e6abda` on the operator's instruction,
  `6247953..4e6abda`, then committed and pushed `38c93cc`; `origin/main` is at
  `38c93cc`. `ff016af` is one commit ahead of `origin/main`, and the operator
  has not instructed its push.

  Validation: doctrine at 58 criteria, hygiene and its self-test, layer-model
  and its self-test, ontology and its self-test, cast and its self-test, the
  validator's own self-test, `validate.py --kernel` at 44 must-pass events
  clean and 98 must-fail fixtures refused, `generate_pse.py --check`,
  `build_corpus.py --check`, the gate-log tests, both forms of `git diff
  --check`, and the pre-commit hook are all green. `tools/validate_conformance.py
  --kernel-gate` is red, on `retention-repo-scan` alone, for the reason above.
  The battery is not green end to end, and this entry does not describe it as
  such.

  **What did not change.** No doctrine file was edited and no criterion,
  conclusion, or stamp moved; `doctrine/DOCTRINE_STATUS.md` carries no new
  dated row. `runner/subject_guard.py` and `runner/dispatch_allowlist.yaml`,
  Step 10, are not built. The encrypted blob store, the sweep, and
  `verify_shred.py`, Step 11, are not built. No connector, no runner dispatch,
  no store. Nothing collected, no platform touched.

- **2026-09-11, `ff016af`. The moved sibling is repointed, the operator's
  local record is ignored, and CI's actions are pinned past Node 20's
  retirement.** *(Written in the closeout commit after, because this session
  committed the fix before the closeout act that records it.)*

  On 2026-09-10, between the previous closeout and this one, four producer
  repositories were consolidated into `../zisr-producers/`, so
  `../zisr-recon/` ceased to exist. PLAINSIGHT was not in scope of that move
  and did not move itself. Nineteen citations across eight files in this
  repository still named the old path; this commit repoints three of them,
  `README.md` and two pointers in `AGENTS.md`, to `../zisr-producers/recon/`,
  because those files describe the current tree in the present tense. The
  dated measurements in `doctrine/`, `docs/`, and the worklog archive keep the
  old path, because a record that states what was true when it was written is
  falsified by editing it after the fact. `tools/validate_hygiene.py` cannot
  see this class of breakage: its citation check, `PATH_REF_RE`, is anchored
  to in-repo prefixes and skips a sibling path by design, so a sibling
  citation that moves is structurally invisible to the battery, and that
  missing mechanism is not closed by this commit.

  `AGENTS.md` said the pre-commit hook runs six commands. It runs seven, which
  the Makefile's own comment above the preflight target already stated; this
  commit corrects the count.

  `LOCAL_*.md` is now in `.gitignore`. The account and provisioning checklist
  the operator keeps in that file carries mailbox addresses, account names,
  and hardware identifiers, which are operator identity rather than case
  material, and no existing rule covered them.

  CI's `actions/checkout` and `actions/setup-python` were pinned at `v4` and
  `v5`, both of which run on Node 20. GitHub removes Node 20 from its runners
  on 2026-09-16, after which those pins would stop the workflow rather than
  warn it. They are now the Node 24 majors, `v5` and `v6`.

  **What did not change.** No doctrine file, no criterion, no stamp. No
  schema, no policy file, no connector. Class A, B, and C by the commit's own
  accounting: nothing here alters who may be a subject, what may be collected,
  how long anything is held, or what may leave the machine.

- **2026-09-11, `38c93cc`. Every `fires_when` value in the layer model is
  quoted, and a code entry that carries none is refused.** *(Written in the
  closeout commit after, because this session committed the fix before the
  closeout act that records it.)*

  Seventeen of the fifty-seven `violation_codes.codes` entries in
  `spec/layer-model.yaml` were unquoted YAML flow mappings whose `fires_when`
  sentence contained a comma. YAML ends the value at that comma and turns the
  remainder into null-valued keys; the file still parsed, so no check saw the
  defect, and the generated `policy/violation-codes.yaml` documented those
  seventeen codes with half a sentence, the dropped half carrying the
  gate-fixture references Step 8 reads. This commit quotes all fifty-seven
  values, the seventeen truncated ones for meaning and the other forty so the
  file has one form rather than two, and regenerates
  `policy/violation-codes.yaml` from the corrected model; the diff measured
  25/17 in the policy file, 57/57 in the model, and 55/1 in
  `tools/validate_layer_model.py`, which gains check L-34, `CODE_ENTRY_KEYS`,
  refusing a code entry that carries a key outside the declared five or
  carries no `fires_when`.

  Two prior sessions recorded this fix as green while
  `tools/validate_layer_model.py --self-test` was exiting 1. The `dead_code`
  self-test fixture appended a code entry with no `fires_when`, which made
  L-34 fire alongside `LM_CODE_UNREFERENCED` and broke that row's
  `expect_only`. This commit gives the fixture a `fires_when` value; the
  self-test now reports 62 deliberate breaks, 62 refused, 50 by the expected
  code alone, 12 cascading, and 44 distinct codes exercised. No gate in the
  repository had run that self-test to catch the regression:
  `tools/validate_conformance.py` invokes the validator with `--quiet`, the
  pre-commit hook runs seven plain commands, `make preflight` runs eight, and
  `.github/workflows/ci.yml` runs one self-test, hygiene's. Only `make
  validate-layer-model` runs this one, and that is the hole that let two
  sessions call the fix green.

  Validation: `tools/generate_pse.py --check` and `tools/build_corpus.py
  --check` both confirm the schema, the other three policy files, and both
  conformance corpora are byte-identical, so the fix reaches only the files it
  targets.

  **What did not change.** No doctrine file, no criterion, no stamp. No
  schema, no connector. Class B and C by the commit's own accounting: no
  change to who may be a subject, what may be retained, or what may leave.

- **2026-09-08. Step 7 lands: the schema, the policy pack, the corpora and the
  contract, all generated from the layer model; the review's patches 2 and 3
  land in doctrine; the kernel gate grows to seven.**

  The operator decided three things on 2026-09-08 and this commit carries all
  three: the voice pass is parked, the 2026-09-03 review's patches 2, 3c and
  3b land, and Step 7 is built. It also carries what the repository going public
  the same day changed.

  **Doctrine.** Patches 2, 3c and 3b from
  `Z-ISR/_session-artifacts/2026-09-03-plainsight-doctrine-review-2/` land in
  five doctrine files, on the operator's instruction of 2026-09-08. Patch 2
  changes the domain `doctrine/SUBJECT_SELECTION.md` SS-4's required-field table
  gives `subject_class` from three classes to the seven R4 decided as maximum
  reach on 2026-08-26, and repairs SS-1's N0 paragraph the same way; that is a
  reach change in the table's text, Class F by effect, decided by the operator
  as R4 and instructed for landing here, and the commit is authored by the
  operator per R6 as amended. Patch 3c is patch 3 with its one pre-rewrite hash
  translated, twelve of thirteen hunks, ten confirmed minors including the
  `guard.py` precedent its own repository fixed; the thirteenth hunk was stale in
  intent and is dropped. Patch 3b is the sound HYGIENE.md hunk alone. Patch 4,
  the four Class F criteria, is regenerated against this tree as `patch-4b` in
  the review directory and is not applied; it waits on the operator.
  `doctrine/DOCTRINE_STATUS.md` gains two pending rows for the contract's
  sections 5 and 12 and one readings row for S7-R1 to S7-R7. No criterion's
  conclusion changed and nothing is stamped.

  **Step 7.** `tools/generate_pse.py` reads `spec/layer-model.yaml` and
  `ontology/selectors.yaml` and writes `schema/pse-event-0.1.schema.json`,
  `policy/semantics.yaml`, `policy/lineage.yaml`, `policy/producer-authority.yaml`
  and `policy/violation-codes.yaml`; `--check` regenerates them in memory and
  refuses drift. `tools/build_corpus.py` writes `conformance/must-pass.jsonl`,
  one synthetic case covering every subtype in one lineage chain, and
  `conformance/must-fail.jsonl`, one break per fixture, and refuses drift the same
  way. `tools/validate.py` is rung 2 of the conformance ladder: schema failures
  named through a code map, producer authority before any semantic check, the
  recursive denylist, the payload rules, lineage at subtype granularity, the
  cross-event citation and circularity rules, `expect_only`, no short-circuit,
  and a self-test that breaks the runner and asserts each break is caught.
  `spec/pse-semantics-contract.md` is written last, UNRATIFIED, thirteen
  sections with an enforcement label on every rule; its sections 5 and 12 are
  stamp targets. Seven readings the generator took where the model is silent are
  recorded as S7-R1 to S7-R7 in the contract, the schema and the semantics policy.
  The `schema` entry in `KERNEL_GATE` turns implemented, the pre-commit hook and
  `make preflight` gain the check, and `CONFORMANCE.md`, `docs/THE-GAMEPLAN.md`
  and the Makefile describe the new state.

  **The public repository.** Branch protection on `main` refuses force-pushes
  and deletions, requires linear history, includes admins, and sets no required
  status check; secret scanning and push protection are on; non-provider pattern
  scanning would not enable on this plan. The CI run on `6247953` passed every
  step, which the previous entry could not record. The handoff's claim that the
  2026-09-07 hash rewrite left the patch measurement intact is corrected: it
  moved one patch-3 anchor, which patch 3c fixes.

  Validation: the five validators with their self-tests, the twelve-case
  telemetry suite, `tools/validate.py --kernel` at 44 must-pass events clean and
  98 must-fail fixtures refused for the expected code with five self-test breaks
  caught, `git diff --cached --check`, the hook, and the kernel gate at 7
  implemented, 0 failed, 1 stubbed, 4 pending.

  **What did not change.** No criterion conclusion, no stamp, no basis. Patch 4
  is not applied and EG-7 does not exist in the tree. The layer model and the
  selector registry are unchanged in content. No voice edit is applied and the
  voice pass is parked by the operator's decision. The D-001 repo scan is still a
  stub. No connector, no runner, no store, no gate corpus. Nothing collected, no
  platform touched. The worklog moves its oldest entry to the archive without
  edit and gains this commit's entry.

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
