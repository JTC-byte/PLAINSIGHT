// DOSSIER (key 1), read-only: STATE, FUSION, INFERENCE and OBSERVATION stacked
// top to bottom, so reading down walks the lineage backwards. Per-member seams
// are printed per member and never rolled up. A STATE sentence prints, under it,
// each cited event that no longer stands as it did. No number is computed here.

import { el, getJSON, go } from "../app.js";

function lineageButton(id) {
  return el("button", { onclick: () => go({ lineage: id, dir: "back" }) }, "l");
}

export async function renderDossier(pane, state) {
  if (!state.focus) { pane.replaceChildren(el("p", {}, "no focus: press esc esc to return to the seed")); return; }
  const r = await getJSON(`/api/cases/${state.caseId}/dossier?focus=${state.focus}`);
  if (!r.ok) { pane.replaceChildren(el("p", { class: "vouch" }, r.body ? r.body.text : "the dossier could not be read")); return; }
  const d = r.body;
  const kids = [
    el("h2", {}, `DOSSIER · focus ${d.focus.slice(0, 8)}`),
    ...d.focus_lines.map((l) => el("div", {}, l)),
    ...d.focus_tokens.map((t) => el("div", { class: "vouch" }, t)),
  ];
  for (const band of d.bands) {
    kids.push(el("h3", { class: "band" }, band.band));
    if (!band.rows.length) { kids.push(el("div", {}, band.empty)); continue; }
    for (const row of band.rows) {
      if (band.band === "STATE") {
        kids.push(el("div", { class: "row", "data-row": "" }, lineageButton(row.lineage), ` ${row.author}: ${row.text}`,
          ...(row.consequences || []).map((c) => el("div", { class: "consequence" }, c))));
      } else if (band.band === "FUSION") {
        kids.push(el("div", { class: "fusion-row row", "data-row": "", "data-node": row.cluster_id },
          lineageButton(row.lineage), " ",
          el("span", { class: row.tombstone ? "struck" : "" }, `cluster ${row.cluster_id.slice(0, 8)}`),
          ...row.lines.map((l) => el("div", {}, l)),
          el("ul", {}, row.members.map((m) => el("li", {}, `${m.node_id.slice(0, 8)} · seams ${m.seams}`)))));
      } else if (band.band === "INFERENCE") {
        kids.push(el("div", { class: "inference-row row", "data-row": "", "data-node": row.other }, lineageButton(row.lineage), ` ${row.text}`));
      } else {
        kids.push(el("div", { class: "observation-row row", "data-row": "", "data-node": row.node_id || null },
          lineageButton(row.lineage), ` ${row.selector_type || ""} `,
          el("span", { class: row.generated ? "generated" : "" }, row.value || row.text),
          el("div", {}, row.provenance || ""),
          ...(row.vouch_tokens || []).map((t) => el("div", { class: "vouch" }, t))));
      }
    }
  }
  pane.replaceChildren(...kids);
}
