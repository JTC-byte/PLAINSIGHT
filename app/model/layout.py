"""The deterministic radial layout of a web.

The focus sits at the centre. A node's ring is its hop count from the focus.
Each sector owns a fixed angular slot, and inside a (ring, sector) group the
order is (selector_type or entity type or kind, node_id). There is no force
simulation, no persisted slot, no hub demotion and no random input, so two
renders of one web are byte-identical.

Coordinates are integers. Nothing here sizes, thickens, fades or weights a
node or an edge by any property of the data: every node box has the same
width, and its height follows the number of text lines it prints.
"""

from __future__ import annotations

import math

#: The fixed angular order of the slots. None holds clusters, which sit in no sector.
SLOTS = ("accounts", "names_aliases", "emails", "phones", "addresses", "organizations", "people", "other_osint", None)
SLOT_DEGREES = 360 / len(SLOTS)

RING_STEP = 420
STAGGER = 96
NODE_W = 300
LINE_H = 15
PAD = 10
MARGIN = 160


def order_key(node: dict) -> tuple:
    """The order inside one (ring, sector) group."""
    return (node.get("selector_type") or node.get("entity_type") or node.get("kind") or "", node["node_id"])


def node_height(node: dict) -> int:
    """The box height for the lines the renderer draws (canvas_lines, set by app/model/svg.py)."""
    lines = node.get("canvas_lines")
    if lines is None:
        lines = len(node.get("lines") or []) + 2  # the deep-dive line and the badge or token line
    return PAD * 2 + LINE_H * lines


def slot_of(sector) -> int:
    return SLOTS.index(sector) if sector in SLOTS else SLOTS.index(None)


def place(nodes: list[dict], cards: list[dict] | None = None, hops: int = 2) -> dict:
    """{'pos': {node_id: (x, y)}, 'cards': {sector: (x, y)}, 'box': (x, y, w, h)}."""
    pos: dict[str, tuple[int, int]] = {}
    groups: dict[tuple[int, int], list[dict]] = {}
    for n in nodes:
        if n["ring"] == 0:
            pos[n["node_id"]] = (0, 0)
            continue
        groups.setdefault((n["ring"], slot_of(n["sector"])), []).append(n)
    for (ring, slot), members in sorted(groups.items()):
        members = sorted(members, key=order_key)
        m = len(members)
        start = slot * SLOT_DEGREES - 90
        for i, n in enumerate(members):
            angle = math.radians(start + (i + 1) * SLOT_DEGREES / (m + 1))
            radius = ring * RING_STEP + (i % 3) * STAGGER
            pos[n["node_id"]] = (round(radius * math.cos(angle)), round(radius * math.sin(angle)))
    card_pos: dict[str, tuple[int, int]] = {}
    for c in sorted(cards or [], key=lambda c: slot_of(c["sector"])):
        angle = math.radians(slot_of(c["sector"]) * SLOT_DEGREES - 90 + SLOT_DEGREES / 2)
        radius = (hops + 1) * RING_STEP
        card_pos[c["sector"]] = (round(radius * math.cos(angle)), round(radius * math.sin(angle)))
    heights = {n["node_id"]: node_height(n) for n in nodes}
    xs = [x for x, _ in list(pos.values()) + list(card_pos.values())] or [0]
    ys = [y for _, y in list(pos.values()) + list(card_pos.values())] or [0]
    tallest = max(list(heights.values()) + [LINE_H * 3])
    x0 = min(xs) - NODE_W // 2 - MARGIN
    y0 = min(ys) - tallest // 2 - MARGIN
    w = max(xs) - min(xs) + NODE_W + 2 * MARGIN
    h = max(ys) - min(ys) + tallest + 2 * MARGIN
    return {"pos": pos, "cards": card_pos, "heights": heights, "box": (x0, y0, w, h)}
