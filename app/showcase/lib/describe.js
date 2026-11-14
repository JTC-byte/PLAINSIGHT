// One event, in words: the server's own sentence for it where a route serves
// one (an adjudication's text, a proposal's text, a decision's text), else the
// lineage summary, plus the decoded fields an analyst reads (a claim's value,
// an item's locator, a run's outcome). Nothing is inferred here; a field the
// server did not serve is left out, never guessed.

import { h, tok } from "./dom.js";
import { selectorLabel, eventLabel, short } from "./words.js";

function payload(e) {
  return e && e.envelope && e.envelope.payload ? e.envelope.payload : null;
}

/** What an adjudication or a citation points at, in a few words. */
export function targetWords(model, ref) {
  if (!ref) return null;
  const claim = model.claims.get(ref);
  if (claim) return [`the ${selectorLabel(claim.selector_type).toLowerCase()} claim `, h("span", { class: ["mono", claim.generated && "generated"] }, claim.value || short(ref))];
  const item = model.items.get(ref);
  if (item) return [`item `, h("span", { class: "mono" }, item.locator || short(ref))];
  const ev = model.events.get(ref);
  if (ev && ev.type === "IDENTITY_EVENT") {
    const band = (ev.summary || [""])[0].split(" · ")[1];
    return [`the ${band || ""} identity cluster ${short(ref)}`.replace("  ", " ")];
  }
  if (ev) return [`${eventLabel(ev.type, ev.subtype).toLowerCase()} ${short(ref)}`];
  return [`event ${short(ref)}`];
}

export function describe(model, e) {
  const p = payload(e);
  const key = `${e.type}.${e.subtype}`;
  const out = { title: eventLabel(e.type, e.subtype), body: [], lines: [], tokens: [] };
  if (e.type === "EXTRACT_EVENT") {
    const c = model.claims.get(e.event_id) || {};
    const type = c.selector_type || (p && p.selector_type);
    const value = c.value || (p && p.value);
    out.body = [`${selectorLabel(type)}: `, h("span", { class: ["mono", c.generated && "generated"] }, value || "value not served")];
    const item = c.item_id ? model.items.get(c.item_id) : null;
    if (!liveLook) out.lines.push(`extracted by ${c.extractor || "an extractor"}${c.source_path ? ` at ${c.source_path}` : ""}${item && item.locator ? ` from item ${item.locator}` : ""}`);
    if (c.review) out.lines.push(c.review);
    else if (c.offWeb) out.lines.push("not about the seed: no edge ties this claim to the seed account");
  } else if (key === "PROBE_EVENT.ITEM") {
    const it = model.items.get(e.event_id) || {};
    const ip = payload(e);
    if (liveLook) {
      out.title = it.locator || "Record";
      out.body = [ip && ip.content_summary ? ip.content_summary : "record returned"];
    } else {
      out.body = ["Item ", h("span", { class: "mono" }, it.locator || short(e.event_id)), ` returned · outcome ${it.outcome || (e.summary || [""])[0].replace("outcome ", "")}`];
    }
    if (e.raw && !liveLook) out.tokens.push(tok(e.raw.replace(/^not held: /, ""), !!e.raw_vouch));
    const ign = [...model.adjudications.values()].find((a) => a.target_ref === e.event_id && a.subtype === "IGNORE");
    if (ign) out.lines.push(ign.text);
  } else if (key === "PROBE_EVENT.RUN_START") {
    out.body = [(e.summary || [])[0] || "a run"];
    out.lines = (e.summary || []).slice(1);
  } else if (key === "PROBE_EVENT.RUN_END") {
    out.body = p ? [liveLook ? `${p.item_count} records returned` : `exit ${p.exit_code} · ${p.error_class} · ${p.item_count} items · ${p.duration_ms} ms`] : ["the run ended"];
  } else if (e.type === "COLLECT_EVENT") {
    const d = model.decisions.get(e.event_id);
    out.body = [d ? d.text : (e.summary || [])[0] || ""];
    out.lines = (e.summary || []).slice(1);
  } else if (e.type === "LINK_EVENT") {
    const ed = model.edgeText.get(e.event_id);
    out.body = [ed ? ed.text : (e.summary || []).join(" · ")];
  } else if (key === "IDENTITY_EVENT.EXCLUDE") {
    const node = [...model.nodes.values()].find((n) => n.created_by_event_id === e.event_id);
    out.body = [node ? node.lines[0] : "a candidate was excluded"];
    out.lines = node ? node.lines.slice(1) : [];
  } else if (e.type === "ADJUDICATE_EVENT") {
    const a = model.adjudications.get(e.event_id);
    out.body = [a ? a.text : (e.summary || []).join(" · ")];
    const t = a ? targetWords(model, a.target_ref) : null;
    if (t) out.lines.push(h("span", {}, "on ", ...t));
  } else if (key === "ASSESS_EVENT.SENTENCE") {
    const st = (model.dossier ? model.dossier.bands.find((b) => b.band === "STATE").rows : []).find((r) => r.sentence_id === e.event_id);
    out.body = st ? [h("q", {}, st.text)] : [(e.summary || []).join(" · ")];
    if (st) out.lines = [st.author];
  } else if (key === "SYSTEM_EVENT.COVERAGE_INTERVAL") {
    const c = model.coverage.find((x) => x.lineage === e.event_id);
    out.body = [c ? c.text : "a coverage interval closed"];
  } else {
    out.body = [(e.summary || []).join(" · ") || eventLabel(e.type, e.subtype)];
    out.lines = [];
  }
  return out;
}

/** The text a search box matches against, from what the card shows. */
export function searchText(node) {
  return node.textContent.replace(/\s+/g, " ").trim();
}

import { liveLook } from "./api.js";
