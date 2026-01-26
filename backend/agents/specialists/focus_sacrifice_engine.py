"""
Focus & Sacrifice Engine
Helps users make strategic tradeoffs in positioning via real AI inference
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from backend.agents.config import ModelTier

from ..base import BaseAgent
from ..state import AgentState

logger = logging.getLogger(__name__)


class FocusCategory(Enum):
    """Categories for focus decisions"""

    AUDIENCE = "audience"
    FEATURE = "feature"
    MARKET = "market"
    VALUE = "value"
    CHANNEL = "channel"


class SacrificeImpact(Enum):
    """Impact level of sacrifice"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class FocusItem:
    """An item to focus on"""

    id: str
    category: FocusCategory
    description: str
    rationale: str
    impact_score: float
    confidence: float
    dependencies: List[str] = field(default_factory=list)

    def to_dict(self):
        d = asdict(self)
        d["category"] = self.category.value
        return d


@dataclass
class SacrificeItem:
    """An item to sacrifice/deprioritize"""

    id: str
    category: FocusCategory
    description: str
    rationale: str
    impact: SacrificeImpact
    alternative_message: str
    recovery_path: str
    confidence: float

    def to_dict(self):
        d = asdict(self)
        d["category"] = self.category.value
        d["impact"] = self.impact.value
        return d


@dataclass
class TradeoffPair:
    """A focus-sacrifice pair"""

    id: str
    focus: FocusItem
    sacrifice: SacrificeItem
    net_benefit: str
    risk_assessment: str
    confidence: float

    def to_dict(self):
        return {
            "id": self.id,
            "focus": self.focus.to_dict(),
            "sacrifice": self.sacrifice.to_dict(),
            "net_benefit": self.net_benefit,
            "risk_assessment": self.risk_assessment,
            "confidence": self.confidence,
        }


@dataclass
class FocusSacrificeResult:
    """Complete focus/sacrifice analysis"""

    focus_items: List[FocusItem]
    sacrifice_items: List[SacrificeItem]
    tradeoff_pairs: List[TradeoffPair]
    positioning_statement: str
    lightbulb_insights: List[Dict[str, str]]
    recommendations: List[str]
    constraint_summary: str

    def to_dict(self):
        return {
            "focus_items": [i.to_dict() for i in self.focus_items],
            "sacrifice_items": [i.to_dict() for i in self.sacrifice_items],
            "tradeoff_pairs": [p.to_dict() for p in self.tradeoff_pairs],
            "positioning_statement": self.positioning_statement,
            "lightbulb_insights": self.lightbulb_insights,
            "recommendations": self.recommendations,
            "constraint_summary": self.constraint_summary,
        }


class FocusSacrificeEngine(BaseAgent):
    """Engine for strategic focus and sacrifice decisions using real inference."""

    def __init__(self):
        super().__init__(
            name="FocusSacrificeEngine",
            description="Recommends strategic focus and sacrifice tradeoffs via real AI inference",
            model_tier=ModelTier.FLASH,
            tools=["database"],
            skills=[
                "strategic_tradeoffs",
                "positioning_strategy",
                "resource_allocation",
            ],
        )
        self.counter = 0

    def get_system_prompt(self) -> str:
        return """You are the FocusSacrificeEngine.
        Your goal is to force strategic clarity by defining what the business will NOT do.
        For every 'Focus' item, there must be a corresponding 'Sacrifice' item.
        Be ruthless. Strategy is the art of sacrifice."""

    def _generate_id(self, prefix: str) -> str:
        """Generate unique ID"""
        self.counter += 1
        return f"{prefix}-{self.counter:03d}"

    async def execute(self, state: Any) -> Dict[str, Any]:
        """Execute focus/sacrifice analysis using real AI inference."""
        company_info = state.get("business_context", {}).get("identity", {})
        positioning = state.get("positioning", {})

        prompt = f"""Generate a strategic Focus & Sacrifice report.

COMPANY INFO:
{json.dumps(company_info, indent=2)}

POSITIONING:
{json.dumps(positioning, indent=2)}

Return a JSON object:
{{
  "pairs": [
    {{
      "focus": {{ "category": "audience/feature/etc", "description": "...", "rationale": "...", "impact": 0.9 }},
      "sacrifice": {{ "category": "...", "description": "...", "rationale": "...", "impact": "high/medium/low", "alternative_message": "...", "recovery_path": "..." }},
      "net_benefit": "...",
      "risk_assessment": "..."
    }}
  ],
  "lightbulb_insights": [{{ "title": "...", "insight": "..." }}],
  "recommendations": ["..."],
  "summary": "..."
}}"""

        res = await self._call_llm(prompt)
        try:
            clean_res = res.strip().replace("```json", "").replace("```", "")
            raw_data = json.loads(clean_res)

            focus_items = []
            sacrifice_items = []
            tradeoff_pairs = []

            for p in raw_data.get("pairs", []):
                f = FocusItem(
                    id=self._generate_id("FOC"),
                    category=FocusCategory(p["focus"]["category"].lower()),
                    description=p["focus"]["description"],
                    rationale=p["focus"]["rationale"],
                    impact_score=p["focus"].get("impact", 0.8),
                    confidence=0.9,
                )
                s = SacrificeItem(
                    id=self._generate_id("SAC"),
                    category=FocusCategory(p["sacrifice"]["category"].lower()),
                    description=p["sacrifice"]["description"],
                    rationale=p["sacrifice"]["rationale"],
                    impact=SacrificeImpact(p["sacrifice"]["impact"].lower()),
                    alternative_message=p["sacrifice"]["alternative_message"],
                    recovery_path=p["sacrifice"]["recovery_path"],
                    confidence=0.9,
                )
                pair = TradeoffPair(
                    id=self._generate_id("TRD"),
                    focus=f,
                    sacrifice=s,
                    net_benefit=p["net_benefit"],
                    risk_assessment=p["risk_assessment"],
                    confidence=0.9,
                )
                focus_items.append(f)
                sacrifice_items.append(s)
                tradeoff_pairs.append(pair)

            result = FocusSacrificeResult(
                focus_items=focus_items,
                sacrifice_items=sacrifice_items,
                tradeoff_pairs=tradeoff_pairs,
                positioning_statement=raw_data.get("summary", ""),
                lightbulb_insights=raw_data.get("lightbulb_insights", []),
                recommendations=raw_data.get("recommendations", []),
                constraint_summary=raw_data.get("summary", ""),
            )
            return {"output": result.to_dict()}
        except:
            return {"output": {"error": "Failed to parse AI focus/sacrifice output"}}
