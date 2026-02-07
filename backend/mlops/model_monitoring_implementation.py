"""
S.W.A.R.M. Phase 2: Model Monitoring Implementation
Production-ready model monitoring and observability system
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
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import yaml

# Import existing components
from model_monitoring_systems import (
    AlertManager,
    MetricCollector,
    MonitoringConfig,
    MonitoringManager,
)

logger = logging.getLogger("raptorflow.model_monitoring")


class MonitoringLevel(Enum):
    """Monitoring levels."""

    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    PRODUCTION = "production"


class AlertSeverity(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricType(Enum):
    """Metric types."""

    PERFORMANCE = "performance"
    ACCURACY = "accuracy"
    BUSINESS = "business"
    INFRASTRUCTURE = "infrastructure"
    DRIFT = "drift"
    FAIRNESS = "fairness"


@dataclass
class MonitoringMetric:
    """Individual monitoring metric."""

    metric_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    metric_type: MetricType = MetricType.PERFORMANCE
    value: float = 0.0
    unit: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    labels: Dict[str, str] = field(default_factory=dict)
    threshold: Optional[float] = None
    alert_enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "metric_id": self.metric_id,
            "name": self.name,
            "metric_type": self.metric_type.value,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat(),
            "labels": self.labels,
            "threshold": self.threshold,
            "alert_enabled": self.alert_enabled,
        }


@dataclass
class MonitoringAlert:
    """Monitoring alert."""

    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metric_name: str = ""
    severity: AlertSeverity = AlertSeverity.WARNING
    message: str = ""
    description: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "alert_id": self.alert_id,
            "metric_name": self.metric_name,
            "severity": self.severity.value,
            "message": self.message,
            "description": self.description,
            "timestamp": self.timestamp.isoformat(),
            "resolved": self.resolved,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "labels": self.labels,
            "metadata": self.metadata,
        }


@dataclass
class MonitoringConfig:
    """Enhanced monitoring configuration."""

    monitoring_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    model_name: str = ""
    model_version: str = ""
    environment: str = "production"
    monitoring_level: MonitoringLevel = MonitoringLevel.STANDARD
    collection_interval_seconds: int = 60
    retention_days: int = 30
    metrics_config: Dict[str, Any] = field(default_factory=dict)
    alerts_config: Dict[str, Any] = field(default_factory=dict)
    dashboard_config: Dict[str, Any] = field(default_factory=dict)
    notification_channels: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "monitoring_id": self.monitoring_id,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "environment": self.environment,
            "monitoring_level": self.monitoring_level.value,
            "collection_interval_seconds": self.collection_interval_seconds,
            "retention_days": self.retention_days,
            "metrics_config": self.metrics_config,
            "alerts_config": self.alerts_config,
            "dashboard_config": self.dashboard_config,
            "notification_channels": self.notification_channels,
        }


class MetricCollectorBase(ABC):
    """Abstract base class for metric collectors."""

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.is_active = False

    @abstractmethod
    async def start_collection(self):
        """Start metric collection."""
        pass

    @abstractmethod
    async def stop_collection(self):
        """Stop metric collection."""
        pass

    @abstractmethod
    async def collect_metrics(self) -> List[MonitoringMetric]:
        """Collect metrics."""
        pass


class PerformanceMetricCollector(MetricCollectorBase):
    """Performance metrics collector."""

    def __init__(self, config: MonitoringConfig):
        super().__init__(config)
        self.collection_task: Optional[asyncio.Task] = None
        self.metrics_buffer: List[MonitoringMetric] = []

    async def start_collection(self):
        """Start performance metric collection."""
        self.is_active = True
        self.collection_task = asyncio.create_task(self._collection_loop())
        logger.info("Performance metric collection started")

    async def stop_collection(self):
        """Stop performance metric collection."""
        self.is_active = False
        if self.collection_task:
            self.collection_task.cancel()
            try:
                await self.collection_task
            except asyncio.CancelledError:
                pass
        logger.info("Performance metric collection stopped")

    async def collect_metrics(self) -> List[MonitoringMetric]:
        """Collect performance metrics."""
        metrics = []

        # Simulate performance metrics collection
        current_time = datetime.now()

        # Latency metric
        latency_metric = MonitoringMetric(
            name="inference_latency",
            metric_type=MetricType.PERFORMANCE,
            value=self._simulate_latency(),
            unit="ms",
            timestamp=current_time,
            labels={
                "model": self.config.model_name,
                "environment": self.config.environment,
            },
            threshold=1000.0,
        )
        metrics.append(latency_metric)

        # Throughput metric
        throughput_metric = MonitoringMetric(
            name="inference_throughput",
            metric_type=MetricType.PERFORMANCE,
            value=self._simulate_throughput(),
            unit="requests/second",
            timestamp=current_time,
            labels={
                "model": self.config.model_name,
                "environment": self.config.environment,
            },
            threshold=100.0,
        )
        metrics.append(throughput_metric)

        # CPU usage metric
        cpu_metric = MonitoringMetric(
            name="cpu_usage",
            metric_type=MetricType.INFRASTRUCTURE,
            value=self._simulate_cpu_usage(),
            unit="percent",
            timestamp=current_time,
            labels={
                "model": self.config.model_name,
                "environment": self.config.environment,
            },
            threshold=80.0,
        )
        metrics.append(cpu_metric)

        # Memory usage metric
        memory_metric = MonitoringMetric(
            name="memory_usage",
            metric_type=MetricType.INFRASTRUCTURE,
            value=self._simulate_memory_usage(),
            unit="percent",
            timestamp=current_time,
            labels={
                "model": self.config.model_name,
                "environment": self.config.environment,
            },
            threshold=85.0,
        )
        metrics.append(memory_metric)

        return metrics

    async def _collection_loop(self):
        """Collection loop."""
        while self.is_active:
            try:
                metrics = await self.collect_metrics()
                self.metrics_buffer.extend(metrics)

                # Keep buffer size manageable
                if len(self.metrics_buffer) > 1000:
                    self.metrics_buffer = self.metrics_buffer[-500:]

                await asyncio.sleep(self.config.collection_interval_seconds)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Performance collection error: {str(e)}")
                await asyncio.sleep(self.config.collection_interval_seconds)

    def _simulate_latency(self) -> float:
        """Simulate inference latency."""
        import random

        return random.uniform(50, 1500)

    def _simulate_throughput(self) -> float:
        """Simulate inference throughput."""
        import random

        return random.uniform(50, 200)

    def _simulate_cpu_usage(self) -> float:
        """Simulate CPU usage."""
        import random

        return random.uniform(20, 90)

    def _simulate_memory_usage(self) -> float:
        """Simulate memory usage."""
        import random

        return random.uniform(30, 95)


class AccuracyMetricCollector(MetricCollectorBase):
    """Accuracy metrics collector."""

    def __init__(self, config: MonitoringConfig):
        super().__init__(config)
        self.collection_task: Optional[asyncio.Task] = None
        self.metrics_buffer: List[MonitoringMetric] = []

    async def start_collection(self):
        """Start accuracy metric collection."""
        self.is_active = True
        self.collection_task = asyncio.create_task(self._collection_loop())
        logger.info("Accuracy metric collection started")

    async def stop_collection(self):
        """Stop accuracy metric collection."""
        self.is_active = False
        if self.collection_task:
            self.collection_task.cancel()
            try:
                await self.collection_task
            except asyncio.CancelledError:
                pass
        logger.info("Accuracy metric collection stopped")

    async def collect_metrics(self) -> List[MonitoringMetric]:
        """Collect accuracy metrics."""
        metrics = []
        current_time = datetime.now()

        # Overall accuracy metric
        accuracy_metric = MonitoringMetric(
            name="model_accuracy",
            metric_type=MetricType.ACCURACY,
            value=self._simulate_accuracy(),
            unit="percent",
            timestamp=current_time,
            labels={
                "model": self.config.model_name,
                "environment": self.config.environment,
            },
            threshold=80.0,
        )
        metrics.append(accuracy_metric)

        # Precision metric
        precision_metric = MonitoringMetric(
            name="model_precision",
            metric_type=MetricType.ACCURACY,
            value=self._simulate_precision(),
            unit="percent",
            timestamp=current_time,
            labels={
                "model": self.config.model_name,
                "environment": self.config.environment,
            },
            threshold=75.0,
        )
        metrics.append(precision_metric)

        # Recall metric
        recall_metric = MonitoringMetric(
            name="model_recall",
            metric_type=MetricType.ACCURACY,
            value=self._simulate_recall(),
            unit="percent",
            timestamp=current_time,
            labels={
                "model": self.config.model_name,
                "environment": self.config.environment,
            },
            threshold=75.0,
        )
        metrics.append(recall_metric)

        return metrics

    async def _collection_loop(self):
        """Collection loop."""
        while self.is_active:
            try:
                metrics = await self.collect_metrics()
                self.metrics_buffer.extend(metrics)

                # Keep buffer size manageable
                if len(self.metrics_buffer) > 1000:
                    self.metrics_buffer = self.metrics_buffer[-500:]

                await asyncio.sleep(
                    self.config.collection_interval_seconds * 5
                )  # Less frequent

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Accuracy collection error: {str(e)}")
                await asyncio.sleep(self.config.collection_interval_seconds * 5)

    def _simulate_accuracy(self) -> float:
        """Simulate model accuracy."""
        import random

        return random.uniform(70, 95)

    def _simulate_precision(self) -> float:
        """Simulate model precision."""
        import random

        return random.uniform(65, 92)

    def _simulate_recall(self) -> float:
        """Simulate model recall."""
        import random

        return random.uniform(68, 90)


class DriftDetector:
    """Model drift detection system."""

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.baseline_metrics: Dict[str, float] = {}
        self.drift_history: List[Dict[str, Any]] = []

    def set_baseline(self, metrics: Dict[str, float]):
        """Set baseline metrics for drift detection."""
        self.baseline_metrics = metrics
        logger.info(f"Baseline metrics set: {list(metrics.keys())}")

    async def detect_drift(self, current_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Detect model drift."""
        drift_result = {
            "timestamp": datetime.now(),
            "drift_detected": False,
            "drift_score": 0.0,
            "drifted_metrics": [],
            "analysis": {},
        }

        if not self.baseline_metrics:
            return drift_result

        total_drift = 0.0
        metric_count = 0

        for metric_name, current_value in current_metrics.items():
            if metric_name in self.baseline_metrics:
                baseline_value = self.baseline_metrics[metric_name]

                # Calculate relative change
                if baseline_value != 0:
                    relative_change = (
                        abs(current_value - baseline_value) / baseline_value
                    )
                else:
                    relative_change = abs(current_value)

                # Drift threshold (typically 10-20% change)
                drift_threshold = 0.15

                if relative_change > drift_threshold:
                    drift_result["drifted_metrics"].append(
                        {
                            "metric": metric_name,
                            "baseline": baseline_value,
                            "current": current_value,
                            "relative_change": relative_change,
                        }
                    )
                    drift_result["drift_detected"] = True

                total_drift += relative_change
                metric_count += 1

        # Calculate overall drift score
        if metric_count > 0:
            drift_result["drift_score"] = total_drift / metric_count

        # Add analysis
        drift_result["analysis"] = {
            "drifted_metric_count": len(drift_result["drifted_metrics"]),
            "total_metrics_analyzed": metric_count,
            "drift_percentage": (
                len(drift_result["drifted_metrics"]) / metric_count
                if metric_count > 0
                else 0
            ),
        }

        self.drift_history.append(drift_result)
        return drift_result

    def get_drift_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get drift summary for the last N days."""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_drifts = [
            drift for drift in self.drift_history if drift["timestamp"] > cutoff_date
        ]

        if not recent_drifts:
            return {
                "period_days": days,
                "total_checks": 0,
                "drift_detected_count": 0,
                "drift_rate": 0.0,
                "average_drift_score": 0.0,
            }

        drift_detected_count = len([d for d in recent_drifts if d["drift_detected"]])
        average_drift_score = sum(d["drift_score"] for d in recent_drifts) / len(
            recent_drifts
        )

        return {
            "period_days": days,
            "total_checks": len(recent_drifts),
            "drift_detected_count": drift_detected_count,
            "drift_rate": drift_detected_count / len(recent_drifts),
            "average_drift_score": average_drift_score,
        }


class AlertEngine:
    """Alert generation and management engine."""

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.alerts: List[MonitoringAlert] = []
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        self.notification_handlers: Dict[str, Callable] = {}
        self._setup_default_rules()

    def _setup_default_rules(self):
        """Setup default alert rules."""
        self.alert_rules = {
            "high_latency": {
                "metric": "inference_latency",
                "condition": "greater_than",
                "threshold": 1000.0,
                "severity": "warning",
                "message": "High inference latency detected",
            },
            "low_accuracy": {
                "metric": "model_accuracy",
                "condition": "less_than",
                "threshold": 80.0,
                "severity": "error",
                "message": "Model accuracy below threshold",
            },
            "high_cpu": {
                "metric": "cpu_usage",
                "condition": "greater_than",
                "threshold": 85.0,
                "severity": "warning",
                "message": "High CPU usage detected",
            },
            "high_memory": {
                "metric": "memory_usage",
                "condition": "greater_than",
                "threshold": 90.0,
                "severity": "critical",
                "message": "High memory usage detected",
            },
        }

    async def evaluate_metrics(
        self, metrics: List[MonitoringMetric]
    ) -> List[MonitoringAlert]:
        """Evaluate metrics against alert rules and generate alerts."""
        new_alerts = []

        for metric in metrics:
            rule = self.alert_rules.get(metric.name)
            if not rule or not metric.alert_enabled:
                continue

            should_alert = self._evaluate_condition(metric.value, rule)

            if should_alert:
                alert = MonitoringAlert(
                    metric_name=metric.name,
                    severity=AlertSeverity(rule["severity"]),
                    message=rule["message"],
                    description=f"Metric {metric.name} value {metric.value} {metric.unit} {rule['condition']} threshold {rule['threshold']}",
                    labels=metric.labels,
                    metadata={
                        "metric_value": metric.value,
                        "threshold": rule["threshold"],
                        "condition": rule["condition"],
                    },
                )

                new_alerts.append(alert)
                self.alerts.append(alert)

                # Send notifications
                await self._send_notifications(alert)

        return new_alerts

    def _evaluate_condition(self, value: float, rule: Dict[str, Any]) -> bool:
        """Evaluate metric condition."""
        condition = rule["condition"]
        threshold = rule["threshold"]

        if condition == "greater_than":
            return value > threshold
        elif condition == "less_than":
            return value < threshold
        elif condition == "greater_equal":
            return value >= threshold
        elif condition == "less_equal":
            return value <= threshold
        elif condition == "equal":
            return value == threshold
        elif condition == "not_equal":
            return value != threshold

        return False

    async def _send_notifications(self, alert: MonitoringAlert):
        """Send alert notifications."""
        for channel in self.config.notification_channels:
            handler = self.notification_handlers.get(channel)
            if handler:
                try:
                    await handler(alert)
                except Exception as e:
                    logger.error(f"Failed to send alert to {channel}: {str(e)}")

    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert."""
        for alert in self.alerts:
            if alert.alert_id == alert_id and not alert.resolved:
                alert.resolved = True
                alert.resolved_at = datetime.now()
                return True
        return False

    def get_active_alerts(self) -> List[MonitoringAlert]:
        """Get active (unresolved) alerts."""
        return [alert for alert in self.alerts if not alert.resolved]

    def get_alert_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get alert summary for the last N hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_alerts = [
            alert for alert in self.alerts if alert.timestamp > cutoff_time
        ]

        severity_counts = {}
        for severity in AlertSeverity:
            severity_counts[severity.value] = len(
                [alert for alert in recent_alerts if alert.severity == severity]
            )

        return {
            "period_hours": hours,
            "total_alerts": len(recent_alerts),
            "active_alerts": len(self.get_active_alerts()),
            "severity_breakdown": severity_counts,
        }


class ModelMonitoringSystem:
    """Main model monitoring system."""

    def __init__(self):
        self.monitoring_configs: Dict[str, MonitoringConfig] = {}
        self.metric_collectors: Dict[str, List[MetricCollectorBase]] = {}
        self.drift_detectors: Dict[str, DriftDetector] = {}
        self.alert_engines: Dict[str, AlertEngine] = {}
        self.active_monitoring: Dict[str, bool] = {}

    def create_monitoring_config(
        self,
        model_name: str,
        model_version: str,
        environment: str = "production",
        level: MonitoringLevel = MonitoringLevel.STANDARD,
    ) -> MonitoringConfig:
        """Create monitoring configuration."""
        config = MonitoringConfig(
            model_name=model_name,
            model_version=model_version,
            environment=environment,
            monitoring_level=level,
        )

        # Configure metrics based on level
        if level == MonitoringLevel.BASIC:
            config.collection_interval_seconds = 300  # 5 minutes
            config.metrics_config = {
                "performance": True,
                "accuracy": False,
                "drift": False,
                "fairness": False,
            }
        elif level == MonitoringLevel.STANDARD:
            config.collection_interval_seconds = 60  # 1 minute
            config.metrics_config = {
                "performance": True,
                "accuracy": True,
                "drift": False,
                "fairness": False,
            }
        elif level == MonitoringLevel.COMPREHENSIVE:
            config.collection_interval_seconds = 30  # 30 seconds
            config.metrics_config = {
                "performance": True,
                "accuracy": True,
                "drift": True,
                "fairness": True,
            }
        elif level == MonitoringLevel.PRODUCTION:
            config.collection_interval_seconds = 15  # 15 seconds
            config.metrics_config = {
                "performance": True,
                "accuracy": True,
                "drift": True,
                "fairness": True,
                "business": True,
            }

        # Configure alerts
        config.alerts_config = {
            "enabled": True,
            "notification_channels": ["email", "slack"],
        }

        return config

    async def start_monitoring(self, config: MonitoringConfig) -> str:
        """Start monitoring for a model."""
        monitoring_id = config.monitoring_id
        self.monitoring_configs[monitoring_id] = config

        # Initialize components
        self.metric_collectors[monitoring_id] = []
        self.drift_detectors[monitoring_id] = DriftDetector(config)
        self.alert_engines[monitoring_id] = AlertEngine(config)

        # Setup metric collectors based on configuration
        if config.metrics_config.get("performance", True):
            perf_collector = PerformanceMetricCollector(config)
            self.metric_collectors[monitoring_id].append(perf_collector)

        if config.metrics_config.get("accuracy", False):
            acc_collector = AccuracyMetricCollector(config)
            self.metric_collectors[monitoring_id].append(acc_collector)

        # Start all collectors
        for collector in self.metric_collectors[monitoring_id]:
            await collector.start_collection()

        self.active_monitoring[monitoring_id] = True
        logger.info(
            f"Started monitoring for {config.model_name} v{config.model_version}"
        )

        return monitoring_id

    async def stop_monitoring(self, monitoring_id: str) -> bool:
        """Stop monitoring for a model."""
        if monitoring_id not in self.active_monitoring:
            return False

        # Stop all collectors
        for collector in self.metric_collectors.get(monitoring_id, []):
            await collector.stop_collection()

        self.active_monitoring[monitoring_id] = False
        logger.info(f"Stopped monitoring for {monitoring_id}")
        return True

    async def get_metrics(
        self,
        monitoring_id: str,
        metric_type: Optional[MetricType] = None,
        hours: int = 24,
    ) -> List[MonitoringMetric]:
        """Get metrics for a monitoring instance."""
        if monitoring_id not in self.metric_collectors:
            return []

        cutoff_time = datetime.now() - timedelta(hours=hours)
        all_metrics = []

        for collector in self.metric_collectors[monitoring_id]:
            if hasattr(collector, "metrics_buffer"):
                metrics = [
                    metric
                    for metric in collector.metrics_buffer
                    if metric.timestamp > cutoff_time
                ]

                if metric_type:
                    metrics = [m for m in metrics if m.metric_type == metric_type]

                all_metrics.extend(metrics)

        # Sort by timestamp
        all_metrics.sort(key=lambda m: m.timestamp, reverse=True)
        return all_metrics

    async def get_alerts(
        self, monitoring_id: str, active_only: bool = True, hours: int = 24
    ) -> List[MonitoringAlert]:
        """Get alerts for a monitoring instance."""
        if monitoring_id not in self.alert_engines:
            return []

        alert_engine = self.alert_engines[monitoring_id]

        if active_only:
            return alert_engine.get_active_alerts()

        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [alert for alert in alert_engine.alerts if alert.timestamp > cutoff_time]

    async def get_drift_report(
        self, monitoring_id: str, days: int = 7
    ) -> Dict[str, Any]:
        """Get drift report for a monitoring instance."""
        if monitoring_id not in self.drift_detectors:
            return {}

        drift_detector = self.drift_detectors[monitoring_id]
        return drift_detector.get_drift_summary(days)

    def get_monitoring_summary(self) -> Dict[str, Any]:
        """Get overall monitoring summary."""
        total_monitoring = len(self.active_monitoring)
        active_monitoring = sum(
            1 for active in self.active_monitoring.values() if active
        )

        total_alerts = 0
        active_alerts = 0

        for alert_engine in self.alert_engines.values():
            total_alerts += len(alert_engine.alerts)
            active_alerts += len(alert_engine.get_active_alerts())

        return {
            "total_monitoring_instances": total_monitoring,
            "active_monitoring_instances": active_monitoring,
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
        }


# Monitoring templates
class MonitoringTemplates:
    """Predefined monitoring templates."""

    @staticmethod
    def get_production_monitoring_config(
        model_name: str, model_version: str
    ) -> MonitoringConfig:
        """Get production monitoring configuration."""
        system = ModelMonitoringSystem()
        return system.create_monitoring_config(
            model_name=model_name,
            model_version=model_version,
            environment="production",
            level=MonitoringLevel.PRODUCTION,
        )

    @staticmethod
    def get_staging_monitoring_config(
        model_name: str, model_version: str
    ) -> MonitoringConfig:
        """Get staging monitoring configuration."""
        system = ModelMonitoringSystem()
        return system.create_monitoring_config(
            model_name=model_name,
            model_version=model_version,
            environment="staging",
            level=MonitoringLevel.STANDARD,
        )

    @staticmethod
    def get_development_monitoring_config(
        model_name: str, model_version: str
    ) -> MonitoringConfig:
        """Get development monitoring configuration."""
        system = ModelMonitoringSystem()
        return system.create_monitoring_config(
            model_name=model_name,
            model_version=model_version,
            environment="development",
            level=MonitoringLevel.BASIC,
        )


# Example usage
async def example_usage():
    """Example usage of model monitoring system."""
    # Create monitoring system
    monitoring_system = ModelMonitoringSystem()

    # Create production monitoring config
    prod_config = MonitoringTemplates.get_production_monitoring_config(
        "image-classifier", "1.0.0"
    )

    # Start monitoring
    monitoring_id = await monitoring_system.start_monitoring(prod_config)

    # Let monitoring run for a bit
    await asyncio.sleep(10)

    # Get metrics
    metrics = await monitoring_system.get_metrics(monitoring_id, hours=1)
    print(f"Collected {len(metrics)} metrics")

    # Get alerts
    alerts = await monitoring_system.get_alerts(monitoring_id, active_only=True)
    print(f"Active alerts: {len(alerts)}")

    # Get monitoring summary
    summary = monitoring_system.get_monitoring_summary()
    print(f"Monitoring summary: {summary}")

    # Stop monitoring
    await monitoring_system.stop_monitoring(monitoring_id)


if __name__ == "__main__":
    asyncio.run(example_usage())
