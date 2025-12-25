"""
S.W.A.R.M. Phase 2: Advanced MLOps - Feature Monitoring System
Production-ready feature monitoring and drift detection
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
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

logger = logging.getLogger("raptorflow.feature_monitoring")


class MonitoringLevel(Enum):
    """Feature monitoring levels."""

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


class DriftType(Enum):
    """Types of data drift."""

    DISTRIBUTION_DRIFT = "distribution_drift"
    CONCEPT_DRIFT = "concept_drift"
    FEATURE_DRIFT = "feature_drift"
    STATISTICAL_DRIFT = "statistical_drift"


@dataclass
class FeatureMonitorConfig:
    """Feature monitoring configuration."""

    monitor_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    feature_name: str = ""
    monitoring_level: MonitoringLevel = MonitoringLevel.STANDARD
    baseline_data: Optional[pd.DataFrame] = None
    monitoring_window: int = 24  # hours
    alert_thresholds: Dict[str, float] = field(default_factory=dict)
    drift_detection_methods: List[str] = field(
        default_factory=lambda: ["ks_test", "psi"]
    )
    auto_retrain: bool = False
    notification_channels: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "monitor_id": self.monitor_id,
            "feature_name": self.feature_name,
            "monitoring_level": self.monitoring_level.value,
            "monitoring_window": self.monitoring_window,
            "alert_thresholds": self.alert_thresholds,
            "drift_detection_methods": self.drift_detection_methods,
            "auto_retrain": self.auto_retrain,
            "notification_channels": self.notification_channels,
        }


@dataclass
class DriftAlert:
    """Feature drift alert."""

    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    feature_name: str = ""
    drift_type: DriftType = DriftType.FEATURE_DRIFT
    severity: AlertSeverity = AlertSeverity.MEDIUM
    drift_score: float = 0.0
    threshold: float = 0.0
    detection_method: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    description: str = ""
    recommendations: List[str] = field(default_factory=list)
    resolved: bool = False
    resolution_notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "alert_id": self.alert_id,
            "feature_name": self.feature_name,
            "drift_type": self.drift_type.value,
            "severity": self.severity.value,
            "drift_score": self.drift_score,
            "threshold": self.threshold,
            "detection_method": self.detection_method,
            "timestamp": self.timestamp.isoformat(),
            "description": self.description,
            "recommendations": self.recommendations,
            "resolved": self.resolved,
            "resolution_notes": self.resolution_notes,
        }


@dataclass
class FeatureMetrics:
    """Feature metrics snapshot."""

    feature_name: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    data_points: int = 0
    null_count: int = 0
    null_percentage: float = 0.0
    unique_count: int = 0
    mean: float = 0.0
    std: float = 0.0
    min_val: float = 0.0
    max_val: float = 0.0
    q25: float = 0.0
    median: float = 0.0
    q75: float = 0.0
    skewness: float = 0.0
    kurtosis: float = 0.0
    distribution_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "feature_name": self.feature_name,
            "timestamp": self.timestamp.isoformat(),
            "data_points": self.data_points,
            "null_count": self.null_count,
            "null_percentage": self.null_percentage,
            "unique_count": self.unique_count,
            "mean": self.mean,
            "std": self.std,
            "min_val": self.min_val,
            "max_val": self.max_val,
            "q25": self.q25,
            "median": self.median,
            "q75": self.q75,
            "skewness": self.skewness,
            "kurtosis": self.kurtosis,
            "distribution_hash": self.distribution_hash,
        }


class DriftDetector:
    """Statistical drift detection methods."""

    def __init__(self):
        self.detection_methods = {
            "ks_test": self._ks_test_drift,
            "psi": self._population_stability_index,
            "wasserstein": self._wasserstein_distance,
            "kl_divergence": self._kl_divergence,
            "jensen_shannon": self._jensen_shannon_distance,
            "anderson_darling": self._anderson_darling_test,
            "cramer_von_mises": self._cramer_von_mises_test,
        }

    def detect_drift(
        self,
        baseline_data: pd.Series,
        current_data: pd.Series,
        method: str = "ks_test",
        threshold: float = 0.05,
    ) -> Dict[str, Any]:
        """Detect drift using specified method."""
        if method not in self.detection_methods:
            raise ValueError(f"Unknown drift detection method: {method}")

        return self.detection_methods[method](baseline_data, current_data, threshold)

    def _ks_test_drift(
        self, baseline: pd.Series, current: pd.Series, threshold: float
    ) -> Dict[str, Any]:
        """Kolmogorov-Smirnov test for drift detection."""
        try:
            # Remove NaN values
            baseline_clean = baseline.dropna()
            current_clean = current.dropna()

            if len(baseline_clean) == 0 or len(current_clean) == 0:
                return {"drift_detected": False, "score": 0.0, "p_value": 1.0}

            statistic, p_value = stats.ks_2samp(baseline_clean, current_clean)
            drift_detected = p_value < threshold

            return {
                "drift_detected": drift_detected,
                "score": float(statistic),
                "p_value": float(p_value),
                "threshold": threshold,
                "method": "ks_test",
            }
        except Exception as e:
            logger.error(f"KS test failed: {str(e)}")
            return {"drift_detected": False, "score": 0.0, "error": str(e)}

    def _population_stability_index(
        self, baseline: pd.Series, current: pd.Series, threshold: float, bins: int = 10
    ) -> Dict[str, Any]:
        """Population Stability Index (PSI) for drift detection."""
        try:
            # Remove NaN values
            baseline_clean = baseline.dropna()
            current_clean = current.dropna()

            if len(baseline_clean) == 0 or len(current_clean) == 0:
                return {"drift_detected": False, "score": 0.0, "psi": 0.0}

            # Create bins
            min_val = min(baseline_clean.min(), current_clean.min())
            max_val = max(baseline_clean.max(), current_clean.max())

            if min_val == max_val:
                return {"drift_detected": False, "score": 0.0, "psi": 0.0}

            bin_edges = np.linspace(min_val, max_val, bins + 1)

            # Calculate frequencies
            baseline_hist, _ = np.histogram(baseline_clean, bins=bin_edges)
            current_hist, _ = np.histogram(current_clean, bins=bin_edges)

            # Normalize to get percentages
            baseline_pct = baseline_hist / len(baseline_clean)
            current_pct = current_hist / len(current_clean)

            # Calculate PSI
            psi = 0.0
            for i in range(len(baseline_pct)):
                if baseline_pct[i] > 0 and current_pct[i] > 0:
                    psi += (current_pct[i] - baseline_pct[i]) * np.log(
                        current_pct[i] / baseline_pct[i]
                    )

            drift_detected = psi > threshold

            return {
                "drift_detected": drift_detected,
                "score": float(psi),
                "psi": float(psi),
                "threshold": threshold,
                "method": "psi",
            }
        except Exception as e:
            logger.error(f"PSI calculation failed: {str(e)}")
            return {"drift_detected": False, "score": 0.0, "error": str(e)}

    def _wasserstein_distance(
        self, baseline: pd.Series, current: pd.Series, threshold: float
    ) -> Dict[str, Any]:
        """Wasserstein distance for drift detection."""
        try:
            baseline_clean = baseline.dropna()
            current_clean = current.dropna()

            if len(baseline_clean) == 0 or len(current_clean) == 0:
                return {"drift_detected": False, "score": 0.0}

            distance = stats.wasserstein_distance(baseline_clean, current_clean)

            # Normalize distance by range
            data_range = max(baseline_clean.max(), current_clean.max()) - min(
                baseline_clean.min(), current_clean.min()
            )
            normalized_distance = distance / data_range if data_range > 0 else 0

            drift_detected = normalized_distance > threshold

            return {
                "drift_detected": drift_detected,
                "score": float(normalized_distance),
                "raw_distance": float(distance),
                "threshold": threshold,
                "method": "wasserstein",
            }
        except Exception as e:
            logger.error(f"Wasserstein distance failed: {str(e)}")
            return {"drift_detected": False, "score": 0.0, "error": str(e)}

    def _kl_divergence(
        self, baseline: pd.Series, current: pd.Series, threshold: float
    ) -> Dict[str, Any]:
        """Kullback-Leibler divergence for drift detection."""
        try:
            baseline_clean = baseline.dropna()
            current_clean = current.dropna()

            if len(baseline_clean) == 0 or len(current_clean) == 0:
                return {"drift_detected": False, "score": 0.0}

            # Create histograms
            bins = min(50, max(10, int(np.sqrt(len(baseline_clean)))))
            baseline_hist, bin_edges = np.histogram(
                baseline_clean, bins=bins, density=True
            )
            current_hist, _ = np.histogram(current_clean, bins=bin_edges, density=True)

            # Add small epsilon to avoid division by zero
            epsilon = 1e-10
            baseline_hist = baseline_hist + epsilon
            current_hist = current_hist + epsilon

            # Calculate KL divergence
            kl_div = np.sum(baseline_hist * np.log(baseline_hist / current_hist))

            drift_detected = kl_div > threshold

            return {
                "drift_detected": drift_detected,
                "score": float(kl_div),
                "threshold": threshold,
                "method": "kl_divergence",
            }
        except Exception as e:
            logger.error(f"KL divergence failed: {str(e)}")
            return {"drift_detected": False, "score": 0.0, "error": str(e)}

    def _jensen_shannon_distance(
        self, baseline: pd.Series, current: pd.Series, threshold: float
    ) -> Dict[str, Any]:
        """Jensen-Shannon distance for drift detection."""
        try:
            baseline_clean = baseline.dropna()
            current_clean = current.dropna()

            if len(baseline_clean) == 0 or len(current_clean) == 0:
                return {"drift_detected": False, "score": 0.0}

            # Create histograms
            bins = min(50, max(10, int(np.sqrt(len(baseline_clean)))))
            baseline_hist, bin_edges = np.histogram(
                baseline_clean, bins=bins, density=True
            )
            current_hist, _ = np.histogram(current_clean, bins=bin_edges, density=True)

            # Calculate Jensen-Shannon distance
            m = 0.5 * (baseline_hist + current_hist)
            js_distance = np.sqrt(
                0.5 * stats.entropy(baseline_hist, m)
                + 0.5 * stats.entropy(current_hist, m)
            )

            drift_detected = js_distance > threshold

            return {
                "drift_detected": drift_detected,
                "score": float(js_distance),
                "threshold": threshold,
                "method": "jensen_shannon",
            }
        except Exception as e:
            logger.error(f"Jensen-Shannon distance failed: {str(e)}")
            return {"drift_detected": False, "score": 0.0, "error": str(e)}

    def _anderson_darling_test(
        self, baseline: pd.Series, current: pd.Series, threshold: float
    ) -> Dict[str, Any]:
        """Anderson-Darling test for drift detection."""
        try:
            baseline_clean = baseline.dropna()
            current_clean = current.dropna()

            if len(baseline_clean) == 0 or len(current_clean) == 0:
                return {"drift_detected": False, "score": 0.0}

            # Combine data for testing
            combined = np.concatenate([baseline_clean, current_clean])

            # Perform Anderson-Darling test
            statistic, critical_values, significance_level = stats.anderson(combined)

            # Use the first critical value (5% significance level)
            drift_detected = statistic > critical_values[0]

            return {
                "drift_detected": drift_detected,
                "score": float(statistic),
                "critical_value": float(critical_values[0]),
                "threshold": threshold,
                "method": "anderson_darling",
            }
        except Exception as e:
            logger.error(f"Anderson-Darling test failed: {str(e)}")
            return {"drift_detected": False, "score": 0.0, "error": str(e)}

    def _cramer_von_mises_test(
        self, baseline: pd.Series, current: pd.Series, threshold: float
    ) -> Dict[str, Any]:
        """Cramér-von Mises test for drift detection."""
        try:
            baseline_clean = baseline.dropna()
            current_clean = current.dropna()

            if len(baseline_clean) == 0 or len(current_clean) == 0:
                return {"drift_detected": False, "score": 0.0}

            statistic, p_value = stats.cramervonmises_2samp(
                baseline_clean, current_clean
            )
            drift_detected = p_value < threshold

            return {
                "drift_detected": drift_detected,
                "score": float(statistic),
                "p_value": float(p_value),
                "threshold": threshold,
                "method": "cramer_von_mises",
            }
        except Exception as e:
            logger.error(f"Cramér-von Mises test failed: {str(e)}")
            return {"drift_detected": False, "score": 0.0, "error": str(e)}


class FeatureMetricsCollector:
    """Feature metrics collection and storage."""

    def __init__(self):
        self.metrics_history: Dict[str, List[FeatureMetrics]] = {}
        self.baseline_metrics: Dict[str, FeatureMetrics] = {}

    def collect_metrics(self, data: pd.Series, feature_name: str) -> FeatureMetrics:
        """Collect comprehensive metrics for a feature."""
        clean_data = data.dropna()

        if len(clean_data) == 0:
            return FeatureMetrics(feature_name=feature_name)

        # Calculate basic statistics
        metrics = FeatureMetrics(
            feature_name=feature_name,
            data_points=len(data),
            null_count=data.isnull().sum(),
            null_percentage=data.isnull().sum() / len(data) * 100,
            unique_count=data.nunique(),
            mean=(
                float(clean_data.mean()) if pd.api.types.is_numeric_dtype(data) else 0.0
            ),
            std=float(clean_data.std()) if pd.api.types.is_numeric_dtype(data) else 0.0,
            min_val=(
                float(clean_data.min()) if pd.api.types.is_numeric_dtype(data) else 0.0
            ),
            max_val=(
                float(clean_data.max()) if pd.api.types.is_numeric_dtype(data) else 0.0
            ),
            q25=(
                float(clean_data.quantile(0.25))
                if pd.api.types.is_numeric_dtype(data)
                else 0.0
            ),
            median=(
                float(clean_data.median())
                if pd.api.types.is_numeric_dtype(data)
                else 0.0
            ),
            q75=(
                float(clean_data.quantile(0.75))
                if pd.api.types.is_numeric_dtype(data)
                else 0.0
            ),
            skewness=(
                float(clean_data.skew()) if pd.api.types.is_numeric_dtype(data) else 0.0
            ),
            kurtosis=(
                float(clean_data.kurtosis())
                if pd.api.types.is_numeric_dtype(data)
                else 0.0
            ),
        )

        # Calculate distribution hash for change detection
        if pd.api.types.is_numeric_dtype(data):
            hist, _ = np.histogram(clean_data, bins=50)
            metrics.distribution_hash = hashlib.md5(hist.tobytes()).hexdigest()

        # Store in history
        if feature_name not in self.metrics_history:
            self.metrics_history[feature_name] = []
        self.metrics_history[feature_name].append(metrics)

        # Keep only last 1000 entries per feature
        if len(self.metrics_history[feature_name]) > 1000:
            self.metrics_history[feature_name] = self.metrics_history[feature_name][
                -1000:
            ]

        return metrics

    def set_baseline(self, data: pd.Series, feature_name: str):
        """Set baseline metrics for a feature."""
        self.baseline_metrics[feature_name] = self.collect_metrics(data, feature_name)
        logger.info(f"Baseline set for feature: {feature_name}")

    def get_metrics_history(
        self, feature_name: str, hours: int = 24
    ) -> List[FeatureMetrics]:
        """Get metrics history for a feature within time window."""
        if feature_name not in self.metrics_history:
            return []

        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            m for m in self.metrics_history[feature_name] if m.timestamp >= cutoff_time
        ]

    def get_baseline_metrics(self, feature_name: str) -> Optional[FeatureMetrics]:
        """Get baseline metrics for a feature."""
        return self.baseline_metrics.get(feature_name)


class AlertManager:
    """Alert management and notification system."""

    def __init__(self):
        self.active_alerts: Dict[str, DriftAlert] = {}
        self.alert_history: List[DriftAlert] = []
        self.notification_handlers: Dict[str, Callable] = {}

    def create_alert(
        self,
        feature_name: str,
        drift_result: Dict[str, Any],
        severity: AlertSeverity = AlertSeverity.MEDIUM,
    ) -> DriftAlert:
        """Create a new drift alert."""
        alert = DriftAlert(
            feature_name=feature_name,
            drift_type=DriftType.FEATURE_DRIFT,
            severity=severity,
            drift_score=drift_result.get("score", 0.0),
            threshold=drift_result.get("threshold", 0.0),
            detection_method=drift_result.get("method", "unknown"),
            description=f"Drift detected in feature {feature_name} using {drift_result.get('method', 'unknown')}",
            recommendations=self._generate_recommendations(drift_result),
        )

        self.active_alerts[alert.alert_id] = alert
        self.alert_history.append(alert)

        logger.warning(f"Alert created: {alert.alert_id} for feature {feature_name}")

        # Send notifications
        self._send_notifications(alert)

        return alert

    def resolve_alert(self, alert_id: str, resolution_notes: str = ""):
        """Resolve an alert."""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            alert.resolution_notes = resolution_notes

            # Move from active to history
            del self.active_alerts[alert_id]

            logger.info(f"Alert resolved: {alert_id}")

    def get_active_alerts(self, feature_name: Optional[str] = None) -> List[DriftAlert]:
        """Get active alerts."""
        alerts = list(self.active_alerts.values())

        if feature_name:
            alerts = [a for a in alerts if a.feature_name == feature_name]

        return alerts

    def get_alert_history(
        self, hours: int = 24, feature_name: Optional[str] = None
    ) -> List[DriftAlert]:
        """Get alert history within time window."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        alerts = [a for a in self.alert_history if a.timestamp >= cutoff_time]

        if feature_name:
            alerts = [a for a in alerts if a.feature_name == feature_name]

        return alerts

    def _generate_recommendations(self, drift_result: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on drift detection results."""
        recommendations = []

        score = drift_result.get("score", 0.0)
        method = drift_result.get("method", "")

        if score > 0.8:
            recommendations.append(
                "Immediate investigation required - high drift detected"
            )
            recommendations.append("Consider retraining the model with recent data")
        elif score > 0.5:
            recommendations.append("Monitor closely - moderate drift detected")
            recommendations.append("Schedule model retraining in near future")
        else:
            recommendations.append("Continue monitoring - low drift detected")

        if method == "psi":
            recommendations.append("Review feature engineering and preprocessing")
        elif method == "ks_test":
            recommendations.append("Check for data quality issues")

        return recommendations

    def _send_notifications(self, alert: DriftAlert):
        """Send notifications for alert."""
        for handler_name, handler in self.notification_handlers.items():
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Notification handler {handler_name} failed: {str(e)}")

    def register_notification_handler(self, name: str, handler: Callable):
        """Register a notification handler."""
        self.notification_handlers[name] = handler


class FeatureMonitoringSystem:
    """Main feature monitoring system orchestrator."""

    def __init__(self):
        self.drift_detector = DriftDetector()
        self.metrics_collector = FeatureMetricsCollector()
        self.alert_manager = AlertManager()
        self.monitoring_configs: Dict[str, FeatureMonitorConfig] = {}
        self.monitoring_status: Dict[str, bool] = {}

    def create_monitor(self, config: FeatureMonitorConfig) -> str:
        """Create a new feature monitor."""
        self.monitoring_configs[config.monitor_id] = config
        self.monitoring_status[config.monitor_id] = False

        # Set baseline if provided
        if (
            config.baseline_data is not None
            and config.feature_name in config.baseline_data.columns
        ):
            self.metrics_collector.set_baseline(
                config.baseline_data[config.feature_name], config.feature_name
            )

        logger.info(f"Created monitor for feature: {config.feature_name}")
        return config.monitor_id

    def start_monitoring(self, monitor_id: str) -> bool:
        """Start monitoring for a feature."""
        if monitor_id not in self.monitoring_configs:
            raise ValueError(f"Monitor {monitor_id} not found")

        self.monitoring_status[monitor_id] = True
        logger.info(f"Started monitoring: {monitor_id}")
        return True

    def stop_monitoring(self, monitor_id: str) -> bool:
        """Stop monitoring for a feature."""
        if monitor_id not in self.monitoring_configs:
            raise ValueError(f"Monitor {monitor_id} not found")

        self.monitoring_status[monitor_id] = False
        logger.info(f"Stopped monitoring: {monitor_id}")
        return True

    def monitor_feature(
        self, monitor_id: str, current_data: pd.Series
    ) -> List[DriftAlert]:
        """Monitor a feature for drift and generate alerts."""
        if monitor_id not in self.monitoring_configs:
            raise ValueError(f"Monitor {monitor_id} not found")

        if not self.monitoring_status[monitor_id]:
            return []

        config = self.monitoring_configs[monitor_id]
        alerts = []

        try:
            # Collect current metrics
            current_metrics = self.metrics_collector.collect_metrics(
                current_data, config.feature_name
            )

            # Get baseline metrics
            baseline_metrics = self.metrics_collector.get_baseline_metrics(
                config.feature_name
            )

            if baseline_metrics is None:
                logger.warning(f"No baseline found for feature: {config.feature_name}")
                return []

            # Get baseline data for drift detection
            if (
                config.baseline_data is not None
                and config.feature_name in config.baseline_data.columns
            ):
                baseline_data = config.baseline_data[config.feature_name]

                # Run drift detection
                for method in config.drift_detection_methods:
                    threshold = config.alert_thresholds.get(method, 0.05)

                    drift_result = self.drift_detector.detect_drift(
                        baseline_data, current_data, method, threshold
                    )

                    if drift_result.get("drift_detected", False):
                        # Determine severity
                        score = drift_result.get("score", 0.0)
                        if score > 0.8:
                            severity = AlertSeverity.CRITICAL
                        elif score > 0.6:
                            severity = AlertSeverity.HIGH
                        elif score > 0.4:
                            severity = AlertSeverity.MEDIUM
                        else:
                            severity = AlertSeverity.LOW

                        # Create alert
                        alert = self.alert_manager.create_alert(
                            config.feature_name, drift_result, severity
                        )
                        alerts.append(alert)

        except Exception as e:
            logger.error(f"Feature monitoring failed: {str(e)}")

        return alerts

    def get_monitoring_summary(self, monitor_id: str) -> Dict[str, Any]:
        """Get monitoring summary for a feature."""
        if monitor_id not in self.monitoring_configs:
            raise ValueError(f"Monitor {monitor_id} not found")

        config = self.monitoring_configs[monitor_id]

        # Get recent metrics
        recent_metrics = self.metrics_collector.get_metrics_history(
            config.feature_name, hours=24
        )

        # Get active alerts
        active_alerts = self.alert_manager.get_active_alerts(config.feature_name)

        return {
            "monitor_id": monitor_id,
            "feature_name": config.feature_name,
            "monitoring_level": config.monitoring_level.value,
            "is_active": self.monitoring_status.get(monitor_id, False),
            "recent_metrics_count": len(recent_metrics),
            "active_alerts_count": len(active_alerts),
            "last_metrics": recent_metrics[-1].to_dict() if recent_metrics else None,
            "active_alerts": [alert.to_dict() for alert in active_alerts],
        }

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data for all monitors."""
        dashboard_data = {
            "total_monitors": len(self.monitoring_configs),
            "active_monitors": sum(
                1 for status in self.monitoring_status.values() if status
            ),
            "total_alerts": len(self.alert_manager.active_alerts),
            "critical_alerts": len(
                [
                    a
                    for a in self.alert_manager.active_alerts.values()
                    if a.severity == AlertSeverity.CRITICAL
                ]
            ),
            "monitors": [],
        }

        for monitor_id in self.monitoring_configs:
            summary = self.get_monitoring_summary(monitor_id)
            dashboard_data["monitors"].append(summary)

        return dashboard_data


# Example usage
async def demonstrate_feature_monitoring():
    """Demonstrate feature monitoring system."""
    print("Demonstrating S.W.A.R.M. Phase 2 Advanced MLOps - Feature Monitoring...")

    # Create monitoring system
    monitoring_system = FeatureMonitoringSystem()

    # Create sample baseline data
    np.random.seed(42)
    baseline_data = pd.DataFrame(
        {
            "feature_1": np.random.normal(0, 1, 1000),
            "feature_2": np.random.exponential(2, 1000),
            "feature_3": np.random.choice(["A", "B", "C"], 1000),
        }
    )

    # Create monitors
    for feature in baseline_data.columns:
        config = FeatureMonitorConfig(
            feature_name=feature,
            monitoring_level=MonitoringLevel.STANDARD,
            baseline_data=baseline_data,
            alert_thresholds={"ks_test": 0.05, "psi": 0.1},
            drift_detection_methods=["ks_test", "psi"],
        )

        monitor_id = monitoring_system.create_monitor(config)
        monitoring_system.start_monitoring(monitor_id)
        print(f"Created and started monitor for: {feature}")

    # Simulate current data with some drift
    current_data = pd.DataFrame(
        {
            "feature_1": np.random.normal(0.5, 1.2, 500),  # Drifted
            "feature_2": np.random.exponential(2.1, 500),  # Slight drift
            "feature_3": np.random.choice(["A", "B", "C", "D"], 500),  # New category
        }
    )

    # Monitor features
    print("\nMonitoring features for drift...")
    for feature in current_data.columns:
        # Find monitor for this feature
        monitor_id = None
        for mid, config in monitoring_system.monitoring_configs.items():
            if config.feature_name == feature:
                monitor_id = mid
                break

        if monitor_id:
            alerts = monitoring_system.monitor_feature(
                monitor_id, current_data[feature]
            )
            if alerts:
                print(f"  {feature}: {len(alerts)} alerts generated")
                for alert in alerts:
                    print(f"    - {alert.severity.value}: {alert.description}")
            else:
                print(f"  {feature}: No alerts")

    # Get dashboard data
    dashboard = monitoring_system.get_dashboard_data()
    print(f"\nDashboard Summary:")
    print(f"  Total monitors: {dashboard['total_monitors']}")
    print(f"  Active monitors: {dashboard['active_monitors']}")
    print(f"  Total alerts: {dashboard['total_alerts']}")
    print(f"  Critical alerts: {dashboard['critical_alerts']}")

    print("\nFeature Monitoring demonstration complete!")


if __name__ == "__main__":
    asyncio.run(demonstrate_feature_monitoring())
