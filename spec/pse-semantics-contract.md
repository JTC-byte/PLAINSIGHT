# PSE semantics contract: pse-event-0.1

**Status: pse-event-0.1, Unlocked. DRAFTED 2026-09-08 by an agent. UNRATIFIED.**
Sections 5 and 12 are two of the eight artifacts `doctrine/SUBJECT_SELECTION.md`
SS-14 item 6 requires stamped in `doctrine/DOCTRINE_STATUS.md` before any
collection. Neither carries a stamp. This document binds nothing until the pin of
record carries their rows, and it explains rather than decides: every rule below
already exists as a schema keyword, a policy entry, a runner check, or a doctrine
criterion, and the sentence here says which.

**Authority.** Rank 2, Class B (`CLAUDE.md` section 2, `AGENTS.md` section 3).
The four rank-1 doctrine files win every conflict with this document. A change to
the event vocabulary, the layer model, or envelope semantics is Class D and needs
a version bump and a divergence-register entry, per `AGENTS.md` section 3 and
the open question `spec/layer-model.yaml` records in its header.

**What this document is derived from, and why it was written last.**
`spec/layer-model.yaml` is the single source. `tools/generate_pse.py` reads it and
writes `schema/pse-event-0.1.schema.json` and the four files under `policy/`;
`tools/build_corpus.py` writes `conformance/must-pass.jsonl` and
`conformance/must-fail.jsonl`; `tools/validate.py` enforces what those files say
and refuses when any of them differs from what the model generates. This
contract was written after all of that was green, on the rule in
`docs/THE-GAMEPLAN.md` Step 7 that the contract explains rules that already
exist rather than inventing rules nothing enforces. ZMeta's contract states the
opposite relationship, authority over the schema, and PSE inverts it on purpose:
where this document and a generated artifact disagree, the generated artifact
is what the tree enforces and this document is wrong until corrected.

**PSE is not ZMeta.** It is a private dialect derived from `zmeta-event-1.0`
under the license `AGENTS.md` section 1 quotes. Nothing here may be described as
ZMeta-conformant. `CONFORMANCE.md` states the negative claim and the four
conditions; section 13 below lists the divergences the register at Step 9 will
govern.

---

## 1. What PSE is, and is not

PSE, the PLAINSIGHT Semantic Envelope, is the event vocabulary a person-centric
OSINT investigation is recorded in. Every fact the program learns, every decision
that let it be learned, every analyst act on it, and every retention act about it
is one event in one case. The product this vocabulary exists for is the citation
chain: a sentence in an assessment walks back through a cluster, through claims,
through items, through a run, to a gate decision and an authorization, and to raw
bytes by hash (`CLAUDE.md` section 1).

Nine event types carry that chain, one per layer of the argument, and the layers
are closed both ways (`spec/layer-model.yaml` `layers`). An event that carries a
field from a layer above its own has collapsed two layers into one row, which is
the defect the denylists in section 3 refuse.

| Layer | Type | Subtypes | What one event is |
|---|---|---|---|
| authorization | `AUTHORIZE_EVENT` | GRANT, EXTEND, REVOKE | The authorization act, by reference to the SS-4 record |
| authorization | `COLLECT_EVENT` | PERMITTED, REQUIRES_EXTENSION, REFUSED | The subject gate's decision at dispatch |
| observation | `PROBE_EVENT` | RUN_START, ITEM, RUN_END | One tool invocation as three append-only events |
| observation | `EXTRACT_EVENT` | CLAIM | One field asserted by one item, named by its datum |
| inference | `LINK_EVENT` | SAME_ENTITY, ASSOCIATED_WITH, CO_LOCATED, CONTROLS | A matcher's proposal, always unaccepted |
| fusion | `IDENTITY_EVENT` | CLUSTER, EXCLUDE | An analyst's identity assertion or exclusion |
| adjudication | `ADJUDICATE_EVENT` | nine dispositions | A human act on an object already in the case |
| state | `ASSESS_EVENT` | SENTENCE | One assessment sentence with live citations |
| system | `SYSTEM_EVENT` | eleven | Diagnostics, health, coverage, retention acts, heartbeats |

What PSE is not. It is not a data model for the case store, which is Postgres
tables the design owns (`docs/PLAINSIGHT-design.md` section 8.3). It is not the
connector manifest, which is Step 12. It carries no numeric confidence anywhere
(section 11), no selector value in any event that survives the shred
(section 12), and no field whose name lies about the provenance of its value
(section 6).

## 2. Version semantics

The version is `pse-event-0.1` and the status is Unlocked, by decision D7: ZMeta's
1.0 is Locked and a matching number would be read as a matching commitment
(`doctrine/DOCTRINE_STATUS.md`). Every event declares both `pse_version` and
`derived_from`, so the two models are distinguishable on the wire eighteen months
from now without a design document. [schema]

An Unlocked version changes by regeneration. The layer model changes, the
generator runs, the generated artifacts change together, and `tools/validate.py
--kernel` refuses a tree where any one of them lags the others. There is no
compatibility promise between two Unlocked states. The version label moves to
1.0 only through Class E release governance in `AGENTS.md`, and nothing in this
repository has been released.

The violation-code vocabulary is append-only once 0.1 ships (`spec/layer-model.yaml`
`violation_codes`). A code is never renamed and never removed; a rule that stops
firing it is recorded, and the code stays declared so an old diagnostic still
resolves.

## 3. Enforcement model, and how to read a rule here

No single surface enforces this contract, and every rule below carries a label
naming the surface that does. The labels are the whole point of the document: a
reader can tell a rule a machine refuses from a rule a person follows.

| Label | Enforced by | What a failure looks like |
|---|---|---|
| [schema] | `schema/pse-event-0.1.schema.json`, run by `tools/validate.py` | A code from `policy/semantics.yaml` `schema_error_map`, never a bare schema message |
| [policy] | `tools/validate.py` reading `policy/semantics.yaml`, `policy/lineage.yaml`, `policy/producer-authority.yaml` | The rule's own code |
| [runner] | The Step 10 runner, evaluating a fact about the case rather than the event | Listed under `runtime_rules` in `policy/semantics.yaml`; the corpus validator does not emit these |
| [gate] | `tools/validate_authorization.py` at Step 8, over the composed pivot chain | Listed under `chain_rules` in `policy/lineage.yaml` |
| [review] | A person, at the point named | Stated in place with no mechanism, on the RT-14 pattern |
| [rendering] | The interface | Listed under `rendering_rules`; not a wire check |
| [unratified] | Nobody yet | A reading awaiting the operator's stamp |

The order of checks, for one event. The schema runs first and names each failure
through the error map. Producer authority runs before any semantic check, as in
ZMeta. The recursive denylist, the payload rules, lineage, and the cross-event
rules follow, and every check that can run does run: the validator does not stop
at a schema failure, because a fixture that is both schema-invalid and
policy-invalid would otherwise report the wrong code (`CONFORMANCE.md` section 5).
The one thing it cannot do is evaluate a type it does not know, so an event whose
`event_type` is outside the nine gets `EVENT_TYPE_UNKNOWN` and a record of the
checks not reached.

What the schema enforces: the envelope shape, the type and subtype enums, the
discriminator agreement, every required field per subtype, every field shape,
every closed set, `additionalProperties: false` at every declared level, the
reserved confidence key, and lineage requiredness per subtype. What the schema
cannot enforce: that a parent resolves, that a producer holds authority, that a
prohibited name arrived below depth zero inside an open object, that a cited
claim was verified, that a basis claim traces to a generated origin, and anything
that is a fact about the case rather than the event. Those are policy, runner,
or gate. What no machine enforces is stated where it applies, and there are three
such rules in this vocabulary: `REASON_NAMES_SUBJECT` (section 12),
`INCIDENTAL_ESTIMATE_MISSING` and `ADJUDICATION_REASON_MISSING` until the runner
exists (sections 5 and 8).

How a schema failure is named. A schema keyword failing at a path is not a
diagnostic an analyst can act on, so `policy/semantics.yaml` carries
`schema_error_map`, and `tools/validate.py` applies it. A `const` failure on the
version fields is `VERSION_MISMATCH`; a missing or malformed `case_id` is
`CASE_ID_MISSING`; an unknown type is `EVENT_TYPE_UNKNOWN`; a subtype outside the
type's set, or a payload discriminator that disagrees with it, is
`EVENT_SUBTYPE_MISMATCH`; a missing required payload field is
`PAYLOAD_FIELD_MISSING` unless a payload rule requires that field, in which case
the rule's code fires instead; an unknown payload key that a denylist group names
is that group's code (S7-R5); the reserved confidence key is the type's own
confidence code; an enum failure at a registry-bound field is
`SELECTOR_TYPE_UNREGISTERED`; any other closed-set failure is
`ENUM_VALUE_INVALID`; and anything left is `SCHEMA_INVALID`. [schema]

## 4. The envelope

Every event carries `pse_version`, `derived_from`, `case_id`, `event`, `source`,
and `payload`, and may carry `lineage`. Nothing else is accepted at the top level.
[schema]

- `case_id` is required without exception. Nothing exists outside a case, and
  decision D4 keys the crypto-shred on it, so an event without one is an event
  the sweep cannot reach (section 12). [schema]
- `event` carries `event_id`, `event_type`, `event_subtype`, and `ts`. `ts` is
  the time the producer emitted the event. For an observation it is collection
  time and never the platform's asserted time, which lives in `payload.temporal`
  on a claim (section 6). [schema]
- `source` carries `platform_id`, `environment`, and `producer`, and may carry
  `sw_version`. `environment` is `LOCAL` or `ISOLATED`, the two environments
  `doctrine/EGRESS.md` EG-1 defines; the FOUNDATION draft's three node roles and
  ZMeta's five mesh roles are gone (LM-R3, DV-04). `producer` is checked against
  producer authority before any semantic check (section 10). [schema] [policy]
- `lineage` carries `based_on`, one or more event ids, and may carry `transform`
  in the form `translate:<schema_id>@<adapter_version>`, so retroactive
  invalidation of an adapter's output is an index scan
  (`docs/PLAINSIGHT-design.md` section 7.5). Whether lineage is required is
  decided per subtype, not per type (S7-R6). [schema]
- `confidence` is a top-level key in `zmeta-event-1.0`. It is reserved here and
  refused on every event, emitted in the schema as `"confidence": false` rather
  than left undefined, so a permissive validator cannot let it in as an unknown
  property (section 11, DV-06). [schema]
- `payload` is bound per type and subtype: the schema carries one closed object
  per subtype, with the subtype's required fields, the fields it may carry
  (S7-R1), and the discriminator field pinned to the subtype name. The
  discriminator in the payload and the subtype in the envelope agree or the
  event is `EVENT_SUBTYPE_MISMATCH`, which is `zmeta-event-1.0`'s mechanism
  carried over unchanged (DV-03). [schema]

Identifiers are uuids matched by pattern, not by the `format` keyword alone,
because the `jsonschema` stack checks `date-time` and `date` only when an extra
package is installed and `zmeta-spec/schema/README.md` records the gotcha. The
date-time pattern is the one `zmeta-event-1.1.0` corrected, not 1.0's, which
accepts any string ending in `Z`. [schema]

## 5. Subject authorization

**Stamp target. `doctrine/SUBJECT_SELECTION.md` SS-14 item 6 names this section
among the eight artifacts stamped before any collection.** This section explains
how the authorization record and the gate's decision appear on the wire. It
decides nothing about who may be a subject: that is rank 1, and the compiled
form is `policy/subject-authorization.yaml` at Step 8. Stamping this section
stamps the explanation, not the doctrine it explains.

### 5.1 The record stays inside the case; the event carries a reference

The SS-4 authorization record carries the exact seed selectors and, for an S1
subject, a named person. It is stratum 1 and never appears on the wire.
`AUTHORIZE_EVENT` carries the act (`GRANT`, `EXTEND`, `REVOKE`), an opaque
`authorization_ref`, the `subject_class`, the expiry, the pivot depth, the
ratifier's identity, and a `purpose_hash`. The purpose sentence itself is
prohibited on the event, because the event is stratum 2 and survives the shred
while the sentence could describe a person (`doctrine/RETENTION.md` RT-2).
[schema] [policy: `AUTHORIZATION_RECORD_INLINED`]

`subject_class` is drawn from SS-1's set minus S5, which SS-1 marks not
authorizable: `S0, S1, S2, S3, S4, N0, L0`. The schema mirrors the doctrine's
enum and does not decide it; `tools/validate_layer_model.py` pins the list as
Class F, so widening it in the model refuses at the gate. [schema]

A `GRANT` carries `purpose_hash`; a case with no purpose has no authorization
(SS-4). A `GRANT` missing it is `CASE_PURPOSE_UNBOUND`, and a `PERMITTED`
decision whose authorization resolves to a `GRANT` without one is the same code
(gate fixture 14 at Step 8). [schema] [policy]

`EXTEND` and `REVOKE` carry `reason`, stated without naming or describing the
subject. No machine can check that sentence, and the rule is stated here rather
than borrowing a mechanism's authority: `REASON_NAMES_SUBJECT` is a review rule.
[review]

### 5.2 The gate's decision is an event, and a run is parented on it

`COLLECT_EVENT` is the subject gate's decision at dispatch (SS-6, SS-7, SS-8):
`PERMITTED`, `REQUIRES_EXTENSION`, or `REFUSED`, with the connector, the target
selector type (never its value), the subject relation the gate computed from the
chain, the pivot depth, the SS-8 step the decision was taken at, and for a
permission the incidental estimate and the bystander disposition. Only
`runner-subject-guard` may emit it, and no wildcard may, because a second
producer for this type would be a second gate (section 10). [schema] [policy:
`PRODUCER_NOT_ALLOWED`]

The decision carries no collected content. `value`, `content`, `raw`, `items`,
`claims`, `body`, `text` and `selector_value` are prohibited on it, because the
gate reads the authorization record and the chain and never the thing it is
deciding about (SS-19). [policy: `COLLECT_HAS_CONTENT`]

`bystander_disposition` is `count_only` or `refuse`, closed at v0.1 by decision
R8. `retain` is defined in doctrine and refused; adding it is Class F by effect
(`CLAUDE.md` design gate 2). [schema] [policy: `BYSTANDER_DISPOSITION_OUT_OF_SET`]

`incidental_estimate` is an integer, or the string `unestimable` with a reason,
and nothing else (SS-12). Whether a given connector reaches beyond its named
selector is a fact about its manifest, so the rule that a reaching connector's
`PERMITTED` carries the estimate is a runner rule. [schema for the shape]
[runner: `INCIDENTAL_ESTIMATE_MISSING`]

**The D5 line.** A `PROBE_EVENT RUN_START` requires a `COLLECT_EVENT PERMITTED`
parent in lineage, and that is the only parent that satisfies it.
`policy/lineage.yaml` carries this at subtype granularity, which ZMeta's
type-granular lineage policy cannot express (DV-11), and a `RUN_START` with no
such parent fires `SUBJECT_NOT_AUTHORIZED` rather than the generic
`LINEAGE_MISSING`, because the model's fixture map binds that entry to the
`run_permitted` rule (S7-R7). `tools/validate_layer_model.py` checks the entry by
name, so deleting it from the model fails the gate rather than widening dispatch.
[policy]

**A run matches its decision.** `RUN_START` carries the same `connector_id`,
`target_selector_type` and `motivated_by` as the `PERMITTED` it names. A run
whose fields differ from its decision's is a dispatch the gate never evaluated,
even though a permission resolves in its lineage; without this rule one
permission would authorize any number of runs against selectors and connectors it
never saw, which is the shape SS-5 records as a field declared, listed, printed,
and never read (`SUBJECT_NOT_AUTHORIZED`). Whether one permission may parent more
than one run is LM-R10 and is open. [policy] [unratified: LM-R10]

`REQUIRES_EXTENSION` and `REFUSED` render as their consequence and never as the
token (SS-7). This is a rendering rule the generator carries into
`rendering_rules`; it is not a wire check. [rendering]

### 5.3 What this section does not do

It does not evaluate the composed chain. Scope drift across three individually
legal hops (`SCOPE_DRIFT_UNADJUDICATED`) and a chain whose origin is an incidental
selector (`SUBJECT_NOT_AUTHORIZED` from `incidental_never_seeds`) are chain rules
the gate evaluates at Step 8, and their fixtures live in `conformance/gate/`.
[gate]

## 6. Observation: runs, items, and claims

Run, Item, Claim is the first of the five things the design says must be right
on day one, because retrofitting the item level rewrites every adapter
(`docs/PLAINSIGHT-design.md` section 8.2). The vocabulary keeps the three levels
apart structurally.

**`PROBE_EVENT`** is one tool invocation as three append-only events, because
decision D3 forbids filling in an end time later. `RUN_START` carries the
connector, its version and kind, the credential by id and never by value
(`doctrine/CREDENTIAL_LIFECYCLE.md` CR-3), the egress record EG-6 requires, an
argv template with values redacted, the motivating claim or null for a seed, the
target selector type, and the manifest hash. `ITEM` carries a locator, an outcome,
and the raw bytes by sha256 reference. `RUN_END` carries the exit code, an error
class from a closed adapter vocabulary, the item count, and the duration.
[schema]

A run from LOCAL is refused, not annotated. `egress.environment` admits only
`ISOLATED`, and a `RUN_START` whose source environment is anything else is
`EGRESS_ENVIRONMENT_REFUSED` (EG-1, EG-6). [schema] [policy]

Raw capture is stratum 0 and addressed by hash. Inline bytes make the raw blob
unenumerable and the shred unverifiable (RT-9), so `raw`, `raw_bytes`,
`stdout`, `stderr`, `body` and `response` are prohibited on every probe event.
[policy: `OBSERVATION_HAS_INLINE_RAW`]

An item is a locator plus an outcome. A field asserted by an item is a claim, and
folding it into the item collapses Run, Item, Claim to Run, Claim. `selector_type`,
`value`, `claims` and `proposes` are prohibited on a probe event.
[policy: `OBSERVATION_HAS_CLAIM`]

The filled argv is prohibited on every type, not only here, because it carries
the credential when a tool takes one as a flag, the measured toutatis defect
CR-3 records, and carries the selector value, which would put stratum-1 material
in a stratum-2 `RUN_START`. [policy: `CREDENTIAL_VALUE_IN_PAYLOAD`]

**`EXTRACT_EVENT CLAIM`** is one field asserted by one item, named by its datum
at the decode boundary. `selector_type` is a key in `ontology/selectors.yaml`, and
the vocabulary is closed at the corpus boundary and not only at the manifest: the
generated schema inlines the registry's keys as the field's enum, so an
unregistered type is `SELECTOR_TYPE_UNREGISTERED` in the schema itself, and a
registry change stales the schema until it is regenerated (S7-R4, D2, fixture 10).
[schema]

The name carries the provenance of the value (`CLAUDE.md` design gate 6). A masked
recovery hint is `email_hint_recovery_masked` and never `email`; a permutation
built from a name and a format is `email_generated_permutation`, whose registry
entry carries `provenance_state: GENERATED`. Section 8 says what that state costs
at the citation.

`temporal` carries `observed_at`, the time the program saw it, `asserted_at`, the
time the platform claimed, or null, and `time_provenance` from a closed set. This
replaces `zmeta-event-1.0`'s `timing_quality` wholesale while keeping its
discipline: mandatory, degraded by default, never repaired (DV-05). A producer
that fills `asserted_at` from `observed_at` has repaired a corrupt datum; the
model promises a fixture for it under `temporal_never_repaired` and the fixture
map does not carry one, which section 13 records. [schema]

`negative_state` is stored from the first version and rendered as evidence only
once a connector's canary has proven the field `always_present`. Until Step 12
delivers a canary proof, every `attempted_and_absent` is
`ABSENCE_CLAIMED_WITHOUT_CANARY`, and the corpus says so rather than exempting it.
[policy]

A claim carries no confidence, no review state, no identity, and no inference.
Each of those has its own code, so a diagnostic says which layer was collapsed:
`EXTRACT_HAS_CONFIDENCE`, `EXTRACT_HAS_REVIEW_STATE`, `OBSERVATION_HAS_IDENTITY`,
`OBSERVATION_HAS_INFERENCE`. [schema] [policy]

An item tagged at the extract boundary as carrying an injection signature
(SS-21) carries `injection_tagged` and a family; the tag dies with the case and the
family aggregated is a stratum-3 finding. [schema]

## 7. Inference and fusion: proposals and assertions

**`LINK_EVENT`** is a matcher's proposal and is always unaccepted. `accepted` is
required and `const: false`, so a proposal cannot be read as accepted by
omission, and a link arriving with `accepted: true`, or with `accepted_at`,
`accepted_by` or `review_state`, is `LINK_HAS_ACCEPTANCE` (fixture 12). Only
`matcher-*` may produce one (LM-R7). A proposal that names a cluster has skipped
the human act that creates one: `cluster_id`, `members`, `asserted_by`, `band`,
`rationale_codes` and `member_seams` are prohibited
(`INFERENCE_HAS_FUSION_STATE`). [schema] [policy]

The `model` block carries a `calibration_ref`, null today. No matcher in the
registry is calibrated, and an uncalibrated matcher may be an argv shape gate but
not an identity basis (`ontology/selectors.yaml` `matchers`). That rule binds at
the merge, not at the proposal, and `policy/matcher-calibration.yaml` un-defers
before the first matcher merges. [unratified]

**`IDENTITY_EVENT`** is an analyst's assertion, `CLUSTER`, or an affirmative
exclusion, `EXCLUDE`. Nothing enters fusion without a named human
(`docs/PLAINSIGHT-design.md` section 8.2 item 4): the type accepts only a human
identity from the session and no wildcard, and the check fires before any
semantic check, so a connector cannot mint a cluster (fixture 11). [policy:
`PRODUCER_NOT_ALLOWED`]

A cluster has at least two members (`CLUSTER_MEMBERS_INSUFFICIENT`), at least one
rationale code, and a seam per member: `member_seams` maps each member id to the
codes that hold for it, shown always and aggregated never (S7-R2,
`RATIONALE_MISSING`). The rationale codes are the closed set `h, e, n, b, i, t,
g, k` from the design's Merge Sheet; `k`, external knowledge, needs a note at
merge time (`RATIONALE_NOTE_MISSING`), and `g`, analyst gestalt, defers its note
to the export boundary (section 8). [schema] [policy]

`band` is `possible`, `likely`, or `almost_certain`, and it is the only ordinal in
the model (section 11). `almost_certain` requires rationale codes from at least
two distinct evidence classes, string, content, image, temporal, judgment, per
the `evidence_classes` map LM-R8 records; two string matches do not qualify
(`BAND_UNSUPPORTED`). [policy]

A cluster is refused as circular when a basis claim's selector traces to a
`GENERATED` origin, or to an observation produced by pivoting on a value one of
the members emitted, unless `circularity_override` carries a note, in which case
the inference carries a permanent circular badge (`MERGE_CIRCULAR`, fixture 16).
The walk is over lineage, which is why lineage is required here; the corpus
validator walks the case index and the runner walks the store. [policy]

A cluster carries no rollup. A strong pair plus a doubtful third is not a weak
cluster, and a rollup hides which member is the problem: `confidence`, `rollup`,
`weakest_seam`, `score` and `probability` are prohibited
(`CLUSTER_HAS_ROLLUP_CONFIDENCE`, fixture 15). It re-carries no raw
(`RAW_ABOVE_OBSERVATION`) and no matcher fields (`FUSION_HAS_INFERENCE_FIELDS`).
[schema] [policy]

## 8. Adjudication and state: acts, and sentences with citations

**`ADJUDICATE_EVENT`** is the set of analyst acts decision D3 made events rather
than columns. `review_state` is a projection over the latest `VERIFY` or
`DISPUTE`, never a stored field, and a `review_state` on an adjudication would be
the removed column reintroduced one layer up (`EXTRACT_HAS_REVIEW_STATE`). Nine
dispositions: `VERIFY`, `DISPUTE`, `PROMOTE`, `IGNORE`, `REVOKE`, `ACKNOWLEDGE`,
`OVERRIDE`, `NOTE`, `QUESTION`. Each names its target by reference and re-carries
none of its content (`RAW_ABOVE_OBSERVATION`). Only a human identity produces one.
[schema] [policy]

The first parent in `based_on` is the target, and each disposition has a set of
target types it may act on: verifying a cluster or revoking a claim is a category
error (`LINEAGE_PARENT_TYPE_INVALID`). The type-granular `allowed_targets` block
and the subtype-granular `required_parents` block disagree for four dispositions
about which link subtypes are targets; both are emitted as the model states them,
and LM-R11 records the disagreement. [policy] [unratified: LM-R11]

A `PROMOTE` of an item to an `Account` carries an anchor selector whose registry
entry has `may_anchor_entity: true`. Two selectors qualify, `platform_uid` and
`channel`; an account anchored on a handle renders a handle-owner change as
ordinary drift when it is an identity catastrophe (`SELECTOR_ANCHOR_PROHIBITED`,
fixture 3, `docs/PLAINSIGHT-design.md` section 2.2). A `PersonCandidate` is
materialized only here, by an analyst act, never by a connector. [policy]

`DISPUTE` and `REVOKE` carry `reason`. `IGNORE` carries it when the target supports
a live cluster or was promoted by another analyst, which is a fact about the case
and a runner rule (`ADJUDICATION_REASON_MISSING`). [schema] [runner]

**`ASSESS_EVENT SENTENCE`** is one assessment sentence with live citations, and it
is the DRAFT export boundary's only input. Every finding carries the subject
class it came from, on the finding itself and not two clicks away, because the
mixed figure is the one that reaches a summary (SS-18, `SUBJECT_CLASS_MISSING`).
[schema] [policy]

Citations are the bond between a sentence and the claims that support it, live
rather than copied. A sentence has at least one citation and every citation's
`ref` resolves in the sentence's own lineage (`CITATION_MISSING`). A cited claim
has an `ADJUDICATE_EVENT VERIFY`, because adjudication on citation is the
mechanism the design turns on: roughly fifteen real reviews per case instead of
four hundred fake ones (`CITATION_UNADJUDICATED`). [policy]

Two citation rules carry the honesty the registry exists for. A citation's
`cited_as` equals the cited claim's `selector_type` or is null; a masked hint
cannot satisfy a citation for the address it constrains (`HINT_CITED_AS_VALUE`,
fixture 1, D2's flagship case). A claim whose selector carries
`provenance_state: GENERATED` is cited only after an `ADJUDICATE_EVENT PROMOTE`
with `promotion_kind: generated_to_observed` exists for it
(`GENERATED_CITED_AS_OBSERVED`, fixture 2). [policy]

A citation of a `possible`-band cluster carries a `caveat`, and a citation of a
cluster whose rationale includes `g` carries the `note` the merge deferred here.
The model marks both runtime because the cited cluster's fields are on another
event; a corpus-aware validator resolves them, so `tools/validate.py` evaluates
both, and the runner will too (`CITATION_CAVEAT_MISSING`, `RATIONALE_NOTE_MISSING`).
[policy] [runner]

`geo` is optional, unlike `zmeta-event-1.0`'s state payload, because a
person-centric assessment usually has no position and a place-name inference
with no coordinate is a list entry, never a pin (DV-08). It has no declared
shape and is emitted open (S7-R3). [schema]

## 9. System events

**`SYSTEM_EVENT`** carries diagnostics, connector health, coverage intervals, the
three retention acts, credential state, and two heartbeats whose absence is a
rendered degraded state rather than a silence (RT-12).

A diagnostic never carries the value it is reporting on, or the telemetry becomes
the PII surface the gate exists to prevent (RT-19): `value`, `offending_value`,
`raw`, `content`, `body`, `text`, `selectors` and `selector_value` are prohibited
(`DIAGNOSTIC_CARRIES_VALUE`). A `SCHEMA_VIOLATION` names the offending event by
id and its reason by a declared code, drawn from the closed vocabulary, so free
text here is the failure `policy/violation-codes.yaml` exists to prevent
(`ENUM_VALUE_INVALID`). [schema] [policy]

`CONNECTOR_HEALTH` carries one of `HEALTHY, DEGRADED, SUSPECT, DOWN, UNVERIFIED`
and `CREDENTIAL_STATE` carries one of `active, quarantined, burned`; the generator
splits the `state` enum by subtype and CR-2's three states admit no fourth
(LM-R9). A quarantine carries its written exit criterion (CR-6,
`CREDENTIAL_QUARANTINE_NO_EXIT`) and a burn carries the `finding_ref` that makes
the recording the load-bearing half (CR-7, `CREDENTIAL_BURN_NO_FINDING`). [schema]
[policy]

The retention acts, `RETENTION_EXTENSION`, `RETENTION_FREEZE` and
`RETENTION_RENEWAL`, are emitted by a named human only; a wildcard cannot be an
author (RT-5, RT-17, LM-R5). A renewal names its obligation and its expected
resolution date, which is what separates a freeze from a habit
(`FREEZE_RENEWAL_UNJUSTIFIED`), and is parented on the freeze or renewal it
extends, so the second renewal can render its escalated state (RT-17). Their
`reason` sentences are stratum 2 and survive the shred, and the rule that they
describe no person is a review rule (`REASON_NAMES_SUBJECT`). [schema] [policy]
[review]

`SHRED_RECEIPT` carries `checks_passed` as exactly `[1, 2, 3, 4, 5]`, all five of
RT-9's checks, each once; `min_items: 5` over an enum was the earlier shape and it
accepts one check counted five times. `SHRED_FAILED` carries `halt_system_wide:
true` as a constant, because RT-11 makes a shred failure block every new run
system-wide and the event cannot say otherwise. [schema]

## 10. Lineage and producer authority

**Lineage.** Every parent resolves to an event in the same case, because the
shred is per case and cross-case lineage does not exist
(`LINEAGE_PARENT_UNRESOLVED`, `LINEAGE_CROSS_CASE`). A parent's type and subtype
are in the child's allowed set (`LINEAGE_PARENT_TYPE_INVALID`), a subtype that
requires a parent has one of the parents it requires (`LINEAGE_MISSING`, or the
rebound code of section 5), and any payload-level provenance, `based_on` on a link
or `basis_claims` on a cluster, is a subset of the envelope's `based_on`
(`LINEAGE_PAYLOAD_BASED_ON_NOT_SUBSET`). Every mode is `reject` and there are no
profiles: one store and one consumer make an unresolved parent an error rather
than a tolerated link loss (DV-07). [schema for requiredness] [policy]

`policy/lineage.yaml` is emitted at subtype granularity for `allowed_parents` and
`required_parents`, and its type-granular `matrix` is a rendering reconciled by
`tools/validate_layer_model.py` and never the generator's input. The reason is
D5: the requirement that a run be parented on a permission is a subtype pair,
`COLLECT_EVENT PERMITTED`, and a type-granular policy cannot express it (DV-11).

**Producer authority.** Every type requires a match, and an unmatched producer is
`PRODUCER_NOT_ALLOWED` before any semantic check runs. Four wildcards exist:
`connector-*` for items and claims, `extractor-*` for claims, `matcher-*` for
links, `runner-*` for run start and end and the eight machine system subtypes.
Two named producers exist: `runner-subject-guard` for every gate decision, and
`manual` for analyst-pasted evidence on probe and extract events, given identical
lineage treatment and distinguished by producer (LM-R6). Authorization, identity,
adjudication, assessment, and the three retention acts accept only a named human
identity from the session. [policy]

The human identity list is deployment configuration read by the runner. It is
never a wildcard and never lives in a tracked file. The conformance corpus is not
a deployment and declares one synthetic analyst, `analyst-example`, which
`tools/validate.py` accepts by default and a deployment overrides with
`--human-identity`.

Composition follows the model's rule: a type's wildcards, named producers and
human-identity flag apply to every subtype unless `by_subtype` names that
subtype, in which case the by-subtype entry replaces them and is the whole
authority for it. A generator reading the model without that rule made
`connector-*` a legal producer of `RUN_START`, which LM-R6 refuses by name, and
`runner-*` an author of a retention freeze, which RT-17 refuses. The rule is in
the model's header and `policy/producer-authority.yaml` carries the composed
result under `effective`, one entry per type and subtype, so a reader need not
compose it again. [policy]

## 11. Confidence, and the naming that replaces it

No numeric confidence exists anywhere at `pse-event-0.1`. The envelope key is
reserved and refused on every event, `confidence`, `score` and `probability` are
prohibited in every payload, and two types carry a narrower code so a diagnostic
says which layer was miscast: `EXTRACT_HAS_CONFIDENCE` on a claim and
`CLUSTER_HAS_ROLLUP_CONFIDENCE` on a cluster; every other type fires
`CONFIDENCE_PROHIBITED`. This inverts `zmeta-event-1.0`, which requires
confidence on its inference, fusion and state events (DV-06). [schema] [policy]

The decision is LM-R2 and it is open. Two rank-7 sources conflict:
`docs/PLAINSIGHT-FOUNDATION.md` section 4.2 requires confidence on a link, and
`docs/PLAINSIGHT-design.md` section 8.4 kills all machine confidence arithmetic
because there is no calibration ground truth anywhere in the system. `CLAUDE.md`
design gate 6 forbids an unlabelled number. Reversing the decision touches five
sites in the layer model, in an order the model's `confidence` section states,
and `tools/validate_layer_model.py` refuses a model with any proper subset of the
five applied, so a half-made reversal cannot ship. [unratified: LM-R2]

What replaces a number is a name. The cluster band is the one ordinal, kept
because it is mechanically consequential (section 7). Every other statement of
strength lives in the selector type, whose name carries the provenance of the
value: a hint, a permutation, a handle interval, a platform id. The consumer
adjudicates truth (`CLAUDE.md` design gate 6).

## 12. Retention, shred, and egress

**Stamp target. `doctrine/SUBJECT_SELECTION.md` SS-14 item 6 names this section
among the eight artifacts stamped before any collection.** This section explains
how the strata of `doctrine/RETENTION.md` and the boundary of `doctrine/EGRESS.md`
appear on the wire. It decides nothing about what may be retained or what may
leave: that is rank 1, and the compiled form is `policy/retention.yaml` at
Step 8.

### 12.1 Every event is reachable by the shred

`case_id` is required on every event without exception, and every parent is in
the same case. Decision D4 keys the crypto-shred on `case_id`, so there is no
event the sweep cannot reach and no lineage edge that crosses a shred boundary.
[schema] [policy]

### 12.2 Each payload declares its stratum, and the surviving strata carry no subject value

RT-1 declares an object's stratum at write time, never at delete time. The model
declares it per type and, where subtypes differ, per subtype, and
`policy/semantics.yaml` carries the declaration under each type's `retention`.
The envelope is stratum 2 everywhere, so the skeleton of every event survives
the shred and the record of an experiment stays auditable from the development
side (EG-5).

| Payload | Stratum | Carries subject values | Crosses to LOCAL |
|---|---|---|---|
| `AUTHORIZE_EVENT` | 2 | no | yes |
| `COLLECT_EVENT` | 2 | no | yes |
| `PROBE_EVENT RUN_START`, `RUN_END` | 2 | no | yes |
| `PROBE_EVENT ITEM` | 1 | yes, the locator | no |
| `EXTRACT_EVENT` | 1 | yes | no |
| `LINK_EVENT` | 1 | yes, as a derived statement | no |
| `IDENTITY_EVENT` | 1 | yes | no |
| `ADJUDICATE_EVENT` | 1 | yes, analyst prose about a person | no |
| `ASSESS_EVENT` | 1 | yes | no, except RT-18's disclosure export to an agency |
| `SYSTEM_EVENT` | 2 | no | yes |

RT-2 makes a subject-derived value in a surviving stratum a defect rather than a
judgment call, and the vocabulary enforces it in the shape of the prohibited
groups on the stratum-2 types: the authorization record is carried by reference
and never inlined (`AUTHORIZATION_RECORD_INLINED` on authorize, collect and
system events), a diagnostic carries no value (`DIAGNOSTIC_CARRIES_VALUE`), a run
carries no filled argv (`CREDENTIAL_VALUE_IN_PAYLOAD`), and the `reason`
sentences on stratum-2 events describe no person (`REASON_NAMES_SUBJECT`). The
first three are machine rules. The fourth is a free sentence a person writes,
and LM-R4 records that the only thing between it and a described subject is the
rule and the review it names. [policy] [review]

The `AUTHORIZE_EVENT` payload sits in stratum 2 by LM-R4, on the argument that it
carries the act by reference and the denylist refuses every field that could
carry a subject value. What the mechanism delivers is narrower than "structurally
forbidden", because a name denylist passes a value re-keyed under a name it does
not carry; `additionalProperties: false` at every declared level is what narrows
that residual, and the residual is stated in `policy/semantics.yaml` rather than
claimed away. [unratified: LM-R4]

### 12.3 The shred is proven by an event, and a failure stops everything

`SHRED_RECEIPT` is the proof the shred happened (RT-10): a receipt hash, a blob
count, and all five of RT-9's checks, each once, as a constant array.
`SHRED_FAILED` names the failed check and carries `halt_system_wide: true`, which
RT-11 makes the consequence of any shred failure. `SWEEP_HEARTBEAT` and
`RECONCILE_HEARTBEAT` carry their next due time, so an absent heartbeat is a
rendered degraded state (RT-12). The sweep, the reconciler and the verifier that
emit these are Step 11 and do not exist yet; the vocabulary they will speak does.
[schema]

### 12.4 Egress is refused at the run and at the crossing

Two environments exist, and the boundary between them is which one may execute a
connector (EG-1). A `RUN_START` records the environment and its egress identity
(EG-6), and a run from LOCAL is `EGRESS_ENVIRONMENT_REFUSED` rather than
annotated, because a run that already reached a platform cannot be un-run.
[schema] [policy]

A payload crosses to LOCAL if and only if its stratum is 2, 3, or 4 (EG-5). The
crossing check fires `EGRESS_STRATUM_REFUSED` when a stratum-0 or stratum-1
payload is presented at the boundary. That check runs where the crossing happens
and not in the corpus validator, so the code is declared, is emitted by the
egress section of the model alone, and has no fixture in the corpus. [runner]

The one path by which a whole non-synthetic case leaves is RT-18's disclosure
export, and it goes to an agency rather than to LOCAL. The state layer's
`ASSESS_EVENT` is the DRAFT export boundary's only input; RT-18 reads more than
this layer, and `doctrine/DISCLOSURE.md`, which RT-18's existence made owed, does
not exist yet.

## 13. Readings, divergences, and the conformance corpus

### 13.1 Readings the generator took

Where the layer model is silent, `tools/generate_pse.py` took a reading rather than
inventing a rule, wrote it into the schema's `$comment` and into
`policy/semantics.yaml` under `readings`, and it is restated here for the
operator to confirm or reverse. Reversing one is an edit to the generator and a
regeneration, never a hand edit to a generated file. Each is [unratified].

| Id | Reading |
|---|---|
| S7-R1 | Which optional fields a subtype may carry. Required where the model requires it; a field no subtype requires and no rule names is legal on every subtype of its type; a field named in a rule's condition follows that rule's subtype scope; a field a rule requires is legal where the rule can hold, narrowed by the condition's value when the field's enum is split by subtype, and on every subtype for a runtime rule. The cost is visible in `policy/semantics.yaml` under each type's `allowed`: a probe's six free optionals are legal on all three phases, and an adjudication's `entity_id` on all nine dispositions. The remedy, if wanted, is an optional list per subtype in the model, which is Class B |
| S7-R2 | `member_seams` maps member uuids to non-empty arrays of rationale codes |
| S7-R3 | `geo` and the two `raw_span` arrays have no declared shape and are emitted open |
| S7-R4 | A registry-bound field inlines the registry's keys as its enum, so the vocabulary is closed in the schema and a registry change stales it |
| S7-R5 | A prohibited name at depth zero is refused by the schema as an unknown property and named by the group's code, so the group's code is the sole code; below depth zero, inside an open object, the denylist fires the group's code and `LAYER_COLLAPSE_NESTED` together |
| S7-R6 | Lineage requiredness is taken per subtype from `lineage.required_by_subtype`, which wins where `required_envelope_fields` disagrees |
| S7-R7 | A `required_parents` entry the fixture map binds to a `code_source` rule emits that rule's code; the D5 line fires `SUBJECT_NOT_AUTHORIZED` |

Two readings in the model shape the schema and are the operator's to stamp:
LM-R1, which nine event types D6 named, with the probe split at subtype level;
and LM-R2, that no numeric confidence exists (section 11). The other nine
readings and the ten in the selector registry are listed in
`_session-artifacts/2026-09-03-plainsight-doctrine-review-2/DECISIONS.md` parts 3
and 4.

### 13.2 Divergences from zmeta-event-1.0

`spec/layer-model.yaml` records eleven under `divergences_from_zmeta`, DV-01 to
DV-11: the version and derivation fields replacing `zmeta_version`; `case_id` new;
nine person-centric types replacing six sensor types; two environments replacing
five node roles; `temporal` replacing `timing_quality`; confidence inverted from
required to prohibited; profiles dropped; `geo` optional on the state layer;
publish and receive timestamps dropped; `sensor_id` dropped; and the lineage
policy at subtype granularity. Three more surfaced in generation and belong in
the register at Step 9: the date-time pattern taken from the 1.1.0 lane rather
than 1.0's; `additionalProperties: false` on every payload where ZMeta leaves
its payloads open; and the producer-authority policy keyed by producer with an
`effective` table, where the FOUNDATION sketch keyed it by type. The register,
`spec/divergence-register.yaml`, and its validator derive the required entry list
from a diff of the two schemas rather than from this prose, which is what keeps
it from going stale.

### 13.3 The corpus, and what it does not cover

`conformance/must-pass.jsonl` is one synthetic case in which every one of the
thirty-seven subtypes appears and the events form one lineage chain from a grant
to an assessment sentence. `conformance/must-fail.jsonl` breaks one thing per
fixture: the thirteen fixtures the model's map assigns to it, by name; the D5
shape twice; one fixture per prohibited group of every type; and one per
envelope, lineage, producer and rule code that a machine emits. Every fixture the
model marks `expect_only` sets it, and the grader refuses the corpus if one does
not. No value appears in either file; every selector-shaped value is a bracketed
placeholder and every identifier is a uuid derived from a label.

Five declared codes have no fixture here, each for a stated reason.
`SCOPE_DRIFT_UNADJUDICATED` is a chain rule graded from `conformance/gate/` at
Step 8. `EGRESS_STRATUM_REFUSED` fires at the crossing, not in a corpus.
`INCIDENTAL_ESTIMATE_MISSING` and `ADJUDICATION_REASON_MISSING` are runner rules
whose condition is a fact about the case. `REASON_NAMES_SUBJECT` is a review rule
with no mechanism. `tools/build_corpus.py` prints this list on every build so it
cannot grow silently.

One fixture the model promises does not exist: `temporal_never_repaired` says
the corpus carries a fixture for a producer that fills `asserted_at` from
`observed_at`, and the fixture map does not name one. Adding it needs
`tools/validate_layer_model.py` and `docs/THE-GAMEPLAN.md` section 2.3 edited
together, and it is recorded here rather than added quietly.

### 13.4 What would have to be true before anyone outside this project is told anything

`CONFORMANCE.md` section 6 states the bar. As of this document two of its five
conditions hold: this contract exists with a version, and the two corpora are
populated, green, and graded by a runner that implements `expect_only` and
short-circuit disclosure. The divergence register, a real connector through all
five rungs, and a kernel gate with no pending entry do not. The correct external
statement is still the one in `CONFORMANCE.md` section 1 and nothing stronger.
