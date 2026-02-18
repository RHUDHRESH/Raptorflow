"""
Infrastructure - Redis Cache Adapter.

Implementation of CachePort using Redis.
"""

from typing import Optional, Dict
import json

from redis.asyncio import Redis

from raptorflow.domain.ai.repositories import CachePort as DomainCachePort
from raptorflow.domain.ai.models import GenerationResult


class RedisCacheAdapter(DomainCachePort):
    """Redis implementation of cache port."""

    def __init__(
        self,
        redis_client: Redis,
        prefix: str = "raptorflow:cache:",
    ):
        self._client = redis_client
        self._prefix = prefix

    def _make_key(self, key: str) -> str:
        """Generate full cache key with prefix."""
        return f"{self._prefix}{key}"

    async def get(self, key: str) -> Optional[GenerationResult]:
        """Get cached result."""
        full_key = self._make_key(key)
        data = await self._client.get(full_key)
        if not data:
            return None

        try:
            # Deserialize cached data
            cached = json.loads(data)
            result = GenerationResult(
                request_id=cached["request_id"],
                text=cached.get("text", ""),
                input_tokens=cached.get("input_tokens", 0),
                output_tokens=cached.get("output_tokens", 0),
                model=cached.get("model", ""),
                provider=cached.get("provider", ""),
                cost_usd=cached.get("cost_usd", 0.0),
                latency_ms=cached.get("latency_ms", 0),
                finish_reason=cached.get("finish_reason", "stop"),
            )
            return result
        except (json.JSONDecodeError, KeyError):
            return None

    async def set(
        self,
        key: str,
        result: GenerationResult,
        ttl_seconds: int = 3600,
    ) -> None:
        """Set cached result with TTL."""
        full_key = self._make_key(key)
        data = {
            "request_id": str(result.request_id),
            "text": result.text,
            "input_tokens": result.input_tokens,
            "output_tokens": result.output_tokens,
            "model": result.model,
            "provider": result.provider,
            "cost_usd": result.cost_usd,
            "latency_ms": result.latency_ms,
            "finish_reason": result.finish_reason,
        }
        await self._client.setex(
            full_key,
            ttl_seconds,
            json.dumps(data),
        )

    async def delete(self, key: str) -> None:
        """Delete cached result."""
        full_key = self._make_key(key)
        await self._client.delete(full_key)

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        full_key = self._make_key(key)
        return await self._client.exists(full_key) > 0

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        full_pattern = self._make_key(pattern)
        keys = []
        async for key in self._client.scan_iter(match=full_pattern):
            keys.append(key)

        if keys:
            return await self._client.delete(*keys)
        return 0


class RedisSimpleCacheAdapter:
    """
    Simple Redis cache adapter for general key-value caching.
    Used by application services.
    """

    def __init__(
        self,
        redis_client: Redis,
        prefix: str = "raptorflow:",
    ):
        self._client = redis_client
        self._prefix = prefix

    def _make_key(self, key: str) -> str:
        return f"{self._prefix}{key}"

    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        full_key = self._make_key(key)
        value = await self._client.get(full_key)
        return value.decode("utf-8") if value else None

    async def set(
        self,
        key: str,
        value: str,
        ttl_seconds: int = 3600,
    ) -> None:
        """Set value in cache with TTL."""
        full_key = self._make_key(key)
        await self._client.setex(full_key, ttl_seconds, value)

    async def delete(self, key: str) -> None:
        """Delete key from cache."""
        full_key = self._make_key(key)
        await self._client.delete(full_key)

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        full_key = self._make_key(key)
        return await self._client.exists(full_key) > 0

    async def get_many(self, keys: list[str]) -> Dict[str, str]:
        """Get multiple values."""
        if not keys:
            return {}

        full_keys = [self._make_key(k) for k in keys]
        values = await self._client.mget(full_keys)

        result = {}
        for key, value in zip(keys, values):
            if value:
                result[key] = value.decode("utf-8")
        return result

    async def set_many(
        self,
        mapping: Dict[str, str],
        ttl_seconds: int = 3600,
    ) -> None:
        """Set multiple values."""
        if not mapping:
            return

        pipeline = self._client.pipeline()
        for key, value in mapping.items():
            full_key = self._make_key(key)
            pipeline.setex(full_key, ttl_seconds, value)
        await pipeline.execute()
