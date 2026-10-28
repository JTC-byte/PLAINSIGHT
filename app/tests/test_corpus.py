"""conformance/must-pass.jsonl ingested into a tmp store, counted.

The brief states 44 rows in one case. The other counts below are what the
store's projections make of that corpus, each derivable from the corpus by
reading it: they claim coverage of the projection mechanism, not the truth of
any identity in the fixture.
"""

from __future__ import annotations

import hashlib
from collections import Counter

from app import config
from app.store import door
from app.tests import helpers
from app.tests.helpers import CASE, CORPUS, count, eid_of


def check_corpus_counts(ctx):
    s = helpers.Ctx.built(ctx)
    assert count(s, "SELECT COUNT(*) FROM event_skeleton") == 44
    assert count(s, "SELECT COUNT(DISTINCT case_id) FROM event_skeleton") == 1
    assert s.cases() == [CASE]
    reg = s.registry(CASE)
    assert reg["source_path"] == config.SYNTHETIC_SOURCES[0]
    assert reg["source_sha256"] == hashlib.sha256(CORPUS.read_bytes()).hexdigest()
    assert reg["synthetic"] == 1 and reg["environment"] == "LOCAL" and reg["state"] == "open"
    strata = Counter(r[0] for r in s.conn.execute("SELECT payload_stratum FROM event_skeleton"))
    assert strata == {1: 25, 2: 19}
    assert count(s, "SELECT COUNT(*) FROM event_payload") == 25
    assert count(s, "SELECT COUNT(*) FROM run") == 1
    assert count(s, "SELECT COUNT(*) FROM item") == 2
    assert count(s, "SELECT COUNT(*) FROM claim") == 4
    assert count(s, "SELECT COUNT(*) FROM coverage_interval WHERE state = 'closed'") == 1
    kinds = Counter(r[0] for r in s.conn.execute("SELECT kind FROM node"))
    assert kinds == {"selector": 4, "entity": 1, "referenced": 2, "cluster": 2, "candidate": 1}
    edges = Counter(r[0] for r in s.conn.execute("SELECT kind FROM edge"))
    assert edges == {"observed_about": 3, "proposes": 4, "member_of": 4, "excludes": 1}
    revoked = s.conn.execute("SELECT revoked_by_event_id FROM node WHERE kind = 'cluster' AND revoked_by_event_id IS NOT NULL").fetchall()
    assert [r[0] for r in revoked] == [eid_of("adjudicate-revoke")]
    assert reg["retain_until"] == "2026-03-16" and reg["frozen_until"] == "2026-05-15"


def break_corpus_reader_drops_a_row(ctx):
    real = helpers.corpus_events
    ctx.mp.setattr(helpers, "corpus_events", lambda: real()[:-1])


def test_corpus_counts(ctx):
    check_corpus_counts(ctx)


def test_source_is_tracked_and_unmodified():
    rel = config.SYNTHETIC_SOURCES[0]
    assert door.git_tracked(rel) and door.git_unmodified(rel)


CONTROLS = [
    ("the corpus reader drops a row", check_corpus_counts, break_corpus_reader_drops_a_row),
]
