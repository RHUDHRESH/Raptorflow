"""
S.W.A.R.M. Phase 2: Distributed Model Versioning
Production-ready distributed model versioning and registry for ML operations
"""

import asyncio
import hashlib
import json
import logging
import os
import pickle
import shutil
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

# ML imports
try:
    import torch
    import torch.nn as nn

    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False

try:
    import tensorflow as tf
    import tensorflow.keras as keras

    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

# Cloud storage imports
try:
    import boto3
    from botocore.exceptions import ClientError

    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

try:
    from google.cloud import storage

    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False

# MLflow imports
try:
    import mlflow
    import mlflow.pytorch
    import mlflow.tensorflow

    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False

logger = logging.getLogger("raptorflow.distributed_model_versioning")


class ModelFramework(Enum):
    """Supported ML frameworks."""

    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    SKLEARN = "sklearn"
    XGBOOST = "xgboost"
    HUGGINGFACE = "huggingface"
    CUSTOM = "custom"


class StorageBackend(Enum):
    """Storage backends."""

    LOCAL = "local"
    S3 = "s3"
    GCS = "gcs"
    AZURE_BLOB = "azure_blob"
    MLFLOW = "mlflow"


class ModelStatus(Enum):
    """Model version status."""

    DRAFT = "draft"
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"


@dataclass
class ModelMetadata:
    """Model metadata."""

    model_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    version: str = "1.0.0"
    framework: ModelFramework = ModelFramework.PYTORCH
    description: str = ""
    author: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    file_size_bytes: int = 0
    model_hash: str = ""
    tags: List[str] = field(default_factory=list)
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    dataset_info: Dict[str, Any] = field(default_factory=dict)
    training_info: Dict[str, Any] = field(default_factory=dict)
    dependencies: Dict[str, str] = field(default_factory=dict)
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    status: ModelStatus = ModelStatus.DRAFT

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "model_id": self.model_id,
            "name": self.name,
            "version": self.version,
            "framework": self.framework.value,
            "description": self.description,
            "author": self.author,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "file_size_bytes": self.file_size_bytes,
            "model_hash": self.model_hash,
            "tags": self.tags,
            "hyperparameters": self.hyperparameters,
            "metrics": self.metrics,
            "dataset_info": self.dataset_info,
            "training_info": self.training_info,
            "dependencies": self.dependencies,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "performance_metrics": self.performance_metrics,
            "status": self.status.value,
        }


@dataclass
class VersionConfig:
    """Version configuration."""

    version_strategy: str = "semantic"  # semantic, timestamp, hash
    auto_increment: bool = True
    max_versions: int = 100
    cleanup_policy: str = "keep_latest"  # keep_latest, keep_best, keep_all

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version_strategy": self.version_strategy,
            "auto_increment": self.auto_increment,
            "max_versions": self.max_versions,
            "cleanup_policy": self.cleanup_policy,
        }


class ModelStorage(ABC):
    """Abstract base class for model storage."""

    @abstractmethod
    async def save_model(
        self, model: Any, model_path: str, metadata: ModelMetadata
    ) -> str:
        """Save model to storage."""
        pass

    @abstractmethod
    async def load_model(self, model_path: str, framework: ModelFramework) -> Any:
        """Load model from storage."""
        pass

    @abstractmethod
    async def delete_model(self, model_path: str) -> bool:
        """Delete model from storage."""
        pass

    @abstractmethod
    async def list_models(self, prefix: str = "") -> List[str]:
        """List models in storage."""
        pass

    @abstractmethod
    async def model_exists(self, model_path: str) -> bool:
        """Check if model exists in storage."""
        pass


class LocalModelStorage(ModelStorage):
    """Local filesystem model storage."""

    def __init__(self, base_path: str = "./model_registry"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def save_model(
        self, model: Any, model_path: str, metadata: ModelMetadata
    ) -> str:
        """Save model to local storage."""
        try:
            full_path = self.base_path / model_path
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Save model based on framework
            if PYTORCH_AVAILABLE and metadata.framework == ModelFramework.PYTORCH:
                torch.save(model.state_dict(), full_path)
            elif (
                TENSORFLOW_AVAILABLE and metadata.framework == ModelFramework.TENSORFLOW
            ):
                model.save(full_path)
            else:
                # Fallback to pickle
                with open(full_path, "wb") as f:
                    pickle.dump(model, f)

            # Save metadata
            metadata_path = full_path.with_suffix(".json")
            with open(metadata_path, "w") as f:
                json.dump(metadata.to_dict(), f, indent=2)

            logger.info(f"Model saved to {full_path}")
            return str(full_path)

        except Exception as e:
            logger.error(f"Failed to save model: {str(e)}")
            raise

    async def load_model(self, model_path: str, framework: ModelFramework) -> Any:
        """Load model from local storage."""
        try:
            full_path = self.base_path / model_path

            if not full_path.exists():
                raise FileNotFoundError(f"Model not found: {model_path}")

            # Load model based on framework
            if PYTORCH_AVAILABLE and framework == ModelFramework.PYTORCH:
                # For PyTorch, we need the model architecture
                # This is a simplified version - in practice, you'd need to reconstruct the model
                state_dict = torch.load(full_path, map_location="cpu")
                return state_dict
            elif TENSORFLOW_AVAILABLE and framework == ModelFramework.TENSORFLOW:
                return tf.keras.models.load_model(full_path)
            else:
                # Fallback to pickle
                with open(full_path, "rb") as f:
                    return pickle.load(f)

        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise

    async def delete_model(self, model_path: str) -> bool:
        """Delete model from local storage."""
        try:
            full_path = self.base_path / model_path

            # Delete model file
            if full_path.exists():
                full_path.unlink()

            # Delete metadata file
            metadata_path = full_path.with_suffix(".json")
            if metadata_path.exists():
                metadata_path.unlink()

            logger.info(f"Model deleted: {model_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete model: {str(e)}")
            return False

    async def list_models(self, prefix: str = "") -> List[str]:
        """List models in local storage."""
        try:
            search_path = self.base_path / prefix if prefix else self.base_path
            models = []

            for file_path in search_path.rglob("*"):
                if file_path.is_file() and not file_path.name.endswith(".json"):
                    models.append(str(file_path.relative_to(self.base_path)))

            return models

        except Exception as e:
            logger.error(f"Failed to list models: {str(e)}")
            return []

    async def model_exists(self, model_path: str) -> bool:
        """Check if model exists in local storage."""
        full_path = self.base_path / model_path
        return full_path.exists()


class S3ModelStorage(ModelStorage):
    """S3-based model storage."""

    def __init__(self, bucket_name: str, prefix: str = "models/"):
        self.bucket_name = bucket_name
        self.prefix = prefix.rstrip("/") + "/"

        if not AWS_AVAILABLE:
            raise ImportError("boto3 is required for S3 storage")

        self.s3_client = boto3.client("s3")

    async def save_model(
        self, model: Any, model_path: str, metadata: ModelMetadata
    ) -> str:
        """Save model to S3."""
        try:
            # Save to temporary file first
            temp_dir = Path("./temp_models")
            temp_dir.mkdir(exist_ok=True)
            temp_path = temp_dir / f"temp_{uuid.uuid4()}.pkl"

            # Save model to temporary file
            with open(temp_path, "wb") as f:
                pickle.dump(model, f)

            # Upload to S3
            s3_key = self.prefix + model_path
            self.s3_client.upload_file(str(temp_path), self.bucket_name, s3_key)

            # Upload metadata
            metadata_key = s3_key + ".json"
            metadata_json = json.dumps(metadata.to_dict())
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=metadata_key,
                Body=metadata_json.encode("utf-8"),
            )

            # Cleanup temporary file
            temp_path.unlink()

            logger.info(f"Model saved to S3: {s3_key}")
            return f"s3://{self.bucket_name}/{s3_key}"

        except Exception as e:
            logger.error(f"Failed to save model to S3: {str(e)}")
            raise

    async def load_model(self, model_path: str, framework: ModelFramework) -> Any:
        """Load model from S3."""
        try:
            # Download to temporary file
            temp_dir = Path("./temp_models")
            temp_dir.mkdir(exist_ok=True)
            temp_path = temp_dir / f"temp_{uuid.uuid4()}.pkl"

            # Extract S3 key from path
            if model_path.startswith("s3://"):
                s3_key = model_path.replace(f"s3://{self.bucket_name}/", "")
            else:
                s3_key = self.prefix + model_path

            # Download from S3
            self.s3_client.download_file(self.bucket_name, s3_key, str(temp_path))

            # Load model
            with open(temp_path, "rb") as f:
                model = pickle.load(f)

            # Cleanup temporary file
            temp_path.unlink()

            return model

        except Exception as e:
            logger.error(f"Failed to load model from S3: {str(e)}")
            raise

    async def delete_model(self, model_path: str) -> bool:
        """Delete model from S3."""
        try:
            # Extract S3 key from path
            if model_path.startswith("s3://"):
                s3_key = model_path.replace(f"s3://{self.bucket_name}/", "")
            else:
                s3_key = self.prefix + model_path

            # Delete model file
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)

            # Delete metadata file
            metadata_key = s3_key + ".json"
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=metadata_key)

            logger.info(f"Model deleted from S3: {s3_key}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete model from S3: {str(e)}")
            return False

    async def list_models(self, prefix: str = "") -> List[str]:
        """List models in S3."""
        try:
            search_prefix = self.prefix + prefix if prefix else self.prefix
            models = []

            paginator = self.s3_client.get_paginator("list_objects_v2")
            for page in paginator.paginate(
                Bucket=self.bucket_name, Prefix=search_prefix
            ):
                if "Contents" in page:
                    for obj in page["Contents"]:
                        key = obj["Key"]
                        if not key.endswith(".json"):
                            # Remove prefix to get relative path
                            relative_key = key.replace(self.prefix, "")
                            models.append(relative_key)

            return models

        except Exception as e:
            logger.error(f"Failed to list models in S3: {str(e)}")
            return []

    async def model_exists(self, model_path: str) -> bool:
        """Check if model exists in S3."""
        try:
            # Extract S3 key from path
            if model_path.startswith("s3://"):
                s3_key = model_path.replace(f"s3://{self.bucket_name}/", "")
            else:
                s3_key = self.prefix + model_path

            self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True

        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise


class MLflowModelStorage(ModelStorage):
    """MLflow-based model storage."""

    def __init__(self, tracking_uri: str = None):
        if not MLFLOW_AVAILABLE:
            raise ImportError("MLflow is required for MLflow storage")

        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)

        self.tracking_uri = tracking_uri

    async def save_model(
        self, model: Any, model_path: str, metadata: ModelMetadata
    ) -> str:
        """Save model to MLflow."""
        try:
            with mlflow.start_run(
                run_name=f"{metadata.name}_v{metadata.version}"
            ) as run:
                # Log model based on framework
                if metadata.framework == ModelFramework.PYTORCH:
                    mlflow.pytorch.log_model(model, "model")
                elif metadata.framework == ModelFramework.TENSORFLOW:
                    mlflow.tensorflow.log_model(model, "model")
                else:
                    # Log as artifact for custom frameworks
                    temp_path = f"./temp_{uuid.uuid4()}.pkl"
                    with open(temp_path, "wb") as f:
                        pickle.dump(model, f)
                    mlflow.log_artifact(temp_path, "model")
                    os.remove(temp_path)

                # Log parameters and metrics
                mlflow.log_params(metadata.hyperparameters)
                mlflow.log_metrics(metadata.metrics)

                # Log metadata as tags
                for key, value in metadata.to_dict().items():
                    if isinstance(value, (str, int, float, bool)):
                        mlflow.set_tag(key, value)

                model_uri = f"runs:/{run.info.run_id}/model"
                logger.info(f"Model saved to MLflow: {model_uri}")
                return model_uri

        except Exception as e:
            logger.error(f"Failed to save model to MLflow: {str(e)}")
            raise

    async def load_model(self, model_path: str, framework: ModelFramework) -> Any:
        """Load model from MLflow."""
        try:
            if framework == ModelFramework.PYTORCH:
                model = mlflow.pytorch.load_model(model_path)
            elif framework == ModelFramework.TENSORFLOW:
                model = mlflow.tensorflow.load_model(model_path)
            else:
                # Load as artifact for custom frameworks
                local_path = mlflow.artifacts.download_artifacts(model_path)
                with open(local_path, "rb") as f:
                    model = pickle.load(f)

            return model

        except Exception as e:
            logger.error(f"Failed to load model from MLflow: {str(e)}")
            raise

    async def delete_model(self, model_path: str) -> bool:
        """Delete model from MLflow."""
        try:
            # MLflow doesn't directly support deletion of models
            # This would require custom implementation
            logger.warning("Model deletion not supported in MLflow storage")
            return False

        except Exception as e:
            logger.error(f"Failed to delete model from MLflow: {str(e)}")
            return False

    async def list_models(self, prefix: str = "") -> List[str]:
        """List models in MLflow."""
        try:
            # This would require querying MLflow tracking server
            # Simplified implementation
            logger.warning("Model listing not fully implemented in MLflow storage")
            return []

        except Exception as e:
            logger.error(f"Failed to list models in MLflow: {str(e)}")
            return []

    async def model_exists(self, model_path: str) -> bool:
        """Check if model exists in MLflow."""
        try:
            # This would require checking MLflow tracking server
            # Simplified implementation
            return True

        except Exception as e:
            logger.error(f"Failed to check model existence in MLflow: {str(e)}")
            return False


class DistributedModelRegistry:
    """Distributed model registry for versioning and management."""

    def __init__(
        self, storage_backend: StorageBackend = StorageBackend.LOCAL, **storage_config
    ):
        self.storage_backend = storage_backend
        self.storage = self._create_storage(storage_backend, **storage_config)
        self.models: Dict[str, ModelMetadata] = {}
        self.model_versions: Dict[str, List[str]] = (
            {}
        )  # model_name -> list of model_ids
        self.version_config = VersionConfig()
        self.registry_history: List[Dict[str, Any]] = []

    def _create_storage(self, backend: StorageBackend, **config) -> ModelStorage:
        """Create storage backend."""
        if backend == StorageBackend.LOCAL:
            return LocalModelStorage(config.get("base_path", "./model_registry"))
        elif backend == StorageBackend.S3:
            return S3ModelStorage(
                config.get("bucket_name"), config.get("prefix", "models/")
            )
        elif backend == StorageBackend.MLFLOW:
            return MLflowModelStorage(config.get("tracking_uri"))
        else:
            raise ValueError(f"Unsupported storage backend: {backend}")

    async def register_model(
        self,
        model: Any,
        name: str,
        framework: ModelFramework,
        version: Optional[str] = None,
        **metadata_kwargs,
    ) -> str:
        """Register a new model version."""
        try:
            # Generate version if not provided
            if version is None:
                version = self._generate_version(name)

            # Calculate model hash
            model_hash = self._calculate_model_hash(model)

            # Create metadata
            metadata = ModelMetadata(
                name=name,
                version=version,
                framework=framework,
                model_hash=model_hash,
                **metadata_kwargs,
            )

            # Check for duplicates
            if await self._model_exists(metadata):
                raise ValueError(f"Model {name}:{version} already exists")

            # Save model
            model_path = f"{name}/{version}/model"
            storage_path = await self.storage.save_model(model, model_path, metadata)

            # Update registry
            self.models[metadata.model_id] = metadata

            if name not in self.model_versions:
                self.model_versions[name] = []
            self.model_versions[name].append(metadata.model_id)

            # Cleanup old versions if needed
            await self._cleanup_old_versions(name)

            # Record registration
            self.registry_history.append(
                {
                    "action": "register",
                    "model_id": metadata.model_id,
                    "name": name,
                    "version": version,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            logger.info(f"Model registered: {name}:{version}")
            return metadata.model_id

        except Exception as e:
            logger.error(f"Failed to register model: {str(e)}")
            raise

    async def load_model(self, model_id: str) -> Tuple[Any, ModelMetadata]:
        """Load a model by ID."""
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found")

        metadata = self.models[model_id]
        model_path = f"{metadata.name}/{metadata.version}/model"

        model = await self.storage.load_model(model_path, metadata.framework)

        return model, metadata

    async def load_latest_model(self, name: str) -> Tuple[Any, ModelMetadata]:
        """Load the latest version of a model."""
        if name not in self.model_versions:
            raise ValueError(f"No models found for {name}")

        # Get latest model ID
        latest_model_id = self.model_versions[name][-1]
        return await self.load_model(latest_model_id)

    async def load_model_by_version(
        self, name: str, version: str
    ) -> Tuple[Any, ModelMetadata]:
        """Load a model by name and version."""
        for model_id in self.model_versions.get(name, []):
            metadata = self.models[model_id]
            if metadata.version == version:
                return await self.load_model(model_id)

        raise ValueError(f"Model {name}:{version} not found")

    async def list_models(self, name: Optional[str] = None) -> List[ModelMetadata]:
        """List all models or models by name."""
        if name:
            if name not in self.model_versions:
                return []
            model_ids = self.model_versions[name]
            return [self.models[model_id] for model_id in model_ids]
        else:
            return list(self.models.values())

    async def delete_model(self, model_id: str) -> bool:
        """Delete a model version."""
        if model_id not in self.models:
            return False

        metadata = self.models[model_id]
        model_path = f"{metadata.name}/{metadata.version}/model"

        # Delete from storage
        storage_deleted = await self.storage.delete_model(model_path)

        # Update registry
        del self.models[model_id]
        self.model_versions[metadata.name].remove(model_id)

        # Record deletion
        self.registry_history.append(
            {
                "action": "delete",
                "model_id": model_id,
                "name": metadata.name,
                "version": metadata.version,
                "timestamp": datetime.now().isoformat(),
            }
        )

        logger.info(f"Model deleted: {metadata.name}:{metadata.version}")
        return storage_deleted

    async def update_model_status(self, model_id: str, status: ModelStatus) -> bool:
        """Update model status."""
        if model_id not in self.models:
            return False

        self.models[model_id].status = status
        self.models[model_id].updated_at = datetime.now()

        # Record status change
        self.registry_history.append(
            {
                "action": "status_update",
                "model_id": model_id,
                "status": status.value,
                "timestamp": datetime.now().isoformat(),
            }
        )

        return True

    async def promote_model(self, model_id: str, target_status: ModelStatus) -> bool:
        """Promote model to target status."""
        return await self.update_model_status(model_id, target_status)

    async def compare_models(self, model_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple models."""
        comparison = {"models": {}, "comparison_timestamp": datetime.now().isoformat()}

        for model_id in model_ids:
            if model_id in self.models:
                metadata = self.models[model_id]
                comparison["models"][model_id] = {
                    "name": metadata.name,
                    "version": metadata.version,
                    "framework": metadata.framework.value,
                    "metrics": metadata.metrics,
                    "performance_metrics": metadata.performance_metrics,
                    "status": metadata.status.value,
                    "created_at": metadata.created_at.isoformat(),
                }

        return comparison

    def _generate_version(self, name: str) -> str:
        """Generate a new version number."""
        if self.version_config.version_strategy == "semantic":
            # Semantic versioning (simplified)
            existing_versions = self.model_versions.get(name, [])
            if not existing_versions:
                return "1.0.0"

            # Get latest version and increment patch
            latest_metadata = self.models[existing_versions[-1]]
            latest_version = latest_metadata.version

            try:
                parts = latest_version.split(".")
                patch = int(parts[2]) + 1
                return f"{parts[0]}.{parts[1]}.{patch}"
            except:
                return "1.0.0"

        elif self.version_config.version_strategy == "timestamp":
            return datetime.now().strftime("%Y%m%d_%H%M%S")

        else:  # hash
            return hashlib.md5(str(time.time()).encode()).hexdigest()[:8]

    def _calculate_model_hash(self, model: Any) -> str:
        """Calculate model hash."""
        try:
            # Serialize model to bytes
            model_bytes = pickle.dumps(model)
            return hashlib.sha256(model_bytes).hexdigest()
        except Exception:
            # Fallback to simple hash
            return hashlib.md5(str(id(model)).encode()).hexdigest()

    async def _model_exists(self, metadata: ModelMetadata) -> bool:
        """Check if model already exists."""
        for model_id in self.model_versions.get(metadata.name, []):
            existing_metadata = self.models[model_id]
            if existing_metadata.version == metadata.version:
                return True
        return False

    async def _cleanup_old_versions(self, name: str):
        """Cleanup old model versions based on policy."""
        if self.version_config.cleanup_policy == "keep_all":
            return

        model_ids = self.model_versions.get(name, [])
        if len(model_ids) <= self.version_config.max_versions:
            return

        if self.version_config.cleanup_policy == "keep_latest":
            # Keep only the latest versions
            models_to_delete = model_ids[: -self.version_config.max_versions]
        else:
            # For other policies, implement as needed
            return

        for model_id in models_to_delete:
            await self.delete_model(model_id)

    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        total_models = len(self.models)
        models_by_framework = {}
        models_by_status = {}

        for metadata in self.models.values():
            # Count by framework
            framework = metadata.framework.value
            models_by_framework[framework] = models_by_framework.get(framework, 0) + 1

            # Count by status
            status = metadata.status.value
            models_by_status[status] = models_by_status.get(status, 0) + 1

        return {
            "total_models": total_models,
            "total_model_names": len(self.model_versions),
            "models_by_framework": models_by_framework,
            "models_by_status": models_by_status,
            "storage_backend": self.storage_backend.value,
            "version_config": self.version_config.to_dict(),
        }


# Example usage
async def example_usage():
    """Example usage of distributed model registry."""
    # Create registry with local storage
    registry = DistributedModelRegistry(StorageBackend.LOCAL)

    # Create a simple model
    if PYTORCH_AVAILABLE:
        model = nn.Linear(10, 1)

        # Register model
        model_id = await registry.register_model(
            model=model,
            name="simple_linear",
            framework=ModelFramework.PYTORCH,
            description="Simple linear regression model",
            author="ML Engineer",
            hyperparameters={"input_size": 10, "output_size": 1},
            metrics={"train_loss": 0.5, "val_loss": 0.6},
        )

        print(f"Model registered with ID: {model_id}")

        # Load model
        loaded_model, metadata = await registry.load_model(model_id)
        print(f"Loaded model: {metadata.name}:{metadata.version}")

        # Get registry stats
        stats = registry.get_registry_stats()
        print(f"Registry stats: {stats}")


if __name__ == "__main__":
    asyncio.run(example_usage())
