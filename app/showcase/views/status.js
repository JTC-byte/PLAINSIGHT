// The case strip: every doctrine state the case header serves, on one calm
// line. Each chip is the state's consequence in a few words, and opens the
// server's own sentence verbatim with what it means and how it clears. Red and
// the hatch appear only where the server's flag says the system does not vouch
// (the halt, the sweep's vouch flag, the retention flag). Nothing is hidden: a
// state the strip cannot condense is shown in the server's words.

import { h, clear } from "../lib/dom.js";
import { stamp, short } from "../lib/words.js";
import { liveLook } from "../lib/api.js";

const RULE = /\s*\(([A-Z]{1,3}-\d+)\)\s*$/;

function rule(text) {
  const m = RULE.exec(text || "");
  return m ? m[1] : null;
}

function chips(header) {
  const out = [];
  const st = String(header.state || "");
  const [stLead, ...stRest] = st.split(":");
  out.push({
    id: "state", lead: stLead === "open" ? "Case open" : stLead, rest: stRest.join(":").replace(" in this store", "").trim(), rule: null, novouch: false,
    title: "The case's registry state", server: st,
    meaning: ["The registry holds this case open in this store, and its case database is present."],
  });
  const ret = String(header.retention || "");
  out.push({
    id: "retention", lead: header.retention_vouch ? "Past retain_until" : "retain_until",
    rest: header.retention_vouch ? (/no sweep acts on LOCAL/.test(ret) ? "not swept on LOCAL" : (ret.split(" · ")[1] || "")) : ret,
    rule: null, novouch: !!header.retention_vouch,
    title: "Retention", server: ret,
    meaning: header.retention_vouch
      ? [/no sweep acts on LOCAL/.test(ret) && !liveLook
        ? "This case is past its retain_until. Its material is synthetic stratum-4 corpus data, and on LOCAL no sweep acts on it."
        : "This case is past its retain_until, in the server's words above.",
        "A token every node carries is stated once on the web, rather than on each node."]
      : ["The date this case's material is held until, as the store reads it."],
  });
  const anc = String(header.anchor || "");
  const am = /anchor_ts (\S+) \(([^)]*)\)/.exec(anc);
  out.push({
    id: "anchor", lead: "Anchor", rest: am ? am[2].replace("first event ts", "first event").replace(/,?\s*U-\d+\s*/, " · ") : anc,
    rule: /U-\d+/.exec(anc) ? /U-\d+/.exec(anc)[0] : null, novouch: false,
    title: "The instant retain_until is counted from", server: anc,
    meaning: ["Open question U-02 asks whether retain_until is a date or a timestamp, which instant anchors it, and whether the sweep's comparison is strict or inclusive.",
      "Until it is stamped, this build reads the anchor as the case's first event, and says so."],
  });
  const env = String(header.environment || "");
  const [envLead, ...envRest] = env.replace(RULE, "").split(":");
  out.push({
    id: "environment", lead: envLead, rest: envLead === "LOCAL" ? (liveLook ? "" : "synthetic corpus only") : envRest.join(":").trim(),
    rule: rule(env), novouch: false, title: "Where this store runs", server: env,
    meaning: envLead === "LOCAL"
      ? ["LOCAL holds code, specification, fixtures and the synthetic corpus, and executes validators and tests. Connectors execute only in ISOLATED, and case material never lives on LOCAL (EG-1, EG-2).",
        ...(liveLook ? [] : ["This case was ingested from the tracked synthetic corpus file. No person, account or platform was queried."])]
      : ["The case store, read through this view and never copied."],
  });
  const sw = header.sweep || {};
  const swText = String(sw.text || "");
  let swRest = swText.replace(RULE, "");
  if (/^RETENTION SWEEP HAS NOT RUN SINCE/.test(swText) && sw.ran) swRest = `sweep last ran ${stamp(sw.ran).slice(5, 10)}`;
  else if (/NEVER RUN/.test(swText)) swRest = "the sweep has never run here";
  out.push({
    id: "sweep", lead: sw.vouch ? "Retention not enforced" : "Retention sweep ran", rest: sw.vouch ? swRest : `${stamp(sw.ran)} · next due ${stamp(sw.next_due)}`,
    rule: "RT-12", novouch: !!sw.vouch, title: "The retention sweep's heartbeat", server: swText,
    meaning: sw.vouch
      ? ["The sweep writes a heartbeat on every run. Its last heartbeat's next due time has passed, so nothing is enforcing retain_until in this case. A missing heartbeat is a named state, never a silence (RT-12).",
        sw.next_due ? `Last heartbeat ${stamp(sw.ran)}; it was next due ${stamp(sw.next_due)}.` : "No next due time could be read.",
        liveLook ? "On LOCAL the sweep deletes nothing: the shred is refused here." : "On LOCAL the sweep deletes nothing: the shred is refused here, and this store holds synthetic corpus files only."]
      : ["The sweep wrote its heartbeat on time. This draft of the sweep deletes nothing."],
  });
  if (header.halt) {
    out.push({
      id: "halt", lead: "No new runs", rest: /shred failed/.test(header.halt) ? "a shred failed" : header.halt.replace(RULE, ""),
      rule: rule(header.halt) || "RT-11", novouch: true, title: "Collection halted", server: header.halt,
      meaning: ["A shred that fails is evidence about the retention mechanism, not about one case, so every new run stops everywhere (RT-11). Reading continues, and nothing on these screens can start a run.",
        "It clears one way: verify_shred passes all five RT-9 checks for the failed case, recorded as a logged act with its author and receipt hash.",
        ...(/^LOCAL/.test(String(header.environment || "")) && !liveLook ? ["On LOCAL the store holds tracked synthetic corpus files, so the failed shred here is a corpus row, and the header reads it exactly as it would read a real one."] : [])],
    });
  }
  // Context first, then what the system does not vouch for, worst last so it sits nearest the eye's end of the line.
  const order = ["environment", "state", "anchor", "retention", "sweep", "halt"];
  return out.sort((a, b) => order.indexOf(a.id) - order.indexOf(b.id));
}

/** The strip carries every state but the routine one: an open, held case is said in the profile's kicker. */
function stripChips(header) {
  return chips(header).filter((c) => !(c.id === "state" && /^open:/.test(String(header.state || ""))));
}

export function closePopover() {
  const pop = document.getElementById("popover");
  pop.hidden = true;
  clear(pop);
}

function openPopover(anchor, c, model) {
  const pop = document.getElementById("popover");
  const at = model.loadedAt.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  clear(pop,
    h("button", { class: "iconbtn close", type: "button", "aria-label": "close", onclick: closePopover }, "esc"),
    h("h3", {}, c.novouch ? h("span", { class: "tok novouch" }, c.rule || "not vouched") : (c.rule ? h("span", { class: "tok" }, c.rule) : null), c.title),
    h("div", { class: "faint" }, "The server's words"),
    h("div", { class: "server" }, c.server || "(the header served no text for this state)"),
    ...c.meaning.map((p) => h("p", {}, p)),
    h("div", { class: "src" }, `Read from the case header of C-${short(model.caseId)} at ${at} on this machine's clock.`));
  pop.hidden = false;
  const r = anchor.getBoundingClientRect();
  const left = Math.max(16, Math.min(r.left, window.innerWidth - pop.offsetWidth - 16));
  pop.style.setProperty("left", `${left}px`);
  pop.style.setProperty("top", `${r.bottom + 8}px`);
  pop.style.removeProperty("right");
  pop.querySelector(".close").focus();
}

export function renderStatus(bar, ctx, onRefresh) {
  const m = ctx.model;
  bar.hidden = !!liveLook;
  if (liveLook) return;
  const list = stripChips(m.header);
  clear(bar,
    h("span", { class: "label" }, "CASE STATUS"),
    h("div", { class: "chips" }, list.map((c) => h("button", {
      class: ["state", c.novouch && "novouch"], type: "button", "aria-haspopup": "dialog",
      title: c.server, "data-state": c.id,
      onclick: (e) => openPopover(e.currentTarget, c, m),
    }, h("span", { class: "lead" }, c.lead), c.rest ? h("span", { class: "txt" }, c.rest) : null, c.rule ? h("span", { class: "rule" }, c.rule) : null)),
    onRefresh ? h("button", { class: "btn primary", type: "button", onclick: onRefresh, title: "the store changed since this view was read" }, "The case changed · refresh") : null));
}

export function stateChips(header) {
  return chips(header);
}
