"""The store root, the DDL of record in both dialects, and the refusal table."""

from __future__ import annotations

import os
import re
import shutil
import subprocess

import pytest
import yaml

from app import config, refusals
from app.refusals import Code, Refusal
from app.store import db
from app.tests.helpers import refusal_of


# -- the store root ----------------------------------------------------------------


def check_root_in_repository_refused(ctx):
    inside = config.REPO_ROOT / "a-store-that-must-not-exist"
    assert refusal_of(db.resolve_root, inside).code == "STORE_PATH_IN_REPOSITORY"
    assert refusal_of(db.resolve_root, config.REPO_ROOT).code == "STORE_PATH_IN_REPOSITORY"
    other_tree = ctx.tmp / "other-tree"
    (other_tree / ".git").mkdir(parents=True)
    assert refusal_of(db.resolve_root, other_tree / "store").code == "STORE_PATH_IN_REPOSITORY"
    ctx.mp.setenv(config.ENV_HOME, str(inside))
    assert refusal_of(db.Store.init).code == "STORE_PATH_IN_REPOSITORY"
    assert not inside.exists(), "nothing was created under the repository"


def break_tree_detector_removed(ctx):
    # Removing the mechanism must not create a store under the repository, so the
    # check above only resolves roots and the one init it attempts is refused
    # by resolve_root before any directory exists. With the detector removed,
    # resolve_root returns instead of refusing and the check fails there.
    ctx.mp.setattr(db, "in_git_working_tree", lambda path: False)
    ctx.mp.setattr(db.Store, "init", classmethod(lambda cls, store=None: db.resolve_root(store)))


def test_root_in_repository_refused(ctx):
    check_root_in_repository_refused(ctx)


def test_root_defaults(ctx):
    assert db.resolve_root() == (ctx.tmp / "home").resolve()
    ctx.mp.delenv(config.ENV_HOME)
    ctx.mp.setenv("LOCALAPPDATA", str(ctx.tmp / "appdata"))
    assert db.resolve_root() == (ctx.tmp / "appdata" / "plainsight").resolve()
    assert not (ctx.tmp / "appdata").exists(), "resolving a root creates nothing"


def check_long_root_refused(ctx):
    long_root = ctx.tmp / ("d" * (db.WINDOWS_PATH_LIMIT - len(str(ctx.tmp))))
    ctx.mp.setattr(db, "IS_WINDOWS", True)
    assert refusal_of(db.resolve_root, long_root).code == "STORE_PATH_TOO_LONG"
    assert not long_root.exists()
    assert db.resolve_root(ctx.tmp / "short") == (ctx.tmp / "short").resolve()


def break_length_check_removed(ctx):
    ctx.mp.setattr(db, "root_too_long", lambda root: False)


def test_long_root_refused(ctx):
    check_long_root_refused(ctx)


def test_open_needs_init(ctx):
    assert refusal_of(db.Store.open, ctx.tmp / "empty").code == "STORE_NOT_INITIALIZED"


def test_case_id_must_be_a_uuid(ctx):
    assert refusal_of(db.case_path, ctx.tmp, "..\\..\\escape").code == "CASE_ID_INVALID"


# -- DDL parity -----------------------------------------------------------------------


def read_ddl(path) -> str:
    return path.read_text(encoding="utf-8")


_TABLE_RE = re.compile(r"CREATE TABLE IF NOT EXISTS\s+(?:\w+\.)?(\w+)\s*\((.*?)\n\);", re.DOTALL)
_CONSTRAINT_WORDS = ("UNIQUE", "CHECK", "PRIMARY", "FOREIGN", "CONSTRAINT")


def ddl_tables(text: str) -> dict[str, list[str]]:
    out = {}
    for name, body in _TABLE_RE.findall(text):
        cols = []
        for line in body.splitlines():
            word = line.strip().split(" ", 1)[0].rstrip(",")
            if word and word.upper() not in _CONSTRAINT_WORDS:
                cols.append(word)
        out[name] = cols
    return out


def check_ddl_parity(ctx):
    lite = ddl_tables(read_ddl(db.DDL_SQLITE))
    pg = ddl_tables(read_ddl(db.DDL_POSTGRES))
    assert len(lite) == 12, "the brief's twelve tables"
    assert set(lite) == set(pg)
    for table in lite:
        assert lite[table] == pg[table], f"{table} differs between the dialects"


def break_postgres_drops_a_column(ctx):
    real = read_ddl

    def dropped(path):
        text = real(path)
        if path == db.DDL_POSTGRES:
            text = text.replace("    credential_id        TEXT,\n", "", 1)
        return text

    ctx.mp.setitem(globals(), "read_ddl", dropped)


def test_ddl_parity(ctx):
    check_ddl_parity(ctx)


def test_ddl_sqlite_sections_apply(ctx):
    s = ctx.store()
    tables = {r[0] for r in s.conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert {"case_registry", "event_skeleton", "run", "coverage_interval", "rollup_vocab"} <= tables


@pytest.mark.skipif(os.environ.get("PLAINSIGHT_PG_DOCKER") != "1", reason="the Postgres apply runs only on the operator's word (PLAINSIGHT_PG_DOCKER=1)")
def test_postgres_ddl_applies_in_docker():  # pragma: no cover - operator-gated
    container = os.environ.get("PLAINSIGHT_PG_CONTAINER", "plainsight-pg")
    if shutil.which("docker") is None:
        pytest.skip("docker is not on PATH")
    text = read_ddl(db.DDL_POSTGRES)
    sections = db.sections(text)
    sql = sections["plane"] + "\n" + sections["case"].replace("case_template", "case_00000000_0000_4000_8000_000000000000")
    proc = subprocess.run(
        ["docker", "exec", "-i", container, "psql", "-v", "ON_ERROR_STOP=1", "-U", "postgres"],
        input=sql.encode("utf-8"),
        capture_output=True,
    )
    assert proc.returncode == 0


# -- the refusal table ----------------------------------------------------------------------


def check_refusals_well_formed(ctx):
    assert refusals.well_formed(refusals.REFUSALS) == []
    for code in refusals.REFUSALS:
        text = Refusal(code).render()
        assert text.startswith(f"Refused {code}: ") and "Legal moves: " in text


def break_a_code_with_one_move(ctx):
    ctx.mp.setitem(refusals.REFUSALS, "BROKEN_CODE", Code("BROKEN_CODE", "something", "a rule", ("one move",)))


def test_refusals_well_formed(ctx):
    check_refusals_well_formed(ctx)


def check_app_codes_are_not_wire_codes(ctx):
    vc = yaml.safe_load((config.REPO_ROOT / "policy" / "violation-codes.yaml").read_text(encoding="utf-8"))
    declared = {c["code"] for c in vc["violation_codes"]["codes"]}
    assert declared, "the wire vocabulary was read"
    assert not set(refusals.REFUSALS) & declared, "an app code is in policy/violation-codes.yaml"


def break_app_declares_a_wire_code(ctx):
    ctx.mp.setitem(refusals.REFUSALS, "SCHEMA_INVALID", Code("SCHEMA_INVALID", "what", "rule", ("one", "two")))


def test_app_codes_are_not_wire_codes(ctx):
    check_app_codes_are_not_wire_codes(ctx)


CONTROLS = [
    ("working-tree detector removed", check_root_in_repository_refused, break_tree_detector_removed),
    ("path-length check removed", check_long_root_refused, break_length_check_removed),
    ("a dropped Postgres column", check_ddl_parity, break_postgres_drops_a_column),
    ("a code with one move", check_refusals_well_formed, break_a_code_with_one_move),
    ("an app code that is a wire code", check_app_codes_are_not_wire_codes, break_app_declares_a_wire_code),
]
