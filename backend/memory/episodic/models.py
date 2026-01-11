"""
Episodic memory models and data structures.

This module defines the core data structures for episodic memory,
including episodes and conversation turns.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class ConversationTurn:
    """Single conversation turn within an episode."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    episode_id: str = ""
    role: str = "user"  # user, assistant, system, tool
    content: str = ""
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    tool_results: List[Dict[str, Any]] = field(default_factory=list)
    turn_index: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    token_count: int = 0
    processing_time_ms: Optional[int] = None
    model_used: Optional[str] = None

    def __post_init__(self):
        """Initialize default values."""
        if not self.id:
            self.id = str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "episode_id": self.episode_id,
            "role": self.role,
            "content": self.content,
            "tool_calls": self.tool_calls,
            "tool_results": self.tool_results,
            "turn_index": self.turn_index,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "token_count": self.token_count,
            "processing_time_ms": self.processing_time_ms,
            "model_used": self.model_used,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationTurn":
        """Create from dictionary."""
        if data.get("timestamp"):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])

        return cls(**data)

    def is_user_turn(self) -> bool:
        """Check if this is a user turn."""
        return self.role == "user"

    def is_assistant_turn(self) -> bool:
        """Check if this is an assistant turn."""
        return self.role == "assistant"

    def is_system_turn(self) -> bool:
        """Check if this is a system turn."""
        return self.role == "system"

    def is_tool_turn(self) -> bool:
        """Check if this is a tool turn."""
        return self.role == "tool"

    def has_tool_calls(self) -> bool:
        """Check if this turn has tool calls."""
        return len(self.tool_calls) > 0

    def get_duration_estimate(self) -> float:
        """Get estimated duration in seconds based on token count."""
        # Rough estimate: 4 tokens per second for reading, 2 tokens per second for generation
        if self.is_assistant_turn():
            return self.token_count / 2.0 if self.token_count > 0 else 1.0
        else:
            return self.token_count / 4.0 if self.token_count > 0 else 0.5

    def __str__(self) -> str:
        """String representation."""
        content_preview = (
            self.content[:50] + "..." if len(self.content) > 50 else self.content
        )
        return f"ConversationTurn(role={self.role}, content='{content_preview}')"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"ConversationTurn(id={self.id}, episode_id={self.episode_id}, "
            f"role={self.role}, turn_index={self.turn_index}, "
            f"content_length={len(self.content)})"
        )


@dataclass
class Episode:
    """Single episode in episodic memory."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workspace_id: str = ""
    user_id: str = ""
    session_id: str = ""
    episode_type: str = (
        "conversation"  # conversation, task, approval, feedback, decision, research
    )
    title: str = ""
    content: str = ""
    summary: str = ""
    key_decisions: List[Dict[str, Any]] = field(default_factory=list)
    entities_mentioned: List[Dict[str, Any]] = field(default_factory=list)
    action_items: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    importance: float = 1.0  # 0.0 to 1.0
    tags: List[str] = field(default_factory=list)
    turns: List[ConversationTurn] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None
    token_count: int = 0
    message_count: int = 0

    def __post_init__(self):
        """Initialize default values."""
        if not self.id:
            self.id = str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "workspace_id": self.workspace_id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "episode_type": self.episode_type,
            "title": self.title,
            "content": self.content,
            "summary": self.summary,
            "key_decisions": self.key_decisions,
            "entities_mentioned": self.entities_mentioned,
            "action_items": self.action_items,
            "metadata": self.metadata,
            "importance": self.importance,
            "tags": self.tags,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "token_count": self.token_count,
            "message_count": self.message_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Episode":
        """Create from dictionary."""
        if data.get("started_at"):
            data["started_at"] = datetime.fromisoformat(data["started_at"])
        if data.get("ended_at"):
            data["ended_at"] = datetime.fromisoformat(data["ended_at"])

        return cls(**data)

    def add_turn(self, turn: ConversationTurn):
        """Add a conversation turn to the episode."""
        turn.episode_id = self.id
        turn.turn_index = len(self.turns)
        self.turns.append(turn)
        self.message_count += 1
        self.token_count += turn.token_count

    def get_duration_seconds(self) -> Optional[int]:
        """Get episode duration in seconds."""
        if self.ended_at:
            return int((self.ended_at - self.started_at).total_seconds())
        return None

    def is_active(self) -> bool:
        """Check if episode is still active."""
        return self.ended_at is None

    def end_episode(self):
        """Mark episode as ended."""
        self.ended_at = datetime.now()

    def get_user_turns(self) -> List[ConversationTurn]:
        """Get all user turns."""
        return [turn for turn in self.turns if turn.is_user_turn()]

    def get_assistant_turns(self) -> List[ConversationTurn]:
        """Get all assistant turns."""
        return [turn for turn in self.turns if turn.is_assistant_turn()]

    def get_tool_turns(self) -> List[ConversationTurn]:
        """Get all tool turns."""
        return [turn for turn in self.turns if turn.is_tool_turn()]

    def get_turn_by_index(self, index: int) -> Optional[ConversationTurn]:
        """Get turn by index."""
        if 0 <= index < len(self.turns):
            return self.turns[index]
        return None

    def get_last_turn(self) -> Optional[ConversationTurn]:
        """Get the last turn."""
        return self.turns[-1] if self.turns else None

    def get_content_preview(self, max_length: int = 100) -> str:
        """Get content preview."""
        if len(self.content) <= max_length:
            return self.content
        return self.content[: max_length - 3] + "..."

    def add_key_decision(self, decision: str, context: str = ""):
        """Add a key decision."""
        self.key_decisions.append(
            {
                "decision": decision,
                "context": context,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def add_action_item(
        self, action: str, assignee: str = "", priority: str = "medium"
    ):
        """Add an action item."""
        self.action_items.append(
            {
                "action": action,
                "assignee": assignee,
                "priority": priority,
                "timestamp": datetime.now().isoformat(),
                "completed": False,
            }
        )

    def add_entity_mention(self, entity_name: str, entity_type: str, context: str = ""):
        """Add an entity mention."""
        self.entities_mentioned.append(
            {
                "entity_name": entity_name,
                "entity_type": entity_type,
                "context": context,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def get_turn_count_by_role(self) -> Dict[str, int]:
        """Get turn count by role."""
        counts = {}
        for turn in self.turns:
            counts[turn.role] = counts.get(turn.role, 0) + 1
        return counts

    def calculate_importance_score(self) -> float:
        """Calculate importance score based on various factors."""
        score = 0.5  # Base score

        # Factor in message count
        if self.message_count > 10:
            score += 0.2
        elif self.message_count > 5:
            score += 0.1

        # Factor in duration
        duration = self.get_duration_seconds()
        if duration and duration > 300:  # 5 minutes
            score += 0.1

        # Factor in key decisions
        if len(self.key_decisions) > 0:
            score += 0.1 * min(len(self.key_decisions), 3)

        # Factor in action items
        if len(self.action_items) > 0:
            score += 0.05 * min(len(self.action_items), 5)

        # Factor in entities mentioned
        if len(self.entities_mentioned) > 0:
            score += 0.05 * min(len(self.entities_mentioned), 10)

        return min(score, 1.0)

    def __str__(self) -> str:
        """String representation."""
        title = self.title or "Untitled"
        return f"Episode(id={self.id}, type={self.episode_type}, title='{title}')"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"Episode(id={self.id}, workspace_id={self.workspace_id}, "
            f"session_id={self.session_id}, type={self.episode_type}, "
            f"turns={len(self.turns)}, duration={self.get_duration_seconds()}s)"
        )
