"""
ICP Deep Generator Agent
Creates comprehensive Ideal Customer Profile with psychographics
"""

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import random

logger = logging.getLogger(__name__)


class ICPTier(Enum):
    """ICP priority tier"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"


class BuyerType(Enum):
    """Type of buyer persona"""
    ECONOMIC = "economic"  # Controls budget
    TECHNICAL = "technical"  # Evaluates tech fit
    USER = "user"  # End user
    CHAMPION = "champion"  # Internal advocate
    BLOCKER = "blocker"  # Potential obstacle


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
    company_size: str  # e.g., "50-200 employees"
    revenue_range: str  # e.g., "$5M-$20M ARR"
    industry: str
    sub_industry: Optional[str] = None
    geography: str = "North America"
    stage: CompanyStage = CompanyStage.GROWTH
    tech_stack: List[str] = field(default_factory=list)
    funding_stage: Optional[str] = None


@dataclass
class Psychographics:
    """Psychological characteristics"""
    motivations: List[str]
    fears: List[str]
    values: List[str]
    decision_style: str  # data-driven, intuitive, consensus
    risk_tolerance: str  # low, medium, high
    information_sources: List[str]
    preferred_communication: str


@dataclass
class PainPoint:
    """A specific pain point"""
    id: str
    description: str
    severity: str  # critical, high, medium, low
    frequency: str  # daily, weekly, monthly
    current_solution: Optional[str] = None
    cost_of_inaction: Optional[str] = None


@dataclass
class TriggerEvent:
    """Event that triggers buying"""
    id: str
    event: str
    timing: str  # when this typically happens
    urgency_level: str  # high, medium, low
    signals: List[str]  # observable signals


@dataclass
class Disqualifier:
    """Criteria that disqualifies a prospect"""
    id: str
    criterion: str
    reason: str
    is_hard: bool  # hard = absolute, soft = negotiable


@dataclass 
class ICPProfile:
    """Complete ICP profile"""
    id: str
    name: str
    tier: ICPTier
    description: str
    
    # Demographics
    firmographics: Firmographics
    
    # Psychographics
    psychographics: Psychographics
    
    # Pain & triggers
    pain_points: List[PainPoint]
    trigger_events: List[TriggerEvent]
    
    # Qualification
    disqualifiers: List[Disqualifier]
    
    # Buyer personas
    buyer_types: List[BuyerType]
    key_stakeholders: List[str]
    
    # Messaging
    key_messages: List[str]
    objections: List[str]
    
    # Metrics
    estimated_deal_size: str
    sales_cycle_length: str
    win_rate_estimate: str


@dataclass
class ICPGenerationResult:
    """Result of ICP generation"""
    profiles: List[ICPProfile]
    primary_icp: ICPProfile
    recommendations: List[str]
    summary: str


class ICPDeepGenerator:
    """AI-powered comprehensive ICP generator"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.icp_counter = 0
        self.pain_counter = 0
        self.trigger_counter = 0
        self.disq_counter = 0
    
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
    
    def _generate_firmographics(self, company_info: Dict[str, Any], tier: ICPTier) -> Firmographics:
        """Generate firmographics based on tier"""
        base_industry = company_info.get("industry", "Technology")
        
        if tier == ICPTier.PRIMARY:
            return Firmographics(
                company_size="50-200 employees",
                revenue_range="$5M-$20M ARR",
                industry=base_industry,
                geography="North America",
                stage=CompanyStage.GROWTH,
                tech_stack=["Modern stack", "Cloud-native"],
                funding_stage="Series A/B"
            )
        elif tier == ICPTier.SECONDARY:
            return Firmographics(
                company_size="200-500 employees",
                revenue_range="$20M-$50M ARR",
                industry=base_industry,
                geography="North America, Europe",
                stage=CompanyStage.SCALE,
                tech_stack=["Enterprise tools", "Hybrid"],
                funding_stage="Series B/C"
            )
        else:
            return Firmographics(
                company_size="10-50 employees",
                revenue_range="$1M-$5M ARR",
                industry=base_industry,
                geography="Global",
                stage=CompanyStage.STARTUP,
                tech_stack=["Lean stack"],
                funding_stage="Seed/Pre-seed"
            )
    
    def _generate_psychographics(self, positioning: Dict[str, Any]) -> Psychographics:
        """Generate psychographic profile"""
        return Psychographics(
            motivations=[
                "Grow revenue faster",
                "Reduce operational overhead",
                "Stay ahead of competition",
                "Delight customers"
            ],
            fears=[
                "Falling behind competitors",
                "Making wrong technology bet",
                "Team resistance to change",
                "Budget constraints"
            ],
            values=[
                "Efficiency",
                "Innovation",
                "Customer success",
                "Data-driven decisions"
            ],
            decision_style="data-driven with peer validation",
            risk_tolerance="medium",
            information_sources=[
                "Industry peers",
                "G2/Capterra reviews",
                "LinkedIn thought leaders",
                "Industry publications"
            ],
            preferred_communication="Email + Demo call"
        )
    
    def _generate_pain_points(self, company_info: Dict[str, Any]) -> List[PainPoint]:
        """Generate relevant pain points"""
        core_problem = company_info.get("core_problem", "inefficiency")
        
        return [
            PainPoint(
                id=self._generate_pain_id(),
                description=f"Spending too much time on {core_problem}",
                severity="critical",
                frequency="daily",
                current_solution="Manual processes or spreadsheets",
                cost_of_inaction="$50K+ per year in lost productivity"
            ),
            PainPoint(
                id=self._generate_pain_id(),
                description="Lack of visibility into key metrics",
                severity="high",
                frequency="weekly",
                current_solution="Ad-hoc reporting",
                cost_of_inaction="Missed opportunities"
            ),
            PainPoint(
                id=self._generate_pain_id(),
                description="Difficulty scaling current processes",
                severity="high",
                frequency="monthly",
                current_solution="Hiring more people",
                cost_of_inaction="Growth bottleneck"
            ),
        ]
    
    def _generate_trigger_events(self) -> List[TriggerEvent]:
        """Generate trigger events"""
        return [
            TriggerEvent(
                id=self._generate_trigger_id(),
                event="New funding round closed",
                timing="Within 30 days of announcement",
                urgency_level="high",
                signals=["Press release", "LinkedIn update", "Crunchbase alert"]
            ),
            TriggerEvent(
                id=self._generate_trigger_id(),
                event="New leadership hire (VP+)",
                timing="First 90 days in role",
                urgency_level="high",
                signals=["LinkedIn job change", "Company announcement"]
            ),
            TriggerEvent(
                id=self._generate_trigger_id(),
                event="Competitor churned",
                timing="Within 60 days",
                urgency_level="medium",
                signals=["Review sites", "Social mentions"]
            ),
        ]
    
    def _generate_disqualifiers(self) -> List[Disqualifier]:
        """Generate disqualification criteria"""
        return [
            Disqualifier(
                id=self._generate_disq_id(),
                criterion="No budget authority",
                reason="Cannot close deals without budget holder",
                is_hard=True
            ),
            Disqualifier(
                id=self._generate_disq_id(),
                criterion="Locked into competitor contract >12 months",
                reason="Long wait time reduces urgency",
                is_hard=False
            ),
            Disqualifier(
                id=self._generate_disq_id(),
                criterion="Technical requirements don't match",
                reason="Product-market fit issue",
                is_hard=True
            ),
        ]
    
    async def generate_icp_profiles(self, company_info: Dict[str, Any], positioning: Dict[str, Any] = None, count: int = 3) -> ICPGenerationResult:
        """
        Generate comprehensive ICP profiles
        
        Args:
            company_info: Company information
            positioning: Positioning data
            count: Number of ICPs to generate (max 3)
        
        Returns:
            ICPGenerationResult with detailed profiles
        """
        positioning = positioning or {}
        count = min(count, 3)  # Enforce max 3 ICPs
        
        profiles = []
        tiers = [ICPTier.PRIMARY, ICPTier.SECONDARY, ICPTier.TERTIARY][:count]
        
        icp_names = [
            ("Growth-Stage SaaS", "Fast-moving SaaS companies ready to scale"),
            ("Enterprise Innovators", "Large companies seeking modern solutions"),
            ("Startup Pioneers", "Early-stage companies with big ambitions"),
        ]
        
        for i, tier in enumerate(tiers):
            name, description = icp_names[i]
            
            profile = ICPProfile(
                id=self._generate_icp_id(),
                name=name,
                tier=tier,
                description=description,
                firmographics=self._generate_firmographics(company_info, tier),
                psychographics=self._generate_psychographics(positioning),
                pain_points=self._generate_pain_points(company_info),
                trigger_events=self._generate_trigger_events(),
                disqualifiers=self._generate_disqualifiers(),
                buyer_types=[BuyerType.ECONOMIC, BuyerType.CHAMPION],
                key_stakeholders=["VP of Operations", "Head of Growth", "CFO"],
                key_messages=[
                    f"We help {name.lower()} {positioning.get('benefit', 'grow faster')}",
                    f"Unlike alternatives, we {positioning.get('differentiator', 'focus on outcomes')}",
                ],
                objections=[
                    "We already have a solution",
                    "Budget is tight this quarter",
                    "Need to involve more stakeholders"
                ],
                estimated_deal_size="$25K-$100K ACV" if tier == ICPTier.PRIMARY else "$10K-$50K ACV",
                sales_cycle_length="30-60 days" if tier == ICPTier.PRIMARY else "60-90 days",
                win_rate_estimate="35%" if tier == ICPTier.PRIMARY else "25%"
            )
            profiles.append(profile)
        
        primary = profiles[0] if profiles else None
        
        recommendations = [
            f"Focus 60% of outreach on {primary.name if primary else 'Primary ICP'}",
            "Use trigger events to time outreach",
            "Train sales team on handling top objections"
        ]
        
        summary = f"Generated {len(profiles)} ICP profiles. Primary: {primary.name if primary else 'N/A'}. "
        summary += f"Key trigger events: {len(profiles[0].trigger_events) if profiles else 0}."
        
        return ICPGenerationResult(
            profiles=profiles,
            primary_icp=primary,
            recommendations=recommendations,
            summary=summary
        )
    
    def profile_to_dict(self, profile: ICPProfile) -> Dict[str, Any]:
        """Convert profile to dictionary for storage"""
        return {
            "id": profile.id,
            "name": profile.name,
            "tier": profile.tier.value,
            "description": profile.description,
            "firmographics": {
                "company_size": profile.firmographics.company_size,
                "revenue_range": profile.firmographics.revenue_range,
                "industry": profile.firmographics.industry,
                "geography": profile.firmographics.geography,
                "stage": profile.firmographics.stage.value,
            },
            "pain_points": [{"id": p.id, "description": p.description, "severity": p.severity} for p in profile.pain_points],
            "trigger_events": [{"id": t.id, "event": t.event, "urgency": t.urgency_level} for t in profile.trigger_events],
            "disqualifiers": [{"id": d.id, "criterion": d.criterion, "is_hard": d.is_hard} for d in profile.disqualifiers],
            "key_messages": profile.key_messages,
            "estimated_deal_size": profile.estimated_deal_size,
            "sales_cycle_length": profile.sales_cycle_length,
        }
