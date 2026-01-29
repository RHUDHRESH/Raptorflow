"""
Comprehensive test suite for metrics collection system.
Tests metrics collection, aggregation, alerting, and analytics.
"""

import asyncio
import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

from .core.metrics_collector import (
    MetricsCollector,
    MetricDefinition,
    MetricCategory,
    MetricType,
    AggregationMethod,
    MetricValue,
    MetricAggregation,
    AlertRule,
    MetricAlert,
    get_metrics_collector,
)


class TestMetricsCollector:
    """Test cases for MetricsCollector."""

    @pytest.fixture
    async def metrics_collector(self):
        """Create a metrics collector for testing."""
        collector = MetricsCollector(max_values=1000, aggregation_interval=1)
        await collector.start()
        yield collector
        await collector.stop()

    @pytest.mark.asyncio
    async def test_define_metric(self, metrics_collector):
        """Test metric definition."""
        metric_def = MetricDefinition(
            name="test_metric",
            category=MetricCategory.PERFORMANCE,
            metric_type=MetricType.GAUGE,
            unit="ms",
            description="Test metric for unit testing",
            aggregation_methods=[AggregationMethod.AVERAGE, AggregationMethod.MAX],
            tags={"test": "true"},
        )

        metrics_collector.define_metric(metric_def)

        assert "test_metric" in metrics_collector.metric_definitions
        assert metrics_collector.metric_definitions["test_metric"].name == "test_metric"
        assert (
            metrics_collector.metric_definitions["test_metric"].category
            == MetricCategory.PERFORMANCE
        )

    @pytest.mark.asyncio
    async def test_record_metric(self, metrics_collector):
        """Test metric recording."""
        # Record a metric
        success = metrics_collector.record_metric(
            metric_name="test_counter",
            value=42,
            tags={"source": "test"},
            metadata={"extra": "data"},
        )

        assert success is True
        assert len(metrics_collector.metric_values["test_counter"]) == 1

        metric_value = metrics_collector.metric_values["test_counter"][0]
        assert metric_value.value == 42
        assert metric_value.tags["source"] == "test"
        assert metric_value.metadata["extra"] == "data"

    @pytest.mark.asyncio
    async def test_increment_counter(self, metrics_collector):
        """Test counter increment."""
        # Increment counter
        metrics_collector.increment_counter("test_counter", 5)
        metrics_collector.increment_counter("test_counter", 3)

        values = list(metrics_collector.metric_values["test_counter"])
        assert len(values) == 2
        assert values[0].value == 5
        assert values[1].value == 8  # 5 + 3

    @pytest.mark.asyncio
    async def test_set_gauge(self, metrics_collector):
        """Test gauge setting."""
        # Set gauge values
        metrics_collector.set_gauge("test_gauge", 100)
        metrics_collector.set_gauge("test_gauge", 250)

        values = list(metrics_collector.metric_values["test_gauge"])
        assert len(values) == 2
        assert values[0].value == 100
        assert values[1].value == 250

    @pytest.mark.asyncio
    async def test_record_timer(self, metrics_collector):
        """Test timer recording."""
        # Record timer values
        metrics_collector.record_timer("test_timer", 150.5)
        metrics_collector.record_timer("test_timer", 200.0)

        values = list(metrics_collector.metric_values["test_timer"])
        assert len(values) == 2
        assert values[0].value == 150.5
        assert values[1].value == 200.0

    @pytest.mark.asyncio
    async def test_alert_rule_creation(self, metrics_collector):
        """Test alert rule creation and evaluation."""
        # Create an alert rule
        alert_rule = AlertRule(
            name="test_alert",
            metric_name="test_threshold",
            condition="gt",
            threshold=100.0,
            duration_seconds=60,
            severity="warning",
            tags={"test": "true"},
        )

        metrics_collector.add_alert_rule(alert_rule)

        assert "test_alert" in metrics_collector.alert_rules
        assert metrics_collector.alert_rules["test_alert"].threshold == 100.0

    @pytest.mark.asyncio
    async def test_alert_triggering(self, metrics_collector):
        """Test alert triggering when threshold is exceeded."""
        # Create alert rule
        alert_rule = AlertRule(
            name="threshold_alert",
            metric_name="test_metric",
            condition="gt",
            threshold=50.0,
            duration_seconds=1,  # Short duration for testing
            severity="warning",
        )
        metrics_collector.add_alert_rule(alert_rule)

        # Record metric below threshold (should not trigger)
        metrics_collector.record_metric("test_metric", 25.0)
        await asyncio.sleep(0.1)  # Allow alert evaluation
        assert len(metrics_collector.active_alerts) == 0

        # Record metric above threshold (should trigger)
        metrics_collector.record_metric("test_metric", 75.0)
        await asyncio.sleep(0.1)  # Allow alert evaluation

        assert len(metrics_collector.active_alerts) == 1
        alert = list(metrics_collector.active_alerts.values())[0]
        assert alert.metric_name == "test_metric"
        assert alert.current_value == 75.0
        assert alert.threshold == 50.0

    @pytest.mark.asyncio
    async def test_metric_aggregation(self, metrics_collector):
        """Test metric aggregation computation."""
        # Define metric with aggregation
        metric_def = MetricDefinition(
            name="agg_test",
            category=MetricCategory.PERFORMANCE,
            metric_type=MetricType.HISTOGRAM,
            unit="ms",
            description="Aggregation test metric",
            aggregation_methods=[AggregationMethod.AVERAGE, AggregationMethod.P95],
        )
        metrics_collector.define_metric(metric_def)

        # Record multiple values
        test_values = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        for value in test_values:
            metrics_collector.record_metric("agg_test", value)

        # Trigger aggregation
        await metrics_collector._compute_aggregations()

        # Check aggregations
        aggregations = metrics_collector.metric_aggregations["agg_test"]
        assert len(aggregations) > 0

        # Find average aggregation
        avg_agg = next(
            (
                a
                for a in aggregations
                if a.aggregation_method == AggregationMethod.AVERAGE
            ),
            None,
        )
        assert avg_agg is not None
        assert abs(avg_agg.value - sum(test_values) / len(test_values)) < 0.01

    @pytest.mark.asyncio
    async def test_percentile_calculation(self, metrics_collector):
        """Test percentile calculation."""
        test_values = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

        # Test percentiles
        p50 = metrics_collector._percentile(test_values, 50)
        p95 = metrics_collector._percentile(test_values, 95)
        p99 = metrics_collector._percentile(test_values, 99)

        assert p50 == 55  # Median of even number of values
        assert p95 == 95
        assert p99 == 100

    @pytest.mark.asyncio
    async def test_system_metrics_collection(self, metrics_collector):
        """Test system metrics collection."""
        # Trigger system metrics collection
        await metrics_collector._collect_system_metrics()

        # Check if system metrics were recorded
        assert "system_cpu_percent" in metrics_collector.metric_values
        assert "system_memory_percent" in metrics_collector.metric_values
        assert "system_disk_usage_percent" in metrics_collector.metric_values

    @pytest.mark.asyncio
    async def test_metrics_cleanup(self, metrics_collector):
        """Test old metrics cleanup."""
        # Record old metric (simulate old timestamp)
        old_timestamp = datetime.now() - timedelta(days=2)
        with patch("datetime.datetime") as mock_datetime:
            mock_datetime.now.return_value = old_timestamp
            metrics_collector.record_metric("old_metric", 100)

        # Record recent metric
        metrics_collector.record_metric("recent_metric", 200)

        # Trigger cleanup
        await metrics_collector._cleanup_old_data()

        # Check that old metric was cleaned up
        values = list(metrics_collector.metric_values.get("old_metric", []))
        assert len(values) == 0

        # Recent metric should still exist
        recent_values = list(metrics_collector.metric_values.get("recent_metric", []))
        assert len(recent_values) == 1

    @pytest.mark.asyncio
    async def test_metrics_summary(self, metrics_collector):
        """Test metrics summary generation."""
        # Record various metrics
        metrics_collector.record_metric("metric1", 10)
        metrics_collector.record_metric("metric2", 20)
        metrics_collector.record_metric("metric1", 30)

        summary = metrics_collector.get_metrics_summary()

        assert summary["total_metrics"] >= 2  # At least metric1 and metric2
        assert summary["total_values"] >= 3  # At least 3 recorded values
        assert "collection_stats" in summary
        assert summary["collection_stats"]["total_metrics_collected"] >= 3

    @pytest.mark.asyncio
    async def test_get_metric_values_with_filters(self, metrics_collector):
        """Test retrieving metric values with filters."""
        # Record metrics with different tags
        now = datetime.now()
        old_time = now - timedelta(hours=2)

        with patch("datetime.datetime") as mock_datetime:
            mock_datetime.now.return_value = old_time
            metrics_collector.record_metric(
                "filtered_metric", 100, tags={"env": "test"}
            )

        metrics_collector.record_metric("filtered_metric", 200, tags={"env": "prod"})

        # Test filtering by tags
        test_values = metrics_collector.get_metric_values(
            "filtered_metric", tags={"env": "test"}
        )

        assert len(test_values) == 1
        assert test_values[0]["value"] == 100
        assert test_values[0]["tags"]["env"] == "test"

        # Test filtering by time range
        recent_values = metrics_collector.get_metric_values(
            "filtered_metric", start_time=now - timedelta(hours=1)
        )

        assert len(recent_values) == 1
        assert recent_values[0]["value"] == 200


class TestMetricDefinitions:
    """Test cases for metric definitions."""

    def test_metric_definition_creation(self):
        """Test metric definition creation and validation."""
        metric_def = MetricDefinition(
            name="comprehensive_test",
            category=MetricCategory.BUSINESS,
            metric_type=MetricType.COUNTER,
            unit="count",
            description="Comprehensive test metric",
            aggregation_methods=[
                AggregationMethod.SUM,
                AggregationMethod.AVERAGE,
                AggregationMethod.P95,
            ],
            tags={"test": "comprehensive"},
            enabled=True,
        )

        assert metric_def.name == "comprehensive_test"
        assert metric_def.category == MetricCategory.BUSINESS
        assert metric_def.metric_type == MetricType.COUNTER
        assert metric_def.unit == "count"
        assert len(metric_def.aggregation_methods) == 3
        assert metric_def.enabled is True

    def test_metric_definition_serialization(self):
        """Test metric definition serialization."""
        metric_def = MetricDefinition(
            name="serialization_test",
            category=MetricCategory.SYSTEM,
            metric_type=MetricType.GAUGE,
            unit="percent",
            description="Serialization test metric",
        )

        metric_dict = metric_def.to_dict()

        assert metric_dict["name"] == "serialization_test"
        assert metric_dict["category"] == "system"
        assert metric_dict["metric_type"] == "gauge"
        assert metric_dict["unit"] == "percent"
        assert "aggregation_methods" in metric_dict
        assert "tags" in metric_dict


class TestAlertSystem:
    """Test cases for alert system."""

    @pytest.mark.asyncio
    async def test_alert_rule_conditions(self):
        """Test different alert rule conditions."""
        collector = MetricsCollector()

        # Test different conditions
        conditions = ["gt", "lt", "eq", "gte", "lte"]

        for condition in conditions:
            alert_rule = AlertRule(
                name=f"test_{condition}",
                metric_name="test_metric",
                condition=condition,
                threshold=50.0,
                duration_seconds=60,
            )
            collector.add_alert_rule(alert_rule)

            # Test condition evaluation
            assert collector._check_condition(75.0, condition, 50.0) == (
                condition in ["gt", "gte"]
            )
            assert collector._check_condition(25.0, condition, 50.0) == (
                condition in ["lt", "lte"]
            )
            assert collector._check_condition(50.0, condition, 50.0) == (
                condition == "eq"
            )

    @pytest.mark.asyncio
    async def test_alert_resolution(self):
        """Test alert resolution when condition is no longer met."""
        collector = MetricsCollector()
        await collector.start()

        try:
            # Create alert rule
            alert_rule = AlertRule(
                name="resolution_test",
                metric_name="test_metric",
                condition="gt",
                threshold=50.0,
                duration_seconds=1,
            )
            collector.add_alert_rule(alert_rule)

            # Trigger alert
            collector.record_metric("test_metric", 75.0)
            await asyncio.sleep(0.1)

            assert len(collector.active_alerts) == 1

            # Resolve alert (record value below threshold)
            collector.record_metric("test_metric", 25.0)
            await asyncio.sleep(0.1)

            assert len(collector.active_alerts) == 0
            assert len(collector.alert_history) == 1

            alert = collector.alert_history[0]
            assert alert.resolved is True
            assert alert.resolved_at is not None

        finally:
            await collector.stop()

    @pytest.mark.asyncio
    async def test_alert_history_management(self):
        """Test alert history management."""
        collector = MetricsCollector(max_values=10)  # Small limit for testing
        await collector.start()

        try:
            # Create alert rule
            alert_rule = AlertRule(
                name="history_test",
                metric_name="test_metric",
                condition="gt",
                threshold=50.0,
                duration_seconds=1,
            )
            collector.add_alert_rule(alert_rule)

            # Trigger multiple alerts
            for i in range(15):  # More than max_values
                collector.record_metric("test_metric", 75.0)
                collector.record_metric("test_metric", 25.0)  # Resolve
                await asyncio.sleep(0.05)

            # Check history management
            assert len(collector.alert_history) <= 10  # Should not exceed max

        finally:
            await collector.stop()


class TestMetricsPerformance:
    """Performance tests for metrics collection."""

    @pytest.mark.asyncio
    async def test_high_volume_metrics(self):
        """Test performance with high volume of metrics."""
        collector = MetricsCollector(max_values=10000)
        await collector.start()

        try:
            # Record many metrics
            start_time = time.time()
            metric_count = 5000

            for i in range(metric_count):
                collector.record_metric(f"perf_metric_{i % 10}", i)

            recording_time = time.time() - start_time

            # Should complete quickly
            assert recording_time < 5.0  # 5 seconds for 5000 metrics

            total_values = sum(
                len(values) for values in collector.metric_values.values()
            )
            assert total_values == metric_count

        finally:
            await collector.stop()

    @pytest.mark.asyncio
    async def test_concurrent_metrics_operations(self):
        """Test concurrent metric operations."""
        collector = MetricsCollector()
        await collector.start()

        try:
            # Record metrics concurrently
            async def record_metrics(start_id, count):
                for i in range(count):
                    collector.record_metric(f"concurrent_metric_{start_id + i}", i)

            # Start multiple concurrent tasks
            tasks = [
                record_metrics(0, 100),
                record_metrics(100, 100),
                record_metrics(200, 100),
                record_metrics(300, 100),
            ]

            start_time = time.time()
            await asyncio.gather(*tasks)
            concurrent_time = time.time() - start_time

            # Should complete efficiently
            assert concurrent_time < 2.0  # 2 seconds for 400 concurrent metrics

            total_values = sum(
                len(values) for values in collector.metric_values.values()
            )
            assert total_values == 400

        finally:
            await collector.stop()


class TestGlobalMetricsCollector:
    """Test cases for global metrics collector."""

    @pytest.mark.asyncio
    async def test_global_collector_singleton(self):
        """Test that global metrics collector is a singleton."""
        collector1 = get_metrics_collector()
        collector2 = get_metrics_collector()

        assert collector1 is collector2

    @pytest.mark.asyncio
    async def test_global_collector_lifecycle(self):
        """Test global collector start/stop lifecycle."""
        collector = get_metrics_collector()

        # Start should be idempotent
        await collector.start()
        await collector.start()
        assert collector._running is True

        # Stop should work
        await collector.stop()
        assert collector._running is False


# Integration Tests


class TestMetricsIntegration:
    """Integration tests for metrics system."""

    @pytest.mark.asyncio
    async def test_end_to_end_metrics_flow(self):
        """Test complete metrics flow from recording to alerting."""
        collector = MetricsCollector(aggregation_interval=1)
        await collector.start()

        try:
            # 1. Define metric with alert rule
            metric_def = MetricDefinition(
                name="integration_test",
                category=MetricCategory.PERFORMANCE,
                metric_type=MetricType.GAUGE,
                unit="ms",
                description="Integration test metric",
            )
            collector.define_metric(metric_def)

            alert_rule = AlertRule(
                name="integration_alert",
                metric_name="integration_test",
                condition="gt",
                threshold=100.0,
                duration_seconds=2,
                severity="warning",
            )
            collector.add_alert_rule(alert_rule)

            # 2. Record metrics (below and above threshold)
            collector.record_metric("integration_test", 50.0)  # Below threshold
            await asyncio.sleep(0.1)
            assert len(collector.active_alerts) == 0

            collector.record_metric("integration_test", 150.0)  # Above threshold
            await asyncio.sleep(0.1)
            assert len(collector.active_alerts) == 1

            # 3. Wait for aggregation
            await asyncio.sleep(1.1)  # Wait for aggregation interval

            # 4. Check aggregations were computed
            aggregations = collector.metric_aggregations.get("integration_test", [])
            assert len(aggregations) > 0

            # 5. Get summary
            summary = collector.get_metrics_summary()
            assert summary["total_metrics"] >= 1
            assert summary["total_alerts_triggered"] >= 1

        finally:
            await collector.stop()

    @pytest.mark.asyncio
    async def test_metrics_with_background_processing(self):
        """Test metrics with background aggregation and alerting."""
        collector = MetricsCollector(aggregation_interval=0.5, max_values=100)
        await collector.start()

        try:
            # Record metrics that should trigger processing
            for i in range(10):
                collector.record_metric(f"bg_test_{i}", i * 10)
                await asyncio.sleep(0.1)  # Allow background processing

            # Wait for background tasks
            await asyncio.sleep(1.0)

            # Check that background processing occurred
            assert collector.collection_stats["total_aggregations_computed"] > 0
            assert len(collector.metric_values) <= 100  # Should respect max_values

        finally:
            await collector.stop()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
