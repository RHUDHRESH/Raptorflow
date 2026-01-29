"""
Cache decorators for Redis-based caching.

Provides decorators for caching function results with automatic
cache key generation and invalidation support.
import hashlib
import inspect
import json
from functools import wraps
from typing import Any, Callable, Dict, List, Optional
from .cache import CacheService
def cached(
    ttl: int = 3600,
    key_fn: Optional[Callable] = None,
    cache_type: str = "default",
    workspace_param: str = "workspace_id",
):
    """
    Decorator for caching function results with Redis.
    Args:
        ttl: Time to live in seconds
        key_fn: Function to generate cache key
        cache_type: Type of cache for TTL configuration
        workspace_param: Parameter name containing workspace_id for isolation
    Usage:
        @cached(ttl=1800, cache_type="foundation")
        async def get_foundation_data(workspace_id: str):
            # Function implementation
            pass
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract workspace_id for isolation
            workspace_id = _extract_workspace_id(args, kwargs, workspace_param)
            if not workspace_id:
                # No workspace isolation, execute function directly
                if inspect.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            # Generate cache key
            cache_key = _generate_cache_key(func, args, kwargs, key_fn)
            # Get cache service
            cache_service = CacheService()
            # Try cache first
            cached_result = await cache_service.get(workspace_id, cache_key)
            if cached_result is not None:
                return cached_result
            # Execute function
            if inspect.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            # Cache result
            await cache_service.set(workspace_id, cache_key, result, ttl, cache_type)
            return result
        return wrapper
    return decorator
def cached_method(
    include_self: bool = False,
    Decorator for caching method results.
        include_self: Whether to include 'self' in cache key generation
        class MyService:
            @cached_method(ttl=1800, include_self=True)
            async def get_data(self, workspace_id: str):
                # Method implementation
                pass
            # Extract workspace_id (first argument after self for methods)
            if len(args) > 1:
                workspace_id = args[1]  # Skip 'self'
            elif "workspace_id" in kwargs:
                workspace_id = kwargs["workspace_id"]
                workspace_id = None
            cache_args = (
                args[1:] if include_self else args
            )  # Skip 'self' if not included
            cache_key = _generate_cache_key(func, cache_args, kwargs, key_fn)
def invalidate_cache(pattern: str, workspace_param: str = "workspace_id"):
    Decorator to invalidate cache after function execution.
        pattern: Cache key pattern to invalidate
        workspace_param: Parameter name containing workspace_id
        @invalidate_cache("foundation:*")
        async def update_foundation(workspace_id: str, data: dict):
            # Execute function first
            # Extract workspace_id
            if workspace_id:
                # Invalidate cache pattern
                cache_service = CacheService()
                await cache_service.invalidate_pattern(workspace_id, pattern)
def cache_until_invalidate(
    invalidate_on: Optional[List[str]] = None,
    Decorator that caches until specific conditions invalidate the cache.
        invalidate_on: List of return values that should invalidate cache
        @cache_until_invalidate(ttl=1800, invalidate_on=["error"])
        async def get_data(workspace_id: str):
            workspace_id = _extract_workspace_id(args, kwargs)
            cache_key = _generate_cache_key(func, args, kwargs)
            # Check if result should invalidate cache
            should_invalidate = False
            if invalidate_on:
                if isinstance(result, str):
                    should_invalidate = result in invalidate_on
                elif isinstance(result, (dict, list)):
                    should_invalidate = any(
                        item in invalidate_on
                        for item in (
                            [result] if not isinstance(result, list) else result
                        )
                    )
            if not should_invalidate:
                # Cache result
                await cache_service.set(
                    workspace_id, cache_key, result, ttl, cache_type
                )
def multi_cached(
    keys: List[str],
    Decorator for caching multiple results from a single function.
        keys: List of cache keys to store results under
        @multi_cached(keys=["user_data", "user_permissions"], ttl=1800)
        async def get_user_info(workspace_id: str, user_id: str):
            return {"user_data": {...}, "user_permissions": [...}]
            # Try to get all cached values
            cached_results = {}
            missing_keys = []
            for key in keys:
                cached_value = await cache_service.get(workspace_id, key)
                if cached_value is not None:
                    cached_results[key] = cached_value
                    missing_keys.append(key)
            # If all values are cached, return combined result
            if not missing_keys:
                return cached_results
            # Execute function to get missing values
            # Cache missing values
            for key in missing_keys:
                if key in result:
                    await cache_service.set(
                        workspace_id, key, result[key], ttl, cache_type
                    cached_results[key] = result[key_key]
            return cached_results
def _extract_workspace_id(
    args: tuple, kwargs: dict, workspace_param: str
) -> Optional[str]:
    """Extract workspace_id from function arguments."""
    # Try kwargs first
    if workspace_param in kwargs:
        return kwargs[workspace_param]
    # Try positional arguments
    for arg in args:
        if isinstance(arg, str) and arg.startswith("ws_"):
            return arg
        elif hasattr(arg, "workspace_id"):
            return getattr(arg, "workspace_id")
    return None
def _generate_cache_key(
    func: Callable, args: tuple, kwargs: dict, key_fn: Optional[Callable] = None
) -> str:
    """Generate cache key for function."""
    if key_fn:
        # Use custom key function
        try:
            return key_fn(*args, **kwargs)
        except Exception:
            pass  # Fall back to default key generation
    # Default key generation
    key_data = {
        "func": func.__name__,
        "module": func.__module__,
        "args": str(args)[:200],  # Limit args length
        "kwargs": str(sorted(kwargs.items()))[:200],  # Limit kwargs length
    }
    # Create hash
    key_string = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_string.encode()).hexdigest()
# Context manager for temporary cache bypass
class CacheBypass:
    """Context manager to bypass caching for specific operations."""
    def __init__(self, cache_service: Optional[CacheService] = None):
        self.cache_service = cache_service or CacheService()
        self.original_methods = {}
    def __enter__(self):
        # Store original methods and replace with no-op versions
        self.original_methods["get"] = self.cache_service.get
        self.original_methods["set"] = self.cache_service.set
        async def no_op_get(*args, **kwargs):
            return None
        async def no_op_set(*args, **kwargs):
            return True
        self.cache_service.get = no_op_get
        self.cache_service.set = no_op_set
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore original methods
        self.cache_service.get = self.original_methods["get"]
        self.cache_service.set = self.original_methods["set"]
# Utility functions for cache management
async def clear_cache_for_workspace(workspace_id: str, pattern: str = "*"):
    """Clear all cache for a workspace."""
    cache_service = CacheService()
    if pattern == "*":
        await cache_service.clear_workspace(workspace_id)
    else:
        await cache_service.invalidate_pattern(workspace_id, pattern)
async def warm_cache(workspace_id: str, cache_data: Dict[str, Any], ttl: int = 3600):
    """Warm cache with initial data."""
    await cache_service.set_multiple(workspace_id, cache_data, ttl)
async def get_cache_info(workspace_id: str) -> Dict[str, Any]:
    """Get cache information for workspace."""
    return await cache_service.get_cache_stats(workspace_id)
