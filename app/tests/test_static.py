"""The static front end: the keymap is a subset of design 8.6 plus the amendment
keys, and app/static touches no browser storage, no canvas and no external host."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from app import config

STATIC = config.REPO_ROOT / "app" / "static"
DESIGN = config.REPO_ROOT / "docs" / "PLAINSIGHT-design.md"

#: The keys amendment 9.10 adds, and nothing else.
AMENDMENT_KEYS = {"7", "8", "+", "-", "t"}

#: Browser storage (EG-3), canvas and WebGL (section 8.5), and any absolute URL,
#: which would be a request to a host other than the server's own origin.
FORBIDDEN = re.compile(
    r"localStorage|sessionStorage|indexedDB|serviceWorker|\bcaches\s*\.|document\.cookie|"
    r"getContext|<canvas|webgl|https?://|@import|\burl\(\s*['\"]?(?!#)",
    re.IGNORECASE,
)


def keymap() -> dict:
    return json.loads((STATIC / "keymap.json").read_text(encoding="utf-8"))


def design_86_block() -> str:
    text = DESIGN.read_text(encoding="utf-8")
    section = text.split("## 8.6", 1)[1]
    return section.split("```", 2)[1]


def check_keymap_is_a_subset_of_8_6(ctx):
    keys = keymap()["keys"]
    block = design_86_block()
    names = [k["key"] for k in keys]
    assert len(names) == len(set(names)), "two bindings share a key"
    assert "d" not in names, "8.6 has no d"
    added = set()
    for k in keys:
        if k["origin"] == "8.6":
            assert k["design"] and k["design"] in block, f"{k['key']} is not a key of design 8.6"
        else:
            assert k["origin"] == "9.10" and k["design"] is None
            added.add(k["key"])
    assert added == AMENDMENT_KEYS, "the additions are not exactly 7, 8, + and -, and t"
    enter = next(k for k in keys if k["key"] == "Enter")
    assert enter["action"] == "promote", "Enter was rebound"


def break_keymap_gains_d(ctx):
    real = keymap()
    real["keys"].append({"key": "d", "design": "d dismiss", "origin": "8.6", "slice": 1, "built": True,
                         "action": "dismiss", "label": "dismiss"})
    ctx.mp.setattr(sys.modules[__name__], "keymap", lambda: real)


def test_keymap_is_a_subset_of_8_6(ctx):
    check_keymap_is_a_subset_of_8_6(ctx)


def forbidden_in(roots) -> list[str]:
    found = []
    for root in roots:
        for path in sorted(Path(root).rglob("*")):
            if path.is_file() and FORBIDDEN.search(path.read_text(encoding="utf-8")):
                found.append(path.name)
    return found


def check_static_uses_no_storage_canvas_or_host(ctx):
    assert forbidden_in([STATIC] + ctx.extra_roots) == []
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    assert "<script>" not in html and "style=" not in html, "inline script or style would need a CSP exception"


def break_planted_storage_call(ctx):
    root = ctx.tmp / "planted-static"
    root.mkdir()
    (root / "cache.js").write_text("window.localStorage.setItem('focus', '1');\n", encoding="utf-8")
    ctx.extra_roots.append(root)


def test_static_uses_no_storage_canvas_or_host(ctx):
    check_static_uses_no_storage_canvas_or_host(ctx)


def app_js() -> str:
    return (STATIC / "app.js").read_text(encoding="utf-8")


def check_focused_controls_keep_tab_and_enter(ctx):
    js = app_js()
    on_key = js.split("function onKey(e) {", 1)[1].split("\n}\n", 1)[0]
    assert "if (controlKeeps(e.target, name)) return;" in on_key, "onKey captures Tab and Enter on a focused control"
    keeps = js.split("export function controlKeeps(target, name) {", 1)[1].split("\n}\n", 1)[0]
    assert "HTMLButtonElement" in keeps and "HTMLAnchorElement" in keeps
    assert 'const CONTROL_KEYS = ["Tab", "Shift+Tab", "Enter", " "];' in js


def break_on_key_captures_everything(ctx):
    real = app_js()
    ctx.mp.setattr(sys.modules[__name__], "app_js", lambda: real.replace("  if (controlKeeps(e.target, name)) return;\n", ""))


def test_focused_controls_keep_tab_and_enter(ctx):
    check_focused_controls_keep_tab_and_enter(ctx)


#: A move names a key as "with <key>". Only keys the keymap lists are checked.
MOVE_KEY = re.compile(r"\bwith (\S+?)(?=,|$|\s)")


def check_refusal_moves_name_built_keys(ctx):
    from app import refusals
    from app.http import acts

    built = {k["key"]: k["built"] for k in keymap()["keys"]}
    texts = [m for c in refusals.REFUSALS.values() for m in c.moves]
    texts.append(acts.not_dispatched_text("LOCAL", gate_present=False))
    texts.append(acts.not_dispatched_text("LOCAL", gate_present=True))
    named = []
    for text in texts:
        for key in MOVE_KEY.findall(text):
            if key in built:
                named.append(key)
                assert built[key], f"a refusal names the key {key}, which this slice does not build"
    assert {"l", "v", "8", "t", "-"} <= set(named), named


def break_deep_dive_moves_name_unbuilt_keys(ctx):
    from app import refusals

    old = refusals.REFUSALS["DEEP_DIVE_NOT_DISPATCHED"]
    ctx.mp.setitem(refusals.REFUSALS, "DEEP_DIVE_NOT_DISPATCHED", refusals.Code(
        old.code, old.what, old.rule,
        ("note the node with n", "raise an open question with ?", "record why it matters for when the gate ships"),
    ))


def test_refusal_moves_name_built_keys(ctx):
    check_refusal_moves_name_built_keys(ctx)


CONTROLS = [
    ("the keymap gains a d", check_keymap_is_a_subset_of_8_6, break_keymap_gains_d),
    ("a planted storage call", check_static_uses_no_storage_canvas_or_host, break_planted_storage_call),
    ("onKey captures every key", check_focused_controls_keep_tab_and_enter, break_on_key_captures_everything),
    ("the deep-dive moves name unbuilt keys", check_refusal_moves_name_built_keys, break_deep_dive_moves_name_unbuilt_keys),
]
