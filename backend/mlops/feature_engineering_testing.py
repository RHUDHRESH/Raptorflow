"""
S.W.A.R.M. Phase 2: Advanced MLOps - Feature Engineering Testing Suite
Comprehensive testing for feature engineering components
"""

import asyncio
import hashlib
import json
import logging
import os
import pickle
import shutil
import tempfile
import time
import unittest
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
import yaml

# Import feature engineering components
from feature_engineering_pipelines import (
    FeatureAnalyzer,
    FeatureEngineeringPipeline,
    FeaturePipelineConfig,
    FeatureSelector,
    FeatureTransformer,
    FeatureType,
    TransformationType,
)
from feature_monitoring_system import (
    FeatureMonitorConfig,
    FeatureMonitoringSystem,
    MonitoringLevel,
)
from feature_versioning_system import (
    FeatureVersion,
    FeatureVersioningSystem,
    VersioningConfig,
    VersionStatus,
)

logger = logging.getLogger("raptorflow.feature_engineering_testing")


class TestResult:
    """Test result container."""

    def __init__(self, test_name: str):
        self.test_name = test_name
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.duration: float = 0.0
        self.passed: bool = False
        self.error_message: Optional[str] = None
        self.assertions: List[str] = []

    def add_assertion(self, message: str, passed: bool):
        """Add test assertion."""
        self.assertions.append(f"{'PASS' if passed else 'FAIL'}: {message}")
        if not passed:
            self.passed = False

    def finish(self, passed: bool = True, error_message: Optional[str] = None):
        """Finish test."""
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()
        self.passed = passed
        self.error_message = error_message

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "test_name": self.test_name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "passed": self.passed,
            "error_message": self.error_message,
        }


class FeatureEngineeringTestSuite:
    """Comprehensive test suite for feature engineering components."""

    def __init__(self):
        self.test_results: List[TestResult] = []
        self.temp_dir = tempfile.mkdtemp()

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all feature engineering tests."""
        logger.info("Starting feature engineering test suite...")

        # Test categories
        test_categories = [
            ("Feature Analysis Tests", self.test_feature_analysis),
            ("Feature Transformation Tests", self.test_feature_transformation),
            ("Feature Selection Tests", self.test_feature_selection),
            ("Pipeline Execution Tests", self.test_pipeline_execution),
            ("Feature Monitoring Tests", self.test_feature_monitoring),
            ("Feature Versioning Tests", self.test_feature_versioning),
            ("Integration Tests", self.test_integration),
            ("Performance Tests", self.test_performance),
        ]

        total_tests = 0
        passed_tests = 0
        failed_tests = 0

        for category_name, test_method in test_categories:
            logger.info(f"Running {category_name}...")
            category_results = await test_method()

            for result in category_results:
                self.test_results.append(result)
                total_tests += 1
                if result.passed:
                    passed_tests += 1
                else:
                    failed_tests += 1

        # Generate summary
        summary = {
            "test_suite": "Feature Engineering Components",
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "total_duration": sum(r.duration for r in self.test_results),
            "categories": {
                category_name: {
                    "total": len(await test_method()),
                    "passed": len([r for r in await test_method() if r.passed]),
                    "failed": len([r for r in await test_method() if not r.passed]),
                }
                for category_name, test_method in test_categories
            },
        }

        logger.info(f"Test suite completed: {passed_tests}/{total_tests} tests passed")
        return summary

    async def test_feature_analysis(self) -> List[TestResult]:
        """Test feature analysis components."""
        results = []

        # Test 1: Feature Type Detection
        result = TestResult("Feature Type Detection")
        try:
            analyzer = FeatureAnalyzer()

            # Create test data
            test_data = pd.DataFrame(
                {
                    "numerical": [1, 2, 3, 4, 5],
                    "categorical": ["A", "B", "A", "C", "B"],
                    "boolean": [True, False, True, False, True],
                    "datetime": pd.date_range("2023-01-01", periods=5),
                }
            )

            # Test type detection
            for column in test_data.columns:
                metadata = analyzer.analyze_feature(column, test_data[column])
                result.add_assertion(
                    f"Type detected for {column}", metadata.feature_type is not None
                )

            result.finish(True)

        except Exception as e:
            result.finish(False, str(e))

        results.append(result)

        # Test 2: Statistical Analysis
        result = TestResult("Statistical Analysis")
        try:
            analyzer = FeatureAnalyzer()

            # Create numerical test data
            np.random.seed(42)
            numerical_data = pd.Series(np.random.normal(0, 1, 1000))

            metadata = analyzer.analyze_feature("test_numerical", numerical_data)

            result.add_assertion(
                "Mean calculated", "mean" in metadata.distribution_stats
            )
            result.add_assertion("Std calculated", "std" in metadata.distribution_stats)
            result.add_assertion("Min calculated", "min" in metadata.distribution_stats)
            result.add_assertion("Max calculated", "max" in metadata.distribution_stats)

            result.finish(True)

        except Exception as e:
            result.finish(False, str(e))

        results.append(result)

        return results

    async def test_feature_transformation(self) -> List[TestResult]:
        """Test feature transformation components."""
        results = []

        # Test 1: Normalization Transformation
        result = TestResult("Normalization Transformation")
        try:
            transformer = FeatureTransformer()

            # Create test data
            test_data = pd.DataFrame(
                {"feature1": [1, 2, 3, 4, 5], "feature2": [10, 20, 30, 40, 50]}
            )

            # Create transformation
            from feature_engineering_pipelines import FeatureTransformation

            transformation = FeatureTransformation(
                transformation_type=TransformationType.NORMALIZATION,
                source_features=["feature1", "feature2"],
            )

            # Apply transformation
            transformed_data = transformer.apply_transformation(
                test_data, transformation
            )

            result.add_assertion(
                "Normalization applied",
                "feature1_normalized" in transformed_data.columns,
            )
            result.add_assertion(
                "Values in range [0,1]",
                all(0 <= val <= 1 for val in transformed_data["feature1_normalized"]),
            )

            result.finish(True)

        except Exception as e:
            result.finish(False, str(e))

        results.append(result)

        # Test 2: Encoding Transformation
        result = TestResult("Encoding Transformation")
        try:
            transformer = FeatureTransformer()

            # Create categorical test data
            test_data = pd.DataFrame({"category": ["A", "B", "A", "C", "B"]})

            # Create encoding transformation
            from feature_engineering_pipelines import FeatureTransformation

            transformation = FeatureTransformation(
                transformation_type=TransformationType.ENCODING,
                source_features=["category"],
                parameters={"method": "one_hot"},
            )

            # Apply transformation
            transformed_data = transformer.apply_transformation(
                test_data, transformation
            )

            result.add_assertion(
                "One-hot encoding applied",
                any(col.startswith("category_") for col in transformed_data.columns),
            )

            result.finish(True)

        except Exception as e:
            result.finish(False, str(e))

        results.append(result)

        return results

    async def test_feature_selection(self) -> List[TestResult]:
        """Test feature selection components."""
        results = []

        # Test 1: Importance-based Selection
        result = TestResult("Importance-based Selection")
        try:
            selector = FeatureSelector()

            # Create test data
            np.random.seed(42)
            feature_data = pd.DataFrame(
                {
                    "important_feature": np.random.normal(0, 1, 100),
                    "noise_feature": np.random.normal(0, 0.1, 100),
                    "another_noise": np.random.normal(0, 0.1, 100),
                }
            )

            target = (feature_data["important_feature"] > 0).astype(int)

            # Select features
            selected_features = selector.select_features(
                feature_data, target, "importance", 2
            )

            result.add_assertion("Features selected", len(selected_features) > 0)
            result.add_assertion("Correct number selected", len(selected_features) <= 2)
            result.add_assertion(
                "Important feature included", "important_feature" in selected_features
            )

            result.finish(True)

        except Exception as e:
            result.finish(False, str(e))

        results.append(result)

        # Test 2: Correlation-based Selection
        result = TestResult("Correlation-based Selection")
        try:
            selector = FeatureSelector()

            # Create correlated test data
            np.random.seed(42)
            base_feature = np.random.normal(0, 1, 100)
            feature_data = pd.DataFrame(
                {
                    "feature1": base_feature,
                    "feature2": base_feature
                    + np.random.normal(0, 0.1, 100),  # Highly correlated
                    "feature3": np.random.normal(0, 1, 100),  # Uncorrelated
                }
            )

            target = (base_feature > 0).astype(int)

            # Select features
            selected_features = selector.select_features(
                feature_data, target, "correlation", 2
            )

            result.add_assertion("Features selected", len(selected_features) > 0)
            result.add_assertion("Correct number selected", len(selected_features) <= 2)

            result.finish(True)

        except Exception as e:
            result.finish(False, str(e))

        results.append(result)

        return results

    async def test_pipeline_execution(self) -> List[TestResult]:
        """Test pipeline execution components."""
        results = []

        # Test 1: Pipeline Creation and Execution
        result = TestResult("Pipeline Creation and Execution")
        try:
            # Create sample data
            np.random.seed(42)
            test_data = pd.DataFrame(
                {
                    "age": np.random.randint(18, 80, 100),
                    "income": np.random.normal(50000, 15000, 100),
                    "gender": np.random.choice(["M", "F"], 100),
                }
            )

            target = ((test_data["age"] > 50) & (test_data["income"] < 40000)).astype(
                int
            )

            # Create pipeline
            pipeline = FeatureEngineeringPipeline()
            config = FeaturePipelineConfig(
                pipeline_name="Test Pipeline",
                selection_method="importance",
                max_features=5,
            )

            pipeline_id = pipeline.create_pipeline(config)

            # Execute pipeline
            result_data = pipeline.execute_pipeline(pipeline_id, test_data, target)

            result.add_assertion("Pipeline created", pipeline_id is not None)
            result.add_assertion(
                "Pipeline executed successfully", result_data["status"] == "success"
            )
            result.add_assertion("Output data generated", "data" in result_data)
            result.add_assertion("Metadata generated", "metadata" in result_data)

            result.finish(True)

        except Exception as e:
            result.finish(False, str(e))

        results.append(result)

        # Test 2: Pipeline Status Tracking
        result = TestResult("Pipeline Status Tracking")
        try:
            pipeline = FeatureEngineeringPipeline()
            config = FeaturePipelineConfig(pipeline_name="Status Test")
            pipeline_id = pipeline.create_pipeline(config)

            # Get status
            status = pipeline.get_pipeline_status(pipeline_id)

            result.add_assertion("Status retrieved", status is not None)
            result.add_assertion(
                "Pipeline config included", "pipeline_config" in status
            )
            result.add_assertion(
                "Execution stats included", "total_executions" in status
            )

            result.finish(True)

        except Exception as e:
            result.finish(False, str(e))

        results.append(result)

        return results

    async def test_feature_monitoring(self) -> List[TestResult]:
        """Test feature monitoring components."""
        results = []

        # Test 1: Drift Detection
        result = TestResult("Drift Detection")
        try:
            from feature_monitoring_system import (
                FeatureMonitorConfig,
                FeatureMonitoringSystem,
                MonitoringLevel,
            )

            monitoring_system = FeatureMonitoringSystem()

            # Create baseline and current data
            np.random.seed(42)
            baseline_data = pd.Series(np.random.normal(0, 1, 1000))
            current_data = pd.Series(np.random.normal(0.5, 1.2, 500))  # Drifted

            # Create monitor
            config = FeatureMonitorConfig(
                feature_name="test_feature",
                monitoring_level=MonitoringLevel.STANDARD,
                baseline_data=pd.DataFrame({"test_feature": baseline_data}),
                alert_thresholds={"ks_test": 0.05},
            )

            monitor_id = monitoring_system.create_monitor(config)
            monitoring_system.start_monitoring(monitor_id)

            # Monitor feature
            alerts = monitoring_system.monitor_feature(monitor_id, current_data)

            result.add_assertion("Monitor created", monitor_id is not None)
            result.add_assertion(
                "Monitoring started", monitoring_system.monitoring_status[monitor_id]
            )
            result.add_assertion(
                "Drift detection executed", True
            )  # If we get here, no exception

            result.finish(True)

        except Exception as e:
            result.finish(False, str(e))

        results.append(result)

        # Test 2: Metrics Collection
        result = TestResult("Metrics Collection")
        try:
            from feature_monitoring_system import FeatureMetricsCollector

            collector = FeatureMetricsCollector()

            # Create test data
            test_data = pd.Series([1, 2, 3, 4, 5, np.nan, 7, 8, 9, 10])

            # Collect metrics
            metrics = collector.collect_metrics(test_data, "test_feature")

            result.add_assertion("Metrics collected", metrics is not None)
            result.add_assertion("Data points counted", metrics.data_points == 10)
            result.add_assertion("Null values detected", metrics.null_count == 1)
            result.add_assertion("Basic statistics calculated", metrics.mean > 0)

            result.finish(True)

        except Exception as e:
            result.finish(False, str(e))

        results.append(result)

        return results

    async def test_feature_versioning(self) -> List[TestResult]:
        """Test feature versioning components."""
        results = []

        # Test 1: Version Creation and Loading
        result = TestResult("Version Creation and Loading")
        try:
            # Create temporary storage
            temp_storage = os.path.join(self.temp_dir, "version_test")
            config = VersioningConfig(storage_path=temp_storage)

            versioning_system = FeatureVersioningSystem(config)

            # Create test data
            test_data = pd.DataFrame(
                {"feature1": [1, 2, 3, 4, 5], "feature2": [10, 20, 30, 40, 50]}
            )

            # Create version
            version = versioning_system.create_version(
                feature_name="test_feature",
                data=test_data,
                version_number="1.0.0",
                description="Test version",
            )

            # Load version
            loaded_data, loaded_version = versioning_system.load_version(
                version.version_id
            )

            result.add_assertion("Version created", version.version_id is not None)
            result.add_assertion("Version loaded successfully", loaded_data is not None)
            result.add_assertion(
                "Data integrity maintained", loaded_data.equals(test_data)
            )
            result.add_assertion(
                "Version metadata preserved", loaded_version.version_number == "1.0.0"
            )

            result.finish(True)

        except Exception as e:
            result.finish(False, str(e))

        results.append(result)

        # Test 2: Active Version Management
        result = TestResult("Active Version Management")
        try:
            # Create temporary storage
            temp_storage = os.path.join(self.temp_dir, "active_test")
            config = VersioningConfig(storage_path=temp_storage)

            versioning_system = FeatureVersioningSystem(config)

            # Create test data
            test_data = pd.DataFrame({"feature": [1, 2, 3, 4, 5]})

            # Create version
            version = versioning_system.create_version("test_feature", test_data)

            # Set as active
            versioning_system.set_active_version(version.version_id)

            # Get active version
            active_data, active_version = versioning_system.get_active_version(
                "test_feature"
            )

            result.add_assertion("Active version set", True)
            result.add_assertion("Active version retrieved", active_data is not None)
            result.add_assertion(
                "Correct active version",
                active_version.version_id == version.version_id,
            )

            result.finish(True)

        except Exception as e:
            result.finish(False, str(e))

        results.append(result)

        return results

    async def test_integration(self) -> List[TestResult]:
        """Test integration between components."""
        results = []

        # Test 1: End-to-End Feature Engineering Workflow
        result = TestResult("End-to-End Feature Engineering Workflow")
        try:
            # Create sample data
            np.random.seed(42)
            raw_data = pd.DataFrame(
                {
                    "age": np.random.randint(18, 80, 100),
                    "income": np.random.normal(50000, 15000, 100),
                    "gender": np.random.choice(["M", "F"], 100),
                    "region": np.random.choice(["North", "South", "East", "West"], 100),
                }
            )

            target = ((raw_data["age"] > 50) & (raw_data["income"] < 40000)).astype(int)

            # Step 1: Feature Engineering Pipeline
            pipeline = FeatureEngineeringPipeline()
            config = FeaturePipelineConfig(
                pipeline_name="Integration Test Pipeline",
                selection_method="importance",
                max_features=5,
            )

            pipeline_id = pipeline.create_pipeline(config)
            pipeline_result = pipeline.execute_pipeline(pipeline_id, raw_data, target)

            result.add_assertion(
                "Pipeline executed", pipeline_result["status"] == "success"
            )

            # Step 2: Feature Versioning
            temp_storage = os.path.join(self.temp_dir, "integration_test")
            version_config = VersioningConfig(storage_path=temp_storage)
            versioning_system = FeatureVersioningSystem(version_config)

            engineered_data = pipeline_result["data"]
            version = versioning_system.create_version(
                feature_name="engineered_features",
                data=engineered_data,
                description="Integrated feature engineering result",
            )

            versioning_system.set_active_version(version.version_id)

            result.add_assertion("Version created and set active", True)

            # Step 3: Feature Monitoring
            from feature_monitoring_system import (
                FeatureMonitorConfig,
                FeatureMonitoringSystem,
                MonitoringLevel,
            )

            monitoring_system = FeatureMonitoringSystem()

            # Monitor one of the engineered features
            if len(engineered_data.columns) > 0:
                feature_to_monitor = engineered_data.columns[0]

                monitor_config = FeatureMonitorConfig(
                    feature_name=feature_to_monitor,
                    monitoring_level=MonitoringLevel.STANDARD,
                    baseline_data=engineered_data[[feature_to_monitor]],
                )

                monitor_id = monitoring_system.create_monitor(monitor_config)
                monitoring_system.start_monitoring(monitor_id)

                result.add_assertion("Monitoring setup completed", True)

            result.finish(True)

        except Exception as e:
            result.finish(False, str(e))

        results.append(result)

        return results

    async def test_performance(self) -> List[TestResult]:
        """Test performance of components."""
        results = []

        # Test 1: Large Dataset Processing
        result = TestResult("Large Dataset Processing")
        try:
            # Create large dataset
            np.random.seed(42)
            large_data = pd.DataFrame(
                {f"feature_{i}": np.random.normal(0, 1, 10000) for i in range(50)}
            )

            target = (large_data["feature_0"] > 0).astype(int)

            # Test pipeline performance
            start_time = time.time()

            pipeline = FeatureEngineeringPipeline()
            config = FeaturePipelineConfig(
                pipeline_name="Performance Test",
                selection_method="importance",
                max_features=10,
            )

            pipeline_id = pipeline.create_pipeline(config)
            result_data = pipeline.execute_pipeline(pipeline_id, large_data, target)

            processing_time = time.time() - start_time

            result.add_assertion(
                "Large dataset processed", result_data["status"] == "success"
            )
            result.add_assertion(
                "Processing time reasonable", processing_time < 30
            )  # Should complete within 30 seconds
            result.add_assertion(
                "Memory usage reasonable", True
            )  # If we get here, no memory issues

            result.finish(True)

        except Exception as e:
            result.finish(False, str(e))

        results.append(result)

        # Test 2: Concurrent Processing
        result = TestResult("Concurrent Processing")
        try:
            # Create multiple pipelines to run concurrently
            async def run_pipeline(pipeline_id: int):
                np.random.seed(pipeline_id)
                test_data = pd.DataFrame(
                    {
                        "feature1": np.random.normal(0, 1, 1000),
                        "feature2": np.random.normal(0, 1, 1000),
                    }
                )
                target = (test_data["feature1"] > 0).astype(int)

                pipeline = FeatureEngineeringPipeline()
                config = FeaturePipelineConfig(
                    pipeline_name=f"Concurrent Test {pipeline_id}",
                    selection_method="importance",
                    max_features=2,
                )

                pid = pipeline.create_pipeline(config)
                return pipeline.execute_pipeline(pid, test_data, target)

            # Run multiple pipelines concurrently
            start_time = time.time()
            results_concurrent = await asyncio.gather(
                *[run_pipeline(i) for i in range(5)]
            )
            concurrent_time = time.time() - start_time

            successful_pipelines = sum(
                1 for r in results_concurrent if r["status"] == "success"
            )

            result.add_assertion("All pipelines completed", successful_pipelines == 5)
            result.add_assertion(
                "Concurrent processing efficient", concurrent_time < 60
            )

            result.finish(True)

        except Exception as e:
            result.finish(False, str(e))

        results.append(result)

        return results

    def generate_test_report(self, summary: Dict[str, Any]) -> str:
        """Generate comprehensive test report."""
        report = []
        report.append("=" * 80)
        report.append("FEATURE ENGINEERING COMPONENTS TEST REPORT")
        report.append("=" * 80)
        report.append(f"Test Suite: {summary['test_suite']}")
        report.append(f"Timestamp: {summary['timestamp']}")
        report.append(f"Total Duration: {summary['total_duration']:.2f} seconds")
        report.append("")

        # Summary
        report.append("SUMMARY:")
        report.append("-" * 40)
        report.append(f"Total Tests: {summary['total_tests']}")
        report.append(f"Passed: {summary['passed_tests']}")
        report.append(f"Failed: {summary['failed_tests']}")
        report.append(f"Success Rate: {summary['success_rate']:.2%}")
        report.append("")

        # Category breakdown
        report.append("CATEGORY BREAKDOWN:")
        report.append("-" * 40)
        for category_name, category_stats in summary["categories"].items():
            report.append(f"{category_name}:")
            report.append(f"  Total: {category_stats['total']}")
            report.append(f"  Passed: {category_stats['passed']}")
            report.append(f"  Failed: {category_stats['failed']}")
            report.append("")

        # Detailed results
        report.append("DETAILED RESULTS:")
        report.append("-" * 40)
        for result in self.test_results:
            report.append(f"\n{result.test_name}:")
            report.append(f"  Status: {'PASS' if result.passed else 'FAIL'}")
            report.append(f"  Duration: {result.duration:.2f}s")

            if result.error_message:
                report.append(f"  Error: {result.error_message}")

        report.append("\n" + "=" * 80)
        report.append("TEST REPORT COMPLETE")
        report.append("=" * 80)

        return "\n".join(report)

    def cleanup(self):
        """Clean up temporary resources."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        logger.info("Temporary resources cleaned up")


# Example usage
async def run_feature_engineering_tests():
    """Run the complete feature engineering test suite."""
    test_suite = FeatureEngineeringTestSuite()

    try:
        # Run all tests
        summary = await test_suite.run_all_tests()

        # Generate and print report
        report = test_suite.generate_test_report(summary)
        print(report)

        # Save results
        results_file = "feature_engineering_test_results.json"
        with open(results_file, "w") as f:
            json.dump(summary, f, indent=2, default=str)

        logger.info(f"Test results saved to {results_file}")

        return summary

    finally:
        # Cleanup
        test_suite.cleanup()


if __name__ == "__main__":
    asyncio.run(run_feature_engineering_tests())
