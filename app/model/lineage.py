"""The Lineage Drawer's model: the chain behind an event, and what depends on it.

Tier 1 is the chain, walked back over parents_json with WITH RECURSIVE:
sentence, cluster or tombstone, LINK, claim, item, RUN_START, COLLECT PERMITTED,
then the authorization's GRANT, EXTEND and REVOKE (amendment 9.9). Tier 2 is
the decoded envelope. Tier 3 is RAW, which reads "not held" on LOCAL.

A missing link renders "▨ chain broken at <event_id>" and the walk stops on that
branch; it never skips. A link is missing when the parent is not in the log, or
when the projection row the chain passes through (claim, item, run) is gone.

Flags render as consequences and never refuse, because chain rules belong to
the gate (VA-U1): a decision recorded after its authorization was revoked, an
authorization past its expires_on, and a chain that cites a cluster or a
proposal an ADJUDICATE REVOKE has withdrawn. A withdrawn cluster or LINK also
carries its REVOKED line in its own entry, so the tombstone names who asserted
and who revoked (design section 5.6).

RAW carries raw_vouch beside its text. It is true only when the item's bytes are
not held, which is the one RAW state the system does not vouch for; the client
paints red and the hatch from that flag and never from the text.

The drawer shows argv_template and never a filled argv (contract section 6).

Each entry's summary is closed fields only (amendment 9.30). An ITEM names the
site its locator names, the part before the first slash, read only for the two
locator kinds this module knows (site: and sherlock-site:) and resolved to a
platform where the repository holds a mapping, which today is Sherlock's site
facts; the part after the slash, which carries the subject's path on that site,
is never quoted. A RUN_START names the egress identity it collected through, the
machine it ran on and its manifest hash, shortened. A CLAIM
names its extractor and its lineage transform. A claim's value, a filled argv
and a full locator stay in the decoded-envelope tier, which shows them already.

The back chain also carries `audit`, the same entries read oldest first as one
row per step, with the VERIFY and DISPUTE acts on the chain's claims added as
reviews, so an auditor reads where the data came from and what handled it in
one pass. Forward lineage carries no audit.
"""

from __future__ import annotations

import functools
import json
from datetime import datetime

from app import config
from app.model import reads
from app.refusals import Refusal
from app.store import blobs, envelope

BROKEN = "▨ chain broken at {}"
MAX_DEPTH = 12
SHORT_HASH = 12

#: Locator kinds whose part before the first slash names a site, each with the connector folder whose
#: site_facts.json maps that site to a platform, or None where the repository holds no mapping. A locator
#: of any other kind may carry a channel or another case value before its slash, so it is not read.
SITE_SCHEMES = {"site": None, "sherlock-site": "sherlock"}

#: The audit trail's steps in the order a chain is built, which breaks a tie between two equal times.
AUDIT_STEPS = ("authorized", "gate", "collected", "fetched", "processed", "proposed", "asserted", "reviewed", "assessed")
AUTHORIZE_LABELS = {"GRANT": "Authorized", "EXTEND": "Extended", "REVOKE": "Authorization revoked"}
REVIEW_LABELS = {"VERIFY": "Verified", "DISPUTE": "Disputed", "PROMOTE": "Promoted", "IGNORE": "Ignored", "REVOKE": "Revoked"}

WALK_BACK = """
WITH RECURSIVE walk(event_id, depth, child) AS (
    SELECT ?, 0, NULL
    UNION
    SELECT j.value, w.depth + 1, w.event_id
    FROM walk w
    JOIN event_skeleton s ON s.event_id = w.event_id AND s.case_id = ?
    JOIN json_each(COALESCE(s.parents_json, '[]')) j
    WHERE w.depth < ?
)
SELECT event_id, MIN(depth) AS depth, MIN(child) AS child FROM walk GROUP BY event_id ORDER BY depth, event_id
"""

WALK_FORWARD = """
WITH RECURSIVE walk(event_id, depth) AS (
    SELECT ?, 0
    UNION
    SELECT s.event_id, w.depth + 1
    FROM walk w
    JOIN event_skeleton s ON s.case_id = ? AND s.parents_json IS NOT NULL
    WHERE w.depth < ? AND EXISTS (SELECT 1 FROM json_each(s.parents_json) j WHERE j.value = w.event_id)
)
SELECT event_id, MIN(depth) AS depth FROM walk GROUP BY event_id ORDER BY depth, event_id
"""


def _summary(conn, e: dict, revoked: dict | None = None) -> list[str]:
    """Closed fields of one chain entry, rendered as text. No value that can carry a case value is quoted here."""
    out = _fields(conn, e)
    withdrawn = (revoked or {}).get(e["event_id"])
    if withdrawn is not None:
        what = "this proposal" if e["type"] == "LINK_EVENT" else "this assertion"
        out.append(reads.revoked_text(withdrawn, what))
    return out


def _fields(conn, e: dict) -> list[str]:
    p = e["payload"] or {}
    kind = (e["type"], e["subtype"])
    if kind == ("PROBE_EVENT", "RUN_START"):
        egress = p.get("egress") or {}
        out = [
            f"connector {p.get('connector_id')} {p.get('connector_version')} ({p.get('connector_kind')})",
            f"argv_template {p.get('argv_template')}",
            f"collected through egress identity {egress.get('egress_identity')} on {egress.get('environment')} egress",
            "credential " + (p.get("credential_id") or "none: no credential was used"),
            "motivated_by " + (p.get("motivated_by") or "none: a seed run"),
        ]
        skel = _skeleton(conn, e["event_id"])
        if skel is not None:
            version = f" {skel['sw_version']}" if skel["sw_version"] else ""
            out.append(f"ran on {skel['platform_id']} in {skel['environment']}, dispatched by {e['producer']}{version}")
        if p.get("manifest_hash"):
            out.append(f"manifest sha256 {_short_hash(p['manifest_hash'])}")
        return out
    if kind == ("PROBE_EVENT", "ITEM"):
        item = conn.execute("SELECT blob_state FROM item WHERE event_id = ?", (e["event_id"],)).fetchone()
        out = [f"outcome {p.get('outcome')}", fetched_from(p.get("locator"), p.get("outcome"))]
        if p.get("method_id"):
            out.append(f"reference method {p['method_id']}")
        statuses = p.get("http_status_chain") or []
        if statuses:
            out.append("HTTP status " + " then ".join(str(x) for x in statuses))
        raw = "raw bytes held" if item and item["blob_state"] == "held" else "raw bytes not held"
        digest = (p.get("raw_ref") or {}).get("blob_sha256") or p.get("raw_blob_sha256")
        if digest and raw == "raw bytes held":
            out.append(f"raw bytes held · blob sha256 {_short_hash(digest)}")
        elif digest:
            out.append(f"raw bytes not held · the item names blob sha256 {_short_hash(digest)}, which this store does not hold")
        else:
            out.append(raw)
        return out
    if kind == ("EXTRACT_EVENT", "CLAIM"):
        ext = p.get("extractor") or {}
        out = [
            f"claim {p.get('selector_type')}",
            f"extracted by {ext.get('name')} {ext.get('version')} at {(p.get('source_ref') or {}).get('source_path')}",
            f"time {((p.get('temporal') or {}).get('time_provenance'))}",
        ]
        skel = _skeleton(conn, e["event_id"])
        if skel is not None and skel["transform"]:
            out.append(transform_text(skel["transform"]))
        return out
    if e["type"] == "COLLECT_EVENT":
        return [reads.decision_text(e), f"authorization {p.get('authorization_ref') or 'none'}"]
    if e["type"] == "AUTHORIZE_EVENT":
        out = [f"{p.get('act')} by {p.get('authorized_by')}"]
        if p.get("expires_on"):
            out.append(f"expires_on {p['expires_on']} · pivot_depth_max {p.get('pivot_depth_max')}")
        return out
    if kind == ("IDENTITY_EVENT", "CLUSTER"):
        return [f"asserted {p.get('asserted_by')} · {p.get('band')} · rationale {','.join(p.get('rationale_codes') or [])}"]
    if e["type"] == "LINK_EVENT":
        model = p.get("model") or {}
        return [f"PROPOSED {str(p.get('link_type')).lower()} by {model.get('name')} {model.get('version')}, not accepted"]
    if kind == ("ADJUDICATE_EVENT", "PROMOTE"):
        return [f"promoted {p.get('promotion_kind')} to {p.get('entity_type')} by {p.get('analyst')}"]
    if e["type"] == "ADJUDICATE_EVENT":
        return [f"{e['subtype']} by {p.get('analyst') or e['producer']}"]
    if kind == ("ASSESS_EVENT", "SENTENCE"):
        return [f"sentence by {p.get('author')}"]
    return []


def _skeleton(conn, event_id: str):
    """The skeleton's closed source fields and lineage transform for one event."""
    return conn.execute(
        "SELECT platform_id, environment, sw_version, transform FROM event_skeleton WHERE event_id = ?", (event_id,)
    ).fetchone()


def _short_hash(value: str) -> str:
    """A digest shortened to SHORT_HASH hex characters, its sha256: prefix dropped."""
    text = str(value)
    if text.startswith("sha256:"):
        text = text[len("sha256:"):]
    return text[:SHORT_HASH] + "…"


@functools.lru_cache(maxsize=None)
def site_facts(connector: str) -> dict:
    """{site: facts} from connectors/<connector>/site_facts.json, or {} when the file cannot be read."""
    path = config.REPO_ROOT / "connectors" / connector / "site_facts.json"
    try:
        sites = json.loads(path.read_text(encoding="utf-8")).get("sites")
    except (OSError, ValueError, AttributeError):
        return {}
    return sites if isinstance(sites, dict) else {}


def fetched_from(locator, outcome="hit") -> str:
    """Where an item was fetched from, or probed where its outcome is not a hit: the site its locator names
    before the first slash, resolved to a platform where the repository maps it. The part after the slash
    is never quoted. A site: locator's first part is a site id by design section 2's ITEM convention; a
    sherlock-site: id is quoted only when it is a key of Sherlock's site facts."""
    verb = "fetched from" if outcome == "hit" else "probed"
    if not isinstance(locator, str) or not locator:
        return f"{verb}: the item names no locator"
    scheme, colon, site = locator.split("/", 1)[0].partition(":")
    if not colon or scheme not in SITE_SCHEMES or not site:
        return f"{verb} a locator of a kind the drawer does not read; the decoded envelope holds it"
    connector = SITE_SCHEMES[scheme]
    if connector is None:
        return f"{verb} site {site}"
    facts = site_facts(connector).get(site)
    if not isinstance(facts, dict):
        return f"{verb} a {connector} site its site facts do not list; the decoded envelope holds it"
    method = f"a {facts['method']} probe" if facts.get("method") else "a probe of unrecorded method"
    line = (f"{verb} platform {site}, by {method} as this repository's site facts for {connector} record it, "
            "which may differ from the version the run pinned")
    if facts.get("probe_host"):
        line += f", sent to {facts['probe_host']} rather than the displayed site"
    return line


def transform_text(transform: str) -> str:
    """A lineage transform in words: translate:<schema_id>@<adapter_version> names the adapter that shaped the output."""
    body = transform[len("translate:"):] if transform.startswith("translate:") else None
    if body and "@" in body:
        schema_id, _, version = body.rpartition("@")
        return f"translated by adapter {schema_id} {version} (lineage transform {transform})"
    return f"lineage transform {transform}"


_PROJECTION_CHECK = {
    ("EXTRACT_EVENT", "CLAIM"): "SELECT 1 FROM claim WHERE claim_id = ?",
    ("PROBE_EVENT", "ITEM"): "SELECT 1 FROM item WHERE event_id = ?",
    ("PROBE_EVENT", "RUN_START"): "SELECT 1 FROM run WHERE start_event_id = ?",
}


def _projection_present(conn, e: dict) -> bool:
    sql = _PROJECTION_CHECK.get((e["type"], e["subtype"]))
    return sql is None or conn.execute(sql, (e["event_id"],)).fetchone() is not None


def chain(conn, case_id: str, event_id: str) -> dict:
    """The chain behind one event, with breaks marked and the two flags."""
    head = reads.event(conn, case_id, event_id)
    if head is None:
        raise Refusal("EVENT_NOT_IN_CASE", "route: lineage")
    walked = list(conn.execute(WALK_BACK, (event_id, case_id, MAX_DEPTH)))
    revoked = reads.revocations(conn, case_id)
    entries, breaks, seen = [], [], set()
    blocked: set[str] = set()
    for row in walked:
        eid = row["event_id"]
        if row["child"] in blocked:
            blocked.add(eid)
            continue
        e = reads.event(conn, case_id, eid)
        if e is None or not _projection_present(conn, e):
            breaks.append({"event_id": eid, "text": BROKEN.format(eid), "below": row["child"]})
            blocked.add(eid)
            continue
        seen.add(eid)
        entries.append(_entry(conn, e, row["depth"], revoked))
    flags, auth_entries = _authorization(conn, case_id, entries, seen)
    flags = _revocation_flags(entries, revoked) + flags
    entries.extend(auth_entries)
    raw_text, raw_vouch = _raw(conn, case_id, head)
    return {
        "event_id": event_id,
        "dir": "back",
        "chain": entries,
        "audit": audit(conn, case_id, entries),
        "breaks": breaks,
        "flags": flags,
        "envelope": _envelope(conn, case_id, event_id),
        "raw": raw_text,
        "raw_vouch": raw_vouch,
    }


def _step_of(x: dict) -> tuple[str, str] | None:
    """(step, heading) for one chain entry, or None for a type the audit trail does not name."""
    t, sub = x["type"], x["subtype"]
    if t == "AUTHORIZE_EVENT":
        return "authorized", AUTHORIZE_LABELS.get(sub, "Authorization act")
    if t == "COLLECT_EVENT":
        return "gate", "Gate"
    if (t, sub) == ("PROBE_EVENT", "RUN_START"):
        return "collected", "Collected"
    if (t, sub) == ("PROBE_EVENT", "ITEM"):
        hit = "outcome hit" in (x.get("summary") or [])
        return "fetched", "Fetched from" if hit else "Probed"
    if t == "EXTRACT_EVENT":
        return "processed", "Processed by"
    if t == "ADJUDICATE_EVENT":
        return "reviewed", REVIEW_LABELS.get(sub, "Reviewed")
    if t == "LINK_EVENT":
        return "proposed", "Proposed"
    if t == "IDENTITY_EVENT":
        return "asserted", "Asserted"
    if t == "ASSESS_EVENT":
        return "assessed", "Assessed"
    return None


def _audit_key(row: dict) -> tuple:
    """Oldest first, and the order a chain is built where two times are equal. The sort is stable, so two
    reviews at one time keep the log's order, in which the later one is the claim's review state."""
    return (_instant(row["ts"]), AUDIT_STEPS.index(row["step"]))


def _instant(ts) -> tuple:
    """A time as (seconds since the epoch, text), so 10:12:00.500Z sorts after 10:12:00Z; a time that does
    not parse sorts first, by its text."""
    try:
        return (datetime.fromisoformat(str(ts).replace("Z", "+00:00")).timestamp(), str(ts))
    except ValueError:
        return (float("-inf"), str(ts))


def audit(conn, case_id: str, entries: list[dict]) -> list[dict]:
    """The chain's entries as one audit row per step, oldest first, with the reviews of its claims.

    Each row is {step, label, event_id, ts, lines}, and its lines are the time and the producer that
    recorded the event, then the entry's closed-field summary. A review is a VERIFY or DISPUTE whose
    target is a claim in the chain and which is not in the chain itself; its lines name the act, the
    analyst and the claim, never the analyst's prose.
    """
    rows = []
    for x in entries:
        step = _step_of(x)
        if step is None:
            continue
        lines = [f"recorded {x['ts']} by {x['producer']}"] + list(x["summary"])
        if x["payload"] != "held":
            lines.append(f"payload {x['payload']}")
        rows.append({"step": step[0], "label": step[1], "event_id": x["event_id"], "ts": x["ts"], "lines": lines})
    rows.extend(_reviews(conn, case_id, entries))
    rows.sort(key=_audit_key)
    return rows


def _reviews(conn, case_id: str, entries: list[dict]) -> list[dict]:
    """The VERIFY and DISPUTE acts on the chain's claims that the walk did not reach, as audit rows."""
    claims = {x["event_id"] for x in entries if x["type"] == "EXTRACT_EVENT"}
    if not claims:
        return []
    walked = {x["event_id"] for x in entries}
    acts = [r for r in reads.events(conn, case_id, "ADJUDICATE_EVENT", ("VERIFY", "DISPUTE"))
            if (r["payload"] or {}).get("target_ref") in claims]
    latest = {r["payload"]["target_ref"]: r["event_id"] for r in acts}
    out = []
    for r in acts:
        if r["event_id"] in walked:
            continue
        target = r["payload"]["target_ref"]
        who = r["payload"].get("analyst") or r["producer"]
        now = latest[target] == r["event_id"]
        out.append({
            "step": "reviewed",
            "label": REVIEW_LABELS[r["subtype"]],
            "event_id": r["event_id"],
            "ts": r["ts"],
            "lines": [
                f"recorded {r['ts']} by {r['producer']}",
                f"{REVIEW_LABELS[r['subtype']].lower()} claim {target[:8]} by {who}",
                "this is the claim's review state now" if now else "a later review of the same claim replaces this one",
            ],
        })
    return out


def _revocation_flags(entries: list[dict], revoked: dict) -> list[str]:
    """One flag per withdrawn cluster or proposal the chain passes through."""
    out = []
    for x in entries:
        if revoked.get(x["event_id"]) is None:
            continue
        if x["type"] == "LINK_EVENT":
            out.append(f"cites withdrawn proposal {x['event_id'][:8]}: that inference no longer stands")
        elif (x["type"], x["subtype"]) == ("IDENTITY_EVENT", "CLUSTER"):
            out.append(f"cites revoked cluster {x['event_id'][:8]}: that assertion no longer stands")
    return out


def _entry(conn, e: dict, depth: int, revoked: dict | None = None) -> dict:
    payload_state = "held" if e["payload"] is not None else "swept: the payload is gone, the skeleton remains"
    return {
        "event_id": e["event_id"],
        "type": e["type"],
        "subtype": e["subtype"],
        "ts": e["ts"],
        "producer": e["producer"],
        "depth": depth,
        "payload": payload_state,
        "summary": _summary(conn, e, revoked) if e["payload"] is not None else [],
    }


def _authorization(conn, case_id: str, entries: list[dict], seen: set) -> tuple[list[str], list[dict]]:
    """The authorization acts above the chain's decisions, and the two render-only flags."""
    auths = reads.authorizations(conn, case_id)
    flags: list[str] = []
    extra: list[dict] = []
    depth = max((x["depth"] for x in entries), default=0) + 1
    refs = []
    for x in entries:
        if x["type"] in ("COLLECT_EVENT", "AUTHORIZE_EVENT"):
            p = (reads.event(conn, case_id, x["event_id"]) or {}).get("payload") or {}
            ref = p.get("authorization_ref")
            if ref and ref not in refs:
                refs.append(ref)
    for ref in refs:
        acts = auths.get(ref, [])
        for act in acts:
            if act["event_id"] not in seen:
                seen.add(act["event_id"])
                extra.append(_entry(conn, act, depth))
        state = reads.authorization_state(acts)
        revoked = state["revoked"]
        for x in entries:
            if x["type"] != "COLLECT_EVENT" or revoked is None:
                continue
            if x["ts"] > revoked["ts"]:
                flags.append(
                    f"decision recorded after its authorization was revoked "
                    f"({x['subtype']} {x['ts'][11:16]} after REVOKE {revoked['ts'][11:16]})"
                )
        if state["expired"]:
            flags.append(f"authorization expired {state['expires_on']}")
    return flags, extra


def _envelope(conn, case_id: str, event_id: str) -> dict | None:
    row = conn.execute("SELECT * FROM event_skeleton WHERE event_id = ? AND case_id = ?", (event_id, case_id)).fetchone()
    e = reads.event(conn, case_id, event_id)
    if row is None or e is None or e["payload"] is None:
        return None
    return envelope.compose(row, e["payload"])


def _raw(conn, case_id: str, head: dict) -> tuple[str, bool]:
    """(the RAW tier's text, whether the system does not vouch for it)."""
    if head["type"] == "EXTRACT_EVENT":
        claim = conn.execute("SELECT item_id FROM claim WHERE claim_id = ?", (head["event_id"],)).fetchone()
        item = conn.execute("SELECT blob_state FROM item WHERE item_id = ?", (claim["item_id"],)).fetchone() if claim else None
    elif (head["type"], head["subtype"]) == ("PROBE_EVENT", "ITEM"):
        item = conn.execute("SELECT blob_state FROM item WHERE event_id = ?", (head["event_id"],)).fetchone()
    else:
        return "no raw bytes belong to this event", False
    if item is not None and item["blob_state"] == "held":
        return "raw bytes held in the case store; this server has no Encryptor and does not decrypt them", False
    reg = conn.execute("SELECT synthetic FROM case_registry WHERE case_id = ?", (case_id,)).fetchone()
    return "not held: " + blobs.not_held_line(reg["synthetic"] if reg else 0), True


def forward(conn, case_id: str, event_id: str) -> dict:
    """What depends on an event: the clusters, sentences, runs and claims built on it."""
    if reads.event(conn, case_id, event_id) is None:
        raise Refusal("EVENT_NOT_IN_CASE", "route: lineage")
    entries = []
    revoked = reads.revocations(conn, case_id)
    for row in conn.execute(WALK_FORWARD, (event_id, case_id, MAX_DEPTH)):
        if row["event_id"] == event_id:
            continue
        e = reads.event(conn, case_id, row["event_id"])
        entries.append(_entry(conn, e, row["depth"], revoked))
    return {"event_id": event_id, "dir": "forward", "chain": entries, "breaks": [], "flags": []}
