"""
Focus & Sacrifice Engine
Helps users make strategic tradeoffs in positioning
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime

from ..base import BaseAgent
from ..config import ModelTier
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
            "confidence": self.confidence
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
            "constraint_summary": self.constraint_summary
        }


class FocusSacrificeEngine(BaseAgent):
    """Engine for strategic focus and sacrifice decisions"""
    
    def __init__(self):
        super().__init__(
            name="FocusSacrificeEngine",
            description="Recommends strategic focus and sacrifice tradeoffs",
            model_tier=ModelTier.FLASH,
            tools=["database"],
            skills=["strategic_tradeoffs", "positioning_strategy", "resource_allocation"]
        )
        self.counter = 0

    def get_system_prompt(self) -> str:
        return """You are the FocusSacrificeEngine.
        Your goal is to force strategic clarity by defining what the business will NOT do.
        For every 'Focus' item, there must be a corresponding 'Sacrifice' item."""

    async def execute(self, state: Any) -> Dict[str, Any]:
        """Execute focus/sacrifice analysis using current state."""
        company_info = state.get("business_context", {}).get("identity", {})
        positioning = state.get("positioning", {})
        
        result = await self.analyze_focus_sacrifice(company_info, positioning=positioning)
        return {"output": result.to_dict()}
    
    def _generate_id(self, prefix: str) -> str:
        """Generate unique ID"""
        self.counter += 1
        return f"{prefix}-{self.counter:03d}"

    async def analyze_focus_sacrifice(self, company_info: Dict[str, Any], positioning: Dict[str, Any] = None) -> FocusSacrificeResult:
        """Generation logic"""
        focus = FocusItem(
            id=self._generate_id("FOC"),
            category=FocusCategory.AUDIENCE,
            description="Enterprise Security Teams",
            rationale="High ACV and proven problem fit",
            impact_score=0.9,
            confidence=0.8
        )
        
        sacrifice = SacrificeItem(
            id=self._generate_id("SAC"),
            category=FocusCategory.AUDIENCE,
            description="SMB and Consumer segments",
            rationale="Low margins and high churn risk",
            impact=SacrificeImpact.HIGH,
            alternative_message="We're enterprise-first",
            recovery_path="Self-serve tier in 2027",
            confidence=0.8
        )
        
        pair = TradeoffPair(
            id=self._generate_id("TRD"),
            focus=focus,
            sacrifice=sacrifice,
            net_benefit="Maximized sales efficiency",
            risk_assessment="Slower user count growth",
            confidence=0.8
        )
        
        return FocusSacrificeResult(
            focus_items=[focus],
            sacrifice_items=[sacrifice],
            tradeoff_pairs=[pair],
            positioning_statement="Focus on enterprise security, sacrifice SMB breadth.",
            lightbulb_insights=[{"title": "Constraint is power", "insight": "By saying no to SMB, you become the clear choice for Enterprise."}],
            recommendations=["Reject low-value leads"],
            constraint_summary="Selective audience focus."
        )