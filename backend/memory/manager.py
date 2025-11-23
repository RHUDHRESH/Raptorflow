"""
MemoryManager - Core memory management interface for RaptorFlow agents.

This module provides the primary interface for agents to interact with memory:
- Search for relevant past experiences
- Store execution results and performance metrics
- Track user preferences and feedback
- Analyze performance patterns for improvement suggestions

The MemoryManager supports both semantic search (via embeddings) and structured
queries (via metadata filters) to enable flexible memory retrieval.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from backend.utils.correlation import get_correlation_id


logger = logging.getLogger(__name__)


class MemoryEntry:
    """
    Represents a single memory entry stored by an agent.

    Attributes:
        memory_id: Unique identifier for this memory
        agent_name: Name of the agent that created this memory
        task_type: Type of task executed (e.g., "icp_building", "content_generation")
        input_summary: Brief summary of task input
        output_summary: Brief summary of task output
        result: Full task result (can be large)
        metadata: Additional structured metadata (tags, user_id, workspace_id, etc.)
        performance_metrics: Execution metrics (latency, tokens, quality scores)
        user_feedback: Optional user feedback (rating, comments, corrections)
        timestamp: When this memory was created
        correlation_id: Request correlation ID for tracing
    """

    def __init__(
        self,
        agent_name: str,
        task_type: str,
        input_summary: str,
        output_summary: str,
        result: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        performance_metrics: Optional[Dict[str, Any]] = None,
        user_feedback: Optional[Dict[str, Any]] = None,
        memory_id: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        correlation_id: Optional[str] = None,
    ):
        self.memory_id = memory_id or str(uuid4())
        self.agent_name = agent_name
        self.task_type = task_type
        self.input_summary = input_summary
        self.output_summary = output_summary
        self.result = result
        self.metadata = metadata or {}
        self.performance_metrics = performance_metrics or {}
        self.user_feedback = user_feedback
        self.timestamp = timestamp or datetime.now(timezone.utc)
        self.correlation_id = correlation_id or get_correlation_id()

    def to_dict(self) -> Dict[str, Any]:
        """Convert memory entry to dictionary."""
        return {
            "memory_id": self.memory_id,
            "agent_name": self.agent_name,
            "task_type": self.task_type,
            "input_summary": self.input_summary,
            "output_summary": self.output_summary,
            "result": self.result,
            "metadata": self.metadata,
            "performance_metrics": self.performance_metrics,
            "user_feedback": self.user_feedback,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MemoryEntry:
        """Create MemoryEntry from dictionary."""
        timestamp_str = data.get("timestamp")
        timestamp = datetime.fromisoformat(timestamp_str) if timestamp_str else None

        return cls(
            memory_id=data.get("memory_id"),
            agent_name=data["agent_name"],
            task_type=data["task_type"],
            input_summary=data["input_summary"],
            output_summary=data["output_summary"],
            result=data["result"],
            metadata=data.get("metadata"),
            performance_metrics=data.get("performance_metrics"),
            user_feedback=data.get("user_feedback"),
            timestamp=timestamp,
            correlation_id=data.get("correlation_id"),
        )


class MemoryManager:
    """
    Core memory management interface for RaptorFlow agents.

    The MemoryManager provides agents with capabilities to:
    1. Search for relevant memories from past executions
    2. Store new memories with results and performance metrics
    3. Update memories with user feedback
    4. Analyze performance patterns for improvement suggestions

    Memory is organized by:
    - Agent name (which agent created it)
    - Task type (what kind of task was performed)
    - Workspace/user context (whose data)
    - Temporal ordering (when it happened)

    Usage:
        memory = MemoryManager(workspace_id="ws123", user_id="u456")

        # Search for relevant memories
        memories = await memory.search(
            query="Build ICP for SaaS company",
            agent_name="ICPBuilderAgent",
            limit=5
        )

        # Store a new memory
        await memory.remember(
            agent_name="ICPBuilderAgent",
            task_type="icp_building",
            input_summary="Build ICP for TechCorp",
            output_summary="Created B2B SaaS executive persona",
            result={"icp_name": "...", ...},
            performance_metrics={"latency_ms": 1200, "tokens_used": 500}
        )
    """

    def __init__(
        self,
        workspace_id: str,
        user_id: Optional[str] = None,
        storage_backend: Optional[str] = "in_memory"
    ):
        """
        Initialize MemoryManager.

        Args:
            workspace_id: Workspace ID to scope memory to
            user_id: Optional user ID for user-specific memory
            storage_backend: Storage backend to use ("in_memory", "redis", "postgres")
        """
        self.workspace_id = workspace_id
        self.user_id = user_id
        self.storage_backend = storage_backend
        self.logger = logging.getLogger(f"MemoryManager[{workspace_id}]")

        # In-memory storage for MVP (will be replaced with persistent storage)
        self._memory_store: List[MemoryEntry] = []

        self.logger.info(
            f"MemoryManager initialized",
            extra={
                "workspace_id": workspace_id,
                "user_id": user_id,
                "storage_backend": storage_backend
            }
        )

    async def search(
        self,
        query: str,
        agent_name: Optional[str] = None,
        task_type: Optional[str] = None,
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[MemoryEntry]:
        """
        Search for relevant memories using semantic search.

        This method finds memories that are contextually relevant to the current task,
        enabling agents to learn from past experiences and user preferences.

        Args:
            query: Natural language query describing what to search for
            agent_name: Optional filter by specific agent
            task_type: Optional filter by task type
            limit: Maximum number of memories to return
            filters: Additional metadata filters (e.g., {"persona_type": "executive"})

        Returns:
            List of relevant MemoryEntry objects, ordered by relevance

        Example:
            memories = await memory.search(
                query="successful ICP for SaaS startups",
                agent_name="ICPBuilderAgent",
                limit=3
            )
        """
        self.logger.debug(
            f"Searching memories: query='{query}', agent={agent_name}, task_type={task_type}",
            extra={"limit": limit, "filters": filters}
        )

        # Apply filters
        filtered_memories = self._memory_store.copy()

        if agent_name:
            filtered_memories = [m for m in filtered_memories if m.agent_name == agent_name]

        if task_type:
            filtered_memories = [m for m in filtered_memories if m.task_type == task_type]

        if filters:
            for key, value in filters.items():
                filtered_memories = [
                    m for m in filtered_memories
                    if m.metadata.get(key) == value
                ]

        # TODO: Implement semantic search using embeddings
        # For MVP, return most recent memories
        filtered_memories.sort(key=lambda m: m.timestamp, reverse=True)
        results = filtered_memories[:limit]

        self.logger.info(f"Found {len(results)} relevant memories")
        return results

    async def remember(
        self,
        agent_name: str,
        task_type: str,
        input_summary: str,
        output_summary: str,
        result: Dict[str, Any],
        performance_metrics: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Store a new memory entry.

        This method persists execution results, performance metrics, and context
        for future retrieval by this or other agents.

        Args:
            agent_name: Name of the agent creating this memory
            task_type: Type of task executed
            input_summary: Brief summary of input (for search/display)
            output_summary: Brief summary of output (for search/display)
            result: Full task result dictionary
            performance_metrics: Optional metrics (latency, tokens, quality scores)
            metadata: Optional additional context (user_id, tags, etc.)

        Returns:
            memory_id: Unique ID of the created memory

        Example:
            memory_id = await memory.remember(
                agent_name="ICPBuilderAgent",
                task_type="icp_building",
                input_summary="Build ICP for TechCorp SaaS platform",
                output_summary="Created 'Scaling SaaS Founders' persona",
                result=icp_data,
                performance_metrics={"latency_ms": 1200, "tokens": 500, "confidence": 0.85},
                metadata={"industry": "SaaS", "persona_type": "executive"}
            )
        """
        # Merge workspace/user context into metadata
        full_metadata = {
            "workspace_id": self.workspace_id,
            "user_id": self.user_id,
            **(metadata or {})
        }

        # Create memory entry
        memory_entry = MemoryEntry(
            agent_name=agent_name,
            task_type=task_type,
            input_summary=input_summary,
            output_summary=output_summary,
            result=result,
            metadata=full_metadata,
            performance_metrics=performance_metrics,
        )

        # Store in memory (will be persisted to DB in production)
        self._memory_store.append(memory_entry)

        self.logger.info(
            f"Stored memory: {memory_entry.memory_id}",
            extra={
                "agent_name": agent_name,
                "task_type": task_type,
                "memory_id": memory_entry.memory_id
            }
        )

        return memory_entry.memory_id

    async def add_feedback(
        self,
        memory_id: str,
        feedback: Dict[str, Any]
    ) -> bool:
        """
        Add user feedback to an existing memory.

        Feedback helps agents learn from user preferences and improve over time.

        Args:
            memory_id: ID of memory to update
            feedback: Feedback dictionary containing:
                - rating: Optional[int] (1-5 stars)
                - comments: Optional[str] (user comments)
                - corrections: Optional[Dict] (corrected fields)
                - helpful: Optional[bool] (was this result helpful?)

        Returns:
            True if feedback was added, False if memory not found

        Example:
            await memory.add_feedback(
                memory_id="mem_123",
                feedback={
                    "rating": 4,
                    "comments": "Good persona but needs more pain points",
                    "corrections": {"pain_points": ["...", "...", "..."]},
                    "helpful": True
                }
            )
        """
        for memory_entry in self._memory_store:
            if memory_entry.memory_id == memory_id:
                memory_entry.user_feedback = feedback
                self.logger.info(
                    f"Added feedback to memory: {memory_id}",
                    extra={"feedback": feedback}
                )
                return True

        self.logger.warning(f"Memory not found: {memory_id}")
        return False

    async def get_performance_history(
        self,
        agent_name: str,
        task_type: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get historical performance metrics for an agent.

        This enables agents to analyze their performance trends over time
        and identify patterns for improvement.

        Args:
            agent_name: Agent to get history for
            task_type: Optional filter by task type
            limit: Maximum number of entries to return

        Returns:
            List of performance metric dictionaries with timestamps

        Example:
            history = await memory.get_performance_history(
                agent_name="ICPBuilderAgent",
                task_type="icp_building",
                limit=10
            )
            # Analyze trends in latency, quality scores, user ratings, etc.
        """
        filtered_memories = [
            m for m in self._memory_store
            if m.agent_name == agent_name
        ]

        if task_type:
            filtered_memories = [
                m for m in filtered_memories
                if m.task_type == task_type
            ]

        # Sort by timestamp descending
        filtered_memories.sort(key=lambda m: m.timestamp, reverse=True)
        filtered_memories = filtered_memories[:limit]

        # Extract performance metrics
        performance_history = []
        for memory in filtered_memories:
            entry = {
                "timestamp": memory.timestamp.isoformat(),
                "task_type": memory.task_type,
                "metrics": memory.performance_metrics,
                "user_feedback": memory.user_feedback,
                "correlation_id": memory.correlation_id,
            }
            performance_history.append(entry)

        return performance_history

    async def get_user_preferences(
        self,
        preference_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract user preferences from historical feedback.

        Analyzes past feedback and corrections to identify user preferences
        that can inform future task execution.

        Args:
            preference_type: Optional filter (e.g., "tone", "length", "format")

        Returns:
            Dictionary of inferred preferences

        Example:
            prefs = await memory.get_user_preferences()
            # Returns: {
            #   "preferred_tone": "professional",
            #   "preferred_length": "concise",
            #   "common_corrections": {...}
            # }
        """
        preferences = {
            "total_feedback_count": 0,
            "average_rating": 0.0,
            "common_corrections": {},
            "preferences": {}
        }

        # Analyze all memories with feedback
        memories_with_feedback = [
            m for m in self._memory_store
            if m.user_feedback is not None
        ]

        if not memories_with_feedback:
            return preferences

        # Calculate average rating
        ratings = [
            m.user_feedback.get("rating", 0)
            for m in memories_with_feedback
            if m.user_feedback.get("rating")
        ]

        if ratings:
            preferences["average_rating"] = sum(ratings) / len(ratings)

        preferences["total_feedback_count"] = len(memories_with_feedback)

        # TODO: Implement more sophisticated preference extraction
        # - Analyze correction patterns
        # - Identify common themes in comments
        # - Extract stylistic preferences

        return preferences

    def clear_workspace_memory(self) -> int:
        """
        Clear all memories for the current workspace.

        USE WITH CAUTION: This permanently deletes all stored memories.

        Returns:
            Number of memories deleted
        """
        initial_count = len(self._memory_store)
        self._memory_store = []

        self.logger.warning(
            f"Cleared {initial_count} memories for workspace {self.workspace_id}"
        )

        return initial_count
