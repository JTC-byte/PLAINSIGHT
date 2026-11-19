// The reading rules of the Connections web (docs/PLAINSIGHT-design.md amendment
// 9.31). They decide what is drawn at once, never what exists: a hidden label is
// one selection away, and a node outside the display depth is one click away.
// This file imports nothing and touches no DOM, so app/tests/test_showcase.py
// runs it under node.

/** The most nodes the web opens on at three hops; past it, it opens at two and says why. */
export const LEGIBLE_NODES = 40;

/** The display depth the web opens at, given how many nodes the three-hop web holds (null when not known). */
export function defaultHops(nodesAtThree) {
  return typeof nodesAtThree === "number" && nodesAtThree > LEGIBLE_NODES ? 2 : 3;
}

/** Whether one pair's label is drawn: only for the selected link, and for the links of the selected or the pointed-at node. At rest the line's style alone shows, and the key above the web says what each style means. */
export function labelShown(pair, selNode, selEdge, hoverNode) {
  const ends = String(pair).split("|");
  return pair === selEdge || (!!selNode && ends.includes(selNode)) || (!!hoverNode && ends.includes(hoverNode));
}

/** The stage's height in pixels, grown with the node count so a ring has room. */
export function stageHeight(nodes) {
  return Math.max(600, Math.min(1700, 200 + 22 * nodes));
}
