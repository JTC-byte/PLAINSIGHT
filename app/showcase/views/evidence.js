// The Lineage Drawer's evidence tier (docs/PLAINSIGHT-design.md amendment 9.31):
// what the source showed at capture, framed as a snapshot of the source's page,
// with the characters a claim was read from highlighted. It draws the closed
// shape of lib/evidence.js and refuses anything else, in words. Every string
// reaches the page as a text node through h() and s(); nothing is parsed as
// markup. No image, video or raw byte is held or fetched: an image or a player
// is a neutral box of the stated proportions, and a route is a sketch in its own
// unit box, never a place on a map. Under a display-only case pack the snapshot
// was written for display, so its hash line names no bytes.

import { h, s } from "../lib/dom.js";
import { refusal, spanPieces, shortHash, sizeText, leadField, KIND_WORDS } from "../lib/evidence.js";
import { stamp } from "../lib/words.js";
import { hasCasePack } from "../lib/api.js";

export const EVIDENCE_TITLE = "EVIDENCE · AS CAPTURED";
const SPAN_WORDS = "the claim was read from this span";
const FIELD_WORDS = "the claim was read from this field";
/** The tallest a neutral box is drawn, in pixels; its stated proportions stay printed inside it. */
export const BOX_MAX_PX = 480;
/** The hash line: a capture's digest, or, under a case pack, a snapshot written for display. */
export const HASH_WORDS = "A rendering of the capture for reading, not the captured bytes. The sha256 names the bytes it stands for, which this page does not hold.";
export const PACK_HASH_WORDS = "This snapshot was written for display by a case pack and stands for no capture, so its sha256 names no bytes.";

const article = (word) => (/^[aeiou]/i.test(word) ? `an ${word}` : `a ${word}`);

/** The body text, each marked span a highlighted run whose title says what it is. */
function bodyText(ev, headId) {
  if (!ev.text) return null;
  return h("p", { class: "ev-text" }, spanPieces(ev.text, ev.spans, headId).map((p) => p.span
    ? h("mark", { class: ["ev-span", p.span.claim_event_id === headId && "this"], title: SPAN_WORDS }, p.text)
    : p.text));
}

function fieldValue(f, headId) {
  return f.claim_event_id
    ? h("mark", { class: ["ev-span", f.claim_event_id === headId && "this"], title: FIELD_WORDS }, f.value)
    : f.value;
}

/** Fields as a source's small print: label and value, side by side. */
function fieldRow(fields, headId) {
  if (!fields.length) return null;
  return h("div", { class: "ev-facts" }, fields.map((f) => h("span", {}, h("small", {}, f.label), " ", fieldValue(f, headId))));
}

/** A neutral box of the stated proportions, standing for an image or a player that is not held. It is drawn at
 * most BOX_MAX_PX tall, so a very tall image is drawn shorter than stated, and its stated proportions are printed. */
function placeholder(media, words) {
  const ratio = media ? `${media.width} / ${media.height}` : "16 / 9";
  return h("div", { class: "ev-box", css: { "aspect-ratio": ratio, "max-height": `${BOX_MAX_PX}px` }, role: "img", "aria-label": words },
    h("span", { class: "ev-box-d" }, media ? media.description : ""),
    h("span", { class: "ev-box-n" }, words),
    h("span", { class: "ev-box-r" }, media ? `stated ${media.width} by ${media.height}, drawn at most ${BOX_MAX_PX} pixels tall` : `no proportions stated, drawn 16 by 9`));
}

/** A route as the activity page sketches it: path_d in its own unit box, with no coordinate anywhere. */
function routeSketch(media) {
  return h("figure", { class: "ev-route" },
    s("svg", { viewBox: `0 0 ${media.width} ${media.height}`, role: "img", "aria-label": `route sketch, not geo-referenced: ${media.description}`, preserveAspectRatio: "xMidYMid meet" },
      s("path", { class: "ev-route-line", d: media.path_d })),
    h("figcaption", {}, "route sketch, not geo-referenced · ", media.description));
}

function postCard(ev, headId) {
  const lead = leadField(ev);
  const rest = (ev.fields || []).filter((f) => f !== lead);
  return h("div", { class: "ev-post" },
    h("div", { class: "ev-author" },
      h("span", { class: "ev-avatar", "aria-hidden": "true" }),
      h("div", {}, h("b", {}, lead ? fieldValue(lead, headId) : "author not captured"), lead ? h("small", {}, lead.label) : null)),
    ev.title ? h("div", { class: "ev-title" }, ev.title) : null,
    bodyText(ev, headId),
    ev.media ? placeholder(ev.media, "no image bytes are held; the box stands for the image") : null,
    fieldRow(rest, headId));
}

function recordCard(ev, headId) {
  return h("div", { class: "ev-record" },
    ev.title ? h("div", { class: "ev-title" }, ev.title) : null,
    (ev.fields || []).length ? h("table", { class: "ev-table" }, h("tbody", {}, ev.fields.map((f) =>
      h("tr", { class: f.claim_event_id && "hit" }, h("th", {}, f.label), h("td", {}, fieldValue(f, headId)))))) : null,
    bodyText(ev, headId));
}

function pageCard(ev, headId) {
  return h("div", { class: "ev-page" },
    ev.title ? h("div", { class: "ev-title" }, ev.title) : null,
    ev.media ? placeholder(ev.media, "no image bytes are held; the box stands for the image") : null,
    bodyText(ev, headId),
    fieldRow(ev.fields || [], headId));
}

function videoCard(ev, headId) {
  const lead = leadField(ev);
  const rest = (ev.fields || []).filter((f) => f !== lead);
  return h("div", { class: "ev-video" },
    placeholder(ev.media || null, "no video or image bytes are held; the box stands for the player"),
    ev.title ? h("div", { class: "ev-title" }, ev.title) : null,
    lead ? h("div", { class: "ev-channel" }, h("small", {}, lead.label), " ", fieldValue(lead, headId)) : null,
    bodyText(ev, headId),
    fieldRow(rest, headId));
}

function activityCard(ev, headId) {
  return h("div", { class: "ev-activity" },
    ev.title ? h("div", { class: "ev-title" }, ev.title) : null,
    (ev.fields || []).length ? h("div", { class: "ev-stats" }, ev.fields.map((f) => h("div", {}, h("small", {}, f.label), h("b", {}, fieldValue(f, headId))))) : null,
    ev.media && ev.media.kind === "route" ? routeSketch(ev.media) : null,
    bodyText(ev, headId));
}

function imageCard(ev, headId) {
  return h("div", { class: "ev-image" },
    ev.title ? h("div", { class: "ev-title" }, ev.title) : null,
    placeholder(ev.media || null, "no image bytes are held; the box stands for the image"),
    bodyText(ev, headId),
    fieldRow(ev.fields || [], headId));
}

const CARDS = { post: postCard, message: postCard, profile: recordCard, record: recordCard, page: pageCard, video: videoCard, activity: activityCard, image: imageCard };

/** The tier for one evidence object, or a sentence saying why it is not drawn. */
export function evidenceTier(ev, headId) {
  const why = refusal(ev);
  if (why) {
    return h("div", { class: "evidence" }, h("div", { class: "tier" }, EVIDENCE_TITLE),
      h("div", { class: "note-line" }, `This snapshot is not drawn: ${why}. The page draws only the closed shape of amendment 9.31.`));
  }
  const marked = (ev.spans || []).length > 0;
  const fieldMarked = (ev.fields || []).some((f) => f.claim_event_id);
  return h("div", { class: "evidence" },
    h("div", { class: "tier" }, EVIDENCE_TITLE),
    h("div", { class: "ev-meta" },
      h("div", {}, h("b", {}, KIND_WORDS[ev.kind]), ` · ${ev.source_label}`),
      h("div", {}, `captured ${stamp(ev.captured_at)} by ${ev.captured_by.tool} ${ev.captured_by.version}`),
      h("div", { class: "mono" }, `${ev.content_type} · ${sizeText(ev.size_bytes)} · sha256 ${shortHash(ev.sha256)}`)),
    h("p", { class: "ev-note" }, ev.provenance_note),
    h("p", { class: "faint" }, hasCasePack() ? PACK_HASH_WORDS : HASH_WORDS),
    h("figure", { class: "ev-shot", "aria-label": `snapshot of ${article(KIND_WORDS[ev.kind].toLowerCase())} on ${ev.source_label}` },
      h("div", { class: "ev-bar" },
        h("span", { class: "ev-dots", "aria-hidden": "true" }, h("i", {}), h("i", {}), h("i", {})),
        h("span", { class: "ev-src" }, ev.source_label),
        h("span", { class: "ev-when" }, `captured ${stamp(ev.captured_at)}`)),
      h("div", { class: "ev-body" }, CARDS[ev.kind](ev, headId))),
    marked || fieldMarked ? h("div", { class: "ev-cap" }, h("mark", { class: "ev-span" }, "highlighted"), ` ${marked ? SPAN_WORDS : FIELD_WORDS}`) : null);
}
