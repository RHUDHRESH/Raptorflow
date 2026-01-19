"""
Perceptual Map Generator Agent
Creates AI-powered positioning maps with 3 strategic options
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import math
from datetime import datetime

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


@dataclass
class PositioningPoint:
    """Represents a point on the perceptual map"""
    id: str
    name: str
    x: float
    y: float
    size: float  # Market size/relevance
    description: str
    is_competitor: bool
    is_current: bool
    strategy: Optional[PositioningStrategy]


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


class PerceptualMapGenerator:
    """AI-powered perceptual map generation specialist"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.axis_definitions = self._load_axis_definitions()
        self.strategy_templates = self._load_strategy_templates()
        self.positioning_counter = 0
    
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
        # Analyze company and competitor data to determine relevant axes
        industry_keywords = company_info.get("industry", "").lower()
        product_keywords = company_info.get("product_description", "").lower()
        
        # Score axes based on relevance
        axis_scores = {}
        
        for axis_type in AxisType:
            score = 0.0
            
            # Check relevance based on keywords
            if axis_type == AxisType.PRICE_QUALITY:
                if any(word in product_keywords for word in ["price", "cost", "quality", "premium", "budget"]):
                    score += 0.8
                if any(word in industry_keywords for word in ["consumer", "retail", "b2c"]):
                    score += 0.6
            
            elif axis_type == AxisType.INNOVATION_TRADITIONAL:
                if any(word in product_keywords for word in ["innovative", "cutting-edge", "advanced", "ai", "tech"]):
                    score += 0.8
                if any(word in industry_keywords for word in ["technology", "software", "saas"]):
                    score += 0.6
            
            elif axis_type == AxisType.COMPLEXITY_SIMPLICITY:
                if any(word in product_keywords for word in ["simple", "easy", "intuitive", "complex", "comprehensive"]):
                    score += 0.8
                if any(word in industry_keywords for word in ["software", "tools", "platform"]):
                    score += 0.6
            
            elif axis_type == AxisType.MASS_MARKET_PREMIUM:
                if any(word in product_keywords for word in ["enterprise", "premium", "luxury", "mass", "mainstream"]):
                    score += 0.8
                if any(word in industry_keywords for word in ["b2b", "enterprise", "consumer"]):
                    score += 0.6
            
            elif axis_type == AxisType.TECHNICAL_HUMAN:
                if any(word in product_keywords for word in ["technical", "user-friendly", "human", "automated"]):
                    score += 0.8
                if any(word in industry_keywords for word in ["technology", "software", "service"]):
                    score += 0.6
            
            elif axis_type == AxisType.FUNCTIONAL_EMOTIONAL:
                if any(word in product_keywords for word in ["emotional", "brand", "story", "functional", "practical"]):
                    score += 0.8
                if any(word in industry_keywords for word in ["consumer", "lifestyle", "retail"]):
                    score += 0.6
            
            axis_scores[axis_type] = score
        
        # Select top 2 axes
        sorted_axes = sorted(axis_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Ensure we have different axes
        primary_axis = sorted_axes[0][0]
        secondary_axis = sorted_axes[1][0] if sorted_axes[1][1] > 0.3 else AxisType.PRICE_QUALITY  # Fallback
        
        return primary_axis, secondary_axis
    
    def _plot_competitor_position(self, competitor: Dict[str, Any], primary_axis: AxisType, secondary_axis: AxisType) -> Tuple[float, float]:
        """Calculate competitor position on the perceptual map"""
        # Mock positioning logic - in production, this would use AI analysis
        competitor_desc = competitor.get("description", "").lower()
        competitor_name = competitor.get("name", "").lower()
        
        # Calculate position on primary axis (0-1 scale)
        if primary_axis == AxisType.PRICE_QUALITY:
            # High quality = high position, low price = low position
            if any(word in competitor_desc for word in ["premium", "luxury", "high-quality"]):
                x = 0.8
            elif any(word in competitor_desc for word in ["budget", "cheap", "low-cost"]):
                x = 0.2
            else:
                x = 0.5
        
        elif primary_axis == AxisType.INNOVATION_TRADITIONAL:
            if any(word in competitor_desc for word in ["innovative", "cutting-edge", "advanced"]):
                x = 0.8
            elif any(word in competitor_desc for word in ["traditional", "established", "legacy"]):
                x = 0.2
            else:
                x = 0.5
        
        elif primary_axis == AxisType.COMPLEXITY_SIMPLICITY:
            if any(word in competitor_desc for word in ["comprehensive", "full-featured", "complex"]):
                x = 0.8
            elif any(word in competitor_desc for word in ["simple", "minimal", "basic"]):
                x = 0.2
            else:
                x = 0.5
        
        else:
            x = 0.5  # Default middle position
        
        # Calculate position on secondary axis (0-1 scale)
        if secondary_axis == AxisType.PRICE_QUALITY:
            if any(word in competitor_desc for word in ["premium", "luxury", "high-quality"]):
                y = 0.8
            elif any(word in competitor_desc for word in ["budget", "cheap", "low-cost"]):
                y = 0.2
            else:
                y = 0.5
        
        elif secondary_axis == AxisType.INNOVATION_TRADITIONAL:
            if any(word in competitor_desc for word in ["innovative", "cutting-edge", "advanced"]):
                y = 0.8
            elif any(word in competitor_desc for word in ["traditional", "established", "legacy"]):
                y = 0.2
            else:
                y = 0.5
        
        elif secondary_axis == AxisType.COMPLEXITY_SIMPLICITY:
            if any(word in competitor_desc for word in ["comprehensive", "full-featured", "complex"]):
                y = 0.8
            elif any(word in competitor_desc for word in ["simple", "minimal", "basic"]):
                y = 0.2
            else:
                y = 0.5
        
        else:
            y = 0.5  # Default middle position
        
        return (x, y)
    
    def _identify_market_gaps(self, competitors: List[PositioningPoint], primary_axis: AxisType, secondary_axis: AxisType) -> List[Dict[str, Any]]:
        """Identify gaps in the market positioning"""
        gaps = []
        
        # Create a grid to identify empty areas
        grid_size = 5
        occupied_positions = set()
        
        for competitor in competitors:
            grid_x = int(competitor.x * (grid_size - 1))
            grid_y = int(competitor.y * (grid_size - 1))
            occupied_positions.add((grid_x, grid_y))
        
        # Find empty positions
        for x in range(grid_size):
            for y in range(grid_size):
                if (x, y) not in occupied_positions:
                    # Calculate gap attractiveness based on distance from competitors
                    min_distance = min(
                        math.sqrt((competitor.x - x/(grid_size-1))**2 + (competitor.y - y/(grid_size-1))**2)
                        for competitor in competitors
                    ) if competitors else 1.0
                    
                    if min_distance > 0.3:  # Significant gap
                        gaps.append({
                            "coordinates": (x/(grid_size-1), y/(grid_size-1)),
                            "grid_position": (x, y),
                            "attractiveness": min_distance,
                            "description": f"Gap at ({x/(grid_size-1):.1f}, {y/(grid_size-1):.1f})"
                        })
        
        # Sort by attractiveness
        gaps.sort(key=lambda x: x["attractiveness"], reverse=True)
        
        return gaps[:5]  # Top 5 gaps
    
    def _generate_positioning_options(self, company_info: Dict[str, Any], gaps: List[Dict[str, Any]], primary_axis: AxisType, secondary_axis: AxisType) -> List[PositioningOption]:
        """Generate 3 strategic positioning options"""
        options = []
        
        # Option 1: Gap-based positioning (most attractive gap)
        if gaps:
            gap = gaps[0]
            strategy = self._select_strategy_for_position(gap["coordinates"], primary_axis, secondary_axis)
            
            option = PositioningOption(
                id=self._generate_positioning_id(),
                name=f"Gap Opportunity: {strategy.value.replace('_', ' ').title()}",
                description=self._generate_gap_description(gap, strategy, primary_axis, secondary_axis),
                strategy=strategy,
                coordinates=gap["coordinates"],
                rationale=f"Exploits the largest gap in the market with minimal competition",
                advantages=self.strategy_templates[strategy]["advantages"],
                disadvantages=self.strategy_templates[strategy]["disadvantages"],
                target_audience=self.strategy_templates[strategy]["target_audience"],
                competitive_angle=self.strategy_templates[strategy]["competitive_angle"],
                confidence=0.8
            )
            options.append(option)
        
        # Option 2: Differentiation strategy
        diff_coords = (0.7, 0.8)  # High innovation, high quality
        strategy = PositioningStrategy.DIFFERENTIATOR
        
        option = PositioningOption(
            id=self._generate_positioning_id(),
            name="Premium Differentiator",
            description="Position as the premium, high-quality solution with superior features",
            strategy=strategy,
            coordinates=diff_coords,
            rationale="Differentiate through superior quality and innovation",
            advantages=self.strategy_templates[strategy]["advantages"],
            disadvantages=self.strategy_templates[strategy]["disadvantages"],
            target_audience=self.strategy_templates[strategy]["target_audience"],
            competitive_angle=self.strategy_templates[strategy]["competitive_angle"],
            confidence=0.7
        )
        options.append(option)
        
        # Option 3: Cost leadership or niche strategy
        if company_info.get("target_market_size", "").lower() in ["small", "niche", "smb"]:
            niche_coords = (0.3, 0.6)  # Specialized, quality-focused
            strategy = PositioningStrategy.NICHE
            name = "Niche Specialist"
            description = "Focus on a specific market segment with specialized solutions"
        else:
            cost_coords = (0.2, 0.4)  # Low price, moderate quality
            strategy = PositioningStrategy.COST_LEADER
            name = "Cost Leader"
            description = "Compete on price while maintaining acceptable quality"
            niche_coords = cost_coords
        
        option = PositioningOption(
            id=self._generate_positioning_id(),
            name=name,
            description=description,
            strategy=strategy,
            coordinates=niche_coords,
            rationale=f"{'Focus on underserved niche' if strategy == PositioningStrategy.NICSE else 'Compete on price advantage'}",
            advantages=self.strategy_templates[strategy]["advantages"],
            disadvantages=self.strategy_templates[strategy]["disadvantages"],
            target_audience=self.strategy_templates[strategy]["target_audience"],
            competitive_angle=self.strategy_templates[strategy]["competitive_angle"],
            confidence=0.6
        )
        options.append(option)
        
        return options
    
    def _select_strategy_for_position(self, coordinates: Tuple[float, float], primary_axis: AxisType, secondary_axis: AxisType) -> PositioningStrategy:
        """Select the best strategy for given coordinates"""
        x, y = coordinates
        
        # Strategy selection logic based on position
        if x > 0.7 and y > 0.7:
            return PositioningStrategy.DIFFERENTIATOR
        elif x < 0.3 and y < 0.3:
            return PositioningStrategy.COST_LEADER
        elif x > 0.7 and y < 0.3:
            return PositioningStrategy.INNOVATION_LEADER
        elif x < 0.3 and y > 0.7:
            return PositioningStrategy.QUALITY_LEADER
        elif 0.3 <= x <= 0.7 and 0.3 <= y <= 0.7:
            return PositioningStrategy.NICHE
        else:
            return PositioningStrategy.SERVICE_LEADER
    
    def _generate_gap_description(self, gap: Dict[str, Any], strategy: PositioningStrategy, primary_axis: AxisType, secondary_axis: AxisType) -> str:
        """Generate description for gap-based positioning"""
        x, y = gap["coordinates"]
        
        primary_desc = "low" if x < 0.3 else "high" if x > 0.7 else "moderate"
        secondary_desc = "low" if y < 0.3 else "high" if y > 0.7 else "moderate"
        
        primary_axis_name = self.axis_definitions[primary_axis]["name"]
        secondary_axis_name = self.axis_definitions[secondary_axis]["name"]
        
        return f"Position in the {primary_desc} {primary_axis_name.split(' vs ')[0]} and {secondary_desc} {secondary_axis_name.split(' vs ')[0]} space with {strategy.value.replace('_', ' ')} approach"
    
    async def generate_perceptual_map(self, company_info: Dict[str, Any], competitors: List[Dict[str, Any]]) -> PerceptualMapResult:
        """
        Generate a perceptual map with positioning options
        
        Args:
            company_info: Company information including product, market, etc.
            competitors: List of competitor information
        
        Returns:
            PerceptualMapResult with complete analysis
        """
        # Select optimal axes
        primary_axis_type, secondary_axis_type = self._select_optimal_axes(company_info, competitors)
        
        # Create axis objects
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
        
        # Plot current position (mock - would be AI-determined)
        current_coords = (0.5, 0.5)  # Default center position
        current_position = PositioningPoint(
            id="current",
            name=company_info.get("name", "Your Company"),
            x=current_coords[0],
            y=current_coords[1],
            size=1.0,
            description=company_info.get("product_description", ""),
            is_competitor=False,
            is_current=True,
            strategy=None
        )
        
        # Plot competitors
        competitor_points = []
        for i, competitor in enumerate(competitors):
            coords = self._plot_competitor_position(competitor, primary_axis_type, secondary_axis_type)
            
            point = PositioningPoint(
                id=f"competitor_{i}",
                name=competitor.get("name", f"Competitor {i+1}"),
                x=coords[0],
                y=coords[1],
                size=competitor.get("market_share", 0.5),
                description=competitor.get("description", ""),
                is_competitor=True,
                is_current=False,
                strategy=None
            )
            competitor_points.append(point)
        
        # Identify market gaps
        all_points = [current_position] + competitor_points
        market_gaps = self._identify_market_gaps(all_points, primary_axis_type, secondary_axis_type)
        
        # Generate positioning options
        positioning_options = self._generate_positioning_options(company_info, market_gaps, primary_axis_type, secondary_axis_type)
        
        # Generate recommendations
        recommendations = []
        if positioning_options:
            best_option = max(positioning_options, key=lambda x: x.confidence)
            recommendations.append(f"Consider the '{best_option.name}' strategy with {best_option.confidence:.1%} confidence")
        
        if market_gaps:
            recommendations.append(f"Explored {len(market_gaps)} market gaps - largest opportunity identified")
        
        # Generate analysis summary
        summary = f"Generated perceptual map using {primary_axis.name} and {secondary_axis.name}. "
        summary += f"Analyzed {len(competitors)} competitors and identified {len(market_gaps)} market gaps. "
        summary += f"Generated {len(positioning_options)} strategic positioning options."
        
        return PerceptualMapResult(
            primary_axis=primary_axis,
            secondary_axis=secondary_axis,
            current_position=current_position,
            competitors=competitor_points,
            positioning_options=positioning_options,
            market_gaps=market_gaps,
            recommendations=recommendations,
            analysis_summary=summary
        )
