// WEB (key 7): the server-rendered SVG, inserted as-is. The server escapes every
// text node and writes no script and no URL into the SVG, so the client parses
// it and adopts the nodes. Over the canvas cap the server draws no SVG; this view
// then shows the cap sentence and the list twin. Selecting a node collects nothing.

import { el, getJSON, go } from "../app.js";
import { renderList } from "./paths.js";

export async function renderWeb(pane, state) {
  if (!state.focus) { pane.replaceChildren(el("p", {}, "no focus: press esc esc to return to the seed")); return; }
  const qs = `focus=${state.focus}&hops=${state.hops}` + (state.sector ? `&sector=${state.sector}` : "");
  const r = await fetch(`/api/cases/${state.caseId}/web.svg?${qs}`, { credentials: "same-origin", cache: "no-store" });
  if (r.status === 409) {
    const body = await r.json().catch(() => null);
    pane.replaceChildren(el("p", { class: "vouch" }, body && body.detail ? body.detail : "over the canvas cap"));
    const list = el("div");
    pane.append(list);
    await renderList(list, state);
    return;
  }
  if (!r.ok) {
    const body = await r.json().catch(() => null);
    pane.replaceChildren(el("p", { class: "vouch" }, body ? body.text : "the web could not be drawn"));
    return;
  }
  const text = await r.text();
  const doc = new DOMParser().parseFromString(text, "image/svg+xml");
  const svg = doc.documentElement;
  if (svg.nodeName !== "svg") { pane.replaceChildren(el("p", { class: "vouch" }, "the web could not be parsed")); return; }
  const head = el("div", {}, `WEB · focus ${state.focus.slice(0, 8)} · hops ${state.hops} · + and - change hops, t the list twin, f refocus`);
  const sectors = await getJSON(`/api/cases/${state.caseId}/web?${qs}`);
  const cards = sectors.ok && sectors.body.collapsed ? sectors.body.collapsed.map((c) =>
    el("button", { onclick: () => go({ sector: c.sector }) }, c.text)) : [];
  pane.replaceChildren(head, ...cards, document.importNode(svg, true));
  const focus = pane.querySelector("svg.web .node.focus");
  if (focus) {
    const f = focus.getBoundingClientRect();
    const p = pane.getBoundingClientRect();
    pane.scrollLeft += f.left - p.left - (pane.clientWidth - f.width) / 2;
    pane.scrollTop += f.top - p.top - (pane.clientHeight - f.height) / 2;
  }
}

export function webNodes(kind) {
  const nodes = [...document.querySelectorAll("#view svg.web [data-node]")];
  nodes.sort((a, b) => Number(a.dataset.order) - Number(b.dataset.order));
  return nodes.filter((n) => !kind || n.dataset.kind === kind).map((n) => n.dataset.node);
}

export function markSelected(nodeId) {
  for (const g of document.querySelectorAll("#view svg.web [data-node]")) {
    g.classList.toggle("selected", g.dataset.node === nodeId);
  }
}
