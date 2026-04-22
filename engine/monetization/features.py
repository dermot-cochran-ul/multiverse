"""Feature flags and service tiers (stubs — no pay-to-win)."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class ServiceTier(str, Enum):
    FREE = "free"
    PATRON = "patron"
    WORLDBUILDER = "worldbuilder"


@dataclass
class FeatureFlags:
    extended_persistence: bool = False
    custom_creatures: bool = False
    extra_snapshots: bool = False
    reset_summaries: bool = False


_TIER_FLAGS = {
    ServiceTier.FREE: FeatureFlags(),
    ServiceTier.PATRON: FeatureFlags(
        extended_persistence=True,
        extra_snapshots=True,
        reset_summaries=True,
    ),
    ServiceTier.WORLDBUILDER: FeatureFlags(
        extended_persistence=True,
        custom_creatures=True,
        extra_snapshots=True,
        reset_summaries=True,
    ),
}


def check_feature(tier: ServiceTier, flag: str) -> bool:
    """Return True if the given tier has the specified feature flag enabled."""
    flags = _TIER_FLAGS.get(tier, FeatureFlags())
    return bool(getattr(flags, flag, False))
