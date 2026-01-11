"""
Redis client with workspace isolation for Raptorflow memory system.
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

try:
    import redis.asyncio as redis
    from redis.asyncio import Redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    Redis = None

from ..agents.exceptions import DatabaseError, ValidationError, WorkspaceError

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis client with workspace isolation and multi-tenant support."""

    def __init__(self):
        """Initialize Redis client with workspace isolation."""
        if not REDIS_AVAILABLE:
            raise DatabaseError(
                "Redis client not available. Install with: pip install redis[hiredis]"
            )

        self.redis_client: Optional[Redis] = None
        self.workspace_id: Optional[str] = None
        self.key_prefix = "raptorflow"
        self.default_ttl = 3600  # 1 hour

        # Connection settings
        self.redis_url = os.getenv("UPSTASH_REDIS_URL")
        self.redis_token = os.getenv("UPSTASH_REDIS_TOKEN")

        if not self.redis_url or not self.redis_token:
            raise DatabaseError(
                "Redis configuration missing. Set UPSTASH_REDIS_URL and UPSTASH_REDIS_TOKEN"
            )

    async def connect(self):
        """Connect to Redis."""
        try:
            # Parse Redis URL and add token
            if self.redis_url.startswith("redis://"):
                redis_url = self.redis_url.replace(
                    "redis://", f"redis://:{self.redis_token}@"
                )
            else:
                redis_url = f"redis://:{self.redis_token}@{self.redis_url}"

            self.redis_client = Redis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True,
                retry_on_timeout=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                health_check_interval=30,
            )

            # Test connection
            await self.redis_client.ping()
            logger.info("Connected to Redis successfully")

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise DatabaseError(f"Redis connection failed: {str(e)}")

    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
            logger.info("Disconnected from Redis")

    def set_workspace_id(self, workspace_id: str):
        """Set the current workspace ID for isolation."""
        if not workspace_id or not workspace_id.strip():
            raise ValidationError("Workspace ID cannot be empty")

        self.workspace_id = workspace_id.strip()
        logger.debug(f"Set workspace ID: {self.workspace_id}")

    def _get_workspace_key(self, key: str) -> str:
        """Get workspace-isolated key."""
        if not self.workspace_id:
            raise WorkspaceError("Workspace ID not set")

        return f"{self.key_prefix}:workspace:{self.workspace_id}:{key}"

    async def set(
        self,
        key: str,
        value: Union[str, Dict[str, Any], List[Any]],
        ttl: Optional[int] = None,
        workspace_id: Optional[str] = None,
    ) -> bool:
        """Set a value with workspace isolation."""
        try:
            # Use provided workspace_id or current one
            original_workspace = self.workspace_id
            if workspace_id:
                self.set_workspace_id(workspace_id)

            if not self.workspace_id:
                raise WorkspaceError("Workspace ID not set")

            # Serialize value if needed
            if isinstance(value, (dict, list)):
                value = json.dumps(value)

            # Get workspace-isolated key
            redis_key = self._get_workspace_key(key)

            # Set with TTL
            ttl = ttl or self.default_ttl
            result = await self.redis_client.setex(redis_key, ttl, value)

            # Restore original workspace
            if workspace_id and original_workspace:
                self.set_workspace_id(original_workspace)

            return result

        except Exception as e:
            logger.error(f"Failed to set Redis key {key}: {e}")
            raise DatabaseError(f"Redis set operation failed: {str(e)}")

    async def get(self, key: str, workspace_id: Optional[str] = None) -> Optional[Any]:
        """Get a value with workspace isolation."""
        try:
            # Use provided workspace_id or current one
            original_workspace = self.workspace_id
            if workspace_id:
                self.set_workspace_id(workspace_id)

            if not self.workspace_id:
                raise WorkspaceError("Workspace ID not set")

            # Get workspace-isolated key
            redis_key = self._get_workspace_key(key)
            value = await self.redis_client.get(redis_key)

            # Restore original workspace
            if workspace_id and original_workspace:
                self.set_workspace_id(original_workspace)

            if value is None:
                return None

            # Try to deserialize JSON
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value

        except Exception as e:
            logger.error(f"Failed to get Redis key {key}: {e}")
            raise DatabaseError(f"Redis get operation failed: {str(e)}")

    async def delete(self, key: str, workspace_id: Optional[str] = None) -> bool:
        """Delete a key with workspace isolation."""
        try:
            # Use provided workspace_id or current one
            original_workspace = self.workspace_id
            if workspace_id:
                self.set_workspace_id(workspace_id)

            if not self.workspace_id:
                raise WorkspaceError("Workspace ID not set")

            # Get workspace-isolated key
            redis_key = self._get_workspace_key(key)
            result = await self.redis_client.delete(redis_key)

            # Restore original workspace
            if workspace_id and original_workspace:
                self.set_workspace_id(original_workspace)

            return result > 0

        except Exception as e:
            logger.error(f"Failed to delete Redis key {key}: {e}")
            raise DatabaseError(f"Redis delete operation failed: {str(e)}")

    async def exists(self, key: str, workspace_id: Optional[str] = None) -> bool:
        """Check if a key exists with workspace isolation."""
        try:
            # Use provided workspace_id or current one
            original_workspace = self.workspace_id
            if workspace_id:
                self.set_workspace_id(workspace_id)

            if not self.workspace_id:
                raise WorkspaceError("Workspace ID not set")

            # Get workspace-isolated key
            redis_key = self._get_workspace_key(key)
            result = await self.redis_client.exists(redis_key)

            # Restore original workspace
            if workspace_id and original_workspace:
                self.set_workspace_id(original_workspace)

            return result > 0

        except Exception as e:
            logger.error(f"Failed to check Redis key existence {key}: {e}")
            raise DatabaseError(f"Redis exists operation failed: {str(e)}")

    async def expire(
        self, key: str, ttl: int, workspace_id: Optional[str] = None
    ) -> bool:
        """Set TTL for a key with workspace isolation."""
        try:
            # Use provided workspace_id or current one
            original_workspace = self.workspace_id
            if workspace_id:
                self.set_workspace_id(workspace_id)

            if not self.workspace_id:
                raise WorkspaceError("Workspace ID not set")

            # Get workspace-isolated key
            redis_key = self._get_workspace_key(key)
            result = await self.redis_client.expire(redis_key, ttl)

            # Restore original workspace
            if workspace_id and original_workspace:
                self.set_workspace_id(original_workspace)

            return result

        except Exception as e:
            logger.error(f"Failed to set TTL for Redis key {key}: {e}")
            raise DatabaseError(f"Redis expire operation failed: {str(e)}")

    async def ttl(self, key: str, workspace_id: Optional[str] = None) -> int:
        """Get TTL for a key with workspace isolation."""
        try:
            # Use provided workspace_id or current one
            original_workspace = self.workspace_id
            if workspace_id:
                self.set_workspace_id(workspace_id)

            if not self.workspace_id:
                raise WorkspaceError("Workspace ID not set")

            # Get workspace-isolated key
            redis_key = self._get_workspace_key(key)
            result = await self.redis_client.ttl(redis_key)

            # Restore original workspace
            if workspace_id and original_workspace:
                self.set_workspace_id(original_workspace)

            return result

        except Exception as e:
            logger.error(f"Failed to get TTL for Redis key {key}: {e}")
            raise DatabaseError(f"Redis TTL operation failed: {str(e)}")

    async def keys(
        self, pattern: str = "*", workspace_id: Optional[str] = None
    ) -> List[str]:
        """Get keys matching pattern with workspace isolation."""
        try:
            # Use provided workspace_id or current one
            original_workspace = self.workspace_id
            if workspace_id:
                self.set_workspace_id(workspace_id)

            if not self.workspace_id:
                raise WorkspaceError("Workspace ID not set")

            # Build workspace-isolated pattern
            workspace_pattern = self._get_workspace_key(pattern)
            redis_keys = await self.redis_client.keys(workspace_pattern)

            # Remove prefix from keys
            prefix = f"{self.key_prefix}:workspace:{self.workspace_id}:"
            keys = [key.replace(prefix, "", 1) for key in redis_keys]

            # Restore original workspace
            if workspace_id and original_workspace:
                self.set_workspace_id(original_workspace)

            return keys

        except Exception as e:
            logger.error(f"Failed to get Redis keys {pattern}: {e}")
            raise DatabaseError(f"Redis keys operation failed: {str(e)}")

    async def flush_workspace(self, workspace_id: str) -> int:
        """Flush all keys for a specific workspace."""
        try:
            # Use provided workspace_id
            original_workspace = self.workspace_id
            self.set_workspace_id(workspace_id)

            # Get all workspace keys
            keys = await self.keys("*", workspace_id)

            # Delete all keys
            deleted_count = 0
            for key in keys:
                if await self.delete(key):
                    deleted_count += 1

            # Restore original workspace
            if original_workspace:
                self.set_workspace_id(original_workspace)

            logger.info(f"Flushed {deleted_count} keys for workspace {workspace_id}")
            return deleted_count

        except Exception as e:
            logger.error(f"Failed to flush workspace {workspace_id}: {e}")
            raise DatabaseError(f"Redis flush workspace operation failed: {str(e)}")

    async def get_workspace_stats(self, workspace_id: str) -> Dict[str, Any]:
        """Get statistics for a specific workspace."""
        try:
            # Use provided workspace_id
            original_workspace = self.workspace_id
            self.set_workspace_id(workspace_id)

            # Get all keys
            keys = await self.keys("*", workspace_id)

            # Calculate stats
            stats = {
                "total_keys": len(keys),
                "keys": [],
                "memory_usage": 0,
                "oldest_key": None,
                "newest_key": None,
            }

            if keys:
                # Get TTL for each key
                key_info = []
                oldest_time = None
                newest_time = None

                for key in keys:
                    ttl = await self.ttl(key, workspace_id)
                    key_info.append(
                        {
                            "key": key,
                            "ttl": ttl,
                            "expires_at": (
                                datetime.now() + timedelta(seconds=ttl)
                                if ttl > 0
                                else None
                            ),
                        }
                    )

                    # Track oldest/newest (simplified - would need actual creation time)
                    if oldest_time is None or ttl < oldest_time:
                        oldest_time = ttl
                    if newest_time is None or ttl > newest_time:
                        newest_time = ttl

                stats["keys"] = key_info
                stats["oldest_key_ttl"] = oldest_time
                stats["newest_key_ttl"] = newest_time

            # Restore original workspace
            if original_workspace:
                self.set_workspace_id(original_workspace)

            return stats

        except Exception as e:
            logger.error(f"Failed to get workspace stats {workspace_id}: {e}")
            raise DatabaseError(f"Redis workspace stats operation failed: {str(e)}")

    async def health_check(self) -> Dict[str, Any]:
        """Check Redis health."""
        try:
            if not self.redis_client:
                return {"status": "disconnected", "error": "No Redis client"}

            # Ping Redis
            start_time = datetime.now()
            await self.redis_client.ping()
            response_time = (datetime.now() - start_time).total_seconds()

            # Get info
            info = await self.redis_client.info()

            return {
                "status": "connected",
                "response_time_ms": response_time * 1000,
                "redis_version": info.get("redis_version"),
                "connected_clients": info.get("connected_clients"),
                "used_memory": info.get("used_memory_human"),
                "uptime_seconds": info.get("uptime_in_seconds"),
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def cleanup_expired_keys(self, workspace_id: str) -> int:
        """Clean up expired keys for a workspace."""
        try:
            # Use provided workspace_id
            original_workspace = self.workspace_id
            self.set_workspace_id(workspace_id)

            # Get all keys
            keys = await self.keys("*", workspace_id)

            # Check TTL and delete expired keys
            expired_count = 0
            for key in keys:
                ttl = await self.ttl(key, workspace_id)
                if ttl == -1:  # No expiration set
                    continue
                elif ttl == -2:  # Key expired but not yet deleted
                    if await self.delete(key):
                        expired_count += 1

            # Restore original workspace
            if original_workspace:
                self.set_workspace_id(original_workspace)

            logger.info(
                f"Cleaned up {expired_count} expired keys for workspace {workspace_id}"
            )
            return expired_count

        except Exception as e:
            logger.error(f"Failed to cleanup expired keys {workspace_id}: {e}")
            raise DatabaseError(f"Redis cleanup operation failed: {str(e)}")


# Global Redis client instance
_redis_client: Optional[RedisClient] = None


async def get_redis_client() -> RedisClient:
    """Get or create Redis client instance."""
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient()
        await _redis_client.connect()

    return _redis_client


async def close_redis_client():
    """Close Redis client instance."""
    global _redis_client

    if _redis_client:
        await _redis_client.disconnect()
        _redis_client = None
