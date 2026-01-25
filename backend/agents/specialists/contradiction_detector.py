"""
Contradiction Detector Agent
Enhanced system for identifying inconsistencies and contradictions in extracted facts via real AI inference
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from backend.agents.config import ModelTier

from ..base import BaseAgent
from ..state import AgentState

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
    conflicting_facts: List[str]
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
            "recommendations": self.recommendations,
        }


class ContradictionDetector(BaseAgent):
    """Enhanced AI-powered contradiction detection specialist using real inference."""

    def __init__(self):
        super().__init__(
            name="ContradictionDetector",
            description="Performs adversarial logic audits on extracted facts via real AI inference",
            model_tier=ModelTier.FLASH,
            tools=["database"],
            skills=["adversarial_logic", "data_consistency", "logical_inference"],
        )
        self.contradiction_counter = 0

    def get_system_prompt(self) -> str:
        return """You are the ContradictionDetector. Your job is to find logical, numerical, or strategic inconsistencies.
        Be extremely skeptical. If one document says 'Market Leader' and another says 'Early Stage', flag it.
        If numbers don't add up (e.g., total users vs segment users), flag it."""

    def _generate_contradiction_id(self) -> str:
        """Generate unique contradiction ID"""
        self.contradiction_counter += 1
        return f"CONTR-{self.contradiction_counter:03d}"

    async def execute(self, state: Any) -> Dict[str, Any]:
        """Execute contradiction check using real AI inference."""
        facts = state.get("step_data", {}).get("auto_extraction", {}).get("facts", [])

        prompt = f"""Analyze the following extracted business facts for contradictions.

FACTS:
{json.dumps(facts, indent=2)}

Return a JSON report:
{{
  "contradictions": [
    {{
      "type": "numerical/logical/positioning/etc",
      "severity": "critical/high/medium/low",
      "description": "...",
      "conflicting_facts": ["fact_id_1", "fact_id_2"],
      "explanation": "...",
      "suggested_resolution": "..."
    }}
  ],
  "recommendations": ["..."]
}}"""

        res = await self._call_llm(prompt)
        try:
            clean_res = res.strip().replace("```json", "").replace("```", "")
            raw_data = json.loads(clean_res)

            # Map back to dataclasses for consistency
            contradictions = [
                Contradiction(
                    id=self._generate_contradiction_id(),
                    type=ContradictionType(
                        c["type"].lower()
                        if c["type"].lower() in [t.value for t in ContradictionType]
                        else "logical"
                    ),
                    severity=ContradictionSeverity(
                        c["severity"].lower()
                        if c["severity"].lower()
                        in [s.value for s in ContradictionSeverity]
                        else "medium"
                    ),
                    description=c["description"],
                    conflicting_facts=c["conflicting_facts"],
                    confidence=0.9,
                    explanation=c["explanation"],
                    suggested_resolution=c.get("suggested_resolution"),
                    auto_resolvable=False,
                )
                for c in raw_data.get("contradictions", [])
            ]

            report = ContradictionReport(
                contradictions=contradictions,
                total_facts_analyzed=len(facts),
                contradiction_count=len(contradictions),
                severity_distribution={},
                type_distribution={},
                auto_resolvable_count=0,
                recommendations=raw_data.get("recommendations", []),
            )
            return {"output": report.to_dict()}
        except:
            return {"output": {"error": "Failed to parse AI contradiction audit"}}
