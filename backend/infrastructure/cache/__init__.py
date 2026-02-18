"""
Cache Infrastructure - Redis caching layer for BCM and prompts.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class CacheClient:
    """
    Redis cache client for caching BCM manifests, prompts, and memories.

    Uses Upstash Redis for serverless-friendly caching.

    Example:
        cache = CacheClient()

        # Cache a manifest
        cache.set("bcm:ws_123", manifest_dict, ttl=3600)

        # Get cached manifest
        manifest = cache.get("bcm:ws_123")
    """

    def __init__(
        self, redis_url: Optional[str] = None, redis_token: Optional[str] = None
    ):
        self._url = redis_url
        self._token = redis_token
        self._client = None
        self._initialized = False

    def _get_client(self):
        if self._client is None:
            from backend.infrastructure.cache.redis import get_redis_client

            self._client = get_redis_client()
        return self._client

    async def initialize(self) -> None:
        """Initialize the cache client."""
        self._client = self._get_client()
        self._initialized = True
        logger.info("Cache client initialized")

    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        try:
            client = self._get_client()
            value = client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as exc:
            logger.warning("Cache get failed for key %s: %s", key, exc)
            return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set a value in cache with TTL."""
        try:
            client = self._get_client()
            client.set(key, json.dumps(value), ex=ttl)
            return True
        except Exception as exc:
            logger.warning("Cache set failed for key %s: %s", key, exc)
            return False

    def delete(self, key: str) -> bool:
        """Delete a value from cache."""
        try:
            client = self._get_client()
            client.delete(key)
            return True
        except Exception as exc:
            logger.warning("Cache delete failed for key %s: %s", key, exc)
            return False

    def get_manifest(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Get cached BCM manifest."""
        return self.get(f"bcm:manifest:{workspace_id}")

    def set_manifest(
        self, workspace_id: str, manifest: Dict[str, Any], ttl: int = 3600
    ) -> bool:
        """Cache a BCM manifest."""
        return self.set(f"bcm:manifest:{workspace_id}", manifest, ttl)

    def get_compiled_prompt(
        self, workspace_id: str, content_type: str
    ) -> Optional[str]:
        """Get cached compiled prompt."""
        return self.get(f"bcm:prompt:{workspace_id}:{content_type}")

    def set_compiled_prompt(
        self, workspace_id: str, content_type: str, prompt: str, ttl: int = 1800
    ) -> bool:
        """Cache a compiled prompt."""
        return self.set(f"bcm:prompt:{workspace_id}:{content_type}", prompt, ttl)

    def get_memory_summary(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Get cached memory summary."""
        return self.get(f"bcm:memory_summary:{workspace_id}")

    def set_memory_summary(
        self, workspace_id: str, summary: Dict[str, Any], ttl: int = 600
    ) -> bool:
        """Cache a memory summary."""
        return self.set(f"bcm:memory_summary:{workspace_id}", summary, ttl)

    def invalidate(self, workspace_id: str) -> None:
        """Invalidate all cache entries for a workspace."""
        patterns = [
            f"bcm:manifest:{workspace_id}",
            f"bcm:prompt:{workspace_id}:*",
            f"bcm:memory_summary:{workspace_id}",
        ]
        for pattern in patterns:
            self.delete(pattern)

    async def health_check(self) -> dict:
        """Check cache health."""
        try:
            client = self._get_client()
            client.ping()
            return {"status": "healthy"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


_cache_client: Optional[CacheClient] = None


def get_cache_client() -> CacheClient:
    """Get the global cache client instance."""
    global _cache_client
    if _cache_client is None:
        _cache_client = CacheClient()
    return _cache_client


__all__ = ["CacheClient", "get_cache_client"]
