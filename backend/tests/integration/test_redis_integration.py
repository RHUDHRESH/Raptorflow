"""
Redis Integration Tests
Comprehensive tests for Redis services and functionality
"""

import asyncio
import pytest
import time
from datetime import datetime

from redis_core.session import SessionService
from redis_core.rate_limit import RateLimitService
from redis_core.client import get_redis
from backend.services.llm_cache import get_semantic_cache
from backend.services.coordination import get_lock_manager


class TestRedisIntegration:
    """Integration tests for Redis services"""
    
    @pytest.mark.asyncio
    async def test_session_management(self):
        """Test session creation, retrieval, and deletion"""
        session_service = SessionService()
        
        # Test session creation
        session = await session_service.create_session("user123", "workspace456")
        assert session is not None
        assert session.user_id == "user123"
        assert session.workspace_id == "workspace456"
        
        # Test session retrieval
        retrieved = await session_service.get_session(session.id)
        assert retrieved is not None
        assert retrieved.user_id == "user123"
        assert retrieved.workspace_id == "workspace456"
        
        # Test session update
        await session_service.update_session(session.id, {"last_activity": datetime.now()})
        updated = await session_service.get_session(session.id)
        assert updated is not None
        
        # Test session deletion
        deleted = await session_service.delete_session(session.id)
        assert deleted is True
        
        # Verify deletion
        deleted_session = await session_service.get_session(session.id)
        assert deleted_session is None
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test rate limiting functionality"""
        rate_limiter = RateLimitService()
        
        # Test rate limiting within limits
        for i in range(50):  # Under typical limit of 100
            allowed = await rate_limiter.check_limit("user123", "api")
            assert allowed is True, f"Request {i} should be allowed"
        
        # Test rate limiting exceeding limits
        exceeded_count = 0
        for i in range(150):  # Exceed limit of 100
            allowed = await rate_limiter.check_limit("user123", "api")
            if not allowed:
                exceeded_count += 1
        
        assert exceeded_count > 0, "Some requests should be rate limited"
        
        # Test different endpoints have separate limits
        for i in range(50):
            auth_allowed = await rate_limiter.check_limit("user123", "auth")
            assert auth_allowed is True, "Auth endpoint should have separate limits"
    
    @pytest.mark.asyncio
    async def test_semantic_cache(self):
        """Test semantic caching functionality"""
        cache = get_semantic_cache()
        
        # Test caching a response
        query1 = "What are the best marketing strategies for SaaS companies?"
        response1 = {
            "answer": "Content marketing, SEO, and paid advertising are effective strategies...",
            "confidence": 0.95,
            "sources": ["marketing_blog", "industry_report"]
        }
        
        cached = await cache.cache_response(query1, response1)
        assert cached is True
        
        # Test exact cache hit
        cached_response = await cache.get_cached_response(query1)
        assert cached_response is not None
        assert cached_response['response'] == response1
        
        # Test semantic cache hit (similar query)
        query2 = "What marketing strategies work well for SaaS businesses?"
        semantic_response = await cache.get_cached_response(query2)
        assert semantic_response is not None
        assert semantic_response['response'] == response1
        assert semantic_response.get('similarity_score') > 0.8
        
        # Test cache miss
        query3 = "How to cook pasta?"
        miss_response = await cache.get_cached_response(query3)
        assert miss_response is None
        
        # Test cache statistics
        stats = await cache.get_cache_stats()
        assert stats['total_entries'] >= 1
        assert stats['total_hits'] >= 2  # Exact + semantic hit
        assert 'error' not in stats
    
    @pytest.mark.asyncio
    async def test_distributed_locks(self):
        """Test distributed locking functionality"""
        lock_manager = get_lock_manager()
        
        # Test basic lock acquisition and release
        lock = await lock_manager.create_lock("test_resource", timeout=10)
        
        acquired = await lock.acquire()
        assert acquired is True
        assert await lock.is_locked() is True
        
        # Test lock info
        lock_info = await lock.get_lock_info()
        assert lock_info is not None
        assert lock_info['is_mine'] is True
        assert lock_info['ttl_seconds'] > 0
        
        # Test lock extension
        extended = await lock.extend(20)
        assert extended is True
        
        # Test lock release
        released = await lock.release()
        assert released is True
        assert await lock.is_locked() is False
        
        # Test context manager
        async with await lock_manager.create_lock("context_test", timeout=5) as ctx_lock:
            assert await ctx_lock.is_locked() is True
            # Simulate some work
            await asyncio.sleep(0.1)
        
        # Lock should be released after context
        lock_info_after = await ctx_lock.get_lock_info()
        assert lock_info_after is None
    
    @pytest.mark.asyncio
    async def test_redis_basic_operations(self):
        """Test basic Redis operations"""
        redis = get_redis()
        
        # Test string operations
        await redis.set("test_key", "test_value", ex=60)
        value = await redis.get("test_key")
        assert value == "test_value"
        
        # Test JSON operations
        test_data = {"name": "test", "value": 123, "active": True}
        await redis.set_json("test_json", test_data)
        retrieved_data = await redis.get_json("test_json")
        assert retrieved_data == test_data
        
        # Test hash operations
        await redis.hset("test_hash", "field1", "value1")
        await redis.hset("test_hash", "field2", "value2")
        hash_value = await redis.hget("test_hash", "field1")
        assert hash_value == "value1"
        
        all_hash = await redis.hgetall("test_hash")
        assert all_hash["field1"] == "value1"
        assert all_hash["field2"] == "value2"
        
        # Test list operations
        await redis.lpush("test_list", "item1", "item2", "item3")
        list_length = await redis.llen("test_list")
        assert list_length == 3
        
        # Cleanup
        await redis.delete("test_key", "test_json", "test_hash", "test_list")
    
    @pytest.mark.asyncio
    async def test_redis_health_and_connectivity(self):
        """Test Redis health checks and connectivity"""
        redis = get_redis()
        
        # Test ping
        ping_result = await redis.ping()
        assert ping_result is True
        
        # Test health check endpoint would work
        # (This would be tested via HTTP in actual integration tests)
        
        # Test error handling
        try:
            await redis.get("nonexistent_key")
            # Should not raise error, just return None
        except Exception:
            pytest.fail("Getting nonexistent key should not raise error")
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self):
        """Test Redis operations under concurrent load"""
        redis = get_redis()
        
        async def worker(worker_id: int):
            """Worker function for concurrent testing"""
            results = []
            for i in range(10):
                key = f"worker_{worker_id}_item_{i}"
                value = f"worker_{worker_id}_value_{i}"
                
                await redis.set(key, value, ex=60)
                retrieved = await redis.get(key)
                results.append(retrieved == value)
            
            return all(results)
        
        # Run multiple workers concurrently
        tasks = [worker(i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        
        # All workers should complete successfully
        assert all(results), "All concurrent operations should succeed"
        
        # Cleanup
        keys_to_delete = []
        for i in range(5):
            for j in range(10):
                keys_to_delete.append(f"worker_{i}_item_{j}")
        
        if keys_to_delete:
            await redis.delete(*keys_to_delete)
    
    @pytest.mark.asyncio
    async def test_cache_performance(self):
        """Test cache performance under load"""
        cache = get_semantic_cache()
        
        # Cache some test data
        queries = [
            f"Test query {i} with some additional context"
            for i in range(100)
        ]
        
        responses = [
            {"answer": f"Response {i}", "confidence": 0.9}
            for i in range(100)
        ]
        
        # Cache all responses
        start_time = time.time()
        for query, response in zip(queries, responses):
            await cache.cache_response(query, response)
        cache_time = time.time() - start_time
        
        # Test cache retrieval performance
        start_time = time.time()
        hits = 0
        for query in queries:
            result = await cache.get_cached_response(query)
            if result:
                hits += 1
        retrieve_time = time.time() - start_time
        
        # Performance assertions
        assert cache_time < 10.0, f"Caching took too long: {cache_time}s"
        assert retrieve_time < 5.0, f"Retrieval took too long: {retrieve_time}s"
        assert hits == 100, f"Expected 100 cache hits, got {hits}"
        
        # Check cache stats
        stats = await cache.get_cache_stats()
        assert stats['total_entries'] == 100


# Performance test class
class TestRedisPerformance:
    """Performance tests for Redis under load"""
    
    @pytest.mark.asyncio
    async def test_redis_under_load(self):
        """Test Redis performance under high load"""
        redis = get_redis()
        
        # Simulate high load
        tasks = []
        for i in range(1000):
            task = redis.set(f"load_test:{i}", f"value:{i}")
            tasks.append(task)
        
        start_time = time.time()
        await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # Performance assertions
        operations_per_second = 1000 / total_time
        assert operations_per_second > 100, f"Redis too slow: {operations_per_second} ops/sec"
        
        # Verify all data was written
        verification_tasks = []
        for i in range(1000):
            task = redis.get(f"load_test:{i}")
            verification_tasks.append(task)
        
        results = await asyncio.gather(*verification_tasks)
        successful_writes = sum(1 for r in results if r == f"value:{i}")
        
        assert successful_writes == 1000, f"Only {successful_writes}/1000 writes successful"
        
        # Cleanup
        cleanup_tasks = []
        for i in range(1000):
            task = redis.delete(f"load_test:{i}")
            cleanup_tasks.append(task)
        
        await asyncio.gather(*cleanup_tasks)
        
        print(f"Redis handled 1000 operations in {total_time:.2f}s "
              f"({operations_per_second:.0f} ops/sec)")
    
    @pytest.mark.asyncio
    async def test_lock_contention(self):
        """Test distributed locks under contention"""
        lock_manager = get_lock_manager()
        
        async def contending_worker(worker_id: int):
            """Worker that tries to acquire the same lock"""
            lock = await lock_manager.create_lock("contention_test", timeout=5)
            
            start_time = time.time()
            acquired = await lock.acquire()
            wait_time = time.time() - start_time
            
            if acquired:
                # Hold lock for a short time
                await asyncio.sleep(0.1)
                await lock.release()
                return {"worker_id": worker_id, "acquired": True, "wait_time": wait_time}
            else:
                return {"worker_id": worker_id, "acquired": False, "wait_time": wait_time}
        
        # Run multiple workers trying to acquire the same lock
        tasks = [contending_worker(i) for i in range(10)]
        results = await asyncio.gather(*tasks)
        
        # Only one worker should acquire the lock at a time
        acquired_workers = [r for r in results if r["acquired"]]
        assert len(acquired_workers) >= 1, "At least one worker should acquire the lock"
        
        # Check wait times are reasonable
        max_wait_time = max(r["wait_time"] for r in results)
        assert max_wait_time < 10.0, f"Wait time too long: {max_wait_time}s"


if __name__ == "__main__":
    # Run tests manually
    async def main():
        test_instance = TestRedisIntegration()
        
        print("Running Redis integration tests...")
        
        try:
            await test_instance.test_session_management()
            print("✅ Session management test passed")
            
            await test_instance.test_rate_limiting()
            print("✅ Rate limiting test passed")
            
            await test_instance.test_semantic_cache()
            print("✅ Semantic cache test passed")
            
            await test_instance.test_distributed_locks()
            print("✅ Distributed locks test passed")
            
            await test_instance.test_redis_basic_operations()
            print("✅ Basic operations test passed")
            
            await test_instance.test_concurrent_operations()
            print("✅ Concurrent operations test passed")
            
            print("🎉 All Redis integration tests passed!")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(main())
