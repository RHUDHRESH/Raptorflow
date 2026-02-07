"""Tests for Redis CacheService (canonical)."""

import json

import pytest
import pytest_asyncio

from ...redis.cache import CacheService


@pytest_asyncio.fixture
async def cache_service() -> CacheService:
    return CacheService()


class TestCacheService:
    @pytest.mark.asyncio
    async def test_set_and_get(self, cache_service: CacheService):
        workspace_id = "ws-1"
        key = "user_profile"
        value = {"name": "Test User"}

        cache_service.redis.async_client.set.return_value = True
        cache_service.redis.async_client.get.return_value = json.dumps(value)

        await cache_service.set(workspace_id, key, value, ttl=3600)
        result = await cache_service.get(workspace_id, key)

        assert result == value
        cache_service.redis.async_client.set.assert_called_once()
        cache_service.redis.async_client.get.assert_called_once_with(
            f"cache:{workspace_id}:{key}"
        )

    @pytest.mark.asyncio
    async def test_delete(self, cache_service: CacheService):
        workspace_id = "ws-1"
        key = "user_profile"
        cache_service.redis.async_client.delete.return_value = 1

        result = await cache_service.delete(workspace_id, key)

        assert result is True
        cache_service.redis.async_client.delete.assert_called_once_with(
            f"cache:{workspace_id}:{key}"
        )
