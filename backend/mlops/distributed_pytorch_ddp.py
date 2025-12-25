"""
S.W.A.R.M. Phase 2: Distributed PyTorch DDP Training Implementation
Production-ready distributed training with PyTorch DistributedDataParallel
"""

import asyncio
import json
import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

# PyTorch imports
try:
    import torch
    import torch.distributed as dist
    import torch.nn as nn
    import torch.optim as optim
    from torch.nn.parallel import DistributedDataParallel as DDP
    from torch.utils.data import DataLoader, DistributedSampler
    from torch.utils.tensorboard import SummaryWriter

    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False

# MLflow imports for experiment tracking
try:
    import mlflow
    import mlflow.pytorch

    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False

# Ray imports for hyperparameter tuning
try:
    import ray
    from ray import tune
    from ray.train import Trainer
    from ray.train.torch import TorchTrainer

    RAY_AVAILABLE = True
except ImportError:
    RAY_AVAILABLE = False

logger = logging.getLogger("raptorflow.distributed_pytorch")


class DistributedBackend(Enum):
    """Distributed training backends."""

    NCCL = "nccl"
    GLOO = "gloo"
    MPI = "mpi"


class OptimizerType(Enum):
    """Optimizer types."""

    ADAM = "adam"
    SGD = "sgd"
    ADAMW = "adamw"
    RMSPROP = "rmsprop"


class SchedulerType(Enum):
    """Learning rate scheduler types."""

    STEP = "step"
    EXPONENTIAL = "exponential"
    COSINE = "cosine"
    PLATEAU = "plateau"
    ONECYCLE = "onecycle"


@dataclass
class DDPConfig:
    """DistributedDataParallel configuration."""

    backend: DistributedBackend = DistributedBackend.NCCL
    world_size: int = 1
    rank: int = 0
    local_rank: int = 0
    master_addr: str = "localhost"
    master_port: str = "12355"
    init_method: str = "env://"
    timeout_seconds: int = 1800  # 30 minutes

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "backend": self.backend.value,
            "world_size": self.world_size,
            "rank": self.rank,
            "local_rank": self.local_rank,
            "master_addr": self.master_addr,
            "master_port": self.master_port,
            "init_method": self.init_method,
            "timeout_seconds": self.timeout_seconds,
        }


@dataclass
class TrainingConfig:
    """Training configuration."""

    epochs: int = 100
    batch_size: int = 32
    learning_rate: float = 0.001
    weight_decay: float = 1e-4
    optimizer_type: OptimizerType = OptimizerType.ADAM
    scheduler_type: SchedulerType = SchedulerType.STEP
    scheduler_params: Dict[str, Any] = field(default_factory=dict)
    gradient_clip_value: Optional[float] = None
    mixed_precision: bool = False
    gradient_accumulation_steps: int = 1
    early_stopping_patience: int = 10
    checkpoint_frequency: int = 10
    validation_frequency: int = 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "epochs": self.epochs,
            "batch_size": self.batch_size,
            "learning_rate": self.learning_rate,
            "weight_decay": self.weight_decay,
            "optimizer_type": self.optimizer_type.value,
            "scheduler_type": self.scheduler_type.value,
            "scheduler_params": self.scheduler_params,
            "gradient_clip_value": self.gradient_clip_value,
            "mixed_precision": self.mixed_precision,
            "gradient_accumulation_steps": self.gradient_accumulation_steps,
            "early_stopping_patience": self.early_stopping_patience,
            "checkpoint_frequency": self.checkpoint_frequency,
            "validation_frequency": self.validation_frequency,
        }


@dataclass
class CheckpointConfig:
    """Checkpoint configuration."""

    checkpoint_dir: str = "./checkpoints"
    save_frequency: int = 10
    save_best_only: bool = True
    save_optimizer_state: bool = True
    max_checkpoints_to_keep: int = 5
    checkpoint_format: str = "pytorch"  # pytorch, safetensors

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "checkpoint_dir": self.checkpoint_dir,
            "save_frequency": self.save_frequency,
            "save_best_only": self.save_best_only,
            "save_optimizer_state": self.save_optimizer_state,
            "max_checkpoints_to_keep": self.max_checkpoints_to_keep,
            "checkpoint_format": self.checkpoint_format,
        }


class DistributedInitializer:
    """Distributed training initialization."""

    @staticmethod
    def setup_distributed(config: DDPConfig) -> bool:
        """Setup distributed training environment."""
        if not PYTORCH_AVAILABLE:
            logger.error("PyTorch is not available")
            return False

        try:
            # Set environment variables
            os.environ["MASTER_ADDR"] = config.master_addr
            os.environ["MASTER_PORT"] = config.master_port
            os.environ["RANK"] = str(config.rank)
            os.environ["WORLD_SIZE"] = str(config.world_size)
            os.environ["LOCAL_RANK"] = str(config.local_rank)

            # Initialize process group
            dist.init_process_group(
                backend=config.backend.value,
                init_method=config.init_method,
                world_size=config.world_size,
                rank=config.rank,
                timeout=timedelta(seconds=config.timeout_seconds),
            )

            # Set device
            if torch.cuda.is_available():
                torch.cuda.set_device(config.local_rank)
                device = torch.device(f"cuda:{config.local_rank}")
            else:
                device = torch.device("cpu")

            logger.info(
                f"Distributed training initialized on rank {config.rank}/{config.world_size}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to initialize distributed training: {str(e)}")
            return False

    @staticmethod
    def cleanup_distributed():
        """Cleanup distributed training."""
        if dist.is_initialized():
            dist.destroy_process_group()


class ModelManager:
    """Model management for distributed training."""

    def __init__(self, model: nn.Module, config: DDPConfig):
        self.model = model
        self.config = config
        self.ddp_model = None
        self.device = None

    def setup_model(self) -> nn.Module:
        """Setup model for distributed training."""
        if not PYTORCH_AVAILABLE:
            raise ImportError("PyTorch is required")

        # Set device
        if torch.cuda.is_available():
            self.device = torch.device(f"cuda:{self.config.local_rank}")
            self.model = self.model.to(self.device)
        else:
            self.device = torch.device("cpu")
            self.model = self.model.to(self.device)

        # Wrap with DDP
        if dist.is_initialized() and self.config.world_size > 1:
            self.ddp_model = DDP(
                self.model,
                device_ids=(
                    [self.config.local_rank] if torch.cuda.is_available() else None
                ),
                output_device=(
                    self.config.local_rank if torch.cuda.is_available() else None
                ),
                find_unused_parameters=False,
            )
            return self.ddp_model
        else:
            return self.model

    def get_model(self) -> nn.Module:
        """Get the appropriate model (DDP or original)."""
        return self.ddp_model if self.ddp_model is not None else self.model

    def unwrap_model(self) -> nn.Module:
        """Unwrap DDP model to get original model."""
        if self.ddp_model is not None:
            return self.ddp_model.module
        return self.model


class OptimizerManager:
    """Optimizer management for distributed training."""

    @staticmethod
    def create_optimizer(model: nn.Module, config: TrainingConfig) -> optim.Optimizer:
        """Create optimizer based on configuration."""
        if not PYTORCH_AVAILABLE:
            raise ImportError("PyTorch is required")

        if config.optimizer_type == OptimizerType.ADAM:
            optimizer = optim.Adam(
                model.parameters(),
                lr=config.learning_rate,
                weight_decay=config.weight_decay,
            )
        elif config.optimizer_type == OptimizerType.SGD:
            optimizer = optim.SGD(
                model.parameters(),
                lr=config.learning_rate,
                weight_decay=config.weight_decay,
                momentum=0.9,
            )
        elif config.optimizer_type == OptimizerType.ADAMW:
            optimizer = optim.AdamW(
                model.parameters(),
                lr=config.learning_rate,
                weight_decay=config.weight_decay,
            )
        elif config.optimizer_type == OptimizerType.RMSPROP:
            optimizer = optim.RMSprop(
                model.parameters(),
                lr=config.learning_rate,
                weight_decay=config.weight_decay,
            )
        else:
            raise ValueError(f"Unsupported optimizer type: {config.optimizer_type}")

        return optimizer

    @staticmethod
    def create_scheduler(
        optimizer: optim.Optimizer, config: TrainingConfig
    ) -> optim.lr_scheduler._LRScheduler:
        """Create learning rate scheduler."""
        if not PYTORCH_AVAILABLE:
            raise ImportError("PyTorch is required")

        if config.scheduler_type == SchedulerType.STEP:
            step_size = config.scheduler_params.get("step_size", 30)
            gamma = config.scheduler_params.get("gamma", 0.1)
            scheduler = optim.lr_scheduler.StepLR(
                optimizer, step_size=step_size, gamma=gamma
            )
        elif config.scheduler_type == SchedulerType.EXPONENTIAL:
            gamma = config.scheduler_params.get("gamma", 0.95)
            scheduler = optim.lr_scheduler.ExponentialLR(optimizer, gamma=gamma)
        elif config.scheduler_type == SchedulerType.COSINE:
            T_max = config.scheduler_params.get("T_max", config.epochs)
            scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=T_max)
        elif config.scheduler_type == SchedulerType.PLATEAU:
            patience = config.scheduler_params.get("patience", 5)
            factor = config.scheduler_params.get("factor", 0.5)
            scheduler = optim.lr_scheduler.ReduceLROnPlateau(
                optimizer, mode="min", patience=patience, factor=factor
            )
        elif config.scheduler_type == SchedulerType.ONECYCLE:
            max_lr = config.scheduler_params.get("max_lr", config.learning_rate)
            steps_per_epoch = config.scheduler_params.get("steps_per_epoch", 100)
            scheduler = optim.lr_scheduler.OneCycleLR(
                optimizer,
                max_lr=max_lr,
                steps_per_epoch=steps_per_epoch,
                epochs=config.epochs,
            )
        else:
            raise ValueError(f"Unsupported scheduler type: {config.scheduler_type}")

        return scheduler


class CheckpointManager:
    """Checkpoint management for distributed training."""

    def __init__(self, config: CheckpointConfig, ddp_config: DDPConfig):
        self.config = config
        self.ddp_config = ddp_config
        self.best_metric = float("inf")
        self.checkpoint_history: List[Dict[str, Any]] = []

    def save_checkpoint(
        self,
        model: nn.Module,
        optimizer: optim.Optimizer,
        scheduler: optim.lr_scheduler._LRScheduler,
        epoch: int,
        metrics: Dict[str, float],
        is_best: bool = False,
    ) -> str:
        """Save training checkpoint."""
        if not PYTORCH_AVAILABLE:
            raise ImportError("PyTorch is required")

        # Only save on rank 0
        if self.ddp_config.rank != 0:
            return ""

        # Create checkpoint directory
        os.makedirs(self.config.checkpoint_dir, exist_ok=True)

        # Prepare checkpoint data
        checkpoint_data = {
            "epoch": epoch,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": (
                optimizer.state_dict() if self.config.save_optimizer_state else None
            ),
            "scheduler_state_dict": scheduler.state_dict() if scheduler else None,
            "metrics": metrics,
            "config": {
                "ddp": self.ddp_config.to_dict(),
                "checkpoint": self.config.to_dict(),
            },
        }

        # Save checkpoint
        checkpoint_path = os.path.join(
            self.config.checkpoint_dir, f"checkpoint_epoch_{epoch}.pth"
        )

        torch.save(checkpoint_data, checkpoint_path)

        # Save best model if applicable
        if is_best or not self.config.save_best_only:
            best_path = os.path.join(self.config.checkpoint_dir, "best_model.pth")
            torch.save(checkpoint_data, best_path)

        # Update checkpoint history
        self.checkpoint_history.append(
            {
                "epoch": epoch,
                "path": checkpoint_path,
                "metrics": metrics,
                "timestamp": datetime.now().isoformat(),
            }
        )

        # Cleanup old checkpoints
        self._cleanup_old_checkpoints()

        logger.info(f"Checkpoint saved: {checkpoint_path}")
        return checkpoint_path

    def load_checkpoint(
        self,
        model: nn.Module,
        optimizer: optim.Optimizer,
        scheduler: optim.lr_scheduler._LRScheduler,
        checkpoint_path: str,
    ) -> Dict[str, Any]:
        """Load training checkpoint."""
        if not PYTORCH_AVAILABLE:
            raise ImportError("PyTorch is required")

        if not os.path.exists(checkpoint_path):
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")

        checkpoint_data = torch.load(checkpoint_path, map_location="cpu")

        # Load model state
        model.load_state_dict(checkpoint_data["model_state_dict"])

        # Load optimizer state
        if self.config.save_optimizer_state and checkpoint_data["optimizer_state_dict"]:
            optimizer.load_state_dict(checkpoint_data["optimizer_state_dict"])

        # Load scheduler state
        if checkpoint_data["scheduler_state_dict"] and scheduler:
            scheduler.load_state_dict(checkpoint_data["scheduler_state_dict"])

        logger.info(f"Checkpoint loaded: {checkpoint_path}")
        return checkpoint_data

    def _cleanup_old_checkpoints(self):
        """Cleanup old checkpoints."""
        if self.ddp_config.rank != 0:
            return

        # Get all checkpoint files
        checkpoint_files = []
        for file in os.listdir(self.config.checkpoint_dir):
            if file.startswith("checkpoint_epoch_") and file.endswith(".pth"):
                file_path = os.path.join(self.config.checkpoint_dir, file)
                epoch = int(file.split("_")[2].split(".")[0])
                checkpoint_files.append((epoch, file_path))

        # Sort by epoch and keep only the latest
        checkpoint_files.sort(key=lambda x: x[0], reverse=True)

        # Remove excess checkpoints
        for epoch, file_path in checkpoint_files[self.config.max_checkpoints_to_keep :]:
            try:
                os.remove(file_path)
                logger.info(f"Removed old checkpoint: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to remove checkpoint {file_path}: {str(e)}")


class MetricsTracker:
    """Metrics tracking for distributed training."""

    def __init__(self, ddp_config: DDPConfig):
        self.ddp_config = ddp_config
        self.metrics_history: Dict[str, List[float]] = {}
        self.tb_writer: Optional[SummaryWriter] = None

        # Setup TensorBoard writer on rank 0
        if self.ddp_config.rank == 0:
            log_dir = f"./logs/tensorboard/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.tb_writer = SummaryWriter(log_dir)

    def log_scalar(self, name: str, value: float, step: int):
        """Log scalar metric."""
        if name not in self.metrics_history:
            self.metrics_history[name] = []

        self.metrics_history[name].append(value)

        # Log to TensorBoard on rank 0
        if self.tb_writer:
            self.tb_writer.add_scalar(name, value, step)

    def log_scalars(self, metrics: Dict[str, float], step: int):
        """Log multiple scalar metrics."""
        for name, value in metrics.items():
            self.log_scalar(name, value, step)

    def log_histogram(self, name: str, values: torch.Tensor, step: int):
        """Log histogram."""
        if self.tb_writer:
            self.tb_writer.add_histogram(name, values, step)

    def log_learning_rate(self, lr: float, step: int):
        """Log learning rate."""
        self.log_scalar("learning_rate", lr, step)

    def close(self):
        """Close metrics tracker."""
        if self.tb_writer:
            self.tb_writer.close()


class DistributedTrainer:
    """Main distributed training orchestrator."""

    def __init__(
        self,
        model: nn.Module,
        train_dataset,
        val_dataset,
        ddp_config: DDPConfig,
        training_config: TrainingConfig,
        checkpoint_config: CheckpointConfig,
    ):
        self.model = model
        self.train_dataset = train_dataset
        self.val_dataset = val_dataset
        self.ddp_config = ddp_config
        self.training_config = training_config
        self.checkpoint_config = checkpoint_config

        # Initialize components
        self.model_manager = ModelManager(model, ddp_config)
        self.optimizer = None
        self.scheduler = None
        self.checkpoint_manager = CheckpointManager(checkpoint_config, ddp_config)
        self.metrics_tracker = MetricsTracker(ddp_config)

        # Training state
        self.current_epoch = 0
        self.best_val_loss = float("inf")
        self.early_stopping_counter = 0
        self.training_complete = False

    def setup(self) -> bool:
        """Setup training components."""
        try:
            # Initialize distributed training
            if not DistributedInitializer.setup_distributed(self.ddp_config):
                return False

            # Setup model
            self.model = self.model_manager.setup_model()

            # Create optimizer and scheduler
            self.optimizer = OptimizerManager.create_optimizer(
                self.model, self.training_config
            )
            self.scheduler = OptimizerManager.create_scheduler(
                self.optimizer, self.training_config
            )

            # Setup data loaders
            self._setup_data_loaders()

            logger.info("Distributed training setup completed")
            return True

        except Exception as e:
            logger.error(f"Failed to setup training: {str(e)}")
            return False

    def _setup_data_loaders(self):
        """Setup distributed data loaders."""
        if not PYTORCH_AVAILABLE:
            raise ImportError("PyTorch is required")

        # Create distributed samplers
        train_sampler = DistributedSampler(
            self.train_dataset,
            num_replicas=self.ddp_config.world_size,
            rank=self.ddp_config.rank,
            shuffle=True,
        )

        val_sampler = DistributedSampler(
            self.val_dataset,
            num_replicas=self.ddp_config.world_size,
            rank=self.ddp_config.rank,
            shuffle=False,
        )

        # Create data loaders
        self.train_loader = DataLoader(
            self.train_dataset,
            batch_size=self.training_config.batch_size,
            sampler=train_sampler,
            num_workers=4,
            pin_memory=torch.cuda.is_available(),
        )

        self.val_loader = DataLoader(
            self.val_dataset,
            batch_size=self.training_config.batch_size,
            sampler=val_sampler,
            num_workers=4,
            pin_memory=torch.cuda.is_available(),
        )

    def train(self) -> Dict[str, Any]:
        """Main training loop."""
        if not self.setup():
            return {"success": False, "error": "Setup failed"}

        try:
            # Log experiment with MLflow
            if MLFLOW_AVAILABLE and self.ddp_config.rank == 0:
                mlflow.start_run()
                mlflow.log_params(self.training_config.to_dict())
                mlflow.log_params(self.ddp_config.to_dict())

            for epoch in range(self.current_epoch, self.training_config.epochs):
                self.current_epoch = epoch

                # Set epoch for distributed sampler
                if hasattr(self.train_loader.sampler, "set_epoch"):
                    self.train_loader.sampler.set_epoch(epoch)

                # Training phase
                train_metrics = self._train_epoch(epoch)

                # Validation phase
                if epoch % self.training_config.validation_frequency == 0:
                    val_metrics = self._validate_epoch(epoch)

                    # Update learning rate scheduler
                    if self.training_config.scheduler_type == SchedulerType.PLATEAU:
                        self.scheduler.step(val_metrics["loss"])
                    else:
                        self.scheduler.step()

                    # Check for early stopping
                    if val_metrics["loss"] < self.best_val_loss:
                        self.best_val_loss = val_metrics["loss"]
                        self.early_stopping_counter = 0
                        is_best = True
                    else:
                        self.early_stopping_counter += 1
                        is_best = False

                    # Save checkpoint
                    if epoch % self.training_config.checkpoint_frequency == 0:
                        self.checkpoint_manager.save_checkpoint(
                            self.model,
                            self.optimizer,
                            self.scheduler,
                            epoch,
                            val_metrics,
                            is_best,
                        )

                    # Log metrics
                    if self.ddp_config.rank == 0:
                        self.metrics_tracker.log_scalars(train_metrics, epoch)
                        self.metrics_tracker.log_scalars(val_metrics, epoch)

                        if MLFLOW_AVAILABLE:
                            mlflow.log_metrics(train_metrics, step=epoch)
                            mlflow.log_metrics(val_metrics, step=epoch)

                    # Early stopping check
                    if (
                        self.early_stopping_counter
                        >= self.training_config.early_stopping_patience
                    ):
                        logger.info(f"Early stopping triggered at epoch {epoch}")
                        break

            # Save final checkpoint
            if self.ddp_config.rank == 0:
                self.checkpoint_manager.save_checkpoint(
                    self.model,
                    self.optimizer,
                    self.scheduler,
                    self.current_epoch,
                    {"loss": self.best_val_loss},
                    True,
                )

            self.training_complete = True

            # Return training summary
            return {
                "success": True,
                "epochs_completed": self.current_epoch + 1,
                "best_val_loss": self.best_val_loss,
                "final_metrics": self.metrics_tracker.metrics_history,
            }

        except Exception as e:
            logger.error(f"Training failed: {str(e)}")
            return {"success": False, "error": str(e)}

        finally:
            self.cleanup()

    def _train_epoch(self, epoch: int) -> Dict[str, float]:
        """Train for one epoch."""
        self.model.train()
        total_loss = 0.0
        num_batches = 0

        for batch_idx, (data, target) in enumerate(self.train_loader):
            # Move data to device
            if torch.cuda.is_available():
                data, target = data.cuda(self.ddp_config.local_rank), target.cuda(
                    self.ddp_config.local_rank
                )

            # Forward pass
            self.optimizer.zero_grad()
            output = self.model(data)
            loss = self._compute_loss(output, target)

            # Backward pass
            if self.training_config.gradient_accumulation_steps > 1:
                loss = loss / self.training_config.gradient_accumulation_steps

            loss.backward()

            # Gradient clipping
            if self.training_config.gradient_clip_value:
                torch.nn.utils.clip_grad_norm_(
                    self.model.parameters(), self.training_config.gradient_clip_value
                )

            # Optimizer step
            if (batch_idx + 1) % self.training_config.gradient_accumulation_steps == 0:
                self.optimizer.step()
                self.optimizer.zero_grad()

            total_loss += loss.item()
            num_batches += 1

        # Average loss across all processes
        avg_loss = total_loss / num_batches
        if dist.is_initialized():
            avg_loss = self._reduce_tensor(avg_loss)

        return {"train_loss": avg_loss}

    def _validate_epoch(self, epoch: int) -> Dict[str, float]:
        """Validate for one epoch."""
        self.model.eval()
        total_loss = 0.0
        num_batches = 0
        correct = 0
        total = 0

        with torch.no_grad():
            for data, target in self.val_loader:
                # Move data to device
                if torch.cuda.is_available():
                    data, target = data.cuda(self.ddp_config.local_rank), target.cuda(
                        self.ddp_config.local_rank
                    )

                # Forward pass
                output = self.model(data)
                loss = self._compute_loss(output, target)

                total_loss += loss.item()
                num_batches += 1

                # Calculate accuracy (for classification tasks)
                if hasattr(output, "argmax"):
                    pred = output.argmax(dim=1)
                    correct += (pred == target).sum().item()
                    total += target.size(0)

        # Average loss and accuracy across all processes
        avg_loss = total_loss / num_batches
        accuracy = correct / total if total > 0 else 0.0

        if dist.is_initialized():
            avg_loss = self._reduce_tensor(avg_loss)
            accuracy = self._reduce_tensor(accuracy)

        return {"val_loss": avg_loss, "val_accuracy": accuracy}

    def _compute_loss(self, output, target) -> torch.Tensor:
        """Compute loss (can be overridden for custom loss functions)."""
        if hasattr(target, "float"):
            return nn.functional.mse_loss(output, target.float())
        else:
            return nn.functional.cross_entropy(output, target)

    def _reduce_tensor(self, tensor: float) -> float:
        """Reduce tensor across all processes."""
        if not dist.is_initialized():
            return tensor

        # Convert to tensor
        tensor_tensor = torch.tensor(
            tensor,
            device=self.ddp_config.local_rank if torch.cuda.is_available() else "cpu",
        )

        # Reduce
        dist.all_reduce(tensor_tensor, op=dist.ReduceOp.SUM)

        return tensor_tensor.item() / self.ddp_config.world_size

    def cleanup(self):
        """Cleanup training resources."""
        self.metrics_tracker.close()
        DistributedInitializer.cleanup_distributed()

        if MLFLOW_AVAILABLE and self.ddp_config.rank == 0:
            mlflow.end_run()


# Example usage and utilities
def create_simple_model() -> nn.Module:
    """Create a simple neural network for testing."""
    if not PYTORCH_AVAILABLE:
        raise ImportError("PyTorch is required")

    class SimpleModel(nn.Module):
        def __init__(
            self, input_size: int = 784, hidden_size: int = 256, num_classes: int = 10
        ):
            super().__init__()
            self.fc1 = nn.Linear(input_size, hidden_size)
            self.fc2 = nn.Linear(hidden_size, hidden_size)
            self.fc3 = nn.Linear(hidden_size, num_classes)
            self.dropout = nn.Dropout(0.2)
            self.relu = nn.ReLU()

        def forward(self, x):
            x = x.view(x.size(0), -1)  # Flatten
            x = self.relu(self.fc1(x))
            x = self.dropout(x)
            x = self.relu(self.fc2(x))
            x = self.dropout(x)
            x = self.fc3(x)
            return x

    return SimpleModel()


def create_dummy_dataset(size: int = 1000):
    """Create dummy dataset for testing."""
    if not PYTORCH_AVAILABLE:
        raise ImportError("PyTorch is required")

    from torch.utils.data import TensorDataset

    # Create random data
    data = torch.randn(size, 784)
    labels = torch.randint(0, 10, (size,))

    return TensorDataset(data, labels)


if __name__ == "__main__":
    # Example usage
    ddp_config = DDPConfig(
        backend=DistributedBackend.NCCL, world_size=2, rank=0, local_rank=0
    )

    training_config = TrainingConfig(epochs=10, batch_size=64, learning_rate=0.001)

    checkpoint_config = CheckpointConfig(
        checkpoint_dir="./checkpoints", save_frequency=5
    )

    # Create model and datasets
    model = create_simple_model()
    train_dataset = create_dummy_dataset(1000)
    val_dataset = create_dummy_dataset(200)

    # Create trainer
    trainer = DistributedTrainer(
        model,
        train_dataset,
        val_dataset,
        ddp_config,
        training_config,
        checkpoint_config,
    )

    # Run training
    result = trainer.train()
    print("Training result:", result)
