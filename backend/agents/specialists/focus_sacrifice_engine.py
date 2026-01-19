"""
Focus & Sacrifice Engine
Helps users make strategic tradeoffs in positioning
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

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
    impact_score: float  # 0-1, how impactful this focus is
    confidence: float
    dependencies: List[str] = field(default_factory=list)


@dataclass
class SacrificeItem:
    """An item to sacrifice/deprioritize"""
    id: str
    category: FocusCategory
    description: str
    rationale: str
    impact: SacrificeImpact
    alternative_message: str  # How to message this to customers
    recovery_path: str  # How to potentially add this back later
    confidence: float


@dataclass
class TradeoffPair:
    """A focus-sacrifice pair"""
    id: str
    focus: FocusItem
    sacrifice: SacrificeItem
    net_benefit: str
    risk_assessment: str
    confidence: float


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


class FocusSacrificeEngine:
    """Engine for strategic focus and sacrifice decisions"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.counter = 0
        self.sacrifice_templates = self._load_sacrifice_templates()
    
    def _load_sacrifice_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load sacrifice reasoning templates"""
        return {
            "enterprise_features": {
                "description": "Enterprise-grade features (SSO, audit logs, compliance)",
                "alternative_message": "We focus on speed and simplicity over enterprise complexity",
                "recovery_path": "Can be added in V2 after PMF with enterprise customers",
                "impact": SacrificeImpact.MEDIUM
            },
            "broad_integrations": {
                "description": "Extensive integration library",
                "alternative_message": "We integrate deeply with the tools that matter most",
                "recovery_path": "Prioritize based on customer demand patterns",
                "impact": SacrificeImpact.LOW
            },
            "all_audiences": {
                "description": "Serving all market segments",
                "alternative_message": "We're built specifically for [target ICP]",
                "recovery_path": "Expand segments after dominating initial niche",
                "impact": SacrificeImpact.HIGH
            },
            "feature_parity": {
                "description": "Feature parity with established competitors",
                "alternative_message": "We do fewer things but do them 10x better",
                "recovery_path": "Add features based on core user feedback",
                "impact": SacrificeImpact.MEDIUM
            },
            "price_competition": {
                "description": "Competing on lowest price",
                "alternative_message": "We charge fair prices for exceptional value",
                "recovery_path": "Consider volume discounts for expansion",
                "impact": SacrificeImpact.MEDIUM
            }
        }
    
    def _generate_id(self, prefix: str) -> str:
        """Generate unique ID"""
        self.counter += 1
        return f"{prefix}-{self.counter:03d}"
    
    def _analyze_audience_focus(self, company_info: Dict[str, Any], icp_data: Dict[str, Any]) -> Tuple[FocusItem, SacrificeItem]:
        """Analyze audience focus decisions"""
        primary_icp = icp_data.get("primary_icp", {})
        secondary_icps = icp_data.get("secondary_icps", [])
        
        focus = FocusItem(
            id=self._generate_id("FOC"),
            category=FocusCategory.AUDIENCE,
            description=f"Focus exclusively on {primary_icp.get('name', 'primary ICP')}",
            rationale="Concentrated focus enables deeper understanding and better product-market fit",
            impact_score=0.9,
            confidence=0.85,
            dependencies=["messaging", "product_roadmap"]
        )
        
        sacrifice = SacrificeItem(
            id=self._generate_id("SAC"),
            category=FocusCategory.AUDIENCE,
            description=f"Deprioritize {len(secondary_icps)} secondary audience segments",
            rationale="Trying to serve everyone results in serving no one well",
            impact=SacrificeImpact.HIGH,
            alternative_message=f"We're built specifically for {primary_icp.get('name', 'our target customers')}",
            recovery_path="Expand to secondary segments after achieving 70% NPS with primary",
            confidence=0.8
        )
        
        return focus, sacrifice
    
    def _analyze_feature_focus(self, company_info: Dict[str, Any], capabilities: List[Dict[str, Any]]) -> Tuple[FocusItem, SacrificeItem]:
        """Analyze feature focus decisions"""
        # Find "Only You" or "Unique" capabilities
        differentiators = [c for c in capabilities if c.get("rating") in ["only-you", "unique"]]
        table_stakes = [c for c in capabilities if c.get("rating") == "table-stakes"]
        
        focus = FocusItem(
            id=self._generate_id("FOC"),
            category=FocusCategory.FEATURE,
            description=f"Double down on {len(differentiators)} differentiating capabilities",
            rationale="Your unique capabilities are your competitive moat",
            impact_score=0.85,
            confidence=0.8,
            dependencies=["engineering_resources", "product_vision"]
        )
        
        sacrifice = SacrificeItem(
            id=self._generate_id("SAC"),
            category=FocusCategory.FEATURE,
            description="Accept 'good enough' on table stakes features",
            rationale="Perfecting commodity features wastes resources better spent on differentiation",
            impact=SacrificeImpact.MEDIUM,
            alternative_message="We nail the things that matter most, and do the basics well",
            recovery_path="Improve table stakes based on specific churn feedback",
            confidence=0.75
        )
        
        return focus, sacrifice
    
    def _analyze_value_focus(self, company_info: Dict[str, Any], positioning: Dict[str, Any]) -> Tuple[FocusItem, SacrificeItem]:
        """Analyze value proposition focus"""
        core_value = positioning.get("primary_benefit", "core value")
        
        focus = FocusItem(
            id=self._generate_id("FOC"),
            category=FocusCategory.VALUE,
            description=f"Own the '{core_value}' position completely",
            rationale="Clear positioning is memorable positioning",
            impact_score=0.9,
            confidence=0.85,
            dependencies=["brand_messaging", "sales_pitch"]
        )
        
        sacrifice = SacrificeItem(
            id=self._generate_id("SAC"),
            category=FocusCategory.VALUE,
            description="Sacrifice being 'complete' or 'all-in-one'",
            rationale="All-in-one solutions are forgettable solutions",
            impact=SacrificeImpact.MEDIUM,
            alternative_message="We're the best at one thing, not mediocre at everything",
            recovery_path="Expand value proposition after owning initial position",
            confidence=0.8
        )
        
        return focus, sacrifice
    
    def _generate_lightbulb_insights(self, focus_items: List[FocusItem], sacrifice_items: List[SacrificeItem]) -> List[Dict[str, str]]:
        """Generate 'lightbulb' insights for the UI"""
        insights = [
            {
                "icon": "💡",
                "title": "The Paradox of Choice",
                "insight": "By choosing to NOT serve everyone, you become irresistible to your ideal customer.",
                "source": "Based on 'The Positioning Playbook'"
            },
            {
                "icon": "🎯",
                "title": "Focus Creates Magnetism",
                "insight": f"Your {len(focus_items)} focus areas will define what you're known for.",
                "source": "Strategic positioning principle"
            },
            {
                "icon": "🔥",
                "title": "Sacrifice is Strategy",
                "insight": f"The {len(sacrifice_items)} things you're choosing NOT to do are as important as what you do.",
                "source": "Michael Porter"
            }
        ]
        
        return insights
    
    async def analyze_focus_sacrifice(
        self,
        company_info: Dict[str, Any],
        icp_data: Dict[str, Any] = None,
        capabilities: List[Dict[str, Any]] = None,
        positioning: Dict[str, Any] = None
    ) -> FocusSacrificeResult:
        """
        Analyze focus and sacrifice tradeoffs
        
        Args:
            company_info: Company information
            icp_data: ICP profile data
            capabilities: Product capabilities with ratings
            positioning: Positioning data
        
        Returns:
            FocusSacrificeResult with complete analysis
        """
        icp_data = icp_data or {}
        capabilities = capabilities or []
        positioning = positioning or {}
        
        focus_items = []
        sacrifice_items = []
        tradeoff_pairs = []
        
        # Audience focus/sacrifice
        if icp_data:
            aud_focus, aud_sacrifice = self._analyze_audience_focus(company_info, icp_data)
            focus_items.append(aud_focus)
            sacrifice_items.append(aud_sacrifice)
            tradeoff_pairs.append(TradeoffPair(
                id=self._generate_id("TRD"),
                focus=aud_focus,
                sacrifice=aud_sacrifice,
                net_benefit="Deeper customer understanding and higher conversion rates",
                risk_assessment="Risk of missing adjacent opportunities - manageable with clear expansion criteria",
                confidence=0.8
            ))
        
        # Feature focus/sacrifice
        if capabilities:
            feat_focus, feat_sacrifice = self._analyze_feature_focus(company_info, capabilities)
            focus_items.append(feat_focus)
            sacrifice_items.append(feat_sacrifice)
            tradeoff_pairs.append(TradeoffPair(
                id=self._generate_id("TRD"),
                focus=feat_focus,
                sacrifice=feat_sacrifice,
                net_benefit="Stronger differentiation and clearer product story",
                risk_assessment="Risk of feature gap perception - mitigate with messaging",
                confidence=0.75
            ))
        
        # Value focus/sacrifice
        if positioning:
            val_focus, val_sacrifice = self._analyze_value_focus(company_info, positioning)
            focus_items.append(val_focus)
            sacrifice_items.append(val_sacrifice)
            tradeoff_pairs.append(TradeoffPair(
                id=self._generate_id("TRD"),
                focus=val_focus,
                sacrifice=val_sacrifice,
                net_benefit="Memorable positioning and word-of-mouth clarity",
                risk_assessment="Risk of appearing limited - counter with proof points",
                confidence=0.85
            ))
        
        # Generate insights
        lightbulb_insights = self._generate_lightbulb_insights(focus_items, sacrifice_items)
        
        # Generate recommendations
        recommendations = [
            "Communicate your focus areas clearly in all marketing",
            "Train sales team on 'why we don't' responses for sacrifices",
            "Review sacrifices quarterly - some may become strategic adds"
        ]
        
        # Constraint summary
        constraint_summary = f"Strategic focus on {len(focus_items)} key areas, "
        constraint_summary += f"with {len(sacrifice_items)} deliberate sacrifices. "
        constraint_summary += "This creates a clear, defensible market position."
        
        # Positioning statement incorporating focus
        positioning_statement = f"We focus on {focus_items[0].description if focus_items else 'our core value'}, "
        positioning_statement += f"which means we deliberately don't {sacrifice_items[0].description.lower() if sacrifice_items else 'try to do everything'}."
        
        return FocusSacrificeResult(
            focus_items=focus_items,
            sacrifice_items=sacrifice_items,
            tradeoff_pairs=tradeoff_pairs,
            positioning_statement=positioning_statement,
            lightbulb_insights=lightbulb_insights,
            recommendations=recommendations,
            constraint_summary=constraint_summary
        )
    
    def get_focus_sacrifice_summary(self, result: FocusSacrificeResult) -> Dict[str, Any]:
        """Get summary for display"""
        return {
            "focus_count": len(result.focus_items),
            "sacrifice_count": len(result.sacrifice_items),
            "tradeoffs": len(result.tradeoff_pairs),
            "positioning_statement": result.positioning_statement,
            "key_insight": result.lightbulb_insights[0] if result.lightbulb_insights else None,
            "summary": result.constraint_summary
        }
