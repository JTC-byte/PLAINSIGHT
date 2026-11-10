"""runner/retention_sweep.py, runner/verify_shred.py and the header's sweep line, drafted refusing.

The sweep writes its heartbeat into every held case on every run and deletes nothing. It writes
none into a case that is not held, it exits 1 when the registry says open for a case whose database
is absent or when the door refuses a heartbeat, it refuses a date it cannot read instead of
crashing, it states and refuses a due case in RETENTION.md section 9's order from the instant
retain_until names, and it skips a frozen case. The five RT-9 checks run as dated facts, none passes
for a reason other than the one it claims, and no run of this draft reports a verified shred. The
header's line stands only on a heartbeat that records a run that has happened, and a heartbeat row
that lacks a ts, a seq or an object payload does not make it raise."""

from __future__ import annotations

import contextlib
import datetime as dt
import io
import sqlite3
import uuid

from app.http import routes
from app.model import reads
from app.model.svg import VOUCH_MARK
from app.store import db, retention
from app.tests.helpers import CASE, corpus_events, corpus_rows, count, files_digest, refusal_of
from runner import retention_sweep as sweep_mod
from runner import verify_shred

NOW = dt.datetime(2026, 1, 20, 12, 0, 0, tzinfo=dt.timezone.utc)
FAR = dt.datetime(2999, 1, 1, tzinfo=dt.timezone.utc)

#: The tables a case database declares, read once at import so that no control changes what a check drops.
CASE_TABLES = verify_shred.case_tables()

#: The three counts check 5 compares, named here so that no control changes what a check supplies.
COUNTS = ("payloads", "claims", "blobs")

#: The files SQLite keeps beside a database, named here so that no control changes what a check plants.
SIDECARS = ("-journal", "-wal", "-shm")


class FixtureStamps:
    """A stamp state the tests supply: nothing stamped unless told otherwise."""

    def __init__(self, policy: bool = False, fixture: bool = False):
        self._policy, self._fixture = policy, fixture

    def policy_stamped(self) -> bool:
        return self._policy

    def fixture_stamped(self) -> bool:
        return self._fixture

    def reason(self, rel: str) -> str:
        return f"{rel} carries no dated row (fixture stamp state)"


def _at(text: str) -> dt.datetime:
    return dt.datetime.fromisoformat(text.replace("Z", "+00:00"))


def _heartbeats(s) -> list[dict]:
    return reads.events(s.conn, CASE, "SYSTEM_EVENT", ("SWEEP_HEARTBEAT",))


def _set_registry(s, **cols) -> None:
    sets = ", ".join(f"{k} = ?" for k in cols)
    s.conn.execute(f"UPDATE case_registry SET {sets} WHERE case_id = ?", (*cols.values(), CASE))
    s.conn.commit()


def _corpus(skip: tuple[str, ...] = (), second: str | None = None) -> list[dict]:
    """The corpus events in order, without the rows named in `skip`, and with the row named `second` moved to second place."""
    pairs = [(row["name"], event) for row, event in zip(corpus_rows(), corpus_events()) if row["name"] not in skip]
    if second is not None:
        moved = [p for p in pairs if p[0] == second]
        rest = [p for p in pairs if p[0] != second]
        pairs = rest[:1] + moved + rest[1:]
    return [event for _, event in pairs]


def _drop(path, tables) -> None:
    """Drops tables from a case database through a connection of its own; the store has detached it first."""
    conn = sqlite3.connect(str(path))
    try:
        for table in tables:
            conn.execute(f"DROP TABLE {table}")
        conn.commit()
    finally:
        conn.close()


def _run(path, *statements) -> None:
    """Runs statements on a case database through a connection of its own; the store has detached it first."""
    conn = sqlite3.connect(str(path))
    try:
        for statement in statements:
            conn.execute(statement)
        conn.commit()
    finally:
        conn.close()


# -- the heartbeat lands on every run and nothing is deleted ----------------------------------------


def check_sweep_writes_heartbeat_and_deletes_nothing(ctx):
    s = ctx.built()
    before_claims = count(s, "SELECT COUNT(*) FROM claim")
    before_payloads = count(s, "SELECT COUNT(*) FROM event_payload")
    corpus_beats = len(_heartbeats(s))
    report = sweep_mod.sweep(s, now=NOW, stamps=FixtureStamps())
    assert report["refused_heartbeats"] == [], report["refused_heartbeats"]
    assert len(report["heartbeats"]) == 1, "one heartbeat per held case was not written"
    beats = _heartbeats(s)
    assert len(beats) == corpus_beats + 1, "the heartbeat did not land through the door"
    newest = beats[-1]
    assert newest["producer"] == sweep_mod.PRODUCER and newest["payload"]["swept_count"] == 0
    assert newest["payload"]["next_due"] == "2026-01-21T12:00:00Z", "next_due is not now plus the policy's daily cadence"
    assert count(s, "SELECT COUNT(*) FROM claim") == before_claims, "the sweep deleted a claim"
    assert count(s, "SELECT COUNT(*) FROM event_payload") == before_payloads, "the sweep deleted a payload"
    assert s.registry(CASE)["state"] == "open"
    assert report["due"] == [] and report["skipped_frozen"] == [], "the corpus case read as due or frozen"
    assert report["not_held"] == [] and report["unreadable"] == [] and sweep_mod.exit_code(report) == 0, report


def break_heartbeat_not_written(ctx):
    ctx.mp.setattr(sweep_mod, "write_heartbeat", lambda store, case_id, now, next_due, humans=None: "0" * 36)


def test_sweep_writes_heartbeat_and_deletes_nothing(ctx):
    check_sweep_writes_heartbeat_and_deletes_nothing(ctx)


# -- a due case is stated and refused in section 9's order ---------------------------------------


def check_due_case_refused_in_order(ctx):
    s = ctx.built()
    # The corpus case is frozen until 2026-05-15 by its RETENTION_RENEWAL; lift the freeze to make it due.
    _set_registry(s, retain_until="2026-01-01", frozen_until=None)
    before = files_digest(s.root)
    # The corpus itself carries one SHRED_RECEIPT and one SHRED_FAILED under runner-sweep; the sweep adds none.
    shred_rows = {sub: len(reads.events(s.conn, CASE, "SYSTEM_EVENT", (sub,))) for sub in ("SHRED_RECEIPT", "SHRED_FAILED")}
    report = sweep_mod.sweep(s, now=NOW, stamps=FixtureStamps())
    assert len(report["due"]) == 1, report
    row = report["due"][0]
    assert row["refusal"] == "SWEEP_REFUSED_FINDING_CHECK_PENDING", "the first refusal is not RT-13's finding check"
    assert row["text"].startswith("DUE, NOT SWEPT · past retain_until 2026-01-01"), row["text"]
    assert s.registry(CASE)["state"] == "open", "a refused sweep changed the registry state"
    for sub, n in shred_rows.items():
        assert len(reads.events(s.conn, CASE, "SYSTEM_EVENT", (sub,))) == n, f"the sweep wrote a {sub}"
    assert files_digest(s.root) != before, "the sweep wrote no heartbeat on a due case"
    # The boundary: a case is due from the instant retain_until names, as the store's own is_past reads it.
    _set_registry(s, retain_until="2026-02-01", frozen_until=None)
    early = sweep_mod.sweep(s, now=_at("2026-01-31T23:59:59Z"), stamps=FixtureStamps())
    assert early["due"] == [], "a case was due one second before the instant retain_until names"
    at_instant = sweep_mod.sweep(s, now=_at("2026-02-01T00:00:00Z"), stamps=FixtureStamps())
    assert len(at_instant["due"]) == 1, "a case was not due at the instant retain_until names"
    # The next refusals in order, each reached only when the one before it is lifted.
    assert sweep_mod.shred_refusal(s, FixtureStamps(), CASE).code == "SWEEP_REFUSED_LOCAL_STORE"
    ctx.mp.setattr(s, "environment", "ISOLATED")
    assert sweep_mod.shred_refusal(s, FixtureStamps(policy=False), CASE).code == "SWEEP_REFUSED_POLICY_UNRATIFIED"
    assert sweep_mod.shred_refusal(s, FixtureStamps(policy=True), CASE).code == "SWEEP_REFUSED_SHRED_NOT_BUILT"


def break_finding_check_lifted(ctx):
    ctx.mp.setattr(sweep_mod, "finding_check_refusal", lambda case_id: None)


def break_due_only_after_the_instant(ctx):
    ctx.mp.setattr(sweep_mod, "past_retain_until", lambda retain, now: retain < now)


def test_due_case_refused_in_order(ctx):
    check_due_case_refused_in_order(ctx)


# -- a frozen case is skipped (RT-17), and a freeze that has ended is no freeze --------------------


def check_frozen_case_skipped(ctx):
    s = ctx.built()
    _set_registry(s, retain_until="2026-01-01", frozen_until="2026-03-01")
    report = sweep_mod.sweep(s, now=NOW, stamps=FixtureStamps())
    assert report["due"] == [] and len(report["skipped_frozen"]) == 1, report
    assert report["skipped_frozen"][0]["text"].startswith("FROZEN until 2026-03-01 · shred suspended (RT-17)")
    _set_registry(s, frozen_until="2026-01-10")
    ended = sweep_mod.sweep(s, now=NOW, stamps=FixtureStamps())
    assert ended["skipped_frozen"] == [] and len(ended["due"]) == 1, "a freeze that ended before now still suspended the case"


def break_freeze_not_read(ctx):
    real = sweep_mod.survey

    def unfrozen(store, now):
        found = real(store, now)
        found["due"], found["frozen"] = found["due"] + found["frozen"], []
        return found

    ctx.mp.setattr(sweep_mod, "survey", unfrozen)


def test_frozen_case_skipped(ctx):
    check_frozen_case_skipped(ctx)


# -- no heartbeat into a case that is not held, and no case database recreated ---------------------


def check_no_heartbeat_into_a_case_not_held(ctx):
    s = ctx.built()
    beats = len(_heartbeats(s))
    # A failed shred is not a held case: no heartbeat is written into it, and its line states RT-11's halt.
    _set_registry(s, state="shred_failed")
    failed = sweep_mod.sweep(s, now=NOW, stamps=FixtureStamps())
    assert failed["heartbeats"] == [] and failed["refused_heartbeats"] == [], "the sweep wrote into a case whose shred failed"
    assert len(_heartbeats(s)) == beats, "a heartbeat landed in a case whose shred failed"
    assert failed["not_held"][0]["text"].startswith("NOT HELD · the registry says the shred failed"), failed["not_held"]
    assert sweep_mod.exit_code(failed) == 0, "a case whose shred failed changed the sweep's exit code"
    _set_registry(s, state="shredded")
    report = sweep_mod.sweep(s, now=NOW, stamps=FixtureStamps())
    assert report["heartbeats"] == [] and report["refused_heartbeats"] == [], "the sweep wrote into a case the registry says is shredded"
    assert len(_heartbeats(s)) == beats, "a heartbeat landed in a case the registry says is shredded"
    assert [row["case_id"] for row in report["not_held"]] == [CASE], report["not_held"]
    assert report["not_held"][0]["text"].startswith("NOT HELD · the registry says shredded and the case database is still present")
    assert report["due"] == [] and report["skipped_frozen"] == [], "a case that is not held was decided as due or frozen"
    assert sweep_mod.exit_code(report) == 0, "a case marked shredded changed the sweep's exit code"
    # Open in the registry with its database gone: the sweep says so, does not recreate the file, and exits 1.
    _set_registry(s, state="open")
    path = s.case_file(CASE)
    s.detach_case()
    path.unlink()
    gone = sweep_mod.sweep(s, now=NOW, stamps=FixtureStamps())
    assert gone["heartbeats"] == [] and gone["refused_heartbeats"] == [], "the sweep wrote into a case whose database is gone"
    assert not path.exists(), "the sweep recreated a case database that was gone"
    assert gone["not_held"][0]["text"].startswith("NOT HELD · the registry says open and the case database is absent")
    assert "this run exits 1" in gone["not_held"][0]["text"] and sweep_mod.exit_code(gone) == 1, "an open case with no database left the run at exit 0"


def break_not_held_read_as_held(ctx):
    real = sweep_mod.survey

    def trusting(store, now):
        found = real(store, now)
        found["held"] = found["held"] + [row["case_id"] for row in found["not_held"]]
        found["not_held"] = []
        return found

    ctx.mp.setattr(sweep_mod, "survey", trusting)


def break_failed_shred_read_as_held(ctx):
    ctx.mp.setattr(sweep_mod, "is_held", lambda state, present: state != "shredded" and present)


def break_open_without_database_exits_0(ctx):
    ctx.mp.setattr(sweep_mod, "unaccounted", lambda state, present: False)


def test_no_heartbeat_into_a_case_not_held(ctx):
    check_no_heartbeat_into_a_case_not_held(ctx)


# -- a registry date the sweep cannot read is refused, and the run goes on -------------------------


def check_unreadable_date_refused_and_the_run_goes_on(ctx):
    s = ctx.built()
    unreadable = (
        ("retain_until", {"retain_until": "not-a-date", "frozen_until": None}),
        ("frozen_until", {"retain_until": "2026-01-01", "frozen_until": "soon"}),
    )
    for field, cols in unreadable:
        _set_registry(s, **cols)
        beats = len(_heartbeats(s))
        try:
            report = sweep_mod.sweep(s, now=NOW, stamps=FixtureStamps())
        except (ValueError, TypeError, AttributeError) as exc:
            raise AssertionError(f"the sweep crashed on a {field} it cannot read, before any heartbeat: {type(exc).__name__}") from exc
        assert [(row["field"], row["refusal"]) for row in report["unreadable"]] == [(field, "SWEEP_REFUSED_DATE_UNREADABLE")], report
        assert report["unreadable"][0]["text"].startswith(f"DATE UNREADABLE, NOT SWEPT · {field}"), report["unreadable"]
        assert report["due"] == [] and report["skipped_frozen"] == [], "a case whose date cannot be read was decided anyway"
        assert len(_heartbeats(s)) == beats + 1, "a held case with an unreadable date got no heartbeat"
        assert sweep_mod.exit_code(report) == 1, "a run that could not read a held case's date exited 0"


def break_unreadable_date_crashes_the_run(ctx):
    ctx.mp.setattr(sweep_mod, "registry_instant", lambda day: retention.parse_ts(retention.date_instant(day)))


def break_unreadable_date_exits_0(ctx):
    real = sweep_mod.exit_code
    ctx.mp.setattr(sweep_mod, "exit_code", lambda report: real(dict(report, unreadable=[])))


def test_unreadable_date_refused_and_the_run_goes_on(ctx):
    check_unreadable_date_refused_and_the_run_goes_on(ctx)


# -- a heartbeat the door refuses is rendered with its legal moves, and that run exits 1 -----------


def check_refused_heartbeat_is_rendered_and_the_run_exits_1(ctx):
    s = ctx.built()
    beats = len(_heartbeats(s))
    # On LOCAL the door lands a system event only in a case the registry marks synthetic, so it refuses this one.
    _set_registry(s, synthetic=0)
    report = sweep_mod.sweep(s, now=NOW, stamps=FixtureStamps())
    assert report["heartbeats"] == [] and len(_heartbeats(s)) == beats, "a heartbeat landed where the door refuses one"
    assert [row["refusal"] for row in report["refused_heartbeats"]] == ["ACT_LOCAL_SYNTHETIC_CASE_ONLY"], report["refused_heartbeats"]
    row = report["refused_heartbeats"][0]
    assert row["case_id"] == CASE and row["text"].startswith("HEARTBEAT REFUSED · "), row
    assert row["render"].startswith("Refused ACT_LOCAL_SYNTHETIC_CASE_ONLY: ") and "Legal moves: " in row["render"], row["render"]
    assert sweep_mod.exit_code(report) == 1, "a run whose heartbeat the door refused exited 0"
    # The report says no heartbeat was written, and prints the refusal with its legal moves.
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        sweep_mod.print_report(report)
    assert out.getvalue().startswith("no heartbeat written at 2026-01-20T12:00:00Z: the door refused it in 1 case(s)"), out.getvalue()
    assert row["text"] in err.getvalue() and row["render"] in err.getvalue(), "the refusal's text and legal moves were not printed"


def break_refused_heartbeat_exits_0(ctx):
    real = sweep_mod.exit_code
    ctx.mp.setattr(sweep_mod, "exit_code", lambda report: real(dict(report, refused_heartbeats=[])))


def break_refused_heartbeat_as_a_bare_code(ctx):
    def bare(case_id, refusal):
        return {"case_id": case_id, "refusal": refusal.code, "render": refusal.code, "text": f"{case_id[:8]}: {refusal.code}"}

    ctx.mp.setattr(sweep_mod, "refused_heartbeat", bare)


def break_refused_run_reported_as_written(ctx):
    real = sweep_mod.print_report

    def as_written(report):
        print(f"heartbeat written in {len(report['heartbeats'])} case(s) at {report['now']}, next due {report['next_due']}")
        real(report)

    ctx.mp.setattr(sweep_mod, "print_report", as_written)


def test_refused_heartbeat_is_rendered_and_the_run_exits_1(ctx):
    check_refused_heartbeat_is_rendered_and_the_run_exits_1(ctx)


# -- verify_shred: five dated facts, a refusal while unratified, and no verified shred -------------


def check_verify_shred_runs_checks_and_refuses_unratified(ctx):
    s = ctx.built()
    result = verify_shred.verify(s, CASE, now=NOW, stamps=FixtureStamps())
    by_id = {c["id"]: c for c in result["checks"]}
    assert set(by_id) == {1, 2, 3, 4, 5}
    assert by_id[1]["outcome"] == "FAIL" and "not_found" in by_id[1]["why"], "check 1 passed or did not name not_found"
    assert by_id[2]["outcome"] == "NOT RUN", by_id[2]
    assert by_id[3]["outcome"] == "FAIL" and "row(s)" in by_id[3]["why"], "check 3 did not fail on a present table"
    assert by_id[4]["outcome"] == "FAIL" and "no tombstone" in by_id[4]["why"], "check 4 did not fail on an open case"
    assert by_id[5]["outcome"] == "NOT RUN" and "U-11" in by_id[5]["why"], by_id[5]
    assert all(c["checked_at"] == "2026-01-20T12:00:00Z" for c in result["checks"]), "a fact carries no date, or another one"
    assert not result["all_passed"] and not result["stamped"]
    assert result["verdict"].startswith("Refused VERIFY_SHRED_UNRATIFIED"), result["verdict"]
    assert verify_shred.exit_code(result) == 1
    # A stamped fixture with checks that failed or did not run is NOT VERIFIED, never a pass.
    stamped = verify_shred.verify(s, CASE, now=NOW, stamps=FixtureStamps(fixture=True))
    assert stamped["stamped"] and not stamped["all_passed"], stamped
    assert stamped["verdict"].startswith("NOT VERIFIED: check 1 key_destruction FAIL; check 2 object_absence NOT RUN"), stamped["verdict"]
    assert verify_shred.exit_code(stamped) == 1, "a run with a check that failed or did not run exited 0"


def break_not_found_read_as_pass(ctx):
    def passing(store, case_id, now):
        return verify_shred._fact(1, "PASS", "not_found", now)

    ctx.mp.setattr(verify_shred, "check_key_destruction", passing)


def break_not_run_counted_as_passed(ctx):
    ctx.mp.setattr(verify_shred, "exit_code", lambda result: 0 if result["stamped"] else 1)


def test_verify_shred_runs_checks_and_refuses_unratified(ctx):
    check_verify_shred_runs_checks_and_refuses_unratified(ctx)


# -- check 2: an object that remains fails, and no object on disk is not a pass --------------------


def check_object_absence_is_never_a_pass_here(ctx):
    s = ctx.built()
    none = verify_shred.check_object_absence(s, CASE, NOW)
    assert none["outcome"] == "NOT RUN" and "SR-U1" in none["why"], "no object on disk read as a pass, with no count to compare"
    folder = s.root / db.BLOBS_DIR / CASE / "kept"
    folder.mkdir(parents=True)
    (folder / "object").write_bytes(b"left behind")
    left = verify_shred.check_object_absence(s, CASE, NOW)
    assert left["outcome"] == "FAIL" and left["why"].startswith("1 object(s) remain"), "an object left on disk did not fail check 2"
    # A file named witness in the case's blob folder is an object check 2 counts and nothing check 1 reads.
    before = verify_shred.check_key_destruction(s, CASE, NOW)
    (s.root / db.BLOBS_DIR / CASE / "witness").write_bytes(b"not a witness")
    assert verify_shred.check_key_destruction(s, CASE, NOW) == before, "check 1 read a path inside the case's blob folder"
    both = verify_shred.check_object_absence(s, CASE, NOW)
    assert both["outcome"] == "FAIL" and both["why"].startswith("2 object(s) remain"), both


def break_no_object_read_as_pass(ctx):
    real = verify_shred.check_object_absence

    def passing(store, case_id, now):
        fact = real(store, case_id, now)
        return verify_shred._fact(2, "PASS", fact["why"], now) if fact["outcome"] == "NOT RUN" else fact

    ctx.mp.setattr(verify_shred, "check_object_absence", passing)


def break_objects_not_counted(ctx):
    ctx.mp.setattr(verify_shred, "_objects", lambda store, case_id: 0)


def break_witness_sought_in_the_blob_folder(ctx):
    real = verify_shred.check_key_destruction

    def sought(store, case_id, now):
        if (store.root / db.BLOBS_DIR / case_id / "witness").is_file():
            return verify_shred._fact(1, "FAIL", "no Encryptor is configured, so no decrypt attempt can be made", now)
        return real(store, case_id, now)

    ctx.mp.setattr(verify_shred, "check_key_destruction", sought)


def test_object_absence_is_never_a_pass_here(ctx):
    check_object_absence_is_never_a_pass_here(ctx)


# -- check 3: only absence passes; rows, zero rows, a sidecar left on disk and an unreadable file all fail


def check_schema_absence_passes_only_on_absence(ctx):
    # A store path carrying '#': the read-only open still reaches the case database and finds its rows.
    s = ctx.built("st#ore")
    present = verify_shred.check_schema_absence(s, CASE, NOW)
    assert present["outcome"] == "FAIL" and "row(s)" in present["why"], "a '#' in the store path hid the case database"
    path = s.case_file(CASE)
    s.detach_case()
    # Every declared table gone but one, and that one empty: it exists, which is not absence.
    _drop(path, [t for t in CASE_TABLES if t != "workspace_kv"])
    one_left = verify_shred.check_schema_absence(s, CASE, NOW)
    assert one_left["outcome"] == "FAIL" and "workspace_kv returned zero rows" in one_left["why"], one_left
    _drop(path, ["workspace_kv"])
    dropped = verify_shred.check_schema_absence(s, CASE, NOW)
    assert dropped["outcome"] == "PASS" and "no such table" in dropped["why"], dropped
    # A table the DDL does not declare is queried by no name; the schema still lists it, and that is not absence.
    _run(path, "CREATE TABLE claim_old (x)", "INSERT INTO claim_old VALUES (1)")
    undeclared = verify_shred.check_schema_absence(s, CASE, NOW)
    assert undeclared["outcome"] == "FAIL" and "still lists 1 object(s)" in undeclared["why"], undeclared
    _run(path, "DROP TABLE claim_old")
    # A view under a declared name that selects from a missing table raises the error a table that is gone raises.
    _run(path, f"CREATE VIEW {CASE_TABLES[0]} AS SELECT * FROM never_there")
    view = verify_shred.check_schema_absence(s, CASE, NOW)
    assert view["outcome"] == "FAIL" and "still lists 1 object(s)" in view["why"], view
    _run(path, f"DROP VIEW {CASE_TABLES[0]}")
    # A view under a declared name that raises another error is a database that could not be read, not one that is gone.
    _run(path, f"CREATE VIEW {CASE_TABLES[0]} AS SELECT no_such_function(1)")
    broken = verify_shred.check_schema_absence(s, CASE, NOW)
    assert broken["outcome"] == "FAIL" and "could not be read (OperationalError)" in broken["why"], broken
    _run(path, f"DROP VIEW {CASE_TABLES[0]}")
    again = verify_shred.check_schema_absence(s, CASE, NOW)
    assert again["outcome"] == "PASS", again
    # A cold rollback journal beside the emptied database: no query sees it, and it can hold pages of the case.
    journal = path.with_name(path.name + "-journal")
    journal.write_bytes(b"\x00" * 512 + b"pages of the case " * 40)
    beside = verify_shred.check_schema_absence(s, CASE, NOW)
    assert beside["outcome"] == "FAIL" and "(-journal)" in beside["why"], beside
    journal.unlink()
    assert verify_shred.check_schema_absence(s, CASE, NOW)["outcome"] == "PASS"
    # A file that is no database cannot be read, and that is not the same as gone.
    path.write_bytes(b"this is not a database. " * 64)
    unreadable = verify_shred.check_schema_absence(s, CASE, NOW)
    assert unreadable["outcome"] == "FAIL" and "could not be read" in unreadable["why"], unreadable
    path.unlink()
    gone = verify_shred.check_schema_absence(s, CASE, NOW)
    assert gone["outcome"] == "PASS" and "not on disk" in gone["why"], gone
    # The database file gone and a file SQLite keeps beside it left: each can hold pages of the case, and none is absence.
    for suffix in SIDECARS:
        sidecar = path.with_name(path.name + suffix)
        sidecar.write_bytes(b"pages of the case " * 40)
        left = verify_shred.check_schema_absence(s, CASE, NOW)
        assert left["outcome"] == "FAIL" and f"({suffix})" in left["why"], left
        sidecar.unlink()
    assert verify_shred.check_schema_absence(s, CASE, NOW)["outcome"] == "PASS"


def break_hash_ends_the_uri(ctx):
    ctx.mp.setattr(verify_shred, "_open_readonly", lambda path: sqlite3.connect("file:" + path.as_posix() + "?mode=ro", uri=True))


def break_zero_rows_read_as_absence(ctx):
    real = verify_shred._rows
    ctx.mp.setattr(verify_shred, "_rows", lambda conn, table: real(conn, table) or None)


def break_only_the_payload_table_read(ctx):
    ctx.mp.setattr(verify_shred, "case_tables", lambda: ("event_payload",))


def break_any_error_read_as_gone(ctx):
    ctx.mp.setattr(verify_shred, "_table_gone", lambda exc: True)


def break_listed_objects_not_counted(ctx):
    ctx.mp.setattr(verify_shred, "_listed", lambda conn: 0)


def break_sidecar_not_seen(ctx):
    ctx.mp.setattr(verify_shred, "_sidecars", lambda path: [])


def test_schema_absence_passes_only_on_absence(ctx):
    check_schema_absence_passes_only_on_absence(ctx)


def check_schema_absence_looks_for_a_sidecar_before_its_open(ctx):
    # A held case at rest, with its rows. What this check reads: verify_shred's one open of a case database,
    # _open_readonly, is not reached while a sidecar is on disk, and the run leaves no file in the cases folder. A
    # read-only open with a -wal beside the database was seen to leave a -shm, so a check that opens first writes
    # where it reads. A read that goes around _open_readonly and writes nothing is not seen here.
    s = ctx.built()
    path = s.case_file(CASE)
    s.detach_case()
    opened = []
    real = verify_shred._open_readonly
    ctx.mp.setattr(verify_shred, "_open_readonly", lambda p: (opened.append(p), real(p))[1])
    folder = sorted(p.name for p in path.parent.iterdir())
    for suffix in SIDECARS:
        sidecar = path.with_name(path.name + suffix)
        sidecar.write_bytes(b"pages of the case " * 40)
        fact = verify_shred.check_schema_absence(s, CASE, NOW)
        assert fact["outcome"] == "FAIL" and f"({suffix})" in fact["why"], fact
        assert not opened, f"check 3 opened the case database with a {suffix} file beside it"
        sidecar.unlink()
        assert sorted(p.name for p in path.parent.iterdir()) == folder, "check 3 left a file in the cases folder"
    # With no sidecar the database is opened and its rows fail the check, so the spy sees an open when one happens.
    held = verify_shred.check_schema_absence(s, CASE, NOW)
    assert held["outcome"] == "FAIL" and "row(s)" in held["why"], held
    assert opened, "the spy did not see the open this check stands on"


def break_sidecars_read_after_an_open(ctx):
    real = verify_shred._sidecars

    def late(path):
        if verify_shred._on_disk(path):
            verify_shred._open_readonly(path).close()
        return real(path)

    ctx.mp.setattr(verify_shred, "_sidecars", late)


def test_schema_absence_looks_for_a_sidecar_before_its_open(ctx):
    check_schema_absence_looks_for_a_sidecar_before_its_open(ctx)


# -- check 4: the tombstone, then a receipt after the last stratum-1 event, and still no pass -------


def check_skeleton_presence_needs_tombstone_and_later_receipt(ctx):
    s = ctx.built()
    still_open = verify_shred.check_skeleton_presence(s, CASE, NOW)
    assert still_open["outcome"] == "FAIL" and "the registry says the case is open" in still_open["why"], still_open
    _set_registry(s, state="shred_failed")
    failed = verify_shred.check_skeleton_presence(s, CASE, NOW)
    assert failed["outcome"] == "FAIL" and "RT-11" in failed["why"], failed
    # The tombstone and the corpus's receipt row are both there, and the receipt hash has no stated preimage.
    _set_registry(s, state="shredded")
    present = verify_shred.check_skeleton_presence(s, CASE, NOW)
    assert present["outcome"] == "NOT RUN" and "U-09" in present["why"], "a receipt hash with no stated preimage read as a pass"
    # The tombstone with no receipt row at all.
    bare = ctx.built("bare", _corpus(skip=("system-shred-receipt",)))
    _set_registry(bare, state="shredded")
    no_receipt = verify_shred.check_skeleton_presence(bare, CASE, NOW)
    assert no_receipt["outcome"] == "FAIL" and "RT-10" in no_receipt["why"], "the tombstone with no receipt row did not fail"
    # A receipt written before the case's last stratum-1 event records no shred of what followed it.
    early = ctx.built("early", _corpus(second="system-shred-receipt"))
    _set_registry(early, state="shredded")
    before = verify_shred.check_skeleton_presence(early, CASE, NOW)
    assert before["outcome"] == "FAIL" and "RT-10" in before["why"], "a receipt older than the case's last payload was counted"


def break_tombstone_not_required(ctx):
    ctx.mp.setattr(verify_shred, "_tombstoned", lambda reg: True)


def break_receipt_row_not_required(ctx):
    ctx.mp.setattr(verify_shred, "receipts_after_last_payload", lambda store, case_id: 1)


def break_earlier_receipt_counted(ctx):
    ctx.mp.setattr(verify_shred, "_follows", lambda seq, last: True)


def break_present_string_read_as_pass(ctx):
    real = verify_shred.check_skeleton_presence

    def passing(store, case_id, now):
        fact = real(store, case_id, now)
        return verify_shred._fact(4, "PASS", fact["why"], now) if fact["outcome"] == "NOT RUN" else fact

    ctx.mp.setattr(verify_shred, "check_skeleton_presence", passing)


def test_skeleton_presence_needs_tombstone_and_later_receipt(ctx):
    check_skeleton_presence_needs_tombstone_and_later_receipt(ctx)


# -- check 5: the canary read in full against three counts taken before the shred -------------------


def check_anti_overreach_reads_the_inventory(ctx):
    s = ctx.built()
    inventory = verify_shred.canary_inventory(s, CASE)
    assert inventory["payloads"] > inventory["claims"] > 0 and inventory["blobs"] == 0, inventory
    same = verify_shred.check_anti_overreach(s, CASE, inventory, NOW)
    assert same["outcome"] == "PASS", same
    # An object that appeared under the canary.
    added = s.root / db.BLOBS_DIR / CASE / "added"
    added.parent.mkdir(parents=True)
    added.write_bytes(b"not there before")
    more = verify_shred.check_anti_overreach(s, CASE, inventory, NOW)
    assert more["outcome"] == "FAIL" and "blobs 0 to 1" in more["why"], "a canary that gained an object passed check 5"
    added.unlink()
    # A payload row that is no claim and no item, gone.
    spare = s.conn.execute(
        "SELECT event_id FROM event_payload WHERE event_id NOT IN (SELECT claim_id FROM claim) "
        "AND event_id NOT IN (SELECT event_id FROM item) ORDER BY event_id LIMIT 1").fetchone()[0]
    s.conn.execute("DELETE FROM event_payload WHERE event_id = ?", (spare,))
    s.conn.commit()
    fewer = verify_shred.check_anti_overreach(s, CASE, inventory, NOW)
    assert fewer["outcome"] == "FAIL" and f"payloads {inventory['payloads']} to {inventory['payloads'] - 1}" in fewer["why"], fewer
    # A claim row gone, with its payload left in place.
    inventory = verify_shred.canary_inventory(s, CASE)
    s.conn.execute("DELETE FROM claim WHERE claim_id = (SELECT claim_id FROM claim ORDER BY claim_id LIMIT 1)")
    s.conn.commit()
    lost = verify_shred.check_anti_overreach(s, CASE, inventory, NOW)
    assert lost["outcome"] == "FAIL" and f"claims {inventory['claims']} to {inventory['claims'] - 1}" in lost["why"], lost
    # No canary, or an inventory missing one of its counts, is not run and is not a pass.
    inventory = verify_shred.canary_inventory(s, CASE)
    assert verify_shred.check_anti_overreach(s, None, inventory, NOW)["outcome"] == "NOT RUN"
    for key in COUNTS:
        partial = {k: v for k, v in inventory.items() if k != key}
        unnamed = verify_shred.check_anti_overreach(s, CASE, partial, NOW)
        assert unnamed["outcome"] == "NOT RUN" and "U-11" in unnamed["why"], f"an inventory with no {key} count was compared"
    # A table of the canary gone: its counts are unchanged and it is no longer readable in full.
    path = s.case_file(CASE)
    s.detach_case()
    _drop(path, ["node"])
    torn = verify_shred.check_anti_overreach(s, CASE, inventory, NOW)
    assert torn["outcome"] == "FAIL" and "not fully readable" in torn["why"], "a canary missing a table passed check 5"


def break_object_count_ignored(ctx):
    ctx.mp.setattr(verify_shred, "INVENTORY_KEYS", ("payloads", "claims"))


def break_payload_count_ignored(ctx):
    ctx.mp.setattr(verify_shred, "INVENTORY_KEYS", ("claims", "blobs"))


def break_claim_count_ignored(ctx):
    ctx.mp.setattr(verify_shred, "INVENTORY_KEYS", ("payloads", "blobs"))


def break_canary_tables_not_all_read(ctx):
    ctx.mp.setattr(verify_shred, "case_tables", lambda: ("event_payload", "claim"))


def test_anti_overreach_reads_the_inventory(ctx):
    check_anti_overreach_reads_the_inventory(ctx)


# -- verify refuses a case never held here, a canary that is the case, and a string that is no id --


def check_verify_refuses_what_it_cannot_witness(ctx):
    s = ctx.built()
    never_held = str(uuid.uuid4())
    stranger = refusal_of(verify_shred.verify, s, never_held, now=NOW, stamps=FixtureStamps())
    assert stranger.code == "VERIFY_SHRED_CASE_NEVER_HELD", stranger.code
    for canary in (CASE, CASE.upper()):
        own = refusal_of(verify_shred.verify, s, CASE, canary=canary, now=NOW, stamps=FixtureStamps())
        assert own.code == "VERIFY_SHRED_CANARY_IS_THE_CASE", own.code
    typed = "a-string-typed-by-hand-that-is-no-case-id"
    for kwargs in ({"case_id": typed}, {"case_id": CASE, "canary": typed}):
        no_id = refusal_of(verify_shred.verify, s, now=NOW, stamps=FixtureStamps(), **kwargs)
        assert no_id.code == "CASE_ID_INVALID", no_id.code
        assert typed not in no_id.render(), "a refusal echoed a string that was typed where a case id belongs"


def break_never_held_case_verified(ctx):
    ctx.mp.setattr(verify_shred, "refuse_unless_held", lambda store, case_id: None)


def break_case_named_as_its_own_canary(ctx):
    ctx.mp.setattr(verify_shred, "refuse_own_canary", lambda store, case_id, canary: None)


def test_verify_refuses_what_it_cannot_witness(ctx):
    check_verify_refuses_what_it_cannot_witness(ctx)


# -- the header's sweep line stands only on a run that has happened ---------------------------------


def check_header_line_stands_only_on_a_run_that_happened(ctx):
    s = ctx.built()
    # The corpus heartbeat ran at 10:17:00Z on 2026-01-15 and names 10:47:00Z as its next due time.
    current = reads.sweep_state(s.conn, CASE, _at("2026-01-15T10:30:00Z"))
    assert current["vouch"] is False and current["not_read"] == 0, current
    assert current["text"].startswith("retention sweep ran 2026-01-15T10:17:00Z, next due 2026-01-15T10:47:00Z"), current["text"]
    late = reads.sweep_state(s.conn, CASE, NOW)
    assert late["vouch"] is True and late["text"].startswith("RETENTION SWEEP HAS NOT RUN SINCE 2026-01-15T10:17:00Z"), late
    # At the due time itself the line is degraded: RET-R7 gives no grace.
    at_due = reads.sweep_state(s.conn, CASE, _at("2026-01-15T10:47:00Z"))
    assert at_due["vouch"] is True and "HAS NOT RUN SINCE" in at_due["text"], "the line gave a grace period at the due time"
    # Before the heartbeat's own time, it records no run that has happened.
    early = reads.sweep_state(s.conn, CASE, _at("2026-01-15T10:00:00Z"))
    assert early["ran"] is None and early["not_read"] == 1 and early["vouch"] is True, "a heartbeat dated after now was read as a run"
    assert early["text"].startswith("NO RETENTION SWEEP RUN IS ON RECORD HERE"), early["text"]
    never = ctx.built("nobeat", _corpus(skip=("system-sweep-heartbeat",)))
    absent = reads.sweep_state(never.conn, CASE, NOW)
    assert absent["vouch"] is True and absent["text"].startswith("RETENTION SWEEP HAS NEVER RUN HERE"), absent
    # The door refuses a heartbeat whose times cannot be read, so these rows are given to the line directly.
    beat = _heartbeats(s)[-1]
    at = _at("2026-01-15T10:30:00Z")
    mixed = reads.sweep_line([beat, dict(beat, ts="2026-02-01T00:00:00Z", seq=beat["seq"] + 1)], at)
    assert mixed["ran"] == "2026-01-15T10:17:00Z" and mixed["not_read"] == 1 and mixed["vouch"] is True, mixed
    assert "1 heartbeat(s) carrying a time after now" in mixed["text"], mixed["text"]
    no_time = reads.sweep_line([dict(beat, ts="yesterday")], at)
    assert no_time["ran"] is None and no_time["vouch"] is True and no_time["not_read"] == 1, no_time
    try:
        no_due = reads.sweep_line([dict(beat, payload=dict(beat["payload"], next_due="tomorrow"))], at)
    except (ValueError, TypeError, AttributeError) as exc:
        raise AssertionError(f"the header line crashed on a next due time it cannot read: {type(exc).__name__}") from exc
    assert no_due["vouch"] is True and "CANNOT BE READ" in no_due["text"], "a next due time that cannot be read was vouched for"
    # Two runs out of arrival order: the later ts is the latest run, whatever its seq.
    later = dict(beat, ts="2026-01-15T10:25:00Z", seq=beat["seq"] - 1, payload=dict(beat["payload"], next_due="2026-01-15T10:55:00Z"))
    out_of_order = reads.sweep_line([later, beat], at)
    assert out_of_order["ran"] == "2026-01-15T10:25:00Z" and out_of_order["vouch"] is False, "the latest run was read by arrival, not by its time"
    # Two runs at one ts: the later arrival is the latest run.
    same = dict(beat, seq=beat["seq"] + 1, payload=dict(beat["payload"], next_due="2026-01-15T10:20:00Z"))
    tied = reads.sweep_line([beat, same], at)
    assert tied["vouch"] is True and "HAS NOT RUN SINCE" in tied["text"], "two runs at one time were not settled by arrival"
    # A heartbeat row that lacks a ts, a seq or an object payload reads as carrying none; none of them raises.
    odd = {
        "a payload that is a list": dict(beat, payload=[1]),
        "a payload that is a string": dict(beat, payload="x"),
        "no payload": {k: v for k, v in beat.items() if k != "payload"},
        "no ts": {k: v for k, v in beat.items() if k != "ts"},
        "no seq": {k: v for k, v in beat.items() if k != "seq"},
    }
    lines = {}
    for name, row in odd.items():
        try:
            lines[name] = reads.sweep_line([row], at)
        except (KeyError, AttributeError, TypeError) as exc:
            raise AssertionError(f"the header line crashed on a heartbeat row with {name}: {type(exc).__name__}") from exc
    for name in ("a payload that is a list", "a payload that is a string", "no payload"):
        assert lines[name]["vouch"] is True and "CANNOT BE READ" in lines[name]["text"], f"{name} was vouched for: {lines[name]['text']}"
    assert lines["no ts"]["ran"] is None and lines["no ts"]["not_read"] == 1 and lines["no ts"]["vouch"] is True, lines["no ts"]
    assert lines["no seq"]["ran"] == "2026-01-15T10:17:00Z" and lines["no seq"]["vouch"] is False, lines["no seq"]
    # The mark is the stylesheet's, written on the server's flag. A line carrying its own would render it twice.
    for line in (current, late, at_due, early, absent, mixed, no_time, no_due, out_of_order, tied, *lines.values()):
        assert VOUCH_MARK not in line["text"], f"the line carries the mark the header's stylesheet also writes: {line['text']}"
    app_js = (routes.STATIC / "app.js").read_text(encoding="utf-8")
    assert 'class: r.body.sweep && r.body.sweep.vouch ? "vouch" : ""' in app_js, "the sweep line is painted red without its flag"
    app_css = (routes.STATIC / "app.css").read_text(encoding="utf-8")
    assert '.vouch::before { content: "' + VOUCH_MARK + ' "; }' in app_css, "the stylesheet writes no mark on a line the system does not vouch for"


def break_later_heartbeat_read_as_a_run(ctx):
    ctx.mp.setattr(reads, "ran_by", lambda beat, at: reads.instant(beat["ts"]))


def break_unreadable_due_time_read_as_not_due(ctx):
    real = reads.instant
    ctx.mp.setattr(reads, "instant", lambda value: real(value) or FAR)


def break_overdue_read_as_current(ctx):
    ctx.mp.setattr(reads, "overdue", lambda due, at: False)


def break_grace_given_at_the_due_time(ctx):
    ctx.mp.setattr(reads, "overdue", lambda due, at: due < at)


def break_latest_run_by_arrival_alone(ctx):
    ctx.mp.setattr(reads, "latest_run", lambda runs: max(runs, key=lambda run: run[1])[2])


def break_latest_run_by_time_alone(ctx):
    ctx.mp.setattr(reads, "latest_run", lambda runs: max(runs, key=lambda run: run[0])[2])


def break_payload_trusted_as_an_object(ctx):
    ctx.mp.setattr(reads, "next_due_of", lambda beat: beat["payload"].get("next_due"))


def break_ts_trusted_to_be_there(ctx):
    def strict(beat, at):
        ts = reads.instant(beat["ts"])
        return ts if ts is not None and ts <= at else None

    ctx.mp.setattr(reads, "ran_by", strict)


def break_seq_trusted_to_be_there(ctx):
    ctx.mp.setattr(reads, "arrival", lambda beat: beat["seq"])


def break_mark_written_by_the_line_too(ctx):
    real = reads.sweep_line

    def marked(beats, at):
        line = real(beats, at)
        return dict(line, text=f"{VOUCH_MARK} {line['text']}") if line["vouch"] else line

    ctx.mp.setattr(reads, "sweep_line", marked)


def test_header_line_stands_only_on_a_run_that_happened(ctx):
    check_header_line_stands_only_on_a_run_that_happened(ctx)


CONTROLS = [
    ("the heartbeat not written", check_sweep_writes_heartbeat_and_deletes_nothing, break_heartbeat_not_written),
    ("the finding check lifted", check_due_case_refused_in_order, break_finding_check_lifted),
    ("a case due only after the instant retain_until names", check_due_case_refused_in_order, break_due_only_after_the_instant),
    ("the freeze not read", check_frozen_case_skipped, break_freeze_not_read),
    ("a case not held read as held", check_no_heartbeat_into_a_case_not_held, break_not_held_read_as_held),
    ("a failed shred read as held", check_no_heartbeat_into_a_case_not_held, break_failed_shred_read_as_held),
    ("an open case with no database exits 0", check_no_heartbeat_into_a_case_not_held, break_open_without_database_exits_0),
    ("an unreadable date crashes the run", check_unreadable_date_refused_and_the_run_goes_on, break_unreadable_date_crashes_the_run),
    ("an unreadable date exits 0", check_unreadable_date_refused_and_the_run_goes_on, break_unreadable_date_exits_0),
    ("a refused heartbeat exits 0", check_refused_heartbeat_is_rendered_and_the_run_exits_1, break_refused_heartbeat_exits_0),
    ("a refused heartbeat reported as a bare code", check_refused_heartbeat_is_rendered_and_the_run_exits_1, break_refused_heartbeat_as_a_bare_code),
    ("a run with every heartbeat refused reported as written", check_refused_heartbeat_is_rendered_and_the_run_exits_1, break_refused_run_reported_as_written),
    ("not_found read as a pass", check_verify_shred_runs_checks_and_refuses_unratified, break_not_found_read_as_pass),
    ("a check not run counted as passed", check_verify_shred_runs_checks_and_refuses_unratified, break_not_run_counted_as_passed),
    ("no object on disk read as a pass", check_object_absence_is_never_a_pass_here, break_no_object_read_as_pass),
    ("an object on disk not counted", check_object_absence_is_never_a_pass_here, break_objects_not_counted),
    ("the witness sought in the case's blob folder", check_object_absence_is_never_a_pass_here, break_witness_sought_in_the_blob_folder),
    ("a # in the store path ends the URI", check_schema_absence_passes_only_on_absence, break_hash_ends_the_uri),
    ("zero rows read as absence", check_schema_absence_passes_only_on_absence, break_zero_rows_read_as_absence),
    ("only the payload table read", check_schema_absence_passes_only_on_absence, break_only_the_payload_table_read),
    ("any query error read as a table that is gone", check_schema_absence_passes_only_on_absence, break_any_error_read_as_gone),
    ("an object the schema still lists read as absence", check_schema_absence_passes_only_on_absence, break_listed_objects_not_counted),
    ("a file SQLite keeps beside the database read as absence", check_schema_absence_passes_only_on_absence, break_sidecar_not_seen),
    ("the look for a sidecar made after the database is opened", check_schema_absence_looks_for_a_sidecar_before_its_open, break_sidecars_read_after_an_open),
    ("the tombstone not required", check_skeleton_presence_needs_tombstone_and_later_receipt, break_tombstone_not_required),
    ("the receipt row not required", check_skeleton_presence_needs_tombstone_and_later_receipt, break_receipt_row_not_required),
    ("a receipt before the last payload counted", check_skeleton_presence_needs_tombstone_and_later_receipt, break_earlier_receipt_counted),
    ("a present string read as a pass", check_skeleton_presence_needs_tombstone_and_later_receipt, break_present_string_read_as_pass),
    ("the object count ignored", check_anti_overreach_reads_the_inventory, break_object_count_ignored),
    ("the payload count ignored", check_anti_overreach_reads_the_inventory, break_payload_count_ignored),
    ("the claim count ignored", check_anti_overreach_reads_the_inventory, break_claim_count_ignored),
    ("a canary with a table gone read as unchanged", check_anti_overreach_reads_the_inventory, break_canary_tables_not_all_read),
    ("a case never held verified", check_verify_refuses_what_it_cannot_witness, break_never_held_case_verified),
    ("the case named as its own canary", check_verify_refuses_what_it_cannot_witness, break_case_named_as_its_own_canary),
    ("a heartbeat dated after now read as a run", check_header_line_stands_only_on_a_run_that_happened, break_later_heartbeat_read_as_a_run),
    ("an unreadable next due time read as not due", check_header_line_stands_only_on_a_run_that_happened, break_unreadable_due_time_read_as_not_due),
    ("an overdue sweep read as current", check_header_line_stands_only_on_a_run_that_happened, break_overdue_read_as_current),
    ("a grace period given at the due time", check_header_line_stands_only_on_a_run_that_happened, break_grace_given_at_the_due_time),
    ("the latest run read by arrival alone", check_header_line_stands_only_on_a_run_that_happened, break_latest_run_by_arrival_alone),
    ("the latest run read by time alone", check_header_line_stands_only_on_a_run_that_happened, break_latest_run_by_time_alone),
    ("a payload trusted to be an object", check_header_line_stands_only_on_a_run_that_happened, break_payload_trusted_as_an_object),
    ("a ts trusted to be there", check_header_line_stands_only_on_a_run_that_happened, break_ts_trusted_to_be_there),
    ("a seq trusted to be there", check_header_line_stands_only_on_a_run_that_happened, break_seq_trusted_to_be_there),
    ("the mark written by the line as well as the stylesheet", check_header_line_stands_only_on_a_run_that_happened, break_mark_written_by_the_line_too),
]
