"""Ingest: the door's checks, then one transaction, then the notice.

The CLI is python -m app ingest --store <root> <path>. The library call is
ingest_batch(store, rows, humans, source=...). There is no HTTP ingest route. A
connector reaches the store only through the runner calling ingest_batch in
ISOLATED, and it contributes no UI.

On LOCAL ingest_batch requires the SourceRecord that door.check_source made
for a tracked, unmodified SYNTHETIC_SOURCES file, and it trusts its caller to
pass that file's rows. The CLI does exactly that. Every EXTRACT value is
shape-checked regardless (SYNTHETIC_VALUE_SHAPE), a defence in depth for RT-15
behind the source rule docs/PLAINSIGHT-design.md amendment 9.12 states.

The write is one transaction across the plane and case databases: the
skeleton row, then the payload row when the stratum is 1, then the projection
rows, then the case_rollup increments. The notice is published after commit and
carries a sequence number, a kind, the case id and opaque ids, never a value.
"""

from __future__ import annotations

import datetime as dt
import uuid
from dataclasses import dataclass, field

from app import __version__, config
from app.refusals import Refusal
from app.store import db, door, envelope, replay, retention
from app.store.project import Projector

#: Callables receiving each notice after commit. The HTTP layer subscribes here.
LISTENERS: list = []

NOTICE_KINDS = ("claims", "nodes", "edges", "runs", "coverage", "case")
NOTICE_MAX_IDS = 50

#: The producer and platform the store writes its own SCHEMA_VIOLATION under.
VIOLATION_PRODUCER = "runner-ingest"
STORE_PLATFORM_ID = "plainsight-store"


@dataclass
class IngestResult:
    case_id: str | None
    landed: int
    held: int
    batch_id: str | None = None
    notices: list = field(default_factory=list)


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ingest_path(store, path, humans=None) -> IngestResult:
    """The CLI path: check the source, read its rows, ingest them."""
    source = door.check_source(path, store.environment)
    rows = door.read_rows(path)
    return ingest_batch(store, rows, humans, source=source)


def ingest_batch(store, rows, humans=None, *, source: door.SourceRecord | None = None) -> IngestResult:
    """Validate a batch with tools/validate.py and the store checks, then write it whole or not at all."""
    humans = set(config.deployment_humans() if humans is None else humans)
    if store.environment == "LOCAL" and (source is None or not source.checked or not source.synthetic):
        raise Refusal("STORE_LOCAL_SYNTHETIC_ONLY", "source: ingest_batch on LOCAL needs door.check_source's record")
    door.check_fresh()
    envs = door.normalize(rows)
    case_id = door.batch_case(envs)
    registered = store.registry(case_id) if case_id else None
    stored, stored_sha = replay.stored_envelopes(store, case_id) if registered else ({}, {})
    pol = door.load_policy()
    failures = door.validate(envs, stored, pol, humans)
    if failures:
        detail = door.render_failures(failures)
        if store.environment == "ISOLATED":
            detail += "\n" + _record_violations(store, case_id, failures, pol, humans)
        raise Refusal("VALIDATION_REFUSED", detail)
    synthetic = bool(registered["synthetic"]) if registered else bool(source and source.synthetic)
    plan, held, problems = door.store_checks(envs, stored, stored_sha, synthetic)
    if problems:
        raise Refusal(problems[0].split(" ", 1)[0], "\n".join(problems) + "\nnothing was written")
    if not plan:
        return IngestResult(case_id, 0, held)
    batch_id = str(uuid.uuid4())
    durations = None if registered else retention.load_durations()
    notices = _write(store, case_id, plan, batch_id, source, durations)
    return IngestResult(case_id, len(plan), held, batch_id, notices)


def overtaken(conn, case_id: str, plan, expect_registered: bool) -> bool:
    """True when another ingest wrote between this batch's checks and its write lock.

    The door's checks read the log without a lock. Under BEGIN IMMEDIATE the
    write re-reads the two facts it planned on: whether the case is registered,
    and whether any planned event id is already in the log.
    """
    registered = conn.execute("SELECT 1 FROM case_registry WHERE case_id = ?", (case_id,)).fetchone() is not None
    if registered != expect_registered:
        return True
    ids = [e["event"]["event_id"] for e in plan]
    for i in range(0, len(ids), 400):
        chunk = ids[i:i + 400]
        marks = ", ".join("?" for _ in chunk)
        if conn.execute(f"SELECT 1 FROM event_skeleton WHERE event_id IN ({marks}) LIMIT 1", chunk).fetchone():
            return True
    return False


def _write(store, case_id, plan, batch_id, source, durations) -> list:
    created = not store.case_file(case_id).exists()
    store.attach_case(case_id)
    conn = store.conn
    conn.execute("BEGIN IMMEDIATE")
    try:
        if overtaken(conn, case_id, plan, expect_registered=durations is None):
            raise Refusal("INGEST_CONCURRENT", "the log moved between the door's checks and the write")
        if durations is not None:
            anchor = min((e["event"]["ts"] for e in plan), key=retention.parse_ts)
            conn.execute(
                "INSERT INTO case_registry (case_id, opened_at, anchor_ts, anchor_reading, environment, synthetic, "
                "source_path, source_sha256, case_ttl_days, extension_days, ceiling_days, incidental_ttl_days, "
                "retain_until, frozen_until, state, policy_sha256) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, 'open', ?)",
                (
                    case_id, _now(), anchor, retention.ANCHOR_READING, store.environment,
                    int(bool(source and source.synthetic)), source.path if source else None,
                    source.sha256 if source else None, durations["case_ttl_days"], durations["extension_days"],
                    durations["ceiling_days"], durations["incidental_ttl_days"],
                    retention.initial_retain_until(anchor, durations["case_ttl_days"]), durations["policy_sha256"],
                ),
            )
        seq = conn.execute(
            "SELECT COALESCE(MAX(case_seq), 0) FROM event_skeleton WHERE case_id = ?", (case_id,)
        ).fetchone()[0]
        projector = Projector(conn, case_id, store.root / db.BLOBS_DIR)
        ingested_at = _now()
        for env in plan:
            seq += 1
            write_event(conn, env, seq, ingested_at, batch_id)
            projector.count_event(env)
            projector.apply(env)
        projector.finish()
        conn.execute("COMMIT")
    except Exception as exc:
        conn.execute("ROLLBACK")
        if created:
            _remove_created_case_file(store, case_id)
        if isinstance(exc, Refusal):
            raise
        refusal = db.refusal_from(exc)
        if refusal is not None:
            raise refusal from None
        raise
    notices = make_notices(case_id, seq, projector.touched)
    for listener in list(LISTENERS):
        for notice in notices:
            listener(notice)
    return notices


def _remove_created_case_file(store, case_id: str) -> None:
    """Remove the case file this write's attach created, so a rolled-back first
    batch leaves no case database without a registry row behind it."""
    store.detach_case()
    path = store.case_file(case_id)
    for p in (path, path.with_name(path.name + "-journal")):
        try:
            p.unlink()
        except FileNotFoundError:
            pass


def write_event(conn, env: dict, case_seq: int, ingested_at: str, batch_id: str) -> None:
    """The skeleton row, then the payload row when the stratum is 1."""
    cols = envelope.decompose(env)
    stratum = envelope.payload_stratum(cols["event_type"], cols["event_subtype"])
    payload_text = envelope.canonical(cols.pop("payload")).decode("utf-8")
    cols.update({
        "case_seq": case_seq,
        "payload_stratum": stratum,
        "payload_inline": payload_text if stratum == 2 else None,
        "ingested_at": ingested_at,
        "batch_id": batch_id,
    })
    names = ", ".join(cols)
    conn.execute(f"INSERT INTO event_skeleton ({names}) VALUES ({', '.join('?' for _ in cols)})", tuple(cols.values()))
    if stratum == 1:
        insert_payload(conn, cols["event_id"], payload_text)


def insert_payload(conn, event_id: str, payload_text: str) -> None:
    conn.execute(
        "INSERT INTO event_payload (event_id, payload_stratum, payload_json) VALUES (?, 1, ?)",
        (event_id, payload_text),
    )


def make_notices(case_id: str, seq: int, touched: dict) -> list[dict]:
    """One notice per touched kind: {seq, kind, case_id, ids}, at most 50 opaque ids each."""
    out = []
    for kind in NOTICE_KINDS:
        ids = [i for i in touched.get(kind, []) if isinstance(i, str) and db.UUID_RE.match(i)]
        if kind in touched:
            out.append({"seq": seq, "kind": kind, "case_id": case_id, "ids": ids[:NOTICE_MAX_IDS]})
    return out


# ---------------------------------------------------------------------------
# ISOLATED: a refused event leaves a SCHEMA_VIOLATION that carries no value
# ---------------------------------------------------------------------------


def build_schema_violation(case_id: str, original: dict, codes, pol) -> dict:
    """A SYSTEM_EVENT SCHEMA_VIOLATION naming the refused event and one code, and nothing else.

    The builder is handed the whole refused envelope, because that is what a
    real runner holds, and it copies the event id out of it and nothing more.
    app/tests/test_door.py asserts that no value reaches the result.
    """
    original_event_id = door._eid(original)
    props = pol.schema["properties"]
    allowed = pol.schema["$defs"]["payload_SYSTEM_EVENT_SCHEMA_VIOLATION"]["properties"]["reason_code"]["enum"]
    code = next((c for c in sorted(codes) if c in allowed), "SCHEMA_INVALID")
    return {
        "pse_version": props["pse_version"]["const"],
        "derived_from": props["derived_from"]["const"],
        "case_id": case_id,
        "event": {
            "event_id": str(uuid.uuid4()),
            "event_type": "SYSTEM_EVENT",
            "event_subtype": "SCHEMA_VIOLATION",
            "ts": _now(),
        },
        "source": {
            "platform_id": STORE_PLATFORM_ID,
            "environment": "ISOLATED",
            "producer": VIOLATION_PRODUCER,
            "sw_version": __version__,
        },
        "payload": {
            "system_type": "SCHEMA_VIOLATION",
            "reason_code": code,
            "original_event_id": original_event_id,
        },
    }


def _record_violations(store, case_id, failures, pol, humans) -> str:
    if not case_id or store.registry(case_id) is None:
        return "no SCHEMA_VIOLATION was appended: the case is not registered in this store"
    stored, _ = replay.stored_envelopes(store, case_id)
    built = []
    for _line, (e, codes) in sorted(failures.items()):
        eid = door._eid(e)
        if eid is None or not db.UUID_RE.match(eid):
            continue
        built.append(build_schema_violation(case_id, e, codes, pol))
    index_events = list(stored.values()) + built
    clean = [v for v in built if not door.check_event(v, pol, door.make_index(index_events), set(humans))]
    if not clean:
        return "no SCHEMA_VIOLATION was appended: none passed tools/validate.py"
    _write(store, case_id, clean, str(uuid.uuid4()), None, None)
    return f"{len(clean)} SCHEMA_VIOLATION event(s) appended, each naming an event id and a code"
