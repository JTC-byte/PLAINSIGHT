# PLAINSIGHT handoff: current state

Current state only. Rewritten every wave. History lives in
`plainsight_worklog.md` and is never restyled.

Capped at roughly 400 lines. Superseded sections move to the archive on the next
session rather than accumulating here. ZMeta's handoff reached 2,080 lines
carrying eleven superseded state sections, which is the failure mode this cap
exists to prevent.

**Wave:** 0. Doctrine foundation complete and committed. Nothing built.
**Date:** 2026-08-27
**Doctrine items:** 74 total across four rank-1 files plus advisory HYGIENE.md. **All carry a recorded
conclusion. 0 have a stamped basis.** Wave 0 landed in `5d53973`; the hardening
pass after it is uncommitted.

**Resume here. The doctrine is done. The next thing is a build.**

Two steps are unblocked and independent, so order is a preference:

- **Step 4**, the synthetic cast, reshaped 2026-08-27 to two personas on two
  platforms across **two email domains**. But provision the **collection pool
  first**: SS-20 established that the accounts which authenticate are a separate
  population from the accounts collected on, and most connectors cannot run at
  all without the former. Numbers are capped by platform acceptance rather than
  budget, so spend them there first.
- **Step 5**, `spec/layer-model.yaml`. Nine event types per D6, labelled
  `pse-event-0.1` per D7. The single source the schema enums and
  `policy/semantics.yaml` are both generated from.

---

## 1. Where the project is

The repository is governed and committed. Nothing is built, no connector exists,
and nothing has touched a platform.

**Every doctrine conclusion is recorded and every basis is unstamped.** That
split is deliberate and it is what a reader needs to know before relying on a
row: the conclusions were decided in session, and the reasoning in
`docs/PLAINSIGHT-FOUNDATION.md` §3 and `docs/THE-GAMEPLAN.md` §3.0 has not been
reviewed. Conclusions bind. Bases are unread.

Rank 1 holds four files as of 2026-08-27, one per question doctrine owns:
`SUBJECT_SELECTION.md` for who may be a subject, `RETENTION.md` for what may be
retained, and `EGRESS.md` with `CREDENTIAL_LIFECYCLE.md` for what may leave.

Three doctrine gates exist and run: `validate_doctrine.py`,
`validate_hygiene.py`, and `validate_conformance.py --kernel-gate`. Six of the
nine kernel-gate checks report PENDING because the artifacts they would check do
not exist, and one reports STUB. A stubbed or pending check is never counted as
a pass.

## 2. What exists

| Path | State |
|---|---|
| `CLAUDE.md` | Written. Advisory. R6 amended 2026-08-27. |
| `AGENTS.md` | Written. Normative. Rank 1 extended, section 3 reconciled with R6. |
| `doctrine/DOCTRINE_STATUS.md` | The pin of record. All conclusions recorded, 0 bases stamped. |
| `doctrine/SUBJECT_SELECTION.md` | SS-1 to SS-21. Reviewed by 14 agents through SS-18; SS-19 to SS-21 unreviewed. |
| `doctrine/RETENTION.md` | RT-1 to RT-19. Same review through RT-18; RT-19 unreviewed. |
| `doctrine/EGRESS.md` | EG-1 to EG-6. **New 2026-08-27.** Unreviewed. |
| `doctrine/CREDENTIAL_LIFECYCLE.md` | CR-1 to CR-8. **New 2026-08-27.** Unreviewed. |
| `doctrine/RETENTION_LEDGER.md` | **Missing.** Required at v0.1. Shape in RT-10. |
| `doctrine/DISCLOSURE.md` | **Missing, owed.** Trigger fired when RT-18 created a second egress path. |
| `doctrine/HYGIENE.md` | HY-1 to HY-4. **New 2026-08-27.** Gate adjudication. Unreviewed. |
| `spec/`, `schema/`, `ontology/`, `policy/` | Empty. Steps 5 through 7. |
| `conformance/` | Empty tree. Step 9. |
| `tools/validate_doctrine.py` | **Written.** Knows all four namespaces. Tested by breaking the corpus. |
| `tools/validate_hygiene.py` | **Written.** Prints the rules it cannot reach on every green run. |
| `tools/validate_conformance.py` | **Written.** `KERNEL_GATE` is the one authoritative list. |
| `tools/validate_retention.py` | Stub. Exits 0, checks nothing. D-001. |
| `tools/gate_log.py` | **Written.** Telemetry, 90d TTL, never records the matched value. |
| `Makefile`, `.github/workflows/ci.yml`, `.githooks/pre-commit` | **Written.** CI proves the hook runs and refuses agent trailers. |
| `connectors/`, `runner/`, `app/`, `synthetic/` | Empty. Later steps. |

## 3. What blocks

**Nothing blocks a build.** D6 was the last decision standing in the way of
`spec/layer-model.yaml`.

Two constraints on ordering rather than blocks:

- **EG-2 and RT-4 both have no later date.** The case store lives in the
  isolated environment and every blob is encrypted with a per-case key from the
  first write. Neither can be retrofitted, so the isolated environment has to
  exist before the first blob does.
- **Live execution stays an operator act.** `AGENTS.md` §4's first Execution
  Limit is unchanged by operator decision on 2026-08-27. An agent builds and
  analyzes; the operator runs anything that reaches a platform. Account creation
  is impossible for an agent regardless of doctrine.

## 4. Known gaps

- **D-003. Step 3's review is complete and closed.** Fourteen agents across
  seven lenses with per-lens adversarial refutation: **123 raised, 66 refuted,
  22 confirmed, the rest downgraded.** Deduplicated, that was 3 blockers and 16
  distinct majors. Every confirmed finding is applied, in two passes. The record
  is at `Z-ISR/_session-artifacts/2026-08-26-plainsight-doctrine-review/`:
  `FINDINGS.md`, `journal.jsonl`, and `review-workflow.js`.

  **Six findings changed an obligation rather than a wording**, and a reader of
  the drafts should know they were added after review rather than designed in.
  Class **N0 NON-PERSON** was added, because the class set covered only natural
  persons while CrossLinked enumerates organizations by design. The
  authorization record had no stratum, despite being the one object carrying
  both a live selector and a named person. `verify_shred` check 1 would have
  passed on a not-found error while reporting the key destroyed, inside the
  criterion that forbids exactly that. SS-8's gate fixture called for a
  NEVER-listed selector, an object the same document forbids, so it could not
  have been built. The RT-17 freeze was renewable without limit and nullified
  RT-5's ceiling; frozen days now count toward it. SS-14 item 3 claimed a
  structural impossibility the system does not have.

  **`DOCTRINE_STATUS.md` now carries a per-criterion row for all 32 Step 3
  criteria.** Before that, both documents declared their tables to be an index
  into a pin of record with no rows for them, so no criterion was stampable.

  **What is left is wording, not obligations:** unmarked paraphrase of quoted
  sources, precision on two refusal strings, and five sentence fragments. Eight
  findings stand refuted and were not applied.
- **D-004 is closed.** All fourteen agents completed. The 26 previously
  unverified findings now carry verdicts. One artefact of the resume is worth
  knowing when reading `FINDINGS.md`: the seventh verifier began before the
  first-pass fixes and finished after them, so three of its confirmations name
  defects that were already corrected, and one REFUTED verdict is REFUTED
  *because* the fix had landed. Read its reasons against the current text rather
  than the verdict alone.

- **D-001.** `tools/validate_retention.py` is a stub. The pre-commit hook calls
  a mechanism that performs no check. Real implementation is Step 8. The review
  raised the consequence for doctrine: any criterion that names `--repo-scan` as
  its enforcement is currently naming a stub, and must say so in place.
- **No commit exists.** The first commit is the operator's, per `CLAUDE.md` §5
  and pending R6.
- **The ratification ladder terminates in one person.** The operator is the
  ratifier, the maintainer, and the analyst, so every operator-approval gate is
  the operator approving their own request. This is stated rather than left
  implicit, because a control whose bypass is undocumented gets bypassed
  silently, and a control whose bypass is a dated entry gets bypassed visibly.

## 5. Session context that lives outside this repository

Wave 0 was produced in a Claude Code session rooted at `Z-ISR/Sherlock/`. The
following exists outside this repository. Some of it is durable and some is not.

**Durable, on disk:**

| What | Where | Why it matters |
|---|---|---|
| Measured Sherlock review | `../Sherlock/sherlock/CAPABILITIES.md` | 64 KB. Source of the 481/429/414 site counts, the 20-worker figure, the 78.8 percent false-positive measurement on excluded sites, and the detection-strategy breakdown. Every OSINT-COP document that cites those numbers cites this. |
| Sherlock clone | `../Sherlock/sherlock/` | Commit `9100f9d`, with `Dockerfile.local`, `docker-compose.yml`, `DOCKER-USAGE.md` added. |
| Built image | `sherlock-local:0.16.1` | 477 MB, in the local Docker daemon. Rebuildable from `Dockerfile.local`. |
| Duplicate design docs | `Z-ISR/*.md` | Byte-identical to `docs/`. See D-002. |

**Published briefings, on claude.ai:**

| Document | URL |
|---|---|
| Sherlock Field Manual | `https://claude.ai/code/artifact/f0d8335a-0498-4eea-803f-8a7c9256ff90` |
| PLAINSIGHT (audit and system design) | `https://claude.ai/code/artifact/c550a27c-d786-4935-a652-c887c0e9de5a` |
| PLAINSIGHT Foundation | `https://claude.ai/code/artifact/acdd9cc7-bee4-4aa5-add7-ba4acb4ec446` |

These are renderings of `docs/OSINT-COP-tool-review.md`,
`docs/PLAINSIGHT-design.md`, and `docs/PLAINSIGHT-FOUNDATION.md`. The markdown
is the record; the artifact is the reading copy. Nothing is in them that is not
in the repository.

**Corrected 2026-08-26. Both entries previously listed here as not durable had
in fact survived, and the false negative was worth more than the caution.**

- **The tool clones are present**, with git history, in the Wave 0 session
  scratchpad under `<wave-0-scratchpad>/`. All
  six audited tools plus nine the audit agents cloned for comparison, including
  `sf` (SpiderFoot, whose ontology the tool review recommends vendoring), `io`
  (IntelOwl), `maigret`, `blackbird`, `ghunt`, and `holehe`. Every `file:line`
  citation in `docs/OSINT-COP-tool-review.md` can be re-verified against the
  exact tree that produced it.
- **The Wave 0 workflow journals are present**, seven runs and 202 agent
  transcripts under that session's `subagents/workflows/wf_*/journal.jsonl`,
  with the generating scripts beside them. They are the only full text behind
  the synthesis documents in `docs/`.

Both live in a temp directory that any cleanup can remove. Copy before relying
on them. Nothing from either may be committed into this repository.

The Step 3 review artifacts are in a durable location rather than a temp one:
`Z-ISR/_session-artifacts/2026-08-26-plainsight-doctrine-review/`.

**One measurement worth re-running rather than trusting.** Tool liveness in
`docs/OSINT-COP-tool-review.md` reflects 2026-08-26 and rots fast. Four of the
six tools were already dead at audit time. Re-probe before relying on any verdict
in that document.

## 6. Standing rules a new session should not have to rediscover

- No agent executes a connector against a live platform. `AGENTS.md` §4.
- No agent lands a Class F change. Drafting is expected.
- No selector belonging to a natural person enters a tracked file, including
  worklog entries and commit messages.
- Unratified binds nothing, and mechanisms read `DOCTRINE_STATUS.md` rather than
  the document they enforce.
- Repo prose follows Register 1 in `CLAUDE.md` §4. Published briefings follow
  `docs/DOCUMENT_STANDARD.md`. Doctrine never becomes a briefing.
