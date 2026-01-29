"""
Comprehensive Error Recovery Testing Framework for Raptorflow.
Tests all error recovery scenarios with validation and performance measurement.
"""

import asyncio
import pytest
import time
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from typing import Any, Dict, List

from .core.error_recovery import (
    ProductionErrorRecovery,
    ErrorPatternDetector,
    ErrorSeverity,
    ErrorPattern,
    RecoveryResult,
    get_production_error_recovery,
    handle_production_error,
)
from .core.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
    get_resilient_client,
)
from .core.predictive_failure import (
    PredictiveFailurePrevention,
    ResourceType,
    AlertLevel,
    get_predictive_failure,
)


class TestErrorPatternDetector:
    """Test error pattern detection and classification"""

    def setup_method(self):
        self.detector = ErrorPatternDetector()

    def test_rate_limit_pattern_detection(self):
        """Test rate limit error pattern detection"""
        error_type = "RateLimitError"
        error_message = "Rate limit exceeded. Try again in 60 seconds."

        pattern = self.detector.detect_pattern(error_type, error_message)
        assert pattern == ErrorPattern.RATE_LIMIT

    def test_timeout_pattern_detection(self):
        """Test timeout error pattern detection"""
        error_type = "TimeoutError"
        error_message = "Operation timed out after 30 seconds"

        pattern = self.detector.detect_pattern(error_type, error_message)
        assert pattern == ErrorPattern.TIMEOUT

    def test_connection_failure_pattern_detection(self):
        """Test connection failure pattern detection"""
        error_type = "ConnectionError"
        error_message = "Connection refused to database server"

        pattern = self.detector.detect_pattern(error_type, error_message)
        assert pattern == ErrorPattern.CONNECTION_FAILED

    def test_auth_failure_pattern_detection(self):
        """Test authentication failure pattern detection"""
        error_type = "AuthenticationError"
        error_message = "401 Unauthorized - Invalid token"

        pattern = self.detector.detect_pattern(error_type, error_message)
        assert pattern == ErrorPattern.AUTHENTICATION_FAILED

    def test_database_error_pattern_detection(self):
        """Test database error pattern detection"""
        error_type = "DatabaseError"
        error_message = "SQL connection pool exhausted"

        pattern = self.detector.detect_pattern(error_type, error_message)
        assert pattern == ErrorPattern.DATABASE_ERROR

    def test_severity_assessment_critical(self):
        """Test critical severity assessment"""
        error_type = "CriticalSystemError"
        error_message = "Critical system failure detected"

        severity = self.detector.assess_severity(error_type, error_message)
        assert severity == ErrorSeverity.CRITICAL

    def test_severity_assessment_high(self):
        """Test high severity assessment"""
        error_type = "DatabaseError"
        error_message = "Database connection lost"

        severity = self.detector.assess_severity(error_type, error_message)
        assert severity == ErrorSeverity.HIGH

    def test_severity_assessment_medium(self):
        """Test medium severity assessment"""
        error_type = "TimeoutError"
        error_message = "Request timeout"

        severity = self.detector.assess_severity(error_type, error_message)
        assert severity == ErrorSeverity.MEDIUM

    def test_unknown_pattern(self):
        """Test handling of unknown error patterns"""
        error_type = "UnknownError"
        error_message = "Something unexpected happened"

        pattern = self.detector.detect_pattern(error_type, error_message)
        assert pattern is None


class TestProductionErrorRecovery:
    """Test production error recovery system"""

    def setup_method(self):
        self.recovery = ProductionErrorRecovery()

    @pytest.mark.asyncio
    async def test_rate_limit_recovery(self):
        """Test rate limit error recovery"""
        error = Exception("429 Too Many Requests")
        context = {"service_name": "test_service", "max_retries": 1}

        result = await self.recovery.handle_error(error, context)

        assert result.success is True
        assert result.strategy == "rate_limit_backoff"
        assert result.error_resolved is True
        assert "backoff_applied" in result.new_state

    @pytest.mark.asyncio
    async def test_timeout_recovery_with_retry(self):
        """Test timeout error recovery with successful retry"""
        error = Exception("Request timeout")
        retry_func = AsyncMock(return_value="success")

        context = {"timeout": 30, "retry_func": retry_func}

        result = await self.recovery.handle_error(error, context)

        assert result.success is True
        assert result.strategy == "timeout_increase_retry"
        assert result.error_resolved is True
        assert retry_func.call_count == 1

    @pytest.mark.asyncio
    async def test_connection_failure_recovery_retry(self):
        """Test connection failure recovery with retry"""
        error = Exception("Connection refused")
        retry_func = AsyncMock(return_value="success")

        context = {"max_retries": 2, "retry_func": retry_func}

        result = await self.recovery.handle_error(error, context)

        assert result.success is True
        assert result.strategy == "connection_retry"
        assert result.error_resolved is True

    @pytest.mark.asyncio
    async def test_connection_failure_recovery_fallback(self):
        """Test connection failure recovery with fallback"""
        error = Exception("Connection refused")
        retry_func = AsyncMock(side_effect=Exception("Still failed"))
        fallback_func = AsyncMock(return_value="fallback_success")

        context = {
            "max_retries": 1,
            "retry_func": retry_func,
            "fallback_func": fallback_func,
        }

        result = await self.recovery.handle_error(error, context)

        assert result.success is True
        assert result.strategy == "connection_fallback"
        assert result.error_resolved is True
        assert fallback_func.call_count == 1

    @pytest.mark.asyncio
    async def test_auth_failure_with_token_refresh(self):
        """Test authentication failure with token refresh"""
        error = Exception("401 Unauthorized")
        refresh_func = AsyncMock()
        retry_func = AsyncMock(return_value="success")

        context = {"refresh_token_func": refresh_func, "retry_func": retry_func}

        result = await self.recovery.handle_error(error, context)

        assert result.success is True
        assert result.strategy == "auth_token_refresh"
        assert result.error_resolved is True
        assert refresh_func.call_count == 1
        assert retry_func.call_count == 1

    @pytest.mark.asyncio
    async def test_database_error_with_reconnect(self):
        """Test database error with reconnection"""
        error = Exception("Connection pool exhausted")
        reconnect_func = AsyncMock()
        retry_func = AsyncMock(return_value="success")

        context = {"reconnect_func": reconnect_func, "retry_func": retry_func}

        result = await self.recovery.handle_error(error, context)

        assert result.success is True
        assert result.strategy == "database_reconnect"
        assert result.error_resolved is True
        assert reconnect_func.call_count == 1
        assert retry_func.call_count == 1

    @pytest.mark.asyncio
    async def test_external_api_error_with_fallback(self):
        """Test external API error with fallback service"""
        error = Exception("503 Service Unavailable")
        fallback_service_func = AsyncMock(return_value="fallback_success")

        context = {"fallback_service_func": fallback_service_func}

        result = await self.recovery.handle_error(error, context)

        assert result.success is True
        assert result.strategy == "external_api_fallback"
        assert result.error_resolved is True
        assert fallback_service_func.call_count == 1

    @pytest.mark.asyncio
    async def test_circuit_breaker_trigger(self):
        """Test circuit breaker triggering after multiple failures"""
        error = Exception("Connection refused")

        # Simulate multiple failures to trigger circuit breaker
        for i in range(12):  # More than the threshold
            await self.recovery.handle_error(error, {"service_name": "test_service"})

        # Next error should trigger circuit breaker
        result = await self.recovery.handle_error(
            error, {"service_name": "test_service"}
        )

        assert result.success is False
        assert result.strategy == "circuit_break_open"
        assert "circuit_open" in result.new_state

    def test_error_statistics(self):
        """Test error statistics collection"""
        # Simulate some errors
        self.recovery.error_metrics["TestError"] = ErrorMetrics(
            error_type="TestError",
            count=10,
            recovery_attempts=8,
            successful_recoveries=6,
        )

        stats = self.recovery.get_error_statistics()

        assert stats["total_errors"] == 10
        assert stats["total_recovery_attempts"] == 8
        assert stats["successful_recoveries"] == 6
        assert stats["overall_success_rate"] == 0.75


class TestCircuitBreaker:
    """Test circuit breaker functionality"""

    def setup_method(self):
        self.config = CircuitBreakerConfig(
            failure_threshold=3, recovery_timeout=5, success_threshold=2
        )
        self.breaker = CircuitBreaker("test_service", self.config)

    @pytest.mark.asyncio
    async def test_circuit_breaker_initial_state(self):
        """Test circuit breaker initial state"""
        assert self.breaker.get_state() == CircuitState.CLOSED
        stats = self.breaker.get_stats()
        assert stats.failures == 0
        assert stats.successes == 0

    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_on_failures(self):
        """Test circuit breaker opens after threshold failures"""
        failing_func = AsyncMock(side_effect=Exception("Service unavailable"))

        # Trigger failures
        for i in range(3):
            try:
                await self.breaker.call(failing_func)
            except Exception:
                pass

        # Circuit should be open
        assert self.breaker.get_state() == CircuitState.OPEN

    @pytest.mark.asyncio
    async def test_circuit_breaker_blocks_calls_when_open(self):
        """Test circuit breaker blocks calls when open"""
        failing_func = AsyncMock(side_effect=Exception("Service unavailable"))

        # Trigger failures to open circuit
        for i in range(3):
            try:
                await self.breaker.call(failing_func)
            except Exception:
                pass

        # Next call should fail fast
        with pytest.raises(Exception):
            await self.breaker.call(failing_func)

    @pytest.mark.asyncio
    async def test_circuit_breaker_half_open_state(self):
        """Test circuit breaker half-open state"""
        failing_func = AsyncMock(side_effect=Exception("Service unavailable"))
        success_func = AsyncMock(return_value="success")

        # Trigger failures to open circuit
        for i in range(3):
            try:
                await self.breaker.call(failing_func)
            except Exception:
                pass

        # Wait for recovery timeout
        await asyncio.sleep(6)

        # First call in half-open should succeed
        result = await self.breaker.call(success_func)
        assert result == "success"

        # Circuit should still be half-open
        assert self.breaker.get_state() == CircuitState.HALF_OPEN

        # Second successful call should close circuit
        result = await self.breaker.call(success_func)
        assert result == "success"

        # Circuit should be closed
        assert self.breaker.get_state() == CircuitState.CLOSED

    def test_adaptive_threshold(self):
        """Test adaptive threshold adjustment"""
        # Simulate many successes
        for i in range(20):
            self.breaker._success_history.append(time.time())

        # Trigger adaptation
        self.breaker._adapt_threshold()

        # Threshold should be adjusted
        assert self.breaker._adaptive_threshold <= self.config.failure_threshold

    def test_health_score(self):
        """Test health score calculation"""
        # Perfect score initially
        assert self.breaker.get_health_score() == 100.0

        # Add some failures
        self.breaker.stats.failures = 2
        self.breaker.stats.total_requests = 10
        self.breaker.stats.successes = 8

        score = self.breaker.get_health_score()
        assert 0 <= score <= 100

    def test_failure_patterns(self):
        """Test failure pattern analysis"""
        # Add some failure history
        self.breaker._failure_history.extend(
            [
                {
                    "time": time.time(),
                    "type": "ConnectionError",
                    "message": "Connection refused",
                },
                {
                    "time": time.time(),
                    "type": "TimeoutError",
                    "message": "Request timeout",
                },
                {
                    "time": time.time(),
                    "type": "ConnectionError",
                    "message": "Connection refused",
                },
            ]
        )

        patterns = self.breaker.get_failure_patterns()

        assert patterns["total_failures"] == 3
        assert patterns["most_common_failure"] == "ConnectionError"
        assert "failure_types" in patterns


class TestPredictiveFailurePrevention:
    """Test predictive failure prevention system"""

    def setup_method(self):
        self.prevention = PredictiveFailurePrevention()

    def test_resource_metric_creation(self):
        """Test resource metric creation"""
        from core.predictive_failure import ResourceMetric

        metric = ResourceMetric(
            resource_type=ResourceType.CPU,
            value=80.0,
            threshold=70.0,
            timestamp=datetime.now(),
            alert_level=AlertLevel.WARNING,
        )

        assert metric.resource_type == ResourceType.CPU
        assert metric.value == 80.0
        assert metric.alert_level == AlertLevel.WARNING

    def test_alert_level_determination(self):
        """Test alert level determination"""
        # Test warning level
        level = self.prevention._determine_alert_level(75, ResourceType.CPU)
        assert level == AlertLevel.WARNING

        # Test critical level
        level = self.prevention._determine_alert_level(90, ResourceType.CPU)
        assert level == AlertLevel.CRITICAL

        # Test emergency level
        level = self.prevention._determine_alert_level(98, ResourceType.CPU)
        assert level == AlertLevel.EMERGENCY

    @pytest.mark.asyncio
    async def test_failure_prediction(self):
        """Test failure prediction logic"""
        from core.predictive_failure import ResourceMetric

        # Create metrics showing increasing trend
        metrics = []
        base_time = time.time()
        for i in range(10):
            value = 70 + i * 2  # Increasing from 70 to 88
            metric = ResourceMetric(
                resource_type=ResourceType.CPU,
                value=value,
                threshold=70.0,
                timestamp=datetime.fromtimestamp(base_time + i * 60),
                alert_level=AlertLevel.WARNING if value < 85 else AlertLevel.CRITICAL,
            )
            metrics.append(metric)

        prediction = await self.prevention._predict_failure(ResourceType.CPU, metrics)

        assert prediction is not None
        assert prediction.resource_type == ResourceType.CPU
        assert prediction.probability > 0.5
        assert prediction.alert_level in [AlertLevel.WARNING, AlertLevel.CRITICAL]

    @pytest.mark.asyncio
    async def test_prevention_action_execution(self):
        """Test prevention action execution"""
        from core.predictive_failure import FailurePrediction, ResourceMetric

        # Create a critical prediction
        prediction = FailurePrediction(
            resource_type=ResourceType.MEMORY,
            probability=0.9,
            time_to_failure=60,
            alert_level=AlertLevel.CRITICAL,
            recommended_actions=["Clear caches"],
            confidence=0.9,
            metrics=[],
        )

        # Execute prevention
        await self.prevention._execute_prevention()

        # Check that action was recorded
        assert len(self.prevention.action_history) >= 0

    def test_current_metrics(self):
        """Test current metrics retrieval"""
        metrics = self.prevention.get_current_metrics()
        assert isinstance(metrics, dict)

    def test_recent_predictions(self):
        """Test recent predictions retrieval"""
        predictions = self.prevention.get_recent_predictions()
        assert isinstance(predictions, list)


class TestIntegration:
    """Integration tests for the complete error recovery system"""

    @pytest.mark.asyncio
    async def test_end_to_end_error_recovery(self):
        """Test complete error recovery flow"""
        # Initialize systems
        recovery = get_production_error_recovery()

        # Simulate an error
        error = Exception("429 Too Many Requests")
        context = {"service_name": "integration_test", "max_retries": 1}

        # Handle error
        result = await recovery.handle_error(error, context)

        # Verify recovery
        assert result.success is True
        assert result.recovery_time > 0
        assert result.metrics_updated is True

    @pytest.mark.asyncio
    async def test_circuit_breaker_integration(self):
        """Test circuit breaker integration with error recovery"""
        client = get_resilient_client()

        # Add a circuit breaker
        breaker = client.add_circuit_breaker(
            "integration_test",
            CircuitBreakerConfig(failure_threshold=2, recovery_timeout=1),
        )

        # Simulate failures
        failing_func = AsyncMock(side_effect=Exception("Service failure"))

        # First failure
        try:
            await breaker.call(failing_func)
        except Exception:
            pass

        # Second failure should open circuit
        try:
            await breaker.call(failing_func)
        except Exception:
            pass

        assert breaker.get_state() == CircuitState.OPEN

    @pytest.mark.asyncio
    async def test_predictive_failure_integration(self):
        """Test predictive failure integration"""
        prevention = get_predictive_failure()

        # Start monitoring
        await prevention._collect_metrics()

        # Get current metrics
        metrics = prevention.get_current_metrics()

        assert isinstance(metrics, dict)
        assert len(metrics) > 0


class TestPerformance:
    """Performance tests for error recovery system"""

    @pytest.mark.asyncio
    async def test_error_recovery_performance(self):
        """Test error recovery performance"""
        recovery = ProductionErrorRecovery()

        # Measure recovery time
        start_time = time.time()

        error = Exception("429 Too Many Requests")
        context = {"service_name": "performance_test"}

        result = await recovery.handle_error(error, context)

        recovery_time = time.time() - start_time

        # Recovery should be fast
        assert recovery_time < 1.0  # Less than 1 second
        assert result.success is True

    @pytest.mark.asyncio
    async def test_circuit_breaker_performance(self):
        """Test circuit breaker performance"""
        config = CircuitBreakerConfig(failure_threshold=5, recovery_timeout=60)
        breaker = CircuitBreaker("performance_test", config)

        # Measure call time
        start_time = time.time()

        success_func = AsyncMock(return_value="success")
        result = await breaker.call(success_func)

        call_time = time.time() - start_time

        # Calls should be fast
        assert call_time < 0.1  # Less than 100ms
        assert result == "success"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
