"""
Request-level caching system for RaptorFlow
Intelligent caching with TTL and invalidation strategies
"""

import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class CacheConfig:
    """Cache configuration"""

    def __init__(
        self,
        ttl_seconds: int = 300,  # 5 minutes default
        max_size: int = 1000,
        key_prefix: str = "cache",
        include_query_params: bool = True,
        vary_on_headers: Optional[list] = None,
        skip_cache_on_status: Optional[list] = None,
    ):
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self.key_prefix = key_prefix
        self.include_query_params = include_query_params
        self.vary_on_headers = vary_on_headers or ["Authorization"]
        self.skip_cache_on_status = skip_cache_on_status or [404, 500, 502, 503]


class RequestCache:
    """Request-level caching system"""

    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        self.config = CacheConfig()

    def _generate_cache_key(
        self, request: Request, endpoint_key: Optional[str] = None
    ) -> str:
        """Generate cache key for request"""

        # Start with method and path
        key_parts = [self.config.key_prefix, request.method.lower(), request.url.path]

        # Add endpoint-specific key if provided
        if endpoint_key:
            key_parts.append(endpoint_key)

        # Add query parameters if enabled
        if self.config.include_query_params:
            query_params = dict(request.query_params)
            if query_params:
                # Sort params for consistent key generation
                sorted_params = sorted(query_params.items())
                query_string = "&".join([f"{k}={v}" for k, v in sorted_params])
                key_parts.append(hashlib.md5(query_string.encode()).hexdigest()[:8])

        # Add header variations
        for header in self.config.vary_on_headers:
            header_value = request.headers.get(header)
            if header_value:
                # Hash header value for security and length
                header_hash = hashlib.md5(header_value.encode()).hexdigest()[:8]
                key_parts.append(f"{header.lower()}:{header_hash}")

        return ":".join(key_parts)

    async def get(
        self, request: Request, endpoint_key: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get cached response"""
        try:
            cache_key = self._generate_cache_key(request, endpoint_key)

            if not self.redis_client:
                return None

            cached_data = await self.redis_client.get(cache_key)

            if cached_data:
                cache_entry = json.loads(cached_data)

                # Check if cache is still valid
                cached_at = datetime.fromisoformat(cache_entry["cached_at"])
                if datetime.utcnow() - cached_at < timedelta(
                    seconds=cache_entry["ttl"]
                ):
                    logger.debug(f"Cache hit for {cache_key}")
                    return cache_entry
                else:
                    # Cache expired, remove it
                    await self.redis_client.delete(cache_key)
                    logger.debug(f"Cache expired for {cache_key}")

            return None

        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    async def set(
        self,
        request: Request,
        response_data: Dict[str, Any],
        endpoint_key: Optional[str] = None,
        ttl_seconds: Optional[int] = None,
    ) -> bool:
        """Cache response data"""
        try:
            cache_key = self._generate_cache_key(request, endpoint_key)

            if not self.redis_client:
                return False

            # Prepare cache entry
            ttl = ttl_seconds or self.config.ttl_seconds
            cache_entry = {
                "data": response_data,
                "cached_at": datetime.utcnow().isoformat(),
                "ttl": ttl,
                "status_code": response_data.get("status_code", 200),
                "content_type": response_data.get("content_type", "application/json"),
            }

            # Store in Redis
            success = await self.redis_client.set(
                cache_key, json.dumps(cache_entry), ex=ttl
            )

            if success:
                logger.debug(f"Cached response for {cache_key}")

            return success

        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    async def invalidate(self, pattern: str) -> int:
        """Invalidate cache entries matching pattern"""
        try:
            if not self.redis_client:
                return 0

            keys = await self.redis_client.keys(f"{self.config.key_prefix}:{pattern}")

            if keys:
                deleted = await self.redis_client.delete(*keys)
                logger.info(f"Invalidated {deleted} cache entries matching {pattern}")
                return deleted

            return 0

        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
            return 0

    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            if not self.redis_client:
                return {"error": "Redis client not available"}

            # Count cache keys
            keys = await self.redis_client.keys(f"{self.config.key_prefix}:*")

            return {
                "total_keys": len(keys),
                "key_prefix": self.config.key_prefix,
                "ttl_seconds": self.config.ttl_seconds,
                "max_size": self.config.max_size,
            }

        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {"error": str(e)}


# Global cache instance
_request_cache: Optional[RequestCache] = None


def get_request_cache() -> RequestCache:
    """Get global request cache instance"""
    global _request_cache
    if _request_cache is None:
        _request_cache = RequestCache()
    return _request_cache


def cache_response(
    ttl_seconds: int = 300,
    endpoint_key: Optional[str] = None,
    vary_on_headers: Optional[list] = None,
    skip_cache_on_status: Optional[list] = None,
):
    """
    Decorator for caching endpoint responses

    Args:
        ttl_seconds: Cache TTL in seconds
        endpoint_key: Custom endpoint key for cache
        vary_on_headers: Headers that should vary cache
        skip_cache_on_status: Status codes that shouldn't be cached
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract request from kwargs
            request = kwargs.get("request")
            if not request:
                return await func(*args, **kwargs)

            cache = get_request_cache()

            # Try to get from cache
            cached_response = await cache.get(request, endpoint_key)
            if cached_response:
                return JSONResponse(
                    content=cached_response["data"],
                    status_code=cached_response["status_code"],
                    headers={"content-type": cached_response["content_type"]},
                )

            # Execute function
            response = await func(*args, **kwargs)

            # Convert response to dict for caching
            if isinstance(response, JSONResponse):
                response_data = {
                    "data": json.loads(response.body.decode()) if response.body else {},
                    "status_code": response.status_code,
                    "content_type": response.headers.get(
                        "content-type", "application/json"
                    ),
                }
            else:
                response_data = {
                    "data": response,
                    "status_code": 200,
                    "content_type": "application/json",
                }

            # Check if we should skip caching based on status
            skip_statuses = skip_cache_on_status or [404, 500, 502, 503]
            if response_data["status_code"] not in skip_statuses:
                # Cache the response
                await cache.set(request, response_data, endpoint_key, ttl_seconds)

            return response

        return wrapper

    return decorator


class CacheMiddleware:
    """Cache middleware for automatic request caching"""

    def __init__(self, app, cache_config: Optional[CacheConfig] = None):
        self.app = app
        self.config = cache_config or CacheConfig()
        self.cache = RequestCache()

        # Endpoints to cache with their TTL
        self.cacheable_endpoints = {
            "/api/v1/icps": 300,  # 5 minutes
            "/api/v1/workspaces": 600,  # 10 minutes
            "/api/v1/users/me": 300,  # 5 minutes
            "/api/v1/foundation": 900,  # 15 minutes
            "/api/v1/moves": 300,  # 5 minutes
        }

    async def __call__(self, scope, receive, send):
        """ASGI middleware implementation"""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Create request-like object for caching
        method = scope["method"]
        path = scope["path"]
        headers = dict(scope.get("headers", []))
        query_string = scope.get("query_string", b"").decode()

        # Check if this endpoint should be cached
        if method != "GET" or path not in self.cacheable_endpoints:
            await self.app(scope, receive, send)
            return

        # Create mock request for cache key generation
        class MockRequest:
            def __init__(self):
                self.method = method
                self.url = MockURL(path, query_string)
                self.headers = headers
                self.query_params = MockQueryParams(query_string)

        class MockURL:
            def __init__(self, path, query_string):
                self.path = path
                self.query = query_string

        class MockQueryParams:
            def __init__(self, query_string):
                if query_string:
                    params = {}
                    for param in query_string.split("&"):
                        if "=" in param:
                            key, value = param.split("=", 1)
                            params[key] = value
                    self._params = params
                else:
                    self._params = {}

            def get(self, key, default=None):
                return self._params.get(key, default)

            def items(self):
                return self._params.items()

        mock_request = MockRequest()

        # Try to get from cache
        cached_response = await self.cache.get(mock_request)
        if cached_response:
            # Send cached response
            response = JSONResponse(
                content=cached_response["data"],
                status_code=cached_response["status_code"],
                headers={"content-type": cached_response["content_type"]},
            )

            await send(
                {
                    "type": "http.response.start",
                    "status": response.status_code,
                    "headers": [
                        (k.encode(), v.encode()) for k, v in response.headers.items()
                    ],
                }
            )

            await send(
                {
                    "type": "http.response.body",
                    "body": response.body,
                }
            )
            return

        # Continue with normal request processing
        # This would need more complex implementation for full middleware
        await self.app(scope, receive, send)


# Cache invalidation utilities
async def invalidate_user_cache(user_id: str) -> int:
    """Invalidate all cache entries for a user"""
    cache = get_request_cache()
    return await cache.invalidate(f"*user:{user_id}*")


async def invalidate_workspace_cache(workspace_id: str) -> int:
    """Invalidate all cache entries for a workspace"""
    cache = get_request_cache()
    return await cache.invalidate(f"*workspace:{workspace_id}*")


async def invalidate_endpoint_cache(endpoint: str) -> int:
    """Invalidate all cache entries for an endpoint"""
    cache = get_request_cache()
    return await cache.invalidate(f"*{endpoint}*")
