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

from backend.services.search.searxng import SearXNGClient

@pytest.mark.asyncio
async def test_searxng_client_query_success(respx_mock):
    # Mock SearXNG response
    mock_response = {
        "results": [
            {"title": "Test Title", "url": "https://example.com", "content": "Test Snippet", "engine": "google"}
        ]
    }
    respx_mock.get("http://localhost:8080/search").mock(return_value=httpx.Response(200, json=mock_response))
    
    client = SearXNGClient(base_url="http://localhost:8080")
    results = await client.query("test query")
    
    assert len(results) == 1
    assert results[0]["title"] == "Test Title"
    assert results[0]["source"] == "native_google"

@pytest.mark.asyncio
async def test_searxng_client_timeout(respx_mock):
    respx_mock.get("http://localhost:8080/search").mock(side_effect=httpx.TimeoutException("Timeout"))
    
    client = SearXNGClient(base_url="http://localhost:8080")
    results = await client.query("test query")
    
    assert results == []

@pytest.mark.asyncio
async def test_searxng_client_error_response(respx_mock):
    respx_mock.get("http://localhost:8080/search").mock(return_value=httpx.Response(500))
    
    client = SearXNGClient(base_url="http://localhost:8080")
    results = await client.query("test query")
    
    assert results == []
