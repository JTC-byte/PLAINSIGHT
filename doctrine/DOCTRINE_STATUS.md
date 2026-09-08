# Doctrine status: the pin of record

Nothing in this repository binds unless it appears below with a date and a
ratifier. One partially stamped item does not stamp its file. Conclusion is
ratified separately from basis, because no mechanism should be built on a
rationale the operator was never shown.

Mechanisms read this file rather than the document they enforce. An unratified
criterion refuses rather than permits.

## Ratified

**Landed 2026-08-27 in commits `1abb354` (the Wave 0 rows) and `4c5cd25` (the
EG, CR, HY, SS-19 to SS-21 and RT-19 rows)**, authored by the operator. R6 as
amended that day permits an agent to execute the commit of a decision the
operator made; the decision and the authorship stayed theirs. These rows are the
operator's decisions transcribed by an agent, and the transcription is still
worth reading against what was actually said.

**Basis is unstamped throughout, deliberately.** The conclusions were decided in
session. The reasoning in `docs/PLAINSIGHT-FOUNDATION.md` §3 and
`docs/THE-GAMEPLAN.md` §3.0 has not been reviewed, and stamping a basis nobody
read is the half-stamping this table exists to prevent.

| Item | File | Version | Conclusion stamped | Basis stamped | Ratifier |
|---|---|---|---|---|---|
| D1 fork ZMeta as PSE | `docs/PLAINSIGHT-FOUNDATION.md` §3 | v0.1 | 2026-08-26 | unstamped | operator |
| D2 closed selector vocabulary | `docs/PLAINSIGHT-FOUNDATION.md` §3 | v0.1 | 2026-08-26 | unstamped | operator |
| D3 append-only event log | `docs/PLAINSIGHT-FOUNDATION.md` §3 | v0.1 | 2026-08-26 | unstamped | operator |
| D4 retention as mechanism | `docs/PLAINSIGHT-FOUNDATION.md` §3 | v0.1 | 2026-08-26 | unstamped | operator |
| D5 three-valued subject gate | `docs/PLAINSIGHT-FOUNDATION.md` §3 | v0.1 | 2026-08-26 | unstamped | operator |
| R1 shred unit, both layers | `doctrine/RETENTION.md` RT-3 | v0.1 | 2026-08-26 | unstamped | operator |
| R2 TTL 30 / 30 / **60** | `doctrine/RETENTION.md` RT-5 | v0.1 | 2026-08-26 | unstamped | operator |
| R3 index inside the boundary | `doctrine/RETENTION.md` RT-7 | v0.1 | 2026-08-26 | unstamped | operator |
| R4 subject classes, **maximum reach** | `doctrine/SUBJECT_SELECTION.md` SS-1 | v0.1 | 2026-08-26 | unstamped | operator |
| R5 `text: forever` scoped by case | `doctrine/RETENTION.md` RT-8 | v0.1 | 2026-08-26 | unstamped | operator |
| R6 human-only attribution, **amended** | `CLAUDE.md` §5 | v0.2 | 2026-08-26, amended 2026-08-27 | unstamped | operator |
| R7 interaction line | `doctrine/SUBJECT_SELECTION.md` SS-14 | v0.1 | 2026-08-26 | unstamped | operator |
| D6 event-type set, **nine** | `spec/layer-model.yaml` | v0.1 | 2026-08-27 | unstamped | operator |
| D7 version label `pse-event-0.1`, Unlocked | `spec/pse-semantics-contract.md` (to be written) | v0.1 | 2026-08-27 | unstamped | operator |
| D8 one repo, lane boundary enforced | `README.md`, `AGENTS.md` | v0.1 | 2026-08-27 | unstamped | operator |
| R8 v0.1 bystander set `count_only \| refuse` | `doctrine/SUBJECT_SELECTION.md` SS-10 | v0.1 | 2026-08-27 | unstamped | operator |
| Disclosure export under freeze | `doctrine/RETENTION.md` RT-18 | v0.1 | 2026-08-27 | unstamped | operator |
| SS-1 to SS-21, all criteria | `doctrine/SUBJECT_SELECTION.md` | v0.1 | 2026-08-27 | unstamped | operator |
| RT-1 to RT-18, all criteria | `doctrine/RETENTION.md` | v0.1 | 2026-08-27 | unstamped | operator |
| EG-1 to EG-6, all criteria | `doctrine/EGRESS.md` | v0.1 | 2026-08-27 | unstamped | operator |
| CR-1 to CR-8, all criteria | `doctrine/CREDENTIAL_LIFECYCLE.md` | v0.1 | 2026-08-27 | unstamped | operator |
| HY-1 to HY-4, all criteria | `doctrine/HYGIENE.md` | v0.1 | 2026-08-27 | unstamped | operator |
| Gate telemetry with a 90 day TTL | `doctrine/RETENTION.md` RT-19, `doctrine/HYGIENE.md` | v0.1 | 2026-08-27 | unstamped | operator |
| Compartmentalized deployment | `doctrine/EGRESS.md` EG-1, EG-2 | v0.1 | 2026-08-27 | unstamped | operator |
| Collection pool provisioned first | `doctrine/CREDENTIAL_LIFECYCLE.md` | v0.1 | 2026-08-27 | unstamped | operator |
| L0 location class | `doctrine/SUBJECT_SELECTION.md` SS-1 | v0.1 | 2026-08-26 | unstamped | operator |
| Inert nodes, manual deep dive | `doctrine/SUBJECT_SELECTION.md` SS-16 | v0.1 | 2026-08-26 | unstamped | operator |
| Baseline gate with logged override | `doctrine/SUBJECT_SELECTION.md` SS-17 | v0.1 | 2026-08-26 | unstamped | operator |
| Class labels, mixed scorecards refused | `doctrine/SUBJECT_SELECTION.md` SS-18 | v0.1 | 2026-08-26 | unstamped | operator |
| Freeze crosses the ceiling | `doctrine/RETENTION.md` RT-17 | v0.1 | 2026-08-26 | unstamped | operator |

### What each decision was, in the operator's terms

Recorded because a row in a table is not a reason, and in six months the row is
all that survives.

- **R4, maximum reach.** S0 through S4 all available, plus N0 and L0. The
  operator's words: get the baseline from known consenting people first, but do
  not limit reach. The ground-truth argument was put and was not disputed; it
  resolves into SS-17 and SS-18 rather than into a refusal.
- **R2, 60 rather than 180.** Cases must live long enough to validate something
  and validating should not take six months. Holding longer is a manual act for
  a stated reason, which is RT-17.
- **R7, the interaction line.** Authenticating with a team-held credential and
  reading is permitted. Anything the subject can observe happened is refused.
  This keeps toutatis, informer, and the Discord and Instagram tooling usable,
  which the unauthenticated-only reading would have removed.
- **The web model.** A query names one node and returns a searchable list of
  linked nodes. Nothing spawns a deep dive. Each node is selectable for a
  deliberate one. The control is the act, not the class.
- **The baseline gate.** Mechanism, with a dated Class F override, rather than
  an intention.
- **R6, amended the same session it was stamped.** The original reading put the
  git command in the operator's hands. The operator corrected it: an agent may
  execute a commit or a push when instructed for that act, with the operator as
  author. The decision stays the operator's and the attribution rule is
  unchanged, so what moved is the mechanics rather than the authority. Recorded
  as v0.2 rather than as an edit, because a stamped item that changes quietly is
  the drift this table exists to prevent.

## Pending ratification

**Every conclusion is recorded. Nothing is pending a conclusion.** What remains
is listed below, and none of it blocks a build.

| Item | Kind | Blocks | Notes |
|---|---|---|---|
| Every basis stamp, all 58 criteria and the 16 D and R decision rows | Basis | nothing mechanical | Deliberate. The reasoning in `docs/PLAINSIGHT-FOUNDATION.md` §3 and `docs/THE-GAMEPLAN.md` §3.0 has not been reviewed. Conclusions bind; bases are unread |
| R8 beyond `count_only \| refuse` | Conclusion, scoped | not blocking v0.1 | The v0.1 pair is stamped. Whether a third disposition exists is left open until a connector manifest shapes the question |
| `doctrine/DISCLOSURE.md` | Artifact | nothing yet | **Its deferral trigger has fired.** RT-18 is the second egress path `docs/THE-GAMEPLAN.md` §2.2 named as the trigger. RETENTION.md RT-14 and RT-18 stand in |
| `PLAINSIGHT-FOUNDATION.md` DRAFT header | Housekeeping | nothing | Line 4 still reads DRAFT and says nothing is operator-ratified. D1 through D5 now are. Clearing that line is the operator's act |
| `spec/pse-semantics-contract.md` §5, subject authorization | Artifact, stamp target | the first collection run, with the other seven items SS-14 item 6 names | Drafted 2026-09-08 with Step 7. The section explains how the SS-4 record and the gate's decision appear on the wire and the D5 line the generated lineage policy carries. Stamping it stamps the explanation, not the doctrine it explains |
| `spec/pse-semantics-contract.md` §12, retention, shred and egress | Artifact, stamp target | the first collection run | Drafted 2026-09-08 with Step 7. The section explains the strata per type, what crosses to LOCAL, and the shred receipt. Same rule |

### Step 3 criteria: all conclusions recorded 2026-08-27

Per-criterion, because one partially stamped item does not stamp its file. The
two documents carry the argument for each; this is where the stamp goes. A
criterion with no row here refuses, so this table is the mechanism rather than an
index of one. **Every row below carries a recorded conclusion and an unstamped
basis.** Four of them were put to the operator individually because they encode a
choice rather than a mechanism: RT-6's incidental TTL, RT-11's blast radius,
RT-14 with RT-18, and SS-2's consent shape.

| Item | Source | Blocks | Notes |
|---|---|---|---|
| SS-1 closed class set | `doctrine/SUBJECT_SELECTION.md` | The gate, the cast | S0-S4, S5, N0, L0. **Conclusion recorded via R4** |
| SS-2 S1 consent per-case, revocable, expiring | same | S1 collection | **Put individually.** No default expiry; absent expiry refuses. Standing consent was offered and declined |
| SS-3 synthetic isolation, per-persona recovery selectors | same | Step 4 | The cast is a measurement instrument and isolation is what keeps it one |
| SS-4 partial authorization refused | same | The authorization schema | `guard.py`'s pattern, which transfers whole |
| SS-5 three fields read by `check()`, each with a refusal fixture | same | `validate_authorization.py --fixtures` | **The criterion that exists because of the measured `guard.py` defect** |
| SS-6 gate placement inside the runner | same | `runner/subject_guard.py` | Carries D5 |
| SS-7 three return values, rendered as consequences | same | The gate, the interface | Carries D5 |
| SS-8 hard refusals first, six-step evaluation order | same | The gate | Step 3 is where SS-17's baseline condition is actually enforced |
| SS-9 chain evaluation, not hop evaluation | same | Fixture 5, `SCOPE_DRIFT_UNADJUDICATED` | |
| SS-10 declared bystander classes, disposition closed | same | `validate_manifest.py` | `retain` defined and refused. R8 open beyond the two |
| SS-11 incidental TTL, shorter and non-extendable | same | `policy/retention.yaml` | Enforced by RT-6 |
| SS-12 incidental estimate or `unestimable` required | same | `subject_guard`, `conformance/gate/` | Blank field refuses |
| SS-13 credentials, and the record we cannot reach | same | Credential pool design | `quarantine_credential` needs a written exit criterion |
| SS-14 the NEVER list, six items | same | **Everything** | Items 1 and 3 **conclusion recorded via R7**. Item 5 names a mechanism that is currently the D-001 stub and says so |
| SS-15 the single-operator limit, stated | same | Nothing mechanical | Stating it is the mitigation |
| SS-16 inert nodes, deep dive is a separate act | same | The gate, the web | **Conclusion recorded.** The control is the act, not the class |
| SS-17 baseline gate for S3 and S4 | same | The gate | **Conclusion recorded.** Mechanism with a dated Class F override |
| SS-18 class labels, mixed scorecards refused | same | The scorer | **Conclusion recorded.** The consequence of maximum reach |
| SS-19 collected content is data, never an instruction | same | `subject_guard`, argv construction | **Conclusion recorded.** Scoped to the two consequences doctrine owns: an unauthorized subject, and an egress |
| SS-20 collection personas disjoint from the cast | same | The credential pool, `validate_authorization.py` | **Conclusion recorded.** Two populations, two provisioning pools. Fired the CREDENTIAL_LIFECYCLE trigger |
| SS-21 injection tag inside the case, payload family as a finding | same | The extract boundary | **Conclusion recorded.** A persistent roster would need a ratified RT-2 exception, which this does not create |
| RT-1 strata declared at write time | `doctrine/RETENTION.md` | **The first write** | Five strata. No later date to decide this |
| RT-2 no subject values in a surviving stratum | same | `--policy` | |
| RT-3 shred unit is both layers | same | The shred implementation | **Conclusion recorded via R1** |
| RT-4 per-case key from the first blob | same | **The first blob** | Carries D4. Cannot be retrofitted at any cost |
| RT-5 30 day TTL, 30 day extensions, **60 day ceiling** | same | The first case | **Conclusion recorded via R2.** Ceiling needs a refusal behind it |
| RT-6 incidental TTL **7 days**, non-extendable, swept daily | same | The first pivot | **Put individually.** Enforces SS-11 |
| RT-7 full-text index inside the shred boundary | same | The index design | **Conclusion recorded via R3.** Real cost in STREAM, accepted in the decision |
| RT-8 `text: forever` scoped by `retain_until` | same | The storage layer | **Conclusion recorded via R5.** Requires the `PLAINSIGHT-design.md:648` correction |
| RT-9 five verification checks, run outside the sweep | same | Any deletion claim | Check 5 is the anti-overreach check |
| RT-10 no receipt row, no shred | same | The ledger | Names `runner/reconcile_ledger.py`, which does not exist yet |
| RT-11 `SHRED_FAILED` blocks all runs **system-wide** | same | The runner | **Put individually.** Cleared only by a passing `verify_shred`, logged. No override |
| RT-12 heartbeat absence is a rendered state | same | The sweep | |
| RT-13 `--finding` before the shred | same | The first case close | Carries the HMAC rejected reading |
| RT-14 demos and recordings built on the cast | same | The first demo | **Put individually.** No mechanism available, and says so. RT-18 is the one exception |
| RT-15 no live selector in a tracked file | same | **Every commit** | `consented` cut from the canary enum |
| RT-16 pinned connector versions not deletable | same | Any case reopen | The one rule here that forbids a deletion act |
| RT-17 the freeze, with expiry, obligation and escalation | same | The first freeze | **Conclusion recorded.** The only path past the 60 day ceiling |
| RT-18 disclosure export under an active freeze | same | The first disclosure | **Conclusion recorded.** The one path a whole non-synthetic case leaves by. Minimization deliberately inverted |
| RT-19 gate telemetry, 90 days rolling, untracked | same | The first gate run | **Conclusion recorded.** Stratum T. Records the location, never the matched value |

| Item | Source | Blocks | Notes |
|---|---|---|---|
| EG-1 two environments, execution is the boundary | `doctrine/EGRESS.md` | The first live run | **Conclusion recorded.** LOCAL is code, ISOLATED is collection |
| EG-2 the case store lives in ISOLATED | same | **The first blob** | **Conclusion recorded.** No later date, same argument as RT-4 |
| EG-3 the interface reads, never copies | same | The interface | **Conclusion recorded.** A local render cache is a stratum-1 object on the wrong side |
| EG-4 no credentials on LOCAL | same | The first credential | **Conclusion recorded.** Restated in CR-4 |
| EG-5 three strata cross outward | same | The first export | **Conclusion recorded.** Stratum 4 crosses both ways, which is the flow RT-15 governs |
| EG-6 `egress` recorded, wrong environment refused | same | The first run | **Conclusion recorded.** Refusal rather than annotation, checked at runner startup |
| CR-1 disjoint from the cast, recovery selectors included | `doctrine/CREDENTIAL_LIFECYCLE.md` | The first credential | **Conclusion recorded.** Mechanism for SS-20 |
| CR-2 provisioning record with `recovery_source` | same | The first credential | **Conclusion recorded.** Resold-number provenance is a measurement problem |
| CR-3 no credential value in argv, a tracked file, or a log | same | The first run | **Conclusion recorded.** Carries the measured toutatis `-s` finding |
| CR-4 credentials only in ISOLATED | same | The first credential | **Conclusion recorded.** Restates EG-4 where an implementer reads it |
| CR-5 one run per persona, daily budget | same | The first run | **Conclusion recorded.** Refuses rather than queues |
| CR-6 quarantine needs a written exit criterion | same | The first quarantine | **Conclusion recorded.** Closes the SS-13 gap |
| CR-7 burn rather than reuse, recorded as a finding | same | The first burn | **Conclusion recorded.** A burn is stratum-3 capability evidence |
| CR-8 an empty pool stops rather than degrades | same | The first empty pool | **Conclusion recorded.** Rendered as its consequence |
| HY-1 every gate run recorded, never the offending value | `doctrine/HYGIENE.md` | The first gate run | **Conclusion recorded.** Advisory, Class A. The fixed field tuple is the mechanism |
| HY-2 both failure directions adjudicated | same | The first telemetry review | **Conclusion recorded.** Thresholds deliberately non-numeric with one contributor |
| HY-3 retiring or loosening a gate needs a written reason | same | The first retirement | **Conclusion recorded.** Quiet deletion is the easiest drift here |
| HY-4 gates adjudicated and kept are recorded too | same | The first review | **Conclusion recorded.** Recording only failures removes the baseline |

**Four of these have a date after which they cannot be made:** RT-1 before the
first write, RT-4 before the first blob, RT-7 before the index is designed, and
RT-15 before the first commit containing a cassette. The rest can be stamped
later at a cost.

**Not stampable, and deliberately absent from this table.** SS-14 item 6's
machine condition, `preflight` green in the runner process at startup, is a
mechanism rather than a document. It has no row here because a stamp is not what
makes it true.

## Assistant readings awaiting confirmation

| Marker | Reading | Raised |
|---|---|---|
| **S7-R1** to **S7-R7** | **Seven readings the Step 7 generator took where `spec/layer-model.yaml` is silent**, listed in `spec/pse-semantics-contract.md` section 13.1 and written into the generated schema's `$comment` and `policy/semantics.yaml` under `readings`. The consequential one is S7-R1, the rule deciding which optional payload fields a subtype may carry; its cost is visible per subtype in `policy/semantics.yaml` under `allowed`, and the remedy, if the operator wants a tighter shape, is an optional list per subtype in the model. Reversing any of the seven is an edit to `tools/generate_pse.py` and a regeneration, never a hand edit to a generated file | 2026-09-08 |
| **AR-1** | **Publishing a roster of accounts carrying injection payloads would be publishing accusations this system cannot verify.** The operator raised publication as a possible public good and marked it a later decision. The argument to weigh first is the program's own: SS-18 establishes that precision is not computable against an S4 subject, because confirming a claim requires an oracle and the analyst's judgment is the system's own output re-entered as ground truth. A published list therefore carries a false-positive rate that is unknown by construction, and each false positive is a public accusation against an identifiable party who has no way to contest it. The defensive value the operator wants is carried better by the payload-family finding under SS-21, which generalizes to accounts nobody has seen and names nobody. If publication is still wanted, the honest form publishes signatures rather than accounts. Recorded rather than decided; the operator may confirm, amend, or refuse this reading | 2026-08-27 |

## Rejected readings, do not re-derive

Recorded so a settled question is not reopened by someone reading the same
evidence and reaching the same wrong conclusion.

| Reading | Why it was rejected | Date |
|---|---|---|
| PSE should emit valid `zmeta_version: "1.0"` | Tested against the shipped schema. `payload.modality` and `event_subtype` are closed enums with no legal token for an HTTP or API observation, and minting one creates the private dialect `ZMeta/zmeta-spec/AGENTS.md` forbids while claiming compatibility. | 2026-08-26 |
| ZMeta is geospatially biased and therefore unfit | False. None of the four required top-level fields is spatial, `InferencePayload` has no geo field, and positionless observation is a shipped tested case in the ADS-B adapter. The fit problem is vocabulary, not geometry. | 2026-08-26 |
| Retention alone bounds the harm of collection | Deleting a profile does not un-collect it, and the platform-side record of the collection is outside every mechanism in this repository. Subject selection is the upstream control. | 2026-08-26 |
