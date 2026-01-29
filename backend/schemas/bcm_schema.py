"""
Business Context Manifest (BCM) JSON Schema

Comprehensive JSON schema definitions for the Business Context Manifest system
including validation, serialization, and compatibility checks.
"""

import hashlib
import json
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, root_validator, validator


class BCMVersion(str, Enum):
    """Supported BCM schema versions."""

    V1_0 = "1.0"
    V1_1 = "1.1"
    V2_0 = "2.0"


class IndustryType(str, Enum):
    """Standard industry classifications."""

    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"
    EDUCATION = "education"
    REAL_ESTATE = "real_estate"
    ENTERTAINMENT = "entertainment"
    FOOD_BEVERAGE = "food_beverage"
    TRANSPORTATION = "transportation"
    ENERGY = "energy"
    CONSULTING = "consulting"
    MEDIA = "media"
    AGRICULTURE = "agriculture"
    CONSTRUCTION = "construction"
    OTHER = "other"


class CompanyStage(str, Enum):
    """Company growth stages."""

    PRE_SEED = "pre_seed"
    SEED = "seed"
    SERIES_A = "series_a"
    SERIES_B = "series_b"
    SERIES_C = "series_c"
    GROWTH = "growth"
    MATURE = "mature"
    ENTERPRISE = "enterprise"


class ChannelType(str, Enum):
    """Marketing channel types."""

    WEBSITE = "website"
    SOCIAL_MEDIA = "social_media"
    EMAIL = "email"
    PAID_SEARCH = "paid_search"
    ORGANIC_SEARCH = "organic_search"
    CONTENT_MARKETING = "content_marketing"
    DIRECT_SALES = "direct_sales"
    PARTNERSHIPS = "partnerships"
    EVENTS = "events"
    PR_MEDIA = "pr_media"
    REFERRALS = "referrals"
    ADVERTISING = "advertising"


# Base Models
class BaseModelWithTimestamp(BaseModel):
    """Base model with timestamp fields."""

    created_at: str = Field(..., description="ISO 8601 timestamp")
    updated_at: Optional[str] = Field(None, description="ISO 8601 timestamp")


class CompanyInfo(BaseModel):
    """Company information schema."""

    name: str = Field(..., min_length=1, max_length=255, description="Company name")
    website: Optional[str] = Field(None, description="Company website URL")
    industry: IndustryType = Field(..., description="Primary industry")
    sub_industry: Optional[str] = Field(
        None, max_length=100, description="Sub-industry specification"
    )
    description: str = Field(
        ..., min_length=10, max_length=1000, description="Company description"
    )
    stage: CompanyStage = Field(..., description="Company growth stage")
    founded_year: Optional[int] = Field(
        None, ge=1800, le=2030, description="Year founded"
    )
    employee_count: Optional[int] = Field(
        None, ge=1, le=100000, description="Number of employees"
    )
    revenue_range: Optional[str] = Field(
        None, description="Revenue range (e.g., '$1M-$10M')"
    )
    headquarters: Optional[str] = Field(
        None, max_length=255, description="Headquarters location"
    )

    @validator("website")
    def validate_website(cls, v):
        if v and not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("Website must start with http:// or https://")
        return v


class ICPPainPoint(BaseModel):
    """ICP pain point schema."""

    category: str = Field(..., description="Pain point category")
    description: str = Field(
        ..., min_length=5, max_length=500, description="Pain point description"
    )
    severity: int = Field(..., ge=1, le=10, description="Severity score (1-10)")
    frequency: str = Field(..., description="How often this pain occurs")


class ICPGoal(BaseModel):
    """ICP goal schema."""

    category: str = Field(..., description="Goal category")
    description: str = Field(
        ..., min_length=5, max_length=500, description="Goal description"
    )
    priority: str = Field(..., description="Priority level (high/medium/low)")
    timeline: Optional[str] = Field(None, description="Expected timeline")


class ICPObjection(BaseModel):
    """ICP objection schema."""

    type: str = Field(..., description="Objection type")
    description: str = Field(
        ..., min_length=5, max_length=500, description="Objection description"
    )
    response: Optional[str] = Field(None, description="Prepared response")


class ICPTriggerEvent(BaseModel):
    """ICP trigger event schema."""

    event: str = Field(..., description="Trigger event")
    timing: str = Field(..., description="When this trigger occurs")
    impact: str = Field(..., description="Impact level/description")


class ICPProfile(BaseModel):
    """Ideal Customer Profile schema."""

    name: str = Field(..., min_length=1, max_length=255, description="ICP name/segment")
    description: str = Field(
        ..., min_length=10, max_length=1000, description="ICP description"
    )
    company_size: Optional[str] = Field(None, description="Target company size")
    vertical: Optional[str] = Field(None, description="Target vertical/industry")
    geography: Optional[List[str]] = Field(
        None, description="Target geographic regions"
    )
    pains: List[ICPPainPoint] = Field(
        default_factory=list, description="Key pain points"
    )
    goals: List[ICPGoal] = Field(default_factory=list, description="Key goals")
    objections: List[ICPObjection] = Field(
        default_factory=list, description="Common objections"
    )
    triggers: List[ICPTriggerEvent] = Field(
        default_factory=list, description="Trigger events"
    )
    confidence_score: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Confidence in this ICP"
    )


class CompetitorInfo(BaseModel):
    """Competitor information schema."""

    name: str = Field(..., min_length=1, max_length=255, description="Competitor name")
    website: Optional[str] = Field(None, description="Competitor website")
    type: str = Field(..., description="Competitor type (direct/indirect/alternative)")
    strengths: List[str] = Field(default_factory=list, description="Key strengths")
    weaknesses: List[str] = Field(default_factory=list, description="Key weaknesses")
    market_share: Optional[str] = Field(None, description="Estimated market share")
    pricing_model: Optional[str] = Field(None, description="Pricing model")
    target_segments: List[str] = Field(
        default_factory=list, description="Target customer segments"
    )


class PositioningDelta(BaseModel):
    """Positioning delta schema."""

    axis: str = Field(..., description="Positioning axis (e.g., price vs quality)")
    our_position: str = Field(..., description="Our position on this axis")
    competitor_position: str = Field(..., description="Competitor position")
    differentiation: str = Field(..., description="How we differentiate")


class BrandValues(BaseModel):
    """Brand values schema."""

    value: str = Field(..., min_length=1, max_length=100, description="Brand value")
    description: str = Field(
        ..., min_length=5, max_length=300, description="Value description"
    )


class BrandPersonality(BaseModel):
    """Brand personality schema."""

    trait: str = Field(
        ..., min_length=1, max_length=100, description="Personality trait"
    )
    description: str = Field(
        ..., min_length=5, max_length=300, description="Trait description"
    )


class MessagingValueProp(BaseModel):
    """Value proposition schema."""

    primary: str = Field(
        ..., min_length=10, max_length=500, description="Primary value proposition"
    )
    secondary: Optional[str] = Field(
        None, max_length=500, description="Secondary value proposition"
    )
    supporting_points: List[str] = Field(
        default_factory=list, description="Supporting points"
    )


class Tagline(BaseModel):
    """Tagline schema."""

    text: str = Field(..., min_length=5, max_length=200, description="Tagline text")
    context: Optional[str] = Field(None, description="Usage context")
    variants: Optional[List[str]] = Field(None, description="Alternative versions")


class KeyMessage(BaseModel):
    """Key message schema."""

    title: str = Field(..., min_length=1, max_length=200, description="Message title")
    content: str = Field(
        ..., min_length=10, max_length=1000, description="Message content"
    )
    audience: str = Field(..., description="Target audience")
    priority: str = Field(..., description="Message priority")


class Soundbite(BaseModel):
    """Soundbite schema."""

    text: str = Field(..., min_length=5, max_length=300, description="Soundbite text")
    context: str = Field(..., description="Usage context")
    length: str = Field(..., description="Length category (short/medium/long)")


class ChannelInfo(BaseModel):
    """Channel information schema."""

    type: ChannelType = Field(..., description="Channel type")
    name: str = Field(..., min_length=1, max_length=255, description="Channel name")
    description: Optional[str] = Field(
        None, max_length=500, description="Channel description"
    )
    effectiveness: Optional[str] = Field(None, description="Effectiveness rating")
    cost_efficiency: Optional[str] = Field(None, description="Cost efficiency rating")
    target_audience: Optional[str] = Field(None, description="Primary target audience")


class MarketSizing(BaseModel):
    """Market sizing schema."""

    tam: Optional[Dict[str, Union[str, float]]] = Field(
        None, description="Total Addressable Market"
    )
    sam: Optional[Dict[str, Union[str, float]]] = Field(
        None, description="Serviceable Addressable Market"
    )
    som: Optional[Dict[str, Union[str, float]]] = Field(
        None, description="Serviceable Obtainable Market"
    )
    currency: Optional[str] = Field(
        None, default="USD", description="Currency for market values"
    )
    year: Optional[int] = Field(None, description="Market sizing year")


class Goal(BaseModel):
    """Goal schema."""

    title: str = Field(..., min_length=1, max_length=200, description="Goal title")
    description: str = Field(
        ..., min_length=10, max_length=1000, description="Goal description"
    )
    timeframe: str = Field(..., description="Timeframe for achievement")
    metrics: List[str] = Field(default_factory=list, description="Success metrics")
    priority: str = Field(..., description="Goal priority")


class KPI(BaseModel):
    """KPI schema."""

    name: str = Field(..., min_length=1, max_length=100, description="KPI name")
    description: str = Field(
        ..., min_length=5, max_length=300, description="KPI description"
    )
    target: Optional[Union[str, float]] = Field(None, description="Target value")
    current: Optional[Union[str, float]] = Field(None, description="Current value")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    frequency: str = Field(..., description="Measurement frequency")


class Contradiction(BaseModel):
    """Contradiction schema."""

    type: str = Field(..., description="Contradiction type")
    description: str = Field(
        ..., min_length=10, max_length=1000, description="Contradiction description"
    )
    severity: str = Field(..., description="Severity level")
    resolution: Optional[str] = Field(None, description="Proposed resolution")


class RecentWin(BaseModel):
    """Recent win schema."""

    title: str = Field(..., min_length=1, max_length=200, description="Win title")
    description: str = Field(
        ..., min_length=10, max_length=1000, description="Win description"
    )
    date: str = Field(..., description="Date of win (ISO 8601)")
    impact: str = Field(..., description="Impact level/description")
    customer: Optional[str] = Field(None, description="Customer name if applicable")


class Risk(BaseModel):
    """Risk schema."""

    title: str = Field(..., min_length=1, max_length=200, description="Risk title")
    description: str = Field(
        ..., min_length=10, max_length=1000, description="Risk description"
    )
    probability: str = Field(..., description="Risk probability")
    impact: str = Field(..., description="Risk impact")
    mitigation: Optional[str] = Field(None, description="Mitigation strategy")


class BusinessContextManifest(BaseModel):
    """Complete Business Context Manifest schema."""

    # Metadata
    version: BCMVersion = Field(
        default=BCMVersion.V2_0, description="BCM schema version"
    )
    generated_at: str = Field(..., description="Generation timestamp (ISO 8601)")
    workspace_id: str = Field(..., min_length=1, description="Workspace ID")
    user_id: Optional[str] = Field(None, description="User ID who generated this")
    checksum: Optional[str] = Field(None, description="SHA-256 checksum for integrity")

    # Core Business Information
    company: CompanyInfo = Field(..., description="Company information")

    # Customer Profiles
    icps: List[ICPProfile] = Field(
        default_factory=list, description="Ideal Customer Profiles"
    )

    # Competitive Landscape
    competitors: Dict[str, Any] = Field(..., description="Competitive information")
    direct_competitors: List[CompetitorInfo] = Field(
        default_factory=list, description="Direct competitors"
    )
    indirect_competitors: List[CompetitorInfo] = Field(
        default_factory=list, description="Indirect competitors"
    )
    positioning_delta: List[PositioningDelta] = Field(
        default_factory=list, description="Positioning deltas"
    )

    # Brand & Positioning
    brand: Dict[str, Any] = Field(..., description="Brand information")
    values: List[BrandValues] = Field(default_factory=list, description="Brand values")
    personality: List[BrandPersonality] = Field(
        default_factory=list, description="Brand personality"
    )
    tone: List[str] = Field(default_factory=list, description="Brand tone descriptors")
    positioning: Optional[str] = Field(
        None, max_length=1000, description="Brand positioning statement"
    )

    # Market Information
    market: MarketSizing = Field(..., description="Market sizing information")
    verticals: List[str] = Field(default_factory=list, description="Target verticals")
    geography: List[str] = Field(
        default_factory=list, description="Target geographic regions"
    )

    # Messaging
    messaging: Dict[str, Any] = Field(..., description="Messaging information")
    value_prop: MessagingValueProp = Field(..., description="Value proposition")
    taglines: List[Tagline] = Field(default_factory=list, description="Brand taglines")
    key_messages: List[KeyMessage] = Field(
        default_factory=list, description="Key messages"
    )
    soundbites: List[Soundbite] = Field(
        default_factory=list, description="Marketing soundbites"
    )

    # Channels
    channels: Dict[str, Any] = Field(..., description="Channel information")
    primary_channels: List[ChannelInfo] = Field(
        default_factory=list, description="Primary channels"
    )
    secondary_channels: List[ChannelInfo] = Field(
        default_factory=list, description="Secondary channels"
    )
    strategy_summary: Optional[str] = Field(
        None, max_length=2000, description="Channel strategy summary"
    )

    # Goals & KPIs
    goals: Dict[str, Any] = Field(..., description="Goals information")
    short_term_goals: List[Goal] = Field(
        default_factory=list, description="Short-term goals"
    )
    long_term_goals: List[Goal] = Field(
        default_factory=list, description="Long-term goals"
    )
    kpis: List[KPI] = Field(
        default_factory=list, description="Key Performance Indicators"
    )

    # Issues & Insights
    contradictions: List[Contradiction] = Field(
        default_factory=list, description="Identified contradictions"
    )
    recent_wins: List[RecentWin] = Field(
        default_factory=list, description="Recent wins/successes"
    )
    risks: List[Risk] = Field(default_factory=list, description="Identified risks")

    # Tracking & Links
    links: Dict[str, Any] = Field(..., description="Links to source data")
    raw_step_ids: List[str] = Field(
        default_factory=list, description="Source onboarding step IDs"
    )
    completion_percentage: float = Field(
        ..., ge=0.0, le=100.0, description="Onboarding completion percentage"
    )

    @validator("generated_at")
    def validate_timestamp(cls, v):
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("Invalid timestamp format, must be ISO 8601")
        return v

    @validator("completion_percentage")
    def validate_completion(cls, v):
        if not (0.0 <= v <= 100.0):
            raise ValueError("Completion percentage must be between 0 and 100")
        return v

    @root_validator
    def compute_checksum(cls, values):
        """Compute SHA-256 checksum if not provided."""
        if "checksum" not in values or not values["checksum"]:
            # Create a copy without checksum for calculation
            values_copy = values.copy()
            values_copy.pop("checksum", None)

            # Sort keys for consistent hashing
            manifest_str = json.dumps(values_copy, sort_keys=True, default=str)
            checksum = hashlib.sha256(manifest_str.encode()).hexdigest()
            values["checksum"] = checksum

        return values

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat()}
        schema_extra = {
            "example": {
                "version": "2.0",
                "generated_at": "2026-01-27T06:30:00Z",
                "workspace_id": "workspace_123",
                "user_id": "user_456",
                "company": {
                    "name": "TechCorp Solutions",
                    "website": "https://techcorp.com",
                    "industry": "technology",
                    "description": "AI-powered business analytics platform",
                    "stage": "series_a",
                },
                "icps": [],
                "competitors": {},
                "direct_competitors": [],
                "indirect_competitors": [],
                "positioning_delta": [],
                "brand": {},
                "values": [],
                "personality": [],
                "tone": [],
                "positioning": None,
                "market": {
                    "tam": {"value": 1000000000, "currency": "USD"},
                    "sam": {"value": 100000000, "currency": "USD"},
                    "som": {"value": 10000000, "currency": "USD"},
                },
                "verticals": [],
                "geography": [],
                "messaging": {},
                "value_prop": {
                    "primary": "Transform your data into actionable insights"
                },
                "taglines": [],
                "key_messages": [],
                "soundbites": [],
                "channels": {},
                "primary_channels": [],
                "secondary_channels": [],
                "strategy_summary": None,
                "goals": {},
                "short_term_goals": [],
                "long_term_goals": [],
                "kpis": [],
                "contradictions": [],
                "recent_wins": [],
                "risks": [],
                "links": {},
                "raw_step_ids": [],
                "completion_percentage": 85.0,
            }
        }


# Schema Validation and Utilities
class BCMSchemaValidator:
    """BCM schema validation utilities."""

    @staticmethod
    def validate_manifest(manifest_data: Dict[str, Any]) -> BusinessContextManifest:
        """Validate manifest data against BCM schema."""
        try:
            return BusinessContextManifest(**manifest_data)
        except Exception as e:
            raise ValueError(f"Invalid BCM manifest: {str(e)}")

    @staticmethod
    def validate_compatibility(
        manifest: BusinessContextManifest,
        required_version: BCMVersion = BCMVersion.V2_0,
    ) -> bool:
        """Check if manifest is compatible with required version."""
        return manifest.version == required_version

    @staticmethod
    def get_schema_json() -> Dict[str, Any]:
        """Get the JSON schema for BCM."""
        return BusinessContextManifest.schema()

    @staticmethod
    def estimate_token_count(manifest: BusinessContextManifest) -> int:
        """Estimate token count for a manifest."""
        manifest_json = manifest.json()
        # Rough estimation: ~4 characters per token
        return len(manifest_json) // 4

    @staticmethod
    def validate_size_constraints(manifest: BusinessContextManifest) -> bool:
        """Validate manifest meets size constraints."""
        token_count = BCMSchemaValidator.estimate_token_count(manifest)
        return token_count <= 1200  # Max token budget


# Migration utilities
class BCMMigration:
    """BCM schema migration utilities."""

    @staticmethod
    def migrate_v1_to_v2(v1_manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate v1 manifest to v2 schema."""
        # Basic migration logic
        v2_manifest = v1_manifest.copy()
        v2_manifest["version"] = "2.0"

        # Ensure required fields exist
        if "completion_percentage" not in v2_manifest:
            v2_manifest["completion_percentage"] = 0.0

        if "generated_at" not in v2_manifest:
            v2_manifest["generated_at"] = datetime.utcnow().isoformat()

        return v2_manifest

    @staticmethod
    def can_migrate(from_version: str, to_version: str) -> bool:
        """Check if migration is supported."""
        migration_map = {
            "1.0": ["2.0"],
            "1.1": ["2.0"],
        }
        return to_version in migration_map.get(from_version, [])


# Export main classes
__all__ = [
    "BusinessContextManifest",
    "BCMSchemaValidator",
    "BCMMigration",
    "BCMVersion",
    "CompanyInfo",
    "ICPProfile",
    "CompetitorInfo",
    "MarketSizing",
    "MessagingValueProp",
    "ChannelInfo",
    "Goal",
    "KPI",
    "Contradiction",
    "RecentWin",
    "Risk",
]
