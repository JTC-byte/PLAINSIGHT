// Overview, the DOSSIER as a profile page (design 3.1, the 11-02 idiom). On the
// left, what the case holds about this account, one layer per card in the
// design's order read from the bottom up: the observations (About), the
// analyst's identity assertions (Identity), the exclusions, and the machine's
// proposals that no analyst accepted. On the right, what was learned, newest
// first: a snapshot, never ranked, every card opening its lineage.

import { h, tok, lin } from "../lib/dom.js";
import { selectorLabel, selectorChip, SEAMS, BAND, roleOf, stamp, hm, day, short, plural, isPlaceholder, PLACEHOLDER_NOTE } from "../lib/words.js";
import { timeline, sources } from "../lib/model.js";
import { describe, searchText } from "../lib/describe.js";

function bandObj(model, name) {
  return model.dossier ? model.dossier.bands.find((x) => x.band === name) || null : null;
}

function band(model, name) {
  const b = bandObj(model, name);
  return b ? b.rows : [];
}

function waits(ctx, part, what) {
  return ctx.missing(part) ? h("div", { class: "card-b muted" }, `${what} waits for ${part === "dossier" ? "the dossier" : "the lineage"}, which did not load. Retry at the top of the page.`) : null;
}

function commonOf(rows) {
  if (!rows.length) return [];
  return (rows[0].vouch_tokens || []).filter((t) => rows.every((r) => (r.vouch_tokens || []).includes(t)));
}

/** A server provenance line, split into its parts with the clock named. */
function provenanceParts(row, claim) {
  const parts = String(row.provenance || "").split(" · ");
  const out = [];
  for (const p of parts) {
    if (p.startsWith("time ")) {
      const prov = p.slice(5);
      out.push(prov === "collection_time"
        ? `COLLECTED ${claim && claim.observed_at ? stamp(claim.observed_at) : ""} on the runner's clock · platform time not reported`.replace("  ", " ")
        : `time ${prov}`);
    } else out.push(p);
  }
  return out;
}

function nodeWords(model, id) {
  if (id === model.focus) return "this account";
  const n = model.nodes.get(id);
  if (!n) return `node ${short(id)}`;
  if (n.kind === "referenced") return "a referenced person, no observation held";
  if (n.kind === "candidate") return "a candidate person";
  return (n.lines || [])[0] || n.kind;
}

function about(ctx) {
  const m = ctx.model;
  const rows = band(m, "OBSERVATION");
  const common = commonOf(rows);
  const facts = rows.map((r) => {
    const claim = m.claims.get(r.claim_id) || {};
    const item = claim.item_id ? m.items.get(claim.item_id) : null;
    const own = (r.vouch_tokens || []).filter((t) => !common.includes(t));
    const parts = provenanceParts(r, claim);
    const review = parts.find((p) => /^(verified|disputed|unreviewed)/.test(p));
    const extracted = parts.find((p) => p.startsWith("extracted by "));
    const when = parts.find((p) => p.startsWith("COLLECTED") || p.startsWith("time "));
    const relation = parts.find((p) => p.startsWith("relation "));
    const other = parts.filter((p) => ![review, extracted, when, relation].includes(p));
    const disputed = /^disputed/.test(review || "");
    const from = [who(claim.producer), item && item.locator ? `item ${item.locator}` : null, extracted ? extracted.replace("@", " ") : null].filter(Boolean).join(" · ");
    return h("div", { class: "fact", "data-search": `${selectorLabel(r.selector_type)} ${r.value} ${r.provenance}` },
      h("div", { class: "k" }, selectorLabel(r.selector_type)),
      h("div", { class: "v" },
        h("span", { class: "type sm", "aria-hidden": "true" }, selectorChip(r.selector_type)),
        h("span", { class: r.generated ? "generated" : "" }, r.value),
        r.generated ? tok("generated, never observed") : null,
        isPlaceholder(r.value) ? h("span", { class: "tok", title: PLACEHOLDER_NOTE }, "placeholder value") : null,
        review ? tok(review.split(" ")[0], false, disputed) : null),
      lin(() => ctx.lineage(r.lineage, r.value), r.value),
      fold(h("dl", { class: "prov" },
        from ? [h("dt", {}, "From"), h("dd", {}, from)] : null,
        when ? [h("dt", {}, "When"), h("dd", {}, when)] : null,
        review ? [h("dt", {}, "Review"), h("dd", {}, disputed ? h("b", {}, review) : review)] : null,
        relation ? [h("dt", {}, "Relation"), h("dd", {}, relation.replace(/^relation /, ""))] : null,
        other.length ? [h("dt", {}, "Also"), h("dd", {}, other.join(" · "))] : null)),
      own.length && !liveLook ? h("div", { class: "tokens" }, own.map((t) => tok(t, true))) : null);
  });
  return h("section", { class: "card", "aria-label": "about this account" },
    h("div", { class: "card-h" }, h("h2", {}, "About"), h("span", { class: "sub" }, "observations about this account"), h("span", { class: "right" }, plural(rows.length, "claim"))),
    waits(ctx, "dossier", "This card") || (rows.length ? h("div", {}, facts) : h("div", { class: "card-b muted" }, (bandObj(m, "OBSERVATION") || {}).empty || "No claim is observed about this account.")),
    common.length && !liveLook ? h("div", { class: "card-foot" }, h("div", { class: "tokens" }, h("span", {}, "Every claim above:"), common.map((t) => tok(t, true)))) : null);
}

function sourcesCard(ctx) {
  const m = ctx.model;
  const list = sources(m, roleOf).filter((s) => !liveLook || s.role.key === "connector");
  if (!list.length) return null;
  return h("section", { class: "card", "aria-label": "sources" },
    h("div", { class: "card-h" }, h("h2", {}, "Sources"), h("span", { class: "sub" }, "who wrote what this page shows"), h("span", { class: "right" }, plural(list.length, "source"))),
    h("div", { class: "card-b" }, h("div", { class: "rows" }, list.map((s) => h("button", {
      class: "row srcrow", type: "button", title: `open ${s.producer}'s feed`,
      onclick: () => ctx.go("sources").then(() => { const t = document.getElementById(`src-${s.producer}`); if (t) t.scrollIntoView({ block: "start" }); }),
    },
    h("span", { class: ["avatar", s.role.key === "analyst" && "analyst"], css: { width: "32px", height: "32px", "font-size": "10.5px" }, "aria-hidden": "true" }, s.role.mono),
    h("div", { class: "grow" }, h("div", { class: "srcname" }, who(s.producer)), h("div", { class: "faint" }, s.role.word)),
    h("span", { class: "tok" }, plural(s.events.length, "event")))))),
    h("div", { class: "card-foot" }, "Two sources that agree stay two sources here. Nothing on this page measures whether they are independent."));
}

function identity(ctx) {
  const m = ctx.model;
  const rows = band(m, "FUSION");
  const items = rows.map((r) => {
    const bandWord = ((r.lines[0] || "").split(" · ")[1] || "").trim();
    const acts = [...m.adjudications.values()].filter((a) => a.target_ref === r.lineage);
    return h("div", { class: "mini layer-fus", "data-search": `${r.lines.join(" ")} ${acts.map((a) => a.text).join(" ")}` },
      h("div", { class: "mini-h" },
        h("span", { class: ["t", r.tombstone && "struck"] }, `Identity cluster ${short(r.cluster_id)}`),
        h("span", { class: "faint mono", title: "the event that asserted it, which the server's sentences name" }, `event ${short(r.lineage)}`),
        bandWord ? tok(BAND[bandWord] || bandWord, false, !r.tombstone) : null,
        r.tombstone ? tok("revoked") : null,
        lin(() => ctx.lineage(r.lineage, `cluster ${short(r.cluster_id)}`), "this cluster")),
      h("div", { class: "mini-b" }, r.lines.map((l) => h("div", {}, l))),
      h("div", { class: "members" }, r.members.map((mem) => h("div", { class: "member" },
        h("span", { class: "type sm", "aria-hidden": "true" }, mem.node_id === m.focus ? "ac" : "pp"),
        h("div", { class: "grow" },
          h("div", {}, nodeWords(m, mem.node_id)),
          h("div", { class: "faint" }, "seam ", ...mem.seams.split(",").map((code) => [h("span", { class: "seam", title: SEAMS[code.trim()] || code }, code.trim()), ` ${SEAMS[code.trim()] || code} `])))))),
      acts.length ? h("div", { class: "mini-b" }, acts.map((a) => h("div", { class: "faint" }, a.text))) : null);
  });
  return h("section", { class: "card", "aria-label": "identity" },
    h("div", { class: "card-h" }, h("h2", {}, "Identity"), h("span", { class: "sub" }, "asserted by an analyst, per member"), h("span", { class: "right" }, plural(rows.length, "cluster"))),
    waits(ctx, "dossier", "This card") || h("div", { class: "card-b" }, rows.length ? items : h("div", { class: "muted" }, (bandObj(m, "FUSION") || {}).empty || "No analyst has asserted a cluster holding this account.")),
    h("div", { class: "card-foot" }, "Seams are shown per member and never rolled up. A cluster is a lens over accounts; splitting it is a revocation, and the tombstone stays."));
}

function excluded(ctx) {
  const m = ctx.model;
  const cands = [...m.nodes.values()].filter((n) => n.kind === "candidate" && (n.lines || []).some((l) => l.startsWith("EXCLUDED")));
  if (!cands.length) return null;
  return h("section", { class: "card", "aria-label": "excluded" },
    h("div", { class: "card-h" }, h("h2", {}, "Not this person"), h("span", { class: "sub" }, "excluded, with a basis"), h("span", { class: "right" }, plural(cands.length, "candidate"))),
    h("div", { class: "card-b" }, cands.map((n) => h("div", { class: "mini layer-obs", "data-search": n.lines.join(" ") },
      h("div", { class: "mini-h" }, h("span", { class: "type sm", "aria-hidden": "true" }, "pp"), h("span", { class: "t struck" }, "Candidate person"), tok("excluded", false, true),
        lin(() => ctx.lineage(n.created_by_event_id, "the exclusion"), "the exclusion")),
      h("div", { class: "mini-b" }, n.lines.map((l) => h("div", {}, l)))))),
    h("div", { class: "card-foot" }, "An exclusion stays on screen, struck through. It is never hidden."));
}

function proposals(ctx) {
  const m = ctx.model;
  const rows = band(m, "INFERENCE");
  if (!rows.length) return null;
  const byOther = new Map();
  for (const r of rows) {
    if (!byOther.has(r.other)) byOther.set(r.other, []);
    byOther.get(r.other).push(r);
  }
  return h("section", { class: "card", "aria-label": "proposals" },
    h("div", { class: "card-h" }, h("h2", {}, liveLook ? "Associates and likely accounts" : "Proposed, not accepted"), h("span", { class: "sub" }, liveLook ? "suggested from shared signals; not yet confirmed by an analyst" : "a machine's suggestion, never a fact"), h("span", { class: "right" }, plural(rows.length, "proposal"))),
    h("div", { class: "card-b" }, [...byOther.entries()].map(([other, list]) => h("div", { class: "mini layer-inf", "data-search": list.map((r) => r.text).join(" ") },
      h("div", { class: "mini-h" }, h("span", { class: "t" }, liveLook ? nodeWords(m, other) : `Between this account and ${nodeWords(m, other)}`)),
      h("div", { class: "rows" }, list.map((r) => {
        const pred = (/PROPOSED (\S+)/.exec(r.text) || [])[1] || "proposal";
        return h("div", { class: "row" }, h("span", { class: "tok strong" }, pred.replaceAll("_", " ")),
          h("div", { class: "grow" }, liveText(r.text.replace(/^NOT ACCEPTED, PROPOSED \S+ /, ""))), lin(() => ctx.lineage(r.lineage, pred), "this proposal"));
      }))))),
    h("div", { class: "card-foot" }, "Dashed means inference and nothing else. A proposal becomes part of the picture only when an analyst asserts it."));
}

function feed(ctx) {
  const m = ctx.model;
  const events = timeline(m).reverse().filter((e) => !liveLook || roleOf(e.producer).key === "connector");
  const groups = [];
  for (const e of events) {
    const key = `${day(e.ts)} ${hm(e.ts)}`;
    if (!groups.length || groups[groups.length - 1].key !== key) groups.push({ key, ts: e.ts, events: [] });
    groups[groups.length - 1].events.push(e);
  }
  const post = (e) => {
    const role = roleOf(e.producer);
    const d = describe(m, e);
    const layer = e.type === "LINK_EVENT" ? "inf" : e.type === "IDENTITY_EVENT" ? "fus layer-fus" : e.type === "ASSESS_EVENT" ? "state" : "";
    const node = h("article", { class: "post" },
      h("div", { class: ["avatar", role.key === "analyst" && "analyst", layer], "aria-hidden": "true" }, role.mono),
      h("div", {},
        h("div", { class: "who" }, h("span", { class: "src" }, who(e.producer)), h("span", { class: "when" }, `${d.title} · ${hm(e.ts)}`)),
        h("div", { class: "what" }, d.body),
        d.lines.length ? h("div", { class: "lines" }, d.lines.map((l) => h("div", {}, l))) : null,
        d.tokens.length ? h("div", { class: "tokens" }, d.tokens) : null),
      lin(() => ctx.lineage(e.event_id, d.title), d.title));
    node.dataset.search = searchText(node);
    return node;
  };
  const posts = [];
  for (const g of groups) {
    posts.push(h("div", { class: "feed-time" }, `${day(g.ts)} · ${hm(g.ts)}`));
    // A burst from one source in one minute folds into one card with its counts;
    // every item stays one click down and is never dropped.
    const runs = [];
    for (const e of g.events) {
      const last = runs[runs.length - 1];
      if (last && last.producer === e.producer) last.events.push(e); else runs.push({ producer: e.producer, events: [e] });
    }
    for (const r of runs) {
      if (r.events.length < 4) { r.events.forEach((e) => posts.push(post(e))); continue; }
      const role = roleOf(r.producer);
      const counts = new Map();
      for (const e of r.events) { const t = describe(m, e).title.toLowerCase(); counts.set(t, (counts.get(t) || 0) + 1); }
      posts.push(h("details", { class: "fold" },
        h("summary", { class: "post" },
          h("div", { class: ["avatar", role.key === "analyst" && "analyst"], "aria-hidden": "true" }, role.mono),
          h("div", {},
            h("div", { class: "who" }, h("span", { class: "src" }, who(r.producer)), h("span", { class: "when" }, `${plural(r.events.length, "event")} · ${hm(g.ts)}`)),
            h("div", { class: "what" }, [...counts.entries()].map(([t, n]) => (n > 1 ? `${t} ×${n}` : t)).join(" · ")),
            h("div", { class: "lines" }, "Folded so the minute reads as one act of work. Open it for each event and its lineage.")),
          h("span", { class: "fold-mark", "aria-hidden": "true" }, "▾")),
        r.events.map((e) => post(e))));
    }
  }
  const first = events.length ? events[events.length - 1].ts : null;
  const last = events.length ? events[0].ts : null;
  return h("section", { class: "card", "aria-label": "what we have learned" },
    h("div", { class: "card-h" }, h("h2", {}, "What we have learned"), h("span", { class: "sub" }, "newest first · nothing is ranked"),
      h("span", { class: "right" }, events.length ? `${plural(events.length, "event")} · ${stamp(first)} to ${hm(last)}` : "")),
    h("div", { class: "feed-note", "data-search-note": "" }),
    ctx.missing("lineage") ? h("div", { class: "feed-note" }, "Some events' lineage did not load, so this feed may be short. Retry at the top of the page.") : null,
    posts.length ? posts : h("div", { class: "card-b muted" }, ctx.missing("lineage") ? "No event arrived." : "No event is held for this case."),
    h("div", { class: "feed-note" }, `The feed is a snapshot of the store, read at ${m.loadedAt.toLocaleTimeString()}; it never moves under you. Every card opens its lineage. Times are COLLECTED, on the runner's clock, in UTC. System events the authorization does not reach are counted under Tools.`));
}

export async function renderOverview(el, ctx) {
  el.append(h("div", { class: "cols" },
    h("div", { class: "stack" }, about(ctx), sourcesCard(ctx), identity(ctx), excluded(ctx), proposals(ctx)),
    h("div", { class: "stack" }, feed(ctx))));
}

import { liveLook } from "../lib/api.js";

/** In the live presentation a claim's provenance rows fold behind one toggle. */
function fold(dl) {
  return liveLook ? h("details", { class: "provfold" }, h("summary", {}, "Provenance"), dl) : dl;
}

import { who } from "../lib/words.js";

/** A proposal's text as the live presentation prints it: without the matcher's tool name and the calibration note. */
function liveText(text) {
  return liveLook ? String(text).replace(/^by \S+ [\d.]+: /, "").replace(/\s*·\s*no analyst has asserted this\s*·\s*uncalibrated\s*$/, "") : text;
}
