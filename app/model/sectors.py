"""The operator's sectors, mapped onto registry selector types and entity types.

The sectors follow the categories the operator named for the social web on
2026-10-01 (docs/PLAINSIGHT-design.md amendment 9.12). Each sector is a closed token, which
the node table stores and case_rollup counts by. The word printed for a sector
is LABELS[token]. The word "shell" is never printed: an Org reached through a
CONTROLS proposal reads "org · CONTROLS proposed" in the view, because calling
it a shell would be a judgment the system invented.

ManualTask is an entity type the registry declares and no sector names. It is a
method a human performs, never promoted by an analyst, so it maps to no sector
and its node carries a null sector.
"""

from __future__ import annotations

SECTORS: dict[str, tuple[str, ...]] = {
    "accounts": ("Account", "Channel", "platform_uid", "handle", "username_string", "channel"),
    "names_aliases": ("person_name", "person_name_alias"),
    "emails": ("email", "email_hint_recovery_masked", "email_generated_permutation"),
    "phones": ("phone", "phone_hint_recovery_masked"),
    "addresses": ("postal_address",),
    "organizations": ("Org", "org_name", "org_registration_number", "public_record_id"),
    "people": ("PersonCandidate",),
    "other_osint": ("domain", "image_phash", "geo_area", "time_window", "Place", "Media"),
}

LABELS = {
    "accounts": "ACCOUNTS",
    "names_aliases": "NAMES AND ALIASES",
    "emails": "EMAILS",
    "phones": "PHONES",
    "addresses": "ADDRESSES",
    "organizations": "ORGANIZATIONS",
    "people": "PEOPLE",
    "other_osint": "OTHER OSINT",
}

#: Node kinds with no selector or entity type of their own, and their sector.
#: A referenced-only entity and an excluded candidate are people the case names
#: without an observation; a cluster is a container and sits in no sector.
KIND_SECTOR = {"referenced": "people", "candidate": "people", "cluster": None}


def sector_of(name: str | None) -> str | None:
    """The sector token for a selector type or an entity type, or None."""
    if name is None:
        return None
    for token, members in SECTORS.items():
        if name in members:
            return token
    return None


def unplaced(selector_keys, table: dict[str, tuple[str, ...]] | None = None) -> dict[str, int]:
    """Selector keys that land in zero sectors or in more than one, with the count."""
    table = SECTORS if table is None else table
    out = {}
    for key in selector_keys:
        n = sum(1 for members in table.values() if key in members)
        if n != 1:
            out[key] = n
    return out
