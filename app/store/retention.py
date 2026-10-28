"""retain_until, expiry columns, and the retention line, computed and never enforced.

The four durations the case registry carries are copied from
policy/retention.yaml when a case is first ingested, and are never literals in
code. policy/retention.yaml is unratified, so every date computed here is a
reading: the app computes the columns and deletes nothing. Only Step 11's
runner/retention_sweep.py will delete.

Expiry follows RET-R4, the compiled reading: the clock acts on the
subject_relation found along each claim's chain (claim, item, RUN_START,
COLLECT PERMITTED).

- A seed or pivot claim expires at retain_until, and a RETENTION_EXTENSION
  moves it.
- An incidental claim expires at min(retain_until, observed_at +
  incidental_ttl_days), computed once, and an extension does not move it
  (RT-6).
- A claim with no relation on its chain is treated as incidental, the earlier
  of the two clocks.

retain_until is a date. Its instant is read as 00:00:00Z on that date, the
earlier reading, because the granularity, anchor and comparison are U-02 and
unratified.
"""

from __future__ import annotations

import datetime as dt
import hashlib

import yaml

from app import config
from app.refusals import Refusal

POLICY = config.REPO_ROOT / "policy" / "retention.yaml"

#: (registry column, dotted path in policy/retention.yaml under `retention`).
DURATION_PATHS = (
    ("case_ttl_days", "case_ttl.default_days"),
    ("extension_days", "case_ttl.extension_days"),
    ("ceiling_days", "case_ttl.ceiling_days"),
    ("incidental_ttl_days", "incidental.ttl_days"),
)

ANCHOR_READING = "first event ts, U-02 unratified"


def load_durations(path=None) -> dict:
    """The four durations and the policy file's sha256, or RETENTION_POLICY_UNREADABLE."""
    path = POLICY if path is None else path
    try:
        raw = path.read_bytes()
        policy = yaml.safe_load(raw.decode("utf-8"))["retention"]
    except (OSError, UnicodeDecodeError, yaml.YAMLError, KeyError, TypeError):
        raise Refusal("RETENTION_POLICY_UNREADABLE", "the file could not be read as a retention policy") from None
    out = {"policy_sha256": hashlib.sha256(raw).hexdigest()}
    for column, dotted in DURATION_PATHS:
        node = policy
        for part in dotted.split("."):
            node = node.get(part) if isinstance(node, dict) else None
        if not isinstance(node, int) or isinstance(node, bool) or node <= 0:
            raise Refusal("RETENTION_POLICY_UNREADABLE", f"field: {dotted}")
        out[column] = node
    return out


def parse_ts(value: str) -> dt.datetime:
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(dt.timezone.utc)


def format_ts(value: dt.datetime) -> str:
    return value.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def date_instant(day: str) -> str:
    """The instant a retain_until date is read as: 00:00:00Z on that date."""
    return format_ts(dt.datetime.combine(dt.date.fromisoformat(day), dt.time(0, 0), dt.timezone.utc))


def initial_retain_until(anchor_ts: str, case_ttl_days: int) -> str:
    return (parse_ts(anchor_ts).date() + dt.timedelta(days=case_ttl_days)).isoformat()


def expiry(relation, retain_until: str, observed_at: str, incidental_ttl_days: int) -> str:
    """The expires_at of a claim or item under RET-R4 and RT-6."""
    case_clock = date_instant(retain_until)
    if relation in ("seed", "pivot"):
        return case_clock
    incidental = format_ts(parse_ts(observed_at) + dt.timedelta(days=incidental_ttl_days))
    return min(case_clock, incidental, key=parse_ts)


def is_past(row, now: dt.datetime | None = None) -> bool:
    """True when the case is past retain_until: the one retention state the system does not vouch for."""
    now = now or dt.datetime.now(dt.timezone.utc)
    return parse_ts(date_instant(row["retain_until"])) <= now


def retention_line(row, now: dt.datetime | None = None) -> str:
    """The case's retention state rendered as its consequence, never as a token."""
    past = is_past(row, now)
    if row["environment"] == "LOCAL" and row["synthetic"]:
        if past:
            return "past retain_until · synthetic stratum-4 material, no sweep acts on LOCAL"
        return f"retain_until {row['retain_until']} · synthetic stratum-4 material, no sweep acts on LOCAL"
    if past:
        return (
            f"past retain_until {row['retain_until']} · the sweep has not run here yet; "
            "policy/retention.yaml is unratified, so this date is a reading"
        )
    return f"retain_until {row['retain_until']} · a reading: policy/retention.yaml is unratified"
