"""
S.W.A.R.M. Phase 2: Serverless ML Infrastructure Design
Enterprise-grade serverless architecture for ML operations at scale
"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class CloudProvider(Enum):
    """Cloud provider options."""

    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"


class FunctionType(Enum):
    """Serverless function types."""

    INFERENCE = "inference"
    PREPROCESSING = "preprocessing"
    POSTPROCESSING = "postprocessing"
    MONITORING = "monitoring"
    TRAINING = "training"
    VALIDATION = "validation"


class TriggerType(Enum):
    """Function trigger types."""

    HTTP = "http"
    QUEUE = "queue"
    SCHEDULE = "schedule"
    STREAM = "stream"
    DATABASE = "database"


@dataclass
class ServerlessFunctionSpec:
    """Serverless function specification."""

    function_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    function_type: FunctionType = FunctionType.INFERENCE
    cloud_provider: CloudProvider = CloudProvider.AWS
    runtime: str = "python3.9"
    memory_mb: int = 512
    timeout_seconds: int = 300
    concurrency_limit: int = 100
    environment_variables: Dict[str, str] = field(default_factory=dict)
    layers: List[str] = field(default_factory=list)
    triggers: List[Dict[str, Any]] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    cold_start_optimization: bool = True
    vpc_config: Optional[Dict[str, Any]] = None
    security_config: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "function_id": self.function_id,
            "name": self.name,
            "function_type": self.function_type.value,
            "cloud_provider": self.cloud_provider.value,
            "runtime": self.runtime,
            "memory_mb": self.memory_mb,
            "timeout_seconds": self.timeout_seconds,
            "concurrency_limit": self.concurrency_limit,
            "environment_variables": self.environment_variables,
            "layers": self.layers,
            "triggers": self.triggers,
            "dependencies": self.dependencies,
            "cold_start_optimization": self.cold_start_optimization,
            "vpc_config": self.vpc_config,
            "security_config": self.security_config,
        }


@dataclass
class DataPipelineSpec:
    """Serverless data processing pipeline specification."""

    pipeline_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    input_source: str = ""
    output_destination: str = ""
    processing_functions: List[str] = field(default_factory=list)
    error_handling: Dict[str, Any] = field(default_factory=dict)
    monitoring_config: Dict[str, Any] = field(default_factory=dict)
    scaling_config: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "pipeline_id": self.pipeline_id,
            "name": self.name,
            "description": self.description,
            "input_source": self.input_source,
            "output_destination": self.output_destination,
            "processing_functions": self.processing_functions,
            "error_handling": self.error_handling,
            "monitoring_config": self.monitoring_config,
            "scaling_config": self.scaling_config,
        }


@dataclass
class MonitoringConfig:
    """Serverless monitoring configuration."""

    metrics_collection: bool = True
    log_aggregation: bool = True
    distributed_tracing: bool = True
    alerting: bool = True
    dashboard: bool = True
    retention_days: int = 30
    sampling_rate: float = 0.1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "metrics_collection": self.metrics_collection,
            "log_aggregation": self.log_aggregation,
            "distributed_tracing": self.distributed_tracing,
            "alerting": self.alerting,
            "dashboard": self.dashboard,
            "retention_days": self.retention_days,
            "sampling_rate": self.sampling_rate,
        }


@dataclass
class SecurityConfig:
    """Serverless security configuration."""

    encryption_at_rest: bool = True
    encryption_in_transit: bool = True
    iam_roles: List[str] = field(default_factory=list)
    vpc_isolation: bool = True
    api_key_auth: bool = True
    jwt_auth: bool = True
    rate_limiting: bool = True
    input_validation: bool = True
    audit_logging: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "encryption_at_rest": self.encryption_at_rest,
            "encryption_in_transit": self.encryption_in_transit,
            "iam_roles": self.iam_roles,
            "vpc_isolation": self.vpc_isolation,
            "api_key_auth": self.api_key_auth,
            "jwt_auth": self.jwt_auth,
            "rate_limiting": self.rate_limiting,
            "input_validation": self.input_validation,
            "audit_logging": self.audit_logging,
        }


class ServerlessMLArchitecture:
    """Serverless ML architecture design system."""

    def __init__(self, cloud_provider: CloudProvider = CloudProvider.AWS):
        self.cloud_provider = cloud_provider
        self.functions: Dict[str, ServerlessFunctionSpec] = {}
        self.pipelines: Dict[str, DataPipelineSpec] = {}
        self.monitoring_config = MonitoringConfig()
        self.security_config = SecurityConfig()
        self.architecture_validated = False

    def create_inference_function(
        self,
        name: str,
        model_path: str,
        memory_mb: int = 1024,
        timeout_seconds: int = 60,
        **kwargs,
    ) -> ServerlessFunctionSpec:
        """Create a serverless inference function."""
        function = ServerlessFunctionSpec(
            name=name,
            function_type=FunctionType.INFERENCE,
            cloud_provider=self.cloud_provider,
            memory_mb=memory_mb,
            timeout_seconds=timeout_seconds,
            environment_variables={
                "MODEL_PATH": model_path,
                "FUNCTION_TYPE": "inference",
            },
            triggers=[
                {
                    "type": TriggerType.HTTP.value,
                    "config": {
                        "method": "POST",
                        "path": f"/inference/{name}",
                        "auth_required": True,
                    },
                }
            ],
            cold_start_optimization=True,
            **kwargs,
        )

        self.functions[function.function_id] = function
        return function

    def create_preprocessing_function(
        self,
        name: str,
        processing_config: Dict[str, Any],
        memory_mb: int = 512,
        **kwargs,
    ) -> ServerlessFunctionSpec:
        """Create a data preprocessing function."""
        function = ServerlessFunctionSpec(
            name=name,
            function_type=FunctionType.PREPROCESSING,
            cloud_provider=self.cloud_provider,
            memory_mb=memory_mb,
            environment_variables={
                "PROCESSING_CONFIG": json.dumps(processing_config),
                "FUNCTION_TYPE": "preprocessing",
            },
            triggers=[
                {
                    "type": TriggerType.QUEUE.value,
                    "config": {"queue_name": f"preprocessing-{name}", "batch_size": 10},
                }
            ],
            **kwargs,
        )

        self.functions[function.function_id] = function
        return function

    def create_monitoring_function(
        self, name: str, monitoring_targets: List[str], **kwargs
    ) -> ServerlessFunctionSpec:
        """Create a monitoring function."""
        function = ServerlessFunctionSpec(
            name=name,
            function_type=FunctionType.MONITORING,
            cloud_provider=self.cloud_provider,
            memory_mb=256,
            timeout_seconds=300,
            environment_variables={
                "MONITORING_TARGETS": json.dumps(monitoring_targets),
                "FUNCTION_TYPE": "monitoring",
            },
            triggers=[
                {
                    "type": TriggerType.SCHEDULE.value,
                    "config": {"schedule": "rate(5 minutes)", "enabled": True},
                }
            ],
            **kwargs,
        )

        self.functions[function.function_id] = function
        return function

    def create_data_pipeline(
        self,
        name: str,
        input_source: str,
        output_destination: str,
        processing_steps: List[str],
        **kwargs,
    ) -> DataPipelineSpec:
        """Create a serverless data processing pipeline."""
        pipeline = DataPipelineSpec(
            name=name,
            input_source=input_source,
            output_destination=output_destination,
            processing_functions=processing_steps,
            error_handling={
                "retry_attempts": 3,
                "retry_delay": 60,
                "dead_letter_queue": f"{name}-dlq",
            },
            monitoring_config={
                "track_latency": True,
                "track_errors": True,
                "alert_on_failure": True,
            },
            scaling_config={
                "auto_scale": True,
                "min_concurrency": 1,
                "max_concurrency": 100,
            },
            **kwargs,
        )

        self.pipelines[pipeline.pipeline_id] = pipeline
        return pipeline

    def setup_cold_start_optimization(self, function_id: str):
        """Setup cold start optimization for a function."""
        if function_id not in self.functions:
            raise ValueError(f"Function {function_id} not found")

        function = self.functions[function_id]

        # Provisioned concurrency
        function.environment_variables["PROVISIONED_CONCURRENCY"] = "10"

        # Keep-alive mechanism
        function.triggers.append(
            {
                "type": TriggerType.SCHEDULE.value,
                "config": {"schedule": "rate(5 minutes)", "keep_alive": True},
            }
        )

        # Optimized runtime
        if function.cloud_provider == CloudProvider.AWS:
            function.runtime = "python3.9"
        elif function.cloud_provider == CloudProvider.GCP:
            function.runtime = "python39"

    def setup_vpc_configuration(self, function_id: str, vpc_config: Dict[str, Any]):
        """Setup VPC configuration for a function."""
        if function_id not in self.functions:
            raise ValueError(f"Function {function_id} not found")

        self.functions[function_id].vpc_config = vpc_config

    def setup_security_configuration(
        self, function_id: str, security_config: Dict[str, Any]
    ):
        """Setup security configuration for a function."""
        if function_id not in self.functions:
            raise ValueError(f"Function {function_id} not found")

        self.functions[function_id].security_config = security_config

    def validate_architecture(self) -> Dict[str, Any]:
        """Validate the serverless architecture."""
        validation_results = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "recommendations": [],
        }

        # Validate functions
        for function_id, function in self.functions.items():
            # Check memory limits
            if function.memory_mb > 10240:  # 10GB limit
                validation_results["warnings"].append(
                    f"Function {function.name} exceeds recommended memory limit"
                )

            # Check timeout limits
            if function.timeout_seconds > 900:  # 15 minutes limit
                validation_results["warnings"].append(
                    f"Function {function.name} exceeds recommended timeout limit"
                )

            # Check cold start optimization
            if function.cold_start_optimization and not function.triggers:
                validation_results["warnings"].append(
                    f"Function {function.name} has cold start optimization but no triggers"
                )

        # Validate pipelines
        for pipeline_id, pipeline in self.pipelines.items():
            # Check processing functions exist
            for func_name in pipeline.processing_functions:
                found = any(f.name == func_name for f in self.functions.values())
                if not found:
                    validation_results["errors"].append(
                        f"Pipeline {pipeline.name} references non-existent function {func_name}"
                    )
                    validation_results["valid"] = False

        # Check monitoring configuration
        if not self.monitoring_config.metrics_collection:
            validation_results["recommendations"].append(
                "Enable metrics collection for better observability"
            )

        # Check security configuration
        if not self.security_config.encryption_at_rest:
            validation_results["warnings"].append("Encryption at rest is not enabled")

        self.architecture_validated = validation_results["valid"]
        return validation_results

    def get_architecture_summary(self) -> Dict[str, Any]:
        """Get architecture summary."""
        return {
            "cloud_provider": self.cloud_provider.value,
            "total_functions": len(self.functions),
            "function_types": {
                func_type.value: sum(
                    1 for f in self.functions.values() if f.function_type == func_type
                )
                for func_type in FunctionType
            },
            "total_pipelines": len(self.pipelines),
            "monitoring_enabled": self.monitoring_config.metrics_collection,
            "security_enabled": self.security_config.encryption_at_rest,
            "architecture_validated": self.architecture_validated,
            "estimated_monthly_cost": self._estimate_monthly_cost(),
        }

    def _estimate_monthly_cost(self) -> Dict[str, float]:
        """Estimate monthly cost for the architecture."""
        # Simplified cost estimation
        total_cost = 0.0
        function_costs = {}

        for function_id, function in self.functions.items():
            # AWS Lambda pricing example
            if function.cloud_provider == CloudProvider.AWS:
                # $0.20 per 1M requests
                requests_per_month = 1000000  # Estimate
                request_cost = requests_per_month * 0.20 / 1000000

                # $0.0000166667 per GB-second
                compute_cost = (
                    (function.memory_mb / 1024)
                    * function.timeout_seconds
                    * requests_per_month
                    * 0.0000166667
                )

                function_cost = request_cost + compute_cost
                function_costs[function.name] = function_cost
                total_cost += function_cost

        return {
            "total_estimated_cost": total_cost,
            "function_costs": function_costs,
            "currency": "USD",
            "period": "monthly",
        }

    def export_configuration(self, format: str = "json") -> str:
        """Export architecture configuration."""
        config = {
            "cloud_provider": self.cloud_provider.value,
            "functions": {fid: func.to_dict() for fid, func in self.functions.items()},
            "pipelines": {pid: pipe.to_dict() for pid, pipe in self.pipelines.items()},
            "monitoring": self.monitoring_config.to_dict(),
            "security": self.security_config.to_dict(),
            "architecture_validated": self.architecture_validated,
        }

        if format == "json":
            return json.dumps(config, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")


# Predefined architecture templates
class ServerlessTemplates:
    """Predefined serverless architecture templates."""

    @staticmethod
    def get_ml_inference_template(
        cloud_provider: CloudProvider = CloudProvider.AWS,
    ) -> ServerlessMLArchitecture:
        """Get ML inference serverless template."""
        architecture = ServerlessMLArchitecture(cloud_provider)

        # Inference function
        architecture.create_inference_function(
            name="ml-inference",
            model_path="s3://models/latest/",
            memory_mb=1024,
            timeout_seconds=60,
        )

        # Preprocessing function
        architecture.create_preprocessing_function(
            name="data-preprocessing",
            processing_config={"normalize": True, "encode": True},
        )

        # Postprocessing function
        architecture.create_preprocessing_function(
            name="data-postprocessing", processing_config={"format_output": True}
        )

        # Monitoring function
        architecture.create_monitoring_function(
            name="inference-monitoring",
            monitoring_targets=[
                "ml-inference",
                "data-preprocessing",
                "data-postprocessing",
            ],
        )

        # Data pipeline
        architecture.create_data_pipeline(
            name="inference-pipeline",
            input_source="s3://input-data/",
            output_destination="s3://output-data/",
            processing_steps=[
                "data-preprocessing",
                "ml-inference",
                "data-postprocessing",
            ],
        )

        return architecture

    @staticmethod
    def get_batch_processing_template(
        cloud_provider: CloudProvider = CloudProvider.AWS,
    ) -> ServerlessMLArchitecture:
        """Get batch processing serverless template."""
        architecture = ServerlessMLArchitecture(cloud_provider)

        # Batch inference function
        architecture.create_inference_function(
            name="batch-inference",
            model_path="s3://models/batch/",
            memory_mb=2048,
            timeout_seconds=900,  # 15 minutes for batch
        )

        # Data validation function
        architecture.create_preprocessing_function(
            name="data-validation",
            processing_config={"schema_validation": True, "quality_checks": True},
        )

        # Results aggregation function
        architecture.create_preprocessing_function(
            name="results-aggregation",
            processing_config={"aggregate_results": True, "generate_report": True},
        )

        # Batch monitoring
        architecture.create_monitoring_function(
            name="batch-monitoring",
            monitoring_targets=[
                "batch-inference",
                "data-validation",
                "results-aggregation",
            ],
        )

        # Batch pipeline
        architecture.create_data_pipeline(
            name="batch-processing-pipeline",
            input_source="s3://batch-input/",
            output_destination="s3://batch-output/",
            processing_steps=[
                "data-validation",
                "batch-inference",
                "results-aggregation",
            ],
        )

        return architecture

    @staticmethod
    def get_real_time_inference_template(
        cloud_provider: CloudProvider = CloudProvider.AWS,
    ) -> ServerlessMLArchitecture:
        """Get real-time inference serverless template."""
        architecture = ServerlessMLArchitecture(cloud_provider)

        # Real-time inference function (optimized for low latency)
        architecture.create_inference_function(
            name="realtime-inference",
            model_path="s3://models/realtime/",
            memory_mb=512,
            timeout_seconds=10,  # Low timeout for real-time
        )

        # Input validation function
        architecture.create_preprocessing_function(
            name="input-validation",
            processing_config={"validate_format": True, "sanitize_input": True},
        )

        # Response formatting function
        architecture.create_preprocessing_function(
            name="response-formatting",
            processing_config={"format_response": True, "add_metadata": True},
        )

        # Real-time monitoring
        architecture.create_monitoring_function(
            name="realtime-monitoring",
            monitoring_targets=[
                "realtime-inference",
                "input-validation",
                "response-formatting",
            ],
        )

        # Real-time pipeline
        architecture.create_data_pipeline(
            name="realtime-pipeline",
            input_source="api/requests/",
            output_destination="api/responses/",
            processing_steps=[
                "input-validation",
                "realtime-inference",
                "response-formatting",
            ],
        )

        # Setup cold start optimization for real-time
        for func_id in architecture.functions:
            architecture.setup_cold_start_optimization(func_id)

        return architecture


if __name__ == "__main__":
    # Example usage
    architecture = ServerlessTemplates.get_ml_inference_template()

    # Validate architecture
    validation = architecture.validate_architecture()
    print("Architecture Validation:", validation)

    # Get summary
    summary = architecture.get_architecture_summary()
    print("Architecture Summary:", summary)

    # Export configuration
    config = architecture.export_configuration()
    print("Configuration exported successfully")
