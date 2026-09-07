# Subject selection: who may be a subject, and what the gate returns

**Status: DRAFTED 2026-08-26. ALL CONCLUSIONS RECORDED. Landed in commits `1abb354` and `4c5cd25` on 2026-08-27.**

The operator decided R2, R3, R4, R6 and R7 on 2026-08-26 and recorded a
conclusion on every remaining criterion on 2026-08-27. **Every basis is
unstamped**, which is deliberate: the conclusions were decided in session and the
reasoning in `docs/PLAINSIGHT-FOUNDATION.md` §3 has not been reviewed.

**Landed 2026-08-27 in commit `1abb354`; SS-19 through SS-21 landed the same day
in `4c5cd25`.** Per R6 as amended, an agent may execute a commit the operator has
instructed; the authorship stays theirs.

Every criterion carries its own marker. One partially stamped item does not
stamp the file. Conclusion is ratified separately from basis, because no
mechanism should be built on a rationale the operator was never shown.

`runner/subject_guard.py` reads `doctrine/DOCTRINE_STATUS.md`, not this file.
A criterion absent from the stamp table refuses rather than permits, and
`tools/validate_authorization.py --fixtures` carries a test asserting that an
unratified criterion refuses. That test is what makes an unratified document
safe to write and unsafe to forget about.

This document is rank 1 and is authoritative on three questions: who may be a
subject, what may be collected about them, and what leaves the machine. It has
no opinion on field names, layer boundaries, or interface design. A section
here that starts adjudicating a schema question has escaped its lane and gets
cut back.

**Scope note.** Nothing in this file grants an authority the operator does not
already hold. Statutory obligations, platform terms of service, and
commitments made outside this repository sit above every rule below. A
`permitted` return from the gate means the runner will construct argv. It
means nothing else.

---

## 1. Why this document outranks the semantic contract

Two independent arguments arrive at the same place. The second one is the one
that changes behaviour.

### 1.1 Retention bounds persistence. It does not bound collection.

Deleting a profile does not un-collect it. The shred in `RETENTION.md` reaches
the blob store, the tables, the index, and the backups. It does not reach:

- The platform's own record that a session viewed a given account at a given
  second. That is a record about the subject-operator link, held by a third
  party, permanent, and outside every mechanism in this repository.
- The credential heat spent making the request.
- The bystanders the run touched on the way to its target.

An event can be schema-valid, ontology-clean, correctly layered, honestly
timed, and fully lineaged, describe a person who was never permitted to be a
subject, and pass every check at ranks 2 through 6. No validator catches it,
because no validator knows who a selector refers to. The gate that bounds the
act has to sit before the act, and the rule that defines the gate has to sit
above the rules that cannot evaluate it.

### 1.2 An identity-correlation engine cannot be validated without ground truth

PLAINSIGHT's central output is a claim of the form "these two handles are one
person." Grading that claim requires an oracle. The argument lives in one cell
of the confusion matrix.

| Cell | Meaning |
|---|---|
| TP | The system proposes A~B and they are the same person |
| FP | The system proposes A~B and they are not |
| FN | A and B are the same person and the system did not propose it |

Recall is TP / (TP + FN). **FN requires enumerating the accounts the person
actually has.** For an arbitrary third party, the accounts never found are
indistinguishable from accounts that do not exist, and no experiment separates
them. A recall figure produced against a stranger is a fabricated number. That
is the same defect class `PLAINSIGHT-design.md` CUT LIST A already removed when
it cut `precision_prior` and `evidentiary_weight` as invented numbers with no
calibration ground truth anywhere in the system.

Precision looks computable and is not. Confirming that a proposed link is
correct requires an oracle, and the analyst's own judgment is the system's
output re-entered as ground truth. That measures self-consistency. The
resulting estimate rises exactly as the analyst's confidence rises, which is
the correlation the measurement most needs to break.

Two consequences are build facts rather than cautions.

- **`attempted_and_absent` cannot be promoted from stored to rendered without
  confirmable subjects.** CUT LIST B defers it until `always_present` is
  canary-proven across the connector fleet. Proving `always_present` requires
  knowing what is actually present, which on a synthetic account is known
  because the team set the fields, and on a stranger is never known. A designed
  v1.1 feature is permanently unshippable in the stranger configuration.
- **On a stranger, a wrong value looks exactly like a right one.** D2's residue
  class is datum-unlabelled plausible values. The toutatis manifest already
  annotates the danger: the platform returns a recovery hint for a linked
  account, not necessarily the owner. Against a subject who can be asked, which
  one it was is discoverable. Against a stranger it is not, so collecting on
  strangers does not merely fail to measure. It conceals the defect class D2
  exists to prevent.

Consenting subjects, purpose-made accounts, and the operator's own accounts are
not a watered-down version of this experiment. They are the only configuration
in which precision, recall, negative-class validity, and extraction correctness
are all computable. Build the capability to full depth and run it at full depth
against subjects who can confirm the answer.

**SS-18. Every finding carries the subject class it came from, and the scorer
refuses to compute a figure across classes.**
*[Conclusion recorded 2026-08-26 by the operator. Basis: unstamped.]*

This is the consequence of 1.2 rather than a separate policy. S3 and S4 are
available, and against them recall is not computable and precision reduces to
self-consistency, so a number produced over a mixed population is not a weaker
measurement. It is a different kind of statement wearing a measurement's
clothes.

Two mechanisms, both small:

- A finding renders the class of the subject it was produced against. Not in a
  tooltip, and not two clicks away, because the mixed figure is the one that
  reaches a summary.
- The scorer refuses a scorecard whose inputs span more than one class, with a
  named violation rather than a warning. `conformance/` carries the refusal
  fixture.

This is the same rule that already removed machine-computed confidence, applied
one level up. A score is a guess in the costume most resistant to scrutiny, and
a score computed across a boundary where its meaning changes is the same guess
with a larger denominator.

---

## 2. Subject classes

**SS-1. The class set is closed at v0.1.**
*[Conclusion recorded 2026-08-26 by the operator, via R4. Basis: unstamped.]*
*Corresponds to R4, decided as maximum reach.*

A selector belongs to exactly one class per case. The class is recorded in the
authorization record, not inferred at dispatch. `policy/subject-authorization.yaml`
carries the enum and `schema/subject-authorization.schema.json` refuses a value
outside it.

| Class | Definition | v0.1 | Evidence required |
|---|---|---|---|
| **S0 SELF** | An account the operator holds and controls | Available | Credential possession, recorded once per account |
| **S1 CONSENTING** | A living person who has given recorded, revocable, per-case consent | Available | A consent record naming the person, the case purpose, the classes of data, and an expiry |
| **S2 SYNTHETIC** | A persona in `synthetic/CAST.md`, created by the team, interacting only with the cast | Available | Presence in the sealed cast manifest |
| **S3 PUBLIC FIGURE** | A person whose public role is argued to make them a legitimate subject | Available, behind SS-17 | A written statement of the public role relied on, recorded per case |
| **S4 ARBITRARY THIRD PARTY** | Anyone else | Available, behind SS-17 | A written purpose naming why this person, recorded per case |
| **S5 INCIDENTAL** | A person whose data arrives as a byproduct of collecting on any authorized node, person or organization or location | Available, never as a target | Not authorizable. See section 5 |
| **N0 NON-PERSON** | A selector that does not belong to a natural person: an organization, a company, an institutional or role account, a published corporate domain | Available | A written statement that the selector is institutional, recorded per case |
| **L0 LOCATION** | A place that is not a person's home: a venue, campus, office, public space, or a coordinate box | Available | A written statement that the location is not a residence, recorded per case |

**S3 and S4 are available, and the ground-truth argument in section 1.2 does not
go away because they are.** Recall is not computable against a subject whose
accounts cannot be enumerated, and precision confirmed by the analyst's own
judgment measures self-consistency. The consequence is not that these classes
are refused. It is that a result produced against them is a coverage claim
rather than a correctness claim, which SS-18 makes the system say out loud, and
that the calibration baseline comes from subjects who can confirm a link, which
SS-17 makes a gate rather than an intention.

**N0 exists because the S-classes cover only natural persons and the tools do
not.** CrossLinked's function is to enumerate an organization. A company domain
is a legitimate seed and is nobody's personal data, and with no class for it
either the class set silently forbids a capability the program wants, or an
analyst files an organization under a person class and the gate's whole meaning
degrades.

Two boundaries keep N0 from becoming the hole in the class set.

- **N0 authorizes the organization, never its members.** The output of an
  organization enumeration is a list of people, and each of those people is
  S5 INCIDENTAL on arrival and cannot become a pivot origin. Promoting one to a
  target requires that person's own authorization record under S0, S1, or S2.
  `conformance/gate/` carries the refusal fixture for an N0-derived selector
  used as a seed.
- **N0 is not self-certifying.** "This is institutional" is a written statement
  in the authorization record, recorded by a person, on the SS-1 rule that the
  gate reads a class rather than inferring one. A role account named for a
  person is a natural person's selector wearing an institutional label, and the
  written statement is what makes that call reviewable.

**L0 has one carve-out that does most of the work.** A residential address tied
to an individual is that person's selector and inherits their class. It is not
an L0 node. Without that line, the location class would be the route by which a
home address becomes infrastructure and stops being personal data, which is the
one thing a location class must not do. A coordinate box drawn on a map is L0. A
house inside it is not.

**The gate does not decide which class a selector belongs to.** It reads the
class from the authorization record and refuses when no record covers the
selector. Class inference from a selector value is out of scope permanently:
it would be a guess about a person's identity made by the same system whose
identity guesses are the thing under test.

**SS-2. An S1 consent record is per-case, revocable, and expires.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

Consent obtained for one case does not carry to the next. Revocation is an
event, and its effect is that the case shreds on the same path an expiry would
take, not a slower one. A consent record with no expiry is refused at schema
validation rather than defaulted, because a default expiry written by the
system is the system consenting on the subject's behalf.

**SS-17. An S3 or S4 run requires a baseline scorecard against S0, S1, or S2
subjects to exist. A dated Class F entry overrides it.**
*[Conclusion recorded 2026-08-26 by the operator. Basis: unstamped.]*

The operator's own sequencing, made a gate rather than left an intention: the
baseline comes from subjects who can confirm a link, and it comes first. The
gate reads whether at least one scorecard exists against a class where precision
and recall are computable, and refuses an S3 or S4 run until one does.

**The override is the point, not a weakness in it.** A gate with no override in
a one-person program is a gate that gets removed the first time it is
inconvenient, and removed silently. A gate with a dated Class F override is one
that gets used visibly, and the entry is the record of the decision. SS-15's
argument applies to this criterion more directly than to any other.

The condition is cheap if the baseline happens anyway, which is what the
operator said would happen. It costs exactly one Class F entry if it does not.

**SS-3. Synthetic personas are isolated, and isolation is a property of the
cast, not of the run.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

A synthetic persona with real followers is a bystander collector. The cast
interacts only with itself. Per-persona recovery selectors are required,
because a cast created from one phone number links the entire cast to the
operator on the first correlation run, which destroys the cast as a measurement
instrument and creates a real subject nobody authorized.

**The two halves of this criterion have different enforcement and it is worth
separating them.** The documented half is checkable: no two personas share a
recovery selector, and no persona declares an edge to a selector outside the
cast. That check runs over `synthetic/CAST.md` and lands in the Step 4 change
that creates the file, because naming a tool mode here while the file does not
exist would be specifying a shape this document does not own. The
account-creation half, meaning whether a persona actually accrued a real
follower on a live platform, is an operator act with no technical control
available, and it is stated rather than mechanized.

---

## 3. The authorization record

**SS-4. A partial authorization is refused, never half-honoured.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

This is `zisr-recon/src/zisr_recon/guard.py`'s
`OriginAuthorization.load()` pattern, which is correct and transfers whole:
every field is required because every field answers a question a reviewer will
ask, and a file missing one of them raises rather than proceeding with the
rest.

Required fields:

| Field | Answers |
|---|---|
| `case_id` | Which case this authorizes, opaque, no subject name |
| `subject_class` | S0, S1, or S2 |
| `selectors` | The exact seed selectors authorized, typed against `ontology/selectors.yaml` |
| `pivot_depth_max` | How far a chain may walk from a seed before it needs a new decision |
| `purpose` | Why this case exists, in one sentence, bound to the case at creation, stated without naming or describing the subject, on the same rule as `case_id` |
| `evidence_ref` | The consent record, credential record, or cast manifest entry |
| `authorized_by` | The ratifier |
| `authorized_on` | The date |
| `expires_on` | The date after which the record no longer authorizes anything |

**Where the record lives, because it is the worst object in the system to
misplace.** The authorization record and its evidence objects are stratum 1 in
`RETENTION.md` RT-1. They sit inside the case boundary under the case key and
they die with the case. An S1 consent record names a living person, so this is
the one object that carries both a selector and a name, and it is never in the
repository under any circumstance. `conformance/gate/*.jsonl` holds synthetic
records only.

`purpose` is a free sentence in a record that a person writes, and
`RETENTION_LEDGER.md` carries a copy of it in a tracked file that survives every
shred. That is why the field is constrained above to a sentence that does not
name or describe the subject. If a purpose cannot be stated that way, the ledger
carries the hash of the purpose record and the sentence itself stays inside the
case boundary.

**SS-5. Three fields of the authorization record are read by `check()`, and a
test proves each one is read.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

This criterion exists because of a measured defect in the precedent, and it is
the single most important line in this document.

In `zisr-recon/src/zisr_recon/guard.py`, `scope` is declared on the frozen
dataclass, listed in the required-fields check, and printed by `describe()`.
`check()` never reads it. The only question `check()` asks of the
authorization is `has_origin`, which is true whenever the file is complete. A
complete authorization file therefore permits every non-NEVER address on
earth, while the tool reports a scope in its own status line. Separately,
`from datetime import date` at line 54 is the only occurrence of that token in
the file, and `expires_on` does not exist at all, so no authorization can
expire.

Both were verified by grep on 2026-08-26. Neither is exploitable where it sits,
because no origin is authorized and the tool cannot act. They stop being
harmless the moment the gated object is a person.

The rule that follows: for each of `selectors`, `pivot_depth_max`, and
`expires_on`, `conformance/gate/*.jsonl` carries a fixture that is identical to
a passing fixture except in that one field, and that fixture must be refused.
A field that no fixture can make refuse is not being read, whatever the code
looks like. `tools/validate_authorization.py --fixtures` fails if any of the
three is missing.

---

## 4. The gate

**SS-6. The gate sits inside the runner, after pivot selection, before argv
construction, and before a credential is drawn.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*
*Corresponds to D5.*

Placement is the whole mechanism. Before `lineage.command_template` is filled
and before the credential pool is touched, because a credential drawn is heat
spent whether or not the request goes out. A gate the analyst consults rather
than passes through is reassurance without protection.

`tools/validate_authorization.py --dispatch-paths` proves that every call site
constructing argv, opening a subscription, **or drawing from the credential
pool** is reached only through `subject_guard.evaluate()`, or is listed in
`runner/dispatch_allowlist.yaml` with a written reason. The credential clause is
not decorative: a draft of this check covered argv and subscriptions only, which
would have passed a call site that draws a credential before the gate and spends
the heat this placement exists to protect. Retrofitting a gate onto a dispatch path that already
has fifteen call sites is how fourteen of them end up gated.

**SS-7. The gate returns three values, and the middle one is not a warning.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

| Return | Consequence, as rendered to the analyst |
|---|---|
| `permitted` | The run proceeds |
| `requires_extension` | REFUSED PENDING AUTHORIZATION. This selector is outside the case authorization. The run did not execute and nothing was collected. Extend the authorization, narrow the pivot, or drop it |
| `refused` | REFUSED. This selector is in a class this case may not collect on. No authorization file unlocks it |

The middle value stops the run. It is the value for "an analyst could
legitimately authorize this, and has not." It is not a prompt rendered over a
request already in flight.

Each state is rendered as its consequence rather than as its token, following
the ZISR COP convention that an operator cannot act on the bare string
`parked`.

**SS-8. Hard refusals are evaluated first, unconditionally.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

Evaluation order:

1. The NEVER list (section 7). Refused whatever any file says.
2. Authorization record present, complete, and unexpired for this case.
3. **`subject_class` is in the set available at this version, and for S3 or S4
   the SS-17 baseline condition is met.** This is the enforcement point for
   SS-17, and without this step the baseline is an intention.
   `conformance/gate/` carries a matched pair on one authorization record
   declaring `subject_class: S4`: with no baseline scorecard on file, asserted
   refused; with a scorecard present, asserted permitted. A single fixture
   proves only that something refuses. The pair proves the gate is reading the
   condition and not the weather.
4. Selector inside the authorized set, or inside `pivot_depth_max` of it.
5. Composed pivot chain inside the authorized set (section 4.1).
6. Bystander declaration present for this connector, with a disposition inside
   the closed set (section 5).

`conformance/gate/*.jsonl` carries a fixture with a complete, valid, unexpired
authorization record that is refused under a named NEVER item, and asserts that
refusal. A present authorization file must not unlock a hard refusal.

**The fixture is built on an item, not on a selector value, and that is not a
convenience.** A draft of this criterion called for a fixture naming a
"NEVER-listed selector". No such thing exists or may exist: section 7 contains
no selector values and names no file holding any, because a per-selector
never-collect list would be a permanent register of real people's selectors in a
tracked file, which is precisely the object SS-14 item 5 and `RETENTION.md`
RT-15 forbid. Item 6 is the item to build the fixture on, since the gate can
evaluate it by reading `DOCTRINE_STATUS.md`, and item 1 is the second.

**Where each NEVER item is actually enforced**, so the list does not read as six
mechanisms when it is not:

| Item | Enforced by |
|---|---|
| 1, authentication and impersonation | A rule. Manifest check at Step 12 under R7 |
| 2, minors | The analyst. The gate cannot verify age, and the text says so |
| 3, platform mutation | A rule. `interaction_class` check at Step 12 under R7 |
| 4, training and fixtures on non-synthetic data | A rule. No mechanism proposed at v0.1 |
| 5, selectors in tracked files | `.githooks/pre-commit`, currently the D-001 stub |
| 6, collection before ratification | The gate, reading `DOCTRINE_STATUS.md` |

### 4.1 Scope drift is a property of the chain, not of the hop

**SS-9. The gate evaluates the composed pivot chain, not the current hop.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

Every run already carries `motivated_by`, the claim that motivated it, so the
pivot chain is already lineage. Scope-drift detection falls out of that
structure rather than needing new plumbing.

Three individually legal hops can compose into a selector outside the
authorized set. The must-fail fixture `scope-drift-three-hops` asserts exactly
this, with violation code `SCOPE_DRIFT_UNADJUDICATED`. A gate that evaluates
only the current hop passes all three and lands somewhere nobody authorized.

### 4.2 Collected content is data, never an instruction

**SS-19. No collected value causes a subject to be reached or data to leave the
machine. Collected content is untrusted input at every boundary that can act on
it.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

Everything this system collects is written by someone else. A bio, a display
name, a channel title, a message body, a filename in a paste. All of it is
attacker-controlled text, and this repository is operated by agents, which means
collected text reaches a context that can act on it.

**This criterion is deliberately narrow, and the boundary matters.** General
input handling, escaping, and rendering are semantics-contract and design
questions at ranks 2 and 7, and doctrine has no opinion on them. Doctrine owns
exactly two of injection's consequences, because they are the two things this
document is authoritative on:

1. **A collected value must never cause a subject to be reached.** An injected
   instruction that results in a run against a selector nobody authorized is a
   subject-selection failure whatever caused it, and the gate in section 4 is
   the thing that has to hold. `subject_guard.evaluate()` reads the
   authorization record and the pivot chain, never the content of a collected
   field, and `conformance/gate/` carries a fixture where a collected bio
   contains a plausible instruction to collect on a second selector, asserting
   the gate refuses.
2. **A collected value must never cause data to leave.** RT-18 is the only
   disclosure path and it requires an active freeze plus a logged act. An export
   triggered by collected content is refused because no such path exists, and
   that is a property of the export boundary rather than of a filter.

**The sharper case is not prompt injection, and it is already in the design.**
`PLAINSIGHT-design.md` specifies `command_template` with a selector interpolated
into argv:

```
command_template: "toutatis -s {credential_ref} -u {username}"
```

A handle containing shell metacharacters is command injection, which reaches
further than any prompt and does so before a model is involved. Interpolation
into argv is therefore a refusal point, and it sits next to the gate for the
same reason the gate sits there: it is the last place before the act. A selector
whose value does not match its registered matcher in `ontology/selectors.yaml` is
refused at argv construction rather than escaped, because escaping is a
transformation that can be got wrong once and a refusal cannot.

**The cast carries the fixture.** One persona holds an injection payload in its
bio, and the pipeline is asserted to collect it, store it, render it to the
analyst, and act on none of it. That is the known-negative canary pattern
applied to injection, and it is a third reason the cast has to exist before the
connectors do.

**What this criterion does not claim.** It does not make the system injection
proof. An analyst reading a bio that says something manipulative is a human
reading manipulative text, and no mechanism here changes that. What it does is
ensure that the two outcomes doctrine cares about, an unauthorized subject and an
unauthorized egress, cannot be reached by content at all, because both are gated
on records rather than on text.

### 4.3 Tagging what tried to attack the pipeline

**SS-21. An account observed carrying an injection payload is tagged inside the
case. The tag is subject-derived and dies with the case. The payload family is a
finding and survives.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

The operator asked for accounts carrying command or prompt injection to be
tagged, so there is a list of actors to avoid. The detection half is
straightforward and worth having. The list half runs into RT-2, and the conflict
is stated here rather than resolved quietly.

**What is tagged, and what it does.** When a collected value matches an injection
signature, the item is tagged at the extract boundary. The tag makes the analyst
see it, keeps SS-16 from treating the node as an ordinary pivot candidate, and
records that the pipeline met an attack and did not act on it. That is real
defensive value and it costs nothing against the posture, because the tag lives
inside the case with everything else derived from the subject.

**What survives is the pattern, not the roster.** Two different objects:

| Object | Example | Subject values | Survives the shred |
|---|---|---|---|
| Payload family finding | A payload family appears in bios on one platform at a measured rate, with the shapes it takes | No | **Yes.** Stratum 3, and this is the transferable knowledge |
| Account roster | These specific accounts carried it | Yes | **No.** RT-2 forbids it |

The finding is what protects the next case, and it protects it better than a
roster would, because a signature generalizes to accounts nobody has seen and a
list only covers the ones already met.

**A persistent roster is a target package wearing a defensive name, and that is
the thing worth saying plainly.** The operator's posture is that PII and target
packages are not maintained here. A durable list of accounts, indexed and
accumulated across cases, is structurally the same object as a target package
regardless of the intent behind it, and RT-2 refuses it for the same reason it
refuses every other subject-derived value in a surviving stratum. Keeping one
would require a deliberate ratified exception to RT-2, not an implicit one, and
this criterion does not create it.

**On publishing such a list.** The operator raised it and marked it a later
decision, which is the right call, and one argument belongs on the record before
that decision is taken. It is recorded as an assistant reading in
`DOCTRINE_STATUS.md` awaiting confirmation rather than settled here.

---

## 5. Incidental collection and bystanders

**SS-10. A connector that reaches beyond its named selector declares what it
reaches, and an undeclared bystander class is refused at manifest validation.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

These tools collect on populations. One channel subscription collects the
message text of every member in order to observe one. A follower-list expansion
on an account with 900 followers creates 900 selector records. CrossLinked
enumerates an entire organization's staff to find one employee; that is its
function, not a side effect.

Three properties follow, and none of them is optional.

- **Bystanders never pass through the gate**, because they arrive as a
  byproduct rather than as a target. The gate cannot be the control here. The
  manifest declaration is.
- **`subject_relation` is a computed column with values `seed | pivot |
  incidental`, never an asserted one.** A connector cannot claim its collection
  was incidental; the runner computes it from the pivot chain.
- **Incidental persons never become pivot origins.** An S5 selector is not a
  seed for anything. `conformance/gate/` carries the refusal fixture.

**The disposition vocabulary is closed at v0.1 to `count_only | refuse`.** A
declaration has to be checkable against something, and "declared" with an open
value set is not a check.

`retain` is defined and refused, on the same pattern SS-1 uses for S3 and S4.
Reaching it is a Class F ratification with a dated stamp, which is the point:
`CLAUDE.md` §3 gate 2 names a bystander disposition of `retain` as one of the
one-line diffs that widens who can be collected on while reading as Class B. A
manifest declaring a disposition outside the closed set is refused at manifest
validation rather than defaulted, and `conformance/gate/` carries a fixture
asserting that `disposition: retain` is refused.

R8 stays open on what lies beyond these two. A `requires_extension` bystander
flow is genuinely undecided, and closing the v0.1 set does not decide it.

**What this criterion decides and what it does not.** Which dispositions are
permitted is a rank-1 question, because `retain` widens who is collected on and
is Class F by effect. The manifest field's name, its value encoding, and where it
sits in the document are schema questions settled in
`schema/connector-manifest.schema.json` at Step 12, and this file has no opinion
on them. What lands with the drafts is the violation code for an undeclared or
out-of-set disposition and one must-fail manifest fixture, so the first bullet
above has a named refusal rather than an intention.

**SS-11. Incidental content carries a shorter, non-extendable TTL.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*
*Enforced in `RETENTION.md` RT-6. Recorded here because the rule is about
subjects.*

Bystander data must not inherit the subject's TTL, including extensions granted
for reasons that have nothing to do with the bystander. At v0.1 this is a flat
rule rather than differential machinery: incidental content expires at the
shorter of the case TTL and the incidental TTL, and an extension of the case
does not extend it.

`PLAINSIGHT-design.md` §8.3 puts messages in a separate table partitioned by
case and then month, for performance. That choice is load-bearing for retention
as well, because it is what makes independent shredding of the
bystander-dominant class possible. The second reason is recorded here so nobody
merges the tables later for simplicity.

**SS-16. Enumeration produces inert nodes. A deep dive on a node is a separate
authorized act, and nothing spawns one automatically.**
*[Conclusion recorded 2026-08-26 by the operator. Basis: unstamped.]*

A query names one node: a person, an organization, or a location. It returns a
searchable list of linked nodes, which for an organization includes the people
tied to it, alias and shell organizations, and the other defaults its manifest
declares. Those results are **nodes in a web, not subjects.** They are listed,
searchable, and linkable. Nothing is collected against any of them.

Selecting a node for a deep dive is a new run, and it passes the gate in section
4 like any other. A discovered person needs their own authorization record and
their own class before anything is collected against them. Which class that is
depends on who they are, and S3 and S4 are available, so this is a decision the
analyst makes deliberately rather than a door that is closed.

**The control here is the act, not the class.** That distinction is worth being
precise about, because a reader could take this criterion for a restriction on
reach and it is not one. What it forbids is a single query fanning out into
collection against everyone it touched. What it permits is any of those nodes
becoming a target the moment a person decides it should and records why.

Three consequences:

- **A node is not a run.** Appearing in a web costs the subject nothing beyond
  the enumeration that surfaced them, and SS-11's incidental TTL governs how
  long that residue lives.
- **Depth is unbounded, breadth is deliberate.** Chaining ten deep dives is
  permitted. Auto-expanding one enumeration into ten runs is not.
- **The pre-flight count in SS-12 is what makes this visible**, because the
  number of nodes an enumeration will surface is the number of people it touches.

**SS-12. A pivot that reaches beyond its named selector does not dispatch unless
the pre-flight record carries an incidental-count estimate, or carries
`unestimable` with a reason. A blank field is a refusal.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

The estimate is a required field on the pre-flight record, checked by
`subject_guard.evaluate()`, with a `conformance/gate/` fixture asserting refusal
when the field is absent. That is the whole criterion.

`unestimable` exists because the two connector shapes differ and a bare refusal
would be unimplementable for the one that most needs the rule. A follower-list
expansion knows its count before dispatch. An organization enumeration does not
know how many people it will surface until it has surfaced them. Refusing the
second shape outright would remove the capability; requiring it to say so, with
a reason, keeps the number honest and keeps the run possible.

How the number is rendered is a rank-7 question and this document does not
answer it. The design already renders a per-run pre-flight exposure line, so the
string exists and gains a field.

---

## 6. Credentials, and the record we cannot reach

**SS-13. The platform's log of our collection is outside every mechanism in
this repository, and the only control over it is not collecting.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

Whose account performs the collection is a subject-selection question, not an
operations question. If collection runs from the operator's real account, the
operator's identity is bound to every view of every subject, in a record the
platform holds permanently and this project cannot see, amend, or destroy.

A synthetic subject viewed by a synthetic credential produces a platform-side
record linking two things the team owns. That is the strongest available
argument for the cast, and it is an argument about evidence rather than about
caution.

Two rules at v0.1:

- A credential used for collection is recorded in the authorization record's
  `evidence_ref` chain, so the question "whose account saw this" has an answer
  that is not a memory.
- `quarantine_credential: true` requires a written exit criterion at the moment
  it is set. A quarantine with no exit criterion either lasts forever or ends
  when somebody notices, and neither is a decision.

**SS-20. The account that looks and the account that is looked at are never the
same account, and they are two separately provisioned populations.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

This was a category error waiting to happen, and it is worth naming because both
populations are fake accounts the team creates and the resemblance is the trap.

| | **Collection persona** | **S2 cast persona** |
|---|---|---|
| Role | The credential a connector authenticates with | The subject a connector is pointed at |
| Purpose | Makes the tool able to run at all | Makes the answer scoreable |
| Governed by | `doctrine/CREDENTIAL_LIFECYCLE.md` | `synthetic/CAST.md`, SS-3 |
| Appears in | `credential_pool` | `GROUND_TRUTH.yaml` |

**Most of the audited connectors cannot run without a collection persona.**
toutatis needs an Instagram `sessionid`. informer needs a Telegram account. The
Discord tooling needs a Discord account. Under R7 that authentication is a read
and is permitted, which means the credential pool is not optional infrastructure
and is not the same work as the cast.

Two things break if the populations overlap.

- **The measurement stops being a measurement.** A cast persona observing another
  cast persona through a credential that is itself in the cast means the system
  is partly observing its own infrastructure, and any correlation it finds
  between them is one the team created for operational reasons rather than one
  the tool discovered. The ground truth would be wrong in a direction nobody
  would think to check.
- **The platform-side record links the two.** SS-13 already states that the
  platform's log of our collection is outside every mechanism here. If the
  looking account is also a subject, that log ties our collection activity to our
  measurement population permanently, in a record we cannot reach.

**The mechanism is a disjointness check, not a rule.** No selector appears in
both `synthetic/CAST.md` and the credential pool, and
`tools/validate_authorization.py` refuses when the two sets intersect. A
recovery selector shared between the populations counts as an intersection, which
is the case a naive set comparison on handles alone would miss.

**The provisioning consequence is the one to plan around.** Both populations need
per-account email and phone, so the cost is two pools rather than one, and the
collection pool is the more urgent of the two because without it no connector
runs at all.

`doctrine/CREDENTIAL_LIFECYCLE.md` was deferred until the credential pool had a
real shape. This criterion gave it one, and that file now carries CR-1 through
CR-8. CR-1 holds the disjointness mechanism named above, and CR-2 the
provisioning record each credential carries.

---

## 7. Absolute prohibitions

**SS-14. These refuse whatever any authorization file says.**
*[Conclusion recorded: items 1 and 3 on 2026-08-26 via R7, items 2, 4, 5 and 6
on 2026-08-27. Basis: unstamped throughout.]*

The NEVER list is the analogue of `guard.py`'s reserved-range list, and it is
evaluated first for the same reason: a hard refusal that a config file can
unlock is not a hard refusal.

1. **No authentication as any account the team does not hold, and no
   impersonation of any person.** Logging in with an S0 or S2 credential the
   team owns is permitted and is a read. Using anyone else's credential, session,
   or identity is not, whatever the source of it. R7 is stamped and this is the
   ratified line rather than a placeholder.
2. **No collection against a person under 18, or against a selector whose
   available evidence indicates that.** The gate cannot verify age. The rule is
   here because its absence would be read as permission, and its presence
   requires a run to stop when the analyst learns it, not when a validator does.
3. **No action that mutates a target platform.** No posting, messaging,
   following, or friend request. No profile view that the platform surfaces to
   the subject as an interaction.

   **R7 is stamped, and the line it draws is observability by the subject.**
   Authenticating with a team-held credential and reading is permitted.
   Anything the subject can observe happened is an interaction and is refused,
   including a view the platform surfaces to them as a view, a follow, a friend
   request, a message, and any state the platform shows them changed.

   **This is a rule that becomes a structure at Step 12, and it is not one
   yet.** The mechanism is an adapter declaring read verbs only, checked by
   `validate_manifest.py` against the declared methods and the
   `command_template`, with `interaction_class` on every manifest resolving
   against this line. Until that check exists this is a rule an author follows,
   and a draft of this item called it an architectural boundary the system
   already had, which is the laundering design gate 6 forbids, in the list that
   reads as most enforced.
4. **No model training and no fixture-building on non-synthetic data.** A
   matcher trained or fixture-built on a real case carries that case in its
   weights or its fixtures permanently and cannot be shredded. CUT LIST B names
   where the pressure arrives: auto-promotion of GENERATED to OBSERVED waits
   until the matcher library has fixtures. Those fixtures come from the cast or
   they do not exist.
5. **No selector belonging to a natural person enters a tracked file**, which
   includes worklog entries, commit messages, cassettes, and fixtures. Git
   history is the one store a crypto-shred cannot reach.

   **Enforcement state, stated in place rather than implied.** The intended
   mechanism is `tools/validate_retention.py --repo-scan` in
   `.githooks/pre-commit`, with violation code
   `FIXTURE_CONTAINS_LIVE_SELECTOR` in `policy/violation-codes.yaml` and
   `canary_subject_class` required on every connector manifest. **None of those
   three exists yet.** The hook is wired and the tool is a stub that exits 0
   and prints that it checked nothing, tracked as D-001 and implemented at Step
   8. `policy/` is empty. Until then the only thing enforcing this item is the
   Execution Limits clause in `AGENTS.md` §4, which is a rule an agent reads
   rather than a gate that refuses.

   Issue text, chat transcripts, and anything outside the working tree are named
   here and are outside what a pre-commit scan can reach at all. That half is a
   stated rule with no mechanism available, on the RT-14 pattern, and it says so
   rather than borrowing the scan's authority.
6. **No collection at all, including against a synthetic account, until every
   one of the following is stamped in `DOCTRINE_STATUS.md`:** this file per
   criterion; `RETENTION.md` per criterion; `policy/subject-authorization.yaml`
   and `schema/subject-authorization.schema.json`; `policy/retention.yaml`;
   `ontology/selectors.yaml`; `spec/pse-semantics-contract.md` §5 and §12;
   `synthetic/CAST.md` with a sealed, hash-pinned `GROUND_TRUTH.yaml` carrying
   at least one designed confuser pair; and `runner/dispatch_allowlist.yaml`.

   **And one condition that is not a document and is therefore not stampable:
   `preflight` has passed in this runner process at startup.** Its failure is
   fatal to the runner rather than a warning. The four checks are
   `validate_authorization.py --dispatch-paths`,
   `validate_authorization.py --fixtures`,
   `validate_retention.py --policy --shred-roundtrip`, and
   `validate_retention.py --repo-scan`. A `make preflight` target exists so CI
   can run the same set against fixtures; the Makefile is not the enforcement,
   because a mechanism whose only enforcement is a build target is enforced only
   against people who run build targets, and collection runs are started by
   people in a hurry.

   **Enforcement state, stated in place.** None of the four checks exists yet.
   `validate_authorization.py` is not written, and `validate_retention.py` is
   the D-001 stub whatever flags it is passed. The `make preflight` target that
   exists today runs a different battery: the doctrine, hygiene, layer-model,
   ontology and cast validators, the telemetry test, and the stub. The
   four-check runner gate is Step 8 and Step 10 work.

   The list above is enumerated here rather than incorporated by reference.
   `docs/THE-GAMEPLAN.md` §4 is its provenance and holds the argument for each
   item, and that file carries no rank in the authority order, declares itself
   unratified, and has an expiry condition. An absolute prohibition whose
   content can change by editing an unranked document is not absolute.

---

## 8. The ladder terminates in one person

**SS-15. The operator is the ratifier, the maintainer, and the analyst, and
this is stated rather than left implicit.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

Every operator-approval gate in this document is the operator approving their
own request. That is a genuine limit on every control here, and writing it down
is the mitigation, because a control whose bypass is undocumented gets bypassed
silently and a control whose bypass is a dated Class F entry gets bypassed
visibly. The ZMeta documents work for this reason. They did not remove the
operator's authority. They made using it leave a mark.

Three mitigations, all already used elsewhere in this program:

- An adversarial pass from a fresh agent context against the operator's own
  decisions, run before a Class F stamp rather than after.
- Freeze-then-score for anything the operator scores themselves: the cluster
  set is frozen with a content hash before the truth file is opened.
- The doctrine review log records the cases where the doctrine won, not only
  the unresolved ones. Recording only failures removes the baseline that makes
  an outlier recognizable.

---

## 9. What is explicitly NOT gated

This section exists so the doctrine is productive rather than obstructive, and
so nobody defers buildable work waiting for a permission it does not need.

None of the following requires any subject authorization beyond S0, S1, and S2:

- The Run, Item, and Claim spine, and the blob store.
- PSE, its schemas, the selector registry, and the whole policy pack.
- Every connector and manifest, both canaries, and the conformance ladder.
- All six views, the Merge Sheet, clusters and exclusions, coverage intervals
  and the watchdog, the Lineage Drawer, and retroactive invalidation.
- DRAFT and the export boundary.
- The entire retention mechanism.
- **Complete end-to-end collection against S0, S1, S2, N0, and L0 nodes at any
  depth, with no ceiling on aggressiveness**, and against S3 and S4 once SS-17's
  baseline exists or is overridden.
- **Enumerating an organization or a location and building the web out of it**,
  including alias and shell organizations and the people tied to them. What SS-16
  gates is collecting against those people automatically, never listing them.

Weeks 1 through 13 of the build plan need no third-party targeting permission
at all, and nothing in this document caps how deep a chain of deliberate deep
dives may go.

**One precise correction to a sentence it would be easy to write here.** The
gate does constrain depth, through `pivot_depth_max` in the authorization
record, and a draft of this section previously claimed it never did. What is
uncapped is depth against an authorized subject: `pivot_depth_max` bounds how
far a chain may walk from a seed *before it needs a new decision*, and a chain
that reaches the limit returns `requires_extension` rather than `refused`. The
analyst raises it. Nothing here sets a ceiling on how deep that decision may
go, and there is no aggressiveness budget, no run quota, and no rate cap in this
document. The constraint is on reaching a new person without a decision, not on
depth as such.

---

## 10. Rejected readings, do not re-derive

Recorded so a settled question is not reopened by someone reading the same
evidence and reaching the same wrong conclusion. Mirrors the table in
`DOCTRINE_STATUS.md`.

> **[REJECTED READING, DO NOT RE-DERIVE IT]** Retention alone bounds the harm
> of collection. Deleting a profile does not un-collect it, and the
> platform-side record of the collection is outside every mechanism in this
> repository. Subject selection is the upstream control. Rejected 2026-08-26.

> **[REJECTED READING, DO NOT RE-DERIVE IT]** The gate can infer a subject
> class from the selector value, so an authorization record is only needed for
> edge cases. Inferring a class means guessing whose account a handle is, using
> the same correlation machinery whose guesses are the thing under test. The
> gate reads a class that a person wrote down, or it refuses. Rejected
> 2026-08-26.

---

## 11. Ratification table

Nothing below is stamped. `DOCTRINE_STATUS.md` is the pin of record and this
table is a convenience index into it. Where the two disagree,
`DOCTRINE_STATUS.md` wins, because the mechanism reads that file.

| Item | Subject | Blocks | Related open decision |
|---|---|---|---|
| SS-1 | Closed class set: S0, S1, S2, S3, S4, S5, N0, L0. **Conclusion recorded** | The gate, the cast | R4 stamped |
| SS-2 | S1 consent is per-case, revocable, expiring | S1 collection | none |
| SS-3 | Synthetic isolation and per-persona recovery selectors | Step 4, the cast | none |
| SS-4 | Partial authorization refused | The authorization schema | none |
| SS-5 | Three fields read by `check()`, each with a refusal fixture | `validate_authorization.py --fixtures` | none |
| SS-6 | Gate placement inside the runner | `runner/subject_guard.py` | D5 |
| SS-7 | Three return values, rendered as consequences | The gate, the interface | D5 |
| SS-8 | Hard refusals first, unconditionally | The gate | none |
| SS-9 | Chain evaluation, not hop evaluation | The gate, fixture 5 | none |
| SS-10 | Declared bystander classes, refused when absent; disposition closed to `count_only \| refuse` | `validate_manifest.py` | R8 beyond the two |
| SS-11 | Incidental TTL, shorter and non-extendable | `policy/retention.yaml` | R8, RT-6 |
| SS-12 | Incidental estimate or `unestimable` required on the pre-flight record; blank refuses | `subject_guard`, `conformance/gate/` | none |
| SS-13 | Credentials, and the record we cannot reach | Credential pool design | none |
| SS-14 | The NEVER list, six items. Items 1 and 3 follow R7. **Conclusion recorded** | Everything | R7 stamped |
| SS-15 | The single-operator limit, stated | Nothing mechanical | none |
| SS-16 | Enumeration yields inert nodes; a deep dive is a separate authorized act. **Conclusion recorded** | The gate, the web | none |
| SS-17 | S3 and S4 behind a baseline scorecard, with a dated Class F override. **Conclusion recorded** | The gate | R4 stamped |
| SS-18 | Findings carry their subject class; mixed scorecards refused. **Conclusion recorded** | The scorer | none |
| SS-19 | Collected content cannot reach a subject or cause an egress; argv refuses an unmatched selector. **Conclusion recorded** | `subject_guard`, argv construction | none |
| SS-20 | Collection personas and cast personas are disjoint populations. **Conclusion recorded** | `validate_authorization.py`, the credential pool | none |
| SS-21 | Injection tag dies with the case; the payload family survives as a finding | The extract boundary, `conformance/` | Publication is an open reading |

**R7 is stamped and the vocabulary it blocked is now defined.** The line is
observability by the subject: authenticating with a team-held credential and
reading is permitted, and anything the subject can observe happened is refused.
`interaction_class` on every connector manifest resolves against that line, and
the check that enforces it lands at Step 12.

**Still open and affecting a criterion above.** R8 remains open on bystander
dispositions beyond `count_only | refuse`, which is what SS-10 defers rather
than decides.
