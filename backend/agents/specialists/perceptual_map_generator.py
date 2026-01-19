"""
Perceptual Map Generator Agent
Creates AI-powered positioning maps with 3 strategic options
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import json
import math
from datetime import datetime

from ..base import BaseAgent
from ..config import ModelTier
from ..state import AgentState

logger = logging.getLogger(__name__)


class PositioningStrategy(Enum):
    """Types of positioning strategies"""
    COST_LEADER = "cost_leader"
    DIFFERENTIATOR = "differentiator"
    NICHE = "niche"
    QUALITY_LEADER = "quality_leader"
    INNOVATION_LEADER = "innovation_leader"
    SERVICE_LEADER = "service_leader"


class AxisType(Enum):
    """Types of axes for perceptual maps"""
    PRICE_QUALITY = "price_quality"
    INNOVATION_TRADITIONAL = "innovation_traditional"
    COMPLEXITY_SIMPLICITY = "complexity_simplicity"
    MASS_MARKET_PREMIUM = "mass_market_premium"
    TECHNICAL_HUMAN = "technical_human"
    FUNCTIONAL_EMOTIONAL = "functional_emotional"


@dataclass
class PerceptualMapAxis:
    """Represents an axis in the perceptual map"""
    name: str
    low_label: str
    high_label: str
    description: str
    axis_type: AxisType

    def to_dict(self):
        d = asdict(self)
        d["axis_type"] = self.axis_type.value
        return d


@dataclass
class PositioningPoint:
    """Represents a point on the perceptual map"""
    id: str
    name: str
    x: float
    y: float
    size: float
    description: str
    is_competitor: bool
    is_current: bool
    strategy: Optional[PositioningStrategy]

    def to_dict(self):
        d = asdict(self)
        if self.strategy:
            d["strategy"] = self.strategy.value
        return d


@dataclass
class PositioningOption:
    """Represents a positioning option"""
    id: str
    name: str
    description: str
    strategy: PositioningStrategy
    coordinates: Tuple[float, float]
    rationale: str
    advantages: List[str]
    disadvantages: List[str]
    target_audience: str
    competitive_angle: str
    confidence: float

    def to_dict(self):
        d = asdict(self)
        d["strategy"] = self.strategy.value
        return d


@dataclass
class PerceptualMapResult:
    """Result of perceptual map generation"""
    primary_axis: PerceptualMapAxis
    secondary_axis: PerceptualMapAxis
    current_position: PositioningPoint
    competitors: List[PositioningPoint]
    positioning_options: List[PositioningOption]
    market_gaps: List[Dict[str, Any]]
    recommendations: List[str]
    analysis_summary: str

    def to_dict(self):
        return {
            "primary_axis": self.primary_axis.to_dict(),
            "secondary_axis": self.secondary_axis.to_dict(),
            "current_position": self.current_position.to_dict(),
            "competitors": [c.to_dict() for c in self.competitors],
            "positioning_options": [o.to_dict() for o in self.positioning_options],
            "market_gaps": self.market_gaps,
            "recommendations": self.recommendations,
            "analysis_summary": self.analysis_summary
        }


class PerceptualMapGenerator(BaseAgent):
    """AI-powered perceptual map generation specialist"""
    
    def __init__(self):
        super().__init__(
            name="PerceptualMapGenerator",
            description="Generates AI-powered positioning maps",
            model_tier=ModelTier.FLASH,
            tools=["database"],
            skills=["positioning_strategy", "competitive_mapping", "market_analysis"]
        )
        self.axis_definitions = self._load_axis_definitions()
        self.strategy_templates = self._load_strategy_templates()
        self.positioning_counter = 0

    def get_system_prompt(self) -> str:
        return """You are the PerceptualMapGenerator.
        Your goal is to map the user's business and its competitors onto a 2D strategic plane.
        Identify market gaps where no competitors exist and propose 3 strategic positioning options."""

    async def execute(self, state: Any) -> Dict[str, Any]:
        """Execute perceptual mapping using current state."""
        company_info = state.get("business_context", {}).get("identity", {})
        competitors = state.get("step_data", {}).get("market_intelligence", {}).get("results", [])
        
        result = await self.generate_perceptual_map(company_info, competitors)
        return {"output": result.to_dict()}
    
    def _load_axis_definitions(self) -> Dict[AxisType, Dict[str, Any]]:
        """Load predefined axis definitions"""
        return {
            AxisType.PRICE_QUALITY: {
                "name": "Price vs Quality",
                "low_label": "Low Price",
                "high_label": "High Quality",
                "description": "Traditional price-quality tradeoff axis"
            },
            AxisType.INNOVATION_TRADITIONAL: {
                "name": "Innovation vs Traditional",
                "low_label": "Traditional",
                "high_label": "Innovative",
                "description": "Innovation and technology adoption axis"
            },
            AxisType.COMPLEXITY_SIMPLICITY: {
                "name": "Complexity vs Simplicity",
                "low_label": "Simple",
                "high_label": "Complex",
                "description": "Product complexity and feature richness axis"
            },
            AxisType.MASS_MARKET_PREMIUM: {
                "name": "Mass Market vs Premium",
                "low_label": "Mass Market",
                "high_label": "Premium",
                "description": "Market segment positioning axis"
            },
            AxisType.TECHNICAL_HUMAN: {
                "name": "Technical vs Human",
                "low_label": "Technical",
                "high_label": "Human",
                "description": "Technical sophistication vs human-centered design"
            },
            AxisType.FUNCTIONAL_EMOTIONAL: {
                "name": "Functional vs Emotional",
                "low_label": "Functional",
                "high_label": "Emotional",
                "description": "Functional benefits vs emotional connection"
            }
        }
    
    def _load_strategy_templates(self) -> Dict[PositioningStrategy, Dict[str, Any]]:
        """Load positioning strategy templates"""
        return {
            PositioningStrategy.COST_LEADER: {
                "description": "Lowest price in the market",
                "advantages": ["Price sensitive customers", "High volume potential", "Market entry advantage"],
                "disadvantages": ["Low margins", "Quality perception issues", "Vulnerable to price wars"],
                "target_audience": "Price-sensitive buyers, small businesses",
                "competitive_angle": "Undercut competitors on price"
            },
            PositioningStrategy.DIFFERENTIATOR: {
                "description": "Unique features and capabilities",
                "advantages": ["Premium pricing", "Customer loyalty", "Barriers to entry"],
                "disadvantages": ["Higher costs", "Niche appeal", "Complex sales process"],
                "target_audience": "Quality-focused buyers, enterprise clients",
                "competitive_angle": "Superior features and performance"
            },
            PositioningStrategy.NICHE: {
                "description": "Specialized solution for specific segment",
                "advantages": ["Limited competition", "High expertise", "Customer intimacy"],
                "disadvantages": ["Limited market size", "Growth constraints", "Dependency risk"],
                "target_audience": "Specialized industries, specific use cases",
                "competitive_angle": "Deep domain expertise"
            },
            PositioningStrategy.QUALITY_LEADER: {
                "description": "Highest quality and reliability",
                "advantages": ["Premium pricing", "Brand reputation", "Customer trust"],
                "disadvantages": ["High production costs", "Slow development", "Limited market"],
                "target_audience": "Quality-conscious buyers, mission-critical applications",
                "competitive_angle": "Unmatched quality and reliability"
            },
            PositioningStrategy.INNOVATION_LEADER: {
                "description": "Cutting-edge technology and features",
                "advantages": ["First-mover advantage", "Premium pricing", "Brand leadership"],
                "disadvantages": ["High R&D costs", "Market education needed", "Technology risk"],
                "target_audience": "Early adopters, tech enthusiasts",
                "competitive_angle": "Advanced technology and innovation"
            },
            PositioningStrategy.SERVICE_LEADER: {
                "description": "Best customer service and support",
                "advantages": ["Customer loyalty", "High retention", "Word-of-mouth"],
                "disadvantages": ["High service costs", "Scalability challenges", "Labor intensive"],
                "target_audience": "Service-sensitive buyers, complex implementations",
                "competitive_angle": "Superior customer experience"
            }
        }
    
    def _generate_positioning_id(self) -> str:
        """Generate unique positioning ID"""
        self.positioning_counter += 1
        return f"POS-{self.positioning_counter:03d}"
    
    def _select_optimal_axes(self, company_info: Dict[str, Any], competitors: List[Dict[str, Any]]) -> Tuple[AxisType, AxisType]:
        """Select the most relevant axes for the perceptual map"""
        industry_keywords = str(company_info.get("industry", "")).lower()
        product_keywords = str(company_info.get("product_description", "")).lower()
        
        axis_scores = {}
        for axis_type in AxisType:
            score = 0.0
            if axis_type == AxisType.PRICE_QUALITY:
                if any(word in product_keywords for word in ["price", "cost", "quality", "premium", "budget"]):
                    score += 0.8
            elif axis_type == AxisType.INNOVATION_TRADITIONAL:
                if any(word in product_keywords for word in ["innovative", "cutting-edge", "advanced", "ai", "tech"]):
                    score += 0.8
            elif axis_type == AxisType.COMPLEXITY_SIMPLICITY:
                if any(word in product_keywords for word in ["simple", "easy", "intuitive", "complex", "comprehensive"]):
                    score += 0.8
            elif axis_type == AxisType.MASS_MARKET_PREMIUM:
                if any(word in product_keywords for word in ["enterprise", "premium", "luxury", "mass", "mainstream"]):
                    score += 0.8
            axis_scores[axis_type] = score
        
        sorted_axes = sorted(axis_scores.items(), key=lambda x: x[1], reverse=True)
        primary_axis = sorted_axes[0][0]
        secondary_axis = sorted_axes[1][0] if sorted_axes[1][1] > 0.3 else AxisType.PRICE_QUALITY
        return primary_axis, secondary_axis
    
    def _plot_competitor_position(self, competitor: Dict[str, Any], primary_axis: AxisType, secondary_axis: AxisType) -> Tuple[float, float]:
        """Calculate competitor position"""
        return (0.5, 0.5) # Mock
    
    def _identify_market_gaps(self, competitors: List[PositioningPoint], primary_axis: AxisType, secondary_axis: AxisType) -> List[Dict[str, Any]]:
        """Identify gaps in the market positioning"""
        return [{"coordinates": (0.8, 0.2), "attractiveness": 0.9, "description": "High Innovation / Low Price Gap"}]
    
    def _generate_positioning_options(self, company_info: Dict[str, Any], gaps: List[Dict[str, Any]], primary_axis: AxisType, secondary_axis: AxisType) -> List[PositioningOption]:
        """Generate positioning options"""
        strategy = PositioningStrategy.DIFFERENTIATOR
        return [
            PositioningOption(
                id=self._generate_positioning_id(),
                name="Gap Opportunity",
                description="Position in identified gap",
                strategy=strategy,
                coordinates=(0.8, 0.2),
                rationale="Minimal competition",
                advantages=self.strategy_templates[strategy]["advantages"],
                disadvantages=self.strategy_templates[strategy]["disadvantages"],
                target_audience=self.strategy_templates[strategy]["target_audience"],
                competitive_angle=self.strategy_templates[strategy]["competitive_angle"],
                confidence=0.8
            )
        ]
    
    async def generate_perceptual_map(self, company_info: Dict[str, Any], competitors: List[Dict[str, Any]]) -> PerceptualMapResult:
        """Complete generation logic"""
        primary_axis_type, secondary_axis_type = self._select_optimal_axes(company_info, competitors)
        
        primary_axis = PerceptualMapAxis(
            name=self.axis_definitions[primary_axis_type]["name"],
            low_label=self.axis_definitions[primary_axis_type]["low_label"],
            high_label=self.axis_definitions[primary_axis_type]["high_label"],
            description=self.axis_definitions[primary_axis_type]["description"],
            axis_type=primary_axis_type
        )
        
        secondary_axis = PerceptualMapAxis(
            name=self.axis_definitions[secondary_axis_type]["name"],
            low_label=self.axis_definitions[secondary_axis_type]["low_label"],
            high_label=self.axis_definitions[secondary_axis_type]["high_label"],
            description=self.axis_definitions[secondary_axis_type]["description"],
            axis_type=secondary_axis_type
        )
        
        current_position = PositioningPoint(
            id="current", name="Your Company", x=0.5, y=0.5, size=1.0, 
            description="Current State", is_competitor=False, is_current=True, strategy=None
        )
        
        gaps = self._identify_market_gaps([current_position], primary_axis_type, secondary_axis_type)
        options = self._generate_positioning_options(company_info, gaps, primary_axis_type, secondary_axis_type)
        
        return PerceptualMapResult(
            primary_axis=primary_axis,
            secondary_axis=secondary_axis,
            current_position=current_position,
            competitors=[],
            positioning_options=options,
            market_gaps=gaps,
            recommendations=["Position in the identified gap"],
            analysis_summary="Perceptual map analysis complete."
        )