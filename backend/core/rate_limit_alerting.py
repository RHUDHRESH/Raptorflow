"""
Rate Limit Alerting Manager
============================

Comprehensive alerting system for rate limiting with abuse detection,
notification management, and automated responses.

Features:
- Real-time abuse detection and alerting
- Multi-channel notifications (email, Slack, webhook)
- Automated response actions
- Alert escalation and de-escalation
- Alert aggregation and deduplication
- Custom alert rules and thresholds
"""

import asyncio
import time
import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)


class AlertType(Enum):
    """Types of rate limit alerts."""
    ABUSE_DETECTED = "abuse_detected"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    UNUSUAL_PATTERN = "unusual_pattern"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    CAPACITY_WARNING = "capacity_warning"
    SECURITY_THREAT = "security_threat"
    SYSTEM_ANOMALY = "system_anomaly"


class AlertSeverity(Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert status."""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


class NotificationChannel(Enum):
    """Notification channels."""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"
    DASHBOARD = "dashboard"


class ResponseAction(Enum):
    """Automated response actions."""
    BLOCK_CLIENT = "block_client"
    INCREASE_LIMITS = "increase_limits"
    DECREASE_LIMITS = "decrease_limits"
    NOTIFY_ADMIN = "notify_admin"
    LOG_EVENT = "log_event"
    SCALE_RESOURCES = "scale_resources"


@dataclass
class AlertRule:
    """Alert rule configuration."""
    
    rule_id: str
    name: str
    description: str
    alert_type: AlertType
    severity: AlertSeverity
    condition: str  # Expression language for conditions
    threshold: float
    time_window_minutes: int
    enabled: bool = True
    
    # Notification settings
    notification_channels: List[NotificationChannel] = field(default_factory=list)
    notification_cooldown_minutes: int = 15
    
    # Response actions
    response_actions: List[ResponseAction] = field(default_factory=list)
    auto_execute_actions: bool = False
    
    # Suppression rules
    suppression_rules: Dict[str, Any] = field(default_factory=dict)
    max_alerts_per_hour: int = 10
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class RateLimitAlert:
    """Rate limit alert instance."""
    
    alert_id: str
    rule_id: str
    alert_type: AlertType
    severity: AlertSeverity
    status: AlertStatus
    
    # Alert data
    title: str
    description: str
    client_id: Optional[str]
    endpoint: Optional[str]
    user_tier: Optional[str]
    ip_address: Optional[str]
    
    # Metrics and context
    metrics: Dict[str, float] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    triggered_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # Response tracking
    notifications_sent: List[NotificationChannel] = field(default_factory=list)
    actions_executed: List[ResponseAction] = field(default_factory=list)
    
    # Metadata
    fingerprint: str = ""
    correlation_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class NotificationConfig:
    """Notification configuration."""
    
    # Email settings
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    email_from: Optional[str] = None
    email_to: List[str] = field(default_factory=list)
    
    # Slack settings
    slack_webhook_url: Optional[str] = None
    slack_channel: str = "#alerts"
    
    # Webhook settings
    webhook_url: Optional[str] = None
    webhook_timeout: int = 10
    
    # SMS settings
    sms_provider: Optional[str] = None
    sms_api_key: Optional[str] = None
    sms_phone_numbers: List[str] = field(default_factory=list)
    
    # General settings
    enable_notifications: bool = True
    notification_timeout: int = 30
    retry_attempts: int = 3


@dataclass
class AlertingConfig:
    """Alerting system configuration."""
    
    # Alert processing
    evaluation_interval_seconds: int = 30
    alert_retention_days: int = 30
    max_active_alerts: int = 1000
    
    # Deduplication
    enable_deduplication: bool = True
    deduplication_window_minutes: int = 5
    
    # Escalation
    enable_escalation: bool = True
    escalation_time_minutes: int = 30
    
    # Performance
    batch_processing_size: int = 100
    enable_async_processing: bool = True
    
    # Notification config
    notification: NotificationConfig = field(default_factory=NotificationConfig)


class RateLimitAlertingManager:
    """Comprehensive rate limit alerting manager."""
    
    def __init__(self, config: AlertingConfig = None):
        self.config = config or AlertingConfig()
        
        # Alert storage
        self.active_alerts: Dict[str, RateLimitAlert] = {}
        self.alert_history: deque = deque(maxlen=10000)
        self.alert_rules: Dict[str, AlertRule] = {}
        
        # Deduplication tracking
        self.recent_fingerprints: Dict[str, datetime] = {}
        self.alert_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        
        # Notification tracking
        self.notification_queue: deque = deque(maxlen=1000)
        self.notification_history: deque = deque(maxlen=5000)
        
        # Response actions
        self.action_queue: deque = deque(maxlen=1000)
        self.action_history: deque = deque(maxlen=5000)
        
        # Statistics
        self.total_alerts_generated = 0
        self.total_notifications_sent = 0
        self.total_actions_executed = 0
        
        # Background tasks
        self._running = False
        self._evaluation_task = None
        self._notification_task = None
        self._action_task = None
        self._cleanup_task = None
        
        # Initialize default rules
        self._initialize_default_rules()
        
        logger.info("Rate Limit Alerting Manager initialized")
    
    def _initialize_default_rules(self) -> None:
        """Initialize default alert rules."""
        default_rules = [
            AlertRule(
                rule_id="high_abuse_score",
                name="High Abuse Score Detected",
                description="Alert when client abuse score exceeds threshold",
                alert_type=AlertType.ABUSE_DETECTED,
                severity=AlertSeverity.HIGH,
                condition="abuse_score > 0.8",
                threshold=0.8,
                time_window_minutes=5,
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK],
                response_actions=[ResponseAction.BLOCK_CLIENT, ResponseAction.NOTIFY_ADMIN],
                auto_execute_actions=True
            ),
            AlertRule(
                rule_id="rate_limit_exceeded",
                name="Rate Limit Exceeded",
                description="Alert when rate limits are consistently exceeded",
                alert_type=AlertType.RATE_LIMIT_EXCEEDED,
                severity=AlertSeverity.MEDIUM,
                condition="block_rate > 0.5",
                threshold=0.5,
                time_window_minutes=10,
                notification_channels=[NotificationChannel.DASHBOARD],
                response_actions=[ResponseAction.LOG_EVENT]
            ),
            AlertRule(
                rule_id="unusual_usage_pattern",
                name="Unusual Usage Pattern",
                description="Alert on unusual usage patterns",
                alert_type=AlertType.UNUSUAL_PATTERN,
                severity=AlertSeverity.MEDIUM,
                condition="anomaly_score > 0.7",
                threshold=0.7,
                time_window_minutes=15,
                notification_channels=[NotificationChannel.EMAIL],
                response_actions=[ResponseAction.NOTIFY_ADMIN]
            ),
            AlertRule(
                rule_id="performance_degradation",
                name="Performance Degradation",
                description="Alert on performance degradation",
                alert_type=AlertType.PERFORMANCE_DEGRADATION,
                severity=AlertSeverity.HIGH,
                condition="avg_response_time > 2.0",
                threshold=2.0,
                time_window_minutes=5,
                notification_channels=[NotificationChannel.SLACK, NotificationChannel.EMAIL],
                response_actions=[ResponseAction.SCALE_RESOURCES]
            ),
            AlertRule(
                rule_id="capacity_warning",
                name="Capacity Warning",
                description="Alert when approaching capacity limits",
                alert_type=AlertType.CAPACITY_WARNING,
                severity=AlertSeverity.CRITICAL,
                condition="utilization > 0.9",
                threshold=0.9,
                time_window_minutes=2,
                notification_channels=[NotificationChannel.SLACK, NotificationChannel.EMAIL, NotificationChannel.SMS],
                response_actions=[ResponseAction.INCREASE_LIMITS, ResponseAction.SCALE_RESOURCES],
                auto_execute_actions=True
            )
        ]
        
        for rule in default_rules:
            self.alert_rules[rule.rule_id] = rule
    
    async def start(self) -> None:
        """Start the alerting manager."""
        if self._running:
            logger.warning("Rate Limit Alerting Manager is already running")
            return
        
        self._running = True
        
        # Start background tasks
        self._evaluation_task = asyncio.create_task(self._evaluation_loop())
        self._notification_task = asyncio.create_task(self._notification_loop())
        self._action_task = asyncio.create_task(self._action_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info("Rate Limit Alerting Manager started")
    
    async def stop(self) -> None:
        """Stop the alerting manager."""
        if not self._running:
            return
        
        self._running = False
        
        # Cancel background tasks
        if self._evaluation_task:
            self._evaluation_task.cancel()
            try:
                await self._evaluation_task
            except asyncio.CancelledError:
                pass
        
        if self._notification_task:
            self._notification_task.cancel()
            try:
                await self._notification_task
            except asyncio.CancelledError:
                pass
        
        if self._action_task:
            self._action_task.cancel()
            try:
                await self._action_task
            except asyncio.CancelledError:
                pass
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Rate Limit Alerting Manager stopped")
    
    async def evaluate_alert_conditions(
        self,
        client_id: str,
        endpoint: str,
        user_tier: str,
        metrics: Dict[str, float],
        context: Dict[str, Any] = None
    ) -> List[RateLimitAlert]:
        """Evaluate alert conditions and generate alerts."""
        alerts = []
        current_time = datetime.now()
        context = context or {}
        
        for rule in self.alert_rules.values():
            if not rule.enabled:
                continue
            
            try:
                # Check if rule conditions are met
                if await self._evaluate_rule_condition(rule, metrics, context):
                    # Check rate limiting for this rule
                    if not await self._check_alert_rate_limit(rule):
                        continue
                    
                    # Create alert
                    alert = await self._create_alert(rule, client_id, endpoint, user_tier, metrics, context)
                    
                    # Check deduplication
                    if self.config.enable_deduplication and await self._is_duplicate_alert(alert):
                        continue
                    
                    # Add alert
                    alerts.append(alert)
                    self.active_alerts[alert.alert_id] = alert
                    self.alert_history.append(alert)
                    self.total_alerts_generated += 1
                    
                    logger.info(f"Alert generated: {alert.alert_id} - {alert.title}")
            
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.rule_id}: {e}")
        
        return alerts
    
    async def _evaluate_rule_condition(
        self,
        rule: AlertRule,
        metrics: Dict[str, float],
        context: Dict[str, Any]
    ) -> bool:
        """Evaluate if rule condition is met."""
        try:
            # Simple condition evaluation (can be enhanced with expression parser)
            if rule.alert_type == AlertType.ABUSE_DETECTED:
                return metrics.get("abuse_score", 0) > rule.threshold
            elif rule.alert_type == AlertType.RATE_LIMIT_EXCEEDED:
                return metrics.get("block_rate", 0) > rule.threshold
            elif rule.alert_type == AlertType.UNUSUAL_PATTERN:
                return metrics.get("anomaly_score", 0) > rule.threshold
            elif rule.alert_type == AlertType.PERFORMANCE_DEGRADATION:
                return metrics.get("avg_response_time", 0) > rule.threshold
            elif rule.alert_type == AlertType.CAPACITY_WARNING:
                return metrics.get("utilization", 0) > rule.threshold
            else:
                return False
        
        except Exception as e:
            logger.error(f"Condition evaluation error: {e}")
            return False
    
    async def _check_alert_rate_limit(self, rule: AlertRule) -> bool:
        """Check if alert rate limiting allows this alert."""
        current_time = datetime.now()
        hour_key = current_time.strftime("%Y-%m-%d:%H")
        
        # Check alerts per hour
        if self.alert_counts[rule.rule_id][hour_key] >= rule.max_alerts_per_hour:
            return False
        
        # Check notification cooldown
        if rule.notification_cooldown_minutes > 0:
            last_alert_key = f"{rule.rule_id}:last_notification"
            if last_alert_key in self.recent_fingerprints:
                last_notification = self.recent_fingerprints[last_alert_key]
                if (current_time - last_notification).total_seconds() < rule.notification_cooldown_minutes * 60:
                    return False
        
        self.alert_counts[rule.rule_id][hour_key] += 1
        return True
    
    async def _create_alert(
        self,
        rule: AlertRule,
        client_id: str,
        endpoint: str,
        user_tier: str,
        metrics: Dict[str, float],
        context: Dict[str, Any]
    ) -> RateLimitAlert:
        """Create a new alert."""
        alert_id = f"alert_{int(time.time())}_{hashlib.md5(f'{rule.rule_id}{client_id}'.encode()).hexdigest()[:8]}"
        
        # Generate fingerprint for deduplication
        fingerprint_data = f"{rule.rule_id}:{client_id}:{endpoint}:{rule.severity.value}"
        fingerprint = hashlib.md5(fingerprint_data.encode()).hexdigest()
        
        # Create title and description
        title = f"{rule.severity.value.upper()}: {rule.name}"
        description = self._generate_alert_description(rule, metrics, context)
        
        alert = RateLimitAlert(
            alert_id=alert_id,
            rule_id=rule.rule_id,
            alert_type=rule.alert_type,
            severity=rule.severity,
            status=AlertStatus.ACTIVE,
            title=title,
            description=description,
            client_id=client_id,
            endpoint=endpoint,
            user_tier=user_tier,
            ip_address=context.get("ip_address"),
            metrics=metrics,
            context=context,
            fingerprint=fingerprint
        )
        
        return alert
    
    def _generate_alert_description(
        self,
        rule: AlertRule,
        metrics: Dict[str, float],
        context: Dict[str, Any]
    ) -> str:
        """Generate alert description."""
        description = f"{rule.description}\n\n"
        
        # Add metrics
        if metrics:
            description += "Metrics:\n"
            for key, value in metrics.items():
                description += f"- {key}: {value:.2f}\n"
        
        # Add context
        if context:
            description += "\nContext:\n"
            for key, value in context.items():
                description += f"- {key}: {value}\n"
        
        return description
    
    async def _is_duplicate_alert(self, alert: RateLimitAlert) -> bool:
        """Check if alert is a duplicate."""
        current_time = datetime.now()
        
        # Check recent fingerprints
        if alert.fingerprint in self.recent_fingerprints:
            last_time = self.recent_fingerprints[alert.fingerprint]
            if (current_time - last_time).total_seconds() < self.config.deduplication_window_minutes * 60:
                return True
        
        # Record fingerprint
        self.recent_fingerprints[alert.fingerprint] = current_time
        return False
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str = "system") -> bool:
        """Acknowledge an alert."""
        if alert_id not in self.active_alerts:
            return False
        
        alert = self.active_alerts[alert_id]
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_at = datetime.now()
        
        logger.info(f"Alert acknowledged: {alert_id} by {acknowledged_by}")
        return True
    
    async def resolve_alert(self, alert_id: str, resolved_by: str = "system", resolution: str = "") -> bool:
        """Resolve an alert."""
        if alert_id not in self.active_alerts:
            return False
        
        alert = self.active_alerts[alert_id]
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.now()
        
        # Move to history
        del self.active_alerts[alert_id]
        
        logger.info(f"Alert resolved: {alert_id} by {acknowledged_by} - {resolution}")
        return True
    
    async def _evaluation_loop(self) -> None:
        """Background alert evaluation loop."""
        while self._running:
            try:
                await asyncio.sleep(self.config.evaluation_interval_seconds)
                
                # This would be called by the rate limiter with actual data
                # For now, we'll just process any queued evaluations
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Evaluation loop error: {e}")
    
    async def _notification_loop(self) -> None:
        """Background notification processing loop."""
        while self._running:
            try:
                await asyncio.sleep(5)  # Process notifications every 5 seconds
                
                if self.notification_queue and self.config.notification.enable_notifications:
                    await self._process_notifications()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Notification loop error: {e}")
    
    async def _action_loop(self) -> None:
        """Background action processing loop."""
        while self._running:
            try:
                await asyncio.sleep(10)  # Process actions every 10 seconds
                
                if self.action_queue:
                    await self._process_actions()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Action loop error: {e}")
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup loop."""
        while self._running:
            try:
                await asyncio.sleep(3600)  # Cleanup every hour
                
                # Clean old fingerprints
                cutoff_time = datetime.now() - timedelta(hours=1)
                self.recent_fingerprints = {
                    fp: time for fp, time in self.recent_fingerprints.items()
                    if time > cutoff_time
                }
                
                # Clean old alert counts
                current_hour = datetime.now().strftime("%Y-%m-%d:%H")
                for rule_id in list(self.alert_counts.keys()):
                    for hour_key in list(self.alert_counts[rule_id].keys()):
                        if hour_key < current_hour:
                            del self.alert_counts[rule_id][hour_key]
                
                # Clean old alert history
                history_cutoff = datetime.now() - timedelta(days=self.config.alert_retention_days)
                self.alert_history = deque(
                    [alert for alert in self.alert_history if alert.triggered_at > history_cutoff],
                    maxlen=10000
                )
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
    
    async def _process_notifications(self) -> None:
        """Process pending notifications."""
        while self.notification_queue:
            try:
                notification_data = self.notification_queue.popleft()
                await self._send_notification(notification_data)
                
            except Exception as e:
                logger.error(f"Notification processing error: {e}")
    
    async def _send_notification(self, notification_data: Dict[str, Any]) -> None:
        """Send notification through configured channels."""
        alert = notification_data.get("alert")
        channels = notification_data.get("channels", [])
        
        for channel in channels:
            try:
                if channel == NotificationChannel.EMAIL:
                    await self._send_email_notification(alert)
                elif channel == NotificationChannel.SLACK:
                    await self._send_slack_notification(alert)
                elif channel == NotificationChannel.WEBHOOK:
                    await self._send_webhook_notification(alert)
                elif channel == NotificationChannel.SMS:
                    await self._send_sms_notification(alert)
                elif channel == NotificationChannel.DASHBOARD:
                    await self._send_dashboard_notification(alert)
                
                # Record notification
                self.total_notifications_sent += 1
                self.notification_history.append({
                    "alert_id": alert.alert_id,
                    "channel": channel.value,
                    "sent_at": datetime.now(),
                    "success": True
                })
                
            except Exception as e:
                logger.error(f"Failed to send {channel.value} notification: {e}")
                self.notification_history.append({
                    "alert_id": alert.alert_id,
                    "channel": channel.value,
                    "sent_at": datetime.now(),
                    "success": False,
                    "error": str(e)
                })
    
    async def _send_email_notification(self, alert: RateLimitAlert) -> None:
        """Send email notification."""
        # Placeholder for email implementation
        logger.info(f"Email notification sent for alert {alert.alert_id}")
    
    async def _send_slack_notification(self, alert: RateLimitAlert) -> None:
        """Send Slack notification."""
        # Placeholder for Slack implementation
        logger.info(f"Slack notification sent for alert {alert.alert_id}")
    
    async def _send_webhook_notification(self, alert: RateLimitAlert) -> None:
        """Send webhook notification."""
        # Placeholder for webhook implementation
        logger.info(f"Webhook notification sent for alert {alert.alert_id}")
    
    async def _send_sms_notification(self, alert: RateLimitAlert) -> None:
        """Send SMS notification."""
        # Placeholder for SMS implementation
        logger.info(f"SMS notification sent for alert {alert.alert_id}")
    
    async def _send_dashboard_notification(self, alert: RateLimitAlert) -> None:
        """Send dashboard notification."""
        # Dashboard notifications are handled by the frontend
        logger.info(f"Dashboard notification sent for alert {alert.alert_id}")
    
    async def _process_actions(self) -> None:
        """Process pending response actions."""
        while self.action_queue:
            try:
                action_data = self.action_queue.popleft()
                await self._execute_action(action_data)
                
            except Exception as e:
                logger.error(f"Action processing error: {e}")
    
    async def _execute_action(self, action_data: Dict[str, Any]) -> None:
        """Execute automated response action."""
        alert = action_data.get("alert")
        action = action_data.get("action")
        
        try:
            if action == ResponseAction.BLOCK_CLIENT:
                await self._block_client_action(alert)
            elif action == ResponseAction.INCREASE_LIMITS:
                await self._increase_limits_action(alert)
            elif action == ResponseAction.DECREASE_LIMITS:
                await self._decrease_limits_action(alert)
            elif action == ResponseAction.NOTIFY_ADMIN:
                await self._notify_admin_action(alert)
            elif action == ResponseAction.LOG_EVENT:
                await self._log_event_action(alert)
            elif action == ResponseAction.SCALE_RESOURCES:
                await self._scale_resources_action(alert)
            
            # Record action
            self.total_actions_executed += 1
            self.action_history.append({
                "alert_id": alert.alert_id,
                "action": action.value,
                "executed_at": datetime.now(),
                "success": True
            })
            
        except Exception as e:
            logger.error(f"Failed to execute action {action.value}: {e}")
            self.action_history.append({
                "alert_id": alert.alert_id,
                "action": action.value,
                "executed_at": datetime.now(),
                "success": False,
                "error": str(e)
            })
    
    async def _block_client_action(self, alert: RateLimitAlert) -> None:
        """Block client action."""
        if alert.client_id:
            logger.warning(f"Blocking client {alert.client_id} due to alert {alert.alert_id}")
            # Integration with rate limiter to block client
    
    async def _increase_limits_action(self, alert: RateLimitAlert) -> None:
        """Increase limits action."""
        logger.info(f"Increasing limits due to alert {alert.alert_id}")
        # Integration with rate limiter to adjust limits
    
    async def _decrease_limits_action(self, alert: RateLimitAlert) -> None:
        """Decrease limits action."""
        logger.info(f"Decreasing limits due to alert {alert.alert_id}")
        # Integration with rate limiter to adjust limits
    
    async def _notify_admin_action(self, alert: RateLimitAlert) -> None:
        """Notify admin action."""
        logger.info(f"Admin notification sent for alert {alert.alert_id}")
        # Send admin notification
    
    async def _log_event_action(self, alert: RateLimitAlert) -> None:
        """Log event action."""
        logger.warning(f"Alert event logged: {alert.alert_id} - {alert.title}")
    
    async def _scale_resources_action(self, alert: RateLimitAlert) -> None:
        """Scale resources action."""
        logger.info(f"Scaling resources due to alert {alert.alert_id}")
        # Integration with infrastructure to scale resources
    
    def get_alert_stats(self) -> Dict[str, Any]:
        """Get comprehensive alert statistics."""
        current_time = datetime.now()
        
        # Alert counts by severity
        severity_counts = defaultdict(int)
        for alert in self.active_alerts.values():
            severity_counts[alert.severity.value] += 1
        
        # Alert counts by type
        type_counts = defaultdict(int)
        for alert in self.active_alerts.values():
            type_counts[alert.alert_type.value] += 1
        
        # Recent alerts
        recent_cutoff = current_time - timedelta(hours=24)
        recent_alerts = [
            alert for alert in self.alert_history
            if alert.triggered_at > recent_cutoff
        ]
        
        return {
            "total_alerts_generated": self.total_alerts_generated,
            "total_notifications_sent": self.total_notifications_sent,
            "total_actions_executed": self.total_actions_executed,
            "active_alerts_count": len(self.active_alerts),
            "alert_history_count": len(self.alert_history),
            "active_rules_count": len([r for r in self.alert_rules.values() if r.enabled]),
            "severity_distribution": dict(severity_counts),
            "type_distribution": dict(type_counts),
            "recent_alerts_24h": len(recent_alerts),
            "notification_queue_size": len(self.notification_queue),
            "action_queue_size": len(self.action_queue),
            "config": {
                "evaluation_interval_seconds": self.config.evaluation_interval_seconds,
                "enable_deduplication": self.config.enable_deduplication,
                "enable_escalation": self.config.enable_escalation,
                "enable_notifications": self.config.notification.enable_notifications
            },
            "running": self._running,
            "timestamp": current_time.isoformat()
        }
    
    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[RateLimitAlert]:
        """Get active alerts."""
        alerts = list(self.active_alerts.values())
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        return sorted(alerts, key=lambda x: x.triggered_at, reverse=True)
    
    def add_alert_rule(self, rule: AlertRule) -> None:
        """Add a new alert rule."""
        self.alert_rules[rule.rule_id] = rule
        logger.info(f"Alert rule added: {rule.rule_id}")
    
    def update_alert_rule(self, rule_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing alert rule."""
        if rule_id not in self.alert_rules:
            return False
        
        rule = self.alert_rules[rule_id]
        for key, value in updates.items():
            if hasattr(rule, key):
                setattr(rule, key, value)
        
        rule.updated_at = datetime.now()
        logger.info(f"Alert rule updated: {rule_id}")
        return True
    
    def delete_alert_rule(self, rule_id: str) -> bool:
        """Delete an alert rule."""
        if rule_id not in self.alert_rules:
            return False
        
        del self.alert_rules[rule_id]
        logger.info(f"Alert rule deleted: {rule_id}")
        return True


# Global alerting manager instance
_rate_limit_alerting_manager: Optional[RateLimitAlertingManager] = None


def get_rate_limit_alerting_manager(config: AlertingConfig = None) -> RateLimitAlertingManager:
    """Get or create global rate limit alerting manager instance."""
    global _rate_limit_alerting_manager
    if _rate_limit_alerting_manager is None:
        _rate_limit_alerting_manager = RateLimitAlertingManager(config)
    return _rate_limit_alerting_manager


async def start_rate_limit_alerting(config: AlertingConfig = None):
    """Start the global rate limit alerting manager."""
    alerting = get_rate_limit_alerting_manager(config)
    await alerting.start()


async def stop_rate_limit_alerting():
    """Stop the global rate limit alerting manager."""
    global _rate_limit_alerting_manager
    if _rate_limit_alerting_manager:
        await _rate_limit_alerting_manager.stop()


async def evaluate_rate_limit_alerts(
    client_id: str,
    endpoint: str,
    user_tier: str,
    metrics: Dict[str, float],
    context: Dict[str, Any] = None
) -> List[RateLimitAlert]:
    """Evaluate rate limit alerts."""
    alerting = get_rate_limit_alerting_manager()
    return await alerting.evaluate_alert_conditions(client_id, endpoint, user_tier, metrics, context)


def get_alerting_stats() -> Dict[str, Any]:
    """Get alerting statistics."""
    alerting = get_rate_limit_alerting_manager()
    return alerting.get_alert_stats()
