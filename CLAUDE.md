# CLAUDE.md: Working Guide for the PLAINSIGHT Repo

Orientation for any Claude Code session working in this repository. This file is
**advisory** (Class A) and **non-normative**. It captures the intent and the
decision gates that keep work aligned. It does not define compliance and it does
not replace `AGENTS.md`.

**Authority order.** When this file conflicts with a governed source, defer to
the order in section 2 below, which `AGENTS.md` repeats normatively.

Read `AGENTS.md` before touching any governed artifact. Read
`doctrine/SUBJECT_SELECTION.md` and `doctrine/RETENTION.md` before touching
anything that collects, stores, or exports.

## 1. North Star

This repository holds two products.

**PLAINSIGHT** is an OSINT common operating plane. It consolidates
person-centric OSINT tools, standardizes their input and output, automates the
pivots between them, and puts an analyst in front of one worked picture instead
of six terminal windows. Its product is the citation chain: every sentence in an
assessment walks back through a cluster, through rationale claims, through
items, through a run, to argv and raw bytes.

**PSE**, the PLAINSIGHT Semantic Envelope, is a ZMeta-derived semantic dialect
for person-centric OSINT. It is an event envelope, a closed selector ontology, a
policy pack, a conformance corpus, and the validators that enforce all of it.

PSE serves PLAINSIGHT. PSE defines what may be said. PLAINSIGHT defines how it
is shown. Each is authoritative in its own lane and subordinate across lanes.

PSE is a private dialect and never claims upstream ZMeta compatibility.
`ZMeta/zmeta-spec/AGENTS.md` licenses exactly this, on one condition:

> "If you change those surfaces locally, treat the result as a private fork or
> dialect. Do not claim upstream compatibility unless the change has versioning,
> documentation, conformance evidence, and release governance."

Those four conditions are why `spec/`, `docs/`, `conformance/`, and `tools/`
exist in the shapes they do.

PSE exists because ZMeta cannot carry this data. The problem is narrow. ZMeta's
envelope is not geospatially biased, and its lineage and layer separation fit
person-centric OSINT well. Its observation vocabulary is a closed enum with no
legal token for an HTTP or API observation, so the fork keeps almost everything.
`docs/PLAINSIGHT-FOUNDATION.md` records the measurement behind that decision.

## 2. Authority order

Statutory obligations, platform terms of service, and any commitment the
operator has made outside this repository sit above every document in it. No
file here grants an authority the operator does not already hold.

When two governed sources conflict, the higher number loses.

1. `doctrine/SUBJECT_SELECTION.md`, `doctrine/RETENTION.md`
2. `spec/pse-semantics-contract.md`
3. `schema/*.json`, `ontology/selectors.yaml`, `policy/*.yaml`,
   `spec/layer-model.yaml`, `spec/divergence-register.yaml`
4. `AGENTS.md`
5. `CONFORMANCE.md`
6. Validators and tests in `tools/` and `connectors/*/tests/`
7. `docs/PLAINSIGHT-design.md`, `docs/PLAINSIGHT-FOUNDATION.md`
8. `CLAUDE.md`, `docs/DOCUMENT_STANDARD.md`, `README.md`, worklog, handoff

**Why doctrine outranks the semantic contract.** ZMeta places its semantics
contract at rank 1 because in ZMeta every failure mode is a failure of meaning.
This repository has a failure mode the contract cannot see. A PSE event that is
schema-valid, ontology-clean, correctly layered, honestly timed, and fully
lineaged, describing a person who was never permitted to be a subject, passes
every check at ranks 2 through 6 and is still the thing this project must not
do. No validator catches it, because no validator knows who a selector refers
to. A rule that no lower rank can evaluate has to sit above them all.

The inverse bounds the doctrine. Doctrine is authoritative only on who may be a
subject, what may be retained, and what may leave. It has no opinion on field
names, layer boundaries, or interface design. A doctrine document that starts
adjudicating schema questions has escaped its lane and gets cut back.

## 3. Design gates: apply to every change

1. **Prohibition is structural.** A rule that lives in a README is not a rule. A
   change that introduces a constraint is not done until the constraint is a
   schema `false`, a policy denylist, a gate that refuses, or a job that runs,
   covered by a test that fails when the constraint is removed. This is gate 1
   because the program has one measured seam, recorded in
   `docs/PLAINSIGHT-FOUNDATION.md`: mechanisms get written where the failure
   mode is technical, and sentences where it is procedural.

2. **Subject selection is upstream of everything.** Ask whether the change
   widens who can be collected on, or how far a pivot can reach. If it does, it
   is Class F regardless of which file it touches. A subject-widening change
   rarely looks like one. A row added to an allowlist, a relaxed regex, a new
   connector `kind`, and a bystander disposition of `retain` are all one-line
   diffs in files that otherwise read as Class B.

3. **Ground truth or it is not a test.** A change claiming a capability works
   names the subject it was scored against and how the answer was known. If the
   answer could not be known, the change claims coverage rather than
   correctness, and says so in those words. This does not cap collection depth,
   connector count, or pivot depth against a scoreable subject. Depth against a
   scoreable subject is the experiment.

4. **The bystander is a first-class object.** Every connector that reaches
   beyond its named selector declares what it reaches and what happens to that
   data. An undeclared bystander class is refused at manifest validation rather
   than flagged.

5. **Collect the minimum an analyst needs to adjudicate.** This is ZMeta's
   consumer-sufficiency gate with the consumer changed to an analyst at the
   Merge Sheet. In ZMeta, producer-completeness costs bandwidth. Here it costs a
   person's data. Both edges point the same way, so data minimization is not a
   tax on the capability work.

6. **Honesty end-to-end. No laundering, no invented numbers, no unlabelled
   datums.** Never make degraded, stale, low-confidence, or promoted data look
   clean. The consumer adjudicates truth. A field name carries the provenance of
   its value: `email_hint_recovery_masked` rather than `email`,
   `email_generated_permutation` rather than `email`, `handle` rather than
   `platform_uid`.

7. **The case is the source of truth. Every projection is lossy and
   one-directional.** The export boundary enforces citation completeness and
   data minimization together. A projection complete in citations and
   unminimized in content has passed half a gate.

8. **Closed vocabulary, cheap additions, outer rings first, then stop.** Solve
   needs through policy, config, manifests, and adapters before touching schema
   or core semantics. A selector registry addition is reviewed once and benefits
   every connector, so it is expected to be routine. A new connector `kind` is a
   platform release. New tools are free. New shapes are not.

## 4. How we work here, and voice

Two registers, with a rule for which applies where.

**Register 1, repo prose.** Inherited whole from `ZMeta/zmeta-spec/CLAUDE.md`.
Flat, declarative technical prose: simple, clean, upfront and detailed,
professional without sounding like a sales pitch. Avoid em dashes as a
connector; use a comma, colon, semicolon, or a second sentence. Avoid inversion
for emphasis. Avoid sentence fragments and mid-sentence bolding used for rhythm,
with bold reserved for genuine scanning aids such as a bullet's leading label.
Avoid sentences opening with And, But, or So to carry cadence. Avoid metaphor
standing in for a checkable statement. Do not over-correct into passive voice,
hedging, or padding; a voice pass leaves word count flat or slightly higher.
Quotations are copied exactly, tics included. Process records are never
restyled, because rewriting them falsifies what was true when they were written.
This applies to every tracked file, commit subjects, and tag annotations.

Two extensions this repository needs that ZMeta does not state.

- **Validator and gate refusal strings are governed prose.** A connector author
  meets `tools/validate.py` at the worst moment of their week, and the refusal
  message is the only documentation they read. It states what was refused, which
  rule refused it, and the two or three legal moves available.
- **A state is rendered as its consequence, never as its token.** The ZISR COP
  renders `parked` as "PARKED, this COP is NOT attached to this source", because
  an operator cannot act on the bare string "parked". This binds the connector
  health states, the subject gate's three values, and every retention state.

One warning specific to `doctrine/`. Those files attract a third register, with
"shall not", capitalized defined terms, and blanket qualifiers. Refuse it. A
doctrine document written in policy-speak reads as someone else's requirement
being imposed, and it gets routed around. The same document written as
engineering, naming the mechanism that enforces each rule and the test that
proves it fired, reads as a system property and holds.

**Register 2, published briefings.** `docs/DOCUMENT_STANDARD.md` applies when a
document has a reader who is not the author, a finding worth leading with, and
enough consequence that being skimmed wrong would cost something. A doctrine
document never becomes a briefing. It is rank 1, it is parsed by the guard, it
is amended by ratified item, and it must diff cleanly.

Analyst prose in the DRAFT view is governed by neither register. Its standard is
the citation requirement. Applying a house voice standard to it would be the
system editing a finding.

## 5. Attribution

**R6 stamped 2026-08-26.** Carry ZMeta's rule: attribute commits and pull
requests to the human maintainer alone, and do not add `Co-Authored-By` trailers
naming the agent. Every contributor in this stack works through Claude, so the
history tracks people rather than the tool.

One rule here is not a matter of taste. **A Class F commit is authored by the
ratifier**, and an agent never authors one under any attribution scheme.

**R6 amended 2026-08-27.** The original reading put the git command itself in the
operator's hands. That was stricter than the property the rule protects, and the
friction bought nothing: git records the configured identity as author either
way, so a commit an agent executes is already authored by the ratifier.

The amended rule separates the decision from the mechanics.

- **The decision stays the operator's.** An agent may draft a Class F change and
  may never decide one. Nothing here relaxes that.
- **An agent may execute a commit or a push on the operator's explicit
  instruction for that act.** Per-instruction, not standing: a general
  willingness to have commits made is not authorization for the next one.
- **The operator is the author of every commit**, and no `Co-Authored-By`
  trailer names the agent. `.github/workflows/ci.yml` refuses a history
  containing one, so this half is a mechanism rather than a habit.
- **The worklog records agent involvement** where it can be stated precisely,
  which is where the history's honesty about how the work was done now lives.

## 6. Before proposing work as done

Run the gates named in `AGENTS.md`. If a required check cannot be run, document
the reason in the handoff rather than omitting it.
