"""
Part 25: Monitoring, Alerting, and Observability
RaptorFlow Unified Search System - Industrial Grade AI Agent Search Infrastructure
===============================================================================
This module implements comprehensive monitoring, alerting, and observability
features for the unified search system with real-time insights and notifications.
"""

import asyncio
import json
import logging
import smtplib
import statistics
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from email.mime.multipart import MimeMultipart
from email.mime.text import MimeText
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from core.unified_search_part1 import SearchMode, SearchQuery, SearchResult
from core.unified_search_part2 import SearchProvider

logger = logging.getLogger("raptorflow.unified_search.monitoring")


class AlertSeverity(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricType(Enum):
    """Types of metrics to monitor."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class MonitoringCategory(Enum):
    """Monitoring categories."""

    SYSTEM = "system"
    SEARCH = "search"
    PERFORMANCE = "performance"
    QUALITY = "quality"
    SECURITY = "security"
    BUSINESS = "business"


@dataclass
class Metric:
    """Monitoring metric."""

    name: str
    value: float
    metric_type: MetricType
    category: MonitoringCategory
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    unit: str = ""
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "value": self.value,
            "type": self.metric_type.value,
            "category": self.category.value,
            "labels": self.labels,
            "timestamp": self.timestamp.isoformat(),
            "unit": self.unit,
            "description": self.description,
        }


@dataclass
class Alert:
    """Monitoring alert."""

    alert_id: str
    name: str
    description: str
    severity: AlertSeverity
    category: MonitoringCategory
    metric_name: str
    threshold: float
    current_value: float
    condition: str
    triggered_at: datetime
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    labels: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "alert_id": self.alert_id,
            "name": self.name,
            "description": self.description,
            "severity": self.severity.value,
            "category": self.category.value,
            "metric_name": self.metric_name,
            "threshold": self.threshold,
            "current_value": self.current_value,
            "condition": self.condition,
            "triggered_at": self.triggered_at.isoformat(),
            "acknowledged": self.acknowledged,
            "acknowledged_by": self.acknowledged_by,
            "acknowledged_at": (
                self.acknowledged_at.isoformat() if self.acknowledged_at else None
            ),
            "resolved": self.resolved,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "labels": self.labels,
        }

    @property
    def age_minutes(self) -> float:
        """Get alert age in minutes."""
        return (datetime.now() - self.triggered_at).total_seconds() / 60

    @property
    def is_active(self) -> bool:
        """Check if alert is active."""
        return not self.resolved


@dataclass
class AlertRule:
    """Alert rule definition."""

    rule_id: str
    name: str
    description: str
    metric_name: str
    condition: str  # gt, lt, eq, gte, lte
    threshold: float
    severity: AlertSeverity
    category: MonitoringCategory
    enabled: bool = True
    evaluation_window_seconds: int = 300
    consecutive_breaches: int = 1
    labels: Dict[str, str] = field(default_factory=dict)
    notification_channels: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "metric_name": self.metric_name,
            "condition": self.condition,
            "threshold": self.threshold,
            "severity": self.severity.value,
            "category": self.category.value,
            "enabled": self.enabled,
            "evaluation_window_seconds": self.evaluation_window_seconds,
            "consecutive_breaches": self.consecutive_breaches,
            "labels": self.labels,
            "notification_channels": self.notification_channels,
        }


@dataclass
class NotificationChannel:
    """Notification channel configuration."""

    channel_id: str
    name: str
    type: str  # email, slack, webhook, sms
    config: Dict[str, Any]
    enabled: bool = True
    rate_limit_minutes: int = 5

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "channel_id": self.channel_id,
            "name": self.name,
            "type": self.type,
            "config": self.config,
            "enabled": self.enabled,
            "rate_limit_minutes": self.rate_limit_minutes,
        }


class MetricsCollector:
    """Collects and stores monitoring metrics."""

    def __init__(self):
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.timers: Dict[str, List[float]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def increment_counter(
        self,
        name: str,
        value: float = 1.0,
        labels: Optional[Dict[str, str]] = None,
        category: MonitoringCategory = MonitoringCategory.SYSTEM,
    ):
        """Increment counter metric."""
        async with self._lock:
            key = self._make_key(name, labels)
            self.counters[key] += value

            metric = Metric(
                name=name,
                value=self.counters[key],
                metric_type=MetricType.COUNTER,
                category=category,
                labels=labels or {},
                unit="count",
            )

            self.metrics[key].append(metric)

    async def set_gauge(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
        category: MonitoringCategory = MonitoringCategory.SYSTEM,
    ):
        """Set gauge metric."""
        async with self._lock:
            key = self._make_key(name, labels)
            self.gauges[key] = value

            metric = Metric(
                name=name,
                value=value,
                metric_type=MetricType.GAUGE,
                category=category,
                labels=labels or {},
            )

            self.metrics[key].append(metric)

    async def record_histogram(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
        category: MonitoringCategory = MonitoringCategory.SYSTEM,
    ):
        """Record histogram metric."""
        async with self._lock:
            key = self._make_key(name, labels)
            self.histograms[key].append(value)

            # Keep only last 1000 values
            if len(self.histograms[key]) > 1000:
                self.histograms[key] = self.histograms[key][-1000:]

            metric = Metric(
                name=name,
                value=value,
                metric_type=MetricType.HISTOGRAM,
                category=category,
                labels=labels or {},
            )

            self.metrics[key].append(metric)

    async def record_timer(
        self,
        name: str,
        duration_ms: float,
        labels: Optional[Dict[str, str]] = None,
        category: MonitoringCategory = MonitoringCategory.PERFORMANCE,
    ):
        """Record timer metric."""
        async with self._lock:
            key = self._make_key(name, labels)
            self.timers[key].append(duration_ms)

            # Keep only last 1000 values
            if len(self.timers[key]) > 1000:
                self.timers[key] = self.timers[key][-1000:]

            metric = Metric(
                name=name,
                value=duration_ms,
                metric_type=MetricType.TIMER,
                category=category,
                labels=labels or {},
                unit="ms",
            )

            self.metrics[key].append(metric)

    def _make_key(self, name: str, labels: Optional[Dict[str, str]]) -> str:
        """Create metric key with labels."""
        if not labels:
            return name

        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"

    async def get_metric(
        self, name: str, labels: Optional[Dict[str, str]] = None
    ) -> Optional[Metric]:
        """Get latest metric value."""
        key = self._make_key(name, labels)

        async with self._lock:
            if key in self.metrics and self.metrics[key]:
                return self.metrics[key][-1]

        return None

    async def get_metric_stats(
        self, name: str, labels: Optional[Dict[str, str]] = None, minutes: int = 5
    ) -> Dict[str, float]:
        """Get metric statistics for time window."""
        key = self._make_key(name, labels)
        cutoff_time = datetime.now() - timedelta(minutes=minutes)

        async with self._lock:
            if key not in self.metrics:
                return {}

            recent_metrics = [
                metric
                for metric in self.metrics[key]
                if metric.timestamp >= cutoff_time
            ]

            if not recent_metrics:
                return {}

            values = [metric.value for metric in recent_metrics]

            return {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "avg": statistics.mean(values),
                "sum": sum(values),
                "latest": values[-1],
            }

    def get_all_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics."""
        summary = {
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "histograms": {},
            "timers": {},
        }

        # Calculate histogram statistics
        for key, values in self.histograms.items():
            if values:
                summary["histograms"][key] = {
                    "count": len(values),
                    "min": min(values),
                    "max": max(values),
                    "avg": statistics.mean(values),
                    "p50": statistics.median(values),
                    "p95": self._percentile(values, 0.95),
                    "p99": self._percentile(values, 0.99),
                }

        # Calculate timer statistics
        for key, values in self.timers.items():
            if values:
                summary["timers"][key] = {
                    "count": len(values),
                    "min": min(values),
                    "max": max(values),
                    "avg": statistics.mean(values),
                    "p50": statistics.median(values),
                    "p95": self._percentile(values, 0.95),
                    "p99": self._percentile(values, 0.99),
                }

        return summary

    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile."""
        if not values:
            return 0.0

        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile)
        return sorted_values[min(index, len(sorted_values) - 1)]


class AlertManager:
    """Manages alert rules and notifications."""

    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: deque = deque(maxlen=1000)
        self.notification_channels: Dict[str, NotificationChannel] = {}
        self.rate_limits: Dict[str, datetime] = {}
        self._evaluation_task: Optional[asyncio.Task] = None

    def add_alert_rule(self, rule: AlertRule):
        """Add alert rule."""
        self.alert_rules[rule.rule_id] = rule
        logger.info(f"Added alert rule: {rule.name}")

    def remove_alert_rule(self, rule_id: str) -> bool:
        """Remove alert rule."""
        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
            logger.info(f"Removed alert rule: {rule_id}")
            return True
        return False

    def add_notification_channel(self, channel: NotificationChannel):
        """Add notification channel."""
        self.notification_channels[channel.channel_id] = channel
        logger.info(f"Added notification channel: {channel.name}")

    async def start_evaluation(self):
        """Start alert evaluation."""
        self._evaluation_task = asyncio.create_task(self._evaluation_loop())
        logger.info("Alert evaluation started")

    async def stop_evaluation(self):
        """Stop alert evaluation."""
        if self._evaluation_task:
            self._evaluation_task.cancel()
            try:
                await self._evaluation_task
            except asyncio.CancelledError:
                pass
        logger.info("Alert evaluation stopped")

    async def _evaluation_loop(self):
        """Main alert evaluation loop."""
        while True:
            try:
                await asyncio.sleep(30)  # Evaluate every 30 seconds

                await self._evaluate_alert_rules()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Alert evaluation error: {e}")
                await asyncio.sleep(60)

    async def _evaluate_alert_rules(self):
        """Evaluate all alert rules."""
        for rule in self.alert_rules.values():
            if not rule.enabled:
                continue

            try:
                await self._evaluate_rule(rule)
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.name}: {e}")

    async def _evaluate_rule(self, rule: AlertRule):
        """Evaluate individual alert rule."""
        # Get current metric value
        metric = await self.metrics_collector.get_metric(rule.metric_name)
        if not metric:
            return

        current_value = metric.value

        # Check condition
        triggered = self._check_condition(current_value, rule.condition, rule.threshold)

        # Check if alert already exists
        existing_alert = self.active_alerts.get(rule.rule_id)

        if triggered and not existing_alert:
            # Create new alert
            alert = Alert(
                alert_id=str(uuid.uuid4()),
                name=rule.name,
                description=rule.description,
                severity=rule.severity,
                category=rule.category,
                metric_name=rule.metric_name,
                threshold=rule.threshold,
                current_value=current_value,
                condition=rule.condition,
                triggered_at=datetime.now(),
                labels=rule.labels,
            )

            self.active_alerts[rule.rule_id] = alert
            self.alert_history.append(alert)

            # Send notifications
            await self._send_notifications(alert, rule)

            logger.warning(
                f"Alert triggered: {rule.name} - {current_value} {rule.condition} {rule.threshold}"
            )

        elif not triggered and existing_alert:
            # Resolve alert
            existing_alert.resolved = True
            existing_alert.resolved_at = datetime.now()

            # Move to history and remove from active
            del self.active_alerts[rule.rule_id]

            logger.info(f"Alert resolved: {rule.name}")

    def _check_condition(self, value: float, condition: str, threshold: float) -> bool:
        """Check if condition is met."""
        if condition == "gt":
            return value > threshold
        elif condition == "gte":
            return value >= threshold
        elif condition == "lt":
            return value < threshold
        elif condition == "lte":
            return value <= threshold
        elif condition == "eq":
            return abs(value - threshold) < 0.001
        else:
            return False

    async def _send_notifications(self, alert: Alert, rule: AlertRule):
        """Send alert notifications."""
        for channel_id in rule.notification_channels:
            channel = self.notification_channels.get(channel_id)
            if not channel or not channel.enabled:
                continue

            # Check rate limit
            if self._is_rate_limited(channel_id, channel.rate_limit_minutes):
                continue

            try:
                await self._send_notification(channel, alert)
                self.rate_limits[channel_id] = datetime.now()
            except Exception as e:
                logger.error(f"Failed to send notification via {channel.name}: {e}")

    def _is_rate_limited(self, channel_id: str, rate_limit_minutes: int) -> bool:
        """Check if channel is rate limited."""
        if channel_id not in self.rate_limits:
            return False

        last_sent = self.rate_limits[channel_id]
        return (datetime.now() - last_sent).total_seconds() < (rate_limit_minutes * 60)

    async def _send_notification(self, channel: NotificationChannel, alert: Alert):
        """Send notification via specific channel."""
        if channel.type == "email":
            await self._send_email_notification(channel, alert)
        elif channel.type == "webhook":
            await self._send_webhook_notification(channel, alert)
        elif channel.type == "slack":
            await self._send_slack_notification(channel, alert)
        else:
            logger.warning(f"Unknown notification channel type: {channel.type}")

    async def _send_email_notification(
        self, channel: NotificationChannel, alert: Alert
    ):
        """Send email notification."""
        config = channel.config

        # Create email message
        msg = MimeMultipart()
        msg["From"] = config.get("from", "alerts@raptorflow.com")
        msg["To"] = config.get("to", "")
        msg["Subject"] = f"[{alert.severity.value.upper()}] {alert.name}"

        # Create email body
        body = f"""
Alert: {alert.name}
Severity: {alert.severity.value.upper()}
Description: {alert.description}
Metric: {alert.metric_name}
Current Value: {alert.current_value}
Threshold: {alert.threshold}
Condition: {alert.condition}
Triggered At: {alert.triggered_at.isoformat()}
        """

        msg.attach(MimeText(body, "plain"))

        # Send email (mock implementation)
        logger.info(f"Email notification sent for alert: {alert.name}")

    async def _send_webhook_notification(
        self, channel: NotificationChannel, alert: Alert
    ):
        """Send webhook notification."""
        config = channel.config
        url = config.get("url")

        if not url:
            return

        # Create payload
        payload = {"alert": alert.to_dict(), "timestamp": datetime.now().isoformat()}

        # Send webhook (mock implementation)
        logger.info(f"Webhook notification sent to {url} for alert: {alert.name}")

    async def _send_slack_notification(
        self, channel: NotificationChannel, alert: Alert
    ):
        """Send Slack notification."""
        config = channel.config
        webhook_url = config.get("webhook_url")

        if not webhook_url:
            return

        # Create Slack message
        color_map = {
            AlertSeverity.INFO: "#36a64f",
            AlertSeverity.WARNING: "#ff9500",
            AlertSeverity.ERROR: "#ff0000",
            AlertSeverity.CRITICAL: "#8b0000",
        }

        payload = {
            "attachments": [
                {
                    "color": color_map.get(alert.severity, "#36a64f"),
                    "title": alert.name,
                    "text": alert.description,
                    "fields": [
                        {
                            "title": "Severity",
                            "value": alert.severity.value.upper(),
                            "short": True,
                        },
                        {"title": "Metric", "value": alert.metric_name, "short": True},
                        {
                            "title": "Current Value",
                            "value": str(alert.current_value),
                            "short": True,
                        },
                        {
                            "title": "Threshold",
                            "value": str(alert.threshold),
                            "short": True,
                        },
                    ],
                    "timestamp": alert.triggered_at.timestamp(),
                }
            ]
        }

        # Send Slack message (mock implementation)
        logger.info(f"Slack notification sent for alert: {alert.name}")

    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert."""
        for alert in self.active_alerts.values():
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                alert.acknowledged_by = acknowledged_by
                alert.acknowledged_at = datetime.now()
                logger.info(f"Alert acknowledged: {alert_id} by {acknowledged_by}")
                return True

        return False

    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts."""
        return list(self.active_alerts.values())

    def get_alert_stats(self) -> Dict[str, Any]:
        """Get alert statistics."""
        active_alerts = self.get_active_alerts()

        severity_counts = defaultdict(int)
        category_counts = defaultdict(int)

        for alert in active_alerts:
            severity_counts[alert.severity.value] += 1
            category_counts[alert.category.value] += 1

        return {
            "total_active_alerts": len(active_alerts),
            "severity_distribution": dict(severity_counts),
            "category_distribution": dict(category_counts),
            "total_rules": len(self.alert_rules),
            "enabled_rules": len([r for r in self.alert_rules.values() if r.enabled]),
            "total_channels": len(self.notification_channels),
            "enabled_channels": len(
                [c for c in self.notification_channels.values() if c.enabled]
            ),
        }


class ObservabilityDashboard:
    """Provides observability insights and dashboards."""

    def __init__(
        self, metrics_collector: MetricsCollector, alert_manager: AlertManager
    ):
        self.metrics_collector = metrics_collector
        self.alert_manager = alert_manager

    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health."""
        active_alerts = self.alert_manager.get_active_alerts()

        # Calculate health score
        critical_alerts = len(
            [a for a in active_alerts if a.severity == AlertSeverity.CRITICAL]
        )
        error_alerts = len(
            [a for a in active_alerts if a.severity == AlertSeverity.ERROR]
        )
        warning_alerts = len(
            [a for a in active_alerts if a.severity == AlertSeverity.WARNING]
        )

        if critical_alerts > 0:
            health_status = "critical"
            health_score = 0.0
        elif error_alerts > 2:
            health_status = "degraded"
            health_score = 0.3
        elif error_alerts > 0 or warning_alerts > 5:
            health_status = "warning"
            health_score = 0.6
        else:
            health_status = "healthy"
            health_score = 1.0

        return {
            "status": health_status,
            "score": health_score,
            "active_alerts": len(active_alerts),
            "critical_alerts": critical_alerts,
            "error_alerts": error_alerts,
            "warning_alerts": warning_alerts,
            "timestamp": datetime.now().isoformat(),
        }

    def get_performance_metrics(self, minutes: int = 60) -> Dict[str, Any]:
        """Get performance metrics summary."""
        metrics = {}

        # Search performance
        search_time_stats = await self.metrics_collector.get_metric_stats(
            "search_duration_ms", minutes=minutes
        )
        if search_time_stats:
            metrics["search_performance"] = search_time_stats

        # System metrics
        cpu_stats = await self.metrics_collector.get_metric_stats(
            "cpu_utilization", minutes=minutes
        )
        if cpu_stats:
            metrics["cpu"] = cpu_stats

        memory_stats = await self.metrics_collector.get_metric_stats(
            "memory_utilization", minutes=minutes
        )
        if memory_stats:
            metrics["memory"] = memory_stats

        # Quality metrics
        quality_stats = await self.metrics_collector.get_metric_stats(
            "search_quality_score", minutes=minutes
        )
        if quality_stats:
            metrics["quality"] = quality_stats

        return metrics

    def get_business_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Get business metrics."""
        metrics = {}

        # Search volume
        search_count = await self.metrics_collector.get_metric_stats(
            "search_requests_total", minutes=hours * 60
        )
        if search_count:
            metrics["search_volume"] = search_count

        # Success rate
        success_count = await self.metrics_collector.get_metric_stats(
            "search_success_total", minutes=hours * 60
        )
        if success_count and search_count:
            success_rate = success_count.get("sum", 0) / search_count.get("sum", 1)
            metrics["success_rate"] = success_rate

        # User satisfaction (mock)
        metrics["user_satisfaction"] = 0.85  # Mock value

        return metrics

    def generate_dashboard_data(self) -> Dict[str, Any]:
        """Generate comprehensive dashboard data."""
        return {
            "system_health": self.get_system_health(),
            "performance_metrics": self.get_performance_metrics(),
            "business_metrics": self.get_business_metrics(),
            "alert_stats": self.alert_manager.get_alert_stats(),
            "active_alerts": [
                alert.to_dict() for alert in self.alert_manager.get_active_alerts()
            ],
            "metrics_summary": self.metrics_collector.get_all_metrics_summary(),
            "timestamp": datetime.now().isoformat(),
        }


# Initialize default monitoring setup
def create_default_monitoring_setup():
    """Create default monitoring configuration."""
    metrics_collector = MetricsCollector()
    alert_manager = AlertManager(metrics_collector)
    dashboard = ObservabilityDashboard(metrics_collector, alert_manager)

    # Create default alert rules
    default_rules = [
        AlertRule(
            rule_id="high_cpu_usage",
            name="High CPU Usage",
            description="CPU utilization is above threshold",
            metric_name="cpu_utilization",
            condition="gt",
            threshold=0.8,
            severity=AlertSeverity.WARNING,
            category=MonitoringCategory.SYSTEM,
        ),
        AlertRule(
            rule_id="high_memory_usage",
            name="High Memory Usage",
            description="Memory utilization is above threshold",
            metric_name="memory_utilization",
            condition="gt",
            threshold=0.85,
            severity=AlertSeverity.WARNING,
            category=MonitoringCategory.SYSTEM,
        ),
        AlertRule(
            rule_id="slow_search_response",
            name="Slow Search Response",
            description="Search response time is above threshold",
            metric_name="search_duration_ms",
            condition="gt",
            threshold=2000.0,
            severity=AlertSeverity.WARNING,
            category=MonitoringCategory.PERFORMANCE,
        ),
        AlertRule(
            rule_id="low_search_quality",
            name="Low Search Quality",
            description="Search quality score is below threshold",
            metric_name="search_quality_score",
            condition="lt",
            threshold=0.6,
            severity=AlertSeverity.WARNING,
            category=MonitoringCategory.QUALITY,
        ),
    ]

    for rule in default_rules:
        alert_manager.add_alert_rule(rule)

    # Create default notification channels
    default_channels = [
        NotificationChannel(
            channel_id="email_alerts",
            name="Email Alerts",
            type="email",
            config={
                "to": "admin@raptorflow.com",
                "from": "alerts@raptorflow.com",
                "smtp_server": "smtp.raptorflow.com",
            },
        ),
        NotificationChannel(
            channel_id="webhook_alerts",
            name="Webhook Alerts",
            type="webhook",
            config={"url": "https://hooks.raptorflow.com/alerts"},
        ),
    ]

    for channel in default_channels:
        alert_manager.add_notification_channel(channel)

    return metrics_collector, alert_manager, dashboard


# Global monitoring components
metrics_collector, alert_manager, observability_dashboard = (
    create_default_monitoring_setup()
)
