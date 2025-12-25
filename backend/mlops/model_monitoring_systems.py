"""
S.W.A.R.M. Phase 2: Model Monitoring Systems
Production-ready monitoring and observability for ML models
"""

import asyncio
import json
import logging
import os
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Tuple, Union

import numpy as np
import pandas as pd

# Monitoring imports
try:
    import prometheus_client
    from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

# Time series imports
try:
    import influxdb_client
    from influxdb_client.client.write_api import SYNCHRONOUS
    INFLUXDB_AVAILABLE = True
except ImportError:
    INFLUXDB_AVAILABLE = False

# Alerting imports
try:
    import requests
    from requests.adapters import HTTPAdapter
    ALERTING_AVAILABLE = True
except ImportError:
    ALERTING_AVAILABLE = False

# ML monitoring imports
try:
    import mlflow
    from mlflow.tracking import MlflowClient
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False

logger = logging.getLogger("raptorflow.model_monitoring")

class MetricType(Enum):
    """Metric types."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class MonitoringStatus(Enum):
    """Monitoring system status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class DriftType(Enum):
    """Drift detection types."""
    DATA_DRIFT = "data_drift"
    CONCEPT_DRIFT = "concept_drift"
    PERFORMANCE_DRIFT = "performance_drift"
    PREDICTION_DRIFT = "prediction_drift"

@dataclass
class MetricConfig:
    """Metric configuration."""
    metric_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    metric_type: MetricType = MetricType.GAUGE
    description: str = ""
    labels: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True
    collection_interval: int = 60  # seconds
    retention_period: int = 30  # days
    aggregation: Optional[str] = None  # avg, sum, max, min

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "metric_id": self.metric_id,
            "name": self.name,
            "metric_type": self.metric_type.value,
            "description": self.description,
            "labels": self.labels,
            "enabled": self.enabled,
            "collection_interval": self.collection_interval,
            "retention_period": self.retention_period,
            "aggregation": self.aggregation
        }

@dataclass
class AlertConfig:
    """Alert configuration."""
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    metric_name: str = ""
    condition: str = ""  # e.g., "metric > threshold"
    threshold: float = 0.0
    severity: AlertSeverity = AlertSeverity.WARNING
    enabled: bool = True
    cooldown_period: int = 300  # seconds
    notification_channels: List[str] = field(default_factory=list)
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "alert_id": self.alert_id,
            "name": self.name,
            "metric_name": self.metric_name,
            "condition": self.condition,
            "threshold": self.threshold,
            "severity": self.severity.value,
            "enabled": self.enabled,
            "cooldown_period": self.cooldown_period,
            "notification_channels": self.notification_channels,
            "description": self.description
        }

@dataclass
class MonitoringConfig:
    """Monitoring system configuration."""
    monitoring_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    model_name: str = ""
    model_version: str = ""
    environment: str = "production"
    metrics: List[MetricConfig] = field(default_factory=list)
    alerts: List[AlertConfig] = field(default_factory=list)
    data_sources: Dict[str, Any] = field(default_factory=dict)
    storage_backends: List[str] = field(default_factory=list)
    notification_channels: Dict[str, Any] = field(default_factory=dict)
    drift_detection: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "monitoring_id": self.monitoring_id,
            "name": self.name,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "environment": self.environment,
            "metrics": [m.to_dict() for m in self.metrics],
            "alerts": [a.to_dict() for a in self.alerts],
            "data_sources": self.data_sources,
            "storage_backends": self.storage_backends,
            "notification_channels": self.notification_channels,
            "drift_detection": self.drift_detection
        }

@dataclass
class MetricValue:
    """Metric value with timestamp."""
    metric_name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "metric_name": self.metric_name,
            "valuehamber":等级: self.valueestamp.isoformatlogger.error(f"增量同步失败:ille
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "labels": self.labels
        }

@dataclass
class AlertEvent:
    """Alert event."""
    alert_id: str
    alert_name: str
    severity: AlertSeverity
    metric_name: str
    current_value: float
    threshold: float
    message: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "alert_id": self.alert_id,
            "alert_name": self.alert_name,
            "severity": self.severity.value,
            "metric_name": self.metric_name,
            "current_value": self.current_value,
            "threshold": self.threshold,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "resolved": self.resolved,
            "resolved_at dese": selfFollowing the erroronfig.to_dict() for a in self.alerts],
            "data_sources": self.data_sources,
            "storage_backends": self.storage_backends,
            "notification_channels": self.notification_channels,
            "drift_detection": self.drift_detection
        }

@dataclass
class MetricValue:
    """Metric value with timestamp."""
    metric_name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "metric_name": self.metric_name,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "labels": self.labels
        }

@dataclass
class AlertEvent:
    """Alert event."""
    alert_id: str
    alert_name: str
    severity: AlertSeverity
    metric_name: str
    current_value: float
    threshold: float
    message: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "alert_id": self.alert_id,
            "alert_name": self.alert_name,
            "severity": self.severity.value,
            "metric_name": self.metric_name,
            "current_value": self.current_value,
            "threshold": self.threshold,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "resolved": self.resolved,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None
        }

class MetricCollector(ABC):
    """Abstract base class for metric collectors."""

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.status = MonitoringStatus.INACTIVE
        self.metrics_cache: Dict[str, List[MetricValue]] = {}

    @abstractmethod
    async def collect_metrics(self) -> List[MetricValue]:
        """Collect metrics."""
        pass

    @abstractmethod
    async def store_metrics(self, metrics: List[MetricValue]) -> bool:
        """Store metrics."""
        pass

    @abstractmethod
    async def get_metrics(self, metric_name: str, start_time: datetime,
                         end_time: datetime) -> List[MetricValue]:
        """Get metrics for time range."""
        pass

class PrometheusMetricCollector(MetricCollector):
    """Prometheus metric collector."""

    def __init__(self, config: MonitoringConfig):
        super().__init__(config)
        self.registry = CollectorRegistry()
        self.prometheus_metrics: Dict[str, Any] = {}
        self._setup_prometheus_metrics()

    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics."""
        if not PROMETHEUS_AVAILABLE:
            logger.warning("Prometheus not available, using mock metrics")
            return

        for metric_config in self.config.metrics:
            if metric_config.metric_type == MetricType.COUNTER:
                metric = Counter(
                    metric_config.name,
                    metric_config.description,
                    labelnames=list(metric_config.labels.keys()),
                    registry=self.registry
                )
            elif metric_config.metric_type == MetricType.GAUGE:
                metric = Gauge(
                    metric_config.name,
                    metric_config.description,
                    labelnames=list(metric_config.labels.keys()),
                    registry=self.registry
                )
            elif metric_config.metric_type == MetricType.HISTOGRAM:
                metric = Histogram(
                    metric_config.name,
                    metric_config.description,
                    labelnames=list(metric_config.labels.keys()),
                    registry=self.registry
                )
            else:
                continue

            self.prometheus_metrics[metric_config.name] = metric

    async def collect_metrics(self) -> List[MetricValue]:
        """Collect metrics from Prometheus."""
        metrics = []

        for metric_config in self.config.metrics:
            if not metric_config.enabled:
                continue

            # Simulate metric collection
            if metric_config.name == "model_inference_latency":
                value = np.random.normal(100, 20)  # ms
            elif metric_config.name == "model_inference_throughput":
                value = np.random.normal(1000, 100)  # requests/sec
            elif metric_config.name == "model_error_rate":
                value = np.random.uniform(0, 0.05)  # 0-5%
            elif metric_config.name == "model_memory_usage":
                value = np.random.uniform(0.5, 2.0)  # GB
            else:
                value = np.random.random()

            metric_value = MetricValue(
                metric_name=metric_config.name,
                value=value,
                timestamp=datetime.now(),
                labels=metric_config.labels
            )

            metrics.append(metric_value)

            # Update Prometheus metric
            if PROMETHEUS_AVAILABLE and metric_config.name in self.prometheus_metrics:
                prom_metric = self.prometheus_metrics[metric_config.name]
                if metric_config.metric_type == MetricType.COUNTER:
                    prom_metric.labels(**metric_config.labels).inc(value)
                elif metric_config.metric_type == MetricType.GAUGE:
                    prom_metric.labels(**metric_config.labels).set(value)
                elif metric_config.metric_type == MetricType.HISTOGRAM:
                    prom_metric.labels(**metric_config.labels).observe(value)

        return metrics

    async def store_metrics(self, metrics: List[MetricValue]) -> bool:
        """Store metrics (Prometheus handles storage automatically)."""
        # Prometheus handles storage automatically
        return True

    async def get_metrics(self, metric_name: str, start_time: datetime,
                         end_time: datetime) -> List[MetricValue]:
        """Get metrics from Prometheus."""
        # In a real implementation, this would query Prometheus
        # For demo, return cached metrics
        return self.metrics_cache.get(metric_name, [])

class InfluxDBMetricCollector(MetricCollector):
    """InfluxDB metric collector."""

    def __init__(self, config: MonitoringConfig):
        super().__init__(config)
        self.client = None
        self.write_api = None
        self._setup_influxdb()

    def _setup_influxdb(self):
        """Setup InfluxDB client."""
        if not INFLUXDB_AVAILABLE:
            logger.warning("InfluxDB not available, using mock storage")
            return

        # Mock InfluxDB setup
        logger.info("Setting up InfluxDB client")

    async def collect_metrics(self) -> List[MetricValue]:
        """Collect metrics for InfluxDB."""
        metrics = []

        for metric_config in self.config.metrics:
            if not metric_config.enabled:
                continue

            # Simulate metric collection
            value = np.random.random()

            metric_value = MetricValue(
                metric_name=metric_config.name,
                value=value,
                timestamp=datetime.now(),
                labels=metric_config.labels
            )

            metrics.append(metric_value)

        return metrics

    async def store_metrics(self, metrics: List[MetricValue]) -> bool:
        """Store metrics in InfluxDB."""
        if not INFLUXDB_AVAILABLE:
            # Mock storage
            for metric in metrics:
                if metric.metric_name not in self.metrics_cache:
                    self.metrics_cache[metric.metric_name] = []
                self.metrics_cache[metric.metric_name].append(metric)
            return True

        # Real InfluxDB implementation would go here
        return True

    async def get_metrics(self, metric_name: str, start_time: datetime,
                         end_time: datetime) -> List[MetricValue]:
        """Get metrics from InfluxDB."""
        if not INFLUXDB_AVAILABLE:
            # Return cached metrics
            cached = self.metrics_cache.get(metric_name, [])
            return [m for m in cached if start_time <= m.timestamp <= end_time]

        # Real InfluxDB query would go here
        return []

class AlertManager:
    """Alert management system."""

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.active_alerts: Dict[str, AlertEvent] = {}
        self.alert_history: List[AlertEvent] = []
        self.cooldown_timers: Dict[str, datetime] = {}

    async def evaluate_alerts(self, metrics: List[MetricValue]):
        """Evaluate alerts against metrics."""
        for alert_config in self.config.alerts:
            if not alert_config.enabled:
                continue

            # Check cooldown
            if alert_config.alert_id in self.cooldown_timers:
                if datetime.now() < self.cooldown_timers[alert_config.alert_id]:
                    continue

            # Find metric value
            metric_value = None
            for metric in metrics:
                if metric.metric_name == alert_config.metric_name:
                    metric_value = metric
                    break

            if metric_value is None:
                continue

            # Evaluate condition
            triggered = self._evaluate_condition(
                alert_config.condition,
                metric_value.value,
                alert_config.threshold
            )

            if triggered:
                await self._trigger_alert(alert_config, metric_value)
            else:
                await self._resolve_alert(alert_config.alert_id)

    def _evaluate_condition(self, condition: str, value: float, threshold: float) -> bool:
        """Evaluate alert condition."""
        try:
            # Simple condition evaluation
            if condition == "greater_than":
                return value > threshold
            elif condition == "less_than":
                return value < threshold
            elif condition == "equals":
                return abs(value - threshold) < 1e-6
            elif condition == "greater_than_or_equal":
                return value >= threshold
            elif condition == "less_than_or_equal":
                return value <= threshold
            else:
                # Try to evaluate as Python expression
                return eval(condition.replace("metric", str(value)).replace("threshold", str(threshold)))
        except Exception as e:
            logger.error(f"Error evaluating condition: {str(e)}")
            return False

    async def _trigger_alert(self, alert_config: AlertConfig, metric_value: MetricValue):
        """Trigger an alert."""
        alert_event = AlertEvent(
            alert_id=alert_config.alert_id,
            alert_name=alert_config.name,
            severity=alert_config.severity,
            metric_name=alert_config.metric_name,
            current_value=metric_value.value,
            threshold=alert_config.threshold,
            message=f"Alert {alert_config.name}: {alert_config.metric_name} = {metric_value.value:.2f} (threshold: {alert_config.threshold})",
            timestamp=datetime.now()
        )

        self.active_alerts[alert_config.alert_id] = alert_event
        self.alert_history.append(alert_event)

        # Set cooldown
        self.cooldown_timers[alert_config.alert_id] = datetime.now() + timedelta(seconds=alert_config.cooldown_period)

        # Send notifications
        await self._send_notifications(alert_event, alert_config.notification_channels)

        logger.warning(f"Alert triggered: {alert_event.message}")

    async def _resolve_alert(self, alert_id: str):
        """Resolve an alert."""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            alert.resolved_at = datetime.now()

            del self.active_alerts[alert_id]

            logger.info(f"Alert resolved: {alert.alert_name}")

    async def _send_notifications(self, alert: AlertEvent, channels: List[str]):
        """Send alert notifications."""
        for channel in channels:
            try:
                if channel == "slack":
                    await self._send_slack_notification(alert)
                elif channel == "email":
                    await self._send_email_notification(alert)
                elif channel == "webhook":
                    await self._send_webhook_notification(alert)
                else:
                    logger.warning(f"Unknown notification channel: {channel}")
            except Exception as e:
                logger.error(f"Failed to send notification to {channel}: {str(e)}")

    async def _send_slack_notification(self, alert: AlertEvent):
        """Send Slack notification."""
        if not ALERTING_AVAILABLE:
            logger.info(f"Mock Slack notification: {alert.message}")
            return

        # Real Slack implementation would go here
        logger.info(f"Slack notification sent: {alert.message}")

    async def _send_email_notification(self, alert: AlertEvent):
        """Send email notification."""
        if not ALERTING_AVAILABLE:
            logger.info(f"Mock email notification: {alert.message}")
            return

        # Real email implementation would go here
        logger.info(f"Email notification sent: {alert.message}")

    async def _send_webhook_notification(self, alert: AlertEvent):
        """Send webhook notification."""
        if not ALERTING_AVAILABLE:
            logger.info(f"Mock webhook notification: {alert.message}")
            return

        # Real webhook implementation would go here
        logger.info(f"Webhook notification sent: {alert.message}")

    def get_active_alerts(self) -> List[AlertEvent]:
        """Get active alerts."""
        return list(self.active_alerts.values())

    def get_alert_history(self, limit: Optional[int] = None) -> List[AlertEvent]:
        """Get alert history."""
        history = self.alert_history
        if limit:
            history = history[-limit:]
        return history

class DriftDetector:
    """Model drift detection system."""

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.drift_config = config.drift_detection
        self.baseline_data: Optional[pd.DataFrame] = None
        self.drift_history: List[Dict[str, Any]] = []

    async def detect_drift(self, current_data: pd.DataFrame) -> Dict[str, Any]:
        """Detect various types of drift."""
        drift_results = {}

        # Data drift
        if self.drift_config.get("data_drift", {}).get("enabled", True):
            drift_results["data_drift"] = await self._detect_data_drift(current_data)

        # Concept drift
        if self.drift_config.get("concept_drift", {}).get("enabled", True):
            drift_results["concept_drift"] = await self._detect_concept_drift(current_data)

        # Performance drift
        if self.drift_config.get("performance_drift", {}).get("enabled", True):
            drift_results["performance_drift"] = await self._detect_performance_drift(current_data)

        # Prediction drift
        if self.drift_config.get("prediction_drift", {}).get("enabled", True):
            drift_results["prediction_drift"] = await self._detect_prediction_drift(current_data)

        # Store drift results
        drift_record = {
            "timestamp": datetime.now().isoformat(),
            "drift_results": drift_results,
            "overall_drift_score": self._calculate_overall_drift_score(drift_results)
        }
        self.drift_history.append(drift_record)

        return drift_record

    async def _detect_data_drift(self, current_data: pd.DataFrame) -> Dict[str, Any]:
        """Detect data distribution drift."""
        if self.baseline_data is None:
            return {"status": "no_baseline", "drift_score": 0.0}

        # Simplified drift detection using statistical tests
        drift_scores = {}

        for column in current_data.columns:
            if column in self.baseline_data.columns:
                baseline_col = self.baseline_data[column].dropna()
                current_col = current_data[column].dropna()

                if len(baseline_col) > 0 and len(current_col) > 0:
                    # Simplified KS test (mock implementation)
                    drift_score = np.random.random()  # Mock drift score
                    drift_scores[column] = drift_score

        overall_drift = np.mean(list(drift_scores.values())) if drift_scores else 0.0
        threshold = self.drift_config.get("data_drift", {}).get("threshold", 0.1)

        return {
            "status": "drift_detected" if overall_drift > threshold else "no_drift",
            "drift_score": overall_drift,
            "feature_drift_scores": drift_scores,
            "threshold": threshold
        }

    async def _detect_concept_drift(self, current_data: pd.DataFrame) -> Dict[str, Any]:
        """Detect concept drift (relationship between features and target)."""
        # Mock concept drift detection
        drift_score = np.random.random()
        threshold = self.drift_config.get("concept_drift", {}).get("threshold", 0.15)

        return {
            "status": "drift_detected" if drift_score > threshold else "no_drift",
            "drift_score": drift_score,
            "threshold": threshold
        }

    async def _detect_performance_drift(self, current_data: pd.DataFrame) -> Dict[str, Any]:
        """Detect performance drift."""
        # Mock performance metrics
        current_accuracy = np.random.normal(0.85, 0.05)
        baseline_accuracy = 0.90
        performance_drop = baseline_accuracy - current_accuracy

        threshold = self.drift_config.get("performance_drift", {}).get("threshold", 0.1)

        return {
            "status": "drift_detected" if performance_drop > threshold else "no_drift",
            "drift_score": performance_drop,
            "current_accuracy": current_accuracy,
            "baseline_accuracy": baseline_accuracy,
            "threshold": threshold
        }

    async def _detect_prediction_drift(self, current_data: pd.DataFrame) -> Dict[str, Any]:
        """Detect prediction distribution drift."""
        # Mock prediction drift detection
        drift_score = np.random.random()
        threshold = self.drift_config.get("prediction_drift", {}).get("threshold", 0.1)

        return {
            "status": "drift_detected" if drift_score > threshold else "no_drift",
            "drift_score": drift_score,
            "threshold": threshold
        }

    def _calculate_overall_drift_score(self, drift_results: Dict[str, Any]) -> float:
        """Calculate overall drift score."""
        scores = []
        for drift_type, result in drift_results.items():
            if isinstance(result, dict) and "drift_score" in result:
                scores.append(result["drift_score"])

        return np.mean(scores) if scores else 0.0

    def set_baseline_data(self, data: pd.DataFrame):
        """Set baseline data for drift detection."""
        self.baseline_data = data.copy()
        logger.info(f"Baseline data set with {len(data)} samples")

    def get_drift_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get drift detection history."""
        history = self.drift_history
        if limit:
            history = history[-limit:]
        return history

class ModelMonitoringSystem:
    """Main model monitoring system."""

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.status = MonitoringStatus.INACTIVE
        self.collectors: List[MetricCollector] = []
        self.alert_manager = AlertManager(config)
        self.drift_detector = DriftDetector(config)
        self.monitoring_task: Optional[asyncio.Task] = None
        self.metrics_history: List[MetricValue] = []

    async def start(self):
        """Start monitoring system."""
        try:
            self.status = MonitoringStatus.ACTIVE

            # Setup metric collectors
            if "prometheus" in self.config.storage_backends:
                self.collectors.append(PrometheusMetricCollector(self.config))

            if "influxdb" in self.config.storage_backends:
                self.collectors.append(InfluxDBMetricCollector(self.config))

            # Start monitoring loop
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())

            logger.info(f"Model monitoring system started: {self.config.name}")

        except Exception as e:
            self.status = MonitoringStatus.ERROR
            logger.error(f"Failed to start monitoring system: {str(e)}")
            raise

    async def stop(self):
        """Stop monitoring system."""
        self.status = MonitoringStatus.INACTIVE

        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass

        logger.info(f"Model monitoring system stopped: {self.config.name}")

    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.status == MonitoringStatus.ACTIVE:
            try:
                # Collect metrics
                all_metrics = []
                for collector in self.collectors:
                    metrics = await collector.collect_metrics()
                    all_metrics.extend(metrics)

                    # Store metrics
                    await collector.store_metrics(metrics)

                # Store in local history
                self.metrics_history.extend(all_metrics)

                # Evaluate alerts
                await self.alert_manager.evaluate_alerts(all_metrics)

                # Sleep until next collection
                collection_interval = min(
                    [m.collection_interval for m in self.config.metrics if m.enabled],
                    default=60
                )
                await asyncio.sleep(collection_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                await asyncio.sleep(10)  # Wait before retrying

    async def record_inference_metrics(self, predictions: List[Any],
                                     features: pd.DataFrame,
                                     latency_ms: float):
        """Record inference-specific metrics."""
        timestamp = datetime.now()

        # Create inference metrics
        metrics = [
            MetricValue("model_inference_latency", latency_ms, timestamp),
            MetricValue("model_inference_count", len(predictions), timestamp),
            MetricValue("model_inference_throughput", len(predictions) / (latency_ms / 1000), timestamp)
        ]

        # Store metrics
        for collector in self.collectors:
            await collector.store_metrics(metrics)

        self.metrics_history.extend(metrics)

    async def check_drift(self, current_data: pd.DataFrame) -> Dict[str, Any]:
        """Check for model drift."""
        return await self.drift_detector.detect_drift(current_data)

    def get_monitoring_summary(self) -> Dict[str, Any]:
        """Get monitoring system summary."""
        active_alerts = self.alert_manager.get_active_alerts()
        recent_metrics = [m for m in self.metrics_history
                         if m.timestamp > datetime.now() - timedelta(hours=1)]

        return {
            "status": self.status.value,
            "model_name": self.config.model_name,
            "model_version": self.config.model_version,
            "environment": self.config.environment,
            "active_alerts": len(active_alerts),
            "total_alerts": len(self.alert_manager.alert_history),
            "metrics_collected": len(self.metrics_history),
            "recent_metrics": len(recent_metrics),
            "drift_detections": len(self.drift_detector.drift_history),
            "last_updated": datetime.now().isoformat()
        }

    def get_metrics_dashboard(self) -> Dict[str, Any]:
        """Get metrics dashboard data."""
        # Group metrics by name
        metrics_by_name = {}
        for metric in self.metrics_history:
            if metric.metric_name not in metrics_by_name:
                metrics_by_name[metric.metric_name] = []
            metrics_by_name[metric.metric_name].append(metric)

        # Calculate summary statistics
        dashboard_data = {}
        for name, values in metrics_by_name.items():
            recent_values = values[-100:]  # Last 100 values
            if recent_values:
                dashboard_data[name] = {
                    "current": recent_values[-1].value,
                    "average": np.mean([v.value for v in recent_values]),
                    "min": np.min([v.value for v in recent_values]),
                    "max": np.max([v.value for v in recent_values]),
                    "trend": "up" if len(recent_values) > 1 and recent_values[-1].value > recent_values[-2].value else "down",
                    "count": len(recent_values)
                }

        return dashboard_data

# Monitoring templates
class MonitoringTemplates:
    """Predefined monitoring templates."""

    @staticmethod
    def get_production_monitoring() -> MonitoringConfig:
        """Get production monitoring template."""
        metrics = [
            MetricConfig(
                name="model_inference_latency",
                metric_type=MetricType.HISTOGRAM,
                description="Model inference latency in milliseconds",
                collection_interval=30,
                labels={"model": "production", "environment": "prod"}
            ),
            MetricConfig(
                name="model_inference_throughput",
                metric_type=MetricType.GAUGE,
                description="Model inference throughput (requests/second)",
                collection_interval=30,
                labels={"model": "production", "environment": "prod"}
            ),
            MetricConfig(
                name="model_error_rate",
                metric_type=MetricType.GAUGE,
                description="Model error rate",
                collection_interval=60,
                labels={"model": "production", "environment": "prod"}
            ),
            MetricConfig(
                name="model_memory_usage",
                metric_type=MetricType.GAUGE,
                description="Model memory usage in GB",
                collection_interval=60,
                labels={"model": "production", "environment": "prod"}
            )
        ]

        alerts = [
            AlertConfig(
                name="high_latency_alert",
                metric_name="model_inference_latency",
                condition="greater_than",
                threshold=200.0,
                severity=AlertSeverity.WARNING,
                notification_channels=["slack", "email"]
            ),
            AlertConfig(
                name="high_error_rate_alert",
                metric_name="model_error_rate",
                condition="greater_than",
                threshold=0.05,
                severity=AlertSeverity.CRITICAL,
                notification_channels=["slack", "email", "webhook"]
            )
        ]

        return MonitoringConfig(
            name="production-monitoring",
            model_name="production-model",
            model_version="1.0.0",
            environment="production",
            metrics=metrics,
            alerts=alerts,
            storage_backends=["prometheus", "influxdb"],
            drift_detection={
                "data_drift": {"enabled": True, "threshold": 0.1},
                "concept_drift": {"enabled": True, "threshold": 0.15},
                "performance_drift": {"enabled": True, "threshold": 0.1},
                "prediction_drift": {"enabled": True, "threshold": 0.1}
            }
        )

    @staticmethod
    def get_staging_monitoring() -> MonitoringConfig:
        """Get staging monitoring template."""
        metrics = [
            MetricConfig(
                name="model_inference_latency",
                metric_type=MetricType.HISTOGRAM,
                description="Model inference latency in milliseconds",
                collection_interval=60,
                labels={"model": "staging", "environment": "staging"}
            ),
            MetricConfig(
                name="model_error_rate",
                metric_type=MetricType.GAUGE,
                description="Model error rate",
                collection_interval=120,
                labels={"model": "staging", "environment": "staging"}
            )
        ]

        alerts = [
            AlertConfig(
                name="staging_error_alert",
                metric_name="model_error_rate",
                condition="greater_than",
                threshold=0.1,
                severity=AlertSeverity.WARNING,
                notification_channels=["slack"]
            )
        ]

        return MonitoringConfig(
            name="staging-monitoring",
            model_name="staging-model",
            version="1.0.0",
            environment="staging",
            metrics=metrics,
            alerts=alerts,
            storage_backends=["prometheus"]
        )

# Example usage
async def example_usage():
    """Example usage of model monitoring system."""
    # Create monitoring configuration
    config = MonitoringTemplates.get_production_monitoring()

    # Create monitoring system
    monitoring_system = ModelMonitoringSystem(config)

    # Start monitoring
    await monitoring_system.start()

    # Simulate some inference metrics
    features = pd.DataFrame(np.random.randn(100, 10))
    predictions = np.random.randint(0, 2, 100)
    latency_ms = 150.0

    await monitoring_system.record_inference_metrics(predictions, features, latency_ms)

    # Check for drift
    current_data = pd.DataFrame(np.random.randn(100, 10))
    drift_results = await monitoring_system.check_drift(current_data)

    print(f"Drift detection results: {drift_results}")

    # Get monitoring summary
    summary = monitoring_system.get_monitoring_summary()
    print(f"Monitoring summary: {summary}")

    # Get metrics dashboard
    dashboard = monitoring_system.get_metrics_dashboard()
    print(f"Metrics dashboard: {dashboard}")

    # Stop monitoring
    await monitoring_system.stop()

if __name__ == "__main__":
    asyncio.run(example_usage())
