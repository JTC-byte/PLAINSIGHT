// Assessment, the DRAFT's read side (design 3.6, 4.5). Each sentence an analyst
// wrote about the seed, with what it cites and what has happened to that
// evidence since, then the chain it rests on, walked back to the
// authorization: the product of PLAINSIGHT is that every sentence can be walked
// back this way. Writing and export are not built in this slice, and the page
// says so rather than offering a control that does nothing.

import { h, tok, lin } from "../lib/dom.js";
import { getJSON, liveLook } from "../lib/api.js";
import { selectorLabel, short, stamp } from "../lib/words.js";
import { chainList } from "./lineage.js";

function clusterName(m, eventId) {
  const row = (m.dossier ? m.dossier.bands.find((b) => b.band === "FUSION").rows : []).find((r) => r.lineage === eventId);
  return row ? `Identity cluster ${short(row.cluster_id)} · event ${short(eventId)}` : `Identity cluster, event ${short(eventId)}`;
}

export async function renderAssessment(el, ctx) {
  const m = ctx.model;
  const band = m.dossier ? m.dossier.bands.find((b) => b.band === "STATE") : null;
  const rows = band ? band.rows : [];
  el.append(h("div", { class: "section-title" },
    h("h2", {}, "What do we say, and can we prove every sentence?"),
    h("span", { class: "sub" }, rows.length ? `${rows.length} ${rows.length === 1 ? "sentence cites" : "sentences cite"} this account` : "")));
  if (!rows.length) {
    el.append(h("div", { class: "card card-b muted" }, band ? band.empty : "No sentence cites this account."));
    return;
  }
  for (const r of rows) {
    const chain = await getJSON(`${m.base}/lineage/${r.lineage}`);
    const d = chain.ok ? chain.body : null;
    const cites = d && d.envelope && d.envelope.payload ? d.envelope.payload.citations || [] : [];
    const citeChips = cites.map((c) => {
      const claim = m.claims.get(c.ref);
      return h("button", { class: "cite", type: "button", onclick: () => ctx.lineage(c.ref, c.cited_as) },
        h("span", { class: "faint" }, `cites ${c.cited_as}`),
        claim ? h("span", { class: ["mono", claim.generated && "generated"] }, claim.value) : h("span", { class: "mono" }, short(c.ref)),
        h("span", { "aria-hidden": "true" }, "⧉"));
    });
    const basis = d ? d.chain.filter((c) => c.depth === 1) : [];
    el.append(h("div", { class: "cols" },
      h("div", { class: "stack" },
        h("section", { class: "card layer-state sentence", "aria-label": "assessment sentence" },
          h("div", { class: "tier" }, "STATE · AN ANALYST'S SENTENCE"),
          h("blockquote", {}, r.text),
          h("div", { class: "by" }, h("span", {}, r.author), citeChips, lin(() => ctx.lineage(r.lineage, "the sentence"), "the sentence")),
          r.consequences && r.consequences.length ? h("div", { class: "cons" },
            h("div", { class: "tier" }, "WHAT HAS HAPPENED TO WHAT IT CITES"),
            r.consequences.map((c) => h("div", { class: "note-line" }, h("b", {}, c)))) : null,
          d && d.flags && d.flags.length ? h("div", { class: "cons" },
            h("div", { class: "tier" }, "FLAGS ON ITS CHAIN"),
            d.flags.map((f) => h("div", { class: "flag" }, f))) : null),
        h("section", { class: "card" },
          h("div", { class: "card-h" }, h("h2", {}, "It rests directly on"), h("span", { class: "right" }, `${basis.length} events`)),
          h("div", { class: "card-b" }, h("div", { class: "rows" }, basis.map((b) => h("div", { class: "row" },
            h("div", { class: "grow" }, h("div", {}, h("b", {}, b.type === "IDENTITY_EVENT" ? clusterName(m, b.event_id) : selectorLabel(((b.summary || [""])[0] || "").replace("claim ", "")))),
              (b.summary || []).map((x) => h("div", { class: "faint" }, x))),
            lin(() => ctx.lineage(b.event_id, b.subtype), b.subtype)))))),
        liveLook ? null : h("section", { class: "card" },
          h("div", { class: "card-h" }, h("h2", {}, "Writing and export")),
          h("div", { class: "card-b muted" },
            h("p", {}, "The writing surface and the export gate are not built in this slice. When they are, citation is the review gate: an unreviewed claim shows its review strip before it can be cited, and the export enforces citation completeness and data minimization together (design 3.6, 4.5)."),
            h("p", {}, "Nothing on this page writes, copies or exports anything.")))),
      h("div", { class: "stack" },
        h("section", { class: "card" },
          h("div", { class: "card-h" }, h("h2", {}, "The proof path"), h("span", { class: "sub" }, "every link, back to the human act that made it collectable"),
            h("span", { class: "right" }, d ? `${d.chain.length} events` : "")),
          h("div", { class: "card-b" }, d ? chainList(ctx, d.chain, d.event_id, "the sentence")
            : chain.dropped ? ctx.notLoaded("lineage") : h("div", { class: "note-line" }, chain.body ? chain.body.text : `the server answered ${chain.status}`)),
          d ? h("div", { class: "card-foot" }, liveLook ? "Read down from the sentence to every record it rests on." : `Read down from the sentence: the cluster and the claim it cites, the proposal and the item beneath them, the run, the gate's permission, and the authorization's grant, extension and revocation. Raw bytes: ${d.raw || "not served"}.`) : null))));
  }
  if (!liveLook) el.append(h("p", { class: "faint" }, `Sentences read from the dossier's STATE band at ${m.loadedAt.toLocaleTimeString()}. A sentence citing evidence that was revoked or disputed stays visible with what happened, and is never silently withdrawn.`));
}
