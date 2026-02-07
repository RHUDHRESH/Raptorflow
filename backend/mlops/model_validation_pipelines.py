"""
S.W.A.R.M. Phase 2: Model Validation Pipelines
Production-ready model validation and quality assurance system
"""

import asyncio
import json
import logging
import os
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import yaml

# Import existing components
from automated_model_testing import (
    TestConfig,
    TestResult,
    TestRunner,
    TestStatus,
    TestType,
)

logger = logging.getLogger("raptorflow.model_validation")


class ValidationLevel(Enum):
    """Validation levels."""

    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    PRODUCTION = "production"


class ValidationStatus(Enum):
    """Validation status."""

    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    CANCELLED = "cancelled"


class ValidationTrigger(Enum):
    """Validation triggers."""

    MANUAL = "manual"
    PRE_DEPLOYMENT = "pre_deployment"
    POST_DEPLOYMENT = "post_deployment"
    SCHEDULED = "scheduled"
    EVENT_DRIVEN = "event_driven"


@dataclass
class ValidationRule:
    """Individual validation rule."""

    rule_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    rule_type: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    threshold: Optional[float] = None
    severity: str = "medium"
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "rule_type": self.rule_type,
            "parameters": self.parameters,
            "threshold": self.threshold,
            "severity": self.severity,
            "enabled": self.enabled,
        }


@dataclass
class ValidationConfig:
    """Validation pipeline configuration."""

    validation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    model_name: str = ""
    model_version: str = ""
    validation_level: ValidationLevel = ValidationLevel.STANDARD
    trigger: ValidationTrigger = ValidationTrigger.MANUAL
    rules: List[ValidationRule] = field(default_factory=list)
    parallel_execution: bool = True
    timeout_minutes: int = 60
    fail_fast: bool = False
    notification_settings: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "validation_id": self.validation_id,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "validation_level": self.validation_level.value,
            "trigger": self.trigger.value,
            "rules": [rule.to_dict() for rule in self.rules],
            "parallel_execution": self.parallel_execution,
            "timeout_minutes": self.timeout_minutes,
            "fail_fast": self.fail_fast,
            "notification_settings": self.notification_settings,
        }


@dataclass
class ValidationResult:
    """Validation execution result."""

    validation_id: str
    model_name: str
    model_version: str
    status: ValidationStatus
    start_time: datetime
    end_time: Optional[datetime]
    duration: float
    total_rules: int
    passed_rules: int
    failed_rules: int
    warning_rules: int
    skipped_rules: int
    rule_results: List[Dict[str, Any]]
    overall_score: float
    recommendations: List[str] = field(default_factory=list)
    artifacts: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "validation_id": self.validation_id,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "status": self.status.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "total_rules": self.total_rules,
            "passed_rules": self.passed_rules,
            "failed_rules": self.failed_rules,
            "warning_rules": self.warning_rules,
            "skipped_rules": self.skipped_rules,
            "rule_results": self.rule_results,
            "overall_score": self.overall_score,
            "recommendations": self.recommendations,
            "artifacts": self.artifacts,
        }


class ValidationRuleBase(ABC):
    """Abstract base class for validation rules."""

    def __init__(self, rule: ValidationRule):
        self.rule = rule

    @abstractmethod
    async def validate(
        self, model_info: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute validation rule."""
        pass

    @abstractmethod
    def get_rule_type(self) -> str:
        """Get rule type."""
        pass


class AccuracyValidationRule(ValidationRuleBase):
    """Accuracy validation rule."""

    def get_rule_type(self) -> str:
        return "accuracy"

    async def validate(
        self, model_info: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate model accuracy."""
        try:
            # Get accuracy metrics
            accuracy_metrics = model_info.get("accuracy_metrics", {})
            threshold = self.rule.threshold or 0.8

            # Check different accuracy metrics
            results = {}

            if "overall_accuracy" in accuracy_metrics:
                overall_acc = accuracy_metrics["overall_accuracy"]
                results["overall_accuracy"] = {
                    "value": overall_acc,
                    "threshold": threshold,
                    "passed": overall_acc >= threshold,
                }

            if "precision" in accuracy_metrics:
                precision = accuracy_metrics["precision"]
                results["precision"] = {
                    "value": precision,
                    "threshold": threshold,
                    "passed": precision >= threshold,
                }

            if "recall" in accuracy_metrics:
                recall = accuracy_metrics["recall"]
                results["recall"] = {
                    "value": recall,
                    "threshold": threshold,
                    "passed": recall >= threshold,
                }

            if "f1_score" in accuracy_metrics:
                f1 = accuracy_metrics["f1_score"]
                results["f1_score"] = {
                    "value": f1,
                    "threshold": threshold,
                    "passed": f1 >= threshold,
                }

            # Overall result
            all_passed = all(result["passed"] for result in results.values())

            return {
                "rule_name": self.rule.name,
                "rule_type": self.get_rule_type(),
                "passed": all_passed,
                "details": results,
                "message": f"Accuracy validation {'passed' if all_passed else 'failed'}",
            }

        except Exception as e:
            return {
                "rule_name": self.rule.name,
                "rule_type": self.get_rule_type(),
                "passed": False,
                "error": str(e),
                "message": f"Accuracy validation error: {str(e)}",
            }


class PerformanceValidationRule(ValidationRuleBase):
    """Performance validation rule."""

    def get_rule_type(self) -> str:
        return "performance"

    async def validate(
        self, model_info: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate model performance."""
        try:
            performance_metrics = model_info.get("performance_metrics", {})

            # Latency threshold (ms)
            latency_threshold = self.rule.parameters.get("latency_threshold", 1000)

            # Throughput threshold (requests/second)
            throughput_threshold = self.rule.parameters.get("throughput_threshold", 100)

            # Memory usage threshold (MB)
            memory_threshold = self.rule.parameters.get("memory_threshold", 1024)

            results = {}

            if "inference_latency" in performance_metrics:
                latency = performance_metrics["inference_latency"]
                results["latency"] = {
                    "value": latency,
                    "threshold": latency_threshold,
                    "passed": latency <= latency_threshold,
                    "unit": "ms",
                }

            if "throughput" in performance_metrics:
                throughput = performance_metrics["throughput"]
                results["throughput"] = {
                    "value": throughput,
                    "threshold": throughput_threshold,
                    "passed": throughput >= throughput_threshold,
                    "unit": "requests/second",
                }

            if "memory_usage" in performance_metrics:
                memory = performance_metrics["memory_usage"]
                results["memory"] = {
                    "value": memory,
                    "threshold": memory_threshold,
                    "passed": memory <= memory_threshold,
                    "unit": "MB",
                }

            # Overall result
            all_passed = all(result["passed"] for result in results.values())

            return {
                "rule_name": self.rule.name,
                "rule_type": self.get_rule_type(),
                "passed": all_passed,
                "details": results,
                "message": f"Performance validation {'passed' if all_passed else 'failed'}",
            }

        except Exception as e:
            return {
                "rule_name": self.rule.name,
                "rule_type": self.get_rule_type(),
                "passed": False,
                "error": str(e),
                "message": f"Performance validation error: {str(e)}",
            }


class DataQualityValidationRule(ValidationRuleBase):
    """Data quality validation rule."""

    def get_rule_type(self) -> str:
        return "data_quality"

    async def validate(
        self, model_info: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate data quality."""
        try:
            data_quality = model_info.get("data_quality_metrics", {})

            # Missing data threshold
            missing_threshold = self.rule.parameters.get("missing_threshold", 0.1)

            # Duplicate data threshold
            duplicate_threshold = self.rule.parameters.get("duplicate_threshold", 0.05)

            # Outlier threshold
            outlier_threshold = self.rule.parameters.get("outlier_threshold", 0.05)

            results = {}

            if "missing_data_ratio" in data_quality:
                missing_ratio = data_quality["missing_data_ratio"]
                results["missing_data"] = {
                    "value": missing_ratio,
                    "threshold": missing_threshold,
                    "passed": missing_ratio <= missing_threshold,
                }

            if "duplicate_ratio" in data_quality:
                duplicate_ratio = data_quality["duplicate_ratio"]
                results["duplicate_data"] = {
                    "value": duplicate_ratio,
                    "threshold": duplicate_threshold,
                    "passed": duplicate_ratio <= duplicate_threshold,
                }

            if "outlier_ratio" in data_quality:
                outlier_ratio = data_quality["outlier_ratio"]
                results["outliers"] = {
                    "value": outlier_ratio,
                    "threshold": outlier_threshold,
                    "passed": outlier_ratio <= outlier_threshold,
                }

            # Overall result
            all_passed = all(result["passed"] for result in results.values())

            return {
                "rule_name": self.rule.name,
                "rule_type": self.get_rule_type(),
                "passed": all_passed,
                "details": results,
                "message": f"Data quality validation {'passed' if all_passed else 'failed'}",
            }

        except Exception as e:
            return {
                "rule_name": self.rule.name,
                "rule_type": self.get_rule_type(),
                "passed": False,
                "error": str(e),
                "message": f"Data quality validation error: {str(e)}",
            }


class FairnessValidationRule(ValidationRuleBase):
    """Fairness validation rule."""

    def get_rule_type(self) -> str:
        return "fairness"

    async def validate(
        self, model_info: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate model fairness."""
        try:
            fairness_metrics = model_info.get("fairness_metrics", {})

            # Fairness threshold
            fairness_threshold = self.rule.parameters.get("fairness_threshold", 0.8)

            results = {}

            # Demographic parity
            if "demographic_parity" in fairness_metrics:
                dem_parity = fairness_metrics["demographic_parity"]
                results["demographic_parity"] = {
                    "value": dem_parity,
                    "threshold": fairness_threshold,
                    "passed": dem_parity >= fairness_threshold,
                }

            # Equal opportunity
            if "equal_opportunity" in fairness_metrics:
                eq_opp = fairness_metrics["equal_opportunity"]
                results["equal_opportunity"] = {
                    "value": eq_opp,
                    "threshold": fairness_threshold,
                    "passed": eq_opp >= fairness_threshold,
                }

            # Equalized odds
            if "equalized_odds" in fairness_metrics:
                eq_odds = fairness_metrics["equalized_odds"]
                results["equalized_odds"] = {
                    "value": eq_odds,
                    "threshold": fairness_threshold,
                    "passed": eq_odds >= fairness_threshold,
                }

            # Overall result
            all_passed = all(result["passed"] for result in results.values())

            return {
                "rule_name": self.rule.name,
                "rule_type": self.get_rule_type(),
                "passed": all_passed,
                "details": results,
                "message": f"Fairness validation {'passed' if all_passed else 'failed'}",
            }

        except Exception as e:
            return {
                "rule_name": self.rule.name,
                "rule_type": self.get_rule_type(),
                "passed": False,
                "error": str(e),
                "message": f"Fairness validation error: {str(e)}",
            }


class SecurityValidationRule(ValidationRuleBase):
    """Security validation rule."""

    def get_rule_type(self) -> str:
        return "security"

    async def validate(
        self, model_info: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate model security."""
        try:
            security_metrics = model_info.get("security_metrics", {})

            results = {}

            # Adversarial robustness
            if "adversarial_robustness" in security_metrics:
                robustness = security_metrics["adversarial_robustness"]
                threshold = self.rule.parameters.get("robustness_threshold", 0.7)
                results["adversarial_robustness"] = {
                    "value": robustness,
                    "threshold": threshold,
                    "passed": robustness >= threshold,
                }

            # Data privacy
            if "data_privacy_score" in security_metrics:
                privacy = security_metrics["data_privacy_score"]
                threshold = self.rule.parameters.get("privacy_threshold", 0.8)
                results["data_privacy"] = {
                    "value": privacy,
                    "threshold": threshold,
                    "passed": privacy >= threshold,
                }

            # Model encryption
            if "model_encrypted" in security_metrics:
                encrypted = security_metrics["model_encrypted"]
                results["model_encryption"] = {
                    "value": encrypted,
                    "threshold": True,
                    "passed": encrypted,
                }

            # Overall result
            all_passed = all(result["passed"] for result in results.values())

            return {
                "rule_name": self.rule.name,
                "rule_type": self.get_rule_type(),
                "passed": all_passed,
                "details": results,
                "message": f"Security validation {'passed' if all_passed else 'failed'}",
            }

        except Exception as e:
            return {
                "rule_name": self.rule.name,
                "rule_type": self.get_rule_type(),
                "passed": False,
                "error": str(e),
                "message": f"Security validation error: {str(e)}",
            }


class ModelValidationPipeline:
    """Main model validation pipeline system."""

    def __init__(self):
        self.validation_history: List[ValidationResult] = []
        self.rule_registry: Dict[str, type] = {
            "accuracy": AccuracyValidationRule,
            "performance": PerformanceValidationRule,
            "data_quality": DataQualityValidationRule,
            "fairness": FairnessValidationRule,
            "security": SecurityValidationRule,
        }
        self.test_runner = TestRunner()

    def create_validation_config(
        self, model_name: str, model_version: str, validation_level: ValidationLevel
    ) -> ValidationConfig:
        """Create validation configuration based on level."""
        rules = self._get_rules_for_level(validation_level)

        return ValidationConfig(
            model_name=model_name,
            model_version=model_version,
            validation_level=validation_level,
            rules=rules,
        )

    def _get_rules_for_level(self, level: ValidationLevel) -> List[ValidationRule]:
        """Get validation rules for validation level."""
        rules = []

        if level in [
            ValidationLevel.BASIC,
            ValidationLevel.STANDARD,
            ValidationLevel.COMPREHENSIVE,
            ValidationLevel.PRODUCTION,
        ]:
            # Basic accuracy rule
            rules.append(
                ValidationRule(
                    name="Basic Accuracy Check",
                    description="Validate model accuracy meets minimum threshold",
                    rule_type="accuracy",
                    threshold=0.7,
                    severity="high",
                )
            )

        if level in [
            ValidationLevel.STANDARD,
            ValidationLevel.COMPREHENSIVE,
            ValidationLevel.PRODUCTION,
        ]:
            # Performance rule
            rules.append(
                ValidationRule(
                    name="Performance Check",
                    description="Validate model performance meets requirements",
                    rule_type="performance",
                    parameters={
                        "latency_threshold": 1000,
                        "throughput_threshold": 100,
                        "memory_threshold": 1024,
                    },
                    severity="high",
                )
            )

            # Data quality rule
            rules.append(
                ValidationRule(
                    name="Data Quality Check",
                    description="Validate training data quality",
                    rule_type="data_quality",
                    parameters={
                        "missing_threshold": 0.1,
                        "duplicate_threshold": 0.05,
                        "outlier_threshold": 0.05,
                    },
                    severity="medium",
                )
            )

        if level in [ValidationLevel.COMPREHENSIVE, ValidationLevel.PRODUCTION]:
            # Fairness rule
            rules.append(
                ValidationRule(
                    name="Fairness Check",
                    description="Validate model fairness across demographics",
                    rule_type="fairness",
                    parameters={"fairness_threshold": 0.8},
                    severity="medium",
                )
            )

        if level == ValidationLevel.PRODUCTION:
            # Security rule
            rules.append(
                ValidationRule(
                    name="Security Check",
                    description="Validate model security and privacy",
                    rule_type="security",
                    parameters={"robustness_threshold": 0.7, "privacy_threshold": 0.8},
                    severity="high",
                )
            )

            # Strict accuracy rule
            rules.append(
                ValidationRule(
                    name="Production Accuracy Check",
                    description="Strict accuracy validation for production",
                    rule_type="accuracy",
                    threshold=0.85,
                    severity="critical",
                )
            )

        return rules

    async def execute_validation(
        self, config: ValidationConfig, model_info: Dict[str, Any]
    ) -> ValidationResult:
        """Execute validation pipeline."""
        start_time = datetime.now()

        # Create rule instances
        rule_instances = []
        for rule in config.rules:
            if not rule.enabled:
                continue

            rule_class = self.rule_registry.get(rule.rule_type)
            if rule_class:
                rule_instances.append(rule_class(rule))

        # Execute validation rules
        if config.parallel_execution:
            rule_results = await self._execute_rules_parallel(
                rule_instances, model_info
            )
        else:
            rule_results = await self._execute_rules_sequential(
                rule_instances, model_info, config.fail_fast
            )

        # Calculate results
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        total_rules = len(rule_results)
        passed_rules = len([r for r in rule_results if r["passed"]])
        failed_rules = len(
            [r for r in rule_results if not r["passed"] and "error" not in r]
        )
        warning_rules = len(
            [r for r in rule_results if not r["passed"] and "error" in r]
        )
        skipped_rules = config.rules.count(lambda r: not r.enabled)

        # Overall status
        if failed_rules > 0:
            overall_status = ValidationStatus.FAILED
        elif warning_rules > 0:
            overall_status = ValidationStatus.WARNING
        else:
            overall_status = ValidationStatus.PASSED

        # Calculate score
        score_weights = {
            "accuracy": 0.3,
            "performance": 0.25,
            "data_quality": 0.2,
            "fairness": 0.15,
            "security": 0.1,
        }

        overall_score = 0.0
        total_weight = 0.0

        for result in rule_results:
            rule_type = result.get("rule_type", "")
            weight = score_weights.get(rule_type, 0.1)
            total_weight += weight

            if result["passed"]:
                overall_score += weight

        if total_weight > 0:
            overall_score /= total_weight

        # Generate recommendations
        recommendations = self._generate_recommendations(rule_results)

        # Generate artifacts
        artifacts = self._generate_artifacts(config, rule_results)

        result = ValidationResult(
            validation_id=config.validation_id,
            model_name=config.model_name,
            model_version=config.model_version,
            status=overall_status,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            total_rules=total_rules,
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            warning_rules=warning_rules,
            skipped_rules=skipped_rules,
            rule_results=rule_results,
            overall_score=overall_score,
            recommendations=recommendations,
            artifacts=artifacts,
        )

        self.validation_history.append(result)
        return result

    async def _execute_rules_parallel(
        self, rule_instances: List[ValidationRuleBase], model_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute validation rules in parallel."""
        tasks = []
        for rule_instance in rule_instances:
            task = asyncio.create_task(rule_instance.validate(model_info, {}))
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(
                    {
                        "rule_name": rule_instances[i].rule.name,
                        "rule_type": rule_instances[i].get_rule_type(),
                        "passed": False,
                        "error": str(result),
                        "message": f"Rule execution error: {str(result)}",
                    }
                )
            else:
                processed_results.append(result)

        return processed_results

    async def _execute_rules_sequential(
        self,
        rule_instances: List[ValidationRuleBase],
        model_info: Dict[str, Any],
        fail_fast: bool,
    ) -> List[Dict[str, Any]]:
        """Execute validation rules sequentially."""
        results = []

        for rule_instance in rule_instances:
            try:
                result = await rule_instance.validate(model_info, {})
                results.append(result)

                # Fail fast if enabled and rule failed
                if fail_fast and not result["passed"]:
                    break

            except Exception as e:
                results.append(
                    {
                        "rule_name": rule_instance.rule.name,
                        "rule_type": rule_instance.get_rule_type(),
                        "passed": False,
                        "error": str(e),
                        "message": f"Rule execution error: {str(e)}",
                    }
                )

                if fail_fast:
                    break

        return results

    def _generate_recommendations(
        self, rule_results: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []

        for result in rule_results:
            if not result["passed"]:
                rule_type = result.get("rule_type", "")

                if rule_type == "accuracy":
                    recommendations.append(
                        "Consider retraining with more data or adjusting model architecture"
                    )
                elif rule_type == "performance":
                    recommendations.append(
                        "Optimize model through quantization or pruning"
                    )
                elif rule_type == "data_quality":
                    recommendations.append("Improve data preprocessing and cleaning")
                elif rule_type == "fairness":
                    recommendations.append("Apply bias mitigation techniques")
                elif rule_type == "security":
                    recommendations.append(
                        "Implement adversarial training and data encryption"
                    )

        return recommendations

    def _generate_artifacts(
        self, config: ValidationConfig, rule_results: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate validation artifacts."""
        artifacts = []

        # Validation report
        report_path = f"validation_reports/{config.validation_id}_report.json"
        artifacts.append(report_path)

        # Detailed metrics
        metrics_path = f"validation_reports/{config.validation_id}_metrics.json"
        artifacts.append(metrics_path)

        return artifacts

    def get_validation_history(
        self, model_name: Optional[str] = None, limit: Optional[int] = None
    ) -> List[ValidationResult]:
        """Get validation history."""
        history = self.validation_history

        if model_name:
            history = [v for v in history if v.model_name == model_name]

        if limit:
            history = history[-limit:]

        return history

    def get_validation_metrics(self) -> Dict[str, Any]:
        """Get validation metrics."""
        if not self.validation_history:
            return {
                "total_validations": 0,
                "average_score": 0.0,
                "pass_rate": 0.0,
                "average_duration": 0.0,
            }

        total_validations = len(self.validation_history)
        average_score = (
            sum(v.overall_score for v in self.validation_history) / total_validations
        )
        passed_validations = len(
            [v for v in self.validation_history if v.status == ValidationStatus.PASSED]
        )
        pass_rate = passed_validations / total_validations
        average_duration = (
            sum(v.duration for v in self.validation_history) / total_validations
        )

        return {
            "total_validations": total_validations,
            "average_score": average_score,
            "pass_rate": pass_rate,
            "average_duration": average_duration,
        }


# Validation templates
class ValidationTemplates:
    """Predefined validation templates."""

    @staticmethod
    def get_production_validation_config(
        model_name: str, model_version: str
    ) -> ValidationConfig:
        """Get production validation configuration."""
        validator = ModelValidationPipeline()
        return validator.create_validation_config(
            model_name=model_name,
            model_version=model_version,
            validation_level=ValidationLevel.PRODUCTION,
        )

    @staticmethod
    def get_development_validation_config(
        model_name: str, model_version: str
    ) -> ValidationConfig:
        """Get development validation configuration."""
        validator = ModelValidationPipeline()
        return validator.create_validation_config(
            model_name=model_name,
            model_version=model_version,
            validation_level=ValidationLevel.STANDARD,
        )

    @staticmethod
    def get_quick_validation_config(
        model_name: str, model_version: str
    ) -> ValidationConfig:
        """Get quick validation configuration."""
        validator = ModelValidationPipeline()
        return validator.create_validation_config(
            model_name=model_name,
            model_version=model_version,
            validation_level=ValidationLevel.BASIC,
        )


# Example usage
async def example_usage():
    """Example usage of model validation pipeline."""
    # Create validation pipeline
    validator = ModelValidationPipeline()

    # Create validation configuration
    config = ValidationTemplates.get_production_validation_config(
        model_name="image-classifier", model_version="1.0.0"
    )

    # Mock model information
    model_info = {
        "accuracy_metrics": {
            "overall_accuracy": 0.87,
            "precision": 0.85,
            "recall": 0.89,
            "f1_score": 0.87,
        },
        "performance_metrics": {
            "inference_latency": 850,
            "throughput": 120,
            "memory_usage": 512,
        },
        "data_quality_metrics": {
            "missing_data_ratio": 0.02,
            "duplicate_ratio": 0.01,
            "outlier_ratio": 0.03,
        },
        "fairness_metrics": {
            "demographic_parity": 0.82,
            "equal_opportunity": 0.85,
            "equalized_odds": 0.83,
        },
        "security_metrics": {
            "adversarial_robustness": 0.75,
            "data_privacy_score": 0.88,
            "model_encrypted": True,
        },
    }

    # Execute validation
    result = await validator.execute_validation(config, model_info)

    print(f"Validation: {result.validation_id}")
    print(f"Status: {result.status.value}")
    print(f"Overall Score: {result.overall_score:.2f}")
    print(f"Duration: {result.duration:.2f}s")
    print(f"Total Rules: {result.total_rules}")
    print(f"Passed: {result.passed_rules}")
    print(f"Failed: {result.failed_rules}")
    print(f"Warnings: {result.warning_rules}")

    # Print rule results
    for rule_result in result.rule_results:
        print(
            f"  {rule_result['rule_name']}: {rule_result['passed']} - {rule_result['message']}"
        )

    # Print recommendations
    if result.recommendations:
        print("Recommendations:")
        for rec in result.recommendations:
            print(f"  - {rec}")

    # Get metrics
    metrics = validator.get_validation_metrics()
    print(f"Validation metrics: {metrics}")


if __name__ == "__main__":
    asyncio.run(example_usage())
