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
  messages. The repository's own coordinates are not handles in this sense:
  its public remote, the account that owns it, and the upstream projects it
  cites may be named, and the D-001 repo scan is written not to refuse them.
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

`make preflight` runs the pre-commit hook's twenty-one commands plus the
telemetry test, which the hook leaves to CI, and `make validate-kernel` runs the
aggregator. The gate battery is defined once, in
`KERNEL_GATE` inside `tools/validate_conformance.py`, so a new check joins it
there rather than in every document that quotes a command.

**Every validator self-test runs on all four automated paths**: the hook,
`make preflight`, the kernel gate, and CI, where ten have a named step of their
own and hygiene's runs in the Housekeeping step. A self-test breaks its governed
artifact in memory and asserts each break is refused, so it is the test that
fails when a check is removed. Until 2026-09-28 five of the six that then existed
ran on no path, and the fires_when fix was reported green in two sessions while
the layer-model self-test exited 1. `tools/validate.py` runs its own inside
`--kernel`. `tools/validate_doctrine.py` gained one on 2026-10-01, and so did
`tools/pin_of_record.py`, the one reader of the pin of record the doctrine,
authorization and retention gates share. `tools/validate_divergence_register.py`
joined with its own at Step 9, and `tools/validate_manifest.py` and
`tools/validate_connector_conformance.py` with theirs at Step 12. The kernel
gate's exit code shows a
self-test failure only while no other entry holds it red, and its entry line
always shows it, which is why CI also runs each self-test as a step of its own.

**What these gates actually cover, stated so a green run is not read as more
than it is.** The governed artifacts checked today are the doctrine corpus
(criterion definitions, per-criterion stamps, cross-references in both
directions, reconciliation against the pin of record, prose counts), the voice
standard, table structure, citations against the artifact register, the handoff
and worklog caps, the handoff's tense, the tools-to-gates inventory, the layer
model in
`spec/layer-model.yaml` (nine types, discriminators, denylists, lineage,
producer authority, strata, and the D5 parent on every run), the selector
registry in `ontology/selectors.yaml` (the closed vocabulary, anchor
eligibility, the constraint rule, prohibitions, matchers, and its codes
reconciled against the layer model), the cast draft in `synthetic/` (the
checkable half of SS-3, the confuser pair, the partition, the seal, and no
filled value while unsealed), the telemetry recorder in `tools/gate_log.py`
(HY-1 and RT-19 exercised by `tools/tests/test_gate_log.py`), and the
divergence register in `spec/divergence-register.yaml` (every pointer a diff of
the PSE schema and zmeta-event-1.0 produces covered once or listed identical,
both pins holding, dispositions from a closed five that fit the diff, entries
that cite the contract, test_refs that resolve to a fixture touching what the
entry names, the compatibility claim in no file of the tree, and its rendering
current). The divergence gate reads the upstream schema from the sibling
checkout `../ZMeta/zmeta-spec`, pinned by sha256; CI clones the pinned release
there, and a checkout without it exits 2 rather than passing. The schema,
policy and authorization checks now exist. The schema check grades the generated
schema, the policy pack and both corpora against `spec/layer-model.yaml`, and the
authorization and retention checks are implemented and refuse, because the
artifacts they grade carry no dated row in `doctrine/DOCTRINE_STATUS.md`. Step 12
added the connector manifest check: `tools/validate_manifest.py --all` grades
every `connectors/*/manifest.yaml` against `schema/connector-manifest.schema.json`,
the selector registry, both canaries, one refusal fixture per required input
linted against `conformance/connector-harness/fixture.schema.json`, SS-10's
bystander declaration, and the R7 stamp. The first connector,
`connectors/sherlock/`, refused under `MANIFEST_SELECTOR_PLATFORM`, which is
reading SH-R5 in its README, until its handle emit declared `platform_from_item`
on 2026-10-28 (MF-R17, amendment 9.14 of `docs/PLAINSIGHT-design.md`), a move
the operator kept the same day on his click on the offered action in the
PLAINSIGHT chat; reverting it would return this check, the pre-commit hook and
`make preflight`, which run it, to refusing.
`tools/validate_connector_conformance.py --all` is rung 4: it runs the manifest
gate first, replays every cassette through the adapter, grades every emitted
event with `tools/validate.py`, asserts each fixture's exact event count, or its
refusal code and the input it withholds, the known negative's zero hits and the
known positive's hits, and asserts that `invoke()` reaches no process or network
call without a permit. It refuses whenever the manifest does. Every
cassette it replays is hand-built in a recorded shape, and the live canaries are
an operator act that has not been performed. Step 10 drafted
`runner/subject_guard.py`, which refuses every request while the artifacts
SS-14 item 6 lists carry no dated row, and its tests,
`runner/tests/test_subject_guard.py`, which run on the kernel gate, in
`make test` and in CI's Mechanism tests step. The Sherlock adapter's own tests
run under pytest in `make prove` and in CI's connector adapter tests step.
The application's tests under `app/tests/` run under pytest on the kernel gate
as its app-tests entry, in `make test` and in CI's Application tests step, and
not in the pre-commit hook or `make preflight`, which reading APP-R30 in
`app/README.md` explains.
`tools/validate_authorization.py --dispatch-paths` reads every Python file under
`runner/`, `connectors/` and `app/` for a site that dispatches outside the gate
and refuses, because `runner/dispatch_allowlist.yaml` does not exist and the
bypass check has nothing to compare against. Its reading VA-R6, which reads a
patch target and its kept original in a test module as no site, narrows what it
reports; applied as the session's reading of 2026-10-28 and decided Class B
by the operator the same day (a precision rule of the scanner, not an
exemption), on his click on the offered action in the PLAINSIGHT chat. `--kernel-gate` prints
an unimplemented check as PENDING with the step that delivers it, prints an
implemented check whose artifact carries no stamp as UNRATIFIED and asserts that
it refused, and never counts a pending, stubbed or unratified check as a pass.
Every validator that parses YAML needs PyYAML, the divergence register's among
them, and `tools/validate.py`, `tools/validate_manifest.py`,
`tools/validate_connector_conformance.py` and
`runner/tests/test_subject_guard.py` need jsonschema.
CI installs both and a local checkout must have both. The connector adapter
tests and the application's tests need pytest, which CI installs, and a local
checkout needs it for the kernel gate, whose app-tests entry runs
`python -m pytest app`.

`tools/validate_retention.py --repo-scan` is implemented as of Step 8, which
closed D-001. It reads every tracked file in the working tree for a filled
selector in its typed form, or written as a type beside a value in a JSON line,
a .json file or a .yaml file, against thirteen shapes reconciled with
`ontology/selectors.yaml` in both directions, and the pre-commit hook runs the
same mode over the index. Three of RT-15's four enforcement parts are in place:
this file's Execution Limits clause, the scan in the hook, and
`canary_subject_class`, required by the manifest schema and refused when absent
since Step 12 and declared on `connectors/sherlock/manifest.yaml`. The fourth is
not: the violation code RT-15 names is not in the wire vocabulary, so the scan
emits a tool-local code. Separately, git history is out
of reach of any check that runs at commit time, so a selector deleted from the
working tree and still present in an earlier commit is not found. The retention
self-test refused with `RETENTION_POLICY_ENFORCEMENT_MISSTATED` while
`policy/retention.yaml` recorded the `canary_subject_class` part as absent. On
the operator's instruction of 2026-10-28 that flag reads present, a one-word
edit of that flag he decided Class B the same day, and the self-test's mutation now flips it. The scan refused on two values that predate Step 8
until both were replaced with placeholders under the operator's overnight grant
of 2026-09-30, and `CONFORMANCE.md` section 4 records what they were and why no
exemption was added.

If a required check cannot be run, document the reason in the handoff.

## 6. Documentation matrix

When a governed artifact changes, the matching surfaces move in the same change.

Every row also updates `CHANGELOG.md` and both process records, which is
`ZMeta/zmeta-spec/AGENTS.md`'s rule rather than a local one, and it is stated
here because the Schema row below used to be the only place this repository named
the changelog.

The two process records do not take the same tense. Write each in the tense
section 8 sets for it.

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
from `../zisr-producers/recon/docs/ENTRY_CRITERIA.md`: no emitter should be
built on a rationale the operator was never shown. That repository stood at
`../zisr-recon/` until the 2026-09-10 consolidation, which is the path the
dated measurements in `doctrine/` and `docs/` still name.

**Unratified binds nothing, and the mechanism reads the stamp rather than the
file.** There must be a test asserting that an unratified criterion refuses
rather than permits. The alternative repeats the
`../zisr-producers/recon/src/zisr_recon/guard.py` defect one level up, where an
expiry check was intended and never written.

One partially stamped item does not stamp its file.

**The gates read the pin through one reader.** `tools/pin_of_record.py` decides
for the doctrine, authorization and retention gates whether an artifact or a
criterion is stamped, and its `READINGS` state the predicates. A row stamps a
whole artifact only when its File cell names the path alone and its Item cell is
exactly "<what>, whole artifact" or a doctrine range such as "RT-1 to RT-18, all
criteria", which is how the sentence above becomes a mechanism rather than a
convention. A criterion binds only inside a stated range or a row that names
it. A struck or withdrawn row stamps nothing, and a row is withdrawn by a later
dated row rather than by editing it.

## 8. Handoff standard, and the closeout

Inherited from `ZMeta/zmeta-spec/AGENTS.md`, which contributes the five
questions and nothing else. Everything after them is local to this
repository. A completed change leaves the next maintainer able to answer
five questions:

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

**Amended 2026-10-25: a closeout files a since-last-record extraction beside its
record before the records are written.** The session runs
`python tools/since_last_record.py <transcript.jsonl> <since> <out.md>`, with
`<since>` the stamp of its last record as a moment with a zone (UTC, or an
explicit offset; the tool refuses a moment without one, because a zone guessed
wrong empties the span silently), to the end of its own transcript, and files
the output beside the closeout record, outside the tree; the tool refuses an
output path inside the repository. The file carries the maintainer's lines in
that span, each marked by how it arrived: typed; a click on an action the
session offered, which the tool detects by comparing the text with the actions
offered in the most recent wrap-up call before the line, reading a message the
app cut at 300 characters as the same click; or a selection on an offered
question, read from the answer to an AskUserQuestion call with each question
and the chosen option verbatim. It carries every message the session sent and
received, verbatim, and its last assistant texts. The session reads the file
once before writing the records: a maintainer line it shows that the records
lack is written in, and a line marked as a click or a selection is never
written as typed, which is the error the records of 2026-10-18 carried and the
commit of 2026-10-24 corrected. A resumer reads the closeout record and that
file, and re-reads the transcript only when the file shows substantive entries
after the closeout. The file is a verbatim copy that no retention mechanism in
this repository reaches, so a closeout does not run the tool over a span in
which case material was discussed until `doctrine/RETENTION.md` says how such
a copy is held. The tool's `--self-test` plants a typed line, a click, a click
cut at 300 characters, a selection, a sent and a received message and an
assistant text and asserts each is classified as what it is, keeps a line
equal to a superseded or a later offer typed, and runs four controls that must
refuse: a since past the last entry (zero entries, every section "none in the
span"), a file that is not a transcript (exit 2), a since without a zone, and
an output path inside the repository; a closeout that files an extraction
names the self-test's result, per the negative-control rule of 2026-10-16. The
extraction is a records aid rather than a gate: it joins no battery, the hook
and CI are unchanged, the Makefile target `since-last-record` runs only the
self-test, by the drafting session's decision the self-test runs on no
automated path and only at closeout, and whether it joins the battery is the
maintainer's separate decision. The rule above that a closeout commits is unchanged by it. It was
adopted on the maintainer's selection of the offered option in the PLAINSIGHT
session on 2026-10-25, after the parent folder's spin-up protocol of
2026-10-24; the tool is a copy under this repository's own process, adapted
after that playbook's click test was found never to fire here, because it
looked for an attachment this harness does not write, and nothing is imported
from the parent folder.

The surfaces a closeout moves, in addition to whatever the change touched:

| Surface | What it carries |
|---|---|
| `CHANGELOG.md` | One entry per commit that changed a governed artifact, naming what did **not** change |
| `docs/plainsight_worklog.md` | The chronological record, added to and never restyled |
| `docs/plainsight_handoff.md` | Current state only, rewritten, answering the five questions above |

**Write the handoff in the tense of the tree the commit will create.** The
order above means nothing in the change is committed at the moment the
records are written, and the two records take that differently. Write the
worklog in the tense of the moment: it is a process record, it is added to
rather than restyled, and its own entry dates it. The handoff is read next
session against a tree in which the commit exists, so name a staged artifact
as committed in this commit rather than as written, untracked, or
uncommitted. Stage the change before the records are written, so that
`git diff --cached --name-only` lists what the commit will contain, and
reconcile every state claim in the handoff against that list rather than
against what `git status` calls untracked.

Three commits have failed this, which is what makes it a rule rather than a
preference. `1abb354` committed a handoff reading "Nothing committed,
nothing built" in the commit that added twenty-one files. `4c5cd25`
committed one whose state header called the hardening pass uncommitted.
`f4e00e1` committed one that marked nine artifacts untracked in the commit
that tracked all nine. `tools/validate_hygiene.py` refuses either word in
that one file as `HYGIENE_HANDOFF_PRE_COMMIT_TENSE`, and its `--self-test`
plants each word and asserts the refusal. That check reaches thirteen of the
fourteen lines that were wrong at `d803213`. The fourteenth, a sentence with
neither word, is caught at the closeout or not at all, which is the half of
this rule that stays a sentence.

**The local rule that binds the commit rather than the records.** A closeout
commit carries no Class F change the operator has not decided. An agent may
draft one, and per R6 as amended may execute the commit of a decision the
operator has made, so the drafts wait outside the commit as a patch with its
argument beside it rather than landing inside it. A closeout that quietly
includes a doctrine amendment has made the ratification a formality, which is
the failure the whole pin-of-record apparatus exists to prevent.
