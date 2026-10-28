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
import uuid
import xml.etree.ElementTree as ET

from app.http import acts, guard as guard_mod, notices, routes, server
from app.model import web
from app.store import kv
from app.tests.helpers import CASE, corpus_events, corpus_strings, eid_of, files_digest, named, refusal_of
from app.tests.served import FOCUS, Client, corpus_copy, open_case, stream_collect, stream_open, template

API = f"/api/cases/{CASE}"
HANDLE_CLAIM = "94746128-88d7-58f3-8e87-31794f06cd25"
REFERENCED = "33c6ba89-16a7-5a0e-8e6d-540e4290a3fa"
CLUSTER_POSSIBLE = "7ef5da42-3536-5468-b095-b78352de28e4"

EXPECTED_HEADERS = {
    "Cache-Control": "no-store",
    "Content-Security-Policy": "default-src 'self'; frame-ancestors 'none'; base-uri 'none'",
    "Referrer-Policy": "no-referrer",
    "X-Content-Type-Options": "nosniff",
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
        "/static/app.js",
        "/static/views/web.js",
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
    c = Client(ctx)
    responses = [c.get(p) for p in get_routes()]
    c.login()
    responses.append(c.send("POST", f"{API}/deep-dives", {"node_id": FOCUS, "motivating_claim": HANDLE_CLAIM}))
    responses.append(c.send("PUT", f"/api/kv/{CASE}/web", {"hops": 2}))
    responses.append(c.request("DELETE", f"{API}/header"))
    for r in responses:
        for k, v in EXPECTED_HEADERS.items():
            assert r.header(k) == v, f"a response lacks {k}"
    _, head, _ = stream_open(c, f"{API}/notices")
    for k, v in EXPECTED_HEADERS.items():
        assert f"{k}: {v}".encode() in head
    cookie = next(r for r in responses if r.header("Set-Cookie")).header("Set-Cookie")
    assert "HttpOnly" in cookie and "SameSite=Strict" in cookie
    assert c.get("/api/cases", {"Host": "elsewhere.test"}).status == 403


def break_no_store_dropped(ctx):
    ctx.mp.delitem(server.SECURITY_HEADERS, "Cache-Control")


def test_every_response_carries_the_headers(ctx):
    check_every_response_carries_the_headers(ctx)


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
    assert h["halt"] == "HALTED, a shred failed: no new run will dispatch system-wide (RT-11)"
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

    ctx.mp.setattr(reads, "halt_line", lambda conn: "shred_failed")


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
]
