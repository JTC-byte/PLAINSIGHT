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

## 2026-08-26, Wave 0. Repository cut.

**Class:** A (documentation) plus F (doctrine skeleton, unratified, binding
nothing).

Cut `plainsight/` beside `ZMeta/` and `zisr-recon/` under `Z-ISR/`. Created the
directory tree from `docs/THE-GAMEPLAN.md` §1.2, including the empty lanes
`connectors/`, `runner/`, `app/`, and `synthetic/`.

Copied in unchanged: `DOCUMENT_STANDARD.md`, `PLAINSIGHT-design.md`,
`PLAINSIGHT-FOUNDATION.md`, `OSINT-COP-tool-review.md`, `THE-GAMEPLAN.md`. The
originals remain at the `Z-ISR/` root and are byte-identical. See D-002.
`PLAINSIGHT-FOUNDATION.md` keeps its DRAFT status header. Stamping it is Step 2
and is the operator's act. Editing that line before the stamp would be the
half-stamping `zisr-recon/docs/ENTRY_CRITERIA.md` warns about.

Wrote `CLAUDE.md`, advisory: North Star, eight-rank authority order with the
argument for doctrine outranking the semantic contract, eight design gates, two
voice registers, attribution.

Wrote `AGENTS.md`, normative: dialect declaration with the licensing clause from
`ZMeta/zmeta-spec/AGENTS.md` quoted exactly, change classes A through F with F
new and defined by effect rather than path, Execution Limits, required local
workflow, documentation matrix, ratification rule.

Wrote `doctrine/DOCTRINE_STATUS.md` with sixteen items pending, zero ratified,
and three rejected readings recorded so they are not re-derived.

Installed `.githooks/pre-commit` calling `tools/validate_retention.py
--repo-scan --staged`, and set `core.hooksPath`. The tool is a stub that exits 0
and prints that it checked nothing. Replaced at Step 8.

**Refused this session:** nothing was collected, no connector was executed, no
platform was touched. No file in the repository contains a selector belonging to
a natural person.

**Not done, deliberately:** no commit was made. `CLAUDE.md` §5 carries ZMeta's
human-only attribution rule pending R6, and the first commit is the operator's.

### Deferred issue register

- **D-001** `tools/validate_retention.py --repo-scan` is a stub. Real
  implementation is Step 8. Until then the pre-commit hook is a wired mechanism
  with no check behind it. This is a known gap, not an oversight.
- **D-002** Five documents exist twice, byte-identical, at the `Z-ISR/` root and
  under `plainsight/docs/`. The repository copy is canonical. Two copies of a
  governed document is the drift condition this framework exists to prevent, and
  the originals predate the repository so deleting them is the operator's call.
  Resolution is one of: delete the root copies, or replace them with a one-line
  pointer to the repository path. Not urgent, and it gets worse the first time
  one copy is edited.

### Closeout, same session

Added `README.md` as the cold-start entry point, naming the read order and the
three rules that bind before any doctrine is ratified. Corrected the wording
above from "moved in" to "copied in", which is what actually happened.

Session context that lives outside this repository and is not reproducible from
it is listed in `plainsight_handoff.md` section 6.

**Next:** Step 2. The operator stamps or amends D1 through D5 in
`doctrine/DOCTRINE_STATUS.md`.

---

## 2026-08-26, Step 3. Doctrine drafted. Not ratified, not finished.

**Class:** F (doctrine drafts, unratified, binding nothing) plus A (process
records). Drafting Class F is permitted and expected. Nothing was landed.

New session rooted at `plainsight/`, cold-started from `README.md`. Harvested
the Wave 0 origin session in full: transcript
`b94b0c75-dfa8-4ed6-b1e6-6854a95710d6.jsonl` under the `Z-ISR/Sherlock` project
directory, 3.4 MB, 1,070 records, 9 operator prompts, 2026-08-19 to 2026-08-26.

Step 2 was not touched. It is the operator's act.

Drafted `doctrine/SUBJECT_SELECTION.md`, fifteen criteria SS-1 through SS-15,
and `doctrine/RETENTION.md`, seventeen criteria RT-1 through RT-17. Both carry
the `ENTRY_CRITERIA.md` header pattern: DRAFTED, AWAITING RATIFICATION, nothing
binds, per-criterion markers with conclusion and basis stamped separately. Both
carry a `## What is explicitly NOT gated` section and a rejected-readings
section.

**One deviation from the Step 3 done-condition, stated rather than quiet.**
`docs/THE-GAMEPLAN.md` §3.1 requires the rejected-readings section to start
empty. Both files start it populated instead. §5.4 had already derived and
rejected the HMAC membership oracle, and `DOCTRINE_STATUS.md` already carries
three rejected readings. An empty section would have discarded work already
done. The operator can refuse this reading.

Two citations were verified rather than trusted before being written into a
rank-1 file. `ZISR COP/docs/OPERATIONAL_CONTRACT.md:272` does carry the
prohibition on inferring that a link is fine from the absence of a failure
signal, inside §4, so the RT-12 citation stands. `PLAINSIGHT-design.md:747` is a
connector-manifest `lineage:` field rather than a global storage rule, so it is
already the legal form under RT-8; the flat prose claim at `:648` is the actual
R5 conflict. RT-8 currently names both and is wrong about `:747`.

Ran an adversarial review as a seven-lens workflow with per-lens refutation:
the guard.py defect class, doctrine lane escape, sentence-versus-mechanism,
coverage against the source corpus, cross-document consistency, operator-posture
fidelity including over-restriction as a failure mode, and voice register.

**Stopped at 13 of 14 agents on an approaching usage limit.** All seven attack
lenses completed. Six of seven verification agents completed. Banked result: 123
findings raised, 52 refuted, 28 downgraded, 17 confirmed, 26 unverified because
the seventh verifier did not run. Heavy duplication across lenses, so the
distinct issue count is well below 123.

No findings were applied. Both drafts stand exactly as written, which is the
correct state to pause in: the review is evidence about the drafts, not a
change to them.

**Refused this session:** nothing was collected, no connector was executed, no
platform was touched. No file in the repository contains a selector belonging to
a natural person, re-checked on both new files.

**Not done, deliberately:** no commit. No row added to `DOCTRINE_STATUS.md`,
because the review's confirmed findings include the SS and RT id spaces having
no rows there, and adding rows before the id space settles would create churn in
the pin of record.

### Deferred issue register, additions

- **D-003** The review's confirmed and downgraded findings are unapplied. The
  two blockers are a cross-reference in SS-11 pointing at the wrong RT item, and
  SS-14 item 5 stating in the present tense that it is enforced by a tool that
  is currently the D-001 stub. Findings and the workflow journal are at
  `Z-ISR/_session-artifacts/2026-08-26-plainsight-doctrine-review/`.
- **D-004** 26 findings are unverified. The seventh verification agent did not
  run. They are listed in that same `FINDINGS.md` under UNVERIFIED and must not
  be treated as confirmed.
- **D-002 correction.** The handoff recorded the audited tool clones and the
  Wave 0 workflow journals as not durable and expected to be gone. Both survived
  and were still present on 2026-08-26. Handoff §5 is corrected in this session.

**Next:** apply the confirmed findings, finish the verification of the 26, then
Step 2 remains the operator's.

---

## 2026-08-26, Step 3 continued. Review findings applied.

**Class:** F (doctrine drafts, still unratified) plus A (process records).

Resumed the stopped review workflow from cache. **The seventh verification agent
had not completed when the findings below were applied, so the 26 unverified
findings are still unverified.** They carry no verdict and were not applied. That
is D-004 and it is open.

One consequence to be aware of when that verifier does return: it began reading
the drafts before these edits and will finish after them, so a verdict of
REFUTED from it may mean the finding was already fixed rather than that it was
never real. Read its reasons against the current text, not the verdict alone.

Applied both confirmed blockers and all nine distinct confirmed majors, plus six
findings from the downgraded set that were real on inspection. The full list is
in `plainsight_handoff.md` §4 under D-003. Two of the six downgraded items
changed an obligation rather than a wording, and both are recorded here because
a reader of the drafts will want to know they were added after review rather
than designed in:

- **Class N0 NON-PERSON was added to SS-1.** The class set covered only natural
  persons. CrossLinked's function is to enumerate an organization, and a company
  domain is nobody's personal data, so with no class for it the set either
  silently forbade a wanted capability or forced an analyst to file an
  organization under a person class. N0 authorizes the organization and never its
  members, and it is not self-certifying.
- **The RT-17 freeze is capped at 180 cumulative days.** The drafted version gave
  the freeze an expiry and allowed unlimited renewal, which is the same loophole
  reached one logged act at a time, and it nullified RT-5's ceiling.

`DOCTRINE_STATUS.md` now carries a per-criterion row for all thirty-two Step 3
criteria. Before that, both documents declared their own tables to be an index
into a pin of record that had no rows for them, so no criterion was actually
stampable. Pending count is now 48 of 48, zero ratified. `README.md` and the
handoff counts were corrected from sixteen.

Two citations in the drafts were checked against their sources rather than
trusted. `ZISR COP/docs/OPERATIONAL_CONTRACT.md:272` does carry the prohibition
RT-12 attributes to it. `PLAINSIGHT-design.md:747` is a connector-manifest
`lineage:` field and is already legal under RT-8, so RT-8's action-on-stamping
note was narrowed to the prose claim at `:648`, which is the actual conflict.

One claim was removed rather than supported. A drafted line in RT-15 said the
cast-versus-live distinction was discovered when a Wave 0 sweep flagged the
design's fictional cast. The worklog records no such sweep and the only tool
that could have run one is the D-001 stub, so the line now states the same
requirement as an inference from the files, and says no sweep has been run.

**Refused this session:** nothing collected, no connector executed, no platform
touched. PII sweep re-run over every authored file, clean. Voice gate clean on
all five edited files.

**Not done, deliberately:** no commit, no stamp. The remaining downgraded
findings are wording precision and do not change an obligation.

**Next:** Step 2 is the operator's. Step 4, the synthetic cast, is unblocked and
has lead time that cannot be recovered later.

### Second pass, same session. The seventh verifier returned.

It completed after the entry above was written, so the note above about the 26
unverified findings is superseded rather than wrong: it was true when written.
Final review tally across all fourteen agents: **123 raised, 66 refuted, 5 of
the remaining 26 confirmed, the rest downgraded.** Three of those five
confirmations were findings already fixed in the first pass, and
`doctrine-status-has-no-rows-and-no-machine-form` came back REFUTED because the
verifier read the rows that had been added by then, which is the caveat above
working as intended.

Ten findings were applied in this pass. Four changed an obligation and are
recorded here.

- **The authorization record had no stratum.** It is the one object that
  necessarily carries both a live selector and a named person, since an S1
  consent record names who consented, and the drafted strata table gave it no
  store, no TTL, and no shred path. It is now stratum 1, inside the case
  boundary under the case key, never in the repository. RT-1 is one of the four
  criteria with no later date on which it can be decided, which is what made
  this the pass's one blocker.
- **`verify_shred` check 1 violated the rule printed three lines below it.** The
  drafted check decrypted "a known stratum-0 blob for the case", which check 2
  requires to be gone, so check 1 would have passed on a not-found error while
  reporting that the key had been destroyed. A check that can pass for a reason
  other than the one claimed is not a check, and this one was in the criterion
  that says so. It now runs against a witness ciphertext held outside the
  enumerable delete path, and a not-found, permission-denied, or malformed-input
  result is a verification failure.
- **SS-8's gate fixture could not be built.** It called for a fixture naming a
  "NEVER-listed selector", and no such object exists or may exist, because a
  per-selector never-collect list is exactly what SS-14 item 5 and RT-15 forbid.
  The fixture is now built on a NEVER item the gate can evaluate, and SS-14
  carries a table naming where each of its six items is actually enforced, which
  stops the list reading as six mechanisms when two of them are rules pending
  R7.
- **The RT-17 freeze cap was replaced with a better rule.** The first pass
  capped cumulative freeze time at 180 days. Frozen days now count toward RT-5's
  ceiling instead, so a freeze buys no case more total life than any other case
  gets, and each renewal must name the obligation it serves and an expected
  resolution date. The uncomfortable half is argued in place: if an obligation
  outlives 180 days, this system is the wrong holder of the material.

Also: SS-14 item 3 claimed the system was structurally incapable of mutating a
platform, which it is not, and the vocabulary that would make it so is R7 and is
undrafted. It now carries the conservative reading on the same footing as item 1.
SS-6's dispatch check now covers a credential draw, which it did not.
`purpose` is constrained to a sentence that does not name the subject, because
`RETENTION_LEDGER.md` copies it into a tracked file that survives every shred.

**Refused this session:** nothing collected, no connector executed, no platform
touched. Voice and PII gates clean on all edited files. Cross-references,
criterion counts, and table integrity re-checked mechanically.

**Not done, deliberately:** no commit, no stamp. Eight findings stand refuted and
were not applied. The remaining downgraded items are wording precision.

**Next:** Step 2 is the operator's. Step 4 is unblocked.

---

## 2026-08-26, Step 2. The operator decided twelve items.

**Class:** F throughout. **Drafted and transcribed by an agent, not landed.** R6
puts a Class F commit in the ratifier's hands and no commit exists yet.

Put the open decisions to the operator as two rounds of prompts. Recorded in
`doctrine/DOCTRINE_STATUS.md`: D1 through D5, R1 through R7, and five items that
arose from the operator's own answers rather than from the drafted list.

**Every conclusion is stamped and every basis is unstamped**, at the operator's
choice. The reasoning in `PLAINSIGHT-FOUNDATION.md` §3 has not been reviewed, and
the split-stamp design exists precisely so that unblocks work without pretending
the argument was read.

Five decisions changed the drafts materially.

- **R4, maximum reach.** S0 through S4 available, plus N0 and L0. The drafted
  recommendation was S0, S1, S2 only with S3 and S4 refused. The operator
  overrode it, having been shown the ground-truth argument, and paired the
  override with their own sequencing: the baseline comes from known consenting
  people first. That sequencing became SS-17 rather than a sentence.
- **The web model, from the operator's clarification.** A query names one node,
  person or organization or location, and returns a searchable list of linked
  nodes including alias and shell organizations. Nothing spawns a deep dive.
  Each node is selectable for a deliberate one. This is SS-16, and the important
  property is that the control is the act rather than the class.
- **L0 LOCATION added**, because the operator's web has location nodes and the
  class set had none. A residential address tied to an individual is that
  person's selector and is not an L0 node, which is the carve-out that stops the
  class becoming the route by which a home address turns into infrastructure.
- **R2, ceiling 60 rather than 180**, and **RT-17 reversed**. The first pass had
  frozen days counting toward the ceiling. The operator wants manual holds for a
  stated reason, law enforcement handoff being their example, so the freeze is
  now the one thing that crosses the ceiling. What bounds it is not a cap: every
  renewal names an obligation and an expected resolution date, and the state
  escalates rather than repeating.
- **R7, the interaction line**, which was undrafted and blocked every connector
  manifest. Authenticating with a team-held credential and reading is permitted.
  Anything the subject can observe happened is refused. The unauthenticated-only
  reading would have removed toutatis, informer, and most of the Instagram and
  Discord tooling, which was stated in the prompt.

**Downstream changes the stamps required.** `CLAUDE.md` §5 no longer says R6 is
pending. `PLAINSIGHT-design.md:648` was corrected under RT-8, replacing the flat
"retained forever" with retention for the life of the case and citing the
stamped decision, which closes the R5 conflict that had rank 7 contradicting
rank 1. `README.md` and this handoff carry the new counts.

**One error made and corrected in place.** A regular expression written to strip
the newly-ratified rows out of the pending table also matched the rows it had
just written into the ratified table, deleting seven of them. Caught by a row
count immediately after, restored, and the count re-verified against the
criterion definitions in both documents.

**Refused this session:** nothing collected, no connector executed, no platform
touched. Voice and PII gates clean on every edited file. Cross-references,
criterion counts, and table integrity re-verified mechanically after each batch.

**Not done, deliberately:** no commit. Basis stamps left unstamped. D6, D7, D8
and R8 remain pending and were not put to the operator.

**Next:** the operator reviews the transcription in `DOCTRINE_STATUS.md` and
commits it, which is also the repository's first commit. Then Step 4, the
synthetic cast, which SS-17 has moved onto the critical path for reach.

---

## 2026-08-27, Step 2 closed out. Every doctrine conclusion recorded.

**Class:** F throughout. **Drafted and transcribed by an agent, not landed.**

The session crossed midnight, so the earlier entries carry 2026-08-26 and this
one carries 2026-08-27. That is what was true when each was written.

Put the remaining open items to the operator. Recorded: **D6 nine event types,
D7 `pse-event-0.1` with an Unlocked status header, D8 one repo with the lane
boundary and the split trigger recorded, R8's v0.1 bystander set closed at
`count_only | refuse`.** D6 was the item actually blocking the build, because
`spec/layer-model.yaml` is the single source the schema and policy enums are both
generated from and it could not be written without the event-type set.

**One correction to what the operator had been told.** A previous entry and the
handoff both described the open set as D6, D7, D8 and R8. That was incomplete:
twenty-two of the thirty-five SS and RT criteria still carried no conclusion
stamp, because only the ones tied to a stamped D or R item had received one, and
an unstamped criterion refuses. The full open set was put to them in the same
round and the record now matches.

The operator chose to stamp the mechanism criteria as drafted and to have the
four that encode a choice put individually. Those four:

- **RT-6, the incidental TTL: 7 days, non-extendable.** As drafted.
- **RT-11, `SHRED_FAILED` blast radius: system-wide, cleared only by a passing
  `verify_shred`.** As drafted, and the logged-override alternative was offered
  and declined.
- **SS-2, consent shape: per-case, revocable, explicit expiry.** As drafted.
  Standing consent per person was offered, and declined despite the friction it
  imposes on the calibration baseline population.
- **RT-14, demo and export material: changed.** The operator added a carve-out
  the drafts did not contain.

### RT-18, the change the operator made

The drafted rule was that nothing from a non-synthetic case leaves the case
boundary and demos are built on the cast. The operator added: unless it is to
share with law enforcement or another appropriate agency, in which case the
entire case should be exportable.

That is a second egress path, so it is written as its own criterion rather than
as an exception clause. **RT-18 binds the disclosure export to an active RT-17
freeze**, which is what stops it becoming a general-purpose export with a
serious-sounding name and means every disclosure inherits the freeze's
requirement to name the obligation it serves. It exports the complete case, it is
a logged act naming the receiving agency, it is recorded in the ledger, it does
not alter the shred path, and the interface states at the moment of export that
the copy is permanently outside every mechanism here.

**RT-18 deliberately inverts data minimization**, and that is recorded in the
criterion rather than left as a quirk. Design gate 7 makes every projection lossy
and enforces citation completeness and minimization together. A disclosure export
enforces completeness and refuses to minimize, because handing an agency a
thinned subset of the evidence misrepresents what was found, and choosing which
parts they see is not a decision this project is positioned to make. It is the
only place in the system where that is true.

**A deferral trigger fired as a result.** `docs/THE-GAMEPLAN.md` §2.2 defers
`doctrine/DISCLOSURE.md` until a second egress path exists. RT-18 is that path.
`DISCLOSURE.md` is now owed rather than deferred, and RT-14 with RT-18 stands in.

### State

All 55 doctrine items carry a recorded conclusion. **Every basis is unstamped**,
at the operator's choice, so `PLAINSIGHT-FOUNDATION.md` §3 and
`THE-GAMEPLAN.md` §3.0 remain unread reasoning behind stamped conclusions. Two
housekeeping items follow from the stamps and are the operator's: the DRAFT
header at `PLAINSIGHT-FOUNDATION.md` line 4 still says nothing is
operator-ratified, and D1 through D5 now are.

**Refused this session:** nothing collected, no connector executed, no platform
touched. Voice and PII gates clean. Criterion counts, cross-references and table
integrity re-verified after each batch.

**Not done, deliberately:** no commit, no basis stamps, and `DISCLOSURE.md` not
written.

**Next:** the operator commits. Then Step 4 and Step 5, which are independent of
each other and both unblocked.

---

## 2026-08-27, the doctrine gates. Written before the first commit.

**Class:** C (tooling) plus A (documentation).

Reviewed `ZMeta/zmeta-spec` for the thoroughness bar: its `Makefile` named
gates, its CI on push and pull request, and `validate_conformance.py` keeping
`KERNEL_GATE_CHECKS` as one authoritative list so a new sub-check joins the
battery in one place rather than in every document quoting the command. Two
patterns carried directly: an empty fixture file proves nothing and is refused,
and a refusal string names what failed and where.

ZMeta has no `.githooks`. This repository does, and that divergence is correct:
there the irreversible act is publishing, here it is a selector reaching git
history.

**Scope, set by the operator: only doctrine exists to check.** No validator was
written for an artifact that does not exist, and none was stubbed to look busy.

Wrote `tools/validate_doctrine.py`. Every check in it exists because the
corresponding defect actually occurred during Step 3 and was caught by an
adversarial review rather than by a mechanism: the SS-11 pointer that named RT-4
instead of RT-6 and was broken in exactly one direction, the pin of record
carrying no rows for the criteria that declared themselves indexed into it, a
criterion marker and its pin row disagreeing silently, and prose counts drifting
from the tables they count. It reconciles in both directions, because one
direction finds half the drift.

Wrote `tools/validate_hygiene.py`: the voice standard, table structure, the
handoff and worklog caps, and the tools-to-gates inventory in both directions.
Its citation check judges a cited path against the artifact register rather than
against the filesystem, because `CLAUDE.md` and `AGENTS.md` legitimately name
artifacts that are planned and unbuilt, and what is not legitimate is a path in
no register and on no disk. **It prints the Register 1 rules it cannot reach on
every successful run**, so a green result is not read as a full voice review.

Wrote `tools/validate_conformance.py`, the aggregator, with `KERNEL_GATE` as the
one authoritative list. It adds one thing to ZMeta's pattern: **a check that is
not implemented reports as PENDING and never as a pass**, naming the step that
delivers it. The failure that prevents is one this program has already measured,
where `validate_retention.py` returns 0 while checking nothing and is harmless
only because it says so.

Wired `Makefile` with `validate-doctrine`, `validate-hygiene`, `validate-kernel`
and `preflight`; rewrote `.githooks/pre-commit` to run the preflight battery
rather than the stub alone; added `.github/workflows/ci.yml` on push and pull
request. CI also proves the hook is still executable and still runs, so a hook
that quietly stops working is caught, and it refuses any `Co-Authored-By`
trailer naming an agent, which makes R6 a mechanism rather than a sentence.

**Two real defects found by the tools on their first runs, both fixed.**
`runner/reconcile_ledger.py` is named by RT-10 and was in no artifact register,
which is exactly the gap the adversarial review predicted and which no human
pass had caught since. SS-14's stamp marker was still partial after the
2026-08-27 batch stamp, because its marker text differed from the one the batch
replaced.

**The gates were tested by breaking the corpus.** A reciprocal pointer was
inverted to reproduce the original SS-11 defect and an em-dash connector was
inserted into `README.md`; both gates refused, from both directions, and the
corpus was restored. Design gate 1 asks for a constraint covered by a test that
fails when the constraint is removed, and a gate nobody has seen fail is an
assumption.

**Not done, deliberately:** no validator for schema, ontology, policy,
authorization, connectors or divergence. Those artifacts do not exist, and the
aggregator names all six as pending with their step.

**Refused this session:** nothing collected, no connector executed, no platform
touched.

### R6 amended, and the first commit made

The operator read back the R6 prompt and corrected their answer: an agent may
commit or push when told to for that act, with the operator marked as author.

Recorded as **R6 v0.2** in `DOCTRINE_STATUS.md` rather than as an edit to v0.1,
because a stamped item that changes quietly is the drift the pin of record
exists to prevent. `CLAUDE.md` §5 and `AGENTS.md` §4 both carry the amended
reading.

The amendment separates two things the original conflated. **The decision stays
the operator's**, and an agent still may not decide a Class F change. What moved
is the mechanics: git records the configured identity as author either way, so
requiring the operator to type the command bought no protection. The
authorization is per-act rather than standing, so a general willingness to have
commits made is not authorization for the next one.

The attribution half is unchanged and is now a mechanism rather than a habit:
`.github/workflows/ci.yml` refuses any history containing a `Co-Authored-By`
trailer naming an agent.

**This entry is the honesty surface the amendment moves the load onto.** The
Wave 0 commit was written and executed by an agent under the operator's
instruction of 2026-08-27, authored as the operator, containing the governance
skeleton, both rank-1 doctrine documents with all 55 conclusions recorded, the
three doctrine gates, the Makefile, the CI workflow, and the pre-commit hook.
Nothing in it was collected and no platform was touched.

---

## 2026-08-27, hardening. Two rank-1 files added, and a count I got wrong.

**Class:** F (two new rank-1 doctrine files, conclusions recorded) plus A.

**Correction to the two entries above.** They state that all 55 doctrine items
carried a recorded conclusion. The true count at that moment was 52. The number
was wrong when written, so it is corrected here rather than edited there, because
a process record showing a correction is worth more than one that reads clean.
`validate_doctrine.py` now counts criteria mechanically, which is why the error
surfaced at all.

Four decisions from the operator, and one of them reshaped the plan.

**SS-19, collected content is data and never an instruction.** Raised by the
operator asking what stops someone using a cast account to attack them through an
agent. The answer is that the fake accounts are the minor vector and the product
is the major one, since every bio, display name and message body this system
collects is attacker-controlled text reaching a context that can act on it. The
criterion is scoped to the two consequences doctrine owns, an unauthorized
subject and an unauthorized egress, and leaves general escaping to ranks 2 and 7.
The sharper case was already in the design: `command_template` interpolates a
selector into argv, so a handle carrying shell metacharacters is command
injection reaching further than any prompt. Argv construction refuses a selector
that does not match its registered matcher rather than escaping it.

**SS-20, the collection pool is not the cast.** This is the finding of the
session. Two populations of team-created accounts exist and the resemblance is
the trap: the accounts that authenticate so a connector can read, and the
accounts that are collected on. Most audited connectors cannot run at all
without the first, which nobody had scoped. If they overlap the system partly
observes its own infrastructure, ground truth is wrong in a direction nobody
would check, and the platform-side log ties collection activity to the
measurement population permanently. Enforced as a disjointness check that counts
a shared recovery selector as an intersection.

**`doctrine/EGRESS.md`**, six criteria. The operator chose a compartmentalized
deployment and, when asked where case material then lives, chose the isolated
environment. That answer is what makes retention true rather than nearly true: a
copy on a second machine is a copy the sweep does not reach and the receipt does
not cover. EG-2 therefore has RT-4's property of having no later date on which it
can be decided. The file also states plainly what compartmentalization is not: a
dedicated egress address would make the research population more correlatable
rather than less, because a static address unique to one account links every
persona behind it.

**`doctrine/CREDENTIAL_LIFECYCLE.md`**, eight criteria. Carries the measured
toutatis finding that a session token passed as `-s` on the command line lands in
shell history and the process list. CR-7 records a burned credential as a
capability finding rather than as an operational loss, because a burn says this
connector at this rate against this platform at this account age gets caught, and
that survives every shred.

**Step 4's done-condition was reshaped** from three personas on two platforms to
two personas on two platforms across two email domains. One domain would give
every persona a shared email root, which is a correlation surface the cast exists
to test and which destroys the confuser pair. Phone numbers cap the cast rather
than budget or effort, and resold numbers from verification services are ruled
out on measurement grounds: a recycled number may carry correlations nobody
designed. The operator chose to provision the collection pool first, since
without it no connector runs and nothing can be measured.

**Rank 1 now holds four files**, one per question doctrine owns, and both
governance files moved in the same change per the documentation matrix. Section 3
of `AGENTS.md` still said an agent may never land a Class F change, which the R6
amendment had already superseded in section 4; that contradiction is closed.

**The gate learned the two new namespaces.** `validate_doctrine.py` checks EG and
CR criteria on the same terms as SS and RT, and refused both files on first run
for having no rows in the pin of record, which is the check working.

**Refused this session:** nothing collected, no connector executed, no platform
touched.

**Not done:** the operator's decision that live execution stays an operator act
means `AGENTS.md` section 4's first Execution Limit is unchanged and correct.

---

## 2026-08-27, gate telemetry, injection tagging, and HYGIENE.md.

**Class:** F (RT-19, SS-21) plus A (HYGIENE.md advisory) plus C (tooling).

Two operator requests, and the second one has a conflict with the operator's own
posture that is recorded rather than resolved quietly.

**Gate telemetry.** `tools/gate_log.py` appends one record per gate run and
sweeps past a 90 day TTL on every write. `doctrine/HYGIENE.md` HY-1 to HY-4 owns
the adjudication, `RETENTION.md` RT-19 owns the lifetime, and stratum **T** was
added to the RT-1 table for it.

**The rule that makes telemetry safe: a record names the file and the line and
never the string that matched.** A `--repo-scan` refusal fires because a
selector-shaped value was found, and a record quoting it would turn the gate's
own evidence into the durable surface the gate exists to prevent. The allowed
field list in `gate_log.py` is a fixed tuple, so widening a record requires
editing that tuple rather than passing an argument.

HY-2 names both failure directions, because both are silent. A check that never
fires is indistinguishable from a check that works, which is the measured
`guard.py` defect. A check that always fires gets routed around rather than
fixed. Thresholds are deliberately non-numeric: with one contributor a rate is
not a statistic, so the telemetry informs the judgment rather than making it.
HY-4 records the gates that were reviewed and kept, on §5.9's reasoning that
recording only failures removes the baseline.

**Injection tagging, SS-21, and the conflict.** The operator asked for accounts
carrying injection payloads to be tagged so there is a list of actors to avoid.
The detection half is clean and is now doctrine. The list half runs into RT-2:

- The **payload family** is a finding. No subject values, stratum 3, survives
  every shred, and it generalizes to accounts nobody has met.
- The **account roster** is subject-derived. RT-2 forbids it in a surviving
  stratum, so the tag lives inside the case and dies with it.

**A persistent roster is a target package wearing a defensive name.** That is
recorded in the criterion in those words, because the operator's stated posture
is that target packages are not maintained here, and the intent behind a list
does not change what the object is. Keeping one would need a ratified exception
to RT-2, and SS-21 does not create it.

**AR-1, the first entry in a section empty since Wave 0.** The operator raised
publishing such a list as a possible public good and marked it a later decision.
The argument recorded for that decision is the program's own rather than a moral
one: SS-18 establishes that precision is not computable against an S4 subject, so
a published roster carries a false-positive rate that is unknown by construction,
and each false positive is a public accusation against an identifiable party with
no way to contest it. The honest publishable form is signatures rather than
accounts. Recorded as an assistant reading awaiting confirmation, not decided.

**Two count errors the tools caught.** RT-1's prose said "Five strata" while the
table carried seven rows, stale since the authorization row was added. And
`gate_log.py` was refused by the hygiene gate on its first run for existing
without a Makefile target, which is the tools-to-gates inventory reconcile
working on a file written minutes earlier.

**Refused this session:** nothing collected, no connector executed, no platform
touched.

**Not done:** `EGRESS.md`, `CREDENTIAL_LIFECYCLE.md`, `HYGIENE.md`, SS-19 through
SS-21 and RT-19 are all unreviewed. The other two rank-1 files went through
fourteen adversarial agents and these have had none. A review pass is owed before
building against them.


---

## 2026-09-03, the review the last entry said was owed, plus Steps 4 and 5.

**Class:** A (review artifacts, worklog, handoff) plus B (`spec/layer-model.yaml`)
plus C (tooling, the first test, gate wiring) plus **F drafted and not landed**
(four doctrine patches, and the cast).

The previous entry closed with an obligation: EGRESS.md, CREDENTIAL_LIFECYCLE.md,
HYGIENE.md, SS-19 through SS-21 and RT-19 had no adversarial review, while the
two older rank-1 files had fourteen agents each. That review ran. Two build steps
ran alongside it.

### The review

Five lenses, then five independent verifiers whose instruction was to refute.
The record is `Z-ISR/_session-artifacts/2026-09-03-plainsight-doctrine-review-2/`:
five `findings-*.md`, five `verdicts-*.md`, and the four patches.

**92 raised, 21 confirmed, 35 downgraded, 27 refuted**, with the rest carried as
notes. Deduplicated, that is **2 blockers and 6 majors**.

**The refutation rate is the finding worth recording.** Nine of sixteen
lane-escape items fell, seven of eighteen threat-model items fell, and six of
eighteen operator-intent items fell. Two blockers fell on text the finding quoted
and then argued past. The pattern in the refusals is one thing: a reviewer reads
a criterion, does not find the answer in it, and does not look in the sibling
file that has it. SS-16 answered three separate findings that each declared
doctrine silent, and the grep that missed it searched for "recursion" against a
corpus that says "spawns" and "fanning out". A single-lens review of this corpus
is worth less than its finding count suggests, and the verifier pass is what made
the count mean anything.

**Both blockers are one defect with two consequences, and both are R4 residue.**
The operator decided R4 as maximum reach on 2026-08-26, S0 through S4 plus N0 and
L0, overriding the drafted S0-to-S2-only recommendation. The drafts were patched
where the decision was visible and not where it was buried. SS-4's
required-field table still gave `subject_class` the domain "S0, S1, or S2", and
that table is the one `schema/subject-authorization.schema.json` compiles from,
so a schema author following the corpus faithfully would have refused every
organization, location, public figure and third-party authorization record the
operator had decided to allow. SS-1's N0 paragraph still limited promotion of an
enumerated person to the same three classes, and it is the only place in the
corpus naming a `conformance/gate/` fixture for that path, so the overridden
reading was the one heading for a mechanism. SS-16 says the opposite in terms and
even anticipates the misreading: "a reader could take this criterion for a
restriction on reach and it is not one."

**The one real gap is third-party egress**, confirmed by two verifiers
independently. `EGRESS.md` holds rank 1 on the ground that it answers what leaves
the machine, and every criterion in it governs one boundary, LOCAL against
ISOLATED. A selector handed to a vendor or to an intermediary a tool routes
through leaves under no criterion at all, which is the largest flow of subject
values out of the system by count. The audit measured two undeclared channels in
the surveyed tools and asked for a declaration allowlist by name. Drafted as
EG-7 in patch 4, unratified.

**What the operator does not have to decide.** Six findings asked doctrine to
rule on a category of data, a deployment shape, an environment marker, a
compartment granularity, or an interface design, and the verifiers refused all
six against `CLAUDE.md` section 2's inverse bound. The public-records question is
the one worth naming, because the operator raised the capability on 2026-09-03
and a lens called doctrine's silence a gap: RT-1 assigns whatever is collected to
stratum 0 or 1 at the case clock inside the shred boundary regardless of source
category, so a criminal record has a stratum, a clock, a key and a shred path the
moment it is written. Whether it should have a shorter clock than a follower
count is a live question and it is not a defect.

**One finding was refuted on a point that changes what the product can be told.**
A lens read SS-10's `count_only` as permitting a count and not a roster, and
concluded the social web the operator described was refused at manifest
validation. The verifier found `count_only` is defined nowhere in doctrine, that
the rank-7 draft it was read against pairs `enumerable: false` with both
dispositions so that field cannot be what distinguishes them, and that SS-16 and
section 9 permit a listed, searchable, linkable web in terms. The web is
permitted. The 7-day incidental TTL on its nodes is real, ratified, and its cost
is written into RT-6 with the trigger that reopens it.

### Step 5, the layer model

`spec/layer-model.yaml`, 1,803 lines, and `tools/validate_layer_model.py`. The
nine event types D6 stamped are enumerated for the first time, because D6 was
stamped as "nine" and no governed file said which nine: AUTHORIZE, COLLECT,
PROBE, EXTRACT, LINK, IDENTITY, ADJUDICATE, ASSESS, SYSTEM, with PROBE split into
RUN_START, ITEM and RUN_END at the subtype level. The arithmetic is the only one
that yields nine, and the two alternative readings give eight and eleven, which
is recorded in the file rather than resolved.

**The D5 line is a named check.** A `PROBE_EVENT` RUN_START requires a
`COLLECT_EVENT` PERMITTED parent in lineage, and the validator fires if that
entry is deleted, so the gate that makes the subject guard structural cannot be
removed quietly. `--self-test` breaks the model in memory nineteen ways and
asserts each refusal.

**Nine interpretive readings are recorded as `pse.readings` awaiting
confirmation.** The one that matters is LM-R2: FOUNDATION section 4.2 requires
`confidence` on LINK_EVENT, the design's CUT LIST A kills all machine confidence
arithmetic, both are rank 7, and they conflict. Resolved as prohibited on every
type with the CLUSTER band as the only ordinal, enforced by the validator, so
reversing it is one edit rather than a hunt.

### Step 4, the cast

`synthetic/CAST.md`, `synthetic/GROUND_TRUTH.yaml` and `tools/validate_cast.py`,
all three DRAFT, UNRATIFIED and UNSEALED. Three personas: P-A linked across two
platforms by five designed surfaces, P-B the confuser sharing nothing true with
P-A and carrying both SS-19 injection payload families, P-C an optional pure
negative costing one more real SIM. Four confuser pairs, three firing rationale
code `h` and one firing `t`, so the cast's negatives are not all string
collisions.

**Every value is a placeholder and no payload string exists in either file.**
`AGENTS.md` section 4 forbids an agent writing a selector into a tracked file and
a synthetic value is still a value, so the operator fills them at account
creation and seals once. `--placeholder-scan` refuses a filled value while the
file is unsealed, which puts that rule in the pre-commit hook rather than in an
instruction.

The unsealed state prints as its consequence on every run, including under
`--quiet`: this cast cannot score anything and SS-14 item 6 refuses collection
until it is sealed and stamped.

### The first test in this repository

`tools/tests/test_gate_log.py`, twelve tests. Design gate 1 says a constraint is
not done until a test fails when it is removed, and until today no test of any
kind was tracked, so every mechanism on disk was an assumption in exactly the
sense HY-2 warns about.

**Seven constraints were deliberately broken on a scratch copy and all seven were
refused**, which is HYGIENE.md section 2's instruction carried out rather than
quoted. Three of the breaks are corrections rather than confirmations, and each
was a verified finding:

- **`where` was an unconstrained string**, so HY-1's rule that a record never
  carries the matched value rested on every caller passing a location. It now
  checks a shape and writes `REDACTED_WHERE` otherwise, with the refusal still
  counted. The `--repo-scan` implementation at Step 8 is the caller with the
  strongest temptation to pass the match, and it now cannot.
- **The `ALLOWED` tuple that HY-1 and RT-19 both credit as the mechanism filtered
  a dict built from exactly those keys**, so it dropped nothing. `record()` now
  discards unknown keywords, which makes the doctrine's sentence true.
- **The TTL swept only on write**, so an idle repository retained records past 90
  days and rendered them. It sweeps on read as well. RT-19's "inaction is
  deletion" was the one place in the corpus where inaction preserved.

**One caller behaviour was also wrong and the numbers it produced were the ones
HY-2 adjudicates against.** HY-1 says one line per gate run; a refusing validator
wrote one line per finding, so ten clean runs plus one refusing run with three
findings rendered as 13 runs and 3 refusals, a 23 percent refusal rate against a
true 9. Split into a run record and per-finding detail records. The older window
is left over-counted rather than rewritten, because rewriting a telemetry history
to look consistent is the laundering design gate 6 forbids.

### Gate wiring

`layer-model`, `cast` and `telemetry` joined `KERNEL_GATE`, which now reports
**five implemented, one stubbed, six pending**, up from two implemented. All five
run in the pre-commit hook and in CI. Two CI defects were fixed in the same
change: the checkout fetched one commit, so the attribution check that
`CLAUDE.md` section 5 calls a mechanism inspected a single commit body and would
pass a trailer anywhere below the tip, and the new validators need PyYAML, which
CI installed nowhere and which would have made them exit 2 rather than pass
vacuously.

### What was drafted and not landed

Four patches in the review directory, applying in order onto a pristine tree with
every gate green, verified from scratch:

1. **Staleness and citations**, 18 hunks. Every doctrine file said NOT YET
   COMMITTED and two said their newest criteria were uncommitted, eight days
   after `a54061b` landed them. SS-20 said CREDENTIAL_LIFECYCLE.md was unwritten
   in the same commit that wrote it. RT-12 cited `OPERATIONAL_CONTRACT.md`
   section 4 lines 269 to 273 for a sentence that is at 315 to 317. HYGIENE.md
   quoted a THE-GAMEPLAN sentence its own commit had deleted. SS-14 item 6 said
   `make preflight` runs the same four checks it names, and none of the four
   exists.
2. **R4 residue**, 6 hunks. Both blockers.
3. **Precision**, 13 hunks. The guard.py precedent, which its own repository
   hardened on 2026-09-01 while this corpus still describes it in the present
   tense as broken; the telemetry corrections above, in the criteria that claim
   them; RT-8's 90-day media clock, which cannot fire under RT-5's 60-day ceiling
   except under a freeze; the LOCAL-compromise residual EG-3 creates and does not
   name.
4. **Obligation drafts, Class F**, 6 hunks. EG-7 third-party hosts, EG-2 vault
   key custody, CR-3's process environment, CR-6's clearing act. Each carries an
   UNRATIFIED marker and a pending row, so an unstamped criterion refuses rather
   than permits and the corpus stays internally consistent while the operator
   decides.

**Refused this session:** nothing collected, no connector executed, no platform
touched, no account created, no doctrine landed, no commit made.

**Not done:** the four patches are unapplied and the operator decides all four.
`doctrine/RETENTION_LEDGER.md` and `doctrine/DISCLOSURE.md` are still owed. The
D-001 repo-scan is still a stub. Every basis stamp is still unstamped, which is
now the oldest open item in the program.

### Later the same day: Step 6, and CONFORMANCE.md

Written after the entry above, while the operator was away, and appended here
rather than folded into it because a process record is added to rather than
rewritten.

**`ontology/selectors.yaml`, 895 lines, and `tools/validate_ontology.py`.** D2 in
one file, and the last artifact gating Step 7. Nineteen selectors, of which five
are proposed rather than inherited from the FOUNDATION draft, and every proposed
one is marked as such because an addition to a closed vocabulary is the
operator's to ratify. Two anchor-eligible, two constraint selectors, seven entity
types, four prohibitions, seventeen matchers, none calibrated. Sixteen
deliberate breaks in `--self-test`, all refused.

**The five proposed selectors are what the operator's 2026-09-03 description
needs and the FOUNDATION draft did not cover:** an alias name, a postal address,
an organization registration number for the shell-entity pivot, a public-record
identifier, and a platform-unbound username string for sweep inputs.

**`postal_address` carries SS-1's carve-out structurally rather than leaving it
to a reader.** A required `premises_class` decides whose selector an address is:
residential means it is that person's own selector at that person's class and is
never an L0 node, non-residential is eligible for L0 on a written statement, and
undetermined is handled as residential. The unresolved default is the
conservative value, and the class is recorded by a person and never inferred from
the address string, which is SS-1's rule that the gate reads a class rather than
inferring one. Without that field the location class becomes the route by which a
home address stops being personal data, which is the one thing SS-1 says a
location class must not do.

**There is no `criminal_record` selector and that is deliberate.** A criminal
record is reached through a public-record identifier and read as claims, which
puts it in stratum 1 on the case clock like everything else derived from a
subject. Whether that category deserves its own clock is the live question the
review raised and it is not settled here.

**Relationship selectors are refused, and the reason is doctrinal rather than
aesthetic.** A selector is a string you pivot on, and "employed by" is not one. A
relation is an EXTRACT_EVENT claim whose `selector_type` is the other endpoint,
which is already registered, and a same-person relation is an IDENTITY_EVENT. The
decisive argument is that a relation selector would let a pivot walk from an
authorized subject to an S5 INCIDENTAL person, which SS-10 forbids, so adding one
would be Class F rather than the Class B addition it looks like. The social web
needs no new type: follower and membership enumeration already yields
`platform_uid`, `handle` and `channel`. Recorded in the file with
`change_class_if_added: F` so the next author meets the argument rather than
rediscovering it.

**Ten readings are recorded as `ontology.readings` awaiting confirmation.** The
two worth the operator's attention are ONT-R3, that an Org is deliberately not
anchored on its registration number even though the design's argument would
permit it, at the cost that two records for one company are structurally
indistinguishable; and ONT-R10, that every `fp_mode_basis` in the file is
`reported` or `reasoned` and none is `measured`, including the toutatis finding,
which is the honest state of what this program has actually observed.

**One thing the registry states rather than hides.** The matchers for
`person_name`, `org_name` and `postal_address` are weak by construction, because
those values are free-form. SS-19's argv refusal reads a matcher, so the refusal
is weakest exactly where the value is most free. That is in the matchers block
rather than left to be found at Step 12.

**`CONFORMANCE.md`, 155 lines.** The honest negative claim, the four licensing
conditions with three of the four marked absent, the five-rung ladder with four
rungs that cannot run, and a section saying in terms that a green kernel gate is
a regression check rather than a conformance claim. It found two things and
states both rather than resolving them: the forbidden compatibility claim is
checked inside one file rather than across the tree, and the whole-tree version
belongs to a Step 9 validator that does not exist; and FOUNDATION §4.4 names the
ontology validator `check_ontology` while the register names it
`validate_ontology.py`. The register is the authority and Step 6 used its name.
FOUNDATION was left unedited, because it is voice-exempt as a record of intent
and rewriting it would falsify what was true when it was written.

**The kernel gate now reports six implemented, one stubbed, five pending**, up
from two implemented this morning. All six run in the pre-commit hook and in CI.

**Refused in this half of the session:** nothing collected, no connector
executed, no platform touched, no doctrine landed, no commit made.

### Later still: the layer model reviewed, and repaired

The layer model went to an adversarial reviewer before Step 7 generates from it,
on the same argument that made the doctrine review worth doing. The record is
`findings-F-layer-model.md` in the review directory.

**31 findings: 3 blockers, 18 majors, 10 minors.** This reviewer proved every
claim by mutating the model in memory and calling the validator, rather than by
reading, which is why its measured results are quoted as facts rather than as
readings. All 31 were applied.

**The first blocker is the one worth remembering, because it is the program's own
flagship defect reappearing inside the mechanism built to prevent it.** The rule
that makes D5 structural required a `PROBE_EVENT` RUN_START to have *a*
`COLLECT_EVENT` PERMITTED parent in its lineage, and nothing bound that decision
to the run it authorized. Both events carried `connector_id` and
`target_selector_type` and no rule related them, so one permitted decision
authorized unlimited runs against selectors the gate never evaluated. That is
`guard.py`'s `scope`: a field declared, required, printed, and never read by
`check()`. Fixed as a `run_matches_its_decision` rule. Whether one decision may
parent several runs is a separate question and is recorded as LM-R10 rather than
decided, because SS-6's "one dispatch path" reads as one decision per run and
that is the operator's call.

**The second blocker.** `argv`, `command`, `credential` and `credential_value`
were prohibited on `PROBE_EVENT` alone while the code they fire declared itself
to cover any payload, so eight of the nine types would have generated a schema
branch accepting a filled argv. CR-3 says a credential value never appears in
argv, and the validator enforced the six session-token names on every type and
stopped there. The four names now sit in every type's denylist and in every
layer's `never_carries`, so L-05 holds them the way it already held the six.

**The third blocker.** LM-R4 put the AUTHORIZE payload at stratum 2 on the ground
that it was structurally forbidden from carrying the record's contents, and
`reason` was a required, unconstrained free-text field on a payload that is
permanent, declared to carry no subject values, and crossing to LOCAL. The same
file had already constrained the identical field on `SYSTEM_EVENT` and not this
one. Both now carry the constraint and a code rather than a comment, and LM-R4's
text was corrected: a name denylist is what the mechanism delivers, and ZMeta's
own `policy/semantics.yaml` documents the re-keying residual that follows, which
PSE had inherited the mechanism from without inheriting the disclosure.

**The eighteen majors are one pattern: checks that could not refuse.** The D5
check caught deletion and not widening, so appending a second parent alternative
passed, including a `COLLECT_EVENT REFUSED` parent, which is a run the gate had
declined. The rule governing which strata may cross to LOCAL was validated
against itself, so widening it plus the flags it governs passed clean. The two
enums the model itself labels Class F by effect, `bystander_disposition` and
`subject_class`, had no check at all, so the exact one-line diffs `CLAUDE.md`
gate 2 names as its examples passed. The envelope's required fields, including
the `case_id` that D4 keys the crypto-shred on, were declared and read by
nothing. Four of the sixteen fixtures could be remapped to an unrelated code and
pass, in a tool whose own docstring cites RT-9's rule that a check which can pass
for a reason other than the one claimed is not a check.

**The self-test grew from 19 deliberate breaks to 60, and it now asserts sole
cause rather than membership.** Eight of the original nineteen fired codes beyond
the one they claimed to exercise, which is the fixture-runner defect gameplan
section 2.4 says PSE fixes on day one, present in the tool that enforces it.
Forty-eight of the sixty now refuse by the expected code alone and twelve cascade
with a stated reason. Seventeen of the thirty-five codes the tool could emit were
exercised by no mutation; forty-three distinct codes are now covered. Checks went
from L-19 to L-33.

**Two findings were recorded rather than resolved.** ADJUDICATE's
`allowed_targets` and `required_parents` disagree about four dispositions, and
which way to reconcile them is LM-R11. The model also read Class D more narrowly
than `AGENTS.md` defines it, which is a rank-4 question, so the narrowing clause
became the question.

**The repairs were verified independently rather than accepted.** Seventeen of
the mutations the review measured as passing were rewritten from scratch in the
parent session, run against a baseline confirmed clean first, and all seventeen
refused. The applying agent reported twenty-nine of twenty-nine by its own
script; the seventeen re-derived here are the subset that could be reconstructed
without reading that script, which is the point of re-deriving them.

**Two things the review missed, found while applying it.** Making `requires`
load-bearing produced a check nobody asked for, refusing a rule whose
unconditional `requires` names a field absent from `payload.required`, and that
is what catches the dropped-citations mutation the review had filed under
envelope shape where no envelope check reaches. And two claims written during
the repair were cut for overstating the mechanism, both about the new
`allowed_targets` check, which does not reach the subtype dimension and now says
so.

**Refused in this half of the session:** nothing collected, no connector
executed, no platform touched, no doctrine landed, no commit made.

---

## 2026-09-04, the two closeout commits, and the record neither of them moved.

**Class:** A (`AGENTS.md` sections 6 and 8, `CHANGELOG.md`, both process
records, `README.md`, `CONFORMANCE.md`, patch 1's fact corrections across six
doctrine files, and two mechanism comments).

Two commits landed after `d99f213` on 2026-09-04 and neither of them moved this
file. The account of those two below is written after the fact from the commits,
the changelog and the diffs, in the same way the first three changelog entries
are marked.

### `8a856b3`, the changelog this repository owed, and the handoff standard

`CHANGELOG.md` was written and backfilled across the first three commits rather
than started from that day forward, in the shape the parent repository uses:
what changed, which surfaces moved, what validation ran, and what did not
change. The last of those is the half a reader needs most.

**Why it went missing for three commits is worth recording, because the cause
was this repository's own documentation matrix.** The register at
`docs/THE-GAMEPLAN.md` section 2.1 has listed the file at v0.1 since Wave 0, and
the matrix named it in exactly one row, the Schema row, for an artifact nobody
has built. An obligation attached to an artifact that does not exist is an
obligation nothing reaches. The matrix now carries it on every row.

`AGENTS.md` gained section 8. It sets the five questions a completed change
leaves the next maintainer able to answer, and it states that a closeout is one
act rather than three: the battery, then the records, then the commit, in that
order, because a record written after the commit describes a tree that is
already in the history. A table there names the three surfaces every closeout
moves, which are the changelog, this worklog, and the handoff.

**One clause in section 8 binds the commit rather than the records, and it is
why the four review patches were still unapplied at `8a856b3`.** A closeout commit carries no Class F change the operator has
not decided. An agent may draft one, and per R6 as amended may execute the
commit of a decision the operator has made, so a draft waits outside the commit
as a patch with its argument beside it. A closeout that quietly includes a
doctrine amendment has made the ratification a formality.

`docs/plainsight_handoff.md` gained section 0, answering those five questions
for `d99f213`.

**The hygiene gate refused that change three times before it passed**, each time
on em dash connectors copied out of the parent repository's changelog, whose
voice standard permits them and whose child's forbids them. That is the gate
working on a file it had never seen.

### `533da17`, the entry regress ended by rule

`8a856b3` introduced two honesty defects into the file it had just created. The
changelog carried no entry for the commit that wrote it, and it labelled the
`d99f213` entry as written with its commit when it was written in the one after.

Both are corrected, and the header now carries the convention that stops the
defect repeating: from the next change onward an entry rides in the same commit
as the work it describes and cites no hash, because it cannot know its own. That
is what `ZMeta/zmeta-spec/CHANGELOG.md` does, where a hash appears only when an
entry refers to some other commit. The convention also terminates the regress
the first four entries walked into, where an entry written after the fact needs
a commit, which needs an entry, which needs a commit. `533da17` therefore has no
changelog entry of its own and cannot be given one.

### Why neither commit moved this file

The rule both commits failed was written in the first of them. `8a856b3` added
the section 8 table naming the changelog, this worklog and the handoff, then
moved the changelog and the handoff and left this file untouched. `533da17`
moved the changelog alone.

**No mechanism refused either commit, because no mechanism reads either process
record for an entry.** `tools/validate_hygiene.py` is the only gate that opens
this file, and four of its checks reach it: em dashes, the three cadence
openers, unterminated table rows, and backtick path citations. One of its two
caps counts the ten live entries here. Nothing counts entries against commits,
so the section 8 obligation to move all three surfaces is enforced by a person,
which is the state design gate 1 describes as a rule living in a README.

The honest reading of the sequence is that both commits were treated as being
about the changelog rather than as closeouts of their own. `8a856b3` was the
commit that made the changelog exist, so the new artifact got the attention and
the two records already in place got none.

### What this session verified rather than assumed

**The whole battery is green at `533da17`, measured rather than carried
forward.** All five implemented validators pass. The three self-test suites
pass: 60 deliberate layer-model breaks all refused, 48 of them by the expected
code alone; 16 ontology breaks; 6 cast defects. `tools/tests/test_gate_log.py`
passes with 12 tests. The kernel gate reports six implemented, zero failed, one
stubbed and five pending, where the stub is the retention repo scan, which is
D-001 and checks nothing.

**The four review patches were applied in sequence onto a scratch clone and all
four went in clean.** The kernel gate on the patched tree reports the identical
six implemented, zero failed, one stubbed and five pending. One line does
differ, and it is the line that should differ: `tools/validate_doctrine.py`
reports 59 criteria on the patched tree against 58 here, because patch 4 defines
EG-7 and adds its unstamped row to `doctrine/DOCTRINE_STATUS.md`. Calling the
result identical is true of the kernel-gate aggregate and false of the criterion
count, so both figures are recorded.

**One ordering trap is worth recording, because the failure it produces reads as
a stale patch set.** Running `git apply --check` on patch 2, 3 or 4 alone
against the tree at `533da17`, before patch 1 landed, reports "patch does not
apply", naming `RETENTION.md` for patch 2, `CREDENTIAL_LIFECYCLE.md` and
`HYGIENE.md` for patch 3, and `EGRESS.md` for patch 4. Patches 2 and 3 each
anchor on hunks patch 1 lands, and patch 4 anchors on a hunk an earlier patch
lands, which is the apply order the last entry recorded. Three isolated
failures are that documented ordering rather than a stale patch set. On the
tree this commit creates, with patch 1 in it, patches 2 and 3 each apply alone
and only patch 4 still fails alone, on `EGRESS.md`.

### The two defects repaired

**Defect 1, the handoff described the tree as it stood before `d99f213`.** Its
state header said the first build artifacts exist uncommitted, its section 1
paragraph said two build steps landed as untracked files, nine rows of its
section 2 table marked artifacts "Written, untracked", and two more described
already-committed files as carrying uncommitted edits. `git ls-files` lists all
nine of those artifacts, and `git show --name-status d99f213` shows that commit
adding every one of them and committing the pending edits to `AGENTS.md`, the
`Makefile`, the CI workflow and the pre-commit hook.

**The cause is structural rather than careless, which is why the repair changes
a rule rather than only the prose.** Section 8 orders a closeout as the battery,
then the records, then the commit, and the reason it gives holds: a record
written after the commit describes a tree already in the history. A handoff
written in that order therefore describes the tree as it stands while the
writing happens, which is the pre-commit tree. The order stays. What section 8
lacked is the instruction to write that record in the tense of the tree the
commit will create, and it now carries it, along with the staging step that
makes `git diff --cached --name-only` answer the question at the moment the rule
applies. Section 6's preamble gained the pointer, because it named "both process
records" in one sentence, which is the conflation the new rule breaks.

**The rule is a sentence and not yet a mechanism, which design gate 1 makes the
live question.** The mechanism that would catch this is narrow and cheap: a
lexical check on the words "untracked" and "uncommitted" scoped to the handoff
alone, in the shape of the existing em dash check, roughly six lines and a
constant with no new dependency. Its measured reach is thirteen of the fourteen
lines that were wrong at `533da17`, which means it would have refused both
`a54061b` and `d99f213`; it misses only "Neither has been committed", which no
lexical rule of reasonable size catches. The alternative of reconciling backtick
path citations against `git ls-files` was measured and rejected: it reaches
eight of the fourteen, misses the state header, which is the most misleading
line in the file, and puts a subprocess git dependency into a tool that is
currently pure filesystem. The check is not in this change for one reason worth
recording, which is ordering. Landing it before the handoff rewrite refuses the
very file being repaired, so the sentence and the rewrite go first and the check
follows as its own Class C change with a test that fails when the constraint is
removed.

**Defect 2 is this entry.** Nothing else repairs it, because a process record is
added to and never restyled, so the 2026-09-03 entry keeps its closing line
saying no commit was made. That line was true when it was written.

### A sweep for the same staleness elsewhere, repaired on instruction

The sweep returned 52 candidates across 25 tracked files. Every candidate acted
on was re-derived against the tree first. What it found outside the two
records was first recorded and left alone, and the operator then instructed
the repair, so this section records both what was found and what was done.

**All five doctrine files still say NOT YET COMMITTED in their status headers**,
eight days after `5d53973` and `a54061b` landed them, and `doctrine/EGRESS.md`
and `doctrine/CREDENTIAL_LIFECYCLE.md` each state that nothing in them is in
force until the operator commits it, which a reader takes to mean rank 1 does
not bind. That half was drafted as patch 1, which the review classes A on the
ground that every change in it is a fact correction. It is applied in this
change, whole, after each of its eighteen hunks was read and classed by effect
rather than by the review's label. Fourteen are header, citation or count
corrections. Two reword a mechanism description without moving its
obligation. One adds an enforcement-state paragraph to SS-14 item 6, the
NEVER list, and was itself stale when drafted, naming five preflight commands
where the target ran seven and omitting the ontology validator and the
telemetry test; it is corrected in place. The one hunk to name is the EGRESS
environment table, where LOCAL's reach changes from "Nothing outside
itself", which git, pip and CI already falsified, to "No third-party
platform through a connector". Nothing that refused now permits, because
EG-6 and the Execution Limits are the refusals and the row is descriptive,
and it is named because gate 2 says a rank-1 change about reach rarely looks
like one. Patches 2 through 4 were re-verified to apply in order on top of
the corrected tree.

**`README.md` said nothing is built and nothing is committed yet**, and its
next-action section still described this repository's first commit as
pending. It now states what `d99f213` landed, names the operator's four
decisions and then Step 7 as the next action, and lists the changelog among
the background reading. **`CONFORMANCE.md` reported five implemented checks
and six pending** where the gate reports six and five, listed the ontology
check among the pending, and said in its rung 3 row and its naming-gap
paragraph that `tools/validate_ontology.py` did not exist. It was written
inside `d99f213`, before the ontology entry flipped in that same commit. All
of it is corrected; the rung 3 row now says the tool exists with its
`--corpus` mode deferred until a corpus does, which keeps "four of the five
rungs cannot run" true for a different reason.

**Two mechanism comments are false, one in each direction.** The `Makefile` says
preflight is deliberately the same set the hook runs, and the hook says it runs
the same battery as preflight. Preflight runs seven commands and the hook runs
six. The telemetry test suite is the difference, and CI runs it as a step of its
own. Both comments are corrected to state the difference. Adding the test to
the hook changes a mechanism, so that choice is left with the operator and
recorded in the handoff's known gaps.

### Agent involvement, stated precisely

`CLAUDE.md` section 5 puts the honesty about how the work was done here rather
than in a commit trailer. Twenty-seven subagents ran, in two passes. The first
pass was fourteen: one recon pass that read the validator source and returned
the gate constraints every draft had to satisfy, one staleness sweep, one
drafting pass for each of the four drafted texts, which were the `AGENTS.md`
section 8 rule, the changelog entry, this entry and the handoff repair, and
two verifiers per draft whose standing instruction was to refute and to
default to refused when uncertain. The verifier pass earned its cost. It caught three blockers, and two
of them were factual errors the parent session had itself stated: the count of
prior failures was three commits rather than two, and the number of artifacts
marked untracked was nine rather than eight. It also caught a reconciliation
command that returns nothing at the moment the rule tells a maintainer to run
it, which is how the staging step got into the rule.

No subagent wrote to the tree. Each returned text and the parent session applied
it, which kept one reviewer in front of every edit. The battery figures above
were run by the parent session against the working tree. The second half of
the session, patch 1 and the four files after it, was applied by the parent
session directly, each hunk read before it landed.

**The second pass ran over the whole staged change before the commit**: seven
lenses, class by effect, facts in the records, facts in the worklog, facts in
the tree, voice and lane, cross-file consistency, and completeness, with one
refuter behind each lens that raised anything above minor. Six refuters ran,
for thirteen agents. Forty-two findings were raised, twenty-two of them above
minor; the refuters confirmed sixteen, downgraded six, and refuted none. That
rate is the opposite of the two doctrine reviews, and the reason is method:
every lens here re-ran a command or re-read a file rather than reading one
criterion and arguing, so what it raised was measured.

What the second pass caught is recorded because most of it was the parent
session's own error. The corrected paragraph in patch 1 sits in SS-14 item 6,
the NEVER list, and every record in this change had called it SS-17,
following the drafting agent's rationale rather than the file. The hunk
classification summed to twenty against eighteen hunks. The records said the
stale paragraph named four preflight commands, and it named five. The
authorization schema that patch 2 unblocks is Step 8, not Step 7, an error
carried from `DECISIONS.md` into `README.md` and the handoff. `AGENTS.md`
section 5 still said preflight and the hook run the same battery, the
`Makefile` header still named the ontology gate as pending,
`.github/workflows/ci.yml` still said two gates were the whole battery,
`CONFORMANCE.md` section 2 still said Step 7 was blocked on Steps 5 and 6 and
described subdirectories a clone does not have, `doctrine/DOCTRINE_STATUS.md`
still marked `spec/layer-model.yaml` as to be written, and
`docs/THE-GAMEPLAN.md` still marked Step 7 BLOCKED. Two handoff sentences and
this entry's heading were in the wrong tense, two records used "in one
breath" where "in one sentence" is the checkable statement, one answer was a
one-word fragment, and HYGIENE.md's rewording of the docstring claim
overstated what the validator does. All of it is corrected in this change.

The review directory's `DECISIONS.md` was amended this session, dated
2026-09-04, to record that patch 1 landed and that its apply sequence now
starts at patch 2. That file is outside the tree, so this line is the tracked
record of the edit.

**Refused this session:** nothing collected, no connector executed, no platform
touched, no doctrine criterion amended or stamped, no Class F change proposed.

**Not done:** patches 2 through 4 are still unapplied and the operator decides
patch 4. The hook still does not run the telemetry test, and the handoff tense
check is still a sentence. `doctrine/RETENTION_LEDGER.md` and
`doctrine/DISCLOSURE.md` are still owed, the D-001 repo scan is still a stub,
and every basis stamp is still unstamped.
