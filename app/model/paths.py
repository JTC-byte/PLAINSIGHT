"""PATHS: the routes of at most three hops between two marked nodes.

A recursive CTE walks the edge table in both directions without revisiting a
node. Each row is a chain of labelled predicates, and its weakest link is named
in words. No number is computed and none is printed: the weakest link is chosen
by a fixed order of edge classes, and an assertion prints its band word as it
stands, without ranking one band against another.

The fixed order, weakest first:

1. a revoked assertion (a member line of a tombstoned cluster) or a withdrawn
   proposal (a LINK an ADJUDICATE REVOKE names);
2. an exclusion, which asserts no connection;
3. an unaccepted proposal, weaker than any assertion;
4. an observation whose relation is unstated;
5. an assertion by a named human, printed with its band.

PATHS and the web's list twin are the fallback past the canvas cap and the
keyboard and screen-reader form of the web.
"""

from __future__ import annotations

import json

from app.model import reads
from app.refusals import Refusal

MAX_HOPS = 3

#: The most routes one request lists. Past it the response says so in words.
MAX_ROUTES = 200

WEAKNESS = ("revoked", "exclusion", "proposal", "observation", "assertion")

ROUTES = """
WITH RECURSIVE und(a, b, edge_id) AS (
    SELECT src_id, dst_id, edge_id FROM edge
    UNION ALL
    SELECT dst_id, src_id, edge_id FROM edge
),
walk(node, nodes, edges, depth) AS (
    SELECT ?, json_array(?), json_array(), 0
    UNION ALL
    SELECT u.b, json_insert(w.nodes, '$[#]', u.b), json_insert(w.edges, '$[#]', u.edge_id), w.depth + 1
    FROM walk w JOIN und u ON u.a = w.node
    WHERE w.depth < ? AND w.node != ?
      AND NOT EXISTS (SELECT 1 FROM json_each(w.nodes) j WHERE j.value = u.b)
)
SELECT nodes, edges FROM walk WHERE node = ? ORDER BY depth, edges LIMIT ?
"""


def classify(conn, case_id: str, edge: dict, clusters: dict, revoked: dict | None = None) -> tuple[str, str]:
    """(weakness class, words) for one edge."""
    if edge["kind"] == "proposes" and (revoked or {}).get(edge["event_id"]) is not None:
        return "revoked", f"a withdrawn proposal: LINK {edge['event_id'][:8]} was revoked and no longer stands"
    if edge["kind"] == "member_of":
        cluster = clusters.get(edge["dst_id"])
        created = reads.event(conn, case_id, cluster["created_by_event_id"]) if cluster else None
        p = (created or {}).get("payload") or {}
        if cluster is not None and cluster["revoked_by_event_id"]:
            return "revoked", f"a revoked assertion: cluster {edge['dst_id'][:8]} was withdrawn"
        return "assertion", f"an assertion by {p.get('asserted_by') or edge['actor']}, band {p.get('band') or 'not recorded'}"
    if edge["kind"] == "excludes":
        return "exclusion", "an exclusion, which asserts no connection"
    if edge["kind"] == "proposes":
        return "proposal", f"an unaccepted proposal ({edge['label']} by {edge['actor']}): no analyst has asserted this"
    return "observation", f"an observation of {edge['label']}, relation unstated"


def routes(conn, case_id: str, src: str | None, dst: str | None) -> dict:
    if not src or not dst:
        raise Refusal("FOCUS_REQUIRED", "route: paths needs from and to")
    for nid in (src, dst):
        if reads.node(conn, nid) is None:
            raise Refusal("NODE_NOT_IN_CASE", "route: paths")
    rows = list(conn.execute(ROUTES, (src, src, MAX_HOPS, dst, dst, MAX_ROUTES + 1)))
    more = len(rows) > MAX_ROUTES
    edge_rows = {r["edge_id"]: dict(r) for r in conn.execute("SELECT * FROM edge")}
    clusters = {r["node_id"]: dict(r) for r in conn.execute("SELECT * FROM node WHERE kind = 'cluster'")}
    revoked = reads.revocations(conn, case_id)
    out = []
    for r in rows[:MAX_ROUTES]:
        nodes = json.loads(r["nodes"])
        hops = []
        for i, eid in enumerate(json.loads(r["edges"])):
            e = edge_rows[eid]
            cls, words = classify(conn, case_id, e, clusters, revoked)
            hops.append({
                "from": nodes[i],
                "to": nodes[i + 1],
                "edge_id": eid,
                "kind": e["kind"],
                "layer": e["layer"],
                "label": e["label"],
                "event_id": e["event_id"],
                "class": cls,
                "words": words,
            })
        weakest = min(hops, key=lambda h: WEAKNESS.index(h["class"]))
        out.append({"nodes": nodes, "hops": hops, "weakest": f"weakest link: {weakest['words']}"})
    return {
        "from": src,
        "to": dst,
        "max_hops": MAX_HOPS,
        "routes": out,
        "more": f"more than {MAX_ROUTES} routes exist; mark nodes closer together" if more else None,
        "none": None if out else f"no route of at most {MAX_HOPS} hops joins these two nodes in this case",
    }
