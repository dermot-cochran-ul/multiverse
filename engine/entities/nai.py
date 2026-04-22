"""Nai / Quiet-Built entity archetype."""
from __future__ import annotations
from typing import TYPE_CHECKING, List

from engine.entities.base import BaseEntity, WorldEvent
from engine.investigation.evidence import Evidence
from engine.investigation.instrumentation import Instrumentation

if TYPE_CHECKING:
    from engine.world.state import WorldState


class Nai(BaseEntity):
    """Nai / Quiet-Built: stabilizes clarity, suppresses ambiguity.

    Leaves trace: clarity_residue.
    """

    def act(self, world_state: "WorldState") -> List[WorldEvent]:
        events: List[WorldEvent] = []
        loc = world_state.locations.get(self.location)
        if loc is None:
            return events

        residue = Evidence(
            id=f"clarity_residue_{self.name}_{self.location}",
            type="residue",
            description_tags=[
                "clarity_residue",
                "stabilizing_field",
                "ambiguity_suppressed",
            ],
            instrumentation_used=Instrumentation.EM_HARMONICS,
        )
        self.traces.append(residue)
        if residue.id not in loc.evidence_present:
            loc.evidence_present.append(residue.id)
        world_state.evidence_store[residue.id] = residue.to_dict()

        for player in world_state.players.values():
            if player.location == self.location:
                player.clarity_score = min(10.0, player.clarity_score + 1.0)
                events.append(
                    WorldEvent(
                        entity_name=self.name,
                        event_type="clarity_increase",
                        description="Nai presence stabilizes ambient clarity.",
                        location=self.location,
                    )
                )

        events.append(
            WorldEvent(
                entity_name=self.name,
                event_type="residue_deposited",
                description=f"clarity_residue deposited at {self.location}",
                location=self.location,
            )
        )
        return events
