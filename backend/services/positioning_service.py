"""
RaptorFlow Market Positioning Service
Phase 3.1.1: Market Positioning Engine

Calculates 2D positioning matrices, competitive positioning analysis,
market opportunity identification, and positioning statement generation.
"""

import asyncio
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from backend.services.llm_service import LLMService, ExtractionContext
from config import get_settings
from backend.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class PositioningAxis(str, Enum):
    """Positioning axes for market analysis."""
    PRICE = "price"
    QUALITY = "quality"
    INNOVATION = "innovation"
    TRADITION = "tradition"
    CONVENIENCE = "convenience"
    PERFORMANCE = "performance"
    SERVICE = "service"
    LUXURY = "luxury"
    BUDGET = "budget"


class PositioningQuadrant(str, Enum):
    """Positioning quadrants."""
    LEADERS = "leaders"
    CHALLENGERS = "challengers"
    NICHE_PLAYERS = "niche_players"
    FOLLOWERS = "followers"
    UNCERTAIN = "uncertain"


@dataclass
class PositioningAxis:
    """Individual positioning axis definition."""
    name: str
    min_val: float
    max_val: float
    description: str
    industry: str


@dataclass
class CompanyPosition:
    """Company position on positioning axes."""
    company_name: str
    position: Dict[str, float]
    confidence: float
    market_share: Optional[float] = None


@dataclass
class MarketOpportunity:
    """Identified market opportunity."""
    id: str
    type: str
    description: str
    potential_size: str
    competition_level: str
    required_investment: str
    time_to_market: str
    confidence_score: float


@dataclass
class PositioningAnalysis:
    """Complete positioning analysis result."""
    company_position: CompanyPosition
    competitor_positions: List[CompanyPosition]
    positioning_matrix: Dict
    market_opportunities: List[MarketOpportunity]
    positioning_statement: str
    visualization_data: Dict
    positioning_score: float
    analysis_timestamp: datetime


class PositioningCalculator:
    """Core positioning calculation engine."""
    
    def __init__(self):
        self.llm_service = LLMService()
        
    async def define_positioning_axes(self, industry: str) -> List[PositioningAxis]:
        """
        Define industry-specific positioning axes.
        
        Args:
            industry: Industry type
            
        Returns:
            List of positioning axes
        """
        industry_axes = {
            'technology': [
                PositioningAxis(
                    name='Innovation',
                    min_val=0,
                    max_val=10,
                    description='Technology innovation and advancement',
                    industry='technology'
                ),
                PositioningAxis(
                    name='Enterprise Focus',
                    min_val=0,
                    max_val=10,
                    description='Target market segment (enterprise vs consumer)',
                    industry='technology'
                )
            ],
            'retail': [
                PositioningAxis(
                    name='Price Point',
                    min_val=0,
                    max_val=10,
                    description='Price positioning in market',
                    industry='retail'
                ),
                PositioningAxis(
                    name='Quality',
                    min_val=0,
                    max_val=10,
                    description='Product quality and perceived value',
                    industry='retail'
                )
            ],
            'healthcare': [
                PositioningAxis(
                    name='Accessibility',
                    min_val=0,
                    max_val=10,
                    description='Healthcare accessibility and reach',
                    industry='healthcare'
                ),
                PositioningAxis(
                    name='Specialization',
                    min_val=0,
                    max_val=10,
                    description='Medical specialization and expertise',
                    industry='healthcare'
                )
            ],
            'financial': [
                PositioningAxis(
                    name='Risk Management',
                    min_val=0,
                    max_val=10,
                    description='Risk management and security',
                    industry='financial'
                ),
                PositioningAxis(
                    name='Innovation',
                    min_val=0,
                    max_val=10,
                    description='Financial innovation and digital transformation',
                    industry='financial'
                )
            ],
            'manufacturing': [
                PositioningAxis(
                    name='Quality',
                    min_val=0,
                    max_val=10,
                    description='Product quality and reliability',
                    industry='manufacturing'
                ),
                PositioningAxis(
                    name='Cost Efficiency',
                    min_val=0,
                    max_val=10,
                    description='Cost efficiency and operational excellence',
                    industry='manufacturing'
                )
            ]
        }
        
        return industry_axes.get(industry, [
            PositioningAxis(
                name='Price',
                min_val=0,
                max_val=10,
                description='Price positioning',
                industry='general'
            ),
            PositioningAxis(
                name='Quality',
                min_val=0,
                max_val=10,
                description='Product/service quality',
                industry='general'
            )
        ])
    
    async def calculate_position_on_axes(self, company_data: Dict, axes: List[PositioningAxis]) -> Dict[str, float]:
        """
        Calculate company position on specified axes.
        
        Args:
            company_data: Company information
            axes: List of positioning axes
            
        Returns:
            Position coordinates
        """
        position = {}
        
        for axis in axes:
            score = await self._calculate_axis_score(company_data, axis)
            position[axis.name] = score
        
        return position
    
    async def _calculate_axis_score(self, company_data: Dict, axis: PositioningAxis) -> float:
        """Calculate score for a specific axis."""
        # Use LLM for intelligent scoring
        try:
            context = ExtractionContext(
                industry=company_data.get('industry', ''),
                business_context=company_data
            )
            
            prompt = f"""
            Analyze the company's position on the {axis.name} axis (0-10 scale).
            
            Company Information:
            - Name: {company_data.get('name', '')}
            - Description: {company_data.get('description', '')}
            - Business Model: {company_data.get('business_model', '')}
            - Target Market: {company_data.get('target_market', '')}
            
            {axis.description}:
            - Score 0: {axis.min_val} ({axis.min_val_description})
            - Score 10: {axis.max_val} ({axis.max_val_description})
            
            Based on the company information, provide a score from 0-10 for their position on the {axis.name} axis.
            Consider their products, pricing, marketing, and competitive positioning.
            """
            
            llm_result = await self.llm_service.generate_response(
                LLMRequest(
                    prompt=prompt,
                    model=ModelType.GPT4_TURBO,
                    temperature=0.1,
                    max_tokens=500
                )
            )
            
            # Extract score from LLM response
            score = self._extract_score_from_response(llm_result.content)
            
            # Validate and normalize score
            score = max(0, min(10, score))
            
            return score
            
        except Exception as e:
            logger.error(f"Failed to calculate {axis.name} score: {e}")
            return 5.0  # Default middle score
    
    def _extract_score_from_response(self, response: str) -> float:
        """Extract numeric score from LLM response."""
        import re
        
        # Look for patterns like "Score: 7/10" or "Rating: 7 out of 10"
        patterns = [
            r'score[:\s]*(\d+(?:\.\d+)?)\s*(?:out\s*of\s*)?(\d+)',
            r'rating[:\s]*(\d+(?:\.\d+)?)\s*(?:out\s*of\s*)?(\d+)',
            r'(\d+(?:\.\d+)?)\s*/\s*10',
            r'position[:\s]*(\d+(?:\.\d+)?)\s*/\s*10'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response.lower())
            if match:
                try:
                    score = float(match.group(1))
                    return score
                except ValueError:
                    continue
        
        # Fallback: look for any number and normalize
        numbers = re.findall(r'\d+(?:\.\d+)?', response)
        if numbers:
            try:
                scores = [float(n) for n in numbers]
                # Normalize to 0-10 scale if needed
                max_score = max(scores)
                if max_score > 10:
                    scores = [s / max_score * 10 for s in scores]
                return np.mean(scores)
            except ValueError:
                    pass
        
        return 5.0  # Default score


class OpportunityIdentifier:
    """Market opportunity identification."""
    
    def __init__(self):
        self.llm_service = LLMService()
        
    async def identify_market_opportunities(self, company_position: CompanyPosition, competitor_positions: List[CompanyPosition], axes: List[PositioningAxis]) -> List[MarketOpportunity]:
        """
        Identify market opportunities based on positioning analysis.
        
        Args:
            company_position: Our company position
            competitor_positions: Competitor positions
            axes: Positioning axes
            
        Returns:
            List of market opportunities
        """
        opportunities = []
        
        try:
            # Analyze positioning gaps
            gaps = await self._analyze_positioning_gaps(company_position, competitor_positions, axes)
            
            # Generate opportunity suggestions using LLM
            for gap in gaps:
                opportunity = await self._generate_opportunity_suggestion(gap, company_position, axes)
                if opportunity:
                    opportunities.append(opportunity)
            
            # Score opportunities
            for opportunity in opportunities:
                opportunity.confidence_score = await self._score_opportunity(opportunity, company_position)
            
            # Sort by confidence
            opportunities.sort(key=lambda x: x.confidence_score, reverse=True)
            
            return opportunities[:10]  # Top 10 opportunities
            
        except Exception as e:
            logger.error(f"Opportunity identification failed: {e}")
            return []
    
    async def _analyze_positioning_gaps(self, company_position: Dict, competitor_positions: List[Dict], axes: List[PositioningAxis]) -> List[Dict]:
        """Analyze gaps in market positioning."""
        gaps = []
        
        for axis in axes:
            axis_name = axis.name
            company_score = company_position.position.get(axis_name, 5.0)
            
            # Find competitor scores on this axis
            competitor_scores = [comp.position.get(axis_name, 5.0) for comp in competitor_positions]
            
            if not competitor_scores:
                continue
            
            # Check if there's a gap in the market
            max_score = max(competitor_scores)
            min_score = min(competitor_scores)
            
            # Look for unoccupied positions
            occupied_positions = [company_score] + competitor_scores
            
            # Find gaps in the positioning
            for score in range(0, 11):
                if score not in [round(pos) for pos in occupied_positions]):
                    # Check if this position is strategically valuable
                    if await self._is_strategic_position(score, axis, occupied_positions):
                        gaps.append({
                            'axis': axis_name,
                            'position': score,
                            'type': 'positioning_gap',
                            'description': f"Open position at {axis_name} score {score}",
                            'potential_value': await self._assess_position_value(score, axis)
                        })
            
            # Look for underserved segments
            if company_score < max_score - 2:  # We're significantly behind leaders
                gaps.append({
                    'axis': axis_name,
                    'position': company_score,
                    'type': 'opportunity_gap',
                    'description': f"Opportunity to improve {axis_name} positioning",
                    'potential_value': 'high'
                })
        
        return gaps
    
    async def _is_strategic_position(self, score: float, axis: PositioningAxis, occupied_positions: List[float]) -> bool:
        """Assess if a position is strategically valuable."""
        # Middle positions (4-7) are often strategic
        return 4 <= score <= 7
    
    async def _assess_position_value(self, score: float, axis: PositioningAxis) -> str:
        """Assess the value of a position."""
        if score >= 8:
            return 'high'
        elif score >= 6:
            return 'medium'
        elif score >= 4:
            return 'low'
        else:
            return 'very_low'
    
    async def _generate_opportunity_suggestion(self, gap: Dict, company_position: CompanyPosition, axes: List[PositioningAxis]) -> Optional[MarketOpportunity]:
        """Generate opportunity suggestion using LLM."""
        try:
            context = ExtractionContext(
                industry=company_position.get('industry', ''),
                business_context={'positioning': company_position.position}
            )
            
            prompt = f"""
            Analyze this market positioning gap and suggest a specific opportunity:
            
            Gap Information:
            - Axis: {gap.get('axis', '')}
            - Position: {gap.get('position', '')}
            - Type: {gap.get('type', '')}
            - Description: {gap.get('description', '')}
            
            Company Context:
            - Name: {company_position.get('company_name', '')}
            - Current Position: {company_position.position}
            
            Market Context:
            - Competitors: {len(axes)} major competitors in the space
            - Axis Description: {[axis.description for axis in axes]}
            
            Provide a detailed opportunity suggestion including:
            1. Specific opportunity name
            2. Market potential (small, medium, large)
            3. Required investment (low, medium, high)
            4. Time to market (short, medium, long)
            5. Strategic value
            6. Confidence score (0-1)
            
            Format as JSON with these fields: name, type, description, potential_size, competition_level, required_investment, time_to_market, confidence_score
            """
            
            llm_result = await self.llm_service.generate_response(
                LLMRequest(
                    prompt=prompt,
                    model=ModelType.GPT4_TURBO,
                    temperature=0.2,
                    max_tokens=800
                )
            )
            
            # Parse LLM response
            try:
                import json
                opportunity_data = json.loads(llm_result.content)
                
                return MarketOpportunity(
                    id=f"opp_{gap.get('axis', '')}_{gap.get('position', '')}",
                    type=opportunity_data.get('type', 'positioning_gap'),
                    description=opportunity_data.get('description', ''),
                    potential_size=opportunity_data.get('potential_size', 'medium'),
                    competition_level=opportunity_data.get('competition_level', 'medium'),
                    required_investment=opportunity_data.get('required_investment', 'medium'),
                    time_to_market=opportunity_data.get('time_to_market', 'medium'),
                    confidence_score=opportunity_data.get('confidence_score', 0.5)
                )
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"Failed to parse opportunity suggestion: {e}")
                return None
            
        except Exception as e:
            logger.error(f"Failed to generate opportunity suggestion: {e}")
            return None
    
    async def _score_opportunity(self, opportunity: MarketOpportunity, company_position: CompanyPosition) -> float:
        """Score opportunity based on multiple factors."""
        score = 0.5  # Base score
        
        # Strategic value
        if opportunity.type == 'opportunity_gap':
            score += 0.3
        
        # Market potential
        potential_scores = {'small': 0.1, 'medium': 0.3, 'large': 0.5}
        score += potential_scores.get(opportunity.potential_size, 0.3)
        
        # Investment requirement
        investment_scores = {'low': 0.2, 'medium': 0.1, 'high': 0.0}
        score += investment_scores.get(opportunity.required_investment, 0.1)
        
        # Time to market
        time_scores = {'short': 0.2, 'medium': 0.1, 'long': 0.0}
        score += time_scores.get(opportunity.time_to_market, 0.1)
        
        return min(1.0, score)


class VisualizationEngine:
    """Generate visualization data for positioning maps."""
    
    async def create_positioning_map(self, company_position: CompanyPosition, competitor_positions: List[CompanyPosition], axes: List[PositioningAxis]) -> Dict:
        """
        Create visualization data for positioning map.
        
        Args:
            company_position: Our company position
            competitor_positions: Competitor positions
            axes: Positioning axes
            
        Returns:
            Visualization data
        """
        if len(axes) != 2:
            return {'error': 'Requires exactly 2 axes for 2D visualization'}
        
        # Extract axis names
        x_axis = axes[0].name
        y_axis = axes[1].name
        
        # Prepare data points
        data_points = []
        
        # Add company position
        data_points.append({
            'name': company_position.company_name,
            'x': company_position.position.get(x_axis, 5.0),
            'y': company_position.position.get(y_axis, 5.0),
            'type': 'company',
            'size': company_position.market_share or 0.0,
            'confidence': company_position.confidence
        })
        
        # Add competitor positions
        for comp in competitor_positions:
            data_points.append({
                'name': comp.company_name,
                'x': comp.position.get(x_axis, 5.0),
                'y': comp.position.get(y_axis, 5.0),
                'type': 'competitor',
                'size': comp.market_share or 0.0,
                'confidence': comp.confidence
            })
        
        # Generate quadrant labels
        quadrants = await self._generate_quadrant_labels(axes)
        
        return {
            'type': 'positioning_map',
            'axes': {
                'x': {
                    'name': x_axis,
                    'min': axes[0].min_val,
                    'max': axes[0].max_val,
                    'label': axes[0].description
                },
                'y': {
                    'name': y_axis,
                    'min': axes[1].min_val,
                    'max': axes[1].max_val,
                    'label': axes[1].description
                }
            },
            'data_points': data_points,
            'quadrants': quadrants,
            'company_position': company_position
        }
    
    async def _generate_quadrant_labels(self, axes: List[PositioningAxis]) -> Dict:
        """Generate quadrant labels for positioning map."""
        x_axis, y_axis = axes[0], axes[1]
        
        return {
            'top_left': {
                'label': f'High {y_axis.label}, Low {x_axis.label}',
                'description': f'Premium {y_axis.lower()} with budget {x_axis.lower()} options'
            },
            'top_right': {
                'label': f'High {y_axis.label}, High {x_axis.label}',
                'description': f'Premium {y_axis.lower()} with premium {x_axis.lower()} options'
            },
            'bottom_left': {
                'label': f'Low {y_axis.label}, Low {x_axis.label}',
                'description': f'Budget {y_axis.lower()} with budget {x_axis.lower()} options'
            },
            'bottom_right': {
                'label': f'Low {y_axis.label}, High {x_axis.label}',
                'description': f'Budget {y_axis.lower()} with premium {x_axis.lower()} options'
            }
        }


class PositioningService:
    """Main positioning service."""
    
    def __init__(self):
        self.calculator = PositioningCalculator()
        self.opportunity_identifier = OpportunityIdentifier()
        self.visualization_engine = VisualizationEngine()
        self.llm_service = LLMService()
        
    async def calculate_positioning(self, company_data: Dict, competitors: List[Dict]) -> PositioningAnalysis:
        """
        Calculate comprehensive market positioning analysis.
        
        Args:
            company_data: Company information
            competitors: List of competitor data
            
        Returns:
            Complete positioning analysis
        """
        try:
            # Define positioning axes
            axes = await self.calculator.define_positioning_axes(company_data.get('industry', ''))
            
            # Calculate company position
            company_position = CompanyPosition(
                company_name=company_data.get('name', ''),
                position=await self.calculator.calculate_position_on_axes(company_data, axes),
                confidence=0.7
            )
            
            # Calculate competitor positions
            competitor_positions = []
            for comp_data in competitors:
                comp_position = CompanyPosition(
                    company_name=comp_data.get('name', ''),
                    position=await self.calculator.calculate_position_on_axes(comp_data, axes),
                    confidence=0.6
                )
                competitor_positions.append(comp_position)
            
            # Identify market opportunities
            opportunities = await self.opportunity_identifier.identify_market_opportunities(
                company_position, competitor_positions, axes
            )
            
            # Generate positioning statement
            positioning_statement = await self.llm_service.generate_market_analysis(company_data)
            
            if 'market_analysis' in positioning_statement:
                statement = positioning_statement['market_analysis'].get('positioning_statement', '')
            else:
                statement = f"{company_data.get('name', '')} is positioned as a {self._get_position_description(company_position.position, axes)} provider"
            
            # Create visualization data
            visualization_data = await self.visualization_engine.create_positioning_map(
                company_position, competitor_positions, axes
            )
            
            # Calculate positioning score
            positioning_score = await self._calculate_positioning_score(
                company_position, competitor_positions, opportunities
            )
            
            return PositioningAnalysis(
                company_position=company_position,
                competitor_positions=competitor_positions,
                positioning_matrix={
                    'axes': [axis.__dict__ for axis in axes],
                    'company_position': company_position.position,
                    'competitor_positions': [comp.position for comp in competitor_positions]
                },
                market_opportunities=opportunities,
                positioning_statement=statement,
                visualization_data=visualization_data,
                positioning_score=positioning_score,
                analysis_timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Positioning analysis failed: {e}")
            raise
    
    def _get_position_description(self, position: Dict[str, float], axes: List[PositioningAxis]) -> str:
        """Get human-readable position description."""
        descriptions = []
        
        for axis in axes:
            score = position.get(axis.name, 5.0)
            axis_desc = axis.description
            
            if score >= 8:
                descriptions.append(f"leader in {axis_desc}")
            elif score >= 6:
                descriptions.append(f"strong in {axis_desc}")
            elif score >= 4:
                descriptions.append(f"moderate in {axis_desc}")
            elif score >= 2:
                descriptions.append(f"challenger in {axis_desc}")
            else:
                descriptions.append(f"follower in {axis_desc}")
        
        return " and ".join(descriptions)
    
    async def _calculate_positioning_score(self, company_position: CompanyPosition, competitor_positions: List[CompanyPosition], opportunities: List[MarketOpportunity]) -> float:
        """Calculate overall positioning score."""
        score = 0.5  # Base score
        
        # Competitive position (higher is better)
        avg_competitor_score = np.mean([comp.confidence for comp in competitor_positions])
        if company_position.confidence > avg_competitor_score:
            score += 0.2
        
        # Market opportunities
        if opportunities:
            avg_opportunity_confidence = np.mean([opp.confidence_score for opp in opportunities])
            score += avg_opportunity_scoreidence * 0.3
        
        return min(1.0, score)


# Pydantic models for API responses
class PositioningResponse(BaseModel):
    """Response model for positioning analysis."""
    company_position: Dict
    competitor_positions: List[Dict]
    positioning_matrix: Dict
    market_opportunities: List[Dict]
    positioning_statement: str
    visualization_data: Dict
    positioning_score: float
    analysis_timestamp: datetime


# Error classes
class PositioningError(Exception):
    """Base positioning error."""
    pass


class AnalysisError(PositioningError):
    """Analysis error during positioning."""
    pass


class VisualizationError(PositioningError):
    """Visualization generation error."""
    pass
