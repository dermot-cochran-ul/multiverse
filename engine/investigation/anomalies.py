"""Anomaly dataclass."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List


@dataclass
class Anomaly:
    id: str
    name: str
    description_tags: List[str] = field(default_factory=list)
    evidence_ids: List[str] = field(default_factory=list)
    hypothesis_ids: List[str] = field(default_factory=list)
    resolved: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description_tags": self.description_tags,
            "evidence_ids": self.evidence_ids,
            "hypothesis_ids": self.hypothesis_ids,
            "resolved": self.resolved,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Anomaly":
        return cls(
            id=d["id"],
            name=d["name"],
            description_tags=d.get("description_tags", []),
            evidence_ids=d.get("evidence_ids", []),
            hypothesis_ids=d.get("hypothesis_ids", []),
            resolved=d.get("resolved", False),
        )
