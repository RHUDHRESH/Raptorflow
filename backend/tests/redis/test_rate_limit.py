"""
Tests for Redis RateLimitService (canonical).
"""

import pytest
import pytest_asyncio

from ...redis.rate_limit import RateLimitConfig, RateLimitService


@pytest_asyncio.fixture
async def rate_limit_service() -> RateLimitService:
    """Rate limit service fixture."""
    return RateLimitService()


class TestRateLimitService:
    @pytest.mark.asyncio
    async def test_within_limit(self, rate_limit_service: RateLimitService):
        redis = rate_limit_service.redis.async_client
        redis.exists.return_value = 0
        redis.zremrangebyscore.return_value = 0
        redis.zcard.return_value = 0
        redis.zadd.return_value = 1
        redis.expire.return_value = True
        redis.get.return_value = None
        redis.set.return_value = True

        result = await rate_limit_service.check_rate_limit(
            "user-123", RateLimitConfig(requests_per_minute=10)
        )

        assert result["allowed"] is True
        assert result["blocked"] is False
        assert result["remaining"] >= 0

    @pytest.mark.asyncio
    async def test_blocked_user(self, rate_limit_service: RateLimitService):
        redis = rate_limit_service.redis.async_client
        redis.exists.return_value = 1

        result = await rate_limit_service.check_rate_limit("user-123")

        assert result["allowed"] is False
        assert result["blocked"] is True
