from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class FoundationBase(BaseModel):
    """Base model for all foundation entities."""

    model_config = ConfigDict(from_attributes=True)


class BrandKit(FoundationBase):
    """Pydantic model for Brand Kit."""

    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    name: str
    logo_url: Optional[str] = None
    primary_color: str
    secondary_color: str
    accent_color: str
    typography_config: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Positioning(FoundationBase):
    """Pydantic model for Positioning."""

    id: UUID = Field(default_factory=uuid4)
    brand_kit_id: UUID
    uvp: str
    target_market: str
    competitive_advantage: Optional[str] = None
    elevator_pitch: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class VoiceTone(FoundationBase):
    """Pydantic model for Voice and Tone."""

    id: UUID = Field(default_factory=uuid4)
    brand_kit_id: UUID
    tone_name: str
    description: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    examples: List[Dict[str, str]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)


class FoundationState(FoundationBase):
    """Universal state storage for Onboarding JSON."""

    tenant_id: UUID
    data: Dict[str, Any] = Field(default_factory=dict)
    updated_at: datetime = Field(default_factory=datetime.now)


class JTBD(FoundationBase):
    """Pydantic model for Jobs to Be Done."""

    id: UUID = Field(default_factory=uuid4)
    workspace_id: UUID
    functional_job: str
    emotional_job: str
    social_job: str
    context_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class MessageHierarchy(FoundationBase):
    """Pydantic model for Message Hierarchy Pyramid."""

    id: UUID = Field(default_factory=uuid4)
    workspace_id: UUID
    essence: str
    core_message: str
    pillars: List[str] = Field(default_factory=list)
    proof_points: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class AwarenessMatrix(FoundationBase):
    """Pydantic model for Customer Awareness Matrix."""

    id: UUID = Field(default_factory=uuid4)
    workspace_id: UUID
    unaware_strategy: Optional[str] = None
    problem_aware_strategy: Optional[str] = None
    solution_aware_strategy: Optional[str] = None
    product_aware_strategy: Optional[str] = None
    most_aware_strategy: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ProofVaultEntry(FoundationBase):
    """Pydantic model for Evidence & Proof Vault."""

    id: UUID = Field(default_factory=uuid4)
    workspace_id: UUID
    type: str  # stat, testimonial, guarantee, case_study
    content: str
    source_link: Optional[str] = None
    source_name: Optional[str] = None
    is_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class PrecisionSoundbite(FoundationBase):
    """Pydantic model for Precision Soundbites."""

    id: UUID = Field(default_factory=uuid4)
    workspace_id: UUID
    type: str  # problem_revelation, agitation, mechanism, etc.
    content: str
    draft_content: Optional[str] = None
    ai_variation_a: Optional[str] = None
    ai_variation_b: Optional[str] = None
    status: str = "draft"
    clarity_score: Optional[float] = None
    proof_links: List[UUID] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
