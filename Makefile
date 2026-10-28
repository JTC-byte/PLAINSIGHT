.PHONY: help validate-doctrine validate-hygiene validate-layer-model validate-ontology validate-cast validate-authorization validate-retention generate validate-schema validate-divergence-register render-divergence-register validate-manifest validate-connector prove test validate-kernel preflight gate-telemetry since-last-record

# The named gates. A gate is a stable token rather than a hand-copied command
# string, so a new check joins the battery in one place. That place is
# KERNEL_GATE in tools/validate_conformance.py, not this file.
#
# What exists here is what there is to check. The governed artifacts are the
# doctrine corpus (58 criteria across four rank-1 files and one advisory file,
# with a pin of record they reconcile against), the layer model in spec/ and
# the schema, policy pack and conformance corpora generated from it, the
# selector registry in ontology/, the unsealed cast draft in synthetic/, and
# the voice standard every tracked file is held to. Step 8 added the compiled
# subject and retention policy, their schema and conformance artifacts, and the
# two validators that read them. Those artifacts are Class F and unratified, so
# their gates refuse rather than pass, and the aggregator carries them as
# UNRATIFIED rather than as failures. Step 9 added the divergence register in
# spec/, graded against a diff of the PSE schema and zmeta-event-1.0 rather than
# against prose. Step 12 added the connector manifest schema, the harness
# fixture schema and the manifest validator, which runs over every
# connectors/*/manifest.yaml. Step 10 drafted runner/subject_guard.py, its tests,
# and the --dispatch-paths mode, which refuses while runner/dispatch_allowlist.yaml
# does not exist and is carried as UNRATIFIED. Step 12's second part added the
# first connector, connectors/sherlock/, on hand-built cassettes only, and the
# connector conformance runner, rung 4. On 2026-10-28, on the maintainer's
# instruction, the Sherlock manifest stopped refusing on reading SH-R5 through
# the manifest schema's platform_from_item (MF-R17), and policy/retention.yaml's
# canary_subject_class part was set to present by a one-word edit of that
# flag, Class B by his decision of the same day, so the retention self-test no longer refuses; the maintainer decides
# whether each stands. The same day the application's tests under app/ joined
# the kernel gate and the test target below, and not preflight (APP-R30). The
# deferred disjointness mode and the retention
# finding mode are named as PENDING inside the aggregator with the step that
# delivers each, so `validate-kernel` reports the gap rather than passing over it.

help:
	@echo "validate-doctrine     criterion definitions, stamps, cross-references, pin of record, both self-tests"
	@echo "validate-hygiene       voice, tables, citations against the register, caps, the handoff's tense, inventories, and its self-test"
	@echo "validate-layer-model  the nine event types, discriminators, denylists, lineage, producer authority"
	@echo "validate-ontology     the closed selector vocabulary, anchors, constraints, prohibitions, matchers"
	@echo "validate-cast         the checkable half of SS-3, the confuser pair, the partition, the seal"
	@echo "validate-authorization the D5 gate corpus, the record shape, SS-5's three fixtures, the stamp read, and the dispatch paths. Refuses until stamped"
	@echo "validate-retention    the compiled strata and TTLs, the shred round trip, and the RT-15 repository scan. Refuses until stamped"
	@echo "generate              rewrite the schema, the policy pack and the corpora from the layer model"
	@echo "validate-schema       generated artifacts current, both corpora graded, the runner's self-test"
	@echo "validate-divergence-register  the register against a diff of the two schemas, its self-test, the rendering current"
	@echo "render-divergence-register    rewrite spec/divergence-register.md from the register"
	@echo "validate-manifest     every connector manifest, the two schemas, bystanders, canaries, refusal fixtures, R7, its self-test"
	@echo "validate-connector    rung 4: every connector's adapter against its cassettes and fixtures, and its self-test"
	@echo "prove                 the five rungs for one connector: make prove CONNECTOR=<id>"
	@echo "test                  the mechanisms that exist, exercised against the criteria that claim them"
	@echo "validate-kernel       the full battery, including what is not built yet"
	@echo "preflight             what must be green before a commit"
	@echo "gate-telemetry        what each gate has been doing, for adjudication"
	@echo "since-last-record     the closeout's delta-file tool: its self-test (the extraction takes arguments; see the target)"
	@echo ""
	@python tools/validate_conformance.py --list

validate-doctrine:
	python tools/validate_doctrine.py
	python tools/validate_doctrine.py --self-test
	python tools/pin_of_record.py --self-test

validate-hygiene:
	python tools/validate_hygiene.py
	python tools/validate_hygiene.py --self-test

# The layer model is the single source the Step 7 schema and policy are
# generated from, so a defect in it is a defect in every generated artifact at
# once. --self-test breaks the model in memory and asserts each break refuses,
# which is doctrine/HYGIENE.md section 2's rule for a newly written check.
validate-layer-model:
	python tools/validate_layer_model.py
	python tools/validate_layer_model.py --self-test

# D2 in one file. The vocabulary is closed at the corpus boundary rather than
# only at the manifest, and the constraint selectors are the reason: a masked
# recovery hint reaching a field named `email` is wrong in a way no guard keyed
# on absence can catch, because the value is present.
validate-ontology:
	python tools/validate_ontology.py
	python tools/validate_ontology.py --self-test

# The placeholder scan is the half that matters before a commit: it refuses a
# filled selector value in the tracked draft while the cast is unsealed, which
# is AGENTS.md section 4's rule made a gate.
validate-cast:
	python tools/validate_cast.py --placeholder-scan
	python tools/validate_cast.py --self-test

# Step 8, and the one place in this file where --self-test runs first. Both
# artifact modes below refuse, which is the designed state rather than a defect:
# --fixtures while policy/subject-authorization.yaml carries no dated row in
# doctrine/DOCTRINE_STATUS.md, and --dispatch-paths, joined at Step 10, while
# runner/dispatch_allowlist.yaml does not exist. A designed refusal on the first
# line would stop the target before the self-test ran, and the self-test is the
# half that can be green today: it breaks the loaded artifacts in memory and
# plants dispatch sources and fixture allowlists, and asserts each break is
# refused, which is doctrine/HYGIENE.md section 2's rule for a new check. make
# stops at the first refusing line, so --fixtures prints its refusal when run on
# its own.
validate-authorization:
	python tools/validate_authorization.py --self-test
	python tools/validate_authorization.py --dispatch-paths
	python tools/validate_authorization.py --fixtures

# Step 8. --repo-scan is RT-15 and reads every tracked file in the working tree;
# the pre-commit hook runs the same mode over the index, because git history is
# the one store a crypto-shred cannot reach. The two artifact modes run last for
# the reason stated above validate-authorization: they refuse until the operator
# stamps policy/retention.yaml and conformance/retention/shred-roundtrip.yaml,
# and a refusal there would otherwise hide a real finding in the scan.
validate-retention:
	python tools/validate_retention.py --self-test
	python tools/validate_retention.py --repo-scan
	python tools/validate_retention.py --policy
	python tools/validate_retention.py --shred-roundtrip

# Step 7. The schema, the four policy files and both conformance corpora are
# generated from spec/layer-model.yaml and the fixture tables, and nothing else
# writes them. `generate` rewrites them. `validate-schema` refuses when what is
# on disk differs from what the model generates, then grades both corpora and
# runs the runner's own self-test. A generated file edited by hand is drift, and
# drift is a refusal rather than something a diff review might notice.
generate:
	python tools/generate_pse.py
	python tools/build_corpus.py

validate-schema:
	python tools/validate.py --kernel

# Step 9. The register's required entry list is derived from a JSON-pointer
# diff of schema/pse-event-0.1.schema.json and zmeta-event-1.0, which is read
# from the sibling checkout ../ZMeta/zmeta-spec and pinned by sha256, so a
# register written from prose cannot pass. The rendering is generated, and
# --check refuses a hand edit the way generate_pse.py --check does. The gate
# itself runs the same comparison, so the third line is the renderer's own
# check of what the first already refuses.
validate-divergence-register:
	python tools/validate_divergence_register.py
	python tools/validate_divergence_register.py --self-test
	python tools/render_divergence_register.py --check

render-divergence-register:
	python tools/render_divergence_register.py

# Step 12. The one CI check docs/PLAINSIGHT-design.md section 6.4 keeps, plus the
# doctrine checks a schema cannot express: SS-10's bystander declaration, RT-15's
# canary_subject_class, one refusal fixture per required input, and the R7 stamp
# read through tools/pin_of_record.py. connectors/sherlock/manifest.yaml refused
# under MANIFEST_SELECTOR_PLATFORM on reading SH-R5 until the platform_from_item
# move of 2026-10-28 (MF-R17), which the maintainer kept the same day. Use
# `python tools/validate_manifest.py --shape <path>` while authoring; it makes no
# conformance claim.
validate-manifest:
	python tools/validate_manifest.py --all
	python tools/validate_manifest.py --self-test

# Step 12, rung 4 of CONFORMANCE.md section 3. --self-test runs first, as in
# validate-authorization, because --all refused while the Sherlock manifest did
# and make stops at the first refusing line; the self-test plants each defect in
# a scratch copy of connectors/sherlock outside the repository. --all runs tools/validate_manifest.py's full mode
# first, replays every cassette through the adapter, grades every emitted event
# with tools/validate.py, and asserts invoke() starts no process without a
# permit. It never runs a connector against a platform.
validate-connector:
	python tools/validate_connector_conformance.py --self-test
	python tools/validate_connector_conformance.py --all

# The five rungs for one connector, narrowest first: make prove CONNECTOR=<id>.
# Rung 1 needs pytest, which CI installs for its own connector adapter tests
# step. Rung 3's --corpus mode is a
# STUB that prints DEFERRED and checks nothing. Rung 5 is the whole-repository
# kernel gate and says nothing about one connector. The live canaries, design
# section 6.5's Prove It, are an operator act this target never performs, so a
# green run here registers nothing for live use.
CONNECTOR ?=
prove:
	python -m pytest connectors/$(CONNECTOR) -q
	python tools/validate_connector_conformance.py --connector $(CONNECTOR)
	python tools/validate_ontology.py --corpus
	python tools/validate_conformance.py --kernel-gate

# Design gate 1: a constraint is not done until a test fails when it is removed.
# Until 2026-09-03 no test existed here, so every mechanism on disk was an
# assumption in the sense doctrine/HYGIENE.md section 2 warns about. Step 10
# added the subject guard's tests, which also run under pytest. CI's Mechanism
# tests step runs the same two scripts. The application's tests joined on
# 2026-10-28 and need pytest; they run about three minutes, with their paired
# negative controls inside the suite, and CI runs them as its Application tests
# step. --tb=short keeps a failure to its assertion line (APP-R30).
test:
	python tools/tests/test_gate_log.py
	python runner/tests/test_subject_guard.py
	python -m pytest app -q --tb=short -p no:cacheprovider

validate-kernel:
	python tools/validate_conformance.py --kernel-gate

# preflight is the pre-commit battery plus the telemetry test. The hook runs the
# same twenty-one commands and not the test, which CI runs as a step of its own. A
# gate that is only enforced in CI is enforced only after the thing it guards
# has already been committed, and git history is the one store a crypto-shred
# cannot reach.
#
# Six validator self-tests joined this list and the hook on 2026-09-28.
# Before then only CI ran one of them, hygiene's, and the fires_when fix was
# reported green in two sessions while the layer-model self-test exited 1,
# because nothing on this path or the hook's ran it. The six grade the checks
# rather than the stamps, which is what separates them from the Step 8 artifact
# modes below. All six are green today; the retention self-test refused from
# Step 12 until the flag the header of this file names was set on 2026-10-28.
# Two ratifying acts reach them anyway: sealing the
# cast did until the cast self-test was fixed the same day, and completing SS-14
# item 6 still does, through row 8 of conformance/gate/decisions.jsonl, which the
# completing commit edits too. The pre-commit hook states the detail.
#
# Two more joined on 2026-10-01: the doctrine gate's first self-test, written
# after the telemetry review found it could not fire for SS-1, and the self-test
# of tools/pin_of_record.py, the one reader of the pin of record the doctrine,
# authorization and retention gates share.
#
# Two more joined at Step 9: the divergence register's gate, which reads the
# upstream schema from ../ZMeta/zmeta-spec and exits 2 where that checkout is
# absent, and its self-test.
#
# Two more joined at Step 12: the manifest gate over every connector manifest
# and its self-test. Two more joined with the first connector: the connector
# conformance runner over every connector and its self-test.
#
# The Step 8 artifact modes are deliberately absent from this list. Every one of
# them refuses while the four Class F artifacts carry no dated row, so adding
# one here would block every commit in the repository on a decision only the
# operator can make, including the commit that records the decision. The one
# retention mode that belongs before a commit is already the last line below:
# --repo-scan --staged is RT-15 over the index, and it is the check that stops a
# selector value from entering the one store nothing can clear. When the
# operator stamps the artifacts, --policy and --fixtures become candidates for
# this list and that is a change to make deliberately rather than by default.
#
# The application's tests are absent from this list and from the hook by
# reading APP-R30 of 2026-10-28. They run about three minutes, they guard
# runtime behaviour rather than what enters git history, and the scan below is
# what stops a selector value at the commit; the kernel gate, make test and CI
# run them.
preflight:
	python tools/validate_doctrine.py
	python tools/validate_hygiene.py
	python tools/validate_layer_model.py
	python tools/validate_ontology.py
	python tools/validate_cast.py --placeholder-scan
	python tools/validate.py --kernel
	python tools/validate_divergence_register.py
	python tools/validate_manifest.py --all
	python tools/validate_connector_conformance.py --all
	python tools/validate_hygiene.py --self-test
	python tools/validate_layer_model.py --self-test
	python tools/validate_ontology.py --self-test
	python tools/validate_cast.py --self-test
	python tools/validate_authorization.py --self-test
	python tools/validate_retention.py --self-test
	python tools/validate_doctrine.py --self-test
	python tools/pin_of_record.py --self-test
	python tools/validate_divergence_register.py --self-test
	python tools/validate_manifest.py --self-test
	python tools/validate_connector_conformance.py --self-test
	python tools/tests/test_gate_log.py
	python tools/validate_retention.py --repo-scan --staged

# The pattern of life on the gates themselves. A gate nobody measures is a gate
# nobody can adjudicate, and both failure directions are silent: a check that
# never fires looks identical to a check that is working, and a check that always
# fires gets ignored rather than fixed. Thresholds are in doctrine/HYGIENE.md.
gate-telemetry:
	python tools/gate_log.py --summary

# The closeout's delta file, AGENTS.md section 8 as amended 2026-10-25. Not a
# gate and not in preflight, by this session's decision put to the maintainer:
# the extraction reads a session transcript the closeout names, so this target
# runs the tool's self-test, which plants one line of each kind (typed, a click
# on an offered action, a click cut at 300 characters, a selection on an
# offered question, a message sent, a message received, an assistant text) and
# sees four controls refuse (a since past the last entry reads zero entries; a
# file that is not a transcript exits 2; a since without a zone and an output
# path inside the repository are refused). The extraction itself:
#   python tools/since_last_record.py <transcript.jsonl> <since with a zone | all> <out.md>
since-last-record:
	python tools/since_last_record.py --self-test
