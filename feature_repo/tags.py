"""Standard tag keys and helpers.

Tags are how the platform attaches governance and ops metadata to Feast objects.
Validation (``feature_platform.registry.validation``) enforces that the mandatory
keys below are present on every feature view.
"""

from __future__ import annotations

# Mandatory tag keys on every FeatureView.
OWNER = "owner"            # email of the owning engineer
TEAM = "team"              # owning team
SENSITIVITY = "sensitivity"  # public | financial | pii
TIER = "tier"              # real-time | near-real-time | batch
SLA_FRESHNESS = "sla_freshness"  # e.g. "24h"
SOURCE_CONTRACT = "source_contract"  # contract id this view depends on

MANDATORY_TAGS = (OWNER, TEAM, SENSITIVITY, TIER, SLA_FRESHNESS)

VALID_SENSITIVITY = frozenset({"public", "financial", "pii"})
VALID_TIER = frozenset({"real-time", "near-real-time", "batch"})


def standard_tags(
    *,
    owner: str,
    team: str,
    sensitivity: str = "public",
    tier: str = "batch",
    sla_freshness: str = "24h",
    source_contract: str | None = None,
) -> dict[str, str]:
    """Build a validated tag dict for a feature view."""
    if sensitivity not in VALID_SENSITIVITY:
        raise ValueError(f"sensitivity must be one of {sorted(VALID_SENSITIVITY)}")
    if tier not in VALID_TIER:
        raise ValueError(f"tier must be one of {sorted(VALID_TIER)}")
    tags = {
        OWNER: owner,
        TEAM: team,
        SENSITIVITY: sensitivity,
        TIER: tier,
        SLA_FRESHNESS: sla_freshness,
    }
    if source_contract:
        tags[SOURCE_CONTRACT] = source_contract
    return tags
