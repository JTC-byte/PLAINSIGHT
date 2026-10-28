-- PLAINSIGHT store, SQLite dialect. One of the two DDL files of record; the
-- other is ddl_postgres.sql, and app/tests/test_store.py asserts that both
-- declare the same tables and columns.
--
-- Two databases. plane.sqlite holds stratum 2 and survives the shred.
-- cases/case_<id>.sqlite holds stratum 1 and the per-case projections, and is
-- removed whole by the shred (doctrine/RETENTION.md RT-3). app/store/db.py
-- attaches the case database to the plane connection, so one commit spans both,
-- which holds in rollback-journal mode only. The store never runs in WAL.
--
-- The case_rollup vocabulary guard references a table in the other database.
-- SQLite allows that only in a TEMP trigger, so app/store/db.py creates it on
-- every connection that attaches a case; ddl_postgres.sql declares it as an
-- ordinary trigger.
--
-- Sections are introduced by "-- @plane" and "-- @case" lines.

-- @plane

CREATE TABLE IF NOT EXISTS case_registry (
    case_id             TEXT PRIMARY KEY,
    opened_at           TEXT NOT NULL,
    anchor_ts           TEXT NOT NULL,
    anchor_reading      TEXT NOT NULL,
    environment         TEXT NOT NULL CHECK (environment IN ('LOCAL', 'ISOLATED')),
    synthetic           INTEGER NOT NULL CHECK (synthetic IN (0, 1)),
    source_path         TEXT,
    source_sha256       TEXT,
    case_ttl_days       INTEGER NOT NULL,
    extension_days      INTEGER NOT NULL,
    ceiling_days        INTEGER NOT NULL,
    incidental_ttl_days INTEGER NOT NULL,
    retain_until        TEXT NOT NULL,
    frozen_until        TEXT,
    state               TEXT NOT NULL CHECK (state IN ('open', 'shredded', 'shred_failed')),
    policy_sha256       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS event_skeleton (
    seq             INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id        TEXT NOT NULL UNIQUE,
    case_id         TEXT NOT NULL REFERENCES case_registry (case_id),
    case_seq        INTEGER NOT NULL,
    pse_version     TEXT NOT NULL,
    derived_from    TEXT NOT NULL,
    event_type      TEXT NOT NULL,
    event_subtype   TEXT NOT NULL,
    ts              TEXT NOT NULL,
    producer        TEXT NOT NULL,
    environment     TEXT NOT NULL,
    platform_id     TEXT NOT NULL,
    sw_version      TEXT,
    parents_json    TEXT,
    transform       TEXT,
    optional_keys   TEXT NOT NULL,
    payload_stratum INTEGER NOT NULL CHECK (payload_stratum IN (1, 2)),
    payload_inline  TEXT,
    envelope_sha256 TEXT NOT NULL,
    ingested_at     TEXT NOT NULL,
    batch_id        TEXT NOT NULL,
    UNIQUE (case_id, case_seq),
    CHECK ((payload_stratum = 2) = (payload_inline IS NOT NULL))
);

CREATE INDEX IF NOT EXISTS event_skeleton_case ON event_skeleton (case_id, case_seq);

CREATE TRIGGER IF NOT EXISTS event_skeleton_no_update
BEFORE UPDATE ON event_skeleton
BEGIN
    SELECT RAISE(ABORT, 'EVENT_LOG_APPEND_ONLY: event_skeleton is append-only; append a new event instead');
END;

CREATE TRIGGER IF NOT EXISTS event_skeleton_no_delete
BEFORE DELETE ON event_skeleton
BEGIN
    SELECT RAISE(ABORT, 'EVENT_LOG_APPEND_ONLY: event_skeleton is append-only; append a new event instead');
END;

CREATE TABLE IF NOT EXISTS run (
    run_id               TEXT PRIMARY KEY,
    case_id              TEXT NOT NULL,
    start_event_id       TEXT NOT NULL UNIQUE,
    end_event_id         TEXT,
    permitted_event_id   TEXT,
    connector_id         TEXT NOT NULL,
    connector_version    TEXT,
    connector_kind       TEXT,
    credential_id        TEXT,
    egress_environment   TEXT,
    egress_identity      TEXT,
    argv_template        TEXT,
    target_selector_type TEXT,
    motivated_by         TEXT,
    subject_relation     TEXT,
    pivot_depth          INTEGER,
    authorization_ref    TEXT,
    manifest_hash        TEXT,
    started_at           TEXT NOT NULL,
    ended_at             TEXT,
    exit_code            INTEGER,
    item_count           INTEGER
);

CREATE TABLE IF NOT EXISTS coverage_interval (
    interval_id        TEXT PRIMARY KEY,
    case_id            TEXT NOT NULL,
    target_ref         TEXT NOT NULL,
    t_start            TEXT NOT NULL,
    last_verified_at   TEXT,
    poll_interval_s    INTEGER,
    t_end              TEXT,
    state              TEXT NOT NULL CHECK (state IN ('open', 'closed')),
    closed_by_event_id TEXT,
    closed_by_producer TEXT,
    verified           INTEGER,
    method             TEXT
);

CREATE TRIGGER IF NOT EXISTS coverage_interval_closed_immutable
BEFORE UPDATE ON coverage_interval
WHEN OLD.state = 'closed'
BEGIN
    SELECT RAISE(ABORT, 'COVERAGE_CLOSED_IMMUTABLE: a closed coverage interval is never rewritten');
END;

CREATE TABLE IF NOT EXISTS rollup_vocab (
    dimension TEXT NOT NULL,
    bucket    TEXT NOT NULL,
    PRIMARY KEY (dimension, bucket)
);

-- @case

CREATE TABLE IF NOT EXISTS event_payload (
    event_id        TEXT PRIMARY KEY,
    payload_stratum INTEGER NOT NULL CHECK (payload_stratum = 1),
    payload_json    TEXT NOT NULL
);

CREATE TRIGGER IF NOT EXISTS event_payload_no_update
BEFORE UPDATE ON event_payload
BEGIN
    SELECT RAISE(ABORT, 'PAYLOAD_UPDATE_REFUSED: a stratum-1 payload is inserted once and never updated');
END;

CREATE TABLE IF NOT EXISTS item (
    item_id          TEXT PRIMARY KEY,
    event_id         TEXT NOT NULL UNIQUE REFERENCES event_payload (event_id) ON DELETE CASCADE,
    run_id           TEXT NOT NULL,
    locator          TEXT,
    outcome          TEXT,
    blob_sha256      TEXT,
    blob_state       TEXT NOT NULL CHECK (blob_state IN ('absent', 'held')),
    raw_span_json    TEXT,
    subject_relation TEXT,
    expires_at       TEXT
);

CREATE TABLE IF NOT EXISTS claim (
    claim_id         TEXT PRIMARY KEY REFERENCES event_payload (event_id) ON DELETE CASCADE,
    item_id          TEXT NOT NULL,
    run_id           TEXT NOT NULL,
    permit_event_id  TEXT,
    subject_relation TEXT,
    pivot_depth      INTEGER,
    selector_type    TEXT NOT NULL,
    value            TEXT NOT NULL,
    subject_ref      TEXT,
    source_path      TEXT,
    extractor        TEXT,
    observed_at      TEXT NOT NULL,
    asserted_at      TEXT,
    time_provenance  TEXT NOT NULL,
    negative_state   TEXT NOT NULL,
    provenance_state TEXT NOT NULL,
    datum_class      TEXT NOT NULL,
    injection_tagged INTEGER,
    expires_at       TEXT
);

CREATE INDEX IF NOT EXISTS claim_selector ON claim (selector_type, value);

CREATE TABLE IF NOT EXISTS node (
    node_id              TEXT PRIMARY KEY,
    kind                 TEXT NOT NULL CHECK (kind IN ('entity', 'referenced', 'selector', 'cluster', 'candidate')),
    entity_type          TEXT,
    selector_type        TEXT,
    anchor_selector_type TEXT,
    anchor_claim_id      TEXT,
    anchor_vouched       INTEGER,
    sector               TEXT,
    created_by_event_id  TEXT NOT NULL,
    revoked_by_event_id  TEXT,
    expires_at           TEXT
);

CREATE TABLE IF NOT EXISTS edge (
    edge_id  TEXT PRIMARY KEY,
    kind     TEXT NOT NULL CHECK (kind IN ('observed_about', 'proposes', 'member_of', 'excludes')),
    src_id   TEXT NOT NULL,
    dst_id   TEXT NOT NULL,
    layer    TEXT NOT NULL CHECK (layer IN ('observation', 'inference', 'fusion')),
    label    TEXT NOT NULL,
    actor    TEXT NOT NULL,
    ts       TEXT NOT NULL,
    event_id TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS edge_src ON edge (src_id);
CREATE INDEX IF NOT EXISTS edge_dst ON edge (dst_id);

CREATE TABLE IF NOT EXISTS case_rollup (
    dimension TEXT NOT NULL,
    bucket    TEXT NOT NULL,
    n         INTEGER NOT NULL,
    PRIMARY KEY (dimension, bucket)
);

CREATE TABLE IF NOT EXISTS workspace_kv (
    analyst    TEXT NOT NULL,
    view       TEXT NOT NULL,
    key        TEXT NOT NULL CHECK (key IN ('scroll', 'sort', 'columns', 'collapsed', 'focus', 'hops', 'drawer')),
    value_json TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (analyst, view, key)
);
