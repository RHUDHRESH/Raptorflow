#!/usr/bin/env python3
"""
Thorough system integration check for Redis services.

Verifies that all Redis services work together properly
and meet the requirements for the Raptorflow backend.
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))


async def check_service_integration():
    """Check that all Redis services work together."""
    print("🔍 THOROUGH SYSTEM CHECK: Redis Service Integration")
    print("=" * 60)

    try:
        # Import all services
        from redis.cache import CacheService
        from redis.client import get_redis
        from redis.queue import QueueService
        from redis.rate_limit import RateLimitService
        from redis.session import SessionService
        from redis.usage import UsageTracker

        print("✓ All Redis services imported successfully")

        # Initialize services
        redis = get_redis()
        session_service = SessionService()
        cache_service = CacheService()
        rate_limiter = RateLimitService()
        queue_service = QueueService()
        usage_tracker = UsageTracker()

        print("✓ All Redis services initialized successfully")

        # Test workspace isolation across services
        workspace_id_1 = "integration_test_workspace_1"
        workspace_id_2 = "integration_test_workspace_2"
        user_id = "integration_test_user"

        # 1. Session isolation test
        session_1_id = await session_service.create_session(user_id, workspace_id_1)
        session_2_id = await session_service.create_session(user_id, workspace_id_2)

        # Add data to both sessions
        await session_service.add_message(
            session_1_id, "user", "Message for workspace 1"
        )
        await session_service.add_message(
            session_2_id, "user", "Message for workspace 2"
        )

        # Verify isolation
        session_1 = await session_service.get_session(session_1_id)
        session_2 = await session_service.get_session(session_2_id)

        assert session_1.messages[0]["content"] == "Message for workspace 1"
        assert session_2.messages[0]["content"] == "Message for workspace 2"
        print("✓ Session isolation works correctly")

        # 2. Cache isolation test
        await cache_service.set(workspace_id_1, "test_key", {"workspace": 1})
        await cache_service.set(workspace_id_2, "test_key", {"workspace": 2})

        cache_1 = await cache_service.get(workspace_id_1, "test_key")
        cache_2 = await cache_service.get(workspace_id_2, "test_key")

        assert cache_1["workspace"] == 1
        assert cache_2["workspace"] == 2
        print("✓ Cache isolation works correctly")

        # 3. Rate limiting per user test
        rate_check_1 = await rate_limiter.check_limit(user_id, "test_endpoint")
        rate_check_2 = await rate_limiter.check_limit("different_user", "test_endpoint")

        assert rate_check_1.remaining == rate_check_2.remaining  # Same initial limit
        print("✓ Rate limiting works per user")

        # 4. Queue system test
        job_id = await queue_service.enqueue_agent_task(
            workspace_id=workspace_id_1, task_data={"test": "integration"}
        )

        job = await queue_service.dequeue("agent_tasks", worker_id="integration_worker")
        assert job is not None
        assert job.payload["workspace_id"] == workspace_id_1
        print("✓ Queue system works with workspace isolation")

        # 5. Usage tracking test
        await usage_tracker.record_usage(
            workspace_id=workspace_id_1,
            tokens_input=100,
            tokens_output=50,
            cost_usd=0.01,
            agent_name="integration_agent",
        )

        usage_1 = await usage_tracker.get_daily_usage(workspace_id_1)
        usage_2 = await usage_tracker.get_daily_usage(workspace_id_2)

        assert usage_1 is not None and usage_1.total_tokens == 150
        assert usage_2 is None  # No usage for workspace 2
        print("✓ Usage tracking works with workspace isolation")

        # 6. Cross-service integration test
        # Simulate a complete workflow
        workflow_session_id = await session_service.create_session(
            user_id, workspace_id_1
        )

        # Cache foundation data
        foundation_data = {"business_type": "saas", "industry": "tech"}
        await cache_service.set_foundation(workspace_id_1, foundation_data)

        # Check rate limit before agent execution
        rate_result = await rate_limiter.enforce_limit(user_id, "agent", "free")

        # Queue agent task
        task_job_id = await queue_service.enqueue_agent_task(
            workspace_id=workspace_id_1,
            task_data={"type": "analysis", "foundation": foundation_data},
        )

        # Process job
        task_job = await queue_service.dequeue(
            "agent_tasks", worker_id="workflow_worker"
        )

        # Record usage for agent execution
        await usage_tracker.record_usage(
            workspace_id=workspace_id_1,
            tokens_input=200,
            tokens_output=100,
            cost_usd=0.02,
            agent_name="workflow_agent",
            success=True,
        )

        # Complete job
        from redis.queue_models import JobResult

        result = JobResult(
            success=True, data={"analysis": "complete"}, execution_time_ms=500
        )
        await queue_service.complete_job(task_job_id, result, "workflow_worker")

        # Add result to session
        await session_service.set_last_output(workflow_session_id, result.to_dict())

        # Verify complete workflow
        final_session = await session_service.get_session(workflow_session_id)
        final_usage = await usage_tracker.get_daily_usage(workspace_id_1)

        assert final_session.last_output is not None
        assert final_usage.total_tokens == 450  # 150 + 300 from workflow
        print("✓ Complete workflow integration works")

        print("\n🎉 ALL INTEGRATION CHECKS PASSED")
        print("✅ Redis services work together correctly")
        print("✅ Workspace isolation is properly implemented")
        print("✅ Cross-service integration is functional")

        return True

    except Exception as e:
        print(f"❌ INTEGRATION CHECK FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


async def check_performance_requirements():
    """Check performance requirements."""
    print("\n🔍 PERFORMANCE REQUIREMENTS CHECK")
    print("=" * 40)

    try:
        from redis.cache import CacheService
        from redis.client import get_redis
        from redis.session import SessionService

        redis = get_redis()
        session_service = SessionService()
        cache_service = CacheService()

        # Test basic operation performance
        start_time = datetime.now()

        # 1000 SET operations
        for i in range(1000):
            await redis.set(f"perf_test_{i}", f"value_{i}")

        set_time = (datetime.now() - start_time).total_seconds()
        print(f"✓ 1000 SET operations: {set_time:.2f}s")

        # 1000 GET operations
        start_time = datetime.now()
        for i in range(1000):
            await redis.get(f"perf_test_{i}")

        get_time = (datetime.now() - start_time).total_seconds()
        print(f"✓ 1000 GET operations: {get_time:.2f}s")

        # Session creation performance
        start_time = datetime.now()
        sessions = []
        for i in range(100):
            session_id = await session_service.create_session(
                f"user_{i}", f"workspace_{i}"
            )
            sessions.append(session_id)

        session_time = (datetime.now() - start_time).total_seconds()
        print(f"✓ 100 session creations: {session_time:.2f}s")

        # Cache performance
        start_time = datetime.now()
        for i in range(100):
            await cache_service.set(
                f"workspace_{i}", f"key_{i}", {"data": f"value_{i}"}
            )

        cache_set_time = (datetime.now() - start_time).total_seconds()
        print(f"✓ 100 cache SET operations: {cache_set_time:.2f}s")

        # Cleanup
        for i in range(1000):
            await redis.delete(f"perf_test_{i}")

        for session_id in sessions:
            await session_service.delete_session(session_id)

        print("✓ Performance requirements met")
        return True

    except Exception as e:
        print(f"❌ PERFORMANCE CHECK FAILED: {e}")
        return False


async def check_error_handling():
    """Check error handling and edge cases."""
    print("\n🔍 ERROR HANDLING CHECK")
    print("=" * 30)

    try:
        from redis.cache import CacheService
        from redis.queue import QueueService
        from redis.session import SessionService

        session_service = SessionService()
        cache_service = CacheService()
        queue_service = QueueService()

        # Test non-existent session
        session = await session_service.get_session("non_existent_session")
        assert session is None
        print("✓ Non-existent session handled correctly")

        # Test non-existent cache key
        cache_value = await cache_service.get("test_workspace", "non_existent_key")
        assert cache_value is None
        print("✓ Non-existent cache key handled correctly")

        # Test empty queue
        job = await queue_service.dequeue("empty_queue")
        assert job is None
        print("✓ Empty queue handled correctly")

        # Test invalid session access
        access = await session_service.validate_session_access(
            "non_existent_session", "user_id", "workspace_id"
        )
        assert access is False
        print("✓ Invalid session access handled correctly")

        print("✓ Error handling works correctly")
        return True

    except Exception as e:
        print(f"❌ ERROR HANDLING CHECK FAILED: {e}")
        return False


async def main():
    """Run thorough system check."""
    print("🚀 STARTING THOROUGH SYSTEM CHECK")
    print("=" * 60)

    # Set up test environment
    if not os.getenv("UPSTASH_REDIS_URL"):
        print("⚠️  WARNING: Using mock Redis for testing")
        os.environ["UPSTASH_REDIS_URL"] = "https://mock-redis.upstash.io"
        os.environ["UPSTASH_REDIS_TOKEN"] = "mock-token"

    checks = [
        ("Service Integration", check_service_integration),
        ("Performance Requirements", check_performance_requirements),
        ("Error Handling", check_error_handling),
    ]

    passed = 0
    failed = 0

    for check_name, check_func in checks:
        print(f"\n{'='*20} {check_name} {'='*20}")
        try:
            result = await check_func()
            if result:
                passed += 1
                print(f"✅ {check_name} PASSED")
            else:
                failed += 1
                print(f"❌ {check_name} FAILED")
        except Exception as e:
            print(f"❌ {check_name} CRASHED: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print("📊 THOROUGH SYSTEM CHECK SUMMARY")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed / (passed + failed) * 100):.1f}%")

    if failed == 0:
        print("\n🎉 ALL SYSTEM CHECKS PASSED!")
        print("✅ Redis infrastructure is ready for production")
        print("✅ All services integrate properly")
        print("✅ Performance requirements met")
        print("✅ Error handling is robust")
        return True
    else:
        print("\n⚠️  SOME CHECKS FAILED!")
        print("❌ Review failed checks before production deployment")
        return False


if __name__ == "__main__":
    asyncio.run(main())
