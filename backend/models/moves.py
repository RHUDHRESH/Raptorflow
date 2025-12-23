from enum import Enum
from typing import Optional, Any, Dict
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


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
    campaign_id: UUID
    title: str
    description: Optional[str] = None
    status: MoveStatus = MoveStatus.PENDING
    agent_id: Optional[str] = None
    thread_id: Optional[str] = None
    execution_result: Dict[str, Any] = Field(default_factory=dict)
    approval_comment: Optional[str] = None
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
    owner: str = Field(default="Agent", description="Who executes this move (Agent/Human)")
    required_tools: list[str] = Field(default_factory=list)
    priority: str = "P1"
    deadline: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(from_attributes=True)
