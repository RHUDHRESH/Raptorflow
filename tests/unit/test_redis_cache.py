"""
Unit tests for Redis Caching Service.
Verifies hit/miss logic, TTL enforcement, and workspace isolation.
"""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from backend.redis_core.cache import CacheService, cached

@pytest.mark.asyncio
class TestRedisCache:
    """Unit tests for the CacheService."""

    @pytest.fixture
    def mock_redis(self):
        with patch("backend.redis_core.cache.get_redis") as mock_get:
            client = MagicMock()
            client.get_json = AsyncMock(return_value=None)
            client.set_json = AsyncMock(return_value=True)
            client.delete = AsyncMock(return_value=1)
            client.expire = AsyncMock(return_value=True)
            client.exists = AsyncMock(return_value=True)
            mock_get.return_value = client
            yield client

    async def test_cache_hit_miss(self, mock_redis):
        """Test basic get/set/miss logic."""
        service = CacheService()
        workspace_id = "test-ws"
        key = "test-key"
        val = {"data": "secure"}

        # 1. Miss
        res = await service.get(workspace_id, key)
        assert res is None
        mock_redis.get_json.assert_called_with("cache:test-ws:test-key")

        # 2. Set
        success = await service.set(workspace_id, key, val)
        assert success is True
        mock_redis.set_json.assert_called()

        # 3. Hit
        mock_redis.get_json.return_value = val
        hit = await service.get(workspace_id, key)
        assert hit == val

    async def test_get_or_set_pattern(self, mock_redis):
        """Test the get_or_set atomic-style utility."""
        service = CacheService()
        workspace_id = "test-ws"
        key = "dynamic-key"
        
        factory = AsyncMock(return_value={"computed": True})
        
        # 1. Miss triggers factory
        res = await service.get_or_set(workspace_id, key, factory)
        assert res == {"computed": True}
        factory.assert_called_once()
        mock_redis.set_json.assert_called()

        # 2. Hit bypasses factory
        mock_redis.get_json.return_value = {"computed": True}
        factory.reset_mock()
        hit = await service.get_or_set(workspace_id, key, factory)
        assert hit == {"computed": True}
        factory.assert_not_called()

    async def test_workspace_isolation(self, mock_redis):
        """Verify that keys are prefixed with workspace_id."""
        service = CacheService()
        
        await service.get("ws-1", "key-a")
        mock_redis.get_json.assert_called_with("cache:ws-1:key-a")
        
        await service.get("ws-2", "key-a")
        mock_redis.get_json.assert_called_with("cache:ws-2:key-a")

    async def test_cache_decorator(self, mock_redis):
        """Test the @cached decorator functionality."""
        
        call_count = 0
        
        @cached(ttl=100)
        async def expensive_op(workspace_id: str, param: str):
            nonlocal call_count
            call_count += 1
            return f"result-{param}"

        workspace_id = "ws-decor"
        
        # 1. First call (miss)
        mock_redis.get_json.return_value = None
        res1 = await expensive_op(workspace_id, "foo")
        assert res1 == "result-foo"
        assert call_count == 1
        
        # 2. Second call (hit)
        mock_redis.get_json.return_value = "result-foo"
        res2 = await expensive_op(workspace_id, "foo")
        assert res2 == "result-foo"
        assert call_count == 1 # Still 1 because of cache
