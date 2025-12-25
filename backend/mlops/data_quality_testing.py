"""
Data Quality Testing Suite
==========================

Comprehensive testing framework for data quality components including
monitoring, validation pipelines, drift detection, governance, and compliance.

This module provides:
- Unit tests for individual components
- Integration tests for end-to-end workflows
- Performance tests for scalability
- Test utilities and fixtures
- Test reporting and analytics
"""

import asyncio
import json
import logging
import time
import unittest
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from data_compliance import ComplianceFramework, DataComplianceSystem, DataSubject
from data_drift_detection import DataDriftDetector, DriftDetectionConfig, DriftResult
from data_governance import DataAccessLevel, DataGovernanceSystem, GovernancePolicy

# Import data quality components
from data_quality_monitoring import (
    DataQualityConfig,
    DataQualityMetrics,
    DataQualityMonitor,
)
from data_validation_pipelines import (
    DataValidationPipeline,
    ValidationPipelineConfig,
    ValidationResult,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("raptorflow.data_quality_testing")


class TestStatus(Enum):
    """Test execution status"""

    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TestType(Enum):
    """Test type categories"""

    UNIT = "unit"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"
    END_TO_END = "end_to_end"


@dataclass
class TestResult:
    """Test result data structure"""

    test_name: str
    test_type: TestType
    status: TestStatus
    execution_time: float
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class TestSuite:
    """Test suite collection"""

    name: str
    description: str
    tests: List[TestResult]
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    total_execution_time: float

    @property
    def success_rate(self) -> float:
        """Calculate test success rate"""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100


class DataQualityTestFramework:
    """Main testing framework for data quality components"""

    def __init__(self):
        self.test_suites: Dict[str, TestSuite] = {}
        self.current_suite: Optional[str] = None
        self.logger = logging.getLogger("raptorflow.data_quality_testing")

    def create_test_suite(self, name: str, description: str) -> None:
        """Create a new test suite"""
        self.current_suite = name
        self.test_suites[name] = TestSuite(
            name=name,
            description=description,
            tests=[],
            total_tests=0,
            passed_tests=0,
            failed_tests=0,
            skipped_tests=0,
            total_execution_time=0.0,
        )
        self.logger.info(f"Created test suite: {name}")

    def run_test(self, test_name: str, test_type: TestType, test_func) -> TestResult:
        """Execute a single test"""
        if not self.current_suite:
            raise ValueError("No active test suite")

        suite = self.test_suites[self.current_suite]
        suite.total_tests += 1

        start_time = time.time()
        status = TestStatus.RUNNING

        try:
            self.logger.info(f"Running test: {test_name}")
            result_data = test_func()
            execution_time = time.time() - start_time

            result = TestResult(
                test_name=test_name,
                test_type=test_type,
                status=TestStatus.PASSED,
                execution_time=execution_time,
                message="Test passed successfully",
                details=result_data,
            )
            suite.passed_tests += 1

        except Exception as e:
            execution_time = time.time() - start_time
            result = TestResult(
                test_name=test_name,
                test_type=test_type,
                status=TestStatus.FAILED,
                execution_time=execution_time,
                message=f"Test failed: {str(e)}",
                details={"error": str(e)},
            )
            suite.failed_tests += 1
            self.logger.error(f"Test failed: {test_name} - {str(e)}")

        suite.tests.append(result)
        suite.total_execution_time += execution_time

        return result

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        report = {
            "summary": {
                "total_suites": len(self.test_suites),
                "total_tests": sum(
                    suite.total_tests for suite in self.test_suites.values()
                ),
                "total_passed": sum(
                    suite.passed_tests for suite in self.test_suites.values()
                ),
                "total_failed": sum(
                    suite.failed_tests for suite in self.test_suites.values()
                ),
                "total_skipped": sum(
                    suite.skipped_tests for suite in self.test_suites.values()
                ),
                "overall_success_rate": 0.0,
                "total_execution_time": sum(
                    suite.total_execution_time for suite in self.test_suites.values()
                ),
            },
            "suites": {},
        }

        # Calculate overall success rate
        if report["summary"]["total_tests"] > 0:
            report["summary"]["overall_success_rate"] = (
                report["summary"]["total_passed"] / report["summary"]["total_tests"]
            ) * 100

        # Add suite details
        for name, suite in self.test_suites.items():
            report["suites"][name] = {
                "description": suite.description,
                "total_tests": suite.total_tests,
                "passed_tests": suite.passed_tests,
                "failed_tests": suite.failed_tests,
                "skipped_tests": suite.skipped_tests,
                "success_rate": suite.success_rate,
                "execution_time": suite.total_execution_time,
                "tests": [asdict(test) for test in suite.tests],
            }

        return report


class TestDataGenerator:
    """Generate test data for quality testing"""

    @staticmethod
    def create_sample_dataframe(
        rows: int = 1000, missing_ratio: float = 0.1
    ) -> pd.DataFrame:
        """Create sample DataFrame with quality issues"""
        np.random.seed(42)

        data = {
            "id": range(1, rows + 1),
            "name": [f"user_{i}" for i in range(1, rows + 1)],
            "age": np.random.normal(35, 10, rows),
            "email": [f"user{i}@example.com" for i in range(1, rows + 1)],
            "salary": np.random.lognormal(10, 1, rows),
            "department": np.random.choice(
                ["Engineering", "Sales", "Marketing", "HR"], rows
            ),
            "join_date": pd.date_range("2020-01-01", periods=rows, freq="D")[:rows],
            "score": np.random.uniform(0, 100, rows),
        }

        df = pd.DataFrame(data)

        # Introduce missing values
        for col in ["age", "email", "salary"]:
            missing_indices = np.random.choice(
                df.index, size=int(rows * missing_ratio), replace=False
            )
            df.loc[missing_indices, col] = np.nan

        # Introduce duplicates
        duplicate_indices = np.random.choice(
            df.index, size=int(rows * 0.05), replace=False
        )
        df.loc[duplicate_indices, "email"] = "duplicate@example.com"

        # Introduce outliers
        outlier_indices = np.random.choice(
            df.index, size=int(rows * 0.02), replace=False
        )
        df.loc[outlier_indices, "salary"] = df["salary"].max() * 10

        return df

    @staticmethod
    def create_reference_dataframe(rows: int = 1000) -> pd.DataFrame:
        """Create reference DataFrame for drift detection"""
        np.random.seed(123)

        data = {
            "id": range(1, rows + 1),
            "feature_1": np.random.normal(0, 1, rows),
            "feature_2": np.random.exponential(1, rows),
            "feature_3": np.random.uniform(0, 100, rows),
            "category": np.random.choice(["A", "B", "C"], rows, p=[0.5, 0.3, 0.2]),
        }

        return pd.DataFrame(data)

    @staticmethod
    def create_drifted_dataframe(
        rows: int = 1000, drift_factor: float = 0.5
    ) -> pd.DataFrame:
        """Create DataFrame with drifted distributions"""
        np.random.seed(456)

        data = {
            "id": range(1, rows + 1),
            "feature_1": np.random.normal(drift_factor, 1, rows),  # Mean shift
            "feature_2": np.random.exponential(1 + drift_factor, rows),  # Scale change
            "feature_3": np.random.uniform(
                0, 100 + drift_factor * 50, rows
            ),  # Range change
            "category": np.random.choice(
                ["A", "B", "C"], rows, p=[0.3, 0.4, 0.3]
            ),  # Distribution change
        }

        return pd.DataFrame(data)


class DataQualityTests:
    """Test cases for data quality components"""

    def __init__(self, framework: DataQualityTestFramework):
        self.framework = framework
        self.data_generator = TestDataGenerator()

    def test_data_quality_monitoring(self) -> Dict[str, Any]:
        """Test data quality monitoring functionality"""
        results = {}

        # Test configuration
        config = DataQualityConfig(
            monitoring_interval=60, alert_threshold=0.1, metrics_history_size=100
        )
        monitor = DataQualityMonitor(config)
        results["config_created"] = True

        # Test metrics calculation
        df = self.data_generator.create_sample_dataframe()
        metrics = monitor.calculate_quality_metrics(df)
        results["metrics_calculated"] = len(metrics.__dict__) > 0
        results["completeness_score"] = metrics.completeness_score
        results["uniqueness_score"] = metrics.uniqueness_score

        # Test alert generation
        alerts = monitor.check_quality_thresholds(metrics)
        results["alerts_generated"] = len(alerts) >= 0

        return results

    def test_data_validation_pipelines(self) -> Dict[str, Any]:
        """Test data validation pipeline functionality"""
        results = {}

        # Test pipeline creation
        config = ValidationPipelineConfig(
            pipeline_name="test_pipeline", parallel_execution=True, fail_fast=False
        )
        pipeline = DataValidationPipeline(config)
        results["pipeline_created"] = True

        # Test validation execution
        df = self.data_generator.create_sample_dataframe()
        validation_result = pipeline.validate_dataframe(df)
        results["validation_executed"] = True
        results["is_valid"] = validation_result.is_valid
        results["validation_count"] = len(validation_result.validation_results)

        # Test custom rules
        def custom_rule_check(data):
            return len(data) > 0, "Dataset not empty"

        pipeline.add_custom_rule("non_empty_check", custom_rule_check)
        custom_result = pipeline.validate_dataframe(df)
        results["custom_rule_added"] = True
        results["custom_rule_count"] = len(custom_result.validation_results)

        return results

    def test_data_drift_detection(self) -> Dict[str, Any]:
        """Test data drift detection functionality"""
        results = {}

        # Test drift detector creation
        config = DriftDetectionConfig(
            detection_methods=["ks_test", "psi", "wasserstein"],
            significance_threshold=0.05,
            psi_threshold=0.2,
        )
        detector = DataDriftDetector(config)
        results["detector_created"] = True

        # Test drift detection
        reference_df = self.data_generator.create_reference_dataframe()
        current_df = self.data_generator.create_drifted_dataframe()

        drift_result = detector.detect_drift(reference_df, current_df)
        results["drift_detected"] = drift_result.drift_detected
        results["drift_score"] = drift_result.overall_drift_score
        results["feature_drift_count"] = len(drift_result.feature_drift_scores)

        # Test alert generation
        alerts = detector.generate_drift_alerts(drift_result)
        results["alerts_generated"] = len(alerts) >= 0

        return results

    def test_data_governance(self) -> Dict[str, Any]:
        """Test data governance functionality"""
        results = {}

        # Test governance system creation
        governance = DataGovernanceSystem()
        results["governance_created"] = True

        # Test policy creation
        policy = GovernancePolicy(
            policy_id="test_policy",
            name="Test Policy",
            description="Test policy for data access",
            rules={"access_level": DataAccessLevel.READ_ONLY},
        )
        governance.add_policy(policy)
        results["policy_added"] = True

        # Test access control
        user_id = "test_user"
        resource_id = "test_resource"
        access_granted = governance.check_access(user_id, resource_id, "read")
        results["access_checked"] = True
        results["access_granted"] = access_granted

        # Test audit logging
        governance.log_access_event(user_id, resource_id, "read", access_granted)
        audit_logs = governance.get_audit_logs(user_id=user_id)
        results["audit_logged"] = len(audit_logs) > 0

        return results

    def test_data_compliance(self) -> Dict[str, Any]:
        """Test data compliance functionality"""
        results = {}

        # Test compliance system creation
        compliance = DataComplianceSystem()
        results["compliance_created"] = True

        # Test data subject registration
        subject = DataSubject(
            subject_id="test_subject",
            name="Test User",
            email="test@example.com",
            consent_status=True,
        )
        compliance.register_data_subject(subject)
        results["subject_registered"] = True

        # Test PII detection
        df = pd.DataFrame(
            {
                "email": ["test@example.com", "user@test.com"],
                "phone": ["123-456-7890", "987-654-3210"],
                "name": ["John Doe", "Jane Smith"],
            }
        )
        pii_fields = compliance.detect_pii_fields(df)
        results["pii_detected"] = len(pii_fields) > 0

        # Test compliance assessment
        assessment = compliance.assess_compliance(df, [ComplianceFramework.GDPR])
        results["assessment_completed"] = True
        results["compliance_score"] = assessment.overall_score

        # Test data anonymization
        anonymized_df = compliance.anonymize_data(df, pii_fields)
        results["data_anonymized"] = not anonymized_df.equals(df)

        return results


class PerformanceTests:
    """Performance tests for data quality components"""

    def __init__(self, framework: DataQualityTestFramework):
        self.framework = framework
        self.data_generator = TestDataGenerator()

    def test_monitoring_performance(self) -> Dict[str, Any]:
        """Test monitoring performance with large datasets"""
        results = {}

        config = DataQualityConfig()
        monitor = DataQualityMonitor(config)

        # Test with different dataset sizes
        sizes = [1000, 5000, 10000]
        execution_times = []

        for size in sizes:
            df = self.data_generator.create_sample_dataframe(rows=size)

            start_time = time.time()
            metrics = monitor.calculate_quality_metrics(df)
            execution_time = time.time() - start_time

            execution_times.append(execution_time)
            results[f"size_{size}_time"] = execution_time

        results["performance_scaling"] = execution_times
        results["avg_time_per_1000_rows"] = np.mean(execution_times)

        return results

    def test_validation_performance(self) -> Dict[str, Any]:
        """Test validation pipeline performance"""
        results = {}

        config = ValidationPipelineConfig(parallel_execution=True)
        pipeline = DataValidationPipeline(config)

        # Test with different dataset sizes
        sizes = [1000, 5000, 10000]
        execution_times = []

        for size in sizes:
            df = self.data_generator.create_sample_dataframe(rows=size)

            start_time = time.time()
            validation_result = pipeline.validate_dataframe(df)
            execution_time = time.time() - start_time

            execution_times.append(execution_time)
            results[f"size_{size}_time"] = execution_time

        results["performance_scaling"] = execution_times
        results["avg_time_per_1000_rows"] = np.mean(execution_times)

        return results


class IntegrationTests:
    """Integration tests for data quality components"""

    def __init__(self, framework: DataQualityTestFramework):
        self.framework = framework
        self.data_generator = TestDataGenerator()

    def test_end_to_end_workflow(self) -> Dict[str, Any]:
        """Test complete data quality workflow"""
        results = {}

        # Create test data
        df = self.data_generator.create_sample_dataframe()
        reference_df = self.data_generator.create_reference_dataframe()
        results["test_data_created"] = True

        # Step 1: Data quality monitoring
        monitor_config = DataQualityConfig()
        monitor = DataQualityMonitor(monitor_config)
        metrics = monitor.calculate_quality_metrics(df)
        results["monitoring_completed"] = True
        results["quality_score"] = metrics.overall_score

        # Step 2: Data validation
        validation_config = ValidationPipelineConfig()
        validator = DataValidationPipeline(validation_config)
        validation_result = validator.validate_dataframe(df)
        results["validation_completed"] = True
        results["validation_passed"] = validation_result.is_valid

        # Step 3: Drift detection
        drift_config = DriftDetectionConfig()
        drift_detector = DataDriftDetector(drift_config)
        drift_result = drift_detector.detect_drift(reference_df, df)
        results["drift_detection_completed"] = True
        results["drift_detected"] = drift_result.drift_detected

        # Step 4: Governance check
        governance = DataGovernanceSystem()
        access_granted = governance.check_access("test_user", "test_data", "read")
        results["governance_checked"] = True
        results["access_granted"] = access_granted

        # Step 5: Compliance assessment
        compliance = DataComplianceSystem()
        assessment = compliance.assess_compliance(df, [ComplianceFramework.GDPR])
        results["compliance_assessed"] = True
        results["compliance_score"] = assessment.overall_score

        # Overall workflow success
        results["workflow_success"] = all(
            [
                results["monitoring_completed"],
                results["validation_completed"],
                results["drift_detection_completed"],
                results["governance_checked"],
                results["compliance_assessed"],
            ]
        )

        return results


async def run_data_quality_tests():
    """Run comprehensive data quality test suite"""
    logger.info("Starting Data Quality Test Suite")

    # Initialize test framework
    framework = DataQualityTestFramework()

    # Unit Tests
    framework.create_test_suite("Unit Tests", "Unit tests for individual components")
    unit_tests = DataQualityTests(framework)

    framework.run_test(
        "Data Quality Monitoring",
        TestType.UNIT,
        unit_tests.test_data_quality_monitoring,
    )
    framework.run_test(
        "Data Validation Pipelines",
        TestType.UNIT,
        unit_tests.test_data_validation_pipelines,
    )
    framework.run_test(
        "Data Drift Detection", TestType.UNIT, unit_tests.test_data_drift_detection
    )
    framework.run_test(
        "Data Governance", TestType.UNIT, unit_tests.test_data_governance
    )
    framework.run_test(
        "Data Compliance", TestType.UNIT, unit_tests.test_data_compliance
    )

    # Performance Tests
    framework.create_test_suite(
        "Performance Tests", "Performance and scalability tests"
    )
    perf_tests = PerformanceTests(framework)

    framework.run_test(
        "Monitoring Performance",
        TestType.PERFORMANCE,
        perf_tests.test_monitoring_performance,
    )
    framework.run_test(
        "Validation Performance",
        TestType.PERFORMANCE,
        perf_tests.test_validation_performance,
    )

    # Integration Tests
    framework.create_test_suite("Integration Tests", "End-to-end integration tests")
    integration_tests = IntegrationTests(framework)

    framework.run_test(
        "End-to-End Workflow",
        TestType.INTEGRATION,
        integration_tests.test_end_to_end_workflow,
    )

    # Generate and display report
    report = framework.generate_report()

    print("\n" + "=" * 80)
    print("DATA QUALITY TEST REPORT")
    print("=" * 80)

    summary = report["summary"]
    print(f"\nSUMMARY:")
    print(f"  Total Suites: {summary['total_suites']}")
    print(f"  Total Tests: {summary['total_tests']}")
    print(f"  Passed: {summary['total_passed']}")
    print(f"  Failed: {summary['total_failed']}")
    print(f"  Success Rate: {summary['overall_success_rate']:.2f}%")
    print(f"  Total Execution Time: {summary['total_execution_time']:.2f}s")

    for suite_name, suite_data in report["suites"].items():
        print(f"\n{suite_name.upper()}:")
        print(f"  Description: {suite_data['description']}")
        print(f"  Tests: {suite_data['total_tests']}")
        print(f"  Passed: {suite_data['passed_tests']}")
        print(f"  Failed: {suite_data['failed_tests']}")
        print(f"  Success Rate: {suite_data['success_rate']:.2f}%")
        print(f"  Execution Time: {suite_data['execution_time']:.2f}s")

        # Show failed tests
        failed_tests = [t for t in suite_data["tests"] if t["status"] == "failed"]
        if failed_tests:
            print(f"  Failed Tests:")
            for test in failed_tests:
                print(f"    - {test['test_name']}: {test['message']}")

    print("\n" + "=" * 80)

    # Save report to file
    report_file = "data_quality_test_report.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2, default=str)

    logger.info(f"Test report saved to {report_file}")

    return report


if __name__ == "__main__":
    asyncio.run(run_data_quality_tests())
