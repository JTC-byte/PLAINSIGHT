"""Fixtures, and the test client's two loopback connections.

Every store lives under tmp_path; the real store home is never touched.

The two connection helpers live in this file rather than in served.py because
tools/validate_authorization.py --dispatch-paths exempts a network call in a
test file, test_*.py or conftest.py under tests/, whose destination is the
literal 127.0.0.1, and reads a helper module beside the tests as needing an
allowlist entry. Each helper names 127.0.0.1 on the call itself, so the scan can
see that it reaches the test's own server and nothing else.
"""

from __future__ import annotations

import http.client
import socket

import pytest

from app import config
from app.store import db
from app.tests.helpers import Ctx

#: The connect and read timeout of the test client, in seconds.
CLIENT_TIMEOUT = 10


def loopback_socket(port: int) -> socket.socket:
    """A socket connected to the test server on 127.0.0.1 at `port`."""
    return socket.create_connection(("127.0.0.1", port), timeout=CLIENT_TIMEOUT)


def loopback_http(port: int) -> http.client.HTTPConnection:
    """An HTTP connection to the test server on 127.0.0.1 at `port`, connected on first request."""
    return http.client.HTTPConnection("127.0.0.1", port, timeout=CLIENT_TIMEOUT)


@pytest.fixture(autouse=True)
def _never_the_real_home(tmp_path, monkeypatch):
    real = db.default_root()
    existed = real.exists()
    monkeypatch.setenv(config.ENV_HOME, str(tmp_path / "home"))
    monkeypatch.delenv(config.ENV_ENVIRONMENT, raising=False)
    monkeypatch.delenv(config.ENV_HUMANS, raising=False)
    yield
    assert real.exists() == existed, "a test created the real store home"


@pytest.fixture
def ctx(tmp_path, monkeypatch):
    c = Ctx(tmp_path, monkeypatch)
    yield c
    c.close()
