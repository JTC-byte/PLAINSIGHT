// Places, the MAP (design 3.4, the 11-02 idiom). A pin needs a machine-emitted
// coordinate; a place name or a co-location proposal is never drawn as a pin.
// This case holds no coordinate, so the tab says so, with what it does hold,
// and draws no map: there is no tile to fetch and no area that was swept.

import { h, tok, lin } from "../lib/dom.js";
import { placeCount, PLACE_SELECTORS, PLACE_ENTITIES, selectorLabel, plural } from "../lib/words.js";

export async function renderPlaces(el, ctx) {
  const m = ctx.model;
  const colocated = [...m.edgeText.values()].filter((e) => e.label === "co_located" || /co_located/.test(e.text || ""));
  const n = placeCount(m);
  if (ctx.missing("nodes") || ctx.missing("web")) el.append(h("p", { class: "muted" }, "Some nodes did not load, so this count may be short. Retry at the top of the page."));
  const held = [...m.claims.values()].filter((c) => PLACE_SELECTORS.includes(c.selector_type)).map((c) => ({ id: c.claim_id, label: `${selectorLabel(c.selector_type)} ${c.value}` }))
    .concat([...m.nodes.values()].filter((x) => PLACE_ENTITIES.includes(x.entity_type)).map((x) => ({ id: (x.lineage_heads || [])[0], label: (x.lines || []).join(" · ") })));
  if (n > 0) {
    el.append(
      h("div", { class: "section-title" }, h("h2", {}, "Where, if anywhere?"), h("span", { class: "sub" }, `${plural(n, "place record")} held`)),
      h("section", { class: "card card-b" },
        liveLook ? null : h("p", {}, "This build lists place records and draws no map: no basemap is requested, because a tile request for an area tells its provider what the case is looking at."),
        h("div", { class: "rows" }, held.map((x) => h("div", { class: "row" }, h("div", { class: "grow mono" }, x.label), lin(() => ctx.lineage(x.id, "place"), "this place record"))))));
    return;
  }
  el.append(
    h("div", { class: "section-title" }, h("h2", {}, "Where, if anywhere?"), h("span", { class: "sub" }, "no place record held: no geo_area claim and no Place entity")),
    h("section", { class: "card" },
      h("div", { class: "empty" },
        h("div", { class: "basemap", role: "img", "aria-label": "no map drawn: no coordinate is held and no area was queried" }),
        h("div", {},
          h("h3", {}, "No coordinate is held in this case, so no map is drawn."),
          h("p", {}, "A pin needs a coordinate a tool emitted, with its declared precision and its capture time. A place name, an address or a proposal that two things are co-located is never turned into a pin."),
          h("p", {}, "No basemap tile is requested either: a tile request for an area tells its provider what the case is looking at."),
          colocated.length ? h("div", { class: "rows" }, colocated.map((e) => h("div", { class: "row layer-inf" },
            h("div", { class: "grow" }, h("div", {}, tok("co-located, proposed"), " ", e.text), h("div", { class: "faint" }, "a relation between two nodes, not a place: nothing here says where")),
            lin(() => ctx.lineage(e.event_id, "co_located"), "this proposal")))) : null,
          h("p", { class: "faint" }, "When a coordinate exists, this tab opens on it: the pin hollow with its precision ring, its age written beside it, and the swept area lighter than what was never queried.")))));
}

import { liveLook } from "../lib/api.js";
