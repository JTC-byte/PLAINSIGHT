#!/usr/bin/env python3
"""Cast integrity gate: the checkable half of SS-3, plus a structural lint.

`synthetic/GROUND_TRUTH.yaml` is the oracle every precision and recall figure in
this program is computed against, and nothing downstream can detect a defect in
it. There is nothing above it to compare it to. A truth file that says two
accounts are one persona when they are not produces a scorecard that is wrong
and internally consistent, and an analyst reading that scorecard has no way to
see it. That asymmetry is why this tool exists before the cast does.

`doctrine/SUBJECT_SELECTION.md` SS-3 splits isolation into two halves, and this
tool holds one of them. The checkable half: no two personas share a recovery
selector, and nothing in the file references an account outside the cast. The
account-creation half, whether a persona actually accrued a real follower on a
live platform, is an operator act with no technical control available. No output
of this tool covers it, and a clean run must not be read as covering it.

Every check guards a specific defect:

  C-01  The file does not parse, or its root is not a mapping. A truth file the
        scorer cannot read fails at scoring time, which is after collection.
  C-02  Fewer than two personas. One persona has no link graph, so nothing is
        measurable. Fewer than two platforms, or an account on a platform the
        `platforms` block does not declare: the cross-platform surfaces the cast
        exists to present cannot be attributed to a connector.
  C-03  Fewer than two email domains, an undeclared persona domain, or a
        confuser or negative persona sharing the linked persona's domain. A
        shared email root is designed surface S-1. Handing it to the confuser
        destroys the confuser, whose job is to look related while being
        distinct, and the resulting false positive is one the team created.
  C-04  No confuser pair, a confuser pair whose two accounts belong to the same
        persona, or a pair not marked `truly_distinct`. Without a case-level
        known negative, recall is measurable and precision is not, and gameplan
        section 4 item 7 refuses collection on exactly this condition.
  C-05  No injection carrier, a carrier holding no payload, or a payload family
        that is not declared in `payload_families`. SS-19 requires the pipeline
        to be exercised against collected content that tries to instruct it, and
        the cast is where that fixture lives.
  C-06  Two personas sharing a recovery phone or a recovery email. SS-3: a cast
        created from one phone number links the entire cast to the operator on
        the first correlation run. **This check compares tokens while the file is
        unsealed, so today it proves the design is distinct rather than that the
        values are.** It becomes a check on real values the moment the operator
        fills them, with no change to this tool.
  C-07  An edge, designed surface, or confuser pair naming an account id the
        file does not declare. That is the machine-readable form of "the cast
        interacts only with itself", and an edge to an undeclared account is
        either a typo or a persona reaching outside the cast.
  C-08  An account with no `created_on` key. Persona age conditions every figure
        the cast produces (SS-18, RT-13), and a scorecard quoting precision
        without age is quoting a number without its conditions. Null is legal
        while unsealed; absent is not, because absent is how the field gets
        forgotten at account creation.
  C-09  `truth.partition` not covering every account exactly once, or not
        covering every persona. A partition with a missing account silently
        removes that account from both the numerator and the denominator.
  C-10  An inconsistent seal. `sealed: false` with a recorded hash claims a seal
        that was never taken. `sealed: true` without `sealed_on`, `sealed_by` or
        a hash claims a seal nobody can verify. A recorded hash that does not
        match the file is either an edit after sealing or a different file.

Two modes beyond the default:

  --placeholder-scan  While the file is unsealed, refuse any value under a
        selector-shaped key that is not in <...> placeholder form. AGENTS.md
        section 4 forbids an agent writing a handle, address, number or display
        name into a tracked file, and a synthetic value is still a value. This
        mode is the mechanism behind that sentence, so the prohibition is not a
        habit. It does not apply once sealed, because sealing is the point at
        which the operator has legitimately filled the values.
  --self-test  Mutate the loaded model in memory and assert each defect is
        refused. A gate nobody has watched refuse has not been shown to work,
        and this file is checked by no corpus of failing fixtures yet.

Exit codes: 0 clean, 1 violations found, 2 the cast file could not be read.

One deliberate departure from --quiet. An unsealed cast prints its consequence
even under --quiet, because the state is not a failure and is not a pass, and
CLAUDE.md section 4 requires a state to render as its consequence rather than as
its token. A silently unsealed cast is how a scorecard gets produced against an
unsealed oracle.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import re
import sys
from pathlib import Path

try:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import gate_log
except Exception:  # telemetry must never be able to break a gate
    gate_log = None

try:
    import yaml
except Exception:  # reported as a refusal, never as a traceback
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
CAST = ROOT / "synthetic" / "GROUND_TRUTH.yaml"
REL = "synthetic/GROUND_TRUTH.yaml"

#: Persona roles, closed. `linked` is the persona whose accounts are truly one
#: person. `confuser` looks related and is not. `negative` shares no designed
#: surface with anything.
ROLES = ("linked", "confuser", "negative")

#: Keys whose values become selectors. AGENTS.md section 4 keeps these out of a
#: tracked file until the operator fills them. `email_domain` on a persona is
#: absent from this set on purpose: it carries a reference to an
#: `email_domains[].id`, and that id is scanned directly, so the value is
#: covered once rather than twice.
PLACEHOLDER_KEYS = (
    "handle",
    "platform_uid",
    "display_name",
    "profile_image",
    "phone",
    "phone_source",
    "email",
)

PLACEHOLDER_RE = re.compile(r"^<[^<>]+>$")

#: The one line the seal blanks before hashing. Anchored at line start so a
#: mention of the word in a comment cannot be mistaken for the field.
SEAL_LINE_RE = re.compile(r"^([ \t]*)sha256:.*$", re.M)

UNSEALED_CONSEQUENCE = (
    "UNSEALED: this cast cannot score anything and SS-14 item 6 refuses "
    "collection until it is sealed and stamped"
)


class Finding:
    __slots__ = ("code", "where", "detail", "moves")

    def __init__(self, code: str, where: str, detail: str, moves: str):
        self.code = code
        self.where = where
        self.detail = detail
        self.moves = moves

    def render(self) -> str:
        return (
            f"REFUSED {self.code}\n"
            f"  where: {self.where}\n"
            f"  what:  {self.detail}\n"
            f"  moves: {self.moves}"
        )


# ---------------------------------------------------------------------------
# Accessors. Every one of these tolerates a malformed file, because a defect in
# the cast file must produce a named refusal rather than a traceback with a line
# number in this tool.
# ---------------------------------------------------------------------------


def _seq(model: dict, key: str) -> list:
    v = model.get(key)
    return [x for x in v if isinstance(x, dict)] if isinstance(v, list) else []


def _personas(model: dict) -> list[dict]:
    return _seq(model, "personas")


def _accounts(model: dict) -> list[tuple[str, dict]]:
    """Every (persona_id, account) pair the file declares."""
    out: list[tuple[str, dict]] = []
    for p in _personas(model):
        pid = str(p.get("id", "?"))
        v = p.get("accounts")
        if isinstance(v, list):
            for a in v:
                if isinstance(a, dict):
                    out.append((pid, a))
    return out


def _account_ids(model: dict) -> list[str]:
    return [str(a.get("account_id")) for _, a in _accounts(model) if a.get("account_id")]


def _partition(model: dict) -> list[dict]:
    truth = model.get("truth")
    if not isinstance(truth, dict):
        return []
    v = truth.get("partition")
    return [x for x in v if isinstance(x, dict)] if isinstance(v, list) else []


def _seal(model: dict) -> dict:
    v = model.get("seal")
    return v if isinstance(v, dict) else {}


def is_sealed(model: dict) -> bool:
    return _seal(model).get("sealed") is True


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------


def check_structure(model: dict) -> list[Finding]:
    findings: list[Finding] = []
    personas = _personas(model)
    accounts = _accounts(model)
    account_ids = _account_ids(model)
    declared = set(account_ids)

    # C-02. Personas and platforms.
    if len(personas) < 2:
        findings.append(
            Finding(
                "CAST_TOO_FEW_PERSONAS",
                f"{REL} > personas",
                f"{len(personas)} persona(s) declared. One persona has no link "
                "graph, so there is nothing to be right or wrong about and no "
                "figure the cast can produce",
                "declare a second persona, or drop the claim that this file can "
                "score anything",
            )
        )

    for p in personas:
        role = p.get("role")
        if role not in ROLES:
            findings.append(
                Finding(
                    "CAST_ROLE_UNKNOWN",
                    f"{REL} > personas > {p.get('id', '?')}",
                    f"role {role!r} is outside the closed set {ROLES}, so no check "
                    "here knows whether this persona is the answer or the trap",
                    f"set role to one of {', '.join(ROLES)}",
                )
            )

    platforms = {str(x.get("id")) for x in _seq(model, "platforms") if x.get("id")}
    if len(platforms) < 2:
        findings.append(
            Finding(
                "CAST_TOO_FEW_PLATFORMS",
                f"{REL} > platforms",
                f"{len(platforms)} platform(s) declared. A single platform presents "
                "no cross-platform surface, and cross-platform correlation is the "
                "capability the cast measures",
                "declare a second platform, or state in synthetic/CAST.md that this "
                "cast measures within-platform matching only",
            )
        )
    for pid, a in accounts:
        plat = a.get("platform")
        if str(plat) not in platforms:
            findings.append(
                Finding(
                    "CAST_ACCOUNT_PLATFORM_UNDECLARED",
                    f"{REL} > {pid} > {a.get('account_id', '?')}",
                    f"platform {plat!r} is not declared in the platforms block, so "
                    "no connector, shape, or credential requirement is recorded for "
                    "the account",
                    "add the platform to the platforms block, or correct the "
                    "account's platform",
                )
            )

    # C-03. Email domains, and the confuser's separation from the linked root.
    domains = {str(x.get("id")) for x in _seq(model, "email_domains") if x.get("id")}
    if len(domains) < 2:
        findings.append(
            Finding(
                "CAST_TOO_FEW_EMAIL_DOMAINS",
                f"{REL} > email_domains",
                f"{len(domains)} domain(s) declared. A single domain gives every "
                "persona a shared email root, which is designed surface S-1 handed "
                "to the confuser for free",
                "declare a second domain and put the confuser on it",
            )
        )

    linked_domains = {
        str(p.get("email_domain"))
        for p in personas
        if p.get("role") == "linked" and p.get("email_domain")
    }
    if not linked_domains:
        findings.append(
            Finding(
                "CAST_NO_LINKED_PERSONA",
                f"{REL} > personas",
                "no persona carries role 'linked', so the file declares no true "
                "cluster and every confuser pair is a negative against nothing",
                "give the persona whose accounts are one person role 'linked'",
            )
        )

    for p in personas:
        dom = p.get("email_domain")
        if dom is None or str(dom) not in domains:
            findings.append(
                Finding(
                    "CAST_PERSONA_DOMAIN_UNDECLARED",
                    f"{REL} > personas > {p.get('id', '?')}",
                    f"email_domain {dom!r} is not declared in the email_domains "
                    "block, so the domain's role in the design is unrecorded",
                    "add the domain to email_domains, or correct the persona",
                )
            )
        elif p.get("role") in ("confuser", "negative") and str(dom) in linked_domains:
            findings.append(
                Finding(
                    "CAST_CONFUSER_SHARES_LINKED_DOMAIN",
                    f"{REL} > personas > {p.get('id', '?')}",
                    f"a {p.get('role')} persona sits on the linked persona's domain "
                    f"{dom!r}. A shared email root is a designed true surface, so "
                    "this persona now shares a true surface with the answer and any "
                    "match on it is a correlation the team created",
                    "move this persona to a domain whose role is not 'linked', or "
                    "change its role to linked and restate the partition",
                )
            )

    # C-09. The partition, first, because later checks read it.
    part_accounts: list[str] = []
    part_personas: list[str] = []
    for row in _partition(model):
        part_personas.append(str(row.get("persona")))
        v = row.get("accounts")
        if isinstance(v, list):
            part_accounts.extend(str(x) for x in v)

    persona_ids = [str(p.get("id")) for p in personas if p.get("id")]
    for aid in sorted(declared - set(part_accounts)):
        findings.append(
            Finding(
                "CAST_PARTITION_INCOMPLETE",
                f"{REL} > truth.partition",
                f"account {aid} is declared and appears in no partition row, so it "
                "is in neither the numerator nor the denominator of any figure and "
                "its absence is invisible in the result",
                "add the account to the row of the persona that holds it",
            )
        )
    for aid in sorted({x for x in part_accounts if part_accounts.count(x) > 1}):
        findings.append(
            Finding(
                "CAST_PARTITION_DOUBLE_COUNTED",
                f"{REL} > truth.partition",
                f"account {aid} appears in more than one partition row. A partition "
                "assigns each account to exactly one persona, and two rows claiming "
                "the same account means the truth file contradicts itself",
                "remove the account from every row but one",
            )
        )
    for aid in sorted(set(part_accounts) - declared):
        findings.append(
            Finding(
                "CAST_REFERENCE_OUTSIDE_CAST",
                f"{REL} > truth.partition",
                f"the partition names account {aid}, which no persona declares",
                "declare the account under its persona, or correct the partition row",
            )
        )
    for pid in sorted(set(persona_ids) - set(part_personas)):
        findings.append(
            Finding(
                "CAST_PARTITION_PERSONA_MISSING",
                f"{REL} > truth.partition",
                f"persona {pid} has no partition row, so the scorer has no statement "
                "of which accounts are that persona",
                "add a partition row for the persona, or remove the persona",
            )
        )
    for pid in sorted(set(part_personas) - set(persona_ids)):
        findings.append(
            Finding(
                "CAST_PARTITION_PERSONA_UNDECLARED",
                f"{REL} > truth.partition",
                f"the partition names persona {pid}, which the personas block does "
                "not declare",
                "declare the persona, or correct the partition row",
            )
        )

    owner: dict[str, str] = {}
    for row in _partition(model):
        v = row.get("accounts")
        if isinstance(v, list):
            for x in v:
                owner[str(x)] = str(row.get("persona"))

    # C-07. Every reference stays inside the cast.
    for surface in _seq(model, "designed_surfaces"):
        for aid in surface.get("links") or []:
            if str(aid) not in declared:
                findings.append(
                    Finding(
                        "CAST_REFERENCE_OUTSIDE_CAST",
                        f"{REL} > designed_surfaces > {surface.get('id', '?')}",
                        f"links account {aid}, which no persona declares. SS-3: the "
                        "cast interacts only with itself, and a surface reaching an "
                        "account outside the cast is either a typo or a real link",
                        "correct the account id, or declare the account under its "
                        "persona if it belongs to the cast",
                    )
                )

    surface_ids = {str(s.get("id")) for s in _seq(model, "designed_surfaces") if s.get("id")}

    pairs = _seq(model, "confuser_pairs")
    for pair in pairs:
        for aid in pair.get("accounts") or []:
            if str(aid) not in declared:
                findings.append(
                    Finding(
                        "CAST_REFERENCE_OUTSIDE_CAST",
                        f"{REL} > confuser_pairs > {pair.get('id', '?')}",
                        f"names account {aid}, which no persona declares, so the "
                        "known negative is stated against nothing",
                        "correct the account id, or declare the account",
                    )
                )
        surf = pair.get("surface")
        if surf is not None and str(surf) not in surface_ids:
            findings.append(
                Finding(
                    "CAST_SURFACE_UNDECLARED",
                    f"{REL} > confuser_pairs > {pair.get('id', '?')}",
                    f"cites designed surface {surf!r}, which the designed_surfaces "
                    "block does not declare, so nothing records what a matcher would "
                    "fire on here",
                    "declare the surface, or correct the reference",
                )
            )

    for edge in _seq(model, "edges"):
        for end in ("from", "to"):
            aid = edge.get(end)
            if str(aid) not in declared:
                findings.append(
                    Finding(
                        "CAST_REFERENCE_OUTSIDE_CAST",
                        f"{REL} > edges > {edge.get('id', '?')}",
                        f"its {end} endpoint is account {aid}, which no persona "
                        "declares. SS-3: an edge leaving the cast makes the persona a "
                        "bystander collector rather than a measurement instrument",
                        "correct the endpoint, or declare the account under its "
                        "persona if it belongs to the cast",
                    )
                )
        surf = edge.get("designed_surface")
        if surf is not None and str(surf) not in surface_ids:
            findings.append(
                Finding(
                    "CAST_SURFACE_UNDECLARED",
                    f"{REL} > edges > {edge.get('id', '?')}",
                    f"cites designed surface {surf!r}, which the designed_surfaces "
                    "block does not declare",
                    "declare the surface, or set designed_surface to null if the edge "
                    "carries no designed correlation",
                )
            )

    # C-04. The case-level known negative.
    usable = 0
    for pair in pairs:
        aids = [str(x) for x in (pair.get("accounts") or [])]
        if len(aids) != 2 or any(a not in declared for a in aids):
            continue
        same_persona = owner.get(aids[0]) == owner.get(aids[1])
        if same_persona:
            findings.append(
                Finding(
                    "CAST_CONFUSER_PAIR_WITHIN_ONE_PERSONA",
                    f"{REL} > confuser_pairs > {pair.get('id', '?')}",
                    f"both accounts belong to persona {owner.get(aids[0])} per "
                    "truth.partition, so this pair is a true link labelled as a "
                    "negative and a correct matcher is scored as wrong",
                    "point the pair at accounts in different personas, or delete it",
                )
            )
            continue
        if pair.get("truly_distinct") is not True:
            findings.append(
                Finding(
                    "CAST_CONFUSER_PAIR_NOT_DISTINCT",
                    f"{REL} > confuser_pairs > {pair.get('id', '?')}",
                    "truly_distinct is not true, so the file does not assert that a "
                    "match on this pair is a false positive and the scorer cannot "
                    "count it as one",
                    "set truly_distinct: true, or delete the pair",
                )
            )
            continue
        usable += 1

    if usable < 1:
        findings.append(
            Finding(
                "CAST_NO_CONFUSER_PAIR",
                f"{REL} > confuser_pairs",
                "no confuser pair spans two personas and is marked truly_distinct. "
                "Without a case-level known negative, recall is measurable and "
                "precision is not, so the case cannot be scored. This is the "
                "connector-level known_negative canary lifted to case level",
                "declare a pair of accounts in different personas with "
                "truly_distinct: true, and name the surface a naive matcher fires on",
            )
        )

    # C-05. The injection fixture.
    families = {str(f.get("id")) for f in _seq(model, "payload_families") if f.get("id")}
    carriers = [p for p in personas if p.get("injection_carrier") is True]
    if not carriers:
        findings.append(
            Finding(
                "CAST_NO_INJECTION_CARRIER",
                f"{REL} > personas",
                "no persona carries injection_carrier: true. SS-19 requires the "
                "pipeline to be exercised against collected content that tries to "
                "instruct it, and the cast is the only place that fixture can live "
                "without collecting an attack from a real person",
                "set injection_carrier: true on one persona and give one of its "
                "accounts a declared payload family",
            )
        )
    for p in carriers:
        held = [
            a.get("bio_carries_payload_family")
            for a in (p.get("accounts") or [])
            if isinstance(a, dict) and a.get("bio_carries_payload_family")
        ]
        if not held:
            findings.append(
                Finding(
                    "CAST_CARRIER_HOLDS_NO_PAYLOAD",
                    f"{REL} > personas > {p.get('id', '?')}",
                    "declared as an injection carrier and no account of it carries a "
                    "payload family, so the fixture is named and absent",
                    "set bio_carries_payload_family on an account to a declared "
                    "payload family id, or set injection_carrier: false",
                )
            )
    for pid, a in accounts:
        fam = a.get("bio_carries_payload_family")
        if fam is not None and str(fam) not in families:
            findings.append(
                Finding(
                    "CAST_PAYLOAD_FAMILY_UNDECLARED",
                    f"{REL} > {pid} > {a.get('account_id', '?')}",
                    f"carries payload family {fam!r}, which the payload_families "
                    "block does not declare, so no boundary and no assertion is "
                    "recorded for what this fixture tests",
                    "declare the family with its boundary and assertion, or correct "
                    "the reference",
                )
            )

    # C-06. Recovery selectors, never shared between personas.
    for field, label in (("phone", "recovery phone"), ("email", "recovery email")):
        seen: dict[str, str] = {}
        for p in personas:
            rec = p.get("recovery")
            if not isinstance(rec, dict):
                continue
            val = rec.get(field)
            if val is None:
                continue
            token = str(val)
            pid = str(p.get("id", "?"))
            if token in seen:
                findings.append(
                    Finding(
                        "CAST_RECOVERY_SELECTOR_SHARED",
                        f"{REL} > personas > {seen[token]} and {pid}",
                        f"two personas declare the same {label}. SS-3: a cast created "
                        "from one phone number links the entire cast to the operator "
                        "on the first correlation run, which destroys the cast as a "
                        "measurement instrument and creates a real subject nobody "
                        "authorized",
                        "give each persona its own recovery selector, with its "
                        "provenance recorded in phone_source per CR-2",
                    )
                )
            else:
                seen[token] = pid

    # C-08. Age is a condition on every figure, so the field is never absent.
    for pid, a in accounts:
        if "created_on" not in a:
            findings.append(
                Finding(
                    "CAST_ACCOUNT_MISSING_CREATED_ON",
                    f"{REL} > {pid} > {a.get('account_id', '?')}",
                    "has no created_on key. Persona age conditions every figure the "
                    "cast produces (SS-18, RT-13), and a thin-target precision quoted "
                    "without its age reads as a fat-target result",
                    "add created_on: null now, and fill it at account creation",
                )
            )

    findings.extend(check_seal_fields(model))
    return findings


def check_seal_fields(model: dict) -> list[Finding]:
    """C-10, the half that reads only the model."""
    findings: list[Finding] = []
    seal = _seal(model)
    if not seal:
        return [
            Finding(
                "CAST_SEAL_INCONSISTENT",
                f"{REL} > seal",
                "no seal block. An unsealed cast must say so in a field the scorer "
                "reads, because the alternative is a scorecard produced against an "
                "oracle whose state nobody recorded",
                "add a seal block with sealed: false and sha256: null",
            )
        ]
    sealed = seal.get("sealed")
    digest = seal.get("sha256")
    if sealed is False and digest is not None:
        findings.append(
            Finding(
                "CAST_SEAL_INCONSISTENT",
                f"{REL} > seal",
                "sealed is false and a sha256 is recorded, which claims a seal that "
                "was never taken and would be quoted in a scorecard as if it were one",
                "clear sha256 to null, or set sealed: true and record sealed_on and "
                "sealed_by",
            )
        )
    if sealed is True:
        missing = [k for k in ("sealed_on", "sealed_by") if not seal.get(k)]
        if digest is None:
            missing.append("sha256")
        if missing:
            findings.append(
                Finding(
                    "CAST_SEAL_INCONSISTENT",
                    f"{REL} > seal",
                    f"sealed is true and {', '.join(missing)} is missing, so the file "
                    "claims a seal nobody can verify or attribute",
                    "record sealed_on, sealed_by and the sha256 of the canonical "
                    "form, or set sealed: false",
                )
            )
    if sealed not in (True, False):
        findings.append(
            Finding(
                "CAST_SEAL_INCONSISTENT",
                f"{REL} > seal",
                f"sealed is {sealed!r} rather than true or false. A tri-state seal is "
                "read as sealed by whichever reader is in a hurry",
                "set sealed to true or false",
            )
        )
    return findings


def canonical_digest(raw: str) -> tuple[str, int]:
    """sha256 of the canonical form: LF endings, the sha256 line blanked to null.

    Line-ending normalization is part of the rule rather than a convenience. Git
    checks this file out with CRLF on one of the two machines that will hash it,
    and a seal that depends on a checkout setting is not a seal.
    """
    text = raw.replace("\r\n", "\n").replace("\r", "\n")
    blanked, n = SEAL_LINE_RE.subn(lambda m: f"{m.group(1)}sha256: null", text, count=1)
    return hashlib.sha256(blanked.encode("utf-8")).hexdigest(), n


def check_seal_hash(model: dict, raw: str) -> list[Finding]:
    """C-10, the half that needs the file bytes."""
    seal = _seal(model)
    if seal.get("sealed") is not True:
        return []
    recorded = seal.get("sha256")
    if recorded is None:
        return []  # already refused by check_seal_fields
    computed, n = canonical_digest(raw)
    if n != 1:
        return [
            Finding(
                "CAST_SEAL_LINE_NOT_FOUND",
                f"{REL} > seal",
                f"the canonical form blanks the sha256 line and {n} such lines were "
                "found, so the digest is not computed over the form the rule names",
                "restore a single 'sha256:' line inside the seal block",
            )
        ]
    if str(recorded).strip().lower() != computed:
        return [
            Finding(
                "CAST_SEAL_HASH_MISMATCH",
                f"{REL} > seal.sha256",
                f"recorded {str(recorded)[:16]}..., computed {computed[:16]}.... The "
                "file has changed since it was sealed, or this is not the file that "
                "was sealed. A sealed truth file changes only by a new sealed version "
                "carrying a new hash",
                "re-seal as a new version and record the new hash in "
                "synthetic/CAST.md and in every scorecard that cites it, or restore "
                "the sealed content",
            )
        ]
    return []


def check_placeholders(model: dict) -> list[Finding]:
    """The mechanism behind AGENTS.md section 4, for this file.

    Applies while unsealed only. Sealing is the point at which the operator has
    legitimately filled the values, and a scan that refused a sealed file would
    make the seal unreachable.
    """
    if is_sealed(model):
        return []
    findings: list[Finding] = []

    def offend(where: str, key: str, value) -> None:
        findings.append(
            Finding(
                "CAST_VALUE_NOT_PLACEHOLDER",
                where,
                f"{key} holds a value that is not in <...> placeholder form while the "
                "file is unsealed. AGENTS.md section 4: no agent writes a selector "
                "value, handle, email, phone number or subject name into a tracked "
                "file, and a synthetic value is still a value",
                "replace the value with a placeholder such as "
                f"<{key}:PERSONA>, or seal the file if the operator has filled it",
            )
        )

    def walk(node, where: str) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                if k in PLACEHOLDER_KEYS and v is not None:
                    if not (isinstance(v, str) and PLACEHOLDER_RE.match(v)):
                        offend(where, str(k), v)
                walk(v, f"{where} > {k}")
        elif isinstance(node, list):
            for i, v in enumerate(node):
                label = v.get("id") or v.get("account_id") if isinstance(v, dict) else None
                walk(v, f"{where}[{label or i}]")

    walk(model, REL)

    for d in _seq(model, "email_domains"):
        did = d.get("id")
        if not (isinstance(did, str) and PLACEHOLDER_RE.match(did)):
            offend(f"{REL} > email_domains", "id", did)

    return findings


# ---------------------------------------------------------------------------
# Self-test. Each case is a defect this tool was written for, applied to the
# real model in memory, with the file on disk untouched.
# ---------------------------------------------------------------------------


def _mut_drop_confusers(m: dict) -> None:
    m["confuser_pairs"] = []


def _mut_share_phone(m: dict) -> None:
    ps = _personas(m)
    ps[1]["recovery"]["phone"] = ps[0]["recovery"]["phone"]


def _mut_edge_outside(m: dict) -> None:
    m.setdefault("edges", []).append(
        {
            "id": "E-SELFTEST",
            "from": _account_ids(m)[0],
            "to": "NOT-A-CAST-ACCOUNT",
            "kind": "aging_interaction",
            "designed_surface": None,
        }
    )


def _mut_seal_without_hash(m: dict) -> None:
    m["seal"]["sealed"] = True


def _mut_real_handle(m: dict) -> None:
    _personas(m)[0]["accounts"][0]["handle"] = "a_filled_in_value"


def _mut_confuser_takes_linked_domain(m: dict) -> None:
    linked = next(p for p in _personas(m) if p.get("role") == "linked")
    confuser = next(p for p in _personas(m) if p.get("role") == "confuser")
    confuser["email_domain"] = linked["email_domain"]


SELF_TESTS = (
    ("every confuser pair removed", _mut_drop_confusers, "CAST_NO_CONFUSER_PAIR", "structure"),
    ("two personas share a phone", _mut_share_phone, "CAST_RECOVERY_SELECTOR_SHARED", "structure"),
    ("an edge leaves the cast", _mut_edge_outside, "CAST_REFERENCE_OUTSIDE_CAST", "structure"),
    ("sealed true, hash null", _mut_seal_without_hash, "CAST_SEAL_INCONSISTENT", "structure"),
    ("a filled handle", _mut_real_handle, "CAST_VALUE_NOT_PLACEHOLDER", "placeholder"),
    (
        "confuser on the linked domain",
        _mut_confuser_takes_linked_domain,
        "CAST_CONFUSER_SHARES_LINKED_DOMAIN",
        "structure",
    ),
)


def self_test(model: dict, quiet: bool = False) -> int:
    missed: list[str] = []
    for label, mutate, expected, which in SELF_TESTS:
        m = copy.deepcopy(model)
        try:
            mutate(m)
        except Exception as exc:
            missed.append(f"{label}: the mutation itself failed ({exc!r})")
            continue
        found = check_structure(m) if which == "structure" else check_placeholders(m)
        codes = {f.code for f in found}
        if expected in codes:
            if not quiet:
                print(f"  refused as designed  {expected:38} {label}")
        else:
            missed.append(f"{label}: expected {expected}, got {sorted(codes) or 'nothing'}")

    if missed:
        print(
            "REFUSED CAST_SELF_TEST_FAILED\n"
            f"  where: tools/validate_cast.py > SELF_TESTS\n"
            "  what:  a defect this gate exists to refuse was not refused, so a "
            "clean run against the real file proves nothing\n"
            "  moves: fix the check, or fix the mutation if it no longer produces "
            "the defect it names",
            file=sys.stderr,
        )
        for m in missed:
            print(f"    {m}", file=sys.stderr)
        return 1

    if not quiet:
        print(f"validate_cast --self-test ok: {len(SELF_TESTS)} defects refused as designed")
    return 0


def _telemetry(outcome: str, findings: list[Finding] | None = None) -> None:
    if gate_log is None:
        return
    try:
        if findings:
            for f in findings:
                gate_log.record("cast", "refuse", code=f.code, where=f.where)
        else:
            gate_log.record("cast", outcome)
    except Exception:
        pass


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Cast integrity gate.")
    ap.add_argument(
        "--placeholder-scan",
        action="store_true",
        help="While unsealed, refuse any selector-shaped value that is not a "
        "<...> placeholder. The mechanism behind AGENTS.md section 4 for this file.",
    )
    ap.add_argument(
        "--self-test",
        action="store_true",
        help="Mutate the loaded model in memory and assert each defect is refused.",
    )
    ap.add_argument("--quiet", action="store_true", help="Print only on failure.")
    args = ap.parse_args(argv)

    if yaml is None:
        print(
            "REFUSED CAST_YAML_READER_MISSING\n"
            "  where: tools/validate_cast.py\n"
            "  what:  PyYAML is not importable, so the truth file cannot be read and "
            "this gate would pass vacuously\n"
            "  moves: pip install pyyaml, or add the install step to the CI workflow "
            "that runs this gate",
            file=sys.stderr,
        )
        _telemetry("error")
        return 2

    try:
        raw = CAST.read_text(encoding="utf-8")
    except OSError as exc:
        print(
            "REFUSED CAST_FILE_UNREADABLE\n"
            f"  where: {REL}\n"
            f"  what:  the truth file could not be read ({exc.strerror}). Every "
            "precision and recall figure in this program is computed against it\n"
            "  moves: create the file, or correct the path in tools/validate_cast.py",
            file=sys.stderr,
        )
        _telemetry("error")
        return 2

    try:
        model = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        first = str(exc).splitlines()[0] if str(exc) else exc.__class__.__name__
        print(
            "REFUSED CAST_FILE_UNPARSEABLE\n"
            f"  where: {REL}\n"
            f"  what:  PyYAML could not parse the file ({first}). A truth file the "
            "scorer cannot read fails at scoring time, which is after collection\n"
            "  moves: fix the YAML at the reported location; the file uses block "
            "mappings, block sequences, flow sequences and plain scalars only",
            file=sys.stderr,
        )
        _telemetry("error")
        return 2

    if not isinstance(model, dict):
        print(
            "REFUSED CAST_ROOT_NOT_A_MAPPING\n"
            f"  where: {REL}\n"
            f"  what:  the document parsed to {type(model).__name__} rather than a "
            "mapping, so no block this gate reads exists\n"
            "  moves: restore the top-level keys seal, platforms, email_domains, "
            "payload_families, personas, truth, designed_surfaces, confuser_pairs, edges",
            file=sys.stderr,
        )
        _telemetry("error")
        return 2

    if args.self_test:
        rc = self_test(model, quiet=args.quiet)
        _telemetry("pass" if rc == 0 else "refuse")
        return rc

    findings = check_structure(model)
    findings += check_seal_hash(model, raw)
    if args.placeholder_scan:
        findings += check_placeholders(model)

    _telemetry("pass", findings)

    if findings:
        for f in findings:
            print(f.render(), file=sys.stderr)
            print(file=sys.stderr)
        print(
            f"validate_cast: {len(findings)} violation(s). rule: "
            "doctrine/SUBJECT_SELECTION.md SS-3 and SS-19, "
            "docs/THE-GAMEPLAN.md section 4 item 7.",
            file=sys.stderr,
        )
        return 1

    if not is_sealed(model):
        # Printed even under --quiet. The state is neither a pass nor a failure,
        # and CLAUDE.md section 4 renders a state as its consequence.
        print(UNSEALED_CONSEQUENCE)
    if not args.quiet:
        n_acc = len(_account_ids(model))
        n_pers = len(_personas(model))
        n_pairs = len(_seq(model, "confuser_pairs"))
        n_surf = len(_seq(model, "designed_surfaces"))
        print(
            f"validate_cast ok: {n_pers} personas, {n_acc} accounts, "
            f"{n_surf} designed surfaces, {n_pairs} confuser pairs, partition covers "
            "every account once"
        )
        if args.placeholder_scan:
            print("  placeholder scan: every selector-shaped value is still a placeholder")
        print(
            "  not covered by this gate: whether a persona accrued a real follower "
            "on a live platform (SS-3, operator act); disjointness from the "
            "credential pool (SS-20, CR-1), which is "
            "tools/validate_authorization.py at Step 8 because the pool lives only "
            "in ISOLATED per EG-4"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
