"""
Redis client for Upstash Redis integration.

Provides a singleton client with async operations for Redis.
"""

import json
import os
from typing import Any, Optional

# PRODUCTION: No fallbacks - Upstash Redis is required
from upstash_redis import Redis
from upstash_redis.asyncio import Redis as AsyncRedis


class RedisClient:
    """Upstash Redis client wrapper with typed operations."""

    def __init__(self):
        self.url = os.getenv("UPSTASH_REDIS_URL")
        self.token = os.getenv("UPSTASH_REDIS_TOKEN")
        self._sync_client: Optional[Redis] = None
        self._async_client: Optional[AsyncRedis] = None

        # PRODUCTION: Validate required credentials
        if not self.url or not self.token:
            raise ValueError(
                "UPSTASH_REDIS_URL and UPSTASH_REDIS_TOKEN must be set in production"
            )

    @property
    def sync(self) -> Redis:
        """Get synchronous client."""
        if self._sync_client is None:
            self._sync_client = Redis(url=self.url, token=self.token)
        return self._sync_client

    @property
    def async_client(self) -> AsyncRedis:
        """Get asynchronous client."""
        if self._async_client is None:
            self._async_client = AsyncRedis(url=self.url, token=self.token)
        return self._async_client

    async def get_json(self, key: str) -> Optional[Any]:
        """Get JSON value from Redis."""
        try:
            value = await self.async_client.get(key)
            if value is None:
                return None
            return json.loads(value)
        except (json.JSONDecodeError, Exception):
            return None

    async def set_json(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Set JSON value in Redis."""
        try:
            json_value = json.dumps(value, default=str)
            await self.async_client.set(key, json_value, ex=ex)
            return True
        except Exception:
            return False

    async def delete(self, key: str) -> int:
        """Delete key from Redis."""
        try:
            return await self.async_client.delete(key)
        except Exception:
            return 0

    async def exists(self, key: str) -> int:
        """Check if key exists in Redis."""
        try:
            return await self.async_client.exists(key)
        except Exception:
            return 0

    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for key."""
        try:
            return await self.async_client.expire(key, seconds)
        except Exception:
            return False

    async def ttl(self, key: str) -> int:
        """Get time to live for key."""
        try:
            return await self.async_client.ttl(key)
        except Exception:
            return -1

    async def zadd(self, key: str, mapping: dict, *args, **kwargs) -> int:
        """Add to sorted set."""
        try:
            return await self.async_client.zadd(key, mapping, *args, **kwargs)
        except Exception:
            return 0

    async def zrange(self, key: str, start: int, end: int, *args, **kwargs) -> list:
        """Get range from sorted set."""
        try:
            return await self.async_client.zrange(key, start, end, *args, **kwargs)
        except Exception:
            return []

    async def zrem(self, key: str, *values) -> int:
        """Remove from sorted set."""
        try:
            return await self.async_client.zrem(key, *values)
        except Exception:
            return 0

    async def zcard(self, key: str) -> int:
        """Get sorted set size."""
        try:
            return await self.async_client.zcard(key)
        except Exception:
            return 0

    async def ping(self) -> bool:
        """Ping Redis server."""
        try:
            result = await self.async_client.ping()
            return result is True
        except Exception:
            return False

    async def close(self):
        """Close Redis connections."""
        if self._async_client:
            await self._async_client.close()
        if self._sync_client:
            self._sync_client.close()


# Singleton instance
_redis_client: Optional[RedisClient] = None


def get_redis() -> RedisClient:
    """Get singleton Redis client."""
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient()
    return _redis_client
