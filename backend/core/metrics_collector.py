"""
Comprehensive metrics collection system for Raptorflow backend.
Provides detailed monitoring, aggregation, and reporting capabilities.
"""

import asyncio
import json
import logging
import statistics
import threading
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union

import psutil

from backend.core.resource_analytics import OptimizationRecommendation

logger = logging.getLogger(__name__)


class MetricCategory(Enum):
    """Categories of metrics for organization."""

    SYSTEM = "system"
    PERFORMANCE = "performance"
    BUSINESS = "business"
    SECURITY = "security"
    RELIABILITY = "reliability"
    RESOURCE = "resource"
    USER = "user"
    AGENT = "agent"


class MetricType(Enum):
    """Types of metrics with specific units and aggregation methods."""

    COUNTER = "counter"  # Cumulative value
    GAUGE = "gauge"  # Current value
    HISTOGRAM = "histogram"  # Distribution of values
    TIMER = "timer"  # Duration measurements
    RATE = "rate"  # Rate per time unit


class AggregationMethod(Enum):
    """Methods for aggregating metric values."""

    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    P50 = "p50"  # Median
    P95 = "p95"
    P99 = "p99"
    COUNT = "count"


@dataclass
class MetricDefinition:
    """Definition of a metric with its properties."""

    name: str
    category: MetricCategory
    metric_type: MetricType
    unit: str
    description: str
    aggregation_methods: List[AggregationMethod] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "category": self.category.value,
            "metric_type": self.metric_type.value,
            "unit": self.unit,
            "description": self.description,
            "aggregation_methods": [m.value for m in self.aggregation_methods],
            "tags": self.tags,
            "enabled": self.enabled,
        }


@dataclass
class MetricValue:
    """A single metric value with timestamp and metadata."""

    metric_name: str
    value: Union[int, float]
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "metric_name": self.metric_name,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags,
            "metadata": self.metadata,
        }


@dataclass
class MetricAggregation:
    """Aggregated metric values over a time window."""

    metric_name: str
    time_window_start: datetime
    time_window_end: datetime
    aggregation_method: AggregationMethod
    value: float
    sample_count: int
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "metric_name": self.metric_name,
            "time_window_start": self.time_window_start.isoformat(),
            "time_window_end": self.time_window_end.isoformat(),
            "aggregation_method": self.aggregation_method.value,
            "value": self.value,
            "sample_count": self.sample_count,
            "tags": self.tags,
        }


@dataclass
class AlertRule:
    """Rule for generating alerts based on metric thresholds."""

    name: str
    metric_name: str
    condition: str  # "gt", "lt", "eq", "gte", "lte"
    threshold: float
    duration_seconds: int = 300  # 5 minutes default
    severity: str = "warning"  # "info", "warning", "error", "critical"
    enabled: bool = True
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "metric_name": self.metric_name,
            "condition": self.condition,
            "threshold": self.threshold,
            "duration_seconds": self.duration_seconds,
            "severity": self.severity,
            "enabled": self.enabled,
            "tags": self.tags,
        }


@dataclass
class MetricAlert:
    """An alert generated from a metric rule."""

    rule_name: str
    metric_name: str
    triggered_at: datetime
    severity: str
    message: str
    current_value: float
    threshold: float
    resolved_at: Optional[datetime] = None
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "rule_name": self.rule_name,
            "metric_name": self.metric_name,
            "triggered_at": self.triggered_at.isoformat(),
            "severity": self.severity,
            "message": self.message,
            "current_value": self.current_value,
            "threshold": self.threshold,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "tags": self.tags,
        }


class MetricsCollector:
    """Comprehensive metrics collector with aggregation and alerting."""

    def __init__(self, max_values: int = 100000, aggregation_interval: int = 60):
        self.max_values = max_values
        self.aggregation_interval = aggregation_interval

        # Metric definitions
        self.metric_definitions: Dict[str, MetricDefinition] = {}
        self._initialize_default_metrics()

        # Metric storage
        self.metric_values: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=max_values)
        )
        self.metric_aggregations: Dict[str, List[MetricAggregation]] = defaultdict(list)

        # Alert system
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, MetricAlert] = {}
        self.alert_history: List[MetricAlert] = []

        # Background tasks
        self._background_tasks: Set[asyncio.Task] = set()
        self._running = False
        self._lock = asyncio.Lock()

        # Performance tracking
        self.collection_stats = {
            "total_metrics_collected": 0,
            "total_aggregations_computed": 0,
            "total_alerts_triggered": 0,
            "collection_time_ms": 0.0,
            "aggregation_time_ms": 0.0,
            "alert_evaluation_time_ms": 0.0,
        }

        logger.info(f"Metrics collector initialized with max values: {max_values}")

    def _initialize_default_metrics(self):
        """Initialize default metric definitions."""
        default_metrics = [
            # System metrics
            MetricDefinition(
                name="system_cpu_percent",
                category=MetricCategory.SYSTEM,
                metric_type=MetricType.GAUGE,
                unit="percent",
                description="CPU usage percentage",
                aggregation_methods=[AggregationMethod.AVERAGE, AggregationMethod.MAX],
            ),
            MetricDefinition(
                name="system_memory_percent",
                category=MetricCategory.SYSTEM,
                metric_type=MetricType.GAUGE,
                unit="percent",
                description="Memory usage percentage",
                aggregation_methods=[AggregationMethod.AVERAGE, AggregationMethod.MAX],
            ),
            MetricDefinition(
                name="system_disk_usage_percent",
                category=MetricCategory.SYSTEM,
                metric_type=MetricType.GAUGE,
                unit="percent",
                description="Disk usage percentage",
                aggregation_methods=[AggregationMethod.AVERAGE],
            ),
            # Performance metrics
            MetricDefinition(
                name="request_duration_ms",
                category=MetricCategory.PERFORMANCE,
                metric_type=MetricType.HISTOGRAM,
                unit="milliseconds",
                description="Request duration in milliseconds",
                aggregation_methods=[
                    AggregationMethod.AVERAGE,
                    AggregationMethod.P95,
                    AggregationMethod.P99,
                ],
            ),
            MetricDefinition(
                name="request_rate",
                category=MetricCategory.PERFORMANCE,
                metric_type=MetricType.RATE,
                unit="requests_per_second",
                description="Request rate per second",
                aggregation_methods=[AggregationMethod.AVERAGE, AggregationMethod.MAX],
            ),
            # Business metrics
            MetricDefinition(
                name="active_users",
                category=MetricCategory.BUSINESS,
                metric_type=MetricType.GAUGE,
                unit="count",
                description="Number of active users",
                aggregation_methods=[AggregationMethod.AVERAGE, AggregationMethod.MAX],
            ),
            MetricDefinition(
                name="agent_executions",
                category=MetricCategory.AGENT,
                metric_type=MetricType.COUNTER,
                unit="count",
                description="Total agent executions",
                aggregation_methods=[AggregationMethod.SUM, AggregationMethod.COUNT],
            ),
            # Resource metrics
            MetricDefinition(
                name="resource_count",
                category=MetricCategory.RESOURCE,
                metric_type=MetricType.GAUGE,
                unit="count",
                description="Number of managed resources",
                aggregation_methods=[AggregationMethod.AVERAGE, AggregationMethod.MAX],
            ),
            MetricDefinition(
                name="resource_leaks",
                category=MetricCategory.RESOURCE,
                metric_type=MetricType.COUNTER,
                unit="count",
                description="Number of resource leaks detected",
                aggregation_methods=[AggregationMethod.SUM],
            ),
        ]

        for metric_def in default_metrics:
            self.metric_definitions[metric_def.name] = metric_def

    async def start(self):
        """Start the metrics collector background tasks."""
        if self._running:
            return

        self._running = True

        # Start background tasks
        self._background_tasks.add(asyncio.create_task(self._aggregation_loop()))
        self._background_tasks.add(asyncio.create_task(self._alert_evaluation_loop()))
        self._background_tasks.add(asyncio.create_task(self._cleanup_loop()))
        self._background_tasks.add(asyncio.create_task(self._system_metrics_loop()))

        logger.info("Metrics collector started")

    async def stop(self):
        """Stop the metrics collector."""
        self._running = False

        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()

        await asyncio.gather(*self._background_tasks, return_exceptions=True)
        self._background_tasks.clear()

        logger.info("Metrics collector stopped")

    def define_metric(self, metric_def: MetricDefinition):
        """Define a new metric."""
        self.metric_definitions[metric_def.name] = metric_def
        logger.debug(f"Defined metric: {metric_def.name}")

    def record_metric(
        self,
        metric_name: str,
        value: Union[int, float],
        tags: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Record a metric value."""
        try:
            # Check if metric is defined
            if metric_name not in self.metric_definitions:
                logger.warning(f"Recording undefined metric: {metric_name}")
                # Auto-define with basic properties
                self.metric_definitions[metric_name] = MetricDefinition(
                    name=metric_name,
                    category=MetricCategory.SYSTEM,
                    metric_type=MetricType.GAUGE,
                    unit="unknown",
                    description="Auto-defined metric",
                )

            metric_def = self.metric_definitions[metric_name]

            if not metric_def.enabled:
                return False

            # Create metric value
            metric_value = MetricValue(
                metric_name=metric_name,
                value=value,
                timestamp=datetime.now(),
                tags=tags or {},
                metadata=metadata or {},
            )

            # Store value
            self.metric_values[metric_name].append(metric_value)
            self.collection_stats["total_metrics_collected"] += 1

            return True

        except Exception as e:
            logger.error(f"Failed to record metric {metric_name}: {e}")
            return False

    def increment_counter(
        self,
        metric_name: str,
        value: int = 1,
        tags: Optional[Dict[str, str]] = None,
    ):
        """Increment a counter metric."""
        # Get current value
        current_values = self.metric_values.get(metric_name, deque())
        current_value = 0

        if current_values:
            latest = current_values[-1]
            if isinstance(latest.value, (int, float)):
                current_value = latest.value

        # Record new value
        new_value = current_value + value
        self.record_metric(metric_name, new_value, tags)

    def set_gauge(
        self,
        metric_name: str,
        value: Union[int, float],
        tags: Optional[Dict[str, str]] = None,
    ):
        """Set a gauge metric value."""
        self.record_metric(metric_name, value, tags)

    def record_timer(
        self,
        metric_name: str,
        duration_ms: float,
        tags: Optional[Dict[str, str]] = None,
    ):
        """Record a timer metric."""
        self.record_metric(metric_name, duration_ms, tags)

    def add_alert_rule(self, alert_rule: AlertRule):
        """Add an alert rule."""
        self.alert_rules[alert_rule.name] = alert_rule
        logger.info(f"Added alert rule: {alert_rule.name}")

    def remove_alert_rule(self, rule_name: str) -> bool:
        """Remove an alert rule."""
        if rule_name in self.alert_rules:
            del self.alert_rules[rule_name]

            # Resolve any active alerts for this rule
            if rule_name in self.active_alerts:
                alert = self.active_alerts[rule_name]
                alert.resolved_at = datetime.now()
                self.alert_history.append(alert)
                del self.active_alerts[rule_name]

            logger.info(f"Removed alert rule: {rule_name}")
            return True
        return False

    async def _aggregation_loop(self):
        """Background loop for computing metric aggregations."""
        while self._running:
            try:
                await asyncio.sleep(self.aggregation_interval)
                await self._compute_aggregations()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Aggregation loop error: {e}")

    async def _compute_aggregations(self):
        """Compute aggregations for all metrics."""
        start_time = time.time()

        try:
            now = datetime.now()
            window_start = now - timedelta(seconds=self.aggregation_interval)

            for metric_name, values in self.metric_values.items():
                if not values:
                    continue

                metric_def = self.metric_definitions.get(metric_name)
                if not metric_def or not metric_def.aggregation_methods:
                    continue

                # Filter values in the time window
                recent_values = [v.value for v in values if v.timestamp >= window_start]

                if not recent_values:
                    continue

                # Compute aggregations
                for method in metric_def.aggregation_methods:
                    aggregated_value = self._compute_aggregation(recent_values, method)

                    if aggregated_value is not None:
                        aggregation = MetricAggregation(
                            metric_name=metric_name,
                            time_window_start=window_start,
                            time_window_end=now,
                            aggregation_method=method,
                            value=aggregated_value,
                            sample_count=len(recent_values),
                        )

                        self.metric_aggregations[metric_name].append(aggregation)
                        self.collection_stats["total_aggregations_computed"] += 1

                        # Keep only recent aggregations
                        if len(self.metric_aggregations[metric_name]) > 1000:
                            self.metric_aggregations[metric_name] = (
                                self.metric_aggregations[metric_name][-1000:]
                            )

            self.collection_stats["aggregation_time_ms"] = (
                time.time() - start_time
            ) * 1000

        except Exception as e:
            logger.error(f"Aggregation computation error: {e}")

    def _compute_aggregation(
        self, values: List[float], method: AggregationMethod
    ) -> Optional[float]:
        """Compute a single aggregation method on values."""
        try:
            if not values:
                return None

            if method == AggregationMethod.SUM:
                return sum(values)
            elif method == AggregationMethod.AVERAGE:
                return statistics.mean(values)
            elif method == AggregationMethod.MIN:
                return min(values)
            elif method == AggregationMethod.MAX:
                return max(values)
            elif method == AggregationMethod.COUNT:
                return len(values)
            elif method == AggregationMethod.P50:
                return statistics.median(values)
            elif method == AggregationMethod.P95:
                return self._percentile(values, 95)
            elif method == AggregationMethod.P99:
                return self._percentile(values, 99)
            else:
                return None

        except Exception as e:
            logger.error(f"Aggregation computation error for {method}: {e}")
            return None

    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile of values."""
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]

    async def _alert_evaluation_loop(self):
        """Background loop for evaluating alert rules."""
        while self._running:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                await self._evaluate_alerts()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Alert evaluation loop error: {e}")

    async def _evaluate_alerts(self):
        """Evaluate all alert rules."""
        start_time = time.time()

        try:
            now = datetime.now()

            for rule_name, rule in self.alert_rules.items():
                if not rule.enabled:
                    continue

                # Get latest value for the metric
                values = self.metric_values.get(rule.metric_name)
                if not values:
                    continue

                latest_value = values[-1].value

                # Check if condition is met
                condition_met = self._check_condition(
                    latest_value, rule.condition, rule.threshold
                )

                if condition_met:
                    # Check if we already have an active alert
                    if rule_name not in self.active_alerts:
                        # Create new alert
                        alert = MetricAlert(
                            rule_name=rule_name,
                            metric_name=rule.metric_name,
                            triggered_at=now,
                            severity=rule.severity,
                            message=f"Metric {rule.metric_name} is {rule.condition} {rule.threshold} (current: {latest_value})",
                            current_value=latest_value,
                            threshold=rule.threshold,
                            tags=rule.tags,
                        )

                        self.active_alerts[rule_name] = alert
                        self.alert_history.append(alert)
                        self.collection_stats["total_alerts_triggered"] += 1

                        logger.warning(f"Alert triggered: {alert.message}")

                else:
                    # Resolve existing alert if condition is no longer met
                    if rule_name in self.active_alerts:
                        alert = self.active_alerts[rule_name]
                        alert.resolved_at = now
                        del self.active_alerts[rule_name]

                        logger.info(f"Alert resolved: {rule_name}")

            self.collection_stats["alert_evaluation_time_ms"] = (
                time.time() - start_time
            ) * 1000

        except Exception as e:
            logger.error(f"Alert evaluation error: {e}")

    def _check_condition(self, value: float, condition: str, threshold: float) -> bool:
        """Check if a value meets the condition."""
        if condition == "gt":
            return value > threshold
        elif condition == "lt":
            return value < threshold
        elif condition == "eq":
            return value == threshold
        elif condition == "gte":
            return value >= threshold
        elif condition == "lte":
            return value <= threshold
        else:
            return False

    async def _cleanup_loop(self):
        """Background loop for cleaning up old data."""
        while self._running:
            try:
                await asyncio.sleep(3600)  # Run every hour
                await self._cleanup_old_data()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")

    async def _cleanup_old_data(self):
        """Clean up old metric values and aggregations."""
        cutoff_time = datetime.now() - timedelta(hours=24)

        # Clean up old values
        for metric_name in list(self.metric_values.keys()):
            values = self.metric_values[metric_name]
            # Keep only recent values
            while values and values[0].timestamp < cutoff_time:
                values.popleft()

        # Clean up old aggregations
        for metric_name in list(self.metric_aggregations.keys()):
            aggregations = self.metric_aggregations[metric_name]
            self.metric_aggregations[metric_name] = [
                agg for agg in aggregations if agg.time_window_end >= cutoff_time
            ]

        # Clean up old alert history
        self.alert_history = [
            alert
            for alert in self.alert_history
            if alert.triggered_at >= cutoff_time or alert.resolved_at is None
        ]

        logger.debug("Completed metrics data cleanup")

    async def _system_metrics_loop(self):
        """Background loop for collecting system metrics."""
        while self._running:
            try:
                await asyncio.sleep(30)  # Collect every 30 seconds
                await self._collect_system_metrics()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"System metrics collection error: {e}")

    async def _collect_system_metrics(self):
        """Collect system-level metrics."""
        try:
            process = psutil.Process()

            # CPU metrics
            cpu_percent = process.cpu_percent()
            self.set_gauge("system_cpu_percent", cpu_percent)

            # Memory metrics
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()
            self.set_gauge("system_memory_percent", memory_percent)
            self.set_gauge("system_memory_bytes", memory_info.rss)

            # Disk metrics
            disk_usage = psutil.disk_usage("/")
            disk_percent = (disk_usage.used / disk_usage.total) * 100
            self.set_gauge("system_disk_usage_percent", disk_percent)

            # Process metrics
            self.set_gauge("system_threads", process.num_threads())
            self.set_gauge("system_open_files", len(process.open_files()))

            # Network metrics
            network_io = psutil.net_io_counters()
            self.increment_counter("system_network_bytes_sent", network_io.bytes_sent)
            self.increment_counter("system_network_bytes_recv", network_io.bytes_recv)

        except Exception as e:
            logger.error(f"System metrics collection error: {e}")

    def get_metric_values(
        self,
        metric_name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        tags: Optional[Dict[str, str]] = None,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """Get metric values with optional filtering."""
        try:
            values = self.metric_values.get(metric_name, deque())

            # Filter by time range
            if start_time or end_time:
                filtered_values = []
                for value in values:
                    if start_time and value.timestamp < start_time:
                        continue
                    if end_time and value.timestamp > end_time:
                        continue
                    filtered_values.append(value)
                values = filtered_values

            # Filter by tags
            if tags:
                filtered_values = []
                for value in values:
                    if all(value.tags.get(k) == v for k, v in tags.items()):
                        filtered_values.append(value)
                values = filtered_values

            # Convert to dict and limit
            result = [value.to_dict() for value in values[-limit:]]
            return result

        except Exception as e:
            logger.error(f"Failed to get metric values for {metric_name}: {e}")
            return []

    def get_metric_aggregations(
        self,
        metric_name: str,
        aggregation_method: Optional[AggregationMethod] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get metric aggregations with optional filtering."""
        try:
            aggregations = self.metric_aggregations.get(metric_name, [])

            # Filter by aggregation method
            if aggregation_method:
                aggregations = [
                    agg
                    for agg in aggregations
                    if agg.aggregation_method == aggregation_method
                ]

            # Filter by time range
            if start_time or end_time:
                filtered_aggregations = []
                for agg in aggregations:
                    if start_time and agg.time_window_end < start_time:
                        continue
                    if end_time and agg.time_window_start > end_time:
                        continue
                    filtered_aggregations.append(agg)
                aggregations = filtered_aggregations

            # Convert to dict and limit
            result = [agg.to_dict() for agg in aggregations[-limit:]]
            return result

        except Exception as e:
            logger.error(f"Failed to get metric aggregations for {metric_name}: {e}")
            return []

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of all metrics."""
        try:
            summary = {
                "total_metrics": len(self.metric_definitions),
                "enabled_metrics": len(
                    [m for m in self.metric_definitions.values() if m.enabled]
                ),
                "total_values": sum(
                    len(values) for values in self.metric_values.values()
                ),
                "total_aggregations": sum(
                    len(agg) for agg in self.metric_aggregations.values()
                ),
                "active_alerts": len(self.active_alerts),
                "alert_rules": len(self.alert_rules),
                "collection_stats": self.collection_stats.copy(),
                "metrics_by_category": defaultdict(int),
                "metrics_by_type": defaultdict(int),
            }

            # Count by category and type
            for metric_def in self.metric_definitions.values():
                if metric_def.enabled:
                    summary["metrics_by_category"][metric_def.category.value] += 1
                    summary["metrics_by_type"][metric_def.metric_type.value] += 1

            return dict(summary)

        except Exception as e:
            logger.error(f"Failed to get metrics summary: {e}")
            return {}

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts."""
        return [alert.to_dict() for alert in self.active_alerts.values()]

    def get_alert_history(
        self,
        severity: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get alert history with optional filtering."""
        history = self.alert_history

        if severity:
            history = [alert for alert in history if alert.severity == severity]

        # Sort by triggered time (most recent first)
        history.sort(key=lambda x: x.triggered_at, reverse=True)

        return [alert.to_dict() for alert in history[:limit]]


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get or create the global metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


async def start_metrics_collector():
    """Start the global metrics collector."""
    collector = get_metrics_collector()
    await collector.start()


async def stop_metrics_collector():
    """Stop the global metrics collector."""
    collector = get_metrics_collector()
    if collector:
        await collector.stop()
