"""The application's refusal codes and the strings an operator reads.

These codes are the store's and the door's. None of them is a PSE wire code,
and none may appear in policy/violation-codes.yaml: a test asserts the two sets
are disjoint (app/tests/test_boundaries.py).

Every code states what was refused, which rule refused it, and the two or three
legal moves available (CLAUDE.md section 4). A refusal's detail carries opaque
ids, line numbers, field names and codes only. It never carries a selector
value, a locator, analyst prose, or a hash of any of them.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Code:
    code: str
    what: str
    rule: str
    moves: tuple[str, ...]


def _c(code: str, what: str, rule: str, *moves: str) -> Code:
    return Code(code, what, rule, tuple(moves))


REFUSALS: dict[str, Code] = {
    c.code: c
    for c in (
        _c(
            "STORE_PATH_IN_REPOSITORY",
            "the store root is inside a git working tree",
            "doctrine/RETENTION.md RT-15: git history is the one store the shred cannot reach",
            "set PLAINSIGHT_HOME to a directory outside every git working tree",
            "pass --store with such a directory",
            "unset both to use the default under %LOCALAPPDATA%\\plainsight",
        ),
        _c(
            "STORE_PATH_TOO_LONG",
            "a store root so long that a case database path would pass the Windows path limit",
            "the store layout: cases/case_<uuid>.sqlite and its journal must open, and SQLite on "
            "Windows cannot open a path past 259 characters",
            "set PLAINSIGHT_HOME to a shorter directory",
            "pass --store with a shorter directory",
            "unset both to use the default under %LOCALAPPDATA%\\plainsight",
        ),
        _c(
            "STORE_NOT_INITIALIZED",
            "the store root holds no plane.sqlite, so there is no store to open",
            "the store layout of docs/PLAINSIGHT-design.md amendment 9.2",
            "run python -m app init --store <root> first",
            "point --store or PLAINSIGHT_HOME at a root that was initialized",
        ),
        _c(
            "STORE_PRAGMA_UNSET",
            "a store connection opened without foreign_keys on, or outside rollback-journal mode",
            "docs/PLAINSIGHT-design.md amendment 9.1: cascades need foreign_keys, and one commit is "
            "atomic across the attached databases only in rollback-journal mode",
            "open the store through app.store.db, which sets both",
            "do not switch the store to WAL; that silently breaks the cross-database commit",
        ),
        _c(
            "STORE_ISOLATED_NOT_PROVISIONED",
            "a SQLite store opened with PLAINSIGHT_ENVIRONMENT set to ISOLATED, so nothing was opened or created",
            "docs/PLAINSIGHT-design.md amendments 9.1 and 9.12, and doctrine/EGRESS.md EG-2: the SQLite "
            "engine is the workstation store and holds synthetic corpus files only; the ISOLATED store "
            "is the operator's Postgres inside the provisioned VM",
            "unset PLAINSIGHT_ENVIRONMENT to open this store on LOCAL",
            "run against the ISOLATED store inside the provisioned VM",
        ),
        _c(
            "INGEST_CONCURRENT",
            "an ingest that another ingest overtook between its checks and its write, so nothing was written",
            "decision D3 and docs/PLAINSIGHT-design.md amendment 9.12: the log is append-only, and the "
            "door's checks hold only for the log they read",
            "run the ingest again; events the other ingest wrote are then reported as held",
            "run one ingest at a time against a store",
        ),
        _c(
            "CASE_ID_INVALID",
            "a case id that is not a uuid, so no per-case file name can be built from it",
            "spec/pse-semantics-contract.md section 4: identifiers are uuids",
            "pass the case's uuid exactly as the envelope carries it",
            "ingest the case before addressing it",
        ),
        _c(
            "STORE_LOCAL_SYNTHETIC_ONLY",
            "this store is on LOCAL and holds tracked, unmodified synthetic corpus files only",
            "doctrine/EGRESS.md EG-2: the case store lives in ISOLATED, and LOCAL holds stratum 4",
            "ingest conformance/must-pass.jsonl from a clean checkout",
            "run against a case store in ISOLATED",
            "ask the operator to add a sealed synthetic file to SYNTHETIC_SOURCES, which is Class F",
        ),
        _c(
            "GENERATED_ARTIFACTS_STALE",
            "the generated schema or policy files differ from what spec/layer-model.yaml generates",
            "CONFORMANCE.md: tools/validate.py enforces the generated artifacts, so stale ones "
            "would validate against an old model",
            "run python tools/generate_pse.py, then python tools/generate_pse.py --check",
            "restore the generated files from a clean checkout",
        ),
        _c(
            "VALIDATOR_UNAVAILABLE",
            "tools/validate.py or the generated artifacts it reads could not be loaded",
            "docs/PLAINSIGHT-design.md amendment 9.12: the door validates with the existing tool and no copy",
            "run python tools/validate.py --kernel and fix what it reports",
            "install PyYAML and jsonschema, which the validator needs",
        ),
        _c(
            "ROW_SHAPE_INVALID",
            "a batch row that is not a JSON object",
            "docs/PLAINSIGHT-design.md amendment 9.12: rows are {name, description, event} wrappers or bare envelopes",
            "fix the named line so it parses as one JSON object",
            "drop the line from the batch",
        ),
        _c(
            "CASE_MISMATCH",
            "a batch whose rows carry more than one case id, or a case other than the store's",
            "spec/pse-semantics-contract.md section 12.1: nothing exists outside one case, and the shred is per case",
            "split the batch so each carries one case",
            "ingest into the store opened for that case",
        ),
        _c(
            "VALIDATION_REFUSED",
            "the batch: tools/validate.py fired at least one code, and nothing was written",
            "docs/PLAINSIGHT-design.md amendment 9.12: any fired code refuses the whole batch",
            "fix each event named in the FAIL lines and ingest the batch again",
            "run python tools/validate.py --file <path> to see the same codes",
        ),
        _c(
            "EVENT_ID_CONFLICT",
            "an event id already held with different canonical bytes",
            "decision D3 and spec/pse-semantics-contract.md section 6: the log is append-only and "
            "an observation is never overwritten",
            "emit a new event with a new event_id for the changed content",
            "re-ingest the identical bytes, which is a no-op",
        ),
        _c(
            "SYNTHETIC_VALUE_SHAPE",
            "an EXTRACT value on a synthetic store that is not a placeholder of the form <a-z0-9->",
            "doctrine/RETENTION.md RT-15, as defence in depth: a synthetic store never holds a filled value",
            "restore the placeholder in the corpus line",
            "ingest the case into a store in ISOLATED, which is not synthetic",
        ),
        _c(
            "PAYLOAD_STRATUM_UNDECLARED",
            "an event whose type and subtype have no stratum the store can hold in spec/layer-model.yaml",
            "doctrine/RETENTION.md RT-1: a stratum is declared at write time, never decided at delete time",
            "declare payload_stratum for the type in spec/layer-model.yaml and regenerate",
            "drop the event from the batch",
        ),
        _c(
            "ITEM_RUN_UNRESOLVED",
            "an ITEM whose run_id names no RUN_START in the case",
            "docs/PLAINSIGHT-design.md section 8.2 item 1: Run, Item, Claim",
            "ingest the run's RUN_START in the same batch or an earlier one",
            "correct the item's run_id",
        ),
        _c(
            "CLAIM_ITEM_MISMATCH",
            "a CLAIM whose source_ref.item_id is not the item its lineage names as parent",
            "spec/pse-semantics-contract.md section 6: a claim is one field asserted by one item",
            "make source_ref.item_id equal the parent ITEM's item_id",
            "re-parent the claim on the item it was extracted from",
        ),
        _c(
            "MOTIVATED_BY_UNRESOLVED",
            "a motivated_by that names no EXTRACT CLAIM in the case",
            "docs/PLAINSIGHT-design.md section 8.2 item 3: every run points at the claim that motivated it",
            "ingest the motivating claim first",
            "set motivated_by to null for a seed run",
        ),
        _c(
            "ENVELOPE_ROUND_TRIP_FAILED",
            "an envelope the skeleton and payload columns cannot rebuild byte for byte",
            "docs/PLAINSIGHT-design.md amendments 9.1 and 9.2: the artifact is event_skeleton plus "
            "event_payload, and replay is the migration",
            "report the event id; the store's column set needs a reading for the shape",
            "drop the event from the batch",
        ),
        _c(
            "BLOB_WRITE_REFUSED",
            "a blob write: raw bytes are written only in ISOLATED, with a per-case Encryptor, "
            "once EG-2 and RT-4 are stamped",
            "doctrine/RETENTION.md RT-4 and doctrine/EGRESS.md EG-2: the first blob is their trigger",
            "run the store in ISOLATED with the operator's chosen AEAD library configured",
            "ask the operator to stamp EG-2 and RT-4 in doctrine/DOCTRINE_STATUS.md",
        ),
        _c(
            "BLOB_DIGEST_MISMATCH",
            "a blob whose bytes do not hash to the sha256 that addresses them",
            "docs/PLAINSIGHT-design.md section 8.2 item 5: raw bytes are content-addressed",
            "treat the blob as corrupt and do not render it",
            "re-run the reconcile job (Step 11) to compare ledger and storage",
        ),
        _c(
            "BLOB_NOT_HELD",
            "a blob read for a digest the store does not hold: raw bytes not held",
            "docs/PLAINSIGHT-design.md amendment 9.4: no blob is written on LOCAL",
            "render the item as raw bytes not held",
            "read the blob from the case store in ISOLATED",
        ),
        _c(
            "RETENTION_POLICY_UNREADABLE",
            "policy/retention.yaml, or one of the four durations the case registry copies from it",
            "doctrine/RETENTION.md RT-5 and RT-6: the durations are read from policy, never literals in code",
            "restore policy/retention.yaml from a clean checkout",
            "run python tools/validate_retention.py --policy to see what is wrong with it",
        ),
        _c(
            "ROLLUP_BUCKET_REFUSED",
            "a case_rollup row whose dimension and bucket are not in rollup_vocab",
            "docs/PLAINSIGHT-design.md section 8.3: counts come from case_rollup, and a count is "
            "never bucketed by a value",
            "count by a closed token from rollup_vocab",
            "add the token to its closed source (the policy or the registry) and run python -m app init",
        ),
        _c(
            "EVENT_LOG_APPEND_ONLY",
            "an UPDATE or DELETE on event_skeleton",
            "decision D3 and spec/pse-semantics-contract.md section 12.2: the skeleton is append-only",
            "append a new event, such as an ADJUDICATE REVOKE, instead of changing an old one",
            "rebuild the projections with python -m app rebuild",
        ),
        _c(
            "PAYLOAD_UPDATE_REFUSED",
            "an UPDATE on event_payload",
            "decision D3: a stratum-1 payload is inserted once and only the retention sweep deletes it",
            "append a new event instead of changing a stored payload",
            "leave deletion to runner/retention_sweep.py (Step 11)",
        ),
        _c(
            "COVERAGE_CLOSED_IMMUTABLE",
            "an UPDATE on a closed coverage interval",
            "docs/PLAINSIGHT-design.md section 8.2 item 2: coverage history cannot be rewritten",
            "open a new interval for the target",
            "append a new SYSTEM_EVENT COVERAGE_INTERVAL for a later span",
        ),
        _c(
            "KV_KEY_REFUSED",
            "a workspace_kv key outside the closed set",
            "docs/PLAINSIGHT-design.md amendment 9.12: workspace keys are scroll, sort, columns, "
            "collapsed, focus, hops and drawer",
            "use one of the seven keys",
            "record an analyst act as a PSE event, never as a workspace row",
        ),
        _c(
            "KV_VALUE_REFUSED",
            "a workspace_kv value that is not a number, a boolean, a closed token or a uuid",
            "doctrine/EGRESS.md EG-3: no case material reaches per-viewer state",
            "store the node or event uuid instead of any text",
            "store a closed token such as a view or sector name",
        ),
        # -- the HTTP layer (app/http/) ------------------------------------
        _c(
            "BIND_REFUSED_LOCAL",
            "a server address other than 127.0.0.1, so nothing was bound",
            "doctrine/EGRESS.md EG-3 and docs/PLAINSIGHT-design.md amendment 9.12: the interface is a "
            "view on the store, served to this machine's loopback only",
            "omit --host, which binds 127.0.0.1",
            "pass --host 127.0.0.1",
        ),
        _c(
            "ANALYST_UNKNOWN",
            "a session identity that is not in the deployment's human identity list",
            "spec/pse-semantics-contract.md section 10: the human identity list is deployment "
            "configuration, and the session's identity comes from --analyst, never from a form",
            "pass --analyst with a name from the deployment's list (analyst-example on LOCAL)",
            "set PLAINSIGHT_HUMANS in ISOLATED to include the analyst",
        ),
        _c(
            "HOST_REFUSED",
            "a request whose Host header does not name this server's loopback address and port",
            "docs/PLAINSIGHT-design.md amendment 9.12: the server answers its own loopback origin "
            "only, so a page served from another origin cannot read it",
            "open the URL the serve command printed",
            "use 127.0.0.1 or localhost with the port the server bound",
        ),
        _c(
            "QUERY_KEY_REFUSED",
            "a query key outside the closed set, or a key given twice; the request was not served",
            "docs/PLAINSIGHT-design.md amendment 9.12: query keys are focus, hops, sector, view, "
            "lineage, dir, after, and from and to on the paths route",
            "drop the key from the URL",
            "use one of the closed keys, each once",
        ),
        _c(
            "QUERY_VALUE_REFUSED",
            "a query value that is not the shape its key takes, so the request was not served",
            "docs/PLAINSIGHT-design.md amendment 9.12: a URL carries uuids and fixed words only",
            "pass a node or event uuid for focus, lineage, from and to",
            "pass hops as 1, 2 or 3, and a closed token for sector, view and dir",
        ),
        _c(
            "REQUEST_VALUE_REFUSED",
            "a request whose path or query carries a value this case holds, so nothing was served "
            "and the value was not echoed",
            "doctrine/EGRESS.md EG-3 and docs/PLAINSIGHT-design.md amendment 9.12: the egress guard "
            "keeps case material out of URLs, logs and error bodies",
            "address the node or event by its uuid",
            "search for the value inside the view, where it never enters a URL",
        ),
        _c(
            "ROUTE_NOT_FOUND",
            "a path that matches no route, so nothing was served",
            "docs/PLAINSIGHT-design.md amendment 9.12: the route set is closed, and no route spans "
            "cases or ingests uploaded bytes",
            "open / or /c/<case uuid>/<view>",
            "read the route list in app/README.md",
        ),
        _c(
            "METHOD_REFUSED",
            "an HTTP method the route does not take",
            "docs/PLAINSIGHT-design.md amendment 9.12: GET reads, and POST and PUT are limited to "
            "the deep-dive and workspace routes",
            "use GET to read",
            "use the method the route list in app/README.md names",
        ),
        _c(
            "TOKEN_REFUSED",
            "a write request without this launch's session cookie, so nothing was written",
            "docs/PLAINSIGHT-design.md amendment 9.12: every POST and PUT carries the per-launch "
            "token, set as an HttpOnly, SameSite=Strict cookie",
            "load the page from the URL the serve command printed, which sets the cookie",
            "restart the server and reload the page if it was restarted",
        ),
        _c(
            "BODY_REFUSED",
            "a request body that is not one JSON object of the closed keys and shapes the route "
            "takes, so nothing was written",
            "docs/PLAINSIGHT-design.md amendment 9.12: a body carries uuids, closed tokens and numbers only",
            "send a JSON object with the keys the route names",
            "keep the body under 8 KiB",
        ),
        _c(
            "CASE_NOT_HELD",
            "a case this store does not hold, or one whose case database is gone",
            "spec/pse-semantics-contract.md section 12.1: nothing exists outside one case",
            "open /api/cases for the cases this store holds",
            "ingest the case first with python -m app ingest",
        ),
        _c(
            "FOCUS_REQUIRED",
            "a web, list or dossier request without a focus, so no picture was drawn",
            "docs/PLAINSIGHT-design.md section 8.4 CUT LIST A: there is no unfocused or "
            "case-wide graph, in v1 or ever",
            "add ?focus=<node uuid> to the URL",
            "press esc esc in the web, which returns the focus to the seed",
        ),
        _c(
            "NODE_NOT_IN_CASE",
            "a node id this case does not hold, so nothing was drawn, read or dispatched",
            "docs/PLAINSIGHT-design.md amendment 9.12: node ids are opaque uuids the projections assign",
            "refocus from, or select, a node the case lists",
            "if the node was swept, refocus from a remaining claim",
        ),
        _c(
            "EVENT_NOT_IN_CASE",
            "an event id this case does not hold, so no chain was walked",
            "docs/PLAINSIGHT-design.md section 5.7: lineage walks the case's own log",
            "open the lineage of a node the case lists",
            "pass an event id from the node's lineage heads",
        ),
        _c(
            "REQUEST_MALFORMED",
            "a request line or header block the server could not parse, so nothing was served",
            "docs/PLAINSIGHT-design.md amendment 9.12: the route set and its shapes are closed, and a "
            "request is read only when it parses",
            "open the URL the serve command printed",
            "send GET, POST or PUT over HTTP/1.0 or HTTP/1.1 with a path under 8 KiB",
        ),
        _c(
            "ITEM_NOT_IN_CASE",
            "an item id this case does not hold, so no raw state was read",
            "docs/PLAINSIGHT-design.md section 8.2 item 5: raw bytes belong to an item of the case",
            "pass the item_id of a claim the INSPECTOR lists",
            "open the lineage of the claim, which names its item",
        ),
        _c(
            "CLAIM_NOT_IN_CASE",
            "a motivating claim id this case does not hold, so nothing was dispatched",
            "doctrine/SUBJECT_SELECTION.md SS-16 and amendment 9.11: a deep dive names one claim of "
            "the case that motivates it",
            "select the node again and request the deep dive from its Pivot Bar",
            "pass a claim_id from the node's claims in the INSPECTOR",
        ),
        _c(
            "WEB_OVER_CAP",
            "a web over the canvas cap, so no SVG was drawn and the list twin is served instead",
            "docs/PLAINSIGHT-design.md section 8.5 and amendment 9.7: the canvas draws at most "
            "300 nodes and 600 edges, and no parameter raises that",
            "narrow by hop with -",
            "open the list twin with t, which ?sector= narrows",
            "open PATHS with 8 between two marked nodes",
        ),
        _c(
            "DEEP_DIVE_ONE_NODE_PER_ACT",
            "a deep-dive request naming more than one node, so nothing was dispatched",
            "doctrine/SUBJECT_SELECTION.md SS-16 and amendment 9.11: breadth is deliberate, one "
            "node and one motivating claim per act",
            "send one node_id and one motivating_claim",
            "make a separate deep-dive request for each node",
        ),
        _c(
            "DEEP_DIVE_NOT_DISPATCHED",
            "NOT DISPATCHED, no subject gate exists yet (Step 10): nothing was collected",
            "doctrine/SUBJECT_SELECTION.md SS-16 and amendment 9.11: a deep dive is a separate "
            "authorized act, and only the subject gate may permit one",
            "open the Lineage Drawer on the motivating claim with l",
            "mark the node and another with v, then open PATHS with 8",
            "ask the operator to connect the subject gate to this route, a Class F change",
        ),
        _c(
            "EGRESS_GUARD_REPLACED",
            "a response that carried a value this case holds where no value may go, so it was "
            "replaced and counted",
            "doctrine/EGRESS.md EG-3 and docs/PLAINSIGHT-design.md amendment 9.12: headers, titles, "
            "Location, error bodies and notice frames never carry case material",
            "report the route template from the server log, which never carries the value",
            "read the value inside the view body, where it belongs",
        ),
        _c(
            "SERVER_FAULT",
            "a request the server could not complete; its exception is logged by type name only",
            "docs/PLAINSIGHT-design.md amendment 9.12: a log line is the fixed tuple of time, method, "
            "route template, status and duration",
            "retry the request",
            "run python -m app rebuild --verify against the store",
        ),
    )
}


class Refusal(Exception):
    """A refusal the operator reads. The message is governed prose."""

    def __init__(self, code: str, detail: str = ""):
        if code not in REFUSALS:
            raise KeyError(f"undeclared refusal code {code}")
        self.code = code
        self.detail = detail
        super().__init__(self.render())

    def render(self) -> str:
        c = REFUSALS[self.code]
        moves = "; or ".join(c.moves)
        text = f"Refused {c.code}: {c.what} ({c.rule}). Legal moves: {moves}."
        if self.detail:
            text += "\n" + self.detail
        return text


def well_formed(table: dict[str, Code]) -> list[str]:
    """Codes in `table` that do not state what, rule and two or three moves."""
    bad = []
    for name, c in table.items():
        if name != c.code or not c.what.strip() or not c.rule.strip():
            bad.append(name)
        elif not 2 <= len(c.moves) <= 3 or any(not m.strip() for m in c.moves):
            bad.append(name)
    return bad
