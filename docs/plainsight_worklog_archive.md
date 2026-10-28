# PLAINSIGHT worklog archive

Entries moved here from `docs/plainsight_worklog.md` when adding one would have
taken it past its cap of ten live entries, oldest first, without edit. A process record is never
restyled, and the live worklog's header states the rules both files follow,
including that neither may quote a case, a selector value, a handle, a subject
name, or a finding about a person.

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
