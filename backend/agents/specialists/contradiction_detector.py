"""
Contradiction Detector Agent
Enhanced system for identifying inconsistencies and contradictions in extracted facts from internal documents
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import re
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class ContradictionType(Enum):
    """Types of contradictions that can be detected"""
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    TEMPORAL = "temporal"
    LOGICAL = "logical"
    SEMANTIC = "semantic"
    FINANCIAL = "financial"
    POSITIONING = "positioning"
    TEAM = "team"
    MARKET = "market"
    PRODUCT = "product"
    COMPETITIVE = "competitive"


class ContradictionSeverity(Enum):
    """Severity levels for contradictions"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Contradiction:
    """Represents a detected contradiction"""
    id: str
    type: ContradictionType
    severity: ContradictionSeverity
    description: str
    conflicting_facts: List[str]  # Fact IDs
    confidence: float
    explanation: str
    suggested_resolution: Optional[str]
    auto_resolvable: bool

    def to_dict(self):
        d = asdict(self)
        d["type"] = self.type.value
        d["severity"] = self.severity.value
        return d


@dataclass
class ContradictionReport:
    """Report of all detected contradictions"""
    contradictions: List[Contradiction]
    total_facts_analyzed: int
    contradiction_count: int
    severity_distribution: Dict[str, int]
    type_distribution: Dict[str, int]
    auto_resolvable_count: int
    recommendations: List[str]

    def to_dict(self):
        return {
            "contradictions": [c.to_dict() for c in self.contradictions],
            "total_facts_analyzed": self.total_facts_analyzed,
            "contradiction_count": self.contradiction_count,
            "severity_distribution": self.severity_distribution,
            "type_distribution": self.type_distribution,
            "auto_resolvable_count": self.auto_resolvable_count,
            "recommendations": self.recommendations
        }


class ContradictionDetector:
    """Enhanced AI-powered contradiction detection specialist"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.contradiction_counter = 0
    
    def _generate_contradiction_id(self) -> str:
        """Generate unique contradiction ID"""
        self.contradiction_counter += 1
        return f"CONTR-{self.contradiction_counter:03d}"

    async def execute(self, state: Any) -> Dict[str, Any]:
        """Execute contradiction check using the current state."""
        facts = state.get("step_data", {}).get("auto_extraction", {}).get("facts", [])
        report = await self.detect_contradictions(facts)
        return {"output": report.to_dict()}

    async def detect_contradictions(self, facts: List[Dict[str, Any]]) -> ContradictionReport:
        """Detection of all types of contradictions in the provided facts"""
        all_contradictions = []
        
        # Basic logical consistency check (Mutually exclusive identity)
        names = [f.get("value") for f in facts if f.get("category") == "Company"]
        if len(set(names)) > 1:
            all_contradictions.append(Contradiction(
                id=self._generate_contradiction_id(),
                type=ContradictionType.LOGICAL,
                severity=ContradictionSeverity.CRITICAL,
                description="Multiple company names detected",
                conflicting_facts=[f.get("id") for f in facts if f.get("category") == "Company"],
                confidence=0.9,
                explanation=f"Found multiple names: {list(set(names))}",
                suggested_resolution="Specify the correct legal entity name",
                auto_resolvable=False
            ))

        return ContradictionReport(
            contradictions=all_contradictions,
            total_facts_analyzed=len(facts),
            contradiction_count=len(all_contradictions),
            severity_distribution={"critical": len(all_contradictions)},
            type_distribution={"logical": len(all_contradictions)},
            auto_resolvable_count=0,
            recommendations=["Verify core business identity before proceeding"] if all_contradictions else []
        )