"""
Upstash Redis Client Configuration
Handles Upstash Redis connections and operations
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel
from upstash_redis import Redis

logger = logging.getLogger(__name__)


class UpstashConfig(BaseModel):
    """Upstash Redis configuration settings"""

    rest_url: str
    rest_token: str
    url: str
    max_connections: int = 10
    retry_attempts: int = 3
    retry_delay: float = 1.0


class UpstashClient:
    """Upstash Redis client wrapper with error handling and connection management"""

    def __init__(self, config: Optional[UpstashConfig] = None):
        self.config = config or self._load_config()
        self._client: Optional[Redis] = None
        self._initialize_client()

    def _load_config(self) -> UpstashConfig:
        """Load Upstash configuration from environment variables"""
        return UpstashConfig(
            rest_url=os.getenv("UPSTASH_REDIS_REST_URL", ""),
            rest_token=os.getenv("UPSTASH_REDIS_REST_TOKEN", ""),
            url=os.getenv("REDIS_URL", ""),
            max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", "10")),
            retry_attempts=int(os.getenv("REDIS_RETRY_ATTEMPTS", "3")),
            retry_delay=float(os.getenv("REDIS_RETRY_DELAY", "1.0")),
        )

    def _initialize_client(self):
        """Initialize Upstash Redis client"""
        try:
            self._client = Redis(url=self.config.rest_url, token=self.config.rest_token)
            logger.info("Upstash Redis client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Upstash Redis client: {e}")
            raise

    def get_client(self) -> Redis:
        """Get Upstash Redis client instance"""
        if not self._client:
            self._initialize_client()
        return self._client

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

    async def get(self, key: str) -> Optional[Any]:
        """Get a value by key"""
        try:
            client = self.get_client()
            value = client.get(key)

            if value is None:
                return None

            try:
                # Try to parse as JSON first
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                # Return as string if not JSON
                return value
        except Exception as e:
            logger.error(f"Failed to get key {key}: {e}")
            return None

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

    async def hgetall(self, key: str) -> Dict[str, Any]:
        """Get all fields from a hash"""
        try:
            client = self.get_client()
            hash_data = client.hgetall(key)

            if not hash_data:
                return {}

            # Try to parse JSON values
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

    async def hdel(self, key: str, field: str) -> int:
        """Delete a field from a hash"""
        try:
            client = self.get_client()
            result = client.hdel(key, field)
            return result
        except Exception as e:
            logger.error(f"Failed to delete hash field {key}.{field}: {e}")
            return 0

    async def lpush(self, key: str, value: Any) -> int:
        """Push a value to the left of a list"""
        try:
            client = self.get_client()
            serialized_value = (
                json.dumps(value)
                if not isinstance(value, (str, int, float, bool))
                else str(value)
            )
            result = client.lpush(key, serialized_value)
            return result
        except Exception as e:
            logger.error(f"Failed to lpush to list {key}: {e}")
            return 0

    async def rpop(self, key: str) -> Optional[Any]:
        """Pop a value from the right of a list"""
        try:
            client = self.get_client()
            value = client.rpop(key)

            if value is None:
                return None

            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.error(f"Failed to rpop from list {key}: {e}")
            return None

    async def lrange(self, key: str, start: int = 0, end: int = -1) -> List[Any]:
        """Get a range of elements from a list"""
        try:
            client = self.get_client()
            values = client.lrange(key, start, end)

            if not values:
                return []

            # Try to parse JSON values
            parsed_values = []
            for value in values:
                try:
                    parsed_values.append(json.loads(value))
                except (json.JSONDecodeError, TypeError):
                    parsed_values.append(value)

            return parsed_values
        except Exception as e:
            logger.error(f"Failed to get range from list {key}: {e}")
            return []

    async def health_check(self) -> Dict[str, Any]:
        """Check Upstash Redis connection health"""
        try:
            client = self.get_client()
            # Simple health check - try to set and get a key
            test_key = "health_check"
            test_value = {"status": "ok"}

            await self.set(test_key, test_value, ttl=10)
            retrieved_value = await self.get(test_key)
            await self.delete(test_key)

            if retrieved_value == test_value:
                return {
                    "status": "healthy",
                    "message": "Upstash Redis connection is working",
                    "timestamp": "2024-01-01T00:00:00Z",
                }
            else:
                return {
                    "status": "unhealthy",
                    "message": "Upstash Redis connection test failed",
                    "timestamp": "2024-01-01T00:00:00Z",
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Upstash Redis connection failed: {str(e)}",
                "timestamp": "2024-01-01T00:00:00Z",
            }

    # Session Management Methods
    async def create_session(
        self, session_id: str, user_data: Dict[str, Any], ttl: int = 3600
    ) -> bool:
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
                # Update last accessed time
                session_data["last_accessed"] = "2024-01-01T00:00:00Z"
                await self.set(f"session:{session_id}", session_data)
            return session_data
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None

    async def update_session(self, session_id: str, user_data: Dict[str, Any]) -> bool:
        """Update session data"""
        try:
            session_data = await self.get_session(session_id)
            if session_data:
                session_data["user_data"] = user_data
                session_data["last_accessed"] = "2024-01-01T00:00:00Z"
                return await self.set(f"session:{session_id}", session_data)
            return False
        except Exception as e:
            logger.error(f"Failed to update session {session_id}: {e}")
            return False

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        try:
            return await self.delete(f"session:{session_id}")
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False

    # Rate Limiting Methods
    async def check_rate_limit(self, key: str, limit: int, window: int = 60) -> bool:
        """Check if rate limit is exceeded"""
        try:
            current_count = await self.incr(key)
            if current_count == 1:
                # First request in window, set expiration
                await self.expire(key, window)

            return current_count <= limit
        except Exception as e:
            logger.error(f"Failed to check rate limit for {key}: {e}")
            return True  # Allow request if check fails

    async def reset_rate_limit(self, key: str) -> bool:
        """Reset rate limit counter"""
        try:
            return await self.delete(key)
        except Exception as e:
            logger.error(f"Failed to reset rate limit for {key}: {e}")
            return False

    # Cache Methods
    async def cache_set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set a cached value"""
        return await self.set(f"cache:{key}", value, ttl)

    async def cache_get(self, key: str) -> Optional[Any]:
        """Get a cached value"""
        return await self.get(f"cache:{key}")

    async def cache_delete(self, key: str) -> bool:
        """Delete a cached value"""
        return await self.delete(f"cache:{key}")

    async def clear_pattern(self, pattern: str) -> int:
        """Clear values matching a general pattern (no prefix)"""
        try:
            client = self.get_client()
            keys = client.keys(pattern)
            if keys:
                return client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Failed to clear pattern {pattern}: {e}")
            return 0

    async def cache_clear(self, pattern: str = "*") -> int:
        """Clear cached values matching pattern"""
        try:
            client = self.get_client()
            keys = client.keys(f"cache:{pattern}")
            if keys:
                return client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Failed to clear cache for pattern {pattern}: {e}")
            return 0

    # BCM Methods
    async def get_bcm(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Get latest BCM for a workspace from cache"""
        try:
            return await self.get(f"bcm:w:{workspace_id}:latest")
        except Exception as e:
            logger.error(f"Failed to get BCM for workspace {workspace_id}: {e}")
            return None

    async def set_bcm(
        self,
        workspace_id: str,
        manifest: Dict[str, Any],
        version: int,
        ttl: int = 86400,
    ) -> bool:
        """
        Set BCM in cache with write-through to Supabase

        Args:
            workspace_id: Workspace UUID
            manifest: BCM JSON content
            version: Integer version number
            ttl: Cache TTL in seconds (default 24h)
        """
        try:
            # First write to Supabase (TODO: Implement Supabase write)
            # Then cache in Upstash
            bcm_data = {
                "manifest": manifest,
                "version": version,
                "updated_at": "2024-01-01T00:00:00Z",  # TODO: Use actual timestamp
            }
            return await self.set(f"bcm:w:{workspace_id}:latest", bcm_data, ttl)
        except Exception as e:
            logger.error(f"Failed to set BCM for workspace {workspace_id}: {e}")
            return False

    async def delete_bcm(self, workspace_id: str) -> bool:
        """Delete BCM cache for a workspace"""
        try:
            return await self.delete(f"bcm:w:{workspace_id}:latest")
        except Exception as e:
            logger.error(f"Failed to delete BCM for workspace {workspace_id}: {e}")
            return False

    async def get_bcm_version(
        self, workspace_id: str, version: int
    ) -> Optional[Dict[str, Any]]:
        """Get specific BCM version (fallback to Supabase if not cached)"""
        try:
            # First try cache
            cached = await self.get(f"bcm:w:{workspace_id}:v:{version}")
            if cached:
                return cached

            # Fallback to Supabase (TODO: Implement Supabase fallback)
            return None
        except Exception as e:
            logger.error(
                f"Failed to get BCM version {version} for workspace {workspace_id}: {e}"
            )
            return None


# Global instance
upstash_client = UpstashClient()

# Backward compatibility alias
upstash_redis = upstash_client


def get_upstash_client() -> UpstashClient:
    """Get Upstash Redis client instance"""
    return upstash_client
