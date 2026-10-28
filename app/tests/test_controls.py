"""The negative-control meta-test.

A check is green only when its negative control has been seen to fail. Each
test module lists (control name, check, breaker) in CONTROLS. This module
applies every breaker in a fresh tmp_path and monkeypatch, runs the paired
check, and fails if the check stays green, because a check that passes with its
mechanism removed proves nothing (CLAUDE.md design gate 1).

It also fails when a module defines a check_ function that no control pairs
with, so a new claim cannot land without its control.
"""

from __future__ import annotations

import inspect

import pytest

from app.tests import (
    test_boundaries,
    test_corpus,
    test_door,
    test_http,
    test_kv,
    test_retention,
    test_rollup,
    test_spine,
    test_static,
    test_store,
)
from app.tests.helpers import Ctx

MODULES = (
    test_door,
    test_spine,
    test_retention,
    test_rollup,
    test_store,
    test_boundaries,
    test_kv,
    test_corpus,
    test_http,
    test_static,
)

ALL = [
    (m.__name__.rsplit(".", 1)[-1], name, check, breaker)
    for m in MODULES
    for (name, check, breaker) in m.CONTROLS
]


@pytest.mark.parametrize(
    "module,name,check,breaker",
    ALL,
    ids=[f"{m}: {n}" for m, n, _, _ in ALL],
)
def test_control_fails_its_check(module, name, check, breaker, tmp_path, monkeypatch):
    ctx = Ctx(tmp_path, monkeypatch)
    try:
        breaker(ctx)
        try:
            check(ctx)
        except AssertionError:
            return
        pytest.fail(f"{module}: the check stayed green under the control '{name}', so it is not load-bearing")
    finally:
        ctx.close()


def test_every_check_has_a_control():
    for m in MODULES:
        checks = {n for n, f in inspect.getmembers(m, inspect.isfunction) if n.startswith("check_") and f.__module__ == m.__name__}
        paired = {c.__name__ for _, c, _ in m.CONTROLS}
        assert checks <= paired, f"{m.__name__}: unpaired checks {sorted(checks - paired)}"
        plain = {n for n in dir(m) if n.startswith("test_")}
        for c in paired:
            assert f"test_{c[len('check_'):]}" in plain, f"{m.__name__}: {c} has no plain test"
