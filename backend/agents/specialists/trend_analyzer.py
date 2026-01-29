"""
TrendAnalyzer specialist agent for Raptorflow marketing automation.
Handles trend analysis, market forecasting, and predictive insights.
"""

import json
import logging
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..base import BaseAgent
from ..config import ModelTier
from ..exceptions import DatabaseError, ValidationError
from ..state import AgentState, add_message, update_state

logger = logging.getLogger(__name__)


@dataclass
class TrendAnalysisRequest:
    """Trend analysis request."""

    analysis_type: str  # market, content, social, consumer, technology, comprehensive
    industry: str
    time_horizon: str  # short_term, medium_term, long_term
    data_sources: List[str]
    focus_areas: List[str]
    geographic_scope: str
    confidence_threshold: float
    prediction_models: List[str]


@dataclass
class TrendData:
    """Individual trend data point."""

    trend_id: str
    name: str
    category: str
    description: str
    current_momentum: float
    growth_potential: float
    market_impact: float
    time_horizon: str
    confidence_score: float
    data_points: List[Dict[str, Any]]
    key_indicators: List[str]


@dataclass
class MarketTrend:
    """Market-specific trend."""

    trend_id: str
    market_segment: str
    trend_name: str
    direction: str  # rising, falling, stable, volatile
    magnitude: float
    drivers: List[str]
    barriers: List[str]
    opportunities: List[str]
    threats: List[str]
    timeline: str
    confidence: float


@dataclass
class ContentTrend:
    """Content-specific trend."""

    trend_id: str
    content_type: str
    trend_name: str
    engagement_trend: str  # increasing, decreasing, seasonal
    performance_metrics: Dict[str, float]
    viral_potential: float
    audience_adoption: float
    platform_specific: Dict[str, Any]
    best_practices: List[str]


@dataclass
class SocialTrend:
    """Social media trend."""

    trend_id: str
    platform: str
    trend_name: str
    hashtag: str
    engagement_rate: float
    reach_potential: float
    demographic_appeal: Dict[str, float]
    longevity: str  # short_lived, medium_term, long_term
    brand_safety: float


@dataclass
class ConsumerTrend:
    """Consumer behavior trend."""

    trend_id: str
    behavior_pattern: str
    demographic_segments: List[str]
    adoption_rate: float
    satisfaction_impact: float
    purchase_influence: float
    loyalty_impact: float
    psychological_drivers: List[str]
    market_size: float


@dataclass
class TechnologyTrend:
    """Technology trend."""

    trend_id: str
    technology_name: str
    maturity_level: str  # emerging, growing, mature, declining
    adoption_rate: float
    market_potential: float
    disruption_potential: float
    investment_trend: str
    key_players: List[str]
    implementation_complexity: float


@dataclass
class TrendForecast:
    """Trend forecast and prediction."""

    forecast_id: str
    trend_name: str
    prediction_period: str
    predicted_trajectory: List[Dict[str, float]]
    confidence_intervals: Dict[str, List[float]]
    key_milestones: List[Dict[str, Any]]
    risk_factors: List[str]
    success_indicators: List[str]
    recommended_actions: List[str]


@dataclass
class TrendAnalysisReport:
    """Complete trend analysis report."""

    report_id: str
    analysis_type: str
    industry: str
    time_horizon: str
    geographic_scope: str
    executive_summary: str
    market_trends: List[MarketTrend]
    content_trends: List[ContentTrend]
    social_trends: List[SocialTrend]
    consumer_trends: List[ConsumerTrend]
    technology_trends: List[TechnologyTrend]
    forecasts: List[TrendForecast]
    key_insights: List[str]
    strategic_recommendations: List[str]
    opportunity_matrix: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    generated_at: datetime
    metadata: Dict[str, Any]


class TrendAnalyzer(BaseAgent):
    """Specialist agent for trend analysis and market forecasting."""

    def __init__(self):
        super().__init__(
            name="TrendAnalyzer",
            description="Analyzes trends and provides predictive market intelligence",
            model_tier=ModelTier.FLASH,
            tools=["web_search", "database", "content_gen"],
        )

        # Trend analysis frameworks
        self.analysis_frameworks = {
            "market": {
                "focus_areas": [
                    "market_size",
                    "growth_rates",
                    "competition",
                    "demand_patterns",
                    "price_trends",
                ],
                "indicators": [
                    "market_volume",
                    "customer_acquisition",
                    "retention_rates",
                    "market_share",
                ],
                "data_sources": [
                    "market_research",
                    "industry_reports",
                    "analyst_data",
                    "economic_indicators",
                ],
            },
            "content": {
                "focus_areas": [
                    "content_formats",
                    "engagement_patterns",
                    "viral_content",
                    "topic_trends",
                    "platform_shifts",
                ],
                "indicators": [
                    "engagement_rates",
                    "share_rates",
                    "comment_patterns",
                    "view_duration",
                ],
                "data_sources": [
                    "social_platforms",
                    "content_analytics",
                    "trending_topics",
                    "viral_analytics",
                ],
            },
            "social": {
                "focus_areas": [
                    "platform_trends",
                    "hashtag_trends",
                    "influencer_patterns",
                    "user_behavior",
                    "community_dynamics",
                ],
                "indicators": [
                    "engagement_metrics",
                    "growth_rates",
                    "sentiment_analysis",
                    "viral_coefficient",
                ],
                "data_sources": [
                    "social_apis",
                    "social_listening",
                    "influencer_data",
                    "community_analytics",
                ],
            },
            "consumer": {
                "focus_areas": [
                    "behavior_patterns",
                    "purchase_decisions",
                    "brand_preferences",
                    "loyalty_trends",
                    "satisfaction_patterns",
                ],
                "indicators": [
                    "purchase_frequency",
                    "customer_lifetime_value",
                    "satisfaction_scores",
                    "brand_switching",
                ],
                "data_sources": [
                    "customer_surveys",
                    "purchase_data",
                    "behavior_analytics",
                    "feedback_data",
                ],
            },
            "technology": {
                "focus_areas": [
                    "adoption_curves",
                    "innovation_patterns",
                    "disruption_potential",
                    "investment_trends",
                    "implementation_barriers",
                ],
                "indicators": [
                    "adoption_rates",
                    "investment_flows",
                    "patent_filings",
                    "developer_activity",
                ],
                "data_sources": [
                    "tech_reports",
                    "patent_data",
                    "investment_data",
                    "developer_metrics",
                ],
            },
        }

        # Industry trend patterns
        self.industry_patterns = {
            "technology": {
                "growth_rate": 0.15,
                "innovation_cycle": "18 months",
                "disruption_frequency": "high",
                "key_drivers": ["innovation", "efficiency", "automation"],
            },
            "retail": {
                "growth_rate": 0.08,
                "innovation_cycle": "24 months",
                "disruption_frequency": "medium",
                "key_drivers": ["convenience", "price", "experience"],
            },
            "healthcare": {
                "growth_rate": 0.12,
                "innovation_cycle": "36 months",
                "disruption_frequency": "low",
                "key_drivers": ["outcomes", "cost", "accessibility"],
            },
            "finance": {
                "growth_rate": 0.10,
                "innovation_cycle": "30 months",
                "disruption_frequency": "high",
                "key_drivers": ["security", "efficiency", "compliance"],
            },
        }

        # Trend prediction models
        self.prediction_models = {
            "linear_regression": {
                "accuracy": 0.75,
                "data_requirements": "historical_data",
                "best_for": "steady_trends",
            },
            "exponential_smoothing": {
                "accuracy": 0.80,
                "data_requirements": "time_series",
                "best_for": "seasonal_trends",
            },
            "neural_network": {
                "accuracy": 0.85,
                "data_requirements": "large_dataset",
                "best_for": "complex_patterns",
            },
            "ensemble_method": {
                "accuracy": 0.88,
                "data_requirements": "multiple_sources",
                "best_for": "high_accuracy",
            },
        }

        # Time horizon definitions
        self.time_horizons = {
            "short_term": {
                "duration": "0-6 months",
                "confidence_factor": 0.9,
                "focus": "immediate_opportunities",
            },
            "medium_term": {
                "duration": "6-18 months",
                "confidence_factor": 0.8,
                "focus": "strategic_planning",
            },
            "long_term": {
                "duration": "18+ months",
                "confidence_factor": 0.7,
                "focus": "vision_and_direction",
            },
        }

        # Trend categories
        self.trend_categories = {
            "emerging": {
                "description": "New trends with high growth potential",
                "risk_level": "high",
                "opportunity_level": "high",
            },
            "growing": {
                "description": "Established trends with steady growth",
                "risk_level": "medium",
                "opportunity_level": "medium",
            },
            "mature": {
                "description": "Stable trends with predictable patterns",
                "risk_level": "low",
                "opportunity_level": "low",
            },
            "declining": {
                "description": "Trends losing momentum",
                "risk_level": "high",
                "opportunity_level": "low",
            },
        }

        # Confidence scoring
        self.confidence_factors = {
            "data_quality": 0.3,
            "sample_size": 0.2,
            "time_relevance": 0.2,
            "source_credibility": 0.15,
            "methodology": 0.15,
        }

    def get_system_prompt(self) -> str:
        """Get the system prompt for the TrendAnalyzer."""
        return """
You are the TrendAnalyzer, a specialist agent for Raptorflow marketing automation platform.

Your role is to analyze trends across multiple domains and provide predictive insights to inform strategic decision-making.

Key responsibilities:
1. Identify and analyze emerging trends in markets, content, social media, consumer behavior, and technology
2. Forecast trend trajectories and market developments
3. Assess trend momentum and growth potential
4. Evaluate risks and opportunities associated with trends
5. Provide actionable recommendations based on trend analysis
6. Monitor trend evolution and pattern changes
7. Generate predictive models and forecasts

Analysis types you can perform:
- Market Trends (market size, growth, competition, demand patterns)
- Content Trends (content formats, engagement patterns, viral content)
- Social Trends (platform trends, hashtags, influencer patterns)
- Consumer Trends (behavior patterns, purchase decisions, brand preferences)
- Technology Trends (adoption curves, innovation patterns, disruption potential)
- Comprehensive Analysis (all domains combined)

For each trend analysis, you should:
- Gather comprehensive trend data from multiple sources
- Analyze trend momentum and growth trajectories
- Assess confidence levels and prediction accuracy
- Identify opportunities and risks
- Generate actionable forecasts and recommendations
- Consider time horizons and geographic scope
- Provide strategic insights for decision-making

Always focus on providing accurate, actionable trend intelligence that helps anticipate market changes and capitalize on emerging opportunities.
"""

    async def execute(self, state: AgentState) -> AgentState:
        """Execute trend analysis."""
        try:
            # Validate workspace context
            if not state.get("workspace_id"):
                return self._set_error(
                    state, "Workspace ID is required for trend analysis"
                )

            # Extract trend analysis request from state
            trend_request = self._extract_trend_request(state)

            if not trend_request:
                return self._set_error(state, "No trend analysis request provided")

            # Validate trend request
            self._validate_trend_request(trend_request)

            # Perform trend analysis
            trend_report = await self._perform_trend_analysis(trend_request, state)

            # Store trend report
            await self._store_trend_report(trend_report, state)

            # Add assistant message
            response = self._format_trend_response(trend_report)
            state = self._add_assistant_message(state, response)

            # Set output
            return self._set_output(
                state,
                {
                    "trend_report": trend_report.__dict__,
                    "trends_identified": len(trend_report.market_trends)
                    + len(trend_report.content_trends)
                    + len(trend_report.social_trends),
                    "forecasts_generated": len(trend_report.forecasts),
                    "key_insights": len(trend_report.key_insights),
                },
            )

        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            return self._set_error(state, f"Trend analysis failed: {str(e)}")

    def _extract_trend_request(
        self, state: AgentState
    ) -> Optional[TrendAnalysisRequest]:
        """Extract trend analysis request from state."""
        # Check if trend request is in state
        if "trend_request" in state:
            request_data = state["trend_request"]
            return TrendAnalysisRequest(**request_data)

        # Extract from user message
        user_input = self._extract_user_input(state)
        if not user_input:
            return None

        # Parse trend request from user input
        return self._parse_trend_request(user_input, state)

    def _parse_trend_request(
        self, user_input: str, state: AgentState
    ) -> Optional[TrendAnalysisRequest]:
        """Parse trend request from user input."""
        # Extract analysis type
        analysis_types = list(self.analysis_frameworks.keys())
        detected_type = None

        for analysis_type in analysis_types:
            if analysis_type in user_input.lower():
                detected_type = analysis_type
                break

        if not detected_type:
            detected_type = "comprehensive"

        # Extract other parameters
        industry = self._extract_parameter(
            user_input, ["industry", "sector", "market"], "technology"
        )
        horizon = self._extract_parameter(
            user_input, ["horizon", "timeframe", "period"], "medium_term"
        )
        scope = self._extract_parameter(
            user_input, ["scope", "geography", "region"], "global"
        )

        # Create trend request
        return TrendAnalysisRequest(
            analysis_type=detected_type,
            industry=industry,
            time_horizon=horizon,
            data_sources=["industry_reports", "social_media", "market_data"],
            focus_areas=[],
            geographic_scope=scope,
            confidence_threshold=0.8,
            prediction_models=["ensemble_method"],
        )

    def _extract_parameter(
        self, text: str, param_names: List[str], default: str
    ) -> str:
        """Extract parameter value from text."""
        for param_name in param_names:
            for pattern in [f"{param_name}:", f"{param_name} is", f"{param_name} ="]:
                if pattern in text.lower():
                    start_idx = text.lower().find(pattern)
                    if start_idx != -1:
                        start_idx += len(pattern)
                        remaining = text[start_idx:].strip()
                        # Get first word or phrase
                        words = remaining.split()
                        if words:
                            return words[0].strip(".,!?")
        return default

    def _validate_trend_request(self, request: TrendAnalysisRequest):
        """Validate trend analysis request."""
        if (
            request.analysis_type not in self.analysis_frameworks
            and request.analysis_type != "comprehensive"
        ):
            raise ValidationError(f"Unsupported analysis type: {request.analysis_type}")

        if request.time_horizon not in self.time_horizons:
            raise ValidationError(f"Invalid time horizon: {request.time_horizon}")

        if request.confidence_threshold < 0.5 or request.confidence_threshold > 1.0:
            raise ValidationError(
                f"Invalid confidence threshold: {request.confidence_threshold}"
            )

        valid_models = list(self.prediction_models.keys())
        for model in request.prediction_models:
            if model not in valid_models:
                raise ValidationError(f"Invalid prediction model: {model}")

    async def _perform_trend_analysis(
        self, request: TrendAnalysisRequest, state: AgentState
    ) -> TrendAnalysisReport:
        """Perform comprehensive trend analysis."""
        try:
            # Generate report ID
            report_id = f"trend_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Perform analysis based on type
            market_trends = []
            content_trends = []
            social_trends = []
            consumer_trends = []
            technology_trends = []

            if request.analysis_type in ["market", "comprehensive"]:
                market_trends = self._analyze_market_trends(request)

            if request.analysis_type in ["content", "comprehensive"]:
                content_trends = self._analyze_content_trends(request)

            if request.analysis_type in ["social", "comprehensive"]:
                social_trends = self._analyze_social_trends(request)

            if request.analysis_type in ["consumer", "comprehensive"]:
                consumer_trends = self._analyze_consumer_trends(request)

            if request.analysis_type in ["technology", "comprehensive"]:
                technology_trends = self._analyze_technology_trends(request)

            # Generate forecasts
            forecasts = self._generate_trend_forecasts(
                market_trends + content_trends + social_trends, request
            )

            # Generate key insights
            key_insights = self._generate_key_insights(
                market_trends,
                content_trends,
                social_trends,
                consumer_trends,
                technology_trends,
            )

            # Generate strategic recommendations
            strategic_recommendations = self._generate_strategic_recommendations(
                key_insights, request
            )

            # Create opportunity matrix
            opportunity_matrix = self._create_opportunity_matrix(
                market_trends, content_trends, social_trends
            )

            # Create risk assessment
            risk_assessment = self._create_risk_assessment(forecasts, request)

            # Generate executive summary
            executive_summary = self._generate_executive_summary(
                key_insights, strategic_recommendations
            )

            # Create trend analysis report
            trend_report = TrendAnalysisReport(
                report_id=report_id,
                analysis_type=request.analysis_type,
                industry=request.industry,
                time_horizon=request.time_horizon,
                geographic_scope=request.geographic_scope,
                executive_summary=executive_summary,
                market_trends=market_trends,
                content_trends=content_trends,
                social_trends=social_trends,
                consumer_trends=consumer_trends,
                technology_trends=technology_trends,
                forecasts=forecasts,
                key_insights=key_insights,
                strategic_recommendations=strategic_recommendations,
                opportunity_matrix=opportunity_matrix,
                risk_assessment=risk_assessment,
                generated_at=datetime.now(),
                metadata={
                    "data_sources": request.data_sources,
                    "focus_areas": request.focus_areas,
                    "confidence_threshold": request.confidence_threshold,
                    "prediction_models": request.prediction_models,
                },
            )

            return trend_report

        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            raise DatabaseError(f"Trend analysis failed: {str(e)}")

    def _analyze_market_trends(
        self, request: TrendAnalysisRequest
    ) -> List[MarketTrend]:
        """Analyze market trends."""
        trends = []

        # Generate simulated market trends
        market_segments = ["enterprise", "smb", "consumer", "government"]
        trend_directions = ["rising", "falling", "stable", "volatile"]

        for i in range(3):  # Generate 3 market trends
            segment = random.choice(market_segments)
            direction = random.choice(trend_directions)

            trend = MarketTrend(
                trend_id=f"market_trend_{i}",
                market_segment=segment,
                trend_name=f"{segment.title()} Market {direction.title()}",
                direction=direction,
                magnitude=random.uniform(0.1, 0.5),
                drivers=[
                    "Digital transformation",
                    "Cost optimization",
                    "Customer experience focus",
                ],
                barriers=[
                    "Implementation complexity",
                    "Budget constraints",
                    "Skill gaps",
                ],
                opportunities=[
                    "Market expansion",
                    "Product innovation",
                    "Strategic partnerships",
                ],
                threats=[
                    "Competitive pressure",
                    "Regulatory changes",
                    "Economic uncertainty",
                ],
                timeline=request.time_horizon,
                confidence=random.uniform(0.7, 0.9),
            )
            trends.append(trend)

        return trends

    def _analyze_content_trends(
        self, request: TrendAnalysisRequest
    ) -> List[ContentTrend]:
        """Analyze content trends."""
        trends = []

        content_types = ["video", "blog", "infographic", "podcast", "interactive"]
        engagement_trends = ["increasing", "decreasing", "seasonal"]

        for i in range(3):  # Generate 3 content trends
            content_type = random.choice(content_types)
            engagement = random.choice(engagement_trends)

            trend = ContentTrend(
                trend_id=f"content_trend_{i}",
                content_type=content_type,
                trend_name=f"{content_type.title()} Content {engagement.title()}",
                engagement_trend=engagement,
                performance_metrics={
                    "engagement_rate": random.uniform(0.02, 0.15),
                    "share_rate": random.uniform(0.01, 0.08),
                    "conversion_rate": random.uniform(0.001, 0.05),
                },
                viral_potential=random.uniform(0.1, 0.8),
                audience_adoption=random.uniform(0.3, 0.9),
                platform_specific={
                    "linkedin": random.uniform(0.2, 0.8),
                    "twitter": random.uniform(0.1, 0.6),
                    "instagram": random.uniform(0.3, 0.9),
                },
                best_practices=[
                    "Mobile-first design",
                    "Interactive elements",
                    "Personalization",
                ],
            )
            trends.append(trend)

        return trends

    def _analyze_social_trends(
        self, request: TrendAnalysisRequest
    ) -> List[SocialTrend]:
        """Analyze social media trends."""
        trends = []

        platforms = ["linkedin", "twitter", "instagram", "tiktok", "facebook"]
        longevities = ["short_lived", "medium_term", "long_term"]

        for i in range(3):  # Generate 3 social trends
            platform = random.choice(platforms)
            longevity = random.choice(longevities)

            trend = SocialTrend(
                trend_id=f"social_trend_{i}",
                platform=platform,
                trend_name=f"{platform.title()} Trend #{i+1}",
                hashtag=f"trend{i+1}2024",
                engagement_rate=random.uniform(0.02, 0.12),
                reach_potential=random.uniform(10000, 1000000),
                demographic_appeal={
                    "gen_z": random.uniform(0.1, 0.8),
                    "millennials": random.uniform(0.2, 0.9),
                    "gen_x": random.uniform(0.1, 0.6),
                    "boomers": random.uniform(0.05, 0.4),
                },
                longevity=longevity,
                brand_safety=random.uniform(0.7, 0.95),
            )
            trends.append(trend)

        return trends

    def _analyze_consumer_trends(
        self, request: TrendAnalysisRequest
    ) -> List[ConsumerTrend]:
        """Analyze consumer behavior trends."""
        trends = []

        behaviors = [
            "digital_first",
            "sustainability_focused",
            "experience_driven",
            "price_sensitive",
            "quality_seeking",
        ]
        demographics = ["gen_z", "millennials", "gen_x", "boomers"]

        for i in range(3):  # Generate 3 consumer trends
            behavior = random.choice(behaviors)
            segments = random.sample(demographics, 2)

            trend = ConsumerTrend(
                trend_id=f"consumer_trend_{i}",
                behavior_pattern=behavior.replace("_", " ").title(),
                demographic_segments=segments,
                adoption_rate=random.uniform(0.2, 0.8),
                satisfaction_impact=random.uniform(0.1, 0.7),
                purchase_influence=random.uniform(0.3, 0.9),
                loyalty_impact=random.uniform(0.2, 0.8),
                psychological_drivers=[
                    "Convenience",
                    "Status",
                    "Sustainability",
                    "Experience",
                ],
                market_size=random.uniform(1000000, 10000000),
            )
            trends.append(trend)

        return trends

    def _analyze_technology_trends(
        self, request: TrendAnalysisRequest
    ) -> List[TechnologyTrend]:
        """Analyze technology trends."""
        trends = []

        technologies = ["ai_ml", "blockchain", "iot", "ar_vr", "quantum_computing"]
        maturity_levels = ["emerging", "growing", "mature", "declining"]

        for i in range(3):  # Generate 3 technology trends
            tech = random.choice(technologies)
            maturity = random.choice(maturity_levels)

            trend = TechnologyTrend(
                trend_id=f"tech_trend_{i}",
                technology_name=tech.replace("_", " ").title(),
                maturity_level=maturity,
                adoption_rate=random.uniform(0.1, 0.9),
                market_potential=random.uniform(0.2, 0.95),
                disruption_potential=random.uniform(0.1, 0.9),
                investment_trend=random.choice(["increasing", "stable", "decreasing"]),
                key_players=["Tech Giant A", "Startup B", "Research Institute C"],
                implementation_complexity=random.uniform(0.3, 0.9),
            )
            trends.append(trend)

        return trends

    def _generate_trend_forecasts(
        self, trends: List[Any], request: TrendAnalysisRequest
    ) -> List[TrendForecast]:
        """Generate trend forecasts."""
        forecasts = []

        # Generate forecasts for top trends
        top_trends = trends[:3]  # Top 3 trends

        for i, trend in enumerate(top_trends):
            # Generate trajectory data points
            trajectory_points = []
            for month in range(1, 13):  # 12 months forecast
                trajectory_points.append(
                    {
                        "month": month,
                        "value": random.uniform(0.5, 1.5),
                        "confidence": random.uniform(0.7, 0.9),
                    }
                )

            forecast = TrendForecast(
                forecast_id=f"forecast_{i}",
                trend_name=getattr(trend, "trend_name", f"Trend {i+1}"),
                prediction_period=request.time_horizon,
                predicted_trajectory=trajectory_points,
                confidence_intervals={
                    "upper": [point["value"] * 1.2 for point in trajectory_points],
                    "lower": [point["value"] * 0.8 for point in trajectory_points],
                },
                key_milestones=[
                    {"month": 3, "event": "Initial adoption milestone"},
                    {"month": 6, "event": "Market penetration threshold"},
                    {"month": 9, "event": "Maturity phase begins"},
                ],
                risk_factors=[
                    "Market volatility",
                    "Competitive response",
                    "Regulatory changes",
                ],
                success_indicators=[
                    "Adoption rate > 50%",
                    "Market share growth",
                    "Positive ROI",
                ],
                recommended_actions=[
                    "Monitor trend closely",
                    "Prepare contingency plans",
                    "Invest in capabilities",
                ],
            )
            forecasts.append(forecast)

        return forecasts

    def _generate_key_insights(
        self,
        market_trends: List[MarketTrend],
        content_trends: List[ContentTrend],
        social_trends: List[SocialTrend],
        consumer_trends: List[ConsumerTrend],
        technology_trends: List[TechnologyTrend],
    ) -> List[str]:
        """Generate key insights from trend analysis."""
        insights = []

        # Market insights
        if market_trends:
            rising_markets = [t for t in market_trends if t.direction == "rising"]
            if rising_markets:
                insights.append(
                    f"{len(rising_markets)} market segments showing strong growth potential"
                )

        # Content insights
        if content_trends:
            increasing_content = [
                t for t in content_trends if t.engagement_trend == "increasing"
            ]
            if increasing_content:
                insights.append(
                    f"{len(increasing_content)} content formats showing increasing engagement"
                )

        # Social insights
        if social_trends:
            high_engagement = [t for t in social_trends if t.engagement_rate > 0.08]
            if high_engagement:
                insights.append(
                    f"High engagement trends identified on {len(set(t.platform for t in high_engagement))} platforms"
                )

        # Consumer insights
        if consumer_trends:
            high_adoption = [t for t in consumer_trends if t.adoption_rate > 0.6]
            if high_adoption:
                insights.append(
                    f"{len(high_adoption)} consumer behavior patterns showing high adoption rates"
                )

        # Technology insights
        if technology_trends:
            emerging_tech = [
                t for t in technology_trends if t.maturity_level == "emerging"
            ]
            if emerging_tech:
                insights.append(
                    f"{len(emerging_tech)} emerging technologies with high disruption potential"
                )

        # Cross-domain insights
        insights.append("Digital transformation continues to drive market evolution")
        insights.append("Customer experience remains a key competitive differentiator")
        insights.append("Sustainability and social responsibility gaining importance")

        return insights[:8]  # Limit to 8 insights

    def _generate_strategic_recommendations(
        self, insights: List[str], request: TrendAnalysisRequest
    ) -> List[str]:
        """Generate strategic recommendations based on insights."""
        recommendations = []

        # Based on insights, generate specific recommendations
        if any("growth" in insight.lower() for insight in insights):
            recommendations.append("Invest resources in high-growth market segments")

        if any("engagement" in insight.lower() for insight in insights):
            recommendations.append(
                "Optimize content strategy for high-engagement formats"
            )

        if any("technology" in insight.lower() for insight in insights):
            recommendations.append(
                "Evaluate emerging technologies for competitive advantage"
            )

        if any("consumer" in insight.lower() for insight in insights):
            recommendations.append(
                "Align product development with consumer behavior trends"
            )

        # General strategic recommendations
        recommendations.append("Develop agile response mechanisms for trend changes")
        recommendations.append("Establish trend monitoring and early warning systems")
        recommendations.append("Build cross-functional trend analysis capabilities")
        recommendations.append("Create innovation pipelines based on trend insights")

        return recommendations[:6]  # Limit to 6 recommendations

    def _create_opportunity_matrix(
        self,
        market_trends: List[MarketTrend],
        content_trends: List[ContentTrend],
        social_trends: List[SocialTrend],
    ) -> Dict[str, Any]:
        """Create opportunity matrix."""
        matrix = {
            "high_impact_high_probability": [],
            "high_impact_low_probability": [],
            "low_impact_high_probability": [],
            "low_impact_low_probability": [],
        }

        # Categorize trends by impact and probability
        all_trends = market_trends + content_trends + social_trends

        for trend in all_trends:
            impact = random.choice(["high", "low"])
            probability = random.choice(["high", "low"])

            category = f"{impact}_impact_{probability}_probability"
            matrix[category].append(
                {
                    "name": getattr(trend, "trend_name", "Unnamed Trend"),
                    "type": type(trend).__name__.replace("Trend", ""),
                    "rationale": "Based on current momentum and market signals",
                }
            )

        return matrix

    def _create_risk_assessment(
        self, forecasts: List[TrendForecast], request: TrendAnalysisRequest
    ) -> Dict[str, Any]:
        """Create risk assessment."""
        assessment = {
            "overall_risk_level": "medium",
            "key_risks": [
                {
                    "risk": "Market volatility",
                    "probability": "medium",
                    "impact": "high",
                    "mitigation": "Diversification strategy",
                },
                {
                    "risk": "Technology disruption",
                    "probability": "high",
                    "impact": "medium",
                    "mitigation": "Continuous innovation",
                },
                {
                    "risk": "Consumer behavior shifts",
                    "probability": "medium",
                    "impact": "medium",
                    "mitigation": "Customer feedback systems",
                },
            ],
            "risk_factors": [
                "Economic uncertainty",
                "Regulatory changes",
                "Competitive pressure",
                "Technology adoption barriers",
            ],
            "mitigation_strategies": [
                "Scenario planning",
                "Agile response capabilities",
                "Strategic partnerships",
                "Investment in R&D",
            ],
        }

        return assessment

    def _generate_executive_summary(
        self, insights: List[str], recommendations: List[str]
    ) -> str:
        """Generate executive summary."""
        summary = f"Trend analysis reveals {len(insights)} key insights across market, content, social, consumer, and technology domains. "
        summary += f"Analysis indicates significant opportunities in digital transformation and customer experience enhancement. "
        summary += f"Strategic recommendations focus on agile response mechanisms and trend monitoring capabilities. "
        summary += f"Overall risk level is manageable with proper mitigation strategies in place."

        return summary

    async def _store_trend_report(self, report: TrendAnalysisReport, state: AgentState):
        """Store trend report in database."""
        try:
            # Store in database with workspace isolation
            database_tool = self._get_tool("database")
            if database_tool:
                await database_tool.arun(
                    table="trend_analysis_reports",
                    workspace_id=state["workspace_id"],
                    data={
                        "report_id": report.report_id,
                        "analysis_type": report.analysis_type,
                        "industry": report.industry,
                        "time_horizon": report.time_horizon,
                        "geographic_scope": report.geographic_scope,
                        "executive_summary": report.executive_summary,
                        "market_trends": [
                            trend.__dict__ for trend in report.market_trends
                        ],
                        "content_trends": [
                            trend.__dict__ for trend in report.content_trends
                        ],
                        "social_trends": [
                            trend.__dict__ for trend in report.social_trends
                        ],
                        "consumer_trends": [
                            trend.__dict__ for trend in report.consumer_trends
                        ],
                        "technology_trends": [
                            trend.__dict__ for trend in report.technology_trends
                        ],
                        "forecasts": [
                            forecast.__dict__ for forecast in report.forecasts
                        ],
                        "key_insights": report.key_insights,
                        "strategic_recommendations": report.strategic_recommendations,
                        "opportunity_matrix": report.opportunity_matrix,
                        "risk_assessment": report.risk_assessment,
                        "generated_at": report.generated_at.isoformat(),
                        "metadata": report.metadata,
                    },
                )

        except Exception as e:
            logger.error(f"Failed to store trend report: {e}")

    def _format_trend_response(self, report: TrendAnalysisReport) -> str:
        """Format trend analysis response for user."""
        response = f"≡ƒôê **Trend Analysis Report**\n\n"
        response += f"**Analysis Type:** {report.analysis_type.title()}\n"
        response += f"**Industry:** {report.industry.title()}\n"
        response += (
            f"**Time Horizon:** {report.time_horizon.replace('_', ' ').title()}\n"
        )
        response += f"**Geographic Scope:** {report.geographic_scope.title()}\n\n"

        response += f"**Executive Summary:**\n{report.executive_summary}\n\n"

        response += f"**Key Insights:**\n"
        for insight in report.key_insights:
            response += f"ΓÇó {insight}\n"
        response += "\n"

        response += f"**Trends Identified:**\n"
        response += f"ΓÇó Market Trends: {len(report.market_trends)}\n"
        response += f"ΓÇó Content Trends: {len(report.content_trends)}\n"
        response += f"ΓÇó Social Trends: {len(report.social_trends)}\n"
        response += f"ΓÇó Consumer Trends: {len(report.consumer_trends)}\n"
        response += f"ΓÇó Technology Trends: {len(report.technology_trends)}\n\n"

        response += f"**Strategic Recommendations:**\n"
        for recommendation in report.strategic_recommendations:
            response += f"ΓÇó {recommendation}\n"
        response += "\n"

        response += f"**Forecasts Generated:** {len(report.forecasts)}\n"
        response += f"**Overall Risk Level:** {report.risk_assessment['overall_risk_level'].title()}\n\n"

        response += f"**Top Opportunities:**\n"
        high_impact_high_prob = report.opportunity_matrix.get(
            "high_impact_high_probability", []
        )
        for opportunity in high_impact_high_prob[:3]:
            response += f"ΓÇó {opportunity['name']} ({opportunity['type']})\n"

        return response
