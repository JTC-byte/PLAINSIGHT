#!/usr/bin/env python3
"""Retention gate: the compiled policy, the shred round trip, the repository scan,
and the pre-shred finding check.

This file replaces the Wave 0 stub tracked as D-001. The stub was wired into
`.githooks/pre-commit` so that the mechanism existed and was called, and it
returned 0 while checking nothing. That is the gap this tool closes, and the
four argv forms the stub accepted still work: `--repo-scan --staged` from the
hook and from `make preflight`, and `--repo-scan` bare from the kernel gate.

`doctrine/RETENTION.md` names this tool three times and each naming is a mode
below. RT-2 names `--policy`, RT-13 names `--finding <file> --case <id>`, and
RT-15 names `--repo-scan` wired into the pre-commit hook.
`conformance/retention/shred-roundtrip.yaml` names `--shred-roundtrip` as its
own self-lint.

Every check here is named by the defect it guards:

  R-01  A policy file that assigns a subject-carrying field to a surviving
        stratum is the RT-2 defect, and RT-2 says this tool refuses it rather
        than a reviewer noticing it. Since 2026-10-01 it reaches strata 4 and T
        as well, which RT-1 gives synthetic values only and none. Enforced by
        RETENTION_SUBJECT_VALUE_IN_SURVIVING_STRATUM.
  R-02  A strata table keyed on the integer loses one of the two stratum-1 rows.
        RT-1 states the shape as seven rows across five numbered levels plus
        telemetry, and the two stratum-1 rows carry different contents and
        different subject-value descriptions, so the stricter one disappears in
        a six-row table. Enforced by RETENTION_POLICY_STRATA_ROW_COUNT, and
        since 2026-10-01 by RETENTION_POLICY_STRATA_ROW_DRIFT, which pins each
        row by name with its stratum, subject values, lifetime and boundary.
  R-03  A strata set can be widened in the policy while the tools keep the
        narrow set, which passes both files' own checks. Reconciled against
        tools/validate_layer_model.py STRATA, SURVIVING_STRATA and
        CROSSING_STRATA by RETENTION_POLICY_STRATA_SET_DRIFT.
  R-04  A duration is one number in a file that reads as configuration, and
        changing it changes how long a person's data is held. Every stamped
        number is pinned below with its criterion, and a difference refuses
        under RETENTION_POLICY_TTL_DRIFT rather than being configured, as are
        three non-numeric rules since 2026-10-01: a case extension does not
        extend incidental content, either way round, and the case ceiling is an
        absolute deadline.
  R-05  RT-9's receipt of five checks can be five copies of one check. The
        model already pins SHRED_CHECKS for the wire; this pins it for the
        compiled policy and for the conformance fixture, under
        RETENTION_POLICY_VERIFICATION_INCOMPLETE and SHRED_ROUNDTRIP_CHECK_SET.
  R-06  A verification check that can pass for a reason other than the one
        claimed is not a check. Check 1 has to fail on the key, check 2 may not
        read a cached path, and check 3 has to tell an erroring query from a
        query that returned nothing. Enforced by
        RETENTION_POLICY_FALSE_PASS_UNGUARDED and
        SHRED_ROUNDTRIP_FALSE_PASS_UNGUARDED.
  R-07  A placeholder these artifacts carry can point at a question nobody
        recorded, and a recorded question can end up referenced by nothing.
        One direction finds half the drift, so both run:
        RETENTION_PLACEHOLDER_UNDECLARED and RETENTION_PLACEHOLDER_UNREFERENCED.
  R-08  A refusal that names no rule and offers no move is a state token rather
        than a refusal. Enforced by RETENTION_REFUSAL_PROSE_INCOMPLETE.
  R-09  An unratified criterion refuses rather than permits, and for a retention
        mechanism that means the sweep refuses to run rather than running with
        an unratified TTL. Enforced by RETENTION_POLICY_UNRATIFIED and
        SHRED_ROUNDTRIP_UNRATIFIED, both of which clear the moment the operator
        stamps the artifact in doctrine/DOCTRINE_STATUS.md. The criteria checked
        are pinned as RT-1 to RT-19 rather than read from the policy's own list,
        which RETENTION_CRITERIA_LIST_DRIFT holds to the same set.
  R-10  A live selector in a tracked file survives every mechanism in
        RETENTION.md, because git history is append-only, distributed to every
        clone, and outside the per-case crypto-shred. This is RT-15 and it is
        the mode the hook calls.
  R-18  RT-11's halt is system-wide, blocks connector dispatch, and clears only
        on a passing verify_shred, and its override is the open question U-17.
        Added 2026-10-01; enforced by RETENTION_POLICY_HALT_DRIFT.
  R-11  A repository scan can claim coverage it does not have. The shapes this
        tool matches on are reconciled against the rank-3 forms in
        ontology/selectors.yaml in both directions, and the types it does not
        reach are printed rather than implied.

Two states are printed rather than refused, because CLAUDE.md section 4 renders
a state as its consequence rather than as its token. The first is the violation
code RT-15 requires and nothing declares. The second is the set of selector
types the scan does not reach while the cast is unsealed.

Exit codes: 0 clean, 1 violations found, 2 the governed input could not be read.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - reported as an unreadable input
    yaml = None

try:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import gate_log
except Exception:  # telemetry must never be able to break a gate
    gate_log = None

# The pin-of-record reader is not optional the way telemetry is: without it
# no stamp can be read, so an import failure is a crash rather than a pass.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pin_of_record  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "policy" / "retention.yaml"
FIXTURE = ROOT / "conformance" / "retention" / "shred-roundtrip.yaml"
REGISTRY = ROOT / "ontology" / "selectors.yaml"
CODES = ROOT / "policy" / "violation-codes.yaml"
STATUS = ROOT / "doctrine" / "DOCTRINE_STATUS.md"
TRUTH = ROOT / "synthetic" / "GROUND_TRUTH.yaml"

POLICY_REL = "policy/retention.yaml"
FIXTURE_REL = "conformance/retention/shred-roundtrip.yaml"

#: Gate tokens. Two of these already exist in tools/validate_conformance.py and
#: are copied rather than coined; the other two are this tool's modes and move
#: with that file when a later step registers them. Reading VR-R4.
GATE_POLICY = "retention-policy"
GATE_SCAN = "retention-repo-scan"
GATE_ROUNDTRIP = "retention-shred-roundtrip"
GATE_FINDING = "retention-finding"

# ---------------------------------------------------------------------------
# Pinned doctrine values. Each carries the criterion that decided it. A policy
# file that differs is refused rather than followed, and widening one of these
# is a Class F change that moves the constant in the same commit as the stamp.
# ---------------------------------------------------------------------------

#: RT-1. Seven rows across five numbered levels, plus telemetry.
STRATA_ROW_COUNT = 7
#: RT-1. The two strata inside the shred boundary, which is also the set that
#: carries subject values.
INSIDE_SHRED_BOUNDARY = {0, 1}
#: RT-1's table, row by row: (stratum, carries subject values, lifetime token,
#: inside the shred boundary). Until 2026-10-01 only the row count was pinned,
#: so the authorization row could be swapped for a second skeleton row, or a
#: lifetime set to free text, with seven rows and no refusal.
STRATA_ROWS = {
    "raw_capture": (0, True, "case_ttl", True),
    "case_material": (1, True, "case_ttl", True),
    "authorization": (1, True, "case_ttl", True),
    "skeleton": (2, False, "permanent", False),
    "findings": (3, False, "permanent", False),
    "synthetic_corpus": (4, False, "permanent_in_git", False),
    "gate_telemetry": ("T", False, "rolling_90_days", False),
}
#: RT-1 to RT-19, the criteria this policy compiles. Pinned here rather than read
#: from the policy's own list, because a check that iterates the artifact's list
#: is switched off by deleting an entry from it.
EXPECTED_CRITERIA = tuple(f"RT-{n}" for n in range(1, 20))
#: Non-numeric rules that bound how long a person's data is held, as (dotted
#: path, value, criterion). No tool read them until 2026-10-01, so flipping one
#: passed every gate.
INVARIANTS = (
    ("incidental.extended_by_case_extension", False, "RT-6, SS-11"),
    ("extension.extends_incidental_content", False, "RT-6, SS-11"),
    ("case_ttl.ceiling_is", "absolute_deadline", "RT-5, reading RET-R3"),
)
#: RT-11's halt, by value. Until the completeness critic of 2026-10-01 R-18
#: matched substrings, so a halt that "blocks nothing; connector dispatch
#: continues", or clears "on a ledger entry, or verify_shred passing all five",
#: passed. The two unratified mappings stay deferred until the operator decides
#: U-03 and U-17, and this pin moves in the commit that records the decision.
HALT_PIN = {
    "trigger": "SHRED_FAILED on any case",
    "scope": "system_wide",
    "per_case": False,
    "blocks": "connector dispatch",
    "does_not_block": [
        "runner/retention_sweep.py",
        "runner/verify_shred.py",
        "runner/reconcile_ledger.py",
        "the validators in tools/",
    ],
    "clears_when": "verify_shred passes all five RT-9 checks for the failed case",
    "clearing_is_a_logged_act": True,
    "clearing_fields": ["author", "timestamp", "receipt_hash"],
    "clearing_author_authority": {"unratified": "U-03"},
    "override": {"unratified": "U-17"},
}
#: Where each HALT_PIN key comes from. RT-11 fixes the trigger, the scope and
#: the clearing; which jobs run during a halt is reading RET-R5, which the
#: operator has not confirmed, and the two deferrals are open entries. Until
#: 2026-10-01 every mismatch said "where RT-11 fixes".
HALT_SOURCE = {
    "blocks": "reading RET-R5, unconfirmed,",
    "does_not_block": "reading RET-R5, unconfirmed,",
    "clearing_author_authority": "the open entry U-03",
    "override": "the open entry U-17",
}

#: RT-9. Five checks, each once. A receipt of [1, 1, 1, 1, 1] is one check
#: counted five times, which RT-9 says is not a check.
SHRED_CHECKS = [1, 2, 3, 4, 5]

#: The stamped durations, as (dotted path in the policy, days, criterion).
#: RT-5 is flat and names no subject class; RT-6 carries the one differentiated
#: number in the corpus.
DURATIONS = (
    ("case_ttl.default_days", 30, "RT-5"),
    ("case_ttl.extension_days", 30, "RT-5"),
    ("case_ttl.ceiling_days", 60, "RT-5, decision R2"),
    ("extension.length_days", 30, "RT-5"),
    ("incidental.ttl_days", 7, "RT-6"),
    ("blob_policy.media.expires_after_days", 90, "RT-8, decision R5"),
    ("freeze.default_expiry_days", 30, "RT-17"),
    ("gate_telemetry.ttl_days", 90, "RT-19"),
)

#: RT-9 check 1. A decrypt that reports not-found, permission-denied or
#: malformed-input has not proven the key was destroyed.
FALSE_PASS_ON_KEY = ("not_found", "permission_denied", "malformed_input")

#: RT-9's passing conditions and the witness's place, by value in each artifact.
#: Until 2026-10-01 these were substring tests, so check 1 could pass "when the
#: decrypt succeeds with the key", a witness could sit "inside the enumerable
#: delete path", and checks 4 and 5 could pass "always".
CHECK1_PASSES_WHEN = "the decrypt fails on the key"
CHECK1_FAILS_WHEN_REQUIRED = frozenset(FALSE_PASS_ON_KEY) | {"decrypt_succeeds"}
WITNESS_HELD_OUTSIDE = "the enumerable delete path"
POLICY_CHECK_PASSES = {
    2: "the objects are gone",
    3: "the query errors",
    4: "stratum 2 is intact and carries the tombstone and the receipt hash",
    5: "the adjacent case is still fully readable and its blob count is unchanged",
}
FIXTURE_CHECK_PASSES = {
    2: "the objects are gone, read through the S3 API",
    3: "the query errors",
    4: "stratum 2 is intact and carries the tombstone and the receipt hash",
    5: "the canary case is still fully readable and its blob count is unchanged",
}

#: Whether the RT-16 reconcile of pinned connector versions against connectors/
#: exists in this tool. It does not: there is neither a ledger nor a connector to
#: read. The policy's enforcement entry for it must say so, and when it lands this
#: flag and that entry move in the same commit.
RT16_RECONCILE_WRITTEN = False

#: Whether AGENTS.md carries the Class C clause RT-16 names. It does not; this
#: flag and the policy's entry move together when it lands.
RT16_CLAUSE_WRITTEN = False

#: RT-16's three enforcement entries, keyed by what each one is.
RT16_ENFORCEMENT = (
    ("clause", "a Class C clause in AGENTS.md stating the rule", RT16_CLAUSE_WRITTEN),
    ("check", "a bidirectional reconcile in tools/validate_retention.py", RT16_RECONCILE_WRITTEN),
    ("code", {"unratified": "U-07"}, None),
)

#: RT-15's four enforcement parts as the policy names them, in rt15_parts order.
#: Until 2026-10-01 the flags were compared by position, so the canary entry
#: moved to the first slot could claim the clause's measurement.
RT15_PART_CLAUSES = (
    "an Execution Limits clause in AGENTS.md",
    "canary_subject_class as a required connector manifest field",
    "violation code FIXTURE_CONTAINS_LIVE_SELECTOR in policy/violation-codes.yaml",
    "tools/validate_retention.py --repo-scan wired into .githooks/pre-commit",
)

#: Whether a connector-manifest validator refuses a manifest without
#: canary_subject_class, which is the "required" half of RT-15's second part.
#: None exists, so that part is absent whatever the manifests carry.
MANIFEST_VALIDATOR_REQUIRES_CANARY = False

#: The Execution Limits sentence RT-15's first part is, read from section 4.
RT15_CLAUSE_SENTENCE = (
    "No agent writes a selector value, handle, email, phone number, or case subject "
    "name into a tracked file."
)

#: Compiled rules that bound what is held and where, by value, each with its
#: criterion. No tool read them until 2026-10-01, so each could be flipped to
#: its permissive value with every gate green.
PINNED_RULES = (
    ("full_text_index.inside_shred_boundary", True, "RT-7"),
    ("blob_policy.text.case_level_value_legal", False, "RT-8"),
    ("encryption.plaintext_blob_legal", False, "RT-4"),
    ("encryption.encrypted_from", "first_write", "RT-4"),
    ("shred.mechanisms_both_required", True, "RT-3"),
    ("finding_check.post_shred_run_possible", False, "RT-13"),
    ("freeze.renewal.required_fields", ["obligation", "expected_resolution_on"], "RT-17"),
    ("freeze.renewal.refused_when_either_is_absent", True, "RT-17"),
    ("disclosure_export.available_only_under_an_active_freeze", True, "RT-18"),
    ("disclosure_export.available_on_an_ordinary_case", False, "RT-18"),
    ("verification.all_checks_required", True, "RT-9"),
    ("gate_telemetry.tracked", False, "RT-19"),
    ("gate_telemetry.carries_subject_derived_values", False, "RT-19"),
    # Added 2026-10-01 for review finding retention-mechanism:1. The cassette
    # rule sits under strata; the overnight record of b24ae5d said it did not
    # exist in the policy, which was wrong.
    ("strata.cassette_rule.live_subject_cassette_stratum", 0, "RT-1, RT-2"),
    ("strata.cassette_rule.persisting_cassette_stratum", 4, "RT-1, RT-2"),
    ("strata.cassette_rule.permitted_capture_targets", ["S2", "N0"], "RT-1, EG-5, RT-15"),
    ("strata.cassette_rule.satisfies_rt16_floor", False, "RT-1, RT-16"),
    ("strata.permanent", [2, 3, 4], "RT-1"),
    # Added after the second review of 2026-10-01, finding rm2:6, which flipped
    # each of these with --policy green after 78131d7 said the last nine were
    # pinned.
    ("strata.declared_at", "write_time", "RT-1"),
    ("strata.decided_at_delete_time", False, "RT-1"),
    ("export_boundary.draft_and_return_brief_stratum", 1, "RT-1, RT-14"),
    ("cross_case_persistence.exception_register_present", False, "RT-2, SS-21"),
    ("extension.inaction_is_deletion", True, "RT-5"),
    ("case_ttl.applies_to_every_subject_class", True, "RT-5, which names no subject class"),
    ("blob_policy.text.scoped_by", "retain_until", "RT-8"),
    ("verification.runs_outside_the_shredding_tool", True, "RT-9"),
    ("ledger.carries_subject_derived_values", False, "RT-10"),
    ("ledger.stratum", 2, "RT-10"),
    ("ledger.reconcile.directions", "both", "RT-10"),
    ("ledger.reconcile.cached_read_path_permitted", False, "RT-9, RT-10"),
    ("finding_check.output_stratum", 3, "RT-1, RT-13"),
    ("disclosure_export.projection_or_summary_permitted", False, "RT-18"),
    ("encryption.per_case_data_key", True, "RT-4"),
    ("full_text_index.stratum", 1, "RT-7"),
    ("full_text_index.per_case", True, "RT-7"),
    ("full_text_index.shared_across_cases", False, "RT-7"),
    ("encryption.retrofittable", False, "RT-4"),
    ("freeze.stops_the_run", True, "RT-17"),
    ("freeze.stops_queued_pivots", True, "RT-17"),
    ("freeze.stops_the_sweep_for_one_case", True, "RT-17"),
    ("freeze.collects_nothing_further", True, "RT-17"),
    ("freeze.notifies_the_operator", True, "RT-17"),
    ("freeze.is_a_logged_act", True, "RT-17"),
    ("freeze.crosses_the_case_ceiling", True, "RT-17"),
    ("unratified.refuses_rather_than_permits", True, "the pin of record, doctrine/DOCTRINE_STATUS.md"),
    # Added after the third review of 2026-10-01, findings rm3:1 and rm3:12.
    ("gate_telemetry.stratum", "T", "RT-1, RT-19"),
    ("strata.rows[6].tracked", False, "RT-19"),
    ("finding_check.survivability[0].carries_subject_values", False, "RT-13"),
    ("finding_check.survivability[0].survives", True, "RT-13"),
    ("finding_check.survivability[1].carries_subject_values", False, "RT-13"),
    ("finding_check.survivability[1].survives", True, "RT-13"),
    ("finding_check.survivability[2].carries_subject_values", True, "RT-13"),
    ("finding_check.survivability[2].survives", False, "RT-2, RT-13"),
    ("cadence.steps[4].cached_read_path_permitted", False, "RT-9, RT-10"),
)

#: Every boolean or stratum value the policy compiles that is not pinned above,
#: named so that "the last unpinned rule" is a fact a check can hold. Until the
#: second review of 2026-10-01 two records claimed the last rules were pinned
#: while twenty more were read by no tool. Each one here is unpinned because it
#: has not yet been checked against doctrine by value, or because it states a
#: fact about the tree that moves when the tree does. A new boolean or stratum
#: in the policy refuses until it is pinned or named here.
UNPINNED_BY_NAME = (
    "ratification.refuses_rather_than_permits",
    "case_ttl.retain_until.is_a_column",
    "case_ttl.ceiling_refusal.required",
    "incidental.subject_relation_is_computed",
    "verification.witness.digest_recorded",
    "ledger.present_in_tree",
    "ledger.survives_the_shred",
    "ledger.reconcile.scheduled",
    "ledger.reconcile.writes_heartbeat_on_every_run",
    "ledger.pinned_connector_versions_read_from_here",
    "heartbeats.written_on_every_run_including_empty_ones",
    "heartbeats.threshold_is_per_job",
    "heartbeats.scheduled_from_day_one",
    "export_boundary.technical_control_available",
    "connector_floor.forbids_a_deletion_act",
    "connector_floor.carries_subject_values",
    "freeze.renewal.escalation.second_renewal_renders_a_distinct_state",
    "disclosure_export.minimization_applied",
    "disclosure_export.minimization_inverted_here_deliberately",
    "disclosure_export.is_a_logged_act",
    "disclosure_export.outside_every_mechanism_once_it_leaves",
    "disclosure_export.interface_states_that_at_the_moment_of_export",
    "disclosure_export.alters_the_freeze_or_the_shred_path",
    "gate_telemetry.rolling",
    "gate_telemetry.swept_on_write",
    "gate_telemetry.swept_on_read",
    "gate_telemetry.swept_by_a_scheduled_job",
    "repo_scan.enforcement_parts_all_required[1].refused_when_missing",
    "repo_scan.enforcement_parts_all_required[3].checks_anything",
    "cadence.steps[2].order_is_normative",
    "unratified.entries[4].consequential",
)


def _rule_leaves(node, path: str = "", seen: set | None = None):
    """Every boolean, a boolean spelled as a string, and every value under a key
    naming a stratum, inside lists as well. Until the third review of 2026-10-01
    the walk skipped lists, so eleven compiled booleans were read by nothing."""
    seen = set() if seen is None else seen
    if isinstance(node, (dict, list)):
        if id(node) in seen:
            return
        seen.add(id(node))
    if isinstance(node, dict):
        for key, value in node.items():
            yield from _rule_leaves(value, f"{path}.{key}" if path else str(key), seen)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from _rule_leaves(value, f"{path}[{index}]", seen)
    elif (
        isinstance(node, bool)
        or (isinstance(node, str) and node.strip().lower() in ("true", "false"))
        or path.endswith("stratum")
    ):
        yield path


#: List items whose booleans and strata are read by a check keyed on the item's
#: name rather than its place: STRATA_ROWS, RT-9's check 2 side flags, and the
#: RT-15 and RT-16 tables.
READ_BY_A_CHECK = re.compile(
    r"^(strata\.rows\[\d+\]\.(stratum|carries_subject_values|inside_shred_boundary)"
    r"|verification\.checks\[1\]\.(cached_read_path_permitted|delete_exit_code_accepted_as_evidence)"
    r"|repo_scan\.enforcement_parts_all_required\[\d+\]\.present"
    r"|connector_floor\.enforcement\[\d+\]\.present)$"
)

#: RT-15. The code doctrine requires in policy/violation-codes.yaml. That file
#: is generated from spec/layer-model.yaml and cannot be hand-edited, and the
#: code is declared in neither. VR-U3 carries the question.
DOCTRINE_SCAN_CODE = "FIXTURE_CONTAINS_LIVE_SELECTOR"
#: What a scan finding carries while the code above is undeclared. Every sibling
#: validator emits a tool-local code, so this matches the house rather than
#: substituting silently for the code doctrine names. The notice below prints on
#: every run until DOCTRINE_SCAN_CODE is declared.
LOCAL_SCAN_CODE = "RETENTION_LIVE_SELECTOR_IN_TRACKED_FILE"

# ---------------------------------------------------------------------------
# Selector shapes for --repo-scan.
#
# VR-U1 carries the question of where these belong. They are module constants
# here because the two candidate homes are closed today: ontology/selectors.yaml
# is rank 3 and this build may not edit it, and policy/matcher-calibration.yaml
# does not exist. The precedent for a shape table inside a validator is
# tools/validate_ontology.py VALUE_SHAPES, which scans one file for the same
# defect.
#
# What keeps this table honest is the reconcile below it. Every segment name
# here has to equal the placeholder name in that selector's rank-3 `form`, in
# order, so the table is a compilation of the registry rather than a second
# opinion about what a selector looks like. A form edited in the registry
# refuses here until the table moves with it.
#
# What this table deliberately does not do is match a bare value. A scan for a
# bare address, domain or handle fires 4,957 times across the 50 tracked files
# in this repository, measured on 2026-09-11: 4,869 digit runs in the generated
# conformance corpora, 39 handle-shaped tokens including thirteen in the
# Makefile, 38 domains in LICENSE, NOTICE and README, and 11 addresses. A gate
# that always fires gets routed around rather than fixed, which doctrine/
# HYGIENE.md HY-2 names as a failure direction in its own right. The typed form
# is the object RT-15 can refuse today, and the bare-shape half is reported as
# coverage this gate does not have.
# ---------------------------------------------------------------------------

SEGMENT_SHAPES = {
    "platform": r"[a-z][a-z0-9_]{1,31}",
    "opaque_id": r"[A-Za-z0-9][A-Za-z0-9_.-]{1,63}",
    "channel_id": r"[A-Za-z0-9][A-Za-z0-9_.-]{1,63}",
    "string": r"[A-Za-z0-9][A-Za-z0-9_.]{1,63}",
    "addr": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}",
    "e164": r"\+[1-9]\d{7,14}",
    # Case-insensitive since 2026-10-01: a domain is the same selector in any case.
    "fqdn": r"(?i:(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,})",
    "hex64": r"[0-9a-fA-F]{16,64}",
    "mask": r"[A-Za-z0-9._%+-]*[*•]{2,}[A-Za-z0-9._%+@*.•-]*",
    "registry": r"[a-z][a-z0-9_.-]{1,31}",
    "registration_id": r"[A-Za-z0-9][A-Za-z0-9_.-]{1,63}",
    "record_system": r"[a-z][a-z0-9_.-]{1,31}",
    "record_id": r"[A-Za-z0-9][A-Za-z0-9_.-]{1,63}",
}

#: The thirteen types ontology/selectors.yaml repo_scan calls shape_detectable,
#: each with the segment names its form declares, in order.
TYPE_SEGMENTS = {
    "platform_uid": ("platform", "opaque_id"),
    "channel": ("platform", "channel_id"),
    "handle": ("platform", "string"),
    "username_string": ("string",),
    "email": ("addr",),
    "phone": ("e164",),
    "domain": ("fqdn",),
    "image_phash": ("hex64",),
    "org_registration_number": ("registry", "registration_id"),
    "public_record_id": ("record_system", "record_id"),
    "email_hint_recovery_masked": ("mask",),
    "phone_hint_recovery_masked": ("mask",),
    "email_generated_permutation": ("addr",),
}

#: What the scan does not reach, printed on every run rather than implied. The
#: first three are the registry's own not_shape_detectable list; the fourth is
#: this tool's declared coverage gap under VR-U1.
SCAN_DOES_NOT_REACH = (
    "a person's name, an alias, and an organization's name, which are ordinary "
    "words no shape finds (ontology/selectors.yaml repo_scan.detection_gap)",
    "a postal address, a bounding box and a time window, which the registry "
    "calls partially detectable and this tool does not attempt",
    "a bare value carrying no selector type, such as an address pasted into a "
    "stack trace or a handle written into a worklog entry. VR-U1 carries the "
    "question and the measurement behind it",
    "a selector_type and value pair outside a JSON line, a .json file or a "
    ".yaml file that parses, such as one quoted in a markdown code block, and a "
    "typed value written with spaces, quotes or URL encoding inside it, or one "
    "character long",
    "git history, which no commit-time check reaches and no later act clears; "
    "it is a reach limit of any such check, not one of RT-15's four parts",
    "compressed and binary containers such as xlsx, docx, zip, pdf and images, "
    "which carry NUL bytes and refuse as unreadable rather than being read",
)

PLACEHOLDER_RE = re.compile(r"<([^<>]+)>")
#: Stamp rows and criterion rows are read by tools/pin_of_record.py.

# ---------------------------------------------------------------------------
# The questions this tool does not answer.
#
# Two registers, on the pattern the two artifacts under lint already use. A
# READING is a choice the tool had to make to exist at all, recorded so the
# operator can confirm or correct it, on the model of doctrine/
# DOCTRINE_STATUS.md's assistant-readings table. An UNRATIFIED entry is a
# question the tool refuses to answer, with the refusal stated and the legal
# options recorded.
# ---------------------------------------------------------------------------

#: (id, question, the reading taken, what would change it)
READINGS = (
    (
        "VR-R1",
        "What predicate over doctrine/DOCTRINE_STATUS.md makes a criterion ratified",
        "A recorded conclusion alone. The pin of record says every basis stamp "
        "blocks nothing mechanical, so a both-stamps predicate would make every "
        "mode here refuse every invocation",
        "A stamped basis becoming a condition, which is a rank-1 edit",
    ),
    (
        "VR-R2",
        "What --shred-roundtrip exercises while the blob store, the sweep and "
        "verify_shred are Step 11",
        "The conformance document, graded as a document. A clean run proves the "
        "fixture is internally honest and proves nothing about a shred",
        "Step 11 landing the store, at which point the executable round trip "
        "replaces this reading rather than joining it",
    ),
    (
        "VR-R3",
        "Whether --policy refuses while policy/retention.yaml is unstamped",
        "It refuses. RETENTION.md names this tool and the sweep in the same "
        "sentence as the refusal, and a retention mechanism that runs on an "
        "unratified TTL is the failure the sentence describes",
        "The operator stamping the artifact, which clears the refusal without "
        "any change here",
    ),
    (
        "VR-R4",
        "Whether the gate telemetry token is one per tool or one per mode",
        "One per mode, with two of the four copied from the tokens "
        "tools/validate_conformance.py already carries",
        "A later step registering these modes in KERNEL_GATE, which moves the "
        "token set and this constant together",
    ),
)

#: (id, class, question, legal options, how this tool refuses)
UNRATIFIED = (
    (
        "VR-U1",
        "B",
        "Where do the machine-readable shapes --repo-scan matches on live, and "
        "which rank governs widening one",
        (
            "Under each matcher entry in ontology/selectors.yaml, which is "
            "rank 3, Class B, and one source for the SS-19 argv shape gate and "
            "this scan together",
            "In policy/matcher-calibration.yaml, the file the registry already "
            "forward-references, which puts a second file behind a Class F "
            "refusal",
            "As module constants in this tool, which is rank 6 and makes "
            "narrowing the scan a tooling diff that no rank-3 validator "
            "reconciles",
        ),
        "The scan refuses to claim coverage it cannot source. It matches the "
        "typed canonical form compiled from the rank-3 selector forms, it does "
        "not run bare-value matching for any type, and every run prints the "
        "four classes it does not reach.",
    ),
    (
        "VR-U2",
        "B",
        "What bare --repo-scan scans, how it differs from --repo-scan --staged, "
        "and whether git history is in scope",
        (
            "--staged scans the index and bare scans every tracked file in the "
            "working tree, so the first full run may refuse on tracked content "
            "that predates the check",
            "Bare scans tracked files at HEAD, with history out of scope and "
            "said so",
            "Bare includes history, which is unbounded and unclearable on a "
            "published repository",
        ),
        "The scan refuses to report the repository as clean. Its summary names "
        "the file set it read and states that git history was not scanned and "
        "cannot be cleared by any act this tool performs.",
    ),
    (
        "VR-U3",
        "B",
        "Which violation code a --repo-scan finding carries, given that RT-15 "
        "requires FIXTURE_CONTAINS_LIVE_SELECTOR in policy/violation-codes.yaml "
        "and that file declares fifty-seven codes without it",
        (
            "Declare it in spec/layer-model.yaml with an emitted_by of a new "
            "kind and regenerate, which satisfies RT-15 literally and puts a "
            "code that never appears on a PSE event into the wire vocabulary",
            "Emit a tool-local code on the sibling pattern and record that the "
            "doctrine's code names the event-level case only, which leaves "
            "RT-15's third enforcement part unsatisfied as written",
            "Both, each with a stated scope",
        ),
        "The scan refuses to mint the code. It emits the tool-local code, and "
        "every run measures RT-15's four enforcement parts, names each one not yet "
        "in place, and names the rank-3 edit and regeneration the code needs. The "
        "code's line disappears when the code is declared, and the finding carries "
        "the declared code from that run onward.",
    ),
    (
        "VR-U4",
        "B",
        "What --finding reads as the case's selector set, and where its "
        "stratum-3 stamp is written",
        (
            "The case store, which EG-2 puts in ISOLATED, so the mode runs "
            "there and refuses anywhere else",
            "A caller-supplied selector-set file, which makes the tool portable "
            "and moves the failure to whoever produced the file",
            "Defer the mode until the first case close",
        ),
        "The mode refuses and writes no stamp. There is no case store to read "
        "and no stamp location, so a pass would be the finding check reporting "
        "that it had run when it had not.",
    ),
)


class Finding:
    __slots__ = ("code", "where", "detail", "moves")

    def __init__(self, code: str, where: str, detail: str, moves: str):
        self.code = code
        self.where = where
        self.detail = detail
        self.moves = moves

    def render(self) -> str:
        return (
            f"REFUSED {self.code}\n"
            f"  where: {self.where}\n"
            f"  what:  {self.detail}\n"
            f"  moves: {self.moves}"
        )


def refuse(code: str, where: str, detail: str, moves: str) -> None:
    """Print a four-line refusal before there are findings to collect."""
    print(Finding(code, where, detail, moves).render(), file=sys.stderr)


def _same(actual, want) -> bool:
    """Equal in value and in type, elementwise for lists and mappings.

    Until 2026-10-01 the pins compared with ==, so true and 1, or false and 0,
    were interchangeable, and a stratum of true passed.
    """
    if type(actual) is not type(want):
        return False
    if isinstance(want, list):
        return len(actual) == len(want) and all(_same(a, w) for a, w in zip(actual, want))
    if isinstance(want, dict):
        return set(actual) == set(want) and all(_same(actual[k], want[k]) for k in want)
    return actual == want


_INDEXED = re.compile(r"^([^\[\]]+)\[(\d+)\]$")


def dig(node, dotted: str):
    """Read a dotted path out of a nested mapping, or return None.

    A part may index a list, as in finding_check.survivability[2].survives.
    """
    cur = node
    for part in dotted.split("."):
        indexed = _INDEXED.match(part)
        key = indexed.group(1) if indexed else part
        if not isinstance(cur, dict) or key not in cur:
            return None
        cur = cur[key]
        if indexed:
            i = int(indexed.group(2))
            if not isinstance(cur, list) or i >= len(cur):
                return None
            cur = cur[i]
    return cur


def as_list(value) -> list:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


#: The exceptions a governed input of the wrong shape raises inside a check.
MALFORMED = (TypeError, AttributeError, KeyError, IndexError, RecursionError)


class Unreadable(Exception):
    """A governed input this tool reads could not be read. Exit code 2."""

    def __init__(self, code: str, where: str, detail: str, moves: str):
        super().__init__(detail)
        self.finding = Finding(code, where, detail, moves)


def _load_yaml(path: Path, rel: str, code: str, why: str, moves: str) -> dict:
    if yaml is None:
        raise Unreadable(
            code,
            rel,
            "PyYAML is not installed, so this gate cannot parse the file it "
            "grades and did not check anything",
            "pip install pyyaml, or move the retention gates to PENDING in "
            "tools/validate_conformance.py",
        )
    if not path.is_file():
        raise Unreadable(code, rel, why, moves)
    try:
        parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise Unreadable(
            code,
            rel,
            f"the file is not parseable YAML: {exc}",
            "fix the syntax; the sweep and this gate read the same parse",
        ) from None
    if not isinstance(parsed, dict):
        raise Unreadable(
            code, rel, "the file did not parse to a mapping", "restore the wrapper key"
        )
    return parsed


def load_policy() -> tuple[dict, str]:
    doc = _load_yaml(
        POLICY,
        POLICY_REL,
        "RETENTION_POLICY_UNREADABLE",
        "the compiled retention policy does not exist, so the sweep has no TTL "
        "to act on and RT-2 has nothing to refuse",
        "write policy/retention.yaml, or move the retention-policy gate to "
        "PENDING in tools/validate_conformance.py",
    )
    return doc, POLICY.read_text(encoding="utf-8")


def load_fixture() -> tuple[dict, str]:
    doc = _load_yaml(
        FIXTURE,
        FIXTURE_REL,
        "SHRED_ROUNDTRIP_UNREADABLE",
        "the shred round trip fixture does not exist, so RT-9's five checks "
        "have no recorded passing conditions and D4 is a sentence with no "
        "artifact behind it",
        "write conformance/retention/shred-roundtrip.yaml, or move the "
        "retention gates to PENDING in tools/validate_conformance.py",
    )
    return doc, FIXTURE.read_text(encoding="utf-8")


def load_registry() -> dict:
    doc = _load_yaml(
        REGISTRY,
        "ontology/selectors.yaml",
        "RETENTION_REPO_SCAN_SOURCE_UNREADABLE",
        "the selector registry does not exist, so the scan has no list of "
        "shape-detectable types and no document exemptions, and it would refuse "
        "or permit for reasons nothing governs",
        "restore ontology/selectors.yaml, or move the retention-repo-scan gate "
        "to PENDING in tools/validate_conformance.py",
    )
    if not isinstance(doc.get("repo_scan"), dict):
        raise Unreadable(
            "RETENTION_REPO_SCAN_SOURCE_UNREADABLE",
            "ontology/selectors.yaml :: repo_scan",
            "the registry carries no repo_scan block, so the scan has no "
            "governed statement of which selector types a text scan can find",
            "restore the repo_scan block, or move the retention-repo-scan gate "
            "to PENDING in tools/validate_conformance.py",
        )
    return doc


def declared_codes() -> set[str]:
    """The violation-code vocabulary, read from the file RT-15 names.

    Read rather than copied. A copy of the list here would give the repository
    two vocabularies that agree until the day one of them changes.
    """
    if yaml is None or not CODES.is_file():
        return set()
    try:
        doc = yaml.safe_load(CODES.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return set()
    out: set[str] = set()
    for entry in as_list((doc.get("violation_codes") or {}).get("codes")):
        if isinstance(entry, dict) and entry.get("code"):
            out.add(str(entry["code"]))
        elif isinstance(entry, str):
            out.add(entry)
    return out


def scan_code(codes: set[str]) -> str:
    return DOCTRINE_SCAN_CODE if DOCTRINE_SCAN_CODE in codes else LOCAL_SCAN_CODE


def load_stamps() -> str:
    if not STATUS.is_file():
        raise Unreadable(
            "DOCTRINE_STATUS_UNREADABLE",
            "doctrine/DOCTRINE_STATUS.md",
            "the pin of record does not exist. Mechanisms read that file rather "
            "than the document they enforce, so with it absent nothing here can "
            "tell a stamped criterion from an unstamped one and every mode "
            "refuses",
            "restore doctrine/DOCTRINE_STATUS.md from git, or move the "
            "retention gates to PENDING in tools/validate_conformance.py",
        )
    return STATUS.read_text(encoding="utf-8")


def stamped_criteria(status: str) -> set[str]:
    """Criteria that bind: a row in the per-criterion table, and a stamped file.

    Reading VR-R1, read since 2026-10-01 through tools/pin_of_record.py, the one
    reader validate_authorization.py and validate_doctrine.py also use. Until then
    this tool counted a row opening with a criterion id anywhere in the pin,
    including the rejected-readings table, and never asked whether
    doctrine/RETENTION.md itself carried a stamp. The Step 8 review of that date
    found both.
    """
    pin = pin_of_record.Pin(status, ROOT)
    return {c for c in pin.criteria if pin.criterion_stamped(c)}


def stamped_path(status: str, rel: str) -> bool:
    """True when the pin of record stamps this artifact as a whole.

    Read through tools/pin_of_record.py since 2026-10-01. Until then this tool
    accepted any dated line naming the path anywhere under the Ratified heading,
    with no ratifier, a review date inside words, or a Pending stamp-target hold
    beside it, and the authorization gate read the same pin a different way.
    """
    return pin_of_record.Pin(status, ROOT).artifact_stamped(rel)


def unstamped_reason(status: str, rel: str) -> str:
    return pin_of_record.Pin(status, ROOT).reason_unstamped(rel)


def layer_model_strata():
    """STRATA, SURVIVING_STRATA and CROSSING_STRATA from the layer model's tool.

    None when the module or a constant cannot be read. Until 2026-10-01 that
    case fell back to three empty sets, and R-01, RT-2's own refusal, and the
    strata-set reconcile then passed with nothing to compare against.
    """
    try:
        import validate_layer_model as lm

        return set(lm.STRATA), set(lm.SURVIVING_STRATA), set(lm.CROSSING_STRATA)
    except Exception:
        return None


def build_context() -> dict:
    policy, policy_text = load_policy()
    fixture, fixture_text = load_fixture()
    return {
        "policy": policy,
        "policy_text": policy_text,
        "fixture": fixture,
        "fixture_text": fixture_text,
        "registry": load_registry(),
        "codes": declared_codes(),
        "status": load_stamps(),
        "strata": layer_model_strata(),
    }


# ---------------------------------------------------------------------------
# --policy
# ---------------------------------------------------------------------------


def _placeholder_ids(node, path: str = "") -> list[tuple[str, str]]:
    """Every field that defers to a recorded question, with where it sits.

    The entry lists themselves are skipped. They declare the questions rather
    than deferring to them, and counting a declaration as a reference would make
    the unreferenced half of the reconcile pass on every entry.
    """
    out: list[tuple[str, str]] = []
    if isinstance(node, dict):
        if isinstance(node.get("unratified"), str):
            out.append((str(node["unratified"]), path))
        for key, value in node.items():
            if key in ("entries", "local_entries"):
                continue
            out.extend(_placeholder_ids(value, f"{path}.{key}" if path else key))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            out.extend(_placeholder_ids(value, f"{path}[{index}]"))
    return out


def _check_refusal_prose(entry: dict, where: str) -> list[Finding]:
    """R-08. A refusal states what was refused, which rule, and the moves."""
    out: list[Finding] = []
    text = str(entry.get("refuses_as") or "")
    missing = [label for label in ("where:", "rule:", "moves:") if label not in text]
    if not text.strip():
        missing = ["the whole sentence"]
    if missing:
        out.append(
            Finding(
                "RETENTION_REFUSAL_PROSE_INCOMPLETE",
                where,
                "the refusal this placeholder renders is missing "
                f"{', '.join(missing)}, so a reader is told that something was "
                "refused without being told which rule refused it or what may "
                "legally be done next. CLAUDE.md section 4 governs refusal "
                "strings as prose and renders a state as its consequence",
                "write the refusal with the consequence first, then where, "
                "rule and moves, on the pattern of the entries beside it",
            )
        )
    return out


def _check_placeholders(
    node: dict, entries: list, rel: str, prefix: str, pool: dict | None = None
) -> list[Finding]:
    """R-07. Both directions of the placeholder reconcile, plus completeness.

    `pool` is the set of entries declared in the other artifact. An entry may
    carry its options by pointing at one of those with `tracks` rather than
    restating them, because two independently resolvable copies of one question
    can be stamped to two different answers.
    """
    out: list[Finding] = []
    pool = pool or {}
    declared = {
        str(entry.get("id")): entry for entry in entries if isinstance(entry, dict)
    }
    used = _placeholder_ids(node)
    for pid, where in used:
        if pid not in declared and pid.startswith(prefix):
            out.append(
                Finding(
                    "RETENTION_PLACEHOLDER_UNDECLARED",
                    f"{rel} :: {where or pid}",
                    f"the field defers to {pid} and no entry declares it, so the "
                    "field reads as a recorded open question while the question "
                    "itself was never written down",
                    f"add the {pid} entry with its question, its legal options, "
                    "its sources and its refusal, or fill the field with a "
                    "ratified value",
                )
            )
    referenced = {pid for pid, _ in used}
    for pid, entry in declared.items():
        if pid not in referenced and not entry.get("referenced_by"):
            out.append(
                Finding(
                    "RETENTION_PLACEHOLDER_UNREFERENCED",
                    f"{rel} :: {pid}",
                    "the entry records an open question that no field defers "
                    "to, so nothing in the compiled artifact refuses on it and "
                    "stamping it would change no behaviour",
                    "point a field at it, or delete the entry",
                )
            )
        options = as_list(entry.get("legal_options"))
        tracks = [str(part) for part in as_list(entry.get("tracks"))]
        tracked = next((part for part in tracks if part in pool), None)
        if tracks and tracked is None:
            out.append(
                Finding(
                    "RETENTION_PLACEHOLDER_UNDECLARED",
                    f"{rel} :: {pid}",
                    "the entry says it tracks a question in another artifact and "
                    f"none of {tracks} is declared there, so the options it "
                    "defers to cannot be read and stamping the other artifact "
                    "would leave this one open with nothing to point at",
                    "correct the pointer, or restate the options here",
                )
            )
        if tracked is not None:
            options = as_list((pool.get(tracked) or {}).get("legal_options"))
        if not entry.get("question") or len(options) < 2 or not entry.get("sources"):
            out.append(
                Finding(
                    "RETENTION_PLACEHOLDER_INCOMPLETE",
                    f"{rel} :: {pid}",
                    "the entry does not carry a question, at least two legal "
                    "options and its sources. An open question with one option "
                    "is a decision written as a placeholder, which is the shape "
                    "an invented default takes when it is dressed as a gap",
                    "state the question, record every option that is legal "
                    "under doctrine, and cite the criteria that bound it",
                )
            )
        out.extend(_check_refusal_prose(entry, f"{rel} :: {pid}"))
    return out


def check_policy(ctx: dict) -> list[Finding]:
    """Grade policy/retention.yaml against doctrine/RETENTION.md."""
    out: list[Finding] = []
    doc = ctx["policy"]
    text = ctx["policy_text"]

    # House convention: one top-level wrapper key named after the file, so a
    # mistyped key fails closed rather than loading an empty policy.
    if list(doc) != ["retention"]:
        out.append(
            Finding(
                "RETENTION_POLICY_WRAPPER_KEY",
                POLICY_REL,
                "the file does not carry exactly one top-level key named "
                f"retention, it carries {sorted(doc)}. A loader that unwraps by "
                "name reads nothing from a mistyped key, and a policy that "
                "loads as empty permits everything it was written to bound",
                "restore the single retention wrapper key, on the pattern of "
                "policy/producer-authority.yaml and policy/violation-codes.yaml",
            )
        )
        return out
    pol = doc["retention"]

    # R-15. The artifact and its lint may not drift apart.
    if dig(pol, "self_lint") != "tools/validate_retention.py":
        out.append(
            Finding(
                "RETENTION_POLICY_SELF_LINT_DRIFT",
                f"{POLICY_REL} :: retention.self_lint",
                "the policy names a self-lint other than this tool, so the file "
                "and the check that refuses its drift from doctrine no longer "
                "point at each other and either could move alone",
                "name tools/validate_retention.py, or move the check to the "
                "tool the policy names",
            )
        )

    # R-17. Hand-authored, and not one of the generator's five targets.
    if re.search(r"^#\s*GENERATED by tools/generate_pse\.py", text, re.M):
        out.append(
            Finding(
                "RETENTION_POLICY_GENERATED_CLAIM",
                POLICY_REL,
                "the file carries the generated banner. tools/generate_pse.py "
                "owns five targets and this is not one of them, so the banner "
                "claims a drift check that nothing performs and invites an "
                "editor to regenerate a Class F artifact from rank 3",
                "restore the hand-authored header naming this tool as the "
                "self-lint, or add the file to the generator and to its --check",
            )
        )

    # R-02 and R-04. The strata table.
    strata = pol.get("strata") or {}
    rows = [row for row in as_list(strata.get("rows")) if isinstance(row, dict)]
    if len(rows) != STRATA_ROW_COUNT:
        out.append(
            Finding(
                "RETENTION_POLICY_STRATA_ROW_COUNT",
                f"{POLICY_REL} :: retention.strata.rows",
                f"the table carries {len(rows)} rows and RT-1 states seven "
                "across five numbered levels plus telemetry. The two stratum-1 "
                "rows carry different contents and different subject-value "
                "descriptions, so a table keyed on the integer silently loses "
                "the stricter of them",
                "restore the seven rows, each keyed by name and each declaring "
                "its stratum token",
            )
        )

    # R-02, by identity. Each RT-1 row by name, with every column it pins.
    names = [str(row.get("name")) for row in rows]
    drift = sorted(set(STRATA_ROWS) - set(names))
    drift_text = [f"missing {n}" for n in drift]
    drift_text += [f"unexpected {n}" for n in sorted(set(names) - set(STRATA_ROWS))]
    drift_text += [f"duplicate {n}" for n in sorted({n for n in names if names.count(n) > 1})]
    for row in rows:
        want = STRATA_ROWS.get(str(row.get("name")))
        got = (
            row.get("stratum"),
            row.get("carries_subject_values"),
            row.get("lifetime"),
            row.get("inside_shred_boundary"),
        )
        if want and not _same(list(got), list(want)):
            drift_text.append(f"{row.get('name')} reads {got} where RT-1 states {want}")
    if drift_text:
        out.append(
            Finding(
                "RETENTION_POLICY_STRATA_ROW_DRIFT",
                f"{POLICY_REL} :: retention.strata.rows",
                "the strata table is not RT-1's table: "
                + "; ".join(drift_text)
                + ". Each row's stratum, subject values, lifetime and boundary are "
                "how long a kind of material lives, and a table that keeps seven rows "
                "can still lose the stricter one",
                "restore the RT-1 values; or amend RT-1 under a dated Class F stamp "
                "in doctrine/DOCTRINE_STATUS.md and move STRATA_ROWS in this tool "
                "in the same commit",
            )
        )

    lm_strata = ctx.get("strata", layer_model_strata())
    if lm_strata is None:
        out.append(
            Finding(
                "RETENTION_LAYER_MODEL_UNREADABLE",
                "tools/validate_layer_model.py",
                "STRATA, SURVIVING_STRATA and CROSSING_STRATA could not be read "
                "from the layer model's tool, so R-01, RT-2's own refusal, and the "
                "strata-set reconcile have nothing to compare against. Until "
                "2026-10-01 this case fell back to empty sets and passed",
                "restore tools/validate_layer_model.py and its three constants; "
                "this tool keeps no copy of them, because a second pin beside the "
                "layer model's would drift from it",
            )
        )
        return out
    model_strata, model_surviving, model_crossing = lm_strata

    row_names = set()
    for row in rows:
        name = str(row.get("name") or "?")
        where = f"{POLICY_REL} :: retention.strata.rows.{name}"
        row_names.add(name)
        missing = [
            field
            for field in (
                "stratum",
                "contents",
                "carries_subject_values",
                "lifetime",
                "inside_shred_boundary",
            )
            if field not in row
        ]
        if missing:
            out.append(
                Finding(
                    "RETENTION_POLICY_STRATUM_INCOMPLETE",
                    where,
                    f"the row does not declare {', '.join(missing)}. RT-1 says a "
                    "stratum is declared at write time rather than decided at "
                    "delete time, and a row missing one of these columns leaves "
                    "the write path with nothing to declare",
                    "complete the row from the RT-1 table",
                )
            )
            continue
        stratum = row["stratum"]
        if model_strata and stratum not in model_strata:
            out.append(
                Finding(
                    "RETENTION_POLICY_STRATA_SET_DRIFT",
                    where,
                    f"the row declares stratum {stratum!r}, which is outside the "
                    "set the layer model and its validator pin. A stratum "
                    "nothing else knows about has no egress rule, no lifetime "
                    "and no shred behaviour",
                    "use a declared stratum, or widen STRATA in "
                    "tools/validate_layer_model.py and this policy in one "
                    "commit against a dated stamp in doctrine/DOCTRINE_STATUS.md",
                )
            )
            continue

        # R-01. RT-2's own refusal, and the reason this mode exists. Since
        # 2026-10-01 it reaches every stratum outside the shred boundary: RT-1
        # gives stratum 4 synthetic values only and stratum T none by
        # construction, and RT-2's sentence names 2 and 3 because those are the
        # strata a subject value could plausibly reach.
        if row.get("carries_subject_values") is True and (
            stratum in model_surviving or stratum not in INSIDE_SHRED_BOUNDARY
        ):
            out.append(
                Finding(
                    "RETENTION_SUBJECT_VALUE_IN_SURVIVING_STRATUM",
                    where,
                    f"the row carries subject values and sits in stratum "
                    f"{stratum}, which survives the shred. RT-2 calls that a "
                    "defect rather than a judgment call: the material outlives "
                    "the case it belonged to, and no later act reaches it",
                    "move the field to stratum 0 or 1, derive a value that "
                    "carries nothing about the subject, or drop it",
                )
            )

        # R-04. The boundary and the lifetime have to agree with RT-1.
        inside = row.get("inside_shred_boundary") is True
        if isinstance(stratum, int) and inside != (stratum in INSIDE_SHRED_BOUNDARY):
            out.append(
                Finding(
                    "RETENTION_POLICY_SHRED_BOUNDARY_DRIFT",
                    where,
                    f"stratum {stratum} is declared "
                    f"{'inside' if inside else 'outside'} the shred boundary and "
                    "RT-1 puts it on the other side. The boundary decides what a "
                    "shred destroys, so a row on the wrong side either survives "
                    "when it should die or dies when the audit trail needs it",
                    "restore the RT-1 value, or change RT-1 first",
                )
            )
        if inside and str(row.get("lifetime")).startswith("permanent"):
            out.append(
                Finding(
                    "RETENTION_POLICY_SHRED_BOUNDARY_DRIFT",
                    where,
                    "the row is inside the shred boundary and permanent at once. "
                    "Those two cannot both hold: an object the shred destroys "
                    "does not survive the case",
                    "set the lifetime to the case TTL, or move the row outside "
                    "the boundary",
                )
            )

    for label, declared, pinned, why in (
        (
            "surviving",
            set(as_list(strata.get("surviving"))),
            model_surviving,
            "RT-2 refuses a subject-carrying field in a surviving stratum, so a "
            "wider list here narrows what that refusal covers",
        ),
        (
            "crossing_to_local",
            set(as_list(strata.get("crossing_to_local"))),
            model_crossing,
            "EG-5 fixes which strata cross outward, and a stratum added here "
            "leaves ISOLATED without an egress decision",
        ),
    ):
        if pinned and declared != pinned:
            out.append(
                Finding(
                    "RETENTION_POLICY_STRATA_SET_DRIFT",
                    f"{POLICY_REL} :: retention.strata.{label}",
                    f"the policy declares {sorted(declared, key=str)} and "
                    f"tools/validate_layer_model.py pins "
                    f"{sorted(pinned, key=str)}. {why}",
                    "restore the pinned set, or move both in one commit against "
                    "a dated Class F stamp in doctrine/DOCTRINE_STATUS.md",
                )
            )

    # R-04's non-numeric half. Each rule bounds how long a person's data is held.
    for path, value, criterion in INVARIANTS:
        actual = dig(pol, path)
        if not _same(actual, value):
            out.append(
                Finding(
                    "RETENTION_POLICY_TTL_DRIFT",
                    f"{POLICY_REL} :: retention.{path}",
                    f"the policy carries {actual!r} and {criterion} fix {value!r}. "
                    "Flipping this rule lengthens how long a person's data is held "
                    "with every number unchanged",
                    f"restore {value!r}; or ratify the change with a dated stamp in "
                    "doctrine/DOCTRINE_STATUS.md and move INVARIANTS in this tool in "
                    "the same commit",
                )
            )

    # R-04. Every stamped duration.
    for path, days, criterion in DURATIONS:
        actual = dig(pol, path)
        if not _same(actual, days):
            out.append(
                Finding(
                    "RETENTION_POLICY_TTL_DRIFT",
                    f"{POLICY_REL} :: retention.{path}",
                    f"the policy carries {actual!r} and {criterion} stamps "
                    f"{days}. This number is how long a person's data is held, "
                    "and it is a one-line diff in a file that reads as "
                    "configuration, which CLAUDE.md gate 2 names as the shape a "
                    "Class F change takes when it looks like a Class B one",
                    f"restore {days}, or ratify the new number with a dated "
                    "stamp in doctrine/DOCTRINE_STATUS.md and move DURATIONS in "
                    "tools/validate_retention.py in that same commit",
                )
            )

    # R-05 and R-06. RT-9's five checks and their false-pass discriminations.
    verification = pol.get("verification") or {}
    checks = [c for c in as_list(verification.get("checks")) if isinstance(c, dict)]
    ids = [c.get("id") for c in checks]
    if sorted(i for i in ids if isinstance(i, int)) != SHRED_CHECKS or len(ids) != len(
        SHRED_CHECKS
    ):
        out.append(
            Finding(
                "RETENTION_POLICY_VERIFICATION_INCOMPLETE",
                f"{POLICY_REL} :: retention.verification.checks",
                f"the compiled checks are {ids} and RT-9 is five checks, each "
                "once. A receipt of one check counted five times reports a "
                "verification that never distinguished the five things it "
                "claims to have distinguished",
                "restore checks 1 through 5, each once, each with the object it "
                "acts on and the condition it passes under",
            )
        )
    by_id = {c.get("id"): c for c in checks}
    first = by_id.get(1) or {}
    fails = {str(x) for x in as_list(first.get("fails_when"))}
    if str(first.get("passes_when") or "") != CHECK1_PASSES_WHEN or not (
        CHECK1_FAILS_WHEN_REQUIRED <= fails
    ):
        out.append(
            Finding(
                "RETENTION_POLICY_FALSE_PASS_UNGUARDED",
                f"{POLICY_REL} :: retention.verification.checks.1",
                "check 1 does not require the decrypt to fail on the key and "
                "name not-found, permission-denied and malformed-input as "
                "failures. Each of those three reports that nothing could be "
                "read for a reason other than the key being gone, so the check "
                "would pass while proving nothing about the key",
                "restore the passing condition to the decrypt failing on the "
                "key, and list the three false passes as failures",
            )
        )
    second = by_id.get(2) or {}
    if second.get("cached_read_path_permitted") is not False or second.get(
        "delete_exit_code_accepted_as_evidence"
    ) is not False:
        out.append(
            Finding(
                "RETENTION_POLICY_FALSE_PASS_UNGUARDED",
                f"{POLICY_REL} :: retention.verification.checks.2",
                "check 2 does not forbid a cached read path and a DELETE exit "
                "code as evidence of absence. The measured incident behind RT-9 "
                "is a read path that served the first write of a key after the "
                "object had been overwritten and deleted",
                "restore both flags to false, so absence is read over the S3 "
                "API and never inferred from a delete's own result",
            )
        )
    third = by_id.get(3) or {}
    if "query_returns_zero_rows" not in {
        str(x) for x in as_list(third.get("fails_when"))
    }:
        out.append(
            Finding(
                "RETENTION_POLICY_FALSE_PASS_UNGUARDED",
                f"{POLICY_REL} :: retention.verification.checks.3",
                "check 3 does not name a query returning zero rows as a "
                "failure. The table is gone and the table returned nothing are "
                "different facts that look identical in a result set, and only "
                "the first is evidence of a shred",
                "restore query_returns_zero_rows to the check's failure list",
            )
        )

    for cid, want in POLICY_CHECK_PASSES.items():
        if str((by_id.get(cid) or {}).get("passes_when") or "") != want:
            out.append(
                Finding(
                    "RETENTION_POLICY_FALSE_PASS_UNGUARDED",
                    f"{POLICY_REL} :: retention.verification.checks.{cid}",
                    f"check {cid}'s passing condition is not RT-9's: it must pass only "
                    f"when {want}. A check that can pass for another reason is not a check",
                    f"restore the passing condition to {want!r}; or ratify RT-9's "
                    "change and move POLICY_CHECK_PASSES in this tool in the same commit",
                )
            )

    # Every boolean and stratum the policy compiles is pinned or named as not.
    known = (
        {path for path, _, _ in PINNED_RULES}
        | {path for path, _, _ in INVARIANTS}
        | {path for path, _, _ in DURATIONS}
        | {f"halt.{key}" for key in HALT_PIN}
        | set(UNPINNED_BY_NAME)
    )
    leaves = set(_rule_leaves(pol))
    for path in sorted(p for p in leaves - known if not READ_BY_A_CHECK.match(p)):
        out.append(
            Finding(
                "RETENTION_POLICY_RULE_UNCLASSIFIED",
                f"{POLICY_REL} :: retention.{path}",
                "the policy compiles a boolean or stratum that this tool neither pins "
                "nor names as unpinned, so it can be flipped with every gate green and "
                "no record can say which rules are left",
                "pin it in PINNED_RULES with the criterion that fixes it; or name it in "
                "UNPINNED_BY_NAME with why it is not pinned",
            )
        )
    for path in sorted(set(UNPINNED_BY_NAME) - leaves):
        out.append(
            Finding(
                "RETENTION_POLICY_RULE_UNCLASSIFIED",
                f"{POLICY_REL} :: retention.{path}",
                "UNPINNED_BY_NAME names a rule the policy no longer compiles, so the list "
                "no longer says which rules are left",
                "remove it from UNPINNED_BY_NAME; or restore the rule",
            )
        )

    # Compiled rules that bound what is held and where.
    for path, value, criterion in PINNED_RULES:
        actual = dig(pol, path)
        if not _same(actual, value):
            out.append(
                Finding(
                    "RETENTION_POLICY_RULE_DRIFT",
                    f"{POLICY_REL} :: retention.{path}",
                    f"the policy carries {actual!r} and {criterion} fixes {value!r}. "
                    "Flipping this rule changes what is held, where, or for how long "
                    "with every duration unchanged",
                    f"restore {value!r}; or ratify the change with a dated stamp in "
                    "doctrine/DOCTRINE_STATUS.md and move PINNED_RULES in this tool in "
                    "the same commit",
                )
            )

    # Every enforcement entry states whether it exists, and the state is measured
    # where it can be. Until 2026-10-01 RT-16's reconcile entry carried no present
    # flag and read as implemented, while this tool printed on every run that it
    # does not exist, and RT-15's flags were compared with the tree only inside
    # the self-test.
    for block in ("repo_scan.enforcement_parts_all_required", "connector_floor.enforcement"):
        for index, entry in enumerate(as_list(dig(pol, block))):
            if not isinstance(entry, dict):
                continue
            # Skipped only when the entry is nothing but a deferral. Until
            # 2026-10-01 any unratified mapping anywhere in it excused it.
            if len(entry) == 1 and all(
                isinstance(v, dict) and set(v) == {"unratified"} for v in entry.values()
            ):
                continue
            if not isinstance(entry.get("present"), bool):
                out.append(
                    Finding(
                        "RETENTION_POLICY_ENFORCEMENT_UNSTATED",
                        f"{POLICY_REL} :: retention.{block}[{index}]",
                        "the enforcement entry does not say whether it exists, so it "
                        "reads as implemented whether or not anything runs",
                        "add present: true or present: false; or replace the entry with "
                        "an unratified mapping naming the open question",
                    )
                )
    out += rt15_table_findings(pol, ctx.get("codes") or set())
    out += rt16_table_findings(pol)

    # R-09's write-path half: RT-9 sends the witness mechanics to the fixture
    # and keeps three properties the store has to know at first write.
    witness = verification.get("witness") or {}
    if (
        witness.get("count_per_case") != 1
        or witness.get("designated_at") != "first_write"
        or witness.get("held_outside") != WITNESS_HELD_OUTSIDE
    ):
        out.append(
            Finding(
                "RETENTION_POLICY_WITNESS_UNDESIGNATED",
                f"{POLICY_REL} :: retention.verification.witness",
                "the witness is not declared as one ciphertext per case, "
                "designated at first write, held outside the enumerable delete "
                "path. A store that designates no witness at first write leaves "
                "check 1 with nothing to try the key against at the first real "
                "case, and a witness inside the delete path makes check 1 pass "
                "on a not-found",
                "restore the three properties RT-9 states, and leave the "
                "designation mechanics to "
                "conformance/retention/shred-roundtrip.yaml",
            )
        )

    # R-07 and R-08.
    out.extend(
        _check_placeholders(
            pol, as_list(dig(pol, "unratified.entries")), POLICY_REL, "U-"
        )
    )

    # R-18. RT-11's halt, which nothing graded until 2026-10-01. The Step 8
    # adversarial review found the compiled block carried a permitted override
    # the pin of record's RT-11 row says does not exist, and no check read the
    # block at all, so it could have been made per-case or cleared on a ledger
    # entry without a refusal.
    halt = dig(pol, "halt")
    drift: list[str] = []
    if not isinstance(halt, dict):
        drift.append("the halt block is absent")
    else:
        for key, want in HALT_PIN.items():
            if not _same(halt.get(key), want):
                drift.append(
                    f"halt.{key} reads {halt.get(key)!r} where "
                    f"{HALT_SOURCE.get(key, 'RT-11')} fixes {want!r}"
                )
    acts = [a for a in as_list(dig(pol, "ledger.additional_recorded_acts")) if isinstance(a, dict)]
    overrides = [a for a in acts if a.get("name") == "halt_override"]
    if len(overrides) != 1 or overrides[0].get("unratified") != "U-17":
        drift.append("the ledger's halt_override act is not the single U-17 deferral")
    clearings = [a for a in acts if a.get("name") == "halt_clearing"]
    if len(clearings) != 1 or clearings[0].get("fields") != HALT_PIN["clearing_fields"]:
        drift.append("the ledger's halt_clearing act does not record author, timestamp and receipt_hash")
    if drift:
        out.append(
            Finding(
                "RETENTION_POLICY_HALT_DRIFT",
                f"{POLICY_REL} :: retention.halt",
                "RT-11's halt is compiled wider than the pin of record allows: "
                + "; ".join(drift)
                + ". The pin's RT-11 row reads 'Cleared only by a passing "
                "verify_shred, logged. No override', and a retention mechanism "
                "that can fail without stopping collection is the failure RT-11 "
                "exists to prevent",
                "restore the halt as system-wide, blocking connector dispatch "
                "and clearing only on a passing verify_shred; or keep the "
                "override deferred to its unratified entry until the operator "
                "decides it in doctrine/DOCTRINE_STATUS.md",
            )
        )

    # R-09. The designed refusal, and the check that clears when it is stamped.
    status = ctx["status"]
    listed = [str(c) for c in as_list(dig(pol, "ratification.criteria_compiled_here"))]
    if tuple(listed) != EXPECTED_CRITERIA:
        out.append(
            Finding(
                "RETENTION_CRITERIA_LIST_DRIFT",
                f"{POLICY_REL} :: retention.ratification.criteria_compiled_here",
                f"the policy lists {listed} and compiles RT-1 to RT-19. The stamp "
                "check below runs over the pinned set, so a criterion dropped from "
                "this list is still checked, and the list itself is refused for "
                "saying otherwise",
                "restore RT-1 to RT-19 in order; or ratify the doctrine change that "
                "adds or removes a criterion and move EXPECTED_CRITERIA in this tool "
                "in the same commit",
            )
        )
    for criterion in EXPECTED_CRITERIA:
        if str(criterion) not in stamped_criteria(status):
            out.append(
                Finding(
                    "RETENTION_CRITERION_UNSTAMPED",
                    f"doctrine/DOCTRINE_STATUS.md :: {criterion}",
                    f"the policy compiles {criterion} and the pin of record "
                    "does not bind it: either the per-criterion table carries no "
                    "row for it, or doctrine/RETENTION.md is unstamped ("
                    f"{unstamped_reason(status, 'doctrine/RETENTION.md') or 'it is stamped'}). "
                    "A criterion that does not bind refuses rather than permits, "
                    "so the rule compiled from it binds nothing",
                    f"add the {criterion} row to the per-criterion table; or "
                    "restore doctrine/RETENTION.md's 'all criteria' range row; or "
                    "remove the rule this policy compiled from it",
                )
            )
    if not stamped_path(status, POLICY_REL):
        out.append(
            Finding(
                "RETENTION_POLICY_UNRATIFIED",
                "doctrine/DOCTRINE_STATUS.md",
                "THE RETENTION SWEEP MAY NOT RUN AND NO CASE MAY OPEN. The pin "
                "of record does not stamp policy/retention.yaml ("
                f"{unstamped_reason(status, POLICY_REL)}), and "
                "an unratified criterion refuses rather than permits. For a "
                "retention mechanism that means the sweep refuses to run rather "
                "than running with an unratified TTL, which is what "
                "doctrine/RETENTION.md states where it names this tool",
                f"stamp policy/retention.yaml with {pin_of_record.ROW_FORMAT}, "
                "which clears this refusal with no change to this tool; or leave "
                "the sweep stopped and open no "
                "case, which is the state this refusal describes",
            )
        )
    return out


# ---------------------------------------------------------------------------
# --shred-roundtrip
# ---------------------------------------------------------------------------


def check_roundtrip(ctx: dict) -> list[Finding]:
    """Grade the conformance document. Reading VR-R2 bounds what this proves."""
    out: list[Finding] = []
    doc = ctx["fixture"]
    if list(doc) != ["shred_roundtrip"]:
        out.append(
            Finding(
                "SHRED_ROUNDTRIP_WRAPPER_KEY",
                FIXTURE_REL,
                "the file does not carry exactly one top-level key named "
                f"shred_roundtrip, it carries {sorted(doc)}. A loader that "
                "unwraps by name reads nothing from a mistyped key, and a "
                "fixture that loads as empty grades everything as passing",
                "restore the single shred_roundtrip wrapper key",
            )
        )
        return out
    fx = doc["shred_roundtrip"]

    verify = fx.get("verify_step") or {}
    checks = [c for c in as_list(verify.get("checks")) if isinstance(c, dict)]
    ids = [c.get("id") for c in checks]
    if sorted(i for i in ids if isinstance(i, int)) != SHRED_CHECKS or len(ids) != len(
        SHRED_CHECKS
    ):
        out.append(
            Finding(
                "SHRED_ROUNDTRIP_CHECK_SET",
                f"{FIXTURE_REL} :: shred_roundtrip.verify_step.checks",
                f"the fixture models {ids} and RT-9 is five checks, each once. "
                "One check counted five times is the receipt RT-9 names as not "
                "being a check at all",
                "restore checks 1 through 5, each once",
            )
        )
    for check in checks:
        if not check.get("acts_on") or not check.get("passes_when"):
            out.append(
                Finding(
                    "SHRED_ROUNDTRIP_CHECK_INCOMPLETE",
                    f"{FIXTURE_REL} :: verify_step.checks.{check.get('id')}",
                    "the check does not name the object it acts on and the "
                    "condition it passes under, so a run could report it green "
                    "without anyone being able to say what was examined",
                    "state acts_on and passes_when for the check",
                )
            )
    by_id = {c.get("id"): c for c in checks}

    first = by_id.get(1) or {}
    fails = {str(x) for x in as_list(first.get("fails_when"))}
    if str(first.get("passes_when") or "") != CHECK1_PASSES_WHEN or not (
        CHECK1_FAILS_WHEN_REQUIRED <= fails
    ):
        out.append(
            Finding(
                "SHRED_ROUNDTRIP_FALSE_PASS_UNGUARDED",
                f"{FIXTURE_REL} :: verify_step.checks.1",
                "check 1 does not require the decrypt to fail on the key while "
                "naming not-found, permission-denied and malformed-input as "
                "failures. A draft of RT-9 pointed check 1 at a blob check 2 "
                "requires to be gone, and it would have passed on a not-found "
                "while reporting that the key had been destroyed",
                "restore the passing condition and the three false passes",
            )
        )
    second = by_id.get(2) or {}
    if second.get("cached_read_path_permitted") is not False or second.get(
        "delete_exit_code_accepted_as_evidence"
    ) is not False:
        out.append(
            Finding(
                "SHRED_ROUNDTRIP_FALSE_PASS_UNGUARDED",
                f"{FIXTURE_REL} :: verify_step.checks.2",
                "check 2 does not forbid a cached read path and a DELETE exit "
                "code as evidence. Both were measured serving a stale answer in "
                "the precedent this criterion is written from",
                "restore both flags to false",
            )
        )
    third = by_id.get(3) or {}
    if "query_returns_zero_rows" not in {
        str(x) for x in as_list(third.get("fails_when"))
    }:
        out.append(
            Finding(
                "SHRED_ROUNDTRIP_FALSE_PASS_UNGUARDED",
                f"{FIXTURE_REL} :: verify_step.checks.3",
                "check 3 does not name a query returning zero rows as a "
                "failure, so the fixture accepts an empty result as proof that "
                "the table is gone",
                "restore query_returns_zero_rows to the check's failure list",
            )
        )

    for cid, want in FIXTURE_CHECK_PASSES.items():
        if str((by_id.get(cid) or {}).get("passes_when") or "") != want:
            out.append(
                Finding(
                    "SHRED_ROUNDTRIP_FALSE_PASS_UNGUARDED",
                    f"{FIXTURE_REL} :: verify_step.checks.{cid}",
                    f"check {cid}'s passing condition is not RT-9's: it must pass only "
                    f"when {want}",
                    f"restore the passing condition to {want!r}",
                )
            )
    shred = fx.get("shred_step") or {}
    if shred.get("acts_on") != "target" or shred.get("does_not_act_on") != "canary":
        out.append(
            Finding(
                "SHRED_ROUNDTRIP_NO_CANARY",
                f"{FIXTURE_REL} :: shred_roundtrip.shred_step",
                "the shred step does not act on the target alone and leave the canary "
                "untouched, so check 5 has no untouched case to read",
                "set acts_on to target and does_not_act_on to canary",
            )
        )

    create = fx.get("create_step") or {}
    roles = [str(r) for r in as_list(create.get("case_roles"))]
    if create.get("case_count") != 2 or "canary" not in roles:
        out.append(
            Finding(
                "SHRED_ROUNDTRIP_NO_CANARY",
                f"{FIXTURE_REL} :: shred_roundtrip.create_step",
                "the scenario does not build a second, adjacent case. RT-9 "
                "check 5 reads an adjacent case to catch an over-eager shred, "
                "whose failure mode is silent: a sweep with a bad case-id "
                "filter that destroys two cases reports one success",
                "restore the target and canary pair, or delete check 5 and say "
                "in RT-9 that anti-overreach is unverified",
            )
        )
    wrapping = create.get("key_wrapping_rule") or {}
    if (
        create.get("atomic") is not True
        or wrapping.get("per_case_data_key") is not True
        or wrapping.get("encrypted_from") != "first_write"
        or wrapping.get("plaintext_intermediate_state_legal") is not False
    ):
        out.append(
            Finding(
                "SHRED_ROUNDTRIP_PLAINTEXT_LEGAL",
                f"{FIXTURE_REL} :: shred_roundtrip.create_step",
                "the create step admits a state in which case material exists "
                "before it is encrypted. RT-4 is the criterion that cannot be "
                "retrofitted: a blob written in plaintext is outside the "
                "crypto-shred forever, so create and encrypt are one act rather "
                "than two steps",
                "restore atomic, the per-case data key from first write, and "
                "the illegality of a plaintext intermediate state",
            )
        )

    witness = None
    for built in as_list(create.get("builds")):
        if isinstance(built, dict) and "witness" in str(built.get("object") or ""):
            witness = built
            break
    if witness is None or (
        witness.get("designated_at") != "first_write"
        or witness.get("held_outside") != WITNESS_HELD_OUTSIDE
        or witness.get("count_per_case") != 1
    ):
        out.append(
            Finding(
                "SHRED_ROUNDTRIP_WITNESS_UNDESIGNATED",
                f"{FIXTURE_REL} :: shred_roundtrip.create_step.builds",
                "the scenario does not build one witness ciphertext per case, "
                "designated at first write and held outside the enumerable "
                "delete path. Without it check 1 has nothing to try the key "
                "against after the shred",
                "restore the witness object with RT-9's three properties",
            )
        )

    order = [str(step).lower() for step in as_list(dig(fx, "receipt_step.order"))]
    if (
        len(order) < 3
        or "shred" not in order[0]
        or "verify" not in order[1]
        or "ledger row" not in order[-1]
    ):
        out.append(
            Finding(
                "SHRED_ROUNDTRIP_RECEIPT_ORDER",
                f"{FIXTURE_REL} :: shred_roundtrip.receipt_step.order",
                "the receipt order does not run shred, then verification, then "
                "the ledger row. A row appended before verification records a "
                "shred that has not been proven, and RT-10 says a shred with no "
                "receipt row did not happen",
                "restore the three ordered steps, with the ledger row appended "
                "only after all five checks pass",
            )
        )

    # The check that keeps this mode from reading as more than it is.
    boundary = fx.get("step_boundary") or {}
    if not boundary.get("what_this_file_is_not") or not boundary.get(
        "vacuous_pass_named"
    ):
        out.append(
            Finding(
                "SHRED_ROUNDTRIP_VACUOUS_PASS",
                f"{FIXTURE_REL} :: shred_roundtrip.step_boundary",
                "the fixture does not state what it is not and does not name "
                "the vacuous pass it could be mistaken for. A document "
                "describing a check nobody has run is not the check having run, "
                "and a green result here would otherwise read as a shred having "
                "been verified",
                "state what this file is not, and name the vacuous pass in "
                "place rather than leaving a reader to infer it",
            )
        )

    unratified = fx.get("unratified") or {}
    policy_ids = {
        str(entry.get("id")): entry
        for entry in as_list(dig(ctx["policy"], "retention.unratified.entries"))
        if isinstance(entry, dict)
    }
    out.extend(
        _check_placeholders(
            fx,
            as_list(unratified.get("local_entries")),
            FIXTURE_REL,
            "SR-U",
            policy_ids,
        )
    )
    for tracked in as_list(unratified.get("tracked_from_policy_retention")):
        if not isinstance(tracked, dict):
            continue
        tid = str(tracked.get("id"))
        if tid not in policy_ids:
            out.append(
                Finding(
                    "SHRED_ROUNDTRIP_PLACEHOLDER_UNDECLARED",
                    f"{FIXTURE_REL} :: shred_roundtrip.unratified.{tid}",
                    f"the fixture tracks {tid} from policy/retention.yaml and "
                    "that file declares no such entry, so the fixture defers to "
                    "a question no artifact carries",
                    f"correct the id, declare {tid} in policy/retention.yaml, "
                    "or drop the reference",
                )
            )

    if not stamped_path(ctx["status"], FIXTURE_REL):
        out.append(
            Finding(
                "SHRED_ROUNDTRIP_UNRATIFIED",
                "doctrine/DOCTRINE_STATUS.md",
                "NO CASE MAY OPEN AND NO SHRED MAY BE CLAIMED AS VERIFIED. The "
                "pin of record carries no dated row for "
                "conformance/retention/shred-roundtrip.yaml. SS-14 item 6 "
                "blocks all collection until every artifact it names is "
                "stamped, and an unratified criterion refuses rather than "
                "permits",
                "stamp conformance/retention/shred-roundtrip.yaml in "
                "doctrine/DOCTRINE_STATUS.md with a date and a ratifier, which "
                "clears this refusal with no change to this tool; or collect "
                "nothing, which is the state this refusal describes",
            )
        )
    return out


# ---------------------------------------------------------------------------
# --repo-scan
# ---------------------------------------------------------------------------


def _form_segments(registry: dict, selector: str) -> tuple[str, ...] | None:
    """The placeholder names in a selector's rank-3 form, in order."""
    spec = (registry.get("selectors") or {}).get(selector)
    if not isinstance(spec, dict) or not isinstance(spec.get("form"), str):
        return None
    form = spec["form"]
    prefix = f"{selector}:"
    if not form.startswith(prefix):
        return None
    return tuple(PLACEHOLDER_RE.findall(form[len(prefix):]))


def check_scan_shapes(ctx: dict) -> list[Finding]:
    """R-11. The shape table is a compilation of rank 3, in both directions."""
    out: list[Finding] = []
    registry = ctx["registry"]
    detectable = [str(t) for t in as_list(registry["repo_scan"].get("shape_detectable"))]
    for selector in detectable:
        if selector not in TYPE_SEGMENTS:
            out.append(
                Finding(
                    "RETENTION_REPO_SCAN_SHAPES_INCOMPLETE",
                    "tools/validate_retention.py :: TYPE_SEGMENTS",
                    f"the registry calls {selector} shape detectable and this "
                    "tool carries no shape for it, so the scan reports a clean "
                    "run over a type it never looked for",
                    f"add {selector} to TYPE_SEGMENTS with the segment names "
                    "its form declares, or move the type out of "
                    "shape_detectable in ontology/selectors.yaml",
                )
            )
            continue
        segments = _form_segments(registry, selector)
        if segments is None:
            out.append(
                Finding(
                    "RETENTION_REPO_SCAN_SHAPES_DRIFT",
                    f"ontology/selectors.yaml :: selectors.{selector}.form",
                    "the selector declares no form opening with its own type "
                    "token, so the scan cannot compile a typed pattern for it",
                    "restore the form as the type, a colon, and its "
                    "placeholders",
                )
            )
            continue
        if tuple(TYPE_SEGMENTS[selector]) != segments:
            out.append(
                Finding(
                    "RETENTION_REPO_SCAN_SHAPES_DRIFT",
                    f"tools/validate_retention.py :: TYPE_SEGMENTS.{selector}",
                    f"this tool compiles {list(TYPE_SEGMENTS[selector])} and the "
                    f"rank-3 form declares {list(segments)}. A scan built on a "
                    "stale form matches a shape the registry no longer uses, "
                    "which is a gate that fires on nothing and says nothing",
                    "move TYPE_SEGMENTS to the form, or correct the form",
                )
            )
    for selector in TYPE_SEGMENTS:
        if selector not in detectable:
            out.append(
                Finding(
                    "RETENTION_REPO_SCAN_SHAPES_DRIFT",
                    f"tools/validate_retention.py :: TYPE_SEGMENTS.{selector}",
                    "this tool scans for a type the registry does not call "
                    "shape detectable, so a refusal here rests on a claim rank "
                    "3 does not make",
                    "remove the entry, or add the type to shape_detectable in "
                    "ontology/selectors.yaml",
                )
            )
    for exemption in as_list(registry["repo_scan"].get("document_exemptions")):
        if not isinstance(exemption, dict):
            continue
        path = str(exemption.get("path") or "")
        if path and not (ROOT / path).is_file():
            out.append(
                Finding(
                    "RETENTION_EXEMPTION_DANGLING",
                    "ontology/selectors.yaml :: repo_scan.document_exemptions",
                    f"the registry exempts {path} and no such file exists, so a "
                    "named, reviewable gap has become a line nobody can review",
                    "correct the path, or remove the exemption",
                )
            )
    return out


def compile_patterns(registry: dict) -> dict[str, re.Pattern]:
    """Build one typed pattern per shape-detectable selector, from its form."""
    out: dict[str, re.Pattern] = {}
    for selector in as_list(registry["repo_scan"].get("shape_detectable")):
        selector = str(selector)
        segments = _form_segments(registry, selector)
        if segments is None or selector not in TYPE_SEGMENTS:
            continue
        if tuple(TYPE_SEGMENTS[selector]) != segments:
            continue
        spec = registry["selectors"][selector]["form"]
        remainder = spec[len(selector) + 1:]
        parts = PLACEHOLDER_RE.split(remainder)
        body = ""
        for index, chunk in enumerate(parts):
            if index % 2:
                body += "(?:" + SEGMENT_SHAPES[chunk] + ")"
            else:
                body += re.escape(chunk)
        out[selector] = re.compile(
            r"(?<![A-Za-z0-9_])" + re.escape(selector) + ":" + body + r"(?![A-Za-z0-9_])"
        )
    return out


def synthetic_allowlist(registry: dict) -> tuple[set[str], str]:
    """The allowlist, and the state of the cast rendered as its consequence.

    There is never an allowlist of live values. The only allowlist is the
    synthetic one and it is read from a sealed cast, so an unsealed cast
    produces an empty set and the scan runs on shape alone.
    """
    before = "the cast is unsealed, so the scan runs on shape alone and builds no synthetic allowlist"
    if yaml is None or not TRUTH.is_file():
        return set(), before
    try:
        truth = yaml.safe_load(TRUTH.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return set(), before
    seal = truth.get("seal") or {}
    if seal.get("sealed") is not True:
        return set(), before
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import validate_cast

        digest, count = validate_cast.canonical_digest(TRUTH.read_text(encoding="utf-8"))
    except Exception:
        digest, count = "", 0
    if count != 1 or digest != seal.get("sha256"):
        return (
            set(),
            "THE SYNTHETIC ALLOWLIST WAS NOT BUILT. The cast declares itself "
            "sealed and its recorded digest does not verify, so it authorizes "
            "nothing and the scan runs on shape alone",
        )
    values: set[str] = set()

    def walk(node):
        if isinstance(node, dict):
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)
        elif isinstance(node, str) and not node.startswith("<"):
            values.add(node)

    walk(truth.get("personas"))
    walk(truth.get("truth"))
    return values, (
        f"the cast is sealed and its digest verifies, so {len(values)} synthetic "
        "values are permitted and anything else is a finding"
    )


#: The key pairs that write a selector as a type beside a value: the CLAIM
#: payloads, the subject-authorization records and the gate fixtures' dispatch.
PAIR_KEYS = (("selector_type", "value"), ("target_selector_type", "target_selector"))


def _mappings(node, seen: set | None = None):
    # Each node once: a YAML anchor can refer to itself, which recursed without
    # end until 2026-10-01.
    seen = set() if seen is None else seen
    if id(node) in seen:
        return
    if isinstance(node, (dict, list)):
        seen.add(id(node))
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _mappings(value, seen)
    elif isinstance(node, list):
        for value in node:
            yield from _mappings(value, seen)


class _Repeated(list):
    """Every value a key was given in one mapping, where the key was repeated.

    A parser keeps the last value of a repeated key, so until the second review
    of 2026-10-01 a live value followed by a placeholder under the same key was
    read as the placeholder alone.
    """


def _keep_repeats(pairs, mapping: dict | None = None):
    mapping = {} if mapping is None else mapping
    for key, value in pairs:
        try:
            hash(key)
        except TypeError:
            # A complex YAML key, which crashed the scan until 2026-10-01.
            key = repr(key)
        if key in mapping:
            held = mapping[key]
            mapping[key] = held + [value] if isinstance(held, _Repeated) else _Repeated([held, value])
        else:
            mapping[key] = value
    return mapping


if yaml is not None:

    class _ScanLoader(yaml.BaseLoader):
        """Every scalar a string, every repeated key kept. An unquoted E.164 number
        was an int under safe_load and was dropped until 2026-10-01."""

    def _flatten_merge(node, seen=None):
        # "<<" merges flattened at node level, as SafeConstructor does, so an
        # inherited selector_type pairs with its value.
        seen = set() if seen is None else seen
        if id(node) in seen:
            return []
        seen.add(id(node))
        pairs, merged = [], []
        for k, v in node.value:
            if isinstance(k, yaml.ScalarNode) and k.value == "<<":
                for source in (v.value if isinstance(v, yaml.SequenceNode) else [v]):
                    if isinstance(source, yaml.MappingNode):
                        merged.extend(_flatten_merge(source, seen))
            else:
                pairs.append((k, v))
        explicit = {k.value for k, _ in pairs if isinstance(k, yaml.ScalarNode)}
        return pairs + [(k, v) for k, v in merged if not (isinstance(k, yaml.ScalarNode) and k.value in explicit)]

    def _construct_scan_mapping(loader, node, deep=False):
        # A generator that yields its mapping before filling it, with children
        # built lazily, so an anchor that refers to itself constructs. Until the
        # third review of 2026-10-01 both a self-referential anchor and a "<<"
        # merge made the whole file read as nothing.
        mapping: dict = {}
        yield mapping
        _keep_repeats(
            ((loader.construct_object(k), loader.construct_object(v)) for k, v in _flatten_merge(node)),
            mapping,
        )

    def _construct_any(loader, suffix, node):
        # Any tag: a tagged mapping keeps its repeats like an untagged one.
        if isinstance(node, yaml.MappingNode):
            return _construct_scan_mapping(loader, node)
        if isinstance(node, yaml.SequenceNode):
            return loader.construct_sequence(node)
        return loader.construct_scalar(node)

    _ScanLoader.add_constructor("tag:yaml.org,2002:map", _construct_scan_mapping)
    _ScanLoader.add_multi_constructor("", _construct_any)


def _strings(value, seen: set | None = None) -> list[str]:
    """The strings a value carries, at any depth of lists, each list once."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        seen = set() if seen is None else seen
        if id(value) in seen:
            return []
        seen.add(id(value))
        return [s for v in value for s in _strings(v, seen)]
    return []


def _pairs_in(node, types: set[str]):
    """(type, value) for every pair in one parsed document, within one mapping.

    Pairing within a mapping rather than within a line matters: a gate fixture's
    line also carries expect_decision.value, and pairing that with a
    selector_type elsewhere on the line would refuse an ordinary word. Keys are
    read in any case, and a list or a repeated key yields every string it holds.
    """
    for mapping in _mappings(node):
        folded = _keep_repeats((str(k).lower(), v) for k, v in mapping.items())
        for type_key, value_key in PAIR_KEYS:
            for selector in _strings(folded.get(type_key)):
                for value in _strings(folded.get(value_key)):
                    yield selector.lower(), value
        for key, value in folded.items():
            if key in types:
                for item in _strings(value):
                    yield key, item


def selector_pairs(rel: str, text: str, types: set[str]) -> list[tuple[int, str, str]]:
    """(line, type, value) for each selector written as a pair, never quoted out.

    A JSON line is parsed on its own line; a .json file and a .yaml file are
    parsed whole and a pair is placed on the first line carrying its value. A
    file that does not parse yields nothing here, which SCAN_DOES_NOT_REACH says.
    """
    out: list[tuple[int, str, str]] = []
    text = text.lstrip("﻿")
    lines = text.splitlines()
    suffix = Path(rel).suffix.lower()
    if suffix in (".yaml", ".yml") or suffix == ".json":
        try:
            if suffix == ".json":
                docs = [json.loads(text, object_pairs_hook=_keep_repeats)]
            elif yaml is not None:
                try:
                    docs = list(yaml.load_all(text, Loader=_ScanLoader))
                except (TypeError, RecursionError, yaml.YAMLError):
                    docs = list(yaml.safe_load_all(text))
            else:
                docs = []
        except (ValueError, TypeError, RecursionError, yaml.YAMLError if yaml is not None else ValueError):
            docs = None
        if docs is not None:
            for doc in docs:
                for selector, value in _pairs_in(doc, types):
                    number = next((n for n, line in enumerate(lines, 1) if value in line), 1)
                    out.append((number, selector, value))
            return out
        if suffix != ".json":
            return out
        # A .json file that does not parse whole is read line by line, as JSON
        # lines; until 2026-10-01 such a file yielded nothing.
    for number, line in enumerate(lines, 1):
        stripped = line.strip().lstrip("﻿").rstrip(",")
        if not stripped.startswith(("{", "[")):
            continue
        try:
            doc = json.loads(stripped, object_pairs_hook=_keep_repeats)
        except (ValueError, RecursionError):
            continue
        out.extend((number, selector, value) for selector, value in _pairs_in(doc, types))
    return out


def scan_text(
    rel: str,
    text: str,
    patterns: dict[str, re.Pattern],
    exemptions: dict[str, set[str]],
    allowlist: set[str],
    code: str,
) -> list[Finding]:
    """Scan one file's content. The finding never carries what matched.

    RT-19 and HY-1: a record names the file and the line and never the string.
    The refusal below is written the same way, because a refusal quoting the
    match would put the value into a terminal, a CI log and an issue thread,
    which are three more durable surfaces than the one it was guarding.
    """
    out: list[Finding] = []
    exempt = exemptions.get(rel, set())
    for number, line in enumerate(text.splitlines(), 1):
        for selector, pattern in patterns.items():
            if selector in exempt:
                continue
            # Every match on the line, not the first. Until 2026-10-01 a first
            # match on the allowlist hid a second, live one after it.
            if all(m.group(0) in allowlist for m in pattern.finditer(line)):
                continue
            out.append(
                Finding(
                    code,
                    f"{rel}:{number}",
                    f"the line carries a filled {selector} selector. Git history "
                    "is append-only, distributed to every clone, and survives "
                    "git rm, so a selector committed here is outside every "
                    "mechanism doctrine/RETENTION.md describes and no later act "
                    "reaches it. This refusal does not quote what matched, per "
                    "RT-19",
                    "replace the value with a placeholder in the registry's "
                    "form, replace it with a synthetic value once the cast is "
                    "sealed, or add the file to repo_scan.document_exemptions "
                    "in ontology/selectors.yaml with the selector types it "
                    "covers and the reason",
                )
            )
            break
    # The pair form. Until 2026-10-01 only the typed string was matched, while
    # the corpora, the records and every CLAIM payload write a selector as a
    # selector_type beside a value, so a live record in that shape carried its
    # type and was not found.
    reported = {f.where for f in out}
    for number, selector, value in selector_pairs(rel, text, set(patterns)):
        where = f"{rel}:{number}"
        if selector in exempt or selector not in patterns or where in reported:
            continue
        typed = f"{selector}:{value}"
        match = patterns[selector].search(typed)
        if not match or match.group(0) != typed or typed in allowlist:
            continue
        reported.add(where)
        out.append(
            Finding(
                code,
                where,
                f"the file carries a filled {selector} selector written as a type "
                "beside a value. Git history is append-only, distributed to every "
                "clone, and survives git rm, so a selector committed here is "
                "outside every mechanism doctrine/RETENTION.md describes. This "
                "refusal does not quote what matched, per RT-19",
                "replace the value with a placeholder in the registry's form, such "
                "as <addr> for an email, replace it with a synthetic value once the "
                "cast is sealed, or add the file to repo_scan.document_exemptions "
                "in ontology/selectors.yaml with the selector types it covers and "
                "the reason",
            )
        )
    return out


def _git(args: list[str]) -> str:
    proc = subprocess.run(
        ["git"] + args,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        raise Unreadable(
            "RETENTION_REPO_SCAN_SOURCE_UNREADABLE",
            "git",
            f"git {' '.join(args)} failed, so the scan has no file set and did "
            "not check anything",
            "run the scan inside a git working tree, or move the "
            "retention-repo-scan gate to PENDING in "
            "tools/validate_conformance.py",
        )
    return proc.stdout


_BOMS = (
    (b"\x00\x00\xfe\xff", "utf-32-be"),
    (b"\xff\xfe\x00\x00", "utf-32-le"),
    (b"\xfe\xff", "utf-16-be"),
    (b"\xff\xfe", "utf-16-le"),
)


def decode_for_scan(name: str, data: bytes) -> str:
    """Bytes to text the typed shapes can match, or a refusal.

    A file carrying a UTF-16 or UTF-32 byte-order mark is decoded with that
    codec. A file with NUL bytes and no mark is binary or BOM-less UTF-16, and
    replacement decoding would turn it into text no shape matches while it was
    still counted as read, so it refuses. Anything else is decoded as UTF-8 with
    replacement: the typed shapes are ASCII, and ASCII bytes read the same in
    every ASCII-compatible encoding. Until the completeness critic of 2026-10-01
    a UTF-16 file was counted as read and clean.
    """
    for bom, codec in _BOMS:
        if data.startswith(bom):
            try:
                return data[len(bom):].decode(codec)
            except UnicodeDecodeError:
                break
    if b"\x00" in data:
        raise Unreadable(
            "RETENTION_REPO_SCAN_SOURCE_UNREADABLE",
            name,
            "the file is not text this scan can read: it carries NUL bytes, as a "
            "binary file or UTF-16 without a byte-order mark does, so a selector in "
            "it would not be found and the file would be counted as read",
            "re-save it as UTF-8; or remove or unstage it; or keep binary files out "
            "of the tracked tree",
        )
    # A UTF-8 byte-order mark is dropped here, so the pair reader parses the
    # file; until 2026-10-01 a .json file PowerShell wrote was read as nothing.
    return data.decode("utf-8", errors="replace").lstrip("﻿")


def scan_paths(staged: bool) -> list[tuple[str, str]]:
    """The file set, and its content. Reading VR-U2 bounds what this covers.

    Until 2026-10-01 both modes could skip a file and still report ok. git
    quotes a path with a non-ASCII character unless asked for NUL-separated
    output, so the quoted name opened nothing and was dropped; and the working
    tree mode dropped any file that was not valid UTF-8. Names are now read
    NUL-separated, every file is decoded with replacement so a selector in its
    ASCII typed form is still found, and a staged file git cannot show refuses
    rather than vanishing. A tracked file missing from the working tree has no
    content to scan in that mode and is still passed over.
    """
    out: list[tuple[str, str]] = []
    if staged:
        names = [
            n
            for n in _git(
                ["diff", "--cached", "--name-only", "-z", "--diff-filter=ACMR"]
            ).split("\0")
            if n.strip()
        ]
        for name in names:
            proc = subprocess.run(
                ["git", "show", f":{name}"],
                cwd=ROOT,
                capture_output=True,
            )
            if proc.returncode != 0:
                raise Unreadable(
                    "RETENTION_REPO_SCAN_SOURCE_UNREADABLE",
                    name,
                    "git could not show this staged file, so the scan cannot read "
                    "what the commit would carry and has not checked it",
                    "restage the file and commit again; or unstage it",
                )
            out.append((name, decode_for_scan(name, proc.stdout)))
        return out
    for name in _git(["ls-files", "-z"]).split("\0"):
        if not name.strip():
            continue
        path = ROOT / name
        try:
            out.append((name, decode_for_scan(name, path.read_bytes())))
        except OSError:
            continue
    return out


def check_repo_scan(ctx: dict, staged: bool) -> tuple[list[Finding], dict]:
    registry = ctx["registry"]
    findings = check_scan_shapes(ctx)
    patterns = compile_patterns(registry)
    exemptions = {
        str(e.get("path")): {str(t) for t in as_list(e.get("selector_types"))}
        for e in as_list(registry["repo_scan"].get("document_exemptions"))
        if isinstance(e, dict)
    }
    allowlist, cast_state = synthetic_allowlist(registry)
    code = scan_code(ctx["codes"])
    files = scan_paths(staged)
    pairs = 0
    for rel, text in files:
        findings.extend(scan_text(rel, text, patterns, exemptions, allowlist, code))
        pairs += sum(1 for _, t, _ in selector_pairs(rel, text, set(patterns)) if t in patterns)
    return findings, {
        "files": len(files),
        "types": len(patterns),
        "pairs": pairs,
        "cast_state": cast_state,
        "code": code,
        "staged": staged,
    }


def _read_for_measure(path: Path) -> str:
    """A file's text for a measurement, or "" when it cannot be read.

    A crash must never stand in for a measurement, and an unreadable file
    measures as absent. Until 2026-10-01 a manifests/ directory or a non-UTF-8
    AGENTS.md ended --policy, --repo-scan and the hook in a traceback.
    """
    try:
        return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""
    except OSError:
        return ""


#: Words that withdraw the clause when they follow it in its own bullet.
CLAUSE_WITHDRAWN = re.compile(r"no longer applies|does not apply|is withdrawn|was removed|is suspended", re.I)


def _clause_in_place(agents: str) -> bool:
    """RT-15's first part: the Execution Limits bullet, rendered and unwithdrawn.

    Until the third review of 2026-10-01 any heading containing "## 4." matched,
    an HTML comment counted, and a following "This rule no longer applies" left
    it in place.
    """
    text = re.sub(r"<!--.*?-->", " ", agents, flags=re.S)
    text = re.sub(r"(?ms)^```.*?^```", " ", text)
    heading = re.search(r"(?m)^## 4\. Execution Limits[ \t]*$", text)
    if not heading:
        return False
    rest = text[heading.end():]
    end = re.search(r"(?m)^## ", rest)
    section = rest[: end.start()] if end else rest
    for bullet in re.split(r"(?m)^- ", section):
        flat = " ".join(bullet.split())
        if flat.startswith("**" + RT15_CLAUSE_SENTENCE + "**"):
            return not CLAUSE_WITHDRAWN.search(flat)
    return False


#: The hook's scan stanza, by shape: the command at the start of a line, its
#: failure block, and that block's refusal.
SCAN_STANZA = "python tools/validate_retention.py --repo-scan --staged || {"


def _scan_stanza_in_place(hook: str) -> bool:
    """RT-15's fourth part: the hook runs the scan and refuses when it refuses.

    Until the third review of 2026-10-01 a line-level test passed a block that
    ended in exit 0, a no-op ":", a trailing --help and an exit 0 before it.
    """
    lines = hook.splitlines()
    starts = [i for i, line in enumerate(lines) if line.strip() == SCAN_STANZA and not line.startswith(" ")]
    if len(starts) != 1:
        return False
    start = starts[0]
    if any(re.match(r"\s*exit\s+0\b", line) for line in lines[:start]):
        return False
    block = []
    for line in lines[start + 1:]:
        if line.strip() == "}":
            break
        block.append(line.strip())
    else:
        return False
    return "exit 1" in block and not any(re.match(r"exit\s+0\b", line) for line in block)


def rt15_parts(codes: set[str], root: Path | None = None) -> list[tuple[str, bool]]:
    """RT-15's four enforcement parts, each measured rather than asserted.

    Until 2026-10-01 every run printed that RT-15 was enforced in three of its
    four parts, counting git history as the fourth. RT-15 lists four parts and
    git history is not one of them; two were in place. Until the second review
    of 2026-10-01 the clause, the field and the hook were substring tests a
    comment satisfied, so a deleted section 4 still measured as in place.
    """
    base = ROOT if root is None else root
    clause = _clause_in_place(_read_for_measure(base / "AGENTS.md"))
    manifests = []
    connectors = base / "connectors"
    try:
        if connectors.is_dir():
            manifests = [m for m in connectors.glob("*/manifest*") if m.is_file()]
    except OSError:
        manifests = []
    declared = bool(manifests)
    for m in manifests:
        try:
            doc = yaml.safe_load(_read_for_measure(m)) if yaml is not None else None
        except yaml.YAMLError:
            doc = None
        if not (isinstance(doc, dict) and doc.get("canary_subject_class") in ("synthetic", "institutional")):
            declared = False
    hook = _read_for_measure(base / ".githooks" / "pre-commit")
    return [
        ("the Execution Limits clause in AGENTS.md", clause),
        ("canary_subject_class required on connector manifests",
         declared and MANIFEST_VALIDATOR_REQUIRES_CANARY),
        (f"the violation code {DOCTRINE_SCAN_CODE} in policy/violation-codes.yaml",
         DOCTRINE_SCAN_CODE in codes),
        ("this scan wired into .githooks/pre-commit",
         _scan_stanza_in_place(hook)),
    ]


def rt15_table_findings(pol: dict, codes: set[str]) -> list[Finding]:
    """RT-15's table, keyed by clause: four parts, each once, each as measured."""
    where = f"{POLICY_REL} :: retention.repo_scan.enforcement_parts_all_required"
    entries = [e for e in as_list(dig(pol, "repo_scan.enforcement_parts_all_required")) if isinstance(e, dict)]
    clauses = [e.get("clause") for e in entries]
    if sorted(map(str, clauses)) != sorted(RT15_PART_CLAUSES):
        return [
            Finding(
                "RETENTION_POLICY_ENFORCEMENT_MISSTATED",
                where,
                f"the table lists {len(entries)} part(s), {clauses}, where RT-15 has four, "
                "each once. A missing, extra or renamed part makes the table say something "
                "about an enforcement RT-15 does not name",
                "restore the four clauses as RT15_PART_CLAUSES in this tool names them; or "
                "ratify an RT-15 amendment and move RT15_PART_CLAUSES in the same commit",
            )
        ]
    out: list[Finding] = []
    measured = dict(zip(RT15_PART_CLAUSES, (present for _, present in rt15_parts(codes))))
    for entry in entries:
        claim, present = entry.get("present"), measured[entry["clause"]]
        if isinstance(claim, bool) and claim is not present:
            out.append(
                Finding(
                    "RETENTION_POLICY_ENFORCEMENT_MISSTATED",
                    where,
                    f"the policy says {entry['clause']} is {'in place' if claim else 'absent'} "
                    f"and the tree shows it {'in place' if present else 'absent'}. RT-15 "
                    "requires all four parts, so a part claimed and not present is an "
                    "enforcement nobody gets",
                    "correct the present flag to what the tree shows; or put the part in "
                    "place and change the flag in the same commit",
                )
            )
    return out


def rt16_table_findings(pol: dict) -> list[Finding]:
    """RT-16's three entries, keyed by what each is, each with its pinned state."""
    where = f"{POLICY_REL} :: retention.connector_floor.enforcement"
    entries = [e for e in as_list(dig(pol, "connector_floor.enforcement")) if isinstance(e, dict)]
    problems = []
    if len(entries) != len(RT16_ENFORCEMENT):
        problems.append(f"{len(entries)} entries where RT-16 names {len(RT16_ENFORCEMENT)}")
    for (key, text, present), entry in zip(RT16_ENFORCEMENT, entries):
        if present is None and not _same(entry, {key: text}):
            problems.append(f"the {key} entry carries {sorted(entry)} where RT-16's is exactly {{{key}: {text!r}}}")
        elif not _same(entry.get(key), text):
            problems.append(f"an entry reads {key}: {entry.get(key)!r} where RT-16's is {text!r}")
        elif present is not None and isinstance(entry.get("present"), bool) and entry.get("present") is not present:
            problems.append(
                f"{text} is stated {'in place' if entry.get('present') else 'absent'} "
                f"and this tool {'carries it' if present else 'does not carry it'}"
            )
    if not problems:
        return []
    return [
        Finding(
            "RETENTION_POLICY_ENFORCEMENT_MISSTATED",
            where,
            "RT-16's enforcement entries do not say what exists: " + "; ".join(problems)
            + ". RT-16 names the clause, the check and a code so that it is not a rule "
            "that states itself and stops",
            "restore the three entries as RT16_ENFORCEMENT in this tool names them; or "
            "write the clause or the reconcile and set its flag in the same commit",
        )
    ]


def scan_notices(report: dict, codes: set[str]) -> str:
    """The states this mode renders rather than refuses."""
    lines = [f"validate_retention --repo-scan: {report['cast_state']}."]
    parts = rt15_parts(codes)
    missing = [name for name, present in parts if not present]
    lines.append(
        f"  RT-15's enforcement is in place in {len(parts) - len(missing)} of its "
        f"{len(parts)} parts"
        + (f"; not yet: {'; '.join(missing)}." if missing else ".")
    )
    if report["code"] != DOCTRINE_SCAN_CODE:
        lines.append(
            "  The violation code "
            f"{DOCTRINE_SCAN_CODE} is required in\n"
            "  policy/violation-codes.yaml and that file declares "
            f"{len(codes)} codes without it, so a refusal from this scan "
            "carries\n"
            f"  the tool-local code {LOCAL_SCAN_CODE} and cannot be graded "
            "against the wire vocabulary.\n"
            "  moves: declare the code in spec/layer-model.yaml and run "
            "tools/generate_pse.py; or ratify VR-U3's\n"
            "         second option, which records that doctrine's code names "
            "the event-level case alone."
        )
    lines.append("  this scan did not reach:")
    for item in SCAN_DOES_NOT_REACH:
        lines.append(f"    - {item}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# --finding
# ---------------------------------------------------------------------------


def check_finding(path: str, case: str) -> int:
    """RT-13, refusing. VR-U4 carries the question this mode cannot answer."""
    candidate = Path(path)
    if not candidate.is_file():
        refuse(
            "RETENTION_FINDING_FILE_UNREADABLE",
            path,
            "the candidate writeup does not exist, so nothing was scanned and "
            "the case may not close",
            "pass the path of the writeup, or do not close the case",
        )
        return 2
    refuse(
        "RETENTION_FINDING_NO_CASE_STORE",
        f"case {case}",
        "THE FINDING CHECK DID NOT RUN AND THIS WRITEUP IS NOT CLEARED FOR "
        "PUBLICATION. RT-13 scans a candidate writeup against the case's "
        "selector set at case close, before the shred, while the values still "
        "exist. There is no case store to read that set from: runner/ is empty "
        "until Step 10, the store lands at Step 11, and EG-2 puts it in "
        "ISOLATED where this tool is not running. A pass here would be the "
        "finding check reporting that it had run when it had not",
        "run this mode in ISOLATED once the case store exists, which is Step "
        "11; or hold the writeup, which is the state this refusal describes; "
        "the rejected alternative of retaining a digest of the selector set is "
        "a membership oracle and RETENTION.md RT-13 refuses it by name",
    )
    return 2


# ---------------------------------------------------------------------------
# --self-test
# ---------------------------------------------------------------------------

#: Codes this gate is expected to fire against the tree as it stands, because
#: both graded artifacts are unratified by design. The baseline guard refuses on
#: anything outside this set, and each mutation is judged against the baseline
#: rather than against silence, so a mutation that fires only these has not been
#: refused. Stamping the two artifacts empties the computed baseline, not this
#: tuple, and the two unstamping cases below observe each refusal fire whether
#: or not the live pin is stamped.
EXPECTED_BASELINE = ("RETENTION_POLICY_UNRATIFIED", "SHRED_ROUNDTRIP_UNRATIFIED")


def _sample(rel: str, filled: bool) -> tuple[str, str]:
    """A one-line file for the scan to look at.

    The selector token is assembled at run time rather than written as a
    literal, because this file is tracked and a literal here would be exactly
    the object the scan refuses. A tool that carries the shape it guards against
    is the first thing its own gate should find.
    """
    token = "handle" + ":" + "acmegram" + "/"
    return rel, "note: " + token + ("examplename" if filled else "<string>")


def _pair_line(ctx) -> tuple[str, str]:
    """A selector written as a type beside a value, on a JSON line."""
    value = "examplename" + "@" + "example" + ".org"
    return "conformance/x.jsonl", json.dumps({"selector_type": "email", "value": value, "expect": {"value": "PERMITTED"}})


def _pair_yaml(ctx) -> tuple[str, str]:
    """The same pair in a YAML file, across two lines."""
    value = "examplename" + "@" + "example" + ".org"
    return "policy/x.yaml", "selectors:\n  - selector_type: email\n    value: " + value + "\n"


def _pair_placeholder(ctx) -> tuple[str, str]:
    """The pair with a placeholder value, and an ordinary word paired elsewhere."""
    return "conformance/x.jsonl", json.dumps(
        {"selector_type": "username_string", "value": "<string>", "expect_decision": {"value": "PERMITTED"}}
    )


def _email_value() -> str:
    return "examplename" + "@" + "example" + ".org"


def _pair_unquoted_phone(ctx) -> tuple[str, str]:
    """A phone written by hand in YAML, which a safe loader reads as a number."""
    return "policy/x.yaml", "selectors:\n  - selector_type: phone\n    value: " + "+1" + "5550100" + "999" + "\n"


def _pair_repeated_value(ctx) -> tuple[str, str]:
    """A live value hidden behind a placeholder under the same key."""
    return "conformance/x.jsonl", '{"selector_type": "email", "value": "' + _email_value() + '", "value": "<addr>"}'


def _pair_json_with_bom(ctx) -> tuple[str, str]:
    """A .json file opening with a byte-order mark, as PowerShell 5.1 writes it."""
    return "conformance/x.json", "﻿" + json.dumps({"selector_type": "email", "value": _email_value()})


def _pair_value_in_a_list(ctx) -> tuple[str, str]:
    return "conformance/x.jsonl", json.dumps({"selector_type": "email", "value": [_email_value()]})


def _pair_json_holding_lines(ctx) -> tuple[str, str]:
    one = json.dumps({"selector_type": "email", "value": _email_value()})
    return "conformance/x.json", one + "\n" + one + "\n"


def _pair_keys_in_capitals(ctx) -> tuple[str, str]:
    return "conformance/x.jsonl", json.dumps({"Selector_Type": "email", "Value": _email_value()})


def _pair_by_merge_key(ctx) -> tuple[str, str]:
    """A selector_type inherited through a YAML merge key."""
    return "policy/x.yaml", "base: &b\n  selector_type: email\nentry:\n  <<: *b\n  value: " + _email_value() + "\n"


def _pair_in_a_tagged_mapping(ctx) -> tuple[str, str]:
    """A live value behind a placeholder in a mapping with a custom tag."""
    return "policy/x.yaml", "entry: !thing\n  selector_type: email\n  value: " + _email_value() + "\n  value: <addr>\n"


def _pair_by_case_variant(ctx) -> tuple[str, str]:
    """A live value under Value hidden by a placeholder under value."""
    return "conformance/x.jsonl", '{"selector_type": "email", "Value": "' + _email_value() + '", "value": "<addr>"}'


def _pair_list_then_repeat(ctx) -> tuple[str, str]:
    """A live value in a list, then the key repeated with a placeholder."""
    return "policy/x.yaml", "entry:\n  selector_type: email\n  value: [" + _email_value() + "]\n  value: <addr>\n"


def _complex_key(ctx) -> tuple[str, str]:
    """A YAML mapping key that is a sequence, which crashed the scan."""
    return "policy/x.yaml", "? [a, b]\n: c\n"


def _upper_domain(ctx) -> tuple[str, str]:
    """A typed domain in capitals."""
    return "notes/x.md", "note: " + "domain" + ":" + "EXAMPLE" + ".ORG"


def _two_on_a_line(ctx) -> tuple[str, str]:
    """An allowlisted selector followed by a live one on the same line."""
    token = "handle" + ":" + "acmegram" + "/"
    ctx["_allowlisted"] = {token + "examplename"}
    return "notes/x.md", "note: " + token + "examplename and " + token + "othername"


def _mutations():
    """(description, which check, mutator, expected code, expect_only).

    `which` selects the harness: policy and roundtrip mutate the loaded
    artifacts, shapes mutates the registry or this tool's table, and scan builds
    a one-line sample. An expected code written with a leading minus asserts the
    opposite direction, that the named code stops firing, which is how the
    ratification check proves it permits once the stamp lands rather than only
    that it refuses while the stamp is absent.
    """

    def drop_a_stratum_row(ctx):
        ctx["policy"]["retention"]["strata"]["rows"].pop()

    def subject_value_survives(ctx):
        for row in ctx["policy"]["retention"]["strata"]["rows"]:
            if row.get("stratum") == 2:
                row["carries_subject_values"] = True

    def widen_surviving(ctx):
        ctx["policy"]["retention"]["strata"]["surviving"] = [2, 3, 4]

    def move_raw_capture_outside(ctx):
        for row in ctx["policy"]["retention"]["strata"]["rows"]:
            if row.get("stratum") == 0:
                row["inside_shred_boundary"] = False

    def swap_authorization_for_a_second_skeleton(ctx):
        rows = ctx["policy"]["retention"]["strata"]["rows"]
        skeleton = next(r for r in rows if r.get("name") == "skeleton")
        idx = next(i for i, r in enumerate(rows) if r.get("name") == "authorization")
        rows[idx] = dict(skeleton)

    def let_telemetry_live_forever(ctx):
        for row in ctx["policy"]["retention"]["strata"]["rows"]:
            if row.get("name") == "gate_telemetry":
                row["lifetime"] = "permanent"

    def give_the_corpus_a_subject_value(ctx):
        for row in ctx["policy"]["retention"]["strata"]["rows"]:
            if row.get("name") == "synthetic_corpus":
                row["carries_subject_values"] = True

    def let_extension_reach_incidental(ctx):
        ctx["policy"]["retention"]["incidental"]["extended_by_case_extension"] = True

    def let_the_ceiling_be_a_cap(ctx):
        ctx["policy"]["retention"]["case_ttl"]["ceiling_is"] = "cap_on_extensions"

    def drop_rt2_from_the_list(ctx):
        lst = ctx["policy"]["retention"]["ratification"]["criteria_compiled_here"]
        ctx["policy"]["retention"]["ratification"]["criteria_compiled_here"] = [
            c for c in lst if c != "RT-2"
        ]

    def _unstamp(ctx, rel):
        ctx["status"] = "\n".join(
            ln for ln in ctx["status"].split("\n")
            if not (ln.startswith("|") and f"`{rel}`" in ln)
        )

    def unstamp_the_policy(ctx):
        _unstamp(ctx, POLICY_REL)

    def unstamp_the_fixture(ctx):
        _unstamp(ctx, FIXTURE_REL)

    def raise_the_ceiling(ctx):
        ctx["policy"]["retention"]["case_ttl"]["ceiling_days"] = 90

    def count_one_check_twice(ctx):
        ctx["policy"]["retention"]["verification"]["checks"][2]["id"] = 1

    def let_check_one_pass_on_not_found(ctx):
        check = ctx["policy"]["retention"]["verification"]["checks"][0]
        check["fails_when"] = [f for f in check["fails_when"] if f != "not_found"]

    def undesignate_the_witness(ctx):
        ctx["policy"]["retention"]["verification"]["witness"]["designated_at"] = "later"

    def defer_to_an_undeclared_question(ctx):
        ctx["policy"]["retention"]["case_ttl"]["default_days"] = {"unratified": "U-99"}

    def declare_a_question_nothing_asks(ctx):
        entries = ctx["policy"]["retention"]["unratified"]["entries"]
        entries.append(
            {
                "id": "U-98",
                "question": "unused",
                "legal_options": ["a", "b"],
                "sources": ["doctrine/RETENTION.md"],
                "refuses_as": "NOTHING HAPPENED.\n  where: x\n  rule:  y\n  moves: z",
            }
        )

    def leave_one_legal_option(ctx):
        ctx["policy"]["retention"]["unratified"]["entries"][0]["legal_options"] = ["one"]

    def empty_a_refusal(ctx):
        ctx["policy"]["retention"]["unratified"]["entries"][0]["refuses_as"] = "no"

    def rename_the_wrapper(ctx):
        ctx["policy"]["retention_policy"] = ctx["policy"].pop("retention")

    def point_the_lint_elsewhere(ctx):
        ctx["policy"]["retention"]["self_lint"] = "tools/validate_layer_model.py"

    def claim_the_file_is_generated(ctx):
        ctx["policy_text"] = (
            "# GENERATED by tools/generate_pse.py from spec/layer-model.yaml\n"
            + ctx["policy_text"]
        )

    def unstamp_a_compiled_criterion(ctx):
        ctx["status"] = re.sub(
            r"^\|\s*RT-9\b.*$", "| placeholder |", ctx["status"], flags=re.M
        )

    def _stamp(ctx, row):
        """Append a row to the Ratified table, where tools/pin_of_record.py reads.

        Until 2026-10-01 this helper inserted its row after the prose under the
        table, which this tool's old reader accepted and the authorization
        gate's reader never saw.
        """
        ctx["status"] = pin_of_record._add(ctx["status"], row)

    def stamp_the_policy(ctx):
        _stamp(
            ctx,
            "| the compiled retention table, whole artifact | "
            "`policy/retention.yaml` | v0.1 | 2026-09-11 | unstamped | operator |",
        )

    def stamp_the_fixture(ctx):
        _stamp(
            ctx,
            "| the shred round trip, whole artifact | "
            "`conformance/retention/shred-roundtrip.yaml` | v0.1 | 2026-09-11 "
            "| unstamped | operator |",
        )

    def stamp_the_policy_by_an_entry_row(ctx):
        # The ratification blocker the Step 8 review found: a dated row for one
        # entry in house format stamped the whole file.
        _stamp(
            ctx,
            "| U-3 retention entry decided | `policy/retention.yaml` | v0.1 "
            "| 2026-09-11 | unstamped | operator |",
        )

    def let_dispatch_continue(ctx):
        ctx["policy"]["retention"]["halt"]["blocks"] = "nothing; connector dispatch continues"

    def clear_the_halt_on_a_ledger_entry_too(ctx):
        ctx["policy"]["retention"]["halt"]["clears_when"] = (
            "a ledger entry by the operator, or verify_shred passes all five RT-9 checks"
        )

    def exempt_a_dispatch_runner(ctx):
        ctx["policy"]["retention"]["halt"]["does_not_block"].append("runner/dispatch.py")

    def narrow_the_trigger(ctx):
        ctx["policy"]["retention"]["halt"]["trigger"] = "SHRED_FAILED on a case the operator flags"

    def decide_u17_in_the_policy(ctx):
        ctx["policy"]["retention"]["halt"]["override"] = {"unratified": "decided, a ledger entry lifts the halt"}

    def let_the_override_lift_the_halt(ctx):
        ctx["policy"]["retention"]["halt"]["override"] = {
            "permitted_when": "the shred genuinely cannot be completed",
            "lifts_dispatch_block": True,
        }

    def make_the_halt_per_case(ctx):
        ctx["policy"]["retention"]["halt"]["per_case"] = True
        ctx["policy"]["retention"]["halt"]["clears_when"] = "a ledger entry is written"

    def delete_the_halt(ctx):
        del ctx["policy"]["retention"]["halt"]

    def hide_the_layer_model(ctx):
        ctx["strata"] = None

    def make_the_policy_a_scalar(ctx):
        ctx["policy"]["retention"] = "a string where the policy was"

    def make_a_stratum_a_list(ctx):
        ctx["policy"]["retention"]["strata"]["rows"][0]["stratum"] = [0, 1]

    def make_the_fixture_a_scalar(ctx):
        ctx["fixture"]["shred_roundtrip"] = 7

    def drop_rt19s_own_row(ctx):
        ctx["status"] = re.sub(
            r"(?m)^\| Gate telemetry with a 90 day TTL[^\n]*\n", "", ctx["status"], count=1
        )

    def withdraw_the_retention_range_row(ctx):
        ctx["status"] = re.sub(
            r"(?m)^\| RT-1 to RT-18, all criteria[^\n]*\n", "", ctx["status"], count=1
        )

    def rename_the_fixture_wrapper(ctx):
        ctx["fixture"]["roundtrip"] = ctx["fixture"].pop("shred_roundtrip")

    def count_one_fixture_check_twice(ctx):
        ctx["fixture"]["shred_roundtrip"]["verify_step"]["checks"][3]["id"] = 1

    def check1_passes_on_success(ctx):
        ctx["policy"]["retention"]["verification"]["checks"][0]["passes_when"] = (
            "the decrypt succeeds with the key"
        )

    def check1_forgets_success(ctx):
        c = ctx["policy"]["retention"]["verification"]["checks"][0]
        c["fails_when"] = [f for f in c["fails_when"] if f != "decrypt_succeeds"]

    def witness_inside_the_delete_path(ctx):
        ctx["policy"]["retention"]["verification"]["witness"]["held_outside"] = (
            "inside the enumerable delete path"
        )

    def check4_passes_always(ctx):
        ctx["policy"]["retention"]["verification"]["checks"][3]["passes_when"] = "always"

    def fixture_check5_passes_always(ctx):
        ctx["fixture"]["shred_roundtrip"]["verify_step"]["checks"][4]["passes_when"] = "always"

    def shred_the_canary_too(ctx):
        ctx["fixture"]["shred_roundtrip"]["shred_step"]["acts_on"] = "target and canary"

    def let_fixture_check_one_pass_on_not_found(ctx):
        check = ctx["fixture"]["shred_roundtrip"]["verify_step"]["checks"][0]
        check["fails_when"] = [f for f in check["fails_when"] if f != "not_found"]

    def permit_a_cached_read(ctx):
        check = ctx["fixture"]["shred_roundtrip"]["verify_step"]["checks"][1]
        check["cached_read_path_permitted"] = True

    def accept_zero_rows(ctx):
        check = ctx["fixture"]["shred_roundtrip"]["verify_step"]["checks"][2]
        check["fails_when"] = []

    def drop_the_canary(ctx):
        ctx["fixture"]["shred_roundtrip"]["create_step"]["case_count"] = 1

    def legalize_plaintext(ctx):
        rule = ctx["fixture"]["shred_roundtrip"]["create_step"]["key_wrapping_rule"]
        rule["plaintext_intermediate_state_legal"] = True

    def undesignate_the_fixture_witness(ctx):
        for built in ctx["fixture"]["shred_roundtrip"]["create_step"]["builds"]:
            if "witness" in str(built.get("object") or ""):
                built["designated_at"] = "whenever"

    def write_the_receipt_first(ctx):
        step = ctx["fixture"]["shred_roundtrip"]["receipt_step"]
        step["order"] = list(reversed(step["order"]))

    def delete_the_boundary_statement(ctx):
        ctx["fixture"]["shred_roundtrip"]["step_boundary"]["vacuous_pass_named"] = ""

    def track_an_undeclared_question(ctx):
        tracked = ctx["fixture"]["shred_roundtrip"]["unratified"][
            "tracked_from_policy_retention"
        ]
        tracked.append({"id": "U-97", "defined_in": "policy/retention.yaml"})

    def forget_a_detectable_type(ctx):
        TYPE_SEGMENTS.pop("domain", None)

    def rewrite_a_rank_three_form(ctx):
        ctx["registry"]["selectors"]["handle"]["form"] = "handle:<platform>"

    scan = scan_code(declared_codes())
    def _flip(path, value):
        def mutate(ctx):
            *parents, last = path.split(".")
            node = dig(ctx["policy"]["retention"], ".".join(parents)) if parents else ctx["policy"]["retention"]
            if isinstance(value, bool):
                node[last] = not value
            elif isinstance(value, list):
                node[last] = value[:1]
            else:
                node[last] = "on request"
        return mutate

    flips = [
        (f"flip {path} away from {criterion}", "policy", _flip(path, value), "RETENTION_POLICY_RULE_DRIFT", True)
        for path, value, criterion in PINNED_RULES
    ]

    def reconcile_unstated(ctx):
        entry = ctx["policy"]["retention"]["connector_floor"]["enforcement"][1]
        entry.pop("present", None)

    def reconcile_claimed(ctx):
        ctx["policy"]["retention"]["connector_floor"]["enforcement"][1]["present"] = True

    def canary_claimed(ctx):
        ctx["policy"]["retention"]["repo_scan"]["enforcement_parts_all_required"][1]["present"] = True

    def canary_moved_first(ctx):
        parts = ctx["policy"]["retention"]["repo_scan"]["enforcement_parts_all_required"]
        parts[0], parts[1] = parts[1], parts[0]
        parts[0]["present"], parts[1]["present"] = True, False

    def rt15_fifth_part(ctx):
        parts = ctx["policy"]["retention"]["repo_scan"]["enforcement_parts_all_required"]
        parts.append({"clause": "git history", "present": True})

    def rt15_table_gone(ctx):
        del ctx["policy"]["retention"]["repo_scan"]["enforcement_parts_all_required"]

    def reconcile_reworded_and_claimed(ctx):
        entry = ctx["policy"]["retention"]["connector_floor"]["enforcement"][1]
        entry["check"] = "a bidirectional diff of pinned versions in tools/validate_retention.py"
        entry["present"] = True

    def reconcile_hidden_by_a_decoy(ctx):
        entry = ctx["policy"]["retention"]["connector_floor"]["enforcement"][1]
        entry.pop("present", None)
        entry["code"] = {"unratified": "U-07"}

    def rt16_clause_claimed(ctx):
        ctx["policy"]["retention"]["connector_floor"]["enforcement"][0]["present"] = True

    def rt16_table_gone(ctx):
        del ctx["policy"]["retention"]["connector_floor"]["enforcement"]

    def check2_passes_always(ctx):
        ctx["policy"]["retention"]["verification"]["checks"][1]["passes_when"] = "always"

    def check3_passes_always(ctx):
        ctx["policy"]["retention"]["verification"]["checks"][2]["passes_when"] = "always"

    def fixture_check2_passes_always(ctx):
        ctx["fixture"]["shred_roundtrip"]["verify_step"]["checks"][1]["passes_when"] = "always"

    def fixture_check3_passes_always(ctx):
        ctx["fixture"]["shred_roundtrip"]["verify_step"]["checks"][2]["passes_when"] = "always"

    def rule_in_a_list_nobody_classified(ctx):
        ctx["policy"]["retention"]["verification"]["checks"][0]["skippable"] = True

    def rule_spelled_as_a_string(ctx):
        ctx["policy"]["retention"]["freeze"]["also_stops_the_ledger"] = "true"

    def narrative_survives(ctx):
        ctx["policy"]["retention"]["finding_check"]["survivability"][2]["survives"] = True

    def rt16_code_claimed(ctx):
        ctx["policy"]["retention"]["connector_floor"]["enforcement"][2]["present"] = True

    def strata_row_stratum_as_true(ctx):
        for row in ctx["policy"]["retention"]["strata"]["rows"]:
            if row.get("name") == "case_material":
                row["stratum"] = True

    def duration_as_a_float(ctx):
        ctx["policy"]["retention"]["case_ttl"]["default_days"] = 30.0

    def rule_nobody_classified(ctx):
        ctx["policy"]["retention"]["freeze"]["also_stops_the_ledger"] = True

    def stratum_written_as_true(ctx):
        ctx["policy"]["retention"]["full_text_index"]["stratum"] = True

    return flips + [
        ("let check 1 pass when the decrypt succeeds", "policy", check1_passes_on_success, "RETENTION_POLICY_FALSE_PASS_UNGUARDED", True),
        ("leave RT-16's reconcile entry silent on whether it exists", "policy", reconcile_unstated, "RETENTION_POLICY_ENFORCEMENT_UNSTATED", True),
        ("claim RT-16's reconcile is written", "policy", reconcile_claimed, "RETENTION_POLICY_ENFORCEMENT_MISSTATED", True),
        ("move the canary part first and claim it", "policy", canary_moved_first, "RETENTION_POLICY_ENFORCEMENT_MISSTATED", False, "RT-15's unpinned table items are named by place in UNPINNED_BY_NAME, so moving or deleting the table also unclassifies them"),
        ("add a fifth part to RT-15's table", "policy", rt15_fifth_part, "RETENTION_POLICY_ENFORCEMENT_MISSTATED", True),
        ("delete RT-15's enforcement table", "policy", rt15_table_gone, "RETENTION_POLICY_ENFORCEMENT_MISSTATED", False, "RT-15's unpinned table items are named by place in UNPINNED_BY_NAME, so moving or deleting the table also unclassifies them"),
        ("reword RT-16's reconcile and claim it", "policy", reconcile_reworded_and_claimed, "RETENTION_POLICY_ENFORCEMENT_MISSTATED", True),
        ("hide RT-16's reconcile flag behind a decoy deferral", "policy", reconcile_hidden_by_a_decoy, "RETENTION_POLICY_ENFORCEMENT_UNSTATED", True),
        ("claim RT-16's AGENTS.md clause is written", "policy", rt16_clause_claimed, "RETENTION_POLICY_ENFORCEMENT_MISSTATED", True),
        ("delete RT-16's enforcement entries", "policy", rt16_table_gone, "RETENTION_POLICY_ENFORCEMENT_MISSTATED", True),
        ("let check 2 pass always", "policy", check2_passes_always, "RETENTION_POLICY_FALSE_PASS_UNGUARDED", True),
        ("let check 3 pass always", "policy", check3_passes_always, "RETENTION_POLICY_FALSE_PASS_UNGUARDED", True),
        ("let the fixture's check 2 pass always", "roundtrip", fixture_check2_passes_always, "SHRED_ROUNDTRIP_FALSE_PASS_UNGUARDED", True),
        ("let the fixture's check 3 pass always", "roundtrip", fixture_check3_passes_always, "SHRED_ROUNDTRIP_FALSE_PASS_UNGUARDED", True),
        ("write the index's stratum as true", "policy", stratum_written_as_true, "RETENTION_POLICY_RULE_DRIFT", True),
        ("compile a rule nobody pinned or named", "policy", rule_nobody_classified, "RETENTION_POLICY_RULE_UNCLASSIFIED", True),
        ("compile a rule inside a list", "policy", rule_in_a_list_nobody_classified, "RETENTION_POLICY_RULE_UNCLASSIFIED", True),
        ("compile a rule spelled as a string", "policy", rule_spelled_as_a_string, "RETENTION_POLICY_RULE_UNCLASSIFIED", True),
        ("let the case narrative survive", "policy", narrative_survives, "RETENTION_POLICY_RULE_DRIFT", True),
        ("claim RT-16's undecided code exists", "policy", rt16_code_claimed, "RETENTION_POLICY_ENFORCEMENT_MISSTATED", True),
        ("write a strata row's stratum as true", "policy", strata_row_stratum_as_true, "RETENTION_POLICY_STRATA_ROW_DRIFT", True),
        ("write a duration as a float", "policy", duration_as_a_float, "RETENTION_POLICY_TTL_DRIFT", True),
        ("claim canary_subject_class is required on manifests", "policy", canary_claimed, "RETENTION_POLICY_ENFORCEMENT_MISSTATED", True),
        ("stop failing check 1 on a successful decrypt", "policy", check1_forgets_success, "RETENTION_POLICY_FALSE_PASS_UNGUARDED", True),
        ("hold the witness inside the delete path", "policy", witness_inside_the_delete_path, "RETENTION_POLICY_WITNESS_UNDESIGNATED", True),
        ("let check 4 pass always", "policy", check4_passes_always, "RETENTION_POLICY_FALSE_PASS_UNGUARDED", True),
        ("let the fixture's check 5 pass always", "roundtrip", fixture_check5_passes_always, "SHRED_ROUNDTRIP_FALSE_PASS_UNGUARDED", True),
        ("shred the canary along with the target", "roundtrip", shred_the_canary_too, "SHRED_ROUNDTRIP_NO_CANARY", True),
        # Since 2026-10-01 the three rows below also trip RETENTION_POLICY_STRATA_ROW_DRIFT,
        # because each changes a column of an RT-1 row the strata pin holds.
        ("drop a stratum row", "policy", drop_a_stratum_row, "RETENTION_POLICY_STRATA_ROW_COUNT", False),
        ("give the skeleton a subject value", "policy", subject_value_survives, "RETENTION_SUBJECT_VALUE_IN_SURVIVING_STRATUM", False),
        ("add stratum 4 to the surviving set", "policy", widen_surviving, "RETENTION_POLICY_STRATA_SET_DRIFT", True),
        ("move raw capture outside the shred boundary", "policy", move_raw_capture_outside, "RETENTION_POLICY_SHRED_BOUNDARY_DRIFT", False),
        ("raise the case ceiling to 90 days", "policy", raise_the_ceiling, "RETENTION_POLICY_TTL_DRIFT", True),
        ("count one verification check twice", "policy", count_one_check_twice, "RETENTION_POLICY_VERIFICATION_INCOMPLETE", False, "renumbering check 3 to 1 removes check 3, so the discrimination between an erroring query and an empty result set is gone as well and the false-pass check fires with the set check"),
        ("let check 1 pass on a not-found", "policy", let_check_one_pass_on_not_found, "RETENTION_POLICY_FALSE_PASS_UNGUARDED", True),
        ("designate the witness after the first write", "policy", undesignate_the_witness, "RETENTION_POLICY_WITNESS_UNDESIGNATED", True),
        ("defer a TTL to a question nothing declares", "policy", defer_to_an_undeclared_question, "RETENTION_PLACEHOLDER_UNDECLARED", False, "the TTL is also no longer the stamped number, so the duration check fires with it"),
        ("declare a question no field defers to", "policy", declare_a_question_nothing_asks, "RETENTION_PLACEHOLDER_UNREFERENCED", True),
        ("leave a placeholder one legal option", "policy", leave_one_legal_option, "RETENTION_PLACEHOLDER_INCOMPLETE", True),
        ("empty a placeholder's refusal", "policy", empty_a_refusal, "RETENTION_REFUSAL_PROSE_INCOMPLETE", True),
        ("rename the policy wrapper key", "policy", rename_the_wrapper, "RETENTION_POLICY_WRAPPER_KEY", True),
        ("point the policy's self-lint at another tool", "policy", point_the_lint_elsewhere, "RETENTION_POLICY_SELF_LINT_DRIFT", True),
        ("give the policy the generated banner", "policy", claim_the_file_is_generated, "RETENTION_POLICY_GENERATED_CLAIM", True),
        ("remove a compiled criterion's stamp row", "policy", unstamp_a_compiled_criterion, "RETENTION_CRITERION_UNSTAMPED", True),
        ("stamp the policy in the pin of record", "policy", stamp_the_policy, "-RETENTION_POLICY_UNRATIFIED", True),
        ("stamp one policy entry in house format", "policy", stamp_the_policy_by_an_entry_row, "=RETENTION_POLICY_UNRATIFIED", True),
        ("withdraw doctrine/RETENTION.md's range row", "policy", withdraw_the_retention_range_row, "RETENTION_CRITERION_UNSTAMPED", True),
        ("drop the only row that stamps RT-19", "policy", drop_rt19s_own_row, "RETENTION_CRITERION_UNSTAMPED", True),
        ("swap the authorization row for a second skeleton row", "policy", swap_authorization_for_a_second_skeleton, "RETENTION_POLICY_STRATA_ROW_DRIFT", True),
        ("let gate telemetry live forever", "policy", let_telemetry_live_forever, "RETENTION_POLICY_STRATA_ROW_DRIFT", False),
        ("give the synthetic corpus a subject value", "policy", give_the_corpus_a_subject_value, "RETENTION_SUBJECT_VALUE_IN_SURVIVING_STRATUM", False),
        ("let a case extension reach incidental content", "policy", let_extension_reach_incidental, "RETENTION_POLICY_TTL_DRIFT", True),
        ("make the case ceiling a cap on extensions", "policy", let_the_ceiling_be_a_cap, "RETENTION_POLICY_TTL_DRIFT", True),
        ("drop RT-2 from the compiled criteria", "policy", drop_rt2_from_the_list, "RETENTION_CRITERIA_LIST_DRIFT", True),
        ("unstamp the policy in the pin of record", "policy", unstamp_the_policy, "=RETENTION_POLICY_UNRATIFIED", True),
        ("unstamp the fixture in the pin of record", "roundtrip", unstamp_the_fixture, "=SHRED_ROUNDTRIP_UNRATIFIED", True),
        ("lose the layer model's strata", "policy", hide_the_layer_model, "RETENTION_LAYER_MODEL_UNREADABLE", False),
        ("make the policy wrapper a scalar", "policy", make_the_policy_a_scalar, "RETENTION_INPUT_MALFORMED", False),
        ("make a stratum a list", "policy", make_a_stratum_a_list, "RETENTION_INPUT_MALFORMED", False),
        ("make the fixture wrapper a scalar", "roundtrip", make_the_fixture_a_scalar, "RETENTION_INPUT_MALFORMED", False),
        ("let a ledger override lift the RT-11 halt", "policy", let_the_override_lift_the_halt, "RETENTION_POLICY_HALT_DRIFT", False),
        ("make the RT-11 halt per-case and clear it on a ledger entry", "policy", make_the_halt_per_case, "RETENTION_POLICY_HALT_DRIFT", True),
        ("delete the RT-11 halt", "policy", delete_the_halt, "RETENTION_POLICY_HALT_DRIFT", False),
        ("let connector dispatch continue under the halt", "policy", let_dispatch_continue, "RETENTION_POLICY_HALT_DRIFT", True),
        ("clear the halt on a ledger entry as well", "policy", clear_the_halt_on_a_ledger_entry_too, "RETENTION_POLICY_HALT_DRIFT", True),
        ("exempt a dispatch runner from the halt", "policy", exempt_a_dispatch_runner, "RETENTION_POLICY_HALT_DRIFT", True),
        ("fire the halt only on a flagged case", "policy", narrow_the_trigger, "RETENTION_POLICY_HALT_DRIFT", True),
        ("write U-17's answer into the deferral", "policy", decide_u17_in_the_policy, "RETENTION_POLICY_HALT_DRIFT", False),
        ("rename the fixture wrapper key", "roundtrip", rename_the_fixture_wrapper, "SHRED_ROUNDTRIP_WRAPPER_KEY", True),
        ("count one fixture check twice", "roundtrip", count_one_fixture_check_twice, "SHRED_ROUNDTRIP_CHECK_SET", False, "renumbering check 4 to 1 replaces check 1, whose passing condition is the decrypt failing on the key, so the false-pass guard fires with the set check"),
        ("let fixture check 1 pass on a not-found", "roundtrip", let_fixture_check_one_pass_on_not_found, "SHRED_ROUNDTRIP_FALSE_PASS_UNGUARDED", True),
        ("confirm absence over a cached read path", "roundtrip", permit_a_cached_read, "SHRED_ROUNDTRIP_FALSE_PASS_UNGUARDED", True),
        ("accept zero rows as proof the table is gone", "roundtrip", accept_zero_rows, "SHRED_ROUNDTRIP_FALSE_PASS_UNGUARDED", True),
        ("shred the only case, with no canary beside it", "roundtrip", drop_the_canary, "SHRED_ROUNDTRIP_NO_CANARY", True),
        ("legalize a plaintext intermediate state", "roundtrip", legalize_plaintext, "SHRED_ROUNDTRIP_PLAINTEXT_LEGAL", True),
        ("designate the fixture's witness later", "roundtrip", undesignate_the_fixture_witness, "SHRED_ROUNDTRIP_WITNESS_UNDESIGNATED", True),
        ("append the ledger row before verification", "roundtrip", write_the_receipt_first, "SHRED_ROUNDTRIP_RECEIPT_ORDER", True),
        ("delete the sentence naming the vacuous pass", "roundtrip", delete_the_boundary_statement, "SHRED_ROUNDTRIP_VACUOUS_PASS", True),
        ("track a question the policy does not declare", "roundtrip", track_an_undeclared_question, "SHRED_ROUNDTRIP_PLACEHOLDER_UNDECLARED", True),
        ("stamp the fixture in the pin of record", "roundtrip", stamp_the_fixture, "-SHRED_ROUNDTRIP_UNRATIFIED", True),
        ("forget a shape-detectable type", "shapes", forget_a_detectable_type, "RETENTION_REPO_SCAN_SHAPES_INCOMPLETE", True),
        ("rewrite a rank-3 form under the scan", "shapes", rewrite_a_rank_three_form, "RETENTION_REPO_SCAN_SHAPES_DRIFT", True),
        ("commit a filled account selector", "scan", lambda ctx: _sample("notes/x.md", True), scan, True),
        ("commit the same selector in placeholder form", "scan", lambda ctx: _sample("notes/x.md", False), "-" + scan, True),
        ("commit a filled selector in an exempted document", "scan", lambda ctx: _sample("docs/PLAINSIGHT-design.md", True), "-" + scan, True),
        ("hide a live selector behind an allowlisted one on the same line", "scan", _two_on_a_line, scan, True),
        ("commit a selector as a type beside a value on a JSON line", "scan", _pair_line, scan, True),
        ("commit the same pair in a YAML file", "scan", _pair_yaml, scan, True),
        ("commit the pair with a placeholder, beside an ordinary word", "scan", _pair_placeholder, "-" + scan, True),
        ("commit a typed domain in capitals", "scan", _upper_domain, scan, True),
        ("commit a pair whose type comes through a merge key", "scan", _pair_by_merge_key, scan, True),
        ("hide a live value in a tagged mapping", "scan", _pair_in_a_tagged_mapping, scan, True),
        ("hide a live value behind a key in other case", "scan", _pair_by_case_variant, scan, True),
        ("hide a live list behind a repeated key", "scan", _pair_list_then_repeat, scan, True),
        ("commit a mapping with a sequence for a key", "scan", _complex_key, "-" + scan, True),
        ("commit a phone pair written by hand in YAML", "scan", _pair_unquoted_phone, scan, True),
        ("hide a live value behind a repeated key", "scan", _pair_repeated_value, scan, True),
        ("commit a .json pair behind a byte-order mark", "scan", _pair_json_with_bom, scan, True),
        ("commit a pair whose value is a list", "scan", _pair_value_in_a_list, scan, True),
        ("commit JSON lines in a .json file", "scan", _pair_json_holding_lines, scan, True),
        ("commit a pair with its keys in capitals", "scan", _pair_keys_in_capitals, scan, True),
    ]


def _run_check(which: str, ctx: dict, sample) -> set[str]:
    try:
        if which == "policy":
            return {f.code for f in check_policy(ctx)}
        if which == "roundtrip":
            return {f.code for f in check_roundtrip(ctx)}
    except MALFORMED:
        return {"RETENTION_INPUT_MALFORMED"}
    if which == "shapes":
        return {f.code for f in check_scan_shapes(ctx)}
    registry = ctx["registry"]
    patterns = compile_patterns(registry)
    exemptions = {
        str(e.get("path")): {str(t) for t in as_list(e.get("selector_types"))}
        for e in as_list(registry["repo_scan"].get("document_exemptions"))
        if isinstance(e, dict)
    }
    rel, text = sample
    allowlist, _ = synthetic_allowlist(registry)
    # A self-test seam: a mutation may name values to treat as allowlisted,
    # because the real allowlist is empty until the cast is sealed.
    allowlist = set(allowlist) | set(ctx.get("_allowlisted", ()))
    code = scan_code(ctx["codes"])
    return {
        f.code
        for f in scan_text(rel, text, patterns, exemptions, allowlist, code)
    }


def self_test(ctx: dict) -> int:
    """Break each artifact and assert the break is refused.

    The baseline is not silent here and cannot be, because both artifacts land
    unratified and refuse by design. The guard therefore refuses on any code
    outside EXPECTED_BASELINE and every assertion below is made against the
    baseline set rather than against an empty one, so a mutation that fires only
    the designed refusals counts as not refused.
    """
    baseline = set()
    for which in ("policy", "roundtrip", "shapes"):
        baseline |= _run_check(which, copy.deepcopy(ctx), None)
    unexpected = baseline - set(EXPECTED_BASELINE)
    if unexpected:
        print(
            "self-test cannot run: the unmutated artifacts refuse for reasons "
            "beyond the two designed refusals, so every mutation below would "
            "pass for the wrong reason",
            file=sys.stderr,
        )
        for code in sorted(unexpected):
            print(f"  {code}", file=sys.stderr)
        return 1
    if baseline:
        print(
            "  baseline: "
            + ", ".join(sorted(baseline))
            + " fire against the tree as it stands, by design. Each mutation "
            "below is judged against that set."
        )

    failures = cascading = 0
    exercised: set[str] = set()
    muts = _mutations()
    saved = dict(TYPE_SEGMENTS)
    for row in muts:
        desc, which, mutate, expected, only = row[0], row[1], row[2], row[3], row[4]
        local = copy.deepcopy(ctx)
        sample = mutate(local)
        raw = _run_check(which, local, sample)
        # One mutation reaches this module's own table rather than a loaded
        # artifact, because that table is what the reconcile grades. It is
        # restored here so the next row runs against the real one.
        TYPE_SEGMENTS.clear()
        TYPE_SEGMENTS.update(saved)
        fired = raw - baseline
        exercised |= fired
        if expected.startswith("-"):
            wanted = expected[1:]
            gone = wanted not in raw
            ok, note = gone, "" if gone else f", {wanted} still fired"
        elif expected.startswith("="):
            # A designed refusal that must survive the mutation: the mutation
            # tries to clear it by a route that must not clear it.
            wanted = expected[1:]
            held = wanted in raw
            ok, note = held, "" if held else f", {wanted} was cleared"
        elif expected not in fired:
            ok, note = False, f", fired {sorted(fired)}"
        elif only and fired != {expected}:
            ok, note = False, f", also fired {sorted(fired - {expected})} and claims expect_only"
        else:
            ok, note = True, ""
        if ok and not only:
            cascading += 1
        failures += 0 if ok else 1
        mark = "refused" if ok else "PASSED  "
        print(f"  {mark}  {desc:56} expected {expected}{note}")

    token = "handle" + ":" + "acmegram" + "/" + "examplename"
    patterns = compile_patterns(ctx["registry"])
    utf16 = b"\xff\xfe" + ("note " + token + "\n").encode("utf-16-le")
    decoded = decode_for_scan("notes/u16.md", utf16)
    ok = any(p.search(decoded) for p in patterns.values())
    failures += 0 if ok else 1
    print(f"  {'refused' if ok else 'PASSED  '}  {'read a UTF-16 file by its byte-order mark':56} expected the typed shape to match")
    try:
        decode_for_scan("notes/u16be.md", ("note " + token).encode("utf-16-be"))
        ok = False
    except Unreadable as exc:
        ok = exc.finding.code == "RETENTION_REPO_SCAN_SOURCE_UNREADABLE"
    failures += 0 if ok else 1
    print(f"  {'refused' if ok else 'PASSED  '}  {'refuse NUL-bearing bytes with no byte-order mark':56} expected RETENTION_REPO_SCAN_SOURCE_UNREADABLE")

    measured = dict(zip(RT15_PART_CLAUSES, (present for _, present in rt15_parts(ctx["codes"]))))
    table = {
        r.get("clause"): r.get("present")
        for r in as_list(dig(ctx["policy"].get("retention") or {}, "repo_scan.enforcement_parts_all_required"))
        if isinstance(r, dict)
    }
    ok = measured == table
    failures += 0 if ok else 1
    print(
        f"  {'refused' if ok else 'PASSED  '}  {'measure RT-15s four parts against the policy table':56} "
        f"expected {table}, measured {measured}"
    )

    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        (base / ".githooks").mkdir()
        (base / "connectors" / "acme" / "manifests").mkdir(parents=True)
        (base / "AGENTS.md").write_bytes(
            b"## 4. Execution Limits\n\n<!-- - **" + RT15_CLAUSE_SENTENCE.encode() + b"** -->\n"
            b"\xff a byte that is not UTF-8\n\n## 5. Next\n"
        )
        (base / ".githooks" / "pre-commit").write_text(
            "# python tools/validate_retention.py --repo-scan --staged\n"
            "python tools/validate_retention.py --repo-scan --staged || {\n"
            "  echo refused\n  exit 0\n}\n",
            encoding="utf-8",
        )
        (base / "connectors" / "acme" / "manifest.yaml").write_text(
            "# canary_subject_class: synthetic\nid: acme\n", encoding="utf-8"
        )
        try:
            got = [present for _, present in rt15_parts(set(), base)]
            ok = got == [False, False, False, False]
            note = f"measured {got}"
        except Exception as exc:  # noqa: BLE001, a crash is the defect under test
            ok, note = False, f"raised {type(exc).__name__}"
    failures += 0 if ok else 1
    print(
        f"  {'refused' if ok else 'PASSED  '}  {'measure no RT-15 part from comments or bad bytes':56} "
        f"expected four absent parts, {note}"
    )

    # The canary half, measured with the validator flag set as if one existed:
    # a commented field is absent and a parsed one is present.
    global MANIFEST_VALIDATOR_REQUIRES_CANARY
    held_flag = MANIFEST_VALIDATOR_REQUIRES_CANARY
    MANIFEST_VALIDATOR_REQUIRES_CANARY = True
    try:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            manifest = base / "connectors" / "acme" / "manifest.yaml"
            manifest.parent.mkdir(parents=True)
            manifest.write_text("# canary_subject_class: synthetic\nid: acme\n", encoding="utf-8")
            commented = rt15_parts(set(), base)[1][1]
            manifest.write_text("canary_subject_class: synthetic\nid: acme\n", encoding="utf-8")
            parsed = rt15_parts(set(), base)[1][1]
        ok = commented is False and parsed is True
    finally:
        MANIFEST_VALIDATOR_REQUIRES_CANARY = held_flag
    failures += 0 if ok else 1
    print(
        f"  {'refused' if ok else 'PASSED  '}  {'measure the canary field by parse, not by text':56} "
        f"expected absent then present, measured {commented} then {parsed}"
    )

    try:
        found = selector_pairs(
            "policy/x.yaml",
            "node: &n\n  child: *n\nselectors:\n  - selector_type: email\n    value: "
            + "examplename" + "@" + "example" + ".org\n",
            {"email"},
        )
        ok = any(selector == "email" for _, selector, _ in found)
    except RecursionError:
        ok = False
    failures += 0 if ok else 1
    print(f"  {'refused' if ok else 'PASSED  '}  {'read a live pair beside a self-referential anchor':56} expected the pair to be read")

    print()
    if failures:
        print(
            f"validate_retention --self-test: {failures} mutation(s) were not "
            "refused as claimed. A gate nobody has watched fail is an "
            "assumption (HYGIENE.md section 2).",
            file=sys.stderr,
        )
        return 1
    print(
        f"validate_retention --self-test ok: {len(muts)} deliberate breaks, "
        f"{len(muts)} refused, {len(muts) - cascading} of them by the expected "
        f"code alone, {cascading} cascading with a stated reason. "
        f"{len(exercised)} distinct codes exercised, and both decode cases held."
    )
    return 0


# ---------------------------------------------------------------------------
# entry
# ---------------------------------------------------------------------------


def open_questions() -> str:
    lines = ["  questions this gate does not answer, and refuses rather than defaults:"]
    for pid, cls, question, _options, refusal in UNRATIFIED:
        lines.append(f"    {pid} (Class {cls}) {question}")
        lines.append(f"      {refusal}")
    lines.append("  readings taken, recorded for confirmation rather than assumed:")
    for rid, question, reading, _changes in READINGS:
        lines.append(f"    {rid} {question}: {reading}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Retention gate.")
    ap.add_argument("--policy", action="store_true", help="Grade policy/retention.yaml. The default.")
    ap.add_argument("--shred-roundtrip", action="store_true", help="Grade conformance/retention/shred-roundtrip.yaml.")
    ap.add_argument("--repo-scan", action="store_true", help="RT-15. Refuse a filled selector in a tracked file.")
    ap.add_argument("--staged", action="store_true", help="With --repo-scan, read the index rather than the working tree.")
    ap.add_argument("--finding", metavar="FILE", help="RT-13. Scan a candidate writeup against a case's selector set.")
    ap.add_argument("--case", metavar="ID", help="With --finding, the case whose selector set is read.")
    ap.add_argument("--self-test", action="store_true", help="Break each artifact in memory and assert each break is refused.")
    ap.add_argument("--questions", action="store_true", help="Print the open questions and the readings taken, and exit.")
    ap.add_argument("--quiet", action="store_true", help="Print only on failure, for --policy, --shred-roundtrip and --repo-scan. --self-test prints its mutation table regardless.")
    args = ap.parse_args(argv)

    # One call grades one thing, with one exception: SS-14 item 6's preflight
    # line names --policy --shred-roundtrip together, and both run. Until
    # 2026-10-01 that line ran the round trip alone and dropped --policy, so a
    # drifted or unstamped policy passed the preflight it names, and every other
    # combination dropped a mode the same way. A combination now refuses.
    modes = [m for m in ("policy", "shred_roundtrip", "repo_scan", "self_test", "finding", "questions") if getattr(args, m)]
    if len(modes) > 1 and set(modes) != {"policy", "shred_roundtrip"}:
        ap.error(
            "REFUSED RETENTION_MODES_COMBINED: "
            + ", ".join("--" + m.replace("_", "-") for m in modes)
            + " grade different things, and a combined call ran one and dropped the rest "
            "until 2026-10-01. moves: run each mode on its own; only --policy "
            "--shred-roundtrip combine, and that call runs both"
        )

    if args.questions:
        print(open_questions())
        return 0

    if args.finding:
        if not args.case:
            ap.error("--finding needs --case, because the selector set is per case")
        return check_finding(args.finding, args.case)

    runs: list = []
    try:
        if args.repo_scan:
            ctx = {"registry": load_registry(), "codes": declared_codes()}
            findings, report = check_repo_scan(ctx, args.staged)
            # The index and the working tree hold different files, so the two
            # modes record under different names and each rate means one thing.
            gate = f"{GATE_SCAN}-staged" if args.staged else GATE_SCAN
        elif args.shred_roundtrip:
            ctx = build_context()
            findings, report = check_roundtrip(ctx), None
            gate = GATE_ROUNDTRIP
            if args.policy:
                policy_findings = check_policy(ctx)
                runs.append((GATE_POLICY, policy_findings))
                findings = policy_findings + findings
        elif args.self_test:
            return self_test(build_context())
        else:
            ctx = build_context()
            findings, report = check_policy(ctx), None
            gate = GATE_POLICY
    except Unreadable as exc:
        print(exc.finding.render(), file=sys.stderr)
        return 2
    except MALFORMED as exc:
        print(
            Finding(
                "RETENTION_INPUT_MALFORMED",
                f"{POLICY_REL} or {FIXTURE_REL}",
                f"a governed input has a shape this gate cannot read "
                f"({exc.__class__.__name__}: {exc}), so the checks after that "
                "point never ran. Until 2026-10-01 this case ended in a traceback "
                "and exit 1, which a caller could not tell from violations found",
                "restore the block to the shape the policy header and the "
                "fixture's contract describe, a mapping where a mapping is "
                "read and a scalar stratum on every row",
            ).render(),
            file=sys.stderr,
        )
        return 2

    if gate_log:
        try:
            own = [f for f in findings if all(f is not g for _, fs in runs for g in fs)]
            for name, fs in runs + [(gate, own)]:
                gate_log.record_run(name, "refuse" if fs else "pass", count=len(fs))
                for fnd in fs:
                    gate_log.record_finding(name, code=fnd.code, where=fnd.where)
        except Exception:
            pass

    # Printed even under --quiet. These are states rather than passes or
    # failures, and CLAUDE.md section 4 renders a state as its consequence.
    if args.repo_scan:
        print(scan_notices(report, ctx["codes"]))

    if findings:
        for fnd in findings:
            print(fnd.render(), file=sys.stderr)
            print(file=sys.stderr)
        print(
            f"validate_retention: {len(findings)} violation(s). "
            "rule: doctrine/RETENTION.md is rank 1 and decides what is retained "
            "and what leaves; CLAUDE.md design gate 1.",
            file=sys.stderr,
        )
        return 1

    if not args.quiet:
        if args.repo_scan:
            scope = "the git index" if report["staged"] else "every tracked file in the working tree"
            print(
                f"validate_retention --repo-scan ok: {report['files']} file(s) "
                f"read from {scope}, {report['types']} selector types matched in "
                f"their typed form and in {report['pairs']} type-and-value pair(s), "
                "no filled selector found."
            )
            print(
                "  this result is not a claim that the repository is clean. It "
                "covers the file set named above and nothing else.\n"
                "  four questions this mode does not answer are open: run "
                "tools/validate_retention.py --questions."
            )
            return 0
        if args.shred_roundtrip and args.policy:
            print("validate_retention --policy ok: graded in the same run as the round trip below.")
        if args.shred_roundtrip:
            print(
                "validate_retention --shred-roundtrip ok: the fixture is "
                "internally consistent, five checks each named once, each false "
                "pass RT-9 warns about guarded."
            )
            print(
                "  not covered by this gate: whether any shred has been "
                "performed or verified. The blob store, "
                "runner/retention_sweep.py and runner/verify_shred.py are Step "
                "11, and this mode graded a document rather than a deletion."
            )
        else:
            pol = ctx["policy"]["retention"]
            rows = len(as_list(dig(pol, "strata.rows")))
            entries = len(as_list(dig(pol, "unratified.entries")))
            print(
                f"validate_retention --policy ok: {rows} strata rows, "
                f"{len(DURATIONS)} stamped durations, 5 verification checks, "
                f"{entries} recorded open questions."
            )
            print(
                "  not covered by this gate: whether any object was actually "
                "written to the stratum it declares, which needs a store; and "
                "the RT-16 reconcile of pinned connector versions against "
                "connectors/, which has neither a ledger nor a connector to "
                "read."
            )
        print(open_questions())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
