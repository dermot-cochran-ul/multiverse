"""Clarity state and vulnerability modifiers."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict

from engine.consequence.costs import CostDomain


@dataclass
class ClarityState:
    """Tracks a player's clarity score (0-10)."""

    score: float = 5.0

    def __post_init__(self) -> None:
        self._clamp()

    def _clamp(self) -> None:
        self.score = max(0.0, min(10.0, self.score))

    def increase(self, amount: float) -> None:
        """Explicit player intent increases clarity."""
        self.score += amount
        self._clamp()

    def decrease(self, amount: float) -> None:
        """Vague or ambiguous intent decreases clarity."""
        self.score -= amount
        self._clamp()

    def vulnerability_modifiers(self) -> Dict[CostDomain, float]:
        """Return cost multipliers per domain based on clarity level.

        Low clarity amplifies Social and Psychological costs.
        High clarity reduces them.
        """
        if self.score >= 8.0:
            social_mod = 0.5
            psych_mod = 0.5
        elif self.score >= 5.0:
            social_mod = 1.0
            psych_mod = 1.0
        elif self.score >= 3.0:
            social_mod = 1.5
            psych_mod = 1.5
        else:
            social_mod = 2.0
            psych_mod = 2.5
        return {
            CostDomain.SOCIAL: social_mod,
            CostDomain.PSYCHOLOGICAL: psych_mod,
            CostDomain.MATERIAL: 1.0,
            CostDomain.PHYSICAL: 1.0,
            CostDomain.INFORMATIONAL: 1.0,
        }
