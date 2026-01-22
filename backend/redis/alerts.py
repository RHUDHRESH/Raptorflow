"""
Alert management system for Redis infrastructure.

Provides comprehensive alerting, notification routing,
escalation policies, and alert lifecycle management.
"""

import asyncio
import json
import logging
import smtplib
import uuid
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .client import get_redis
from .critical_fixes import SecureErrorHandler
from .monitoring import Alert, AlertSeverity, MonitorStatus


class AlertStatus(Enum):
    """Alert status enumeration."""

    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    ESCALATED = "escalated"


class NotificationChannel(Enum):
    """Notification channel enumeration."""

    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"
    PAGERDUTY = "pagerduty"
    TELEGRAM = "telegram"


class EscalationPolicy(Enum):
    """Escalation policy enumeration."""

    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    IMMEDIATE = "immediate"
    CUSTOM = "custom"


@dataclass
class NotificationConfig:
    """Notification configuration."""

    channel: NotificationChannel
    enabled: bool = True

    # Channel-specific settings
    email_recipients: List[str] = field(default_factory=list)
    email_subject_template: str = "Alert: {title}"
    email_body_template: str = (
        "Alert: {title}\n\n{description}\n\nSeverity: {severity}\nTimestamp: {timestamp}"
    )

    slack_webhook_url: str = ""
    slack_channel: str = "#alerts"
    slack_username: str = "Redis Monitor"

    webhook_url: str = ""
    webhook_method: str = "POST"
    webhook_headers: Dict[str, str] = field(default_factory=dict)

    sms_recipients: List[str] = field(default_factory=list)
    sms_message_template: str = "Redis Alert: {title} - {severity}"

    pagerduty_service_key: str = ""
    pagerduty_severity: str = "critical"

    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # Notification settings
    rate_limit_per_hour: int = 10
    retry_attempts: int = 3
    retry_delay_seconds: int = 60

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.channel, str):
            self.channel = NotificationChannel(self.channel)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)

        # Convert enum to string
        data["channel"] = self.channel.value

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NotificationConfig":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class EscalationRule:
    """Escalation rule configuration."""

    rule_id: str
    name: str
    policy: EscalationPolicy

    # Trigger conditions
    severity_threshold: AlertSeverity = AlertSeverity.ERROR
    time_threshold_minutes: int = 30
    consecutive_violations: int = 3

    # Escalation actions
    escalate_to_channels: List[NotificationChannel] = field(default_factory=list)
    escalate_to_users: List[str] = field(default_factory=list)

    # Custom escalation logic
    custom_script: Optional[str] = None
    custom_webhook: Optional[str] = None

    # Timing
    escalation_delay_minutes: int = 0
    max_escalations: int = 3

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.policy, str):
            self.policy = EscalationPolicy(self.policy)
        if isinstance(self.severity_threshold, str):
            self.severity_threshold = AlertSeverity(self.severity_threshold)

    def should_escalate(self, alert: Alert, violation_count: int) -> bool:
        """Check if alert should be escalated."""
        if alert.severity.value < self.severity_threshold.value:
            return False

        if violation_count < self.consecutive_violations:
            return False

        if alert.acknowledged_at:
            return False

        # Check time threshold
        if (
            alert.created_at + timedelta(minutes=self.time_threshold_minutes)
            > datetime.now()
        ):
            return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)

        # Convert enums to strings
        data["policy"] = self.policy.value
        data["severity_threshold"] = self.severity_threshold.value

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EscalationRule":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class AlertGroup:
    """Alert grouping for correlation and suppression."""

    group_id: str
    name: str
    description: str

    # Grouping criteria
    cluster_ids: List[str] = field(default_factory=list)
    node_ids: List[str] = field(default_factory=list)
    alert_types: List[str] = field(default_factory=list)
    severity_levels: List[AlertSeverity] = field(default_factory=list)

    # Suppression rules
    suppress_duplicates: bool = True
    suppression_window_minutes: int = 5
    max_alerts_per_window: int = 1

    # Auto-resolution rules
    auto_resolve_minutes: Optional[int] = None
    auto_resolve_threshold: Optional[float] = None

    def __post_init__(self):
        """Post-initialization processing."""
        if (
            isinstance(self.severity_levels, list)
            and self.severity_levels
            and isinstance(self.severity_levels[0], str)
        ):
            self.severity_levels = [
                AlertSeverity(level) for level in self.severity_levels
            ]

    def matches_alert(self, alert: Alert) -> bool:
        """Check if alert matches this group."""
        # Check cluster IDs
        if self.cluster_ids and alert.cluster_id not in self.cluster_ids:
            return False

        # Check node IDs
        if self.node_ids and alert.node_id not in self.node_ids:
            return False

        # Check alert types
        if self.alert_types and alert.alert_type not in self.alert_types:
            return False

        # Check severity levels
        if self.severity_levels and alert.severity not in self.severity_levels:
            return False

        return True

    def should_suppress(self, alert: Alert, existing_alerts: List[Alert]) -> bool:
        """Check if alert should be suppressed."""
        if not self.suppress_duplicates:
            return False

        # Check for similar alerts in suppression window
        cutoff_time = datetime.now() - timedelta(
            minutes=self.suppression_window_minutes
        )

        similar_alerts = [
            existing
            for existing in existing_alerts
            if existing.created_at > cutoff_time
            and existing.alert_type == alert.alert_type
            and existing.cluster_id == alert.cluster_id
            and (existing.node_id == alert.node_id or existing.node_id is None)
        ]

        return len(similar_alerts) >= self.max_alerts_per_window

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)

        # Convert enums to strings
        data["severity_levels"] = [level.value for level in self.severity_levels]

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AlertGroup":
        """Create from dictionary."""
        return cls(**data)


class AlertManager:
    """Manages alert lifecycle, notifications, and escalation."""

    def __init__(self):
        self.redis = get_redis()
        self.error_handler = SecureErrorHandler()
        self.logger = logging.getLogger("alert_manager")

        # Alert management
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_groups: Dict[str, AlertGroup] = {}
        self.escalation_rules: Dict[str, EscalationRule] = {}
        self.notification_configs: Dict[str, NotificationConfig] = {}

        # State tracking
        self.is_running = False
        self._processing_task = None

        # Notification state
        self._notification_queue: List[Dict[str, Any]] = []
        self._rate_limits: Dict[str, List[datetime]] = {}

        # Setup default configurations
        self._setup_default_configs()

    def _setup_default_configs(self):
        """Setup default alert configurations."""
        # Default notification configs
        email_config = NotificationConfig(
            channel=NotificationChannel.EMAIL,
            email_recipients=["admin@example.com"],
            enabled=False,
        )
        self.notification_configs["email"] = email_config

        slack_config = NotificationConfig(
            channel=NotificationChannel.SLACK,
            slack_webhook_url="",
            slack_channel="#alerts",
            enabled=False,
        )
        self.notification_configs["slack"] = slack_config

        webhook_config = NotificationConfig(
            channel=NotificationChannel.WEBHOOK, webhook_url="", enabled=False
        )
        self.notification_configs["webhook"] = webhook_config

        # Default escalation rules
        critical_escalation = EscalationRule(
            rule_id="critical_escalation",
            name="Critical Alert Escalation",
            policy=EscalationPolicy.IMMEDIATE,
            severity_threshold=AlertSeverity.CRITICAL,
            time_threshold_minutes=5,
            escalate_to_channels=[NotificationChannel.EMAIL, NotificationChannel.SMS],
        )
        self.escalation_rules["critical"] = critical_escalation

        # Default alert groups
        memory_alerts = AlertGroup(
            group_id="memory_alerts",
            name="Memory Alerts",
            description="Memory-related alerts",
            alert_types=["memory_usage"],
            suppress_duplicates=True,
            suppression_window_minutes=10,
        )
        self.alert_groups["memory"] = memory_alerts

    def add_notification_config(self, name: str, config: NotificationConfig):
        """Add notification configuration."""
        self.notification_configs[name] = config
        self.logger.info(f"Added notification config {name} for {config.channel.value}")

    def add_escalation_rule(self, rule: EscalationRule):
        """Add escalation rule."""
        self.escalation_rules[rule.rule_id] = rule
        self.logger.info(f"Added escalation rule {rule.rule_id}")

    def add_alert_group(self, group: AlertGroup):
        """Add alert group."""
        self.alert_groups[group.group_id] = group
        self.logger.info(f"Added alert group {group.group_id}")

    async def start_processing(self):
        """Start alert processing."""
        if self.is_running:
            return

        self.is_running = True
        self._processing_task = asyncio.create_task(self._processing_loop())

        self.logger.info("Started alert processing")

        try:
            await self._processing_task
        except asyncio.CancelledError:
            pass
        finally:
            self.is_running = False
            self._processing_task = None
            self.logger.info("Stopped alert processing")

    async def stop_processing(self):
        """Stop alert processing."""
        if self._processing_task:
            self._processing_task.cancel()
            self._processing_task = None

        self.is_running = False
        self.logger.info("Stopped alert processing")

    async def _processing_loop(self):
        """Main alert processing loop."""
        while self.is_running:
            try:
                # Process notification queue
                await self._process_notifications()

                # Check for escalations
                await self._check_escalations()

                # Clean up old alerts
                await self._cleanup_old_alerts()

                # Wait for next iteration
                await asyncio.sleep(10)  # Process every 10 seconds

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Alert processing loop error: {e}")
                await asyncio.sleep(5)

    async def process_alert(self, alert: Alert) -> bool:
        """Process a new alert."""
        try:
            # Check alert groups for suppression
            for group in self.alert_groups.values():
                if group.matches_alert(alert):
                    existing_alerts = list(self.active_alerts.values())
                    if group.should_suppress(alert, existing_alerts):
                        self.logger.info(
                            f"Alert {alert.alert_id} suppressed by group {group.group_id}"
                        )
                        return False

            # Add to active alerts
            self.active_alerts[alert.alert_id] = alert

            # Store in Redis
            alert_key = f"alert:{alert.alert_id}"
            await self.redis.set_json(
                alert_key, alert.to_dict(), ex=86400 * 7
            )  # 7 days

            # Queue for notification
            await self._queue_notification(alert)

            self.logger.info(f"Processed alert {alert.alert_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to process alert {alert.alert_id}: {e}")
            return False

    async def _queue_notification(self, alert: Alert):
        """Queue alert for notification."""
        notification = {
            "alert_id": alert.alert_id,
            "alert": alert.to_dict(),
            "queued_at": datetime.now().isoformat(),
            "attempts": 0,
        }

        self._notification_queue.append(notification)

    async def _process_notifications(self):
        """Process notification queue."""
        if not self._notification_queue:
            return

        # Process notifications
        processed = []

        for notification in self._notification_queue[:10]:  # Process 10 at a time
            try:
                alert = Alert.from_dict(notification["alert"])

                # Check rate limits
                if not self._check_rate_limit(alert):
                    continue

                # Send notifications
                await self._send_notifications(alert)

                processed.append(notification)

            except Exception as e:
                self.logger.error(
                    f"Failed to process notification {notification['alert_id']}: {e}"
                )

                # Retry logic
                notification["attempts"] += 1
                if notification["attempts"] < 3:
                    continue  # Keep in queue for retry
                else:
                    processed.append(notification)  # Remove after max attempts

        # Remove processed notifications
        for notification in processed:
            if notification in self._notification_queue:
                self._notification_queue.remove(notification)

    async def _send_notifications(self, alert: Alert):
        """Send notifications for alert."""
        for config_name, config in self.notification_configs.items():
            if not config.enabled:
                continue

            try:
                if config.channel == NotificationChannel.EMAIL:
                    await self._send_email_notification(alert, config)
                elif config.channel == NotificationChannel.SLACK:
                    await self._send_slack_notification(alert, config)
                elif config.channel == NotificationChannel.WEBHOOK:
                    await self._send_webhook_notification(alert, config)
                elif config.channel == NotificationChannel.SMS:
                    await self._send_sms_notification(alert, config)
                elif config.channel == NotificationChannel.PAGERDUTY:
                    await self._send_pagerduty_notification(alert, config)
                elif config.channel == NotificationChannel.TELEGRAM:
                    await self._send_telegram_notification(alert, config)

            except Exception as e:
                self.logger.error(
                    f"Failed to send {config.channel.value} notification: {e}"
                )

    def _check_rate_limit(self, alert: Alert) -> bool:
        """Check notification rate limits."""
        for config_name, config in self.notification_configs.items():
            if not config.enabled:
                continue

            # Check rate limit for this channel
            key = f"{config_name}:{alert.cluster_id}"
            now = datetime.now()

            # Clean old entries
            if key in self._rate_limits:
                self._rate_limits[key] = [
                    timestamp
                    for timestamp in self._rate_limits[key]
                    if now - timestamp < timedelta(hours=1)
                ]

            # Check if rate limit exceeded
            if (
                key in self._rate_limits
                and len(self._rate_limits[key]) >= config.rate_limit_per_hour
            ):
                return False

            # Add current notification
            if key not in self._rate_limits:
                self._rate_limits[key] = []
            self._rate_limits[key].append(now)

        return True

    async def _send_email_notification(self, alert: Alert, config: NotificationConfig):
        """Send email notification."""
        if not config.email_recipients:
            return

        # This would integrate with actual email service
        # For now, just log the notification
        subject = config.email_subject_template.format(
            title=alert.title,
            severity=alert.severity.value,
            cluster_id=alert.cluster_id,
        )

        body = config.email_body_template.format(
            title=alert.title,
            description=alert.description,
            severity=alert.severity.value,
            timestamp=alert.created_at.isoformat(),
            cluster_id=alert.cluster_id,
            node_id=alert.node_id or "N/A",
            current_value=alert.current_value,
            threshold_value=alert.threshold_value,
        )

        self.logger.info(
            f"Email notification would be sent to {config.email_recipients}: {subject}"
        )

        # Store notification for debugging
        notification_key = f"notification:email:{alert.alert_id}"
        await self.redis.set_json(
            notification_key,
            {
                "subject": subject,
                "body": body,
                "recipients": config.email_recipients,
                "sent_at": datetime.now().isoformat(),
            },
            ex=3600,
        )  # 1 hour

    async def _send_slack_notification(self, alert: Alert, config: NotificationConfig):
        """Send Slack notification."""
        if not config.slack_webhook_url:
            return

        # This would integrate with actual Slack API
        # For now, just log the notification
        payload = {
            "channel": config.slack_channel,
            "username": config.slack_username,
            "text": f"🚨 {alert.title}",
            "attachments": [
                {
                    "color": self._get_slack_color(alert.severity),
                    "fields": [
                        {
                            "title": "Severity",
                            "value": alert.severity.value,
                            "short": True,
                        },
                        {"title": "Cluster", "value": alert.cluster_id, "short": True},
                        {
                            "title": "Description",
                            "value": alert.description,
                            "short": False,
                        },
                        {
                            "title": "Current Value",
                            "value": str(alert.current_value),
                            "short": True,
                        },
                        {
                            "title": "Threshold",
                            "value": str(alert.threshold_value),
                            "short": True,
                        },
                        {
                            "title": "Time",
                            "value": alert.created_at.isoformat(),
                            "short": True,
                        },
                    ],
                }
            ],
        }

        self.logger.info(f"Slack notification would be sent to {config.slack_channel}")

        # Store notification for debugging
        notification_key = f"notification:slack:{alert.alert_id}"
        await self.redis.set_json(
            notification_key,
            {"payload": payload, "sent_at": datetime.now().isoformat()},
            ex=3600,
        )  # 1 hour

    async def _send_webhook_notification(
        self, alert: Alert, config: NotificationConfig
    ):
        """Send webhook notification."""
        if not config.webhook_url:
            return

        # This would integrate with actual webhook service
        # For now, just log the notification
        payload = {
            "alert_id": alert.alert_id,
            "alert_type": alert.alert_type,
            "severity": alert.severity.value,
            "title": alert.title,
            "description": alert.description,
            "cluster_id": alert.cluster_id,
            "node_id": alert.node_id,
            "current_value": alert.current_value,
            "threshold_value": alert.threshold_value,
            "created_at": alert.created_at.isoformat(),
        }

        self.logger.info(f"Webhook notification would be sent to {config.webhook_url}")

        # Store notification for debugging
        notification_key = f"notification:webhook:{alert.alert_id}"
        await self.redis.set_json(
            notification_key,
            {
                "url": config.webhook_url,
                "method": config.webhook_method,
                "payload": payload,
                "sent_at": datetime.now().isoformat(),
            },
            ex=3600,
        )  # 1 hour

    async def _send_sms_notification(self, alert: Alert, config: NotificationConfig):
        """Send SMS notification."""
        if not config.sms_recipients:
            return

        # This would integrate with actual SMS service
        # For now, just log the notification
        message = config.sms_message_template.format(
            title=alert.title,
            severity=alert.severity.value,
            cluster_id=alert.cluster_id,
        )

        self.logger.info(
            f"SMS notification would be sent to {config.sms_recipients}: {message}"
        )

        # Store notification for debugging
        notification_key = f"notification:sms:{alert.alert_id}"
        await self.redis.set_json(
            notification_key,
            {
                "message": message,
                "recipients": config.sms_recipients,
                "sent_at": datetime.now().isoformat(),
            },
            ex=3600,
        )  # 1 hour

    async def _send_pagerduty_notification(
        self, alert: Alert, config: NotificationConfig
    ):
        """Send PagerDuty notification."""
        if not config.pagerduty_service_key:
            return

        # This would integrate with actual PagerDuty API
        # For now, just log the notification
        payload = {
            "service_key": config.pagerduty_service_key,
            "event_type": "trigger",
            "incident_key": alert.alert_id,
            "description": alert.title,
            "client": "Redis Monitor",
            "client_url": "https://redis-monitor.example.com",
            "details": {
                "alert_id": alert.alert_id,
                "severity": alert.severity.value,
                "cluster_id": alert.cluster_id,
                "description": alert.description,
                "current_value": alert.current_value,
                "threshold_value": alert.threshold_value,
            },
        }

        self.logger.info(
            f"PagerDuty notification would be sent for alert {alert.alert_id}"
        )

        # Store notification for debugging
        notification_key = f"notification:pagerduty:{alert.alert_id}"
        await self.redis.set_json(
            notification_key,
            {"payload": payload, "sent_at": datetime.now().isoformat()},
            ex=3600,
        )  # 1 hour

    async def _send_telegram_notification(
        self, alert: Alert, config: NotificationConfig
    ):
        """Send Telegram notification."""
        if not config.telegram_bot_token or not config.telegram_chat_id:
            return

        # This would integrate with actual Telegram API
        # For now, just log the notification
        message = f"🚨 {alert.title}\n\n{alert.description}\n\nSeverity: {alert.severity.value}\nCluster: {alert.cluster_id}\nTime: {alert.created_at.isoformat()}"

        self.logger.info(
            f"Telegram notification would be sent to chat {config.telegram_chat_id}"
        )

        # Store notification for debugging
        notification_key = f"notification:telegram:{alert.alert_id}"
        await self.redis.set_json(
            notification_key,
            {
                "message": message,
                "chat_id": config.telegram_chat_id,
                "sent_at": datetime.now().isoformat(),
            },
            ex=3600,
        )  # 1 hour

    def _get_slack_color(self, severity: AlertSeverity) -> str:
        """Get Slack color for alert severity."""
        colors = {
            AlertSeverity.INFO: "#36a64f",  # green
            AlertSeverity.WARNING: "#ff9500",  # orange
            AlertSeverity.ERROR: "#ff0000",  # red
            AlertSeverity.CRITICAL: "#8b0000",  # dark red
        }
        return colors.get(severity, "#36a64f")

    async def _check_escalations(self):
        """Check for alert escalations."""
        for alert_id, alert in self.active_alerts.items():
            if alert.is_acknowledged() or alert.is_resolved():
                continue

            for rule in self.escalation_rules.values():
                if rule.should_escalate(alert, alert.violation_count):
                    await self._escalate_alert(alert, rule)

    async def _escalate_alert(self, alert: Alert, rule: EscalationRule):
        """Escalate alert according to rule."""
        self.logger.info(f"Escalating alert {alert.alert_id} using rule {rule.rule_id}")

        # Update alert status
        alert.severity = AlertSeverity.CRITICAL  # Escalate severity

        # Send escalation notifications
        for channel in rule.escalate_to_channels:
            config = self.notification_configs.get(channel.value)
            if config and config.enabled:
                await self._send_notifications(alert)

        # Log security event for critical escalations
        if alert.severity == AlertSeverity.CRITICAL:
            self.error_handler.log_security_event(
                event_type="alert_escalation",
                severity="HIGH",
                description=f"Alert escalated: {alert.title}",
                context={
                    "alert_id": alert.alert_id,
                    "rule_id": rule.rule_id,
                    "cluster_id": alert.cluster_id,
                },
            )

    async def _cleanup_old_alerts(self):
        """Clean up old resolved alerts."""
        cutoff_time = datetime.now() - timedelta(days=7)

        alerts_to_remove = []

        for alert_id, alert in self.active_alerts.items():
            if (
                alert.is_resolved()
                and alert.resolved_at
                and alert.resolved_at < cutoff_time
            ):
                alerts_to_remove.append(alert_id)

        for alert_id in alerts_to_remove:
            del self.active_alerts[alert_id]

            # Remove from Redis
            alert_key = f"alert:{alert_id}"
            await self.redis.delete(alert_key)

        if alerts_to_remove:
            self.logger.info(f"Cleaned up {len(alerts_to_remove)} old alerts")

    async def acknowledge_alert(self, alert_id: str, user: str = "system") -> bool:
        """Acknowledge an alert."""
        if alert_id not in self.active_alerts:
            return False

        alert = self.active_alerts[alert_id]
        alert.acknowledge()

        # Update in Redis
        alert_key = f"alert:{alert_id}"
        await self.redis.set_json(alert_key, alert.to_dict(), ex=86400 * 7)

        self.logger.info(f"Alert {alert_id} acknowledged by {user}")
        return True

    async def resolve_alert(self, alert_id: str, user: str = "system") -> bool:
        """Resolve an alert."""
        if alert_id not in self.active_alerts:
            return False

        alert = self.active_alerts[alert_id]
        alert.resolve()

        # Update in Redis
        alert_key = f"alert:{alert_id}"
        await self.redis.set_json(alert_key, alert.to_dict(), ex=86400 * 7)

        self.logger.info(f"Alert {alert_id} resolved by {user}")
        return True

    async def get_alert_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get alert summary for the specified time period."""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        # Get all alerts from Redis
        pattern = f"alert:*"
        keys = await self.redis.keys(pattern)

        total_alerts = 0
        severity_counts = {severity.value: 0 for severity in AlertSeverity}
        recent_alerts = []

        for key in keys:
            data = await self.redis.get_json(key)
            if data:
                alert = Alert.from_dict(data)

                if alert.created_at >= cutoff_time:
                    total_alerts += 1
                    severity_counts[alert.severity.value] += 1

                    if not alert.is_resolved():
                        recent_alerts.append(alert.to_dict())

        return {
            "time_range_hours": hours,
            "total_alerts": total_alerts,
            "severity_counts": severity_counts,
            "active_alerts": len(recent_alerts),
            "recent_alerts": recent_alerts[:10],  # Top 10
        }

    async def get_notification_status(self) -> Dict[str, Any]:
        """Get notification system status."""
        return {
            "is_running": self.is_running,
            "queue_size": len(self._notification_queue),
            "active_alerts": len(self.active_alerts),
            "notification_configs": {
                name: {
                    "channel": config.channel.value,
                    "enabled": config.enabled,
                    "rate_limit": config.rate_limit_per_hour,
                }
                for name, config in self.notification_configs.items()
            },
            "escalation_rules": len(self.escalation_rules),
            "alert_groups": len(self.alert_groups),
            "rate_limits": {
                key: len(timestamps) for key, timestamps in self._rate_limits.items()
            },
        }

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start_processing()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop_processing()
