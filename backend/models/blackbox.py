from typing import Any, Dict, List
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class BlackboxTelemetry(BaseModel):
    """Pydantic model for Blackbox Telemetry (Execution Traces)."""

    id: UUID = Field(default_factory=uuid4)
    move_id: UUID
    agent_id: str
    trace: Dict[str, Any] = Field(default_factory=dict)
    tokens: int = 0
    latency: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(from_attributes=True)


class BlackboxOutcome(BaseModel):
    """Pydantic model for Blackbox Outcomes (Conversion/Engagement)."""

    id: UUID = Field(default_factory=uuid4)
    source: str
    value: float
    confidence: float = 1.0
    timestamp: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(from_attributes=True)


class BlackboxLearning(BaseModel):
    """Pydantic model for Blackbox Strategic Learnings."""

    id: UUID = Field(default_factory=uuid4)
    content: str
    embedding: List[float] = Field(default_factory=list)
    source_ids: List[UUID] = Field(default_factory=list)
    learning_type: str  # e.g., tactical, strategic, content
    timestamp: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(from_attributes=True)
