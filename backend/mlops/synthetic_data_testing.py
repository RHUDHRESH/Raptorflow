"""
S.W.A.R.M. Phase 2: Advanced MLOps - Synthetic Data Testing Suite
Comprehensive testing for synthetic data generation, quality, and monitoring
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

warnings.filterwarnings("ignore")

from data_quality_validation import (
    DataQualityValidator,
    QualityDimension,
    ValidationLevel,
    ValidationRule,
)

# Import synthetic data components
from synthetic_data_generation import (
    DataPrivacyLevel,
    DataQualityLevel,
    SyntheticDataConfig,
    SyntheticDataGenerator,
    SyntheticMethod,
)
from synthetic_data_monitoring import (
    MetricType,
    MonitoringConfig,
    MonitoringLevel,
    SyntheticDataMonitor,
)
from synthetic_data_scaling import ScalingConfig, ScalingStrategy, SyntheticDataScaler

logger = logging.getLogger("raptorflow.synthetic_data_testing")


class TestStatus(Enum):
    """Test execution status."""

    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TestCategory(Enum):
    """Test categories."""

    UNIT = "unit"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"
    END_TO_END = "end_to_end"
    REGRESSION = "regression"


@dataclass
class TestResult:
    """Test execution result."""

    test_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    test_name: str = ""
    category: TestCategory = TestCategory.UNIT
    status: TestStatus = TestStatus.PENDING
    execution_time: float = 0.0
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "test_id": self.test_id,
            "test_name": self.test_name,
            "category": self.category.value,
            "status": self.status.value,
            "execution_time": self.execution_time,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class TestSuite:
    """Test suite for synthetic data components."""

    suite_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    tests: List[TestResult] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    @property
    def total_tests(self) -> int:
        return len(self.tests)

    @property
    def passed_tests(self) -> int:
        return sum(1 for test in self.tests if test.status == TestStatus.PASSED)

    @property
    def failed_tests(self) -> int:
        return sum(1 for test in self.tests if test.status == TestStatus.FAILED)

    @property
    def skipped_tests(self) -> int:
        return sum(1 for test in self.tests if test.status == TestStatus.SKIPPED)

    @property
    def success_rate(self) -> float:
        return self.passed_tests / self.total_tests if self.total_tests > 0 else 0.0

    @property
    def total_execution_time(self) -> float:
        return sum(test.execution_time for test in self.tests)


class SyntheticDataTestSuite:
    """Comprehensive test suite for synthetic data components."""

    def __init__(self):
        self.test_suites: Dict[str, TestSuite] = {}
        self.sample_data = self._create_sample_data()

    def _create_sample_data(self) -> pd.DataFrame:
        """Create sample data for testing."""
        np.random.seed(42)
        return pd.DataFrame(
            {
                "customer_id": range(1000),
                "age": np.random.randint(18, 80, 1000),
                "income": np.random.normal(50000, 15000, 1000),
                "spending_score": np.random.uniform(1, 100, 1000),
                "gender": np.random.choice(["M", "F"], 1000),
                "region": np.random.choice(["North", "South", "East", "West"], 1000),
                "loyalty_years": np.random.exponential(2, 1000),
            }
        )

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all synthetic data tests."""
        logger.info("Starting comprehensive synthetic data test suite")

        # Run test categories
        unit_results = await self.run_unit_tests()
        integration_results = await self.run_integration_tests()
        performance_results = await self.run_performance_tests()
        end_to_end_results = await self.run_end_to_end_tests()

        # Create summary
        all_results = (
            unit_results
            + integration_results
            + performance_results
            + end_to_end_results
        )

        summary = {
            "total_tests": len(all_results),
            "passed": sum(1 for r in all_results if r.status == TestStatus.PASSED),
            "failed": sum(1 for r in all_results if r.status == TestStatus.FAILED),
            "skipped": sum(1 for r in all_results if r.status == TestStatus.SKIPPED),
            "success_rate": (
                sum(1 for r in all_results if r.status == TestStatus.PASSED)
                / len(all_results)
                if all_results
                else 0.0
            ),
            "total_execution_time": sum(r.execution_time for r in all_results),
            "test_categories": {
                "unit": len(unit_results),
                "integration": len(integration_results),
                "performance": len(performance_results),
                "end_to_end": len(end_to_end_results),
            },
            "results": [r.to_dict() for r in all_results],
        }

        logger.info(
            f"Test suite completed: {summary['passed']}/{summary['total_tests']} passed"
        )
        return summary

    async def run_unit_tests(self) -> List[TestResult]:
        """Run unit tests for individual components."""
        logger.info("Running unit tests")

        tests = []

        # Test synthetic data generator
        tests.extend(await self._test_synthetic_data_generator())

        # Test data quality validator
        tests.extend(await self._test_data_quality_validator())

        # Test synthetic data scaler
        tests.extend(await self._test_synthetic_data_scaler())

        # Test synthetic data monitor
        tests.extend(await self._test_synthetic_data_monitor())

        return tests

    async def run_integration_tests(self) -> List[TestResult]:
        """Run integration tests between components."""
        logger.info("Running integration tests")

        tests = []

        # Test generator + validator integration
        tests.extend(await self._test_generator_validator_integration())

        # Test generator + scaler integration
        tests.extend(await self._test_generator_scaler_integration())

        # Test generator + monitor integration
        tests.extend(await self._test_generator_monitor_integration())

        # Test full pipeline integration
        tests.extend(await self._test_full_pipeline_integration())

        return tests

    async def run_performance_tests(self) -> List[TestResult]:
        """Run performance tests."""
        logger.info("Running performance tests")

        tests = []

        # Test generation performance
        tests.extend(await self._test_generation_performance())

        # Test scaling performance
        tests.extend(await self._test_scaling_performance())

        # Test validation performance
        tests.extend(await self._test_validation_performance())

        return tests

    async def run_end_to_end_tests(self) -> List[TestResult]:
        """Run end-to-end tests."""
        logger.info("Running end-to-end tests")

        tests = []

        # Test complete synthetic data workflow
        tests.extend(await self._test_complete_workflow())

        # Test large-scale synthetic data generation
        tests.extend(await self._test_large_scale_generation())

        return tests

    async def _test_synthetic_data_generator(self) -> List[TestResult]:
        """Test synthetic data generator."""
        tests = []

        # Test basic generation
        test = TestResult(test_name="test_basic_generation", category=TestCategory.UNIT)

        start_time = time.time()

        try:
            generator = SyntheticDataGenerator()
            config = SyntheticDataConfig(
                method=SyntheticMethod.STATISTICAL,
                target_columns=list(self.sample_data.columns),
                sample_size=100,
            )

            result = generator.generate_synthetic_data(self.sample_data, config)

            assert result["status"] == "success", "Generation should succeed"
            assert (
                len(result["synthetic_data"]) == 100
            ), "Should generate correct number of samples"
            assert result["overall_quality"] > 0, "Quality score should be positive"

            test.status = TestStatus.PASSED
            test.message = "Basic generation test passed"
            test.details = {
                "generated_samples": len(result["synthetic_data"]),
                "quality_score": result["overall_quality"],
                "privacy_score": result["privacy_score"],
            }

        except Exception as e:
            test.status = TestStatus.FAILED
            test.message = f"Basic generation test failed: {str(e)}"

        test.execution_time = time.time() - start_time
        tests.append(test)

        # Test privacy levels
        test = TestResult(test_name="test_privacy_levels", category=TestCategory.UNIT)

        start_time = time.time()

        try:
            generator = SyntheticDataGenerator()
            privacy_scores = []

            for privacy_level in DataPrivacyLevel:
                config = SyntheticDataConfig(
                    method=SyntheticMethod.STATISTICAL,
                    target_columns=list(self.sample_data.columns),
                    sample_size=100,
                    privacy_level=privacy_level,
                )

                result = generator.generate_synthetic_data(self.sample_data, config)

                if result["status"] == "success":
                    privacy_scores.append(result["privacy_score"])

            assert len(privacy_scores) > 0, "Should have privacy scores"
            assert all(
                score >= 0 for score in privacy_scores
            ), "Privacy scores should be non-negative"

            test.status = TestStatus.PASSED
            test.message = "Privacy levels test passed"
            test.details = {
                "privacy_levels_tested": len(privacy_scores),
                "privacy_scores": privacy_scores,
            }

        except Exception as e:
            test.status = TestStatus.FAILED
            test.message = f"Privacy levels test failed: {str(e)}"

        test.execution_time = time.time() - start_time
        tests.append(test)

        return tests

    async def _test_data_quality_validator(self) -> List[TestResult]:
        """Test data quality validator."""
        tests = []

        # Test basic validation
        test = TestResult(test_name="test_basic_validation", category=TestCategory.UNIT)

        start_time = time.time()

        try:
            validator = DataQualityValidator()

            # Add validation rules
            rule = ValidationRule(
                name="Age Completeness",
                dimension=QualityDimension.COMPLETENESS,
                column="age",
                rule_type="completeness",
                threshold=0.90,
            )

            validator.add_rule(rule)

            # Create test data with missing values
            test_data = self.sample_data.copy()
            test_data.loc[:10, "age"] = np.nan

            report = validator.validate_dataset(
                test_data, ValidationLevel.BASIC, "test_data"
            )

            assert report.total_rules > 0, "Should have validation rules"
            assert report.overall_score >= 0, "Overall score should be non-negative"

            test.status = TestStatus.PASSED
            test.message = "Basic validation test passed"
            test.details = {
                "total_rules": report.total_rules,
                "overall_score": report.overall_score,
                "passed_rules": report.passed_rules,
            }

        except Exception as e:
            test.status = TestStatus.FAILED
            test.message = f"Basic validation test failed: {str(e)}"

        test.execution_time = time.time() - start_time
        tests.append(test)

        return tests

    async def _test_synthetic_data_scaler(self) -> List[TestResult]:
        """Test synthetic data scaler."""
        tests = []

        # Test basic scaling
        test = TestResult(test_name="test_basic_scaling", category=TestCategory.UNIT)

        start_time = time.time()

        try:
            scaler = SyntheticDataScaler()
            config = ScalingConfig(
                strategy=ScalingStrategy.BATCH, target_size=1000, batch_size=100
            )

            scaling_id = scaler.create_scaling_operation(config)
            result = scaler.scale_synthetic_data(self.sample_data[:100], config)

            assert result["status"] == "success", "Scaling should succeed"
            assert len(result["synthetic_data"]) == 1000, "Should scale to target size"

            test.status = TestStatus.PASSED
            test.message = "Basic scaling test passed"
            test.details = {
                "target_size": 1000,
                "actual_size": len(result["synthetic_data"]),
                "scaling_id": scaling_id,
            }

        except Exception as e:
            test.status = TestStatus.FAILED
            test.message = f"Basic scaling test failed: {str(e)}"

        test.execution_time = time.time() - start_time
        tests.append(test)

        return tests

    async def _test_synthetic_data_monitor(self) -> List[TestResult]:
        """Test synthetic data monitor."""
        tests = []

        # Test basic monitoring
        test = TestResult(test_name="test_basic_monitoring", category=TestCategory.UNIT)

        start_time = time.time()

        try:
            monitor = SyntheticDataMonitor()
            config = MonitoringConfig(
                dataset_name="test_data",
                monitoring_level=MonitoringLevel.BASIC,
                baseline_data=self.sample_data,
            )

            monitor_id = monitor.create_monitor(config)
            monitor.start_monitoring(monitor_id)

            # Monitor synthetic data
            alerts = monitor.monitor_synthetic_data(monitor_id, self.sample_data)

            summary = monitor.get_monitoring_summary(monitor_id)

            assert summary["monitor_id"] == monitor_id, "Monitor ID should match"
            assert summary["is_active"] == True, "Monitor should be active"

            test.status = TestStatus.PASSED
            test.message = "Basic monitoring test passed"
            test.details = {
                "monitor_id": monitor_id,
                "total_alerts": len(alerts),
                "is_active": summary["is_active"],
            }

        except Exception as e:
            test.status = TestStatus.FAILED
            test.message = f"Basic monitoring test failed: {str(e)}"

        test.execution_time = time.time() - start_time
        tests.append(test)

        return tests

    async def _test_generator_validator_integration(self) -> List[TestResult]:
        """Test generator + validator integration."""
        tests = []

        test = TestResult(
            test_name="test_generator_validator_integration",
            category=TestCategory.INTEGRATION,
        )

        start_time = time.time()

        try:
            # Generate synthetic data
            generator = SyntheticDataGenerator()
            config = SyntheticDataConfig(
                method=SyntheticMethod.STATISTICAL,
                target_columns=list(self.sample_data.columns),
                sample_size=1000,
                quality_level=DataQualityLevel.COMPREHENSIVE,
            )

            generation_result = generator.generate_synthetic_data(
                self.sample_data, config
            )

            # Validate synthetic data
            validator = DataQualityValidator()
            validation_report = validator.validate_dataset(
                generation_result["synthetic_data"],
                ValidationLevel.STANDARD,
                "synthetic_data",
            )

            assert generation_result["status"] == "success", "Generation should succeed"
            assert validation_report.total_rules > 0, "Should have validation rules"

            test.status = TestStatus.PASSED
            test.message = "Generator + validator integration test passed"
            test.details = {
                "generation_quality": generation_result["overall_quality"],
                "validation_score": validation_report.overall_score,
                "validation_rules": validation_report.total_rules,
            }

        except Exception as e:
            test.status = TestStatus.FAILED
            test.message = f"Generator + validator integration test failed: {str(e)}"

        test.execution_time = time.time() - start_time
        tests.append(test)

        return tests

    async def _test_generator_scaler_integration(self) -> List[TestResult]:
        """Test generator + scaler integration."""
        tests = []

        test = TestResult(
            test_name="test_generator_scaler_integration",
            category=TestCategory.INTEGRATION,
        )

        start_time = time.time()

        try:
            # Generate synthetic data
            generator = SyntheticDataGenerator()
            config = SyntheticDataConfig(
                method=SyntheticMethod.STATISTICAL,
                target_columns=list(self.sample_data.columns),
                sample_size=100,
            )

            generation_result = generator.generate_synthetic_data(
                self.sample_data, config
            )

            # Scale synthetic data
            scaler = SyntheticDataScaler()
            scaling_config = ScalingConfig(
                strategy=ScalingStrategy.BATCH, target_size=1000, batch_size=100
            )

            scaling_result = scaler.scale_synthetic_data(
                generation_result["synthetic_data"], scaling_config
            )

            assert generation_result["status"] == "success", "Generation should succeed"
            assert scaling_result["status"] == "success", "Scaling should succeed"
            assert (
                len(scaling_result["synthetic_data"]) == 1000
            ), "Should scale to target size"

            test.status = TestStatus.PASSED
            test.message = "Generator + scaler integration test passed"
            test.details = {
                "original_size": len(generation_result["synthetic_data"]),
                "scaled_size": len(scaling_result["synthetic_data"]),
                "scaling_factor": len(scaling_result["synthetic_data"])
                / len(generation_result["synthetic_data"]),
            }

        except Exception as e:
            test.status = TestStatus.FAILED
            test.message = f"Generator + scaler integration test failed: {str(e)}"

        test.execution_time = time.time() - start_time
        tests.append(test)

        return tests

    async def _test_generator_monitor_integration(self) -> List[TestResult]:
        """Test generator + monitor integration."""
        tests = []

        test = TestResult(
            test_name="test_generator_monitor_integration",
            category=TestCategory.INTEGRATION,
        )

        start_time = time.time()

        try:
            # Create monitor
            monitor = SyntheticDataMonitor()
            config = MonitoringConfig(
                dataset_name="test_data",
                monitoring_level=MonitoringLevel.STANDARD,
                baseline_data=self.sample_data,
            )

            monitor_id = monitor.create_monitor(config)
            monitor.start_monitoring(monitor_id)

            # Generate synthetic data
            generator = SyntheticDataGenerator()
            generation_config = SyntheticDataConfig(
                method=SyntheticMethod.STATISTICAL,
                target_columns=list(self.sample_data.columns),
                sample_size=1000,
            )

            generation_result = generator.generate_synthetic_data(
                self.sample_data, generation_config
            )

            # Monitor synthetic data
            alerts = monitor.monitor_synthetic_data(
                monitor_id,
                generation_result["synthetic_data"],
                self.sample_data,
                generation_result["generation_time"],
            )

            assert generation_result["status"] == "success", "Generation should succeed"
            assert len(alerts) >= 0, "Should generate alerts (or none)"

            test.status = TestStatus.PASSED
            test.message = "Generator + monitor integration test passed"
            test.details = {
                "generation_quality": generation_result["overall_quality"],
                "alerts_generated": len(alerts),
                "monitoring_active": monitor.active_monitors[monitor_id],
            }

        except Exception as e:
            test.status = TestStatus.FAILED
            test.message = f"Generator + monitor integration test failed: {str(e)}"

        test.execution_time = time.time() - start_time
        tests.append(test)

        return tests

    async def _test_full_pipeline_integration(self) -> List[TestResult]:
        """Test full pipeline integration."""
        tests = []

        test = TestResult(
            test_name="test_full_pipeline_integration",
            category=TestCategory.INTEGRATION,
        )

        start_time = time.time()

        try:
            # Generate synthetic data
            generator = SyntheticDataGenerator()
            config = SyntheticDataConfig(
                method=SyntheticMethod.STATISTICAL,
                target_columns=list(self.sample_data.columns),
                sample_size=500,
                quality_level=DataQualityLevel.COMPREHENSIVE,
                privacy_level=DataPrivacyLevel.STANDARD,
            )

            generation_result = generator.generate_synthetic_data(
                self.sample_data, config
            )

            # Validate synthetic data
            validator = DataQualityValidator()
            validation_report = validator.validate_dataset(
                generation_result["synthetic_data"],
                ValidationLevel.STANDARD,
                "synthetic_data",
            )

            # Scale synthetic data
            scaler = SyntheticDataScaler()
            scaling_config = ScalingConfig(
                strategy=ScalingStrategy.BATCH, target_size=2000, batch_size=200
            )

            scaling_result = scaler.scale_synthetic_data(
                generation_result["synthetic_data"], scaling_config
            )

            # Monitor scaled data
            monitor = SyntheticDataMonitor()
            monitor_config = MonitoringConfig(
                dataset_name="scaled_synthetic_data",
                monitoring_level=MonitoringLevel.STANDARD,
                baseline_data=self.sample_data,
            )

            monitor_id = monitor.create_monitor(monitor_config)
            monitor.start_monitoring(monitor_id)

            alerts = monitor.monitor_synthetic_data(
                monitor_id,
                scaling_result["synthetic_data"],
                self.sample_data,
                scaling_result["progress"]["processing_rate"],
            )

            # Verify all components worked
            assert generation_result["status"] == "success", "Generation should succeed"
            assert validation_report.total_rules > 0, "Validation should have rules"
            assert scaling_result["status"] == "success", "Scaling should succeed"
            assert (
                len(scaling_result["synthetic_data"]) == 2000
            ), "Should scale correctly"

            test.status = TestStatus.PASSED
            test.message = "Full pipeline integration test passed"
            test.details = {
                "generation_quality": generation_result["overall_quality"],
                "validation_score": validation_report.overall_score,
                "scaling_factor": len(scaling_result["synthetic_data"])
                / len(generation_result["synthetic_data"]),
                "monitoring_alerts": len(alerts),
            }

        except Exception as e:
            test.status = TestStatus.FAILED
            test.message = f"Full pipeline integration test failed: {str(e)}"

        test.execution_time = time.time() - start_time
        tests.append(test)

        return tests

    async def _test_generation_performance(self) -> List[TestResult]:
        """Test generation performance."""
        tests = []

        test = TestResult(
            test_name="test_generation_performance", category=TestCategory.PERFORMANCE
        )

        start_time = time.time()

        try:
            generator = SyntheticDataGenerator()

            # Test different sample sizes
            sample_sizes = [100, 500, 1000]
            generation_times = []

            for size in sample_sizes:
                config = SyntheticDataConfig(
                    method=SyntheticMethod.STATISTICAL,
                    target_columns=list(self.sample_data.columns),
                    sample_size=size,
                )

                gen_start = time.time()
                result = generator.generate_synthetic_data(self.sample_data, config)
                gen_time = time.time() - gen_start

                if result["status"] == "success":
                    generation_times.append(gen_time)

            assert len(generation_times) == len(
                sample_sizes
            ), "All generations should succeed"

            # Check performance scaling
            avg_time_per_sample = np.mean(
                [t / s for t, s in zip(generation_times, sample_sizes)]
            )

            test.status = TestStatus.PASSED
            test.message = "Generation performance test passed"
            test.details = {
                "sample_sizes": sample_sizes,
                "generation_times": generation_times,
                "avg_time_per_sample": avg_time_per_sample,
            }

        except Exception as e:
            test.status = TestStatus.FAILED
            test.message = f"Generation performance test failed: {str(e)}"

        test.execution_time = time.time() - start_time
        tests.append(test)

        return tests

    async def _test_scaling_performance(self) -> List[TestResult]:
        """Test scaling performance."""
        tests = []

        test = TestResult(
            test_name="test_scaling_performance", category=TestCategory.PERFORMANCE
        )

        start_time = time.time()

        try:
            scaler = SyntheticDataScaler()

            # Test different scaling strategies
            strategies = [ScalingStrategy.BATCH]
            scaling_times = []

            for strategy in strategies:
                config = ScalingConfig(
                    strategy=strategy, target_size=1000, batch_size=100
                )

                scaling_start = time.time()
                result = scaler.scale_synthetic_data(self.sample_data[:100], config)
                scaling_time = time.time() - scaling_start

                if result["status"] == "success":
                    scaling_times.append(scaling_time)

            assert len(scaling_times) > 0, "At least one scaling should succeed"

            test.status = TestStatus.PASSED
            test.message = "Scaling performance test passed"
            test.details = {
                "strategies_tested": [s.value for s in strategies],
                "scaling_times": scaling_times,
                "avg_scaling_time": np.mean(scaling_times),
            }

        except Exception as e:
            test.status = TestStatus.FAILED
            test.message = f"Scaling performance test failed: {str(e)}"

        test.execution_time = time.time() - start_time
        tests.append(test)

        return tests

    async def _test_validation_performance(self) -> List[TestResult]:
        """Test validation performance."""
        tests = []

        test = TestResult(
            test_name="test_validation_performance", category=TestCategory.PERFORMANCE
        )

        start_time = time.time()

        try:
            validator = DataQualityValidator()

            # Add validation rules
            rule = ValidationRule(
                name="Age Completeness",
                dimension=QualityDimension.COMPLETENESS,
                column="age",
                rule_type="completeness",
                threshold=0.90,
            )

            validator.add_rule(rule)

            # Test validation on different data sizes
            data_sizes = [100, 500, 1000]
            validation_times = []

            for size in data_sizes:
                test_data = self.sample_data[:size].copy()
                test_data.loc[: size // 10, "age"] = np.nan  # Add some missing values

                val_start = time.time()
                report = validator.validate_dataset(
                    test_data, ValidationLevel.BASIC, f"test_data_{size}"
                )
                val_time = time.time() - val_start

                validation_times.append(val_time)

            assert len(validation_times) == len(
                data_sizes
            ), "All validations should succeed"

            test.status = TestStatus.PASSED
            test.message = "Validation performance test passed"
            test.details = {
                "data_sizes": data_sizes,
                "validation_times": validation_times,
                "avg_validation_time": np.mean(validation_times),
            }

        except Exception as e:
            test.status = TestStatus.FAILED
            test.message = f"Validation performance test failed: {str(e)}"

        test.execution_time = time.time() - start_time
        tests.append(test)

        return tests

    async def _test_complete_workflow(self) -> List[TestResult]:
        """Test complete synthetic data workflow."""
        tests = []

        test = TestResult(
            test_name="test_complete_workflow", category=TestCategory.END_TO_END
        )

        start_time = time.time()

        try:
            workflow_start = time.time()

            # Step 1: Generate synthetic data
            generator = SyntheticDataGenerator()
            config = SyntheticDataConfig(
                method=SyntheticMethod.STATISTICAL,
                target_columns=list(self.sample_data.columns),
                sample_size=1000,
                quality_level=DataQualityLevel.COMPREHENSIVE,
                privacy_level=DataPrivacyLevel.STANDARD,
            )

            generation_result = generator.generate_synthetic_data(
                self.sample_data, config
            )

            # Step 2: Validate synthetic data
            validator = DataQualityValidator()
            validation_report = validator.validate_dataset(
                generation_result["synthetic_data"],
                ValidationLevel.STANDARD,
                "synthetic_data",
            )

            # Step 3: Scale synthetic data
            scaler = SyntheticDataScaler()
            scaling_config = ScalingConfig(
                strategy=ScalingStrategy.BATCH, target_size=5000, batch_size=500
            )

            scaling_result = scaler.scale_synthetic_data(
                generation_result["synthetic_data"], scaling_config
            )

            # Step 4: Monitor scaled data
            monitor = SyntheticDataMonitor()
            monitor_config = MonitoringConfig(
                dataset_name="workflow_synthetic_data",
                monitoring_level=MonitoringLevel.STANDARD,
                baseline_data=self.sample_data,
            )

            monitor_id = monitor.create_monitor(monitor_config)
            monitor.start_monitoring(monitor_id)

            alerts = monitor.monitor_synthetic_data(
                monitor_id,
                scaling_result["synthetic_data"],
                self.sample_data,
                scaling_result["progress"]["processing_rate"],
            )

            workflow_time = time.time() - workflow_start

            # Verify workflow success
            assert generation_result["status"] == "success", "Generation should succeed"
            assert validation_report.total_rules > 0, "Validation should have rules"
            assert scaling_result["status"] == "success", "Scaling should succeed"
            assert (
                len(scaling_result["synthetic_data"]) == 5000
            ), "Should scale correctly"

            test.status = TestStatus.PASSED
            test.message = "Complete workflow test passed"
            test.details = {
                "workflow_time": workflow_time,
                "generation_quality": generation_result["overall_quality"],
                "validation_score": validation_report.overall_score,
                "final_data_size": len(scaling_result["synthetic_data"]),
                "monitoring_alerts": len(alerts),
                "steps_completed": 4,
            }

        except Exception as e:
            test.status = TestStatus.FAILED
            test.message = f"Complete workflow test failed: {str(e)}"

        test.execution_time = time.time() - start_time
        tests.append(test)

        return tests

    async def _test_large_scale_generation(self) -> List[TestResult]:
        """Test large-scale synthetic data generation."""
        tests = []

        test = TestResult(
            test_name="test_large_scale_generation", category=TestCategory.END_TO_END
        )

        start_time = time.time()

        try:
            # Generate large synthetic dataset
            generator = SyntheticDataGenerator()
            config = SyntheticDataConfig(
                method=SyntheticMethod.STATISTICAL,
                target_columns=list(self.sample_data.columns),
                sample_size=10000,  # Large dataset
                quality_level=DataQualityLevel.STANDARD,
                privacy_level=DataPrivacyLevel.STANDARD,
            )

            generation_start = time.time()
            result = generator.generate_synthetic_data(self.sample_data, config)
            generation_time = time.time() - generation_start

            assert (
                result["status"] == "success"
            ), "Large-scale generation should succeed"
            assert (
                len(result["synthetic_data"]) == 10000
            ), "Should generate correct size"

            # Test scaling to even larger size
            scaler = SyntheticDataScaler()
            scaling_config = ScalingConfig(
                strategy=ScalingStrategy.BATCH,
                target_size=50000,  # Very large dataset
                batch_size=1000,
            )

            scaling_start = time.time()
            scaling_result = scaler.scale_synthetic_data(
                result["synthetic_data"], scaling_config
            )
            scaling_time = time.time() - scaling_start

            assert (
                scaling_result["status"] == "success"
            ), "Large-scale scaling should succeed"
            assert (
                len(scaling_result["synthetic_data"]) == 50000
            ), "Should scale to target size"

            test.status = TestStatus.PASSED
            test.message = "Large-scale generation test passed"
            test.details = {
                "initial_generation_size": len(result["synthetic_data"]),
                "final_scaled_size": len(scaling_result["synthetic_data"]),
                "generation_time": generation_time,
                "scaling_time": scaling_time,
                "generation_rate": len(result["synthetic_data"]) / generation_time,
                "scaling_rate": len(scaling_result["synthetic_data"]) / scaling_time,
            }

        except Exception as e:
            test.status = TestStatus.FAILED
            test.message = f"Large-scale generation test failed: {str(e)}"

        test.execution_time = time.time() - start_time
        tests.append(test)

        return tests


# Example usage
async def demonstrate_synthetic_data_testing():
    """Demonstrate synthetic data testing system."""
    print("Demonstrating S.W.A.R.M. Phase 2 Advanced MLOps - Synthetic Data Testing...")

    # Create test suite
    test_suite = SyntheticDataTestSuite()

    print("Running comprehensive synthetic data test suite...")

    # Run all tests
    start_time = time.time()
    results = await test_suite.run_all_tests()
    total_time = time.time() - start_time

    # Display results
    print(f"\nTest Suite Results:")
    print(f"  Total tests: {results['total_tests']}")
    print(f"  Passed: {results['passed']}")
    print(f"  Failed: {results['failed']}")
    print(f"  Skipped: {results['skipped']}")
    print(f"  Success rate: {results['success_rate']:.1%}")
    print(f"  Total execution time: {results['total_execution_time']:.2f} seconds")
    print(f"  Suite execution time: {total_time:.2f} seconds")

    print(f"\nTest Categories:")
    for category, count in results["test_categories"].items():
        print(f"  {category}: {count} tests")

    # Show failed tests
    failed_tests = [r for r in results["results"] if r["status"] == "failed"]
    if failed_tests:
        print(f"\nFailed Tests ({len(failed_tests)}):")
        for test in failed_tests:
            print(f"  {test['test_name']}: {test['message']}")

    # Show performance highlights
    performance_tests = [
        r
        for r in results["results"]
        if "performance" in r["test_name"] and r["status"] == "passed"
    ]
    if performance_tests:
        print(f"\nPerformance Test Highlights:")
        for test in performance_tests:
            print(f"  {test['test_name']}: {test['execution_time']:.3f}s")
            if "details" in test and test["details"]:
                for key, value in test["details"].items():
                    if isinstance(value, (int, float)) and not isinstance(value, bool):
                        print(f"    {key}: {value:.3f}")

    print("\nSynthetic Data Testing demonstration complete!")


if __name__ == "__main__":
    asyncio.run(demonstrate_synthetic_data_testing())
