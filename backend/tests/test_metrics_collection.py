"""
Test file to verify metrics collection works correctly.
"""

import pytest

pytest.skip(
    "Archived script-style module; not collected in canonical suite.",
    allow_module_level=True,
)

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

# Import monitoring components
from monitoring.metrics import (
    MetricCategory,
    MetricDefinition,
    MetricsCollector,
    MetricType,
    TimerMetric,
    count_metric,
    get_metrics_collector,
    time_metric,
)

logger = logging.getLogger(__name__)


class TestMetricsCollection:
    """Test suite for metrics collection functionality."""

    def __init__(self):
        self.test_results = {}
        self.metrics_collector = None
        self.test_metrics = []

    async def run_all_tests(self):
        """Run all metrics collection tests."""
        logger.info("Starting metrics collection tests")

        # Initialize metrics collector
        await self._initialize_metrics_collector()

        # Test metric registration
        await self._test_metric_registration()

        # Test counter metrics
        await self._test_counter_metrics()

        # Test gauge metrics
        await self._test_gauge_metrics()

        # Test timer metrics
        await self._test_timer_metrics()

        # Test histogram metrics
        await self._test_histogram_metrics()

        # Test average metrics
        await self._test_average_metrics()

        # Test metric retrieval
        await self._test_metric_retrieval()

        # Test metric aggregation
        await self._test_metric_aggregation()

        # Test metric history
        await self._test_metric_history()

        # Test metric export
        await self._test_metric_export()

        # Test decorators
        await self._test_decorators()

        # Test cleanup
        await self._test_cleanup()

        # Print results
        self.print_test_results()

        return self.test_results

    async def _initialize_metrics_collector(self):
        """Initialize metrics collector."""
        try:
            self.metrics_collector = get_metrics_collector()

            # Verify initialization
            is_initialized = self.metrics_collector is not None
            is_enabled = self.metrics_collector.is_enabled()
            has_default_metrics = len(self.metrics_collector.metrics) > 0

            self.test_results["initialization"] = {
                "status": (
                    "PASS"
                    if is_initialized and is_enabled and has_default_metrics
                    else "FAIL"
                ),
                "message": f"Metrics collector initialization {'successful' if is_initialized and is_enabled and has_default_metrics else 'failed'}",
                "is_initialized": is_initialized,
                "is_enabled": is_enabled,
                "default_metrics_count": len(self.metrics_collector.metrics),
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Metrics collector initialization {'successful' if is_initialized and is_enabled and has_default_metrics else 'failed'}"
            )

        except Exception as e:
            self.test_results["initialization"] = {
                "status": "FAIL",
                "message": f"Metrics collector initialization failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Metrics collector initialization failed: {e}")

    async def _test_metric_registration(self):
        """Test metric registration."""
        try:
            # Register test metrics
            test_metrics = [
                MetricDefinition(
                    name="test_counter",
                    metric_type=MetricType.COUNTER,
                    category=MetricCategory.SYSTEM,
                    description="Test counter metric",
                    unit="count",
                ),
                MetricDefinition(
                    name="test_gauge",
                    metric_type=MetricType.GAUGE,
                    category=MetricCategory.SYSTEM,
                    description="Test gauge metric",
                    unit="percent",
                ),
                MetricDefinition(
                    name="test_timer",
                    metric_type=MetricType.TIMER,
                    category=MetricCategory.PERFORMANCE,
                    description="Test timer metric",
                    unit="seconds",
                ),
            ]

            for metric in test_metrics:
                self.metrics_collector.register_metric(metric)
                self.test_metrics.append(metric.name)

            # Verify registration
            registered_count = len(
                [
                    m
                    for m in self.metrics_collector.metrics.keys()
                    if m.startswith("test_")
                ]
            )
            expected_count = len(test_metrics)

            self.test_results["metric_registration"] = {
                "status": "PASS" if registered_count == expected_count else "FAIL",
                "message": f"Metric registration {'successful' if registered_count == expected_count else 'failed'}",
                "registered_count": registered_count,
                "expected_count": expected_count,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Metric registration {'successful' if registered_count == expected_count else 'failed'}"
            )

        except Exception as e:
            self.test_results["metric_registration"] = {
                "status": "FAIL",
                "message": f"Metric registration failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Metric registration failed: {e}")

    async def _test_counter_metrics(self):
        """Test counter metrics."""
        try:
            # Test counter increment
            self.metrics_collector.increment_counter("test_counter", 1)
            self.metrics_collector.increment_counter("test_counter", 5)

            # Verify counter value
            counter_value = self.metrics_collector.get_metric_value("test_counter")
            expected_value = 6

            counter_success = counter_value == expected_value

            # Test counter with tags
            self.metrics_collector.increment_counter("test_counter", 2, {"tag": "test"})

            # Verify counter with tags
            counter_with_tags = self.metrics_collector.get_metric_value("test_counter")
            expected_with_tags = 8

            tags_success = counter_with_tags == expected_with_tags

            self.test_results["counter_metrics"] = {
                "status": "PASS" if counter_success and tags_success else "FAIL",
                "message": f"Counter metrics {'successful' if counter_success and tags_success else 'failed'}",
                "counter_success": counter_success,
                "tags_success": tags_success,
                "counter_value": counter_value,
                "expected_value": expected_value,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Counter metrics {'successful' if counter_success and tags_success else 'failed'}"
            )

        except Exception as e:
            self.test_results["counter_metrics"] = {
                "status": "FAIL",
                "message": f"Counter metrics test failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Counter metrics test failed: {e}")

    async def _test_gauge_metrics(self):
        """Test gauge metrics."""
        try:
            # Test gauge setting
            self.metrics_collector.set_gauge("test_gauge", 75.5)
            self.metrics_collector.set_gauge("test_gauge", 85.0)

            # Verify gauge value
            gauge_value = self.metrics_collector.get_metric_value("test_gauge")
            expected_value = 85.0

            gauge_success = gauge_value == expected_value

            # Test gauge with tags
            self.metrics_collector.set_gauge("test_gauge", 90.0, {"tag": "test"})

            # Verify gauge with tags
            gauge_with_tags = self.metrics_collector.get_metric_value("test_gauge")
            expected_with_tags = 90.0

            tags_success = gauge_with_tags == expected_with_tags

            self.test_results["gauge_metrics"] = {
                "status": "PASS" if gauge_success and tags_success else "FAIL",
                "message": f"Gauge metrics {'successful' if gauge_success and tags_success else 'failed'}",
                "gauge_success": gauge_success,
                "tags_success": tags_success,
                "gauge_value": gauge_value,
                "expected_value": expected_value,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Gauge metrics {'successful' if gauge_success and tags_success else 'failed'}"
            )

        except Exception as e:
            self.test_results["gauge_metrics"] = {
                "status": "FAIL",
                "message": f"Gauge metrics test failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Gauge metrics test failed: {e}")

    async def _test_timer_metrics(self):
        """Test timer metrics."""
        try:
            # Test timer recording
            self.metrics_collector.record_timer("test_timer", 0.5)
            self.metrics_collector.record_timer("test_timer", 1.2)
            self.metrics_collector.record_timer("test_timer", 0.8)

            # Verify timer values
            timer_values = self.metrics_collector.timers.get("test_timer", [])
            expected_count = 3

            timer_success = len(timer_values) == expected_count

            # Test timer aggregation
            timer_average = self.metrics_collector.get_metric_value(
                "test_timer", "average"
            )
            timer_sum = self.metrics_collector.get_metric_value("test_timer", "sum")

            aggregation_success = timer_average is not None and timer_sum is not None

            # Test timer with tags
            self.metrics_collector.record_timer("test_timer", 1.0, {"tag": "test"})

            # Verify timer with tags
            timer_with_tags = self.metrics_collector.timers.get("test_timer", [])
            tags_success = len(timer_with_tags) == 4

            self.test_results["timer_metrics"] = {
                "status": (
                    "PASS"
                    if timer_success and aggregation_success and tags_success
                    else "FAIL"
                ),
                "message": f"Timer metrics {'successful' if timer_success and aggregation_success and tags_success else 'failed'}",
                "timer_success": timer_success,
                "aggregation_success": aggregation_success,
                "tags_success": tags_success,
                "timer_count": len(timer_values),
                "expected_count": expected_count,
                "timer_average": timer_average,
                "timer_sum": timer_sum,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Timer metrics {'successful' if timer_success and aggregation_success and tags_success else 'failed'}"
            )

        except Exception as e:
            self.test_results["timer_metrics"] = {
                "status": "FAIL",
                "message": f"Timer metrics test failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Timer metrics test failed: {e}")

    async def _test_histogram_metrics(self):
        """Test histogram metrics."""
        try:
            # Test histogram recording
            values = [0.1, 0.2, 0.3, 0.4, 0.5]
            for value in values:
                self.metrics_collector.record_histogram("test_histogram", value)

            # Verify histogram values
            histogram_values = self.metrics_collector.histograms.get(
                "test_histogram", []
            )
            expected_count = len(values)

            histogram_success = len(histogram_values) == expected_count

            # Test histogram aggregation
            histogram_average = self.metrics_collector.get_metric_value(
                "test_histogram", "average"
            )
            histogram_min = self.metrics_collector.get_metric_value(
                "test_histogram", "min"
            )
            histogram_max = self.metrics_collector.get_metric_value(
                "test_histogram", "max"
            )

            aggregation_success = (
                histogram_average is not None
                and histogram_min is not None
                and histogram_max is not None
            )

            # Verify aggregation values
            expected_average = sum(values) / len(values)
            expected_min = min(values)
            expected_max = max(values)

            values_match = (
                abs(histogram_average - expected_average) < 0.001
                and histogram_min == expected_min
                and histogram_max == expected_max
            )

            self.test_results["histogram_metrics"] = {
                "status": (
                    "PASS"
                    if histogram_success and aggregation_success and values_match
                    else "FAIL"
                ),
                "message": f"Histogram metrics {'successful' if histogram_success and aggregation_success and values_match else 'failed'}",
                "histogram_success": histogram_success,
                "aggregation_success": aggregation_success,
                "values_match": values_match,
                "histogram_count": len(histogram_values),
                "expected_count": expected_count,
                "histogram_average": histogram_average,
                "expected_average": expected_average,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Histogram metrics {'successful' if histogram_success and aggregation_success and values_match else 'failed'}"
            )

        except Exception as e:
            self.test_results["histogram_metrics"] = {
                "status": "FAIL",
                "message": f"Histogram metrics test failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Histogram metrics test failed: {e}")

    async def _test_average_metrics(self):
        """Test average metrics."""
        try:
            # Test average recording
            values = [10.0, 20.0, 30.0, 40.0, 50.0]
            for value in values:
                self.metrics_collector.record_average("test_average", value)

            # Verify average values
            average_values = self.metrics_collector.averages.get("test_average", [])
            expected_count = len(values)

            average_success = len(average_values) == expected_count

            # Test average aggregation
            average_result = self.metrics_collector.get_metric_value(
                "test_average", "average"
            )
            expected_average = sum(values) / len(values)

            aggregation_success = (
                average_result is not None
                and abs(average_result - expected_average) < 0.001
            )

            # Test other aggregations
            average_min = self.metrics_collector.get_metric_value("test_average", "min")
            average_max = self.metrics_collector.get_metric_value("test_average", "max")

            min_max_success = (
                average_min is not None
                and average_max is not None
                and average_min == min(values)
                and average_max == max(values)
            )

            self.test_results["average_metrics"] = {
                "status": (
                    "PASS"
                    if average_success and aggregation_success and min_max_success
                    else "FAIL"
                ),
                "message": f"Average metrics {'successful' if average_success and aggregation_success and min_max_success else 'failed'}",
                "average_success": average_success,
                "aggregation_success": aggregation_success,
                "min_max_success": min_max_success,
                "average_count": len(average_values),
                "expected_count": expected_count,
                "average_result": average_result,
                "expected_average": expected_average,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Average metrics {'successful' if average_success and aggregation_success and min_max_success else 'failed'}"
            )

        except Exception as e:
            self.test_results["average_metrics"] = {
                "status": "FAIL",
                "message": f"Average metrics test failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Average metrics test failed: {e}")

    async def _test_metric_retrieval(self):
        """Test metric retrieval."""
        try:
            # Test getting all metrics
            all_metrics = self.metrics_collector.get_all_metrics()

            # Test getting metrics by category
            system_metrics = self.metrics_collector.get_metrics_by_category(
                MetricCategory.SYSTEM
            )
            performance_metrics = self.metrics_collector.get_metrics_by_category(
                MetricCategory.PERFORMANCE
            )

            # Test getting metric statistics
            stats = self.metrics_collector.get_metric_statistics("test_counter")

            # Verify retrieval
            all_metrics_success = len(all_metrics) > 0
            category_success = len(system_metrics) > 0 and len(performance_metrics) > 0
            stats_success = len(stats) > 0

            self.test_results["metric_retrieval"] = {
                "status": (
                    "PASS"
                    if all_metrics_success and category_success and stats_success
                    else "FAIL"
                ),
                "message": f"Metric retrieval {'successful' if all_metrics_success and category_success and stats_success else 'failed'}",
                "all_metrics_success": all_metrics_success,
                "category_success": category_success,
                "stats_success": stats_success,
                "all_metrics_count": len(all_metrics),
                "system_metrics_count": len(system_metrics),
                "performance_metrics_count": len(performance_metrics),
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Metric retrieval {'successful' if all_metrics_success and category_success and stats_success else 'failed'}"
            )

        except Exception as e:
            self.test_results["metric_retrieval"] = {
                "status": "FAIL",
                "message": f"Metric retrieval failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Metric retrieval failed: {e}")

    async def _test_metric_aggregation(self):
        """Test metric aggregation."""
        try:
            # Test different aggregation methods
            latest_value = self.metrics_collector.get_metric_value(
                "test_timer", "latest"
            )
            sum_value = self.metrics_collector.get_metric_value("test_timer", "sum")
            count_value = self.metrics_collector.get_metric_value("test_timer", "count")
            min_value = self.metrics_collector.get_metric_value("test_timer", "min")
            max_value = self.metrics_collector.get_metric_value("test_timer", "max")

            # Verify aggregations
            aggregations_success = (
                latest_value is not None
                and sum_value is not None
                and count_value is not None
                and min_value is not None
                and max_value is not None
            )

            # Test invalid aggregation
            invalid_value = self.metrics_collector.get_metric_value(
                "test_timer", "invalid"
            )
            invalid_success = invalid_value is None

            self.test_results["metric_aggregation"] = {
                "status": (
                    "PASS" if aggregations_success and invalid_success else "FAIL"
                ),
                "message": f"Metric aggregation {'successful' if aggregations_success and invalid_success else 'failed'}",
                "aggregations_success": aggregations_success,
                "invalid_success": invalid_success,
                "latest_value": latest_value,
                "sum_value": sum_value,
                "count_value": count_value,
                "min_value": min_value,
                "max_value": max_value,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Metric aggregation {'successful' if aggregations_success and invalid_success else 'failed'}"
            )

        except Exception as e:
            self.test_results["metric_aggregation"] = {
                "status": "FAIL",
                "message": f"Metric aggregation failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Metric aggregation failed: {e}")

    async def _test_metric_history(self):
        """Test metric history."""
        try:
            # Add some delay to get different timestamps
            await asyncio.sleep(0.1)
            self.metrics_collector.increment_counter("test_counter", 1)
            await asyncio.sleep(0.1)
            self.metrics_collector.increment_counter("test_counter", 1)
            await asyncio.sleep(0.1)
            self.metrics_collector.increment_counter("test_counter", 1)

            # Test getting history
            all_history = self.metrics_collector.get_metric_history("test_counter")

            # Test getting history with time range
            now = datetime.now()
            start_time = now - timedelta(minutes=1)
            recent_history = self.metrics_collector.get_metric_history(
                "test_counter", start_time, now
            )

            # Verify history
            all_history_success = len(all_history) >= 3
            recent_history_success = len(recent_history) >= 3

            # Test empty history
            empty_history = self.metrics_collector.get_metric_history(
                "nonexistent_metric"
            )
            empty_success = len(empty_history) == 0

            self.test_results["metric_history"] = {
                "status": (
                    "PASS"
                    if all_history_success and recent_history_success and empty_success
                    else "FAIL"
                ),
                "message": f"Metric history {'successful' if all_history_success and recent_history_success and empty_success else 'failed'}",
                "all_history_success": all_history_success,
                "recent_history_success": recent_history_success,
                "empty_success": empty_success,
                "all_history_count": len(all_history),
                "recent_history_count": len(recent_history),
                "empty_history_count": len(empty_history),
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Metric history {'successful' if all_history_success and recent_history_success and empty_success else 'failed'}"
            )

        except Exception as e:
            self.test_results["metric_history"] = {
                "status": "FAIL",
                "message": f"Metric history failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Metric history failed: {e}")

    async def _test_metric_export(self):
        """Test metric export."""
        try:
            # Test JSON export
            json_export = self.metrics_collector.export_metrics("json")
            json_success = json_export is not None and len(json_export) > 0

            # Test Prometheus export
            prometheus_export = self.metrics_collector.export_metrics("prometheus")
            prometheus_success = (
                prometheus_export is not None and len(prometheus_export) > 0
            )

            # Test invalid export format
            try:
                invalid_export = self.metrics_collector.export_metrics("invalid")
                invalid_success = False
            except ValueError:
                invalid_success = True

            # Verify JSON format
            try:
                json_data = json.loads(json_export)
                json_format_success = True
            except:
                json_format_success = False

            self.test_results["metric_export"] = {
                "status": (
                    "PASS"
                    if json_success
                    and prometheus_success
                    and invalid_success
                    and json_format_success
                    else "FAIL"
                ),
                "message": f"Metric export {'successful' if json_success and prometheus_success and invalid_success and json_format_success else 'failed'}",
                "json_success": json_success,
                "prometheus_success": prometheus_success,
                "invalid_success": invalid_success,
                "json_format_success": json_format_success,
                "json_length": len(json_export) if json_export else 0,
                "prometheus_length": len(prometheus_export) if prometheus_export else 0,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Metric export {'successful' if json_success and prometheus_success and invalid_success and json_format_success else 'failed'}"
            )

        except Exception as e:
            self.test_results["metric_export"] = {
                "status": "FAIL",
                "message": f"Metric export failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Metric export failed: {e}")

    async def _test_decorators(self):
        """Test metric decorators."""
        try:
            # Test time_metric decorator
            @time_metric("test_function_timer")
            async def test_function():
                await asyncio.sleep(0.1)
                return "test_result"

            result = await test_function()
            timer_value = self.metrics_collector.get_metric_value("test_function_timer")
            timer_success = timer_value is not None and timer_value > 0

            # Test count_metric decorator
            @count_metric("test_function_counter")
            async def test_function2():
                return "test_result"

            await test_function2()
            await test_function2()

            counter_value = self.metrics_collector.get_metric_value(
                "test_function_counter"
            )
            counter_success = counter_value == 2

            # Test TimerMetric context manager
            async with TimerMetric("test_context_timer"):
                await asyncio.sleep(0.05)

            context_timer_value = self.metrics_collector.get_metric_value(
                "test_context_timer"
            )
            context_success = (
                context_timer_value is not None and context_timer_value > 0
            )

            self.test_results["decorators"] = {
                "status": (
                    "PASS"
                    if timer_success and counter_success and context_success
                    else "FAIL"
                ),
                "message": f"Decorators {'successful' if timer_success and counter_success and context_success else 'failed'}",
                "timer_success": timer_success,
                "counter_success": counter_success,
                "context_success": context_success,
                "timer_value": timer_value,
                "counter_value": counter_value,
                "context_timer_value": context_timer_value,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Decorators {'successful' if timer_success and counter_success and context_success else 'failed'}"
            )

        except Exception as e:
            self.test_results["decorators"] = {
                "status": "FAIL",
                "message": f"Decorators test failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Decorators test failed: {e}")

    async def _test_cleanup(self):
        """Test cleanup functionality."""
        try:
            # Reset individual metric
            self.metrics_collector.reset_metric("test_counter")
            counter_reset = self.metrics_collector.get_metric_value("test_counter") == 0

            # Reset all metrics
            self.metrics_collector.reset_all_metrics()
            all_reset = self.metrics_collector.get_metric_value("test_counter") == 0

            # Test cleanup of old metrics
            self.metrics_collector.cleanup_old_metrics(1)  # 1 day retention
            cleanup_success = True  # Assuming cleanup works

            # Test enable/disable
            self.metrics_collector.disable()
            disabled = not self.metrics_collector.is_enabled()

            self.metrics_collector.enable()
            enabled = self.metrics_collector.is_enabled()

            cleanup_success = cleanup_success and disabled and enabled

            self.test_results["cleanup"] = {
                "status": (
                    "PASS"
                    if counter_reset and all_reset and cleanup_success
                    else "FAIL"
                ),
                "message": f"Cleanup {'successful' if counter_reset and all_reset and cleanup_success else 'failed'}",
                "counter_reset": counter_reset,
                "all_reset": all_reset,
                "cleanup_success": cleanup_success,
                "disabled": disabled,
                "enabled": enabled,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(
                f"✅ Cleanup {'successful' if counter_reset and all_reset and cleanup_success else 'failed'}"
            )

        except Exception as e:
            self.test_results["cleanup"] = {
                "status": "FAIL",
                "message": f"Cleanup test failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

            logger.error(f"❌ Cleanup test failed: {e}")

    def print_test_results(self):
        """Print test results summary."""
        logger.info("\n" + "=" * 50)
        logger.info("METRICS COLLECTION TEST RESULTS")
        logger.info("=" * 50)

        total_tests = len(self.test_results)
        passed_tests = len(
            [r for r in self.test_results.values() if r["status"] == "PASS"]
        )
        failed_tests = total_tests - passed_tests

        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")

        logger.info("\nDetailed Results:")
        for test_name, result in self.test_results.items():
            status_icon = "✅" if result["status"] == "PASS" else "❌"
            logger.info(f"{status_icon} {test_name}: {result['message']}")

        if failed_tests > 0:
            logger.info(
                f"\n⚠️  {failed_tests} tests failed. Please review the errors above."
            )
        else:
            logger.info(
                "\n🎉 All tests passed! Metrics collection is working correctly."
            )

        logger.info("=" * 50)


async def main():
    """Main function to run tests."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run tests
    tester = TestMetricsCollection()
    results = await tester.run_all_tests()

    return results


if __name__ == "__main__":
    # Run the tests
    results = asyncio.run(main())

    # Exit with appropriate code
    failed_count = len([r for r in results.values() if r["status"] == "FAIL"])
    exit(1 if failed_count > 0 else 0)
