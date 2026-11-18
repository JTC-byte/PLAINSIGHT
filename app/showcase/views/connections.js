// Connections, the WEB as a social graph around one person (design amendment
// 9.7, the 11-02 idiom). The seed sits at the centre. Each ring is a hop. The
// layout is deterministic and radial: ring-one nodes take the sector order of
// app/model/sectors.py clockwise from the top, each with an arc sized by how
// many nodes hang behind it, so a label never sits on a label. No force
// simulation, no weight, no size by importance: every card is the same width.
// Lines are grouped by pair, and each pair carries one label in words; the
// side panel prints every link's own sentence. Selecting collects nothing.

import { h, s, clear, tok, lin, silhouette } from "../lib/dom.js";
import { need, liveLook } from "../lib/api.js";
import { selectorChip, selectorLabel, SECTOR_LABEL, SEAMS, SEAM_SHORT, stamp, short, plural } from "../lib/words.js";
import { commonTokens } from "../lib/model.js";

const SLOTS = ["accounts", "names_aliases", "emails", "phones", "addresses", "organizations", "people", "other_osint", null];
const CARD_W = 220;
const CARD_H = 58;

function slotOf(n) {
  const i = SLOTS.indexOf(n.sector === undefined ? null : n.sector);
  return i < 0 ? SLOTS.length - 1 : i;
}

function orderKey(n) {
  return `${String(slotOf(n)).padStart(2, "0")} ${n.selector_type || n.entity_type || n.kind || ""} ${n.node_id}`;
}

function pairKey(a, b) {
  return a < b ? `${a}|${b}` : `${b}|${a}`;
}

/** The node's card text: a title, a sub-line, and whether the sub-line is the server's not-vouched flag. */
function cardText(n, common) {
  const own = liveLook ? [] : (n.vouch_tokens || []).filter((t) => !common.includes(t));
  if (n.kind === "selector") {
    return { glyph: selectorChip(n.selector_type), title: (n.lines || [])[1] || n.selector_type, mono: true, generated: n.generated,
      sub: selectorLabel(n.selector_type) + (own.length ? ` · ${own.join(" · ")}` : ""), subVouch: own.length > 0 };
  }
  if (n.kind === "cluster") {
    const band = ((n.lines || [])[0] || "").split(" · ")[1] || "";
    return { glyph: "⌐", title: `Cluster ${short(n.node_id)}`, struck: n.revoked,
      sub: n.revoked ? "revoked: no longer stands" : `asserted · ${band}`, subVouch: false };
  }
  if (n.kind === "candidate") {
    const excl = (n.lines || []).some((l) => l.startsWith("EXCLUDED"));
    return { glyph: "person", title: "Candidate person", struck: excl, sub: excl ? "excluded: not the subject" : "candidate", subVouch: false };
  }
  if (n.kind === "referenced") return { glyph: "person", title: "Referenced person", sub: "named by a cluster or proposal · no observation held", subVouch: false };
  if (n.kind === "entity") return { glyph: selectorChip(n.entity_type || "en"), title: (n.lines || [])[0] || n.entity_type, sub: (n.lines || [])[1] || "", subVouch: own.length > 0 };
  return { glyph: "··", title: (n.lines || [])[0] || n.kind, sub: n.kind, subVouch: false };
}

function edgeClass(e) {
  if (e.kind === "proposes") return "inf";
  if (e.layer === "fusion" || e.kind === "member_of" || e.kind === "excludes") return "fus";
  return "obs";
}

function gone(e) {
  return !!e.withdrawn || /revoked|withdrawn/i.test(e.text || "");
}

function groupLabel(list) {
  const kinds = new Set(list.map((e) => e.kind));
  if (kinds.size === 1 && kinds.has("proposes")) {
    return list.length > 1 ? `${list.length} proposals, not accepted` : `proposed ${String(list[0].label).replaceAll("_", " ")}, not accepted`;
  }
  const e = list[0];
  if (e.kind === "member_of") return `member · ${String(e.label).split(",").map((c) => SEAM_SHORT[c.trim()] || `seam ${c.trim()}`).join(", ")}${gone(e) ? " · revoked" : ""}`;
  if (e.kind === "excludes") return "excluded: not the subject";
  if (e.kind === "observed_about") return `observed about · ${selectorLabel(e.label).toLowerCase()}`;
  return list.length > 1 ? `${list.length} links` : String(e.label || e.kind).replaceAll("_", " ");
}

/** Deterministic radial placement. Ring one sits on an ellipse, in sector
 * order clockwise from the top, each node's arc sized by the nodes behind it.
 * A node further out sits beside its parent, away from the centre: radially
 * first, then to either side, so its link is short and its label has room. */
function layout(nodes, edges, focus, w, hgt) {
  const cx = w / 2;
  const cy = hgt / 2;
  const TOP = 8;
  const BOTTOM = 10;
  const byId = new Map(nodes.map((n) => [n.node_id, n]));
  const adj = new Map(nodes.map((n) => [n.node_id, new Set()]));
  for (const e of edges) {
    if (adj.has(e.src_id) && adj.has(e.dst_id)) { adj.get(e.src_id).add(e.dst_id); adj.get(e.dst_id).add(e.src_id); }
  }
  const rings = new Map();
  for (const n of nodes) {
    if (n.node_id === focus) continue;
    const r = n.ring || 1;
    if (!rings.has(r)) rings.set(r, []);
    rings.get(r).push(n);
  }
  for (const list of rings.values()) list.sort((a, b) => orderKey(a).localeCompare(orderKey(b)));
  // A node in no sector (a cluster) sits beside the latest ring-one node it links to, so a
  // container is drawn next to what it holds and its line does not cross the web.
  const sorted = (rings.get(1) || []).filter((n) => n.sector);
  for (const n of (rings.get(1) || []).filter((x) => !x.sector)) {
    let at = -1;
    sorted.forEach((q, i) => { if (adj.get(n.node_id).has(q.node_id)) at = i; });
    if (at < 0) sorted.push(n); else sorted.splice(at + 1, 0, n);
  }
  rings.set(1, sorted);
  const ring1 = sorted;
  const maxRing = Math.max(1, ...rings.keys());
  const parent = new Map();
  for (let r = 2; r <= maxRing; r += 1) {
    const inner = rings.get(r - 1) || [];
    for (const n of rings.get(r) || []) {
      const p = inner.find((q) => adj.get(n.node_id).has(q.node_id)) || inner[0];
      if (p) parent.set(n.node_id, p.node_id);
    }
  }
  const kids = new Map();
  for (const [c, p] of parent) { if (!kids.has(p)) kids.set(p, []); kids.get(p).push(c); }
  const weight = (id) => 1 + (kids.get(id) || []).reduce((acc, k) => acc + weight(k), 0);
  const total = ring1.reduce((acc, n) => acc + weight(n.node_id), 0) || 1;
  const pos = new Map([[focus, { x: cx, y: cy, a: 0 }]]);
  const frac = maxRing === 1 ? 0.84 : 0.74;
  const rx1 = (w / 2 - CARD_W / 2 - 14) * frac;
  const ry1 = (hgt / 2 - CARD_H / 2 - TOP) * frac;
  const first = ring1.length ? weight(ring1[0].node_id) : 1;
  let a0 = -Math.PI / 2 - (Math.PI * first) / total;
  for (const n of ring1) {
    const sw = (2 * Math.PI * weight(n.node_id)) / total;
    const a = a0 + sw / 2;
    pos.set(n.node_id, { x: cx + rx1 * Math.cos(a), y: cy + ry1 * Math.sin(a), a });
    a0 += sw;
  }
  const placed = [];
  const centreHit = (p) => Math.abs(p.x - cx) < 70 + CARD_W / 2 && Math.abs(p.y - cy) < 70 + CARD_H / 2;
  const hits = (p) => placed.some((q) => Math.abs(q.x - p.x) < CARD_W + 10 && Math.abs(q.y - p.y) < CARD_H + 10) || centreHit(p);
  const inside = (p) => p.x >= CARD_W / 2 + 8 && p.x <= w - CARD_W / 2 - 8 && p.y >= CARD_H / 2 + TOP && p.y <= hgt - CARD_H / 2 - BOTTOM;
  const clamp = (p) => {
    p.x = Math.max(CARD_W / 2 + 8, Math.min(w - CARD_W / 2 - 8, p.x));
    p.y = Math.max(CARD_H / 2 + TOP, Math.min(hgt - CARD_H / 2 - BOTTOM, p.y));
    return p;
  };
  for (const n of ring1) {
    const p = pos.get(n.node_id);
    for (let step = 0; step < 30 && hits(p); step += 1) { p.x += Math.cos(p.a) * 8; p.y += Math.sin(p.a) * 6; }
    placed.push(clamp(p));
  }
  for (let r = 2; r <= maxRing; r += 1) {
    for (const n of rings.get(r) || []) {
      const p = pos.get(parent.get(n.node_id)) || { x: cx, y: cy - 1, a: -Math.PI / 2 };
      const base = Math.atan2(p.y - cy, p.x - cx);
      const dirs = [base, base + Math.PI / 2, base - Math.PI / 2, base + Math.PI / 4, base - Math.PI / 4, base + (3 * Math.PI) / 4, base - (3 * Math.PI) / 4];
      let chosen = null;
      for (let lap = 0; lap < 3 && !chosen; lap += 1) {
        for (const a of dirs) {
          const d = Math.min((CARD_W + 44) / Math.max(1e-6, Math.abs(Math.cos(a))), (CARD_H + 26) / Math.max(1e-6, Math.abs(Math.sin(a)))) + lap * 40;
          const c = { x: p.x + d * Math.cos(a), y: p.y + d * Math.sin(a), a };
          if (inside(c) && !hits(c)) { chosen = c; break; }
        }
      }
      if (!chosen) {
        chosen = clamp({ x: p.x + (CARD_H + 30) * Math.cos(base), y: p.y + (CARD_H + 30) * Math.sin(base), a: base });
      }
      pos.set(n.node_id, chosen);
      placed.push(chosen);
    }
  }
  const radii = new Map([[1, [rx1, ry1]]]);
  return { pos, radii };
}

function nodePanel(ctx, n, web) {
  const m = ctx.model;
  const d = n.inspect;
  const t = cardText(n, []);
  const head = h("div", { class: "mini-h" },
    n.node_id === m.focus ? h("span", { class: "glyph" }, silhouette(30)) : h("span", { class: "type" }, t.glyph === "person" ? "pp" : t.glyph),
    h("span", { class: ["t", t.mono && "mono", t.struck && "struck", t.generated && "generated"] }, n.node_id === m.focus ? "The seed account" : t.title),
    lin(() => ctx.lineage((n.lineage_heads || [])[0] || n.node_id, t.title), t.title));
  const kids = [
    h("div", { class: "card-h" }, h("h2", {}, "Selected"), h("span", { class: "right" }, d ? d.sector_label : (n.sector ? SECTOR_LABEL[n.sector] : "no sector"))),
    h("div", { class: "card-b" },
      h("div", { class: ["mini", n.kind === "cluster" ? "layer-fus" : "layer-obs"] }, head,
        h("div", { class: "mini-b" }, (n.lines || []).map((l) => h("div", {}, l))),
        (n.vouch_tokens || []).length && !liveLook ? h("div", { class: "tokens" }, n.vouch_tokens.map((x) => tok(x, true))) : null),
      h("p", { class: "faint" }, n.deep_dive_state || "inert · nothing has been collected against this node")),
  ];
  if (d && d.claims && d.claims.length) {
    kids.push(h("div", { class: "card-b" }, h("div", { class: "tier" }, "CLAIMS HELD"),
      h("div", { class: "rows" }, d.claims.map((c) => h("div", { class: "row" },
        h("div", { class: "grow" },
          h("div", {}, h("b", {}, selectorLabel(c.selector_type)), " ", h("span", { class: ["mono", c.generated && "generated"] }, c.value)),
          h("div", { class: "faint" }, c.review),
          h("div", { class: "faint" }, c.relation),
          h("div", { class: "tokens" }, tok(c.raw), tok(c.expiry))),
        lin(() => ctx.lineage(c.claim_id, c.value), c.value))))));
  }
  if (d && d.edges && d.edges.length) {
    kids.push(h("div", { class: "card-b" }, h("div", { class: "tier" }, `LINKS · ${d.edges.length}`),
      h("div", { class: "rows" }, d.edges.map((e) => h("div", { class: "row" },
        h("div", { class: "grow" }, h("div", {}, e.text), h("div", { class: "faint" }, `${e.actor} · ${stamp(e.ts)}`)),
        lin(() => ctx.lineage(e.event_id, e.label), e.label))))));
  }
  if (d && d.adjudications && d.adjudications.length) {
    kids.push(h("div", { class: "card-b" }, h("div", { class: "tier" }, `ADJUDICATIONS · ${d.adjudications.length}`),
      h("div", { class: "rows" }, d.adjudications.map((a) => h("div", { class: "row" }, h("div", { class: "grow" }, a.text), lin(() => ctx.lineage(a.event_id, a.subtype), a.subtype))))));
  }
  if (d && d.unattached_decisions && d.unattached_decisions.length) {
    kids.push(h("div", { class: "card-b" }, h("div", { class: "tier" }, "GATE DECISIONS NOT ON A RUN"),
      h("div", { class: "rows" }, d.unattached_decisions.map((u) => h("div", { class: "row" }, h("div", { class: "grow" }, u.text), lin(() => ctx.lineage(u.event_id, "decision"), "this decision"))))));
  }
  if (d && d.pivot) {
    kids.push(h("div", { class: "card-b" }, h("div", { class: "tier" }, "DEEP DIVE PRE-FLIGHT · RECORDS NOTHING"),
      h("div", { class: "rows" }, d.pivot.lines.map((l) => h("div", { class: "note-line" }, l)))));
  }
  return kids;
}

function edgePanel(ctx, list, web) {
  const m = ctx.model;
  const byId = new Map(web.nodes.map((n) => [n.node_id, n]));
  const name = (id) => id === m.focus ? "the seed account" : cardText(byId.get(id) || { kind: "?" }, []).title;
  const e0 = list[0];
  return [
    h("div", { class: "card-h" }, h("h2", {}, "Selected link"), h("span", { class: "right" }, plural(list.length, "event"))),
    h("div", { class: "card-b" },
      h("p", { class: "muted" }, `Between ${name(e0.src_id)} and ${name(e0.dst_id)}. Each line below is one event in the log, in the server's words.`),
      h("div", { class: "rows" }, list.map((e) => h("div", { class: ["row", e.kind === "proposes" ? "layer-inf" : ""] },
        h("div", { class: "grow" }, h("div", {}, e.text), h("div", { class: "faint" }, `${e.kind.replaceAll("_", " ")} · ${e.layer} · ${e.actor} · ${stamp(e.ts)}`)),
        lin(() => ctx.lineage(e.event_id, e.label), e.label))))),
  ];
}

function overview(ctx, web, common) {
  const counts = new Map([["the seed", 0]]);
  for (const n of web.nodes) {
    const key = n.node_id === ctx.model.focus ? "the seed" : n.kind === "cluster" ? "identity clusters" : (SECTOR_LABEL[n.sector] || n.kind).toLowerCase();
    counts.set(key, (counts.get(key) || 0) + 1);
  }
  return [
    h("div", { class: "card-h" }, h("h2", {}, "Nothing selected")),
    h("div", { class: "card-b" },
      h("p", { class: "muted" }, "Select a person, an account, a selector or a line. Selecting reads what the store already holds and collects nothing."),
      h("dl", { class: "kv" }, [...counts.entries()].map(([k, v]) => [h("dt", {}, k), h("dd", {}, String(v))]).flat(),
        h("dt", {}, "links"), h("dd", {}, String(web.edges.length))),
      common.length && !liveLook ? h("div", { class: "tokens" }, h("span", { class: "faint" }, "Every node:"), common.map((t) => tok(t, true))) : null),
    h("div", { class: "card-foot" }, "A deep dive takes one node and one motivating claim per act, and the subject gate is not connected to this route, so none can start here (amendment 9.11)."),
  ];
}

function listTwin(ctx, web) {
  const m = ctx.model;
  const byId = new Map(web.nodes.map((n) => [n.node_id, n]));
  const name = (id) => id === m.focus ? "the seed account" : cardText(byId.get(id) || { kind: "?" }, []).title;
  return h("div", { class: "card" },
    h("div", { class: "card-h" }, h("h2", {}, "The web as a list"), h("span", { class: "sub" }, "the same nodes and links, for reading and for screen readers")),
    h("table", { class: "listtwin" },
      h("thead", {}, h("tr", {}, h("th", {}, "Node"), h("th", {}, "Kind"), h("th", {}, "Hop"), h("th", {}, "What the server says"), h("th", {}, ""))),
      h("tbody", {}, web.nodes.map((n) => h("tr", {},
        h("td", { class: n.kind === "selector" ? "mono" : "" }, n.node_id === m.focus ? "the seed account" : cardText(n, []).title),
        h("td", {}, n.kind), h("td", {}, String(n.ring)), h("td", {}, (n.lines || []).join(" · ")),
        h("td", {}, lin(() => ctx.lineage((n.lineage_heads || [])[0], n.kind), n.kind)))))),
    h("table", { class: "listtwin" },
      h("thead", {}, h("tr", {}, h("th", {}, "From"), h("th", {}, "Link"), h("th", {}, "To"), h("th", {}, "Layer"), h("th", {}, ""))),
      h("tbody", {}, web.edges.map((e) => h("tr", {},
        h("td", {}, name(e.src_id)), h("td", {}, e.text), h("td", {}, name(e.dst_id)), h("td", {}, e.layer),
        h("td", {}, lin(() => ctx.lineage(e.event_id, e.label), e.label)))))));
}

export async function renderConnections(el, ctx) {
  const m = ctx.model;
  const st = ctx.state;
  st.hops = st.hops || 3;
  st.webView = st.webView || "web";
  if (!m.focus) { el.append(h("div", { class: "loading" }, "This case has no seed, so there is no web to draw.")); return; }
  if (ctx.missing("web") && st.hops === 3) { el.append(h("div", { class: "section-title" }, h("h2", {}, "Who and what is this account connected to?")), ctx.notLoaded("web")); return; }
  let web = st.hops === 3 && m.web ? m.web : await need(`${m.base}/web?focus=${m.focus}&hops=${st.hops}`);
  const title = h("div", { class: "section-title" },
    h("h2", {}, "Who and what is this account connected to?"),
    h("span", { class: "sub" }, web.mode === "web" ? `${plural(web.nodes.length, "node")} · ${plural(web.edges.length, "link")} within ${plural(st.hops, "hop")}` : ""));
  const hopsSeg = h("div", { class: "seg", role: "group", "aria-label": "display depth" }, [1, 2, 3].map((n) =>
    h("button", { type: "button", "aria-pressed": String(st.hops === n), onclick: () => { st.hops = n; ctx.select(st.selected); } }, `${n} ${n === 1 ? "hop" : "hops"}`)));
  const viewSeg = h("div", { class: "seg", role: "group", "aria-label": "web or list" }, ["web", "list"].map((v) =>
    h("button", { type: "button", "aria-pressed": String(st.webView === v), onclick: () => { st.webView = v; ctx.select(st.selected); } }, v === "web" ? "Web" : "List")));
  const all = m.web ? m.web.nodes.length : null;
  const hidden = all !== null && web.mode === "web" ? all - web.nodes.length : 0;
  const depthLine = st.hops === 3 ? "display depth 3, the most this route draws" : hidden > 0 ? `display depth ${st.hops} · ${plural(hidden, "more node")} within 3 hops hidden, not removed` : `display depth ${st.hops} · nothing more within 3 hops`;
  const tools = h("div", { class: "web-tools" }, hopsSeg, h("span", { class: "faint" }, `${depthLine} · display depth, not authorization depth`), h("span", { css: { flex: "1 1 auto" } }), viewSeg);
  if (web.mode !== "web") {
    el.append(title, tools, h("div", { class: "flag" }, web.cap || "Over the canvas cap: the server draws no web and serves the list."));
    return;
  }
  if (st.webView === "list") { el.append(title, tools, listTwin(ctx, web)); return; }

  const common = commonTokens({ nodes: new Map(web.nodes.map((n) => [n.node_id, n])) });
  const nodes = web.nodes.map((n) => ({ ...n, inspect: (m.nodes.get(n.node_id) || {}).inspect || null }));
  const byId = new Map(nodes.map((n) => [n.node_id, n]));
  const groups = new Map();
  for (const e of web.edges) {
    const k = pairKey(e.src_id, e.dst_id);
    if (!groups.has(k)) groups.set(k, []);
    groups.get(k).push(e);
  }
  const selEdge = st.selectedEdge && groups.has(st.selectedEdge) ? st.selectedEdge : null;
  const selNode = st.selected && byId.has(st.selected) ? st.selected : null;
  const touching = (k) => selNode && k.split("|").includes(selNode);

  const svgEl = s("svg", { class: "edges", "aria-hidden": "true" });
  const stage = h("div", { class: "stage", role: "group", "aria-label": `the web around the seed, ${web.nodes.length} nodes; the list view carries the same content as text` });
  stage.append(svgEl);
  const cards = new Map();
  for (const n of nodes) {
    if (n.node_id === m.focus) {
      const b = h("button", { class: "focusnode", type: "button", "aria-pressed": String(selNode === n.node_id), onclick: () => { st.selectedEdge = null; ctx.select(n.node_id); } },
        h("span", { class: "ph" }, silhouette(116)),
        h("span", { class: "sr" }, "the seed account"));
      cards.set(n.node_id, b);
      stage.append(b);
      continue;
    }
    const t = cardText(n, common);
    const b = h("button", {
      class: ["wnode", n.kind === "cluster" ? "layer-fus" : "layer-obs", selNode && selNode !== n.node_id && !groupsTouch(groups, selNode, n.node_id) ? "dim" : null],
      type: "button", "aria-pressed": String(selNode === n.node_id), title: (n.lines || []).join(" · "),
      onclick: () => { st.selectedEdge = null; ctx.select(n.node_id); },
    },
    t.glyph === "person" ? h("span", { class: "glyph" }, silhouette(30, "a person; no image is held")) : h("span", { class: "type", "aria-hidden": "true" }, t.glyph),
    h("span", { class: "nb" },
      h("span", { class: ["nv", !t.mono && "sans", t.struck && "struck", t.generated && "generated"] }, t.title),
      h("span", { class: ["nt", t.subVouch && "novouch"] }, t.sub)));
    cards.set(n.node_id, b);
    stage.append(b);
  }
  const labels = new Map();
  for (const [k, list] of groups) {
    const cls = edgeClass(list[0]);
    const b = h("button", {
      class: ["elabel", cls === "inf" && "inf", list.every(gone) && "gone"], type: "button", "aria-pressed": String(selEdge === k),
      onclick: () => { st.selectedEdge = k; ctx.select(null); },
    }, groupLabel(list));
    labels.set(k, b);
    stage.append(b);
  }
  const caption = h("div", { class: "web-caption" },
    common.length && !liveLook ? h("span", { class: "tokens" }, h("span", {}, "Every node:"), common.map((t) => tok(t, true))) : null,
    h("span", {}, `Showing links already held between these ${web.nodes.length} nodes; nothing was collected to draw them. Size, position and distance say nothing about any person, and no line carries a weight.`));

  const panel = h("aside", { class: "card panel", "aria-label": "selection" });
  if (selNode) clear(panel, ...nodePanel(ctx, byId.get(selNode), web));
  else if (selEdge) clear(panel, ...edgePanel(ctx, groups.get(selEdge), web));
  else clear(panel, ...overview(ctx, web, common));

  // The key to the lines sits above the stage, so it is on screen with the web at first sight.
  const legend = h("div", { class: "legend top", role: "note", "aria-label": "how to read the lines" },
    h("span", {}, h("i", { class: "swatch" }), "observed: a claim recorded about the node"),
    h("span", {}, h("i", { class: "swatch inf" }), "dashed: proposed by a matcher, not accepted"),
    h("span", {}, h("i", { class: "swatch fus" }), "an analyst's assertion: cluster membership or exclusion"),
    h("span", {}, h("i", { class: "swatch gone" }), "revoked: the tombstone stays, struck"),
    h("span", {}, "corner brackets: a cluster, a container of accounts"));

  el.append(title, tools, h("div", { class: "web-layout" }, h("div", {}, legend, stage, caption), panel));

  const draw = () => {
    const w = stage.clientWidth;
    const hh = stage.clientHeight;
    if (!w || !hh) return;
    const { pos, radii } = layout(nodes, web.edges, m.focus, w, hh);
    for (const [id, b] of cards) {
      const p = pos.get(id);
      if (!p) continue;
      b.style.setProperty("left", `${p.x}px`);
      b.style.setProperty("top", `${p.y}px`);
    }
    clear(svgEl);
    svgEl.setAttribute("viewBox", `0 0 ${w} ${hh}`);
    for (const [ex, ey] of radii.values()) svgEl.append(s("ellipse", { class: "ring", cx: w / 2, cy: hh / 2, rx: ex, ry: ey }));
    const boxes = [];
    for (const [id, b] of cards) {
      const p = pos.get(id);
      if (!p) continue;
      const bw = id === m.focus ? 132 : CARD_W;
      const bh = id === m.focus ? 132 : CARD_H;
      boxes.push({ x: p.x - bw / 2, y: p.y - bh / 2, w: bw, h: bh });
    }
    const overlap = (r, q) => r.x < q.x + q.w && q.x < r.x + r.w && r.y < q.y + q.h && q.y < r.y + r.h;
    const keys = [...groups.keys()].sort();
    for (const k of keys) {
      const list = groups.get(k);
      const [a, b] = k.split("|");
      const pa = pos.get(a);
      const pb = pos.get(b);
      if (!pa || !pb) { labels.get(k).hidden = true; continue; }
      const cls = edgeClass(list[0]);
      const dead = list.every(gone);
      const on = selEdge === k || touching(k);
      const dim = (selNode || selEdge) && !on;
      svgEl.append(s("line", { class: ["e", cls, dead && "gone", on && "sel", dim && "dim"].filter(Boolean).join(" "), x1: pa.x, y1: pa.y, x2: pb.x, y2: pb.y }));
      const lab = labels.get(k);
      const lw = lab.offsetWidth || 120;
      const lh = lab.offsetHeight || 20;
      const fromCentre = (pa.x === w / 2 && pa.y === hh / 2) || (pb.x === w / 2 && pb.y === hh / 2);
      const inner = Math.hypot(pa.x - w / 2, pa.y - hh / 2) <= Math.hypot(pb.x - w / 2, pb.y - hh / 2) ? pa : pb;
      const outer = inner === pa ? pb : pa;
      const tries = fromCentre ? [0.6, 0.68, 0.52, 0.76, 0.46] : [0.5, 0.42, 0.58, 0.34, 0.66, 0.28, 0.72];
      const shifts = [[0, 0], [0, -(lh + 10)], [0, lh + 10], [0, -(2 * lh + 16)], [0, 2 * lh + 16]];
      let best = null;
      for (const [sx, sy] of shifts) {
        for (const f of tries) {
          const lx = inner.x + (outer.x - inner.x) * f + sx;
          const ly = inner.y + (outer.y - inner.y) * f + sy;
          const r = { x: lx - lw / 2 - 5, y: ly - lh / 2 - 5, w: lw + 10, h: lh + 10 };
          if (!boxes.some((q) => overlap(r, q))) { best = { lx, ly, r }; break; }
          if (!best) best = { lx, ly, r, fallback: true };
        }
        if (best && !best.fallback) break;
      }
      boxes.push(best.r);
      lab.style.setProperty("left", `${best.lx}px`);
      lab.style.setProperty("top", `${best.ly}px`);
      lab.classList.toggle("dim", !!dim);
    }
  };
  const ro = new ResizeObserver(() => draw());
  ro.observe(stage);
  requestAnimationFrame(draw);
}

function groupsTouch(groups, a, b) {
  return groups.has(pairKey(a, b));
}
