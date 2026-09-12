.PHONY: help validate-doctrine validate-hygiene validate-layer-model validate-ontology validate-cast validate-authorization validate-retention generate validate-schema test validate-kernel preflight gate-telemetry

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
# UNRATIFIED rather than as failures. The divergence register, the connector
# gate and the two deferred authorization modes are named as PENDING inside the
# aggregator with the step that delivers each, so `validate-kernel` reports the
# gap rather than passing over it.

help:
	@echo "validate-doctrine     criterion definitions, stamps, cross-references, pin of record"
	@echo "validate-hygiene       voice, tables, citations against the register, caps, the handoff's tense, inventories, and its self-test"
	@echo "validate-layer-model  the nine event types, discriminators, denylists, lineage, producer authority"
	@echo "validate-ontology     the closed selector vocabulary, anchors, constraints, prohibitions, matchers"
	@echo "validate-cast         the checkable half of SS-3, the confuser pair, the partition, the seal"
	@echo "validate-authorization the D5 gate corpus, the record shape, SS-5's three fixtures, and the stamp read. Refuses until stamped"
	@echo "validate-retention    the compiled strata and TTLs, the shred round trip, and the RT-15 repository scan. Refuses until stamped"
	@echo "generate              rewrite the schema, the policy pack and the corpora from the layer model"
	@echo "validate-schema       generated artifacts current, both corpora graded, the runner's self-test"
	@echo "test                  the mechanisms that exist, exercised against the criteria that claim them"
	@echo "validate-kernel       the full battery, including what is not built yet"
	@echo "preflight             what must be green before a commit"
	@echo "gate-telemetry        what each gate has been doing, for adjudication"
	@echo ""
	@python tools/validate_conformance.py --list

validate-doctrine:
	python tools/validate_doctrine.py

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
# artifact modes below refuse while policy/subject-authorization.yaml carries no
# dated row in doctrine/DOCTRINE_STATUS.md, which is the designed state rather
# than a defect. A designed refusal on the first line would stop the target
# before the self-test ran, and the self-test is the half that can be green
# today: it breaks the loaded artifacts 41 ways and asserts each break is
# refused, which is doctrine/HYGIENE.md section 2's rule for a new check.
validate-authorization:
	python tools/validate_authorization.py --self-test
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

# Design gate 1: a constraint is not done until a test fails when it is removed.
# Until 2026-09-03 no test existed here, so every mechanism on disk was an
# assumption in the sense doctrine/HYGIENE.md section 2 warns about.
test:
	python tools/tests/test_gate_log.py

validate-kernel:
	python tools/validate_conformance.py --kernel-gate

# preflight is the pre-commit battery plus the telemetry test. The hook runs the
# same seven commands and not the test, which CI runs as a step of its own. A
# gate that is only enforced in CI is enforced only after the thing it guards
# has already been committed, and git history is the one store a crypto-shred
# cannot reach.
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
preflight:
	python tools/validate_doctrine.py
	python tools/validate_hygiene.py
	python tools/validate_layer_model.py
	python tools/validate_ontology.py
	python tools/validate_cast.py --placeholder-scan
	python tools/validate.py --kernel
	python tools/tests/test_gate_log.py
	python tools/validate_retention.py --repo-scan --staged

# The pattern of life on the gates themselves. A gate nobody measures is a gate
# nobody can adjudicate, and both failure directions are silent: a check that
# never fires looks identical to a check that is working, and a check that always
# fires gets ignored rather than fixed. Thresholds are in doctrine/HYGIENE.md.
gate-telemetry:
	python tools/gate_log.py --summary
