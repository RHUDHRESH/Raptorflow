"""
S.W.A.R.M. Phase 2: Distributed Data Processing (Spark/Dask)
Production-ready distributed data processing for large-scale ML operations
"""

import asyncio
import json
import logging
import os
import pickle
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, Iterator, List, Optional, Union

# Distributed computing imports
try:
    import dask
    import dask.array as da
    import dask.dataframe as dd
    from dask.distributed import Client, as_completed, performance_report

    DASK_AVAILABLE = True
except ImportError:
    DASK_AVAILABLE = False

try:
    import pyspark
    from pyspark.ml import Pipeline
    from pyspark.ml.feature import StandardScaler, VectorAssembler
    from pyspark.sql import DataFrame, SparkSession
    from pyspark.sql.functions import col, lit, when
    from pyspark.sql.types import (
        FloatType,
        IntegerType,
        StringType,
        StructField,
        StructType,
    )

    SPARK_AVAILABLE = True
except ImportError:
    SPARK_AVAILABLE = False

# Pandas and numpy
try:
    import numpy as np
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

logger = logging.getLogger("raptorflow.distributed_data_processing")


class ProcessingBackend(Enum):
    """Distributed processing backends."""

    DASK = "dask"
    SPARK = "spark"
    RAY = "ray"
    CUSTOM = "custom"


class DataFormat(Enum):
    """Supported data formats."""

    CSV = "csv"
    PARQUET = "parquet"
    JSON = "json"
    AVRO = "avro"
    ORC = "orc"
    DELTA = "delta"


class StorageType(Enum):
    """Storage types."""

    LOCAL = "local"
    S3 = "s3"
    GCS = "gcs"
    HDFS = "hdfs"
    AZURE_BLOB = "azure_blob"


@dataclass
class ClusterConfig:
    """Cluster configuration for distributed processing."""

    cluster_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    backend: ProcessingBackend = ProcessingBackend.DASK
    scheduler_address: str = ""
    num_workers: int = 4
    worker_memory: str = "4GB"
    worker_cores: int = 2
    auto_scaling: bool = True
    min_workers: int = 1
    max_workers: int = 10
    environment_variables: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "cluster_id": self.cluster_id,
            "backend": self.backend.value,
            "scheduler_address": self.scheduler_address,
            "num_workers": self.num_workers,
            "worker_memory": self.worker_memory,
            "worker_cores": self.worker_cores,
            "auto_scaling": self.auto_scaling,
            "min_workers": self.min_workers,
            "max_workers": self.max_workers,
            "environment_variables": self.environment_variables,
        }


@dataclass
class DataProcessingJob:
    """Data processing job configuration."""

    job_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    input_path: str = ""
    output_path: str = ""
    input_format: DataFormat = DataFormat.PARQUET
    output_format: DataFormat = DataFormat.PARQUET
    storage_type: StorageType = StorageType.LOCAL
    processing_steps: List[Dict[str, Any]] = field(default_factory=list)
    partition_columns: List[str] = field(default_factory=list)
    num_partitions: Optional[int] = None
    cache_intermediate: bool = True
    optimize_execution: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "job_id": self.job_id,
            "name": self.name,
            "input_path": self.input_path,
            "output_path": self.output_path,
            "input_format": self.input_format.value,
            "output_format": self.output_format.value,
            "storage_type": self.storage_type.value,
            "processing_steps": self.processing_steps,
            "partition_columns": self.partition_columns,
            "num_partitions": self.num_partitions,
            "cache_intermediate": self.cache_intermediate,
            "optimize_execution": self.optimize_execution,
        }


class DistributedDataProcessor(ABC):
    """Abstract base class for distributed data processors."""

    @abstractmethod
    async def initialize_cluster(self, config: ClusterConfig) -> bool:
        """Initialize processing cluster."""
        pass

    @abstractmethod
    async def shutdown_cluster(self):
        """Shutdown processing cluster."""
        pass

    @abstractmethod
    async def load_data(self, path: str, format: DataFormat, **kwargs) -> Any:
        """Load data from storage."""
        pass

    @abstractmethod
    async def save_data(
        self, data: Any, path: str, format: DataFormat, **kwargs
    ) -> bool:
        """Save data to storage."""
        pass

    @abstractmethod
    async def apply_transformations(
        self, data: Any, transformations: List[Dict[str, Any]]
    ) -> Any:
        """Apply data transformations."""
        pass

    @abstractmethod
    async def get_cluster_status(self) -> Dict[str, Any]:
        """Get cluster status."""
        pass


class DaskDataProcessor(DistributedDataProcessor):
    """Dask-based distributed data processor."""

    def __init__(self):
        self.client: Optional[Client] = None
        self.cluster_config: Optional[ClusterConfig] = None
        self.performance_reports: List[Dict[str, Any]] = []

    async def initialize_cluster(self, config: ClusterConfig) -> bool:
        """Initialize Dask cluster."""
        if not DASK_AVAILABLE:
            logger.error("Dask is not available")
            return False

        try:
            if config.scheduler_address:
                # Connect to existing cluster
                self.client = Client(config.scheduler_address)
            else:
                # Create local cluster
                from dask.distributed import LocalCluster

                cluster = LocalCluster(
                    n_workers=config.num_workers,
                    threads_per_worker=config.worker_cores,
                    memory_limit=config.worker_memory,
                    processes=True,
                )
                self.client = Client(cluster)

            self.cluster_config = config

            # Set environment variables
            for key, value in config.environment_variables.items():
                os.environ[key] = value

            logger.info(f"Dask cluster initialized with {config.num_workers} workers")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Dask cluster: {str(e)}")
            return False

    async def shutdown_cluster(self):
        """Shutdown Dask cluster."""
        if self.client:
            self.client.close()
            self.client = None
            logger.info("Dask cluster shutdown")

    async def load_data(self, path: str, format: DataFormat, **kwargs) -> dd.DataFrame:
        """Load data using Dask."""
        if not DASK_AVAILABLE:
            raise ImportError("Dask is required")

        if not self.client:
            raise RuntimeError("Cluster not initialized")

        try:
            if format == DataFormat.CSV:
                data = dd.read_csv(path, **kwargs)
            elif format == DataFormat.PARQUET:
                data = dd.read_parquet(path, **kwargs)
            elif format == DataFormat.JSON:
                data = dd.read_json(path, **kwargs)
            else:
                raise ValueError(f"Unsupported format: {format}")

            # Optimize partitions if specified
            if self.cluster_config.num_partitions:
                data = data.repartition(npartitions=self.cluster_config.num_partitions)

            logger.info(f"Loaded data from {path} with {data.npartitions} partitions")
            return data

        except Exception as e:
            logger.error(f"Failed to load data from {path}: {str(e)}")
            raise

    async def save_data(
        self, data: dd.DataFrame, path: str, format: DataFormat, **kwargs
    ) -> bool:
        """Save data using Dask."""
        if not DASK_AVAILABLE:
            raise ImportError("Dask is required")

        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(path), exist_ok=True)

            if format == DataFormat.CSV:
                data.to_csv(path, index=False, **kwargs)
            elif format == DataFormat.PARQUET:
                data.to_parquet(path, **kwargs)
            elif format == DataFormat.JSON:
                data.to_json(path, **kwargs)
            else:
                raise ValueError(f"Unsupported format: {format}")

            logger.info(f"Saved data to {path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save data to {path}: {str(e)}")
            return False

    async def apply_transformations(
        self, data: dd.DataFrame, transformations: List[Dict[str, Any]]
    ) -> dd.DataFrame:
        """Apply transformations to Dask DataFrame."""
        if not DASK_AVAILABLE:
            raise ImportError("Dask is required")

        result = data

        for transform in transformations:
            transform_type = transform["type"]

            if transform_type == "filter":
                condition = transform["condition"]
                result = result.query(condition)

            elif transform_type == "select_columns":
                columns = transform["columns"]
                result = result[columns]

            elif transform_type == "rename_columns":
                mapping = transform["mapping"]
                result = result.rename(columns=mapping)

            elif transform_type == "add_column":
                column_name = transform["column_name"]
                expression = transform["expression"]
                result[column_name] = result.eval(expression)

            elif transform_type == "group_by":
                group_cols = transform["group_columns"]
                agg_funcs = transform["aggregations"]
                result = result.groupby(group_cols).agg(agg_funcs).reset_index()

            elif transform_type == "sort":
                columns = transform["columns"]
                ascending = transform.get("ascending", True)
                result = result.sort_values(columns, ascending=ascending)

            elif transform_type == "drop_duplicates":
                subset = transform.get("subset")
                result = result.drop_duplicates(subset=subset)

            elif transform_type == "fill_na":
                value = transform.get("value", 0)
                method = transform.get("method", None)
                result = result.fillna(value=value, method=method)

            # Cache intermediate results if enabled
            if self.cluster_config.cache_intermediate:
                result = result.persist()

        return result

    async def get_cluster_status(self) -> Dict[str, Any]:
        """Get Dask cluster status."""
        if not self.client:
            return {"status": "not_initialized"}

        dashboard_link = self.client.dashboard_link

        # Get worker information
        workers = self.client.scheduler_info()["workers"]

        return {
            "status": "running",
            "dashboard_link": dashboard_link,
            "num_workers": len(workers),
            "worker_info": {
                worker_id: {
                    "cores": info["ncores"],
                    "memory": info["memory_limit"],
                    "utilization": info["metrics"].get("cpu", 0),
                }
                for worker_id, info in workers.items()
            },
        }

    async def generate_performance_report(self, job_name: str) -> str:
        """Generate performance report."""
        if not self.client:
            return ""

        report_path = f"./reports/dask_performance_{job_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

        with performance_report(filename=report_path):
            # This context manager generates the report
            pass

        self.performance_reports.append(
            {
                "job_name": job_name,
                "report_path": report_path,
                "timestamp": datetime.now().isoformat(),
            }
        )

        return report_path


class SparkDataProcessor(DistributedDataProcessor):
    """Spark-based distributed data processor."""

    def __init__(self):
        self.spark: Optional[SparkSession] = None
        self.cluster_config: Optional[ClusterConfig] = None

    async def initialize_cluster(self, config: ClusterConfig) -> bool:
        """Initialize Spark cluster."""
        if not SPARK_AVAILABLE:
            logger.error("Spark is not available")
            return False

        try:
            # Create Spark session
            builder = (
                SparkSession.builder.appName(f"raptorflow-spark-{config.cluster_id}")
                .config("spark.sql.adaptive.enabled", "true")
                .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
                .config("spark.sql.adaptive.skewJoin.enabled", "true")
            )

            # Add environment variables as Spark config
            for key, value in config.environment_variables.items():
                builder = builder.config(key, value)

            self.spark = builder.getOrCreate()
            self.cluster_config = config

            logger.info(f"Spark cluster initialized")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Spark cluster: {str(e)}")
            return False

    async def shutdown_cluster(self):
        """Shutdown Spark cluster."""
        if self.spark:
            self.spark.stop()
            self.spark = None
            logger.info("Spark cluster shutdown")

    async def load_data(self, path: str, format: DataFormat, **kwargs) -> DataFrame:
        """Load data using Spark."""
        if not SPARK_AVAILABLE:
            raise ImportError("Spark is required")

        if not self.spark:
            raise RuntimeError("Cluster not initialized")

        try:
            if format == DataFormat.CSV:
                data = self.spark.read.csv(path, header=True, **kwargs)
            elif format == DataFormat.PARQUET:
                data = self.spark.read.parquet(path, **kwargs)
            elif format == DataFormat.JSON:
                data = self.spark.read.json(path, **kwargs)
            elif format == DataFormat.DELTA:
                data = self.spark.read.format("delta").load(path, **kwargs)
            else:
                raise ValueError(f"Unsupported format: {format}")

            # Cache if enabled
            if self.cluster_config.cache_intermediate:
                data.cache()

            logger.info(f"Loaded data from {path}")
            return data

        except Exception as e:
            logger.error(f"Failed to load data from {path}: {str(e)}")
            raise

    async def save_data(
        self, data: DataFrame, path: str, format: DataFormat, **kwargs
    ) -> bool:
        """Save data using Spark."""
        if not SPARK_AVAILABLE:
            raise ImportError("Spark is required")

        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(path), exist_ok=True)

            if format == DataFormat.CSV:
                data.write.csv(path, header=True, **kwargs)
            elif format == DataFormat.PARQUET:
                data.write.parquet(path, **kwargs)
            elif format == DataFormat.JSON:
                data.write.json(path, **kwargs)
            elif format == DataFormat.DELTA:
                data.write.format("delta").save(path, **kwargs)
            else:
                raise ValueError(f"Unsupported format: {format}")

            logger.info(f"Saved data to {path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save data to {path}: {str(e)}")
            return False

    async def apply_transformations(
        self, data: DataFrame, transformations: List[Dict[str, Any]]
    ) -> DataFrame:
        """Apply transformations to Spark DataFrame."""
        if not SPARK_AVAILABLE:
            raise ImportError("Spark is required")

        result = data

        for transform in transformations:
            transform_type = transform["type"]

            if transform_type == "filter":
                condition = transform["condition"]
                result = result.filter(condition)

            elif transform_type == "select_columns":
                columns = transform["columns"]
                result = result.select(*columns)

            elif transform_type == "rename_columns":
                mapping = transform["mapping"]
                for old_name, new_name in mapping.items():
                    result = result.withColumnRenamed(old_name, new_name)

            elif transform_type == "add_column":
                column_name = transform["column_name"]
                expression = transform["expression"]
                result = result.withColumn(column_name, expr(expression))

            elif transform_type == "group_by":
                group_cols = transform["group_columns"]
                agg_funcs = transform["aggregations"]
                result = result.groupBy(*group_cols).agg(agg_funcs)

            elif transform_type == "sort":
                columns = transform["columns"]
                ascending = transform.get("ascending", True)
                result = result.orderBy(*columns, ascending=ascending)

            elif transform_type == "drop_duplicates":
                subset = transform.get("subset")
                result = result.dropDuplicates(subset)

            elif transform_type == "fill_na":
                value = transform.get("value", 0)
                subset = transform.get("subset")
                result = result.fillna(value, subset)

            elif transform_type == "feature_engineering":
                # Feature engineering with Spark ML
                feature_cols = transform["feature_columns"]
                assembler = VectorAssembler(
                    inputCols=feature_cols, outputCol="features"
                )
                scaler = StandardScaler(
                    inputCol="features", outputCol="scaled_features"
                )

                pipeline = Pipeline(stages=[assembler, scaler])
                model = pipeline.fit(result)
                result = model.transform(result)

            # Cache intermediate results if enabled
            if self.cluster_config.cache_intermediate:
                result.cache()

        return result

    async def get_cluster_status(self) -> Dict[str, Any]:
        """Get Spark cluster status."""
        if not self.spark:
            return {"status": "not_initialized"}

        # Get Spark UI information
        spark_ui_url = self.spark.conf.get("spark.ui.proxyBase", "")

        return {
            "status": "running",
            "spark_ui_url": spark_ui_url,
            "app_name": self.spark.sparkContext.appName,
            "version": self.spark.version,
        }


class DistributedDataProcessingOrchestrator:
    """Orchestrator for distributed data processing jobs."""

    def __init__(self):
        self.processors: Dict[ProcessingBackend, DistributedDataProcessor] = {
            ProcessingBackend.DASK: DaskDataProcessor(),
            ProcessingBackend.SPARK: SparkDataProcessor(),
        }
        self.active_jobs: Dict[str, DataProcessingJob] = {}
        self.job_status: Dict[str, Dict[str, Any]] = {}
        self.job_history: List[Dict[str, Any]] = []

    async def submit_job(self, job: DataProcessingJob) -> str:
        """Submit a data processing job."""
        # Determine backend from job or use default
        backend = ProcessingBackend.DASK  # Default to Dask

        # Initialize processor
        processor = self.processors[backend]

        # Create cluster config
        cluster_config = ClusterConfig(
            backend=backend, num_workers=4, worker_memory="4GB", worker_cores=2
        )

        # Store job
        self.active_jobs[job.job_id] = job

        # Initialize job status
        self.job_status[job.job_id] = {
            "status": "pending",
            "backend": backend.value,
            "cluster_config": cluster_config.to_dict(),
            "start_time": None,
            "end_time": None,
            "error": None,
            "metrics": {},
        }

        return job.job_id

    async def execute_job(self, job_id: str) -> Dict[str, Any]:
        """Execute a data processing job."""
        if job_id not in self.active_jobs:
            return {"success": False, "error": "Job not found"}

        job = self.active_jobs[job_id]
        status = self.job_status[job_id]
        backend = ProcessingBackend(status["backend"])
        processor = self.processors[backend]

        try:
            # Update status
            status["status"] = "running"
            status["start_time"] = datetime.now().isoformat()

            # Initialize cluster
            cluster_config = ClusterConfig(**status["cluster_config"])
            if not await processor.initialize_cluster(cluster_config):
                raise RuntimeError("Failed to initialize cluster")

            # Load data
            data = await processor.load_data(
                job.input_path,
                job.input_format,
                storage_options=self._get_storage_options(job.storage_type),
            )

            # Apply transformations
            if job.processing_steps:
                data = await processor.apply_transformations(data, job.processing_steps)

            # Save data
            success = await processor.save_data(
                data,
                job.output_path,
                job.output_format,
                storage_options=self._get_storage_options(job.storage_type),
            )

            if not success:
                raise RuntimeError("Failed to save data")

            # Update status
            status["status"] = "completed"
            status["end_time"] = datetime.now().isoformat()

            # Record job completion
            self.job_history.append(
                {
                    "job_id": job_id,
                    "job_config": job.to_dict(),
                    "status": status,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            return {"success": True, "job_id": job_id}

        except Exception as e:
            status["status"] = "failed"
            status["error"] = str(e)
            status["end_time"] = datetime.now().isoformat()

            logger.error(f"Job {job_id} failed: {str(e)}")
            return {"success": False, "error": str(e)}

        finally:
            # Cleanup
            await processor.shutdown_cluster()

    def _get_storage_options(self, storage_type: StorageType) -> Dict[str, Any]:
        """Get storage options for different storage types."""
        if storage_type == StorageType.S3:
            return {
                "key": os.getenv("AWS_ACCESS_KEY_ID"),
                "secret": os.getenv("AWS_SECRET_ACCESS_KEY"),
                "client_kwargs": {
                    "region_name": os.getenv("AWS_DEFAULT_REGION", "us-west-2")
                },
            }
        elif storage_type == StorageType.GCS:
            return {
                "token": os.getenv("GCS_TOKEN"),
                "project": os.getenv("GCP_PROJECT_ID"),
            }
        elif storage_type == StorageType.AZURE_BLOB:
            return {
                "account_name": os.getenv("AZURE_STORAGE_ACCOUNT_NAME"),
                "account_key": os.getenv("AZURE_STORAGE_ACCOUNT_KEY"),
            }
        else:
            return {}

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get job status."""
        if job_id not in self.job_status:
            return {}

        return self.job_status[job_id].copy()

    def list_jobs(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all jobs with optional status filter."""
        jobs = []

        for job_id, status in self.job_status.items():
            if status_filter is None or status["status"] == status_filter:
                job_info = {
                    "job_id": job_id,
                    "job_config": self.active_jobs[job_id].to_dict(),
                    "status": status,
                }
                jobs.append(job_info)

        return jobs

    def get_job_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get job history."""
        return self.job_history[-limit:]


# Predefined data processing templates
class DataProcessingTemplates:
    """Predefined data processing templates."""

    @staticmethod
    def get_ml_data_preprocessing_template() -> DataProcessingJob:
        """Get ML data preprocessing template."""
        return DataProcessingJob(
            name="ml_data_preprocessing",
            input_path="s3://data/raw/",
            output_path="s3://data/processed/",
            input_format=DataFormat.PARQUET,
            output_format=DataFormat.PARQUET,
            storage_type=StorageType.S3,
            processing_steps=[
                {"type": "filter", "condition": "age > 0 and age < 100"},
                {"type": "fill_na", "value": 0, "subset": ["income", "score"]},
                {
                    "type": "add_column",
                    "column_name": "age_group",
                    "expression": "case when age < 18 then 'minor' when age < 65 then 'adult' else 'senior' end",
                },
                {
                    "type": "select_columns",
                    "columns": ["age", "income", "score", "age_group"],
                },
                {
                    "type": "feature_engineering",
                    "feature_columns": ["age", "income", "score"],
                },
            ],
            partition_columns=["age_group"],
            cache_intermediate=True,
            optimize_execution=True,
        )

    @staticmethod
    def get_analytics_aggregation_template() -> DataProcessingJob:
        """Get analytics aggregation template."""
        return DataProcessingJob(
            name="analytics_aggregation",
            input_path="s3://data/events/",
            output_path="s3://data/aggregated/",
            input_format=DataFormat.JSON,
            output_format=DataFormat.PARQUET,
            storage_type=StorageType.S3,
            processing_steps=[
                {"type": "filter", "condition": "timestamp >= '2023-01-01'"},
                {
                    "type": "add_column",
                    "column_name": "event_date",
                    "expression": "to_date(timestamp)",
                },
                {
                    "type": "group_by",
                    "group_columns": ["event_date", "event_type"],
                    "aggregations": {
                        "count": "count",
                        "unique_users": "countDistinct(user_id)",
                        "avg_value": "avg(value)",
                    },
                },
                {
                    "type": "sort",
                    "columns": ["event_date", "count"],
                    "ascending": [True, False],
                },
            ],
            partition_columns=["event_date"],
            num_partitions=100,
            optimize_execution=True,
        )


if __name__ == "__main__":
    # Example usage
    async def main():
        orchestrator = DistributedDataProcessingOrchestrator()

        # Create a sample job
        job = DataProcessingTemplates.get_ml_data_preprocessing_template()

        # Submit and execute job
        job_id = await orchestrator.submit_job(job)
        print(f"Submitted job: {job_id}")

        result = await orchestrator.execute_job(job_id)
        print(f"Job result: {result}")

        # Get job status
        status = orchestrator.get_job_status(job_id)
        print(f"Job status: {status}")

    asyncio.run(main())
