"""
S.W.A.R.M. Phase 2: Advanced MLOps - Data Quality Monitoring System
Production-ready data quality monitoring with real-time alerts and metrics
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
from sklearn.ensemble import IsolationForest
from sklearn.metrics import jensen_shannon_distance

warnings.filterwarnings("ignore")

logger = logging.getLogger("raptorflow.data_quality_monitoring")


class MonitoringFrequency(Enum):
    """Data quality monitoring frequencies."""

    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class QualityDimension(Enum):
    """Data quality dimensions for monitoring."""

    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    CONSISTENCY = "consistency"
    VALIDITY = "validity"
    UNIQUENESS = "uniqueness"
    TIMELINESS = "timeliness"
    INTEGRITY = "integrity"


class AlertSeverity(Enum):
    """Alert severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DataQualityMonitorConfig:
    """Configuration for data quality monitoring."""

    monitor_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    dataset_name: str = ""
    monitoring_frequency: MonitoringFrequency = MonitoringFrequency.DAILY
    dimensions: List[QualityDimension] = field(
        default_factory=lambda: list(QualityDimension)
    )
    alert_thresholds: Dict[str, float] = field(default_factory=dict)
    notification_channels: List[str] = field(default_factory=list)
    baseline_data: Optional[pd.DataFrame] = None
    retention_days: int = 30
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "monitor_id": self.monitor_id,
            "dataset_name": self.dataset_name,
            "monitoring_frequency": self.monitoring_frequency.value,
            "dimensions": [d.value for d in self.dimensions],
            "alert_thresholds": self.alert_thresholds,
            "notification_channels": self.notification_channels,
            "retention_days": self.retention_days,
            "enabled": self.enabled,
        }


@dataclass
class QualityMetric:
    """Data quality metric data point."""

    metric_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    monitor_id: str = ""
    dimension: QualityDimension = QualityDimension.COMPLETENESS
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
            "dimension": self.dimension.value,
            "metric_name": self.metric_name,
            "value": self.value,
            "threshold": self.threshold,
            "status": self.status,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
        }


@dataclass
class QualityAlert:
    """Data quality alert."""

    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    monitor_id: str = ""
    dimension: QualityDimension = QualityDimension.COMPLETENESS
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
            "dimension": self.dimension.value,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "metric_value": self.metric_value,
            "threshold": self.threshold,
            "timestamp": self.timestamp.isoformat(),
            "resolved": self.resolved,
            "resolution_notes": self.resolution_notes,
        }


class DataQualityMonitor:
    """Production-ready data quality monitoring system."""

    def __init__(self):
        self.monitors: Dict[str, DataQualityMonitorConfig] = {}
        self.metrics_history: Dict[str, List[QualityMetric]] = {}
        self.alerts: Dict[str, QualityAlert] = {}
        self.baseline_stats: Dict[str, Dict[str, Any]] = {}
        self.active_monitors: Set[str] = set()

    def create_monitor(self, config: DataQualityMonitorConfig) -> str:
        """Create a new data quality monitor."""
        self.monitors[config.monitor_id] = config
        self.metrics_history[config.monitor_id] = []

        # Calculate baseline statistics if provided
        if config.baseline_data is not None:
            self.baseline_stats[config.monitor_id] = self._calculate_baseline_stats(
                config.baseline_data
            )

        logger.info(f"Created data quality monitor: {config.monitor_id}")
        return config.monitor_id

    def start_monitoring(self, monitor_id: str) -> bool:
        """Start monitoring for a dataset."""
        if monitor_id not in self.monitors:
            raise ValueError(f"Monitor {monitor_id} not found")

        self.active_monitors.add(monitor_id)
        logger.info(f"Started monitoring: {monitor_id}")
        return True

    def stop_monitoring(self, monitor_id: str) -> bool:
        """Stop monitoring for a dataset."""
        if monitor_id not in self.monitors:
            raise ValueError(f"Monitor {monitor_id} not found")

        self.active_monitors.discard(monitor_id)
        logger.info(f"Stopped monitoring: {monitor_id}")
        return True

    def monitor_data_quality(
        self, monitor_id: str, data: pd.DataFrame
    ) -> List[QualityAlert]:
        """Monitor data quality and generate alerts."""
        if monitor_id not in self.monitors:
            raise ValueError(f"Monitor {monitor_id} not found")

        if monitor_id not in self.active_monitors:
            return []

        config = self.monitors[monitor_id]
        alerts = []

        try:
            # Monitor each configured dimension
            for dimension in config.dimensions:
                dimension_alerts = self._monitor_dimension(
                    monitor_id, data, dimension, config
                )
                alerts.extend(dimension_alerts)

            logger.info(f"Monitoring completed for {monitor_id}: {len(alerts)} alerts")

        except Exception as e:
            logger.error(f"Monitoring failed for {monitor_id}: {str(e)}")

        return alerts

    def _monitor_dimension(
        self,
        monitor_id: str,
        data: pd.DataFrame,
        dimension: QualityDimension,
        config: DataQualityMonitorConfig,
    ) -> List[QualityAlert]:
        """Monitor a specific quality dimension."""
        alerts = []

        if dimension == QualityDimension.COMPLETENESS:
            alerts.extend(self._monitor_completeness(monitor_id, data, config))
        elif dimension == QualityDimension.UNIQUENESS:
            alerts.extend(self._monitor_uniqueness(monitor_id, data, config))
        elif dimension == QualityDimension.VALIDITY:
            alerts.extend(self._monitor_validity(monitor_id, data, config))
        elif dimension == QualityDimension.ACCURACY:
            alerts.extend(self._monitor_accuracy(monitor_id, data, config))
        elif dimension == QualityDimension.CONSISTENCY:
            alerts.extend(self._monitor_consistency(monitor_id, data, config))
        elif dimension == QualityDimension.TIMELINESS:
            alerts.extend(self._monitor_timeliness(monitor_id, data, config))
        elif dimension == QualityDimension.INTEGRITY:
            alerts.extend(self._monitor_integrity(monitor_id, data, config))

        return alerts

    def _monitor_completeness(
        self, monitor_id: str, data: pd.DataFrame, config: DataQualityMonitorConfig
    ) -> List[QualityAlert]:
        """Monitor data completeness."""
        alerts = []
        threshold = config.alert_thresholds.get("completeness", 0.95)

        for column in data.columns:
            total_count = len(data)
            null_count = data[column].isnull().sum()
            completeness_score = 1.0 - (null_count / total_count)

            # Create metric
            metric = QualityMetric(
                monitor_id=monitor_id,
                dimension=QualityDimension.COMPLETENESS,
                metric_name=f"completeness_{column}",
                value=completeness_score,
                threshold=threshold,
                status=(
                    "good"
                    if completeness_score >= threshold
                    else (
                        "warning"
                        if completeness_score >= threshold * 0.8
                        else "critical"
                    )
                ),
                details={
                    "column": column,
                    "null_count": null_count,
                    "total_count": total_count,
                    "completeness_percentage": completeness_score * 100,
                },
            )

            self.metrics_history[monitor_id].append(metric)

            # Generate alert if needed
            if completeness_score < threshold:
                severity = (
                    AlertSeverity.HIGH
                    if completeness_score < threshold * 0.8
                    else AlertSeverity.MEDIUM
                )

                alert = QualityAlert(
                    monitor_id=monitor_id,
                    dimension=QualityDimension.COMPLETENESS,
                    severity=severity,
                    title=f"Low completeness in {column}",
                    description=f"Column {column} has {null_count} null values ({completeness_score:.1%} complete)",
                    metric_value=completeness_score,
                    threshold=threshold,
                )

                alerts.append(alert)
                self.alerts[alert.alert_id] = alert

        return alerts

    def _monitor_uniqueness(
        self, monitor_id: str, data: pd.DataFrame, config: DataQualityMonitorConfig
    ) -> List[QualityAlert]:
        """Monitor data uniqueness."""
        alerts = []
        threshold = config.alert_thresholds.get("uniqueness", 0.95)

        for column in data.columns:
            total_count = len(data)
            unique_count = data[column].nunique()
            uniqueness_score = unique_count / total_count

            # Create metric
            metric = QualityMetric(
                monitor_id=monitor_id,
                dimension=QualityDimension.UNIQUENESS,
                metric_name=f"uniqueness_{column}",
                value=uniqueness_score,
                threshold=threshold,
                status=(
                    "good"
                    if uniqueness_score >= threshold
                    else (
                        "warning" if uniqueness_score >= threshold * 0.8 else "critical"
                    )
                ),
                details={
                    "column": column,
                    "unique_count": unique_count,
                    "duplicate_count": total_count - unique_count,
                    "total_count": total_count,
                    "uniqueness_percentage": uniqueness_score * 100,
                },
            )

            self.metrics_history[monitor_id].append(metric)

            # Generate alert if needed
            if uniqueness_score < threshold:
                severity = (
                    AlertSeverity.HIGH
                    if uniqueness_score < threshold * 0.8
                    else AlertSeverity.MEDIUM
                )

                alert = QualityAlert(
                    monitor_id=monitor_id,
                    dimension=QualityDimension.UNIQUENESS,
                    severity=severity,
                    title=f"Low uniqueness in {column}",
                    description=f"Column {column} has {total_count - unique_count} duplicates ({uniqueness_score:.1%} unique)",
                    metric_value=uniqueness_score,
                    threshold=threshold,
                )

                alerts.append(alert)
                self.alerts[alert.alert_id] = alert

        return alerts

    def _monitor_validity(
        self, monitor_id: str, data: pd.DataFrame, config: DataQualityMonitorConfig
    ) -> List[QualityAlert]:
        """Monitor data validity."""
        alerts = []
        threshold = config.alert_thresholds.get("validity", 0.95)

        for column in data.columns:
            validity_score = 1.0  # Default to valid

            # Check for validity based on data type
            if pd.api.types.is_numeric_dtype(data[column]):
                # Check for outliers using IQR method
                Q1 = data[column].quantile(0.25)
                Q3 = data[column].quantile(0.75)
                IQR = Q3 - Q1

                if IQR > 0:
                    outliers = (
                        (data[column] < (Q1 - 1.5 * IQR))
                        | (data[column] > (Q3 + 1.5 * IQR))
                    ).sum()
                    validity_score = 1.0 - (outliers / len(data))

            # Create metric
            metric = QualityMetric(
                monitor_id=monitor_id,
                dimension=QualityDimension.VALIDITY,
                metric_name=f"validity_{column}",
                value=validity_score,
                threshold=threshold,
                status=(
                    "good"
                    if validity_score >= threshold
                    else "warning" if validity_score >= threshold * 0.8 else "critical"
                ),
                details={
                    "column": column,
                    "validity_score": validity_score,
                    "data_type": str(data[column].dtype),
                },
            )

            self.metrics_history[monitor_id].append(metric)

            # Generate alert if needed
            if validity_score < threshold:
                severity = (
                    AlertSeverity.HIGH
                    if validity_score < threshold * 0.8
                    else AlertSeverity.MEDIUM
                )

                alert = QualityAlert(
                    monitor_id=monitor_id,
                    dimension=QualityDimension.VALIDITY,
                    severity=severity,
                    title=f"Low validity in {column}",
                    description=f"Column {column} has validity score {validity_score:.1%}",
                    metric_value=validity_score,
                    threshold=threshold,
                )

                alerts.append(alert)
                self.alerts[alert.alert_id] = alert

        return alerts

    def _monitor_accuracy(
        self, monitor_id: str, data: pd.DataFrame, config: DataQualityMonitorConfig
    ) -> List[QualityAlert]:
        """Monitor data accuracy using outlier detection."""
        alerts = []
        threshold = config.alert_thresholds.get("accuracy", 0.95)

        numeric_columns = data.select_dtypes(include=[np.number]).columns

        for column in numeric_columns:
            column_data = data[column].dropna()

            if len(column_data) < 10:
                continue

            # Use Isolation Forest for outlier detection
            try:
                isolation_forest = IsolationForest(contamination=0.1, random_state=42)
                outlier_labels = isolation_forest.fit_predict(
                    column_data.values.reshape(-1, 1)
                )
                outlier_count = (outlier_labels == -1).sum()
                accuracy_score = 1.0 - (outlier_count / len(column_data))

                # Create metric
                metric = QualityMetric(
                    monitor_id=monitor_id,
                    dimension=QualityDimension.ACCURACY,
                    metric_name=f"accuracy_{column}",
                    value=accuracy_score,
                    threshold=threshold,
                    status=(
                        "good"
                        if accuracy_score >= threshold
                        else (
                            "warning"
                            if accuracy_score >= threshold * 0.8
                            else "critical"
                        )
                    ),
                    details={
                        "column": column,
                        "outlier_count": outlier_count,
                        "total_count": len(column_data),
                        "accuracy_percentage": accuracy_score * 100,
                    },
                )

                self.metrics_history[monitor_id].append(metric)

                # Generate alert if needed
                if accuracy_score < threshold:
                    severity = (
                        AlertSeverity.HIGH
                        if accuracy_score < threshold * 0.8
                        else AlertSeverity.MEDIUM
                    )

                    alert = QualityAlert(
                        monitor_id=monitor_id,
                        dimension=QualityDimension.ACCURACY,
                        severity=severity,
                        title=f"Low accuracy in {column}",
                        description=f"Column {column} has {outlier_count} outliers ({accuracy_score:.1%} accurate)",
                        metric_value=accuracy_score,
                        threshold=threshold,
                    )

                    alerts.append(alert)
                    self.alerts[alert.alert_id] = alert

            except Exception as e:
                logger.warning(f"Error monitoring accuracy for {column}: {str(e)}")

        return alerts

    def _monitor_consistency(
        self, monitor_id: str, data: pd.DataFrame, config: DataQualityMonitorConfig
    ) -> List[QualityAlert]:
        """Monitor data consistency across related columns."""
        alerts = []
        threshold = config.alert_thresholds.get("consistency", 0.8)

        # Check correlation consistency for numeric columns
        numeric_columns = data.select_dtypes(include=[np.number]).columns

        if len(numeric_columns) > 1:
            try:
                # Calculate correlation matrix
                corr_matrix = data[numeric_columns].corr()

                # Check for extremely low correlations (potential inconsistency)
                low_correlations = []
                for i in range(len(corr_matrix.columns)):
                    for j in range(i + 1, len(corr_matrix.columns)):
                        col1, col2 = corr_matrix.columns[i], corr_matrix.columns[j]
                        correlation = abs(corr_matrix.iloc[i, j])

                        if correlation < 0.1:  # Very low correlation
                            low_correlations.append((col1, col2, correlation))

                consistency_score = 1.0 - (
                    len(low_correlations)
                    / (len(numeric_columns) * (len(numeric_columns) - 1) / 2)
                )

                # Create metric
                metric = QualityMetric(
                    monitor_id=monitor_id,
                    dimension=QualityDimension.CONSISTENCY,
                    metric_name="correlation_consistency",
                    value=consistency_score,
                    threshold=threshold,
                    status=(
                        "good"
                        if consistency_score >= threshold
                        else (
                            "warning"
                            if consistency_score >= threshold * 0.8
                            else "critical"
                        )
                    ),
                    details={
                        "numeric_columns": list(numeric_columns),
                        "low_correlations": low_correlations,
                        "consistency_score": consistency_score,
                    },
                )

                self.metrics_history[monitor_id].append(metric)

                # Generate alert if needed
                if consistency_score < threshold:
                    severity = (
                        AlertSeverity.HIGH
                        if consistency_score < threshold * 0.8
                        else AlertSeverity.MEDIUM
                    )

                    alert = QualityAlert(
                        monitor_id=monitor_id,
                        dimension=QualityDimension.CONSISTENCY,
                        severity=severity,
                        title="Low correlation consistency",
                        description=f"Found {len(low_correlations)} pairs of columns with very low correlation",
                        metric_value=consistency_score,
                        threshold=threshold,
                    )

                    alerts.append(alert)
                    self.alerts[alert.alert_id] = alert

            except Exception as e:
                logger.warning(f"Error monitoring consistency: {str(e)}")

        return alerts

    def _monitor_timeliness(
        self, monitor_id: str, data: pd.DataFrame, config: DataQualityMonitorConfig
    ) -> List[QualityAlert]:
        """Monitor data timeliness."""
        alerts = []
        threshold = config.alert_thresholds.get("timeliness", 0.8)

        # Check for datetime columns
        datetime_columns = data.select_dtypes(include=["datetime64"]).columns

        for column in datetime_columns:
            column_data = data[column].dropna()

            if len(column_data) == 0:
                continue

            # Check data recency
            max_date = column_data.max()
            current_date = datetime.now()
            days_old = (current_date - max_date).days

            # Calculate timeliness score (newer is better)
            timeliness_score = max(0.0, 1.0 - (days_old / 30))  # 30-day window

            # Create metric
            metric = QualityMetric(
                monitor_id=monitor_id,
                dimension=QualityDimension.TIMELINESS,
                metric_name=f"timeliness_{column}",
                value=timeliness_score,
                threshold=threshold,
                status=(
                    "good"
                    if timeliness_score >= threshold
                    else (
                        "warning" if timeliness_score >= threshold * 0.8 else "critical"
                    )
                ),
                details={
                    "column": column,
                    "max_date": max_date.isoformat(),
                    "days_old": days_old,
                    "timeliness_score": timeliness_score,
                },
            )

            self.metrics_history[monitor_id].append(metric)

            # Generate alert if needed
            if timeliness_score < threshold:
                severity = (
                    AlertSeverity.HIGH
                    if timeliness_score < threshold * 0.8
                    else AlertSeverity.MEDIUM
                )

                alert = QualityAlert(
                    monitor_id=monitor_id,
                    dimension=QualityDimension.TIMELINESS,
                    severity=severity,
                    title=f"Low timeliness in {column}",
                    description=f"Column {column} data is {days_old} days old",
                    metric_value=timeliness_score,
                    threshold=threshold,
                )

                alerts.append(alert)
                self.alerts[alert.alert_id] = alert

        return alerts

    def _monitor_integrity(
        self, monitor_id: str, data: pd.DataFrame, config: DataQualityMonitorConfig
    ) -> List[QualityAlert]:
        """Monitor data integrity."""
        alerts = []
        threshold = config.alert_thresholds.get("integrity", 0.9)

        # Check for duplicate rows
        duplicate_rows = data.duplicated().sum()
        total_rows = len(data)
        integrity_score = 1.0 - (duplicate_rows / total_rows)

        # Create metric
        metric = QualityMetric(
            monitor_id=monitor_id,
            dimension=QualityDimension.INTEGRITY,
            metric_name="row_integrity",
            value=integrity_score,
            threshold=threshold,
            status=(
                "good"
                if integrity_score >= threshold
                else "warning" if integrity_score >= threshold * 0.8 else "critical"
            ),
            details={
                "duplicate_rows": duplicate_rows,
                "total_rows": total_rows,
                "integrity_score": integrity_score,
            },
        )

        self.metrics_history[monitor_id].append(metric)

        # Generate alert if needed
        if integrity_score < threshold:
            severity = (
                AlertSeverity.HIGH
                if integrity_score < threshold * 0.8
                else AlertSeverity.MEDIUM
            )

            alert = QualityAlert(
                monitor_id=monitor_id,
                dimension=QualityDimension.INTEGRITY,
                severity=severity,
                title="Low data integrity",
                description=f"Found {duplicate_rows} duplicate rows ({integrity_score:.1%} integrity)",
                metric_value=integrity_score,
                threshold=threshold,
            )

            alerts.append(alert)
            self.alerts[alert.alert_id] = alert

        return alerts

    def _calculate_baseline_stats(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate baseline statistics for comparison."""
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
                    "null_count": data[column].isnull().sum(),
                    "unique_count": data[column].nunique(),
                }
            else:
                stats[column] = {
                    "null_count": data[column].isnull().sum(),
                    "unique_count": data[column].nunique(),
                    "value_counts": data[column].value_counts().to_dict(),
                }

        return stats

    def get_monitoring_summary(self, monitor_id: str) -> Dict[str, Any]:
        """Get monitoring summary for a dataset."""
        if monitor_id not in self.monitors:
            raise ValueError(f"Monitor {monitor_id} not found")

        config = self.monitors[monitor_id]
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
            "is_active": monitor_id in self.active_monitors,
            "monitoring_frequency": config.monitoring_frequency.value,
            "dimensions": [d.value for d in config.dimensions],
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
            "total_monitors": len(self.monitors),
            "active_monitors": len(self.active_monitors),
            "total_alerts": len(self.alerts),
            "active_alerts": len([a for a in self.alerts.values() if not a.resolved]),
            "monitors": [],
        }

        for monitor_id in self.monitors:
            summary = self.get_monitoring_summary(monitor_id)
            dashboard_data["monitors"].append(summary)

        return dashboard_data


# Example usage
async def demonstrate_data_quality_monitoring():
    """Demonstrate data quality monitoring system."""
    print(
        "Demonstrating S.W.A.R.M. Phase 2 Advanced MLOps - Data Quality Monitoring..."
    )

    # Create sample data with quality issues
    np.random.seed(42)
    sample_data = pd.DataFrame(
        {
            "customer_id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1],  # Duplicate
            "age": [25, 30, None, 45, 22, 35, 28, 33, 40, 27, 25],  # Missing value
            "income": [
                50000,
                60000,
                70000,
                80000,
                45000,
                65000,
                55000,
                75000,
                85000,
                48000,
                50000,
            ],
            "email": [
                "a@b.com",
                "invalid-email",
                "c@d.com",
                "e@f.com",
                "g@h.com",
                "i@j.com",
                "k@l.com",
                "m@n.com",
                "o@p.com",
                "q@r.com",
                "a@b.com",
            ],
            "registration_date": pd.date_range("2020-01-01", periods=10).tolist()
            + [pd.Timestamp("2020-01-01")],  # Old data
            "category": [
                "A",
                "B",
                "C",
                "D",
                "E",
                "F",
                "G",
                "H",
                "I",
                "J",
                "A",
            ],  # Duplicate
        }
    )

    print(f"Sample data shape: {sample_data.shape}")
    print(f"Sample data columns: {list(sample_data.columns)}")

    # Create monitor
    monitor = DataQualityMonitor()

    # Create monitoring configuration
    config = DataQualityMonitorConfig(
        dataset_name="customer_data",
        monitoring_frequency=MonitoringFrequency.DAILY,
        dimensions=list(QualityDimension),
        alert_thresholds={
            "completeness": 0.95,
            "uniqueness": 0.95,
            "validity": 0.90,
            "accuracy": 0.90,
            "consistency": 0.80,
            "timeliness": 0.80,
            "integrity": 0.90,
        },
        baseline_data=sample_data,
    )

    monitor_id = monitor.create_monitor(config)
    monitor.start_monitoring(monitor_id)
    print(f"\nCreated and started monitor: {monitor_id}")

    # Monitor data quality
    print("\nMonitoring data quality...")
    alerts = monitor.monitor_data_quality(monitor_id, sample_data)

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

    print("\nData Quality Monitoring demonstration complete!")


if __name__ == "__main__":
    asyncio.run(demonstrate_data_quality_monitoring())
