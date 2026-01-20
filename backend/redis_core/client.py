"""
Redis client for Upstash Redis integration.

Provides a singleton client with async operations for Redis.
"""

import json
import os
from typing import Any, Optional

# PRODUCTION: No fallbacks - Upstash Redis is required
try:
    from upstash_redis import Redis
    from upstash_redis.asyncio import Redis as AsyncRedis
except ImportError:
    # Fallback to @upstash/redis
    from upstash import Redis
    from upstash.asyncio import Redis as AsyncRedis


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

    # Basic operations
    async def get(self, key: str) -> Optional[str]:
        """Get string value."""
        return await self.async_client.get(key)

    async def set(
        self,
        key: str,
        value: str,
        ex: Optional[int] = None,  # Expiry in seconds
        px: Optional[int] = None,  # Expiry in milliseconds
        nx: bool = False,  # Only set if not exists
        xx: bool = False,  # Only set if exists
    ) -> bool:
        """Set string value."""
        return await self.async_client.set(key, value, ex=ex, px=px, nx=nx, xx=xx)

    async def delete(self, *keys: str) -> int:
        """Delete keys."""
        return await self.async_client.delete(*keys)

    async def exists(self, *keys: str) -> int:
        """Check if keys exist."""
        return await self.async_client.exists(*keys)

    async def expire(self, key: str, seconds: int) -> bool:
        """Set key expiry."""
        return await self.async_client.expire(key, seconds)

    async def ttl(self, key: str) -> int:
        """Get time to live."""
        return await self.async_client.ttl(key)

    # Counter operations
    async def incr(self, key: str) -> int:
        """Increment counter."""
        return await self.async_client.incr(key)

    async def incrby(self, key: str, amount: int) -> int:
        """Increment counter by amount."""
        return await self.async_client.incrby(key, amount)

    async def decr(self, key: str) -> int:
        """Decrement counter."""
        return await self.async_client.decr(key)

    async def decrby(self, key: str, amount: int) -> int:
        """Decrement counter by amount."""
        return await self.async_client.decrby(key, amount)

    # JSON operations
    async def get_json(self, key: str) -> Optional[dict]:
        """Get JSON value."""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None

    async def set_json(self, key: str, value: dict, ex: Optional[int] = None) -> bool:
        """Set JSON value."""
        return await self.set(key, json.dumps(value), ex=ex)

    # Hash operations
    async def hget(self, key: str, field: str) -> Optional[str]:
        """Get hash field."""
        return await self.async_client.hget(key, field)

    async def hset(self, key: str, field: str, value: str) -> int:
        """Set hash field."""
        return await self.async_client.hset(key, field, value)

    async def hgetall(self, key: str) -> dict:
        """Get all hash fields."""
        return await self.async_client.hgetall(key)

    async def hmset(self, key: str, mapping: dict) -> bool:
        """Set multiple hash fields."""
        return await self.async_client.hmset(key, mapping)

    async def hincrby(self, key: str, field: str, amount: int = 1) -> int:
        """Increment hash field."""
        return await self.async_client.hincrby(key, field, amount)

    async def hincrbyfloat(self, key: str, field: str, amount: float) -> float:
        """Increment hash field by float."""
        return await self.async_client.hincrbyfloat(key, field, amount)

    async def hdel(self, key: str, *fields: str) -> int:
        """Delete hash fields."""
        return await self.async_client.hdel(key, *fields)

    # List operations (for queues)
    async def lpush(self, key: str, *values: str) -> int:
        """Push to left of list."""
        return await self.async_client.lpush(key, *values)

    async def rpush(self, key: str, *values: str) -> int:
        """Push to right of list."""
        return await self.async_client.rpush(key, *values)

    async def lpop(self, key: str) -> Optional[str]:
        """Pop from left of list."""
        return await self.async_client.lpop(key)

    async def rpop(self, key: str) -> Optional[str]:
        """Pop from right of list."""
        return await self.async_client.rpop(key)

    async def lrange(self, key: str, start: int, end: int) -> list:
        """Get range from list."""
        return await self.async_client.lrange(key, start, end)

    async def llen(self, key: str) -> int:
        """Get list length."""
        return await self.async_client.llen(key)

    # Sorted set operations (for rate limiting)
    async def zadd(self, key: str, mapping: dict, ex: Optional[int] = None) -> int:
        """Add to sorted set."""
        # Convert mapping to the format expected by Upstash
        score_members = []
        for member, score in mapping.items():
            score_members.append({"score": float(score), "member": str(member)})
        
        result = await self.async_client.zadd(key, score_members)
        if ex:
            await self.expire(key, ex)
        return result

    async def zremrangebyscore(self, key: str, min_score: float, max_score: float) -> int:
        """Remove members from sorted set by score range."""
        return await self.async_client.zremrangebyscore(key, min_score, max_score)

    async def zcard(self, key: str) -> int:
        """Get sorted set size."""
        return await self.async_client.zcard(key)

    # Health check
    async def ping(self) -> bool:
        """Check Redis connection."""
        try:
            result = await self.async_client.ping()
            # Upstash may return 'PONG' string or True boolean
            return result is True or result == "PONG"
        except Exception:
            return False


# Singleton instance
_redis_client: Optional[RedisClient] = None


def get_redis() -> RedisClient:
    """Get singleton Redis client."""
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient()
    return _redis_client


def get_redis_client() -> RedisClient:
    """Alias for get_redis() for compatibility."""
    return get_redis()
