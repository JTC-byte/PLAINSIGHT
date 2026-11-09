// Analyst acts (slice 3, docs/PLAINSIGHT-design.md amendments 9.16 and 9.17).
//
// Every act is one POST to /api/cases/<case>/acts with a closed body; the server
// mints the envelope under the session's identity and sends it through the door.
// Nothing here writes to the store, and the client keeps no case material.
//
// Undo is a cancel window (amendment 9.17): a single-key disposition is queued
// for ten seconds with its consequence shown and nothing recorded; Backspace
// cancels it; on expiry it is sent. After that the model offers no reversal
// except REVOKE of a PROMOTE, a CLUSTER, an EXCLUDE or a SAME_ENTITY link. The
// Merge Sheet commits on its own button and is not queued: a modal confirmed by
// hand is not a slip.
//
// The review strip (design 4.5) appears before a claim is used for something
// load-bearing: as a merge basis in the Merge Sheet, or as the motivating claim
// in the Pivot Bar. Citation into DRAFT is not in this slice.

import { el, getJSON, sendJSON, say, state } from "../app.js";

export const UNDO_WINDOW_MS = 10000;

let pending = null;

function host() {
  return document.getElementById("inspector");
}

export async function sendAct(body, caseId = state.caseId) {
  const r = await sendJSON("POST", `/api/cases/${caseId}/acts`, body);
  if (r.ok) say(`recorded ${r.body.recorded.slice(0, 8)}: ${r.body.consequence}`);
  else say(r.body ? `${r.body.text}${r.body.detail ? " " + r.body.detail : ""}` : "the act could not be sent");
  return r;
}

export function cancelPending() {
  if (!pending) { say("nothing is queued: Backspace cancels an act within ten seconds of pressing its key"); return false; }
  clearTimeout(pending.timer);
  if (pending.box) pending.box.remove();
  say(`${pending.label} cancelled: nothing was recorded`);
  pending = null;
  return true;
}

export function flushPending() {
  if (!pending) return Promise.resolve(null);
  const p = pending;
  clearTimeout(p.timer);
  pending = null;
  if (p.box) p.box.remove();
  return sendAct(p.body, p.caseId).then((r) => { if (p.done) p.done(r); return r; });
}

// Queue one act for the undo window, with its consequence shown. The case is the
// one open when the key was pressed. A second act queued while one waits sends the
// first at once. Leaving the page inside the window cancels the act: nothing was
// recorded, and the status line says so on the way out.
export function queueAct(label, body, consequence, done) {
  if (pending) flushPending();
  const box = el("div", { class: "toast", role: "status" },
    el("div", {}, `${label} queued · Backspace within ten seconds cancels · nothing recorded yet`),
    el("div", { class: "consequence" }, consequence));
  host().prepend(box);
  const timer = setTimeout(() => { if (pending && pending.timer === timer) flushPending(); }, UNDO_WINDOW_MS);
  pending = { label, body, caseId: state.caseId, timer, box, done };
}

window.addEventListener("pagehide", () => { if (pending) { clearTimeout(pending.timer); pending = null; } });

// An inline form in the INSPECTOR: no modal, Enter submits, Escape cancels.
export function inlineForm(title, fields, onSubmit) {
  const inputs = {};
  const form = el("form", { class: "card act-form" }, el("h3", {}, title));
  for (const f of fields) {
    const input = f.kind === "select"
      ? el("select", { name: f.name }, ...f.options.map((o) => el("option", { value: o }, o)))
      : el(f.kind === "textarea" ? "textarea" : "input", { name: f.name, type: "text", placeholder: f.placeholder || "", maxlength: 2000 });
    inputs[f.name] = input;
    form.append(el("label", {}, `${f.label} `, input));
  }
  const cancel = () => { form.remove(); say("cancelled: nothing was recorded"); };
  form.append(el("div", {},
    el("button", { type: "submit" }, "⏎ record"), " ",
    el("button", { type: "button", onclick: cancel }, "esc cancel")));
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const values = Object.fromEntries(Object.entries(inputs).map(([k, v]) => [k, v.value.trim()]));
    form.remove();
    onSubmit(values);
  });
  form.addEventListener("keydown", (e) => { if (e.key === "Escape") { e.preventDefault(); cancel(); } e.stopPropagation(); });
  host().prepend(form);
  const first = form.querySelector("input, textarea, select");
  if (first) first.focus();
  return form;
}

// The review strip before a claim is used for something load-bearing (design 4.5).
export function reviewStrip(claim, inCourseOf, onDone) {
  const strip = el("div", { class: "strip" },
    el("div", {}, `REVIEW BEFORE ${inCourseOf.replace("_", " ").toUpperCase()} · claim ${claim.claim_id.slice(0, 8)} · ${claim.selector_type}`),
    el("div", {}, claim.review));
  const verify = el("button", {
    onclick: async () => {
      const r = await sendAct({ act: "VERIFY", target: claim.claim_id, in_course_of: inCourseOf });
      strip.remove();
      if (onDone) onDone(r);
    },
  }, "⏎ verified");
  const dispute = el("button", {
    onclick: () => {
      inlineForm(`DISPUTE claim ${claim.claim_id.slice(0, 8)}`, [{ name: "reason", label: "reason", kind: "textarea" }], async (v) => {
        const r = await sendAct({ act: "DISPUTE", target: claim.claim_id, reason: v.reason });
        strip.remove();
        if (onDone) onDone(r);
      });
    },
  }, "d dispute");
  strip.append(el("div", {}, verify, " ", dispute, " ", el("button", { onclick: () => { strip.remove(); say("review cancelled: nothing was recorded"); } }, "esc cancel")));
  return strip;
}

const SEAM_CODES = [
  ["h", "same handle, exact"], ["e", "shared email or hint consistent"], ["n", "shared phone or hint consistent"],
  ["b", "bio cross-reference or self-link"], ["i", "image or pHash match"], ["t", "temporal co-location or pattern"],
  ["g", "analyst gestalt, no note required at merge"], ["k", "external knowledge, note required"],
];

// The Merge Sheet (design 5.5): the only modal. Members are the marked nodes
// (v), at least two. Basis claims are the claims holding the members; an
// unreviewed one shows the review strip first. Seams are ticked per member and
// never rolled up. The band is consequential: possible needs a caveat to cite,
// almost_certain needs two evidence classes, which the model enforces.
export async function mergeSheet(members) {
  if (members.length < 2) { say("the Merge Sheet needs at least two marked nodes: select one and press v, then another and press v, then m"); return; }
  const nodes = [];
  for (const id of members) {
    const r = await getJSON(`/api/cases/${state.caseId}/node/${id}`);
    if (!r.ok) { say("a marked node could not be read"); return; }
    if (!["entity", "referenced"].includes(r.body.node.kind)) { say(`${id.slice(0, 8)} is a ${r.body.node.kind}: a cluster references accounts and referenced-only ids only`); return; }
    nodes.push(r.body);
  }
  const claims = new Map();
  const holder = new Map();
  const proposals = new Set();
  for (const d of nodes) {
    for (const c of d.claims) { claims.set(c.claim_id, c); if (!holder.has(c.claim_id)) holder.set(c.claim_id, d.node.node_id); }
    for (const e of d.edges) {
      if (e.kind === "proposes" && members.includes(e.src_id) && members.includes(e.dst_id) && !e.withdrawn) proposals.add(e.event_id);
    }
  }
  if (!claims.size) { say("no claim holds any marked node, so there is no basis to select"); return; }
  const dialog = el("dialog", { class: "sheet" });
  const seamBoxes = {};
  const memberRows = nodes.map((d) => {
    seamBoxes[d.node.node_id] = {};
    return el("div", { class: "fusion-row" },
      el("div", {}, `${d.node.node_id.slice(0, 8)} · ${d.node.lines[0] || d.node.kind}`),
      el("div", {}, ...SEAM_CODES.map(([code, label]) => {
        const box = el("input", { type: "checkbox", value: code, title: label });
        seamBoxes[d.node.node_id][code] = box;
        return el("label", { class: "seam" }, box, code);
      })));
  });
  const basisBoxes = {};
  const basisRows = [...claims.values()].map((c) => {
    const box = el("input", { type: "checkbox", value: c.claim_id });
    basisBoxes[c.claim_id] = box;
    const row = el("div", { class: "observation-row" }, el("label", {}, box, ` ${c.claim_id.slice(0, 8)} · ${c.selector_type} · `, el("span", { class: "review" }, c.review)));
    if (c.review.startsWith("unreviewed")) {
      box.disabled = true;
      row.append(reviewStrip(c, "merge_basis", async (r) => {
        if (r && r.ok) {
          // Re-read the member that holds this claim; a claim whose state cannot be
          // re-read stays unselectable rather than reading as reviewed.
          const again = await getJSON(`/api/cases/${state.caseId}/node/${holder.get(c.claim_id)}`);
          const fresh = again.ok ? again.body.claims.find((x) => x.claim_id === c.claim_id) : null;
          row.querySelector(".review").textContent = fresh ? fresh.review : "review state could not be re-read: not selectable";
          box.disabled = !fresh || !fresh.review.startsWith("verified");
        }
      }));
    }
    return row;
  });
  const band = el("select", { name: "band" }, ...["possible", "likely", "almost_certain"].map((b) => el("option", { value: b }, b)));
  band.value = "likely";
  const note = el("textarea", { name: "note", placeholder: "note (required with k; required at export with g)", maxlength: 2000 });
  const override = el("textarea", { name: "override", placeholder: "circularity override note, only after MERGE_CIRCULAR", maxlength: 2000, hidden: true });
  const result = el("div", { class: "consequence" });
  const submit = async () => {
    const seams = {};
    for (const [id, boxes] of Object.entries(seamBoxes)) seams[id] = Object.entries(boxes).filter(([, b]) => b.checked).map(([code]) => code);
    const basis = Object.entries(basisBoxes).filter(([, b]) => b.checked && !b.disabled).map(([id]) => id);
    const body = { act: "CLUSTER", members, member_seams: seams, band: band.value, basis_claims: basis };
    if (note.value.trim()) body.note = note.value.trim();
    if (proposals.size) body.proposals = [...proposals];
    if (!override.hidden && override.value.trim()) body.circularity_override = { note: override.value.trim() };
    const r = await sendAct(body);
    if (r.ok) { dialog.close(); dialog.remove(); return; }
    const detail = r.body && r.body.detail ? r.body.detail : "";
    result.textContent = r.body ? `${r.body.text} ${detail}` : "the cluster could not be asserted";
    if (detail.includes("MERGE_CIRCULAR")) {
      override.hidden = false;
      result.append(el("div", {}, "CIRCULAR EVIDENCE: a basis claim traces to a GENERATED origin or to a pivot on a member; override with a note, and the inference carries a permanent circular badge"));
    }
  };
  dialog.append(
    el("h2", {}, "ASSERT IDENTITY · the Merge Sheet"),
    el("h3", {}, "MEMBERS and RATIONALE per member (h e n b i t g k)"), ...memberRows,
    el("h3", {}, "BASIS claims (an unreviewed claim is reviewed first)"), ...basisRows,
    proposals.size ? el("div", {}, `${proposals.size} proposal(s) between the members enter the cluster's lineage as accepted`) : el("div", {}, "no proposal between the members; the assertion rests on the basis claims alone"),
    el("div", {}, "BAND ", band, " · possible is citable only with a caveat; almost_certain needs two evidence classes"),
    el("div", {}, note), el("div", {}, override), result,
    el("div", {}, el("button", { onclick: submit }, "⏎ assert identity"), " ", el("button", { onclick: () => { dialog.close(); dialog.remove(); say("merge cancelled: nothing was recorded"); } }, "esc cancel")));
  dialog.addEventListener("keydown", (e) => { e.stopPropagation(); if (e.key === "Escape") { e.preventDefault(); dialog.close(); dialog.remove(); say("merge cancelled: nothing was recorded"); } });
  document.body.append(dialog);
  dialog.showModal();
}

// The acts bound to keys. Each takes the INSPECTOR's data for the selected node.
export const KEY_ACTS = {
  promote(d) {
    const claim = d.claims[0];
    if (!claim) { say("promote needs a node a claim holds: its item becomes the entity"); return; }
    inlineForm(`PROMOTE item ${claim.item_id.slice(0, 8)} to an entity`, [
      { name: "entity_type", label: "entity type", kind: "select", options: ["Account", "PersonCandidate", "Org", "Channel", "Place", "Media", "ManualTask"] },
    ], (v) => queueAct("PROMOTE", { act: "PROMOTE", target: claim.item_id, entity_type: v.entity_type, anchor_claim: claim.claim_id },
      `item ${claim.item_id.slice(0, 8)} becomes a ${v.entity_type} anchored on ${claim.selector_type}; vouched only when a claim of that type holds it`));
  },
  exclude(d) {
    const basis = d.claims[0] || null;
    const focusClaim = basis ? basis.claim_id : null;
    inlineForm(`EXCLUDE ${d.node.node_id.slice(0, 8)}: affirmatively not the subject`, [
      { name: "basis", label: "basis", kind: "textarea" },
      { name: "based_on", label: "claim id it rests on", kind: "input", placeholder: focusClaim || "a claim id" },
    ], (v) => queueAct("EXCLUDE", { act: "EXCLUDE", target: d.node.node_id, basis: v.basis, based_on: [v.based_on || focusClaim] },
      `${d.node.node_id.slice(0, 8)} is asserted not the subject; it stays in place, struck through`));
  },
  ignore(d) {
    const claim = d.claims[0];
    const target = claim ? claim.claim_id : d.node.created_by_event_id;
    inlineForm(`IGNORE ${target.slice(0, 8)}: soft, reversible, stays in the log`, [
      { name: "reason", label: "reason (needed only when the target supports a live cluster or another analyst promoted it)", kind: "input" },
    ], (v) => {
      const body = { act: "IGNORE", target };
      if (v.reason) body.reason = v.reason;
      queueAct("IGNORE", body, `${target.slice(0, 8)} is ignored: soft and reversible, it stays in the log and in lineage`);
    });
  },
  note(d) {
    const target = d.claims[0] ? d.claims[0].claim_id : d.node.created_by_event_id;
    inlineForm(`NOTE on ${target.slice(0, 8)}`, [{ name: "text", label: "note", kind: "textarea" }],
      (v) => queueAct("NOTE", { act: "NOTE", target, text: v.text }, `a note is recorded on ${target.slice(0, 8)}; it stands in the log once sent`));
  },
  question(d) {
    const target = d.claims[0] ? d.claims[0].claim_id : d.node.created_by_event_id;
    inlineForm(`QUESTION on ${target.slice(0, 8)}`, [{ name: "text", label: "open question", kind: "textarea" }],
      (v) => queueAct("QUESTION", { act: "QUESTION", target, text: v.text }, `an open question is recorded on ${target.slice(0, 8)}; it stands in the log once sent`));
  },
  revoke(d) {
    const target = d.node.created_by_event_id;
    inlineForm(`REVOKE ${target.slice(0, 8)}: it no longer stands, the tombstone stays walkable`, [{ name: "reason", label: "reason", kind: "textarea" }],
      (v) => queueAct("REVOKE", { act: "REVOKE", target, reason: v.reason }, `${target.slice(0, 8)} no longer stands; the tombstone names who asserted and who revoked`));
  },
};
