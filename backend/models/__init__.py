"""
Pydantic models for RaptorFlow backend.
"""

from backend.models.base import BaseSchema
from backend.models.onboarding import (
    OnboardingProfile,
    OnboardingSession,
    OnboardingAnswer,
    PersonaInput,
    Goal,
    Constraints,
    ChannelFootprint,
    BusinessProfile,
    PersonalBrandProfile,
    ExecutiveBrandProfile,
    AgencyProfile,
    StylePreferences,
)

from backend.models.persona import (
    ICPProfile,
    ICPRequest,
    ICPResponse,
    Cohort,
    Demographics,
    Psychographics,
    Communication,
    PersonaNarrative,
)

from backend.models.campaign import (
    MoveRequest,
    MoveResponse,
    MoveMetrics,
    Task,
    Sprint,
    LineOfOperation,
    AssetRequirement,
    ChecklistItem,
    TaskUpdateRequest,
    MoveDecision,
    MoveAnomaly,
)

from backend.models.content import (
    BlogRequest,
    BlogResponse,
    EmailRequest,
    SocialPostRequest,
    ContentRequest,
    ContentResponse,
    ContentVariant,
    Hook,
    ContentApprovalRequest,
    BulkContentRequest,
    ContentCalendar,
    ContentCalendarEntry,
    AssetMetadata,
    BrandVoiceProfile,
    ContentMetadata,
    EmailMessage,
)

__all__ = [
    # Base
    "BaseSchema",
    # Onboarding
    "OnboardingProfile",
    "OnboardingSession",
    "OnboardingAnswer",
    "PersonaInput",
    "Goal",
    "Constraints",
    "ChannelFootprint",
    "BusinessProfile",
    "PersonalBrandProfile",
    "ExecutiveBrandProfile",
    "AgencyProfile",
    "StylePreferences",
    # Persona
    "ICPProfile",
    "ICPRequest",
    "ICPResponse",
    "Cohort",
    "Demographics",
    "Psychographics",
    "Communication",
    "PersonaNarrative",
    # Campaign
    "MoveRequest",
    "MoveResponse",
    "MoveMetrics",
    "Task",
    "Sprint",
    "LineOfOperation",
    "AssetRequirement",
    "ChecklistItem",
    "TaskUpdateRequest",
    "MoveDecision",
    "MoveAnomaly",
    # Content
    "BlogRequest",
    "BlogResponse",
    "EmailRequest",
    "SocialPostRequest",
    "ContentRequest",
    "ContentResponse",
    "ContentVariant",
    "Hook",
    "ContentApprovalRequest",
    "BulkContentRequest",
    "ContentCalendar",
    "ContentCalendarEntry",
    "AssetMetadata",
    "BrandVoiceProfile",
    "ContentMetadata",
    "EmailMessage",
]
