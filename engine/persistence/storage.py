"""JSON file-based persistence for world snapshots."""
from __future__ import annotations
import json
import os
from typing import List

from engine.world.state import Player, WorldState

SNAPSHOT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data",
    "snapshots",
)


def _ensure_dir() -> None:
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)


def save_world(world_state: WorldState) -> str:
    """Save world state to a JSON snapshot. Returns snapshot_id."""
    _ensure_dir()
    snapshot_id = world_state.world_id
    path = os.path.join(SNAPSHOT_DIR, f"{snapshot_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(world_state.to_dict(), f, indent=2)
    return snapshot_id


def load_world(snapshot_id: str) -> WorldState:
    """Load world state from a JSON snapshot."""
    _ensure_dir()
    path = os.path.join(SNAPSHOT_DIR, f"{snapshot_id}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Snapshot '{snapshot_id}' not found.")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return WorldState.from_dict(data)


def list_snapshots() -> List[str]:
    """Return a list of available snapshot IDs."""
    _ensure_dir()
    return [f[:-5] for f in os.listdir(SNAPSHOT_DIR) if f.endswith(".json")]


def reset_player(player: Player, retain_memories: List[str]) -> Player:
    """Reset player costs/clarity/location but keep specified memory keys."""
    retained = {k: player.memory[k] for k in retain_memories if k in player.memory}
    return Player(
        name=player.name,
        location=player.location,
        clarity_score=5.0,
        cost_pools={},
        memory=retained,
        inventory=[],
    )
