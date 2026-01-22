"""
Agent Message Protocol - Standardized message format

Defines the standard message format for agent communication
with proper typing, validation, and metadata.
"""

import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Union

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """Types of agent messages."""

    REQUEST = "request"
    RESPONSE = "response"
    ERROR = "error"
    HANDOFF = "handoff"
    NOTIFICATION = "notification"
    HEARTBEAT = "heartbeat"
    STATUS_UPDATE = "status_update"


class MessagePriority(str, Enum):
    """Message priority levels."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AgentMessage:
    """Standard agent message format."""

    # Core message fields
    from_agent: str
    to_agent: str
    message_type: MessageType
    payload: Dict[str, Any]

    # Metadata
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    reply_to: Optional[str] = None
    priority: MessagePriority = MessagePriority.NORMAL

    # Protocol information
    protocol_version: str = "1.0"
    content_type: str = "application/json"

    # Routing and tracking
    routing_path: list[str] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3

    # Performance metrics
    processing_time_ms: Optional[float] = None
    queue_time_ms: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "message_type": self.message_type.value,
            "payload": self.payload,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat(),
            "reply_to": self.reply_to,
            "priority": self.priority.value,
            "protocol_version": self.protocol_version,
            "content_type": self.content_type,
            "routing_path": self.routing_path,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "processing_time_ms": self.processing_time_ms,
            "queue_time_ms": self.queue_time_ms,
        }

    def to_json(self) -> str:
        """Convert message to JSON string."""
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentMessage":
        """Create message from dictionary."""
        # Handle timestamp conversion
        if isinstance(data.get("timestamp"), str):
            data["timestamp"] = datetime.fromisoformat(
                data["timestamp"].replace("Z", "+00:00")
            )

        # Handle enum conversions
        if isinstance(data.get("message_type"), str):
            data["message_type"] = MessageType(data["message_type"])

        if isinstance(data.get("priority"), str):
            data["priority"] = MessagePriority(data["priority"])

        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> "AgentMessage":
        """Create message from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def create_reply(
        self, payload: Dict[str, Any], message_type: MessageType = MessageType.RESPONSE
    ) -> "AgentMessage":
        """Create a reply message."""
        return AgentMessage(
            from_agent=self.to_agent,
            to_agent=self.from_agent,
            message_type=message_type,
            payload=payload,
            correlation_id=self.correlation_id,
            reply_to=self.correlation_id,
            priority=self.priority,
            protocol_version=self.protocol_version,
        )

    def create_error_reply(
        self,
        error_code: str,
        error_message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> "AgentMessage":
        """Create an error reply message."""
        error_payload = {
            "error_code": error_code,
            "error_message": error_message,
            "details": details or {},
            "original_correlation_id": self.correlation_id,
        }

        return self.create_reply(error_payload, MessageType.ERROR)

    def add_routing_step(self, agent_id: str) -> None:
        """Add agent to routing path."""
        if agent_id not in self.routing_path:
            self.routing_path.append(agent_id)

    def increment_retry(self) -> bool:
        """Increment retry count and check if max retries reached."""
        self.retry_count += 1
        return self.retry_count <= self.max_retries

    def is_expired(self, timeout_seconds: int = 300) -> bool:
        """Check if message has expired."""
        age_seconds = (datetime.now() - self.timestamp).total_seconds()
        return age_seconds > timeout_seconds


class MessageFormat:
    """Message format utilities and validation."""

    @staticmethod
    def validate_message(message: AgentMessage) -> bool:
        """Validate message format and required fields."""
        try:
            # Check required fields
            if not message.from_agent:
                logger.error("Missing from_agent field")
                return False

            if not message.to_agent:
                logger.error("Missing to_agent field")
                return False

            if not message.message_type:
                logger.error("Missing message_type field")
                return False

            if not isinstance(message.payload, dict):
                logger.error("Payload must be a dictionary")
                return False

            # Validate correlation ID
            if not message.correlation_id:
                logger.error("Missing correlation_id")
                return False

            # Validate timestamp
            if not isinstance(message.timestamp, datetime):
                logger.error("Invalid timestamp format")
                return False

            return True

        except Exception as e:
            logger.error(f"Message validation failed: {e}")
            return False

    @staticmethod
    def sanitize_message(message: AgentMessage) -> AgentMessage:
        """Sanitize message for safe transmission."""
        # Create a copy to avoid modifying original
        sanitized = AgentMessage(
            from_agent=str(message.from_agent)[:100],  # Limit length
            to_agent=str(message.to_agent)[:100],
            message_type=message.message_type,
            payload=message.payload,
            correlation_id=message.correlation_id,
            timestamp=message.timestamp,
            reply_to=message.reply_to,
            priority=message.priority,
            protocol_version=message.protocol_version,
            content_type=message.content_type,
            routing_path=message.routing_path[:10],  # Limit routing path length
            retry_count=min(message.retry_count, 10),  # Cap retry count
            max_retries=min(message.max_retries, 10),
            processing_time_ms=message.processing_time_ms,
            queue_time_ms=message.queue_time_ms,
        )

        return sanitized

    @staticmethod
    def create_heartbeat(from_agent: str, to_agent: str = "system") -> AgentMessage:
        """Create a heartbeat message."""
        return AgentMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=MessageType.HEARTBEAT,
            payload={"status": "alive", "timestamp": datetime.now().isoformat()},
            priority=MessagePriority.LOW,
        )

    @staticmethod
    def create_status_update(
        from_agent: str, status: Dict[str, Any], to_agent: str = "system"
    ) -> AgentMessage:
        """Create a status update message."""
        return AgentMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=MessageType.STATUS_UPDATE,
            payload={"status": status, "timestamp": datetime.now().isoformat()},
            priority=MessagePriority.NORMAL,
        )

    @staticmethod
    def create_notification(
        from_agent: str, to_agent: str, notification: Dict[str, Any]
    ) -> AgentMessage:
        """Create a notification message."""
        return AgentMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=MessageType.NOTIFICATION,
            payload={
                "notification": notification,
                "timestamp": datetime.now().isoformat(),
            },
            priority=MessagePriority.NORMAL,
        )
