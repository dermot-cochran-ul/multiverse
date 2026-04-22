"""Clock system: named progress trackers with causal justification."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class Clock:
    """A named progress clock with segments."""

    name: str
    segments: int  # total segments (1-6)
    current: int = 0
    trigger_effect: str = ""
    linked_clock_name: Optional[str] = None  # advance this clock when filled

    def __post_init__(self) -> None:
        if not (1 <= self.segments <= 6):
            raise ValueError(f"Clock segments must be 1-6, got {self.segments}")
        if not (0 <= self.current <= self.segments):
            raise ValueError(
                f"Clock current must be 0-{self.segments}, got {self.current}"
            )

    def advance(self, amount: int, justification: str) -> bool:
        """Advance the clock by *amount* with a causal justification.

        Returns True if the clock filled (triggered).
        Raises ValueError if justification is empty or amount < 1.
        """
        if not justification or not justification.strip():
            raise ValueError("Clock advancement requires a causal justification.")
        if amount < 1:
            raise ValueError("Advancement amount must be at least 1.")
        self.current = min(self.current + amount, self.segments)
        return self.is_filled()

    def is_filled(self) -> bool:
        """Return True if the clock has reached its maximum."""
        return self.current >= self.segments

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "segments": self.segments,
            "current": self.current,
            "trigger_effect": self.trigger_effect,
            "linked_clock_name": self.linked_clock_name,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Clock":
        return cls(
            name=d["name"],
            segments=d["segments"],
            current=d.get("current", 0),
            trigger_effect=d.get("trigger_effect", ""),
            linked_clock_name=d.get("linked_clock_name"),
        )
