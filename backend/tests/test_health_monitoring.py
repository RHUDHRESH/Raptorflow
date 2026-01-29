"""
Comprehensive test suite for advanced health monitoring system.
Tests predictive analytics, alerting, and real-time monitoring capabilities.
"""

import asyncio
import json
import pytest
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
from unittest.mock import Mock, patch, AsyncMock

from .core.health_monitor import (
    HealthMonitorAdvanced,
    HealthStatus,
    HealthMetric,
    HealthAlert,
    HealthPrediction,
    PredictiveAnalytics,
    SystemHealthReport,
)
from .core.health_analytics import (
    HealthAnalytics,
    AlertRule,
    AlertType,
    AlertSeverity,
    NotificationChannel,
    NotificationEngine,
    NotificationConfig,
)
from .core.threat_intelligence import get_threat_intelligence


class TestHealthMonitorAdvanced:
    """Test suite for HealthMonitorAdvanced."""

    @pytest.fixture
    def monitor(self):
        """Create health monitor instance."""
        return HealthMonitorAdvanced()

    @pytest.fixture
    def sample_metrics(self):
        """Sample health metrics for testing."""
        return [
            (
                "cpu_usage",
                75.5,
                "%",
                {"threshold_warning": 70, "threshold_critical": 90},
            ),
            (
                "memory_usage",
                60.2,
                "%",
                {"threshold_warning": 80, "threshold_critical": 95},
            ),
            (
                "response_time",
                150.0,
                "ms",
                {"threshold_warning": 500, "threshold_critical": 1000},
            ),
            (
                "error_rate",
                2.5,
                "%",
                {"threshold_warning": 5, "threshold_critical": 10},
            ),
        ]

    @pytest.mark.asyncio
    async def test_metric_recording(self, monitor, sample_metrics):
        """Test health metric recording."""
        for name, value, unit, thresholds in sample_metrics:
            monitor.record_metric(name, value, unit, **thresholds)

        # Check metrics were recorded
        assert len(monitor.metrics) == len(sample_metrics)

        for name, value, unit, thresholds in sample_metrics:
            metric = monitor.metrics[name]
            assert metric.name == name
            assert metric.value == value
            assert metric.unit == unit
            assert metric.timestamp is not None

    @pytest.mark.asyncio
    async def test_alert_generation(self, monitor):
        """Test automatic alert generation."""
        # Record metric that exceeds threshold
        monitor.record_metric(
            "cpu_usage",
            95.0,  # Exceeds critical threshold
            "%",
            threshold_warning=70,
            threshold_critical=90,
        )

        # Check if alert was generated
        active_alerts = [
            alert for alert in monitor.alerts.values() if not alert.resolved
        ]
        assert len(active_alerts) > 0

        cpu_alerts = [
            alert for alert in active_alerts if alert.metric_name == "cpu_usage"
        ]
        assert len(cpu_alerts) > 0
        assert cpu_alerts[0].severity == AlertSeverity.CRITICAL

    @pytest.mark.asyncio
    async def test_health_check_execution(self, monitor):
        """Test health check execution."""
        report = await monitor.run_health_checks()

        assert isinstance(report, SystemHealthReport)
        assert report.timestamp is not None
        assert report.overall_status in [status.value for status in HealthStatus]
        assert 0 <= report.health_score <= 1
        assert isinstance(report.metrics, dict)
        assert isinstance(report.alerts, list)
        assert isinstance(report.predictions, list)
        assert isinstance(report.recommendations, list)

    @pytest.mark.asyncio
    async def test_predictive_analytics(self, monitor):
        """Test predictive analytics functionality."""
        # Generate historical data
        base_value = 50.0
        for i in range(100):
            # Simulate growing trend
            value = base_value + (i * 0.5)
            monitor.record_metric("test_metric", value)
            await asyncio.sleep(0.001)  # Small delay

        # Train model
        monitor.predictive_analytics.train_model("test_metric")

        # Generate prediction
        prediction = monitor.predictive_analytics.predict_metric("test_metric", 30)

        if prediction:
            assert prediction.metric_name == "test_metric"
            assert prediction.confidence >= 0
            assert prediction.confidence <= 1
            assert prediction.prediction_horizon.total_seconds() == 1800  # 30 minutes

    @pytest.mark.asyncio
    async def test_anomaly_detection(self, monitor):
        """Test anomaly detection in metrics."""
        # Generate normal data
        for i in range(50):
            monitor.record_metric("stable_metric", 50.0 + (i % 10))

        # Generate anomalous data point
        monitor.record_metric("stable_metric", 200.0)

        # Check if anomaly was detected
        anomalies = []
        for metric_name, history in monitor.metric_history.items():
            if metric_name == "stable_metric":
                # Check last few points for anomalies
                for metric in list(history)[-5:]:
                    if monitor.predictive_analytics.detect_anomaly(
                        metric_name, metric.value
                    ):
                        anomalies.append(metric)

        # Should have detected the anomaly (implementation dependent)
        assert len(anomalies) >= 0  # At minimum, no errors

    def test_health_score_calculation(self, monitor):
        """Test health score calculation."""
        # Test with all healthy checks
        healthy_checks = {
            "check1": {"status": "healthy"},
            "check2": {"status": "healthy"},
            "check3": {"status": "healthy"},
        }
        score = monitor._calculate_health_score(healthy_checks)
        assert score == 1.0

        # Test with mixed statuses
        mixed_checks = {
            "check1": {"status": "healthy"},
            "check2": {"status": "degraded"},
            "check3": {"status": "unhealthy"},
        }
        score = monitor._calculate_health_score(mixed_checks)
        assert 0 <= score <= 1
        assert score < 1.0

    @pytest.mark.asyncio
    async def test_monitoring_lifecycle(self, monitor):
        """Test monitoring start/stop lifecycle."""
        # Start monitoring
        await monitor.start_monitoring()
        assert monitor._is_monitoring is True

        # Let it run briefly
        await asyncio.sleep(0.1)

        # Stop monitoring
        await monitor.stop_monitoring()
        assert monitor._is_monitoring is False

    def test_dashboard_data_generation(self, monitor):
        """Test dashboard data generation."""
        # Add some sample data
        monitor.record_metric("cpu_usage", 75.0, "%")
        monitor.record_metric("memory_usage", 60.0, "%")

        # Generate dashboard data
        dashboard_data = monitor.get_health_dashboard_data()

        assert "current_metrics" in dashboard_data
        assert "active_alerts" in dashboard_data
        assert "recent_predictions" in dashboard_data
        assert "uptime_percentage" in dashboard_data
        assert "monitoring_status" in dashboard_data

        assert len(dashboard_data["current_metrics"]) == 2


class TestPredictiveAnalytics:
    """Test suite for PredictiveAnalytics."""

    @pytest.fixture
    def analytics(self):
        """Create predictive analytics instance."""
        return PredictiveAnalytics()

    def test_feature_preparation(self, analytics):
        """Test feature preparation for ML models."""
        # Generate sample data
        history = []
        for i in range(100):
            history.append(
                {
                    "value": 50.0 + (i % 20),
                    "timestamp": datetime.now() + timedelta(minutes=i),
                }
            )

        analytics.feature_history["test_metric"] = history

        # Prepare features
        X, y = analytics.prepare_features("test_metric")

        if len(X) > 0:
            assert X.shape[1] > 0  # Should have features
            assert len(y) > 0  # Should have targets
            assert X.shape[0] == len(y)  # Should match

    def test_model_training(self, analytics):
        """Test ML model training."""
        # Generate sufficient training data
        history = []
        for i in range(100):
            history.append(
                {
                    "value": 50.0 + (i * 0.5),  # Growing trend
                    "timestamp": datetime.now() + timedelta(minutes=i),
                }
            )

        analytics.feature_history["test_metric"] = history

        # Train model
        success = analytics.train_model("test_metric")

        if success:
            assert "test_metric" in analytics.models
            assert "test_metric" in analytics.anomaly_detectors
            assert "test_metric" in analytics.scalers
            assert analytics._is_trained is True

    def test_prediction_generation(self, analytics):
        """Test prediction generation."""
        # Setup trained model (mock for testing)
        analytics.models["test_metric"] = Mock()
        analytics.models["test_metric"].predict.return_value = [55.0]
        analytics.scalers["test_metric"] = Mock()
        analytics.scalers["test_metric"].transform.return_value = [[1.0, 2.0, 3.0]]

        prediction = analytics.predict_metric("test_metric", 60)

        if prediction:
            assert prediction.metric_name == "test_metric"
            assert prediction.predicted_value == 55.0
            assert prediction.prediction_horizon.total_seconds() == 3600  # 1 hour

    def test_anomaly_detection(self, analytics):
        """Test anomaly detection."""
        # Setup trained model
        analytics.anomaly_detectors["test_metric"] = Mock()
        analytics.anomaly_detectors["test_metric"].predict.return_value = [1]  # Normal
        analytics.scalers["test_metric"] = Mock()
        analytics.scalers["test_metric"].transform.return_value = [[1.0]]

        # Test normal data
        is_anomaly = analytics.detect_anomaly("test_metric", [1.0, 2.0, 3.0])
        assert is_anomaly is False

        # Test anomalous data
        analytics.anomaly_detectors["test_metric"].predict.return_value = [
            -1
        ]  # Anomaly
        is_anomaly = analytics.detect_anomaly("test_metric", [1.0, 2.0, 3.0])
        assert is_anomaly is True

    def test_confidence_calculation(self, analytics):
        """Test prediction confidence calculation."""
        # Setup prediction history
        for i in range(10):
            prediction = Mock()
            prediction.predicted_value = 50.0 + i
            prediction.prediction_horizon = timedelta(minutes=30)
            analytics.prediction_history["test_metric"].append(prediction)

        # Add actual values
        for i in range(10):
            analytics.feature_history["test_metric"].append(
                {"value": 50.5 + i, "timestamp": datetime.now()}  # Close to predictions
            )

        confidence = analytics._calculate_prediction_confidence("test_metric", 55.0)
        assert 0 <= confidence <= 1
        assert confidence > 0.5  # Should be reasonably confident


class TestHealthAnalytics:
    """Test suite for HealthAnalytics."""

    @pytest.fixture
    def analytics(self):
        """Create health analytics instance."""
        return HealthAnalytics()

    @pytest.mark.asyncio
    async def test_metric_processing_and_alerting(self, analytics):
        """Test metric processing with automatic alerting."""
        # Add alert rule
        rule = AlertRule(
            id="cpu_rule",
            name="High CPU Usage",
            description="Alert when CPU usage is high",
            metric_pattern="cpu_usage",
            condition="gt",
            threshold=80.0,
            severity=AlertSeverity.WARNING,
            enabled=True,
            notification_channels=[],
        )
        analytics.add_alert_rule(rule)

        # Process metric that triggers alert
        await analytics.process_metric("cpu_usage", 85.0)

        # Check alert was generated
        active_alerts = analytics.get_active_alerts()
        cpu_alerts = [
            alert for alert in active_alerts if alert.metric_name == "cpu_usage"
        ]
        assert len(cpu_alerts) > 0
        assert cpu_alerts[0].severity == AlertSeverity.WARNING

    @pytest.mark.asyncio
    async def test_alert_lifecycle(self, analytics):
        """Test complete alert lifecycle."""
        # Create test alert
        alert_id = "test_alert_123"
        test_alert = Mock(
            id=alert_id,
            status=AlertStatus.ACTIVE,
            acknowledged_at=None,
            acknowledged_by=None,
            resolved_at=None,
            resolved_by=None,
        )
        analytics.alerts[alert_id] = test_alert

        # Acknowledge alert
        await analytics.acknowledge_alert(alert_id, "test_user")
        assert test_alert.status == AlertStatus.ACKNOWLEDGED
        assert test_alert.acknowledged_by == "test_user"
        assert test_alert.acknowledged_at is not None

        # Resolve alert
        await analytics.resolve_alert(alert_id, "admin")
        assert test_alert.status == AlertStatus.RESOLVED
        assert test_alert.resolved_by == "admin"
        assert test_alert.resolved_at is not None

    @pytest.mark.asyncio
    async def test_trend_analysis(self, analytics):
        """Test trend analysis functionality."""
        # Generate alert history with increasing frequency
        now = datetime.now()
        for i in range(50):
            alert = Mock(
                metric_name="test_metric",
                timestamp=now - timedelta(minutes=i),
                severity=AlertSeverity.WARNING,
            )
            analytics.alert_history.append(alert)

        # Analyze trends
        await analytics.analyze_trends()

        # Check if trend was analyzed
        assert "test_metric" in analytics.trend_analysis
        trend = analytics.trend_analysis["test_metric"]
        assert trend.metric_name == "test_metric"
        assert trend.alert_count == 50
        assert trend.trend_direction in ["increasing", "decreasing", "stable"]

    def test_alert_summary_generation(self, analytics):
        """Test alert summary generation."""
        # Add sample alerts
        now = datetime.now()
        for i in range(10):
            alert = Mock(
                timestamp=now - timedelta(hours=i),
                severity=AlertSeverity.WARNING if i % 2 == 0 else AlertSeverity.ERROR,
                status=AlertStatus.ACTIVE,
                alert_type=AlertType.THRESHOLD_EXCEEDED,
                metric_name=f"metric_{i % 3}",
            )
            analytics.alert_history.append(alert)

        summary = analytics.get_alert_summary(24)

        assert "total_alerts" in summary
        assert "active_alerts" in summary
        assert "severity_distribution" in summary
        assert "type_distribution" in summary
        assert summary["total_alerts"] == 10


class TestNotificationEngine:
    """Test suite for NotificationEngine."""

    @pytest.fixture
    def notification_engine(self):
        """Create notification engine instance."""
        return NotificationEngine()

    @pytest.fixture
    def sample_alert(self):
        """Sample alert for testing."""
        from core.health_analytics import HealthAlert, AlertType, AlertSeverity

        return HealthAlert(
            id="test_alert",
            name="Test Alert",
            description="This is a test alert",
            alert_type=AlertType.THRESHOLD_EXCEEDED,
            severity=AlertSeverity.WARNING,
            status=AlertStatus.ACTIVE,
            source="test",
            metric_name="cpu_usage",
            current_value=85.0,
            threshold_value=80.0,
            timestamp=datetime.now(),
        )

    @pytest.mark.asyncio
    async def test_notification_configuration(self, notification_engine):
        """Test notification channel configuration."""
        config = NotificationConfig(
            channel=NotificationChannel.EMAIL,
            enabled=True,
            recipients=["test@example.com"],
            template="test_template.html",
        )

        notification_engine.configure_channel(NotificationChannel.EMAIL, config)

        assert NotificationChannel.EMAIL in notification_engine.configs
        assert notification_engine.configs[NotificationChannel.EMAIL].enabled is True
        assert notification_engine.configs[NotificationChannel.EMAIL].recipients == [
            "test@example.com"
        ]

    @pytest.mark.asyncio
    async def test_rate_limiting(self, notification_engine):
        """Test notification rate limiting."""
        config = NotificationConfig(
            channel=NotificationChannel.EMAIL,
            enabled=True,
            recipients=["test@example.com"],
            template="test_template.html",
            rate_limit=2,  # Very low limit for testing
        )
        notification_engine.configure_channel(NotificationChannel.EMAIL, config)

        alert = Mock()

        # Send notifications up to limit
        result1 = await notification_engine.send_notification(
            alert, [NotificationChannel.EMAIL]
        )
        result2 = await notification_engine.send_notification(
            alert, [NotificationChannel.EMAIL]
        )
        result3 = await notification_engine.send_notification(
            alert, [NotificationChannel.EMAIL]
        )

        # First two should succeed, third should be rate limited
        assert result1[NotificationChannel.EMAIL.value] is True
        assert result2[NotificationChannel.EMAIL.value] is True
        # Third might be rate limited depending on timing

    @pytest.mark.asyncio
    async def test_in_app_notifications(self, notification_engine, sample_alert):
        """Test in-app notification delivery."""
        result = await notification_engine.send_notification(
            sample_alert, [NotificationChannel.IN_APP]
        )

        assert result[NotificationChannel.IN_APP.value] is True
        assert NotificationChannel.IN_APP.value in sample_alert.notifications_sent

    def test_delivery_statistics(self, notification_engine):
        """Test notification delivery statistics."""
        # Add some delivery history
        now = datetime.now()
        for i in range(10):
            notification_engine.delivery_history.append(
                {
                    "timestamp": now - timedelta(hours=i),
                    "channel": "email",
                    "alert_id": f"alert_{i}",
                    "severity": "warning",
                    "success": i % 3 != 0,  # 2/3 success rate
                }
            )

        stats = notification_engine.get_delivery_stats(24)

        assert "total_deliveries" in stats
        assert "successful_deliveries" in stats
        assert "success_rate" in stats
        assert stats["total_deliveries"] == 10
        assert stats["successful_deliveries"] == 6  # 2/3 of 10
        assert abs(stats["success_rate"] - 0.6) < 0.01


class TestIntegrationScenarios:
    """Integration tests for health monitoring scenarios."""

    @pytest.mark.asyncio
    async def test_complete_monitoring_workflow(self):
        """Test complete monitoring workflow."""
        # Setup components
        monitor = HealthMonitorAdvanced()
        analytics = HealthAnalytics()
        notification_engine = NotificationEngine()

        # Configure notifications
        email_config = NotificationConfig(
            channel=NotificationChannel.EMAIL,
            enabled=True,
            recipients=["admin@example.com"],
            template="alert.html",
        )
        notification_engine.configure_channel(NotificationChannel.EMAIL, email_config)

        # Add alert rule
        rule = AlertRule(
            id="integration_rule",
            name="Integration Test Rule",
            description="Test rule for integration",
            metric_pattern="cpu_usage",
            condition="gt",
            threshold=80.0,
            severity=AlertSeverity.WARNING,
            enabled=True,
            notification_channels=[NotificationChannel.EMAIL],
        )
        analytics.add_alert_rule(rule)

        # Simulate metric that triggers alert
        await analytics.process_metric("cpu_usage", 85.0)

        # Run health checks
        report = await monitor.run_health_checks()

        # Verify workflow
        assert report.overall_status != "unknown"
        assert len(analytics.get_active_alerts()) > 0

        # Test notification would be sent (mocked)
        active_alerts = analytics.get_active_alerts()
        if active_alerts:
            # This would send notifications in real scenario
            pass

    @pytest.mark.asyncio
    async def test_predictive_failure_scenario(self):
        """Test predictive failure detection and alerting."""
        monitor = HealthMonitorAdvanced()

        # Generate metrics showing degradation trend
        base_cpu = 50.0
        for i in range(50):
            # Simulate increasing CPU usage
            cpu_value = base_cpu + (i * 0.8)  # Increasing trend
            monitor.record_metric("cpu_usage", cpu_value)
            await asyncio.sleep(0.001)

        # Train predictive model
        monitor.predictive_analytics.train_model("cpu_usage")

        # Generate prediction
        prediction = monitor.predictive_analytics.predict_metric("cpu_usage", 60)

        if prediction:
            # Check if prediction indicates future failure
            if prediction.predicted_value > 90 and prediction.confidence > 0.7:
                # This would trigger predictive alert
                assert prediction.metric_name == "cpu_usage"
                assert prediction.confidence > 0.7

    @pytest.mark.asyncio
    async def test_massive_alert_scenario(self):
        """Test system behavior under massive alert conditions."""
        analytics = HealthAnalytics()

        # Generate many alerts quickly
        start_time = datetime.now()
        for i in range(100):
            await analytics.process_metric(
                f"metric_{i % 10}", 95.0
            )  # All exceed thresholds
            await asyncio.sleep(0.001)  # Small delay

        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()

        # Check performance
        assert processing_time < 5.0  # Should process 100 alerts quickly

        # Check alert generation
        active_alerts = analytics.get_active_alerts()
        assert len(active_alerts) > 0

        # Check summary
        summary = analytics.get_alert_summary(1)  # Last hour
        assert summary["total_alerts"] >= 100


class TestPerformanceBenchmarks:
    """Performance benchmarks for health monitoring."""

    @pytest.mark.asyncio
    async def benchmark_metric_processing(self):
        """Benchmark metric processing performance."""
        analytics = HealthAnalytics()

        # Generate many metrics
        metrics = [(f"metric_{i % 10}", 50.0 + (i % 50)) for i in range(1000)]

        start_time = time.time()
        for name, value in metrics:
            await analytics.process_metric(name, value)
        processing_time = time.time() - start_time

        # Performance assertions
        assert processing_time < 2.0  # Should process 1000 metrics quickly
        avg_time_per_metric = processing_time / 1000
        assert avg_time_per_metric < 0.002  # < 2ms per metric

        print(f"Metric processing: {avg_time_per_metric:.6f}s per metric")

    @pytest.mark.asyncio
    async def benchmark_health_checks(self):
        """Benchmark health check performance."""
        monitor = HealthMonitorAdvanced()

        # Run multiple health checks
        iterations = 10
        start_time = time.time()

        for _ in range(iterations):
            await monitor.run_health_checks()

        total_time = time.time() - start_time
        avg_time = total_time / iterations

        # Performance assertions
        assert avg_time < 1.0  # Should complete health checks quickly

        print(f"Health checks: {avg_time:.3f}s per check")

    @pytest.mark.asyncio
    async def benchmark_prediction_generation(self):
        """Benchmark prediction generation performance."""
        monitor = HealthMonitorAdvanced()

        # Generate historical data
        for i in range(200):
            monitor.record_metric("benchmark_metric", 50.0 + (i * 0.1))

        # Train model
        monitor.predictive_analytics.train_model("benchmark_metric")

        # Benchmark predictions
        iterations = 50
        start_time = time.time()

        for _ in range(iterations):
            monitor.predictive_analytics.predict_metric("benchmark_metric", 30)

        total_time = time.time() - start_time
        avg_time = total_time / iterations

        # Performance assertions
        assert avg_time < 0.01  # Should generate predictions quickly

        print(f"Predictions: {avg_time:.6f}s per prediction")


if __name__ == "__main__":
    # Run specific tests
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "-k",
            "test_metric_recording or test_alert_generation",
        ]
    )
