"""
ICP Deep Generator Agent
Creates comprehensive Ideal Customer Profile with psychographics
"""

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime

from ..base import BaseAgent
from ..config import ModelTier
from ..state import AgentState

logger = logging.getLogger(__name__)


class ICPTier(Enum):
    """ICP priority tier"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"


class BuyerType(Enum):
    """Type of buyer persona"""
    ECONOMIC = "economic"
    TECHNICAL = "technical"
    USER = "user"
    CHAMPION = "champion"
    BLOCKER = "blocker"


class CompanyStage(Enum):
    """Company lifecycle stage"""
    STARTUP = "startup"
    GROWTH = "growth"
    SCALE = "scale"
    ENTERPRISE = "enterprise"
    MATURE = "mature"


@dataclass
class Firmographics:
    """Company demographics"""
    company_size: str
    revenue_range: str
    industry: str
    sub_industry: Optional[str] = None
    geography: str = "North America"
    stage: CompanyStage = CompanyStage.GROWTH
    tech_stack: List[str] = field(default_factory=list)
    funding_stage: Optional[str] = None

    def to_dict(self):
        d = asdict(self)
        d["stage"] = self.stage.value
        return d


@dataclass
class Psychographics:
    """Psychological characteristics"""
    motivations: List[str]
    fears: List[str]
    values: List[str]
    decision_style: str
    risk_tolerance: str
    information_sources: List[str]
    preferred_communication: str

    def to_dict(self):
        return asdict(self)


@dataclass
class PainPoint:
    """A specific pain point"""
    id: str
    description: str
    severity: str
    frequency: str
    current_solution: Optional[str] = None
    cost_of_inaction: Optional[str] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class TriggerEvent:
    """Event that triggers buying"""
    id: str
    event: str
    timing: str
    urgency_level: str
    signals: List[str]

    def to_dict(self):
        return asdict(self)


@dataclass
class Disqualifier:
    """Criteria that disqualifies a prospect"""
    id: str
    criterion: str
    reason: str
    is_hard: bool

    def to_dict(self):
        return asdict(self)


@dataclass 
class ICPProfile:
    """Complete ICP profile"""
    id: str
    name: str
    tier: ICPTier
    description: str
    firmographics: Firmographics
    psychographics: Psychographics
    pain_points: List[PainPoint]
    trigger_events: List[TriggerEvent]
    disqualifiers: List[Disqualifier]
    buyer_types: List[BuyerType]
    key_stakeholders: List[str]
    key_messages: List[str]
    objections: List[str]
    estimated_deal_size: str
    sales_cycle_length: str
    win_rate_estimate: str

    def to_dict(self):
        d = asdict(self)
        d["tier"] = self.tier.value
        d["firmographics"] = self.firmographics.to_dict()
        d["psychographics"] = self.psychographics.to_dict()
        d["pain_points"] = [p.to_dict() for p in self.pain_points]
        d["trigger_events"] = [t.to_dict() for t in self.trigger_events]
        d["disqualifiers"] = [dq.to_dict() for dq in self.disqualifiers]
        d["buyer_types"] = [bt.value for bt in self.buyer_types]
        return d


@dataclass
class ICPGenerationResult:
    """Result of ICP generation"""
    profiles: List[ICPProfile]
    primary_icp: ICPProfile
    recommendations: List[str]
    summary: str

    def to_dict(self):
        return {
            "profiles": [p.to_dict() for p in self.profiles],
            "primary_icp": self.primary_icp.to_dict() if self.primary_icp else None,
            "recommendations": self.recommendations,
            "summary": self.summary
        }


class ICPDeepGenerator(BaseAgent):
    """AI-powered comprehensive ICP generator"""
    
    def __init__(self):
        super().__init__(
            name="ICPDeepGenerator",
            description="Generates deep ICP profiles with firmographics and psychographics",
            model_tier=ModelTier.FLASH,
            tools=["database"],
            skills=["customer_profiling", "market_segmentation", "buyer_persona_development"]
        )
        self.icp_counter = 0
        self.pain_counter = 0
        self.trigger_counter = 0
        self.disq_counter = 0

    def get_system_prompt(self) -> str:
        return """You are the ICPDeepGenerator.
        Your goal is to define the Ideal Customer Profile (ICP) across 3 tiers (Primary, Secondary, Tertiary).
        For each tier, define Firmographics, Psychographics, Pain Points, and Buying Triggers."""

    async def execute(self, state: Any) -> Dict[str, Any]:
        """Execute ICP generation using current state."""
        company_info = state.get("business_context", {}).get("identity", {})
        positioning = state.get("positioning", {})
        
        result = await self.generate_icp_profiles(company_info, positioning)
        return {"output": result.to_dict()}
    
    def _generate_icp_id(self) -> str:
        self.icp_counter += 1
        return f"ICP-{self.icp_counter:03d}"
    
    def _generate_pain_id(self) -> str:
        self.pain_counter += 1
        return f"PAIN-{self.pain_counter:03d}"
    
    def _generate_trigger_id(self) -> str:
        self.trigger_counter += 1
        return f"TRIG-{self.trigger_counter:03d}"
    
    def _generate_disq_id(self) -> str:
        self.disq_counter += 1
        return f"DISQ-{self.disq_counter:03d}"

    async def generate_icp_profiles(self, company_info: Dict[str, Any], positioning: Dict[str, Any]) -> ICPGenerationResult:
        """Mock generation logic for Step 15."""
        
        primary_icp = ICPProfile(
            id=self._generate_icp_id(),
            name="Enterprise Security Guard",
            tier=ICPTier.PRIMARY,
            description="High-security enterprise teams needing real-time AI defense",
            firmographics=Firmographics(
                company_size="5000+ employees",
                revenue_range="$1B+ ARR",
                industry="Finance / Critical Infrastructure",
                stage=CompanyStage.ENTERPRISE
            ),
            psychographics=Psychographics(
                motivations=["Risk mitigation", "Regulatory compliance"],
                fears=["Zero-day exploits", "Data exfiltration"],
                values=["Integrity", "Security"],
                decision_style="Data-driven",
                risk_tolerance="Low",
                information_sources=["Gartner", "Security Forums"],
                preferred_communication="Direct / Case Studies"
            ),
            pain_points=[PainPoint(id=self._generate_pain_id(), description="Alert fatigue", severity="High", frequency="Daily")],
            trigger_events=[TriggerEvent(id=self._generate_trigger_id(), event="Recent breach in sector", timing="Immediate", urgency_level="Critical", signals=["News"])],
            disqualifiers=[Disqualifier(id=self._generate_disq_id(), criterion="Legacy air-gapped system", reason="No cloud connectivity", is_hard=True)],
            buyer_types=[BuyerType.ECONOMIC, BuyerType.TECHNICAL],
            key_stakeholders=["CISO", "VP Infrastructure"],
            key_messages=["Secure your future with AI", "Eliminate zero-day gaps"],
            objections=["Too expensive", "AI is a black box"],
            estimated_deal_size="$100k-$500k",
            sales_cycle_length="6-12 months",
            win_rate_estimate="30%"
        )
        
        return ICPGenerationResult(
            profiles=[primary_icp],
            primary_icp=primary_icp,
            recommendations=["Focus on Fortune 500 Financials"],
            summary="Primary ICP profile generated."
        )