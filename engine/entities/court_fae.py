"""CourtFae entity archetype."""
from __future__ import annotations
from typing import TYPE_CHECKING, List

from engine.entities.base import BaseEntity, WorldEvent
from engine.investigation.evidence import Evidence
from engine.investigation.instrumentation import Instrumentation

if TYPE_CHECKING:
    from engine.world.state import WorldState


class CourtFae(BaseEntity):
    """CourtFae: preys on ambiguity, generates obsession, social debt, drift.

    Leaves traces: glamour_residue, debt_marker.
    """

    def act(self, world_state: "WorldState") -> List[WorldEvent]:
        events: List[WorldEvent] = []
        loc = world_state.locations.get(self.location)
        if loc is None:
            return events

        glamour = Evidence(
            id=f"glamour_residue_{self.name}_{self.location}",
            type="residue",
            description_tags=["glamour_residue", "obsession_seed", "social_drift"],
            instrumentation_used=Instrumentation.SPECTRAL_RESIDUE,
        )
        self.traces.append(glamour)
        if glamour.id not in loc.evidence_present:
            loc.evidence_present.append(glamour.id)
        world_state.evidence_store[glamour.id] = glamour.to_dict()

        debt = Evidence(
            id=f"debt_marker_{self.name}_{self.location}",
            type="social_marker",
            description_tags=["debt_marker", "obligation_imposed", "fae_contract"],
            instrumentation_used=None,
        )
        self.traces.append(debt)
        if debt.id not in loc.evidence_present:
            loc.evidence_present.append(debt.id)
        world_state.evidence_store[debt.id] = debt.to_dict()

        for player in world_state.players.values():
            if player.location == self.location:
                if player.clarity_score < 5.0:
                    player.cost_pools["social"] = (
                        player.cost_pools.get("social", 0) + 2
                    )
                    player.cost_pools["psychological"] = (
                        player.cost_pools.get("psychological", 0) + 1
                    )
                    events.append(
                        WorldEvent(
                            entity_name=self.name,
                            event_type="debt_imposed",
                            description=(
                                "CourtFae exploits low clarity: "
                                "social debt and psychological drift imposed."
                            ),
                            location=self.location,
                        )
                    )
                else:
                    player.cost_pools["social"] = (
                        player.cost_pools.get("social", 0) + 1
                    )
                    events.append(
                        WorldEvent(
                            entity_name=self.name,
                            event_type="glamour_imposed",
                            description="CourtFae imposes glamour: minor social cost.",
                            location=self.location,
                        )
                    )

        events.append(
            WorldEvent(
                entity_name=self.name,
                event_type="residue_deposited",
                description=(
                    f"glamour_residue and debt_marker deposited at {self.location}"
                ),
                location=self.location,
            )
        )
        return events
