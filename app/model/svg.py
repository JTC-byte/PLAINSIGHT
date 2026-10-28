"""The WEB view rendered as SVG on the server, with stdlib XML escaping.

SVG only: no canvas, no WebGL, no script inside the document. Border geometry
carries the epistemic layer and nothing else (docs/PLAINSIGHT-design.md
section 5.2):

- OBSERVATION, a 1px solid line;
- INFERENCE, a 2px dashed line, never inside a bracket;
- FUSION, a cluster drawn with corner brackets, its member lines solid.

Dash means INFERENCE and nothing else: every node box, every card and the
Pivot Bar are drawn solid. A referenced-only node says what it is in its text
line, "referenced, never promoted in this case: no observation held".

Edge labels are painted after the node boxes, on a halo of the background, so
no box covers a label. A proposal's label leads with its consequence, NOT
ACCEPTED or PROPOSAL WITHDRAWN.

A state line wraps over as many lines as it needs and is never cut, so its
consequence always prints. Only a selector's value line is cut to the box,
with a visible " …"; the full value prints in the INSPECTOR.

The hatch and the red class mean only "the system does not vouch", and a text
token beside them always says which: raw not held, anchor unproven, past
retain_until. GENERATED values carry the ~ prefix and italics. A revoked cluster
and an excluded candidate are struck through in place, never removed.

Every element that stands for a node or an edge carries its uuid in data-node
or data-edge and the event its lineage starts from in data-lineage, so the
Lineage Drawer can walk it. Ids are uuids; no URL is written into the SVG.
"""

from __future__ import annotations

from xml.sax.saxutils import escape, quoteattr

from app.model import layout as layout_mod
from app.model.web import Web, collapsed_cards

#: Presentation attributes per epistemic layer. One fixed style per layer; no
#: property of the data changes a line's width, dash or colour.
LAYER_STYLE = {
    "observation": {"stroke-width": "1"},
    "inference": {"stroke-width": "2", "stroke-dasharray": "6 4"},
    "fusion": {"stroke-width": "1"},
}

#: The visible marker for a value line cut to fit the box. The full value is in the INSPECTOR.
CUT = " …"
MAX_CHARS = 46

#: The order the three layers are painted in. Labels last, so no box covers one.
PAINT_ORDER = ("edges", "nodes", "labels")

VOUCH_MARK = "▨"


def _attrs(pairs: dict) -> str:
    return "".join(f" {k}={quoteattr(str(v))}" for k, v in pairs.items())


def _fit(text: str) -> str:
    return text if len(text) <= MAX_CHARS else text[: MAX_CHARS - len(CUT)] + CUT


def wrap(text: str, width: int = MAX_CHARS) -> list[str]:
    """A state line over as many box lines as it needs, broken at spaces. Nothing is dropped."""
    out: list[str] = []
    line = ""
    for word in text.split(" "):
        while len(word) > width:
            if line:
                out.append(line)
                line = ""
            out.append(word[:width])
            word = word[width:]
        candidate = f"{line} {word}" if line else word
        if len(candidate) <= width:
            line = candidate
        else:
            out.append(line)
            line = word
    if line or not out:
        out.append(line)
    return out


def node_lines(n: dict) -> list[tuple[str, str]]:
    """(class, text) for each line a node prints, top to bottom, before fitting."""
    out = []
    for i, line in enumerate(n["lines"]):
        cls = "line"
        if n["kind"] == "selector" and i == 1:
            cls += " value"
            if n["generated"]:
                cls += " generated"
        if n["revoked"] or n["kind"] == "candidate":
            cls += " struck"
        out.append((cls, line))
    if n["vouch_tokens"]:
        out.append(("line vouch-token", f"{VOUCH_MARK} " + " · ".join(n["vouch_tokens"])))
    if n["sentences"]:
        out.append(("line badge", "¶ cited by sentence " + " ".join(s[:8] for s in n["sentences"])))
    out.append(("line deep-dive", n["deep_dive_state"]))
    return out


def canvas_lines(n: dict) -> list[tuple[str, str]]:
    """The lines a node box draws: a value line cut to the box, every other line wrapped."""
    out = []
    for cls, text in node_lines(n):
        if "value" in cls.split():
            out.append((cls, _fit(text)))
        else:
            out.extend((cls, part) for part in wrap(text))
    return out


def _node(n: dict, x: int, y: int, h: int, order: int, focus: str) -> str:
    w = layout_mod.NODE_W
    classes = ["node", f"k-{n['kind']}"]
    if n["node_id"] == focus:
        classes.append("focus")
    if n["vouch_tokens"]:
        classes.append("not-vouched")
    if n["revoked"]:
        classes.append("tombstone")
    g = {
        "class": " ".join(classes),
        "data-node": n["node_id"],
        "data-kind": n["kind"],
        "data-order": order,
        "data-lineage": " ".join(n["lineage_heads"]),
        "data-sector": n["sector"] or "fusion",
        "transform": f"translate({x} {y})",
    }
    parts = [f"<g{_attrs(g)}>"]
    box = {"class": "box", "x": -w // 2, "y": -h // 2, "width": w, "height": h}
    parts.append(f"<rect{_attrs(box)}/>")
    if n["vouch_tokens"]:
        band = {"class": "vouch-band", "x": -w // 2, "y": -h // 2, "width": 8, "height": h, "fill": "url(#hatch)"}
        parts.append(f"<rect{_attrs(band)}/>")
    if n["kind"] == "cluster":
        x0, y0, x1, y1, k = -w // 2 - 6, -h // 2 - 6, w // 2 + 6, h // 2 + 6, 14
        for d in (
            f"M {x0} {y0 + k} L {x0} {y0} L {x0 + k} {y0}",
            f"M {x1 - k} {y0} L {x1} {y0} L {x1} {y0 + k}",
            f"M {x0} {y1 - k} L {x0} {y1} L {x0 + k} {y1}",
            f"M {x1 - k} {y1} L {x1} {y1} L {x1} {y1 - k}",
        ):
            parts.append(f'<path class="bracket" d="{d}"/>')
    ty = -h // 2 + layout_mod.PAD + 11
    for cls, text in canvas_lines(n):
        attrs = {"class": cls, "x": -w // 2 + 14, "y": ty}
        if "generated" in cls:
            attrs["font-style"] = "italic"
        if "struck" in cls:
            attrs["text-decoration"] = "line-through"
        parts.append(f"<text{_attrs(attrs)}>{escape(text)}</text>")
        ty += layout_mod.LINE_H
    parts.append("</g>")
    return "".join(parts)


def _edge_groups(edges: list[dict]) -> list[list[dict]]:
    """Proposals on one pair share one path; every other edge has its own."""
    groups: dict[tuple, list[dict]] = {}
    for e in edges:
        if e["kind"] == "proposes":
            key = ("proposes",) + tuple(sorted((e["src_id"], e["dst_id"])))
        else:
            key = ("edge", e["edge_id"])
        groups.setdefault(key, []).append(e)
    return [sorted(g, key=lambda e: e["edge_id"]) for _, g in sorted(groups.items())]


def _edges(edges: list[dict], pos: dict) -> tuple[list[str], list[str]]:
    """(the edge lines, their labels). The two are painted in separate layers."""
    lines, labels = [], []
    for group in _edge_groups(edges):
        first = group[0]
        if first["src_id"] not in pos or first["dst_id"] not in pos:
            continue
        (x1, y1), (x2, y2) = pos[first["src_id"]], pos[first["dst_id"]]
        layer = first["layer"]
        g = {
            "class": f"edge e-{layer} k-{first['kind']}",
            "data-edges": " ".join(e["edge_id"] for e in group),
            "data-layer": layer,
        }
        line = {"class": "edge-line", "d": f"M {x1} {y1} L {x2} {y2}"}
        line.update(LAYER_STYLE[layer])
        lines.append(f"<g{_attrs(g)}><path{_attrs(line)}/></g>")
        mx, my = (x1 + x2) // 2, (y1 + y2) // 2
        parts = [f"<g{_attrs({'class': 'edge-label-group', 'data-label-layer': layer})}>"]
        for i, e in enumerate(group):
            label = {
                "class": "edge-label" + (" struck" if e.get("withdrawn") else ""),
                "x": mx + 6,
                "y": my - 4 + i * 14,
                "data-edge": e["edge_id"],
                "data-lineage": e["event_id"],
            }
            parts.append(f"<text{_attrs(label)}>{escape(e['text'])}</text>")
        parts.append("</g>")
        labels.append("".join(parts))
    return lines, labels


def render(web: Web, standalone: bool = True) -> str:
    """The SVG document for a web under its caps. The caller never calls this over cap."""
    cards = collapsed_cards(web)
    nodes = [dict(n, canvas_lines=len(canvas_lines(n))) for n in web.nodes]
    placed = layout_mod.place(nodes, cards, web.hops)
    pos, heights = placed["pos"], placed["heights"]
    x0, y0, w, h = placed["box"]
    root = {
        "xmlns": "http://www.w3.org/2000/svg",
        "class": "web",
        "viewBox": f"{x0} {y0} {w} {h}",
        "width": w,
        "height": h,
        "data-case": web.case_id,
        "data-focus": web.focus,
        "data-hops": web.hops,
        "role": "img",
        "aria-label": "WEB view: the list twin on key t carries the same nodes and edges as text",
    }
    parts = []
    if standalone:
        parts.append('<?xml version="1.0" encoding="UTF-8"?>\n')
        parts.append('<?xml-stylesheet type="text/css" href="/static/app.css"?>\n')
    parts.append(f"<svg{_attrs(root)}>")
    parts.append(
        '<defs><pattern id="hatch" patternUnits="userSpaceOnUse" width="6" height="6" '
        'patternTransform="rotate(45)"><rect class="hatch-ground" width="6" height="6"/>'
        '<line class="hatch-line" x1="0" y1="0" x2="0" y2="6"/></pattern></defs>'
    )
    edge_lines, edge_labels = _edges(web.edges, pos)
    node_parts = []
    ordered = sorted(web.nodes, key=lambda n: (n["ring"], layout_mod.slot_of(n["sector"]), layout_mod.order_key(n)))
    for order, n in enumerate(ordered):
        x, y = pos[n["node_id"]]
        node_parts.append(_node(n, x, y, heights[n["node_id"]], order, web.focus))
    for c in cards:
        x, y = placed["cards"][c["sector"]]
        g = {"class": "node k-card", "data-sector": c["sector"], "transform": f"translate({x} {y})"}
        box = {"class": "box", "x": -layout_mod.NODE_W // 2, "y": -20, "width": layout_mod.NODE_W, "height": 40}
        node_parts.append(f"<g{_attrs(g)}><rect{_attrs(box)}/><text class=\"line\" x=\"{-layout_mod.NODE_W // 2 + 14}\" y=\"4\">{escape(c['text'])}</text></g>")
    layers = {"edges": edge_lines, "nodes": node_parts, "labels": edge_labels}
    for name in PAINT_ORDER:
        parts.append(f'<g class="{name}">')
        parts.extend(layers[name])
        parts.append("</g>")
    parts.append("</svg>")
    return "".join(parts)
