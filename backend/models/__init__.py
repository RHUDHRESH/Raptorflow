"""
Pydantic models for RaptorFlow backend.
"""

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
    Demographics,
    Psychographics,
    Communication,
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
)

__all__ = [
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
    "Demographics",
    "Psychographics",
    "Communication",
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
]
