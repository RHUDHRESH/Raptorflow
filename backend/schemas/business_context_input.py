import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, ValidationInfo, field_validator
from schemas.business_context import (
    BrandIdentity,
    BusinessContext,
    ChannelStrategy,
    CompetitivePosition,
    ICPProfile,
    Intelligence,
    MarketPosition,
    MessagingFramework,
    StrategicAudience,
    StrategyPath,
)


class ICPProfileInput(BaseModel):
    name: str = Field(..., min_length=2, description="ICP name")
    description: str = Field(..., min_length=10, description="ICP description")
    company_size: Optional[str] = Field(None, description="Target company size")
    industry: Optional[str] = Field(None, description="Target industry")
    revenue_range: Optional[str] = Field(None, description="Revenue range")
    geographic_focus: List[str] = Field(default_factory=list)
    pain_points: List[str] = Field(default_factory=list)
    value_proposition: str = Field(..., min_length=10)
    priority: int = Field(1, ge=1, le=3)

    @field_validator(
        "geographic_focus",
        "pain_points",
        mode="before",
    )
    @classmethod
    def normalize_list_fields(cls, value):
        if value is None:
            return []
        return [item.strip() for item in value if item and item.strip()]


class ChannelStrategyInput(BaseModel):
    channel: str = Field(..., min_length=2)
    priority: str = Field(..., min_length=2)
    budget_allocation: Optional[float] = Field(None, ge=0, le=100)
    key_metrics: List[str] = Field(default_factory=list)
    tactics: List[str] = Field(default_factory=list)

    @field_validator("key_metrics", "tactics", mode="before")
    @classmethod
    def normalize_list_fields(cls, value):
        if value is None:
            return []
        return [item.strip() for item in value if item and item.strip()]


class BusinessContextInput(BaseModel):
    brand_name: str = Field(..., min_length=2)
    tagline: Optional[str] = Field(None, max_length=120)
    core_promise: str = Field(..., min_length=10)
    mission_statement: Optional[str] = Field(None, max_length=300)
    vision_statement: Optional[str] = Field(None, max_length=300)
    manifesto_summary: str = Field(..., min_length=10)
    values: List[str] = Field(default_factory=list)
    tone_of_voice: List[str] = Field(default_factory=list)
    personality_traits: List[str] = Field(default_factory=list)
    primary_audience: str = Field(..., min_length=5)
    secondary_audiences: List[str] = Field(default_factory=list)
    pain_points: List[str] = Field(default_factory=list)
    desires: List[str] = Field(default_factory=list)
    challenges: List[str] = Field(default_factory=list)
    goals: List[str] = Field(default_factory=list)
    media_consumption: List[str] = Field(default_factory=list)
    decision_factors: List[str] = Field(default_factory=list)
    market_category: str = Field(..., min_length=3)
    market_subcategory: Optional[str] = Field(None, max_length=120)
    differentiator: str = Field(..., min_length=10)
    perceptual_quadrant: str = Field(..., min_length=3)
    strategy_path: StrategyPath
    positioning_statement: str = Field(..., min_length=15)
    messaging_core_message: str = Field(..., min_length=15)
    messaging_value_proposition: str = Field(..., min_length=10)
    messaging_supporting_points: List[str] = Field(default_factory=list)
    messaging_proof_points: List[str] = Field(default_factory=list)
    messaging_call_to_action: str = Field(..., min_length=3)
    messaging_tone_guidelines: List[str] = Field(default_factory=list)
    competitive_market_position: str = Field(..., min_length=8)
    competitive_positioning_statement: str = Field(..., min_length=15)
    primary_competitors: List[str] = Field(default_factory=list)
    competitive_advantages: List[str] = Field(default_factory=list)
    competitive_differentiators: List[str] = Field(default_factory=list)
    icp_profiles: List[ICPProfileInput] = Field(default_factory=list)
    channel_strategies: List[ChannelStrategyInput] = Field(default_factory=list)

    @field_validator(
        "values",
        "tone_of_voice",
        "personality_traits",
        "secondary_audiences",
        "pain_points",
        "desires",
        "challenges",
        "goals",
        "media_consumption",
        "decision_factors",
        "messaging_supporting_points",
        "messaging_proof_points",
        "messaging_tone_guidelines",
        "primary_competitors",
        "competitive_advantages",
        "competitive_differentiators",
        mode="before",
    )
    @classmethod
    def normalize_list_fields(cls, value):
        if value is None:
            return []
        return [item.strip() for item in value if item and item.strip()]

    @field_validator("brand_name")
    @classmethod
    def validate_brand_name(cls, value):
        if not re.match(r"^[a-zA-Z0-9 .,&'-]+$", value):
            raise ValueError("Brand name contains unsupported characters")
        return value.strip()

    @field_validator("pain_points", "desires")
    @classmethod
    def validate_core_lists(cls, value, info: ValidationInfo):
        if len(value) < 2:
            field_name = (info.field_name or "field").replace("_", " ").title()
            raise ValueError(f"{field_name} must include at least 2 items")
        return value

    def to_business_context(self, workspace_id: str, user_id: str) -> BusinessContext:
        ucid = f"bcx_{uuid4().hex}"
        identity = BrandIdentity(
            name=self.brand_name,
            tagline=self.tagline,
            core_promise=self.core_promise,
            mission_statement=self.mission_statement,
            vision_statement=self.vision_statement,
            values=self.values,
            tone_of_voice=self.tone_of_voice,
            manifesto_summary=self.manifesto_summary,
            personality_traits=self.personality_traits,
        )
        audience = StrategicAudience(
            primary_segment=self.primary_audience,
            secondary_segments=self.secondary_audiences,
            pain_points=self.pain_points,
            desires=self.desires,
            challenges=self.challenges,
            goals=self.goals,
            media_consumption=self.media_consumption,
            decision_factors=self.decision_factors,
        )
        positioning = MarketPosition(
            category=self.market_category,
            subcategory=self.market_subcategory,
            differentiator=self.differentiator,
            perceptual_quadrant=self.perceptual_quadrant,
            strategy_path=self.strategy_path,
            positioning_statement=self.positioning_statement,
        )
        messaging = MessagingFramework(
            core_message=self.messaging_core_message,
            value_proposition=self.messaging_value_proposition,
            supporting_points=self.messaging_supporting_points,
            proof_points=self.messaging_proof_points,
            call_to_action=self.messaging_call_to_action,
            tone_guidelines=self.messaging_tone_guidelines,
        )
        competitive_position = CompetitivePosition(
            primary_competitors=self.primary_competitors,
            competitive_advantages=self.competitive_advantages,
            differentiators=self.competitive_differentiators,
            market_position=self.competitive_market_position,
            positioning_statement=self.competitive_positioning_statement,
        )
        icp_profiles = [
            ICPProfile(
                name=icp.name,
                description=icp.description,
                company_size=icp.company_size,
                industry=icp.industry,
                revenue_range=icp.revenue_range,
                geographic_focus=icp.geographic_focus,
                pain_points=icp.pain_points,
                value_proposition=icp.value_proposition,
                priority=icp.priority,
            )
            for icp in self.icp_profiles
        ]
        channel_strategies = [
            ChannelStrategy(
                channel=strategy.channel,
                priority=strategy.priority,
                budget_allocation=strategy.budget_allocation,
                key_metrics=strategy.key_metrics,
                tactics=strategy.tactics,
            )
            for strategy in self.channel_strategies
        ]
        metadata: Dict[str, Any] = {
            "source": "business_context_form",
            "input_timestamp": datetime.utcnow().isoformat(),
        }
        return BusinessContext(
            ucid=ucid,
            workspace_id=workspace_id,
            user_id=user_id,
            identity=identity,
            audience=audience,
            positioning=positioning,
            messaging_framework=messaging,
            competitive_position=competitive_position,
            icp_profiles=icp_profiles,
            channel_strategies=channel_strategies,
            intelligence=Intelligence(),
            evidence_ids=[],
            noteworthy_insights=[],
            metadata=metadata,
        )
