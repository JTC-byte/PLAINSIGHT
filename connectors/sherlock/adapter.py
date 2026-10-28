"""Sherlock 0.16.1 adapter: parse, emit, invoke.

DRAFT, written by an agent at Step 12 on 2026-10-28, UNRATIFIED. Three layers,
each usable without the next:

  parse(csv_text, stdout_text, exit_code)
      Reads one run's --csv --print-all export and its stdout. Returns the
      items, one per probed site, each with an outcome from the design's enum
      (hit, miss, error, throttled, ambiguous) and the run's adapter state from
      the fixed enum (ok, empty, throttled, auth_failed, blocked, malformed,
      error). It runs no process and opens no network connection; it reads
      site_facts.json when facts is not passed.
  emit(parsed, run_context)
      Returns PSE events: PROBE_EVENT RUN_START, one ITEM per probed site,
      RUN_END, and one EXTRACT_EVENT CLAIM per item whose outcome is hit. Pure.
  invoke(decision, inputs)
      The live path. It refuses unless `decision` is a runner.subject_guard
      Decision whose `permits` is True for this connector and this selector
      type, and only then builds argv from the manifest's command_template and
      runs the Docker image. Nothing in this repository calls it with a permit:
      the guard refuses every request while SS-14 item 6's artifacts carry no
      dated row, and every test replaces subprocess.run before calling it.

THE CSV IS THE RECORD AND STDOUT IS THE CROSS-CHECK. --print-all is the only
switch that widens the CSV past hits, so a run without it would export Claimed
rows alone and every negative would vanish from the file. Stdout carries a
variable preamble (the unsuppressible update check, and the exclusions warning
when that fetch failed) and the Unknown context string, which no export keeps.
The parser skips the preamble, reads the context, and refuses the run as
malformed when the two disagree on the site set, a site's status, the number of
result lines, or the Claimed count, or when the CSV names one site twice, which
Sherlock 0.16.1 never writes.

WHAT AN OUTCOME MEANS (reading SH-R6, connectors/sherlock/README.md):

  Claimed, 2xx, site not on the measured exclusion list  hit, and one claim
  Claimed, 2xx, site on that list                         ambiguous (SH-R7)
  Claimed, 2xx, site whose url has no username slot       ambiguous (SH-R15)
  Claimed, 2xx, site whose name yields no platform token  ambiguous (SH-R18)
  Claimed, 429                                            throttled (the Steam shape)
  Claimed, any other status                               ambiguous
  Available, 200, 404, 410, a 3xx, or the site's errorCode  miss, site_rule_reports_available
  Available, 429                                          throttled
  Available, any other status (403, 503, 999 ...)         ambiguous
  Illegal                                                 miss, username_format_illegal_for_site
  WAF                                                     error, no negative class
  Unknown                                                 error, no negative class

A WAF or Unknown row is a request that returned no answer, so it carries no
negative_class: spec/layer-model.yaml draws that field only for an item whose
outcome is miss. The parsed item keeps Sherlock's status in `exists` and the
Unknown context string in `unknown_context`, which is where the two are told
apart. A run whose every row is Unknown is adapter state error, because no site
answered and nothing blocked the probe.

Only a hit becomes a claim. A throttled or ambiguous row is an item an analyst
can see and never a claim, because a rate-limit page scored Claimed is not an
observation that the string is registered.

WHAT THE WIRE CANNOT CARRY. A site's errorType strategy, its verb and the host
urlProbe sends the username to are the quality and exposure facts of an item,
read from site_facts.json at the pinned commit. pse-event-0.1's ITEM payload
admits none of them (additionalProperties is false), so they live on the parsed
item and in site_facts.json, keyed by the site the ITEM locator names, and the
locator plus the case's pinned connector version recovers them (SH-R9).

THE HANDLE'S PLATFORM (reading SH-R18). A handle's registry form is
handle:<platform>/<string>, and the manifest's handle emit declares
platform_from_item (reading MF-R17 in tools/validate_manifest.py), so each
claim carries the platform of the site its ITEM locator names. The claim value
is that platform token, a slash, and the CSV's username cell. The token is
derived from the site name and nothing else: the name lower-cased, each run of
characters outside a to z and 0 to 9 replaced by one underscore, and leading and
trailing underscores removed, so Diskusjon.no gives diskusjon_no. A result that
does not match ^[a-z][a-z0-9_]*$ is no token, which at the pinned commit is the
four site names that begin with a digit. A name carrying a parenthesised
qualifier is also no token, which at the pinned commit is the five endpoint
sites of three platforms, Genius (Artists), Genius (Users), HackenProof
(Hackers), Steam Community (Group) and Steam Community (User): the qualifier
names an endpoint rather than a platform, so the plain rule would give one
platform two tokens and would record a group or artist directory as a person's
handle platform. A Claimed 2xx row on any of these nine sites is ambiguous with
no claim rather than a claim under an invented or endpoint token, until the
maintainer decides a mapping. No two sites at the pinned commit give the same
token, and the adapter tests hold these facts against site_facts.json.

VALUES. A username, a URL cell or any other cell is never formatted into an
exception, a log line or a printed string here; a refusal names the column, the
row number or the site, which is not a selector. A placeholder in a cassette is
carried through to the claim unchanged after the platform token and its slash.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runner.subject_guard import Decision  # noqa: E402  the gate's answer, read and never built here

CONNECTOR_ID = "sherlock"
VERSION = "0.16.1"
KIND = "one_shot"
PRODUCER = "connector-sherlock"
RUNNER_PRODUCER = "runner-dispatch"
TARGET_SELECTOR_TYPE = "username_string"
CLAIM_SELECTOR_TYPE = "handle"
INPUT = "username"
MANIFEST = HERE / "manifest.yaml"
SITE_FACTS = HERE / "site_facts.json"

CSV_COLUMNS = ("username", "name", "url_main", "url_user", "exists", "http_status", "response_time_s")
STATUSES = ("Claimed", "Available", "Unknown", "Illegal", "WAF")
ADAPTER_STATES = ("ok", "empty", "throttled", "auth_failed", "blocked", "malformed", "error")
OUTCOMES = ("hit", "miss", "error", "throttled", "ambiguous")

NEG_AVAILABLE = "site_rule_reports_available"
NEG_ILLEGAL = "username_format_illegal_for_site"
#: The manifest's distinguishable_negatives. A WAF or Unknown row is an error
#: item and carries none of them.
NEGATIVE_CLASSES = (NEG_AVAILABLE, NEG_ILLEGAL)

#: The context strings get_response() can attach to an Unknown row (the audit,
#: section A1.7). Stdout is the only place they appear.
UNKNOWN_CONTEXTS = ("Proxy Error", "Error Connecting", "Timeout Error", "Encoding Error",
                    "Unknown Error", "General Unknown Error")

STDOUT_TEXT = {
    "Not Found!": "Available",
    "Illegal Username Format For This Site!": "Illegal",
    "Blocked by bot detection (proxy may help)": "WAF",
}
CHECKING_RE = re.compile(r"^\[\*\] Checking username (.*) on:$")
RESULT_RE = re.compile(r"^\[([+-])\] (?:\[\d+ms\] )?(.+?): (.*)$")
COMPLETED_RE = re.compile(r"^\[\*\] Search completed with (\d+) results$")
PLACEHOLDER_RE = re.compile(r"^<[^<>]+>$")
#: The manifest schema's platform token pattern, which a claim's platform must match (SH-R18).
PLATFORM_TOKEN_RE = re.compile(r"^[a-z][a-z0-9_]*$")
_TOKEN_SEPARATOR_RE = re.compile(r"[^a-z0-9]+")

#: Code a missing or empty required input refuses under. spec/layer-model.yaml
#: declares no code for an adapter refusing its input; this is the nearest
#: declared one, the reading tools/validate_manifest.py records as MF-R10.
CODE_INPUT_MISSING = "PAYLOAD_FIELD_MISSING"
#: Code a capture whose username differs from the input refuses under: the run
#: would carry claims about a string the gate never evaluated (SS-5, SS-6).
CODE_INPUT_DISAGREES = "SUBJECT_NOT_AUTHORIZED"


class AdapterRefusal(Exception):
    """The adapter declines to turn this input into events. Never carries a value."""

    def __init__(self, code: str, adapter_state: str, what: str, moves: str, input_field: str | None = None):
        super().__init__(f"REFUSED {code}: {what}. moves: {moves}")
        self.code, self.adapter_state, self.what, self.moves = code, adapter_state, what, moves
        #: The input whose check refused, by name, or None when no input did.
        self.input_field = input_field


class InvokeRefused(AdapterRefusal):
    """invoke() declined to run anything. No process was started."""


# ---------------------------------------------------------------------------
# site facts
# ---------------------------------------------------------------------------


def load_site_facts(path: Path = SITE_FACTS) -> dict:
    """site_facts.json: per-site errorType, verb, errorCode and probe host at the pinned commit."""
    doc = json.loads(path.read_text(encoding="utf-8"))
    return {"sites": dict(doc["sites"]), "exclusions": frozenset(doc["fp_exclusions_measured"]["names"]),
            "slotless": frozenset(doc["url_without_username_slot"]["names"])}


# ---------------------------------------------------------------------------
# parse
# ---------------------------------------------------------------------------


def platform_token(site: str) -> str | None:
    """The site's platform token by SH-R18, or None when the name yields none.

    Derived from the site name and nothing else: lower-cased, each run of
    characters outside a-z and 0-9 replaced by one underscore, and the edges
    stripped of underscores. A result outside ^[a-z][a-z0-9_]*$ is None, and so
    is a name carrying a parenthesised qualifier, which names an endpoint of a
    platform rather than the platform. The caller holds that site's Claimed row
    as ambiguous rather than inventing a token for it.
    """
    if "(" in site or ")" in site:
        return None
    token = _TOKEN_SEPARATOR_RE.sub("_", site.lower()).strip("_")
    return token if PLATFORM_TOKEN_RE.match(token) else None


def _status(cell: str):
    """int, '?' when the request raised, or None when empty (Illegal rows)."""
    if cell == "":
        return None
    if cell == "?":
        return "?"
    if cell.isdigit():
        return int(cell)
    raise ValueError("http_status")


def classify(exists: str, status, fact: dict | None, excluded: bool,
             slotless: bool = False, untokened: bool = False) -> tuple[str, str | None]:
    """(outcome, negative_class) for one row. The table is in the module docstring."""
    is_int = isinstance(status, int)
    if exists == "Claimed":
        if is_int and 200 <= status < 300:
            return ("ambiguous", None) if excluded or slotless or untokened else ("hit", None)
        if status == 429:
            return "throttled", None
        return "ambiguous", None
    if exists == "Available":
        if status == 429:
            return "throttled", None
        own_code = (fact or {}).get("error_code")
        if is_int and (status in (200, 404, 410) or 300 <= status < 400 or status == own_code):
            return "miss", NEG_AVAILABLE
        return "ambiguous", None
    if exists == "Illegal":
        return "miss", NEG_ILLEGAL
    # WAF and Unknown: the request returned no answer, so no negative class.
    return "error", None


def _read_stdout(stdout_text: str) -> dict:
    """Preamble, per-site status, Unknown context, and the Claimed count. Never a value."""
    out = {"checking": False, "preamble_lines": 0, "update_check": "absent", "exclusions_unavailable": False,
           "sites": {}, "context": {}, "completed": None, "unread_lines": 0, "result_lines": 0}
    lines = [ln[:-1] if ln.endswith("\r") else ln for ln in (stdout_text or "").split("\n")]
    body = False
    for ln in lines:
        if not body:
            if CHECKING_RE.match(ln):
                out["checking"] = body = True
                continue
            if ln.strip() == "":
                continue
            out["preamble_lines"] += 1
            if ln.startswith("Update available!"):
                out["update_check"] = "newer_version_reported"
            elif ln.startswith("A problem occurred while checking for an update"):
                out["update_check"] = "failed"
            elif ln.startswith("Warning: Could not load exclusions"):
                out["exclusions_unavailable"] = True
            continue
        if ln.strip() == "":
            continue
        m = COMPLETED_RE.match(ln)
        if m:
            out["completed"] = int(m.group(1))
            continue
        m = RESULT_RE.match(ln)
        if not m:
            out["unread_lines"] += 1
            continue
        marker, site, text = m.groups()
        out["result_lines"] += 1
        if marker == "+":
            out["sites"][site] = "Claimed"
            continue
        status = STDOUT_TEXT.get(text.rstrip())
        if status is None:
            status = "Unknown"
            ctx = text.rstrip()
            out["context"][site] = ctx if ctx in UNKNOWN_CONTEXTS else "unlisted"
        out["sites"][site] = status
    return out


def _malformed(problems: list, exit_code: int, so: dict | None, digest: str | None) -> dict:
    return {"adapter_state": "malformed", "exit_code": exit_code, "items": [], "username": None,
            "problems": problems, "stdout": so, "csv_sha256": digest}


def parse(csv_text: str | None, stdout_text: str | None, exit_code: int, facts: dict | None = None) -> dict:
    """One run's capture as items. See the module docstring for the outcome table."""
    facts = facts or load_site_facts()
    digest = hashlib.sha256(csv_text.encode("utf-8")).hexdigest() if csv_text is not None else None
    so = _read_stdout(stdout_text or "")
    if exit_code != 0:
        # Exit 1 is a manifest load failure, every --site name unresolved, or an
        # unhandled traceback; exit 2 is argparse. Neither carries a usable sweep.
        return {"adapter_state": "error", "exit_code": exit_code, "items": [], "username": None,
                "problems": [f"Sherlock exited {exit_code}, so no row of this run is read"],
                "stdout": so, "csv_sha256": digest}
    if csv_text is None:
        return _malformed(["exit 0 and no CSV export, so the run left no record of what it probed"],
                          exit_code, so, digest)
    try:
        rows = list(csv.reader(io.StringIO(csv_text, newline="")))
    except csv.Error:
        return _malformed(["the CSV export is not RFC 4180 text"], exit_code, so, digest)
    if not rows or tuple(rows[0]) != CSV_COLUMNS:
        return _malformed(["the CSV header is not Sherlock 0.16.1's seven columns"], exit_code, so, digest)
    problems: list[str] = []
    items: list[dict] = []
    users: set[str] = set()
    seen_sites: set[str] = set()
    for n, cells in enumerate(rows[1:], start=1):
        if len(cells) != len(CSV_COLUMNS):
            problems.append(f"row {n} has {len(cells)} cells, not 7")
            continue
        rec = dict(zip(CSV_COLUMNS, cells))
        site, exists = rec["name"], rec["exists"]
        if exists not in STATUSES:
            problems.append(f"row {n} carries an exists value outside Sherlock's five statuses")
            continue
        try:
            status = _status(rec["http_status"])
        except ValueError:
            problems.append(f"row {n} carries an http_status that is not an integer, ? or empty")
            continue
        if exists == "Illegal":
            if rec["url_user"] or rec["http_status"] or rec["response_time_s"]:
                problems.append(f"row {n} is Illegal and carries a URL, status or time, which an Illegal row never has")
                continue
        elif status is None:
            problems.append(f"row {n} is {exists} and carries no http_status")
            continue
        slotless = site in facts["slotless"]
        # A site whose url carries no {} slot gets that bare url as url_user on
        # every row, so the containment check cannot apply to it (SH-R15).
        if rec["url_user"] and not slotless and rec["username"] not in rec["url_user"]:
            problems.append(f"row {n} carries a url_user that does not contain its username cell")
            continue
        if site in seen_sites:
            problems.append(f"row {n} names a site an earlier row names, and Sherlock 0.16.1 writes each site once")
            continue
        seen_sites.add(site)
        users.add(rec["username"])
        fact = facts["sites"].get(site)
        excluded = site in facts["exclusions"]
        token = platform_token(site)
        outcome, negative = classify(exists, status, fact, excluded, slotless, untokened=token is None)
        items.append({
            "row": n,
            "site": site,
            "exists": exists,
            "http_status": status,
            "response_time_s": rec["response_time_s"] or None,
            "username": rec["username"],
            "outcome": outcome,
            "negative_class": negative,
            "error_type": (fact or {}).get("error_type"),
            "method": (fact or {}).get("method"),
            "probe_host": (fact or {}).get("probe_host"),
            "site_known_at_pinned_commit": fact is not None,
            "on_measured_fp_exclusion_list": excluded,
            "url_has_username_slot": not slotless,
            "platform_token": token,
            "unknown_context": so["context"].get(site) if exists == "Unknown" else None,
        })
    if len(users) > 1:
        problems.append("the CSV carries more than one username, and one run probes one")
    if not items and not problems:
        problems.append("the CSV carries no row, so no site was probed")
    if so["checking"]:
        csv_sites = {i["site"]: i["exists"] for i in items}
        if set(csv_sites) != set(so["sites"]):
            problems.append("stdout and the CSV name different site sets")
        elif any(so["sites"][s] != e for s, e in csv_sites.items()):
            problems.append("stdout and the CSV disagree on a site's status")
        if so["result_lines"] != len(items):
            problems.append("stdout prints a different number of result lines than the CSV carries rows")
        claimed = sum(1 for i in items if i["exists"] == "Claimed")
        if so["completed"] is None or so["completed"] != claimed:
            problems.append("stdout's Search completed count differs from the CSV's Claimed rows")
    else:
        problems.append("stdout carries no Checking username line, so the CSV cannot be cross-checked")
    if problems:
        return _malformed(problems, exit_code, so, digest)
    hits = sum(1 for i in items if i["outcome"] == "hit")
    misses = sum(1 for i in items if i["outcome"] == "miss")
    if hits:
        state = "ok"
    elif misses:
        state = "empty"
    elif all(i["exists"] == "Unknown" for i in items):
        # Every request raised (A1.7): an egress or connection failure, which
        # is not the platforms blocking the probe.
        state = "error"
    elif all(i["outcome"] == "throttled" for i in items):
        state = "throttled"
    else:
        state = "blocked"
    return {"adapter_state": state, "exit_code": exit_code, "items": items, "username": users.pop(),
            "problems": [], "stdout": so, "csv_sha256": digest,
            "exclusions_applied": not (so["exclusions_unavailable"]
                                       or any(i["on_measured_fp_exclusion_list"] for i in items))}


# ---------------------------------------------------------------------------
# emit
# ---------------------------------------------------------------------------


def required_input(inputs) -> str:
    """The username input, or a refusal. The refusal names the input, never its value."""
    value = inputs.get(INPUT) if isinstance(inputs, dict) else None
    if not isinstance(value, str) or not value.strip():
        raise AdapterRefusal(
            CODE_INPUT_MISSING, "malformed",
            f"the required input {INPUT} is absent, null or empty, and Sherlock sweeps one username string",
            f"supply {INPUT} as the consumed username_string; or withdraw the run, which has nothing to probe",
            input_field=INPUT)
    return value


def _uid(seed: str, *parts) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "plainsight:connector-sherlock:" + seed + ":" + ":".join(map(str, parts))))


def _envelope(ctx: dict, eid: str, etype: str, sub: str, producer: str, payload: dict,
              parents: list, transform: str | None = None) -> dict:
    return {
        "pse_version": "pse-event-0.1",
        "derived_from": "zmeta-event-1.0",
        "case_id": ctx["case_id"],
        "event": {"event_id": eid, "event_type": etype, "event_subtype": sub, "ts": ctx["ts"]},
        "source": {"platform_id": ctx["platform_id"], "environment": "ISOLATED", "producer": producer,
                   "sw_version": ctx.get("sw_version")},
        "payload": payload,
        "lineage": {"based_on": list(parents), "transform": transform},
    }


def emit(parsed: dict, run_context: dict) -> list[dict]:
    """PSE events for one parsed run.

    run_context: case_id, decision_event_id (the COLLECT_EVENT PERMITTED the run
    names as its parent), motivated_by, inputs, manifest_hash, argv_template,
    egress_identity, platform_id, sw_version, ts, duration_ms, id_seed.
    """
    username = required_input(run_context.get("inputs"))
    if parsed.get("username") is not None and parsed["username"] != username:
        raise AdapterRefusal(
            CODE_INPUT_DISAGREES, "malformed",
            "the capture's username column differs from the input the run was dispatched with, so every "
            "claim would be about a string the gate never evaluated",
            "replay the cassette with the input it was captured for; or recapture against the input")
    ctx = run_context
    seed = str(ctx["id_seed"])
    run_id = _uid(seed, "run")
    start_id = _uid(seed, "run_start")
    events = [_envelope(ctx, start_id, "PROBE_EVENT", "RUN_START", ctx.get("runner_producer", RUNNER_PRODUCER), {
        "phase": "RUN_START",
        "run_id": run_id,
        "connector_id": CONNECTOR_ID,
        "connector_version": VERSION,
        "connector_kind": KIND,
        "credential_id": None,
        "egress": {"environment": "ISOLATED", "egress_identity": ctx["egress_identity"]},
        "argv_template": ctx["argv_template"],
        "motivated_by": ctx.get("motivated_by"),
        "target_selector_type": TARGET_SELECTOR_TYPE,
        "manifest_hash": ctx["manifest_hash"],
    }, [ctx["decision_event_id"]])]
    claims = []
    blob = parsed.get("csv_sha256") or ""
    for item in parsed["items"]:
        item_id = _uid(seed, "item", item["row"])
        payload = {
            "phase": "ITEM",
            "run_id": run_id,
            "item_id": item_id,
            "locator": f"sherlock-site:{item['site']}",
            "outcome": item["outcome"],
            "raw_ref": {"blob_sha256": blob, "raw_span": [item["row"]]},
        }
        if item["negative_class"] is not None:
            payload["negative_class"] = item["negative_class"]
        if isinstance(item["http_status"], int):
            payload["http_status_chain"] = [item["http_status"]]
        events.append(_envelope(ctx, item_id, "PROBE_EVENT", "ITEM", PRODUCER, payload, [start_id]))
        if item["outcome"] == "hit":
            token = platform_token(item["site"])
            if token is None:
                # parse() holds such a row as ambiguous; a parsed run edited by
                # hand into a hit is refused rather than given an invented token.
                raise AdapterRefusal(
                    "PAYLOAD_FIELD_MISSING", "malformed",
                    f"row {item['row']} is a hit on a site whose name yields no platform token (SH-R18), so "
                    "the handle claim would carry no platform",
                    "parse the capture with parse(), which holds that row as ambiguous; or correct the item")
            claim_id = _uid(seed, "claim", item["row"])
            claims.append(_envelope(ctx, claim_id, "EXTRACT_EVENT", "CLAIM", PRODUCER, {
                "extract_kind": "CLAIM",
                "selector_type": CLAIM_SELECTOR_TYPE,
                "value": f"{token}/{item['username']}",
                "subject_ref": None,
                "source_ref": {"item_id": item_id, "source_path": f"/rows/{item['row']}/username", "raw_span": None},
                "extractor": {"name": PRODUCER, "version": VERSION},
                "temporal": {"observed_at": ctx["ts"], "asserted_at": None, "time_provenance": "collection_time"},
                "negative_state": "present",
            }, [item_id], f"translate:{PRODUCER}@{VERSION}"))
    events.append(_envelope(ctx, _uid(seed, "run_end"), "PROBE_EVENT", "RUN_END",
                            ctx.get("runner_producer", RUNNER_PRODUCER), {
        "phase": "RUN_END",
        "run_id": run_id,
        "exit_code": parsed["exit_code"],
        "error_class": parsed["adapter_state"],
        "item_count": len(parsed["items"]),
        "duration_ms": int(ctx["duration_ms"]),
    }, [start_id]))
    return events + claims


# ---------------------------------------------------------------------------
# cassettes
# ---------------------------------------------------------------------------


def read_cassette(path: Path | None) -> dict:
    """A cassette directory as parse() arguments plus the run's duration.

    result.csv is the --csv --print-all export, stdout.txt and stderr.txt the
    streams, meta.json the exit code and duration. A cassette with no CSV is a
    run that wrote none. path None is the empty capture a refusal fixture gives.
    """
    if path is None:
        return {"parse": {"csv_text": None, "stdout_text": "", "exit_code": 0}, "duration_ms": 0}
    path = Path(path)
    meta = json.loads((path / "meta.json").read_text(encoding="utf-8"))
    csv_path = path / "result.csv"
    csv_text = csv_path.read_bytes().decode("utf-8") if csv_path.is_file() else None
    stdout = (path / "stdout.txt").read_bytes().decode("utf-8")
    return {"parse": {"csv_text": csv_text, "stdout_text": stdout, "exit_code": int(meta["exit_code"])},
            "duration_ms": int(meta["duration_ms"])}


def cassette_values(path: Path) -> list[tuple[str, str]]:
    """Every selector-bearing cell a cassette holds, as (where, value), for the
    harness's placeholder rule: the CSV's username column and the name stdout
    says it checked. The caller compares; nothing here prints a value."""
    path = Path(path)
    out: list[tuple[str, str]] = []
    csv_path = path / "result.csv"
    if csv_path.is_file():
        rows = list(csv.reader(io.StringIO(csv_path.read_bytes().decode("utf-8"), newline="")))
        for n, cells in enumerate(rows[1:], start=1):
            if cells:
                out.append((f"result.csv row {n} username", cells[0]))
    for n, ln in enumerate((path / "stdout.txt").read_bytes().decode("utf-8").split("\n"), start=1):
        m = CHECKING_RE.match(ln.rstrip("\r"))
        if m:
            out.append((f"stdout.txt line {n} checking", m.group(1)))
    return out


# ---------------------------------------------------------------------------
# invoke: the live path, reached only through the gate
# ---------------------------------------------------------------------------


def command_template(path: Path = MANIFEST) -> str:
    import yaml  # PyYAML, as every validator here

    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    return doc["lineage"]["command_template"]


def check_argv_value(value: str) -> None:
    """Refuse a value Sherlock or argparse would read as something other than one
    username, or that would name a path other than this run's own capture.
    Names the rule, never the value.

    This is the interim shape gate at the one argv builder in the tree. SS-19
    refuses a value that does not match its registered matcher at argv
    construction, and shape.username.v1 carries no grammar in
    ontology/selectors.yaml, so this list stands in for it (reading SH-R16).
    """
    rules = (
        (PLACEHOLDER_RE.match(value) is not None, "it is an unresolved placeholder"),
        (value.startswith("-"), "it starts with a hyphen, which argparse reads as a flag"),
        ("{" in value or "}" in value, "it carries a brace, and Sherlock expands {?} into three sweeps"),
        (any(c.isspace() or not c.isprintable() for c in value), "it carries whitespace or a control character"),
        (len(value) > 256, "it is longer than 256 characters"),
        ("/" in value or "\\" in value,
         "it carries a path separator, and Sherlock names its CSV export after the username"),
        (":" in value, "it carries a colon, which a Windows path reads as a drive or a stream"),
        (value in (".", ".."), "it is a dot path segment, which names a directory rather than a file"),
    )
    for hit, why in rules:
        if hit:
            raise InvokeRefused(
                CODE_INPUT_MISSING, "malformed", f"the {INPUT} input is refused at argv because {why}",
                "resolve the input to the one username string the gate evaluated; or withdraw the run")


def build_argv(template: str, values: dict) -> list[str]:
    """argv from the template: each {slot} token replaced by its value, whole.
    The template carries no quoting, so a split on spaces is exact."""
    argv = []
    for token in template.split(" "):
        if not token:
            continue
        if token.startswith("{") and token.endswith("}") and token[1:-1] in values:
            argv.append(values[token[1:-1]])
        elif "{" in token or "}" in token:
            raise InvokeRefused(
                "PAYLOAD_FIELD_MISSING", "malformed",
                "the command template carries a slot that names no supplied input",
                "correct lineage.command_template in manifest.yaml; or supply the input")
        else:
            argv.append(token)
    return argv


def invoke(decision: Decision, inputs: dict, workdir: Path | None = None, timeout_s: int = 900) -> dict:
    """Run Sherlock once, behind the gate. Returns the capture for parse().

    Refuses, with no process started, unless `decision` is a runner.subject_guard
    Decision with permits True for this connector and selector type. The
    Decision carries no selector value by design, so the runner, which builds
    the Request and these inputs from one case record, owns their equality
    (reading SH-R8).
    """
    no_decision = (
        "SUBJECT_NOT_AUTHORIZED", "error",
        "invoke was given no decision from runner.subject_guard.evaluate(), so nothing has evaluated "
        "this subject",
        "call runner.subject_guard.evaluate(request) and pass the Decision it returns; or do not run")
    if decision is None or not hasattr(decision, "permits"):
        raise InvokeRefused(*no_decision)
    if not decision.permits:
        raise InvokeRefused(
            "SUBJECT_NOT_AUTHORIZED", "error",
            "the subject gate did not permit this run, so no argv is built and no process starts",
            "render decision.consequence to the analyst and stop; or clear what the decision names and "
            "evaluate again")
    # The type check sits after the permits check because
    # tools/validate_authorization.py --dispatch-paths reads any reference to
    # runner.subject_guard.Decision outside a permitted region as a forgery
    # (reading SH-R10). Before it, an object that is not the gate's Decision but
    # says permits True reaches this line, and is refused here.
    if not isinstance(decision, Decision) or decision.permits is not True:
        raise InvokeRefused(*no_decision)
    if decision.connector_id not in (CONNECTOR_ID, PRODUCER) or decision.target_selector_type != TARGET_SELECTOR_TYPE:
        raise InvokeRefused(
            "SUBJECT_NOT_AUTHORIZED", "error",
            "the permit names another connector or selector type, and a permit authorizes the dispatch it "
            "evaluated and no other (SS-5)",
            "evaluate a request for connector sherlock and selector type username_string")
    username = required_input(inputs)
    check_argv_value(username)
    argv = build_argv(command_template(), {INPUT: username})
    # The CSV the run writes is raw capture carrying the selector in its name
    # and its rows, stratum 0 under RT-1. A scratch directory this call makes
    # is removed before it returns, on every path, so the capture lives only in
    # the returned text that the runner writes inside the case boundary.
    own_dir = workdir is None
    run_dir = Path(tempfile.mkdtemp(prefix="plainsight-sherlock-")) if own_dir else Path(workdir)
    try:
        started = time.monotonic()
        proc = subprocess.run(argv, cwd=run_dir, capture_output=True, timeout=timeout_s, check=False)
        duration_ms = int((time.monotonic() - started) * 1000)
        csv_path = run_dir / "out" / "run" / f"{username}.csv"
        csv_text = csv_path.read_bytes().decode("utf-8") if csv_path.is_file() else None
    finally:
        if own_dir:
            shutil.rmtree(run_dir, ignore_errors=True)
    return {
        "parse": {
            "csv_text": csv_text,
            "stdout_text": proc.stdout.decode("utf-8", errors="replace"),
            "exit_code": proc.returncode,
        },
        "stderr_text": (proc.stderr or b"").decode("utf-8", errors="replace"),
        "duration_ms": duration_ms,
    }
