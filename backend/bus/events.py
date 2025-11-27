"""
BusEvent models for RaptorBus message schema validation.

Pydantic-based type-safe event definitions with schema versioning.
"""

from typing import Any, Dict, Optional
from datetime import datetime
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field, ConfigDict


class EventPriority(str, Enum):
    """Message priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class BusEvent(BaseModel):
    """
    Base event model for RaptorBus messages.

    All messages published to RaptorBus must conform to this schema.
    Includes metadata for routing, tracking, and retry logic.
    """

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique event ID for tracking and deduplication"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO 8601 timestamp when event was created"
    )
    type: str = Field(
        ...,
        description="Event type: asset_generated, research_complete, lord_heartbeat, etc"
    )
    priority: EventPriority = Field(
        default=EventPriority.NORMAL,
        description="Message priority affecting routing and retry behavior"
    )
    source_agent_id: Optional[str] = Field(
        default=None,
        description="ID of agent that published this event (e.g., RES-001, MUS-015)"
    )
    destination_guild: Optional[str] = Field(
        default=None,
        description="Target guild (research, muse, matrix, guardians) if applicable"
    )
    request_id: Optional[str] = Field(
        default=None,
        description="Correlation ID for request/response tracking"
    )
    payload: Dict[str, Any] = Field(
        default_factory=dict,
        description="Event-specific data"
    )
    version: str = Field(
        default="1.0",
        description="Schema version for backward compatibility"
    )
    retry_count: int = Field(
        default=0,
        description="Number of times this message has been retried"
    )
    max_retries: int = Field(
        default=3,
        description="Maximum retry attempts before sending to DLQ"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "evt-a1b2c3d4-e5f6",
                "timestamp": "2024-11-27T10:30:00.000Z",
                "type": "asset_generated",
                "priority": "normal",
                "source_agent_id": "MUS-011",
                "destination_guild": "muse",
                "request_id": "req-789",
                "payload": {
                    "asset_id": "ast-456",
                    "type": "hero_image",
                    "variants": 5,
                    "quality_score": 0.92,
                    "tokens_used": 2500
                },
                "version": "1.0",
                "retry_count": 0,
                "max_retries": 3
            }
        }
    )

    def to_json_str(self) -> str:
        """Serialize event to JSON string for Redis storage."""
        return self.model_dump_json()

    @classmethod
    def from_json_str(cls, json_str: str) -> "BusEvent":
        """Deserialize event from JSON string."""
        return cls.model_validate_json(json_str)


class HeartbeatEvent(BusEvent):
    """Agent heartbeat event (sys.global.heartbeat channel)."""

    type: str = "heartbeat"
    source_agent_id: str  # Required for heartbeats

    class Config:
        json_schema_extra = {
            "example": {
                "id": "evt-hb-123",
                "timestamp": "2024-11-27T10:30:00Z",
                "type": "heartbeat",
                "priority": "high",
                "source_agent_id": "LORD-001",
                "payload": {
                    "status": "healthy",
                    "memory_percent": 45.2,
                    "tasks_in_progress": 3,
                    "total_tokens_used_today": 125000,
                    "budget_remaining": 875000
                }
            }
        }


class AlertEvent(BusEvent):
    """Alert/notification event (sys.alert.* channels)."""

    type: str = Field(..., description="crisis, opportunity, warning, etc")
    severity: str = Field(
        ...,
        description="low, medium, high, critical"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "evt-alert-456",
                "timestamp": "2024-11-27T10:30:00Z",
                "type": "newsjack_opportunity",
                "priority": "critical",
                "severity": "high",
                "payload": {
                    "opportunity": "Trending: AI for healthcare",
                    "relevance_score": 0.89,
                    "suggested_content": "Check out how AI is transforming healthcare...",
                    "expires_in_minutes": 60
                }
            }
        }


class GuildCommandEvent(BusEvent):
    """Command from Lord to Guild (sys.guild.*.broadcast channel)."""

    type: str = "lord_command"
    source_agent_id: str  # Lord ID
    destination_guild: str  # Guild name

    class Config:
        json_schema_extra = {
            "example": {
                "id": "evt-cmd-789",
                "timestamp": "2024-11-27T10:30:00Z",
                "type": "lord_command",
                "priority": "high",
                "source_agent_id": "LORD-002",
                "destination_guild": "research",
                "request_id": "req-123",
                "payload": {
                    "command": "analyze_market",
                    "context": {
                        "positioning": {...},
                        "personas": [...],
                        "budget": 5000,
                        "timeline": 8
                    },
                    "deadline": 300
                }
            }
        }


class StateUpdateEvent(BusEvent):
    """Real-time state update for frontend (sys.state.update channel)."""

    type: str = "state_update"

    class Config:
        json_schema_extra = {
            "example": {
                "id": "evt-state-111",
                "timestamp": "2024-11-27T10:30:00Z",
                "type": "state_update",
                "priority": "normal",
                "payload": {
                    "state_type": "campaign_created",
                    "campaign_id": "camp-123",
                    "status": "assets_generating",
                    "update": {
                        "war_brief_complete": True,
                        "assets_in_progress": 5
                    }
                }
            }
        }
