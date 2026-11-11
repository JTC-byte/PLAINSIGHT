"""verify_shred: RT-9's five checks, run outside the tool that performed the shred, drafted refusing.

DRAFT, UNRATIFIED, AND IT REPORTS NO PASS. doctrine/RETENTION.md RT-9 makes
verification a separate program from runner/retention_sweep.py and names five
checks, each with the condition under which it passes and the ways it may not
pass for a reason other than the one claimed. This module runs the five checks
against a store and a case, prints each as a dated fact with its outcome and
why, and then refuses to report a pass while conformance/retention/shred-roundtrip.yaml
carries no dated row in the pin of record (VERIFY_SHRED_UNRATIFIED): the facts
are shown, the exit code is the refusal. Step 11 of docs/THE-GAMEPLAN.md, in
the shape Step 10 took; the 10-28 record's item 7 says the draft may land only
refusing.

OUTCOMES. PASS: the check observed the condition RT-9 names. FAIL: the check
ran and did not observe it. NOT RUN: the check could not be decided, because a
record it compares against was never taken or the policy leaves its definition
unratified; the fact's why names which. Only PASS counts toward a verified
shred. In this draft checks 1, 2 and 4 have no passing path, so no run reports
five passes, whatever the stamp says.

THE FIVE CHECKS, as this store can run them (reading RS-R6):

  1  key_destruction. A decrypt attempt on the case's witness ciphertext must
     fail on the key. What designates a witness is undecided
     (conformance/retention/shred-roundtrip.yaml SR-U1) and this store
     configures no Encryptor on LOCAL, so the check looks at no path and reads
     not_found, which RT-9 names a verification failure and never a pass. RT-9
     holds the witness outside the enumerable delete path, so a file named
     witness inside the case's blob directory is an object check 2 counts and
     nothing this check reads.
  2  object_absence. The case's blob directory is listed directly on disk,
     never through a cache and never from a DELETE's exit code. Objects that
     remain fail the check. No object on disk is NOT RUN, because the store
     records no count of the objects a case held before a shred (the per-case
     inventory is conformance/retention/shred-roundtrip.yaml SR-U1, undecided),
     so absence cannot be told from a case that never held one.
  3  schema_absence. The case database file is read by its path. The check
     fails, before it opens anything, when a file SQLite keeps beside the
     database is on disk (-journal, -wal or -shm): a rollback journal or a
     write-ahead log can hold pages of the case, and a read-only open of a
     database with a -wal beside it was seen to leave a -shm on disk (SQLite
     3.50.4, 2026-11-09). With none of the three on disk, the check passes
     when the database file is not on disk either, or when it is on disk, a
     query against every table the SQLite DDL of record declares for a case
     database errors with no such table, and the file's schema lists no object.
     It fails on zero rows, because "the table is gone" and "the table returned
     nothing" look identical in a result set. It fails on any other error,
     because a database that could not be read is not a database that is gone.
     It fails when the schema still lists a table, view, index or trigger once
     every declared table has errored, counted from sqlite_master without
     SQLite's own sqlite_ names: a table the DDL does not declare is not
     queried by name, and a view under a declared name that selects from a
     missing table raises the same error as a table that is gone. The check
     reads four names by stat (the database's own and the three sidecar
     names), the row count of each declared table and the schema's list of
     objects, and nothing else. It does not read the free pages of a database
     whose tables were dropped, where text of the case was seen to remain, and
     it does not look for a sidecar again after it has read the database.
  4  skeleton_presence. The case's skeleton rows exist in the plane database,
     the registry carries the tombstone state, and a SHRED_RECEIPT row carrying
     a receipt_hash follows the case's last stratum-1 event. Any of the three
     missing fails the check, since a shred with no receipt row did not happen
     (RT-10). All three present is NOT RUN, because policy/retention.yaml states
     no preimage for the receipt hash (U-09), so the check can confirm that a
     string is present and nothing more. The registry has no receipt-hash
     column; the hash is read from the receipt row.
  5  anti_overreach. An adjacent canary case still opens read-only, every table
     of its case database can be read, and its payload-row, claim and object
     counts equal the inventory the caller recorded before the shred. With no
     canary and inventory named the check is NOT RUN (U-11 is open). The check
     cannot tell an inventory taken before the shred from one taken after it.

verify() refuses a case this store has no registry row for
(VERIFY_SHRED_CASE_NEVER_HELD) and a canary that is the case under verification
(VERIFY_SHRED_CANARY_IS_THE_CASE), each before any check runs. A case id is
read under any spelling of its letters, because the case database's file name
is built from it in lower case, and the registry's spelling of the id is used
for every check.

Run as python -m runner.verify_shred --store ROOT --case CASE [--canary CASE
--canary-payloads N --canary-claims N --canary-blobs N]. Exit 0 only when the
fixture is stamped and all five checks pass, which no run of this draft
reaches; 1 otherwise; 2 when the command line could not be read.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sqlite3
import sys
import urllib.parse
from pathlib import Path

from app.refusals import Refusal
from app.store import db, ingest, retention
from app.store.db import Store
from runner.retention_sweep import FIXTURE_REL, read_stamps

CHECKS = (
    (1, "key_destruction", "the decrypt of the witness ciphertext fails on the key"),
    (2, "object_absence", "no object for the case remains, read directly on disk"),
    (3, "schema_absence", "a query against every table of the case database errors because the table is gone"),
    (4, "skeleton_presence", "stratum 2 is intact and carries the tombstone and the receipt hash"),
    (5, "anti_overreach", "the adjacent canary case is fully readable with its counts unchanged"),
)

#: The counts check 5 compares, in the order its facts name them.
INVENTORY_KEYS = ("payloads", "claims", "blobs")

#: A registry state that is no tombstone, as a clause for check 4's fact.
NO_TOMBSTONE = {
    "open": "the registry says the case is open",
    "shred_failed": "the registry says the shred failed, which halts new runs until a verification passes (RT-11)",
}

NOT_A_PASS = "not run is not a pass"

#: The suffixes of the files SQLite keeps beside a database: the rollback journal, the write-ahead log and its index.
SIDECAR_SUFFIXES = ("-journal", "-wal", "-shm")


def _fact(check_id: int, outcome: str, why: str, now: dt.datetime) -> dict:
    name, passes_when = next((n, p) for i, n, p in CHECKS if i == check_id)
    return {"id": check_id, "name": name, "passes_when": passes_when, "outcome": outcome, "why": why,
            "checked_at": retention.format_ts(now.replace(microsecond=0))}


def _on_disk(path: Path) -> bool:
    """Whether a path is on disk, read by stat. Only not-found reads as absent; any other error is raised."""
    try:
        path.stat()
    except FileNotFoundError:
        return False
    return True


def _sidecars(path: Path) -> list[str]:
    """The suffixes of the files SQLite keeps beside a database that are on disk beside this one, read by stat."""
    return [suffix for suffix in SIDECAR_SUFFIXES if _on_disk(path.with_name(path.name + suffix))]


def _objects(store, case_id: str) -> int:
    """The case's objects counted on disk; 0 when its blob directory is not there."""
    folder = store.root / db.BLOBS_DIR / case_id
    if not _on_disk(folder):
        return 0
    return sum(1 for p in folder.rglob("*") if not p.is_dir())


def case_tables() -> tuple[str, ...]:
    """The tables a case database declares, read from the SQLite DDL of record."""
    return tuple(db.statement_table(s) for s in db.ddl("case") if re.match(r"CREATE\s+TABLE\b", s, re.IGNORECASE))


def _open_readonly(path: Path) -> sqlite3.Connection:
    """A case database opened read-only by its path, percent-quoted so that no character in it ends the URI early."""
    return sqlite3.connect("file:" + urllib.parse.quote(path.as_posix(), safe="/:") + "?mode=ro", uri=True)


def _table_gone(exc: sqlite3.Error) -> bool:
    """True only for the error a query raises when its table does not exist."""
    return isinstance(exc, sqlite3.OperationalError) and "no such table" in str(exc)


def _rows(conn: sqlite3.Connection, table: str) -> int | None:
    """A table's row count, or None when the query errors because the table is gone. Any other error is raised."""
    try:
        return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    except sqlite3.Error as exc:
        if _table_gone(exc):
            return None
        raise


def _listed(conn: sqlite3.Connection) -> int:
    """The objects a case database's schema still lists, SQLite's own sqlite_ names left out. Check 3 calls it
    after every declared table has errored as gone, so whatever it counts is something those queries did not see."""
    return conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE name NOT LIKE 'sqlite~_%' ESCAPE '~'").fetchone()[0]


def check_key_destruction(store, case_id: str, now: dt.datetime) -> dict:
    """Check 1. No witness is designated and no decrypt can be attempted: not_found, a failure by RT-9. Looks at no path."""
    return _fact(1, "FAIL", "not_found: no witness ciphertext is designated for this case, because what designates one is undecided "
                 "(conformance/retention/shred-roundtrip.yaml SR-U1), so this draft has nothing to attempt a decrypt on; "
                 "RT-9 names not-found a failure, never a pass", now)


def check_object_absence(store, case_id: str, now: dt.datetime) -> dict:
    """Check 2. The blob directory listed on disk. Objects that remain fail; none is NOT RUN, with no count to compare."""
    try:
        remaining = _objects(store, case_id)
    except OSError as exc:
        return _fact(2, "FAIL", f"the case's blob directory could not be listed ({type(exc).__name__}); a directory that cannot be listed is not an empty one", now)
    if remaining:
        return _fact(2, "FAIL", f"{remaining} object(s) remain on disk for the case", now)
    return _fact(2, "NOT RUN", "no object is on disk for the case, and this store records no count of the objects a case held before a shred "
                 "(the per-case inventory is conformance/retention/shred-roundtrip.yaml SR-U1, undecided), so their absence cannot be told "
                 f"from a case that never held one; {NOT_A_PASS}", now)


def check_schema_absence(store, case_id: str, now: dt.datetime) -> dict:
    """Check 3. Fails before any open when a file SQLite keeps beside the case database is on disk. With none on
    disk it passes when the file is gone, or when every declared table errors as gone and the schema lists no
    object; zero rows, an object the schema still lists and an unreadable file fail."""
    path = store.case_file(case_id)
    try:
        left = _sidecars(path)
        if left:
            return _fact(3, "FAIL", f"{len(left)} file(s) SQLite keeps beside the case database are on disk ({', '.join(left)}); "
                         "a rollback journal or a write-ahead log can hold pages of the case, which is not absence, "
                         "and the database was not opened", now)
        if not _on_disk(path):
            return _fact(3, "PASS", "the case database file and the files SQLite keeps beside it are not on disk, "
                         "so no table of the case remains to query", now)
        conn = _open_readonly(path)
        try:
            for table in case_tables():
                n = _rows(conn, table)
                if n is None:
                    continue
                if n == 0:
                    return _fact(3, "FAIL", f"the table {table} returned zero rows; it exists, which is not absence", now)
                return _fact(3, "FAIL", f"the table {table} holds {n} row(s)", now)
            listed = _listed(conn)
            if listed:
                return _fact(3, "FAIL", "every table the DDL declares errored with no such table, and the case database's schema "
                             f"still lists {listed} object(s); what the schema still lists is not absent", now)
        finally:
            conn.close()
    except (sqlite3.Error, OSError) as exc:
        return _fact(3, "FAIL", f"the case database could not be read ({type(exc).__name__}); a database that cannot be read is not a database that is gone", now)
    return _fact(3, "PASS", "the case database file is on disk with none of the files SQLite keeps beside it, every table the DDL "
                 "declares for it errored with no such table, and its schema lists no object", now)


def _receipt_hash(raw) -> str | None:
    """The receipt_hash a SHRED_RECEIPT payload carries, or None when it carries none that is a non-empty string."""
    try:
        value = json.loads(raw).get("receipt_hash")
    except (ValueError, TypeError, AttributeError):
        return None
    return value if isinstance(value, str) and value.strip() else None


def _follows(seq: int, last: int | None) -> bool:
    """Whether a receipt at `seq` follows the case's last stratum-1 event, which is at `last` or was never written."""
    return last is None or seq > last


def receipts_after_last_payload(store, case_id: str) -> int:
    """How many SHRED_RECEIPT rows carrying a receipt_hash follow the case's last stratum-1 event."""
    last = store.conn.execute(
        "SELECT MAX(case_seq) FROM event_skeleton WHERE case_id = ? AND payload_stratum = 1", (case_id,)).fetchone()[0]
    rows = store.conn.execute(
        "SELECT case_seq, payload_inline FROM event_skeleton WHERE case_id = ? AND event_type = 'SYSTEM_EVENT' "
        "AND event_subtype = 'SHRED_RECEIPT'", (case_id,)).fetchall()
    return sum(1 for seq, raw in rows if _follows(seq, last) and _receipt_hash(raw))


def _tombstoned(reg) -> bool:
    """Whether a registry row carries the tombstone state."""
    return reg["state"] == "shredded"


def check_skeleton_presence(store, case_id: str, now: dt.datetime) -> dict:
    """Check 4. Skeleton rows, the tombstone, and a receipt after the last stratum-1 event; no pass while U-09 is open."""
    rows = store.conn.execute("SELECT COUNT(*) FROM event_skeleton WHERE case_id = ?", (case_id,)).fetchone()[0]
    reg = store.registry(case_id)
    if reg is None or rows == 0:
        return _fact(4, "FAIL", "no skeleton rows or no registry row survive for the case: stratum 2 is not intact", now)
    if not _tombstoned(reg):
        said = NO_TOMBSTONE.get(reg["state"], "the registry carries a state that is not the tombstone")
        return _fact(4, "FAIL", f"{rows} skeleton row(s) are present and {said}, so stratum 2 carries no tombstone for this case "
                     "and nothing here records that a shred happened", now)
    if receipts_after_last_payload(store, case_id) == 0:
        return _fact(4, "FAIL", f"{rows} skeleton row(s) and the tombstone are present, and no SHRED_RECEIPT row carrying a receipt_hash "
                     "follows the case's last stratum-1 event: a shred with no receipt row did not happen (RT-10)", now)
    return _fact(4, "NOT RUN", f"{rows} skeleton row(s), the tombstone and a SHRED_RECEIPT row carrying a receipt_hash are present, and "
                 "policy/retention.yaml states no preimage for the receipt hash (U-09), so this check can confirm that a string is "
                 f"present and nothing more; {NOT_A_PASS}", now)


def canary_inventory(store, case_id: str) -> dict:
    """The counts check 5 compares: payload rows and claims in the case database, objects on disk.

    The case database is opened read-only by its path and every table it declares is read, so a table
    that is gone raises sqlite3.Error here rather than leaving a count out."""
    path = store.case_file(case_id)
    if store.registry(case_id) is None or not path.is_file():
        raise Refusal("CASE_NOT_HELD", f"canary {case_id[:8]}")
    conn = _open_readonly(path)
    try:
        counts = {table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in case_tables()}
    finally:
        conn.close()
    return {"payloads": counts["event_payload"], "claims": counts["claim"], "blobs": _objects(store, case_id)}


def check_anti_overreach(store, canary: str | None, inventory: dict | None, now: dt.datetime) -> dict:
    """Check 5. The canary reads in full and its three counts equal the inventory; no canary means not run."""
    if canary is None or inventory is None or any(key not in inventory for key in INVENTORY_KEYS):
        return _fact(5, "NOT RUN", "no adjacent canary case with its three counts taken before the shred (payload rows, claims, objects) was "
                     f"named, and what check 5 does when no adjacent case exists is undecided (policy/retention.yaml U-11); {NOT_A_PASS}", now)
    try:
        current = canary_inventory(store, canary)
    except Refusal as refusal:
        return _fact(5, "FAIL", f"the canary case could not be opened: {refusal.code}", now)
    except (sqlite3.Error, OSError) as exc:
        return _fact(5, "FAIL", f"the canary case is not fully readable ({type(exc).__name__})", now)
    if any(current[key] != inventory[key] for key in INVENTORY_KEYS):
        moved = ", ".join(f"{key} {inventory[key]} to {current[key]}" for key in INVENTORY_KEYS)
        return _fact(5, "FAIL", f"the canary's counts changed: {moved}", now)
    return _fact(5, "PASS", f"the canary is readable and unchanged: {current['payloads']} payload row(s), {current['claims']} claim(s), "
                 f"{current['blobs']} object(s)", now)


def held_spelling(store, case_id: str) -> str | None:
    """The case id as the registry holds it: the id itself when a row carries it exactly, else the one row whose
    id names the same case database under another spelling, else None. The case database's file name is built
    from the id in lower case, so an id written in upper case names the case it spells."""
    if store.registry(case_id) is not None:
        return case_id
    rows = ingest.rows_for_file(store.conn, case_id)
    return rows[0]["case_id"] if len(rows) == 1 else None


def refuse_unless_held(store, case_id: str) -> str:
    """The registry's spelling of a case this store holds. Refuses a case it has no registry row for, whose absent
    objects and tables would read as passes, and an id two rows name under other spellings.

    store.case_file runs first and refuses a string that is not a case id, so no part of a typed value is echoed."""
    store.case_file(case_id)
    held = held_spelling(store, case_id)
    if held is None:
        named = len(ingest.rows_for_file(store.conn, case_id))
        detail = f"case {case_id[:8]}" if not named else (
            f"case {case_id[:8]}: {named} registry rows name this case database under other spellings; name one exactly")
        raise Refusal("VERIFY_SHRED_CASE_NEVER_HELD", detail)
    return held


def refuse_own_canary(store, case_id: str, canary: str | None) -> None:
    """Refuses a canary that is the case under verification: a case cannot witness that its own shred spared it."""
    if canary is None:
        return
    store.case_file(canary)
    if canary.lower() == case_id.lower():
        raise Refusal("VERIFY_SHRED_CANARY_IS_THE_CASE", f"case {case_id[:8]}")


def exit_code(result: dict) -> int:
    """0 only when the fixture is stamped and all five checks passed; 1 otherwise."""
    return 0 if result["stamped"] and result["all_passed"] else 1


def verify(store, case_id: str, canary: str | None = None, inventory: dict | None = None,
           now: dt.datetime | None = None, stamps=None) -> dict:
    """The five checks as dated facts, then the stamp read. Refuses a case never held here and a canary that is the case.

    Returns {"case_id", "checks", "all_passed", "stamped", "verdict"}."""
    case_id = refuse_unless_held(store, case_id)
    refuse_own_canary(store, case_id, canary)
    if canary is not None:
        canary = held_spelling(store, canary) or canary
    now = now or dt.datetime.now(dt.timezone.utc)
    stamps = stamps or read_stamps()
    checks = [
        check_key_destruction(store, case_id, now),
        check_object_absence(store, case_id, now),
        check_schema_absence(store, case_id, now),
        check_skeleton_presence(store, case_id, now),
        check_anti_overreach(store, canary, inventory, now),
    ]
    all_passed = all(c["outcome"] == "PASS" for c in checks)
    stamped = stamps.fixture_stamped()
    if not stamped:
        verdict = Refusal("VERIFY_SHRED_UNRATIFIED", stamps.reason(FIXTURE_REL)).render()
    elif not all_passed:
        verdict = "NOT VERIFIED: " + "; ".join(f"check {c['id']} {c['name']} {c['outcome']}" for c in checks if c["outcome"] != "PASS")
    else:
        verdict = f"VERIFIED: 5 of 5 checks passed at {retention.format_ts(now.replace(microsecond=0))}, run outside the shredding tool"
    return {"case_id": case_id, "checks": checks, "all_passed": all_passed, "stamped": stamped, "verdict": verdict}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m runner.verify_shred", description="RT-9's five checks, outside the shredding tool.")
    ap.add_argument("--store", help="store root; default $PLAINSIGHT_HOME, else %%LOCALAPPDATA%%\\plainsight")
    ap.add_argument("--case", required=True, help="the shredded case's id")
    ap.add_argument("--canary", help="an adjacent held case that must be unchanged; never the case under verification")
    ap.add_argument("--canary-payloads", type=int, help="the canary's payload-row count recorded before the shred")
    ap.add_argument("--canary-claims", type=int, help="the canary's claim count recorded before the shred")
    ap.add_argument("--canary-blobs", type=int, help="the canary's object count recorded before the shred")
    try:
        args = ap.parse_args(argv)
    except SystemExit as exit_:
        return 0 if exit_.code == 0 else 2
    counts = (args.canary_payloads, args.canary_claims, args.canary_blobs)
    inventory = dict(zip(INVENTORY_KEYS, counts)) if args.canary and all(n is not None for n in counts) else None
    try:
        with Store.open(args.store) as store:
            result = verify(store, args.case, args.canary, inventory)
    except Refusal as refusal:
        print(refusal.render(), file=sys.stderr)
        return 1
    for c in result["checks"]:
        print(f"check {c['id']} {c['name']}: {c['outcome']} · {c['why']} · checked {c['checked_at']}")
    print(result["verdict"])
    return exit_code(result)


if __name__ == "__main__":
    sys.exit(main())
