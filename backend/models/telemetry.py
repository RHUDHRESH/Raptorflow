from typing import Any, Dict, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class TelemetryLog(BaseModel):
    """Pydantic model for Blackbox Telemetry."""

    id: UUID = Field(default_factory=uuid4)
    tenant_id: UUID
    entity_type: str  # move, campaign, agent
    entity_id: UUID
    event_type: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(from_attributes=True)


class OutcomeMetric(BaseModel):
    """Pydantic model for Blackbox Outcomes."""

    id: UUID = Field(default_factory=uuid4)
    campaign_id: UUID
    move_id: Optional[UUID] = None
    metric_name: str
    metric_value: float
    attributed_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(from_attributes=True)
