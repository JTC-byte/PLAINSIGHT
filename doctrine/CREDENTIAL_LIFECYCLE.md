# Credential lifecycle: the accounts that do the looking

**Status: DRAFTED 2026-08-27. ALL CONCLUSIONS RECORDED. Landed in commit `4c5cd25` on 2026-08-27.**

`docs/THE-GAMEPLAN.md` §2.2 deferred this file until the credential pool had a
real shape. SS-20 gave it one on 2026-08-27 by separating the accounts that
collect from the accounts that are collected on, so the trigger has fired.

Rank 1 alongside `SUBJECT_SELECTION.md`, `RETENTION.md` and `EGRESS.md`. The
justification is narrow: whose account performs a collection determines which
identity a third party permanently records as having looked at a person, and that
is a subject-selection consequence rather than an operations detail.

This document has no opinion on schema shape. Where it names a field or a state
it is naming an enforcement point rather than specifying a data model, and which
values are permitted is the rank-1 half because CR-8's stop keys on one of
them.

Landed 2026-08-27 in commit `4c5cd25`, authored by the operator. Per R6 as
amended the conclusions are in force, and every basis is unstamped.

---

## 1. The population this file governs

A **collection persona** is an account the team holds, used to authenticate to a
platform so a connector can read. Under R7 that authentication is a read and is
permitted. Most of the audited connectors cannot run without one: toutatis needs
an Instagram session, informer needs a Telegram account, the Discord tooling
needs a Discord account.

**CR-1. A collection persona is never a subject, and the two populations are
disjoint by check rather than by intention.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

The full argument is in `SUBJECT_SELECTION.md` SS-20 and is not repeated. The
mechanism lives here: `tools/validate_authorization.py` compares the credential
pool against `synthetic/CAST.md` and refuses on any intersection, **including a
shared recovery selector**, which is the case a comparison on handles alone would
miss. A shared recovery phone between a collection persona and a cast persona is
an intersection even though no handle matches.

**CR-2. Every credential carries a provisioning record.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

| Field | Answers |
|---|---|
| `credential_id` | The opaque handle lineage refers to. Never the value |
| `platform` | Which service |
| `persona` | Which collection persona, by opaque id |
| `recovery_source` | How the number and address were obtained, so provenance is knowable later |
| `created_on` | The date, because acceptance behaviour and account age both matter |
| `environment` | Which environment holds it. Always ISOLATED, per EG-4 |
| `state` | `active`, `quarantined`, or `burned` |

`recovery_source` exists because of a measurement problem rather than a
bookkeeping one. A resold number from a verification service may already carry
correlations nobody designed, and a pool whose provenance is unrecorded cannot be
audited for that later. A credential whose `recovery_source` is unknown is
recorded as unknown rather than guessed.

---

## 2. Handling

**CR-3. A credential value never appears in argv, in a tracked file, or in a
log.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

This carries a measured finding from the tool audit forward. toutatis takes its
session as a command-line parameter, `-s <sessionid>`, which places a live
session token into shell history and into the process list of every user on the
machine. The reimplementation reads it out of band, from a file the process is
given rather than from its command line.

`lineage.command_template` records `{credential_ref}` and the run records the
`credential_id`. The value is supplied out of band and renders redacted in every
view and every export, which the design already specifies as `▮▮▮▮▮`.

**CR-4. Credentials live only in ISOLATED.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

Enforces `EGRESS.md` EG-4, restated because this is the file an implementer
reads when handling one. The phrasing is the one `tools/validate_doctrine.py`
parses, so the pair is reconciled by the D-01 check rather than by a reader. A credential on LOCAL is within reach of a development machine's
shell history, editor state, crash dumps and backups, none of which the sweep
reaches.

**CR-5. Concurrency is one run per persona, and each persona has a daily
budget.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

Two runs sharing a session concurrently is the pattern platforms flag first. One
single-holder lock per persona, and a per-persona daily job budget that refuses
rather than queues when exhausted, so exhaustion is visible at the moment it
happens rather than as unexplained slowness. Which lock and which number are
rank-3 questions; that exhaustion refuses rather than slows is this file's.

---

## 3. Quarantine and burn

**CR-6. `quarantine_credential` requires a written exit criterion at the moment
it is set.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

The design has `quarantine_credential: true` with no lifecycle, which SS-13
already names as a gap. A quarantine with no exit criterion either lasts forever
or ends when somebody notices, and neither is a decision.

The criterion is written when the quarantine is set, by the person setting it,
and it names the observable condition that would clear it. The runner refuses to
set a quarantine without one, which makes this a field rather than a habit.

**CR-7. A credential that trips platform enforcement is burned, not reused, and
the burn is recorded as evidence about the connector.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

Reusing a flagged credential teaches the platform that the accounts are related,
which is the correlation this whole separation exists to avoid.

The recording half matters more than the burn. **A burn is a capability finding**:
it says that this connector, at this rate, against this platform, at this account
age, gets caught. That is stratum 3, it carries no subject values, and it
survives every shred. A pool that loses credentials without recording why
produces a program that keeps rediscovering the same rate limit.

**CR-8. Losing the pool is a stop, not a degradation.**
*[Conclusion recorded 2026-08-27 by the operator. Basis: unstamped.]*

When no active credential exists for a platform, that platform's connectors
render as their consequence rather than returning empty:

```
▨ NO ACTIVE CREDENTIAL for Instagram · this connector did not run · absence here is not evidence
```

This is `../ZISR COP/docs/OPERATIONAL_CONTRACT.md` §4's rule applied to the
credential pool, the same rule RT-12 applies to the sweep heartbeat. A
connector that cannot authenticate and returns zero results looks exactly like a
connector that ran and found nothing, and the second reading is the one that
produces a false negative in an assessment.

---

## 4. What is explicitly NOT gated

- How many personas exist, on which platforms, or how they were provisioned.
  That is an operator judgment constrained by platform acceptance rather than by
  this document.
- Running against S0, S1 and S2 subjects with whatever pool exists, inside the
  per-persona concurrency and budget CR-5 sets.
- Rotating, retiring or adding personas at any time, provided CR-1's
  disjointness check still passes.

---

## 5. Ratification table

| Item | Subject | Must precede | Related |
|---|---|---|---|
| CR-1 | Disjoint from the cast, recovery selectors included | The first credential | SS-20 |
| CR-2 | Provisioning record, `recovery_source` included | The first credential | none |
| CR-3 | No credential value in argv, a tracked file, or a log | The first run | RT-15 |
| CR-4 | Credentials only in ISOLATED | The first credential | EG-4 |
| CR-5 | One run per persona, daily budget | The first run | none |
| CR-6 | Quarantine needs a written exit criterion | The first quarantine | SS-13 |
| CR-7 | Burn rather than reuse, and record it as a finding | The first burn | none |
| CR-8 | An empty pool stops rather than degrades | The first empty pool | RT-12 |
