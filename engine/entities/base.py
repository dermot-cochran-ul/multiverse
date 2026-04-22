"""Base entity class."""
from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, List

from engine.investigation.evidence import Evidence

if TYPE_CHECKING:
    from engine.world.state import WorldState


@dataclass
class WorldEvent:
    """An event produced by an entity acting on the world."""

    entity_name: str
    event_type: str
    description: str
    location: str


class BaseEntity:
    """Base class for all entity archetypes."""

    def __init__(self, name: str, location: str) -> None:
        self.name = name
        self.location = location
        self.traces: List[Evidence] = []

    def act(self, world_state: "WorldState") -> List[WorldEvent]:
        """Deterministically produce events based on world state."""
        raise NotImplementedError
