"""Scene builder: produces SceneOutput JSON from WorldState.

The engine NEVER generates prose. SceneOutput is the structured contract
that an LLM (or template) receives to render prose from.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List

from engine.consequence.resolution import Effect, Position

if TYPE_CHECKING:
    from engine.world.state import Player, WorldState


@dataclass
class Choice:
    description: str
    position: str
    estimated_effect: str
    costs: Dict[str, int]
    risks: List[str]

    def to_dict(self) -> dict:
        return {
            "description": self.description,
            "position": self.position,
            "estimated_effect": self.estimated_effect,
            "costs": self.costs,
            "risks": self.risks,
        }


@dataclass
class SceneOutput:
    """Structured scene data for LLM prose rendering.

    This dataclass is the LLM contract boundary: it contains only tags,
    IDs, and structured data — never prose.
    """

    scene: Dict[str, Any]
    evidence: List[Dict[str, Any]]
    working_models: List[Dict[str, Any]]
    clocks: List[Dict[str, Any]]
    choices: List[Choice]
    player_prompt: str

    def to_dict(self) -> dict:
        return {
            "scene": self.scene,
            "evidence": self.evidence,
            "working_models": self.working_models,
            "clocks": self.clocks,
            "choices": [c.to_dict() for c in self.choices],
            "player_prompt": self.player_prompt,
        }


def build_scene(world_state: "WorldState", player_name: str) -> SceneOutput:
    """Build a SceneOutput from a WorldState for a given player."""
    player = world_state.players.get(player_name)
    if player is None:
        raise ValueError(f"Player '{player_name}' not found in world state.")

    location = world_state.locations.get(player.location)
    loc_tags = location.description_tags if location else []
    entities_present = location.entities_present if location else []
    evidence_ids = location.evidence_present if location else []

    scene = {
        "location": player.location,
        "description_tags": loc_tags,
        "entities_present": entities_present,
        "ambient_conditions": world_state.flags.get("ambient_conditions", []),
    }

    evidence = []
    for eid in evidence_ids:
        ev = world_state.evidence_store.get(eid)
        if ev:
            evidence.append(ev)

    working_models = []
    for anomaly_id, anomaly_data in world_state.anomalies.items():
        if not anomaly_data.get("resolved", False):
            hypotheses = []
            for hyp_id in anomaly_data.get("hypothesis_ids", []):
                hyp = world_state.hypotheses.get(hyp_id)
                if hyp:
                    confidence = (
                        "medium"
                        if hyp.get("supporting_evidence")
                        else "low"
                    )
                    hypotheses.append(
                        {
                            "id": hyp_id,
                            "claim": hyp.get("claim", ""),
                            "confidence": confidence,
                            "associated_clock": hyp.get("associated_clock_id"),
                        }
                    )
            working_models.append(
                {
                    "anomaly_id": anomaly_id,
                    "name": anomaly_data.get("name", ""),
                    "description_tags": anomaly_data.get("description_tags", []),
                    "hypotheses": hypotheses,
                }
            )

    clocks = [clock.to_dict() for clock in world_state.clocks.values()]

    choices = _generate_choices(world_state, player, location)

    prompt_tags = [
        f"location:{player.location}",
        f"clarity:{player.clarity_score:.1f}",
    ]
    for domain, amount in player.cost_pools.items():
        if amount > 0:
            prompt_tags.append(f"cost_{domain}:{amount}")
    for anomaly_data in world_state.anomalies.values():
        if not anomaly_data.get("resolved", False):
            label = anomaly_data.get("name", "unknown")
            prompt_tags.append(f"active_anomaly:{label}")

    player_prompt = " | ".join(prompt_tags)

    return SceneOutput(
        scene=scene,
        evidence=evidence,
        working_models=working_models,
        clocks=clocks,
        choices=choices,
        player_prompt=player_prompt,
    )


def _generate_choices(
    world_state: "WorldState",
    player: "Player",
    location: Any,
) -> List[Choice]:
    """Generate 3-5 deterministic choices based on world state."""
    choices: List[Choice] = []

    choices.append(
        Choice(
            description="observe_surroundings",
            position=Position.CONTROLLED.value,
            estimated_effect=Effect.LIMITED.value,
            costs={},
            risks=["none"],
        )
    )

    if location and location.evidence_present:
        choices.append(
            Choice(
                description="investigate_evidence",
                position=Position.RISKY.value,
                estimated_effect=Effect.STANDARD.value,
                costs={"informational": 1},
                risks=["evidence_contamination", "time_cost"],
            )
        )

    has_testable = any(
        world_state.hypotheses.get(hid, {}).get("testable_actions")
        for a in world_state.anomalies.values()
        if not a.get("resolved", False)
        for hid in a.get("hypothesis_ids", [])
    )
    if has_testable:
        choices.append(
            Choice(
                description="test_hypothesis",
                position=Position.RISKY.value,
                estimated_effect=Effect.STANDARD.value,
                costs={"informational": 1, "physical": 1},
                risks=["clock_advancement", "hypothesis_invalidated"],
            )
        )

    if location and location.connections:
        choices.append(
            Choice(
                description=f"move_to_{location.connections[0]}",
                position=Position.CONTROLLED.value,
                estimated_effect=Effect.LIMITED.value,
                costs={},
                risks=["new_entity_encounter"],
            )
        )

    if player.clarity_score < 4.0:
        choices.append(
            Choice(
                description="desperate_action",
                position=Position.DESPERATE.value,
                estimated_effect=Effect.GREAT.value,
                costs={"psychological": 2, "physical": 1},
                risks=["severe_cost", "clock_spike", "clarity_loss"],
            )
        )

    while len(choices) < 3:
        choices.append(
            Choice(
                description="wait_and_observe",
                position=Position.CONTROLLED.value,
                estimated_effect=Effect.LIMITED.value,
                costs={},
                risks=["time_passes"],
            )
        )

    return choices[:5]
