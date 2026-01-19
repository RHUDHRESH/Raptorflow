"""
Event type definitions for the Raptorflow event system.
"""

import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class EventType(str, Enum):
    """Event types for the system."""

    FOUNDATION_UPDATED = "foundation_updated"
    ICP_CREATED = "icp_created"
    ICP_UPDATED = "icp_updated"
    ICP_DELETED = "icp_deleted"
    MOVE_STARTED = "move_started"
    MOVE_COMPLETED = "move_completed"
    MOVE_FAILED = "move_failed"
    CONTENT_GENERATED = "content_generated"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_GRANTED = "approval_granted"
    APPROVAL_DENIED = "approval_denied"
    USAGE_LIMIT_REACHED = "usage_limit_reached"
    USAGE_LIMIT_EXCEEDED = "usage_limit_exceeded"
    AGENT_EXECUTION_STARTED = "agent_execution_started"
    AGENT_EXECUTION_COMPLETED = "agent_execution_completed"
    AGENT_EXECUTION_FAILED = "agent_execution_failed"
    USER_REGISTERED = "user_registered"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    WORKSPACE_CREATED = "workspace_created"
    WORKSPACE_UPDATED = "workspace_updated"
    WORKSPACE_DELETED = "workspace_deleted"
    BILLING_EVENT = "billing_event"
    SYSTEM_ALERT = "system_alert"
    WEBHOOK_RECEIVED = "webhook_received"
    JOB_STARTED = "job_started"
    JOB_COMPLETED = "job_completed"
    JOB_FAILED = "job_failed"


@dataclass
class Event:
    """Base event structure."""

    event_id: str
    event_type: EventType
    timestamp: datetime
    source: str
    user_id: Optional[str] = None
    workspace_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Generate event_id if not provided."""
        if not self.event_id:
            self.event_id = str(uuid.uuid4())

        if self.data is None:
            self.data = {}

        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "user_id": self.user_id,
            "workspace_id": self.workspace_id,
            "data": self.data,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        """Create event from dictionary."""
        return cls(
            event_id=data["event_id"],
            event_type=EventType(data["event_type"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            source=data["source"],
            user_id=data.get("user_id"),
            workspace_id=data.get("workspace_id"),
            data=data.get("data", {}),
            metadata=data.get("metadata", {}),
        )


# Specific event types for better type safety
@dataclass
class FoundationUpdatedEvent(Event):
    """Event fired when foundation data is updated."""

    workspace_id: str = ""
    user_id: str = ""
    changes: Dict[str, Any] = None


@dataclass
class ICPCreatedEvent(Event):
    """Event fired when a new ICP is created."""

    workspace_id: str = ""
    user_id: str = ""
    icp_id: str = ""
    icp_name: str = ""
    generation_method: str = "manual"  # "manual", "ai_generated", "template"


@dataclass
class MoveStartedEvent(Event):
    """Event fired when a new move is initiated."""

    workspace_id: str = ""
    user_id: str = ""
    move_id: str = ""
    move_type: str = ""
    agent: str = ""


@dataclass
class ContentGeneratedEvent(Event):
    """Event fired when content is generated."""

    workspace_id: str = ""
    user_id: str = ""
    content_type: str = ""
    tokens_used: int = 0
    cost: float = 0.0


@dataclass
class ApprovalRequestedEvent(Event):
    """Event fired when content approval is requested."""

    workspace_id: str = ""
    user_id: str = ""
    approver_id: str = ""
    content_id: str = ""
    content_type: str = ""


@dataclass
class UsageLimitReachedEvent(Event):
    """Event fired when usage limit is reached."""

    workspace_id: str = ""
    limit_type: str = ""  # "tokens", "cost", "requests"
    current_usage: float = 0.0
    limit: float = 0.0
    percentage_used: float = 0.0


@dataclass
class AgentExecutionEvent(Event):
    """Event fired for agent execution lifecycle."""

    workspace_id: str = ""
    user_id: str = ""
    agent_name: str = ""
    execution_id: str = ""
    input_data: Dict[str, Any] = None
    output_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
