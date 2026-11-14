// The case model the showcase draws from: one person at the centre, and every
// source's selectors, items, proposals, assertions and acts consolidated
// around them. Everything here is read through the existing GET routes:
//
//   header       the case strip's states (EG-1, RT-11, RT-12, retention, U-02)
//   dossier      the four layers about the seed: STATE, FUSION, INFERENCE, OBSERVATION
//   web          the nodes and edges within three hops of the seed
//   node/<id>    each node's claims, edges, adjudications and pre-flight
//   lineage      each chain, and forward from the authorization, which reaches
//                every event the authorization made collectable
//   coverage     the coverage intervals
//
// Nothing is computed about a person: no score, no weight, no ranking. Counts
// are counts of what the server returned, and every text is the server's.

import { getJSON, need } from "./api.js";

/** The words the page uses for each part of the load that can fail to arrive. */
export const PARTS = {
  coverage: "the coverage intervals",
  dossier: "the dossier",
  web: "the web",
  nodes: "some nodes' details",
  lineage: "some events' lineage",
};

/** A GET whose failure to arrive is recorded against a part of the page; a refusal is an answer, not a gap. */
function reader(model) {
  return async (url, part) => {
    const r = await getJSON(url);
    if (r.ok) return r.body;
    if (r.dropped && part) model.missing.add(part);
    return null;
  };
}

function byTime(a, b) {
  return String(a.ts).localeCompare(String(b.ts)) || ORDER(a) - ORDER(b) || String(a.event_id).localeCompare(String(b.event_id));
}

const TYPE_ORDER = ["AUTHORIZE_EVENT", "COLLECT_EVENT", "PROBE_EVENT", "EXTRACT_EVENT", "LINK_EVENT", "IDENTITY_EVENT", "ADJUDICATE_EVENT", "ASSESS_EVENT", "SYSTEM_EVENT"];
function ORDER(e) {
  const i = TYPE_ORDER.indexOf(e.type);
  return i < 0 ? 99 : i;
}

export async function listCases() {
  return need("/api/cases");
}

export async function loadCase(caseId) {
  const base = `/api/cases/${caseId}`;
  const header = await need(`${base}/header`);
  const focus = header.seed_focus;
  const model = {
    caseId, base, header, focus,
    dossier: null, web: null, overCap: null, coverage: [],
    nodes: new Map(), edges: [], events: new Map(),
    claims: new Map(), items: new Map(), runs: new Map(),
    adjudications: new Map(), edgeText: new Map(), decisions: new Map(),
    anchorClaim: null, promote: null, grants: [], loadedAt: new Date(), missing: new Set(),
  };
  const maybe = reader(model);
  const coverage = await maybe(`${base}/coverage`, "coverage");
  model.coverage = coverage ? coverage.intervals : [];
  if (!focus) return model;

  const [dossier, web] = await Promise.all([maybe(`${base}/dossier?focus=${focus}`, "dossier"), maybe(`${base}/web?focus=${focus}&hops=3`, "web")]);
  model.dossier = dossier;
  if (web && web.mode === "web") {
    model.web = web;
    model.edges = web.edges;
  } else if (web) {
    model.overCap = web;
  }
  const webNodes = model.web ? model.web.nodes : [];
  const inspected = await Promise.all(webNodes.map((n) => maybe(`${base}/node/${n.node_id}`, "nodes")));
  webNodes.forEach((n, i) => model.nodes.set(n.node_id, { ...n, inspect: inspected[i] }));

  for (const e of model.edges) model.edgeText.set(e.event_id, e);
  for (const n of model.nodes.values()) {
    const d = n.inspect;
    if (!d) continue;
    for (const a of d.adjudications || []) model.adjudications.set(a.event_id, a);
    for (const e of d.edges || []) if (!model.edgeText.has(e.event_id)) model.edgeText.set(e.event_id, e);
    for (const u of d.unattached_decisions || []) model.decisions.set(u.event_id, u);
    for (const c of d.claims || []) model.claims.set(c.claim_id, { ...c, node_id: n.node_id });
  }

  // The seed's own chain names its anchor claim and the authorization above it.
  const focusNode = model.nodes.get(focus);
  const head = focusNode && focusNode.lineage_heads ? focusNode.lineage_heads[0] : null;
  const headChain = head ? await maybe(`${base}/lineage/${head}`, "lineage") : null;
  if (headChain) {
    model.promote = headChain;
    const p = headChain.envelope && headChain.envelope.payload ? headChain.envelope.payload : {};
    model.anchorRef = p.anchor_claim_ref || null;
    model.anchorType = p.anchor_selector_type || null;
    for (const c of headChain.chain) add(model, c);
    model.grants = headChain.chain.filter((c) => c.type === "AUTHORIZE_EVENT" && c.subtype === "GRANT");
  }
  for (const g of model.grants) {
    const fwd = await maybe(`${base}/lineage/${g.event_id}?dir=forward`, "lineage");
    if (fwd) for (const c of fwd.chain) add(model, c);
  }
  // Events no authorization reaches: each node's own lineage heads, the gate's
  // decisions that name no authorization, and the closing events of coverage.
  const extra = new Set();
  for (const n of model.nodes.values()) for (const id of n.lineage_heads || []) extra.add(id);
  for (const id of model.decisions.keys()) extra.add(id);
  for (const c of model.coverage) if (c.lineage) extra.add(c.lineage);
  const missing = [...extra].filter((id) => !model.events.has(id));
  const chains = await Promise.all(missing.map((id) => maybe(`${base}/lineage/${id}`, "lineage")));
  chains.forEach((ch) => { if (ch && ch.chain && ch.chain[0]) add(model, ch.chain[0]); });

  // The decoded envelope of each item, claim and run end: the locator, the
  // value, the run's outcome. These are the head of their own back chain.
  const decode = [...model.events.values()].filter((e) =>
    (e.type === "PROBE_EVENT" && (e.subtype === "ITEM" || e.subtype === "RUN_END" || e.subtype === "RUN_START")) ||
    (e.type === "EXTRACT_EVENT"));
  const decoded = await Promise.all(decode.map((e) => maybe(`${base}/lineage/${e.event_id}`, "lineage")));
  decode.forEach((e, i) => {
    const d = decoded[i];
    if (!d) return;
    e.envelope = d.envelope || null;
    e.raw = d.raw || null;
    e.raw_vouch = !!d.raw_vouch;
    e.flags = d.flags || [];
  });
  for (const e of model.events.values()) {
    const p = e.envelope && e.envelope.payload ? e.envelope.payload : null;
    if (!p) continue;
    if (e.subtype === "ITEM") model.items.set(e.event_id, { event: e, locator: p.locator, outcome: p.outcome, run_id: p.run_id });
    if (e.subtype === "RUN_START") model.runs.set(p.run_id, { start: e, payload: p, end: null, items: [] });
  }
  for (const e of model.events.values()) {
    const p = e.envelope && e.envelope.payload ? e.envelope.payload : null;
    if (p && e.subtype === "RUN_END" && model.runs.has(p.run_id)) model.runs.get(p.run_id).end = { event: e, payload: p };
  }
  for (const it of model.items.values()) if (model.runs.has(it.run_id)) model.runs.get(it.run_id).items.push(it);

  // Claims no web node holds, such as one from an ignored item, are still the
  // case's: their node is read where the projection serves one.
  const claimEvents = [...model.events.values()].filter((e) => e.type === "EXTRACT_EVENT");
  const unseen = claimEvents.filter((e) => !model.claims.has(e.event_id));
  const more = await Promise.all(unseen.map((e) => maybe(`${base}/node/${e.event_id}`, "nodes")));
  unseen.forEach((e, i) => {
    const d = more[i];
    const own = d && d.claims ? d.claims.find((c) => c.claim_id === e.event_id) : null;
    const p = e.envelope && e.envelope.payload ? e.envelope.payload : {};
    model.claims.set(e.event_id, own ? { ...own, node_id: d.node.node_id, offWeb: true } : {
      claim_id: e.event_id, selector_type: p.selector_type, value: p.value, generated: p.selector_type === "email_generated_permutation",
      item_id: p.source_ref ? p.source_ref.item_id : null, review: null, raw: null, expiry: null, relation: null, offWeb: true,
    });
    if (d) for (const a of d.adjudications || []) model.adjudications.set(a.event_id, a);
  });
  for (const c of model.claims.values()) {
    const ev = model.events.get(c.claim_id);
    c.event = ev || null;
    const p = ev && ev.envelope ? ev.envelope.payload : null;
    c.extractor = p && p.extractor ? `${p.extractor.name} ${p.extractor.version}` : null;
    c.observed_at = p && p.temporal ? p.temporal.observed_at : null;
    c.time_provenance = p && p.temporal ? p.temporal.time_provenance : null;
    c.source_path = p && p.source_ref ? p.source_ref.source_path : null;
    c.producer = ev ? ev.producer : null;
  }
  model.anchorClaim = model.anchorRef ? model.claims.get(model.anchorRef) || null : null;
  return model;
}

function add(model, c) {
  if (!c || !c.event_id) return;
  const had = model.events.get(c.event_id);
  if (had) return;
  model.events.set(c.event_id, { ...c });
}

/** Every event, oldest first: the log order a feed reverses. */
export function timeline(model) {
  return [...model.events.values()].sort(byTime);
}

/** The case's sources, each the events one producer wrote, in a fixed role order. */
export function sources(model, roleOf) {
  const groups = new Map();
  for (const e of model.events.values()) {
    const key = e.producer || "unknown";
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(e);
  }
  return [...groups.entries()]
    .map(([producer, events]) => ({ producer, role: roleOf(producer), events: events.sort(byTime) }))
    .sort((a, b) => a.role.order - b.role.order || a.producer.localeCompare(b.producer));
}

/** The node a claim, item, cluster or event names, by any of the ids the server uses. */
export function nodeFor(model, id) {
  if (model.nodes.has(id)) return model.nodes.get(id);
  for (const n of model.nodes.values()) {
    if (n.created_by_event_id === id) return n;
    if ((n.lineage_heads || []).includes(id)) return n;
  }
  return null;
}

/** Tokens that every node carries are stated once for the whole web, never dropped. */
export function commonTokens(model) {
  const all = [...model.nodes.values()];
  if (!all.length) return [];
  return (all[0].vouch_tokens || []).filter((t) => all.every((n) => (n.vouch_tokens || []).includes(t)));
}
