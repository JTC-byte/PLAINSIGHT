-- PLAINSIGHT store, Postgres dialect. One of the two DDL files of record; the
-- other is ddl_sqlite.sql, and app/tests/test_store.py asserts that both
-- declare the same tables and columns. Nothing provisions a Postgres server:
-- that is the operator's act, and this file has not been applied to one
-- unless PLAINSIGHT_PG_DOCKER=1 ran the gated test.
--
-- Each SQLite database maps one to one onto a schema. plane.sqlite is schema
-- plane, which survives the shred. cases/case_<id>.sqlite is schema
-- case_<id>, which doctrine/RETENTION.md RT-3 drops with DROP SCHEMA CASCADE.
-- The @case section is written against the placeholder schema case_template;
-- app/store/db.py substitutes the case's schema name before applying it.
--
-- Sections are introduced by "-- @plane" and "-- @case" lines.

-- @plane

CREATE SCHEMA IF NOT EXISTS plane;

CREATE TABLE IF NOT EXISTS plane.case_registry (
    case_id             TEXT PRIMARY KEY,
    opened_at           TIMESTAMPTZ NOT NULL,
    anchor_ts           TIMESTAMPTZ NOT NULL,
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

CREATE TABLE IF NOT EXISTS plane.event_skeleton (
    seq             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    event_id        TEXT NOT NULL UNIQUE,
    case_id         TEXT NOT NULL REFERENCES plane.case_registry (case_id),
    case_seq        INTEGER NOT NULL,
    pse_version     TEXT NOT NULL,
    derived_from    TEXT NOT NULL,
    event_type      TEXT NOT NULL,
    event_subtype   TEXT NOT NULL,
    ts              TIMESTAMPTZ NOT NULL,
    producer        TEXT NOT NULL,
    environment     TEXT NOT NULL,
    platform_id     TEXT NOT NULL,
    sw_version      TEXT,
    parents_json    JSONB,
    transform       TEXT,
    optional_keys   JSONB NOT NULL,
    payload_stratum INTEGER NOT NULL CHECK (payload_stratum IN (1, 2)),
    payload_inline  JSONB,
    envelope_sha256 TEXT NOT NULL,
    ingested_at     TIMESTAMPTZ NOT NULL,
    batch_id        TEXT NOT NULL,
    UNIQUE (case_id, case_seq),
    CHECK ((payload_stratum = 2) = (payload_inline IS NOT NULL))
);

CREATE OR REPLACE FUNCTION plane.refuse_log_change() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'EVENT_LOG_APPEND_ONLY: event_skeleton is append-only; append a new event instead';
END;
$$;

CREATE OR REPLACE TRIGGER event_skeleton_no_update
BEFORE UPDATE OR DELETE ON plane.event_skeleton
FOR EACH ROW EXECUTE FUNCTION plane.refuse_log_change();

REVOKE UPDATE, DELETE ON plane.event_skeleton FROM PUBLIC;

CREATE TABLE IF NOT EXISTS plane.run (
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
    started_at           TIMESTAMPTZ NOT NULL,
    ended_at             TIMESTAMPTZ,
    exit_code            INTEGER,
    item_count           INTEGER
);

CREATE TABLE IF NOT EXISTS plane.coverage_interval (
    interval_id        TEXT PRIMARY KEY,
    case_id            TEXT NOT NULL,
    target_ref         TEXT NOT NULL,
    t_start            TIMESTAMPTZ NOT NULL,
    last_verified_at   TIMESTAMPTZ,
    poll_interval_s    INTEGER,
    t_end              TIMESTAMPTZ,
    state              TEXT NOT NULL CHECK (state IN ('open', 'closed')),
    closed_by_event_id TEXT,
    closed_by_producer TEXT,
    verified           INTEGER,
    method             TEXT
);

CREATE OR REPLACE FUNCTION plane.refuse_closed_interval_update() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF OLD.state = 'closed' THEN
        RAISE EXCEPTION 'COVERAGE_CLOSED_IMMUTABLE: a closed coverage interval is never rewritten';
    END IF;
    RETURN NEW;
END;
$$;

CREATE OR REPLACE TRIGGER coverage_interval_closed_immutable
BEFORE UPDATE ON plane.coverage_interval
FOR EACH ROW EXECUTE FUNCTION plane.refuse_closed_interval_update();

CREATE TABLE IF NOT EXISTS plane.rollup_vocab (
    dimension TEXT NOT NULL,
    bucket    TEXT NOT NULL,
    PRIMARY KEY (dimension, bucket)
);

CREATE OR REPLACE FUNCTION plane.refuse_unlisted_bucket() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM plane.rollup_vocab v WHERE v.dimension = NEW.dimension AND v.bucket = NEW.bucket) THEN
        RAISE EXCEPTION 'ROLLUP_BUCKET_REFUSED: the dimension and bucket are not in rollup_vocab';
    END IF;
    RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION plane.refuse_payload_update() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'PAYLOAD_UPDATE_REFUSED: a stratum-1 payload is inserted once and never updated';
END;
$$;

-- @case

CREATE SCHEMA IF NOT EXISTS case_template;

CREATE TABLE IF NOT EXISTS case_template.event_payload (
    event_id        TEXT PRIMARY KEY,
    payload_stratum INTEGER NOT NULL CHECK (payload_stratum = 1),
    payload_json    JSONB NOT NULL
);

CREATE OR REPLACE TRIGGER event_payload_no_update
BEFORE UPDATE ON case_template.event_payload
FOR EACH ROW EXECUTE FUNCTION plane.refuse_payload_update();

CREATE TABLE IF NOT EXISTS case_template.item (
    item_id          TEXT PRIMARY KEY,
    event_id         TEXT NOT NULL UNIQUE REFERENCES case_template.event_payload (event_id) ON DELETE CASCADE,
    run_id           TEXT NOT NULL,
    locator          TEXT,
    outcome          TEXT,
    blob_sha256      TEXT,
    blob_state       TEXT NOT NULL CHECK (blob_state IN ('absent', 'held')),
    raw_span_json    JSONB,
    subject_relation TEXT,
    expires_at       TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS case_template.claim (
    claim_id         TEXT PRIMARY KEY REFERENCES case_template.event_payload (event_id) ON DELETE CASCADE,
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
    observed_at      TIMESTAMPTZ NOT NULL,
    asserted_at      TIMESTAMPTZ,
    time_provenance  TEXT NOT NULL,
    negative_state   TEXT NOT NULL,
    provenance_state TEXT NOT NULL,
    datum_class      TEXT NOT NULL,
    injection_tagged INTEGER,
    expires_at       TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS claim_selector ON case_template.claim (selector_type, value);

CREATE TABLE IF NOT EXISTS case_template.node (
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
    expires_at           TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS case_template.edge (
    edge_id  TEXT PRIMARY KEY,
    kind     TEXT NOT NULL CHECK (kind IN ('observed_about', 'proposes', 'member_of', 'excludes')),
    src_id   TEXT NOT NULL,
    dst_id   TEXT NOT NULL,
    layer    TEXT NOT NULL CHECK (layer IN ('observation', 'inference', 'fusion')),
    label    TEXT NOT NULL,
    actor    TEXT NOT NULL,
    ts       TIMESTAMPTZ NOT NULL,
    event_id TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS edge_src ON case_template.edge (src_id);
CREATE INDEX IF NOT EXISTS edge_dst ON case_template.edge (dst_id);

CREATE TABLE IF NOT EXISTS case_template.case_rollup (
    dimension TEXT NOT NULL,
    bucket    TEXT NOT NULL,
    n         INTEGER NOT NULL,
    PRIMARY KEY (dimension, bucket)
);

CREATE OR REPLACE TRIGGER case_rollup_vocab
BEFORE INSERT OR UPDATE ON case_template.case_rollup
FOR EACH ROW EXECUTE FUNCTION plane.refuse_unlisted_bucket();

CREATE TABLE IF NOT EXISTS case_template.workspace_kv (
    analyst    TEXT NOT NULL,
    view       TEXT NOT NULL,
    key        TEXT NOT NULL CHECK (key IN ('scroll', 'sort', 'columns', 'collapsed', 'focus', 'hops', 'drawer')),
    value_json JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (analyst, view, key)
);
