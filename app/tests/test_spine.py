"""The spine: Run, Item, Claim, the append-only log, rebuild, and blobs."""

from __future__ import annotations

import hashlib
import re
import uuid
from pathlib import Path

from app import config
from app.store import blobs, db, project, replay
from app.store.project import Projector
from app.tests.helpers import CASE, corpus_events, count, eid_of, named, refusal_of, sql_error


# -- every claim resolves to an item and every item to a run ---------------------


def check_claims_resolve(ctx):
    s = ctx.built()
    claims = s.conn.execute("SELECT claim_id, item_id, run_id FROM claim").fetchall()
    assert len(claims) == 4
    for c in claims:
        item = s.conn.execute("SELECT run_id FROM item WHERE item_id = ?", (c["item_id"],)).fetchone()
        assert item is not None, "a claim names an item the store holds"
        assert item["run_id"] == c["run_id"]
        assert s.conn.execute("SELECT 1 FROM run WHERE run_id = ?", (item["run_id"],)).fetchone()
    events = corpus_events()
    named(events, "extract-claim-handle")["lineage"]["based_on"] = [eid_of("probe-run-start")]
    r = refusal_of(ctx.ingest, ctx.store("reparented"), events)
    assert "FAIL LINEAGE_PARENT_TYPE_INVALID" in r.detail


def break_claim_loses_its_run(ctx):
    real = Projector._claim

    def broken(self, env, p):
        real(self, env, p)
        self.c.execute("UPDATE claim SET run_id = 'unresolved' WHERE claim_id = ?", (env["event"]["event_id"],))

    ctx.mp.setattr(Projector, "_claim", broken)


def test_claims_resolve(ctx):
    check_claims_resolve(ctx)


# -- the seed run --------------------------------------------------------------------


def check_seed_run(ctx):
    s = ctx.built()
    run = s.conn.execute("SELECT * FROM run").fetchone()
    assert run["motivated_by"] is None
    assert run["subject_relation"] == "seed"
    assert run["pivot_depth"] == 0
    assert run["permitted_event_id"] == eid_of("collect-permitted")
    assert run["start_event_id"] == eid_of("probe-run-start")
    assert run["end_event_id"] == eid_of("probe-run-end")
    events = [e for e in corpus_events() if e["event"]["event_id"] != eid_of("collect-permitted")]
    r = refusal_of(ctx.ingest, ctx.store("no-permit"), events)
    assert "FAIL SUBJECT_NOT_AUTHORIZED" in r.detail
    events = corpus_events()
    named(events, "probe-run-start")["payload"]["target_selector_type"] = "email"
    r = refusal_of(ctx.ingest, ctx.store("retargeted"), events)
    assert "FAIL SUBJECT_NOT_AUTHORIZED" in r.detail


def break_relation_not_copied(ctx):
    real = Projector._run_start

    def broken(self, env, p):
        real(self, env, p)
        self.c.execute("UPDATE run SET subject_relation = NULL WHERE run_id = ?", (p.get("run_id"),))

    ctx.mp.setattr(Projector, "_run_start", broken)


def test_seed_run(ctx):
    check_seed_run(ctx)


# -- fusion only by a named human ----------------------------------------------------


def check_two_clusters_none_from_link(ctx):
    s = ctx.built()
    clusters = s.conn.execute("SELECT node_id, created_by_event_id FROM node WHERE kind = 'cluster'").fetchall()
    assert len(clusters) == 2
    for c in clusters:
        row = s.conn.execute(
            "SELECT event_type, event_subtype, producer FROM event_skeleton WHERE event_id = ?", (c["created_by_event_id"],)
        ).fetchone()
        assert (row["event_type"], row["event_subtype"]) == ("IDENTITY_EVENT", "CLUSTER")
        assert row["producer"] in config.LOCAL_HUMANS
    events = corpus_events()
    named(events, "identity-cluster")["source"]["producer"] = "connector-example"
    r = refusal_of(ctx.ingest, ctx.store("connector-cluster"), events)
    assert "FAIL PRODUCER_NOT_ALLOWED" in r.detail


def break_link_makes_a_cluster(ctx):
    real = Projector._link

    def broken(self, env, p):
        real(self, env, p)
        self._put_node({"node_id": env["event"]["event_id"], "kind": "cluster", "created_by_event_id": env["event"]["event_id"]})

    ctx.mp.setattr(Projector, "_link", broken)


def test_two_clusters_none_from_link(ctx):
    check_two_clusters_none_from_link(ctx)


# -- the log is append-only ------------------------------------------------------------


def _strip_triggers(ctx):
    real = db.ddl
    ctx.mp.setattr(db, "ddl", lambda section: [s for s in real(section) if not s.upper().startswith("CREATE TRIGGER")])


def check_skeleton_append_only(ctx):
    s = ctx.built()
    msg = sql_error(s.conn, "UPDATE event_skeleton SET producer = producer WHERE case_seq = 1")
    assert msg.startswith("EVENT_LOG_APPEND_ONLY")
    msg = sql_error(s.conn, "DELETE FROM event_skeleton WHERE case_seq = 1")
    assert msg.startswith("EVENT_LOG_APPEND_ONLY")
    assert count(s, "SELECT COUNT(*) FROM event_skeleton") == 44


def test_skeleton_append_only(ctx):
    check_skeleton_append_only(ctx)


def check_payload_update_refused(ctx):
    s = ctx.built()
    msg = sql_error(s.conn, "UPDATE event_payload SET payload_json = payload_json WHERE event_id = ?", (eid_of("adjudicate-note"),))
    assert msg.startswith("PAYLOAD_UPDATE_REFUSED")


def test_payload_update_refused(ctx):
    check_payload_update_refused(ctx)


def check_payload_delete_cascades(ctx):
    s = ctx.built()
    claim = eid_of("extract-claim-handle")
    assert count(s, "SELECT COUNT(*) FROM claim WHERE claim_id = ?", (claim,)) == 1
    s.conn.execute("DELETE FROM event_payload WHERE event_id = ?", (claim,))
    assert count(s, "SELECT COUNT(*) FROM claim WHERE claim_id = ?", (claim,)) == 0, "the claim row follows its payload"
    item = eid_of("probe-item-2")
    s.conn.execute("DELETE FROM event_payload WHERE event_id = ?", (item,))
    assert count(s, "SELECT COUNT(*) FROM item WHERE event_id = ?", (item,)) == 0


def break_foreign_keys_off(ctx):
    def off(conn, schema="main"):
        conn.execute("PRAGMA foreign_keys=OFF")
        conn.execute(f"PRAGMA {schema}.journal_mode=DELETE")

    ctx.mp.setattr(db, "set_pragmas", off)
    ctx.mp.setattr(db, "assert_pragmas", lambda conn, schemas=("main",): None)


def test_payload_delete_cascades(ctx):
    check_payload_delete_cascades(ctx)


def check_pragmas_asserted(ctx):
    s = ctx.built()
    assert s.conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    assert s.conn.execute("PRAGMA main.journal_mode").fetchone()[0] == "delete"
    assert s.conn.execute(f"PRAGMA {db.CASE_ALIAS}.journal_mode").fetchone()[0] == "delete"

    def wal(conn, schema="main"):
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute(f"PRAGMA {schema}.journal_mode=WAL")

    ctx.mp.setattr(db, "set_pragmas", wal)
    r = refusal_of(db.connect, ctx.tmp / "wal.sqlite")
    assert r.code == "STORE_PRAGMA_UNSET"


def break_pragma_assertion_removed(ctx):
    ctx.mp.setattr(db, "assert_pragmas", lambda conn, schemas=("main",): None)


def test_pragmas_asserted(ctx):
    check_pragmas_asserted(ctx)


# -- only the retention sweep deletes from event_payload ------------------------------

PAYLOAD_DELETE_RE = re.compile(r"DELETE\s+FROM\s+(?:\w+\.)?event_payload\b", re.IGNORECASE)


def payload_deleters(roots) -> list[str]:
    found = []
    for root in roots:
        for path in sorted(Path(root).rglob("*.py")):
            if "tests" in path.relative_to(root).parts:
                continue
            if PAYLOAD_DELETE_RE.search(path.read_text(encoding="utf-8")):
                found.append(path.name)
    return found


def check_no_payload_delete_in_app(ctx):
    roots = [config.REPO_ROOT / "app", *ctx.extra_roots]
    assert payload_deleters(roots) == [], "only runner/retention_sweep.py may delete from event_payload"


def break_a_module_that_deletes(ctx):
    root = ctx.tmp / "planted"
    root.mkdir()
    (root / "sweeper.py").write_text('SQL = "DELETE FROM event_payload WHERE 1"\n', encoding="utf-8")
    ctx.extra_roots.append(root)


def test_no_payload_delete_in_app(ctx):
    check_no_payload_delete_in_app(ctx)


# -- rebuild ---------------------------------------------------------------------------------


def check_rebuild_identical(ctx):
    s = ctx.built()
    first = replay.dump(s, CASE)
    replay.rebuild(s)
    assert replay.dump(s, CASE) == first, "a rebuild of an unswept store is byte-identical"
    assert replay.verify(s, ctx.tmp / "fresh") == {CASE: []}


def break_uuid4_node_ids(ctx):
    ctx.mp.setattr(project, "selector_node_id", lambda claim_event_id: str(uuid.uuid4()))


def test_rebuild_identical(ctx):
    check_rebuild_identical(ctx)


def check_planted_difference_detected(ctx):
    s = ctx.built()
    first = replay.dump(s, CASE)
    entity = named(corpus_events(), "adjudicate-promote")["payload"]["entity_id"]
    s.conn.execute("UPDATE node SET sector = 'phones' WHERE node_id = ?", (entity,))
    assert replay.dump(s, CASE) != first
    assert replay.verify(s, ctx.tmp / "fresh") == {CASE: ["node"]}, "a fresh replay names the planted table"
    replay.rebuild(s)
    assert replay.dump(s, CASE) == first, "the rebuild removes the planted difference"


def break_verify_compares_nothing(ctx):
    ctx.mp.setattr(replay, "_by_table", lambda data: {})


def test_planted_difference_detected(ctx):
    check_planted_difference_detected(ctx)


def check_verify_ignores_working_state(ctx):
    s = ctx.built()
    row = s.conn.execute("SELECT * FROM coverage_interval").fetchone()
    open_id = str(uuid.uuid5(uuid.UUID(CASE), "open working interval"))
    s.conn.execute(
        "INSERT INTO coverage_interval (interval_id, case_id, target_ref, t_start, last_verified_at, poll_interval_s, state) "
        "VALUES (?, ?, ?, ?, ?, 60, 'open')",
        (open_id, CASE, row["target_ref"], row["t_end"], row["t_end"]),
    )
    assert replay.verify(s, ctx.tmp / "fresh") == {CASE: []}, "an open working interval reads as a replay difference"
    assert open_id.encode() in replay.dump(s, CASE), "dump() no longer shows the working row a rebuild keeps"
    assert open_id.encode() not in replay.dump(s, CASE, working=False)


def break_verify_compares_working_state(ctx):
    real = replay.dump
    ctx.mp.setattr(replay, "dump", lambda store, case_id, working=True: real(store, case_id, True))


def test_verify_ignores_working_state(ctx):
    check_verify_ignores_working_state(ctx)


# -- blobs ---------------------------------------------------------------------------------------


class XorEncryptor:
    """A test double. It is not a cipher and nothing outside this file uses it."""

    def encrypt(self, case_id, plaintext):
        return bytes(b ^ 0x5A for b in plaintext)

    def decrypt(self, case_id, ciphertext):
        return bytes(b ^ 0x5A for b in ciphertext)


def check_blobs(ctx):
    data = b"synthetic fixture bytes for the blob test"
    local = blobs.BlobStore(ctx.tmp / "root", CASE, "LOCAL", XorEncryptor())
    r = refusal_of(local.put, data)
    assert r.code == "BLOB_WRITE_REFUSED" and "not ISOLATED" in r.detail
    assert not (ctx.tmp / "root").exists(), "a refused put writes nothing"
    iso = blobs.BlobStore(ctx.tmp / "root", CASE, "ISOLATED", None)
    assert "Encryptor" in refusal_of(iso.put, data).detail
    assert refusal_of(local.get, hashlib.sha256(data).hexdigest()).code == "BLOB_NOT_HELD"
    ok = blobs.BlobStore(ctx.tmp / "root", CASE, "ISOLATED", XorEncryptor())
    with ctx.mp.context() as m:
        m.setattr(blobs, "stamped", lambda criteria=blobs.REQUIRED_STAMPS: {c: False for c in criteria})
        assert "RT-4 is not stamped" in refusal_of(ok.put, data).detail
    assert not (ctx.tmp / "root").exists(), "no refused put wrote anything"
    # the positive arm: a fake Encryptor and a patched pin let put() through
    ctx.mp.setattr(blobs, "stamped", lambda criteria=blobs.REQUIRED_STAMPS: {c: True for c in criteria})
    sha = ok.put(data)
    assert ok.path(sha).read_bytes() != data, "the stored bytes are not the plaintext"
    assert ok.get(sha) == data
    stored = bytearray(ok.path(sha).read_bytes())
    stored[0] ^= 0x01
    ok.path(sha).write_bytes(bytes(stored))
    assert refusal_of(ok.get, sha).code == "BLOB_DIGEST_MISMATCH"


def break_put_conditions_removed(ctx):
    ctx.mp.setattr(blobs.BlobStore, "refusals", lambda self: [])


def test_blobs(ctx):
    check_blobs(ctx)


def test_blob_stamps_are_read_from_the_pin():
    """stamped() agrees with tools/pin_of_record.py on the working tree, whatever that says today."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("pin_for_test", blobs.PIN_TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    pin = module.read(config.REPO_ROOT)
    assert blobs.stamped() == {c: pin.criterion_stamped(c) for c in blobs.REQUIRED_STAMPS}


def test_corpus_items_hold_no_raw(ctx):
    s = ctx.built()
    states = {r[0] for r in s.conn.execute("SELECT blob_state FROM item")}
    assert states == {"absent"}
    assert not any((s.root / db.BLOBS_DIR).iterdir())


# -- coverage intervals ----------------------------------------------------------------------------


def check_coverage_closed_immutable(ctx):
    s = ctx.built()
    row = s.conn.execute("SELECT * FROM coverage_interval").fetchone()
    assert row["state"] == "closed" and row["verified"] == 1
    assert row["interval_id"] == eid_of("system-coverage-interval")
    assert row["closed_by_producer"] == "runner-watchdog"
    msg = sql_error(s.conn, "UPDATE coverage_interval SET t_end = t_start WHERE interval_id = ?", (row["interval_id"],))
    assert msg.startswith("COVERAGE_CLOSED_IMMUTABLE")
    open_id = str(uuid.uuid5(uuid.UUID(CASE), "open interval"))
    s.conn.execute(
        "INSERT INTO coverage_interval (interval_id, case_id, target_ref, t_start, last_verified_at, poll_interval_s, state) "
        "VALUES (?, ?, ?, ?, ?, 60, 'open')",
        (open_id, CASE, row["target_ref"], row["t_end"], row["t_end"]),
    )
    s.conn.execute("UPDATE coverage_interval SET last_verified_at = last_verified_at WHERE interval_id = ?", (open_id,))


def test_coverage_closed_immutable(ctx):
    check_coverage_closed_immutable(ctx)


# -- the anchor is stored as vouched or not, never refused ----------------------------------------


def check_anchor_vouched(ctx):
    s = ctx.built()
    entity = named(corpus_events(), "adjudicate-promote")["payload"]["entity_id"]
    row = s.conn.execute("SELECT * FROM node WHERE node_id = ?", (entity,)).fetchone()
    assert row["kind"] == "entity" and row["anchor_selector_type"] == "platform_uid"
    assert row["anchor_vouched"] == 0, "the anchor claim is a handle, so the anchor is unproven"
    events = corpus_events()
    named(events, "extract-claim-handle")["payload"]["selector_type"] = "platform_uid"
    for citation in named(events, "assess-sentence")["payload"]["citations"]:
        citation["cited_as"] = "platform_uid"
    s2 = ctx.built("patched", events)
    assert s2.conn.execute("SELECT anchor_vouched FROM node WHERE node_id = ?", (entity,)).fetchone()[0] == 1


def break_anchor_always_vouched(ctx):
    real = Projector._promote

    def broken(self, env, p):
        real(self, env, p)
        self.c.execute("UPDATE node SET anchor_vouched = 1 WHERE kind = 'entity'")

    ctx.mp.setattr(Projector, "_promote", broken)


def test_anchor_vouched(ctx):
    check_anchor_vouched(ctx)


# -- a hint and a permutation are never one node ----------------------------------------------------


def check_selector_types_never_share_a_node(ctx):
    s = ctx.built()
    rows = s.conn.execute("SELECT node_id, selector_type FROM node WHERE kind = 'selector'").fetchall()
    ids = {r["node_id"] for r in rows}
    assert eid_of("extract-claim-hint") in ids and eid_of("extract-claim-generated") in ids
    types = {r["node_id"]: r["selector_type"] for r in rows}
    assert types[eid_of("extract-claim-hint")] == "email_hint_recovery_masked"
    assert types[eid_of("extract-claim-generated")] == "email_generated_permutation"
    assert len(rows) == 4


def break_node_lookup_ignores_type(ctx):
    def first_node(self, selector_type, value):
        row = self.c.execute("SELECT node_id FROM node WHERE kind = 'selector' ORDER BY rowid LIMIT 1").fetchone()
        return row["node_id"] if row else None

    ctx.mp.setattr(Projector, "_selector_node_for", first_node)


def test_selector_types_never_share_a_node(ctx):
    check_selector_types_never_share_a_node(ctx)


CONTROLS = [
    ("a claim loses its run", check_claims_resolve, break_claim_loses_its_run),
    ("the run does not copy the gate's relation", check_seed_run, break_relation_not_copied),
    ("a LINK makes a cluster", check_two_clusters_none_from_link, break_link_makes_a_cluster),
    ("skeleton DDL built without triggers", check_skeleton_append_only, _strip_triggers),
    ("payload DDL built without triggers", check_payload_update_refused, _strip_triggers),
    ("foreign_keys off", check_payload_delete_cascades, break_foreign_keys_off),
    ("pragma assertion removed", check_pragmas_asserted, break_pragma_assertion_removed),
    ("a planted module deletes from event_payload", check_no_payload_delete_in_app, break_a_module_that_deletes),
    ("uuid4 selector node ids", check_rebuild_identical, break_uuid4_node_ids),
    ("verify compares nothing", check_planted_difference_detected, break_verify_compares_nothing),
    ("verify compares working state", check_verify_ignores_working_state, break_verify_compares_working_state),
    ("put() conditions removed", check_blobs, break_put_conditions_removed),
    ("coverage DDL built without triggers", check_coverage_closed_immutable, _strip_triggers),
    ("anchor always vouched", check_anchor_vouched, break_anchor_always_vouched),
    ("node lookup ignores the selector type", check_selector_types_never_share_a_node, break_node_lookup_ignores_type),
]
