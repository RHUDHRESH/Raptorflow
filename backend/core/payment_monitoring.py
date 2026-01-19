"""
Payment Monitoring System with Real-time Metrics and Anomaly Detection
Implements comprehensive monitoring with anomaly detection and alerting
Addresses monitoring vulnerabilities identified in red team audit
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List, Union, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import redis
import numpy as np
from collections import defaultdict, deque
from statistics import mean, median, stdev
import asyncio

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "COUNTER"
    GAUGE = "GAUGE"
    HISTOGRAM = "HISTOGRAM"
    TIMER = "TIMER"

class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AnomalyType(Enum):
    """Types of anomalies"""
    SPIKE = "SPIKE"
    DROP = "DROP"
    UNUSUAL_PATTERN = "UNUSUAL_PATTERN"
    THRESHOLD_BREACH = "THRESHOLD_BREACH"
    STATISTICAL_OUTLIER = "STATISTICAL_OUTLIER"
    TREND_DEVIATION = "TREND_DEVIATION"

@dataclass
class MetricPoint:
    """Single metric data point"""
    timestamp: datetime
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MetricDefinition:
    """Metric definition with configuration"""
    name: str
    metric_type: MetricType
    description: str
    unit: str
    labels: List[str] = field(default_factory=list)
    aggregation: Optional[str] = None  # sum, avg, max, min
    retention_hours: int = 24
    thresholds: Dict[str, float] = field(default_factory=dict)

@dataclass
class AnomalyDetection:
    """Anomaly detection configuration"""
    metric_name: str
    anomaly_type: AnomalyType
    sensitivity: float = 0.95  # Statistical sensitivity
    window_minutes: int = 60
    min_samples: int = 10
    threshold_multiplier: float = 2.0  # Standard deviations from mean
    enabled: bool = True

@dataclass
class AnomalyAlert:
    """Anomaly alert"""
    alert_id: str
    metric_name: str
    anomaly_type: AnomalyType
    severity: AlertSeverity
    timestamp: datetime
    value: float
    expected_range: Tuple[float, float]
    confidence: float
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MonitoringDashboard:
    """Monitoring dashboard data"""
    timestamp: datetime
    total_transactions: int = 0
    successful_transactions: int = 0
    failed_transactions: int = 0
    total_amount: int = 0
    average_amount: float = 0.0
    success_rate: float = 0.0
    error_rate: float = 0.0
    average_response_time: float = 0.0
    active_users: int = 0
    alerts: List[AnomalyAlert] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)

class PaymentMonitor:
    """
    Production-Ready Payment Monitoring System
    Implements real-time metrics collection and anomaly detection
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        
        # Metric definitions
        self._metrics: Dict[str, MetricDefinition] = {}
        self._load_default_metrics()
        
        # Anomaly detection configurations
        self._anomaly_detectors: Dict[str, AnomalyDetection] = {}
        self._load_default_anomaly_detectors()
        
        # Metric storage
        self._metric_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._real_time_metrics: Dict[str, float] = {}
        
        # Alert management
        self._active_alerts: Dict[str, AnomalyAlert] = {}
        self._alert_handlers: List[Callable] = []
        
        # Background tasks
        self._monitoring_task: Optional[asyncio.Task] = None
        self._anomaly_detection_task: Optional[asyncio.Task] = None
        
        # Redis keys
        self.metrics_prefix = "payment_metrics:"
        self.alerts_prefix = "payment_alerts:"
        self.dashboard_prefix = "payment_dashboard:"
        
        # Configuration
        self.monitoring_interval_seconds = 30
        self.anomaly_detection_interval_seconds = 60
        self.max_alerts_per_metric = 10
        
        logger.info("Payment Monitor initialized")
    
    def _load_default_metrics(self):
        """Load default metric definitions"""
        default_metrics = [
            MetricDefinition(
                name="payment_transactions_total",
                metric_type=MetricType.COUNTER,
                description="Total number of payment transactions",
                unit="count",
                aggregation="sum"
            ),
            MetricDefinition(
                name="payment_transactions_successful",
                metric_type=MetricType.COUNTER,
                description="Number of successful payment transactions",
                unit="count",
                aggregation="sum"
            ),
            MetricDefinition(
                name="payment_transactions_failed",
                metric_type=MetricType.COUNTER,
                description="Number of failed payment transactions",
                unit="count",
                aggregation="sum"
            ),
            MetricDefinition(
                name="payment_amount_total",
                metric_type=MetricType.COUNTER,
                description="Total amount of all payment transactions",
                unit="paise",
                aggregation="sum"
            ),
            MetricDefinition(
                name="payment_response_time",
                metric_type=MetricType.TIMER,
                description="Payment transaction response time",
                unit="milliseconds",
                aggregation="avg",
                thresholds={"warning": 5000, "critical": 10000}
            ),
            MetricDefinition(
                name="payment_success_rate",
                metric_type=MetricType.GAUGE,
                description="Payment transaction success rate",
                unit="percent",
                aggregation="avg",
                thresholds={"warning": 95.0, "critical": 90.0}
            ),
            MetricDefinition(
                name="payment_error_rate",
                metric_type=MetricType.GAUGE,
                description="Payment transaction error rate",
                unit="percent",
                aggregation="avg",
                thresholds={"warning": 5.0, "critical": 10.0}
            ),
            MetricDefinition(
                name="refund_transactions_total",
                metric_type=MetricType.COUNTER,
                description="Total number of refund transactions",
                unit="count",
                aggregation="sum"
            ),
            MetricDefinition(
                name="webhook_events_total",
                metric_type=MetricType.COUNTER,
                description="Total number of webhook events",
                unit="count",
                aggregation="sum"
            ),
            MetricDefinition(
                name="fraud_alerts_total",
                metric_type=MetricType.COUNTER,
                description="Total number of fraud alerts",
                unit="count",
                aggregation="sum"
            ),
            MetricDefinition(
                name="active_users",
                metric_type=MetricType.GAUGE,
                description="Number of active users",
                unit="count",
                aggregation="avg"
            )
        ]
        
        for metric in default_metrics:
            self._metrics[metric.name] = metric
    
    def _load_default_anomaly_detectors(self):
        """Load default anomaly detection configurations"""
        default_detectors = [
            AnomalyDetection(
                metric_name="payment_transactions_failed",
                anomaly_type=AnomalyType.SPIKE,
                sensitivity=0.95,
                window_minutes=5,
                threshold_multiplier=2.0
            ),
            AnomalyDetection(
                metric_name="payment_success_rate",
                anomaly_type=AnomalyType.DROP,
                sensitivity=0.95,
                window_minutes=10,
                threshold_multiplier=2.0
            ),
            AnomalyDetection(
                metric_name="payment_response_time",
                anomaly_type=AnomalyType.SPIKE,
                sensitivity=0.95,
                window_minutes=5,
                threshold_multiplier=2.0
            ),
            AnomalyDetection(
                metric_name="payment_amount_total",
                anomaly_type=AnomalyType.UNUSUAL_PATTERN,
                sensitivity=0.95,
                window_minutes=15,
                threshold_multiplier=3.0
            ),
            AnomalyDetection(
                metric_name="webhook_events_total",
                anomaly_type=AnomalyType.STATISTICAL_OUTLIER,
                sensitivity=0.95,
                window_minutes=5,
                threshold_multiplier=2.5
            )
        ]
        
        for detector in default_detectors:
            self._anomaly_detectors[detector.metric_name] = detector
    
    async def start_monitoring(self):
        """Start background monitoring tasks"""
        if not self._monitoring_task:
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        if not self._anomaly_detection_task:
            self._anomaly_detection_task = asyncio.create_task(self._anomaly_detection_loop())
        
        logger.info("Payment monitoring started")
    
    async def stop_monitoring(self):
        """Stop background monitoring tasks"""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
            self._monitoring_task = None
        
        if self._anomaly_detection_task:
            self._anomaly_detection_task.cancel()
            try:
                await self._anomaly_detection_task
            except asyncio.CancelledError:
                pass
            self._anomaly_detection_task = None
        
        logger.info("Payment monitoring stopped")
    
    async def _monitoring_loop(self):
        """Background monitoring loop"""
        while True:
            try:
                await asyncio.sleep(self.monitoring_interval_seconds)
                await self._update_dashboard()
                await self._cleanup_old_data()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
    
    async def _anomaly_detection_loop(self):
        """Background anomaly detection loop"""
        while True:
            try:
                await asyncio.sleep(self.anomaly_detection_interval_seconds)
                await self._detect_anomalies()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in anomaly detection loop: {e}")
    
    async def record_transaction_event(
        self,
        event_type: str,
        transaction_id: str,
        amount: Optional[int] = None,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        response_time_ms: Optional[float] = None
    ):
        """Record payment transaction event"""
        try:
            timestamp = datetime.now()
            
            # Record basic transaction metrics
            await self._record_metric("payment_transactions_total", 1.0, timestamp)
            
            if status == "COMPLETED" or status == "SUCCESS":
                await self._record_metric("payment_transactions_successful", 1.0, timestamp)
                if amount:
                    await self._record_metric("payment_amount_total", float(amount), timestamp)
            elif status == "FAILED" or status == "ERROR":
                await self._record_metric("payment_transactions_failed", 1.0, timestamp)
            
            # Record response time
            if response_time_ms:
                await self._record_metric("payment_response_time", response_time_ms, timestamp)
            
            # Update real-time metrics
            await self._update_real_time_metrics()
            
        except Exception as e:
            logger.error(f"Error recording transaction event: {e}")
    
    async def record_webhook_event(
        self,
        event_type: str,
        transaction_id: Optional[str] = None,
        status: Optional[str] = None
    ):
        """Record webhook event"""
        try:
            timestamp = datetime.now()
            await self._record_metric("webhook_events_total", 1.0, timestamp)
            
        except Exception as e:
            logger.error(f"Error recording webhook event: {e}")
    
    async def record_fraud_alert(
        self,
        user_id: str,
        risk_score: float,
        risk_level: str,
        transaction_id: Optional[str] = None
    ):
        """Record fraud alert"""
        try:
            timestamp = datetime.now()
            await self._record_metric("fraud_alerts_total", 1.0, timestamp)
            
            # Create anomaly alert for high fraud risk
            if risk_level in ["HIGH", "CRITICAL"]:
                alert = AnomalyAlert(
                    alert_id=str(uuid.uuid4()),
                    metric_name="fraud_alerts_total",
                    anomaly_type=AnomalyType.THRESHOLD_BREACH,
                    severity=AlertSeverity.HIGH if risk_level == "HIGH" else AlertSeverity.CRITICAL,
                    timestamp=timestamp,
                    value=risk_score,
                    expected_range=(0.0, 0.5),
                    confidence=0.9,
                    description=f"High fraud risk detected: {risk_level}",
                    metadata={
                        "user_id": user_id,
                        "transaction_id": transaction_id,
                        "risk_level": risk_level
                    }
                )
                
                await self._create_alert(alert)
            
        except Exception as e:
            logger.error(f"Error recording fraud alert: {e}")
    
    async def _record_metric(self, metric_name: str, value: float, timestamp: datetime):
        """Record metric value"""
        try:
            # Add to time series data
            self._metric_data[metric_name].append(MetricPoint(timestamp=timestamp, value=value))
            
            # Update real-time value
            self._real_time_metrics[metric_name] = value
            
            # Store in Redis for persistence
            metric_key = f"{self.metrics_prefix}{metric_name}"
            metric_data = {
                "timestamp": timestamp.isoformat(),
                "value": value
            }
            
            # Use Redis list for time series
            self.redis.lpush(metric_key, json.dumps(metric_data))
            
            # Trim to retention period
            metric_def = self._metrics.get(metric_name)
            if metric_def:
                max_entries = metric_def.retention_hours * 120  # 2 entries per minute
                self.redis.ltrim(metric_key, 0, max_entries)
            
            # Set expiration
            self.redis.expire(metric_key, metric_def.retention_hours * 3600)
            
        except Exception as e:
            logger.error(f"Error recording metric {metric_name}: {e}")
    
    async def _update_real_time_metrics(self):
        """Update calculated real-time metrics"""
        try:
            # Calculate success rate
            total_tx = self._real_time_metrics.get("payment_transactions_total", 0)
            successful_tx = self._real_time_metrics.get("payment_transactions_successful", 0)
            
            if total_tx > 0:
                success_rate = (successful_tx / total_tx) * 100
                error_rate = ((total_tx - successful_tx) / total_tx) * 100
                
                await self._record_metric("payment_success_rate", success_rate, datetime.now())
                await self._record_metric("payment_error_rate", error_rate, datetime.now())
            
            # Calculate average amount
            total_amount = self._real_time_metrics.get("payment_amount_total", 0)
            successful_tx = self._real_time_metrics.get("payment_transactions_successful", 0)
            
            if successful_tx > 0:
                avg_amount = total_amount / successful_tx
                await self._record_metric("payment_average_amount", avg_amount, datetime.now())
            
        except Exception as e:
            logger.error(f"Error updating real-time metrics: {e}")
    
    async def _detect_anomalies(self):
        """Detect anomalies in metrics"""
        for metric_name, detector in self._anomaly_detectors.items():
            if not detector.enabled:
                continue
            
            try:
                await self._detect_metric_anomaly(metric_name, detector)
            except Exception as e:
                logger.error(f"Error detecting anomaly for {metric_name}: {e}")
    
    async def _detect_metric_anomaly(self, metric_name: str, detector: AnomalyDetection):
        """Detect anomaly for specific metric"""
        try:
            # Get recent data points
            recent_data = list(self._metric_data[metric_name])
            
            if len(recent_data) < detector.min_samples:
                return
            
            # Filter data within window
            cutoff_time = datetime.now() - timedelta(minutes=detector.window_minutes)
            window_data = [point for point in recent_data if point.timestamp >= cutoff_time]
            
            if len(window_data) < detector.min_samples:
                return
            
            values = [point.value for point in window_data]
            current_value = values[-1]
            
            # Detect based on anomaly type
            if detector.anomaly_type == AnomalyType.SPIKE:
                await self._detect_spike(metric_name, detector, values, current_value)
            elif detector.anomaly_type == AnomalyType.DROP:
                await self._detect_drop(metric_name, detector, values, current_value)
            elif detector.anomaly_type == AnomalyType.STATISTICAL_OUTLIER:
                await self._detect_statistical_outlier(metric_name, detector, values, current_value)
            elif detector.anomaly_type == AnomalyType.THRESHOLD_BREACH:
                await self._detect_threshold_breach(metric_name, detector, current_value)
            
        except Exception as e:
            logger.error(f"Error detecting metric anomaly: {e}")
    
    async def _detect_spike(self, metric_name: str, detector: AnomalyDetection, values: List[float], current_value: float):
        """Detect spike anomaly"""
        try:
            # Calculate baseline (excluding recent values)
            baseline_values = values[:-5] if len(values) > 5 else values[:-1]
            
            if len(baseline_values) < 3:
                return
            
            baseline_mean = mean(baseline_values)
            baseline_std = stdev(baseline_values) if len(baseline_values) > 1 else 0
            
            # Check for spike (multiple standard deviations from baseline)
            if baseline_std > 0:
                z_score = abs(current_value - baseline_mean) / baseline_std
                
                if z_score > detector.threshold_multiplier:
                    severity = AlertSeverity.HIGH if z_score > 3 else AlertSeverity.MEDIUM
                    
                    alert = AnomalyAlert(
                        alert_id=str(uuid.uuid4()),
                        metric_name=metric_name,
                        anomaly_type=AnomalyType.SPIKE,
                        severity=severity,
                        timestamp=datetime.now(),
                        value=current_value,
                        expected_range=(baseline_mean - 2*baseline_std, baseline_mean + 2*baseline_std),
                        confidence=min(z_score / 3.0, 1.0),
                        description=f"Spike detected in {metric_name}: {current_value:.2f} (baseline: {baseline_mean:.2f})",
                        metadata={
                            "z_score": z_score,
                            "baseline_mean": baseline_mean,
                            "baseline_std": baseline_std
                        }
                    )
                    
                    await self._create_alert(alert)
            
        except Exception as e:
            logger.error(f"Error detecting spike: {e}")
    
    async def _detect_drop(self, metric_name: str, detector: AnomalyDetection, values: List[float], current_value: float):
        """Detect drop anomaly"""
        try:
            # Calculate baseline
            baseline_values = values[:-5] if len(values) > 5 else values[:-1]
            
            if len(baseline_values) < 3:
                return
            
            baseline_mean = mean(baseline_values)
            
            # Check for significant drop (more than 50% decrease)
            if baseline_mean > 0:
                drop_percentage = (baseline_mean - current_value) / baseline_mean
                
                if drop_percentage > 0.5:  # 50% drop
                    severity = AlertSeverity.CRITICAL if drop_percentage > 0.8 else AlertSeverity.HIGH
                    
                    alert = AnomalyAlert(
                        alert_id=str(uuid.uuid4()),
                        metric_name=metric_name,
                        anomaly_type=AnomalyType.DROP,
                        severity=severity,
                        timestamp=datetime.now(),
                        value=current_value,
                        expected_range=(baseline_mean * 0.5, baseline_mean * 1.5),
                        confidence=drop_percentage,
                        description=f"Drop detected in {metric_name}: {current_value:.2f} (baseline: {baseline_mean:.2f})",
                        metadata={
                            "drop_percentage": drop_percentage,
                            "baseline_mean": baseline_mean
                        }
                    )
                    
                    await self._create_alert(alert)
            
        except Exception as e:
            logger.error(f"Error detecting drop: {e}")
    
    async def _detect_statistical_outlier(self, metric_name: str, detector: AnomalyDetection, values: List[float], current_value: float):
        """Detect statistical outlier"""
        try:
            if len(values) < 10:
                return
            
            # Calculate statistics
            mean_val = mean(values)
            std_val = stdev(values)
            
            if std_val == 0:
                return
            
            # Calculate Z-score
            z_score = abs(current_value - mean_val) / std_val
            
            if z_score > detector.threshold_multiplier:
                severity = AlertSeverity.HIGH if z_score > 3 else AlertSeverity.MEDIUM
                
                alert = AnomalyAlert(
                    alert_id=str(uuid.uuid4()),
                    metric_name=metric_name,
                    anomaly_type=AnomalyType.STATISTICAL_OUTLIER,
                    severity=severity,
                    timestamp=datetime.now(),
                    value=current_value,
                    expected_range=(mean_val - 2*std_val, mean_val + 2*std_val),
                    confidence=min(z_score / 3.0, 1.0),
                    description=f"Statistical outlier in {metric_name}: {current_value:.2f} (mean: {mean_val:.2f})",
                    metadata={
                        "z_score": z_score,
                        "mean": mean_val,
                        "std": std_val
                    }
                )
                
                await self._create_alert(alert)
            
        except Exception as e:
            logger.error(f"Error detecting statistical outlier: {e}")
    
    async def _detect_threshold_breach(self, metric_name: str, detector: AnomalyDetection, current_value: float):
        """Detect threshold breach"""
        try:
            metric_def = self._metrics.get(metric_name)
            if not metric_def or not metric_def.thresholds:
                return
            
            # Check against thresholds
            for threshold_name, threshold_value in metric_def.thresholds.items():
                if threshold_name == "critical" and current_value > threshold_value:
                    alert = AnomalyAlert(
                        alert_id=str(uuid.uuid4()),
                        metric_name=metric_name,
                        anomaly_type=AnomalyType.THRESHOLD_BREACH,
                        severity=AlertSeverity.CRITICAL,
                        timestamp=datetime.now(),
                        value=current_value,
                        expected_range=(0, threshold_value),
                        confidence=1.0,
                        description=f"Critical threshold breach in {metric_name}: {current_value:.2f} > {threshold_value}",
                        metadata={
                            "threshold_type": threshold_name,
                            "threshold_value": threshold_value
                        }
                    )
                    
                    await self._create_alert(alert)
                    break
                elif threshold_name == "warning" and current_value > threshold_value:
                    alert = AnomalyAlert(
                        alert_id=str(uuid.uuid4()),
                        metric_name=metric_name,
                        anomaly_type=AnomalyType.THRESHOLD_BREACH,
                        severity=AlertSeverity.MEDIUM,
                        timestamp=datetime.now(),
                        value=current_value,
                        expected_range=(0, threshold_value),
                        confidence=0.8,
                        description=f"Warning threshold breach in {metric_name}: {current_value:.2f} > {threshold_value}",
                        metadata={
                            "threshold_type": threshold_name,
                            "threshold_value": threshold_value
                        }
                    )
                    
                    await self._create_alert(alert)
                    break
            
        except Exception as e:
            logger.error(f"Error detecting threshold breach: {e}")
    
    async def _create_alert(self, alert: AnomalyAlert):
        """Create and handle anomaly alert"""
        try:
            # Check if we already have too many alerts for this metric
            metric_alerts = [a for a in self._active_alerts.values() if a.metric_name == alert.metric_name]
            
            if len(metric_alerts) >= self.max_alerts_per_metric:
                # Remove oldest alert
                oldest_alert = min(metric_alerts, key=lambda a: a.timestamp)
                del self._active_alerts[oldest_alert.alert_id]
            
            # Add new alert
            self._active_alerts[alert.alert_id] = alert
            
            # Store in Redis
            alert_key = f"{self.alerts_prefix}{alert.alert_id}"
            alert_data = {
                "alert_id": alert.alert_id,
                "metric_name": alert.metric_name,
                "anomaly_type": alert.anomaly_type.value,
                "severity": alert.severity.value,
                "timestamp": alert.timestamp.isoformat(),
                "value": alert.value,
                "expected_range": alert.expected_range,
                "confidence": alert.confidence,
                "description": alert.description,
                "metadata": alert.metadata
            }
            
            self.redis.setex(alert_key, 86400, json.dumps(alert_data))  # 24 hours
            
            # Notify handlers
            for handler in self._alert_handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(alert)
                    else:
                        handler(alert)
                except Exception as e:
                    logger.error(f"Error in alert handler: {e}")
            
            # Log alert
            await self._log_alert(alert)
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
    
    async def _log_alert(self, alert: AnomalyAlert):
        """Log alert to audit system"""
        try:
            # This would integrate with the audit logger
            logger.warning(f"Anomaly Alert: {alert.description}")
        except Exception as e:
            logger.error(f"Error logging alert: {e}")
    
    async def _update_dashboard(self):
        """Update monitoring dashboard"""
        try:
            timestamp = datetime.now()
            
            # Get current metrics
            total_tx = self._real_time_metrics.get("payment_transactions_total", 0)
            successful_tx = self._real_time_metrics.get("payment_transactions_successful", 0)
            failed_tx = self._real_time_metrics.get("payment_transactions_failed", 0)
            total_amount = self._real_time_metrics.get("payment_amount_total", 0)
            success_rate = self._real_time_metrics.get("payment_success_rate", 0)
            error_rate = self._real_time_metrics.get("payment_error_rate", 0)
            response_time = self._real_time_metrics.get("payment_response_time", 0)
            active_users = self._real_time_metrics.get("active_users", 0)
            
            # Calculate average amount
            avg_amount = (total_amount / successful_tx) if successful_tx > 0 else 0
            
            # Get recent alerts
            recent_alerts = list(self._active_alerts.values())
            recent_alerts.sort(key=lambda a: a.timestamp, reverse=True)
            recent_alerts = recent_alerts[:10]  # Top 10 recent alerts
            
            # Create dashboard
            dashboard = MonitoringDashboard(
                timestamp=timestamp,
                total_transactions=int(total_tx),
                successful_transactions=int(successful_tx),
                failed_transactions=int(failed_tx),
                total_amount=int(total_amount),
                average_amount=avg_amount,
                success_rate=success_rate,
                error_rate=error_rate,
                average_response_time=response_time,
                active_users=int(active_users),
                alerts=recent_alerts,
                metrics=self._real_time_metrics.copy()
            )
            
            # Store in Redis
            dashboard_key = f"{self.dashboard_prefix}current"
            dashboard_data = {
                "timestamp": timestamp.isoformat(),
                "total_transactions": dashboard.total_transactions,
                "successful_transactions": dashboard.successful_transactions,
                "failed_transactions": dashboard.failed_transactions,
                "total_amount": dashboard.total_amount,
                "average_amount": dashboard.average_amount,
                "success_rate": dashboard.success_rate,
                "error_rate": dashboard.error_rate,
                "average_response_time": dashboard.average_response_time,
                "active_users": dashboard.active_users,
                "alerts": [
                    {
                        "alert_id": alert.alert_id,
                        "metric_name": alert.metric_name,
                        "severity": alert.severity.value,
                        "description": alert.description,
                        "timestamp": alert.timestamp.isoformat()
                    }
                    for alert in dashboard.alerts
                ],
                "metrics": dashboard.metrics
            }
            
            self.redis.setex(dashboard_key, 300, json.dumps(dashboard_data))  # 5 minutes
            
        except Exception as e:
            logger.error(f"Error updating dashboard: {e}")
    
    async def _cleanup_old_data(self):
        """Clean up old monitoring data"""
        try:
            # Clean up old metric data
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            for metric_name, data_points in self._metric_data.items():
                # Remove old data points
                while data_points and data_points[0].timestamp < cutoff_time:
                    data_points.popleft()
            
            # Clean up old alerts
            alert_cutoff_time = datetime.now() - timedelta(hours=24)
            expired_alerts = [
                alert_id for alert_id, alert in self._active_alerts.items()
                if alert.timestamp < alert_cutoff_time
            ]
            
            for alert_id in expired_alerts:
                del self._active_alerts[alert_id]
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
    
    def add_alert_handler(self, handler: Callable):
        """Add alert handler function"""
        self._alert_handlers.append(handler)
    
    def remove_alert_handler(self, handler: Callable):
        """Remove alert handler function"""
        if handler in self._alert_handlers:
            self._alert_handlers.remove(handler)
    
    async def get_dashboard(self) -> Optional[MonitoringDashboard]:
        """Get current monitoring dashboard"""
        try:
            dashboard_key = f"{self.dashboard_prefix}current"
            dashboard_data = self.redis.get(dashboard_key)
            
            if dashboard_data:
                data = json.loads(dashboard_data)
                
                alerts = []
                for alert_data in data.get("alerts", []):
                    alert = AnomalyAlert(
                        alert_id=alert_data["alert_id"],
                        metric_name=alert_data["metric_name"],
                        anomaly_type=AnomalyType(alert_data["anomaly_type"]),
                        severity=AlertSeverity(alert_data["severity"]),
                        timestamp=datetime.fromisoformat(alert_data["timestamp"]),
                        value=0.0,  # Not included in dashboard
                        expected_range=(0.0, 0.0),
                        confidence=0.0,
                        description=alert_data["description"]
                    )
                    alerts.append(alert)
                
                return MonitoringDashboard(
                    timestamp=datetime.fromisoformat(data["timestamp"]),
                    total_transactions=data["total_transactions"],
                    successful_transactions=data["successful_transactions"],
                    failed_transactions=data["failed_transactions"],
                    total_amount=data["total_amount"],
                    average_amount=data["average_amount"],
                    success_rate=data["success_rate"],
                    error_rate=data["error_rate"],
                    average_response_time=data["average_response_time"],
                    active_users=data["active_users"],
                    alerts=alerts,
                    metrics=data["metrics"]
                )
            
        except Exception as e:
            logger.error(f"Error getting dashboard: {e}")
        
        return None
    
    async def get_metrics(self, metric_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get current metrics"""
        try:
            if metric_names:
                return {name: self._real_time_metrics.get(name, 0) for name in metric_names}
            else:
                return self._real_time_metrics.copy()
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return {}
    
    async def get_alerts(self, severity: Optional[AlertSeverity] = None, limit: int = 50) -> List[AnomalyAlert]:
        """Get recent alerts"""
        try:
            alerts = list(self._active_alerts.values())
            
            if severity:
                alerts = [alert for alert in alerts if alert.severity == severity]
            
            alerts.sort(key=lambda a: a.timestamp, reverse=True)
            return alerts[:limit]
            
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for payment monitor"""
        try:
            # Check Redis connection
            try:
                self.redis.ping()
                redis_healthy = True
            except Exception as e:
                redis_healthy = False
                redis_error = str(e)
            
            # Check background tasks
            monitoring_active = self._monitoring_task and not self._monitoring_task.done()
            anomaly_active = self._anomaly_detection_task and not self._anomaly_detection_task.done()
            
            # Get system stats
            total_metrics = len(self._real_time_metrics)
            active_alerts = len(self._active_alerts)
            data_points = sum(len(data) for data in self._metric_data.values())
            
            overall_healthy = redis_healthy and monitoring_active
            
            return {
                "status": "healthy" if overall_healthy else "unhealthy",
                "message": "Payment monitor is operational" if overall_healthy else "Payment monitor has issues",
                "features": {
                    "real_time_metrics": True,
                    "anomaly_detection": True,
                    "alert_management": True,
                    "dashboard_updates": True,
                    "data_retention": True,
                    "background_monitoring": monitoring_active,
                    "statistical_analysis": True
                },
                "configuration": {
                    "monitoring_interval_seconds": self.monitoring_interval_seconds,
                    "anomaly_detection_interval_seconds": self.anomaly_detection_interval_seconds,
                    "max_alerts_per_metric": self.max_alerts_per_metric,
                    "total_metrics_defined": len(self._metrics),
                    "total_anomaly_detectors": len(self._anomaly_detectors)
                },
                "runtime": {
                    "total_metrics": total_metrics,
                    "active_alerts": active_alerts,
                    "data_points_in_memory": data_points,
                    "alert_handlers": len(self._alert_handlers)
                },
                "dependencies": {
                    "redis": "healthy" if redis_healthy else f"unhealthy: {redis_error}"
                }
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Health check failed: {str(e)}",
                "error": str(e)
            }

# Global payment monitor instance
payment_monitor = None

def get_payment_monitor(redis_client: redis.Redis) -> PaymentMonitor:
    """Get or create payment monitor instance"""
    global payment_monitor
    if payment_monitor is None:
        payment_monitor = PaymentMonitor(redis_client)
        asyncio.create_task(payment_monitor.start_monitoring())
    return payment_monitor
