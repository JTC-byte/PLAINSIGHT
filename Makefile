.PHONY: help validate-doctrine validate-hygiene validate-kernel preflight

# The named gates. A gate is a stable token rather than a hand-copied command
# string, so a new check joins the battery in one place. That place is
# KERNEL_GATE in tools/validate_conformance.py, not this file.
#
# What exists here is what there is to check. At Wave 0 the governed artifact is
# the doctrine corpus: 36 criteria across two rank-1 files, a pin of record they
# reconcile against, and the voice standard every tracked file is held to. The
# schema, ontology, policy and connector gates are named as PENDING inside the
# aggregator with the step that delivers each, so `validate-kernel` reports the
# gap rather than passing over it.

help:
	@echo "validate-doctrine  criterion definitions, stamps, cross-references, pin of record"
	@echo "validate-hygiene   voice, tables, citations against the register, caps, inventories"
	@echo "validate-kernel    the full battery, including what is not built yet"
	@echo "preflight          what must be green before a commit"
	@echo ""
	@python tools/validate_conformance.py --list

validate-doctrine:
	python tools/validate_doctrine.py

validate-hygiene:
	python tools/validate_hygiene.py

validate-kernel:
	python tools/validate_conformance.py --kernel-gate

# preflight is the pre-commit battery. It is deliberately the same set the hook
# runs, because a gate that is only enforced in CI is enforced only after the
# thing it guards has already been committed, and git history is the one store a
# crypto-shred cannot reach.
preflight:
	python tools/validate_doctrine.py
	python tools/validate_hygiene.py
	python tools/validate_retention.py --repo-scan --staged
