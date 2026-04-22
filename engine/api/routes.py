"""FastAPI routes for the interactive fiction engine — stateless JSON API."""
from __future__ import annotations
import uuid
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from engine.consequence.resolution import Effect, Position, resolve
from engine.narrative.scene_builder import build_scene
from engine.persistence.storage import load_world, reset_player, save_world
from engine.world.state import WorldState

app = FastAPI(title="Multiverse Engine API", version="0.1.0")


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------


class ActionRequest(BaseModel):
    world_state_id: str
    player_name: str
    action: str
    position: str = "risky"
    effect: str = "standard"
    justification: str = ""
    clock_id: Optional[str] = None
    costs: Dict[str, int] = {}


class ActionResponse(BaseModel):
    world_state_id: str
    scene: Dict[str, Any]


class NewWorldRequest(BaseModel):
    world_id: Optional[str] = None


class ResetRequest(BaseModel):
    player_name: str
    retain_memories: List[str] = []


class HypothesisRequest(BaseModel):
    anomaly_id: str
    hypothesis_id: str
    claim: str
    testable_action: Optional[str] = None
    clock_id: Optional[str] = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.post("/action", response_model=ActionResponse)
def take_action(req: ActionRequest) -> ActionResponse:
    """Take an action in the world. Stateless: loads and saves world by ID."""
    try:
        world = load_world(req.world_state_id)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"World '{req.world_state_id}' not found."
        )

    player = world.players.get(req.player_name)
    if player is None:
        raise HTTPException(
            status_code=404, detail=f"Player '{req.player_name}' not found."
        )

    try:
        pos = Position(req.position)
        eff = Effect(req.effect)
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid position or effect value."
        )

    outcome = resolve(pos, eff)

    if req.clock_id and req.clock_id in world.clocks:
        clock = world.clocks[req.clock_id]
        justification = req.justification or f"Action: {req.action}"
        filled = clock.advance(outcome.clock_segments_advanced, justification)
        if (
            filled
            and clock.linked_clock_name
            and clock.linked_clock_name in world.clocks
        ):
            linked = world.clocks[clock.linked_clock_name]
            linked.advance(1, f"Linked clock fill from {clock.name}")

    for domain, amount in req.costs.items():
        player.cost_pools[domain] = player.cost_pools.get(domain, 0) + int(
            amount * outcome.cost_multiplier
        )

    save_world(world)
    scene_output = build_scene(world, req.player_name)
    return ActionResponse(
        world_state_id=req.world_state_id, scene=scene_output.to_dict()
    )


@app.get("/world/{world_state_id}")
def get_world(world_state_id: str) -> Dict[str, Any]:
    """Return the current world state."""
    try:
        world = load_world(world_state_id)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"World '{world_state_id}' not found."
        )
    return world.to_dict()


@app.post("/world")
def create_world(req: NewWorldRequest) -> Dict[str, str]:
    """Create a new empty world. Returns world_state_id."""
    world_id = req.world_id or str(uuid.uuid4())
    world = WorldState(world_id=world_id)
    save_world(world)
    return {"world_state_id": world_id}


@app.post("/world/{world_state_id}/reset")
def reset_world_player(
    world_state_id: str, req: ResetRequest
) -> Dict[str, Any]:
    """Reset a player with memory retention options."""
    try:
        world = load_world(world_state_id)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"World '{world_state_id}' not found."
        )

    player = world.players.get(req.player_name)
    if player is None:
        raise HTTPException(
            status_code=404, detail=f"Player '{req.player_name}' not found."
        )

    world.players[req.player_name] = reset_player(player, req.retain_memories)
    save_world(world)
    return {
        "world_state_id": world_state_id,
        "player": world.players[req.player_name].to_dict(),
    }


@app.get("/anomalies/{world_state_id}")
def list_anomalies(world_state_id: str) -> Dict[str, Any]:
    """List active anomalies in the world."""
    try:
        world = load_world(world_state_id)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"World '{world_state_id}' not found."
        )
    active = {k: v for k, v in world.anomalies.items() if not v.get("resolved", False)}
    return {"world_state_id": world_state_id, "anomalies": active}


@app.post("/hypothesis/{world_state_id}")
def submit_hypothesis(
    world_state_id: str, req: HypothesisRequest
) -> Dict[str, Any]:
    """Submit or test a hypothesis for an anomaly."""
    try:
        world = load_world(world_state_id)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"World '{world_state_id}' not found."
        )

    anomaly = world.anomalies.get(req.anomaly_id)
    if anomaly is None:
        raise HTTPException(
            status_code=404, detail=f"Anomaly '{req.anomaly_id}' not found."
        )

    hyp_data: Dict[str, Any] = {
        "id": req.hypothesis_id,
        "claim": req.claim,
        "testable_actions": [req.testable_action] if req.testable_action else [],
        "supporting_evidence": [],
        "contradicting_evidence": [],
        "associated_clock_id": req.clock_id,
    }
    world.hypotheses[req.hypothesis_id] = hyp_data
    if req.hypothesis_id not in anomaly.get("hypothesis_ids", []):
        anomaly.setdefault("hypothesis_ids", []).append(req.hypothesis_id)

    save_world(world)
    return {"world_state_id": world_state_id, "hypothesis": hyp_data}
