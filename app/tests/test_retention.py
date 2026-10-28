"""Retention columns: durations from policy, and RT-6's incidental clock."""

from __future__ import annotations

import datetime as dt
import hashlib

import yaml

from app import config
from app.store import retention
from app.tests.helpers import CASE, corpus_events, named


#: The tracked policy, read here independently of the module the store uses,
#: so a store pointed at another file disagrees with it.
TRACKED_POLICY = config.REPO_ROOT / "policy" / "retention.yaml"


def _policy():
    return yaml.safe_load(TRACKED_POLICY.read_text(encoding="utf-8"))["retention"]


def check_durations_follow_policy(ctx):
    pol = _policy()
    s = ctx.built()
    reg = s.registry(CASE)
    assert reg["case_ttl_days"] == pol["case_ttl"]["default_days"]
    assert reg["extension_days"] == pol["case_ttl"]["extension_days"]
    assert reg["ceiling_days"] == pol["case_ttl"]["ceiling_days"]
    assert reg["incidental_ttl_days"] == pol["incidental"]["ttl_days"]
    assert reg["policy_sha256"] == hashlib.sha256(TRACKED_POLICY.read_bytes()).hexdigest()


def break_tmp_policy_ttl_5(ctx):
    doc = yaml.safe_load(TRACKED_POLICY.read_text(encoding="utf-8"))
    doc["retention"]["case_ttl"]["default_days"] = 5
    tmp = ctx.tmp / "retention.yaml"
    tmp.write_text(yaml.safe_dump(doc), encoding="utf-8")
    ctx.mp.setattr(retention, "POLICY", tmp)


def test_durations_follow_policy(ctx):
    check_durations_follow_policy(ctx)


def check_incidental_expiry(ctx):
    pol = _policy()
    events = corpus_events()
    named(events, "collect-permitted")["payload"]["subject_relation"] = "incidental"
    s = ctx.built("incidental", events)
    reg = s.registry(CASE)
    first = named(events, "authorize-grant")["event"]["ts"]
    initial = retention.initial_retain_until(first, pol["case_ttl"]["default_days"])
    assert reg["retain_until"] != initial, "the corpus RETENTION_EXTENSION moved retain_until"
    for row in s.conn.execute("SELECT observed_at, expires_at, subject_relation FROM claim"):
        assert row["subject_relation"] == "incidental"
        clock = retention.parse_ts(row["observed_at"]) + dt.timedelta(days=pol["incidental"]["ttl_days"])
        want = min(retention.parse_ts(retention.date_instant(initial)), clock)
        assert retention.parse_ts(row["expires_at"]) == want, "the extension does not move incidental content"
    seed = ctx.built("seed")
    for row in seed.conn.execute("SELECT expires_at, subject_relation FROM claim"):
        assert row["subject_relation"] == "seed"
        assert row["expires_at"] == retention.date_instant(seed.registry(CASE)["retain_until"])


def break_incidental_from_retain_until(ctx):
    ctx.mp.setattr(retention, "expiry", lambda relation, retain_until, observed_at, days: retention.date_instant(retain_until))


def test_incidental_expiry(ctx):
    check_incidental_expiry(ctx)


def test_retention_line_renders_a_consequence(ctx):
    s = ctx.built()
    line = retention.retention_line(s.registry(CASE), dt.datetime(2026, 10, 28, tzinfo=dt.timezone.utc))
    assert line == "past retain_until · synthetic stratum-4 material, no sweep acts on LOCAL"


def test_node_expiry_is_the_latest_claim(ctx):
    s = ctx.built()
    latest = s.conn.execute("SELECT MAX(expires_at) FROM claim").fetchone()[0]
    for row in s.conn.execute("SELECT node_id, expires_at FROM node"):
        assert row["expires_at"] == latest, "every corpus node is held by seed claims"


CONTROLS = [
    ("a tmp policy with ttl 5", check_durations_follow_policy, break_tmp_policy_ttl_5),
    ("incidental expiry computed from retain_until", check_incidental_expiry, break_incidental_from_retain_until),
]
