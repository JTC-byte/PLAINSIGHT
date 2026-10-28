"""The store root, the connections, and the dialect-specific statements.

LOCAL runs stdlib sqlite3 in rollback-journal mode, never WAL, so that one
commit is atomic across the plane database and the attached case database.
ISOLATED will run one Postgres in the VM; ddl_postgres.sql is its DDL of
record, and nothing here provisions or connects to a Postgres server.

Every connection runs PRAGMA foreign_keys=ON and journal_mode=DELETE, and
open() asserts both (STORE_PRAGMA_UNSET).

The store root is PLAINSIGHT_HOME, default %LOCALAPPDATA%\\plainsight. A root
inside a git working tree is refused with STORE_PATH_IN_REPOSITORY before
anything is created, because git is the one store the shred cannot reach
(doctrine/RETENTION.md RT-15).
"""

from __future__ import annotations

import os
import re
import sqlite3
from pathlib import Path

from app import config
from app.refusals import REFUSALS, Refusal
from app.store import rollup

HERE = Path(__file__).resolve().parent
DDL_SQLITE = HERE / "ddl_sqlite.sql"
DDL_POSTGRES = HERE / "ddl_postgres.sql"

PLANE_FILE = "plane.sqlite"
CASES_DIR = "cases"
BLOBS_DIR = "blobs"

#: The schema name the case database is attached under.
CASE_ALIAS = "casedb"

#: Of the twelve tables docs/PLAINSIGHT-design.md amendment 9.2 names, these
#: seven are projections, rebuilt by replay.
PROJECTION_TABLES_PLANE = ("run", "coverage_interval")
PROJECTION_TABLES_CASE = ("item", "claim", "node", "edge", "case_rollup")

UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$")


# ---------------------------------------------------------------------------
# the root
# ---------------------------------------------------------------------------


def default_root() -> Path:
    base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
    return Path(base) / "plainsight"


def in_git_working_tree(path: Path) -> bool:
    """True when `path`, or any ancestor of it, is this repository or holds a .git entry."""
    path = Path(path)
    repo = config.REPO_ROOT.resolve()
    if path == repo or repo in path.parents:
        return True
    for candidate in (path, *path.parents):
        if (candidate / ".git").exists():
            return True
    return False


#: The longest path a store root may have on Windows: 259 characters less the
#: suffix of a case database's journal, \cases\case_<uuid>.sqlite-journal.
WINDOWS_PATH_LIMIT = 259
CASE_JOURNAL_SUFFIX = len("\\cases\\case_") + 36 + len(".sqlite-journal")
IS_WINDOWS = os.name == "nt"


def root_too_long(root: Path) -> bool:
    return IS_WINDOWS and len(str(root)) + CASE_JOURNAL_SUFFIX > WINDOWS_PATH_LIMIT


def resolve_root(store=None) -> Path:
    """The store root, refused when inside a git working tree or too long to open. Creates nothing."""
    raw = store or os.environ.get(config.ENV_HOME) or default_root()
    root = Path(raw).expanduser().resolve()
    if in_git_working_tree(root):
        raise Refusal("STORE_PATH_IN_REPOSITORY", "root: refused before anything was created")
    if root_too_long(root):
        raise Refusal("STORE_PATH_TOO_LONG", f"root: {len(str(root))} characters; refused before anything was created")
    return root


def case_path(root: Path, case_id: str) -> Path:
    if not isinstance(case_id, str) or not UUID_RE.match(case_id):
        raise Refusal("CASE_ID_INVALID")
    return Path(root) / CASES_DIR / f"case_{case_id.lower()}.sqlite"


# ---------------------------------------------------------------------------
# DDL
# ---------------------------------------------------------------------------


def sections(text: str) -> dict[str, str]:
    out: dict[str, list[str]] = {}
    current = None
    for line in text.splitlines():
        marker = re.match(r"^--\s*@(\w+)\s*$", line)
        if marker:
            current = marker.group(1)
            out.setdefault(current, [])
            continue
        if current is not None:
            out[current].append(line)
    return {k: "\n".join(v) for k, v in out.items()}


def statements(text: str) -> list[str]:
    """SQLite statements, split where sqlite3 says a statement is complete."""
    out, buf = [], []
    for line in text.splitlines():
        if line.strip().startswith("--") or not line.strip():
            if not buf:
                continue
        buf.append(line)
        joined = "\n".join(buf)
        if sqlite3.complete_statement(joined):
            out.append(joined.strip())
            buf = []
    return out


def ddl(section: str) -> list[str]:
    """The SQLite DDL statements of one section, plane or case."""
    return statements(sections(DDL_SQLITE.read_text(encoding="utf-8"))[section])


_TARGET_RE = re.compile(
    r"^CREATE\s+(TABLE|INDEX|TRIGGER)\s+IF\s+NOT\s+EXISTS\s+(\w+)(?:.*?\bON\s+(\w+))?",
    re.IGNORECASE | re.DOTALL,
)


def statement_table(stmt: str) -> str | None:
    """The table a CREATE TABLE, INDEX or TRIGGER statement is about."""
    m = _TARGET_RE.match(stmt)
    if not m:
        return None
    kind, name, on = m.group(1).upper(), m.group(2), m.group(3)
    return name if kind == "TABLE" else on


def qualify(stmt: str, alias: str) -> str:
    """Put a CREATE statement into the attached schema `alias`."""
    return re.sub(
        r"^(CREATE\s+(?:TABLE|INDEX|TRIGGER)\s+IF\s+NOT\s+EXISTS\s+)(\w+)",
        lambda m: f"{m.group(1)}{alias}.{m.group(2)}",
        stmt,
        count=1,
        flags=re.IGNORECASE,
    )


# ---------------------------------------------------------------------------
# pragmas and the cross-database guard
# ---------------------------------------------------------------------------


def set_pragmas(conn: sqlite3.Connection, schema: str = "main") -> None:
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute(f"PRAGMA {schema}.journal_mode=DELETE")


def assert_pragmas(conn: sqlite3.Connection, schemas=("main",)) -> None:
    fk = conn.execute("PRAGMA foreign_keys").fetchone()[0]
    modes = [conn.execute(f"PRAGMA {s}.journal_mode").fetchone()[0].lower() for s in schemas]
    if fk != 1 or any(m != "delete" for m in modes):
        raise Refusal("STORE_PRAGMA_UNSET", "foreign_keys and journal_mode were checked at open")


#: The case_rollup vocabulary guard. SQLite allows a trigger to read another
#: database only when the trigger is TEMP, so it is created on each connection
#: that attaches a case, and dropped before the case is detached.
ROLLUP_GUARD = (
    f"""CREATE TEMP TRIGGER IF NOT EXISTS case_rollup_vocab_insert
BEFORE INSERT ON {CASE_ALIAS}.case_rollup
WHEN NOT EXISTS (SELECT 1 FROM main.rollup_vocab v WHERE v.dimension = NEW.dimension AND v.bucket = NEW.bucket)
BEGIN
    SELECT RAISE(ABORT, 'ROLLUP_BUCKET_REFUSED: the dimension and bucket are not in rollup_vocab');
END""",
    f"""CREATE TEMP TRIGGER IF NOT EXISTS case_rollup_vocab_update
BEFORE UPDATE ON {CASE_ALIAS}.case_rollup
WHEN NOT EXISTS (SELECT 1 FROM main.rollup_vocab v WHERE v.dimension = NEW.dimension AND v.bucket = NEW.bucket)
BEGIN
    SELECT RAISE(ABORT, 'ROLLUP_BUCKET_REFUSED: the dimension and bucket are not in rollup_vocab');
END""",
)


def install_rollup_guard(conn: sqlite3.Connection) -> None:
    for stmt in ROLLUP_GUARD:
        conn.execute(stmt)


def drop_rollup_guard(conn: sqlite3.Connection) -> None:
    conn.execute("DROP TRIGGER IF EXISTS temp.case_rollup_vocab_insert")
    conn.execute("DROP TRIGGER IF EXISTS temp.case_rollup_vocab_update")


def refusal_from(exc: Exception) -> Refusal | None:
    """The Refusal a trigger raised, when its message opens with a declared code."""
    code = str(exc).split(":", 1)[0].strip()
    return Refusal(code, "raised by a store trigger") if code in REFUSALS else None


# ---------------------------------------------------------------------------
# the store
# ---------------------------------------------------------------------------


def connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path), isolation_level=None)
    conn.row_factory = sqlite3.Row
    set_pragmas(conn)
    assert_pragmas(conn)
    return conn


#: The environments the SQLite engine serves. It is the workstation store, which
#: holds tracked, unmodified synthetic corpus files only (amendment 9.1); the
#: ISOLATED store is the operator's Postgres inside the provisioned VM (EG-2).
SQLITE_ENVIRONMENTS = ("LOCAL",)


def check_engine(environment: str) -> None:
    """STORE_ISOLATED_NOT_PROVISIONED before a SQLite store is opened or created in ISOLATED.

    One environment variable must not lift the LOCAL source rule on the
    workstation: on LOCAL the door admits only SYNTHETIC_SOURCES, and in ISOLATED
    it admits any file, so the SQLite engine refuses to run as ISOLATED at all.
    """
    if environment not in SQLITE_ENVIRONMENTS:
        raise Refusal("STORE_ISOLATED_NOT_PROVISIONED", f"environment: {environment}")


class Store:
    """One store root: the plane database and, while attached, one case database."""

    def __init__(self, root: Path, conn: sqlite3.Connection):
        self.root = root
        self.conn = conn
        self.environment = config.environment()
        self.case_id: str | None = None

    # -- lifecycle ---------------------------------------------------------

    @classmethod
    def init(cls, store=None) -> "Store":
        check_engine(config.environment())
        root = resolve_root(store)
        (root / CASES_DIR).mkdir(parents=True, exist_ok=True)
        (root / BLOBS_DIR).mkdir(parents=True, exist_ok=True)
        conn = connect(root / PLANE_FILE)
        for stmt in ddl("plane"):
            conn.execute(stmt)
        self = cls(root, conn)
        rollup.load_vocab(conn)
        return self

    @classmethod
    def open(cls, store=None) -> "Store":
        check_engine(config.environment())
        root = resolve_root(store)
        if not (root / PLANE_FILE).is_file():
            raise Refusal("STORE_NOT_INITIALIZED")
        return cls(root, connect(root / PLANE_FILE))

    def close(self) -> None:
        self.detach_case()
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    # -- cases -------------------------------------------------------------

    def case_file(self, case_id: str) -> Path:
        return case_path(self.root, case_id)

    def attach_case(self, case_id: str, create: bool = True) -> bool:
        """Attach the case database. With create=False an absent file is not created."""
        path = self.case_file(case_id)
        if self.case_id == case_id:
            return True
        self.detach_case()
        if not create and not path.is_file():
            return False
        self.conn.execute(f"ATTACH DATABASE ? AS {CASE_ALIAS}", (str(path),))
        set_pragmas(self.conn, CASE_ALIAS)
        if create:
            for stmt in ddl("case"):
                self.conn.execute(qualify(stmt, CASE_ALIAS))
        assert_pragmas(self.conn, ("main", CASE_ALIAS))
        install_rollup_guard(self.conn)
        self.case_id = case_id
        return True

    def detach_case(self) -> None:
        if self.case_id is None:
            return
        drop_rollup_guard(self.conn)
        self.conn.execute(f"DETACH DATABASE {CASE_ALIAS}")
        self.case_id = None

    def recreate_case_projections(self) -> None:
        """Drop and recreate tables 7 to 11 in the attached case database."""
        for table in PROJECTION_TABLES_CASE:
            self.conn.execute(f"DROP TABLE IF EXISTS {CASE_ALIAS}.{table}")
        for stmt in ddl("case"):
            if statement_table(stmt) in PROJECTION_TABLES_CASE:
                self.conn.execute(qualify(stmt, CASE_ALIAS))
        install_rollup_guard(self.conn)

    def registry(self, case_id: str):
        return self.conn.execute("SELECT * FROM case_registry WHERE case_id = ?", (case_id,)).fetchone()

    def cases(self) -> list[str]:
        return [r[0] for r in self.conn.execute("SELECT case_id FROM case_registry ORDER BY case_id")]
