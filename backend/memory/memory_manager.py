"""
Memory Manager - Unified Memory Orchestration

This module provides a unified interface for managing all memory types in RaptorFlow.
The MemoryManager orchestrates conversation, agent, workspace, and semantic memory,
providing a single entry point for all memory operations.

Purpose:
--------
- Provide a unified API for all memory operations
- Route requests to appropriate memory backends
- Enable cross-memory operations (e.g., get full context)
- Handle memory initialization and cleanup
- Support correlation IDs for tracking memory operations

Memory Types Managed:
---------------------
1. Conversation Memory: Session-based message history (Redis, TTL 1h)
2. Agent Memory: Agent performance and learning (Redis, persistent)
3. Workspace Memory: Shared workspace context (Supabase, persistent)
4. Semantic Memory: Vector search (ChromaDB, persistent)
5. Working Memory: Temporary execution state (Redis, short TTL)

Key Features:
-------------
- Automatic memory type routing
- Context aggregation across memory types
- Correlation ID tracking for debugging
- Error handling and logging
- Resource cleanup and connection management

Dependencies:
-------------
- memory.conversation_memory: ConversationMemory
- memory.agent_memory: AgentMemory
- memory.workspace_memory: WorkspaceMemory
- memory.semantic_memory: SemanticMemory
- utils.correlation: For correlation ID management
- structlog: For structured logging

Usage Example:
--------------
from memory.memory_manager import MemoryManager
from uuid import UUID

# Initialize memory manager
memory = MemoryManager()

# Store conversation message
await memory.remember(
    memory_type="conversation",
    key="session:abc123",
    value={"role": "user", "content": "Hello"},
    workspace_id=UUID("...")
)

# Retrieve agent patterns
patterns = await memory.recall(
    memory_type="agent",
    key="campaign_planner",
    workspace_id=UUID("...")
)

# Semantic search
results = await memory.search(
    query="AI marketing strategies",
    memory_type="semantic",
    workspace_id=UUID("..."),
    top_k=5
)

# Get comprehensive context for a task
context = await memory.get_context(
    workspace_id=UUID("..."),
    task_type="campaign_planning"
)
# Returns: {
#   "conversation_history": [...],
#   "agent_patterns": {...},
#   "workspace_preferences": {...},
#   "relevant_content": [...]
# }

# Learn from feedback
await memory.learn_from_feedback(
    agent_name="campaign_planner",
    feedback={"success": True, "rating": 5},
    workspace_id=UUID("...")
)

# Cleanup resources
await memory.close()
"""

from typing import Any, Dict, List, Optional
from uuid import UUID
import structlog

from memory.base import BaseMemory, MemoryError
from memory.conversation_memory import ConversationMemory
from memory.agent_memory import AgentMemory
from memory.workspace_memory import WorkspaceMemory
from memory.semantic_memory import SemanticMemory

try:
    from utils.correlation import get_correlation_id
except ImportError:
    # Fallback if correlation module doesn't exist
    def get_correlation_id() -> str:
        return "no-correlation-id"

logger = structlog.get_logger()


class MemoryManager:
    """
    Unified memory manager for all memory types.

    This class provides a single interface for interacting with all memory
    backends. It handles routing, error handling, and resource management.

    Attributes:
        conversation_memory: ConversationMemory instance
        agent_memory: AgentMemory instance
        workspace_memory: WorkspaceMemory instance
        semantic_memory: SemanticMemory instance
        logger: Structured logger with correlation IDs
    """

    def __init__(
        self,
        conversation_ttl: int = 3600,
        max_conversation_messages: int = 100,
        max_agent_feedback: int = 50,
        semantic_persist_dir: str = "./data/chroma",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize memory manager with all memory backends.

        Args:
            conversation_ttl: TTL for conversation sessions in seconds
            max_conversation_messages: Max messages per conversation session
            max_agent_feedback: Max feedback items per agent
            semantic_persist_dir: Directory for ChromaDB persistence
            embedding_model: Model for generating embeddings
        """
        self.logger = structlog.get_logger().bind(component="memory_manager")

        # Initialize memory backends
        try:
            self.conversation_memory = ConversationMemory(
                default_ttl=conversation_ttl,
                max_messages=max_conversation_messages
            )
            self.logger.info("Conversation memory initialized")
        except Exception as e:
            self.logger.warning("Failed to initialize conversation memory", error=str(e))
            self.conversation_memory = None

        try:
            self.agent_memory = AgentMemory(
                max_feedback_history=max_agent_feedback
            )
            self.logger.info("Agent memory initialized")
        except Exception as e:
            self.logger.warning("Failed to initialize agent memory", error=str(e))
            self.agent_memory = None

        try:
            self.workspace_memory = WorkspaceMemory()
            self.logger.info("Workspace memory initialized")
        except Exception as e:
            self.logger.warning("Failed to initialize workspace memory", error=str(e))
            self.workspace_memory = None

        try:
            self.semantic_memory = SemanticMemory(
                persist_directory=semantic_persist_dir,
                embedding_model=embedding_model
            )
            self.logger.info("Semantic memory initialized")
        except Exception as e:
            self.logger.warning("Failed to initialize semantic memory", error=str(e))
            self.semantic_memory = None

    def _get_memory_backend(self, memory_type: str) -> BaseMemory:
        """
        Get the appropriate memory backend for a memory type.

        Args:
            memory_type: Type of memory (conversation, agent, workspace, semantic, working)

        Returns:
            Memory backend instance

        Raises:
            ValueError: If memory type is unknown or backend not available
        """
        memory_map = {
            "conversation": self.conversation_memory,
            "agent": self.agent_memory,
            "workspace": self.workspace_memory,
            "semantic": self.semantic_memory,
            "working": self.conversation_memory,  # Reuse conversation for working memory
        }

        if memory_type not in memory_map:
            raise ValueError(
                f"Unknown memory type: {memory_type}. "
                f"Available types: {list(memory_map.keys())}"
            )

        backend = memory_map[memory_type]
        if backend is None:
            raise ValueError(
                f"Memory backend '{memory_type}' not available. "
                "Check initialization logs for errors."
            )

        return backend

    async def remember(
        self,
        memory_type: str,
        key: str,
        value: Any,
        workspace_id: UUID,
        metadata: Optional[Dict[str, Any]] = None,
        ttl: Optional[int] = None
    ) -> None:
        """
        Store information in the specified memory type.

        Args:
            memory_type: Type of memory (conversation, agent, workspace, semantic)
            key: Unique identifier for the memory item
            value: Data to store
            workspace_id: Workspace UUID
            metadata: Optional metadata
            ttl: Optional TTL in seconds (for conversation/working memory)

        Raises:
            MemoryError: If storage operation fails
            ValueError: If memory type is unknown
        """
        correlation_id = get_correlation_id()

        try:
            backend = self._get_memory_backend(memory_type)

            self.logger.debug(
                "Storing memory",
                memory_type=memory_type,
                key=key,
                workspace_id=str(workspace_id),
                correlation_id=correlation_id
            )

            await backend.remember(
                key=key,
                value=value,
                workspace_id=workspace_id,
                metadata=metadata,
                ttl=ttl
            )

            self.logger.debug(
                "Memory stored successfully",
                memory_type=memory_type,
                key=key,
                correlation_id=correlation_id
            )

        except Exception as e:
            self.logger.error(
                "Failed to store memory",
                memory_type=memory_type,
                key=key,
                error=str(e),
                correlation_id=correlation_id
            )
            raise

    async def recall(
        self,
        memory_type: str,
        key: str,
        workspace_id: UUID,
        default: Any = None
    ) -> Any:
        """
        Retrieve information from the specified memory type.

        Args:
            memory_type: Type of memory to query
            key: Memory item identifier
            workspace_id: Workspace UUID
            default: Default value if not found

        Returns:
            Stored value or default

        Raises:
            MemoryError: If retrieval operation fails
            ValueError: If memory type is unknown
        """
        correlation_id = get_correlation_id()

        try:
            backend = self._get_memory_backend(memory_type)

            self.logger.debug(
                "Recalling memory",
                memory_type=memory_type,
                key=key,
                workspace_id=str(workspace_id),
                correlation_id=correlation_id
            )

            result = await backend.recall(
                key=key,
                workspace_id=workspace_id,
                default=default
            )

            self.logger.debug(
                "Memory recalled successfully",
                memory_type=memory_type,
                key=key,
                found=result is not None,
                correlation_id=correlation_id
            )

            return result

        except Exception as e:
            self.logger.error(
                "Failed to recall memory",
                memory_type=memory_type,
                key=key,
                error=str(e),
                correlation_id=correlation_id
            )
            raise

    async def search(
        self,
        query: str,
        memory_type: str,
        workspace_id: UUID,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Any]:
        """
        Search for information in the specified memory type.

        Args:
            query: Search query
            memory_type: Type of memory to search
            workspace_id: Workspace UUID
            top_k: Maximum results to return
            filters: Optional search filters

        Returns:
            List of matching items

        Raises:
            MemoryError: If search operation fails
            ValueError: If memory type is unknown
        """
        correlation_id = get_correlation_id()

        try:
            backend = self._get_memory_backend(memory_type)

            self.logger.debug(
                "Searching memory",
                memory_type=memory_type,
                query=query,
                workspace_id=str(workspace_id),
                top_k=top_k,
                correlation_id=correlation_id
            )

            results = await backend.search(
                query=query,
                workspace_id=workspace_id,
                top_k=top_k,
                filters=filters
            )

            self.logger.debug(
                "Memory search completed",
                memory_type=memory_type,
                query=query,
                results_count=len(results),
                correlation_id=correlation_id
            )

            return results

        except Exception as e:
            self.logger.error(
                "Failed to search memory",
                memory_type=memory_type,
                query=query,
                error=str(e),
                correlation_id=correlation_id
            )
            raise

    async def forget(
        self,
        memory_type: str,
        key: str,
        workspace_id: UUID
    ) -> bool:
        """
        Remove information from the specified memory type.

        Args:
            memory_type: Type of memory
            key: Memory item identifier to delete
            workspace_id: Workspace UUID

        Returns:
            True if deletion was successful

        Raises:
            MemoryError: If deletion operation fails
            ValueError: If memory type is unknown
        """
        correlation_id = get_correlation_id()

        try:
            backend = self._get_memory_backend(memory_type)

            self.logger.debug(
                "Forgetting memory",
                memory_type=memory_type,
                key=key,
                workspace_id=str(workspace_id),
                correlation_id=correlation_id
            )

            success = await backend.forget(
                key=key,
                workspace_id=workspace_id
            )

            self.logger.debug(
                "Memory forgotten",
                memory_type=memory_type,
                key=key,
                success=success,
                correlation_id=correlation_id
            )

            return success

        except Exception as e:
            self.logger.error(
                "Failed to forget memory",
                memory_type=memory_type,
                key=key,
                error=str(e),
                correlation_id=correlation_id
            )
            raise

    async def learn_from_feedback(
        self,
        agent_name: str,
        feedback: Dict[str, Any],
        workspace_id: UUID
    ) -> None:
        """
        Update agent memory based on task feedback.

        This is the primary mechanism for agents to learn from their
        performance and improve over time.

        Args:
            agent_name: Name of the agent
            feedback: Feedback dictionary (success, rating, metrics, etc.)
            workspace_id: Workspace UUID

        Raises:
            MemoryError: If learning operation fails
        """
        correlation_id = get_correlation_id()

        try:
            if self.agent_memory is None:
                self.logger.warning(
                    "Agent memory not available, cannot learn from feedback",
                    agent_name=agent_name,
                    correlation_id=correlation_id
                )
                return

            self.logger.info(
                "Agent learning from feedback",
                agent_name=agent_name,
                workspace_id=str(workspace_id),
                success=feedback.get("success", False),
                correlation_id=correlation_id
            )

            await self.agent_memory.learn_from_feedback(
                key=agent_name,
                feedback=feedback,
                workspace_id=workspace_id
            )

            self.logger.info(
                "Agent learned from feedback successfully",
                agent_name=agent_name,
                correlation_id=correlation_id
            )

        except Exception as e:
            self.logger.error(
                "Failed to learn from feedback",
                agent_name=agent_name,
                error=str(e),
                correlation_id=correlation_id
            )
            raise

    async def get_context(
        self,
        workspace_id: UUID,
        task_type: str,
        session_id: Optional[str] = None,
        include_semantic: bool = True
    ) -> Dict[str, Any]:
        """
        Get comprehensive context for a task.

        Aggregates relevant information from all memory types to provide
        complete context for agent execution.

        Args:
            workspace_id: Workspace UUID
            task_type: Type of task (campaign_planning, content_creation, etc.)
            session_id: Optional session ID for conversation history
            include_semantic: Whether to include semantic search results

        Returns:
            Dictionary containing:
            - conversation_history: Recent messages (if session_id provided)
            - agent_patterns: Relevant agent performance data
            - workspace_context: Brand voice, ICPs, preferences
            - relevant_content: Semantically similar past content

        Raises:
            MemoryError: If context retrieval fails
        """
        correlation_id = get_correlation_id()

        try:
            self.logger.info(
                "Getting context for task",
                workspace_id=str(workspace_id),
                task_type=task_type,
                correlation_id=correlation_id
            )

            context = {
                "workspace_id": str(workspace_id),
                "task_type": task_type,
                "correlation_id": correlation_id
            }

            # Get conversation history if session provided
            if session_id and self.conversation_memory:
                try:
                    context["conversation_history"] = await self.conversation_memory.recall(
                        key=session_id,
                        workspace_id=workspace_id,
                        default=[]
                    )
                except Exception as e:
                    self.logger.warning(
                        "Failed to get conversation history",
                        error=str(e),
                        correlation_id=correlation_id
                    )
                    context["conversation_history"] = []

            # Get agent patterns for task type
            if self.agent_memory:
                try:
                    # Try to get agent specific to task type
                    agent_name = self._get_agent_for_task(task_type)
                    context["agent_patterns"] = await self.agent_memory.recall(
                        key=agent_name,
                        workspace_id=workspace_id,
                        default={}
                    )
                except Exception as e:
                    self.logger.warning(
                        "Failed to get agent patterns",
                        error=str(e),
                        correlation_id=correlation_id
                    )
                    context["agent_patterns"] = {}

            # Get workspace context
            if self.workspace_memory:
                try:
                    # Get brand voice
                    brand_voice = await self.workspace_memory.recall(
                        key="brand_voice",
                        workspace_id=workspace_id
                    )

                    # Get all ICPs
                    icps = await self.workspace_memory.search(
                        query="",
                        workspace_id=workspace_id,
                        filters={"memory_type": "icp"},
                        top_k=10
                    )

                    # Get preferences
                    preferences = await self.workspace_memory.recall(
                        key="preferences",
                        workspace_id=workspace_id,
                        default={}
                    )

                    context["workspace_context"] = {
                        "brand_voice": brand_voice,
                        "icps": icps,
                        "preferences": preferences
                    }

                except Exception as e:
                    self.logger.warning(
                        "Failed to get workspace context",
                        error=str(e),
                        correlation_id=correlation_id
                    )
                    context["workspace_context"] = {}

            # Get relevant content via semantic search
            if include_semantic and self.semantic_memory:
                try:
                    semantic_results = await self.semantic_memory.search(
                        query=task_type,
                        workspace_id=workspace_id,
                        top_k=5
                    )
                    context["relevant_content"] = semantic_results
                except Exception as e:
                    self.logger.warning(
                        "Failed to get semantic context",
                        error=str(e),
                        correlation_id=correlation_id
                    )
                    context["relevant_content"] = []

            self.logger.info(
                "Context retrieved successfully",
                workspace_id=str(workspace_id),
                task_type=task_type,
                has_conversation=bool(context.get("conversation_history")),
                has_agent_patterns=bool(context.get("agent_patterns")),
                has_workspace=bool(context.get("workspace_context")),
                semantic_results=len(context.get("relevant_content", [])),
                correlation_id=correlation_id
            )

            return context

        except Exception as e:
            self.logger.error(
                "Failed to get context",
                workspace_id=str(workspace_id),
                task_type=task_type,
                error=str(e),
                correlation_id=correlation_id
            )
            raise MemoryError(
                f"Failed to get context: {str(e)}",
                memory_type="all",
                operation="get_context"
            )

    def _get_agent_for_task(self, task_type: str) -> str:
        """
        Map task type to agent name.

        Args:
            task_type: Type of task

        Returns:
            Agent name string
        """
        task_agent_map = {
            "campaign_planning": "campaign_planner",
            "content_creation": "social_copy",
            "research": "icp_builder",
            "strategy": "synthesis_agent",
            "execution": "scheduler_agent",
        }

        return task_agent_map.get(task_type, task_type)

    async def clear_workspace(
        self,
        workspace_id: UUID,
        memory_types: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """
        Clear memory for a workspace.

        Args:
            workspace_id: Workspace UUID
            memory_types: Optional list of memory types to clear (default: all)

        Returns:
            Dictionary mapping memory type to success status
        """
        correlation_id = get_correlation_id()

        if memory_types is None:
            memory_types = ["conversation", "agent", "workspace", "semantic"]

        results = {}

        for memory_type in memory_types:
            try:
                backend = self._get_memory_backend(memory_type)
                success = await backend.clear(workspace_id)
                results[memory_type] = success

                self.logger.info(
                    "Cleared memory type",
                    memory_type=memory_type,
                    workspace_id=str(workspace_id),
                    success=success,
                    correlation_id=correlation_id
                )

            except Exception as e:
                self.logger.error(
                    "Failed to clear memory type",
                    memory_type=memory_type,
                    workspace_id=str(workspace_id),
                    error=str(e),
                    correlation_id=correlation_id
                )
                results[memory_type] = False

        return results

    async def close(self):
        """Close all memory connections and cleanup resources."""
        self.logger.info("Closing memory manager")

        # Close conversation memory
        if self.conversation_memory:
            try:
                await self.conversation_memory.close()
            except Exception as e:
                self.logger.warning("Error closing conversation memory", error=str(e))

        # Close agent memory
        if self.agent_memory:
            try:
                await self.agent_memory.close()
            except Exception as e:
                self.logger.warning("Error closing agent memory", error=str(e))

        self.logger.info("Memory manager closed")


# Global singleton instance
_memory_manager: Optional[MemoryManager] = None


def get_memory_manager() -> MemoryManager:
    """
    Get or create global memory manager instance.

    Returns:
        MemoryManager singleton instance
    """
    global _memory_manager

    if _memory_manager is None:
        _memory_manager = MemoryManager()

    return _memory_manager
