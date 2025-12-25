"""
S.W.A.R.M. Phase 2: Distributed Experiment Tracking
Production-ready distributed experiment tracking for ML operations
"""

import asyncio
import json
import logging
import os
import pickle
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

# MLflow imports
try:
    import mlflow
    import mlflow.pytorch
    import mlflow.tensorflow
    from mlflow.entities import Experiment, Run
    from mlflow.tracking import MlflowClient

    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False

# Weights & Biases imports
try:
    import wandb

    WANDB_AVAILABLE = True
except ImportError:
    WANDB_AVAILABLE = False

# TensorBoard imports
try:
    import tensorboard
    from torch.utils.tensorboard import SummaryWriter

    TENSORBOARD_AVAILABLE = True
except ImportError:
    TENSORBOARD_AVAILABLE = False

# Database imports
try:
    import psycopg2
    from psycopg2.extras import Json as PsycopgJson

    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

try:
    import pymongo

    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

logger = logging.getLogger("raptorflow.distributed_experiment_tracking")


class TrackingBackend(Enum):
    """Experiment tracking backends."""

    MLFLOW = "mlflow"
    WANDB = "wandb"
    TENSORBOARD = "tensorboard"
    CUSTOM = "custom"
    POSTGRES = "postgres"
    MONGODB = "mongodb"


class ExperimentStatus(Enum):
    """Experiment status."""

    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SCHEDULED = "scheduled"


class MetricType(Enum):
    """Metric types."""

    SCALAR = "scalar"
    HISTOGRAM = "histogram"
    IMAGE = "image"
    AUDIO = "audio"
    TEXT = "text"
    ARTIFACT = "artifact"


@dataclass
class ExperimentConfig:
    """Experiment configuration."""

    experiment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    tracking_backend: TrackingBackend = TrackingBackend.MLFLOW
    auto_logging: bool = True
    artifact_location: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "experiment_id": self.experiment_id,
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
            "parameters": self.parameters,
            "metadata": self.metadata,
            "tracking_backend": self.tracking_backend.value,
            "auto_logging": self.auto_logging,
            "artifact_location": self.artifact_location,
        }


@dataclass
class RunConfig:
    """Run configuration."""

    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    experiment_id: str = ""
    name: str = ""
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    status: ExperimentStatus = ExperimentStatus.RUNNING
    user_id: Optional[str] = None
    git_commit: Optional[str] = None
    environment: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "run_id": self.run_id,
            "experiment_id": self.experiment_id,
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "tags": self.tags,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status.value,
            "user_id": self.user_id,
            "git_commit": self.git_commit,
            "environment": self.environment,
        }


@dataclass
class MetricData:
    """Metric data point."""

    name: str
    value: float
    step: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    metric_type: MetricType = MetricType.SCALAR
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "value": self.value,
            "step": self.step,
            "timestamp": self.timestamp.isoformat(),
            "metric_type": self.metric_type.value,
            "metadata": self.metadata,
        }


class ExperimentTracker(ABC):
    """Abstract base class for experiment trackers."""

    @abstractmethod
    async def create_experiment(self, config: ExperimentConfig) -> str:
        """Create a new experiment."""
        pass

    @abstractmethod
    async def start_run(self, config: RunConfig) -> str:
        """Start a new run."""
        pass

    @abstractmethod
    async def log_metric(self, run_id: str, metric: MetricData):
        """Log a metric."""
        pass

    @abstractmethod
    async def log_parameter(self, run_id: str, key: str, value: Any):
        """Log a parameter."""
        pass

    @abstractmethod
    async def log_artifact(self, run_id: str, artifact_path: str, artifact_name: str):
        """Log an artifact."""
        pass

    @abstractmethod
    async def end_run(
        self, run_id: str, status: ExperimentStatus = ExperimentStatus.COMPLETED
    ):
        """End a run."""
        pass

    @abstractmethod
    async def get_run_info(self, run_id: str) -> Dict[str, Any]:
        """Get run information."""
        pass

    @abstractmethod
    async def list_experiments(self) -> List[Dict[str, Any]]:
        """List all experiments."""
        pass

    @abstractmethod
    async def search_runs(
        self, experiment_ids: List[str], filter_expr: str = ""
    ) -> List[Dict[str, Any]]:
        """Search runs."""
        pass


class MLflowTracker(ExperimentTracker):
    """MLflow-based experiment tracker."""

    def __init__(self, tracking_uri: str = None):
        if not MLFLOW_AVAILABLE:
            raise ImportError("MLflow is required")

        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)

        self.client = MlflowClient(tracking_uri)
        self.active_runs: Dict[str, Run] = {}

    async def create_experiment(self, config: ExperimentConfig) -> str:
        """Create a new MLflow experiment."""
        try:
            experiment_id = mlflow.create_experiment(
                name=config.name,
                tags=config.tags,
                artifact_location=config.artifact_location,
            )

            logger.info(f"Created MLflow experiment: {config.name} ({experiment_id})")
            return experiment_id

        except Exception as e:
            logger.error(f"Failed to create MLflow experiment: {str(e)}")
            raise

    async def start_run(self, config: RunConfig) -> str:
        """Start a new MLflow run."""
        try:
            # Set experiment if specified
            if config.experiment_id:
                experiment = self.client.get_experiment(config.experiment_id)
                mlflow.set_experiment(experiment.name)

            # Start run
            run = mlflow.start_run(
                run_name=config.name,
                tags=config.tags,
                experiment_id=config.experiment_id,
            )

            self.active_runs[config.run_id] = run

            # Log parameters
            for key, value in config.parameters.items():
                await self.log_parameter(config.run_id, key, value)

            # Log environment info
            if config.environment:
                for key, value in config.environment.items():
                    mlflow.set_tag(f"env.{key}", value)

            # Log git commit if provided
            if config.git_commit:
                mlflow.set_tag("git_commit", config.git_commit)

            logger.info(f"Started MLflow run: {run.info.run_id}")
            return run.info.run_id

        except Exception as e:
            logger.error(f"Failed to start MLflow run: {str(e)}")
            raise

    async def log_metric(self, run_id: str, metric: MetricData):
        """Log a metric to MLflow."""
        try:
            if run_id not in self.active_runs:
                raise ValueError(f"Run {run_id} not found")

            if metric.metric_type == MetricType.SCALAR:
                mlflow.log_metric(
                    metric.name,
                    metric.value,
                    step=metric.step,
                    timestamp=metric.timestamp.timestamp(),
                )
            elif metric.metric_type == MetricType.HISTOGRAM:
                # For histograms, log as artifact
                mlflow.log_dict(metric.metadata, f"{metric.name}_histogram.json")
            else:
                # For other types, log as artifact
                mlflow.log_dict(metric.to_dict(), f"{metric.name}.json")

        except Exception as e:
            logger.error(f"Failed to log metric to MLflow: {str(e)}")
            raise

    async def log_parameter(self, run_id: str, key: str, value: Any):
        """Log a parameter to MLflow."""
        try:
            if run_id not in self.active_runs:
                raise ValueError(f"Run {run_id} not found")

            mlflow.log_param(key, value)

        except Exception as e:
            logger.error(f"Failed to log parameter to MLflow: {str(e)}")
            raise

    async def log_artifact(self, run_id: str, artifact_path: str, artifact_name: str):
        """Log an artifact to MLflow."""
        try:
            if run_id not in self.active_runs:
                raise ValueError(f"Run {run_id} not found")

            mlflow.log_artifact(artifact_path, artifact_name)

        except Exception as e:
            logger.error(f"Failed to log artifact to MLflow: {str(e)}")
            raise

    async def end_run(
        self, run_id: str, status: ExperimentStatus = ExperimentStatus.COMPLETED
    ):
        """End an MLflow run."""
        try:
            if run_id in self.active_runs:
                mlflow.end_run()
                del self.active_runs[run_id]

            logger.info(f"Ended MLflow run: {run_id}")

        except Exception as e:
            logger.error(f"Failed to end MLflow run: {str(e)}")
            raise

    async def get_run_info(self, run_id: str) -> Dict[str, Any]:
        """Get MLflow run information."""
        try:
            run = self.client.get_run(run_id)

            return {
                "run_id": run.info.run_id,
                "experiment_id": run.info.experiment_id,
                "status": run.info.status,
                "start_time": datetime.fromtimestamp(
                    run.info.start_time / 1000
                ).isoformat(),
                "end_time": (
                    datetime.fromtimestamp(run.info.end_time / 1000).isoformat()
                    if run.info.end_time
                    else None
                ),
                "parameters": run.data.params,
                "metrics": run.data.metrics,
                "tags": run.data.tags,
            }

        except Exception as e:
            logger.error(f"Failed to get MLflow run info: {str(e)}")
            raise

    async def list_experiments(self) -> List[Dict[str, Any]]:
        """List all MLflow experiments."""
        try:
            experiments = self.client.list_experiments()

            return [
                {
                    "experiment_id": exp.experiment_id,
                    "name": exp.name,
                    "artifact_location": exp.artifact_location,
                    "creation_time": datetime.fromtimestamp(
                        exp.creation_time / 1000
                    ).isoformat(),
                    "tags": exp.tags,
                }
                for exp in experiments
            ]

        except Exception as e:
            logger.error(f"Failed to list MLflow experiments: {str(e)}")
            raise

    async def search_runs(
        self, experiment_ids: List[str], filter_expr: str = ""
    ) -> List[Dict[str, Any]]:
        """Search MLflow runs."""
        try:
            runs = self.client.search_runs(experiment_ids, filter_expr)

            return [
                {
                    "run_id": run.info.run_id,
                    "experiment_id": run.info.experiment_id,
                    "status": run.info.status,
                    "start_time": datetime.fromtimestamp(
                        run.info.start_time / 1000
                    ).isoformat(),
                    "end_time": (
                        datetime.fromtimestamp(run.info.end_time / 1000).isoformat()
                        if run.info.end_time
                        else None
                    ),
                    "parameters": run.data.params,
                    "metrics": run.data.metrics,
                    "tags": run.data.tags,
                }
                for run in runs
            ]

        except Exception as e:
            logger.error(f"Failed to search MLflow runs: {str(e)}")
            raise


class WandbTracker(ExperimentTracker):
    """Weights & Biases-based experiment tracker."""

    def __init__(self, project: str, entity: str = None):
        if not WANDB_AVAILABLE:
            raise ImportError("Weights & Biases is required")

        self.project = project
        self.entity = entity
        self.active_runs: Dict[str, wandb.wandb_sdk.wandb_run.Run] = {}

    async def create_experiment(self, config: ExperimentConfig) -> str:
        """Create a new W&B experiment (project)."""
        try:
            # W&B doesn't have explicit experiment creation like MLflow
            # Projects are created automatically when runs are logged
            logger.info(f"W&B project: {self.project}")
            return self.project

        except Exception as e:
            logger.error(f"Failed to create W&B project: {str(e)}")
            raise

    async def start_run(self, config: RunConfig) -> str:
        """Start a new W&B run."""
        try:
            run = wandb.init(
                project=self.project,
                entity=self.entity,
                name=config.name,
                tags=config.tags,
                config=config.parameters,
                notes=config.description,
                resume=None,
            )

            self.active_runs[config.run_id] = run

            # Log environment info
            if config.environment:
                for key, value in config.environment.items():
                    wandb.config[f"env_{key}"] = value

            # Log git commit if provided
            if config.git_commit:
                wandb.config["git_commit"] = config.git_commit

            logger.info(f"Started W&B run: {run.id}")
            return run.id

        except Exception as e:
            logger.error(f"Failed to start W&B run: {str(e)}")
            raise

    async def log_metric(self, run_id: str, metric: MetricData):
        """Log a metric to W&B."""
        try:
            if run_id not in self.active_runs:
                raise ValueError(f"Run {run_id} not found")

            if metric.metric_type == MetricType.SCALAR:
                wandb.log({metric.name: metric.value}, step=metric.step)
            elif metric.metric_type == MetricType.HISTOGRAM:
                wandb.log(
                    {metric.name: wandb.Histogram(metric.metadata.get("values", []))},
                    step=metric.step,
                )
            else:
                # For other types, log as JSON
                wandb.log({metric.name: metric.to_dict()}, step=metric.step)

        except Exception as e:
            logger.error(f"Failed to log metric to W&B: {str(e)}")
            raise

    async def log_parameter(self, run_id: str, key: str, value: Any):
        """Log a parameter to W&B."""
        try:
            if run_id not in self.active_runs:
                raise ValueError(f"Run {run_id} not found")

            wandb.config[key] = value

        except Exception as e:
            logger.error(f"Failed to log parameter to W&B: {str(e)}")
            raise

    async def log_artifact(self, run_id: str, artifact_path: str, artifact_name: str):
        """Log an artifact to W&B."""
        try:
            if run_id not in self.active_runs:
                raise ValueError(f"Run {run_id} not found")

            wandb.save(artifact_path, base_path=artifact_name)

        except Exception as e:
            logger.error(f"Failed to log artifact to W&B: {str(e)}")
            raise

    async def end_run(
        self, run_id: str, status: ExperimentStatus = ExperimentStatus.COMPLETED
    ):
        """End a W&B run."""
        try:
            if run_id in self.active_runs:
                wandb.finish()
                del self.active_runs[run_id]

            logger.info(f"Ended W&B run: {run_id}")

        except Exception as e:
            logger.error(f"Failed to end W&B run: {str(e)}")
            raise

    async def get_run_info(self, run_id: str) -> Dict[str, Any]:
        """Get W&B run information."""
        try:
            # W&B API would be needed for this
            # Simplified implementation
            return {"run_id": run_id, "project": self.project, "status": "finished"}

        except Exception as e:
            logger.error(f"Failed to get W&B run info: {str(e)}")
            raise

    async def list_experiments(self) -> List[Dict[str, Any]]:
        """List all W&B experiments (projects)."""
        try:
            # W&B API would be needed for this
            # Simplified implementation
            return [
                {
                    "experiment_id": self.project,
                    "name": self.project,
                    "project": self.project,
                }
            ]

        except Exception as e:
            logger.error(f"Failed to list W&B experiments: {str(e)}")
            raise

    async def search_runs(
        self, experiment_ids: List[str], filter_expr: str = ""
    ) -> List[Dict[str, Any]]:
        """Search W&B runs."""
        try:
            # W&B API would be needed for this
            # Simplified implementation
            return []

        except Exception as e:
            logger.error(f"Failed to search W&B runs: {str(e)}")
            raise


class TensorBoardTracker(ExperimentTracker):
    """TensorBoard-based experiment tracker."""

    def __init__(self, log_dir: str = "./tensorboard_logs"):
        if not TENSORBOARD_AVAILABLE:
            raise ImportError("TensorBoard is required")

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.writers: Dict[str, SummaryWriter] = {}

    async def create_experiment(self, config: ExperimentConfig) -> str:
        """Create a new TensorBoard experiment."""
        try:
            experiment_dir = self.log_dir / config.name
            experiment_dir.mkdir(parents=True, exist_ok=True)

            logger.info(f"Created TensorBoard experiment: {config.name}")
            return str(experiment_dir)

        except Exception as e:
            logger.error(f"Failed to create TensorBoard experiment: {str(e)}")
            raise

    async def start_run(self, config: RunConfig) -> str:
        """Start a new TensorBoard run."""
        try:
            run_dir = self.log_dir / f"run_{config.run_id}_{int(time.time())}"
            run_dir.mkdir(parents=True, exist_ok=True)

            writer = SummaryWriter(log_dir=str(run_dir))
            self.writers[config.run_id] = writer

            # Log parameters as text
            for key, value in config.parameters.items():
                writer.add_text(f"parameters/{key}", str(value))

            logger.info(f"Started TensorBoard run: {config.run_id}")
            return config.run_id

        except Exception as e:
            logger.error(f"Failed to start TensorBoard run: {str(e)}")
            raise

    async def log_metric(self, run_id: str, metric: MetricData):
        """Log a metric to TensorBoard."""
        try:
            if run_id not in self.writers:
                raise ValueError(f"Run {run_id} not found")

            writer = self.writers[run_id]

            if metric.metric_type == MetricType.SCALAR:
                writer.add_scalar(metric.name, metric.value, metric.step)
            elif metric.metric_type == MetricType.HISTOGRAM:
                # For histograms, we need numpy array
                values = metric.metadata.get("values", [])
                if values:
                    writer.add_histogram(metric.name, values, metric.step)
            else:
                # For other types, log as text
                writer.add_text(metric.name, str(metric.to_dict()), metric.step)

        except Exception as e:
            logger.error(f"Failed to log metric to TensorBoard: {str(e)}")
            raise

    async def log_parameter(self, run_id: str, key: str, value: Any):
        """Log a parameter to TensorBoard."""
        try:
            if run_id not in self.writers:
                raise ValueError(f"Run {run_id} not found")

            writer = self.writers[run_id]
            writer.add_text(f"parameters/{key}", str(value))

        except Exception as e:
            logger.error(f"Failed to log parameter to TensorBoard: {str(e)}")
            raise

    async def log_artifact(self, run_id: str, artifact_path: str, artifact_name: str):
        """Log an artifact to TensorBoard."""
        try:
            if run_id not in self.writers:
                raise ValueError(f"Run {run_id} not found")

            # TensorBoard doesn't have direct artifact logging
            # We can log the file path as text
            writer = self.writers[run_id]
            writer.add_text(f"artifacts/{artifact_name}", artifact_path)

        except Exception as e:
            logger.error(f"Failed to log artifact to TensorBoard: {str(e)}")
            raise

    async def end_run(
        self, run_id: str, status: ExperimentStatus = ExperimentStatus.COMPLETED
    ):
        """End a TensorBoard run."""
        try:
            if run_id in self.writers:
                self.writers[run_id].close()
                del self.writers[run_id]

            logger.info(f"Ended TensorBoard run: {run_id}")

        except Exception as e:
            logger.error(f"Failed to end TensorBoard run: {str(e)}")
            raise

    async def get_run_info(self, run_id: str) -> Dict[str, Any]:
        """Get TensorBoard run information."""
        try:
            run_dir = self.log_dir / f"run_{run_id}"

            return {"run_id": run_id, "log_dir": str(run_dir), "status": "completed"}

        except Exception as e:
            logger.error(f"Failed to get TensorBoard run info: {str(e)}")
            raise

    async def list_experiments(self) -> List[Dict[str, Any]]:
        """List all TensorBoard experiments."""
        try:
            experiments = []

            for item in self.log_dir.iterdir():
                if item.is_dir():
                    experiments.append(
                        {
                            "experiment_id": str(item),
                            "name": item.name,
                            "log_dir": str(item),
                        }
                    )

            return experiments

        except Exception as e:
            logger.error(f"Failed to list TensorBoard experiments: {str(e)}")
            raise

    async def search_runs(
        self, experiment_ids: List[str], filter_expr: str = ""
    ) -> List[Dict[str, Any]]:
        """Search TensorBoard runs."""
        try:
            # TensorBoard doesn't have built-in search functionality
            # Simplified implementation
            runs = []

            for exp_id in experiment_ids:
                exp_dir = self.log_dir / exp_id
                if exp_dir.exists():
                    for item in exp_dir.iterdir():
                        if item.is_dir() and item.name.startswith("run_"):
                            run_id = item.name.replace("run_", "").split("_")[0]
                            runs.append(
                                {
                                    "run_id": run_id,
                                    "experiment_id": exp_id,
                                    "log_dir": str(item),
                                }
                            )

            return runs

        except Exception as e:
            logger.error(f"Failed to search TensorBoard runs: {str(e)}")
            raise


class DistributedExperimentTracker:
    """Main distributed experiment tracking orchestrator."""

    def __init__(
        self, backend: TrackingBackend = TrackingBackend.MLFLOW, **backend_config
    ):
        self.backend = backend
        self.tracker = self._create_tracker(backend, **backend_config)
        self.experiments: Dict[str, ExperimentConfig] = {}
        self.runs: Dict[str, RunConfig] = {}
        self.tracking_history: List[Dict[str, Any]] = []

    def _create_tracker(self, backend: TrackingBackend, **config) -> ExperimentTracker:
        """Create experiment tracker based on backend."""
        if backend == TrackingBackend.MLFLOW:
            return MLflowTracker(config.get("tracking_uri"))
        elif backend == TrackingBackend.WANDB:
            return WandbTracker(config.get("project"), config.get("entity"))
        elif backend == TrackingBackend.TENSORBOARD:
            return TensorBoardTracker(config.get("log_dir", "./tensorboard_logs"))
        else:
            raise ValueError(f"Unsupported tracking backend: {backend}")

    async def create_experiment(self, config: ExperimentConfig) -> str:
        """Create a new experiment."""
        config.tracking_backend = self.backend
        experiment_id = await self.tracker.create_experiment(config)

        self.experiments[experiment_id] = config

        # Record creation
        self.tracking_history.append(
            {
                "action": "create_experiment",
                "experiment_id": experiment_id,
                "config": config.to_dict(),
                "timestamp": datetime.now().isoformat(),
            }
        )

        return experiment_id

    async def start_run(self, config: RunConfig) -> str:
        """Start a new experiment run."""
        run_id = await self.tracker.start_run(config)

        self.runs[run_id] = config

        # Record start
        self.tracking_history.append(
            {
                "action": "start_run",
                "run_id": run_id,
                "config": config.to_dict(),
                "timestamp": datetime.now().isoformat(),
            }
        )

        return run_id

    async def log_metrics(self, run_id: str, metrics: List[MetricData]):
        """Log multiple metrics."""
        for metric in metrics:
            await self.tracker.log_metric(run_id, metric)

    async def log_metric(
        self, run_id: str, name: str, value: float, step: int = 0, **metadata
    ):
        """Log a single metric."""
        metric = MetricData(name=name, value=value, step=step, metadata=metadata)
        await self.tracker.log_metric(run_id, metric)

    async def log_parameters(self, run_id: str, parameters: Dict[str, Any]):
        """Log multiple parameters."""
        for key, value in parameters.items():
            await self.tracker.log_parameter(run_id, key, value)

    async def log_artifacts(self, run_id: str, artifacts: Dict[str, str]):
        """Log multiple artifacts."""
        for artifact_name, artifact_path in artifacts.items():
            await self.tracker.log_artifact(run_id, artifact_path, artifact_name)

    async def end_run(
        self, run_id: str, status: ExperimentStatus = ExperimentStatus.COMPLETED
    ):
        """End an experiment run."""
        await self.tracker.end_run(run_id, status)

        # Update run status
        if run_id in self.runs:
            self.runs[run_id].status = status
            self.runs[run_id].end_time = datetime.now()

        # Record end
        self.tracking_history.append(
            {
                "action": "end_run",
                "run_id": run_id,
                "status": status.value,
                "timestamp": datetime.now().isoformat(),
            }
        )

    async def get_experiment_summary(self, experiment_id: str) -> Dict[str, Any]:
        """Get experiment summary."""
        if experiment_id not in self.experiments:
            return {}

        experiment_config = self.experiments[experiment_id]
        experiment_runs = [
            run for run in self.runs.values() if run.experiment_id == experiment_id
        ]

        return {
            "experiment": experiment_config.to_dict(),
            "total_runs": len(experiment_runs),
            "running_runs": len(
                [r for r in experiment_runs if r.status == ExperimentStatus.RUNNING]
            ),
            "completed_runs": len(
                [r for r in experiment_runs if r.status == ExperimentStatus.COMPLETED]
            ),
            "failed_runs": len(
                [r for r in experiment_runs if r.status == ExperimentStatus.FAILED]
            ),
            "runs": [run.to_dict() for run in experiment_runs],
        }

    async def compare_runs(self, run_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple runs."""
        comparison = {"runs": {}, "comparison_timestamp": datetime.now().isoformat()}

        for run_id in run_ids:
            if run_id in self.runs:
                run_config = self.runs[run_id]
                run_info = await self.tracker.get_run_info(run_id)

                comparison["runs"][run_id] = {
                    "config": run_config.to_dict(),
                    "info": run_info,
                }

        return comparison

    def get_tracking_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get tracking history."""
        return self.tracking_history[-limit:]


# Context manager for experiment tracking
@asynccontextmanager
async def track_experiment(
    tracker: DistributedExperimentTracker,
    experiment_config: ExperimentConfig,
    run_config: RunConfig,
):
    """Context manager for experiment tracking."""
    try:
        # Create experiment and start run
        experiment_id = await tracker.create_experiment(experiment_config)
        run_config.experiment_id = experiment_id
        run_id = await tracker.start_run(run_config)

        yield run_id

    except Exception as e:
        # End run with failed status
        await tracker.end_run(run_id, ExperimentStatus.FAILED)
        raise

    finally:
        # End run with completed status
        if "run_id" in locals():
            await tracker.end_run(run_id, ExperimentStatus.COMPLETED)


# Example usage
async def example_usage():
    """Example usage of distributed experiment tracking."""
    # Create tracker with MLflow backend
    tracker = DistributedExperimentTracker(TrackingBackend.MLFLOW)

    # Create experiment AI
    experiment_config = ExperimentConfig(
        name="pytorch_mlp_experiment",
        description="Testing MLP hyperparameters",
        tags=["pytorch", "mlp", "classification"],
        parameters={"dataset": "cifar10", "model_type": "mlp"},
    )

    # Create run config
    run_config = RunConfig(
        name="run_001",
        description="Testing with learning rate 0.001",
        parameters={
            "learning_rate": 0.001,
            "batch_size": 32,
            "hidden_size": 256,
            "dropout": 0.2,
        },
        tags=["baseline", "lr_001"],
    )

    # Track experiment
    async with track_experiment(tracker, experiment_config, run_config) as run_id:
        # Simulate training loop
        for epoch in range(10):
            # Simulate metrics
            train_loss = 1.0 - epoch * 0.1
            val_loss = 1.2 - epoch * 0.08
            accuracy = epoch * 0.1

            # Log metrics
            await tracker.log_metric(run_id, "train_loss", train_loss, step=epoch)
            await tracker.log_metric(run_id, "val_loss", val_loss, step=epoch)
            await tracker.log_metric(run_id, "accuracy", accuracy, step=epoch)

            # Simulate training time
            await asyncio.sleep(0.1)

    # Get experiment summary
    summary = await tracker.get_experiment_summary(experiment_config.experiment_id)
    print(f"Experiment summary: {summary}")


if __name__ == "__main__":
    asyncio.run(example_usage())
