from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class MoveStatus(str, Enum):
    """Possible statuses for a move."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"


class Move(BaseModel):
    """Pydantic model for Move."""

    id: UUID = Field(default_factory=uuid4)
    campaign_id: Optional[UUID] = None
    title: str
    description: Optional[str] = None
    consensus_metrics: Dict[str, float] = Field(default_factory=dict)
    decree: Optional[str] = None
    refinement_data: Dict[str, Any] = Field(default_factory=dict)
    campaign_name: Optional[str] = None
    status: MoveStatus = MoveStatus.PENDING
    agent_id: Optional[str] = None
    thread_id: Optional[str] = None
    execution_result: Dict[str, Any] = Field(default_factory=dict)
    approval_comment: Optional[str] = None
    reasoning_chain_id: Optional[str] = None
    checklist: List[Dict[str, Any]] = Field(default_factory=list)
    assets: List[Dict[str, Any]] = Field(default_factory=list)
    daily_metrics: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: Optional[float] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    paused_at: Optional[datetime] = None
    rag_status: Optional[str] = None
    rag_reason: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(from_attributes=True)


class MovePacket(BaseModel):
    """
    SOTA Move Packet.
    The final execution-ready structure for a 'Move'.
    """

    id: UUID = Field(default_factory=uuid4)
    move_id: UUID  # Reference to the parent Move
    title: str
    description: str
    owner: str = Field(
        default="Agent", description="Who executes this move (Agent/Human)"
    )
    required_tools: list[str] = Field(default_factory=list)
    priority: str = "P1"
    deadline: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(from_attributes=True)
