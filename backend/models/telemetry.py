from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class TelemetryEventType(str, Enum):
    INFERENCE_START = "inference_start"
    INFERENCE_END = "inference_end"
    AGENT_START = "agent_start"
    AGENT_END = "agent_end"
    TOOL_START = "tool_start"
    TOOL_END = "tool_end"
    ERROR = "error"
    SYSTEM_HALT = "system_halt"


class TelemetryEvent(BaseModel):
    """Strictly validated telemetry event for the Matrix."""

    event_id: str = Field(..., description="Unique event identifier")
    timestamp: datetime = Field(default_factory=datetime.now)
    event_type: TelemetryEventType
    source: str = Field(..., description="Agent or component name")
    payload: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


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
