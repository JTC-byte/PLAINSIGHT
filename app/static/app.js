// PLAINSIGHT shell: router, keymap, INSPECTOR, header and workspace state.
//
// Every view and every drawer state is a URL: /c/<case>/<view>?focus=&hops=&lineage=
// with working back navigation. A URL carries uuids and fixed words only. The
// client keeps no case material: it never touches browser storage of any kind
// (doctrine/EGRESS.md EG-3), and per-viewer state goes to workspace_kv through
// PUT /api/kv/<case>/<view>, which takes closed keys and opaque values only.
// Every node is inert: selecting one fills the INSPECTOR and nothing else.

import { renderWeb, webNodes, markSelected } from "./views/web.js";
import { renderLineage } from "./views/lineage.js";
import { renderDossier } from "./views/dossier.js";
import { renderPaths, renderList } from "./views/paths.js";
import { openStream } from "./views/stream.js";

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const VIEWS = ["dossier", "web", "paths", "list"];
const SECTORS = ["accounts", "names_aliases", "emails", "phones", "addresses", "organizations", "people", "other_osint"];

export const state = {
  caseId: null, view: null, focus: null, hops: 2, lineage: null, dir: "back",
  from: null, to: null, sector: null, selected: null, marks: [], header: null, keymap: null, pivot: false,
};

export function el(tag, attrs = {}, ...kids) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === null || v === undefined || v === false) continue;
    if (k === "class") node.className = v;
    else if (k.startsWith("on")) node.addEventListener(k.slice(2), v);
    else node.setAttribute(k, v === true ? "" : String(v));
  }
  for (const kid of kids.flat()) {
    if (kid === null || kid === undefined) continue;
    node.append(kid instanceof Node ? kid : document.createTextNode(String(kid)));
  }
  return node;
}

export async function getJSON(url) {
  const r = await fetch(url, { credentials: "same-origin", cache: "no-store" });
  let body = null;
  try { body = await r.json(); } catch (_) { body = null; }
  return { ok: r.ok, status: r.status, body };
}

export async function sendJSON(method, url, payload) {
  const r = await fetch(url, {
    method, credentials: "same-origin", cache: "no-store",
    headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload),
  });
  let body = null;
  try { body = await r.json(); } catch (_) { body = null; }
  return { ok: r.ok, status: r.status, body };
}

export function say(text) {
  document.getElementById("status").textContent = text || "";
}

function uuidOr(v) { return v && UUID.test(v) ? v.toLowerCase() : null; }

function readURL() {
  const parts = location.pathname.split("/").filter(Boolean);
  const q = new URLSearchParams(location.search);
  state.caseId = parts[0] === "c" ? uuidOr(parts[1]) : null;
  state.view = VIEWS.includes(parts[2]) ? parts[2] : null;
  state.focus = uuidOr(q.get("focus"));
  const hops = Number(q.get("hops"));
  state.hops = [1, 2, 3].includes(hops) ? hops : 2;
  state.lineage = uuidOr(q.get("lineage"));
  state.dir = q.get("dir") === "forward" ? "forward" : "back";
  state.from = uuidOr(q.get("from"));
  state.to = uuidOr(q.get("to"));
  state.sector = SECTORS.includes(q.get("sector")) ? q.get("sector") : null;
}

export function urlFor(over = {}) {
  const s = { ...state, ...over };
  const q = new URLSearchParams();
  if (s.focus) q.set("focus", s.focus);
  if (s.view === "web" || s.view === "list") q.set("hops", String(s.hops));
  if (s.sector && (s.view === "web" || s.view === "list")) q.set("sector", s.sector);
  if (s.view === "paths" && s.from && s.to) { q.set("from", s.from); q.set("to", s.to); }
  if (s.lineage) { q.set("lineage", s.lineage); if (s.dir === "forward") q.set("dir", "forward"); }
  const qs = q.toString();
  return `/c/${s.caseId}/${s.view}${qs ? "?" + qs : ""}`;
}

export function go(over = {}, replace = false) {
  const url = urlFor(over);
  if (replace) history.replaceState(null, "", url); else history.pushState(null, "", url);
  readURL();
  render();
  saveWorkspace();
}

function saveWorkspace() {
  if (!state.caseId || !state.view) return;
  const values = { hops: state.hops, drawer: state.lineage ? "open" : "closed" };
  if (state.focus) values.focus = state.focus;
  const view = state.view === "list" ? "web" : state.view;
  sendJSON("PUT", `/api/kv/${state.caseId}/${view}`, values).catch(() => {});
}

async function header() {
  const r = await getJSON(`/api/cases/${state.caseId}/header`);
  if (!r.ok) { say(r.body ? r.body.text : "the case header could not be read"); return null; }
  state.header = r.body;
  document.title = r.body.title;
  document.getElementById("bar-title").textContent = `${r.body.title} · ${r.body.analyst}`;
  const lines = document.getElementById("bar-lines");
  lines.replaceChildren(
    el("div", {}, r.body.environment),
    el("div", { class: r.body.retention_vouch ? "vouch" : "" }, r.body.retention),
    el("div", {}, r.body.anchor),
  );
  const halt = document.getElementById("halt");
  halt.hidden = !r.body.halt;
  halt.textContent = r.body.halt || "";
  const runs = await getJSON(`/api/cases/${state.caseId}/coverage`);
  const runStarts = ((r.body.rollup || {}).event_subtype || {})["PROBE_EVENT.RUN_START"] || 0;
  const cover = runs.ok && runs.body.intervals.length ? runs.body.intervals.map((i) => i.text).join(" · ") : "no coverage interval recorded";
  document.getElementById("runs").textContent = `RUNS · ${runStarts} run start(s) recorded · ${cover}`;
  return r.body;
}

function viewButtons() {
  const nav = document.getElementById("bar-views");
  const mk = (view, key, label) => el("button", {
    "aria-current": state.view === view ? "page" : null,
    onclick: () => go({ view }),
  }, `${key} ${label}`);
  nav.replaceChildren(mk("dossier", "1", "DOSSIER"), mk("web", "7", "WEB"), mk("paths", "8", "PATHS"), mk("list", "t", "LIST"));
  document.getElementById("bar-focus").textContent =
    `FOCUS ${state.focus ? state.focus.slice(0, 8) : "none"} · hops ${state.hops}` +
    (state.marks.length ? ` · marked ${state.marks.map((m) => m.slice(0, 8)).join(", ")}` : "");
}

export async function select(nodeId) {
  state.selected = nodeId;
  markSelected(nodeId);
  const pane = document.getElementById("inspector");
  if (!nodeId) { pane.replaceChildren(el("p", {}, "Select a node to fill the INSPECTOR. Selecting collects nothing.")); return; }
  const r = await getJSON(`/api/cases/${state.caseId}/node/${nodeId}`);
  if (!r.ok) { pane.replaceChildren(el("p", { class: "vouch" }, r.body ? r.body.text : "the node could not be read")); return; }
  const d = r.body;
  const n = d.node;
  const kids = [
    el("h2", {}, `INSPECTOR · ${d.sector_label} · ${n.kind}`),
    el("div", {}, `node ${n.node_id}`),
    ...n.lines.map((line, i) => el("div", { class: (n.generated && i === 1 ? "generated " : "") + (n.revoked || n.kind === "candidate" ? "struck" : "") }, line)),
    ...n.vouch_tokens.map((t) => el("div", { class: "vouch" }, t)),
    el("div", { class: "consequence" }, n.deep_dive_state),
    el("h3", {}, "LINEAGE HEADS"),
    el("ul", {}, n.lineage_heads.map((h) => el("li", {}, el("button", { onclick: () => go({ lineage: h, dir: "back" }) }, `l ${h.slice(0, 8)}`),
      " ", el("button", { onclick: () => go({ lineage: h, dir: "forward" }) }, "⇧L")))),
  ];
  if (d.claims.length) {
    kids.push(el("h3", {}, "CLAIMS"));
    kids.push(el("ul", {}, d.claims.map((c) => el("li", {},
      el("div", {}, `${c.selector_type} `, el("span", { class: c.generated ? "generated" : "" }, c.value)),
      el("div", {}, c.review), el("div", {}, c.relation),
      el("div", { class: c.raw === "raw bytes held" ? "" : "vouch" }, c.raw),
      el("div", {}, c.expiry)))));
  }
  if (d.edges.length) {
    kids.push(el("h3", {}, "EDGES"));
    kids.push(el("ul", {}, d.edges.map((e) => el("li", {}, el("button", { onclick: () => go({ lineage: e.event_id, dir: "back" }) }, "l"), ` ${e.text}`))));
  }
  if (d.unattached_decisions.length) {
    kids.push(el("h3", {}, "UNATTACHED DECISIONS"));
    kids.push(el("ul", {}, d.unattached_decisions.map((u) => el("li", {}, u.text))));
  }
  if (state.pivot) kids.push(pivotBar(d));
  pane.replaceChildren(...kids);
}

function pivotBar(d) {
  const p = d.pivot;
  const out = el("div", { class: "card" },
    el("h3", {}, "PIVOT BAR · one node, one motivating claim"),
    el("div", {}, `target ${p.target_selector_type || "none"}`),
    el("div", {}, `motivating claim ${p.motivating_claim ? p.motivating_claim.slice(0, 8) : "none"}`),
    ...p.capabilities.map((c) => el("div", {}, c)),
    ...p.lines.map((line) => el("div", { class: "consequence" }, line)));
  if (p.motivating_claim) {
    const result = el("div", { class: "consequence" });
    out.append(el("button", {
      onclick: async () => {
        const r = await sendJSON("POST", `/api/cases/${state.caseId}/deep-dives`, { node_id: d.node.node_id, motivating_claim: p.motivating_claim });
        result.textContent = r.body ? (r.body.text || "") : "the deep-dive request could not be read";
      },
    }, "request deep dive"), result);
  }
  return out;
}

async function render() {
  viewButtons();
  const view = document.getElementById("view");
  if (!state.caseId) { await landing(); return; }
  if (!state.header) await header();
  if (!state.view) {
    // A /c/<case> URL with no view lands on the configured landing view, so the
    // address bar always names a view the server serves.
    if (state.header && VIEWS.includes(state.header.landing_view)) go({ view: state.header.landing_view }, true);
    else view.replaceChildren(el("p", { class: "consequence" }, "no view named: open 1 DOSSIER or 7 WEB"));
    return;
  }
  if (!state.focus && state.view !== "paths") {
    const kv = await getJSON(`/api/kv/${state.caseId}/${state.view === "list" ? "web" : state.view}`);
    const saved = kv.ok ? kv.body.values : {};
    const focus = uuidOr(saved.focus) || (state.header && state.header.seed_focus);
    if (focus) { go({ focus, hops: [1, 2, 3].includes(saved.hops) ? saved.hops : state.hops }, true); return; }
  }
  if (state.view === "web") await renderWeb(view, state);
  else if (state.view === "list") await renderList(view, state);
  else if (state.view === "dossier") await renderDossier(view, state);
  else if (state.view === "paths") await renderPaths(view, state);
  await renderRoster();
  await select(state.selected || state.focus);
  const drawer = document.getElementById("lineage");
  drawer.hidden = !state.lineage;
  if (state.lineage) await renderLineage(drawer, state);
}

async function renderRoster() {
  const pane = document.getElementById("roster");
  if (!state.focus) { pane.replaceChildren(el("p", {}, "no focus")); return; }
  const r = await getJSON(`/api/cases/${state.caseId}/web.list?focus=${state.focus}&hops=${state.hops}`);
  if (!r.ok) { pane.replaceChildren(el("p", { class: "vouch" }, r.body ? r.body.text : "the roster could not be read")); return; }
  const groups = { entity: "ENTITIES", cluster: "CLUSTERS", candidate: "EXCLUSIONS", referenced: "REFERENCED ONLY", selector: "SELECTORS" };
  const kids = [el("h2", {}, "ROSTER")];
  for (const [kind, title] of Object.entries(groups)) {
    const rows = r.body.nodes.filter((n) => n.kind === kind);
    if (!rows.length) continue;
    kids.push(el("h3", {}, title));
    kids.push(el("ul", {}, rows.map((n) => el("li", {},
      el("button", { onclick: () => select(n.node_id) }, n.node_id.slice(0, 8)), " ",
      el("span", { class: n.revoked || n.kind === "candidate" ? "struck" : "" }, n.lines[0] || n.kind)))));
  }
  pane.replaceChildren(...kids);
}

async function landing() {
  const r = await getJSON("/api/cases");
  const view = document.getElementById("view");
  if (!r.ok) { view.replaceChildren(el("p", {}, "the case list could not be read")); return; }
  if (r.body.cases.length === 1 && r.body.cases[0].held) {
    history.replaceState(null, "", `/c/${r.body.cases[0].case_id}/${r.body.landing_view}`);
    readURL();
    render();
    return;
  }
  view.replaceChildren(el("h2", {}, "CASES"), el("ul", {}, r.body.cases.map((c) => el("li", {},
    el("button", { onclick: () => { history.pushState(null, "", `/c/${c.case_id}/${r.body.landing_view}`); readURL(); render(); } }, c.title),
    ` ${c.state}`))));
}

function legend() {
  const box = document.getElementById("legend");
  if (!box.hidden) { box.hidden = true; return; }
  const keys = (state.keymap ? state.keymap.keys : []).map((k) =>
    el("li", {}, el("span", { class: "kbd" }, k.key), ` ${k.label}`, k.built ? "" : " (slice 3, not built: records nothing)"));
  box.replaceChildren(
    el("h2", {}, "LEGEND · ?? closes"),
    el("ul", {},
      el("li", {}, "1px solid line: OBSERVATION, a claim observed about an entity, relation unstated"),
      el("li", {}, "2px dashed line: INFERENCE, PROPOSED and not accepted; no analyst has asserted it"),
      el("li", {}, "corner brackets: FUSION, a cluster a named human asserted; struck through when revoked"),
      el("li", {}, "a box reading \"referenced, never promoted in this case\": no observation held; boxes are never dashed"),
      el("li", { class: "generated" }, "~ and italics: a GENERATED value, never an observation"),
      el("li", { class: "vouch" }, "red and the hatch: the system does not vouch; the token beside it says why")),
    el("h3", {}, "KEYS"), el("ul", {}, keys));
  box.hidden = false;
}

function moveRow(step) {
  if (state.view === "web") {
    const order = webNodes();
    if (!order.length) return;
    const i = order.indexOf(state.selected);
    select(order[(i + step + order.length) % order.length]);
    return;
  }
  const rows = [...document.querySelectorAll("#view [data-row]")];
  if (!rows.length) return;
  const i = rows.findIndex((r) => r.classList.contains("selected"));
  rows.forEach((r) => r.classList.remove("selected"));
  const next = rows[(i + step + rows.length) % rows.length];
  next.classList.add("selected");
  next.scrollIntoView({ block: "nearest" });
  if (next.dataset.node) select(next.dataset.node);
}

function moveChip(step) {
  const order = webNodes("selector");
  if (!order.length) return;
  const i = order.indexOf(state.selected);
  select(order[(i + step + order.length) % order.length]);
}

async function selectedHead() {
  if (!state.selected) return null;
  const r = await getJSON(`/api/cases/${state.caseId}/node/${state.selected}`);
  return r.ok ? r.body.node.lineage_heads[0] : null;
}

const ACTIONS = {
  row_next: () => moveRow(1),
  row_prev: () => moveRow(-1),
  chip_next: () => moveChip(1),
  chip_prev: () => moveChip(-1),
  lineage: async () => { const h = await selectedHead(); if (h) go({ lineage: h, dir: "back" }); },
  lineage_forward: async () => { const h = await selectedHead(); if (h) go({ lineage: h, dir: "forward" }); },
  clear_scopes: () => {
    state.marks = []; state.pivot = false;
    go({ focus: state.header ? state.header.seed_focus : state.focus, hops: 2, sector: null, lineage: null, dir: "back" });
  },
  legend,
  view_web: () => go({ view: "web" }),
  view_dossier: () => go({ view: "dossier" }),
  view_paths: () => {
    if (state.marks.length === 2) go({ view: "paths", from: state.marks[0], to: state.marks[1] });
    else say("PATHS needs two marked nodes: select one and press v, then another and press v");
  },
  refocus: () => { if (state.selected) go({ focus: state.selected }); },
  mark: () => {
    if (!state.selected) return;
    state.marks = [...state.marks.filter((m) => m !== state.selected), state.selected].slice(-2);
    viewButtons();
    say(`marked ${state.marks.length} of 2 for PATHS`);
  },
  hops_more: () => go({ hops: Math.min(3, state.hops + 1) }),
  hops_less: () => go({ hops: Math.max(1, state.hops - 1) }),
  list_twin: () => go({ view: "list" }),
  pivot: () => { state.pivot = !state.pivot; select(state.selected || state.focus); },
};

let lastKey = null;
let lastAt = 0;
let pendingQuestion = null;

function keyName(e) {
  if (e.key === "Tab") return e.shiftKey ? "Shift+Tab" : "Tab";
  if (e.key === "L" && e.shiftKey) return "Shift+L";
  return e.key;
}

function run(binding) {
  if (!binding) return;
  if (!binding.built) { say(`${binding.key}: ${binding.label} is not built in this slice; nothing was recorded`); return; }
  const fn = ACTIONS[binding.action];
  if (fn) fn();
}

// Keys a focused control keeps for itself: Tab and Shift+Tab move focus between
// controls, and Enter and Space press the focused button. On the canvas and the
// document body they run their keymap bindings as design 8.6 binds them.
const CONTROL_KEYS = ["Tab", "Shift+Tab", "Enter", " "];

export function controlKeeps(target, name) {
  const focusable = target instanceof HTMLButtonElement || target instanceof HTMLAnchorElement ||
    target instanceof HTMLSelectElement;
  return focusable && CONTROL_KEYS.includes(name);
}

function onKey(e) {
  if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
  if (e.ctrlKey || e.altKey || e.metaKey) return;
  const name = keyName(e);
  if (controlKeeps(e.target, name)) return;
  const keys = state.keymap ? state.keymap.keys : [];
  const now = Date.now();
  const seq = lastKey && now - lastAt < 500 ? `${lastKey} ${name}` : null;
  lastKey = name;
  lastAt = now;
  if (name === "?") {
    if (pendingQuestion) { clearTimeout(pendingQuestion); pendingQuestion = null; lastKey = null; run(keys.find((k) => k.key === "? ?")); }
    else pendingQuestion = setTimeout(() => { pendingQuestion = null; run(keys.find((k) => k.key === "?")); }, 450);
    e.preventDefault();
    return;
  }
  const pair = seq && keys.find((k) => k.key === seq);
  if (pair) { e.preventDefault(); lastKey = null; run(pair); return; }
  const single = keys.find((k) => k.key === name);
  if (single) { e.preventDefault(); run(single); }
}

async function boot() {
  const km = await getJSON("/keymap.json");
  state.keymap = km.ok ? km.body : { keys: [] };
  readURL();
  document.addEventListener("keydown", onKey);
  window.addEventListener("popstate", () => { readURL(); render(); });
  document.getElementById("view").addEventListener("click", (e) => {
    const g = e.target.closest ? e.target.closest("[data-node]") : null;
    if (!g) return;
    if (e.ctrlKey) { const heads = (g.dataset.lineage || "").split(" ").filter(Boolean); if (heads[0]) go({ lineage: heads[0], dir: "back" }); return; }
    select(g.dataset.node);
  });
  await render();
  if (state.caseId) openStream(state.caseId, () => { state.header = null; render(); });
}

boot();
