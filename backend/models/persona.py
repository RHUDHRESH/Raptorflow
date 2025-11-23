"""
Pydantic models for ICP/Persona data.

This module defines comprehensive schemas for Ideal Customer Profile (ICP) and
persona management in RaptorFlow. It includes:

- Request/response models for ICP generation workflows
- Structured demographic, firmographic, and psychographic data
- 50+ pre-defined tags for persona classification
- Validation for age ranges, income ranges, and other demographic data
- Support for confidence scores on tag assignments
- Persona narrative generation for storytelling

Models in this module are used by the Research Supervisor and ICP agents
to build, enrich, and manage customer intelligence.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from backend.models.base import BaseSchema

# 50+ demographic/psychographic tags used by tag assignment agents
# These tags are used for cohort segmentation and content personalization
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


class TagWithConfidence(BaseModel):
    """
    A tag with an associated confidence score.

    Used for AI-assigned tags where the confidence represents how
    strongly the tag applies to the persona (0.0 = not applicable,
    1.0 = highly applicable).

    Attributes:
        tag: The tag name (must be in TAG_OPTIONS)
        confidence: Confidence score between 0.0 and 1.0
    """

    tag: str = Field(..., description="Tag name from TAG_OPTIONS catalog")
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score (0.0-1.0) for this tag assignment",
    )

    @field_validator("tag")
    @classmethod
    def validate_tag_in_catalog(cls, value: str) -> str:
        """Ensure tag is from the approved catalog."""
        if value not in TAG_OPTIONS:
            raise ValueError(
                f"Tag '{value}' not in approved TAG_OPTIONS catalog. "
                f"Available tags: {', '.join(TAG_OPTIONS[:10])}..."
            )
        return value


class Demographics(BaseModel):
    """
    Structured demographics and firmographics for an ICP.

    This model captures quantifiable attributes about the target persona,
    including both B2C demographics (age, gender, education) and B2B
    firmographics (company size, revenue, industry).

    All fields are optional to support both B2C and B2B personas, but
    validation ensures that provided values follow realistic constraints.

    Attributes:
        age_range: Age range (e.g., "25-34", "35-44", "45-54")
        gender: Gender identity (optional, for B2C personas)
        education: Education level (e.g., "Bachelor's", "Master's", "PhD")
        income_range: Annual income range (e.g., "$50K-$75K", "$100K-$150K")
        company_size: Number of employees (e.g., "1-10", "11-50", "51-200")
        revenue_range: Annual revenue range (e.g., "$1M-$10M", "$10M-$50M")
        industry: Industry vertical (e.g., "SaaS", "Healthcare", "E-commerce")
        geography: Geographic location or market (e.g., "North America", "EMEA")
        buyer_role: Job title or role (e.g., "CMO", "VP Sales", "Product Manager")
    """

    age_range: Optional[str] = Field(
        None,
        description="Age range in format '25-34' or '35-44'",
    )
    gender: Optional[str] = Field(
        None,
        description="Gender identity (for B2C personas)",
    )
    education: Optional[str] = Field(
        None,
        description="Highest education level completed",
    )
    income_range: Optional[str] = Field(
        None,
        description="Annual income range (e.g., '$50K-$75K')",
    )
    company_size: Optional[str] = Field(
        None,
        description="Number of employees (e.g., '11-50', '51-200')",
    )
    revenue_range: Optional[str] = Field(
        None,
        description="Annual company revenue range (e.g., '$1M-$10M')",
    )
    industry: Optional[str] = Field(
        None,
        description="Industry vertical or sector",
    )
    geography: Optional[str] = Field(
        None,
        description="Geographic location or target market",
    )
    buyer_role: Optional[str] = Field(
        None,
        description="Job title or organizational role",
    )

    @field_validator("age_range")
    @classmethod
    def validate_age_range(cls, value: Optional[str]) -> Optional[str]:
        """
        Validate age range format and realistic values.

        Accepts formats like "25-34", "35-44", "45-54", "18-24", etc.
        Ensures ages are between 18 and 100.
        """
        if value is None:
            return value

        # Match pattern like "25-34" or "18-24"
        match = re.match(r"^(\d+)-(\d+)$", value.strip())
        if not match:
            raise ValueError(
                f"Age range must be in format 'XX-YY' (e.g., '25-34'), got '{value}'"
            )

        min_age, max_age = int(match.group(1)), int(match.group(2))

        # Validate realistic age ranges
        if min_age < 18 or max_age > 100:
            raise ValueError(
                f"Age range must be between 18-100, got {min_age}-{max_age}"
            )

        if min_age >= max_age:
            raise ValueError(
                f"Minimum age ({min_age}) must be less than maximum age ({max_age})"
            )

        return value

    @field_validator("income_range", "revenue_range")
    @classmethod
    def validate_currency_range(cls, value: Optional[str]) -> Optional[str]:
        """
        Validate income/revenue range format.

        Accepts formats like "$50K-$75K", "$1M-$10M", "$100K-$150K".
        Ensures numeric values are logical (min < max).
        """
        if value is None:
            return value

        # Match patterns like "$50K-$75K" or "$1M-$10M"
        match = re.match(
            r"^\$(\d+(?:\.\d+)?)(K|M|B)?-\$(\d+(?:\.\d+)?)(K|M|B)?$",
            value.strip(),
            re.IGNORECASE,
        )
        if not match:
            raise ValueError(
                f"Currency range must be in format '$XXK-$YYK' or '$XXM-$YYM', "
                f"got '{value}'"
            )

        # Extract numeric values and multipliers
        min_val = float(match.group(1))
        min_mult = match.group(2).upper() if match.group(2) else ""
        max_val = float(match.group(3))
        max_mult = match.group(3).upper() if match.group(4) else ""

        # Convert to same scale for comparison
        multipliers = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000, "": 1}
        min_amount = min_val * multipliers.get(min_mult, 1)
        max_amount = max_val * multipliers.get(max_mult, 1)

        if min_amount >= max_amount:
            raise ValueError(
                f"Minimum amount must be less than maximum amount in '{value}'"
            )

        return value


class Psychographics(BaseModel):
    """
    Psychographic attributes aligned to pain points and goals.

    Psychographics capture the psychological, behavioral, and motivational
    characteristics of a persona. Unlike demographics (quantifiable facts),
    psychographics describe how the persona thinks, feels, and makes decisions.

    These attributes are critical for content personalization and messaging
    that resonates emotionally with the target audience.

    Attributes:
        values: Core values and beliefs (e.g., "innovation", "sustainability")
        pain_points: Key challenges and frustrations
        goals: Aspirations and desired outcomes
        motivation: Primary driver for action (singular, deprecated - use motivations)
        motivations: List of motivational factors
        ability: Capability or readiness to adopt solutions
        objections: Common barriers or hesitations to purchase
        buying_behavior: How they research and make purchase decisions
        risk_tolerance: Attitude toward risk (e.g., "conservative", "aggressive")
        decision_style: Decision-making approach (e.g., "analytical", "intuitive")
    """

    values: List[str] = Field(
        default_factory=list,
        description="Core values and beliefs that guide decisions",
    )
    pain_points: List[str] = Field(
        default_factory=list,
        description="Key challenges, frustrations, or problems to solve",
    )
    goals: List[str] = Field(
        default_factory=list,
        description="Aspirations, desired outcomes, or success metrics",
    )
    motivation: Optional[str] = Field(
        None,
        description="Primary motivational driver (deprecated - use motivations list)",
    )
    motivations: List[str] = Field(
        default_factory=list,
        description="Motivational factors driving behavior and decisions",
    )
    ability: Optional[str] = Field(
        None,
        description="Capability or readiness to adopt solutions",
    )
    objections: List[str] = Field(
        default_factory=list,
        description="Common barriers, hesitations, or objections to purchase",
    )
    buying_behavior: Optional[str] = Field(
        None,
        description="How they research and make purchase decisions",
    )
    risk_tolerance: Optional[str] = Field(
        None,
        description="Attitude toward risk (e.g., 'conservative', 'moderate', 'aggressive')",
    )
    decision_style: Optional[str] = Field(
        None,
        description="Decision-making approach (e.g., 'analytical', 'intuitive', 'collaborative')",
    )


class Communication(BaseModel):
    """
    Communication preferences for an ICP/persona.

    Defines how, when, and where to reach the target persona with
    marketing messages. This informs channel selection and content
    formatting decisions.

    Attributes:
        channels: Preferred communication channels (e.g., "email", "LinkedIn", "Slack")
        tone: Preferred tone (e.g., "professional", "casual", "technical")
        format: Content format preferences (e.g., "long-form", "video", "infographic")
        cadence: Communication frequency (e.g., "daily", "weekly", "monthly")
    """

    channels: List[str] = Field(
        default_factory=list,
        description="Preferred communication channels (email, social, etc.)",
    )
    tone: Optional[str] = Field(
        None,
        description="Preferred communication tone (professional, casual, etc.)",
    )
    format: Optional[str] = Field(
        None,
        description="Preferred content format (long-form, video, etc.)",
    )
    cadence: Optional[str] = Field(
        None,
        description="Preferred communication frequency (daily, weekly, etc.)",
    )


class ICPRequest(BaseModel):
    """
    Request payload to build an ICP/persona.

    Submitted by users during onboarding or when creating new personas.
    The Research Supervisor uses this information to orchestrate ICP
    generation, tag enrichment, and narrative creation.

    Required vs Optional Fields:
        - Required: company_name, industry, product_description
        - Optional: All other fields provide additional context to refine the ICP

    Attributes:
        company_name: Name of the company/brand
        industry: Industry vertical or sector
        product_description: What the product/service does and its value proposition
        target_market: Description of the target market or customer segment
        target_geo: Geographic target market (e.g., "North America", "Global")
        goals: Business goals for this ICP (e.g., "increase leads", "improve retention")
        constraints: Constraints or limitations (e.g., "budget", "timeline")
        preferred_channels: Preferred marketing channels to focus on
        seed_tags: Optional seed tags to guide tag assignment
    """

    company_name: str = Field(
        ...,
        description="Name of the company or brand",
        min_length=1,
    )
    industry: str = Field(
        ...,
        description="Industry vertical or sector (e.g., 'SaaS', 'Healthcare')",
        min_length=1,
    )
    product_description: str = Field(
        ...,
        description="Product/service description and value proposition",
        min_length=10,
    )
    target_market: Optional[str] = Field(
        None,
        description="Target market or customer segment description",
    )
    target_geo: Optional[str] = Field(
        None,
        description="Geographic target market (e.g., 'North America', 'EMEA')",
    )
    goals: List[str] = Field(
        default_factory=list,
        description="Business goals for this ICP (e.g., 'increase leads')",
    )
    constraints: List[str] = Field(
        default_factory=list,
        description="Constraints or limitations (budget, timeline, etc.)",
    )
    preferred_channels: List[str] = Field(
        default_factory=list,
        description="Preferred marketing channels (email, LinkedIn, etc.)",
    )
    seed_tags: List[str] = Field(
        default_factory=list,
        description="Optional seed tags to guide initial tag assignment",
    )


class ICPProfile(BaseModel):
    """
    Reusable ICP profile consumed by agents and graphs.

    This is the core data structure representing an Ideal Customer Profile.
    It aggregates demographic, psychographic, and behavioral data into a
    comprehensive persona that drives all downstream content generation
    and campaign planning.

    The profile supports both simple tag lists (tags) and confidence-scored
    tags (tags_with_confidence) for more nuanced persona classification.

    Required vs Optional Fields:
        - Required: name
        - Optional: All other fields, though a well-defined ICP should have
          demographics, psychographics, and pain_points populated

    Relationships:
        - Used by Content Supervisor to personalize messaging
        - Referenced in Campaign/Move planning to target specific cohorts
        - Enhanced by Research agents through tag enrichment and pain point mining

    Attributes:
        id: Unique identifier (auto-generated)
        workspace_id: Workspace scoping for multi-tenancy
        name: Human-readable ICP name (e.g., "Enterprise CMO", "SMB Founder")
        executive_summary: 1-2 paragraph overview of this ICP
        demographics: Structured demographic and firmographic data
        psychographics: Behavioral and psychological attributes
        pain_points: Key challenges and frustrations (deprecated, use psychographics.pain_points)
        goals: Aspirations and desired outcomes (deprecated, use psychographics.goals)
        behavioral_triggers: Events or situations that trigger buying behavior
        communication: Communication preferences and channels
        budget: Typical budget range or purchasing power
        timeline: Typical decision timeline (e.g., "3-6 months", "1 week")
        decision_structure: How decisions are made (e.g., "committee", "single buyer")
        tags: Simple list of assigned tags (from TAG_OPTIONS)
        tags_with_confidence: Tags with confidence scores (0.0-1.0)
        created_at: Timestamp of creation
        updated_at: Timestamp of last modification
    """

    id: UUID = Field(
        default_factory=uuid4,
        description="Unique identifier for this ICP profile",
    )
    workspace_id: Optional[UUID] = Field(
        None,
        description="Workspace ID for multi-tenant isolation",
    )
    name: str = Field(
        ...,
        alias="icp_name",
        description="Human-readable ICP name (e.g., 'Enterprise CMO')",
        min_length=1,
    )
    executive_summary: Optional[str] = Field(
        None,
        description="1-2 paragraph executive summary of this ICP",
    )
    demographics: Demographics = Field(
        default_factory=Demographics,
        description="Structured demographic and firmographic data",
    )
    psychographics: Psychographics = Field(
        default_factory=Psychographics,
        description="Behavioral and psychological attributes",
    )
    pain_points: List[str] = Field(
        default_factory=list,
        description="Key challenges (deprecated - use psychographics.pain_points)",
    )
    goals: List[str] = Field(
        default_factory=list,
        description="Desired outcomes (deprecated - use psychographics.goals)",
    )
    behavioral_triggers: List[str] = Field(
        default_factory=list,
        description="Events or situations triggering buying behavior",
    )
    communication: Communication = Field(
        default_factory=Communication,
        description="Communication preferences and channels",
    )
    budget: Optional[str] = Field(
        None,
        description="Typical budget range or purchasing power",
    )
    timeline: Optional[str] = Field(
        None,
        description="Typical decision timeline (e.g., '3-6 months')",
    )
    decision_structure: Optional[str] = Field(
        None,
        description="How decisions are made (e.g., 'committee', 'single buyer')",
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Simple list of assigned tags from TAG_OPTIONS",
    )
    tags_with_confidence: List[TagWithConfidence] = Field(
        default_factory=list,
        description="Tags with confidence scores (0.0-1.0) for nuanced classification",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when this ICP was created",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when this ICP was last updated",
    )

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )

    @field_validator("tags")
    @classmethod
    def _validate_tags(cls, value: List[str]) -> List[str]:
        """
        Ensure tags are deduplicated and pulled from the approved catalog.

        Only tags in TAG_OPTIONS are allowed. Invalid tags are silently
        filtered out. Maximum of 50 tags retained.
        """
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

    @model_validator(mode="after")
    def sync_tags_with_confidence(self) -> "ICPProfile":
        """
        Ensure consistency between tags and tags_with_confidence.

        If tags_with_confidence is populated but tags is empty, populate
        tags from tags_with_confidence for backward compatibility.
        """
        if self.tags_with_confidence and not self.tags:
            self.tags = [twc.tag for twc in self.tags_with_confidence]
        return self


class ICPResponse(ICPProfile):
    """
    Structured response returned by ICP builder workflows.

    Extends ICPProfile with metadata about the generation process,
    including confidence scores and evidence sources. Returned by
    the Research Supervisor after ICP generation is complete.

    Attributes:
        confidence: Overall confidence in the ICP accuracy (0.0-1.0)
        sources: Evidence sources used during generation (URLs, documents, etc.)
    """

    confidence: float = Field(
        default=0.75,
        ge=0.0,
        le=1.0,
        description="Overall confidence in ICP accuracy (0.0-1.0)",
    )
    sources: List[str] = Field(
        default_factory=list,
        description="Evidence sources used during generation (URLs, docs, etc.)",
    )


class Cohort(BaseSchema):
    """
    Persisted cohort/ICP record in the database.

    Represents a saved ICP profile that can be targeted in campaigns.
    Extends BaseSchema for consistent ID and timestamp management.

    Workflow States:
        - draft: Initial state, still being refined
        - review: Submitted for review/approval
        - approved: Approved and ready for campaign use

    Source Types:
        - onboarding: Created during user onboarding flow
        - manual: Manually created by user
        - agent: Generated by AI agents

    Attributes:
        name: Display name for this cohort
        profile: Complete ICP profile data
        status: Workflow status (draft|review|approved)
        source: How this cohort was created
    """

    name: str = Field(
        ...,
        description="Display name for this cohort",
        min_length=1,
    )
    profile: ICPResponse = Field(
        ...,
        description="Complete ICP profile data",
    )
    status: str = Field(
        default="draft",
        description="Workflow status: draft|review|approved",
    )
    source: Optional[str] = Field(
        default=None,
        description="Source: onboarding|manual|agent",
    )


class PersonaNarrative(BaseModel):
    """
    Narrative persona description suitable for storytelling.

    Transforms structured ICP data into an engaging narrative format
    that brings the persona to life. Used in pitch decks, strategy
    documents, and to help content creators empathize with the audience.

    This is the "story" version of the ICP, designed for human
    consumption rather than machine processing.

    Attributes:
        icp_id: Reference to the source ICP profile
        persona_name: Human name for the persona (e.g., "Marketing Mary")
        hook: Attention-grabbing opening line
        narrative: 1-3 paragraph narrative in engaging, storytelling voice
        day_in_life: Bulleted day-in-the-life details
        goals: Aspirations and desired outcomes
        pain_points: Key challenges and frustrations
        preferred_channels: Where to reach this persona
    """

    icp_id: Optional[UUID] = Field(
        None,
        description="Reference to the source ICP profile",
    )
    persona_name: Optional[str] = Field(
        None,
        description="Human name for persona (e.g., 'Marketing Mary')",
    )
    hook: Optional[str] = Field(
        None,
        description="Attention-grabbing opening line",
    )
    narrative: str = Field(
        ...,
        description="1-3 paragraph narrative in engaging, storytelling voice",
        min_length=50,
    )
    day_in_life: List[str] = Field(
        default_factory=list,
        description="Bulleted day-in-the-life details",
    )
    goals: List[str] = Field(
        default_factory=list,
        description="Aspirations and desired outcomes",
    )
    pain_points: List[str] = Field(
        default_factory=list,
        description="Key challenges and frustrations",
    )
    preferred_channels: List[str] = Field(
        default_factory=list,
        description="Where to reach this persona",
    )


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

