"""
Alerting system for Raptorflow agent system.
Handles alert generation, routing, and notification.
"""

import asyncio
import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from backend.agents.exceptions import DatabaseError, ValidationError
from .health_checks import HealthStatus, get_health_checker
from .metrics import MetricCategory, get_metrics_collector

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert status levels."""

    ACTIVE = "active"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    ACKNOWLEDGED = "acknowledged"


class AlertType(Enum):
    """Types of alerts."""

    METRIC_THRESHOLD = "metric_threshold"
    HEALTH_CHECK = "health_check"
    SYSTEM_ERROR = "system_error"
    BUSINESS_RULE = "business_rule"
    CUSTOM = "custom"


@dataclass
class AlertRule:
    """Alert rule definition."""

    name: str
    alert_type: AlertType
    description: str
    severity: AlertSeverity
    enabled: bool = True
    condition: str = ""
    threshold: float = 0.0
    metric_name: str = ""
    health_check_name: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    cooldown: int = 300  # seconds
    max_alerts_per_hour: int = 10
    notification_channels: List[str] = field(default_factory=list)
    escalation_policy: str = "immediate"
    auto_resolve: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Alert:
    """Alert instance."""

    id: str
    rule_name: str
    alert_type: AlertType
    severity: AlertSeverity
    status: AlertStatus
    title: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolved_by: Optional[str] = None
    notification_sent: bool = False
    escalation_sent: bool = False


@dataclass
class NotificationChannel:
    """Notification channel definition."""

    name: str
    type: str  # email, slack, webhook, sms
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)
    rate_limit: int = 100  # per hour
    retry_attempts: int = 3
    retry_delay: int = 60  # seconds


class AlertManager:
    """Manages alert rules and notifications."""

    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self.alerts: Dict[str, Alert] = {}
        self.channels: Dict[str, NotificationChannel] = {}
        self.alert_history: List[Alert] = []
        self.notification_queue: asyncio.Queue = asyncio.Queue()
        self.notification_task = None
        self.enabled = True
        self.running = False

        # Alert statistics
        self.alert_counts = defaultdict(int)
        self.last_alert_times = defaultdict(datetime)
        self.hourly_alert_counts = defaultdict(int)

        # Initialize default rules and channels
        self._initialize_default_rules()
        self._initialize_default_channels()

    def _initialize_default_rules(self):
        """Initialize default alert rules."""
        default_rules = [
            # Metric threshold rules
            AlertRule(
                name="high_cpu_usage",
                alert_type=AlertType.METRIC_THRESHOLD,
                description="Alert when CPU usage is high",
                severity=AlertSeverity.HIGH,
                metric_name="system_cpu_usage",
                threshold=80.0,
                condition=">=",
                notification_channels=["email", "slack"],
                cooldown=300,
            ),
            AlertRule(
                name="high_memory_usage",
                alert_type=AlertType.METRIC_THRESHOLD,
                description="Alert when memory usage is high",
                severity=AlertSeverity.HIGH,
                metric_name="system_memory_usage",
                threshold=85.0,
                condition=">=",
                notification_channels=["email", "slack"],
                cooldown=300,
            ),
            AlertRule(
                name="high_error_rate",
                alert_type=AlertType.METRIC_THRESHOLD,
                description="Alert when error rate is high",
                severity=AlertSeverity.CRITICAL,
                metric_name="error_rate",
                threshold=5.0,
                condition=">=",
                notification_channels=["email", "slack", "webhook"],
                cooldown=180,
            ),
            # Health check rules
            AlertRule(
                name="critical_health_check",
                alert_type=AlertType.HEALTH_CHECK,
                description="Alert when health check is critical",
                severity=AlertSeverity.CRITICAL,
                health_check_name="database_connection",
                notification_channels=["email", "slack", "webhook"],
                cooldown=60,
            ),
            AlertRule(
                name="warning_health_check",
                alert_type=AlertType.HEALTH_CHECK,
                description="Alert when health check is warning",
                severity=AlertSeverity.MEDIUM,
                health_check_name="agent_performance",
                notification_channels=["email"],
                cooldown=300,
            ),
            # System error rules
            AlertRule(
                name="database_error",
                alert_type=AlertType.SYSTEM_ERROR,
                description="Alert on database errors",
                severity=AlertSeverity.HIGH,
                notification_channels=["email", "slack"],
                cooldown=180,
            ),
            AlertRule(
                name="agent_execution_error",
                alert_type=AlertType.SYSTEM_ERROR,
                description="Alert on agent execution errors",
                severity=AlertSeverity.MEDIUM,
                notification_channels=["email"],
                cooldown=300,
            ),
        ]

        for rule in default_rules:
            self.register_rule(rule)

    def _initialize_default_channels(self):
        """Initialize default notification channels."""
        default_channels = [
            NotificationChannel(
                name="email",
                type="email",
                config={
                    "smtp_server": "smtp.example.com",
                    "smtp_port": 587,
                    "username": "alerts@example.com",
                    "password": "password",
                    "from_address": "alerts@example.com",
                    "to_addresses": ["admin@example.com"],
                },
            ),
            NotificationChannel(
                name="slack",
                type="slack",
                config={
                    "webhook_url": "https://hooks.slack.com/services/...",
                    "channel": "#alerts",
                    "username": "Raptorflow Alerts",
                },
            ),
            NotificationChannel(
                name="webhook",
                type="webhook",
                config={
                    "url": "https://api.example.com/webhooks/alerts",
                    "method": "POST",
                    "headers": {"Content-Type": "application/json"},
                },
            ),
        ]

        for channel in default_channels:
            self.register_channel(channel)

    def register_rule(self, rule: AlertRule):
        """Register an alert rule."""
        self.rules[rule.name] = rule
        logger.info(f"Registered alert rule: {rule.name}")

    def unregister_rule(self, name: str):
        """Unregister an alert rule."""
        if name in self.rules:
            del self.rules[name]
            logger.info(f"Unregistered alert rule: {name}")

    def enable_rule(self, name: str):
        """Enable an alert rule."""
        if name in self.rules:
            self.rules[name].enabled = True
            logger.info(f"Enabled alert rule: {name}")

    def disable_rule(self, name: str):
        """Disable an alert rule."""
        if name in self.rules:
            self.rules[name].enabled = False
            logger.info(f"Disabled alert rule: {name}")

    def register_channel(self, channel: NotificationChannel):
        """Register a notification channel."""
        self.channels[channel.name] = channel
        logger.info(f"Registered notification channel: {channel.name}")

    def unregister_channel(self, name: str):
        """Unregister a notification channel."""
        if name in self.channels:
            del self.channels[name]
            logger.info(f"Unregistered notification channel: {name}")

    def enable_channel(self, name: str):
        """Enable a notification channel."""
        if name in self.channels:
            self.channels[name].enabled = True
            logger.info(f"Enabled notification channel: {name}")

    def disable_channel(self, name: str):
        """Disable a notification channel."""
        if name in self.channels:
            self.channels[name].enabled = False
            logger.info(f"Disabled notification channel: {name}")

    async def check_rules(self):
        """Check all alert rules and generate alerts."""
        if not self.enabled:
            return

        for rule_name, rule in self.rules.items():
            if not rule.enabled:
                continue

            # Check cooldown
            if self._is_in_cooldown(rule):
                continue

            # Check hourly limit
            if self._is_hourly_limit_exceeded(rule):
                continue

            try:
                alert = await self._evaluate_rule(rule)
                if alert:
                    await self._create_alert(alert)
            except Exception as e:
                logger.error(f"Error evaluating rule {rule_name}: {e}")

    async def _evaluate_rule(self, rule: AlertRule) -> Optional[Alert]:
        """Evaluate an alert rule."""
        if rule.alert_type == AlertType.METRIC_THRESHOLD:
            return await self._evaluate_metric_rule(rule)
        elif rule.alert_type == AlertType.HEALTH_CHECK:
            return await self._evaluate_health_rule(rule)
        elif rule.alert_type == AlertType.SYSTEM_ERROR:
            return await self._evaluate_error_rule(rule)
        elif rule.alert_type == AlertType.CUSTOM:
            return await self._evaluate_custom_rule(rule)

        return None

    async def _evaluate_metric_rule(self, rule: AlertRule) -> Optional[Alert]:
        """Evaluate a metric threshold rule."""
        try:
            metrics_collector = get_metrics_collector()
            metric_value = metrics_collector.get_metric_value(rule.metric_name)

            if metric_value is None:
                return None

            # Evaluate condition
            triggered = False
            if rule.condition == ">=":
                triggered = metric_value >= rule.threshold
            elif rule.condition == ">":
                triggered = metric_value > rule.threshold
            elif rule.condition == "<=":
                triggered = metric_value <= rule.threshold
            elif rule.condition == "<":
                triggered = metric_value < rule.threshold
            elif rule.condition == "==":
                triggered = metric_value == rule.threshold
            elif rule.condition == "!=":
                triggered = metric_value != rule.threshold

            if triggered:
                return Alert(
                    id=f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(rule.name) % 10000}",
                    rule_name=rule.name,
                    alert_type=rule.alert_type,
                    severity=rule.severity,
                    status=AlertStatus.ACTIVE,
                    title=f"Metric Threshold Alert: {rule.name}",
                    message=f"Metric {rule.metric_name} is {metric_value} (threshold: {rule.threshold})",
                    details={
                        "metric_name": rule.metric_name,
                        "metric_value": metric_value,
                        "threshold": rule.threshold,
                        "condition": rule.condition,
                    },
                    tags=rule.tags,
                )

        except Exception as e:
            logger.error(f"Error evaluating metric rule {rule.name}: {e}")

        return None

    async def _evaluate_health_rule(self, rule: AlertRule) -> Optional[Alert]:
        """Evaluate a health check rule."""
        try:
            health_checker = get_health_checker()
            health_result = health_checker.get_check_result(rule.health_check_name)

            if not health_result:
                return None

            # Trigger alert based on health status
            triggered = health_result.status in [
                HealthStatus.CRITICAL,
                HealthStatus.WARNING,
            ]

            if triggered:
                severity = (
                    AlertSeverity.CRITICAL
                    if health_result.status == HealthStatus.CRITICAL
                    else AlertSeverity.HIGH
                )

                return Alert(
                    id=f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(rule.name) % 10000}",
                    rule_name=rule.name,
                    alert_type=rule.alert_type,
                    severity=severity,
                    status=AlertStatus.ACTIVE,
                    title=f"Health Check Alert: {rule.name}",
                    message=f"Health check {rule.health_check_name} is {health_result.status.value}",
                    details={
                        "health_check_name": rule.health_check_name,
                        "health_status": health_result.status.value,
                        "health_message": health_result.message,
                        "health_duration": health_result.duration,
                    },
                    tags=rule.tags,
                )

        except Exception as e:
            logger.error(f"Error evaluating health rule {rule.name}: {e}")

        return None

    async def _evaluate_error_rule(self, rule: AlertRule) -> Optional[Alert]:
        """Evaluate a system error rule."""
        try:
            metrics_collector = get_metrics_collector()
            error_count = metrics_collector.get_metric_value("error_total")

            if error_count is None:
                return None

            # Check if error count increased significantly
            # This is a simplified implementation
            if error_count > 0:
                return Alert(
                    id=f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(rule.name) % 10000}",
                    rule_name=rule.name,
                    alert_type=rule.alert_type,
                    severity=rule.severity,
                    status=AlertStatus.ACTIVE,
                    title=f"System Error Alert: {rule.name}",
                    message=f"System errors detected: {error_count} total errors",
                    details={
                        "error_count": error_count,
                        "error_rate": metrics_collector.get_metric_value("error_rate"),
                    },
                    tags=rule.tags,
                )

        except Exception as e:
            logger.error(f"Error evaluating error rule {rule.name}: {e}")

        return None

    async def _evaluate_custom_rule(self, rule: AlertRule) -> Optional[Alert]:
        """Evaluate a custom alert rule."""
        # This would integrate with custom rule evaluation logic
        # For now, return None as placeholder
        return None

    def _is_in_cooldown(self, rule: AlertRule) -> bool:
        """Check if rule is in cooldown period."""
        last_time = self.last_alert_times.get(rule.name)
        if last_time:
            return datetime.now() - last_time < timedelta(seconds=rule.cooldown)
        return False

    def _is_hourly_limit_exceeded(self, rule: AlertRule) -> bool:
        """Check if hourly alert limit is exceeded."""
        current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
        count = self.hourly_alert_counts.get((rule.name, current_hour), 0)
        return count >= rule.max_alerts_per_hour

    async def _create_alert(self, alert: Alert):
        """Create and process an alert."""
        # Update statistics
        self.alert_counts[alert.rule_name] += 1
        self.last_alert_times[alert.rule_name] = datetime.now()

        # Update hourly count
        current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
        self.hourly_alert_counts[(alert.rule_name, current_hour)] += 1

        # Store alert
        self.alerts[alert.id] = alert
        self.alert_history.append(alert)

        # Limit history size
        if len(self.alert_history) > 10000:
            self.alert_history = self.alert_history[-10000:]

        logger.info(f"Created alert: {alert.title}")

        # Queue for notification
        await self.notification_queue.put(alert)

    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert."""
        if alert_id not in self.alerts:
            return False

        alert = self.alerts[alert_id]
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_at = datetime.now()
        alert.acknowledged_by = acknowledged_by
        alert.updated_at = datetime.now()

        logger.info(f"Acknowledged alert {alert_id} by {acknowledged_by}")
        return True

    async def resolve_alert(self, alert_id: str, resolved_by: str) -> bool:
        """Resolve an alert."""
        if alert_id not in self.alerts:
            return False

        alert = self.alerts[alert_id]
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.now()
        alert.resolved_by = resolved_by
        alert.updated_at = datetime.now()

        logger.info(f"Resolved alert {alert_id} by {resolved_by}")
        return True

    async def suppress_alert(self, alert_id: str) -> bool:
        """Suppress an alert."""
        if alert_id not in self.alerts:
            return False

        alert = self.alerts[alert_id]
        alert.status = AlertStatus.SUPPRESSED
        alert.updated_at = datetime.now()

        logger.info(f"Suppressed alert {alert_id}")
        return True

    def get_alert(self, alert_id: str) -> Optional[Alert]:
        """Get an alert by ID."""
        return self.alerts.get(alert_id)

    def get_alerts(
        self,
        status: Optional[AlertStatus] = None,
        severity: Optional[AlertSeverity] = None,
        limit: int = 100,
    ) -> List[Alert]:
        """Get alerts with optional filtering."""
        alerts = list(self.alerts.values())

        # Filter by status
        if status:
            alerts = [a for a in alerts if a.status == status]

        # Filter by severity
        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        # Sort by creation time (newest first)
        alerts.sort(key=lambda a: a.created_at, reverse=True)

        # Limit results
        return alerts[:limit]

    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics."""
        stats = {
            "total_alerts": len(self.alerts),
            "active_alerts": len(
                [a for a in self.alerts.values() if a.status == AlertStatus.ACTIVE]
            ),
            "resolved_alerts": len(
                [a for a in self.alerts.values() if a.status == AlertStatus.RESOLVED]
            ),
            "acknowledged_alerts": len(
                [
                    a
                    for a in self.alerts.values()
                    if a.status == AlertStatus.ACKNOWLEDGED
                ]
            ),
            "suppressed_alerts": len(
                [a for a in self.alerts.values() if a.status == AlertStatus.SUPPRESSED]
            ),
            "alerts_by_severity": {},
            "alerts_by_type": {},
            "alerts_by_rule": {},
            "recent_alerts": len(
                [
                    a
                    for a in self.alert_history
                    if a.created_at > datetime.now() - timedelta(hours=24)
                ]
            ),
        }

        # Group by severity
        for severity in AlertSeverity:
            stats["alerts_by_severity"][severity.value] = len(
                [a for a in self.alerts.values() if a.severity == severity]
            )

        # Group by type
        for alert_type in AlertType:
            stats["alerts_by_type"][alert_type.value] = len(
                [a for a in self.alerts.values() if a.alert_type == alert_type]
            )

        # Group by rule
        for rule_name in self.rules:
            stats["alerts_by_rule"][rule_name] = len(
                [a for a in self.alerts.values() if a.rule_name == rule_name]
            )

        return stats

    async def start_notification_service(self):
        """Start the notification service."""
        if self.running:
            logger.warning("Notification service is already running")
            return

        self.running = True
        self.notification_task = asyncio.create_task(self._notification_loop())
        logger.info("Started notification service")

    async def stop_notification_service(self):
        """Stop the notification service."""
        if not self.running:
            logger.warning("Notification service is not running")
            return

        self.running = False
        if self.notification_task:
            self.notification_task.cancel()
            try:
                await self.notification_task
            except asyncio.CancelledError:
                pass

        logger.info("Stopped notification service")

    async def _notification_loop(self):
        """Notification processing loop."""
        while self.running:
            try:
                # Get alert from queue
                alert = await asyncio.wait_for(
                    self.notification_queue.get(), timeout=1.0
                )

                # Send notifications
                await self._send_notifications(alert)

            except asyncio.TimeoutError:
                # No alerts in queue, continue
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Notification loop error: {e}")
                await asyncio.sleep(1)

    async def _send_notifications(self, alert: Alert):
        """Send notifications for an alert."""
        rule = self.rules.get(alert.rule_name)
        if not rule:
            return

        for channel_name in rule.notification_channels:
            channel = self.channels.get(channel_name)
            if not channel or not channel.enabled:
                continue

            try:
                await self._send_notification(channel, alert)
                alert.notification_sent = True
            except Exception as e:
                logger.error(f"Failed to send notification via {channel_name}: {e}")

    async def _send_notification(self, channel: NotificationChannel, alert: Alert):
        """Send notification via a channel."""
        if channel.type == "email":
            await self._send_email_notification(channel, alert)
        elif channel.type == "slack":
            await self._send_slack_notification(channel, alert)
        elif channel.type == "webhook":
            await self._send_webhook_notification(channel, alert)
        elif channel.type == "sms":
            await self._send_sms_notification(channel, alert)
        else:
            logger.warning(f"Unknown notification channel type: {channel.type}")

    async def _send_email_notification(
        self, channel: NotificationChannel, alert: Alert
    ):
        """Send email notification."""
        # This would integrate with actual email sending
        logger.info(f"Sending email notification for alert {alert.id}")

    async def _send_slack_notification(
        self, channel: NotificationChannel, alert: Alert
    ):
        """Send Slack notification."""
        # This would integrate with actual Slack API
        logger.info(f"Sending Slack notification for alert {alert.id}")

    async def _send_webhook_notification(
        self, channel: NotificationChannel, alert: Alert
    ):
        """Send webhook notification."""
        # This would integrate with actual webhook API
        logger.info(f"Sending webhook notification for alert {alert.id}")

    async def _send_sms_notification(self, channel: NotificationChannel, alert: Alert):
        """Send SMS notification."""
        # This would integrate with actual SMS service
        logger.info(f"Sending SMS notification for alert {alert.id}")

    def enable(self):
        """Enable alerting."""
        self.enabled = True
        logger.info("Alerting enabled")

    def disable(self):
        """Disable alerting."""
        self.enabled = False
        logger.info("Alerting disabled")

    def is_enabled(self) -> bool:
        """Check if alerting is enabled."""
        return self.enabled

    def is_notification_service_running(self) -> bool:
        """Check if notification service is running."""
        return self.running

    def get_alerting_stats(self) -> Dict[str, Any]:
        """Get alerting statistics."""
        return {
            "enabled": self.enabled,
            "notification_service_running": self.running,
            "total_rules": len(self.rules),
            "enabled_rules": len([r for r in self.rules.values() if r.enabled]),
            "total_channels": len(self.channels),
            "enabled_channels": len([c for c in self.channels.values() if c.enabled]),
            "total_alerts": len(self.alerts),
            "active_alerts": len(
                [a for a in self.alerts.values() if a.status == AlertStatus.ACTIVE]
            ),
            "queue_size": self.notification_queue.qsize(),
        }


# Global alert manager instance
alert_manager = AlertManager()


def get_alert_manager() -> AlertManager:
    """Get the global alert manager instance."""
    return alert_manager
