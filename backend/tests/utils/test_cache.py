"""
Comprehensive tests for Redis cache utilities.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from backend.utils.cache import RedisCache


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    redis_mock = AsyncMock()
    redis_mock.ping = AsyncMock(return_value=True)
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.set = AsyncMock(return_value=True)
    redis_mock.delete = AsyncMock(return_value=1)
    redis_mock.exists = AsyncMock(return_value=0)
    redis_mock.close = AsyncMock()
    return redis_mock


@pytest.fixture
def redis_cache():
    """Create RedisCache instance for testing."""
    return RedisCache(redis_url="redis://localhost:6379/0")


@pytest.mark.asyncio
class TestRedisCache:
    """Test RedisCache functionality."""

    async def test_connect_success(self, redis_cache, mock_redis):
        """Test successful Redis connection."""
        with patch('backend.utils.cache.aioredis.from_url', return_value=mock_redis):
            await redis_cache.connect()

            assert redis_cache.client is not None
            mock_redis.ping.assert_called_once()

    async def test_connect_failure(self, redis_cache):
        """Test Redis connection failure."""
        with patch('backend.utils.cache.aioredis.from_url',
                   side_effect=Exception("Connection failed")):

            await redis_cache.connect()
            assert redis_cache.client is None

    async def test_disconnect(self, redis_cache, mock_redis):
        """Test Redis disconnection."""
        redis_cache.client = mock_redis

        await redis_cache.disconnect()

        mock_redis.close.assert_called_once()
        assert redis_cache.client is None

    async def test_ping_success(self, redis_cache, mock_redis):
        """Test Redis ping with active connection."""
        redis_cache.client = mock_redis

        result = await redis_cache.ping()

        assert result is True
        mock_redis.ping.assert_called_once()

    async def test_ping_no_client(self, redis_cache):
        """Test ping without active connection."""
        result = await redis_cache.ping()
        assert result is False

    async def test_ping_failure(self, redis_cache, mock_redis):
        """Test ping with connection error."""
        redis_cache.client = mock_redis
        mock_redis.ping.side_effect = Exception("Ping failed")

        result = await redis_cache.ping()
        assert result is False

    async def test_get_success(self, redis_cache, mock_redis):
        """Test successful cache get."""
        redis_cache.client = mock_redis
        mock_redis.get.return_value = b'{"data": "test"}'

        result = await redis_cache.get("test_key")

        assert result == {"data": "test"}
        mock_redis.get.assert_called_once_with("test_key")

    async def test_get_not_found(self, redis_cache, mock_redis):
        """Test cache get with missing key."""
        redis_cache.client = mock_redis
        mock_redis.get.return_value = None

        result = await redis_cache.get("missing_key")

        assert result is None

    async def test_get_no_client(self, redis_cache):
        """Test get without active connection."""
        result = await redis_cache.get("test_key")
        assert result is None

    async def test_set_success(self, redis_cache, mock_redis):
        """Test successful cache set."""
        redis_cache.client = mock_redis

        result = await redis_cache.set("test_key", {"data": "test"}, ttl=3600)

        assert result is True
        mock_redis.set.assert_called_once()

    async def test_set_with_default_ttl(self, redis_cache, mock_redis):
        """Test cache set with default TTL."""
        redis_cache.client = mock_redis

        await redis_cache.set("test_key", {"data": "test"})

        mock_redis.set.assert_called_once()

    async def test_set_no_client(self, redis_cache):
        """Test set without active connection."""
        result = await redis_cache.set("test_key", {"data": "test"})
        assert result is False

    async def test_delete_success(self, redis_cache, mock_redis):
        """Test successful cache delete."""
        redis_cache.client = mock_redis
        mock_redis.delete.return_value = 1

        result = await redis_cache.delete("test_key")

        assert result is True
        mock_redis.delete.assert_called_once_with("test_key")

    async def test_delete_not_found(self, redis_cache, mock_redis):
        """Test delete of non-existent key."""
        redis_cache.client = mock_redis
        mock_redis.delete.return_value = 0

        result = await redis_cache.delete("missing_key")

        assert result is False

    async def test_delete_no_client(self, redis_cache):
        """Test delete without active connection."""
        result = await redis_cache.delete("test_key")
        assert result is False

    async def test_exists_true(self, redis_cache, mock_redis):
        """Test checking existence of existing key."""
        redis_cache.client = mock_redis
        mock_redis.exists.return_value = 1

        result = await redis_cache.exists("test_key")

        assert result is True
        mock_redis.exists.assert_called_once_with("test_key")

    async def test_exists_false(self, redis_cache, mock_redis):
        """Test checking existence of missing key."""
        redis_cache.client = mock_redis
        mock_redis.exists.return_value = 0

        result = await redis_cache.exists("missing_key")

        assert result is False

    async def test_exists_no_client(self, redis_cache):
        """Test exists without active connection."""
        result = await redis_cache.exists("test_key")
        assert result is False

    async def test_clear_pattern_success(self, redis_cache, mock_redis):
        """Test clearing keys matching pattern."""
        redis_cache.client = mock_redis
        mock_redis.scan_iter = AsyncMock(return_value=AsyncIterator([b"key1", b"key2"]))

        result = await redis_cache.clear_pattern("test:*")

        assert result > 0

    async def test_clear_pattern_no_client(self, redis_cache):
        """Test clear pattern without active connection."""
        result = await redis_cache.clear_pattern("test:*")
        assert result == 0


class AsyncIterator:
    """Helper class for async iteration in tests."""

    def __init__(self, items):
        self.items = items
        self.index = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.index >= len(self.items):
            raise StopAsyncIteration
        item = self.items[self.index]
        self.index += 1
        return item
