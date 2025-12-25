"""
S.W.A.R.M. Phase 2: Advanced MLOps - Synthetic Data Monitoring System
Production-ready synthetic data monitoring and quality tracking
"""

import asyncio
import hashlib
import json
import logging
import os
import pickle
import time
import uuid
import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

import numpy as np
import pandas as pd
import yaml
from scipy import stats
from sklearn.metrics import jensen_shannon_distance

warnings.filterwarnings("ignore")

logger = logging.getLogger("raptorflow.synthetic_data_monitoring")


class MonitoringLevel(Enum):
    """Synthetic data monitoring levels."""

    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    PRODUCTION = "production"


class AlertSeverity(Enum):
    """Alert severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MetricType(Enum):
    """Types of monitoring metrics."""

    QUALITY = "quality"
    PRIVACY = "privacy"
    PERFORMANCE = "performance"
    DRIFT = "drift"
    USAGE = "usage"


@dataclass
class MonitoringConfig:
    """Configuration for synthetic data monitoring."""

    monitor_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    dataset_name: str = ""
    monitoring_level: MonitoringLevel = MonitoringLevel.STANDARD
    baseline_data: Optional[pd.DataFrame] = None
    monitoring_interval: int = 3600  # seconds
    alert_thresholds: Dict[str, float] = field(default_factory=dict)
    enabled_metrics: List[MetricType] = field(default_factory=lambda: list(MetricType))
    notification_channels: List[str] = field(default_factory=list)
    retention_days: int = 30

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "monitor_id": self.monitor_id,
            "dataset_name": self.dataset_name,
            "monitoring_level": self.monitoring_level.value,
            "monitoring_interval": self.monitoring_interval,
            "alert_thresholds": self.alert_thresholds,
            "enabled_metrics": [m.value for m in self.enabled_metrics],
            "notification_channels": self.notification_channels,
            "retention_days": self.retention_days,
        }


@dataclass
class MonitoringMetric:
    """Monitoring metric data point."""

    metric_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    monitor_id: str = ""
    metric_type: MetricType = MetricType.QUALITY
    metric_name: str = ""
    value: float = 0.0
    threshold: float = 0.0
    status: str = "normal"
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "metric_id": self.metric_id,
            "monitor_id": self.monitor_id,
            "metric_type": self.metric_type.value,
            "metric_name": self.metric_name,
            "value": self.value,
            "threshold": self.threshold,
            "status": self.status,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
        }


@dataclass
class MonitoringAlert:
    """Synthetic data monitoring alert."""

    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    monitor_id: str = ""
    metric_type: MetricType = MetricType.QUALITY
    severity: AlertSeverity = AlertSeverity.MEDIUM
    title: str = ""
    description: str = ""
    metric_value: float = 0.0
    threshold: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolution_notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "alert_id": self.alert_id,
            "monitor_id": self.monitor_id,
            "metric_type": self.metric_type.value,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "metric_value": self.metric_value,
            "threshold": self.threshold,
            "timestamp": self.timestamp.isoformat(),
            "resolved": self.resolved,
            "resolution_notes": self.resolution_notes,
        }


class QualityMetricsCollector:
    """Collector for synthetic data quality metrics."""

    def __init__(self):
        self.baseline_stats = {}

    def set_baseline(self, data: pd.DataFrame, monitor_id: str):
        """Set baseline statistics for monitoring."""
        self.baseline_stats[monitor_id] = self._calculate_baseline_stats(data)
        logger.info(f"Baseline set for monitor: {monitor_id}")

    def collect_quality_metrics(
        self, data: pd.DataFrame, monitor_id: str
    ) -> List[MonitoringMetric]:
        """Collect quality metrics for synthetic data."""
        metrics = []

        if monitor_id not in self.baseline_stats:
            logger.warning(f"No baseline found for monitor: {monitor_id}")
            return metrics

        baseline = self.baseline_stats[monitor_id]

        # Distribution similarity
        for column in data.columns:
            if column in baseline and pd.api.types.is_numeric_dtype(data[column]):
                similarity = self._calculate_distribution_similarity(
                    data[column], baseline[column]["distribution"]
                )

                metric = MonitoringMetric(
                    monitor_id=monitor_id,
                    metric_type=MetricType.QUALITY,
                    metric_name=f"distribution_similarity_{column}",
                    value=similarity,
                    threshold=0.8,
                    status=(
                        "good"
                        if similarity >= 0.8
                        else "warning" if similarity >= 0.6 else "critical"
                    ),
                    details={"column": column, "baseline_stats": baseline[column]},
                )
                metrics.append(metric)

        # Statistical similarity
        overall_similarity = self._calculate_overall_similarity(data, baseline)
        metric = MonitoringMetric(
            monitor_id=monitor_id,
            metric_type=MetricType.QUALITY,
            metric_name="overall_similarity",
            value=overall_similarity,
            threshold=0.8,
            status=(
                "good"
                if overall_similarity >= 0.8
                else "warning" if overall_similarity >= 0.6 else "critical"
            ),
        )
        metrics.append(metric)

        return metrics

    def _calculate_baseline_stats(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate baseline statistics."""
        stats = {}

        for column in data.columns:
            if pd.api.types.is_numeric_dtype(data[column]):
                column_data = data[column].dropna()

                stats[column] = {
                    "mean": column_data.mean(),
                    "std": column_data.std(),
                    "min": column_data.min(),
                    "max": column_data.max(),
                    "q25": column_data.quantile(0.25),
                    "median": column_data.median(),
                    "q75": column_data.quantile(0.75),
                    "distribution": column_data.values,
                }
            else:
                value_counts = data[column].value_counts(normalize=True)
                stats[column] = {"distribution": value_counts.to_dict()}

        return stats

    def _calculate_distribution_similarity(
        self, current: pd.Series, baseline_distribution: Any
    ) -> float:
        """Calculate distribution similarity score."""
        try:
            if isinstance(baseline_distribution, np.ndarray):
                # Numerical distribution comparison
                current_clean = current.dropna()

                if len(current_clean) == 0:
                    return 0.0

                # Kolmogorov-Smirnov test
                statistic, _ = stats.ks_2samp(current_clean, baseline_distribution)
                similarity = 1.0 - statistic

                return max(0.0, min(1.0, similarity))
            else:
                # Categorical distribution comparison
                current_counts = current.value_counts(normalize=True)

                # Calculate overlap
                all_categories = set(current_counts.index) | set(
                    baseline_distribution.keys()
                )
                overlap = 0.0

                for cat in all_categories:
                    current_prob = current_counts.get(cat, 0)
                    baseline_prob = baseline_distribution.get(cat, 0)
                    overlap += min(current_prob, baseline_prob)

                return overlap
        except:
            return 0.0

    def _calculate_overall_similarity(
        self, data: pd.DataFrame, baseline: Dict[str, Any]
    ) -> float:
        """Calculate overall similarity score."""
        similarities = []

        for column in data.columns:
            if column in baseline:
                similarity = self._calculate_distribution_similarity(
                    data[column], baseline[column]["distribution"]
                )
                similarities.append(similarity)

        return np.mean(similarities) if similarities else 0.0


class PrivacyMetricsCollector:
    """Collector for synthetic data privacy metrics."""

    def collect_privacy_metrics(
        self, original_data: pd.DataFrame, synthetic_data: pd.DataFrame, monitor_id: str
    ) -> List[MonitoringMetric]:
        """Collect privacy metrics for synthetic data."""
        metrics = []

        # Privacy score based on distance from original
        privacy_score = self._calculate_privacy_score(original_data, synthetic_data)

        metric = MonitoringMetric(
            monitor_id=monitor_id,
            metric_type=MetricType.PRIVACY,
            metric_name="privacy_score",
            value=privacy_score,
            threshold=0.7,
            status=(
                "good"
                if privacy_score >= 0.7
                else "warning" if privacy_score >= 0.5 else "critical"
            ),
            details={"method": "distance_based"},
        )
        metrics.append(metric)

        # Re-identification risk
        reid_risk = self._calculate_reidentification_risk(original_data, synthetic_data)

        metric = MonitoringMetric(
            monitor_id=monitor_id,
            metric_type=MetricType.PRIVACY,
            metric_name="reidentification_risk",
            value=reid_risk,
            threshold=0.3,
            status=(
                "good"
                if reid_risk <= 0.3
                else "warning" if reid_risk <= 0.5 else "critical"
            ),
            details={"method": "uniqueness_based"},
        )
        metrics.append(metric)

        return metrics

    def _calculate_privacy_score(
        self, original: pd.DataFrame, synthetic: pd.DataFrame
    ) -> float:
        """Calculate privacy protection score."""
        scores = []

        for column in original.columns:
            if column not in synthetic.columns:
                continue

            if pd.api.types.is_numeric_dtype(original[column]):
                # Wasserstein distance for numerical columns
                orig_clean = original[column].dropna()
                synth_clean = synthetic[column].dropna()

                if len(orig_clean) > 0 and len(synth_clean) > 0:
                    distance = stats.wasserstein_distance(orig_clean, synth_clean)
                    max_distance = orig_clean.max() - orig_clean.min()

                    if max_distance > 0:
                        normalized_distance = distance / max_distance
                        scores.append(min(normalized_distance, 1.0))

        return np.mean(scores) if scores else 0.0

    def _calculate_reidentification_risk(
        self, original: pd.DataFrame, synthetic: pd.DataFrame
    ) -> float:
        """Calculate re-identification risk."""
        # Simple risk assessment based on uniqueness
        risk_scores = []

        for column in original.columns:
            if column not in synthetic.columns:
                continue

            orig_uniqueness = original[column].nunique() / len(original)
            synth_uniqueness = synthetic[column].nunique() / len(synthetic)

            # Higher uniqueness means higher risk
            risk = (orig_uniqueness + synth_uniqueness) / 2
            risk_scores.append(risk)

        return np.mean(risk_scores) if risk_scores else 0.0


class PerformanceMetricsCollector:
    """Collector for synthetic data performance metrics."""

    def collect_performance_metrics(
        self, generation_time: float, data_size: int, monitor_id: str
    ) -> List[MonitoringMetric]:
        """Collect performance metrics for synthetic data generation."""
        metrics = []

        # Generation rate (records per second)
        generation_rate = data_size / generation_time if generation_time > 0 else 0

        metric = MonitoringMetric(
            monitor_id=monitor_id,
            metric_type=MetricType.PERFORMANCE,
            metric_name="generation_rate",
            value=generation_rate,
            threshold=1000,  # records per second
            status=(
                "good"
                if generation_rate >= 1000
                else "warning" if generation_rate >= 500 else "critical"
            ),
            details={"data_size": data_size, "generation_time": generation_time},
        )
        metrics.append(metric)

        # Memory efficiency (simplified)
        memory_efficiency = 1.0  # Placeholder for actual memory measurement

        metric = MonitoringMetric(
            monitor_id=monitor_id,
            metric_type=MetricType.PERFORMANCE,
            metric_name="memory_efficiency",
            value=memory_efficiency,
            threshold=0.8,
            status=(
                "good"
                if memory_efficiency >= 0.8
                else "warning" if memory_efficiency >= 0.6 else "critical"
            ),
        )
        metrics.append(metric)

        return metrics


class SyntheticDataMonitor:
    """Main synthetic data monitoring system."""

    def __init__(self):
        self.monitoring_configs: Dict[str, MonitoringConfig] = {}
        self.quality_collector = QualityMetricsCollector()
        self.privacy_collector = PrivacyMetricsCollector()
        self.performance_collector = PerformanceMetricsCollector()
        self.metrics_history: Dict[str, List[MonitoringMetric]] = {}
        self.alerts: Dict[str, MonitoringAlert] = {}
        self.active_monitors: Dict[str, bool] = {}

    def create_monitor(self, config: MonitoringConfig) -> str:
        """Create a new synthetic data monitor."""
        self.monitoring_configs[config.monitor_id] = config
        self.active_monitors[config.monitor_id] = False
        self.metrics_history[config.monitor_id] = []

        # Set baseline if provided
        if config.baseline_data is not None:
            self.quality_collector.set_baseline(config.baseline_data, config.monitor_id)

        logger.info(f"Created monitor: {config.monitor_id}")
        return config.monitor_id

    def start_monitoring(self, monitor_id: str) -> bool:
        """Start monitoring for a synthetic dataset."""
        if monitor_id not in self.monitoring_configs:
            raise ValueError(f"Monitor {monitor_id} not found")

        self.active_monitors[monitor_id] = True
        logger.info(f"Started monitoring: {monitor_id}")
        return True

    def stop_monitoring(self, monitor_id: str) -> bool:
        """Stop monitoring for a synthetic dataset."""
        if monitor_id not in self.monitoring_configs:
            raise ValueError(f"Monitor {monitor_id} not found")

        self.active_monitors[monitor_id] = False
        logger.info(f"Stopped monitoring: {monitor_id}")
        return True

    def monitor_synthetic_data(
        self,
        monitor_id: str,
        synthetic_data: pd.DataFrame,
        original_data: Optional[pd.DataFrame] = None,
        generation_time: Optional[float] = None,
    ) -> List[MonitoringAlert]:
        """Monitor synthetic data and generate alerts."""
        if monitor_id not in self.monitoring_configs:
            raise ValueError(f"Monitor {monitor_id} not found")

        if not self.active_monitors[monitor_id]:
            return []

        config = self.monitoring_configs[monitor_id]
        all_metrics = []
        alerts = []

        try:
            # Collect enabled metrics
            if MetricType.QUALITY in config.enabled_metrics:
                quality_metrics = self.quality_collector.collect_quality_metrics(
                    synthetic_data, monitor_id
                )
                all_metrics.extend(quality_metrics)

            if (
                MetricType.PRIVACY in config.enabled_metrics
                and original_data is not None
            ):
                privacy_metrics = self.privacy_collector.collect_privacy_metrics(
                    original_data, synthetic_data, monitor_id
                )
                all_metrics.extend(privacy_metrics)

            if (
                MetricType.PERFORMANCE in config.enabled_metrics
                and generation_time is not None
            ):
                performance_metrics = (
                    self.performance_collector.collect_performance_metrics(
                        generation_time, len(synthetic_data), monitor_id
                    )
                )
                all_metrics.extend(performance_metrics)

            # Store metrics
            self.metrics_history[monitor_id].extend(all_metrics)

            # Generate alerts
            for metric in all_metrics:
                if metric.status in ["warning", "critical"]:
                    alert = self._create_alert(metric, config)
                    alerts.append(alert)
                    self.alerts[alert.alert_id] = alert

            logger.info(
                f"Monitoring completed for {monitor_id}: {len(all_metrics)} metrics, {len(alerts)} alerts"
            )

        except Exception as e:
            logger.error(f"Monitoring failed for {monitor_id}: {str(e)}")

        return alerts

    def _create_alert(
        self, metric: MonitoringMetric, config: MonitoringConfig
    ) -> MonitoringAlert:
        """Create an alert from a metric."""
        severity = AlertSeverity.MEDIUM

        if metric.status == "critical":
            severity = AlertSeverity.HIGH
        elif metric.value < metric.threshold * 0.5:
            severity = AlertSeverity.CRITICAL

        alert = MonitoringAlert(
            monitor_id=metric.monitor_id,
            metric_type=metric.metric_type,
            severity=severity,
            title=f"{metric.metric_name} - {metric.status.upper()}",
            description=f"Metric {metric.metric_name} is {metric.status}: {metric.value:.3f} (threshold: {metric.threshold:.3f})",
            metric_value=metric.value,
            threshold=metric.threshold,
        )

        return alert

    def get_monitoring_summary(self, monitor_id: str) -> Dict[str, Any]:
        """Get monitoring summary for a dataset."""
        if monitor_id not in self.monitoring_configs:
            raise ValueError(f"Monitor {monitor_id} not found")

        config = self.monitoring_configs[monitor_id]
        metrics = self.metrics_history.get(monitor_id, [])
        active_alerts = [
            alert
            for alert in self.alerts.values()
            if alert.monitor_id == monitor_id and not alert.resolved
        ]

        # Calculate recent metrics
        recent_time = datetime.now() - timedelta(hours=24)
        recent_metrics = [m for m in metrics if m.timestamp >= recent_time]

        return {
            "monitor_id": monitor_id,
            "dataset_name": config.dataset_name,
            "is_active": self.active_monitors.get(monitor_id, False),
            "monitoring_level": config.monitoring_level.value,
            "total_metrics": len(metrics),
            "recent_metrics": len(recent_metrics),
            "active_alerts": len(active_alerts),
            "latest_metrics": {m.metric_name: m.value for m in recent_metrics[-10:]},
            "alert_summary": {
                "critical": len(
                    [a for a in active_alerts if a.severity == AlertSeverity.CRITICAL]
                ),
                "high": len(
                    [a for a in active_alerts if a.severity == AlertSeverity.HIGH]
                ),
                "medium": len(
                    [a for a in active_alerts if a.severity == AlertSeverity.MEDIUM]
                ),
                "low": len(
                    [a for a in active_alerts if a.severity == AlertSeverity.LOW]
                ),
            },
        }

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data for all monitors."""
        dashboard_data = {
            "total_monitors": len(self.monitoring_configs),
            "active_monitors": sum(
                1 for active in self.active_monitors.values() if active
            ),
            "total_alerts": len(self.alerts),
            "active_alerts": len([a for a in self.alerts.values() if not a.resolved]),
            "monitors": [],
        }

        for monitor_id in self.monitoring_configs:
            summary = self.get_monitoring_summary(monitor_id)
            dashboard_data["monitors"].append(summary)

        return dashboard_data


# Example usage
async def demonstrate_synthetic_data_monitoring():
    """Demonstrate synthetic data monitoring system."""
    print(
        "Demonstrating S.W.A.R.M. Phase 2 Advanced MLOps - Synthetic Data Monitoring..."
    )

    # Create sample original data
    np.random.seed(42)
    original_data = pd.DataFrame(
        {
            "customer_id": range(1000),
            "age": np.random.randint(18, 80, 1000),
            "income": np.random.normal(50000, 15000, 1000),
            "spending_score": np.random.uniform(1, 100, 1000),
            "gender": np.random.choice(["M", "F"], 1000),
            "region": np.random.choice(["North", "South", "East", "West"], 1000),
        }
    )

    # Create synthetic data (with some quality issues)
    synthetic_data = pd.DataFrame(
        {
            "customer_id": range(1000),
            "age": np.random.randint(20, 75, 1000),  # Slightly different range
            "income": np.random.normal(52000, 16000, 1000),  # Shifted distribution
            "spending_score": np.random.uniform(5, 95, 1000),  # Narrower range
            "gender": np.random.choice(["M", "F"], 1000),
            "region": np.random.choice(["North", "South", "East", "West"], 1000),
        }
    )

    print(f"Original data shape: {original_data.shape}")
    print(f"Synthetic data shape: {synthetic_data.shape}")

    # Create monitor
    monitor = SyntheticDataMonitor()

    # Create monitoring configuration
    config = MonitoringConfig(
        dataset_name="customer_synthetic_data",
        monitoring_level=MonitoringLevel.STANDARD,
        baseline_data=original_data,
        alert_thresholds={"quality": 0.8, "privacy": 0.7, "performance": 1000},
        enabled_metrics=[
            MetricType.QUALITY,
            MetricType.PRIVACY,
            MetricType.PERFORMANCE,
        ],
    )

    monitor_id = monitor.create_monitor(config)
    monitor.start_monitoring(monitor_id)
    print(f"\nCreated and started monitor: {monitor_id}")

    # Monitor synthetic data
    print("\nMonitoring synthetic data...")
    generation_time = 5.0  # Simulated generation time
    alerts = monitor.monitor_synthetic_data(
        monitor_id, synthetic_data, original_data, generation_time
    )

    print(f"Generated {len(alerts)} alerts")

    # Display alerts
    if alerts:
        print("\nGenerated Alerts:")
        for alert in alerts:
            print(f"  {alert.severity.value.upper()}: {alert.title}")
            print(f"    {alert.description}")
            print(
                f"    Value: {alert.metric_value:.3f} (Threshold: {alert.threshold:.3f})"
            )
    else:
        print("\nNo alerts generated")

    # Get monitoring summary
    summary = monitor.get_monitoring_summary(monitor_id)
    print(f"\nMonitoring Summary:")
    print(f"  Dataset: {summary['dataset_name']}")
    print(f"  Active: {summary['is_active']}")
    print(f"  Total metrics: {summary['total_metrics']}")
    print(f"  Active alerts: {summary['active_alerts']}")
    print(f"  Alert breakdown: {summary['alert_summary']}")

    # Get dashboard data
    dashboard = monitor.get_dashboard_data()
    print(f"\nDashboard Summary:")
    print(f"  Total monitors: {dashboard['total_monitors']}")
    print(f"  Active monitors: {dashboard['active_monitors']}")
    print(f"  Total alerts: {dashboard['total_alerts']}")
    print(f"  Active alerts: {dashboard['active_alerts']}")

    print("\nSynthetic Data Monitoring demonstration complete!")


if __name__ == "__main__":
    asyncio.run(demonstrate_synthetic_data_monitoring())
