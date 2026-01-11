"""
Google Cloud Monitoring integration for Raptorflow.

Provides custom metrics collection, alerting, and
monitoring dashboard capabilities.
"""

import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from google.api_core import exceptions
from google.cloud import monitoring_v3
from google.cloud.monitoring_v3 import (
    AlertPolicyServiceClient,
    MetricServiceClient,
    NotificationChannelServiceClient,
)

from .gcp import get_gcp_client

logger = logging.getLogger(__name__)


class MetricKind(Enum):
    """Metric kinds."""

    GAUGE = "GAUGE"
    DELTA = "DELTA"
    CUMULATIVE = "CUMULATIVE"


class ValueType(Enum):
    """Value types for metrics."""

    BOOL = "BOOL"
    INT64 = "INT64"
    DOUBLE = "DOUBLE"
    STRING = "STRING"
    DISTRIBUTION = "DISTRIBUTION"


class AlertSeverity(Enum):
    """Alert severity levels."""

    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class NotificationChannelType(Enum):
    """Notification channel types."""

    EMAIL = "email"
    SLACK = "slack"
    PAGERDUTY = "pagerduty"
    SMS = "sms"
    WEBHOOK = "webhook"


@dataclass
class MetricDescriptor:
    """Metric descriptor definition."""

    name: str
    display_name: str
    description: str
    metric_kind: MetricKind
    value_type: ValueType
    unit: str
    labels: Dict[str, str] = None

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.metric_kind, str):
            self.metric_kind = MetricKind(self.metric_kind)
        if isinstance(self.value_type, str):
            self.value_type = ValueType(self.value_type)

        if self.labels is None:
            self.labels = {}


@dataclass
class MetricPoint:
    """Single metric data point."""

    value: Union[bool, int, float, str]
    timestamp: datetime
    labels: Dict[str, str] = None

    def __post_init__(self):
        """Post-initialization processing."""
        if self.labels is None:
            self.labels = {}


@dataclass
class AlertCondition:
    """Alert condition definition."""

    display_name: str
    filter_expression: str
    duration_seconds: int
    trigger_threshold_value: float
    trigger_threshold_comparison: str  # "COMPARISON_LT", "COMPARISON_GT", etc.
    aggregation_period: str = "60s"
    aggregation_alignment: str = "ALIGN_MEAN"

    def __post_init__(self):
        """Post-initialization processing."""
        if not self.trigger_threshold_comparison.startswith("COMPARISON_"):
            self.trigger_threshold_comparison = (
                f"COMPARISON_{self.trigger_threshold_comparison.upper()}"
            )


@dataclass
class AlertPolicy:
    """Alert policy definition."""

    name: str
    display_name: str
    description: str
    conditions: List[AlertCondition]
    severity: AlertSeverity = AlertSeverity.WARNING
    enabled: bool = True
    notification_channels: List[str] = None

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.severity, str):
            self.severity = AlertSeverity(self.severity)

        if self.notification_channels is None:
            self.notification_channels = []


class CloudMonitoring:
    """Google Cloud Monitoring client for Raptorflow."""

    def __init__(self):
        self.gcp_client = get_gcp_client()
        self.logger = logging.getLogger("cloud_monitoring")

        # Get Cloud Monitoring clients
        self.metric_client = MetricServiceClient(
            credentials=self.gcp_client.get_credentials()
        )
        self.alert_client = AlertPolicyServiceClient(
            credentials=self.gcp_client.get_credentials()
        )
        self.notification_client = NotificationChannelServiceClient(
            credentials=self.gcp_client.get_credentials()
        )

        # Project ID
        self.project_id = self.gcp_client.get_project_id()
        self.project_name = f"projects/{self.project_id}"

        # Metric prefix
        self.metric_prefix = os.getenv("MONITORING_METRIC_PREFIX", "raptorflow")

        # Default metric descriptors
        self._default_metrics = {}
        self._setup_default_metrics()

    def _setup_default_metrics(self):
        """Setup default metric descriptors."""
        self._default_metrics = {
            "agent_executions": MetricDescriptor(
                name="agent_executions",
                display_name="Agent Executions",
                description="Number of agent executions",
                metric_kind=MetricKind.CUMULATIVE,
                value_type=ValueType.INT64,
                unit="1",
                labels={
                    "agent_type": "Type of agent",
                    "status": "Execution status",
                    "workspace_id": "Workspace identifier",
                },
            ),
            "agent_execution_time": MetricDescriptor(
                name="agent_execution_time",
                display_name="Agent Execution Time",
                description="Time taken for agent execution",
                metric_kind=MetricKind.GAUGE,
                value_type=ValueType.DOUBLE,
                unit="ms",
                labels={
                    "agent_type": "Type of agent",
                    "workspace_id": "Workspace identifier",
                },
            ),
            "api_requests": MetricDescriptor(
                name="api_requests",
                display_name="API Requests",
                description="Number of API requests",
                metric_kind=MetricKind.CUMULATIVE,
                value_type=ValueType.INT64,
                unit="1",
                labels={
                    "method": "HTTP method",
                    "endpoint": "API endpoint",
                    "status_code": "HTTP status code",
                    "workspace_id": "Workspace identifier",
                },
            ),
            "api_response_time": MetricDescriptor(
                name="api_response_time",
                display_name="API Response Time",
                description="API response time",
                metric_kind=MetricKind.GAUGE,
                value_type=ValueType.DOUBLE,
                unit="ms",
                labels={
                    "method": "HTTP method",
                    "endpoint": "API endpoint",
                    "workspace_id": "Workspace identifier",
                },
            ),
            "active_users": MetricDescriptor(
                name="active_users",
                display_name="Active Users",
                description="Number of active users",
                metric_kind=MetricKind.GAUGE,
                value_type=ValueType.INT64,
                unit="1",
                labels={"workspace_id": "Workspace identifier"},
            ),
            "error_rate": MetricDescriptor(
                name="error_rate",
                display_name="Error Rate",
                description="Error rate percentage",
                metric_kind=MetricKind.GAUGE,
                value_type=ValueType.DOUBLE,
                unit="%",
                labels={
                    "component": "System component",
                    "error_type": "Type of error",
                    "workspace_id": "Workspace identifier",
                },
            ),
            "memory_usage": MetricDescriptor(
                name="memory_usage",
                display_name="Memory Usage",
                description="Memory usage in bytes",
                metric_kind=MetricKind.GAUGE,
                value_type=ValueType.INT64,
                unit="By",
                labels={
                    "component": "System component",
                    "workspace_id": "Workspace identifier",
                },
            ),
            "queue_length": MetricDescriptor(
                name="queue_length",
                display_name="Queue Length",
                description="Number of items in queue",
                metric_kind=MetricKind.GAUGE,
                value_type=ValueType.INT64,
                unit="1",
                labels={
                    "queue_name": "Queue name",
                    "workspace_id": "Workspace identifier",
                },
            ),
        }

    def _get_metric_type(self, metric_name: str) -> str:
        """Get full metric type."""
        return f"custom.googleapis.com/{self.metric_prefix}/{metric_name}"

    async def create_metric_descriptor(self, descriptor: MetricDescriptor) -> bool:
        """Create a custom metric descriptor."""
        try:
            metric_type = self._get_metric_type(descriptor.name)

            # Build descriptor
            metric_descriptor = monitoring_v3.MetricDescriptor(
                name=metric_type,
                type=metric_type,
                metric_kind=monitoring_v3.MetricDescriptor.MetricKind[
                    descriptor.metric_kind.value
                ],
                value_type=monitoring_v3.MetricDescriptor.ValueType[
                    descriptor.value_type.value
                ],
                unit=descriptor.unit,
                display_name=descriptor.display_name,
                description=descriptor.description,
            )

            # Add labels
            if descriptor.labels:
                for key, description in descriptor.labels.items():
                    label_key = monitoring_v3.LabelDescriptor(
                        key=key,
                        value_type=monitoring_v3.LabelDescriptor.ValueType.STRING,
                        description=description,
                    )
                    metric_descriptor.labels.append(label_key)

            # Create descriptor
            self.metric_client.create_metric_descriptor(
                name=self.project_name, metric_descriptor=metric_descriptor
            )

            self.logger.info(f"Created metric descriptor: {descriptor.name}")
            return True

        except exceptions.AlreadyExists:
            self.logger.info(f"Metric descriptor {descriptor.name} already exists")
            return True
        except Exception as e:
            self.logger.error(
                f"Failed to create metric descriptor {descriptor.name}: {e}"
            )
            return False

    async def record_metric(
        self,
        metric_name: str,
        value: Union[bool, int, float, str],
        labels: Optional[Dict[str, str]] = None,
        timestamp: Optional[datetime] = None,
    ) -> bool:
        """Record a metric value."""
        try:
            # Get metric descriptor
            descriptor = self._default_metrics.get(metric_name)
            if not descriptor:
                self.logger.warning(f"Unknown metric: {metric_name}")
                return False

            # Create metric descriptor if needed
            await self.create_metric_descriptor(descriptor)

            # Build time series
            metric_type = self._get_metric_type(metric_name)

            # Create metric
            metric = monitoring_v3.Metric(type=metric_type)

            # Add labels
            if labels:
                for key, value in labels.items():
                    metric.labels[key] = value

            # Create point
            if timestamp is None:
                timestamp = datetime.utcnow()

            seconds = int(timestamp.timestamp())
            nanos = int(timestamp.microsecond * 1000)

            # Create value based on type
            if descriptor.value_type == ValueType.BOOL:
                typed_value = monitoring_v3.TypedValue(bool_value=bool(value))
            elif descriptor.value_type == ValueType.INT64:
                typed_value = monitoring_v3.TypedValue(int64_value=int(value))
            elif descriptor.value_type == ValueType.DOUBLE:
                typed_value = monitoring_v3.TypedValue(double_value=float(value))
            elif descriptor.value_type == ValueType.STRING:
                typed_value = monitoring_v3.TypedValue(string_value=str(value))
            else:
                raise ValueError(f"Unsupported value type: {descriptor.value_type}")

            point = monitoring_v3.Point(
                interval=monitoring_v3.TimeInterval(
                    end_time={"seconds": seconds, "nanos": nanos}
                ),
                value=typed_value,
            )

            # Create time series
            time_series = monitoring_v3.TimeSeries(metric=metric, points=[point])

            # Write time series
            self.metric_client.create_time_series(
                name=self.project_name, time_series=[time_series]
            )

            self.logger.debug(f"Recorded metric: {metric_name} = {value}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to record metric {metric_name}: {e}")
            return False

    async def record_metric_batch(self, metrics: List[Dict[str, Any]]) -> bool:
        """Record multiple metrics in batch."""
        try:
            time_series_list = []

            for metric_data in metrics:
                metric_name = metric_data["name"]
                value = metric_data["value"]
                labels = metric_data.get("labels", {})
                timestamp = metric_data.get("timestamp")

                # Get descriptor
                descriptor = self._default_metrics.get(metric_name)
                if not descriptor:
                    self.logger.warning(f"Unknown metric: {metric_name}")
                    continue

                # Create metric descriptor if needed
                await self.create_metric_descriptor(descriptor)

                # Build time series
                metric_type = self._get_metric_type(metric_name)
                metric = monitoring_v3.Metric(type=metric_type)

                # Add labels
                if labels:
                    for key, value in labels.items():
                        metric.labels[key] = value

                # Create point
                if timestamp is None:
                    timestamp = datetime.utcnow()

                seconds = int(timestamp.timestamp())
                nanos = int(timestamp.microsecond * 1000)

                # Create value
                if descriptor.value_type == ValueType.BOOL:
                    typed_value = monitoring_v3.TypedValue(bool_value=bool(value))
                elif descriptor.value_type == ValueType.INT64:
                    typed_value = monitoring_v3.TypedValue(int64_value=int(value))
                elif descriptor.value_type == ValueType.DOUBLE:
                    typed_value = monitoring_v3.TypedValue(double_value=float(value))
                elif descriptor.value_type == ValueType.STRING:
                    typed_value = monitoring_v3.TypedValue(string_value=str(value))
                else:
                    continue

                point = monitoring_v3.Point(
                    interval=monitoring_v3.TimeInterval(
                        end_time={"seconds": seconds, "nanos": nanos}
                    ),
                    value=typed_value,
                )

                time_series = monitoring_v3.TimeSeries(metric=metric, points=[point])

                time_series_list.append(time_series)

            # Write time series
            if time_series_list:
                self.metric_client.create_time_series(
                    name=self.project_name, time_series=time_series_list
                )

            self.logger.info(f"Recorded {len(time_series_list)} metrics in batch")
            return True

        except Exception as e:
            self.logger.error(f"Failed to record metrics batch: {e}")
            return False

    async def create_alert_policy(self, policy: AlertPolicy) -> bool:
        """Create an alert policy."""
        try:
            # Build conditions
            conditions = []
            for condition in policy.conditions:
                # Build filter
                metric_type = self._get_metric_type(
                    condition.display_name.split()[0].lower()
                )
                filter_expr = f'metric.type="{metric_type}"'

                if condition.filter_expression:
                    filter_expr += f" AND {condition.filter_expression}"

                # Build condition
                alert_condition = monitoring_v3.AlertPolicy.Condition(
                    display_name=condition.display_name,
                    condition_monitoring_query_language=monitoring_v3.AlertPolicy.Condition.MonitoringQueryLanguageCondition(
                        query=filter_expr,
                        duration={"seconds": condition.duration_seconds},
                        trigger=monitoring_v3.AlertPolicy.Condition.Trigger(
                            count=1, percent=0.0
                        ),
                        aggregations=[
                            monitoring_v3.Aggregation(
                                alignment_period=condition.aggregation_period,
                                per_series_aligner=monitoring_v3.Aggregation.Aligner[
                                    condition.aggregation_alignment
                                ],
                            )
                        ],
                        trigger_threshold=monitoring_v3.AlertPolicy.Condition.TriggerThreshold(
                            value=condition.trigger_threshold_value,
                            comparison=monitoring_v3.ComparisonType[
                                condition.trigger_threshold_comparison
                            ],
                        ),
                    ),
                )

                conditions.append(alert_condition)

            # Build alert policy
            alert_policy = monitoring_v3.AlertPolicy(
                display_name=policy.display_name,
                documentation=monitoring_v3.AlertPolicy.Documentation(
                    content=policy.description
                ),
                conditions=conditions,
                combiner=monitoring_v3.AlertPolicy.ConditionCombiner.OR,
                enabled=monitoring_v3.AlertPolicy.Enabled(value=policy.enabled),
                notification_channels=policy.notification_channels,
                severity=monitoring_v3.AlertPolicy.Severity[policy.severity.value],
            )

            # Create policy
            self.alert_client.create_alert_policy(
                name=self.project_name, alert_policy=alert_policy
            )

            self.logger.info(f"Created alert policy: {policy.name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to create alert policy {policy.name}: {e}")
            return False

    async def create_notification_channel(
        self,
        channel_type: NotificationChannelType,
        display_name: str,
        description: str,
        labels: Dict[str, str],
    ) -> bool:
        """Create a notification channel."""
        try:
            # Build channel
            channel = monitoring_v3.NotificationChannel(
                type=f"projects/{self.project_id}/notificationChannelDescriptors/{channel_type.value}",
                display_name=display_name,
                description=description,
                labels=labels,
                enabled=monitoring_v3.NotificationChannel.Enabled(value=True),
            )

            # Create channel
            created_channel = self.notification_client.create_notification_channel(
                name=self.project_name, notification_channel=channel
            )

            # Get verification code
            verification_code = created_channel.labels.get("verification_code")

            self.logger.info(f"Created notification channel: {display_name}")
            if verification_code:
                self.logger.info(f"Verification code: {verification_code}")

            return True

        except Exception as e:
            self.logger.error(
                f"Failed to create notification channel {display_name}: {e}"
            )
            return False

    async def get_metric_data(
        self,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        labels: Optional[Dict[str, str]] = None,
        aggregation_period: str = "60s",
    ) -> List[Dict[str, Any]]:
        """Get metric data points."""
        try:
            metric_type = self._get_metric_type(metric_name)

            # Build filter
            filter_expr = f'metric.type="{metric_type}"'

            if labels:
                for key, value in labels.items():
                    filter_expr += f' AND metric.labels.{key}="{value}"'

            # Build interval
            interval = monitoring_v3.TimeInterval(
                start_time={"seconds": int(start_time.timestamp())},
                end_time={"seconds": int(end_time.timestamp())},
            )

            # Build aggregation
            aggregation = monitoring_v3.Aggregation(
                alignment_period=aggregation_period,
                per_series_aligner=monitoring_v3.Aggregation.Aligner.ALIGN_MEAN,
            )

            # List time series
            results = self.metric_client.list_time_series(
                name=self.project_name,
                filter=filter_expr,
                interval=interval,
                aggregation=aggregation,
            )

            # Convert to list of dictionaries
            data_points = []

            for time_series in results:
                for point in time_series.points:
                    # Extract value
                    value = None
                    if point.value.HasField("int64_value"):
                        value = point.value.int64_value
                    elif point.value.HasField("double_value"):
                        value = point.value.double_value
                    elif point.value.HasField("bool_value"):
                        value = point.value.bool_value
                    elif point.value.HasField("string_value"):
                        value = point.value.string_value

                    # Extract timestamp
                    timestamp = datetime.fromtimestamp(point.interval.end_time.seconds)

                    # Extract labels
                    point_labels = dict(time_series.metric.labels)

                    data_point = {
                        "timestamp": timestamp.isoformat(),
                        "value": value,
                        "labels": point_labels,
                    }

                    data_points.append(data_point)

            return data_points

        except Exception as e:
            self.logger.error(f"Failed to get metric data for {metric_name}: {e}")
            return []

    async def get_alert_policies(self) -> List[Dict[str, Any]]:
        """Get all alert policies."""
        try:
            policies = []

            for policy in self.alert_client.list_alert_policies(name=self.project_name):
                policy_data = {
                    "name": policy.name,
                    "display_name": policy.display_name,
                    "description": (
                        policy.documentation.content if policy.documentation else ""
                    ),
                    "enabled": policy.enabled.value,
                    "severity": policy.severity.name,
                    "conditions": [],
                }

                # Add conditions
                for condition in policy.conditions:
                    condition_data = {
                        "display_name": condition.display_name,
                        "filter": (
                            condition.condition_monitoring_query_language.query
                            if condition.condition_monitoring_query_language
                            else ""
                        ),
                        "duration": (
                            condition.condition_monitoring_query_language.duration.seconds
                            if condition.condition_monitoring_query_language
                            else 0
                        ),
                    }
                    policy_data["conditions"].append(condition_data)

                policies.append(policy_data)

            return policies

        except Exception as e:
            self.logger.error(f"Failed to get alert policies: {e}")
            return []

    async def get_notification_channels(self) -> List[Dict[str, Any]]:
        """Get all notification channels."""
        try:
            channels = []

            for channel in self.notification_client.list_notification_channels(
                name=self.project_name
            ):
                channel_data = {
                    "name": channel.name,
                    "display_name": channel.display_name,
                    "description": channel.description,
                    "type": channel.type,
                    "enabled": channel.enabled.value,
                    "labels": dict(channel.labels),
                }

                channels.append(channel_data)

            return channels

        except Exception as e:
            self.logger.error(f"Failed to get notification channels: {e}")
            return []

    async def delete_alert_policy(self, policy_name: str) -> bool:
        """Delete an alert policy."""
        try:
            self.alert_client.delete_alert_policy(name=policy_name)
            self.logger.info(f"Deleted alert policy: {policy_name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to delete alert policy {policy_name}: {e}")
            return False

    async def delete_notification_channel(self, channel_name: str) -> bool:
        """Delete a notification channel."""
        try:
            self.notification_client.delete_notification_channel(name=channel_name)
            self.logger.info(f"Deleted notification channel: {channel_name}")
            return True

        except Exception as e:
            self.logger.error(
                f"Failed to delete notification channel {channel_name}: {e}"
            )
            return False

    async def get_dashboard_url(self) -> str:
        """Get Cloud Monitoring dashboard URL."""
        return f"https://console.cloud.google.com/monitoring?project={self.project_id}"

    def get_default_metrics(self) -> Dict[str, MetricDescriptor]:
        """Get default metric descriptors."""
        return self._default_metrics.copy()

    def add_default_metric(self, descriptor: MetricDescriptor):
        """Add a default metric descriptor."""
        self._default_metrics[descriptor.name] = descriptor


# Global Cloud Monitoring instance
_cloud_monitoring: Optional[CloudMonitoring] = None


def get_cloud_monitoring() -> CloudMonitoring:
    """Get global Cloud Monitoring instance."""
    global _cloud_monitoring
    if _cloud_monitoring is None:
        _cloud_monitoring = CloudMonitoring()
    return _cloud_monitoring


# Convenience functions
async def record_metric(
    metric_name: str,
    value: Union[bool, int, float, str],
    labels: Optional[Dict[str, str]] = None,
) -> bool:
    """Record a metric value."""
    monitoring = get_cloud_monitoring()
    return await monitoring.record_metric(metric_name, value, labels)


async def record_agent_execution(
    agent_type: str,
    status: str,
    workspace_id: str,
    execution_time_ms: Optional[float] = None,
):
    """Record agent execution metrics."""
    monitoring = get_cloud_monitoring()

    # Record execution count
    await monitoring.record_metric(
        "agent_executions",
        1,
        {"agent_type": agent_type, "status": status, "workspace_id": workspace_id},
    )

    # Record execution time if provided
    if execution_time_ms is not None:
        await monitoring.record_metric(
            "agent_execution_time",
            execution_time_ms,
            {"agent_type": agent_type, "workspace_id": workspace_id},
        )


async def record_api_request(
    method: str,
    endpoint: str,
    status_code: int,
    response_time_ms: float,
    workspace_id: Optional[str] = None,
):
    """Record API request metrics."""
    monitoring = get_cloud_monitoring()

    labels = {"method": method, "endpoint": endpoint, "status_code": str(status_code)}

    if workspace_id:
        labels["workspace_id"] = workspace_id

    # Record request count
    await monitoring.record_metric("api_requests", 1, labels)

    # Record response time
    await monitoring.record_metric("api_response_time", response_time_ms, labels)


async def record_error(
    component: str, error_type: str, workspace_id: Optional[str] = None
):
    """Record error metric."""
    monitoring = get_cloud_monitoring()

    labels = {"component": component, "error_type": error_type}

    if workspace_id:
        labels["workspace_id"] = workspace_id

    await monitoring.record_metric("error_rate", 1, labels)


async def create_basic_alert(
    metric_name: str,
    threshold: float,
    comparison: str = "GT",
    duration_minutes: int = 5,
    severity: AlertSeverity = AlertSeverity.WARNING,
) -> bool:
    """Create a basic alert for a metric."""
    monitoring = get_cloud_monitoring()

    condition = AlertCondition(
        display_name=f"{metric_name} Alert",
        filter_expression="",
        duration_seconds=duration_minutes * 60,
        trigger_threshold_value=threshold,
        trigger_threshold_comparison=comparison,
    )

    policy = AlertPolicy(
        name=f"{metric_name}_alert",
        display_name=f"{metric_name} Alert",
        description=f"Alert when {metric_name} {comparison.lower()} {threshold}",
        conditions=[condition],
        severity=severity,
    )

    return await monitoring.create_alert_policy(policy)


# Decorator for automatic metric recording
def monitor_performance(metric_name: str, labels: Optional[Dict[str, str]] = None):
    """Decorator to monitor function performance."""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000

                # Record success metric
                await record_metric(metric_name, duration_ms, labels)

                return result

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000

                # Record error metric
                error_labels = (labels or {}).copy()
                error_labels["error"] = type(e).__name__
                await record_metric(f"{metric_name}_error", duration_ms, error_labels)

                raise

        return wrapper

    return decorator
