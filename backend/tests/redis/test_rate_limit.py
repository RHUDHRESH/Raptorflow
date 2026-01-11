"""
Tests for Redis RateLimitService.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio

from ...redis.client import RedisClient
from ...redis.rate_limit import RateLimitResult, RateLimitService


@pytest_asyncio.fixture
async def rate_limit_service(mock_redis: AsyncMock) -> RateLimitService:
    """Rate limit service fixture."""
    return RateLimitService(mock_redis)


class TestRateLimitService:
    """Test cases for RateLimitService."""

    @pytest_asyncio.asyncio.async_test
    async def test_within_limit(self, rate_limit_service: RateLimitService):
        """Test rate limiting when within limits."""
        user_id = "test-user"
        endpoint = "/api/v1/agents/execute"
        limit = 10
        window_seconds = 60

        # Setup mock - no existing requests
        rate_limit_service.redis.eval.return_value = [
            1,
            9,
            int((datetime.utcnow() + timedelta(seconds=60)).timestamp()),
        ]

        # Test
        result = await rate_limit_service.check_limit(
            user_id, endpoint, limit, window_seconds
        )

        # Assertions
        assert result.allowed is True
        assert result.remaining == 9
        assert result.reset_at > datetime.utcnow()

        # Verify Redis call
        rate_limit_service.redis.eval.assert_called_once()
        call_args = rate_limit_service.redis.eval.call_args
        assert call_args[0][0] == rate_limit_service.lua_scripts["RATE_LIMIT_SCRIPT"]
        assert call_args[0][1] == 1  # Number of keys
        assert call_args[0][2][0].startswith("rate:test-user:/api/v1/agents/execute")
        assert call_args[0][3] == [
            limit,
            window_seconds,
            int(datetime.utcnow().timestamp()),
        ]

    @pytest_asyncio.asyncio.async_test
    async def test_exceeded_limit(self, rate_limit_service: RateLimitService):
        """Test rate limiting when limit exceeded."""
        user_id = "test-user"
        endpoint = "/api/v1/agents/execute"
        limit = 5
        window_seconds = 60

        # Setup mock - limit exceeded
        rate_limit_service.redis.eval.return_value = [
            6,
            0,
            int((datetime.utcnow() + timedelta(seconds=60)).timestamp()),
        ]

        # Test
        result = await rate_limit_service.check_limit(
            user_id, endpoint, limit, window_seconds
        )

        # Assertions
        assert result.allowed is False
        assert result.remaining == 0
        assert result.reset_at > datetime.utcnow()

    @pytest_asyncio.asyncio.async_test
    async def test_limit_reset(self, rate_limit_service: RateLimitService):
        """Test rate limit reset after window expires."""
        user_id = "test-user"
        endpoint = "/api/v1/agents/execute"
        limit = 10
        window_seconds = 60

        # Setup mock - new window
        rate_limit_service.redis.eval.return_value = [
            1,
            9,
            int((datetime.utcnow() + timedelta(seconds=60)).timestamp()),
        ]

        # Test first request
        result1 = await rate_limit_service.check_limit(
            user_id, endpoint, limit, window_seconds
        )
        assert result1.allowed is True
        assert result1.remaining == 9

        # Simulate time passing and window reset
        past_time = datetime.utcnow() - timedelta(seconds=61)
        rate_limit_service.redis.eval.return_value = [
            1,
            9,
            int((datetime.utcnow() + timedelta(seconds=60)).timestamp()),
        ]

        # Test after window reset
        result2 = await rate_limit_service.check_limit(
            user_id, endpoint, limit, window_seconds
        )
        assert result2.allowed is True
        assert result2.remaining == 9

    @pytest_asyncio.asyncio.async_test
    async def test_sliding_window(self, rate_limit_service: RateLimitService):
        """Test sliding window rate limiting."""
        user_id = "test-user"
        endpoint = "/api/v1/muse/generate"
        limit = 3
        window_seconds = 30

        # Setup mock for multiple requests
        responses = [
            [
                1,
                2,
                int((datetime.utcnow() + timedelta(seconds=30)).timestamp()),
            ],  # 1st request
            [
                2,
                1,
                int((datetime.utcnow() + timedelta(seconds=30)).timestamp()),
            ],  # 2nd request
            [
                3,
                0,
                int((datetime.utcnow() + timedelta(seconds=30)).timestamp()),
            ],  # 3rd request (limit reached)
            [
                4,
                0,
                int((datetime.utcnow() + timedelta(seconds=30)).timestamp()),
            ],  # 4th request (blocked)
        ]
        rate_limit_service.redis.eval.side_effect = responses

        # Test multiple requests
        results = []
        for i in range(4):
            result = await rate_limit_service.check_limit(
                user_id, endpoint, limit, window_seconds
            )
            results.append(result)

        # Assertions
        assert results[0].allowed is True
        assert results[0].remaining == 2

        assert results[1].allowed is True
        assert results[1].remaining == 1

        assert results[2].allowed is True  # Last allowed request
        assert results[2].remaining == 0

        assert results[3].allowed is False  # Blocked
        assert results[3].remaining == 0

        # Verify Redis was called 4 times
        assert rate_limit_service.redis.eval.call_count == 4

    @pytest_asyncio.asyncio.async_test
    async def test_record_request(self, rate_limit_service: RateLimitService):
        """Test recording a request."""
        user_id = "test-user"
        endpoint = "/api/v1/test"

        # Setup mock
        rate_limit_service.redis.eval.return_value = [
            1,
            9,
            int((datetime.utcnow() + timedelta(seconds=60)).timestamp()),
        ]

        # Test
        await rate_limit_service.record_request(user_id, endpoint)

        # Verify Redis call
        rate_limit_service.redis.eval.assert_called_once()
        call_args = rate_limit_service.redis.eval.call_args
        assert call_args[0][0] == rate_limit_service.lua_scripts["RATE_LIMIT_SCRIPT"]
        assert call_args[0][1] == 1
        assert call_args[0][2][0].startswith(f"rate:{user_id}:{endpoint}")

    @pytest_asyncio.asyncio.async_test
    async def test_different_endpoints(self, rate_limit_service: RateLimitService):
        """Test rate limiting for different endpoints."""
        user_id = "test-user"

        # Setup mock
        rate_limit_service.redis.eval.return_value = [
            1,
            9,
            int((datetime.utcnow() + timedelta(seconds=60)).timestamp()),
        ]

        endpoints = [
            ("/api/v1/agents/execute", 10, 60),
            ("/api/v1/muse/generate", 20, 60),
            ("/api/v1/content/create", 5, 300),
        ]

        # Test each endpoint
        for endpoint, limit, window in endpoints:
            result = await rate_limit_service.check_limit(
                user_id, endpoint, limit, window
            )

            # Assertions
            assert result.allowed is True
            assert result.remaining == limit - 1

            # Verify correct key pattern
            call_args = rate_limit_service.redis.eval.call_args
            assert call_args[0][2][0].startswith(f"rate:{user_id}:{endpoint}")
            assert call_args[0][3][0] == limit
            assert call_args[0][3][1] == window

    @pytest_asyncio.asyncio.async_test
    async def test_different_users(self, rate_limit_service: RateLimitService):
        """Test rate limiting for different users."""
        endpoint = "/api/v1/test"
        limit = 5
        window_seconds = 60

        users = ["user-1", "user-2", "user-3"]

        # Setup mock
        rate_limit_service.redis.eval.return_value = [
            1,
            4,
            int((datetime.utcnow() + timedelta(seconds=60)).timestamp()),
        ]

        # Test each user
        for user_id in users:
            result = await rate_limit_service.check_limit(
                user_id, endpoint, limit, window_seconds
            )

            # Assertions
            assert result.allowed is True
            assert result.remaining == 4

            # Verify correct key pattern
            call_args = rate_limit_service.redis.eval.call_args
            assert call_args[0][2][0].startswith(f"rate:{user_id}:{endpoint}")

    @pytest_asyncio.asyncio.async_test
    async def test_rate_limit_with_zero_limit(
        self, rate_limit_service: RateLimitService
    ):
        """Test rate limiting with zero limit (always blocked)."""
        user_id = "test-user"
        endpoint = "/api/v1/blocked"
        limit = 0
        window_seconds = 60

        # Setup mock
        rate_limit_service.redis.eval.return_value = [
            1,
            0,
            int((datetime.utcnow() + timedelta(seconds=60)).timestamp()),
        ]

        # Test
        result = await rate_limit_service.check_limit(
            user_id, endpoint, limit, window_seconds
        )

        # Assertions
        assert result.allowed is False
        assert result.remaining == 0

    @pytest_asyncio.asyncio.async_test
    async def test_rate_limit_with_large_window(
        self, rate_limit_service: RateLimitService
    ):
        """Test rate limiting with large time window."""
        user_id = "test-user"
        endpoint = "/api/v1/limited"
        limit = 1000
        window_seconds = 86400  # 24 hours

        # Setup mock
        rate_limit_service.redis.eval.return_value = [
            1,
            999,
            int((datetime.utcnow() + timedelta(seconds=86400)).timestamp()),
        ]

        # Test
        result = await rate_limit_service.check_limit(
            user_id, endpoint, limit, window_seconds
        )

        # Assertions
        assert result.allowed is True
        assert result.remaining == 999
        assert result.reset_at > datetime.utcnow() + timedelta(
            seconds=86000
        )  # ~24 hours from now

    @pytest_asyncio.asyncio.async_test
    async def test_concurrent_requests(self, rate_limit_service: RateLimitService):
        """Test concurrent rate limit checks."""
        import asyncio

        user_id = "test-user"
        endpoint = "/api/v1/concurrent"
        limit = 10
        window_seconds = 60

        # Setup mock - allow all requests
        rate_limit_service.redis.eval.return_value = [
            1,
            9,
            int((datetime.utcnow() + timedelta(seconds=60)).timestamp()),
        ]

        # Concurrent requests
        tasks = []
        for i in range(5):
            task = rate_limit_service.check_limit(
                user_id, endpoint, limit, window_seconds
            )
            tasks.append(task)

        # Execute concurrently
        results = await asyncio.gather(*tasks)

        # Assertions
        assert len(results) == 5
        assert all(result.allowed is True for result in results)
        assert all(result.remaining == 9 for result in results)

        # Verify Redis was called 5 times
        assert rate_limit_service.redis.eval.call_count == 5

    @pytest_asyncio.asyncio.async_test
    async def test_rate_limit_error_handling(
        self, rate_limit_service: RateLimitService
    ):
        """Test error handling in rate limiting."""
        user_id = "test-user"
        endpoint = "/api/v1/test"

        # Setup mock to raise exception
        rate_limit_service.redis.eval.side_effect = Exception("Redis error")

        # Test
        with pytest.raises(Exception, match="Redis error"):
            await rate_limit_service.check_limit(user_id, endpoint, 10, 60)

    @pytest_asyncio.asyncio.async_test
    async def test_rate_limit_key_patterns(self, rate_limit_service: RateLimitService):
        """Test rate limit key patterns."""
        test_cases = [
            (
                "user-123",
                "/api/v1/agents/execute",
                "rate:user-123:/api/v1/agents/execute",
            ),
            (
                "user-456",
                "/api/v1/muse/generate",
                "rate:user-456:/api/v1/muse/generate",
            ),
            (
                "user-789",
                "/api/v1/content/create",
                "rate:user-789:/api/v1/content/create",
            ),
        ]

        # Setup mock
        rate_limit_service.redis.eval.return_value = [
            1,
            9,
            int((datetime.utcnow() + timedelta(seconds=60)).timestamp()),
        ]

        for user_id, endpoint, expected_key in test_cases:
            await rate_limit_service.check_limit(user_id, endpoint, 10, 60)

            # Verify correct key pattern
            call_args = rate_limit_service.redis.eval.call_args
            assert call_args[0][2][0] == expected_key

    @pytest_asyncio.asyncio.async_test
    async def test_rate_limit_timestamp_precision(
        self, rate_limit_service: RateLimitService
    ):
        """Test rate limit timestamp precision."""
        user_id = "test-user"
        endpoint = "/api/v1/test"
        limit = 10
        window_seconds = 60

        # Setup mock with specific timestamp
        current_time = datetime.utcnow()
        reset_time = current_time + timedelta(seconds=60)

        rate_limit_service.redis.eval.return_value = [1, 9, int(reset_time.timestamp())]

        # Test
        result = await rate_limit_service.check_limit(
            user_id, endpoint, limit, window_seconds
        )

        # Assertions
        assert result.allowed is True
        assert result.remaining == 9
        assert (
            abs((result.reset_at - reset_time).total_seconds()) < 1
        )  # Within 1 second

    @pytest_asyncio.asyncio.async_test
    async def test_rate_limit_lua_script_execution(
        self, rate_limit_service: RateLimitService
    ):
        """Test that Lua script is executed correctly."""
        user_id = "test-user"
        endpoint = "/api/v1/test"
        limit = 5
        window_seconds = 60

        # Setup mock
        rate_limit_service.redis.eval.return_value = [
            1,
            4,
            int((datetime.utcnow() + timedelta(seconds=60)).timestamp()),
        ]

        # Test
        await rate_limit_service.check_limit(user_id, endpoint, limit, window_seconds)

        # Verify Lua script execution
        call_args = rate_limit_service.redis.eval.call_args
        assert call_args[0][0] == rate_limit_service.lua_scripts["RATE_LIMIT_SCRIPT"]
        assert len(call_args[0]) == 4  # script, num_keys, keys, args
        assert call_args[0][1] == 1  # one key
        assert len(call_args[0][2]) == 1  # one key in keys list
        assert (
            len(call_args[0][3]) == 3
        )  # three arguments (limit, window, current_time)
