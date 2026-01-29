"""
AgentMetricsCollector for Raptorflow agent system.
Collects, aggregates, and provides metrics for agent operations.
"""

import asyncio
import json
import logging
import statistics
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from ..config import ModelTier

from ..base import BaseAgent
from ..exceptions import MetricsError

logger = logging.getLogger(__name__)


class RequestStatus(Enum):
    """Request status for tracking."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MetricType(Enum):
    """Metric types."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class MetricAggregation(Enum):
    """Metric aggregation methods."""

    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    PERCENTILE = "percentile"


@dataclass
class MetricPoint:
    """Individual metric data point."""

    timestamp: datetime
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricDefinition:
    """Metric definition."""

    name: str
    metric_type: MetricType
    description: str
    unit: str
    labels: List[str] = field(default_factory=list)
    aggregation: MetricAggregation = MetricAggregation.SUM


@dataclass
class AggregatedMetric:
    """Aggregated metric data."""

    name: str
    aggregation_type: MetricAggregation
    value: float
    count: int
    min_value: float
    max_value: float
    avg_value: float
    percentiles: Dict[float, float] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MetricsConfig:
    """Metrics collector configuration."""

    retention_hours: int = 72
    aggregation_interval_seconds: int = 60
    max_points_per_metric: int = 10000
    enable_percentiles: bool = True
    percentile_values: List[float] = field(default_factory=lambda: [50, 90, 95, 99])
    enable_export: bool = True
    export_format: str = "json"  # json, prometheus, csv


class AgentMetricsCollector:
    """Collects and manages metrics for agent operations."""

    def __init__(self, config: MetricsConfig = None):
        self.config = config or MetricsConfig()

        # Metric storage
        self._metrics: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=self.config.max_points_per_metric)
        )
        self._metric_definitions: Dict[str, MetricDefinition] = {}
        self._aggregated_metrics: Dict[str, AggregatedMetric] = {}

        # Predefined metrics
        self._initialize_predefined_metrics()

        # Background tasks
        self._background_tasks: Set[asyncio.Task] = set()
        self._running = False

        # Event handlers
        self._event_handlers: Dict[str, List[Callable]] = defaultdict(list)

        # Locks
        self._metrics_lock = asyncio.Lock()

        # Start background tasks
        self._start_background_tasks()

    def _initialize_predefined_metrics(self):
        """Initialize predefined metric definitions."""
        predefined_metrics = [
            MetricDefinition(
                name="agent_requests_total",
                metric_type=MetricType.COUNTER,
                description="Total number of agent requests",
                unit="count",
                labels=["agent_id", "workspace_id", "status"],
            ),
            MetricDefinition(
                name="agent_response_time_seconds",
                metric_type=MetricType.HISTOGRAM,
                description="Agent response time in seconds",
                unit="seconds",
                labels=["agent_id", "model_tier"],
            ),
            MetricDefinition(
                name="agent_tokens_used_total",
                metric_type=MetricType.COUNTER,
                description="Total tokens used by agents",
                unit="tokens",
                labels=["agent_id", "model_tier"],
            ),
            MetricDefinition(
                name="agent_cost_estimate",
                metric_type=MetricType.GAUGE,
                description="Estimated cost of agent operations",
                unit="dollars",
                labels=["agent_id", "model_tier"],
            ),
            MetricDefinition(
                name="agent_error_rate",
                metric_type=MetricType.GAUGE,
                description="Agent error rate",
                unit="percentage",
                labels=["agent_id", "error_type"],
            ),
            MetricDefinition(
                name="workspace_active_agents",
                metric_type=MetricType.GAUGE,
                description="Number of active agents in workspace",
                unit="count",
                labels=["workspace_id"],
            ),
            MetricDefinition(
                name="system_cpu_usage",
                metric_type=MetricType.GAUGE,
                description="System CPU usage percentage",
                unit="percentage",
                labels=[],
            ),
            MetricDefinition(
                name="system_memory_usage",
                metric_type=MetricType.GAUGE,
                description="System memory usage percentage",
                unit="percentage",
                labels=[],
            ),
        ]

        for metric_def in predefined_metrics:
            self._metric_definitions[metric_def.name] = metric_def

    def define_metric(self, metric_def: MetricDefinition):
        """Define a new metric."""
        self._metric_definitions[metric_def.name] = metric_def
        logger.info(f"Defined metric: {metric_def.name}")

    async def record_metric(
        self,
        name: str,
        value: float,
        labels: Dict[str, str] = None,
        metadata: Dict[str, Any] = None,
    ):
        """Record a metric value."""
        async with self._metrics_lock:
            # Check if metric is defined
            if name not in self._metric_definitions:
                # Auto-define as gauge if not exists
                self.define_metric(
                    MetricDefinition(
                        name=name,
                        metric_type=MetricType.GAUGE,
                        description=f"Auto-defined metric: {name}",
                        unit="unit",
                    )
                )

            # Create metric point
            point = MetricPoint(
                timestamp=datetime.now(),
                value=value,
                labels=labels or {},
                metadata=metadata or {},
            )

            # Store metric point
            self._metrics[name].append(point)

            # Emit event
            await self._emit_event(
                "metric_recorded",
                {"metric_name": name, "value": value, "labels": labels},
            )

    async def increment_counter(
        self, name: str, labels: Dict[str, str] = None, value: float = 1.0
    ):
        """Increment a counter metric."""
        await self.record_metric(name, value, labels)

    async def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """Set a gauge metric value."""
        await self.record_metric(name, value, labels)

    async def record_timer(
        self, name: str, duration_seconds: float, labels: Dict[str, str] = None
    ):
        """Record a timer metric."""
        await self.record_metric(name, duration_seconds, labels)

    async def record_histogram(
        self, name: str, value: float, labels: Dict[str, str] = None
    ):
        """Record a histogram metric."""
        await self.record_metric(name, value, labels)

    async def get_metric(
        self,
        name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        labels: Dict[str, str] = None,
        aggregation: Optional[MetricAggregation] = None,
    ) -> AggregatedMetric:
        """Get aggregated metric data."""
        async with self._metrics_lock:
            # Get metric points
            points = list(self._metrics.get(name, []))

            if not points:
                raise MetricsError(f"No data for metric: {name}")

            # Filter by time range
            if start_time:
                points = [p for p in points if p.timestamp >= start_time]

            if end_time:
                points = [p for p in points if p.timestamp <= end_time]

            # Filter by labels
            if labels:
                points = [
                    p
                    for p in points
                    if all(p.labels.get(k) == v for k, v in labels.items())
                ]

            if not points:
                raise MetricsError(f"No data matching filters for metric: {name}")

            # Get metric definition
            metric_def = self._metric_definitions.get(name)
            if not metric_def:
                raise MetricsError(f"Metric not defined: {name}")

            # Determine aggregation method
            agg_method = aggregation or metric_def.aggregation

            # Extract values
            values = [p.value for p in points]

            # Calculate aggregation
            if agg_method == MetricAggregation.SUM:
                agg_value = sum(values)
            elif agg_method == MetricAggregation.AVERAGE:
                agg_value = statistics.mean(values)
            elif agg_method == MetricAggregation.MIN:
                agg_value = min(values)
            elif agg_method == MetricAggregation.MAX:
                agg_value = max(values)
            elif agg_method == MetricAggregation.PERCENTILE:
                # Default to 95th percentile
                agg_value = self._calculate_percentile(values, 95)
            else:
                agg_value = sum(values)  # Default to sum

            # Calculate percentiles if enabled
            percentiles = {}
            if self.config.enable_percentiles and len(values) > 1:
                for p in self.config.percentile_values:
                    percentiles[p] = self._calculate_percentile(values, p)

            # Create aggregated metric
            aggregated = AggregatedMetric(
                name=name,
                aggregation_type=agg_method,
                value=agg_value,
                count=len(values),
                min_value=min(values),
                max_value=max(values),
                avg_value=statistics.mean(values),
                percentiles=percentiles,
                labels=labels or {},
                timestamp=datetime.now(),
            )

            return aggregated

    async def get_metrics_summary(
        self,
        names: List[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> Dict[str, AggregatedMetric]:
        """Get summary of multiple metrics."""
        metrics_to_get = names or list(self._metric_definitions.keys())
        summary = {}

        for name in metrics_to_get:
            try:
                metric = await self.get_metric(name, start_time, end_time)
                summary[name] = metric
            except MetricsError:
                # Skip metrics without data
                continue

        return summary

    async def get_agent_metrics(self, agent_id: str) -> Dict[str, Any]:
        """Get metrics for a specific agent."""
        # Get agent-specific metrics
        agent_metrics = {}

        # Request count
        try:
            requests = await self.get_metric(
                "agent_requests_total", labels={"agent_id": agent_id}
            )
            agent_metrics["requests_total"] = requests.value
        except MetricsError:
            agent_metrics["requests_total"] = 0

        # Response time
        try:
            response_time = await self.get_metric(
                "agent_response_time_seconds", labels={"agent_id": agent_id}
            )
            agent_metrics["avg_response_time_ms"] = response_time.avg_value * 1000
            agent_metrics["p95_response_time_ms"] = (
                response_time.percentiles.get(95, 0) * 1000
            )
        except MetricsError:
            agent_metrics["avg_response_time_ms"] = 0
            agent_metrics["p95_response_time_ms"] = 0

        # Tokens used
        try:
            tokens = await self.get_metric(
                "agent_tokens_used_total", labels={"agent_id": agent_id}
            )
            agent_metrics["tokens_used"] = tokens.value
        except MetricsError:
            agent_metrics["tokens_used"] = 0

        # Cost estimate
        try:
            cost = await self.get_metric(
                "agent_cost_estimate", labels={"agent_id": agent_id}
            )
            agent_metrics["cost_estimate"] = cost.value
        except MetricsError:
            agent_metrics["cost_estimate"] = 0.0

        # Error rate
        try:
            error_rate = await self.get_metric(
                "agent_error_rate", labels={"agent_id": agent_id}
            )
            agent_metrics["error_rate"] = error_rate.value
        except MetricsError:
            agent_metrics["error_rate"] = 0.0

        return agent_metrics

    async def get_workspace_metrics(self, workspace_id: str) -> Dict[str, Any]:
        """Get metrics for a specific workspace."""
        workspace_metrics = {}

        # Active agents
        try:
            active_agents = await self.get_metric(
                "workspace_active_agents", labels={"workspace_id": workspace_id}
            )
            workspace_metrics["active_agents"] = active_agents.value
        except MetricsError:
            workspace_metrics["active_agents"] = 0

        # Total requests
        try:
            requests = await self.get_metric(
                "agent_requests_total", labels={"workspace_id": workspace_id}
            )
            workspace_metrics["total_requests"] = requests.value
        except MetricsError:
            workspace_metrics["total_requests"] = 0

        # Total cost
        try:
            cost = await self.get_metric(
                "agent_cost_estimate", labels={"workspace_id": workspace_id}
            )
            workspace_metrics["total_cost"] = cost.value
        except MetricsError:
            workspace_metrics["total_cost"] = 0.0

        return workspace_metrics

    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get system-level metrics."""
        system_metrics = {}

        # CPU usage
        try:
            cpu = await self.get_metric("system_cpu_usage")
            system_metrics["cpu_usage_percent"] = cpu.value
        except MetricsError:
            system_metrics["cpu_usage_percent"] = 0.0

        # Memory usage
        try:
            memory = await self.get_metric("system_memory_usage")
            system_metrics["memory_usage_percent"] = memory.value
        except MetricsError:
            system_metrics["memory_usage_percent"] = 0.0

        return system_metrics

    async def get_metrics(self, workspace_id: str) -> Dict[str, Any]:
        """Get comprehensive metrics for workspace."""
        metrics = {
            "workspace_id": workspace_id,
            "timestamp": datetime.now().isoformat(),
            "workspace_metrics": await self.get_workspace_metrics(workspace_id),
            "system_metrics": await get_system_metrics(),
            "agent_metrics": {},
        }

        # Get metrics for all agents in workspace
        # This would require tracking which agents belong to which workspace
        # For now, return empty dict

        return metrics

    async def record_agent_execution(
        self,
        agent_id: str,
        workspace_id: str,
        execution_time_ms: float,
        tokens_used: int,
        cost_estimate: float,
        success: bool,
    ):
        """Record agent execution metrics."""
        # Record request count
        status = "success" if success else "error"
        await self.increment_counter(
            "agent_requests_total",
            labels={
                "agent_id": agent_id,
                "workspace_id": workspace_id,
                "status": status,
            },
        )

        # Record response time
        await self.record_histogram(
            "agent_response_time_seconds",
            execution_time_ms / 1000.0,
            labels={"agent_id": agent_id},
        )

        # Record tokens used
        await self.increment_counter(
            "agent_tokens_used_total", tokens_used, labels={"agent_id": agent_id}
        )

        # Record cost estimate
        await self.set_gauge(
            "agent_cost_estimate", cost_estimate, labels={"agent_id": agent_id}
        )

    async def record_gateway_request(
        self, request_data: Dict[str, Any], processing_time: float, success: bool
    ):
        """Record gateway request metrics."""
        # Record gateway metrics
        await self.record_histogram(
            "gateway_request_duration_seconds",
            processing_time,
            labels={"request_type": request_data.get("request_type", "unknown")},
        )

        await self.increment_counter(
            "gateway_requests_total", labels={"success": str(success)}
        )

    async def record_workflow_registration(self, workflow_data: Dict[str, Any]):
        """Record workflow registration metrics."""
        await self.increment_counter("workflows_registered_total")

    async def record_workflow_completion(self, execution_data: Dict[str, Any]):
        """Record workflow completion metrics."""
        execution_time = execution_data.completed_at - execution_data.started_at
        await self.record_histogram(
            "workflow_execution_duration_seconds", execution_time.total_seconds()
        )

        await self.increment_counter(
            "workflows_completed_total", labels={"status": execution_data.status.value}
        )

    async def record_workflow_failure(self, execution_data: Dict[str, Any]):
        """Record workflow failure metrics."""
        await self.increment_counter("workflows_failed_total")

    async def record_dispatch(self, dispatch_result: Dict[str, Any]):
        """Record dispatch metrics."""
        await self.record_histogram(
            "dispatch_confidence_score",
            dispatch_result.confidence_score,
            labels={"strategy": dispatch_result.strategy_used},
        )

        await self.increment_counter("dispatches_total")

    async def export_metrics(self, format: str = None, output_file: str = None) -> str:
        """Export metrics in specified format."""
        export_format = format or self.config.export_format

        if export_format == "json":
            return await self._export_json(output_file)
        elif export_format == "prometheus":
            return await self._export_prometheus(output_file)
        elif export_format == "csv":
            return await self._export_csv(output_file)
        else:
            raise MetricsError(f"Unsupported export format: {export_format}")

    async def _export_json(self, output_file: str = None) -> str:
        """Export metrics as JSON."""
        export_data = {"timestamp": datetime.now().isoformat(), "metrics": {}}

        for name in self._metric_definitions:
            try:
                # Get last hour of data
                end_time = datetime.now()
                start_time = end_time - timedelta(hours=1)

                metric = await self.get_metric(name, start_time, end_time)
                export_data["metrics"][name] = {
                    "value": metric.value,
                    "count": metric.count,
                    "avg": metric.avg_value,
                    "min": metric.min_value,
                    "max": metric.max_value,
                    "percentiles": metric.percentiles,
                }
            except MetricsError:
                continue

        json_data = json.dumps(export_data, indent=2, default=str)

        if output_file:
            with open(output_file, "w") as f:
                f.write(json_data)

        return json_data

    async def _export_prometheus(self, output_file: str = None) -> str:
        """Export metrics in Prometheus format."""
        prometheus_lines = []

        for name in self._metric_definitions:
            try:
                metric = await self.get_metric(name)
                metric_def = self._metric_definitions[name]

                # Create metric line
                label_str = ""
                if metric.labels:
                    label_pairs = [f'{k}="{v}"' for k, v in metric.labels.items()]
                    label_str = "{" + ",".join(label_pairs) + "}"

                prometheus_lines.append(f"# HELP {name} {metric_def.description}")
                prometheus_lines.append(f"# TYPE {name} {metric_def.metric_type.value}")
                prometheus_lines.append(f"{name}{label_str} {metric.value}")

            except MetricsError:
                continue

        prometheus_data = "\n".join(prometheus_lines)

        if output_file:
            with open(output_file, "w") as f:
                f.write(prometheus_data)

        return prometheus_data

    async def _export_csv(self, output_file: str = None) -> str:
        """Export metrics as CSV."""
        csv_lines = ["metric_name,value,count,avg,min,max,timestamp"]

        for name in self._metric_definitions:
            try:
                metric = await self.get_metric(name)

                csv_lines.append(
                    f"{name},{metric.value},{metric.count},{metric.avg_value},{metric.min_value},{metric.max_value},{metric.timestamp.isoformat()}"
                )
            except MetricsError:
                continue

        csv_data = "\n".join(csv_lines)

        if output_file:
            with open(output_file, "w") as f:
                f.write(csv_data)

        return csv_data

    def _calculate_percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile of values."""
        if not values:
            return 0.0

        sorted_values = sorted(values)
        index = (percentile / 100.0) * (len(sorted_values) - 1)

        if index.is_integer():
            return sorted_values[int(index)]
        else:
            lower_index = int(index)
            upper_index = lower_index + 1

            if upper_index >= len(sorted_values):
                return sorted_values[-1]

            lower_value = sorted_values[lower_index]
            upper_value = sorted_values[upper_index]

            fraction = index - lower_index
            return lower_value + fraction * (upper_value - lower_value)

    async def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit metrics event."""
        event_data = {
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            **data,
        }

        # Call event handlers
        for handler in self._event_handlers[event_type]:
            try:
                await handler(event_data)
            except Exception as e:
                logger.error(f"Event handler failed: {e}")

    def add_event_handler(self, event_type: str, handler: Callable):
        """Add event handler."""
        self._event_handlers[event_type].append(handler)

    def _start_background_tasks(self):
        """Start background tasks."""
        self._running = True

        # Aggregation task
        self._background_tasks.add(asyncio.create_task(self._aggregation_loop()))

        # Cleanup task
        self._background_tasks.add(asyncio.create_task(self._cleanup_loop()))

    async def _aggregation_loop(self):
        """Background aggregation loop."""
        while self._running:
            try:
                # Aggregate metrics
                for name in self._metric_definitions:
                    try:
                        # Get recent data
                        end_time = datetime.now()
                        start_time = end_time - timedelta(
                            seconds=self.config.aggregation_interval_seconds
                        )

                        aggregated = await self.get_metric(name, start_time, end_time)
                        self._aggregated_metrics[name] = aggregated

                    except MetricsError:
                        continue

                # Sleep until next aggregation
                await asyncio.sleep(self.config.aggregation_interval_seconds)

            except Exception as e:
                logger.error(f"Aggregation loop failed: {e}")
                await asyncio.sleep(10)

    async def _cleanup_loop(self):
        """Background cleanup loop."""
        while self._running:
            try:
                # Clean up old metric points
                cutoff_time = datetime.now() - timedelta(
                    hours=self.config.retention_hours
                )

                cleaned_points = 0
                for name, points in self._metrics.items():
                    original_count = len(points)

                    # Remove old points
                    while points and points[0].timestamp < cutoff_time:
                        points.popleft()
                        cleaned_points += 1

                    if len(points) != original_count:
                        logger.debug(
                            f"Cleaned {original_count - len(points)} old points from metric: {name}"
                        )

                if cleaned_points > 0:
                    logger.info(f"Cleaned up {cleaned_points} old metric points")

                # Sleep for 1 hour
                await asyncio.sleep(3600)

            except Exception as e:
                logger.error(f"Cleanup loop failed: {e}")
                await asyncio.sleep(300)  # Retry after 5 minutes

    async def get_collector_statistics(self) -> Dict[str, Any]:
        """Get metrics collector statistics."""
        total_points = sum(len(points) for points in self._metrics.values())

        return {
            "total_metrics": len(self._metric_definitions),
            "total_points": total_points,
            "aggregated_metrics": len(self._aggregated_metrics),
            "retention_hours": self.config.retention_hours,
            "aggregation_interval_seconds": self.config.aggregation_interval_seconds,
            "max_points_per_metric": self.config.max_points_per_metric,
            "background_tasks_running": self._running,
            "background_task_count": len(self._background_tasks),
        }

    async def stop(self):
        """Stop metrics collector."""
        self._running = False

        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()


# Request tracking functions for backward compatibility
def start_request_tracking(request_id: str, agent_id: str, request_type: str):
    """Start tracking a request."""
    # Simple implementation - can be extended
    return {
        "request_id": request_id,
        "agent_id": agent_id,
        "request_type": request_type,
        "status": RequestStatus.PENDING,
        "start_time": datetime.now(),
    }


def end_request_tracking(
    request_data: dict, status: RequestStatus, result: Any = None, error: str = None
):
    """End tracking a request."""
    # Simple implementation - can be extended
    request_data["status"] = status
    request_data["end_time"] = datetime.now()
    request_data["duration"] = (
        request_data["end_time"] - request_data["start_time"]
    ).total_seconds()
    if result is not None:
        request_data["result"] = result
    if error:
        request_data["error"] = error
    return request_data
