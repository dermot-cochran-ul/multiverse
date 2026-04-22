"""Cost domains and application to player state."""
from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from engine.world.state import Player


class CostDomain(str, Enum):
    MATERIAL = "material"
    PHYSICAL = "physical"
    INFORMATIONAL = "informational"
    PSYCHOLOGICAL = "psychological"
    SOCIAL = "social"


def apply_costs(player: "Player", costs: Dict[CostDomain, int]) -> None:
    """Apply a cost dict to a player's cost pools (mutates in place)."""
    for domain, amount in costs.items():
        key = domain.value if isinstance(domain, CostDomain) else str(domain)
        player.cost_pools[key] = player.cost_pools.get(key, 0) + amount
