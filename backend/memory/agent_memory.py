"""
Agent Memory - Agent-Specific Learning and Performance Tracking

This module implements agent memory for tracking agent-specific patterns,
successes, failures, and preferences using Redis hashes for fast access.

Purpose:
--------
- Track agent performance metrics and success patterns
- Store agent-specific preferences and learned behaviors
- Enable agents to learn from past successes and failures
- Support continuous improvement through feedback loops
- Maintain agent-specific context across sessions

Schema:
-------
Key Pattern: "agent:{workspace_id}:{agent_name}"
Value: Redis Hash with fields:
{
    "total_tasks": int,           # Total tasks completed
    "successful_tasks": int,      # Number of successful tasks
    "failed_tasks": int,          # Number of failed tasks
    "success_rate": float,        # Overall success rate
    "preferences": json,          # Agent-specific preferences
    "patterns": json,             # Learned patterns and strategies
    "last_updated": str,          # ISO 8601 timestamp
    "feedback_history": json,     # Recent feedback items
    "performance_metrics": json   # Custom performance metrics
}

Storage Backend: Redis Hashes
- Fast field-level access and updates
- Atomic increment operations for counters
- No expiration (persistent learning)
- Efficient memory usage for structured data

Dependencies:
-------------
- redis: For Redis client and hash operations
- json: For serializing complex fields
- datetime: For timestamp management
- statistics: For calculating metrics

Usage Example:
--------------
from memory.agent_memory import AgentMemory
from uuid import UUID

# Initialize agent memory
agent_memory = AgentMemory()

# Store agent performance
await agent_memory.learn_from_feedback(
    key="campaign_planner",
    feedback={
        "task": "campaign_creation",
        "success": True,
        "execution_time": 12.5,
        "user_rating": 5,
        "strategy": "persona_targeted"
    },
    workspace_id=UUID("...")
)

# Retrieve agent patterns
patterns = await agent_memory.recall(
    key="campaign_planner",
    workspace_id=UUID("...")
)

# Search for successful patterns
results = await agent_memory.search(
    query="high_success",
    workspace_id=UUID("..."),
    filters={"min_success_rate": 0.8}
)
"""

import json
from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime
from statistics import mean
import redis.asyncio as redis
from redis.asyncio import ConnectionPool
import structlog

from memory.base import BaseMemory, MemoryError
from config.settings import settings

logger = structlog.get_logger()


class AgentMemory(BaseMemory):
    """
    Redis-based agent memory for tracking agent performance and learning.

    This class maintains agent-specific knowledge including performance metrics,
    learned patterns, and preferences. It supports continuous learning through
    feedback accumulation and pattern recognition.

    Attributes:
        redis_client: Async Redis client instance
        max_feedback_history: Maximum feedback items to keep per agent
    """

    def __init__(self, max_feedback_history: int = 50):
        """
        Initialize agent memory with Redis connection.

        Args:
            max_feedback_history: Maximum feedback items to keep (default: 50)
        """
        super().__init__(memory_type="agent")
        self.max_feedback_history = max_feedback_history
        self.redis_client: Optional[redis.Redis] = None
        self._pool: Optional[ConnectionPool] = None

    async def _get_client(self) -> redis.Redis:
        """
        Get or create Redis client with connection pooling.

        Returns:
            Async Redis client instance

        Raises:
            MemoryError: If connection to Redis fails
        """
        if self.redis_client is None:
            try:
                self._pool = ConnectionPool.from_url(
                    settings.REDIS_URL,
                    max_connections=settings.REDIS_MAX_CONNECTIONS,
                    socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
                    decode_responses=True
                )
                self.redis_client = redis.Redis(connection_pool=self._pool)
                await self.redis_client.ping()
                self.logger.info("Connected to Redis for agent memory")
            except Exception as e:
                self.logger.error("Failed to connect to Redis", error=str(e))
                raise MemoryError(
                    f"Failed to connect to Redis: {str(e)}",
                    memory_type=self.memory_type,
                    operation="connect"
                )
        return self.redis_client

    def _make_key(self, agent_name: str, workspace_id: UUID) -> str:
        """
        Generate Redis key for agent memory.

        Args:
            agent_name: Name of the agent
            workspace_id: Workspace UUID

        Returns:
            Full Redis key: "agent:{workspace_id}:{agent_name}"
        """
        return f"agent:{workspace_id}:{agent_name}"

    async def remember(
        self,
        key: str,
        value: Any,
        workspace_id: UUID,
        metadata: Optional[Dict[str, Any]] = None,
        ttl: Optional[int] = None
    ) -> None:
        """
        Store or update agent-specific information.

        Args:
            key: Agent name
            value: Agent data (dict with preferences, patterns, etc.)
            workspace_id: Workspace UUID
            metadata: Optional metadata
            ttl: Not used for agent memory (persistent storage)

        Raises:
            MemoryError: If storage operation fails
        """
        self._validate_workspace_id(workspace_id)
        client = await self._get_client()
        redis_key = self._make_key(key, workspace_id)

        try:
            # Ensure value is a dict
            if not isinstance(value, dict):
                value = {"data": value}

            # Get existing data
            existing = await self._get_agent_data(redis_key, client)

            # Merge with existing data
            if existing:
                # Update specific fields
                for field, val in value.items():
                    if field in ["preferences", "patterns", "performance_metrics"]:
                        # Merge JSON fields
                        existing_json = json.loads(existing.get(field, "{}"))
                        if isinstance(val, dict):
                            existing_json.update(val)
                            value[field] = json.dumps(existing_json)
                        else:
                            value[field] = json.dumps(val)
                    else:
                        # Direct update for other fields
                        existing[field] = str(val) if not isinstance(val, str) else val

                # Combine updates
                for k, v in existing.items():
                    if k not in value:
                        value[k] = v

            # Add timestamp
            value["last_updated"] = datetime.utcnow().isoformat()

            # Serialize JSON fields
            for field in ["preferences", "patterns", "performance_metrics", "feedback_history"]:
                if field in value and not isinstance(value[field], str):
                    value[field] = json.dumps(value[field])

            # Store in Redis hash
            await client.hset(redis_key, mapping=value)

            self.logger.debug(
                "Stored agent memory",
                agent_name=key,
                workspace_id=str(workspace_id)
            )

        except Exception as e:
            self.logger.error(
                "Failed to store agent memory",
                agent_name=key,
                error=str(e)
            )
            raise MemoryError(
                f"Failed to store agent memory: {str(e)}",
                memory_type=self.memory_type,
                operation="remember"
            )

    async def recall(
        self,
        key: str,
        workspace_id: UUID,
        default: Any = None
    ) -> Dict[str, Any]:
        """
        Retrieve agent-specific memory.

        Args:
            key: Agent name
            workspace_id: Workspace UUID
            default: Default value if not found

        Returns:
            Dictionary containing agent memory data

        Raises:
            MemoryError: If retrieval operation fails
        """
        self._validate_workspace_id(workspace_id)
        client = await self._get_client()
        redis_key = self._make_key(key, workspace_id)

        try:
            data = await self._get_agent_data(redis_key, client)

            if not data:
                self.logger.debug(
                    "No agent memory found, returning default",
                    agent_name=key,
                    workspace_id=str(workspace_id)
                )
                return default if default is not None else {}

            # Parse JSON fields
            for field in ["preferences", "patterns", "performance_metrics", "feedback_history"]:
                if field in data and data[field]:
                    try:
                        data[field] = json.loads(data[field])
                    except json.JSONDecodeError:
                        data[field] = {}

            # Convert numeric fields
            for field in ["total_tasks", "successful_tasks", "failed_tasks"]:
                if field in data:
                    data[field] = int(data[field])

            if "success_rate" in data:
                data["success_rate"] = float(data["success_rate"])

            self.logger.debug(
                "Recalled agent memory",
                agent_name=key,
                workspace_id=str(workspace_id)
            )

            return data

        except Exception as e:
            self.logger.error(
                "Failed to recall agent memory",
                agent_name=key,
                error=str(e)
            )
            raise MemoryError(
                f"Failed to recall agent memory: {str(e)}",
                memory_type=self.memory_type,
                operation="recall"
            )

    async def search(
        self,
        query: str,
        workspace_id: UUID,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for agents based on criteria.

        Args:
            query: Search query (agent name pattern or "high_success", "low_success")
            workspace_id: Workspace UUID
            top_k: Maximum results to return
            filters: Optional filters (min_success_rate, task_type, etc.)

        Returns:
            List of matching agent memory records

        Raises:
            MemoryError: If search operation fails
        """
        self._validate_workspace_id(workspace_id)
        client = await self._get_client()

        try:
            # Get all agent keys for this workspace
            pattern = f"agent:{workspace_id}:*"
            keys = []
            async for key in client.scan_iter(match=pattern):
                keys.append(key)

            results = []

            for redis_key in keys:
                agent_name = redis_key.split(":")[-1]
                data = await self._get_agent_data(redis_key, client)

                if not data:
                    continue

                # Parse data
                agent_info = {
                    "agent_name": agent_name,
                    "total_tasks": int(data.get("total_tasks", 0)),
                    "successful_tasks": int(data.get("successful_tasks", 0)),
                    "failed_tasks": int(data.get("failed_tasks", 0)),
                    "success_rate": float(data.get("success_rate", 0.0)),
                    "last_updated": data.get("last_updated", ""),
                }

                # Apply filters
                if filters:
                    if "min_success_rate" in filters:
                        if agent_info["success_rate"] < filters["min_success_rate"]:
                            continue
                    if "max_success_rate" in filters:
                        if agent_info["success_rate"] > filters["max_success_rate"]:
                            continue
                    if "min_tasks" in filters:
                        if agent_info["total_tasks"] < filters["min_tasks"]:
                            continue

                # Check query match
                if query.lower() == "high_success" and agent_info["success_rate"] < 0.8:
                    continue
                elif query.lower() == "low_success" and agent_info["success_rate"] > 0.5:
                    continue
                elif query.lower() != "high_success" and query.lower() != "low_success":
                    if query.lower() not in agent_name.lower():
                        continue

                # Include full data
                for field in ["preferences", "patterns", "performance_metrics"]:
                    if field in data:
                        try:
                            agent_info[field] = json.loads(data[field])
                        except json.JSONDecodeError:
                            agent_info[field] = {}

                results.append(agent_info)

                if len(results) >= top_k:
                    break

            # Sort by success rate (descending)
            results.sort(key=lambda x: x["success_rate"], reverse=True)

            self.logger.debug(
                "Agent memory search completed",
                query=query,
                workspace_id=str(workspace_id),
                results_count=len(results)
            )

            return results[:top_k]

        except Exception as e:
            self.logger.error(
                "Failed to search agent memory",
                query=query,
                error=str(e)
            )
            raise MemoryError(
                f"Failed to search agent memory: {str(e)}",
                memory_type=self.memory_type,
                operation="search"
            )

    async def forget(
        self,
        key: str,
        workspace_id: UUID
    ) -> bool:
        """
        Delete agent memory.

        Args:
            key: Agent name to delete
            workspace_id: Workspace UUID

        Returns:
            True if deletion was successful

        Raises:
            MemoryError: If deletion fails
        """
        self._validate_workspace_id(workspace_id)
        client = await self._get_client()
        redis_key = self._make_key(key, workspace_id)

        try:
            deleted = await client.delete(redis_key)

            self.logger.debug(
                "Agent memory deleted",
                agent_name=key,
                workspace_id=str(workspace_id),
                deleted=bool(deleted)
            )

            return bool(deleted)

        except Exception as e:
            self.logger.error(
                "Failed to delete agent memory",
                agent_name=key,
                error=str(e)
            )
            raise MemoryError(
                f"Failed to delete agent memory: {str(e)}",
                memory_type=self.memory_type,
                operation="forget"
            )

    async def learn_from_feedback(
        self,
        key: str,
        feedback: Dict[str, Any],
        workspace_id: UUID
    ) -> None:
        """
        Update agent memory based on task feedback.

        This is the primary learning mechanism for agents. It updates
        performance metrics, stores successful patterns, and maintains
        feedback history.

        Args:
            key: Agent name
            feedback: Feedback dict with task, success, metrics, etc.
            workspace_id: Workspace UUID

        Raises:
            MemoryError: If update fails
        """
        self._validate_workspace_id(workspace_id)
        client = await self._get_client()
        redis_key = self._make_key(key, workspace_id)

        try:
            # Get existing data
            existing = await self._get_agent_data(redis_key, client)

            # Initialize counters if needed
            total_tasks = int(existing.get("total_tasks", 0)) if existing else 0
            successful_tasks = int(existing.get("successful_tasks", 0)) if existing else 0
            failed_tasks = int(existing.get("failed_tasks", 0)) if existing else 0

            # Update counters
            total_tasks += 1
            if feedback.get("success", False):
                successful_tasks += 1
            else:
                failed_tasks += 1

            # Calculate success rate
            success_rate = successful_tasks / total_tasks if total_tasks > 0 else 0.0

            # Get feedback history
            feedback_history = []
            if existing and "feedback_history" in existing:
                try:
                    feedback_history = json.loads(existing["feedback_history"])
                except json.JSONDecodeError:
                    feedback_history = []

            # Add new feedback with timestamp
            feedback_item = feedback.copy()
            feedback_item["timestamp"] = datetime.utcnow().isoformat()
            feedback_history.append(feedback_item)

            # Keep only recent feedback
            if len(feedback_history) > self.max_feedback_history:
                feedback_history = feedback_history[-self.max_feedback_history:]

            # Extract patterns from successful tasks
            patterns = {}
            if existing and "patterns" in existing:
                try:
                    patterns = json.loads(existing["patterns"])
                except json.JSONDecodeError:
                    patterns = {}

            if feedback.get("success", False) and "strategy" in feedback:
                strategy = feedback["strategy"]
                if strategy not in patterns:
                    patterns[strategy] = {"count": 0, "avg_rating": 0.0, "ratings": []}

                patterns[strategy]["count"] += 1
                if "user_rating" in feedback:
                    patterns[strategy]["ratings"].append(feedback["user_rating"])
                    patterns[strategy]["avg_rating"] = mean(patterns[strategy]["ratings"])

            # Update performance metrics
            performance_metrics = {}
            if existing and "performance_metrics" in existing:
                try:
                    performance_metrics = json.loads(existing["performance_metrics"])
                except json.JSONDecodeError:
                    performance_metrics = {}

            if "execution_time" in feedback:
                if "avg_execution_time" not in performance_metrics:
                    performance_metrics["avg_execution_time"] = 0.0
                    performance_metrics["execution_times"] = []

                performance_metrics["execution_times"].append(feedback["execution_time"])
                if len(performance_metrics["execution_times"]) > 100:
                    performance_metrics["execution_times"] = performance_metrics["execution_times"][-100:]
                performance_metrics["avg_execution_time"] = mean(performance_metrics["execution_times"])

            # Store updated data
            updated_data = {
                "total_tasks": str(total_tasks),
                "successful_tasks": str(successful_tasks),
                "failed_tasks": str(failed_tasks),
                "success_rate": str(success_rate),
                "feedback_history": json.dumps(feedback_history),
                "patterns": json.dumps(patterns),
                "performance_metrics": json.dumps(performance_metrics),
                "last_updated": datetime.utcnow().isoformat()
            }

            # Preserve preferences if they exist
            if existing and "preferences" in existing:
                updated_data["preferences"] = existing["preferences"]

            await client.hset(redis_key, mapping=updated_data)

            self.logger.info(
                "Agent learned from feedback",
                agent_name=key,
                workspace_id=str(workspace_id),
                success=feedback.get("success", False),
                new_success_rate=success_rate
            )

        except Exception as e:
            self.logger.error(
                "Failed to learn from feedback",
                agent_name=key,
                error=str(e)
            )
            raise MemoryError(
                f"Failed to learn from feedback: {str(e)}",
                memory_type=self.memory_type,
                operation="learn_from_feedback"
            )

    async def _get_agent_data(self, redis_key: str, client: redis.Redis) -> Optional[Dict[str, str]]:
        """
        Helper to get all fields from agent hash.

        Args:
            redis_key: Full Redis key
            client: Redis client instance

        Returns:
            Dictionary of agent data or None if not found
        """
        data = await client.hgetall(redis_key)
        return data if data else None

    async def clear(self, workspace_id: UUID) -> bool:
        """
        Clear all agent memory for a workspace.

        Args:
            workspace_id: Workspace UUID

        Returns:
            True if successful

        Raises:
            MemoryError: If clear operation fails
        """
        self._validate_workspace_id(workspace_id)
        client = await self._get_client()

        try:
            pattern = f"agent:{workspace_id}:*"
            keys = []
            async for key in client.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                await client.delete(*keys)

            self.logger.info(
                "Cleared all agent memory for workspace",
                workspace_id=str(workspace_id),
                cleared_count=len(keys)
            )

            return True

        except Exception as e:
            self.logger.error(
                "Failed to clear agent memory",
                workspace_id=str(workspace_id),
                error=str(e)
            )
            raise MemoryError(
                f"Failed to clear agent memory: {str(e)}",
                memory_type=self.memory_type,
                operation="clear"
            )

    async def close(self):
        """Close Redis connection and cleanup resources."""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
        if self._pool:
            await self._pool.disconnect()
            self._pool = None
        self.logger.info("Closed agent memory Redis connection")
