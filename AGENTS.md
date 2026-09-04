# PLAINSIGHT Agent And Maintainer Guide

This repository holds a governed specification (PSE) and the application built
on it (PLAINSIGHT). Treat it as a governed specification, not as an application
codebase where a local need can redefine the data model.

It also collects, holds, and correlates information about identifiable people.
That fact changes the operating model in ways `ZMeta/zmeta-spec/AGENTS.md` does
not have to address, and the differences are marked below.

Read before touching a governed artifact:

```text
CLAUDE.md
doctrine/SUBJECT_SELECTION.md
doctrine/RETENTION.md
doctrine/EGRESS.md
doctrine/CREDENTIAL_LIFECYCLE.md
doctrine/DOCTRINE_STATUS.md
```

## 1. What this repository is

PSE is a **private dialect** derived from `zmeta-event-1.0`. It does not claim
upstream ZMeta compatibility and must not be described as ZMeta-conformant.
`ZMeta/zmeta-spec/AGENTS.md` permits this on one condition:

> "If you change those surfaces locally, treat the result as a private fork or
> dialect. Do not claim upstream compatibility unless the change has versioning,
> documentation, conformance evidence, and release governance."

Versioning lives in `spec/pse-semantics-contract.md`. Documentation of the delta
lives in `spec/divergence-register.yaml`. Conformance evidence lives in
`conformance/`. Release governance lives in this file.

## 2. Authority order

As in `CLAUDE.md` section 2, repeated here normatively. Statutory obligations,
platform terms of service, and commitments made outside this repository sit
above every document in it.

1. `doctrine/SUBJECT_SELECTION.md`, `doctrine/RETENTION.md`,
   `doctrine/EGRESS.md`, `doctrine/CREDENTIAL_LIFECYCLE.md`
2. `spec/pse-semantics-contract.md`
3. `schema/*.json`, `ontology/selectors.yaml`, `policy/*.yaml`,
   `spec/layer-model.yaml`, `spec/divergence-register.yaml`
4. `AGENTS.md`
5. `CONFORMANCE.md`
6. Validators and tests
7. `docs/PLAINSIGHT-design.md`, `docs/PLAINSIGHT-FOUNDATION.md`
8. `CLAUDE.md`, `docs/DOCUMENT_STANDARD.md`, `README.md`, worklog, handoff

## 3. Change classes

Classes A through E are ZMeta's, from
`ZMeta/zmeta-spec/docs/zmeta_change_governance.md`. Class F is new here.

- **Class A, advisory documentation.** README, examples, explanatory docs,
  worklog, handoff. No governed artifact changes.
- **Class B, governed baseline.** Semantic contract, schemas, ontology, policy
  YAML, conformance fixtures, validators, layer model.
- **Class C, runtime or reference.** Runner, connectors, adapters, application
  code, tools that implement the baseline.
- **Class D, versioned semantic branch.** A change to the event vocabulary, the
  layer model, or envelope semantics. Requires a version bump and a divergence
  register entry.
- **Class E, release publication.** Tags, signatures, checksums, packaged
  artifacts, anything published outside the team.
- **Class F, authority.** Any change that alters who may be a subject, what may
  be collected, how long anything is held, or what may leave the machine.

Three rules about the classes themselves.

1. A change carries the **highest** class it touches.
2. **Class F is defined by effect, not by path.** The reviewer's question is
   whether, after this change, any subject, bystander, selector, or retained
   object could be reached that could not be reached before. A row added to an
   allowlist in a file that otherwise looks like Class B is Class F.
3. Class C here diverges from ZMeta's Class C by adding a **design-record
   requirement**. A runtime change that alters observable behaviour updates the
   design record in the same change. The program has already failed this way:
   `docs/PLAINSIGHT-FOUNDATION.md` records that the ZISR COP's documented
   behaviour and implemented behaviour drifted in both directions, and the worse
   direction was the undocumented good patterns.

Class F requires the operator's explicit per-item ratification with a dated
stamp in `doctrine/DOCTRINE_STATUS.md`. An agent may draft a Class F change and
may never decide one. Per R6 as amended 2026-08-27, an agent may execute the
commit of a decision the operator has made, on a per-act instruction, with the
operator as author. Section 4 carries the full reading.

## 4. Execution Limits

This section replaces ZMeta's Release Limits and reads at the same authority.

In ZMeta the one act with irreversible external consequence is publishing, and
nothing an agent does to a schema file leaves the machine. Here the irreversible
act is executing a connector against a live platform. That reaches a third
party, writes to a platform's logs, spends credential heat, and cannot be undone
by any control this repository contains.

- **No agent executes a connector, adapter, or runner against a live platform,
  account, or person.** Not to check a hypothesis, not to confirm liveness, not
  to run the known-positive canary. Canaries are operator-run during onboarding.
- **No agent adds, edits, or removes an entry** in any allowlist, NEVER list,
  authorization file, or `retain_until` value. Drafting a proposed diff is
  permitted. Applying it is Class F.
- **No agent extends a case past `retain_until`**, disables a shred job, or
  edits a scheduled reconcile.
- **No agent commits a cassette, fixture, screenshot, or log excerpt containing
  data about a person**, including into a scratch directory inside the
  repository.
- **No agent writes a selector value, handle, email, phone number, or case
  subject name into a tracked file.** This includes worklog entries and commit
  messages.
- **No agent decides a Class F change.** Drafting one is permitted and expected.
  Per R6 as amended 2026-08-27, an agent may execute the commit or push of a
  Class F change the operator has decided, on the operator's explicit
  instruction for that act, with the operator as author. The instruction is
  per-act and does not stand.
- Do not create tags, push branches, upload releases, or generate signatures
  unless explicitly asked.
- Do not commit credentials, session tokens, cookies, or private keys.

## 5. Required local workflow

Inspect current state before editing:

```bash
git status --short --branch
git log --oneline --decorate -n 10
```

Run the narrowest focused check first, then the kernel gate:

```bash
python tools/validate_doctrine.py
python tools/validate_hygiene.py
python tools/validate_layer_model.py
python tools/validate_ontology.py
python tools/validate_cast.py --placeholder-scan
python tools/validate_conformance.py --kernel-gate
git diff --check
```

`make preflight` runs the same battery the pre-commit hook runs, and
`make validate-kernel` runs the aggregator. The gate battery is defined once, in
`KERNEL_GATE` inside `tools/validate_conformance.py`, so a new check joins it
there rather than in every document that quotes a command.

**What these gates actually cover, stated so a green run is not read as more
than it is.** The governed artifacts checked today are the doctrine corpus
(criterion definitions, per-criterion stamps, cross-references in both
directions, reconciliation against the pin of record, prose counts), the voice
standard, table structure, citations against the artifact register, the handoff
and worklog caps, the tools-to-gates inventory, the layer model in
`spec/layer-model.yaml` (nine types, discriminators, denylists, lineage,
producer authority, strata, and the D5 parent on every run), the selector
registry in `ontology/selectors.yaml` (the closed vocabulary, anchor
eligibility, the constraint rule, prohibitions, matchers, and its codes
reconciled against the layer model), the cast draft in `synthetic/` (the
checkable half of SS-3, the confuser pair, the partition, the seal, and no
filled value while unsealed), and the telemetry recorder in `tools/gate_log.py`
(HY-1 and RT-19 exercised by `tools/tests/test_gate_log.py`). The schema,
policy, authorization and connector checks do not exist because the artifacts
they would check do not exist. `--kernel-gate` prints each of them as PENDING
with the step that delivers it, and a stubbed or pending check is never counted
as a pass. The three YAML validators need PyYAML, which CI installs and a local
checkout must have.

`tools/validate_retention.py --repo-scan` is a wired stub that checks nothing.
That is D-001, it is scheduled for Step 8, and the aggregator reports it as
STUB rather than green.

If a required check cannot be run, document the reason in the handoff.

## 6. Documentation matrix

When a governed artifact changes, the matching surfaces move in the same change.

Every row also updates `CHANGELOG.md` and both process records, which is
`ZMeta/zmeta-spec/AGENTS.md`'s rule rather than a local one, and it is stated
here because the Schema row below used to be the only place this repository named
the changelog.

| Changed | Also update |
|---|---|
| Doctrine | `DOCTRINE_STATUS.md`, the compiled policy YAML, the enforcing mechanism, its test |
| Semantic contract | `schema/`, `spec/layer-model.yaml`, `spec/divergence-register.yaml`, conformance fixtures |
| Schema | Divergence register, must-pass and must-fail corpora, `CHANGELOG.md` |
| Ontology | Connector manifests that emit the affected type, corpus coverage check |
| Policy | The validator that reads it, its fixtures, `policy/violation-codes.yaml` |
| Connector manifest | Cassettes, fixtures, connector tests, health canaries |
| Tooling | `Makefile` targets, `AGENTS.md` section 5 if the gate set changed |

## 7. Ratification

Doctrine items carry a per-item marker with the item, the date, and the
ratifier. Conclusion is ratified separately from basis. The standard phrasing is
from `zisr-recon/docs/ENTRY_CRITERIA.md`: no emitter should be built on a
rationale the operator was never shown.

**Unratified binds nothing, and the mechanism reads the stamp rather than the
file.** There must be a test asserting that an unratified criterion refuses
rather than permits. The alternative repeats the `zisr-recon/src/zisr_recon/guard.py`
defect one level up, where an expiry check was intended and never written.

One partially stamped item does not stamp its file.

## 8. Handoff standard, and the closeout

Inherited from `ZMeta/zmeta-spec/AGENTS.md` with one addition this repository
needs. A completed change leaves the next maintainer able to answer five
questions:

- what changed and why;
- whether it changed doctrine, semantics, schema, policy, ontology, runtime,
  docs, or release packaging;
- what validation ran and what passed;
- whether a release baseline changed or only the working branch;
- what remains open or intentionally deferred.

**A closeout runs the battery, updates the records, and commits.** Those are one
act rather than three, because a session whose work is verified and recorded and
then left uncommitted has produced nothing a later session can rely on. Git
history is also the one store a crypto-shred cannot reach, which cuts the other
way here: the same permanence that makes a committed selector unrecoverable makes
a committed record durable. The order is the battery, then the records, then the
commit, because a record written after the commit describes a tree that is
already in the history.

The surfaces a closeout moves, in addition to whatever the change touched:

| Surface | What it carries |
|---|---|
| `CHANGELOG.md` | One entry per commit that changed a governed artifact, naming what did **not** change |
| `docs/plainsight_worklog.md` | The chronological record, added to and never restyled |
| `docs/plainsight_handoff.md` | Current state only, rewritten, answering the five questions above |

**The addition this repository needs, and it is the one rule here that is not
ZMeta's.** A closeout commit carries no Class F change the operator has not
decided. An agent may draft one, and per R6 as amended may execute the commit of
a decision the operator has made, so the drafts wait outside the commit as a
patch with its argument beside it rather than landing inside it. A closeout that
quietly includes a doctrine amendment has made the ratification a formality, which
is the failure the whole pin-of-record apparatus exists to prevent.
