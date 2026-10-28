"""The closed route set, its path and query shapes, and the read handlers.

A URL carries uuids and fixed words only. Each path parameter is a uuid or a
closed token, and each query key belongs to a closed set and takes one shape:

    focus, lineage, from, to   a uuid
    hops                       1, 2 or 3
    sector                     a sector token from app/model/sectors.py
    view                       a view token
    dir                        back or forward
    after                      a case_seq, digits only

Any other key is QUERY_KEY_REFUSED and any other shape QUERY_VALUE_REFUSED, and
neither refusal echoes what it refused. A route takes only the keys it lists.

Every GET handler opens its own store connection, attaches the case without
creating anything, and sets PRAGMA query_only before it reads, so a GET performs
zero writes. No handler opens an outbound socket. No route ingests uploaded
bytes and no route spans cases.
"""

from __future__ import annotations

import json
import re
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import parse_qsl, urlencode

from app import config
from app.http import acts
from app.model import dossier as dossier_mod
from app.model import inspector, lineage, paths, reads, sectors, svg, web
from app.refusals import Refusal
from app.store import blobs, db, kv, retention

STATIC = Path(__file__).resolve().parents[1] / "static"

UUID = r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}"

#: The views a /c/<case>/<view> URL may name.
VIEWS = ("dossier", "web", "paths", "list")

#: Every query key any route takes: the seven docs/PLAINSIGHT-design.md
#: amendment 9.12 names, plus from and to, which 9.12 gives the paths route.
QUERY_KEYS = ("focus", "hops", "sector", "view", "lineage", "dir", "after", "from", "to")

_HOPS = {str(h) for h in range(web.HOPS_MIN, web.HOPS_MAX + 1)}

_ASCII_DIGITS = re.compile(r"[0-9]+")


def ascii_digits(value, max_len: int = 12) -> bool:
    """True for 1 to max_len ASCII digits. str.isdigit would also pass a Unicode
    digit such as superscript two, which int() then rejects."""
    return isinstance(value, str) and len(value) <= max_len and _ASCII_DIGITS.fullmatch(value) is not None


def _valid(key: str, value: str) -> bool:
    if key in ("focus", "lineage", "from", "to"):
        return reads.is_uuid(value)
    if key == "hops":
        return value in _HOPS
    if key == "sector":
        return value in sectors.SECTORS
    if key == "view":
        return value in VIEWS
    if key == "dir":
        return value in ("back", "forward")
    if key == "after":
        return ascii_digits(value)
    return False


def parse_query(query: str, allowed: tuple[str, ...]) -> dict[str, str]:
    """The query as {key: value}, or a refusal that never echoes the key or the value."""
    pairs = parse_qsl(query, keep_blank_values=True)
    out: dict[str, str] = {}
    for key, value in pairs:
        if key not in QUERY_KEYS or key not in allowed or key in out:
            raise Refusal("QUERY_KEY_REFUSED")
        if not validate_value(key, value):
            raise Refusal("QUERY_VALUE_REFUSED", f"key: {key}")
        out[key] = value
    return out


def validate_value(key: str, value: str) -> bool:
    return _valid(key, value)


@dataclass(frozen=True)
class Route:
    method: str
    template: str
    pattern: re.Pattern
    handler: str
    query: tuple[str, ...] = ()


def _route(method: str, template: str, handler: str, query: tuple[str, ...] = ()) -> Route:
    rx = re.escape(template)
    rx = rx.replace(re.escape("{case}"), f"(?P<case>{UUID})")
    for name in ("node", "event", "item"):
        rx = rx.replace(re.escape("{" + name + "}"), f"(?P<{name}>{UUID})")
    rx = rx.replace(re.escape("{view}"), "(?P<view>[a-z]+)")
    rx = rx.replace(re.escape("{file}"), r"(?P<file>[a-z]+(?:/[a-z]+)?\.(?:js|css|json|html))")
    return Route(method, template, re.compile(f"^{rx}$"), handler, query)


WEB_KEYS = ("focus", "hops", "sector")

ROUTES = (
    _route("GET", "/", "index", QUERY_KEYS),
    _route("GET", "/c/{case}", "index", QUERY_KEYS),
    _route("GET", "/c/{case}/{view}", "index", QUERY_KEYS),
    _route("GET", "/static/{file}", "static"),
    _route("GET", "/keymap.json", "keymap"),
    _route("GET", "/api/cases", "cases"),
    _route("GET", "/api/cases/{case}/header", "header"),
    _route("GET", "/api/cases/{case}/web", "web_json", WEB_KEYS),
    _route("GET", "/api/cases/{case}/web.svg", "web_svg", WEB_KEYS),
    _route("GET", "/api/cases/{case}/web.list", "web_list", WEB_KEYS),
    _route("GET", "/api/cases/{case}/node/{node}", "node"),
    _route("GET", "/api/cases/{case}/lineage/{event}", "lineage", ("dir",)),
    _route("GET", "/api/cases/{case}/paths", "paths", ("from", "to")),
    _route("GET", "/api/cases/{case}/dossier", "dossier", ("focus",)),
    _route("GET", "/api/cases/{case}/coverage", "coverage"),
    _route("GET", "/api/cases/{case}/blobs/{item}", "blob"),
    _route("GET", "/api/cases/{case}/notices", "notices", ("after",)),
    _route("POST", "/api/cases/{case}/deep-dives", "deep_dive"),
    _route("GET", "/api/kv/{case}/{view}", "kv_get"),
    _route("PUT", "/api/kv/{case}/{view}", "kv_put"),
)


def match(method: str, path: str) -> tuple[Route, dict]:
    """The route for a method and path, or ROUTE_NOT_FOUND or METHOD_REFUSED."""
    found_other = False
    for r in ROUTES:
        m = r.pattern.match(path)
        if m is None:
            continue
        if r.method != method:
            found_other = True
            continue
        params = {k: v.lower() if k in ("case", "node", "event", "item") else v for k, v in m.groupdict().items()}
        return r, params
    raise Refusal("METHOD_REFUSED" if found_other else "ROUTE_NOT_FOUND")


# ---------------------------------------------------------------------------
# responses
# ---------------------------------------------------------------------------


@dataclass
class Response:
    status: int
    content_type: str
    body: bytes
    headers: dict


def json_response(obj, status: int = 200) -> Response:
    body = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return Response(status, "application/json; charset=utf-8", body, {})


CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
}


def static_files() -> dict[str, tuple[str, bytes]]:
    """Every file under app/static, read once at launch: {relative path: (type, bytes)}."""
    out = {}
    for p in sorted(STATIC.rglob("*")):
        if p.is_file() and p.suffix in CONTENT_TYPES:
            out[p.relative_to(STATIC).as_posix()] = (CONTENT_TYPES[p.suffix], p.read_bytes())
    return out


def title_for(case_id: str | None) -> str:
    return f"PLAINSIGHT C-{case_id[:8]}" if case_id else "PLAINSIGHT"


# ---------------------------------------------------------------------------
# the case connection
# ---------------------------------------------------------------------------


def read_only(conn) -> None:
    """Make a connection refuse every write, so SQLite refuses a GET that tries one."""
    conn.execute("PRAGMA query_only=ON")


@contextmanager
def case_store(root, case_id: str, write: bool = False):
    """A store with the case attached, read-only unless `write`. Refuses a case not held."""
    store = db.Store.open(root)
    try:
        if case_id not in store.cases() or not store.attach_case(case_id, create=False):
            raise Refusal("CASE_NOT_HELD")
        if not write:
            read_only(store.conn)
        yield store
    finally:
        try:
            store.conn.execute("PRAGMA query_only=OFF")
        finally:
            store.close()


# ---------------------------------------------------------------------------
# handlers: (app, params, query, body) -> Response
# ---------------------------------------------------------------------------


def h_index(app, params, query, body) -> Response:
    """The page. A case URL with no view is redirected to the landing view, so every
    URL the client keeps names a view (docs/PLAINSIGHT-design.md section 3.1)."""
    if "case" in params and params.get("view") is None:
        location = f"/c/{params['case']}/{config.LANDING_VIEW}"
        if query:
            location += "?" + urlencode(sorted(query.items()))
        return Response(302, "text/plain; charset=utf-8", b"", {"Location": location})
    if "case" in params and params.get("view") not in VIEWS:
        raise Refusal("ROUTE_NOT_FOUND")
    content_type, data = app.static["index.html"]
    title = title_for(params.get("case"))
    html = data.decode("utf-8").replace("<title>PLAINSIGHT</title>", f"<title>{title}</title>", 1)
    return Response(200, content_type, html.encode("utf-8"), {"Set-Cookie": app.cookie()})


def h_static(app, params, query, body) -> Response:
    found = app.static.get(params["file"])
    if found is None:
        raise Refusal("ROUTE_NOT_FOUND")
    return Response(200, found[0], found[1], {})


def h_keymap(app, params, query, body) -> Response:
    content_type, data = app.static["keymap.json"]
    return Response(200, content_type, data, {})


def _case_state(state: str) -> str:
    return {
        "open": "open: held in this store, nothing swept",
        "shredded": "SHREDDED, the case material is gone: only the registry tombstone remains",
        "shred_failed": "SHRED FAILED, the case material may remain: no new run dispatches (RT-11)",
    }.get(state, "a state this view does not render")


def h_cases(app, params, query, body) -> Response:
    store = db.Store.open(app.root)
    try:
        read_only(store.conn)
        out = []
        for case_id in store.cases():
            reg = store.registry(case_id)
            out.append({
                "case_id": case_id,
                "title": title_for(case_id),
                "state": _case_state(reg["state"]),
                "held": store.case_file(case_id).is_file(),
            })
        store.conn.execute("PRAGMA query_only=OFF")
    finally:
        store.close()
    return json_response({"cases": out, "landing_view": config.LANDING_VIEW})


ENVIRONMENT_LINE = {
    "LOCAL": "LOCAL: synthetic corpus files only, and no connector runs on this machine (EG-1)",
    "ISOLATED": "ISOLATED: the case store, read through this view and never copied (EG-3)",
}


def h_header(app, params, query, body) -> Response:
    case_id = params["case"]
    with case_store(app.root, case_id) as store:
        conn = store.conn
        reg = store.registry(case_id)
        rollup: dict[str, dict[str, int]] = {}
        for r in conn.execute("SELECT dimension, bucket, n FROM case_rollup WHERE n != 0 ORDER BY dimension, bucket"):
            rollup.setdefault(r["dimension"], {})[r["bucket"]] = r["n"]
        out = {
            "case_id": case_id,
            "title": title_for(case_id),
            "state": _case_state(reg["state"]),
            "environment": ENVIRONMENT_LINE.get(reg["environment"], reg["environment"]),
            "retention": retention.retention_line(reg),
            "retention_vouch": retention.is_past(reg),
            "anchor": f"anchor_ts {reg['anchor_ts']} ({reg['anchor_reading']})",
            "halt": reads.halt_line(conn),
            "seed_focus": reads.seed_focus(conn, case_id),
            "landing_view": config.LANDING_VIEW,
            "analyst": app.analyst,
            "rollup": rollup,
            "guard_replaced": app.guard.counts(),
            "notices_dropped": app.hub.drop_counts(),
        }
    return json_response(out)


def _hops(query) -> int:
    return web.parse_hops(query.get("hops"))


def h_web_json(app, params, query, body) -> Response:
    case_id = params["case"]
    with case_store(app.root, case_id) as store:
        w = web.build(store.conn, case_id, query.get("focus"), _hops(query), query.get("sector"))
        if w.over_cap:
            twin = web.list_twin(store.conn, case_id, w.focus, w.hops, w.sector)
            twin["cap"] = web.cap_text(w.n_nodes, len(w.edges))
            return json_response(twin)
        return json_response({
            "mode": "web",
            "case_id": case_id,
            "focus": w.focus,
            "hops": w.hops,
            "sector": w.sector,
            "nodes": w.nodes,
            "edges": w.edges,
            "collapsed": web.collapsed_cards(w),
        })


def h_web_svg(app, params, query, body) -> Response:
    case_id = params["case"]
    with case_store(app.root, case_id) as store:
        w = web.build(store.conn, case_id, query.get("focus"), _hops(query), query.get("sector"))
        if w.over_cap:
            raise Refusal("WEB_OVER_CAP", web.cap_text(w.n_nodes, len(w.edges)))
        text = svg.render(w)
    return Response(200, "image/svg+xml; charset=utf-8", text.encode("utf-8"), {})


def h_web_list(app, params, query, body) -> Response:
    case_id = params["case"]
    with case_store(app.root, case_id) as store:
        twin = web.list_twin(store.conn, case_id, query.get("focus"), _hops(query), query.get("sector"))
    return json_response(twin)


def h_node(app, params, query, body) -> Response:
    case_id = params["case"]
    with case_store(app.root, case_id) as store:
        return json_response(inspector.inspect(store.conn, case_id, params["node"]))


def h_lineage(app, params, query, body) -> Response:
    case_id = params["case"]
    with case_store(app.root, case_id) as store:
        if query.get("dir") == "forward":
            return json_response(lineage.forward(store.conn, case_id, params["event"]))
        return json_response(lineage.chain(store.conn, case_id, params["event"]))


def h_paths(app, params, query, body) -> Response:
    case_id = params["case"]
    with case_store(app.root, case_id) as store:
        return json_response(paths.routes(store.conn, case_id, query.get("from"), query.get("to")))


def h_dossier(app, params, query, body) -> Response:
    case_id = params["case"]
    with case_store(app.root, case_id) as store:
        return json_response(dossier_mod.build(store.conn, case_id, query.get("focus")))


def coverage_text(r) -> str:
    target = r["target_ref"][:8]
    if r["state"] == "open":
        return (
            f"OPEN, the watchdog has not closed this interval for {target}: coverage after "
            f"{r['last_verified_at'] or r['t_start']} is unproven"
        )
    if r["verified"]:
        return f"verified coverage of {target} from {r['t_start']} to {r['t_end']} by {r['method']}, closed by {r['closed_by_producer']}"
    return f"UNVERIFIED span for {target} from {r['t_start']} to {r['t_end']}: the system does not vouch for coverage here"


def h_coverage(app, params, query, body) -> Response:
    case_id = params["case"]
    with case_store(app.root, case_id) as store:
        rows = [
            {"interval_id": r["interval_id"], "target_ref": r["target_ref"], "text": coverage_text(r),
             "lineage": r["closed_by_event_id"]}
            for r in store.conn.execute(
                "SELECT * FROM coverage_interval WHERE case_id = ? ORDER BY t_start, interval_id", (case_id,)
            )
        ]
    return json_response({"case_id": case_id, "intervals": rows})


def h_blob(app, params, query, body) -> Response:
    case_id = params["case"]
    with case_store(app.root, case_id) as store:
        item = store.conn.execute("SELECT blob_state FROM item WHERE item_id = ?", (params["item"],)).fetchone()
        if item is None:
            raise Refusal("ITEM_NOT_IN_CASE", "route: blobs")
        if item["blob_state"] != "held":
            reg = store.registry(case_id)
            return json_response({"item_id": params["item"], "raw": "not held", "text": blobs.not_held_line(reg["synthetic"])})
    return json_response({
        "item_id": params["item"],
        "raw": "held, not served",
        "text": "raw bytes held in the case store; this server has no Encryptor configured and does not decrypt them",
    })


def h_deep_dive(app, params, query, body) -> Response:
    case_id = params["case"]
    with case_store(app.root, case_id) as store:
        out = acts.deep_dive(store.conn, case_id, body, app.environment)
    return json_response(out, status=409)


def h_kv_get(app, params, query, body) -> Response:
    case_id = params["case"]
    if params["view"] not in kv.TOKENS:
        raise Refusal("ROUTE_NOT_FOUND")
    with case_store(app.root, case_id) as store:
        rows = store.conn.execute(
            "SELECT key, value_json FROM workspace_kv WHERE analyst = ? AND view = ? ORDER BY key",
            (app.analyst, params["view"]),
        )
        values = {r["key"]: json.loads(r["value_json"]) for r in rows}
    return json_response({"view": params["view"], "values": values})


def h_kv_put(app, params, query, body) -> Response:
    """Write workspace keys: closed keys, and values that are numbers, booleans, closed tokens or uuids."""
    case_id = params["case"]
    if not isinstance(body, dict) or not body:
        raise Refusal("BODY_REFUSED", "route: kv takes a JSON object of workspace keys")
    for key, value in body.items():
        if key not in kv.KEYS:
            raise Refusal("KV_KEY_REFUSED")
        if params["view"] not in kv.TOKENS or not kv.legal_value(value):
            raise Refusal("KV_VALUE_REFUSED", f"key={key}")
    with case_store(app.root, case_id, write=True) as store:
        for key, value in sorted(body.items()):
            kv.put(store, case_id, app.analyst, params["view"], key, value)
    return json_response({"view": params["view"], "written": sorted(body)})


HANDLERS = {
    "index": h_index,
    "static": h_static,
    "keymap": h_keymap,
    "cases": h_cases,
    "header": h_header,
    "web_json": h_web_json,
    "web_svg": h_web_svg,
    "web_list": h_web_list,
    "node": h_node,
    "lineage": h_lineage,
    "paths": h_paths,
    "dossier": h_dossier,
    "coverage": h_coverage,
    "blob": h_blob,
    "deep_dive": h_deep_dive,
    "kv_get": h_kv_get,
    "kv_put": h_kv_put,
}
