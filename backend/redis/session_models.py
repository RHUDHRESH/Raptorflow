"""
Session data models for Redis-based session management.
"""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class SessionMessage:
    """Individual message in a session."""

    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SessionData:
    """Session data stored in Redis."""

    session_id: str
    user_id: str
    workspace_id: str

    # Current state
    current_agent: Optional[str] = None
    current_task: Optional[str] = None

    # Conversation history
    messages: List[Dict[str, Any]] = field(default_factory=list)

    # Context data
    context: Dict[str, Any] = field(default_factory=dict)
    foundation_summary: Optional[str] = None
    active_icps: List[Dict[str, Any]] = field(default_factory=list)

    # Approval system
    pending_approvals: List[Dict[str, Any]] = field(default_factory=list)
    last_output: Optional[Dict[str, Any]] = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    last_active_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

    # Session settings
    settings: Dict[str, Any] = field(default_factory=dict)

    # Security fields
    workspace_signature: Optional[str] = None

    def __post_init__(self):
        """Post-initialization processing."""
        # Convert string timestamps to datetime if needed
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.last_active_at, str):
            self.last_active_at = datetime.fromisoformat(self.last_active_at)
        if isinstance(self.expires_at, str):
            self.expires_at = datetime.fromisoformat(self.expires_at)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        data["created_at"] = self.created_at.isoformat()
        data["last_active_at"] = self.last_active_at.isoformat()
        if self.expires_at:
            data["expires_at"] = self.expires_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionData":
        """Create from dictionary."""
        return cls(**data)

    def add_message(
        self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ):
        """Add a message to the session."""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        }
        self.messages.append(message)
        self.last_active_at = datetime.now()

        # Keep only last 20 messages to prevent bloat
        if len(self.messages) > 20:
            self.messages = self.messages[-20:]

    def update_context(self, key: str, value: Any):
        """Update context data."""
        self.context[key] = value
        self.last_active_at = datetime.now()

    def set_current_agent(self, agent_name: str):
        """Set the currently active agent."""
        self.current_agent = agent_name
        self.last_active_at = datetime.now()

    def add_pending_approval(self, approval_data: Dict[str, Any]):
        """Add a pending approval request."""
        self.pending_approvals.append(approval_data)
        self.last_active_at = datetime.now()

    def remove_pending_approval(self, approval_id: str):
        """Remove a pending approval request."""
        self.pending_approvals = [
            approval
            for approval in self.pending_approvals
            if approval.get("id") != approval_id
        ]
        self.last_active_at = datetime.now()

    def is_expired(self) -> bool:
        """Check if session is expired."""
        if not self.expires_at:
            return False
        return datetime.now() > self.expires_at

    def extend_expiry(self, seconds: int):
        """Extend session expiry."""
        if self.expires_at:
            self.expires_at = self.expires_at.replace(
                second=self.expires_at.second + seconds
            )
        else:
            self.expires_at = datetime.now().replace(
                second=datetime.now().second + seconds
            )

    def get_summary(self) -> Dict[str, Any]:
        """Get session summary for debugging."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "workspace_id": self.workspace_id,
            "current_agent": self.current_agent,
            "message_count": len(self.messages),
            "pending_approvals": len(self.pending_approvals),
            "created_at": self.created_at.isoformat(),
            "last_active_at": self.last_active_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_expired": self.is_expired(),
        }
