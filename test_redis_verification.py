#!/usr/bin/env python3
"""
Empirical verification test for Redis services.

Tests actual functionality, not just compilation.
This is a cynical test - it verifies things actually work.
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))


async def test_redis_client():
    """Test 1: Redis client connection and basic operations."""
    print("🔍 CHECK 1: Testing Redis client connection and basic operations")

    try:
        # Import and test client
        from redis.client import get_redis

        # Get client (this will fail if env vars not set)
        redis = get_redis()
        print("✓ Redis client created successfully")

        # Test basic operations
        test_key = "test:verification:basic_ops"
        test_value = "test_value_12345"

        # Set operation
        result = await redis.set(test_key, test_value, ex=60)
        assert result == True, "SET operation failed"
        print("✓ SET operation works")

        # Get operation
        retrieved = await redis.get(test_key)
        assert (
            retrieved == test_value
        ), f"GET failed: expected {test_value}, got {retrieved}"
        print("✓ GET operation works")

        # JSON operations
        test_data = {"test": "data", "number": 42, "list": [1, 2, 3]}
        json_key = "test:verification:json_ops"

        result = await redis.set_json(json_key, test_data, ex=60)
        assert result == True, "SET JSON failed"
        print("✓ SET JSON operation works")

        retrieved_data = await redis.get_json(json_key)
        assert (
            retrieved_data == test_data
        ), f"GET JSON failed: {retrieved_data} != {test_data}"
        print("✓ GET JSON operation works")

        # Counter operations
        counter_key = "test:verification:counter"
        await redis.set(counter_key, "0")

        result = await redis.incr(counter_key)
        assert result == 1, f"INCR failed: expected 1, got {result}"

        result = await redis.incrby(counter_key, 5)
        assert result == 6, f"INCRBY failed: expected 6, got {result}"
        print("✓ Counter operations work")

        # Cleanup
        await redis.delete(test_key, json_key, counter_key)
        print("✓ Cleanup successful")

        print("🎉 CHECK 1 PASSED: Redis client and basic operations work correctly")
        return True

    except Exception as e:
        print(f"❌ CHECK 1 FAILED: {e}")
        return False


async def test_session_service():
    """Test 2: Session management with workspace isolation."""
    print("\n🔍 CHECK 2: Testing session management with workspace isolation")

    try:
        from redis.session import SessionService
        from redis.session_models import SessionData

        session_service = SessionService()

        # Test session creation
        user_id = "test_user_123"
        workspace_id = "test_workspace_456"

        session_id = await session_service.create_session(
            user_id=user_id, workspace_id=workspace_id, metadata={"test": True}
        )
        assert session_id is not None, "Session creation failed"
        print("✓ Session created successfully")

        # Test session retrieval
        session = await session_service.get_session(session_id)
        assert session is not None, "Session retrieval failed"
        assert (
            session.user_id == user_id
        ), f"User ID mismatch: {session.user_id} != {user_id}"
        assert (
            session.workspace_id == workspace_id
        ), f"Workspace ID mismatch: {session.workspace_id} != {workspace_id}"
        print("✓ Session retrieval works")

        # Test message addition
        await session_service.add_message(
            session_id=session_id,
            role="user",
            content="Test message",
            metadata={"test": True},
        )

        updated_session = await session_service.get_session(session_id)
        assert len(updated_session.messages) == 1, "Message not added"
        assert updated_session.messages[0]["role"] == "user", "Message role incorrect"
        print("✓ Message addition works")

        # Test workspace isolation (create session for different workspace)
        other_workspace_id = "other_workspace_789"
        other_session_id = await session_service.create_session(
            user_id=user_id, workspace_id=other_workspace_id
        )

        # Verify isolation
        access_check = await session_service.validate_session_access(
            session_id=session_id, user_id=user_id, workspace_id=workspace_id
        )
        assert access_check == True, "Valid access check failed"

        # Try wrong workspace
        wrong_access = await session_service.validate_session_access(
            session_id=session_id, user_id=user_id, workspace_id="wrong_workspace"
        )
        assert wrong_access == False, "Invalid access should have failed"
        print("✓ Workspace isolation works")

        # Test session expiry
        await session_service.extend_session(session_id, 3600)
        extended_session = await session_service.get_session(session_id)
        assert extended_session.expires_at is not None, "Expiry not set"
        print("✓ Session extension works")

        # Cleanup
        await session_service.delete_session(session_id)
        await session_service.delete_session(other_session_id)

        print("🎉 CHECK 2 PASSED: Session management with workspace isolation works")
        return True

    except Exception as e:
        print(f"❌ CHECK 2 FAILED: {e}")
        return False


async def test_cache_service():
    """Test 3: Caching service with TTL and invalidation."""
    print("\n🔍 CHECK 3: Testing caching service with TTL and invalidation")

    try:
        from redis.cache import CacheService

        cache_service = CacheService()

        workspace_id = "test_cache_workspace"
        cache_key = "test_cache_key"
        test_data = {"cached": "data", "timestamp": datetime.now().isoformat()}

        # Test cache set/get
        result = await cache_service.set(workspace_id, cache_key, test_data, ttl=60)
        assert result == True, "Cache set failed"
        print("✓ Cache set works")

        retrieved_data = await cache_service.get(workspace_id, cache_key)
        assert (
            retrieved_data == test_data
        ), f"Cache get failed: {retrieved_data} != {test_data}"
        print("✓ Cache get works")

        # Test cache miss
        miss_data = await cache_service.get(workspace_id, "non_existent_key")
        assert miss_data is None, "Cache miss should return None"
        print("✓ Cache miss works")

        # Test get_or_set
        factory_called = False

        async def test_factory():
            nonlocal factory_called
            factory_called = True
            return {"factory": "data"}

        # First call should call factory
        result1 = await cache_service.get_or_set(
            workspace_id, "factory_key", test_factory
        )
        assert factory_called == True, "Factory not called on first get_or_set"
        assert result1 == {"factory": "data"}, "Factory result incorrect"
        print("✓ get_or_set factory call works")

        # Second call should use cache
        factory_called = False
        result2 = await cache_service.get_or_set(
            workspace_id, "factory_key", test_factory
        )
        assert factory_called == False, "Factory called on cached get_or_set"
        assert result2 == {"factory": "data"}, "Cached result incorrect"
        print("✓ get_or_set cache hit works")

        # Test TTL
        ttl_result = await cache_service.get_ttl(workspace_id, cache_key)
        assert ttl_result > 0, "TTL should be positive"
        print(f"✓ TTL works: {ttl_result} seconds")

        # Test cache deletion
        delete_result = await cache_service.delete(workspace_id, cache_key)
        assert delete_result == True, "Cache delete failed"

        deleted_data = await cache_service.get(workspace_id, cache_key)
        assert deleted_data is None, "Data should be deleted"
        print("✓ Cache deletion works")

        print("🎉 CHECK 3 PASSED: Caching service with TTL and invalidation works")
        return True

    except Exception as e:
        print(f"❌ CHECK 3 FAILED: {e}")
        return False


async def test_rate_limiting():
    """Test 4: Rate limiting with sliding window algorithm."""
    print("\n🔍 CHECK 4: Testing rate limiting with sliding window algorithm")

    try:
        from redis.rate_limit import RateLimitService

        rate_limiter = RateLimitService()

        user_id = "test_rate_user"
        endpoint = "test_endpoint"
        user_tier = "free"

        # Test rate limit check (should be allowed initially)
        result = await rate_limiter.check_limit(user_id, endpoint, user_tier)
        assert result.allowed == True, "First request should be allowed"
        assert result.remaining > 0, "Should have remaining requests"
        print(f"✓ Initial rate limit check: {result.remaining}/{result.limit}")

        # Record multiple requests quickly
        requests_made = 0
        for i in range(5):
            result = await rate_limiter.record_request(user_id, endpoint, user_tier)
            if result.allowed:
                requests_made += 1

        assert requests_made > 0, "Some requests should be allowed"
        print(f"✓ Multiple requests recorded: {requests_made} allowed")

        # Test rate limit enforcement
        # Make requests until limit is hit
        limit_hit = False
        for i in range(200):  # High number to ensure limit is hit
            result = await rate_limiter.check_limit(user_id, endpoint, user_tier)
            if not result.allowed:
                limit_hit = True
                break

        assert limit_hit == True, "Rate limit should be hit eventually"
        print(f"✓ Rate limit enforced: retry_after={result.retry_after}s")

        # Test different user tier
        premium_result = await rate_limiter.check_limit(user_id, endpoint, "growth")
        assert (
            premium_result.limit > result.limit
        ), "Higher tier should have higher limit"
        print(
            f"✓ Tier-based limits: free={result.limit}, growth={premium_result.limit}"
        )

        # Test limit reset
        reset_result = await rate_limiter.reset_limit(user_id, endpoint)
        assert reset_result == True, "Limit reset should work"

        after_reset = await rate_limiter.check_limit(user_id, endpoint, user_tier)
        assert after_reset.allowed == True, "Should be allowed after reset"
        print("✓ Rate limit reset works")

        print("🎉 CHECK 4 PASSED: Rate limiting with sliding window algorithm works")
        return True

    except Exception as e:
        print(f"❌ CHECK 4 FAILED: {e}")
        return False


async def test_queue_system():
    """Test 5: Queue system with priority and retry logic."""
    print("\n🔍 CHECK 5: Testing queue system with priority and retry logic")

    try:
        from redis.queue import QueueService
        from redis.queue_models import Job, JobPriority, JobStatus

        queue_service = QueueService()
        queue_name = "test_queue"

        # Test job enqueue
        job_id = await queue_service.enqueue(
            queue_name=queue_name,
            job_type="test_job",
            payload={"test": "data", "priority": "high"},
            priority=JobPriority.HIGH.value,
        )
        assert job_id is not None, "Job enqueue failed"
        print(f"✓ Job enqueued: {job_id}")

        # Test queue length
        length = await queue_service.queue_length(queue_name)
        assert length >= 1, f"Queue should have at least 1 job, got {length}"
        print(f"✓ Queue length: {length}")

        # Test job dequeue
        job = await queue_service.dequeue(queue_name, worker_id="test_worker")
        assert job is not None, "Job dequeue failed"
        assert job.job_id == job_id, "Dequeued job ID mismatch"
        assert job.status == JobStatus.PROCESSING, "Job should be marked as processing"
        assert job.worker_id == "test_worker", "Worker ID not set"
        print("✓ Job dequeued and marked as processing")

        # Test job completion
        from redis.queue_models import JobResult

        result = JobResult(
            success=True, data={"result": "success"}, execution_time_ms=100
        )

        complete_result = await queue_service.complete_job(
            job_id, result, "test_worker"
        )
        assert complete_result == True, "Job completion failed"
        print("✓ Job completed successfully")

        # Verify job status
        completed_job = await queue_service.get_job(job_id)
        assert completed_job.status == JobStatus.COMPLETED, "Job should be completed"
        assert completed_job.result.success == True, "Job result should be successful"
        print("✓ Job status verified")

        # Test priority queue (multiple jobs)
        high_priority_id = await queue_service.enqueue(
            queue_name=queue_name,
            job_type="high_priority",
            payload={"priority": "high"},
            priority=JobPriority.HIGH.value,
        )

        low_priority_id = await queue_service.enqueue(
            queue_name=queue_name,
            job_type="low_priority",
            payload={"priority": "low"},
            priority=JobPriority.LOW.value,
        )

        # Should get high priority job first
        first_job = await queue_service.peek(queue_name)
        assert first_job is not None, "Should have job in queue"
        assert (
            first_job.priority == JobPriority.HIGH.value
        ), "Should get high priority job first"
        print("✓ Priority queue works")

        # Test retry logic
        retry_job_id = await queue_service.enqueue(
            queue_name=queue_name,
            job_type="retry_test",
            payload={"test": "retry"},
            max_retries=2,
        )

        retry_job = await queue_service.dequeue(queue_name, worker_id="retry_worker")
        fail_result = await queue_service.fail_job(
            retry_job_id, "Test error", worker_id="retry_worker"
        )
        assert fail_result == True, "Job fail should work"

        # Check if job is retried
        retried_job = await queue_service.get_job(retry_job_id)
        assert retried_job.status == JobStatus.PENDING, "Job should be retried"
        assert retried_job.attempt_count == 1, "Attempt count should increment"
        print("✓ Retry logic works")

        # Cleanup
        await queue_service.clear_queue(queue_name)

        print("🎉 CHECK 5 PASSED: Queue system with priority and retry logic works")
        return True

    except Exception as e:
        print(f"❌ CHECK 5 FAILED: {e}")
        return False


async def test_usage_tracking():
    """Test 6: Usage tracking with budget enforcement."""
    print("\n🔍 CHECK 6: Testing usage tracking with budget enforcement")

    try:
        from redis.usage import UsageTracker

        usage_tracker = UsageTracker()

        workspace_id = "test_usage_workspace"

        # Test usage recording
        await usage_tracker.record_usage(
            workspace_id=workspace_id,
            tokens_input=100,
            tokens_output=50,
            cost_usd=0.01,
            agent_name="test_agent",
            success=True,
            latency_ms=150.0,
        )
        print("✓ Usage recorded successfully")

        # Test daily usage retrieval
        daily_usage = await usage_tracker.get_daily_usage(workspace_id)
        assert daily_usage is not None, "Daily usage should exist"
        assert (
            daily_usage.total_tokens == 150
        ), f"Token count mismatch: {daily_usage.total_tokens}"
        assert daily_usage.total_requests == 1, "Request count mismatch"
        assert daily_usage.successful_requests == 1, "Success count mismatch"
        print(
            f"✓ Daily usage retrieved: {daily_usage.total_tokens} tokens, {daily_usage.total_requests} requests"
        )

        # Test agent performance
        performance = await usage_tracker.get_agent_performance(
            workspace_id, "test_agent"
        )
        assert (
            performance["total_requests"] == 1
        ), "Agent performance should show 1 request"
        assert performance["total_tokens"] == 150, "Agent token count mismatch"
        assert performance["success_rate"] == 1.0, "Agent success rate should be 100%"
        print("✓ Agent performance tracking works")

        # Test budget check
        budget = await usage_tracker.check_budget(workspace_id, 0.05, "free")
        assert budget["can_afford"] == True, "Should afford small cost"
        assert budget["budget_limit"] == 1.0, "Free tier budget should be $1"
        assert budget["remaining"] > 0, "Should have remaining budget"
        print(f"✓ Budget check works: ${budget['remaining']:.2f} remaining")

        # Test budget enforcement
        try:
            await usage_tracker.enforce_budget(workspace_id, 10.0, "free")
            assert False, "Should have raised budget exceeded exception"
        except Exception as e:
            assert "Budget exceeded" in str(e), "Should be budget exceeded error"
            print("✓ Budget enforcement works")

        # Test usage summary
        summary = await usage_tracker.get_usage_summary(workspace_id, days=1)
        assert summary["total_tokens"] == 150, "Summary token count mismatch"
        assert summary["total_cost"] == 0.01, "Summary cost mismatch"
        assert len(summary["top_agents"]) == 1, "Should have 1 top agent"
        print("✓ Usage summary works")

        print("🎉 CHECK 6 PASSED: Usage tracking with budget enforcement works")
        return True

    except Exception as e:
        print(f"❌ CHECK 6 FAILED: {e}")
        return False


async def main():
    """Run all empirical verification tests."""
    print("🚀 STARTING EMPIRICAL VERIFICATION OF REDIS SERVICES")
    print("=" * 60)

    # Set up test environment variables (if not set)
    if not os.getenv("UPSTASH_REDIS_URL"):
        print("⚠️  WARNING: UPSTASH_REDIS_URL not set, using mock values")
        os.environ["UPSTASH_REDIS_URL"] = "https://mock-redis.upstash.io"
        os.environ["UPSTASH_REDIS_TOKEN"] = "mock-token"

    tests = [
        ("Redis Client", test_redis_client),
        ("Session Service", test_session_service),
        ("Cache Service", test_cache_service),
        ("Rate Limiting", test_rate_limiting),
        ("Queue System", test_queue_system),
        ("Usage Tracking", test_usage_tracking),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            result = await test_func()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print("📊 EMPIRICAL VERIFICATION SUMMARY")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed / (passed + failed) * 100):.1f}%")

    if failed == 0:
        print("🎉 ALL TESTS PASSED - Redis services are working correctly!")
        return True
    else:
        print("⚠️  SOME TESTS FAILED - Check implementation")
        return False


if __name__ == "__main__":
    asyncio.run(main())
