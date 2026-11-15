// COLLECTION (key 5), read-only: the connectors this checkout carries and the
// health records this case holds, joined and labelled by source. Every present
// state is UNVERIFIED, and a recorded state is a dated record, never the present
// one; the server writes each line and this view prints it. Red and the hatch
// come from the server's flags. No number is computed here.

import { el, getJSON, go } from "../app.js";

function record(rec) {
  return el("div", { class: "row", "data-row": "" },
    el("button", { onclick: () => go({ lineage: rec.event_id, dir: "back" }) }, "l"), " ",
    el("span", { class: rec.vouch ? "vouch" : "" }, rec.text));
}

export async function renderCollection(pane, state) {
  const r = await getJSON(`/api/cases/${state.caseId}/collection`);
  if (!r.ok) { pane.replaceChildren(el("p", { class: "vouch" }, r.body ? r.body.text : "the COLLECTION board could not be read")); return; }
  const d = r.body;
  const kids = [
    el("h2", {}, `COLLECTION · ${d.summary}`),
    el("div", {}, d.scope),
    ...d.capabilities.map((c) => el("div", { class: c.vouch ? "vouch" : "" }, c.text)),
  ];
  if (d.set_aside) kids.push(el("div", { class: "vouch" }, d.set_aside));
  kids.push(el("h3", { class: "band" }, "CONNECTORS THIS CHECKOUT CARRIES"));
  if (!d.connectors.length) kids.push(el("div", {}, d.connectors_empty));
  for (const c of d.connectors) {
    kids.push(el("div", { class: "card" },
      el("div", { class: "row", "data-row": "" }, c.title),
      el("div", { class: c.state_vouch ? "vouch" : "" }, c.state),
      ...c.lines.map((line) => el("div", {}, line)),
      ...c.records.map(record)));
  }
  kids.push(el("h3", { class: "band" }, d.unmatched_heading));
  if (!d.unmatched.length) kids.push(el("div", {}, d.unmatched_empty));
  for (const rec of d.unmatched) kids.push(el("div", { class: "card" }, el("div", {}, `${rec.connector_id} · probe unit ${rec.probe_unit}`), record(rec)));
  pane.replaceChildren(...kids);
}
