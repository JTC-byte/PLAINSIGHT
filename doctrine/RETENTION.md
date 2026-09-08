# Retention doctrine: what is held, in what form, for how long, and how deletion is proved

**Status: DRAFTED 2026-08-26. ALL CONCLUSIONS RECORDED. Landed in commits `1abb354` and `4c5cd25` on 2026-08-27.**

The operator decided R1, R2, R3 and R5 on 2026-08-26, setting the case ceiling
at 60 days with a logged freeze as the only path past it, and recorded a
conclusion on every remaining criterion on 2026-08-27. Four were put
individually because they encode a choice rather than a mechanism: RT-6's
incidental TTL, RT-11's blast radius, RT-14 with RT-18, and the consent shape in
`SUBJECT_SELECTION.md`. **Every basis is unstamped**, deliberately.

**Landed 2026-08-27 in commit `1abb354`; RT-19 landed the same day in
`4c5cd25`.** Per R6 as amended, an agent may execute a commit the operator has
instructed; the authorship stays theirs.

Every criterion carries its own marker. One partially stamped item does not
stamp the file. Conclusion is ratified separately from basis.

`runner/retention_sweep.py` and `tools/validate_retention.py` read
`doctrine/DOCTRINE_STATUS.md`, not this file. An unstamped criterion refuses
rather than permits, which for a retention mechanism means the sweep refuses to
run rather than running with an unratified TTL.

This document is rank 1 alongside `SUBJECT_SELECTION.md` and is authoritative
on what is retained, for how long, and what leaves the machine. It has no
opinion on schema shape. Where it names a column or a table it is naming an
enforcement point, not specifying a data model.

**Several decisions here must be made before the first blob is written.**
Unencrypted blobs cannot be retroactively crypto-shredded, and plaintext values
in a durable table cannot be un-sampled from Postgres column statistics after
the rows are deleted. That is the whole reason this document is drafted at Step
3 rather than at Step 8.

---

## 1. The governing principle, and where it differs from the precedent

`ZMeta/zmeta-field-capture/RETENTION.md` states it well and it transfers:
**retention follows purpose. No qualifying purpose, no object.** The discipline
lives at the entrance rather than the exit, and the question is never when to
delete an artifact but whether the artifact had a reason to exist.

One thing differs, and it changes the default.

In field capture, the scarce resource is the honesty of the archive. Storage is
free at that scale, so permanence is free, and tiers 2 through 4 are kept
forever. Here the scarce resource is a person's data. Permanence is not free at
any scale, because the cost is not measured in bytes. **The direction of the
default therefore inverts: field capture defaults to keeping and deletes on
decision; PLAINSIGHT defaults to deleting and keeps on decision.**

The precedent also demonstrates why this has to be a mechanism. `RETENTION.md`
line 74 in that repository commits to a default expiry of 30 days from the
pull. Nothing in the codebase reads a pull date or deletes a pull directory. On
2026-08-26, roughly 365 MB of retained capture was sitting in `pulled/` at day
11. On day 31 nothing will happen. That is not a criticism of a working
system; it is protocol capture rather than people, and it is harmless where it
sits. It stops being harmless when the retained object is a person, which is
the only reason it is quoted here.

**Extension is an act. Inaction is deletion.** Every rule below is arranged so
that the thing which happens when nobody does anything is the thing this
project wants.

---

## 2. Object strata

**RT-1. An object's stratum is declared at write time, never decided at delete
time.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

Seven strata rows across five numbered levels, plus telemetry. Sensitivity
decreases as durability increases, which is the same shape the field-capture
tiers have and for the same reason: the durable things are durable because they
carry no subject-derived values.

| Stratum | Contents | Subject values | Lifetime | Inside shred boundary |
|---|---|---|---|---|
| **0 Raw capture** | Response bytes, page captures, connector stdout and stderr, cassettes captured against a live subject | Yes, verbatim | Case TTL | Yes |
| **1 Case material** | Items, extracts, claims, inferences, message rows, dispositions, notes, the full-text index, DRAFT exports, Return Briefs | Yes, derived | Case TTL | Yes |
| **1 Authorization** | The per-case subject authorization record and every evidence object it points at, including the S1 consent record | Yes, verbatim, plus a named person | Case TTL | Yes |
| **2 Skeleton** | Run, item, and claim structure: opaque ids, timestamps, connector at version, argv template with values redacted, exit codes, counts, coverage intervals, `egress`, the ledger row, the tombstone | No | Permanent | No |
| **3 Findings** | Capability findings, scorecards with persona age and truth-file hash, connector health history, the RT-13 finding-check stamp | No, or synthetic only | Permanent | No |
| **4 Synthetic corpus** | The cast, `GROUND_TRUTH.yaml`, cassettes captured against S2, conformance fixtures | Synthetic only | Permanent, in git | No |
| **T Gate telemetry** | One record per gate run: timestamp, gate, outcome, violation code, location | **None, by construction** | 90 days rolling | No, and untracked |

**The authorization record is stratum 1, and getting this wrong would have been
the expensive kind of mistake.** It is the one object in the system that
necessarily carries both a live selector and a named person: an S1 consent
record names who consented. A draft of this table gave it no stratum at all,
which meant the object with the highest concentration of subject data had no
store, no TTL, and no shred path, in a document whose other criteria forbid
committing it to the repository. It lives inside the case boundary under the
case key, and it dies with the case. It is never in the repository, and
`conformance/gate/*.jsonl` holds synthetic records only.

**One consequence worth stating, because two criteria appear to collide over
it.** A cassette captured against a live S0 or S1 subject is stratum 0 and dies
with the case. RT-16 requires a pinned connector version's cassette to survive
as long as its case can be reopened. Those two are only compatible for a
cassette that is not stratum 0, which is the same conclusion RT-15 reaches from
the git side: **cassettes are captured against S2 or N0 targets, where they are
stratum 4 and permanent.** A live-subject cassette is not a thing this system
keeps, so it cannot satisfy RT-16 and must not be relied on to. The two criteria
do not conflict; they jointly forbid one artifact.

**Stratum 2 is what makes the posture coherent.** After a shred, the record
that an experiment happened, which connectors ran, how long they took, what
they returned in count, and what the analyst concluded remains auditable, while
the material it ran on no longer exists. Both sentences are true at once, and
neither is true without this stratum.

The skeleton renders the shred as its consequence rather than as a state token,
in the design's existing hatch channel:

```
▨ case material shredded 2026-11-04 · purpose served · 41 blobs · receipt 9f2c…a081
```

**RT-2. A stratum-2 or stratum-3 object containing a subject-derived value is a
defect, not a judgment call.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

`tools/validate_retention.py --policy` refuses a policy file that assigns a
subject-carrying field to a surviving stratum. The five-stratum table is
compiled into `policy/retention.yaml` and the validator reads the compiled
form, not this prose.

---

## 3. R1: what a shred destroys

**RT-3. The shred unit is both layers: enumerable deletion and key
destruction.**
*[Conclusion recorded 2026-08-26 by the operator, via R1. Basis: unstamped.]*
*Corresponds to R1.*

Two mechanisms, because neither one is sufficient.

1. **`DROP SCHEMA case_<id> CASCADE`** for everything enumerable: stratum-1
   tables, the message partitions, the case's full-text index.
2. **Destruction of the per-case data key** for everything not enumerable:
   object-store replicas, filesystem snapshots, WAL segments, base backups,
   page cache.

`DROP` reaches what can be enumerated. Cryptography reaches what cannot.
Backups are the canonical thing that cannot be enumerated, which is why a
retention doctrine resting only on `DROP` is a doctrine that has not thought
about backups.

**RT-4. Every blob is encrypted with a per-case data key from the first write.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*
*Corresponds to D4.*

Case keys are wrapped by a vault key. Deleting one case key renders every blob
for that case unreadable in a single atomic act, regardless of replicas,
snapshots, or caches, all of which defeat `rm`.

`zmeta-field-capture/RETENTION.md` names the same property as its worst risk:
losing the evidence key makes every stored specimen permanently unreadable.
**One key per case converts that liability into the deletion mechanism.** It is
the only way "deleted" is verifiable for data whose copies cannot all be
enumerated.

This is the criterion that cannot be retrofitted. A blob written in plaintext
in week 2 is outside this mechanism forever.

---

## 4. R2 and R3: how long, and what is inside the boundary

**RT-5. Default case TTL is 30 days. Extensions are 30 days. The hard ceiling
is 60 days.**
*[Conclusion recorded 2026-08-26 by the operator, via R2. Basis: unstamped.]*
*Corresponds to R2. The operator set the ceiling at 60 rather than the drafted
180, on the reasoning that validating a capability should not take six months.*

`retain_until` is a column, not a convention. The sweep acts on it.

An extension carries an author, a timestamp, and a reason, which is the same
shape `PLAINSIGHT-design.md` §5.5 already requires for a cluster assertion.
Extension is an analyst act recorded in the audit log. Absence of that act is
deletion.

At 60 days the case does not extend. It closes, shreds, and is re-authorized
from a new purpose record if the work continues. A ceiling that can be extended
is not a ceiling, and the re-authorization is cheap precisely because the
purpose record is one sentence. The single exception is a logged freeze under
RT-17, which is the operator's deliberate manual hold and is the only thing that
crosses this line.

**RT-6. Incidental content expires at the shorter of the case TTL and the
incidental TTL, and a case extension does not extend it.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*
*Enforces `SUBJECT_SELECTION.md` SS-11.*

Bystander data must not inherit extensions granted for reasons that have
nothing to do with the bystander. Default incidental TTL at v0.1 is 7 days,
**enforced at the next sweep, which is why the sweep runs daily.** A weekly
sweep against a 7 day TTL means the ratified number is 7 and the enforced number
is anywhere from 7 to 14, and doubling the life of the one class whose entire
purpose is a shorter life is not a rounding error.
`conformance/retention/` carries a case asserting that incidental content is
gone within 24 hours of its TTL.

This is a flat rule at v0.1 rather than differential machinery. The
differential version is deferred to v0.2, and the trigger for un-deferring it
is the first case where the flat rule destroys something the analyst needed,
which is a real cost and is accepted here deliberately.

**RT-7. The full-text index is inside the shred boundary.**
*[Conclusion recorded 2026-08-26 by the operator, via R3. Basis: unstamped.]*
*Corresponds to R3. The cost below was stated in the decision and accepted.*

An FTS index over message bodies is a plaintext copy of those bodies with a
different access pattern. An index that survives a shred is a searchable
archive of the case that was just deleted.

**This costs real performance and real design work in STREAM, and the cost
belongs in the decision rather than in a footnote.** A per-case index cannot be
shared across cases, cannot be warmed once, and is rebuilt rather than
incrementally maintained across the case boundary. The alternative is a
surviving index, and there is no third option that is honest.

**RT-8. R5 resolves as: `text: forever` is legal as a within-case blob policy
and illegal as a case-level value.**
*[Conclusion recorded 2026-08-26 by the operator, via R5. Basis: unstamped.]*
*Corresponds to R5. Resolves a live conflict.*

`PLAINSIGHT-design.md` §5.7 sets `retain: {text: forever, media: 90d}`. That
document is rank 7 and does not set a retention rule, so the conflict resolves
here or the storage layer holds two contradictory instructions.

The resolution: within a case, text blobs are kept for the life of the case and
media expires at 90 days, which is the design's real intent and preserves the
lineage promise for the period the case exists. `forever` is scoped by
`retain_until`, never above it. A text blob does not outlive its case.

**The 90 day figure is inherited and under RT-5 it can almost never fire.** It
comes from `PLAINSIGHT-design.md`, written before the operator set the ceiling at
60 rather than the drafted 180, so on an ordinary case media dies with the case
and the media clock is the case clock. The number is kept rather than retired
because it is the correct behaviour for the one case that reaches past 60 days,
which is an RT-17 freeze, and a media blob under a freeze is the one place the
distinction is real. An implementer configuring from this line should know it is
a ceiling that the case ceiling almost always beats, which is the unfalsifiable
check `HYGIENE.md` HY-2 exists to catch.

The design's own reasoning survives intact. A `retain_raw: 90d` that silently
voids the lineage promise is worse than an honest tombstone, and the tombstone
is what the skeleton renders.

**Action required on stamping, narrowed after checking the actual lines.**
`PLAINSIGHT-design.md:747` is a `lineage:` field inside a connector manifest
example, so it is a per-connector blob policy and is already the legal form
under this criterion. It needs no edit. The conflict is the prose claim in §5.7
at `:648`, which states flatly that text blobs are retained forever with no
scoping to a case. That line is corrected in the same change that stamps RT-8,
with the correction logged in the worklog, because leaving rank 7 contradicting
rank 1 is how the contradiction gets found by an implementer instead of by a
reviewer.

---

## 5. Proving the shred happened

**RT-9. Verification runs outside the tool that performed the shred, and
comprises five checks.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

`runner/verify_shred.py` is a separate program from `runner/retention_sweep.py`
for the same reason the field-capture restore path is part of the doctrine
rather than a convenience: a vault nobody has restored from is an assumption.

| # | Check | Passes when |
|---|---|---|
| 1 | Decrypt attempt on a witness ciphertext for the case, held outside the enumerable delete path | The decrypt **fails on the key**. Not-found, permission-denied, or malformed-input is a verification **failure**, not a pass |
| 2 | Absence over the S3 endpoint | The objects are gone, read through the S3 API, never a cached path |
| 3 | Schema absence | A query against any stratum-1 table for the case errors, rather than returning zero rows |
| 4 | Skeleton presence | Stratum 2 is intact and carries the tombstone and the receipt hash |
| 5 | Anti-overreach | An adjacent canary case is still fully readable and its blob count is unchanged |

Three of these are written the way they are because of a measured incident in
the precedent, recorded in `zmeta-field-capture/RETENTION.md`. During the
2026-08-17 setup, a synthetic test object appeared to survive repeated deletes
that each reported success. Every delete had worked. The Cloudflare API read
path used by `wrangler r2 object get` serves cached responses, first read of a
key wins, demonstrated on a fresh key: write 18 bytes, read 18; write 34 bytes
over it, read 18 again; delete, read 18 again.

Two rules follow and both are load-bearing here.

- **Never confirm a deletion with a cached read path**, and never with a
  DELETE's exit code. Check 2 uses the S3 endpoint specifically.
- **A check that can pass for a reason other than the one claimed is not a
  check.** Check 1 requires a failure and treats a success as the alarm. Check
  3 distinguishes "the table is gone" from "the table returned nothing", which
  are different facts that look identical in a result set.

**Check 1 needs the witness, and a draft of it violated the rule it sits three
lines above.** That draft read "decrypt attempt on a known stratum-0 blob for the
case". Check 2 requires exactly that blob to be gone, so the two checks demanded
contradictory states of one object, and check 1 would have passed on
`NoSuchKey` while reporting that the key had been destroyed. That is the failure
mode this criterion exists to catch, reached inside the criterion itself. The
witness is one ciphertext per case, designated at first write and held outside
the enumerable delete path, so that after the shred there is still something to
try the key against. Its designation, its recorded digest, and the per-case
inventory are mechanics for
`conformance/retention/shred-roundtrip.yaml`, not for this document.

Check 5 exists because the failure mode of an over-eager shred is silent. A
sweep with a bad case-id filter that destroys two cases reports one success.

**RT-10. A shred with no receipt row did not happen.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

`doctrine/RETENTION_LEDGER.md` is the case registry and carries one row per
case: opaque case id, subject class, purpose, `retain_until`, current state,
and the receipt hash once shredded. It carries no subject-derived value, so it
is stratum 2 and survives.

**The reconcile is a named job, not a cadence bullet.** `runner/reconcile_ledger.py`
runs on a schedule and diffs in both directions. A case in the ledger with no
corresponding storage, and storage with no corresponding ledger row, are both
findings. One-directional reconciliation finds only the first.

The shape being transferred is `zmeta-field-capture/reconcile_evidence.py`,
including its docstring as the standard: the schedule rests on something that
runs rather than on someone remembering what to compare. It gets RT-12's
treatment as well, meaning it writes a heartbeat on every run including runs
that find nothing, and the absence of that heartbeat is a rendered degraded
state rather than a silence.

Stamping RT-10 therefore requires the `docs/THE-GAMEPLAN.md` §2.1 register row
and the job itself to land in the same change, per the documentation matrix in
`AGENTS.md` §6. `AGENTS.md` §4 already forbids an agent editing a scheduled
reconcile, which is a limit on a job that does not exist yet.

**RT-11. `SHRED_FAILED` on any case blocks all new runs system-wide.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

A retention mechanism that can fail without stopping collection will be found
to have been broken for six months. The block is system-wide rather than
per-case, because a shred failure is evidence about the mechanism, not about
the case.

**The halt clears one way: `verify_shred` passes all five RT-9 checks for the
failed case.** Clearing is a logged act carrying an author, a timestamp, and the
receipt hash, written to `RETENTION_LEDGER.md` as that case's current state.

A halt with no documented way out is not a stronger control than one with a
documented way out. It is a weaker one, because this program's ladder terminates
in one person and SS-15 states the consequence: a control whose bypass is
undocumented gets bypassed silently, and a control whose bypass is a dated entry
gets bypassed visibly. An undismissable stop with no exit produces the first.

If the shred genuinely cannot be completed, the override is an entry in
`RETENTION_LEDGER.md` naming the case, the author, the date, and the reason, and
it renders in the case header as its consequence until resolved, in the same
channel as the RT-12 and RT-17 renders. It does not go in `DOCTRINE_STATUS.md`.
That file is the ratification pin for doctrine items, and a case-level
operational override entered there would be the lane escape `CLAUDE.md` §2
warns about.

Roughly forty lines and one integration test.

**RT-12. Absence of the sweep's heartbeat is a named degraded state, rendered,
not a silence.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

The sweep writes a heartbeat on every run, including runs that delete nothing.
A missing heartbeat renders in the case header as its consequence:

```
▨ RETENTION SWEEP HAS NOT RUN SINCE 2026-10-02 · retain_until is not being enforced
```

This follows `../ZISR COP/docs/OPERATIONAL_CONTRACT.md` §4, lines 315 to 316,
which prohibits "inferring 'link is fine' from absence of a failure signal
rather than an active freshness check". That file sits in a sibling repository
this one reads from and never writes to, per `README.md`, and the same section's
item 5 carries the rule this tombstone implements: a retention boundary presents
as an explicit "not available before X", never as a silent gap. The sweep is scheduled from day
one, while it still has nothing to delete. A scheduled job that does nothing
yet is a mechanism. A comment describing a future job is not.

---

## 6. What survives, and the one case where a finding is PII

**RT-13. A finding is checked against the case's selector set before the shred,
never after.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

Three classes of post-shred artifact. The third is where the pressure will be.

| Artifact | Carries subject values | Survives |
|---|---|---|
| Capability finding: a connector returns a recovery hint for a linked account rather than the owner, measured across six synthetic accounts, four of six resolving elsewhere | No | Yes. This is the entire point of the program |
| Scorecard: precision and recall against the cast, with persona age and truth-file hash | Synthetic only | Yes, and it carries its conditions |
| Case narrative: a specific person linked to a specific second account by a specific shared selector | Yes | No |

The case narrative is the most compelling demonstration artifact this program
will produce, which is exactly why it needs a named rule rather than a judgment
call made by whoever is preparing the demo.

`tools/validate_retention.py --finding <file> --case <id>` scans a candidate
writeup against the case's selector set and refuses on a match. **It runs at
case close, before the shred, while the values still exist.** Its output is a
stamp recording that it passed, and that stamp is stratum 3.

> **[REJECTED READING, DO NOT RE-DERIVE IT]** Retain a salted HMAC of the
> case's selector set after the shred so the finding check can run later. A
> surviving HMAC key plus a surviving digest set is a membership oracle: anyone
> holding both can test a candidate selector for membership and get a yes or a
> no. That is a re-identification channel built into the deletion evidence.
> Running the check before the shred needs no retained digest at all, so the
> oracle never exists. Rejected 2026-08-26.

**RT-14. Screen recordings, screenshots, and exported briefs from a
non-synthetic case do not leave the case boundary.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

These sit in a downloads folder: outside the database, outside the sweep,
outside the shred, and outside every mechanism above. There is no technical
control available, so the rule is stated and the alternative is provided:
**demos are built on the cast.** A demo on the cast is also a better demo,
because the ground truth is known and the narrator can say whether the system
was right.

DRAFT and Return Brief exports are stratum 1. They are written inside the case
boundary where the sweep reaches them, or they are not written.

**RT-19. Gate telemetry is retained for 90 days rolling, is untracked, and
carries no subject-derived value by construction.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

The operator asked for gate firings and gate failures to be recorded so that
keeping, improving or retiring a check becomes an adjudicated decision rather
than a remembered impression. `doctrine/HYGIENE.md` owns the adjudication. This
criterion owns the lifetime, because a log is an object and every object here has
one.

Stratum **T**, which sits outside the numbered strata deliberately. It is not
case material, so it is not inside the shred boundary. It is not a finding, so it
is not permanent. It is telemetry, and telemetry that is kept forever has become
an archive of how the tools behaved in 2026, which nobody will read and which
grows without bound.

**Ninety days rolling**, swept on every write and on every read rather than by
a scheduled job, because the writer and the reader are already running and a
separate schedule would be a third thing that can fail silently. The read-side
sweep is not decoration: a write-only sweep leaves an idle repository holding
records past the TTL and rendering them in the summary, which inverts the rule it
was chosen to serve. Inaction is deletion once something runs, and for this
stratum nothing runs unless a gate does.

**Untracked, and that is a decision rather than an oversight.** A telemetry file
in git is permanent, which contradicts the TTL in the one direction that cannot
be undone. `.gitignore` carries `.gate-log/` and RT-15's repo scan would refuse
it anyway.

**The rule that makes this safe is HY-1 and it is worth restating here.** A
telemetry record names the file and the line. It never names the string that
matched. A `--repo-scan` refusal fires because a selector-shaped value was found
in a tracked file, and a record quoting that value would take the gate's own
evidence and make it the durable surface the gate exists to prevent. Two things
hold it: the allowed field list in `tools/gate_log.py` is a fixed tuple and an
unknown keyword is discarded rather than raised, so widening the record requires
editing that tuple; and the location is checked against a shape, so a caller
passing a matched value writes a redaction and the refusal is still counted.
`tools/tests/test_gate_log.py` breaks both and asserts the refusal.

**RT-18. A disclosure export is the one path by which a whole non-synthetic case
leaves the machine. It exists only under an active freeze.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

The operator's case: a run surfaces something a reasonable person would report,
and the material has to reach law enforcement or another appropriate agency. The
freeze in RT-17 already stops the shred for exactly that situation. This
criterion is what allows the material to actually go.

Six conditions, and the first one carries the weight:

1. **An RT-17 freeze is active on the case.** A disclosure export is not
   available on an ordinary case. Binding the two together is what stops this
   from becoming a general-purpose export with a serious-sounding name, and it
   means every disclosure inherits the freeze's requirement to name the
   obligation it serves.
2. **It exports the complete case**, not a projection and not a summary.
3. **It is a logged act** carrying an author, a date, the receiving agency or
   process named, and the obligation from the freeze.
4. **It is recorded in `RETENTION_LEDGER.md`** against the case, so the question
   "did anything ever leave" has an answer that is not a memory.
5. **Once it leaves it is outside every mechanism in this document, permanently.**
   The shred does not reach it, the sweep does not reach it, and no revocation
   reaches it. The export interface says this at the moment of export rather
   than in a footnote.
6. **It does not alter the freeze or the shred path.** The case still shreds when
   the freeze lapses. Handing the material to the process it belongs to is the
   reason the copy exists; it is not a reason to keep ours.

**This is the one place in the system where data minimization is deliberately
inverted, and that is worth stating plainly rather than leaving as a
special case.** Design gate 7 says every projection is lossy and one-directional,
and the export boundary normally enforces citation completeness and
minimization together. A disclosure export enforces completeness and refuses to
minimize. Handing an agency a thinned subset of the evidence misrepresents what
was found, and choosing which parts of it they see is not a decision this
project is positioned to make. Completeness is the correct behaviour here and
this is the only place that is true.

**A deferral trigger has fired.** `docs/THE-GAMEPLAN.md` §2.2 defers
`doctrine/DISCLOSURE.md`, standing in with a section inside this file, until a
second egress path exists. RT-18 is that second path. The section above stands
in the meantime, and `DISCLOSURE.md` is now owed rather than deferred.

---

## 7. The repository is an unshreddable surface

**RT-15. No object containing a live selector is committed, and the check runs
before the commit rather than after.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

Per-case crypto-shred is the right mechanism for the blob store and it does not
reach git. Git history is append-only, distributed to every clone, and survives
`git rm`. Four routine acts defeat the entire retention mechanism: committing a
cassette captured against a real subject, pasting a stack trace containing a
selector into an issue, screenshotting a dossier into a design document, and
writing a case subject's handle into a worklog entry.

This is sharper than it first appears. `PLAINSIGHT-design.md` §6.3 makes
cassettes mandatory day-one CI infrastructure, because live platforms cannot be
hit in CI and without replay no connector change can ever be tested. A cassette
is a verbatim, durable, committed copy of a platform's response about a person.
**The one artifact class this doctrine structurally cannot destroy is exactly
the artifact class the test harness requires to be permanent.**

The consequence is a build-order fact rather than a caution: subject selection
is the precondition for having a test harness at all. Cassettes are captured
against S2 subjects, which is why the cast is Step 4 and not Step 12.

Enforcement, all four parts required:

- An Execution Limits clause in `AGENTS.md`. Present as of Wave 0.
- `canary_subject_class` as a required connector manifest field, with values
  `synthetic | institutional`. A manifest missing it is refused.

  **`consented` is deliberately not in that enum, and the source list it was
  inherited from had it.** A canary declaration carries its target selector, and
  a manifest is a tracked file, so a consented person's selector in a canary is
  permanent in git and outside every mechanism in this document. Consent cannot
  authorize that, because the subject cannot revoke it afterwards and neither
  can we. If a consented canary is ever genuinely needed, the only legal shape
  is an indirection: a canary target id resolved at run time from an untracked
  file. That is a separate ratified item and not a value in this enum.

  `institutional` means an account that is not a natural person, matching N0 in
  `SUBJECT_SELECTION.md` SS-1, so the enum cannot be used to relabel a person's
  account as infrastructure.
- Violation code `FIXTURE_CONTAINS_LIVE_SELECTOR` in
  `policy/violation-codes.yaml`.
- `tools/validate_retention.py --repo-scan` wired into `.githooks/pre-commit`.
  **Wired as of Wave 0 and currently a stub that checks nothing**, tracked as
  D-001 and implemented at Step 8. The gap is known rather than silent, and the
  stub says so on every commit.

The real implementation must distinguish a synthetic cast selector from a live
one, or it will refuse every commit that touches the design documents, which
already carry the fictional cast: `docs/PLAINSIGHT-design.md` renders an
obfuscated address and a platform uid inside its own worked examples, and
`docs/THE-GAMEPLAN.md` §5.4 quotes a case narrative in the same shape.
`synthetic/CAST.md` is therefore an input to `--repo-scan` and not only to the
scorer.

That is an inference from the files as they stand, not a report of a scan. No
sweep has been run against this tree, because the only tool that would run one
is the D-001 stub.

**RT-16. A connector version's manifest, cassette, and adapter are not
deletable while any case pinned to that version can be reopened.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

`PLAINSIGHT-design.md` §6.4 keeps exactly one governance item, per-case version
pinning, so reopening a case renders the connector version and whether it has
been superseded. That guarantee requires the artifacts for the pinned version
to still exist. This is a retention floor rather than a retention ceiling,
which makes it the only rule here that forbids a deletion act. It carries no
subject values, so it costs nothing against the posture.

Enforcement, in RT-15's shape:

- A Class C clause in `AGENTS.md` stating that a connector version's manifest,
  cassette, and adapter are not deletable while any case pinned to that version
  can be reopened. **Not present as of Wave 0.**
- A bidirectional check in `tools/validate_retention.py` reconciling the pinned
  versions in `RETENTION_LEDGER.md` against the contents of `connectors/<id>/`.
  A pinned version with missing artifacts, and an artifact set with no pinning
  case, are both findings.
- A violation code in `policy/violation-codes.yaml`. **`policy/` is empty as of
  Wave 0.**

The clause is one sentence and the check is small. Both are named here so that
RT-16 is not the one criterion in this document that states a rule and stops,
which is what a previous draft of it did.

---

## 8. The freeze, and its expiry

**RT-17. A freeze stops the run, stops the sweep for one case, notifies the
operator, and collects nothing further. It has its own expiry, and it is the
only thing that crosses RT-5's ceiling.**
*[Conclusion recorded 2026-08-26 by the operator. Basis: unstamped.]*

If a run surfaces something a reasonable person would report, two rules the
operator holds at once collide: the automatic shred destroys the material, and
the material is the thing that would be reported. Neither rule yields quietly,
so the path is defined here rather than improvised at the moment.

The freeze is narrow:

1. The run stops. No further collection on that case, including pivots already
   queued.
2. The case enters the frozen state in `RETENTION_LEDGER.md`, and the sweep
   skips cases in that state. `retain_until` is a stored date and does not
   advance or stop advancing; what changes is that the sweep declines to act on
   it, and the ledger row carries the freeze expiry.
3. The operator is notified. The freeze is an explicit logged act with an
   author, a timestamp, and a reason.
4. **The freeze carries its own expiry**, default 30 days, and on expiry it
   either is renewed as a new logged act or the case shreds on the normal path.
5. **A freeze is the one thing that crosses RT-5's ceiling.** The 60 day ceiling
   is absolute for every ordinary case. A logged freeze suspends the shred past
   it, because the obligation that triggered the freeze is not on the operator's
   timetable.
6. **Each renewal names the external obligation it serves and an expected
   resolution date.** A renewal carrying neither is refused. This is what
   separates a freeze from a habit.
7. **The second renewal renders a distinct escalated state**, not the same
   FROZEN line a third time. A state that looks identical on day 30 and day 90
   stops being read.

Points 4 through 7 are the criterion, and point 4 alone is not enough. A draft of
this section had only point 4: an expiring freeze that renews without limit is
the same loophole as a freeze with no expiry, reached one logged act at a time.

**Point 5 is the operator's decision and it is the one place this doctrine
permits an indefinite hold, so points 6 and 7 carry the whole weight.** The
freeze exists for the case the operator described: a run surfaces something a
reasonable person would report, and the automatic shred would destroy the
material that has to be reported. Capping the freeze at the ordinary ceiling
would mean the handoff has to complete inside 60 days, which is not a timetable
this project controls.

What stops that from becoming an archive is not a cap. It is that every renewal
has to name an obligation and an expected resolution date, and that the state
escalates rather than repeating. A freeze nobody can name a reason for expires,
and a freeze that has been renewed twice stops looking like an ordinary case on
the screen.

Enforcement sits where the TTL is enforced. `runner/retention_sweep.py` skips
cases in the frozen state, refuses a renewal that carries no obligation and no
expected resolution date, and shreds on the normal path the moment a freeze
lapses. `conformance/retention/` carries a renewal with no named obligation,
asserting it is refused, and a lapsed freeze, asserting the shred proceeds.
RT-5's 60 day ceiling gets its own refusal in the same check, because a ceiling
with nothing refusing at it is a number in a table.

A frozen case is rendered as its consequence, not as its token:

```
▨ FROZEN 2026-09-14 by <ratifier> · shred suspended · freeze expires 2026-10-14
```

---

## 9. Cadence

Most maintenance is one decision taken at the right time. This mirrors the
field-capture cadence section, adapted to cases.

- **At case open:** the purpose is bound and `retain_until` is set. That
  decision is the maintenance.
- **At every extension:** an author, a timestamp, and a reason. Inaction needs
  no act, because inaction is deletion.
- **At case close:** run `--finding` before the shred, then shred, then
  `verify_shred`, then write the receipt row.
- **Daily:** the sweep runs, whether or not it has anything to do, and writes
  its heartbeat. Daily rather than weekly because RT-6's incidental TTL is 7
  days and the sweep interval is the enforcement granularity.
- **Monthly:** `runner/reconcile_ledger.py` diffs `RETENTION_LEDGER.md` against
  storage in both directions. Never through a cached read path.
- **At every doctrine change:** re-run `tools/validate_retention.py --policy`,
  because the strata table above is prose and `policy/retention.yaml` is what
  executes.

---

## 10. What is explicitly NOT gated

This section exists so the doctrine is productive rather than obstructive.

- Collecting at full depth against any authorized subject class. The retention
  rules bound how long, never how much.
- Keeping raw bytes for the life of the case. Content-addressed raw capture
  from the first run is a design invariant and this document does not weaken
  it. Stdout that was thrown away cannot be recaptured.
- Permanent retention of every capability finding, scorecard, connector health
  record, and conformance fixture, which is the program's actual product.
- Permanent retention of the skeleton, which is what makes the shred auditable
  rather than merely claimed.
- The entire synthetic corpus, permanently, in git.

---

## 11. Rejected readings, do not re-derive

> **[REJECTED READING, DO NOT RE-DERIVE IT]** A salted HMAC of the case's
> selector set may be retained after the shred so the finding check can run
> later. Restated in full at RT-13. Rejected 2026-08-26.

> **[REJECTED READING, DO NOT RE-DERIVE IT]** Retention alone bounds the harm
> of collection. Deleting a profile does not un-collect it, and the
> platform-side record is outside every mechanism here. Subject selection is
> the upstream control, which is why it is rank 1 alongside this file rather
> than below it. Rejected 2026-08-26.

> **[REJECTED READING, DO NOT RE-DERIVE IT]** `DROP SCHEMA ... CASCADE` is
> sufficient, so per-case encryption can be deferred until the storage layer
> settles. `DROP` does not reach object-store replicas, filesystem snapshots,
> WAL segments, or base backups, and a blob written in plaintext is outside the
> mechanism permanently. The encryption decision has no later date on which it
> can be made. Rejected 2026-08-26.

---

## 12. Ratification table

Nothing below is stamped. `DOCTRINE_STATUS.md` is the pin of record; this table
is an index into it.

| Item | Subject | Must precede | Related open decision |
|---|---|---|---|
| RT-1 | Strata declared at write time | The first write | none |
| RT-2 | No subject values in a surviving stratum | `--policy` | none |
| RT-3 | Shred unit is both layers | The shred implementation | R1 |
| RT-4 | Per-case key from the first blob | **The first blob** | D4 |
| RT-5 | 30 day TTL, 30 day extensions, **60 day ceiling**. Conclusion recorded | The first case | R2 stamped |
| RT-6 | Incidental TTL, shorter, non-extendable | The first pivot | R8, SS-11 |
| RT-7 | FTS index inside the boundary | The index design | R3 |
| RT-8 | `text: forever` scoped by `retain_until` | The storage layer | R5 |
| RT-9 | Five verification checks, run outside the sweep | Any deletion claim | none |
| RT-10 | No receipt row, no shred; `runner/reconcile_ledger.py` diffs both directions | The ledger | none |
| RT-11 | `SHRED_FAILED` blocks all runs, cleared only by a passing `verify_shred` | The runner | none |
| RT-12 | Heartbeat absence is a rendered state | The sweep | none |
| RT-13 | `--finding` before the shred | The first case close | none |
| RT-14 | No exports or recordings outside the boundary | The first demo | none |
| RT-15 | No live selector in a tracked file | **Every commit** | none |
| RT-16 | Pinned connector versions are not deletable | Any case reopen | none |
| RT-17 | The freeze, with its own expiry, and the only path past the 60 day ceiling. Conclusion recorded | The first freeze | none |
| RT-18 | Disclosure export, only under an active freeze, complete rather than minimized | The first disclosure | none |
| RT-19 | Gate telemetry, 90 days rolling, untracked, no subject values | The first gate run | HY-1 |

**Four of these have a date after which they cannot be made.** RT-4 before the
first blob, RT-7 before the index is designed, RT-15 before the first commit
containing a cassette, and RT-1 before the first write. The rest can be stamped
later at a cost. These four cannot be stamped later at any cost.
