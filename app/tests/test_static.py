"""The static front end: the keymap is a subset of design 8.6 plus the amendment
keys, and app/static touches no browser storage, no canvas and no external host.
Every text field either front end builds opts out of the browser's spellcheck,
autofill, capitalization, correction and translation, and the classic front
end's writes are sent in the shape the server admits (amendment 9.27)."""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

from app import config

STATIC = config.REPO_ROOT / "app" / "static"
SHOWCASE = config.REPO_ROOT / "app" / "showcase"
FRONT_ENDS = (STATIC, SHOWCASE)
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


def break_a_named_key_marked_unbuilt(ctx):
    """Since slice 3 every key is built, so the control marks one a refusal names
    (x, in ACT_REASON_REQUIRED's moves) as not built; the check must then refuse."""
    real = keymap()
    for k in real["keys"]:
        if k["key"] == "x":
            k["built"] = False
    ctx.mp.setattr(sys.modules[__name__], "keymap", lambda: real)


def test_refusal_moves_name_built_keys(ctx):
    check_refusal_moves_name_built_keys(ctx)


# ---------------------------------------------------------------------------
# text fields keep what is typed into them on this machine (amendment 9.27)
# ---------------------------------------------------------------------------

#: The six attributes every text field carries. They ask the browser not to send what is typed into the field to
#: a spelling or translation service and not to keep it in its form history (review finding 2 of 2026-11-14), and
#: not to offer writing suggestions, which Microsoft Edge turns off for a field by writingsuggestions="false"
#: from version 124 (the P6 read's A3, amendment 9.28).
FIELD_OPT_OUT = {"spellcheck": "false", "autocomplete": "off", "autocapitalize": "off", "autocorrect": "off", "translate": "no",
                 "writingsuggestions": "false"}

#: Each front end's element helper: its file, its first line, and the line that sets the six attributes on an
#: input or a textarea after the caller's own.
HELPERS = (
    (STATIC / "app.js", "export function el(tag, attrs = {}, ...kids) {",
     "for (const [k, v] of Object.entries(field ? { ...attrs, ...FIELD_OPT_OUT } : attrs)) {"),
    (SHOWCASE / "lib" / "dom.js", "export function h(tag, attrs, ...kids) {",
     "apply(node, field ? { ...attrs, ...FIELD_OPT_OUT } : attrs);"),
)
FIELD_LINE = "const field = FIELD_TAGS.includes(String(tag).toLowerCase());"

#: The text of each function that builds an input or a textarea, from the end of its first line to its closing
#: brace: el in the classic app.js, and in the showcase's lib/dom.js h with the apply and append it calls, and s,
#: whose tag is a parameter as h's is, and which builds an SVG element only while it calls createElementNS, so
#: a change that had it build an HTML element would make s("textarea") a field the scan does not see; and
#: svgNamespace, whose answer s passes to createElementNS, since a probe that answered the HTML namespace would
#: make s("textarea") such a field as well. The check reads source and runs none of it, so it pins what each
#: function does to the six attributes, and a change to one of them is refused until a reader has seen what it
#: does and updated its pin here.
HELPER_BODIES = (
    (STATIC / "app.js", "export function el(tag, attrs = {}, ...kids) {", (
        "  const node = document.createElement(tag);",
        "  const field = FIELD_TAGS.includes(String(tag).toLowerCase());",
        "  for (const [k, v] of Object.entries(field ? { ...attrs, ...FIELD_OPT_OUT } : attrs)) {",
        "    if (v === null || v === undefined || v === false) continue;",
        '    if (k === "class") node.className = v;',
        '    else if (k.startsWith("on")) node.addEventListener(k.slice(2), v);',
        '    else node.setAttribute(k, v === true ? "" : String(v));',
        "  }",
        "  for (const kid of kids.flat()) {",
        "    if (kid === null || kid === undefined) continue;",
        "    node.append(kid instanceof Node ? kid : document.createTextNode(String(kid)));",
        "  }",
        "  return node;",
    )),
    (SHOWCASE / "lib" / "dom.js", "function apply(node, attrs) {", (
        "  for (const [k, v] of Object.entries(attrs || {})) {",
        "    if (v === null || v === undefined || v === false) continue;",
        '    if (k === "class") node.setAttribute("class", Array.isArray(v) ? v.filter(Boolean).join(" ") : v);',
        '    else if (k === "css") for (const [p, val] of Object.entries(v)) node.style.setProperty(p, String(val));',
        '    else if (k.startsWith("on") && typeof v === "function") node.addEventListener(k.slice(2), v);',
        '    else node.setAttribute(k, v === true ? "" : String(v));',
        "  }",
    )),
    (SHOWCASE / "lib" / "dom.js", "function append(node, kids) {", (
        "  for (const kid of kids.flat(Infinity)) {",
        "    if (kid === null || kid === undefined || kid === false) continue;",
        "    node.append(kid instanceof Node ? kid : document.createTextNode(shown(String(kid))));",
        "  }",
    )),
    (SHOWCASE / "lib" / "dom.js", "export function h(tag, attrs, ...kids) {", (
        "  const node = document.createElement(tag);",
        "  const field = FIELD_TAGS.includes(String(tag).toLowerCase());",
        "  apply(node, field ? { ...attrs, ...FIELD_OPT_OUT } : attrs);",
        "  append(node, kids);",
        "  return node;",
    )),
    (SHOWCASE / "lib" / "dom.js", "export function s(tag, attrs, ...kids) {", (
        "  const node = document.createElementNS(svgNamespace(), tag);",
        "  apply(node, attrs);",
        "  append(node, kids);",
        "  return node;",
    )),
    (SHOWCASE / "lib" / "dom.js", "function svgNamespace() {", (
        "  if (!svgNS) {",
        '    const probe = document.createElement("div");',
        '    probe.innerHTML = "<svg></svg>";',
        "    svgNS = probe.firstChild.namespaceURI;",
        "  }",
        "  return svgNS;",
    )),
)

#: How lib/dom.js names svgNS, the namespace svgNamespace keeps: its declaration, and the three mentions in the
#: pinned function. A fifth mention could hand s() another namespace without touching a pinned line.
SVG_NS_DECLARATION = "\nlet svgNS = null;\n"
SVG_NS_MENTIONS = 4

#: The createElement calls whose tag is a parameter rather than a literal: el in the classic app.js, and h and
#: its SVG twin s in the showcase's lib/dom.js, each pinned in HELPER_BODIES. Any other mention of either name
#: that the scan cannot read as a call with a literal tag is refused.
HELPER_SITES = {"app/static/app.js": 1, "app/showcase/lib/dom.js": 2}

PAGES = (STATIC / "index.html", SHOWCASE / "index.html")
#: The notranslate meta as both pages write it, which the breakers edit. The check reads each page's tags as an
#: HTML parser reads them, so this text inside a comment or inside another attribute's value does not count.
NOTRANSLATE = '<meta name="google" content="notranslate">'

#: Where markup opens an input or a textarea. Its attributes are read by tag_attributes, as an HTML parser reads
#: them, so a data- look-alike or the six written inside another attribute's value do not count.
MARKUP_FIELD = re.compile(r"<(input|textarea)\b", re.IGNORECASE)
#: Every mention of createElement or createElementNS, however it is reached, and the calls whose tag is a quoted
#: literal, with or without spaces or line breaks before the parenthesis. A mention the second pattern does not
#: read counts as a call whose tag the scan cannot read, so a call made through call or bind, by bracket access,
#: or with an argument the scan cannot parse fails closed.
CREATE_ANY = re.compile(r"\bcreateElement(?:NS)?\b")
CREATE_LITERAL = re.compile(
    r"""\bcreateElement\s*\(\s*["'`]([A-Za-z][A-Za-z0-9-]*)["'`]\s*\)"""
    r"""|\bcreateElementNS\s*\([^,()]*,\s*["'`]([A-Za-z][A-Za-z0-9-]*)["'`]\s*\)"""
)
EDITABLE = re.compile(r"contenteditable|designmode", re.IGNORECASE)
#: A field built from its interface rather than its tag: a customized built-in element, whose class extends
#: HTMLInputElement or HTMLTextAreaElement, can be made with new, and that call names neither input nor textarea
#: where the scan reads a tag. A script may name either interface only in an instanceof test, as the key handlers
#: of both front ends do to leave a field's own keys alone; a test builds nothing, and any other mention is refused.
FIELD_INTERFACE = re.compile(r"\bHTML(?:Input|TextArea)Element\b")
FIELD_INTERFACE_TEST = re.compile(r"\binstanceof\s+HTML(?:Input|TextArea)Element\b")
#: A customized built-in element is made with new only after customElements.define has registered its class, and
#: that class can extend a field's interface without naming it, as one that extends
#: document.querySelector("textarea").constructor does. Neither front end registers a custom element, so a script
#: that names customElements is refused.
CUSTOM_ELEMENTS = re.compile(r"\bcustomElements\b")
#: A script that names one of the six attributes as a word, in any letter case: in setAttribute, removeAttribute
#: or toggleAttribute, as a property or as an object key. Outside the FIELD_OPT_OUT list in the two helpers' files,
#: such a script could turn an attribute back on after the helper returns. A call to translate(), the transform
#: function of SVG and CSS, names no attribute and is not read as one, unless a brace follows its closing
#: parenthesis on its line, as one does where a method named translate is written, such as
#: Object.assign(box, { translate() {} }): a function set as the translate property turns the attribute on. The
#: CSS property of that name is written as the word alone, so a script that sets it is refused as well.
OPT_OUT_NAMED = re.compile(r"\b(?:spellcheck|autocomplete|autocapitalize|autocorrect|writingsuggestions)\b|\btranslate\b(?!\s*\()"
                           r"|\btranslate\s*\([^{}\n]*\)\s*\{", re.IGNORECASE)
FIELD_OPT_OUT_LIST = re.compile(r"const FIELD_OPT_OUT = Object\.freeze\(\{.*?\}\);", re.S)

#: Scripts the scan must not report, because they make no field and name none of the six: an SVG transform
#: written as translate(), and the instanceof tests a key handler uses. Each is planted on its own and scanned.
NOT_FIELDS = (
    ("move.js", 'const g = s("g", { transform: "translate(4, 8)" });\n',
     "the name scan reads a transform's translate() as the translate attribute"),
    ("keys.js", "const typing = (t) => t instanceof HTMLInputElement || t instanceof HTMLTextAreaElement;\n",
     "the interface scan reads an instanceof test as a field built from its interface"),
)


def front_end_text(path) -> str:
    return Path(path).read_text(encoding="utf-8")


def _rel(path: Path) -> str:
    try:
        return path.relative_to(config.REPO_ROOT).as_posix()
    except ValueError:
        return path.name


def _js_object(text: str, name: str) -> dict[str, str]:
    m = re.search(rf"const {name} = Object\.freeze\(\{{(.*?)\}}\);", text, re.S)
    return dict(re.findall(r'(\w+):\s*"([^"]*)"', m.group(1))) if m else {}


def _js_list(text: str, name: str) -> list[str]:
    m = re.search(rf"const {name} = Object\.freeze\(\[(.*?)\]\);", text, re.S)
    return re.findall(r'"([^"]*)"', m.group(1)) if m else []


class _FirstStartTag(HTMLParser):
    """Keeps the attributes of the first start tag the standard library's HTML parser reads."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.attrs = None

    def handle_starttag(self, tag, attrs):
        if self.attrs is None:
            self.attrs = attrs


def _kept(attrs) -> dict[str, str]:
    kept: dict[str, str] = {}
    for name, value in attrs or []:
        kept.setdefault(name, "" if value is None else value)
    return kept


def tag_attributes(text: str) -> dict[str, str]:
    """The attributes of the start tag that opens `text`, as the standard library's HTML parser reads them: each
    name in lower case, character references decoded, the first of a repeated name kept, as a browser keeps it,
    and an attribute written with no value read as the empty string. A tag the parser does not read has none."""
    reader = _FirstStartTag()
    reader.feed(text)
    reader.close()
    return _kept(reader.attrs)


class _StartTags(HTMLParser):
    """Keeps every start tag the standard library's HTML parser reads, in document order, except those inside a
    noscript or a template element. The parser reads no tag inside a comment, and none inside another attribute's
    value. It does read the tags inside noscript and template, where a browser does not: with scripting on, a
    browser reads a noscript element's content as text, and it keeps a template's content out of the document, so
    a meta or an html tag inside either takes no effect."""

    INERT = ("noscript", "template")

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags: list[tuple[str, dict[str, str]]] = []
        self.inert = 0

    def handle_starttag(self, tag, attrs):
        if not self.inert:
            self.tags.append((tag, _kept(attrs)))
        if tag in self.INERT:
            self.inert += 1

    def handle_endtag(self, tag):
        if tag in self.INERT and self.inert:
            self.inert -= 1


def page_tags(text: str) -> list[tuple[str, dict[str, str]]]:
    """Each start tag of a page, in order, with its attributes read as tag_attributes reads them."""
    reader = _StartTags()
    reader.feed(text)
    reader.close()
    return reader.tags


def _a(tag: str) -> str:
    return f"an {tag}" if tag == "input" else f"a {tag}"


def field_sites(roots) -> list[str]:
    """Each place under `roots` where a text field is made without the six attributes or outside an element
    helper, or where a script could turn them back on: an input or a textarea written as markup without them,
    its attributes read as an HTML parser reads the tag; a createElement or createElementNS that names input or
    textarea; a mention of either name outside the helpers that the scan cannot read as a call with a literal
    tag, which covers a call written through call or bind or by bracket access; a script that names
    HTMLInputElement or HTMLTextAreaElement other than in an instanceof test; a script that names customElements,
    which a customized built-in element needs before it can be made with new, whatever class it extends; an
    editable surface, which no helper gives the attributes; and a script that names one of the six outside the
    helpers' FIELD_OPT_OUT, or writes a method named translate. The scan refuses these routes and no other. It
    reads source text, so a tag, a name or markup assembled at run time from pieces is not read, and neither is a
    script that removes a node's attributes by walking them without naming one."""
    found = []
    for root in roots:
        for path in sorted(Path(root).rglob("*")):
            if not path.is_file() or path.suffix not in (".js", ".html"):
                continue
            text, rel = front_end_text(path), _rel(path)
            for m in MARKUP_FIELD.finditer(text):
                attrs = tag_attributes(text[m.start():])
                if any(attrs.get(k, "").lower() != v for k, v in FIELD_OPT_OUT.items()):
                    found.append(f"{rel}: {_a(m.group(1).lower())} written as markup without the six attributes")
            literal = [(m.group(1) or m.group(2)).lower() for m in CREATE_LITERAL.finditer(text)]
            for tag in literal:
                if tag in ("input", "textarea"):
                    found.append(f"{rel}: {_a(tag)} made by createElement outside the element helper")
            unread = len(CREATE_ANY.findall(text)) - len(literal)
            if unread > HELPER_SITES.get(rel, 0):
                found.append(f"{rel}: a createElement the scan cannot read as a call with a literal tag, outside the element helpers")
            if path.suffix == ".js" and len(FIELD_INTERFACE.findall(text)) > len(FIELD_INTERFACE_TEST.findall(text)):
                found.append(f"{rel}: a script names HTMLInputElement or HTMLTextAreaElement other than in an instanceof test, so it could build a field from that interface outside the element helpers")
            if path.suffix == ".js" and CUSTOM_ELEMENTS.search(text):
                found.append(f"{rel}: a script names customElements, so it could register a customized built-in field and make it with new outside the element helpers")
            if EDITABLE.search(text):
                found.append(f"{rel}: an editable surface, which no element helper gives the six attributes")
            script = FIELD_OPT_OUT_LIST.sub("", text, count=1) if rel in HELPER_SITES else text
            if path.suffix == ".js" and OPT_OUT_NAMED.search(script):
                found.append(f"{rel}: a script names one of the six attributes outside FIELD_OPT_OUT, so it could turn one back on after the element helper returns")
    return found


def check_text_fields_opt_out_of_spellcheck_autofill_and_translation(ctx):
    """A browser's enhanced spellcheck and its page translation can send text to a remote service, and its
    autofill keeps typed values in its form history, outside the store the shred reaches (review finding 2,
    EGRESS.md EG-2 and EG-3), and Microsoft Edge turns off its writing suggestions for a field by
    writingsuggestions="false" (the P6 read's A3, amendment 9.28). Every input and textarea either front end
    builds goes through its element helper, which sets spellcheck, autocomplete, autocapitalize, autocorrect,
    translate and writingsuggestions off after the caller's attributes; the text of each function that builds a field is pinned, svgNamespace among them, and lib/dom.js
    names svgNS nowhere else; both pages carry translate="no" on the document and the notranslate meta, read as
    an HTML parser reads the page and outside any noscript or template element; the scan refuses each other way
    of making a field that field_sites lists, and a script that names one of the six outside the helpers' list
    or writes a method named translate; and it reports neither a transform written as translate() nor an
    instanceof test. This reads the source and does not run it."""
    for path, first, applied in HELPERS:
        text, rel = front_end_text(path), _rel(path)
        assert _js_object(text, "FIELD_OPT_OUT") == FIELD_OPT_OUT and _js_list(text, "FIELD_TAGS") == ["input", "textarea"], \
            f"{rel}: FIELD_OPT_OUT is not the six attributes, or FIELD_TAGS is not input and textarea"
        assert first in text, f"{rel}: the element helper is not where this check reads it"
        body = text.split(first, 1)[1].split("\n}\n", 1)[0]
        assert FIELD_LINE in body and applied in body, \
            f"{rel}: the element helper does not set the six attributes on every input and textarea it builds"
    for path, first, lines in HELPER_BODIES:
        text, rel = front_end_text(path), _rel(path)
        assert first in text, f"{rel}: {first} is not where this check reads it"
        body = text.split(first, 1)[1].split("\n}\n", 1)[0]
        assert body == "\n" + "\n".join(lines), \
            (f"{rel}: the function that opens with {first} is not the text this check pinned, so what it does to "
             "the six attributes is unread; read the change, then update its pin in HELPER_BODIES")
    dom = front_end_text(DOM_JS)
    assert dom.count(SVG_NS_DECLARATION) == 1 and len(re.findall(r"\bsvgNS\b", dom)) == SVG_NS_MENTIONS, \
        ("app/showcase/lib/dom.js: svgNS is named outside its declaration and the pinned svgNamespace(), so s() "
         "could be handed a namespace that no pinned line shows")
    for page in PAGES:
        tags, rel = page_tags(front_end_text(page)), _rel(page)
        document = next((attrs for tag, attrs in tags if tag == "html"), {})
        assert document.get("translate", "").lower() == "no", \
            f'{rel}: the page carries no translate="no" on the document, so a browser may translate its text'
        assert any(attrs.get("name", "").lower() == "google" and attrs.get("content", "").lower() == "notranslate"
                   for tag, attrs in tags if tag == "meta"), \
            f"{rel}: the page carries no notranslate meta, so a browser may offer to translate it"
    for name, text, why in NOT_FIELDS:
        root = ctx.tmp / f"not-a-field-{name.split('.')[0]}"
        root.mkdir(exist_ok=True)
        (root / name).write_text(text, encoding="utf-8")
        assert field_sites([root]) == [], f"{why}, so a script that makes no field is refused: {field_sites([root])}"
    sites = field_sites(list(FRONT_ENDS) + ctx.extra_roots)
    assert sites == [], \
        f"a text field is made without the six attributes or outside an element helper, or a script could turn them back on: {sites}"


def _plant(ctx, folder: str, name: str, text: str) -> None:
    root = ctx.tmp / folder
    root.mkdir()
    (root / name).write_text(text, encoding="utf-8")
    ctx.extra_roots.append(root)


def break_planted_field_by_create_element(ctx):
    _plant(ctx, "planted-field", "note.js", 'const box = document.createElement("textarea");\n')


def break_planted_field_as_markup(ctx):
    _plant(ctx, "planted-markup", "form.html", '<label>note <textarea name="note"></textarea></label>\n')


def break_planted_field_by_unread_tag(ctx):
    _plant(ctx, "planted-tag", "note.js", 'const kind = () => ["text", "area"].join("");\nconst box = document.createElement(kind());\n')


def break_planted_editable_surface(ctx):
    _plant(ctx, "planted-editable", "note.js", 'document.getElementById("view").contentEditable = "true";\n')


# The plants below are forms the scan must report: a call to createElement written five more ways, two
# look-alikes of the attributes in markup, and two scripts that turn an attribute back on.


def break_planted_field_by_spaced_create_element(ctx):
    _plant(ctx, "planted-spaced", "note.js", 'const box = document.createElement ("textarea");\n')


def break_planted_field_by_create_element_on_a_new_line(ctx):
    _plant(ctx, "planted-line", "note.js", 'const box = document.createElement\n("input");\n')


def break_planted_field_by_create_element_call(ctx):
    _plant(ctx, "planted-call", "note.js", 'const box = document.createElement.call(document, "input");\n')


def break_planted_field_by_create_element_in_brackets(ctx):
    _plant(ctx, "planted-bracket", "note.js", 'const box = document["createElement"]("input");\n')


def break_planted_field_by_bound_create_element(ctx):
    _plant(ctx, "planted-bind", "note.js", 'const make = document.createElement.bind(document);\nconst box = make("textarea");\n')


def break_planted_field_with_look_alike_attributes(ctx):
    _plant(ctx, "planted-data", "form.html",
           '<textarea data-spellcheck="false" data-autocomplete="off" data-autocapitalize="off" data-autocorrect="off" '
           'data-translate="no"></textarea>\n')


def break_planted_field_with_the_attributes_in_a_value(ctx):
    _plant(ctx, "planted-title", "form.html",
           """<textarea title="spellcheck='false' autocomplete='off' autocapitalize='off' autocorrect='off' """
           """translate='no'"></textarea>\n""")


def break_planted_script_sets_and_removes_an_attribute(ctx):
    _plant(ctx, "planted-set", "note.js",
           'const t = el("textarea");\nt.setAttribute("spellcheck", "true");\nt.removeAttribute("autocomplete");\n')


def break_planted_script_writes_the_properties(ctx):
    _plant(ctx, "planted-property", "note.js", 'const t = el("textarea");\nt.spellcheck = true;\nt.autocomplete = "on";\n')


def break_planted_script_turns_writing_suggestions_on(ctx):
    """A script that turns the sixth attribute back on after the helper returns, which the name scan must read as
    it reads the other five (the P6 read's A3)."""
    _plant(ctx, "planted-writing-suggestions", "note.js",
           'const t = el("textarea");\nt.setAttribute("writingsuggestions", "true");\n')


def break_planted_field_by_its_interface(ctx):
    """A customized built-in textarea made with new, which names neither the tag nor createElement. It reaches the
    registry through a name assembled at run time, so the interface's name is all the scan can read."""
    _plant(ctx, "planted-interface", "note.js",
           'const registry = window["custom" + "Elements"];\nclass NoteBox extends HTMLTextAreaElement {}\n'
           'registry.define("note-box", NoteBox, { extends: "textarea" });\nconst box = new NoteBox();\n')


def break_planted_field_by_a_found_constructor(ctx):
    """The last reader's plant of 2026-11-15: a customized built-in textarea whose class extends the constructor
    of a textarea found in the page, so it names neither interface."""
    _plant(ctx, "planted-constructor", "note.js",
           'class NoteBox extends document.querySelector("textarea").constructor {}\n'
           'customElements.define("note-box", NoteBox, { extends: "textarea" });\nconst box = new NoteBox();\n')


def break_planted_script_sets_translate_by_a_method(ctx):
    """The last reader's plant of 2026-11-15: a method named translate, which sets the property to a function and
    so turns the attribute on, written as a call the transform exception would read as translate()."""
    _plant(ctx, "planted-method", "note.js", 'const t = el("textarea");\nObject.assign(t, { translate() {} });\n')


def _read_with(ctx, targets, old: str, new: str) -> None:
    """Patch front_end_text so each file in `targets` reads with its one `old` replaced by `new`."""
    real = front_end_text
    for target in targets:
        assert real(target).count(old) == 1, f"the breaker's text is not in {target.name} exactly once"
    ctx.mp.setattr(sys.modules[__name__], "front_end_text",
                   lambda path: real(path).replace(old, new) if Path(path) in targets else real(path))


DOM_JS = SHOWCASE / "lib" / "dom.js"
SKIP_EMPTY = "if (v === null || v === undefined || v === false) continue;"


def break_classic_helper_removes_an_attribute_after_its_loop(ctx):
    """A mutant of el(): it sets the six attributes and then removes one."""
    _read_with(ctx, (HELPERS[0][0],), "\n  for (const kid of kids.flat()) {",
               '\n  if (field) node.removeAttribute("autocomplete");\n  for (const kid of kids.flat()) {')


def break_showcase_apply_skips_translate(ctx):
    """A mutant of apply(): it skips the translate attribute."""
    _read_with(ctx, (DOM_JS,), SKIP_EMPTY, SKIP_EMPTY.replace(") continue;", ' || k === "translate") continue;'))


def break_showcase_apply_skips_the_value_off(ctx):
    """A change to apply() that names no attribute, so only the pin sees it: it skips every value off, which
    drops autocomplete, autocapitalize and autocorrect."""
    _read_with(ctx, (DOM_JS,), SKIP_EMPTY, SKIP_EMPTY.replace(") continue;", ' || v === "off") continue;'))


def break_classic_helper_sets_no_opt_out(ctx):
    _read_with(ctx, (HELPERS[0][0],), HELPERS[0][2], "for (const [k, v] of Object.entries(attrs)) {")


def break_showcase_helper_sets_no_opt_out(ctx):
    _read_with(ctx, (HELPERS[1][0],), HELPERS[1][2], "apply(node, attrs);")


def break_classic_opt_out_lacks_spellcheck(ctx):
    _read_with(ctx, (HELPERS[0][0],), 'spellcheck: "false", ', "")


#: The sixth attribute's line in each helper's FIELD_OPT_OUT, which the two breakers below remove.
WRITING_SUGGESTIONS_LINE = '\n  writingsuggestions: "false",'


def break_classic_opt_out_lacks_writing_suggestions(ctx):
    _read_with(ctx, (HELPERS[0][0],), WRITING_SUGGESTIONS_LINE, "")


def break_showcase_opt_out_lacks_writing_suggestions(ctx):
    _read_with(ctx, (HELPERS[1][0],), WRITING_SUGGESTIONS_LINE, "")


def break_pages_drop_translate_no(ctx):
    _read_with(ctx, PAGES, '<html lang="en" translate="no">', '<html lang="en">')


def break_pages_drop_the_notranslate_meta(ctx):
    _read_with(ctx, PAGES, NOTRANSLATE + "\n", "")


def break_showcase_svg_helper_builds_html(ctx):
    """A mutant of s(): it builds an HTML element, so s("textarea") makes a field without the six attributes, while
    the scan still counts the one unread createElement in s that HELPER_SITES allows."""
    _read_with(ctx, (DOM_JS,), "document.createElementNS(svgNamespace(), tag);", "document.createElement(tag);")


def break_pages_carry_a_look_alike_of_translate_no(ctx):
    _read_with(ctx, PAGES, '<html lang="en" translate="no">', '<html lang="en" data-translate="no">')


def break_pages_carry_translate_no_in_a_comment(ctx):
    """Each page's document tag drops translate="no", and a copy of the tag that keeps it stands in a comment above."""
    _read_with(ctx, PAGES, '<html lang="en" translate="no">', '<!-- <html lang="en" translate="no"> -->\n<html lang="en">')


def break_pages_carry_the_meta_in_a_comment(ctx):
    _read_with(ctx, PAGES, NOTRANSLATE, f"<!-- {NOTRANSLATE} -->")


def break_pages_carry_the_meta_in_noscript(ctx):
    """The last reader's plant of 2026-11-15: the meta inside a noscript element, whose content a browser with
    scripting on reads as text."""
    _read_with(ctx, PAGES, NOTRANSLATE, f"<noscript>{NOTRANSLATE}</noscript>")


def break_pages_carry_the_meta_in_a_template(ctx):
    _read_with(ctx, PAGES, NOTRANSLATE, f"<template>{NOTRANSLATE}</template>")


def break_showcase_svg_namespace_probes_html(ctx):
    """The last reader's mutant of 2026-11-15: svgNamespace() probes markup that answers the HTML namespace, so
    s("textarea") makes a field without the six attributes."""
    _read_with(ctx, (DOM_JS,), 'probe.innerHTML = "<svg></svg>";', 'probe.innerHTML = "<p></p>";')


def break_showcase_svg_namespace_set_elsewhere(ctx):
    """A function outside the pins that sets svgNS, so s() could be handed another namespace."""
    _read_with(ctx, (DOM_JS,), "export function clear(node, ...kids) {",
               "export function useNamespace(ns) {\n  svgNS = ns;\n}\n\nexport function clear(node, ...kids) {")


def break_name_scan_reads_a_translate_call(ctx):
    """The name scan as it was before the second verification: it reads translate() as the attribute."""
    ctx.mp.setattr(sys.modules[__name__], "OPT_OUT_NAMED",
                   re.compile(r"\b(?:spellcheck|autocomplete|autocapitalize|autocorrect|translate)\b", re.IGNORECASE))


def break_interface_scan_reads_an_instanceof_test(ctx):
    """An interface scan that counts every mention of the two interfaces, an instanceof test among them."""
    ctx.mp.setattr(sys.modules[__name__], "FIELD_INTERFACE_TEST", re.compile(r"(?!)"))


def test_text_fields_opt_out_of_spellcheck_autofill_and_translation(ctx):
    check_text_fields_opt_out_of_spellcheck_autofill_and_translation(ctx)


SEND_JSON = "export async function sendJSON(method, url, payload) {"

#: A request that could write, outside sendJSON: a fetch or a Request given a method, and the two other request
#: APIs. A form the classic front end builds is sent by script, and the CSP's form-action 'none' refuses a form's
#: own submission (app/tests/test_http.py checks that header).
WRITE_OUTSIDE = re.compile(r"\bmethod\b|XMLHttpRequest|sendBeacon", re.IGNORECASE)


def writes_outside_send_json(roots) -> list[str]:
    """Each file under `roots` that names a request that could write anywhere but in sendJSON, whose own text is
    left out of app.js before the scan. The scan reads source text, so a method assembled at run time is not
    read."""
    found = []
    for root in roots:
        for path in sorted(Path(root).rglob("*")):
            if not path.is_file() or path.suffix not in (".js", ".html"):
                continue
            if path == STATIC / "app.js":
                before, _, after = app_js().partition(SEND_JSON)
                text = before + after.split("\n}\n", 1)[-1]
            else:
                text = path.read_text(encoding="utf-8")
            if WRITE_OUTSIDE.search(text):
                found.append(_rel(path))
    return found


def check_the_page_sends_writes_the_server_admits(ctx):
    """The classic front end sends its writes, the workspace keys, the deep dive and the acts, through sendJSON,
    and no file under app/static names a request that could write anywhere else. sendJSON's fetch keeps the
    default mode, cors, because in any other mode a page served with Referrer-Policy: no-referrer sends Origin:
    null on a POST or PUT (the Fetch standard's step that appends the Origin header), and it sends
    application/json. The server refuses a write whose Origin is not its own and one that is not
    application/json (amendment 9.27). sendJSON names no mode at all, as a key or as a shorthand property, names
    headers and credentials once each, because the last of a repeated key wins in an object literal, and spreads
    or assigns no other object into its options, whose keys this check could not count. This reads the source and
    does not run it."""
    js = app_js()
    assert SEND_JSON in js, "sendJSON is not where this check reads it"
    body = js.split(SEND_JSON, 1)[1].split("\n}\n", 1)[0]
    assert re.search(r"\bmode\b", body) is None, \
        "sendJSON names a fetch mode, and outside cors a page served with no-referrer sends Origin: null, which the server refuses"
    assert 'headers: { "Content-Type": "application/json" }' in body, \
        "sendJSON does not send application/json, which the server requires of a write"
    assert len(re.findall(r"\bheaders\b", body)) == 1, \
        "sendJSON names headers more than once, and the last of a repeated key wins, so it may not send application/json"
    assert 'credentials: "same-origin"' in body, "sendJSON does not send the session cookie"
    assert len(re.findall(r"\bcredentials\b", body)) == 1, \
        "sendJSON names credentials more than once, and the last of a repeated key wins, so it may not send the session cookie"
    assert re.search(r"\.\.\.|\bassign\b", body) is None, \
        "sendJSON spreads or assigns another object into its fetch options, whose keys this check cannot count"
    sites = writes_outside_send_json([STATIC] + ctx.extra_roots)
    assert sites == [], f"a request that could write is sent outside sendJSON, the one place whose shape the server admits: {sites}"


def break_send_json_in_same_origin_mode(ctx):
    real = app_js()
    assert real.count("method, credentials:") == 1
    ctx.mp.setattr(sys.modules[__name__], "app_js", lambda: real.replace("method, credentials:", 'method, mode: "same-origin", credentials:'))


def break_send_json_as_text(ctx):
    real = app_js()
    old = 'headers: { "Content-Type": "application/json" }'
    assert real.count(old) == 1
    ctx.mp.setattr(sys.modules[__name__], "app_js", lambda: real.replace(old, 'headers: { "Content-Type": "text/plain" }'))


def break_a_second_write_beside_send_json(ctx):
    """A second function in app.js that writes. In no-cors mode a fetch sends text/plain and Origin: null, both
    of which the server refuses, so the page's write would fail."""
    real = app_js()
    raw = ('\nexport async function sendRaw(url, payload) {\n'
           '  return fetch(url, { method: "POST", mode: "no-cors", body: JSON.stringify(payload) });\n}\n')
    ctx.mp.setattr(sys.modules[__name__], "app_js", lambda: real + raw)


def break_planted_beacon(ctx):
    _plant(ctx, "planted-beacon", "beacon.js", 'navigator.sendBeacon("/api/kv/x/web", JSON.stringify({ hops: 2 }));\n')


def break_send_json_mode_as_a_shorthand(ctx):
    """A mutant of sendJSON that sets no-cors through a shorthand property, which names mode with no colon."""
    real = app_js()
    old = SEND_JSON + "\n  const r = await fetch(url, {\n    method, credentials:"
    assert real.count(old) == 1
    new = SEND_JSON + '\n  const mode = "no-cors";\n  const r = await fetch(url, {\n    method, mode, credentials:'
    ctx.mp.setattr(sys.modules[__name__], "app_js", lambda: real.replace(old, new))


def break_send_json_names_headers_twice(ctx):
    """A mutant of sendJSON whose second headers key, the one the object literal keeps, sends text/plain."""
    real = app_js()
    old = 'headers: { "Content-Type": "application/json" },'
    assert real.count(old) == 1
    ctx.mp.setattr(sys.modules[__name__], "app_js", lambda: real.replace(old, old + ' headers: { "Content-Type": "text/plain" },'))


def break_send_json_names_credentials_twice(ctx):
    """A mutant of sendJSON whose second credentials key, the one the object literal keeps, sends no cookie."""
    real = app_js()
    old = 'method, credentials: "same-origin", cache: "no-store",'
    assert real.count(old) == 1
    ctx.mp.setattr(sys.modules[__name__], "app_js", lambda: real.replace(old, old + ' credentials: "omit",'))


def break_send_json_spreads_defaults(ctx):
    """The last reader's mutant of 2026-11-15: options kept in a constant outside sendJSON, spread last into its
    own, where no key count reads them. In no-cors mode the page would send no cookie."""
    real = app_js()
    old = 'headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload),'
    assert real.count(old) == 1
    defaults = 'const FETCH_DEFAULTS = Object.freeze({ mode: "no-cors", credentials: "omit" });\n'
    ctx.mp.setattr(sys.modules[__name__], "app_js", lambda: defaults + real.replace(old, old + " ...FETCH_DEFAULTS,"))


def break_send_json_assigns_defaults(ctx):
    """A mutant of sendJSON that merges a constant's options into its own with Object.assign."""
    real = app_js()
    old_open = SEND_JSON + "\n  const r = await fetch(url, {\n"
    old_close = "body: JSON.stringify(payload),\n  });"
    assert real.count(old_open) == 1 and real.count(old_close) == 1
    defaults = 'const FETCH_DEFAULTS = Object.freeze({ mode: "no-cors", credentials: "omit" });\n'
    mutated = real.replace(old_open, SEND_JSON + "\n  const r = await fetch(url, Object.assign({\n").replace(
        old_close, "body: JSON.stringify(payload),\n  }, FETCH_DEFAULTS));")
    ctx.mp.setattr(sys.modules[__name__], "app_js", lambda: defaults + mutated)


def test_the_page_sends_writes_the_server_admits(ctx):
    check_the_page_sends_writes_the_server_admits(ctx)


CONTROLS = [
    ("the keymap gains a d", check_keymap_is_a_subset_of_8_6, break_keymap_gains_d),
    ("a planted storage call", check_static_uses_no_storage_canvas_or_host, break_planted_storage_call),
    ("onKey captures every key", check_focused_controls_keep_tab_and_enter, break_on_key_captures_everything),
    ("a key a refusal names is marked unbuilt", check_refusal_moves_name_built_keys, break_a_named_key_marked_unbuilt),
    # amendment 9.27: the read-only review of the HTTP boundary of 2026-11-14
    ("a planted field made by createElement", check_text_fields_opt_out_of_spellcheck_autofill_and_translation, break_planted_field_by_create_element),
    ("a planted field written as markup", check_text_fields_opt_out_of_spellcheck_autofill_and_translation, break_planted_field_as_markup),
    ("a planted createElement whose tag is not a literal", check_text_fields_opt_out_of_spellcheck_autofill_and_translation, break_planted_field_by_unread_tag),
    ("a planted editable surface", check_text_fields_opt_out_of_spellcheck_autofill_and_translation, break_planted_editable_surface),
    ("the classic element helper sets no opt-out", check_text_fields_opt_out_of_spellcheck_autofill_and_translation, break_classic_helper_sets_no_opt_out),
    ("the showcase element helper sets no opt-out", check_text_fields_opt_out_of_spellcheck_autofill_and_translation, break_showcase_helper_sets_no_opt_out),
    ("the classic opt-out lacks spellcheck", check_text_fields_opt_out_of_spellcheck_autofill_and_translation, break_classic_opt_out_lacks_spellcheck),
    ("the classic opt-out lacks writingsuggestions", check_text_fields_opt_out_of_spellcheck_autofill_and_translation, break_classic_opt_out_lacks_writing_suggestions),
    ("the showcase opt-out lacks writingsuggestions", check_text_fields_opt_out_of_spellcheck_autofill_and_translation, break_showcase_opt_out_lacks_writing_suggestions),
    ("a planted script that turns writingsuggestions on", check_text_fields_opt_out_of_spellcheck_autofill_and_translation, break_planted_script_turns_writing_suggestions_on),
    ("the pages drop translate=no", check_text_fields_opt_out_of_spellcheck_autofill_and_translation, break_pages_drop_translate_no),
    ("the pages drop the notranslate meta", check_text_fields_opt_out_of_spellcheck_autofill_and_translation, break_pages_drop_the_notranslate_meta),
    ("sendJSON sends in same-origin mode", check_the_page_sends_writes_the_server_admits, break_send_json_in_same_origin_mode),
    ("sendJSON sends text/plain", check_the_page_sends_writes_the_server_admits, break_send_json_as_text),
    # the verification of amendment 9.27 of 2026-11-14
    ("a planted createElement with a space before its parenthesis", check_text_fields_opt_out_of_spellcheck_autofill_and_translation, break_planted_field_by_spaced_create_element),
    ("a planted createElement with a line break before its parenthesis", check_text_fields_opt_out_of_spellcheck_autofill_and_translation, break_planted_field_by_create_element_on_a_new_line),
    ("a planted createElement reached through call", check_text_fields_opt_out_of_spellcheck_autofill_and_translation, break_planted_field_by_create_element_call),
    ("a planted createElement reached by bracket access", check_text_fields_opt_out_of_spellcheck_autofill_and_translation, break_planted_field_by_create_element_in_brackets),
    ("a planted createElement reached through bind", check_text_fields_opt_out_of_spellcheck_autofill_and_translation, break_planted_field_by_bound_create_element),
    ("a planted field with data- look-alikes of the attributes", check_text_fields_opt_out_of_spellcheck_autofill_and_translation, break_planted_field_with_look_alike_attributes),
    ("a planted field with the attributes inside another attribute's value", check_text_fields_opt_out_of_spellcheck_autofill_and_translation, break_planted_field_with_the_attributes_in_a_value),
    ("a planted script that sets and removes an attribute", check_text_fields_opt_out_of_spellcheck_autofill_and_translation, break_planted_script_sets_and_removes_an_attribute),
    ("a planted script that writes the properties", check_text_fields_opt_out_of_spellcheck_autofill_and_translation, break_planted_script_writes_the_properties),
    ("the classic helper removes an attribute after its loop", check_text_fields_opt_out_of_spellcheck_autofill_and_translation, break_classic_helper_removes_an_attribute_after_its_loop),
    ("the showcase apply skips translate", check_text_fields_opt_out_of_spellcheck_autofill_and_translation, break_showcase_apply_skips_translate),
    ("the showcase apply skips the value off", check_text_fields_opt_out_of_spellcheck_autofill_and_translation, break_showcase_apply_skips_the_value_off),
    ("a second write function beside sendJSON", check_the_page_sends_writes_the_server_admits, break_a_second_write_beside_send_json),
    ("a planted sendBeacon", check_the_page_sends_writes_the_server_admits, break_planted_beacon),
    # the second verification of amendment 9.27 of 2026-11-14
    ("the showcase's SVG helper builds an HTML element", check_text_fields_opt_out_of_spellcheck_autofill_and_translation, break_showcase_svg_helper_builds_html),
    ("a planted field built from its interface", check_text_fields_opt_out_of_spellcheck_autofill_and_translation, break_planted_field_by_its_interface),
    ("the pages carry a data- look-alike of translate=no", check_text_fields_opt_out_of_spellcheck_autofill_and_translation, break_pages_carry_a_look_alike_of_translate_no),
    ("the pages carry translate=no only inside a comment", check_text_fields_opt_out_of_spellcheck_autofill_and_translation, break_pages_carry_translate_no_in_a_comment),
    ("the pages carry the notranslate meta inside a comment", check_text_fields_opt_out_of_spellcheck_autofill_and_translation, break_pages_carry_the_meta_in_a_comment),
    ("the name scan reads translate() as the attribute", check_text_fields_opt_out_of_spellcheck_autofill_and_translation, break_name_scan_reads_a_translate_call),
    ("the interface scan reads an instanceof test as a field", check_text_fields_opt_out_of_spellcheck_autofill_and_translation, break_interface_scan_reads_an_instanceof_test),
    ("sendJSON sets its mode through a shorthand property", check_the_page_sends_writes_the_server_admits, break_send_json_mode_as_a_shorthand),
    ("sendJSON names headers twice", check_the_page_sends_writes_the_server_admits, break_send_json_names_headers_twice),
    ("sendJSON names credentials twice", check_the_page_sends_writes_the_server_admits, break_send_json_names_credentials_twice),
    # the rework of amendment 9.27 of 2026-11-16, on the last reader's notes of 2026-11-15
    ("the showcase's namespace probe answers HTML", check_text_fields_opt_out_of_spellcheck_autofill_and_translation, break_showcase_svg_namespace_probes_html),
    ("the showcase sets svgNS outside the pins", check_text_fields_opt_out_of_spellcheck_autofill_and_translation, break_showcase_svg_namespace_set_elsewhere),
    ("a planted field whose class extends a found constructor", check_text_fields_opt_out_of_spellcheck_autofill_and_translation, break_planted_field_by_a_found_constructor),
    ("a planted method named translate", check_text_fields_opt_out_of_spellcheck_autofill_and_translation, break_planted_script_sets_translate_by_a_method),
    ("the pages carry the notranslate meta inside noscript", check_text_fields_opt_out_of_spellcheck_autofill_and_translation, break_pages_carry_the_meta_in_noscript),
    ("the pages carry the notranslate meta inside a template", check_text_fields_opt_out_of_spellcheck_autofill_and_translation, break_pages_carry_the_meta_in_a_template),
    ("sendJSON spreads a constant's options into its own", check_the_page_sends_writes_the_server_admits, break_send_json_spreads_defaults),
    ("sendJSON assigns a constant's options into its own", check_the_page_sends_writes_the_server_admits, break_send_json_assigns_defaults),
]
