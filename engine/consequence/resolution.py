"""Deterministic position x effect resolution table — no RNG."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple


class Position(str, Enum):
    CONTROLLED = "controlled"
    RISKY = "risky"
    DESPERATE = "desperate"


class Effect(str, Enum):
    LIMITED = "limited"
    STANDARD = "standard"
    GREAT = "great"


@dataclass(frozen=True)
class OutcomeDescriptor:
    """Deterministic outcome for a (Position, Effect) combination."""

    clock_segments_advanced: int
    cost_multiplier: float
    description: str


# Pure deterministic lookup table — no RNG whatsoever
RESOLUTION_TABLE: Dict[Tuple[Position, Effect], OutcomeDescriptor] = {
    (Position.CONTROLLED, Effect.LIMITED): OutcomeDescriptor(
        1, 0.5, "Controlled action, limited effect: minor progress, reduced cost."
    ),
    (Position.CONTROLLED, Effect.STANDARD): OutcomeDescriptor(
        2, 1.0, "Controlled action, standard effect: solid progress, normal cost."
    ),
    (Position.CONTROLLED, Effect.GREAT): OutcomeDescriptor(
        3, 1.5, "Controlled action, great effect: major progress, increased cost."
    ),
    (Position.RISKY, Effect.LIMITED): OutcomeDescriptor(
        1, 1.0, "Risky action, limited effect: minor progress at normal cost."
    ),
    (Position.RISKY, Effect.STANDARD): OutcomeDescriptor(
        2, 1.5, "Risky action, standard effect: solid progress, elevated cost."
    ),
    (Position.RISKY, Effect.GREAT): OutcomeDescriptor(
        3, 2.0, "Risky action, great effect: major progress, high cost."
    ),
    (Position.DESPERATE, Effect.LIMITED): OutcomeDescriptor(
        1, 1.5, "Desperate action, limited effect: minor progress, high cost."
    ),
    (Position.DESPERATE, Effect.STANDARD): OutcomeDescriptor(
        2, 2.0, "Desperate action, standard effect: solid progress, very high cost."
    ),
    (Position.DESPERATE, Effect.GREAT): OutcomeDescriptor(
        3, 3.0, "Desperate action, great effect: major progress, critical cost."
    ),
}


def resolve(position: Position, effect: Effect) -> OutcomeDescriptor:
    """Return the deterministic outcome for the given position and effect."""
    return RESOLUTION_TABLE[(position, effect)]
