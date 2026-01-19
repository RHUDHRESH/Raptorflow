import pytest
import httpx
import os
import json
from unittest.mock import AsyncMock, MagicMock, patch

# Set mock environment variables for Pydantic Settings
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost:5432/db"
os.environ["UPSTASH_REDIS_URL"] = "https://test.upstash.io"
os.environ["UPSTASH_REDIS_TOKEN"] = "test-token"
os.environ["VERTEX_AI_PROJECT_ID"] = "test-project"
os.environ["GCP_PROJECT_ID"] = "test-project"
os.environ["WEBHOOK_SECRET"] = "test-webhook-secret"

from backend.services.search.orchestrator import SOTASearchOrchestrator

@pytest.mark.asyncio
async def test_orchestrator_aggregation_and_deduplication():
    # Mock engines
    mock_searxng = MagicMock()
    mock_searxng.query = AsyncMock(return_value=[
        {"title": "Duplicate Result", "url": "https://example.com/1", "snippet": "Snippet 1", "source": "native_google"}
    ])
    mock_searxng.close = AsyncMock()
    
    mock_reddit = MagicMock()
    mock_reddit.query = AsyncMock(return_value=[
        {"title": "Duplicate Result", "url": "https://example.com/1", "snippet": "Snippet 1", "source": "native_reddit"},
        {"title": "Unique Reddit", "url": "https://reddit.com/r/test", "snippet": "Snippet 2", "source": "native_reddit"}
    ])
    mock_reddit.close = AsyncMock()
    
    # Mock Redis (Sync methods)
    mock_redis = MagicMock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    
    with patch("backend.services.search.orchestrator.SearXNGClient", return_value=mock_searxng), \
         patch("backend.services.search.orchestrator.RedditNativeScraper", return_value=mock_reddit), \
         patch("backend.services.search.orchestrator.Redis", return_value=mock_redis):
        
        orchestrator = SOTASearchOrchestrator()
        results = await orchestrator.query("test query")
        
        # Should have 2 results (1 deduplicated, 1 unique)
        assert len(results) == 2
        # Check deduplication (url should be unique)
        urls = [r["url"] for r in results]
        assert len(set(urls)) == 2

@pytest.mark.asyncio
async def test_orchestrator_cache_hit():
    # Mock Redis (Sync methods)
    mock_redis = MagicMock()
    cached_data = [{"title": "Cached", "url": "https://cached.com", "snippet": "...", "source": "cache"}]
    mock_redis.get.return_value = json.dumps(cached_data)
    
    with patch("backend.services.search.orchestrator.Redis", return_value=mock_redis):
        orchestrator = SOTASearchOrchestrator()
        # Mock engines to ensure they ARE NOT called on cache hit
        orchestrator.searxng = MagicMock()
        orchestrator.searxng.query = AsyncMock()
        orchestrator.reddit = MagicMock()
        orchestrator.reddit.query = AsyncMock()
        
        results = await orchestrator.query("test query")
        
        assert results[0]["title"] == "Cached"
        orchestrator.searxng.query.assert_not_called()
        orchestrator.reddit.query.assert_not_called()