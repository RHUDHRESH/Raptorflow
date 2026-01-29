import json
import re
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, ValidationError, validator


class StrategyPath(str, Enum):
    """Strategy path enumeration."""

    SAFE = "safe"
    CLEVER = "clever"
    BOLD = "bold"


class CompanySize(str, Enum):
    """Company size enumeration."""

    STARTUP = "startup"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    ENTERPRISE = "enterprise"


class Industry(str, Enum):
    """Industry enumeration."""

    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    EDUCATION = "education"
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"
    CONSULTING = "consulting"
    MEDIA = "media"
    OTHER = "other"


class ICPProfile(BaseModel):
    """Ideal Customer Profile definition."""

    name: str = Field(description="ICP name")
    description: str = Field(description="ICP description")
    company_size: Optional[CompanySize] = Field(None, description="Target company size")
    industry: Optional[Industry] = Field(None, description="Target industry")
    revenue_range: Optional[str] = Field(None, description="Revenue range")
    geographic_focus: List[str] = Field(
        default_factory=list, description="Geographic focus areas"
    )
    pain_points: List[str] = Field(default_factory=list, description="Key pain points")
    value_proposition: str = Field(description="Value proposition for this ICP")
    priority: int = Field(default=1, ge=1, le=3, description="Priority level (1-3)")


class ChannelStrategy(BaseModel):
    """Channel strategy definition."""

    channel: str = Field(description="Channel name")
    priority: str = Field(description="Priority level")
    budget_allocation: Optional[float] = Field(
        None, description="Budget allocation percentage"
    )
    key_metrics: List[str] = Field(
        default_factory=list, description="Key metrics to track"
    )
    tactics: List[str] = Field(default_factory=list, description="Specific tactics")


class MessagingFramework(BaseModel):
    """Messaging framework definition."""

    core_message: str = Field(description="Core brand message")
    value_proposition: str = Field(description="Value proposition")
    supporting_points: List[str] = Field(
        default_factory=list, description="Supporting points"
    )
    proof_points: List[str] = Field(
        default_factory=list, description="Proof points and evidence"
    )
    call_to_action: str = Field(description="Primary call to action")
    tone_guidelines: List[str] = Field(
        default_factory=list, description="Tone guidelines"
    )


class CompetitivePosition(BaseModel):
    """Competitive positioning analysis."""

    primary_competitors: List[str] = Field(
        default_factory=list, description="Primary competitors"
    )
    competitive_advantages: List[str] = Field(
        default_factory=list, description="Competitive advantages"
    )
    differentiators: List[str] = Field(
        default_factory=list, description="Key differentiators"
    )
    market_position: str = Field(description="Current market position")
    positioning_statement: str = Field(description="Positioning statement")


class Intelligence(BaseModel):
    """Business intelligence and insights."""

    market_insights: List[Dict[str, Any]] = Field(
        default_factory=list, description="Market insights"
    )
    competitor_analysis: List[Dict[str, Any]] = Field(
        default_factory=list, description="Competitor analysis"
    )
    trend_analysis: List[Dict[str, Any]] = Field(
        default_factory=list, description="Trend analysis"
    )
    opportunity_areas: List[str] = Field(
        default_factory=list, description="Opportunity areas"
    )
    risk_factors: List[str] = Field(default_factory=list, description="Risk factors")


class BrandIdentity(BaseModel):
    """Enhanced brand identity definition."""

    name: str = Field(description="Brand name")
    tagline: Optional[str] = Field(None, description="Brand tagline")
    core_promise: str = Field(description="Core brand promise")
    mission_statement: Optional[str] = Field(None, description="Mission statement")
    vision_statement: Optional[str] = Field(None, description="Vision statement")
    values: List[str] = Field(default_factory=list, description="Core values")
    tone_of_voice: List[str] = Field(
        default_factory=list, description="Tone of voice guidelines"
    )
    manifesto_summary: str = Field(description="Brand manifesto summary")
    personality_traits: List[str] = Field(
        default_factory=list, description="Brand personality traits"
    )
    visual_identity: Dict[str, Any] = Field(
        default_factory=dict, description="Visual identity guidelines"
    )

    @validator("name")
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError("Brand name must be at least 2 characters long")
        return v.strip()

    @validator("core_promise")
    def validate_core_promise(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError("Core promise must be at least 10 characters long")
        return v.strip()


class StrategicAudience(BaseModel):
    """Enhanced strategic audience definition."""

    primary_segment: str = Field(description="Primary audience segment")
    secondary_segments: List[str] = Field(
        default_factory=list, description="Secondary audience segments"
    )
    demographics: Dict[str, Any] = Field(
        default_factory=dict, description="Demographic information"
    )
    psychographics: Dict[str, Any] = Field(
        default_factory=dict, description="Psychographic information"
    )
    pain_points: List[str] = Field(default_factory=list, description="Key pain points")
    desires: List[str] = Field(
        default_factory=list, description="Key desires and motivations"
    )
    challenges: List[str] = Field(default_factory=list, description="Challenges faced")
    goals: List[str] = Field(default_factory=list, description="Goals and aspirations")
    media_consumption: List[str] = Field(
        default_factory=list, description="Media consumption habits"
    )
    decision_factors: List[str] = Field(
        default_factory=list, description="Key decision factors"
    )

    @validator("primary_segment")
    def validate_primary_segment(cls, v):
        if not v or len(v.strip()) < 5:
            raise ValueError("Primary segment must be at least 5 characters long")
        return v.strip()


class MarketPosition(BaseModel):
    """Enhanced market position definition."""

    category: str = Field(description="Market category")
    subcategory: Optional[str] = Field(None, description="Market subcategory")
    differentiator: str = Field(description="Key differentiator")
    perceptual_quadrant: str = Field(description="Perceptual quadrant positioning")
    strategy_path: StrategyPath = Field(description="Strategy path (safe/clever/bold)")
    market_share: Optional[float] = Field(
        None, description="Current market share percentage"
    )
    target_market_share: Optional[float] = Field(
        None, description="Target market share"
    )
    competitive_landscape: List[str] = Field(
        default_factory=list, description="Competitive landscape"
    )
    positioning_statement: str = Field(description="Clear positioning statement")

    @validator("differentiator")
    def validate_differentiator(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError("Differentiator must be at least 10 characters long")
        return v.strip()

    @validator("positioning_statement")
    def validate_positioning_statement(cls, v):
        if not v or len(v.strip()) < 15:
            raise ValueError(
                "Positioning statement must be at least 15 characters long"
            )
        return v.strip()


class BusinessContext(BaseModel):
    """Comprehensive business context schema for RaptorFlow onboarding."""

    # Metadata
    ucid: str = Field(description="Unique context identifier")
    version: str = Field(default="1.0", description="Schema version")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )
    workspace_id: str = Field(description="Workspace ID")
    user_id: str = Field(description="User ID")

    # Core business context
    identity: BrandIdentity = Field(
        default_factory=BrandIdentity, description="Brand identity"
    )
    audience: StrategicAudience = Field(
        default_factory=StrategicAudience, description="Strategic audience"
    )
    positioning: MarketPosition = Field(
        default_factory=MarketPosition, description="Market position"
    )

    # Enhanced components
    icp_profiles: List[ICPProfile] = Field(
        default_factory=list, description="Ideal Customer Profiles"
    )
    channel_strategies: List[ChannelStrategy] = Field(
        default_factory=list, description="Channel strategies"
    )
    messaging_framework: MessagingFramework = Field(
        default_factory=MessagingFramework, description="Messaging framework"
    )
    competitive_position: CompetitivePosition = Field(
        default_factory=CompetitivePosition, description="Competitive positioning"
    )
    intelligence: Intelligence = Field(
        default_factory=Intelligence, description="Business intelligence"
    )

    # Evidence and validation
    evidence_ids: List[str] = Field(
        default_factory=list, description="Evidence IDs from onboarding steps"
    )
    noteworthy_insights: List[Dict[str, Any]] = Field(
        default_factory=list, description="Noteworthy insights"
    )
    validation_score: Optional[float] = Field(
        None, ge=0, le=1, description="Validation score (0-1)"
    )
    completion_percentage: float = Field(
        default=0.0, ge=0, le=100, description="Completion percentage"
    )

    # Status and metadata
    status: str = Field(
        default="draft", description="Context status (draft/complete/published)"
    )
    quality_score: Optional[float] = Field(
        None, ge=0, le=1, description="Quality score (0-1)"
    )
    ai_generated: bool = Field(
        default=False, description="Whether this was AI-generated"
    )
    human_reviewed: bool = Field(
        default=False, description="Whether this was human-reviewed"
    )

    # Flexible metadata for future extensions
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    @validator("ucid")
    def validate_ucid(cls, v):
        if not v or not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                "UCID must contain only alphanumeric characters, hyphens, and underscores"
            )
        return v

    @validator("completion_percentage")
    def validate_completion_percentage(cls, v):
        if not 0 <= v <= 100:
            raise ValueError("Completion percentage must be between 0 and 100")
        return v

    @validator("status")
    def validate_status(cls, v):
        valid_statuses = ["draft", "complete", "published", "archived"]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")
        return v

    def calculate_completion_percentage(self) -> float:
        """Calculate completion percentage based on filled fields."""
        total_fields = 0
        filled_fields = 0

        # Check each major component
        components = [
            (self.identity, ["name", "core_promise", "tone_of_voice"]),
            (self.audience, ["primary_segment", "pain_points", "desires"]),
            (self.positioning, ["category", "differentiator", "strategy_path"]),
        ]

        for component, required_fields in components:
            for field in required_fields:
                total_fields += 1
                value = getattr(component, field)
                if isinstance(value, list):
                    if value and len(value) > 0:
                        filled_fields += 1
                elif isinstance(value, str):
                    if value and value.strip():
                        filled_fields += 1

        # Check optional components
        if self.icp_profiles:
            total_fields += 1
            if self.icp_profiles and len(self.icp_profiles) > 0:
                filled_fields += 1

        if self.channel_strategies:
            total_fields += 1
            if self.channel_strategies and len(self.channel_strategies) > 0:
                filled_fields += 1

        if self.messaging_framework.core_message:
            total_fields += 1
            filled_fields += 1

        # Calculate percentage
        if total_fields == 0:
            return 0.0

        percentage = (filled_fields / total_fields) * 100
        return round(percentage, 2)

    def validate_quality(self) -> Dict[str, Any]:
        """Validate the quality and completeness of the business context."""
        issues = []
        warnings = []
        score = 1.0

        # Check required fields
        if not self.identity.name or len(self.identity.name.strip()) < 2:
            issues.append("Brand name is required")
            score -= 0.2

        if (
            not self.identity.core_promise
            or len(self.identity.core_promise.strip()) < 10
        ):
            issues.append("Core promise is required and should be descriptive")
            score -= 0.2

        if (
            not self.audience.primary_segment
            or len(self.audience.primary_segment.strip()) < 5
        ):
            issues.append("Primary audience segment is required")
            score -= 0.2

        if not self.positioning.category:
            issues.append("Market category is required")
            score -= 0.1

        # Check data quality
        if len(self.audience.pain_points) < 3:
            warnings.append(
                "Consider adding more pain points for better audience understanding"
            )
            score -= 0.05

        if len(self.audience.desires) < 3:
            warnings.append(
                "Consider adding more desires for better audience understanding"
            )
            score -= 0.05

        if not self.icp_profiles:
            warnings.append("Consider adding ICP profiles for better targeting")
            score -= 0.1

        if not self.channel_strategies:
            warnings.append(
                "Consider adding channel strategies for better go-to-market planning"
            )
            score -= 0.1

        # Check consistency
        if self.identity.name and self.positioning.positioning_statement:
            if (
                self.identity.name.lower()
                not in self.positioning.positioning_statement.lower()
            ):
                warnings.append(
                    "Consider including brand name in positioning statement"
                )
                score -= 0.05

        return {
            "score": max(0.0, score),
            "issues": issues,
            "warnings": warnings,
            "is_valid": len(issues) == 0,
        }

    def to_summary(self) -> Dict[str, Any]:
        """Generate a summary of the business context."""
        return {
            "brand": self.identity.name,
            "tagline": self.identity.tagline,
            "primary_audience": self.audience.primary_segment,
            "market_category": self.positioning.category,
            "strategy_path": self.positioning.strategy_path.value,
            "icp_count": len(self.icp_profiles),
            "completion_percentage": self.calculate_completion_percentage(),
            "status": self.status,
            "quality_score": self.validate_quality()["score"],
        }
