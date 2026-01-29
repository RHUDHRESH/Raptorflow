"""
Positioning Statement Generator Agent
Creates strategic positioning statements and frameworks via real AI inference
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from ..config import ModelTier

from ..base import BaseAgent
from ..state import AgentState

logger = logging.getLogger(__name__)


class PositioningFramework(Enum):
    """Positioning framework types"""

    CLASSIC = "classic"
    CHALLENGER = "challenger"
    CATEGORY_CREATOR = "category_creator"
    BENEFIT_FOCUSED = "benefit_focused"
    COMPARISON = "comparison"


class StatementType(Enum):
    """Types of positioning statements"""

    FULL = "full"
    ELEVATOR = "elevator"
    TAGLINE = "tagline"
    VALUE_PROP = "value_prop"
    CATEGORY = "category"


@dataclass
class PositioningStatement:
    """A positioning statement"""

    id: str
    type: StatementType
    framework: PositioningFramework
    statement: str
    audience: str
    key_elements: Dict[str, str]
    score: float = 0.0
    notes: str = ""

    def to_dict(self):
        d = asdict(self)
        d["type"] = self.type.value
        d["framework"] = self.framework.value
        return d


@dataclass
class PositioningMatrix:
    """Positioning comparison matrix"""

    axes: List[str]
    your_position: Dict[str, float]
    competitor_positions: Dict[str, Dict[str, float]]
    white_space: str

    def to_dict(self):
        return asdict(self)


@dataclass
class PositioningResult:
    """Complete positioning result"""

    statements: List[PositioningStatement]
    primary_statement: PositioningStatement
    matrix: Optional[PositioningMatrix]
    only_we_claims: List[str]
    recommendations: List[str]
    summary: str

    def to_dict(self):
        return {
            "statements": [s.to_dict() for s in self.statements],
            "primary_statement": (
                self.primary_statement.to_dict() if self.primary_statement else None
            ),
            "matrix": self.matrix.to_dict() if self.matrix else None,
            "only_we_claims": self.only_we_claims,
            "recommendations": self.recommendations,
            "summary": self.summary,
        }


class PositioningStatementGenerator(BaseAgent):
    """AI-powered positioning statement generator using real inference."""

    def __init__(self):
        super().__init__(
            name="PositioningStatementGenerator",
            description="Generates strategic positioning statements and frameworks via real AI inference",
            model_tier=ModelTier.FLASH,
            tools=["database"],
            skills=["brand_positioning", "copywriting", "strategic_messaging"],
        )
        self.statement_counter = 0

    def get_system_prompt(self) -> str:
        return """You are the PositioningStatementGenerator.
        Your goal is to synthesize all research, truths, and strategic decisions into definitive positioning statements.
        Generate statements across multiple frameworks (Classic, Challenger, Category Creator, etc.).
        Be definitive. Be bold. Use 'Editorial Restraint'."""

    def _generate_statement_id(self) -> str:
        self.statement_counter += 1
        return f"POS-{self.statement_counter:03d}"

    async def execute(self, state: Any) -> Dict[str, Any]:
        """Execute positioning generation using real AI inference."""
        company_info = state.get("business_context", {}).get("identity", {})
        step_data = state.get("step_data", {})

        prompt = f"""Synthesize a definitive positioning strategy.

COMPANY INFO:
{json.dumps(company_info, indent=2)}

RESEARCH DATA:
{json.dumps(step_data, indent=2)}

Return a JSON object:
{{
  "statements": [
    {{
      "framework": "classic/challenger/etc",
      "type": "full/elevator/tagline",
      "statement": "...",
      "audience": "...",
      "key_elements": {{ "target": "...", "benefit": "...", "differentiator": "..." }},
      "score": 0.0-1.0
    }}
  ],
  "only_we_claims": ["..."],
  "matrix": {{
    "axes": ["...", "..."],
    "your_position": {{ "axis1": 8, "axis2": 9 }},
    "competitor_positions": {{ "Comp A": {{ "axis1": 5, "axis2": 4 }} }},
    "white_space": "..."
  }},
  "recommendations": ["..."],
  "summary": "..."
}}"""

        res = await self._call_llm(prompt)
        try:
            clean_res = res.strip().replace("```json", "").replace("```", "")
            raw_data = json.loads(clean_res)

            statements = [
                PositioningStatement(
                    id=self._generate_statement_id(),
                    type=StatementType(
                        s["type"].lower()
                        if s["type"].lower() in [t.value for t in StatementType]
                        else "full"
                    ),
                    framework=PositioningFramework(
                        s["framework"].lower()
                        if s["framework"].lower()
                        in [f.value for f in PositioningFramework]
                        else "classic"
                    ),
                    statement=s["statement"],
                    audience=s["audience"],
                    key_elements=s["key_elements"],
                    score=s.get("score", 0.0),
                )
                for s in raw_data.get("statements", [])
            ]

            primary = statements[0] if statements else None
            matrix_data = raw_data.get("matrix")
            matrix = PositioningMatrix(**matrix_data) if matrix_data else None

            result = PositioningResult(
                statements=statements,
                primary_statement=primary,
                matrix=matrix,
                only_we_claims=raw_data.get("only_we_claims", []),
                recommendations=raw_data.get("recommendations", []),
                summary=raw_data.get("summary", ""),
            )
            return {"output": result.to_dict()}
        except:
            return {"output": {"error": "Failed to parse AI positioning output"}}
