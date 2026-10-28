"""The ingest door. Each check claims coverage of a mechanism on the corpus, never
the correctness of an identity or of collection (CLAUDE.md design gate 3)."""

from __future__ import annotations

import shutil
import uuid

from app import config
from app.refusals import Refusal
from app.store import db, door, envelope, ingest
from app.tests.helpers import (
    CASE,
    CORPUS,
    corpus_events,
    corpus_strings,
    count,
    eid_of,
    files_digest,
    named,
    refusal_of,
)


# -- 44 events land and round-trip -------------------------------------------


def check_corpus_lands_and_round_trips(ctx):
    s = ctx.store()
    result = ctx.ingest(s)
    assert result.landed == 44 and result.held == 0
    stored = ctx.stored(s)
    assert len(stored) == 44, "every corpus envelope rebuilds from skeleton plus payload"
    for e in corpus_events():
        got = stored[e["event"]["event_id"]]
        assert envelope.canonical(got) == envelope.canonical(e)


def break_drop_one_payload(ctx):
    target = eid_of("adjudicate-note")
    real = ingest.insert_payload

    def skip(conn, event_id, payload_text):
        if event_id != target:
            real(conn, event_id, payload_text)

    ctx.mp.setattr(ingest, "insert_payload", skip)


def test_corpus_lands_and_round_trips(ctx):
    check_corpus_lands_and_round_trips(ctx)


# -- the door calls the tool, not a copy --------------------------------------


def check_door_calls_the_tool(ctx):
    tool = door.validator()
    ctx.mp.setattr(tool, "check_event", lambda e, pol, index, humans: ({"X"}, set()))
    s = ctx.store()
    r = refusal_of(ctx.ingest, s)
    assert r.code == "VALIDATION_REFUSED"
    assert "FAIL X line=" in r.detail
    assert count(s, "SELECT COUNT(*) FROM event_skeleton") == 0


def break_door_uses_a_copy(ctx):
    ctx.mp.setattr(door, "check_event", lambda e, pol, index, humans: set())


def test_door_calls_the_tool(ctx):
    check_door_calls_the_tool(ctx)


# -- a fired code refuses the batch and writes nothing ------------------------


def check_confidence_refused_zero_rows(ctx):
    events = corpus_events()
    named(events, "extract-claim-handle")["payload"]["confidence"] = 0.5
    s = ctx.store()
    r = refusal_of(ctx.ingest, s, events)
    assert r.code == "VALIDATION_REFUSED"
    assert "FAIL EXTRACT_HAS_CONFIDENCE" in r.detail
    assert count(s, "SELECT COUNT(*) FROM event_skeleton") == 0
    assert count(s, "SELECT COUNT(*) FROM case_registry") == 0
    assert not s.case_file(CASE).exists()


def break_validation_removed(ctx):
    ctx.mp.setattr(door, "validate", lambda envs, stored, pol, humans: {})


def test_confidence_refused_zero_rows(ctx):
    check_confidence_refused_zero_rows(ctx)


def check_bad_30th_leaves_files_identical(ctx):
    events = corpus_events()
    events[29]["payload"]["score"] = 1
    s = ctx.store()
    before = files_digest(s.root)
    r = refusal_of(ctx.ingest, s, events)
    assert r.code == "VALIDATION_REFUSED" and "line=30 " in r.detail
    assert files_digest(s.root) == before


def test_bad_30th_leaves_files_identical(ctx):
    check_bad_30th_leaves_files_identical(ctx)


# -- re-ingest is a no-op; changed bytes conflict -----------------------------


def check_reingest_noop_and_conflict(ctx):
    s = ctx.built()
    before = files_digest(s.root)
    again = ctx.ingest(s)
    assert (again.landed, again.held) == (0, 44)
    assert files_digest(s.root) == before
    events = corpus_events()
    note = named(events, "adjudicate-note")
    note["payload"]["text"] = note["payload"]["text"].upper()
    r = refusal_of(ctx.ingest, s, events)
    assert r.code == "EVENT_ID_CONFLICT"
    assert files_digest(s.root) == before


def break_conflict_reads_as_held(ctx):
    ctx.mp.setattr(door, "classify", lambda stored_sha, new_sha: "new" if stored_sha is None else "held")


def test_reingest_noop_and_conflict(ctx):
    check_reingest_noop_and_conflict(ctx)


# -- the source rule ------------------------------------------------------------


def check_source_rule(ctx):
    copy_path = ctx.tmp / "copy.jsonl"
    shutil.copyfile(CORPUS, copy_path)
    assert refusal_of(door.check_source, copy_path, "LOCAL").code == "STORE_LOCAL_SYNTHETIC_ONLY"
    with ctx.mp.context() as m:
        m.setattr(door, "git_unmodified", lambda rel: False)
        assert refusal_of(door.check_source, CORPUS, "LOCAL").code == "STORE_LOCAL_SYNTHETIC_ONLY"
    rec = door.check_source(CORPUS, "LOCAL")
    assert rec.path == config.SYNTHETIC_SOURCES[0] and rec.synthetic and rec.checked
    s = ctx.store()
    assert refusal_of(ingest.ingest_batch, s, corpus_events(), None).code == "STORE_LOCAL_SYNTHETIC_ONLY"


def break_source_rule_open(ctx):
    ctx.mp.setattr(door, "is_allowed_source", lambda rel: True)
    ctx.mp.setattr(door, "git_tracked", lambda rel: True)
    ctx.mp.setattr(door, "git_unmodified", lambda rel: True)


def test_source_rule(ctx):
    check_source_rule(ctx)


# -- freshness ----------------------------------------------------------------------


def check_stale_artifacts_refused(ctx):
    assert door.generated_current(), "the tree's generated artifacts are current"
    ctx.mp.setattr(door, "generated_current", lambda: False)
    s = ctx.store()
    assert refusal_of(ctx.ingest, s).code == "GENERATED_ARTIFACTS_STALE"
    assert count(s, "SELECT COUNT(*) FROM event_skeleton") == 0


def break_freshness_skipped(ctx):
    ctx.mp.setattr(door, "check_fresh", lambda: None)


def test_stale_artifacts_refused(ctx):
    check_stale_artifacts_refused(ctx)


# -- shape: one case per batch ----------------------------------------------------


def check_case_mismatch(ctx):
    events = corpus_events()
    events[-1]["case_id"] = str(uuid.uuid5(uuid.UUID(CASE), "another case"))
    s = ctx.store()
    assert refusal_of(ctx.ingest, s, events).code == "CASE_MISMATCH"


def break_case_check_removed(ctx):
    ctx.mp.setattr(door, "batch_case", lambda envs, store_case=None: envs[0][1].get("case_id"))


def test_case_mismatch(ctx):
    check_case_mismatch(ctx)


# -- store checks the validator cannot make -------------------------------------


def check_synthetic_value_shape(ctx):
    events = corpus_events()
    claim = named(events, "extract-claim-handle")
    claim["payload"]["value"] = claim["payload"]["value"][1:-1]
    s = ctx.store()
    r = refusal_of(ctx.ingest, s, events)
    assert r.code == "SYNTHETIC_VALUE_SHAPE"
    assert claim["payload"]["value"] not in r.render()
    assert count(s, "SELECT COUNT(*) FROM event_skeleton") == 0


def break_shape_accepts_anything(ctx):
    ctx.mp.setattr(door, "value_shape_ok", lambda value: True)


def test_synthetic_value_shape(ctx):
    check_synthetic_value_shape(ctx)


def check_stratum_from_the_model(ctx):
    assert envelope.payload_stratum("PROBE_EVENT", "ITEM") == 1
    assert envelope.payload_stratum("PROBE_EVENT", "RUN_START") == 2
    assert envelope.payload_stratum("EXTRACT_EVENT", "CLAIM") == 1
    assert envelope.payload_stratum("SYSTEM_EVENT", "COVERAGE_INTERVAL") == 2
    real = envelope._model_strata()
    ctx.mp.setattr(envelope, "_model_strata", lambda: {k: v for k, v in real.items() if k != ("ADJUDICATE_EVENT", "NOTE")})
    s = ctx.store()
    r = refusal_of(ctx.ingest, s)
    assert r.code == "PAYLOAD_STRATUM_UNDECLARED"
    assert eid_of("adjudicate-note") in r.detail


def break_stratum_hard_coded(ctx):
    ctx.mp.setattr(envelope, "payload_stratum", lambda t, s: 2 if t in ("AUTHORIZE_EVENT", "COLLECT_EVENT", "SYSTEM_EVENT") or s in ("RUN_START", "RUN_END") else 1)


def test_stratum_from_the_model(ctx):
    check_stratum_from_the_model(ctx)


def _drop_problem(ctx, code):
    real = door.store_checks

    def filtered(*args, **kwargs):
        plan, held, problems = real(*args, **kwargs)
        return plan, held, [p for p in problems if not p.startswith(code)]

    ctx.mp.setattr(door, "store_checks", filtered)


def check_item_run_unresolved(ctx):
    events = corpus_events()
    named(events, "probe-item-2")["payload"]["run_id"] = str(uuid.uuid5(uuid.UUID(CASE), "no such run"))
    s = ctx.store()
    r = refusal_of(ctx.ingest, s, events)
    assert r.code == "ITEM_RUN_UNRESOLVED", r.render()


def test_item_run_unresolved(ctx):
    check_item_run_unresolved(ctx)


def check_claim_item_mismatch(ctx):
    events = corpus_events()
    claim = named(events, "extract-claim-handle")
    claim["payload"]["source_ref"]["item_id"] = named(events, "probe-item-2")["payload"]["item_id"]
    s = ctx.store()
    r = refusal_of(ctx.ingest, s, events)
    assert r.code == "CLAIM_ITEM_MISMATCH", r.render()


def test_claim_item_mismatch(ctx):
    check_claim_item_mismatch(ctx)


def check_motivated_by_unresolved(ctx):
    events = corpus_events()
    grant = eid_of("authorize-grant")
    named(events, "collect-permitted")["payload"]["motivated_by"] = grant
    named(events, "probe-run-start")["payload"]["motivated_by"] = grant
    s = ctx.store()
    r = refusal_of(ctx.ingest, s, events)
    assert r.code == "MOTIVATED_BY_UNRESOLVED", r.render()


def test_motivated_by_unresolved(ctx):
    check_motivated_by_unresolved(ctx)


# -- ISOLATED: SCHEMA_VIOLATION carries no value ------------------------------------


def check_schema_violation_carries_no_value(ctx):
    ctx.mp.setenv(config.ENV_ENVIRONMENT, "ISOLATED")
    ctx.mp.setenv(config.ENV_HUMANS, "analyst-example")
    # The SQLite engine refuses ISOLATED (check_isolated_refused_on_sqlite). This
    # check exercises the ISOLATED ingest path the runner will call, so it lets
    # the engine admit ISOLATED for the length of the test only.
    ctx.mp.setattr(db, "SQLITE_ENVIRONMENTS", ("LOCAL", "ISOLATED"))
    s = ctx.built("isolated")
    built = []
    real = ingest.build_schema_violation

    def spy(*args, **kwargs):
        out = real(*args, **kwargs)
        built.append(out)
        return out

    ctx.mp.setattr(ingest, "build_schema_violation", spy)
    events = corpus_events()
    named(events, "extract-claim-handle")["payload"]["confidence"] = 0.5
    r = refusal_of(ctx.ingest, s, events)
    assert r.code == "VALIDATION_REFUSED"
    assert len(built) == 1
    v = built[0]
    assert v["payload"]["original_event_id"] == eid_of("extract-claim-handle")
    assert v["payload"]["reason_code"] == "EXTRACT_HAS_CONFIDENCE"
    text = envelope.canonical(v).decode("utf-8")
    leaked = [x for x in corpus_strings() if x in text]
    assert not leaked, "the SCHEMA_VIOLATION carries a corpus value"
    rows = s.conn.execute(
        "SELECT payload_inline FROM event_skeleton WHERE event_subtype = 'SCHEMA_VIOLATION' AND producer = 'runner-ingest' "
        "AND batch_id <> (SELECT batch_id FROM event_skeleton WHERE case_seq = 1 AND case_id = ?)",
        (CASE,),
    ).fetchall()
    assert len(rows) == 1, "one SCHEMA_VIOLATION was appended"
    assert not [x for x in corpus_strings() if x in rows[0][0]]


def break_builder_copies_the_value(ctx):
    real = ingest.build_schema_violation

    def leaky(case_id, original, codes, pol):
        out = real(case_id, original, codes, pol)
        out["payload"]["detail"] = (original.get("payload") or {}).get("value")
        return out

    ctx.mp.setattr(ingest, "build_schema_violation", leaky)


def test_schema_violation_carries_no_value(ctx):
    check_schema_violation_carries_no_value(ctx)


def check_rebuilt_index_reaches_the_tool(ctx):
    """The Index the door hands the tool holds the stored case plus the batch: a second
    batch whose only lineage parent is already stored lands, and the tool saw the parent."""
    events = corpus_events()
    note = named(events, "adjudicate-note")
    rest = [e for e in events if e is not note]
    s = ctx.store()
    assert ctx.ingest(s, rest).landed == 43
    seen = []
    real = door.make_index

    def spy(envs):
        seen.append({door._eid(e) for e in envs})
        return real(envs)

    ctx.mp.setattr(door, "make_index", spy)
    try:
        result = ctx.ingest(s, [note])
    except Refusal as refusal:
        raise AssertionError(f"a batch whose parent is only in the store was refused: {refusal.code}") from None
    assert result.landed == 1, "a batch whose parent is only in the store did not land"
    parent = note["lineage"]["based_on"][0]
    assert seen and parent in seen[0] and len(seen[0]) == 44, "the Index handed to the tool lacks the stored case"


def break_index_holds_the_batch_only(ctx):
    def batch_only(envs, stored, pol, humans):
        index = door.make_index([e for _, e in envs])
        failures = {}
        for line, e in envs:
            codes = door.check_event(e, pol, index, set(humans))
            if codes:
                failures[line] = (e, set(codes))
        return failures

    ctx.mp.setattr(door, "validate", batch_only)


def test_rebuilt_index_reaches_the_tool(ctx):
    check_rebuilt_index_reaches_the_tool(ctx)


# -- a repeated event id inside one batch ----------------------------------------


def check_batch_duplicate_classified(ctx):
    events = corpus_events()
    events.append(named(corpus_events(), "adjudicate-note"))
    s = ctx.store("dup-identical")
    try:
        result = ctx.ingest(s, events)
    except Exception as exc:  # noqa: BLE001 - a crash where a no-op belongs fails the check
        raise AssertionError(f"an identical repeat in one batch crashed the ingest: {type(exc).__name__}") from None
    assert (result.landed, result.held) == (44, 1), "an identical repeat is not a no-op"
    events = corpus_events()
    changed = named(corpus_events(), "adjudicate-note")
    changed["payload"]["text"] = changed["payload"]["text"].upper()
    events.append(changed)
    s = ctx.store("dup-changed")
    r = refusal_of(ctx.ingest, s, events)
    assert r.code == "EVENT_ID_CONFLICT", r.code
    assert count(s, "SELECT COUNT(*) FROM case_registry") == 0
    assert not s.case_file(CASE).exists(), "a refused first batch left a case file behind"


def break_batch_ignored_by_classify(ctx):
    ctx.mp.setattr(door, "prior_sha", lambda stored_sha, batch_sha, eid: stored_sha.get(eid))


def test_batch_duplicate_classified(ctx):
    check_batch_duplicate_classified(ctx)


def test_rolled_back_first_batch_leaves_no_case_file(ctx):
    """A write that fails inside its transaction removes the case file its attach created."""
    real = ingest.write_event
    calls = {"n": 0}

    def failing(conn, env, case_seq, ingested_at, batch_id):
        calls["n"] += 1
        if calls["n"] == 30:
            raise RuntimeError("a fault in the middle of the write")
        real(conn, env, case_seq, ingested_at, batch_id)

    ctx.mp.setattr(ingest, "write_event", failing)
    s = ctx.store()
    try:
        ctx.ingest(s)
    except RuntimeError:
        pass
    else:
        raise AssertionError("the planted fault did not fire")
    assert count(s, "SELECT COUNT(*) FROM event_skeleton") == 0
    assert not s.case_file(CASE).exists()


# -- an ingest overtaken between its checks and its write ---------------------------------


def check_overtaken_ingest_refused(ctx):
    s = ctx.store("race")
    other = db.Store.open(s.root)
    real = door.store_checks
    raced = {"done": False}

    def overtaking(*args, **kwargs):
        out = real(*args, **kwargs)
        if not raced["done"]:
            raced["done"] = True
            ctx.ingest(other)
        return out

    ctx.mp.setattr(door, "store_checks", overtaking)
    try:
        r = refusal_of(ctx.ingest, s)
    finally:
        other.close()
    assert r.code == "INGEST_CONCURRENT", r.code
    assert count(s, "SELECT COUNT(*) FROM event_skeleton") == 44, "the overtaking ingest's events are not the only ones"
    ctx.mp.setattr(door, "store_checks", real)
    again = ctx.ingest(s)
    assert (again.landed, again.held) == (0, 44)


def break_overtake_unchecked(ctx):
    ctx.mp.setattr(ingest, "overtaken", lambda conn, case_id, plan, expect_registered: False)


def test_overtaken_ingest_refused(ctx):
    check_overtaken_ingest_refused(ctx)


# -- ISOLATED is not a mode of the SQLite store -----------------------------------------


def check_isolated_refused_on_sqlite(ctx):
    ctx.mp.setenv(config.ENV_ENVIRONMENT, "isolated")
    ctx.mp.setenv(config.ENV_HUMANS, "analyst-example")
    assert refusal_of(db.Store.init, ctx.tmp / "iso").code == "STORE_ISOLATED_NOT_PROVISIONED"
    assert not (ctx.tmp / "iso").exists(), "a refused ISOLATED init created the store root"
    ctx.mp.delenv(config.ENV_ENVIRONMENT)
    db.Store.init(ctx.tmp / "local").close()
    ctx.mp.setenv(config.ENV_ENVIRONMENT, "ISOLATED")
    assert refusal_of(db.Store.open, ctx.tmp / "local").code == "STORE_ISOLATED_NOT_PROVISIONED"


def break_engine_admits_isolated(ctx):
    ctx.mp.setattr(db, "check_engine", lambda environment: None)


def test_isolated_refused_on_sqlite(ctx):
    check_isolated_refused_on_sqlite(ctx)


CONTROLS = [
    ("drop one payload row", check_corpus_lands_and_round_trips, break_drop_one_payload),
    ("the door uses a copy of check_event", check_door_calls_the_tool, break_door_uses_a_copy),
    ("validation removed: confidence lands", check_confidence_refused_zero_rows, break_validation_removed),
    ("validation removed: the bad 30th writes", check_bad_30th_leaves_files_identical, break_validation_removed),
    ("changed bytes read as held", check_reingest_noop_and_conflict, break_conflict_reads_as_held),
    ("source rule opened", check_source_rule, break_source_rule_open),
    ("freshness check skipped", check_stale_artifacts_refused, break_freshness_skipped),
    ("case check removed", check_case_mismatch, break_case_check_removed),
    ("value shape accepts anything", check_synthetic_value_shape, break_shape_accepts_anything),
    ("stratum hard-coded, not read from the model", check_stratum_from_the_model, break_stratum_hard_coded),
    ("ITEM_RUN_UNRESOLVED dropped", check_item_run_unresolved, lambda ctx: _drop_problem(ctx, "ITEM_RUN_UNRESOLVED")),
    ("CLAIM_ITEM_MISMATCH dropped", check_claim_item_mismatch, lambda ctx: _drop_problem(ctx, "CLAIM_ITEM_MISMATCH")),
    ("MOTIVATED_BY_UNRESOLVED dropped", check_motivated_by_unresolved, lambda ctx: _drop_problem(ctx, "MOTIVATED_BY_UNRESOLVED")),
    ("SCHEMA_VIOLATION builder copies the value", check_schema_violation_carries_no_value, break_builder_copies_the_value),
    ("the Index holds the batch only", check_rebuilt_index_reaches_the_tool, break_index_holds_the_batch_only),
    ("classify ignores the batch", check_batch_duplicate_classified, break_batch_ignored_by_classify),
    ("the overtake check removed", check_overtaken_ingest_refused, break_overtake_unchecked),
    ("the SQLite engine admits ISOLATED", check_isolated_refused_on_sqlite, break_engine_admits_isolated),
]
