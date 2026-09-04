# PLAINSIGHT

An OSINT common operating plane, and PSE, the ZMeta-derived semantic dialect it
runs on.

**Status: Wave 0 committed, and the first build artifacts are committed with
the gates that check them.** Every doctrine conclusion has been recorded since
2026-08-27 and every basis is deliberately unstamped. The layer model, the
selector registry, the unsealed cast draft, and the validators that read them
landed in `d99f213`. No schema, no policy pack, and no collection mechanism
exists. No connector exists. Nothing here has touched a platform.

## What this is

**PLAINSIGHT** consolidates person-centric OSINT tools into one surface,
standardizes their input and output, automates the pivots between them, and puts
an analyst in front of one worked picture. Its product is the citation chain:
every sentence in an assessment walks back through a cluster, through rationale
claims, through items, through a run, to argv and raw bytes.

**PSE**, the PLAINSIGHT Semantic Envelope, is a private dialect derived from
`zmeta-event-1.0`. It does not claim upstream ZMeta compatibility and must not be
described as ZMeta-conformant.

The project is an experimentation program. Its purpose is to establish what these
capabilities can actually do, measured against subjects whose answers can be
confirmed. Findings survive. Profiles do not.

## Read in this order

A session starting cold reads these four files before doing anything:

1. `CLAUDE.md`: orientation, authority order, the eight design gates, voice.
   Advisory and non-normative.
2. `AGENTS.md`: normative operating model, change classes A through F,
   **Execution Limits**, required local workflow, ratification rule.
3. `doctrine/DOCTRINE_STATUS.md`: what is ratified. Every conclusion is
   recorded and every basis is unstamped, so read the header before relying on a
   row. Mechanisms read this file rather than the document they enforce.
4. `docs/plainsight_handoff.md`: current state, what blocks, known gaps.

Then, for background rather than authority:

- `CHANGELOG.md`: one entry per commit that changed a governed artifact, each
  naming what did not change.
- `CONFORMANCE.md`: why PSE is not ZMeta, what a connector conformance claim
  contains, and what the kernel gate does and does not cover today.
- `docs/THE-GAMEPLAN.md`: the full artifact register and the numbered steps.
- `docs/PLAINSIGHT-FOUNDATION.md`: the ecosystem read-back, the transfer map,
  and decisions D1 through D5. Still carries its DRAFT header.
- `docs/PLAINSIGHT-design.md`: the application design of record.
- `docs/OSINT-COP-tool-review.md`: the audit of six candidate tools.
- `docs/DOCUMENT_STANDARD.md`: the standard for published briefings.

## Three rules that bind immediately

These apply from the first line of work, before any doctrine is ratified.

1. **No agent executes a connector, adapter, or runner against a live platform,
   account, or person.** Not to check a hypothesis, not to confirm liveness, not
   to run a canary. See `AGENTS.md` section 4.
2. **No agent lands a Class F change.** Drafting one is permitted and expected.
   Class F is any change to who may be a subject, what may be collected, how
   long anything is held, or what may leave the machine. It is defined by effect,
   not by path.
3. **No selector belonging to a natural person enters a tracked file.** This
   includes worklog entries, commit messages, fixtures, and cassettes. Git
   history is the one store a crypto-shred cannot reach.

## Layout

```
doctrine/     rank 1. human-ratified per item.
spec/         the PSE semantic contract, layer model, divergence register
schema/       event, connector manifest, subject authorization
ontology/     the closed selector vocabulary
policy/       compiled doctrine and semantics, read by validators
conformance/  must-pass and must-fail corpora, harnesses
tools/        validators and diagnostics
synthetic/    the designed cast and sealed ground truth
connectors/   one directory per connector. empty at Wave 0.
runner/       subject guard, retention sweep, shred verification. empty at Wave 0.
app/          the analyst interface. empty at Wave 0.
docs/         design records, worklog, handoff
```

One lane rule is enforced: nothing under `spec/`, `schema/`, `ontology/`,
`policy/`, or `tools/` may import from `app/`. The reverse is permitted.

## Next action

**The operator decides four Class F items.** They are drafted as patch 4 in
`Z-ISR/_session-artifacts/2026-09-03-plainsight-doctrine-review-2/`, with
`DECISIONS.md` beside them, and each lands unratified and refuses until
stamped. Patch 2 in the same directory restores to SS-4's required-field table
the reach R4 decided on 2026-08-26, and the authorization schema Step 8 compiles
from that table, so patch 2 lands before Step 8. Step 7 does not wait on it.

Then Step 7: `schema/pse-event-0.1.schema.json` generated from
`spec/layer-model.yaml`, the four policy files, and
`spec/pse-semantics-contract.md` written last, because the contract explains
rules that already exist rather than inventing rules nothing enforces.

## Relationship to the rest of Z-ISR

This repository reads from its siblings and writes to none of them.

- `../ZMeta/zmeta-spec/`: the parent standard. PSE derives from
  `zmeta-event-1.0` and is licensed as a private dialect by that repository's
  `AGENTS.md`.
- `../ZMeta/zmeta-field-capture/`: the retention and evidence precedent.
- `../zisr-recon/`: the permission-gate precedent.
- `../ZISR COP/`: the operational client, and the source of several interface
  patterns. PLAINSIGHT is a sibling application, not a mode within it.
