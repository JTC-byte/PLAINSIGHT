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

The door writes only into a held case. A case is held when the registry says
open and its case database is present. A batch for a case the registry holds
any other way is refused with CASE_CLOSED_TO_WRITES before the stored log is
read, whatever its origin: an event landed in a shredded case would put
material back, and an attach would recreate a case database that is gone. The
rule is read from every registry row that names the case's database file, and
that file's name ignores letter case, so another spelling of a closed case's id
is refused with it, and a batch under another spelling of an open case's id
would open a second registry row onto one case database, so such batches
are refused with CASE_ID_SPELLING_DIFFERS. _write holds the rule again before
its attach, attaches a registered case without create, and re-reads the
registry under its write lock. The HTTP routes that write (app/http/routes.py
case_store) and rebuild (app/store/replay.py) read the same rule
(docs/PLAINSIGHT-design.md amendment 9.21, reading APP-R34).

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


#: Where a batch comes from: a file through the CLI, an analyst act the server
#: mints (app/http/acts.py), or a system event the runner's watchdog mints
#: (runner/watchdog.py). The source rule governs a file; origin_allowed governs
#: the other two.
ORIGINS = ("file", "act", "system")


def local_acts_enabled() -> bool:
    """Whether the operator has set app.config.LOCAL_ACTS. A function, so a test can show the refusal is load-bearing."""
    return bool(config.LOCAL_ACTS)


def origin_allowed(store, case_id, origin: str) -> None:
    """A minted act or system event lands only in a case the store holds. On
    LOCAL an act lands only once the operator has set config.LOCAL_ACTS
    (ACT_LOCAL_PENDING_DECISION until then, reading APP-R31: an act's payload is
    stratum 1 and its prose is typed at run time, so admitting it is his
    decision under EG-2), and then, like a system event, only in a case the
    registry marks synthetic (ACT_LOCAL_SYNTHETIC_CASE_ONLY), so the LOCAL
    store holds nothing about a person. A file batch is governed by the source
    rule and passes here (docs/PLAINSIGHT-design.md amendment 9.16)."""
    if origin not in ORIGINS:
        raise Refusal("ROW_SHAPE_INVALID", f"origin: {origin}")
    if origin == "file":
        return
    registered = store.registry(case_id) if case_id else None
    if registered is None:
        raise Refusal("CASE_NOT_HELD", "a minted event cannot open a case")
    if store.environment == "LOCAL":
        if origin == "act" and not local_acts_enabled():
            raise Refusal("ACT_LOCAL_PENDING_DECISION")
        if not registered["synthetic"]:
            raise Refusal("ACT_LOCAL_SYNTHETIC_CASE_ONLY")


def case_held(state: str, present: bool) -> bool:
    """A case is held when the registry says open and its case database is present. The retention sweep reads
    the same rule through this function (runner/retention_sweep.py, reading RS-R1)."""
    return state == "open" and present


#: What the registry says of a case the door does not write into, as a clause for the refusal's detail.
REGISTRY_SAYS = {
    "open": "the registry says open",
    "shredded": "the registry says shredded",
    "shred_failed": "the registry says the shred failed, which halts new runs until verify_shred passes (RT-11)",
}

#: The clause for a registry state the schema's CHECK does not name.
STATE_NOT_NAMED = "the registry carries a state that is none of open, shredded and shred_failed"


def rows_for_file(conn, case_id: str) -> list:
    """Every registry row whose case id names this case's database file. db.case_path builds that name from the
    id in lower case, so a row under another spelling of the id names the same file."""
    return conn.execute(
        "SELECT case_id, state FROM case_registry WHERE lower(case_id) = ? ORDER BY case_id", (case_id.lower(),)
    ).fetchall()


def closed_to_writes(store, case_id: str) -> str | None:
    """Why the door does not write into this case, or None when it may: a registry row that names the case's
    database file and is not held. A case with no registry row is a first batch and is not closed. A string
    that is no case id names no file and is left to the validator, which refuses the batch."""
    if not isinstance(case_id, str) or not db.UUID_RE.match(case_id):
        return None
    present = store.case_file(case_id).is_file()
    for row in rows_for_file(store.conn, case_id):
        if not case_held(row["state"], present):
            said = REGISTRY_SAYS.get(row["state"], STATE_NOT_NAMED)
            where = "is still present" if present else "is absent"
            return f"case {row['case_id'][:8]}: {said}; the case database {where}"
    return None


def refuse_closed_case(store, case_id: str) -> None:
    """ingest_batch's own refusal of a case that is closed to writes, before the stored log is read. A batch
    that would change nothing is refused too, so a closed case is never reported as holding what was sent."""
    why = closed_to_writes(store, case_id)
    if why is not None:
        raise Refusal("CASE_CLOSED_TO_WRITES", why)


def closed_under_lock(conn, case_id: str) -> bool:
    """True when a registry row that names the case's database file is not open, read under the write lock.
    The door's checks read the registry without a lock, and this is the read the write stands on."""
    return any(not case_held(row["state"], True) for row in rows_for_file(conn, case_id))


def other_spelling(conn, case_id: str) -> str | None:
    """The registry's spelling of this case's id when registry rows name its case database and none carries the
    id exactly, else None. A batch under another spelling would open a second registry row, and with it a
    second retention clock, onto one case database."""
    if not isinstance(case_id, str) or not db.UUID_RE.match(case_id):
        return None
    rows = rows_for_file(conn, case_id)
    if rows and all(row["case_id"] != case_id for row in rows):
        return rows[0]["case_id"]
    return None


def spelling_registered_under_lock(conn, case_id: str) -> bool:
    """True when, read under the write lock, registry rows name this case's database and none carries the id
    exactly: another spelling was registered after the door's read, which happens only to a first batch."""
    return other_spelling(conn, case_id) is not None


def database_present(store, case_id: str) -> bool:
    """Whether the case database is on disk after the write's attach. The attach returns at once for a case already
    attached and reads no file, and on a system that lets an open file be deleted the database can be gone."""
    return store.case_file(case_id).is_file()


def keep_created_file(conn, case_id: str) -> bool:
    """Whether a case database this write created stays after its rollback: a registry row names it, so another
    ingest registered it, under this spelling or another, between this write's attach and its lock, and wrote into
    it. Removing it then would delete that case's database."""
    return bool(rows_for_file(conn, case_id))


def database_present_under_lock(store, case_id: str) -> bool:
    """Whether the case database is on disk, read after the write takes its lock: a file deleted between the attach
    and the lock, which a system that lets an open file be deleted allows, is read here."""
    return database_present(store, case_id)


def refuse_other_spelling(conn, case_id: str) -> None:
    """ingest_batch's refusal of a case id that names a case database the registry holds under another spelling."""
    held = other_spelling(conn, case_id)
    if held is not None:
        raise Refusal("CASE_ID_SPELLING_DIFFERS", f"case {case_id[:8]}: the registry holds this case database as {held[:8]}")


def ingest_batch(store, rows, humans=None, *, source: door.SourceRecord | None = None, origin: str = "file") -> IngestResult:
    """Validate a batch with tools/validate.py and the store checks, then write it whole or not at all."""
    humans = set(config.deployment_humans() if humans is None else humans)
    if origin == "file" and store.environment == "LOCAL" and (source is None or not source.checked or not source.synthetic):
        raise Refusal("STORE_LOCAL_SYNTHETIC_ONLY", "source: ingest_batch on LOCAL needs door.check_source's record")
    door.check_fresh()
    envs = door.normalize(rows)
    case_id = door.batch_case(envs)
    origin_allowed(store, case_id, origin)
    if case_id:
        refuse_closed_case(store, case_id)
        refuse_other_spelling(store.conn, case_id)
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
    # Before the attach, which creates an absent case database: a registered case's database is never recreated.
    # ingest_batch has refused already; the ISOLATED violation path reaches this function without it.
    why = closed_to_writes(store, case_id)
    if why is not None:
        raise Refusal("CASE_CLOSED_TO_WRITES", why + "; the write did not attach it")
    # Only a first batch creates a case database. A registered case is attached without create, so a case
    # database that is gone by the time of the attach is refused and never recreated.
    first = durations is not None
    created = first and not store.case_file(case_id).exists()
    if not store.attach_case(case_id, create=first) or not (first or database_present(store, case_id)):
        raise Refusal("CASE_CLOSED_TO_WRITES", f"case {case_id[:8]}: the case database is absent at the attach, and "
                      "the write creates one only for a case the registry does not hold yet")
    conn = store.conn
    conn.execute("BEGIN IMMEDIATE")
    try:
        if overtaken(conn, case_id, plan, expect_registered=durations is None):
            raise Refusal("INGEST_CONCURRENT", "the log moved between the door's checks and the write")
        if closed_under_lock(conn, case_id):
            raise Refusal("CASE_CLOSED_TO_WRITES", f"case {case_id[:8]}: the registry stopped saying open between "
                          "the door's checks and the write")
        if spelling_registered_under_lock(conn, case_id):
            raise Refusal("CASE_ID_SPELLING_DIFFERS", f"case {case_id[:8]}: another spelling of the id was registered "
                          "between the door's checks and the write")
        if not database_present_under_lock(store, case_id):
            raise Refusal("CASE_CLOSED_TO_WRITES", f"case {case_id[:8]}: the case database was gone when the write "
                          "took its lock")
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
        if created and not keep_created_file(conn, case_id):
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


def _unlink_left_if_open(path) -> bool:
    """Remove one file and say whether it is gone. A file another connection holds open, which Windows refuses to
    delete, is left, so the rollback's own error never takes the place of the error that rolled the write back."""
    try:
        path.unlink()
    except FileNotFoundError:
        return True
    except OSError:
        return False
    return True


def _remove_created_case_file(store, case_id: str) -> None:
    """Remove the case file this write's attach created, so a rolled-back first
    batch leaves no case database without a registry row behind it. A file that
    cannot be removed is left, and the write's own error is the one raised."""
    store.detach_case()
    path = store.case_file(case_id)
    for p in (path, path.with_name(path.name + "-journal")):
        _unlink_left_if_open(p)


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
