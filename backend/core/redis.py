"""
Core Redis client wrapper for production use.
Provides hard failures for missing Redis configuration.
"""

import logging
import os
from typing import Optional

from redis.client import Redis as AsyncRedis

logger = logging.getLogger(__name__)


class RedisClient:
    """Production Redis client wrapper with hard failures."""

    def __init__(self):
        """Initialize Redis client with production validation."""
        self.url = os.getenv("UPSTASH_REDIS_URL")
        self.token = os.getenv("UPSTASH_REDIS_TOKEN")
        self._client: Optional[AsyncRedis] = None

        # PRODUCTION: Hard failure if credentials missing
        if not self.url or not self.token:
            raise ValueError(
                "UPSTASH_REDIS_URL and UPSTASH_REDIS_TOKEN are required in production"
            )

    async def get_client(self) -> AsyncRedis:
        """Get or create Redis client."""
        if self._client is None:
            # Parse Redis URL and add token
            if self.url.startswith("redis://"):
                redis_url = self.url.replace("redis://", f"redis://:{self.token}@")
            else:
                redis_url = f"redis://:{self.token}@{self.url}"

            self._client = AsyncRedis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True,
                retry_on_timeout=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                health_check_interval=30,
            )

            # Test connection
            await self._client.ping()
            logger.info("Connected to Redis successfully")

        return self._client

    async def close(self):
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            self._client = None
            logger.info("Redis connection closed")


# Global client instance
_redis_client: Optional[RedisClient] = None


async def get_redis_client() -> RedisClient:
    """Get or create Redis client instance."""
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient()
    return _redis_client


async def close_redis_client():
    """Close global Redis client."""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None
