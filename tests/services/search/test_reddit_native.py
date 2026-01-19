import pytest
import httpx
import os

# Set mock environment variables for Pydantic Settings
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost:5432/db"
os.environ["UPSTASH_REDIS_URL"] = "https://test.upstash.io"
os.environ["UPSTASH_REDIS_TOKEN"] = "test-token"
os.environ["VERTEX_AI_PROJECT_ID"] = "test-project"
os.environ["GCP_PROJECT_ID"] = "test-project"
os.environ["WEBHOOK_SECRET"] = "test-webhook-secret"

from backend.services.search.reddit_native import RedditNativeScraper

@pytest.mark.asyncio
async def test_reddit_scraper_query_success(respx_mock):
    # Mock Reddit .json response
    mock_response = {
        "data": {
            "children": [
                {
                    "data": {
                        "title": "Reddit Post Title",
                        "permalink": "/r/test/comments/123/",
                        "selftext": "Post content snippet",
                        "subreddit": "test"
                    }
                }
            ]
        }
    }
    respx_mock.get("https://www.reddit.com/search.json").mock(return_value=httpx.Response(200, json=mock_response))
    
    scraper = RedditNativeScraper()
    results = await scraper.query("test query")
    
    assert len(results) == 1
    assert results[0]["title"] == "Reddit Post Title"
    assert "reddit.com/r/test/comments/123/" in results[0]["url"]
    assert results[0]["source"] == "native_reddit"

@pytest.mark.asyncio
async def test_reddit_scraper_error_response(respx_mock):
    respx_mock.get("https://www.reddit.com/search.json").mock(return_value=httpx.Response(429))
    
    scraper = RedditNativeScraper()
    results = await scraper.query("test query")
    
    assert results == []
