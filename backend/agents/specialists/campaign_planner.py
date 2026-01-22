"""
CampaignPlanner specialist agent for Raptorflow marketing automation.
Handles comprehensive campaign planning, execution, and optimization.
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from ..base import BaseAgent
from backend.agents.config import ModelTier
from ..exceptions import DatabaseError, ValidationError
from ..state import AgentState, add_message, update_state

logger = logging.getLogger(__name__)


class CampaignType(Enum):
    """Types of marketing campaigns."""

    AWARENESS = "awareness"
    LEAD_GENERATION = "lead_generation"
    CONVERSION = "conversion"
    RETENTION = "retention"
    LAUNCH = "launch"
    PROMOTION = "promotion"
    BRAND_BUILDING = "brand_building"
    EVENT = "event"


class CampaignStatus(Enum):
    """Campaign status states."""

    PLANNING = "planning"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class CampaignObjective:
    """Campaign objective definition."""

    primary_goal: str
    secondary_goals: List[str]
    success_metrics: List[str]
    target_kpis: Dict[str, float]
    success_criteria: str


@dataclass
class CampaignBudget:
    """Campaign budget allocation."""

    total_budget: float
    currency: str
    allocation: Dict[str, float]  # channel -> amount
    daily_spend_limit: float
    cost_per_acquisition_target: float


@dataclass
class CampaignTimeline:
    """Campaign timeline and milestones."""

    start_date: datetime
    end_date: datetime
    duration_days: int
    milestones: List[Dict[str, Any]]
    review_points: List[datetime]


@dataclass
class CampaignAudience:
    """Campaign target audience definition."""

    primary_audience: str
    secondary_audiences: List[str]
    audience_size: int
    demographics: Dict[str, Any]
    psychographics: Dict[str, Any]
    custom_segments: List[str]


@dataclass
class CampaignChannel:
    """Campaign channel configuration."""

    channel_name: str
    enabled: bool
    budget_allocation: float
    targeting_config: Dict[str, Any]
    creative_requirements: List[str]
    optimization_settings: Dict[str, Any]


@dataclass
class CampaignPlan:
    """Complete campaign plan."""

    name: str
    description: str
    campaign_type: CampaignType
    status: CampaignStatus
    objective: CampaignObjective
    budget: CampaignBudget
    timeline: CampaignTimeline
    audience: CampaignAudience
    channels: List[CampaignChannel]
    content_strategy: Dict[str, Any]
    measurement_plan: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]


class CampaignPlanner(BaseAgent):
    """Specialist agent for comprehensive campaign planning."""

    def __init__(self):
        super().__init__(
            name="CampaignPlanner",
            description="Plans and manages comprehensive marketing campaigns",
            model_tier=ModelTier.FLASH,
            tools=["web_search", "database", "content_gen"],
        )

        # Campaign type templates
        self.campaign_templates = {
            CampaignType.AWARENESS: {
                "typical_duration": 30,
                "primary_channels": ["social", "display", "content"],
                "success_metrics": [
                    "impressions",
                    "reach",
                    "brand_awareness",
                    "share_of_voice",
                ],
                "budget_allocation": {"social": 0.4, "display": 0.3, "content": 0.3},
                "typical_kpis": {"cpm": 10, "reach": 100000, "frequency": 3},
            },
            CampaignType.LEAD_GENERATION: {
                "typical_duration": 21,
                "primary_channels": ["paid_search", "social", "email", "landing_pages"],
                "success_metrics": ["leads", "conversion_rate", "cpl", "mql_count"],
                "budget_allocation": {
                    "paid_search": 0.4,
                    "social": 0.3,
                    "email": 0.2,
                    "landing_pages": 0.1,
                },
                "typical_kpis": {
                    "cpl": 50,
                    "conversion_rate": 0.02,
                    "lead_quality": 0.7,
                },
            },
            CampaignType.CONVERSION: {
                "typical_duration": 14,
                "primary_channels": ["email", "retargeting", "landing_pages", "social"],
                "success_metrics": ["conversions", "revenue", "conversion_rate", "aov"],
                "budget_allocation": {
                    "email": 0.3,
                    "retargeting": 0.4,
                    "landing_pages": 0.2,
                    "social": 0.1,
                },
                "typical_kpis": {"conversion_rate": 0.03, "aov": 150, "roas": 3.0},
            },
            CampaignType.RETENTION: {
                "typical_duration": 60,
                "primary_channels": ["email", "social", "content", "loyalty"],
                "success_metrics": [
                    "retention_rate",
                    "repeat_purchases",
                    "clv",
                    "engagement",
                ],
                "budget_allocation": {
                    "email": 0.4,
                    "social": 0.2,
                    "content": 0.2,
                    "loyalty": 0.2,
                },
                "typical_kpis": {
                    "retention_rate": 0.8,
                    "repeat_purchase_rate": 0.3,
                    "engagement_rate": 0.6,
                },
            },
            CampaignType.LAUNCH: {
                "typical_duration": 45,
                "primary_channels": ["pr", "social", "email", "influencers", "events"],
                "success_metrics": [
                    "awareness",
                    "adoption",
                    "reviews",
                    "media_mentions",
                ],
                "budget_allocation": {
                    "pr": 0.3,
                    "social": 0.3,
                    "email": 0.2,
                    "influencers": 0.1,
                    "events": 0.1,
                },
                "typical_kpis": {
                    "media_mentions": 50,
                    "adoption_rate": 0.05,
                    "review_count": 100,
                },
            },
            CampaignType.PROMOTION: {
                "typical_duration": 7,
                "primary_channels": ["email", "social", "paid_ads", "website"],
                "success_metrics": [
                    "sales",
                    "redemptions",
                    "traffic",
                    "conversion_rate",
                ],
                "budget_allocation": {
                    "email": 0.3,
                    "social": 0.3,
                    "paid_ads": 0.3,
                    "website": 0.1,
                },
                "typical_kpis": {
                    "conversion_rate": 0.05,
                    "redemption_rate": 0.15,
                    "sales_lift": 0.2,
                },
            },
        }

        # Channel configurations
        self.channel_configs = {
            "social": {
                "platforms": ["facebook", "instagram", "linkedin", "twitter"],
                "ad_formats": ["image", "video", "carousel", "story"],
                "targeting_options": [
                    "demographics",
                    "interests",
                    "behaviors",
                    "custom_audiences",
                ],
                "optimization_goals": [
                    "impressions",
                    "clicks",
                    "conversions",
                    "engagement",
                ],
            },
            "email": {
                "platforms": ["mailchimp", "constant_contact", "sendgrid"],
                "formats": ["newsletter", "promotional", "transactional", "automation"],
                "segmentation_options": [
                    "demographics",
                    "behavior",
                    "purchase_history",
                    "engagement",
                ],
                "optimization_goals": [
                    "open_rate",
                    "click_rate",
                    "conversion_rate",
                    "unsubscribe_rate",
                ],
            },
            "paid_search": {
                "platforms": ["google_ads", "bing_ads"],
                "ad_types": ["search", "display", "shopping", "video"],
                "targeting_options": ["keywords", "demographics", "location", "time"],
                "optimization_goals": ["clicks", "conversions", "quality_score", "cpc"],
            },
            "content": {
                "platforms": ["blog", "website", "medium", "industry_publications"],
                "formats": [
                    "blog_post",
                    "article",
                    "whitepaper",
                    "case_study",
                    "infographic",
                ],
                "distribution_options": ["seo", "social", "email", "syndication"],
                "optimization_goals": [
                    "traffic",
                    "engagement",
                    "leads",
                    "seo_rankings",
                ],
            },
            "display": {
                "platforms": ["google_display", "programmatic", "direct"],
                "ad_formats": ["banner", "video", "rich_media", "native"],
                "targeting_options": [
                    "contextual",
                    "behavioral",
                    "demographic",
                    "retargeting",
                ],
                "optimization_goals": [
                    "impressions",
                    "clicks",
                    "conversions",
                    "viewability",
                ],
            },
        }

        # Risk factors
        self.risk_factors = {
            "budget_overrun": {
                "probability": 0.3,
                "impact": "high",
                "mitigation": "Daily spend monitoring",
            },
            "low_performance": {
                "probability": 0.4,
                "impact": "medium",
                "mitigation": "A/B testing and optimization",
            },
            "technical_issues": {
                "probability": 0.2,
                "impact": "medium",
                "mitigation": "Pre-launch testing",
            },
            "competitive_response": {
                "probability": 0.3,
                "impact": "medium",
                "mitigation": "Competitive monitoring",
            },
            "audience_fatigue": {
                "probability": 0.4,
                "impact": "medium",
                "mitigation": "Frequency capping and creative rotation",
            },
            "seasonal_factors": {
                "probability": 0.2,
                "impact": "low",
                "mitigation": "Seasonal trend analysis",
            },
        }

    def get_system_prompt(self) -> str:
        """Get the system prompt for the CampaignPlanner."""
        return """
You are the CampaignPlanner, a specialist agent for Raptorflow marketing automation platform.

Your role is to create comprehensive, data-driven campaign plans that achieve specific marketing objectives.

Key responsibilities:
1. Analyze campaign requirements and business objectives
2. Develop multi-channel campaign strategies
3. Define clear success metrics and KPIs
4. Plan budget allocation and timeline
5. Identify target audiences and segmentation
6. Assess risks and create mitigation strategies
7. Provide actionable implementation steps

Campaign types you can plan:
- Awareness campaigns (brand visibility, reach)
- Lead generation campaigns (prospects, MQLs)
- Conversion campaigns (sales, revenue)
- Retention campaigns (customer loyalty, CLV)
- Launch campaigns (product releases, go-to-market)
- Promotion campaigns (sales, discounts, offers)
- Brand building campaigns (long-term brand equity)
- Event campaigns (webinars, conferences, product events)

For each campaign, you should:
- Define clear objectives and success criteria
- Select appropriate channels and tactics
- Plan budget allocation across channels
- Create detailed timeline with milestones
- Identify target audiences with segmentation
- Set measurable KPIs and targets
- Assess risks and mitigation strategies
- Provide content strategy recommendations
- Define measurement and optimization approach

Always focus on creating practical, executable campaigns that align with business goals and available resources. Consider the competitive landscape and market conditions in your recommendations.
"""

    async def execute(self, state: AgentState) -> AgentState:
        """Execute campaign planning."""
        try:
            # Validate workspace context
            if not state.get("workspace_id"):
                return self._set_error(
                    state, "Workspace ID is required for campaign planning"
                )

            # Extract campaign request from state
            campaign_request = self._extract_campaign_request(state)

            if not campaign_request:
                return self._set_error(state, "No campaign request provided")

            # Validate campaign request
            self._validate_campaign_request(campaign_request)

            # Generate campaign plan
            campaign_plan = await self._generate_campaign_plan(campaign_request, state)

            # Store campaign plan
            await self._store_campaign_plan(campaign_plan, state)

            # Add assistant message
            response = self._format_campaign_response(campaign_plan)
            state = self._add_assistant_message(state, response)

            # Set output
            return self._set_output(
                state,
                {
                    "campaign_plan": campaign_plan.__dict__,
                    "campaign_type": campaign_plan.campaign_type.value,
                    "campaign_name": campaign_plan.name,
                    "duration_days": campaign_plan.timeline.duration_days,
                    "total_budget": campaign_plan.budget.total_budget,
                    "primary_channels": [
                        c.channel_name for c in campaign_plan.channels if c.enabled
                    ],
                },
            )

        except Exception as e:
            logger.error(f"Campaign planning failed: {e}")
            return self._set_error(state, f"Campaign planning failed: {str(e)}")

    def _extract_campaign_request(self, state: AgentState) -> Optional[Dict[str, Any]]:
        """Extract campaign request from state."""
        # Check if campaign request is in state
        if "campaign_request" in state:
            return state["campaign_request"]

        # Extract from user message
        user_input = self._extract_user_input(state)
        if not user_input:
            return None

        # Parse campaign request from user input
        return self._parse_campaign_request(user_input, state)

    def _parse_campaign_request(
        self, user_input: str, state: AgentState
    ) -> Dict[str, Any]:
        """Parse campaign request from user input."""
        # Check for explicit campaign type mention
        campaign_types = [t.value for t in CampaignType]
        detected_type = None

        for campaign_type in campaign_types:
            if campaign_type.lower() in user_input.lower():
                detected_type = campaign_type
                break

        if not detected_type:
            # Default to awareness
            detected_type = "awareness"

        # Extract other parameters
        budget = self._extract_parameter(
            user_input, ["budget", "cost", "investment"], 10000
        )
        duration = self._extract_parameter(
            user_input, ["duration", "timeline", "length"], 30
        )
        audience = self._extract_parameter(
            user_input, ["audience", "target", "market"], "general"
        )
        primary_goal = self._extract_parameter(
            user_input, ["goal", "objective", "purpose"], "awareness"
        )

        # Extract channels
        channels = self._extract_channels(user_input)

        # Get context from state
        company_name = state.get("company_name", "")
        industry = state.get("industry", "")
        brand_voice = state.get("brand_voice", "professional")

        return {
            "campaign_type": detected_type,
            "budget": budget,
            "duration": duration,
            "audience": audience,
            "primary_goal": primary_goal,
            "channels": channels,
            "company_name": company_name,
            "industry": industry,
            "brand_voice": brand_voice,
            "user_input": user_input,
        }

    def _extract_parameter(
        self, text: str, param_names: List[str], default: Any
    ) -> Any:
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
                            value = words[0].strip(".,!?")
                            # Try to convert to number
                            try:
                                if "." in value:
                                    return float(value)
                                else:
                                    return int(value)
                            except ValueError:
                                return value
        return default

    def _extract_channels(self, text: str) -> List[str]:
        """Extract marketing channels from text."""
        channel_keywords = {
            "social": ["social", "facebook", "twitter", "instagram", "linkedin"],
            "email": ["email", "newsletter", "mailing"],
            "paid_search": ["search", "google ads", "ppc", "sem"],
            "content": ["content", "blog", "article", "seo"],
            "display": ["display", "banner", "ads"],
            "pr": ["pr", "press", "media"],
            "events": ["events", "webinars", "conferences"],
            "influencers": ["influencers", "influencer marketing"],
        }

        channels = []
        text_lower = text.lower()

        for channel, keywords in channel_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                channels.append(channel)

        return channels or ["social", "email"]  # Default channels

    def _validate_campaign_request(self, request: Dict[str, Any]):
        """Validate campaign request."""
        if request["campaign_type"] not in [t.value for t in CampaignType]:
            raise ValidationError(
                f"Unsupported campaign type: {request['campaign_type']}"
            )

        if request["budget"] <= 0:
            raise ValidationError("Budget must be greater than 0")

        if request["duration"] <= 0:
            raise ValidationError("Duration must be greater than 0")

    async def _generate_campaign_plan(
        self, request: Dict[str, Any], state: AgentState
    ) -> CampaignPlan:
        """Generate campaign plan based on request."""
        try:
            # Get campaign type
            campaign_type = CampaignType(request["campaign_type"])
            template = self.campaign_templates[campaign_type]

            # Generate campaign name
            campaign_name = self._generate_campaign_name(campaign_type, request)

            # Create objective
            objective = self._create_campaign_objective(campaign_type, request)

            # Create budget
            budget = self._create_campaign_budget(request["budget"], template)

            # Create timeline
            timeline = self._create_campaign_timeline(request["duration"], template)

            # Create audience
            audience = self._create_campaign_audience(request, state)

            # Create channels
            channels = self._create_campaign_channels(
                request["channels"], template, budget
            )

            # Create content strategy (Enhanced with Swarm FunnelBlueprint)
            content_strategy = await self._create_content_strategy_with_swarm(campaign_type, request)

            # Create measurement plan
            measurement_plan = self._create_measurement_plan(template, objective)

            # Create risk assessment
            risk_assessment = self._create_risk_assessment(campaign_type, request)

            # Create campaign plan
            campaign_plan = CampaignPlan(
                name=campaign_name,
                description=f"{campaign_type.value.title()} campaign to achieve {request['primary_goal']}",
                campaign_type=campaign_type,
                status=CampaignStatus.PLANNING,
                objective=objective,
                budget=budget,
                timeline=timeline,
                audience=audience,
                channels=channels,
                content_strategy=content_strategy,
                measurement_plan=measurement_plan,
                risk_assessment=risk_assessment,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                metadata={
                    "generated_by": "CampaignPlanner (Swarm Intelligence)",
                    "template_used": template,
                    "request_context": request,
                },
            )
            return campaign_plan

        except Exception as e:
            logger.error(f"Campaign plan generation failed: {e}")
            raise DatabaseError(f"Campaign plan generation failed: {str(e)}")

    def _generate_campaign_name(
        self, campaign_type: CampaignType, request: Dict[str, Any]
    ) -> str:
        """Generate campaign name."""
        company_name = request.get("company_name", "")
        timestamp = datetime.now().strftime("%Y%m%d")

        if company_name:
            return f"{company_name} {campaign_type.value.title()} Campaign {timestamp}"
        else:
            return f"{campaign_type.value.title()} Campaign {timestamp}"

    def _create_campaign_objective(
        self, campaign_type: CampaignType, request: Dict[str, Any]
    ) -> CampaignObjective:
        """Create campaign objective."""
        template = self.campaign_templates[campaign_type]

        primary_goal = request.get("primary_goal", campaign_type.value)
        secondary_goals = template["success_metrics"][
            :3
        ]  # Use first 3 metrics as secondary goals
        success_metrics = template["success_metrics"]
        target_kpis = template["typical_kpis"]

        return CampaignObjective(
            primary_goal=primary_goal,
            secondary_goals=secondary_goals,
            success_metrics=success_metrics,
            target_kpis=target_kpis,
            success_criteria=f"Achieve target KPIs within campaign duration",
        )

    def _create_campaign_budget(
        self, total_budget: float, template: Dict[str, Any]
    ) -> CampaignBudget:
        """Create campaign budget."""
        allocation = {}

        # Allocate budget based on template
        for channel, percentage in template["budget_allocation"].items():
            allocation[channel] = total_budget * percentage

        return CampaignBudget(
            total_budget=total_budget,
            currency="USD",
            allocation=allocation,
            daily_spend_limit=total_budget / template["typical_duration"],
            cost_per_acquisition_target=template["typical_kpis"].get("cpl", 50),
        )

    def _create_campaign_timeline(
        self, duration: int, template: Dict[str, Any]
    ) -> CampaignTimeline:
        """Create campaign timeline."""
        start_date = datetime.now()
        end_date = start_date + timedelta(days=duration)

        # Create milestones
        milestones = [
            {
                "name": "Campaign Launch",
                "date": start_date.isoformat(),
                "description": "Campaign goes live",
            },
            {
                "name": "Mid-Campaign Review",
                "date": (start_date + timedelta(days=duration // 2)).isoformat(),
                "description": "Performance review and optimization",
            },
            {
                "name": "Campaign End",
                "date": end_date.isoformat(),
                "description": "Campaign concludes",
            },
        ]

        # Create review points
        review_points = [
            start_date + timedelta(days=7),
            start_date + timedelta(days=duration // 2),
            start_date + timedelta(days=duration - 7),
        ]

        return CampaignTimeline(
            start_date=start_date,
            end_date=end_date,
            duration_days=duration,
            milestones=milestones,
            review_points=review_points,
        )

    def _create_campaign_audience(
        self, request: Dict[str, Any], state: AgentState
    ) -> CampaignAudience:
        """Create campaign audience."""
        primary_audience = request.get("audience", "general")

        # Get audience size estimate
        audience_size = self._estimate_audience_size(primary_audience, state)

        # Get demographics from context
        demographics = {
            "age_range": "25-55",
            "location": "United States",
            "language": "English",
        }

        # Get psychographics
        psychographics = {
            "interests": ["technology", "business", "innovation"],
            "values": ["efficiency", "growth", "quality"],
            "behaviors": ["online_research", "social_media_engagement"],
        }

        return CampaignAudience(
            primary_audience=primary_audience,
            secondary_audiences=[],
            audience_size=audience_size,
            demographics=demographics,
            psychographics=psychographics,
            custom_segments=[],
        )

    def _estimate_audience_size(self, audience: str, state: AgentState) -> int:
        """Estimate audience size."""
        # Simple estimation based on audience type
        size_estimates = {
            "general": 1000000,
            "b2b": 500000,
            "b2c": 2000000,
            "enterprise": 100000,
            "smb": 300000,
        }

        return size_estimates.get(audience.lower(), 500000)

    def _create_campaign_channels(
        self,
        requested_channels: List[str],
        template: Dict[str, Any],
        budget: CampaignBudget,
    ) -> List[CampaignChannel]:
        """Create campaign channels."""
        channels = []

        # Use template channels if none requested
        if not requested_channels:
            requested_channels = template["primary_channels"]

        for channel_name in requested_channels:
            if channel_name in self.channel_configs:
                channel_config = self.channel_configs[channel_name]

                # Get budget allocation
                budget_allocation = budget.allocation.get(channel_name, 0)

                channel = CampaignChannel(
                    channel_name=channel_name,
                    enabled=True,
                    budget_allocation=budget_allocation,
                    targeting_config=channel_config["targeting_options"],
                    creative_requirements=channel_config["ad_formats"],
                    optimization_settings=channel_config["optimization_goals"],
                )
                channels.append(channel)

        return channels

    def _create_content_strategy(
        self, campaign_type: CampaignType, request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create content strategy."""
        content_types = {
            CampaignType.AWARENESS: [
                "brand_videos",
                "infographics",
                "blog_posts",
                "social_content",
            ],
            CampaignType.LEAD_GENERATION: [
                "landing_pages",
                "ebooks",
                "webinars",
                "case_studies",
            ],
            CampaignType.CONVERSION: [
                "product_demos",
                "testimonials",
                "comparison_guides",
                "offers",
            ],
            CampaignType.RETENTION: [
                "newsletters",
                "loyalty_content",
                "tips",
                "community_content",
            ],
            CampaignType.LAUNCH: [
                "press_releases",
                "launch_videos",
                "demo_content",
                "announcements",
            ],
            CampaignType.PROMOTION: [
                "promo_banners",
                "offer_content",
                "urgency_messaging",
                "social_posts",
            ],
        }

        return {
            "content_types": content_types.get(
                campaign_type, ["blog_posts", "social_content"]
            ),
            "content_frequency": "weekly",
            "content_tone": request.get("brand_voice", "professional"),
            "content_distribution": ["social", "email", "website"],
            "content_calendar": "to_be_developed",
        }


        return {
            "content_types": content_types.get(
                campaign_type, ["blog_posts", "social_content"]
            ),
            "content_frequency": "weekly",
            "content_tone": request.get("brand_voice", "professional"),
            "content_distribution": ["social", "email", "website"],
            "content_calendar": "to_be_developed",
        }

    def _create_measurement_plan(
        self, template: Dict[str, Any], objective: CampaignObjective
    ) -> Dict[str, Any]:
        """Create measurement plan."""
        return {
            "primary_metrics": objective.success_metrics,
            "secondary_metrics": template["success_metrics"],
            "kpis": objective.target_kpis,
            "measurement_frequency": "daily",
            "reporting_schedule": "weekly",
            "optimization_triggers": {
                "low_performance": "below_target_3_days",
                "high_performance": "above_target_2_days",
                "budget_efficiency": "cpa_above_target",
            },
        }

    def _create_risk_assessment(
        self, campaign_type: CampaignType, request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create risk assessment."""
        risks = []
        total_risk_score = 0

        for risk_name, risk_info in self.risk_factors.items():
            # Adjust probability based on campaign type and budget
            adjusted_probability = risk_info["probability"]

            if campaign_type == CampaignType.LAUNCH:
                adjusted_probability *= 1.2  # Higher risk for launches

            if request.get("budget", 0) > 50000:
                adjusted_probability *= 1.1  # Higher risk for large budgets

            risk_score = (
                adjusted_probability
                * {"low": 0.3, "medium": 0.6, "high": 1.0}[risk_info["impact"]]
            )
            total_risk_score += risk_score

            risks.append(
                {
                    "risk": risk_name,
                    "probability": adjusted_probability,
                    "impact": risk_info["impact"],
                    "mitigation": risk_info["mitigation"],
                    "risk_score": risk_score,
                }
            )

        # Sort risks by score
        risks.sort(key=lambda x: x["risk_score"], reverse=True)

        return {
            "overall_risk_score": total_risk_score,
            "risk_level": (
                "high"
                if total_risk_score > 2.0
                else "medium" if total_risk_score > 1.0 else "low"
            ),
            "top_risks": risks[:3],
            "mitigation_strategies": [risk["mitigation"] for risk in risks[:3]],
        }

    async def _store_campaign_plan(
        self, campaign_plan: CampaignPlan, state: AgentState
    ):
        """Store campaign plan in database."""
        try:
            # Store in database with workspace isolation
            database_tool = self._get_tool("database")
            if database_tool:
                await database_tool.arun(
                    table="campaigns",
                    workspace_id=state["workspace_id"],
                    data={
                        "name": campaign_plan.name,
                        "description": campaign_plan.description,
                        "campaign_type": campaign_plan.campaign_type.value,
                        "status": campaign_plan.status.value,
                        "objective": campaign_plan.objective.__dict__,
                        "budget": campaign_plan.budget.__dict__,
                        "timeline": campaign_plan.timeline.__dict__,
                        "audience": campaign_plan.audience.__dict__,
                        "channels": [c.__dict__ for c in campaign_plan.channels],
                        "content_strategy": campaign_plan.content_strategy,
                        "measurement_plan": campaign_plan.measurement_plan,
                        "risk_assessment": campaign_plan.risk_assessment,
                        "created_at": campaign_plan.created_at.isoformat(),
                        "updated_at": campaign_plan.updated_at.isoformat(),
                        "metadata": campaign_plan.metadata,
                    },
                )

        except Exception as e:
            logger.error(f"Failed to store campaign plan: {e}")

    def _format_campaign_response(self, campaign_plan: CampaignPlan) -> str:
        """Format campaign response for user."""
        response = f"≡ƒÜÇ **Campaign Plan Created**\n\n"
        response += f"**Campaign Name:** {campaign_plan.name}\n"
        response += f"**Type:** {campaign_plan.campaign_type.value.title()}\n"
        response += f"**Duration:** {campaign_plan.timeline.duration_days} days\n"
        response += f"**Budget:** ${campaign_plan.budget.total_budget:,.2f}\n"
        response += f"**Status:** {campaign_plan.status.value.title()}\n\n"

        response += f"**Primary Objective:** {campaign_plan.objective.primary_goal}\n"
        response += f"**Success Metrics:** {', '.join(campaign_plan.objective.success_metrics[:3])}\n\n"

        response += f"**Target Audience:** {campaign_plan.audience.primary_audience}\n"
        response += (
            f"**Estimated Audience Size:** {campaign_plan.audience.audience_size:,}\n\n"
        )

        response += f"**Active Channels:**\n"
        for channel in campaign_plan.channels:
            if channel.enabled:
                response += f"ΓÇó {channel.channel_name.title()}: ${channel.budget_allocation:,.2f}\n"

        response += f"\n**Key Milestones:**\n"
        for milestone in campaign_plan.timeline.milestones:
            response += f"ΓÇó {milestone['name']}: {milestone['date'][:10]}\n"

        response += f"\n**Risk Assessment:** {campaign_plan.risk_assessment['risk_level'].title()} Risk\n"
        response += f"**Top Risks:** {', '.join([risk['risk'].replace('_', ' ').title() for risk in campaign_plan.risk_assessment['top_risks'][:2]])}\n"

        return response
