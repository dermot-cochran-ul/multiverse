"""GildedSaint entity archetype."""
from __future__ import annotations
from typing import TYPE_CHECKING, List

from engine.entities.base import BaseEntity, WorldEvent
from engine.investigation.evidence import Evidence
from engine.investigation.instrumentation import Instrumentation

if TYPE_CHECKING:
    from engine.world.state import WorldState


class GildedSaint(BaseEntity):
    """GildedSaint: extracts virtue via institutional pressure, penance loops.

    Leaves traces: penance_residue, virtue_ledger_entry.
    """

    def act(self, world_state: "WorldState") -> List[WorldEvent]:
        events: List[WorldEvent] = []
        loc = world_state.locations.get(self.location)
        if loc is None:
            return events

        penance = Evidence(
            id=f"penance_residue_{self.name}_{self.location}",
            type="residue",
            description_tags=[
                "penance_residue",
                "institutional_pressure",
                "virtue_drain",
            ],
            instrumentation_used=Instrumentation.GRAVITATIONAL_FLUX,
        )
        self.traces.append(penance)
        if penance.id not in loc.evidence_present:
            loc.evidence_present.append(penance.id)
        world_state.evidence_store[penance.id] = penance.to_dict()

        ledger = Evidence(
            id=f"virtue_ledger_{self.name}_{self.location}",
            type="institutional_record",
            description_tags=[
                "virtue_ledger_entry",
                "penance_loop",
                "debt_recorded",
            ],
            instrumentation_used=None,
        )
        self.traces.append(ledger)
        if ledger.id not in loc.evidence_present:
            loc.evidence_present.append(ledger.id)
        world_state.evidence_store[ledger.id] = ledger.to_dict()

        for player in world_state.players.values():
            if player.location == self.location:
                multiplier = 2 if player.clarity_score < 5.0 else 1
                player.cost_pools["psychological"] = (
                    player.cost_pools.get("psychological", 0) + multiplier
                )
                player.cost_pools["social"] = (
                    player.cost_pools.get("social", 0) + multiplier
                )
                events.append(
                    WorldEvent(
                        entity_name=self.name,
                        event_type="penance_imposed",
                        description="GildedSaint imposes institutional penance.",
                        location=self.location,
                    )
                )

        events.append(
            WorldEvent(
                entity_name=self.name,
                event_type="residue_deposited",
                description=(
                    f"penance_residue and virtue_ledger_entry deposited "
                    f"at {self.location}"
                ),
                location=self.location,
            )
        )
        return events
