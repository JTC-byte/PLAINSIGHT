"""COLLECTION (key 5): the connectors this checkout carries, and the health records one case holds.

The board joins two sources and labels each row by its source (the maintainer's
ruling 1C of 2026-11-12, docs/PLAINSIGHT-design.md amendment 9.25):

- the manifests under connectors/, one row per connector this checkout carries;
- the SYSTEM_EVENT CONNECTOR_HEALTH events of one case. The scope of the read
  is its one case argument (ruling 2A), and the board says its scope in words.

Three readings the rulings leave to the build, each recorded in amendment 9.25
for the maintainer to confirm or reverse.

Reading APP-R35, the present state. No row states a present health state other
than UNVERIFIED, the fifth state of design section 7.1: "state genuinely
unknown". On LOCAL no canary runs, because LOCAL executes no connector
(doctrine/EGRESS.md EG-1), so nothing on this machine can produce a present
state. In ISOLATED a recorded state would be the present one only inside a
freshness window, and no manifest declares one
(schema/connector-manifest.schema.json has no field for it), so this module
picks no number (design section 5.1).

Reading APP-R36, what a record is and which records a row shows. A recorded
state is printed as a dated record: the state its producer recorded, when, by
which producer and canary, the design's own definition of that state quoted as
the design's, and why it is not the present state. The board vouches for no
recorded state, so every record carries the flag the view paints red. A record
of the connector as a whole is one stream: the latest, by time and then by
arrival, supersedes the earlier ones, which are counted and not listed. An
endpoint or subscription record names no endpoint, because the payload carries
none, so two of them may concern two endpoints and neither supersedes the
other: they are grouped by the state they record, the latest of each state is
shown, and the row says how many records that state has. A record of a
dangerous state is therefore never hidden behind a later record of a safer one.
A record that names no readable time, or a time after now, or no connector,
probe unit or state the model names, records no state that has been observed,
so it is set aside and counted, as reads.sweep_line does for a heartbeat, and
the row of the connector it names says so. A record's reason is printed when it
carries one. A record whose connector no manifest folder here carries is listed
apart, as recorded in this case for a connector this checkout does not carry.

Reading APP-R37, what a manifest row prints. A row prints what the file
declares as text: id, version, capability, kind, probe unit, canary cadence,
the canaries' names and the declared class of their target. YAML reads a bare
number, a date or a list as another type, and printing that would print a
value the file does not hold (1.10 reads as 1.1), so such a value is said to be
not declared as text. A row never prints a canary's input, because a canary
declaration carries its target (doctrine/RETENTION.md RT-15). The manifest gate
makes a connector's id the name of its folder, so a manifest that cannot be
read, or declares no id, is listed under its folder's name and holds the
records that name it; it is never skipped, because a connector missing from a
health board reads as a connector with nothing wrong. This module does not
grade a manifest: tools/validate_manifest.py does, and a row is no finding
that its manifest is valid.

Nothing here writes, and nothing here executes a connector or a canary. The
manifests are read from the working tree on every request.
"""

from __future__ import annotations

import datetime as dt

import yaml

from app import config
from app.model import reads

CONNECTORS = config.REPO_ROOT / "connectors"

#: Design section 7.4: the board is sorted by danger, so SUSPECT outranks DOWN.
DANGER = ("SUSPECT", "DOWN", "DEGRADED", "UNVERIFIED", "HEALTHY")

#: Design section 7.1's own words for each state, copied exactly. A record
#: prints the definition as the design's. It is not this module's finding about
#: the connector: the payload carries a state, a canary id and nothing of yield.
DEFINED = {
    "HEALTHY": "canaries pass, yield within band, fresh",
    "DEGRADED": "works but impaired: throttled, partial endpoints, latency 3× p95",
    "SUSPECT": "returns 200 OK and zero/wrong results. NO ERROR.",
    "DOWN": "hard failure: auth, network, non-zero exit, schema violation",
    "UNVERIFIED": "no canary in the freshness window; state genuinely unknown",
}

#: What design section 7.4 tells the analyst to do about a state, where it says so.
ACT_ON = {"SUSPECT": "verify before citing what it produced then (design section 7.4)"}

PROBE_UNITS = ("connector", "endpoint", "subscription")

#: The manifest keys a row prints, each a declaration and none a canary input.
DECLARED = ("version", "capability", "kind", "probe_unit", "cadence", "canary_subject_class")

NOT_DECLARED = "not declared"
NOT_TEXT = "not declared as text"


def _text(value) -> str:
    """A manifest value as the text the file declares: the string itself; NOT_DECLARED for a key that is absent
    or empty; NOT_TEXT for any other type, which YAML made of something the file does not spell that way."""
    if value is None or value == "":
        return NOT_DECLARED
    return value if isinstance(value, str) else NOT_TEXT


def declared(value: str) -> bool:
    return value not in (NOT_DECLARED, NOT_TEXT)


def read_manifest(path) -> dict | None:
    """The manifest at `path` as a mapping, or None when it cannot be read as one."""
    try:
        manifest = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        return None
    return manifest if isinstance(manifest, dict) else None


def canary_names(health: dict) -> list[str] | None:
    """The names of the canaries a health block declares, and nothing a canary holds. None when the block
    declares canaries as something other than a mapping."""
    canaries = health.get("canaries")
    if canaries is None:
        return []
    return sorted(str(name) for name in canaries) if isinstance(canaries, dict) else None


def declared_id(manifest: dict, folder: str) -> tuple[str, bool]:
    """(the id a row is listed under, whether the manifest declares it as text). A manifest that declares no id
    is listed under its folder's name, which the manifest gate makes the connector's id, and its row says so."""
    value = manifest.get("id")
    return (value, True) if isinstance(value, str) and value else (folder, False)


def declarations() -> list[dict]:
    """One declaration per manifest under connectors/, in path order. A manifest that cannot be read is
    listed with readable False under its folder's name."""
    out = []
    for path in sorted(CONNECTORS.glob("*/manifest.yaml")):
        folder = path.parent.name
        source = f"connectors/{folder}/manifest.yaml"
        manifest = read_manifest(path)
        if manifest is None:
            out.append({"readable": False, "connector_id": folder, "folder": folder, "source": source})
            continue
        block = manifest.get("health")
        health = block if isinstance(block, dict) else {}
        connector_id, id_declared = declared_id(manifest, folder)
        row = {
            "readable": True,
            "connector_id": connector_id,
            "id_declared": id_declared,
            "folder": folder,
            "source": source,
            "health_is_a_mapping": block is None or isinstance(block, dict),
            "canaries": canary_names(health),
        }
        for key in DECLARED:
            row[key] = _text(health.get(key) if key in ("probe_unit", "cadence") else manifest.get(key))
        out.append(row)
    return out


def health_events(conn, case_id: str) -> list[dict]:
    """The CONNECTOR_HEALTH events of one case, in arrival order. The case is the read's scope (ruling 2A)."""
    return reads.events(conn, case_id, "SYSTEM_EVENT", ("CONNECTOR_HEALTH",))


def named_connector(e: dict) -> str | None:
    """The connector a health event names, or None when its payload names none as text."""
    p = e.get("payload")
    value = p.get("connector_id") if isinstance(p, dict) else None
    return value if isinstance(value, str) and value else None


def readable(e: dict, at: dt.datetime) -> bool:
    """Whether a health event records a state that has been observed: a connector, a probe unit and a state
    the model names, at an instant that is not after `at`."""
    if named_connector(e) is None:
        return False
    unit, state = e["payload"].get("probe_unit"), e["payload"].get("state")
    if not isinstance(unit, str) or unit not in PROBE_UNITS:
        return False
    if not isinstance(state, str) or state not in DEFINED:
        return False
    ts = reads.instant(e.get("ts"))
    return ts is not None and ts <= at


def record_order(found: tuple) -> tuple:
    """What orders two records of one group: the time each names, then its arrival."""
    return found[:2]


def group_key(p: dict) -> tuple:
    """Which records one shown record stands for. A record of the connector as a whole is one stream. An
    endpoint or subscription record names no endpoint, so a later one may concern another endpoint and does
    not supersede an earlier one of another state: those are grouped by state as well."""
    if p["probe_unit"] == "connector":
        return (p["connector_id"], p["probe_unit"])
    return (p["connector_id"], p["probe_unit"], p["state"])


def latest_records(events: list[dict], at: dt.datetime) -> tuple[dict, list[dict]]:
    """({group: (the latest record of the group, how many earlier ones it stands for)}, the events set aside).
    The latest is the latest by time, then by arrival, as reads.latest_run picks."""
    groups: dict[tuple, list[tuple]] = {}
    aside = []
    for e in events:
        if not readable(e, at):
            aside.append(e)
            continue
        groups.setdefault(group_key(e["payload"]), []).append((reads.instant(e["ts"]), reads.arrival(e), e))
    latest = {key: (max(found, key=record_order)[2], len(found) - 1) for key, found in groups.items()}
    return latest, aside


def since_line(environment: str) -> str:
    """Why a recorded state is not the present one, in the environment's own terms."""
    if environment == "LOCAL":
        return "not the present state: no canary runs from this machine, because LOCAL executes no connector (EG-1)"
    return "not the present state: no freshness window is declared, so whether it still holds is unknown"


def present_state(environment: str) -> dict:
    """The present state of a connector this checkout carries: UNVERIFIED, rendered as its consequence."""
    if environment == "LOCAL":
        text = ("UNVERIFIED, no canary runs from this machine, because LOCAL executes no connector (EG-1): "
                "this connector's state is unknown here")
    else:
        text = ("UNVERIFIED, no freshness window is declared for a recorded state, so none is read as the "
                "present one: this connector's state is unknown here")
    return {"text": text, "vouch": True}


def stands_for(p: dict, earlier: int) -> str | None:
    """What a shown record says of the records of its group that are not listed, or None when it has none."""
    if not earlier:
        return None
    if p["probe_unit"] == "connector":
        counted = "1 earlier record" if earlier == 1 else f"{earlier} earlier records"
        return f"{counted} of this connector as a whole in this case, superseded and not listed"
    unit = p["probe_unit"]
    return (f"the latest of {earlier + 1} records of this state for this connector's {unit}s in this case; each "
            f"may concern another {unit}, and the earlier ones are not listed")


def record_text(e: dict, earlier: int, environment: str) -> str:
    """One health record as a dated record: the state its producer recorded, when, by which producer and
    canary, the design's definition of that state, and why it is not the present state."""
    p = e["payload"]
    state = p["state"]
    canary = f", canary {p['canary_id']}" if isinstance(p.get("canary_id"), str) and p["canary_id"] else ", no canary named"
    parts = [f"{state} recorded {e['ts']} by {e['producer']}{canary}: design section 7.1 defines {state} as "
             f"\"{DEFINED[state]}\""]
    if state in ACT_ON:
        parts.append(ACT_ON[state])
    if isinstance(p.get("reason"), str) and p["reason"]:
        parts.append(f"recorded reason: {p['reason']}")
    if p["probe_unit"] != "connector":
        parts.append(f"recorded for one {p['probe_unit']}, which the record does not name")
    parts.append(since_line(environment))
    others = stands_for(p, earlier)
    if others:
        parts.append(others)
    return " · ".join(parts)


def record_row(e: dict, earlier: int, environment: str) -> dict:
    """A record as the board serves it. vouch is True for every record: the board vouches for no recorded
    state, and the view paints the flag (reading APP-R36). rank is this module's sort key and is not served."""
    p = e["payload"]
    return {
        "event_id": e["event_id"],
        "connector_id": p["connector_id"],
        "probe_unit": p["probe_unit"],
        "text": record_text(e, earlier, environment),
        "vouch": True,
        "rank": DANGER.index(p["state"]),
    }


def capability_lines(connectors: list[dict]) -> list[dict]:
    """Design section 7.4's line, per declared capability. Every member's present state is UNVERIFIED in this
    build (reading APP-R35), so no capability has a healthy member and the line prints for each one."""
    members: dict[str, list[dict]] = {}
    for c in connectors:
        if c["readable"] and declared(c["capability"]):
            members.setdefault(c["capability"], []).append(c)
    out = []
    for capability, rows in sorted(members.items()):
        names = ", ".join(sorted(r["connector_id"] for r in rows))
        count = "its one member is" if len(rows) == 1 else f"its {len(rows)} members are"
        out.append({
            "capability": capability,
            "text": f"CAPABILITY {capability} HAS NO HEALTHY MEMBER: {count} UNVERIFIED here ({names})",
            "vouch": True,
        })
    return out


def _count(n: int, one: str, many: str) -> str:
    return f"{n} {one if n == 1 else many}"


def title(d: dict) -> str:
    """A connector row's first line: id, version, capability and kind, each named when the file does not
    declare it as text."""
    version = f" {d['version']}" if declared(d["version"]) else f", version {d['version']}"
    capability = d["capability"] if declared(d["capability"]) else f"capability {d['capability']}"
    kind = d["kind"] if declared(d["kind"]) else f"kind {d['kind']}"
    return f"{d['connector_id']}{version} · {capability} · {kind}"


def canary_line(d: dict) -> str:
    """The canaries a manifest declares, by name, and the declared class of their target."""
    names = d["canaries"]
    if names is None:
        canaries = "canaries not declared as a mapping"
    elif not names:
        canaries = "no canary declared"
    elif len(names) == 1:
        canaries = f"canary {names[0]}"
    else:
        canaries = f"canaries {', '.join(names[:-1])} and {names[-1]}"
    target = (f"against a target declared {d['canary_subject_class']}" if declared(d["canary_subject_class"])
              else f"with a target class {d['canary_subject_class']}")
    return f"{canaries}, {target}; the manifest's canary inputs are never shown here (RT-15)"


def declared_lines(d: dict) -> list[str]:
    """What a readable manifest declares about its health checks, and what it does not."""
    lines = []
    if not d["id_declared"]:
        lines.append("the manifest declares no id as text, so this row is listed under its folder's name")
    elif d["connector_id"] != d["folder"]:
        lines.append(f"the manifest declares the id {d['connector_id']} in the folder {d['folder']}, and the "
                     "manifest gate refuses an id that is not its folder's name")
    if not d["health_is_a_mapping"]:
        lines.append("the manifest's health block is not a mapping, so nothing in it is read")
    lines.append(f"declared by {d['source']}: probe unit {d['probe_unit']}, canary cadence {d['cadence']}")
    lines.append(canary_line(d))
    return lines


def records_lines(records: list[dict], aside: int, what: str = "this connector") -> list[str]:
    """What a row says of the case's health events that name it: how many events that name it were set aside,
    and how many records it shows."""
    lines = []
    if aside == 1:
        lines.append(f"1 health event that names {what} is set aside and not read as a record")
    elif aside:
        lines.append(f"{aside} health events that name {what} are set aside and not read as records")
    if not records:
        lines.append(f"no health record read in this case names {what}")
    else:
        lines.append(f"{_count(len(records), 'health record', 'health records')} shown from this case, each a dated "
                     "record and not the present state:")
    return lines


def rows_for(connector_id: str, latest: dict, environment: str) -> list[dict]:
    """The records a connector's row shows: the latest of each group that names it, sorted by danger."""
    return sorted(
        (record_row(e, earlier, environment) for key, (e, earlier) in latest.items() if key[0] == connector_id),
        key=lambda r: (r["rank"], r["probe_unit"]),
    )


def carried_ids(found: list[dict]) -> set:
    """The ids this checkout carries a connector under: one per manifest folder, readable or not. A manifest
    that cannot be read is still a connector the checkout carries, under its folder's name."""
    return {d["connector_id"] for d in found}


def listed_apart(latest: dict, carried: set, environment: str) -> list[dict]:
    """The records that name a connector no manifest folder here carries, sorted by danger."""
    return sorted(
        (record_row(e, earlier, environment) for key, (e, earlier) in latest.items() if key[0] not in carried),
        key=lambda r: (r["rank"], r["connector_id"], r["probe_unit"]),
    )


def board(conn, case_id: str, environment: str, at: dt.datetime | None = None) -> dict:
    """The COLLECTION board for one case: the checkout's connectors, each UNVERIFIED, with the case's health
    records beside the connector they name, and the records that name no connector carried here."""
    events = health_events(conn, case_id)
    latest, aside = latest_records(events, at or reads.now())
    aside_names = [named_connector(e) for e in aside]
    present = present_state(environment)
    found = declarations()
    carried = carried_ids(found)
    connectors = []
    for d in found:
        records = rows_for(d["connector_id"], latest, environment)
        rank = min([r["rank"] for r in records] + [DANGER.index("UNVERIFIED")])
        set_aside_here = aside_names.count(d["connector_id"])
        if not d["readable"]:
            connectors.append({
                "readable": False,
                "connector_id": d["connector_id"],
                "title": f"{d['connector_id']} · {d['source']}",
                "state": (f"{d['source']} could not be read as a manifest: this checkout carries a connector "
                          "the board cannot describe, and its state is unknown here"),
                "state_vouch": True,
                "lines": records_lines(records, set_aside_here, "this folder's name"),
                "records": records,
                "rank": rank,
            })
            continue
        connectors.append({
            "readable": True,
            "connector_id": d["connector_id"],
            "capability": d["capability"],
            "title": title(d),
            "state": present["text"],
            "state_vouch": present["vouch"],
            "lines": declared_lines(d) + records_lines(records, set_aside_here),
            "records": records,
            "rank": rank,
        })
    connectors.sort(key=lambda c: (c["rank"], c["connector_id"]))
    unmatched = listed_apart(latest, carried, environment)
    capabilities = capability_lines(connectors)
    unread = sum(1 for c in connectors if not c["readable"])
    counted = _count(len(connectors), "connector in this checkout", "connectors in this checkout")
    if unread == 1:
        counted += ", 1 with a manifest that cannot be read"
    elif unread:
        counted += f", {unread} with manifests that cannot be read"
    out = {
        "case_id": case_id,
        "summary": " · ".join([
            counted,
            _count(len({c["capability"] for c in connectors if c["readable"] and declared(c["capability"])}),
                   "capability declared", "capabilities declared"),
            _count(len(events), "health event in this case's log", "health events in this case's log"),
        ]),
        "scope": (f"scope: case {case_id[:8]} only. A health record is read from this case's log, and a record "
                  "in another case is not read here"),
        "capabilities": capabilities,
        "connectors": connectors,
        "connectors_empty": "this checkout carries no connector manifest",
        "unmatched_heading": "RECORDED IN THIS CASE FOR A CONNECTOR THIS CHECKOUT DOES NOT CARRY",
        "unmatched": unmatched,
        "unmatched_empty": ("no health record is read from this case's log" if not latest else
                            "every health record read in this case names a connector this checkout carries"),
        "set_aside": None,
    }
    if aside:
        subject = ("1 health event in this case carries" if len(aside) == 1
                   else f"{len(aside)} health events in this case carry")
        out["set_aside"] = (
            f"{subject} a time after now, no readable time, or no connector, probe unit or state the model "
            f"names, and {'is' if len(aside) == 1 else 'are'} not read as a record"
        )
    # The sort ranks and the readable flag are this module's own, and no row serves them.
    for row in connectors + unmatched + [rec for c in connectors for rec in c["records"]]:
        for key in ("rank", "readable"):
            row.pop(key, None)
    return out
