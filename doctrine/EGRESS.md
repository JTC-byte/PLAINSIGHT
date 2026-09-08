# Egress doctrine: the two environments, and what crosses between them

**Status: DRAFTED 2026-08-27. ALL CONCLUSIONS RECORDED. Landed in commit `4c5cd25` on 2026-08-27.**

`docs/THE-GAMEPLAN.md` §2.2 deferred this file until the deployment decision was
made. The operator made it on 2026-08-27: code work stays local, anything live
runs in an isolated environment, and the case store lives on the isolated side.
That trigger has fired and this file replaces the `egress` field standing in for
it.

Rank 1 alongside `SUBJECT_SELECTION.md` and `RETENTION.md`, because this document
answers the third of doctrine's three questions: what leaves the machine. It has
no opinion on which hypervisor, which provider, or how the link is built.

Landed 2026-08-27 in commit `4c5cd25`, authored by the operator. Per R6 as
amended the conclusions are in force, and every basis is unstamped.

---

## 1. Why compartmentalization is a doctrine question

The obvious reason is the weaker one. Separating research infrastructure from a
personal machine limits what a mistake can reach, and that is ordinary hygiene.

The reason it is rank 1 is different. **Every mechanism in `RETENTION.md`
governs one store, and the shred is only meaningful if that store is the only
place case material exists.** A copy on a second machine is a copy the sweep does
not reach, `verify_shred` does not check, and the receipt does not cover. The
deployment decision therefore decides whether retention is a mechanism or a
mechanism plus an exception, and there is no third option.

**Two things this doctrine does not claim.** The first is a residual EG-3
creates and does not name: an interface on LOCAL that reads across the boundary
holds an authenticated read channel into the case store for the life of a
session, so a LOCAL compromise during a session reaches whatever that session can
read. EG-3 bounds what persists afterwards and does not bound what is seen
during. Hardening the machine on either side is an operator act, outside this
document on the same reasoning that keeps the hypervisor out of it.

The second is anonymity. The isolated environment is not an anonymity
boundary. Its egress identity differs from the operator's home
connection, and that reduces cross-contamination between research activity and
personal accounts. It does not make collection unattributable, and a dedicated
egress address would make the research population *more* correlatable rather than
less, because a static address unique to one account links every persona behind
it. SS-13 states the governing fact: the platform's record of our collection sits
outside every mechanism here, and the only control over it is not collecting.
Compartmentalization is about blast radius, not about hiding.

---

## 2. The two environments

**EG-1. There are two environments and the boundary between them is which one
may execute a connector.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

| | **LOCAL** | **ISOLATED** |
|---|---|---|
| Holds | Code, spec, schema, policy, doctrine, fixtures, the synthetic corpus | The case store, the credential pool, the runner, the sweep |
| Executes | Validators, tests, the harness against cassettes | Connectors against live platforms |
| Reaches | No third-party platform through a connector | Third-party platforms |
| Case material | **Never** | Always |

LOCAL is a development machine. ISOLATED is whatever the operator stands up for
it, a virtual machine or an isolated browser environment, and this document does
not name the technology because the boundary is the governed thing rather than
the implementation.

**EG-2. The case store lives in ISOLATED. No stratum-0 or stratum-1 object
crosses to LOCAL.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

Raw capture, items, extracts, claims, message rows, the full-text index, the
authorization record, and DRAFT exports all live where collection happens. The
per-case keys live there. `runner/retention_sweep.py` and `runner/verify_shred.py`
run there.

This is the criterion that makes the rest of retention true. RT-4 requires
per-case encryption from the first blob and says it cannot be retrofitted at any
cost; **EG-2 has the same property for the same reason.** A store that starts on
LOCAL and moves later leaves the original copy behind in snapshots, backups and
file history that no later decision reaches.

**EG-3. The analyst interface reads across the boundary. It does not copy across
it.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

The consequence of EG-2 that is easy to get wrong. An interface that fetches a
case to render it locally has moved case material to LOCAL, and the boundary is
then decorative. Rendering happens against the store, and what reaches the
operator's screen is a view rather than a copy.

A local cache of rendered case content is a stratum-1 object on the wrong side of
the boundary. `conformance/` carries the fixture asserting that no case material
persists on LOCAL after a session closes.

**EG-4. The credential pool never exists on LOCAL.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

Enforced in `CREDENTIAL_LIFECYCLE.md` CR-4, which is where an implementer
handling a credential reads it.

Session tokens, cookies, API keys and persona passwords live in ISOLATED and are
drawn there. A credential on LOCAL is a credential in reach of a development
machine's shell history, editor state, crash dumps and backups. Detailed in
`doctrine/CREDENTIAL_LIFECYCLE.md`.

---

## 3. What crosses outward, and what does not

**EG-5. Three strata cross outward. Two do not, and the exception is named.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

| Stratum | Crosses to LOCAL | Why |
|---|---|---|
| 0 Raw capture | No | Verbatim subject values |
| 1 Case material | No | Derived subject values. RT-18 disclosure export is the one exception, and it goes to an agency rather than to LOCAL |
| 2 Skeleton | Yes | No subject values. This is what makes the record of an experiment auditable from the development side |
| 3 Findings | Yes | The program's actual product |
| 4 Synthetic corpus | Both directions | Synthetic only. Cassettes are captured in ISOLATED and committed from LOCAL |

Stratum 4 crossing in both directions is deliberate and is the one flow worth
watching. A cassette is captured against a live platform in ISOLATED and then
committed to git from LOCAL, which is exactly the path RT-15 governs: **a
cassette captured against anything other than an S2 or N0 target must not make
that crossing**, because git is the store a crypto-shred cannot reach.

**RT-15's mechanism is the pre-commit scan and that scan is currently the D-001
stub**, which this criterion states rather than borrowing. The prohibition above
is a rule an author follows until Step 8 writes the check. RT-1 reaches the same
conclusion from the capture side, that a live-subject cassette is stratum 0 and
is not a thing this system keeps, so the artifact this crossing would refuse is
one the corpus already forbids at capture.

**EG-6. Every run records the environment it executed from, and a run from the
wrong environment is refused rather than logged.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

`egress` is a required stratum-2 field on every run from day one, naming the
environment and its egress identity at the time of the run. That was the
stand-in this file replaces, and it survives as the mechanism.

Refusal rather than annotation, because a run that already reached a platform
cannot be un-run. `preflight` checks the environment identity at runner startup
and its failure is fatal, which is the same shape SS-14 item 6 already requires.
`conformance/gate/` carries the fixture: a runner started on LOCAL with a live
connector manifest, asserted refused.

---

## 4. What is explicitly NOT gated

- Developing, testing and validating everything against cassettes and the
  synthetic corpus on LOCAL, at any depth. The whole conformance ladder runs
  there.
- Reading and adjudicating a case from LOCAL through the interface. What is
  forbidden is the copy, not the work.
- Every finding, scorecard and skeleton record crossing outward, which is the
  program's product and the reason the boundary is worth having.

---

## 5. Ratification table

| Item | Subject | Must precede | Related |
|---|---|---|---|
| EG-1 | Two environments, execution is the boundary | The first live run | none |
| EG-2 | The store lives in ISOLATED | **The first blob** | RT-4 |
| EG-3 | The interface reads, never copies | The interface | none |
| EG-4 | No credentials on LOCAL | The first credential | CR-5 |
| EG-5 | Three strata cross outward | The first export | RT-18, RT-15 |
| EG-6 | `egress` recorded, wrong environment refused | The first run | SS-14 |

**EG-2 has no later date on which it can be decided**, on exactly the same
argument as RT-4. The other five can be stamped later at a cost.
