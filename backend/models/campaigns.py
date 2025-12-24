from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


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
    progress: float = Field(
        default=0.0, description="Total campaign completion (0.0 to 1.0)"
    )
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # SOTA Data Blobs
    arc_data: Optional[dict] = None
    kpi_targets: Optional[dict] = None
    audit_data: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)


class GanttItem(BaseModel):
    """SOTA structured task for Gantt visualization."""

    id: UUID = Field(default_factory=uuid4)
    task: str
    start_date: datetime
    end_date: datetime
    dependency_ids: List[UUID] = Field(default_factory=list)
    progress: float = 0.0  # 0.0 to 1.0


class GanttChart(BaseModel):
    """Collection of tasks for a campaign timeline."""

    items: List[GanttItem]
