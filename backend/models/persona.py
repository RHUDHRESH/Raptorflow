"""
Pydantic models for ICP/Persona data.
Includes request/response schemas, structured ICP profiles, and persona narratives.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from backend.models.base import BaseSchema

# 50+ demographic/psychographic tags used by tag assignment agents
TAG_OPTIONS: List[str] = [
    "early_adopter",
    "fast_follower",
    "cost_sensitive",
    "value_buyer",
    "premium_buyer",
    "security_first",
    "compliance_led",
    "data_driven",
    "risk_averse",
    "risk_tolerant",
    "innovation_culture",
    "process_oriented",
    "experimentation_culture",
    "automation_focus",
    "ai_first",
    "developer_tooling",
    "product_led_growth",
    "sales_led_growth",
    "community_led",
    "partner_led",
    "brand_marketing",
    "performance_marketing",
    "demand_generation",
    "account_based",
    "field_sales",
    "self_serve",
    "trial_focused",
    "freemium_motion",
    "enterprise_it",
    "midmarket_ops",
    "smb_owner",
    "agency_owner",
    "founder_led",
    "technical_buyer",
    "marketing_leader",
    "sales_leader",
    "ops_manager",
    "finance_leader",
    "product_manager",
    "customer_success",
    "revops",
    "remote_first",
    "hybrid_team",
    "distributed_team",
    "in_office",
    "global_team",
    "regulated_industry",
    "healthcare",
    "finserv",
    "education",
    "manufacturing",
    "ecommerce",
    "saas",
    "marketplace",
    "b2b",
    "b2c",
    "sustainability_focus",
    "diversity_inclusion",
    "quality_first",
    "speed_over_perfection",
    "storytelling_resonates",
    "analytical_buyer",
    "roi_focused",
]


class Demographics(BaseModel):
    """Structured demographics/firmographics for an ICP."""

    age_range: Optional[str] = None
    gender: Optional[str] = None
    education: Optional[str] = None
    income_range: Optional[str] = None
    company_size: Optional[str] = None
    revenue_range: Optional[str] = None
    industry: Optional[str] = None
    geography: Optional[str] = None
    buyer_role: Optional[str] = None


class Psychographics(BaseModel):
    """Psychographic attributes aligned to pain points/goals."""

    values: List[str] = Field(default_factory=list)
    pain_points: List[str] = Field(default_factory=list)
    goals: List[str] = Field(default_factory=list)
    motivation: Optional[str] = None
    motivations: List[str] = Field(default_factory=list)
    ability: Optional[str] = None
    objections: List[str] = Field(default_factory=list)
    buying_behavior: Optional[str] = None
    risk_tolerance: Optional[str] = None
    decision_style: Optional[str] = None


class Communication(BaseModel):
    """Communication preferences for an ICP/persona."""

    channels: List[str] = Field(default_factory=list)
    tone: Optional[str] = None
    format: Optional[str] = None
    cadence: Optional[str] = None


class ICPRequest(BaseModel):
    """Request payload to build an ICP/persona."""

    company_name: str
    industry: str
    product_description: str
    target_market: Optional[str] = None
    target_geo: Optional[str] = None
    goals: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    preferred_channels: List[str] = Field(default_factory=list)
    seed_tags: List[str] = Field(default_factory=list, description="Optional seed tags for tag assignment")


class ICPProfile(BaseModel):
    """Reusable ICP profile consumed by agents and graphs."""

    id: UUID = Field(default_factory=uuid4)
    workspace_id: Optional[UUID] = None
    name: str = Field(..., alias="icp_name")
    executive_summary: Optional[str] = None
    demographics: Demographics = Field(default_factory=Demographics)
    psychographics: Psychographics = Field(default_factory=Psychographics)
    pain_points: List[str] = Field(default_factory=list)
    goals: List[str] = Field(default_factory=list)
    behavioral_triggers: List[str] = Field(default_factory=list)
    communication: Communication = Field(default_factory=Communication)
    budget: Optional[str] = None
    timeline: Optional[str] = None
    decision_structure: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
        from_attributes = True

    @field_validator("tags")
    @classmethod
    def _validate_tags(cls, value: List[str]) -> List[str]:
        """Ensure tags are deduplicated and pulled from the approved catalog."""
        if not value:
            return []
        deduped = []
        seen = set()
        for tag in value:
            if tag in seen:
                continue
            if tag in TAG_OPTIONS:
                deduped.append(tag)
                seen.add(tag)
        return deduped[:50]


class ICPResponse(ICPProfile):
    """Structured response returned by ICP builder workflows."""

    confidence: float = Field(default=0.75, ge=0.0, le=1.0)
    sources: List[str] = Field(default_factory=list, description="Evidence sources used during generation")


class Cohort(BaseSchema):
    """Persisted cohort/ICP record."""

    name: str
    profile: ICPResponse
    status: str = Field(default="draft", description="draft|review|approved")
    source: Optional[str] = Field(default=None, description="onboarding|manual|agent")


class PersonaNarrative(BaseModel):
    """Narrative persona description suitable for storytelling."""

    icp_id: Optional[UUID] = None
    persona_name: Optional[str] = None
    hook: Optional[str] = None
    narrative: str = Field(..., description="1-3 paragraph narrative in engaging voice")
    day_in_life: List[str] = Field(default_factory=list, description="Bulleted day-in-the-life details")
    goals: List[str] = Field(default_factory=list)
    pain_points: List[str] = Field(default_factory=list)
    preferred_channels: List[str] = Field(default_factory=list)


class PersonaNarrativeRequest(BaseModel):
    """Request to generate persona narrative."""

    icp_id: UUID
    tone: Optional[str] = Field("professional", description="Narrative tone")


class PersonaNarrativeResponse(PersonaNarrative):
    """Generated persona narrative response."""

    name_suggestion: Optional[str] = Field(None, description="Suggested persona name")


class TagEnrichmentRequest(BaseModel):
    """Request to enrich ICP with tags."""

    icp_id: UUID
    description: str = Field(..., description="Raw ICP description")


class TagEnrichmentResponse(BaseModel):
    """Enriched tags."""

    icp_id: UUID
    tags: List[str] = Field(..., description="50+ assigned tags")
    categories: Dict[str, List[str]] = Field(
        ...,
        description="Tags grouped by category (demographic, psychographic, behavioral)",
    )


class PainPointMiningRequest(BaseModel):
    """Request to mine pain points."""

    icp_id: UUID
    sources: List[str] = Field(
        default=["reddit", "quora", "g2", "trustpilot"],
        description="Sources to scrape",
    )


class PainPointMiningResponse(BaseModel):
    """Mined pain points with evidence."""

    icp_id: UUID
    pain_points: List[Dict[str, Any]] = Field(
        ...,
        description="Each pain point with description, frequency, evidence quotes",
    )
    triggers: List[str] = Field(..., description="Buying triggers identified")
    objections: List[str] = Field(..., description="Common objections")

