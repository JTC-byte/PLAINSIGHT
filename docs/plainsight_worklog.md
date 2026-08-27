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

