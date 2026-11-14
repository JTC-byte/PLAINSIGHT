// Sources, the STREAM as one feed per source (design 3.2, the 11-02 idiom).
// Each producer that wrote into this case gets its own card: its role, its
// counts by kind, the time of its last event, and everything it wrote, newest
// first, each line opening its lineage. The connector's card leads with its
// runs, because a run is where an observation comes from. Nothing is ranked
// and nothing is merged: two sources saying the same thing stay two lines.

import { h, tok, lin } from "../lib/dom.js";
import { roleOf, eventLabel, stamp, hm, short, plural } from "../lib/words.js";
import { sources } from "../lib/model.js";
import { describe, searchText } from "../lib/describe.js";

function countsByKind(events) {
  const out = new Map();
  for (const e of events) {
    const k = eventLabel(e.type, e.subtype);
    out.set(k, (out.get(k) || 0) + 1);
  }
  return [...out.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
}

function runBlock(ctx, run) {
  const p = run.payload;
  const end = run.end ? run.end.payload : null;
  return h("div", { class: "mini layer-obs" },
    h("div", { class: "mini-h" }, h("span", { class: "t" }, `Run ${short(p.run_id)}`), tok(p.connector_kind || "run"),
      end ? tok(`exit ${end.exit_code} · ${end.error_class}`) : tok("no run end recorded", true),
      lin(() => ctx.lineage(run.start.event_id, `run ${short(p.run_id)}`), "this run")),
    h("dl", { class: "prov" },
      h("dt", {}, "Tool"), h("dd", {}, `${p.connector_id} ${p.connector_version}`),
      h("dt", {}, "Command"), h("dd", { class: "mono" }, p.argv_template || "not recorded"),
      h("dt", {}, "Looked as"), h("dd", {}, p.egress ? `${p.egress.egress_identity} from ${p.egress.environment}` : "not recorded"),
      h("dt", {}, "Credential"), h("dd", {}, p.credential_id || "none: no credential was used"),
      h("dt", {}, "Why"), h("dd", {}, p.motivated_by ? `motivated by ${short(p.motivated_by)}` : "a seed run, motivated by no earlier claim"),
      h("dt", {}, "Returned"), h("dd", {}, end ? `${plural(end.item_count, "item")} in ${end.duration_ms} ms` : `${plural(run.items.length, "item")} recorded`)),
    h("div", { class: "rows" }, run.items.map((it) => h("div", { class: "row" },
      h("span", { class: "type sm", "aria-hidden": "true" }, "it"),
      h("div", { class: "grow" }, h("div", { class: "mono" }, it.locator || short(it.event.event_id)), h("div", { class: "faint" }, `outcome ${it.outcome} · ${(it.event.raw || "").replace(/^not held: /, "")}`)),
      lin(() => ctx.lineage(it.event.event_id, it.locator || "item"), "this item")))));
}

function sourceCard(ctx, src) {
  const m = ctx.model;
  const events = [...src.events].reverse().filter((e) => !liveLook || (e.type === "PROBE_EVENT" && e.subtype === "ITEM") || e.type === "EXTRACT_EVENT");
  const last = src.events.length ? src.events[src.events.length - 1].ts : null;
  const runs = src.role.key === "connector" ? [...m.runs.values()].filter((r) => r.payload.connector_id === src.producer) : [];
  const items = events.map((e) => {
    const d = describe(m, e);
    const node = h("div", { class: "src-item" },
      h("div", { class: "t" }, `${d.title} · ${hm(e.ts)}`),
      lin(() => ctx.lineage(e.event_id, d.title), d.title),
      h("div", { class: "b" }, d.body),
      d.lines.length ? h("div", { class: "d" }, d.lines.map((l) => h("div", {}, l))) : null,
      d.tokens.length ? h("div", { class: "d tokens" }, d.tokens) : null);
    node.dataset.search = searchText(node);
    return node;
  });
  return h("section", { class: "card", id: `src-${src.producer}`, "aria-label": src.producer },
    h("div", { class: "src-h" },
      h("div", { class: ["avatar", src.role.key === "analyst" && "analyst"], "aria-hidden": "true" }, src.role.mono),
      h("div", {}, h("h3", {}, who(src.producer)), h("div", { class: "role" }, src.role.word)),
      h("div", { class: "right faint", css: { "margin-left": "auto", "text-align": "right", "font-size": "12.5px" } },
        h("div", {}, liveLook ? `${events.length} ${events.length === 1 ? "record" : "records"}` : plural(src.events.length, "event")), h("div", {}, last ? `last ${stamp(last)}` : ""))),
    liveLook ? null : h("div", { class: "src-stats" }, countsByKind(src.events).map(([k, n]) => tok(`${n} · ${k.toLowerCase()}`))),
    runs.length && !liveLook ? h("div", { class: "card-b" }, runs.map((r) => runBlock(ctx, r))) : null,
    h("div", {}, items));
}

export async function renderSources(el, ctx) {
  const m = ctx.model;
  const list = sources(m, roleOf).filter((s) => !liveLook || s.role.key === "connector");
  const total = list.reduce((a, s) => a + s.events.length, 0);
  el.append(
    h("div", { class: "section-title" },
      h("h2", {}, "Who told us what?"),
      h("span", { class: "sub" }, liveLook ? `${list.length} platforms and records, each with what it returned` : `${plural(list.length, "source")} wrote the ${plural(total, "event")} drawn here; Tools counts all ${Object.values((m.header.rollup || {}).event_type || {}).reduce((a, b) => a + b, 0)} in the log`),
      h("span", { class: "right" }, liveLook ? "times in UTC" : "times are COLLECTED, on the runner's clock, UTC")),
    h("div", { class: "chiprow", css: { padding: "0 0 16px" } }, list.map((s) => h("a", {
      class: "chip", href: `#sources`, onclick: (e) => { e.preventDefault(); document.getElementById(`src-${s.producer}`).scrollIntoView({ behavior: "smooth", block: "start" }); },
    }, h("span", { class: "type", "aria-hidden": "true" }, s.role.mono), who(s.producer), h("span", { class: "note" }, String(s.events.length))))),
    h("div", { class: "feed-note", "data-search-note": "" }),
    ctx.missing("lineage") ? h("p", { class: "muted" }, "Some events' lineage did not load, so a feed below may be short. Retry at the top of the page.") : "",
    h("div", { class: "sources" }, list.map((s) => sourceCard(ctx, s))),
    h("p", { class: "faint" }, "A source here is a producer in the log: the connector that collected, the matcher that proposed, the analyst who decided, the gate that permitted, and the runner. Two sources that agree are shown as two sources; nothing here measures whether they are independent."));
}

import { who } from "../lib/words.js";
import { liveLook } from "../lib/api.js";
