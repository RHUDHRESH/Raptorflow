"""
Pydantic models for Onboarding flow.
These models define the structure for capturing user/business information
during the initial onboarding process.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal
from uuid import UUID
from datetime import datetime


class PersonaInput(BaseModel):
    """User's initial persona definition during onboarding."""
    nickname: str = Field(..., description="Short nickname for the persona (e.g., 'Scaling Sarah')")
    role: str = Field(..., description="Job title or role")
    biggest_pain_point: str = Field(..., description="Primary challenge this persona faces")
    known_attributes: List[str] = Field(default_factory=list, description="Any known demographic or psychographic traits")


class Goal(BaseModel):
    """A business or personal goal."""
    description: str = Field(..., description="What the user wants to achieve")
    timeframe_days: Optional[int] = Field(None, description="Target timeframe in days")
    priority: Literal["high", "medium", "low"] = Field(default="medium")
    metrics: List[str] = Field(default_factory=list, description="Success metrics")


class Constraints(BaseModel):
    """Operational constraints for strategy execution."""
    budget_monthly: Optional[str] = Field(None, description="Monthly marketing budget")
    team_size: Optional[int] = Field(None, description="Size of the marketing team")
    time_commitment_hours_per_week: Optional[int] = Field(None, description="Hours available per week")
    content_restrictions: List[str] = Field(default_factory=list, description="Legal/brand restrictions")
    preferred_posting_times: Dict[str, List[str]] = Field(
        default_factory=dict, 
        description="Optimal posting times by day of week"
    )
    blackout_dates: List[str] = Field(default_factory=list, description="Dates to avoid publishing")


class ChannelFootprint(BaseModel):
    """Active marketing channels and their status."""
    linkedin: bool = Field(default=False)
    twitter: bool = Field(default=False)
    instagram: bool = Field(default=False)
    youtube: bool = Field(default=False)
    tiktok: bool = Field(default=False)
    email: bool = Field(default=False)
    blog: bool = Field(default=False)
    podcast: bool = Field(default=False)
    other_channels: List[str] = Field(default_factory=list, description="Other active channels")


class BusinessProfile(BaseModel):
    """Profile for businesses/companies."""
    company_name: str
    industry: str
    company_size: Optional[str] = None  # e.g., "1-10", "11-50", "51-200"
    revenue_range: Optional[str] = None
    target_market: Optional[str] = None
    value_proposition: Optional[str] = None
    competitive_advantages: List[str] = Field(default_factory=list)
    proof_points: List[str] = Field(default_factory=list, description="Case studies, testimonials, metrics")


class PersonalBrandProfile(BaseModel):
    """Profile for personal brands."""
    name: str
    niche: str
    expertise_areas: List[str] = Field(default_factory=list)
    current_audience_size: Optional[int] = None
    unique_perspective: Optional[str] = Field(None, description="What makes this brand unique")
    content_pillars: List[str] = Field(default_factory=list, description="Main content themes")
    monetization_model: Optional[str] = None  # e.g., "courses", "consulting", "sponsorships"


class ExecutiveBrandProfile(BaseModel):
    """Profile for executive/thought leader brands."""
    executive_name: str
    company: str
    title: str
    industry_focus: str
    thought_leadership_topics: List[str] = Field(default_factory=list)
    speaking_experience: Optional[str] = None
    publications: List[str] = Field(default_factory=list)
    board_positions: List[str] = Field(default_factory=list)


class AgencyProfile(BaseModel):
    """Profile for marketing agencies."""
    agency_name: str
    client_name: str
    client_industry: str
    campaign_objectives: List[str] = Field(default_factory=list)
    reporting_requirements: Optional[str] = None
    approval_workflow: Optional[str] = None


class StylePreferences(BaseModel):
    """User's content style preferences."""
    tone: Literal["professional", "casual", "inspirational", "educational", "witty", "authoritative"] = Field(
        default="professional"
    )
    formality_level: int = Field(default=5, ge=1, le=10, description="1=very casual, 10=very formal")
    emoji_usage: Literal["none", "minimal", "moderate", "heavy"] = Field(default="minimal")
    average_post_length: Literal["short", "medium", "long"] = Field(default="medium")
    visual_style: Optional[str] = Field(None, description="Preferred visual aesthetic")


class OnboardingProfile(BaseModel):
    """
    Complete onboarding profile capturing all information needed
    to generate a personalized marketing strategy.
    """
    id: Optional[UUID] = None
    workspace_id: UUID
    entity_type: Literal["business", "personal_brand", "executive", "agency"]
    
    # Entity-specific profiles (only one will be populated based on entity_type)
    business: Optional[BusinessProfile] = None
    personal_brand: Optional[PersonalBrandProfile] = None
    executive: Optional[ExecutiveBrandProfile] = None
    agency: Optional[AgencyProfile] = None
    
    # Universal fields
    clarity_statement: Optional[str] = Field(
        None, 
        description="One-line description of what the entity does and for whom"
    )
    goals: List[Goal] = Field(default_factory=list)
    constraints: Constraints = Field(default_factory=Constraints)
    channels: ChannelFootprint = Field(default_factory=ChannelFootprint)
    personas: List[PersonaInput] = Field(default_factory=list, description="Initial ICP inputs")
    style_preferences: StylePreferences = Field(default_factory=StylePreferences)
    
    # Metadata
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "workspace_id": "550e8400-e29b-41d4-a716-446655440000",
                "entity_type": "business",
                "business": {
                    "company_name": "Acme SaaS",
                    "industry": "B2B Software",
                    "company_size": "11-50",
                    "value_proposition": "We help sales teams close faster with AI-powered insights",
                    "proof_points": ["500+ customers", "30% average increase in close rates"]
                },
                "clarity_statement": "We provide AI sales insights for mid-market B2B companies",
                "goals": [
                    {
                        "description": "Generate 100 qualified leads",
                        "timeframe_days": 90,
                        "priority": "high",
                        "metrics": ["MQLs", "demo requests"]
                    }
                ],
                "channels": {
                    "linkedin": True,
                    "email": True,
                    "blog": True
                },
                "personas": [
                    {
                        "nickname": "VP Victor",
                        "role": "VP of Sales",
                        "biggest_pain_point": "Sales team missing quota consistently"
                    }
                ]
            }
        }


class OnboardingAnswer(BaseModel):
    """A single answer in the onboarding questionnaire."""
    question_id: str
    question_text: str
    answer: str  # Free-form text or structured JSON
    answered_at: datetime = Field(default_factory=datetime.utcnow)


class OnboardingSession(BaseModel):
    """Tracks an in-progress onboarding session."""
    session_id: UUID
    workspace_id: UUID
    entity_type: Optional[Literal["business", "personal_brand", "executive", "agency"]] = None
    current_step: int = Field(default=1)
    answers: List[OnboardingAnswer] = Field(default_factory=list)
    profile: Optional[OnboardingProfile] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed: bool = Field(default=False)

