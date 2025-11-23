"""
Memory Manager for intelligent agent orchestration.

This service provides persistent memory storage for:
- Task history and execution patterns
- Agent performance metrics
- Successful agent sequences
- Failed attempts and critiques
- User preferences and workspace context

The MemoryManager uses Redis for fast retrieval and supports semantic search
for finding similar tasks and determining optimal agent routing.
"""

from __future__ import annotations

import json
import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

import structlog

from backend.utils.cache import redis_cache

logger = structlog.get_logger()


class MemoryEntry:
    """
    A single memory entry with metadata for searchability.

    Attributes:
        key: Unique identifier for this memory
        memory_type: Type of memory (task_history, agent_performance, critique, etc.)
        content: The actual memory content
        metadata: Additional searchable metadata
        confidence: Confidence score (0.0-1.0) for memory quality
        timestamp: When this memory was created
        workspace_id: Workspace this memory belongs to
    """

    def __init__(
        self,
        key: str,
        memory_type: str,
        content: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        confidence: float = 1.0,
        workspace_id: Optional[UUID] = None,
    ):
        self.key = key
        self.memory_type = memory_type
        self.content = content
        self.metadata = metadata or {}
        self.confidence = confidence
        self.timestamp = datetime.now(timezone.utc)
        self.workspace_id = str(workspace_id) if workspace_id else None

    def to_dict(self) -> Dict[str, Any]:
        """Convert memory entry to dictionary for storage."""
        return {
            "key": self.key,
            "memory_type": self.memory_type,
            "content": self.content,
            "metadata": self.metadata,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "workspace_id": self.workspace_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryEntry":
        """Reconstruct memory entry from stored dictionary."""
        entry = cls(
            key=data["key"],
            memory_type=data["memory_type"],
            content=data["content"],
            metadata=data.get("metadata", {}),
            confidence=data.get("confidence", 1.0),
            workspace_id=UUID(data["workspace_id"]) if data.get("workspace_id") else None,
        )
        if "timestamp" in data:
            entry.timestamp = datetime.fromisoformat(data["timestamp"])
        return entry


class MemoryManager:
    """
    Intelligent memory management system for agent orchestration.

    Provides methods for:
    - Storing and retrieving task execution history
    - Tracking agent performance metrics
    - Finding similar tasks via semantic search
    - Learning from failures and successes
    - Workspace-specific context management

    Usage:
        memory = MemoryManager()

        # Store successful agent sequence
        await memory.store_task_result(
            goal="Generate blog post",
            agent_sequence=["content_supervisor", "blog_writer"],
            success=True,
            workspace_id=workspace_id
        )

        # Retrieve best agent for a task
        best_agent = await memory.get_best_performing_agent(
            task_type="blog_writing",
            workspace_id=workspace_id
        )
    """

    def __init__(self):
        """Initialize memory manager with Redis backend."""
        self.cache = redis_cache
        self.logger = logger

    def _generate_key(self, prefix: str, identifier: str) -> str:
        """Generate a consistent cache key."""
        return f"memory:{prefix}:{identifier}"

    def _hash_query(self, query: str) -> str:
        """Generate a hash for query-based lookups."""
        return hashlib.md5(query.lower().strip().encode()).hexdigest()

    async def store(
        self,
        memory_type: str,
        key: str,
        content: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        confidence: float = 1.0,
        workspace_id: Optional[UUID] = None,
        ttl: int = 2592000,  # 30 days default
    ) -> bool:
        """
        Store a memory entry.

        Args:
            memory_type: Type of memory (task_history, agent_performance, etc.)
            key: Unique identifier for this memory
            content: The memory content
            metadata: Additional searchable metadata
            confidence: Confidence score (0.0-1.0)
            workspace_id: Workspace this memory belongs to
            ttl: Time to live in seconds (default: 30 days)

        Returns:
            True if stored successfully, False otherwise
        """
        entry = MemoryEntry(
            key=key,
            memory_type=memory_type,
            content=content,
            metadata=metadata,
            confidence=confidence,
            workspace_id=workspace_id,
        )

        cache_key = self._generate_key(memory_type, key)

        try:
            serialized = json.dumps(entry.to_dict())
            await self.cache.set(cache_key, serialized, ttl=ttl)

            # Also store in a workspace-specific index if workspace_id is provided
            if workspace_id:
                index_key = self._generate_key(f"workspace_index:{workspace_id}", memory_type)
                await self._add_to_index(index_key, key, ttl=ttl)

            self.logger.debug(
                "Memory stored",
                memory_type=memory_type,
                key=key,
                workspace_id=str(workspace_id) if workspace_id else None,
            )
            return True

        except Exception as e:
            self.logger.error(
                "Failed to store memory",
                error=str(e),
                memory_type=memory_type,
                key=key,
            )
            return False

    async def _add_to_index(self, index_key: str, item: str, ttl: int) -> None:
        """Add an item to a set-based index."""
        try:
            # For now, we'll store as a JSON array since we're using RedisCache wrapper
            # In production, you'd use native Redis SADD
            current = await self.cache.get(index_key)
            if current:
                items = json.loads(current) if isinstance(current, str) else current
                if isinstance(items, list) and item not in items:
                    items.append(item)
                else:
                    items = [item]
            else:
                items = [item]

            await self.cache.set(index_key, json.dumps(items), ttl=ttl)
        except Exception as e:
            self.logger.warning("Failed to update index", error=str(e), index_key=index_key)

    async def retrieve(
        self,
        memory_type: str,
        key: str,
    ) -> Optional[MemoryEntry]:
        """
        Retrieve a specific memory entry.

        Args:
            memory_type: Type of memory to retrieve
            key: Unique identifier for the memory

        Returns:
            MemoryEntry if found, None otherwise
        """
        cache_key = self._generate_key(memory_type, key)

        try:
            data = await self.cache.get(cache_key)
            if data:
                # Handle if data is already a dict or a JSON string
                if isinstance(data, str):
                    data = json.loads(data)
                return MemoryEntry.from_dict(data)
            return None

        except Exception as e:
            self.logger.error(
                "Failed to retrieve memory",
                error=str(e),
                memory_type=memory_type,
                key=key,
            )
            return None

    async def search(
        self,
        query: str,
        memory_type: str,
        workspace_id: Optional[UUID] = None,
        limit: int = 10,
    ) -> List[MemoryEntry]:
        """
        Search for similar memories based on query.

        This is a simplified version using keyword matching. In production,
        you'd use vector embeddings for semantic search.

        Args:
            query: Search query
            memory_type: Type of memories to search
            workspace_id: Filter by workspace
            limit: Maximum number of results

        Returns:
            List of matching memory entries, sorted by relevance
        """
        try:
            results = []

            # Get all keys for this memory type and workspace
            if workspace_id:
                index_key = self._generate_key(f"workspace_index:{workspace_id}", memory_type)
                index_data = await self.cache.get(index_key)

                if index_data:
                    keys = json.loads(index_data) if isinstance(index_data, str) else index_data

                    for key in keys[:limit]:  # Limit iteration
                        entry = await self.retrieve(memory_type, key)
                        if entry:
                            # Simple keyword matching (would be embeddings in production)
                            if self._matches_query(query, entry):
                                results.append(entry)

            # Sort by confidence and timestamp
            results.sort(key=lambda x: (x.confidence, x.timestamp), reverse=True)
            return results[:limit]

        except Exception as e:
            self.logger.error("Memory search failed", error=str(e), query=query)
            return []

    def _matches_query(self, query: str, entry: MemoryEntry) -> bool:
        """
        Simple keyword-based matching.

        In production, replace with vector similarity using embeddings.
        """
        query_lower = query.lower()

        # Search in content
        content_str = json.dumps(entry.content).lower()
        if query_lower in content_str:
            return True

        # Search in metadata
        metadata_str = json.dumps(entry.metadata).lower()
        if query_lower in metadata_str:
            return True

        return False

    async def store_task_result(
        self,
        goal: str,
        agent_sequence: List[str],
        success: bool,
        workspace_id: UUID,
        execution_time: Optional[float] = None,
        error: Optional[str] = None,
        result_quality: Optional[float] = None,
    ) -> bool:
        """
        Store the result of a task execution for learning.

        Args:
            goal: The task goal/description
            agent_sequence: List of agents used in order
            success: Whether the task succeeded
            workspace_id: Workspace identifier
            execution_time: Time taken in seconds
            error: Error message if failed
            result_quality: Quality score (0.0-1.0)

        Returns:
            True if stored successfully
        """
        goal_hash = self._hash_query(goal)
        key = f"{workspace_id}:{goal_hash}"

        content = {
            "goal": goal,
            "agent_sequence": agent_sequence,
            "success": success,
            "execution_time": execution_time,
            "error": error,
            "result_quality": result_quality,
        }

        metadata = {
            "task_type": self._infer_task_type(goal),
            "agent_count": len(agent_sequence),
        }

        confidence = result_quality if result_quality else (0.9 if success else 0.3)

        return await self.store(
            memory_type="task_history",
            key=key,
            content=content,
            metadata=metadata,
            confidence=confidence,
            workspace_id=workspace_id,
        )

    def _infer_task_type(self, goal: str) -> str:
        """Infer task type from goal description."""
        goal_lower = goal.lower()

        if any(kw in goal_lower for kw in ["blog", "article", "post"]):
            return "content_generation"
        elif any(kw in goal_lower for kw in ["strategy", "campaign", "plan"]):
            return "strategy_planning"
        elif any(kw in goal_lower for kw in ["icp", "persona", "customer"]):
            return "research"
        elif any(kw in goal_lower for kw in ["publish", "schedule", "execute"]):
            return "execution"
        elif any(kw in goal_lower for kw in ["analytics", "metrics", "performance"]):
            return "analytics"
        else:
            return "general"

    async def get_best_performing_agent(
        self,
        task_type: str,
        workspace_id: Optional[UUID] = None,
    ) -> Optional[str]:
        """
        Get the best performing agent for a given task type.

        Args:
            task_type: Type of task (content_generation, strategy_planning, etc.)
            workspace_id: Optional workspace filter

        Returns:
            Name of best performing agent, or None if no history
        """
        try:
            # Search for successful tasks of this type
            search_query = task_type
            memories = await self.search(
                query=search_query,
                memory_type="task_history",
                workspace_id=workspace_id,
                limit=50,
            )

            # Filter for successful tasks matching this type
            relevant_memories = [
                m for m in memories
                if m.content.get("success") and m.metadata.get("task_type") == task_type
            ]

            if not relevant_memories:
                return None

            # Count agent performance
            agent_scores: Dict[str, List[float]] = {}

            for memory in relevant_memories:
                sequence = memory.content.get("agent_sequence", [])
                quality = memory.content.get("result_quality", memory.confidence)

                # Give primary credit to the last agent in the sequence
                if sequence:
                    primary_agent = sequence[-1]
                    if primary_agent not in agent_scores:
                        agent_scores[primary_agent] = []
                    agent_scores[primary_agent].append(quality)

            # Find agent with highest average quality
            if agent_scores:
                best_agent = max(
                    agent_scores.items(),
                    key=lambda x: sum(x[1]) / len(x[1])  # Average score
                )
                return best_agent[0]

            return None

        except Exception as e:
            self.logger.error(
                "Failed to get best performing agent",
                error=str(e),
                task_type=task_type,
            )
            return None

    async def store_critique(
        self,
        content_id: str,
        critique: str,
        issues: List[str],
        workspace_id: UUID,
    ) -> bool:
        """
        Store a content critique for learning.

        Args:
            content_id: Identifier for the content being critiqued
            critique: The critique text
            issues: List of specific issues found
            workspace_id: Workspace identifier

        Returns:
            True if stored successfully
        """
        key = f"{workspace_id}:{content_id}"

        content = {
            "content_id": content_id,
            "critique": critique,
            "issues": issues,
            "issue_count": len(issues),
        }

        return await self.store(
            memory_type="critique",
            key=key,
            content=content,
            workspace_id=workspace_id,
            ttl=604800,  # 7 days
        )


# Global memory manager instance
memory_manager = MemoryManager()
