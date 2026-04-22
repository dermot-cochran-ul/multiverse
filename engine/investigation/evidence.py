"""Evidence dataclass."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional

from engine.investigation.instrumentation import Instrumentation


@dataclass
class Evidence:
    id: str
    type: str  # sensor_log, residue, testimony, etc.
    description_tags: List[str] = field(default_factory=list)
    instrumentation_used: Optional[Instrumentation] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type,
            "description_tags": self.description_tags,
            "instrumentation_used": (
                self.instrumentation_used.value
                if self.instrumentation_used
                else None
            ),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Evidence":
        instr = None
        if d.get("instrumentation_used"):
            instr = Instrumentation(d["instrumentation_used"])
        return cls(
            id=d["id"],
            type=d["type"],
            description_tags=d.get("description_tags", []),
            instrumentation_used=instr,
        )
