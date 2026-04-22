"""World state dataclasses — fully JSON-serializable."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List

from engine.consequence.clocks import Clock


@dataclass
class Player:
    name: str
    location: str
    clarity_score: float = 5.0
    cost_pools: Dict[str, int] = field(default_factory=dict)
    memory: Dict[str, Any] = field(default_factory=dict)
    inventory: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "location": self.location,
            "clarity_score": self.clarity_score,
            "cost_pools": self.cost_pools,
            "memory": self.memory,
            "inventory": self.inventory,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Player":
        return cls(
            name=d["name"],
            location=d["location"],
            clarity_score=d.get("clarity_score", 5.0),
            cost_pools=d.get("cost_pools", {}),
            memory=d.get("memory", {}),
            inventory=d.get("inventory", []),
        )


@dataclass
class Location:
    name: str
    description_tags: List[str] = field(default_factory=list)
    connections: List[str] = field(default_factory=list)
    entities_present: List[str] = field(default_factory=list)
    evidence_present: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description_tags": self.description_tags,
            "connections": self.connections,
            "entities_present": self.entities_present,
            "evidence_present": self.evidence_present,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Location":
        return cls(
            name=d["name"],
            description_tags=d.get("description_tags", []),
            connections=d.get("connections", []),
            entities_present=d.get("entities_present", []),
            evidence_present=d.get("evidence_present", []),
        )


@dataclass
class WorldState:
    world_id: str
    players: Dict[str, Player] = field(default_factory=dict)
    locations: Dict[str, Location] = field(default_factory=dict)
    clocks: Dict[str, Clock] = field(default_factory=dict)
    flags: Dict[str, Any] = field(default_factory=dict)
    entities: Dict[str, Any] = field(default_factory=dict)
    anomalies: Dict[str, Any] = field(default_factory=dict)
    evidence_store: Dict[str, Any] = field(default_factory=dict)
    hypotheses: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "world_id": self.world_id,
            "players": {k: v.to_dict() for k, v in self.players.items()},
            "locations": {k: v.to_dict() for k, v in self.locations.items()},
            "clocks": {k: v.to_dict() for k, v in self.clocks.items()},
            "flags": self.flags,
            "entities": self.entities,
            "anomalies": self.anomalies,
            "evidence_store": self.evidence_store,
            "hypotheses": self.hypotheses,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "WorldState":
        ws = cls(world_id=d["world_id"])
        ws.players = {
            k: Player.from_dict(v) for k, v in d.get("players", {}).items()
        }
        ws.locations = {
            k: Location.from_dict(v) for k, v in d.get("locations", {}).items()
        }
        ws.clocks = {
            k: Clock.from_dict(v) for k, v in d.get("clocks", {}).items()
        }
        ws.flags = d.get("flags", {})
        ws.entities = d.get("entities", {})
        ws.anomalies = d.get("anomalies", {})
        ws.evidence_store = d.get("evidence_store", {})
        ws.hypotheses = d.get("hypotheses", {})
        return ws
