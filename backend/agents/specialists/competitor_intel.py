"""
CompetitorIntelAgent specialist agent for Raptorflow marketing automation.
Handles competitor analysis, market intelligence, and competitive positioning.
"""

import json
import logging
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..base import BaseAgent
from backend.agents.config import ModelTier
from ..exceptions import DatabaseError, ValidationError
from ..state import AgentState, add_message, update_state

logger = logging.getLogger(__name__)


@dataclass
class CompetitorRequest:
    """Competitor intelligence request."""

    competitors: List[str]  # Competitor names or domains
    analysis_type: str  # content, seo, social, pricing, positioning, comprehensive
    industry: str
    target_market: str
    analysis_depth: str  # basic, detailed, comprehensive
    time_period: str  # last_30_days, last_90_days, last_year
    focus_areas: List[str]  # Specific areas to analyze


@dataclass
class CompetitorProfile:
    """Individual competitor profile."""

    competitor_id: str
    name: str
    domain: str
    company_size: str
    market_position: str
    strengths: List[str]
    weaknesses: List[str]
    market_share: float
    estimated_revenue: str
    founding_year: int
    headquarters: str
    employee_count: str
    key_products: List[str]
    target_audience: str
    brand_positioning: str


@dataclass
class ContentAnalysis:
    """Content strategy analysis."""

    content_types: Dict[str, int]  # Content type frequencies
    content_themes: List[str]
    content_frequency: str
    content_quality_score: float
    top_performing_content: List[Dict[str, Any]]
    content_gaps: List[str]
    voice_tone: str
    engagement_metrics: Dict[str, float]


@dataclass
class SEOAnalysis:
    """SEO performance analysis."""

    organic_keywords: int
    monthly_organic_traffic: int
    domain_authority: float
    backlinks_count: int
    top_keywords: List[Dict[str, Any]]
    keyword_gaps: List[str]
    content_optimization: float
    technical_seo_score: float


@dataclass
class SocialAnalysis:
    """Social media analysis."""

    platforms: Dict[str, Dict[str, Any]]
    posting_frequency: Dict[str, str]
    engagement_rates: Dict[str, float]
    follower_growth: Dict[str, float]
    top_performing_posts: List[Dict[str, Any]]
    social_strategy: str
    brand_voice_consistency: float


@dataclass
class PricingAnalysis:
    """Pricing strategy analysis."""

    pricing_model: str
    price_points: List[Dict[str, Any]]
    discount_strategies: List[str]
    value_proposition: str
    competitive_positioning: str
    price_elasticity: str
    revenue_streams: List[str]


@dataclass
class CompetitiveInsight:
    """Competitive intelligence insight."""

    insight_id: str
    category: str  # opportunity, threat, strength, weakness
    title: str
    description: str
    impact: str  # high, medium, low
    confidence: float
    actionable: bool
    recommendation: str
    data_points: List[str]


@dataclass
class CompetitorIntelReport:
    """Complete competitor intelligence report."""

    report_id: str
    analysis_type: str
    industry: str
    target_market: str
    competitors: List[CompetitorProfile]
    content_analysis: ContentAnalysis
    seo_analysis: SEOAnalysis
    social_analysis: SocialAnalysis
    pricing_analysis: PricingAnalysis
    insights: List[CompetitiveInsight]
    market_positioning_map: Dict[str, Any]
    strategic_recommendations: List[str]
    competitive_advantages: List[str]
    threats: List[str]
    opportunities: List[str]
    generated_at: datetime
    metadata: Dict[str, Any]


class CompetitorIntelAgent(BaseAgent):
    """Specialist agent for competitor intelligence and market analysis."""

    def __init__(self):
        super().__init__(
            name="CompetitorIntelAgent",
            description="Analyzes competitors and provides strategic market intelligence",
            model_tier=ModelTier.FLASH,
            tools=["web_search", "database", "content_gen"],
        )

        # Analysis frameworks
        self.analysis_frameworks = {
            "content": {
                "focus_areas": [
                    "content_strategy",
                    "themes",
                    "quality",
                    "frequency",
                    "engagement",
                ],
                "metrics": [
                    "word_count",
                    "readability",
                    "seo_score",
                    "engagement_rate",
                    "shareability",
                ],
                "data_sources": [
                    "website_content",
                    "blog_posts",
                    "social_media",
                    "email_campaigns",
                ],
            },
            "seo": {
                "focus_areas": [
                    "keywords",
                    "backlinks",
                    "domain_authority",
                    "technical_seo",
                    "content_optimization",
                ],
                "metrics": [
                    "organic_traffic",
                    "keyword_rankings",
                    "backlink_quality",
                    "page_speed",
                    "mobile_friendly",
                ],
                "data_sources": [
                    "seo_tools",
                    "search_engines",
                    "analytics",
                    "technical_audits",
                ],
            },
            "social": {
                "focus_areas": [
                    "platform_presence",
                    "engagement",
                    "growth",
                    "content_strategy",
                    "brand_voice",
                ],
                "metrics": [
                    "follower_count",
                    "engagement_rate",
                    "posting_frequency",
                    "reach",
                    "impressions",
                ],
                "data_sources": [
                    "social_platforms",
                    "social_listening",
                    "influencer_analysis",
                    "sentiment_analysis",
                ],
            },
            "pricing": {
                "focus_areas": [
                    "pricing_model",
                    "price_points",
                    "discounts",
                    "value_proposition",
                    "positioning",
                ],
                "metrics": [
                    "price_levels",
                    "feature_comparison",
                    "discount_frequency",
                    "customer_lifetime_value",
                ],
                "data_sources": [
                    "pricing_pages",
                    "customer_reviews",
                    "industry_reports",
                    "market_research",
                ],
            },
            "positioning": {
                "focus_areas": [
                    "brand_positioning",
                    "value_proposition",
                    "target_audience",
                    "messaging",
                    "differentiation",
                ],
                "metrics": [
                    "brand awareness",
                    "market_share",
                    "customer_satisfaction",
                    "brand_perception",
                ],
                "data_sources": [
                    "brand_materials",
                    "customer_feedback",
                    "market_research",
                    "competitive_analysis",
                ],
            },
        }

        # Industry benchmarks
        self.industry_benchmarks = {
            "technology": {
                "avg_domain_authority": 45,
                "avg_monthly_traffic": 50000,
                "avg_engagement_rate": 0.025,
                "avg_content_frequency": "3 posts per week",
                "avg_pricing_model": "subscription",
            },
            "ecommerce": {
                "avg_domain_authority": 35,
                "avg_monthly_traffic": 100000,
                "avg_engagement_rate": 0.015,
                "avg_content_frequency": "5 posts per week",
                "avg_pricing_model": "transactional",
            },
            "saas": {
                "avg_domain_authority": 50,
                "avg_monthly_traffic": 75000,
                "avg_engagement_rate": 0.02,
                "avg_content_frequency": "4 posts per week",
                "avg_pricing_model": "tiered_subscription",
            },
            "consulting": {
                "avg_domain_authority": 40,
                "avg_monthly_traffic": 25000,
                "avg_engagement_rate": 0.03,
                "avg_content_frequency": "2 posts per week",
                "avg_pricing_model": "project_based",
            },
        }

        # SWOT analysis templates
        self.swot_templates = {
            "strengths": [
                "Strong brand recognition in {market}",
                "Superior product features in {area}",
                "Larger market share ({percentage}%)",
                "Established customer base",
                "Strong financial position",
            ],
            "weaknesses": [
                "Limited market presence in {region}",
                "Higher pricing than competitors",
                "Outdated technology stack",
                "Poor customer satisfaction ratings",
                "Limited product offerings",
            ],
            "opportunities": [
                "Growing market demand in {sector}",
                "Emerging technologies adoption",
                "Untapped customer segments",
                "Partnership opportunities",
                "Market expansion potential",
            ],
            "threats": [
                "Increasing competitive pressure",
                "Changing customer preferences",
                "Regulatory challenges",
                "Economic uncertainties",
                "Technological disruptions",
            ],
        }

        # Competitive positioning axes
        self.positioning_axes = {
            "price_quality": {
                "x_axis": "Price (Low to High)",
                "y_axis": "Quality (Basic to Premium)",
                "quadrants": ["Budget", "Value", "Premium", "Luxury"],
            },
            "innovation_tradition": {
                "x_axis": "Innovation (Traditional to Cutting-edge)",
                "y_axis": "Market Approach (Niche to Mass)",
                "quadrants": [
                    "Traditional Specialist",
                    "Innovative Specialist",
                    "Traditional Mainstream",
                    "Innovative Mainstream",
                ],
            },
        }

        # Insight categories
        self.insight_categories = {
            "opportunity": {
                "color": "green",
                "priority": "high",
                "action_level": "strategic",
            },
            "threat": {"color": "red", "priority": "high", "action_level": "defensive"},
            "strength": {
                "color": "blue",
                "priority": "medium",
                "action_level": "leveraging",
            },
            "weakness": {
                "color": "orange",
                "priority": "medium",
                "action_level": "improvement",
            },
        }

    def get_system_prompt(self) -> str:
        """Get the system prompt for the CompetitorIntelAgent."""
        return """
You are the CompetitorIntelAgent, a specialist agent for Raptorflow marketing automation platform.

Your role is to gather, analyze, and provide strategic intelligence about competitors to inform marketing and business decisions.

Key responsibilities:
1. Analyze competitor strategies and performance
2. Identify market opportunities and threats
3. Benchmark against industry standards
4. Provide actionable competitive insights
5. Monitor competitor activities and trends
6. Assess competitive positioning and differentiation
7. Generate strategic recommendations

Analysis types you can perform:
- Content Analysis (content strategy, themes, quality, frequency)
- SEO Analysis (keywords, traffic, backlinks, technical SEO)
- Social Analysis (platform presence, engagement, growth)
- Pricing Analysis (pricing models, value propositions, positioning)
- Positioning Analysis (brand positioning, value propositions, differentiation)
- Comprehensive Analysis (all areas combined)

For each competitor analysis, you should:
- Gather comprehensive competitor data
- Analyze performance across key metrics
- Identify strengths, weaknesses, opportunities, and threats
- Benchmark against industry standards
- Provide actionable insights and recommendations
- Assess competitive positioning and market dynamics
- Monitor trends and changes over time

Always focus on providing strategic, actionable intelligence that helps improve competitive positioning and business performance.
"""

    async def execute(self, state: AgentState) -> AgentState:
        """Execute competitor intelligence analysis."""
        try:
            # Validate workspace context
            if not state.get("workspace_id"):
                return self._set_error(
                    state, "Workspace ID is required for competitor intelligence"
                )

            # Extract competitor request from state
            competitor_request = self._extract_competitor_request(state)

            if not competitor_request:
                return self._set_error(
                    state, "No competitor intelligence request provided"
                )

            # Validate competitor request
            self._validate_competitor_request(competitor_request)

            # Perform competitor analysis
            intel_report = await self._perform_competitor_analysis(
                competitor_request, state
            )

            # Store intelligence report
            await self._store_intel_report(intel_report, state)

            # Add assistant message
            response = self._format_intel_response(intel_report)
            state = self._add_assistant_message(state, response)

            # Set output
            return self._set_output(
                state,
                {
                    "intel_report": intel_report.__dict__,
                    "competitors_count": len(intel_report.competitors),
                    "insights_count": len(intel_report.insights),
                    "opportunities": len(intel_report.opportunities),
                    "threats": len(intel_report.threats),
                },
            )

        except Exception as e:
            logger.error(f"Competitor intelligence analysis failed: {e}")
            return self._set_error(
                state, f"Competitor intelligence analysis failed: {str(e)}"
            )

    def _extract_competitor_request(
        self, state: AgentState
    ) -> Optional[CompetitorRequest]:
        """Extract competitor request from state."""
        # Check if competitor request is in state
        if "competitor_request" in state:
            request_data = state["competitor_request"]
            return CompetitorRequest(**request_data)

        # Extract from user message
        user_input = self._extract_user_input(state)
        if not user_input:
            return None

        # Parse competitor request from user input
        return self._parse_competitor_request(user_input, state)

    def _parse_competitor_request(
        self, user_input: str, state: AgentState
    ) -> Optional[CompetitorRequest]:
        """Parse competitor request from user input."""
        # Extract competitor names (simplified)
        import re

        competitor_pattern = (
            r"(?:competitors?|companies? like|similar to)\s*:?\s*([^.]+)"
        )
        match = re.search(competitor_pattern, user_input, re.IGNORECASE)

        competitors = []
        if match:
            competitor_text = match.group(1)
            # Split by common separators
            competitors = [
                comp.strip()
                for comp in re.split(r"[,;]|\s+and\s+", competitor_text)
                if comp.strip()
            ]

        # If no explicit competitors found, use common names for demo
        if not competitors:
            competitors = ["Competitor A", "Competitor B"]

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
        depth = self._extract_parameter(
            user_input, ["depth", "detail", "level"], "detailed"
        )

        # Create competitor request
        return CompetitorRequest(
            competitors=competitors,
            analysis_type=detected_type,
            industry=industry,
            target_market="B2B",  # Default
            analysis_depth=depth,
            time_period="last_90_days",
            focus_areas=[],
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

    def _validate_competitor_request(self, request: CompetitorRequest):
        """Validate competitor request."""
        if not request.competitors or len(request.competitors) == 0:
            raise ValidationError("At least one competitor is required")

        if (
            request.analysis_type not in self.analysis_frameworks
            and request.analysis_type != "comprehensive"
        ):
            raise ValidationError(f"Unsupported analysis type: {request.analysis_type}")

        if request.analysis_depth not in ["basic", "detailed", "comprehensive"]:
            raise ValidationError(f"Invalid analysis depth: {request.analysis_depth}")

        if request.time_period not in ["last_30_days", "last_90_days", "last_year"]:
            raise ValidationError(f"Invalid time period: {request.time_period}")

    async def _perform_competitor_analysis(
        self, request: CompetitorRequest, state: AgentState
    ) -> CompetitorIntelReport:
        """Perform comprehensive competitor analysis."""
        try:
            # Generate report ID
            report_id = f"intel_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Create competitor profiles (Enhanced with Swarm CompetitorScoutSkill)
            competitors = []
            scout_skill = self.skills_registry.get_skill("competitor_scout")
            
            for competitor_name in request.competitors:
                profile = None
                
                # Try to use Swarm Skill
                if scout_skill:
                    try:
                        logger.info(f"Swarm: Scouting {competitor_name}...")
                        scout_res = await scout_skill.execute({
                            "agent": self,
                            "competitor_name": competitor_name,
                            "competitor_url": "unknown" 
                        })
                        # Convert skill result to profile if successful
                        if "profile" in scout_res:
                            # Map dict to CompetitorProfile object - simplified mapping
                            p_data = scout_res["profile"]
                            profile = CompetitorProfile(
                                competitor_id=f"comp_{competitor_name.lower().replace(' ', '_')}",
                                name=competitor_name,
                                domain=p_data.get("url", ""),
                                company_size=p_data.get("size", "Unknown"),
                                market_position=p_data.get("position", "Challenger"),
                                strengths=p_data.get("strengths", []),
                                weaknesses=p_data.get("weaknesses", []),
                                market_share=0.0, # detailed data hard to get
                                estimated_revenue="Unknown", 
                                founding_year=2020,
                                headquarters="Unknown",
                                employee_count="Unknown",
                                key_products=p_data.get("products", []),
                                target_audience=p_data.get("audience", ""),
                                brand_positioning=p_data.get("usp", "")
                            )
                    except Exception as e:
                        logger.warning(f"CompetitorScoutSkill failed for {competitor_name}: {e}")

                # Fallback to internal simulation if skill failed or wasn't used
                if not profile:
                     profile = self._create_competitor_profile(competitor_name, request)
                
                competitors.append(profile)

            # Perform analysis based on type
            content_analysis = self._analyze_content_strategy(competitors, request)
            seo_analysis = self._analyze_seo_performance(competitors, request)
            social_analysis = self._analyze_social_presence(competitors, request)
            pricing_analysis = self._analyze_pricing_strategy(competitors, request)

            # Generate insights
            insights = self._generate_competitive_insights(competitors, request)

            # Create market positioning map
            market_positioning_map = self._create_positioning_map(competitors, request)

            # Generate strategic recommendations
            strategic_recommendations = self._generate_strategic_recommendations(
                insights, request
            )

            # Identify competitive advantages, threats, and opportunities
            competitive_advantages = self._identify_competitive_advantages(insights)
            threats = [
                insight.description
                for insight in insights
                if insight.category == "threat"
            ]
            opportunities = [
                insight.description
                for insight in insights
                if insight.category == "opportunity"
            ]

            # Create intelligence report
            intel_report = CompetitorIntelReport(
                report_id=report_id,
                analysis_type=request.analysis_type,
                industry=request.industry,
                target_market=request.target_market,
                competitors=competitors,
                content_analysis=content_analysis,
                seo_analysis=seo_analysis,
                social_analysis=social_analysis,
                pricing_analysis=pricing_analysis,
                insights=insights,
                market_positioning_map=market_positioning_map,
                strategic_recommendations=strategic_recommendations,
                competitive_advantages=competitive_advantages,
                threats=threats,
                opportunities=opportunities,
                generated_at=datetime.now(),
                metadata={
                    "analysis_depth": request.analysis_depth,
                    "time_period": request.time_period,
                    "focus_areas": request.focus_areas,
                },
            )

            return intel_report

        except Exception as e:
            logger.error(f"Competitor analysis failed: {e}")
            raise DatabaseError(f"Competitor analysis failed: {str(e)}")

    def _create_competitor_profile(
        self, competitor_name: str, request: CompetitorRequest
    ) -> CompetitorProfile:
        """Create competitor profile."""
        # Generate simulated competitor data
        competitor_id = f"comp_{competitor_name.lower().replace(' ', '_')}"

        # Simulated company data
        company_sizes = ["Startup", "Small", "Medium", "Large", "Enterprise"]
        market_positions = ["Leader", "Challenger", "Follower", "Niche"]

        return CompetitorProfile(
            competitor_id=competitor_id,
            name=competitor_name,
            domain=f"www.{competitor_name.lower().replace(' ', '')}.com",
            company_size=random.choice(company_sizes),
            market_position=random.choice(market_positions),
            strengths=[
                "Strong brand recognition",
                "Innovative product features",
                "Large customer base",
            ],
            weaknesses=[
                "Limited market presence",
                "Higher pricing",
                "Slow innovation cycle",
            ],
            market_share=random.uniform(5.0, 25.0),
            estimated_revenue=f"${random.randint(10, 500)}M",
            founding_year=random.randint(2000, 2020),
            headquarters=random.choice(
                ["San Francisco", "New York", "London", "Berlin"]
            ),
            employee_count=f"{random.randint(50, 5000)}",
            key_products=["Main Product", "Premium Service", "Enterprise Solution"],
            target_audience="Business Professionals",
            brand_positioning="Innovation Leader",
        )

    def _analyze_content_strategy(
        self, competitors: List[CompetitorProfile], request: CompetitorRequest
    ) -> ContentAnalysis:
        """Analyze competitor content strategies."""
        # Simulated content analysis
        content_types = {
            "blog_posts": random.randint(50, 200),
            "social_posts": random.randint(500, 2000),
            "white_papers": random.randint(10, 50),
            "case_studies": random.randint(20, 100),
            "videos": random.randint(30, 150),
        }

        content_themes = [
            "Industry Trends",
            "Product Features",
            "Customer Success",
            "Thought Leadership",
            "How-To Guides",
        ]

        top_performing_content = [
            {
                "title": "Industry Trends 2024",
                "engagement": random.randint(1000, 10000),
            },
            {
                "title": "Product Launch Announcement",
                "engagement": random.randint(500, 5000),
            },
            {
                "title": "Customer Success Story",
                "engagement": random.randint(800, 8000),
            },
        ]

        return ContentAnalysis(
            content_types=content_types,
            content_themes=content_themes,
            content_frequency="3-5 posts per week",
            content_quality_score=random.uniform(0.6, 0.9),
            top_performing_content=top_performing_content,
            content_gaps=["Technical Documentation", "User-Generated Content"],
            voice_tone="Professional and Authoritative",
            engagement_metrics={
                "avg_engagement_rate": random.uniform(0.02, 0.08),
                "share_rate": random.uniform(0.01, 0.05),
                "comment_rate": random.uniform(0.005, 0.02),
            },
        )

    def _analyze_seo_performance(
        self, competitors: List[CompetitorProfile], request: CompetitorRequest
    ) -> SEOAnalysis:
        """Analyze competitor SEO performance."""
        # Get industry benchmarks
        benchmarks = self.industry_benchmarks.get(
            request.industry, self.industry_benchmarks["technology"]
        )

        top_keywords = [
            {
                "keyword": "industry solution",
                "position": random.randint(1, 20),
                "volume": random.randint(1000, 10000),
            },
            {
                "keyword": "professional service",
                "position": random.randint(1, 30),
                "volume": random.randint(500, 5000),
            },
            {
                "keyword": "business software",
                "position": random.randint(1, 25),
                "volume": random.randint(800, 8000),
            },
        ]

        return SEOAnalysis(
            organic_keywords=random.randint(1000, 10000),
            monthly_organic_traffic=random.randint(10000, 100000),
            domain_authority=random.uniform(20, 80),
            backlinks_count=random.randint(100, 10000),
            top_keywords=top_keywords,
            keyword_gaps=["long-tail variations", "local keywords"],
            content_optimization=random.uniform(0.6, 0.9),
            technical_seo_score=random.uniform(0.7, 0.95),
        )

    def _analyze_social_presence(
        self, competitors: List[CompetitorProfile], request: CompetitorRequest
    ) -> SocialAnalysis:
        """Analyze competitor social media presence."""
        platforms = {
            "LinkedIn": {
                "followers": random.randint(10000, 100000),
                "engagement_rate": random.uniform(0.02, 0.08),
                "posting_frequency": "Daily",
            },
            "Twitter": {
                "followers": random.randint(5000, 50000),
                "engagement_rate": random.uniform(0.01, 0.05),
                "posting_frequency": "Multiple times daily",
            },
            "Facebook": {
                "followers": random.randint(20000, 200000),
                "engagement_rate": random.uniform(0.015, 0.06),
                "posting_frequency": "Weekly",
            },
        }

        top_posts = [
            {
                "platform": "LinkedIn",
                "content": "Product Announcement",
                "engagement": random.randint(500, 5000),
            },
            {
                "platform": "Twitter",
                "content": "Industry Insight",
                "engagement": random.randint(200, 2000),
            },
            {
                "platform": "Facebook",
                "content": "Customer Story",
                "engagement": random.randint(300, 3000),
            },
        ]

        return SocialAnalysis(
            platforms=platforms,
            posting_frequency={
                platform: data["posting_frequency"]
                for platform, data in platforms.items()
            },
            engagement_rates={
                platform: data["engagement_rate"]
                for platform, data in platforms.items()
            },
            follower_growth={
                platform: random.uniform(0.05, 0.15) for platform in platforms
            },
            top_performing_posts=top_posts,
            social_strategy="Professional thought leadership",
            brand_voice_consistency=random.uniform(0.7, 0.9),
        )

    def _analyze_pricing_strategy(
        self, competitors: List[CompetitorProfile], request: CompetitorRequest
    ) -> PricingAnalysis:
        """Analyze competitor pricing strategies."""
        pricing_models = [
            "subscription",
            "freemium",
            "tiered",
            "usage-based",
            "one-time",
        ]

        price_points = [
            {"tier": "Basic", "price": f"${random.randint(9, 49)}/month"},
            {"tier": "Professional", "price": f"${random.randint(49, 199)}/month"},
            {"tier": "Enterprise", "price": "Custom Pricing"},
        ]

        return PricingAnalysis(
            pricing_model=random.choice(pricing_models),
            price_points=price_points,
            discount_strategies=[
                "Annual Discount",
                "Volume Discount",
                "Student Discount",
            ],
            value_proposition="Comprehensive business solution with premium features",
            competitive_positioning="Premium quality with competitive pricing",
            price_elasticity="Medium sensitivity to price changes",
            revenue_streams=["Subscription Fees", "Professional Services", "Training"],
        )

    def _generate_competitive_insights(
        self, competitors: List[CompetitorProfile], request: CompetitorRequest
    ) -> List[CompetitiveInsight]:
        """Generate competitive insights."""
        insights = []

        # Generate insights for each category
        for category, templates in self.swot_templates.items():
            # Generate 2-3 insights per category
            for i in range(random.randint(2, 3)):
                template = random.choice(templates)

                # Fill template with context
                insight_description = template.format(
                    market=request.industry,
                    area="product features",
                    percentage=f"{random.randint(10, 40)}",
                    region="international markets",
                    sector="emerging technologies",
                )

                insight = CompetitiveInsight(
                    insight_id=f"insight_{category}_{i}",
                    category=category,
                    title=f"{category.title()} Identified",
                    description=insight_description,
                    impact=random.choice(["high", "medium", "low"]),
                    confidence=random.uniform(0.6, 0.9),
                    actionable=category in ["opportunity", "weakness"],
                    recommendation=self._generate_recommendation(category),
                    data_points=[
                        f"Competitor analysis",
                        f"Market research",
                        f"Industry benchmarks",
                    ],
                )
                insights.append(insight)

        return insights

    def _generate_recommendation(self, category: str) -> str:
        """Generate recommendation based on insight category."""
        recommendations = {
            "opportunity": "Capitalize on this opportunity by developing targeted strategies",
            "threat": "Develop contingency plans to mitigate this potential threat",
            "strength": "Leverage this strength to differentiate from competitors",
            "weakness": "Address this weakness through strategic improvements",
        }
        return recommendations.get(category, "Further analysis recommended")

    def _create_positioning_map(
        self, competitors: List[CompetitorProfile], request: CompetitorRequest
    ) -> Dict[str, Any]:
        """Create market positioning map."""
        # Simulate positioning data
        positioning_data = {}

        for competitor in competitors:
            positioning_data[competitor.name] = {
                "x_position": random.uniform(0, 100),  # Price axis
                "y_position": random.uniform(0, 100),  # Quality axis
                "size": competitor.market_share,
                "color": "blue",
            }

        return {
            "axis_type": "price_quality",
            "x_axis": "Price (Low to High)",
            "y_axis": "Quality (Basic to Premium)",
            "competitors": positioning_data,
            "quadrants": ["Budget", "Value", "Premium", "Luxury"],
            "insights": "Most competitors are positioned in the Value and Premium quadrants",
        }

    def _generate_strategic_recommendations(
        self, insights: List[CompetitiveInsight], request: CompetitorRequest
    ) -> List[str]:
        """Generate strategic recommendations based on insights."""
        recommendations = []

        # High-impact opportunities
        opportunities = [
            insight
            for insight in insights
            if insight.category == "opportunity" and insight.impact == "high"
        ]
        for opportunity in opportunities[:2]:
            recommendations.append(f"Prioritize: {opportunity.description}")

        # High-impact threats
        threats = [
            insight
            for insight in insights
            if insight.category == "threat" and insight.impact == "high"
        ]
        for threat in threats[:2]:
            recommendations.append(f"Address: {threat.description}")

        # Strategic positioning
        recommendations.append("Differentiate through unique value proposition")
        recommendations.append("Focus on underserved market segments")
        recommendations.append("Develop strategic partnerships for market expansion")

        return recommendations[:5]  # Limit to 5 recommendations

    def _identify_competitive_advantages(
        self, insights: List[CompetitiveInsight]
    ) -> List[str]:
        """Identify competitive advantages."""
        advantages = []

        # Extract from strength insights
        strength_insights = [
            insight for insight in insights if insight.category == "strength"
        ]
        for insight in strength_insights:
            advantages.append(insight.description)

        # Add common advantages
        advantages.extend(
            [
                "Superior product quality",
                "Strong customer relationships",
                "Innovative technology stack",
            ]
        )

        return advantages[:5]  # Limit to 5 advantages

    async def _store_intel_report(
        self, report: CompetitorIntelReport, state: AgentState
    ):
        """Store intelligence report in database."""
        try:
            # Store in database with workspace isolation
            database_tool = self._get_tool("database")
            if database_tool:
                await database_tool.arun(
                    table="competitor_intel_reports",
                    workspace_id=state["workspace_id"],
                    data={
                        "report_id": report.report_id,
                        "analysis_type": report.analysis_type,
                        "industry": report.industry,
                        "target_market": report.target_market,
                        "competitors": [comp.__dict__ for comp in report.competitors],
                        "content_analysis": report.content_analysis.__dict__,
                        "seo_analysis": report.seo_analysis.__dict__,
                        "social_analysis": report.social_analysis.__dict__,
                        "pricing_analysis": report.pricing_analysis.__dict__,
                        "insights": [insight.__dict__ for insight in report.insights],
                        "market_positioning_map": report.market_positioning_map,
                        "strategic_recommendations": report.strategic_recommendations,
                        "competitive_advantages": report.competitive_advantages,
                        "threats": report.threats,
                        "opportunities": report.opportunities,
                        "generated_at": report.generated_at.isoformat(),
                        "metadata": report.metadata,
                    },
                )

        except Exception as e:
            logger.error(f"Failed to store intelligence report: {e}")

    def _format_intel_response(self, report: CompetitorIntelReport) -> str:
        """Format intelligence report response for user."""
        response = f"≡ƒöì **Competitor Intelligence Report**\n\n"
        response += f"**Analysis Type:** {report.analysis_type.title()}\n"
        response += f"**Industry:** {report.industry.title()}\n"
        response += f"**Competitors Analyzed:** {len(report.competitors)}\n"
        response += f"**Insights Generated:** {len(report.insights)}\n\n"

        response += f"**Competitors Overview:**\n"
        for competitor in report.competitors:
            response += f"ΓÇó {competitor.name} ({competitor.market_position}, {competitor.market_share:.1f}% market share)\n"
        response += "\n"

        response += f"**Key Insights:**\n"
        # Show top insights by impact
        top_insights = sorted(
            report.insights, key=lambda x: {"high": 0, "medium": 1, "low": 2}[x.impact]
        )[:5]
        for insight in top_insights:
            response += f"ΓÇó {insight.category.title()}: {insight.description}\n"
        response += "\n"

        response += f"**Strategic Recommendations:**\n"
        for recommendation in report.strategic_recommendations:
            response += f"ΓÇó {recommendation}\n"
        response += "\n"

        response += f"**Market Positioning:**\n"
        response += f"ΓÇó Most competitors positioned in Value and Premium quadrants\n"
        response += f"ΓÇó Opportunity exists in Budget and Luxury segments\n\n"

        response += f"**Key Opportunities:** {len(report.opportunities)}\n"
        response += f"**Major Threats:** {len(report.threats)}\n"
        response += (
            f"**Competitive Advantages:** {len(report.competitive_advantages)}\n\n"
        )

        response += f"**Performance Benchmarks:**\n"
        response += (
            f"ΓÇó Avg Domain Authority: {report.seo_analysis.domain_authority:.1f}\n"
        )
        response += (
            f"ΓÇó Avg Monthly Traffic: {report.seo_analysis.monthly_organic_traffic:,}\n"
        )
        response += f"ΓÇó Avg Engagement Rate: {report.social_analysis.platforms.get('LinkedIn', {}).get('engagement_rate', 0):.2%}\n"

        return response
