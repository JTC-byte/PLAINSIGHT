// Tools, the COLLECTION side (design 7.4) and the system's own state (the
// harvest's lesson 14). Tiles for what ran and what decided, each state in
// words with its source. Then every mechanism's state as the server reports
// it, verbatim. Then the whole log counted, so that what the other tabs do not
// draw is still accounted for: annotate, never filter. Connector health in its
// five states is the COLLECTION board of slice 4, and this build's API does not
// serve it, so no tile here claims a health state.

import { h, tok, lin } from "../lib/dom.js";
import { roleOf, eventLabel, stamp, short, plural } from "../lib/words.js";

function tile(head, state, novouch, lines, action) {
  return h("section", { class: "card tile" },
    h("div", { class: "tile-h" }, head),
    h("div", { class: ["tile-state", novouch && "novouch"] }, state),
    h("div", { class: "tile-b" }, lines.map((l) => h("div", {}, l))),
    action || null);
}

export async function renderTools(el, ctx) {
  if (liveLook) {
    renderLiveTools(el, ctx);
    return;
  }
  const m = ctx.model;
  const hd = m.header;
  const roll = hd.rollup || {};
  const subtypes = roll.event_subtype || {};
  const tiles = [];

  for (const run of m.runs.values()) {
    const p = run.payload;
    const end = run.end ? run.end.payload : null;
    const health = subtypes["SYSTEM_EVENT.CONNECTOR_HEALTH"] || 0;
    tiles.push(tile(
      [h("div", { class: "avatar", "aria-hidden": "true" }, "co"), h("div", {}, h("h3", {}, p.connector_id), h("div", { class: "ver" }, `version ${p.connector_version} · ${p.connector_kind}`))],
      end ? `RAN · exit ${end.exit_code} · ${end.error_class} · ${plural(end.item_count, "item")} in ${duration(end.duration_ms)}` : "RAN · no run end is recorded",
      !end,
      [`argv_template ${p.argv_template}`, `looked as ${p.egress ? p.egress.egress_identity : "?"} from ${p.egress ? p.egress.environment : "?"}`,
        p.credential_id ? `credential ${p.credential_id}` : "no credential was used",
        `health: ${plural(health, "connector health report")} in the log; this build's API does not serve its state, so this tile claims none`],
      h("div", { css: { "margin-top": "10px" } }, lin(() => ctx.lineage(run.start.event_id, "the run"), "the run"))));
  }
  const proposals = [...m.edgeText.values()].filter((e) => e.kind === "proposes");
  if (proposals.length) {
    const actor = proposals[0].actor;
    const model = (/by (\S+ \S+):/.exec(proposals[0].text) || [])[1] || actor;
    const uncal = proposals.filter((e) => /uncalibrated/.test(e.text)).length;
    const notAccepted = proposals.filter((e) => /^NOT ACCEPTED/.test(e.text)).length;
    tiles.push(tile(
      [h("div", { class: "avatar inf", "aria-hidden": "true" }, "ma"), h("div", {}, h("h3", {}, actor), h("div", { class: "ver" }, model))],
      `PROPOSED ${proposals.length} · ${notAccepted} of them NOT ACCEPTED`, false,
      [`${uncal} of ${proposals.length} uncalibrated: no calibration reference is recorded`, "a matcher proposes and never asserts; only an analyst's act puts a proposal into the picture"]));
  }
  const decisions = [...m.events.values()].filter((e) => e.type === "COLLECT_EVENT").sort((a, b) => String(a.ts).localeCompare(String(b.ts)));
  if (decisions.length) {
    tiles.push(h("section", { class: "card tile" },
      h("div", { class: "tile-h" }, h("div", { class: "avatar", "aria-hidden": "true" }, "gt"), h("div", {}, h("h3", {}, "runner-subject-guard"), h("div", { class: "ver" }, "the subject gate: decides what may run"))),
      h("div", { class: "tile-state" }, decisions.map((d) => d.subtype.replaceAll("_", " ")).join(" · ")),
      h("div", { class: "rows", css: { "margin-top": "10px" } }, decisions.map((d) => {
        const text = (m.decisions.get(d.event_id) || {}).text || (d.summary || [])[0];
        return h("div", { class: "row" }, h("div", { class: "grow" }, h("div", {}, text), h("div", { class: "faint" }, stamp(d.ts))), lin(() => ctx.lineage(d.event_id, d.subtype), d.subtype));
      }))));
  }

  const guard = hd.guard_replaced || {};
  const dropped = hd.notices_dropped || {};
  const sum = (o) => Object.values(o).reduce((a, b) => a + (Number(b) || 0), 0);
  const mech = [
    { m: "Collection halt", r: "RT-11", s: hd.halt || "no halt: no SHRED_FAILED with halt_system_wide is held", sub: hd.halt ? "clears only when verify_shred passes all five RT-9 checks for the failed case" : "", novouch: !!hd.halt },
    { m: "Retention sweep", r: "RT-12", s: (hd.sweep || {}).text || "not served", sub: "read from the latest heartbeat against its own next due time, with no grace", novouch: !!(hd.sweep || {}).vouch },
    { m: "Retention", r: "retain_until", s: hd.retention, sub: "", novouch: !!hd.retention_vouch },
    { m: "Retention anchor", r: "U-02", s: hd.anchor, sub: "the anchor instant is an open question; this build reads the first event", novouch: false },
    { m: "Environment", r: "EG-1", s: hd.environment, sub: "", novouch: false },
    { m: "Case registry", r: "registry", s: hd.state, sub: "", novouch: false },
    ...m.coverage.map((c) => ({ m: "Coverage", r: "watchdog", s: c.text, sub: "", novouch: /^(OPEN|UNVERIFIED)/.test(c.text), id: c.lineage })),
    { m: "Egress guard", r: "EG-3", s: sum(guard) ? `${sum(guard)} header, title or body value(s) replaced since launch` : "nothing replaced since launch: no header, title or error body carried a held value", sub: "", novouch: sum(guard) > 0 },
    { m: "Notice stream", r: "9.3", s: sum(dropped) ? `${sum(dropped)} notice(s) dropped since launch` : "no notice dropped since launch", sub: "", novouch: sum(dropped) > 0 },
  ];

  const types = roll.event_type || {};
  const total = Object.values(types).reduce((a, b) => a + b, 0);
  const drawn = m.events.size;
  const drawnBySub = new Map();
  for (const e of m.events.values()) drawnBySub.set(`${e.type}.${e.subtype}`, (drawnBySub.get(`${e.type}.${e.subtype}`) || 0) + 1);
  const countRows = [];
  for (const [t, n] of Object.entries(types).sort()) {
    countRows.push(h("tr", {}, h("th", {}, t.replace("_EVENT", "").toLowerCase()), h("th", { class: "n" }, String(n)), h("th", { class: "n" }, "")));
    for (const [st, k] of Object.entries(subtypes).filter(([x]) => x.startsWith(`${t}.`)).sort()) {
      const shown = drawnBySub.get(st) || 0;
      countRows.push(h("tr", { class: "sub" }, h("td", {}, eventLabel(t, st.split(".")[1])), h("td", { class: "n" }, String(k)),
        h("td", { class: "n" }, shown >= k ? "drawn" : shown ? `${shown} drawn` : "counted here only")));
    }
  }

  el.append(
    h("div", { class: "section-title" }, h("h2", {}, "What ran, what decided, and what is the system's own state?")),
    ctx.missing("lineage") ? h("p", { class: "muted" }, "Some events' lineage did not load, so a tile below may be missing. The System section reads the case header and is complete.") : "",
    h("div", { class: "tiles" }, tiles),
    liveLook ? "" : h("section", { class: "card", css: { "margin-top": "18px" } },
      h("div", { class: "card-h" }, h("h2", {}, "System"), h("span", { class: "sub" }, "every mechanism's state, in the server's words")),
      mech.map((x) => h("div", { class: ["mech", x.novouch && "novouch"] },
        h("div", { class: "m" }, x.m, h("small", {}, x.r)),
        h("div", { class: "s" }, x.s, x.sub ? h("small", {}, x.sub) : null),
        x.id ? lin(() => ctx.lineage(x.id, x.m), x.m) : h("span", {})))),
    liveLook ? "" : h("section", { class: "card", css: { "margin-top": "18px" } },
      h("div", { class: "card-h" }, h("h2", {}, "Everything the log holds"), h("span", { class: "sub" }, `${plural(total, "event")} in this case; ${drawn} are drawn on the other tabs`)),
      h("table", { class: "counts" }, h("tbody", {}, countRows)),
      h("div", { class: "card-foot" }, "Counted from the store's rollup. An event marked counted here only is in the log and reachable from no node and no authorization this build reads, such as a heartbeat; nothing is dropped.")));
}

import { liveLook } from "../lib/api.js";

/** A run's length in the largest unit that reads plainly. */
function duration(ms) {
  const n = Number(ms);
  if (!Number.isFinite(n)) return `${ms} ms`;
  if (n < 2000) return `${n} ms`;
  if (n < 120000) return `${Math.round(n / 1000)} s`;
  if (n < 7200000) return `${Math.round(n / 60000)} min`;
  if (n < 172800000) return `${Math.round(n / 3600000)} h`;
  return `${Math.round(n / 86400000)} days`;
}

import { who as whoLabel, day as dayOf } from "../lib/words.js";

/** The live presentation's Tools tab, in an operator's terms: which collectors ran on which platform, and what waits on review. */
function renderLiveTools(el, ctx) {
  const m = ctx.model;
  const items = [...m.events.values()].filter((e) => e.type === "PROBE_EVENT" && e.subtype === "ITEM");
  const byProducer = new Map();
  for (const e of items) {
    if (!byProducer.has(e.producer)) byProducer.set(e.producer, []);
    byProducer.get(e.producer).push(String(e.ts));
  }
  const rows = [...byProducer.entries()].map(([p, ts]) => ({ name: whoLabel(p), n: ts.length, first: ts.sort()[0], last: ts[ts.length - 1] }))
    .sort((a, b) => a.name.localeCompare(b.name));
  const links = [...m.events.values()].filter((e) => e.type === "LINK_EVENT");
  const kinds = new Map();
  for (const e of links) {
    const k = String(e.subtype || "link").toLowerCase().replaceAll("_", " ");
    kinds.set(k, (kinds.get(k) || 0) + 1);
  }
  const unreviewed = [...m.claims.values()].filter((c) => !c.review || /^unreviewed/.test(c.review)).length;
  el.append(
    h("div", { class: "section-title" }, h("h2", {}, "What was collected, and what waits on review?"),
      h("span", { class: "sub" }, `${rows.length} collectors · ${items.length} posts and records`)),
    h("section", { class: "card" },
      h("div", { class: "card-h" }, h("h2", {}, "Collectors by platform"), h("span", { class: "right" }, `${rows.length} platforms`)),
      h("div", { class: "card-b" }, h("div", { class: "rows" }, rows.map((r) => h("div", { class: "row" },
        h("div", { class: "grow" }, h("b", {}, r.name), h("div", { class: "faint" }, `${r.n} ${r.n === 1 ? "record" : "records"} · ${dayOf(r.first)} to ${dayOf(r.last)}`))))))),
    h("section", { class: "card", css: { "margin-top": "18px" } },
      h("div", { class: "card-h" }, h("h2", {}, "Waiting on review")),
      h("div", { class: "card-b" }, h("div", { class: "rows" },
        h("div", { class: "row" }, h("div", { class: "grow" }, h("b", {}, `${links.length} suggested ${links.length === 1 ? "link" : "links"}`),
          h("div", { class: "faint" }, `${[...kinds.entries()].map(([k, n]) => `${n} ${k}`).join(" · ")} · not yet confirmed by an analyst`))),
        h("div", { class: "row" }, h("div", { class: "grow" }, h("b", {}, `${unreviewed} unreviewed ${unreviewed === 1 ? "claim" : "claims"}`),
          h("div", { class: "faint" }, "observed, and not yet verified or disputed")))))));
}
