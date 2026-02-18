"""
Cache decorator for expensive operations
Uses Redis for distributed caching
"""

import json
import hashlib
from functools import wraps
from typing import Any, Callable, Optional

from backend.infrastructure.cache.redis import get_redis_client


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from function arguments"""
    key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
    return hashlib.md5(key_data.encode()).hexdigest()


def cached(
    ttl: int = 300,
    prefix: str = "cache",
    key_func: Optional[Callable] = None,
):
    """
    Cache decorator for async functions.

    Args:
        ttl: Time to live in seconds (default: 5 minutes)
        prefix: Cache key prefix
        key_func: Custom function to generate cache key

    Example:
        @cached(ttl=600, prefix="user")
        async def get_user(user_id: str):
            return await db.get_user(user_id)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            redis = get_redis_client()

            if not redis:
                return await func(*args, **kwargs)

            if key_func:
                key_suffix = key_func(*args, **kwargs)
            else:
                key_suffix = cache_key(*args, **kwargs)

            full_key = f"{prefix}:{func.__name__}:{key_suffix}"

            cached_value = redis.get(full_key)
            if cached_value:
                try:
                    return json.loads(cached_value)
                except json.JSONDecodeError:
                    return cached_value

            result = await func(*args, **kwargs)

            try:
                cache_value = json.dumps(result)
                redis.setex(full_key, ttl, cache_value)
            except (TypeError, ValueError):
                pass

            return result

        return wrapper

    return decorator


async def invalidate_cache(prefix: str, pattern: str = "*") -> int:
    """Invalidate cache entries matching pattern."""
    redis = get_redis_client()
    if not redis:
        return 0

    full_pattern = f"{prefix}:*{pattern}*"
    keys = redis.keys(full_pattern)

    if keys:
        return redis.delete(*keys)
    return 0
