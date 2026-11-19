// The showcase reads the case through the existing GET routes only. It sends no
// POST and no PUT, writes no workspace state, and keeps nothing in browser
// storage (doctrine/EGRESS.md EG-3). A URL it requests carries uuids and fixed
// words only, so no case value ever reaches a request line.
//
// Every request passes one gate: at most LOAD.inFlight are open at once, so the
// first load never opens dozens of sockets on the stdlib server at the same
// moment. A request that does not arrive (the network failed, not the server
// refused) is tried again LOAD.retries times after a short pause. A refusal is
// an answer and is never retried. A request that still does not arrive comes
// back as { dropped: true }, so the page can draw everything else and say
// which part did not load. app/tests/test_showcase.py runs this file under node
// with a fetch that drops one request.

export const LOAD = { inFlight: 4, retries: 2, pauseMs: [250, 750] };

let open = 0;
const queue = [];

// The display overlay (app/http/overlay.py): fictional stand-ins drawn over the
// corpus's placeholders in every body the page reads, at display time only, so
// every view and the drawer show the same values. The store is never written.
let swaps = null;

export function setOverlay(values) {
  const pairs = values ? Object.entries(values).filter(([k, v]) => typeof k === "string" && typeof v === "string") : [];
  swaps = pairs.length ? pairs : null;
}

// The overlay's presentation. Live draws the case without the page's own test,
// fictional and placeholder labels, for a presenter's screen; the overlay file
// chooses it, so a page served without --overlay is never live.
export let liveLook = false;

export function setLiveLook(on) {
  liveLook = !!on;
}

// A display-only case pack (app/http/overlay.py): one response for every request the page
// makes for one fictional case, keyed by path and sorted query. While a pack is set, every
// /api/ request is answered from it, and one it does not hold is answered "not held" without
// reaching the server, so the store's own case never shows through the fictional one.
let pack = null;
export let labels = {};

export function setCasePack(p) {
  pack = p && p.responses && typeof p.responses === "object" ? p.responses : null;
  labels = pack && p.labels && typeof p.labels === "object" ? p.labels : {};
}

export function hasCasePack() {
  return !!pack;
}

function packKey(url) {
  const [path, query] = String(url).split("?");
  return query ? `${path}?${query.split("&").sort().join("&")}` : path;
}

function fromPack(url) {
  const key = packKey(url);
  if (!Object.prototype.hasOwnProperty.call(pack, key)) {
    return { ok: false, status: 404, body: { code: "NOT_HELD", text: "this case holds no such record" } };
  }
  const body = JSON.parse(JSON.stringify(pack[key]));
  return { ok: true, status: 200, body: swaps ? swap(body) : body };
}

function swapText(v) {
  let s = v;
  for (const [from, to] of swaps) if (s.includes(from)) s = s.split(from).join(to);
  return s;
}

function swap(v) {
  if (typeof v === "string") return swapText(v);
  if (Array.isArray(v)) return v.map(swap);
  if (v && typeof v === "object") {
    const o = {};
    for (const [k, x] of Object.entries(v)) o[k] = swap(x);
    if (typeof v.text === "string" && Array.isArray(v.spans)) o.spans = v.spans.map((sp) => rebase(v.text, sp));
    return o;
  }
  return v;
}

// An evidence snapshot's span counts UTF-16 code units of its text as the pack holds it (amendment 9.31), and
// the page reads that text with the stand-ins drawn in, so each boundary moves to where the same characters
// now sit. A boundary inside a placeholder has no such place: it becomes -1, and the page refuses the snapshot
// in words rather than mark the wrong characters.
function rebase(text, sp) {
  const moved = swap(sp);
  if (!sp || typeof sp !== "object" || !Number.isInteger(sp.start) || !Number.isInteger(sp.end)) return moved;
  const whole = swapText(text);
  const at = (i) => {
    const head = swapText(text.slice(0, i));
    return head + swapText(text.slice(i)) === whole ? head.length : -1;
  };
  return { ...moved, start: at(sp.start), end: at(sp.end) };
}

function enter() {
  return new Promise((resolve) => {
    if (open < LOAD.inFlight) {
      open += 1;
      resolve();
    } else {
      queue.push(resolve);
    }
  });
}

function leave() {
  const next = queue.shift();
  if (next) next();
  else open -= 1;
}

function pause(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function getJSON(url) {
  if (pack && String(url).startsWith("/api/")) return fromPack(url);
  await enter();
  try {
    for (let attempt = 0; ; attempt += 1) {
      try {
        const r = await fetch(url, { credentials: "same-origin", cache: "no-store" });
        const text = await r.text();
        let body = null;
        try { body = JSON.parse(text); } catch (_) { body = null; }
        if (swaps && body && !String(url).startsWith("/static/")) body = swap(body);
        return { ok: r.ok, status: r.status, body };
      } catch (err) {
        if (attempt >= LOAD.retries) {
          return { ok: false, status: 0, body: null, dropped: true, error: String((err && err.message) || err) };
        }
        await pause(LOAD.pauseMs[attempt] || 750);
      }
    }
  } finally {
    leave();
  }
}

/** The body of a GET, or an Error carrying the server's own refusal text, or `dropped` when nothing arrived. */
export async function need(url) {
  const r = await getJSON(url);
  if (!r.ok) {
    const text = r.dropped
      ? "a request did not arrive after three tries"
      : (r.body && r.body.text ? r.body.text : `the server answered ${r.status}`);
    const err = new Error(text);
    err.status = r.status;
    err.body = r.body;
    err.dropped = !!r.dropped;
    throw err;
  }
  return r.body;
}
