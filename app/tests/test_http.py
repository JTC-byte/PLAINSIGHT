"""The server, its routes, the egress guard and the notice stream, over loopback.

Each check ingests conformance/must-pass.jsonl into a tmp store (a copy of one
template built through the real door), starts the server on 127.0.0.1 on an
ephemeral port, and fetches routes over a socket the test connects itself. Each
claims coverage of a mechanism on the corpus, never the correctness of an
identity or of collection (CLAUDE.md design gate 3). Each is paired in CONTROLS
with a breaker that removes the mechanism, and app/tests/test_controls.py fails
the suite if the check stays green under it.
"""

from __future__ import annotations

import json
import re
import socket
import struct
import sys
import time
import uuid
import xml.etree.ElementTree as ET

import pytest

from app.http import acts, guard as guard_mod, notices, routes, server
from app.model import web
from app.store import kv
from app.tests import served
from app.tests.helpers import CASE, corpus_events, corpus_strings, eid_of, files_digest, named, refusal_of
from app.tests.served import FOCUS, Client, corpus_copy, open_case, stream_collect, stream_open, template

API = f"/api/cases/{CASE}"
HANDLE_CLAIM = "94746128-88d7-58f3-8e87-31794f06cd25"
REFERENCED = "33c6ba89-16a7-5a0e-8e6d-540e4290a3fa"
CLUSTER_POSSIBLE = "7ef5da42-3536-5468-b095-b78352de28e4"

EXPECTED_HEADERS = {
    "Cache-Control": "no-store",
    "Content-Security-Policy": "default-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'",
    "Referrer-Policy": "no-referrer",
    "X-Content-Type-Options": "nosniff",
    "Cross-Origin-Resource-Policy": "same-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}

BANNED = re.compile(
    r"\b(confidence|score|scores|scored|weight|weights|weighted|probability|probabilities|opacity|thickness)\b"
    r"|\d\s*%|\bpercent",
    re.IGNORECASE,
)

#: The deep-dive route's text while no subject gate exists. Its moves name only keys
#: this slice builds; app/tests/test_static.py checks every key a refusal names.
NOT_DISPATCHED = (
    "NOT DISPATCHED, no subject gate exists yet (Step 10): nothing was collected. Legal moves: open the "
    "Lineage Drawer on the motivating claim with l, mark the node and another with v, then open PATHS "
    "with 8, or ask the operator to connect the subject gate to this route, a Class F change."
)


def get_routes() -> list[str]:
    """Every GET route with corpus ids, the error routes among them."""
    item = eid_of("probe-item-1")
    return [
        "/",
        f"/c/{CASE}/web?focus={FOCUS}&hops=2",
        f"/c/{CASE}/dossier?focus={FOCUS}",
        f"/c/{CASE}/collection",
        "/static/app.js",
        "/static/views/web.js",
        "/static/views/collection.js",
        "/keymap.json",
        "/api/cases",
        f"{API}/header",
        f"{API}/web?focus={FOCUS}&hops=2",
        f"{API}/web.svg?focus={FOCUS}&hops=2",
        f"{API}/web.list?focus={FOCUS}&hops=2",
        f"{API}/node/{FOCUS}",
        f"{API}/node/{HANDLE_CLAIM}",
        f"{API}/lineage/{eid_of('adjudicate-promote')}",
        f"{API}/lineage/{HANDLE_CLAIM}?dir=forward",
        f"{API}/paths?from={FOCUS}&to={REFERENCED}",
        f"{API}/dossier?focus={FOCUS}",
        f"{API}/coverage",
        f"{API}/collection",
        f"{API}/collection?focus={FOCUS}",
        f"{API}/blobs/{item}",
        f"/api/kv/{CASE}/web",
        f"{API}/web",
        f"{API}/web?focus={FOCUS}&q=1",
        f"{API}/node/{uuid.uuid5(uuid.UUID(CASE), 'absent')}",
        f"/api/cases/{uuid.uuid5(uuid.UUID(CASE), 'other')}/web?focus={FOCUS}",
        "/nowhere",
    ]


def svg_ids(body: bytes) -> tuple[set[str], set[str]]:
    root = ET.fromstring(body)
    nodes = {e.get("data-node") for e in root.iter() if e.get("data-node")}
    edges = {e.get("data-edge") for e in root.iter() if e.get("data-edge")}
    return nodes, edges


def expected_web(root, focus: str, hops: int) -> tuple[set[str], set[str]]:
    """The node and edge set for a focus, by a recursive CTE written here, not in app/."""
    store = open_case(root)
    try:
        nodes = {r[0] for r in store.conn.execute(
            "WITH RECURSIVE und(a, b) AS (SELECT src_id, dst_id FROM edge UNION SELECT dst_id, src_id FROM edge), "
            "reach(n, d) AS (SELECT ?, 0 UNION SELECT u.b, r.d + 1 FROM reach r JOIN und u ON u.a = r.n WHERE r.d < ?) "
            "SELECT DISTINCT n FROM reach",
            (focus, hops),
        )}
        edges = {r[0] for r in store.conn.execute("SELECT edge_id, src_id, dst_id FROM edge") if r[1] in nodes and r[2] in nodes}
    finally:
        store.close()
    return nodes, edges


# ---------------------------------------------------------------------------
# the web
# ---------------------------------------------------------------------------


def check_web_renders_every_node_and_edge(ctx):
    c = Client(ctx)
    r = c.get(f"{API}/web.svg?focus={FOCUS}&hops=2")
    assert r.status == 200 and r.header("Content-Type").startswith("image/svg+xml")
    got_nodes, got_edges = svg_ids(r.body)
    want_nodes, want_edges = expected_web(c.root, FOCUS, 2)
    assert got_nodes == want_nodes, "the SVG does not draw every node the store holds for the focus"
    assert got_edges == want_edges, "the SVG does not draw every edge the store holds for the focus"
    assert len(want_nodes) == 9 and len(want_edges) == 12
    assert eid_of("extract-claim-unverified") not in got_nodes, "the ignored item's handle is attached to the focus"
    one, _ = svg_ids(c.get(f"{API}/web.svg?focus={FOCUS}&hops=1").body)
    assert one == expected_web(c.root, FOCUS, 1)[0]


def break_web_walks_one_direction(ctx):
    real = web.incident_edges

    def outgoing_only(conn, ids):
        ids = set(ids)
        return [e for e in real(conn, ids) if e["src_id"] in ids]

    ctx.mp.setattr(web, "incident_edges", outgoing_only)


def test_web_renders_every_node_and_edge(ctx):
    check_web_renders_every_node_and_edge(ctx)


def check_no_number_weight_or_confidence(ctx):
    c = Client(ctx)
    bodies = []
    for path in (
        f"{API}/web?focus={FOCUS}&hops=2",
        f"{API}/web.svg?focus={FOCUS}&hops=3",
        f"{API}/web.list?focus={FOCUS}&hops=3",
        f"{API}/node/{FOCUS}",
        f"{API}/node/{HANDLE_CLAIM}",
        f"{API}/dossier?focus={FOCUS}",
        f"{API}/paths?from={FOCUS}&to={REFERENCED}",
        f"{API}/lineage/{eid_of('identity-cluster')}",
    ):
        r = c.get(path)
        assert r.status == 200, path
        bodies.append(r.body.decode("utf-8"))
    for text in bodies:
        hit = BANNED.search(text)
        assert hit is None, f"a weight, score, confidence or percentage reached a view: {hit.group(0)!r}"
    for text in bodies[:1] + bodies[2:]:
        assert not _floats(json.loads(text)), "a fractional number reached a view"


def _floats(obj) -> list:
    if isinstance(obj, float):
        return [obj]
    if isinstance(obj, dict):
        return [f for v in obj.values() for f in _floats(v)]
    if isinstance(obj, list):
        return [f for v in obj for f in _floats(v)]
    return []


def break_svg_prints_a_confidence(ctx):
    from app.model import svg

    real = svg.node_lines
    ctx.mp.setattr(svg, "node_lines", lambda n: real(n) + [("line", "confidence 0.61")])


def test_no_number_weight_or_confidence(ctx):
    check_no_number_weight_or_confidence(ctx)


def check_dashed_inference_edges(ctx):
    c = Client(ctx)
    root = ET.fromstring(c.get(f"{API}/web.svg?focus={FOCUS}&hops=2").body)
    ns = "{http://www.w3.org/2000/svg}"
    groups = [g for g in root.iter(f"{ns}g") if g.get("data-layer")]
    inference = [g for g in groups if g.get("data-layer") == "inference"]
    assert inference, "no inference edge was drawn"
    links = {eid_of(n) for n in ("link-same_entity", "link-associated_with", "link-co_located", "link-controls")}
    drawn = set()
    for g in inference:
        path = g.find(f"{ns}path")
        assert path.get("stroke-dasharray"), "an inference edge is not dashed"
        assert path.get("stroke-width") == "2"
    for g in root.iter(f"{ns}g"):
        if g.get("data-label-layer") != "inference":
            continue
        for t in g.findall(f"{ns}text"):
            assert t.text.startswith("NOT ACCEPTED, PROPOSED ") and "no analyst has asserted this" in t.text
            drawn.add(t.get("data-lineage"))
    assert drawn == links, "every LINK draws one proposed edge row"
    assert len(inference) == 1, "four proposals on one pair share a single path"
    for g in groups:
        if g.get("data-layer") != "inference":
            assert not g.find(f"{ns}path").get("stroke-dasharray"), "an observation or fusion edge is dashed"
    clusters = {g.get("data-node") for g in root.iter(f"{ns}g") if g.get("data-kind") == "cluster"}
    store = open_case(c.root)
    try:
        made = {r[0] for r in store.conn.execute(
            "SELECT n.node_id FROM node n JOIN event_skeleton s ON s.event_id = n.created_by_event_id "
            "WHERE n.kind = 'cluster' AND s.event_type = 'IDENTITY_EVENT'"
        )}
    finally:
        store.close()
    assert clusters == made, "a fusion object exists without an IDENTITY_EVENT"


def break_inference_drawn_solid(ctx):
    from app.model import svg

    ctx.mp.setitem(svg.LAYER_STYLE, "inference", {"stroke-width": "2"})


def test_dashed_inference_edges(ctx):
    check_dashed_inference_edges(ctx)


def check_citation_chain_reaches_run_and_item(ctx):
    c = Client(ctx)
    need = {eid_of(n) for n in ("probe-item-1", "probe-run-start", "collect-permitted", "authorize-grant")}
    for node_id in (FOCUS, HANDLE_CLAIM):
        node = c.get(f"{API}/node/{node_id}").json()
        heads = node["node"]["lineage_heads"]
        assert heads, "a node has no lineage head"
        chain = c.get(f"{API}/lineage/{heads[0]}").json()
        ids = {x["event_id"] for x in chain["chain"]}
        assert need <= ids, "the chain does not reach the item, the run, the decision and the grant"
        assert not chain["breaks"], "the chain is broken"
        run = next(x for x in chain["chain"] if x["subtype"] == "RUN_START")
        assert any(s.startswith("argv_template ") for s in run["summary"])
        assert any(f.startswith("decision recorded after its authorization was revoked") for f in chain["flags"])
    referenced = c.get(f"{API}/node/{REFERENCED}").json()
    head = referenced["node"]["lineage_heads"][0]
    assert head == eid_of("identity-cluster-possible"), "a referenced node walks from its referencing event"


def break_item_projection_row_deleted(ctx):
    root = corpus_copy(ctx, "broken")
    store = open_case(root)
    store.conn.execute("DELETE FROM item WHERE event_id = ?", (eid_of("probe-item-1"),))
    store.close()
    ctx.mp.setattr(Client, "__init__", _client_on(root, Client.__init__))


def _client_on(root, init):
    def patched(self, ctx, _root=None):
        init(self, ctx, root)

    return patched


def test_citation_chain_reaches_run_and_item(ctx):
    check_citation_chain_reaches_run_and_item(ctx)


def test_chain_broken_renders(ctx):
    root = corpus_copy(ctx, "broken")
    store = open_case(root)
    store.conn.execute("DELETE FROM item WHERE event_id = ?", (eid_of("probe-item-1"),))
    store.close()
    c = Client(ctx, root)
    chain = c.get(f"{API}/lineage/{eid_of('adjudicate-promote')}").json()
    assert [b["text"] for b in chain["breaks"]] == [f"▨ chain broken at {eid_of('probe-item-1')}"]
    assert eid_of("probe-run-start") not in {x["event_id"] for x in chain["chain"]}, "a break was skipped"


# ---------------------------------------------------------------------------
# the deep dive
# ---------------------------------------------------------------------------


def app_constructors(roots) -> list[str]:
    """Modules that build a COLLECT_EVENT or AUTHORIZE_EVENT envelope, or import runner."""
    import ast
    from pathlib import Path

    found = []
    for root in roots:
        for path in sorted(Path(root).rglob("*.py")):
            if "tests" in path.parts:
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Dict):
                    for k, v in zip(node.keys, node.values):
                        if isinstance(k, ast.Constant) and k.value == "event_type" and isinstance(v, ast.Constant) \
                                and v.value in ("COLLECT_EVENT", "AUTHORIZE_EVENT"):
                            found.append(path.name)
                if isinstance(node, ast.Import) and any(a.name.split(".")[0] == "runner" for a in node.names):
                    found.append(path.name)
                if isinstance(node, ast.ImportFrom) and node.module and node.module.split(".")[0] == "runner":
                    found.append(path.name)
    return found


def check_deep_dive_refuses_and_writes_nothing(ctx):
    from app import config

    c = Client(ctx)
    c.login()
    before = files_digest(c.root)
    body = {"node_id": HANDLE_CLAIM, "motivating_claim": HANDLE_CLAIM}
    ctx.mp.setattr(acts, "GATE", c.root / "absent" / "subject_guard.py")
    r = c.send("POST", f"{API}/deep-dives", body)
    assert r.status == 409, "the deep dive was not refused"
    out = r.json()
    assert out["refused"] == "DEEP_DIVE_NOT_DISPATCHED" and out["state"] == "NOT DISPATCHED"
    assert out["text"].startswith(NOT_DISPATCHED), "the refusal is not the brief's consequence text"
    assert "LOCAL executes no connector (EG-1)" in out["text"]
    ctx.mp.setattr(acts, "GATE", config.REPO_ROOT / "app" / "http" / "acts.py")
    r = c.send("POST", f"{API}/deep-dives", body)
    assert r.status == 409 and "not connected to this route" in r.json()["text"], "an existing gate file changed the route"
    r = c.send("POST", f"{API}/deep-dives", {"node_ids": [FOCUS, HANDLE_CLAIM], "motivating_claim": HANDLE_CLAIM})
    assert r.status == 400 and r.json()["refused"] == "DEEP_DIVE_ONE_NODE_PER_ACT"
    r = c.send("POST", f"{API}/deep-dives", {"node_id": [FOCUS, HANDLE_CLAIM], "motivating_claim": HANDLE_CLAIM})
    assert r.json()["refused"] == "DEEP_DIVE_ONE_NODE_PER_ACT"
    r = c.send("POST", f"{API}/deep-dives", body, cookie=False)
    assert r.status == 403 and r.json()["refused"] == "TOKEN_REFUSED"
    assert files_digest(c.root) == before, "the deep-dive route wrote to the store"
    assert app_constructors([config.REPO_ROOT / "app"] + ctx.extra_roots) == []


def break_deep_dive_records_something(ctx):
    def dispatching(app, params, query, body):
        with routes.case_store(app.root, params["case"], write=True) as store:
            kv.put(store, params["case"], app.analyst, "web", "focus", body["node_id"])
        return routes.json_response({"state": "DISPATCHED"}, status=202)

    ctx.mp.setitem(routes.HANDLERS, "deep_dive", dispatching)


def break_planted_collect_constructor(ctx):
    root = ctx.tmp / "planted-app"
    root.mkdir()
    (root / "minter.py").write_text('E = {"event_type": "COLLECT_EVENT", "event_subtype": "PERMITTED"}\n', encoding="utf-8")
    ctx.extra_roots.append(root)


def test_deep_dive_refuses_and_writes_nothing(ctx):
    check_deep_dive_refuses_and_writes_nothing(ctx)


def check_the_deep_dive_answers_for_the_applications_environment(ctx):
    """The deep-dive route's consequence is written for the environment the application read at launch, as the
    header, the case list and the COLLECTION board are (app/tests/test_collection.py). Every store that opens
    today is LOCAL, so the route is held to another environment here by setting it on the running application. A
    hand mutant that passed LOCAL to the route's read whatever the application says passed every other check in
    the suite until this one (2026-11-16)."""
    c = Client(ctx)
    c.login()
    ctx.mp.setattr(c.app, "environment", "ISOLATED")
    r = c.send("POST", f"{API}/deep-dives", {"node_id": HANDLE_CLAIM, "motivating_claim": HANDLE_CLAIM})
    out = r.json()
    assert (r.status, out.get("refused")) == (409, "DEEP_DIVE_NOT_DISPATCHED"), "the deep dive was not refused with its consequence"
    assert out["text"] == acts.not_dispatched_text("ISOLATED") and "LOCAL" not in out["text"] and "EG-1" not in out["text"], \
        "the deep-dive route states LOCAL's rule while the application runs in another environment"


def break_deep_dive_answers_as_local(ctx):
    real = acts.deep_dive
    ctx.mp.setattr(acts, "deep_dive", lambda conn, case_id, body, environment: real(conn, case_id, body, "LOCAL"))


def test_the_deep_dive_answers_for_the_applications_environment(ctx):
    check_the_deep_dive_answers_for_the_applications_environment(ctx)


# ---------------------------------------------------------------------------
# the notice stream
# ---------------------------------------------------------------------------


def check_sse_frames_carry_opaque_ids_only(ctx):
    c = Client(ctx)
    _, captured = template()
    assert captured, "the corpus ingest published no notice"
    sock, head, rest = stream_open(c, f"{API}/notices")
    assert b" 200 " in head.split(b"\r\n", 1)[0] and b"text/event-stream" in head
    value = next(iter(sorted(corpus_strings())))
    extra = dict(captured[0], value=value)
    not_opaque = dict(captured[0], ids=["not-a-uuid"])
    from app.store import ingest

    for notice in list(captured) + [extra, not_opaque]:
        for listener in list(ingest.LISTENERS):
            listener(notice)
    frames = stream_collect(sock, rest, 1.5)
    datas = [json.loads(line[len("data: "):]) for f in frames for line in f.splitlines() if line.startswith("data: ")]
    assert len(datas) == len(captured), "a frame was dropped or an invalid one was sent"
    for d in datas:
        assert set(d) == {"seq", "kind", "case_id", "ids"} and d["case_id"] == CASE
        assert all(guard_mod.is_uuid(i) for i in d["ids"]) and len(d["ids"]) <= 50
    joined = "\n".join(frames)
    assert not [v for v in corpus_strings() if v in joined], "a corpus value reached a notice frame"
    assert c.app.hub.drop_counts() == {"schema": 2}, "the two invalid notices were not dropped by the schema"
    head, frames = c.stream(f"{API}/notices", {"Last-Event-ID": "0"}, 0.6)
    first = json.loads(frames[0].split("data: ", 1)[1])
    assert first == {"seq": 44, "kind": "case", "case_id": CASE, "ids": [CASE]}, "Last-Event-ID did not resume"


def break_notice_schema_removed(ctx):
    ctx.mp.setattr(notices, "valid", lambda notice: True)


def test_sse_frames_carry_opaque_ids_only(ctx):
    check_sse_frames_carry_opaque_ids_only(ctx)


# ---------------------------------------------------------------------------
# the egress guard
# ---------------------------------------------------------------------------


def _leaks(c: Client, responses: list) -> list[str]:
    texts = [json.dumps(c.logs)]
    for r in responses:
        texts.append(json.dumps(r.headers))
        m = re.search(rb"<title>(.*?)</title>", r.body)
        if m:
            texts.append(m.group(1).decode("utf-8"))
        if r.status >= 400:
            texts.append(r.body.decode("utf-8", "replace"))
    joined = "\n".join(texts)
    return [v for v in corpus_strings() if v in joined]


def check_selector_shaped_request_refused_without_echo(ctx):
    c = Client(ctx)
    claim = named(corpus_events(), "extract-claim-handle")["payload"]["value"]
    bare = claim[1:-1]
    shaped = bare[::-1] + "@" + "example" + ".test"
    responses = []
    for path in (f"{API}/node/{bare}", f"{API}/web?focus={bare}", f"/c/{CASE}/web?focus={claim}", f"{API}/web.svg?focus={FOCUS}&hops={bare}"):
        r = c.get(path)
        responses.append(r)
        assert r.status == 400 and r.json()["refused"] == "REQUEST_VALUE_REFUSED", "a held value in a URL was not refused by the guard"
    r = c.get(f"{API}/web?focus={shaped}")
    responses.append(r)
    assert r.status == 400 and r.json()["refused"] == "QUERY_VALUE_REFUSED"
    for r in responses:
        assert bare.encode() not in r.body and shaped.encode() not in r.body
    assert not _leaks(c, responses), "a refused value was echoed"
    assert shaped not in json.dumps(c.logs) and bare not in json.dumps(c.logs)
    assert c.app.guard.counts().get("request") == 4


def break_request_guard_removed(ctx):
    ctx.mp.setattr(guard_mod.Guard, "scan_request", lambda self, target: False)


def break_log_writes_the_request_line(ctx):
    ctx.mp.setattr(server.Handler, "log_request", lambda self, code="-", size="-": self.app.log((self.requestline, code)))


def test_selector_shaped_request_refused_without_echo(ctx):
    check_selector_shaped_request_refused_without_echo(ctx)


def check_crawl_leaks_no_value(ctx):
    c = Client(ctx)
    responses = [c.get(p) for p in get_routes()]
    bare = named(corpus_events(), "extract-claim-handle")["payload"]["value"][1:-1]
    responses.append(c.get(f"{API}/node/{bare}"))
    assert {r.status for r in responses} >= {200, 400, 404}
    sock, head, rest = stream_open(c, f"{API}/notices", {"Last-Event-ID": "1"})
    frames = stream_collect(sock, rest, 0.5)
    leaks = _leaks(c, responses)
    leaks += [v for v in corpus_strings() if v in head.decode("utf-8", "replace") + "\n".join(frames)]
    assert not leaks, "a corpus value reached a log line, a header, a title, an error body or a frame"
    title = next(r for r in responses if (r.header("Content-Type") or "").startswith("text/html") and b"C-" in r.body)
    assert f"<title>PLAINSIGHT C-{CASE[:8]}</title>".encode() in title.body
    for line in c.logs:
        assert len(line) == 5 and line[2].startswith(("/", "unmatched")) and isinstance(line[3], int)


def test_crawl_leaks_no_value(ctx):
    check_crawl_leaks_no_value(ctx)


def check_every_response_carries_the_headers(ctx):
    """Every response and the notice stream's head carry the security headers. The session cookie's attributes
    and the Host check, which this check also asserted before amendment 9.27, have checks of their own below,
    each with its controls."""
    c = Client(ctx)
    responses = [c.get(p) for p in get_routes()]
    c.login()
    responses.append(c.send("POST", f"{API}/deep-dives", {"node_id": FOCUS, "motivating_claim": HANDLE_CLAIM}))
    responses.append(c.send("PUT", f"/api/kv/{CASE}/web", {"hops": 2}))
    responses.append(c.request("DELETE", f"{API}/header"))
    for r in responses:
        for k, v in EXPECTED_HEADERS.items():
            assert r.header(k) == v, f"a response does not carry {k}: {v}"
    _, head, _ = stream_open(c, f"{API}/notices")
    for k, v in EXPECTED_HEADERS.items():
        assert f"{k}: {v}".encode() in head, f"the notice stream's head does not carry {k}: {v}"


def break_no_store_dropped(ctx):
    ctx.mp.delitem(server.SECURITY_HEADERS, "Cache-Control")


def break_corp_dropped(ctx):
    ctx.mp.delitem(server.SECURITY_HEADERS, "Cross-Origin-Resource-Policy")


def break_permissions_policy_dropped(ctx):
    ctx.mp.delitem(server.SECURITY_HEADERS, "Permissions-Policy")


def break_form_action_dropped(ctx):
    csp = server.SECURITY_HEADERS["Content-Security-Policy"]
    assert csp.endswith("; form-action 'none'")
    ctx.mp.setitem(server.SECURITY_HEADERS, "Content-Security-Policy", csp[: -len("; form-action 'none'")])


def test_every_response_carries_the_headers(ctx):
    check_every_response_carries_the_headers(ctx)


def check_a_route_cannot_replace_a_security_header(ctx):
    """A route's header that names a security header, in any letter case, is dropped, and the configured one is
    sent once (review finding 9 of 2026-11-14, amendment 9.27). No route sets one today, so this plants one on
    the keymap route."""
    c = Client(ctx)
    weak = {"content-security-policy": "default-src *", "Cache-Control": "max-age=600", "X-Route-Note": "kept"}
    ctx.mp.setitem(routes.HANDLERS, "keymap",
                   lambda app, params, query, body: routes.Response(200, "application/json; charset=utf-8", b"{}", dict(weak)))
    r = c.get("/keymap.json")
    assert r.status == 200
    for k, v in EXPECTED_HEADERS.items():
        sent = [value for name, value in r.headers if name.lower() == k.lower()]
        assert sent == [v], f"a route's own header replaced or joined the configured {k}: {sent}"
    assert r.header("X-Route-Note") == "kept", "a route's header that names no security header was dropped"


def break_route_header_wins(ctx):
    ctx.mp.setattr(server, "with_security_headers", lambda headers: {**server.SECURITY_HEADERS, **headers})


def test_a_route_cannot_replace_a_security_header(ctx):
    check_a_route_cannot_replace_a_security_header(ctx)


# ---------------------------------------------------------------------------
# the boundary: the Host check, the session cookie, and the page that sent a
# write (amendment 9.27, the read-only review of 2026-11-14)
# ---------------------------------------------------------------------------


def _writes() -> list[tuple[str, str, dict]]:
    """One body for each write route: a deep dive, which refuses with its consequence and writes nothing, a NOTE,
    which lands while LOCAL_ACTS is set in memory, and a workspace key."""
    return [
        ("POST", f"{API}/deep-dives", {"node_id": HANDLE_CLAIM, "motivating_claim": HANDLE_CLAIM}),
        ("POST", f"{API}/acts", {"act": "NOTE", "target": HANDLE_CLAIM, "text": "compare against item 2 before citing"}),
        ("PUT", f"/api/kv/{CASE}/web", {"hops": 2}),
    ]


#: What each write route answers once the boundary admits a write: the deep dive its own refusal, the act as
#: landed, the workspace key as written.
ADMITTED = {"deep-dives": (409, "DEEP_DIVE_NOT_DISPATCHED"), "acts": (201, None), "web": (200, None)}


def _write_client(ctx) -> Client:
    """A served corpus copy, logged in, with LOCAL_ACTS set in memory so an act can land, as
    app/tests/test_acts.py sets it; the shipped value is False (reading APP-R31)."""
    from app import config

    ctx.mp.setattr(config, "LOCAL_ACTS", True)
    c = Client(ctx)
    c.login()
    return c


def _other_port(port: int) -> int:
    return port + 1 if port < 65535 else port - 1


def _refused_unwritten(c: Client, headers: dict, status: int, code: str, detail: str, why: str) -> None:
    """Every write route refuses a write carrying `headers`, and the store's files are unchanged after."""
    before = files_digest(c.root)
    for method, path, body in _writes():
        r = c.send(method, path, body, headers=headers)
        out = r.json()
        assert (r.status, out.get("refused"), out.get("detail", "")) == (status, code, detail), \
            f"{why}: {method} {path} answered {r.status} {out.get('refused')}"
    assert files_digest(c.root) == before, f"{why}, and the write reached the store"


def _admitted(c: Client, headers: dict) -> None:
    """Every write route answers a write carrying `headers` as it does once the boundary admits it."""
    for method, path, body in _writes():
        r = c.send(method, path, body, headers=headers)
        status, refused = ADMITTED[path.rsplit("/", 1)[1]]
        assert (r.status, r.json().get("refused")) == (status, refused), \
            f"a write the boundary admits was refused: {method} {path} with {sorted(headers)} answered {r.status}"


def _raw_write(c: Client, method: str, path: str, body: dict, lines: list) -> tuple[int, str | None, str]:
    """(status, refusal code, detail) of one write sent as raw bytes, its head and body in one send, so that a
    header can be sent on two lines, which the test client cannot do. It sends Host, the session cookie, each
    (name, value) of `lines` in order, and Content-Length."""
    data = json.dumps(body).encode("utf-8")
    head = [f"{method} {path} HTTP/1.0", f"Host: 127.0.0.1:{c.port}", f"Cookie: {c.cookie}"]
    head += [f"{name}: {value}" for name, value in lines] + [f"Content-Length: {len(data)}"]
    raw = _raw_request(c, ("\r\n".join(head) + "\r\n\r\n").encode("latin-1") + data)
    out = json.loads(raw.split(b"\r\n\r\n", 1)[1].decode("utf-8"))
    return int(raw.split(b" ", 2)[1]), out.get("refused"), out.get("detail", "")


def _refused_raw(c: Client, lines: list, status: int, code: str, detail: str, why: str) -> None:
    """Every write route refuses a raw write carrying `lines`, and the store's files are unchanged after."""
    before = files_digest(c.root)
    for method, path, body in _writes():
        got = _raw_write(c, method, path, body, lines)
        assert got == (status, code, detail), f"{why}: {method} {path} answered {got[0]} {got[1]}"
    assert files_digest(c.root) == before, f"{why}, and the write reached the store"


def _admitted_raw(c: Client, lines: list) -> None:
    """Every write route answers a raw write carrying `lines` as it does once the boundary admits it, so a raw
    write that a check sees refused is refused for the header it repeats and not for its shape."""
    for method, path, body in _writes():
        status, refused, _ = _raw_write(c, method, path, body, lines)
        assert (status, refused) == ADMITTED[path.rsplit("/", 1)[1]], \
            f"a raw write the boundary admits was refused: {method} {path} answered {status} {refused}"


JSON_TYPE = [("Content-Type", "application/json")]


def check_a_write_from_another_origin_is_refused(ctx):
    """A write is authorized by the page that sent it as well as by the session cookie (review finding 1). A page
    on another port of this host is the same site, so the browser attaches the cookie to that page's requests
    under SameSite=Strict, and its browser names this server in Host; its Origin names its own port. Every write
    here carries the valid cookie and an application/json body, so the Origin check alone stands between it and
    the store. The Origin must be exactly this server's own: one on another port, one with no port, as a page on
    port 80 of this host sends, one in another letter case and an empty one are refused, and so is an Origin sent
    on two lines, whether its first line or each of its lines is this server's own, because its lines are read as
    one value. A write from this server's own origin, under either spelling of its host, and a write carrying no
    Origin, as a command-line client sends, are admitted. The Origin is read before the body is parsed: a write from
    another port whose body is not JSON is refused as ORIGIN_REFUSED and not BODY_REFUSED. That it is read before
    any byte of the body is check_a_write_is_refused_before_its_body_arrives's to show."""
    c = _write_client(ctx)
    other = _other_port(c.port)
    own = f"http://127.0.0.1:{c.port}"
    for origin in (f"http://127.0.0.1:{other}", f"http://localhost:{other}", "http://127.0.0.1", "http://localhost",
                   "null", f"https://127.0.0.1:{c.port}", f"http://127.0.0.1:{c.port}/", f"HTTP://127.0.0.1:{c.port}",
                   "", "http://elsewhere.test"):
        _refused_unwritten(c, {"Origin": origin}, 403, "ORIGIN_REFUSED", "header: Origin",
                           "a write whose Origin is not exactly this server's own was not refused by the Origin check")
    for origin in (own, f"http://localhost:{c.port}"):
        _admitted(c, {"Origin": origin})
    _admitted(c, {})
    _admitted_raw(c, [("Origin", own)] + JSON_TYPE)
    for second in (f"http://127.0.0.1:{other}", "null"):
        _refused_raw(c, [("Origin", own), ("Origin", second)] + JSON_TYPE, 403, "ORIGIN_REFUSED", "header: Origin",
                     "a write whose Origin is sent on two lines, the first this server's own, was not refused by the "
                     "Origin check")
    _refused_raw(c, [("Origin", own), ("Origin", own)] + JSON_TYPE, 403, "ORIGIN_REFUSED", "header: Origin",
                 "a write whose Origin is sent on two lines, each this server's own, was not refused by the Origin "
                 "check, so one of its lines stood for the request")
    r = c.request("PUT", f"/api/kv/{CASE}/web", b"not json",
                  {"Cookie": c.cookie, "Content-Type": "application/json", "Origin": f"http://127.0.0.1:{other}"})
    out = r.json()
    assert (r.status, out.get("refused"), out.get("detail", "")) == (403, "ORIGIN_REFUSED", "header: Origin"), \
        f"the Origin check ran after the body was parsed: a write from another port answered {r.status} {out.get('refused')}"


def break_origin_check_removed(ctx):
    ctx.mp.setattr(server.Handler, "_check_origin", lambda self: None)


def break_origin_check_reads_the_host_only(ctx):
    """A weaker Origin check that compares the scheme and host and not the port, which is the gap a page on
    another loopback port uses."""
    def host_only(self):
        origin = self.headers.get("Origin")
        if origin is not None and not origin.startswith(("http://127.0.0.1:", "http://localhost:")):
            raise server.Refusal("ORIGIN_REFUSED", "header: Origin")

    ctx.mp.setattr(server.Handler, "_check_origin", host_only)


def break_origin_check_admits_port_80(ctx):
    """App.origins also names the origins of a page served on port 80 of this host, which carry no port."""
    real = server.App.origins
    ctx.mp.setattr(server.App, "origins", lambda self: real(self) | {"http://127.0.0.1", "http://localhost"})


def break_origin_compared_in_lower_case(ctx):
    def lowered(self):
        origin = self._header_value("Origin")
        if origin is not None and origin.lower() not in self.app.origins():
            raise server.Refusal("ORIGIN_REFUSED", "header: Origin")

    ctx.mp.setattr(server.Handler, "_check_origin", lowered)


def break_empty_origin_skipped(ctx):
    def skipping(self):
        origin = self._header_value("Origin")
        if origin and origin not in self.app.origins():
            raise server.Refusal("ORIGIN_REFUSED", "header: Origin")

    ctx.mp.setattr(server.Handler, "_check_origin", skipping)


def break_repeated_header_read_by_its_first_line(ctx):
    """The server reads a header sent on two lines by its first line, so an admissible first line stands for
    the request."""
    ctx.mp.setattr(server.Handler, "_header_value", lambda self, name: self.headers.get(name))


def break_repeated_header_read_by_its_last_line(ctx):
    """The server reads the headers into a dict keyed by the lower-case name, a plausible refactor, in which the
    last line of a repeated header wins, so an admissible last line stands for the request."""
    ctx.mp.setattr(server.Handler, "_header_value",
                   lambda self, name: {k.lower(): v for k, v in self.headers.items()}.get(name.lower()))


def break_page_checks_run_after_the_body_is_read(ctx):
    """The Origin and Sec-Fetch-Site checks run after the body is read, as they would if a change moved them below
    _read_body in _dispatch. Each still refuses, but only once the body of a write that another page sent has been
    read and parsed."""
    check_origin, check_fetch_site = server.Handler._check_origin, server.Handler._check_fetch_site
    read_body = server.Handler._read_body

    def read_then_check(self):
        body = read_body(self)
        check_origin(self)
        check_fetch_site(self)
        return body

    ctx.mp.setattr(server.Handler, "_check_origin", lambda self: None)
    ctx.mp.setattr(server.Handler, "_check_fetch_site", lambda self: None)
    ctx.mp.setattr(server.Handler, "_read_body", read_then_check)


def test_a_write_from_another_origin_is_refused(ctx):
    check_a_write_from_another_origin_is_refused(ctx)


def check_a_write_a_page_on_another_site_sent_is_refused(ctx):
    """Sec-Fetch-Site, which no page's script can set, says how the sending page relates to this one: same-site
    for a page on another port of this host, cross-site for one on another host. A write carrying any value but
    exactly same-origin, from this server's own page, or none, from the address bar, is refused, and so is one
    whose header is sent on two lines, whether its first line or each of its lines is same-origin. The header is
    read before the body is parsed: a same-site write whose body is not JSON is refused as ORIGIN_REFUSED and not
    BODY_REFUSED. No Origin header is sent here, so the Sec-Fetch-Site check stands alone (review finding 1)."""
    c = _write_client(ctx)
    for site in ("same-site", "cross-site", "Same-Origin", "same-origin ", ""):
        _refused_unwritten(c, {"Sec-Fetch-Site": site}, 403, "ORIGIN_REFUSED", "header: Sec-Fetch-Site",
                           "a write whose Sec-Fetch-Site is not exactly same-origin or none was not refused by the "
                           "Sec-Fetch-Site check")
    for site in ("same-origin", "none"):
        _admitted(c, {"Sec-Fetch-Site": site})
    _admitted_raw(c, [("Sec-Fetch-Site", "same-origin")] + JSON_TYPE)
    _refused_raw(c, [("Sec-Fetch-Site", "same-origin"), ("Sec-Fetch-Site", "cross-site")] + JSON_TYPE, 403,
                 "ORIGIN_REFUSED", "header: Sec-Fetch-Site",
                 "a write whose Sec-Fetch-Site is sent on two lines, the first same-origin, was not refused by the "
                 "Sec-Fetch-Site check")
    _refused_raw(c, [("Sec-Fetch-Site", "same-origin")] * 2 + JSON_TYPE, 403, "ORIGIN_REFUSED", "header: Sec-Fetch-Site",
                 "a write whose Sec-Fetch-Site is sent on two lines, each same-origin, was not refused by the "
                 "Sec-Fetch-Site check, so one of its lines stood for the request")
    r = c.request("PUT", f"/api/kv/{CASE}/web", b"not json",
                  {"Cookie": c.cookie, "Content-Type": "application/json", "Sec-Fetch-Site": "same-site"})
    out = r.json()
    assert (r.status, out.get("refused"), out.get("detail", "")) == (403, "ORIGIN_REFUSED", "header: Sec-Fetch-Site"), \
        f"the Sec-Fetch-Site check ran after the body was parsed: a same-site write answered {r.status} {out.get('refused')}"


def break_fetch_site_check_removed(ctx):
    ctx.mp.setattr(server.Handler, "_check_fetch_site", lambda self: None)


def break_fetch_site_read_by_prefix(ctx):
    def prefix(self):
        site = self._header_value("Sec-Fetch-Site")
        if site is not None and not site.startswith(server.WRITE_FETCH_SITES):
            raise server.Refusal("ORIGIN_REFUSED", "header: Sec-Fetch-Site")

    ctx.mp.setattr(server.Handler, "_check_fetch_site", prefix)


def test_a_write_a_page_on_another_site_sent_is_refused(ctx):
    check_a_write_a_page_on_another_site_sent_is_refused(ctx)


def check_a_write_that_is_not_json_is_refused_unread(ctx):
    """A page on another origin can send a POST whose body is text/plain, a form encoding or multipart, or carries
    no Content-Type, without a preflight, with the cookie attached, and a POST of application/json, or any PUT, only
    after a preflight, which this server refuses (OPTIONS answers METHOD_REFUSED). A write must therefore be
    application/json, alone or with charset=utf-8, and the type is read before the body is parsed: a JSON body sent
    as text/plain is refused, and a body that is not JSON at all is refused as CONTENT_TYPE_REFUSED and not
    BODY_REFUSED (review finding 1). Only spaces and tabs around the type's parts are ignored, as HTTP's optional
    whitespace, so a vertical tab, a unit separator, a form feed or a no-break space is refused, and so is a
    Content-Type sent on two lines, whether its first line or each of its lines is application/json. The refusal's
    rule says so and no more: it names multipart/form-data, and it says that only a POST goes without a preflight
    (the last reader's note 8 of 2026-11-15)."""
    c = _write_client(ctx)
    for content_type in ("text/plain", "text/plain;charset=UTF-8", "application/x-www-form-urlencoded",
                         "multipart/form-data; boundary=x", None, "application/jsonx", "application/json-patch+json",
                         "text/json", "application/json; charset=iso-8859-1", "application/json; profile=x",
                         "application/json\x0b", "application/json\x1f", "application/json\xa0",
                         "application/json; charset=utf-8\x0c"):
        _refused_unwritten(c, {"Content-Type": content_type}, 415, "CONTENT_TYPE_REFUSED", "",
                           "a write that is not application/json was not refused by the Content-Type check")
    r = c.request("PUT", f"/api/kv/{CASE}/web", b"not json", {"Cookie": c.cookie, "Content-Type": "text/plain"})
    assert (r.status, r.json().get("refused")) == (415, "CONTENT_TYPE_REFUSED"), "the Content-Type check ran after the body was parsed"
    for content_type in ("application/json", "application/json; charset=utf-8", 'Application/JSON;charset="UTF-8"',
                         "application/json \t; \tcharset=utf-8 "):
        _admitted(c, {"Content-Type": content_type})
    _admitted_raw(c, JSON_TYPE)
    _refused_raw(c, JSON_TYPE + [("Content-Type", "text/plain")], 415, "CONTENT_TYPE_REFUSED", "",
                 "a write whose Content-Type is sent on two lines, the first application/json, was not refused by "
                 "the Content-Type check")
    _refused_raw(c, JSON_TYPE * 2, 415, "CONTENT_TYPE_REFUSED", "",
                 "a write whose Content-Type is sent on two lines, each application/json, was not refused by the "
                 "Content-Type check, so one of its lines stood for the request")
    rule = c.send("PUT", f"/api/kv/{CASE}/web", {"hops": 2}, headers={"Content-Type": "text/plain"}).json()["rule"]
    assert "multipart/form-data" in rule and "a POST" in rule and "any PUT" in rule, \
        "CONTENT_TYPE_REFUSED's rule leaves out multipart, or does not say that only a POST goes without a preflight"


#: CONTENT_TYPE_REFUSED's rule before the last reader's note 8 of 2026-11-15 corrected it: it left out multipart,
#: and it spoke of any write, where a PUT always needs a preflight.
CONTENT_TYPE_RULE_BEFORE = ("docs/PLAINSIGHT-design.md amendment 9.27: a page on another origin needs no preflight to "
                            "send a body as text/plain, as a form encoding or with no Content-Type, and needs one to "
                            "send application/json, which this server refuses, so a write carries application/json")


def break_content_type_rule_as_before(ctx):
    import dataclasses

    from app import refusals

    ctx.mp.setitem(refusals.REFUSALS, "CONTENT_TYPE_REFUSED",
                   dataclasses.replace(refusals.REFUSALS["CONTENT_TYPE_REFUSED"], rule=CONTENT_TYPE_RULE_BEFORE))


def break_content_type_check_removed(ctx):
    ctx.mp.setattr(server.Handler, "_check_content_type", lambda self: None)


def break_content_type_read_by_prefix(ctx):
    ctx.mp.setattr(server, "json_content_type", lambda value: isinstance(value, str) and value.lower().startswith("application/json"))


def break_content_type_stripped_by_str_strip(ctx):
    """json_content_type with str.strip() and no argument, which also removes characters that are not HTTP
    whitespace, such as a vertical tab or a no-break space."""
    def stripping(value):
        if not isinstance(value, str):
            return False
        media, _, params = value.partition(";")
        if media.strip().lower() != "application/json":
            return False
        params = params.strip()
        if not params:
            return True
        name, eq, charset = params.partition("=")
        return bool(eq) and name.strip().lower() == "charset" and charset.strip().strip('"').lower() == "utf-8"

    ctx.mp.setattr(server, "json_content_type", stripping)


def test_a_write_that_is_not_json_is_refused_unread(ctx):
    check_a_write_that_is_not_json_is_refused_unread(ctx)


#: HOST_REFUSED's rule before review finding 6 corrected it. It said the Host check keeps a page served from
#: another origin from reading the server, which, for a page that names this server in Host, the browser's
#: same-origin policy does.
HOST_RULE_BEFORE = ("docs/PLAINSIGHT-design.md amendment 9.12: the server answers its own loopback origin only, so "
                    "a page served from another origin cannot read it")


def check_the_host_check_refuses_another_name_or_port(ctx):
    """Every request must name this server in Host, exactly 127.0.0.1 or localhost with the bound port. A host name
    that a DNS rebinding points at this loopback arrives under its own name and is refused, on a read and on a
    write that carries the valid cookie, and nothing is written; so is another port, no port, and another letter
    case. The refusal's text says so and claims no more: a page on another origin names this server in Host and
    passes (review findings 3 and 6). The test client replaces its own Host with one given in lower case, so this
    check sends the request it names: a Host naming this server, given in lower case, is answered, where a client
    that sent its own Host beside it would send two Host lines, which the server refuses."""
    c = _write_client(ctx)
    other = _other_port(c.port)
    before = files_digest(c.root)
    for host in ("elsewhere.test", f"rebound.test:{c.port}", f"127.0.0.1:{other}", f"localhost:{other}", "127.0.0.1",
                 f"127.0.0.2:{c.port}", f"LOCALHOST:{c.port}", ""):
        r = c.get("/api/cases", {"Host": host})
        assert (r.status, r.json().get("refused")) == (403, "HOST_REFUSED"), \
            "a read whose Host is not exactly this server's was not refused by the Host check"
        for method, path, body in _writes():
            # One send holding the head and the body, with a Host the test client would not send as given. A body
            # that comes after the answer is read and discarded, which the late-body check below reads.
            data = json.dumps(body).encode("utf-8")
            raw = _raw_request(c, f"{method} {path} HTTP/1.0\r\nHost: {host}\r\nCookie: {c.cookie}\r\nContent-Type: "
                                  f"application/json\r\nContent-Length: {len(data)}\r\n\r\n".encode("ascii") + data)
            assert raw.startswith(b"HTTP/1.0 403") and _refused_code(raw) == "HOST_REFUSED", \
                "a write whose Host is not exactly this server's was not refused by the Host check"
    assert _refused_code(_raw_request(c, b"GET /api/cases HTTP/1.0\r\n\r\n")) == "HOST_REFUSED", \
        "a request with no Host header was not refused by the Host check"
    r = c.get("/api/cases", {"host": f"127.0.0.1:{c.port}"})
    assert r.status == 200, \
        "the test client sent its own Host beside one given in lower case, so this check sent a request other than the one it names"
    assert files_digest(c.root) == before, "a write naming another host reached the store"
    for host in (f"127.0.0.1:{c.port}", f"localhost:{c.port}"):
        assert c.get("/api/cases", {"Host": host}).status == 200, "a read naming this server was refused"
    rule = c.get("/api/cases", {"Host": "elsewhere.test"}).json()["rule"]
    assert "DNS rebinding" in rule and "passes this check" in rule and "cannot read it" not in rule, \
        "HOST_REFUSED's text claims more than the Host check does"


def break_host_check_removed(ctx):
    ctx.mp.setattr(server.Handler, "_check_host", lambda self: None)


def break_host_compared_in_any_case(ctx):
    def any_case(self):
        if (self.headers.get("Host") or "").lower() not in self.app.authorities():
            raise server.Refusal("HOST_REFUSED")

    ctx.mp.setattr(server.Handler, "_check_host", any_case)


def break_client_merges_headers_by_exact_name(ctx):
    """A test client that merges headers by their exact name: a header given in another letter case is sent
    beside the client's own, and the server reads the client's own."""
    ctx.mp.setattr(served, "merge_headers", lambda defaults, given: {**defaults, **(given or {})})


def break_host_refusal_claims_a_cross_origin_read(ctx):
    import dataclasses

    from app import refusals

    ctx.mp.setitem(refusals.REFUSALS, "HOST_REFUSED", dataclasses.replace(refusals.REFUSALS["HOST_REFUSED"], rule=HOST_RULE_BEFORE))


def test_the_host_check_refuses_another_name_or_port(ctx):
    check_the_host_check_refuses_another_name_or_port(ctx)


def check_a_write_needs_the_launch_token(ctx):
    """Every POST and PUT carries this launch's token in the session cookie, under the name that carries the
    bound port. A write from this server's own origin with no cookie, a wrong token, the token under the
    unqualified name, or a cookie header that does not parse is refused, and nothing is written (review
    finding 3). So is the token followed by a character outside ASCII in a quoted value: the server compared the
    value as a string, which hmac.compare_digest refuses with a TypeError for such a character, and answered
    SERVER_FAULT (the second reader's should-fix 4 of 2026-11-16). The token is read before the body is parsed: a
    write with no cookie whose body is not JSON is refused as TOKEN_REFUSED and not BODY_REFUSED."""
    c = _write_client(ctx)
    name, token = c.app.cookie_name(), c.app.token
    own = {"Origin": f"http://127.0.0.1:{c.port}", "Sec-Fetch-Site": "same-origin"}
    for cookie in (None, f"{name}={token[::-1]}", f"{name}={token[:-1]}", f"{server.COOKIE}={token}", f'{name}="{token}', "=;=;",
                   f'{name}="{token}\u00e9"'):
        _refused_unwritten(c, dict(own, Cookie=cookie), 403, "TOKEN_REFUSED", "",
                           "a write without this launch's token was not refused by the token check")
    _admitted(c, own)
    r = c.request("PUT", f"/api/kv/{CASE}/web", b"not json", dict(own))
    assert (r.status, r.json().get("refused")) == (403, "TOKEN_REFUSED"), \
        f"the token check ran after the body was parsed: a write with no cookie answered {r.status} {r.json().get('refused')}"


def break_token_check_removed(ctx):
    ctx.mp.setattr(server.Handler, "_check_token", lambda self: None)


def break_token_checked_after_the_body_is_read(ctx):
    """The token check runs after the body is read, as it would if a change moved it below _read_body in
    _dispatch. A write without the token is still refused, but only once its body has been read and parsed."""
    check_token, read_body = server.Handler._check_token, server.Handler._read_body

    def read_then_check(self):
        body = read_body(self)
        check_token(self)
        return body

    ctx.mp.setattr(server.Handler, "_check_token", lambda self: None)
    ctx.mp.setattr(server.Handler, "_read_body", read_then_check)


def break_token_compared_as_text(ctx):
    """The token compared as text, as it was before the second reader's should-fix 4 of 2026-11-16, so a cookie
    value holding a character outside ASCII raises a TypeError in hmac.compare_digest and is answered SERVER_FAULT."""
    import hmac

    real = hmac.compare_digest

    class AsText:
        @staticmethod
        def compare_digest(a, b):
            return real(*(x.decode("utf-8") if isinstance(x, bytes) else x for x in (a, b)))

    ctx.mp.setattr(server, "hmac", AsText)


def test_a_write_needs_the_launch_token(ctx):
    check_a_write_needs_the_launch_token(ctx)


def check_the_session_cookie_carries_its_attributes(ctx):
    """The server sets the session cookie on the page's response as <name>=<token>; HttpOnly; SameSite=Strict;
    Path=/, under the name that carries the bound port. HttpOnly keeps the token from the page's script,
    SameSite=Strict keeps a page on another site from sending it, and Path=/ sends it to the write routes from a
    page under /c/ (review finding 3)."""
    c = Client(ctx)
    for page in ("/", f"/c/{CASE}/dossier"):
        parts = [p.strip() for p in c.get(page).header("Set-Cookie").split(";")]
        name, _, value = parts[0].partition("=")
        assert (name, value) == (f"{server.COOKIE}_{c.port}", c.app.token), "the session cookie does not carry this launch's token under its port's name"
        attrs = {}
        for p in parts[1:]:
            k, eq, v = p.partition("=")
            attrs[k.strip().lower()] = v.strip() if eq else True
        assert attrs.get("httponly") is True, "the session cookie lacks HttpOnly, so the page's script could read the token"
        assert attrs.get("samesite") == "Strict", "the session cookie is not SameSite=Strict, so a page on another site could send it"
        assert attrs.get("path") == "/", "the session cookie is not set for Path=/, so a page under /c/ would not send it to the write routes"


def break_cookie_without_http_only(ctx):
    ctx.mp.setattr(server.App, "cookie", lambda self: f"{self.cookie_name()}={self.token}; SameSite=Strict; Path=/")


def break_cookie_same_site_lax(ctx):
    ctx.mp.setattr(server.App, "cookie", lambda self: f"{self.cookie_name()}={self.token}; HttpOnly; SameSite=Lax; Path=/")


def break_cookie_for_another_path(ctx):
    ctx.mp.setattr(server.App, "cookie", lambda self: f"{self.cookie_name()}={self.token}; HttpOnly; SameSite=Strict; Path=/c")


def test_the_session_cookie_carries_its_attributes(ctx):
    check_the_session_cookie_carries_its_attributes(ctx)


def check_two_launches_keep_their_own_cookie(ctx):
    """A browser keeps one cookie per name for a host whatever its port (RFC 6265 section 8.5), so two launches on
    127.0.0.1 share one jar. The cookie's name carries the port, so the second launch's page does not overwrite
    the first launch's token, and both pages still write (review finding 4). The jar here holds one value per
    name, as a browser's does for one host and path."""
    first, second = Client(ctx), Client(ctx, corpus_copy(ctx, "second"))
    jar: dict[str, str] = {}
    for c in (first, second):
        name, _, value = c.get("/").header("Set-Cookie").split(";", 1)[0].partition("=")
        jar[name] = value
    sent = "; ".join(f"{k}={v}" for k, v in jar.items())
    for c in (first, second):
        r = c.request("PUT", f"/api/kv/{CASE}/web", b'{"hops": 2}', {"Cookie": sent})
        assert r.status == 200, "a second launch on this host overwrote the first launch's session cookie, so its page is refused every write"


def break_one_cookie_name(ctx):
    ctx.mp.setattr(server.App, "cookie_name", lambda self: server.COOKIE)


def test_two_launches_keep_their_own_cookie(ctx):
    check_two_launches_keep_their_own_cookie(ctx)


def check_an_exception_outside_dispatch_prints_no_traceback(ctx):
    """An exception raised outside _dispatch reaches the server's handle_error, whose stdlib default prints a
    traceback, the exception's message included, to stderr. The server logs the type name only (review finding
    7). Here the handler's setup raises with a held value in its message, and neither stderr nor the log
    carries it."""
    import io
    import sys
    import time

    c = Client(ctx)
    value = named(corpus_events(), "extract-claim-handle")["payload"]["value"]
    err = io.StringIO()
    ctx.mp.setattr(sys, "stderr", err)
    real = server.Handler.setup

    def failing(self):
        real(self)
        raise RuntimeError(f"a fault outside the dispatcher, carrying {value}")

    ctx.mp.setattr(server.Handler, "setup", failing)
    try:
        c.get("/api/cases")
    except OSError:
        pass
    end = time.monotonic() + 5
    while time.monotonic() < end and not err.getvalue() and not [line for line in c.logs if line[-1] == "RuntimeError"]:
        time.sleep(0.05)
    printed = err.getvalue()
    assert value not in printed and "Traceback" not in printed, "an exception outside the dispatcher printed a traceback to stderr"
    faults = [line[1:] for line in c.logs if line[-1] == "RuntimeError"]
    assert faults == [("-", "outside dispatch", "-", "-", "RuntimeError")], "an exception outside the dispatcher was not logged by its type name"
    assert value not in json.dumps(c.logs), "an exception's message reached the log"


def break_default_handle_error(ctx):
    ctx.mp.delattr(server.Server, "handle_error")


def test_an_exception_outside_dispatch_prints_no_traceback(ctx):
    check_an_exception_outside_dispatch_prints_no_traceback(ctx)


# ---------------------------------------------------------------------------
# a refused write's body, a header sent on two lines, and the listening socket
# (amendment 9.27 as reworked on 2026-11-16)
# ---------------------------------------------------------------------------


def _refusing(c: Client) -> list[tuple[dict, tuple[int, str, str]]]:
    """For each write rule, a header that breaks it and the answer the refusal brings."""
    return [
        ({"Origin": f"http://127.0.0.1:{_other_port(c.port)}"}, (403, "ORIGIN_REFUSED", "header: Origin")),
        ({"Sec-Fetch-Site": "same-site"}, (403, "ORIGIN_REFUSED", "header: Sec-Fetch-Site")),
        ({"Cookie": None}, (403, "TOKEN_REFUSED", "")),
        ({"Content-Type": "text/plain"}, (415, "CONTENT_TYPE_REFUSED", "")),
    ]


def _head(c: Client, method: str, path: str, headers: dict, length: int) -> bytes:
    """A write's head as raw bytes: Host, the session cookie and application/json, each replaced by the header of
    `headers` that names it and left out where that header is None, then the rest of `headers`, then a
    Content-Length of `length`."""
    sent = served.merge_headers({"Host": f"127.0.0.1:{c.port}", "Cookie": c.cookie, "Content-Type": "application/json"},
                                headers)
    lines = [f"{method} {path} HTTP/1.0"] + [f"{k}: {v}" for k, v in sent.items() if v is not None]
    return ("\r\n".join(lines + [f"Content-Length: {length}"]) + "\r\n\r\n").encode("latin-1")


def _answer(raw: bytes) -> tuple[int, str | None, str]:
    """(status, refusal code, detail) of a raw answer, with a status of 0 when no status line was read."""
    head, _, body = raw.partition(b"\r\n\r\n")
    if not head.startswith(b"HTTP/"):
        return 0, None, ""
    out = json.loads(body.decode("utf-8")) if body else {}
    return int(head.split(b" ", 2)[1]), out.get("refused"), out.get("detail", "")


def _read_to_end(sock: socket.socket) -> bytes:
    out = b""
    while True:
        chunk = sock.recv(65536)
        if not chunk:
            return out
        out += chunk


def _late_body(c: Client, head: bytes, body: bytes, delay: float) -> tuple[tuple[int, str | None, str], int]:
    """(the answer, the socket's pending error once the answer is read to its end) for a write sent as its head
    and, `delay` seconds later, its body, as a client whose body arrives late sends it. A connection that fails
    before the answer is read raises an AssertionError, so a control sees the check fail rather than error."""
    sock = c.connect()
    try:
        sock.sendall(head)
        time.sleep(delay)
        sock.sendall(body)
        time.sleep(0.1)
        got = _answer(_read_to_end(sock))
        return got, sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
    except OSError as exc:
        raise AssertionError(f"the connection failed before the answer was read ({type(exc).__name__})") from exc
    finally:
        sock.close()


def check_a_refusal_reaches_a_client_whose_body_arrives_late(ctx):
    """A refused write is answered before its body is read, and the client may still be sending that body:
    http.client sends a head and its body in two sends, and amendment 9.27 records how often the body reached the
    server after the head had been read. The server stops sending after its answer, and reads and discards the
    body, never parsing it, before it closes. A server that closed at once met the late body with a reset: with
    the test client's body 50 ms late, the last reader of 2026-11-15 saw all four write checks fail with
    ConnectionAbortedError on Windows, whose stack drops an answer it has received when a reset arrives, while a
    Linux client reads the answer and keeps the reset as the socket's pending error. So each refusal here is sent
    with its body 50 ms late on every write route, and 200 ms late as a body of MAX_BODY bytes that is not JSON,
    and its answer must be read whole with no pending error. Every answer written before a declared body is read
    is followed by the discard, not the four write rules' answers alone, so a write the Host check refuses, before
    any route is matched, is sent the same way, and so is one refused as BODY_REFUSED and answered 400 for a head
    that declares MAX_BODY + 1 bytes, its body a write's JSON 50 ms late (the second reader's should-fix 2 of
    2026-11-16). Nothing is written, and no line logs a fault."""
    c = _write_client(ctx)
    before = files_digest(c.root)
    host = ({"Host": f"127.0.0.1:{_other_port(c.port)}"}, (403, "HOST_REFUSED", ""))
    for headers, want in _refusing(c) + [host]:
        cases = [(method, path, json.dumps(body).encode("utf-8"), 0.05) for method, path, body in _writes()]
        cases.append(("PUT", f"/api/kv/{CASE}/web", b"x" * server.MAX_BODY, 0.2))
        for method, path, data, delay in cases:
            got, error = _late_body(c, _head(c, method, path, headers, len(data)), data, delay)
            assert got == want, f"a refused write whose body came {delay} s late was answered {got}, not {want}: {method} {path}"
            assert error == 0, \
                f"a refused write whose body came {delay} s late left the connection reset (socket error {error}): {method} {path}"
    too_long = (400, "BODY_REFUSED", "a body needs one Content-Length header of at most 8192 bytes")
    for method, path, body in _writes():
        data = json.dumps(body).encode("utf-8")
        got, error = _late_body(c, _head(c, method, path, {}, server.MAX_BODY + 1), data, 0.05)
        assert got == too_long, \
            f"a write that declared {server.MAX_BODY + 1} bytes, its body 50 ms late, was answered {got}, not {too_long}: {method} {path}"
        assert error == 0, \
            f"a write refused for its length, its body 50 ms late, left the connection reset (socket error {error}): {method} {path}"
    assert files_digest(c.root) == before, "a refused write whose body came late reached the store"
    assert [r for r in c.logs if len(r) > 5] == [], "a refused write's discarded body faulted the server"


def _discard_as(*, cap: bool = True, deadline: bool = True, half_close: bool = True, guard: bool = True,
                read_timeout: bool = True, end_of_stream: bool = True, stretch: float = 1.0):
    """The server's discard, written again here with one of its parts left out for the breakers below: its byte
    bound, its deadline, its half-close, its guard on a body already read, the timeout on each read, which alone
    bounds a client that sends nothing, or its stop at the end of the stream; or with its deadline set at
    `stretch` times DISCARD_SECONDS."""
    def discard(self):
        if guard and self._body_read:
            return
        length = self._header_value("Content-Length")
        if not routes.ascii_digits(length):
            return
        left = min(int(length), server.MAX_BODY) if cap else int(length)
        try:
            if half_close:
                self.connection.shutdown(socket.SHUT_WR)
            end = time.monotonic() + stretch * server.DISCARD_SECONDS
            while left > 0 and (not deadline or time.monotonic() < end):
                timed = deadline and read_timeout
                self.connection.settimeout(max(end - time.monotonic(), 0.001) if timed else None)
                chunk = self.rfile.read1(left)
                if not chunk:
                    if end_of_stream:
                        break
                    time.sleep(0.01)
                left -= len(chunk)
        except OSError:
            pass

    return discard


def break_refused_write_closed_at_once(ctx):
    """The close the change made before 2026-11-16: the answer is written, and the connection closes with the
    body unread."""
    ctx.mp.setattr(server.Handler, "_discard_unread_body", lambda self: None)


def break_discard_kept_to_the_write_rules(ctx):
    """The discard run only after a refusal by one of the four write rules, so a Host refusal and BODY_REFUSED for
    a length close at once with the body on its way. The second reader's mutant 1 of 2026-11-16, a discard that
    returned when no route had matched or the status was 400, did as much and left test_http.py green."""
    real = server.Handler._discard_unread_body

    def flagged(check):
        def run(self):
            try:
                check(self)
            except server.Refusal:
                self._write_rule_refused = True
                raise

        return run

    for name in ("_check_origin", "_check_fetch_site", "_check_token", "_check_content_type"):
        ctx.mp.setattr(server.Handler, name, flagged(getattr(server.Handler, name)))

    def discard(self):
        if getattr(self, "_write_rule_refused", False):
            real(self)

    ctx.mp.setattr(server.Handler, "_discard_unread_body", discard)


def test_a_refusal_reaches_a_client_whose_body_arrives_late(ctx):
    check_a_refusal_reaches_a_client_whose_body_arrives_late(ctx)


#: How long a client waits for the answer to a write whose body never comes, in seconds. The server answers a
#: refused write in milliseconds; one that read the body first would not answer here at all, since no body comes.
REFUSAL_WAIT = 3.0


def _answer_without_body(c: Client, head: bytes) -> tuple[int, str | None, str]:
    """The answer to a write head that declares a body and is followed by none, read to its end within
    REFUSAL_WAIT. A wait past it raises an AssertionError, so a control sees the check fail rather than error,
    and says whether any of the answer had come."""
    sock = c.connect()
    sock.settimeout(REFUSAL_WAIT)
    out = b""
    try:
        sock.sendall(head)
        while True:
            chunk = sock.recv(65536)
            if not chunk:
                return _answer(out)
            out += chunk
    except OSError as exc:
        why = ("the server did not mark the answer's end" if out
               else "no answer came, so the server read the body before it answered")
        raise AssertionError(f"no whole answer within {REFUSAL_WAIT} s to a write that declared a body and sent none "
                             f"({type(exc).__name__}): {why}") from exc
    finally:
        sock.close()


def check_a_write_is_refused_before_its_body_arrives(ctx):
    """Each write rule is decided, and its refusal written, before any byte of the body is read, and the server
    then half-closes. The checks above show that a rule runs before the body is parsed; a server that read the
    whole body off the socket first, and parsed it after the rules, passes every one of them, as the last reader
    of 2026-11-15 showed (its should-fix 2). Here each refused write declares 100 bytes of body and sends none, so
    a server that read the body before it answered would wait for it, and the answer must arrive whole within
    REFUSAL_WAIT, its end marked by the server's half-close. The discard deadline is set far past the wait, so a
    server that discarded the body before it answered, or answered without the half-close that ends the client's
    read, would hold the client past the wait as well. Each client closes once it has read the answer, and every
    discard must end at that close, counted from the server's side, where one that went on reading a closed
    stream would spin until the deadline."""
    ctx.mp.setattr(server, "DISCARD_SECONDS", 60.0)
    c = _write_client(ctx)
    ended = []
    real_discard = server.Handler._discard_unread_body

    def counted(self):
        try:
            real_discard(self)
        finally:
            ended.append(True)

    ctx.mp.setattr(server.Handler, "_discard_unread_body", counted)
    sent = 0
    for headers, want in _refusing(c):
        for method, path, _ in _writes():
            got = _answer_without_body(c, _head(c, method, path, headers, 100))
            sent += 1
            assert got == want, f"a refused write that declared a body and sent none was answered {got}, not {want}: {method} {path}"
    until = time.monotonic() + 2.0
    while len(ended) < sent and time.monotonic() < until:
        time.sleep(0.05)
    assert len(ended) == sent, \
        f"{sent - len(ended)} of {sent} discards went on after their client closed, so a closed stream is read until the deadline"


def break_body_read_before_the_checks(ctx):
    """The last reader's mutant of 2026-11-15: the whole body is read off the socket before the four write checks
    run, and parsed only after them, so each check still refuses before the body is parsed."""
    check_origin, read_body = server.Handler._check_origin, server.Handler._read_body

    def read_then_check(self):
        length = self.headers.get("Content-Length")
        fits = routes.ascii_digits(length, 5) and int(length) <= server.MAX_BODY
        self._early = self.rfile.read(int(length)) if fits else None
        check_origin(self)

    def parse_early(self):
        if getattr(self, "_early", None) is None:
            return read_body(self)
        self._body_read = True
        try:
            return json.loads(self._early.decode("utf-8"))
        except (UnicodeDecodeError, ValueError):
            raise server.Refusal("BODY_REFUSED", "the body is not JSON") from None

    ctx.mp.setattr(server.Handler, "_check_origin", read_then_check)
    ctx.mp.setattr(server.Handler, "_read_body", parse_early)


def break_discard_reads_on_after_the_close(ctx):
    """A discard that does not stop at the end of the stream, so a client that closed leaves it reading empty reads
    until the deadline, as the battery's mutant M35 does; this one pauses 10 ms between empty reads, where M35 spins,
    so the breaker holds no processor while the suite goes on."""
    ctx.mp.setattr(server.Handler, "_discard_unread_body", _discard_as(end_of_stream=False))


def break_answer_without_the_half_close(ctx):
    """The discard without its half-close: the server reads the body after its answer and never marks the answer's
    end, so a client that reads to the end waits for the discard's deadline."""
    ctx.mp.setattr(server.Handler, "_discard_unread_body", _discard_as(half_close=False))


def test_a_write_is_refused_before_its_body_arrives(ctx):
    check_a_write_is_refused_before_its_body_arrives(ctx)


#: The seconds past DISCARD_SECONDS a client may wait to see the close: two of its sends, one that meets the
#: closed connection and one that fails, with room for a loaded machine.
CLOSE_MARGIN = 2.0

#: The seconds past DISCARD_SECONDS a discard may run, timed from the server's side, where no send of the client's
#: has to meet the close first: the last read's timeout ends at the deadline, and the margin is room for a loaded
#: machine. The second reader measured 1.001 to 1.015 s for a client that sent nothing (its should-fix 3 of
#: 2026-11-16).
DEADLINE_MARGIN = 0.5


def _sends_until_closed(sock: socket.socket, chunk: bytes, every: float, within: float) -> float | None:
    """Send `chunk` each `every` seconds until a send fails, and return the seconds until it failed, or None when
    none failed within `within` seconds. A send fails once the server has closed and its reset has come back."""
    t0 = time.monotonic()
    while time.monotonic() - t0 < within:
        try:
            sock.sendall(chunk)
        except OSError:
            return time.monotonic() - t0
        time.sleep(every)
    return None


def _answer_then_sends(c: Client, head: bytes, chunk: bytes, every: float, within: float) -> tuple[tuple, float | None]:
    """(the answer, the seconds until a send failed) for a write that keeps sending after its answer."""
    sock = c.connect()
    try:
        sock.sendall(head)
        got = _answer(_read_to_end(sock))
        return got, _sends_until_closed(sock, chunk, every, within)
    except OSError as exc:
        raise AssertionError(f"the connection failed before the answer was read ({type(exc).__name__})") from exc
    finally:
        sock.close()


def check_a_refused_writes_body_is_discarded_within_its_bounds(ctx):
    """The discard is bounded in bytes and in time, and its deadline is the one second amendment 9.27 states. A
    client that declares 65536 bytes, sends MAX_BODY of them with its head and then keeps sending finds the
    connection closed once MAX_BODY bytes are read, with the deadline set far off. A client that declares 100
    bytes and never finishes them, sending one each 200 ms, finds it closed at the deadline: not before it, and
    within CLOSE_MARGIN after it. Each sees the close as a send that fails. A discard with no byte bound reads on
    to the declared length or the deadline, and one with no deadline reads until the declared length comes, some
    twenty seconds on here. A client that resets the connection while the server waits for its body ends the
    discard, and no line logs a fault. A client that sends nothing after its head, and keeps the connection open,
    sees no close it could read, so that discard is timed from the server's side: it must end within
    DEADLINE_MARGIN of the deadline, where a read with no timeout would wait for the client, and a deadline longer
    than DISCARD_SECONDS would hold the thread past the one second, which the client's side, waiting CLOSE_MARGIN
    for a send to fail, does not see (the second reader's should-fix 3 of 2026-11-16). An admitted write, whose
    body the server read, is closed at once after its answer: with the deadline set far off again, a client that
    keeps sending one byte each 50 ms after a body of some 8 KiB finds the connection closed within a second, where
    a discard run on a body already read would hold it open for the deadline."""
    assert server.DISCARD_SECONDS == 1.0, "the discard deadline is not the one second amendment 9.27 states"
    shipped = server.DISCARD_SECONDS
    c = _write_client(ctx)
    headers, want = _refusing(c)[0]
    path = f"/api/kv/{CASE}/web"
    ctx.mp.setattr(server, "DISCARD_SECONDS", 60.0)
    got, took = _answer_then_sends(c, _head(c, "PUT", path, headers, 65536) + b"x" * server.MAX_BODY, b"x" * 64, 0.05, 3.0)
    assert got == want, f"a write that declared more than MAX_BODY bytes was answered {got}, not {want}"
    assert took is not None, "a client that sent past MAX_BODY found the connection open 3 s on, so the discard read past its byte bound"
    ctx.mp.setattr(server, "DISCARD_SECONDS", shipped)
    got, took = _answer_then_sends(c, _head(c, "PUT", path, headers, 100) + b"x", b"x", 0.2, shipped + CLOSE_MARGIN)
    assert got == want, f"a write that declared 100 bytes was answered {got}, not {want}"
    assert took is not None, \
        f"a client that never finished its body found the connection open {shipped + CLOSE_MARGIN} s on, so the discard has no deadline"
    assert took >= shipped - 0.05, f"the connection closed {took:.2f} s after the answer, before the discard's deadline"
    sock = c.connect()
    try:
        sock.sendall(_head(c, "PUT", path, headers, 100))
        got = _answer(_read_to_end(sock))
        linger = struct.pack("HH" if sys.platform == "win32" else "ii", 1, 0)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, linger)
    finally:
        sock.close()
    assert got == want, f"a write that declared 100 bytes was answered {got}, not {want}"
    time.sleep(0.5)
    assert [r for r in c.logs if len(r) > 5] == [], "a client that reset the connection during the discard faulted the server"
    took_server = []
    real_discard = server.Handler._discard_unread_body

    def timed(self):
        t0 = time.monotonic()
        try:
            real_discard(self)
        finally:
            took_server.append(time.monotonic() - t0)

    ctx.mp.setattr(server.Handler, "_discard_unread_body", timed)
    sock = c.connect()
    try:
        sock.sendall(_head(c, "PUT", path, headers, 100))
        got = _answer(_read_to_end(sock))
        until = time.monotonic() + shipped + CLOSE_MARGIN
        while not took_server and time.monotonic() < until:
            time.sleep(0.05)
        ended = bool(took_server)
    finally:
        sock.close()
    assert got == want, f"a write that declared 100 bytes was answered {got}, not {want}"
    assert ended, \
        f"a client that sent nothing after its head held the discard open {shipped + CLOSE_MARGIN} s on, so it waits with no deadline"
    assert took_server[0] <= shipped + DEADLINE_MARGIN, \
        (f"the discard for a client that sent nothing after its head ran {took_server[0]:.2f} s, more than "
         f"{DEADLINE_MARGIN} s past DISCARD_SECONDS, so its deadline is longer than the {shipped} s amendment 9.27 states")
    ctx.mp.setattr(server.Handler, "_discard_unread_body", real_discard)
    ctx.mp.setattr(server, "DISCARD_SECONDS", 60.0)
    data = (json.dumps({"hops": 2}) + " " * 8000).encode("utf-8")
    got, took = _answer_then_sends(c, _head(c, "PUT", path, {}, len(data)) + data, b"x", 0.05, 3.0)
    assert got[:2] == (200, None), f"a write the boundary admits was answered {got}"
    assert took is not None and took < 1.0, \
        "an admitted write's connection stayed open after its answer, so the discard ran on a body the server had read"


def break_discard_reads_past_the_cap(ctx):
    """A discard bounded by the declared Content-Length alone."""
    ctx.mp.setattr(server.Handler, "_discard_unread_body", _discard_as(cap=False))


def break_discard_waits_without_a_deadline(ctx):
    """A discard that waits for the declared body however long it takes."""
    ctx.mp.setattr(server.Handler, "_discard_unread_body", _discard_as(deadline=False))


def break_discard_reads_with_no_timeout(ctx):
    """A discard whose reads carry no timeout, so its deadline is read only between reads, and a client that sends
    nothing holds it: the battery's mutant M20."""
    ctx.mp.setattr(server.Handler, "_discard_unread_body", _discard_as(read_timeout=False))


def break_discard_waits_twice_its_deadline(ctx):
    """A discard whose deadline is twice DISCARD_SECONDS, the second reader's surviving mutant of 2026-11-16: a client
    that waits CLOSE_MARGIN past the deadline for a send to fail sees the close in time."""
    ctx.mp.setattr(server.Handler, "_discard_unread_body", _discard_as(stretch=2.0))


def break_discard_runs_after_a_read_body(ctx):
    """A discard that runs after every answer, a body the server read included, which the battery's mutant M16
    showed no other check would see."""
    ctx.mp.setattr(server.Handler, "_discard_unread_body", _discard_as(guard=False))


def test_a_refused_writes_body_is_discarded_within_its_bounds(ctx):
    check_a_refused_writes_body_is_discarded_within_its_bounds(ctx)


def _raw_lines(c: Client, method: str, path: str, lines: list, data: bytes = b"") -> tuple[int, str | None, str]:
    """(status, refusal code, detail) of one request sent as raw bytes in one send, with exactly the header lines
    `lines` gives, in order, and `data` after the head."""
    head = [f"{method} {path} HTTP/1.0"] + [f"{name}: {value}" for name, value in lines]
    return _answer(_raw_request(c, ("\r\n".join(head) + "\r\n\r\n").encode("latin-1") + data))


def check_a_repeated_host_cookie_or_content_length_stands_for_no_request(ctx):
    """Host, Cookie and Content-Length are read as Origin is: one sent on two lines stands for no request, whichever
    line the server would read, even when each line is admissible. Two Host lines that each name this server are
    refused as HOST_REFUSED, on a read and on every write route; a write whose two Cookie lines each carry the
    token is refused as TOKEN_REFUSED; and a write whose two Content-Length lines each give its body's length is
    refused as BODY_REFUSED. Nothing is written. The same requests with each header on one line are admitted, so
    each refusal is the repetition's."""
    c = _write_client(ctx)
    host, cookie = ("Host", f"127.0.0.1:{c.port}"), ("Cookie", c.cookie)
    assert _raw_lines(c, "GET", "/api/cases", [host])[0] == 200, "a read with one Host line was refused"
    for method, path, body in _writes():
        data = json.dumps(body).encode("utf-8")
        got = _raw_lines(c, method, path, [host, cookie] + JSON_TYPE + [("Content-Length", str(len(data)))], data)
        assert got[:2] == ADMITTED[path.rsplit("/", 1)[1]], \
            f"a write with each header on one line was refused: {method} {path} answered {got[0]} {got[1]}"
    before = files_digest(c.root)
    assert _raw_lines(c, "GET", "/api/cases", [host, host]) == (403, "HOST_REFUSED", ""), \
        "a read whose Host is sent on two lines, each naming this server, was not refused, so one line stood for the request"
    for method, path, body in _writes():
        data = json.dumps(body).encode("utf-8")
        length = ("Content-Length", str(len(data)))
        for name, lines, want in (
            ("Host", [host, host, cookie] + JSON_TYPE + [length], (403, "HOST_REFUSED", "")),
            ("Cookie", [host, cookie, cookie] + JSON_TYPE + [length], (403, "TOKEN_REFUSED", "")),
            ("Content-Length", [host, cookie] + JSON_TYPE + [length, length],
             (400, "BODY_REFUSED", "a body needs one Content-Length header of at most 8192 bytes")),
        ):
            got = _raw_lines(c, method, path, lines, data)
            assert got == want, \
                f"a write whose {name} is sent on two lines, each admissible, answered {got[0]} {got[1]}, so one line stood for the request: {method} {path}"
    assert files_digest(c.root) == before, "a write with a header sent on two lines reached the store"
    assert [r for r in c.logs if len(r) > 5] == [], "a request with a header sent on two lines faulted the server"


def _token_check_reading(read_cookie):
    """The token check, with its Cookie header read by `read_cookie(handler)`, for the breakers below."""
    import hmac
    from http.cookies import SimpleCookie

    def check(self):
        jar = SimpleCookie()
        try:
            jar.load(read_cookie(self) or "")
        except Exception:  # noqa: BLE001 - as the server reads an unparseable cookie
            jar = SimpleCookie()
        got = jar.get(self.app.cookie_name())
        if got is None or not hmac.compare_digest(got.value.encode("utf-8"), self.app.token.encode("utf-8")):
            raise server.Refusal("TOKEN_REFUSED")

    return check


def break_repeated_cookie_read_by_its_first_line(ctx):
    """The token check as it was before 2026-11-16: the cookie parser reads the Cookie header's first line."""
    ctx.mp.setattr(server.Handler, "_check_token", _token_check_reading(lambda self: self.headers.get("Cookie")))


def break_cookie_read_from_its_joined_lines(ctx):
    """The Cookie header read as Origin is, its lines joined by a comma: the parser reads the joined lines as one
    cookie list and keeps the last value of a repeated name, so the last line stands for the request."""
    ctx.mp.setattr(server.Handler, "_check_token", _token_check_reading(lambda self: self._header_value("Cookie")))


def break_content_length_read_by_its_first_line(ctx):
    """The body's length read from the Content-Length header's first line, as it was before 2026-11-16."""
    real = server.Handler._header_value
    ctx.mp.setattr(server.Handler, "_header_value",
                   lambda self, name: self.headers.get(name) if name == "Content-Length" else real(self, name))


def test_a_repeated_host_cookie_or_content_length_stands_for_no_request(ctx):
    check_a_repeated_host_cookie_or_content_length_stands_for_no_request(ctx)


#: Whether this platform offers a port for exclusive use, read here and not from the server, so a server that
#: misreads its platform takes the other branch where the checks below see it.
PLATFORM_EXCLUSIVE = hasattr(socket, "SO_EXCLUSIVEADDRUSE")


def _reuse_options(sock: socket.socket) -> dict:
    """The reuse options a socket carries, each read as 0 or 1, for each option the platform has. Each option is
    named as a constant, so tools/validate_authorization.py --dispatch-paths reads no dynamic call here."""
    options = {"SO_REUSEADDR": socket.SO_REUSEADDR}
    if hasattr(socket, "SO_REUSEPORT"):
        options["SO_REUSEPORT"] = socket.SO_REUSEPORT
    if PLATFORM_EXCLUSIVE:
        options["SO_EXCLUSIVEADDRUSE"] = socket.SO_EXCLUSIVEADDRUSE
    return {name: int(sock.getsockopt(socket.SOL_SOCKET, option) != 0) for name, option in options.items()}


def _bound_for(sock: socket.socket, exclusive: bool) -> None:
    """The listening socket carries the options of a platform that offers exclusive use, or of one that does not."""
    got = _reuse_options(sock)
    assert got.get("SO_REUSEPORT", 0) == 0, \
        "the listening socket carries SO_REUSEPORT, so a socket of the same user could share its port"
    if exclusive:
        assert (got["SO_EXCLUSIVEADDRUSE"], got["SO_REUSEADDR"]) == (1, 0), \
            (f"where the platform offers exclusive use the listening socket carries SO_EXCLUSIVEADDRUSE "
             f"{got['SO_EXCLUSIVEADDRUSE']} and SO_REUSEADDR {got['SO_REUSEADDR']}, not 1 and 0, so another socket "
             "that sets SO_REUSEADDR could bind its port")
    else:
        assert got["SO_REUSEADDR"] == 1, \
            ("where the platform offers no exclusive use the listening socket leaves SO_REUSEADDR off, so on Linux a "
             "restart on its port is refused while the port's last connections wait out TIME_WAIT")


def check_the_listening_socket_is_bound_per_platform(ctx):
    """The listening socket shares its port with no other socket, by options chosen per platform (review finding 8
    of 2026-11-14 and the second reader's should-fix 1 of 2026-11-16). Where the platform offers exclusive use,
    which is Windows, the socket carries SO_EXCLUSIVEADDRUSE and not SO_REUSEADDR, because there SO_REUSEADDR lets
    another socket that sets it too bind the port. Elsewhere it carries SO_REUSEADDR, as the standard library and
    socket.create_server set it: the second reader saw on Linux on 2026-11-16 that a second server that set
    SO_REUSEADDR was refused whether or not the first set it, so the option opens nothing there, and that without
    it a restart on a port that had just served a request was refused for 60.3 s. SO_REUSEPORT, which lets a socket
    of the same user share the port on Linux, is off everywhere, in the class and on the socket. The platform is
    read here, and the branch the server takes for it is read from a live server; where exclusive use exists, the
    branch every other platform takes is read as well, from a server bound with EXCLUSIVE_USE set false, so a
    control on that branch fails on this workstation too. The options are what is read: a second bind is the next
    check's, on Windows, and on Linux the second reader's runs."""
    assert server.SERVER_CLASS.allow_reuse_port is False, "the server class sets SO_REUSEPORT on its listening socket"
    _bound_for(Client(ctx).server.socket, PLATFORM_EXCLUSIVE)
    if PLATFORM_EXCLUSIVE:
        ctx.mp.setattr(server, "EXCLUSIVE_USE", False)
        _bound_for(Client(ctx, corpus_copy(ctx, "other-branch")).server.socket, False)


def break_reuse_port_allowed(ctx):
    ctx.mp.setattr(server.Server, "allow_reuse_port", True)


def break_reuse_address_off_everywhere(ctx):
    """The bind as the rework of 2026-11-16 first made it: exclusive use where the platform offers it, and
    SO_REUSEADDR off on every platform, which on Linux refused a restart on a fixed port for a minute."""
    def bind(self):
        if server.EXCLUSIVE_USE:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super(server.Server, self).server_bind()

    ctx.mp.setattr(server.Server, "server_bind", bind)


def break_no_exclusive_use(ctx):
    """A plain bind where the platform offers exclusive use: SO_EXCLUSIVEADDRUSE unset and SO_REUSEADDR off. A
    platform without exclusive use never takes the branch this breaks, so there the control is skipped, as the
    second-bind check is."""
    if not PLATFORM_EXCLUSIVE:
        pytest.skip("this platform offers no exclusive use, so its bind takes the branch this control leaves as it is")

    def bind(self):
        if not server.EXCLUSIVE_USE:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        super(server.Server, self).server_bind()

    ctx.mp.setattr(server.Server, "server_bind", bind)


def test_the_listening_socket_is_bound_per_platform(ctx):
    check_the_listening_socket_is_bound_per_platform(ctx)


class _Contender(server.Server):
    """A second server bound as the standard library's HTTPServer binds, with SO_REUSEADDR on and no exclusive use,
    as another process might bind. It is made and closed and never serves."""

    allow_reuse_address = True

    def server_bind(self) -> None:
        super(server.Server, self).server_bind()


def check_a_second_bind_to_the_port_is_refused(ctx):
    """On Windows a second server that sets SO_REUSEADDR binds a port held by a socket that set it too, as the
    standard library's HTTPServer does, so another process could take this server's connections (review finding 8;
    seen on this workstation on 2026-11-16). The server's socket is bound with SO_REUSEADDR off and
    SO_EXCLUSIVEADDRUSE on, and such a second server, bound to the server's address and port, is refused. With
    SO_REUSEADDR off alone it was refused here as well, so the exclusive use, which refuses every second bind
    whatever its options, is read from the socket. Elsewhere the check is skipped: Linux and the BSDs refuse a
    second bind to a listening address and port unless both sockets set SO_REUSEPORT, which the check above
    reads, so a server bound without exclusive use passes there and the check could not fail under its control.
    The second reader saw this on Linux on 2026-11-16: a second server that set SO_REUSEADDR was refused whether
    or not the first set it, and only SO_REUSEPORT on both shared the port. The second server is this module's
    server class bound to 127.0.0.1, as every test server is, so the check adds no network call of its own to
    what tools/validate_authorization.py --dispatch-paths reads."""
    if not PLATFORM_EXCLUSIVE:
        pytest.skip("SO_EXCLUSIVEADDRUSE is a Windows option; this platform refuses a second bind to a listening "
                    "port without it, so the check could not fail under its control")
    c = Client(ctx)
    try:
        contender = _Contender(("127.0.0.1", c.port), server.Handler, c.app)
    except OSError:
        contender = None
    if contender is not None:
        contender.server_close()
        raise AssertionError("a second server bound this server's port, so another process could take its connections")
    assert c.server.socket.getsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE) == 1, \
        "the listening socket is not bound for exclusive use"


def break_the_stdlib_bind_restored(ctx):
    """The bind the stdlib's HTTPServer makes: SO_REUSEADDR on, and no exclusive use."""
    ctx.mp.setattr(server.Server, "allow_reuse_address", True)
    ctx.mp.delattr(server.Server, "server_bind")


def test_a_second_bind_to_the_port_is_refused(ctx):
    check_a_second_bind_to_the_port_is_refused(ctx)


def check_get_routes_write_nothing_and_open_no_socket(ctx):
    opened = []
    c = Client(ctx)
    # Each original is kept beside the patch that replaces it, which
    # tools/validate_authorization.py --dispatch-paths reads as no dispatch
    # (reading VA-R6). The client reaches its own server through 127.0.0.1 and
    # its port, so every lookup of another name and every connection elsewhere
    # is refused and recorded.
    real_lookup = socket.getaddrinfo
    real_connect = socket.socket.connect
    real_connect_ex = socket.socket.connect_ex

    def loopback_lookup_only(host, *args, **kwargs):
        if host != "127.0.0.1":
            opened.append(("getaddrinfo",))
            raise OSError("a name lookup refused by the test")
        return real_lookup(host, *args, **kwargs)

    def own_server_only(sock, address, *args):
        if tuple(address[:2]) != ("127.0.0.1", c.port):
            opened.append(("connect",))
            raise OSError("outbound connection refused by the test")
        return real_connect(sock, address, *args)

    def own_server_only_ex(sock, address, *args):
        if tuple(address[:2]) != ("127.0.0.1", c.port):
            opened.append(("connect_ex",))
            return 111
        return real_connect_ex(sock, address, *args)

    ctx.mp.setattr(socket, "getaddrinfo", loopback_lookup_only)
    ctx.mp.setattr(socket.socket, "connect", own_server_only)
    ctx.mp.setattr(socket.socket, "connect_ex", own_server_only_ex)
    before = files_digest(c.root)
    store = open_case(c.root)
    seq = store.conn.execute("SELECT MAX(seq) FROM event_skeleton").fetchone()[0]
    store.close()
    for p in get_routes():
        r = c.get(p)
        assert r.status < 500, f"a GET route failed: {p}"
    _, frames = c.stream(f"{API}/notices", None, 0.5)
    assert files_digest(c.root) == before, "a GET route wrote to the store"
    store = open_case(c.root)
    assert store.conn.execute("SELECT MAX(seq) FROM event_skeleton").fetchone()[0] == seq
    store.close()
    assert opened == [], "a GET route opened an outbound connection"


def break_header_route_writes(ctx):
    real = routes.HANDLERS["header"]

    def writing(app, params, query, body):
        with routes.case_store(app.root, params["case"], write=True) as store:
            kv.put(store, params["case"], app.analyst, "web", "hops", 3)
        return real(app, params, query, body)

    ctx.mp.setitem(routes.HANDLERS, "header", writing)


def break_header_route_dials_out(ctx):
    real = routes.HANDLERS["header"]

    def dialing(app, params, query, body):
        try:
            socket.create_connection(("127.0.0.1", 9), timeout=0.1)
        except OSError:
            pass
        return real(app, params, query, body)

    ctx.mp.setitem(routes.HANDLERS, "header", dialing)


def break_header_route_dials_with_connect_ex(ctx):
    """A dial that bypasses create_connection and connect: connect_ex on a socket
    the route made itself. The socket is a loopback listener, the one constructor
    whose loopback destination the dispatch scan can read on the call, and
    connect_ex on it sends nothing when the check's patch is absent."""
    real = routes.HANDLERS["header"]

    def dialing(app, params, query, body):
        sock = socket.create_server(("127.0.0.1", 0))
        try:
            sock.connect_ex(("127.0.0.1", 9))
        except OSError:
            pass
        finally:
            sock.close()
        return real(app, params, query, body)

    ctx.mp.setitem(routes.HANDLERS, "header", dialing)


def break_header_route_looks_up_a_name(ctx):
    """A name lookup, which reaches a resolver before any connection exists.
    localhost resolves from the hosts file when the check's patch is absent."""
    real = routes.HANDLERS["header"]

    def looking_up(app, params, query, body):
        try:
            socket.getaddrinfo("localhost", 9)
        except OSError:
            pass
        return real(app, params, query, body)

    ctx.mp.setitem(routes.HANDLERS, "header", looking_up)


def test_get_routes_write_nothing_and_open_no_socket(ctx):
    check_get_routes_write_nothing_and_open_no_socket(ctx)


def check_bind_refused_off_loopback(ctx):
    built = []

    class Recorder:
        def __init__(self, *args, **kwargs):
            built.append(args)
            raise RuntimeError("a server socket was about to be created")

    ctx.mp.setattr(server, "SERVER_CLASS", Recorder)
    root = corpus_copy(ctx)
    for host in ("0.0.0.0", "::", "localhost", "192.0.2.1"):
        assert refusal_of(server.make_server, root, host=host, analyst="analyst-example").code == "BIND_REFUSED_LOCAL"
    assert built == [], "a socket was created for a refused address"


def break_bind_check_removed(ctx):
    ctx.mp.setattr(server, "check_bind", lambda host: None)


def test_bind_refused_off_loopback(ctx):
    check_bind_refused_off_loopback(ctx)


def check_a_held_port_is_refused_with_its_moves(ctx):
    """python -m app serve with --port naming a port another socket holds exits 1 and prints BIND_REFUSED_PORT on
    stderr: what was refused, the rule, the moves, the port and the error's code, and no traceback. The bind
    refuses that port on every platform, under exclusive use on Windows and by the kernel's own rule on Linux, and
    its error used to leave main() as a traceback, errno 10048 on Windows and 98 on Linux in the second reader's
    runs of 2026-11-16 (its should-fix 5). The held port is this check's own server's, which goes on serving; a
    second server that bound the port anyway fails the check rather than serve."""
    import contextlib
    import io

    from app import __main__ as cli
    from app import refusals

    c = Client(ctx)

    def served(self, *args, **kwargs):
        raise AssertionError("a second server bound a port another socket holds and began to serve")

    ctx.mp.setattr(server.Server, "serve_forever", served)
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            code = cli.main(["serve", "--store", str(c.root), "--analyst", "analyst-example", "--port", str(c.port)])
    except OSError as exc:
        raise AssertionError(f"a bind to a port another socket holds left main() as {type(exc).__name__}, which the "
                             "operator reads as a traceback") from None
    text = err.getvalue()
    assert code == 1, f"a bind to a port another socket holds exited {code}: {text!r}"
    assert text.startswith("Refused BIND_REFUSED_PORT: "), f"a bind to a port another socket holds printed {text!r}"
    assert all(move in text for move in refusals.REFUSALS["BIND_REFUSED_PORT"].moves), \
        f"the refused bind's line leaves out a move: {text!r}"
    assert f"\nport {c.port}: " in text and "Traceback" not in text, \
        f"the refused bind's line does not name the port, or carries a traceback: {text!r}"
    assert c.get("/api/cases").status == 200, "the server that held the port stopped serving"


def break_bind_error_left_to_main(ctx):
    """The bind as it was before the second reader's should-fix 5 of 2026-11-16: its OSError leaves make_server and
    main() as it is."""
    ctx.mp.setattr(server, "bind_server", lambda host, port, app: server.SERVER_CLASS((host, port), server.Handler, app))


def test_a_held_port_is_refused_with_its_moves(ctx):
    check_a_held_port_is_refused_with_its_moves(ctx)


def test_unknown_analyst_refused(ctx):
    assert refusal_of(server.make_server, corpus_copy(ctx), analyst="someone-else").code == "ANALYST_UNKNOWN"


# ---------------------------------------------------------------------------
# the cap
# ---------------------------------------------------------------------------


def over_cap_store(ctx, extra: int = 301):
    """The corpus store plus `extra` opaque referenced nodes, each proposed from the focus."""
    root = corpus_copy(ctx, "overcap")
    store = open_case(root)
    link = eid_of("link-same_entity")
    rows = []
    for i in range(extra):
        nid = str(uuid.uuid5(uuid.UUID(CASE), f"cap-{i}"))
        rows.append(nid)
        store.conn.execute(
            "INSERT INTO node (node_id, kind, sector, created_by_event_id) VALUES (?, 'referenced', 'people', ?)",
            (nid, link),
        )
        store.conn.execute(
            "INSERT INTO edge (edge_id, kind, src_id, dst_id, layer, label, actor, ts, event_id) "
            "VALUES (?, 'proposes', ?, ?, 'inference', 'same_entity', 'matcher-example', '2026-01-15T10:10:00Z', ?)",
            (f"{link}#{i + 100}", FOCUS, nid, link),
        )
    store.close()
    return root


def check_cap_fallback_engages(ctx):
    assert (web.WEB_MAX_NODES, web.WEB_MAX_EDGES) == (300, 600)
    assert web.over_cap(range(301), ()) and web.over_cap(range(1), range(601))
    assert not web.over_cap(range(300), range(600))
    c = Client(ctx, over_cap_store(ctx))
    n_nodes, _ = expected_web(c.root, FOCUS, 1)
    r = c.get(f"{API}/web.svg?focus={FOCUS}&hops=1")
    assert r.status == 409 and b"<svg" not in r.body, "an over-cap web was drawn"
    assert r.json()["refused"] == "WEB_OVER_CAP"
    text = f"this web has {len(n_nodes)} nodes; the canvas draws at most 300; narrow by hop to draw the canvas; a sector narrows the list twin"
    assert r.json()["detail"] == text
    twin = c.get(f"{API}/web?focus={FOCUS}&hops=1").json()
    assert twin["mode"] == "list" and twin["cap"] == text and len(twin["nodes"]) == len(n_nodes)
    assert c.get(f"{API}/web.svg?focus={FOCUS}&hops=1&max=1000").json()["refused"] == "QUERY_KEY_REFUSED"


def break_cap_raised(ctx):
    ctx.mp.setattr(web, "WEB_MAX_NODES", 10 ** 6)


def test_cap_fallback_engages(ctx):
    check_cap_fallback_engages(ctx)


def test_sector_collapse_past_fifty(ctx):
    c = Client(ctx, over_cap_store(ctx, extra=60))
    twin = c.get(f"{API}/web.list?focus={FOCUS}&hops=1").json()["nodes"]
    people = [n for n in twin if n["sector"] == "people"]
    body = c.get(f"{API}/web?focus={FOCUS}&hops=1").json()
    assert body["mode"] == "web" and f"PEOPLE {len(people)} · open as list" in [x["text"] for x in body["collapsed"]]
    drawn = {n["node_id"] for n in body["nodes"]}
    assert drawn == {FOCUS} | {n["node_id"] for n in twin if n["sector"] is None}
    expanded = c.get(f"{API}/web?focus={FOCUS}&hops=1&sector=people").json()
    assert "PEOPLE" not in " ".join(x["text"] for x in expanded["collapsed"])
    assert {n["node_id"] for n in people} <= {n["node_id"] for n in expanded["nodes"]}


# ---------------------------------------------------------------------------
# workspace_kv
# ---------------------------------------------------------------------------


def check_kv_refuses_free_text(ctx):
    c = Client(ctx)
    c.login()
    prose = named(corpus_events(), "adjudicate-note")["payload"]["text"]
    r = c.send("PUT", f"/api/kv/{CASE}/web", {"focus": prose})
    assert r.status == 400 and r.json()["refused"] == "KV_VALUE_REFUSED", "a free-text workspace value was written"
    assert prose.encode() not in r.body
    r = c.send("PUT", f"/api/kv/{CASE}/web", {"query": 1})
    assert r.status == 400 and r.json()["refused"] == "KV_KEY_REFUSED"
    r = c.send("PUT", f"/api/kv/{CASE}/web", {"collapsed": ["emails", prose]})
    assert r.status == 400 and r.json()["refused"] == "KV_VALUE_REFUSED", "a list carried free text into workspace_kv"
    assert prose.encode() not in r.body
    r = c.send("PUT", f"/api/kv/{CASE}/web", {"columns": [["web"]]})
    assert r.status == 400 and r.json()["refused"] == "KV_VALUE_REFUSED"
    assert c.get(f"/api/kv/{CASE}/web").json()["values"] == {}, "a refused value reached workspace_kv"
    r = c.send("PUT", f"/api/kv/{CASE}/web", {"focus": FOCUS, "hops": 2, "drawer": "open"})
    assert r.status == 200
    assert c.get(f"/api/kv/{CASE}/web").json()["values"] == {"drawer": "open", "focus": FOCUS, "hops": 2}
    assert c.send("PUT", f"/api/kv/{CASE}/web", {"hops": 1}, cookie=False).status == 403


def break_kv_value_check_removed(ctx):
    ctx.mp.setattr(kv, "legal_value", lambda value: True)


def break_kv_list_branch_open(ctx):
    real = kv.legal_value
    ctx.mp.setattr(kv, "legal_value", lambda value: True if isinstance(value, list) else real(value))


def test_kv_refuses_free_text(ctx):
    check_kv_refuses_free_text(ctx)


# ---------------------------------------------------------------------------
# focus, paths, dossier and consequences
# ---------------------------------------------------------------------------


def check_focus_required_and_case_scoped(ctx):
    c = Client(ctx)
    for path in (f"{API}/web", f"{API}/web.svg", f"{API}/web.list", f"{API}/dossier"):
        r = c.get(path)
        assert r.status == 400 and r.json()["refused"] == "FOCUS_REQUIRED", f"{path} drew without a focus"
        assert "CUT LIST A" in r.json()["text"]
    other = uuid.uuid5(uuid.UUID(CASE), "other")
    assert c.get(f"/api/cases/{other}/web?focus={FOCUS}").json()["refused"] == "CASE_NOT_HELD"
    assert c.get(f"{API}/web?focus={other}").json()["refused"] == "NODE_NOT_IN_CASE"
    assert c.get(f"/api/cases/{CASE},{other}/web?focus={FOCUS}").status == 404


def _served_under(ctx, spelling: str, name: str) -> Client:
    """A server on a store whose one case is the corpus's, registered under `spelling` of its id."""
    events = corpus_events()
    for e in events:
        e["case_id"] = spelling
    return Client(ctx, ctx.built(name, events).root)


def check_a_second_spelling_of_a_held_case_is_served(ctx):
    """A case registered under another spelling of its id is held, and the routes say so. A URL names a case
    in lower case, so the registry's spelling is read, as verify_shred reads it (amendment 9.26)."""
    upper = CASE.upper()
    assert upper != CASE
    c = _served_under(ctx, upper, "upper")
    assert [x["case_id"] for x in c.get("/api/cases").json()["cases"]] == [upper]
    for spelled in (CASE, upper):
        r = c.get(f"/api/cases/{spelled}/header")
        assert r.status == 200, "a held case named under another spelling of its id was answered as not held"
        h = r.json()
        assert h["case_id"] == upper, "the routes do not read the case under the registry's spelling"
        assert h["rollup"].get("event_type"), "the case's events were not read under the registry's spelling"
    assert h["seed_focus"], "the case under its registry spelling has no node to focus"
    assert c.get(f"/api/cases/{CASE}/dossier?focus={h['seed_focus']}").status == 200
    assert len(c.get(f"/api/cases/{CASE}/coverage").json()["intervals"]) == 1
    assert c.get(f"/c/{CASE}/dossier").status == 200
    other = uuid.uuid5(uuid.UUID(CASE), "other")
    r = c.get(f"/api/cases/{other}/header")
    assert r.status == 404 and r.json()["refused"] == "CASE_NOT_HELD" and "detail" not in r.json()
    # Two rows that name one case database under other spellings cannot be told apart by a URL: refused, and
    # the refusal says why.
    mixed = upper[:9] + CASE[9:]
    assert mixed not in (upper, CASE)
    store = open_case(c.root)
    cols = [x["name"] for x in store.conn.execute("PRAGMA table_info(case_registry)") if x["name"] != "case_id"]
    store.conn.execute(
        f"INSERT INTO case_registry (case_id, {', '.join(cols)}) SELECT ?, {', '.join(cols)} FROM case_registry "
        "WHERE case_id = ?", (mixed, upper))
    store.conn.commit()
    store.close()
    r = c.get(f"/api/cases/{CASE}/header")
    assert r.status == 404 and r.json()["refused"] == "CASE_NOT_HELD"
    assert r.json().get("detail") == (
        f"case {CASE[:8]}: 2 registry rows name this case database under other spellings, and a URL names a case "
        "in lower case, so this server cannot tell which is meant"), "a case two rows name was refused without saying why"


def break_second_spelling_answered_not_held(ctx):
    ctx.mp.setattr(routes, "registered", lambda root, params: params)


def break_two_spellings_refused_without_a_reason(ctx):
    ctx.mp.setattr(routes, "other_spellings", lambda store, case_id: None)


def break_two_spellings_served_as_the_first(ctx):
    from app.store import ingest

    def first_row(store, case_id):
        rows = ingest.rows_for_file(store.conn, case_id)
        return case_id if store.registry(case_id) is not None else (rows[0]["case_id"] if rows else None)

    ctx.mp.setattr(ingest, "registry_spelling", first_row)


def test_a_second_spelling_of_a_held_case_is_served(ctx):
    check_a_second_spelling_of_a_held_case_is_served(ctx)


def break_focus_defaults_to_seed(ctx):
    real = web.build

    def defaulting(conn, case_id, focus, hops=2, sector=None):
        from app.model import reads

        return real(conn, case_id, focus or reads.seed_focus(conn, case_id), hops, sector)

    ctx.mp.setattr(web, "build", defaulting)


def test_focus_required_and_case_scoped(ctx):
    check_focus_required_and_case_scoped(ctx)


def check_paths_route_through_cluster(ctx):
    c = Client(ctx)
    d = c.get(f"{API}/paths?from={FOCUS}&to={REFERENCED}").json()
    assert [r["nodes"] for r in d["routes"]] == [[FOCUS, CLUSTER_POSSIBLE, REFERENCED]]
    assert "band possible" in d["routes"][0]["weakest"]
    d = c.get(f"{API}/paths?from={FOCUS}&to=584e2e90-328f-537c-9f00-5527f9dab8c2").json()
    direct = [r for r in d["routes"] if len(r["hops"]) == 1]
    assert len(direct) == 4 and all("unaccepted proposal" in r["weakest"] for r in direct)
    via_tombstone = [r for r in d["routes"] if r["nodes"][1] == "d3455fc7-427c-58c5-93c0-bc9171334de5"]
    assert via_tombstone and all("revoked assertion" in r["weakest"] for r in via_tombstone)


def break_paths_one_hop(ctx):
    from app.model import paths

    ctx.mp.setattr(paths, "MAX_HOPS", 1)


def test_paths_route_through_cluster(ctx):
    check_paths_route_through_cluster(ctx)


def check_states_render_as_consequences(ctx):
    c = Client(ctx)
    h = c.get(f"{API}/header").json()
    assert h["halt"].startswith(f"HALTED, a shred failed in case {CASE[:8]} at "), "the halt is not rendered as its consequence"
    assert "no new run dispatches system-wide (RT-11)" in h["halt"]
    assert h["retention"] == "past retain_until · synthetic stratum-4 material, no sweep acts on LOCAL"
    assert h["state"].startswith("open: ")
    cov = c.get(f"{API}/coverage").json()["intervals"]
    assert [i["interval_id"] for i in cov] == [eid_of("system-coverage-interval")]
    assert cov[0]["text"].startswith("verified coverage of ")
    d = c.get(f"{API}/dossier?focus={FOCUS}").json()
    assert [b["band"] for b in d["bands"]] == ["STATE", "FUSION", "INFERENCE", "OBSERVATION"]
    fusion = d["bands"][1]["rows"]
    assert any(f["tombstone"] and any(line.startswith("REVOKED by ") for line in f["lines"]) for f in fusion)
    assert [m["seams"] for f in fusion for m in f["members"]] == ["h", "b", "g", "g"], "seams were rolled up"
    blob = c.get(f"{API}/blobs/{eid_of('probe-item-1')}").json()
    assert blob["text"] == "raw bytes not held · synthetic fixture names a digest with no capture"
    node = c.get(f"{API}/node/{HANDLE_CLAIM}").json()
    assert node["node"]["deep_dive_state"] == "inert · nothing has been collected against this node"
    assert "no manifest declares a capability for selector type handle" in node["pivot"]["lines"]
    assert [u["event_id"] for u in node["unattached_decisions"]] == [eid_of("collect-requires-extension"), eid_of("collect-refused")]
    ref = c.get(f"{API}/node/{REFERENCED}").json()
    assert ref["node"]["lines"] == ["referenced, never promoted in this case: no observation held"]
    assert any(line.startswith("SS-16: ") for line in ref["pivot"]["lines"])
    focus = c.get(f"{API}/node/{FOCUS}").json()["node"]
    assert "anchor declared platform_uid, anchor claim is a handle, anchor unproven" in focus["lines"]
    joined = json.dumps([h, cov, d, node, ref])
    for token in ('"shred_failed"', '"open"', '"closed"', '"absent"'):
        assert token not in joined, f"a bare state token {token} was rendered"


def break_halt_rendered_as_token(ctx):
    from app.model import reads

    ctx.mp.setattr(reads, "halt_line", lambda conn, environment: "shred_failed")


def test_states_render_as_consequences(ctx):
    check_states_render_as_consequences(ctx)


def test_hint_and_permutation_are_distinct_nodes(ctx):
    c = Client(ctx)
    nodes = {n["node_id"]: n for n in c.get(f"{API}/web?focus={FOCUS}&hops=1").json()["nodes"]}
    hint = nodes[eid_of("extract-claim-hint")]
    perm = nodes[eid_of("extract-claim-generated")]
    assert hint["lines"][0] == "email_hint_recovery_masked" and not hint["generated"]
    assert perm["lines"][0] == "email_generated_permutation" and perm["generated"] and perm["lines"][1].startswith("~")
    root = ET.fromstring(c.get(f"{API}/web.svg?focus={FOCUS}&hops=1").body)
    italics = [t for t in root.iter("{http://www.w3.org/2000/svg}text") if t.get("font-style") == "italic"]
    assert len(italics) == 1 and italics[0].text.startswith("~")


def test_anchor_hatch_clears_when_the_anchor_type_matches(ctx):
    root = corpus_copy(ctx, "anchored")
    store = open_case(root)
    store.conn.execute("UPDATE claim SET selector_type = 'platform_uid' WHERE claim_id = ?", (HANDLE_CLAIM,))
    store.conn.execute("UPDATE node SET anchor_vouched = 1 WHERE node_id = ?", (FOCUS,))
    store.close()
    c = Client(ctx, root)
    focus = c.get(f"{API}/node/{FOCUS}").json()["node"]
    assert focus["lines"][1] == "anchor platform_uid" and "anchor unproven" not in focus["vouch_tokens"]


def check_render_deterministic(ctx):
    from app.model import svg

    root = corpus_copy(ctx)
    outs = []
    for _ in range(2):
        store = open_case(root)
        try:
            outs.append(svg.render(web.build(store.conn, CASE, FOCUS, 3)))
        finally:
            store.close()
    assert outs[0] == outs[1], "two renders of one web differ"
    other = corpus_copy(ctx, "second")
    store = open_case(other)
    try:
        assert svg.render(web.build(store.conn, CASE, FOCUS, 3)) == outs[0], "a second store renders differently"
    finally:
        store.close()


def break_layout_insertion_order(ctx):
    from app.model import layout

    calls = {"n": 0}
    real = layout.place

    def place(nodes, cards=None, hops=2):
        calls["n"] += 1
        return real(nodes if calls["n"] % 2 else list(reversed(nodes)), cards, hops)

    ctx.mp.setattr(layout, "order_key", lambda node: 0)
    ctx.mp.setattr(layout, "place", place)


def test_render_deterministic(ctx):
    check_render_deterministic(ctx)


def test_selector_values_stay_out_of_urls_and_ids(ctx):
    c = Client(ctx)
    raw = c.get(f"{API}/web.svg?focus={FOCUS}&hops=3").body
    body = raw.decode("utf-8")
    ids = re.findall(r'data-(?:node|edge|lineage|edges)="([^"]*)"', body)
    assert ids
    for value in ids:
        for part in value.replace("#", " ").split():
            assert guard_mod.is_uuid(part) or part.isdigit(), "an id in the SVG is not opaque"
    for element in ET.fromstring(raw).iter():
        assert not [k for k in element.attrib if k.endswith("href")], "the SVG carries a URL"



# ---------------------------------------------------------------------------
# the landing URL, the cluster DOSSIER, red, dash, labels and state lines
# ---------------------------------------------------------------------------

CLUSTER_REVOKED = "d3455fc7-427c-58c5-93c0-bc9171334de5"
SVG = "{http://www.w3.org/2000/svg}"


def check_case_url_lands_on_a_view(ctx):
    from app import config

    c = Client(ctx)
    r = c.get(f"/c/{CASE}")
    assert r.status == 302, "a case URL with no view was served as a page with no view"
    assert r.header("Location") == f"/c/{CASE}/{config.LANDING_VIEW}"
    r = c.get(f"/c/{CASE}?focus={FOCUS}")
    assert r.status == 302 and r.header("Location") == f"/c/{CASE}/{config.LANDING_VIEW}?focus={FOCUS}"
    assert c.get(r.header("Location")).status == 200, "the landing view the redirect names is not served"
    assert c.get(f"/c/{CASE}/null").status == 404


def break_case_url_served_without_a_view(ctx):
    real = routes.HANDLERS["index"]

    def serving(app, params, query, body):
        if "case" in params and params.get("view") is None:
            params = dict(params, view="dossier")
        return real(app, params, query, body)

    ctx.mp.setitem(routes.HANDLERS, "index", serving)


def test_case_url_lands_on_a_view(ctx):
    check_case_url_lands_on_a_view(ctx)


def check_dossier_on_a_cluster(ctx):
    c = Client(ctx)
    for cluster, tomb in ((CLUSTER_POSSIBLE, False), (CLUSTER_REVOKED, True)):
        d = c.get(f"{API}/dossier?focus={cluster}").json()
        fusion = d["bands"][1]
        assert fusion["band"] == "FUSION" and len(fusion["rows"]) == 1, "a cluster focus prints no FUSION row"
        row = fusion["rows"][0]
        assert row["cluster_id"] == cluster and row["tombstone"] is tomb
        assert len(row["members"]) == 2 and all(m["seams"] for m in row["members"])
    d = c.get(f"{API}/dossier?focus={FOCUS}").json()
    assert {r["cluster_id"] for r in d["bands"][1]["rows"]} == {CLUSTER_POSSIBLE, CLUSTER_REVOKED}


def break_fusion_reads_members_only(ctx):
    from app.model import dossier

    ctx.mp.setattr(
        dossier, "clusters_for",
        lambda focus_row, edges: [e["dst_id"] for e in edges if e["kind"] == "member_of" and e["src_id"] == focus_row["node_id"]],
    )


def test_dossier_on_a_cluster(ctx):
    check_dossier_on_a_cluster(ctx)


def check_red_means_does_not_vouch(ctx):
    c = Client(ctx)
    link = c.get(f"{API}/lineage/{eid_of('link-same_entity')}").json()
    assert link["raw"] == "no raw bytes belong to this event" and link["raw_vouch"] is False
    claim = c.get(f"{API}/lineage/{HANDLE_CLAIM}").json()
    assert claim["raw"].startswith("not held: ") and claim["raw_vouch"] is True
    h = c.get(f"{API}/header").json()
    assert h["retention"].startswith("past retain_until") and h["retention_vouch"] is True
    from app.store import retention

    reg = {"retain_until": "2999-01-01", "environment": "LOCAL", "synthetic": 1}
    assert retention.is_past(reg) is False, "a future retain_until reads as past"
    js = (routes.STATIC / "views" / "lineage.js").read_text(encoding="utf-8")
    assert 'class: d.raw_vouch ? "vouch" : ""' in js, "the RAW tier is painted red without the server's flag"
    app_js = (routes.STATIC / "app.js").read_text(encoding="utf-8")
    assert 'class: r.body.retention_vouch ? "vouch" : ""' in app_js, "the retention line is painted red without its flag"


def break_raw_always_vouch(ctx):
    from app.model import lineage

    real = lineage._raw
    ctx.mp.setattr(lineage, "_raw", lambda conn, case_id, head: (real(conn, case_id, head)[0], True))


def test_red_means_does_not_vouch(ctx):
    check_red_means_does_not_vouch(ctx)


def _svg_root(c, focus=FOCUS, hops=2):
    return ET.fromstring(c.get(f"{API}/web.svg?focus={focus}&hops={hops}").body)


def check_dash_means_inference_only(ctx):
    c = Client(ctx)
    referenced = "584e2e90-328f-537c-9f00-5527f9dab8c2"
    for focus in (FOCUS, referenced, REFERENCED):
        root = _svg_root(c, focus)
        for el in root.iter():
            if el.get("stroke-dasharray"):
                assert el.tag == f"{SVG}path" and el.get("class") == "edge-line", "a box or card carries a dash"
        for g in root.iter(f"{SVG}g"):
            if g.get("data-layer") and g.get("data-layer") != "inference":
                assert not g.find(f"{SVG}path").get("stroke-dasharray"), "a non-inference edge is dashed"
    css = (routes.STATIC / "app.css").read_text(encoding="utf-8")
    dashed = [line for line in css.splitlines() if re.search(r"dash(ed|array)", line) and not line.lstrip().startswith(("/*", "INFERENCE"))]
    assert dashed == [".inference-row { border-left: 2px dashed var(--ink); padding-left: 6px; margin: 4px 0; }"], dashed


def break_referenced_box_dashed(ctx):
    from app.model import svg

    real = svg._node

    def dashed(n, x, y, h, order, focus):
        out = real(n, x, y, h, order, focus)
        return out.replace('class="box"', 'class="box" stroke-dasharray="5 3"', 1) if n["kind"] == "referenced" else out

    ctx.mp.setattr(svg, "_node", dashed)


def test_dash_means_inference_only(ctx):
    check_dash_means_inference_only(ctx)


def check_labels_painted_above_nodes(ctx):
    c = Client(ctx)
    root = _svg_root(c)
    layers = [g.get("class") for g in root if g.tag == f"{SVG}g"]
    assert layers == ["edges", "nodes", "labels"], "edge labels are painted under the node boxes"
    labels = [t for t in root.iter(f"{SVG}text") if (t.get("class") or "").startswith("edge-label")]
    assert labels and all(t in list(root[-1].iter(f"{SVG}text")) for t in labels)
    proposals = [t.text for t in labels if "PROPOSED" in t.text]
    assert len(proposals) == 4 and all(p.startswith("NOT ACCEPTED, ") for p in proposals)


def break_labels_under_nodes(ctx):
    from app.model import svg

    ctx.mp.setattr(svg, "PAINT_ORDER", ("edges", "labels", "nodes"))


def test_labels_painted_above_nodes(ctx):
    check_labels_painted_above_nodes(ctx)


def check_state_lines_never_cut(ctx):
    from app.model import svg

    c = Client(ctx)
    texts = []
    for focus in (FOCUS, CLUSTER_REVOKED, REFERENCED):
        root = _svg_root(c, focus)
        for g in root.iter(f"{SVG}g"):
            if not g.get("data-node"):
                continue
            lines = [(t.get("class"), t.text or "") for t in g.findall(f"{SVG}text")]
            for cls, text in lines:
                if "value" not in cls.split():
                    assert not text.endswith(svg.CUT), f"a state line was cut on the canvas: {cls}"
            deep = " ".join(text for cls, text in lines if "deep-dive" in cls.split())
            texts.append(deep)
            joined = " ".join(text for _, text in lines)
            texts.append(joined)
    assert web.INERT in texts, "the inert consequence does not print in full"
    whole = "\n".join(texts)
    for phrase in ("this assertion no longer stands", "asserted not the subject", "no observation held", "past retain_until"):
        assert phrase in whole, f"the consequence '{phrase}' does not print on the canvas"


def break_state_lines_cut(ctx):
    from app.model import svg

    ctx.mp.setattr(svg, "wrap", lambda text, width=svg.MAX_CHARS: [svg._fit(text)])


def test_state_lines_never_cut(ctx):
    check_state_lines_never_cut(ctx)


# ---------------------------------------------------------------------------
# the egress guard after another process ingests, and the response side
# ---------------------------------------------------------------------------


def check_guard_follows_out_of_process_ingest(ctx):
    from app.store import db, door, ingest
    from app.tests.helpers import CORPUS

    root = ctx.tmp / "empty"
    db.Store.init(root).close()
    c = Client(ctx, root)
    assert c.app.guard.held() == 0
    ingest.LISTENERS.remove(c.app._listener)
    try:
        store = db.Store.open(root)
        try:
            ingest.ingest_batch(store, door.read_rows(CORPUS), None, source=door.check_source(CORPUS))
        finally:
            store.close()
    finally:
        ingest.LISTENERS.append(c.app._listener)
    assert not c.app.guard.stale, "the ingest reached the server's own listener, so it was not out of process"
    bare = named(corpus_events(), "extract-claim-handle")["payload"]["value"][1:-1]
    r = c.get(f"{API}/node/{bare}")
    assert r.status == 400 and r.json()["refused"] == "REQUEST_VALUE_REFUSED", "the guard missed a value another process ingested"
    assert c.app.guard.counts().get("request") == 1


def break_guard_never_reloads(ctx):
    ctx.mp.setattr(guard_mod, "store_mark", lambda root: ())


def test_guard_follows_out_of_process_ingest(ctx):
    check_guard_follows_out_of_process_ingest(ctx)


def check_response_guard_replaces(ctx):
    c = Client(ctx)
    value = named(corpus_events(), "extract-claim-handle")["payload"]["value"]

    def leaky_header(app, params, query, body):
        return routes.Response(200, "application/json; charset=utf-8", b"{}", {"X-Note": value})

    def leaky_location(app, params, query, body):
        return routes.Response(302, "text/plain; charset=utf-8", b"", {"Location": f"/c/{CASE}/web?{value}"})

    def leaky_title(app, params, query, body):
        return routes.Response(200, "text/html; charset=utf-8", f"<title>{value}</title>".encode(), {})

    def leaky_error(app, params, query, body):
        return routes.Response(404, "application/json; charset=utf-8", json.dumps({"x": value}).encode(), {})

    ctx.mp.setitem(routes.HANDLERS, "header", leaky_header)
    ctx.mp.setitem(routes.HANDLERS, "coverage", leaky_location)
    ctx.mp.setitem(routes.HANDLERS, "keymap", leaky_title)
    ctx.mp.setitem(routes.HANDLERS, "cases", leaky_error)
    r = c.get(f"{API}/header")
    assert r.status == 200 and r.header("X-Note") is None, "a header carrying a held value was sent"
    r = c.get(f"{API}/coverage")
    assert r.status == 500 and r.json()["refused"] == "EGRESS_GUARD_REPLACED" and r.header("Location") is None
    r = c.get("/keymap.json")
    assert r.status == 200 and r.body == b"<title>PLAINSIGHT</title>", "a title carrying a held value was sent"
    r = c.get("/api/cases")
    assert r.status == 500 and r.json()["refused"] == "EGRESS_GUARD_REPLACED"
    assert value.encode() not in b"".join(x.body for x in (r,))
    counts = c.app.guard.counts()
    assert counts == {"Location": 1, "error body": 1, "header": 1, "title": 1}, counts
    ctx.mp.setattr(notices, "valid", lambda notice: True)
    assert c.app.hub.publish({"seq": 1, "kind": "case", "case_id": CASE, "ids": [CASE], "note": value}) is False
    assert c.app.hub.drop_counts() == {"guard": 1}, "a notice carrying a held value was not dropped by the guard"


def break_response_guard_removed(ctx):
    real_scan = guard_mod.Guard.scan

    def request_only(self, target):
        from urllib.parse import unquote, unquote_plus

        return real_scan(self, target) or real_scan(self, unquote(target)) or real_scan(self, unquote_plus(target))

    ctx.mp.setattr(guard_mod.Guard, "scan_request", request_only)
    ctx.mp.setattr(guard_mod.Guard, "scan", lambda self, text: False)


def test_response_guard_replaces(ctx):
    check_response_guard_replaces(ctx)


def check_get_store_is_query_only(ctx):
    import sqlite3

    root = corpus_copy(ctx)
    before = files_digest(root)
    with routes.case_store(root, CASE) as store:
        try:
            store.conn.execute(
                "INSERT INTO workspace_kv (analyst, view, key, value_json, updated_at) VALUES ('a', 'web', 'hops', '2', 'x')"
            )
        except sqlite3.OperationalError as exc:
            assert "readonly" in str(exc) or "read-only" in str(exc)
        else:
            raise AssertionError("a GET connection accepted a write")
    assert files_digest(root) == before


def break_query_only_removed(ctx):
    ctx.mp.setattr(routes, "read_only", lambda conn: None)


def test_get_store_is_query_only(ctx):
    check_get_store_is_query_only(ctx)


# ---------------------------------------------------------------------------
# requests the stdlib parser or a numeric shape refuses
# ---------------------------------------------------------------------------


def _raw_request(c: Client, data: bytes) -> bytes:
    sock = c.connect()
    try:
        sock.sendall(data)
        out = b""
        while True:
            chunk = sock.recv(65536)
            if not chunk:
                break
            out += chunk
        return out
    finally:
        sock.close()


def _refused_code(raw: bytes) -> str:
    """The refusal code of a raw response. A request the stdlib reads as HTTP/0.9 gets a bare body."""
    body = raw.split(b"\r\n\r\n", 1)[1] if raw.startswith(b"HTTP/") else raw
    return json.loads(body.decode("utf-8"))["refused"]


def check_stdlib_rejections_name_their_cause(ctx):
    c = Client(ctx)
    host = f"Host: 127.0.0.1:{c.port}\r\n".encode()
    raw = _raw_request(c, b"OPTIONS / HTTP/1.0\r\n" + host + b"\r\n")
    assert raw.startswith(b"HTTP/1.0 501") and _refused_code(raw) == "METHOD_REFUSED"
    raw = _raw_request(c, b"GET /" + b"a" * (65537 - 5))
    assert raw.startswith(b"HTTP/1.0 414") and _refused_code(raw) == "REQUEST_MALFORMED"
    raw = _raw_request(c, b"GET / HTTP/9.9\r\n")
    assert _refused_code(raw) == "REQUEST_MALFORMED"


def break_stdlib_rejections_read_as_no_route(ctx):
    def send_error(self, code, message=None, explain=None):
        self._template = getattr(self, "_template", "unparsed")
        self._send_refusal(server.Refusal("ROUTE_NOT_FOUND"), status=400 if code == 400 else code)

    ctx.mp.setattr(server.Handler, "send_error", send_error)


def test_stdlib_rejections_name_their_cause(ctx):
    check_stdlib_rejections_name_their_cause(ctx)


def check_unicode_digits_refused(ctx):
    c = Client(ctx)
    c.login()
    r = c.get(f"{API}/notices?after=%C2%B2")
    assert r.status == 400 and r.json()["refused"] == "QUERY_VALUE_REFUSED", "a Unicode digit passed the after shape"
    host = f"Host: 127.0.0.1:{c.port}\r\n".encode()
    raw = _raw_request(
        c,
        f"PUT /api/kv/{CASE}/web HTTP/1.0\r\n".encode() + host + f"Cookie: {c.cookie}\r\n".encode()
        + b"Content-Type: application/json\r\nContent-Length: \xb2\r\n\r\n",
    )
    assert raw.startswith(b"HTTP/1.0 400") and _refused_code(raw) == "BODY_REFUSED", raw[:40]
    sock = c.connect()
    sock.sendall(f"GET {API}/notices HTTP/1.0\r\n".encode() + host + b"Last-Event-ID: \xb2\r\n\r\n")
    joined = "\n\n".join(stream_collect(sock, b"", 0.6))
    assert joined.startswith("HTTP/1.0 200") and joined.count("HTTP/1.0 ") == 1, "a Unicode-digit Last-Event-ID faulted the stream"
    assert not [line for line in c.logs if line[3] == 500], "a Unicode digit reached a server fault"


def break_digits_by_isdigit(ctx):
    ctx.mp.setattr(routes, "ascii_digits", lambda value, max_len=12: isinstance(value, str) and value.isdigit() and len(value) <= max_len)


def test_unicode_digits_refused(ctx):
    check_unicode_digits_refused(ctx)


def check_stream_fault_writes_one_response(ctx):
    from app.refusals import Refusal

    c = Client(ctx)
    calls = {"n": 0}
    real = server.Handler._current_seq

    def failing(self, case_id):
        calls["n"] += 1
        if calls["n"] > 1:
            raise Refusal("CASE_NOT_HELD")
        return real(self, case_id)

    ctx.mp.setattr(server.Handler, "_current_seq", failing)
    sock, head, rest = stream_open(c, f"{API}/notices")
    frames = stream_collect(sock, rest, 1.0)
    body = head.decode("utf-8", "replace") + "\n".join(frames)
    assert body.count("HTTP/1.0 ") == 1, "a second response was written into the event stream"
    assert '"refused"' not in body


def break_sent_flag_ignored(ctx):
    ctx.mp.setattr(server.Handler, "_mark_sent", lambda self: None)


def test_stream_fault_writes_one_response(ctx):
    check_stream_fault_writes_one_response(ctx)


# ---------------------------------------------------------------------------
# withdrawn proposals and revoked clusters render as withdrawn
# ---------------------------------------------------------------------------


def _revoke_link_store(ctx):
    import copy

    from app.store import door, ingest
    from app.tests.helpers import CORPUS

    root = corpus_copy(ctx, "revoked-link")
    rev = copy.deepcopy(named(corpus_events(), "adjudicate-revoke"))
    link = eid_of("link-same_entity")
    rev["event"]["event_id"] = str(uuid.uuid5(uuid.UUID(CASE), "revoke the same_entity link"))
    rev["payload"]["target_ref"] = link
    rev["lineage"]["based_on"] = [link]
    store = open_case(root)
    try:
        result = ingest.ingest_batch(store, [rev], None, source=door.check_source(CORPUS))
    finally:
        store.close()
    assert result.landed == 1, "the REVOKE of a LINK did not land"
    return root, link


def check_withdrawn_proposal_renders_withdrawn(ctx):
    root, link = _revoke_link_store(ctx)
    c = Client(ctx, root)
    edges = c.get(f"{API}/web?focus={FOCUS}&hops=1").json()["edges"]
    mine = [e for e in edges if e["event_id"] == link]
    assert mine and all(e["text"].startswith("PROPOSAL WITHDRAWN by ") and e["withdrawn"] for e in mine)
    assert not any("NOT ACCEPTED" in e["text"] for e in mine), "a withdrawn proposal still reads as pending"
    others = [e for e in edges if e["kind"] == "proposes" and e["event_id"] != link]
    assert others and all(e["text"].startswith("NOT ACCEPTED, ") for e in others)
    d = c.get(f"{API}/paths?from={FOCUS}&to=584e2e90-328f-537c-9f00-5527f9dab8c2").json()
    via = [r for r in d["routes"] if len(r["hops"]) == 1 and r["hops"][0]["event_id"] == link]
    assert via and "withdrawn proposal" in via[0]["weakest"]
    chain = c.get(f"{API}/lineage/{link}").json()
    assert any(s.startswith("REVOKED by ") for s in chain["chain"][0]["summary"])


def break_revocations_ignored(ctx):
    from app.model import reads

    ctx.mp.setattr(reads, "revocations", lambda conn, case_id: {})


def test_withdrawn_proposal_renders_withdrawn(ctx):
    check_withdrawn_proposal_renders_withdrawn(ctx)


def check_revoked_cluster_marked_in_state_and_drawer(ctx):
    c = Client(ctx)
    cluster_event = eid_of("identity-cluster")
    sentence = eid_of("assess-sentence")
    d = c.get(f"{API}/dossier?focus={FOCUS}").json()
    state = [r for r in d["bands"][0]["rows"] if r["sentence_id"] == sentence]
    assert state, "the corpus sentence is not in STATE"
    lines = state[0]["consequences"]
    assert any(line.startswith(f"cites revoked cluster {cluster_event[:8]}: REVOKED by ") for line in lines), lines
    assert any(line.startswith(f"cites claim {HANDLE_CLAIM[:8]}, which is disputed") for line in lines), lines
    chain = c.get(f"{API}/lineage/{sentence}").json()
    entry = next(x for x in chain["chain"] if x["event_id"] == cluster_event)
    assert any(s.startswith("REVOKED by ") for s in entry["summary"]), "the drawer draws a tombstone as a standing cluster"
    assert any(f.startswith(f"cites revoked cluster {cluster_event[:8]}") for f in chain["flags"])
    tomb = c.get(f"{API}/lineage/{cluster_event}").json()
    assert any(s.startswith("REVOKED by ") for s in tomb["chain"][0]["summary"])


def test_revoked_cluster_marked_in_state_and_drawer(ctx):
    check_revoked_cluster_marked_in_state_and_drawer(ctx)


def check_absent_raw_names_its_store(ctx):
    from app.store import blobs

    root = corpus_copy(ctx, "not-synthetic")
    store = open_case(root)
    store.conn.execute("UPDATE case_registry SET synthetic = 0 WHERE case_id = ?", (CASE,))
    store.close()
    c = Client(ctx, root)
    blob = c.get(f"{API}/blobs/{eid_of('probe-item-1')}").json()
    assert blob["text"] == blobs.NOT_HELD_LINE_CASE, "a non-synthetic case reads as a synthetic fixture"
    chain = c.get(f"{API}/lineage/{HANDLE_CLAIM}").json()
    assert chain["raw"] == "not held: " + blobs.NOT_HELD_LINE_CASE
    synthetic = Client(ctx)
    assert synthetic.get(f"{API}/blobs/{eid_of('probe-item-1')}").json()["text"] == blobs.NOT_HELD_LINE


def break_absent_raw_always_synthetic(ctx):
    from app.store import blobs

    ctx.mp.setattr(blobs, "not_held_line", lambda synthetic: blobs.NOT_HELD_LINE)


def test_absent_raw_names_its_store(ctx):
    check_absent_raw_names_its_store(ctx)


def check_pivot_bar_names_no_unproven_target(ctx):
    from app.model import inspector

    c = Client(ctx)
    pivot = c.get(f"{API}/node/{FOCUS}").json()["pivot"]
    assert pivot["target_selector_type"] is None, "an unproven anchor type is named as the deep dive's target"
    assert any(line.startswith("anchor unproven: the declared type platform_uid is not held") for line in pivot["lines"])
    assert any(line.startswith(f"motivating claim {HANDLE_CLAIM[:8]} is disputed") for line in pivot["lines"])
    assert inspector.NOT_DISPATCHED_LINE in pivot["lines"]
    sel = c.get(f"{API}/node/{HANDLE_CLAIM}").json()["pivot"]
    assert sel["target_selector_type"] == "handle"


def break_pivot_trusts_the_declared_anchor(ctx):
    from app.model import inspector, reads

    real = inspector.preflight
    ctx.mp.setattr(inspector, "preflight", lambda conn, case_id, row, claims: real(conn, case_id, {**dict(row), "anchor_vouched": 1}, claims))
    ctx.mp.setattr(reads, "review_states", lambda conn, case_id: {})


def test_pivot_bar_names_no_unproven_target(ctx):
    check_pivot_bar_names_no_unproven_target(ctx)


def test_route_refusals_name_their_object(ctx):
    c = Client(ctx)
    c.login()
    absent = str(uuid.uuid5(uuid.UUID(CASE), "absent"))
    assert c.get(f"{API}/blobs/{absent}").json()["refused"] == "ITEM_NOT_IN_CASE"
    r = c.send("POST", f"{API}/deep-dives", {"node_id": FOCUS, "motivating_claim": absent})
    assert r.status == 404 and r.json()["refused"] == "CLAIM_NOT_IN_CASE"
    r = c.send("POST", f"{API}/deep-dives", {"node_id": absent, "motivating_claim": HANDLE_CLAIM})
    assert r.json()["refused"] == "NODE_NOT_IN_CASE" and "dispatched" in r.json()["text"]


def test_keymap_and_preflight_say_connected(ctx):
    import json as _json

    from app.model import inspector

    keys = _json.loads((routes.STATIC / "keymap.json").read_text(encoding="utf-8"))["keys"]
    p = next(k for k in keys if k["key"] == "p")
    assert "until the subject gate is connected to this route" in p["label"]
    assert "connected to this route" in inspector.NOT_DISPATCHED_LINE


CONTROLS = [
    ("the web walks edges in one direction only", check_web_renders_every_node_and_edge, break_web_walks_one_direction),
    ("the SVG prints a confidence", check_no_number_weight_or_confidence, break_svg_prints_a_confidence),
    ("inference drawn solid", check_dashed_inference_edges, break_inference_drawn_solid),
    ("the item projection row deleted", check_citation_chain_reaches_run_and_item, break_item_projection_row_deleted),
    ("the deep dive records something", check_deep_dive_refuses_and_writes_nothing, break_deep_dive_records_something),
    ("a planted COLLECT_EVENT constructor", check_deep_dive_refuses_and_writes_nothing, break_planted_collect_constructor),
    ("the notice schema removed", check_sse_frames_carry_opaque_ids_only, break_notice_schema_removed),
    ("the request guard removed", check_selector_shaped_request_refused_without_echo, break_request_guard_removed),
    ("a log line writes the request line", check_selector_shaped_request_refused_without_echo, break_log_writes_the_request_line),
    ("a log line writes the request line, crawled", check_crawl_leaks_no_value, break_log_writes_the_request_line),
    ("no-store dropped", check_every_response_carries_the_headers, break_no_store_dropped),
    ("the header route writes", check_get_routes_write_nothing_and_open_no_socket, break_header_route_writes),
    ("the header route dials out", check_get_routes_write_nothing_and_open_no_socket, break_header_route_dials_out),
    ("the bind check removed", check_bind_refused_off_loopback, break_bind_check_removed),
    ("the cap raised", check_cap_fallback_engages, break_cap_raised),
    ("the kv value check removed", check_kv_refuses_free_text, break_kv_value_check_removed),
    ("the kv list branch accepts anything", check_kv_refuses_free_text, break_kv_list_branch_open),
    ("the focus defaults to the seed", check_focus_required_and_case_scoped, break_focus_defaults_to_seed),
    ("a second spelling of a held case is answered as not held", check_a_second_spelling_of_a_held_case_is_served, break_second_spelling_answered_not_held),
    ("two spellings on one database are refused without a reason", check_a_second_spelling_of_a_held_case_is_served, break_two_spellings_refused_without_a_reason),
    ("two spellings on one database are served as the first row", check_a_second_spelling_of_a_held_case_is_served, break_two_spellings_served_as_the_first),
    ("paths limited to one hop", check_paths_route_through_cluster, break_paths_one_hop),
    ("the halt rendered as its token", check_states_render_as_consequences, break_halt_rendered_as_token),
    ("layout in insertion order", check_render_deterministic, break_layout_insertion_order),
    ("the header route dials with connect_ex", check_get_routes_write_nothing_and_open_no_socket, break_header_route_dials_with_connect_ex),
    ("the header route looks up a name", check_get_routes_write_nothing_and_open_no_socket, break_header_route_looks_up_a_name),
    ("a case URL served without a view", check_case_url_lands_on_a_view, break_case_url_served_without_a_view),
    ("FUSION reads members only", check_dossier_on_a_cluster, break_fusion_reads_members_only),
    ("RAW always painted red", check_red_means_does_not_vouch, break_raw_always_vouch),
    ("a referenced box dashed", check_dash_means_inference_only, break_referenced_box_dashed),
    ("labels painted under the nodes", check_labels_painted_above_nodes, break_labels_under_nodes),
    ("state lines cut to the box", check_state_lines_never_cut, break_state_lines_cut),
    ("the guard never reloads", check_guard_follows_out_of_process_ingest, break_guard_never_reloads),
    ("the response guard removed", check_response_guard_replaces, break_response_guard_removed),
    ("query_only removed", check_get_store_is_query_only, break_query_only_removed),
    ("stdlib rejections read as no route", check_stdlib_rejections_name_their_cause, break_stdlib_rejections_read_as_no_route),
    ("digits checked by isdigit", check_unicode_digits_refused, break_digits_by_isdigit),
    ("the sent flag ignored", check_stream_fault_writes_one_response, break_sent_flag_ignored),
    ("revocations ignored: a withdrawn LINK", check_withdrawn_proposal_renders_withdrawn, break_revocations_ignored),
    ("revocations ignored: a revoked cluster", check_revoked_cluster_marked_in_state_and_drawer, break_revocations_ignored),
    ("absent raw always synthetic", check_absent_raw_names_its_store, break_absent_raw_always_synthetic),
    ("the Pivot Bar trusts the declared anchor", check_pivot_bar_names_no_unproven_target, break_pivot_trusts_the_declared_anchor),
    # amendment 9.27: the read-only review of the HTTP boundary of 2026-11-14
    ("Cross-Origin-Resource-Policy dropped", check_every_response_carries_the_headers, break_corp_dropped),
    ("Permissions-Policy dropped", check_every_response_carries_the_headers, break_permissions_policy_dropped),
    ("form-action dropped from the CSP", check_every_response_carries_the_headers, break_form_action_dropped),
    ("a route's header replaces a security header", check_a_route_cannot_replace_a_security_header, break_route_header_wins),
    ("the Origin check removed", check_a_write_from_another_origin_is_refused, break_origin_check_removed),
    ("the Origin check reads the host and not the port", check_a_write_from_another_origin_is_refused, break_origin_check_reads_the_host_only),
    ("the Sec-Fetch-Site check removed", check_a_write_a_page_on_another_site_sent_is_refused, break_fetch_site_check_removed),
    ("the Content-Type check removed", check_a_write_that_is_not_json_is_refused_unread, break_content_type_check_removed),
    ("the Content-Type read by its prefix", check_a_write_that_is_not_json_is_refused_unread, break_content_type_read_by_prefix),
    ("the Host check removed", check_the_host_check_refuses_another_name_or_port, break_host_check_removed),
    ("the Host refusal claims to stop a cross-origin read", check_the_host_check_refuses_another_name_or_port, break_host_refusal_claims_a_cross_origin_read),
    ("the token check removed", check_a_write_needs_the_launch_token, break_token_check_removed),
    ("the session cookie without HttpOnly", check_the_session_cookie_carries_its_attributes, break_cookie_without_http_only),
    ("the session cookie with SameSite=Lax", check_the_session_cookie_carries_its_attributes, break_cookie_same_site_lax),
    ("the session cookie for another path", check_the_session_cookie_carries_its_attributes, break_cookie_for_another_path),
    ("one cookie name for every launch", check_two_launches_keep_their_own_cookie, break_one_cookie_name),
    ("the stdlib's handle_error restored", check_an_exception_outside_dispatch_prints_no_traceback, break_default_handle_error),
    # the verification of amendment 9.27 of 2026-11-14
    ("the Origin check admits the origins of a page on port 80", check_a_write_from_another_origin_is_refused, break_origin_check_admits_port_80),
    ("the Origin check ignores letter case", check_a_write_from_another_origin_is_refused, break_origin_compared_in_lower_case),
    ("the Origin check skips an empty Origin", check_a_write_from_another_origin_is_refused, break_empty_origin_skipped),
    ("a repeated Origin read by its first line", check_a_write_from_another_origin_is_refused, break_repeated_header_read_by_its_first_line),
    ("the Sec-Fetch-Site check reads a prefix", check_a_write_a_page_on_another_site_sent_is_refused, break_fetch_site_read_by_prefix),
    ("a repeated Sec-Fetch-Site read by its first line", check_a_write_a_page_on_another_site_sent_is_refused, break_repeated_header_read_by_its_first_line),
    ("the Content-Type stripped of characters that are not HTTP whitespace", check_a_write_that_is_not_json_is_refused_unread, break_content_type_stripped_by_str_strip),
    ("a repeated Content-Type read by its first line", check_a_write_that_is_not_json_is_refused_unread, break_repeated_header_read_by_its_first_line),
    ("the Host check ignores letter case", check_the_host_check_refuses_another_name_or_port, break_host_compared_in_any_case),
    ("the test client sends its own Host beside one given in lower case", check_the_host_check_refuses_another_name_or_port, break_client_merges_headers_by_exact_name),
    # the second verification of amendment 9.27 of 2026-11-14
    ("the Origin check runs after the body is read", check_a_write_from_another_origin_is_refused, break_page_checks_run_after_the_body_is_read),
    ("the Sec-Fetch-Site check runs after the body is read", check_a_write_a_page_on_another_site_sent_is_refused, break_page_checks_run_after_the_body_is_read),
    ("the token check runs after the body is read", check_a_write_needs_the_launch_token, break_token_checked_after_the_body_is_read),
    ("a repeated Origin read by its last line", check_a_write_from_another_origin_is_refused, break_repeated_header_read_by_its_last_line),
    ("a repeated Sec-Fetch-Site read by its last line", check_a_write_a_page_on_another_site_sent_is_refused, break_repeated_header_read_by_its_last_line),
    ("a repeated Content-Type read by its last line", check_a_write_that_is_not_json_is_refused_unread, break_repeated_header_read_by_its_last_line),
    # the rework of amendment 9.27 of 2026-11-16
    ("a refused write is closed at once with its body on the way", check_a_refusal_reaches_a_client_whose_body_arrives_late, break_refused_write_closed_at_once),
    ("the body is read off the socket before the write checks", check_a_write_is_refused_before_its_body_arrives, break_body_read_before_the_checks),
    ("the answer is written without the half-close", check_a_write_is_refused_before_its_body_arrives, break_answer_without_the_half_close),
    ("the discard reads past MAX_BODY", check_a_refused_writes_body_is_discarded_within_its_bounds, break_discard_reads_past_the_cap),
    ("the discard has no deadline", check_a_refused_writes_body_is_discarded_within_its_bounds, break_discard_waits_without_a_deadline),
    ("the discard runs after a body the server read", check_a_refused_writes_body_is_discarded_within_its_bounds, break_discard_runs_after_a_read_body),
    ("the discard's reads carry no timeout", check_a_refused_writes_body_is_discarded_within_its_bounds, break_discard_reads_with_no_timeout),
    ("the discard reads on after its client closed", check_a_write_is_refused_before_its_body_arrives, break_discard_reads_on_after_the_close),
    ("CONTENT_TYPE_REFUSED's rule as it was before note 8", check_a_write_that_is_not_json_is_refused_unread, break_content_type_rule_as_before),
    ("a repeated Host read by its first line", check_a_repeated_host_cookie_or_content_length_stands_for_no_request, break_repeated_header_read_by_its_first_line),
    ("a repeated Host read by its last line", check_a_repeated_host_cookie_or_content_length_stands_for_no_request, break_repeated_header_read_by_its_last_line),
    ("a repeated Cookie read by its first line", check_a_repeated_host_cookie_or_content_length_stands_for_no_request, break_repeated_cookie_read_by_its_first_line),
    ("a repeated Cookie read from its joined lines", check_a_repeated_host_cookie_or_content_length_stands_for_no_request, break_cookie_read_from_its_joined_lines),
    ("a repeated Content-Length read by its first line", check_a_repeated_host_cookie_or_content_length_stands_for_no_request, break_content_length_read_by_its_first_line),
    ("the server class allows SO_REUSEPORT", check_the_listening_socket_is_bound_per_platform, break_reuse_port_allowed),
    ("the stdlib's bind restored", check_a_second_bind_to_the_port_is_refused, break_the_stdlib_bind_restored),
    ("the deep-dive route answers as LOCAL whatever the application says", check_the_deep_dive_answers_for_the_applications_environment, break_deep_dive_answers_as_local),
    # the second reader's should-fixes of 2026-11-16, built on 2026-11-17
    ("SO_REUSEADDR off where the platform offers no exclusive use", check_the_listening_socket_is_bound_per_platform, break_reuse_address_off_everywhere),
    ("no exclusive use where the platform offers it", check_the_listening_socket_is_bound_per_platform, break_no_exclusive_use),
    ("the discard follows the four write rules' refusals only", check_a_refusal_reaches_a_client_whose_body_arrives_late, break_discard_kept_to_the_write_rules),
    ("the discard waits twice its deadline", check_a_refused_writes_body_is_discarded_within_its_bounds, break_discard_waits_twice_its_deadline),
    ("the token compared as text", check_a_write_needs_the_launch_token, break_token_compared_as_text),
    ("a refused bind left to main() as an OSError", check_a_held_port_is_refused_with_its_moves, break_bind_error_left_to_main),
]
