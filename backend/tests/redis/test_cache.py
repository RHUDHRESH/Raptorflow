"""
Tests for Redis CacheService.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio

from ...redis.cache import CacheService
from ...redis.client import RedisClient


@pytest_asyncio.fixture
async def cache_service(mock_redis: AsyncMock) -> CacheService:
    """Cache service fixture."""
    return CacheService(mock_redis)


class TestCacheService:
    """Test cases for CacheService."""

    @pytest_asyncio.asyncio.async_test
    async def test_set_and_get_cache(
        self, cache_service: CacheService, test_cache_data: dict
    ):
        """Test setting and getting cache values."""
        workspace_id = "test-workspace"
        key = "user_profile"
        value = test_cache_data["user_profile"]

        # Setup mock
        cache_service.redis.set.return_value = True
        cache_service.redis.get.return_value = '{"name": "Test User", "email": "test@example.com", "preferences": {"theme": "dark"}}'

        # Test set
        await cache_service.set(workspace_id, key, value, ttl=3600)

        # Verify Redis call
        cache_service.redis.set.assert_called_once()
        call_args = cache_service.redis.set.call_args
        assert call_args[0][0] == f"cache:{workspace_id}:{key}"
        assert "Test User" in call_args[0][1]
        assert call_args[1]["ex"] == 3600

        # Test get
        result = await cache_service.get(workspace_id, key)

        # Assertions
        assert result is not None
        assert result["name"] == "Test User"
        assert result["email"] == "test@example.com"
        assert result["preferences"]["theme"] == "dark"

        # Verify Redis call
        cache_service.redis.get.assert_called_once_with(f"cache:{workspace_id}:{key}")

    @pytest_asyncio.asyncio.async_test
    async def test_get_nonexistent_cache(self, cache_service: CacheService):
        """Test getting non-existent cache key."""
        # Setup mock
        cache_service.redis.get.return_value = None

        # Test
        result = await cache_service.get("test-workspace", "nonexistent_key")

        # Assertions
        assert result is None

        # Verify Redis call
        cache_service.redis.get.assert_called_once_with(
            "cache:test-workspace:nonexistent_key"
        )

    @pytest_asyncio.async_test
    async def test_delete_cache(self, cache_service: CacheService):
        """Test deleting cache key."""
        workspace_id = "test-workspace"
        key = "user_profile"

        # Setup mock
        cache_service.redis.delete.return_value = 1

        # Test
        result = await cache_service.delete(workspace_id, key)

        # Assertions
        assert result is True

        # Verify Redis call
        cache_service.redis.delete.assert_called_once_with(
            f"cache:{workspace_id}:{key}"
        )

    @pytest_asyncio.asyncio.async_test
    async def test_delete_nonexistent_cache(self, cache_service: CacheService):
        """Test deleting non-existent cache key."""
        # Setup mock
        cache_service.redis.delete.return_value = 0

        # Test
        result = await cache_service.delete("test-workspace", "nonexistent_key")

        # Assertions
        assert result is False

    @pytest_asyncio.asyncio.async_test
    async def test_clear_workspace_cache(self, cache_service: CacheService):
        """Test clearing all cache for a workspace."""
        workspace_id = "test-workspace"

        # Setup mock
        cache_service.redis.keys.return_value = [
            f"cache:{workspace_id}:key1",
            f"cache:{workspace_id}:key2",
            f"cache:{workspace_id}:key3",
        ]
        cache_service.redis.delete.return_value = 3

        # Test
        result = await cache_service.clear_workspace(workspace_id)

        # Assertions
        assert result is True

        # Verify Redis calls
        cache_service.redis.keys.assert_called_once_with(f"cache:{workspace_id}:*")
        cache_service.redis.delete.assert_called_once()

        # Verify correct keys were deleted
        delete_args = cache_service.redis.delete.call_args[0][0]
        assert len(delete_args) == 3
        assert all(key.startswith(f"cache:{workspace_id}:") for key in delete_args)

    @pytest_asyncio.async_test
    async def test_get_or_set_cache_miss(self, cache_service: CacheService):
        """Test get_or_set when cache miss occurs."""
        workspace_id = "test-workspace"
        key = "computed_data"
        computed_value = {
            "result": "computed",
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Setup mock for cache miss
        cache_service.redis.get.return_value = None
        cache_service.redis.set.return_value = True

        # Factory function
        async def factory():
            return computed_value

        # Test
        result = await cache_service.get_or_set(workspace_id, key, factory, ttl=1800)

        # Assertions
        assert result == computed_value

        # Verify Redis calls
        cache_service.redis.get.assert_called_once_with(f"cache:{workspace_id}:{key}")
        cache_service.redis.set.assert_called_once()

        # Verify set call arguments
        set_args = cache_service.redis.set.call_args
        assert set_args[0][0] == f"cache:{workspace_id}:{key}"
        assert set_args[1]["ex"] == 1800

    @pytest_asyncio.asyncio.async_test
    async def test_get_or_set_cache_hit(self, cache_service: CacheService):
        """Test get_or_set when cache hit occurs."""
        workspace_id = "test-workspace"
        key = "cached_data"
        cached_value = {"result": "cached", "version": 1}

        # Setup mock for cache hit
        cache_service.redis.get.return_value = '{"result": "cached", "version": 1}'

        # Factory function (should not be called)
        factory_called = False

        async def factory():
            nonlocal factory_called
            factory_called = True
            return {"result": "should_not_be_called"}

        # Test
        result = await cache_service.get_or_set(workspace_id, key, factory, ttl=1800)

        # Assertions
        assert result == cached_value
        assert not factory_called  # Factory should not be called

        # Verify Redis calls
        cache_service.redis.get.assert_called_once_with(f"cache:{workspace_id}:{key}")
        cache_service.redis.set.assert_not_called()

    @pytest_asyncio.async_test
    async def test_cache_expiry(self, cache_service: CacheService):
        """Test cache expiry behavior."""
        workspace_id = "test-workspace"
        key = "expiring_data"
        value = {"data": "will_expire"}

        # Setup mock
        cache_service.redis.set.return_value = True
        cache_service.redis.get.return_value = None  # Expired

        # Test set with short TTL
        await cache_service.set(workspace_id, key, value, ttl=1)

        # Verify set call
        set_args = cache_service.redis.set.call_args
        assert set_args[1]["ex"] == 1

        # Test get after expiry
        result = await cache_service.get(workspace_id, key)

        # Assertions
        assert result is None

    @pytest_asyncio.asyncio.async_test
    async def test_cache_with_complex_data(self, cache_service: CacheService):
        """Test caching complex data structures."""
        workspace_id = "test-workspace"
        key = "complex_data"
        complex_data = {
            "users": [
                {"id": 1, "name": "Alice", "roles": ["admin", "user"]},
                {"id": 2, "name": "Bob", "roles": ["user"]},
            ],
            "settings": {
                "theme": "dark",
                "notifications": {"email": True, "push": False},
                "features": {"beta": True, "experimental": False},
            },
            "metadata": {
                "created_at": datetime.utcnow().isoformat(),
                "version": 2,
                "tags": ["production", "v2"],
            },
        }

        # Setup mock
        cache_service.redis.set.return_value = True
        cache_service.redis.get.return_value = '{"users": [{"id": 1, "name": "Alice", "roles": ["admin", "user"]}, {"id": 2, "name": "Bob", "roles": ["user"]}], "settings": {"theme": "dark", "notifications": {"email": true, "push": false}, "features": {"beta": true, "experimental": false}}, "metadata": {"created_at": "2024-01-01T00:00:00", "version": 2, "tags": ["production", "v2"]}}'

        # Test set
        await cache_service.set(workspace_id, key, complex_data)

        # Test get
        result = await cache_service.get(workspace_id, key)

        # Assertions
        assert result is not None
        assert len(result["users"]) == 2
        assert result["users"][0]["name"] == "Alice"
        assert "admin" in result["users"][0]["roles"]
        assert result["settings"]["theme"] == "dark"
        assert result["settings"]["notifications"]["email"] is True
        assert result["metadata"]["version"] == 2
        assert "production" in result["metadata"]["tags"]

    @pytest_asyncio.asyncio.async_test
    async def test_cache_with_none_values(self, cache_service: CacheService):
        """Test caching None values."""
        workspace_id = "test-workspace"
        key = "null_value"

        # Setup mock
        cache_service.redis.set.return_value = True
        cache_service.redis.get.return_value = "null"

        # Test set None
        await cache_service.set(workspace_id, key, None)

        # Test get None
        result = await cache_service.get(workspace_id, key)

        # Assertions
        assert result is None

        # Verify Redis calls
        cache_service.redis.set.assert_called_once_with(
            f"cache:{workspace_id}:key", "null", ex=3600
        )
        cache_service.redis.get.assert_called_once_with(f"cache:{workspace_id}:key")

    @pytest_asyncio.asyncio.async_test
    async def test_cache_error_handling(self, cache_service: CacheService):
        """Test error handling in cache operations."""
        # Setup mock to raise exception
        cache_service.redis.get.side_effect = Exception("Redis connection error")

        # Test
        with pytest.raises(Exception, match="Redis connection error"):
            await cache_service.get("test-workspace", "test_key")

    @pytest_asyncio.asyncio.async_test
    async def test_concurrent_cache_operations(self, cache_service: CacheService):
        """Test concurrent cache operations."""
        import asyncio

        # Setup mock
        cache_service.redis.set.return_value = True
        cache_service.redis.get.return_value = None

        # Concurrent cache sets
        tasks = []
        for i in range(10):
            task = cache_service.set("test-workspace", f"key_{i}", {"value": i})
            tasks.append(task)

        # Execute concurrently
        await asyncio.gather(*tasks)

        # Assertions
        assert cache_service.redis.set.call_count == 10

        # Verify all keys were set correctly
        for i in range(10):
            cache_service.redis.set.assert_any_call(
                f"cache:test-workspace:key_{i}", '{"value": ' + str(i) + "}", ex=3600
            )

    @pytest_asyncio.asyncio.async_test
    async def test_cache_key_patterns(self, cache_service: CacheService):
        """Test cache key patterns."""
        workspace_id = "workspace-123"

        # Test various key formats
        test_cases = [
            ("user_profile", "cache:workspace-123:user_profile"),
            ("settings:theme", "cache:workspace-123:settings:theme"),
            ("data:analytics:daily", "cache:workspace-123:data:analytics:daily"),
            (
                "complex_key_with_underscores_and-numbers123",
                "cache:workspace-123:complex_key_with_underscores_and-numbers123",
            ),
        ]

        # Setup mock
        cache_service.redis.set.return_value = True

        for key, expected_redis_key in test_cases:
            await cache_service.set(workspace_id, key, {"test": "data"})

            # Verify correct key pattern
            cache_service.redis.set.assert_any_call(
                expected_redis_key, '{"test": "data"}', ex=3600
            )

    @pytest_asyncio.asyncio.async_test
    async def test_cache_factory_exception(self, cache_service: CacheService):
        """Test get_or_set when factory function raises exception."""
        workspace_id = "test-workspace"
        key = "error_key"

        # Setup mock for cache miss
        cache_service.redis.get.return_value = None

        # Factory function that raises exception
        async def failing_factory():
            raise ValueError("Factory function failed")

        # Test
        with pytest.raises(ValueError, match="Factory function failed"):
            await cache_service.get_or_set(workspace_id, key, failing_factory)

        # Verify Redis was not called for set
        cache_service.redis.set.assert_not_called()
