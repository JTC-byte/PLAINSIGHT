"""The ingest door. Each check claims coverage of a mechanism on the corpus, never
the correctness of an identity or of collection (CLAUDE.md design gate 3)."""

from __future__ import annotations

import pathlib
import shutil
import uuid

from app import config
from app.refusals import Refusal
from app.store import db, door, envelope, ingest, replay
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


# -- the door writes only into a held case (amendment 9.21, reading APP-R34) -----------------------


def _set_state(store, state: str) -> None:
    store.conn.execute("UPDATE case_registry SET state = ? WHERE case_id = ?", (state, CASE))
    store.conn.commit()


def _fresh_heartbeat(case_id: str = CASE) -> dict:
    """The corpus's sweep heartbeat under a new event id: a system event that needs no lineage parent."""
    beat = named(corpus_events(), "system-sweep-heartbeat")
    beat["event"]["event_id"] = str(uuid.uuid4())
    beat["case_id"] = case_id
    return beat


def check_door_writes_only_into_a_held_case(ctx):
    s = ctx.built()
    path = s.case_file(CASE)
    landed = ingest.ingest_batch(s, [_fresh_heartbeat()], None, origin="system")
    assert landed.landed == 1, "a system event did not land in a held case"
    for state in ("shredded", "shred_failed"):
        _set_state(s, state)
        before = files_digest(s.root)
        r = refusal_of(ingest.ingest_batch, s, [_fresh_heartbeat()], None, origin="system")
        assert r.code == "CASE_CLOSED_TO_WRITES", f"a case the registry says is {state} was not refused: {r.code}"
        assert files_digest(s.root) == before, f"a refused batch changed the store of a case the registry says is {state}"
    # The rule is read before the stored log: the log of a closed case is not read, and a batch that would also
    # fail validation is refused for the case and not for its rows.
    _set_state(s, "shredded")
    read = []
    log = replay.stored_envelopes

    def reading(store, case_id):
        read.append(case_id)
        return log(store, case_id)

    ctx.mp.setattr(replay, "stored_envelopes", reading)
    invalid = _fresh_heartbeat()
    invalid["event"]["event_subtype"] = "NOT_A_SUBTYPE"
    first = refusal_of(ingest.ingest_batch, s, [invalid], None, origin="system")
    assert first.code == "CASE_CLOSED_TO_WRITES", f"a batch for a closed case was refused for its rows first: {first.code}"
    assert read == [], "the stored log was read for a case closed to writes"
    ctx.mp.setattr(replay, "stored_envelopes", log)
    # The corpus sent again to a shredded case is refused, and never reported as already held.
    resent = refusal_of(ctx.ingest, s)
    assert resent.code == "CASE_CLOSED_TO_WRITES", f"a shredded case was reported as holding the batch: {resent.code}"
    # Open in the registry with its database gone: refused at the door before the stored log is read, and the
    # database is not recreated.
    _set_state(s, "open")
    s.detach_case()
    path.unlink()
    ctx.mp.setattr(replay, "stored_envelopes", reading)
    gone = refusal_of(ingest.ingest_batch, s, [_fresh_heartbeat()], None, origin="system")
    assert gone.code == "CASE_CLOSED_TO_WRITES" and "is absent" in gone.detail, gone.render()
    assert read == [], "the stored log was read for an open case whose database is gone"
    assert not path.exists(), "the door recreated a case database that was gone"


def break_rule_removed_at_the_door(ctx):
    ctx.mp.setattr(ingest, "refuse_closed_case", lambda store, case_id: None)


def break_rule_read_after_the_log(ctx):
    rule = ingest.refuse_closed_case
    log = replay.stored_envelopes

    def late(store, case_id):
        out = log(store, case_id)
        rule(store, case_id)
        return out

    ctx.mp.setattr(ingest, "refuse_closed_case", lambda store, case_id: None)
    ctx.mp.setattr(replay, "stored_envelopes", late)


def break_open_case_without_database_read_as_held(ctx):
    ctx.mp.setattr(ingest, "case_held", lambda state, present: state == "open")


def test_door_writes_only_into_a_held_case(ctx):
    check_door_writes_only_into_a_held_case(ctx)


def check_door_reads_every_spelling_of_a_case_id(ctx):
    # The case database's file name is built from the id in lower case, so the id in upper case names the
    # same file. A batch under that spelling is a first batch to an exact lookup, and would open a second
    # registry row onto the shredded case's database.
    s = ctx.built()
    _set_state(s, "shredded")
    before = files_digest(s.root)
    r = refusal_of(ctx.ingest, s, [_fresh_heartbeat(CASE.upper())])
    assert r.code == "CASE_CLOSED_TO_WRITES", f"another spelling of a shredded case's id was not refused: {r.code}"
    assert files_digest(s.root) == before, "a batch under another spelling of a shredded case's id wrote to the store"
    assert count(s, "SELECT COUNT(*) FROM case_registry") == 1, "a second registry row was opened onto one case database"


def break_spelling_not_read(ctx):
    ctx.mp.setattr(ingest, "rows_for_file", lambda conn, case_id: conn.execute(
        "SELECT case_id, state FROM case_registry WHERE case_id = ?", (case_id,)).fetchall())


def test_door_reads_every_spelling_of_a_case_id(ctx):
    check_door_reads_every_spelling_of_a_case_id(ctx)


def check_door_refuses_another_spelling_of_an_open_case(ctx):
    # A held case, and a batch under its id in upper case: the same case database to the file name, a new case to
    # an exact lookup. Landing it would open a second registry row, with a second retention clock, onto one file.
    s = ctx.built()
    before = files_digest(s.root)
    r = refusal_of(ctx.ingest, s, [_fresh_heartbeat(CASE.upper())])
    assert r.code == "CASE_ID_SPELLING_DIFFERS", f"another spelling of an open case's id was not refused: {r.code}"
    assert files_digest(s.root) == before, "a batch under another spelling of an open case's id wrote to the store"
    assert count(s, "SELECT COUNT(*) FROM case_registry") == 1, "a second registry row was opened onto one case database"


def break_other_spelling_admitted(ctx):
    ctx.mp.setattr(ingest, "other_spelling", lambda conn, case_id: None)


def test_door_refuses_another_spelling_of_an_open_case(ctx):
    check_door_refuses_another_spelling_of_an_open_case(ctx)


def check_write_attaches_no_case_closed_to_writes(ctx):
    # _write is reached without ingest_batch's own refusal on the ISOLATED violation path, and its attach creates
    # an absent case database, so the write holds the rule itself before it attaches.
    s = ctx.built()
    _set_state(s, "shredded")
    path = s.case_file(CASE)
    s.detach_case()
    path.unlink()
    attached = []
    real = s.attach_case

    def spy(case_id, create=True):
        attached.append((case_id, create))
        return real(case_id, create)

    ctx.mp.setattr(s, "attach_case", spy)
    r = refusal_of(ingest._write, s, CASE, [_fresh_heartbeat()], str(uuid.uuid4()), None, None)
    assert r.code == "CASE_CLOSED_TO_WRITES", r.code
    assert attached == [], "the write attached a case the registry says is shredded"
    assert not path.exists(), "the write recreated a shredded case's database"


def break_write_check_before_attach_removed(ctx):
    ctx.mp.setattr(ingest, "closed_to_writes", lambda store, case_id: None)


def test_write_attaches_no_case_closed_to_writes(ctx):
    check_write_attaches_no_case_closed_to_writes(ctx)


def check_write_creates_no_database_for_a_registered_case(ctx):
    # The case is open and its database present when the write checks, and the database is gone by the attach.
    # A registered case is attached without create, so the write is refused and nothing is recreated.
    s = ctx.built()
    path = s.case_file(CASE)
    s.detach_case()
    real = s.attach_case

    def gone_at_the_attach(case_id, create=True):
        if path.exists():
            path.unlink()
        return real(case_id, create)

    ctx.mp.setattr(s, "attach_case", gone_at_the_attach)
    r = refusal_of(ingest._write, s, CASE, [_fresh_heartbeat()], str(uuid.uuid4()), None, None)
    assert r.code == "CASE_CLOSED_TO_WRITES" and "absent at the attach" in r.detail, r.render()
    assert not path.exists(), "the write recreated the database of a registered case that was gone at its attach"


def break_write_attach_creates(ctx):
    real = db.Store.attach_case
    ctx.mp.setattr(db.Store, "attach_case", lambda self, case_id, create=True: real(self, case_id, True))


def test_write_creates_no_database_for_a_registered_case(ctx):
    check_write_creates_no_database_for_a_registered_case(ctx)


def check_write_rereads_the_state_under_its_lock(ctx):
    # The door's checks read the registry with no lock. A state that changes after them is read again under
    # the write lock, and the write is refused.
    s = ctx.built()
    other = db.Store.open(s.root)
    real = s.attach_case
    rule = ingest.closed_to_writes
    fired = {"done": False, "reads": 0}

    def counted(store, case_id):
        fired["reads"] += 1
        return rule(store, case_id)

    def attach_then_close(case_id, create=True):
        out = real(case_id, create)
        # The rule's second read is the write's own, made just before this attach; the state changes after it.
        if fired["reads"] == 2 and not fired["done"]:
            fired["done"] = True
            other.conn.execute("UPDATE case_registry SET state = 'shredded' WHERE case_id = ?", (CASE,))
        return out

    ctx.mp.setattr(ingest, "closed_to_writes", counted)
    ctx.mp.setattr(s, "attach_case", attach_then_close)
    events = count(s, "SELECT COUNT(*) FROM event_skeleton WHERE case_id = ?", (CASE,))
    try:
        r = refusal_of(ingest.ingest_batch, s, [_fresh_heartbeat()], None, origin="system")
    finally:
        other.close()
    assert fired["done"], "the registry was not changed between the door's checks and the write"
    assert r.code == "CASE_CLOSED_TO_WRITES" and "stopped saying open" in r.detail, r.render()
    assert count(s, "SELECT COUNT(*) FROM event_skeleton WHERE case_id = ?", (CASE,)) == events, \
        "an event landed in a case the registry marked shredded before the write took its lock"


def break_state_not_reread_under_the_lock(ctx):
    ctx.mp.setattr(ingest, "closed_under_lock", lambda conn, case_id: False)


def test_write_rereads_the_state_under_its_lock(ctx):
    check_write_rereads_the_state_under_its_lock(ctx)


def check_write_rereads_the_spelling_under_its_lock(ctx):
    # A first batch for a new case reads no other spelling at the door. Before it takes its lock, another store
    # lands a batch under the id in upper case, which names the same case database. Read again under the lock,
    # the other spelling refuses the first batch, so one case database does not get two registry rows.
    s = ctx.built()
    other = db.Store.open(s.root)
    new = str(uuid.uuid4())
    real = s.attach_case
    fired = {"done": False}

    def attach_then_register(case_id, create=True):
        out = real(case_id, create)
        if case_id == new and not fired["done"]:
            fired["done"] = True
            ctx.ingest(other, [_fresh_heartbeat(new.upper())])
        return out

    ctx.mp.setattr(s, "attach_case", attach_then_register)
    removed = []
    remove = ingest._remove_created_case_file

    def removing(store, case_id):
        removed.append(case_id)
        return remove(store, case_id)

    ctx.mp.setattr(ingest, "_remove_created_case_file", removing)
    try:
        r = refusal_of(ctx.ingest, s, [_fresh_heartbeat(new)])
    finally:
        other.close()
    assert fired["done"], "the other spelling was not registered between the door's checks and the write"
    assert r.code == "CASE_ID_SPELLING_DIFFERS" and "between the door's checks and the write" in r.detail, r.render()
    rows = s.conn.execute("SELECT case_id FROM case_registry WHERE lower(case_id) = ?", (new,)).fetchall()
    assert [row[0] for row in rows] == [new.upper()], "a second registry row was opened onto one case database"
    # The refused batch created the file and the other store registered it and wrote into it: the file stays, and
    # the rollback does not try to remove it.
    assert removed == [], "the rollback tried to remove a case database another ingest had registered"
    assert s.case_file(new).is_file(), "the other spelling's case database was removed with the refused batch"


def break_spelling_not_reread_under_the_lock(ctx):
    ctx.mp.setattr(ingest, "spelling_registered_under_lock", lambda conn, case_id: False)


def break_created_file_removed_although_registered(ctx):
    ctx.mp.setattr(ingest, "keep_created_file", lambda conn, case_id: False)


def test_write_rereads_the_spelling_under_its_lock(ctx):
    check_write_rereads_the_spelling_under_its_lock(ctx)


def check_write_refuses_a_database_gone_while_attached(ctx):
    # The case is attached when the write reaches its attach, which then returns at once and reads no file. On a
    # system that lets an open file be deleted the database can be gone by then; the write reads it again.
    s = ctx.built()
    rule = ingest.closed_to_writes
    reads = {"n": 0}

    def counted(store, case_id):
        reads["n"] += 1
        return rule(store, case_id)

    real = s.attach_case
    gone = s.root / "cases" / "deleted-while-attached.sqlite"

    def attach_then_lose(case_id, create=True):
        out = real(case_id, create)
        if reads["n"] == 2:
            ctx.mp.setattr(s, "case_file", lambda cid: gone)
        return out

    ctx.mp.setattr(ingest, "closed_to_writes", counted)
    ctx.mp.setattr(s, "attach_case", attach_then_lose)
    events = count(s, "SELECT COUNT(*) FROM event_skeleton WHERE case_id = ?", (CASE,))
    r = refusal_of(ingest.ingest_batch, s, [_fresh_heartbeat()], None, origin="system")
    assert r.code == "CASE_CLOSED_TO_WRITES" and "absent at the attach" in r.detail, r.render()
    assert count(s, "SELECT COUNT(*) FROM event_skeleton WHERE case_id = ?", (CASE,)) == events, \
        "an event landed in a case database that was gone while it was attached"


def break_presence_not_read_after_the_attach(ctx):
    ctx.mp.setattr(ingest, "database_present", lambda store, case_id: True)


def test_write_refuses_a_database_gone_while_attached(ctx):
    check_write_refuses_a_database_gone_while_attached(ctx)


def check_write_refuses_a_database_gone_before_its_lock(ctx):
    # The file is there at the attach and gone when the write takes its lock, which a system that lets an open file
    # be deleted allows. Read again under the lock, its absence refuses the write.
    s = ctx.built()
    gone = s.root / "cases" / "deleted-before-the-lock.sqlite"
    rule = ingest.closed_under_lock

    def lost_then_read(conn, case_id):
        ctx.mp.setattr(s, "case_file", lambda cid: gone)
        return rule(conn, case_id)

    ctx.mp.setattr(ingest, "closed_under_lock", lost_then_read)
    events = count(s, "SELECT COUNT(*) FROM event_skeleton WHERE case_id = ?", (CASE,))
    r = refusal_of(ingest.ingest_batch, s, [_fresh_heartbeat()], None, origin="system")
    assert r.code == "CASE_CLOSED_TO_WRITES" and "gone when the write took its lock" in r.detail, r.render()
    assert count(s, "SELECT COUNT(*) FROM event_skeleton WHERE case_id = ?", (CASE,)) == events, \
        "an event landed in a case database that was gone when the write took its lock"


def break_presence_not_read_under_the_lock(ctx):
    ctx.mp.setattr(ingest, "database_present_under_lock", lambda store, case_id: True)


def test_write_refuses_a_database_gone_before_its_lock(ctx):
    check_write_refuses_a_database_gone_before_its_lock(ctx)


def check_rollback_leaves_a_file_it_cannot_remove_and_raises_the_write_error(ctx):
    # A first batch fails in the middle of its write, and the case database it created cannot be removed because
    # another connection holds it open (planted here, as Windows does it). The caller sees the write's own error.
    s = ctx.store()
    new = str(uuid.uuid4())
    target = s.case_file(new)
    unlink = pathlib.Path.unlink

    def held_open(self, *args, **kwargs):
        if self == target:
            raise PermissionError("the file is open in another connection")
        return unlink(self, *args, **kwargs)

    def failing(conn, env, case_seq, ingested_at, batch_id):
        raise RuntimeError("a fault in the middle of the write")

    ctx.mp.setattr(pathlib.Path, "unlink", held_open)
    ctx.mp.setattr(ingest, "write_event", failing)
    try:
        ctx.ingest(s, [_fresh_heartbeat(new)])
    except RuntimeError:
        pass
    except PermissionError as exc:
        raise AssertionError("the rollback's own error took the place of the write's") from exc
    else:
        raise AssertionError("the planted fault did not fire")
    assert target.exists(), "the file the rollback could not remove is not on disk"
    assert count(s, "SELECT COUNT(*) FROM case_registry") == 0, "a rolled-back first batch left a registry row"


def break_unremovable_file_raised(ctx):
    def plain(path):
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        return True

    ctx.mp.setattr(ingest, "_unlink_left_if_open", plain)


def test_rollback_leaves_a_file_it_cannot_remove_and_raises_the_write_error(ctx):
    check_rollback_leaves_a_file_it_cannot_remove_and_raises_the_write_error(ctx)


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
    ("the door's held-case rule removed at ingest_batch", check_door_writes_only_into_a_held_case, break_rule_removed_at_the_door),
    ("an open case whose database is gone read as held", check_door_writes_only_into_a_held_case, break_open_case_without_database_read_as_held),
    ("a closed case's row read under one spelling of its id", check_door_reads_every_spelling_of_a_case_id, break_spelling_not_read),
    ("the write's own check before its attach removed", check_write_attaches_no_case_closed_to_writes, break_write_check_before_attach_removed),
    ("the state not read again under the write lock", check_write_rereads_the_state_under_its_lock, break_state_not_reread_under_the_lock),
    ("the held-case rule read after the stored log", check_door_writes_only_into_a_held_case, break_rule_read_after_the_log),
    ("another spelling of an open case's id admitted", check_door_refuses_another_spelling_of_an_open_case, break_other_spelling_admitted),
    ("the write's attach allowed to create for a registered case", check_write_creates_no_database_for_a_registered_case, break_write_attach_creates),
    ("the spelling not read again under the write lock", check_write_rereads_the_spelling_under_its_lock, break_spelling_not_reread_under_the_lock),
    ("a created file removed although another ingest registered it", check_write_rereads_the_spelling_under_its_lock, break_created_file_removed_although_registered),
    ("the database's presence not read after the attach", check_write_refuses_a_database_gone_while_attached, break_presence_not_read_after_the_attach),
    ("the database's presence not read under the write lock", check_write_refuses_a_database_gone_before_its_lock, break_presence_not_read_under_the_lock),
    ("a file the rollback cannot remove raised in place of the write's error", check_rollback_leaves_a_file_it_cannot_remove_and_raises_the_write_error, break_unremovable_file_raised),
]
