"""
Regression Test Framework with Automated Diff Analysis and Change Detection

Comprehensive regression testing for RaptorFlow backend:
- Automated diff analysis between versions
- Change detection and impact assessment
- Regression test suite execution
- Performance regression detection
- Breaking change identification
"""

import pytest

pytest.skip(
    "Archived manual test script; use explicit run if needed.", allow_module_level=True
)

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
import yaml
from deepdiff import DeepDiff
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ChangeImpact(Enum):
    """Change impact levels."""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RegressionType(Enum):
    """Regression test types."""

    API_RESPONSE = "api_response"
    PERFORMANCE = "performance"
    FUNCTIONALITY = "functionality"
    SECURITY = "security"
    SCHEMA = "schema"


@dataclass
class ChangeDetection:
    """Detected change between versions."""

    change_type: str
    path: str
    old_value: Any
    new_value: Any
    impact: ChangeImpact
    description: str
    breaking: bool = False


@dataclass
class RegressionTest:
    """Regression test result."""

    name: str
    type: RegressionType
    passed: bool
    duration: float
    baseline_result: Optional[Any] = None
    current_result: Optional[Any] = None
    differences: List[ChangeDetection] = field(default_factory=list)
    performance_impact: Optional[float] = None


@dataclass
class RegressionReport:
    """Regression test report."""

    timestamp: datetime
    baseline_version: str
    current_version: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    performance_regressions: int
    breaking_changes: int
    test_results: List[RegressionTest] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)


class RegressionTestConfig(BaseModel):
    """Regression test configuration."""

    baseline_spec_path: str = "docs/openapi_baseline.yaml"
    current_spec_path: str = "docs/openapi_comprehensive.yaml"
    baseline_results_dir: str = "test_results/baseline"
    current_results_dir: str = "test_results/current"
    output_dir: str = "regression_results"
    base_url: str = "http://localhost:8000"
    performance_threshold: float = 10.0  # percentage
    timeout: int = 30
    parallel_tests: int = 5


class RegressionTestFramework:
    """Comprehensive regression test framework."""

    def __init__(self, config: RegressionTestConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.baseline_spec: Dict[str, Any] = {}
        self.current_spec: Dict[str, Any] = {}
        self.baseline_results: Dict[str, Any] = {}
        self.current_results: Dict[str, Any] = {}

        # Create output directory
        Path(config.output_dir).mkdir(parents=True, exist_ok=True)

        # Load specifications and baseline results
        self._load_specifications()
        self._load_baseline_results()

    async def __aenter__(self):
        """Async context manager entry."""
        await self._setup_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def _setup_session(self) -> None:
        """Setup HTTP session."""
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        connector = aiohttp.TCPConnector(limit=self.config.parallel_tests * 2)

        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={"User-Agent": "RaptorFlow-Regression-Test/1.0"},
        )

    def _load_specifications(self) -> None:
        """Load OpenAPI specifications."""
        try:
            # Load baseline specification
            if Path(self.config.baseline_spec_path).exists():
                with open(self.config.baseline_spec_path, "r") as f:
                    self.baseline_spec = yaml.safe_load(f)
                logger.info(f"Loaded baseline spec: {self.config.baseline_spec_path}")

            # Load current specification
            with open(self.config.current_spec_path, "r") as f:
                self.current_spec = yaml.safe_load(f)
            logger.info(f"Loaded current spec: {self.config.current_spec_path}")

        except Exception as e:
            logger.error(f"Failed to load specifications: {e}")
            raise

    def _load_baseline_results(self) -> None:
        """Load baseline test results."""
        baseline_dir = Path(self.config.baseline_results_dir)
        if baseline_dir.exists():
            for result_file in baseline_dir.glob("*.json"):
                try:
                    with open(result_file, "r") as f:
                        self.baseline_results[result_file.stem] = json.load(f)
                except Exception as e:
                    logger.warning(f"Failed to load baseline result {result_file}: {e}")

    def detect_spec_changes(self) -> List[ChangeDetection]:
        """Detect changes between OpenAPI specifications."""
        changes = []

        diff = DeepDiff(self.baseline_spec, self.current_spec, ignore_order=True)

        # Handle added endpoints
        if "dictionary_item_added" in diff:
            for item in diff["dictionary_item_added"]:
                if "paths" in item:
                    changes.append(
                        ChangeDetection(
                            change_type="endpoint_added",
                            path=item,
                            old_value=None,
                            new_value="added",
                            impact=ChangeImpact.LOW,
                            description=f"New endpoint added: {item}",
                            breaking=False,
                        )
                    )

        # Handle removed endpoints
        if "dictionary_item_removed" in diff:
            for item in diff["dictionary_item_removed"]:
                if "paths" in item:
                    changes.append(
                        ChangeDetection(
                            change_type="endpoint_removed",
                            path=item,
                            old_value="removed",
                            new_value=None,
                            impact=ChangeImpact.CRITICAL,
                            description=f"Endpoint removed: {item}",
                            breaking=True,
                        )
                    )

        # Handle changed endpoints
        if "values_changed" in diff:
            for item in diff["values_changed"]:
                if "paths" in item:
                    changes.append(
                        ChangeDetection(
                            change_type="endpoint_modified",
                            path=item,
                            old_value=item["old_value"],
                            new_value=item["new_value"],
                            impact=ChangeImpact.MEDIUM,
                            description=f"Endpoint modified: {item}",
                            breaking=self._is_breaking_change(item),
                        )
                    )

        # Handle type changes
        if "type_changes" in diff:
            for item in diff["type_changes"]:
                if "paths" in item:
                    changes.append(
                        ChangeDetection(
                            change_type="type_changed",
                            path=item,
                            old_value=item["old_type"],
                            new_value=item["new_type"],
                            impact=ChangeImpact.HIGH,
                            description=f"Type changed: {item}",
                            breaking=True,
                        )
                    )

        return changes

    def _is_breaking_change(self, change_item: Dict[str, Any]) -> bool:
        """Determine if a change is breaking."""
        # Simplified breaking change detection
        breaking_indicators = ["required", "status", "method", "parameters"]

        path = change_item.get("path", "")
        return any(indicator in path for indicator in breaking_indicators)

    async def run_api_regression_tests(self) -> List[RegressionTest]:
        """Run API regression tests."""
        logger.info("Running API regression tests")

        tests = []

        # Get common endpoints
        baseline_paths = self.baseline_spec.get("paths", {})
        current_paths = self.current_spec.get("paths", {})
        common_paths = set(baseline_paths.keys()) & set(current_paths.keys())

        for path in common_paths:
            baseline_methods = baseline_paths[path]
            current_methods = current_paths[path]
            common_methods = set(baseline_methods.keys()) & set(current_methods.keys())

            for method in common_methods:
                test_name = f"{method.upper()} {path}"

                # Run test
                test = await self._run_single_api_test(
                    test_name,
                    method.upper(),
                    path,
                    self.baseline_results.get(
                        f"{method.lower()}_{path.replace('/', '_')}"
                    ),
                    self.current_results.get(
                        f"{method.lower()}_{path.replace('/', '_')}"
                    ),
                )

                tests.append(test)

        return tests

    async def _run_single_api_test(
        self,
        test_name: str,
        method: str,
        endpoint: str,
        baseline_result: Optional[Dict[str, Any]],
        current_result: Optional[Dict[str, Any]],
    ) -> RegressionTest:
        """Run single API regression test."""
        start_time = time.time()

        try:
            # Make current API call
            url = f"{self.config.base_url}{endpoint}"

            async with self.session.request(method, url) as response:
                current_data = await response.json()
                current_status = response.status
                current_time = time.time() - start_time

            # Compare with baseline
            differences = []
            performance_impact = None

            if baseline_result:
                baseline_data = baseline_result.get("response_data", {})
                baseline_time = baseline_result.get("response_time", 0)

                # Compare response data
                data_diff = DeepDiff(baseline_data, current_data, ignore_order=True)
                if data_diff:
                    for change_type, changes in data_diff.items():
                        for change in changes:
                            if isinstance(change, dict):
                                path = change.get("path", "")
                                differences.append(
                                    ChangeDetection(
                                        change_type=change_type,
                                        path=path,
                                        old_value=change.get("old_value"),
                                        new_value=change.get("new_value"),
                                        impact=self._assess_change_impact(
                                            change_type, path
                                        ),
                                        description=f"Response change: {change_type} at {path}",
                                    )
                                )

                # Compare performance
                if baseline_time > 0:
                    performance_change = (
                        (current_time - baseline_time) / baseline_time
                    ) * 100
                    if abs(performance_change) > self.config.performance_threshold:
                        performance_impact = performance_change

            # Determine test result
            passed = len(differences) == 0 and (
                performance_impact is None
                or abs(performance_impact) <= self.config.performance_threshold
            )

            return RegressionTest(
                name=test_name,
                type=RegressionType.API_RESPONSE,
                passed=passed,
                duration=current_time,
                baseline_result=baseline_result,
                current_result=current_data,
                differences=differences,
                performance_impact=performance_impact,
            )

        except Exception as e:
            return RegressionTest(
                name=test_name,
                type=RegressionType.API_RESPONSE,
                passed=False,
                duration=time.time() - start_time,
                current_result={"error": str(e)},
            )

    def _assess_change_impact(self, change_type: str, path: str) -> ChangeImpact:
        """Assess the impact of a change."""
        if change_type in ["dictionary_item_removed", "type_changes"]:
            return ChangeImpact.HIGH
        elif change_type in ["values_changed"]:
            if "status" in path or "required" in path:
                return ChangeImpact.HIGH
            else:
                return ChangeImpact.MEDIUM
        elif change_type in ["dictionary_item_added"]:
            return ChangeImpact.LOW
        else:
            return ChangeImpact.NONE

    async def run_performance_regression_tests(self) -> List[RegressionTest]:
        """Run performance regression tests."""
        logger.info("Running performance regression tests")

        tests = []

        # Test key endpoints for performance
        performance_endpoints = [
            ("GET", "/health"),
            ("GET", "/users/me"),
            ("GET", "/workspaces"),
            ("POST", "/auth/login"),
        ]

        for method, endpoint in performance_endpoints:
            test_name = f"Performance {method.upper()} {endpoint}"

            # Run multiple iterations
            times = []
            for _ in range(5):
                start_time = time.time()
                try:
                    url = f"{self.config.base_url}{endpoint}"
                    data = (
                        {"email": "test@example.com", "password": "test"}
                        if method == "POST"
                        else None
                    )

                    async with self.session.request(method, url, json=data) as response:
                        await response.text()  # Consume response
                        times.append(time.time() - start_time)

                except Exception as e:
                    logger.error(f"Performance test failed for {test_name}: {e}")
                    times.append(float("inf"))

            # Calculate metrics
            valid_times = [t for t in times if t != float("inf")]
            if valid_times:
                avg_time = sum(valid_times) / len(valid_times)
                baseline_avg = self.baseline_results.get(
                    f"perf_{method}_{endpoint}", {}
                ).get("avg_time", avg_time)

                performance_change = (
                    ((avg_time - baseline_avg) / baseline_avg) * 100
                    if baseline_avg > 0
                    else 0
                )

                passed = abs(performance_change) <= self.config.performance_threshold

                tests.append(
                    RegressionTest(
                        name=test_name,
                        type=RegressionType.PERFORMANCE,
                        passed=passed,
                        duration=avg_time,
                        baseline_result=baseline_avg,
                        current_result=avg_time,
                        performance_impact=performance_change,
                    )
                )

        return tests

    def run_schema_regression_tests(self) -> List[RegressionTest]:
        """Run schema regression tests."""
        logger.info("Running schema regression tests")

        tests = []

        # Compare OpenAPI schemas
        baseline_paths = self.baseline_spec.get("paths", {})
        current_paths = self.current_spec.get("paths", {})

        for path in set(baseline_paths.keys()) | set(current_paths.keys()):
            baseline_methods = baseline_paths.get(path, {})
            current_methods = current_paths.get(path, {})

            for method in set(baseline_methods.keys()) | set(current_methods.keys()):
                test_name = f"Schema {method.upper()} {path}"

                baseline_details = baseline_methods.get(method, {})
                current_details = current_methods.get(method, {})

                # Compare schemas
                differences = []
                if baseline_details and current_details:
                    baseline_responses = baseline_details.get("responses", {})
                    current_responses = current_details.get("responses", {})

                    for status_code in set(baseline_responses.keys()) | set(
                        current_responses.keys()
                    ):
                        baseline_schema = (
                            baseline_responses.get(status_code, {})
                            .get("content", {})
                            .get("application/json", {})
                            .get("schema", {})
                        )
                        current_schema = (
                            current_responses.get(status_code, {})
                            .get("content", {})
                            .get("application/json", {})
                            .get("schema", {})
                        )

                        if baseline_schema and current_schema:
                            schema_diff = DeepDiff(
                                baseline_schema, current_schema, ignore_order=True
                            )
                            if schema_diff:
                                for change_type, changes in schema_diff.items():
                                    for change in changes:
                                        differences.append(
                                            ChangeDetection(
                                                change_type=change_type,
                                                path=f"{path}.{method}.{status_code}",
                                                old_value=(
                                                    change.get("old_value")
                                                    if isinstance(change, dict)
                                                    else change
                                                ),
                                                new_value=(
                                                    change.get("new_value")
                                                    if isinstance(change, dict)
                                                    else change
                                                ),
                                                impact=self._assess_change_impact(
                                                    change_type,
                                                    f"{path}.{method}.{status_code}",
                                                ),
                                                description=f"Schema change for {status_code}",
                                            )
                                        )

                passed = len(differences) == 0

                tests.append(
                    RegressionTest(
                        name=test_name,
                        type=RegressionType.SCHEMA,
                        passed=passed,
                        duration=0.0,
                        differences=differences,
                    )
                )

        return tests

    async def run_all_regression_tests(self) -> RegressionReport:
        """Run all regression tests."""
        logger.info("Starting comprehensive regression testing")

        # Detect specification changes
        spec_changes = self.detect_spec_changes()

        # Run different types of regression tests
        api_tests = await self.run_api_regression_tests()
        performance_tests = await self.run_performance_regression_tests()
        schema_tests = self.run_schema_regression_tests()

        # Combine all test results
        all_tests = api_tests + performance_tests + schema_tests

        # Calculate summary statistics
        total_tests = len(all_tests)
        passed_tests = sum(1 for test in all_tests if test.passed)
        failed_tests = total_tests - passed_tests
        performance_regressions = sum(
            1
            for test in all_tests
            if test.performance_impact
            and abs(test.performance_impact) > self.config.performance_threshold
        )
        breaking_changes = sum(
            1 for test in all_tests if any(diff.breaking for diff in test.differences)
        )

        # Create report
        report = RegressionReport(
            timestamp=datetime.now(),
            baseline_version="baseline",
            current_version="current",
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            performance_regressions=performance_regressions,
            breaking_changes=breaking_changes,
            test_results=all_tests,
            summary={
                "spec_changes": len(spec_changes),
                "breaking_spec_changes": sum(
                    1 for change in spec_changes if change.breaking
                ),
                "success_rate": (
                    (passed_tests / total_tests * 100) if total_tests > 0 else 0
                ),
                "high_impact_changes": sum(
                    1
                    for test in all_tests
                    for diff in test.differences
                    if diff.impact == ChangeImpact.HIGH
                ),
                "critical_impact_changes": sum(
                    1
                    for test in all_tests
                    for diff in test.differences
                    if diff.impact == ChangeImpact.CRITICAL
                ),
            },
        )

        return report

    def generate_regression_report(self, report: RegressionReport) -> Dict[str, Any]:
        """Generate comprehensive regression report."""
        return {
            "metadata": {
                "timestamp": report.timestamp.isoformat(),
                "baseline_version": report.baseline_version,
                "current_version": report.current_version,
                "test_duration": sum(test.duration for test in report.test_results),
            },
            "summary": {
                "total_tests": report.total_tests,
                "passed_tests": report.passed_tests,
                "failed_tests": report.failed_tests,
                "success_rate": (
                    (report.passed_tests / report.total_tests * 100)
                    if report.total_tests > 0
                    else 0
                ),
                "performance_regressions": report.performance_regressions,
                "breaking_changes": report.breaking_changes,
                **report.summary,
            },
            "test_results": [
                {
                    "name": test.name,
                    "type": test.type.value,
                    "passed": test.passed,
                    "duration": test.duration,
                    "performance_impact": test.performance_impact,
                    "differences": [
                        {
                            "change_type": diff.change_type,
                            "path": diff.path,
                            "old_value": diff.old_value,
                            "new_value": diff.new_value,
                            "impact": diff.impact.value,
                            "breaking": diff.breaking,
                            "description": diff.description,
                        }
                        for diff in test.differences
                    ],
                }
                for test in report.test_results
            ],
            "spec_changes": [
                {
                    "change_type": change.change_type,
                    "path": change.path,
                    "old_value": change.old_value,
                    "new_value": change.new_value,
                    "impact": change.impact.value,
                    "breaking": change.breaking,
                    "description": change.description,
                }
                for change in self.detect_spec_changes()
            ],
            "recommendations": self._generate_recommendations(report),
        }

    def _generate_recommendations(self, report: RegressionReport) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []

        if report.failed_tests > 0:
            recommendations.append(
                f"Address {report.failed_tests} failing regression tests before deployment"
            )

        if report.performance_regressions > 0:
            recommendations.append(
                f"Investigate {report.performance_regressions} performance regressions"
            )

        if report.breaking_changes > 0:
            recommendations.append(
                f"Review {report.breaking_changes} breaking changes and update documentation"
            )

        if report.summary.get("critical_impact_changes", 0) > 0:
            recommendations.append(
                "Critical changes detected - consider version bump and migration guide"
            )

        success_rate = (
            (report.passed_tests / report.total_tests * 100)
            if report.total_tests > 0
            else 0
        )
        if success_rate < 95:
            recommendations.append(
                f"Success rate ({success_rate:.1f}%) below threshold - review changes"
            )

        return recommendations

    def save_report(self, report: RegressionReport) -> None:
        """Save regression test report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Generate detailed report
        report_data = self.generate_regression_report(report)

        # Save JSON report
        json_file = Path(self.config.output_dir) / f"regression_report_{timestamp}.json"
        with open(json_file, "w") as f:
            json.dump(report_data, f, indent=2)

        logger.info(f"Regression report saved: {json_file}")

        # Save current results as new baseline
        current_results_file = (
            Path(self.config.current_results_dir) / f"baseline_{timestamp}.json"
        )
        current_results_file.parent.mkdir(parents=True, exist_ok=True)
        with open(current_results_file, "w") as f:
            json.dump(
                {
                    test.name: {
                        "response_data": test.current_result,
                        "response_time": test.duration,
                        "timestamp": datetime.now().isoformat(),
                    }
                    for test in report.test_results
                    if test.current_result
                },
                f,
                indent=2,
            )

        logger.info(f"Current results saved as baseline: {current_results_file}")

        # Print summary
        print(f"\nRegression Testing Summary:")
        print(f"Total Tests: {report.total_tests}")
        print(f"Passed: {report.passed_tests}")
        print(f"Failed: {report.failed_tests}")
        print(f"Success Rate: {(report.passed_tests / report.total_tests * 100):.1f}%")
        print(f"Performance Regressions: {report.performance_regressions}")
        print(f"Breaking Changes: {report.breaking_changes}")


# CLI usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run regression tests")
    parser.add_argument(
        "--baseline-spec",
        default="docs/openapi_baseline.yaml",
        help="Baseline OpenAPI spec",
    )
    parser.add_argument(
        "--current-spec",
        default="docs/openapi_comprehensive.yaml",
        help="Current OpenAPI spec",
    )
    parser.add_argument(
        "--baseline-results",
        default="test_results/baseline",
        help="Baseline results directory",
    )
    parser.add_argument(
        "--current-results",
        default="test_results/current",
        help="Current results directory",
    )
    parser.add_argument(
        "--output-dir", default="regression_results", help="Output directory"
    )
    parser.add_argument(
        "--base-url", default="http://localhost:8000", help="Base API URL"
    )
    parser.add_argument(
        "--performance-threshold",
        type=float,
        default=10.0,
        help="Performance regression threshold (%)",
    )

    args = parser.parse_args()

    # Create configuration
    config = RegressionTestConfig(
        baseline_spec_path=args.baseline_spec,
        current_spec_path=args.current_spec,
        baseline_results_dir=args.baseline_results,
        current_results_dir=args.current_results,
        output_dir=args.output_dir,
        base_url=args.base_url,
        performance_threshold=args.performance_threshold,
    )

    # Run regression tests
    async def main():
        async with RegressionTestFramework(config) as framework:
            report = await framework.run_all_regression_tests()
            framework.save_report(report)

    asyncio.run(main())
