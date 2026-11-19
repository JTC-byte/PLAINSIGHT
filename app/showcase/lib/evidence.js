// The evidence snapshot's display contract (docs/PLAINSIGHT-design.md amendment
// 9.31). A back lineage response may carry an optional `evidence` object: a
// rendering of what a source showed at capture, laid out as the source showed
// it, so an analyst can see the text a claim was read from. It is never the raw
// bytes. Raw capture is stratum 0 and does not cross to LOCAL (doctrine/EGRESS.md
// EG-2 and EG-5), and this server holds and serves no blob on LOCAL (amendment
// 9.4), so the server sends no evidence object today. A display-only case pack
// can supply one.
//
// A span's start and end count UTF-16 code units of the text, as JavaScript
// strings do, and not code points or bytes; a boundary that falls inside a
// surrogate pair, between the two halves of one character, is refused.
//
// The shape is closed. The page draws an object that fits it and refuses one
// that does not, saying why, so a key nobody reviewed never reaches the screen.
// This file imports nothing and touches no DOM, so app/tests/test_showcase.py
// runs it under node.

export const EVIDENCE_KINDS = Object.freeze(["post", "profile", "page", "record", "activity", "video", "image", "message"]);
export const EVIDENCE_KEYS = Object.freeze(["kind", "captured_at", "captured_by", "source_label", "content_type", "sha256", "size_bytes", "title", "fields", "text", "spans", "media", "provenance_note"]);
const REQUIRED = Object.freeze(["kind", "captured_at", "captured_by", "source_label", "content_type", "sha256", "size_bytes", "provenance_note"]);
const CAPTURED_BY_KEYS = Object.freeze(["tool", "version"]);
const FIELD_KEYS = Object.freeze(["label", "value", "claim_event_id"]);
const SPAN_KEYS = Object.freeze(["start", "end", "claim_event_id"]);
export const MEDIA_KEYS = Object.freeze(["kind", "description", "width", "height", "path_d"]);
const MEDIA_KINDS = Object.freeze(["image", "route", "thumbnail"]);
/** The media each kind's card draws. A record and a profile draw none, only an activity draws a route, and an activity draws nothing else. */
export const MEDIA_BY_KIND = Object.freeze({
  post: Object.freeze(["image", "thumbnail"]),
  message: Object.freeze(["image", "thumbnail"]),
  page: Object.freeze(["image", "thumbnail"]),
  video: Object.freeze(["image", "thumbnail"]),
  image: Object.freeze(["image", "thumbnail"]),
  activity: Object.freeze(["route"]),
  record: Object.freeze([]),
  profile: Object.freeze([]),
});
/** An SVG path's commands and numbers and nothing else. Its numbers live in the path's own box, never on a map. */
export const PATH_D = /^[MmLlHhVvCcSsQqTtAaZz0-9eE.,\s+-]{1,4000}$/;
const HEX64 = /^[0-9a-f]{64}$/;
const LINKISH = /:\/\/|\bwww\./i;

export const KIND_WORDS = Object.freeze({
  post: "Post", profile: "Profile", page: "Page", record: "Registry record",
  activity: "Activity", video: "Video page", image: "Image", message: "Message",
});

const text = (v) => typeof v === "string" && v.length > 0;
const only = (o, keys) => o && typeof o === "object" && !Array.isArray(o) && Object.keys(o).every((k) => keys.includes(k));
const count = (n) => Number.isInteger(n) && n >= 0;
/** Whether offset i of s falls between the two halves of a surrogate pair. */
const high = (c) => c >= 0xd800 && c <= 0xdbff;
const low = (c) => c >= 0xdc00 && c <= 0xdfff;
const splitsPair = (s, i) => i > 0 && i < s.length && high(s.charCodeAt(i - 1)) && low(s.charCodeAt(i));
const extent = (n) => typeof n === "number" && Number.isFinite(n) && n > 0 && n <= 10000;

function strings(v, out = []) {
  if (typeof v === "string") out.push(v);
  else if (Array.isArray(v)) v.forEach((x) => strings(x, out));
  else if (v && typeof v === "object") Object.values(v).forEach((x) => strings(x, out));
  return out;
}

/** Why an evidence object is not drawn, as a clause, or null when it fits the closed shape. */
export function refusal(ev) {
  if (!only(ev, EVIDENCE_KEYS)) return "it is not an object, or it carries a key outside the closed shape";
  for (const k of REQUIRED) if (!(k in ev)) return `it has no ${k}`;
  if (!EVIDENCE_KINDS.includes(ev.kind)) return "its kind is not one the page draws";
  for (const k of ["captured_at", "source_label", "content_type", "provenance_note"]) if (!text(ev[k])) return `its ${k} is not text`;
  if (!only(ev.captured_by, CAPTURED_BY_KEYS) || !text(ev.captured_by.tool) || !text(ev.captured_by.version)) return "its captured_by is not a tool and a version";
  if (!HEX64.test(String(ev.sha256))) return "its sha256 is not 64 lowercase hex characters";
  if (!count(ev.size_bytes)) return "its size_bytes is not a whole number";
  if ("title" in ev && !text(ev.title)) return "its title is not text";
  if ("text" in ev && typeof ev.text !== "string") return "its text is not text";
  if ("fields" in ev) {
    if (!Array.isArray(ev.fields)) return "its fields are not a list";
    for (const f of ev.fields) {
      if (!only(f, FIELD_KEYS) || !text(f.label) || typeof f.value !== "string") return "a field is not a label and a value";
      if ("claim_event_id" in f && !text(f.claim_event_id)) return "a field names a claim that is not text";
    }
  }
  if ("spans" in ev) {
    if (!Array.isArray(ev.spans) || typeof ev.text !== "string") return "it marks spans without a text to mark";
    for (const s of ev.spans) {
      if (!only(s, SPAN_KEYS) || !count(s.start) || !count(s.end) || !text(s.claim_event_id)) return "a span is not a start, an end and a claim";
      if (s.start >= s.end || s.end > ev.text.length) return "a span falls outside its text";
      if (splitsPair(ev.text, s.start) || splitsPair(ev.text, s.end)) return "a span's boundary splits one character in two; offsets count UTF-16 code units";
    }
  }
  if ("media" in ev) {
    const m = ev.media;
    if (!only(m, MEDIA_KEYS) || !MEDIA_KINDS.includes(m.kind) || !text(m.description) || !extent(m.width) || !extent(m.height)) {
      return "its media is not a kind, a description, a width and a height";
    }
    if (m.kind === "route" ? !PATH_D.test(String(m.path_d || "")) : "path_d" in m) return "its media's path_d is not a route sketch's path";
    if (!MEDIA_BY_KIND[ev.kind].includes(m.kind)) return "its media is not one its card draws: a record and a profile draw none, and only an activity draws a route and draws nothing else";
  }
  if (strings(ev).some((s) => LINKISH.test(s))) return "it holds a link, and a snapshot links to nothing";
  return null;
}

/** The text cut at every span boundary into pieces, each with the span that marks it or null. Every character
 * a span covers is marked, so overlapping spans keep every claim visible; where spans overlap, a piece takes
 * the head claim's span, so the head's span is drawn whole with its outline. */
export function spanPieces(body, spans, headId) {
  const list = spans || [];
  const cuts = [...new Set([0, body.length, ...list.flatMap((sp) => [sp.start, sp.end])])].sort((a, b) => a - b);
  const out = [];
  for (let i = 0; i + 1 < cuts.length; i += 1) {
    const [a, b] = [cuts[i], cuts[i + 1]];
    const over = list.filter((sp) => sp.start <= a && b <= sp.end);
    const span = over.find((sp) => sp.claim_event_id === headId) || over[0] || null;
    const last = out[out.length - 1];
    if (last && last.span === span) last.text += body.slice(a, b);
    else out.push({ text: body.slice(a, b), span });
  }
  return out;
}

export function shortHash(sha) {
  return `${String(sha).slice(0, 12)}…`;
}

export function sizeText(n) {
  if (n < 1024) return `${n} bytes`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / (1024 * 1024)).toFixed(1)} MB`;
}

/** The field a post, a message or a video page leads with: its author, or its channel. */
export function leadField(ev) {
  const want = ev.kind === "video" ? /^channel$/i : /^(author|handle|from|sender|account)$/i;
  return (ev.fields || []).find((f) => want.test(f.label)) || null;
}
