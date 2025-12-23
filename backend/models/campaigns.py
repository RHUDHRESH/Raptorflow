from enum import Enum
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class CampaignStatus(str, Enum):
    """Possible statuses for a campaign."""

    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Campaign(BaseModel):
    """Pydantic model for Campaign."""

    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    title: str
    objective: Optional[str] = None
    status: CampaignStatus = CampaignStatus.DRAFT
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(from_attributes=True)
