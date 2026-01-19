"""
Security Monitoring with Real-Time Alerts
Provides comprehensive security monitoring, threat detection, and real-time alerting system.
"""

import asyncio
import json
import logging
import smtplib
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable
from collections import defaultdict, deque
import statistics
import hashlib
import base64

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert status values."""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


class AlertType(Enum):
    """Types of security alerts."""
    THREAT_DETECTED = "threat_detected"
    ANOMALY_DETECTED = "anomaly_detected"
    VULNERABILITY_FOUND = "vulnerability_found"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SYSTEM_COMPROMISE = "system_compromise"
    DATA_BREACH = "data_breach"
    POLICY_VIOLATION = "policy_violation"
    PERFORMANCE_ISSUE = "performance_issue"
    AVAILABILITY_ISSUE = "availability_issue"


class NotificationChannel(Enum):
    """Alert notification channels."""
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    WEBHOOK = "webhook"
    PAGERDUTY = "pagerduty"
    TEAMS = "teams"
    DISCORD = "discord"


@dataclass
class SecurityAlert:
    """Security alert definition."""
    id: str
    title: str
    description: str
    alert_type: AlertType
    severity: AlertSeverity
    status: AlertStatus
    source: str
    user_id: Optional[str]
    session_id: Optional[str]
    client_ip: Optional[str]
    endpoint: Optional[str]
    details: Dict[str, Any]
    evidence: Dict[str, Any]
    first_seen: datetime
    last_seen: datetime
    count: int
    acknowledged_by: Optional[str]
    acknowledged_at: Optional[datetime]
    resolved_by: Optional[str]
    resolved_at: Optional[datetime]
    tags: Set[str]
    correlation_id: Optional[str]


@dataclass
class AlertRule:
    """Alert rule definition."""
    id: str
    name: str
    description: str
    alert_type: AlertType
    severity: AlertSeverity
    enabled: bool
    conditions: Dict[str, Any]
    threshold: float
    time_window_minutes: int
    cooldown_minutes: int
    notification_channels: List[NotificationChannel]
    suppression_rules: List[Dict[str, Any]]
    escalation_rules: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime


@dataclass
class NotificationConfig:
    """Notification configuration."""
    channel: NotificationChannel
    enabled: bool
    config: Dict[str, Any]
    rate_limit_per_hour: int
    last_sent: Optional[datetime]
    send_count: int


class SecurityMonitoringSystem:
    """Comprehensive security monitoring and alerting system."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        
        # Storage
        self.alerts: Dict[str, SecurityAlert] = {}
        self.alert_rules: Dict[str, AlertRule] = {}
        self.notification_configs: Dict[NotificationChannel, NotificationConfig] = {}
        
        # Alert processing
        self.alert_queue: asyncio.Queue = asyncio.Queue()
        self.alert_history: deque = deque(maxlen=10000)
        self.active_correlations: Dict[str, List[str]] = defaultdict(list)
        
        # Monitoring state
        self.metrics_collector = defaultdict(list)
        self.threat_indicators = defaultdict(int)
        self.anomaly_scores = defaultdict(float)
        
        # Background tasks
        self._monitoring_task = None
        self._alert_processing_task = None
        self._cleanup_task = None
        
        # Initialize default rules and notifications
        self._initialize_default_rules()
        self._initialize_notification_configs()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration."""
        return {
            "alert_retention_days": 30,
            "max_alerts_per_minute": 100,
            "correlation_window_minutes": 15,
            "enable_real_time_monitoring": True,
            "enable_threat_intelligence": True,
            "enable_anomaly_detection": True,
            "default_cooldown_minutes": 5,
            "max_correlation_group_size": 10,
            "alert_deduplication_window_minutes": 10,
        }
    
    def _initialize_default_rules(self):
        """Initialize default alert rules."""
        default_rules = [
            AlertRule(
                id="failed_auth_threshold",
                name="Failed Authentication Threshold",
                description="Alert when failed authentication attempts exceed threshold",
                alert_type=AlertType.UNAUTHORIZED_ACCESS,
                severity=AlertSeverity.HIGH,
                enabled=True,
                conditions={
                    "event_type": "authentication_failure",
                    "field": "count",
                    "operator": ">",
                },
                threshold=5.0,
                time_window_minutes=5,
                cooldown_minutes=15,
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK],
                suppression_rules=[],
                escalation_rules=[
                    {
                        "condition": "count > 20",
                        "severity": AlertSeverity.CRITICAL,
                        "channels": [NotificationChannel.SMS, NotificationChannel.PAGERDUTY],
                    }
                ],
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            AlertRule(
                id="rate_limit_exceeded",
                name="Rate Limiting Threshold",
                description="Alert when rate limiting is frequently triggered",
                alert_type=AlertType.RATE_LIMIT_EXCEEDED,
                severity=AlertSeverity.MEDIUM,
                enabled=True,
                conditions={
                    "event_type": "rate_limit_triggered",
                    "field": "count",
                    "operator": ">",
                },
                threshold=10.0,
                time_window_minutes=1,
                cooldown_minutes=5,
                notification_channels=[NotificationChannel.EMAIL],
                suppression_rules=[],
                escalation_rules=[],
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            AlertRule(
                id="critical_vulnerability",
                name="Critical Vulnerability Detected",
                description="Alert when critical vulnerability is found",
                alert_type=AlertType.VULNERABILITY_FOUND,
                severity=AlertSeverity.CRITICAL,
                enabled=True,
                conditions={
                    "event_type": "vulnerability_found",
                    "field": "severity",
                    "operator": "==",
                },
                threshold=1.0,  # Critical severity
                time_window_minutes=1,
                cooldown_minutes=30,
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SMS, NotificationChannel.SLACK],
                suppression_rules=[],
                escalation_rules=[],
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            AlertRule(
                id="anomaly_detected",
                name="Behavioral Anomaly Detected",
                description="Alert when behavioral anomaly is detected",
                alert_type=AlertType.ANOMALY_DETECTED,
                severity=AlertSeverity.MEDIUM,
                enabled=True,
                conditions={
                    "event_type": "behavioral_anomaly",
                    "field": "anomaly_score",
                    "operator": ">",
                },
                threshold=0.8,
                time_window_minutes=5,
                cooldown_minutes=10,
                notification_channels=[NotificationChannel.EMAIL],
                suppression_rules=[],
                escalation_rules=[
                    {
                        "condition": "anomaly_score > 0.9",
                        "severity": AlertSeverity.HIGH,
                        "channels": [NotificationChannel.SLACK],
                    }
                ],
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
        ]
        
        for rule in default_rules:
            self.alert_rules[rule.id] = rule
    
    def _initialize_notification_configs(self):
        """Initialize notification configurations."""
        self.notification_configs = {
            NotificationChannel.EMAIL: NotificationConfig(
                channel=NotificationChannel.EMAIL,
                enabled=True,
                config={
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "username": "alerts@raptorflow.com",
                    "password": "app_password",
                    "from_address": "alerts@raptorflow.com",
                    "to_addresses": ["security@raptorflow.com"],
                },
                rate_limit_per_hour=50,
                last_sent=None,
                send_count=0,
            ),
            NotificationChannel.SLACK: NotificationConfig(
                channel=NotificationChannel.SLACK,
                enabled=True,
                config={
                    "webhook_url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
                    "channel": "#security-alerts",
                    "username": "SecurityBot",
                },
                rate_limit_per_hour=100,
                last_sent=None,
                send_count=0,
            ),
            NotificationChannel.SMS: NotificationConfig(
                channel=NotificationChannel.SMS,
                enabled=False,
                config={
                    "provider": "twilio",
                    "account_sid": "your_account_sid",
                    "auth_token": "your_auth_token",
                    "from_number": "+1234567890",
                    "to_numbers": ["+0987654321"],
                },
                rate_limit_per_hour=20,
                last_sent=None,
                send_count=0,
            ),
            NotificationChannel.WEBHOOK: NotificationConfig(
                channel=NotificationChannel.WEBHOOK,
                enabled=True,
                config={
                    "url": "https://your-webhook-endpoint.com/alerts",
                    "method": "POST",
                    "headers": {"Authorization": "Bearer your_webhook_token"},
                },
                rate_limit_per_hour=200,
                last_sent=None,
                send_count=0,
            ),
        }
    
    async def start_monitoring(self):
        """Start security monitoring."""
        logger.info("Starting security monitoring system")
        
        # Start background tasks
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        self._alert_processing_task = asyncio.create_task(self._alert_processing_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def stop_monitoring(self):
        """Stop security monitoring."""
        logger.info("Stopping security monitoring system")
        
        # Cancel background tasks
        if self._monitoring_task:
            self._monitoring_task.cancel()
        if self._alert_processing_task:
            self._alert_processing_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while True:
            try:
                # Collect metrics
                await self._collect_security_metrics()
                
                # Analyze for threats
                await self._analyze_threats()
                
                # Check alert rules
                await self._evaluate_alert_rules()
                
                # Sleep for monitoring interval
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)
    
    async def _alert_processing_loop(self):
        """Alert processing loop."""
        while True:
            try:
                # Get alert from queue
                alert = await asyncio.wait_for(self.alert_queue.get(), timeout=1.0)
                
                # Process alert
                await self._process_alert(alert)
                
                # Mark task as done
                self.alert_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in alert processing loop: {e}")
    
    async def _cleanup_loop(self):
        """Cleanup loop for old data."""
        while True:
            try:
                # Clean up old alerts
                await self._cleanup_old_alerts()
                
                # Reset notification rate limits
                await self._reset_notification_rate_limits()
                
                # Sleep for cleanup interval
                await asyncio.sleep(3600)  # Run every hour
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(300)
    
    async def collect_security_event(self, event: Dict[str, Any]):
        """Collect security event for monitoring."""
        # Add timestamp if not present
        if "timestamp" not in event:
            event["timestamp"] = datetime.now()
        
        # Store in metrics collector
        event_type = event.get("event_type", "unknown")
        self.metrics_collector[event_type].append(event)
        
        # Keep only recent events
        if len(self.metrics_collector[event_type]) > 1000:
            self.metrics_collector[event_type] = self.metrics_collector[event_type][-500:]
        
        # Update threat indicators
        await self._update_threat_indicators(event)
        
        # Update anomaly scores
        await self._update_anomaly_scores(event)
    
    async def _collect_security_metrics(self):
        """Collect security metrics from various sources."""
        current_time = datetime.now()
        
        # Collect from different sources
        metrics = {
            "timestamp": current_time,
            "failed_auth_count": await self._count_failed_auth(),
            "rate_limit_triggers": await self._count_rate_limit_triggers(),
            "vulnerabilities_found": await self._count_vulnerabilities(),
            "anomaly_count": await self._count_anomalies(),
            "active_sessions": await self._count_active_sessions(),
            "blocked_ips": await self._count_blocked_ips(),
        }
        
        # Store metrics
        self.metrics_collector["security_metrics"].append(metrics)
    
    async def _count_failed_auth(self) -> int:
        """Count failed authentication attempts."""
        if "authentication_failure" not in self.metrics_collector:
            return 0
        
        recent_events = [
            event for event in self.metrics_collector["authentication_failure"]
            if (datetime.now() - event["timestamp"]).total_seconds() < 300  # Last 5 minutes
        ]
        
        return len(recent_events)
    
    async def _count_rate_limit_triggers(self) -> int:
        """Count rate limit triggers."""
        if "rate_limit_triggered" not in self.metrics_collector:
            return 0
        
        recent_events = [
            event for event in self.metrics_collector["rate_limit_triggered"]
            if (datetime.now() - event["timestamp"]).total_seconds() < 60  # Last minute
        ]
        
        return len(recent_events)
    
    async def _count_vulnerabilities(self) -> int:
        """Count vulnerabilities found."""
        if "vulnerability_found" not in self.metrics_collector:
            return 0
        
        recent_events = [
            event for event in self.metrics_collector["vulnerability_found"]
            if (datetime.now() - event["timestamp"]).total_seconds() < 3600  # Last hour
        ]
        
        return len(recent_events)
    
    async def _count_anomalies(self) -> int:
        """Count behavioral anomalies."""
        if "behavioral_anomaly" not in self.metrics_collector:
            return 0
        
        recent_events = [
            event for event in self.metrics_collector["behavioral_anomaly"]
            if (datetime.now() - event["timestamp"]).total_seconds() < 300  # Last 5 minutes
        ]
        
        return len(recent_events)
    
    async def _count_active_sessions(self) -> int:
        """Count active sessions."""
        # This would integrate with session management system
        return 0  # Placeholder
    
    async def _count_blocked_ips(self) -> int:
        """Count blocked IPs."""
        # This would integrate with security system
        return 0  # Placeholder
    
    async def _update_threat_indicators(self, event: Dict[str, Any]):
        """Update threat indicators based on event."""
        event_type = event.get("event_type", "unknown")
        
        # Update threat indicators
        if event_type in ["authentication_failure", "unauthorized_access", "suspicious_activity"]:
            client_ip = event.get("client_ip")
            if client_ip:
                self.threat_indicators[f"ip:{client_ip}"] += 1
        
        user_id = event.get("user_id")
        if user_id and event_type in ["authentication_failure", "policy_violation"]:
            self.threat_indicators[f"user:{user_id}"] += 1
    
    async def _update_anomaly_scores(self, event: Dict[str, Any]):
        """Update anomaly scores based on event."""
        user_id = event.get("user_id")
        if not user_id:
            return
        
        event_type = event.get("event_type", "unknown")
        
        # Update anomaly score based on event type
        if event_type == "behavioral_anomaly":
            anomaly_score = event.get("anomaly_score", 0.5)
            self.anomaly_scores[user_id] = (self.anomaly_scores[user_id] * 0.7) + (anomaly_score * 0.3)
        elif event_type in ["authentication_failure", "unauthorized_access"]:
            self.anomaly_scores[user_id] = min(self.anomaly_scores[user_id] + 0.1, 1.0)
        else:
            # Decay anomaly score for normal events
            self.anomaly_scores[user_id] = max(self.anomaly_scores[user_id] * 0.95, 0.0)
    
    async def _analyze_threats(self):
        """Analyze collected data for threats."""
        # Analyze threat indicators
        for indicator, count in self.threat_indicators.items():
            if count > 10:  # Threshold for threat indicator
                await self._create_threat_alert(indicator, count)
        
        # Analyze anomaly scores
        for user_id, score in self.anomaly_scores.items():
            if score > 0.8:  # High anomaly threshold
                await self._create_anomaly_alert(user_id, score)
    
    async def _create_threat_alert(self, indicator: str, count: int):
        """Create threat alert."""
        alert_id = f"threat_{indicator}_{int(time.time())}"
        
        alert = SecurityAlert(
            id=alert_id,
            title=f"Threat Indicator: {indicator}",
            description=f"Threat indicator {indicator} detected {count} times",
            alert_type=AlertType.THREAT_DETECTED,
            severity=AlertSeverity.HIGH if count > 20 else AlertSeverity.MEDIUM,
            status=AlertStatus.ACTIVE,
            source="threat_monitoring",
            user_id=None,
            session_id=None,
            client_ip=indicator.split(":")[1] if indicator.startswith("ip:") else None,
            endpoint=None,
            details={"indicator": indicator, "count": count},
            evidence={"threat_intelligence": True},
            first_seen=datetime.now(),
            last_seen=datetime.now(),
            count=count,
            acknowledged_by=None,
            acknowledged_at=None,
            resolved_by=None,
            resolved_at=None,
            tags={"threat", "indicator"},
            correlation_id=None,
        )
        
        await self._queue_alert(alert)
    
    async def _create_anomaly_alert(self, user_id: str, score: float):
        """Create anomaly alert."""
        alert_id = f"anomaly_{user_id}_{int(time.time())}"
        
        alert = SecurityAlert(
            id=alert_id,
            title=f"Behavioral Anomaly: {user_id}",
            description=f"Behavioral anomaly detected for user {user_id} with score {score:.2f}",
            alert_type=AlertType.ANOMALY_DETECTED,
            severity=AlertSeverity.HIGH if score > 0.9 else AlertSeverity.MEDIUM,
            status=AlertStatus.ACTIVE,
            source="behavioral_analysis",
            user_id=user_id,
            session_id=None,
            client_ip=None,
            endpoint=None,
            details={"user_id": user_id, "anomaly_score": score},
            evidence={"behavioral_analysis": True},
            first_seen=datetime.now(),
            last_seen=datetime.now(),
            count=1,
            acknowledged_by=None,
            acknowledged_at=None,
            resolved_by=None,
            resolved_at=None,
            tags={"anomaly", "behavioral"},
            correlation_id=None,
        )
        
        await self._queue_alert(alert)
    
    async def _evaluate_alert_rules(self):
        """Evaluate alert rules against collected metrics."""
        current_time = datetime.now()
        
        for rule in self.alert_rules.values():
            if not rule.enabled:
                continue
            
            # Check cooldown
            if self._is_rule_in_cooldown(rule, current_time):
                continue
            
            # Evaluate rule conditions
            should_alert = await self._evaluate_rule_conditions(rule)
            
            if should_alert:
                await self._create_rule_alert(rule)
    
    def _is_rule_in_cooldown(self, rule: AlertRule, current_time: datetime) -> bool:
        """Check if rule is in cooldown period."""
        # Check if similar alert was recently created
        recent_alerts = [
            alert for alert in self.alerts.values()
            if (alert.alert_type == rule.alert_type and
                alert.status == AlertStatus.ACTIVE and
                (current_time - alert.first_seen).total_seconds() < rule.cooldown_minutes * 60)
        ]
        
        return len(recent_alerts) > 0
    
    async def _evaluate_rule_conditions(self, rule: AlertRule) -> bool:
        """Evaluate rule conditions."""
        event_type = rule.conditions.get("event_type")
        field = rule.conditions.get("field")
        operator = rule.conditions.get("operator")
        
        if not all([event_type, field, operator]):
            return False
        
        # Get relevant events
        if event_type not in self.metrics_collector:
            return False
        
        # Filter events by time window
        cutoff_time = datetime.now() - timedelta(minutes=rule.time_window_minutes)
        recent_events = [
            event for event in self.metrics_collector[event_type]
            if event["timestamp"] >= cutoff_time
        ]
        
        if not recent_events:
            return False
        
        # Evaluate condition
        if field == "count":
            value = len(recent_events)
        elif field == "severity":
            # For vulnerabilities, check if any critical ones
            value = 1.0 if any(event.get("severity") == "critical" for event in recent_events) else 0.0
        elif field == "anomaly_score":
            # For anomalies, get maximum score
            value = max([event.get("anomaly_score", 0.0) for event in recent_events], default=0.0)
        else:
            return False
        
        # Compare with threshold
        if operator == ">":
            return value > rule.threshold
        elif operator == ">=":
            return value >= rule.threshold
        elif operator == "==":
            return value == rule.threshold
        elif operator == "<":
            return value < rule.threshold
        elif operator == "<=":
            return value <= rule.threshold
        
        return False
    
    async def _create_rule_alert(self, rule: AlertRule):
        """Create alert from rule."""
        alert_id = f"rule_{rule.id}_{int(time.time())}"
        
        alert = SecurityAlert(
            id=alert_id,
            title=rule.name,
            description=rule.description,
            alert_type=rule.alert_type,
            severity=rule.severity,
            status=AlertStatus.ACTIVE,
            source="alert_rule",
            user_id=None,
            session_id=None,
            client_ip=None,
            endpoint=None,
            details={"rule_id": rule.id, "threshold": rule.threshold},
            evidence={"rule_evaluation": True},
            first_seen=datetime.now(),
            last_seen=datetime.now(),
            count=1,
            acknowledged_by=None,
            acknowledged_at=None,
            resolved_by=None,
            resolved_at=None,
            tags={"rule", "automated"},
            correlation_id=None,
        )
        
        await self._queue_alert(alert)
    
    async def _queue_alert(self, alert: SecurityAlert):
        """Queue alert for processing."""
        # Check for deduplication
        if await self._is_duplicate_alert(alert):
            return
        
        # Add to alerts storage
        self.alerts[alert.id] = alert
        self.alert_history.append(alert)
        
        # Add to processing queue
        await self.alert_queue.put(alert)
        
        logger.info(f"Alert queued: {alert.title} ({alert.severity.value})")
    
    async def _is_duplicate_alert(self, alert: SecurityAlert) -> bool:
        """Check if alert is duplicate."""
        # Check for similar alerts in deduplication window
        cutoff_time = datetime.now() - timedelta(minutes=self.config["alert_deduplication_window_minutes"])
        
        for existing_alert in self.alerts.values():
            if (existing_alert.alert_type == alert.alert_type and
                existing_alert.status == AlertStatus.ACTIVE and
                existing_alert.first_seen >= cutoff_time and
                existing_alert.title == alert.title):
                return True
        
        return False
    
    async def _process_alert(self, alert: SecurityAlert):
        """Process alert and send notifications."""
        try:
            # Check suppression rules
            if await self._is_alert_suppressed(alert):
                alert.status = AlertStatus.SUPPRESSED
                return
            
            # Check for escalation
            await self._check_alert_escalation(alert)
            
            # Send notifications
            await self._send_notifications(alert)
            
            # Correlate with other alerts
            await self._correlate_alert(alert)
            
        except Exception as e:
            logger.error(f"Error processing alert {alert.id}: {e}")
    
    async def _is_alert_suppressed(self, alert: SecurityAlert) -> bool:
        """Check if alert should be suppressed."""
        # Check suppression rules
        for rule in self.alert_rules.values():
            if rule.alert_type == alert.alert_type:
                for suppression_rule in rule.suppression_rules:
                    if await self._evaluate_suppression_rule(alert, suppression_rule):
                        return True
        
        return False
    
    async def _evaluate_suppression_rule(self, alert: SecurityAlert, rule: Dict[str, Any]) -> bool:
        """Evaluate suppression rule."""
        # Simple suppression logic - can be extended
        condition = rule.get("condition")
        if condition == "maintenance_window":
            # Suppress during maintenance windows
            return False  # Placeholder
        elif condition == "known_issue":
            # Suppress known issues
            return False  # Placeholder
        
        return False
    
    async def _check_alert_escalation(self, alert: SecurityAlert):
        """Check if alert should be escalated."""
        # Check escalation rules
        for rule in self.alert_rules.values():
            if rule.alert_type == alert.alert_type:
                for escalation_rule in rule.escalation_rules:
                    if await self._evaluate_escalation_rule(alert, escalation_rule):
                        # Escalate alert
                        alert.severity = escalation_rule["severity"]
                        logger.info(f"Alert {alert.id} escalated to {alert.severity.value}")
    
    async def _evaluate_escalation_rule(self, alert: SecurityAlert, rule: Dict[str, Any]) -> bool:
        """Evaluate escalation rule."""
        condition = rule.get("condition")
        
        if condition.startswith("count >"):
            threshold = int(condition.split(">")[1].strip())
            return alert.count > threshold
        elif condition.startswith("anomaly_score >"):
            threshold = float(condition.split(">")[1].strip())
            return alert.details.get("anomaly_score", 0.0) > threshold
        
        return False
    
    async def _send_notifications(self, alert: SecurityAlert):
        """Send notifications for alert."""
        # Find applicable rules
        applicable_rules = [
            rule for rule in self.alert_rules.values()
            if rule.alert_type == alert.alert_type and rule.enabled
        ]
        
        if not applicable_rules:
            return
        
        # Get notification channels from rules
        notification_channels = set()
        for rule in applicable_rules:
            notification_channels.update(rule.notification_channels)
        
        # Send notifications
        for channel in notification_channels:
            if channel in self.notification_configs:
                config = self.notification_configs[channel]
                if config.enabled and await self._check_notification_rate_limit(config):
                    await self._send_notification(channel, alert, config)
    
    async def _check_notification_rate_limit(self, config: NotificationConfig) -> bool:
        """Check notification rate limit."""
        current_time = datetime.now()
        
        # Reset counter if hour has passed
        if (config.last_sent and 
            (current_time - config.last_sent).total_seconds() > 3600):
            config.send_count = 0
        
        # Check rate limit
        if config.send_count >= config.rate_limit_per_hour:
            return False
        
        return True
    
    async def _send_notification(self, channel: NotificationChannel, alert: SecurityAlert, config: NotificationConfig):
        """Send notification through specified channel."""
        try:
            if channel == NotificationChannel.EMAIL:
                await self._send_email_notification(alert, config)
            elif channel == NotificationChannel.SLACK:
                await self._send_slack_notification(alert, config)
            elif channel == NotificationChannel.SMS:
                await self._send_sms_notification(alert, config)
            elif channel == NotificationChannel.WEBHOOK:
                await self._send_webhook_notification(alert, config)
            
            # Update rate limit tracking
            config.last_sent = datetime.now()
            config.send_count += 1
            
        except Exception as e:
            logger.error(f"Failed to send {channel.value} notification: {e}")
    
    async def _send_email_notification(self, alert: SecurityAlert, config: NotificationConfig):
        """Send email notification."""
        # This would integrate with email service
        logger.info(f"Email notification sent for alert {alert.id}")
    
    async def _send_slack_notification(self, alert: SecurityAlert, config: NotificationConfig):
        """Send Slack notification."""
        # This would integrate with Slack API
        logger.info(f"Slack notification sent for alert {alert.id}")
    
    async def _send_sms_notification(self, alert: SecurityAlert, config: NotificationConfig):
        """Send SMS notification."""
        # This would integrate with SMS provider
        logger.info(f"SMS notification sent for alert {alert.id}")
    
    async def _send_webhook_notification(self, alert: SecurityAlert, config: NotificationConfig):
        """Send webhook notification."""
        # This would send HTTP request to webhook URL
        logger.info(f"Webhook notification sent for alert {alert.id}")
    
    async def _correlate_alert(self, alert: SecurityAlert):
        """Correlate alert with other alerts."""
        # Find related alerts
        related_alerts = [
            existing_alert for existing_alert in self.alerts.values()
            if (existing_alert.id != alert.id and
                existing_alert.alert_type == alert.alert_type and
                existing_alert.status == AlertStatus.ACTIVE and
                (datetime.now() - existing_alert.first_seen).total_seconds() < self.config["correlation_window_minutes"] * 60)
        ]
        
        if related_alerts:
            # Create correlation group
            correlation_id = f"corr_{alert.alert_type.value}_{int(time.time())}"
            
            # Add to correlation group
            self.active_correlations[correlation_id].append(alert.id)
            for related_alert in related_alerts:
                self.active_correlations[correlation_id].append(related_alert.id)
            
            # Update correlation IDs
            alert.correlation_id = correlation_id
            for related_alert in related_alerts:
                related_alert.correlation_id = correlation_id
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert."""
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_by = acknowledged_by
            alert.acknowledged_at = datetime.now()
            
            logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
            return True
        
        return False
    
    async def resolve_alert(self, alert_id: str, resolved_by: str, resolution_notes: str = "") -> bool:
        """Resolve an alert."""
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            alert.status = AlertStatus.RESOLVED
            alert.resolved_by = resolved_by
            alert.resolved_at = datetime.now()
            
            if resolution_notes:
                alert.details["resolution_notes"] = resolution_notes
            
            logger.info(f"Alert {alert_id} resolved by {resolved_by}")
            return True
        
        return False
    
    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[SecurityAlert]:
        """Get active alerts."""
        active_alerts = [
            alert for alert in self.alerts.values()
            if alert.status in [AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED]
        ]
        
        if severity:
            active_alerts = [alert for alert in active_alerts if alert.severity == severity]
        
        return sorted(active_alerts, key=lambda x: x.first_seen, reverse=True)
    
    def get_alert_metrics(self) -> Dict[str, Any]:
        """Get alert metrics."""
        current_time = datetime.now()
        last_24h = current_time - timedelta(hours=24)
        
        # Filter alerts by time
        recent_alerts = [
            alert for alert in self.alerts.values()
            if alert.first_seen >= last_24h
        ]
        
        # Calculate metrics
        severity_counts = defaultdict(int)
        type_counts = defaultdict(int)
        status_counts = defaultdict(int)
        
        for alert in recent_alerts:
            severity_counts[alert.severity.value] += 1
            type_counts[alert.alert_type.value] += 1
            status_counts[alert.status.value] += 1
        
        return {
            "total_alerts": len(self.alerts),
            "active_alerts": len(self.get_active_alerts()),
            "alerts_last_24h": len(recent_alerts),
            "severity_distribution": dict(severity_counts),
            "type_distribution": dict(type_counts),
            "status_distribution": dict(status_counts),
            "correlation_groups": len(self.active_correlations),
            "threat_indicators": dict(self.threat_indicators),
            "average_anomaly_score": statistics.mean(self.anomaly_scores.values()) if self.anomaly_scores else 0.0,
        }
    
    async def _cleanup_old_alerts(self):
        """Clean up old alerts."""
        cutoff_date = datetime.now() - timedelta(days=self.config["alert_retention_days"])
        
        old_alerts = [
            alert_id for alert_id, alert in self.alerts.items()
            if alert.first_seen < cutoff_date and alert.status == AlertStatus.RESOLVED
        ]
        
        for alert_id in old_alerts:
            del self.alerts[alert_id]
        
        if old_alerts:
            logger.info(f"Cleaned up {len(old_alerts)} old alerts")
    
    async def _reset_notification_rate_limits(self):
        """Reset notification rate limits."""
        for config in self.notification_configs.values():
            if config.last_sent and (datetime.now() - config.last_sent).total_seconds() > 3600:
                config.send_count = 0


# Global security monitoring system instance
_security_monitoring_system: Optional[SecurityMonitoringSystem] = None


def get_security_monitoring_system() -> SecurityMonitoringSystem:
    """Get the global security monitoring system instance."""
    global _security_monitoring_system
    if _security_monitoring_system is None:
        _security_monitoring_system = SecurityMonitoringSystem()
    return _security_monitoring_system
