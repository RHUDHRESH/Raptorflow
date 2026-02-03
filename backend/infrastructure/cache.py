"""
Cache Infrastructure Layer
Handles Upstash Redis connections and operations
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel
from upstash_redis import Redis

logger = logging.getLogger(__name__)


class CacheConfig(BaseModel):
    """Cache/Redis configuration settings"""
    rest_url: str
    rest_token: str
    url: str
    max_connections: int = 10
    retry_attempts: int = 3
    retry_delay: float = 1.0


class CacheClient:
    """Cache client wrapper with error handling and connection management"""

    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or self._load_config()
        self._client: Optional[Redis] = None
        # Lazy init: do not connect at import time

    def _load_config(self) -> CacheConfig:
        """Load cache configuration from environment variables"""
        return CacheConfig(
            rest_url=os.getenv("UPSTASH_REDIS_REST_URL", ""),
            rest_token=os.getenv("UPSTASH_REDIS_REST_TOKEN", ""),
            url=os.getenv("REDIS_URL", ""),
            max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", "10")),
            retry_attempts=int(os.getenv("REDIS_RETRY_ATTEMPTS", "3")),
            retry_delay=float(os.getenv("REDIS_RETRY_DELAY", "1.0")),
        )

    def _initialize_client(self):
        """Initialize Redis client"""
        try:
            if not self.config.rest_url or not self.config.rest_token:
                raise ValueError(
                    "Redis not configured. Set UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN."
                )
            self._client = Redis(url=self.config.rest_url, token=self.config.rest_token)
            logger.info("Cache client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize cache client: {e}")
            raise

    def get_client(self) -> Redis:
        """Get Redis client instance"""
        if not self._client:
            self._initialize_client()
        return self._client

    async def get(self, key: str) -> Optional[Any]:
        """Get a value by key"""
        try:
            client = self.get_client()
            value = client.get(key)

            if value is None:
                return None

            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.error(f"Failed to get key {key}: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a key-value pair with optional TTL"""
        try:
            client = self.get_client()
            serialized_value = (
                json.dumps(value)
                if not isinstance(value, (str, int, float, bool))
                else str(value)
            )

            if ttl:
                result = client.setex(key, ttl, serialized_value)
            else:
                result = client.set(key, serialized_value)

            return result
        except Exception as e:
            logger.error(f"Failed to set key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete a key"""
        try:
            client = self.get_client()
            result = client.delete(key)
            return result
        except Exception as e:
            logger.error(f"Failed to delete key {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if a key exists"""
        try:
            client = self.get_client()
            result = client.exists(key)
            return result
        except Exception as e:
            logger.error(f"Failed to check existence of key {key}: {e}")
            return False

    async def expire(self, key: str, ttl: int) -> bool:
        """Set TTL for a key"""
        try:
            client = self.get_client()
            result = client.expire(key, ttl)
            return result
        except Exception as e:
            logger.error(f"Failed to set TTL for key {key}: {e}")
            return False

    async def ttl(self, key: str) -> int:
        """Get TTL for a key"""
        try:
            client = self.get_client()
            result = client.ttl(key)
            return result
        except Exception as e:
            logger.error(f"Failed to get TTL for key {key}: {e}")
            return -1

    async def incr(self, key: str, amount: int = 1) -> int:
        """Increment a key by amount"""
        try:
            client = self.get_client()
            result = client.incrby(key, amount)
            return result
        except Exception as e:
            logger.error(f"Failed to increment key {key}: {e}")
            return 0

    async def decr(self, key: str, amount: int = 1) -> int:
        """Decrement a key by amount"""
        try:
            client = self.get_client()
            result = client.decrby(key, amount)
            return result
        except Exception as e:
            logger.error(f"Failed to decrement key {key}: {e}")
            return 0

    async def hget(self, key: str, field: str) -> Optional[Any]:
        """Get a field from a hash"""
        try:
            client = self.get_client()
            value = client.hget(key, field)

            if value is None:
                return None

            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.error(f"Failed to get hash field {key}.{field}: {e}")
            return None

    async def hset(self, key: str, field: str, value: Any) -> int:
        """Set a field in a hash"""
        try:
            client = self.get_client()
            serialized_value = (
                json.dumps(value)
                if not isinstance(value, (str, int, float, bool))
                else str(value)
            )
            result = client.hset(key, field, serialized_value)
            return result
        except Exception as e:
            logger.error(f"Failed to set hash field {key}.{field}: {e}")
            return 0

    async def hgetall(self, key: str) -> Dict[str, Any]:
        """Get all fields from a hash"""
        try:
            client = self.get_client()
            hash_data = client.hgetall(key)

            if not hash_data:
                return {}

            parsed_data = {}
            for field, value in hash_data.items():
                try:
                    parsed_data[field] = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    parsed_data[field] = value

            return parsed_data
        except Exception as e:
            logger.error(f"Failed to get all hash fields for {key}: {e}")
            return {}

    async def health_check(self) -> Dict[str, Any]:
        """Check cache connection health"""
        try:
            client = self.get_client()
            test_key = "health_check"
            test_value = {"status": "ok"}

            await self.set(test_key, test_value, ttl=10)
            retrieved_value = await self.get(test_key)
            await self.delete(test_key)

            if retrieved_value == test_value:
                return {
                    "status": "healthy",
                    "message": "Cache connection is working",
                    "timestamp": "2024-01-01T00:00:00Z",
                }
            else:
                return {
                    "status": "unhealthy",
                    "message": "Cache connection test failed",
                    "timestamp": "2024-01-01T00:00:00Z",
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Cache connection failed: {str(e)}",
                "timestamp": "2024-01-01T00:00:00Z",
            }

    # Session Management
    async def create_session(self, session_id: str, user_data: Dict[str, Any], ttl: int = 3600) -> bool:
        """Create a new session"""
        try:
            session_data = {
                "user_data": user_data,
                "created_at": "2024-01-01T00:00:00Z",
                "last_accessed": "2024-01-01T00:00:00Z",
            }
            return await self.set(f"session:{session_id}", session_data, ttl)
        except Exception as e:
            logger.error(f"Failed to create session {session_id}: {e}")
            return False

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        try:
            session_data = await self.get(f"session:{session_id}")
            if session_data:
                session_data["last_accessed"] = "2024-01-01T00:00:00Z"
                await self.set(f"session:{session_id}", session_data)
            return session_data
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        try:
            return await self.delete(f"session:{session_id}")
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False

    # Rate Limiting
    async def check_rate_limit(self, key: str, limit: int, window: int = 60) -> bool:
        """Check if rate limit is exceeded"""
        try:
            current_count = await self.incr(key)
            if current_count == 1:
                await self.expire(key, window)
            return current_count <= limit
        except Exception as e:
            logger.error(f"Failed to check rate limit for {key}: {e}")
            return True

    # Cache Helpers
    async def cache_get(self, key: str) -> Optional[Any]:
        """Get a cached value"""
        return await self.get(f"cache:{key}")

    async def cache_set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set a cached value"""
        return await self.set(f"cache:{key}", value, ttl)

    async def cache_delete(self, key: str) -> bool:
        """Delete a cached value"""
        return await self.delete(f"cache:{key}")


_cache_client: Optional[CacheClient] = None


def get_cache() -> CacheClient:
    """Get cache client instance"""
    global _cache_client
    if _cache_client is None:
        _cache_client = CacheClient()
    return _cache_client
