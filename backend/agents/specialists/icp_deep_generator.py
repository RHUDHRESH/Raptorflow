"""
ICP Deep Generator Agent
Creates comprehensive Ideal Customer Profile via real AI inference
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from ..config import ModelTier

from ..base import BaseAgent
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
            "summary": self.summary,
        }


class ICPDeepGenerator(BaseAgent):
    """AI-powered comprehensive ICP generator using real inference."""

    def __init__(self):
        super().__init__(
            name="ICPDeepGenerator",
            description="Generates deep ICP profiles via real AI inference",
            model_tier=ModelTier.FLASH,
            tools=["database"],
            skills=[
                "customer_profiling",
                "market_segmentation",
                "buyer_persona_development",
            ],
        )
        self.icp_counter = 0
        self.pain_counter = 0
        self.trigger_counter = 0
        self.disq_counter = 0

    def get_system_prompt(self) -> str:
        return """You are the ICPDeepGenerator.
        Your goal is to define the Ideal Customer Profile (ICP) across 3 tiers (Primary, Secondary, Tertiary).
        For each tier, define Firmographics, Psychographics, Pain Points, and Buying Triggers.
        Be specific. Avoid generic labels. Use behavioral science markers."""

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

    async def execute(self, state: Any) -> Dict[str, Any]:
        """Execute ICP generation using real AI inference."""
        company_info = state.get("business_context", {}).get("identity", {})
        positioning = state.get("positioning", {})

        prompt = f"""Generate a 3-tier ICP report.

COMPANY INFO:
{json.dumps(company_info, indent=2)}

POSITIONING:
{json.dumps(positioning, indent=2)}

Return a JSON object:
{{
  "profiles": [
    {{
      "tier": "primary/secondary/tertiary",
      "name": "...",
      "description": "...",
      "firmographics": {{ "company_size": "...", "industry": "...", "stage": "startup/growth/scale/enterprise/mature" }},
      "psychographics": {{ "motivations": ["..."], "fears": ["..."], "values": ["..."], "decision_style": "...", "risk_tolerance": "..." }},
      "pain_points": [{{ "description": "...", "severity": "high/medium/low" }}],
      "trigger_events": [{{ "event": "...", "urgency": "high/medium/low" }}],
      "disqualifiers": [{{ "criterion": "...", "reason": "...", "is_hard": true }}],
      "buyer_types": ["economic", "technical", "user"],
      "key_messages": ["..."],
      "estimated_deal_size": "...",
      "sales_cycle_length": "..."
    }}
  ],
  "recommendations": ["..."],
  "summary": "..."
}}"""

        res = await self._call_llm(prompt)
        try:
            clean_res = res.strip().replace("```json", "").replace("```", "")
            raw_data = json.loads(clean_res)

            profiles = []
            for p in raw_data.get("profiles", []):
                profile = ICPProfile(
                    id=self._generate_icp_id(),
                    name=p["name"],
                    tier=ICPTier(p["tier"].lower()),
                    description=p["description"],
                    firmographics=Firmographics(
                        company_size=p["firmographics"]["company_size"],
                        revenue_range="TBD",
                        industry=p["firmographics"]["industry"],
                        stage=CompanyStage(p["firmographics"]["stage"].lower()),
                    ),
                    psychographics=Psychographics(
                        motivations=p["psychographics"]["motivations"],
                        fears=p["psychographics"]["fears"],
                        values=p["psychographics"]["values"],
                        decision_style=p["psychographics"]["decision_style"],
                        risk_tolerance=p["psychographics"]["risk_tolerance"],
                        information_sources=[],
                        preferred_communication="TBD",
                    ),
                    pain_points=[
                        PainPoint(
                            id=self._generate_pain_id(),
                            description=pp["description"],
                            severity=pp["severity"],
                            frequency="TBD",
                        )
                        for pp in p.get("pain_points", [])
                    ],
                    trigger_events=[
                        TriggerEvent(
                            id=self._generate_trigger_id(),
                            event=te["event"],
                            timing="TBD",
                            urgency_level=te["urgency"],
                            signals=[],
                        )
                        for te in p.get("trigger_events", [])
                    ],
                    disqualifiers=[
                        Disqualifier(
                            id=self._generate_disq_id(),
                            criterion=dq["criterion"],
                            reason=dq["reason"],
                            is_hard=dq["is_hard"],
                        )
                        for dq in p.get("disqualifiers", [])
                    ],
                    buyer_types=[
                        BuyerType(bt.lower()) for bt in p.get("buyer_types", [])
                    ],
                    key_stakeholders=[],
                    key_messages=p.get("key_messages", []),
                    objections=[],
                    estimated_deal_size=p.get("estimated_deal_size", ""),
                    sales_cycle_length=p.get("sales_cycle_length", ""),
                    win_rate_estimate="TBD",
                )
                profiles.append(profile)

            result = ICPGenerationResult(
                profiles=profiles,
                primary_icp=profiles[0] if profiles else None,
                recommendations=raw_data.get("recommendations", []),
                summary=raw_data.get("summary", ""),
            )
            return {"output": result.to_dict()}
        except:
            return {"output": {"error": "Failed to parse AI ICP output"}}
