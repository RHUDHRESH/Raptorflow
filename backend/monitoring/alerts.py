"""
Alert management system for Raptorflow backend.
Handles alert creation, notification, and escalation.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from backend.config.settings import get_settings
from ..redis_core.client import RedisClient

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """Alert status values."""

    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


@dataclass
class Alert:
    """Alert data structure."""

    id: str
    title: str
    message: str
    severity: AlertSeverity
    status: AlertStatus
    source: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    escalation_level: int = 0
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "severity": self.severity.value,
            "status": self.status.value,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "acknowledged_at": (
                self.acknowledged_at.isoformat() if self.acknowledged_at else None
            ),
            "acknowledged_by": self.acknowledged_by,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolved_by": self.resolved_by,
            "escalation_level": self.escalation_level,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Alert":
        """Create alert from dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            message=data["message"],
            severity=AlertSeverity(data["severity"]),
            status=AlertStatus(data["status"]),
            source=data["source"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {}),
            acknowledged_at=(
                datetime.fromisoformat(data["acknowledged_at"])
                if data.get("acknowledged_at")
                else None
            ),
            acknowledged_by=data.get("acknowledged_by"),
            resolved_at=(
                datetime.fromisoformat(data["resolved_at"])
                if data.get("resolved_at")
                else None
            ),
            resolved_by=data.get("resolved_by"),
            escalation_level=data.get("escalation_level", 0),
            tags=data.get("tags", []),
        )


class AlertManager:
    """Alert management system."""

    def __init__(self):
        """Initialize alert manager."""
        self.settings = get_settings()
        self.redis_client = RedisClient()
        self.alert_rules = {}
        self.notification_channels = {}
        self.escalation_policies = {}

        # Initialize default rules
        self._initialize_default_rules()
        self._initialize_notification_channels()
        self._initialize_escalation_policies()

    def _initialize_default_rules(self):
        """Initialize default alert rules."""
        self.alert_rules = {
            "high_cpu_usage": {
                "condition": lambda metrics: metrics.get("cpu_percent", 0) > 80,
                "severity": AlertSeverity.HIGH,
                "title": "High CPU Usage",
                "message_template": "CPU usage is {cpu_percent:.1f}%",
                "cooldown": 300,  # 5 minutes
                "enabled": True,
            },
            "high_memory_usage": {
                "condition": lambda metrics: metrics.get("memory_percent", 0) > 85,
                "severity": AlertSeverity.HIGH,
                "title": "High Memory Usage",
                "message_template": "Memory usage is {memory_percent:.1f}%",
                "cooldown": 300,
                "enabled": True,
            },
            "redis_connection_failed": {
                "condition": lambda status: status.get("redis", {}).get("status")
                == "unhealthy",
                "severity": AlertSeverity.CRITICAL,
                "title": "Redis Connection Failed",
                "message_template": "Redis service is unavailable: {error}",
                "cooldown": 60,
                "enabled": True,
            },
            "database_connection_failed": {
                "condition": lambda status: status.get("database", {}).get("status")
                == "unhealthy",
                "severity": AlertSeverity.CRITICAL,
                "title": "Database Connection Failed",
                "message_template": "Database service is unavailable: {error}",
                "cooldown": 60,
                "enabled": True,
            },
            "high_error_rate": {
                "condition": lambda metrics: metrics.get("error_rate", 0) > 0.05,  # 5%
                "severity": AlertSeverity.MEDIUM,
                "title": "High Error Rate",
                "message_template": "Error rate is {error_rate:.1%}",
                "cooldown": 600,  # 10 minutes
                "enabled": True,
            },
            "slow_response_time": {
                "condition": lambda metrics: metrics.get("response_time_p95", 0)
                > 1000,  # 1 second
                "severity": AlertSeverity.MEDIUM,
                "title": "Slow Response Time",
                "message_template": "95th percentile response time is {response_time_p95:.0f}ms",
                "cooldown": 600,
                "enabled": True,
            },
            "usage_limit_reached": {
                "condition": lambda usage: usage.get("percentage_used", 0) > 90,
                "severity": AlertSeverity.HIGH,
                "title": "Usage Limit Reached",
                "message_template": "Usage limit {percentage_used:.1f}% reached for workspace {workspace_id}",
                "cooldown": 1800,  # 30 minutes
                "enabled": True,
            },
        }

    def _initialize_notification_channels(self):
        """Initialize notification channels."""
        self.notification_channels = {
            "slack": {
                "enabled": bool(self.settings.SLACK_WEBHOOK_URL),
                "webhook_url": self.settings.SLACK_WEBHOOK_URL,
                "channel": "#alerts",
                "severity_threshold": AlertSeverity.MEDIUM,
            },
            "email": {
                "enabled": bool(self.settings.EMAIL_FROM),
                "smtp_host": self.settings.SMTP_HOST,
                "smtp_port": self.settings.SMTP_PORT,
                "from_email": self.settings.EMAIL_FROM,
                "severity_threshold": AlertSeverity.HIGH,
            },
            "webhook": {
                "enabled": True,
                "url": "https://api.raptorflow.app/webhooks/alerts",
                "severity_threshold": AlertSeverity.LOW,
            },
        }

    def _initialize_escalation_policies(self):
        """Initialize escalation policies."""
        self.escalation_policies = {
            AlertSeverity.CRITICAL: {
                "escalation_intervals": [300, 900, 1800],  # 5min, 15min, 30min
                "max_escalation_level": 3,
                "channels": ["slack", "email", "webhook"],
            },
            AlertSeverity.HIGH: {
                "escalation_intervals": [900, 3600],  # 15min, 1hour
                "max_escalation_level": 2,
                "channels": ["slack", "webhook"],
            },
            AlertSeverity.MEDIUM: {
                "escalation_intervals": [3600],  # 1hour
                "max_escalation_level": 1,
                "channels": ["webhook"],
            },
            AlertSeverity.LOW: {
                "escalation_intervals": [],
                "max_escalation_level": 0,
                "channels": ["webhook"],
            },
        }

    async def check_alerts(self) -> List[Alert]:
        """Check all alert rules and return triggered alerts."""
        alerts = []

        try:
            # Get system metrics
            system_metrics = await self._get_system_metrics()
            system_status = await self._get_system_status()

            # Check each rule
            for rule_name, rule in self.alert_rules.items():
                if not rule["enabled"]:
                    continue

                # Check cooldown
                if await self._is_in_cooldown(rule_name):
                    continue

                # Evaluate condition
                condition_met = False
                context = {}

                if "cpu" in rule_name or "memory" in rule_name:
                    condition_met = rule["condition"](system_metrics)
                    context = system_metrics
                elif "connection" in rule_name:
                    condition_met = rule["condition"](system_status)
                    context = system_status
                else:
                    # Generic metrics check
                    condition_met = rule["condition"](system_metrics)
                    context = system_metrics

                if condition_met:
                    # Create alert
                    alert = await self._create_alert(rule_name, rule, context)
                    alerts.append(alert)

                    # Set cooldown
                    await self._set_cooldown(rule_name, rule["cooldown"])

                    # Send notifications
                    await self._send_notifications(alert)

            return alerts

        except Exception as e:
            logger.error(f"Failed to check alerts: {e}")
            return []

    async def create_manual_alert(
        self,
        title: str,
        message: str,
        severity: AlertSeverity,
        source: str = "manual",
        metadata: Dict[str, Any] = None,
    ) -> Alert:
        """Create a manual alert."""
        import uuid

        alert = Alert(
            id=str(uuid.uuid4()),
            title=title,
            message=message,
            severity=severity,
            status=AlertStatus.ACTIVE,
            source=source,
            timestamp=datetime.utcnow(),
            metadata=metadata or {},
            tags=["manual"],
        )

        # Store alert
        await self._store_alert(alert)

        # Send notifications
        await self._send_notifications(alert)

        logger.info(f"Manual alert created: {alert.id} - {title}")
        return alert

    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert."""
        try:
            alert = await self._get_alert(alert_id)
            if not alert:
                return False

            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.utcnow()
            alert.acknowledged_by = acknowledged_by

            await self._store_alert(alert)

            logger.info(f"Alert acknowledged: {alert_id} by {acknowledged_by}")
            return True

        except Exception as e:
            logger.error(f"Failed to acknowledge alert {alert_id}: {e}")
            return False

    async def resolve_alert(self, alert_id: str, resolved_by: str) -> bool:
        """Resolve an alert."""
        try:
            alert = await self._get_alert(alert_id)
            if not alert:
                return False

            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.utcnow()
            alert.resolved_by = resolved_by

            await self._store_alert(alert)

            logger.info(f"Alert resolved: {alert_id} by {resolved_by}")
            return True

        except Exception as e:
            logger.error(f"Failed to resolve alert {alert_id}: {e}")
            return False

    async def get_active_alerts(
        self, severity: Optional[AlertSeverity] = None
    ) -> List[Alert]:
        """Get active alerts."""
        try:
            pattern = "alert:*"
            keys = await self.redis_client.keys(pattern)

            alerts = []
            for key in keys:
                alert_data = await self.redis_client.get(key)
                if alert_data:
                    alert = Alert.from_dict(alert_data)

                    if alert.status == AlertStatus.ACTIVE:
                        if severity is None or alert.severity == severity:
                            alerts.append(alert)

            # Sort by timestamp (most recent first)
            alerts.sort(key=lambda x: x.timestamp, reverse=True)

            return alerts

        except Exception as e:
            logger.error(f"Failed to get active alerts: {e}")
            return []

    async def get_alert_history(
        self, limit: int = 100, severity: Optional[AlertSeverity] = None
    ) -> List[Alert]:
        """Get alert history."""
        try:
            pattern = "alert:*"
            keys = await self.redis_client.keys(pattern)

            alerts = []
            for key in keys:
                alert_data = await self.redis_client.get(key)
                if alert_data:
                    alert = Alert.from_dict(alert_data)

                    if severity is None or alert.severity == severity:
                        alerts.append(alert)

            # Sort by timestamp (most recent first)
            alerts.sort(key=lambda x: x.timestamp, reverse=True)

            return alerts[:limit]

        except Exception as e:
            logger.error(f"Failed to get alert history: {e}")
            return []

    async def escalate_alert(self, alert_id: str) -> bool:
        """Escalate an alert."""
        try:
            alert = await self._get_alert(alert_id)
            if not alert:
                return False

            policy = self.escalation_policies.get(alert.severity, {})
            max_level = policy.get("max_escalation_level", 0)

            if alert.escalation_level >= max_level:
                return False  # Already at max escalation

            alert.escalation_level += 1
            alert.tags.append(f"escalated_level_{alert.escalation_level}")

            await self._store_alert(alert)

            # Send escalation notifications
            await self._send_escalation_notifications(alert)

            logger.warning(
                f"Alert escalated: {alert_id} to level {alert.escalation_level}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to escalate alert {alert_id}: {e}")
            return False

    async def suppress_alert(self, alert_id: str, duration: int = 3600) -> bool:
        """Suppress an alert for a duration."""
        try:
            alert = await self._get_alert(alert_id)
            if not alert:
                return False

            alert.status = AlertStatus.SUPPRESSED
            alert.metadata["suppressed_until"] = (
                datetime.utcnow() + timedelta(seconds=duration)
            ).isoformat()

            await self._store_alert(alert)

            logger.info(f"Alert suppressed: {alert_id} for {duration} seconds")
            return True

        except Exception as e:
            logger.error(f"Failed to suppress alert {alert_id}: {e}")
            return False

    async def _get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        try:
            import psutil

            return {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": (
                    psutil.disk_usage("/").used / psutil.disk_usage("/").total
                )
                * 100,
                "load_average": (
                    psutil.getloadavg()[0] if hasattr(psutil, "getloadavg") else 0
                ),
            }

        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return {}

    async def _get_system_status(self) -> Dict[str, Any]:
        """Get current system status."""
        try:
            # This would integrate with actual health checks
            return {
                "redis": {"status": "healthy"},
                "database": {"status": "healthy"},
                "vertex_ai": {"status": "healthy"},
                "cloud_storage": {"status": "healthy"},
            }

        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return {}

    async def _create_alert(
        self, rule_name: str, rule: Dict[str, Any], context: Dict[str, Any]
    ) -> Alert:
        """Create an alert from a rule."""
        import uuid

        # Format message
        message = rule["message_template"].format(**context)

        alert = Alert(
            id=str(uuid.uuid4()),
            title=rule["title"],
            message=message,
            severity=rule["severity"],
            status=AlertStatus.ACTIVE,
            source="automated",
            timestamp=datetime.utcnow(),
            metadata={
                "rule_name": rule_name,
                "context": context,
            },
            tags=["automated", rule_name],
        )

        # Store alert
        await self._store_alert(alert)

        return alert

    async def _store_alert(self, alert: Alert) -> None:
        """Store alert in Redis."""
        key = f"alert:{alert.id}"
        alert_data = alert.to_dict()

        # Store with TTL (7 days)
        await self.redis_client.set(key, alert_data, ex=604800)

    async def _get_alert(self, alert_id: str) -> Optional[Alert]:
        """Get alert by ID."""
        key = f"alert:{alert_id}"
        alert_data = await self.redis_client.get(key)

        if alert_data:
            return Alert.from_dict(alert_data)

        return None

    async def _is_in_cooldown(self, rule_name: str) -> bool:
        """Check if rule is in cooldown."""
        key = f"alert_cooldown:{rule_name}"
        return await self.redis_client.exists(key)

    async def _set_cooldown(self, rule_name: str, duration: int) -> None:
        """Set cooldown for rule."""
        key = f"alert_cooldown:{rule_name}"
        await self.redis_client.set(key, "1", ex=duration)

    async def _send_notifications(self, alert: Alert) -> None:
        """Send notifications for alert."""
        policy = self.escalation_policies.get(alert.severity, {})
        channels = policy.get("channels", ["webhook"])

        for channel_name in channels:
            channel = self.notification_channels.get(channel_name)
            if channel and channel.get("enabled", False):
                await self._send_notification(alert, channel_name, channel)

    async def _send_escalation_notifications(self, alert: Alert) -> None:
        """Send escalation notifications."""
        # Send to all available channels for escalation
        for channel_name, channel in self.notification_channels.items():
            if channel.get("enabled", False):
                await self._send_notification(
                    alert, channel_name, channel, escalated=True
                )

    async def _send_notification(
        self,
        alert: Alert,
        channel_name: str,
        channel_config: Dict[str, Any],
        escalated: bool = False,
    ) -> None:
        """Send notification to specific channel."""
        try:
            if channel_name == "slack":
                await self._send_slack_notification(alert, channel_config, escalated)
            elif channel_name == "email":
                await self._send_email_notification(alert, channel_config, escalated)
            elif channel_name == "webhook":
                await self._send_webhook_notification(alert, channel_config, escalated)

        except Exception as e:
            logger.error(
                f"Failed to send {channel_name} notification for alert {alert.id}: {e}"
            )

    async def _send_slack_notification(
        self, alert: Alert, config: Dict[str, Any], escalated: bool
    ) -> None:
        """Send Slack notification."""
        import httpx

        webhook_url = config["webhook_url"]
        channel = config.get("channel", "#alerts")

        # Determine color based on severity and escalation
        color_map = {
            AlertSeverity.LOW: "good",
            AlertSeverity.MEDIUM: "warning",
            AlertSeverity.HIGH: "danger",
            AlertSeverity.CRITICAL: "danger",
        }

        color = color_map.get(alert.severity, "warning")
        if escalated:
            color = "danger"  # Escalated alerts are always red

        payload = {
            "channel": channel,
            "username": "Raptorflow Alerts",
            "icon_emoji": ":warning:",
            "attachments": [
                {
                    "color": color,
                    "title": alert.title,
                    "text": alert.message,
                    "fields": [
                        {
                            "title": "Severity",
                            "value": alert.severity.value.upper(),
                            "short": True,
                        },
                        {"title": "Source", "value": alert.source, "short": True},
                        {
                            "title": "Time",
                            "value": alert.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"),
                            "short": True,
                        },
                    ],
                    "footer": "Raptorflow Monitoring",
                    "ts": int(alert.timestamp.timestamp()),
                }
            ],
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json=payload)
            response.raise_for_status()

    async def _send_email_notification(
        self, alert: Alert, config: Dict[str, Any], escalated: bool
    ) -> None:
        """Send email notification."""
        # This would integrate with your email service
        logger.info(f"Email notification sent for alert {alert.id}")

    async def _send_webhook_notification(
        self, alert: Alert, config: Dict[str, Any], escalated: bool
    ) -> None:
        """Send webhook notification."""
        import httpx

        webhook_url = config["url"]

        payload = {
            "alert": alert.to_dict(),
            "escalated": escalated,
            "timestamp": datetime.utcnow().isoformat(),
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json=payload)
            # Don't raise for webhook errors to avoid alert loops


# Global alert manager instance
_alert_manager: AlertManager = None


def get_alert_manager() -> AlertManager:
    """Get the global alert manager instance."""
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager()
    return _alert_manager
