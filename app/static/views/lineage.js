// The Lineage Drawer: full width, 40vh, three tiers. CHAIN walks back through
// claim, item, RUN_START, COLLECT PERMITTED and the authorization's acts. A
// missing link reads "chain broken at <event_id>" and is never skipped. Flags
// render as consequences and never refuse. ENVELOPE is the decoded event. RAW
// reads "not held" on LOCAL, and is red only when the server's raw_vouch says
// the system does not vouch for it. Shift+L reads the same table forward.

import { el, getJSON, go } from "../app.js";

export async function renderLineage(pane, state) {
  const dir = state.dir === "forward" ? "forward" : "back";
  const r = await getJSON(`/api/cases/${state.caseId}/lineage/${state.lineage}?dir=${dir}`);
  const close = el("button", { onclick: () => go({ lineage: null }) }, "esc close");
  if (!r.ok) { pane.replaceChildren(close, el("p", { class: "vouch" }, r.body ? r.body.text : "the chain could not be read")); return; }
  const d = r.body;
  const title = dir === "forward" ? "FORWARD LINEAGE · what depends on this event" : "LINEAGE · CHAIN";
  const kids = [
    el("div", {}, close, " ", el("strong", {}, `${title} · ${d.event_id.slice(0, 8)}`), " ",
      el("button", { onclick: () => go({ dir: dir === "forward" ? "back" : "forward" }) }, dir === "forward" ? "l back" : "⇧L forward")),
    ...d.flags.map((f) => el("div", { class: "flag" }, `▨ ${f}`)),
    ...d.breaks.map((b) => el("div", { class: "broken" }, b.text)),
    el("ol", {}, d.chain.map((c) => el("li", {},
      el("button", { onclick: () => go({ lineage: c.event_id }) }, c.event_id.slice(0, 8)),
      ` ${c.type} ${c.subtype} · ${c.producer} · ${c.ts}`,
      c.payload === "held" ? "" : el("span", { class: "vouch" }, ` ${c.payload}`),
      el("ul", {}, c.summary.map((s) => el("li", {}, s)))))),
  ];
  if (dir === "back") {
    kids.push(el("h3", {}, "ENVELOPE"));
    kids.push(el("pre", {}, d.envelope ? JSON.stringify(d.envelope, null, 2) : "no decoded envelope: the payload is not held"));
    kids.push(el("h3", {}, "RAW"));
    kids.push(el("div", { class: d.raw_vouch ? "vouch" : "" }, d.raw));
  }
  pane.replaceChildren(...kids);
}
