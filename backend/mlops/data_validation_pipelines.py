"""
S.W.A.R.M. Phase 2: Advanced MLOps - Data Validation Pipelines
Production-ready data validation pipelines with automated checks and workflows
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
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

logger = logging.getLogger("raptorflow.data_validation_pipelines")


class PipelineStatus(Enum):
    """Pipeline execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ValidationLevel(Enum):
    """Data validation levels."""

    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    PRODUCTION = "production"


class PipelineTrigger(Enum):
    """Pipeline trigger types."""

    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT_DRIVEN = "event_driven"
    API_CALL = "api_call"


@dataclass
class ValidationPipelineConfig:
    """Configuration for data validation pipeline."""

    pipeline_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    validation_level: ValidationLevel = ValidationLevel.STANDARD
    trigger_type: PipelineTrigger = PipelineTrigger.MANUAL
    schedule: Optional[str] = None  # Cron expression
    data_sources: List[str] = field(default_factory=list)
    validation_rules: List[str] = field(default_factory=list)
    notification_channels: List[str] = field(default_factory=list)
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    timeout_minutes: int = 60
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "pipeline_id": self.pipeline_id,
            "name": self.name,
            "description": self.description,
            "validation_level": self.validation_level.value,
            "trigger_type": self.trigger_type.value,
            "schedule": self.schedule,
            "data_sources": self.data_sources,
            "validation_rules": self.validation_rules,
            "notification_channels": self.notification_channels,
            "retry_policy": self.retry_policy,
            "timeout_minutes": self.timeout_minutes,
            "enabled": self.enabled,
        }


@dataclass
class PipelineExecution:
    """Pipeline execution record."""

    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    pipeline_id: str = ""
    status: PipelineStatus = PipelineStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    input_data_summary: Dict[str, Any] = field(default_factory=dict)
    validation_results: List[Dict[str, Any]] = field(default_factory=list)
    error_message: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "execution_id": self.execution_id,
            "pipeline_id": self.pipeline_id,
            "status": self.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "input_data_summary": self.input_data_summary,
            "validation_results": self.validation_results,
            "error_message": self.error_message,
            "metrics": self.metrics,
        }


class ValidationRule:
    """Base class for validation rules."""

    def __init__(self, rule_id: str, name: str, description: str):
        self.rule_id = rule_id
        self.name = name
        self.description = description
        self.enabled = True

    def validate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Validate data against this rule."""
        raise NotImplementedError("Subclasses must implement validate method")


class SchemaValidationRule(ValidationRule):
    """Schema validation rule."""

    def __init__(self, rule_id: str, expected_schema: Dict[str, str]):
        super().__init__(
            rule_id,
            "Schema Validation",
            "Validates data schema against expected structure",
        )
        self.expected_schema = expected_schema

    def validate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Validate data schema."""
        results = {
            "rule_id": self.rule_id,
            "rule_name": self.name,
            "passed": True,
            "issues": [],
            "details": {},
        }

        # Check column existence
        missing_columns = set(self.expected_schema.keys()) - set(data.columns)
        extra_columns = set(data.columns) - set(self.expected_schema.keys())

        if missing_columns:
            results["passed"] = False
            results["issues"].append(f"Missing columns: {list(missing_columns)}")

        if extra_columns:
            results["issues"].append(f"Extra columns: {list(extra_columns)}")

        # Check data types
        type_mismatches = []
        for column, expected_type in self.expected_schema.items():
            if column in data.columns:
                actual_type = str(data[column].dtype)
                if expected_type not in actual_type:
                    type_mismatches.append(
                        f"{column}: expected {expected_type}, got {actual_type}"
                    )

        if type_mismatches:
            results["passed"] = False
            results["issues"].extend(type_mismatches)

        results["details"] = {
            "expected_columns": list(self.expected_schema.keys()),
            "actual_columns": list(data.columns),
            "missing_columns": list(missing_columns),
            "extra_columns": list(extra_columns),
            "type_mismatches": type_mismatches,
        }

        return results


class RangeValidationRule(ValidationRule):
    """Range validation rule for numeric columns."""

    def __init__(self, rule_id: str, column_ranges: Dict[str, Tuple[float, float]]):
        super().__init__(
            rule_id,
            "Range Validation",
            "Validates numeric values within specified ranges",
        )
        self.column_ranges = column_ranges

    def validate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Validate value ranges."""
        results = {
            "rule_id": self.rule_id,
            "rule_name": self.name,
            "passed": True,
            "issues": [],
            "details": {},
        }

        range_violations = {}

        for column, (min_val, max_val) in self.column_ranges.items():
            if column not in data.columns:
                continue

            if not pd.api.types.is_numeric_dtype(data[column]):
                results["issues"].append(f"Column {column} is not numeric")
                continue

            violations = data[(data[column] < min_val) | (data[column] > max_val)]

            if len(violations) > 0:
                range_violations[column] = {
                    "min_violations": len(data[data[column] < min_val]),
                    "max_violations": len(data[data[column] > max_val]),
                    "total_violations": len(violations),
                    "violation_percentage": len(violations) / len(data) * 100,
                }
                results["passed"] = False

        if range_violations:
            results["issues"].append(
                f"Range violations found in {len(range_violations)} columns"
            )

        results["details"] = {
            "column_ranges": self.column_ranges,
            "range_violations": range_violations,
        }

        return results


class UniquenessValidationRule(ValidationRule):
    """Uniqueness validation rule."""

    def __init__(self, rule_id: str, unique_columns: List[str]):
        super().__init__(
            rule_id,
            "Uniqueness Validation",
            "Validates uniqueness of specified columns",
        )
        self.unique_columns = unique_columns

    def validate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Validate column uniqueness."""
        results = {
            "rule_id": self.rule_id,
            "rule_name": self.name,
            "passed": True,
            "issues": [],
            "details": {},
        }

        uniqueness_issues = {}

        for column in self.unique_columns:
            if column not in data.columns:
                results["issues"].append(f"Column {column} not found")
                continue

            total_count = len(data)
            unique_count = data[column].nunique()
            duplicate_count = total_count - unique_count

            uniqueness_score = unique_count / total_count

            uniqueness_issues[column] = {
                "total_count": total_count,
                "unique_count": unique_count,
                "duplicate_count": duplicate_count,
                "uniqueness_score": uniqueness_score,
                "duplicate_percentage": duplicate_count / total_count * 100,
            }

            if duplicate_count > 0:
                results["passed"] = False

        if any(issue["duplicate_count"] > 0 for issue in uniqueness_issues.values()):
            results["issues"].append(
                f"Duplicates found in {len([c for c, i in uniqueness_issues.items() if i['duplicate_count'] > 0])} columns"
            )

        results["details"] = {
            "unique_columns": self.unique_columns,
            "uniqueness_issues": uniqueness_issues,
        }

        return results


class NullValidationRule(ValidationRule):
    """Null value validation rule."""

    def __init__(self, rule_id: str, null_thresholds: Dict[str, float]):
        super().__init__(rule_id, "Null Validation", "Validates null value thresholds")
        self.null_thresholds = null_thresholds

    def validate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Validate null value thresholds."""
        results = {
            "rule_id": self.rule_id,
            "rule_name": self.name,
            "passed": True,
            "issues": [],
            "details": {},
        }

        null_issues = {}

        for column, threshold in self.null_thresholds.items():
            if column not in data.columns:
                results["issues"].append(f"Column {column} not found")
                continue

            null_count = data[column].isnull().sum()
            total_count = len(data)
            null_percentage = null_count / total_count * 100

            null_issues[column] = {
                "null_count": null_count,
                "total_count": total_count,
                "null_percentage": null_percentage,
                "threshold": threshold,
            }

            if null_percentage > threshold:
                results["passed"] = False
                results["issues"].append(
                    f"Column {column} has {null_percentage:.1f}% null values (threshold: {threshold}%)"
                )

        results["details"] = {
            "null_thresholds": self.null_thresholds,
            "null_issues": null_issues,
        }

        return results


class DataValidationPipeline:
    """Production-ready data validation pipeline system."""

    def __init__(self):
        self.pipelines: Dict[str, ValidationPipelineConfig] = {}
        self.executions: Dict[str, PipelineExecution] = {}
        self.validation_rules: Dict[str, ValidationRule] = {}
        self.active_executions: Set[str] = set()

        # Register built-in validation rules
        self._register_builtin_rules()

    def _register_builtin_rules(self):
        """Register built-in validation rules."""
        # These would be configured based on specific requirements
        pass

    def create_pipeline(self, config: ValidationPipelineConfig) -> str:
        """Create a new validation pipeline."""
        self.pipelines[config.pipeline_id] = config
        logger.info(f"Created validation pipeline: {config.pipeline_id}")
        return config.pipeline_id

    def add_validation_rule(self, rule: ValidationRule) -> str:
        """Add a validation rule to the system."""
        self.validation_rules[rule.rule_id] = rule
        logger.info(f"Added validation rule: {rule.rule_id}")
        return rule.rule_id

    def execute_pipeline(
        self, pipeline_id: str, data: pd.DataFrame
    ) -> PipelineExecution:
        """Execute a validation pipeline."""
        if pipeline_id not in self.pipelines:
            raise ValueError(f"Pipeline {pipeline_id} not found")

        config = self.pipelines[pipeline_id]

        # Create execution record
        execution = PipelineExecution(
            pipeline_id=pipeline_id,
            status=PipelineStatus.RUNNING,
            start_time=datetime.now(),
        )

        self.executions[execution.execution_id] = execution
        self.active_executions.add(execution.execution_id)

        try:
            # Execute validation rules
            validation_results = []

            for rule_id in config.validation_rules:
                if rule_id not in self.validation_rules:
                    continue

                rule = self.validation_rules[rule_id]
                if not rule.enabled:
                    continue

                result = rule.validate(data)
                validation_results.append(result)

            # Calculate summary metrics
            total_rules = len(validation_results)
            passed_rules = sum(1 for r in validation_results if r["passed"])
            failed_rules = total_rules - passed_rules

            # Update execution
            execution.status = PipelineStatus.COMPLETED
            execution.end_time = datetime.now()
            execution.duration_seconds = (
                execution.end_time - execution.start_time
            ).total_seconds()
            execution.validation_results = validation_results
            execution.input_data_summary = {
                "rows": len(data),
                "columns": list(data.columns),
                "memory_usage": data.memory_usage(deep=True).sum(),
                "data_types": data.dtypes.to_dict(),
            }
            execution.metrics = {
                "total_rules": total_rules,
                "passed_rules": passed_rules,
                "failed_rules": failed_rules,
                "success_rate": passed_rules / total_rules if total_rules > 0 else 0.0,
            }

            logger.info(f"Pipeline execution completed: {execution.execution_id}")

        except Exception as e:
            execution.status = PipelineStatus.FAILED
            execution.end_time = datetime.now()
            execution.duration_seconds = (
                execution.end_time - execution.start_time
            ).total_seconds()
            execution.error_message = str(e)

            logger.error(
                f"Pipeline execution failed: {execution.execution_id} - {str(e)}"
            )

        finally:
            self.active_executions.discard(execution.execution_id)

        return execution

    def get_execution_status(self, execution_id: str) -> Optional[PipelineExecution]:
        """Get execution status."""
        return self.executions.get(execution_id)

    def get_pipeline_executions(
        self, pipeline_id: str, limit: int = 10
    ) -> List[PipelineExecution]:
        """Get recent executions for a pipeline."""
        executions = [
            e for e in self.executions.values() if e.pipeline_id == pipeline_id
        ]
        executions.sort(key=lambda x: x.start_time or datetime.min, reverse=True)
        return executions[:limit]

    def get_pipeline_summary(self, pipeline_id: str) -> Dict[str, Any]:
        """Get pipeline summary."""
        if pipeline_id not in self.pipelines:
            raise ValueError(f"Pipeline {pipeline_id} not found")

        config = self.pipelines[pipeline_id]
        executions = self.get_pipeline_executions(pipeline_id, 100)

        # Calculate statistics
        total_executions = len(executions)
        successful_executions = sum(
            1 for e in executions if e.status == PipelineStatus.COMPLETED
        )
        failed_executions = sum(
            1 for e in executions if e.status == PipelineStatus.FAILED
        )

        avg_duration = (
            np.mean([e.duration_seconds for e in executions if e.duration_seconds > 0])
            if executions
            else 0.0
        )

        return {
            "pipeline_id": pipeline_id,
            "name": config.name,
            "description": config.description,
            "validation_level": config.validation_level.value,
            "trigger_type": config.trigger_type.value,
            "enabled": config.enabled,
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "success_rate": (
                successful_executions / total_executions
                if total_executions > 0
                else 0.0
            ),
            "average_duration": avg_duration,
            "last_execution": (
                executions[0].start_time.isoformat() if executions else None
            ),
            "validation_rules": config.validation_rules,
        }


# Example usage
async def demonstrate_data_validation_pipelines():
    """Demonstrate data validation pipelines system."""
    print(
        "Demonstrating S.W.A.R.M. Phase 2 Advanced MLOps - Data Validation Pipelines..."
    )

    # Create sample data
    np.random.seed(42)
    sample_data = pd.DataFrame(
        {
            "customer_id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1],  # Duplicate
            "age": [25, 30, None, 45, 22, 35, 28, 33, 40, 27, 25],  # Missing value
            "income": [
                50000,
                60000,
                70000,
                80000,
                45000,
                65000,
                55000,
                75000,
                85000,
                48000,
                50000,
            ],
            "email": [
                "a@b.com",
                "invalid-email",
                "c@d.com",
                "e@f.com",
                "g@h.com",
                "i@j.com",
                "k@l.com",
                "m@n.com",
                "o@p.com",
                "q@r.com",
                "a@b.com",
            ],
            "registration_date": pd.date_range("2020-01-01", periods=10).tolist()
            + [pd.Timestamp("2020-01-01")],
        }
    )

    print(f"Sample data shape: {sample_data.shape}")
    print(f"Sample data columns: {list(sample_data.columns)}")

    # Create validation pipeline
    pipeline = DataValidationPipeline()

    # Create validation rules
    schema_rule = SchemaValidationRule(
        "schema_check",
        {
            "customer_id": "int64",
            "age": "float64",
            "income": "float64",
            "email": "object",
            "registration_date": "datetime64",
        },
    )

    range_rule = RangeValidationRule(
        "range_check", {"age": (18, 100), "income": (0, 200000)}
    )

    uniqueness_rule = UniquenessValidationRule(
        "uniqueness_check", ["customer_id", "email"]
    )

    null_rule = NullValidationRule(
        "null_check", {"customer_id": 0.0, "age": 10.0, "income": 5.0, "email": 5.0}
    )

    # Add rules to pipeline
    pipeline.add_validation_rule(schema_rule)
    pipeline.add_validation_rule(range_rule)
    pipeline.add_validation_rule(uniqueness_rule)
    pipeline.add_validation_rule(null_rule)

    # Create pipeline configuration
    config = ValidationPipelineConfig(
        name="Customer Data Validation",
        description="Validates customer data for quality and consistency",
        validation_level=ValidationLevel.COMPREHENSIVE,
        trigger_type=PipelineTrigger.MANUAL,
        validation_rules=[
            "schema_check",
            "range_check",
            "uniqueness_check",
            "null_check",
        ],
    )

    pipeline_id = pipeline.create_pipeline(config)
    print(f"\nCreated validation pipeline: {pipeline_id}")

    # Execute pipeline
    print("\nExecuting validation pipeline...")
    execution = pipeline.execute_pipeline(pipeline_id, sample_data)

    # Display results
    print(f"\nExecution Results:")
    print(f"  Status: {execution.status.value}")
    print(f"  Duration: {execution.duration_seconds:.3f} seconds")
    print(f"  Total Rules: {execution.metrics['total_rules']}")
    print(f"  Passed Rules: {execution.metrics['passed_rules']}")
    print(f"  Failed Rules: {execution.metrics['failed_rules']}")
    print(f"  Success Rate: {execution.metrics['success_rate']:.1%}")

    print(f"\nValidation Results:")
    for result in execution.validation_results:
        print(f"  {result['rule_name']}: {'PASSED' if result['passed'] else 'FAILED'}")
        if result["issues"]:
            for issue in result["issues"]:
                print(f"    - {issue}")

    # Get pipeline summary
    summary = pipeline.get_pipeline_summary(pipeline_id)
    print(f"\nPipeline Summary:")
    print(f"  Name: {summary['name']}")
    print(f"  Total Executions: {summary['total_executions']}")
    print(f"  Success Rate: {summary['success_rate']:.1%}")
    print(f"  Average Duration: {summary['average_duration']:.3f} seconds")

    print("\nData Validation Pipelines demonstration complete!")


if __name__ == "__main__":
    asyncio.run(demonstrate_data_validation_pipelines())
