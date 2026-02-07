"""
S.W.A.R.M. Phase 2: Serverless Data Processing Functions
Production-ready serverless data processing for ML operations
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
from io import BytesIO
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Union

# Data processing imports
import numpy as np
import pandas as pd
import redis
from fastapi import BackgroundTasks, FastAPI, HTTPException
from pydantic import BaseModel, Field

# Cloud provider imports
try:
    import boto3
    from botocore.exceptions import ClientError

    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

try:
    from google.cloud import bigquery, pubsub_v1, storage
    from google.cloud.dataflow import PipelineOptions

    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False

logger = logging.getLogger("raptorflow.data_processing")


class DataFormat(Enum):
    """Supported data formats."""

    CSV = "csv"
    JSON = "json"
    PARQUET = "parquet"
    AVRO = "avro"
    XML = "xml"
    EXCEL = "excel"


class ProcessingType(Enum):
    """Data processing types."""

    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    ENRICHMENT = "enrichment"
    AGGREGATION = "aggregation"
    CLEANING = "cleaning"
    NORMALIZATION = "normalization"


class StorageType(Enum):
    """Storage types."""

    S3 = "s3"
    GCS = "gcs"
    AZURE_BLOB = "azure_blob"
    LOCAL = "local"


@dataclass
class DataProcessingConfig:
    """Data processing configuration."""

    processing_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    processing_type: ProcessingType = ProcessingType.TRANSFORMATION
    input_format: DataFormat = DataFormat.JSON
    output_format: DataFormat = DataFormat.JSON
    input_source: str = ""
    output_destination: str = ""
    batch_size: int = 1000
    max_workers: int = 4
    error_handling: str = "skip"  # skip, fail, retry
    retry_attempts: int = 3
    timeout_seconds: int = 300
    memory_limit_mb: int = 1024
    custom_parameters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "processing_id": self.processing_id,
            "processing_type": self.processing_type.value,
            "input_format": self.input_format.value,
            "output_format": self.output_format.value,
            "input_source": self.input_source,
            "output_destination": self.output_destination,
            "batch_size": self.batch_size,
            "max_workers": self.max_workers,
            "error_handling": self.error_handling,
            "retry_attempts": self.retry_attempts,
            "timeout_seconds": self.timeout_seconds,
            "memory_limit_mb": self.memory_limit_mb,
            "custom_parameters": self.custom_parameters,
        }


@dataclass
class ProcessingResult:
    """Data processing result."""

    processing_id: str = ""
    success: bool = False
    records_processed: int = 0
    records_failed: int = 0
    processing_time_seconds: float = 0.0
    error_message: Optional[str] = None
    output_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "processing_id": self.processing_id,
            "success": self.success,
            "records_processed": self.records_processed,
            "records_failed": self.records_failed,
            "processing_time_seconds": self.processing_time_seconds,
            "error_message": self.error_message,
            "output_path": self.output_path,
            "metadata": self.metadata,
        }


class DataValidator:
    """Data validation and quality checking."""

    def __init__(self):
        self.validation_rules: Dict[str, Callable] = {}
        self.quality_metrics: Dict[str, Any] = {}

    def add_validation_rule(self, field_name: str, rule: Callable):
        """Add a validation rule for a field."""
        self.validation_rules[field_name] = rule

    async def validate_data(
        self, data: Union[Dict, List[Dict], pd.DataFrame]
    ) -> Dict[str, Any]:
        """Validate data against rules."""
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "quality_metrics": {},
        }

        # Convert to DataFrame if needed
        if isinstance(data, dict):
            df = pd.DataFrame([data])
        elif isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = data

        # Apply validation rules
        for field_name, rule in self.validation_rules.items():
            if field_name in df.columns:
                try:
                    is_valid = rule(df[field_name])
                    if not is_valid:
                        validation_results["errors"].append(
                            f"Validation failed for field: {field_name}"
                        )
                        validation_results["valid"] = False
                except Exception as e:
                    validation_results["warnings"].append(
                        f"Validation error for field {field_name}: {str(e)}"
                    )

        # Calculate quality metrics
        validation_results["quality_metrics"] = self._calculate_quality_metrics(df)

        return validation_results

    def _calculate_quality_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate data quality metrics."""
        metrics = {
            "total_records": len(df),
            "total_columns": len(df.columns),
            "null_counts": df.isnull().sum().to_dict(),
            "duplicate_count": df.duplicated().sum(),
            "data_types": df.dtypes.to_dict(),
            "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 / 1024,
        }

        # Add column-specific metrics
        for column in df.columns:
            if df[column].dtype in ["int64", "float64"]:
                metrics[f"{column}_stats"] = {
                    "mean": df[column].mean(),
                    "std": df[column].std(),
                    "min": df[column].min(),
                    "max": df[column].max(),
                }
            elif df[column].dtype == "object":
                metrics[f"{column}_unique_count"] = df[column].nunique()
                metrics[f"{column}_top_values"] = (
                    df[column].value_counts().head(5).to_dict()
                )

        return metrics


class DataTransformer:
    """Data transformation and processing."""

    def __init__(self):
        self.transformation_functions: Dict[str, Callable] = {}
        self.transformation_history: List[Dict[str, Any]] = []

    def add_transformation(self, name: str, function: Callable):
        """Add a transformation function."""
        self.transformation_functions[name] = function

    async def transform_data(
        self,
        data: Union[Dict, List[Dict], pd.DataFrame],
        transformations: List[str],
        config: Dict[str, Any] = None,
    ) -> pd.DataFrame:
        """Apply transformations to data."""
        if config is None:
            config = {}

        # Convert to DataFrame
        if isinstance(data, dict):
            df = pd.DataFrame([data])
        elif isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = data.copy()

        original_shape = df.shape

        # Apply transformations
        for transform_name in transformations:
            if transform_name not in self.transformation_functions:
                raise ValueError(f"Unknown transformation: {transform_name}")

            try:
                start_time = datetime.now()
                df = self.transformation_functions[transform_name](
                    df, **config.get(transform_name, {})
                )
                processing_time = (datetime.now() - start_time).total_seconds()

                self.transformation_history.append(
                    {
                        "transformation": transform_name,
                        "processing_time": processing_time,
                        "input_shape": original_shape,
                        "output_shape": df.shape,
                        "timestamp": start_time.isoformat(),
                    }
                )

            except Exception as e:
                logger.error(f"Transformation {transform_name} failed: {str(e)}")
                raise

        return df

    def get_transformation_history(self) -> List[Dict[str, Any]]:
        """Get transformation history."""
        return self.transformation_history.copy()


# Predefined transformation functions
async def normalize_numeric_columns(
    df: pd.DataFrame, columns: List[str] = None, method: str = "zscore"
) -> pd.DataFrame:
    """Normalize numeric columns."""
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()

    result_df = df.copy()

    for column in columns:
        if column in df.columns:
            if method == "zscore":
                result_df[column] = (df[column] - df[column].mean()) / df[column].std()
            elif method == "minmax":
                result_df[column] = (df[column] - df[column].min()) / (
                    df[column].max() - df[column].min()
                )

    return result_df


async def encode_categorical_columns(
    df: pd.DataFrame, columns: List[str] = None, method: str = "onehot"
) -> pd.DataFrame:
    """Encode categorical columns."""
    if columns is None:
        columns = df.select_dtypes(include=["object"]).columns.tolist()

    result_df = df.copy()

    for column in columns:
        if column in df.columns:
            if method == "onehot":
                dummies = pd.get_dummies(df[column], prefix=column)
                result_df = pd.concat([result_df.drop(column, axis=1), dummies], axis=1)
            elif method == "label":
                result_df[column] = df[column].astype("category").cat.codes

    return result_df


async def handle_missing_values(
    df: pd.DataFrame, strategy: str = "mean"
) -> pd.DataFrame:
    """Handle missing values."""
    result_df = df.copy()

    if strategy == "mean":
        result_df = result_df.fillna(
            result_df.select_dtypes(include=[np.number]).mean()
        )
    elif strategy == "median":
        result_df = result_df.fillna(
            result_df.select_dtypes(include=[np.number]).median()
        )
    elif strategy == "mode":
        result_df = result_df.fillna(result_df.mode().iloc[0])
    elif strategy == "drop":
        result_df = result_df.dropna()

    return result_df


async def remove_duplicates(df: pd.DataFrame, subset: List[str] = None) -> pd.DataFrame:
    """Remove duplicate rows."""
    return df.drop_duplicates(subset=subset)


async def filter_outliers(
    df: pd.DataFrame, columns: List[str] = None, method: str = "iqr"
) -> pd.DataFrame:
    """Filter outliers from numeric columns."""
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()

    result_df = df.copy()

    for column in columns:
        if column in df.columns:
            if method == "iqr":
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                result_df = result_df[
                    (result_df[column] >= lower_bound)
                    & (result_df[column] <= upper_bound)
                ]
            elif method == "zscore":
                z_scores = np.abs((df[column] - df[column].mean()) / df[column].std())
                result_df = result_df[z_scores < 3]

    return result_df


class DataEnricher:
    """Data enrichment and augmentation."""

    def __init__(self):
        self.enrichment_sources: Dict[str, Any] = {}
        self.enrichment_cache: Dict[str, Any] = {}

    def add_enrichment_source(self, name: str, source: Any):
        """Add an enrichment data source."""
        self.enrichment_sources[name] = source

    async def enrich_data(
        self, data: pd.DataFrame, enrichment_rules: List[Dict[str, Any]]
    ) -> pd.DataFrame:
        """Enrich data based on rules."""
        result_df = data.copy()

        for rule in enrichment_rules:
            source_name = rule["source"]
            join_key = rule["join_key"]
            enrich_fields = rule["fields"]

            if source_name not in self.enrichment_sources:
                logger.warning(f"Enrichment source {source_name} not found")
                continue

            try:
                enrichment_data = self.enrichment_sources[source_name]

                # Perform enrichment
                if isinstance(enrichment_data, pd.DataFrame):
                    enriched = result_df.merge(
                        enrichment_data[[join_key] + enrich_fields],
                        on=join_key,
                        how="left",
                    )
                    result_df = enriched
                else:
                    # Custom enrichment logic
                    for index, row in result_df.iterrows():
                        key_value = row[join_key]
                        enriched_data = await self._get_enriched_data(
                            source_name, key_value
                        )

                        for field in enrich_fields:
                            if field in enriched_data:
                                result_df.at[index, field] = enriched_data[field]

            except Exception as e:
                logger.error(f"Enrichment failed for rule {rule}: {str(e)}")

        return result_df

    async def _get_enriched_data(self, source_name: str, key: Any) -> Dict[str, Any]:
        """Get enriched data for a key."""
        cache_key = f"{source_name}:{key}"

        if cache_key in self.enrichment_cache:
            return self.enrichment_cache[cache_key]

        # Simulate enrichment lookup
        enriched_data = {"enriched_field": f"enriched_value_for_{key}"}
        self.enrichment_cache[cache_key] = enriched_data

        return enriched_data


class DataAggregator:
    """Data aggregation and summarization."""

    def __init__(self):
        self.aggregation_functions: Dict[str, Callable] = {
            "sum": lambda x: x.sum(),
            "mean": lambda x: x.mean(),
            "count": lambda x: x.count(),
            "min": lambda x: x.min(),
            "max": lambda x: x.max(),
            "std": lambda x: x.std(),
        }

    async def aggregate_data(
        self,
        data: pd.DataFrame,
        group_by: List[str],
        aggregations: Dict[str, List[str]],
    ) -> pd.DataFrame:
        """Aggregate data by groups."""
        agg_dict = {}

        for column, functions in aggregations.items():
            if column in data.columns:
                agg_dict[column] = functions

        if not agg_dict:
            raise ValueError("No valid aggregation columns found")

        result = data.groupby(group_by).agg(agg_dict).reset_index()

        # Flatten column names
        result.columns = [
            "_".join(col).strip() if col[1] else col[0] for col in result.columns.values
        ]

        return result


class StorageManager:
    """Storage abstraction layer."""

    def __init__(self, storage_type: StorageType = StorageType.S3):
        self.storage_type = storage_type
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize storage client."""
        if self.storage_type == StorageType.S3 and AWS_AVAILABLE:
            self.client = boto3.client("s3")
        elif self.storage_type == StorageType.GCS and GCP_AVAILABLE:
            self.client = storage.Client()
        else:
            logger.warning(f"Storage type {self.storage_type} not available")

    async def read_data(
        self, path: str, format: DataFormat = DataFormat.JSON
    ) -> pd.DataFrame:
        """Read data from storage."""
        if self.storage_type == StorageType.S3:
            return await self._read_from_s3(path, format)
        elif self.storage_type == StorageType.GCS:
            return await self._read_from_gcs(path, format)
        elif self.storage_type == StorageType.LOCAL:
            return await self._read_from_local(path, format)
        else:
            raise ValueError(f"Unsupported storage type: {self.storage_type}")

    async def write_data(
        self, data: pd.DataFrame, path: str, format: DataFormat = DataFormat.JSON
    ):
        """Write data to storage."""
        if self.storage_type == StorageType.S3:
            await self._write_to_s3(data, path, format)
        elif self.storage_type == StorageType.GCS:
            await self._write_to_gcs(data, path, format)
        elif self.storage_type == StorageType.LOCAL:
            await self._write_to_local(data, path, format)
        else:
            raise ValueError(f"Unsupported storage type: {self.storage_type}")

    async def _read_from_s3(self, path: str, format: DataFormat) -> pd.DataFrame:
        """Read data from S3."""
        bucket_name = path.split("/")[2]
        object_key = "/".join(path.split("/")[3:])

        response = self.client.get_object(Bucket=bucket_name, Key=object_key)
        data = response["Body"].read()

        if format == DataFormat.CSV:
            return pd.read_csv(BytesIO(data))
        elif format == DataFormat.JSON:
            return pd.read_json(BytesIO(data))
        elif format == DataFormat.PARQUET:
            return pd.read_parquet(BytesIO(data))
        else:
            raise ValueError(f"Unsupported format: {format}")

    async def _write_to_s3(self, data: pd.DataFrame, path: str, format: DataFormat):
        """Write data to S3."""
        bucket_name = path.split("/")[2]
        object_key = "/".join(path.split("/")[3:])

        if format == DataFormat.CSV:
            buffer = BytesIO()
            data.to_csv(buffer, index=False)
        elif format == DataFormat.JSON:
            buffer = BytesIO()
            data.to_json(buffer, orient="records")
        elif format == DataFormat.PARQUET:
            buffer = BytesIO()
            data.to_parquet(buffer, index=False)
        else:
            raise ValueError(f"Unsupported format: {format}")

        buffer.seek(0)
        self.client.put_object(
            Bucket=bucket_name, Key=object_key, Body=buffer.getvalue()
        )

    async def _read_from_local(self, path: str, format: DataFormat) -> pd.DataFrame:
        """Read data from local storage."""
        if format == DataFormat.CSV:
            return pd.read_csv(path)
        elif format == DataFormat.JSON:
            return pd.read_json(path)
        elif format == DataFormat.PARQUET:
            return pd.read_parquet(path)
        else:
            raise ValueError(f"Unsupported format: {format}")

    async def _write_to_local(self, data: pd.DataFrame, path: str, format: DataFormat):
        """Write data to local storage."""
        if format == DataFormat.CSV:
            data.to_csv(path, index=False)
        elif format == DataFormat.JSON:
            data.to_json(path, orient="records")
        elif format == DataFormat.PARQUET:
            data.to_parquet(path, index=False)
        else:
            raise ValueError(f"Unsupported format: {format}")


class ServerlessDataProcessor:
    """Main serverless data processing orchestrator."""

    def __init__(self, storage_type: StorageType = StorageType.S3):
        self.storage_manager = StorageManager(storage_type)
        self.validator = DataValidator()
        self.transformer = DataTransformer()
        self.enricher = DataEnricher()
        self.aggregator = DataAggregator()

        # Register default transformations
        self._register_default_transformations()

        # Processing statistics
        self.processing_stats: Dict[str, Any] = {
            "total_processed": 0,
            "successful_processed": 0,
            "failed_processed": 0,
            "average_processing_time": 0.0,
        }

    def _register_default_transformations(self):
        """Register default transformation functions."""
        self.transformer.add_transformation("normalize", normalize_numeric_columns)
        self.transformer.add_transformation("encode", encode_categorical_columns)
        self.transformer.add_transformation("handle_missing", handle_missing_values)
        self.transformer.add_transformation("remove_duplicates", remove_duplicates)
        self.transformer.add_transformation("filter_outliers", filter_outliers)

    async def process_data(self, config: DataProcessingConfig) -> ProcessingResult:
        """Process data according to configuration."""
        start_time = datetime.now()
        result = ProcessingResult(processing_id=config.processing_id)

        try:
            # Read input data
            logger.info(f"Reading data from: {config.input_source}")
            data = await self.storage_manager.read_data(
                config.input_source, config.input_format
            )

            # Validate data
            if config.processing_type == ProcessingType.VALIDATION:
                validation_result = await self.validator.validate_data(data)
                result.metadata["validation_result"] = validation_result

                if not validation_result["valid"]:
                    result.success = False
                    result.error_message = "Data validation failed"
                    return result

            # Transform data
            if config.processing_type == ProcessingType.TRANSFORMATION:
                transformations = config.custom_parameters.get("transformations", [])
                data = await self.transformer.transform_data(
                    data, transformations, config.custom_parameters
                )
                result.metadata["transformation_history"] = (
                    self.transformer.get_transformation_history()
                )

            # Enrich data
            if config.processing_type == ProcessingType.ENRICHMENT:
                enrichment_rules = config.custom_parameters.get("enrichment_rules", [])
                data = await self.enricher.enrich_data(data, enrichment_rules)

            # Aggregate data
            if config.processing_type == ProcessingType.AGGREGATION:
                group_by = config.custom_parameters.get("group_by", [])
                aggregations = config.custom_parameters.get("aggregations", {})
                data = await self.aggregator.aggregate_data(
                    data, group_by, aggregations
                )

            # Clean data
            if config.processing_type == ProcessingType.CLEANING:
                cleaning_steps = config.custom_parameters.get(
                    "cleaning_steps", ["handle_missing", "remove_duplicates"]
                )
                data = await self.transformer.transform_data(
                    data, cleaning_steps, config.custom_parameters
                )

            # Normalize data
            if config.processing_type == ProcessingType.NORMALIZATION:
                normalization_config = config.custom_parameters.get("normalization", {})
                data = await self.transformer.transform_data(
                    data, ["normalize"], normalization_config
                )

            # Write output data
            if config.output_destination:
                await self.storage_manager.write_data(
                    data, config.output_destination, config.output_format
                )
                result.output_path = config.output_destination

            # Update result
            result.success = True
            result.records_processed = len(data)
            result.processing_time_seconds = (
                datetime.now() - start_time
            ).total_seconds()

            # Update stats
            self.processing_stats["total_processed"] += 1
            self.processing_stats["successful_processed"] += 1
            self._update_average_processing_time(result.processing_time_seconds)

            logger.info(f"Processing completed successfully: {config.processing_id}")

        except Exception as e:
            result.success = False
            result.error_message = str(e)
            result.processing_time_seconds = (
                datetime.now() - start_time
            ).total_seconds()

            self.processing_stats["total_processed"] += 1
            self.processing_stats["failed_processed"] += 1

            logger.error(f"Processing failed: {config.processing_id} - {str(e)}")

        return result

    def _update_average_processing_time(self, processing_time: float):
        """Update average processing time."""
        current_avg = self.processing_stats["average_processing_time"]
        total_processed = self.processing_stats["successful_processed"]

        if total_processed == 1:
            self.processing_stats["average_processing_time"] = processing_time
        else:
            self.processing_stats["average_processing_time"] = (
                current_avg * (total_processed - 1) + processing_time
            ) / total_processed

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return self.processing_stats.copy()


# FastAPI application for serverless deployment
app = FastAPI(title="RaptorFlow Serverless Data Processing", version="1.0.0")
processor = ServerlessDataProcessor()


@app.post("/process")
async def process_data_endpoint(config: DataProcessingConfig):
    """Process data endpoint."""
    try:
        result = await processor.process_data(config)
        return result
    except Exception as e:
        logger.error(f"Processing endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get processing statistics."""
    return processor.get_processing_stats()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
