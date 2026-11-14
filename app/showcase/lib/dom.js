// DOM helpers for the showcase. Every string reaches the page as a text node or
// an attribute value; nothing is parsed as markup, so collected text stays inert
// (docs/PLAINSIGHT-design.md 5.4; the harvest's rule B33). Styles are set
// through the CSSOM only, which the server's CSP (default-src 'self') allows,
// and never as a style attribute.

let svgNS = null;

function svgNamespace() {
  if (!svgNS) {
    const probe = document.createElement("div");
    probe.innerHTML = "<svg></svg>";
    svgNS = probe.firstChild.namespaceURI;
  }
  return svgNS;
}

function apply(node, attrs) {
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v === null || v === undefined || v === false) continue;
    if (k === "class") node.setAttribute("class", Array.isArray(v) ? v.filter(Boolean).join(" ") : v);
    else if (k === "css") for (const [p, val] of Object.entries(v)) node.style.setProperty(p, String(val));
    else if (k.startsWith("on") && typeof v === "function") node.addEventListener(k.slice(2), v);
    else node.setAttribute(k, v === true ? "" : String(v));
  }
}

// The live presentation's display renames, such as the example analyst's id printed as a neutral
// label. They apply to text as it reaches the page; nothing read or stored changes.
let renames = null;

export function setRenames(pairs) {
  renames = pairs && pairs.length ? pairs : null;
}

function shown(text) {
  if (!renames) return text;
  let t = text;
  for (const [from, to] of renames) if (from && t.includes(from)) t = t.split(from).join(to);
  return t;
}

function append(node, kids) {
  for (const kid of kids.flat(Infinity)) {
    if (kid === null || kid === undefined || kid === false) continue;
    node.append(kid instanceof Node ? kid : document.createTextNode(shown(String(kid))));
  }
}

/** An HTML element. */
export function h(tag, attrs, ...kids) {
  const node = document.createElement(tag);
  apply(node, attrs);
  append(node, kids);
  return node;
}

/** An SVG element. */
export function s(tag, attrs, ...kids) {
  const node = document.createElementNS(svgNamespace(), tag);
  apply(node, attrs);
  append(node, kids);
  return node;
}

export function clear(node, ...kids) {
  node.replaceChildren();
  append(node, kids);
  return node;
}

/** The portrait the design asks for when no image is held: a silhouette, never a face. */
export function silhouette(size = 120, label = "no image is held for this subject") {
  return s("svg", { viewBox: "0 0 120 120", width: size, height: size, role: "img", "aria-label": label },
    s("rect", { width: 120, height: 120, fill: "#232a35" }),
    s("circle", { cx: 60, cy: 47, r: 22, fill: "#59616d" }),
    s("path", { d: "M17 120c4-27 22-41 43-41s39 14 43 41z", fill: "#59616d" }));
}

/** A lineage affordance: every rendered value has one (design 5.7). */
export function lin(onopen, what = "this value") {
  return h("button", { class: "lin", type: "button", title: `open the lineage of ${what}`, "aria-label": `lineage of ${what}`, onclick: (e) => { e.stopPropagation(); onopen(); } }, "⧉");
}

import { liveLook } from "./api.js";

/** A text token. `novouch` paints the one hue and the hatch, and only a server flag sets it. In the live
 * presentation a clause that names the test corpus moves to the hover title; the state the token names stays. */
export function tok(text, novouch = false, strong = false) {
  const attrs = { class: ["tok", novouch && "novouch", strong && "strong"] };
  let shown = text;
  if (liveLook && typeof text === "string") {
    shown = text.split(" · ").filter((part) => !/synthetic|corpus|fixture/i.test(part)).join(" · ") || text;
    if (shown !== text) attrs.title = text;
  }
  return h("span", attrs, shown);
}

/** A part of the page that did not arrive, said calmly, with a way to try again. Never red: it is the page's own transport, not a state of the case. */
export function notLoaded(what, onRetry) {
  return h("div", { class: "retry", role: "status" },
    h("span", { class: "retry-mark", "aria-hidden": "true" }, "↻"),
    h("span", { class: "grow" }, `${what} did not load: a request did not arrive after three tries. Everything else here is drawn.`),
    onRetry ? h("button", { class: "btn", type: "button", onclick: onRetry }, "Retry") : null);
}

export function kbd(key) {
  return h("span", { class: "kbd", "aria-hidden": "true" }, key);
}
