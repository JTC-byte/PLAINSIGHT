// The Lineage Drawer (design 5.7, amendment 9.9): the chain behind a value,
// read top to bottom, back to the human act that made it collectable; or,
// forward, everything that rests on it. Three tiers: the chain, the decoded
// envelope, the raw bytes. Flags and breaks render as consequences in the one
// hue, because the server says the system does not vouch for them; a raw pane
// is red only on the server's raw_vouch. Every entry re-centres the drawer.
// Above the envelope, and only when the response carries one, an evidence
// snapshot shows what the source showed at capture (amendment 9.31); the
// server sends none, and a display-only case pack can supply one.

import { h, clear, tok, notLoaded } from "../lib/dom.js";
import { getJSON } from "../lib/api.js";
import { eventLabel, layerOf, stamp, short } from "../lib/words.js";
import { evidenceTier } from "./evidence.js";

let returnFocus = null;
let hook = null;
let asked = 0;

/** The shell's callback, told {id, dir, label} when the drawer opens and null when it closes, so the drawer's state is in the URL. */
export function onLineageChange(fn) {
  hook = fn;
}

export function lineageOpen() {
  return !document.getElementById("drawer").hidden;
}

export function closeLineage() {
  const drawer = document.getElementById("drawer");
  drawer.hidden = true;
  document.getElementById("scrim").hidden = true;
  clear(drawer);
  if (returnFocus && document.body.contains(returnFocus)) returnFocus.focus();
  returnFocus = null;
  if (hook) hook(null);
}

export function entry(ctx, c, headId, label) {
  const layer = layerOf(c.type);
  const dot = layer === "auth" ? "dot auth" : layer === "act" ? "dot" : `dot ${layer}`;
  const indent = Math.min(c.depth || 0, 7) * 18;
  return h("li", { class: [c.event_id === headId && "head"], css: { "--indent": `${indent}px` } },
    h("span", { class: dot, "aria-hidden": "true" }),
    h("div", { class: "what" }, eventLabel(c.type, c.subtype), h("small", {}, `${who(c.producer)} · ${stamp(c.ts)}`)),
    h("div", { class: "lines" },
      (c.summary || []).map((s) => h("div", {}, s)),
      c.payload && c.payload !== "held" ? h("div", {}, tok(`payload ${c.payload}`, true)) : null),
    c.event_id === headId ? h("span", { class: "go faint" }, "here")
      : h("button", { class: "lin go", type: "button", title: "re-centre the drawer on this event", "aria-label": `re-centre on ${eventLabel(c.type, c.subtype)}`, onclick: () => openLineage(ctx, c.event_id, eventLabel(c.type, c.subtype), "back") }, "⧉"));
}

/**
 * The audit trail (amendment 9.30): the server's steps, oldest first, one row
 * each, heading in the gutter and its closed-field lines beside it. A heading
 * re-centres the drawer on its event, as an entry's button does; the head's
 * own row says so instead. A break below leaves the trail incomplete, and the
 * block says so rather than reading as whole.
 */
export function auditTrail(ctx, audit, headId, broken, flags = []) {
  return h("div", { class: "audit" },
    h("div", { class: "tier" }, "AUDIT TRAIL"),
    h("p", { class: "faint" }, "Read down, oldest first: who authorized it, what the gate decided, which tool collected it and from where, what processed it, and who acted on it since."),
    broken ? h("div", { class: "flag" }, "This trail is incomplete: the chain is broken below, and each break is listed under CHAIN.") : null,
    flags.length ? h("div", { class: "rows" }, flags.map((f) => h("div", { class: "flag" }, f))) : null,
    h("ol", { class: "audit-trail" }, audit.map((a) => h("li", {},
      a.event_id === headId
        ? h("span", { class: "audit-step here", title: "the drawer is on this event" }, a.label)
        : h("button", { class: "audit-step", type: "button", title: "re-centre the drawer on this event", "aria-label": `re-centre on ${a.label}`, onclick: () => openLineage(ctx, a.event_id, a.label, "back") }, a.label),
      h("div", { class: "lines" }, (a.lines || []).map((s) => h("div", {}, s)))))));
}

/** The chain as a list, the head first, each entry indented by its depth. */
export function chainList(ctx, chain, headId, label) {
  return h("ol", { class: "chain" }, h("span", { class: "chain-rail", "aria-hidden": "true" }), chain.map((c) => entry(ctx, c, headId, label)));
}

export async function openLineage(ctx, eventId, label, dir = "back") {
  const m = ctx.model;
  const drawer = document.getElementById("drawer");
  if (drawer.hidden) returnFocus = document.activeElement;
  const mine = ++asked;
  const r = await getJSON(`${m.base}/lineage/${eventId}${dir === "forward" ? "?dir=forward" : ""}`);
  if (mine !== asked) return;
  const close = h("button", { class: "iconbtn", type: "button", "aria-label": "close the lineage drawer", onclick: closeLineage }, "esc");
  const flip = h("button", {
    class: "btn", type: "button", onclick: () => openLineage(ctx, eventId, label, dir === "forward" ? "back" : "forward"),
  }, dir === "forward" ? "What it rests on" : "What depends on it");
  if (!r.ok) {
    clear(drawer, h("div", { class: "drawer-h" }, h("h2", {}, "Lineage"), h("div", { class: "right" }, close)),
      h("div", { class: "drawer-b" }, h("div", {}, r.dropped
        ? notLoaded("This chain", () => openLineage(ctx, eventId, label, dir))
        : h("div", { class: "note-line" }, r.body ? r.body.text : `the server answered ${r.status}`))));
  } else {
    const d = r.body;
    const chain = chainList(ctx, d.chain, d.event_id, label);
    const left = h("div", {},
      dir === "back" && (d.audit || []).length ? auditTrail(ctx, d.audit, d.event_id, (d.breaks || []).length > 0, d.flags || []) : null,
      h("div", { class: "tier" }, dir === "forward" ? "EVERYTHING THAT RESTS ON IT" : "CHAIN · WHAT IT RESTS ON"),
      h("p", { class: "faint" }, dir === "forward"
        ? (d.chain.length ? `${d.chain.length} ${d.chain.length === 1 ? "event rests" : "events rest"} on this one, and would need review if it were wrong.` : "Nothing in this case rests on this event.")
        : "Read down: each event rests on the ones beneath it. Where the chain reaches it, the bottom is the authorization that made the run collectable."),
      (d.flags || []).length ? h("div", { class: "rows" }, d.flags.map((f) => h("div", { class: "flag" }, f))) : null,
      (d.breaks || []).length ? h("div", { class: "rows" }, d.breaks.map((b) => h("div", { class: "flag" }, b.text || String(b)))) : null,
      chain);
    const right = dir === "forward"
      ? h("div", {}, h("div", { class: "tier" }, "HOW TO READ IT"),
        h("p", { class: "muted" }, "Forward lineage reads the same table the other way. It answers what would break if this event were wrong."),
        h("p", { class: "muted" }, "Selecting an event here re-centres the drawer on it and collects nothing."))
      : h("div", {},
        d.evidence ? evidenceTier(d.evidence, d.event_id) : null,
        h("div", { class: "tier" }, "DECODED ENVELOPE"),
        h("pre", { class: "env" }, d.envelope ? JSON.stringify(d.envelope, null, 2) : "no decoded envelope: the payload is not held"),
        h("div", { class: "tier" }, "RAW"),
        h("div", { class: d.raw_vouch ? "flag" : "note-line" }, d.raw || "no raw state was served"));
    clear(drawer,
      h("div", { class: "drawer-h" },
        h("h2", {}, dir === "forward" ? "Forward lineage" : "Lineage"),
        h("span", { class: "sub" }, `${label ? label + " · " : ""}event ${short(d.event_id)}`),
        h("div", { class: "right" }, flip, close)),
      h("div", { class: "drawer-b" }, left, right));
  }
  drawer.hidden = false;
  document.getElementById("scrim").hidden = false;
  close.focus();
  if (hook) hook({ id: eventId, dir, label });
}

import { who } from "../lib/words.js";
