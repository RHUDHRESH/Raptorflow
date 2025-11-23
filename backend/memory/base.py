"""
Memory Base Module - Abstract Memory Interface

This module defines the abstract base class for all memory implementations in RaptorFlow.
All concrete memory types (conversation, agent, workspace, semantic, working) must implement
this interface to ensure consistent behavior across the memory system.

Purpose:
--------
- Provide a unified interface for all memory operations
- Ensure consistency across different memory implementations
- Enable polymorphic usage of memory backends
- Support dependency injection and testing

Memory Types:
-------------
1. Conversation Memory: Short-term session-based conversation history
2. Agent Memory: Agent-specific learning and performance patterns
3. Workspace Memory: Shared workspace context (ICPs, brand voice, preferences)
4. Semantic Memory: Vector-based semantic search across content
5. Working Memory: Temporary execution state and intermediate results

Core Operations:
----------------
- remember(): Store information in memory
- recall(): Retrieve specific information by key
- search(): Find information using queries (semantic or keyword-based)
- forget(): Remove information from memory
- learn_from_feedback(): Update memory based on feedback/performance

Dependencies:
-------------
- abc: For abstract base classes
- typing: For type hints
- uuid: For workspace and correlation IDs

Usage Example:
--------------
from memory.conversation_memory import ConversationMemory

# Create a memory instance
memory = ConversationMemory()

# Store a message
await memory.remember(
    key="session:123",
    value={"role": "user", "content": "Hello"},
    workspace_id=workspace_id,
    metadata={"timestamp": "2024-01-01T00:00:00"}
)

# Retrieve messages
messages = await memory.recall(key="session:123", workspace_id=workspace_id)

# Search for relevant context
results = await memory.search(query="Hello", workspace_id=workspace_id, top_k=5)
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from uuid import UUID
import structlog

logger = structlog.get_logger()


class BaseMemory(ABC):
    """
    Abstract base class for all memory implementations.

    This class defines the interface that all memory types must implement.
    Concrete implementations should handle specific storage backends and
    use cases while maintaining this consistent interface.

    Attributes:
        memory_type (str): The type of memory (e.g., "conversation", "agent", "workspace")
        logger: Structured logger for tracking memory operations
    """

    def __init__(self, memory_type: str):
        """
        Initialize the base memory instance.

        Args:
            memory_type: Identifier for the type of memory (e.g., "conversation", "agent")
        """
        self.memory_type = memory_type
        self.logger = structlog.get_logger().bind(memory_type=memory_type)

    @abstractmethod
    async def remember(
        self,
        key: str,
        value: Any,
        workspace_id: UUID,
        metadata: Optional[Dict[str, Any]] = None,
        ttl: Optional[int] = None
    ) -> None:
        """
        Store information in memory.

        Args:
            key: Unique identifier for the memory item (e.g., session_id, agent_name)
            value: The data to store (can be dict, list, string, etc.)
            workspace_id: UUID of the workspace this memory belongs to
            metadata: Optional metadata about the memory item (timestamps, tags, etc.)
            ttl: Optional time-to-live in seconds (for expiring memories)

        Raises:
            MemoryError: If storage operation fails

        Example:
            await memory.remember(
                key="session:abc123",
                value={"role": "user", "content": "Hello"},
                workspace_id=UUID("..."),
                metadata={"timestamp": "2024-01-01T00:00:00"},
                ttl=3600
            )
        """
        pass

    @abstractmethod
    async def recall(
        self,
        key: str,
        workspace_id: UUID,
        default: Any = None
    ) -> Any:
        """
        Retrieve specific information from memory by key.

        Args:
            key: Unique identifier for the memory item
            workspace_id: UUID of the workspace
            default: Default value to return if key not found

        Returns:
            The stored value, or default if not found

        Raises:
            MemoryError: If retrieval operation fails

        Example:
            messages = await memory.recall(
                key="session:abc123",
                workspace_id=UUID("..."),
                default=[]
            )
        """
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        workspace_id: UUID,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Any]:
        """
        Search for information in memory using a query.

        For semantic memory, this performs vector similarity search.
        For other memory types, this may perform keyword or pattern matching.

        Args:
            query: Search query (text for semantic search, pattern for others)
            workspace_id: UUID of the workspace
            top_k: Maximum number of results to return
            filters: Optional filters to narrow search (e.g., date range, type)

        Returns:
            List of matching items, ordered by relevance

        Raises:
            MemoryError: If search operation fails

        Example:
            results = await memory.search(
                query="customer pain points",
                workspace_id=UUID("..."),
                top_k=10,
                filters={"date_from": "2024-01-01"}
            )
        """
        pass

    @abstractmethod
    async def forget(
        self,
        key: str,
        workspace_id: UUID
    ) -> bool:
        """
        Remove information from memory.

        Args:
            key: Unique identifier for the memory item to remove
            workspace_id: UUID of the workspace

        Returns:
            True if deletion was successful, False otherwise

        Raises:
            MemoryError: If deletion operation fails

        Example:
            success = await memory.forget(
                key="session:abc123",
                workspace_id=UUID("...")
            )
        """
        pass

    @abstractmethod
    async def learn_from_feedback(
        self,
        key: str,
        feedback: Dict[str, Any],
        workspace_id: UUID
    ) -> None:
        """
        Update memory based on feedback or performance data.

        This method allows the memory system to learn and adapt based on
        outcomes, user feedback, or performance metrics. Primarily used by
        agent memory to track patterns of success and failure.

        Args:
            key: Identifier for what to update (e.g., agent_name, pattern_id)
            feedback: Feedback data containing performance metrics, ratings, etc.
            workspace_id: UUID of the workspace

        Raises:
            MemoryError: If update operation fails

        Example:
            await memory.learn_from_feedback(
                key="campaign_planner",
                feedback={
                    "task": "campaign_planning",
                    "success": True,
                    "metrics": {"engagement_rate": 0.85},
                    "user_rating": 5
                },
                workspace_id=UUID("...")
            )
        """
        pass

    async def clear(self, workspace_id: UUID) -> bool:
        """
        Clear all memory for a specific workspace.

        This is an optional method that can be overridden by concrete implementations.
        Useful for cleanup operations or resetting workspace state.

        Args:
            workspace_id: UUID of the workspace to clear

        Returns:
            True if clearing was successful, False otherwise
        """
        self.logger.warning(
            "clear() not implemented for this memory type",
            workspace_id=str(workspace_id)
        )
        return False

    def _validate_workspace_id(self, workspace_id: UUID) -> None:
        """
        Validate that workspace_id is a valid UUID.

        Args:
            workspace_id: The workspace ID to validate

        Raises:
            ValueError: If workspace_id is not a valid UUID
        """
        if not isinstance(workspace_id, UUID):
            raise ValueError(f"workspace_id must be a UUID, got {type(workspace_id)}")


class MemoryError(Exception):
    """
    Custom exception for memory operation failures.

    This exception should be raised when memory operations fail due to
    storage issues, connection problems, or data validation errors.
    """

    def __init__(self, message: str, memory_type: str = None, operation: str = None):
        """
        Initialize MemoryError with context.

        Args:
            message: Error message
            memory_type: Type of memory where error occurred
            operation: Operation that failed (e.g., "remember", "recall")
        """
        self.memory_type = memory_type
        self.operation = operation
        super().__init__(message)

    def __str__(self):
        context = []
        if self.memory_type:
            context.append(f"memory_type={self.memory_type}")
        if self.operation:
            context.append(f"operation={self.operation}")

        if context:
            return f"{super().__str__()} ({', '.join(context)})"
        return super().__str__()
