// PLAINSIGHT showcase shell: one person at the centre, seven tabs, one drawer.
//
// The page is /c/<case>/dossier, the server's landing view; the tab and the
// selection live in the fragment (#connections/<node uuid>), which never
// reaches the server and carries a fixed word and a uuid only. The showcase
// reads through GET routes only: no act, no deep dive, no workspace write, and
// nothing in browser storage (doctrine/EGRESS.md EG-3). The view is a snapshot:
// when the case changes on the server, a refresh button appears and nothing
// moves under the reader.

import { h, clear, kbd, notLoaded } from "./lib/dom.js";
import { listCases, loadCase, PARTS } from "./lib/model.js";
import { getJSON, setOverlay, setLiveLook, liveLook, setCasePack, hasCasePack } from "./lib/api.js";
import { TABS, TAB_ORDER, short, placeCount, fictionLabel, sourceWords } from "./lib/words.js";
import { renderStatus, closePopover } from "./views/status.js";
import { renderProfile } from "./views/profile.js";
import { renderOverview } from "./views/overview.js";
import { renderConnections } from "./views/connections.js";
import { renderSources } from "./views/sources.js";
import { renderTimeline } from "./views/timeline.js";
import { renderPlaces } from "./views/places.js";
import { renderTools } from "./views/tools.js";
import { renderAssessment } from "./views/assessment.js";
import { openLineage, closeLineage, lineageOpen, onLineageChange } from "./views/lineage.js";

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const RENDER = {
  overview: renderOverview, connections: renderConnections, sources: renderSources, timeline: renderTimeline,
  places: renderPlaces, tools: renderTools, assessment: renderAssessment,
};

const state = { caseId: null, tab: "overview", selected: null, lineage: null, model: null, search: "", changed: false, stream: null, overlay: null, overlayOn: false };

export function say(text) {
  document.getElementById("say").textContent = text || "";
}

// The fragment is #<tab>[/<selected node>|/-][/<lineage event>[/forward]]: fixed words and uuids only.
function readHash() {
  const [tab, sel, lin, dir] = location.hash.replace(/^#/, "").split("/");
  if (tab && !TAB_ORDER.includes(tab)) return;
  state.tab = tab || "overview";
  state.selected = sel && UUID.test(sel) ? sel.toLowerCase() : null;
  state.lineage = lin && UUID.test(lin) ? { id: lin.toLowerCase(), dir: dir === "forward" ? "forward" : "back" } : null;
}

function fragment() {
  let frag = `#${state.tab}`;
  if (state.selected || state.lineage) frag += `/${state.selected || "-"}`;
  if (state.lineage) frag += `/${state.lineage.id}${state.lineage.dir === "forward" ? "/forward" : ""}`;
  return frag;
}

function writeHash(replace = false) {
  const frag = fragment();
  if (frag === location.hash) return;
  if (replace) history.replaceState(null, "", frag); else history.pushState(null, "", frag);
}

/** Move to a tab, and optionally select a node there. */
export function go(tab, selected = undefined) {
  if (tab && TAB_ORDER.includes(tab)) state.tab = tab;
  if (selected !== undefined) state.selected = selected;
  writeHash();
  window.scrollTo({ top: 0, behavior: "instant" });
  return render();
}

/** Select a node in the current tab without leaving it. */
export function select(nodeId) {
  state.selected = nodeId;
  writeHash(true);
  render(false);
}

function ctx() {
  return {
    model: state.model, state, go, select, say, retry: reload,
    missing: (part) => !!(state.model && state.model.missing && state.model.missing.has(part)),
    fictional: state.overlay && state.overlayOn ? state.overlay : null,
    notLoaded: (part) => notLoaded(PARTS[part] ? PARTS[part][0].toUpperCase() + PARTS[part].slice(1) : "This part", reload),
    lineage: (eventId, label, dir = "back") => openLineage(ctxForDrawer(), eventId, label, dir),
  };
}

function ctxForDrawer() {
  return { ...ctx(), lineage: (eventId, label, dir = "back") => openLineage(ctxForDrawer(), eventId, label, dir) };
}

function initials(name) {
  return String(name || "").split(/[^A-Za-z0-9]+/).filter(Boolean).slice(0, 2).map((p) => p[0].toUpperCase()).join("") || "?";
}

function topbar() {
  const m = state.model;
  const fiction = fictionLabel(state.overlay, state.overlayOn);
  const search = h("input", {
    type: "search", placeholder: "Search this case", "aria-label": "search this case; the text never leaves this page",
    value: state.search, oninput: (e) => { state.search = e.target.value; applySearch(); },
  });
  clear(document.getElementById("topbar"),
    h("div", { class: "brand" }, h("div", { class: "brand-mark", "aria-hidden": "true" }, "P"), "PLAINSIGHT"),
    h("div", { class: "crumb" },
      h("span", { "aria-hidden": "true" }, "/"),
      h("b", { class: "mono" }, m ? showTitle(m.header.title).replace("PLAINSIGHT ", "") : "no case"),
      fiction && fiction.switches
        ? h("button", { class: ["pill", "fictional", !state.overlayOn && "off"], type: "button", title: state.overlay.note || "display only", onclick: toggleOverlay },
          h("b", {}, fiction.head), fiction.text)
      : fiction
        ? h("span", { class: ["pill", "fictional"], title: state.overlay.note || "display only" }, h("b", {}, fiction.head), fiction.text)
      : liveLook ? null
      : m && /^LOCAL/.test(m.header.environment || "") ? h("span", { class: "pill", title: m.header.environment }, h("b", {}, "SYNTHETIC"), h("span", { class: "pill-more" }, "corpus case, no live collection")) : null),
    h("label", { class: "search" }, h("span", { "aria-hidden": "true" }, "⌕"), search, kbd("/")),
    h("div", { class: "who" }, h("span", { class: "who-dot", "aria-hidden": "true" }, initials(m ? (liveLook ? "Analyst" : m.header.analyst) : "")), m ? m.header.analyst : ""),
    h("button", { class: "iconbtn", type: "button", title: "how to read this page, and the keys", "aria-label": "how to read this page", onclick: showKeys }, "Guide", kbd("?")));
}

function tabs() {
  const m = state.model;
  const count = {
    connections: m && m.web ? m.web.nodes.length : null,
    sources: m ? new Set([...m.events.values()].filter((e) => !liveLook || String(e.producer || "").startsWith("connector-")).map((e) => e.producer)).size : null,
    places: placeCount(m),
    assessment: m && m.dossier ? m.dossier.bands.find((b) => b.band === "STATE").rows.length : null,
    timeline: m ? (liveLook ? [...m.events.values()].filter((e) => e.type === "PROBE_EVENT" && e.subtype === "ITEM").length : m.events.size) : null,
  };
  const wrap = h("div", { class: "wrap", role: "tablist", "aria-label": "views of this case" },
    TAB_ORDER.map((t) => {
      const def = TABS[t];
      const n = count[t];
      return h("button", {
        class: ["tabbtn", n === 0 && "zero"], type: "button", role: "tab", "aria-selected": String(state.tab === t),
        title: `${def.view} · ${def.question}`, onclick: () => go(t, null),
      }, def.label, n !== null && n !== undefined ? h("span", { class: "count" }, `· ${n}`) : null, kbd(def.key));
    }));
  clear(document.getElementById("tabs"), wrap);
}

function applySearch() {
  const q = state.search.trim().toLowerCase();
  const pane = document.getElementById("tab");
  const all = [...pane.querySelectorAll("[data-search]")];
  let shown = 0;
  for (const node of all) {
    const hit = !q || node.dataset.search.toLowerCase().includes(q);
    node.classList.toggle("hidden-by-search", !hit);
    if (hit) shown += 1;
  }
  for (const fold of pane.querySelectorAll("details.fold")) {
    if (q && fold.querySelector("[data-search]:not(.hidden-by-search)")) fold.open = true;
  }
  const note = pane.querySelector("[data-search-note]");
  if (note) note.textContent = q ? `Search shows ${shown} of ${all.length}; ${all.length - shown} hidden by the search box, not removed.` : "";
  say(q ? `${shown} of ${all.length} shown` : "");
}

async function render(full = true) {
  const m = state.model;
  const page = document.getElementById("page");
  if (!m) return;
  if (full) {
    topbar();
    renderStatus(document.getElementById("statusbar"), ctx(), state.changed ? reload : null);
  }
  renderProfile(document.getElementById("profile"), ctx(), state.tab !== "overview");
  tabs();
  const pane = document.getElementById("tab");
  const keepScroll = !full ? window.scrollY : 0;
  clear(pane, h("div", { class: "wrap" }, h("div", { class: "loading" }, "Reading the case…")));
  const inner = h("div", { class: "wrap" });
  if (m.missing && m.missing.size) {
    const parts = [...m.missing].map((p) => PARTS[p] || p).join(", ");
    inner.append(notLoaded(`Part of this case (${parts})`, reload));
  }
  try {
    await RENDER[state.tab](inner, ctx());
  } catch (err) {
    inner.append(err && err.dropped
      ? notLoaded("This view", reload)
      : h("div", { class: "error" }, `This view could not be drawn: ${err.message}`));
  }
  clear(pane, inner);
  applySearch();
  page.setAttribute("aria-busy", "false");
  document.title = `${showTitle(m.header.title)} · ${TABS[state.tab].label}`;
  if (!full) window.scrollTo({ top: keepScroll, behavior: "instant" });
}

async function reload() {
  state.changed = false;
  say("Reading the case again…");
  try {
    state.model = await loadCase(state.caseId);
  } catch (err) {
    failedShell(err);
    return;
  }
  await render();
  say(state.model.missing.size ? "The case was read again; part of it still did not load." : "The case was read again from the store.");
}

/** The shell when even the case header did not arrive: the bar, the strip's place and one calm panel. */
function failedShell(err) {
  clear(document.getElementById("topbar"),
    h("div", { class: "brand" }, h("div", { class: "brand-mark", "aria-hidden": "true" }, "P"), "PLAINSIGHT"),
    h("div", { class: "crumb" }, h("span", { "aria-hidden": "true" }, "/"), h("b", { class: "mono" }, state.caseId ? `C-${short(state.caseId)}` : "")));
  clear(document.getElementById("statusbar"), h("span", { class: "label" }, "CASE STATUS"), h("span", { class: "faint" }, "not read yet"));
  clear(document.getElementById("profile"));
  clear(document.getElementById("tabs"));
  clear(document.getElementById("tab"), h("div", { class: "wrap" },
    err && err.dropped
      ? notLoaded("The case header", () => boot())
      : h("div", { class: "error" }, `The case could not be read: ${err ? err.message : "no answer"}`, " ", h("button", { class: "btn", type: "button", onclick: () => boot() }, "Retry"))));
  document.getElementById("page").setAttribute("aria-busy", "false");
}

function watch() {
  if (state.stream || typeof EventSource === "undefined" || hasCasePack()) return;
  const es = new EventSource(`/api/cases/${state.caseId}/notices`);
  // The server writes every frame as `event: notice` (app/http/notices.py), which onmessage never receives.
  es.addEventListener("notice", () => {
    if (state.changed) return;
    state.changed = true;
    renderStatus(document.getElementById("statusbar"), ctx(), reload);
    say("The case changed in the store. The view stays as it was until you refresh.");
  });
  es.onerror = () => {};
  state.stream = es;
}

function showKeys() {
  const pop = document.getElementById("popover");
  const source = sourceWords(state.overlay, state.overlayOn);
  const rows = TAB_ORDER.map((t) => h("div", { class: "row" }, kbd(TABS[t].key), h("div", { class: "grow" }, h("b", {}, TABS[t].label), ` · ${TABS[t].question}`, h("span", { class: "faint" }, ` · ${TABS[t].view}`))));
  clear(pop,
    h("button", { class: "iconbtn close", type: "button", "aria-label": "close", onclick: closePopover }, "esc"),
    h("h3", {}, "How to read this page"),
    h("p", {}, "PLAINSIGHT puts one person at the centre and gathers what every source returned around them, as a profile. Each tab answers one question. Every value opens its lineage with ⧉: the chain back through the item and the run to the gate's permission and the human authorization."),
    h("div", { class: "rows" }, rows),
    h("p", {}, h("b", {}, "One colour, one meaning. "), "Red with the hatch marks only what the system does not vouch for, with a word beside it saying why. Dashed means proposed and not accepted. Corner brackets mark an analyst's cluster. Struck through means revoked or excluded, and it stays on screen."),
    h("div", { class: "rows" },
      h("div", { class: "row" }, kbd("l"), h("div", { class: "grow" }, "Lineage of the selection: what it rests on")),
      h("div", { class: "row" }, kbd("L"), h("div", { class: "grow" }, "Forward lineage: what rests on the selection")),
      h("div", { class: "row" }, kbd("/"), h("div", { class: "grow" }, "Search this case; the text stays on this page and never reaches a URL")),
      h("div", { class: "row" }, kbd("?"), h("div", { class: "grow" }, "Open this guide")),
      h("div", { class: "row" }, kbd("esc"), h("div", { class: "grow" }, "Close the drawer or this panel"))),
    source.note ? h("p", {}, h("b", {}, source.note[0]), source.note[1]) : null,
    h("p", { class: "src" }, source.line));
  pop.hidden = false;
  pop.style.setProperty("right", "24px");
  pop.style.setProperty("top", "64px");
  pop.style.removeProperty("left");
}

function onKey(e) {
  const t = e.target;
  const typing = t instanceof HTMLInputElement || t instanceof HTMLTextAreaElement;
  if (e.key === "Escape") {
    if (lineageOpen()) { closeLineage(); return; }
    if (!document.getElementById("popover").hidden) { closePopover(); return; }
    if (typing) { t.blur(); return; }
    return;
  }
  if (typing || e.ctrlKey || e.metaKey || e.altKey) return;
  if (e.key === "/") { e.preventDefault(); document.querySelector(".search input").focus(); return; }
  if (e.key === "?") { showKeys(); return; }
  const tab = TAB_ORDER.find((x) => TABS[x].key === e.key);
  if (tab) { go(tab, null); return; }
  if (e.key === "l" || e.key === "L") {
    const m = state.model;
    const target = state.selected || m.focus;
    const node = m.nodes.get(target);
    const head = node && node.lineage_heads ? node.lineage_heads[0] : target;
    if (head) openLineage(ctxForDrawer(), head, node ? labelOf(node) : short(head), e.key === "L" ? "forward" : "back");
  }
}

function labelOf(node) {
  if (node.selector_type) return (node.lines || [])[1] || node.selector_type;
  return (node.lines || [])[0] || node.kind;
}

// A case pack is a whole case answered in the page: nothing stored stands behind it to switch to.
async function toggleOverlay() {
  if (!state.overlay || hasCasePack()) return;
  state.overlayOn = !state.overlayOn;
  setOverlay(state.overlayOn ? state.overlay.values : null);
  setLiveLook(state.overlayOn && state.overlay.presentation === "live");
  await reload();
  say(state.overlayOn ? "Showing the fictional person, drawn over the stored placeholders." : "Showing the stored values, the test corpus's placeholders.");
}

async function boot() {
  const parts = location.pathname.split("/").filter(Boolean);
  let caseId = parts[0] === "c" && UUID.test(parts[1] || "") ? parts[1].toLowerCase() : null;
  try {
    // The overlay loads first, so a case pack answers the case list too and no request reaches the store.
    if (!state.overlay) {
      const ov = await getJSON("/static/overlay.json");
      if (ov.ok && ov.body && ov.body.values) {
        state.overlay = ov.body;
        state.overlayOn = true;
        setOverlay(ov.body.values);
        setLiveLook(ov.body.presentation === "live");
        if (ov.body.case) setCasePack(ov.body.case);
      }
    }
    if (!caseId) {
      const list = await listCases();
      const held = list.cases.find((c) => c.held) || list.cases[0];
      if (!held) {
        clear(document.getElementById("tab"), h("div", { class: "wrap" }, h("div", { class: "loading" },
          "This store holds no case. On LOCAL a case comes only from the tracked synthetic corpus (EG-2).")));
        return;
      }
      caseId = held.case_id;
      history.replaceState(null, "", `/c/${caseId}/${list.landing_view}${location.hash}`);
    }
    state.caseId = caseId;
    readHash();
    clear(document.getElementById("tab"), h("div", { class: "wrap" }, h("div", { class: "loading" }, "Reading the case from the store…")));
    state.model = await loadCase(caseId);
    if (liveLook && state.model.header.analyst) setRenames([[state.model.header.analyst, "Analyst"]]);
  } catch (err) {
    failedShell(err);
    return;
  }
  const halt = state.model.header.halt;
  if (halt) document.getElementById("announce").textContent = halt;
  await render();
  if (state.lineage) syncDrawer();
  // The notice stream opens once the page has settled, so the first frame
  // never waits on a long-lived connection.
  setTimeout(watch, 15000);
}

onLineageChange((open) => {
  state.lineage = open ? { id: open.id, dir: open.dir } : null;
  writeHash(true);
});

function syncDrawer() {
  if (state.lineage && UUID.test(state.lineage.id)) openLineage(ctxForDrawer(), state.lineage.id, "", state.lineage.dir);
  else if (lineageOpen()) closeLineage();
}

window.addEventListener("popstate", async () => { readHash(); await render(false); syncDrawer(); });
window.dispatchEvent(new Event("plainsight:started"));
document.addEventListener("keydown", onKey);
document.getElementById("scrim").addEventListener("click", () => closeLineage());
document.querySelector(".skip").addEventListener("click", (e) => { e.preventDefault(); document.getElementById("tab").focus(); });
boot();

/** The case title as the page prints it: the live presentation drops a "(fictional)" suffix. */
function showTitle(title) {
  return liveLook ? String(title || "").replace(/\s*\(fictional\)/i, "") : title;
}

import { setRenames } from "./lib/dom.js";
