from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class AgentMessage(BaseModel):
    """Represents a single message in an agent conversation."""

    id: UUID = Field(default_factory=uuid4)
    role: str  # researcher, strategist, creator, critic, human
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


class AgentThread(BaseModel):
    """Represents a persistent conversation thread for an agentic run."""

    id: str
    tenant_id: UUID
    move_id: Optional[UUID] = None
    messages: List[AgentMessage] = Field(default_factory=list)
    state: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(from_attributes=True)
