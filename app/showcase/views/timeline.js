// Timeline, the CHRONOLOGY (design 3.3, the 11-02 idiom): one lane per kind of
// actor across the case's window, a mark per minute with its count, the
// verified coverage drawn as a band, and below it the minutes opened like a
// calendar day. Every time is COLLECTED on the runner's clock, in UTC: no
// claim here carries a platform time, and the page says so. A third card
// lists the dates that govern the case, each from the server's own text.

import { h, tok, lin } from "../lib/dom.js";
import { timeline } from "../lib/model.js";
import { describe } from "../lib/describe.js";
import { eventLabel, roleOf, hm, stamp, day, short, plural, who } from "../lib/words.js";
import { liveLook } from "../lib/api.js";

const LANES = [
  { key: "auth", name: "Authorization", sub: "the human act", test: (e) => e.type === "AUTHORIZE_EVENT" },
  { key: "gate", name: "Subject gate", sub: "what may run", test: (e) => e.type === "COLLECT_EVENT" },
  { key: "run", name: "Collection", sub: "runs and items", test: (e) => e.type === "PROBE_EVENT" },
  { key: "claim", name: "Extraction", sub: "claims", test: (e) => e.type === "EXTRACT_EVENT" },
  { key: "match", name: "Matching", sub: "proposals", test: (e) => e.type === "LINK_EVENT" },
  { key: "analyst", name: "Analyst", sub: "assertions and acts", test: (e) => ["IDENTITY_EVENT", "ADJUDICATE_EVENT", "ASSESS_EVENT"].includes(e.type) },
  { key: "system", name: "System", sub: "watchdog and sweep", test: (e) => e.type === "SYSTEM_EVENT" },
];

// A mark's unit grows with the case's span, so months of posts draw as days or weeks rather than
// as hundreds of thousands of minute marks: the smallest unit that keeps the span within 240 marks.
const UNITS = [
  { ms: 60000, name: "minute", label: (d) => `${pad(d.getUTCHours())}:${pad(d.getUTCMinutes())}Z` },
  { ms: 3600000, name: "hour", label: (d) => `${d.toISOString().slice(5, 10)} ${pad(d.getUTCHours())}Z` },
  { ms: 86400000, name: "day", label: (d) => d.toISOString().slice(0, 10) },
  { ms: 604800000, name: "week", label: (d) => d.toISOString().slice(0, 10) },
];

function pad(n) {
  return String(n).padStart(2, "0");
}

function msOf(ts) {
  const d = new Date(ts);
  return Number.isNaN(d.getTime()) ? null : d.getTime();
}

// The live presentation draws one lane per source, each holding the posts and records it returned,
// and one for the analyst, so behavior over time reads by platform.
function liveLanes(m) {
  const items = (e) => e.type === "PROBE_EVENT" && e.subtype === "ITEM";
  const producers = [...new Set([...m.events.values()].filter(items).map((e) => e.producer))].sort((a, b) => who(a).localeCompare(who(b)));
  return producers.map((p) => ({ key: `src-${p}`, name: who(p), sub: "posts and records", test: (e) => e.producer === p && items(e) }))
    .concat([{ key: "analyst", name: "Analyst", sub: "assertions and notes", test: (e) => ["IDENTITY_EVENT", "ADJUDICATE_EVENT", "ASSESS_EVENT"].includes(e.type) }]);
}

function liveDates(ctx) {
  const m = ctx.model;
  return [...m.events.values()].filter((e) => (e.type === "ADJUDICATE_EVENT" && e.subtype === "NOTE") || e.type === "ASSESS_EVENT")
    .sort((a, b) => String(a.ts).localeCompare(String(b.ts)))
    .map((e) => { const d = describe(m, e); return { d: stamp(e.ts), w: d.title, s: d.body, id: e.event_id, what: "this record" }; });
}

function minuteOf(ts) {
  const d = new Date(ts);
  return Number.isNaN(d.getTime()) ? null : Math.floor(d.getTime() / 60000);
}

function clockOf(minute) {
  const d = new Date(minute * 60000);
  return `${String(d.getUTCHours()).padStart(2, "0")}:${String(d.getUTCMinutes()).padStart(2, "0")}Z`;
}

function dates(ctx) {
  const m = ctx.model;
  const out = [];
  const auth = [...m.events.values()].filter((e) => e.type === "AUTHORIZE_EVENT").sort((a, b) => String(a.ts).localeCompare(String(b.ts)));
  for (const a of auth) {
    out.push({ d: stamp(a.ts), w: `${eventLabel(a.type, a.subtype)}: ${(a.summary || []).join(" · ")}`, s: "from the authorization's own event", id: a.event_id });
  }
  const anc = /anchor_ts (\S+)/.exec(m.header.anchor || "");
  if (anc) out.push({ d: stamp(anc[1]), w: "The retention clock's anchor: the case's first event", s: m.header.anchor, rule: "U-02" });
  const exp = [...m.claims.values()].map((c) => c.expiry).filter((x) => /^past retain_until/.test(x || ""));
  if (exp.length) {
    const first = exp[0];
    const when = (/expired (\S+)/.exec(first) || [])[1];
    out.push({ d: when ? stamp(when) : "", w: `Claims' readings expired: ${exp.length} of ${m.claims.size} claims say past retain_until`, s: first, novouch: !!m.header.retention_vouch });
  }
  const sw = m.header.sweep || {};
  if (sw.ran) out.push({ d: stamp(sw.ran), w: "The retention sweep's last heartbeat", s: sw.text, novouch: !!sw.vouch, rule: "RT-12" });
  if (sw.next_due) out.push({ d: stamp(sw.next_due), w: sw.vouch ? "The sweep was next due, and has not run since" : "The sweep is next due", s: "read from the heartbeat's own next_due, with no grace", novouch: !!sw.vouch, rule: "RT-12" });
  return out.sort((a, b) => a.d.localeCompare(b.d));
}

export async function renderTimeline(el, ctx) {
  const m = ctx.model;
  const st = ctx.state;
  const all = timeline(m).filter((e) => msOf(e.ts) !== null);
  const LANE_SET = liveLook ? liveLanes(m) : LANES;
  const listed = liveLook ? all.filter((e) => LANE_SET.some((l) => l.test(e))) : all;
  const events = listed.length ? listed : all;
  if (!events.length) { el.append(h("div", { class: "card card-b muted" }, ctx.missing("lineage") ? "No dated event arrived: the lineage did not load. Retry at the top of the page." : "No dated event is held for this case.")); return; }
  const t0 = msOf(events[0].ts);
  const unit = UNITS.find((u) => (msOf(events[events.length - 1].ts) - t0) / u.ms <= 240) || UNITS[UNITS.length - 1];
  const minuteOf = (ts) => { const t = msOf(ts); return t === null ? null : Math.floor(t / unit.ms); };
  const clockOf = (b) => unit.label(new Date(b * unit.ms));
  const m0 = minuteOf(events[0].ts) - 1;
  const m1 = minuteOf(events[events.length - 1].ts) + 1;
  const span = Math.max(1, m1 - m0);
  const pct = (minute) => `${((minute - m0) / span) * 100}%`;
  const step = Math.max(1, Math.ceil(span / 8));
  const ticks = [];
  for (let t = Math.ceil(m0 / step) * step; t <= m1; t += step) ticks.push(t);
  const byMinute = new Map();
  for (const e of events) {
    const k = minuteOf(e.ts);
    if (!byMinute.has(k)) byMinute.set(k, []);
    byMinute.get(k).push(e);
  }
  const sel = st.minute && byMinute.has(st.minute) ? st.minute : null;
  const pick = (minute) => {
    st.minute = minute;
    ctx.select(st.selected);
    requestAnimationFrame(() => {
      const target = document.getElementById(`min-${minute}`);
      if (target) target.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  };
  const axis = h("div", { class: "tl-axis" }, h("div", {}),
    h("div", { class: "scale" }, ticks.map((t) => h("span", { class: "tick", css: { left: pct(t) } }, clockOf(t)))));
  const lanes = LANE_SET.map((lane) => {
    const mine = events.filter(lane.test);
    const counts = new Map();
    for (const e of mine) counts.set(minuteOf(e.ts), (counts.get(minuteOf(e.ts)) || 0) + 1);
    const track = h("div", { class: "track" });
    if (lane.key === "run") {
      for (const c of m.coverage) {
        // The coverage route's three texts: verified ... from A to B by M, UNVERIFIED span ... from A to B:, OPEN ... coverage after A is unproven.
        const open = /^OPEN/.test(c.text);
        const verified = /^verified/.test(c.text);
        const a = minuteOf(open ? (/after (\S+) is unproven/.exec(c.text) || [])[1] : (/from (\S+) to/.exec(c.text) || [])[1]);
        const b = open ? m1 : minuteOf((/ to (\S+)(?: by |: )/.exec(c.text) || [])[1]);
        if (a === null || b === null) continue;
        const lo = Math.max(a, m0);
        const hi = Math.min(b, m1);
        if (hi <= lo) continue;
        const method = (/ by (\S+),/.exec(c.text) || [])[1];
        track.append(h("button", {
          class: verified ? "tl-band" : "tl-gap", type: "button", title: c.text, css: { left: pct(lo), width: `${((hi - lo) / span) * 100}%` },
          onclick: () => c.lineage ? ctx.lineage(c.lineage, "coverage interval") : null,
        }, verified ? `verified coverage · ${short(c.target_ref)}${method ? ` · by ${method}` : ""}` : h("span", {}, c.text.split(":")[0])));
      }
    }
    for (const [minute, n] of counts) {
      const first = mine.find((e) => minuteOf(e.ts) === minute);
      const layer = first.type === "LINK_EVENT" ? "inf" : first.type === "ASSESS_EVENT" ? "state" : "";
      track.append(h("button", {
        class: ["tl-mark", layer], type: "button", "aria-pressed": String(sel === minute),
        title: `${lane.name} · ${clockOf(minute)} · ${plural(n, "event")}`, css: { left: pct(minute) },
        onclick: () => pick(minute),
      }, String(n)));
    }
    return h("div", { class: "tl-lane" }, h("div", { class: "name" }, lane.name, h("small", {}, `${lane.sub} · ${mine.length}`)), track);
  });
  const minutes = [...byMinute.entries()].sort((a, b) => a[0] - b[0]).map(([minute, list]) => h("div", { class: ["minute", sel === minute && "sel"], id: `min-${minute}` },
    h("div", { class: "clock" }, clockOf(minute), h("small", {}, `${day(list[0].ts)} · ${plural(list.length, "event")}`)),
    h("div", { class: "rows" }, list.map((e) => {
      const d = describe(m, e);
      const role = roleOf(e.producer);
      return h("div", { class: "row", "data-search": `${d.title} ${who(e.producer)}` },
        h("span", { class: ["avatar", role.key === "analyst" && "analyst"], css: { width: "30px", height: "30px", "font-size": "10.5px", "border-radius": role.key === "analyst" ? "50%" : "8px" }, "aria-hidden": "true" }, role.mono),
        h("div", { class: "grow" }, h("div", {}, h("b", {}, d.title), h("span", { class: "faint" }, ` · ${who(e.producer)}`)), h("div", { class: "faint" }, d.body)),
        lin(() => ctx.lineage(e.event_id, d.title), d.title));
    }))));
  el.append(
    h("div", { class: "section-title" },
      h("h2", {}, "What happened when, and when were we watching?"),
      h("span", { class: "sub" }, `${liveLook ? ((n) => `${n} ${n === 1 ? "post or record" : "posts and records"}`)(events.filter((e) => e.type === "PROBE_EVENT" && e.subtype === "ITEM").length) : plural(events.length, "event")} · ${stamp(events[0].ts)} to ${unit.ms >= 86400000 ? stamp(events[events.length - 1].ts) : hm(events[events.length - 1].ts)}`),
      h("span", { class: "right" }, liveLook ? `one mark per ${unit.name}, UTC` : "COLLECTED on the runner's clock, UTC")),
    h("section", { class: "card" },
      h("div", { class: "tl" }, axis, lanes),
      h("div", { class: "card-foot" }, h("div", { class: "tokens" },
        liveLook ? null : tok("every time is COLLECTED: no claim in this case carries a platform time"),
        tok(`a number on a mark is how many ${liveLook ? "posts or records" : "events"} fell in that ${unit.name}`),
        tok(m.coverage.length ? "a band is a coverage interval in the server's words; where none is drawn, none is recorded" : "no coverage interval is recorded for this case")))),
    h("div", { class: "cols", css: { "margin-top": "18px" } },
      h("section", { class: "card" },
        h("div", { class: "card-h" }, h("h2", {}, liveLook ? "What changed, and when" : "Dates that govern this case")),
        h("div", { class: "card-b" }, h("div", { class: "dates", css: { "grid-template-columns": "minmax(0, 1fr)" } }, (liveLook ? liveDates(ctx) : dates(ctx)).map((x) => h("div", { class: ["date", x.novouch && "novouch"] },
          h("div", { class: "d" }, x.d, x.rule ? h("span", { class: "tok", css: { "margin-left": "8px" } }, x.rule) : null),
          h("div", { class: "w" }, x.w), h("div", { class: "s" }, x.s), x.id ? h("div", { css: { "margin-top": "6px" } }, lin(() => ctx.lineage(x.id, x.what || "authorization"), x.what || "the authorization")) : null))))),
      h("section", { class: "card" },
        h("div", { class: "card-h" }, h("h2", {}, `${unit.name[0].toUpperCase()}${unit.name.slice(1)} by ${unit.name}`), h("span", { class: "sub" }, "opened, oldest first")),
        h("div", { class: "feed-note", "data-search-note": "" }),
        minutes)));
}
