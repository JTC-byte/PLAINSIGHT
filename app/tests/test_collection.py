"""COLLECTION (key 5) and the RT-11 line, over loopback on the corpus store.

The board's rows are the manifests this checkout carries, each UNVERIFIED on
LOCAL, and the health records one case holds, each a dated record and never the
present state (the maintainer's rulings 1C, 2A and 3B of 2026-11-12, amendment
9.25). Each check claims coverage of a mechanism on the corpus and on variants
built from it, never the health of a connector: no canary runs on LOCAL, so no
check here can know one (CLAUDE.md design gate 3). A variant event is the
corpus's own health event under a new id, a planted row is a corpus row's
skeleton copied by SQL, and a planted manifest is a copy of one this checkout
carries or a few declaration lines written here, so no selector value enters
the tree. Each check is paired in CONTROLS with a breaker that removes its
mechanism.
"""

from __future__ import annotations

import datetime as dt
import json
import re
import sqlite3
import sys
import uuid

import yaml

from app import config
from app.http import routes
from app.model import collection, reads
from app.store import db, ingest
from app.tests.helpers import CASE, corpus_events, eid_of, files_digest, named
from app.tests.served import Client, corpus_copy, open_case

API = f"/api/cases/{CASE}"
STATIC = config.REPO_ROOT / "app" / "static"
DESIGN = config.REPO_ROOT / "docs" / "PLAINSIGHT-design.md"
MANIFESTS = sorted((config.REPO_ROOT / "connectors").glob("*/manifest.yaml"))

#: A second case id, opaque, for the rows a check plants beside the corpus case.
OTHER = str(uuid.uuid5(uuid.UUID(CASE), "collection: another case"))

LOCAL_SENTENCE = " On LOCAL nothing dispatches in any case (EG-1)."
NOT_ENFORCED = " No dispatch path reads this halt yet, and the deep-dive route refuses in every state."
NOT_PRESENT_LOCAL = "not the present state: no canary runs from this machine, because LOCAL executes no connector (EG-1)"
NOT_PRESENT_ISOLATED = "not the present state: no freshness window is declared, so whether it still holds is unknown"
UNNAMED = "recorded for one {unit}, which the record does not name"
NO_RECORD = "no health record read in this case names this connector"
CANARY_INPUTS = "the manifest's canary inputs are never shown here (RT-15)"

#: The closed shape of a connector row and of a record row. A key outside these would be a field nobody
#: decided to serve, a sort rank or an internal flag among them.
CONNECTOR_KEYS = {"connector_id", "capability", "title", "state", "state_vouch", "lines", "records"}
UNREADABLE_KEYS = CONNECTOR_KEYS - {"capability"}
RECORD_KEYS = {"event_id", "connector_id", "probe_unit", "text", "vouch"}
BOARD_KEYS = {
    "case_id", "summary", "scope", "capabilities", "connectors", "connectors_empty", "unmatched_heading",
    "unmatched", "unmatched_empty", "set_aside",
}


def manifests() -> list[dict]:
    return [yaml.safe_load(p.read_text(encoding="utf-8")) for p in MANIFESTS]


def keymap() -> dict:
    return json.loads((STATIC / "keymap.json").read_text(encoding="utf-8"))


def app_js() -> str:
    return (STATIC / "app.js").read_text(encoding="utf-8")


def view_js() -> str:
    return (STATIC / "views" / "collection.js").read_text(encoding="utf-8")


def design_71_block() -> str:
    """The five-state block of design section 7.1, as the design prints it."""
    text = DESIGN.read_text(encoding="utf-8")
    return text.split("## 7.1 ", 1)[1].split("```", 2)[1]


def recorded(state: str, ts: str, producer: str, canary: str | None) -> str:
    """The clause a record opens with, written out here so the check does not read it from the module."""
    said = f", canary {canary}" if canary else ", no canary named"
    return f'{state} recorded {ts} by {producer}{said}: design section 7.1 defines {state} as "{collection.DEFINED[state]}"'


def health(connector: str, state: str, ts: str, unit: str = "connector", reason: str | None = None) -> dict:
    """The corpus's health event under a new id, naming `connector`, `state`, `ts` and `unit`."""
    e = named(corpus_events(), "system-connector-health")
    e["event"]["event_id"] = str(uuid.uuid4())
    e["event"]["ts"] = ts
    e["payload"].update(connector_id=connector, state=state, probe_unit=unit)
    if reason is not None:
        e["payload"]["reason"] = reason
    return e


def land(root, events: list[dict]) -> None:
    """Land `events` in the corpus case through the door, one batch each, in order."""
    store = db.Store.open(root)
    try:
        for e in events:
            landed = ingest.ingest_batch(store, [e], None, origin="system").landed
            assert landed == 1, "a variant health event did not land"
    finally:
        store.close()


def served(ctx, events: list[dict], name: str = "collection") -> Client:
    """A server on a copy of the corpus store with `events` landed through the door, in order."""
    root = corpus_copy(ctx, name)
    land(root, events)
    return Client(ctx, root)


def plant(root, subtype: str, payload, case_id: str = OTHER, seq: int | None = None, ts: str | None = None) -> str:
    """Copy the corpus row of `subtype` into the skeleton under `case_id` and a new event id, with `payload`
    as its inline payload, a registry row for the case when it has none, `seq` as its arrival when one is
    given, and `ts` as its time when one is given. Returns the new event id."""
    event_id = str(uuid.uuid4())
    store = db.Store.open(root)
    try:
        conn = store.conn
        if conn.execute("SELECT 1 FROM case_registry WHERE case_id = ?", (case_id,)).fetchone() is None:
            cols = [r["name"] for r in conn.execute("PRAGMA table_info(case_registry)") if r["name"] != "case_id"]
            conn.execute(
                f"INSERT INTO case_registry (case_id, {', '.join(cols)}) SELECT ?, {', '.join(cols)} "
                "FROM case_registry WHERE case_id = ?", (case_id, CASE))
        cols = [r["name"] for r in conn.execute("PRAGMA table_info(event_skeleton)")
                if r["name"] not in ("seq", "event_id", "case_id", "case_seq", "payload_inline", "ts")]
        case_seq = conn.execute(
            "SELECT COALESCE(MAX(case_seq), 0) + 1 FROM event_skeleton WHERE case_id = ?", (case_id,)).fetchone()[0]
        inline = payload if isinstance(payload, str) else json.dumps(payload)
        conn.execute(
            f"INSERT INTO event_skeleton (seq, event_id, case_id, case_seq, payload_inline, ts, {', '.join(cols)}) "
            f"SELECT ?, ?, ?, ?, ?, COALESCE(?, ts), {', '.join(cols)} FROM event_skeleton "
            "WHERE case_id = ? AND event_type = 'SYSTEM_EVENT' AND event_subtype = ? ORDER BY seq LIMIT 1",
            (seq, event_id, case_id, case_seq, inline, ts, CASE, subtype))
        conn.commit()
    finally:
        store.close()
    return event_id


def connectors_root(ctx, second_id: str | None = None):
    """A connectors folder under tmp holding a copy of every manifest this checkout carries, and, when
    `second_id` is given, a second copy of the first one under that id and folder."""
    root = ctx.tmp / "connectors"
    for path in MANIFESTS:
        (root / path.parent.name).mkdir(parents=True)
        (root / path.parent.name / "manifest.yaml").write_bytes(path.read_bytes())
    if second_id is not None:
        text, n = re.subn(r"(?m)^id: .*$", f"id: {second_id}", MANIFESTS[0].read_text(encoding="utf-8"), count=1)
        assert n == 1, "the first manifest declares no id line to rewrite"
        (root / second_id).mkdir()
        (root / second_id / "manifest.yaml").write_text(text, encoding="utf-8")
    return root


def write_manifest(root, folder: str, text: str) -> None:
    (root / folder).mkdir(parents=True)
    (root / folder / "manifest.yaml").write_text(text, encoding="utf-8")


def board(c: Client) -> dict:
    r = c.get(f"{API}/collection")
    assert r.status == 200, "the COLLECTION route did not answer"
    return r.json()


def closed_shapes(d: dict) -> None:
    """Every row of a board carries its closed key set and nothing else."""
    assert set(d) == BOARD_KEYS, "the board carries a key outside its closed set"
    for row in d["connectors"]:
        assert set(row) in (CONNECTOR_KEYS, UNREADABLE_KEYS), "a connector row carries a key outside its closed set"
        for rec in row["records"]:
            assert set(rec) == RECORD_KEYS, "a record row carries a key outside its closed set"
    for rec in d["unmatched"]:
        assert set(rec) == RECORD_KEYS, "a record row carries a key outside its closed set"
    for line in d["capabilities"]:
        assert set(line) == {"capability", "text", "vouch"}


# ---------------------------------------------------------------------------
# the rows are the manifests, and every present state is UNVERIFIED (ruling 1C)
# ---------------------------------------------------------------------------


def check_rows_are_the_manifests_each_unverified(ctx):
    d = board(Client(ctx))
    declared = manifests()
    assert declared, "this checkout carries no manifest to check the board against"
    rows = {r["connector_id"]: r for r in d["connectors"]}
    assert sorted(rows) == sorted(m["id"] for m in declared), "the board's rows are not the checkout's manifests"
    for m in declared:
        row = rows[m["id"]]
        assert row["title"] == f"{m['id']} {m['version']} · {m['capability']} · {m['kind']}"
        assert row["state"] == (
            "UNVERIFIED, no canary runs from this machine, because LOCAL executes no connector (EG-1): "
            "this connector's state is unknown here")
        assert row["state_vouch"] is True, "an unknown state was not flagged as one the system does not vouch for"
        unit, cadence = m["health"]["probe_unit"], m["health"]["cadence"]
        assert row["lines"] == [
            f"declared by connectors/{m['id']}/manifest.yaml: probe unit {unit}, canary cadence {cadence}",
            f"canaries known_negative and known_positive, against a target declared {m['canary_subject_class']}; "
            + CANARY_INPUTS,
            NO_RECORD,
        ]
    one = "connector in this checkout" if len(declared) == 1 else "connectors in this checkout"
    assert d["summary"].startswith(f"{len(declared)} {one} · ")
    assert d["summary"].endswith(" · 1 health event in this case's log")
    closed_shapes(d)


def break_a_row_printed_as_healthy(ctx):
    ctx.mp.setattr(collection, "present_state", lambda environment: {"text": "HEALTHY, its canaries pass", "vouch": False})


def break_manifests_not_read(ctx):
    ctx.mp.setattr(collection, "declarations", lambda: [])


def break_internal_keys_served(ctx):
    real = collection.board

    def unpopped(conn, case_id, environment, at=None):
        out = real(conn, case_id, environment, at)
        for row in out["connectors"]:
            row["rank"] = 3
        return out

    ctx.mp.setattr(collection, "board", unpopped)


def test_rows_are_the_manifests_each_unverified(ctx):
    check_rows_are_the_manifests_each_unverified(ctx)


def check_capability_with_no_healthy_member_is_said(ctx):
    declared = manifests()
    c = Client(ctx)
    lines = {x["capability"]: x for x in board(c)["capabilities"]}
    assert sorted(lines) == sorted({m["capability"] for m in declared})
    for m in declared:
        members = sorted(x["id"] for x in declared if x["capability"] == m["capability"])
        count = "its one member is" if len(members) == 1 else f"its {len(members)} members are"
        assert lines[m["capability"]] == {
            "capability": m["capability"],
            "text": f"CAPABILITY {m['capability']} HAS NO HEALTHY MEMBER: {count} UNVERIFIED here ({', '.join(members)})",
            "vouch": True,
        }, "a capability with no healthy member was not said at the capability level"
    # Two members of one capability are counted and named together.
    first = declared[0]
    second = first["id"] + "-second"
    ctx.mp.setattr(collection, "CONNECTORS", connectors_root(ctx, second))
    members = sorted([x["id"] for x in declared if x["capability"] == first["capability"]] + [second])
    line = next(x for x in board(c)["capabilities"] if x["capability"] == first["capability"])
    assert line["text"] == (
        f"CAPABILITY {first['capability']} HAS NO HEALTHY MEMBER: its {len(members)} members are UNVERIFIED here "
        f"({', '.join(members)})"), "two members of one capability are not counted and named together"


def break_capability_line_removed(ctx):
    ctx.mp.setattr(collection, "capability_lines", lambda connectors: [])


def break_capability_line_names_one_member(ctx):
    real = collection.capability_lines

    def one_member(connectors):
        seen, kept = set(), []
        for c in connectors:
            if c.get("capability") in seen:
                continue
            seen.add(c.get("capability"))
            kept.append(c)
        return real(kept)

    ctx.mp.setattr(collection, "capability_lines", one_member)


def test_capability_with_no_healthy_member_is_said(ctx):
    check_capability_with_no_healthy_member_is_said(ctx)


# ---------------------------------------------------------------------------
# a recorded state is a dated record, never the present state (ruling 1C)
# ---------------------------------------------------------------------------


def check_recorded_state_is_a_dated_record_listed_apart(ctx):
    d = board(Client(ctx))
    e = named(corpus_events(), "system-connector-health")
    p = e["payload"]
    assert p["connector_id"] not in {r["connector_id"] for r in d["connectors"]}, \
        "the corpus names a connector the checkout carries, so this check has no record to list apart"
    assert d["unmatched_heading"] == "RECORDED IN THIS CASE FOR A CONNECTOR THIS CHECKOUT DOES NOT CARRY"
    assert [r["event_id"] for r in d["unmatched"]] == [eid_of("system-connector-health")], \
        "the record for a connector this checkout does not carry is not listed apart"
    rec = d["unmatched"][0]
    assert rec["connector_id"] == p["connector_id"] and rec["probe_unit"] == p["probe_unit"]
    assert rec["text"] == " · ".join([
        recorded(p["state"], e["event"]["ts"], e["source"]["producer"], p["canary_id"]), NOT_PRESENT_LOCAL])
    assert rec["vouch"] is True, "a recorded state is served without the flag that says the board does not vouch for it"
    body = json.dumps(d)
    for token in collection.DANGER:
        assert f'"{token}"' not in body, f"the bare state token {token} was rendered"
    for row in d["connectors"]:
        assert not row["records"] and row["lines"][-1] == NO_RECORD
    assert d["set_aside"] is None
    closed_shapes(d)


def break_recorded_state_printed_bare(ctx):
    ctx.mp.setattr(collection, "record_text", lambda e, earlier, environment: e["payload"]["state"])


def break_unmatched_record_dropped(ctx):
    ctx.mp.setattr(collection, "listed_apart", lambda latest, carried, environment: [])


def break_a_record_left_unflagged(ctx):
    real = collection.record_row
    ctx.mp.setattr(collection, "record_row", lambda e, earlier, environment: dict(real(e, earlier, environment), vouch=False))


def test_recorded_state_is_a_dated_record_listed_apart(ctx):
    check_recorded_state_is_a_dated_record_listed_apart(ctx)


def check_definitions_are_the_designs_words(ctx):
    """A record prints the design's definition of a state as the design's. Each definition is section 7.1's
    line for that state, word for word, and the states are that section's five."""
    block = design_71_block()
    states = re.findall(r"(?m)^\s*\S\s+([A-Z]+)\s", block)
    assert sorted(states) == sorted(collection.DEFINED) == sorted(collection.DANGER), \
        "the states a record may carry are not section 7.1's five"
    for state, definition in collection.DEFINED.items():
        assert re.search(rf"\b{state}\s+{re.escape(definition)}", block), \
            f"the definition printed for {state} is not design section 7.1's"
    assert set(collection.ACT_ON) == {"SUSPECT"}
    assert "verify before citing" in DESIGN.read_text(encoding="utf-8").split("## 7.4 ", 1)[1].split("## 7.5 ", 1)[0]
    assert collection.ACT_ON["SUSPECT"].startswith("verify before citing ")


def break_a_definition_reworded(ctx):
    ctx.mp.setitem(collection.DEFINED, "HEALTHY", "canaries passed and yield was within band then")


def test_definitions_are_the_designs_words(ctx):
    check_definitions_are_the_designs_words(ctx)


def check_a_record_sits_beside_the_connector_it_names(ctx):
    """The connector as a whole is one stream, and its latest record supersedes the earlier ones. An endpoint
    or subscription record names no endpoint, so the latest of each state is shown and a SUSPECT record is
    never hidden behind a later record of another state."""
    m = manifests()[0]
    reason = "the " + m["health"]["cadence"].replace("_", " ") + " pass named no failing check"
    events = [
        health(m["id"], "SUSPECT", "2026-01-15T10:20:00Z", "endpoint"),
        health(m["id"], "SUSPECT", "2026-01-15T10:20:00Z", "endpoint", reason),
        health(m["id"], "SUSPECT", "2026-01-15T10:19:00Z", "endpoint"),
        health(m["id"], "DOWN", "2026-01-15T10:19:00Z", "endpoint"),
        health(m["id"], "HEALTHY", "2026-01-15T10:23:00Z", "endpoint"),
        health(m["id"], "HEALTHY", "2026-01-15T10:17:00Z", "connector"),
        health(m["id"], "DEGRADED", "2026-01-15T10:21:00Z", "connector", ""),
        health(m["id"], "UNVERIFIED", "2026-01-15T10:22:00Z", "subscription"),
        health(m["id"], "HEALTHY", "2026-01-15T10:24:00Z", "subscription"),
    ]
    events[3]["payload"]["canary_id"] = ""
    events[6]["payload"]["canary_id"] = None
    d = board(served(ctx, events))
    row = next(r for r in d["connectors"] if r["connector_id"] == m["id"])
    ids = [r["event_id"] for r in row["records"]]
    suspect, down, healthy, degraded, unverified, subscribed = (events[i]["event"]["event_id"] for i in (1, 3, 4, 6, 7, 8))
    assert suspect in ids and ids.index(suspect) == 0, \
        "a SUSPECT endpoint record is hidden behind a later record of another state, or is not shown first"
    assert ids == [suspect, down, degraded, unverified, healthy, subscribed], \
        "the row does not hold the latest record of each group, by time and then by arrival, sorted by danger"
    producer, canary = events[0]["source"]["producer"], events[0]["payload"]["canary_id"]
    texts = [r["text"] for r in row["records"]]
    assert texts[0] == " · ".join([
        recorded("SUSPECT", "2026-01-15T10:20:00Z", producer, canary),
        "verify before citing what it produced then (design section 7.4)",
        f"recorded reason: {reason}",
        UNNAMED.format(unit="endpoint"),
        NOT_PRESENT_LOCAL,
        "the latest of 3 records of this state for this connector's endpoints in this case; each may concern "
        "another endpoint, and the earlier ones are not listed",
    ])
    assert texts[1] == " · ".join([
        recorded("DOWN", "2026-01-15T10:19:00Z", producer, None), UNNAMED.format(unit="endpoint"), NOT_PRESENT_LOCAL]), \
        "a record whose canary id is empty is not said to name no canary"
    assert texts[2] == " · ".join([
        recorded("DEGRADED", "2026-01-15T10:21:00Z", producer, None),
        NOT_PRESENT_LOCAL,
        "1 earlier record of this connector as a whole in this case, superseded and not listed",
    ]), "a record with no canary, an empty reason, the connector as its unit and one earlier record is misprinted"
    assert texts[3] == " · ".join([
        recorded("UNVERIFIED", "2026-01-15T10:22:00Z", producer, canary), UNNAMED.format(unit="subscription"),
        NOT_PRESENT_LOCAL])
    assert texts[4] == " · ".join([
        recorded("HEALTHY", "2026-01-15T10:23:00Z", producer, canary), UNNAMED.format(unit="endpoint"), NOT_PRESENT_LOCAL])
    assert texts[5] == " · ".join([
        recorded("HEALTHY", "2026-01-15T10:24:00Z", producer, canary), UNNAMED.format(unit="subscription"),
        NOT_PRESENT_LOCAL]), "a subscription record is merged with an endpoint record of its state"
    assert [r["probe_unit"] for r in row["records"]] == [
        "endpoint", "endpoint", "connector", "subscription", "endpoint", "subscription"]
    assert all(r["vouch"] is True for r in row["records"])
    assert row["lines"][-1] == "6 health records shown from this case, each a dated record and not the present state:"
    assert row["state"].startswith("UNVERIFIED, "), "a recorded state replaced the present one"
    assert [r["event_id"] for r in d["unmatched"]] == [eid_of("system-connector-health")]
    assert d["summary"].endswith(f" · {len(events) + 1} health events in this case's log")
    closed_shapes(d)


def break_latest_by_arrival_alone(ctx):
    ctx.mp.setattr(collection, "record_order", lambda found: found[1:2])


def break_latest_by_time_alone(ctx):
    ctx.mp.setattr(collection, "record_order", lambda found: found[:1])


def break_an_endpoint_record_supersedes_another_state(ctx):
    ctx.mp.setattr(collection, "group_key", lambda p: (p["connector_id"], p["probe_unit"]))


def break_probe_units_merged(ctx):
    real = collection.latest_records

    def merged(events, at):
        for e in events:
            if isinstance(e.get("payload"), dict):
                e["payload"]["probe_unit"] = "connector"
        return real(events, at)

    ctx.mp.setattr(collection, "latest_records", merged)


def test_a_record_sits_beside_the_connector_it_names(ctx):
    check_a_record_sits_beside_the_connector_it_names(ctx)


def check_rows_are_sorted_by_danger(ctx):
    """Design section 7.4: SUSPECT outranks DOWN. A connector that holds a SUSPECT record sits first whatever
    its name, a later HEALTHY endpoint record does not move it, and a record listed apart sorts the same way."""
    first = manifests()[0]["id"]
    second = first + "-second"
    apart = [f"apart-{n}" for n in ("a", "b", "c", "d", "e")]
    events = [
        health(second, "SUSPECT", "2026-01-15T10:20:00Z", "endpoint"),
        health(second, "HEALTHY", "2026-01-15T10:21:00Z", "endpoint"),
        health(apart[0], "HEALTHY", "2026-01-15T10:20:00Z"),
        health(apart[1], "DOWN", "2026-01-15T10:20:00Z"),
        health(apart[2], "SUSPECT", "2026-01-15T10:20:00Z"),
        health(apart[3], "DEGRADED", "2026-01-15T10:20:00Z"),
        health(apart[4], "UNVERIFIED", "2026-01-15T10:20:00Z"),
    ]
    ctx.mp.setattr(collection, "CONNECTORS", connectors_root(ctx, second))
    d = board(served(ctx, events))
    assert first < second, "the planted connector must sort after the first by name for this check to mean anything"
    order = [r["connector_id"] for r in d["connectors"]]
    assert order.index(second) < order.index(first), "a connector with a SUSPECT record does not sit first"
    corpus = named(corpus_events(), "system-connector-health")["payload"]["connector_id"]
    assert [r["connector_id"] for r in d["unmatched"]] == [apart[2], apart[1], apart[3], apart[4]] + sorted([apart[0], corpus]), \
        "the records listed apart are not sorted SUSPECT, DOWN, DEGRADED, UNVERIFIED, then HEALTHY by name"
    assert tuple(collection.DANGER) == ("SUSPECT", "DOWN", "DEGRADED", "UNVERIFIED", "HEALTHY")


def break_danger_order_is_the_alphabet(ctx):
    ctx.mp.setattr(collection, "DANGER", tuple(sorted(collection.DANGER)))


def break_a_row_ranks_by_its_latest_record(ctx):
    ctx.mp.setattr(collection, "group_key", lambda p: (p["connector_id"], p["probe_unit"]))


def test_rows_are_sorted_by_danger(ctx):
    check_rows_are_sorted_by_danger(ctx)


def check_a_record_that_records_no_observed_state_is_set_aside(ctx):
    m = manifests()[0]
    c = Client(ctx)
    e = named(corpus_events(), "system-connector-health")
    plant(c.root, "CONNECTOR_HEALTH", dict(e["payload"], state="DOWN"), case_id=CASE, ts="2999-01-01T00:00:00Z")
    d = board(c)
    assert [r["event_id"] for r in d["unmatched"]] == [eid_of("system-connector-health")], \
        "a record dated after now was read as the latest record"
    assert d["unmatched"][0]["text"].startswith("HEALTHY recorded ")
    assert d["set_aside"] == (
        "1 health event in this case carries a time after now, no readable time, or no connector, probe unit "
        "or state the model names, and is not read as a record")
    # Seven more that record nothing observed: no readable time, a payload that is not an object, no connector,
    # a probe unit the model does not name, a state it does not name, and a state and a unit that are no text.
    plant(c.root, "CONNECTOR_HEALTH", dict(e["payload"], state="DOWN"), case_id=CASE, ts="not a time")
    plant(c.root, "CONNECTOR_HEALTH", "[]", case_id=CASE)
    plant(c.root, "CONNECTOR_HEALTH", dict(e["payload"], connector_id="", state="DOWN"), case_id=CASE)
    plant(c.root, "CONNECTOR_HEALTH", dict(e["payload"], probe_unit="site", state="DOWN"), case_id=CASE)
    plant(c.root, "CONNECTOR_HEALTH", dict(e["payload"], state="FINE"), case_id=CASE)
    plant(c.root, "CONNECTOR_HEALTH", dict(e["payload"], state=["HEALTHY"]), case_id=CASE)
    plant(c.root, "CONNECTOR_HEALTH", dict(e["payload"], probe_unit=["endpoint"]), case_id=CASE)
    d = board(c)
    assert [r["event_id"] for r in d["unmatched"]] == [eid_of("system-connector-health")]
    assert d["set_aside"] == (
        "8 health events in this case carry a time after now, no readable time, or no connector, probe unit "
        "or state the model names, and are not read as a record")
    assert d["summary"].endswith(" · 9 health events in this case's log")
    # An event set aside is said on the row of the connector it names, so that row does not read as untouched.
    row = next(r for r in d["connectors"] if r["connector_id"] == m["id"])
    assert row["lines"][-1] == NO_RECORD and "set aside" not in " ".join(row["lines"])
    plant(c.root, "CONNECTOR_HEALTH", dict(e["payload"], connector_id=m["id"], state="DOWN"), case_id=CASE,
          ts="2999-01-01T00:00:00Z")
    row = next(r for r in board(c)["connectors"] if r["connector_id"] == m["id"])
    assert row["lines"][-2:] == ["1 health event that names this connector is set aside and not read as a record", NO_RECORD]
    plant(c.root, "CONNECTOR_HEALTH", dict(e["payload"], connector_id=m["id"], state="FINE"), case_id=CASE)
    row = next(r for r in board(c)["connectors"] if r["connector_id"] == m["id"])
    assert row["lines"][-2:] == ["2 health events that name this connector are set aside and not read as records", NO_RECORD]
    assert not row["records"]


def break_every_record_reads(ctx):
    ctx.mp.setattr(collection, "readable", lambda e, at: True)


def break_an_unnamed_probe_unit_reads(ctx):
    ctx.mp.setattr(collection, "PROBE_UNITS", collection.PROBE_UNITS + ("site",))


def break_an_unnamed_state_reads(ctx):
    ctx.mp.setitem(collection.DEFINED, "FINE", "it was fine then")
    ctx.mp.setattr(collection, "DANGER", collection.DANGER + ("FINE",))


def break_an_unreadable_time_reads(ctx):
    real = reads.instant
    epoch = dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc)
    ctx.mp.setattr(reads, "instant", lambda value: real(value) or epoch)


def break_a_set_aside_event_is_not_said_on_its_row(ctx):
    real = collection.records_lines
    ctx.mp.setattr(collection, "records_lines", lambda records, aside, what="this connector": real(records, 0, what))


def test_a_record_that_records_no_observed_state_is_set_aside(ctx):
    check_a_record_that_records_no_observed_state_is_set_aside(ctx)


def check_a_record_dated_at_the_reads_instant_is_read(ctx):
    """The boundary of "after now": a record whose time is the instant of the read is read, and one second
    earlier the same record is dated after the read and is set aside."""
    root = corpus_copy(ctx, "boundary")
    e = named(corpus_events(), "system-connector-health")
    at = reads.instant(e["event"]["ts"])
    store = open_case(root)
    try:
        on_time = collection.board(store.conn, CASE, "LOCAL", at=at)
        early = collection.board(store.conn, CASE, "LOCAL", at=at - dt.timedelta(seconds=1))
    finally:
        store.close()
    assert [r["event_id"] for r in on_time["unmatched"]] == [eid_of("system-connector-health")], \
        "a record dated at the instant of the read was set aside"
    assert on_time["set_aside"] is None
    assert early["unmatched"] == [] and early["set_aside"] is not None, "a record dated after the read was read"
    assert early["unmatched_empty"] == "no health record is read from this case's log"


def break_a_record_dated_now_is_set_aside(ctx):
    real = collection.readable
    ctx.mp.setattr(collection, "readable", lambda e, at: real(e, at - dt.timedelta(microseconds=1)))


def test_a_record_dated_at_the_reads_instant_is_read(ctx):
    check_a_record_dated_at_the_reads_instant_is_read(ctx)


def check_an_empty_list_apart_says_which_empty_it_is(ctx):
    """No record at all, and every record matched, are two different facts, and the board says which."""
    m = manifests()[0]
    events = [e for e in corpus_events() if e["event"]["event_id"] != eid_of("system-connector-health")]
    store = ctx.built("no-health", events)
    c = Client(ctx, store.root)
    d = board(c)
    assert d["unmatched"] == [] and d["unmatched_empty"] == "no health record is read from this case's log"
    assert d["summary"].endswith(" · 0 health events in this case's log")
    land(store.root, [health(m["id"], "HEALTHY", "2026-01-15T10:20:00Z")])
    d = board(c)
    assert d["unmatched"] == []
    assert d["unmatched_empty"] == "every health record read in this case names a connector this checkout carries"
    row = next(r for r in d["connectors"] if r["connector_id"] == m["id"])
    assert row["lines"][-1] == "1 health record shown from this case, each a dated record and not the present state:"
    assert len(row["records"]) == 1 and "earlier record" not in row["records"][0]["text"]
    assert "recorded for one" not in row["records"][0]["text"] and "the latest of" not in row["records"][0]["text"]


def break_one_sentence_for_both_empties(ctx):
    real = collection.board

    def one_sentence(conn, case_id, environment, at=None):
        out = real(conn, case_id, environment, at)
        out["unmatched_empty"] = "every health record read in this case names a connector this checkout carries"
        return out

    ctx.mp.setattr(collection, "board", one_sentence)


def test_an_empty_list_apart_says_which_empty_it_is(ctx):
    check_an_empty_list_apart_says_which_empty_it_is(ctx)


def check_another_environment_is_not_said_in_locals_terms(ctx):
    """LOCAL's reason is EG-1. In ISOLATED the reason a recorded state is not the present one is that no
    freshness window is declared, and the board says that and never LOCAL's rule."""
    root = corpus_copy(ctx, "isolated-terms")
    store = open_case(root)
    try:
        d = collection.board(store.conn, CASE, "ISOLATED")
    finally:
        store.close()
    text = json.dumps(d)
    assert "LOCAL" not in text and "EG-1" not in text, "the board states LOCAL's rule in another environment"
    assert d["connectors"] and d["capabilities"], "the board in another environment lost its rows or its capability lines"
    for row in d["connectors"]:
        assert row["state"] == (
            "UNVERIFIED, no freshness window is declared for a recorded state, so none is read as the "
            "present one: this connector's state is unknown here")
        assert row["state_vouch"] is True
    assert d["unmatched"] and d["unmatched"][0]["text"].endswith(" · " + NOT_PRESENT_ISOLATED)
    assert d["unmatched"][0]["vouch"] is True


def break_every_environment_reads_as_local(ctx):
    real = collection.board
    ctx.mp.setattr(collection, "board", lambda conn, case_id, environment, at=None: real(conn, case_id, "LOCAL", at))


def test_another_environment_is_not_said_in_locals_terms(ctx):
    check_another_environment_is_not_said_in_locals_terms(ctx)


# ---------------------------------------------------------------------------
# the board reads one case, through a connection that cannot write (ruling 2A)
# ---------------------------------------------------------------------------


def check_board_reads_one_case_and_says_so(ctx):
    c = Client(ctx)
    e = named(corpus_events(), "system-connector-health")
    other_connector = e["payload"]["connector_id"] + "-" + OTHER[:8]
    plant(c.root, "CONNECTOR_HEALTH", dict(e["payload"], connector_id=other_connector, state="DOWN"))
    d = board(c)
    assert [r["connector_id"] for r in d["unmatched"]] == [e["payload"]["connector_id"]], \
        "a health record of another case was read into this case's board"
    assert d["scope"] == (
        f"scope: case {CASE[:8]} only. A health record is read from this case's log, and a record in another "
        "case is not read here")
    assert d["case_id"] == CASE
    assert d["summary"].endswith(" · 1 health event in this case's log"), "another case's event was counted"
    r = c.get(f"{API}/collection?focus={CASE}")
    assert r.status == 400 and r.json()["refused"] == "QUERY_KEY_REFUSED", "the board's route takes a query key"


def break_board_reads_every_case(ctx):
    def every_case(conn, case_id):
        rows = conn.execute(
            reads.SKELETON_SELECT
            + "WHERE s.event_type = 'SYSTEM_EVENT' AND s.event_subtype = 'CONNECTOR_HEALTH' ORDER BY s.seq")
        return [reads._shape(r) for r in rows]

    ctx.mp.setattr(collection, "health_events", every_case)


def break_board_route_takes_a_query_key(ctx):
    ctx.mp.setattr(routes, "ROUTES", tuple(
        routes._route("GET", "/api/cases/{case}/collection", "collection", ("focus",)) if r.handler == "collection" else r
        for r in routes.ROUTES))


def test_board_reads_one_case_and_says_so(ctx):
    check_board_reads_one_case_and_says_so(ctx)


def check_board_is_read_through_a_connection_that_cannot_write(ctx):
    """The board's handler opens the case as every GET does: SQLite refuses a write on its connection."""
    tried = []
    real = collection.board

    def probing(conn, case_id, environment, at=None):
        try:
            conn.execute(
                "INSERT INTO workspace_kv (analyst, view, key, value_json, updated_at) "
                "VALUES ('a', 'collection', 'hops', '2', 'x')")
            tried.append("accepted")
        except sqlite3.OperationalError as exc:
            tried.append(str(exc))
        return real(conn, case_id, environment, at)

    ctx.mp.setattr(collection, "board", probing)
    c = Client(ctx)
    before = files_digest(c.root)
    board(c)
    assert len(tried) == 1 and ("readonly" in tried[0] or "read-only" in tried[0]), \
        f"the board's connection accepted a write: {tried}"
    assert files_digest(c.root) == before


def break_board_opens_the_case_for_writing(ctx):
    def writing(app, params, query, body):
        with routes.case_store(app.root, params["case"], write=True) as store:
            return routes.json_response(collection.board(store.conn, params["case"], app.environment))

    ctx.mp.setitem(routes.HANDLERS, "collection", writing)


def test_board_is_read_through_a_connection_that_cannot_write(ctx):
    check_board_is_read_through_a_connection_that_cannot_write(ctx)


# ---------------------------------------------------------------------------
# what a manifest row may print
# ---------------------------------------------------------------------------


def check_no_canary_input_is_shown(ctx):
    c = Client(ctx)
    body = c.get(f"{API}/collection").body.decode("utf-8")
    inputs = [v for m in manifests() for canary in m["health"]["canaries"].values() for v in canary["input"].values()]
    assert inputs and all(isinstance(v, str) and len(v) > 2 for v in inputs), \
        "the manifests declare no canary input to look for"
    for v in inputs:
        assert v not in body and v[1:-1] not in body, "a canary's input reached the board"
    row = board(c)["connectors"][0]
    assert any(line.startswith("canaries known_negative and known_positive, ") for line in row["lines"])


def break_canary_inputs_printed(ctx):
    def names_and_inputs(health_block):
        canaries = health_block.get("canaries") or {}
        return sorted(f"{name} {json.dumps(canary.get('input'))}" for name, canary in canaries.items())

    ctx.mp.setattr(collection, "canary_names", names_and_inputs)


def test_no_canary_input_is_shown(ctx):
    check_no_canary_input_is_shown(ctx)


def check_an_unreadable_manifest_is_listed(ctx):
    """A manifest that cannot be read is a connector the checkout carries, under its folder's name: it is
    listed, counted, and holds the records that name it, which are not listed apart."""
    root = connectors_root(ctx)
    write_manifest(root, "not-yaml", "id: [unclosed\n")
    ctx.mp.setattr(collection, "CONNECTORS", root)
    e = named(corpus_events(), "system-connector-health")
    c = Client(ctx)
    assert board(c)["summary"].startswith(
        f"{len(MANIFESTS) + 1} connectors in this checkout, 1 with a manifest that cannot be read · ")
    # The manifests are read on every request, so three more that cannot be read are on the next board: a
    # list, bytes that are no UTF-8, and a folder where the file should be.
    write_manifest(root, "not-a-mapping", "- one\n- two\n")
    (root / "not-utf8").mkdir()
    (root / "not-utf8" / "manifest.yaml").write_bytes(b"\xff\xfe\x00id: x\n")
    (root / "not-a-file" / "manifest.yaml").mkdir(parents=True)
    unread = ["not-a-file", "not-a-mapping", "not-utf8", "not-yaml"]
    d = board(c)
    rows = {r["connector_id"]: r for r in d["connectors"]}
    assert set(rows) == {m["id"] for m in manifests()} | set(unread), "a manifest that cannot be read was skipped"
    for name in unread:
        assert rows[name] == {
            "connector_id": name,
            "title": f"{name} · connectors/{name}/manifest.yaml",
            "state": (f"connectors/{name}/manifest.yaml could not be read as a manifest: this checkout carries a "
                      "connector the board cannot describe, and its state is unknown here"),
            "state_vouch": True,
            "lines": ["no health record read in this case names this folder's name"],
            "records": [],
        }
    assert d["summary"].startswith(
        f"{len(MANIFESTS) + 4} connectors in this checkout, 4 with manifests that cannot be read · ")
    assert sorted(x["capability"] for x in d["capabilities"]) == sorted({m["capability"] for m in manifests()})
    closed_shapes(d)
    # A record that names the folder sits on its row and is not listed apart.
    planted = plant(c.root, "CONNECTOR_HEALTH", dict(e["payload"], connector_id="not-yaml", state="DOWN"), case_id=CASE)
    d = board(c)
    row = next(r for r in d["connectors"] if r["connector_id"] == "not-yaml")
    assert [r["event_id"] for r in row["records"]] == [planted], \
        "a record that names an unreadable manifest's folder is not on that folder's row"
    assert row["lines"] == ["1 health record shown from this case, each a dated record and not the present state:"]
    assert planted not in [r["event_id"] for r in d["unmatched"]], \
        "a record for a connector the checkout carries, unread, is listed as one it does not carry"
    assert d["connectors"][0]["connector_id"] == "not-yaml", "an unreadable connector with a DOWN record does not sit first"


def break_unreadable_manifest_skipped(ctx):
    real = collection.declarations
    ctx.mp.setattr(collection, "declarations", lambda: [d for d in real() if d["readable"]])


def break_an_unreadable_folder_is_not_carried(ctx):
    ctx.mp.setattr(collection, "carried_ids", lambda found: {d["connector_id"] for d in found if d["readable"]})


def break_only_bad_yaml_is_unreadable(ctx):
    def strict(path):
        manifest = yaml.safe_load(path.read_text(encoding="utf-8", errors="replace")) if path.is_file() else {}
        return manifest if isinstance(manifest, dict) else None

    def reading(path):
        try:
            return strict(path)
        except yaml.YAMLError:
            return None

    ctx.mp.setattr(collection, "read_manifest", reading)


def test_an_unreadable_manifest_is_listed(ctx):
    check_an_unreadable_manifest_is_listed(ctx)


MINIMAL = """id: {id}
version: "1.0.0"
capability: one.thing
kind: one_shot
health:
  probe_unit: connector
  cadence: hourly
  canaries:
    known_positive: {{}}
canary_subject_class: synthetic
"""


def check_a_missing_declaration_is_said(ctx):
    """A row prints what its manifest declares as text and says what it does not: a missing id, a value YAML
    read as a number or a list, a health block or canaries that are no mapping, one canary, and an id that
    is not its folder's name. No capability line is built on a capability nobody declared."""
    root = connectors_root(ctx)
    write_manifest(root, "declares-nothing", "manifest_schema: none\n")
    write_manifest(root, "one-canary", MINIMAL.format(id="one-canary"))
    write_manifest(root, "other-folder", MINIMAL.format(id="another-id"))
    write_manifest(root, "typed", MINIMAL.format(id="typed").replace('version: "1.0.0"', "version: 1.10")
                   .replace("cadence: hourly", "cadence: [hourly, on_use]").replace("kind: one_shot", "kind: 2026-11-14"))
    write_manifest(root, "health-list", "id: health-list\ncapability: one.thing\nhealth: [a, b]\n")
    write_manifest(root, "canary-list", "id: canary-list\nhealth:\n  canaries: [a, b]\n")
    write_manifest(root, "empty-id", 'id: ""\nversion: ""\n')
    ctx.mp.setattr(collection, "CONNECTORS", root)
    d = board(Client(ctx))
    rows = {r["connector_id"]: r for r in d["connectors"]}
    assert "empty-id" in rows, "a manifest whose id is empty is not listed under its folder's name"
    assert rows["empty-id"]["title"] == "empty-id, version not declared · capability not declared · kind not declared"
    assert rows["empty-id"]["lines"][0] == (
        "the manifest declares no id as text, so this row is listed under its folder's name")
    assert "declares-nothing" in rows, "a manifest that declares no id is not listed under its folder's name"
    row = rows["declares-nothing"]
    assert row["title"] == "declares-nothing, version not declared · capability not declared · kind not declared"
    assert row["lines"] == [
        "the manifest declares no id as text, so this row is listed under its folder's name",
        "declared by connectors/declares-nothing/manifest.yaml: probe unit not declared, canary cadence not declared",
        "no canary declared, with a target class not declared; " + CANARY_INPUTS,
        NO_RECORD,
    ]
    assert row["state"].startswith("UNVERIFIED, ") and row["state_vouch"] is True
    assert rows["one-canary"]["title"] == "one-canary 1.0.0 · one.thing · one_shot"
    assert rows["one-canary"]["lines"] == [
        "declared by connectors/one-canary/manifest.yaml: probe unit connector, canary cadence hourly",
        "canary known_positive, against a target declared synthetic; " + CANARY_INPUTS,
        NO_RECORD,
    ]
    assert rows["another-id"]["lines"][0] == (
        "the manifest declares the id another-id in the folder other-folder, and the manifest gate refuses an id "
        "that is not its folder's name")
    assert rows["typed"]["title"] == "typed, version not declared as text · one.thing · kind not declared as text", \
        "a value YAML read as a number or a date was printed as if the file declared it"
    assert rows["typed"]["lines"][0] == (
        "declared by connectors/typed/manifest.yaml: probe unit connector, canary cadence not declared as text")
    assert rows["health-list"]["lines"][:3] == [
        "the manifest's health block is not a mapping, so nothing in it is read",
        "declared by connectors/health-list/manifest.yaml: probe unit not declared, canary cadence not declared",
        "no canary declared, with a target class not declared; " + CANARY_INPUTS,
    ]
    assert rows["canary-list"]["lines"][1] == (
        "canaries not declared as a mapping, with a target class not declared; " + CANARY_INPUTS)
    capabilities = {m["capability"] for m in manifests()} | {"one.thing"}
    assert sorted(c["capability"] for c in d["capabilities"]) == sorted(capabilities), \
        "a capability line was printed for a capability no manifest declares"
    assert f" · {len(capabilities)} capabilities declared · " in d["summary"]
    for m in manifests():
        assert rows[m["id"]]["lines"][0].startswith("declared by "), "a declared id was said to be missing"
    closed_shapes(d)


def break_a_missing_id_printed_as_a_value(ctx):
    ctx.mp.setattr(collection, "declared_id", lambda manifest, folder: (str(manifest.get("id")), True))


def break_an_undeclared_capability_gets_a_line(ctx):
    real = collection.capability_lines

    def naming_the_missing(connectors):
        for c in connectors:
            if c.get("capability") == collection.NOT_DECLARED:
                c["capability"] = "undeclared"
        return real(connectors)

    ctx.mp.setattr(collection, "capability_lines", naming_the_missing)


def break_a_number_printed_for_a_version(ctx):
    ctx.mp.setattr(collection, "_text", lambda value: collection.NOT_DECLARED if value in (None, "") else str(value))


def break_one_canary_said_as_several(ctx):
    real = collection.canary_line
    ctx.mp.setattr(collection, "canary_line", lambda d: real(d).replace("canary known_positive,", "canaries known_positive,"))


def test_a_missing_declaration_is_said(ctx):
    check_a_missing_declaration_is_said(ctx)


# ---------------------------------------------------------------------------
# the RT-11 line states its evidence and its limit (ruling 3B)
# ---------------------------------------------------------------------------


def halt_text(environment: str = "LOCAL") -> str:
    e = named(corpus_events(), "system-shred-failed")
    line = (
        f"HALTED, a shred failed in case {CASE[:8]} at {e['event']['ts']} (check {e['payload']['failed_check']}): "
        "no new run dispatches system-wide (RT-11). This build reads no clearing, because verify_shred has no "
        "passing path yet."
    )
    return line + (LOCAL_SENTENCE if environment == "LOCAL" else NOT_ENFORCED)


def check_halt_states_its_evidence_and_limit(ctx):
    c = Client(ctx)
    want = halt_text()
    assert c.get(f"{API}/header").json().get("halt") == want, \
        "the header's RT-11 line does not state its evidence and its limit"
    assert c.get("/api/cases").json().get("halt") == want, "the case list does not carry the RT-11 line"
    store = db.Store.open(c.root)
    try:
        assert reads.halt_line(store.conn, "ISOLATED") == halt_text("ISOLATED"), \
            "outside LOCAL the line states LOCAL's rule, or claims an enforcement nothing performs"
    finally:
        store.close()
    # A store whose log holds no failed shred carries no line, on the header and on the case list.
    events = [e for e in corpus_events() if e["event"]["event_id"] != eid_of("system-shred-failed")]
    quiet = Client(ctx, ctx.built("no-failed-shred", events).root)
    header = quiet.get(f"{API}/header").json()
    assert "halt" in header and header["halt"] is None, "a store with no failed shred shows the RT-11 line"
    cases = quiet.get("/api/cases").json()
    assert "halt" in cases and cases["halt"] is None, "a store with no failed shred shows the RT-11 line on the case list"


def break_halt_names_no_evidence(ctx):
    ctx.mp.setattr(reads, "halt_line", lambda conn, environment:
                   "HALTED, a shred failed: no new run will dispatch system-wide (RT-11)")


def break_case_list_carries_no_halt(ctx):
    real = routes.HANDLERS["cases"]

    def without(app, params, query, body):
        obj = json.loads(real(app, params, query, body).body)
        obj["halt"] = None
        return routes.json_response(obj)

    ctx.mp.setitem(routes.HANDLERS, "cases", without)


def break_halt_read_needs_an_attached_case(ctx):
    real = reads.halt_line

    def joined(conn, environment):
        conn.execute(reads.SKELETON_SELECT + "WHERE s.event_subtype = 'SHRED_FAILED'").fetchall()
        return real(conn, environment)

    ctx.mp.setattr(reads, "halt_line", joined)


def break_local_sentence_in_every_environment(ctx):
    real = reads.halt_line
    ctx.mp.setattr(reads, "halt_line", lambda conn, environment: real(conn, "LOCAL"))


def break_the_halt_claims_enforcement_outside_local(ctx):
    ctx.mp.setattr(reads, "NOT_ENFORCED_BY_THE_HALT", "")


def break_halt_always_lit(ctx):
    real = reads.halt_line
    ctx.mp.setattr(reads, "halt_line", lambda conn, environment: real(conn, environment) or halt_text(environment))


def test_halt_states_its_evidence_and_limit(ctx):
    check_halt_states_its_evidence_and_limit(ctx)


def check_the_routes_answer_for_the_applications_environment(ctx):
    """The header, the case list and the board are written for the environment the application read at
    launch. Every store that opens today is LOCAL, so the routes are held to another environment here by
    setting it on the running application. A route that answered in LOCAL's terms whatever the application
    says passes every other check in this module, which a hand mutant showed on 2026-11-14."""
    c = Client(ctx)
    ctx.mp.setattr(c.app, "environment", "ISOLATED")
    want = halt_text("ISOLATED")
    assert c.get(f"{API}/header").json().get("halt") == want, \
        "the header's RT-11 line is not written for the application's environment"
    assert c.get("/api/cases").json().get("halt") == want, \
        "the case list's RT-11 line is not written for the application's environment"
    text = json.dumps(c.get(f"{API}/collection").json())
    assert "LOCAL" not in text and "EG-1" not in text, \
        "the COLLECTION route states LOCAL's rule while the application runs in another environment"


def break_the_collection_route_answers_as_local(ctx):
    real = collection.board
    ctx.mp.setattr(collection, "board", lambda conn, case_id, environment, at=None: real(conn, case_id, "LOCAL", at))


def test_the_routes_answer_for_the_applications_environment(ctx):
    check_the_routes_answer_for_the_applications_environment(ctx)


def _halt_of(root) -> str | None:
    store = db.Store.open(root)
    try:
        return reads.halt_line(store.conn, "LOCAL")
    except sqlite3.Error as exc:
        raise AssertionError(f"the halt read raised {type(exc).__name__}") from exc
    finally:
        store.close()


def _more(n: int) -> str:
    said = "1 more failed shred that halts is" if n == 1 else f"{n} more failed shreds that halt are"
    return halt_text().replace("):", f"), and {said} on record in this store:", 1)


def check_halt_counts_every_failed_shred(ctx):
    failed = named(corpus_events(), "system-shred-failed")
    root = corpus_copy(ctx, "halts")
    assert _halt_of(root) == halt_text()
    plant(root, "SHRED_FAILED", dict(failed["payload"], halt_system_wide=False))
    assert _halt_of(root) == halt_text(), "a failed shred that says it does not halt was counted"
    plant(root, "SHRED_FAILED", dict(failed["payload"], failed_check=1))
    assert _halt_of(root) == _more(1), "a second halting shred was not counted"
    plant(root, "SHRED_FAILED", "[]")
    assert _halt_of(root) == _more(2), "a failed shred whose payload cannot be read was not read as halting"
    plant(root, "SHRED_FAILED", {k: v for k, v in failed["payload"].items() if k != "halt_system_wide"})
    assert _halt_of(root) == _more(3), "a failed shred whose payload does not say whether it halts was read as not halting"
    # The line names the first halting shred by arrival, whatever time it carries. One that arrived before the
    # corpus's, carries a later time and a payload that is not JSON is named by its own case and time, and the
    # line says that no check can be read from it.
    tail = (": no new run dispatches system-wide (RT-11). This build reads no clearing, because verify_shred has "
            "no passing path yet." + LOCAL_SENTENCE)
    plant(root, "SHRED_FAILED", "{", seq=0, ts="2026-01-16T00:00:00Z")
    assert _halt_of(root) == (
        f"HALTED, a shred failed in case {OTHER[:8]} at 2026-01-16T00:00:00Z (no failed check can be read from it), "
        "and 4 more failed shreds that halt are on record in this store" + tail), \
        "the line does not name the first halting shred by arrival"
    # A failed check that is no whole number is not printed as one.
    plant(root, "SHRED_FAILED", dict(failed["payload"], failed_check=True), seq=-1, ts="2026-01-17T00:00:00Z")
    assert _halt_of(root) == (
        f"HALTED, a shred failed in case {OTHER[:8]} at 2026-01-17T00:00:00Z (no failed check can be read from it), "
        "and 5 more failed shreds that halt are on record in this store" + tail), \
        "a failed check that is true was printed as a check"


def break_only_the_first_failed_shred_is_said(ctx):
    ctx.mp.setattr(reads, "more_failed", lambda more: "")


def break_unreadable_payload_reads_as_no_halt(ctx):
    real = reads.halting

    def lenient(payload_inline):
        try:
            p = json.loads(payload_inline) if payload_inline else None
        except ValueError:
            p = None
        return real(payload_inline) if isinstance(p, dict) else (False, None)

    ctx.mp.setattr(reads, "halting", lenient)


def break_a_payload_with_no_flag_reads_as_no_halt(ctx):
    real = reads.halting

    def by_truth(payload_inline):
        halts, check = real(payload_inline)
        try:
            p = json.loads(payload_inline) if payload_inline else None
        except ValueError:
            p = None
        return (bool(p.get("halt_system_wide")) if isinstance(p, dict) else halts), check

    ctx.mp.setattr(reads, "halting", by_truth)


def break_a_shred_that_does_not_halt_is_counted(ctx):
    real = reads.halting
    ctx.mp.setattr(reads, "halting", lambda payload_inline: (True, real(payload_inline)[1]))


def test_halt_counts_every_failed_shred(ctx):
    check_halt_counts_every_failed_shred(ctx)


# ---------------------------------------------------------------------------
# key 5, the view and the banner on the case list
# ---------------------------------------------------------------------------


def check_collection_view_is_wired(ctx):
    c = Client(ctx)
    assert c.get(f"/c/{CASE}/collection").status == 200, "the server does not serve COLLECTION as a view"
    assert c.get("/static/views/collection.js").status == 200
    c.login()
    saved = c.send("PUT", f"/api/kv/{CASE}/collection", {"hops": 2, "drawer": "closed"})
    assert saved.status == 200, "the workspace store refuses the view the shell saves state for"
    keys = keymap()["keys"]
    five = [k for k in keys if k["key"] == "5"]
    one = next(k for k in keys if k["key"] == "1")
    assert len(five) == 1, "key 5 is not bound once"
    assert five[0]["action"] == "view_collection" and five[0]["built"] is True
    assert (five[0]["origin"], five[0]["design"]) == (one["origin"], one["design"]), "key 5 is not design 8.6's view key"
    js = app_js()
    assert 'import { renderCollection } from "./views/collection.js";' in js
    assert "export async function renderCollection(pane, state) {" in view_js(), \
        "the view does not export the function the shell imports"
    assert '"collection"' in js.split("const VIEWS = ", 1)[1].split(";", 1)[0]
    assert 'view_collection: () => go({ view: "collection" }),' in js
    assert 'mk("collection", "5", "COLLECTION")' in js, "the shell shows no button for the view"
    assert 'else if (state.view === "collection") await renderCollection(view, state);' in js
    show = js.split("function showHalt(text) {", 1)[1].split("\n}\n", 1)[0]
    assert "halt.hidden = !text;" in show and 'halt.textContent = text || "";' in show, \
        "the RT-11 line is not hidden when the server sends none, or keeps a stale text"
    landing = js.split("async function landing() {", 1)[1].split("\n}\n", 1)[0]
    header = js.split("async function header() {", 1)[1].split("\n}\n", 1)[0]
    assert "showHalt(r.body.halt);" in header, "the case header does not fill the RT-11 line"
    assert "  showHalt(r.body.halt);\n  if (r.body.cases.length === 1" in landing, \
        "the case list does not fill the RT-11 line before it decides what to show"


def break_collection_not_a_served_view(ctx):
    ctx.mp.setattr(routes, "VIEWS", tuple(v for v in routes.VIEWS if v != "collection"))


def break_key_five_unbound(ctx):
    real = keymap()
    real["keys"] = [k for k in real["keys"] if k["key"] != "5"]
    ctx.mp.setattr(sys.modules[__name__], "keymap", lambda: real)


def break_case_list_never_fills_the_banner(ctx):
    real = app_js()
    head, rest = real.split("async function landing() {", 1)
    broken = head + "async function landing() {" + rest.replace("  showHalt(r.body.halt);\n", "", 1)
    ctx.mp.setattr(sys.modules[__name__], "app_js", lambda: broken)


def break_banner_never_hidden(ctx):
    real = app_js()
    ctx.mp.setattr(sys.modules[__name__], "app_js", lambda: real.replace("halt.hidden = !text;", "halt.hidden = false;", 1))


def break_view_export_renamed(ctx):
    real = view_js()
    ctx.mp.setattr(sys.modules[__name__], "view_js",
                   lambda: real.replace("export async function renderCollection(", "export async function renderBoard(", 1))


def break_workspace_refuses_the_view(ctx):
    from app.store import kv

    ctx.mp.setattr(kv, "TOKENS", frozenset(kv.TOKENS - {"collection"}))


def test_collection_view_is_wired(ctx):
    check_collection_view_is_wired(ctx)


def check_view_prints_the_servers_lines_and_flags(ctx):
    """The view computes nothing: it fetches the board, prints the server's lines, paints red from the
    server's flags, and its l button opens the Lineage Drawer on the record's event."""
    js = view_js()
    assert "getJSON(`/api/cases/${state.caseId}/collection`)" in js
    for printed in ("d.summary", "d.scope", "c.text", "d.set_aside", "c.title", "c.state", "c.lines.map(",
                    "c.records.map(record)", "d.unmatched_heading", "d.connectors_empty", "d.unmatched_empty",
                    "rec.text"):
        assert printed in js, f"the view does not print {printed}"
    assert "for (const rec of d.unmatched) kids.push(" in js, "the view does not print the records listed apart"
    assert 'class: c.state_vouch ? "vouch" : ""' in js and 'class: rec.vouch ? "vouch" : ""' in js, \
        "red does not come from the server's flags"
    assert 'go({ lineage: rec.event_id, dir: "back" })' in js, "a record's button does not open its event"
    code = " ".join(line for line in js.splitlines() if not line.lstrip().startswith("//"))
    for token in collection.DANGER:
        assert token not in code, "the view names a state token of its own"
    assert not re.search(r"[^a-zA-Z](sort|filter|reduce|Math\.)\(", code), "the view computes or reorders"


def break_view_paints_from_its_own_rule(ctx):
    real = view_js()
    ctx.mp.setattr(sys.modules[__name__], "view_js",
                   lambda: real.replace('class: rec.vouch ? "vouch" : ""', 'class: rec.vouch ? "" : "vouch"', 1))


def break_view_reorders_the_rows(ctx):
    real = view_js()
    ctx.mp.setattr(sys.modules[__name__], "view_js",
                   lambda: real.replace("for (const c of d.connectors) {", "for (const c of d.connectors.sort()) {", 1))


def break_view_drops_the_list_apart(ctx):
    real = view_js()
    ctx.mp.setattr(sys.modules[__name__], "view_js",
                   lambda: real.replace("for (const rec of d.unmatched) kids.push(", "for (const rec of []) kids.push(", 1))


def test_view_prints_the_servers_lines_and_flags(ctx):
    check_view_prints_the_servers_lines_and_flags(ctx)


CONTROLS = [
    ("a connector row printed as healthy", check_rows_are_the_manifests_each_unverified, break_a_row_printed_as_healthy),
    ("the manifests are not read", check_rows_are_the_manifests_each_unverified, break_manifests_not_read),
    ("an internal key is served", check_rows_are_the_manifests_each_unverified, break_internal_keys_served),
    ("the capability line removed", check_capability_with_no_healthy_member_is_said, break_capability_line_removed),
    ("the capability line names one member", check_capability_with_no_healthy_member_is_said, break_capability_line_names_one_member),
    ("a recorded state printed bare", check_recorded_state_is_a_dated_record_listed_apart, break_recorded_state_printed_bare),
    ("a record for a connector not carried is dropped", check_recorded_state_is_a_dated_record_listed_apart, break_unmatched_record_dropped),
    ("a recorded state is left unflagged", check_recorded_state_is_a_dated_record_listed_apart, break_a_record_left_unflagged),
    ("a definition is reworded", check_definitions_are_the_designs_words, break_a_definition_reworded),
    ("the latest record is the last to arrive", check_a_record_sits_beside_the_connector_it_names, break_latest_by_arrival_alone),
    ("the latest record is settled by time alone", check_a_record_sits_beside_the_connector_it_names, break_latest_by_time_alone),
    ("an endpoint record supersedes one of another state", check_a_record_sits_beside_the_connector_it_names, break_an_endpoint_record_supersedes_another_state),
    ("probe units are merged into one record", check_a_record_sits_beside_the_connector_it_names, break_probe_units_merged),
    ("danger order replaced by the alphabet", check_rows_are_sorted_by_danger, break_danger_order_is_the_alphabet),
    ("a row ranks by its latest endpoint record", check_rows_are_sorted_by_danger, break_a_row_ranks_by_its_latest_record),
    ("a record dated after now is read", check_a_record_that_records_no_observed_state_is_set_aside, break_every_record_reads),
    ("a probe unit the model does not name is read", check_a_record_that_records_no_observed_state_is_set_aside, break_an_unnamed_probe_unit_reads),
    ("a state the model does not name is read", check_a_record_that_records_no_observed_state_is_set_aside, break_an_unnamed_state_reads),
    ("a record with no readable time is read", check_a_record_that_records_no_observed_state_is_set_aside, break_an_unreadable_time_reads),
    ("a set-aside event is not said on its connector's row", check_a_record_that_records_no_observed_state_is_set_aside, break_a_set_aside_event_is_not_said_on_its_row),
    ("a record dated now is set aside", check_a_record_dated_at_the_reads_instant_is_read, break_a_record_dated_now_is_set_aside),
    ("one sentence for both empties", check_an_empty_list_apart_says_which_empty_it_is, break_one_sentence_for_both_empties),
    ("every environment reads as LOCAL", check_another_environment_is_not_said_in_locals_terms, break_every_environment_reads_as_local),
    ("the board reads every case", check_board_reads_one_case_and_says_so, break_board_reads_every_case),
    ("the board's route takes a query key", check_board_reads_one_case_and_says_so, break_board_route_takes_a_query_key),
    ("the board opens the case for writing", check_board_is_read_through_a_connection_that_cannot_write, break_board_opens_the_case_for_writing),
    ("a canary's input is printed", check_no_canary_input_is_shown, break_canary_inputs_printed),
    ("an unreadable manifest is skipped", check_an_unreadable_manifest_is_listed, break_unreadable_manifest_skipped),
    ("an unreadable manifest's folder is not carried", check_an_unreadable_manifest_is_listed, break_an_unreadable_folder_is_not_carried),
    ("only bad YAML is unreadable", check_an_unreadable_manifest_is_listed, break_only_bad_yaml_is_unreadable),
    ("a missing id is printed as a value", check_a_missing_declaration_is_said, break_a_missing_id_printed_as_a_value),
    ("an undeclared capability gets a capability line", check_a_missing_declaration_is_said, break_an_undeclared_capability_gets_a_line),
    ("a number is printed for a version declared as one", check_a_missing_declaration_is_said, break_a_number_printed_for_a_version),
    ("one canary is said as several", check_a_missing_declaration_is_said, break_one_canary_said_as_several),
    ("the halt names no case, time or check", check_halt_states_its_evidence_and_limit, break_halt_names_no_evidence),
    ("the case list carries no halt", check_halt_states_its_evidence_and_limit, break_case_list_carries_no_halt),
    ("the halt read needs an attached case", check_halt_states_its_evidence_and_limit, break_halt_read_needs_an_attached_case),
    ("LOCAL's sentence printed in every environment", check_halt_states_its_evidence_and_limit, break_local_sentence_in_every_environment),
    ("the halt claims an enforcement outside LOCAL", check_halt_states_its_evidence_and_limit, break_the_halt_claims_enforcement_outside_local),
    ("the halt lit with no failed shred", check_halt_states_its_evidence_and_limit, break_halt_always_lit),
    ("a route writes the RT-11 line for LOCAL whatever the application says", check_the_routes_answer_for_the_applications_environment, break_local_sentence_in_every_environment),
    ("the COLLECTION route answers as LOCAL whatever the application says", check_the_routes_answer_for_the_applications_environment, break_the_collection_route_answers_as_local),
    ("only the first failed shred is said", check_halt_counts_every_failed_shred, break_only_the_first_failed_shred_is_said),
    ("an unreadable payload reads as no halt", check_halt_counts_every_failed_shred, break_unreadable_payload_reads_as_no_halt),
    ("a payload with no halt flag reads as no halt", check_halt_counts_every_failed_shred, break_a_payload_with_no_flag_reads_as_no_halt),
    ("a shred that says it does not halt is counted", check_halt_counts_every_failed_shred, break_a_shred_that_does_not_halt_is_counted),
    ("COLLECTION is not a view the server serves", check_collection_view_is_wired, break_collection_not_a_served_view),
    ("key 5 is not bound", check_collection_view_is_wired, break_key_five_unbound),
    ("the case list never fills the banner", check_collection_view_is_wired, break_case_list_never_fills_the_banner),
    ("the banner is never hidden", check_collection_view_is_wired, break_banner_never_hidden),
    ("the view's export is renamed", check_collection_view_is_wired, break_view_export_renamed),
    ("the workspace store refuses the view", check_collection_view_is_wired, break_workspace_refuses_the_view),
    ("the view paints red by its own rule", check_view_prints_the_servers_lines_and_flags, break_view_paints_from_its_own_rule),
    ("the view reorders the rows", check_view_prints_the_servers_lines_and_flags, break_view_reorders_the_rows),
    ("the view drops the list apart", check_view_prints_the_servers_lines_and_flags, break_view_drops_the_list_apart),
]
