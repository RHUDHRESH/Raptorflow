"""
Cache-Aware Middleware for Automatic API Response Caching
Intelligently caches API responses based on request patterns and response characteristics
"""

import asyncio
import hashlib
import json
import logging
import re
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any, Dict, List, Optional, Set, Tuple, Union

logger = logging.getLogger(__name__)


class CacheStrategy(Enum):
    """Caching strategies for API responses."""

    NO_CACHE = "no_cache"
    CACHE_GET = "cache_get"  # Cache only GET requests
    CACHE_SAFE_METHODS = "cache_safe"  # Cache GET, HEAD, OPTIONS
    CACHE_ALL = "cache_all"  # Cache all methods (with caution)
    INTELLIGENT = "intelligent"  # AI-driven caching decisions


class CacheKeyScope(Enum):
    """Scope for cache keys."""

    GLOBAL = "global"
    USER_SPECIFIC = "user"
    WORKSPACE_SPECIFIC = "workspace"
    SESSION_SPECIFIC = "session"
    QUERY_SPECIFIC = "query"


@dataclass
class CacheRule:
    """Cache rule for API endpoints."""

    pattern: str
    strategy: CacheStrategy
    ttl: int
    key_scope: CacheKeyScope
    vary_by: List[str]  # Headers to vary cache by
    exclude_headers: List[str]
    max_response_size: int
    conditions: Dict[str, Any]

    def matches(self, path: str, method: str, headers: Dict[str, str]) -> bool:
        """Check if request matches this rule."""
        # Check path pattern
        if not re.match(self.pattern, path):
            return False

        # Check conditions
        for condition_key, condition_value in self.conditions.items():
            if condition_key == "method" and condition_value != method:
                return False
            elif condition_key == "headers":
                for header, expected_value in condition_value.items():
                    if headers.get(header) != expected_value:
                        return False

        return True


@dataclass
class CacheEntry:
    """Cache entry for API responses."""

    response_data: Dict[str, Any]
    status_code: int
    headers: Dict[str, str]
    timestamp: datetime
    ttl: int
    hit_count: int = 0
    etag: Optional[str] = None
    last_modified: Optional[datetime] = None

    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return (datetime.now() - self.timestamp).total_seconds() > self.ttl

    def access(self) -> Dict[str, Any]:
        """Access the cache entry."""
        self.hit_count += 1
        return {
            "data": self.response_data,
            "status_code": self.status_code,
            "headers": self.headers,
            "etag": self.etag,
            "last_modified": self.last_modified,
        }


class APIResponseCache:
    """Cache for API responses."""

    def __init__(self, max_entries: int = 10000):
        self.max_entries = max_entries
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: List[str] = []

        # Statistics
        self.stats = {"hits": 0, "misses": 0, "sets": 0, "evictions": 0}

    def get(self, key: str) -> Optional[CacheEntry]:
        """Get cache entry."""
        entry = self.cache.get(key)

        if entry:
            if entry.is_expired():
                self.delete(key)
                self.stats["misses"] += 1
                return None

            # Move to end of access order
            if key in self.access_order:
                self.access_order.remove(key)
            self.access_order.append(key)

            self.stats["hits"] += 1
            return entry

        self.stats["misses"] += 1
        return None

    def set(
        self,
        key: str,
        response_data: Dict[str, Any],
        status_code: int,
        headers: Dict[str, str],
        ttl: int,
        etag: Optional[str] = None,
        last_modified: Optional[datetime] = None,
    ):
        """Set cache entry."""
        # Check if we need to evict
        if len(self.cache) >= self.max_entries and key not in self.cache:
            self._evict_oldest()

        entry = CacheEntry(
            response_data=response_data,
            status_code=status_code,
            headers=headers,
            timestamp=datetime.now(),
            ttl=ttl,
            etag=etag,
            last_modified=last_modified,
        )

        self.cache[key] = entry

        # Update access order
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)

        self.stats["sets"] += 1

    def delete(self, key: str):
        """Delete cache entry."""
        if key in self.cache:
            del self.cache[key]

        if key in self.access_order:
            self.access_order.remove(key)

    def clear(self):
        """Clear all cache entries."""
        self.cache.clear()
        self.access_order.clear()

    def _evict_oldest(self):
        """Evict oldest entry."""
        if self.access_order:
            oldest_key = self.access_order.pop(0)
            if oldest_key in self.cache:
                del self.cache[oldest_key]
                self.stats["evictions"] += 1

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / total_requests if total_requests > 0 else 0

        return {
            "entries": len(self.cache),
            "max_entries": self.max_entries,
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "sets": self.stats["sets"],
            "evictions": self.stats["evictions"],
            "hit_rate": hit_rate,
        }


class CacheKeyGenerator:
    """Generates cache keys for API requests."""

    def __init__(self):
        self.vary_headers = ["authorization", "cookie", "accept-language"]

    def generate_key(
        self,
        path: str,
        method: str,
        query_params: Dict[str, Any],
        headers: Dict[str, str],
        body: Optional[str],
        scope: CacheKeyScope,
        user_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> str:
        """Generate cache key for API request."""
        # Base key components
        key_parts = [method.upper(), path]

        # Add query parameters
        if query_params:
            sorted_params = sorted(query_params.items())
            query_string = json.dumps(sorted_params, sort_keys=True)
            key_parts.append(f"q:{hashlib.md5(query_string.encode()).hexdigest()[:8]}")

        # Add body hash for non-GET requests
        if body and method.upper() not in ["GET", "HEAD", "OPTIONS"]:
            body_hash = hashlib.md5(body.encode()).hexdigest()[:8]
            key_parts.append(f"b:{body_hash}")

        # Add scope information
        if scope == CacheKeyScope.USER_SPECIFIC and user_id:
            key_parts.append(f"user:{user_id}")
        elif scope == CacheKeyScope.WORKSPACE_SPECIFIC and workspace_id:
            key_parts.append(f"ws:{workspace_id}")
        elif scope == CacheKeyScope.SESSION_SPECIFIC and session_id:
            key_parts.append(f"sess:{session_id}")

        # Add vary headers
        vary_values = []
        for header in self.vary_headers:
            if header in headers:
                vary_values.append(f"{header}:{headers[header]}")

        if vary_values:
            vary_string = "|".join(sorted(vary_values))
            vary_hash = hashlib.md5(vary_string.encode()).hexdigest()[:8]
            key_parts.append(f"v:{vary_hash}")

        # Generate final key
        key_string = ":".join(key_parts)
        return f"api:{hashlib.sha256(key_string.encode()).hexdigest()}"


class CacheAwareMiddleware:
    """Cache-aware middleware for automatic API response caching."""

    def __init__(
        self,
        app,
        cache_strategy: CacheStrategy = CacheStrategy.INTELLIGENT,
        default_ttl: int = 300,  # 5 minutes
        max_response_size: int = 1024 * 1024,  # 1MB
        enable_compression: bool = True,
    ):
        self.app = app
        self.cache_strategy = cache_strategy
        self.default_ttl = default_ttl
        self.max_response_size = max_response_size
        self.enable_compression = enable_compression

        # Components
        self.response_cache = APIResponseCache()
        self.key_generator = CacheKeyGenerator()

        # Cache rules
        self.cache_rules: List[CacheRule] = []
        self._setup_default_rules()

        # Request/response tracking
        self.request_stats: Dict[str, Any] = {}

    def _setup_default_rules(self):
        """Setup default caching rules."""
        # Cache GET requests for static data
        self.cache_rules.append(
            CacheRule(
                pattern=r"^/api/(users|campaigns|icp)/[^/]+$",
                strategy=CacheStrategy.CACHE_GET,
                ttl=600,  # 10 minutes
                key_scope=CacheKeyScope.WORKSPACE_SPECIFIC,
                vary_by=["authorization"],
                exclude_headers=["set-cookie"],
                max_response_size=512 * 1024,  # 512KB
                conditions={"method": "GET"},
            )
        )

        # Cache analytics endpoints
        self.cache_rules.append(
            CacheRule(
                pattern=r"^/api/analytics/.*",
                strategy=CacheStrategy.CACHE_GET,
                ttl=1800,  # 30 minutes
                key_scope=CacheKeyScope.USER_SPECIFIC,
                vary_by=["authorization"],
                exclude_headers=["set-cookie"],
                max_response_size=2 * 1024 * 1024,  # 2MB
                conditions={"method": "GET"},
            )
        )

        # Don't cache auth endpoints
        self.cache_rules.append(
            CacheRule(
                pattern=r"^/api/auth/.*",
                strategy=CacheStrategy.NO_CACHE,
                ttl=0,
                key_scope=CacheKeyScope.GLOBAL,
                vary_by=[],
                exclude_headers=[],
                max_response_size=0,
                conditions={},
            )
        )

        # Don't cache write operations
        self.cache_rules.append(
            CacheRule(
                pattern=r"^/api/.*",
                strategy=CacheStrategy.CACHE_GET,
                ttl=self.default_ttl,
                key_scope=CacheKeyScope.WORKSPACE_SPECIFIC,
                vary_by=["authorization", "content-type"],
                exclude_headers=["set-cookie"],
                max_response_size=self.max_response_size,
                conditions={"method": ["GET", "HEAD", "OPTIONS"]},
            )
        )

    def add_cache_rule(self, rule: CacheRule):
        """Add a cache rule."""
        self.cache_rules.append(rule)

    def get_cache_rule(
        self, path: str, method: str, headers: Dict[str, str]
    ) -> Optional[CacheRule]:
        """Get matching cache rule for request."""
        for rule in self.cache_rules:
            if rule.matches(path, method, headers):
                return rule
        return None

    def should_cache_response(
        self,
        path: str,
        method: str,
        status_code: int,
        headers: Dict[str, str],
        response_size: int,
    ) -> bool:
        """Determine if response should be cached."""
        # Don't cache error responses
        if status_code >= 400:
            return False

        # Don't cache if response is too large
        if response_size > self.max_response_size:
            return False

        # Check for cache control headers
        cache_control = headers.get("cache-control", "").lower()
        if "no-store" in cache_control or "private" in cache_control:
            return False

        return True

    async def __call__(self, scope, receive, send):
        """ASGI middleware entry point."""
        start_time = time.time()

        # Extract request information
        request = scope.get("type")
        if request != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        method = scope.get("method", "")
        headers = dict(scope.get("headers", []))
        query_string = scope.get("query_string", b"").decode()

        # Parse query parameters
        query_params = {}
        if query_string:
            for param in query_string.split("&"):
                if "=" in param:
                    key, value = param.split("=", 1)
                    query_params[key] = value

        # Get body for non-GET requests
        body = None
        if method.upper() not in ["GET", "HEAD", "OPTIONS"]:
            # Receive body
            body_parts = []
            more_body = True

            while more_body:
                message = await receive()
                message_type = message.get("type")

                if message_type == "http.request":
                    body_parts.append(message.get("body", b""))
                    more_body = message.get("more_body", False)
                elif message_type == "http.disconnect":
                    break

            body = b"".join(body_parts).decode() if body_parts else None

        # Check cache rules
        rule = self.get_cache_rule(path, method, headers)

        # Determine caching strategy
        if not rule or rule.strategy == CacheStrategy.NO_CACHE:
            # No caching - pass through
            await self._pass_through(scope, receive, send, start_time)
            return

        # Generate cache key
        user_id = headers.get("x-user-id")
        workspace_id = headers.get("x-workspace-id")
        session_id = headers.get("x-session-id")

        cache_key = self.key_generator.generate_key(
            path=path,
            method=method,
            query_params=query_params,
            headers=headers,
            body=body,
            scope=rule.key_scope,
            user_id=user_id,
            workspace_id=workspace_id,
            session_id=session_id,
        )

        # Check cache
        cached_entry = self.response_cache.get(cache_key)

        if cached_entry:
            # Cache hit - return cached response
            await self._send_cached_response(cached_entry, send, start_time)
            return

        # Cache miss - proceed with request
        await self._cache_response(
            scope,
            receive,
            send,
            start_time,
            cache_key,
            rule,
            user_id,
            workspace_id,
            session_id,
        )

    async def _pass_through(self, scope, receive, send, start_time):
        """Pass request through without caching."""

        # Wrap send to track response
        async def wrapped_send(message):
            if message.get("type") == "http.response.start":
                # Log response time
                response_time = time.time() - start_time
                logger.debug(f"Response time: {response_time:.3f}s (no cache)")

            await send(message)

        await self.app(scope, receive, wrapped_send)

    async def _send_cached_response(self, cached_entry: CacheEntry, send, start_time):
        """Send cached response."""
        # Add cache headers
        cached_headers = cached_entry.headers.copy()
        cached_headers["x-cache-status"] = "HIT"
        cached_headers["x-cache-age"] = str(
            int((datetime.now() - cached_entry.timestamp).total_seconds())
        )

        if cached_entry.etag:
            cached_headers["etag"] = cached_entry.etag

        if cached_entry.last_modified:
            cached_headers["last-modified"] = cached_entry.last_modified.strftime(
                "%a, %d %b %Y %H:%M:%S GMT"
            )

        # Send response
        await send(
            {
                "type": "http.response.start",
                "status": cached_entry.status_code,
                "headers": [
                    (k.encode(), v.encode()) for k, v in cached_headers.items()
                ],
            }
        )

        await send(
            {
                "type": "http.response.body",
                "body": json.dumps(cached_entry.response_data).encode(),
            }
        )

        # Log response time
        response_time = time.time() - start_time
        logger.debug(f"Response time: {response_time:.3f}s (cache hit)")

    async def _cache_response(
        self,
        scope,
        receive,
        send,
        start_time,
        cache_key: str,
        rule: CacheRule,
        user_id: Optional[str],
        workspace_id: Optional[str],
        session_id: Optional[str],
    ):
        """Cache the response."""
        response_data = None
        response_status = 200
        response_headers = {}

        # Wrap send to capture response
        async def wrapped_send(message):
            nonlocal response_data, response_status, response_headers

            if message.get("type") == "http.response.start":
                response_status = message.get("status", 200)
                response_headers = dict(message.get("headers", []))

                # Convert bytes to strings
                response_headers = {
                    k.decode(): v.decode() for k, v in response_headers.items()
                }

                # Check if response should be cached
                content_length = int(response_headers.get("content-length", 0))
                if not self.should_cache_response(
                    scope["path"],
                    scope["method"],
                    response_status,
                    response_headers,
                    content_length,
                ):
                    # Don't cache - send immediately
                    await send(message)
                    return

            elif message.get("type") == "http.response.body":
                response_data = message.get("body", b"").decode()

                # Cache the response
                try:
                    parsed_data = json.loads(response_data) if response_data else {}

                    # Extract cache-related headers
                    etag = response_headers.get("etag")
                    last_modified_str = response_headers.get("last-modified")
                    last_modified = None
                    if last_modified_str:
                        try:
                            from email.utils import parsedate_to_datetime

                            last_modified = parsedate_to_datetime(last_modified_str)
                        except:
                            pass

                    # Store in cache
                    self.response_cache.set(
                        key=cache_key,
                        response_data=parsed_data,
                        status_code=response_status,
                        headers=response_headers,
                        ttl=rule.ttl,
                        etag=etag,
                        last_modified=last_modified,
                    )

                    logger.debug(f"Cached response: {cache_key}")

                except Exception as e:
                    logger.error(f"Failed to cache response: {e}")

                # Add cache headers
                response_headers["x-cache-status"] = "MISS"

                # Send original message
                message["headers"] = [
                    (k.encode(), v.encode()) for k, v in response_headers.items()
                ]

            await send(message)

        # Process request through app
        await self.app(scope, receive, wrapped_send)

        # Log response time
        response_time = time.time() - start_time
        logger.debug(f"Response time: {response_time:.3f}s (cache miss)")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "cache_stats": self.response_cache.get_stats(),
            "cache_strategy": self.cache_strategy.value,
            "default_ttl": self.default_ttl,
            "max_response_size": self.max_response_size,
            "cache_rules_count": len(self.cache_rules),
        }


# Convenience function for creating middleware
def cache_aware_middleware(
    app,
    cache_strategy: CacheStrategy = CacheStrategy.INTELLIGENT,
    default_ttl: int = 300,
    max_response_size: int = 1024 * 1024,
):
    """Create cache-aware middleware."""
    return CacheAwareMiddleware(
        app=app,
        cache_strategy=cache_strategy,
        default_ttl=default_ttl,
        max_response_size=max_response_size,
    )


# Decorator for caching specific endpoints
def cache_api_response(
    ttl: int = 300,
    strategy: CacheStrategy = CacheStrategy.CACHE_GET,
    scope: CacheKeyScope = CacheKeyScope.WORKSPACE_SPECIFIC,
    vary_by: List[str] = None,
):
    """Decorator for caching API responses."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # This would need to be integrated with the framework
            # For now, it's a placeholder for the concept
            return await func(*args, **kwargs)

        wrapper._cache_config = {
            "ttl": ttl,
            "strategy": strategy,
            "scope": scope,
            "vary_by": vary_by or [],
        }

        return wrapper

    return decorator
