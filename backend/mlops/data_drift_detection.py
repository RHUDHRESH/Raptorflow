"""
S.W.A.R.M. Phase 2: Advanced MLOps - Data Drift Detection System
Production-ready data drift detection with statistical methods and alerting
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
from scipy.spatial.distance import jensenshannon
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

logger = logging.getLogger("raptorflow.data_drift_detection")


class DriftType(Enum):
    """Types of data drift."""

    COVARIATE_SHIFT = "covariate_shift"
    PRIOR_PROBABILITY_SHIFT = "prior_probability_shift"
    CONCEPT_SHIFT = "concept_shift"
    DATA_QUALITY_DRIFT = "data_quality_drift"


class DriftSeverity(Enum):
    """Drift severity levels."""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DetectionMethod(Enum):
    """Drift detection methods."""

    KOLMOGOROV_SMIRNOV = "kolmogorov_smirnov"
    CHI_SQUARE = "chi_square"
    WASSERSTEIN = "wasserstein"
    JENSEN_SHANNON = "jensen_shannon"
    POPULATION_STABILITY_INDEX = "population_stability_index"
    KL_DIVERGENCE = "kl_divergence"
    ANDERSON_DARLING = "anderson_darling"


@dataclass
class DriftDetectionConfig:
    """Configuration for drift detection."""

    detector_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    dataset_name: str = ""
    detection_methods: List[DetectionMethod] = field(
        default_factory=lambda: [DetectionMethod.KOLMOGOROV_SMIRNOV]
    )
    threshold_levels: Dict[str, float] = field(default_factory=dict)
    monitoring_frequency: str = "daily"  # daily, weekly, monthly
    baseline_window_days: int = 30
    current_window_days: int = 7
    min_sample_size: int = 100
    significance_level: float = 0.05
    alert_thresholds: Dict[DriftSeverity, float] = field(
        default_factory=lambda: {
            DriftSeverity.LOW: 0.1,
            DriftSeverity.MEDIUM: 0.2,
            DriftSeverity.HIGH: 0.3,
            DriftSeverity.CRITICAL: 0.4,
        }
    )
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "detector_id": self.detector_id,
            "dataset_name": self.dataset_name,
            "detection_methods": [m.value for m in self.detection_methods],
            "threshold_levels": self.threshold_levels,
            "monitoring_frequency": self.monitoring_frequency,
            "baseline_window_days": self.baseline_window_days,
            "current_window_days": self.current_window_days,
            "min_sample_size": self.min_sample_size,
            "significance_level": self.significance_level,
            "alert_thresholds": {k.value: v for k, v in self.alert_thresholds.items()},
            "enabled": self.enabled,
        }


@dataclass
class DriftResult:
    """Result of drift detection analysis."""

    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    detector_id: str = ""
    column_name: str = ""
    drift_type: DriftType = DriftType.COVARIATE_SHIFT
    detection_method: DetectionMethod = DetectionMethod.KOLMOGOROV_SMIRNOV
    drift_score: float = 0.0
    p_value: Optional[float] = None
    severity: DriftSeverity = DriftSeverity.NONE
    threshold: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "result_id": self.result_id,
            "detector_id": self.detector_id,
            "column_name": self.column_name,
            "drift_type": self.drift_type.value,
            "detection_method": self.detection_method.value,
            "drift_score": self.drift_score,
            "p_value": self.p_value,
            "severity": self.severity.value,
            "threshold": self.threshold,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
        }


@dataclass
class DriftAlert:
    """Data drift alert."""

    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    detector_id: str = ""
    severity: DriftSeverity = DriftSeverity.MEDIUM
    title: str = ""
    description: str = ""
    affected_columns: List[str] = field(default_factory=list)
    drift_summary: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolution_notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "alert_id": self.alert_id,
            "detector_id": self.detector_id,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "affected_columns": self.affected_columns,
            "drift_summary": self.drift_summary,
            "timestamp": self.timestamp.isoformat(),
            "resolved": self.resolved,
            "resolution_notes": self.resolution_notes,
        }


class DriftDetector:
    """Base class for drift detection methods."""

    def __init__(self, method: DetectionMethod):
        self.method = method

    def detect_drift(
        self, baseline_data: pd.Series, current_data: pd.Series, threshold: float = 0.05
    ) -> Dict[str, Any]:
        """Detect drift between baseline and current data."""
        raise NotImplementedError("Subclasses must implement detect_drift method")


class KolmogorovSmirnovDetector(DriftDetector):
    """Kolmogorov-Smirnov test for drift detection."""

    def __init__(self):
        super().__init__(DetectionMethod.KOLMOGOROV_SMIRNOV)

    def detect_drift(
        self, baseline_data: pd.Series, current_data: pd.Series, threshold: float = 0.05
    ) -> Dict[str, Any]:
        """Detect drift using KS test."""
        try:
            # Clean data
            baseline_clean = baseline_data.dropna()
            current_clean = current_data.dropna()

            if len(baseline_clean) < 30 or len(current_clean) < 30:
                return {
                    "drift_score": 0.0,
                    "p_value": 1.0,
                    "drift_detected": False,
                    "error": "Insufficient sample size",
                }

            # Perform KS test
            statistic, p_value = stats.ks_2samp(baseline_clean, current_clean)

            drift_detected = p_value < threshold

            return {
                "drift_score": statistic,
                "p_value": p_value,
                "drift_detected": drift_detected,
                "baseline_size": len(baseline_clean),
                "current_size": len(current_clean),
            }

        except Exception as e:
            return {
                "drift_score": 0.0,
                "p_value": 1.0,
                "drift_detected": False,
                "error": str(e),
            }


class WassersteinDetector(DriftDetector):
    """Wasserstein distance for drift detection."""

    def __init__(self):
        super().__init__(DetectionMethod.WASSERSTEIN)

    def detect_drift(
        self, baseline_data: pd.Series, current_data: pd.Series, threshold: float = 0.1
    ) -> Dict[str, Any]:
        """Detect drift using Wasserstein distance."""
        try:
            # Clean data
            baseline_clean = baseline_data.dropna()
            current_clean = current_data.dropna()

            if len(baseline_clean) < 30 or len(current_clean) < 30:
                return {
                    "drift_score": 0.0,
                    "p_value": 1.0,
                    "drift_detected": False,
                    "error": "Insufficient sample size",
                }

            # Calculate Wasserstein distance
            distance = stats.wasserstein_distance(baseline_clean, current_clean)

            # Normalize distance (approximate normalization)
            max_distance = max(baseline_clean.max(), current_clean.max()) - min(
                baseline_clean.min(), current_clean.min()
            )
            normalized_distance = distance / max_distance if max_distance > 0 else 0.0

            drift_detected = normalized_distance > threshold

            return {
                "drift_score": normalized_distance,
                "p_value": None,
                "drift_detected": drift_detected,
                "raw_distance": distance,
                "baseline_size": len(baseline_clean),
                "current_size": len(current_clean),
            }

        except Exception as e:
            return {
                "drift_score": 0.0,
                "p_value": 1.0,
                "drift_detected": False,
                "error": str(e),
            }


class JensenShannonDetector(DriftDetector):
    """Jensen-Shannon divergence for drift detection."""

    def __init__(self):
        super().__init__(DetectionMethod.JENSEN_SHANNON)

    def detect_drift(
        self, baseline_data: pd.Series, current_data: pd.Series, threshold: float = 0.1
    ) -> Dict[str, Any]:
        """Detect drift using Jensen-Shannon divergence."""
        try:
            # Clean data
            baseline_clean = baseline_data.dropna()
            current_clean = current_data.dropna()

            if len(baseline_clean) < 30 or len(current_clean) < 30:
                return {
                    "drift_score": 0.0,
                    "p_value": 1.0,
                    "drift_detected": False,
                    "error": "Insufficient sample size",
                }

            # Create histograms
            bins = 50
            baseline_hist, bin_edges = np.histogram(
                baseline_clean, bins=bins, density=True
            )
            current_hist, _ = np.histogram(current_clean, bins=bin_edges, density=True)

            # Add small epsilon to avoid division by zero
            epsilon = 1e-10
            baseline_hist = baseline_hist + epsilon
            current_hist = current_hist + epsilon

            # Normalize
            baseline_hist = baseline_hist / np.sum(baseline_hist)
            current_hist = current_hist / np.sum(current_hist)

            # Calculate Jensen-Shannon divergence
            js_distance = jensenshannon(baseline_hist, current_hist)

            drift_detected = js_distance > threshold

            return {
                "drift_score": js_distance,
                "p_value": None,
                "drift_detected": drift_detected,
                "baseline_size": len(baseline_clean),
                "current_size": len(current_clean),
            }

        except Exception as e:
            return {
                "drift_score": 0.0,
                "p_value": 1.0,
                "drift_detected": False,
                "error": str(e),
            }


class PopulationStabilityIndexDetector(DriftDetector):
    """Population Stability Index (PSI) for drift detection."""

    def __init__(self):
        super().__init__(DetectionMethod.POPULATION_STABILITY_INDEX)

    def detect_drift(
        self, baseline_data: pd.Series, current_data: pd.Series, threshold: float = 0.1
    ) -> Dict[str, Any]:
        """Detect drift using Population Stability Index."""
        try:
            # Clean data
            baseline_clean = baseline_data.dropna()
            current_clean = current_data.dropna()

            if len(baseline_clean) < 30 or len(current_clean) < 30:
                return {
                    "drift_score": 0.0,
                    "p_value": 1.0,
                    "drift_detected": False,
                    "error": "Insufficient sample size",
                }

            # Create bins
            bins = 10
            min_val = min(baseline_clean.min(), current_clean.min())
            max_val = max(baseline_clean.max(), current_clean.max())
            bin_edges = np.linspace(min_val, max_val, bins + 1)

            # Calculate frequencies
            baseline_counts, _ = np.histogram(baseline_clean, bins=bin_edges)
            current_counts, _ = np.histogram(current_clean, bins=bin_edges)

            # Calculate percentages
            baseline_pct = baseline_counts / len(baseline_clean)
            current_pct = current_counts / len(current_clean)

            # Calculate PSI
            psi = 0.0
            for i in range(len(baseline_pct)):
                if baseline_pct[i] > 0:
                    if current_pct[i] == 0:
                        current_pct[i] = 0.0001  # Avoid division by zero

                    psi += (current_pct[i] - baseline_pct[i]) * np.log(
                        current_pct[i] / baseline_pct[i]
                    )

            drift_detected = psi > threshold

            return {
                "drift_score": psi,
                "p_value": None,
                "drift_detected": drift_detected,
                "baseline_size": len(baseline_clean),
                "current_size": len(current_clean),
            }

        except Exception as e:
            return {
                "drift_score": 0.0,
                "p_value": 1.0,
                "drift_detected": False,
                "error": str(e),
            }


class DataDriftDetector:
    """Production-ready data drift detection system."""

    def __init__(self):
        self.detectors: Dict[DetectionMethod, DriftDetector] = {
            DetectionMethod.KOLMOGOROV_SMIRNOV: KolmogorovSmirnovDetector(),
            DetectionMethod.WASSERSTEIN: WassersteinDetector(),
            DetectionMethod.JENSEN_SHANNON: JensenShannonDetector(),
            DetectionMethod.POPULATION_STABILITY_INDEX: PopulationStabilityIndexDetector(),
        }
        self.detection_configs: Dict[str, DriftDetectionConfig] = {}
        self.baseline_data: Dict[str, pd.DataFrame] = {}
        self.drift_results: Dict[str, List[DriftResult]] = {}
        self.drift_alerts: Dict[str, DriftAlert] = {}
        self.active_detectors: Set[str] = set()

    def create_detector(self, config: DriftDetectionConfig) -> str:
        """Create a new drift detector."""
        self.detection_configs[config.detector_id] = config
        self.drift_results[config.detector_id] = []

        logger.info(f"Created drift detector: {config.detector_id}")
        return config.detector_id

    def set_baseline(self, detector_id: str, data: pd.DataFrame) -> bool:
        """Set baseline data for drift detection."""
        if detector_id not in self.detection_configs:
            raise ValueError(f"Detector {detector_id} not found")

        self.baseline_data[detector_id] = data.copy()
        logger.info(f"Set baseline data for detector: {detector_id}")
        return True

    def start_detection(self, detector_id: str) -> bool:
        """Start drift detection for a dataset."""
        if detector_id not in self.detection_configs:
            raise ValueError(f"Detector {detector_id} not found")

        self.active_detectors.add(detector_id)
        logger.info(f"Started drift detection: {detector_id}")
        return True

    def stop_detection(self, detector_id: str) -> bool:
        """Stop drift detection for a dataset."""
        if detector_id not in self.detection_configs:
            raise ValueError(f"Detector {detector_id} not found")

        self.active_detectors.discard(detector_id)
        logger.info(f"Stopped drift detection: {detector_id}")
        return True

    def detect_drift(
        self, detector_id: str, current_data: pd.DataFrame
    ) -> List[DriftResult]:
        """Detect drift in current data compared to baseline."""
        if detector_id not in self.detection_configs:
            raise ValueError(f"Detector {detector_id} not found")

        if detector_id not in self.active_detectors:
            return []

        config = self.detection_configs[detector_id]

        if detector_id not in self.baseline_data:
            raise ValueError(f"No baseline data set for detector {detector_id}")

        baseline_data = self.baseline_data[detector_id]
        drift_results = []

        try:
            # Check each column
            for column in current_data.columns:
                if column not in baseline_data.columns:
                    continue

                baseline_column = baseline_data[column]
                current_column = current_data[column]

                # Skip if insufficient data
                if (
                    len(baseline_column.dropna()) < config.min_sample_size
                    or len(current_column.dropna()) < config.min_sample_size
                ):
                    continue

                # Run each detection method
                for method in config.detection_methods:
                    if method not in self.detectors:
                        continue

                    detector = self.detectors[method]
                    threshold = config.threshold_levels.get(method.value, 0.05)

                    detection_result = detector.detect_drift(
                        baseline_column, current_column, threshold
                    )

                    # Determine severity
                    severity = self._calculate_severity(
                        detection_result["drift_score"], config.alert_thresholds
                    )

                    # Create drift result
                    drift_result = DriftResult(
                        detector_id=detector_id,
                        column_name=column,
                        drift_type=DriftType.COVARIATE_SHIFT,
                        detection_method=method,
                        drift_score=detection_result["drift_score"],
                        p_value=detection_result.get("p_value"),
                        severity=severity,
                        threshold=threshold,
                        details=detection_result,
                    )

                    drift_results.append(drift_result)

            # Store results
            self.drift_results[detector_id].extend(drift_results)

            # Generate alerts if needed
            alerts = self._generate_alerts(detector_id, drift_results)

            logger.info(
                f"Drift detection completed for {detector_id}: {len(drift_results)} results, {len(alerts)} alerts"
            )

        except Exception as e:
            logger.error(f"Drift detection failed for {detector_id}: {str(e)}")

        return drift_results

    def _calculate_severity(
        self, drift_score: float, alert_thresholds: Dict[DriftSeverity, float]
    ) -> DriftSeverity:
        """Calculate drift severity based on score."""
        if drift_score >= alert_thresholds.get(DriftSeverity.CRITICAL, 0.4):
            return DriftSeverity.CRITICAL
        elif drift_score >= alert_thresholds.get(DriftSeverity.HIGH, 0.3):
            return DriftSeverity.HIGH
        elif drift_score >= alert_thresholds.get(DriftSeverity.MEDIUM, 0.2):
            return DriftSeverity.MEDIUM
        elif drift_score >= alert_thresholds.get(DriftSeverity.LOW, 0.1):
            return DriftSeverity.LOW
        else:
            return DriftSeverity.NONE

    def _generate_alerts(
        self, detector_id: str, drift_results: List[DriftResult]
    ) -> List[DriftAlert]:
        """Generate alerts based on drift results."""
        alerts = []

        # Group results by severity
        severity_groups = {}
        for result in drift_results:
            if result.severity != DriftSeverity.NONE:
                if result.severity not in severity_groups:
                    severity_groups[result.severity] = []
                severity_groups[result.severity].append(result)

        # Create alerts for each severity level
        for severity, results in severity_groups.items():
            alert = DriftAlert(
                detector_id=detector_id,
                severity=severity,
                title=f"Data Drift Detected - {severity.value.upper()}",
                description=f"Data drift detected in {len(results)} columns with {severity.value} severity",
                affected_columns=[r.column_name for r in results],
                drift_summary={
                    "total_columns": len(results),
                    "max_drift_score": max(r.drift_score for r in results),
                    "avg_drift_score": np.mean([r.drift_score for r in results]),
                    "detection_methods": list(
                        set(r.detection_method.value for r in results)
                    ),
                },
            )

            alerts.append(alert)
            self.drift_alerts[alert.alert_id] = alert

        return alerts

    def get_detector_summary(self, detector_id: str) -> Dict[str, Any]:
        """Get detector summary."""
        if detector_id not in self.detection_configs:
            raise ValueError(f"Detector {detector_id} not found")

        config = self.detection_configs[detector_id]
        results = self.drift_results.get(detector_id, [])
        active_alerts = [
            alert
            for alert in self.drift_alerts.values()
            if alert.detector_id == detector_id and not alert.resolved
        ]

        # Calculate recent results
        recent_time = datetime.now() - timedelta(days=7)
        recent_results = [r for r in results if r.timestamp >= recent_time]

        # Calculate statistics
        severity_counts = {}
        for result in recent_results:
            severity = result.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        return {
            "detector_id": detector_id,
            "dataset_name": config.dataset_name,
            "is_active": detector_id in self.active_detectors,
            "detection_methods": [m.value for m in config.detection_methods],
            "total_results": len(results),
            "recent_results": len(recent_results),
            "active_alerts": len(active_alerts),
            "severity_distribution": severity_counts,
            "baseline_set": detector_id in self.baseline_data,
            "baseline_shape": (
                self.baseline_data[detector_id].shape
                if detector_id in self.baseline_data
                else None
            ),
        }

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data for all detectors."""
        dashboard_data = {
            "total_detectors": len(self.detection_configs),
            "active_detectors": len(self.active_detectors),
            "total_alerts": len(self.drift_alerts),
            "active_alerts": len(
                [a for a in self.drift_alerts.values() if not a.resolved]
            ),
            "detectors": [],
        }

        for detector_id in self.detection_configs:
            summary = self.get_detector_summary(detector_id)
            dashboard_data["detectors"].append(summary)

        return dashboard_data


# Example usage
async def demonstrate_data_drift_detection():
    """Demonstrate data drift detection system."""
    print("Demonstrating S.W.A.R.M. Phase 2 Advanced MLOps - Data Drift Detection...")

    # Create baseline data
    np.random.seed(42)
    baseline_data = pd.DataFrame(
        {
            "customer_age": np.random.normal(35, 10, 1000),
            "income": np.random.normal(50000, 15000, 1000),
            "spending_score": np.random.uniform(1, 100, 1000),
            "gender": np.random.choice(["M", "F"], 1000),
            "region": np.random.choice(["North", "South", "East", "West"], 1000),
        }
    )

    # Create current data with drift
    current_data = pd.DataFrame(
        {
            "customer_age": np.random.normal(40, 12, 1000),  # Shifted mean and variance
            "income": np.random.normal(55000, 18000, 1000),  # Shifted mean and variance
            "spending_score": np.random.uniform(
                5, 95, 1000
            ),  # Slightly different range
            "gender": np.random.choice(["M", "F"], 1000),
            "region": np.random.choice(["North", "South", "East", "West"], 1000),
        }
    )

    print(f"Baseline data shape: {baseline_data.shape}")
    print(f"Current data shape: {current_data.shape}")

    # Create drift detector
    detector = DataDriftDetector()

    # Create detector configuration
    config = DriftDetectionConfig(
        dataset_name="customer_data",
        detection_methods=[
            DetectionMethod.KOLMOGOROV_SMIRNOV,
            DetectionMethod.WASSERSTEIN,
            DetectionMethod.JENSEN_SHANNON,
        ],
        threshold_levels={
            "kolmogorov_smirnov": 0.05,
            "wasserstein": 0.1,
            "jensen_shannon": 0.1,
        },
        alert_thresholds={
            DriftSeverity.LOW: 0.1,
            DriftSeverity.MEDIUM: 0.2,
            DriftSeverity.HIGH: 0.3,
            DriftSeverity.CRITICAL: 0.4,
        },
    )

    detector_id = detector.create_detector(config)
    detector.set_baseline(detector_id, baseline_data)
    detector.start_detection(detector_id)

    print(f"\nCreated and started drift detector: {detector_id}")

    # Detect drift
    print("\nDetecting data drift...")
    drift_results = detector.detect_drift(detector_id, current_data)

    print(f"Detected {len(drift_results)} drift instances")

    # Display drift results
    if drift_results:
        print("\nDrift Detection Results:")
        for result in drift_results:
            if result.severity != DriftSeverity.NONE:
                print(f"  {result.column_name}:")
                print(f"    Method: {result.detection_method.value}")
                print(f"    Score: {result.drift_score:.4f}")
                print(f"    Severity: {result.severity.value.upper()}")
                if result.p_value:
                    print(f"    P-value: {result.p_value:.4f}")

    # Get detector summary
    summary = detector.get_detector_summary(detector_id)
    print(f"\nDetector Summary:")
    print(f"  Dataset: {summary['dataset_name']}")
    print(f"  Active: {summary['is_active']}")
    print(f"  Total results: {summary['total_results']}")
    print(f"  Recent results: {summary['recent_results']}")
    print(f"  Active alerts: {summary['active_alerts']}")
    print(f"  Severity distribution: {summary['severity_distribution']}")

    # Get dashboard data
    dashboard = detector.get_dashboard_data()
    print(f"\nDashboard Summary:")
    print(f"  Total detectors: {dashboard['total_detectors']}")
    print(f"  Active detectors: {dashboard['active_detectors']}")
    print(f"  Total alerts: {dashboard['total_alerts']}")
    print(f"  Active alerts: {dashboard['active_alerts']}")

    print("\nData Drift Detection demonstration complete!")


if __name__ == "__main__":
    asyncio.run(demonstrate_data_drift_detection())
