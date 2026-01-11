#!/usr/bin/env python3
"""
End-to-end production verification test.

Tests all critical services work together without fallbacks.
"""

import asyncio
import json
import logging
import os
import sys
import time
from typing import Any, Dict, List

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from events.bus import EventBus
from infrastructure.secrets import SecretsManager
from infrastructure.storage import CloudStorage
from jobs.scheduler import JobScheduler
from monitoring.health import HealthAggregator
from redis.cache import CacheService
from redis.client import RedisClient
from redis.config import RedisConfig
from redis.pubsub import PubSubService
from redis.queue import QueueService
from redis.rate_limit import RateLimitService
from redis.session import SessionService
from webhooks.handler import WebhookHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductionE2ETester:
    """End-to-end production tester."""

    def __init__(self):
        self.test_results = {}
        self.errors = []
        self.warnings = []

    def log_error(self, test_name: str, error: str):
        """Log an error."""
        self.errors.append(f"{test_name}: {error}")
        logger.error(f"❌ {test_name}: {error}")

    def log_warning(self, test_name: str, warning: str):
        """Log a warning."""
        self.warnings.append(f"{test_name}: {warning}")
        logger.warning(f"⚠️ {test_name}: {warning}")

    def log_success(self, test_name: str, message: str):
        """Log success."""
        logger.info(f"✅ {test_name}: {message}")

    async def test_redis_core_operations(self) -> bool:
        """Test Redis core operations."""
        test_name = "Redis Core Operations"

        try:
            client = RedisClient()

            # Test basic operations
            test_key = "raptorflow:e2e:test"
            test_value = json.dumps({"test": True, "timestamp": time.time()})

            # Set and get
            await client.set(test_key, test_value, ex=60)
            retrieved = await client.get(test_key)

            if retrieved != test_value:
                self.log_error(test_name, "Set/Get operation failed")
                return False

            # Test JSON operations
            await client.set_json(test_key + ":json", {"nested": {"data": "value"}})
            json_data = await client.get_json(test_key + ":json")

            if not json_data or json_data.get("nested", {}).get("data") != "value":
                self.log_error(test_name, "JSON operations failed")
                return False

            # Test increment
            await client.set(test_key + ":counter", "0")
            await client.incr(test_key + ":counter")
            counter = await client.get(test_key + ":counter")

            if counter != "1":
                self.log_error(test_name, "Counter operations failed")
                return False

            # Cleanup
            await client.delete(test_key, test_key + ":json", test_key + ":counter")

            self.log_success(test_name, "All Redis operations working")
            return True

        except Exception as e:
            self.log_error(test_name, str(e))
            return False

    async def test_session_service(self) -> bool:
        """Test session service."""
        test_name = "Session Service"

        try:
            session_service = SessionService()

            # Create session
            user_id = "test-user-123"
            workspace_id = "test-workspace-456"
            metadata = {"test": True, "role": "admin"}

            session_id = await session_service.create_session(
                user_id, workspace_id, metadata
            )

            if not session_id:
                self.log_error(test_name, "Failed to create session")
                return False

            # Get session
            session_data = await session_service.get_session(session_id)

            if not session_data or session_data.user_id != user_id:
                self.log_error(test_name, "Failed to retrieve session")
                return False

            # Update session
            await session_service.update_session(session_id, {"last_action": "test"})
            updated_session = await session_service.get_session(session_id)

            if (
                not updated_session
                or updated_session.context.get("last_action") != "test"
            ):
                self.log_error(test_name, "Failed to update session")
                return False

            # Delete session
            await session_service.delete_session(session_id)
            deleted_session = await session_service.get_session(session_id)

            if deleted_session is not None:
                self.log_error(test_name, "Failed to delete session")
                return False

            self.log_success(test_name, "Session service working correctly")
            return True

        except Exception as e:
            self.log_error(test_name, str(e))
            return False

    async def test_cache_service(self) -> bool:
        """Test cache service."""
        test_name = "Cache Service"

        try:
            cache_service = CacheService()

            workspace_id = "test-workspace"
            cache_key = "test-cache-key"
            cache_value = {"data": "test", "timestamp": time.time()}

            # Set cache
            await cache_service.set(workspace_id, cache_key, cache_value, ttl=60)

            # Get cache
            retrieved_value = await cache_service.get(workspace_id, cache_key)

            if not retrieved_value or retrieved_value.get("data") != "test":
                self.log_error(test_name, "Cache get/set failed")
                return False

            # Test get_or_set
            new_key = "test-new-key"
            factory_called = False

            async def factory():
                nonlocal factory_called
                factory_called = True
                return {"factory": True}

            result = await cache_service.get_or_set(workspace_id, new_key, factory)

            if not factory_called or not result.get("factory"):
                self.log_error(test_name, "Cache get_or_set failed")
                return False

            # Clear workspace cache
            await cache_service.clear_workspace(workspace_id)

            # Verify cleared
            cleared_value = await cache_service.get(workspace_id, cache_key)
            if cleared_value is not None:
                self.log_error(test_name, "Cache clear failed")
                return False

            self.log_success(test_name, "Cache service working correctly")
            return True

        except Exception as e:
            self.log_error(test_name, str(e))
            return False

    async def test_rate_limiting(self) -> bool:
        """Test rate limiting service."""
        test_name = "Rate Limiting"

        try:
            rate_limit_service = RateLimitService()

            user_id = "test-user"
            endpoint = "/api/v1/test"
            limit = 5
            window = 60

            # Reset rate limit
            await rate_limit_service.reset_limit(user_id, endpoint)

            # Test within limit
            for i in range(limit):
                result = await rate_limit_service.check_limit(
                    user_id, endpoint, limit, window
                )
                if not result.allowed:
                    self.log_error(
                        test_name, f"Rate limit blocked request {i+1} unexpectedly"
                    )
                    return False

            # Test exceeding limit
            result = await rate_limit_service.check_limit(
                user_id, endpoint, limit, window
            )
            if result.allowed:
                self.log_error(test_name, "Rate limit allowed request beyond limit")
                return False

            if result.remaining != 0:
                self.log_error(
                    test_name, f"Expected 0 remaining, got {result.remaining}"
                )
                return False

            self.log_success(test_name, "Rate limiting working correctly")
            return True

        except Exception as e:
            self.log_error(test_name, str(e))
            return False

    async def test_queue_service(self) -> bool:
        """Test queue service."""
        test_name = "Queue Service"

        try:
            queue_service = QueueService()
            queue_name = "test-queue"

            # Clear queue
            await queue_service.clear_queue(queue_name)

            # Enqueue jobs
            job_data = [
                {"id": 1, "task": "test1"},
                {"id": 2, "task": "test2"},
                {"id": 3, "task": "test3"},
            ]

            for data in job_data:
                await queue_service.enqueue(queue_name, data)

            # Check queue length
            length = await queue_service.queue_length(queue_name)
            if length != len(job_data):
                self.log_error(
                    test_name, f"Expected queue length {len(job_data)}, got {length}"
                )
                return False

            # Dequeue jobs
            dequeued_jobs = []
            while True:
                job = await queue_service.dequeue(queue_name)
                if job is None:
                    break
                dequeued_jobs.append(job)

            if len(dequeued_jobs) != len(job_data):
                self.log_error(
                    test_name,
                    f"Expected {len(job_data)} jobs, got {len(dequeued_jobs)}",
                )
                return False

            # Verify job data
            for i, job in enumerate(dequeued_jobs):
                expected_data = job_data[i]
                if job.data.get("id") != expected_data["id"]:
                    self.log_error(test_name, f"Job data mismatch for job {i}")
                    return False

            self.log_success(test_name, "Queue service working correctly")
            return True

        except Exception as e:
            self.log_error(test_name, str(e))
            return False

    async def test_pubsub_service(self) -> bool:
        """Test pub/sub service."""
        test_name = "Pub/Sub Service"

        try:
            pubsub_service = PubSubService()

            # Test message
            test_message = {"type": "test", "data": "hello world"}
            message_received = asyncio.Event()
            received_message = None

            async def message_handler(message):
                nonlocal received_message
                received_message = message
                message_received.set()

            # Subscribe
            await pubsub_service.subscribe("test-channel", message_handler)

            # Publish
            await pubsub_service.publish("test-channel", test_message)

            # Wait for message
            try:
                await asyncio.wait_for(message_received.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                self.log_error(test_name, "Pub/Sub message not received")
                return False

            if not received_message or received_message.get("data") != test_message:
                self.log_error(test_name, "Pub/Sub message mismatch")
                return False

            # Unsubscribe
            await pubsub_service.unsubscribe("test-channel")

            self.log_success(test_name, "Pub/Sub service working correctly")
            return True

        except Exception as e:
            self.log_error(test_name, str(e))
            return False

    async def test_webhook_handling(self) -> bool:
        """Test webhook handling."""
        test_name = "Webhook Handling"

        try:
            webhook_handler = WebhookHandler()

            # Test webhook event
            from webhooks.models import WebhookEvent

            test_event = WebhookEvent(
                event_id="test-event-123",
                event_type="test.event",
                payload={"test": True},
                timestamp=time.time(),
                source="test",
            )

            # Register handler
            handled_event = None

            async def test_handler(event):
                nonlocal handled_event
                handled_event = event

            webhook_handler.register_handler("test.event", test_handler)

            # Handle event
            await webhook_handler.handle(test_event)

            if not handled_event or handled_event.event_id != test_event.event_id:
                self.log_error(test_name, "Webhook handling failed")
                return False

            self.log_success(test_name, "Webhook handling working correctly")
            return True

        except Exception as e:
            self.log_error(test_name, str(e))
            return False

    async def test_event_bus(self) -> bool:
        """Test event bus."""
        test_name = "Event Bus"

        try:
            event_bus = EventBus()

            # Test event
            from events.types import Event

            test_event = Event(
                type="test.event", data={"message": "hello"}, source="e2e-test"
            )

            # Subscribe and emit
            received_event = None

            async def event_handler(event):
                nonlocal received_event
                received_event = event

            event_bus.subscribe("test.event", event_handler)
            await event_bus.emit(test_event)

            # Wait for processing
            await asyncio.sleep(0.1)

            if not received_event or received_event.data.get("message") != "hello":
                self.log_error(test_name, "Event bus failed")
                return False

            self.log_success(test_name, "Event bus working correctly")
            return True

        except Exception as e:
            self.log_error(test_name, str(e))
            return False

    async def test_health_aggregator(self) -> bool:
        """Test health aggregator."""
        test_name = "Health Aggregator"

        try:
            health_aggregator = HealthAggregator()

            # Run full health check
            health_report = await health_aggregator.full_health_check()

            if not health_report:
                self.log_error(test_name, "Health check returned None")
                return False

            # Check report structure
            if "status" not in health_report:
                self.log_error(test_name, "Health report missing status")
                return False

            if "checks" not in health_report:
                self.log_error(test_name, "Health report missing checks")
                return False

            # Log health status
            status = health_report["status"]
            self.log_success(test_name, f"Health status: {status}")

            return True

        except Exception as e:
            self.log_error(test_name, str(e))
            return False

    async def test_integration_workflow(self) -> bool:
        """Test complete integration workflow."""
        test_name = "Integration Workflow"

        try:
            # Create a user session
            session_service = SessionService()
            user_id = "integration-test-user"
            workspace_id = "integration-test-workspace"

            session_id = await session_service.create_session(
                user_id, workspace_id, {"test": "integration"}
            )

            # Cache some data
            cache_service = CacheService()
            await cache_service.set(workspace_id, "user-preferences", {"theme": "dark"})

            # Queue a background job
            queue_service = QueueService()
            await queue_service.enqueue(
                "background-jobs",
                {"type": "test-job", "user_id": user_id, "workspace_id": workspace_id},
            )

            # Publish an event
            event_bus = EventBus()
            await event_bus.emit(
                {
                    "type": "user.session.created",
                    "data": {"session_id": session_id, "user_id": user_id},
                    "source": "integration-test",
                }
            )

            # Check rate limiting
            rate_limit_service = RateLimitService()
            rate_result = await rate_limit_service.check_limit(
                user_id, "api.test", 10, 60
            )

            if not rate_result.allowed:
                self.log_error(test_name, "Rate limiting blocked integration test")
                return False

            # Verify all components worked together
            session_data = await session_service.get_session(session_id)
            cached_data = await cache_service.get(workspace_id, "user-preferences")
            queue_length = await queue_service.queue_length("background-jobs")

            if not session_data or session_data.user_id != user_id:
                self.log_error(test_name, "Session not created correctly")
                return False

            if not cached_data or cached_data.get("theme") != "dark":
                self.log_error(test_name, "Cache not working correctly")
                return False

            if queue_length == 0:
                self.log_error(test_name, "Job not queued correctly")
                return False

            # Cleanup
            await session_service.delete_session(session_id)
            await cache_service.clear_workspace(workspace_id)
            await queue_service.clear_queue("background-jobs")

            self.log_success(test_name, "Integration workflow completed successfully")
            return True

        except Exception as e:
            self.log_error(test_name, str(e))
            return False

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all e2e tests."""
        logger.info("Starting end-to-end production tests...")

        tests = [
            ("redis_core", self.test_redis_core_operations),
            ("session_service", self.test_session_service),
            ("cache_service", self.test_cache_service),
            ("rate_limiting", self.test_rate_limiting),
            ("queue_service", self.test_queue_service),
            ("pubsub_service", self.test_pubsub_service),
            ("webhook_handling", self.test_webhook_handling),
            ("event_bus", self.test_event_bus),
            ("health_aggregator", self.test_health_aggregator),
            ("integration_workflow", self.test_integration_workflow),
        ]

        results = {}

        for test_name, test_func in tests:
            logger.info(f"Running {test_name}...")
            try:
                result = await test_func()
                results[test_name] = result
            except Exception as e:
                logger.error(f"Test {test_name} crashed: {e}")
                results[test_name] = False
                self.log_error(test_name, f"Test crashed: {e}")

        # Summary
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result)

        return {
            "results": results,
            "summary": {
                "total": total_tests,
                "passed": passed_tests,
                "failed": total_tests - passed_tests,
                "success_rate": (passed_tests / total_tests) * 100,
            },
            "errors": self.errors,
            "warnings": self.warnings,
        }

    def print_summary(self, test_results: Dict[str, Any]):
        """Print test summary."""
        summary = test_results["summary"]

        print("\n" + "=" * 60)
        print("END-TO-END PRODUCTION TEST SUMMARY")
        print("=" * 60)

        print(f"\nOverall Result: {summary['passed']}/{summary['total']} tests passed")
        print(f"Success Rate: {summary['success_rate']:.1f}%")

        print("\nTest Results:")
        for test_name, passed in test_results["results"].items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"  {test_name:20} {status}")

        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print(f"\n⚠️ WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")

        print("\n" + "=" * 60)

        if summary["failed"] > 0:
            print("🚨 E2E TESTS FAILED - Production not ready")
            sys.exit(1)
        else:
            print("🎉 ALL E2E TESTS PASSED - Production ready!")
            sys.exit(0)


async def main():
    """Main test function."""
    tester = ProductionE2ETester()
    results = await tester.run_all_tests()
    tester.print_summary(results)


if __name__ == "__main__":
    asyncio.run(main())
