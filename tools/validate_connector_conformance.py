#!/usr/bin/env python3
"""Rung 4 of the conformance ladder: every connector's adapter against its own
cassettes and fixtures.

`CONFORMANCE.md` section 3 defines a connector conformance claim as DECLARE plus
five rungs, all passing, never one read alone. This tool runs DECLARE and rung 4
for each connector, grades every emitted event the way rung 2 does, and prints
the claim with every rung's state in words. It never runs a connector against a
platform: it replays recorded files, and calls `invoke()` only when the static
scan finds no dispatch site outside the gate, and then only with every process
and network callable of the standard library replaced by a recorder that
raises.

Modes:

  --all              every connectors/<id>/ directory. A directory whose name
                     starts with . or _ is not a connector and is skipped, as
                     tools/validate_manifest.py --all skips it. With zero
                     connectors it says that no connector was graded and exits 0
  --connector <id>   connectors/<id>/ alone
  --self-test        copies connectors/sherlock to a scratch directory outside
                     the repository, plants each defect named below, and asserts
                     each is refused by its own code, and that the unplanted
                     copy is clean
  --quiet            prints nothing on a pass but the claim's one-line state

THE CHECKS, in the order they run, each with its code:

  DECLARE      tools/validate_manifest.py's full mode, run in process on the
               connector's manifest. Every finding it returns is reported under
               CONFORMANCE_MANIFEST_REFUSED with the manifest code inside, and
               refuses the claim. Rung 4 still runs after a DECLARE refusal, so
               the operator reads both results, and the claim stays refused
  adapter      adapter.py loads and exports parse, emit, invoke, read_cassette,
               cassette_values and AdapterRefusal (CONFORMANCE_ADAPTER_CONTRACT)
  fixtures     every line of fixtures.jsonl linted by the same reader
               tools/validate_manifest.py uses: the fixture schema, no repeated
               key, every input a slot name or a typed token the cast carries
               (CONFORMANCE_FIXTURE_SHAPE); each fixture names this connector at
               this version (CONFORMANCE_FIXTURE_CONNECTOR_MISMATCH)
  cassettes    a fixture's cassette exists (CONFORMANCE_CASSETTE_ABSENT), and
               every selector-bearing cell the adapter says the cassette holds
               is a placeholder by the same rule (CONFORMANCE_CASSETTE_VALUE).
               The location is named and the cell never is
  replay       read_cassette, parse and emit, with the replay context below.
               An exception other than the adapter's own refusal is
               CONFORMANCE_ADAPTER_CRASHED, named by its class and never its text
  events       for an events fixture: the adapter did not refuse
               (CONFORMANCE_UNEXPECTED_REFUSAL); the count equals event_count
               exactly, zero included (CONFORMANCE_EVENT_COUNT); RUN_END's
               error_class equals adapter_state (CONFORMANCE_ADAPTER_STATE);
               every event passes tools/validate.py check_event over an Index of
               the replay context and the run, with every code it fires named
               (CONFORMANCE_EVENT_REFUSED); every claim value is a placeholder,
               or, for a key whose registry form binds a platform, a platform
               token, a slash and a placeholder (CONFORMANCE_CASSETTE_VALUE,
               readings MF-R17 and SH-R18)
  refusals     for a refusal fixture: the adapter refused
               (CONFORMANCE_REFUSAL_EXPECTED), with the declared code
               (CONFORMANCE_REFUSAL_CODE), in the declared adapter state
               (CONFORMANCE_ADAPTER_STATE), naming the input the manifest's
               health.refusal_fixtures names for that fixture id
               (CONFORMANCE_REFUSAL_INPUT). A refusal fixture with no cassette
               replays the golden cassette, so the withheld input is the only
               thing that differs from a run the adapter reads
  known neg.   the fixture whose input equals the manifest's known_negative
               canary input yields no hit item and no claim
               (CONFORMANCE_KNOWN_NEGATIVE_HIT) and at least one item in the
               canary's negative class (CONFORMANCE_KNOWN_NEGATIVE_CLASS); a
               connector with no such events fixture is refused
               (CONFORMANCE_KNOWN_NEGATIVE_ABSENT)
  known pos.   an events fixture whose input equals the manifest's
               known_positive canary input holds and yields at least
               result_count_min hit items (CONFORMANCE_KNOWN_POSITIVE_ABSENT)
  golden       an events fixture that holds replays the cassette directory that
               holds the manifest's golden_fixture; a refusal fixture on that
               cassette does not count (CONFORMANCE_GOLDEN_NOT_REPLAYED)
  vacuity      at least one events fixture exists, and at least one returned
               one event or more without refusing; an adapter that refuses every
               events fixture satisfies every refusal fixture and proves nothing
               (CONFORMANCE_VACUOUS)
  invoke       statically, tools/validate_authorization.py's dispatch scanner
               over adapter.py finds every site behind a permits check. Only
               when it does, at run time, invoke() given no decision, a REFUSED
               decision runner.subject_guard.evaluate() returned for a request
               with no record, and an object that says permits True and is not
               the gate's Decision refuses with the adapter's refusal each time
               and reaches no process or network call
               (CONFORMANCE_INVOKE_UNGUARDED). A static site outside the gate
               withholds the run-time cases, because that adapter could
               dispatch for real through a callable the stand-in does not
               cover. The run-time input is a random string made in memory and
               never written

THE ADAPTER CONTRACT this tool reads, from connectors/<id>/adapter.py:
read_cassette(path or None) returns {"parse": kwargs for parse, "duration_ms":
int}; parse(**kwargs) returns the parsed run; emit(parsed, run_context) returns
a list of PSE events or raises AdapterRefusal, whose code and adapter_state the
refusal fixtures pin and whose input_field names the input whose check refused;
cassette_values(path) lists (where, value) for every
selector-bearing cell; invoke(decision, inputs) is the live path.

THE REPLAY CONTEXT. Two events this tool writes in memory so lineage resolves
the way it would in a case: an AUTHORIZE_EVENT GRANT and the COLLECT_EVENT
PERMITTED a run names as its parent, for the manifest's connector and first
required selector type. They are not a Decision object, they are never passed to
invoke(), they permit nothing, and no adapter reads more of them than the
decision's event id.

WHAT THIS DOES NOT PROVE, stated so a green run is not read as more. A cassette
is frozen when it is written, and every cassette in this tree is hand-built in a
recorded shape rather than captured, so rung 4 proves the adapter against the
shapes its author chose. The live canaries, design section 6.5's Prove It, are
an operator act this tool never performs, and until they pass no connector is
registered for live use. Rung 1 (pytest) and rung 5 (the kernel gate) are other
commands, named in the claim it prints.

Readings, each an agent reading awaiting the operator, recorded in
connectors/sherlock/README.md as SH-R1 onward where they bind the first
connector, and here where they bind the tool:

  CC-R1  The fixture schema has no result_count or negative_class key (MF-R15),
         so the known-negative fixture is identified by its input equalling the
         manifest canary's, and its expectations are read from the canary.
  CC-R2  The brief that built this tool named the live canaries rung 5;
         CONFORMANCE.md section 3 names the kernel gate rung 5 and rank 5 wins,
         so the claim prints the kernel gate as rung 5 and the live canaries as
         a separate precondition for live use.
  CC-R3  DECLARE refusing does not stop rung 4, so a manifest held on a reading
         still shows whether its adapter replays honestly; the claim is refused
         either way.

Exit codes: 0 every graded connector holds DECLARE and rung 4, 1 a refusal, 2 an
input this tool reads could not be read: a schema, the policy pack, the
registry, the layer model, the cast draft or the pin of record.
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import datetime as _dt
import hashlib
import importlib.util
import io
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))
if str(ROOT) not in sys.path:
    sys.path.insert(1, str(ROOT))

import validate as V  # noqa: E402  rung 2's grader, the one check_event
import validate_manifest as VM  # noqa: E402  DECLARE, the fixture lint and the placeholder rule

try:
    import gate_log
except Exception:  # telemetry must never be able to break a gate
    gate_log = None

CONNECTORS = ROOT / "connectors"
GATE = "connector-conformance"
ADAPTER_API = ("parse", "emit", "invoke", "read_cassette", "cassette_values", "AdapterRefusal")

#: The replay context's fixed identities. uuid5, so they are valid PSE uuids.
_NS = uuid.uuid5(uuid.NAMESPACE_URL, "plainsight:connector-harness:replay")
CASE_ID = str(uuid.uuid5(_NS, "case"))
GRANT_ID = str(uuid.uuid5(_NS, "grant"))
DECISION_ID = str(uuid.uuid5(_NS, "decision"))
AUTH_REF = str(uuid.uuid5(_NS, "authorization"))
TS = "2026-01-15T10:06:00Z"
PLATFORM_ID = "replay-isolated"
EGRESS_IDENTITY = "replay-egress"
REPLAY_HUMAN = "analyst-replay"

CODES: dict[str, tuple[str, str]] = {
    "CONFORMANCE_MANIFEST_REFUSED": (
        "CONFORMANCE.md section 3: a claim names a manifest tools/validate_manifest.py passes in full",
        "fix the manifest line the inner code names, then rerun; or, where the refusal is held on a "
        "reading, put that reading to the operator, which is what the connector's README.md records",
    ),
    "CONFORMANCE_ADAPTER_CONTRACT": (
        "docs/THE-GAMEPLAN.md section 1.2: connectors/<id>/adapter.py, and this tool's docstring states "
        "what it calls",
        "export parse, emit, invoke, read_cassette, cassette_values and AdapterRefusal from adapter.py; "
        "or fix the import error named above",
    ),
    "CONFORMANCE_FIXTURES_ABSENT": (
        "docs/THE-GAMEPLAN.md section 1.2: connectors/<id>/fixtures.jsonl",
        "write fixtures.jsonl beside the manifest, one events fixture per cassette and one refusal "
        "fixture per required input",
    ),
    "CONFORMANCE_FIXTURE_SHAPE": (
        "conformance/connector-harness/fixture.schema.json, read through tools/validate_manifest.py; "
        "doctrine/RETENTION.md RT-15 and reading MF-R8 for inputs",
        "correct the line against the fixture schema; replace a filled value with a slot name in angle "
        "brackets or a typed token synthetic/GROUND_TRUTH.yaml carries, and keep the value out of every "
        "commit",
    ),
    "CONFORMANCE_FIXTURE_CONNECTOR_MISMATCH": (
        "conformance/connector-harness/fixture.schema.json: a fixture names its connector at a version",
        "set connector.id and connector.version to the manifest's; or move the fixture to the connector "
        "it belongs to",
    ),
    "CONFORMANCE_CASSETTE_ABSENT": (
        "docs/PLAINSIGHT-design.md section 6.3: record and replay is day-one infrastructure",
        "place the cassette at the named path; or correct the fixture's cassette path",
    ),
    "CONFORMANCE_CASSETTE_VALUE": (
        "doctrine/RETENTION.md RT-15 and AGENTS.md section 4: no selector value in a tracked file; "
        "cassettes are captured against S2 or N0 targets only",
        "replace the cell with the placeholder the fixture's input carries, everywhere it appears in the "
        "cassette; and keep the value out of every commit, because git history is the one store a "
        "crypto-shred cannot reach",
    ),
    "CONFORMANCE_ADAPTER_CRASHED": (
        "docs/PLAINSIGHT-design.md section 6.3: error classification is adapter code returning a fixed enum",
        "return a parsed run with adapter state malformed or error for input it cannot read; or raise "
        "AdapterRefusal with a declared code",
    ),
    "CONFORMANCE_UNEXPECTED_REFUSAL": (
        "conformance/connector-harness/fixture.schema.json: result events pins events, not a refusal",
        "fix the adapter so it reads this cassette; or, if refusing is right, change the fixture to "
        "result refusal with the code the adapter declares",
    ),
    "CONFORMANCE_EVENT_COUNT": (
        "docs/THE-GAMEPLAN.md section 2.1: event_count is exact, zero included, because without it a "
        "refusing adapter satisfies every expectation",
        "fix the adapter if it emitted the wrong events; or correct event_count to the count the "
        "cassette honestly yields, recounted from the cassette and never copied from the output",
    ),
    "CONFORMANCE_ADAPTER_STATE": (
        "docs/PLAINSIGHT-design.md section 6.3: the adapter decides which fixed-enum state occurred",
        "fix the adapter's classification; or correct adapter_state to what the cassette shows",
    ),
    "CONFORMANCE_EVENT_REFUSED": (
        "CONFORMANCE.md section 3 rung 2: every emitted event passes tools/validate.py, schema, layer "
        "denylists, lineage and producer authority",
        "fix the emitted event so the named code no longer fires; never widen the schema or the policy "
        "to admit it",
    ),
    "CONFORMANCE_REFUSAL_EXPECTED": (
        "docs/PLAINSIGHT-FOUNDATION.md section 4.3: one refusal fixture per required input, and the "
        "adapter refuses it",
        "make the adapter refuse the withheld input with the declared code; or correct the fixture",
    ),
    "CONFORMANCE_REFUSAL_CODE": (
        "spec/layer-model.yaml violation_codes, read as the one code vocabulary (MF-R10)",
        "refuse with the fixture's declared code; or change the fixture's refusal_code to a declared "
        "code that names the refusal",
    ),
    "CONFORMANCE_KNOWN_NEGATIVE_HIT": (
        "docs/PLAINSIGHT-design.md section 7.2: a guaranteed-nonexistent input yields no hit, and a hit "
        "means every positive since the last passing run is untrustworthy",
        "fix the adapter's classification if it scored a negative row as a hit; or, if the cassette "
        "shows the tool claiming a nonexistent string, that endpoint fails its canary and the cassette "
        "is the evidence, so it does not belong in the known-negative fixture",
    ),
    "CONFORMANCE_KNOWN_NEGATIVE_CLASS": (
        "docs/PLAINSIGHT-design.md section 6.5 step 3: the known negative returns zero results in its "
        "declared class",
        "emit the canary's negative_class on the negative items; or correct the canary's class to one "
        "the source tells apart",
    ),
    "CONFORMANCE_KNOWN_NEGATIVE_ABSENT": (
        "docs/PLAINSIGHT-design.md section 6.5: no connector enters the registry without a passing "
        "known negative",
        "add an events fixture whose input equals the manifest's known_negative canary input, with a "
        "zero-hit cassette",
    ),
    "CONFORMANCE_GOLDEN_NOT_REPLAYED": (
        "docs/PLAINSIGHT-design.md section 6.4: the golden fixture replays green",
        "point an events fixture's cassette at the directory holding health.golden_fixture, and make "
        "that fixture hold; or correct the golden_fixture path",
    ),
    "CONFORMANCE_KNOWN_POSITIVE_ABSENT": (
        "docs/PLAINSIGHT-design.md section 6.5: a connector enters the registry with a passing known "
        "positive, and a replay that grades no hit grades no claim",
        "add an events fixture whose input equals the manifest's known_positive canary input, with a "
        "cassette that yields at least result_count_min hit items; or fix the adapter if it stopped "
        "scoring the cassette's hits",
    ),
    "CONFORMANCE_REFUSAL_INPUT": (
        "docs/PLAINSIGHT-FOUNDATION.md section 4.3 and the manifest's health.refusal_fixtures: a "
        "refusal fixture proves the adapter refuses the input it withholds",
        "raise the refusal from the check of that input, naming it in AdapterRefusal.input_field; or "
        "correct input_field in health.refusal_fixtures",
    ),
    "CONFORMANCE_VACUOUS": (
        "docs/THE-GAMEPLAN.md section 2.1: a refusing adapter satisfies every expectation vacuously",
        "add an events fixture with a cassette the adapter reads into one event or more; or fix the "
        "adapter so it stops refusing input it can read",
    ),
    "CONFORMANCE_INVOKE_UNGUARDED": (
        "doctrine/SUBJECT_SELECTION.md SS-6 and D5: no dispatch constructs argv or starts a process "
        "before runner.subject_guard.evaluate() has returned a permitting decision",
        "put every argv construction and process start in invoke() after if not decision.permits: "
        "raise; refuse with AdapterRefusal when the decision is absent, refused or not the gate's",
    ),
}


class ToolFailure(Exception):
    def __init__(self, where: str, what: str, moves: str):
        super().__init__(what)
        self.where, self.what, self.moves = where, what, moves

    def render(self) -> str:
        return (f"REFUSED CONFORMANCE_TOOL_INPUT_UNREADABLE\n  where: {self.where}\n"
                f"  what:  {self.what}\n  moves: {self.moves}")


class Finding:
    __slots__ = ("code", "where", "what")

    def __init__(self, code: str, where: str, what: str):
        if code not in CODES:
            raise KeyError(f"undeclared code {code}")
        self.code, self.where, self.what = code, where, what

    def render(self) -> str:
        rule, moves = CODES[self.code]
        return (f"REFUSED {self.code}\n  where: {self.where}\n  what:  {self.what}\n"
                f"  rule:  {rule}\n  moves: {moves}")


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


# ---------------------------------------------------------------------------
# loading
# ---------------------------------------------------------------------------

_loads = 0


def load_adapter(cdir: Path):
    """adapter.py loaded under a fresh module name. Raises Finding-worthy errors as ImportError."""
    global _loads
    _loads += 1
    path = cdir / "adapter.py"
    spec = importlib.util.spec_from_file_location(f"plainsight_connector_{cdir.name}_{_loads}", path)
    if spec is None or spec.loader is None:
        raise ImportError("no adapter.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    missing = [name for name in ADAPTER_API if not hasattr(module, name)]
    if missing:
        raise ImportError("adapter.py does not export " + ", ".join(missing))
    return module


def load_contexts() -> tuple[dict, object]:
    """validate_manifest's context and validate's policy. Exit 2 on failure."""
    try:
        vctx = VM.load_context()
    except VM.ToolFailure as fail:
        raise ToolFailure(fail.where, fail.what, fail.moves)
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            pol = V.Policy()
    except Exception as exc:  # noqa: BLE001  any defect in a generated artifact
        raise ToolFailure("schema/, policy/", f"the generated schema or policy pack could not be read "
                          f"({exc.__class__.__name__})", "run python tools/generate_pse.py --check")
    return vctx, pol


def _first_required(manifest: dict) -> dict:
    req = ((manifest.get("consumes") or {}).get("required") or [])
    opt = ((manifest.get("consumes") or {}).get("optional") or [])
    return (req or opt or [{"selector": "", "as": ""}])[0]


def replay_context(manifest: dict) -> list[dict]:
    """The GRANT and the COLLECT_EVENT PERMITTED a replayed run names as its parent."""
    common = {"pse_version": "pse-event-0.1", "derived_from": "zmeta-event-1.0", "case_id": CASE_ID}
    grant = dict(common, event={"event_id": GRANT_ID, "event_type": "AUTHORIZE_EVENT", "event_subtype": "GRANT",
                                "ts": "2026-01-15T10:00:00Z"},
                 source={"platform_id": PLATFORM_ID, "environment": "ISOLATED", "producer": REPLAY_HUMAN},
                 payload={"act": "GRANT", "authorization_ref": AUTH_REF, "subject_class": "S2",
                          "expires_on": "2026-02-14", "pivot_depth_max": 2, "authorized_by": REPLAY_HUMAN,
                          "purpose_hash": "sha256:" + "0" * 64})
    reach = ((manifest.get("bystanders") or {}).get("reach"))
    decision = dict(common, event={"event_id": DECISION_ID, "event_type": "COLLECT_EVENT",
                                   "event_subtype": "PERMITTED", "ts": "2026-01-15T10:03:00Z"},
                    source={"platform_id": PLATFORM_ID, "environment": "ISOLATED",
                            "producer": "runner-subject-guard"},
                    payload={"decision": "PERMITTED", "authorization_ref": AUTH_REF,
                             "connector_id": manifest.get("id"),
                             "target_selector_type": _first_required(manifest).get("selector"),
                             "subject_relation": "seed", "pivot_depth": 0, "decided_at_step": 6,
                             "incidental_estimate": 0,
                             "bystander_disposition": "refuse" if reach == "named_selector_only" else "count_only",
                             "motivated_by": None},
                    lineage={"based_on": [GRANT_ID], "transform": None})
    return [grant, decision]


def run_context(manifest: dict, manifest_hash: str, fixture: dict, duration_ms: int) -> dict:
    return {
        "case_id": CASE_ID,
        "decision_event_id": DECISION_ID,
        "motivated_by": None,
        "inputs": dict(fixture.get("input") or {}),
        "manifest_hash": manifest_hash,
        "argv_template": ((manifest.get("lineage") or {}).get("command_template") or ""),
        "egress_identity": EGRESS_IDENTITY,
        "platform_id": PLATFORM_ID,
        "sw_version": "replay",
        "ts": TS,
        "duration_ms": duration_ms,
        "id_seed": fixture["id"],
    }


# ---------------------------------------------------------------------------
# DECLARE
# ---------------------------------------------------------------------------


def declare(cdir: Path, vctx: dict) -> tuple[dict | None, list[Finding]]:
    path = cdir / "manifest.yaml"
    try:
        manifest, repeated = VM.load_manifest(path)
    except VM.ToolFailure as fail:
        return None, [Finding("CONFORMANCE_MANIFEST_REFUSED", fail.where, f"the manifest could not be read: {fail.what}")]
    inner = repeated + VM.check_manifest(manifest, vctx, rel(path), cdir, expect_id=cdir.name)
    out = [Finding("CONFORMANCE_MANIFEST_REFUSED", f.where, f"{f.code}: {f.what}") for f in inner]
    return (manifest if isinstance(manifest, dict) else None), out


# ---------------------------------------------------------------------------
# rung 4
# ---------------------------------------------------------------------------


#: A claim value of a platform-bound key: a platform token, a slash, and the rest (MF-R17, SH-R18).
PLATFORM_PREFIXED_RE = re.compile(r"([a-z][a-z0-9_]*)/(.+)", re.S)


def claim_value_ok(value, selector_type, vctx: dict) -> bool:
    """A claim value is a placeholder, or, for a key whose registry form binds a
    platform, a platform token, a slash and a placeholder. The token is a
    platform name and not a selector, so only the part after the slash is held
    to the placeholder rule; nothing here checks that the token names a real
    platform, which the connector's own reading states (SH-R18 for Sherlock)."""
    if VM.placeholder_ok(value, vctx):
        return True
    if not (isinstance(value, str) and isinstance(selector_type, str)
            and VM.platform_bound(vctx["registry"], selector_type)):
        return False
    m = PLATFORM_PREFIXED_RE.fullmatch(value)
    return m is not None and VM.placeholder_ok(m.group(2), vctx)


def _events_of(events, etype, sub=None):
    return [e for e in events if (e.get("event") or {}).get("event_type") == etype
            and (sub is None or (e.get("event") or {}).get("event_subtype") == sub)]


def grade_fixtures(cdir: Path, manifest: dict, adapter, vctx: dict, pol) -> tuple[list[Finding], dict]:
    out: list[Finding] = []
    stats = {"fixtures": 0, "events_fixtures": 0, "events_with_output": 0, "refusal_fixtures": 0,
             "events_graded": 0, "held": 0}
    fpath = cdir / "fixtures.jsonl"
    frel = rel(fpath)
    if not fpath.is_file():
        return [Finding("CONFORMANCE_FIXTURES_ABSENT", frel, "no fixtures file, so nothing is replayed")], stats
    by_id, lint = VM._fixture_lines(fpath, frel, vctx, {})
    out += [Finding("CONFORMANCE_FIXTURE_SHAPE", f.where, f"{f.code}: {f.what}") for f in lint]
    by_id = by_id or {}
    manifest_hash = "sha256:" + hashlib.sha256((cdir / "manifest.yaml").read_bytes()).hexdigest()
    canary = (((manifest.get("health") or {}).get("canaries") or {}).get("known_negative") or {})
    canary_input = canary.get("input")
    canary_class = (canary.get("expect") or {}).get("negative_class")
    golden = (manifest.get("health") or {}).get("golden_fixture")
    golden_dir = (cdir / golden).resolve().parent if golden else None
    golden_replayed = False
    known_negative_seen = False
    positive = (((manifest.get("health") or {}).get("canaries") or {}).get("known_positive") or {})
    positive_input = positive.get("input")
    positive_min = (positive.get("expect") or {}).get("result_count_min")
    positive_min = positive_min if isinstance(positive_min, int) and not isinstance(positive_min, bool) \
        and positive_min > 0 else 1
    known_positive_held = False
    refusal_inputs = {r.get("id"): r.get("input_field")
                      for r in ((manifest.get("health") or {}).get("refusal_fixtures") or []) if isinstance(r, dict)}
    context = replay_context(manifest)
    humans = {REPLAY_HUMAN}
    for fid, fx in by_id.items():
        stats["fixtures"] += 1
        where = f"{frel} :: {fid}"
        held = True
        if fx["connector"] != {"id": manifest.get("id"), "version": manifest.get("version")}:
            out.append(Finding("CONFORMANCE_FIXTURE_CONNECTOR_MISMATCH", where,
                               "the fixture names another connector or version than the manifest"))
            continue
        cassette = fx.get("cassette")
        cpath = (cdir / cassette) if cassette else None
        if cpath is None and fx["result"] == "refusal" and golden_dir is not None:
            # A refusal fixture with no cassette replays the golden one, so the
            # withheld input is the only thing that differs from a run the
            # adapter reads, and a refusal of the empty capture proves nothing.
            cpath, cassette = golden_dir, rel(golden_dir)
        is_golden = cpath is not None and golden_dir is not None and cpath.resolve() == golden_dir
        if cpath is not None:
            if not cpath.exists():
                out.append(Finding("CONFORMANCE_CASSETTE_ABSENT", where, f"no cassette at {cassette}"))
                continue
            try:
                cells = adapter.cassette_values(cpath)
            except Exception as exc:  # noqa: BLE001
                out.append(Finding("CONFORMANCE_ADAPTER_CRASHED", where,
                                   f"cassette_values raised {exc.__class__.__name__}"))
                continue
            loose = [w for w, v in cells if not VM.placeholder_ok(v, vctx)]
            if loose:
                out.append(Finding("CONFORMANCE_CASSETTE_VALUE", f"{cassette}",
                                   f"{len(loose)} selector-bearing cell(s) are not placeholders, first at "
                                   f"{loose[0]}; the cell is not printed"))
                continue
        refusal = None
        events: list = []
        try:
            cap = adapter.read_cassette(cpath)
            parsed = adapter.parse(**cap["parse"])
            events = adapter.emit(parsed, run_context(manifest, manifest_hash, fx, cap.get("duration_ms", 0)))
        except adapter.AdapterRefusal as ref:
            refusal = ref
        except Exception as exc:  # noqa: BLE001  named by class, never by text
            out.append(Finding("CONFORMANCE_ADAPTER_CRASHED", where,
                               f"the adapter raised {exc.__class__.__name__} rather than returning a state "
                               "or refusing"))
            continue
        is_known_negative = canary_input is not None and fx["input"] == canary_input
        if fx["result"] == "events":
            stats["events_fixtures"] += 1
            if refusal is not None:
                out.append(Finding("CONFORMANCE_UNEXPECTED_REFUSAL", where,
                                   f"the fixture pins {fx['event_count']} event(s) and the adapter refused "
                                   f"under {refusal.code}"))
                continue
            if len(events) != fx["event_count"]:
                held = False
                out.append(Finding("CONFORMANCE_EVENT_COUNT", where,
                                   f"the fixture pins event_count {fx['event_count']} and the adapter emitted "
                                   f"{len(events)}"))
            ends = _events_of(events, "PROBE_EVENT", "RUN_END")
            state = (ends[0].get("payload") or {}).get("error_class") if len(ends) == 1 else None
            if state != fx["adapter_state"]:
                held = False
                out.append(Finding("CONFORMANCE_ADAPTER_STATE", where,
                                   f"the fixture pins adapter_state {fx['adapter_state']} and the run's RUN_END "
                                   f"carries {state if state is not None else 'no single RUN_END'}"))
            index = V.Index(context + list(events))
            for n, ev in enumerate(events):
                stats["events_graded"] += 1
                codes, _ = V.check_event(ev, pol, index, humans)
                if codes:
                    held = False
                    t = (ev.get("event") or {}) if isinstance(ev, dict) else {}
                    out.append(Finding("CONFORMANCE_EVENT_REFUSED", f"{where} :: event {n}",
                                       f"{t.get('event_type')} {t.get('event_subtype')} fires "
                                       f"{', '.join(sorted(codes))} under tools/validate.py check_event"))
            for n, ev in enumerate(_events_of(events, "EXTRACT_EVENT")):
                value = (ev.get("payload") or {}).get("value")
                if value is not None and not claim_value_ok(value, (ev.get("payload") or {}).get("selector_type"), vctx):
                    held = False
                    out.append(Finding("CONFORMANCE_CASSETTE_VALUE", f"{where} :: claim {n}",
                                       "a claim carries a value that is not a placeholder; the value is not "
                                       "printed"))
            if events:
                stats["events_with_output"] += 1
            if is_known_negative:
                known_negative_seen = True
                items = _events_of(events, "PROBE_EVENT", "ITEM")
                hits = [i for i in items if (i.get("payload") or {}).get("outcome") == "hit"]
                claims = _events_of(events, "EXTRACT_EVENT")
                if hits or claims:
                    held = False
                    out.append(Finding("CONFORMANCE_KNOWN_NEGATIVE_HIT", where,
                                       f"the known_negative canary's input yields {len(hits)} hit item(s) and "
                                       f"{len(claims)} claim(s), and the canary expects result_count 0"))
                if not any((i.get("payload") or {}).get("negative_class") == canary_class for i in items):
                    held = False
                    out.append(Finding("CONFORMANCE_KNOWN_NEGATIVE_CLASS", where,
                                       f"no item carries the canary's negative_class {canary_class}"))
            hit_items = [i for i in _events_of(events, "PROBE_EVENT", "ITEM")
                         if (i.get("payload") or {}).get("outcome") == "hit"]
            if positive_input is not None and fx["input"] == positive_input and held \
                    and len(hit_items) >= positive_min:
                known_positive_held = True
            if is_golden and held:
                golden_replayed = True
        else:
            stats["refusal_fixtures"] += 1
            if refusal is None:
                held = False
                out.append(Finding("CONFORMANCE_REFUSAL_EXPECTED", where,
                                   f"the fixture pins a refusal under {fx['refusal_code']} and the adapter "
                                   f"returned {len(events)} event(s)"))
            else:
                if refusal.code != fx["refusal_code"] or fx["refusal_code"] not in vctx["codes"]:
                    held = False
                    out.append(Finding("CONFORMANCE_REFUSAL_CODE", where,
                                       f"the fixture pins {fx['refusal_code']}"
                                       f"{'' if fx['refusal_code'] in vctx['codes'] else ', which spec/layer-model.yaml does not declare,'}"
                                       f" and the adapter refused under {refusal.code}"))
                if refusal.adapter_state != fx["adapter_state"]:
                    held = False
                    out.append(Finding("CONFORMANCE_ADAPTER_STATE", where,
                                       f"the fixture pins adapter_state {fx['adapter_state']} and the refusal "
                                       f"carries {refusal.adapter_state}"))
                want_field = refusal_inputs.get(fid)
                got_field = getattr(refusal, "input_field", None)
                if want_field is not None and got_field != want_field:
                    held = False
                    out.append(Finding("CONFORMANCE_REFUSAL_INPUT", where,
                                       f"the manifest's health.refusal_fixtures names input {want_field} for this "
                                       f"fixture and the refusal names {got_field or 'no input'}"))
        if held:
            stats["held"] += 1
    if canary_input is not None and not known_negative_seen:
        out.append(Finding("CONFORMANCE_KNOWN_NEGATIVE_ABSENT", frel,
                           "no events fixture carries the known_negative canary's input"))
    if positive_input is not None and not known_positive_held:
        out.append(Finding("CONFORMANCE_KNOWN_POSITIVE_ABSENT", frel,
                           f"no events fixture carrying the known_positive canary's input held with at least "
                           f"{positive_min} hit item(s)"))
    if golden and not golden_replayed:
        out.append(Finding("CONFORMANCE_GOLDEN_NOT_REPLAYED", frel,
                           f"no events fixture that holds replays the cassette directory holding {golden}"))
    if stats["events_fixtures"] == 0 or stats["events_with_output"] == 0:
        out.append(Finding("CONFORMANCE_VACUOUS", frel,
                           f"{stats['events_fixtures']} events fixture(s), and {stats['events_with_output']} "
                           "returned an event, so every expectation this file pins is met by an adapter "
                           "that refuses everything"))
    return out, stats


# ---------------------------------------------------------------------------
# invoke: reachable only through the gate
# ---------------------------------------------------------------------------


class _Dispatched(Exception):
    """Raised by the recorder that stands in for every process call."""


def _stand_in_targets() -> list[tuple[object, str]]:
    """Every process and network callable the stand-in replaces, as (owner,
    attribute): the process and network acts of tools/validate_authorization.py's
    DISPATCH_PATTERNS that the standard library carries on this platform, plus
    the socket and HTTP connect methods every client library ends in."""
    import asyncio
    import http.client
    import socket
    import urllib.request

    targets: list[tuple[object, str]] = [
        (subprocess, n) for n in ("run", "Popen", "call", "check_call", "check_output", "getoutput",
                                  "getstatusoutput")]
    targets += [(os, n) for n in dir(os) if n in ("system", "popen", "startfile")
                or n.startswith(("exec", "spawn", "posix_spawn", "fork"))]
    targets += [(asyncio, n) for n in ("create_subprocess_exec", "create_subprocess_shell", "open_connection",
                                       "start_server", "open_unix_connection")]
    targets += [(socket, n) for n in ("create_connection", "create_server", "getaddrinfo", "socketpair")]
    targets += [(socket.socket, n) for n in ("connect", "connect_ex", "bind", "sendto")]
    targets += [(urllib.request, n) for n in ("urlopen", "urlretrieve")]
    targets += [(http.client.HTTPConnection, "connect")]
    try:
        import pty
        targets.append((pty, "spawn"))
    except ImportError:
        pass
    return [(owner, n) for owner, n in targets if hasattr(owner, n)]


@contextlib.contextmanager
def _no_processes(record: list):
    """Replace every process and network callable with a recorder that raises.
    Nothing reaches a process or a socket while this is in force."""
    def recorder(*args, **kwargs):
        record.append(1)
        raise _Dispatched()

    saved = [(owner, n, getattr(owner, n)) for owner, n in _stand_in_targets()]
    for owner, n, _ in saved:
        setattr(owner, n, recorder)
    try:
        yield
    finally:
        for owner, n, fn in saved:
            setattr(owner, n, fn)


class _SaysPermitted:
    """Not the gate's Decision, and says permits True."""

    permits = True
    value = "PERMITTED"

    def __init__(self, connector_id: str, selector_type: str):
        self.connector_id, self.target_selector_type = connector_id, selector_type


def check_invoke(cdir: Path, manifest: dict, adapter) -> list[Finding]:
    out: list[Finding] = []
    path = cdir / "adapter.py"
    where = rel(path)
    try:
        import validate_authorization as VA

        sites = VA._Scan(where, ast.parse(path.read_text(encoding="utf-8"))).sites
    except SyntaxError:
        sites = []
        out.append(Finding("CONFORMANCE_INVOKE_UNGUARDED", where, "adapter.py does not parse, so no site can be read"))
    for s in sites:
        if not s.guarded and not s.exempt:
            out.append(Finding("CONFORMANCE_INVOKE_UNGUARDED", f"{where}:{s.line}",
                               f"in {s.function}, {s.call} {VA.ACT_PHRASE.get(s.act, s.act)} outside a permits "
                               "check on a runner.subject_guard decision (the --dispatch-paths rule)"))
    if out:
        # An adapter with a dispatch site outside the gate may dispatch for
        # real through a callable the stand-in does not cover, so it is never
        # called. The static finding above already refuses the claim.
        out.append(Finding("CONFORMANCE_INVOKE_UNGUARDED", f"{where} :: invoke",
                           "the run-time cases were not run, because the static scan found a site outside the "
                           "gate and calling invoke() could start a real process or connection"))
        return out
    from runner import subject_guard as sg

    req = _first_required(manifest)
    probe = "r" + secrets.token_hex(6)  # made in memory, never written, never sent: every process call is replaced
    request = sg.Request(case_id=CASE_ID, authorization_ref=None, authorization=None,
                         connector_id=str(manifest.get("id")), selector_type=str(req.get("selector") or "unknown"),
                         selector="<conformance_probe>", subject_class="S2",
                         clock=_dt.datetime.now(_dt.timezone.utc))
    refused = sg.evaluate(request)
    if refused.permits:
        out.append(Finding("CONFORMANCE_INVOKE_UNGUARDED", where,
                           "the guard permitted a request carrying no authorization record, so the run-time "
                           "check has no refused decision to offer and the guard itself is wrong"))
        return out
    cases = (("no decision", None), ("a REFUSED decision from evaluate()", refused),
             ("an object that says permits True and is not the gate's Decision",
              _SaysPermitted(str(manifest.get("id")), str(req.get("selector")))))
    for label, decision in cases:
        record: list = []
        outcome = None
        with _no_processes(record):
            try:
                adapter.invoke(decision, {req.get("as") or "input": probe})
                outcome = "returned without refusing"
            except _Dispatched:
                outcome = "reached a process or network call"
            except adapter.AdapterRefusal:
                outcome = None
            except Exception as exc:  # noqa: BLE001
                outcome = f"raised {exc.__class__.__name__} rather than the adapter's refusal"
        if record and outcome is None:
            outcome = "reached a process or network call and swallowed the stand-in's exception"
        if outcome:
            out.append(Finding("CONFORMANCE_INVOKE_UNGUARDED", f"{where} :: invoke",
                               f"given {label}, invoke {outcome}"))
    return out


# ---------------------------------------------------------------------------
# one connector
# ---------------------------------------------------------------------------


def grade_connector(cdir: Path, vctx: dict, pol, run_declare: bool = True) -> dict:
    report = {"id": cdir.name, "declare": [], "rung4": [], "stats": {}, "version": None}
    manifest, declare_findings = declare(cdir, vctx)
    if run_declare:
        report["declare"] = declare_findings
    if manifest is None:
        return report
    report["version"] = manifest.get("version")
    try:
        adapter = load_adapter(cdir)
    except Exception as exc:  # noqa: BLE001
        report["rung4"].append(Finding("CONFORMANCE_ADAPTER_CONTRACT", rel(cdir / "adapter.py"),
                                       f"adapter.py could not be loaded or is incomplete ({exc.__class__.__name__})"))
        return report
    findings, stats = grade_fixtures(cdir, manifest, adapter, vctx, pol)
    findings += check_invoke(cdir, manifest, adapter)
    report["rung4"], report["stats"] = findings, stats
    return report


def claim_text(report: dict) -> str:
    cid, ver = report["id"], report["version"] or "unversioned"
    d, r, s = report["declare"], report["rung4"], report["stats"]
    holds = not d and not r
    lines = [f"connector {cid} {ver}: " + (
        "DECLARE and rung 4 hold. That is not a conformance claim by itself; the claim is the five rungs together."
        if holds else
        "NO CONFORMANCE CLAIM. A refused rung refuses the claim, and no connector it describes may run.")]
    lines.append("  DECLARE  " + ("tools/validate_manifest.py full mode passes"
                                  if not d else f"REFUSED, {len(d)} manifest finding(s): "
                                  + ", ".join(sorted({f.what.split(':', 1)[0] for f in d}))))
    lines.append(f"  rung 1   python -m pytest connectors/{cid}: not run by this tool; make prove runs it")
    lines.append(f"  rung 2   tools/validate.py check_event over every emitted event, in process: "
                 f"{s.get('events_graded', 0)} event(s), "
                 f"{sum(1 for f in r if f.code == 'CONFORMANCE_EVENT_REFUSED')} refused")
    lines.append("  rung 3   tools/validate_ontology.py --corpus: STUB, prints DEFERRED and checks nothing; "
                 "rung 2's generated selector enum enforces registry membership meanwhile")
    lines.append(f"  rung 4   this tool: {s.get('fixtures', 0)} fixture(s), {s.get('held', 0)} held, "
                 f"{len(r)} finding(s)" + ("" if r else ", invoke refused without a permit and reached no process "
                                                        "or network call"))
    lines.append("  rung 5   tools/validate_conformance.py --kernel-gate: a whole-repository regression gate, "
                 "not run here and never a claim about one connector")
    lines.append("  live     NOT PERFORMED. Both canaries passing live at onboarding, design section 6.5's "
                 "Prove It, is an operator act, so no connector is registered for live use")
    return "\n".join(lines)


def _telemetry(outcome: str, findings: list[Finding]) -> None:
    if not gate_log:
        return
    try:
        gate_log.record_run(GATE, outcome, count=len(findings))
        for f in findings:
            gate_log.record_finding(GATE, code=f.code, where=f.where.split(" :: ")[0])
    except Exception:
        pass


def run(dirs: list[Path], quiet: bool) -> int:
    try:
        vctx, pol = load_contexts()
    except ToolFailure as fail:
        print(fail.render(), file=sys.stderr)
        return 2
    every: list[Finding] = []
    for cdir in dirs:
        if not (cdir / "manifest.yaml").is_file():
            f = Finding("CONFORMANCE_MANIFEST_REFUSED", rel(cdir), "MANIFEST_ABSENT: the directory carries no manifest.yaml")
            every.append(f)
            print(f.render(), file=sys.stderr)
            print(file=sys.stderr)
            continue
        report = grade_connector(cdir, vctx, pol)
        findings = report["declare"] + report["rung4"]
        every += findings
        for f in findings:
            print(f.render(), file=sys.stderr)
            print(file=sys.stderr)
        text = claim_text(report)
        print(text if not quiet or findings else text.splitlines()[0])
    _telemetry("refuse" if every else "pass", every)
    if not dirs:
        print("validate_connector_conformance: no connector directory exists under connectors/, so no "
              "connector was graded and none is registered.")
    if every:
        print(f"validate_connector_conformance: {len(every)} refusal(s).", file=sys.stderr)
        return 1
    return 0


def connector_dirs() -> list[Path]:
    if not CONNECTORS.is_dir():
        return []
    return sorted(p for p in CONNECTORS.iterdir() if p.is_dir() and not p.name.startswith((".", "_"))
                  and p.name != "__pycache__")


# ---------------------------------------------------------------------------
# --self-test
# ---------------------------------------------------------------------------

BASELINE = "sherlock"


def _rewrite_fixture(cdir: Path, fid: str, **over) -> None:
    path = cdir / "fixtures.jsonl"
    lines = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            fx = json.loads(line)
            if fx["id"] == fid:
                fx.update(over)
            line = json.dumps(fx)
        lines.append(line)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _replace_bytes(path: Path, old: str, new: str, count: int = -1) -> None:
    data = path.read_bytes().decode("utf-8")
    if old not in data:
        raise AssertionError(f"the plant's anchor is absent from {path.name}")
    path.write_bytes(data.replace(old, new, count).encode("utf-8"))


def _plant_known_negative_hit(cdir: Path) -> None:
    cas = cdir / "cassettes" / "known_negative"
    _replace_bytes(cas / "result.csv", "GitHub,https://www.github.com/,https://www.github.com/<random_nonexistent_string>,Available,404,",
                   "GitHub,https://www.github.com/,https://www.github.com/<random_nonexistent_string>,Claimed,200,", 1)
    _replace_bytes(cas / "stdout.txt", "[-] GitHub: Not Found!",
                   "[+] GitHub: https://www.github.com/<random_nonexistent_string>", 1)
    _replace_bytes(cas / "stdout.txt", "Search completed with 0 results", "Search completed with 1 results", 1)


def _plant_event_count(cdir: Path) -> None:
    for line in (cdir / "fixtures.jsonl").read_text(encoding="utf-8").splitlines():
        fx = json.loads(line)
        if fx["id"] == "known-positive":
            _rewrite_fixture(cdir, "known-positive", event_count=fx["event_count"] + 1)


def _plant_fixture_value(token: str):
    def plant(cdir: Path) -> None:
        _rewrite_fixture(cdir, "known-positive", input={"username": token})
    return plant


def _plant_cassette_value(token: str):
    def plant(cdir: Path) -> None:
        cas = cdir / "cassettes" / "known_positive"
        _replace_bytes(cas / "result.csv", "<institutional_handle>", token)
        _replace_bytes(cas / "stdout.txt", "<institutional_handle>", token)
    return plant


def _plant_invoke_unguarded(cdir: Path) -> None:
    """Both permit reads removed, so a REFUSED decision reaches argv and the process call."""
    _replace_bytes(cdir / "adapter.py", "    if not decision.permits:\n", "    if False:\n", 1)
    _replace_bytes(cdir / "adapter.py", " or decision.permits is not True:\n", ":\n", 1)


def _plant_uncalled_dispatch(cdir: Path) -> None:
    """A dispatch no test reaches: only the static scan can see it."""
    with open(cdir / "adapter.py", "a", encoding="utf-8") as fh:
        fh.write('\n\ndef warm_image():\n    subprocess.run(["docker", "image", "inspect", "sherlock-local:0.16.1"])\n')


def _plant_refusal_code(cdir: Path) -> None:
    _rewrite_fixture(cdir, "refuse-no-username", refusal_code="SCHEMA_INVALID")


def _plant_manifest_subject_class(cdir: Path) -> None:
    _replace_bytes(cdir / "manifest.yaml", "canary_subject_class: institutional\n", "", 1)


def _plant_runtime_call(line: str):
    """A call through sys.modules, which the static scan cannot resolve, placed
    before every permit check in invoke(): only the run-time stand-in sees it."""
    def plant(cdir: Path) -> None:
        _replace_bytes(cdir / "adapter.py", "    no_decision = (\n", f"    {line}\n    no_decision = (\n", 1)
    return plant


def _plant_canary_class(cdir: Path) -> None:
    _replace_bytes(cdir / "manifest.yaml", "        negative_class: site_rule_reports_available\n",
                   "        negative_class: account_suspended\n", 1)


def _plant_known_negative_input(cdir: Path) -> None:
    _rewrite_fixture(cdir, "known-negative", input={"username": "<cast_username>"})


def _plant_no_known_positive(cdir: Path) -> None:
    path = cdir / "fixtures.jsonl"
    kept = [ln for ln in path.read_text(encoding="utf-8").splitlines()
            if ln.strip() and json.loads(ln)["id"] != "known-positive"]
    path.write_text("\n".join(kept) + "\n", encoding="utf-8")


def _plant_connector_version(cdir: Path) -> None:
    _rewrite_fixture(cdir, "argparse-error", connector={"id": BASELINE, "version": "0.16.0"})


def _plant_cassette_path(cdir: Path) -> None:
    _rewrite_fixture(cdir, "argparse-error", cassette="cassettes/absent")


def _plant_input_check_removed(cdir: Path) -> None:
    _replace_bytes(cdir / "adapter.py", "    if not isinstance(value, str) or not value.strip():\n", "    if False:\n", 1)


def _wrap_confidence(adapter) -> None:
    emit = adapter.emit
    adapter.emit = lambda parsed, ctx: [dict(e, confidence=0.9) for e in emit(parsed, ctx)]


def _wrap_refuse_all(adapter) -> None:
    def emit(parsed, ctx):
        raise adapter.AdapterRefusal("PAYLOAD_FIELD_MISSING", "malformed", "planted: refuses everything",
                                     "none, this is the self-test's plant")
    adapter.emit = emit


def _wrap_refuse_empty_runs(adapter) -> None:
    emit = adapter.emit

    def wrapped(parsed, ctx):
        if parsed.get("adapter_state") == "empty":
            raise adapter.AdapterRefusal("PAYLOAD_FIELD_MISSING", "malformed", "planted", "none, a plant")
        return emit(parsed, ctx)
    adapter.emit = wrapped


def _wrap_never_refuse(adapter) -> None:
    emit = adapter.emit

    def wrapped(parsed, ctx):
        try:
            return emit(parsed, ctx)
        except adapter.AdapterRefusal:
            return []
    adapter.emit = wrapped


def _wrap_run_end_state(adapter) -> None:
    emit = adapter.emit

    def wrapped(parsed, ctx):
        events = emit(parsed, ctx)
        for e in events:
            if e["event"]["event_subtype"] == "RUN_END" and e["payload"]["error_class"] == "empty":
                e["payload"]["error_class"] = "ok"
        return events
    adapter.emit = wrapped


def _wrap_refusal(**over):
    def wrap(adapter) -> None:
        emit = adapter.emit

        def wrapped(parsed, ctx):
            try:
                return emit(parsed, ctx)
            except adapter.AdapterRefusal as ref:
                kw = dict(code=ref.code, adapter_state=ref.adapter_state, what=ref.what, moves=ref.moves,
                          input_field=getattr(ref, "input_field", None))
                kw.update(over)
                raise adapter.AdapterRefusal(**kw) from None
        adapter.emit = wrapped
    return wrap


def _wrap_claim_value(token: str):
    def wrap(adapter) -> None:
        emit = adapter.emit

        def wrapped(parsed, ctx):
            events = emit(parsed, ctx)
            for e in events:
                if e["event"]["event_type"] == "EXTRACT_EVENT":
                    e["payload"]["value"] = token
            return events
        adapter.emit = wrapped
    return wrap


def _wrap_no_hits(adapter) -> None:
    parse = adapter.parse

    def wrapped(**kw):
        parsed = parse(**kw)
        for item in parsed.get("items") or []:
            if item["outcome"] == "hit":
                item["outcome"] = "ambiguous"
        return parsed
    adapter.parse = wrapped


def _wrap_refuse_empty_capture(adapter) -> None:
    """With the input check gone, refuse the capture-less run a refusal fixture
    used to replay: the shape that passed while refusal fixtures had no cassette."""
    emit = adapter.emit

    def wrapped(parsed, ctx):
        if parsed.get("csv_sha256") is None:
            raise adapter.AdapterRefusal("PAYLOAD_FIELD_MISSING", "malformed", "planted", "none, a plant")
        return emit(parsed, ctx)
    adapter.emit = wrapped


def self_test(quiet: bool = False) -> int:
    source = CONNECTORS / BASELINE
    if not (source / "manifest.yaml").is_file():
        print(f"validate_connector_conformance --self-test: connectors/{BASELINE}/ is absent, and the self-test "
              "plants its defects in a copy of it", file=sys.stderr)
        return 2
    try:
        vctx, pol = load_contexts()
    except ToolFailure as fail:
        print(fail.render(), file=sys.stderr)
        return 2
    filled = "f" + secrets.token_hex(5)  # made in memory, written only to the scratch copy
    plants = [
        ("the known-negative cassette altered so the known negative yields a hit",
         _plant_known_negative_hit, None, False, "CONFORMANCE_KNOWN_NEGATIVE_HIT", None),
        ("event_count off by one on the known-positive fixture",
         _plant_event_count, None, False, "CONFORMANCE_EVENT_COUNT", None),
        ("an emitted event carrying confidence",
         None, _wrap_confidence, False, "CONFORMANCE_EVENT_REFUSED", "EXTRACT_HAS_CONFIDENCE"),
        ("a fixture input filled with a value instead of a placeholder",
         _plant_fixture_value(filled), None, False, "CONFORMANCE_FIXTURE_SHAPE", None),
        ("a cassette username cell filled with a value instead of a placeholder",
         _plant_cassette_value(filled), None, False, "CONFORMANCE_CASSETTE_VALUE", None),
        ("invoke with both permit reads removed, caught statically, so the run-time cases are withheld",
         _plant_invoke_unguarded, None, False, "CONFORMANCE_INVOKE_UNGUARDED", "the run-time cases were not run"),
        ("a process call the static scan cannot resolve, before the permit check, caught at run time",
         _plant_runtime_call('sys.modules["subprocess"].run(["tool"])'), None, False,
         "CONFORMANCE_INVOKE_UNGUARDED", "reached a process or network call"),
        ("a socket connect the static scan cannot resolve, before the permit check, caught at run time",
         _plant_runtime_call('sys.modules["socket"].create_connection(("127.0.0.1", 9))'), None, False,
         "CONFORMANCE_INVOKE_UNGUARDED", "reached a process or network call"),
        ("a process call outside the permit region that nothing calls, caught by the static scan",
         _plant_uncalled_dispatch, None, False, "CONFORMANCE_INVOKE_UNGUARDED", "in warm_image"),
        ("an adapter that refuses every input",
         None, _wrap_refuse_all, False, "CONFORMANCE_VACUOUS", None),
        ("a refusal fixture pinning a code the adapter does not refuse under",
         _plant_refusal_code, None, False, "CONFORMANCE_REFUSAL_CODE", None),
        ("the manifest without canary_subject_class, caught by DECLARE",
         _plant_manifest_subject_class, None, True, "CONFORMANCE_MANIFEST_REFUSED", "MANIFEST_CANARY_SUBJECT_CLASS"),
        ("the known-negative canary naming a class no item carries",
         _plant_canary_class, None, False, "CONFORMANCE_KNOWN_NEGATIVE_CLASS", None),
        ("no events fixture carrying the known-negative canary's input",
         _plant_known_negative_input, None, False, "CONFORMANCE_KNOWN_NEGATIVE_ABSENT", None),
        ("the known-positive fixture removed, leaving only a refusal fixture on the golden cassette",
         _plant_no_known_positive, None, False, "CONFORMANCE_GOLDEN_NOT_REPLAYED", None),
        ("an adapter whose known-positive replay scores no hit",
         None, _wrap_no_hits, False, "CONFORMANCE_KNOWN_POSITIVE_ABSENT", None),
        ("an adapter that refuses an events fixture",
         None, _wrap_refuse_empty_runs, False, "CONFORMANCE_UNEXPECTED_REFUSAL", None),
        ("an adapter that never refuses",
         None, _wrap_never_refuse, False, "CONFORMANCE_REFUSAL_EXPECTED", None),
        ("an events fixture whose RUN_END carries another state",
         None, _wrap_run_end_state, False, "CONFORMANCE_ADAPTER_STATE", "pins adapter_state empty"),
        ("a refusal carrying another adapter state",
         None, _wrap_refusal(adapter_state="error"), False, "CONFORMANCE_ADAPTER_STATE", "the refusal carries"),
        ("a refusal naming another input than the manifest's refusal fixture",
         None, _wrap_refusal(input_field="other"), False, "CONFORMANCE_REFUSAL_INPUT", None),
        ("the input check removed and the empty capture refused instead",
         _plant_input_check_removed, _wrap_refuse_empty_capture, False, "CONFORMANCE_REFUSAL_CODE",
         "refuse-null-username"),
        ("a claim value filled by the adapter rather than carried from the cassette",
         None, _wrap_claim_value(filled), False, "CONFORMANCE_CASSETTE_VALUE", "a claim carries a value"),
        ("a handle claim value with a platform token and a filled string after it",
         None, _wrap_claim_value("github/" + filled), False, "CONFORMANCE_CASSETTE_VALUE",
         "a claim carries a value"),
        ("a fixture naming another connector version",
         _plant_connector_version, None, False, "CONFORMANCE_FIXTURE_CONNECTOR_MISMATCH", None),
        ("a fixture pointing at a cassette that does not exist",
         _plant_cassette_path, None, False, "CONFORMANCE_CASSETTE_ABSENT", None),
    ]
    failures = 0

    def show(ok: bool, label: str, detail: str) -> None:
        if not quiet or not ok:
            print(f"  {'refused ' if ok else 'MISSED  '} {label}{detail}")

    with tempfile.TemporaryDirectory(prefix="plainsight-cc-selftest-") as scratch:
        def fresh(name: str) -> Path:
            dest = Path(scratch) / name / "connectors" / BASELINE
            shutil.copytree(source, dest, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
            return dest

        def grade(cdir: Path, wrap, with_declare: bool) -> list[Finding]:
            manifest, dfind = declare(cdir, vctx)
            adapter = load_adapter(cdir)
            if wrap:
                wrap(adapter)
            found, _ = grade_fixtures(cdir, manifest, adapter, vctx, pol)
            found += check_invoke(cdir, manifest, adapter)
            return (dfind if with_declare else []) + found

        base_dir = fresh("baseline")
        base = grade(base_dir, None, False)
        base_declare = {f.what.split(":", 1)[0] for f in declare(base_dir, vctx)[1]}
        if base:
            failures += 1
            print(f"  BASELINE the unplanted copy is not clean under rung 4: "
                  f"{', '.join(sorted({f.code for f in base}))}")
        elif not quiet:
            print(f"  clean    the unplanted copy of connectors/{BASELINE}/ under rung 4 and the invoke check")
        for n, (label, plant, wrap, with_declare, code, inner) in enumerate(plants):
            cdir = fresh(f"plant{n}")
            if plant:
                plant(cdir)
            got = grade(cdir, wrap, with_declare)
            hit = [f for f in got if f.code == code and (inner is None or inner in f.what or inner in f.where)]
            if with_declare and inner in base_declare:
                hit = []
            ok = bool(hit)
            failures += 0 if ok else 1
            show(ok, label, f"  ({code}{', ' + inner if inner else ''})" if ok
                 else f"  expected {code}{' naming ' + inner if inner else ''}, got "
                      f"{', '.join(sorted({f.code for f in got})) or 'nothing'}")
    if failures:
        print(f"validate_connector_conformance --self-test: {failures} plant(s) not refused or baseline unclean",
              file=sys.stderr)
        return 1
    print(f"validate_connector_conformance --self-test ok: {len(plants)} plants, {len(plants)} refused by their "
          "own code, and the unplanted copy clean")
    return 0


# ---------------------------------------------------------------------------
# entry
# ---------------------------------------------------------------------------


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Rung 4: every connector's adapter against its cassettes and fixtures.")
    ap.add_argument("--all", action="store_true", help="Every connectors/<id>/.")
    ap.add_argument("--connector", metavar="ID", help="connectors/<ID>/ alone.")
    ap.add_argument("--self-test", action="store_true", help="Plant each defect in a scratch copy; assert each refusal.")
    ap.add_argument("--quiet", action="store_true", help="Print only refusals and the claim's first line.")
    args = ap.parse_args(argv)
    if sum(bool(x) for x in (args.all, args.connector is not None, args.self_test)) != 1:
        ap.error("pass one of: --all, --connector <id>, or --self-test")
    if args.self_test:
        return self_test(quiet=args.quiet)
    if args.all:
        return run(connector_dirs(), args.quiet)
    cid = args.connector
    if not re.fullmatch(r"[a-z][a-z0-9_]{1,62}", cid or ""):
        print("REFUSED CONFORMANCE_TOOL_INPUT_UNREADABLE\n"
              "  where: --connector\n"
              "  what:  the id is empty or outside the manifest schema's id pattern, so it names no "
              "connectors/<id>/ directory\n"
              "  moves: pass the id of a directory under connectors/, such as --connector sherlock; or "
              "run --all", file=sys.stderr)
        return 2
    cdir = CONNECTORS / cid
    if not cdir.is_dir():
        print("REFUSED CONFORMANCE_TOOL_INPUT_UNREADABLE\n"
              f"  where: connectors/{cid}/\n"
              "  what:  no such connector directory\n"
              "  moves: correct the id; or run --all to grade every connector", file=sys.stderr)
        return 2
    return run([cdir], args.quiet)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
