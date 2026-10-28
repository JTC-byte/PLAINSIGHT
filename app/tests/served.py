"""A served corpus store for the web and HTTP tests.

The corpus is ingested once per process, through the real door, into a template
store under the system temporary directory (never under the repository), and
each test copies the template into its own tmp_path. The notices that ingest
published are kept, so a test can replay them into a live server's stream.

Client reaches the server through loopback_socket and loopback_http in
app/tests/conftest.py, each of which names 127.0.0.1 on the call that connects,
so a test may refuse every name lookup and every connection to any other
address and port and still reach the server: anything in the app that opened an
outbound connection would then be refused and recorded.
"""

from __future__ import annotations

import atexit
import shutil
import socket
import tempfile
from dataclasses import dataclass
from pathlib import Path

from app.http import server
from app.store import db, door, ingest
from app.tests.conftest import loopback_http, loopback_socket
from app.tests.helpers import CASE, CORPUS

FOCUS = "60b4e95a-46f7-5441-b17f-d7318984b45d"

_template: dict = {}


def template() -> tuple[Path, list[dict]]:
    """(the template store root, the notices its ingest published)."""
    root = _template.get("root")
    if root is not None and root.is_dir():
        return root, _template["notices"]
    tmp = Path(tempfile.mkdtemp(prefix="plainsight-template-"))
    atexit.register(shutil.rmtree, tmp, True)
    root = tmp / "store"
    captured: list[dict] = []
    store = db.Store.init(root)
    try:
        source = door.check_source(CORPUS)
        ingest.LISTENERS.append(captured.append)
        try:
            result = ingest.ingest_batch(store, door.read_rows(CORPUS), None, source=source)
        finally:
            ingest.LISTENERS.remove(captured.append)
        assert result.landed == 44, "the template store did not land the corpus"
    finally:
        store.close()
    _template.update(root=root, notices=captured)
    return root, captured


def corpus_copy(ctx, name: str = "served") -> Path:
    root, _ = template()
    dst = ctx.tmp / name
    shutil.copytree(root, dst)
    return dst


def open_case(root: Path):
    store = db.Store.open(root)
    store.attach_case(CASE, create=False)
    return store


@dataclass
class Resp:
    status: int
    headers: list[tuple[str, str]]
    body: bytes

    def header(self, name: str) -> str | None:
        for k, v in self.headers:
            if k.lower() == name.lower():
                return v
        return None

    def json(self):
        import json

        return json.loads(self.body.decode("utf-8"))


class Client:
    """A live server on 127.0.0.1 and a client for it. Closed by ctx.close()."""

    def __init__(self, ctx, root: Path | None = None):
        self.root = root or corpus_copy(ctx)
        self.logs: list[tuple] = []
        self.server, self.app = server.make_server(self.root, analyst="analyst-example", log_sink=self.logs.append)
        self.app.sse_poll = 0.2
        server.start(self.server)
        self.port = self.app.port
        self.cookie: str | None = None
        ctx._stores.append(self)

    def close(self) -> None:
        server.stop(self.server)

    def connect(self) -> socket.socket:
        return loopback_socket(self.port)

    def request(self, method: str, path: str, body: bytes | None = None, headers: dict | None = None) -> Resp:
        conn = loopback_http(self.port)
        h = {"Host": f"127.0.0.1:{self.port}"}
        if body is not None:
            h["Content-Type"] = "application/json"
        h.update(headers or {})
        conn.request(method, path, body=body, headers=h)
        r = conn.getresponse()
        data = r.read()
        conn.close()
        return Resp(r.status, r.getheaders(), data)

    def get(self, path: str, headers: dict | None = None) -> Resp:
        return self.request("GET", path, headers=headers)

    def login(self) -> str:
        r = self.get("/")
        self.cookie = r.header("Set-Cookie").split(";", 1)[0]
        return self.cookie

    def send(self, method: str, path: str, payload, cookie: bool = True) -> Resp:
        import json

        headers = {"Cookie": self.cookie} if cookie and self.cookie else {}
        return self.request(method, path, json.dumps(payload).encode("utf-8"), headers)

    def stream(self, path: str, headers: dict | None = None, seconds: float = 2.0) -> tuple[bytes, list[str]]:
        """(response head, the event-stream frames read within `seconds`)."""
        return stream_read(self, path, headers, seconds)


def stream_open(client: Client, path: str, headers: dict | None = None) -> tuple[socket.socket, bytes, bytes]:
    sock = client.connect()
    lines = [f"GET {path} HTTP/1.0", f"Host: 127.0.0.1:{client.port}"]
    for k, v in (headers or {}).items():
        lines.append(f"{k}: {v}")
    sock.sendall(("\r\n".join(lines) + "\r\n\r\n").encode("ascii"))
    buf = b""
    while b"\r\n\r\n" not in buf:
        chunk = sock.recv(4096)
        if not chunk:
            break
        buf += chunk
    head, _, rest = buf.partition(b"\r\n\r\n")
    return sock, head, rest


def stream_collect(sock: socket.socket, rest: bytes, seconds: float) -> list[str]:
    import time

    sock.settimeout(0.1)
    data = rest
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        try:
            chunk = sock.recv(4096)
        except (TimeoutError, socket.timeout):
            continue
        if not chunk:
            break
        data += chunk
    sock.close()
    frames = [f for f in data.decode("utf-8", "replace").split("\n\n") if f.strip()]
    return [f for f in frames if not f.startswith(":")]


def stream_read(client: Client, path: str, headers: dict | None, seconds: float) -> tuple[bytes, list[str]]:
    sock, head, rest = stream_open(client, path, headers)
    return head, stream_collect(sock, rest, seconds)
