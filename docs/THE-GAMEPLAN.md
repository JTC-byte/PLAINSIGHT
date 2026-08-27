# THE GAMEPLAN
## PLAINSIGHT + PSE — from four loose documents to a governed repository, in order, starting today

**Status: DRAFT 2026-08-26. Nothing here is operator-ratified.** Sections 3, 4, and 5 contain recommendations, not records. Every item marked BLOCKED names the person who decides, and that person is the operator in every case.

This plan was written against the actual files. Where it quotes, the quote is exact and the path is given.

---

# 1. What we are building

Two products, one repository, two lanes.

**PLAINSIGHT** is an OSINT common operating plane: one surface that consolidates person-centric OSINT tools, standardizes their input and output, automates the pivots between them, and puts an analyst in front of the result with a working citation chain. Its design of record is `<Z-ISR>/PLAINSIGHT-design.md`, 1,088 lines, already written. Its central claim is stated in that file's §1: every sentence in an assessment "walks back through a cluster, through rationale claims, through items, through a run, to argv and raw bytes. The chain is the product."

**PSE** (PLAINSIGHT Semantic Envelope) is a ZMeta-derived semantic dialect for person-centric OSINT. It is a data standard: an event envelope, a closed selector ontology, a policy pack, a conformance corpus, and the validators that enforce all of it. PSE exists because ZMeta cannot carry this data honestly. `PLAINSIGHT-FOUNDATION.md` D1 established why, and the finding worth repeating is the narrowness of the problem: "ZMeta is the wrong carrier only because its observation vocabulary is locked and closed. That is a narrow, fixable-by-fork problem, and it means the fork keeps almost everything."

PSE is a private dialect. `ZMeta/zmeta-spec/AGENTS.md` licenses exactly this, on one condition: "If you change those surfaces locally, treat the result as a private fork or dialect. Do not claim upstream compatibility unless the change has versioning, documentation, conformance evidence, and release governance." The four conditions in that sentence are the reason sections 2 and 3 below look the way they do.

## 1.1 The relationship between the two, stated once

ZMeta's repository holds a standard plus a reference implementation whose job is to demonstrate the standard. This repository inverts that. PLAINSIGHT is the product; PSE exists to serve it. The rule that keeps the inversion from becoming drift:

> **PSE defines what may be said. PLAINSIGHT defines how it is shown. Each is authoritative in its own lane and subordinate across lanes.**
>
> When the application needs a fact the envelope cannot carry, three moves are forbidden: adding a field to the envelope locally, widening an existing field's meaning to fit, and carrying the fact in free text. The available moves are a Class D change against the spec, or doing without.

## 1.2 Repo shape

One repository, `plainsight/`, sitting beside `ZMeta/` and `zisr-recon/` under `Z-ISR/`. One repository rather than two because there is one author, and splitting a spec from its only implementation at v0.1 buys a version pin and nothing else. **Split trigger, recorded now so the split is not a judgment call later: a second implementation of PSE exists, or PSE is published outside the team.**

The lane boundary is a directory boundary with one enforced rule: nothing under `spec/`, `schema/`, `ontology/`, `policy/`, or `tools/` may import from `app/`. The reverse is permitted.

```
plainsight/
├── CLAUDE.md                              advisory orientation, gates, voice
├── AGENTS.md                              normative operating model, change classes, execution limits
├── CONFORMANCE.md                         the not-ZMeta claim; what a connector conformance claim is
├── CHANGELOG.md
├── README.md
├── Makefile                               validate-kernel · validate-manifest · prove · preflight · audit
│
├── doctrine/                              rank 1. human-ratified, per item.
│   ├── SUBJECT_SELECTION.md               who may be a subject
│   ├── RETENTION.md                       strata, TTL, shred, verification, disclosure
│   ├── HYGIENE.md                         housekeeping, staleness, rejected reasoning, cadence
│   ├── DOCTRINE_STATUS.md                 the ratification pin of record
│   └── RETENTION_LEDGER.md                case registry + shred receipts
│
├── spec/
│   ├── pse-semantics-contract.md          the normative authority
│   ├── layer-model.yaml                   single source for event types + per-type rules
│   ├── divergence-register.yaml           machine-readable, normative
│   └── divergence-register.md             GENERATED. never hand-edited.
│
├── schema/
│   ├── pse-event-0.1.schema.json
│   ├── connector-manifest.schema.json
│   └── subject-authorization.schema.json
│
├── ontology/
│   └── selectors.yaml                     the closed selector vocabulary (D2)
│
├── policy/
│   ├── semantics.yaml                     recursive per-type payload denylists
│   ├── lineage.yaml                       typed parents, subset rule, collect_evidence
│   ├── producer-authority.yaml            who may emit what; no wildcard for identity
│   ├── subject-authorization.yaml         the subject doctrine, compiled
│   ├── retention.yaml                     the retention doctrine, compiled
│   └── violation-codes.yaml               governed diagnostic vocabulary
│
├── conformance/
│   ├── must-pass.jsonl
│   ├── must-fail.jsonl
│   ├── gate/{must-pass,must-fail}.jsonl   subject-gate decision fixtures
│   ├── connector-harness/
│   │   ├── fixture.schema.json
│   │   └── must-pass.jsonl
│   └── retention/shred-roundtrip.yaml
│
├── tools/
│   ├── validate.py                        schema + policy over a JSONL corpus
│   ├── validate_ontology.py               registry lint · corpus coverage
│   ├── validate_manifest.py               one connector manifest
│   ├── validate_connector_conformance.py  calls the adapter with cassettes
│   ├── validate_authorization.py          --fixtures and --dispatch-paths
│   ├── validate_retention.py              policy · strata · shred round-trip · repo scan · finding scan
│   ├── validate_divergence_register.py    six checks, derived from the schema diff
│   ├── validate_conformance.py            the aggregator. --kernel-gate.
│   ├── validate_hygiene.py                doc claims, stamps, four-way inventory reconcile
│   └── render_divergence_register.py      yaml -> md
│
├── synthetic/
│   ├── CAST.md                            the designed link graph
│   └── GROUND_TRUTH.yaml                  sealed, hash-pinned, read only by the scorer
│
├── connectors/                            empty at v0.1
│   └── <id>/{manifest.yaml,adapter.py,cassettes/,fixtures.jsonl,tests/}
│
├── runner/                                empty at v0.1
│   ├── subject_guard.py                   the D5 gate
│   ├── dispatch_allowlist.yaml            sanctioned dispatch entry points
│   ├── retention_sweep.py                 the job that acts on retain_until
│   └── verify_shred.py                    four checks, from outside the shredding tool
│
├── app/                                   empty at v0.1
│
├── docs/
│   ├── DOCUMENT_STANDARD.md               moved in unchanged
│   ├── PLAINSIGHT-design.md               moved in. application design of record.
│   ├── PLAINSIGHT-FOUNDATION.md           moved in. ratified decision record.
│   ├── OSINT-COP-tool-review.md           moved in. capability salvage list.
│   ├── plainsight_worklog.md              chronological, never restyled
│   └── plainsight_handoff.md              current state, rewritten every wave
│
└── .githooks/pre-commit                   runs validate_retention.py --repo-scan
```

## 1.3 Authority order

Written into `CLAUDE.md` and repeated normatively in `AGENTS.md`. When two governed sources conflict, the higher number loses.

**Preamble.** Statutory obligations, platform terms of service, and any commitment the operator has made outside this repository sit above every document in it. No file here grants an authority the operator does not already hold.

1. `doctrine/SUBJECT_SELECTION.md`, `doctrine/RETENTION.md` (normative, per-item human-ratified)
2. `spec/pse-semantics-contract.md`
3. `schema/*.json`, `ontology/selectors.yaml`, `policy/*.yaml`, `spec/layer-model.yaml`, `spec/divergence-register.yaml`
4. `AGENTS.md`
5. `CONFORMANCE.md`
6. Validators and tests in `tools/` and `connectors/*/tests/`
7. `docs/PLAINSIGHT-design.md` and `docs/PLAINSIGHT-FOUNDATION.md`
8. `CLAUDE.md`, `docs/DOCUMENT_STANDARD.md`, `README.md`, worklog, handoff, connector READMEs

**Why doctrine outranks the semantic contract, argued rather than asserted.** ZMeta puts `spec/semantics-contract.md` at rank 1 because in ZMeta every failure mode is a failure of meaning. This repository has a failure mode the contract cannot see. A PSE event that is schema-valid, ontology-clean, correctly layered, honestly timed, and fully lineaged, describing a person who was never permitted to be a subject, passes every check at ranks 2 through 6 and is still the thing this project must not do. No validator can catch it, because no validator knows who a selector refers to. A rule that no rank below it can evaluate has to sit above them all.

The inverse bounds the doctrine and belongs in the same paragraph. Doctrine is authoritative only on who may be a subject, what may be retained, and what may leave. It has no opinion on field names, layer boundaries, or UI. A doctrine document that starts adjudicating schema questions has escaped its lane and gets cut back.

---

# 2. The artifact register

Change classes are ZMeta's, from `ZMeta/zmeta-spec/docs/zmeta_change_governance.md` §Change Classes: **A** advisory documentation, **B** governed baseline, **C** runtime or reference implementation, **D** versioned semantic branch, **E** release publication. PSE adds one:

> **Class F — Authority.** Any change that alters who may be a subject, what may be collected, how long anything is held, or what may leave the machine. Requires the operator's explicit per-item ratification with a dated stamp. An agent may draft a Class F change and may never land one. **Class F is defined by effect, not by path**: the reviewer's question is "after this change, is there any subject, any bystander, any pivot depth, or any retained byte that was previously refused and is now permitted?" A one-line YAML edit that adds an allowlist entry is Class F.

Rule for every class: **a change carries the highest class it touches.**

## 2.1 v0.1 — the set that must exist

| Path | Job | N/A | Class | Blocks if absent | Depends on |
|---|---|---|---|---|---|
| `doctrine/SUBJECT_SELECTION.md` | Defines who may be a subject, what evidence authorizes it, what the gate returns | Normative | F | **Every collection run.** `subject_guard` has no criteria to read | none |
| `doctrine/RETENTION.md` | Object strata, TTL, shred unit, verification, export/disclosure rules | Normative | F | **The first blob and the first row.** Unencrypted blobs cannot be retroactively crypto-shredded (D4) | R1, R2, R3, R5 |
| `doctrine/DOCTRINE_STATUS.md` | The ratification pin of record: item, date, ratifier | Normative | F | Ratification tracking. Without it a document half-stamps itself | none |
| `doctrine/RETENTION_LEDGER.md` | Case registry: opaque case id, class, purpose, `retain_until`, state, receipt hash | Normative | F | Reconciliation. A shred with no receipt row did not happen | RETENTION |
| `doctrine/HYGIENE.md` | Housekeeping obligations, staleness detection, rejected-reasoning discipline, cadence | Advisory | A | Nothing immediately. Its absence shows up at month four as drift in both directions | worklog, handoff |
| `AGENTS.md` | Normative operating model: change classes A–F, execution limits, required local workflow, documentation matrix | Normative | A | Any agent-assisted work. Everything else is advisory without it | doctrine |
| `CLAUDE.md` | Advisory orientation: North Star, authority order, eight design gates, voice, attribution | Advisory | A | Nothing hard. Its absence produces drift, not violation | AGENTS.md |
| `CONFORMANCE.md` | The honest negative claim (PSE is not ZMeta), and what a connector conformance claim contains | Advisory | A | Connector onboarding; the honesty of any external statement about ZMeta | AGENTS.md |
| `spec/pse-semantics-contract.md` | The authority every other surface preserves. 13 sections against ZMeta's 24 | Normative | B | Everything. Without it the schema is the spec | D1, D6, layer-model |
| `spec/layer-model.yaml` | Single source for event types, subtypes, discriminators, per-type required/prohibited/denylist | Normative | B | Schema and policy enums drift within two releases | D6 |
| `spec/divergence-register.yaml` | Every place PSE departs from ZMeta, with disposition, rationale, mechanism preserved, test ref | Normative | B | D1 is undocumented. In eighteen months nobody can map the two models | contract, schema |
| `spec/divergence-register.md` | Human-readable rendering. **Generated. Never hand-edited.** | Advisory | A | Nothing | register yaml |
| `schema/pse-event-0.1.schema.json` | Structural validation of the envelope | Normative | B | No machine check on shape | layer-model |
| `schema/connector-manifest.schema.json` | Structural validation of a connector manifest | Normative | B | Connector registration | ontology |
| `schema/subject-authorization.schema.json` | The authorization record. Partial is refused, not half-honoured | Normative | F | `subject_guard` has nothing to read | SUBJECT_SELECTION |
| `ontology/selectors.yaml` | The closed selector vocabulary: form, datum class, stability, anchor eligibility, matcher, prohibitions | Normative | B | D2 in its entirety. Without it every connector invents field names | D2, contract §9 |
| `policy/semantics.yaml` | Per-event-type **recursive** payload denylists and discriminator matches | Normative | B | Layer separation is prose. A hint rides in an observed-value payload | contract, layer-model |
| `policy/lineage.yaml` | Typed parents, `based_on` subset rule, unresolved handling, authorization-parent requirement | Normative | B | Authorization is untraceable; pivot chains cannot be walked | contract, ontology |
| `policy/producer-authority.yaml` | Which producer may emit which type. No wildcard for identity assertions | Normative | B | A connector can mint a cluster. Design §8.2 item 4 becomes unenforceable | contract |
| `policy/subject-authorization.yaml` | The subject doctrine compiled: classes, evidence, expiry, gate values, bystanders, absolute prohibitions | Normative | F | The runner has nothing to enforce. **No run may execute before this exists** | SUBJECT_SELECTION |
| `policy/retention.yaml` | `retain_until` defaults per class, extension requirements, shred verification, skeleton | Normative | F | D4 is a sentence | RETENTION, R1–R3, R5 |
| `policy/violation-codes.yaml` | Governed diagnostic vocabulary with severity, `since`, `status`. Append-only | Normative | B | Diagnostics become free text | contract |
| `conformance/must-pass.jsonl` | One clean event per type, one full lineage chain. ~12 lines, all synthetic | Normative | B | The spec is unverified prose | schema, policy |
| `conformance/must-fail.jsonl` | One per denylist entry, per layer collapse, per D2 prohibition. 14 named in §2.3 | Normative | B | The prohibitions are untested and therefore not real | schema, policy |
| `conformance/gate/*.jsonl` | Subject-gate decision fixtures: seed, one-hop, three-hop drift, expired, NEVER, bystander | Normative | F | The gate is unfalsifiable | policy/subject-authorization |
| `conformance/connector-harness/fixture.schema.json` | Lints every harness fixture. **`event_count` required whenever `result: events`** | Normative | B | A refusing adapter satisfies every expectation vacuously | none |
| `conformance/retention/shred-roundtrip.yaml` | The ephemeral-case create/encrypt/shred/verify round trip | Normative | F | The shred mechanism is unexercised | policy/retention |
| `tools/validate.py` | Schema plus policy over a JSONL corpus. `--strict` | Tooling | C | Rung 2 of the ladder. Everything | schema, policy |
| `tools/validate_ontology.py` | Registry self-lint and corpus selector coverage | Tooling | C | Rung 3. D2 is unenforced | ontology |
| `tools/validate_manifest.py` | One manifest: shape gate, registry agreement, canaries, refusal fixtures, targeting, canary subject class | Tooling | C | Connector registration | manifest schema, ontology |
| `tools/validate_connector_conformance.py` | Calls the adapter with cassettes and fixtures, including `event_count: 0` | Tooling | C | Rung 4. Every manifest claim is unfalsifiable | fixture schema |
| `tools/validate_authorization.py` | `--fixtures` proves the gate refuses; `--dispatch-paths` proves nothing bypasses it | Tooling | F | **Any collection run.** This is the D5 mechanism | policy, gate fixtures |
| `tools/validate_retention.py` | Policy well-formedness, strata, shred round-trip, `--repo-scan`, `--finding` | Tooling | F | D4 becomes a sentence with no code behind it | policy/retention |
| `tools/validate_divergence_register.py` | Six checks. Derives the required entry list from the schema diff | Tooling | B | The register goes stale within two releases | register yaml |
| `tools/validate_conformance.py` | The aggregator. `--kernel-gate` expands in one place | Tooling | B | Nothing regresses silently | all validators |
| `tools/validate_doctrine.py` | Criterion definitions, per-criterion stamps, cross-references both directions, reconciliation against the pin of record, prose counts | Tooling | C | The doctrine corpus is checked by hand. Added 2026-08-27 | doctrine |
| `tools/validate_hygiene.py` | Re-derives every cited count and `file:line`; reconciles five inventories both directions | Tooling | C | HYGIENE.md is a checklist, and checklists rot | HYGIENE |
| `tools/render_divergence_register.py` | yaml to md | Tooling | C | Nothing | register yaml |
| `runner/subject_guard.py` | The three-valued gate, on the dispatch path, before argv and before a credential is drawn | Normative | F | **The runner.** Do not build argv construction before this exists | policy/subject-authorization |
| `runner/dispatch_allowlist.yaml` | The sanctioned dispatch entry points `--dispatch-paths` checks against | Normative | F | The bypass check has nothing to compare | subject_guard |
| `runner/retention_sweep.py` | The scheduled job that acts on `retain_until` and writes a heartbeat | Normative | F | Nothing, and that is the point. Its absence is invisible until day 31 | policy/retention |
| `runner/reconcile_ledger.py` | Bidirectional diff of `RETENTION_LEDGER.md` against storage, with a heartbeat | Normative | F | Reconciliation is a cadence bullet with nothing scheduled behind it. Added 2026-08-27 when RT-10 named it and no register row existed | RETENTION_LEDGER |
| `runner/verify_shred.py` | Four checks plus the anti-overreach check, run outside the shredding tool | Normative | F | Any honest claim that data was deleted | retention_sweep |
| `synthetic/CAST.md` | The designed link graph, the confuser pairs, isolation and attribution rules | Normative | F | All precision and recall measurement | SUBJECT_SELECTION |
| `synthetic/GROUND_TRUTH.yaml` | The sealed truth partition. Hash-pinned. Read only by the scorer | Normative | F | Scoring. Nothing can be graded | CAST.md |
| `docs/DOCUMENT_STANDARD.md` | The LEDE standard for published briefings. **Exists. Moves in unchanged** | Advisory | A | Published briefings only | none |
| `docs/PLAINSIGHT-design.md` | Application design of record. **Exists. Moves in unchanged** | Advisory | A | Nothing hard; it is rank 7 | none |
| `docs/PLAINSIGHT-FOUNDATION.md` | Ratified decision record for D1–D5. **Exists. Moves in, stamped** | Advisory | A | D1–D5 have no record | DOCTRINE_STATUS |
| `docs/plainsight_worklog.md` | Chronological record + the D-NNN deferred issue register. Never restyled | Advisory | A | Continuity across sessions | HYGIENE |
| `docs/plainsight_handoff.md` | Current state, decisions due, field-gated items, deferrals. Rewritten every wave | Advisory | A | The next session's first twenty minutes | HYGIENE |
| `.githooks/pre-commit` | Runs `validate_retention.py --repo-scan` before every commit | Normative | F | **Git history is the one store crypto-shred cannot reach** | validate_retention |
| `Makefile` | Four named gates: `validate-kernel`, `validate-manifest`, `prove`, `preflight` | Tooling | C | Nobody runs the same thing twice | tools |
| `.github/workflows/ci.yml` | Runs the kernel gate on push and pull request, proves the hook still executes, refuses agent co-authorship trailers | Tooling | C | A gate nobody runs. Added 2026-08-27 | tools |
| `CHANGELOG.md` | Release notes | Advisory | A | Nothing | none |

**Twelve prose documents written new**, plus four moved in unchanged, plus registers, schemas, policy, fixtures, and tools. The "forty stale documents" warning applies to prose, and the way the count stays low is that every rule that can be a mechanism is written as a mechanism instead of as a paragraph. That is design gate 1 below.

## 2.2 DEFERRED, with the trigger that un-defers each

| Deferred | Stands in until then | Un-defers when |
|---|---|---|
| `docs/pse_change_governance.md` | The change-class list and documentation matrix inline in `AGENTS.md` | A second contributor exists, or the matrix exceeds one screen |
| `CONTRIBUTING.md` | The no-third-party-data clause in `AGENTS.md` Execution Limits | A second contributor exists |
| `IP_POLICY.md`, `TRADEMARK.md`, defensive publication | Nothing | PSE is described to anyone outside the project as a standard others might adopt |
| `spec/versioning.md` | Contract §2 | A second PSE version ships |
| `spec/field-dictionary.md` | The schema plus `spec/layer-model.yaml` | A second author, or a UI author who is not the spec author |
| `spec/extension-registry.{md,yaml}` | Contract §11 as prose; reserved names listed inline | `ontology/selectors.yaml` gains a *proposed but not adopted* state. v0.1's registry is closed and flat |
| `spec/conformance-classes.md`, `conformance/claims/` | The five-rung ladder in `PLAINSIGHT-FOUNDATION.md` §4.4 | A connector is written by someone who cannot ask you a question |
| `policy/matcher-calibration.yaml` + `conformance/ontology/matcher-truth/` | Contract §10's rule that an unscored matcher may not be an identity basis | **Before the first matcher merges.** Hard trigger, not a soft one |
| `policy/adjudication.yaml` (rationale codes) | Free-text rationale, flagged as a known gap | Week 9, before the Merge Sheet ships |
| `policy/freshness.yaml` | The `3 × poll_interval` watchdog rule stated in contract §12 | Week 9, before informer ships |
| `policy/export-release.yaml`, contract §14 in full | One invariant paragraph: only ASSESS events cross the export boundary, and projection may thin, never reinterpret | Week 14, before DRAFT export ships |
| `policy/use-labels.yaml` | The tokens inline in `subject-authorization.yaml` | A third consumer of the token list exists |
| `doctrine/CREDENTIAL_LIFECYCLE.md` | One paragraph in `SUBJECT_SELECTION.md` §credentials | The synthetic cast exists and the credential pool has a real shape |
| `doctrine/DISCLOSURE.md` | A section inside `RETENTION.md` | A second egress path exists (handoff packet plus brief, or any programmatic export) |
| `doctrine/EGRESS.md` | `egress` as a required stratum-2 field on every run from day one | The deployment decision (LOCAL / RUNNER / CLOUD) is made |
| `doctrine/plainsight_audit_playbook.md` | HYGIENE.md's cadence section | The first real after-action review. ZMeta's was "Adopted 2026-07-22 from the R1-11 after-action review", written after the lesson |
| `doctrine/plainsight_doctrine_review_log.md` | Nothing | The first genuine pressure on a doctrine point. An empty pressure log trains everyone to skip it |
| `docs/plainsight_worklog_archive.md` | Nothing | The worklog passes ~1,500 lines |
| `tools/validate_ontology.py --matchers` | Nothing | The first matcher exists. Requires labelled ground truth, which requires the cast |
| Diagnostics: `pse-health`, `pse-retain`, `pse-lineage`, `pse-authz` | The validators, run by hand | Week 5 for `pse-retain`, week 14 for `pse-health`. All four are read-only and **never exit nonzero for a state of the world** |
| `tools/validate_projection.py`, `validate_precision_policy.py`, `validate_encoding_negative.py`, `validate_release_*.py`, `validate_conformance_classes.py` | Nothing | There is no profile thinning, one encoding, no release, and no third-party implementation. Several of these never un-defer |
| Profiles L/M/H, profile precision, compact binary, protobuf, mesh trust, UAS identity, command deconfliction topology, geodesy | Nothing | **Never.** One Postgres, one consumer, no wire budget, no bandwidth axis |
| `CODE_OF_CONDUCT.md`, issue and PR templates | Nothing | Outside contributors exist |

## 2.3 The fourteen must-fail fixtures, named now so they are not negotiated later

The first six fail in the direction where the analyst believes a false thing rather than seeing an error. They are the reason the corpus exists.

| # | Fixture | What it asserts | Code |
|---|---|---|---|
| 1 | `hint-cited-as-email` | An `email_hint_recovery_masked` claim satisfying a citation for `email`. D2's flagship case | `HINT_CITED_AS_VALUE` |
| 2 | `generated-permutation-cited-as-observed` | A CrossLinked `email_generated_permutation` cited as observed with no promotion act | `GENERATED_CITED_AS_OBSERVED` |
| 3 | `account-anchored-on-handle` | An `Account` entity anchored on `handle:instagram/…`. Design §2.2 calls the handle-owner change under handle-anchoring "an identity catastrophe" that renders as ordinary drift | `SELECTOR_ANCHOR_PROHIBITED` |
| 4 | `run-against-unauthorized-subject` | A run whose selector belongs to a person outside the case authorization | `SUBJECT_NOT_AUTHORIZED` |
| 5 | `scope-drift-three-hops` | Three individually-legal pivots whose composition leaves the authorized set. Forces the gate to evaluate the chain, not the hop | `SCOPE_DRIFT_UNADJUDICATED` |
| 6 | `absence-claimed-without-canary` | `attempted_and_absent` rendered as evidence for a field whose `always_present` is not canary-proven. CUT LIST A's "manufactures negative evidence from a YAML typo", as a check | `ABSENCE_CLAIMED_WITHOUT_CANARY` |
| 7 | `extract-carries-confidence` | An observation payload with `confidence` | `EXTRACT_HAS_CONFIDENCE` |
| 8 | `extract-carries-review-state` | D3: adjudication is an appended event, never a column | `EXTRACT_HAS_REVIEW_STATE` |
| 9 | `nested-layer-collapse` | `cluster_id` at `payload.extensions.notes.cluster_id`. Proves the denylist is recursive | `LAYER_COLLAPSE_NESTED` |
| 10 | `unregistered-selector-type` | `selector_type: "gravatar_hash"`. The vocabulary is closed at the corpus boundary, not only at the manifest | `SELECTOR_TYPE_UNREGISTERED` |
| 11 | `cluster-minted-by-connector` | An identity assertion with `producer: "connector-toutatis"`. Fires before any semantic check | `PRODUCER_NOT_ALLOWED` |
| 12 | `link-arrives-accepted` | A proposal with `accepted: true`. Acceptance is a separate human act | `LINK_HAS_ACCEPTANCE` |
| 13 | `extract-no-lineage` | An extract with no probe parent. A claim with no item is uncitable by construction | `LINEAGE_MISSING` |
| 14 | `run-without-purpose-binding` | A run whose case carries no purpose | `CASE_PURPOSE_UNBOUND` |

Two more are added the moment the shapes exist: `cluster-carries-rollup-confidence` and `merge-circularity`.

## 2.4 Two improvements on ZMeta's fixture runner, both worth taking on day one

**`expect_only`.** `ZMeta/zmeta-spec/tools/validate_conformance.py` passes a must-fail fixture when the expected code appears anywhere in the violation list. For most ZMeta fixtures that is fine. For fixtures 1 through 6 above it is not, because those are policy failures that will often be accompanied by incidental schema noise, and a fixture that passes for the wrong reason proves nothing about the guard it was written for. PSE fixtures may set `expect_only: true`, requiring the expected code to be the sole failing code. All D2 and D5 fixtures set it.

**Short-circuit disclosure.** `validate_bad_events.py` returns early on schema violations, so a policy-code fixture that is also schema-invalid never reaches the policy checks and reports the wrong code. PSE's runner records that it short-circuited and fails any fixture whose expected code belongs to a check that was never reached.

---

# 3. The critical path

Each step has a done-condition. Steps marked **BLOCKED** cannot complete without an operator decision; the drafting inside them can still start.

## 3.0 The open decisions, listed once

FOUNDATION D1–D5 are recorded there and are inputs, not open items, once they are stamped (that stamping is Step 2). Eleven items remain open. The operator decides all of them.

| # | Question | Recommendation | Blocks |
|---|---|---|---|
| **D6** | The PSE event-type set: FOUNDATION §4.2's seven, or nine (add `AUTHORIZE_EVENT`, `COLLECT_EVENT`, `ADJUDICATE_EVENT`; merge `CLUSTER`+`EXCLUDE` into `IDENTITY_EVENT`; split `PROBE` into RUN_START/ITEM/RUN_END) | **Nine.** Every addition closes a hole already named in a file on disk. `COLLECT_EVENT` is what makes D5's gate a structural boundary instead of a function call. `ADJUDICATE_EVENT` is the type D3 chose and never named. RUN_START/RUN_END is what append-only requires, since under immutability you cannot fill in `ended` later. The one row I would give up under pressure is `AUTHORIZE_EVENT` folded into `ADJUDICATE_EVENT` as a subtype, and I do not recommend it | Steps 4, 5 |
| **D7** | Version label: `pse-event-0.1` or `pse-event-1.0` | **0.1, and say "Unlocked" in the status header.** ZMeta's 1.0 is Locked, and a matching number will be read as a matching commitment | Steps 4, 5 |
| **D8** | One repo with two lanes, or two repos | **One, with the split trigger recorded** (§1.2) | Step 1 |
| **R1** | The shred unit | **Both layers.** `DROP SCHEMA case_… CASCADE` for everything enumerable, plus destruction of the per-case data key for everything not enumerable: object-store replicas, filesystem snapshots, WAL segments, base backups, page cache. `DROP` reaches what you can enumerate; crypto reaches what you cannot; backups are the canonical thing you cannot | Steps 3, 8 |
| **R2** | Default case TTL and hard ceiling | **30 days default, 30-day extensions, 180-day ceiling** past which the case is re-authorized from a new purpose record | Steps 3, 8 |
| **R3** | Is the full-text index inside the shred boundary? | **Inside.** An FTS index over message bodies is a plaintext copy of them. This costs real performance and design work in STREAM and the cost belongs in the decision, not in a footnote | Steps 3, 8 |
| **R4** | Which subject classes are available at v0.1 | **S0 SELF, S1 CONSENTING, S2 SYNTHETIC only.** S3 PUBLIC FIGURE and S4 ARBITRARY THIRD PARTY defined but refused, with the ratification path named so the refusal is a decision rather than an omission | Steps 2, 6 |
| **R5** | `text: forever` versus the stated posture | **Legal as a within-case blob policy, illegal as a case-level value.** FOUNDATION D4 already reads it this way. It cannot be resolved in `PLAINSIGHT-design.md`, because rank 7 does not set a retention rule. Until it is stamped, the storage layer has two contradictory instructions | Step 3 |
| **R6** | Commit attribution, and Class F authorship | **Keep ZMeta's human-only rule** (`ZMeta/zmeta-spec/CLAUDE.md`: "Do not add `Co-Authored-By` trailers naming Claude"), carry agent involvement in the worklog entry where it can be stated precisely, and add one hard rule: **a Class F commit is authored by the ratifier**, because Class F is the ratification | Step 1 |
| **R7** | The interaction line | Undrafted. FOUNDATION §6 admits the current wording is "my draft, not a ratified rule, and it is blurrier than the line it replaces". The manifest's `interaction_class` enum already depends on it, so every manifest written before it is ratified declares a value against an undefined vocabulary | Step 6, before the first manifest |
| **R8** | Bystander disposition beyond `count_only \| refuse` | Undecided, and it should stay that way. The gate forces the declaration at v0.1; what a `requires_extension` bystander flow looks like is genuinely open | Not blocking v0.1 |

## 3.1 The steps

**Step 1 — Cut the repo and land the governance skeleton.** *Not blocked. Start today.* Spelled out in full in §6.
**Done when:** the tree in §1.2 exists, the four existing documents are moved in unchanged, `CLAUDE.md` and `AGENTS.md` are written, `doctrine/DOCTRINE_STATUS.md` exists with every item marked UNRATIFIED, `.githooks/pre-commit` is installed, and `docs/plainsight_worklog.md` has its first entry.

**Step 2 — Stamp D1 through D5.** **BLOCKED on the operator.** `PLAINSIGHT-FOUNDATION.md` line 4 currently reads "Status: DRAFT 2026-08-26. Nothing here is operator-ratified." Each of the five decisions gets a row in `DOCTRINE_STATUS.md` with a separate stamp for the conclusion and for the basis, following the discipline in `zisr-recon/docs/ENTRY_CRITERIA.md` lines 6–18. Refusing or amending a decision here is cheaper than at any later point.
**Done when:** five rows in `DOCTRINE_STATUS.md` carry a date and a ratifier, and any refused decision has a written replacement.

**Step 3 — Draft `doctrine/RETENTION.md` and `doctrine/SUBJECT_SELECTION.md`.** *Drafting not blocked. Ratification blocked on R1–R5 and R4 respectively.* These two are drafted before any schema work because their decisions are the irreversible ones. Both carry the `ENTRY_CRITERIA.md` header pattern: DRAFTED, AWAITING RATIFICATION, nothing binds until stamped, per criterion.
**Done when:** both files exist with per-item ratification markers, a `## What is explicitly NOT gated` section, and a `[REJECTED READING — DO NOT RE-DERIVE IT]` section that starts empty.

**Step 4 — Open the synthetic cast.** *Not blocked, and it has lead time, which is why it is this early.* Write `synthetic/CAST.md` with a designed link graph of six to nine personas whose true partition is fixed before any collection. Seal `synthetic/GROUND_TRUTH.yaml` and hash-pin it. Create the accounts.
**Done when:** the cast design is written, the truth file is committed and hash-pinned, and at least three personas exist on at least two platforms. **Accounts age. A cast created in week 12 measures the system against a thin target, and thin-target performance is not fat-target performance.** Record persona age in every scorecard so a precision figure is never quoted without the conditions that produced it. Creating platform accounts is an operator act with a platform terms-of-service consequence and possible IP-level attribution; that is an operational risk to the credential pool and it belongs in the decision.

**Step 5 — Write `spec/layer-model.yaml`.** **BLOCKED on D6 and D7.** This is the single source the schema enums and `policy/semantics.yaml` are both generated from. ZMeta restates the same enum in the contract, the schema, the field dictionary, and four policy files; do not inherit that.
**Done when:** every event type, subtype, discriminator, confidence rule, lineage rule, producer authority, required-field list, and payload denylist is in one file, and the schema generator reads it.

**Step 6 — Write `ontology/selectors.yaml`.** **BLOCKED on D2 (stamped in Step 2) and R7 for `interaction_class`.** FOUNDATION §4.1 already carries a substantial draft at lines 233–300.
**Done when:** `tools/validate_ontology.py --registry` passes, and every constraint selector has `may_anchor_entity: false`, a `matcher`, and a `constraint_semantics`.

**Step 7 — Write the schema, the policy pack, and the contract.** **BLOCKED on Steps 5 and 6.** In this order: `schema/pse-event-0.1.schema.json` generated from the layer model, then `policy/{semantics,lineage,producer-authority,violation-codes}.yaml`, then `spec/pse-semantics-contract.md` written last, because the contract explains rules that already exist rather than inventing rules nothing enforces.
**Done when:** `make validate-kernel` is green against `conformance/must-pass.jsonl` and `must-fail.jsonl`.

**Step 8 — Compile the doctrine into policy.** **BLOCKED on Step 3 ratification.** `policy/subject-authorization.yaml`, `policy/retention.yaml`, `schema/subject-authorization.schema.json`, `conformance/gate/*.jsonl`, `conformance/retention/shred-roundtrip.yaml`.
**Done when:** `tools/validate_authorization.py --fixtures` and `tools/validate_retention.py --policy --shred-roundtrip` are both green, including the check that an **unratified** criterion refuses rather than permits.

**Step 9 — Write the divergence register and its validator.** *Not blocked once Step 7 lands.* `spec/divergence-register.yaml` plus `tools/validate_divergence_register.py`. The validator derives the required entry list from a JSON-pointer diff of the two schemas rather than trusting the prose, which is what makes the register non-stale by construction.
**Done when:** every path present in one schema and absent in the other, and every path present in both with a differing type, enum, or required-ness, has a register entry or is listed under `identical:`. Every `INVERT`, `REPLACE`, `DROP`, or `NEW` carries a rationale, a `mechanism_preserved`, and a `test_ref` resolving to a real fixture line. The string "ZMeta-compatible" does not appear anywhere in the tree.

**Step 10 — Build `runner/subject_guard.py` and the dispatch allowlist.** **BLOCKED on Step 8.** Roughly 70 lines, stdlib only, no network, fully testable. Placement is inside the runner, after pivot selection, before argv construction, before a credential is drawn from the pool. Evaluation order puts hard refusals first, unconditionally, with a test proving a present authorization file does not unlock them.
**Done when:** `tools/validate_authorization.py --dispatch-paths` passes, meaning every call site that constructs argv or opens a subscription is reached only through `subject_guard.evaluate()` or is listed in `runner/dispatch_allowlist.yaml` with a reason.

**Step 11 — Build the encrypted blob store, `retention_sweep.py`, and `verify_shred.py`.** **BLOCKED on Step 8.** Encrypted per-case from the first write, `retain_until` as a column, and the sweep scheduled from day one even while it has nothing to delete. A scheduled job that does nothing yet is a mechanism; a comment is not.
**Done when:** the CI test that opens a case with `retain_until` in the past, runs the sweep, and passes all five `verify_shred` checks is green. Until that test is green, the claim that PLAINSIGHT's retention is a mechanism rather than a sentence is not true.

**Step 12 — The manifest schema, the harness, and the first connector.** **BLOCKED on Steps 6, 7, 10.** toutatis first, because it is the `one_shot` shape and because its `email_hint` is the exact D2 case the ontology was written for.
**Done when:** `make prove CONNECTOR=toutatis` passes all five rungs, including a passing known-negative canary and one refusal fixture per schema-required input field.

**Step 13 onward — the spine, per `PLAINSIGHT-design.md` §8.1.** Weeks 1–4 spine, 5–8 triage, 9–13 the picture, 14–18 honesty and handoff. Nothing in that plan changes. Note that **weeks 1 through 13 need no third-party targeting permission at all** under the subject classes in R4, which is the whole point of the design.

---

# 4. Ratify-before-collection

Nine items. Nothing collects against anything, including a synthetic account, until every one of them is stamped in `doctrine/DOCTRINE_STATUS.md`.

| # | Artifact | Why it gates |
|---|---|---|
| 1 | `doctrine/SUBJECT_SELECTION.md`, per criterion | The gate has no criteria to read. An unratified criterion must refuse, and there must be a test asserting it refuses. This is the direct lesson of `zisr-recon/src/zisr_recon/guard.py`, where `scope` is loaded, required, printed in `describe()`, and never read by `check()`, so any complete authorization file permits every non-NEVER address on earth |
| 2 | `doctrine/RETENTION.md`, including R1, R2, R3, R5 | Unencrypted blobs cannot be retroactively crypto-shredded, and plaintext values in a durable table cannot be un-sampled from Postgres column statistics after the rows are deleted |
| 3 | `policy/subject-authorization.yaml` and `schema/subject-authorization.schema.json` | The doctrine compiled. Prose does not dispatch |
| 4 | `policy/retention.yaml` | Same, for retention |
| 5 | `ontology/selectors.yaml` | D2. A masked recovery hint reaching a field named `email` produces a dossier line an analyst reads as an established fact, and it is wrong in a way no validator can catch, because every guard keys on absence and this value is present |
| 6 | `spec/pse-semantics-contract.md` §5 (subject authorization) and §12 (retention and shred) | The normative surface the two doctrine documents argue for. A doctrine without a contract section is an opinion |
| 7 | `synthetic/CAST.md` with a sealed, hash-pinned `GROUND_TRUTH.yaml` containing at least one designed confuser pair | Without a confuser pair you can measure recall and cannot measure precision, so the case cannot be scored. The confuser pair is the connector-level `known_negative` canary lifted to case level, and the rule reads the same way |
| 8 | `runner/dispatch_allowlist.yaml` | The bypass check has nothing to compare against, and gate coverage becomes a claim |
| 9 | `doctrine/DOCTRINE_STATUS.md` showing 1 through 8 stamped | One partially stamped item does not stamp the file |

**And one machine condition, which is not a document.** `make preflight` green:

```
python tools/validate_authorization.py --dispatch-paths
python tools/validate_authorization.py --fixtures
python tools/validate_retention.py --policy --shred-roundtrip
python tools/validate_retention.py --repo-scan
```

`preflight` runs in the runner process at startup and its failure is fatal to the runner. The Makefile target exists so it is also runnable in CI against fixtures. The enforcement is in the process, because a doctrine mechanism whose only enforcement is a build target is enforced only against people who run build targets, and collection runs are started by people in a hurry.

## 4.1 The argument the gate rests on, stated as engineering

Two independent arguments arrive at the same place. Both belong in `doctrine/SUBJECT_SELECTION.md`, and the second one is the one that will change behaviour.

**Retention bounds persistence. It does not bound collection.** Deleting a profile does not un-collect it. It does not reach the platform's own record that session `ig_sess_04` viewed uid 25025320 at 12:08:41Z, which is a record about the subject-operator link, held by a third party, permanent, and outside every mechanism in `RETENTION.md`. It does not reach the credential heat spent. It does not reach the bystanders the run touched on the way. The gate that bounds the act has to sit before the act.

**You cannot validate an identity-correlation engine without ground truth.** PLAINSIGHT's central output is a claim of the form "these two handles are one person." Grading that claim requires an oracle. Write the confusion matrix out, because the argument lives in one cell:

- TP: the system proposes A~B and they are the same person.
- FP: the system proposes A~B and they are not.
- FN: A and B are the same person and the system did not propose it.

Recall is TP / (TP + FN). **FN requires enumerating the accounts the person actually has.** For an arbitrary third party the accounts you never found are indistinguishable from accounts that do not exist, and no experiment separates them. Any recall figure produced against a stranger is a fabricated number, which is the same defect class `PLAINSIGHT-design.md` CUT LIST A already killed when it removed `precision_prior` and `evidentiary_weight` as "Invented numbers with no calibration ground truth anywhere in the system."

Precision looks computable and is not. Confirming that a proposed link is correct requires an oracle, and the analyst's own judgment is the system's output re-entered as ground truth. That measures self-consistency. The resulting precision estimate rises exactly as the analyst's confidence rises, which is the correlation the measurement most needs to break.

Two further consequences that are build facts rather than cautions:

- **`attempted_and_absent` can never be promoted from stored to rendered without confirmable subjects.** CUT LIST B defers it "until canary-proven `always_present` across the connector fleet." Proving `always_present` requires knowing what is actually present, which on a synthetic account is known because the team set the fields, and on a stranger is never known. A designed v1.1 feature is permanently unshippable in the stranger configuration.
- **On a stranger, a wrong value looks exactly like a right one.** D2's residue class is datum-unlabelled plausible values. Toutatis's manifest already annotates the danger: `fp_mode: "platform returns recovery hint for a LINKED account, not necessarily owner"`. Against a subject who can be asked, you find out which it was. Against a stranger you cannot, so collecting on strangers does not merely fail to measure. It conceals the defect class D2 exists to prevent.

Consenting subjects, purpose-made accounts, and the operator's own accounts are not the watered-down version of this experiment. They are the only configuration in which precision, recall, negative-class validity, and extraction correctness are all computable. Build the capability to full depth and run it at full depth against subjects who can confirm the answer. That is the configuration in which "we proved the capability fully and completely" is a statement with evidence behind it.

**What is explicitly not gated**, so the doctrine is productive rather than obstructive: the Run/Item/Claim spine, the blob store, PSE and its schemas, the selector registry, every connector and manifest, both canaries, all six views, the Merge Sheet, clusters and exclusions, coverage intervals and the watchdog, the Lineage Drawer, retroactive invalidation, DRAFT and the export boundary, the whole retention mechanism, the conformance ladder, and complete end-to-end collection against S0, S1, and S2 subjects at any depth, with no ceiling on aggressiveness. Weeks 1 through 13 need no targeting permission at all.

---

# 5. What the operator did not ask for and needs

Ten items, ordered by how expensive they are to fix later.

### 5.1 The repository is itself an unshreddable PII surface

D4 gives per-case crypto-shred, which is the right mechanism for the blob store. It does not reach git. Git history is append-only, distributed to every clone, and survives `git rm`. Four routine acts defeat the entire retention mechanism: committing an HTTP cassette captured against a real subject, pasting a stack trace containing a selector into an issue, screenshotting a dossier into a design document, and writing "case for @realhandle" in a worklog entry.

This is sharper than it first looks, because `PLAINSIGHT-design.md` §6.3 makes cassettes **mandatory day-one CI infrastructure**: "You cannot hit live Instagram in CI. VCR-style HTTP cassettes per connector, captured during onboarding, replayed in CI. Without it no connector change can ever be tested and the entire extensibility story dies quietly." A cassette is a verbatim, durable, committed copy of a platform's response about a person. **The one artifact class the retention mechanism structurally cannot destroy is exactly the artifact class the CI harness requires to be permanent.** Subject selection is therefore the precondition for having a test harness at all, not something adjacent to it.

**Proposed artifacts (v0.1):** an Execution Limits clause in `AGENTS.md`; `canary_subject_class` as a required manifest field with values `synthetic | institutional | consented`; the violation code `FIXTURE_CONTAINS_LIVE_SELECTOR`; `tools/validate_retention.py --repo-scan` wired into `.githooks/pre-commit`.

### 5.2 Incidental and bystander collection has no name anywhere in the plan

These tools collect on populations. One Telegram channel subscription collects the message text of every member to observe one, and the design sizes the message table at 100,000 to 3,000,000 rows per case. A follower-list expansion on an account with 900 followers creates 900 selector records. CrossLinked enumerates an entire company's staff to find one employee; that is its function.

Three consequences the current design does not handle: the gate is per-selector and bystanders never pass through it, because they arrive as a byproduct; bystander data inherits the subject's TTL including extensions granted for unrelated reasons; and consent is unobtainable at that scale, so even an S1 case collects on non-consenting people.

**Proposed artifacts:** subject class **S5 INCIDENTAL** in `SUBJECT_SELECTION.md` (v0.1); `subject_relation: seed | pivot | incidental` as a computed column, never asserted (v0.1); incidental content gets a shorter, non-extendable TTL (v0.1 as a rule, v0.2 for the differential machinery); an incidental persons never become pivot origins rule (v0.1); and **the pre-flight line shows the incidental count before the run**. The design already renders a per-run pre-flight exposure line, so adding "this pivot will collect on approximately 900 people" to a string that already exists is the highest-value UI change in this plan and costs one estimate and one string.

One architectural note worth recording: `PLAINSIGHT-design.md` §8.3 puts messages in "a separate partitioned table (by case, then month)" for performance reasons. That choice turns out to be load-bearing for retention, because it is what makes independent shredding of the bystander-dominant class possible. Record the second reason so nobody merges the tables later for simplicity.

### 5.3 The synthetic cast has lead time and cannot be assembled retroactively

Accounts created last week look like accounts created last week: thin post history, no follower graph, no cross-platform residue, no archived copies. A matcher fixture set with ground truth cannot be built after the fact, for the same structural reason `PLAINSIGHT-design.md` §8.2 item 2 gives for coverage: it "cannot be reconstructed retroactively."

**Proposed artifacts:** `synthetic/CAST.md` and `synthetic/GROUND_TRUTH.yaml` (v0.1, Step 4, today). Content requirements: a designed link graph containing the correlation surfaces the system claims to exploit (shared email root, shared recovery phone, reused profile photo, reused writing pattern, and at least one pair sharing nothing); **at least one designed confuser pair** that a naive matcher will link and that is truly distinct; strict isolation, meaning the cast interacts only with itself, because a synthetic persona with real followers is a bystander collector; per-persona recovery selectors, because a cast created from the operator's own phone links the entire cast to the operator on the first correlation run; and **freeze-then-score**, meaning the analyst's cluster set is frozen with a content hash before the truth file is opened, so a single-operator program can still measure something.

### 5.4 The finding survives the shred, and sometimes the finding is PII

Three classes of post-shred artifact, and the third is where the pressure will be.

| Artifact | Contains subject-derived values | Survives |
|---|---|---|
| Capability finding: "toutatis returns a recovery hint for a linked account, not necessarily the owner: measured across 6 synthetic accounts, 4 of 6 resolved to a different account" | No | Yes. This is the entire point of the program |
| Scorecard: precision and recall against the cast, with persona age and truth-file hash | Synthetic only | Yes, and it must carry its conditions |
| Case narrative: "we linked @j_voss_88 to a Reddit account via a shared recovery phone" | Yes | No |

The case narrative is the most compelling demonstration artifact the program will produce, which is exactly why it needs a named rule rather than a judgment call.

**Proposed artifact:** `tools/validate_retention.py --finding <file> --case <id>`, scanning a candidate writeup against the case's selector set and refusing on a match. **The check runs at case close, before the shred, while the values still exist.** The output is a stamp recording that it passed.

> **[REJECTED READING — DO NOT RE-DERIVE IT]** The natural design is to retain a salted HMAC of the case's selector set after the shred so the finding check can run later. That is wrong and must not be reintroduced. A surviving HMAC key plus a surviving digest set is a membership oracle: anyone holding it can test a candidate selector for membership and get a yes or no. That is a re-identification channel built into the deletion evidence. Running the check before the shred needs no retained digest at all, so the oracle never exists.

Two further artifacts live outside every mechanism above. **Screen recordings, screenshots, and exported briefs** from a real case sit in a downloads folder, outside the database, outside the sweep, outside the shred. Rule: no screen recording, screenshot, or exported brief from a non-synthetic case leaves the case boundary, and demos are built on the cast. **DRAFT and Return Brief exports** are stratum 1 and are written inside the case boundary where the sweep reaches them, or they are not written.

### 5.5 The `text: forever` conflict is a governance conflict and it is live

`PLAINSIGHT-design.md` §5.7 sets `retain: {text: forever, media: 90d}`. When the text is a person's bio, follower list, and message history, that is in direct tension with the operator's stated posture. It cannot be resolved in the design document, because rank 7 does not get to set a retention rule. It resolves in `doctrine/RETENTION.md` as R5, and until it is stamped the storage layer has two contradictory instructions.

### 5.6 Credential and persona lifecycle is undefined

The design has `credential_pool`, `credential_ref`, `quarantine_credential: true`, and `▮▮▮▮▮` redaction in argv. It has no lifecycle. Whose account performs the collection is undefined; if it is the operator's real account, the operator's identity is bound to every view of every subject in a record the platform holds permanently. `quarantine_credential` has no exit criterion, so a quarantined credential either stays quarantined forever or gets released by whoever notices.

**Proposed artifacts:** one paragraph in `SUBJECT_SELECTION.md` at v0.1 stating that the platform's log of our collection is outside every mechanism in this repository and that the only control over it is not collecting; `doctrine/CREDENTIAL_LIFECYCLE.md` deferred until the cast exists. Note that a synthetic subject viewed by a synthetic credential produces a platform-side record linking two things the team owns, which is the strongest available argument for the cast.

### 5.7 Legal hold conflicts with automatic shred, and the conflict is live

If a run surfaces something a reasonable person would report, the doctrine's own automatic shred destroys the material and there is no defined path. Two rules the operator holds at once collide.

**Proposed artifact:** a narrow freeze act in `RETENTION.md` (v0.1): stop the run, freeze the case against the sweep, notify the operator, collect nothing further. **The freeze is an explicit logged act with its own expiry**, or it becomes the retention loophole that eventually swallows the doctrine.

### 5.8 Retention failure must stop collection, and connector versions must not be deletable

Two small mechanisms, both cheap, both invisible until they are needed.

**A retention mechanism that can fail without stopping collection will be found to have been broken for six months.** `SHRED_FAILED` on any case blocks all new runs system-wide, not only for that case. Roughly forty lines and one integration test. Similarly, the absence of the sweep's heartbeat is a named degraded state rendered in the case header, not a silence, following `OPERATIONAL_CONTRACT` §4's prohibition on inferring that a link is fine from the absence of a failure signal.

**`PLAINSIGHT-design.md` §6.4 keeps exactly one governance item, per-case version pinning**, so reopening a case shows `toutatis 1.4.2 (superseded by 2.0.0 — output shape changed)`. That guarantee requires the manifest, the cassette, and the adapter for 1.4.2 to still exist when the case is reopened in eight months. Nothing currently says a connector version may not be deleted. One clause in `AGENTS.md` under Class C.

### 5.9 The ladder terminates in one person

The operator is the ratifier, the maintainer, and the analyst. Every "requires operator approval" gate in this set is the operator approving their own request. That is a genuine limit and it should be stated in `SUBJECT_SELECTION.md` rather than left implicit, because a control whose bypass is undocumented gets bypassed silently, and a control whose bypass is a dated Class F entry gets bypassed visibly. Visibly is the whole mechanism. It is also precisely why the ZMeta documents have worked: they did not remove the operator's authority, they made using it a thing that leaves a mark.

**Proposed mitigations, all already used elsewhere in the program:** adversarial passes from a fresh agent context against the operator's own decisions; freeze-then-score for anything the operator scores themselves; and the doctrine review log rule that you **log the cases where the doctrine won**, not only the unresolved ones, because recording only the failures removes the baseline that makes an outlier recognizable.

### 5.10 No model training or fixture-building on non-synthetic data

A matcher trained or fixture-built on a real case carries that case in its weights or its fixtures permanently and cannot be shredded. CUT LIST B already names where the pressure arrives: auto-promotion of GENERATED to OBSERVED "waits until the matcher library has fixtures." Those fixtures come from the synthetic cast or they do not exist. **Proposed artifact:** one clause in `SUBJECT_SELECTION.md`, v0.1.

---

# 6. Step 1, in full detail

One session. No operator decision required. Nothing here touches a platform.

## 6.1 Cut the repository

```bash
cd "<Z-ISR>"
mkdir plainsight && cd plainsight && git init
mkdir -p doctrine spec schema ontology policy synthetic connectors runner app docs tools .githooks
mkdir -p conformance/gate conformance/connector-harness conformance/retention

git mv 2>/dev/null || true
cp ../DOCUMENT_STANDARD.md      docs/DOCUMENT_STANDARD.md
cp ../PLAINSIGHT-design.md      docs/PLAINSIGHT-design.md
cp ../PLAINSIGHT-FOUNDATION.md  docs/PLAINSIGHT-FOUNDATION.md
cp ../OSINT-COP-tool-review.md  docs/OSINT-COP-tool-review.md

git config core.hooksPath .githooks
```

The four copied files are moved in **unchanged**. `PLAINSIGHT-FOUNDATION.md` keeps its line 4 status header ("Status: DRAFT 2026-08-26. Nothing here is operator-ratified.") until Step 2 stamps it. Editing that line before the stamp is exactly the half-stamping `zisr-recon/docs/ENTRY_CRITERIA.md` warns about.

## 6.2 `CLAUDE.md` — advisory, four sections

**§ North Star.** Two products, and which serves which. PLAINSIGHT is an OSINT common operating plane whose product is the citation chain. PSE is the ZMeta-derived dialect that makes the chain expressible. PSE serves PLAINSIGHT. PSE is a private dialect operating under the clause in `ZMeta/zmeta-spec/AGENTS.md`, quoted in full, and never claims upstream compatibility.

**§ Authority order.** The eight-rank ladder from §1.3 above, with the preamble, the doctrine-outranks-contract argument, the doctrine-stays-in-its-lane inverse, the cross-lane rule, and three worked examples:

1. *The design wants a field the envelope forbids.* `PLAINSIGHT-design.md` §5 wants a per-field "looked and did not find" state; `policy/semantics.yaml` forbids an observation carrying a negative assertion. Rank 3 wins. The move is a Class D proposal for a distinct negative-observation shape, or the design does without. The design already reached this conclusion on its own: CUT LIST A kills the hollow pip because it "manufactures negative evidence from a YAML typo."
2. *Doctrine refuses a subject the case purpose covers.* Rank 1 wins over the analyst's judgment and over the case record at rank 7. The path is an extension carrying author, timestamp, and reason, which is a Class F act. The path is not editing the guard.
3. *A validator disagrees with the contract.* Rank 6 loses to rank 2 and the validator is the defect. When a validator is **stricter** than the contract it stays until the contract is amended or the validator is proven wrong, because an over-strict validator fails closed and an under-strict one lets a wrong claim into a dossier.

**§ Design gates — eight, applied to every change.** Written as questions, at the authority ZMeta gives its seven.

1. **Prohibition is structural.** A rule that lives in a README is not a rule. A change that introduces a constraint is not done until the constraint is a schema `false`, a policy denylist, a gate that refuses, or a job that runs, covered by a test that fails when the constraint is removed. This is gate 1 rather than implicit because FOUNDATION §1 already named the program's one consistent seam: "You write mechanisms where the failure mode is technical, and sentences where the failure mode is procedural."
2. **Subject selection is upstream of everything.** Does this change widen who can be collected on, or how far a pivot can reach? If yes it is Class F regardless of which file it touches. The trap this closes is that a subject-widening change rarely looks like one: a row added to a YAML allowlist, a relaxed regex, a new `kind` in the connector shapes, and a bystander disposition of `retain` are all one-line diffs in files that look like Class B.
3. **Ground truth or it is not a test.** A change that claims a capability works names the subject it was scored against and how the answer was known. If the answer could not be known, the change claims coverage rather than correctness, and says so in those words. This does not cap collection depth, aggressiveness, connector count, or pivot depth against a scoreable subject. Depth against a scoreable subject is the experiment.
4. **The bystander is a first-class object.** Every connector that reaches beyond its named selector declares what it reaches and what happens to it. An undeclared bystander class is refused at manifest validation, not flagged.
5. **Collect the minimum an analyst needs to adjudicate.** ZMeta gate 2 with the consumer changed to an analyst at the Merge Sheet. The second edge is new: in ZMeta producer-completeness costs bandwidth, here it costs a person's data. Both edges point the same way, which means data minimization is not a tax on the capability work.
6. **Honesty end-to-end. No laundering, no invented numbers, no unlabelled datums.** ZMeta gate 3 verbatim, extended by D2. `email_hint_recovery_masked`, never `email`. `email_generated_permutation`, never `email`. `handle`, never `platform_uid`.
7. **The case is the source of truth. Every projection is lossy and one-directional.** ZMeta gates 4 and 5 merged, because here they are one gate. The export boundary enforces citation completeness **and** data minimization; a projection complete in citations and unminimized in content passes half a gate.
8. **Closed vocabulary, cheap additions, outer rings first, then stop.** ZMeta gates 1, 6, and 7 merged, with the posture of gate 1 deliberately inverted while its mechanism is kept. ZMeta makes vocabulary additions expensive because a new event type breaks interoperability downstream. PSE's selector registry has no downstream ecosystem and is not trying to have one, so a registry addition is reviewed once, benefits every connector, and is expected to be routine. What stays expensive is a new connector `kind`: new tools are free, new shapes are a platform release.

**§ How we work here, and voice.** Two registers, with the rule for which applies where.

*Register 1, repo prose, inherited whole from `ZMeta/zmeta-spec/CLAUDE.md`.* Flat, declarative technical prose; professional without sounding like a sales pitch. Avoid em dashes as a connector. Avoid inversion for emphasis. Avoid sentence fragments and mid-sentence bolding for rhythm. Avoid sentences opening with And, But, or So to carry cadence. Avoid metaphor standing in for a checkable statement. Do not over-correct into passive voice, hedging, or padding; a voice pass leaves word count flat or slightly higher. Quotations are copied exactly, tics included. **Process records are never restyled, because rewriting them falsifies what was true when they were written.** Applies to every tracked file, commit subjects, tag annotations, and PR text.

Two extensions this repository needs that ZMeta does not state. **Validator and gate refusal strings are governed prose**: a connector author meets `tools/validate.py` at the worst moment of their week and the message is the only documentation they read, so it states what was refused, which rule refused it, and what the two or three legal moves are. **A state is rendered as its consequence, never as its token**, lifted from the ZISR COP pattern where `parked` renders as "PARKED — this COP is NOT attached to this source", because an operator cannot act on the string "forgotten." This binds PLAINSIGHT's five connector health states, the gate's three values, and every retention state, and there is a test behind it.

One warning specific to `doctrine/`: those two files will attract a third register with its "shall not", its capitalized defined terms, and its blanket qualifiers. Refuse it. A doctrine document written in policy-speak reads as someone else's requirement being imposed and gets routed around. The same document written as engineering, naming the mechanism that enforces each rule and the test that proves it fired, reads as a system property and holds.

*Register 2, published briefings.* `docs/DOCUMENT_STANDARD.md` in full, applied when a document has a reader who is not the author, a finding worth leading with, and enough consequence that being skimmed wrong would cost something. **A doctrine document never becomes a briefing**: it is rank 1, it is parsed by the guard, it is amended by ratified item, and it must diff cleanly.

*Analyst prose in the DRAFT view is governed by neither register.* Its standard is the citation requirement. Applying a house voice standard to it would be the system editing a finding.

**§ Attribution.** Carry ZMeta's rule pending R6: attribute commits to the human maintainer alone, no `Co-Authored-By` trailers naming the agent. Add the one rule that is not a matter of taste: **a Class F commit is authored by the ratifier**, and an agent never authors one under any attribution scheme.

## 6.3 `AGENTS.md` — normative, six sections

**§ What this repository is.** Two lanes, the dialect declaration in the first ten lines, and the quoted licence clause from `ZMeta/zmeta-spec/AGENTS.md`.

**§ Change classes A through F**, as §2 above, with the three rules about the classes themselves: a change carries the highest class it touches; Class F is defined by effect and not by path; and Class C diverges from ZMeta's Class C by adding a design-record requirement. That last one is added because the program has already failed this exact way, and FOUNDATION §1 measured it: `UIUX_DESIGN.md` §3 says any value outside its token list is a bug while `config.js` carries `SIM_LABEL_BACKGROUND_HEX`; §9 documents four keyboard shortcuts and one is implemented; §4 documents five tabs and four render `Planned — slice ${slice}`. The drift runs both directions, which is the worse half: the reference-camera availability layer, `bridgeStateLabel()`, the session retention bound, and the imagery picker "are the best patterns in the repo and appear nowhere in the design record."

**§ Execution Limits.** This section replaces ZMeta's Release Limits and reads at the same authority. In ZMeta the one act with irreversible external consequence is publishing, and nothing an agent does to a schema file leaves the machine. Here the irreversible act is executing a connector against a live platform, which reaches a third party, writes to a platform's logs, spends credential heat, and cannot be undone by any control this repository contains.

- No agent executes a connector, adapter, or runner against a live platform, account, or person. Not to check a hypothesis, not to confirm liveness, not "just the known-positive canary." Canaries are operator-run during onboarding.
- No agent adds, edits, or removes an entry in any allowlist, NEVER list, authorization file, or `retain_until` value. Drafting a proposed diff is permitted; applying it is Class F.
- No agent extends a case past `retain_until`, disables a shred job, or edits a scheduled reconcile.
- No agent commits a cassette, fixture, screenshot, or log excerpt containing data about a person, including into a scratch directory inside the repository.
- No agent writes a selector value, handle, email, phone, or case-subject name into a tracked file, and that includes worklog entries and commit messages.
- No agent lands a Class F change. Drafting one is permitted and expected.

**§ Required local workflow.** ZMeta's shape, with the four named gates from the Makefile.

**§ Documentation matrix.** Which surfaces must move together. Rows for Doctrine, Contract, Schema, Ontology, Policy, Conformance, Connector manifest, Tooling.

**§ Ratification rule.** Doctrine items carry a per-item marker with item, date, and ratifier. Conclusion is ratified separately from basis; FOUNDATION's phrasing is the standard, "No emitter should be built on a rationale the operator was never shown." **Unratified binds nothing, and the mechanism reads the stamp rather than the file.** There must be a test asserting that an unratified criterion refuses rather than permits, because the alternative is repeating the `guard.py` defect one level up.

## 6.4 `doctrine/DOCTRINE_STATUS.md`

Created now, with everything UNRATIFIED. Its existence is what makes "is this ratified" a lookup instead of a memory.

```markdown
# Doctrine status — the pin of record

Nothing in this repository binds unless it appears below with a date and a
ratifier. One partially stamped item does not stamp its file.

## Ratified

| Item | File | Version | Conclusion stamped | Basis stamped | Ratifier |
|---|---|---|---|---|---|
| (none) | | | | | |

## Pending ratification

| Item | File | Drafted | Blocking | Notes |
|---|---|---|---|---|
| D1 fork as PSE | docs/PLAINSIGHT-FOUNDATION.md §3 | 2026-08-26 | Steps 5,7 | |
| D2 closed selector vocabulary | docs/PLAINSIGHT-FOUNDATION.md §3 | 2026-08-26 | Step 6 | |
| D3 append-only | docs/PLAINSIGHT-FOUNDATION.md §3 | 2026-08-26 | Step 7 | |
| D4 retention as mechanism | docs/PLAINSIGHT-FOUNDATION.md §3 | 2026-08-26 | Steps 3,11 | |
| D5 three-valued subject gate | docs/PLAINSIGHT-FOUNDATION.md §3 | 2026-08-26 | Steps 3,10 | |
| D6 event-type set | THE GAMEPLAN §3.0 | 2026-08-26 | Step 5 | 7 or 9 |
| D7 version label | THE GAMEPLAN §3.0 | 2026-08-26 | Step 5 | 0.1 or 1.0 |
| D8 repo shape | THE GAMEPLAN §3.0 | 2026-08-26 | Step 1 | |
| R1 shred unit | THE GAMEPLAN §3.0 | 2026-08-26 | Steps 3,11 | |
| R2 TTL and ceiling | THE GAMEPLAN §3.0 | 2026-08-26 | Steps 3,11 | |
| R3 FTS inside shred boundary | THE GAMEPLAN §3.0 | 2026-08-26 | Steps 3,11 | |
| R4 subject classes at v0.1 | THE GAMEPLAN §3.0 | 2026-08-26 | Steps 3,8 | |
| R5 `text: forever` | THE GAMEPLAN §3.0 | 2026-08-26 | Step 3 | |
| R6 commit attribution | THE GAMEPLAN §3.0 | 2026-08-26 | Step 1 | |
| R7 interaction line | THE GAMEPLAN §3.0 | undrafted | Step 6 | |
| R8 bystander disposition | THE GAMEPLAN §3.0 | undrafted | not blocking | |

## Assistant readings awaiting confirmation

| Marker location | Reading | Raised |
|---|---|---|
| (none yet) | | |
```

## 6.5 `.githooks/pre-commit`

```sh
#!/bin/sh
# Class F. Git history is the one store crypto-shred cannot reach.
python tools/validate_retention.py --repo-scan --staged || {
  echo "pre-commit refused: a staged file contains a selector-shaped string."
  echo "  rule:  AGENTS.md > Execution Limits"
  echo "  moves: replace the value with a synthetic one from synthetic/CAST.md,"
  echo "         or classify the fixture as institutional in its manifest."
  exit 1
}
```

At Step 1 `tools/validate_retention.py` does not exist yet, so the hook is written with the invocation and the refusal message and the tool is stubbed to exit 0 with a printed line saying it is a stub. That stub is a scheduled mechanism with a real message, and it is replaced in Step 8. A stubbed job that is wired is a mechanism; a comment is not.

## 6.6 `docs/plainsight_worklog.md` and `docs/plainsight_handoff.md`

Two files with two jobs. The worklog is chronological and is never restyled. The handoff is current-state and is rewritten every wave. ZMeta's worklog opens with a "Current Resume Note", which is the handoff's job leaking upward; do not inherit that. `ZMeta/zmeta-spec/docs/zmeta_refinement_handoff.md` is 2,080 lines and carries eleven superseded state sections, so cap the handoff at roughly 400 lines with superseded sections moving to the archive on the next session, and cap the worklog's live entries at the ten most recent.

**One divergence from ZMeta, and it is the hygiene doctrine the operator asked for: the worklog is a PII surface.** ZMeta's worklog can quote anything in the repo. This one cannot quote a case, a selector value, a handle, or a finding. An entry says "case `c7f2` shredded on schedule, 41 blobs, verified by external decrypt failure." It never says whose case it was. That single rule is what keeps the crypto-shred mechanism from being defeated by good record-keeping habits.

Worklog entry 1, written today:

```markdown
## 2026-08-26 — Wave 0. Repository cut.

**Class:** A (documentation) + F (doctrine skeleton, unratified and binding nothing)

Cut `plainsight/`. Moved in unchanged: DOCUMENT_STANDARD.md, PLAINSIGHT-design.md,
PLAINSIGHT-FOUNDATION.md, OSINT-COP-tool-review.md. FOUNDATION keeps its DRAFT
header; stamping it is Step 2 and is the operator's act.

Wrote CLAUDE.md (advisory: North Star, 8-rank authority order, 8 design gates,
2 voice registers) and AGENTS.md (normative: change classes A-F with F new,
Execution Limits, documentation matrix, ratification rule).

Wrote doctrine/DOCTRINE_STATUS.md with 16 items pending and zero ratified.

Installed .githooks/pre-commit calling tools/validate_retention.py --repo-scan.
The tool is a stub that exits 0 and prints that it is a stub. Replaced in Step 8.

**Refused this session:** nothing collected, no connector executed, no platform
touched. No file in the repository contains a selector belonging to a person.

**Deferred issue register**
- D-001 `tools/validate_retention.py --repo-scan` is a stub. Real implementation
  is Step 8. Until then the pre-commit hook is a wired mechanism with no check
  behind it, and that is a known gap rather than an oversight.

**Next:** Step 2. Operator stamps or amends D1-D5 in DOCTRINE_STATUS.md.
```

## 6.7 Done-condition for Step 1

- The tree in §1.2 exists, with the empty directories present.
- Four documents moved in unchanged, `PLAINSIGHT-FOUNDATION.md` still carrying its DRAFT header.
- `CLAUDE.md` and `AGENTS.md` written, both citing the ZMeta files they derive from by path.
- `doctrine/DOCTRINE_STATUS.md` exists with sixteen pending items and zero ratified.
- `.githooks/pre-commit` installed and executing, with `core.hooksPath` set.
- `docs/plainsight_worklog.md` entry 1 and `docs/plainsight_handoff.md` written.
- Every file passes a manual read against the Register 1 voice rules in `CLAUDE.md`.
- Nothing in the repository contains a selector belonging to a natural person.
- One commit, authored by the operator, subject line describing the change in plain terms with no aphorism.

**The next thing the operator does after Step 1 is Step 2, and Step 2 is a decision, not a build.** Refusing or amending D1 through D5 costs an hour now and is unavailable at month five.

---

## Expiry condition for this plan

Every mechanism named here is unbuilt. The claim that PLAINSIGHT's retention is a mechanism rather than a sentence becomes true when the CI test that opens a past-due case, runs the sweep, and passes all five `verify_shred` checks is green, and not before. The claim that the subject gate protects the dispatch path becomes true when `tools/validate_authorization.py --dispatch-paths` is green, and not before. Re-read this document against those two tests before quoting anything in it as the program's posture.