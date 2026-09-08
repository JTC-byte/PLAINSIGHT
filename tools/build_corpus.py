#!/usr/bin/env python3
"""Build the conformance corpora, and refuse drift in them.

Writes `conformance/must-pass.jsonl` and `conformance/must-fail.jsonl` from the
fixture tables below. Both files are generated artifacts in the same sense as
the schema: this tool is their only writer, and `--check` regenerates them in
memory and refuses on any difference, so a fixture cannot be edited by hand
into passing.

The must-pass corpus is one synthetic case. Every one of the model's 37
subtypes appears at least once, and the events form one lineage chain from a
GRANT to an assessment sentence, so lineage, citations, adjudication and
promotion resolve inside the file. The must-fail corpus takes an event from
that case, breaks one thing, and states the code the break must produce. The
sixteen fixtures the model names in its fixture map are here by name, less the
three the map assigns to `conformance/gate/`, which are Step 8's. Beyond the
named ones, one fixture per prohibited group of every type proves each denylist
entry is live, and one fixture per envelope, lineage, producer and rule code
proves each emitter fires.

NO VALUE APPEARS IN THIS FILE. Every selector-shaped value is a bracketed
placeholder such as `<synthetic-handle-1>`, on the rule ontology/selectors.yaml
already follows: AGENTS.md section 4 keeps a selector value out of every
tracked file, and RT-15's repo scan, when it exists, must find nothing here to
refuse. Every identifier is a uuid5 of a label, so the corpus is deterministic
and no line carries a random value.

Exit codes: 0 written or current, 1 a corpus is stale or missing under --check.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MUST_PASS = ROOT / "conformance" / "must-pass.jsonl"
MUST_FAIL = ROOT / "conformance" / "must-fail.jsonl"
TOOL = "tools/build_corpus.py"

NS = uuid.UUID("7d3a0e3c-5b8f-4c1e-9a2b-000000000001")


def u(label: str) -> str:
    return str(uuid.uuid5(NS, label))


CASE = u("case")
HUMAN = "analyst-example"
T = "2026-01-15T10:{m:02d}:00Z"

ENTITY_A = u("entity-a")
ENTITY_B = u("entity-b")
ENTITY_C = u("entity-c")
CANDIDATE = u("candidate")

# ---------------------------------------------------------------------------
# the base case, one event per subtype and then some
# ---------------------------------------------------------------------------


def env(event_id: str, etype: str, esub: str, minute: int, producer: str, payload: dict,
        parents: list[str] | None = None, transform: str | None = None, environment: str = "ISOLATED") -> dict:
    e = {
        "pse_version": "pse-event-0.1",
        "derived_from": "zmeta-event-1.0",
        "case_id": CASE,
        "event": {"event_id": event_id, "event_type": etype, "event_subtype": esub, "ts": T.format(m=minute)},
        "source": {"platform_id": "isolated-01", "environment": environment, "producer": producer, "sw_version": "0.1.0"},
        "payload": payload,
    }
    if parents is not None:
        e["lineage"] = {"based_on": list(parents), "transform": transform}
    return e


def base_case() -> list[tuple[str, str, dict]]:
    """(name, description, event) in a lineage-safe order."""
    a1, a2, a3 = u("grant"), u("extend"), u("revoke")
    c1, c2, c3 = u("permitted"), u("requires-extension"), u("refused")
    r1, i1, i2, e1 = u("run-start"), u("item-1"), u("item-2"), u("run-end")
    x1, x2, xh, xg = u("claim-handle"), u("claim-unverified"), u("claim-hint"), u("claim-generated")
    l1, l2, l3, l4 = u("link-same"), u("link-assoc"), u("link-coloc"), u("link-controls")
    k1, k2, kp = u("cluster"), u("exclude"), u("cluster-possible")
    d1, d2, d3, d4, d5, d6, d7, d8, d9 = (u(f"adj-{n}") for n in ("verify", "dispute", "promote", "ignore", "revoke", "ack", "override", "note", "question"))
    dh, dg = u("adj-verify-hint"), u("adj-verify-generated")
    s1 = u("sentence")
    y = {n: u(f"sys-{n}") for n in ("schema", "health", "coverage", "extension", "freeze", "renewal", "receipt", "failed", "cred", "sweep", "reconcile")}
    auth_ref = u("authorization-record")
    run_id = u("run-id")
    blob = "0" * 63 + "1"

    ev: list[tuple[str, str, dict]] = []

    ev.append(("authorize-grant", "The recorded authorization act, by reference.", env(
        a1, "AUTHORIZE_EVENT", "GRANT", 0, HUMAN,
        {"act": "GRANT", "authorization_ref": auth_ref, "subject_class": "S2", "expires_on": "2026-02-14",
         "pivot_depth_max": 2, "authorized_by": HUMAN, "purpose_hash": "sha256:" + "a" * 64})))
    ev.append(("authorize-extend", "An extension, parented on the grant.", env(
        a2, "AUTHORIZE_EVENT", "EXTEND", 1, HUMAN,
        {"act": "EXTEND", "authorization_ref": auth_ref, "subject_class": "S2", "expires_on": "2026-03-16",
         "pivot_depth_max": 3, "authorized_by": HUMAN, "purpose_hash": "sha256:" + "a" * 64,
         "reason": "the case needs one more hop to close its open question"}, [a1])))
    ev.append(("authorize-revoke", "A revocation, parented on the extension.", env(
        a3, "AUTHORIZE_EVENT", "REVOKE", 2, HUMAN,
        {"act": "REVOKE", "authorization_ref": auth_ref, "authorized_by": HUMAN,
         "reason": "the case closed and the record is withdrawn"}, [a2])))

    ev.append(("collect-permitted", "The gate permits a seed run.", env(
        c1, "COLLECT_EVENT", "PERMITTED", 3, "runner-subject-guard",
        {"decision": "PERMITTED", "authorization_ref": auth_ref, "connector_id": "connector-example",
         "target_selector_type": "handle", "subject_relation": "seed", "pivot_depth": 0, "decided_at_step": 6,
         "incidental_estimate": 0, "bystander_disposition": "refuse", "motivated_by": None}, [a1])))
    ev.append(("collect-requires-extension", "The gate asks for a decision.", env(
        c2, "COLLECT_EVENT", "REQUIRES_EXTENSION", 4, "runner-subject-guard",
        {"decision": "REQUIRES_EXTENSION", "authorization_ref": auth_ref, "connector_id": "connector-example",
         "target_selector_type": "email", "subject_relation": "pivot", "pivot_depth": 3, "decided_at_step": 4,
         "extension_basis": "pivot_depth_exceeded"}, [a2])))
    ev.append(("collect-refused", "The gate refuses at step 2, with no record to point at.", env(
        c3, "COLLECT_EVENT", "REFUSED", 5, "runner-subject-guard",
        {"decision": "REFUSED", "connector_id": "connector-example", "target_selector_type": "phone",
         "decided_at_step": 2, "refusal_basis": "authorization_missing"})))

    ev.append(("probe-run-start", "A run, gated by the PERMITTED it names.", env(
        r1, "PROBE_EVENT", "RUN_START", 6, "runner-dispatch",
        {"phase": "RUN_START", "run_id": run_id, "connector_id": "connector-example", "connector_version": "0.1.0",
         "connector_kind": "one_shot", "credential_id": None,
         "egress": {"environment": "ISOLATED", "egress_identity": "egress-persona-1"},
         "argv_template": "example --target <handle>", "motivated_by": None, "target_selector_type": "handle",
         "manifest_hash": "sha256:" + "b" * 64}, [c1])))
    ev.append(("probe-item-1", "One item the run returned.", env(
        i1, "PROBE_EVENT", "ITEM", 7, "connector-example",
        {"phase": "ITEM", "run_id": run_id, "item_id": i1, "locator": "site:example/1", "outcome": "hit",
         "raw_ref": {"blob_sha256": blob, "raw_span": None}}, [r1])))
    ev.append(("probe-item-2", "A second item.", env(
        i2, "PROBE_EVENT", "ITEM", 7, "connector-example",
        {"phase": "ITEM", "run_id": run_id, "item_id": i2, "locator": "site:example/2", "outcome": "hit",
         "raw_ref": {"blob_sha256": blob, "raw_span": None}}, [r1])))
    ev.append(("probe-run-end", "The run ends.", env(
        e1, "PROBE_EVENT", "RUN_END", 8, "runner-dispatch",
        {"phase": "RUN_END", "run_id": run_id, "exit_code": 0, "error_class": "ok", "item_count": 2,
         "duration_ms": 1200}, [r1])))

    def claim(eid: str, item: str, selector: str, value: str) -> dict:
        return env(eid, "EXTRACT_EVENT", "CLAIM", 9, "connector-example",
                   {"extract_kind": "CLAIM", "selector_type": selector, "value": value, "subject_ref": None,
                    "source_ref": {"item_id": item, "source_path": "/profile/0", "raw_span": None},
                    "extractor": {"name": "example-extractor", "version": "0.1.0"},
                    "temporal": {"observed_at": T.format(m=9), "asserted_at": None, "time_provenance": "collection_time"},
                    "negative_state": "present"}, [item], "translate:connector-example@0.1.0")

    ev.append(("extract-claim-handle", "One claim from item 1.", claim(x1, i1, "handle", "<synthetic-handle-1>")))
    ev.append(("extract-claim-unverified", "A claim nothing has verified.", claim(x2, i2, "handle", "<synthetic-handle-2>")))
    ev.append(("extract-claim-hint", "A masked recovery hint, a constraint and never a value.",
               claim(xh, i1, "email_hint_recovery_masked", "<synthetic-mask>")))
    ev.append(("extract-claim-generated", "A generated permutation, observed nowhere.",
               claim(xg, i1, "email_generated_permutation", "<synthetic-permutation>")))

    def link(eid: str, kind: str) -> dict:
        return env(eid, "LINK_EVENT", kind, 10, "matcher-example",
                   {"link_type": kind, "claim": {"subject_refs": [ENTITY_A, ENTITY_B], "predicate": kind.lower(),
                                                 "rationale_template": None},
                    "model": {"name": "example-matcher", "version": "0.1.0", "calibration_ref": None},
                    "based_on": [x1], "accepted": False}, [x1])

    for eid, kind in ((l1, "SAME_ENTITY"), (l2, "ASSOCIATED_WITH"), (l3, "CO_LOCATED"), (l4, "CONTROLS")):
        ev.append((f"link-{kind.lower()}", "A proposal, always unaccepted.", link(eid, kind)))

    ev.append(("identity-cluster", "An analyst's assertion with per-member seams.", env(
        k1, "IDENTITY_EVENT", "CLUSTER", 11, HUMAN,
        {"assertion": "CLUSTER", "cluster_id": u("cluster-id"), "members": [ENTITY_A, ENTITY_B], "asserted_by": HUMAN,
         "rationale_codes": ["h", "b"], "band": "likely", "last_supporting_ts": T.format(m=9),
         "member_seams": {ENTITY_A: ["h"], ENTITY_B: ["b"]}, "basis_claims": [x1], "note": None,
         "hypothesis_set": None, "circularity_override": None, "subject_ref": None}, [x1, l1])))
    ev.append(("identity-cluster-possible", "A possible-band cluster, cited by no sentence here.", env(
        kp, "IDENTITY_EVENT", "CLUSTER", 11, HUMAN,
        {"assertion": "CLUSTER", "cluster_id": u("cluster-id-possible"), "members": [ENTITY_A, ENTITY_C],
         "asserted_by": HUMAN, "rationale_codes": ["g"], "band": "possible", "last_supporting_ts": T.format(m=9),
         "member_seams": {ENTITY_A: ["g"], ENTITY_C: ["g"]}, "basis_claims": [x1]}, [x1])))
    ev.append(("identity-exclude", "An affirmative exclusion.", env(
        k2, "IDENTITY_EVENT", "EXCLUDE", 11, HUMAN,
        {"assertion": "EXCLUDE", "candidate_ref": CANDIDATE, "asserted_by": HUMAN,
         "basis": "the candidate's declared location contradicts the anchor claim"}, [x1])))

    def adj(eid: str, disp: str, target: str, extra: dict) -> dict:
        p = {"disposition": disp, "target_ref": target, "analyst": HUMAN}
        p.update(extra)
        return env(eid, "ADJUDICATE_EVENT", disp, 12, HUMAN, p, [target])

    ev.append(("adjudicate-verify", "Review on citation.", adj(d1, "VERIFY", x1, {"in_course_of": "citation"})))
    ev.append(("adjudicate-verify-hint", "The hint claim is verified too.", adj(dh, "VERIFY", xh, {"in_course_of": "citation"})))
    ev.append(("adjudicate-verify-generated", "The generated claim is verified, and never promoted.",
               adj(dg, "VERIFY", xg, {"in_course_of": "citation"})))
    ev.append(("adjudicate-dispute", "A dispute carries its reason.", adj(d2, "DISPUTE", x1, {"reason": "the source page rendered a cached copy"})))
    ev.append(("adjudicate-promote", "An item promoted to an Account on a permitted anchor.", adj(
        d3, "PROMOTE", i1, {"promotion_kind": "item_to_entity", "entity_type": "Account", "entity_id": ENTITY_A,
                             "anchor_selector_type": "platform_uid", "anchor_claim_ref": x1})))
    ev.append(("adjudicate-ignore", "An ignore with nothing load-bearing behind the target.", adj(d4, "IGNORE", i2, {})))
    ev.append(("adjudicate-revoke", "A revocation of a cluster.", adj(d5, "REVOKE", k1, {"reason": "a member was shown to be a namesake"})))
    ev.append(("adjudicate-acknowledge", "An acknowledgement.", adj(d6, "ACKNOWLEDGE", k1, {"note": "seen, no action"})))
    ev.append(("adjudicate-override", "An override with its note.", adj(d7, "OVERRIDE", k1, {"override_kind": "circular_evidence", "note": "the basis is independent of the member's own value"})))
    ev.append(("adjudicate-note", "A note on a claim.", adj(d8, "NOTE", x1, {"text": "compare against item 2 before citing"})))
    ev.append(("adjudicate-question", "A question on a claim.", adj(d9, "QUESTION", x1, {"text": "is the platform id stable across the rename"})))

    ev.append(("assess-sentence", "One sentence, one live citation to a verified claim.", env(
        s1, "ASSESS_EVENT", "SENTENCE", 13, HUMAN,
        {"assessment_kind": "SENTENCE", "subject_ref": ENTITY_A, "subject_class": "S2",
         "text": "The account is held by the cluster's subject.",
         "citations": [{"ref": x1, "cited_as": "handle", "caveat": None, "note": None}], "author": HUMAN,
         "geo": None, "paragraph_ref": None}, [k1, x1])))

    sysev = lambda eid, sub, minute, producer, payload, parents=None: env(eid, "SYSTEM_EVENT", sub, minute, producer, payload, parents)  # noqa: E731
    ev.append(("system-schema-violation", "A diagnostic that names the code and never the value.",
               sysev(y["schema"], "SCHEMA_VIOLATION", 14, "runner-ingest", {"system_type": "SCHEMA_VIOLATION", "reason_code": "SCHEMA_INVALID", "original_event_id": u("offending")})))
    ev.append(("system-connector-health", "Health is a field, frozen at collection time.",
               sysev(y["health"], "CONNECTOR_HEALTH", 14, "runner-canary", {"system_type": "CONNECTOR_HEALTH", "connector_id": "connector-example", "probe_unit": "connector", "state": "HEALTHY", "canary_id": "canary-1"})))
    ev.append(("system-coverage-interval", "A coverage interval closed by a positive read.",
               sysev(y["coverage"], "COVERAGE_INTERVAL", 14, "runner-watchdog", {"system_type": "COVERAGE_INTERVAL", "target_ref": u("target"), "t_start": T.format(m=0), "t_end": T.format(m=14), "verified": True, "method": "poll"})))
    ev.append(("system-retention-extension", "An extension, by a named human, with a reason.",
               sysev(y["extension"], "RETENTION_EXTENSION", 15, HUMAN, {"system_type": "RETENTION_EXTENSION", "author": HUMAN, "reason": "the validation run is not finished", "previous_retain_until": "2026-02-14", "new_retain_until": "2026-03-16"})))
    ev.append(("system-retention-freeze", "A freeze with its expiry.",
               sysev(y["freeze"], "RETENTION_FREEZE", 15, HUMAN, {"system_type": "RETENTION_FREEZE", "author": HUMAN, "reason": "a stated obligation holds the case", "freeze_expires_on": "2026-04-15"})))
    ev.append(("system-retention-renewal", "A renewal names its obligation and expected resolution.",
               sysev(y["renewal"], "RETENTION_RENEWAL", 15, HUMAN, {"system_type": "RETENTION_RENEWAL", "author": HUMAN, "obligation": "records request 2026-0001", "expected_resolution_on": "2026-05-15", "renewal_ordinal": 1, "freeze_expires_on": "2026-05-15"}, [y["freeze"]])))
    ev.append(("system-shred-receipt", "All five checks, each once.",
               sysev(y["receipt"], "SHRED_RECEIPT", 16, "runner-sweep", {"system_type": "SHRED_RECEIPT", "receipt_hash": "sha256:" + "c" * 64, "blob_count": 12, "checks_passed": [1, 2, 3, 4, 5]})))
    ev.append(("system-shred-failed", "A failed check halts every run.",
               sysev(y["failed"], "SHRED_FAILED", 16, "runner-sweep", {"system_type": "SHRED_FAILED", "failed_check": 3, "halt_system_wide": True})))
    ev.append(("system-credential-state", "An active credential, by id and never by value.",
               sysev(y["cred"], "CREDENTIAL_STATE", 16, "runner-pool", {"system_type": "CREDENTIAL_STATE", "credential_id": "credential-1", "state": "active"})))
    ev.append(("system-sweep-heartbeat", "The sweep's heartbeat.",
               sysev(y["sweep"], "SWEEP_HEARTBEAT", 17, "runner-sweep", {"system_type": "SWEEP_HEARTBEAT", "swept_count": 0, "next_due": T.format(m=47)})))
    ev.append(("system-reconcile-heartbeat", "The ledger reconciler's heartbeat.",
               sysev(y["reconcile"], "RECONCILE_HEARTBEAT", 17, "runner-reconcile", {"system_type": "RECONCILE_HEARTBEAT", "ledger_only_count": 0, "storage_only_count": 0, "next_due": T.format(m=47)})))
    return ev


# ---------------------------------------------------------------------------
# must-fail: one break each
# ---------------------------------------------------------------------------


def _by_name(base: list[tuple[str, str, dict]]) -> dict[str, dict]:
    return {n: e for n, _, e in base}


def fixtures(base: list[tuple[str, str, dict]]) -> list[dict]:
    B = _by_name(base)
    ids = {n: e["event"]["event_id"] for n, _, e in base}
    out: list[dict] = []

    def add(name: str, description: str, code: str, only: bool, source: str, mutate, fresh_id: bool = False):
        e = copy.deepcopy(B[source])
        if fresh_id:
            e["event"]["event_id"] = u(f"fixture-{name}")
        mutate(e)
        context = [copy.deepcopy(x) for n, _, x in base if n != source or fresh_id]
        out.append({"name": name, "description": description, "expect_code": code, "expect_only": only,
                    "context": context, "event": e})

    # ---- the model's named fixtures, must-fail corpus (13) ----
    def m(e):  # hint cited as email
        e["payload"]["citations"] = [{"ref": ids["extract-claim-hint"], "cited_as": "email", "caveat": None, "note": None}]
        e["lineage"]["based_on"] = [ids["identity-cluster"], ids["extract-claim-hint"]]
    add("hint-cited-as-email", "An email_hint_recovery_masked claim satisfying a citation for email. D2's flagship case.",
        "HINT_CITED_AS_VALUE", True, "assess-sentence", m)

    def m(e):
        e["payload"]["citations"] = [{"ref": ids["extract-claim-generated"], "cited_as": "email_generated_permutation", "caveat": None, "note": None}]
        e["lineage"]["based_on"] = [ids["identity-cluster"], ids["extract-claim-generated"]]
    add("generated-permutation-cited-as-observed", "A generated permutation cited with no PROMOTE generated_to_observed.",
        "GENERATED_CITED_AS_OBSERVED", True, "assess-sentence", m)

    add("account-anchored-on-handle", "An Account promoted on an anchor whose registry entry has may_anchor_entity false.",
        "SELECTOR_ANCHOR_PROHIBITED", True, "adjudicate-promote", lambda e: e["payload"].__setitem__("anchor_selector_type", "handle"))
    add("absence-claimed-without-canary", "attempted_and_absent on a field with no canary-proven always_present.",
        "ABSENCE_CLAIMED_WITHOUT_CANARY", False, "extract-claim-handle", lambda e: e["payload"].__setitem__("negative_state", "attempted_and_absent"))
    add("extract-carries-confidence", "An observation payload carrying confidence.",
        "EXTRACT_HAS_CONFIDENCE", True, "extract-claim-handle", lambda e: e["payload"].__setitem__("confidence", 0.9))
    add("extract-carries-review-state", "A stored review column instead of an appended adjudication (D3).",
        "EXTRACT_HAS_REVIEW_STATE", True, "extract-claim-handle", lambda e: e["payload"].__setitem__("review_state", "verified"))
    add("nested-layer-collapse", "cluster_id at payload.extensions.notes.cluster_id. Proves the denylist is recursive.",
        "LAYER_COLLAPSE_NESTED", False, "extract-claim-handle",
        lambda e: e["payload"].__setitem__("extensions", {"notes": {"cluster_id": u("smuggled")}}))
    add("unregistered-selector-type", "selector_type gravatar_hash. Closed at the corpus boundary.",
        "SELECTOR_TYPE_UNREGISTERED", True, "extract-claim-handle", lambda e: e["payload"].__setitem__("selector_type", "gravatar_hash"))
    add("cluster-minted-by-connector", "An identity assertion with producer connector-toutatis. Fires before any semantic check.",
        "PRODUCER_NOT_ALLOWED", True, "identity-cluster", lambda e: e["source"].__setitem__("producer", "connector-toutatis"))
    add("link-arrives-accepted", "A proposal with accepted true.",
        "LINK_HAS_ACCEPTANCE", True, "link-same_entity", lambda e: e["payload"].__setitem__("accepted", True))
    add("extract-no-lineage", "A claim with no item parent is uncitable by construction.",
        "LINEAGE_MISSING", True, "extract-claim-handle", lambda e: e.pop("lineage"))
    add("cluster-carries-rollup-confidence", "A cluster carrying a rollup.",
        "CLUSTER_HAS_ROLLUP_CONFIDENCE", True, "identity-cluster", lambda e: e["payload"].__setitem__("rollup", 0.8))

    def m(e):
        e["payload"]["basis_claims"] = [ids["extract-claim-generated"]]
        e["lineage"]["based_on"] = [ids["extract-claim-generated"], ids["link-same_entity"]]
    add("merge-circularity", "A basis claim tracing to a GENERATED origin, without circularity_override.",
        "MERGE_CIRCULAR", True, "identity-cluster", m)

    # ---- the D5 shape, in the must-fail corpus as well as the gate corpus ----
    def m(e):
        e["lineage"]["based_on"] = [ids["probe-run-start"]]
    add("run-start-without-permitted", "A RUN_START whose only parent is another run: no COLLECT PERMITTED resolves.",
        "SUBJECT_NOT_AUTHORIZED", True, "probe-run-start", m, fresh_id=True)
    add("run-differs-from-its-decision", "A RUN_START whose connector_id is not the one its PERMITTED evaluated.",
        "SUBJECT_NOT_AUTHORIZED", True, "probe-run-start", lambda e: e["payload"].__setitem__("connector_id", "connector-other"))

    # ---- one per prohibited group of every type ----
    import yaml  # local import: the tables above need no YAML

    sem = yaml.safe_load((ROOT / "policy" / "semantics.yaml").read_text(encoding="utf-8"))["semantics"]
    first_of = {}
    for n, _, e in base:
        first_of.setdefault(e["event"]["event_type"], n)
    for tname, tdef in sem["event_types"].items():
        src = first_of[tname]
        for g in tdef["payload_must_not_contain"]:
            name = g["names"][0]
            add(f"denylist-{tname.lower()}-{name}", f"{tname} payload carrying prohibited name {name} at depth zero.",
                g["code"], True, src, lambda e, name=name: e["payload"].__setitem__(name, "<prohibited>"))

    # ---- envelope, shape, and confidence ----
    add("version-mismatch", "pse_version outside the declared const.", "VERSION_MISMATCH", True, "system-sweep-heartbeat",
        lambda e: e.__setitem__("pse_version", "pse-event-9.9"))
    add("case-id-missing", "No case_id. D4 keys the shred on it.", "CASE_ID_MISSING", True, "system-sweep-heartbeat",
        lambda e: e.pop("case_id"))
    add("event-type-unknown", "event_type outside the nine.", "EVENT_TYPE_UNKNOWN", True, "system-sweep-heartbeat",
        lambda e: e["event"].__setitem__("event_type", "TRACK_EVENT"))
    add("event-subtype-outside-type", "event_subtype outside the type's set.", "EVENT_SUBTYPE_MISMATCH", True, "system-sweep-heartbeat",
        lambda e: e["event"].__setitem__("event_subtype", "HEARTBEAT"))
    add("discriminator-disagrees", "The payload discriminator differs from event_subtype.", "EVENT_SUBTYPE_MISMATCH", True,
        "system-sweep-heartbeat", lambda e: e["payload"].__setitem__("system_type", "SHRED_RECEIPT"))
    add("payload-field-missing", "A field the subtype requires is absent.", "PAYLOAD_FIELD_MISSING", True, "system-sweep-heartbeat",
        lambda e: e["payload"].pop("next_due"))
    add("enum-value-invalid", "A closed-set field outside its set.", "ENUM_VALUE_INVALID", True, "system-connector-health",
        lambda e: e["payload"].__setitem__("state", "GREAT"))
    add("schema-invalid-envelope-key", "An unknown envelope key.", "SCHEMA_INVALID", True, "system-sweep-heartbeat",
        lambda e: e.__setitem__("profile", "L"))
    add("envelope-confidence-refused", "The reserved envelope key, on a type with the general code.", "CONFIDENCE_PROHIBITED", True,
        "authorize-grant", lambda e: e.__setitem__("confidence", 0.5))
    add("envelope-confidence-on-extract", "The reserved envelope key, on the type with its own code.", "EXTRACT_HAS_CONFIDENCE", True,
        "extract-claim-handle", lambda e: e.__setitem__("confidence", 0.5))
    add("incidental-estimate-outside-set", "incidental_estimate as a string other than unestimable.", "ENUM_VALUE_INVALID", True,
        "collect-permitted", lambda e: e["payload"].__setitem__("incidental_estimate", "a few"))

    # ---- producer authority ----
    add("grant-by-runner", "An authorization emitted by a runner rather than a named human.", "PRODUCER_NOT_ALLOWED", True,
        "authorize-grant", lambda e: e["source"].__setitem__("producer", "runner-dispatch"))
    add("permitted-by-human", "A gate decision emitted by a human rather than the subject guard.", "PRODUCER_NOT_ALLOWED", True,
        "collect-permitted", lambda e: e["source"].__setitem__("producer", HUMAN))
    add("run-start-by-connector", "A connector emitting RUN_START, which LM-R6 refuses by name.", "PRODUCER_NOT_ALLOWED", True,
        "probe-run-start", lambda e: e["source"].__setitem__("producer", "connector-example"))
    add("freeze-by-runner", "A retention freeze by a wildcard producer. A wildcard cannot be an author.", "PRODUCER_NOT_ALLOWED", True,
        "system-retention-freeze", lambda e: e["source"].__setitem__("producer", "runner-sweep"))

    # ---- lineage ----
    add("lineage-parent-unresolved", "A based_on id that resolves to no event.", "LINEAGE_PARENT_UNRESOLVED", False,
        "extract-claim-handle", lambda e: e["lineage"].__setitem__("based_on", [u("nowhere")]))
    add("lineage-parent-type-invalid", "A claim parented on a GRANT.", "LINEAGE_PARENT_TYPE_INVALID", False,
        "extract-claim-handle", lambda e: e["lineage"].__setitem__("based_on", [ids["authorize-grant"]]))
    add("lineage-cross-case", "A parent in another case. The shred is per case.", "LINEAGE_CROSS_CASE", True,
        "extract-claim-handle", lambda e: e.__setitem__("case_id", u("other-case")))
    add("lineage-payload-based-on-not-subset", "payload.based_on names an id absent from lineage.based_on.",
        "LINEAGE_PAYLOAD_BASED_ON_NOT_SUBSET", True, "link-same_entity",
        lambda e: e["payload"].__setitem__("based_on", [ids["extract-claim-unverified"]]))
    add("verify-targets-a-cluster", "VERIFY on a cluster is a category error.", "LINEAGE_PARENT_TYPE_INVALID", False,
        "adjudicate-verify", lambda e: (e["payload"].__setitem__("target_ref", ids["identity-cluster"]),
                                        e["lineage"].__setitem__("based_on", [ids["identity-cluster"]])))
    add("renewal-without-freeze", "A renewal with no freeze or renewal parent.", "LINEAGE_MISSING", True,
        "system-retention-renewal", lambda e: e.pop("lineage"))

    # ---- payload rules ----
    add("grant-without-purpose", "A GRANT with no purpose_hash. A case with no purpose has no authorization.",
        "CASE_PURPOSE_UNBOUND", True, "authorize-grant", lambda e: e["payload"].pop("purpose_hash"))
    add("bystander-disposition-retain", "bystander_disposition retain, defined in doctrine and refused.",
        "BYSTANDER_DISPOSITION_OUT_OF_SET", True, "collect-permitted", lambda e: e["payload"].__setitem__("bystander_disposition", "retain"))
    add("run-from-local", "A RUN_START naming LOCAL as its egress environment.", "EGRESS_ENVIRONMENT_REFUSED", True,
        "probe-run-start", lambda e: e["payload"]["egress"].__setitem__("environment", "LOCAL"))
    add("run-source-local", "A RUN_START whose source environment is LOCAL.", "EGRESS_ENVIRONMENT_REFUSED", True,
        "probe-run-start", lambda e: e["source"].__setitem__("environment", "LOCAL"))
    add("cluster-one-member", "One account is not an identity assertion.", "CLUSTER_MEMBERS_INSUFFICIENT", True,
        "identity-cluster", lambda e: e["payload"].__setitem__("members", [ENTITY_A]))
    add("cluster-no-rationale", "rationale_codes empty.", "RATIONALE_MISSING", True,
        "identity-cluster", lambda e: e["payload"].__setitem__("rationale_codes", []))
    add("cluster-seam-missing-member", "member_seams omits a member.", "RATIONALE_MISSING", True,
        "identity-cluster", lambda e: e["payload"].__setitem__("member_seams", {ENTITY_A: ["h"]}))
    add("external-knowledge-without-note", "rationale code k without a note.", "RATIONALE_NOTE_MISSING", True,
        "identity-cluster", lambda e: e["payload"].__setitem__("rationale_codes", ["h", "k"]))
    add("almost-certain-on-one-class", "band almost_certain on two string matches.", "BAND_UNSUPPORTED", True,
        "identity-cluster", lambda e: (e["payload"].__setitem__("band", "almost_certain"),
                                       e["payload"].__setitem__("rationale_codes", ["h", "e"])))
    add("renewal-without-obligation", "A renewal naming no obligation.", "FREEZE_RENEWAL_UNJUSTIFIED", True,
        "system-retention-renewal", lambda e: e["payload"].pop("obligation"))
    add("quarantine-without-exit", "A quarantine with no written exit criterion.", "CREDENTIAL_QUARANTINE_NO_EXIT", True,
        "system-credential-state", lambda e: e["payload"].__setitem__("state", "quarantined"))
    add("burn-without-finding", "A burn with no finding_ref.", "CREDENTIAL_BURN_NO_FINDING", True,
        "system-credential-state", lambda e: e["payload"].__setitem__("state", "burned"))
    add("reason-code-undeclared", "A SCHEMA_VIOLATION naming a code the vocabulary does not declare.", "ENUM_VALUE_INVALID", True,
        "system-schema-violation", lambda e: e["payload"].__setitem__("reason_code", "NOT_A_CODE"))
    add("sentence-without-class", "An assessment with no subject_class. SS-18.", "SUBJECT_CLASS_MISSING", True,
        "assess-sentence", lambda e: e["payload"].pop("subject_class"))
    add("sentence-without-citation", "An assessment with no citations.", "CITATION_MISSING", True,
        "assess-sentence", lambda e: e["payload"].__setitem__("citations", []))
    add("citation-outside-lineage", "A citation whose ref is not in lineage.based_on.", "CITATION_MISSING", True,
        "assess-sentence", lambda e: e["payload"].__setitem__("citations", [{"ref": ids["extract-claim-unverified"], "cited_as": None, "caveat": None, "note": None}]))

    def m(e):
        e["payload"]["citations"] = [{"ref": ids["extract-claim-unverified"], "cited_as": None, "caveat": None, "note": None}]
        e["lineage"]["based_on"] = [ids["identity-cluster"], ids["extract-claim-unverified"]]
    add("citation-unadjudicated", "A cited claim with no VERIFY.", "CITATION_UNADJUDICATED", True, "assess-sentence", m)

    def m(e):
        e["payload"]["citations"] = [{"ref": ids["identity-cluster-possible"], "cited_as": None, "caveat": None, "note": "gestalt reviewed"}]
        e["lineage"]["based_on"] = [ids["identity-cluster-possible"]]
    add("possible-band-without-caveat", "A possible-band cluster cited without a caveat.", "CITATION_CAVEAT_MISSING", True, "assess-sentence", m)

    def m(e):
        e["payload"]["citations"] = [{"ref": ids["identity-cluster-possible"], "cited_as": None, "caveat": "possible only", "note": None}]
        e["lineage"]["based_on"] = [ids["identity-cluster-possible"]]
    add("gestalt-cited-without-note", "A gestalt-rationale cluster cited without a note.", "RATIONALE_NOTE_MISSING", True, "assess-sentence", m)

    return out


# ---------------------------------------------------------------------------
# rendering, writing, checking
# ---------------------------------------------------------------------------


def render() -> tuple[str, str]:
    base = base_case()
    must_pass = "".join(
        json.dumps({"name": n, "description": d, "event": e}, ensure_ascii=False, separators=(",", ":")) + "\n"
        for n, d, e in base
    )
    must_fail = "".join(json.dumps(f, ensure_ascii=False, separators=(",", ":")) + "\n" for f in fixtures(base))
    return must_pass, must_fail


def coverage(must_fail_text: str) -> tuple[set[str], set[str]]:
    import yaml

    codes = {c["code"] for c in yaml.safe_load((ROOT / "policy" / "violation-codes.yaml").read_text(encoding="utf-8"))["violation_codes"]["codes"]}
    covered = {json.loads(line)["expect_code"] for line in must_fail_text.splitlines() if line.strip()}
    return covered, codes - covered


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Build the conformance corpora from the fixture tables.")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    must_pass, must_fail = render()
    targets = ((MUST_PASS, must_pass), (MUST_FAIL, must_fail))
    if args.check:
        stale = [p for p, text in targets if not p.is_file() or p.read_text(encoding="utf-8") != text]
        if stale:
            for p in stale:
                print(
                    f"REFUSED GENERATED_ARTIFACT_STALE\n  where: {p.relative_to(ROOT).as_posix()}\n"
                    f"  what:  differs from what {TOOL} builds, or is missing\n"
                    f"  moves: run `python {TOOL}`, and never edit a corpus file by hand",
                    file=sys.stderr,
                )
            return 1
        if not args.quiet:
            print("build_corpus ok: both corpora current")
        return 0
    for p, text in targets:
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        if not args.quiet:
            print(f"wrote {p.relative_to(ROOT).as_posix()} ({len(text.splitlines())} lines)")
    covered, uncovered = coverage(must_fail)
    if not args.quiet:
        print(f"must-fail covers {len(covered)} codes; no fixture for: {', '.join(sorted(uncovered)) or 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
