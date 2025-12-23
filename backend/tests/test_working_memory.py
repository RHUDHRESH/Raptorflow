import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.services.cache import get_cache

@pytest.mark.asyncio
async def test_working_memory_caching_flow():
    """Verify that agent working memory can be stored and retrieved from the cache."""
    # Mock the Redis client
    mock_redis = AsyncMock()
    mock_redis.set = AsyncMock(return_value=True)
    mock_redis.get = AsyncMock(return_value='{"thought": "Need to research ICP segments", "certainty": 0.9}')
    
    with patch("backend.services.cache.RaptorCache.client", new_callable=PropertyMock) as mock_client_prop:
        mock_client_prop.return_value = mock_redis
        
        cache = get_cache()
        
        # Test Set
        await cache.set("working_thought:thread_1", '{"thought": "test"}', ex=60)
        mock_redis.set.assert_called_once()
        
        # Test Get
        res = await cache.get("working_thought:thread_1")
        assert "ICP segments" in res
        mock_redis.get.assert_called_once_with("working_thought:thread_1")

from unittest.mock import PropertyMock
