// The labels the showcase prints beside what the server says. A label names a
// kind of thing; it never states a fact about the case. Every fact on screen is
// the server's own text, quoted, or a count of what the server returned.

const SELECTOR = {
  platform_uid: ["id", "Platform user id"],
  handle: ["hd", "Handle"],
  username_string: ["un", "Username string"],
  channel: ["ch", "Channel"],
  person_name: ["nm", "Name"],
  person_name_alias: ["al", "Alias"],
  email: ["em", "Email"],
  email_hint_recovery_masked: ["eh", "Email, recovery hint (masked)"],
  email_generated_permutation: ["eg", "Email, generated permutation"],
  phone: ["ph", "Phone"],
  phone_hint_recovery_masked: ["pm", "Phone, recovery hint (masked)"],
  postal_address: ["ad", "Postal address"],
  org_name: ["or", "Organization name"],
  org_registration_number: ["rn", "Organization registration number"],
  public_record_id: ["pr", "Public record id"],
  domain: ["dn", "Domain"],
  image_phash: ["ih", "Image hash"],
  geo_area: ["ga", "Area"],
  time_window: ["tw", "Time window"],
};

export function selectorLabel(type) {
  return (SELECTOR[type] || [null, String(type || "selector").replaceAll("_", " ")])[1];
}

export function selectorChip(type) {
  return (SELECTOR[type] || [String(type || "??").slice(0, 2)])[0];
}

export const SECTOR_LABEL = {
  accounts: "Accounts",
  names_aliases: "Names and aliases",
  emails: "Emails",
  phones: "Phones",
  addresses: "Addresses",
  organizations: "Organizations",
  people: "People",
  other_osint: "Other OSINT",
};

export const SEAMS = {
  h: "same handle, exact",
  e: "shared email or hint consistent",
  n: "shared phone or hint consistent",
  b: "bio cross-reference or self-link",
  i: "image or pHash match",
  t: "temporal co-location or pattern",
  g: "analyst gestalt, no note required at merge",
  k: "external knowledge, note required",
};

/** The seams in a few words, for a label on a line; the side panel prints SEAMS in full. */
export const SEAM_SHORT = {
  h: "same handle", e: "shared email", n: "shared phone", b: "bio cross-reference",
  i: "image match", t: "temporal pattern", g: "analyst gestalt", k: "external knowledge",
};

/** The registry's place-bearing kinds: a geo_area selector (a box or polygon) and a Place entity. */
export const PLACE_SELECTORS = ["geo_area"];
export const PLACE_ENTITIES = ["Place"];

/** How many place-bearing claims and nodes the case holds, counted from what the server returned. */
export function placeCount(model) {
  if (!model) return null;
  const claims = [...model.claims.values()].filter((c) => PLACE_SELECTORS.includes(c.selector_type)).length;
  const nodes = [...model.nodes.values()].filter((n) => PLACE_ENTITIES.includes(n.entity_type)).length;
  return claims + nodes;
}

/** The consequence of a band, from spec/layer-model.yaml's note on the only ordinal in the model. */
export const BAND = {
  possible: "possible: citing it needs a caveat",
  likely: "likely",
  almost_certain: "almost certain: needs two evidence classes",
};

const EVENT = {
  "AUTHORIZE_EVENT.GRANT": "Authorization granted",
  "AUTHORIZE_EVENT.EXTEND": "Authorization extended",
  "AUTHORIZE_EVENT.REVOKE": "Authorization revoked",
  "COLLECT_EVENT.PERMITTED": "The subject gate permitted a run",
  "COLLECT_EVENT.REQUIRES_EXTENSION": "The subject gate held a pivot",
  "COLLECT_EVENT.REFUSED": "The subject gate refused",
  "PROBE_EVENT.RUN_START": "Run started",
  "PROBE_EVENT.ITEM": "Item returned",
  "PROBE_EVENT.RUN_END": "Run ended",
  "EXTRACT_EVENT.CLAIM": "Claim extracted",
  "LINK_EVENT.SAME_ENTITY": "Proposed: same entity",
  "LINK_EVENT.ASSOCIATED_WITH": "Proposed: associated with",
  "LINK_EVENT.CO_LOCATED": "Proposed: co-located",
  "LINK_EVENT.CONTROLS": "Proposed: controls",
  "IDENTITY_EVENT.CLUSTER": "Identity cluster asserted",
  "IDENTITY_EVENT.EXCLUDE": "Candidate excluded",
  "ADJUDICATE_EVENT.VERIFY": "Verified",
  "ADJUDICATE_EVENT.DISPUTE": "Disputed",
  "ADJUDICATE_EVENT.PROMOTE": "Promoted to an entity",
  "ADJUDICATE_EVENT.IGNORE": "Ignored",
  "ADJUDICATE_EVENT.REVOKE": "Revoked",
  "ADJUDICATE_EVENT.ACKNOWLEDGE": "Acknowledged",
  "ADJUDICATE_EVENT.OVERRIDE": "Override recorded",
  "ADJUDICATE_EVENT.NOTE": "Note",
  "ADJUDICATE_EVENT.QUESTION": "Open question",
  "ASSESS_EVENT.SENTENCE": "Assessment sentence",
  "SYSTEM_EVENT.COVERAGE_INTERVAL": "Coverage interval closed",
  "SYSTEM_EVENT.SWEEP_HEARTBEAT": "Retention sweep heartbeat",
  "SYSTEM_EVENT.SHRED_FAILED": "Shred failed",
  "SYSTEM_EVENT.SHRED_RECEIPT": "Shred receipt",
  "SYSTEM_EVENT.CONNECTOR_HEALTH": "Connector health",
  "SYSTEM_EVENT.CREDENTIAL_STATE": "Credential state",
  "SYSTEM_EVENT.SCHEMA_VIOLATION": "Schema violation",
  "SYSTEM_EVENT.RECONCILE_HEARTBEAT": "Reconcile heartbeat",
  "SYSTEM_EVENT.RETENTION_EXTENSION": "Retention extended",
  "SYSTEM_EVENT.RETENTION_FREEZE": "Retention frozen",
  "SYSTEM_EVENT.RETENTION_RENEWAL": "Freeze renewed",
};

export function eventLabel(type, subtype) {
  return EVENT[`${type}.${subtype}`] || `${String(type).replace("_EVENT", "").toLowerCase()} ${String(subtype).toLowerCase().replaceAll("_", " ")}`;
}

/** The epistemic layer an event belongs to, which sets its border geometry and nothing else. */
export function layerOf(type) {
  if (type === "LINK_EVENT") return "inf";
  if (type === "IDENTITY_EVENT") return "fus";
  if (type === "ASSESS_EVENT") return "state";
  if (type === "AUTHORIZE_EVENT") return "auth";
  if (type === "ADJUDICATE_EVENT") return "act";
  return "obs";
}

/** A source's role, read from its producer name. */
export function roleOf(producer) {
  const p = String(producer || "");
  if (p.startsWith("connector-")) return { key: "connector", word: liveLook ? "Source · records" : "Connector · collection", mono: liveLook && labels[p] ? labels[p].slice(0, 2) : "co", order: 0 };
  if (p.startsWith("matcher-")) return { key: "matcher", word: "Matcher · proposes, never asserts", mono: "ma", order: 1 };
  if (p.startsWith("analyst-")) return { key: "analyst", word: "Analyst · the only one who asserts", mono: "an", order: 2 };
  if (p === "runner-subject-guard") return { key: "gate", word: "Subject gate · decides what may run", mono: "gt", order: 3 };
  if (p.startsWith("runner-")) return { key: "runner", word: `Runner · ${p.slice(7).replaceAll("-", " ")}`, mono: "rn", order: 4 };
  return { key: "other", word: "Producer", mono: p.slice(0, 2) || "??", order: 5 };
}

export const TAB_ORDER = ["overview", "timeline", "connections", "sources", "places", "tools", "assessment"];

/** Each tab, its design view and the key design 8.6 and amendment 9.10 give that view. */
export const TABS = {
  overview: { label: "Overview", view: "DOSSIER", key: "1", question: "Who is this, and what is it built on?" },
  sources: { label: "Sources", view: "STREAM", key: "2", question: "What came back, from whom, and what is it worth?" },
  timeline: { label: "Timeline", view: "CHRONOLOGY", key: "3", question: "What happened when, and when were we watching?" },
  places: { label: "Places", view: "MAP", key: "4", question: "Where, if anywhere?" },
  tools: { label: "Tools", view: "COLLECTION", key: "5", question: "What ran, what decided, and what is the system's own state?" },
  assessment: { label: "Assessment", view: "DRAFT", key: "6", question: "What do we say, and can we prove every sentence?" },
  connections: { label: "Connections", view: "WEB", key: "7", question: "Who and what is this connected to?" },
};

/** "2026-01-15T10:09:00Z" as "10:09Z". */
export function hm(ts) {
  const m = /T(\d\d:\d\d)/.exec(String(ts || ""));
  return m ? `${m[1]}Z` : String(ts || "");
}

/** "2026-01-15T10:09:00Z" as "2026-01-15 10:09Z". */
export function stamp(ts) {
  const m = /^(\d{4}-\d\d-\d\d)T(\d\d:\d\d)/.exec(String(ts || ""));
  return m ? `${m[1]} ${m[2]}Z` : String(ts || "");
}

export function day(ts) {
  const m = /^(\d{4}-\d\d-\d\d)/.exec(String(ts || ""));
  return m ? m[1] : "";
}

/** The conformance corpus's stand-in values, such as <synthetic-handle-1>: a test fixture never carries a real or realistic value. */
const PLACEHOLDER = /^~?<synthetic-[a-z0-9-]+>$/;

export function isPlaceholder(value) {
  return PLACEHOLDER.test(String(value || ""));
}

export const PLACEHOLDER_NOTE = "a placeholder the conformance corpus uses in place of a value: AGENTS.md section 4 keeps every value, synthetic ones included, out of the repository";

export function short(id) {
  return String(id || "").slice(0, 8);
}

export function plural(n, one, many) {
  return `${n} ${n === 1 ? one : (many || one + "s")}`;
}

import { hasCasePack, labels, liveLook } from "./api.js";

/** A producer as the page prints it: the case pack's display name for a source, else the producer's own id. */
export function who(producer) {
  if (liveLook && String(producer || "").startsWith("analyst-")) return "Analyst";
  return (labels && labels[producer]) || producer;
}

/** The top bar's label for a display overlay, or null when there is none or the live look hides it.
 *  `switches` says whether pressing the label changes what is shown. A case pack is a whole case answered
 *  in the page, so nothing stored stands behind it and its label is not a switch. */
export function fictionLabel(overlay, on) {
  if (!overlay || liveLook) return null;
  const head = overlay.label || "FICTIONAL PERSON";
  if (hasCasePack()) return { head, text: "invented for this showcase, answered from a display file · the store is not read", switches: false };
  return on
    ? { head, text: "invented for this showcase, display only · show stored values", switches: true }
    : { head: "STORED VALUES", text: "the test corpus's placeholders · show the fictional person", switches: true };
}

/** The help panel's statements of where the values on screen come from: a note, which the live look leaves
 *  out, and a closing line. With a case pack set, neither says the page reads the store. */
export function sourceWords(overlay, on) {
  const packed = hasCasePack();
  const note = liveLook ? null
    : packed ? ["The person on this page is invented. ", "The whole case was written for this showcase and is answered in the page from a display file that the server read at launch. The store is not read while it is shown, and nothing was collected about anyone."]
    : overlay && on ? ["The person on this page is invented. ", "The name, handles and emails were made up for this showcase and are drawn over the test corpus's placeholders as the page displays them. The store holds the placeholders, and nothing was collected about anyone. The FICTIONAL PERSON button in the top bar shows the stored values."]
    : ["Values written in angle brackets ", "are the test corpus's placeholders. The repository never holds a value, synthetic ones included, so the fixture stands in for each one, and the page shows exactly what the store holds."];
  const line = packed
    ? (liveLook
      ? "The page writes nothing, and nothing on it can start a run."
      : "This case is fiction answered from a display file: no person, account or platform was queried. The page writes nothing, and nothing on it can start a run.")
    : (liveLook
      ? "The page reads the store and writes nothing, and nothing on it can start a run."
      : "This is a synthetic case from the conformance corpus: no person, account or platform was queried. The page reads the store and writes nothing, and nothing on it can start a run.");
  return { note, line };
}
