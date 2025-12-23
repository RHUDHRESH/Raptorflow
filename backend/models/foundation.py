from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


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
