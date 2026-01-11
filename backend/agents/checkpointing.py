"""
Redis-based checkpointing for LangGraph workflow state persistence.
"""

import json
import pickle
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from langchain_core.checkpoint import BaseCheckpointSaver
from langchain_core.checkpoint.base import Checkpoint, CheckpointTuple
from langchain_core.runnables import RunnableConfig

from ..config import get_config


class RedisCheckpointer(BaseCheckpointSaver):
    """
    Redis-based checkpoint saver for LangGraph workflows.

    Provides persistent storage of workflow state with TTL management
    and workspace-based isolation.
    """

    def __init__(self, redis_client=None, ttl_hours: int = 24):
        """
        Initialize Redis checkpointer.

        Args:
            redis_client: Redis client instance (if None, creates from config)
            ttl_hours: Time-to-live for checkpoints in hours
        """
        self.ttl_seconds = ttl_hours * 3600

        if redis_client:
            self.redis = redis_client
        else:
            # Create Redis client from config
            config = get_config()
            import redis

            self.redis = redis.from_url(
                config.UPSTASH_REDIS_URL,
                password=config.UPSTASH_REDIS_TOKEN,
                decode_responses=False,  # Keep binary for pickle
            )

    def _make_key(self, thread_id: str, checkpoint_ns: str = "") -> str:
        """Generate Redis key for checkpoint."""
        if checkpoint_ns:
            return f"checkpoint:{checkpoint_ns}:{thread_id}"
        return f"checkpoint:{thread_id}"

    def _serialize_checkpoint(self, checkpoint: Checkpoint) -> bytes:
        """Serialize checkpoint to bytes."""
        return pickle.dumps(checkpoint)

    def _deserialize_checkpoint(self, data: bytes) -> Checkpoint:
        """Deserialize checkpoint from bytes."""
        return pickle.loads(data)

    async def save_checkpoint(
        self,
        checkpoint: Checkpoint,
        config: RunnableConfig,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Save checkpoint to Redis.

        Args:
            checkpoint: Checkpoint to save
            config: Runnable configuration
            metadata: Optional metadata to store
        """
        try:
            thread_id = config.get("configurable", {}).get("thread_id")
            checkpoint_ns = config.get("configurable", {}).get("checkpoint_ns", "")

            if not thread_id:
                raise ValueError("thread_id must be provided in config")

            key = self._make_key(thread_id, checkpoint_ns)

            # Prepare checkpoint data
            checkpoint_data = {
                "checkpoint": self._serialize_checkpoint(checkpoint),
                "config": json.dumps(config),
                "metadata": json.dumps(metadata or {}),
                "created_at": datetime.utcnow().isoformat(),
                "thread_id": thread_id,
                "checkpoint_ns": checkpoint_ns,
            }

            # Save to Redis with TTL
            await self.redis.hset(key, mapping=checkpoint_data)
            await self.redis.expire(key, self.ttl_seconds)

        except Exception as e:
            raise RuntimeError(f"Failed to save checkpoint: {str(e)}")

    async def get_checkpoint(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        """
        Get checkpoint from Redis.

        Args:
            config: Runnable configuration

        Returns:
            CheckpointTuple if found, None otherwise
        """
        try:
            thread_id = config.get("configurable", {}).get("thread_id")
            checkpoint_ns = config.get("configurable", {}).get("checkpoint_ns", "")

            if not thread_id:
                return None

            key = self._make_key(thread_id, checkpoint_ns)

            # Get checkpoint data
            data = await self.redis.hgetall(key)

            if not data:
                return None

            # Deserialize checkpoint
            checkpoint = self._deserialize_checkpoint(data.get("checkpoint"))
            saved_config = json.loads(data.get("config"))
            metadata = json.loads(data.get("metadata"))

            return CheckpointTuple(
                config=saved_config, checkpoint=checkpoint, metadata=metadata
            )

        except Exception as e:
            raise RuntimeError(f"Failed to get checkpoint: {str(e)}")

    async def list_checkpoints(
        self,
        config: Optional[RunnableConfig] = None,
        limit: int = 10,
        before: Optional[datetime] = None,
    ) -> List[CheckpointTuple]:
        """
        List checkpoints with optional filtering.

        Args:
            config: Optional configuration for filtering
            limit: Maximum number of checkpoints to return
            before: Only return checkpoints before this time

        Returns:
            List of CheckpointTuple objects
        """
        try:
            # Build pattern for key search
            pattern = "checkpoint:*"
            if config:
                checkpoint_ns = config.get("configurable", {}).get("checkpoint_ns", "")
                thread_id = config.get("configurable", {}).get("thread_id")
                if thread_id:
                    pattern = self._make_key(thread_id, checkpoint_ns)

            # Search for keys
            keys = []
            async for key in self.redis.scan_iter(match=pattern):
                keys.append(key)

            # Limit results
            if limit:
                keys = keys[:limit]

            # Get checkpoint data
            checkpoints = []
            for key in keys:
                try:
                    data = await self.redis.hgetall(key)
                    if not data:
                        continue

                    # Check time filter
                    if before:
                        created_at = datetime.fromisoformat(data.get("created_at"))
                        if created_at >= before:
                            continue

                    # Deserialize
                    checkpoint = self._deserialize_checkpoint(data.get("checkpoint"))
                    saved_config = json.loads(data.get("config"))
                    metadata = json.loads(data.get("metadata"))

                    checkpoints.append(
                        CheckpointTuple(
                            config=saved_config,
                            checkpoint=checkpoint,
                            metadata=metadata,
                        )
                    )

                except Exception as e:
                    # Skip invalid checkpoints
                    continue

            # Sort by creation time (newest first)
            checkpoints.sort(
                key=lambda x: x.metadata.get("created_at", ""), reverse=True
            )

            return checkpoints

        except Exception as e:
            raise RuntimeError(f"Failed to list checkpoints: {str(e)}")

    async def delete_checkpoint(self, config: RunnableConfig) -> bool:
        """
        Delete checkpoint from Redis.

        Args:
            config: Runnable configuration

        Returns:
            True if deleted, False if not found
        """
        try:
            thread_id = config.get("configurable", {}).get("thread_id")
            checkpoint_ns = config.get("configurable", {}).get("checkpoint_ns", "")

            if not thread_id:
                return False

            key = self._make_key(thread_id, checkpoint_ns)

            # Delete key
            result = await self.redis.delete(key)

            return result > 0

        except Exception as e:
            raise RuntimeError(f"Failed to delete checkpoint: {str(e)}")

    async def clear_workspace_checkpoints(self, workspace_id: str) -> int:
        """
        Clear all checkpoints for a workspace.

        Args:
            workspace_id: Workspace ID to clear

        Returns:
            Number of checkpoints deleted
        """
        try:
            # Find all keys for workspace
            pattern = f"checkpoint:*{workspace_id}*"
            keys = []
            async for key in self.redis.scan_iter(match=pattern):
                keys.append(key)

            # Delete all keys
            if keys:
                await self.redis.delete(*keys)

            return len(keys)

        except Exception as e:
            raise RuntimeError(f"Failed to clear workspace checkpoints: {str(e)}")

    async def get_checkpoint_count(
        self, workspace_id: Optional[str] = None
    ) -> Dict[str, int]:
        """
        Get checkpoint counts by type.

        Args:
            workspace_id: Optional workspace ID to filter by

        Returns:
            Dictionary with checkpoint counts
        """
        try:
            pattern = "checkpoint:*"
            if workspace_id:
                pattern = f"checkpoint:*{workspace_id}*"

            # Count by checkpoint namespace
            counts = {}
            total = 0

            async for key in self.redis.scan_iter(match=pattern):
                try:
                    data = await self.redis.hgetall(key)
                    if data:
                        checkpoint_ns = json.loads(data.get("metadata", "{}")).get(
                            "checkpoint_ns", "default"
                        )
                        counts[checkpoint_ns] = counts.get(checkpoint_ns, 0) + 1
                        total += 1
                except Exception:
                    continue

            counts["total"] = total
            return counts

        except Exception as e:
            raise RuntimeError(f"Failed to get checkpoint count: {str(e)}")

    async def cleanup_expired_checkpoints(self) -> int:
        """
        Clean up expired checkpoints.

        Returns:
            Number of checkpoints cleaned up
        """
        try:
            # Redis automatically handles TTL expiration
            # This method can be used for manual cleanup if needed

            # Find expired keys (those without TTL or with expired TTL)
            cleaned = 0
            pattern = "checkpoint:*"

            async for key in self.redis.scan_iter(match=pattern):
                try:
                    ttl = await self.redis.ttl(key)
                    if ttl == -1:  # No TTL set
                        await self.redis.expire(key, self.ttl_seconds)
                        cleaned += 1
                    elif ttl == -2:  # Key doesn't exist
                        continue
                except Exception:
                    continue

            return cleaned

        except Exception as e:
            raise RuntimeError(f"Failed to cleanup checkpoints: {str(e)}")


class WorkspaceCheckpointer(RedisCheckpointer):
    """
    Workspace-specific checkpointer with enhanced isolation.
    """

    def __init__(self, workspace_id: str, redis_client=None, ttl_hours: int = 24):
        """
        Initialize workspace-specific checkpointer.

        Args:
            workspace_id: Workspace ID for isolation
            redis_client: Redis client instance
            ttl_hours: Time-to-live for checkpoints
        """
        super().__init__(redis_client, ttl_hours)
        self.workspace_id = workspace_id

    def _make_key(self, thread_id: str, checkpoint_ns: str = "") -> str:
        """Generate workspace-isolated Redis key."""
        base_key = super()._make_key(thread_id, checkpoint_ns)
        return f"workspace:{self.workspace_id}:{base_key}"

    async def save_checkpoint(
        self,
        checkpoint: Checkpoint,
        config: RunnableConfig,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Save checkpoint with workspace metadata."""
        # Add workspace ID to metadata
        if metadata is None:
            metadata = {}
        metadata["workspace_id"] = self.workspace_id

        await super().save_checkpoint(checkpoint, config, metadata)


# Factory functions
def create_redis_checkpointer(
    workspace_id: Optional[str] = None, ttl_hours: int = 24
) -> BaseCheckpointSaver:
    """
    Create Redis checkpointer instance.

    Args:
        workspace_id: Optional workspace ID for isolation
        ttl_hours: Time-to-live for checkpoints

    Returns:
        Checkpointer instance
    """
    if workspace_id:
        return WorkspaceCheckpointer(workspace_id, ttl_hours=ttl_hours)
    else:
        return RedisCheckpointer(ttl_hours=ttl_hours)


def create_memory_checkpointer() -> BaseCheckpointSaver:
    """
    Create in-memory checkpointer for testing.

    Returns:
        Memory-based checkpointer
    """
    from langchain_core.checkpoint.memory import MemorySaver

    return MemorySaver()
