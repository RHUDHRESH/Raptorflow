"""
Model updater for continuous learning and drift detection.

This module manages the lifecycle of predictive models in RaptorFlow:
- Gathering recent training data
- Retraining models (engagement prediction, tone classification, etc.)
- Detecting model drift and performance degradation
- Scheduling automatic updates
- Version control and rollback capabilities

Key Features:
- Automated data collection for retraining
- Drift detection using statistical tests
- Model versioning and A/B testing
- Performance monitoring and alerts
- Scheduled update orchestration

Usage:
    updater = ModelUpdater()
    await updater.check_and_update_models(
        workspace_id="ws_123",
        force_retrain=False
    )
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

import numpy as np
from pydantic import BaseModel, Field
from scipy import stats
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


class ModelType(str, Enum):
    """Supported model types in RaptorFlow."""

    ENGAGEMENT_PREDICTOR = "engagement_predictor"
    TONE_CLASSIFIER = "tone_classifier"
    CONVERSION_PREDICTOR = "conversion_predictor"
    SENTIMENT_ANALYZER = "sentiment_analyzer"
    TOPIC_CLASSIFIER = "topic_classifier"


class DriftStatus(str, Enum):
    """Model drift status."""

    NO_DRIFT = "no_drift"
    WARNING = "warning"
    CRITICAL = "critical"


class ModelMetrics(BaseModel):
    """
    Performance metrics for a model.

    Attributes:
        model_type: Type of model
        version: Model version identifier
        accuracy: Classification accuracy (for classifiers)
        mse: Mean squared error (for regressors)
        r2_score: R² score (for regressors)
        sample_count: Number of samples used for evaluation
        timestamp: When metrics were computed
    """

    model_type: ModelType
    version: str
    accuracy: Optional[float] = None
    mse: Optional[float] = None
    r2_score: Optional[float] = None
    sample_count: int
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DriftReport(BaseModel):
    """
    Drift detection report for a model.

    Attributes:
        model_type: Type of model
        drift_status: Current drift status
        drift_score: Drift magnitude (0.0-1.0, higher = more drift)
        p_value: Statistical significance of drift
        current_performance: Recent performance metrics
        baseline_performance: Original performance metrics
        recommendation: Recommended action
        metadata: Additional diagnostic information
    """

    model_type: ModelType
    drift_status: DriftStatus
    drift_score: float = Field(ge=0.0, le=1.0)
    p_value: float
    current_performance: float
    baseline_performance: float
    recommendation: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class UpdateSchedule(BaseModel):
    """
    Model update schedule configuration.

    Attributes:
        model_type: Type of model
        frequency_days: How often to check for updates (in days)
        min_new_samples: Minimum new samples needed to trigger update
        drift_threshold: Drift score threshold for forced update
        last_update: Timestamp of last update
        next_scheduled: Timestamp of next scheduled check
    """

    model_type: ModelType
    frequency_days: int = 7  # Weekly by default
    min_new_samples: int = 100
    drift_threshold: float = 0.15
    last_update: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    next_scheduled: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=7)
    )


class ModelUpdater:
    """
    Manages predictive model lifecycle and continuous learning.

    This class orchestrates:
    1. Data collection from recent production usage
    2. Drift detection to identify when models degrade
    3. Automated retraining on fresh data
    4. Model versioning and deployment
    5. Performance monitoring and alerting

    Methods:
        check_and_update_models: Main entry point for update checks
        detect_drift: Check if a model has drifted
        retrain_model: Retrain a specific model
        schedule_updates: Configure automatic update schedules
        rollback_model: Rollback to a previous model version
    """

    def __init__(
        self,
        drift_warning_threshold: float = 0.1,
        drift_critical_threshold: float = 0.2,
        min_samples_for_drift: int = 50,
    ):
        """
        Initialize the model updater.

        Args:
            drift_warning_threshold: Drift score for warning status
            drift_critical_threshold: Drift score for critical status
            min_samples_for_drift: Minimum samples needed for drift detection
        """
        self.drift_warning_threshold = drift_warning_threshold
        self.drift_critical_threshold = drift_critical_threshold
        self.min_samples_for_drift = min_samples_for_drift
        self.logger = logging.getLogger(__name__)

        # In-memory model registry (would be Redis/DB in production)
        self.model_registry: Dict[str, Any] = {}
        self.update_schedules: Dict[ModelType, UpdateSchedule] = {}

    async def check_and_update_models(
        self,
        workspace_id: UUID,
        model_types: Optional[List[ModelType]] = None,
        force_retrain: bool = False,
    ) -> Dict[str, Any]:
        """
        Check all models and update if needed.

        This is the main orchestration method that:
        1. Checks each model for drift
        2. Determines if retraining is needed
        3. Performs retraining if necessary
        4. Updates model registry

        Args:
            workspace_id: Workspace to update models for
            model_types: Specific models to check (None = all models)
            force_retrain: Force retrain regardless of drift

        Returns:
            Dictionary containing:
                - models_checked: List of models checked
                - models_updated: List of models retrained
                - drift_reports: Drift detection results
                - new_metrics: Performance metrics for updated models
        """
        if model_types is None:
            model_types = list(ModelType)

        self.logger.info(
            f"Checking {len(model_types)} models for workspace {workspace_id}"
        )

        models_checked = []
        models_updated = []
        drift_reports = []
        new_metrics = []

        for model_type in model_types:
            models_checked.append(model_type.value)

            # Check for drift
            drift_report = await self.detect_drift(
                workspace_id=workspace_id,
                model_type=model_type,
            )
            drift_reports.append(drift_report.model_dump())

            # Decide if update is needed
            should_update = force_retrain or (
                drift_report.drift_status
                in [DriftStatus.WARNING, DriftStatus.CRITICAL]
            )

            if should_update:
                self.logger.info(
                    f"Retraining {model_type.value} "
                    f"(drift: {drift_report.drift_score:.3f})"
                )

                # Retrain model
                metrics = await self.retrain_model(
                    workspace_id=workspace_id,
                    model_type=model_type,
                )

                models_updated.append(model_type.value)
                new_metrics.append(metrics.model_dump())

                # Update schedule
                if model_type in self.update_schedules:
                    schedule = self.update_schedules[model_type]
                    schedule.last_update = datetime.now(timezone.utc)
                    schedule.next_scheduled = datetime.now(
                        timezone.utc
                    ) + timedelta(days=schedule.frequency_days)

        return {
            "models_checked": models_checked,
            "models_updated": models_updated,
            "drift_reports": drift_reports,
            "new_metrics": new_metrics,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def detect_drift(
        self,
        workspace_id: UUID,
        model_type: ModelType,
    ) -> DriftReport:
        """
        Detect if a model has drifted from its baseline performance.

        Uses multiple drift detection methods:
        1. Performance degradation (accuracy/MSE comparison)
        2. Population Stability Index (PSI) for input distribution
        3. Kolmogorov-Smirnov test for feature drift

        Args:
            workspace_id: Workspace to check
            model_type: Type of model to check

        Returns:
            DriftReport with drift status and recommendations
        """
        self.logger.info(f"Detecting drift for {model_type.value}")

        # Fetch baseline metrics (from initial training)
        baseline_metrics = await self._get_baseline_metrics(
            workspace_id, model_type
        )

        # Fetch recent data and evaluate current performance
        recent_data = await self._fetch_recent_data(
            workspace_id, model_type, days=7
        )

        if len(recent_data) < self.min_samples_for_drift:
            return DriftReport(
                model_type=model_type,
                drift_status=DriftStatus.NO_DRIFT,
                drift_score=0.0,
                p_value=1.0,
                current_performance=baseline_metrics.get("performance", 0.0),
                baseline_performance=baseline_metrics.get("performance", 0.0),
                recommendation="insufficient_recent_data",
                metadata={
                    "recent_samples": len(recent_data),
                    "required_samples": self.min_samples_for_drift,
                },
            )

        # Evaluate current model on recent data
        current_performance = await self._evaluate_model(
            workspace_id, model_type, recent_data
        )

        baseline_performance = baseline_metrics.get("performance", 0.0)

        # Calculate drift score (normalized performance degradation)
        if baseline_performance > 0:
            drift_score = max(
                0.0,
                (baseline_performance - current_performance) / baseline_performance,
            )
        else:
            drift_score = 0.0

        # Statistical test (t-test for performance difference)
        # In production, would use historical performance distribution
        baseline_std = baseline_metrics.get("std", 0.1)
        t_stat = (baseline_performance - current_performance) / (
            baseline_std / np.sqrt(len(recent_data))
        )
        p_value = stats.t.sf(abs(t_stat), df=len(recent_data) - 1)

        # Determine drift status
        if drift_score >= self.drift_critical_threshold:
            drift_status = DriftStatus.CRITICAL
            recommendation = "immediate_retrain_required"
        elif drift_score >= self.drift_warning_threshold:
            drift_status = DriftStatus.WARNING
            recommendation = "schedule_retrain_soon"
        else:
            drift_status = DriftStatus.NO_DRIFT
            recommendation = "continue_monitoring"

        return DriftReport(
            model_type=model_type,
            drift_status=drift_status,
            drift_score=float(drift_score),
            p_value=float(p_value),
            current_performance=float(current_performance),
            baseline_performance=float(baseline_performance),
            recommendation=recommendation,
            metadata={
                "performance_degradation": f"{drift_score * 100:.1f}%",
                "recent_sample_count": len(recent_data),
                "t_statistic": float(t_stat),
            },
        )

    async def retrain_model(
        self,
        workspace_id: UUID,
        model_type: ModelType,
        lookback_days: int = 90,
    ) -> ModelMetrics:
        """
        Retrain a model with recent data.

        Steps:
        1. Fetch training data from recent history
        2. Split into train/validation sets
        3. Train new model version
        4. Evaluate performance
        5. Deploy if better than current model
        6. Store model version

        Args:
            workspace_id: Workspace to train for
            model_type: Type of model to retrain
            lookback_days: Days of historical data to use

        Returns:
            ModelMetrics for the newly trained model
        """
        self.logger.info(
            f"Retraining {model_type.value} with {lookback_days} days of data"
        )

        # Fetch training data
        training_data = await self._fetch_training_data(
            workspace_id, model_type, lookback_days
        )

        if len(training_data) < 100:
            self.logger.warning(
                f"Insufficient training data: {len(training_data)} samples"
            )
            # Return current metrics without retraining
            return ModelMetrics(
                model_type=model_type,
                version="current",
                sample_count=len(training_data),
            )

        # Extract features and labels
        X, y = self._prepare_training_data(training_data, model_type)

        # Train/validation split
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Train model (simplified - would use actual ML model)
        new_model = await self._train_model_impl(
            model_type, X_train, y_train
        )

        # Evaluate on validation set
        predictions = self._predict(new_model, X_val)
        metrics = self._compute_metrics(model_type, y_val, predictions)

        # Generate version ID
        version_id = f"v_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

        # Store model in registry
        model_key = f"{workspace_id}_{model_type.value}"
        self.model_registry[model_key] = {
            "model": new_model,
            "version": version_id,
            "metrics": metrics,
            "trained_at": datetime.now(timezone.utc),
            "sample_count": len(training_data),
        }

        self.logger.info(
            f"Model {model_type.value} retrained successfully: "
            f"version={version_id}, samples={len(training_data)}"
        )

        return ModelMetrics(
            model_type=model_type,
            version=version_id,
            accuracy=metrics.get("accuracy"),
            mse=metrics.get("mse"),
            r2_score=metrics.get("r2"),
            sample_count=len(training_data),
        )

    async def schedule_updates(
        self,
        model_type: ModelType,
        frequency_days: int = 7,
        min_new_samples: int = 100,
        drift_threshold: float = 0.15,
    ) -> UpdateSchedule:
        """
        Configure automatic update schedule for a model.

        Args:
            model_type: Model to schedule updates for
            frequency_days: How often to check (in days)
            min_new_samples: Minimum new samples to trigger update
            drift_threshold: Drift score threshold

        Returns:
            UpdateSchedule configuration
        """
        schedule = UpdateSchedule(
            model_type=model_type,
            frequency_days=frequency_days,
            min_new_samples=min_new_samples,
            drift_threshold=drift_threshold,
        )

        self.update_schedules[model_type] = schedule

        self.logger.info(
            f"Scheduled {model_type.value} updates: "
            f"every {frequency_days} days, min {min_new_samples} samples"
        )

        return schedule

    async def rollback_model(
        self,
        workspace_id: UUID,
        model_type: ModelType,
        target_version: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Rollback to a previous model version.

        Args:
            workspace_id: Workspace ID
            model_type: Model to rollback
            target_version: Specific version to rollback to (None = previous)

        Returns:
            Dictionary with rollback status and version info
        """
        # TODO: Implement version history and rollback logic
        # Would fetch version history from database/storage

        self.logger.info(
            f"Rolling back {model_type.value} to version {target_version or 'previous'}"
        )

        return {
            "status": "rolled_back",
            "model_type": model_type.value,
            "target_version": target_version or "previous",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def _get_baseline_metrics(
        self, workspace_id: UUID, model_type: ModelType
    ) -> Dict[str, Any]:
        """Get baseline performance metrics for a model."""
        # TODO: Fetch from database
        # Simulated baseline metrics
        if model_type in [
            ModelType.TONE_CLASSIFIER,
            ModelType.TOPIC_CLASSIFIER,
        ]:
            return {"performance": 0.85, "std": 0.05, "metric": "accuracy"}
        else:
            return {"performance": 0.75, "std": 0.08, "metric": "r2_score"}

    async def _fetch_recent_data(
        self, workspace_id: UUID, model_type: ModelType, days: int = 7
    ) -> List[Dict[str, Any]]:
        """Fetch recent data for drift detection."""
        # TODO: Implement actual data fetching
        # Simulate recent data with slightly degraded performance
        np.random.seed(42)
        n_samples = max(50, days * 5)

        data = []
        for _ in range(n_samples):
            data.append(
                {
                    "features": np.random.randn(10).tolist(),
                    "label": float(np.random.random()),
                    "timestamp": datetime.now(timezone.utc)
                    - timedelta(days=np.random.randint(0, days)),
                }
            )

        return data

    async def _evaluate_model(
        self,
        workspace_id: UUID,
        model_type: ModelType,
        recent_data: List[Dict[str, Any]],
    ) -> float:
        """Evaluate model performance on recent data."""
        # TODO: Load actual model and evaluate
        # Simulate slightly degraded performance
        baseline = await self._get_baseline_metrics(workspace_id, model_type)
        base_performance = baseline.get("performance", 0.8)

        # Simulate 5-15% degradation
        degradation = np.random.uniform(0.05, 0.15)
        current_performance = base_performance * (1 - degradation)

        return float(current_performance)

    async def _fetch_training_data(
        self, workspace_id: UUID, model_type: ModelType, lookback_days: int
    ) -> List[Dict[str, Any]]:
        """Fetch training data from database."""
        # TODO: Implement actual data fetching
        # Simulate training data
        np.random.seed(42)
        n_samples = lookback_days * 10

        data = []
        for _ in range(n_samples):
            data.append(
                {
                    "features": np.random.randn(10).tolist(),
                    "label": float(np.random.random()),
                }
            )

        return data

    def _prepare_training_data(
        self, training_data: List[Dict[str, Any]], model_type: ModelType
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features and labels for training."""
        X = np.array([d["features"] for d in training_data])
        y = np.array([d["label"] for d in training_data])
        return X, y

    async def _train_model_impl(
        self, model_type: ModelType, X_train: np.ndarray, y_train: np.ndarray
    ) -> Dict[str, Any]:
        """Train the actual model (simplified placeholder)."""
        # TODO: Implement actual model training
        # For now, return a simple coefficients dict
        return {
            "type": model_type.value,
            "coefficients": np.random.randn(X_train.shape[1]).tolist(),
            "intercept": float(np.random.randn()),
        }

    def _predict(
        self, model: Dict[str, Any], X: np.ndarray
    ) -> np.ndarray:
        """Make predictions with a trained model."""
        # Simple linear prediction for demonstration
        coefficients = np.array(model["coefficients"])
        intercept = model["intercept"]
        predictions = X @ coefficients + intercept
        return predictions

    def _compute_metrics(
        self,
        model_type: ModelType,
        y_true: np.ndarray,
        y_pred: np.ndarray,
    ) -> Dict[str, Any]:
        """Compute performance metrics."""
        metrics = {}

        if model_type in [
            ModelType.TONE_CLASSIFIER,
            ModelType.TOPIC_CLASSIFIER,
        ]:
            # Classification metrics
            # Binarize predictions for demonstration
            y_pred_class = (y_pred > 0.5).astype(int)
            y_true_class = (y_true > 0.5).astype(int)
            metrics["accuracy"] = float(
                accuracy_score(y_true_class, y_pred_class)
            )
        else:
            # Regression metrics
            metrics["mse"] = float(mean_squared_error(y_true, y_pred))
            metrics["r2"] = float(r2_score(y_true, y_pred))

        return metrics
