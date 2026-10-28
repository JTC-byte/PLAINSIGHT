"""runner/subject_guard.py exercised against the criteria that claim it.

Each test names the claim it proves. Every value below is a placeholder from
synthetic/GROUND_TRUTH.yaml's token set; nothing here is a selector.

Runs under pytest (python -m pytest runner -q) and as a script
(python runner/tests/test_subject_guard.py), so the kernel gate needs nothing
beyond PyYAML and jsonschema, which every validator here already needs.

The stamp state is replaced through `subject_guard.read_stamps`, the one seam
the module offers, with a fixture-supplied table on the corpus's GF-U1 pattern.
Two tests read the live pin of record instead, and both assert a refusal.
"""

from __future__ import annotations

import builtins
import contextlib
import copy
import datetime as dt
import importlib
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))

from runner import subject_guard as sg  # noqa: E402

CASE = "7ff25497-b478-542c-bdbd-2363207a8127"
REF = "b7b0f5d8-3154-51d4-a756-94d531f2b735"
CLAIM_1 = "08051b5d-66dc-51fa-b6bd-05289a7ddab6"
CLAIM_2 = "2b0c8d3e-5a5e-5f0e-9c55-0d5f6a0f1a11"
CLAIM_3 = "6d1f7b2a-0c3e-5b6d-8e9f-1a2b3c4d5e6f"
ADJ = "a1b2c3d4-e5f6-5a7b-8c9d-0e1f2a3b4c5d"
GRANT = "203cb0dd-8873-51cf-94ba-82b2aa703533"
SEED = ("handle", "<handle:instagram:P-A>")
SEED_OTHER = ("handle", "<handle:instagram:P-C>")
HOP_1 = ("handle", "<handle:telegram:P-A>")
HOP_2 = ("handle", "<handle:telegram:P-C>")
PLACEHOLDERS = [SEED[1], SEED_OTHER[1], HOP_1[1], HOP_2[1]]
CLOCK = dt.datetime(2026, 1, 20, 9, 0, tzinfo=dt.timezone.utc)
SCHEMA = ROOT / "schema" / "pse-event-0.1.schema.json"


class FixtureStamps:
    """A fixture-supplied stamp state. Everything stamped unless told otherwise."""

    def __init__(self, missing=(), open_entries=(), readable=True):
        self.missing, self.open, self.readable = set(missing), set(open_entries), readable

    def item_6_reasons(self, paths, criteria):
        return [f"{p} withheld by the fixture" for p in list(paths) + list(criteria) if p in self.missing]

    def entry_resolved(self, entry_id):
        return entry_id not in self.open


STAMPED = FixtureStamps()


@contextlib.contextmanager
def stamps(state):
    saved = sg.read_stamps
    sg.read_stamps = lambda: state
    try:
        yield
    finally:
        sg.read_stamps = saved


@contextlib.contextmanager
def policy(doc):
    saved = sg.load_policy
    rt = sg._yaml_load(sg.RETENTION_POLICY)["retention"]["ratification"]["criteria_compiled_here"]
    sg.load_policy = lambda: sg.Policy(doc, rt)
    try:
        yield
    finally:
        sg.load_policy = saved


def record(**over):
    rec = {
        "case_id": CASE,
        "subject_class": "S2",
        "selectors": [{"selector_type": SEED[0], "value": SEED[1]}],
        "pivot_depth_max": 2,
        "purpose": "Measure the matcher against the designed cast, scoring the confuser pair as known negatives.",
        "evidence_ref": {"kind": "cast_manifest_entry", "ref": "synthetic/GROUND_TRUTH.yaml personas P-A"},
        "authorized_by": "analyst-example",
        "authorized_on": "2026-01-15",
        "expires_on": "2026-02-14",
    }
    rec.update(over)
    return rec


def request(target=SEED, chain=(), rec=None, **over):
    base = record() if rec is None else rec
    kw = dict(
        case_id=CASE,
        authorization_ref=REF,
        authorization=base,
        connector_id="connector-example",
        selector_type=target[0],
        selector=target[1],
        subject_class=base.get("subject_class", "S2"),
        clock=CLOCK,
        chain=chain,
        bystanders={"reach": "named_selector_only"},
        incidental_estimate=0,
        preflight_passed=True,
    )
    kw.update(over)
    return sg.Request(**kw)


def seed_hop():
    return sg.Hop(SEED[0], SEED[1], relation="seed")


def one_hop(**over):
    kw = dict(target=HOP_1, chain=(seed_hop(),), motivated_by=CLAIM_1, adjudication_ref=ADJ)
    kw.update(over)
    return request(**kw)


def pol():
    return sg.load_policy()


# ---------------------------------------------------------------------------
# SS-14 item 6 and the stamp read
# ---------------------------------------------------------------------------


def test_live_pin_refuses_a_valid_request_at_step_1():
    """Today's pin: a complete, valid, unexpired record does not unlock item 6."""
    p = pol()
    d = sg.evaluate(request())
    assert not d.permits
    assert d.value == p.value_of(1) and d.value != p.permit
    assert (d.decided_at_step, d.basis, d.never_item) == (1, "never_item", 6)
    assert d.consequence == p.ratify_refuses
    assert any("policy/subject-authorization.yaml" in r for r in d.reasons)


def test_live_pin_refuses_a_pivot_and_an_s4_request_the_same_way():
    for rq in (one_hop(), request(rec=record(subject_class="S4"))):
        d = sg.evaluate(rq)
        assert not d.permits and (d.decided_at_step, d.never_item) == (1, 6)


def test_only_a_fully_stamped_pin_permits():
    p = pol()
    with stamps(STAMPED):
        d = sg.evaluate(request())
    assert d.permits and d.value == p.permit
    assert d.consequence == p.members[p.permit]["consequence"]
    assert (d.decided_at_step, d.subject_relation, d.pivot_depth) == (6, "seed", 0)
    assert d.bystander_disposition == "refuse"


def test_every_item_6_path_and_criterion_refuses_when_its_row_is_missing():
    p = pol()
    for missing in p.ratify_paths + ["SS-5", "SS-14", "RT-1", "RT-19"]:
        with stamps(FixtureStamps(missing=[missing])):
            d = sg.evaluate(request())
        assert not d.permits, missing
        assert (d.decided_at_step, d.never_item) == (1, 6), missing


def test_preflight_not_passed_refuses_at_step_1():
    with stamps(STAMPED):
        d = sg.evaluate(request(preflight_passed=False))
    assert not d.permits and (d.decided_at_step, d.never_item) == (1, 6)
    assert any("preflight" in r for r in d.reasons)


def test_an_unreadable_pin_refuses_with_sa_u15():
    p = pol()
    with stamps(FixtureStamps(readable=False)):
        d = sg.evaluate(request())
    assert not d.permits and d.held_on == ("SA-U15",)
    assert d.consequence == p.entries["SA-U15"]["refuses"]

    def boom():
        raise OSError("gone")

    saved = sg.read_stamps
    sg.read_stamps = boom
    try:
        d = sg.evaluate(request())
    finally:
        sg.read_stamps = saved
    assert not d.permits and d.held_on == ("SA-U15",)

    class Faulty(FixtureStamps):
        def item_6_reasons(self, paths, criteria):
            raise TypeError("a reader defect")

    with stamps(Faulty()):
        d = sg.evaluate(request())
    assert not d.permits and d.consequence == sg.GUARD_FAULT, "a gate that raises must refuse"


def test_an_open_entry_on_the_permit_path_holds_the_permit():
    p = pol()
    for entry in ("SA-U9", "SA-U15", "SA-U10", "SA-U16"):
        with stamps(FixtureStamps(open_entries=[entry])):
            d = sg.evaluate(request())
        assert not d.permits and entry in d.held_on, entry
        assert d.consequence == p.entries[entry]["refuses"], entry
    with stamps(FixtureStamps(open_entries=["GF-U4"])):
        assert sg.evaluate(request()).permits, "GF-U4 is not on a seed's path"
        d = sg.evaluate(one_hop())
    assert not d.permits and d.consequence == sg.PIVOT_HELD


def _with_row(item: str, file_cell: str, ratifier: str = "operator") -> str:
    """The live pin with one row appended to its Ratified table, as pin_of_record's self-test does."""
    reader = sg._load_by_path("plainsight_pin_of_record", sg.PIN_READER)
    text = reader.PIN.read_text(encoding="utf-8")
    i = text.find(reader.RATIFIED_END)
    return text[:i].rstrip("\n") + f"\n| {item} | {file_cell} | v0.1 | 2026-10-01 | unstamped | {ratifier} |\n\n" + text[i:]


def test_the_live_reader_reads_item_6_and_entry_rows_in_both_directions():
    p = pol()
    live = sg.LivePin()
    reasons = live.item_6_reasons(p.ratify_paths, p.ss_criteria + p.rt_criteria)
    assert any(r.startswith("policy/subject-authorization.yaml ") for r in reasons)
    assert not any(r.startswith("doctrine/SUBJECT_SELECTION.md ") for r in reasons)
    stamped = sg.LivePin(_with_row("the compiled policy, whole artifact", "`policy/subject-authorization.yaml`"))
    after = stamped.item_6_reasons(p.ratify_paths, p.ss_criteria + p.rt_criteria)
    assert not any(r.startswith("policy/subject-authorization.yaml ") for r in after)
    assert len(after) == len(reasons) - 1
    assert not any(live.entry_resolved(e) for e in list(p.entries) + ["GF-U4"])
    row = "SA-U4 expires_on against retain_until"
    assert sg.LivePin(_with_row(row, "`policy/subject-authorization.yaml`")).entry_resolved("SA-U4")
    assert not sg.LivePin(_with_row(row + " (withdrawn)", "`policy/subject-authorization.yaml`")).entry_resolved("SA-U4")
    assert not sg.LivePin(_with_row(row, "`conformance/gate/README.md`")).entry_resolved("SA-U4")
    assert not sg.LivePin(_with_row(row, "`policy/subject-authorization.yaml`", "pending")).entry_resolved("SA-U4")
    assert not sg.LivePin(_with_row("SA-U40 a longer id", "`policy/subject-authorization.yaml`")).entry_resolved("SA-U4")
    assert sg.LivePin(_with_row("GF-U4 the drift predicate", "`conformance/gate/README.md`")).entry_resolved("GF-U4")


# ---------------------------------------------------------------------------
# SS-8: a present, valid authorization record unlocks no hard refusal
# ---------------------------------------------------------------------------


def test_valid_record_does_not_unlock_a_hard_refusal():
    p = pol()
    cases = {
        "S4 with no baseline": (request(rec=record(subject_class="S4")), 3, "baseline_missing"),
        "S3 with no baseline": (request(rec=record(subject_class="S3")), 3, "baseline_missing"),
        "a retain disposition": (
            request(bystanders={"reach": "declared", "classes": [
                {"class": "followers", "estimate": {"method": "platform_reported_count"}, "disposition": "retain"}]}),
            6, "disposition_out_of_set"),
        "no bystander declaration": (request(bystanders=None), 6, "bystander_undeclared"),
        "a blank estimate": (request(incidental_estimate=None), None, "incidental_estimate_missing"),
        "unestimable with no reason": (request(incidental_estimate="unestimable"), None, "incidental_estimate_missing"),
    }
    with stamps(STAMPED):
        assert sg.evaluate(request()).permits, "the baseline request must permit, or nothing below is proven"
        for name, (rq, step, basis) in cases.items():
            d = sg.evaluate(rq)
            assert not d.permits, name
            assert (d.decided_at_step, d.basis) == (step, basis), name
            assert d.value == p.value_of(1), name
        # The incidental rule: an S5 selector, or a chain through an incidental hop.
        for rq in (request(subject_class="S5"),
                   one_hop(chain=(sg.Hop(SEED[0], SEED[1], relation="incidental"),))):
            d = sg.evaluate(rq)
            assert not d.permits and d.code == "SUBJECT_NOT_AUTHORIZED" and d.held_on == ("GF-U2",)


def test_a_class_whose_entry_options_the_guard_does_not_implement_refuses_whatever_the_pin_says():
    """SG-R17: a dated row for SA-U2 or SA-U5 may ratify a hold, so it unlocks nothing here."""
    p = pol()
    with stamps(STAMPED):
        assert sg.evaluate(request()).permits, "S2 under the same stamps must permit, or nothing below is proven"
        for cls, entry in (("N0", "SA-U2"), ("L0", "SA-U2"), ("S1", "SA-U5")):
            d = sg.evaluate(request(rec=record(subject_class=cls)))
            assert not d.permits, cls
            assert (d.decided_at_step, d.basis) == (3, "class_unavailable"), cls
            assert d.held_on[0] == entry and d.consequence == p.entries[entry]["refuses"], cls


def test_a_class_outside_the_authorizable_set_refuses_at_step_3():
    with stamps(STAMPED):
        d = sg.evaluate(request(rec=record(subject_class="S9")))
    assert not d.permits and d.consequence != sg.GUARD_FAULT
    assert (d.decided_at_step, d.basis) == (3, "class_unavailable")


def test_a_pivot_whose_chain_starts_outside_the_record_refuses_at_step_4():
    """SS-5 and SS-9: an adjudicated chain rooted at a selector the record never named is not a pivot."""
    p = pol()
    with stamps(STAMPED):
        assert sg.evaluate(one_hop()).permits, "the same pivot from the authorized seed must permit"
        d = sg.evaluate(one_hop(chain=(sg.Hop(SEED_OTHER[0], SEED_OTHER[1], relation="seed"),)))
    assert not d.permits and d.value == p.value_of(4)
    assert (d.decided_at_step, d.basis) == (4, "selector_outside_set")
    assert any("does not start at an authorized seed" in r for r in d.reasons)


# ---------------------------------------------------------------------------
# SS-5: each of the three fields is read
# ---------------------------------------------------------------------------


def test_ss5_selectors_is_read():
    p = pol()
    with stamps(STAMPED):
        d = sg.evaluate(request(rec=record(selectors=[{"selector_type": SEED_OTHER[0], "value": SEED_OTHER[1]}])))
    assert not d.permits and d.value == p.value_of(4)
    assert (d.decided_at_step, d.basis_field, d.basis) == (4, "extension_basis", "selector_outside_set")
    assert d.consequence == p.members[p.value_of(4)]["consequence"]


def test_ss5_pivot_depth_max_is_read():
    p = pol()
    with stamps(STAMPED):
        assert sg.evaluate(one_hop()).permits
        d = sg.evaluate(one_hop(rec=record(pivot_depth_max=0)))
        assert not d.permits and (d.decided_at_step, d.basis) == (4, "pivot_depth_exceeded")
        assert d.value == p.value_of(4) and d.held_on == ()
        d = sg.evaluate(one_hop(rec=record(pivot_depth_max=1)))
        assert not d.permits and d.basis == "pivot_depth_exceeded" and d.held_on == ("GF-U4",)


def test_ss5_expires_on_is_read():
    p = pol()
    with stamps(STAMPED):
        d = sg.evaluate(request(rec=record(expires_on="2026-01-16")))
        assert not d.permits and (d.decided_at_step, d.basis) == (2, "authorization_expired")
        assert d.consequence == p.entries["SA-U1"]["refuses"]
        d = sg.evaluate(request(rec=record(expires_on="2026-01-20")))
        assert not d.permits and d.held_on[0] == "SA-U3"
        assert d.consequence == p.entries["SA-U3"]["refuses"]
        assert sg.evaluate(request(rec=record(expires_on="2026-01-21"))).permits


def test_the_record_is_refused_when_absent_partial_unbound_or_for_another_case():
    with stamps(STAMPED):
        assert sg.evaluate(request(authorization=None)).basis == "authorization_missing"
        partial = record()
        del partial["expires_on"]
        assert sg.evaluate(request(rec=partial)).basis == "authorization_incomplete"
        d = sg.evaluate(request(rec=record(purpose=None)))
        assert (d.basis, d.code, d.decided_at_step) == ("purpose_unbound", "CASE_PURPOSE_UNBOUND", None)
        assert sg.evaluate(request(rec=record(case_id=GRANT))).basis == "authorization_missing"
        assert sg.evaluate(request(subject_class="S0")).basis == "authorization_missing"
        assert sg.evaluate(request(rec=record(pivot_depth_max=True))).basis == "authorization_incomplete"


# ---------------------------------------------------------------------------
# SS-9: the chain, not the hop
# ---------------------------------------------------------------------------


def test_scope_drift_is_an_unadjudicated_hop():
    p = pol()
    middle = sg.Hop(HOP_1[0], HOP_1[1], motivated_by=CLAIM_1, adjudication_ref=None)
    rq = request(target=HOP_2, rec=record(pivot_depth_max=4), chain=(seed_hop(), middle),
                 motivated_by=CLAIM_2, adjudication_ref=ADJ)
    with stamps(STAMPED):
        d = sg.evaluate(rq)
        assert not d.permits and d.value == p.value_of(5)
        assert (d.decided_at_step, d.basis, d.code) == (5, "chain_scope_drift", "SCOPE_DRIFT_UNADJUDICATED")
        assert not sg.evaluate(one_hop(adjudication_ref=None)).permits
        adjudicated = sg.Hop(HOP_1[0], HOP_1[1], motivated_by=CLAIM_1, adjudication_ref=ADJ)
        third = sg.Hop(SEED_OTHER[0], SEED_OTHER[1], motivated_by=CLAIM_2, adjudication_ref=ADJ)
        ok = request(target=HOP_2, rec=record(pivot_depth_max=4), chain=(seed_hop(), adjudicated, third),
                     motivated_by=CLAIM_3, adjudication_ref=ADJ)
        d = sg.evaluate(ok)
        assert d.permits and (d.subject_relation, d.pivot_depth) == ("pivot", 3)


# ---------------------------------------------------------------------------
# The values, the codes and the sentences are the compiled policy's
# ---------------------------------------------------------------------------


def test_values_are_read_from_the_policy_rather_than_written_in_the_guard():
    doc = sg._yaml_load(sg.POLICY)
    renamed = copy.deepcopy(doc)
    gate = renamed["subject_authorization"]["gate"]
    rename = {"PERMITTED": "PERMITTED-AS-COMPILED", "REQUIRES_EXTENSION": "EXTENSION-AS-COMPILED"}
    gate["values"]["enum"] = [rename.get(v, v) for v in gate["values"]["enum"]]
    for m in gate["values"]["members"]:
        m["value"] = rename.get(m["value"], m["value"])
    for s in gate["evaluation_order"]["steps"]:
        s["returns"] = rename.get(s["returns"], s["returns"])
    with stamps(STAMPED), policy(renamed):
        assert sg.evaluate(request()).value == "PERMITTED-AS-COMPILED"
        assert sg.evaluate(one_hop(rec=record(pivot_depth_max=0))).value == "EXTENSION-AS-COMPILED"
    broken = copy.deepcopy(doc)
    broken["subject_authorization"]["gate"]["evaluation_order"]["steps"].pop()
    with stamps(STAMPED), policy(broken):
        d = sg.evaluate(request())
    assert not d.permits and d.consequence == sg.POLICY_UNREADABLE


def test_no_selector_value_escapes_a_request_a_decision_or_a_payload():
    rendered = []
    for state in (None, STAMPED):
        ctx = stamps(state) if state else contextlib.nullcontext()
        with ctx:
            for rq in (request(), one_hop(), request(rec=record(subject_class="S4")), request(bystanders=None),
                       request(subject_class="S5"), one_hop(adjudication_ref=None)):
                d = sg.evaluate(rq)
                rendered += [repr(rq), repr(d), json.dumps(d.to_collect_payload()), d.consequence, *d.reasons]
                rendered += [repr(h) for h in rq.chain]
    for text in rendered:
        for value in PLACEHOLDERS:
            assert value not in text


def test_the_decision_serializes_as_a_collect_event_a_run_can_be_parented_on():
    from jsonschema import Draft202012Validator

    validator = Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8")))

    def event(d, n):
        return d.to_collect_event(case_id=CASE, event_id=f"00000000-0000-5000-8000-00000000000{n}",
                                  ts="2026-01-20T09:00:00Z", platform_id="isolated-01",
                                  sw_version="0.1.0", grant_event_id=GRANT)

    decisions = [sg.evaluate(request())]
    with stamps(STAMPED):
        decisions += [sg.evaluate(request()), sg.evaluate(one_hop()),
                      sg.evaluate(one_hop(rec=record(pivot_depth_max=0))),
                      sg.evaluate(request(rec=record(expires_on="2026-01-16")))]
        held = sg.evaluate(request(subject_class="S5"))
    for n, d in enumerate(decisions):
        e = event(d, n)
        errors = [err.message for err in validator.iter_errors(e)]
        assert not errors, (d.value, errors)
        assert e["source"]["producer"] == sg.PRODUCER
    permit = decisions[1].to_collect_payload()
    for key in ("decision", "authorization_ref", "connector_id", "target_selector_type", "subject_relation",
                "pivot_depth", "decided_at_step", "incidental_estimate", "bystander_disposition"):
        assert key in permit, key
    assert list(validator.iter_errors(event(held, 9))), "a held refusal must not validate until its entry is stamped"


def test_importing_the_module_reads_no_file_and_changes_no_path():
    def refuse_open(*a, **k):
        raise AssertionError("runner.subject_guard opened a file at import")

    path_before = list(sys.path)
    saved = sys.modules.pop("runner.subject_guard")
    saved_open, saved_io_open = builtins.open, io.open
    builtins.open = io.open = refuse_open
    try:
        fresh = importlib.import_module("runner.subject_guard")
    finally:
        builtins.open, io.open = saved_open, saved_io_open
        sys.modules["runner.subject_guard"] = saved
    assert sys.path == path_before
    assert not any(isinstance(v, (sg.Policy, sg.LivePin)) for v in vars(fresh).values())


def test_a_request_without_a_zone_on_its_clock_cannot_be_built():
    try:
        request(clock=dt.datetime(2026, 1, 20, 9, 0))
    except ValueError as exc:
        assert "zone" in str(exc)
    else:
        raise AssertionError("a naive clock was accepted")


if __name__ == "__main__":
    failed = 0
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    for name, fn in tests:
        try:
            fn()
        except Exception as exc:  # report every test, then fail
            failed += 1
            print(f"  FAILED  {name}: {exc.__class__.__name__}: {exc}")
        else:
            print(f"  ok      {name}")
    print(f"test_subject_guard: {len(tests) - failed} of {len(tests)} passed")
    sys.exit(1 if failed else 0)
