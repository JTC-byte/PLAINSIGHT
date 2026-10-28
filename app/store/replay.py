"""Rebuild and replay: the projections dropped and derived again from the log.

The artifact is event_skeleton plus event_payload. Tables 3, 4 and 7 to 11 are
projections, and rebuild() drops them for each case and replays the stored log
through the same handlers the ingest uses, in seq order. On an unswept store
the result is byte-identical to the first build, as measured by dump(): every
projection row of the case in canonical JSON, ordered by primary key.

Open coverage intervals are working state the watchdog keeps, not log, so a
rebuild keeps them and replays only the closed ones.

replay_into() copies the log of one store into another and rebuilds it there.
That is the migration path amendment 9.1 names for Postgres; verify() uses it to
compare a live store against a fresh replay and names every table that differs.
verify() compares what the log derives, so it leaves open coverage rows out of
both sides: a replay cannot reproduce working state, and a live watchdog
interval is not a difference.
"""

from __future__ import annotations

import hashlib
import json

from app.store import db, envelope, retention, rollup
from app.store.project import Projector

#: The projection tables of one case, each with the columns its rows sort on.
DUMP_TABLES = (
    ("run", ("run_id",), "case_id"),
    ("coverage_interval", ("interval_id",), "case_id"),
    ("item", ("item_id",), None),
    ("claim", ("claim_id",), None),
    ("node", ("node_id",), None),
    ("edge", ("edge_id",), None),
    ("case_rollup", ("dimension", "bucket"), None),
)


def skeleton_rows(store, case_id: str) -> list:
    return list(store.conn.execute(
        "SELECT * FROM event_skeleton WHERE case_id = ? ORDER BY seq", (case_id,)
    ))


def stored_envelopes(store, case_id: str) -> tuple[dict, dict]:
    """({event_id: envelope}, {event_id: envelope_sha256}) for the case's stored log.

    The case database is attached for reading without being created, so a case
    the store does not hold yet yields nothing. A stratum-1 event whose payload
    is gone (swept) has no envelope and is left out.
    """
    shas = {r["event_id"]: r["envelope_sha256"] for r in skeleton_rows(store, case_id)}
    if not shas:
        return {}, {}
    attached = store.attach_case(case_id, create=False)
    payloads = {}
    if attached:
        payloads = {r[0]: r[1] for r in store.conn.execute("SELECT event_id, payload_json FROM event_payload")}
    out = {}
    for row in skeleton_rows(store, case_id):
        if row["payload_stratum"] == 2:
            payload = json.loads(row["payload_inline"])
        elif row["event_id"] in payloads:
            payload = json.loads(payloads[row["event_id"]])
        else:
            continue
        out[row["event_id"]] = envelope.compose(row, payload)
    return out, shas


def replay_case(store, case_id: str) -> None:
    """Drop and replay the projections of one case, in one transaction."""
    store.attach_case(case_id)
    conn = store.conn
    conn.execute("BEGIN IMMEDIATE")
    try:
        conn.execute("DELETE FROM run WHERE case_id = ?", (case_id,))
        conn.execute("DELETE FROM coverage_interval WHERE case_id = ? AND state = 'closed'", (case_id,))
        store.recreate_case_projections()
        reg = store.registry(case_id)
        conn.execute(
            "UPDATE case_registry SET retain_until = ?, frozen_until = NULL WHERE case_id = ?",
            (retention.initial_retain_until(reg["anchor_ts"], reg["case_ttl_days"]), case_id),
        )
        payloads = {r[0]: r[1] for r in conn.execute("SELECT event_id, payload_json FROM event_payload")}
        projector = Projector(conn, case_id, store.root / db.BLOBS_DIR)
        for row in skeleton_rows(store, case_id):
            if row["payload_stratum"] == 2:
                payload = json.loads(row["payload_inline"])
            elif row["event_id"] in payloads:
                payload = json.loads(payloads[row["event_id"]])
            else:
                payload = None
            env = envelope.compose(row, payload if payload is not None else {})
            projector.count_event(env)
            if payload is not None:
                projector.apply(env)
        projector.finish()
        conn.execute("COMMIT")
    except Exception as exc:
        conn.execute("ROLLBACK")
        refusal = db.refusal_from(exc)
        if refusal is not None:
            raise refusal from None
        raise


def rebuild(store) -> list[str]:
    """Rebuild every case's projections from its log. Returns the case ids rebuilt.

    A case whose case database is absent is left alone: rebuilding it would
    create a per-case file the shred already removed.
    """
    rollup.load_vocab(store.conn)
    cases = [c for c in store.cases() if store.case_file(c).is_file()]
    for case_id in cases:
        replay_case(store, case_id)
    return cases


#: The rows verify() leaves out: working state no replay of the log can reproduce.
WORKING_STATE = {"coverage_interval": "state = 'open'"}


def dump(store, case_id: str, working: bool = True) -> bytes:
    """Every projection row of the case, canonical, ordered by primary key.

    With working=False the rows WORKING_STATE names are left out.
    """
    store.attach_case(case_id, create=False)
    lines = []
    reg = store.registry(case_id)
    lines.append(envelope.canonical({
        "table": "case_registry",
        "row": {"retain_until": reg["retain_until"], "frozen_until": reg["frozen_until"], "state": reg["state"]},
    }))
    for table, keys, scope in DUMP_TABLES:
        order = ", ".join(keys)
        skip = "" if working or table not in WORKING_STATE else f" AND NOT ({WORKING_STATE[table]})"
        if scope:
            rows = store.conn.execute(f"SELECT * FROM {table} WHERE {scope} = ?{skip} ORDER BY {order}", (case_id,))
        else:
            rows = store.conn.execute(f"SELECT * FROM {table} WHERE 1{skip} ORDER BY {order}")
        for row in rows:
            lines.append(envelope.canonical({"table": table, "row": dict(row)}))
    return b"\n".join(lines) + b"\n"


def digest(store, case_id: str) -> str:
    return hashlib.sha256(dump(store, case_id)).hexdigest()


def replay_into(src, dst) -> list[str]:
    """Copy the log of every case in `src` into `dst` and rebuild it there."""
    cases = src.cases()
    for case_id in cases:
        reg = dict(src.registry(case_id))
        skel = [dict(r) for r in skeleton_rows(src, case_id)]
        src.attach_case(case_id, create=False)
        payloads = [dict(r) for r in src.conn.execute("SELECT * FROM event_payload ORDER BY event_id")]
        dst.attach_case(case_id)
        conn = dst.conn
        conn.execute("BEGIN IMMEDIATE")
        try:
            cols = ", ".join(reg)
            conn.execute(f"INSERT INTO case_registry ({cols}) VALUES ({', '.join('?' for _ in reg)})", tuple(reg.values()))
            for row in skel:
                conn.execute(
                    f"INSERT INTO event_skeleton ({', '.join(row)}) VALUES ({', '.join('?' for _ in row)})",
                    tuple(row.values()),
                )
            for row in payloads:
                conn.execute(
                    "INSERT INTO event_payload (event_id, payload_stratum, payload_json) VALUES (?, ?, ?)",
                    (row["event_id"], row["payload_stratum"], row["payload_json"]),
                )
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise
    rebuild(dst)
    return cases


def verify(store, scratch_root) -> dict[str, list[str]]:
    """Replay `store` into a fresh store at `scratch_root` and name each differing table per case."""
    fresh = db.Store.init(scratch_root)
    try:
        replay_into(store, fresh)
        out = {}
        for case_id in store.cases():
            live = _by_table(dump(store, case_id, working=False))
            again = _by_table(dump(fresh, case_id, working=False))
            out[case_id] = sorted(t for t in set(live) | set(again) if live.get(t) != again.get(t))
        return out
    finally:
        fresh.close()


def _by_table(data: bytes) -> dict[str, list[bytes]]:
    out: dict[str, list[bytes]] = {}
    for line in data.splitlines():
        table = json.loads(line)["table"]
        out.setdefault(table, []).append(line)
    return out
