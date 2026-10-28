"""connectors/sherlock/adapter.py against its own cassettes. Rung 1, replay only.

Every username here is a placeholder or a random string made in memory by the
test that uses it, so no value is written to this file. No test runs Sherlock,
Docker or any network request: every test that calls invoke() first replaces
subprocess.run, and the one that reaches argv does so through a decision
runner.subject_guard.evaluate() returned under a fixture stamp state.

Run with: python -m pytest connectors -q
"""

from __future__ import annotations

import datetime as dt
import importlib.util
import json
import secrets
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "connectors" / "sherlock"
CASSETTES = HERE / "cassettes"
for p in (str(ROOT), str(ROOT / "tools")):
    if p not in sys.path:
        sys.path.insert(0, p)

import validate as V  # noqa: E402  tools/validate.py, rung 2's grader
from runner import subject_guard as sg  # noqa: E402

_spec = importlib.util.spec_from_file_location("plainsight_sherlock_adapter_under_test", HERE / "adapter.py")
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)

KP, KN, OTHER = "<institutional_handle>", "<random_nonexistent_string>", "<cast_username>"
CASE = "77c83c13-2bce-5db3-8356-4785b2403fe7"
GRANT = "3d502dfd-6a3f-5e00-a5c8-0f1688a5c277"
DECISION = "99cefd34-ca6e-5766-81de-b8f7e48179cb"
AUTH = "3011f685-7d03-5e27-95a0-3ce433995e2e"


def capture(name: str) -> dict:
    return A.read_cassette(CASSETTES / name)


def parsed(name: str) -> dict:
    return A.parse(**capture(name)["parse"])


def by_site(p: dict) -> dict:
    return {i["site"]: i for i in p["items"]}


def context(inputs: dict, seed: str = "t") -> dict:
    return dict(case_id=CASE, decision_event_id=DECISION, motivated_by=None, inputs=inputs,
                manifest_hash="sha256:" + "b" * 64, argv_template=A.command_template(),
                egress_identity="replay-egress", platform_id="replay-isolated", sw_version="test",
                ts="2026-01-15T10:06:00Z", duration_ms=1000, id_seed=seed)


def replay_parents() -> list[dict]:
    common = {"pse_version": "pse-event-0.1", "derived_from": "zmeta-event-1.0", "case_id": CASE}
    grant = dict(common, event={"event_id": GRANT, "event_type": "AUTHORIZE_EVENT", "event_subtype": "GRANT",
                                "ts": "2026-01-15T10:00:00Z"},
                 source={"platform_id": "x", "environment": "ISOLATED", "producer": "analyst-example"},
                 payload={"act": "GRANT", "authorization_ref": AUTH, "subject_class": "S2", "expires_on": "2026-02-14",
                          "pivot_depth_max": 2, "authorized_by": "analyst-example", "purpose_hash": "sha256:" + "a" * 64})
    decision = dict(common, event={"event_id": DECISION, "event_type": "COLLECT_EVENT", "event_subtype": "PERMITTED",
                                   "ts": "2026-01-15T10:03:00Z"},
                    source={"platform_id": "x", "environment": "ISOLATED", "producer": "runner-subject-guard"},
                    payload={"decision": "PERMITTED", "authorization_ref": AUTH, "connector_id": "sherlock",
                             "target_selector_type": "username_string", "subject_relation": "seed", "pivot_depth": 0,
                             "decided_at_step": 6, "incidental_estimate": 0, "bystander_disposition": "refuse",
                             "motivated_by": None},
                    lineage={"based_on": [GRANT], "transform": None})
    return [grant, decision]


# ---------------------------------------------------------------------------
# parse
# ---------------------------------------------------------------------------


def test_known_positive_outcomes_follow_the_table():
    p = parsed("known_positive")
    assert p["adapter_state"] == "ok" and p["problems"] == []
    got = {s: (i["outcome"], i["negative_class"]) for s, i in by_site(p).items()}
    assert got == {
        "1337x": ("error", None),
        "Discord": ("ambiguous", None),
        "GitHub": ("hit", None),
        "GitLab": ("miss", A.NEG_AVAILABLE),
        "HackerNews": ("throttled", None),
        "Instagram": ("hit", None),
        "LinkedIn": ("ambiguous", None),
        "ResearchGate": ("miss", A.NEG_ILLEGAL),
        "Slides": ("miss", A.NEG_AVAILABLE),
        "Steam Community (User)": ("throttled", None),
        "Trakt": ("hit", None),
        "Twitter": ("error", None),
    }


def test_claimed_429_is_throttled_and_never_a_claim():
    """The Steam shape: a rate-limit page on a message site scores Claimed."""
    steam = by_site(parsed("known_positive"))["Steam Community (User)"]
    assert (steam["exists"], steam["http_status"], steam["outcome"]) == ("Claimed", 429, "throttled")
    events = A.emit(parsed("known_positive"), context({"username": KP}))
    rows_claimed = {e["payload"]["source_ref"]["item_id"] for e in events if e["event"]["event_type"] == "EXTRACT_EVENT"}
    steam_item = [e for e in events if e["payload"].get("locator") == "sherlock-site:Steam Community (User)"][0]
    assert steam_item["payload"]["item_id"] not in rows_claimed


def test_illegal_row_has_empty_cells_and_is_a_negative():
    rg = by_site(parsed("known_positive"))["ResearchGate"]
    assert rg["http_status"] is None and rg["response_time_s"] is None and rg["outcome"] == "miss"


def test_unknown_row_reads_the_question_status_and_the_stdout_context():
    tw = by_site(parsed("known_positive"))["Twitter"]
    assert tw["http_status"] == "?" and tw["outcome"] == "error"
    assert tw["unknown_context"] == "Error Connecting"
    assert by_site(parsed("known_negative"))["Twitter"]["unknown_context"] == "Timeout Error"


def test_available_on_the_sites_own_error_code_is_a_negative_and_999_is_not():
    p = by_site(parsed("known_positive"))
    assert p["Slides"]["http_status"] == 204 and p["Slides"]["outcome"] == "miss"
    assert p["LinkedIn"]["http_status"] == 999 and p["LinkedIn"]["outcome"] == "ambiguous"


def test_quality_and_exposure_facts_ride_on_the_parsed_item():
    p = by_site(parsed("known_positive"))
    assert (p["Instagram"]["probe_host"], p["Instagram"]["method"], p["Instagram"]["error_type"]) == \
        ("imginn.com", "HEAD", "status_code")
    assert p["Twitter"]["probe_host"] == "nitter.privacydev.net"
    assert (p["1337x"]["method"], p["1337x"]["error_type"]) == ("GET", "message")
    assert p["GitHub"]["probe_host"] is None and p["GitHub"]["method"] == "HEAD"


def test_crlf_and_lf_exports_read_the_same():
    cap = capture("known_positive")["parse"]
    assert "\r\n" in cap["csv_text"]
    lf = dict(cap, csv_text=cap["csv_text"].replace("\r\n", "\n"))
    assert A.parse(**cap)["items"] == A.parse(**lf)["items"]


def test_both_preamble_shapes_are_skipped():
    kp, kn = parsed("known_positive"), parsed("known_negative")
    assert kp["stdout"]["preamble_lines"] == 2 and kp["stdout"]["update_check"] == "newer_version_reported"
    assert kn["stdout"]["preamble_lines"] == 1 and kn["stdout"]["update_check"] == "failed"
    assert kp["exclusions_applied"] and kn["exclusions_applied"]


def test_known_negative_has_no_hit_and_reads_as_empty():
    p = parsed("known_negative")
    assert p["adapter_state"] == "empty"
    assert not [i for i in p["items"] if i["outcome"] == "hit"]
    assert sum(1 for i in p["items"] if i["negative_class"] == A.NEG_AVAILABLE) == 6


def test_exit_2_is_an_error_with_no_item():
    p = parsed("argparse_error")
    assert p["adapter_state"] == "error" and p["items"] == [] and p["exit_code"] == 2


def test_stdout_and_csv_disagreeing_is_malformed():
    cap = capture("known_positive")["parse"]
    wrong_count = dict(cap, stdout_text=cap["stdout_text"].replace("with 5 results", "with 4 results"))
    assert A.parse(**wrong_count)["adapter_state"] == "malformed"
    wrong_status = dict(cap, stdout_text=cap["stdout_text"].replace("[-] GitLab: Not Found!", "[+] GitLab: x"))
    assert A.parse(**wrong_status)["adapter_state"] == "malformed"
    no_csv = dict(cap, csv_text=None)
    assert A.parse(**no_csv)["adapter_state"] == "malformed"


def test_a_claimed_site_on_the_measured_exclusion_list_is_ambiguous():
    """Its presence means the exclusions fetch failed; 41 of 52 claim a random string."""
    cap = capture("known_positive")["parse"]
    row = f"{KP},Reddit,https://www.reddit.com/,https://www.reddit.com/user/{KP},Claimed,200,0.5\r\n"
    out = f"[+] Reddit: https://www.reddit.com/user/{KP}\n"
    planted = dict(cap, csv_text=cap["csv_text"] + row,
                   stdout_text=cap["stdout_text"].replace("\n\n[*] Search completed with 5", "\n" + out + "\n[*] Search completed with 6"))
    p = A.parse(**planted)
    assert p["adapter_state"] == "ok" and by_site(p)["Reddit"]["outcome"] == "ambiguous"
    assert p["exclusions_applied"] is False


def test_a_site_whose_url_has_no_username_slot_is_read_and_its_claimed_row_is_ambiguous():
    """Discord's url_user is its bare host on every row (A1.5, SH-R15). A Claimed
    row there says the name is taken at registration, not that a profile exists."""
    kp = by_site(parsed("known_positive"))["Discord"]
    assert (kp["exists"], kp["http_status"], kp["outcome"], kp["url_has_username_slot"]) == \
        ("Claimed", 200, "ambiguous", False)
    kn = by_site(parsed("known_negative"))["Discord"]
    assert (kn["outcome"], kn["negative_class"]) == ("miss", A.NEG_AVAILABLE)
    # Control: the same bare url on a site that has a slot is still refused.
    cap = capture("known_positive")["parse"]
    moved = dict(cap, csv_text=cap["csv_text"].replace(
        f"{KP},GitLab,https://gitlab.com/,https://gitlab.com/{KP},", f"{KP},GitLab,https://gitlab.com/,https://gitlab.com,"))
    assert A.parse(**moved)["adapter_state"] == "malformed"


def test_a_run_whose_every_request_failed_is_an_error_not_a_block():
    """Unknown is a request that raised (A1.7). An egress outage is not the platforms blocking."""
    header = ",".join(A.CSV_COLUMNS) + "\r\n"
    rows = (f"{KN},GitHub,https://www.github.com/,https://www.github.com/{KN},Unknown,?,\r\n"
            f"{KN},Twitter,https://x.com/,https://x.com/{KN},Unknown,?,\r\n")
    out = (f"[*] Checking username {KN} on:\n\n[-] GitHub: Error Connecting \n[-] Twitter: Timeout Error \n\n"
           "[*] Search completed with 0 results\n")
    p = A.parse(header + rows, out, 0)
    assert p["problems"] == [] and p["adapter_state"] == "error"
    waf_row = f"{KN},1337x,https://www.1337x.to/,https://www.1337x.to/user/{KN}/,WAF,403,0.09\r\n"
    waf_out = out.replace("\n\n[-] GitHub", "\n\n[-] 1337x: Blocked by bot detection (proxy may help)\n[-] GitHub")
    assert A.parse(header + waf_row + rows, waf_out, 0)["adapter_state"] == "blocked"


def test_a_site_named_twice_or_a_result_line_printed_twice_is_malformed():
    """Sherlock 0.16.1 keys its results by site, so a repeated site is a malformed capture."""
    cap = capture("known_positive")["parse"]
    assert A.parse(**cap)["adapter_state"] == "ok"
    lines = cap["csv_text"].split("\r\n")
    gitlab = [ln for ln in lines if ",GitLab," in ln][0]
    github = [ln for ln in lines if ",GitHub," in ln][0]
    csv_only = dict(cap, csv_text=cap["csv_text"] + gitlab + "\r\n")
    assert A.parse(**csv_only)["adapter_state"] == "malformed"
    both = dict(cap, csv_text=cap["csv_text"] + github + "\r\n", stdout_text=cap["stdout_text"].replace(
        "\n\n[*] Search completed with 5", f"\n[+] GitHub: https://www.github.com/{KP}\n\n[*] Search completed with 6"))
    assert A.parse(**both)["adapter_state"] == "malformed"
    stdout_only = dict(cap, stdout_text=cap["stdout_text"].replace(
        "[-] GitLab: Not Found!\n", "[-] GitLab: Not Found!\n[-] GitLab: Not Found!\n"))
    assert A.parse(**stdout_only)["adapter_state"] == "malformed"


# ---------------------------------------------------------------------------
# emit
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name,inp,count,claims,state", [
    ("known_positive", KP, 17, 3, "ok"),
    ("known_negative", KN, 11, 0, "empty"),
    ("argparse_error", OTHER, 2, 0, "error"),
])
def test_emitted_events_grade_clean_under_tools_validate(name, inp, count, claims, state):
    events = A.emit(parsed(name), context({"username": inp}, seed=name))
    assert len(events) == count
    assert sum(1 for e in events if e["event"]["event_type"] == "EXTRACT_EVENT") == claims
    end = [e for e in events if e["event"]["event_subtype"] == "RUN_END"][0]
    assert end["payload"]["error_class"] == state
    pol = V.load_policy()
    index = V.Index(replay_parents() + events)
    for e in events:
        codes, _ = V.check_event(e, pol, index, {"analyst-example"})
        assert codes == set(), (e["event"]["event_subtype"], codes)


def test_claims_carry_the_items_platform_token_and_the_placeholder_unchanged():
    """SH-R18: the value is the token of the site the claim's ITEM locator names, a slash, and the cell."""
    events = A.emit(parsed("known_positive"), context({"username": KP}))
    claims = [e for e in events if e["event"]["event_type"] == "EXTRACT_EVENT"]
    assert {c["payload"]["selector_type"] for c in claims} == {"handle"}
    items = {e["payload"]["item_id"]: e for e in events if e["event"]["event_subtype"] == "ITEM"}
    pairs = sorted((items[c["payload"]["source_ref"]["item_id"]]["payload"]["locator"], c["payload"]["value"])
                   for c in claims)
    assert [p[0] for p in pairs] == ["sherlock-site:GitHub", "sherlock-site:Instagram", "sherlock-site:Trakt"]
    for locator, value in pairs:
        site = locator.split(":", 1)[1]
        assert value == f"{A.platform_token(site)}/{KP}"
    assert [p[1].split("/", 1)[0] for p in pairs] == ["github", "instagram", "trakt"]


@pytest.mark.parametrize("site,token", [
    ("GitHub", "github"),
    ("Steam Community (User)", None),
    ("Steam Community (Group)", None),
    ("Diskusjon.no", "diskusjon_no"),
    ("1337x", None),
    ("9GAG", None),
    ("", None),
    ("---", None),
])
def test_platform_token_is_derived_from_the_site_name_alone(site, token):
    assert A.platform_token(site) == token


def test_every_site_at_the_pinned_commit_gives_a_distinct_token_or_none():
    """SH-R18 against site_facts.json: no two sites share a token, and exactly the
    four names that begin with a digit and the five carrying a parenthesised
    qualifier give none."""
    facts = json.loads((HERE / "site_facts.json").read_text(encoding="utf-8"))
    tokens = {name: A.platform_token(name) for name in facts["sites"]}
    named = [t for t in tokens.values() if t is not None]
    assert len(named) == len(set(named))
    assert sorted(n for n, t in tokens.items() if t is None) == [
        "1337x", "2Dimensions", "7Cups", "9GAG", "Genius (Artists)", "Genius (Users)", "HackenProof (Hackers)",
        "Steam Community (Group)", "Steam Community (User)"]
    assert all(A.PLATFORM_TOKEN_RE.match(t) for t in named)


def test_no_token_is_an_endpoint_qualifier_of_another_sites_name():
    """SH-R18: an endpoint qualifier never becomes part of a platform token, so one
    platform cannot carry two tokens that differ only by the qualifier, and a group
    or artist directory is never a handle's platform."""
    facts = json.loads((HERE / "site_facts.json").read_text(encoding="utf-8"))
    for name in facts["sites"]:
        if "(" in name or ")" in name:
            assert A.platform_token(name) is None, name
            base = A.platform_token(name.split("(", 1)[0])
            assert base is None or base not in {A.platform_token(n) for n in facts["sites"]}, name


def test_a_claimed_2xx_row_on_a_qualified_site_is_ambiguous_and_never_a_claim():
    cap = capture("known_positive")["parse"]
    line = next(ln for ln in cap["csv_text"].splitlines() if ",Steam Community (User)," in ln)
    assert ",Claimed,429," in line
    csv_text = cap["csv_text"].replace(line, line.replace(",Claimed,429,", ",Claimed,200,"), 1)
    p = A.parse(csv_text=csv_text, stdout_text=cap["stdout_text"], exit_code=0)
    assert p["problems"] == []
    row = by_site(p)["Steam Community (User)"]
    assert (row["exists"], row["platform_token"], row["outcome"]) == ("Claimed", None, "ambiguous")
    events = A.emit(p, context({"username": KP}))
    assert sum(1 for e in events if e["event"]["event_type"] == "EXTRACT_EVENT") == 3


def test_a_claimed_row_on_a_site_with_no_token_is_ambiguous_and_never_a_claim():
    cap = capture("known_positive")["parse"]
    csv_text = cap["csv_text"].replace(
        "1337x,https://www.1337x.to/,https://www.1337x.to/user/<institutional_handle>/,WAF,403,",
        "1337x,https://www.1337x.to/,https://www.1337x.to/user/<institutional_handle>/,Claimed,200,", 1)
    stdout = cap["stdout_text"].replace(
        "[-] 1337x: Blocked by bot detection (proxy may help)",
        f"[+] 1337x: https://www.1337x.to/user/{KP}/", 1).replace(
        "Search completed with 5 results", "Search completed with 6 results", 1)
    p = A.parse(csv_text=csv_text, stdout_text=stdout, exit_code=0)
    assert p["problems"] == []
    row = by_site(p)["1337x"]
    assert (row["exists"], row["platform_token"], row["outcome"]) == ("Claimed", None, "ambiguous")
    events = A.emit(p, context({"username": KP}))
    assert sum(1 for e in events if e["event"]["event_type"] == "EXTRACT_EVENT") == 3


def test_emit_refuses_a_hit_on_a_site_with_no_token_rather_than_inventing_one():
    p = parsed("known_positive")
    for item in p["items"]:
        if item["site"] == "1337x":
            item["outcome"], item["negative_class"] = "hit", None
    with pytest.raises(A.AdapterRefusal) as exc:
        A.emit(p, context({"username": KP}))
    assert "SH-R18" in str(exc.value) and KP not in str(exc.value)


@pytest.mark.parametrize("inputs", [{}, {"username": None}, {"username": "  "}])
def test_emit_refuses_a_missing_input(inputs):
    with pytest.raises(A.AdapterRefusal) as exc:
        A.emit(parsed("known_positive"), context(inputs))
    assert exc.value.code == "PAYLOAD_FIELD_MISSING" and exc.value.adapter_state == "malformed"


def test_emit_refuses_a_capture_for_another_input_and_never_prints_either_value():
    with pytest.raises(A.AdapterRefusal) as exc:
        A.emit(parsed("known_positive"), context({"username": OTHER}))
    assert exc.value.code == "SUBJECT_NOT_AUTHORIZED"
    assert KP not in str(exc.value) and OTHER not in str(exc.value)


def test_only_a_miss_carries_a_negative_class_and_every_class_is_the_manifests():
    """spec/layer-model.yaml draws negative_class from distinguishable_negatives when outcome is miss."""
    import yaml

    manifest = yaml.safe_load((HERE / "manifest.yaml").read_text(encoding="utf-8"))
    declared = set(manifest["distinguishable_negatives"])
    assert set(A.NEGATIVE_CLASSES) == declared
    for name, inp in (("known_positive", KP), ("known_negative", KN)):
        events = A.emit(parsed(name), context({"username": inp}, seed=name))
        for e in events:
            if e["event"]["event_subtype"] != "ITEM":
                continue
            pl = e["payload"]
            if "negative_class" in pl:
                assert pl["outcome"] == "miss" and pl["negative_class"] in declared, pl["locator"]
    items = {e["payload"]["locator"]: e["payload"] for e in A.emit(parsed("known_positive"), context({"username": KP}))
             if e["event"]["event_subtype"] == "ITEM"}
    for site in ("1337x", "Twitter"):
        assert items[f"sherlock-site:{site}"]["outcome"] == "error"
        assert "negative_class" not in items[f"sherlock-site:{site}"]


def test_cassette_values_name_every_username_cell():
    cells = A.cassette_values(CASSETTES / "known_positive")
    assert len(cells) == 13 and {v for _, v in cells} == {KP}


def test_site_facts_agree_with_the_audit():
    facts = json.loads((HERE / "site_facts.json").read_text(encoding="utf-8"))
    sites = facts["sites"]
    assert len(sites) == 481 and len(facts["fp_exclusions_measured"]["names"]) == 52
    assert sum(1 for s in sites.values() if s["method"] == "HEAD") == 303
    assert sum(1 for s in sites.values() if s["probe_host"]) == 21
    assert sum(1 for s in sites.values() if s["error_type"] == "status_code") == 327
    assert facts["url_without_username_slot"]["names"] == ["Discord", "Diskusjon.no", "Kvinneguiden"]


# ---------------------------------------------------------------------------
# invoke
# ---------------------------------------------------------------------------


def _boom(*args, **kwargs):
    raise AssertionError("a process was started")


def _refused_decision():
    req = sg.Request(case_id=CASE, authorization_ref=None, authorization=None, connector_id="sherlock",
                     selector_type="username_string", selector=OTHER, subject_class="S2",
                     clock=dt.datetime(2026, 1, 20, 9, 0, tzinfo=dt.timezone.utc))
    d = sg.evaluate(req)
    assert not d.permits
    return d


class _SaysPermitted:
    permits = True
    connector_id = "sherlock"
    target_selector_type = "username_string"


def test_invoke_without_a_permit_starts_no_process(monkeypatch):
    calls = []
    monkeypatch.setattr(A.subprocess, "run", lambda *a, **k: calls.append(1) or _boom())
    monkeypatch.setattr(A.subprocess, "Popen", lambda *a, **k: calls.append(1) or _boom())
    value = "r" + secrets.token_hex(6)
    for decision in (None, _refused_decision(), _SaysPermitted()):
        with pytest.raises(A.InvokeRefused) as exc:
            A.invoke(decision, {"username": value})
        assert exc.value.code == "SUBJECT_NOT_AUTHORIZED" and value not in str(exc.value)
    assert calls == []


class _AllStamped:
    readable = True

    def item_6_reasons(self, paths, criteria):
        return []

    def entry_resolved(self, entry_id):
        return True


def _permitted_decision(monkeypatch, value, selector_type="username_string"):
    monkeypatch.setattr(sg, "read_stamps", lambda: _AllStamped())
    record = {"case_id": CASE, "subject_class": "S2",
              "selectors": [{"selector_type": selector_type, "value": value}],
              "pivot_depth_max": 2, "purpose": "Score the sweep adapter against the designed cast.",
              "evidence_ref": {"kind": "cast_manifest_entry", "ref": "synthetic/GROUND_TRUTH.yaml"},
              "authorized_by": "analyst-example", "authorized_on": "2026-01-15", "expires_on": "2026-02-14"}
    req = sg.Request(case_id=CASE, authorization_ref=AUTH, authorization=record, connector_id="sherlock",
                     selector_type=selector_type, selector=value, subject_class="S2",
                     clock=dt.datetime(2026, 1, 20, 9, 0, tzinfo=dt.timezone.utc),
                     bystanders={"reach": "named_selector_only"}, incidental_estimate=0, preflight_passed=True)
    decision = sg.evaluate(req)
    assert decision.permits, decision.consequence
    return decision


def test_invoke_with_a_permit_builds_argv_from_the_manifest_template(monkeypatch, tmp_path):
    value = "r" + secrets.token_hex(6)
    decision = _permitted_decision(monkeypatch, value)
    seen = {}

    def fake_run(argv, **kw):
        seen["argv"], seen["cwd"] = argv, kw.get("cwd")
        return subprocess.CompletedProcess(argv, 2, b"", b"usage")

    monkeypatch.setattr(A.subprocess, "run", fake_run)
    out = A.invoke(decision, {"username": value}, workdir=tmp_path)
    template = A.command_template().split(" ")
    assert seen["argv"][:-1] == template[:-1] and seen["argv"][-1] == value
    assert seen["argv"][-2] == "--" and seen["cwd"] == tmp_path
    assert out["parse"]["exit_code"] == 2 and out["parse"]["csv_text"] is None


@pytest.mark.parametrize("make", [
    lambda v: "<cast_username>",
    lambda v: "-" + v,
    lambda v: v + "{?}",
    lambda v: v + " " + v,
    lambda v: v + "/" + v,
    lambda v: "..\\" + v,
    lambda v: v + ":" + v,
    lambda v: "..",
])
def test_invoke_refuses_a_value_argparse_or_sherlock_would_reinterpret(monkeypatch, make):
    value = "r" + secrets.token_hex(6)
    decision = _permitted_decision(monkeypatch, value)
    monkeypatch.setattr(A.subprocess, "run", _boom)
    bad = make(value)
    with pytest.raises(A.InvokeRefused) as exc:
        A.invoke(decision, {"username": bad})
    assert bad not in str(exc.value)


def test_invoke_removes_the_scratch_directory_it_made_on_every_path(monkeypatch, tmp_path):
    """The CSV is stratum-0 raw capture (RT-1); it must not outlive invoke() outside the case."""
    value = "r" + secrets.token_hex(6)
    decision = _permitted_decision(monkeypatch, value)
    made = []

    def mkdtemp(prefix=""):
        d = tmp_path / f"run{len(made)}"
        d.mkdir()
        made.append(d)
        return str(d)

    def writes_a_capture(argv, cwd=None, **kw):
        out = Path(cwd) / "out" / "run"
        out.mkdir(parents=True)
        (out / f"{value}.csv").write_bytes((",".join(A.CSV_COLUMNS) + "\r\n").encode("utf-8"))
        return subprocess.CompletedProcess(argv, 0, b"", b"")

    monkeypatch.setattr(A.tempfile, "mkdtemp", mkdtemp)
    monkeypatch.setattr(A.subprocess, "run", writes_a_capture)
    got = A.invoke(decision, {"username": value})
    assert got["parse"]["csv_text"].startswith("username,") and not made[0].exists()
    monkeypatch.setattr(A.subprocess, "run", _boom)
    with pytest.raises(AssertionError):
        A.invoke(decision, {"username": value})
    assert len(made) == 2 and not made[1].exists()


def test_invoke_refuses_a_permit_the_gate_gave_another_selector_type(monkeypatch):
    """SS-5: a permit authorizes the dispatch it evaluated and no other."""
    value = "r" + secrets.token_hex(6)
    decision = _permitted_decision(monkeypatch, value, selector_type="handle")
    monkeypatch.setattr(A.subprocess, "run", _boom)
    with pytest.raises(A.InvokeRefused) as exc:
        A.invoke(decision, {"username": value})
    assert "another connector or selector type" in str(exc.value)
