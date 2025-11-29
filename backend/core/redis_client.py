"""
Redis Client Factory for RaptorFlow Backend

Provides centralized async Redis client creation and management.
Supports both localhost development and Upstash Redis cloud.
"""

import redis.asyncio as redis
from typing import Optional
from contextlib import asynccontextmanager

from backend.core.config import get_settings


class RedisClientFactory:
    """Factory for creating and managing Redis connections."""

    def __init__(self):
        self._client: Optional[redis.Redis] = None
        self._settings = get_settings()

    async def get_client(self) -> redis.Redis:
        """
        Get or create a Redis client instance.

        Returns:
            Async Redis client instance

        Raises:
            ConnectionError: If Redis connection fails
        """
        if self._client is None:
            try:
                self._client = redis.from_url(
                    self._settings.redis_url,
                    max_connections=self._settings.redis_max_connections,
                    socket_timeout=self._settings.redis_socket_timeout,
                    retry_on_timeout=True,
                    socket_connect_timeout=self._settings.redis_socket_timeout,
                    decode_responses=True,  # Decode strings automatically
                )

                # Test connection
                await self._client.ping()

            except Exception as e:
                raise ConnectionError(f"Failed to connect to Redis: {e}")

        return self._client

    async def close(self) -> None:
        """Close the Redis connection."""
        if self._client:
            await self._client.aclose()
            self._client = None

    @asynccontextmanager
    async def connection_context(self):
        """
        Context manager for Redis connections.

        Usage:
            async with redis_factory.connection_context() as client:
                await client.set("key", "value")
        """
        client = None
        try:
            client = await self.get_client()
            yield client
        finally:
            # Don't close here - keep connection alive for reuse
            pass


# Global factory instance
_redis_factory = RedisClientFactory()


async def get_redis_client() -> redis.Redis:
    """
    Get the global Redis client instance.

    This is the main entry point for Redis access throughout the application.

    Returns:
        Async Redis client
    """
    return await _redis_factory.get_client()


async def close_redis_client() -> None:
    """Close the global Redis client connection."""
    await _redis_factory.close()
