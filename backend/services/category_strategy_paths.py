"""
Category Strategy Paths Service
Safe/Clever/Bold strategic positioning paths for Raptorflow
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import asyncio
from collections import defaultdict

# Import AI services
try:
    from services.vertex_ai_service import vertex_ai_service
except ImportError:
    vertex_ai_service = None

logger = logging.getLogger(__name__)


class StrategyPath(str, Enum):
    """Types of strategic paths"""
    SAFE = "safe"
    CLEVER = "clever"
    BOLD = "bold"


class RiskLevel(str, Enum):
    """Risk levels for strategies"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


class TimeHorizon(str, Enum):
    """Time horizons for strategy"""
    SHORT_TERM = "short_term"  # 3-6 months
    MEDIUM_TERM = "medium_term"  # 6-18 months
    LONG_TERM = "long_term"  # 18+ months


@dataclass
class StrategicPosition:
    """Strategic positioning option"""
    id: str
    name: str
    description: str
    path: StrategyPath
    risk_level: RiskLevel
    time_horizon: TimeHorizon
    investment_required: float  # 0-1 scale
    expected_roi: float  # 0-1 scale
    success_probability: float  # 0-1 scale
    competitive_advantage: float  # 0-1 scale
    market_opportunity: float  # 0-1 scale
    key_actions: List[str] = field(default_factory=list)
    required_capabilities: List[str] = field(default_factory=list)
    potential_obstacles: List[str] = field(default_factory=list)
    success_metrics: List[str] = field(default_factory=list)
    rationale: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "path": self.path.value,
            "risk_level": self.risk_level.value,
            "time_horizon": self.time_horizon.value,
            "investment_required": self.investment_required,
            "expected_roi": self.expected_roi,
            "success_probability": self.success_probability,
            "competitive_advantage": self.competitive_advantage,
            "market_opportunity": self.market_opportunity,
            "key_actions": self.key_actions,
            "required_capabilities": self.required_capabilities,
            "potential_obstacles": self.potential_obstacles,
            "success_metrics": self.success_metrics,
            "rationale": self.rationale,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class PathAnalysis:
    """Analysis of strategic paths"""
    recommended_path: StrategyPath
    alternative_paths: List[StrategyPath]
    path_positions: Dict[StrategyPath, StrategicPosition]
    risk_assessment: Dict[str, float]
    resource_requirements: Dict[str, float]
    timeline_recommendations: Dict[StrategyPath, TimeHorizon]
    decision_factors: List[str]
    confidence_score: float
    created_at: datetime = field(default_factory=datetime.now)


class CategoryStrategyPaths:
    """Category strategy paths service for safe/clever/bold positioning"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Strategy templates
        self.strategy_templates = self._initialize_strategy_templates()
        
        # Risk assessment factors
        self.risk_factors = self._initialize_risk_factors()
        
        # Capability requirements
        self.capability_matrix = self._initialize_capability_matrix()
    
    def _initialize_strategy_templates(self) -> Dict[StrategyPath, Dict[str, Any]]:
        """Initialize strategy templates for each path"""
        return {
            StrategyPath.SAFE: {
                "description": "Conservative approach with proven methods and minimal risk",
                "risk_level": RiskLevel.LOW,
                "time_horizon": TimeHorizon.SHORT_TERM,
                "investment_range": (0.1, 0.3),
                "roi_range": (0.2, 0.5),
                "success_probability_range": (0.7, 0.9),
                "competitive_advantage_range": (0.1, 0.3),
                "market_opportunity_range": (0.2, 0.4),
                "key_themes": ["proven", "reliable", "established", "conservative", "stable"],
                "required_capabilities": ["execution", "reliability", "consistency"],
                "typical_obstacles": ["market saturation", "price competition", "slow growth"]
            },
            StrategyPath.CLEVER: {
                "description": "Smart approach with innovative tactics within acceptable risk",
                "risk_level": RiskLevel.MEDIUM,
                "time_horizon": TimeHorizon.MEDIUM_TERM,
                "investment_range": (0.3, 0.6),
                "roi_range": (0.4, 0.8),
                "success_probability_range": (0.5, 0.7),
                "competitive_advantage_range": (0.4, 0.6),
                "market_opportunity_range": (0.4, 0.6),
                "key_themes": ["innovative", "smart", "efficient", "strategic", "optimized"],
                "required_capabilities": ["innovation", "adaptability", "strategic_thinking"],
                "typical_obstacles": ["execution complexity", "resource constraints", "market adoption"]
            },
            StrategyPath.BOLD: {
                "description": "Aggressive approach with high risk and high reward potential",
                "risk_level": RiskLevel.HIGH,
                "time_horizon": TimeHorizon.LONG_TERM,
                "investment_range": (0.6, 0.9),
                "roi_range": (0.6, 1.0),
                "success_probability_range": (0.3, 0.5),
                "competitive_advantage_range": (0.7, 0.9),
                "market_opportunity_range": (0.6, 0.8),
                "key_themes": ["disruptive", "revolutionary", "breakthrough", "pioneering", "game-changing"],
                "required_capabilities": ["vision", "risk_tolerance", "innovation", "leadership"],
                "typical_obstacles": ["market resistance", "resource requirements", "timing risks"]
            }
        }
    
    def _initialize_risk_factors(self) -> Dict[str, float]:
        """Initialize risk assessment factors"""
        return {
            "market_maturity": 0.2,  # Mature markets = lower risk
            "competition_intensity": 0.3,  # High competition = higher risk
            "resource_availability": 0.2,  # Limited resources = higher risk
            "technological_complexity": 0.15,  # Complex tech = higher risk
            "regulatory_environment": 0.1,  # Heavy regulation = higher risk
            "economic_conditions": 0.05  # Poor economy = higher risk
        }
    
    def _initialize_capability_matrix(self) -> Dict[StrategyPath, List[str]]:
        """Initialize capability requirements matrix"""
        return {
            StrategyPath.SAFE: [
                "operational_excellence",
                "financial_management",
                "customer_service",
                "quality_control",
                "process_optimization"
            ],
            StrategyPath.CLEVER: [
                "strategic_planning",
                "market_analysis",
                "product_innovation",
                "data_analytics",
                "agile_execution"
            ],
            StrategyPath.BOLD: [
                "visionary_leadership",
                "disruptive_innovation",
                "risk_management",
                "resource_mobilization",
                "market_creation"
            ]
        }
    
    async def generate_category_paths(self, company_info: Dict[str, Any], market_analysis: Dict[str, Any], competitive_insights: List[Dict[str, Any]]) -> PathAnalysis:
        """Generate strategic category paths"""
        
        # Analyze company context
        company_context = await self._analyze_company_context(company_info)
        
        # Analyze market conditions
        market_context = await self._analyze_market_context(market_analysis, competitive_insights)
        
        # Generate strategic positions for each path
        path_positions = {}
        for path in StrategyPath:
            position = await self._generate_strategic_position(path, company_context, market_context)
            path_positions[path] = position
        
        # Assess risks for each path
        risk_assessment = await self._assess_path_risks(path_positions, company_context, market_context)
        
        # Analyze resource requirements
        resource_requirements = await self._analyze_resource_requirements(path_positions)
        
        # Generate timeline recommendations
        timeline_recommendations = await self._generate_timeline_recommendations(path_positions, company_context)
        
        # Determine recommended path
        recommended_path = await self._determine_recommended_path(path_positions, risk_assessment, company_context)
        
        # Generate decision factors
        decision_factors = await self._generate_decision_factors(path_positions, risk_assessment, company_context)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(path_positions, company_context, market_context)
        
        return PathAnalysis(
            recommended_path=recommended_path,
            alternative_paths=[path for path in StrategyPath if path != recommended_path],
            path_positions=path_positions,
            risk_assessment=risk_assessment,
            resource_requirements=resource_requirements,
            timeline_recommendations=timeline_recommendations,
            decision_factors=decision_factors,
            confidence_score=confidence_score
        )
    
    async def _analyze_company_context(self, company_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze company context for strategy selection"""
        context = {
            "size": company_info.get("size", "startup").lower(),
            "age": self._calculate_company_age(company_info.get("founded_year")),
            "financial_resources": company_info.get("financial_resources", "limited").lower(),
            "team_size": company_info.get("employee_count", 10),
            "growth_stage": company_info.get("growth_stage", "early").lower(),
            "risk_tolerance": company_info.get("risk_tolerance", "medium").lower(),
            "innovation_capability": company_info.get("innovation_capability", "developing").lower(),
            "market_position": company_info.get("market_position", "new").lower()
        }
        
        # Calculate strategic maturity
        strategic_maturity = 0.0
        if context["age"] > 5:
            strategic_maturity += 0.2
        if context["team_size"] > 50:
            strategic_maturity += 0.2
        if context["financial_resources"] == "strong":
            strategic_maturity += 0.3
        if context["innovation_capability"] == "mature":
            strategic_maturity += 0.3
        
        context["strategic_maturity"] = strategic_maturity
        
        return context
    
    def _calculate_company_age(self, founded_year: Optional[int]) -> int:
        """Calculate company age"""
        if not founded_year:
            return 0
        return datetime.now().year - founded_year
    
    async def _analyze_market_context(self, market_analysis: Dict[str, Any], competitive_insights: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze market context for strategy selection"""
        context = {
            "market_growth_rate": market_analysis.get("growth_rate", 0.1),
            "market_size": market_analysis.get("market_size", "medium").lower(),
            "competition_level": market_analysis.get("competition_level", "moderate").lower(),
            "technological_change": market_analysis.get("technological_change", "moderate").lower(),
            "customer_demand": market_analysis.get("customer_demand", "growing").lower(),
            "barriers_to_entry": market_analysis.get("barriers_to_entry", "medium").lower(),
            "profit_margins": market_analysis.get("profit_margins", "average").lower()
        }
        
        # Analyze competitive intensity
        if competitive_insights:
            high_competition = len([insight for insight in competitive_insights if insight.get("urgency_score", 0) > 0.7])
            context["competitive_intensity"] = high_competition / len(competitive_insights)
        else:
            context["competitive_intensity"] = 0.5
        
        # Calculate market attractiveness
        market_attractiveness = 0.0
        if context["market_growth_rate"] > 0.15:
            market_attractiveness += 0.3
        if context["customer_demand"] == "growing":
            market_attractiveness += 0.2
        if context["barriers_to_entry"] == "low":
            market_attractiveness += 0.2
        if context["profit_margins"] == "high":
            market_attractiveness += 0.3
        
        context["market_attractiveness"] = market_attractiveness
        
        return context
    
    async def _generate_strategic_position(self, path: StrategyPath, company_context: Dict[str, Any], market_context: Dict[str, Any]) -> StrategicPosition:
        """Generate strategic position for specific path"""
        template = self.strategy_templates[path]
        
        # Generate position name and description
        name, description = await self._generate_position_content(path, company_context, market_context)
        
        # Calculate metrics based on template ranges and context
        investment_required = self._calculate_investment_required(path, template, company_context)
        expected_roi = self._calculate_expected_roi(path, template, market_context)
        success_probability = self._calculate_success_probability(path, template, company_context, market_context)
        competitive_advantage = self._calculate_competitive_advantage(path, template, market_context)
        market_opportunity = self._calculate_market_opportunity(path, template, market_context)
        
        # Generate key actions
        key_actions = await self._generate_key_actions(path, company_context, market_context)
        
        # Determine required capabilities
        required_capabilities = self.capability_matrix[path]
        
        # Identify potential obstacles
        potential_obstacles = self._identify_potential_obstacles(path, template, company_context, market_context)
        
        # Generate success metrics
        success_metrics = self._generate_success_metrics(path)
        
        # Generate rationale
        rationale = self._generate_rationale(path, company_context, market_context)
        
        return StrategicPosition(
            id=f"{path.value}_position",
            name=name,
            description=description,
            path=path,
            risk_level=template["risk_level"],
            time_horizon=template["time_horizon"],
            investment_required=investment_required,
            expected_roi=expected_roi,
            success_probability=success_probability,
            competitive_advantage=competitive_advantage,
            market_opportunity=market_opportunity,
            key_actions=key_actions,
            required_capabilities=required_capabilities,
            potential_obstacles=potential_obstacles,
            success_metrics=success_metrics,
            rationale=rationale
        )
    
    async def _generate_position_content(self, path: StrategyPath, company_context: Dict[str, Any], market_context: Dict[str, Any]) -> Tuple[str, str]:
        """Generate position name and description"""
        if path == StrategyPath.SAFE:
            name = "Market Follower Strategy"
            description = "Conservative approach focusing on proven methods and steady growth with minimal risk"
        elif path == StrategyPath.CLEVER:
            name = "Smart Challenger Strategy"
            description = "Innovative approach leveraging unique capabilities to outmaneuver competitors"
        else:  # BOLD
            name = "Market Disruptor Strategy"
            description = "Aggressive approach aiming to reshape the market through breakthrough innovation"
        
        return name, description
    
    def _calculate_investment_required(self, path: StrategyPath, template: Dict[str, Any], company_context: Dict[str, Any]) -> float:
        """Calculate investment required for strategy"""
        base_range = template["investment_range"]
        
        # Adjust based on company context
        if company_context["financial_resources"] == "limited":
            multiplier = 0.8
        elif company_context["financial_resources"] == "strong":
            multiplier = 1.2
        else:
            multiplier = 1.0
        
        # Calculate within range
        investment = (base_range[0] + base_range[1]) / 2 * multiplier
        return min(1.0, max(0.0, investment))
    
    def _calculate_expected_roi(self, path: StrategyPath, template: Dict[str, Any], market_context: Dict[str, Any]) -> float:
        """Calculate expected ROI for strategy"""
        base_range = template["roi_range"]
        
        # Adjust based on market context
        if market_context["market_attractiveness"] > 0.7:
            multiplier = 1.2
        elif market_context["market_attractiveness"] < 0.3:
            multiplier = 0.8
        else:
            multiplier = 1.0
        
        # Calculate within range
        roi = (base_range[0] + base_range[1]) / 2 * multiplier
        return min(1.0, max(0.0, roi))
    
    def _calculate_success_probability(self, path: StrategyPath, template: Dict[str, Any], company_context: Dict[str, Any], market_context: Dict[str, Any]) -> float:
        """Calculate success probability for strategy"""
        base_range = template["success_probability_range"]
        
        # Adjust based on company and market context
        company_multiplier = 1.0
        if path == StrategyPath.SAFE and company_context["strategic_maturity"] > 0.5:
            company_multiplier = 1.2
        elif path == StrategyPath.CLEVER and company_context["innovation_capability"] == "mature":
            company_multiplier = 1.2
        elif path == StrategyPath.BOLD and company_context["risk_tolerance"] == "high":
            company_multiplier = 1.2
        
        market_multiplier = 1.0
        if market_context["competitive_intensity"] < 0.3:
            market_multiplier = 1.2
        elif market_context["competitive_intensity"] > 0.7:
            market_multiplier = 0.8
        
        # Calculate within range
        probability = (base_range[0] + base_range[1]) / 2 * company_multiplier * market_multiplier
        return min(1.0, max(0.0, probability))
    
    def _calculate_competitive_advantage(self, path: StrategyPath, template: Dict[str, Any], market_context: Dict[str, Any]) -> float:
        """Calculate competitive advantage for strategy"""
        base_range = template["competitive_advantage_range"]
        
        # Adjust based on market context
        if market_context["competition_level"] == "low":
            multiplier = 1.2
        elif market_context["competition_level"] == "high":
            multiplier = 0.8
        else:
            multiplier = 1.0
        
        # Calculate within range
        advantage = (base_range[0] + base_range[1]) / 2 * multiplier
        return min(1.0, max(0.0, advantage))
    
    def _calculate_market_opportunity(self, path: StrategyPath, template: Dict[str, Any], market_context: Dict[str, Any]) -> float:
        """Calculate market opportunity for strategy"""
        base_range = template["market_opportunity_range"]
        
        # Adjust based on market context
        if market_context["market_growth_rate"] > 0.2:
            multiplier = 1.3
        elif market_context["market_growth_rate"] < 0.05:
            multiplier = 0.7
        else:
            multiplier = 1.0
        
        # Calculate within range
        opportunity = (base_range[0] + base_range[1]) / 2 * multiplier
        return min(1.0, max(0.0, opportunity))
    
    async def _generate_key_actions(self, path: StrategyPath, company_context: Dict[str, Any], market_context: Dict[str, Any]) -> List[str]:
        """Generate key actions for strategy"""
        if path == StrategyPath.SAFE:
            return [
                "Optimize existing processes for efficiency",
                "Focus on customer retention and satisfaction",
                "Implement proven marketing tactics",
                "Maintain financial discipline",
                "Build operational excellence"
            ]
        elif path == StrategyPath.CLEVER:
            return [
                "Identify and exploit market inefficiencies",
                "Develop differentiated value proposition",
                "Implement data-driven decision making",
                "Build strategic partnerships",
                "Focus on innovation within constraints"
            ]
        else:  # BOLD
            return [
                "Pursue breakthrough innovation",
                "Disrupt existing market dynamics",
                "Build strong brand presence",
                "Secure significant funding/resources",
                "Create new market categories"
            ]
    
    def _identify_potential_obstacles(self, path: StrategyPath, template: Dict[str, Any], company_context: Dict[str, Any], market_context: Dict[str, Any]) -> List[str]:
        """Identify potential obstacles for strategy"""
        base_obstacles = template["typical_obstacles"]
        
        # Add context-specific obstacles
        obstacles = base_obstacles.copy()
        
        if company_context["financial_resources"] == "limited":
            obstacles.append("Resource constraints")
        
        if market_context["competitive_intensity"] > 0.7:
            obstacles.append("Intense competitive pressure")
        
        if company_context["team_size"] < 20:
            obstacles.append("Limited team capacity")
        
        return obstacles[:5]  # Top 5 obstacles
    
    def _generate_success_metrics(self, path: StrategyPath) -> List[str]:
        """Generate success metrics for strategy"""
        if path == StrategyPath.SAFE:
            return [
                "Revenue growth rate (5-15% annually)",
                "Customer retention rate (>85%)",
                "Profit margin stability",
                "Operational efficiency metrics",
                "Market share maintenance"
            ]
        elif path == StrategyPath.CLEVER:
            return [
                "Revenue growth rate (15-30% annually)",
                "Market share gain (3-5% annually)",
                "Customer acquisition cost efficiency",
                "Innovation adoption rate",
                "Competitive differentiation metrics"
            ]
        else:  # BOLD
            return [
                "Revenue growth rate (30%+ annually)",
                "Market disruption indicators",
                "New customer segment acquisition",
                "Brand recognition growth",
                "Industry leadership position"
            ]
    
    def _generate_rationale(self, path: StrategyPath, company_context: Dict[str, Any], market_context: Dict[str, Any]) -> str:
        """Generate rationale for strategy selection"""
        if path == StrategyPath.SAFE:
            return "This strategy minimizes risk while building a solid foundation for future growth, ideal for companies with limited resources or in mature markets."
        elif path == StrategyPath.CLEVER:
            return "This strategy balances innovation with risk, leveraging unique capabilities to outperform competitors while maintaining financial discipline."
        else:  # BOLD
            return "This strategy pursues market leadership through disruption, requiring significant investment but offering substantial rewards for successful execution."
    
    async def _assess_path_risks(self, path_positions: Dict[StrategyPath, StrategicPosition], company_context: Dict[str, Any], market_context: Dict[str, Any]) -> Dict[str, float]:
        """Assess risks for each strategic path"""
        risk_assessment = {}
        
        for path, position in path_positions.items():
            risk_score = 0.0
            
            # Base risk from strategy type
            if path == StrategyPath.SAFE:
                base_risk = 0.2
            elif path == StrategyPath.CLEVER:
                base_risk = 0.5
            else:  # BOLD
                base_risk = 0.8
            
            # Adjust for company context
            if company_context["strategic_maturity"] < 0.3:
                risk_score += 0.2
            
            if company_context["financial_resources"] == "limited":
                risk_score += 0.1
            
            # Adjust for market context
            if market_context["competitive_intensity"] > 0.7:
                risk_score += 0.1
            
            if market_context["technological_change"] == "rapid":
                risk_score += 0.1
            
            # Calculate final risk
            final_risk = base_risk + risk_score
            risk_assessment[path.value] = min(1.0, max(0.0, final_risk))
        
        return risk_assessment
    
    async def _analyze_resource_requirements(self, path_positions: Dict[StrategyPath, StrategicPosition]) -> Dict[str, float]:
        """Analyze resource requirements for each path"""
        resource_requirements = {}
        
        for path, position in path_positions.items():
            # Base resource requirement from investment level
            base_requirement = position.investment_required
            
            # Adjust for complexity
            if path == StrategyPath.BOLD:
                complexity_multiplier = 1.5
            elif path == StrategyPath.CLEVER:
                complexity_multiplier = 1.2
            else:  # SAFE
                complexity_multiplier = 1.0
            
            final_requirement = base_requirement * complexity_multiplier
            resource_requirements[path.value] = min(1.0, max(0.0, final_requirement))
        
        return resource_requirements
    
    async def _generate_timeline_recommendations(self, path_positions: Dict[StrategyPath, StrategicPosition], company_context: Dict[str, Any]) -> Dict[StrategyPath, TimeHorizon]:
        """Generate timeline recommendations for each path"""
        timeline_recommendations = {}
        
        for path, position in path_positions.items():
            base_horizon = position.time_horizon
            
            # Adjust based on company context
            if company_context["strategic_maturity"] < 0.3:
                # Less mature companies need more time
                if base_horizon == TimeHorizon.SHORT_TERM:
                    timeline_recommendations[path] = TimeHorizon.MEDIUM_TERM
                elif base_horizon == TimeHorizon.MEDIUM_TERM:
                    timeline_recommendations[path] = TimeHorizon.LONG_TERM
                else:
                    timeline_recommendations[path] = TimeHorizon.LONG_TERM
            else:
                timeline_recommendations[path] = base_horizon
        
        return timeline_recommendations
    
    async def _determine_recommended_path(self, path_positions: Dict[StrategyPath, StrategicPosition], risk_assessment: Dict[str, float], company_context: Dict[str, Any]) -> StrategyPath:
        """Determine recommended strategic path"""
        # Calculate score for each path
        path_scores = {}
        
        for path, position in path_positions.items():
            score = 0.0
            
            # Weight factors
            weights = {
                "success_probability": 0.3,
                "expected_roi": 0.2,
                "competitive_advantage": 0.2,
                "market_opportunity": 0.15,
                "risk_penalty": 0.15
            }
            
            # Calculate weighted score
            score += position.success_probability * weights["success_probability"]
            score += position.expected_roi * weights["expected_roi"]
            score += position.competitive_advantage * weights["competitive_advantage"]
            score += position.market_opportunity * weights["market_opportunity"]
            
            # Subtract risk penalty
            risk_penalty = risk_assessment[path.value] * weights["risk_penalty"]
            score -= risk_penalty
            
            # Adjust for company context
            if company_context["risk_tolerance"] == "low" and path == StrategyPath.BOLD:
                score -= 0.2
            elif company_context["risk_tolerance"] == "high" and path == StrategyPath.SAFE:
                score -= 0.1
            
            path_scores[path] = score
        
        # Return path with highest score
        return max(path_scores, key=path_scores.get)
    
    async def _generate_decision_factors(self, path_positions: Dict[StrategyPath, StrategicPosition], risk_assessment: Dict[str, float], company_context: Dict[str, Any]) -> List[str]:
        """Generate key decision factors"""
        factors = []
        
        # Risk tolerance consideration
        if company_context["risk_tolerance"] == "low":
            factors.append("Low risk tolerance favors Safe strategy")
        elif company_context["risk_tolerance"] == "high":
            factors.append("High risk tolerance enables Bold strategy")
        
        # Resource availability
        if company_context["financial_resources"] == "limited":
            factors.append("Limited resources constrain Bold options")
        
        # Market conditions
        highest_opportunity = max(path_positions.values(), key=lambda x: x.market_opportunity)
        factors.append(f"Highest market opportunity: {highest_opportunity.name}")
        
        # Success probability
        highest_success = max(path_positions.values(), key=lambda x: x.success_probability)
        factors.append(f"Highest success probability: {highest_success.name}")
        
        # Risk assessment
        lowest_risk = min(risk_assessment.items(), key=lambda x: x[1])
        factors.append(f"Lowest risk path: {lowest_risk[0].title()}")
        
        return factors
    
    def _calculate_confidence_score(self, path_positions: Dict[StrategyPath, StrategicPosition], company_context: Dict[str, Any], market_context: Dict[str, Any]) -> float:
        """Calculate confidence score in recommendations"""
        base_confidence = 0.7
        
        # Adjust based on data quality
        if company_context["strategic_maturity"] > 0.5:
            base_confidence += 0.1
        
        if market_context["market_attractiveness"] > 0.5:
            base_confidence += 0.1
        
        # Adjust for consistency
        success_probabilities = [pos.success_probability for pos in path_positions.values()]
        if max(success_probabilities) - min(success_probabilities) > 0.4:
            base_confidence -= 0.1
        
        return min(1.0, max(0.0, base_confidence))


# Export service
__all__ = ["CategoryStrategyPaths", "PathAnalysis", "StrategicPosition"]
