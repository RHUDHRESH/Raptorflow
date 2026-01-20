"""
Economy & Billing Audit for Redis Caching.
Verifies that redundant workflows trigger ZERO external API calls.
"""

import os
import pytest
import uuid
import hashlib
from unittest.mock import MagicMock, AsyncMock, patch

# Mock environment variables
os.environ["SECRET_KEY"] = "test"
os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost:5432/db"
os.environ["GCP_PROJECT_ID"] = "test"
os.environ["WEBHOOK_SECRET"] = "test"
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_ANON_KEY"] = "test"
os.environ["UPSTASH_REDIS_URL"] = "https://test.upstash.io"
os.environ["UPSTASH_REDIS_TOKEN"] = "test"

@pytest.mark.asyncio
class TestEconomyAudit:
    """Audit suite for cost reduction verification."""

    @pytest.fixture
    def mock_redis(self):
        with patch("backend.redis_core.client.get_redis") as mock_get_client, \
             patch("backend.redis_core.cache.get_redis") as mock_get_cache:
            
            client = MagicMock()
            cache_store = {}
            
            async def get_json(k): return cache_store.get(k)
            async def set_json(k, v, **kw): cache_store[k] = v; return True
            async def delete(*keys): 
                for k in keys: cache_store.pop(k, None)
                return 1
            async def smembers(key): return []
            async def get(k):
                val = cache_store.get(k)
                return val.encode() if isinstance(val, str) else val
            async def set(k, v, **kw):
                cache_store[k] = v
                return True
                
            client.get_json = AsyncMock(side_effect=get_json)
            client.set_json = AsyncMock(side_effect=set_json)
            client.delete = AsyncMock(side_effect=delete)
            client.get = AsyncMock(side_effect=get)
            client.set = AsyncMock(side_effect=set)
            client.async_client.smembers = AsyncMock(side_effect=smembers)
            client.async_client.sadd = AsyncMock(return_value=1)
            client.async_client.expire = AsyncMock(return_value=True)
            
            mock_get_client.return_value = client
            mock_get_cache.return_value = client
            yield client

    async def test_titan_search_economy(self, mock_redis):
        """Verify that multiplexed search is only executed once."""
        from backend.services.titan.multiplexer import SearchMultiplexer
        
        multiplexer = SearchMultiplexer()
        query = "market research query"
        
        # 1. First Call: Should call search_orchestrator
        with patch.object(multiplexer.search_orchestrator, "query", new_callable=AsyncMock) as mock_query:
            mock_query.return_value = [{"url": "https://test.com"}]
            with patch.object(multiplexer, "generate_variations", AsyncMock(return_value=["v1"])):
                res1 = await multiplexer.execute_multiplexed(query)
                assert len(res1) == 1
                mock_query.assert_called_once()
                
                # 2. Second Call: Should NOT call search_orchestrator
                mock_query.reset_mock()
                res2 = await multiplexer.execute_multiplexed(query)
                assert res2 == res1
                mock_query.assert_not_called()
                print("\nTitan Economy: Redundant search intercepted by cache.")

    async def test_llm_inference_economy(self, mock_redis):
        """Verify that redundant LLM prompts trigger zero SDK calls."""
        from backend.services.vertex_ai_client import VertexAIClient
        client = VertexAIClient()
        prompt = "Strategic vision for 2026"
        
        # Mock SDK generate_content
        with patch.object(client.client.models, "generate_content") as mock_gen:
            mock_resp = MagicMock()
            mock_resp.text = "The vision is clear."
            mock_gen.return_value = mock_resp
            
            # Ensure cache is clear for this prompt
            cache_key = f"ai_res:{hashlib.md5(client._sanitize_input(prompt).encode()).hexdigest()}"
            await mock_redis.delete(cache_key)
            
            # 1. First Call
            await client.generate_text(prompt)
            mock_gen.assert_called_once()
            
            # 2. Second Call
            mock_gen.reset_mock()
            await client.generate_text(prompt)
            mock_gen.assert_not_called()
            print("LLM Economy: Redundant inference intercepted by cache.")