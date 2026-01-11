"""
Memory system models and types.

This module defines the core data structures for the memory system,
including memory types and chunks.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np


class MemoryType(Enum):
    """Types of memory stored in the system."""

    FOUNDATION = "foundation"
    ICP = "icp"
    MOVE = "move"
    CAMPAIGN = "campaign"
    RESEARCH = "research"
    CONVERSATION = "conversation"
    FEEDBACK = "feedback"

    @classmethod
    def get_all_types(cls) -> List[str]:
        """Get all memory type values as strings."""
        return [t.value for t in cls]

    @classmethod
    def from_string(cls, value: str) -> "MemoryType":
        """Create MemoryType from string value."""
        for memory_type in cls:
            if memory_type.value == value:
                return memory_type
        raise ValueError(f"Invalid memory type: {value}")


@dataclass
class MemoryChunk:
    """A chunk of memory with embedding and metadata."""

    id: Optional[str] = None
    workspace_id: Optional[str] = None
    memory_type: Optional[MemoryType] = None
    content: str = ""
    metadata: Dict[str, Any] = None
    embedding: Optional[np.ndarray] = None
    score: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    reference_id: Optional[str] = None
    reference_table: Optional[str] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "workspace_id": self.workspace_id,
            "memory_type": self.memory_type.value if self.memory_type else None,
            "content": self.content,
            "metadata": self.metadata,
            "score": self.score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "reference_id": self.reference_id,
            "reference_table": self.reference_table,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryChunk":
        """Create from dictionary."""
        # Handle datetime parsing
        if data.get("created_at"):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])

        # Handle memory type
        if data.get("memory_type"):
            data["memory_type"] = MemoryType.from_string(data["memory_type"])

        return cls(**data)

    def get_embedding_list(self) -> Optional[List[float]]:
        """Get embedding as list for JSON serialization."""
        if self.embedding is not None:
            return self.embedding.tolist()
        return None

    def set_embedding_from_list(self, embedding_list: List[float]):
        """Set embedding from list."""
        self.embedding = np.array(embedding_list)

    def add_metadata(self, key: str, value: Any):
        """Add metadata key-value pair."""
        self.metadata[key] = value
        self.updated_at = datetime.now()

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value."""
        return self.metadata.get(key, default)

    def has_metadata(self, key: str) -> bool:
        """Check if metadata key exists."""
        return key in self.metadata

    def is_expired(self, max_age_days: int = 90) -> bool:
        """Check if memory chunk is older than max_age_days."""
        if self.created_at is None:
            return False
        age = datetime.now() - self.created_at
        return age.days > max_age_days

    def get_token_count(self) -> int:
        """Estimate token count (rough approximation: 1 token ≈ 4 characters)."""
        return len(self.content) // 4

    def is_empty(self) -> bool:
        """Check if chunk is empty (no meaningful content)."""
        if not self.content:
            return True

        # Handle None content
        if self.content is None:
            return True

        # Check if content is just whitespace
        if isinstance(self.content, str):
            return self.content.strip() == ""

        # For non-string content, check if it's falsy
        return not bool(self.content)

    def truncate_content(self, max_length: int = 500) -> str:
        """Truncate content to max_length with ellipsis."""
        if len(self.content) <= max_length:
            return self.content
        return self.content[: max_length - 3] + "..."

    def __str__(self) -> str:
        """String representation."""
        type_str = self.memory_type.value if self.memory_type else "unknown"
        content_preview = self.truncate_content(50)
        return f"MemoryChunk(id={self.id}, type={type_str}, content='{content_preview}...')"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"MemoryChunk(id={self.id}, workspace_id={self.workspace_id}, "
            f"memory_type={self.memory_type}, content_length={len(self.content)}, "
            f"metadata_keys={list(self.metadata.keys())})"
        )


# Type aliases for better readability
MemoryChunks = List[MemoryChunk]
MemoryChunkDict = Dict[str, MemoryChunk]
