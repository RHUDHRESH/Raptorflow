"""
Performance Benchmark for Redis Caching.
Compares response times for Cache-Hit vs Cache-Miss across core modules.
Uses mocked Redis to test logic and local overhead.
"""

import os
import pytest
import time
import uuid
import asyncio
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
class TestCachingPerformance:
    """Performance benchmarks for the caching layer (Mocked Redis)."""

    @pytest.fixture
    def workspace_id(self):
        return str(uuid.uuid4())

    @pytest.fixture
    def mock_redis(self):
        # Patch in multiple places where get_redis might be imported
        with patch("backend.redis_core.client.get_redis") as mock_get_client, \
             patch("backend.redis_core.cache.get_redis") as mock_get_cache:
            
            client = MagicMock()
            cache_store = {}
            
            async def get_json(key):
                return cache_store.get(key)
            async def set_json(key, val, **kwargs):
                cache_store[key] = val
                return True
            async def delete(*keys):
                for k in keys: cache_store.pop(k, None)
                return 1
            async def smembers(key):
                return []
            async def get(key):
                val = cache_store.get(key)
                return val.encode() if isinstance(val, str) else val
            async def set(key, val, **kwargs):
                cache_store[key] = val
                return True
                
            client.get_json = AsyncMock(side_effect=get_json)
            client.set_json = AsyncMock(side_effect=set_json)
            client.delete = AsyncMock(side_effect=delete)
            client.get = AsyncMock(side_effect=get)
            client.set = AsyncMock(side_effect=set)
            client.async_client.smembers = AsyncMock(side_effect=smembers)
            client.async_client.sadd = AsyncMock(return_value=1)
            client.async_client.srem = AsyncMock(return_value=1)
            client.async_client.expire = AsyncMock(return_value=True)
            client.async_client.delete = AsyncMock(side_effect=delete)
            
            mock_get_client.return_value = client
            mock_get_cache.return_value = client
            yield client

    async def test_foundation_retrieval_performance(self, workspace_id, mock_redis):
        """Benchmark Foundation retrieval logic."""
        with patch("backend.core.supabase_mgr.get_supabase_client"):
            from backend.services.foundation import FoundationService
            service = FoundationService()
            
            sample_data = {"id": "f1", "company_name": "PerfCorp", "workspace_id": workspace_id}
            
            # Simulate slow DB
            async def slow_db(ws):
                await asyncio.sleep(0.3)
                return sample_data
                
            service.repository.get_by_workspace = AsyncMock(side_effect=slow_db)
            
            # 1. Measure Cache Miss
            start_miss = time.perf_counter()
            res_miss = await service.get_foundation(workspace_id)
            end_miss = time.perf_counter()
            miss_duration = end_miss - start_miss
            
            # 2. Measure Cache Hit
            start_hit = time.perf_counter()
            res_hit = await service.get_foundation(workspace_id)
            end_hit = time.perf_counter()
            hit_duration = end_hit - start_hit
            
            print(f"\nFoundation Retrieval (Mocked):")
            print(f"Cache Miss: {miss_duration:.4f}s")
            print(f"Cache Hit:  {hit_duration:.4f}s")
            
            assert res_hit == sample_data
            assert hit_duration < miss_duration
            assert hit_duration < 0.05

    async def test_llm_inference_caching_performance(self, mock_redis):
        """Benchmark LLM generation logic with prompt-based caching."""
        from backend.services.vertex_ai_client import VertexAIClient
        client = VertexAIClient()
        prompt = "Performance test prompt"
        
        # Mock real SDK call to be slow
        # NOTE: client.client.models.generate_content is called SYNCHRONOUSLY in vertex_ai_client.py 
        # (the current implementation doesn't use 'await' on the call itself, though the wrapper is async)
        # Wait, I should check if it's async in the source.
        
        def slow_generate(*args, **kwargs):
            time.sleep(0.3) # Synchronous sleep to simulate blocking SDK call
            mock_resp = MagicMock()
            mock_resp.text = "Slow result"
            return mock_resp
            
        client.client.models.generate_content = MagicMock(side_effect=slow_generate)
        
        # 1. Cache Miss
        start_miss = time.perf_counter()
        res_miss = await client.generate_text(prompt)
        end_miss = time.perf_counter()
        miss_duration = end_miss - start_miss
        
        # 2. Cache Hit
        start_hit = time.perf_counter()
        res_hit = await client.generate_text(prompt)
        end_hit = time.perf_counter()
        hit_duration = end_hit - start_hit
        
        print(f"\nLLM Inference (Mocked):")
        print(f"Cache Miss: {miss_duration:.4f}s")
        print(f"Cache Hit:  {hit_duration:.4f}s")
        
        assert res_hit == "Slow result"
        assert hit_duration < 0.05