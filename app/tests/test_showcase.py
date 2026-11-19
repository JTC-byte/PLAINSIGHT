"""The showcase front end: `python -m app serve --ui showcase` serves app/showcase
over the same routes and API as the classic front end, which stays the default.

Eleven properties, each with a control in CONTROLS:

- app/showcase obeys the rules app/static obeys: no browser storage (EG-3), no
  canvas or WebGL (design 8.5), no absolute URL, no @import and no url() but a
  fragment, and no inline script or style in its page, which the server's CSP
  would refuse;
- the showcase sends no write: no script or page names a method, and nothing
  uses XMLHttpRequest, sendBeacon or a form, so every request it makes is a GET;
- `--ui showcase` serves the showcase's page and files, the default serves the
  classic ones, the API answers both, and an unknown front end is refused
  before a socket exists;
- the showcase's request layer, app/showcase/lib/api.js, run under node with a
  fetch that drops one request, still answers that request, and never has more
  than six requests open at once. This check runs JavaScript, so it needs node
  on PATH. Without node it is skipped, unless PLAINSIGHT_REQUIRE_NODE=1, which
  CI sets and under which it fails;
- the first-load guard is wired: the page loads app/showcase/boot.js, a classic
  script, before the module, and app.js tells it that it started. This half is
  read from the files and not run, because it needs a browser;
- the display overlay's reader, app/http/overlay.py, admits fictional stand-ins
  only, and refuses a file inside the store or any git working tree;
- a case pack never reaches or names the store: under node, with a case pack
  set, no request reaches the server, the top bar's label is not a switch to
  stored values, and no statement of the page's source says the page reads the
  store. That app.js prints those statements from lib/words.js is read from
  the file and not run;
- the reading aids of amendment 9.29 hold: the key to the lines is drawn above
  the web, the Guide button shows the ? key that opens it, and the top bar keeps
  the case id on one line and the word SYNTHETIC on screen at a narrow width.
  These are read from the files and not run, because layout needs a browser;
- the evidence snapshot of amendment 9.31: the drawer draws it only when a
  lineage response carries one, above the decoded envelope, and the server
  sends none. Under node with a recording document, its text is drawn as text,
  a claim's span or field is marked, counted in UTF-16 code units, with the
  head claim's span drawn whole where spans overlap, a route is drawn from
  path_d alone in its own box, media is drawn only where its card draws it, an
  image box is capped in height, the provenance note is always drawn, the hash
  line under a case pack names no bytes, and an object outside the closed
  shape is refused in words. Through the overlay's swap, a span still marks
  the characters it marked before the stand-ins were drawn in;
- the Connections web of amendment 9.31 draws link labels only for the
  selection, opens a three-hop web of more than forty nodes at two hops with
  the reason said, keeps its honesty marks, shows a focused card's labels as
  hover does and puts them next in the tab order, and scrolls the seed into
  view when it first draws. The rules run under node, and the view's use of
  them is read from the files;
- the checks that run JavaScript fail rather than skip when node is absent and
  PLAINSIGHT_REQUIRE_NODE=1, and CI's workflow checks for node before the
  application tests and sets that variable on them. A local run without node
  still skips them.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from app import config
from app.http import routes, server
from app.tests import test_static
from app.tests.helpers import CASE, eid_of
from app.tests.served import Client, corpus_copy

SHOWCASE = config.REPO_ROOT / "app" / "showcase"

#: A request that could write: a fetch or a Request given a method, which the
#: word method alone stands for, so a key, a quoted key, a shorthand property
#: and an assignment are each read; the two other request APIs; and a form,
#: written as markup or built by the showcase's element helper, which a browser
#: submits without script. The classic front end's scan reads the word the same
#: way (app/tests/test_static.py).
WRITE_REQUEST = re.compile(r"""\bmethod\b|XMLHttpRequest|sendBeacon|<form\b|\bh\(\s*["']form["']""", re.IGNORECASE)


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


def break_planted_post_by_a_shorthand(ctx):
    """A POST whose method is a shorthand property, which names method with no colon after it."""
    root = ctx.tmp / "planted-shorthand"
    root.mkdir()
    (root / "act.js").write_text('const method = "POST";\nfetch("/api/cases/x/acts", { method, body: "{}" });\n',
                                 encoding="utf-8")
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


#: The environment variable under which a check that needs node fails, rather than skips, when node is absent.
#: CI's Application tests step sets it to 1 (.github/workflows/ci.yml).
REQUIRE_NODE = "PLAINSIGHT_REQUIRE_NODE"


def run_node(ctx, folder: str, files: dict, what: str) -> dict:
    """Run harness.mjs under node in a scratch folder holding `files`, and return the JSON it prints last.
    Every harness in this module runs through this one call, so the module holds one process site. Without
    node the check skips, or fails when PLAINSIGHT_REQUIRE_NODE is 1."""
    node = shutil.which("node")
    if node is None:
        if os.environ.get(REQUIRE_NODE) == "1":
            pytest.fail(f"node is not on PATH, so {what} cannot be run, and {REQUIRE_NODE}=1 refuses the skip")
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

    evidence_pack = {"case": {"responses": {"/api/cases": {"evidence": evidence_samples()["drawn"]["activity"]}}}, "values": {"<synthetic-handle-1>": "someone"}}
    got_evidence = json.loads(ov.read_overlay(written("evidence.json", evidence_pack), store))
    assert got_evidence["case"] == evidence_pack["case"], "the overlay reader refused or changed a case pack carrying an evidence snapshot"
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
        "a case pack whose evidence route holds a coordinate key": {"case": {"responses": {"/api/cases": {"evidence": {"media": {"path_d": "M 0 0", "lat": 1.5}}}}}, "values": {"<synthetic-handle-1>": "someone"}},
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


def reading_files() -> dict[str, str]:
    """The three files the reading aids of amendment 9.29 live in."""
    return {name: (SHOWCASE / name).read_text(encoding="utf-8") for name in ("app.js", "app.css", "views/connections.js")}


def media_block(css: str, query: str) -> str:
    """The body of the first @media block whose query is `query`, read to its closing brace."""
    start = css.find("@media (" + query + ") {")
    assert start != -1, f"app.css has no @media ({query}) block"
    depth, i = 0, css.index("{", start)
    for j in range(i, len(css)):
        depth += {"{": 1, "}": -1}.get(css[j], 0)
        if depth == 0:
            return css[i + 1:j]
    raise AssertionError(f"the @media ({query}) block never closes")


def check_lines_key_sits_above_the_web(ctx):
    src = reading_files()["views/connections.js"]
    assert 'class: "legend top"' in src, "the key to the lines is not marked as the one above the web"
    assert 'h("div", {}, legend, stage, caption)' in src, "the key to the lines is not drawn before the web"
    assert ".legend.top {" in reading_files()["app.css"], "the key above the web has no spacing rule"


def break_key_below_the_web(ctx):
    real = reading_files()
    real["views/connections.js"] = real["views/connections.js"].replace(
        'h("div", {}, legend, stage, caption)', 'h("div", {}, stage, caption, legend)')
    ctx.mp.setattr(sys.modules[__name__], "reading_files", lambda: real)


def test_lines_key_sits_above_the_web(ctx):
    check_lines_key_sits_above_the_web(ctx)


def check_guide_shows_its_key(ctx):
    src = reading_files()["app.js"]
    assert '"Guide", kbd("?"))' in src, "the Guide button does not show the key that opens it"
    assert 'kbd("?"), h("div", { class: "grow" }, "Open this guide")' in src, "the guide does not list its own key"
    assert 'if (e.key === "?") { showKeys(); return; }' in src, "the ? key no longer opens the guide it is shown on"


def break_guide_hides_its_key(ctx):
    real = reading_files()
    real["app.js"] = real["app.js"].replace('"Guide", kbd("?"))', '"Guide")')
    ctx.mp.setattr(sys.modules[__name__], "reading_files", lambda: real)


def break_question_key_unbound(ctx):
    real = reading_files()
    real["app.js"] = real["app.js"].replace('if (e.key === "?") { showKeys(); return; }', "")
    ctx.mp.setattr(sys.modules[__name__], "reading_files", lambda: real)


def test_guide_shows_its_key(ctx):
    check_guide_shows_its_key(ctx)


def check_top_bar_keeps_the_case_and_synthetic_whole(ctx):
    """The case id never breaks across two lines, the crumb is not squeezed under the search box, and a
    narrow screen drops the SYNTHETIC chip's trailing words while the word SYNTHETIC itself stays."""
    f = reading_files()
    css = f["app.css"]
    crumb = re.search(r"^\.crumb \{([^}]*)\}", css, re.MULTILINE)
    assert crumb and "flex-shrink: 0" in crumb.group(1), "the crumb shrinks, so the search box covers the SYNTHETIC chip"
    crumb_b = re.search(r"^\.crumb b \{([^}]*)\}", css, re.MULTILINE)
    assert crumb_b and "white-space: nowrap" in crumb_b.group(1), "the case id can break across two lines"
    narrow = media_block(css, "max-width: 1100px")
    assert ".crumb .pill-more { display: none; }" in narrow, "a narrow screen does not drop the chip's trailing words"
    hidden = [sel.strip() for sel, body in re.findall(r"([^{}]+)\{([^}]*)\}", narrow) if "display: none" in body]
    assert all(sel.endswith(".pill-more") for sel in hidden if ".pill" in sel), "a narrow screen hides the word SYNTHETIC"
    phone = media_block(css, "max-width: 720px")
    assert ".topbar .iconbtn .kbd { display: none; }" in phone and ".who { font-size: 0; gap: 0; }" in phone, "at a phone's width the top bar is wider than the screen and pushes the Guide button off it"
    search = re.search(r"^\.search \{([^}]*)\}", css, re.MULTILINE)
    assert search and "min-width: 0" in search.group(1), "the search box keeps its width, so the top bar overflows instead of giving way"
    assert 'h("b", {}, "SYNTHETIC"), h("span", { class: "pill-more" }, ' in f["app.js"], "the chip's trailing words are not their own span"


def break_case_id_wraps(ctx):
    real = reading_files()
    real["app.css"] = real["app.css"].replace("font-weight: 600; white-space: nowrap; flex-shrink: 0; }", "font-weight: 600; }", 1)
    ctx.mp.setattr(sys.modules[__name__], "reading_files", lambda: real)


def break_crumb_shrinks(ctx):
    real = reading_files()
    real["app.css"] = real["app.css"].replace("font-size: 14px; flex-shrink: 0; }", "font-size: 14px; min-width: 0; }", 1)
    ctx.mp.setattr(sys.modules[__name__], "reading_files", lambda: real)


def break_narrow_hides_synthetic(ctx):
    real = reading_files()
    real["app.css"] = real["app.css"].replace(".crumb .pill-more { display: none; }", ".crumb .pill-more { display: none; }\n  .topbar .pill { display: none; }", 1)
    ctx.mp.setattr(sys.modules[__name__], "reading_files", lambda: real)


def break_narrow_drops_the_trailing_words_no_more(ctx):
    real = reading_files()
    real["app.css"] = real["app.css"].replace(".crumb .pill-more { display: none; }", "", 1)
    ctx.mp.setattr(sys.modules[__name__], "reading_files", lambda: real)


def break_phone_top_bar_overflows(ctx):
    real = reading_files()
    real["app.css"] = real["app.css"].replace("  .topbar .iconbtn .kbd { display: none; }" + chr(10), "", 1)
    ctx.mp.setattr(sys.modules[__name__], "reading_files", lambda: real)


def break_search_keeps_its_width(ctx):
    real = reading_files()
    real["app.css"] = real["app.css"].replace(".search { min-width: 0; }\n", "", 1)
    ctx.mp.setattr(sys.modules[__name__], "reading_files", lambda: real)


def break_trailing_words_not_their_own_span(ctx):
    real = reading_files()
    real["app.js"] = real["app.js"].replace('h("span", { class: "pill-more" }, "corpus case', 'h("span", {}, "corpus case', 1)
    ctx.mp.setattr(sys.modules[__name__], "reading_files", lambda: real)


def break_key_above_has_no_rule(ctx):
    real = reading_files()
    real["app.css"] = real["app.css"].replace(".legend.top {", ".legend.upper {", 1)
    ctx.mp.setattr(sys.modules[__name__], "reading_files", lambda: real)


def break_guide_lists_no_own_key(ctx):
    real = reading_files()
    real["app.js"] = real["app.js"].replace('h("div", { class: "grow" }, "Open this guide")', 'h("div", { class: "grow" }, "Open the guide")', 1)
    ctx.mp.setattr(sys.modules[__name__], "reading_files", lambda: real)


def test_top_bar_keeps_the_case_and_synthetic_whole(ctx):
    check_top_bar_keeps_the_case_and_synthetic_whole(ctx)


#: The left column's first child in the back lineage, and the call an audit row's heading makes.
AUDIT_BLOCK = 'dir === "back" && (d.audit || []).length ? auditTrail(ctx, d.audit, d.event_id, (d.breaks || []).length > 0, d.flags || []) : null,'
AUDIT_REFOCUS = 'onclick: () => openLineage(ctx, a.event_id, a.label, "back")'


def lineage_view_source() -> str:
    return (SHOWCASE / "views" / "lineage.js").read_text(encoding="utf-8")


def showcase_css() -> str:
    return (SHOWCASE / "app.css").read_text(encoding="utf-8")


def check_drawer_renders_the_audit_trail(ctx):
    """The drawer draws the server's audit field as an AUDIT TRAIL block at the top of the back lineage's
    left column, above the chain list, each row's heading a button that re-centres the drawer on its event
    (amendment 9.30). Read from the files and not run, because it needs a browser."""
    js = lineage_view_source()
    assert '"AUDIT TRAIL"' in js, "the drawer names no AUDIT TRAIL block"
    left = js[js.index('const left = h("div", {},'):js.index("const right =")]
    assert AUDIT_BLOCK in left, "the back lineage's left column does not draw the audit trail"
    assert left.index(AUDIT_BLOCK) < left.index('h("div", { class: "tier" }, dir === "forward"') < left.index("chain);"), \
        "the audit trail is not at the top of the left column, above the chain list"
    trail = js[js.index("export function auditTrail("):js.index("/** The chain as a list")]
    assert 'h("button", { class: "audit-step", type: "button"' in trail and AUDIT_REFOCUS in trail, \
        "an audit row's heading is not a button that re-centres the drawer on its event"
    assert "(a.lines || []).map(" in trail, "an audit row does not print its lines"
    assert 'flags.length ? h("div", { class: "rows" }, flags.map(' in trail, "a flag on the chain is not shown in the audit trail"
    css = showcase_css()
    for rule in (".audit-trail li {", ".audit-step {"):
        assert rule in css, f"app.css has no rule {rule!r} for the audit trail"


def break_audit_block_not_drawn(ctx):
    real = lineage_view_source()
    assert real.count(AUDIT_BLOCK) == 1
    ctx.mp.setattr(sys.modules[__name__], "lineage_view_source", lambda: real.replace(AUDIT_BLOCK, ""))


def break_audit_heading_not_a_button(ctx):
    real = lineage_view_source()
    assert real.count(AUDIT_REFOCUS) == 1
    ctx.mp.setattr(sys.modules[__name__], "lineage_view_source", lambda: real.replace(AUDIT_REFOCUS, "onclick: () => null"))


def break_audit_hides_flags(ctx):
    real = lineage_view_source()
    old = 'flags.length ? h("div", { class: "rows" }, flags.map((f) => h("div", { class: "flag" }, f))) : null,'
    assert real.count(old) == 1
    ctx.mp.setattr(sys.modules[__name__], "lineage_view_source", lambda: real.replace(old, "null,"))


def break_audit_style_missing(ctx):
    real = showcase_css()
    assert real.count(".audit-step {") == 1
    ctx.mp.setattr(sys.modules[__name__], "showcase_css", lambda: real.replace(".audit-step {", ".audit-step-gone {"))


def test_drawer_renders_the_audit_trail(ctx):
    check_drawer_renders_the_audit_trail(ctx)


#: The call that draws the evidence tier in the back lineage's right column, above the decoded envelope.
EVIDENCE_CALL = "d.evidence ? evidenceTier(d.evidence, d.event_id) : null,"
ENVELOPE_TIER = 'h("div", { class: "tier" }, "DECODED ENVELOPE"),'
RAW_TIER = 'h("div", { class: "tier" }, "RAW"),'
SPAN_WORDS = "the claim was read from this span"
FIELD_WORDS = "the claim was read from this field"
#: The ways a script can parse a string as markup. The evidence tier uses none of them.
MARKUP_SINK = re.compile(r"innerHTML|outerHTML|insertAdjacentHTML|document\.write|DOMParser|createContextualFragment|srcdoc")
#: The keys a route must never carry, the overlay reader's own list.
COORDINATE_WORDS = {"lat", "lon", "lng", "latitude", "longitude", "coordinate", "coordinates", "geometry", "geo_point"}


def evidence_view_source() -> str:
    return (SHOWCASE / "views" / "evidence.js").read_text(encoding="utf-8")


def evidence_lib_source() -> str:
    return (SHOWCASE / "lib" / "evidence.js").read_text(encoding="utf-8")


def dom_source() -> str:
    return (SHOWCASE / "lib" / "dom.js").read_text(encoding="utf-8")


def check_drawer_draws_evidence_above_the_envelope(ctx):
    """The back lineage's right column draws the evidence tier only when the response carries `evidence`, above
    the decoded envelope, and keeps the RAW tier below both (amendment 9.31). Read from the files and not run,
    because the drawer needs a browser; the tier itself is run under node by the checks below."""
    js = lineage_view_source()
    right = js[js.index("const right ="):js.index("clear(drawer,", js.index("const right ="))]
    assert right.count(EVIDENCE_CALL) == 1, "the drawer does not draw the evidence tier, or draws it whether or not the response carries one"
    assert ENVELOPE_TIER in right and RAW_TIER in right, "the decoded envelope or the RAW tier is gone"
    assert right.index(EVIDENCE_CALL) < right.index(ENVELOPE_TIER) < right.index(RAW_TIER), \
        "the evidence tier is not above the decoded envelope, or the RAW tier is gone"
    assert 'h("div", { class: d.raw_vouch ? "flag" : "note-line" }, d.raw || "no raw state was served"));' in right, \
        "the RAW tier no longer renders as it did before amendment 9.31"
    assert 'export const EVIDENCE_TITLE = "EVIDENCE · AS CAPTURED";' in evidence_view_source(), "the tier is not titled EVIDENCE · AS CAPTURED"
    css = showcase_css()
    for rule in (".ev-shot {", ".ev-bar {", "mark.ev-span {"):
        assert rule in css, f"app.css has no rule {rule!r} for the evidence snapshot"


def break_evidence_drawn_without_evidence(ctx):
    real = lineage_view_source()
    assert real.count(EVIDENCE_CALL) == 1
    ctx.mp.setattr(sys.modules[__name__], "lineage_view_source", lambda: real.replace(EVIDENCE_CALL, "evidenceTier(d.evidence || {}, d.event_id),"))


def break_evidence_below_the_envelope(ctx):
    real = lineage_view_source()
    moved = real.replace("        " + EVIDENCE_CALL + "\n", "").replace(RAW_TIER, EVIDENCE_CALL + " " + RAW_TIER)
    ctx.mp.setattr(sys.modules[__name__], "lineage_view_source", lambda: moved)


def break_raw_tier_dropped(ctx):
    real = lineage_view_source()
    assert real.count(RAW_TIER) == 1
    ctx.mp.setattr(sys.modules[__name__], "lineage_view_source", lambda: real.replace(RAW_TIER, ""))


def test_drawer_draws_evidence_above_the_envelope(ctx):
    check_drawer_draws_evidence_above_the_envelope(ctx)


#: A fake document for node: elements record their attributes, styles and children, a text node records its
#: text, and every write to innerHTML or a sibling sink is recorded. The dom.js probe that learns the SVG
#: namespace writes "<svg></svg>" once; app/tests/test_static.py pins that line.
EVIDENCE_HARNESS = """
const writes = [];
class N {
  constructor(tag, ns) { this.tag = String(tag).toLowerCase(); this.ns = ns; this.attrs = {}; this.kids = []; this.css = {}; const self = this; this.style = { setProperty(k, v) { self.css[k] = String(v); } }; }
  setAttribute(k, v) { this.attrs[k] = String(v); }
  addEventListener() {}
  append(...k) { this.kids.push(...k); }
  replaceChildren(...k) { this.kids = [...k]; }
  set innerHTML(v) { writes.push(String(v)); if (v === "<svg></svg>") this.kids = [new N("svg", "svg-ns")]; }
  set outerHTML(v) { writes.push(String(v)); }
  insertAdjacentHTML(_, v) { writes.push(String(v)); }
  get firstChild() { return this.kids[0]; }
  get namespaceURI() { return this.ns; }
}
class T extends N { constructor(d) { super("#text", null); this.data = String(d); } }
globalThis.Node = N;
globalThis.document = { createElement: (t) => new N(t, "html-ns"), createElementNS: (ns, t) => new N(t, ns), createTextNode: (d) => new T(d) };
const { evidenceTier } = await import("./evidence.mjs");
const ser = (n) => n instanceof T ? { text: n.data } : { tag: n.tag, attrs: n.attrs, css: n.css, kids: n.kids.map(ser) };
const out = { trees: {}, refused: {} };
for (const [name, ev] of Object.entries(SAMPLES.drawn)) out.trees[name] = ser(evidenceTier(ev, SAMPLES.claim));
for (const [name, ev] of Object.entries(SAMPLES.refused)) out.refused[name] = ser(evidenceTier(ev, SAMPLES.claim));
out.writes = writes;
const api = await import("./api.mjs");
api.setCasePack({ responses: {} });
out.pack = ser(evidenceTier(SAMPLES.drawn.post, SAMPLES.claim));
console.log(JSON.stringify(out));
"""

EVIDENCE_CLAIM = "8c1d4b2e-3f60-5a7b-9c8d-0e1f2a3b4c5d"
#: A second claim, whose span overlaps the head claim's in the overlap sample.
OTHER_CLAIM = "11111111-3f60-5a7b-9c8d-0e1f2a3b4c5d"
#: A character outside the Basic Multilingual Plane, two UTF-16 code units long.
ASTRAL = "\U0001F6B4"
EVIDENCE_NOTE = "Invented for this test: no page and no person stands behind this snapshot."
ROUTE_PATH = "M 2 9 C 4 3, 8 2, 11 4 L 18 6 Z"


def evidence_samples() -> dict:
    """One evidence object of each kind, and the objects the closed shape refuses. No value here names a person:
    a handle or a name is a corpus placeholder, and a link is built at run time."""
    claim = EVIDENCE_CLAIM

    def base(kind):
        return {"kind": kind, "captured_at": "2026-11-09T13:54:40Z", "captured_by": {"tool": "snapshot-test", "version": "0.1.0"},
                "source_label": f"a {kind} source", "content_type": "text/html", "sha256": "ab" * 32, "size_bytes": 2048,
                "provenance_note": EVIDENCE_NOTE}

    def units(text):
        """A Python string's length in UTF-16 code units, the unit a span's offsets count."""
        return len(text.encode("utf-16-le")) // 2

    def spanned(text, phrase):
        i = units(text[:text.index(phrase)])
        return {"text": text, "spans": [{"start": i, "end": i + units(phrase), "claim_event_id": claim}]}

    drawn = {
        "post": {**base("post"), "fields": [{"label": "author", "value": "<synthetic-handle-1>"}, {"label": "likes", "value": "41"}],
                 **spanned("Rode the <b>river</b> loop past the mill bridge today.", "past the mill bridge"),
                 "media": {"kind": "thumbnail", "description": "a path at dawn", "width": 4, "height": 3}},
        "message": {**base("message"), "fields": [{"label": "author", "value": "<synthetic-handle-1>"}], **spanned("I can lead the ride.", "lead the ride")},
        "record": {**base("record"), "title": "Entity detail", "fields": [{"label": "Entity name", "value": "Example Works LLC"},
                                                                         {"label": "Registered agent", "value": "<synthetic-name-1>", "claim_event_id": claim}]},
        "profile": {**base("profile"), "fields": [{"label": "headline", "value": "Bike mechanic", "claim_event_id": claim}]},
        "page": {**base("page"), "title": "Members", **spanned("Ride captains this season: <synthetic-name-1>.", "<synthetic-name-1>")},
        "video": {**base("video"), "title": "A restoration, part 2", "fields": [{"label": "channel", "value": "Example channel"}],
                  **spanned("Thanks to the shop on the dock for the parts.", "the shop on the dock")},
        "activity": {**base("activity"), "title": "Morning Ride", "fields": [{"label": "distance", "value": "24.6 km"}, {"label": "club", "value": "Example riders", "claim_event_id": claim}],
                     "media": {"kind": "route", "description": "a loop", "width": 20, "height": 12, "path_d": ROUTE_PATH}},
        "image": {**base("image"), "media": {"kind": "image", "description": "cyclists by a bridge", "width": 3, "height": 2}},
        "tall image": {**base("image"), "media": {"kind": "image", "description": "a narrow banner", "width": 1, "height": 40}},
        "astral post": {**base("post"), **spanned(f"Great ride {ASTRAL}{ASTRAL} past the mill bridge today.", "past the mill bridge")},
        "overlap post": {**base("post"), "text": "alpha beta gamma delta",
                         "spans": [{"start": 0, "end": 10, "claim_event_id": OTHER_CLAIM}, {"start": 6, "end": 16, "claim_event_id": claim}]},
    }
    image = {"kind": "image", "description": "a still", "width": 4, "height": 3}
    route = drawn["activity"]["media"]
    without_note = {k: v for k, v in base("post").items() if k != "provenance_note"}
    refused = {
        "media with a coordinate key": {**drawn["activity"], "media": {**drawn["activity"]["media"], "lat": 1.5}},
        "a key outside the shape": {**drawn["post"], "permalink_path": "a/b"},
        "a link": {**drawn["post"], "text": "see https" + "://" + "example.com", "spans": []},
        "a span outside its text": {**drawn["message"], "spans": [{"start": 2, "end": 999, "claim_event_id": claim}]},
        "a path_d that is not a path": {**drawn["activity"], "media": {**drawn["activity"]["media"], "path_d": "M 1 1 L <x>"}},
        "no provenance note": without_note,
        "a span splitting a character": {**base("post"), "text": f"ride {ASTRAL} on", "spans": [{"start": 6, "end": 9, "claim_event_id": claim}]},
        "media on a record": {**drawn["record"], "media": image},
        "media on a profile": {**drawn["profile"], "media": image},
        "an image on an activity": {**drawn["activity"], "media": image},
        "a route on a post": {**drawn["post"], "media": route},
        "a route on an image": {**drawn["image"], "media": route},
    }
    return {"claim": claim, "drawn": drawn, "refused": refused}


def render_evidence(ctx) -> dict:
    view, lib, dom, words = evidence_view_source(), evidence_lib_source(), dom_source(), words_source()
    for src, spec in ((view, '"../lib/dom.js"'), (view, '"../lib/evidence.js"'), (view, '"../lib/words.js"'), (view, '"../lib/api.js"'),
                      (dom, '"./api.js"'), (words, '"./api.js"')):
        assert spec in src, f"an import the harness rewrites, {spec}, is gone"
    files = {
        "evidence.mjs": view.replace('"../lib/dom.js"', '"./dom.mjs"').replace('"../lib/evidence.js"', '"./evlib.mjs"')
        .replace('"../lib/words.js"', '"./words.mjs"').replace('"../lib/api.js"', '"./api.mjs"'),
        "evlib.mjs": lib, "dom.mjs": dom.replace('"./api.js"', '"./api.mjs"'), "words.mjs": words.replace('"./api.js"', '"./api.mjs"'),
        "api.mjs": api_source(), "harness.mjs": "const SAMPLES = " + json.dumps(evidence_samples()) + ";\n" + EVIDENCE_HARNESS,
    }
    return run_node(ctx, "evidence-harness", files, "the evidence tier")


def tree_nodes(t):
    yield t
    for k in t.get("kids", []):
        yield from tree_nodes(k)


def tree_text(t) -> str:
    return "".join(n["text"] for n in tree_nodes(t) if "text" in n)


def with_class(t, cls) -> list:
    return [n for n in tree_nodes(t) if cls in n.get("attrs", {}).get("class", "").split()]


def check_evidence_text_is_set_as_text(ctx):
    """Every string the evidence tier draws reaches the page as a text node: under node with a recording
    document, nothing but the dom.js namespace probe writes markup, and a capture's text that looks like
    markup is drawn as those characters. Neither file names a way to parse a string as markup."""
    got = render_evidence(ctx)
    assert [w for w in got["writes"] if w != "<svg></svg>"] == [], "the evidence tier parsed a string as markup"
    post = got["trees"]["post"]
    assert any("<b>river</b>" in n["text"] for n in tree_nodes(post) if "text" in n), "a capture's text was not drawn as its own characters"
    for name, src in (("views/evidence.js", evidence_view_source()), ("lib/evidence.js", evidence_lib_source())):
        found = MARKUP_SINK.search(src)
        assert not found, f"{name} names {found.group(0)}, a way to parse a string as markup"


def break_evidence_text_as_markup(ctx):
    real = evidence_view_source()
    old = "    : p.text));"
    assert real.count(old) == 1
    planted = real.replace(old, '    : (() => { const x = h("span", {}); x.innerHTML = p.text; return x; })()));')
    ctx.mp.setattr(sys.modules[__name__], "evidence_view_source", lambda: planted)


def test_evidence_text_is_set_as_text(ctx):
    check_evidence_text_is_set_as_text(ctx)


def check_evidence_spans_are_marked(ctx):
    """The characters a claim was read from are a mark whose title says so, in a post, a message, a page and a
    video page; the field a claim was read from is marked the same way in a record, a profile and an activity;
    and a caption under the snapshot names what the highlight means."""
    got = render_evidence(ctx)
    drawn = evidence_samples()["drawn"]
    for kind in ("post", "message", "page", "video"):
        t = got["trees"][kind]
        span = drawn[kind]["spans"][0]
        want = drawn[kind]["text"][span["start"]:span["end"]]
        marks = [tree_text(n) for n in tree_nodes(t) if n.get("tag") == "mark" and n["attrs"].get("title") == SPAN_WORDS]
        assert marks == [want], f"the {kind} does not mark the span its claim was read from: {marks}"
        assert SPAN_WORDS in tree_text(with_class(t, "ev-cap")[0]), f"the {kind} does not say what its highlight means"
    for kind in ("record", "profile", "activity"):
        t = got["trees"][kind]
        want = [f["value"] for f in drawn[kind]["fields"] if f.get("claim_event_id")]
        marks = [tree_text(n) for n in tree_nodes(t) if n.get("tag") == "mark" and n["attrs"].get("title") == FIELD_WORDS]
        assert marks == want, f"the {kind} does not mark the field its claim was read from: {marks}"
    astral = [tree_text(n) for n in tree_nodes(got["trees"]["astral post"]) if n.get("tag") == "mark" and n["attrs"].get("title") == SPAN_WORDS]
    assert astral == ["past the mill bridge"], f"a span after a character two code units long marks the wrong characters: {astral}"
    t = got["trees"]["overlap post"]
    marks = [n for n in tree_nodes(t) if n.get("tag") == "mark" and n["attrs"].get("title") == SPAN_WORDS]
    head = [tree_text(n) for n in marks if "this" in n["attrs"].get("class", "").split()]
    assert head == ["beta gamma"], f"where spans overlap, the head claim's span is not drawn whole with its outline: {head}"
    assert "".join(tree_text(n) for n in marks) == "alpha beta gamma", "where spans overlap, a claim's characters are not all marked"


def break_spans_not_marked(ctx):
    real = evidence_lib_source()
    old = "else out.push({ text: body.slice(a, b), span });"
    assert real.count(old) == 1
    ctx.mp.setattr(sys.modules[__name__], "evidence_lib_source", lambda: real.replace(old, "else out.push({ text: body.slice(a, b), span: null });"))


HEAD_FIRST = "over.find((sp) => sp.claim_event_id === headId) || over[0] || null;"


def break_overlap_drops_the_head(ctx):
    real = evidence_lib_source()
    assert real.count(HEAD_FIRST) == 1
    ctx.mp.setattr(sys.modules[__name__], "evidence_lib_source", lambda: real.replace(HEAD_FIRST, "over[0] || null;"))


def break_field_not_marked(ctx):
    real = evidence_view_source()
    old = "  return f.claim_event_id\n"
    assert real.count(old) == 1
    ctx.mp.setattr(sys.modules[__name__], "evidence_view_source", lambda: real.replace(old, "  return false\n"))


def test_evidence_spans_are_marked(ctx):
    check_evidence_spans_are_marked(ctx)


def check_route_sketch_uses_only_path_d(ctx):
    """An activity's route is drawn from path_d alone, in a box of its own width and height, labelled as a
    sketch that is not geo-referenced. No attribute or style in any drawn snapshot names a coordinate, a media
    object carrying a coordinate key or a path_d that is not a path is refused in words, and the route's
    drawing reads no field of the media object but path_d, its box and its description."""
    got = render_evidence(ctx)
    t = got["trees"]["activity"]
    paths = [n for n in tree_nodes(t) if n.get("tag") == "path"]
    assert [p["attrs"].get("d") for p in paths] == [ROUTE_PATH], "the route is not drawn from path_d alone"
    svgs = [n for n in tree_nodes(t) if n.get("tag") == "svg"]
    assert len(svgs) == 1 and svgs[0]["attrs"].get("viewBox") == "0 0 20 12", "the route is not drawn in its own box"
    assert "route sketch, not geo-referenced" in tree_text(t), "the route is not labelled as a sketch that is not geo-referenced"
    for name, tree in got["trees"].items():
        for n in tree_nodes(tree):
            named = {k.lower() for k in list(n.get("attrs", {})) + list(n.get("css", {}))}
            assert not named & COORDINATE_WORDS, f"the {name} snapshot carries a coordinate attribute"
    for why in ("media with a coordinate key", "a path_d that is not a path"):
        r = got["refused"][why]
        assert not with_class(r, "ev-shot") and "This snapshot is not drawn" in tree_text(r), f"a snapshot with {why} was drawn"
    view = evidence_view_source()
    sketch = view[view.index("function routeSketch("):view.index("function postCard(")]
    assert set(re.findall(r"media\.(\w+)", sketch)) <= {"path_d", "width", "height", "description"}, "the route reads a field other than path_d and its box"


def break_route_from_another_field(ctx):
    real = evidence_view_source()
    old = 'd: media.path_d }'
    assert real.count(old) == 1
    ctx.mp.setattr(sys.modules[__name__], "evidence_view_source", lambda: real.replace(old, 'd: String(media.route || "M 0 0") }'))


def break_media_admits_a_coordinate(ctx):
    real = evidence_lib_source()
    old = 'MEDIA_KEYS = Object.freeze(["kind", "description", "width", "height", "path_d"]);'
    assert real.count(old) == 1
    ctx.mp.setattr(sys.modules[__name__], "evidence_lib_source", lambda: real.replace(old, old.replace('"path_d"]', '"path_d", "lat"]')))


def break_path_d_admits_anything(ctx):
    real = evidence_lib_source()
    old = "export const PATH_D = /^[MmLlHhVvCcSsQqTtAaZz0-9eE.,\\s+-]{1,4000}$/;"
    assert real.count(old) == 1, "the path_d rule's text changed"
    ctx.mp.setattr(sys.modules[__name__], "evidence_lib_source", lambda: real.replace(old, "export const PATH_D = /^[^]{1,4000}$/;"))


def test_route_sketch_uses_only_path_d(ctx):
    check_route_sketch_uses_only_path_d(ctx)


def check_evidence_provenance_note_is_drawn(ctx):
    """Every drawn snapshot carries its provenance note as its own line above the captured page, and an
    evidence object without one is not drawn."""
    got = render_evidence(ctx)
    for name, t in got["trees"].items():
        order = list(tree_nodes(t))
        notes = with_class(t, "ev-note")
        shots = with_class(t, "ev-shot")
        assert len(notes) == 1 and tree_text(notes[0]) == EVIDENCE_NOTE, f"the {name} snapshot does not draw its provenance note"
        assert len(shots) == 1 and order.index(notes[0]) < order.index(shots[0]), f"the {name} snapshot's note is not above the captured page"
    r = got["refused"]["no provenance note"]
    assert not with_class(r, "ev-shot") and "This snapshot is not drawn" in tree_text(r), "a snapshot without a provenance note was drawn"


def break_note_not_drawn(ctx):
    real = evidence_view_source()
    old = '    h("p", { class: "ev-note" }, ev.provenance_note),\n'
    assert real.count(old) == 1
    ctx.mp.setattr(sys.modules[__name__], "evidence_view_source", lambda: real.replace(old, ""))


def break_note_not_required(ctx):
    """The note is required twice, as a key and as text; the control removes both."""
    real = evidence_lib_source()
    old = '"size_bytes", "provenance_note"]);'
    as_text = 'for (const k of ["captured_at", "source_label", "content_type", "provenance_note"])'
    assert real.count(old) == 1 and real.count(as_text) == 1
    broken = real.replace(old, '"size_bytes"]);').replace(as_text, as_text.replace(', "provenance_note"]', "]"))
    ctx.mp.setattr(sys.modules[__name__], "evidence_lib_source", lambda: broken)


def test_evidence_provenance_note_is_drawn(ctx):
    check_evidence_provenance_note_is_drawn(ctx)


def check_evidence_outside_the_shape_is_not_drawn(ctx):
    """The page draws the closed shape of amendment 9.31 and nothing else: a key outside it, a link and a span
    that falls outside its text each turn the tier into one sentence saying why, with no captured page."""
    got = render_evidence(ctx)
    for why in ("a key outside the shape", "a link", "a span outside its text", "a span splitting a character"):
        r = got["refused"][why]
        assert not with_class(r, "ev-shot") and "This snapshot is not drawn" in tree_text(r), f"a snapshot with {why} was drawn"
    for name, t in got["trees"].items():
        assert len(with_class(t, "ev-shot")) == 1, f"a well-formed {name} snapshot was refused"


def break_shape_admits_any_key(ctx):
    real = evidence_lib_source()
    old = "if (!only(ev, EVIDENCE_KEYS))"
    assert real.count(old) == 1
    ctx.mp.setattr(sys.modules[__name__], "evidence_lib_source", lambda: real.replace(old, 'if (!ev || typeof ev !== "object")'))


def break_shape_admits_a_link(ctx):
    real = evidence_lib_source()
    old = "const LINKISH = /:\\/\\/|\\bwww\\./i;"
    assert real.count(old) == 1
    ctx.mp.setattr(sys.modules[__name__], "evidence_lib_source", lambda: real.replace(old, "const LINKISH = /(?!x)x/;"))


def break_shape_admits_a_stray_span(ctx):
    real = evidence_lib_source()
    old = "if (s.start >= s.end || s.end > ev.text.length)"
    assert real.count(old) == 1
    ctx.mp.setattr(sys.modules[__name__], "evidence_lib_source", lambda: real.replace(old, "if (s.start >= s.end)"))


def break_shape_admits_a_split_character(ctx):
    real = evidence_lib_source()
    old = "      if (splitsPair(ev.text, s.start) || splitsPair(ev.text, s.end))"
    assert real.count(old) == 1
    ctx.mp.setattr(sys.modules[__name__], "evidence_lib_source", lambda: real.replace(old, "      if (false)"))


def test_evidence_outside_the_shape_is_not_drawn(ctx):
    check_evidence_outside_the_shape_is_not_drawn(ctx)


MEDIA_REFUSED = ("media on a record", "media on a profile", "an image on an activity", "a route on a post", "a route on an image")


def check_evidence_media_is_drawn_where_its_card_draws_it(ctx):
    """Media is admitted only where its kind's card draws it: a record and a profile carry none, only an activity
    carries a route, and an activity carries nothing else; each other pairing is refused in words. A neutral box
    is drawn at most 480 pixels tall and prints the proportions its media states, so a 1 by 40 image draws no
    taller than that and still says what it stands for."""
    got = render_evidence(ctx)
    for why in MEDIA_REFUSED:
        r = got["refused"][why]
        assert not with_class(r, "ev-shot") and "This snapshot is not drawn" in tree_text(r), f"a snapshot with {why} was drawn"
    boxes = with_class(got["trees"]["tall image"], "ev-box")
    assert len(boxes) == 1 and boxes[0]["css"].get("max-height") == "480px", "a tall image's box is not capped at 480 pixels"
    assert "stated 1 by 40" in tree_text(boxes[0]), "a capped box does not print the proportions its media states"


def break_record_admits_media(ctx):
    real = evidence_lib_source()
    old = "  record: Object.freeze([]),"
    assert real.count(old) == 1
    ctx.mp.setattr(sys.modules[__name__], "evidence_lib_source", lambda: real.replace(old, '  record: Object.freeze(["image"]),').replace(
        "  profile: Object.freeze([]),", '  profile: Object.freeze(["image"]),'))


def break_activity_admits_an_image(ctx):
    real = evidence_lib_source()
    old = '  activity: Object.freeze(["route"]),'
    assert real.count(old) == 1
    ctx.mp.setattr(sys.modules[__name__], "evidence_lib_source", lambda: real.replace(old, '  activity: Object.freeze(["route", "image"]),'))


def break_post_admits_a_route(ctx):
    real = evidence_lib_source()
    old = '  post: Object.freeze(["image", "thumbnail"]),'
    assert real.count(old) == 1
    ctx.mp.setattr(sys.modules[__name__], "evidence_lib_source", lambda: real.replace(old, '  post: Object.freeze(["image", "thumbnail", "route"]),'))


def break_box_uncapped(ctx):
    real = evidence_view_source()
    old = ', "max-height": `${BOX_MAX_PX}px`'
    assert real.count(old) == 1
    ctx.mp.setattr(sys.modules[__name__], "evidence_view_source", lambda: real.replace(old, ""))


def test_evidence_media_is_drawn_where_its_card_draws_it(ctx):
    check_evidence_media_is_drawn_where_its_card_draws_it(ctx)


HASH_WORDS = "The sha256 names the bytes it stands for, which this page does not hold."
PACK_HASH_WORDS = "This snapshot was written for display by a case pack and stands for no capture, so its sha256 names no bytes."


def check_hash_line_under_a_case_pack(ctx):
    """Without a case pack the hash line says the sha256 names the captured bytes, which the page does not hold.
    Under a case pack the snapshot was written for display, so the line says so and that its sha256 names no
    bytes, and the capture's wording is gone."""
    got = render_evidence(ctx)
    plain, packed = tree_text(got["trees"]["post"]), tree_text(got["pack"])
    assert HASH_WORDS in plain and PACK_HASH_WORDS not in plain, "without a case pack the hash line does not name the captured bytes"
    assert PACK_HASH_WORDS in packed and HASH_WORDS not in packed, "under a case pack the hash line still says the sha256 names captured bytes"


def break_hash_line_ignores_the_pack(ctx):
    real = evidence_view_source()
    old = "hasCasePack() ? PACK_HASH_WORDS : HASH_WORDS"
    assert real.count(old) == 1
    ctx.mp.setattr(sys.modules[__name__], "evidence_view_source", lambda: real.replace(old, "HASH_WORDS"))


def test_hash_line_under_a_case_pack(ctx):
    check_hash_line_under_a_case_pack(ctx)


#: A case pack whose lineage response carries a snapshot written over placeholders. The overlay draws a longer
#: stand-in over one placeholder and a shorter one over the other, so a span after the first moves, a span over
#: the second marks its stand-in, and a span that starts inside the first has no place in the swapped text.
SWAP_HARNESS = """
import { getJSON, setOverlay, setCasePack } from "./api.mjs";
const text = "<synthetic-handle-1> rode past the mill bridge with <synthetic-handle-2>.";
const at = (p) => text.indexOf(p);
const spans = [
  { start: at("past the mill bridge"), end: at("past the mill bridge") + 20, claim_event_id: "c1" },
  { start: at("<synthetic-handle-2>"), end: at("<synthetic-handle-2>") + 20, claim_event_id: "c2" },
  { start: at("<synthetic-handle-1>") + 3, end: at(" rode"), claim_event_id: "c3" },
];
setOverlay({ "<synthetic-handle-1>": "a_much_longer_stand_in", "<synthetic-handle-2>": "ab" });
setCasePack({ responses: { "/api/x": { evidence: { text, spans } } } });
const ev = (await getJSON("/api/x")).body.evidence;
console.log(JSON.stringify({ text: ev.text, cut: ev.spans.map((s) => s.start >= 0 ? ev.text.slice(s.start, s.end) : null), spans: ev.spans }));
"""


def check_case_pack_spans_follow_the_overlay(ctx):
    """Under node, a snapshot read from a case pack through the overlay's swap still marks the characters its
    spans marked before the stand-ins were drawn in: a span after a placeholder moves with it, a span over a
    placeholder marks the stand-in, and a span whose boundary falls inside a placeholder is left at -1, so the
    page refuses the snapshot rather than mark the wrong characters."""
    got = run_node(ctx, "swap-harness", {"api.mjs": api_source(), "harness.mjs": SWAP_HARNESS}, "the overlay's span re-basing")
    assert got["text"] == "a_much_longer_stand_in rode past the mill bridge with ab.", "the overlay did not draw its stand-ins in"
    assert got["cut"][:2] == ["past the mill bridge", "ab"], f"a span no longer marks its characters after the swap: {got['cut']}"
    assert got["spans"][2]["start"] == -1, "a span whose boundary falls inside a placeholder was moved to a guessed place"


REBASE_CALL = '    if (typeof v.text === "string" && Array.isArray(v.spans)) o.spans = v.spans.map((sp) => rebase(v.text, sp));\n'


def break_spans_not_rebased(ctx):
    real = api_source()
    assert real.count(REBASE_CALL) == 1
    ctx.mp.setattr(sys.modules[__name__], "api_source", lambda: real.replace(REBASE_CALL, ""))


def break_split_boundary_guessed(ctx):
    real = api_source()
    old = "return head + swapText(text.slice(i)) === whole ? head.length : -1;"
    assert real.count(old) == 1
    ctx.mp.setattr(sys.modules[__name__], "api_source", lambda: real.replace(old, "return head.length;"))


def test_case_pack_spans_follow_the_overlay(ctx):
    check_case_pack_spans_follow_the_overlay(ctx)


#: The keys of a back lineage response. The server adds no evidence object: raw capture does not cross to
#: LOCAL (EG-2, EG-5), and this server holds and serves no blob (amendment 9.4).
LINEAGE_KEYS = {"event_id", "dir", "chain", "audit", "breaks", "flags", "envelope", "raw", "raw_vouch"}


def check_server_sends_no_evidence(ctx):
    """Over the corpus, the back lineage of an item, a claim and a sentence carries exactly the keys it carried
    before amendment 9.31, and no evidence object: only a display-only case pack supplies one."""
    c = UiClient(ctx, "showcase")
    for name in ("probe-item-1", "extract-claim-handle", "assess-sentence"):
        d = c.get(f"/api/cases/{CASE}/lineage/{eid_of(name)}").json()
        assert "evidence" not in d, f"the server sent an evidence object in the lineage of {name}"
        assert set(d) == LINEAGE_KEYS, f"the lineage of {name} carries keys {sorted(set(d) ^ LINEAGE_KEYS)} it did not carry"


def break_server_sends_evidence(ctx):
    from app.model import lineage

    real = lineage.chain

    def with_evidence(conn, case_id, event_id):
        return dict(real(conn, case_id, event_id), evidence={"kind": "post"})

    ctx.mp.setattr(lineage, "chain", with_evidence)


def test_server_sends_no_evidence(ctx):
    check_server_sends_no_evidence(ctx)


def webrules_source() -> str:
    return (SHOWCASE / "lib" / "webrules.js").read_text(encoding="utf-8")


def connections_source() -> str:
    return (SHOWCASE / "views" / "connections.js").read_text(encoding="utf-8")


WEB_HARNESS = """
import { defaultHops, labelShown, stageHeight, LEGIBLE_NODES } from "./webrules.mjs";
const pairs = ["a|b", "b|c", "c|d"];
console.log(JSON.stringify({
  rest: pairs.map((p) => labelShown(p, null, null, null)),
  selected: pairs.map((p) => labelShown(p, "b", null, null)),
  edge: pairs.map((p) => labelShown(p, null, "c|d", null)),
  hover: pairs.map((p) => labelShown(p, null, null, "d")),
  hops: [57, 41, 40, 17, null].map(defaultHops),
  legible: LEGIBLE_NODES,
  heights: [17, 40, 57].map(stageHeight),
}));
"""


def run_web_rules(ctx) -> dict:
    return run_node(ctx, "web-harness", {"webrules.mjs": webrules_source(), "harness.mjs": WEB_HARNESS}, "the web's reading rules")


#: A card, the seed's included, shows its labels when focused by keyboard as when pointed at, and those labels
#: follow it in the tab order.
KEYBOARD_POINT = "onfocus: () => point(n.node_id)"
KEYBOARD_ORDER = 'if (card) card.after(...[...labels].filter(([k]) => k.split("|").includes(id)).map(([, lab]) => lab));'
LABEL_APPLIED = ("const shown = labelShown(k, selNode, selEdge, hoverId);", "lab.hidden = !shown;", "hidden: !labelShown(k, selNode, selEdge, null),")


def check_web_draws_labels_for_the_selection_only(ctx):
    """At rest no link label is drawn; selecting a node draws the labels of its links, selecting a link draws its
    own, and pointing at a node draws its links' labels. The view applies the rule to every label at creation
    and on every draw, and the key above the web says where the labels went (amendment 9.31)."""
    got = run_web_rules(ctx)
    assert got["rest"] == [False, False, False], "a link label is drawn at rest"
    assert got["selected"] == [True, True, False], "selecting a node does not draw exactly its links' labels"
    assert got["edge"] == [False, False, True], "selecting a link does not draw its own label"
    assert got["hover"] == [False, False, True], "pointing at a node does not draw its links' labels"
    src = connections_source()
    for piece in LABEL_APPLIED:
        assert piece in src, f"the web does not apply the label rule: {piece!r} is gone"
    assert src.count(KEYBOARD_POINT) == 2, "a card focused by keyboard does not show its labels as hover does"
    assert KEYBOARD_ORDER in src, "a focused card's labels do not follow it in the tab order"
    assert "labels: select or point at a node to read its links in words; the List view prints every link" in src, \
        "the key above the web does not say where the labels went"


def break_labels_drawn_at_rest(ctx):
    real = webrules_source()
    old = "  return pair === selEdge ||"
    assert real.count(old) == 1
    ctx.mp.setattr(sys.modules[__name__], "webrules_source", lambda: real.replace(old, "  return true ||"))


def break_label_rule_not_applied(ctx):
    real = connections_source()
    assert real.count(LABEL_APPLIED[1]) == 1
    ctx.mp.setattr(sys.modules[__name__], "connections_source", lambda: real.replace(LABEL_APPLIED[1], ""))


def break_focus_shows_no_labels(ctx):
    real = connections_source()
    assert real.count(", onfocus: () => point(n.node_id)") == 2
    ctx.mp.setattr(sys.modules[__name__], "connections_source", lambda: real.replace(", onfocus: () => point(n.node_id)", ""))


def break_labels_not_in_tab_order(ctx):
    real = connections_source()
    assert real.count(KEYBOARD_ORDER) == 1
    ctx.mp.setattr(sys.modules[__name__], "connections_source", lambda: real.replace(KEYBOARD_ORDER, ""))


def test_web_draws_labels_for_the_selection_only(ctx):
    check_web_draws_labels_for_the_selection_only(ctx)


DEFAULT_SENTENCE_GATE = ": st.hopsAuto && all > LEGIBLE_NODES ? `display depth"
SEED_SCROLL = 'seed.scrollIntoView({ block: "nearest", inline: "nearest" });'
DEFAULT_HOPS = 'st.hops = defaultHops(m.web && m.web.mode === "web" ? m.web.nodes.length : null);'


def check_web_opens_at_two_hops_past_forty_nodes(ctx):
    """A three-hop web of more than forty nodes opens at two hops, the caption says why and that three hops is
    one click away, the three-hop button stays, and choosing a depth ends the default; a web of forty or
    fewer, or one whose size is not known, opens at three as before. The stage grows with the node count."""
    got = run_web_rules(ctx)
    assert got["legible"] == 40 and got["hops"] == [2, 2, 3, 3, 3], f"the default depth rule changed: {got['hops']}"
    assert got["heights"][0] < got["heights"][1] < got["heights"][2], "the stage does not grow with the node count"
    src = connections_source()
    assert DEFAULT_HOPS in src, "the web does not take its default depth from the rule"
    assert "by default: the 3-hop web holds ${all} nodes, more than the ${LEGIBLE_NODES} drawn legibly at once" in src \
        and "3 hops is one click away" in src, "the caption does not say why the web opened at two hops"
    assert "[1, 2, 3].map((n) =>" in src, "the three-hop button is gone"
    assert "st.hops = n; st.hopsAuto = false;" in src, "choosing a depth does not end the default"
    assert 'css: { height: `${stageHeight(web.nodes.length)}px` }' in src, "the stage is not sized to the node count"
    assert DEFAULT_SENTENCE_GATE in src, "the default-depth sentence is not gated on a known web of more than forty nodes"
    assert SEED_SCROLL in src and "if (!st.seedShown) {" in src, "the web does not scroll the seed into view when it first draws"


def break_opens_at_three_past_forty(ctx):
    real = webrules_source()
    old = "nodesAtThree > LEGIBLE_NODES ? 2 : 3;"
    assert real.count(old) == 1
    ctx.mp.setattr(sys.modules[__name__], "webrules_source", lambda: real.replace(old, "nodesAtThree > LEGIBLE_NODES ? 3 : 3;"))


def break_default_without_its_reason(ctx):
    real = connections_source()
    assert real.count("3 hops is one click away") == 1
    ctx.mp.setattr(sys.modules[__name__], "connections_source", lambda: real.replace("3 hops is one click away", "more on request"))


def break_three_hop_button_gone(ctx):
    real = connections_source()
    assert real.count("[1, 2, 3].map((n) =>") == 1
    ctx.mp.setattr(sys.modules[__name__], "connections_source", lambda: real.replace("[1, 2, 3].map((n) =>", "[1, 2].map((n) =>"))


def break_default_sentence_ungated(ctx):
    real = connections_source()
    assert real.count(DEFAULT_SENTENCE_GATE) == 1
    ctx.mp.setattr(sys.modules[__name__], "connections_source", lambda: real.replace(DEFAULT_SENTENCE_GATE, ": st.hopsAuto ? `display depth"))


def break_seed_not_scrolled(ctx):
    real = connections_source()
    assert real.count(SEED_SCROLL) == 1
    ctx.mp.setattr(sys.modules[__name__], "connections_source", lambda: real.replace(SEED_SCROLL, ""))


def test_web_opens_at_two_hops_past_forty_nodes(ctx):
    check_web_opens_at_two_hops_past_forty_nodes(ctx)


NOVOUCH_FLAG = 't.subVouch ? h("span", { class: "nt novouch" }, t.flag) : null,'


def check_web_keeps_its_honesty_marks(ctx):
    """The less crowded web keeps every honesty mark: a proposal's line is dashed, a struck card stays struck on
    its one line, a node the server does not vouch for keeps its flag on the card, the key names the dashed and
    the revoked lines, and display depth, not authorization depth, stays on screen."""
    src = connections_source()
    assert "· display depth, not authorization depth`" in src, "the web no longer says display depth, not authorization depth"
    assert 'h("span", { class: ["nv", !t.mono && "sans", t.struck && "struck", t.generated && "generated"] }, t.title),' in src, \
        "a struck card is no longer struck"
    assert 'if (e.kind === "proposes") return "inf";' in src, "a proposal's line is no longer drawn as an inference"
    assert NOVOUCH_FLAG in src, "a node the server does not vouch for lost its flag on the card"
    for words in ("dashed: proposed by a matcher, not accepted", "revoked: the tombstone stays, struck"):
        assert words in src, f"the key above the web no longer says {words!r}"
    css = showcase_css()
    inf = re.search(r"^\.stage \.e\.inf \{([^}]*)\}", css, re.MULTILINE)
    assert inf and "stroke-dasharray" in inf.group(1), "a proposal's line is no longer dashed"
    struck = re.search(r"^\.struck \{([^}]*)\}", css, re.MULTILINE)
    assert struck and "line-through" in struck.group(1), "struck text is no longer struck through"
    flag = re.search(r"^\.wnode \.nt\.novouch::before \{([^}]*)\}", css, re.MULTILINE)
    assert flag and "var(--hatch)" in flag.group(1), "the card's flag lost its hatch"


def break_depth_disclaimer_dropped(ctx):
    real = connections_source()
    old = "· display depth, not authorization depth`"
    assert real.count(old) == 1
    ctx.mp.setattr(sys.modules[__name__], "connections_source", lambda: real.replace(old, "`"))


def break_card_not_struck(ctx):
    real = connections_source()
    old = 'h("span", { class: ["nv", !t.mono && "sans", t.struck && "struck", t.generated && "generated"] }, t.title),'
    assert real.count(old) == 1
    ctx.mp.setattr(sys.modules[__name__], "connections_source", lambda: real.replace(old, old.replace('t.struck && "struck", ', "")))


def break_proposal_not_dashed(ctx):
    real = showcase_css()
    old = ".stage .e.inf { stroke: #b8bec7; stroke-width: 2; stroke-dasharray: 7 6; }"
    assert real.count(old) == 1
    ctx.mp.setattr(sys.modules[__name__], "showcase_css", lambda: real.replace(old, ".stage .e.inf { stroke: #b8bec7; stroke-width: 2; }"))


def break_card_flag_dropped(ctx):
    real = connections_source()
    assert real.count(NOVOUCH_FLAG) == 1
    ctx.mp.setattr(sys.modules[__name__], "connections_source", lambda: real.replace(NOVOUCH_FLAG, "null,"))


def test_web_keeps_its_honesty_marks(ctx):
    check_web_keeps_its_honesty_marks(ctx)


def ci_source() -> str:
    return (config.REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")


NODE_STEP = "      - name: Node for the showcase checks\n        if: ${{ !cancelled() }}\n        run: node --version\n"
APP_STEP = '      - name: Application tests\n        if: ${{ !cancelled() }}\n        env:\n          PLAINSIGHT_REQUIRE_NODE: "1"\n'


def check_node_checks_fail_without_node_in_ci(ctx):
    """With PLAINSIGHT_REQUIRE_NODE=1 and no node on PATH, a check that runs JavaScript fails rather than skips,
    and CI's workflow runs node --version in its own step before the application tests and sets the variable on
    them, so the node-run checks cannot skip silently there. A local run without the variable still skips."""
    ctx.mp.setattr(shutil, "which", lambda name, *a, **k: None)
    ctx.mp.setenv("PLAINSIGHT_REQUIRE_NODE", "1")
    try:
        run_node(ctx, "absent-node", {"harness.mjs": "console.log('{}');"}, "a probe")
    except pytest.fail.Exception:
        pass
    except pytest.skip.Exception as skipped:
        raise AssertionError("a node-run check skipped with PLAINSIGHT_REQUIRE_NODE=1 and no node") from skipped
    else:
        raise AssertionError("a node-run check passed with no node on PATH")
    ci = ci_source()
    assert NODE_STEP in ci, "CI runs no node --version step"
    assert APP_STEP in ci, "CI's application tests do not set PLAINSIGHT_REQUIRE_NODE=1"
    assert ci.index(NODE_STEP) < ci.index(APP_STEP), "CI checks for node only after the application tests"


def break_require_node_not_read(ctx):
    ctx.mp.setattr(sys.modules[__name__], "REQUIRE_NODE", "PLAINSIGHT_NOT_READ")


def break_ci_without_node_step(ctx):
    real = ci_source()
    assert real.count(NODE_STEP) == 1
    ctx.mp.setattr(sys.modules[__name__], "ci_source", lambda: real.replace(NODE_STEP, ""))


def break_ci_without_require_node(ctx):
    real = ci_source()
    assert real.count(APP_STEP) == 1
    ctx.mp.setattr(sys.modules[__name__], "ci_source", lambda: real.replace('        env:\n          PLAINSIGHT_REQUIRE_NODE: "1"\n', ""))


def test_node_checks_fail_without_node_in_ci(ctx):
    check_node_checks_fail_without_node_in_ci(ctx)


CONTROLS = [
    ("the drawer does not draw the audit trail", check_drawer_renders_the_audit_trail, break_audit_block_not_drawn),
    ("the audit trail hides the chain's flags", check_drawer_renders_the_audit_trail, break_audit_hides_flags),
    ("an audit heading does not re-centre the drawer", check_drawer_renders_the_audit_trail, break_audit_heading_not_a_button),
    ("app.css has no rule for an audit heading", check_drawer_renders_the_audit_trail, break_audit_style_missing),
    ("a planted storage call in the showcase", check_showcase_uses_no_storage_canvas_or_host, break_planted_storage_in_showcase),
    ("a planted POST in the showcase", check_showcase_sends_get_only, break_planted_post),
    ("a planted form built by the element helper", check_showcase_sends_get_only, break_planted_form),
    ("a planted POST whose method is a shorthand property", check_showcase_sends_get_only, break_planted_post_by_a_shorthand),
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
    ("the key to the lines is drawn below the web", check_lines_key_sits_above_the_web, break_key_below_the_web),
    ("the Guide button hides the key that opens it", check_guide_shows_its_key, break_guide_hides_its_key),
    ("the ? key no longer opens the guide", check_guide_shows_its_key, break_question_key_unbound),
    ("the case id can break across two lines", check_top_bar_keeps_the_case_and_synthetic_whole, break_case_id_wraps),
    ("the crumb shrinks under the search box", check_top_bar_keeps_the_case_and_synthetic_whole, break_crumb_shrinks),
    ("a narrow screen hides the word SYNTHETIC", check_top_bar_keeps_the_case_and_synthetic_whole, break_narrow_hides_synthetic),
    ("a narrow screen no longer drops the chip's trailing words", check_top_bar_keeps_the_case_and_synthetic_whole, break_narrow_drops_the_trailing_words_no_more),
    ("the top bar is wider than a phone's screen", check_top_bar_keeps_the_case_and_synthetic_whole, break_phone_top_bar_overflows),
    ("the search box keeps its width at a narrow screen", check_top_bar_keeps_the_case_and_synthetic_whole, break_search_keeps_its_width),
    ("the chip's trailing words are not their own span", check_top_bar_keeps_the_case_and_synthetic_whole, break_trailing_words_not_their_own_span),
    ("the key above the web has no spacing rule", check_lines_key_sits_above_the_web, break_key_above_has_no_rule),
    ("the guide does not list its own key", check_guide_shows_its_key, break_guide_lists_no_own_key),
    ("the evidence tier is drawn without evidence", check_drawer_draws_evidence_above_the_envelope, break_evidence_drawn_without_evidence),
    ("the evidence tier is drawn below the envelope", check_drawer_draws_evidence_above_the_envelope, break_evidence_below_the_envelope),
    ("the RAW tier is dropped", check_drawer_draws_evidence_above_the_envelope, break_raw_tier_dropped),
    ("a capture's text is parsed as markup", check_evidence_text_is_set_as_text, break_evidence_text_as_markup),
    ("a claim's span is not marked", check_evidence_spans_are_marked, break_spans_not_marked),
    ("a claim's field is not marked", check_evidence_spans_are_marked, break_field_not_marked),
    ("the route is drawn from another field", check_route_sketch_uses_only_path_d, break_route_from_another_field),
    ("a route's media admits a coordinate key", check_route_sketch_uses_only_path_d, break_media_admits_a_coordinate),
    ("the provenance note is not drawn", check_evidence_provenance_note_is_drawn, break_note_not_drawn),
    ("the provenance note is not required", check_evidence_provenance_note_is_drawn, break_note_not_required),
    ("the evidence shape admits any key", check_evidence_outside_the_shape_is_not_drawn, break_shape_admits_any_key),
    ("the evidence shape admits a link", check_evidence_outside_the_shape_is_not_drawn, break_shape_admits_a_link),
    ("the evidence shape admits a span outside its text", check_evidence_outside_the_shape_is_not_drawn, break_shape_admits_a_stray_span),
    ("the server sends an evidence object", check_server_sends_no_evidence, break_server_sends_evidence),
    ("link labels are drawn at rest", check_web_draws_labels_for_the_selection_only, break_labels_drawn_at_rest),
    ("the web does not apply the label rule", check_web_draws_labels_for_the_selection_only, break_label_rule_not_applied),
    ("a web past forty nodes opens at three hops", check_web_opens_at_two_hops_past_forty_nodes, break_opens_at_three_past_forty),
    ("the two-hop default does not say why", check_web_opens_at_two_hops_past_forty_nodes, break_default_without_its_reason),
    ("the three-hop button is gone", check_web_opens_at_two_hops_past_forty_nodes, break_three_hop_button_gone),
    ("display depth, not authorization depth is dropped", check_web_keeps_its_honesty_marks, break_depth_disclaimer_dropped),
    ("a struck card is no longer struck", check_web_keeps_its_honesty_marks, break_card_not_struck),
    ("a proposal's line is no longer dashed", check_web_keeps_its_honesty_marks, break_proposal_not_dashed),
    ("a card loses its not-vouched flag", check_web_keeps_its_honesty_marks, break_card_flag_dropped),
    ("overlapping spans drop the head claim's span", check_evidence_spans_are_marked, break_overlap_drops_the_head),
    ("a span boundary may split a character", check_evidence_outside_the_shape_is_not_drawn, break_shape_admits_a_split_character),
    ("the path_d rule admits anything", check_route_sketch_uses_only_path_d, break_path_d_admits_anything),
    ("a record or a profile admits media", check_evidence_media_is_drawn_where_its_card_draws_it, break_record_admits_media),
    ("an activity admits an image", check_evidence_media_is_drawn_where_its_card_draws_it, break_activity_admits_an_image),
    ("a post admits a route", check_evidence_media_is_drawn_where_its_card_draws_it, break_post_admits_a_route),
    ("an image box is not capped", check_evidence_media_is_drawn_where_its_card_draws_it, break_box_uncapped),
    ("the hash line ignores the case pack", check_hash_line_under_a_case_pack, break_hash_line_ignores_the_pack),
    ("spans are not re-based through the swap", check_case_pack_spans_follow_the_overlay, break_spans_not_rebased),
    ("a boundary inside a placeholder is guessed", check_case_pack_spans_follow_the_overlay, break_split_boundary_guessed),
    ("a focused card shows no labels", check_web_draws_labels_for_the_selection_only, break_focus_shows_no_labels),
    ("a focused card's labels are not next in the tab order", check_web_draws_labels_for_the_selection_only, break_labels_not_in_tab_order),
    ("the default-depth sentence is not gated", check_web_opens_at_two_hops_past_forty_nodes, break_default_sentence_ungated),
    ("the seed is not scrolled into view", check_web_opens_at_two_hops_past_forty_nodes, break_seed_not_scrolled),
    ("a node-run check skips under PLAINSIGHT_REQUIRE_NODE", check_node_checks_fail_without_node_in_ci, break_require_node_not_read),
    ("CI runs no node --version step", check_node_checks_fail_without_node_in_ci, break_ci_without_node_step),
    ("CI does not set PLAINSIGHT_REQUIRE_NODE", check_node_checks_fail_without_node_in_ci, break_ci_without_require_node),
]
