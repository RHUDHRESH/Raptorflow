import json
import logging
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from typing import Any, Dict, Optional
from uuid import UUID

from upstash_redis import Redis

from core.config import get_settings


def get_cache_client() -> Optional[Redis]:
    """
    Returns an initialized Upstash Redis client.
    Uses GCP Secret Manager support via get_settings().
    Ensures unified secret retrieval for caching.
    """
    settings = get_settings()
    if not settings.UPSTASH_REDIS_REST_URL or not settings.UPSTASH_REDIS_REST_TOKEN:
        return None
    return Redis(
        url=settings.UPSTASH_REDIS_REST_URL, token=settings.UPSTASH_REDIS_REST_TOKEN
    )


class CacheManager:
    """
    High-level manager for RaptorFlow caching and state persistence.
    Consolidated from core and services for industrial reliability.
    """

    def __init__(self, client: Redis = None):
        self.client = client if client is not None else get_cache_client()

    def set_json(self, key: str, value: Any, expiry_seconds: int = 3600):
        """Saves a JSON-serializable object to Redis."""
        if not self.client:
            return None
        try:
            serialized = json.dumps(value, default=_json_default)
        except TypeError as exc:
            logger = logging.getLogger("raptorflow.cache")
            logger.error("Cache serialization failed for %s: %s", key, exc)
            return None
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


def _json_default(value: Any):
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "dict"):
        return value.dict()
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, UUID):
        return str(value)
    return str(value)


_manager = None


def get_cache_manager() -> CacheManager:
    global _manager
    if _manager is None:
        client = get_cache_client()
        _manager = CacheManager(client=client)
    return _manager
