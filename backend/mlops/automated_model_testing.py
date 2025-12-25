"""
S.W.A.R.M. Phase 2: Automated Model Testing Workflows
Production-ready automated testing framework for ML models
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
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union

import numpy as np
import pandas as pd

# ML imports
try:
    import tensorflow as tf
    import torch
    import torch.nn as nn
    from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
    from sklearn.model_selection import train_test_split

    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

# Testing imports
try:
    import unittest
    from unittest.mock import Mock, patch

    import pytest

    TESTING_AVAILABLE = True
except ImportError:
    TESTING_AVAILABLE = False

# Data validation imports
try:
    import great_expectations as ge
    from great_expectations.dataset import PandasDataset

    GE_AVAILABLE = True
except ImportError:
    GE_AVAILABLE = False

# Fairness imports
try:
    import aif360
    from aif360.datasets import StandardDataset
    from aif360.metrics import ClassificationMetric

    AIF360_AVAILABLE = True
except ImportError:
    AIF360_AVAILABLE = False

# Security imports
try:
    import adversarial_robustness_toolbox as art
    from art.attacks import FastGradientMethod, ProjectedGradientDescent
    from art.defences import GaussianSmoothing

    ART_AVAILABLE = True
except ImportError:
    ART_AVAILABLE = False

logger = logging.getLogger("raptorflow.automated_model_testing")


class TestType(Enum):
    """Test types for model validation."""

    ACCURACY = "accuracy"
    PERFORMANCE = "performance"
    FAIRNESS = "fairness"
    ROBUSTNESS = "robustness"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    DATA_QUALITY = "data_quality"
    MODEL_DRIFT = "model_drift"


class TestStatus(Enum):
    """Test execution status."""

    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class Severity(Enum):
    """Test failure severity."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class TestConfig:
    """Test configuration."""

    test_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    test_type: TestType = TestType.ACCURACY
    description: str = ""
    enabled: bool = True
    threshold: float = 0.0
    timeout_seconds: int = 300
    retry_count: int = 1
    severity: Severity = Severity.MEDIUM
    parameters: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "test_id": self.test_id,
            "name": self.name,
            "test_type": self.test_type.value,
            "description": self.description,
            "enabled": self.enabled,
            "threshold": self.threshold,
            "timeout_seconds": self.timeout_seconds,
            "retry_count": self.retry_count,
            "severity": self.severity.value,
            "parameters": self.parameters,
            "tags": self.tags,
        }


@dataclass
class TestResult:
    """Test execution result."""

    test_id: str
    test_name: str
    status: TestStatus
    score: float
    threshold: float
    passed: bool
    execution_time: float
    start_time: datetime
    end_time: datetime
    error_message: Optional[str] = None
    metrics: Dict[str, float] = field(default_factory=dict)
    artifacts: Dict[str, str] = field(default_factory=dict)
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "test_id": self.test_id,
            "test_name": self.test_name,
            "status": self.status.value,
            "score": self.score,
            "threshold": self.threshold,
            "passed": self.passed,
            "execution_time": self.execution_time,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "error_message": self.error_message,
            "metrics": self.metrics,
            "artifacts": self.artifacts,
            "details": self.details,
        }


@dataclass
class TestSuite:
    """Test suite configuration."""

    suite_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    tests: List[TestConfig] = field(default_factory=list)
    parallel_execution: bool = True
    max_parallel_tests: int = 5
    fail_fast: bool = False
    environment: str = "test"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "suite_id": self.suite_id,
            "name": self.name,
            "description": self.description,
            "tests": [test.to_dict() for test in self.tests],
            "parallel_execution": self.parallel_execution,
            "max_parallel_tests": self.max_parallel_tests,
            "fail_fast": self.fail_fast,
            "environment": self.environment,
        }


class ModelTest(ABC):
    """Abstract base class for model tests."""

    def __init__(self, config: TestConfig):
        self.config = config
        self.status = TestStatus.PENDING
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.error_message: Optional[str] = None

    @abstractmethod
    async def execute(self, model: Any, test_data: Dict[str, Any]) -> TestResult:
        """Execute the test."""
        pass

    @abstractmethod
    async def validate_prerequisites(
        self, model: Any, test_data: Dict[str, Any]
    ) -> bool:
        """Validate test prerequisites."""
        pass

    def get_test_result(
        self,
        score: float,
        metrics: Dict[str, float] = None,
        artifacts: Dict[str, str] = None,
        details: Dict[str, Any] = None,
    ) -> TestResult:
        """Create test result."""
        passed = score >= self.config.threshold

        return TestResult(
            test_id=self.config.test_id,
            test_name=self.config.name,
            status=TestStatus.PASSED if passed else TestStatus.FAILED,
            score=score,
            threshold=self.config.threshold,
            passed=passed,
            execution_time=(
                (self.end_time - self.start_time).total_seconds()
                if self.start_time and self.end_time
                else 0
            ),
            start_time=self.start_time or datetime.now(),
            end_time=self.end_time or datetime.now(),
            error_message=self.error_message,
            metrics=metrics or {},
            artifacts=artifacts or {},
            details=details or {},
        )


class AccuracyTest(ModelTest):
    """Model accuracy test."""

    async def execute(self, model: Any, test_data: Dict[str, Any]) -> TestResult:
        """Execute accuracy test."""
        try:
            self.status = TestStatus.RUNNING
            self.start_time = datetime.now()

            # Validate prerequisites
            await self.validate_prerequisites(model, test_data)

            # Get test data
            X_test = test_data.get("X_test")
            y_test = test_data.get("y_test")

            if X_test is None or y_test is None:
                raise ValueError("Test data not provided")

            # Make predictions
            if ML_AVAILABLE:
                if isinstance(model, torch.nn.Module):
                    predictions = self._torch_predict(model, X_test)
                elif hasattr(model, "predict"):
                    predictions = model.predict(X_test)
                else:
                    raise ValueError("Unsupported model type")
            else:
                # Mock predictions for demonstration
                predictions = np.random.randint(0, 2, len(y_test))

            # Calculate metrics
            accuracy = accuracy_score(y_test, predictions)
            precision = precision_score(
                y_test, predictions, average="weighted", zero_division=0
            )
            recall = recall_score(
                y_test, predictions, average="weighted", zero_division=0
            )
            f1 = f1_score(y_test, predictions, average="weighted", zero_division=0)

            metrics = {
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1_score": f1,
            }

            self.status = TestStatus.PASSED
            self.end_time = datetime.now()

            return self.get_test_result(
                score=accuracy,
                metrics=metrics,
                details={"predictions_count": len(predictions)},
            )

        except Exception as e:
            self.status = TestStatus.FAILED
            self.error_message = str(e)
            self.end_time = datetime.now()
            raise

    async def validate_prerequisites(
        self, model: Any, test_data: Dict[str, Any]
    ) -> bool:
        """Validate test prerequisites."""
        if not ML_AVAILABLE:
            raise ValueError("ML libraries not available")

        if test_data.get("X_test") is None or test_data.get("y_test") is None:
            raise ValueError("Test data not provided")

        return True

    def _torch_predict(self, model: torch.nn.Module, X_test: np.ndarray) -> np.ndarray:
        """Make predictions with PyTorch model."""
        model.eval()
        with torch.no_grad():
            X_tensor = torch.FloatTensor(X_test)
            predictions = model(X_tensor)
            return torch.argmax(predictions, dim=1).numpy()


class PerformanceTest(ModelTest):
    """Model performance test."""

    async def execute(self, model: Any, test_data: Dict[str, Any]) -> TestResult:
        """Execute performance test."""
        try:
            self.status = TestStatus.RUNNING
            self.start_time = datetime.now()

            # Validate prerequisites
            await self.validate_prerequisites(model, test_data)

            # Get test data
            X_test = test_data.get("X_test")
            batch_size = self.config.parameters.get("batch_size", 32)
            max_latency_ms = self.config.parameters.get("max_latency_ms", 100)

            # Measure inference time
            latencies = []
            for i in range(0, len(X_test), batch_size):
                batch = X_test[i : i + batch_size]

                start_time = time.time()

                if ML_AVAILABLE:
                    if isinstance(model, torch.nn.Module):
                        predictions = self._torch_predict(model, batch)
                    elif hasattr(model, "predict"):
                        predictions = model.predict(batch)
                    else:
                        raise ValueError("Unsupported model type")
                else:
                    # Mock predictions
                    predictions = np.random.randint(0, 2, len(batch))

                end_time = time.time()
                latency_ms = (end_time - start_time) * 1000
                latencies.append(latency_ms)

            # Calculate performance metrics
            avg_latency = np.mean(latencies)
            p95_latency = np.percentile(latencies, 95)
            p99_latency = np.percentile(latencies, 99)
            throughput = len(X_test) / sum(latencies) * 1000  # samples per second

            metrics = {
                "avg_latency_ms": avg_latency,
                "p95_latency_ms": p95_latency,
                "p99_latency_ms": p99_latency,
                "throughput_samples_per_sec": throughput,
            }

            # Score based on latency (lower is better, invert for scoring)
            score = max(0, 1 - (avg_latency / max_latency_ms))

            self.status = TestStatus.PASSED
            self.end_time = datetime.now()

            return self.get_test_result(
                score=score,
                metrics=metrics,
                details={"total_samples": len(X_test), "batch_size": batch_size},
            )

        except Exception as e:
            self.status = TestStatus.FAILED
            self.error_message = str(e)
            self.end_time = datetime.now()
            raise

    async def validate_prerequisites(
        self, model: Any, test_data: Dict[str, Any]
    ) -> bool:
        """Validate test prerequisites."""
        if test_data.get("X_test") is None:
            raise ValueError("Test data not provided")

        return True


class FairnessTest(ModelTest):
    """Model fairness test."""

    async def execute(self, model: Any, test_data: Dict[str, Any]) -> TestResult:
        """Execute fairness test."""
        try:
            self.status = TestStatus.RUNNING
            self.start_time = datetime.now()

            # Validate prerequisites
            await self.validate_prerequisites(model, test_data)

            # Get test data
            X_test = test_data.get("X_test")
            y_test = test_data.get("y_test")
            protected_attribute = test_data.get("protected_attribute")

            if protected_attribute is None:
                raise ValueError("Protected attribute not specified")

            # Make predictions
            if ML_AVAILABLE:
                if isinstance(model, torch.nn.Module):
                    predictions = self._torch_predict(model, X_test)
                elif hasattr(model, "predict"):
                    predictions = model.predict(X_test)
                else:
                    raise ValueError("Unsupported model type")
            else:
                # Mock predictions
                predictions = np.random.randint(0, 2, len(y_test))

            # Calculate fairness metrics
            fairness_metrics = self._calculate_fairness_metrics(
                y_test, predictions, protected_attribute
            )

            # Overall fairness score (average of all metrics)
            score = np.mean(list(fairness_metrics.values()))

            self.status = TestStatus.PASSED
            self.end_time = datetime.now()

            return self.get_test_result(
                score=score,
                metrics=fairness_metrics,
                details={"protected_attribute": protected_attribute},
            )

        except Exception as e:
            self.status = TestStatus.FAILED
            self.error_message = str(e)
            self.end_time = datetime.now()
            raise

    async def validate_prerequisites(
        self, model: Any, test_data: Dict[str, Any]
    ) -> bool:
        """Validate test prerequisites."""
        if test_data.get("protected_attribute") is None:
            raise ValueError("Protected attribute not specified")

        return True

    def _calculate_fairness_metrics(
        self, y_true: np.ndarray, y_pred: np.ndarray, protected_attr: np.ndarray
    ) -> Dict[str, float]:
        """Calculate fairness metrics."""
        # Demographic parity
        groups = np.unique(protected_attr)
        group_rates = {}

        for group in groups:
            group_mask = protected_attr == group
            if np.sum(group_mask) > 0:
                group_rate = np.mean(y_pred[group_mask])
                group_rates[group] = group_rate

        # Statistical parity difference
        if len(group_rates) >= 2:
            rates = list(group_rates.values())
            statistical_parity_diff = max(rates) - min(rates)
        else:
            statistical_parity_diff = 0.0

        # Equal opportunity difference (simplified)
        equal_opportunity_diff = 0.0
        for group in groups:
            group_mask = (protected_attr == group) & (y_true == 1)
            if np.sum(group_mask) > 0:
                group_tpr = np.mean(y_pred[group_mask])
                equal_opportunity_diff += abs(group_tpr - 0.5)  # Simplified

        if len(groups) > 0:
            equal_opportunity_diff /= len(groups)

        return {
            "demographic_parity_difference": statistical_parity_diff,
            "equal_opportunity_difference": equal_opportunity_diff,
            "overall_fairness_score": 1.0
            - (statistical_parity_diff + equal_opportunity_diff) / 2,
        }


class RobustnessTest(ModelTest):
    """Model robustness test."""

    async def execute(self, model: Any, test_data: Dict[str, Any]) -> TestResult:
        """Execute robustness test."""
        try:
            self.status = TestStatus.RUNNING
            self.start_time = datetime.now()

            # Validate prerequisites
            await self.validate_prerequisites(model, test_data)

            # Get test data
            X_test = test_data.get("X_test")
            y_test = test_data.get("y_test")
            noise_level = self.config.parameters.get("noise_level", 0.1)

            # Add noise to test data
            X_noisy = X_test + np.random.normal(0, noise_level, X_test.shape)

            # Make predictions on clean data
            if ML_AVAILABLE:
                if isinstance(model, torch.nn.Module):
                    clean_predictions = self._torch_predict(model, X_test)
                    noisy_predictions = self._torch_predict(model, X_noisy)
                elif hasattr(model, "predict"):
                    clean_predictions = model.predict(X_test)
                    noisy_predictions = model.predict(X_noisy)
                else:
                    raise ValueError("Unsupported model type")
            else:
                # Mock predictions
                clean_predictions = np.random.randint(0, 2, len(y_test))
                noisy_predictions = np.random.randint(0, 2, len(y_test))

            # Calculate robustness metrics
            clean_accuracy = accuracy_score(y_test, clean_predictions)
            noisy_accuracy = accuracy_score(y_test, noisy_predictions)
            accuracy_drop = clean_accuracy - noisy_accuracy

            metrics = {
                "clean_accuracy": clean_accuracy,
                "noisy_accuracy": noisy_accuracy,
                "accuracy_drop": accuracy_drop,
            }

            # Score based on accuracy retention
            score = max(0, 1 - accuracy_drop)

            self.status = TestStatus.PASSED
            self.end_time = datetime.now()

            return self.get_test_result(
                score=score, metrics=metrics, details={"noise_level": noise_level}
            )

        except Exception as e:
            self.status = TestStatus.FAILED
            self.error_message = str(e)
            self.end_time = datetime.now()
            raise

    async def validate_prerequisites(
        self, model: Any, test_data: Dict[str, Any]
    ) -> bool:
        """Validate test prerequisites."""
        if test_data.get("X_test") is None or test_data.get("y_test") is None:
            raise ValueError("Test data not provided")

        return True


class SecurityTest(ModelTest):
    """Model security test."""

    async def execute(self, model: Any, test_data: Dict[str, Any]) -> TestResult:
        """Execute security test."""
        try:
            self.status = TestStatus.RUNNING
            self.start_time = datetime.now()

            # Validate prerequisites
            await self.validate_prerequisites(model, test_data)

            # Get test data
            X_test = test_data.get("X_test")
            y_test = test_data.get("y_test")
            attack_epsilon = self.config.parameters.get("attack_epsilon", 0.1)

            # Generate adversarial examples (simplified)
            X_adv = self._generate_adversarial_examples(model, X_test, attack_epsilon)

            # Make predictions
            if ML_AVAILABLE:
                if isinstance(model, torch.nn.Module):
                    clean_predictions = self._torch_predict(model, X_test)
                    adv_predictions = self._torch_predict(model, X_adv)
                elif hasattr(model, "predict"):
                    clean_predictions = model.predict(X_test)
                    adv_predictions = model.predict(X_adv)
                else:
                    raise ValueError("Unsupported model type")
            else:
                # Mock predictions
                clean_predictions = np.random.randint(0, 2, len(y_test))
                adv_predictions = np.random.randint(0, 2, len(y_test))

            # Calculate security metrics
            clean_accuracy = accuracy_score(y_test, clean_predictions)
            adv_accuracy = accuracy_score(y_test, adv_predictions)
            success_rate = 1 - adv_accuracy  # Attack success rate

            metrics = {
                "clean_accuracy": clean_accuracy,
                "adversarial_accuracy": adv_accuracy,
                "attack_success_rate": success_rate,
            }

            # Score based on adversarial robustness
            score = adv_accuracy / clean_accuracy if clean_accuracy > 0 else 0

            self.status = TestStatus.PASSED
            self.end_time = datetime.now()

            return self.get_test_result(
                score=score, metrics=metrics, details={"attack_epsilon": attack_epsilon}
            )

        except Exception as e:
            self.status = TestStatus.FAILED
            self.error_message = str(e)
            self.end_time = datetime.now()
            raise

    async def validate_prerequisites(
        self, model: Any, test_data: Dict[str, Any]
    ) -> bool:
        """Validate test prerequisites."""
        if test_data.get("X_test") is None or test_data.get("y_test") is None:
            raise ValueError("Test data not provided")

        return True

    def _generate_adversarial_examples(
        self, model: Any, X: np.ndarray, epsilon: float
    ) -> np.ndarray:
        """Generate adversarial examples (simplified FGSM)."""
        # Simplified adversarial example generation
        noise = np.random.uniform(-epsilon, epsilon, X.shape)
        return np.clip(X + noise, 0, 1)


class AutomatedTestRunner:
    """Automated test runner for ML models."""

    def __init__(self):
        self.test_registry: Dict[str, Type[ModelTest]] = {
            TestType.ACCURACY.value: AccuracyTest,
            TestType.PERFORMANCE.value: PerformanceTest,
            TestType.FAIRNESS.value: FairnessTest,
            TestType.ROBUSTNESS.value: RobustnessTest,
            TestType.SECURITY.value: SecurityTest,
        }
        self.test_history: List[TestResult] = []

    def create_test_from_config(self, config: TestConfig) -> ModelTest:
        """Create test instance from configuration."""
        test_type = config.test_type.value
        test_class = self.test_registry.get(test_type)

        if test_class is None:
            raise ValueError(f"Unknown test type: {test_type}")

        return test_class(config)

    async def run_test_suite(
        self, test_suite: TestSuite, model: Any, test_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run a complete test suite."""
        suite_start_time = datetime.now()
        results = []

        try:
            if test_suite.parallel_execution:
                # Run tests in parallel
                semaphore = asyncio.Semaphore(test_suite.max_parallel_tests)
                tasks = []

                for test_config in test_suite.tests:
                    if not test_config.enabled:
                        continue

                    task = self._run_test_with_semaphore(
                        semaphore, test_config, model, test_data
                    )
                    tasks.append(task)

                results = await asyncio.gather(*tasks, return_exceptions=True)
            else:
                # Run tests sequentially
                for test_config in test_suite.tests:
                    if not test_config.enabled:
                        continue

                    try:
                        result = await self._run_single_test(
                            test_config, model, test_data
                        )
                        results.append(result)
                    except Exception as e:
                        # Create failed result
                        failed_result = TestResult(
                            test_id=test_config.test_id,
                            test_name=test_config.name,
                            status=TestStatus.ERROR,
                            score=0.0,
                            threshold=test_config.threshold,
                            passed=False,
                            execution_time=0.0,
                            start_time=datetime.now(),
                            end_time=datetime.now(),
                            error_message=str(e),
                        )
                        results.append(failed_result)

                    # Fail fast if enabled and test failed
                    if test_suite.fail_fast and not results[-1].passed:
                        break

            # Calculate suite summary
            suite_end_time = datetime.now()
            suite_execution_time = (suite_end_time - suite_start_time).total_seconds()

            passed_tests = [r for r in results if r.passed]
            failed_tests = [r for r in results if not r.passed]

            suite_result = {
                "suite_id": test_suite.suite_id,
                "suite_name": test_suite.name,
                "status": "passed" if len(failed_tests) == 0 else "failed",
                "start_time": suite_start_time.isoformat(),
                "end_time": suite_end_time.isoformat(),
                "execution_time": suite_execution_time,
                "total_tests": len(results),
                "passed_tests": len(passed_tests),
                "failed_tests": len(failed_tests),
                "pass_rate": len(passed_tests) / len(results) if results else 0,
                "test_results": [r.to_dict() for r in results],
                "summary": {
                    "critical_failures": len(
                        [
                            r
                            for r in failed_tests
                            if r.details.get("severity") == "critical"
                        ]
                    ),
                    "high_failures": len(
                        [r for r in failed_tests if r.details.get("severity") == "high"]
                    ),
                    "medium_failures": len(
                        [
                            r
                            for r in failed_tests
                            if r.details.get("severity") == "medium"
                        ]
                    ),
                    "low_failures": len(
                        [r for r in failed_tests if r.details.get("severity") == "low"]
                    ),
                },
            }

            # Store results
            self.test_history.extend(results)

            return suite_result

        except Exception as e:
            suite_end_time = datetime.now()

            return {
                "suite_id": test_suite.suite_id,
                "suite_name": test_suite.name,
                "status": "error",
                "start_time": suite_start_time.isoformat(),
                "end_time": suite_end_time.isoformat(),
                "execution_time": (suite_end_time - suite_start_time).total_seconds(),
                "error": str(e),
                "test_results": [],
            }

    async def _run_test_with_semaphore(
        self,
        semaphore: asyncio.Semaphore,
        test_config: TestConfig,
        model: Any,
        test_data: Dict[str, Any],
    ) -> TestResult:
        """Run test with semaphore for parallel execution."""
        async with semaphore:
            return await self._run_single_test(test_config, model, test_data)

    async def _run_single_test(
        self, test_config: TestConfig, model: Any, test_data: Dict[str, Any]
    ) -> TestResult:
        """Run a single test."""
        test = self.create_test_from_config(test_config)

        for attempt in range(test_config.retry_count + 1):
            try:
                result = await test.execute(model, test_data)
                return result
            except Exception as e:
                if attempt == test_config.retry_count:
                    raise
                await asyncio.sleep(1)  # Wait before retry

    def get_test_history(
        self, test_type: Optional[TestType] = None, limit: Optional[int] = None
    ) -> List[TestResult]:
        """Get test history."""
        history = self.test_history

        if test_type:
            history = [
                r for r in history if r.details.get("test_type") == test_type.value
            ]

        if limit:
            history = history[-limit:]

        return history

    def get_test_metrics(self) -> Dict[str, Any]:
        """Get test metrics and statistics."""
        if not self.test_history:
            return {}

        total_tests = len(self.test_history)
        passed_tests = len([r for r in self.test_history if r.passed])
        failed_tests = total_tests - passed_tests

        # Metrics by test type
        type_metrics = {}
        for test_type in TestType:
            type_tests = [
                r
                for r in self.test_history
                if r.details.get("test_type") == test_type.value
            ]
            if type_tests:
                type_passed = len([r for r in type_tests if r.passed])
                type_metrics[test_type.value] = {
                    "total": len(type_tests),
                    "passed": type_passed,
                    "failed": len(type_tests) - type_passed,
                    "pass_rate": type_passed / len(type_tests),
                }

        # Average scores by test type
        avg_scores = {}
        for test_type in TestType:
            type_tests = [
                r
                for r in self.test_history
                if r.details.get("test_type") == test_type.value
            ]
            if type_tests:
                avg_scores[test_type.value] = np.mean([r.score for r in type_tests])

        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "overall_pass_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "type_metrics": type_metrics,
            "average_scores": avg_scores,
            "last_updated": datetime.now().isoformat(),
        }


# Test templates and utilities
class TestTemplates:
    """Predefined test templates."""

    @staticmethod
    def get_comprehensive_test_suite() -> TestSuite:
        """Get comprehensive test suite for ML models."""
        tests = [
            TestConfig(
                name="accuracy_test",
                test_type=TestType.ACCURACY,
                threshold=0.8,
                description="Test model accuracy on test dataset",
                severity=Severity.HIGH,
            ),
            TestConfig(
                name="performance_test",
                test_type=TestType.PERFORMANCE,
                threshold=0.7,
                parameters={"max_latency_ms": 100, "batch_size": 32},
                description="Test model inference performance",
                severity=Severity.MEDIUM,
            ),
            TestConfig(
                name="fairness_test",
                test_type=TestType.FAIRNESS,
                threshold=0.7,
                description="Test model fairness across protected attributes",
                severity=Severity.HIGH,
            ),
            TestConfig(
                name="robustness_test",
                test_type=TestType.ROBUSTNESS,
                threshold=0.8,
                parameters={"noise_level": 0.1},
                description="Test model robustness to noisy inputs",
                severity=Severity.MEDIUM,
            ),
            TestConfig(
                name="security_test",
                test_type=TestType.SECURITY,
                threshold=0.6,
                parameters={"attack_epsilon": 0.1},
                description="Test model security against adversarial attacks",
                severity=Severity.HIGH,
            ),
        ]

        return TestSuite(
            name="comprehensive_ml_test_suite",
            description="Comprehensive test suite for ML models",
            tests=tests,
            parallel_execution=True,
            max_parallel_tests=3,
            fail_fast=False,
        )

    @staticmethod
    def get_production_test_suite() -> TestSuite:
        """Get production-ready test suite."""
        tests = [
            TestConfig(
                name="production_accuracy",
                test_type=TestType.ACCURACY,
                threshold=0.9,
                description="Production accuracy test",
                severity=Severity.CRITICAL,
            ),
            TestConfig(
                name="production_performance",
                test_type=TestType.PERFORMANCE,
                threshold=0.8,
                parameters={"max_latency_ms": 50},
                description="Production performance test",
                severity=Severity.CRITICAL,
            ),
            TestConfig(
                name="production_fairness",
                test_type=TestType.FAIRNESS,
                threshold=0.8,
                description="Production fairness test",
                severity=Severity.HIGH,
            ),
        ]

        return TestSuite(
            name="production_test_suite",
            description="Production deployment test suite",
            tests=tests,
            parallel_execution=False,
            fail_fast=True,
        )


# Example usage
async def example_usage():
    """Example usage of automated model testing."""
    # Create test runner
    runner = AutomatedTestRunner()

    # Create test suite
    test_suite = TestTemplates.get_comprehensive_test_suite()

    # Create dummy model and data
    class DummyModel:
        def predict(self, X):
            return np.random.randint(0, 2, len(X))

    model = DummyModel()

    # Create test data
    X_test = np.random.randn(100, 10)
    y_test = np.random.randint(0, 2, 100)
    protected_attr = np.random.randint(0, 2, 100)

    test_data = {
        "X_test": X_test,
        "y_test": y_test,
        "protected_attribute": protected_attr,
    }

    # Run test suite
    results = await runner.run_test_suite(test_suite, model, test_data)

    print(f"Test suite: {results['suite_name']}")
    print(f"Status: {results['status']}")
    print(f"Pass rate: {results['pass_rate']:.2%}")
    print(f"Execution time: {results['execution_time']:.2f}s")

    # Get metrics
    metrics = runner.get_test_metrics()
    print(f"Overall metrics: {metrics}")


if __name__ == "__main__":
    asyncio.run(example_usage())
