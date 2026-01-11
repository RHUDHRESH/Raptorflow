"""
Cognitive Monitor for Integration Components

Real-time monitoring and metrics for cognitive processing.
Implements PROMPT 65 from STREAM_3_COGNITIVE_ENGINE.
"""

import asyncio
import json
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from ..models import ExecutionPlan, PerceivedInput, ReflectionResult


class MetricType(Enum):
    """Types of cognitive metrics."""

    PERFORMANCE = "performance"
    QUALITY = "quality"
    COST = "cost"
    ERROR = "error"
    USAGE = "usage"
    RESOURCE = "resource"


class AlertSeverity(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class MetricPoint:
    """A single metric data point."""

    metric_name: str
    metric_type: MetricType
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricAggregation:
    """Aggregated metric data."""

    metric_name: str
    metric_type: MetricType
    aggregation_type: str  # "avg", "min", "max", "sum", "count"
    value: float
    period_start: datetime
    period_end: datetime
    sample_count: int
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class Alert:
    """A monitoring alert."""

    alert_id: str
    severity: AlertSeverity
    title: str
    description: str
    metric_name: str
    threshold_value: float
    actual_value: float
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class ExecutionTrace:
    """Trace of a cognitive execution."""

    execution_id: str
    workspace_id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_ms: Optional[int]
    status: str
    stages: List[Dict[str, Any]]
    metrics: List[MetricPoint]
    errors: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)


class CognitiveMonitor:
    """
    Real-time monitoring and metrics for cognitive processing.

    Tracks performance, quality, costs, and system health.
    """

    def __init__(self, storage_client=None, notification_client=None):
        """
        Initialize the cognitive monitor.

        Args:
            storage_client: Client for persistent storage
            notification_client: Client for alert notifications
        """
        self.storage_client = storage_client
        self.notification_client = notification_client

        # In-memory storage for real-time data
        self.metrics_buffer: deque = deque(maxlen=10000)  # Last 10k metrics
        self.active_traces: Dict[str, ExecutionTrace] = {}
        self.alerts: Dict[str, Alert] = {}

        # Metric aggregations
        self.aggregated_metrics: Dict[str, List[MetricAggregation]] = defaultdict(list)

        # Alert rules
        self.alert_rules: List[Dict[str, Any]] = []
        self._setup_default_alert_rules()

        # Monitoring configuration
        self.config = {
            "metrics_retention_hours": 24,
            "trace_retention_hours": 72,
            "alert_retention_hours": 168,  # 1 week
            "aggregation_interval_minutes": 5,
            "enable_real_time_monitoring": True,
            "enable_alerts": True,
        }

        # Background tasks
        self._monitoring_task: Optional[asyncio.Task] = None
        self._aggregation_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None

    async def start_monitoring(self) -> None:
        """Start background monitoring tasks."""
        if self.config["enable_real_time_monitoring"]:
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())
            self._aggregation_task = asyncio.create_task(self._aggregation_loop())
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def stop_monitoring(self) -> None:
        """Stop background monitoring tasks."""
        tasks = [self._monitoring_task, self._aggregation_task, self._cleanup_task]

        for task in tasks:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

    async def track_execution_start(
        self, execution_id: str, plan: ExecutionPlan
    ) -> None:
        """Track the start of an execution."""
        trace = ExecutionTrace(
            execution_id=execution_id,
            workspace_id=plan.metadata.get("workspace_id", "unknown"),
            user_id=plan.metadata.get("user_id", "unknown"),
            start_time=datetime.now(),
            end_time=None,
            duration_ms=None,
            status="running",
            stages=[],
            metrics=[],
            errors=[],
            metadata={
                "plan_goal": plan.goal,
                "plan_steps": len(plan.steps),
                "estimated_cost": plan.total_cost.total_cost_usd,
            },
        )

        self.active_traces[execution_id] = trace

        # Record start metric
        await self.record_metric(
            "execution_started",
            MetricType.USAGE,
            1.0,
            tags={
                "execution_id": execution_id,
                "workspace_id": trace.workspace_id,
                "user_id": trace.user_id,
            },
        )

    async def track_execution_complete(self, execution_id: str, result: Any) -> None:
        """Track the completion of an execution."""
        trace = self.active_traces.get(execution_id)
        if not trace:
            return

        trace.end_time = datetime.now()
        trace.duration_ms = int(
            (trace.end_time - trace.start_time).total_seconds() * 1000
        )
        trace.status = "completed"

        # Extract metrics from result
        if hasattr(result, "total_tokens_used"):
            await self.record_metric(
                "execution_tokens",
                MetricType.COST,
                result.total_tokens_used,
                tags={"execution_id": execution_id},
            )

        if hasattr(result, "total_cost_usd"):
            await self.record_metric(
                "execution_cost",
                MetricType.COST,
                result.total_cost_usd,
                tags={"execution_id": execution_id},
            )

        # Record completion metric
        await self.record_metric(
            "execution_completed",
            MetricType.USAGE,
            1.0,
            tags={
                "execution_id": execution_id,
                "duration_ms": str(trace.duration_ms),
                "status": trace.status,
            },
        )

        # Move to completed traces (keep for retention period)
        await self._archive_trace(trace)
        self.active_traces.pop(execution_id, None)

    async def track_execution_error(
        self, execution_id: str, result: Any, error: Exception
    ) -> None:
        """Track an execution error."""
        trace = self.active_traces.get(execution_id)
        if not trace:
            return

        trace.end_time = datetime.now()
        trace.duration_ms = int(
            (trace.end_time - trace.start_time).total_seconds() * 1000
        )
        trace.status = "failed"
        trace.errors.append(
            {
                "error": str(error),
                "type": type(error).__name__,
                "timestamp": datetime.now().isoformat(),
            }
        )

        # Record error metric
        await self.record_metric(
            "execution_error",
            MetricType.ERROR,
            1.0,
            tags={"execution_id": execution_id, "error_type": type(error).__name__},
        )

        # Check for alert conditions
        await self._check_error_alerts(execution_id, error)

        # Archive trace
        await self._archive_trace(trace)
        self.active_traces.pop(execution_id, None)

    async def track_stage_metrics(
        self, execution_id: str, stage_name: str, metrics: Dict[str, Any]
    ) -> None:
        """Track metrics for a specific stage."""
        trace = self.active_traces.get(execution_id)
        if not trace:
            return

        stage_data = {
            "stage": stage_name,
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
        }

        trace.stages.append(stage_data)

        # Record stage metrics
        for metric_name, value in metrics.items():
            if isinstance(value, (int, float)):
                await self.record_metric(
                    f"stage_{stage_name}_{metric_name}",
                    MetricType.PERFORMANCE,
                    float(value),
                    tags={"execution_id": execution_id, "stage": stage_name},
                )

    async def record_metric(
        self,
        metric_name: str,
        metric_type: MetricType,
        value: float,
        tags: Dict[str, str] = None,
        metadata: Dict[str, Any] = None,
    ) -> None:
        """Record a metric point."""
        metric = MetricPoint(
            metric_name=metric_name,
            metric_type=metric_type,
            value=value,
            timestamp=datetime.now(),
            tags=tags or {},
            metadata=metadata or {},
        )

        # Add to buffer
        self.metrics_buffer.append(metric)

        # Check for alerts
        if self.config["enable_alerts"]:
            await self._check_metric_alerts(metric)

    async def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get status of an execution."""
        trace = self.active_traces.get(execution_id)
        if not trace:
            return None

        return {
            "execution_id": execution_id,
            "status": trace.status,
            "start_time": trace.start_time.isoformat(),
            "duration_ms": trace.duration_ms,
            "stages_completed": len(trace.stages),
            "errors_count": len(trace.errors),
            "workspace_id": trace.workspace_id,
            "user_id": trace.user_id,
        }

    async def get_metrics(
        self,
        metric_name: str = None,
        metric_type: MetricType = None,
        start_time: datetime = None,
        end_time: datetime = None,
        tags: Dict[str, str] = None,
    ) -> List[MetricPoint]:
        """Get metrics with optional filtering."""
        filtered_metrics = []

        for metric in self.metrics_buffer:
            # Filter by name
            if metric_name and metric.metric_name != metric_name:
                continue

            # Filter by type
            if metric_type and metric.metric_type != metric_type:
                continue

            # Filter by time range
            if start_time and metric.timestamp < start_time:
                continue
            if end_time and metric.timestamp > end_time:
                continue

            # Filter by tags
            if tags:
                if not all(metric.tags.get(k) == v for k, v in tags.items()):
                    continue

            filtered_metrics.append(metric)

        return filtered_metrics

    async def get_aggregated_metrics(
        self, metric_name: str, aggregation_type: str = "avg", period_minutes: int = 60
    ) -> List[MetricAggregation]:
        """Get aggregated metrics for a time period."""
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=period_minutes)

        # Get recent metrics
        recent_metrics = await self.get_metrics(
            metric_name=metric_name, start_time=start_time, end_time=end_time
        )

        if not recent_metrics:
            return []

        # Calculate aggregation
        values = [m.value for m in recent_metrics]

        if aggregation_type == "avg":
            agg_value = sum(values) / len(values)
        elif aggregation_type == "min":
            agg_value = min(values)
        elif aggregation_type == "max":
            agg_value = max(values)
        elif aggregation_type == "sum":
            agg_value = sum(values)
        elif aggregation_type == "count":
            agg_value = len(values)
        else:
            agg_value = sum(values) / len(values)  # Default to avg

        # Get tags from first metric (assuming consistent tags)
        tags = recent_metrics[0].tags if recent_metrics else {}

        aggregation = MetricAggregation(
            metric_name=metric_name,
            metric_type=recent_metrics[0].metric_type,
            aggregation_type=aggregation_type,
            value=agg_value,
            period_start=start_time,
            period_end=end_time,
            sample_count=len(values),
            tags=tags,
        )

        return [aggregation]

    async def get_alerts(
        self, severity: AlertSeverity = None, resolved: bool = None
    ) -> List[Alert]:
        """Get alerts with optional filtering."""
        filtered_alerts = []

        for alert in self.alerts.values():
            # Filter by severity
            if severity and alert.severity != severity:
                continue

            # Filter by resolved status
            if resolved is not None and alert.resolved != resolved:
                continue

            filtered_alerts.append(alert)

        # Sort by timestamp (newest first)
        filtered_alerts.sort(key=lambda a: a.timestamp, reverse=True)

        return filtered_alerts

    async def create_alert(
        self,
        severity: AlertSeverity,
        title: str,
        description: str,
        metric_name: str,
        threshold_value: float,
        actual_value: float,
        tags: Dict[str, str] = None,
    ) -> Alert:
        """Create a new alert."""
        alert = Alert(
            alert_id=str(uuid.uuid4()),
            severity=severity,
            title=title,
            description=description,
            metric_name=metric_name,
            threshold_value=threshold_value,
            actual_value=actual_value,
            timestamp=datetime.now(),
            tags=tags or {},
        )

        self.alerts[alert.alert_id] = alert

        # Send notification
        if self.notification_client:
            await self.notification_client.send_alert(alert)

        return alert

    async def resolve_alert(self, alert_id: str, resolution_note: str = None) -> bool:
        """Resolve an alert."""
        alert = self.alerts.get(alert_id)
        if not alert:
            return False

        alert.resolved = True
        alert.resolved_at = datetime.now()

        if resolution_note:
            alert.metadata["resolution_note"] = resolution_note

        return True

    def _setup_default_alert_rules(self) -> None:
        """Setup default alert rules."""
        self.alert_rules = [
            {
                "metric_name": "execution_error",
                "condition": "rate",
                "threshold": 0.1,  # 10% error rate
                "period_minutes": 5,
                "severity": "warning",
            },
            {
                "metric_name": "execution_cost",
                "condition": "avg",
                "threshold": 5.0,  # $5 average cost
                "period_minutes": 60,
                "severity": "warning",
            },
            {
                "metric_name": "execution_duration",
                "condition": "p95",
                "threshold": 30000,  # 30 seconds
                "period_minutes": 15,
                "severity": "error",
            },
        ]

    async def _check_metric_alerts(self, metric: MetricPoint) -> None:
        """Check if metric triggers any alert rules."""
        for rule in self.alert_rules:
            if rule["metric_name"] != metric.metric_name:
                continue

            # Get metrics for the period
            period_metrics = await self.get_metrics(
                metric_name=metric.metric_name,
                start_time=datetime.now() - timedelta(minutes=rule["period_minutes"]),
            )

            if not period_metrics:
                continue

            values = [m.value for m in period_metrics]

            # Check condition
            triggered = False
            actual_value = 0

            if rule["condition"] == "rate":
                # Rate of specific value (e.g., error rate)
                if metric.metric_name == "execution_error":
                    error_count = len(values)
                    total_count = await self._get_metric_count(
                        "execution_started", rule["period_minutes"]
                    )
                    actual_value = error_count / max(total_count, 1)
                    triggered = actual_value > rule["threshold"]

            elif rule["condition"] == "avg":
                actual_value = sum(values) / len(values)
                triggered = actual_value > rule["threshold"]

            elif rule["condition"] == "p95":
                sorted_values = sorted(values)
                index = int(len(sorted_values) * 0.95)
                actual_value = sorted_values[min(index, len(sorted_values) - 1)]
                triggered = actual_value > rule["threshold"]

            elif rule["condition"] == "max":
                actual_value = max(values)
                triggered = actual_value > rule["threshold"]

            # Create alert if triggered
            if triggered:
                await self.create_alert(
                    severity=AlertSeverity(rule["severity"]),
                    title=f"Alert: {metric.metric_name}",
                    description=f"{metric.metric_name} {rule['condition']} ({actual_value:.2f}) exceeds threshold ({rule['threshold']})",
                    metric_name=metric.metric_name,
                    threshold_value=rule["threshold"],
                    actual_value=actual_value,
                    tags=metric.tags,
                )

    async def _check_error_alerts(self, execution_id: str, error: Exception) -> None:
        """Check for error-specific alerts."""
        # Check for repeated errors from same user/workspace
        trace = self.active_traces.get(execution_id)
        if not trace:
            return

        # Count recent errors for this workspace
        recent_errors = await self.get_metrics(
            metric_name="execution_error",
            tags={"workspace_id": trace.workspace_id},
            start_time=datetime.now() - timedelta(minutes=10),
        )

        if len(recent_errors) > 5:  # More than 5 errors in 10 minutes
            await self.create_alert(
                severity=AlertSeverity.ERROR,
                title="High Error Rate Detected",
                description=f"Workspace {trace.workspace_id} has {len(recent_errors)} errors in last 10 minutes",
                metric_name="execution_error",
                threshold_value=5.0,
                actual_value=len(recent_errors),
                tags={"workspace_id": trace.workspace_id},
            )

    async def _get_metric_count(self, metric_name: str, period_minutes: int) -> int:
        """Get count of metric occurrences in period."""
        metrics = await self.get_metrics(
            metric_name=metric_name,
            start_time=datetime.now() - timedelta(minutes=period_minutes),
        )
        return len(metrics)

    async def _archive_trace(self, trace: ExecutionTrace) -> None:
        """Archive a trace to storage."""
        if self.storage_client:
            await self.storage_client.set(
                "execution_traces",
                trace.execution_id,
                {
                    "execution_id": trace.execution_id,
                    "workspace_id": trace.workspace_id,
                    "user_id": trace.user_id,
                    "start_time": trace.start_time.isoformat(),
                    "end_time": trace.end_time.isoformat() if trace.end_time else None,
                    "duration_ms": trace.duration_ms,
                    "status": trace.status,
                    "stages": trace.stages,
                    "metrics": [
                        {
                            "metric_name": m.metric_name,
                            "metric_type": m.metric_type.value,
                            "value": m.value,
                            "timestamp": m.timestamp.isoformat(),
                            "tags": m.tags,
                        }
                        for m in trace.metrics
                    ],
                    "errors": trace.errors,
                    "metadata": trace.metadata,
                },
            )

    async def _monitoring_loop(self) -> None:
        """Background monitoring loop."""
        while True:
            try:
                # Process any pending monitoring tasks
                await self._process_monitoring_queue()
                await asyncio.sleep(1)  # Check every second
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Monitoring loop error: {e}")
                await asyncio.sleep(5)  # Wait before retrying

    async def _aggregation_loop(self) -> None:
        """Background aggregation loop."""
        while True:
            try:
                # Aggregate metrics
                await self._aggregate_metrics()
                await asyncio.sleep(300)  # Aggregate every 5 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Aggregation loop error: {e}")
                await asyncio.sleep(60)  # Wait before retrying

    async def _cleanup_loop(self) -> None:
        """Background cleanup loop."""
        while True:
            try:
                # Clean up old data
                await self._cleanup_old_data()
                await asyncio.sleep(3600)  # Clean every hour
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Cleanup loop error: {e}")
                await asyncio.sleep(300)  # Wait before retrying

    async def _process_monitoring_queue(self) -> None:
        """Process monitoring queue (placeholder)."""
        # This would process any queued monitoring tasks
        pass

    async def _aggregate_metrics(self) -> None:
        """Aggregate metrics for storage."""
        # Get recent metrics
        recent_metrics = list(self.metrics_buffer)

        # Group by metric name and type
        metric_groups = defaultdict(list)
        for metric in recent_metrics:
            key = f"{metric.metric_name}_{metric.metric_type.value}"
            metric_groups[key].append(metric)

        # Calculate aggregations
        for key, metrics in metric_groups.items():
            if len(metrics) < 2:
                continue

            metric_name, metric_type = key.split("_", 1)

            # Calculate various aggregations
            values = [m.value for m in metrics]

            aggregations = [
                ("avg", sum(values) / len(values)),
                ("min", min(values)),
                ("max", max(values)),
                ("sum", sum(values)),
            ]

            for agg_type, agg_value in aggregations:
                aggregation = MetricAggregation(
                    metric_name=metric_name,
                    metric_type=MetricType(metric_type),
                    aggregation_type=agg_type,
                    value=agg_value,
                    period_start=min(m.timestamp for m in metrics),
                    period_end=max(m.timestamp for m in metrics),
                    sample_count=len(values),
                    tags=metrics[0].tags,
                )

                self.aggregated_metrics[key].append(aggregation)

    async def _cleanup_old_data(self) -> None:
        """Clean up old data based on retention policies."""
        cutoff_time = datetime.now() - timedelta(
            hours=self.config["metrics_retention_hours"]
        )

        # Clean old metrics from buffer
        self.metrics_buffer = deque(
            (m for m in self.metrics_buffer if m.timestamp > cutoff_time),
            maxlen=self.metrics_buffer.maxlen,
        )

        # Clean old alerts
        alert_cutoff = datetime.now() - timedelta(
            hours=self.config["alert_retention_hours"]
        )
        old_alerts = [
            alert_id
            for alert_id, alert in self.alerts.items()
            if alert.timestamp < alert_cutoff and alert.resolved
        ]

        for alert_id in old_alerts:
            self.alerts.pop(alert_id, None)

    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics."""
        return {
            "active_traces": len(self.active_traces),
            "buffered_metrics": len(self.metrics_buffer),
            "active_alerts": len([a for a in self.alerts.values() if not a.resolved]),
            "total_alerts": len(self.alerts),
            "alert_rules": len(self.alert_rules),
            "aggregated_metrics": sum(
                len(aggs) for aggs in self.aggregated_metrics.values()
            ),
            "monitoring_enabled": self.config["enable_real_time_monitoring"],
            "alerts_enabled": self.config["enable_alerts"],
        }
