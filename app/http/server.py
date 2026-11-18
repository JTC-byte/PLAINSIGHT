"""The stdlib HTTP server: 127.0.0.1 only, one guard, one notice hub.

python -m app serve --store <root> --analyst <name> starts it. It binds
127.0.0.1 and refuses any other address with BIND_REFUSED_LOCAL before a socket
exists. A random token is minted per launch and set as an HttpOnly,
SameSite=Strict cookie on the page, named for the bound port, because a browser
keeps one cookie per name for a host whatever its port; every POST and PUT must
carry it. The session's human identity comes from --analyst, never from a form,
and must be in the deployment's human identity list.

Every request must name this server in its Host header, 127.0.0.1 or localhost
with the bound port, so a request sent under a host name that a DNS rebinding
points at this loopback is refused. A POST or PUT is also authorized by the page
that sent it (docs/PLAINSIGHT-design.md amendment 9.27), and each write rule is
decided before any byte of the body is read: an Origin header, when present,
must be this server's own origin; a Sec-Fetch-Site header, when present, must be
same-origin or none; the cookie must carry the launch token; and the
Content-Type must be application/json. A header sent on more than one line is
read as one value, its lines joined by a comma, which no rule admits, so a Host,
Origin, Sec-Fetch-Site, Content-Type or Content-Length sent on two lines stands
for no request even when each line is admissible, and a Cookie sent on two
lines carries no token. A page on another port of this host is the same site,
so the browser attaches the cookie to that page's requests under
SameSite=Strict, and the Host check passes it, because its browser names this
server in Host. Its Origin names its own port, and a POST body it can send
without a preflight is never application/json. A write that carries neither
header, as a command-line client sends, is admitted on the cookie and the
Content-Type.

A response to a request whose body was not read, a refused write among them, is
written before any byte of that body is read. The server then stops sending,
reads and discards what the client sends of the body, never parsing it, up to
its declared Content-Length capped at MAX_BODY and for at most DISCARD_SECONDS,
and closes. A server that closed at once would meet a body still on its way
with a reset, and a Windows client's stack drops an answer it has received when
a reset arrives, so the page would see a network error in place of the refusal
and its moves. RFC 9112 section 9.6 describes this staged close. The notice
stream holds its connection until it ends. A stream the server stops returns
before the discard, and the server closes it. A stream its client closes, or
one a fault ends, reaches the discard once it is over: a page's stream declares
no body, so nothing is read, and a client that has closed ends the read at once.

The listening socket shares its port with no other socket, by options chosen
per platform. Where the platform offers exclusive use, which is Windows, it is
bound with SO_EXCLUSIVEADDRUSE and with SO_REUSEADDR off, because there
SO_REUSEADDR would let another process bind the port this server holds.
Elsewhere it is bound with SO_REUSEADDR on, as the standard library binds it:
Linux refuses a second bind to a listening port whatever that option says, and
without it refuses a restart on the port while the port's last connections
wait out TIME_WAIT. SO_REUSEPORT is off everywhere. A port the platform refuses
to bind, one another socket listens on among them, is refused with
BIND_REFUSED_PORT.

Every response carries Cache-Control: no-store, the Content-Security-Policy
default-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action
'none', Referrer-Policy: no-referrer, X-Content-Type-Options: nosniff,
Cross-Origin-Resource-Policy: same-origin, and a Permissions-Policy that denies
the camera, the microphone and geolocation. A route's own header never replaces
one of these. There is no CDN, no web font and no build step.

A log line is the fixed tuple (ts, method, route template, status, ms), plus the
exception's type name on a fault. A path, a query, a body or an exception
message is never logged. The stdlib's own request and error logging is
overridden so it cannot write the request line, and an exception raised outside
the dispatcher is logged by its type name and prints no traceback.

Once a response's status line is sent, nothing else is written for that
request: a fault inside the notice stream ends the stream and closes the
connection, so a client never reads a second response inside an event stream.
"""

from __future__ import annotations

import datetime as dt
import errno
import hmac
import json
import re
import secrets
import socket
import sys
import threading
import time
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

from app import config
from app.http import guard as guard_mod
from app.http import notices, routes
from app.http import overlay as overlay_mod
from app.model import reads
from app.refusals import REFUSALS, Refusal
from app.store import db, ingest

#: The session cookie's name. App.cookie_name() adds the bound port to it.
COOKIE = "ps_token"
MAX_BODY = 8192

#: The longest the server reads and discards the unread body of a request it has answered before it closes the
#: connection, in seconds (amendment 9.27). The design gives no number, and RFC 9112 section 9.6 gives none for
#: this staged close. One second is a reading of 2026-11-16 that awaits the maintainer's confirmation: in 800
#: POSTs from http.client measured on this workstation that day, no body came more than 0.62 ms after its head;
#: the controls see a refusal reach a client whose body is 200 ms late; and a client that declares a body and
#: never sends it holds one server thread for one second after its answer was written.
DISCARD_SECONDS = 1.0

#: Every response's security headers. form-action 'none' has the browser refuse a form's own submission, because
#: every form the front ends build is sent by script; Cross-Origin-Resource-Policy has it refuse this server's
#: responses to a page on another origin that loads them as a subresource, such as web.svg as an image; the
#: Permissions-Policy denies features no view uses (amendment 9.27).
SECURITY_HEADERS = {
    "Cache-Control": "no-store",
    "Content-Security-Policy": "default-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'",
    "Referrer-Policy": "no-referrer",
    "X-Content-Type-Options": "nosniff",
    "Cross-Origin-Resource-Policy": "same-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}

#: The Sec-Fetch-Site values a write may carry: a request from this server's own page, or one the user started
#: in the address bar. A page on another port of this host sends same-site, and one on another host cross-site.
WRITE_FETCH_SITES = ("same-origin", "none")

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
    "ACT_UNKNOWN": 400,
    "ACT_REASON_REQUIRED": 400,
    "ACT_MEMBER_KIND_REFUSED": 400,
    "TOKEN_REFUSED": 403,
    "HOST_REFUSED": 403,
    "ORIGIN_REFUSED": 403,
    "CONTENT_TYPE_REFUSED": 415,
    "ACT_LOCAL_SYNTHETIC_CASE_ONLY": 403,
    "ACT_LOCAL_PENDING_DECISION": 403,
    "ROUTE_NOT_FOUND": 404,
    "CASE_NOT_HELD": 404,
    "NODE_NOT_IN_CASE": 404,
    "EVENT_NOT_IN_CASE": 404,
    "ITEM_NOT_IN_CASE": 404,
    "CLAIM_NOT_IN_CASE": 404,
    "METHOD_REFUSED": 405,
    "WEB_OVER_CAP": 409,
    "CASE_CLOSED_TO_WRITES": 409,
    "DEEP_DIVE_NOT_DISPATCHED": 409,
    "ACT_TARGET_ALREADY_PROMOTED": 409,
    "ACT_TARGET_ALREADY_REVOKED": 409,
    "ACT_REFUSED_BY_MODEL": 422,
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


#: HTTP's optional whitespace, the space and the horizontal tab (RFC 9110 section 5.6.3). str.strip() with no
#: argument also removes characters that are not HTTP whitespace, such as a vertical tab or a no-break space.
OWS = " \t"


def json_content_type(value) -> bool:
    """True for a Content-Type of application/json, alone or with one charset parameter naming utf-8, in any
    letter case, with optional spaces and tabs around the type, the parameter's name and its value and no other
    character. The body is read as UTF-8, so a charset naming another encoding is not admitted. A page on
    another origin can send a POST whose body is text/plain, application/x-www-form-urlencoded or
    multipart/form-data, or carries no Content-Type, without a preflight, and a POST of application/json, or any
    PUT, only after one, which this server refuses: OPTIONS answers METHOD_REFUSED."""
    if not isinstance(value, str):
        return False
    media, _, params = value.partition(";")
    if media.strip(OWS).lower() != "application/json":
        return False
    params = params.strip(OWS)
    if not params:
        return True
    name, eq, charset = params.partition("=")
    return bool(eq) and name.strip(OWS).lower() == "charset" and charset.strip(OWS).strip('"').lower() == "utf-8"


def with_security_headers(headers: dict) -> dict:
    """A response's headers with SECURITY_HEADERS set last. A route's header that names one of them, in any
    letter case, is dropped, so no route can send a weaker policy beside or in place of the configured one."""
    security = {k.lower() for k in SECURITY_HEADERS}
    out = {k: v for k, v in headers.items() if k.lower() not in security}
    out.update(SECURITY_HEADERS)
    return out


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def stderr_sink(record: tuple) -> None:
    print("\t".join(str(x) for x in record), file=sys.stderr, flush=True)


class App:
    """What one launch holds: the store root, the identity, the token, the guard and the hub."""

    def __init__(self, root, analyst: str, log_sink=None, ui: str = "classic"):
        self.root = root
        self.analyst = analyst
        self.environment = config.environment()
        self.token = secrets.token_urlsafe(32)
        self.guard = guard_mod.Guard.from_store(root)
        self.hub = notices.Hub(self.guard)
        self.ui = ui
        self.static = routes.static_files(routes.UIS[ui])
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

    def authorities(self) -> set[str]:
        """The two Host values this server answers: its loopback address and localhost, each with its port."""
        return {f"127.0.0.1:{self.port}", f"localhost:{self.port}"}

    def origins(self) -> set[str]:
        """This server's own origins, one for each authority the Host check accepts."""
        return {f"http://{a}" for a in self.authorities()}

    def cookie_name(self) -> str:
        """The session cookie's name, which carries the bound port. A browser keeps one cookie per name for a
        host whatever its port, so under one name a second launch on 127.0.0.1 would overwrite the first
        launch's token, and the first launch's page would be refused every write."""
        return f"{COOKIE}_{self.port}"

    def cookie(self) -> str:
        return f"{self.cookie_name()}={self.token}; HttpOnly; SameSite=Strict; Path=/"

    def log(self, record: tuple) -> None:
        self.log_sink(record)

    def refresh_guard(self) -> None:
        """Reload the guard when the store moved, whichever process appended to it."""
        if not self.guard.current(self.root):
            self.guard.reload(self.root)


#: True where the platform offers a port for exclusive use, SO_EXCLUSIVEADDRUSE, which is Windows. Server.server_bind
#: reads it at each bind and chooses the socket's options by it (review finding 8 of 2026-11-14, amendment 9.27).
EXCLUSIVE_USE = hasattr(socket, "SO_EXCLUSIVEADDRUSE")


class Server(ThreadingHTTPServer):
    """The stdlib's threading server, bound so that no other socket shares its port (review finding 8 of
    2026-11-14), by options chosen per platform. On Windows a second socket that sets SO_REUSEADDR may bind a port
    held by a socket that set it too, as the stdlib's HTTPServer does, and take its connections, so there
    SO_REUSEADDR stays off and SO_EXCLUSIVEADDRUSE, which refuses every second bind to the port, is set. Elsewhere
    SO_REUSEADDR is set, as the stdlib and socket.create_server set it: Linux refuses a second bind to a listening
    port unless both sockets set SO_REUSEPORT, and without SO_REUSEADDR it refuses a restart on the port while the
    port's last connections wait out TIME_WAIT, for 60.3 s in a second reader's run on Linux on 2026-11-16.
    SO_REUSEPORT stays off everywhere. The stdlib's own switch for SO_REUSEADDR stays off, so that server_bind
    alone decides it."""

    daemon_threads = True
    allow_reuse_address = False
    allow_reuse_port = False

    def __init__(self, address, handler, app: App):
        self.app = app
        super().__init__(address, handler)

    def server_bind(self) -> None:
        """Set the platform's option before the stdlib binds: SO_EXCLUSIVEADDRUSE where EXCLUSIVE_USE is true, and
        SO_REUSEADDR elsewhere. Windows refuses the two together, in either order."""
        if EXCLUSIVE_USE:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        else:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        super().server_bind()

    def handle_error(self, request, client_address) -> None:
        """An exception raised outside _dispatch, while the stdlib sets up, parses or closes a connection. The
        stdlib's default prints a traceback to stderr, which carries the exception's message; this logs the
        exception's type name only, as _dispatch's fault branch does, and prints no traceback. The method, the
        status and the duration are not known here, so each is written as -."""
        try:
            self.app.log((now_iso(), "-", "outside dispatch", "-", "-", type(sys.exc_info()[1]).__name__))
        except Exception:  # noqa: BLE001 - a sink that fails here has nowhere to report, and nothing is printed
            pass


#: The server class make_server builds. A test replaces it to prove the bind
#: refusal happens before any socket is created.
SERVER_CLASS = Server


def bind_server(host: str, port: int, app: App) -> Server:
    """The server bound to (host, port), or BIND_REFUSED_PORT when the platform refuses the bind, as it does for a
    port another socket listens on. The detail names the port and the error's code, never the platform's message."""
    try:
        return SERVER_CLASS((host, port), Handler, app)
    except OSError as exc:
        code = errno.errorcode.get(exc.errno) or f"errno {exc.errno}"
        raise Refusal("BIND_REFUSED_PORT", f"port {port}: {code}") from None


def make_server(store=None, host: str = "127.0.0.1", port: int = 0, analyst: str | None = None, log_sink=None,
                ui: str = "classic", overlay=None):
    """(server, app), bound and not yet serving. Refuses before binding when it must. `ui` names the front end
    the page and /static/ serve, one of routes.UIS; the API is the same for both. `overlay`, showcase only, is a
    JSON file of fictional display stand-ins read once and served as /static/overlay.json (app/http/overlay.py)."""
    check_bind(host)
    if ui not in routes.UIS:
        raise ValueError(f"ui must be one of {', '.join(sorted(routes.UIS))}")
    if overlay is not None and ui != "showcase":
        raise ValueError("an overlay is drawn by the showcase front end only; add --ui showcase or drop --overlay")
    root = db.resolve_root(store)
    overlay_bytes = overlay_mod.read_overlay(overlay, root) if overlay is not None else None
    probe = db.Store.open(root)
    probe.close()
    if not analyst or analyst not in config.deployment_humans():
        raise Refusal("ANALYST_UNKNOWN")
    app = App(root, analyst, log_sink, ui)
    if overlay_bytes is not None:
        app.static["overlay.json"] = ("application/json; charset=utf-8", overlay_bytes)
    server = bind_server(host, port, app)
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
        self._body_read = False
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
            params = routes.registered(self.app.root, params)
            query = routes.parse_query(split.query, route.query)
            body = None
            if method in ("POST", "PUT"):
                self._check_origin()
                self._check_fetch_site()
                self._check_token()
                self._check_content_type()
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
        self._discard_unread_body()

    # -- checks -----------------------------------------------------------

    def _check_host(self) -> None:
        """HOST_REFUSED unless Host names this server. A browser names the request's target in Host, so this
        refuses a host name rebound to this loopback and passes a page on another origin of this machine. A Host
        sent on two lines is read as one value, which names no authority, so neither line stands for the
        request."""
        if self._header_value("Host") not in self.app.authorities():
            raise Refusal("HOST_REFUSED")

    def _header_value(self, name: str) -> str | None:
        """A request header's value, or None when the request does not carry it. A header sent on more than one
        line is read as one value, its lines joined by a comma and a space, as HTTP combines repeated field lines
        (RFC 9110 section 5.3), so no one of its lines can stand for the request, whichever line it is. No rule
        that reads a header here admits a combined value, so a write that sends Origin, Sec-Fetch-Site,
        Content-Type or Content-Length on two lines, and any request that sends Host on two, is refused even when
        each line is admissible."""
        lines = self.headers.get_all(name)
        return ", ".join(lines) if lines else None

    def _check_origin(self) -> None:
        """ORIGIN_REFUSED for a write whose Origin is present and is not exactly this server's own. A browser
        sends Origin on every POST and PUT, and a page on another port of this host sends its own port in it."""
        origin = self._header_value("Origin")
        if origin is not None and origin not in self.app.origins():
            raise Refusal("ORIGIN_REFUSED", "header: Origin")

    def _check_fetch_site(self) -> None:
        """ORIGIN_REFUSED for a write whose Sec-Fetch-Site is present and is not exactly same-origin or none. A
        page cannot set this header; a browser that sends it names the relation of the sending page to this one."""
        site = self._header_value("Sec-Fetch-Site")
        if site is not None and site not in WRITE_FETCH_SITES:
            raise Refusal("ORIGIN_REFUSED", "header: Sec-Fetch-Site")

    def _check_token(self) -> None:
        """TOKEN_REFUSED unless one Cookie header carries this launch's token under the name that carries the
        bound port. A browser sends one Cookie header (RFC 6265 section 5.4). One sent on two lines carries no
        token here: read as one value, as Origin is, its lines would parse as one cookie list in which the last
        value of a repeated name wins, so a line would stand for the request. The value and the token are compared
        as bytes: hmac.compare_digest raises a TypeError for a string that holds a character outside ASCII, which a
        cookie's value may hold, and the server answered such a cookie with SERVER_FAULT, not TOKEN_REFUSED."""
        lines = self.headers.get_all("Cookie") or []
        jar = SimpleCookie()
        if len(lines) == 1:
            try:
                jar.load(lines[0])
            except Exception:  # noqa: BLE001 - an unparseable cookie is a missing one
                jar = SimpleCookie()
        got = jar.get(self.app.cookie_name())
        if got is None or not hmac.compare_digest(got.value.encode("utf-8"), self.app.token.encode("utf-8")):
            raise Refusal("TOKEN_REFUSED")

    def _check_content_type(self) -> None:
        """CONTENT_TYPE_REFUSED for a write that is not application/json, before its body is read, so a
        request another origin's page sends without a preflight never carries a body this server parses."""
        if not json_content_type(self._header_value("Content-Type")):
            raise Refusal("CONTENT_TYPE_REFUSED")

    def _read_body(self):
        """The body as JSON, read once every write rule has admitted the request. A Content-Length sent on two
        lines is read as one value, which is no length."""
        length = self._header_value("Content-Length")
        if not routes.ascii_digits(length, 5) or int(length) > MAX_BODY:
            raise Refusal("BODY_REFUSED", "a body needs one Content-Length header of at most 8192 bytes")
        self._body_read = True
        raw = self.rfile.read(int(length))
        try:
            return json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, ValueError):
            raise Refusal("BODY_REFUSED", "the body is not JSON") from None

    def _discard_unread_body(self) -> None:
        """After the answer to a request whose body was not read: stop sending, then read and drop what the client
        sends of its body, never parsing it, up to its declared Content-Length capped at MAX_BODY, for at most
        DISCARD_SECONDS, and return, after which the server closes the connection. A server that closed with the
        body still on its way would meet it with a reset, and a Windows client's stack drops the answer it had
        received when the reset arrives. A Content-Length that is absent, sent on two lines, not ASCII digits, or
        longer than the twelve digits routes.ascii_digits reads declares no body, and nothing is read. A notice
        stream the server stops returns from _dispatch before this runs; one its client closes, or one a fault ends,
        reaches it once the stream is over."""
        if self._body_read:
            return
        length = self._header_value("Content-Length")
        if not routes.ascii_digits(length):
            return
        left = min(int(length), MAX_BODY)
        if left == 0:
            return
        self.close_connection = True
        try:
            self.connection.shutdown(socket.SHUT_WR)
            end = time.monotonic() + DISCARD_SECONDS
            while left > 0:
                wait = end - time.monotonic()
                if wait <= 0:
                    break
                self.connection.settimeout(wait)
                chunk = self.rfile.read1(left)
                if not chunk:
                    break
                left -= len(chunk)
        except OSError:  # a deadline passed or the client reset: the connection closes either way
            pass

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
        for k, v in with_security_headers(headers).items():
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
            for k, v in with_security_headers({"Content-Type": "text/event-stream; charset=utf-8"}).items():
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
