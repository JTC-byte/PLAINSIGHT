"""The showcase front end: `python -m app serve --ui showcase` serves app/showcase
over the same routes and API as the classic front end, which stays the default.

Seven properties, each with a control in CONTROLS:

- app/showcase obeys the rules app/static obeys: no browser storage (EG-3), no
  canvas or WebGL (design 8.5), no absolute URL, no @import and no url() but a
  fragment, and no inline script or style in its page, which the server's CSP
  would refuse;
- the showcase sends no write: no fetch carries a method, and nothing uses
  XMLHttpRequest, sendBeacon or a form, so every request it makes is a GET;
- `--ui showcase` serves the showcase's page and files, the default serves the
  classic ones, the API answers both, and an unknown front end is refused
  before a socket exists;
- the showcase's request layer, app/showcase/lib/api.js, run under node with a
  fetch that drops one request, still answers that request, and never has more
  than six requests open at once. This check runs JavaScript, so it needs node
  on PATH and is skipped without it; CI's runner has node;
- the first-load guard is wired: the page loads app/showcase/boot.js, a classic
  script, before the module, and app.js tells it that it started. This half is
  read from the files and not run, because it needs a browser;
- the display overlay's reader, app/http/overlay.py, admits fictional stand-ins
  only, and refuses a file inside the store or any git working tree;
- a case pack never reaches or names the store: under node, with a case pack
  set, no request reaches the server, the top bar's label is not a switch to
  stored values, and no statement of the page's source says the page reads the
  store. That app.js prints those statements from lib/words.js is read from
  the file and not run.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from app import config
from app.http import routes, server
from app.tests import test_static
from app.tests.served import Client, corpus_copy

SHOWCASE = config.REPO_ROOT / "app" / "showcase"

#: A request that could write: a fetch given a method, the two other request
#: APIs, and a form, written as markup or built by the showcase's element
#: helper, which a browser submits without script.
WRITE_REQUEST = re.compile(r"""\bmethod\s*:|XMLHttpRequest|sendBeacon|<form\b|\bh\(\s*["']form["']""", re.IGNORECASE)


def showcase_files(roots) -> list[Path]:
    out = []
    for root in roots:
        out.extend(p for p in sorted(Path(root).rglob("*")) if p.is_file())
    return out


def check_showcase_uses_no_storage_canvas_or_host(ctx):
    assert test_static.forbidden_in([SHOWCASE] + ctx.extra_roots) == []
    html = (SHOWCASE / "index.html").read_text(encoding="utf-8")
    assert "<script>" not in html and "style=" not in html, "inline script or style would need a CSP exception"
    assert "<title>PLAINSIGHT</title>" in html, "the index route writes the case title into this exact element"


def break_planted_storage_in_showcase(ctx):
    root = ctx.tmp / "planted-showcase"
    root.mkdir()
    (root / "cache.js").write_text("window.sessionStorage.setItem('tab', 'overview');\n", encoding="utf-8")
    ctx.extra_roots.append(root)


def test_showcase_uses_no_storage_canvas_or_host(ctx):
    check_showcase_uses_no_storage_canvas_or_host(ctx)


def check_showcase_sends_get_only(ctx):
    writes = [p.name for p in showcase_files([SHOWCASE] + ctx.extra_roots)
              if p.suffix in (".js", ".html") and WRITE_REQUEST.search(p.read_text(encoding="utf-8"))]
    assert writes == [], f"a showcase file can send a request other than GET: {writes}"


def break_planted_post(ctx):
    root = ctx.tmp / "planted-post"
    root.mkdir()
    (root / "act.js").write_text("fetch('/api/cases/x/acts', { method: 'POST', body: '{}' });\n", encoding="utf-8")
    ctx.extra_roots.append(root)


def break_planted_form(ctx):
    root = ctx.tmp / "planted-form"
    root.mkdir()
    (root / "act.js").write_text('h("form", { action: "/api/cases/x/acts" });\n', encoding="utf-8")
    ctx.extra_roots.append(root)


def test_showcase_sends_get_only(ctx):
    check_showcase_sends_get_only(ctx)


class UiClient(Client):
    """A live server for one front end, closed by ctx.close()."""

    def __init__(self, ctx, ui: str):
        self.root = corpus_copy(ctx, f"served-{ui}")
        self.logs: list[tuple] = []
        self.server, self.app = server.make_server(self.root, analyst="analyst-example", log_sink=self.logs.append, ui=ui)
        self.app.sse_poll = 0.2
        server.start(self.server)
        self.port = self.app.port
        self.cookie = None
        ctx._stores.append(self)


def check_serve_ui_selects_the_front_end(ctx):
    show = UiClient(ctx, "showcase")
    page = show.get("/")
    assert page.status == 200 and b'id="statusbar"' in page.body, "--ui showcase does not serve the showcase page"
    assert show.get("/static/app.js").body == (SHOWCASE / "app.js").read_bytes()
    assert show.get("/static/views/connections.js").status == 200
    assert show.get("/keymap.json").status == 404, "a front end with no keymap answers a refusal, not a fault"
    assert show.get("/api/cases").status == 200
    classic = Client(ctx)
    page = classic.get("/")
    assert page.status == 200 and b'id="roster"' in page.body, "the default front end is no longer the classic one"
    assert classic.get("/static/app.js").body == (config.REPO_ROOT / "app" / "static" / "app.js").read_bytes()
    try:
        srv, app = server.make_server(corpus_copy(ctx, "unknown-ui"), analyst="analyst-example", ui="elsewhere")
    except ValueError:
        pass
    else:
        app.close()
        srv.server_close()
        raise AssertionError("an unknown front end was served")


def break_showcase_root_points_at_classic(ctx):
    ctx.mp.setitem(routes.UIS, "showcase", routes.STATIC)


def break_keymap_faults_without_a_keymap(ctx):
    def faulting(app, params, query, body):
        content_type, data = app.static["keymap.json"]
        return routes.Response(200, content_type, data, {})

    ctx.mp.setitem(routes.HANDLERS, "keymap", faulting)


def break_default_is_the_showcase(ctx):
    ctx.mp.setitem(routes.UIS, "classic", routes.SHOWCASE)


def break_unknown_ui_served(ctx):
    ctx.mp.setitem(routes.UIS, "elsewhere", routes.STATIC)


def test_serve_ui_selects_the_front_end(ctx):
    check_serve_ui_selects_the_front_end(ctx)


#: The harness node runs: the real api.js copied beside it as an .mjs module, a
#: fetch that rejects the first request to /drop as a network failure would, and
#: thirty requests at once while it counts how many are open.
HARNESS = """
import { getJSON, LOAD } from "./api.mjs";
LOAD.pauseMs = [1, 1];
let open = 0, peak = 0, calls = 0;
const drop = new Set(["/drop"]);
globalThis.fetch = async (url) => {
  calls += 1; open += 1; peak = Math.max(peak, open);
  await new Promise((r) => setTimeout(r, 5));
  open -= 1;
  if (drop.has(url)) { drop.delete(url); throw new TypeError("Failed to fetch"); }
  return { ok: true, status: 200, text: async () => JSON.stringify({ url }) };
};
const one = await getJSON("/drop");
const many = await Promise.all(Array.from({ length: 30 }, (_, i) => getJSON(`/n/${i}`)));
console.log(JSON.stringify({ dropped: !!one.dropped, ok: one.ok, body: one.body, calls, peak, all: many.every((r) => r.ok) }));
"""


def api_source() -> str:
    return (SHOWCASE / "lib" / "api.js").read_text(encoding="utf-8")


def run_node(ctx, folder: str, files: dict, what: str) -> dict:
    """Run harness.mjs under node in a scratch folder holding `files`, and return the JSON it prints last.
    Every harness in this module runs through this one call, so the module holds one process site."""
    node = shutil.which("node")
    if node is None:
        pytest.skip(f"node is not on PATH, so {what} cannot be run here")
    work = ctx.tmp / folder
    work.mkdir(exist_ok=True)
    for name, text in files.items():
        (work / name).write_text(text, encoding="utf-8")
    proc = subprocess.run([node, str(work / "harness.mjs")], capture_output=True, text=True, encoding="utf-8", timeout=60, cwd=work)
    assert proc.returncode == 0, f"the harness did not run: {proc.stderr[-400:]}"
    return json.loads(proc.stdout.strip().splitlines()[-1])


def run_api_harness(ctx) -> dict:
    return run_node(ctx, "api-harness", {"api.mjs": api_source(), "harness.mjs": HARNESS}, "the request layer's JavaScript")


def check_a_dropped_request_is_retried_and_requests_are_gated(ctx):
    got = run_api_harness(ctx)
    assert got["ok"] and not got["dropped"] and got["body"] == {"url": "/drop"}, "a request dropped once was not answered on a retry"
    assert got["all"], "a request in a burst of thirty was not answered"
    assert got["calls"] == 32, f"expected 32 fetches (one drop, its retry, thirty more), saw {got['calls']}"
    assert 1 <= got["peak"] <= 6, f"{got['peak']} requests were open at once; the gate allows at most six"


def break_no_retry(ctx):
    real = api_source()
    assert "retries: 2" in real
    ctx.mp.setattr(sys.modules[__name__], "api_source", lambda: real.replace("retries: 2", "retries: 0"))


def break_no_gate(ctx):
    real = api_source()
    assert "inFlight: 4" in real
    ctx.mp.setattr(sys.modules[__name__], "api_source", lambda: real.replace("inFlight: 4", "inFlight: 100"))


def test_a_dropped_request_is_retried_and_requests_are_gated(ctx):
    check_a_dropped_request_is_retried_and_requests_are_gated(ctx)


def page_files() -> dict[str, str]:
    return {name: (SHOWCASE / name).read_text(encoding="utf-8") for name in ("index.html", "boot.js", "app.js")}


def check_first_load_guard_is_wired(ctx):
    f = page_files()
    html = f["index.html"]
    guard = html.find('<script src="/static/boot.js" defer></script>')
    module = html.find('<script type="module" src="/static/app.js" id="app-module"></script>')
    assert guard != -1 and module != -1 and guard < module, "the page does not load the classic guard before the module"
    assert 'window.dispatchEvent(new Event("plainsight:started"))' in f["app.js"], "app.js never tells the guard it started"
    boot = f["boot.js"]
    assert '"plainsight:started"' in boot and 'getElementById("app-module")' in boot
    assert 'navigationType() !== "reload"' in boot and "location.reload()" in boot, "the guard does not reload exactly once"


def break_guard_not_loaded(ctx):
    real = page_files()
    real["index.html"] = real["index.html"].replace('<script src="/static/boot.js" defer></script>\n', "")
    ctx.mp.setattr(sys.modules[__name__], "page_files", lambda: real)


def break_never_says_started(ctx):
    real = page_files()
    real["app.js"] = real["app.js"].replace('window.dispatchEvent(new Event("plainsight:started"));', "")
    ctx.mp.setattr(sys.modules[__name__], "page_files", lambda: real)


def test_first_load_guard_is_wired(ctx):
    check_first_load_guard_is_wired(ctx)


def overlay_module():
    from app.http import overlay

    return overlay


def check_overlay_is_fictional_by_construction(ctx):
    """The display overlay's reader admits fictional stand-ins for placeholders only. No email- or
    number-shaped literal sits in this file: each is built at run time, so the repository scan reads none."""
    ov = overlay_module()
    store = ctx.tmp / "store"
    store.mkdir(exist_ok=True)
    fake_repo = ctx.tmp / "repo"
    fake_repo.mkdir(exist_ok=True)
    ctx.mp.setattr(config, "REPO_ROOT", fake_repo)

    def written(name, data, where=None):
        p = (where or ctx.tmp) / name
        p.write_text(json.dumps(data), encoding="utf-8")
        return p

    reserved = "a.person" + "@" + "example.com"

    def pack(text):
        return {"case": {"responses": {"/api/cases": {"t": text}}}, "values": {"<synthetic-handle-1>": "someone"}}

    clean = "rode with @someone on 2025-07-05T17:40:00Z, record 77c83c13-2bce-5db3-8356-4785b2403fe7, tool@0.1.0, mail " + reserved + ", call +1 253 " + "555-01" + "47"
    admitted = json.loads(ov.read_overlay(written("case.json", dict(pack(clean), presentation="live")), store))
    assert admitted["case"]["responses"]["/api/cases"]["t"] == clean, "the overlay reader refused or changed a clean case pack"
    good = written("good.json", {"presentation": "live", "subject": {"name": "A Person"},
                                 "values": {"<synthetic-handle-1>": "someone", "<synthetic-permutation>": reserved}})
    got = json.loads(ov.read_overlay(good, store))
    assert got["values"]["<synthetic-permutation>"] == reserved and got["subject"]["name"] == "A Person"
    assert got["presentation"] == "live"
    refused = {
        "an email on a domain that is not reserved": {"values": {"<synthetic-handle-1>": "someone" + "@" + "site.test"}},
        "a number outside 555-0100 to 555-0199": {"values": {"<synthetic-handle-1>": "0" * 10}},
        "a key that is not a corpus placeholder": {"values": {"handle": "someone"}},
        "a handle that is the subject's plain first and last name": {"subject": {"name": "A Person"}, "values": {"<synthetic-handle-1>": "a" + "." + "person"}},
        "a presentation other than marked or live": {"presentation": "loud", "values": {"<synthetic-handle-1>": "someone"}},
        "a case pack naming an email domain that is not reserved": pack("write to someone" + "@" + "site" + ".test today"),
        "a case pack holding a phone number outside 555-0100 to 555-0199": pack("call (" + "253) " + "867-" + "0" * 4),
        "a case pack holding a number led by a plus sign outside that range": pack("ring +" + "44 20 " + "79" + "46 " + "0" * 4),
        "a case pack holding a bare run of ten digits outside that range": pack("ring " + "0" * 10 + " after six"),
        "a case pack holding a link": pack("see https" + "://" + "site.test"),
        "a case pack holding a coordinate key": {"case": {"responses": {"/api/cases": {"lat": 1.5}}}, "values": {"<synthetic-handle-1>": "someone"}},
        "a case pack answering a request that is not a case request": {"case": {"responses": {"/static/app.js": {}}}, "values": {"<synthetic-handle-1>": "someone"}},
    }
    for why, data in refused.items():
        try:
            ov.read_overlay(written("bad.json", data), store)
        except ValueError:
            continue
        raise AssertionError(f"the overlay reader accepted {why}")
    try:
        ov.read_overlay(written("inside.json", {"values": {"<synthetic-handle-1>": "someone"}}, fake_repo), store)
    except ValueError:
        pass
    else:
        raise AssertionError("the overlay reader read a file inside the repository")
    elsewhere = ctx.tmp / "another-working-tree"
    (elsewhere / ".git").mkdir(parents=True)
    (elsewhere / "deep").mkdir()
    try:
        ov.read_overlay(written("inside.json", {"values": {"<synthetic-handle-1>": "someone"}}, elsewhere / "deep"), store)
    except ValueError:
        pass
    else:
        raise AssertionError("the overlay reader read a file inside another git working tree")
    try:
        ov.read_overlay(written("inside.json", {"values": {"<synthetic-handle-1>": "someone"}}, store), store)
    except ValueError:
        pass
    else:
        raise AssertionError("the overlay reader read a file inside the store root")


def break_overlay_any_domain(ctx):
    ctx.mp.setattr(overlay_module(), "RESERVED", ("example.com", "site.test"))


def break_overlay_any_key(ctx):
    ctx.mp.setattr(overlay_module(), "PLACEHOLDER", re.compile(r".+"))


def break_overlay_plain_name_handle(ctx):
    ctx.mp.setattr(overlay_module(), "_plain_name", lambda handle, name: False)


def break_overlay_any_presentation(ctx):
    ctx.mp.setattr(overlay_module(), "PRESENTATIONS", ("marked", "live", "loud"))


def break_overlay_case_any_email(ctx):
    ctx.mp.setattr(overlay_module(), "CASE_EMAIL", re.compile(r"(?!x)x"))


def break_overlay_case_any_phone(ctx):
    ctx.mp.setattr(overlay_module(), "PHONE_SHAPE", re.compile(r"(?!x)x"))


def break_overlay_case_any_plus_number(ctx):
    ctx.mp.setattr(overlay_module(), "PLUS_RUN", re.compile(r"(?!x)x"))


def break_overlay_case_any_bare_number(ctx):
    ctx.mp.setattr(overlay_module(), "BARE_RUN", re.compile(r"(?!x)x"))


def break_overlay_inside_another_working_tree(ctx):
    def this_repository_only(path):
        repo = config.REPO_ROOT.resolve()
        return path == repo or repo in path.parents

    ctx.mp.setattr(overlay_module().db, "in_git_working_tree", this_repository_only)


def break_overlay_case_links(ctx):
    ctx.mp.setattr(overlay_module(), "LINK", re.compile(r"(?!x)x"))


def break_overlay_case_coordinates(ctx):
    ctx.mp.setattr(overlay_module(), "GEO_KEYS", set())


def break_overlay_case_any_request(ctx):
    ctx.mp.setattr(overlay_module(), "CASE_KEY_PREFIX", "/")


def break_overlay_inside_repo(ctx):
    ctx.mp.setattr(overlay_module().db, "in_git_working_tree", lambda path: False)


def break_overlay_inside_the_store(ctx):
    ctx.mp.setattr(overlay_module(), "_inside", lambda path, root: False)


def test_overlay_is_fictional_by_construction(ctx):
    check_overlay_is_fictional_by_construction(ctx)


#: The harness for a case pack: the real api.js and words.js, a fetch that counts what reaches the server,
#: and the page's statements of its source read in four states: an overlay of values, the same in the live
#: look, a case pack, and a case pack in the live look.
PACK_HARNESS = """
import { getJSON, setCasePack, setLiveLook } from "./api.mjs";
import { fictionLabel, sourceWords } from "./words.mjs";
let calls = 0;
globalThis.fetch = async () => { calls += 1; return { ok: true, status: 200, text: async () => "{}" }; };
const ov = { values: { "<synthetic-handle-1>": "someone" } };
const look = () => ({ on: fictionLabel(ov, true), off: fictionLabel(ov, false), words: sourceWords(ov, true) });
const out = { plain: look() };
setLiveLook(true);
out.plainLive = look();
setLiveLook(false);
setCasePack({ responses: { "/api/cases": { cases: [] } } });
const held = await getJSON("/api/cases");
const missing = await getJSON("/api/cases/0/header");
out.packed = Object.assign(look(), { held: held.ok, missing: missing.status, calls });
setLiveLook(true);
out.packedLive = look();
console.log(JSON.stringify(out));
"""


def words_source() -> str:
    return (SHOWCASE / "lib" / "words.js").read_text(encoding="utf-8")


def run_pack_harness(ctx) -> dict:
    words = words_source()
    assert 'from "./api.js"' in words, "words.js no longer reads the case pack's state from api.js"
    files = {"api.mjs": api_source(), "words.mjs": words.replace('from "./api.js"', 'from "./api.mjs"'), "harness.mjs": PACK_HARNESS}
    return run_node(ctx, "pack-harness", files, "the page's statements about a case pack")


def check_a_case_pack_never_reaches_or_names_the_store(ctx):
    """A case pack answers every /api/ request in the page. While one is set no request reaches the server,
    the top bar's label is not a switch to stored values, and no statement of the page's source says the
    page reads the store. app.js prints those statements from words.js and holds none of its own."""
    got = run_pack_harness(ctx)
    plain, packed, packed_live = got["plain"], got["packed"], got["packedLive"]
    assert plain["on"]["switches"] and plain["off"]["switches"] and plain["off"]["head"] == "STORED VALUES", \
        "without a case pack, the overlay's label no longer switches to the stored values"
    assert "reads the store" in plain["words"]["line"] and "reads the store" in got["plainLive"]["words"]["line"], \
        "without a case pack, the page no longer says it reads the store"
    assert packed["held"] and packed["missing"] == 404 and packed["calls"] == 0, \
        f"with a case pack set, {packed['calls']} request(s) reached the server"
    assert packed["on"] == packed["off"] and packed["on"]["switches"] is False, \
        "with a case pack set, the top bar's label is a switch, and nothing stored stands behind a case pack"
    said = json.dumps([packed["on"], packed["words"], packed_live["words"]]).lower()
    for phrase in ("stored values", "reads the store", "placeholder", "corpus"):
        assert phrase not in said, f"with a case pack set, the page says {phrase!r}, and a case pack is not read from the store"
    assert packed_live["on"] is None and packed_live["words"]["note"] is None, "the live look labelled the case"
    app_js = page_files()["app.js"]
    for phrase in ("STORED VALUES", "reads the store"):
        assert phrase not in app_js, f"app.js states {phrase!r} itself; the statement belongs to words.js, which reads the case pack"


def break_pack_label_is_a_switch(ctx):
    real = words_source()
    assert real.count("switches: false") == 1
    ctx.mp.setattr(sys.modules[__name__], "words_source", lambda: real.replace("switches: false", "switches: true"))


def break_pack_words_ignore_the_pack(ctx):
    real = words_source()
    assert real.count("const packed = hasCasePack();") == 1
    ctx.mp.setattr(sys.modules[__name__], "words_source", lambda: real.replace("const packed = hasCasePack();", "const packed = false;"))


def break_pack_requests_reach_the_server(ctx):
    real = api_source()
    answered = 'if (pack && String(url).startsWith("/api/")) return fromPack(url);'
    assert real.count(answered) == 1
    ctx.mp.setattr(sys.modules[__name__], "api_source", lambda: real.replace(answered, ""))


def break_app_states_its_source_itself(ctx):
    real = page_files()
    planted = dict(real, **{"app.js": real["app.js"] + '\nsay("The page reads the store.");\n'})
    ctx.mp.setattr(sys.modules[__name__], "page_files", lambda: planted)


def test_a_case_pack_never_reaches_or_names_the_store(ctx):
    check_a_case_pack_never_reaches_or_names_the_store(ctx)


CONTROLS = [
    ("a planted storage call in the showcase", check_showcase_uses_no_storage_canvas_or_host, break_planted_storage_in_showcase),
    ("a planted POST in the showcase", check_showcase_sends_get_only, break_planted_post),
    ("a planted form built by the element helper", check_showcase_sends_get_only, break_planted_form),
    ("the showcase root points at the classic one", check_serve_ui_selects_the_front_end, break_showcase_root_points_at_classic),
    ("the keymap route faults when a front end has none", check_serve_ui_selects_the_front_end, break_keymap_faults_without_a_keymap),
    ("the default front end is the showcase", check_serve_ui_selects_the_front_end, break_default_is_the_showcase),
    ("an unknown front end is served", check_serve_ui_selects_the_front_end, break_unknown_ui_served),
    ("the request layer does not retry", check_a_dropped_request_is_retried_and_requests_are_gated, break_no_retry),
    ("the request gate is opened wide", check_a_dropped_request_is_retried_and_requests_are_gated, break_no_gate),
    ("the page does not load the guard", check_first_load_guard_is_wired, break_guard_not_loaded),
    ("app.js never says it started", check_first_load_guard_is_wired, break_never_says_started),
    ("the overlay admits any email domain", check_overlay_is_fictional_by_construction, break_overlay_any_domain),
    ("the overlay replaces any key", check_overlay_is_fictional_by_construction, break_overlay_any_key),
    ("the overlay reads inside the repository", check_overlay_is_fictional_by_construction, break_overlay_inside_repo),
    ("the overlay admits the subject's plain name as a handle", check_overlay_is_fictional_by_construction, break_overlay_plain_name_handle),
    ("the overlay admits any presentation", check_overlay_is_fictional_by_construction, break_overlay_any_presentation),
    ("a case pack admits any email domain", check_overlay_is_fictional_by_construction, break_overlay_case_any_email),
    ("a case pack admits any phone number", check_overlay_is_fictional_by_construction, break_overlay_case_any_phone),
    ("a case pack admits a number led by a plus sign", check_overlay_is_fictional_by_construction, break_overlay_case_any_plus_number),
    ("a case pack admits a bare run of digits", check_overlay_is_fictional_by_construction, break_overlay_case_any_bare_number),
    ("the overlay reads inside another git working tree", check_overlay_is_fictional_by_construction, break_overlay_inside_another_working_tree),
    ("the overlay reads inside the store root", check_overlay_is_fictional_by_construction, break_overlay_inside_the_store),
    ("a case pack admits a link", check_overlay_is_fictional_by_construction, break_overlay_case_links),
    ("a case pack admits a coordinate key", check_overlay_is_fictional_by_construction, break_overlay_case_coordinates),
    ("a case pack answers any request", check_overlay_is_fictional_by_construction, break_overlay_case_any_request),
    ("a case pack's label is a switch to stored values", check_a_case_pack_never_reaches_or_names_the_store, break_pack_label_is_a_switch),
    ("the page's statements of its source ignore a case pack", check_a_case_pack_never_reaches_or_names_the_store, break_pack_words_ignore_the_pack),
    ("a request reaches the server while a case pack is set", check_a_case_pack_never_reaches_or_names_the_store, break_pack_requests_reach_the_server),
    ("app.js states the page's source itself", check_a_case_pack_never_reaches_or_names_the_store, break_app_states_its_source_itself),
]
