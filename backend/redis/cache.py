"""
Caching service using Redis.

Provides workspace-isolated caching with TTL support,
cache invalidation, and performance optimization.
"""

import hashlib
import json
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

from .client import get_redis


class CacheDataValidator:
    """Validates cached data to prevent poisoning."""

    def __init__(self):
        self.max_cache_size = 1024 * 1024  # 1MB max per entry
        self.allowed_types = (str, int, float, bool, list, dict, type(None))

    def validate_cache_data(self, data: Any) -> bool:
        """Validate cached data structure."""
        try:
            # Size check
            if len(str(data)) > self.max_cache_size:
                return False

            # Type check
            if not isinstance(data, self.allowed_types):
                return False

            # Recursive validation for complex types
            if isinstance(data, dict):
                for key, value in data.items():
                    if not isinstance(key, str) or len(key) > 256:
                        return False
                    if not self.validate_cache_data(value):
                        return False
            elif isinstance(data, list):
                if len(data) > 1000:  # Max 1000 items per list
                    return False
                for item in data:
                    if not self.validate_cache_data(item):
                        return False

            # Prototype pollution protection
            if isinstance(data, dict):
                dangerous_keys = ["__proto__", "constructor", "prototype"]
                if any(key in dangerous_keys for key in data.keys()):
                    return False

            return True

        except Exception:
            return False

    def sanitize_cache_data(self, data: Any) -> Any:
        """Sanitize cached data."""
        if isinstance(data, dict):
            # Remove dangerous keys
            dangerous_keys = ["__proto__", "constructor", "prototype"]
            return {
                k: self.sanitize_cache_data(v)
                for k, v in data.items()
                if k not in dangerous_keys
            }
        elif isinstance(data, list):
            return [self.sanitize_cache_data(item) for item in data[:1000]]
        else:
            return data


class CacheService:
    """Redis-based caching service with workspace isolation."""

    KEY_PREFIX = "cache:"
    DEFAULT_TTL = 3600  # 1 hour

    def __init__(self):
        self.redis = get_redis()
        self.validator = CacheDataValidator()

        # TTL configurations per cache type
        self.ttl_configs = {
            "foundation": 3600,  # 1 hour
            "icps": 3600,  # 1 hour
            "llm_response": 86400,  # 24 hours
            "semantic": 86400,  # 24 hours
            "default": self.DEFAULT_TTL,
        }

    def _get_key(self, workspace_id: str, key: str) -> str:
        """Get Redis key for cache."""
        return f"{self.KEY_PREFIX}{workspace_id}:{key}"

    async def get(self, workspace_id: str, key: str) -> Optional[Any]:
        """Get cached value."""
        redis_key = self._get_key(workspace_id, key)
        value = await self.redis.get_json(redis_key)
        return value

    async def set(
        self,
        workspace_id: str,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        cache_type: str = "default",
    ) -> bool:
        """Set cached value with validation and sanitization."""
        # Validate data before caching
        if not self.validator.validate_cache_data(value):
            return False  # Reject invalid data

        # Sanitize data
        sanitized_value = self.validator.sanitize_cache_data(value)

        redis_key = self._get_key(workspace_id, key)

        # Determine TTL
        if ttl is None:
            ttl = self.ttl_configs.get(cache_type, self.DEFAULT_TTL)

        return await self.redis.set_json(redis_key, sanitized_value, ex=ttl)

    async def delete(self, workspace_id: str, key: str) -> bool:
        """Delete cached value."""
        redis_key = self._get_key(workspace_id, key)
        result = await self.redis.delete(redis_key)
        return result > 0

    async def clear_workspace(self, workspace_id: str) -> int:
        """Clear all cache for a workspace."""
        # In production, maintain a cache index for efficient clearing
        # For now, this is a placeholder
        pattern = f"{self.KEY_PREFIX}{workspace_id}:*"
        # Note: Upstash Redis doesn't support KEYS command in production
        # Would need to maintain an index of cache keys
        return 0

    async def get_or_set(
        self,
        workspace_id: str,
        key: str,
        factory: Callable,
        ttl: Optional[int] = None,
        cache_type: str = "default",
    ) -> Any:
        """Get value from cache or set using factory function."""
        # Try cache first
        value = await self.get(workspace_id, key)
        if value is not None:
            return value

        # Generate value
        if callable(factory):
            if hasattr(factory, "__await__"):
                value = await factory()
            else:
                value = factory()
        else:
            value = factory

        # Cache the value
        await self.set(workspace_id, key, value, ttl, cache_type)

        return value

    async def exists(self, workspace_id: str, key: str) -> bool:
        """Check if key exists in cache."""
        redis_key = self._get_key(workspace_id, key)
        result = await self.redis.exists(redis_key)
        return result > 0

    async def get_ttl(self, workspace_id: str, key: str) -> int:
        """Get time to live for cached key."""
        redis_key = self._get_key(workspace_id, key)
        return await self.redis.ttl(redis_key)

    async def refresh_ttl(
        self,
        workspace_id: str,
        key: str,
        ttl: Optional[int] = None,
        cache_type: str = "default",
    ) -> bool:
        """Refresh TTL for existing key."""
        redis_key = self._get_key(workspace_id, key)

        if ttl is None:
            ttl = self.ttl_configs.get(cache_type, self.DEFAULT_TTL)

        return await self.redis.expire(redis_key, ttl)

    async def get_multiple(self, workspace_id: str, keys: List[str]) -> Dict[str, Any]:
        """Get multiple cached values."""
        results = {}
        for key in keys:
            value = await self.get(workspace_id, key)
            if value is not None:
                results[key] = value
        return results

    async def set_multiple(
        self,
        workspace_id: str,
        items: Dict[str, Any],
        ttl: Optional[int] = None,
        cache_type: str = "default",
    ) -> int:
        """Set multiple cached values."""
        success_count = 0
        for key, value in items.items():
            if await self.set(workspace_id, key, value, ttl, cache_type):
                success_count += 1
        return success_count

    async def invalidate_pattern(self, workspace_id: str, pattern: str) -> int:
        """Invalidate cache keys matching pattern."""
        # In production, maintain a pattern index
        # For now, placeholder implementation
        return 0


def cached(
    ttl: int = 3600, key_fn: Optional[Callable] = None, cache_type: str = "default"
):
    """Decorator for caching function results."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract workspace_id from first argument or kwargs
            workspace_id = None
            if args and hasattr(args[0], "workspace_id"):
                workspace_id = args[0].workspace_id
            elif "workspace_id" in kwargs:
                workspace_id = kwargs["workspace_id"]
            elif args and isinstance(args[0], str):
                # Assume first arg is workspace_id
                workspace_id = args[0]

            if not workspace_id:
                # No workspace isolation, execute function
                return (
                    await func(*args, **kwargs)
                    if hasattr(func, "__await__")
                    else func(*args, **kwargs)
                )

            # Generate cache key
            if key_fn:
                cache_key = key_fn(*args, **kwargs)
            else:
                # Generate key from function name and args
                key_data = {
                    "func": func.__name__,
                    "args": str(args),
                    "kwargs": str(kwargs),
                }
                cache_key = hashlib.md5(
                    json.dumps(key_data, sort_keys=True).encode()
                ).hexdigest()

            # Get cache service
            cache_service = CacheService()

            # Try cache
            cached_result = await cache_service.get(workspace_id, cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function
            result = (
                await func(*args, **kwargs)
                if hasattr(func, "__await__")
                else func(*args, **kwargs)
            )

            # Cache result
            await cache_service.set(workspace_id, cache_key, result, ttl, cache_type)

            return result

        return wrapper

    return decorator
