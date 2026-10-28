// PATHS (key 8) and the web's list twin (t). Both are the fallback past the
// canvas cap and the keyboard and screen-reader form of the web. A route is a
// chain of labelled predicates with its weakest link named in words; no number
// is computed.

import { el, getJSON, go } from "../app.js";

export async function renderPaths(pane, state) {
  if (!state.from || !state.to) {
    pane.replaceChildren(el("p", {}, "PATHS needs two marked nodes: select one and press v, then another and press v, then 8"));
    return;
  }
  const r = await getJSON(`/api/cases/${state.caseId}/paths?from=${state.from}&to=${state.to}`);
  if (!r.ok) { pane.replaceChildren(el("p", { class: "vouch" }, r.body ? r.body.text : "the routes could not be read")); return; }
  const d = r.body;
  const kids = [el("h2", {}, `PATHS · ${d.from.slice(0, 8)} to ${d.to.slice(0, 8)} · at most ${d.max_hops} hops`)];
  if (d.none) kids.push(el("p", {}, d.none));
  if (d.more) kids.push(el("p", {}, d.more));
  for (const route of d.routes) {
    kids.push(el("div", { class: "row", "data-row": "" },
      el("div", {}, route.nodes.map((n) => n.slice(0, 8)).join(" → ")),
      el("ul", {}, route.hops.map((h) => el("li", { class: h.layer === "inference" ? "inference-row" : "observation-row" },
        el("button", { onclick: () => go({ lineage: h.event_id, dir: "back" }) }, "l"), ` ${h.words}`))),
      el("div", { class: "consequence" }, route.weakest)));
  }
  pane.replaceChildren(...kids);
}

export async function renderList(pane, state) {
  if (!state.focus) { pane.replaceChildren(el("p", {}, "no focus: press esc esc to return to the seed")); return; }
  const qs = `focus=${state.focus}&hops=${state.hops}` + (state.sector ? `&sector=${state.sector}` : "");
  const r = await getJSON(`/api/cases/${state.caseId}/web.list?${qs}`);
  if (!r.ok) { pane.replaceChildren(el("p", { class: "vouch" }, r.body ? r.body.text : "the list could not be read")); return; }
  const d = r.body;
  const kids = [el("h2", {}, `LIST TWIN · focus ${d.focus.slice(0, 8)} · hops ${d.hops}`)];
  kids.push(el("h3", {}, "NODES"));
  for (const n of d.nodes) {
    kids.push(el("div", { class: "row", "data-row": "", "data-node": n.node_id },
      `ring ${n.ring} · ${n.kind} · ${n.node_id.slice(0, 8)} · `,
      ...n.lines.map((l, i) => el("span", { class: (n.generated && i === 1 ? "generated " : "") + (n.revoked || n.kind === "candidate" ? "struck" : "") }, `${l} `)),
      ...n.vouch_tokens.map((t) => el("span", { class: "vouch" }, `${t} `)),
      el("span", {}, n.deep_dive_state)));
  }
  kids.push(el("h3", {}, "EDGES"));
  for (const e of d.edges) {
    kids.push(el("div", { class: `row ${e.layer === "inference" ? "inference-row" : e.layer === "fusion" ? "fusion-row" : "observation-row"}`, "data-row": "" },
      el("button", { onclick: () => go({ lineage: e.event_id, dir: "back" }) }, "l"),
      ` ${e.src_id.slice(0, 8)} → ${e.dst_id.slice(0, 8)} · ${e.text}`));
  }
  pane.replaceChildren(...kids);
}
