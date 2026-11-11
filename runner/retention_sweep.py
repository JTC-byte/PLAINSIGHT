"""The retention sweep: the scheduled job that acts on retain_until, drafted refusing.

DRAFT, UNRATIFIED, AND IT DELETES NOTHING. Step 11 of docs/THE-GAMEPLAN.md, in
the shape Step 10 took for the subject gate: every value is read from
policy/retention.yaml, the stamp state is read from the pin of record through
tools/pin_of_record.py, and every act that would remove material refuses while
the pin carries no row, each refusal rendered as its consequence with the legal
moves. The Class F edges, retain_until itself and the shred, stay the
operator's; this file may land only refusing (the 10-28 record, item 7).

WHAT RUNS NOW. doctrine/RETENTION.md RT-12: the sweep is scheduled from day one,
while it still has nothing to delete, and writes a heartbeat on every run,
including runs that delete nothing; a missing heartbeat renders in the case
header as its consequence. A run has two halves, in this order.

First it reads every registry row and decides, writing nothing. A case that is
not open, or whose case database is absent, is not held: it is listed and gets
no heartbeat. The door refuses a write into such a case
(CASE_CLOSED_TO_WRITES), and the sweep does not attempt one, so the run reports
the case as not held and not as a refused heartbeat (reading RS-R1). A held
case whose retain_until or frozen_until cannot be read as a date is refused as
SWEEP_REFUSED_DATE_UNREADABLE, neither swept nor passed over as current. A
frozen case is skipped and said so (RT-17). Every other held case whose
retain_until instant is at or before now is due, and the sweep states the
sequence of RETENTION.md section 9 (the RT-13 finding check, the shred,
verify_shred, the receipt) and refuses at its first step:

  1. the RT-13 finding check, which tools/validate_retention.py --finding
     refuses as RETENTION_FINDING_NO_CASE_STORE and the kernel gate lists as
     PENDING (SWEEP_REFUSED_FINDING_CHECK_PENDING);
  2. the shred, refused on LOCAL because its two mechanisms, DROP SCHEMA and
     the destruction of a per-case key, are the ISOLATED store's
     (SWEEP_REFUSED_LOCAL_STORE, EG-2), refused while policy/retention.yaml
     carries no dated row (SWEEP_REFUSED_POLICY_UNRATIFIED), and refused after
     both because this draft holds no shred (SWEEP_REFUSED_SHRED_NOT_BUILT).

Steps 3 and 4, verify_shred and the receipt, are never reached: no shred runs,
so there is nothing to verify and nothing to receipt.

Then, with every case decided, it appends one SYSTEM_EVENT SWEEP_HEARTBEAT per
held case through the same door every corpus row passes (app/store/ingest.py,
origin "system", producer runner-sweep), with swept_count 0 and next_due from
the policy's daily cadence. The heartbeat is written last so that it attests a
run that finished deciding, never one that stopped part way (reading RS-R7).

WHAT IS WRITTEN. The heartbeat is the only write, and the door makes it as two
things: one appended event, and the door's projector raising that case's
case_rollup counters for the event, which updates a projection row in place.
No claim, item, payload or registry row changes, and nothing is deleted. A
refusal to act is neither a shred nor a failed shred, so the sweep writes no
SHRED_RECEIPT and no SHRED_FAILED (RT-10, RT-11), and case_registry.state stays
open.

READINGS, recorded on the pattern of runner/subject_guard.py so the maintainer
can confirm or reverse each:

  RS-R1  Where the heartbeat lives. One SWEEP_HEARTBEAT per held case, through
         the door, because the corpus places the event in a case and no
         plane-level event store exists. A case is held when its registry
         state is open and its case database is present. The heartbeat goes
         nowhere else: the door refuses a write into a case that is not held
         (amendment 9.21), because an event landed there would put material
         back and an attach would recreate the file the shred removed, and
         the sweep reads the same rule and does not attempt the write. A
         store with no held case gets no heartbeat and has no header to
         render one on. A
         plane-level heartbeat row would be a schema change. A registry row
         that says open with no case database is a case the sweep answers for
         and cannot act on, so that run exits 1. A row that says shredded or
         shred_failed is verify_shred's to judge, whatever is on disk, and
         does not change the exit code. Reconciling a ledger against storage
         in both directions is RT-10's job, runner/reconcile_ledger.py, which
         is not built.
  RS-R2  What a due case reads while nothing may be deleted: "DUE, NOT SWEPT",
         then the first refusal in the section 9 order, never a bare state word.
         A run that states a due case and refuses it exits 0, because the run
         finished deciding and the refusal is on its report. RT-12 and RT-13
         name no exit code, so that exit code is this draft's reading.
  RS-R3  The cadence. next_due is now plus one day, read from the policy's
         cadence step whose `when` is daily; the heartbeat's due time has no
         grace (policy/retention.yaml heartbeats.grace_period: none, and its
         reading RET-R7), so the header turns red at next_due.
  RS-R4  The sweep writes no SHRED_FAILED on a refusal: SHRED_FAILED is evidence
         that a shred ran and did not verify, and halts dispatch system-wide;
         a sweep that refused to start one has nothing to report under RT-11.
  RS-R5  The LOCAL store. On LOCAL the heartbeat lands only in a synthetic case
         (the door's origin rule, ACT_LOCAL_SYNTHETIC_CASE_ONLY), and the shred
         refuses before the policy question is reached.
  RS-R7  The order. Every case is decided before anything is written, and the
         heartbeat is written last. A heartbeat written first would say the
         sweep ran on a run that then stopped on a date it could not read.
  RS-R8  The clock. The command line takes no instant. The log is append-only
         and the header reads it, so a heartbeat dated other than when it was
         written is a false row that cannot be taken back. sweep() takes an
         instant for the test suite alone.

(RS-R6 is in runner/verify_shred.py.)

Run as python -m runner.retention_sweep --store ROOT [--once] [--every S].
Exit 0 when the run finished deciding and every heartbeat it attempted was
written, whether or not a case was due, frozen, shredded or marked
shred_failed; a store with no held case writes no heartbeat and says so. Exit
1 when the door refused a heartbeat, when a held case carries a date the sweep
could not read, when the registry says open for a case whose database is
absent, or when the store could not be opened. Exit 2 when the command line
could not be read.
"""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import sys
import time
import uuid
from pathlib import Path

import yaml

from app import __version__
from app.refusals import REFUSALS, Refusal
from app.store import door, ingest, retention
from app.store.db import Store

ROOT = Path(__file__).resolve().parents[1]
POLICY_REL = "policy/retention.yaml"
FIXTURE_REL = "conformance/retention/shred-roundtrip.yaml"
PIN_READER = ROOT / "tools" / "pin_of_record.py"

#: The producer the heartbeat is written under (the corpus's system-sweep-heartbeat row).
PRODUCER = "runner-sweep"

#: The policy's cadence step this job is.
CADENCE_WHEN = "daily"

#: The kernel gate entry that holds RT-13's finding check (tools/validate_conformance.py).
FINDING_ENTRY = "retention-finding"


def _load_by_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Stamps:
    """The pin of record as tools/pin_of_record.py reads it: is the policy or the fixture stamped."""

    def __init__(self, text: str | None = None):
        self.reader = _load_by_path("plainsight_pin_of_record_sweep", PIN_READER)
        self.text = self.reader.PIN.read_text(encoding="utf-8") if text is None else text
        self.pin = self.reader.Pin(self.text, ROOT)

    def policy_stamped(self) -> bool:
        return bool(self.pin.parsed) and self.pin.artifact_stamped(POLICY_REL)

    def fixture_stamped(self) -> bool:
        return bool(self.pin.parsed) and self.pin.artifact_stamped(FIXTURE_REL)

    def reason(self, rel: str) -> str:
        return self.pin.reason_unstamped(rel)


def read_stamps() -> Stamps:
    """The live pin. The test suite replaces this function; a caller never does."""
    return Stamps()


def cadence_days(policy_path: Path | None = None) -> int:
    """The sweep's interval in days. The policy's cadence must carry the step whose `when` is daily; that
    step names no number, so the one day is written here."""
    path = policy_path or retention.POLICY
    try:
        policy = yaml.safe_load(path.read_text(encoding="utf-8"))["retention"]
        steps = policy["cadence"]["steps"]
    except (OSError, UnicodeDecodeError, yaml.YAMLError, KeyError, TypeError):
        raise Refusal("RETENTION_POLICY_UNREADABLE", "field: cadence.steps") from None
    for step in steps:
        if isinstance(step, dict) and step.get("when") == CADENCE_WHEN:
            return 1
    raise Refusal("RETENTION_POLICY_UNREADABLE", "field: cadence.steps has no daily step")


def heartbeat_event(store, case_id: str, now: dt.datetime, swept: int, next_due: dt.datetime) -> dict:
    props = door.load_policy().schema["properties"]
    return {
        "pse_version": props["pse_version"]["const"],
        "derived_from": props["derived_from"]["const"],
        "case_id": case_id,
        "event": {
            "event_id": str(uuid.uuid4()),
            "event_type": "SYSTEM_EVENT",
            "event_subtype": "SWEEP_HEARTBEAT",
            "ts": retention.format_ts(now.replace(microsecond=0)),
        },
        "source": {
            "platform_id": ingest.STORE_PLATFORM_ID,
            "environment": store.environment,
            "producer": PRODUCER,
            "sw_version": __version__,
        },
        "payload": {
            "system_type": "SWEEP_HEARTBEAT",
            "swept_count": swept,
            "next_due": retention.format_ts(next_due.replace(microsecond=0)),
        },
    }


def write_heartbeat(store, case_id: str, now: dt.datetime, next_due: dt.datetime, humans=None) -> str:
    """One SWEEP_HEARTBEAT through the door. Returns the event id, or raises the door's refusal."""
    env = heartbeat_event(store, case_id, now, 0, next_due)
    ingest.ingest_batch(store, [env], humans, origin="system")
    return env["event"]["event_id"]


#: What the registry says of a case the sweep does not write into, as a clause for its report line.
NOT_HELD_STATE = {
    "open": "the registry says open",
    "shredded": "the registry says shredded",
    "shred_failed": "the registry says the shred failed, which halts new runs until verify_shred passes (RT-11)",
}


def is_held(state: str, present: bool) -> bool:
    """A case is held when the registry says open and its case database is present: the door's own rule, read
    through the door's function so that the two cannot drift apart."""
    return ingest.case_held(state, present)


def unaccounted(state: str, present: bool) -> bool:
    """An open registry row with no case database: a case the sweep answers for and cannot act on."""
    return state == "open" and not present


def not_held_text(state: str, present: bool) -> str:
    """A case that is not held, rendered as what the sweep did about it."""
    where = "is still present" if present else "is absent"
    text = (f"NOT HELD · {NOT_HELD_STATE[state]} and the case database {where} · no heartbeat written: "
            "the sweep writes only into an open case whose database is present, and never recreates one")
    if unaccounted(state, present):
        text += " · retain_until cannot be enforced on a case with no database, so this run exits 1"
    return text


def past_retain_until(retain: dt.datetime, now: dt.datetime) -> bool:
    """Whether a case is past retain_until at `now`: from the instant itself, as app/store/retention.py
    is_past reads it."""
    return retain <= now


def registry_instant(day) -> dt.datetime | None:
    """A registry date as an instant, or None when it cannot be read as a date."""
    try:
        return retention.parse_ts(retention.date_instant(day))
    except (ValueError, TypeError, AttributeError):
        return None


def survey(store, now: dt.datetime) -> dict:
    """Every registry row decided, with nothing written.

    Returns {"held": [case ids], "not_held": [...], "unreadable": [...], "frozen": [...], "due": [...]}.
    A case is held when its state is open and its case database is present. A held case with a date
    that cannot be read is listed as unreadable and is in neither of the last two lists."""
    out = {"held": [], "not_held": [], "unreadable": [], "frozen": [], "due": []}
    for r in store.conn.execute("SELECT * FROM case_registry ORDER BY case_id").fetchall():
        case_id = r["case_id"]
        present = store.case_file(case_id).is_file()
        if not is_held(r["state"], present):
            out["not_held"].append({"case_id": case_id, "state": r["state"], "present": present})
            continue
        out["held"].append(case_id)
        retain = registry_instant(r["retain_until"])
        freeze = None if r["frozen_until"] is None else registry_instant(r["frozen_until"])
        if retain is None or (r["frozen_until"] is not None and freeze is None):
            out["unreadable"].append({"case_id": case_id, "field": "retain_until" if retain is None else "frozen_until"})
            continue
        if not past_retain_until(retain, now):
            continue
        row = {"case_id": case_id, "retain_until": r["retain_until"], "frozen_until": r["frozen_until"]}
        (out["frozen"] if freeze is not None and freeze > now else out["due"]).append(row)
    return out


def finding_check_refusal(case_id: str) -> Refusal:
    """Step 1 of section 9: RT-13's finding check, which the gate lists as PENDING."""
    return Refusal("SWEEP_REFUSED_FINDING_CHECK_PENDING", f"case {case_id[:8]}")


def shred_refusal(store, stamps: Stamps, case_id: str) -> Refusal:
    """Step 2 of section 9: the shred, refused on LOCAL, then while the policy is unstamped, then
    because this draft holds none. Steps 3 and 4 are not reached."""
    if store.environment == "LOCAL":
        return Refusal("SWEEP_REFUSED_LOCAL_STORE", f"case {case_id[:8]}")
    if not stamps.policy_stamped():
        return Refusal("SWEEP_REFUSED_POLICY_UNRATIFIED", f"case {case_id[:8]}: {stamps.reason(POLICY_REL)}")
    return Refusal("SWEEP_REFUSED_SHRED_NOT_BUILT", f"case {case_id[:8]}")


def first_refusal(store, stamps: Stamps, case_id: str) -> Refusal:
    """The first step of RETENTION.md section 9's order that refuses, in that order."""
    return finding_check_refusal(case_id) or shred_refusal(store, stamps, case_id)


def refused_heartbeat(case_id: str, refusal: Refusal) -> dict:
    """A heartbeat the door refused, as its consequence with the refusal's own text and legal moves."""
    return {"case_id": case_id, "refusal": refusal.code, "render": refusal.render(),
            "text": "HEARTBEAT REFUSED · the door refused this run's heartbeat, so this case's record does not "
                    "show the run · this run exits 1"}


def sweep(store, now: dt.datetime | None = None, humans=None, stamps: Stamps | None = None) -> dict:
    """One run: every case decided with nothing written, then the heartbeat in every held case.

    Returns {"now", "next_due", "not_held": [...], "unreadable": [...], "skipped_frozen": [...], "due": [...],
    "heartbeats": [event ids], "refused_heartbeats": [...]}. The heartbeat is the only write: one appended
    event, and the door's projector raising that case's case_rollup counters. Nothing is deleted. `now` is
    for the test suite; the command line takes no instant (reading RS-R8)."""
    now = now or dt.datetime.now(dt.timezone.utc)
    stamps = stamps or read_stamps()
    next_due = now + dt.timedelta(days=cadence_days())
    found = survey(store, now)
    report = {"now": retention.format_ts(now.replace(microsecond=0)), "next_due": retention.format_ts(next_due.replace(microsecond=0)),
              "not_held": [], "unreadable": [], "skipped_frozen": [], "due": [], "heartbeats": [], "refused_heartbeats": []}
    for row in found["not_held"]:
        report["not_held"].append(dict(row, text=not_held_text(row["state"], row["present"])))
    for row in found["unreadable"]:
        refusal = Refusal("SWEEP_REFUSED_DATE_UNREADABLE", f"case {row['case_id'][:8]}: {row['field']}")
        report["unreadable"].append({
            "case_id": row["case_id"],
            "field": row["field"],
            "refusal": refusal.code,
            "text": f"DATE UNREADABLE, NOT SWEPT · {row['field']} is not a date the sweep can read",
        })
    for row in found["frozen"]:
        report["skipped_frozen"].append({"case_id": row["case_id"], "text": (
            f"FROZEN until {row['frozen_until']} · shred suspended (RT-17) · the sweep skips this case")})
    for row in found["due"]:
        refusal = first_refusal(store, stamps, row["case_id"])
        report["due"].append({
            "case_id": row["case_id"],
            "retain_until": row["retain_until"],
            "refusal": refusal.code,
            "text": f"DUE, NOT SWEPT · past retain_until {row['retain_until']} · {REFUSALS[refusal.code].what}",
        })
    for case_id in found["held"]:
        try:
            report["heartbeats"].append(write_heartbeat(store, case_id, now, next_due, humans))
        except Refusal as refusal:
            report["refused_heartbeats"].append(refused_heartbeat(case_id, refusal))
    return report


def print_report(report: dict) -> None:
    """One run as lines: the heartbeat, each case the run had something to say about, each refusal once."""
    if report["heartbeats"]:
        print(f"heartbeat written in {len(report['heartbeats'])} case(s) at {report['now']}, next due {report['next_due']}; this draft of the sweep deletes nothing")
    elif report["refused_heartbeats"]:
        print(f"no heartbeat written at {report['now']}: the door refused it in {len(report['refused_heartbeats'])} case(s); this draft of the sweep deletes nothing")
    else:
        print(f"no heartbeat written at {report['now']}: this store holds no open case whose database is present")
    for row in report["refused_heartbeats"]:
        print(f"{row['case_id'][:8]}: {row['text']}", file=sys.stderr)
        print(row["render"], file=sys.stderr)
    for key in ("not_held", "unreadable", "skipped_frozen", "due"):
        for row in report[key]:
            print(f"{row['case_id'][:8]}: {row['text']}")
    if not report["due"] and not report["skipped_frozen"] and not report["unreadable"]:
        print("nothing due: no held case is past retain_until")
    for code in sorted({row["refusal"] for row in report["due"] + report["unreadable"]}):
        print(Refusal(code).render())


def exit_code(report: dict) -> int:
    """1 when a heartbeat was refused, when a held case carries a date the sweep could not read, or when
    the registry says open for a case whose database is absent; else 0."""
    lost = [row for row in report["not_held"] if unaccounted(row["state"], row["present"])]
    return 1 if report["refused_heartbeats"] or report["unreadable"] or lost else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m runner.retention_sweep", description="The retention sweep, drafted refusing: a heartbeat in every held case on every run; this draft deletes nothing.")
    ap.add_argument("--store", help="store root; default $PLAINSIGHT_HOME, else %%LOCALAPPDATA%%\\plainsight")
    ap.add_argument("--once", action="store_true", help="one sweep, then exit")
    ap.add_argument("--every", type=int, default=86400, help="seconds between sweeps when not --once (default one day, the policy's cadence)")
    try:
        args = ap.parse_args(argv)
    except SystemExit as exit_:
        return 0 if exit_.code == 0 else 2
    try:
        with Store.open(args.store) as store:
            while True:
                report = sweep(store)
                print_report(report)
                if args.once:
                    return exit_code(report)
                time.sleep(max(1, args.every))
    except Refusal as refusal:
        print(refusal.render(), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
