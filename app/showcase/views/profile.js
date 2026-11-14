// The profile header: the seed at the top of every tab, in the idiom of a
// profile page. The name is the value of the claim that anchors the seed,
// shown with its lineage and with the server's tokens beside it. Nothing here
// is a count of standing: the numbers are how many claims, clusters,
// exclusions and proposals the case holds about this one account, each a fact
// that opens one layer down.

import { h, clear, silhouette, tok, kbd, lin } from "../lib/dom.js";
import { selectorChip, selectorLabel, short, plural, isPlaceholder, PLACEHOLDER_NOTE } from "../lib/words.js";
import { liveLook } from "../lib/api.js";
import { closePopover } from "./status.js";

export function subjectName(model) {
  const a = model.anchorClaim;
  if (a && a.value) return { text: a.value, mono: true, claim: a };
  const node = model.nodes.get(model.focus);
  const first = node && node.lines ? node.lines[0].replace(/^[a-z]{2} /, "") : "the seed";
  return { text: first, mono: false, claim: null };
}

function bands(model) {
  const out = {};
  for (const b of (model.dossier ? model.dossier.bands : [])) out[b.band] = b.rows;
  return out;
}

function entityType(model) {
  const node = model.nodes.get(model.focus);
  return node && node.entity_type ? node.entity_type : (node ? node.kind : "entity");
}

function anchorLine(model) {
  const node = model.nodes.get(model.focus);
  return node && node.lines ? node.lines.find((l) => l.startsWith("anchor")) : null;
}

export function facts(model) {
  const b = bands(model);
  const clusters = b.FUSION || [];
  const excluded = [...model.nodes.values()].filter((n) => n.kind === "candidate" && (n.lines || []).some((l) => l.startsWith("EXCLUDED")));
  return {
    claims: (b.OBSERVATION || []).length,
    inForce: clusters.filter((c) => !c.tombstone).length,
    revoked: clusters.filter((c) => c.tombstone).length,
    excluded: excluded.length,
    proposals: (b.INFERENCE || []).length,
    sentences: (b.STATE || []).length,
    sources: new Set([...model.events.values()].filter((e) => !liveLook || String(e.producer || "").startsWith("connector-")).map((e) => e.producer)).size,
  };
}

function preflight(anchor, model) {
  const node = model.nodes.get(model.focus);
  const p = node && node.inspect ? node.inspect.pivot : null;
  const pop = document.getElementById("popover");
  clear(pop,
    h("button", { class: "iconbtn close", type: "button", "aria-label": "close", onclick: closePopover }, "esc"),
    h("h3", {}, "Deep dive pre-flight"),
    h("p", {}, "What a deep dive from this account would need, read from the server's pre-flight. It records nothing and dispatches nothing."),
    p ? h("div", { class: "rows" }, p.lines.map((l) => h("div", { class: "note-line" }, l)))
      : h("p", {}, "No pre-flight was served for this node."),
    h("div", { class: "src" }, "A deep dive takes one node and one motivating claim per act (amendment 9.11). This page sends no request that could start one."));
  pop.hidden = false;
  const r = anchor.getBoundingClientRect();
  pop.style.setProperty("left", `${Math.max(16, Math.min(r.left - 200, window.innerWidth - pop.offsetWidth - 16))}px`);
  pop.style.setProperty("top", `${Math.min(r.bottom + 8, window.innerHeight - pop.offsetHeight - 16)}px`);
  pop.style.removeProperty("right");
  pop.querySelector(".close").focus();
}

function chips(ctx) {
  const m = ctx.model;
  const rows = (bands(m).OBSERVATION || []);
  return rows.map((r) => {
    const claim = m.claims.get(r.claim_id) || {};
    // A review is read from its own leading word: "unreviewed: no analyst has verified or disputed" is neither.
    const review = /^disputed/.test(claim.review || "") || /(^|· )disputed/.test(r.provenance || "") ? "disputed" : (/(^|· )verified/.test(r.provenance || "") ? "verified" : "unreviewed");
    return h("button", {
      class: "chip", type: "button", title: `${selectorLabel(r.selector_type)} · open its lineage`,
      onclick: () => ctx.lineage(r.lineage, r.value || r.selector_type),
    },
    h("span", { class: "type", "aria-hidden": "true" }, selectorChip(r.selector_type)),
    h("span", { class: ["mono", r.generated && "generated"] }, r.value),
    h("span", { class: "note" }, `${r.generated ? "generated · " : ""}${review === "unreviewed" ? "unreviewed" : `analyst: ${review}`}`));
  });
}

export function renderProfile(el, ctx, compact) {
  const m = ctx.model;
  const name = subjectName(m);
  const person = ctx.fictional && ctx.fictional.subject ? ctx.fictional.subject.name : null;
  const f = facts(m);
  const node = m.nodes.get(m.focus);
  const tokens = (m.dossier ? m.dossier.focus_tokens : []).filter((t) => t !== "past retain_until");
  const nameEl = person
    ? h("span", { class: "person" }, person, liveLook ? null : h("span", { class: "tok", title: ctx.fictional.note || "invented for this showcase, display only" }, "fictional"))
    : name.claim
      ? h("button", { type: "button", class: "namebtn mono", title: "open the lineage of the claim that anchors this account", onclick: () => ctx.lineage(name.claim.claim_id, name.text) }, name.text)
      : h("span", {}, name.text);
  el.classList.toggle("compact", !!compact);
  if (compact) {
    clear(el, h("div", { class: "wrap" }, h("div", { class: "compact-row" },
      h("div", { class: "portrait" }, silhouette(48)),
      h("div", { class: "name" }, nameEl, h("span", { class: "tok strong" }, entityType(m))),
      liveLook ? null : h("div", { class: "tokens" }, tokens.map((t) => tok(t, true))),
      h("div", { class: "faint" }, liveLook ? dossierCounts(m).map(([n, one, many]) => `${n} ${n === 1 ? one : many}`).join(" · ") : `${plural(f.claims, "claim")} · ${plural(f.inForce, "cluster")} in force · ${f.excluded} excluded · ${plural(f.proposals, "proposal")} not accepted`))));
    return;
  }
  const anchor = anchorLine(m);
  clear(el, h("div", { class: "wrap" },
    h("div", { class: "cover" }, h("div", { class: "cover-grid", "aria-hidden": "true" }),
      liveLook ? null
      : ctx.fictional
        ? h("div", { class: "cover-note" }, h("span", { class: "pill" }, h("b", {}, "FICTIONAL"), "an invented person drawn over a test case; nothing was collected"))
        : /^LOCAL/.test(m.header.environment || "") ? h("div", { class: "cover-note" }, h("span", { class: "pill" }, h("b", {}, "SYNTHETIC"), "a test subject from a tracked corpus file, not a person")) : null),
    h("div", { class: "idrow" },
      h("div", { class: "portrait" }, silhouette(148)),
      h("div", { class: "idblock" },
        liveLook ? null : h("div", { class: "kicker" }, `Seed ${entityType(m).toLowerCase()} · case C-${short(m.caseId)} · ${String(m.header.state || "").replace(/^open: /, "open, ")}`),
        h("h1", {}, nameEl, h("span", { class: "tok strong" }, entityType(m)), name.claim ? lin(() => ctx.lineage(name.claim.claim_id, name.text), "the anchor claim") : null,
          isPlaceholder(name.text) ? h("span", { class: "tok", title: PLACEHOLDER_NOTE }, "placeholder value") : null),
        liveLook ? null : h("div", { class: "idline" },
          anchor ? h("span", {}, anchor.replace(/^anchor /, "Anchor: ")) : null,
          tokens.map((t) => tok(t, true))),
        ctx.missing("dossier") ? h("div", { class: "idmeta" }, h("span", {}, "The counts wait for the dossier, which did not load.")) : liveLook ? h("div", { class: "idmeta" }, dossierCounts(m).map(([n, one, many]) => h("span", {}, h("b", {}, String(n)), ` ${n === 1 ? one : many}`))) : h("div", { class: "idmeta" },
          h("span", {}, h("b", {}, String(f.claims)), ` ${f.claims === 1 ? "claim" : "claims"}`),
          h("span", {}, h("b", {}, String(f.inForce)), ` ${f.inForce === 1 ? "cluster" : "clusters"} in force`),
          h("span", {}, h("b", {}, String(f.revoked)), " revoked"),
          h("span", {}, h("b", {}, String(f.excluded)), " excluded"),
          h("span", {}, h("b", {}, String(f.proposals)), ` ${f.proposals === 1 ? "proposal" : "proposals"} not accepted`),
          h("span", {}, h("b", {}, String(f.sources)), " sources"))),
      h("div", { class: "actions" },
        h("button", { class: "btn primary", type: "button", onclick: () => node && ctx.lineage(node.lineage_heads[0], name.text) }, kbd("l"), "Lineage"),
        h("button", { class: "btn", type: "button", onclick: (e) => preflight(e.currentTarget, m) }, "Deep dive pre-flight"))),
    h("div", { class: "chiprow", "aria-label": "selectors about this account" }, chips(ctx))));
}

/** The live presentation's header counts: what the dossier holds, each counted from the case as read. */
function dossierCounts(m) {
  const nodes = [...m.nodes.values()];
  const entities = (...types) => nodes.filter((n) => n.kind === "entity" && types.includes(n.entity_type)).length;
  const claims = [...m.claims.values()];
  const values = (type) => new Set(claims.filter((c) => c.selector_type === type).map((c) => c.value)).size;
  const items = [...m.events.values()].filter((e) => e.type === "PROBE_EVENT" && e.subtype === "ITEM").length;
  const sources = new Set([...m.events.values()].filter((e) => String(e.producer || "").startsWith("connector-")).map((e) => e.producer)).size;
  return [
    [entities("Account"), "account", "accounts"],
    [values("email"), "email", "emails"],
    [values("phone"), "phone", "phones"],
    [entities("PersonCandidate", "Person"), "person", "people"],
    [entities("Org", "Organization"), "organization", "organizations"],
    [items, "post or record", "posts and records"],
    [sources, "source", "sources"],
  ];
}
