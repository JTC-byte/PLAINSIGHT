"""The stdlib HTTP server: 127.0.0.1 only, one guard, one notice hub.

python -m app serve --store <root> --analyst <name> starts it. It binds
127.0.0.1 and refuses any other address with BIND_REFUSED_LOCAL before a socket
exists. A random token is minted per launch and set as an HttpOnly,
SameSite=Strict cookie on the page; every POST and PUT must carry it. The
session's human identity comes from --analyst, never from a form, and must be
in the deployment's human identity list.

Every response carries Cache-Control: no-store, the Content-Security-Policy
default-src 'self'; frame-ancestors 'none'; base-uri 'none', Referrer-Policy:
no-referrer and X-Content-Type-Options: nosniff. There is no CDN, no web font
and no build step.

A log line is the fixed tuple (ts, method, route template, status, ms), plus the
exception's type name on a fault. A path, a query, a body or an exception
message is never logged. The stdlib's own request and error logging is
overridden so it cannot write the request line.

Once a response's status line is sent, nothing else is written for that
request: a fault inside the notice stream ends the stream and closes the
connection, so a client never reads a second response inside an event stream.
"""

from __future__ import annotations

import datetime as dt
import hmac
import json
import re
import secrets
import sys
import threading
import time
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

from app import config
from app.http import guard as guard_mod
from app.http import notices, routes
from app.model import reads
from app.refusals import REFUSALS, Refusal
from app.store import db, ingest

COOKIE = "ps_token"
MAX_BODY = 8192

SECURITY_HEADERS = {
    "Cache-Control": "no-store",
    "Content-Security-Policy": "default-src 'self'; frame-ancestors 'none'; base-uri 'none'",
    "Referrer-Policy": "no-referrer",
    "X-Content-Type-Options": "nosniff",
}

#: HTTP status per refusal code. A code not listed is a store fault, 500.
STATUS = {
    "QUERY_KEY_REFUSED": 400,
    "QUERY_VALUE_REFUSED": 400,
    "REQUEST_MALFORMED": 400,
    "REQUEST_VALUE_REFUSED": 400,
    "FOCUS_REQUIRED": 400,
    "BODY_REFUSED": 400,
    "KV_KEY_REFUSED": 400,
    "KV_VALUE_REFUSED": 400,
    "DEEP_DIVE_ONE_NODE_PER_ACT": 400,
    "TOKEN_REFUSED": 403,
    "HOST_REFUSED": 403,
    "ROUTE_NOT_FOUND": 404,
    "CASE_NOT_HELD": 404,
    "NODE_NOT_IN_CASE": 404,
    "EVENT_NOT_IN_CASE": 404,
    "ITEM_NOT_IN_CASE": 404,
    "CLAIM_NOT_IN_CASE": 404,
    "METHOD_REFUSED": 405,
    "WEB_OVER_CAP": 409,
    "DEEP_DIVE_NOT_DISPATCHED": 409,
    "STORE_NOT_INITIALIZED": 503,
}

#: Seconds between a notice stream's polls of the log for a write by another process.
SSE_POLL = 2.0

#: The refusal for each status the stdlib's request parser raises before routing.
#: 501 is a method with no handler; every other parser status is a request that
#: did not parse (400, 414 and 431 for size, 505 for the version).
STDLIB_REFUSAL = {501: "METHOD_REFUSED"}

_TITLE_RE = re.compile(rb"<title>(.*?)</title>", re.S)


def check_bind(host: str) -> None:
    """BIND_REFUSED_LOCAL for any address but 127.0.0.1. Called before a socket exists."""
    if host not in config.BIND_HOSTS:
        raise Refusal("BIND_REFUSED_LOCAL")


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def stderr_sink(record: tuple) -> None:
    print("\t".join(str(x) for x in record), file=sys.stderr, flush=True)


class App:
    """What one launch holds: the store root, the identity, the token, the guard and the hub."""

    def __init__(self, root, analyst: str, log_sink=None):
        self.root = root
        self.analyst = analyst
        self.environment = config.environment()
        self.token = secrets.token_urlsafe(32)
        self.guard = guard_mod.Guard.from_store(root)
        self.hub = notices.Hub(self.guard)
        self.static = routes.static_files()
        self.log_sink = log_sink or stderr_sink
        self.port = None
        self.sse_poll = SSE_POLL
        self._listener = self.hub.publish

    def attach(self) -> None:
        ingest.LISTENERS.append(self._listener)

    def close(self) -> None:
        if self._listener in ingest.LISTENERS:
            ingest.LISTENERS.remove(self._listener)
        self.hub.close()

    def cookie(self) -> str:
        return f"{COOKIE}={self.token}; HttpOnly; SameSite=Strict; Path=/"

    def log(self, record: tuple) -> None:
        self.log_sink(record)

    def refresh_guard(self) -> None:
        """Reload the guard when the store moved, whichever process appended to it."""
        if not self.guard.current(self.root):
            self.guard.reload(self.root)


class Server(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, handler, app: App):
        self.app = app
        super().__init__(address, handler)


#: The server class make_server builds. A test replaces it to prove the bind
#: refusal happens before any socket is created.
SERVER_CLASS = Server


def make_server(store=None, host: str = "127.0.0.1", port: int = 0, analyst: str | None = None, log_sink=None):
    """(server, app), bound and not yet serving. Refuses before binding when it must."""
    check_bind(host)
    root = db.resolve_root(store)
    probe = db.Store.open(root)
    probe.close()
    if not analyst or analyst not in config.deployment_humans():
        raise Refusal("ANALYST_UNKNOWN")
    app = App(root, analyst, log_sink)
    server = SERVER_CLASS((host, port), Handler, app)
    app.port = server.server_address[1]
    app.attach()
    return server, app


def start(server) -> threading.Thread:
    t = threading.Thread(target=server.serve_forever, name="plainsight-http", daemon=True)
    t.start()
    return t


def stop(server) -> None:
    server.app.close()
    server.shutdown()
    server.server_close()


def refusal_body(refusal: Refusal) -> bytes:
    """An error body: the code, the governed text, and nothing from the request."""
    c = REFUSALS[refusal.code]
    body = {"refused": refusal.code, "text": Refusal(refusal.code).render(), "rule": c.rule, "moves": list(c.moves)}
    if refusal.detail:
        body["detail"] = refusal.detail
    return json.dumps(body, ensure_ascii=False, sort_keys=True).encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    server_version = "PLAINSIGHT"
    sys_version = ""

    # -- the stdlib's logging, silenced: it writes the request line --------

    def log_message(self, format, *args):  # noqa: A002 - the stdlib's signature
        return

    def log_request(self, code="-", size="-"):
        return

    def log_error(self, format, *args):  # noqa: A002
        return

    def send_error(self, code, message=None, explain=None):
        """The stdlib calls this before routing: an unknown method, or a request that did
        not parse. Answer with the refusal that names it, without echoing the request."""
        self._template = getattr(self, "_template", "unparsed")
        self._send_refusal(Refusal(STDLIB_REFUSAL.get(code, "REQUEST_MALFORMED")), status=code)

    # -- methods ----------------------------------------------------------

    def do_GET(self):
        self._dispatch("GET")

    def do_POST(self):
        self._dispatch("POST")

    def do_PUT(self):
        self._dispatch("PUT")

    def do_DELETE(self):
        self._dispatch("DELETE")

    def do_PATCH(self):
        self._dispatch("PATCH")

    def do_HEAD(self):
        self._dispatch("HEAD")

    @property
    def app(self) -> App:
        return self.server.app

    def _dispatch(self, method: str) -> None:
        t0 = time.monotonic()
        self._template = "unmatched"
        self._status = 0
        self._sent = False
        fault = None
        try:
            self._check_host()
            target = self.path
            self.app.refresh_guard()
            if self.app.guard.scan_request(target):
                self.app.guard.count("request")
                raise Refusal("REQUEST_VALUE_REFUSED")
            split = urlsplit(target)
            if split.scheme or split.netloc or split.fragment:
                raise Refusal("ROUTE_NOT_FOUND")
            if method in ("HEAD", "DELETE", "PATCH"):
                raise Refusal("METHOD_REFUSED")
            route, params = routes.match(method, split.path)
            self._template = route.template
            query = routes.parse_query(split.query, route.query)
            body = None
            if method in ("POST", "PUT"):
                self._check_token()
                body = self._read_body()
            if route.handler == "notices":
                self._notices(params, query)
                return
            response = routes.HANDLERS[route.handler](self.app, params, query, body)
            self._send(response)
        except Refusal as refusal:
            if self._sent:
                fault = refusal.code
                self.close_connection = True
            else:
                self._send_refusal(refusal)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            self._status = self._status or 499
        except Exception as exc:  # noqa: BLE001 - logged by type name only
            fault = type(exc).__name__
            if self._sent:
                self.close_connection = True
            else:
                self._send_refusal(Refusal("SERVER_FAULT"), status=500)
        finally:
            ms = int((time.monotonic() - t0) * 1000)
            record = (now_iso(), method, self._template, self._status, ms)
            self.app.log(record + ((fault,) if fault else ()))

    # -- checks -----------------------------------------------------------

    def _check_host(self) -> None:
        host = self.headers.get("Host")
        allowed = {f"127.0.0.1:{self.app.port}", f"localhost:{self.app.port}"}
        if host not in allowed:
            raise Refusal("HOST_REFUSED")

    def _check_token(self) -> None:
        jar = SimpleCookie()
        try:
            jar.load(self.headers.get("Cookie") or "")
        except Exception:  # noqa: BLE001 - an unparseable cookie is a missing one
            jar = SimpleCookie()
        got = jar.get(COOKIE)
        if got is None or not hmac.compare_digest(got.value, self.app.token):
            raise Refusal("TOKEN_REFUSED")

    def _read_body(self):
        length = self.headers.get("Content-Length")
        if not routes.ascii_digits(length, 5) or int(length) > MAX_BODY:
            raise Refusal("BODY_REFUSED", "a body needs a Content-Length of at most 8192 bytes")
        raw = self.rfile.read(int(length))
        try:
            return json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, ValueError):
            raise Refusal("BODY_REFUSED", "the body is not JSON") from None

    # -- sending ----------------------------------------------------------

    def _mark_sent(self) -> None:
        """Record that a status line is on the wire, so no second response follows it."""
        self._sent = True

    def _guarded_headers(self, headers: dict, status: int) -> tuple[dict, int, bool]:
        out = {}
        replace = False
        for k, v in headers.items():
            if self.app.guard.scan(v) or self.app.guard.scan(k):
                self.app.guard.count("Location" if k.lower() == "location" else "header")
                if k.lower() == "location":
                    replace = True
                continue
            out[k] = v
        return out, status, replace

    def _send(self, response: routes.Response) -> None:
        headers = {"Content-Type": response.content_type, **response.headers}
        headers, status, replace = self._guarded_headers(headers, response.status)
        body = response.body
        if response.status >= 400 and self.app.guard.scan(body):
            self.app.guard.count("error body")
            replace = True
        if replace:
            self._send_refusal(Refusal("EGRESS_GUARD_REPLACED"), status=500)
            return
        m = _TITLE_RE.search(body) if response.content_type.startswith("text/html") else None
        if m and self.app.guard.scan(m.group(1)):
            self.app.guard.count("title")
            body = body.replace(m.group(0), b"<title>PLAINSIGHT</title>", 1)
        self._write(status, headers, body)

    def _send_refusal(self, refusal: Refusal, status: int | None = None) -> None:
        status = status or STATUS.get(refusal.code, 500)
        body = refusal_body(refusal)
        if self.app.guard.scan(body):
            self.app.guard.count("error body")
            body = refusal_body(Refusal("EGRESS_GUARD_REPLACED"))
            status = 500
        self._write(status, {"Content-Type": "application/json; charset=utf-8"}, body)

    def _write(self, status: int, headers: dict, body: bytes) -> None:
        self._status = status
        self._mark_sent()
        self.send_response(status)
        for k, v in {**SECURITY_HEADERS, **headers}.items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    # -- the notice stream ------------------------------------------------

    def _current_seq(self, case_id: str) -> int:
        with routes.case_store(self.app.root, case_id) as store:
            return reads.max_seq(store.conn, case_id)

    def _notices(self, params: dict, query: dict) -> None:
        case_id = params["case"]
        current = self._current_seq(case_id)
        after = query.get("after")
        last_id = self.headers.get("Last-Event-ID")
        if after is None and routes.ascii_digits(last_id):
            after = last_id
        after = int(after) if after is not None else None
        q = self.app.hub.subscribe(case_id)
        try:
            self._status = 200
            self._mark_sent()
            self.send_response(200)
            for k, v in {**SECURITY_HEADERS, "Content-Type": "text/event-stream; charset=utf-8"}.items():
                self.send_header(k, v)
            self.end_headers()
            last = current
            if after is not None and current > after:
                self._frame(notices.resume_notice(case_id, current))
            self.wfile.flush()
            while not self.app.hub.closed:
                try:
                    item = q.get(timeout=self.app.sse_poll)
                except Exception:  # noqa: BLE001 - queue.Empty: poll the log
                    seq = self._current_seq(case_id)
                    if seq > last:
                        self.app.guard.stale = True
                        self.app.refresh_guard()
                        self._frame(notices.resume_notice(case_id, seq))
                        last = seq
                    else:
                        self.wfile.write(b": keepalive\n\n")
                    self.wfile.flush()
                    continue
                if item is None:
                    break
                self._frame(item)
                last = max(last, item["seq"])
                self.wfile.flush()
        finally:
            self.app.hub.unsubscribe(case_id, q)

    def _frame(self, notice: dict) -> None:
        if self.app.hub.check(notice) is not None:
            return
        self.wfile.write(notices.frame(notice))
