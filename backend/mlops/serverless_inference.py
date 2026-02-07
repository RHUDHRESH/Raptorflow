"""
S.W.A.R.M. Phase 2: Serverless Model Serving Implementation
Production-ready serverless model serving endpoints and inference pipelines
"""

import asyncio
import base64
import json
import logging
import os
import pickle
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

# ML imports
import numpy as np
import uvicorn
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

# Cloud provider imports (conditional)
try:
    import boto3
    from botocore.exceptions import ClientError

    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

try:
    from google.cloud import functions_v2, pubsub_v1, storage
    from google.cloud.run_v2 import ServicesClient

    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False

logger = logging.getLogger("raptorflow.serverless")


class CloudProvider(Enum):
    """Cloud provider options."""

    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"


class ModelFormat(Enum):
    """Supported model formats."""

    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    ONNX = "onnx"
    HUGGINGFACE = "huggingface"
    SKLEARN = "sklearn"
    XGBOOST = "xgboost"


class InferenceType(Enum):
    """Inference types."""

    SINGLE = "single"
    BATCH = "batch"
    STREAMING = "streaming"


@dataclass
class ModelMetadata:
    """Model metadata."""

    model_id: str
    name: str
    version: str
    format: ModelFormat
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    model_size_mb: float = 0.0
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "model_id": self.model_id,
            "name": self.name,
            "version": self.version,
            "format": self.format.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "model_size_mb": self.model_size_mb,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "performance_metrics": self.performance_metrics,
            "tags": self.tags,
        }


@dataclass
class InferenceRequest:
    """Inference request data."""

    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    model_id: str = ""
    inference_type: InferenceType = InferenceType.SINGLE
    input_data: Dict[str, Any] = field(default_factory=dict)
    batch_data: List[Dict[str, Any]] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "request_id": self.request_id,
            "model_id": self.model_id,
            "inference_type": self.inference_type.value,
            "input_data": self.input_data,
            "batch_data": self.batch_data,
            "parameters": self.parameters,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class InferenceResponse:
    """Inference response data."""

    request_id: str = ""
    model_id: str = ""
    inference_type: InferenceType = InferenceType.SINGLE
    predictions: Union[Dict[str, Any], List[Dict[str, Any]]] = field(
        default_factory=dict
    )
    confidence_scores: Optional[List[float]] = None
    processing_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "request_id": self.request_id,
            "model_id": self.model_id,
            "inference_type": self.inference_type.value,
            "predictions": self.predictions,
            "confidence_scores": self.confidence_scores,
            "processing_time_ms": self.processing_time_ms,
            "timestamp": self.timestamp.isoformat(),
            "error": self.error,
            "metadata": self.metadata,
        }


class ModelLoader:
    """Model loading and caching system."""

    def __init__(self, cache_size: int = 10):
        self.cache_size = cache_size
        self.model_cache: Dict[str, Any] = {}
        self.model_metadata: Dict[str, ModelMetadata] = {}
        self.loading_stats: Dict[str, Dict[str, Any]] = {}

    async def load_model(self, model_path: str, model_format: ModelFormat) -> Any:
        """Load model from storage."""
        cache_key = f"{model_path}:{model_format.value}"

        # Check cache first
        if cache_key in self.model_cache:
            logger.info(f"Model loaded from cache: {cache_key}")
            return self.model_cache[cache_key]

        # Load model based on format
        start_time = datetime.now()

        try:
            if model_format == ModelFormat.PYTORCH:
                model = await self._load_pytorch_model(model_path)
            elif model_format == ModelFormat.TENSORFLOW:
                model = await self._load_tensorflow_model(model_path)
            elif model_format == ModelFormat.ONNX:
                model = await self._load_onnx_model(model_path)
            elif model_format == ModelFormat.HUGGINGFACE:
                model = await self._load_huggingface_model(model_path)
            elif model_format == ModelFormat.SKLEARN:
                model = await self._load_sklearn_model(model_path)
            elif model_format == ModelFormat.XGBOOST:
                model = await self._load_xgboost_model(model_path)
            else:
                raise ValueError(f"Unsupported model format: {model_format}")

            loading_time = (datetime.now() - start_time).total_seconds()

            # Update cache
            if len(self.model_cache) >= self.cache_size:
                # Remove oldest entry
                oldest_key = next(iter(self.model_cache))
                del self.model_cache[oldest_key]

            self.model_cache[cache_key] = model

            # Update stats
            self.loading_stats[cache_key] = {
                "load_time": loading_time,
                "last_loaded": datetime.now(),
                "cache_hits": 0,
            }

            logger.info(
                f"Model loaded successfully: {cache_key} in {loading_time:.2f}s"
            )
            return model

        except Exception as e:
            logger.error(f"Failed to load model {cache_key}: {str(e)}")
            raise

    async def _load_pytorch_model(self, model_path: str) -> Any:
        """Load PyTorch model."""
        import torch

        if model_path.startswith("s3://"):
            model_data = await self._download_from_s3(model_path)
            model = torch.load(model_data)
        else:
            model = torch.load(model_path)
        return model

    async def _load_tensorflow_model(self, model_path: str) -> Any:
        """Load TensorFlow model."""
        import tensorflow as tf

        if model_path.startswith("s3://"):
            model_path = await self._download_from_s3(model_path)
        model = tf.keras.models.load_model(model_path)
        return model

    async def _load_onnx_model(self, model_path: str) -> Any:
        """Load ONNX model."""
        import onnxruntime as ort

        if model_path.startswith("s3://"):
            model_path = await self._download_from_s3(model_path)
        session = ort.InferenceSession(model_path)
        return session

    async def _load_huggingface_model(self, model_path: str) -> Any:
        """Load HuggingFace model."""
        from transformers import AutoModel, AutoTokenizer

        if model_path.startswith("s3://"):
            model_path = await self._download_from_s3(model_path)
        model = AutoModel.from_pretrained(model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        return {"model": model, "tokenizer": tokenizer}

    async def _load_sklearn_model(self, model_path: str) -> Any:
        """Load scikit-learn model."""
        import joblib

        if model_path.startswith("s3://"):
            model_path = await self._download_from_s3(model_path)
        model = joblib.load(model_path)
        return model

    async def _load_xgboost_model(self, model_path: str) -> Any:
        """Load XGBoost model."""
        import xgboost as xgb

        if model_path.startswith("s3://"):
            model_path = await self._download_from_s3(model_path)
        model = xgb.Booster()
        model.load_model(model_path)
        return model

    async def _download_from_s3(self, s3_path: str) -> str:
        """Download model from S3."""
        if not AWS_AVAILABLE:
            raise ImportError("boto3 is required for S3 operations")

        s3_client = boto3.client("s3")
        bucket_name = s3_path.split("/")[2]
        object_key = "/".join(s3_path.split("/")[3:])

        local_path = f"/tmp/{uuid.uuid4()}.model"
        s3_client.download_file(bucket_name, object_key, local_path)
        return local_path

    def get_model_stats(self) -> Dict[str, Any]:
        """Get model loading statistics."""
        return {
            "cached_models": len(self.model_cache),
            "cache_size": self.cache_size,
            "loading_stats": self.loading_stats,
        }


class InferenceEngine:
    """Core inference engine."""

    def __init__(self, model_loader: ModelLoader):
        self.model_loader = model_loader
        self.inference_stats: Dict[str, Any] = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_processing_time": 0.0,
        }

    async def predict(
        self,
        model_path: str,
        model_format: ModelFormat,
        input_data: Dict[str, Any],
        parameters: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Run single prediction."""
        start_time = datetime.now()

        try:
            # Load model
            model = await self.model_loader.load_model(model_path, model_format)

            # Run inference based on model format
            if model_format == ModelFormat.PYTORCH:
                predictions = await self._predict_pytorch(model, input_data, parameters)
            elif model_format == ModelFormat.TENSORFLOW:
                predictions = await self._predict_tensorflow(
                    model, input_data, parameters
                )
            elif model_format == ModelFormat.ONNX:
                predictions = await self._predict_onnx(model, input_data, parameters)
            elif model_format == ModelFormat.HUGGINGFACE:
                predictions = await self._predict_huggingface(
                    model, input_data, parameters
                )
            elif model_format == ModelFormat.SKLEARN:
                predictions = await self._predict_sklearn(model, input_data, parameters)
            elif model_format == ModelFormat.XGBOOST:
                predictions = await self._predict_xgboost(model, input_data, parameters)
            else:
                raise ValueError(f"Unsupported model format: {model_format}")

            processing_time = (datetime.now() - start_time).total_seconds() * 1000

            # Update stats
            self.inference_stats["total_requests"] += 1
            self.inference_stats["successful_requests"] += 1
            self._update_average_processing_time(processing_time)

            return {
                "predictions": predictions,
                "processing_time_ms": processing_time,
                "confidence_scores": self._extract_confidence_scores(predictions),
            }

        except Exception as e:
            self.inference_stats["total_requests"] += 1
            self.inference_stats["failed_requests"] += 1
            logger.error(f"Inference failed: {str(e)}")
            raise

    async def predict_batch(
        self,
        model_path: str,
        model_format: ModelFormat,
        batch_data: List[Dict[str, Any]],
        parameters: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        """Run batch prediction."""
        results = []

        for input_data in batch_data:
            try:
                result = await self.predict(
                    model_path, model_format, input_data, parameters
                )
                results.append(result)
            except Exception as e:
                results.append({"error": str(e), "processing_time_ms": 0.0})

        return results

    async def _predict_pytorch(
        self, model: Any, input_data: Dict[str, Any], parameters: Dict[str, Any]
    ) -> Any:
        """PyTorch prediction."""
        import torch

        model.eval()
        with torch.no_grad():
            # Convert input to tensor
            input_tensor = torch.tensor(input_data["features"])
            if len(input_tensor.shape) == 1:
                input_tensor = input_tensor.unsqueeze(0)

            # Run prediction
            output = model(input_tensor)

            # Convert to numpy/json serializable
            if isinstance(output, torch.Tensor):
                return output.numpy().tolist()
            return output

    async def _predict_tensorflow(
        self, model: Any, input_data: Dict[str, Any], parameters: Dict[str, Any]
    ) -> Any:
        """TensorFlow prediction."""
        import tensorflow as tf

        input_tensor = tf.constant(input_data["features"])
        if len(input_tensor.shape) == 1:
            input_tensor = tf.expand_dims(input_tensor, 0)

        output = model(input_tensor)
        return output.numpy().tolist()

    async def _predict_onnx(
        self, session: Any, input_data: Dict[str, Any], parameters: Dict[str, Any]
    ) -> Any:
        """ONNX prediction."""
        input_name = session.get_inputs()[0].name
        input_array = np.array(input_data["features"])
        if len(input_array.shape) == 1:
            input_array = np.expand_dims(input_array, 0)

        output = session.run(None, {input_name: input_array})
        return output[0].tolist()

    async def _predict_huggingface(
        self,
        model_dict: Dict[str, Any],
        input_data: Dict[str, Any],
        parameters: Dict[str, Any],
    ) -> Any:
        """HuggingFace prediction."""
        model = model_dict["model"]
        tokenizer = model_dict["tokenizer"]

        # Tokenize input
        text = input_data.get("text", "")
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)

        # Run prediction
        with torch.no_grad():
            outputs = model(**inputs)

        # Extract relevant outputs
        if hasattr(outputs, "last_hidden_state"):
            return outputs.last_hidden_state.numpy().tolist()
        elif hasattr(outputs, "logits"):
            return outputs.logits.numpy().tolist()
        else:
            return outputs.numpy().tolist()

    async def _predict_sklearn(
        self, model: Any, input_data: Dict[str, Any], parameters: Dict[str, Any]
    ) -> Any:
        """Scikit-learn prediction."""
        features = np.array(input_data["features"])
        if len(features.shape) == 1:
            features = features.reshape(1, -1)

        prediction = model.predict(features)
        return prediction.tolist()

    async def _predict_xgboost(
        self, model: Any, input_data: Dict[str, Any], parameters: Dict[str, Any]
    ) -> Any:
        """XGBoost prediction."""
        import xgboost as xgb

        features = np.array(input_data["features"])
        if len(features.shape) == 1:
            features = features.reshape(1, -1)

        dmatrix = xgb.DMatrix(features)
        prediction = model.predict(dmatrix)
        return prediction.tolist()

    def _extract_confidence_scores(self, predictions: Any) -> Optional[List[float]]:
        """Extract confidence scores from predictions."""
        # This is a simplified implementation
        # In practice, this would depend on the model type and output format
        try:
            if isinstance(predictions, list) and isinstance(predictions[0], list):
                # For classification probabilities
                return [max(pred) for pred in predictions]
            elif isinstance(predictions, list):
                return [max(predictions)]
            else:
                return None
        except:
            return None

    def _update_average_processing_time(self, processing_time: float):
        """Update average processing time."""
        current_avg = self.inference_stats["average_processing_time"]
        total_requests = self.inference_stats["successful_requests"]

        if total_requests == 1:
            self.inference_stats["average_processing_time"] = processing_time
        else:
            self.inference_stats["average_processing_time"] = (
                current_avg * (total_requests - 1) + processing_time
            ) / total_requests

    def get_inference_stats(self) -> Dict[str, Any]:
        """Get inference statistics."""
        return self.inference_stats.copy()


class ServerlessModelServer:
    """Serverless model serving system."""

    def __init__(self, cloud_provider: CloudProvider = CloudProvider.AWS):
        self.cloud_provider = cloud_provider
        self.model_loader = ModelLoader()
        self.inference_engine = InferenceEngine(self.model_loader)
        self.app = FastAPI(title="RaptorFlow Serverless ML", version="1.0.0")
        self.setup_middleware()
        self.setup_routes()

    def setup_middleware(self):
        """Setup FastAPI middleware."""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def setup_routes(self):
        """Setup API routes."""

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
            }

        @self.app.get("/stats")
        async def get_stats():
            """Get server statistics."""
            return {
                "model_stats": self.model_loader.get_model_stats(),
                "inference_stats": self.inference_engine.get_inference_stats(),
                "timestamp": datetime.now().isoformat(),
            }

        @self.app.post("/predict")
        async def predict(request: InferenceRequest):
            """Single prediction endpoint."""
            try:
                # Get model metadata (simplified)
                model_path = f"s3://models/{request.model_id}/model.pkl"
                model_format = ModelFormat.PYTORCH  # Default

                # Run inference
                result = await self.inference_engine.predict(
                    model_path=model_path,
                    model_format=model_format,
                    input_data=request.input_data,
                    parameters=request.parameters,
                )

                # Create response
                response = InferenceResponse(
                    request_id=request.request_id,
                    model_id=request.model_id,
                    inference_type=request.inference_type,
                    predictions=result["predictions"],
                    confidence_scores=result["confidence_scores"],
                    processing_time_ms=result["processing_time_ms"],
                    metadata={"model_format": model_format.value},
                )

                return response

            except Exception as e:
                logger.error(f"Prediction failed: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/predict/batch")
        async def predict_batch(request: InferenceRequest):
            """Batch prediction endpoint."""
            try:
                # Get model metadata
                model_path = f"s3://models/{request.model_id}/model.pkl"
                model_format = ModelFormat.PYTORCH  # Default

                # Run batch inference
                results = await self.inference_engine.predict_batch(
                    model_path=model_path,
                    model_format=model_format,
                    batch_data=request.batch_data,
                    parameters=request.parameters,
                )

                # Create response
                response = InferenceResponse(
                    request_id=request.request_id,
                    model_id=request.model_id,
                    inference_type=InferenceType.BATCH,
                    predictions=results,
                    processing_time_ms=sum(
                        r.get("processing_time_ms", 0) for r in results
                    ),
                    metadata={"batch_size": len(request.batch_data)},
                )

                return response

            except Exception as e:
                logger.error(f"Batch prediction failed: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """Run the server."""
        uvicorn.run(self.app, host=host, port=port)


class ServerlessInferencePipeline:
    """Serverless inference pipeline orchestrator."""

    def __init__(self, cloud_provider: CloudProvider = CloudProvider.AWS):
        self.cloud_provider = cloud_provider
        self.pipeline_steps: List[Dict[str, Any]] = []
        self.pipeline_stats: Dict[str, Any] = {
            "total_pipelines": 0,
            "successful_pipelines": 0,
            "failed_pipelines": 0,
            "average_pipeline_time": 0.0,
        }

    def add_preprocessing_step(self, step_name: str, function: Callable, **config):
        """Add preprocessing step to pipeline."""
        step = {
            "name": step_name,
            "type": "preprocessing",
            "function": function,
            "config": config,
        }
        self.pipeline_steps.append(step)

    def add_inference_step(
        self, step_name: str, model_path: str, model_format: ModelFormat, **config
    ):
        """Add inference step to pipeline."""
        step = {
            "name": step_name,
            "type": "inference",
            "model_path": model_path,
            "model_format": model_format,
            "config": config,
        }
        self.pipeline_steps.append(step)

    def add_postprocessing_step(self, step_name: str, function: Callable, **config):
        """Add postprocessing step to pipeline."""
        step = {
            "name": step_name,
            "type": "postprocessing",
            "function": function,
            "config": config,
        }
        self.pipeline_steps.append(step)

    async def execute_pipeline(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the inference pipeline."""
        start_time = datetime.now()
        pipeline_result = {"input_data": input_data}

        try:
            for step in self.pipeline_steps:
                step_start = datetime.now()

                if step["type"] == "preprocessing":
                    result = await step["function"](pipeline_result, **step["config"])
                elif step["type"] == "inference":
                    # Create inference engine for this step
                    model_loader = ModelLoader()
                    inference_engine = InferenceEngine(model_loader)

                    result = await inference_engine.predict(
                        model_path=step["model_path"],
                        model_format=step["model_format"],
                        input_data=pipeline_result,
                        parameters=step["config"],
                    )
                elif step["type"] == "postprocessing":
                    result = await step["function"](pipeline_result, **step["config"])
                else:
                    raise ValueError(f"Unknown step type: {step['type']}")

                step_time = (datetime.now() - step_start).total_seconds()

                pipeline_result[f"{step['name']}_result"] = result
                pipeline_result[f"{step['name']}_time"] = step_time

            total_time = (datetime.now() - start_time).total_seconds()

            # Update stats
            self.pipeline_stats["total_pipelines"] += 1
            self.pipeline_stats["successful_pipelines"] += 1
            self._update_average_pipeline_time(total_time)

            pipeline_result["total_pipeline_time"] = total_time
            pipeline_result["pipeline_success"] = True

            return pipeline_result

        except Exception as e:
            self.pipeline_stats["total_pipelines"] += 1
            self.pipeline_stats["failed_pipelines"] += 1

            pipeline_result["pipeline_success"] = False
            pipeline_result["pipeline_error"] = str(e)
            pipeline_result["total_pipeline_time"] = (
                datetime.now() - start_time
            ).total_seconds()

            logger.error(f"Pipeline execution failed: {str(e)}")
            raise

    def _update_average_pipeline_time(self, pipeline_time: float):
        """Update average pipeline execution time."""
        current_avg = self.pipeline_stats["average_pipeline_time"]
        total_pipelines = self.pipeline_stats["successful_pipelines"]

        if total_pipelines == 1:
            self.pipeline_stats["average_pipeline_time"] = pipeline_time
        else:
            self.pipeline_stats["average_pipeline_time"] = (
                current_avg * (total_pipelines - 1) + pipeline_time
            ) / total_pipelines

    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics."""
        return self.pipeline_stats.copy()


# Example preprocessing and postprocessing functions
async def normalize_input(data: Dict[str, Any], **config) -> Dict[str, Any]:
    """Normalize input data."""
    features = np.array(data.get("features", []))
    if len(features) > 0:
        features = (features - np.mean(features)) / np.std(features)
    return {"features": features.tolist()}


async def format_output(data: Dict[str, Any], **config) -> Dict[str, Any]:
    """Format output data."""
    predictions = data.get("predictions", [])
    formatted = {
        "results": predictions,
        "count": len(predictions) if isinstance(predictions, list) else 1,
        "timestamp": datetime.now().isoformat(),
    }
    return formatted


if __name__ == "__main__":
    # Example usage
    server = ServerlessModelServer()

    # Create inference pipeline
    pipeline = ServerlessInferencePipeline()
    pipeline.add_preprocessing_step("normalize", normalize_input)
    pipeline.add_inference_step(
        "predict", "s3://models/test/model.pkl", ModelFormat.PYTORCH
    )
    pipeline.add_postprocessing_step("format", format_output)

    print("Serverless ML Server ready!")
