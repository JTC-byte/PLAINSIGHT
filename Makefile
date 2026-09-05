.PHONY: help validate-doctrine validate-hygiene validate-layer-model validate-ontology validate-cast test validate-kernel preflight gate-telemetry

# The named gates. A gate is a stable token rather than a hand-copied command
# string, so a new check joins the battery in one place. That place is
# KERNEL_GATE in tools/validate_conformance.py, not this file.
#
# What exists here is what there is to check. The governed artifacts are the
# doctrine corpus (58 criteria across four rank-1 files and one advisory file,
# with a pin of record they reconcile against), the layer model in spec/ that the
# schema and policy will be generated from, the selector registry in ontology/,
# the unsealed cast draft in synthetic/, and the voice standard every tracked
# file is held to. The schema, policy, divergence-register and connector gates
# are named as PENDING inside the aggregator with the step that delivers each,
# so `validate-kernel` reports the gap rather than passing over it.

help:
	@echo "validate-doctrine     criterion definitions, stamps, cross-references, pin of record"
	@echo "validate-hygiene       voice, tables, citations against the register, caps, the handoff's tense, inventories, and its self-test"
	@echo "validate-layer-model  the nine event types, discriminators, denylists, lineage, producer authority"
	@echo "validate-ontology     the closed selector vocabulary, anchors, constraints, prohibitions, matchers"
	@echo "validate-cast         the checkable half of SS-3, the confuser pair, the partition, the seal"
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

# Design gate 1: a constraint is not done until a test fails when it is removed.
# Until 2026-09-03 no test existed here, so every mechanism on disk was an
# assumption in the sense doctrine/HYGIENE.md section 2 warns about.
test:
	python tools/tests/test_gate_log.py

validate-kernel:
	python tools/validate_conformance.py --kernel-gate

# preflight is the pre-commit battery plus the telemetry test. The hook runs the
# same six commands and not the test, which CI runs as a step of its own. A gate
# that is only enforced in CI is enforced only after the thing it guards has
# already been committed, and git history is the one store a crypto-shred cannot
# reach.
preflight:
	python tools/validate_doctrine.py
	python tools/validate_hygiene.py
	python tools/validate_layer_model.py
	python tools/validate_ontology.py
	python tools/validate_cast.py --placeholder-scan
	python tools/tests/test_gate_log.py
	python tools/validate_retention.py --repo-scan --staged

# The pattern of life on the gates themselves. A gate nobody measures is a gate
# nobody can adjudicate, and both failure directions are silent: a check that
# never fires looks identical to a check that is working, and a check that always
# fires gets ignored rather than fixed. Thresholds are in doctrine/HYGIENE.md.
gate-telemetry:
	python tools/gate_log.py --summary
