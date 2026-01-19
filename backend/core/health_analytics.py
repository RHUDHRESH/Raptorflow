"""
Health analytics and intelligent alerting system.
Provides comprehensive health analytics with smart notification capabilities.
"""

import asyncio
import json
import logging
import smtplib
import time
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from enum import Enum
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import aiohttp
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


class AlertType(Enum):
    """Types of health alerts."""
    THRESHOLD_EXCEEDED = "threshold_exceeded"
    ANOMALY_DETECTED = "anomaly_detected"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    SERVICE_UNAVAILABLE = "service_unavailable"
    SECURITY_BREACH = "security_breach"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    PREDICTIVE_FAILURE = "predictive_failure"
    CUSTOM = "custom"


class NotificationChannel(Enum):
    """Notification channels."""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"
    IN_APP = "in_app"
    DATABASE = "database"


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert status values."""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


@dataclass
class NotificationConfig:
    """Notification configuration."""
    
    channel: NotificationChannel
    enabled: bool
    recipients: List[str]
    template: str
    retry_count: int = 3
    retry_delay: int = 60  # seconds
    rate_limit: int = 10  # per hour
    custom_settings: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.custom_settings is None:
            self.custom_settings = {}


@dataclass
class HealthAlert:
    """Health alert with full context."""
    
    id: str
    name: str
    description: str
    alert_type: AlertType
    severity: AlertSeverity
    status: AlertStatus
    source: str
    metric_name: str
    current_value: float
    threshold_value: Optional[float]
    timestamp: datetime
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    metadata: Dict[str, Any] = None
    notifications_sent: List[str] = None
    suppression_rules: List[str] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.notifications_sent is None:
            self.notifications_sent = []
        if self.suppression_rules is None:
            self.suppression_rules = []


@dataclass
class AlertRule:
    """Alert rule definition."""
    
    id: str
    name: str
    description: str
    metric_pattern: str
    condition: str  # gt, lt, eq, ne, gte, lte
    threshold: float
    severity: AlertSeverity
    enabled: bool
    notification_channels: List[NotificationChannel]
    cooldown_period: int = 300  # seconds
    evaluation_window: int = 60  # seconds
    suppression_rules: List[str] = None
    custom_logic: Optional[str] = None
    
    def __post_init__(self):
        if self.suppression_rules is None:
            self.suppression_rules = []


@dataclass
class AlertTrend:
    """Alert trend analysis."""
    
    metric_name: str
    time_window: timedelta
    alert_count: int
    severity_distribution: Dict[str, int]
    trend_direction: str  # increasing, decreasing, stable
    confidence: float
    prediction: Optional[str] = None


class NotificationEngine:
    """Intelligent notification engine."""
    
    def __init__(self):
        self.configs: Dict[NotificationChannel, NotificationConfig] = {}
        self.rate_limits: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.delivery_history: deque = deque(maxlen=1000)
        
        # Initialize default configurations
        self._initialize_default_configs()
    
    def _initialize_default_configs(self):
        """Initialize default notification configurations."""
        # Email configuration
        self.configs[NotificationChannel.EMAIL] = NotificationConfig(
            channel=NotificationChannel.EMAIL,
            enabled=False,
            recipients=[],
            template="email_alert.html",
            custom_settings={
                "smtp_server": "localhost",
                "smtp_port": 587,
                "use_tls": True,
                "sender_email": "alerts@raptorflow.com",
                "sender_name": "Raptorflow Alerts"
            }
        )
        
        # Slack configuration
        self.configs[NotificationChannel.SLACK] = NotificationConfig(
            channel=NotificationChannel.SLACK,
            enabled=False,
            recipients=[],
            template="slack_alert.json",
            custom_settings={
                "webhook_url": "",
                "channel": "#alerts",
                "username": "Raptorflow Bot"
            }
        )
        
        # Webhook configuration
        self.configs[NotificationChannel.WEBHOOK] = NotificationConfig(
            channel=NotificationChannel.WEBHOOK,
            enabled=False,
            recipients=[],
            template="webhook_alert.json",
            custom_settings={
                "timeout": 30,
                "headers": {"Content-Type": "application/json"}
            }
        )
    
    def configure_channel(self, channel: NotificationChannel, config: NotificationConfig):
        """Configure notification channel."""
        self.configs[channel] = config
        logger.info(f"Configured notification channel: {channel.value}")
    
    async def send_notification(self, alert: HealthAlert, 
                            channels: List[NotificationChannel] = None) -> Dict[str, bool]:
        """Send alert notification through specified channels."""
        if channels is None:
            channels = [NotificationChannel.IN_APP]  # Default to in-app
        
        results = {}
        
        for channel in channels:
            try:
                # Check if channel is enabled
                config = self.configs.get(channel)
                if not config or not config.enabled:
                    results[channel.value] = False
                    continue
                
                # Check rate limiting
                if not self._check_rate_limit(channel, config):
                    logger.warning(f"Rate limit exceeded for {channel.value}")
                    results[channel.value] = False
                    continue
                
                # Send notification
                success = await self._send_via_channel(alert, channel, config)
                results[channel.value] = success
                
                if success:
                    alert.notifications_sent.append(channel.value)
                    self._record_delivery(channel, alert, success)
                
            except Exception as e:
                logger.error(f"Failed to send {channel.value} notification: {e}")
                results[channel.value] = False
        
        return results
    
    def _check_rate_limit(self, channel: NotificationChannel, config: NotificationConfig) -> bool:
        """Check if notification is within rate limits."""
        now = time.time()
        rate_key = f"{channel.value}_{int(now // 3600)}"  # Per hour key
        
        current_count = len(self.rate_limits[rate_key])
        return current_count < config.rate_limit
    
    async def _send_via_channel(self, alert: HealthAlert, 
                              channel: NotificationChannel, 
                              config: NotificationConfig) -> bool:
        """Send notification via specific channel."""
        try:
            if channel == NotificationChannel.EMAIL:
                return await self._send_email(alert, config)
            elif channel == NotificationChannel.SLACK:
                return await self._send_slack(alert, config)
            elif channel == NotificationChannel.WEBHOOK:
                return await self._send_webhook(alert, config)
            elif channel == NotificationChannel.SMS:
                return await self._send_sms(alert, config)
            elif channel == NotificationChannel.IN_APP:
                return await self._send_in_app(alert, config)
            else:
                logger.warning(f"Unsupported notification channel: {channel.value}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending via {channel.value}: {e}")
            return False
    
    async def _send_email(self, alert: HealthAlert, config: NotificationConfig) -> bool:
        """Send email notification."""
        try:
            # Create message
            msg = MimeMultipart('alternative')
            msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.name}"
            msg['From'] = f"{config.custom_settings['sender_name']} <{config.custom_settings['sender_email']}>"
            msg['To'] = ', '.join(config.recipients)
            
            # Create HTML content
            html_content = self._generate_email_html(alert)
            html_part = MimeText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            smtp_server = config.custom_settings['smtp_server']
            smtp_port = config.custom_settings['smtp_port']
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                if config.custom_settings.get('use_tls', False):
                    server.starttls()
                
                # Add authentication if configured
                username = config.custom_settings.get('username')
                password = config.custom_settings.get('password')
                if username and password:
                    server.login(username, password)
                
                server.send_message(msg)
            
            logger.info(f"Email alert sent for {alert.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    async def _send_slack(self, alert: HealthAlert, config: NotificationConfig) -> bool:
        """Send Slack notification."""
        try:
            webhook_url = config.custom_settings.get('webhook_url')
            if not webhook_url:
                logger.error("Slack webhook URL not configured")
                return False
            
            # Create Slack payload
            payload = {
                "channel": config.custom_settings.get('channel', '#alerts'),
                "username": config.custom_settings.get('username', 'Raptorflow Bot'),
                "icon_emoji": ":warning:",
                "attachments": [
                    {
                        "color": self._get_slack_color(alert.severity),
                        "title": alert.name,
                        "text": alert.description,
                        "fields": [
                            {
                                "title": "Severity",
                                "value": alert.severity.value.upper(),
                                "short": True
                            },
                            {
                                "title": "Source",
                                "value": alert.source,
                                "short": True
                            },
                            {
                                "title": "Metric",
                                "value": f"{alert.metric_name}: {alert.current_value}",
                                "short": True
                            },
                            {
                                "title": "Time",
                                "value": alert.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"),
                                "short": True
                            }
                        ],
                        "footer": "Raptorflow Health Monitor",
                        "ts": int(alert.timestamp.timestamp())
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload, timeout=30) as response:
                    if response.status == 200:
                        logger.info(f"Slack alert sent for {alert.id}")
                        return True
                    else:
                        logger.error(f"Slack API error: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return False
    
    async def _send_webhook(self, alert: HealthAlert, config: NotificationConfig) -> bool:
        """Send webhook notification."""
        try:
            recipients = config.recipients
            if not recipients:
                logger.error("No webhook URLs configured")
                return False
            
            # Create webhook payload
            payload = {
                "alert_id": alert.id,
                "name": alert.name,
                "description": alert.description,
                "type": alert.alert_type.value,
                "severity": alert.severity.value,
                "status": alert.status.value,
                "source": alert.source,
                "metric": {
                    "name": alert.metric_name,
                    "current_value": alert.current_value,
                    "threshold": alert.threshold_value
                },
                "timestamp": alert.timestamp.isoformat(),
                "metadata": alert.metadata
            }
            
            headers = config.custom_settings.get('headers', {})
            timeout = config.custom_settings.get('timeout', 30)
            
            async with aiohttp.ClientSession() as session:
                tasks = []
                for url in recipients:
                    task = session.post(url, json=payload, headers=headers, timeout=timeout)
                    tasks.append(task)
                
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                
                success_count = sum(1 for r in responses if not isinstance(r, Exception) and r.status == 200)
                
                if success_count > 0:
                    logger.info(f"Webhook alert sent to {success_count}/{len(recipients)} endpoints for {alert.id}")
                    return True
                else:
                    logger.error("All webhook deliveries failed")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
            return False
    
    async def _send_sms(self, alert: HealthAlert, config: NotificationConfig) -> bool:
        """Send SMS notification."""
        # Placeholder for SMS implementation
        logger.info(f"SMS notification would be sent for {alert.id}")
        return True
    
    async def _send_in_app(self, alert: HealthAlert, config: NotificationConfig) -> bool:
        """Send in-app notification."""
        # Store in database or memory for in-app display
        logger.info(f"In-app notification stored for {alert.id}")
        return True
    
    def _generate_email_html(self, alert: HealthAlert) -> str:
        """Generate HTML email content."""
        color = self._get_alert_color(alert.severity)
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
                .header {{ background-color: {color}; color: white; padding: 20px; border-radius: 5px 5px 0 0; }}
                .content {{ background-color: #f9f9f9; padding: 20px; border: 1px solid #ddd; }}
                .footer {{ background-color: #f0f0f0; padding: 15px; border-radius: 0 0 5px 5px; font-size: 12px; color: #666; }}
                .severity {{ font-weight: bold; text-transform: uppercase; }}
                .metric {{ background-color: white; padding: 10px; margin: 10px 0; border-left: 4px solid {color}; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{alert.name}</h1>
                <p class="severity">Severity: {alert.severity.value.upper()}</p>
            </div>
            <div class="content">
                <p><strong>Description:</strong> {alert.description}</p>
                <div class="metric">
                    <p><strong>Metric:</strong> {alert.metric_name}</p>
                    <p><strong>Current Value:</strong> {alert.current_value}</p>
                    {f'<p><strong>Threshold:</strong> {alert.threshold_value}</p>' if alert.threshold_value else ''}
                </div>
                <p><strong>Source:</strong> {alert.source}</p>
                <p><strong>Time:</strong> {alert.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")}</p>
            </div>
            <div class="footer">
                <p>This alert was generated by Raptorflow Health Monitor.</p>
                <p>If you believe this is a false positive, please acknowledge the alert in the monitoring dashboard.</p>
            </div>
        </body>
        </html>
        """
        return html
    
    def _get_slack_color(self, severity: AlertSeverity) -> str:
        """Get Slack color for alert severity."""
        colors = {
            AlertSeverity.INFO: "#36a64f",      # green
            AlertSeverity.WARNING: "#ff9500",   # orange
            AlertSeverity.ERROR: "#ff0000",      # red
            AlertSeverity.CRITICAL: "#8b0000"   # dark red
        }
        return colors.get(severity, "#36a64f")
    
    def _get_alert_color(self, severity: AlertSeverity) -> str:
        """Get color for alert severity."""
        colors = {
            AlertSeverity.INFO: "#28a745",      # green
            AlertSeverity.WARNING: "#ffc107",   # yellow
            AlertSeverity.ERROR: "#dc3545",      # red
            AlertSeverity.CRITICAL: "#6f0000"   # dark red
        }
        return colors.get(severity, "#28a745")
    
    def _record_delivery(self, channel: NotificationChannel, alert: HealthAlert, success: bool):
        """Record notification delivery for analytics."""
        self.delivery_history.append({
            "timestamp": datetime.now(),
            "channel": channel.value,
            "alert_id": alert.id,
            "severity": alert.severity.value,
            "success": success
        })
    
    def get_delivery_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get notification delivery statistics."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_deliveries = [
            delivery for delivery in self.delivery_history
            if delivery["timestamp"] >= cutoff_time
        ]
        
        total_deliveries = len(recent_deliveries)
        successful_deliveries = sum(1 for d in recent_deliveries if d["success"])
        
        channel_stats = defaultdict(lambda: {"total": 0, "success": 0})
        for delivery in recent_deliveries:
            channel = delivery["channel"]
            channel_stats[channel]["total"] += 1
            if delivery["success"]:
                channel_stats[channel]["success"] += 1
        
        return {
            "period_hours": hours,
            "total_deliveries": total_deliveries,
            "successful_deliveries": successful_deliveries,
            "success_rate": successful_deliveries / max(total_deliveries, 1),
            "channel_stats": dict(channel_stats),
            "channels_enabled": [ch.value for ch, cfg in self.configs.items() if cfg.enabled]
        }


class HealthAnalytics:
    """Advanced health analytics with intelligent alerting."""
    
    def __init__(self):
        self.alerts: Dict[str, HealthAlert] = {}
        self.rules: Dict[str, AlertRule] = {}
        self.notification_engine = NotificationEngine()
        
        # Analytics data
        self.metric_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.alert_history: deque = deque(maxlen=10000)
        self.trend_analysis: Dict[str, AlertTrend] = {}
        
        # ML models for anomaly detection
        self.anomaly_detectors: Dict[str, IsolationForest] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        
        # Background processing
        self._analytics_task: Optional[asyncio.Task] = None
        self._is_running = False
        
        # Initialize default rules
        self._initialize_default_rules()
        
        logger.info("HealthAnalytics initialized")
    
    def _initialize_default_rules(self):
        """Initialize default alert rules."""
        default_rules = [
            AlertRule(
                id="cpu_high",
                name="High CPU Usage",
                description="Alert when CPU usage exceeds threshold",
                metric_pattern="cpu_usage",
                condition="gt",
                threshold=80.0,
                severity=AlertSeverity.WARNING,
                enabled=True,
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK],
                cooldown_period=300
            ),
            AlertRule(
                id="memory_high",
                name="High Memory Usage",
                description="Alert when memory usage exceeds threshold",
                metric_pattern="memory_usage",
                condition="gt",
                threshold=85.0,
                severity=AlertSeverity.WARNING,
                enabled=True,
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK],
                cooldown_period=300
            ),
            AlertRule(
                id="response_time_high",
                name="High Response Time",
                description="Alert when response time exceeds threshold",
                metric_pattern="response_time",
                condition="gt",
                threshold=1000.0,  # 1 second
                severity=AlertSeverity.ERROR,
                enabled=True,
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK],
                cooldown_period=180
            ),
            AlertRule(
                id="error_rate_high",
                name="High Error Rate",
                description="Alert when error rate exceeds threshold",
                metric_pattern="error_rate",
                condition="gt",
                threshold=5.0,  # 5%
                severity=AlertSeverity.ERROR,
                enabled=True,
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK],
                cooldown_period=300
            ),
            AlertRule(
                id="service_down",
                name="Service Unavailable",
                description="Alert when service becomes unavailable",
                metric_pattern="service_status",
                condition="eq",
                threshold=0.0,  # 0 = unhealthy
                severity=AlertSeverity.CRITICAL,
                enabled=True,
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK, NotificationChannel.SMS],
                cooldown_period=60
            )
        ]
        
        for rule in default_rules:
            self.rules[rule.id] = rule
    
    async def process_metric(self, metric_name: str, value: float, 
                          timestamp: Optional[datetime] = None,
                          metadata: Optional[Dict[str, Any]] = None):
        """Process metric and generate alerts if needed."""
        if timestamp is None:
            timestamp = datetime.now()
        
        # Store metric history
        self.metric_history[metric_name].append({
            "value": value,
            "timestamp": timestamp,
            "metadata": metadata or {}
        })
        
        # Evaluate alert rules
        await self._evaluate_rules(metric_name, value, timestamp, metadata)
        
        # Update anomaly detection
        await self._update_anomaly_detection(metric_name, value)
    
    async def _evaluate_rules(self, metric_name: str, value: float,
                            timestamp: datetime, metadata: Optional[Dict[str, Any]]):
        """Evaluate alert rules for metric."""
        for rule in self.rules.values():
            if not rule.enabled:
                continue
            
            # Check if rule applies to this metric
            if not self._metric_matches_rule(metric_name, rule.metric_pattern):
                continue
            
            # Check cooldown period
            if self._is_in_cooldown(rule, metric_name):
                continue
            
            # Evaluate condition
            if self._evaluate_condition(value, rule.condition, rule.threshold):
                # Generate alert
                alert = HealthAlert(
                    id=f"{rule.id}_{metric_name}_{int(timestamp.timestamp())}",
                    name=rule.name,
                    description=f"{rule.description}: {metric_name} = {value} (threshold: {rule.threshold})",
                    alert_type=AlertType.THRESHOLD_EXCEEDED,
                    severity=rule.severity,
                    status=AlertStatus.ACTIVE,
                    source="health_analytics",
                    metric_name=metric_name,
                    current_value=value,
                    threshold_value=rule.threshold,
                    timestamp=timestamp,
                    metadata=metadata or {}
                )
                
                # Store alert
                self.alerts[alert.id] = alert
                self.alert_history.append(alert)
                
                # Send notifications
                await self.notification_engine.send_notification(alert, rule.notification_channels)
                
                logger.warning(f"Alert generated: {alert.name}")
    
    def _metric_matches_rule(self, metric_name: str, pattern: str) -> bool:
        """Check if metric name matches rule pattern."""
        # Simple pattern matching - can be enhanced with regex
        return pattern in metric_name or metric_name in pattern
    
    def _evaluate_condition(self, value: float, condition: str, threshold: float) -> bool:
        """Evaluate alert condition."""
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
        elif condition == "ne":
            return abs(value - threshold) >= 0.001
        else:
            return False
    
    def _is_in_cooldown(self, rule: AlertRule, metric_name: str) -> bool:
        """Check if alert is in cooldown period."""
        cooldown_key = f"{rule.id}_{metric_name}"
        
        # Find recent alerts for this rule and metric
        recent_alerts = [
            alert for alert in self.alert_history
            if alert.id.startswith(rule.id) and alert.metric_name == metric_name
        ]
        
        if not recent_alerts:
            return False
        
        # Check if any alert is within cooldown period
        latest_alert = max(recent_alerts, key=lambda a: a.timestamp)
        time_since_last = (datetime.now() - latest_alert).total_seconds()
        
        return time_since_last < rule.cooldown_period
    
    async def _update_anomaly_detection(self, metric_name: str, value: float):
        """Update anomaly detection models."""
        history = list(self.metric_history[metric_name])
        
        if len(history) < 50:  # Need minimum data for training
            return
        
        try:
            # Prepare training data
            values = np.array([point["value"] for point in history[-100:]]).reshape(-1, 1)
            
            # Train or update model
            if metric_name not in self.anomaly_detectors:
                self.anomaly_detectors[metric_name] = IsolationForest(contamination=0.1, random_state=42)
                self.scalers[metric_name] = StandardScaler()
            
            # Scale data
            scaler = self.scalers[metric_name]
            scaled_values = scaler.fit_transform(values)
            
            # Train model
            detector = self.anomaly_detectors[metric_name]
            detector.fit(scaled_values)
            
            # Check for anomaly
            current_value = np.array([[value]])
            scaled_current = scaler.transform(current_value)
            
            is_anomaly = detector.predict(scaled_current)[0] == -1
            
            if is_anomaly:
                await self._generate_anomaly_alert(metric_name, value)
                
        except Exception as e:
            logger.error(f"Anomaly detection failed for {metric_name}: {e}")
    
    async def _generate_anomaly_alert(self, metric_name: str, value: float):
        """Generate anomaly alert."""
        alert = HealthAlert(
            id=f"anomaly_{metric_name}_{int(time.time())}",
            name=f"Anomaly Detected in {metric_name}",
            description=f"Anomalous value detected: {metric_name} = {value}",
            alert_type=AlertType.ANOMALY_DETECTED,
            severity=AlertSeverity.WARNING,
            status=AlertStatus.ACTIVE,
            source="anomaly_detection",
            metric_name=metric_name,
            current_value=value,
            threshold_value=None,
            timestamp=datetime.now(),
            metadata={"detection_method": "isolation_forest"}
        )
        
        self.alerts[alert.id] = alert
        self.alert_history.append(alert)
        
        # Send notifications
        await self.notification_engine.send_notification(alert)
        
        logger.warning(f"Anomaly alert generated: {alert.name}")
    
    async def analyze_trends(self):
        """Analyze trends in metrics and alerts."""
        for metric_name, history in self.metric_history.items():
            if len(history) < 10:
                continue
            
            # Analyze alert trends
            recent_alerts = [
                alert for alert in self.alert_history
                if alert.metric_name == metric_name and
                (datetime.now() - alert.timestamp).total_seconds() < 3600  # Last hour
            ]
            
            if len(recent_alerts) >= 3:  # Only analyze if enough alerts
                trend = self._calculate_alert_trend(metric_name, recent_alerts)
                self.trend_analysis[metric_name] = trend
    
    def _calculate_alert_trend(self, metric_name: str, alerts: List[HealthAlert]) -> AlertTrend:
        """Calculate alert trend for metric."""
        # Sort alerts by timestamp
        sorted_alerts = sorted(alerts, key=lambda a: a.timestamp)
        
        # Calculate severity distribution
        severity_dist = defaultdict(int)
        for alert in sorted_alerts:
            severity_dist[alert.severity.value] += 1
        
        # Determine trend direction
        if len(sorted_alerts) >= 5:
            # Compare first half with second half
            mid_point = len(sorted_alerts) // 2
            first_half = len(sorted_alerts[:mid_point])
            second_half = len(sorted_alerts[mid_point:])
            
            if second_half > first_half * 1.2:
                trend_direction = "increasing"
            elif second_half < first_half * 0.8:
                trend_direction = "decreasing"
            else:
                trend_direction = "stable"
        else:
            trend_direction = "stable"
        
        # Calculate confidence based on consistency
        confidence = min(len(sorted_alerts) / 10.0, 1.0)
        
        return AlertTrend(
            metric_name=metric_name,
            time_window=timedelta(hours=1),
            alert_count=len(sorted_alerts),
            severity_distribution=dict(severity_dist),
            trend_direction=trend_direction,
            confidence=confidence
        )
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str):
        """Acknowledge an alert."""
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.now()
            alert.acknowledged_by = acknowledged_by
            
            logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
    
    async def resolve_alert(self, alert_id: str, resolved_by: str):
        """Resolve an alert."""
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.now()
            alert.resolved_by = resolved_by
            
            logger.info(f"Alert {alert_id} resolved by {resolved_by}")
    
    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[HealthAlert]:
        """Get active alerts."""
        alerts = [
            alert for alert in self.alerts.values()
            if alert.status in [AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED]
        ]
        
        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]
        
        return sorted(alerts, key=lambda a: a.timestamp, reverse=True)
    
    def get_alert_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get alert summary for specified time period."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_alerts = [
            alert for alert in self.alert_history
            if alert.timestamp >= cutoff_time
        ]
        
        # Calculate statistics
        total_alerts = len(recent_alerts)
        active_alerts = len([a for a in recent_alerts if a.status == AlertStatus.ACTIVE])
        acknowledged_alerts = len([a for a in recent_alerts if a.status == AlertStatus.ACKNOWLEDGED])
        resolved_alerts = len([a for a in recent_alerts if a.status == AlertStatus.RESOLVED])
        
        # Severity distribution
        severity_dist = defaultdict(int)
        for alert in recent_alerts:
            severity_dist[alert.severity.value] += 1
        
        # Type distribution
        type_dist = defaultdict(int)
        for alert in recent_alerts:
            type_dist[alert.alert_type.value] += 1
        
        return {
            "period_hours": hours,
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "acknowledged_alerts": acknowledged_alerts,
            "resolved_alerts": resolved_alerts,
            "severity_distribution": dict(severity_dist),
            "type_distribution": dict(type_dist),
            "trend_analysis": {name: asdict(trend) for name, trend in self.trend_analysis.items()},
            "notification_stats": self.notification_engine.get_delivery_stats(hours)
        }
    
    async def start_analytics(self):
        """Start background analytics processing."""
        if self._is_running:
            logger.warning("Health analytics already running")
            return
        
        self._is_running = True
        self._analytics_task = asyncio.create_task(self._analytics_loop())
        logger.info("Started health analytics")
    
    async def stop_analytics(self):
        """Stop background analytics processing."""
        if not self._is_running:
            return
        
        self._is_running = False
        if self._analytics_task:
            self._analytics_task.cancel()
            try:
                await self._analytics_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopped health analytics")
    
    async def _analytics_loop(self):
        """Background analytics processing loop."""
        while self._is_running:
            try:
                await self.analyze_trends()
                await asyncio.sleep(300)  # Analyze every 5 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Analytics loop error: {e}")
                await asyncio.sleep(60)
    
    def add_alert_rule(self, rule: AlertRule):
        """Add a new alert rule."""
        self.rules[rule.id] = rule
        logger.info(f"Added alert rule: {rule.name}")
    
    def update_alert_rule(self, rule_id: str, **kwargs):
        """Update an existing alert rule."""
        if rule_id in self.rules:
            rule = self.rules[rule_id]
            for key, value in kwargs.items():
                if hasattr(rule, key):
                    setattr(rule, key, value)
            logger.info(f"Updated alert rule: {rule_id}")
    
    def configure_notifications(self, channel: NotificationChannel, config: NotificationConfig):
        """Configure notification channel."""
        self.notification_engine.configure_channel(channel, config)


# Global health analytics instance
_health_analytics: Optional[HealthAnalytics] = None


def get_health_analytics() -> HealthAnalytics:
    """Get the global health analytics instance."""
    global _health_analytics
    if _health_analytics is None:
        _health_analytics = HealthAnalytics()
    return _health_analytics


async def process_health_metric(metric_name: str, value: float,
                            timestamp: Optional[datetime] = None,
                            metadata: Optional[Dict[str, Any]] = None):
    """Process health metric (convenience function)."""
    analytics = get_health_analytics()
    await analytics.process_metric(metric_name, value, timestamp, metadata)


def get_alert_summary(hours: int = 24) -> Dict[str, Any]:
    """Get alert summary (convenience function)."""
    analytics = get_health_analytics()
    return analytics.get_alert_summary(hours)


async def acknowledge_alert(alert_id: str, acknowledged_by: str):
    """Acknowledge alert (convenience function)."""
    analytics = get_health_analytics()
    await analytics.acknowledge_alert(alert_id, acknowledged_by)


async def resolve_alert(alert_id: str, resolved_by: str):
    """Resolve alert (convenience function)."""
    analytics = get_health_analytics()
    await analytics.resolve_alert(alert_id, resolved_by)


async def start_health_analytics():
    """Start health analytics (convenience function)."""
    analytics = get_health_analytics()
    await analytics.start_analytics()


async def stop_health_analytics():
    """Stop health analytics (convenience function)."""
    analytics = get_health_analytics()
    await analytics.stop_analytics()
