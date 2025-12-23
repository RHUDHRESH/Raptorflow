import pytest
from unittest.mock import AsyncMock, patch
from backend.core.governance import RateLimiter, CostGovernor

@pytest.mark.asyncio
async def test_rate_limiter_exceeded():
    """
    Phase 18: Verify that the rate limiter stops requests when limits are hit.
    """
    mock_cache = AsyncMock()
    # Mock cache to return 100 (limit reached)
    mock_cache.get.return_value = "100"
    
    limiter = RateLimiter(cache=mock_cache, limit=100)
    
    with pytest.raises(Exception) as exc:
        await limiter.check_rate_limit("test-tenant", "memory_retrieval")
    
    assert "Rate limit exceeded" in str(exc.value)

@pytest.mark.asyncio
async def test_cost_governor_tracking():
    """
    Phase 18: Verify that the cost governor tracks token usage.
    """
    mock_cache = AsyncMock()
    mock_cache.incrby = AsyncMock()
    
    governor = CostGovernor(cache=mock_cache)
    await governor.log_cost("test-tenant", tokens=1000, model="gemini-1.5-pro")
    
    mock_cache.incrby.assert_called()
    # Check if key contains tenant and cost type
    args, _ = mock_cache.incrby.call_args
    assert "test-tenant" in args[0]
    assert "cost" in args[0]

