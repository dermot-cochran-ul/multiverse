"""Hypothesis dataclass."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Hypothesis:
    id: str
    claim: str
    supporting_evidence: List[str] = field(default_factory=list)
    contradicting_evidence: List[str] = field(default_factory=list)
    testable_actions: List[str] = field(default_factory=list)
    associated_clock_id: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "claim": self.claim,
            "supporting_evidence": self.supporting_evidence,
            "contradicting_evidence": self.contradicting_evidence,
            "testable_actions": self.testable_actions,
            "associated_clock_id": self.associated_clock_id,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Hypothesis":
        return cls(
            id=d["id"],
            claim=d["claim"],
            supporting_evidence=d.get("supporting_evidence", []),
            contradicting_evidence=d.get("contradicting_evidence", []),
            testable_actions=d.get("testable_actions", []),
            associated_clock_id=d.get("associated_clock_id"),
        )
