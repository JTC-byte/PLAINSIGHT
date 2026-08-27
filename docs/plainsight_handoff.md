# PLAINSIGHT handoff: current state

Current state only. Rewritten every wave. History lives in
`plainsight_worklog.md` and is never restyled.

Capped at roughly 400 lines. Superseded sections move to the archive on the next
session rather than accumulating here. ZMeta's handoff reached 2,080 lines
carrying eleven superseded state sections, which is the failure mode this cap
exists to prevent.

**Wave:** 0. Doctrine foundation complete. Nothing committed, nothing built.
**Date:** 2026-08-26
**Doctrine items:** 55 total. **All 55 carry a recorded conclusion. 0 have a stamped basis. 0 are committed.**

**Resume here. The doctrine foundation is done. The next thing is a build.**

1. **The operator reviews and commits the transcription.** Every doctrine
   conclusion is recorded in `doctrine/DOCTRINE_STATUS.md` by an agent across
   2026-08-26 and 2026-08-27. R6 puts a Class F commit in the ratifier's hands,
   so nothing is in force until that commit exists, and it is also this
   repository's first commit.
2. **Step 4 and Step 5 are both unblocked and independent**, so either can go
   first. Step 4 is `synthetic/CAST.md` plus a sealed, hash-pinned
   `GROUND_TRUTH.yaml`, and it has lead time that cannot be recovered. Step 5 is
   `spec/layer-model.yaml`, now writable because D6 settled nine event types and
   D7 settled `pse-event-0.1`.

**Nothing is pending a conclusion.** What remains is every basis stamp, the R8
question of whether a third bystander disposition exists, `doctrine/DISCLOSURE.md`
whose deferral trigger has now fired, and the DRAFT header on
`PLAINSIGHT-FOUNDATION.md` line 4 which still says nothing is operator-ratified.

---

## 1. Where the project is

The repository exists and is governed. Nothing is built and nothing is ratified.
No collection mechanism exists, and none can be built until Step 2 completes,
because five of the D and R items block the schema and the runner.

Step 3's two doctrine documents are drafted and reviewed and neither is
finished. They bind nothing. `runner/subject_guard.py` and the retention sweep
will read `DOCTRINE_STATUS.md` rather than these files, and an unstamped
criterion refuses rather than permits, which is what makes an unfinished
doctrine document safe to leave on disk.

The four design documents that preceded the repository are moved in unchanged
under `docs/`. They are rank 7 in the authority order, which means they are
records of intent rather than binding sources. `docs/PLAINSIGHT-FOUNDATION.md`
still carries its DRAFT header.

## 2. What exists

| Path | State |
|---|---|
| `CLAUDE.md` | Written. Advisory. |
| `AGENTS.md` | Written. Normative. |
| `doctrine/DOCTRINE_STATUS.md` | Written. **All 55 conclusions recorded, 0 bases stamped, 0 committed.** Per-criterion rows for every SS and RT item. |
| `doctrine/SUBJECT_SELECTION.md` | **Drafted, all conclusions recorded, not committed.** SS-1 to SS-18. Reviewed; all confirmed findings applied. |
| `doctrine/RETENTION.md` | **Drafted, all conclusions recorded, not committed.** RT-1 to RT-18. Reviewed; confirmed findings applied. |
| `doctrine/RETENTION_LEDGER.md` | **Missing.** Required at v0.1. Shape defined in `RETENTION.md` RT-10. |
| `doctrine/HYGIENE.md` | **Missing.** Advisory, Class A, blocks nothing immediately. |
| `doctrine/DISCLOSURE.md` | **Missing, and now owed.** Its deferral trigger fired when RT-18 created a second egress path. |
| `spec/`, `schema/`, `ontology/`, `policy/` | Empty. Steps 5 through 7. |
| `conformance/` | Empty tree. Step 9. |
| `tools/validate_doctrine.py` | **Written.** Criteria, stamps, cross-references both ways, pin reconcile, counts. |
| `tools/validate_hygiene.py` | **Written.** Voice, tables, citations vs the register, caps, inventories. |
| `tools/validate_conformance.py` | **Written.** Aggregator. `KERNEL_GATE` is the one authoritative list. |
| `tools/validate_retention.py` | Stub. Exits 0, checks nothing. D-001. Reported as STUB by the aggregator. |
| `Makefile` | **Written.** `validate-doctrine`, `validate-hygiene`, `validate-kernel`, `preflight`. |
| `.github/workflows/ci.yml` | **Written.** Kernel gate on push and PR, proves the hook runs, refuses agent trailers. |
| `.githooks/pre-commit` | **Rewritten.** Runs the full preflight battery, not the stub alone. |
| `connectors/`, `runner/`, `app/`, `synthetic/` | Empty. Later steps. |
| `docs/*.md` | Five documents moved in unchanged. |

## 3. What blocks

**Nothing blocks a build any more.** Every doctrine conclusion is recorded, and
D6 was the last item standing between the repository and `spec/layer-model.yaml`.

One thing gates *authority* rather than work: per R6 a Class F commit is authored
by the ratifier, so none of the stamps are in force until the operator commits
them. An agent transcribed them and an agent may not land them.

Two steps are unblocked and independent, so order is a preference:

- **Step 4**, the synthetic cast. `synthetic/CAST.md` and a sealed, hash-pinned
  `GROUND_TRUTH.yaml` with at least one designed confuser pair. It has lead time
  that cannot be recovered, and SS-17 makes the baseline a gate on S3 and S4
  reach, so it is on the critical path for capability rather than beside it.
- **Step 5**, `spec/layer-model.yaml`. Nine event types per D6, labelled
  `pse-event-0.1` per D7. This is the single source the schema enums and
  `policy/semantics.yaml` are both generated from, and ZMeta's mistake of
  restating the same enum in four places is the thing not to inherit.

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
