#!/usr/bin/env python3
"""Retention gate: the compiled policy, the shred round trip, the repository scan,
and the pre-shred finding check.

This file replaces the Wave 0 stub tracked as D-001. The stub was wired into
`.githooks/pre-commit` so that the mechanism existed and was called, and it
returned 0 while checking nothing. That is the gap this tool closes, and the
four argv forms the stub accepted still work: `--repo-scan --staged` from the
hook and from `make preflight`, and `--repo-scan` bare from the kernel gate.

`doctrine/RETENTION.md` names this tool three times and each naming is a mode
below. RT-2 names `--policy`, RT-13 names `--finding <file> --case <id>`, and
RT-15 names `--repo-scan` wired into the pre-commit hook.
`conformance/retention/shred-roundtrip.yaml` names `--shred-roundtrip` as its
own self-lint.

Every check here is named by the defect it guards:

  R-01  A policy file that assigns a subject-carrying field to a surviving
        stratum is the RT-2 defect, and RT-2 says this tool refuses it rather
        than a reviewer noticing it. Enforced by
        RETENTION_SUBJECT_VALUE_IN_SURVIVING_STRATUM.
  R-02  A strata table keyed on the integer loses one of the two stratum-1 rows.
        RT-1 states the shape as seven rows across five numbered levels plus
        telemetry, and the two stratum-1 rows carry different contents and
        different subject-value descriptions, so the stricter one disappears in
        a six-row table. Enforced by RETENTION_POLICY_STRATA_ROW_COUNT.
  R-03  A strata set can be widened in the policy while the tools keep the
        narrow set, which passes both files' own checks. Reconciled against
        tools/validate_layer_model.py STRATA, SURVIVING_STRATA and
        CROSSING_STRATA by RETENTION_POLICY_STRATA_SET_DRIFT.
  R-04  A duration is one number in a file that reads as configuration, and
        changing it changes how long a person's data is held. Every stamped
        number is pinned below with its criterion, and a difference refuses
        under RETENTION_POLICY_TTL_DRIFT rather than being configured.
  R-05  RT-9's receipt of five checks can be five copies of one check. The
        model already pins SHRED_CHECKS for the wire; this pins it for the
        compiled policy and for the conformance fixture, under
        RETENTION_POLICY_VERIFICATION_INCOMPLETE and SHRED_ROUNDTRIP_CHECK_SET.
  R-06  A verification check that can pass for a reason other than the one
        claimed is not a check. Check 1 has to fail on the key, check 2 may not
        read a cached path, and check 3 has to tell an erroring query from a
        query that returned nothing. Enforced by
        RETENTION_POLICY_FALSE_PASS_UNGUARDED and
        SHRED_ROUNDTRIP_FALSE_PASS_UNGUARDED.
  R-07  A placeholder these artifacts carry can point at a question nobody
        recorded, and a recorded question can end up referenced by nothing.
        One direction finds half the drift, so both run:
        RETENTION_PLACEHOLDER_UNDECLARED and RETENTION_PLACEHOLDER_UNREFERENCED.
  R-08  A refusal that names no rule and offers no move is a state token rather
        than a refusal. Enforced by RETENTION_REFUSAL_PROSE_INCOMPLETE.
  R-09  An unratified criterion refuses rather than permits, and for a retention
        mechanism that means the sweep refuses to run rather than running with
        an unratified TTL. Enforced by RETENTION_POLICY_UNRATIFIED and
        SHRED_ROUNDTRIP_UNRATIFIED, both of which clear the moment the operator
        stamps the artifact in doctrine/DOCTRINE_STATUS.md.
  R-10  A live selector in a tracked file survives every mechanism in
        RETENTION.md, because git history is append-only, distributed to every
        clone, and outside the per-case crypto-shred. This is RT-15 and it is
        the mode the hook calls.
  R-11  A repository scan can claim coverage it does not have. The shapes this
        tool matches on are reconciled against the rank-3 forms in
        ontology/selectors.yaml in both directions, and the types it does not
        reach are printed rather than implied.

Two states are printed rather than refused, because CLAUDE.md section 4 renders
a state as its consequence rather than as its token. The first is the violation
code RT-15 requires and nothing declares. The second is the set of selector
types the scan does not reach while the cast is unsealed.

Exit codes: 0 clean, 1 violations found, 2 the governed input could not be read.
"""

from __future__ import annotations

import argparse
import copy
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - reported as an unreadable input
    yaml = None

try:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import gate_log
except Exception:  # telemetry must never be able to break a gate
    gate_log = None

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "policy" / "retention.yaml"
FIXTURE = ROOT / "conformance" / "retention" / "shred-roundtrip.yaml"
REGISTRY = ROOT / "ontology" / "selectors.yaml"
CODES = ROOT / "policy" / "violation-codes.yaml"
STATUS = ROOT / "doctrine" / "DOCTRINE_STATUS.md"
TRUTH = ROOT / "synthetic" / "GROUND_TRUTH.yaml"

POLICY_REL = "policy/retention.yaml"
FIXTURE_REL = "conformance/retention/shred-roundtrip.yaml"

#: Gate tokens. Two of these already exist in tools/validate_conformance.py and
#: are copied rather than coined; the other two are this tool's modes and move
#: with that file when a later step registers them. Reading VR-R4.
GATE_POLICY = "retention-policy"
GATE_SCAN = "retention-repo-scan"
GATE_ROUNDTRIP = "retention-shred-roundtrip"
GATE_FINDING = "retention-finding"

# ---------------------------------------------------------------------------
# Pinned doctrine values. Each carries the criterion that decided it. A policy
# file that differs is refused rather than followed, and widening one of these
# is a Class F change that moves the constant in the same commit as the stamp.
# ---------------------------------------------------------------------------

#: RT-1. Seven rows across five numbered levels, plus telemetry.
STRATA_ROW_COUNT = 7
#: RT-1. The two strata inside the shred boundary, which is also the set that
#: carries subject values.
INSIDE_SHRED_BOUNDARY = {0, 1}
#: RT-9. Five checks, each once. A receipt of [1, 1, 1, 1, 1] is one check
#: counted five times, which RT-9 says is not a check.
SHRED_CHECKS = [1, 2, 3, 4, 5]

#: The stamped durations, as (dotted path in the policy, days, criterion).
#: RT-5 is flat and names no subject class; RT-6 carries the one differentiated
#: number in the corpus.
DURATIONS = (
    ("case_ttl.default_days", 30, "RT-5"),
    ("case_ttl.extension_days", 30, "RT-5"),
    ("case_ttl.ceiling_days", 60, "RT-5, decision R2"),
    ("extension.length_days", 30, "RT-5"),
    ("incidental.ttl_days", 7, "RT-6"),
    ("blob_policy.media.expires_after_days", 90, "RT-8, decision R5"),
    ("freeze.default_expiry_days", 30, "RT-17"),
    ("gate_telemetry.ttl_days", 90, "RT-19"),
)

#: RT-9 check 1. A decrypt that reports not-found, permission-denied or
#: malformed-input has not proven the key was destroyed.
FALSE_PASS_ON_KEY = ("not_found", "permission_denied", "malformed_input")

#: RT-15. The code doctrine requires in policy/violation-codes.yaml. That file
#: is generated from spec/layer-model.yaml and cannot be hand-edited, and the
#: code is declared in neither. VR-U3 carries the question.
DOCTRINE_SCAN_CODE = "FIXTURE_CONTAINS_LIVE_SELECTOR"
#: What a scan finding carries while the code above is undeclared. Every sibling
#: validator emits a tool-local code, so this matches the house rather than
#: substituting silently for the code doctrine names. The notice below prints on
#: every run until DOCTRINE_SCAN_CODE is declared.
LOCAL_SCAN_CODE = "RETENTION_LIVE_SELECTOR_IN_TRACKED_FILE"

# ---------------------------------------------------------------------------
# Selector shapes for --repo-scan.
#
# VR-U1 carries the question of where these belong. They are module constants
# here because the two candidate homes are closed today: ontology/selectors.yaml
# is rank 3 and this build may not edit it, and policy/matcher-calibration.yaml
# does not exist. The precedent for a shape table inside a validator is
# tools/validate_ontology.py VALUE_SHAPES, which scans one file for the same
# defect.
#
# What keeps this table honest is the reconcile below it. Every segment name
# here has to equal the placeholder name in that selector's rank-3 `form`, in
# order, so the table is a compilation of the registry rather than a second
# opinion about what a selector looks like. A form edited in the registry
# refuses here until the table moves with it.
#
# What this table deliberately does not do is match a bare value. A scan for a
# bare address, domain or handle fires 4,957 times across the 50 tracked files
# in this repository, measured on 2026-09-11: 4,869 digit runs in the generated
# conformance corpora, 39 handle-shaped tokens including thirteen in the
# Makefile, 38 domains in LICENSE, NOTICE and README, and 11 addresses. A gate
# that always fires gets routed around rather than fixed, which doctrine/
# HYGIENE.md HY-2 names as a failure direction in its own right. The typed form
# is the object RT-15 can refuse today, and the bare-shape half is reported as
# coverage this gate does not have.
# ---------------------------------------------------------------------------

SEGMENT_SHAPES = {
    "platform": r"[a-z][a-z0-9_]{1,31}",
    "opaque_id": r"[A-Za-z0-9][A-Za-z0-9_.-]{1,63}",
    "channel_id": r"[A-Za-z0-9][A-Za-z0-9_.-]{1,63}",
    "string": r"[A-Za-z0-9][A-Za-z0-9_.]{1,63}",
    "addr": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}",
    "e164": r"\+[1-9]\d{7,14}",
    "fqdn": r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}",
    "hex64": r"[0-9a-fA-F]{16,64}",
    "mask": r"[A-Za-z0-9._%+-]*[*•]{2,}[A-Za-z0-9._%+@*.•-]*",
    "registry": r"[a-z][a-z0-9_.-]{1,31}",
    "registration_id": r"[A-Za-z0-9][A-Za-z0-9_.-]{1,63}",
    "record_system": r"[a-z][a-z0-9_.-]{1,31}",
    "record_id": r"[A-Za-z0-9][A-Za-z0-9_.-]{1,63}",
}

#: The thirteen types ontology/selectors.yaml repo_scan calls shape_detectable,
#: each with the segment names its form declares, in order.
TYPE_SEGMENTS = {
    "platform_uid": ("platform", "opaque_id"),
    "channel": ("platform", "channel_id"),
    "handle": ("platform", "string"),
    "username_string": ("string",),
    "email": ("addr",),
    "phone": ("e164",),
    "domain": ("fqdn",),
    "image_phash": ("hex64",),
    "org_registration_number": ("registry", "registration_id"),
    "public_record_id": ("record_system", "record_id"),
    "email_hint_recovery_masked": ("mask",),
    "phone_hint_recovery_masked": ("mask",),
    "email_generated_permutation": ("addr",),
}

#: What the scan does not reach, printed on every run rather than implied. The
#: first three are the registry's own not_shape_detectable list; the fourth is
#: this tool's declared coverage gap under VR-U1.
SCAN_DOES_NOT_REACH = (
    "a person's name, an alias, and an organization's name, which are ordinary "
    "words no shape finds (ontology/selectors.yaml repo_scan.detection_gap)",
    "a postal address, a bounding box and a time window, which the registry "
    "calls partially detectable and this tool does not attempt",
    "a bare value carrying no selector type, such as an address pasted into a "
    "stack trace or a handle written into a worklog entry. VR-U1 carries the "
    "question and the measurement behind it",
    "git history, which no commit-time check reaches and no later act clears",
)

PLACEHOLDER_RE = re.compile(r"<([^<>]+)>")
#: A dated stamp row in the pin of record: a table row whose cells carry the
#: artifact path, an ISO date and a ratifier.
DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
CRITERION_ROW_RE = re.compile(r"^\|\s*((?:SS|RT|EG|CR|HY)-\d+)\b", re.M)

# ---------------------------------------------------------------------------
# The questions this tool does not answer.
#
# Two registers, on the pattern the two artifacts under lint already use. A
# READING is a choice the tool had to make to exist at all, recorded so the
# operator can confirm or correct it, on the model of doctrine/
# DOCTRINE_STATUS.md's assistant-readings table. An UNRATIFIED entry is a
# question the tool refuses to answer, with the refusal stated and the legal
# options recorded.
# ---------------------------------------------------------------------------

#: (id, question, the reading taken, what would change it)
READINGS = (
    (
        "VR-R1",
        "What predicate over doctrine/DOCTRINE_STATUS.md makes a criterion ratified",
        "A recorded conclusion alone. The pin of record says every basis stamp "
        "blocks nothing mechanical, so a both-stamps predicate would make every "
        "mode here refuse every invocation",
        "A stamped basis becoming a condition, which is a rank-1 edit",
    ),
    (
        "VR-R2",
        "What --shred-roundtrip exercises while the blob store, the sweep and "
        "verify_shred are Step 11",
        "The conformance document, graded as a document. A clean run proves the "
        "fixture is internally honest and proves nothing about a shred",
        "Step 11 landing the store, at which point the executable round trip "
        "replaces this reading rather than joining it",
    ),
    (
        "VR-R3",
        "Whether --policy refuses while policy/retention.yaml is unstamped",
        "It refuses. RETENTION.md names this tool and the sweep in the same "
        "sentence as the refusal, and a retention mechanism that runs on an "
        "unratified TTL is the failure the sentence describes",
        "The operator stamping the artifact, which clears the refusal without "
        "any change here",
    ),
    (
        "VR-R4",
        "Whether the gate telemetry token is one per tool or one per mode",
        "One per mode, with two of the four copied from the tokens "
        "tools/validate_conformance.py already carries",
        "A later step registering these modes in KERNEL_GATE, which moves the "
        "token set and this constant together",
    ),
)

#: (id, class, question, legal options, how this tool refuses)
UNRATIFIED = (
    (
        "VR-U1",
        "B",
        "Where do the machine-readable shapes --repo-scan matches on live, and "
        "which rank governs widening one",
        (
            "Under each matcher entry in ontology/selectors.yaml, which is "
            "rank 3, Class B, and one source for the SS-19 argv shape gate and "
            "this scan together",
            "In policy/matcher-calibration.yaml, the file the registry already "
            "forward-references, which puts a second file behind a Class F "
            "refusal",
            "As module constants in this tool, which is rank 6 and makes "
            "narrowing the scan a tooling diff that no rank-3 validator "
            "reconciles",
        ),
        "The scan refuses to claim coverage it cannot source. It matches the "
        "typed canonical form compiled from the rank-3 selector forms, it does "
        "not run bare-value matching for any type, and every run prints the "
        "four classes it does not reach.",
    ),
    (
        "VR-U2",
        "B",
        "What bare --repo-scan scans, how it differs from --repo-scan --staged, "
        "and whether git history is in scope",
        (
            "--staged scans the index and bare scans every tracked file in the "
            "working tree, so the first full run may refuse on tracked content "
            "that predates the check",
            "Bare scans tracked files at HEAD, with history out of scope and "
            "said so",
            "Bare includes history, which is unbounded and unclearable on a "
            "published repository",
        ),
        "The scan refuses to report the repository as clean. Its summary names "
        "the file set it read and states that git history was not scanned and "
        "cannot be cleared by any act this tool performs.",
    ),
    (
        "VR-U3",
        "B",
        "Which violation code a --repo-scan finding carries, given that RT-15 "
        "requires FIXTURE_CONTAINS_LIVE_SELECTOR in policy/violation-codes.yaml "
        "and that file declares fifty-seven codes without it",
        (
            "Declare it in spec/layer-model.yaml with an emitted_by of a new "
            "kind and regenerate, which satisfies RT-15 literally and puts a "
            "code that never appears on a PSE event into the wire vocabulary",
            "Emit a tool-local code on the sibling pattern and record that the "
            "doctrine's code names the event-level case only, which leaves "
            "RT-15's third enforcement part unsatisfied as written",
            "Both, each with a stated scope",
        ),
        "The scan refuses to mint the code. It emits the tool-local code, and "
        "every run states that RT-15 is enforced in three of its four parts and "
        "names the rank-3 edit and regeneration the fourth needs. The statement "
        "disappears when the code is declared, and the finding carries the "
        "declared code from that run onward.",
    ),
    (
        "VR-U4",
        "B",
        "What --finding reads as the case's selector set, and where its "
        "stratum-3 stamp is written",
        (
            "The case store, which EG-2 puts in ISOLATED, so the mode runs "
            "there and refuses anywhere else",
            "A caller-supplied selector-set file, which makes the tool portable "
            "and moves the failure to whoever produced the file",
            "Defer the mode until the first case close",
        ),
        "The mode refuses and writes no stamp. There is no case store to read "
        "and no stamp location, so a pass would be the finding check reporting "
        "that it had run when it had not.",
    ),
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


def refuse(code: str, where: str, detail: str, moves: str) -> None:
    """Print a four-line refusal before there are findings to collect."""
    print(Finding(code, where, detail, moves).render(), file=sys.stderr)


def dig(node, dotted: str):
    """Read a dotted path out of a nested mapping, or return None."""
    cur = node
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def as_list(value) -> list:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


class Unreadable(Exception):
    """A governed input this tool reads could not be read. Exit code 2."""

    def __init__(self, code: str, where: str, detail: str, moves: str):
        super().__init__(detail)
        self.finding = Finding(code, where, detail, moves)


def _load_yaml(path: Path, rel: str, code: str, why: str, moves: str) -> dict:
    if yaml is None:
        raise Unreadable(
            code,
            rel,
            "PyYAML is not installed, so this gate cannot parse the file it "
            "grades and did not check anything",
            "pip install pyyaml, or move the retention gates to PENDING in "
            "tools/validate_conformance.py",
        )
    if not path.is_file():
        raise Unreadable(code, rel, why, moves)
    try:
        parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise Unreadable(
            code,
            rel,
            f"the file is not parseable YAML: {exc}",
            "fix the syntax; the sweep and this gate read the same parse",
        ) from None
    if not isinstance(parsed, dict):
        raise Unreadable(
            code, rel, "the file did not parse to a mapping", "restore the wrapper key"
        )
    return parsed


def load_policy() -> tuple[dict, str]:
    doc = _load_yaml(
        POLICY,
        POLICY_REL,
        "RETENTION_POLICY_UNREADABLE",
        "the compiled retention policy does not exist, so the sweep has no TTL "
        "to act on and RT-2 has nothing to refuse",
        "write policy/retention.yaml, or move the retention-policy gate to "
        "PENDING in tools/validate_conformance.py",
    )
    return doc, POLICY.read_text(encoding="utf-8")


def load_fixture() -> tuple[dict, str]:
    doc = _load_yaml(
        FIXTURE,
        FIXTURE_REL,
        "SHRED_ROUNDTRIP_UNREADABLE",
        "the shred round trip fixture does not exist, so RT-9's five checks "
        "have no recorded passing conditions and D4 is a sentence with no "
        "artifact behind it",
        "write conformance/retention/shred-roundtrip.yaml, or move the "
        "retention gates to PENDING in tools/validate_conformance.py",
    )
    return doc, FIXTURE.read_text(encoding="utf-8")


def load_registry() -> dict:
    doc = _load_yaml(
        REGISTRY,
        "ontology/selectors.yaml",
        "RETENTION_REPO_SCAN_SOURCE_UNREADABLE",
        "the selector registry does not exist, so the scan has no list of "
        "shape-detectable types and no document exemptions, and it would refuse "
        "or permit for reasons nothing governs",
        "restore ontology/selectors.yaml, or move the retention-repo-scan gate "
        "to PENDING in tools/validate_conformance.py",
    )
    if not isinstance(doc.get("repo_scan"), dict):
        raise Unreadable(
            "RETENTION_REPO_SCAN_SOURCE_UNREADABLE",
            "ontology/selectors.yaml :: repo_scan",
            "the registry carries no repo_scan block, so the scan has no "
            "governed statement of which selector types a text scan can find",
            "restore the repo_scan block, or move the retention-repo-scan gate "
            "to PENDING in tools/validate_conformance.py",
        )
    return doc


def declared_codes() -> set[str]:
    """The violation-code vocabulary, read from the file RT-15 names.

    Read rather than copied. A copy of the list here would give the repository
    two vocabularies that agree until the day one of them changes.
    """
    if yaml is None or not CODES.is_file():
        return set()
    try:
        doc = yaml.safe_load(CODES.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return set()
    out: set[str] = set()
    for entry in as_list((doc.get("violation_codes") or {}).get("codes")):
        if isinstance(entry, dict) and entry.get("code"):
            out.add(str(entry["code"]))
        elif isinstance(entry, str):
            out.add(entry)
    return out


def scan_code(codes: set[str]) -> str:
    return DOCTRINE_SCAN_CODE if DOCTRINE_SCAN_CODE in codes else LOCAL_SCAN_CODE


def load_stamps() -> str:
    if not STATUS.is_file():
        raise Unreadable(
            "DOCTRINE_STATUS_UNREADABLE",
            "doctrine/DOCTRINE_STATUS.md",
            "the pin of record does not exist. Mechanisms read that file rather "
            "than the document they enforce, so with it absent nothing here can "
            "tell a stamped criterion from an unstamped one and every mode "
            "refuses",
            "restore doctrine/DOCTRINE_STATUS.md from git, or move the "
            "retention gates to PENDING in tools/validate_conformance.py",
        )
    return STATUS.read_text(encoding="utf-8")


def stamped_criteria(status: str) -> set[str]:
    """Criteria with a row in the per-criterion table.

    Reading VR-R1. The pin of record calls that table the mechanism rather than
    an index of one, and says a criterion with no row there refuses.
    """
    return set(CRITERION_ROW_RE.findall(status))


def stamped_path(status: str, rel: str) -> bool:
    """True when a ratified table row names this artifact with a date.

    Reading VR-R1 again: a recorded conclusion with a date is the predicate, and
    the basis column is read by nobody. Only the Ratified section counts. A
    dated row naming this artifact under the pending, the assistant-readings or
    the rejected-readings heading says the opposite of a stamp, and a predicate
    that read the whole file would take each of those three as one.
    """
    section = ""
    for line in status.splitlines():
        if line.startswith("## "):
            section = line[3:].strip().lower()
        if section != "ratified" or not line.startswith("|") or rel not in line:
            continue
        if DATE_RE.search(line):
            return True
    return False


def build_context() -> dict:
    policy, policy_text = load_policy()
    fixture, fixture_text = load_fixture()
    return {
        "policy": policy,
        "policy_text": policy_text,
        "fixture": fixture,
        "fixture_text": fixture_text,
        "registry": load_registry(),
        "codes": declared_codes(),
        "status": load_stamps(),
    }


# ---------------------------------------------------------------------------
# --policy
# ---------------------------------------------------------------------------


def _placeholder_ids(node, path: str = "") -> list[tuple[str, str]]:
    """Every field that defers to a recorded question, with where it sits.

    The entry lists themselves are skipped. They declare the questions rather
    than deferring to them, and counting a declaration as a reference would make
    the unreferenced half of the reconcile pass on every entry.
    """
    out: list[tuple[str, str]] = []
    if isinstance(node, dict):
        if isinstance(node.get("unratified"), str):
            out.append((str(node["unratified"]), path))
        for key, value in node.items():
            if key in ("entries", "local_entries"):
                continue
            out.extend(_placeholder_ids(value, f"{path}.{key}" if path else key))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            out.extend(_placeholder_ids(value, f"{path}[{index}]"))
    return out


def _check_refusal_prose(entry: dict, where: str) -> list[Finding]:
    """R-08. A refusal states what was refused, which rule, and the moves."""
    out: list[Finding] = []
    text = str(entry.get("refuses_as") or "")
    missing = [label for label in ("where:", "rule:", "moves:") if label not in text]
    if not text.strip():
        missing = ["the whole sentence"]
    if missing:
        out.append(
            Finding(
                "RETENTION_REFUSAL_PROSE_INCOMPLETE",
                where,
                "the refusal this placeholder renders is missing "
                f"{', '.join(missing)}, so a reader is told that something was "
                "refused without being told which rule refused it or what may "
                "legally be done next. CLAUDE.md section 4 governs refusal "
                "strings as prose and renders a state as its consequence",
                "write the refusal with the consequence first, then where, "
                "rule and moves, on the pattern of the entries beside it",
            )
        )
    return out


def _check_placeholders(
    node: dict, entries: list, rel: str, prefix: str, pool: dict | None = None
) -> list[Finding]:
    """R-07. Both directions of the placeholder reconcile, plus completeness.

    `pool` is the set of entries declared in the other artifact. An entry may
    carry its options by pointing at one of those with `tracks` rather than
    restating them, because two independently resolvable copies of one question
    can be stamped to two different answers.
    """
    out: list[Finding] = []
    pool = pool or {}
    declared = {
        str(entry.get("id")): entry for entry in entries if isinstance(entry, dict)
    }
    used = _placeholder_ids(node)
    for pid, where in used:
        if pid not in declared and pid.startswith(prefix):
            out.append(
                Finding(
                    "RETENTION_PLACEHOLDER_UNDECLARED",
                    f"{rel} :: {where or pid}",
                    f"the field defers to {pid} and no entry declares it, so the "
                    "field reads as a recorded open question while the question "
                    "itself was never written down",
                    f"add the {pid} entry with its question, its legal options, "
                    "its sources and its refusal, or fill the field with a "
                    "ratified value",
                )
            )
    referenced = {pid for pid, _ in used}
    for pid, entry in declared.items():
        if pid not in referenced and not entry.get("referenced_by"):
            out.append(
                Finding(
                    "RETENTION_PLACEHOLDER_UNREFERENCED",
                    f"{rel} :: {pid}",
                    "the entry records an open question that no field defers "
                    "to, so nothing in the compiled artifact refuses on it and "
                    "stamping it would change no behaviour",
                    "point a field at it, or delete the entry",
                )
            )
        options = as_list(entry.get("legal_options"))
        tracks = [str(part) for part in as_list(entry.get("tracks"))]
        tracked = next((part for part in tracks if part in pool), None)
        if tracks and tracked is None:
            out.append(
                Finding(
                    "RETENTION_PLACEHOLDER_UNDECLARED",
                    f"{rel} :: {pid}",
                    "the entry says it tracks a question in another artifact and "
                    f"none of {tracks} is declared there, so the options it "
                    "defers to cannot be read and stamping the other artifact "
                    "would leave this one open with nothing to point at",
                    "correct the pointer, or restate the options here",
                )
            )
        if tracked is not None:
            options = as_list((pool.get(tracked) or {}).get("legal_options"))
        if not entry.get("question") or len(options) < 2 or not entry.get("sources"):
            out.append(
                Finding(
                    "RETENTION_PLACEHOLDER_INCOMPLETE",
                    f"{rel} :: {pid}",
                    "the entry does not carry a question, at least two legal "
                    "options and its sources. An open question with one option "
                    "is a decision written as a placeholder, which is the shape "
                    "an invented default takes when it is dressed as a gap",
                    "state the question, record every option that is legal "
                    "under doctrine, and cite the criteria that bound it",
                )
            )
        out.extend(_check_refusal_prose(entry, f"{rel} :: {pid}"))
    return out


def check_policy(ctx: dict) -> list[Finding]:
    """Grade policy/retention.yaml against doctrine/RETENTION.md."""
    out: list[Finding] = []
    doc = ctx["policy"]
    text = ctx["policy_text"]

    # House convention: one top-level wrapper key named after the file, so a
    # mistyped key fails closed rather than loading an empty policy.
    if list(doc) != ["retention"]:
        out.append(
            Finding(
                "RETENTION_POLICY_WRAPPER_KEY",
                POLICY_REL,
                "the file does not carry exactly one top-level key named "
                f"retention, it carries {sorted(doc)}. A loader that unwraps by "
                "name reads nothing from a mistyped key, and a policy that "
                "loads as empty permits everything it was written to bound",
                "restore the single retention wrapper key, on the pattern of "
                "policy/producer-authority.yaml and policy/violation-codes.yaml",
            )
        )
        return out
    pol = doc["retention"]

    # R-15. The artifact and its lint may not drift apart.
    if dig(pol, "self_lint") != "tools/validate_retention.py":
        out.append(
            Finding(
                "RETENTION_POLICY_SELF_LINT_DRIFT",
                f"{POLICY_REL} :: retention.self_lint",
                "the policy names a self-lint other than this tool, so the file "
                "and the check that refuses its drift from doctrine no longer "
                "point at each other and either could move alone",
                "name tools/validate_retention.py, or move the check to the "
                "tool the policy names",
            )
        )

    # R-17. Hand-authored, and not one of the generator's five targets.
    if re.search(r"^#\s*GENERATED by tools/generate_pse\.py", text, re.M):
        out.append(
            Finding(
                "RETENTION_POLICY_GENERATED_CLAIM",
                POLICY_REL,
                "the file carries the generated banner. tools/generate_pse.py "
                "owns five targets and this is not one of them, so the banner "
                "claims a drift check that nothing performs and invites an "
                "editor to regenerate a Class F artifact from rank 3",
                "restore the hand-authored header naming this tool as the "
                "self-lint, or add the file to the generator and to its --check",
            )
        )

    # R-02 and R-04. The strata table.
    strata = pol.get("strata") or {}
    rows = [row for row in as_list(strata.get("rows")) if isinstance(row, dict)]
    if len(rows) != STRATA_ROW_COUNT:
        out.append(
            Finding(
                "RETENTION_POLICY_STRATA_ROW_COUNT",
                f"{POLICY_REL} :: retention.strata.rows",
                f"the table carries {len(rows)} rows and RT-1 states seven "
                "across five numbered levels plus telemetry. The two stratum-1 "
                "rows carry different contents and different subject-value "
                "descriptions, so a table keyed on the integer silently loses "
                "the stricter of them",
                "restore the seven rows, each keyed by name and each declaring "
                "its stratum token",
            )
        )

    try:
        import validate_layer_model as lm

        model_strata = set(lm.STRATA)
        model_surviving = set(lm.SURVIVING_STRATA)
        model_crossing = set(lm.CROSSING_STRATA)
    except Exception:
        model_strata, model_surviving, model_crossing = set(), set(), set()

    row_names = set()
    for row in rows:
        name = str(row.get("name") or "?")
        where = f"{POLICY_REL} :: retention.strata.rows.{name}"
        row_names.add(name)
        missing = [
            field
            for field in (
                "stratum",
                "contents",
                "carries_subject_values",
                "lifetime",
                "inside_shred_boundary",
            )
            if field not in row
        ]
        if missing:
            out.append(
                Finding(
                    "RETENTION_POLICY_STRATUM_INCOMPLETE",
                    where,
                    f"the row does not declare {', '.join(missing)}. RT-1 says a "
                    "stratum is declared at write time rather than decided at "
                    "delete time, and a row missing one of these columns leaves "
                    "the write path with nothing to declare",
                    "complete the row from the RT-1 table",
                )
            )
            continue
        stratum = row["stratum"]
        if model_strata and stratum not in model_strata:
            out.append(
                Finding(
                    "RETENTION_POLICY_STRATA_SET_DRIFT",
                    where,
                    f"the row declares stratum {stratum!r}, which is outside the "
                    "set the layer model and its validator pin. A stratum "
                    "nothing else knows about has no egress rule, no lifetime "
                    "and no shred behaviour",
                    "use a declared stratum, or widen STRATA in "
                    "tools/validate_layer_model.py and this policy in one "
                    "commit against a dated stamp in doctrine/DOCTRINE_STATUS.md",
                )
            )
            continue

        # R-01. RT-2's own refusal, and the reason this mode exists.
        if row.get("carries_subject_values") is True and stratum in model_surviving:
            out.append(
                Finding(
                    "RETENTION_SUBJECT_VALUE_IN_SURVIVING_STRATUM",
                    where,
                    f"the row carries subject values and sits in stratum "
                    f"{stratum}, which survives the shred. RT-2 calls that a "
                    "defect rather than a judgment call: the material outlives "
                    "the case it belonged to, and no later act reaches it",
                    "move the field to stratum 0 or 1, derive a value that "
                    "carries nothing about the subject, or drop it",
                )
            )

        # R-04. The boundary and the lifetime have to agree with RT-1.
        inside = row.get("inside_shred_boundary") is True
        if isinstance(stratum, int) and inside != (stratum in INSIDE_SHRED_BOUNDARY):
            out.append(
                Finding(
                    "RETENTION_POLICY_SHRED_BOUNDARY_DRIFT",
                    where,
                    f"stratum {stratum} is declared "
                    f"{'inside' if inside else 'outside'} the shred boundary and "
                    "RT-1 puts it on the other side. The boundary decides what a "
                    "shred destroys, so a row on the wrong side either survives "
                    "when it should die or dies when the audit trail needs it",
                    "restore the RT-1 value, or change RT-1 first",
                )
            )
        if inside and str(row.get("lifetime")).startswith("permanent"):
            out.append(
                Finding(
                    "RETENTION_POLICY_SHRED_BOUNDARY_DRIFT",
                    where,
                    "the row is inside the shred boundary and permanent at once. "
                    "Those two cannot both hold: an object the shred destroys "
                    "does not survive the case",
                    "set the lifetime to the case TTL, or move the row outside "
                    "the boundary",
                )
            )

    for label, declared, pinned, why in (
        (
            "surviving",
            set(as_list(strata.get("surviving"))),
            model_surviving,
            "RT-2 refuses a subject-carrying field in a surviving stratum, so a "
            "wider list here narrows what that refusal covers",
        ),
        (
            "crossing_to_local",
            set(as_list(strata.get("crossing_to_local"))),
            model_crossing,
            "EG-5 fixes which strata cross outward, and a stratum added here "
            "leaves ISOLATED without an egress decision",
        ),
    ):
        if pinned and declared != pinned:
            out.append(
                Finding(
                    "RETENTION_POLICY_STRATA_SET_DRIFT",
                    f"{POLICY_REL} :: retention.strata.{label}",
                    f"the policy declares {sorted(declared, key=str)} and "
                    f"tools/validate_layer_model.py pins "
                    f"{sorted(pinned, key=str)}. {why}",
                    "restore the pinned set, or move both in one commit against "
                    "a dated Class F stamp in doctrine/DOCTRINE_STATUS.md",
                )
            )

    # R-04. Every stamped duration.
    for path, days, criterion in DURATIONS:
        actual = dig(pol, path)
        if actual != days:
            out.append(
                Finding(
                    "RETENTION_POLICY_TTL_DRIFT",
                    f"{POLICY_REL} :: retention.{path}",
                    f"the policy carries {actual!r} and {criterion} stamps "
                    f"{days}. This number is how long a person's data is held, "
                    "and it is a one-line diff in a file that reads as "
                    "configuration, which CLAUDE.md gate 2 names as the shape a "
                    "Class F change takes when it looks like a Class B one",
                    f"restore {days}, or ratify the new number with a dated "
                    "stamp in doctrine/DOCTRINE_STATUS.md and move DURATIONS in "
                    "tools/validate_retention.py in that same commit",
                )
            )

    # R-05 and R-06. RT-9's five checks and their false-pass discriminations.
    verification = pol.get("verification") or {}
    checks = [c for c in as_list(verification.get("checks")) if isinstance(c, dict)]
    ids = [c.get("id") for c in checks]
    if sorted(i for i in ids if isinstance(i, int)) != SHRED_CHECKS or len(ids) != len(
        SHRED_CHECKS
    ):
        out.append(
            Finding(
                "RETENTION_POLICY_VERIFICATION_INCOMPLETE",
                f"{POLICY_REL} :: retention.verification.checks",
                f"the compiled checks are {ids} and RT-9 is five checks, each "
                "once. A receipt of one check counted five times reports a "
                "verification that never distinguished the five things it "
                "claims to have distinguished",
                "restore checks 1 through 5, each once, each with the object it "
                "acts on and the condition it passes under",
            )
        )
    by_id = {c.get("id"): c for c in checks}
    first = by_id.get(1) or {}
    fails = {str(x) for x in as_list(first.get("fails_when"))}
    if "key" not in str(first.get("passes_when") or "") or not set(
        FALSE_PASS_ON_KEY
    ) <= fails:
        out.append(
            Finding(
                "RETENTION_POLICY_FALSE_PASS_UNGUARDED",
                f"{POLICY_REL} :: retention.verification.checks.1",
                "check 1 does not require the decrypt to fail on the key and "
                "name not-found, permission-denied and malformed-input as "
                "failures. Each of those three reports that nothing could be "
                "read for a reason other than the key being gone, so the check "
                "would pass while proving nothing about the key",
                "restore the passing condition to the decrypt failing on the "
                "key, and list the three false passes as failures",
            )
        )
    second = by_id.get(2) or {}
    if second.get("cached_read_path_permitted") is not False or second.get(
        "delete_exit_code_accepted_as_evidence"
    ) is not False:
        out.append(
            Finding(
                "RETENTION_POLICY_FALSE_PASS_UNGUARDED",
                f"{POLICY_REL} :: retention.verification.checks.2",
                "check 2 does not forbid a cached read path and a DELETE exit "
                "code as evidence of absence. The measured incident behind RT-9 "
                "is a read path that served the first write of a key after the "
                "object had been overwritten and deleted",
                "restore both flags to false, so absence is read over the S3 "
                "API and never inferred from a delete's own result",
            )
        )
    third = by_id.get(3) or {}
    if "query_returns_zero_rows" not in {
        str(x) for x in as_list(third.get("fails_when"))
    }:
        out.append(
            Finding(
                "RETENTION_POLICY_FALSE_PASS_UNGUARDED",
                f"{POLICY_REL} :: retention.verification.checks.3",
                "check 3 does not name a query returning zero rows as a "
                "failure. The table is gone and the table returned nothing are "
                "different facts that look identical in a result set, and only "
                "the first is evidence of a shred",
                "restore query_returns_zero_rows to the check's failure list",
            )
        )

    # R-09's write-path half: RT-9 sends the witness mechanics to the fixture
    # and keeps three properties the store has to know at first write.
    witness = verification.get("witness") or {}
    if (
        witness.get("count_per_case") != 1
        or witness.get("designated_at") != "first_write"
        or "enumerable delete path" not in str(witness.get("held_outside") or "")
    ):
        out.append(
            Finding(
                "RETENTION_POLICY_WITNESS_UNDESIGNATED",
                f"{POLICY_REL} :: retention.verification.witness",
                "the witness is not declared as one ciphertext per case, "
                "designated at first write, held outside the enumerable delete "
                "path. A store that designates no witness at first write leaves "
                "check 1 with nothing to try the key against at the first real "
                "case, and a witness inside the delete path makes check 1 pass "
                "on a not-found",
                "restore the three properties RT-9 states, and leave the "
                "designation mechanics to "
                "conformance/retention/shred-roundtrip.yaml",
            )
        )

    # R-07 and R-08.
    out.extend(
        _check_placeholders(
            pol, as_list(dig(pol, "unratified.entries")), POLICY_REL, "U-"
        )
    )

    # R-09. The designed refusal, and the check that clears when it is stamped.
    status = ctx["status"]
    for criterion in as_list(dig(pol, "ratification.criteria_compiled_here")):
        if str(criterion) not in stamped_criteria(status):
            out.append(
                Finding(
                    "RETENTION_CRITERION_UNSTAMPED",
                    f"doctrine/DOCTRINE_STATUS.md :: {criterion}",
                    f"the policy compiles {criterion} and the pin of record "
                    "carries no row for it. A criterion with no row refuses "
                    "rather than permits, so the rule compiled from it binds "
                    "nothing",
                    f"add the {criterion} row to the per-criterion table, or "
                    "remove the rule this policy compiled from it",
                )
            )
    if not stamped_path(status, POLICY_REL):
        out.append(
            Finding(
                "RETENTION_POLICY_UNRATIFIED",
                "doctrine/DOCTRINE_STATUS.md",
                "THE RETENTION SWEEP MAY NOT RUN AND NO CASE MAY OPEN. The pin "
                "of record carries no dated row for policy/retention.yaml, and "
                "an unratified criterion refuses rather than permits. For a "
                "retention mechanism that means the sweep refuses to run rather "
                "than running with an unratified TTL, which is what "
                "doctrine/RETENTION.md states where it names this tool",
                "stamp policy/retention.yaml in doctrine/DOCTRINE_STATUS.md "
                "with a date and a ratifier, which clears this refusal with no "
                "change to this tool; or leave the sweep stopped and open no "
                "case, which is the state this refusal describes",
            )
        )
    return out


# ---------------------------------------------------------------------------
# --shred-roundtrip
# ---------------------------------------------------------------------------


def check_roundtrip(ctx: dict) -> list[Finding]:
    """Grade the conformance document. Reading VR-R2 bounds what this proves."""
    out: list[Finding] = []
    doc = ctx["fixture"]
    if list(doc) != ["shred_roundtrip"]:
        out.append(
            Finding(
                "SHRED_ROUNDTRIP_WRAPPER_KEY",
                FIXTURE_REL,
                "the file does not carry exactly one top-level key named "
                f"shred_roundtrip, it carries {sorted(doc)}. A loader that "
                "unwraps by name reads nothing from a mistyped key, and a "
                "fixture that loads as empty grades everything as passing",
                "restore the single shred_roundtrip wrapper key",
            )
        )
        return out
    fx = doc["shred_roundtrip"]

    verify = fx.get("verify_step") or {}
    checks = [c for c in as_list(verify.get("checks")) if isinstance(c, dict)]
    ids = [c.get("id") for c in checks]
    if sorted(i for i in ids if isinstance(i, int)) != SHRED_CHECKS or len(ids) != len(
        SHRED_CHECKS
    ):
        out.append(
            Finding(
                "SHRED_ROUNDTRIP_CHECK_SET",
                f"{FIXTURE_REL} :: shred_roundtrip.verify_step.checks",
                f"the fixture models {ids} and RT-9 is five checks, each once. "
                "One check counted five times is the receipt RT-9 names as not "
                "being a check at all",
                "restore checks 1 through 5, each once",
            )
        )
    for check in checks:
        if not check.get("acts_on") or not check.get("passes_when"):
            out.append(
                Finding(
                    "SHRED_ROUNDTRIP_CHECK_INCOMPLETE",
                    f"{FIXTURE_REL} :: verify_step.checks.{check.get('id')}",
                    "the check does not name the object it acts on and the "
                    "condition it passes under, so a run could report it green "
                    "without anyone being able to say what was examined",
                    "state acts_on and passes_when for the check",
                )
            )
    by_id = {c.get("id"): c for c in checks}

    first = by_id.get(1) or {}
    fails = {str(x) for x in as_list(first.get("fails_when"))}
    if "key" not in str(first.get("passes_when") or "") or not set(
        FALSE_PASS_ON_KEY
    ) <= fails:
        out.append(
            Finding(
                "SHRED_ROUNDTRIP_FALSE_PASS_UNGUARDED",
                f"{FIXTURE_REL} :: verify_step.checks.1",
                "check 1 does not require the decrypt to fail on the key while "
                "naming not-found, permission-denied and malformed-input as "
                "failures. A draft of RT-9 pointed check 1 at a blob check 2 "
                "requires to be gone, and it would have passed on a not-found "
                "while reporting that the key had been destroyed",
                "restore the passing condition and the three false passes",
            )
        )
    second = by_id.get(2) or {}
    if second.get("cached_read_path_permitted") is not False or second.get(
        "delete_exit_code_accepted_as_evidence"
    ) is not False:
        out.append(
            Finding(
                "SHRED_ROUNDTRIP_FALSE_PASS_UNGUARDED",
                f"{FIXTURE_REL} :: verify_step.checks.2",
                "check 2 does not forbid a cached read path and a DELETE exit "
                "code as evidence. Both were measured serving a stale answer in "
                "the precedent this criterion is written from",
                "restore both flags to false",
            )
        )
    third = by_id.get(3) or {}
    if "query_returns_zero_rows" not in {
        str(x) for x in as_list(third.get("fails_when"))
    }:
        out.append(
            Finding(
                "SHRED_ROUNDTRIP_FALSE_PASS_UNGUARDED",
                f"{FIXTURE_REL} :: verify_step.checks.3",
                "check 3 does not name a query returning zero rows as a "
                "failure, so the fixture accepts an empty result as proof that "
                "the table is gone",
                "restore query_returns_zero_rows to the check's failure list",
            )
        )

    create = fx.get("create_step") or {}
    roles = [str(r) for r in as_list(create.get("case_roles"))]
    if create.get("case_count") != 2 or "canary" not in roles:
        out.append(
            Finding(
                "SHRED_ROUNDTRIP_NO_CANARY",
                f"{FIXTURE_REL} :: shred_roundtrip.create_step",
                "the scenario does not build a second, adjacent case. RT-9 "
                "check 5 reads an adjacent case to catch an over-eager shred, "
                "whose failure mode is silent: a sweep with a bad case-id "
                "filter that destroys two cases reports one success",
                "restore the target and canary pair, or delete check 5 and say "
                "in RT-9 that anti-overreach is unverified",
            )
        )
    wrapping = create.get("key_wrapping_rule") or {}
    if (
        create.get("atomic") is not True
        or wrapping.get("per_case_data_key") is not True
        or wrapping.get("encrypted_from") != "first_write"
        or wrapping.get("plaintext_intermediate_state_legal") is not False
    ):
        out.append(
            Finding(
                "SHRED_ROUNDTRIP_PLAINTEXT_LEGAL",
                f"{FIXTURE_REL} :: shred_roundtrip.create_step",
                "the create step admits a state in which case material exists "
                "before it is encrypted. RT-4 is the criterion that cannot be "
                "retrofitted: a blob written in plaintext is outside the "
                "crypto-shred forever, so create and encrypt are one act rather "
                "than two steps",
                "restore atomic, the per-case data key from first write, and "
                "the illegality of a plaintext intermediate state",
            )
        )

    witness = None
    for built in as_list(create.get("builds")):
        if isinstance(built, dict) and "witness" in str(built.get("object") or ""):
            witness = built
            break
    if witness is None or (
        witness.get("designated_at") != "first_write"
        or "enumerable delete path" not in str(witness.get("held_outside") or "")
        or witness.get("count_per_case") != 1
    ):
        out.append(
            Finding(
                "SHRED_ROUNDTRIP_WITNESS_UNDESIGNATED",
                f"{FIXTURE_REL} :: shred_roundtrip.create_step.builds",
                "the scenario does not build one witness ciphertext per case, "
                "designated at first write and held outside the enumerable "
                "delete path. Without it check 1 has nothing to try the key "
                "against after the shred",
                "restore the witness object with RT-9's three properties",
            )
        )

    order = [str(step).lower() for step in as_list(dig(fx, "receipt_step.order"))]
    if (
        len(order) < 3
        or "shred" not in order[0]
        or "verify" not in order[1]
        or "ledger row" not in order[-1]
    ):
        out.append(
            Finding(
                "SHRED_ROUNDTRIP_RECEIPT_ORDER",
                f"{FIXTURE_REL} :: shred_roundtrip.receipt_step.order",
                "the receipt order does not run shred, then verification, then "
                "the ledger row. A row appended before verification records a "
                "shred that has not been proven, and RT-10 says a shred with no "
                "receipt row did not happen",
                "restore the three ordered steps, with the ledger row appended "
                "only after all five checks pass",
            )
        )

    # The check that keeps this mode from reading as more than it is.
    boundary = fx.get("step_boundary") or {}
    if not boundary.get("what_this_file_is_not") or not boundary.get(
        "vacuous_pass_named"
    ):
        out.append(
            Finding(
                "SHRED_ROUNDTRIP_VACUOUS_PASS",
                f"{FIXTURE_REL} :: shred_roundtrip.step_boundary",
                "the fixture does not state what it is not and does not name "
                "the vacuous pass it could be mistaken for. A document "
                "describing a check nobody has run is not the check having run, "
                "and a green result here would otherwise read as a shred having "
                "been verified",
                "state what this file is not, and name the vacuous pass in "
                "place rather than leaving a reader to infer it",
            )
        )

    unratified = fx.get("unratified") or {}
    policy_ids = {
        str(entry.get("id")): entry
        for entry in as_list(dig(ctx["policy"], "retention.unratified.entries"))
        if isinstance(entry, dict)
    }
    out.extend(
        _check_placeholders(
            fx,
            as_list(unratified.get("local_entries")),
            FIXTURE_REL,
            "SR-U",
            policy_ids,
        )
    )
    for tracked in as_list(unratified.get("tracked_from_policy_retention")):
        if not isinstance(tracked, dict):
            continue
        tid = str(tracked.get("id"))
        if tid not in policy_ids:
            out.append(
                Finding(
                    "SHRED_ROUNDTRIP_PLACEHOLDER_UNDECLARED",
                    f"{FIXTURE_REL} :: shred_roundtrip.unratified.{tid}",
                    f"the fixture tracks {tid} from policy/retention.yaml and "
                    "that file declares no such entry, so the fixture defers to "
                    "a question no artifact carries",
                    f"correct the id, declare {tid} in policy/retention.yaml, "
                    "or drop the reference",
                )
            )

    if not stamped_path(ctx["status"], FIXTURE_REL):
        out.append(
            Finding(
                "SHRED_ROUNDTRIP_UNRATIFIED",
                "doctrine/DOCTRINE_STATUS.md",
                "NO CASE MAY OPEN AND NO SHRED MAY BE CLAIMED AS VERIFIED. The "
                "pin of record carries no dated row for "
                "conformance/retention/shred-roundtrip.yaml. SS-14 item 6 "
                "blocks all collection until every artifact it names is "
                "stamped, and an unratified criterion refuses rather than "
                "permits",
                "stamp conformance/retention/shred-roundtrip.yaml in "
                "doctrine/DOCTRINE_STATUS.md with a date and a ratifier, which "
                "clears this refusal with no change to this tool; or collect "
                "nothing, which is the state this refusal describes",
            )
        )
    return out


# ---------------------------------------------------------------------------
# --repo-scan
# ---------------------------------------------------------------------------


def _form_segments(registry: dict, selector: str) -> tuple[str, ...] | None:
    """The placeholder names in a selector's rank-3 form, in order."""
    spec = (registry.get("selectors") or {}).get(selector)
    if not isinstance(spec, dict) or not isinstance(spec.get("form"), str):
        return None
    form = spec["form"]
    prefix = f"{selector}:"
    if not form.startswith(prefix):
        return None
    return tuple(PLACEHOLDER_RE.findall(form[len(prefix):]))


def check_scan_shapes(ctx: dict) -> list[Finding]:
    """R-11. The shape table is a compilation of rank 3, in both directions."""
    out: list[Finding] = []
    registry = ctx["registry"]
    detectable = [str(t) for t in as_list(registry["repo_scan"].get("shape_detectable"))]
    for selector in detectable:
        if selector not in TYPE_SEGMENTS:
            out.append(
                Finding(
                    "RETENTION_REPO_SCAN_SHAPES_INCOMPLETE",
                    "tools/validate_retention.py :: TYPE_SEGMENTS",
                    f"the registry calls {selector} shape detectable and this "
                    "tool carries no shape for it, so the scan reports a clean "
                    "run over a type it never looked for",
                    f"add {selector} to TYPE_SEGMENTS with the segment names "
                    "its form declares, or move the type out of "
                    "shape_detectable in ontology/selectors.yaml",
                )
            )
            continue
        segments = _form_segments(registry, selector)
        if segments is None:
            out.append(
                Finding(
                    "RETENTION_REPO_SCAN_SHAPES_DRIFT",
                    f"ontology/selectors.yaml :: selectors.{selector}.form",
                    "the selector declares no form opening with its own type "
                    "token, so the scan cannot compile a typed pattern for it",
                    "restore the form as the type, a colon, and its "
                    "placeholders",
                )
            )
            continue
        if tuple(TYPE_SEGMENTS[selector]) != segments:
            out.append(
                Finding(
                    "RETENTION_REPO_SCAN_SHAPES_DRIFT",
                    f"tools/validate_retention.py :: TYPE_SEGMENTS.{selector}",
                    f"this tool compiles {list(TYPE_SEGMENTS[selector])} and the "
                    f"rank-3 form declares {list(segments)}. A scan built on a "
                    "stale form matches a shape the registry no longer uses, "
                    "which is a gate that fires on nothing and says nothing",
                    "move TYPE_SEGMENTS to the form, or correct the form",
                )
            )
    for selector in TYPE_SEGMENTS:
        if selector not in detectable:
            out.append(
                Finding(
                    "RETENTION_REPO_SCAN_SHAPES_DRIFT",
                    f"tools/validate_retention.py :: TYPE_SEGMENTS.{selector}",
                    "this tool scans for a type the registry does not call "
                    "shape detectable, so a refusal here rests on a claim rank "
                    "3 does not make",
                    "remove the entry, or add the type to shape_detectable in "
                    "ontology/selectors.yaml",
                )
            )
    for exemption in as_list(registry["repo_scan"].get("document_exemptions")):
        if not isinstance(exemption, dict):
            continue
        path = str(exemption.get("path") or "")
        if path and not (ROOT / path).is_file():
            out.append(
                Finding(
                    "RETENTION_EXEMPTION_DANGLING",
                    "ontology/selectors.yaml :: repo_scan.document_exemptions",
                    f"the registry exempts {path} and no such file exists, so a "
                    "named, reviewable gap has become a line nobody can review",
                    "correct the path, or remove the exemption",
                )
            )
    return out


def compile_patterns(registry: dict) -> dict[str, re.Pattern]:
    """Build one typed pattern per shape-detectable selector, from its form."""
    out: dict[str, re.Pattern] = {}
    for selector in as_list(registry["repo_scan"].get("shape_detectable")):
        selector = str(selector)
        segments = _form_segments(registry, selector)
        if segments is None or selector not in TYPE_SEGMENTS:
            continue
        if tuple(TYPE_SEGMENTS[selector]) != segments:
            continue
        spec = registry["selectors"][selector]["form"]
        remainder = spec[len(selector) + 1:]
        parts = PLACEHOLDER_RE.split(remainder)
        body = ""
        for index, chunk in enumerate(parts):
            if index % 2:
                body += "(?:" + SEGMENT_SHAPES[chunk] + ")"
            else:
                body += re.escape(chunk)
        out[selector] = re.compile(
            r"(?<![A-Za-z0-9_])" + re.escape(selector) + ":" + body + r"(?![A-Za-z0-9_])"
        )
    return out


def synthetic_allowlist(registry: dict) -> tuple[set[str], str]:
    """The allowlist, and the state of the cast rendered as its consequence.

    There is never an allowlist of live values. The only allowlist is the
    synthetic one and it is read from a sealed cast, so an unsealed cast
    produces an empty set and the scan runs on shape alone.
    """
    before = "the cast is unsealed, so the scan runs on shape alone and builds no synthetic allowlist"
    if yaml is None or not TRUTH.is_file():
        return set(), before
    try:
        truth = yaml.safe_load(TRUTH.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return set(), before
    seal = truth.get("seal") or {}
    if seal.get("sealed") is not True:
        return set(), before
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import validate_cast

        digest, count = validate_cast.canonical_digest(TRUTH.read_text(encoding="utf-8"))
    except Exception:
        digest, count = "", 0
    if count != 1 or digest != seal.get("sha256"):
        return (
            set(),
            "THE SYNTHETIC ALLOWLIST WAS NOT BUILT. The cast declares itself "
            "sealed and its recorded digest does not verify, so it authorizes "
            "nothing and the scan runs on shape alone",
        )
    values: set[str] = set()

    def walk(node):
        if isinstance(node, dict):
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)
        elif isinstance(node, str) and not node.startswith("<"):
            values.add(node)

    walk(truth.get("personas"))
    walk(truth.get("truth"))
    return values, (
        f"the cast is sealed and its digest verifies, so {len(values)} synthetic "
        "values are permitted and anything else is a finding"
    )


def scan_text(
    rel: str,
    text: str,
    patterns: dict[str, re.Pattern],
    exemptions: dict[str, set[str]],
    allowlist: set[str],
    code: str,
) -> list[Finding]:
    """Scan one file's content. The finding never carries what matched.

    RT-19 and HY-1: a record names the file and the line and never the string.
    The refusal below is written the same way, because a refusal quoting the
    match would put the value into a terminal, a CI log and an issue thread,
    which are three more durable surfaces than the one it was guarding.
    """
    out: list[Finding] = []
    exempt = exemptions.get(rel, set())
    for number, line in enumerate(text.splitlines(), 1):
        for selector, pattern in patterns.items():
            if selector in exempt:
                continue
            match = pattern.search(line)
            if not match or match.group(0) in allowlist:
                continue
            out.append(
                Finding(
                    code,
                    f"{rel}:{number}",
                    f"the line carries a filled {selector} selector. Git history "
                    "is append-only, distributed to every clone, and survives "
                    "git rm, so a selector committed here is outside every "
                    "mechanism doctrine/RETENTION.md describes and no later act "
                    "reaches it. This refusal does not quote what matched, per "
                    "RT-19",
                    "replace the value with a placeholder in the registry's "
                    "form, replace it with a synthetic value once the cast is "
                    "sealed, or add the file to repo_scan.document_exemptions "
                    "in ontology/selectors.yaml with the selector types it "
                    "covers and the reason",
                )
            )
            break
    return out


def _git(args: list[str]) -> str:
    proc = subprocess.run(
        ["git"] + args,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        raise Unreadable(
            "RETENTION_REPO_SCAN_SOURCE_UNREADABLE",
            "git",
            f"git {' '.join(args)} failed, so the scan has no file set and did "
            "not check anything",
            "run the scan inside a git working tree, or move the "
            "retention-repo-scan gate to PENDING in "
            "tools/validate_conformance.py",
        )
    return proc.stdout


def scan_paths(staged: bool) -> list[tuple[str, str]]:
    """The file set, and its content. Reading VR-U2 bounds what this covers."""
    out: list[tuple[str, str]] = []
    if staged:
        names = [
            n
            for n in _git(
                ["diff", "--cached", "--name-only", "--diff-filter=ACMR"]
            ).splitlines()
            if n.strip()
        ]
        for name in names:
            proc = subprocess.run(
                ["git", "show", f":{name}"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            if proc.returncode == 0:
                out.append((name, proc.stdout))
        return out
    for name in _git(["ls-files"]).splitlines():
        if not name.strip():
            continue
        path = ROOT / name
        try:
            out.append((name, path.read_text(encoding="utf-8")))
        except (OSError, UnicodeDecodeError):
            continue
    return out


def check_repo_scan(ctx: dict, staged: bool) -> tuple[list[Finding], dict]:
    registry = ctx["registry"]
    findings = check_scan_shapes(ctx)
    patterns = compile_patterns(registry)
    exemptions = {
        str(e.get("path")): {str(t) for t in as_list(e.get("selector_types"))}
        for e in as_list(registry["repo_scan"].get("document_exemptions"))
        if isinstance(e, dict)
    }
    allowlist, cast_state = synthetic_allowlist(registry)
    code = scan_code(ctx["codes"])
    files = scan_paths(staged)
    for rel, text in files:
        findings.extend(scan_text(rel, text, patterns, exemptions, allowlist, code))
    return findings, {
        "files": len(files),
        "types": len(patterns),
        "cast_state": cast_state,
        "code": code,
        "staged": staged,
    }


def scan_notices(report: dict, codes: set[str]) -> str:
    """The states this mode renders rather than refuses."""
    lines = [f"validate_retention --repo-scan: {report['cast_state']}."]
    if report["code"] != DOCTRINE_SCAN_CODE:
        lines.append(
            "  RT-15 is enforced in three of its four parts. The violation code "
            f"{DOCTRINE_SCAN_CODE} is required in\n"
            "  policy/violation-codes.yaml and that file declares "
            f"{len(codes)} codes without it, so a refusal from this scan "
            "carries\n"
            f"  the tool-local code {LOCAL_SCAN_CODE} and cannot be graded "
            "against the wire vocabulary.\n"
            "  moves: declare the code in spec/layer-model.yaml and run "
            "tools/generate_pse.py; or ratify VR-U3's\n"
            "         second option, which records that doctrine's code names "
            "the event-level case alone."
        )
    lines.append("  this scan did not reach:")
    for item in SCAN_DOES_NOT_REACH:
        lines.append(f"    - {item}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# --finding
# ---------------------------------------------------------------------------


def check_finding(path: str, case: str) -> int:
    """RT-13, refusing. VR-U4 carries the question this mode cannot answer."""
    candidate = Path(path)
    if not candidate.is_file():
        refuse(
            "RETENTION_FINDING_FILE_UNREADABLE",
            path,
            "the candidate writeup does not exist, so nothing was scanned and "
            "the case may not close",
            "pass the path of the writeup, or do not close the case",
        )
        return 2
    refuse(
        "RETENTION_FINDING_NO_CASE_STORE",
        f"case {case}",
        "THE FINDING CHECK DID NOT RUN AND THIS WRITEUP IS NOT CLEARED FOR "
        "PUBLICATION. RT-13 scans a candidate writeup against the case's "
        "selector set at case close, before the shred, while the values still "
        "exist. There is no case store to read that set from: runner/ is empty "
        "until Step 10, the store lands at Step 11, and EG-2 puts it in "
        "ISOLATED where this tool is not running. A pass here would be the "
        "finding check reporting that it had run when it had not",
        "run this mode in ISOLATED once the case store exists, which is Step "
        "11; or hold the writeup, which is the state this refusal describes; "
        "the rejected alternative of retaining a digest of the selector set is "
        "a membership oracle and RETENTION.md RT-13 refuses it by name",
    )
    return 2


# ---------------------------------------------------------------------------
# --self-test
# ---------------------------------------------------------------------------

#: Codes this gate is expected to fire against the tree as it stands, because
#: both graded artifacts are unratified by design. The baseline guard refuses on
#: anything outside this set, and each mutation is judged against the baseline
#: rather than against silence, so a mutation that fires only these has not been
#: refused. Stamping the two artifacts empties this tuple by itself.
EXPECTED_BASELINE = ("RETENTION_POLICY_UNRATIFIED", "SHRED_ROUNDTRIP_UNRATIFIED")


def _sample(rel: str, filled: bool) -> tuple[str, str]:
    """A one-line file for the scan to look at.

    The selector token is assembled at run time rather than written as a
    literal, because this file is tracked and a literal here would be exactly
    the object the scan refuses. A tool that carries the shape it guards against
    is the first thing its own gate should find.
    """
    token = "handle" + ":" + "acmegram" + "/"
    return rel, "note: " + token + ("examplename" if filled else "<string>")


def _mutations():
    """(description, which check, mutator, expected code, expect_only).

    `which` selects the harness: policy and roundtrip mutate the loaded
    artifacts, shapes mutates the registry or this tool's table, and scan builds
    a one-line sample. An expected code written with a leading minus asserts the
    opposite direction, that the named code stops firing, which is how the
    ratification check proves it permits once the stamp lands rather than only
    that it refuses while the stamp is absent.
    """

    def drop_a_stratum_row(ctx):
        ctx["policy"]["retention"]["strata"]["rows"].pop()

    def subject_value_survives(ctx):
        for row in ctx["policy"]["retention"]["strata"]["rows"]:
            if row.get("stratum") == 2:
                row["carries_subject_values"] = True

    def widen_surviving(ctx):
        ctx["policy"]["retention"]["strata"]["surviving"] = [2, 3, 4]

    def move_raw_capture_outside(ctx):
        for row in ctx["policy"]["retention"]["strata"]["rows"]:
            if row.get("stratum") == 0:
                row["inside_shred_boundary"] = False

    def raise_the_ceiling(ctx):
        ctx["policy"]["retention"]["case_ttl"]["ceiling_days"] = 90

    def count_one_check_twice(ctx):
        ctx["policy"]["retention"]["verification"]["checks"][2]["id"] = 1

    def let_check_one_pass_on_not_found(ctx):
        check = ctx["policy"]["retention"]["verification"]["checks"][0]
        check["fails_when"] = [f for f in check["fails_when"] if f != "not_found"]

    def undesignate_the_witness(ctx):
        ctx["policy"]["retention"]["verification"]["witness"]["designated_at"] = "later"

    def defer_to_an_undeclared_question(ctx):
        ctx["policy"]["retention"]["case_ttl"]["default_days"] = {"unratified": "U-99"}

    def declare_a_question_nothing_asks(ctx):
        entries = ctx["policy"]["retention"]["unratified"]["entries"]
        entries.append(
            {
                "id": "U-98",
                "question": "unused",
                "legal_options": ["a", "b"],
                "sources": ["doctrine/RETENTION.md"],
                "refuses_as": "NOTHING HAPPENED.\n  where: x\n  rule:  y\n  moves: z",
            }
        )

    def leave_one_legal_option(ctx):
        ctx["policy"]["retention"]["unratified"]["entries"][0]["legal_options"] = ["one"]

    def empty_a_refusal(ctx):
        ctx["policy"]["retention"]["unratified"]["entries"][0]["refuses_as"] = "no"

    def rename_the_wrapper(ctx):
        ctx["policy"]["retention_policy"] = ctx["policy"].pop("retention")

    def point_the_lint_elsewhere(ctx):
        ctx["policy"]["retention"]["self_lint"] = "tools/validate_layer_model.py"

    def claim_the_file_is_generated(ctx):
        ctx["policy_text"] = (
            "# GENERATED by tools/generate_pse.py from spec/layer-model.yaml\n"
            + ctx["policy_text"]
        )

    def unstamp_a_compiled_criterion(ctx):
        ctx["status"] = re.sub(
            r"^\|\s*RT-9\b.*$", "| placeholder |", ctx["status"], flags=re.M
        )

    def _stamp(ctx, row):
        """Insert a row into the Ratified table, where a stamp actually goes."""
        ctx["status"] = ctx["status"].replace(
            "\n## Pending ratification", row + "\n## Pending ratification", 1
        )

    def stamp_the_policy(ctx):
        _stamp(
            ctx,
            "\n| the compiled retention table | `policy/retention.yaml` | v0.1 "
            "| 2026-09-11 | unstamped | operator |\n",
        )

    def stamp_the_fixture(ctx):
        _stamp(
            ctx,
            "\n| the shred round trip | "
            "`conformance/retention/shred-roundtrip.yaml` | v0.1 | 2026-09-11 "
            "| unstamped | operator |\n",
        )

    def rename_the_fixture_wrapper(ctx):
        ctx["fixture"]["roundtrip"] = ctx["fixture"].pop("shred_roundtrip")

    def count_one_fixture_check_twice(ctx):
        ctx["fixture"]["shred_roundtrip"]["verify_step"]["checks"][3]["id"] = 1

    def let_fixture_check_one_pass_on_not_found(ctx):
        check = ctx["fixture"]["shred_roundtrip"]["verify_step"]["checks"][0]
        check["fails_when"] = [f for f in check["fails_when"] if f != "not_found"]

    def permit_a_cached_read(ctx):
        check = ctx["fixture"]["shred_roundtrip"]["verify_step"]["checks"][1]
        check["cached_read_path_permitted"] = True

    def accept_zero_rows(ctx):
        check = ctx["fixture"]["shred_roundtrip"]["verify_step"]["checks"][2]
        check["fails_when"] = []

    def drop_the_canary(ctx):
        ctx["fixture"]["shred_roundtrip"]["create_step"]["case_count"] = 1

    def legalize_plaintext(ctx):
        rule = ctx["fixture"]["shred_roundtrip"]["create_step"]["key_wrapping_rule"]
        rule["plaintext_intermediate_state_legal"] = True

    def undesignate_the_fixture_witness(ctx):
        for built in ctx["fixture"]["shred_roundtrip"]["create_step"]["builds"]:
            if "witness" in str(built.get("object") or ""):
                built["designated_at"] = "whenever"

    def write_the_receipt_first(ctx):
        step = ctx["fixture"]["shred_roundtrip"]["receipt_step"]
        step["order"] = list(reversed(step["order"]))

    def delete_the_boundary_statement(ctx):
        ctx["fixture"]["shred_roundtrip"]["step_boundary"]["vacuous_pass_named"] = ""

    def track_an_undeclared_question(ctx):
        tracked = ctx["fixture"]["shred_roundtrip"]["unratified"][
            "tracked_from_policy_retention"
        ]
        tracked.append({"id": "U-97", "defined_in": "policy/retention.yaml"})

    def forget_a_detectable_type(ctx):
        TYPE_SEGMENTS.pop("domain", None)

    def rewrite_a_rank_three_form(ctx):
        ctx["registry"]["selectors"]["handle"]["form"] = "handle:<platform>"

    scan = scan_code(declared_codes())
    return [
        ("drop a stratum row", "policy", drop_a_stratum_row, "RETENTION_POLICY_STRATA_ROW_COUNT", True),
        ("give the skeleton a subject value", "policy", subject_value_survives, "RETENTION_SUBJECT_VALUE_IN_SURVIVING_STRATUM", True),
        ("add stratum 4 to the surviving set", "policy", widen_surviving, "RETENTION_POLICY_STRATA_SET_DRIFT", True),
        ("move raw capture outside the shred boundary", "policy", move_raw_capture_outside, "RETENTION_POLICY_SHRED_BOUNDARY_DRIFT", True),
        ("raise the case ceiling to 90 days", "policy", raise_the_ceiling, "RETENTION_POLICY_TTL_DRIFT", True),
        ("count one verification check twice", "policy", count_one_check_twice, "RETENTION_POLICY_VERIFICATION_INCOMPLETE", False, "renumbering check 3 to 1 removes check 3, so the discrimination between an erroring query and an empty result set is gone as well and the false-pass check fires with the set check"),
        ("let check 1 pass on a not-found", "policy", let_check_one_pass_on_not_found, "RETENTION_POLICY_FALSE_PASS_UNGUARDED", True),
        ("designate the witness after the first write", "policy", undesignate_the_witness, "RETENTION_POLICY_WITNESS_UNDESIGNATED", True),
        ("defer a TTL to a question nothing declares", "policy", defer_to_an_undeclared_question, "RETENTION_PLACEHOLDER_UNDECLARED", False, "the TTL is also no longer the stamped number, so the duration check fires with it"),
        ("declare a question no field defers to", "policy", declare_a_question_nothing_asks, "RETENTION_PLACEHOLDER_UNREFERENCED", True),
        ("leave a placeholder one legal option", "policy", leave_one_legal_option, "RETENTION_PLACEHOLDER_INCOMPLETE", True),
        ("empty a placeholder's refusal", "policy", empty_a_refusal, "RETENTION_REFUSAL_PROSE_INCOMPLETE", True),
        ("rename the policy wrapper key", "policy", rename_the_wrapper, "RETENTION_POLICY_WRAPPER_KEY", True),
        ("point the policy's self-lint at another tool", "policy", point_the_lint_elsewhere, "RETENTION_POLICY_SELF_LINT_DRIFT", True),
        ("give the policy the generated banner", "policy", claim_the_file_is_generated, "RETENTION_POLICY_GENERATED_CLAIM", True),
        ("remove a compiled criterion's stamp row", "policy", unstamp_a_compiled_criterion, "RETENTION_CRITERION_UNSTAMPED", True),
        ("stamp the policy in the pin of record", "policy", stamp_the_policy, "-RETENTION_POLICY_UNRATIFIED", True),
        ("rename the fixture wrapper key", "roundtrip", rename_the_fixture_wrapper, "SHRED_ROUNDTRIP_WRAPPER_KEY", True),
        ("count one fixture check twice", "roundtrip", count_one_fixture_check_twice, "SHRED_ROUNDTRIP_CHECK_SET", False, "renumbering check 4 to 1 replaces check 1, whose passing condition is the decrypt failing on the key, so the false-pass guard fires with the set check"),
        ("let fixture check 1 pass on a not-found", "roundtrip", let_fixture_check_one_pass_on_not_found, "SHRED_ROUNDTRIP_FALSE_PASS_UNGUARDED", True),
        ("confirm absence over a cached read path", "roundtrip", permit_a_cached_read, "SHRED_ROUNDTRIP_FALSE_PASS_UNGUARDED", True),
        ("accept zero rows as proof the table is gone", "roundtrip", accept_zero_rows, "SHRED_ROUNDTRIP_FALSE_PASS_UNGUARDED", True),
        ("shred the only case, with no canary beside it", "roundtrip", drop_the_canary, "SHRED_ROUNDTRIP_NO_CANARY", True),
        ("legalize a plaintext intermediate state", "roundtrip", legalize_plaintext, "SHRED_ROUNDTRIP_PLAINTEXT_LEGAL", True),
        ("designate the fixture's witness later", "roundtrip", undesignate_the_fixture_witness, "SHRED_ROUNDTRIP_WITNESS_UNDESIGNATED", True),
        ("append the ledger row before verification", "roundtrip", write_the_receipt_first, "SHRED_ROUNDTRIP_RECEIPT_ORDER", True),
        ("delete the sentence naming the vacuous pass", "roundtrip", delete_the_boundary_statement, "SHRED_ROUNDTRIP_VACUOUS_PASS", True),
        ("track a question the policy does not declare", "roundtrip", track_an_undeclared_question, "SHRED_ROUNDTRIP_PLACEHOLDER_UNDECLARED", True),
        ("stamp the fixture in the pin of record", "roundtrip", stamp_the_fixture, "-SHRED_ROUNDTRIP_UNRATIFIED", True),
        ("forget a shape-detectable type", "shapes", forget_a_detectable_type, "RETENTION_REPO_SCAN_SHAPES_INCOMPLETE", True),
        ("rewrite a rank-3 form under the scan", "shapes", rewrite_a_rank_three_form, "RETENTION_REPO_SCAN_SHAPES_DRIFT", True),
        ("commit a filled account selector", "scan", lambda ctx: _sample("notes/x.md", True), scan, True),
        ("commit the same selector in placeholder form", "scan", lambda ctx: _sample("notes/x.md", False), "-" + scan, True),
        ("commit a filled selector in an exempted document", "scan", lambda ctx: _sample("docs/PLAINSIGHT-design.md", True), "-" + scan, True),
    ]


def _run_check(which: str, ctx: dict, sample) -> set[str]:
    if which == "policy":
        return {f.code for f in check_policy(ctx)}
    if which == "roundtrip":
        return {f.code for f in check_roundtrip(ctx)}
    if which == "shapes":
        return {f.code for f in check_scan_shapes(ctx)}
    registry = ctx["registry"]
    patterns = compile_patterns(registry)
    exemptions = {
        str(e.get("path")): {str(t) for t in as_list(e.get("selector_types"))}
        for e in as_list(registry["repo_scan"].get("document_exemptions"))
        if isinstance(e, dict)
    }
    rel, text = sample
    allowlist, _ = synthetic_allowlist(registry)
    code = scan_code(ctx["codes"])
    return {
        f.code
        for f in scan_text(rel, text, patterns, exemptions, allowlist, code)
    }


def self_test(ctx: dict) -> int:
    """Break each artifact and assert the break is refused.

    The baseline is not silent here and cannot be, because both artifacts land
    unratified and refuse by design. The guard therefore refuses on any code
    outside EXPECTED_BASELINE and every assertion below is made against the
    baseline set rather than against an empty one, so a mutation that fires only
    the designed refusals counts as not refused.
    """
    baseline = set()
    for which in ("policy", "roundtrip", "shapes"):
        baseline |= _run_check(which, copy.deepcopy(ctx), None)
    unexpected = baseline - set(EXPECTED_BASELINE)
    if unexpected:
        print(
            "self-test cannot run: the unmutated artifacts refuse for reasons "
            "beyond the two designed refusals, so every mutation below would "
            "pass for the wrong reason",
            file=sys.stderr,
        )
        for code in sorted(unexpected):
            print(f"  {code}", file=sys.stderr)
        return 1
    if baseline:
        print(
            "  baseline: "
            + ", ".join(sorted(baseline))
            + " fire against the tree as it stands, by design. Each mutation "
            "below is judged against that set."
        )

    failures = cascading = 0
    exercised: set[str] = set()
    muts = _mutations()
    saved = dict(TYPE_SEGMENTS)
    for row in muts:
        desc, which, mutate, expected, only = row[0], row[1], row[2], row[3], row[4]
        local = copy.deepcopy(ctx)
        sample = mutate(local)
        raw = _run_check(which, local, sample)
        # One mutation reaches this module's own table rather than a loaded
        # artifact, because that table is what the reconcile grades. It is
        # restored here so the next row runs against the real one.
        TYPE_SEGMENTS.clear()
        TYPE_SEGMENTS.update(saved)
        fired = raw - baseline
        exercised |= fired
        if expected.startswith("-"):
            wanted = expected[1:]
            gone = wanted not in raw
            ok, note = gone, "" if gone else f", {wanted} still fired"
        elif expected not in fired:
            ok, note = False, f", fired {sorted(fired)}"
        elif only and fired != {expected}:
            ok, note = False, f", also fired {sorted(fired - {expected})} and claims expect_only"
        else:
            ok, note = True, ""
        if ok and not only:
            cascading += 1
        failures += 0 if ok else 1
        mark = "refused" if ok else "PASSED  "
        print(f"  {mark}  {desc:56} expected {expected}{note}")

    print()
    if failures:
        print(
            f"validate_retention --self-test: {failures} mutation(s) were not "
            "refused as claimed. A gate nobody has watched fail is an "
            "assumption (HYGIENE.md section 2).",
            file=sys.stderr,
        )
        return 1
    print(
        f"validate_retention --self-test ok: {len(muts)} deliberate breaks, "
        f"{len(muts)} refused, {len(muts) - cascading} of them by the expected "
        f"code alone, {cascading} cascading with a stated reason. "
        f"{len(exercised)} distinct codes exercised."
    )
    return 0


# ---------------------------------------------------------------------------
# entry
# ---------------------------------------------------------------------------


def open_questions() -> str:
    lines = ["  questions this gate does not answer, and refuses rather than defaults:"]
    for pid, cls, question, _options, refusal in UNRATIFIED:
        lines.append(f"    {pid} (Class {cls}) {question}")
        lines.append(f"      {refusal}")
    lines.append("  readings taken, recorded for confirmation rather than assumed:")
    for rid, question, reading, _changes in READINGS:
        lines.append(f"    {rid} {question}: {reading}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Retention gate.")
    ap.add_argument("--policy", action="store_true", help="Grade policy/retention.yaml. The default.")
    ap.add_argument("--shred-roundtrip", action="store_true", help="Grade conformance/retention/shred-roundtrip.yaml.")
    ap.add_argument("--repo-scan", action="store_true", help="RT-15. Refuse a filled selector in a tracked file.")
    ap.add_argument("--staged", action="store_true", help="With --repo-scan, read the index rather than the working tree.")
    ap.add_argument("--finding", metavar="FILE", help="RT-13. Scan a candidate writeup against a case's selector set.")
    ap.add_argument("--case", metavar="ID", help="With --finding, the case whose selector set is read.")
    ap.add_argument("--self-test", action="store_true", help="Break each artifact in memory and assert each break is refused.")
    ap.add_argument("--questions", action="store_true", help="Print the open questions and the readings taken, and exit.")
    ap.add_argument("--quiet", action="store_true", help="Print only on failure.")
    args = ap.parse_args(argv)

    if args.questions:
        print(open_questions())
        return 0

    if args.finding:
        if not args.case:
            ap.error("--finding needs --case, because the selector set is per case")
        return check_finding(args.finding, args.case)

    try:
        if args.repo_scan:
            ctx = {"registry": load_registry(), "codes": declared_codes()}
            findings, report = check_repo_scan(ctx, args.staged)
            gate = GATE_SCAN
        elif args.shred_roundtrip:
            ctx = build_context()
            findings, report = check_roundtrip(ctx), None
            gate = GATE_ROUNDTRIP
        elif args.self_test:
            return self_test(build_context())
        else:
            ctx = build_context()
            findings, report = check_policy(ctx), None
            gate = GATE_POLICY
    except Unreadable as exc:
        print(exc.finding.render(), file=sys.stderr)
        return 2

    if gate_log:
        try:
            gate_log.record_run(gate, "refuse" if findings else "pass", count=len(findings))
            for fnd in findings:
                gate_log.record_finding(gate, code=fnd.code, where=fnd.where)
        except Exception:
            pass

    # Printed even under --quiet. These are states rather than passes or
    # failures, and CLAUDE.md section 4 renders a state as its consequence.
    if args.repo_scan:
        print(scan_notices(report, ctx["codes"]))

    if findings:
        for fnd in findings:
            print(fnd.render(), file=sys.stderr)
            print(file=sys.stderr)
        print(
            f"validate_retention: {len(findings)} violation(s). "
            "rule: doctrine/RETENTION.md is rank 1 and decides what is retained "
            "and what leaves; CLAUDE.md design gate 1.",
            file=sys.stderr,
        )
        return 1

    if not args.quiet:
        if args.repo_scan:
            scope = "the git index" if report["staged"] else "every tracked file in the working tree"
            print(
                f"validate_retention --repo-scan ok: {report['files']} file(s) "
                f"read from {scope}, {report['types']} selector types matched in "
                "their typed form, no filled selector found."
            )
            print(
                "  this result is not a claim that the repository is clean. It "
                "covers the file set named above and nothing else.\n"
                "  four questions this mode does not answer are open: run "
                "tools/validate_retention.py --questions."
            )
            return 0
        if args.shred_roundtrip:
            print(
                "validate_retention --shred-roundtrip ok: the fixture is "
                "internally consistent, five checks each named once, each false "
                "pass RT-9 warns about guarded."
            )
            print(
                "  not covered by this gate: whether any shred has been "
                "performed or verified. The blob store, "
                "runner/retention_sweep.py and runner/verify_shred.py are Step "
                "11, and this mode graded a document rather than a deletion."
            )
        else:
            pol = ctx["policy"]["retention"]
            rows = len(as_list(dig(pol, "strata.rows")))
            entries = len(as_list(dig(pol, "unratified.entries")))
            print(
                f"validate_retention --policy ok: {rows} strata rows, "
                f"{len(DURATIONS)} stamped durations, 5 verification checks, "
                f"{entries} recorded open questions."
            )
            print(
                "  not covered by this gate: whether any object was actually "
                "written to the stratum it declares, which needs a store; and "
                "the RT-16 reconcile of pinned connector versions against "
                "connectors/, which has neither a ledger nor a connector to "
                "read."
            )
        print(open_questions())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
