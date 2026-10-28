"""Projections: the rows of tables 3, 4 and 7 to 11, derived from the log only.

A handler keyed by event type and subtype turns one envelope into projection
rows. The ingest transaction calls it after writing the skeleton and payload,
and python -m app rebuild calls the same handler over the stored log in seq
order, so a rebuild of an unswept store reproduces every projection row.

What the projections never do, each because a governed rule says so:

- compute subject_relation or pivot_depth. They are copied from the gate's
  COLLECT PERMITTED decision through the run (SS-10).
- store a review state. It is projected at read time from the latest VERIFY or
  DISPUTE (contract section 8, D3).
- make a cluster from anything but an IDENTITY_EVENT CLUSTER from a named human
  (design 8.2 item 4). A LINK becomes an inference edge and nothing more.
- refuse an anchor tools/validate.py passed. A mismatch between the anchor
  claim's selector_type and anchor_selector_type is stored as
  anchor_vouched = 0, so the view can render "anchor unproven".
- put a value in a node id, an edge id or an edge label. A selector node's id
  is the event_id of the earliest claim carrying that (selector_type, value),
  and a label is a closed token.
"""

from __future__ import annotations

import json

import yaml

from app import config
from app.model import sectors
from app.store import retention, rollup

REGISTRY = config.REPO_ROOT / "ontology" / "selectors.yaml"

SEAM_CODES = frozenset("henbitgk")
EXCLUDE_LABEL = "excluded"


def selector_node_id(claim_event_id: str) -> str:
    """The id of a selector node: the event_id of its earliest claim. Never a value or a hash of one."""
    return claim_event_id


def _registry() -> dict:
    return yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))


class Projector:
    """Applies envelopes of one case to the projection tables, inside the caller's transaction."""

    def __init__(self, conn, case_id: str, blob_root=None):
        self.c = conn
        self.case_id = case_id
        self.blob_root = blob_root
        reg = _registry()
        self.selectors = reg["selectors"]
        self.label_tokens = (
            set(self.selectors)
            | {"same_entity", "associated_with", "co_located", "controls"}
            | {EXCLUDE_LABEL}
        )
        self.touched: dict[str, list[str]] = {}
        self.handlers = {
            ("PROBE_EVENT", "RUN_START"): self._run_start,
            ("PROBE_EVENT", "RUN_END"): self._run_end,
            ("PROBE_EVENT", "ITEM"): self._item,
            ("EXTRACT_EVENT", "CLAIM"): self._claim,
            ("IDENTITY_EVENT", "CLUSTER"): self._cluster,
            ("IDENTITY_EVENT", "EXCLUDE"): self._exclude,
            ("ADJUDICATE_EVENT", "PROMOTE"): self._promote,
            ("ADJUDICATE_EVENT", "REVOKE"): self._revoke,
            ("SYSTEM_EVENT", "COVERAGE_INTERVAL"): self._coverage,
            ("SYSTEM_EVENT", "RETENTION_EXTENSION"): self._extension,
            ("SYSTEM_EVENT", "RETENTION_FREEZE"): self._freeze,
            ("SYSTEM_EVENT", "RETENTION_RENEWAL"): self._freeze,
        }
        for sub in ("SAME_ENTITY", "ASSOCIATED_WITH", "CO_LOCATED", "CONTROLS"):
            self.handlers[("LINK_EVENT", sub)] = self._link

    # -- entry points ------------------------------------------------------

    def count_event(self, env: dict) -> None:
        """The skeleton counts, made for every stored event whether or not its payload survives."""
        ev = env["event"]
        rollup.increment(self.c, "event_type", ev["event_type"])
        rollup.increment(self.c, "event_subtype", f"{ev['event_type']}.{ev['event_subtype']}")
        self._touch("case", self.case_id)

    def apply(self, env: dict) -> None:
        ev = env["event"]
        handler = self.handlers.get((ev["event_type"], ev["event_subtype"]))
        if handler is not None:
            handler(env, env.get("payload") or {})

    def finish(self) -> None:
        """Node expiry: the latest expires_at among the claims that hold the node."""
        claims = {r["claim_id"]: r for r in self.c.execute("SELECT claim_id, selector_type, value, expires_at FROM claim")}
        edges = list(self.c.execute("SELECT src_id, dst_id, event_id FROM edge"))
        for node in list(self.c.execute("SELECT node_id, kind, created_by_event_id, expires_at FROM node")):
            holders = set()
            nid = node["node_id"]
            if node["kind"] == "selector" and node["created_by_event_id"] in claims:
                anchor = claims[node["created_by_event_id"]]
                holders |= {
                    cid for cid, r in claims.items()
                    if r["selector_type"] == anchor["selector_type"] and r["value"] == anchor["value"]
                }
            sources = [node["created_by_event_id"]] + [e["event_id"] for e in edges if nid in (e["src_id"], e["dst_id"])]
            for eid in sources:
                if eid in claims:
                    holders.add(eid)
                else:
                    holders |= {p for p in self._parents(eid) if p in claims}
            dates = [claims[h]["expires_at"] for h in holders if claims[h]["expires_at"]]
            value = max(dates, key=retention.parse_ts) if dates else None
            if value != node["expires_at"]:
                self.c.execute("UPDATE node SET expires_at = ? WHERE node_id = ?", (value, nid))

    # -- reads -------------------------------------------------------------

    def _registry_row(self):
        return self.c.execute("SELECT * FROM case_registry WHERE case_id = ?", (self.case_id,)).fetchone()

    def _event(self, eid):
        """(type, subtype, payload) of a stored event of this case, or None."""
        row = self.c.execute(
            "SELECT s.event_type, s.event_subtype, s.payload_stratum, s.payload_inline, p.payload_json "
            "FROM event_skeleton s LEFT JOIN event_payload p ON p.event_id = s.event_id "
            "WHERE s.event_id = ? AND s.case_id = ?",
            (eid, self.case_id),
        ).fetchone()
        if row is None:
            return None
        raw = row["payload_inline"] if row["payload_stratum"] == 2 else row["payload_json"]
        return row["event_type"], row["event_subtype"], (json.loads(raw) if raw else None)

    def _parents(self, eid) -> list[str]:
        row = self.c.execute("SELECT parents_json FROM event_skeleton WHERE event_id = ?", (eid,)).fetchone()
        return json.loads(row["parents_json"]) if row and row["parents_json"] else []

    def _node(self, nid):
        return self.c.execute("SELECT * FROM node WHERE node_id = ?", (nid,)).fetchone()

    def _selector_node_for(self, selector_type, value):
        """The selector node for an exact (selector_type, value): the node its earliest claim created."""
        row = self.c.execute(
            "SELECT n.node_id FROM node n JOIN claim c ON c.claim_id = n.created_by_event_id "
            "WHERE n.kind = 'selector' AND c.selector_type = ? AND c.value = ?",
            (selector_type, value),
        ).fetchone()
        return row["node_id"] if row else None

    def _node_for_event(self, eid):
        """The node an event stands for: a claim's selector node, a cluster, an entity or a candidate."""
        found = self._event(eid)
        if found is None:
            return None
        etype, esub, payload = found
        payload = payload or {}
        if (etype, esub) == ("EXTRACT_EVENT", "CLAIM"):
            return self._selector_node_for(payload.get("selector_type"), payload.get("value"))
        if (etype, esub) == ("IDENTITY_EVENT", "CLUSTER"):
            return payload.get("cluster_id")
        if (etype, esub) == ("IDENTITY_EVENT", "EXCLUDE"):
            return payload.get("candidate_ref")
        if (etype, esub) == ("ADJUDICATE_EVENT", "PROMOTE"):
            return payload.get("entity_id")
        return None

    # -- writes ------------------------------------------------------------

    def _touch(self, kind: str, ident: str) -> None:
        bucket = self.touched.setdefault(kind, [])
        if ident not in bucket:
            bucket.append(ident)

    def _node_pairs(self, row: dict) -> list[tuple[str, str]]:
        pairs = [("node_kind", row["kind"])]
        if row.get("sector"):
            pairs.append(("sector", row["sector"]))
        if row["kind"] == "entity" and row.get("entity_type"):
            pairs.append(("entity_type", row["entity_type"]))
        return pairs

    def _put_node(self, row: dict) -> None:
        """Insert a node, or replace an existing one, keeping the rollup in step."""
        old = self._node(row["node_id"])
        full = {
            "node_id": row["node_id"],
            "kind": row["kind"],
            "entity_type": row.get("entity_type"),
            "selector_type": row.get("selector_type"),
            "anchor_selector_type": row.get("anchor_selector_type"),
            "anchor_claim_id": row.get("anchor_claim_id"),
            "anchor_vouched": row.get("anchor_vouched"),
            "sector": row.get("sector"),
            "created_by_event_id": row["created_by_event_id"],
            "revoked_by_event_id": row.get("revoked_by_event_id"),
            "expires_at": row.get("expires_at"),
        }
        if old is not None:
            for dim, bucket in self._node_pairs(dict(old)):
                rollup.increment(self.c, dim, bucket, -1)
            self.c.execute("DELETE FROM node WHERE node_id = ?", (row["node_id"],))
        cols = ", ".join(full)
        marks = ", ".join("?" for _ in full)
        self.c.execute(f"INSERT INTO node ({cols}) VALUES ({marks})", tuple(full.values()))
        for dim, bucket in self._node_pairs(full):
            rollup.increment(self.c, dim, bucket, 1)
        self._touch("nodes", row["node_id"])

    def _ensure_referenced(self, nid: str, event_id: str) -> None:
        """A referenced-only node for an id a LINK, CLUSTER or EXCLUDE names with no PROMOTE."""
        if self._node(nid) is None:
            self._put_node({
                "node_id": nid,
                "kind": "referenced",
                "sector": sectors.KIND_SECTOR["referenced"],
                "created_by_event_id": event_id,
            })

    def _edge(self, kind, src, dst, layer, label, actor, ts, event_id) -> None:
        tokens = set(label.split(","))
        if not (tokens <= self.label_tokens or tokens <= SEAM_CODES):
            raise ValueError("an edge label must be a closed token")
        n = self.c.execute("SELECT COUNT(*) FROM edge WHERE event_id = ?", (event_id,)).fetchone()[0]
        self.c.execute(
            "INSERT INTO edge (edge_id, kind, src_id, dst_id, layer, label, actor, ts, event_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (f"{event_id}#{n}", kind, src, dst, layer, label, actor, ts, event_id),
        )
        rollup.increment(self.c, "edge_kind", kind)
        self._touch("edges", event_id)

    def _observed_about(self, claim_id: str, entity_id: str) -> None:
        exists = self.c.execute(
            "SELECT 1 FROM edge WHERE kind = 'observed_about' AND event_id = ? AND dst_id = ?",
            (claim_id, entity_id),
        ).fetchone()
        if exists:
            return
        claim = self.c.execute("SELECT selector_type, value FROM claim WHERE claim_id = ?", (claim_id,)).fetchone()
        src = self._selector_node_for(claim["selector_type"], claim["value"])
        ts = self.c.execute("SELECT ts, producer FROM event_skeleton WHERE event_id = ?", (claim_id,)).fetchone()
        self._edge("observed_about", src, entity_id, "observation", claim["selector_type"], ts["producer"], ts["ts"], claim_id)

    # -- handlers ----------------------------------------------------------

    def _run_start(self, env, p) -> None:
        permitted_id, decision = None, {}
        for pid in (env.get("lineage") or {}).get("based_on") or []:
            found = self._event(pid)
            if found and found[:2] == ("COLLECT_EVENT", "PERMITTED"):
                permitted_id, decision = pid, found[2] or {}
                break
        egress = p.get("egress") or {}
        self.c.execute(
            "INSERT INTO run (run_id, case_id, start_event_id, permitted_event_id, connector_id, "
            "connector_version, connector_kind, credential_id, egress_environment, egress_identity, "
            "argv_template, target_selector_type, motivated_by, subject_relation, pivot_depth, "
            "authorization_ref, manifest_hash, started_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                p.get("run_id"), self.case_id, env["event"]["event_id"], permitted_id, p.get("connector_id"),
                p.get("connector_version"), p.get("connector_kind"), p.get("credential_id"),
                egress.get("environment"), egress.get("egress_identity"), p.get("argv_template"),
                p.get("target_selector_type"), p.get("motivated_by"), decision.get("subject_relation"),
                decision.get("pivot_depth"), decision.get("authorization_ref"), p.get("manifest_hash"),
                env["event"]["ts"],
            ),
        )
        self._touch("runs", p.get("run_id"))

    def _run_end(self, env, p) -> None:
        self.c.execute(
            "UPDATE run SET end_event_id = ?, ended_at = ?, exit_code = ?, item_count = ? "
            "WHERE run_id = ? AND case_id = ?",
            (env["event"]["event_id"], env["event"]["ts"], p.get("exit_code"), p.get("item_count"), p.get("run_id"), self.case_id),
        )
        self._touch("runs", p.get("run_id"))

    def _item(self, env, p) -> None:
        run = self.c.execute("SELECT subject_relation FROM run WHERE run_id = ?", (p.get("run_id"),)).fetchone()
        relation = run["subject_relation"] if run else None
        reg = self._registry_row()
        raw = p.get("raw_ref") or {}
        sha = raw.get("blob_sha256")
        held = False
        if self.blob_root is not None and isinstance(sha, str) and len(sha) == 64:
            held = (self.blob_root / self.case_id / sha[:2] / sha).is_file()
        self.c.execute(
            "INSERT INTO item (item_id, event_id, run_id, locator, outcome, blob_sha256, blob_state, "
            "raw_span_json, subject_relation, expires_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                p.get("item_id"), env["event"]["event_id"], p.get("run_id"), p.get("locator"), p.get("outcome"),
                sha, "held" if held else "absent",
                None if raw.get("raw_span") is None else json.dumps(raw.get("raw_span"), separators=(",", ":")),
                relation,
                retention.expiry(relation, reg["retain_until"], env["event"]["ts"], reg["incidental_ttl_days"]),
            ),
        )
        if p.get("outcome"):
            rollup.increment(self.c, "item_outcome", p["outcome"])

    def _claim(self, env, p) -> None:
        eid = env["event"]["event_id"]
        src = p.get("source_ref") or {}
        item = self.c.execute("SELECT item_id, event_id, run_id FROM item WHERE item_id = ?", (src.get("item_id"),)).fetchone()
        run = None
        if item is not None:
            run = self.c.execute(
                "SELECT permitted_event_id, subject_relation, pivot_depth FROM run WHERE run_id = ?",
                (item["run_id"],),
            ).fetchone()
        entry = self.selectors.get(p.get("selector_type")) or {}
        temporal = p.get("temporal") or {}
        reg = self._registry_row()
        relation = run["subject_relation"] if run else None
        extractor = p.get("extractor") or {}
        self.c.execute(
            "INSERT INTO claim (claim_id, item_id, run_id, permit_event_id, subject_relation, pivot_depth, "
            "selector_type, value, subject_ref, source_path, extractor, observed_at, asserted_at, "
            "time_provenance, negative_state, provenance_state, datum_class, injection_tagged, expires_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                eid, src.get("item_id"), item["run_id"] if item else None,
                run["permitted_event_id"] if run else None, relation, run["pivot_depth"] if run else None,
                p.get("selector_type"), p.get("value"), p.get("subject_ref"), src.get("source_path"),
                f"{extractor.get('name')}@{extractor.get('version')}", temporal.get("observed_at"),
                temporal.get("asserted_at"), temporal.get("time_provenance"), p.get("negative_state"),
                entry.get("provenance_state", "OBSERVED"), entry.get("datum_class"),
                None if p.get("injection_tagged") is None else int(bool(p.get("injection_tagged"))),
                retention.expiry(relation, reg["retain_until"], temporal.get("observed_at"), reg["incidental_ttl_days"]),
            ),
        )
        rollup.increment(self.c, "selector_type", p.get("selector_type"))
        self._touch("claims", eid)
        if self._selector_node_for(p.get("selector_type"), p.get("value")) is None:
            self._put_node({
                "node_id": selector_node_id(eid),
                "kind": "selector",
                "selector_type": p.get("selector_type"),
                "sector": sectors.sector_of(p.get("selector_type")),
                "created_by_event_id": eid,
            })
        # observed_about: the item was already promoted, or the claim names an entity
        if item is not None:
            for entity_id in self._entities_from_item(item["event_id"]):
                self._observed_about(eid, entity_id)
        subject = p.get("subject_ref")
        if subject:
            node = self._node(subject)
            if node is not None and node["kind"] == "entity":
                self._observed_about(eid, subject)

    def _entities_from_item(self, item_event_id) -> list[str]:
        out = []
        rows = self.c.execute(
            "SELECT s.event_id, p.payload_json FROM event_skeleton s JOIN event_payload p ON p.event_id = s.event_id "
            "WHERE s.case_id = ? AND s.event_type = 'ADJUDICATE_EVENT' AND s.event_subtype = 'PROMOTE' ORDER BY s.seq",
            (self.case_id,),
        )
        for row in rows:
            payload = json.loads(row["payload_json"])
            if payload.get("promotion_kind") == "item_to_entity" and payload.get("target_ref") == item_event_id:
                if payload.get("entity_id") and self._node(payload["entity_id"]) is not None:
                    out.append(payload["entity_id"])
        return out

    def _link(self, env, p) -> None:
        refs = ((p.get("claim") or {}).get("subject_refs")) or []
        eid = env["event"]["event_id"]
        label = (p.get("link_type") or env["event"]["event_subtype"]).lower()
        for ref in refs:
            self._ensure_referenced(ref, eid)
        for other in refs[1:]:
            self._edge("proposes", refs[0], other, "inference", label, env["source"]["producer"], env["event"]["ts"], eid)

    def _cluster(self, env, p) -> None:
        eid = env["event"]["event_id"]
        cid = p.get("cluster_id")
        self._put_node({
            "node_id": cid,
            "kind": "cluster",
            "sector": sectors.KIND_SECTOR["cluster"],
            "created_by_event_id": eid,
        })
        seams = p.get("member_seams") or {}
        for member in p.get("members") or []:
            self._ensure_referenced(member, eid)
            label = ",".join(seams.get(member) or [])
            self._edge("member_of", member, cid, "fusion", label, env["source"]["producer"], env["event"]["ts"], eid)

    def _exclude(self, env, p) -> None:
        eid = env["event"]["event_id"]
        cand = p.get("candidate_ref")
        existing = self._node(cand)
        if existing is None or existing["kind"] == "referenced":
            self._put_node({
                "node_id": cand,
                "kind": "candidate",
                "sector": sectors.KIND_SECTOR["candidate"],
                "created_by_event_id": eid,
            })
        parents = (env.get("lineage") or {}).get("based_on") or []
        src = self._node_for_event(parents[0]) if parents else None
        if src is not None:
            self._edge("excludes", src, cand, "fusion", EXCLUDE_LABEL, env["source"]["producer"], env["event"]["ts"], eid)

    def _promote(self, env, p) -> None:
        if p.get("promotion_kind") != "item_to_entity":
            return
        eid = env["event"]["event_id"]
        entity_id = p.get("entity_id")
        anchor = p.get("anchor_claim_ref")
        anchor_claim = self.c.execute("SELECT selector_type FROM claim WHERE claim_id = ?", (anchor,)).fetchone()
        vouched = 1 if anchor_claim is not None and anchor_claim["selector_type"] == p.get("anchor_selector_type") else 0
        self._put_node({
            "node_id": entity_id,
            "kind": "entity",
            "entity_type": p.get("entity_type"),
            "anchor_selector_type": p.get("anchor_selector_type"),
            "anchor_claim_id": anchor,
            "anchor_vouched": vouched,
            "sector": sectors.sector_of(p.get("entity_type")),
            "created_by_event_id": eid,
        })
        item = self.c.execute("SELECT item_id FROM item WHERE event_id = ?", (p.get("target_ref"),)).fetchone()
        claim_ids = []
        if item is not None:
            claim_ids += [r[0] for r in self.c.execute("SELECT claim_id FROM claim WHERE item_id = ? ORDER BY claim_id", (item["item_id"],))]
        claim_ids += [r[0] for r in self.c.execute("SELECT claim_id FROM claim WHERE subject_ref = ? ORDER BY claim_id", (entity_id,))]
        seq = {r[0]: r[1] for r in self.c.execute("SELECT event_id, seq FROM event_skeleton WHERE case_id = ?", (self.case_id,))}
        for cid in sorted(dict.fromkeys(claim_ids), key=lambda c: seq.get(c, 0)):
            self._observed_about(cid, entity_id)

    def _revoke(self, env, p) -> None:
        """A revoked cluster, entity or candidate is marked on its node. A revoked LINK
        leaves its edges as they are: the views read the REVOKE from the log at read
        time (app/model/reads.py revocations) and draw the proposal as withdrawn."""
        target = p.get("target_ref")
        nid = self._node_for_event(target)
        if nid is not None and self._node(nid) is not None:
            self.c.execute("UPDATE node SET revoked_by_event_id = ? WHERE node_id = ?", (env["event"]["event_id"], nid))
            self._touch("nodes", nid)
        if self.c.execute("SELECT 1 FROM edge WHERE event_id = ? AND kind = 'proposes'", (target,)).fetchone():
            self._touch("edges", target)

    def _coverage(self, env, p) -> None:
        eid = env["event"]["event_id"]
        self.c.execute(
            "DELETE FROM coverage_interval WHERE case_id = ? AND target_ref = ? AND t_start = ? AND state = 'open'",
            (self.case_id, p.get("target_ref"), p.get("t_start")),
        )
        self.c.execute(
            "INSERT INTO coverage_interval (interval_id, case_id, target_ref, t_start, last_verified_at, "
            "poll_interval_s, t_end, state, closed_by_event_id, closed_by_producer, verified, method) "
            "VALUES (?, ?, ?, ?, ?, NULL, ?, 'closed', ?, ?, ?, ?)",
            (
                eid, self.case_id, p.get("target_ref"), p.get("t_start"), p.get("t_end"), p.get("t_end"),
                eid, env["source"]["producer"], None if p.get("verified") is None else int(bool(p.get("verified"))),
                p.get("method"),
            ),
        )
        self._touch("coverage", eid)

    def _extension(self, env, p) -> None:
        new = p.get("new_retain_until")
        self.c.execute("UPDATE case_registry SET retain_until = ? WHERE case_id = ?", (new, self.case_id))
        instant = retention.date_instant(new)
        self.c.execute("UPDATE claim SET expires_at = ? WHERE subject_relation IN ('seed', 'pivot')", (instant,))
        self.c.execute("UPDATE item SET expires_at = ? WHERE subject_relation IN ('seed', 'pivot')", (instant,))

    def _freeze(self, env, p) -> None:
        self.c.execute(
            "UPDATE case_registry SET frozen_until = ? WHERE case_id = ?",
            (p.get("freeze_expires_on"), self.case_id),
        )
