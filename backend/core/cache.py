import json
from typing import Any, Dict, Optional

from upstash_redis import Redis

from core.config import get_settings


def get_cache_client() -> Redis:
    """
    Returns an initialized Upstash Redis client.
    Uses GCP Secret Manager support via get_settings().
    Ensures unified secret retrieval for caching.
    """
    settings = get_settings()
    if not settings.UPSTASH_REDIS_REST_URL or not settings.UPSTASH_REDIS_REST_TOKEN:
        raise ValueError("Upstash Redis configuration missing. Set UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN.")
    return Redis(
        url=settings.UPSTASH_REDIS_REST_URL, token=settings.UPSTASH_REDIS_REST_TOKEN
    )


class CacheManager:
    """
    High-level manager for RaptorFlow caching and state persistence.
    Consolidated from core and services for industrial reliability.
    """

    def __init__(self, client: Redis = None):
        self.client = client or get_cache_client()

    def set_json(self, key: str, value: Any, expiry_seconds: int = 3600):
        """Saves a JSON-serializable object to Redis."""
        if not self.client:
            return None
        serialized = json.dumps(value)
        return self.client.set(key, serialized, ex=expiry_seconds)

    def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieves and deserializes a JSON object from Redis."""
        if not self.client:
            return None
        data = self.client.get(key)
        if data:
            return json.loads(data)
        return None

    def set_with_expiry(self, key: str, value: str, expiry_seconds: int = 3600):
        if not self.client:
            return None
        return self.client.set(key, value, ex=expiry_seconds)

    def get(self, key: str):
        if not self.client:
            return None
        return self.client.get(key)


_manager = None


def get_cache_manager() -> CacheManager:
    global _manager
    if _manager is None:
        _manager = CacheManager()
    return _manager
