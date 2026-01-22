"""
Core Redis client wrapper for production use.
Provides hard failures for missing Redis configuration.
"""

import logging
import os
from typing import Optional

from upstash_redis import Redis as SyncRedis

logger = logging.getLogger(__name__)


class RedisClient:
    """Production Redis client wrapper with hard failures."""

    def __init__(self):
        """Initialize Redis client with production validation."""
        self.url = os.getenv("UPSTASH_REDIS_URL")
        self.token = os.getenv("UPSTASH_REDIS_TOKEN")
        self._client: Optional[SyncRedis] = None

        # PRODUCTION: Hard failure if credentials missing
        if not self.url or not self.token:
            raise ValueError(
                "UPSTASH_REDIS_URL and UPSTASH_REDIS_TOKEN are required in production"
            )

    def get_client(self) -> SyncRedis:
        """Get or create Redis client."""
        if self._client is None:
            # Create Upstash Redis client
            self._client = SyncRedis(url=self.url, token=self.token)

            # Test connection
            result = self._client.ping()
            if result == "PONG":
                logger.info("Connected to Redis successfully")
            else:
                raise ConnectionError("Redis ping failed")

        return self._client

    async def get_async_client(self) -> SyncRedis:
        """Get Redis client (async interface for compatibility)."""
        return self.get_client()

    def close(self):
        """Close Redis connection."""
        if self._client:
            # Upstash Redis doesn't need explicit closing
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


def close_redis_client():
    """Close global Redis client."""
    global _redis_client
    if _redis_client:
        _redis_client.close()
        _redis_client = None
