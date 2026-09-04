# Changelog

Advisory, Class A. One entry per commit that changed a governed artifact, newest
first, in the shape `ZMeta/zmeta-spec/CHANGELOG.md` uses: what changed, which
surfaces moved, what validation ran, and what did **not** change. The last of
those is the half a reader needs most, because an entry that only lists additions
leaves them guessing about the rest.

**Backfilled 2026-09-04.** `docs/THE-GAMEPLAN.md` section 2.1 registers this file
at v0.1 and it did not exist until the third commit, so the first two entries
were written from the commits and the worklog rather than at the time. They are
marked as such. Every later entry is written in the same change as its commit.

## [Unreleased]

Nothing is released. PSE has no version, no tag, and no published artifact, and
`CONFORMANCE.md` states the bar that would have to be met first.

- **2026-09-04, `d99f213`. The owed review runs, Steps 4 through 6 land, and
  the repository gets its first test.** *(Written with the commit.)*

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
