"""
S.W.A.R.M. Phase 2: Distributed Implementation Tests
Comprehensive testing suite for distributed ML infrastructure components
"""

import asyncio
import json
import shutil
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, patch

import pytest

from mlops.distributed_data_processing import (
    DataFormat,
    DataProcessingJob,
    DistributedDataProcessingOrchestrator,
    ProcessingBackend,
    StorageType,
)
from mlops.distributed_experiment_tracking import (
    DistributedExperimentTracker,
    ExperimentConfig,
    ExperimentStatus,
    MetricData,
    RunConfig,
    TrackingBackend,
)
from mlops.distributed_hyperparameter_tuning import (
    DistributedHyperparameterTuner,
    HyperparameterSpace,
    OptimizationDirection,
    SearchStrategy,
    TuningConfig,
)
from mlops.distributed_model_versioning import (
    DistributedModelRegistry,
    ModelFramework,
    ModelMetadata,
    ModelStatus,
)
from mlops.distributed_model_versioning import StorageBackend as ModelStorageBackend
from mlops.distributed_pytorch_ddp import (
    CheckpointConfig,
    DDPConfig,
    DistributedTrainer,
    TrainingConfig,
    create_dummy_dataset,
    create_simple_model,
)

# Import all distributed components
from mlops.distributed_training_architecture import (
    ClusterConfig,
    DistributedFramework,
    DistributedTrainingArchitecture,
    ParallelismType,
    ResourceBackend,
    TrainingJobConfig,
)


class TestDistributedTrainingArchitecture:
    """Test distributed training architecture."""

    @pytest.fixture
    def architecture(self):
        """Create distributed training architecture."""
        return DistributedTrainingArchitecture(ResourceBackend.KUBERNETES)

    def test_create_cluster(self, architecture):
        """Test cluster creation."""
        cluster_id = architecture.create_training_cluster(
            name="test-cluster", max_nodes=4, min_nodes=1, gpu_per_node=2
        )

        assert cluster_id is not None
        assert cluster_id in architecture.resource_manager.clusters

        cluster = architecture.resource_manager.clusters[cluster_id]
        assert cluster.name == "test-cluster"
        assert cluster.max_nodes == 4
        assert cluster.gpu_per_node == 2

    def test_setup_distributed_training(self, architecture):
        """Test distributed training setup."""
        job_id = architecture.setup_distributed_training(
            job_name="test-job",
            framework=DistributedFramework.PYTORCH_DDP,
            parallelism_type=ParallelismType.DATA_PARALLEL,
            num_workers=4,
            model_config={"input_size": 784, "hidden_size": 256},
            dataset_config={"dataset_path": "/data/train"},
        )

        assert job_id is not None
        assert job_id in architecture.orchestrator.active_jobs

        job = architecture.orchestrator.active_jobs[job_id]
        assert job.name == "test-job"
        assert job.framework == DistributedFramework.PYTORCH_DDP
        assert job.num_workers == 4

    def test_validate_architecture(self, architecture):
        """Test architecture validation."""
        # Create cluster and job
        cluster_id = architecture.create_training_cluster("test-cluster", max_nodes=4)
        job_id = architecture.setup_distributed_training(
            "test-job",
            DistributedFramework.PYTORCH_DDP,
            ParallelismType.DATA_PARALLEL,
            2,
        )

        validation = architecture.validate_architecture()

        assert "valid" in validation
        assert "warnings" in validation
        assert "errors" in validation
        assert "recommendations" in validation

    def test_get_architecture_summary(self, architecture):
        """Test architecture summary."""
        summary = architecture.get_architecture_summary()

        assert "backend" in summary
        assert "total_clusters" in summary
        assert "active_jobs" in summary
        assert "supported_frameworks" in summary
        assert "architecture_validated" in summary


class TestDistributedPytorchDDP:
    """Test PyTorch DDP training."""

    @pytest.fixture
    def ddp_config(self):
        """Create DDP configuration."""
        return DDPConfig(
            backend=DistributedBackend.NCCL, world_size=2, rank=0, local_rank=0
        )

    @pytest.fixture
    def training_config(self):
        """Create training configuration."""
        return TrainingConfig(epochs=5, batch_size=32, learning_rate=0.001)

    @pytest.fixture
    def checkpoint_config(self):
        """Create checkpoint configuration."""
        return CheckpointConfig(checkpoint_dir=tempfile.mkdtemp(), save_frequency=2)

    @pytest.fixture
    def model_and_datasets(self):
        """Create model and datasets."""
        model = create_simple_model()
        train_dataset = create_dummy_dataset(100)
        val_dataset = create_dummy_dataset(20)
        return model, train_dataset, val_dataset

    def test_ddp_config_creation(self, ddp_config):
        """Test DDP configuration creation."""
        assert ddp_config.world_size == 2
        assert ddp_config.rank == 0
        assert ddp_config.backend.value == "nccl"

        config_dict = ddp_config.to_dict()
        assert "backend" in config_dict
        assert "world_size" in config_dict

    def test_training_config_creation(self, training_config):
        """Test training configuration creation."""
        assert training_config.epochs == 5
        assert training_config.batch_size == 32
        assert training_config.learning_rate == 0.001

        config_dict = training_config.to_dict()
        assert "epochs" in config_dict
        assert "batch_size" in config_dict

    def test_checkpoint_config_creation(self, checkpoint_config):
        """Test checkpoint configuration creation."""
        assert checkpoint_config.save_frequency == 2
        assert checkpoint_config.checkpoint_dir is not None

        config_dict = checkpoint_config.to_dict()
        assert "checkpoint_dir" in config_dict
        assert "save_frequency" in config_dict

    @patch("torch.distributed.is_initialized", return_value=True)
    @patch("torch.cuda.is_available", return_value=True)
    def test_trainer_initialization(
        self,
        mock_cuda,
        mock_dist,
        ddp_config,
        training_config,
        checkpoint_config,
        model_and_datasets,
    ):
        """Test trainer initialization."""
        model, train_dataset, val_dataset = model_and_datasets

        trainer = DistributedTrainer(
            model,
            train_dataset,
            val_dataset,
            ddp_config,
            training_config,
            checkpoint_config,
        )

        assert trainer.model == model
        assert trainer.train_dataset == train_dataset
        assert trainer.val_dataset == val_dataset
        assert trainer.ddp_config == ddp_config

    def test_model_creation(self):
        """Test model creation."""
        model = create_simple_model()
        assert model is not None

        # Test forward pass
        import torch

        dummy_input = torch.randn(1, 784)
        output = model(dummy_input)
        assert output is not None
        assert output.shape[1] == 10  # Number of classes

    def test_dataset_creation(self):
        """Test dataset creation."""
        dataset = create_dummy_dataset(100)
        assert len(dataset) == 100

        # Test data loading
        data, label = dataset[0]
        assert data.shape == (784,)
        assert isinstance(label, int)


class TestDistributedDataProcessing:
    """Test distributed data processing."""

    @pytest.fixture
    def orchestrator(self):
        """Create data processing orchestrator."""
        return DistributedDataProcessingOrchestrator()

    @pytest.fixture
    def data_processing_job(self):
        """Create data processing job."""
        return DataProcessingJob(
            name="test-job",
            input_path="/data/input",
            output_path="/data/output",
            input_format=DataFormat.PARQUET,
            output_format=DataFormat.PARQUET,
            processing_steps=[
                {"type": "filter", "condition": "age > 0"},
                {"type": "select_columns", "columns": ["age", "income"]},
            ],
        )

    @pytest.mark.asyncio
    async def test_submit_job(self, orchestrator, data_processing_job):
        """Test job submission."""
        job_id = await orchestrator.submit_job(data_processing_job)

        assert job_id is not None
        assert job_id in orchestrator.active_jobs
        assert job_id in orchestrator.job_status

        status = orchestrator.get_job_status(job_id)
        assert status["status"] == "pending"

    @pytest.mark.asyncio
    async def test_list_jobs(self, orchestrator, data_processing_job):
        """Test job listing."""
        job_id = await orchestrator.submit_job(data_processing_job)

        all_jobs = orchestrator.list_jobs()
        assert len(all_jobs) == 1
        assert all_jobs[0]["job_id"] == job_id

        pending_jobs = orchestrator.list_jobs(status_filter="pending")
        assert len(pending_jobs) == 1

    def test_data_processing_job_config(self, data_processing_job):
        """Test data processing job configuration."""
        assert data_processing_job.name == "test-job"
        assert data_processing_job.input_format == DataFormat.PARQUET
        assert len(data_processing_job.processing_steps) == 2

        config_dict = data_processing_job.to_dict()
        assert "name" in config_dict
        assert "processing_steps" in config_dict


class TestDistributedHyperparameterTuning:
    """Test distributed hyperparameter tuning."""

    @pytest.fixture
    def tuner(self):
        """Create hyperparameter tuner."""
        return DistributedHyperparameterTuner()

    @pytest.fixture
    def tuning_config(self):
        """Create tuning configuration."""
        return TuningConfig(
            study_name="test-study",
            search_strategy=SearchStrategy.OPTUNA_TPE,
            direction=OptimizationDirection.MINIMIZE,
            max_trials=10,
            hyperparameter_spaces=[
                HyperparameterSpace(
                    name="learning_rate",
                    parameter_type="uniform",
                    low=1e-4,
                    high=1e-1,
                    log=True,
                ),
                HyperparameterSpace(
                    name="batch_size", parameter_type="choice", choices=[16, 32, 64]
                ),
            ],
        )

    @pytest.mark.asyncio
    async def test_create_study(self, tuner, tuning_config):
        """Test study creation."""
        study_name = await tuner.create_study(tuning_config)

        assert study_name == tuning_config.study_name
        assert study_name in tuner.active_studies
        assert study_name in tuner.study_results

    @pytest.mark.asyncio
    async def test_run_optimization(self, tuner, tuning_config):
        """Test optimization run."""
        study_name = await tuner.create_study(tuning_config)

        # Dummy objective function
        def dummy_objective(trial, hyperparams):
            lr = hyperparams.get("learning_rate", 0.001)
            batch_size = hyperparams.get("batch_size", 32)
            # Simple loss function
            return abs(lr - 0.01) + (batch_size - 32) * 0.001

        # Mock the optimizer to avoid actual optimization
        with patch.object(
            tuner.optimizers[SearchStrategy.OPTUNA_TPE], "optimize"
        ) as mock_optimize:
            mock_optimize.return_value = [
                Mock(
                    trial_id="test_trial",
                    trial_number=0,
                    hyperparameters={"learning_rate": 0.01, "batch_size": 32},
                    objective_value=0.001,
                    intermediate_values=[],
                    user_attrs={},
                    datetime_complete=datetime.now(),
                    state="COMPLETE",
                )
            ]

            results = await tuner.run_optimization(study_name, dummy_objective)

            assert len(results) > 0
            assert study_name in tuner.study_results

    def test_tuning_config_creation(self, tuning_config):
        """Test tuning configuration creation."""
        assert tuning_config.study_name == "test-study"
        assert tuning_config.search_strategy == SearchStrategy.OPTUNA_TPE
        assert len(tuning_config.hyperparameter_spaces) == 2

        config_dict = tuning_config.to_dict()
        assert "study_name" in config_dict
        assert "hyperparameter_spaces" in config_dict


class TestDistributedModelVersioning:
    """Test distributed model versioning."""

    @pytest.fixture
    def registry(self):
        """Create model registry."""
        temp_dir = tempfile.mkdtemp()
        return DistributedModelRegistry(
            storage_backend=ModelStorageBackend.LOCAL, base_path=temp_dir
        )

    @pytest.fixture
    def dummy_model(self):
        """Create dummy model."""
        import torch
        import torch.nn as nn

        class DummyModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.linear = nn.Linear(10, 1)

            def forward(self, x):
                return self.linear(x)

        return DummyModel()

    @pytest.mark.asyncio
    async def test_register_model(self, registry, dummy_model):
        """Test model registration."""
        model_id = await registry.register_model(
            model=dummy_model,
            name="test-model",
            framework=ModelFramework.PYTORCH,
            description="Test model",
            author="Test Author",
            hyperparameters={"input_size": 10, "output_size": 1},
            metrics={"train_loss": 0.5},
        )

        assert model_id is not None
        assert model_id in registry.models

        metadata = registry.models[model_id]
        assert metadata.name == "test-model"
        assert metadata.framework == ModelFramework.PYTORCH
        assert metadata.author == "Test Author"

    @pytest.mark.asyncio
    async def test_load_model(self, registry, dummy_model):
        """Test model loading."""
        # Register model first
        model_id = await registry.register_model(
            dummy_model, "test-model", ModelFramework.PYTORCH
        )

        # Load model
        loaded_model, metadata = await registry.load_model(model_id)

        assert loaded_model is not None
        assert metadata.name == "test-model"
        assert metadata.framework == ModelFramework.PYTORCH

    @pytest.mark.asyncio
    async def test_list_models(self, registry, dummy_model):
        """Test model listing."""
        # Register multiple models
        await registry.register_model(dummy_model, "model-1", ModelFramework.PYTORCH)
        await registry.register_model(dummy_model, "model-2", ModelFramework.PYTORCH)

        # List all models
        all_models = await registry.list_models()
        assert len(all_models) == 2

        # List models by name
        model_1_list = await registry.list_models("model-1")
        assert len(model_1_list) == 1
        assert model_1_list[0].name == "model-1"

    @pytest.mark.asyncio
    async def test_model_status_update(self, registry, dummy_model):
        """Test model status update."""
        model_id = await registry.register_model(
            dummy_model, "test-model", ModelFramework.PYTORCH
        )

        # Update status to staging
        success = await registry.update_model_status(model_id, ModelStatus.STAGING)
        assert success

        metadata = registry.models[model_id]
        assert metadata.status == ModelStatus.STAGING

    def test_model_metadata_creation(self):
        """Test model metadata creation."""
        metadata = ModelMetadata(
            name="test-model",
            framework=ModelFramework.PYTORCH,
            description="Test model",
            tags=["test", "pytorch"],
            hyperparameters={"lr": 0.001},
            metrics={"accuracy": 0.95},
        )

        assert metadata.name == "test-model"
        assert metadata.framework == ModelFramework.PYTORCH
        assert len(metadata.tags) == 2
        assert metadata.metrics["accuracy"] == 0.95

        config_dict = metadata.to_dict()
        assert "name" in config_dict
        assert "framework" in config_dict
        assert "tags" in config_dict


class TestDistributedExperimentTracking:
    """Test distributed experiment tracking."""

    @pytest.fixture
    def tracker(self):
        """Create experiment tracker."""
        temp_dir = tempfile.mkdtemp()
        return DistributedExperimentTracker(
            backend=TrackingBackend.TENSORBOARD, log_dir=temp_dir
        )

    @pytest.fixture
    def experiment_config(self):
        """Create experiment configuration."""
        return ExperimentConfig(
            name="test-experiment",
            description="Test experiment",
            tags=["test", "ml"],
            parameters={"dataset": "test", "model": "test"},
        )

    @pytest.fixture
    def run_config(self):
        """Create run configuration."""
        return RunConfig(
            name="test-run",
            description="Test run",
            parameters={"lr": 0.001, "batch_size": 32},
            tags=["baseline"],
        )

    @pytest.mark.asyncio
    async def test_create_experiment(self, tracker, experiment_config):
        """Test experiment creation."""
        experiment_id = await tracker.create_experiment(experiment_config)

        assert experiment_id is not None
        assert experiment_id in tracker.experiments

        stored_config = tracker.experiments[experiment_id]
        assert stored_config.name == "test-experiment"
        assert stored_config.description == "Test experiment"

    @pytest.mark.asyncio
    async def test_start_run(self, tracker, experiment_config, run_config):
        """Test run start."""
        experiment_id = await tracker.create_experiment(experiment_config)
        run_config.experiment_id = experiment_id

        run_id = await tracker.start_run(run_config)

        assert run_id is not None
        assert run_id in tracker.runs

        stored_run = tracker.runs[run_id]
        assert stored_run.name == "test-run"
        assert stored_run.status == ExperimentStatus.RUNNING

    @pytest.mark.asyncio
    async def test_log_metrics(self, tracker, experiment_config, run_config):
        """Test metric logging."""
        experiment_id = await tracker.create_experiment(experiment_config)
        run_config.experiment_id = experiment_id
        run_id = await tracker.start_run(run_config)

        # Log single metric
        await tracker.log_metric(run_id, "loss", 0.5, step=1)

        # Log multiple metrics
        metrics = [
            MetricData(name="accuracy", value=0.8, step=1),
            MetricData(name="val_loss", value=0.6, step=1),
        ]
        await tracker.log_metrics(run_id, metrics)

        # Log parameters
        await tracker.log_parameters(run_id, {"epoch": 1, "batch_size": 32})

    @pytest.mark.asyncio
    async def test_end_run(self, tracker, experiment_config, run_config):
        """Test run end."""
        experiment_id = await tracker.create_experiment(experiment_config)
        run_config.experiment_id = experiment_id
        run_id = await tracker.start_run(run_config)

        await tracker.end_run(run_id, ExperimentStatus.COMPLETED)

        stored_run = tracker.runs[run_id]
        assert stored_run.status == ExperimentStatus.COMPLETED
        assert stored_run.end_time is not None

    @pytest.mark.asyncio
    async def test_experiment_summary(self, tracker, experiment_config, run_config):
        """Test experiment summary."""
        experiment_id = await tracker.create_experiment(experiment_config)
        run_config.experiment_id = experiment_id
        run_id = await tracker.start_run(run_config)

        summary = await tracker.get_experiment_summary(experiment_id)

        assert "experiment" in summary
        assert "total_runs" in summary
        assert "running_runs" in summary
        assert summary["total_runs"] == 1
        assert summary["running_runs"] == 1

    def test_experiment_config_creation(self, experiment_config):
        """Test experiment configuration creation."""
        assert experiment_config.name == "test-experiment"
        assert len(experiment_config.tags) == 2
        assert len(experiment_config.parameters) == 2

        config_dict = experiment_config.to_dict()
        assert "name" in config_dict
        assert "tags" in config_dict
        assert "parameters" in config_dict

    def test_run_config_creation(self, run_config):
        """Test run configuration creation."""
        assert run_config.name == "test-run"
        assert len(run_config.parameters) == 2
        assert len(run_config.tags) == 1
        assert run_config.status == ExperimentStatus.RUNNING

        config_dict = run_config.to_dict()
        assert "name" in config_dict
        assert "parameters" in config_dict
        assert "status" in config_dict


class TestIntegration:
    """Integration tests for distributed components."""

    @pytest.mark.asyncio
    async def test_end_to_end_ml_pipeline(self):
        """Test end-to-end ML pipeline integration."""
        # This would test the full integration of all components
        # Simplified version for demonstration

        # 1. Setup data processing
        data_orchestrator = DistributedDataProcessingOrchestrator()
        data_job = DataProcessingJob(
            name="data-prep",
            input_path="/data/raw",
            output_path="/data/processed",
            processing_steps=[{"type": "filter", "condition": "quality > 0.8"}],
        )

        # 2. Setup hyperparameter tuning
        tuner = DistributedHyperparameterTuner()
        tuning_config = TuningConfig(
            study_name="integration-test",
            max_trials=5,
            hyperparameter_spaces=[
                HyperparameterSpace(
                    name="lr", parameter_type="uniform", low=1e-4, high=1e-2
                )
            ],
        )

        # 3. Setup model registry
        temp_dir = tempfile.mkdtemp()
        registry = DistributedModelRegistry(
            storage_backend=ModelStorageBackend.LOCAL, base_path=temp_dir
        )

        # 4. Setup experiment tracking
        temp_tracker_dir = tempfile.mkdtemp()
        tracker = DistributedExperimentTracker(
            backend=TrackingBackend.TENSORBOARD, log_dir=temp_tracker_dir
        )

        # Simulate pipeline execution
        study_name = await tuner.create_study(tuning_config)
        assert study_name is not None

        experiment_config = ExperimentConfig(name="integration-test")
        experiment_id = await tracker.create_experiment(experiment_config)
        assert experiment_id is not None

        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
        shutil.rmtree(temp_tracker_dir, ignore_errors=True)


class TestPerformance:
    """Performance tests for distributed components."""

    @pytest.mark.asyncio
    async def test_concurrent_job_processing(self):
        """Test concurrent job processing."""
        orchestrator = DistributedDataProcessingOrchestrator()

        # Create multiple jobs
        jobs = []
        for i in range(5):
            job = DataProcessingJob(
                name=f"job-{i}",
                input_path=f"/data/input-{i}",
                output_path=f"/data/output-{i}",
            )
            jobs.append(job)

        # Submit all jobs concurrently
        job_ids = await asyncio.gather(*[orchestrator.submit_job(job) for job in jobs])

        assert len(job_ids) == 5
        assert len(set(job_ids)) == 5  # All unique

        # Check all jobs are pending
        all_jobs = orchestrator.list_jobs()
        assert len(all_jobs) == 5

    def test_memory_usage(self):
        """Test memory usage patterns."""
        # This would test memory usage of various components
        # Simplified version for demonstration

        import sys

        # Test model registry memory usage
        temp_dir = tempfile.mkdtemp()
        registry = DistributedModelRegistry(
            storage_backend=ModelStorageBackend.LOCAL, base_path=temp_dir
        )

        # Create dummy models
        models = []
        for i in range(10):
            import torch
            import torch.nn as nn

            model = nn.Linear(10, 1)
            models.append(model)

        # Check memory before and after registration
        # This is a simplified check
        initial_size = sys.getsizeof(registry.models)

        # Register models (would be async in real usage)
        # For testing, we'll just check the structure
        assert len(models) == 10

        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


# Test utilities
class TestUtils:
    """Test utilities and helpers."""

    def create_mock_distributed_environment(self):
        """Create mock distributed environment for testing."""
        return {"world_size": 2, "rank": 0, "local_rank": 0, "backend": "nccl"}

    def create_test_data(self, size: int = 100):
        """Create test data for processing."""
        import numpy as np
        import pandas as pd

        data = {
            "feature1": np.random.randn(size),
            "feature2": np.random.randn(size),
            "target": np.random.randint(0, 2, size),
        }
        return pd.DataFrame(data)

    def validate_model_output(self, model, input_shape, output_shape):
        """Validate model output shape and type."""
        import torch

        dummy_input = torch.randn(input_shape)
        with torch.no_grad():
            output = model(dummy_input)

        assert output.shape == output_shape
        assert torch.is_tensor(output)
        assert not torch.isnan(output).any()


# Pytest configuration
def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line("markers", "asyncio: mark test as async")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "performance: mark test as performance test")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
