"""
Edge Case Tester for Adversarial Critic

Tests content against edge cases to validate robustness.
Implements PROMPT 58 from STREAM_3_COGNITIVE_ENGINE.
"""

import asyncio
import json
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from ..models import ExecutionPlan, PlanStep


class EdgeCaseType(Enum):
    """Types of edge cases to test."""

    EMPTY_INPUT = "empty_input"
    NULL_VALUES = "null_values"
    EXTREME_VALUES = "extreme_values"
    INVALID_FORMATS = "invalid_formats"
    UNEXPECTED_CHARACTERS = "unexpected_characters"
    BOUNDARY_CONDITIONS = "boundary_conditions"
    CONCURRENT_ACCESS = "concurrent_access"
    RESOURCE_LIMITS = "resource_limits"
    NETWORK_FAILURES = "network_failures"
    TIMEOUT_SCENARIOS = "timeout_scenarios"
    MALICIOUS_INPUT = "malicious_input"
    ENCODING_ISSUES = "encoding_issues"


class TestResult(Enum):
    """Results of edge case testing."""

    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"
    WARNING = "warning"


@dataclass
class EdgeCase:
    """An edge case scenario."""

    id: str
    name: str
    description: str
    edge_case_type: EdgeCaseType
    test_input: Any
    expected_behavior: str
    severity: str  # "low", "medium", "high", "critical"
    tags: List[str]


@dataclass
class EdgeCaseTest:
    """Result of testing an edge case."""

    edge_case: EdgeCase
    result: TestResult
    actual_behavior: str
    error_message: Optional[str]
    performance_impact: float  # 0-1 scale
    response_time_ms: int
    timestamp: datetime


@dataclass
class EdgeCaseReport:
    """Complete edge case testing report."""

    component_id: str
    test_date: datetime
    total_edge_cases: int
    passed_tests: int
    failed_tests: int
    error_tests: int
    warning_tests: int
    critical_failures: int
    test_results: List[EdgeCaseTest]
    robustness_score: float  # 0-100 scale
    recommendations: List[str]
    testing_time_ms: int


class EdgeCaseTester:
    """
    Tests content against edge cases to validate robustness.

    Ensures system handles unexpected inputs gracefully.
    """

    def __init__(self, test_client=None):
        """
        Initialize the edge case tester.

        Args:
            test_client: Client for executing tests
        """
        self.test_client = test_client

        # Predefined edge cases for different input types
        self.edge_cases = {
            EdgeCaseType.EMPTY_INPUT: [
                EdgeCase(
                    id="empty_string",
                    name="Empty String Input",
                    description="Test with empty string input",
                    edge_case_type=EdgeCaseType.EMPTY_INPUT,
                    test_input="",
                    expected_behavior="Handle gracefully with appropriate error message",
                    severity="medium",
                    tags=["input_validation", "basic"],
                ),
                EdgeCase(
                    id="empty_list",
                    name="Empty List Input",
                    description="Test with empty list input",
                    edge_case_type=EdgeCaseType.EMPTY_INPUT,
                    test_input=[],
                    expected_behavior="Handle empty list without errors",
                    severity="medium",
                    tags=["input_validation", "data_structures"],
                ),
                EdgeCase(
                    id="empty_dict",
                    name="Empty Dictionary Input",
                    description="Test with empty dictionary input",
                    edge_case_type=EdgeCaseType.EMPTY_INPUT,
                    test_input={},
                    expected_behavior="Handle empty dictionary without errors",
                    severity="medium",
                    tags=["input_validation", "data_structures"],
                ),
            ],
            EdgeCaseType.NULL_VALUES: [
                EdgeCase(
                    id="null_string",
                    name="Null String",
                    description="Test with null string",
                    edge_case_type=EdgeCaseType.NULL_VALUES,
                    test_input=None,
                    expected_behavior="Handle null value gracefully",
                    severity="high",
                    tags=["null_handling", "input_validation"],
                ),
                EdgeCase(
                    id="undefined_value",
                    name="Undefined Value",
                    description="Test with undefined value",
                    edge_case_type=EdgeCaseType.NULL_VALUES,
                    test_input=undefined,
                    expected_behavior="Handle undefined without crashing",
                    severity="high",
                    tags=["null_handling", "input_validation"],
                ),
            ],
            EdgeCaseType.EXTREME_VALUES: [
                EdgeCase(
                    id="very_large_number",
                    name="Very Large Number",
                    description="Test with extremely large number",
                    edge_case_type=EdgeCaseType.EXTREME_VALUES,
                    test_input=999999999999999999999,
                    expected_behavior="Handle large number without overflow",
                    severity="medium",
                    tags=["numeric_limits", "performance"],
                ),
                EdgeCase(
                    id="very_small_number",
                    name="Very Small Number",
                    description="Test with extremely small number",
                    edge_case_type=EdgeCaseType.EXTREME_VALUES,
                    test_input=0.0000000000000001,
                    expected_behavior="Handle small number with precision",
                    severity="medium",
                    tags=["numeric_limits", "precision"],
                ),
                EdgeCase(
                    id="negative_infinity",
                    name="Negative Infinity",
                    description="Test with negative infinity",
                    edge_case_type=EdgeCaseType.EXTREME_VALUES,
                    test_input=float("-inf"),
                    expected_behavior="Handle infinity gracefully",
                    severity="high",
                    tags=["numeric_limits", "edge_cases"],
                ),
                EdgeCase(
                    id="positive_infinity",
                    name="Positive Infinity",
                    description="Test with positive infinity",
                    edge_case_type=EdgeCaseType.EXTREME_VALUES,
                    test_input=float("inf"),
                    expected_behavior="Handle infinity gracefully",
                    severity="high",
                    tags=["numeric_limits", "edge_cases"],
                ),
            ],
            EdgeCaseType.INVALID_FORMATS: [
                EdgeCase(
                    id="invalid_json",
                    name="Invalid JSON",
                    description="Test with malformed JSON",
                    edge_case_type=EdgeCaseType.INVALID_FORMATS,
                    test_input='{"invalid": json, "missing": quote}',
                    expected_behavior="Reject with proper error message",
                    severity="medium",
                    tags=["format_validation", "parsing"],
                ),
                EdgeCase(
                    id="invalid_email",
                    name="Invalid Email Format",
                    description="Test with invalid email address",
                    edge_case_type=EdgeCaseType.INVALID_FORMATS,
                    test_input="not-an-email@",
                    expected_behavior="Reject invalid email format",
                    severity="low",
                    tags=["format_validation", "email"],
                ),
                EdgeCase(
                    id="invalid_url",
                    name="Invalid URL Format",
                    description="Test with invalid URL",
                    edge_case_type=EdgeCaseType.INVALID_FORMATS,
                    test_input="http://invalid-url-with-no-tld",
                    expected_behavior="Handle invalid URL gracefully",
                    severity="low",
                    tags=["format_validation", "url"],
                ),
            ],
            EdgeCaseType.UNEXPECTED_CHARACTERS: [
                EdgeCase(
                    id="unicode_characters",
                    name="Unicode Characters",
                    description="Test with various Unicode characters",
                    edge_case_type=EdgeCaseType.UNEXPECTED_CHARACTERS,
                    test_input="Hello 🌟 世界 🚀 ñiño",
                    expected_behavior="Handle Unicode correctly",
                    severity="medium",
                    tags=["unicode", "encoding"],
                ),
                EdgeCase(
                    id="control_characters",
                    name="Control Characters",
                    description="Test with control characters",
                    edge_case_type=EdgeCaseType.UNEXPECTED_CHARACTERS,
                    test_input="Hello\x00\x01\x02World",
                    expected_behavior="Handle control characters safely",
                    severity="medium",
                    tags=["control_chars", "security"],
                ),
                EdgeCase(
                    id="special_characters",
                    name="Special Characters",
                    description="Test with special characters",
                    edge_case_type=EdgeCaseType.UNEXPECTED_CHARACTERS,
                    test_input="Hello!@#$%^&*()_+-=[]{}|;':\",./<>?",
                    expected_behavior="Handle special characters correctly",
                    severity="low",
                    tags=["special_chars", "encoding"],
                ),
            ],
            EdgeCaseType.BOUNDARY_CONDITIONS: [
                EdgeCase(
                    id="zero_value",
                    name="Zero Value",
                    description="Test with zero value",
                    edge_case_type=EdgeCaseType.BOUNDARY_CONDITIONS,
                    test_input=0,
                    expected_behavior="Handle zero correctly",
                    severity="low",
                    tags=["boundary", "numeric"],
                ),
                EdgeCase(
                    id="max_int_value",
                    name="Maximum Integer Value",
                    description="Test with maximum integer",
                    edge_case_type=EdgeCaseType.BOUNDARY_CONDITIONS,
                    test_input=2**31 - 1,
                    expected_behavior="Handle max int without overflow",
                    severity="medium",
                    tags=["boundary", "numeric"],
                ),
                EdgeCase(
                    id="min_int_value",
                    name="Minimum Integer Value",
                    description="Test with minimum integer",
                    edge_case_type=EdgeCaseType.BOUNDARY_CONDITIONS,
                    test_input=-(2**31),
                    expected_behavior="Handle min int without underflow",
                    severity="medium",
                    tags=["boundary", "numeric"],
                ),
            ],
            EdgeCaseType.MALICIOUS_INPUT: [
                EdgeCase(
                    id="sql_injection",
                    name="SQL Injection Attempt",
                    description="Test with SQL injection payload",
                    edge_case_type=EdgeCaseType.MALICIOUS_INPUT,
                    test_input="'; DROP TABLE users; --",
                    expected_behavior="Reject malicious input safely",
                    severity="critical",
                    tags=["security", "sql_injection"],
                ),
                EdgeCase(
                    id="xss_attempt",
                    name="XSS Attempt",
                    description="Test with XSS payload",
                    edge_case_type=EdgeCaseType.MALICIOUS_INPUT,
                    test_input="<script>alert('xss')</script>",
                    expected_behavior="Sanitize or reject XSS attempt",
                    severity="critical",
                    tags=["security", "xss"],
                ),
                EdgeCase(
                    id="path_traversal",
                    name="Path Traversal Attempt",
                    description="Test with path traversal payload",
                    edge_case_type=EdgeCaseType.MALICIOUS_INPUT,
                    test_input="../../../etc/passwd",
                    expected_behavior="Reject path traversal attempt",
                    severity="critical",
                    tags=["security", "path_traversal"],
                ),
            ],
            EdgeCaseType.ENCODING_ISSUES: [
                EdgeCase(
                    id="utf8_bom",
                    name="UTF-8 BOM",
                    description="Test with UTF-8 BOM",
                    edge_case_type=EdgeCaseType.ENCODING_ISSUES,
                    test_input="\ufeffHello World",
                    expected_behavior="Handle BOM correctly",
                    severity="low",
                    tags=["encoding", "utf8"],
                ),
                EdgeCase(
                    id="mixed_encoding",
                    name="Mixed Encoding",
                    description="Test with mixed character encoding",
                    edge_case_type=EdgeCaseType.ENCODING_ISSUES,
                    test_input="Hello\xff\xfeWorld",
                    expected_behavior="Handle mixed encoding gracefully",
                    severity="medium",
                    tags=["encoding", "mixed"],
                ),
            ],
        }

    async def generate_edge_cases(self, input_type: str) -> List[EdgeCase]:
        """
        Generate edge cases for a specific input type.

        Args:
            input_type: Type of input (e.g., "text", "number", "json", "email")

        Returns:
            List of edge cases for the input type
        """
        edge_cases = []

        # Base edge cases for all types
        base_cases = [
            self.edge_cases[EdgeCaseType.EMPTY_INPUT],
            self.edge_cases[EdgeCaseType.NULL_VALUES],
            self.edge_cases[EdgeCaseType.INVALID_FORMATS],
        ]

        for case_list in base_cases:
            edge_cases.extend(case_list)

        # Type-specific edge cases
        if input_type == "text":
            edge_cases.extend(self.edge_cases[EdgeCaseType.UNEXPECTED_CHARACTERS])
            edge_cases.extend(self.edge_cases[EdgeCaseType.MALICIOUS_INPUT])
            edge_cases.extend(self.edge_cases[EdgeCaseType.ENCODING_ISSUES])
        elif input_type == "number":
            edge_cases.extend(self.edge_cases[EdgeCaseType.EXTREME_VALUES])
            edge_cases.extend(self.edge_cases[EdgeCaseType.BOUNDARY_CONDITIONS])
        elif input_type == "json":
            edge_cases.extend(self.edge_cases[EdgeCaseType.INVALID_FORMATS])
        elif input_type == "email":
            email_cases = [
                case
                for case in self.edge_cases[EdgeCaseType.INVALID_FORMATS]
                if "email" in case.tags
            ]
            edge_cases.extend(email_cases)

        return edge_cases

    async def test_edge_cases(
        self,
        component_id: str,
        test_function: callable,
        edge_cases: List[EdgeCase] = None,
    ) -> EdgeCaseReport:
        """
        Test a component against edge cases.

        Args:
            component_id: ID of component being tested
            test_function: Function to test with edge case input
            edge_cases: List of edge cases to test (auto-generated if None)

        Returns:
            Complete edge case testing report
        """
        import time

        start_time = time.time()

        # Generate edge cases if not provided
        if edge_cases is None:
            edge_cases = await self._generate_default_edge_cases()

        # Test each edge case
        test_results = []
        for edge_case in edge_cases:
            result = await self._test_single_edge_case(edge_case, test_function)
            test_results.append(result)

        # Calculate statistics
        total_tests = len(test_results)
        passed_tests = sum(1 for r in test_results if r.result == TestResult.PASS)
        failed_tests = sum(1 for r in test_results if r.result == TestResult.FAIL)
        error_tests = sum(1 for r in test_results if r.result == TestResult.ERROR)
        warning_tests = sum(1 for r in test_results if r.result == TestResult.WARNING)

        # Count critical failures
        critical_failures = sum(
            1
            for r in test_results
            if r.result in [TestResult.FAIL, TestResult.ERROR]
            and r.edge_case.severity == "critical"
        )

        # Calculate robustness score
        robustness_score = self._calculate_robustness_score(test_results)

        # Generate recommendations
        recommendations = await self._generate_recommendations(test_results)

        testing_time_ms = int((time.time() - start_time) * 1000)

        return EdgeCaseReport(
            component_id=component_id,
            test_date=datetime.now(),
            total_edge_cases=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            error_tests=error_tests,
            warning_tests=warning_tests,
            critical_failures=critical_failures,
            test_results=test_results,
            robustness_score=robustness_score,
            recommendations=recommendations,
            testing_time_ms=testing_time_ms,
        )

    async def _generate_default_edge_cases(self) -> List[EdgeCase]:
        """Generate default set of edge cases."""
        edge_cases = []

        # Include a representative sample from each category
        for case_list in self.edge_cases.values():
            # Take first 2 cases from each category
            edge_cases.extend(case_list[:2])

        return edge_cases

    async def _test_single_edge_case(
        self, edge_case: EdgeCase, test_function: callable
    ) -> EdgeCaseTest:
        """Test a single edge case."""
        import time

        start_time = time.time()

        try:
            # Execute test with edge case input
            result = await self._execute_test(edge_case.test_input, test_function)

            # Determine test result
            test_result, actual_behavior, error_message = (
                await self._evaluate_test_result(edge_case, result)
            )

            # Calculate performance impact
            performance_impact = self._calculate_performance_impact(result)

            response_time_ms = int((time.time() - start_time) * 1000)

            return EdgeCaseTest(
                edge_case=edge_case,
                result=test_result,
                actual_behavior=actual_behavior,
                error_message=error_message,
                performance_impact=performance_impact,
                response_time_ms=response_time_ms,
                timestamp=datetime.now(),
            )

        except Exception as e:
            return EdgeCaseTest(
                edge_case=edge_case,
                result=TestResult.ERROR,
                actual_behavior="Exception occurred",
                error_message=str(e),
                performance_impact=1.0,
                response_time_ms=int((time.time() - start_time) * 1000),
                timestamp=datetime.now(),
            )

    async def _execute_test(self, test_input: Any, test_function: callable) -> Any:
        """Execute test function with edge case input."""
        try:
            if asyncio.iscoroutinefunction(test_function):
                return await test_function(test_input)
            else:
                return test_function(test_input)
        except Exception as e:
            return {"error": str(e), "exception": type(e).__name__}

    async def _evaluate_test_result(
        self, edge_case: EdgeCase, result: Any
    ) -> Tuple[TestResult, str, Optional[str]]:
        """Evaluate the result of an edge case test."""
        # Check for errors
        if isinstance(result, dict) and "error" in result:
            if edge_case.severity == "critical":
                return (
                    TestResult.FAIL,
                    f"Error occurred: {result['error']}",
                    result["error"],
                )
            else:
                return (
                    TestResult.WARNING,
                    f"Handled with warning: {result['error']}",
                    result["error"],
                )

        # Check if result is None (which might be expected for some cases)
        if result is None:
            if edge_case.edge_case_type == EdgeCaseType.NULL_VALUES:
                return TestResult.PASS, "Handled null input correctly", None
            else:
                return TestResult.WARNING, "Returned None unexpectedly", None

        # Check for expected behavior patterns
        if isinstance(result, str):
            if "error" in result.lower() or "invalid" in result.lower():
                if edge_case.edge_case_type in [
                    EdgeCaseType.INVALID_FORMATS,
                    EdgeCaseType.MALICIOUS_INPUT,
                ]:
                    return TestResult.PASS, "Properly rejected invalid input", None
                else:
                    return (
                        TestResult.WARNING,
                        f"Unexpected error message: {result}",
                        None,
                    )
            elif (
                len(result) == 0
                and edge_case.edge_case_type == EdgeCaseType.EMPTY_INPUT
            ):
                return TestResult.PASS, "Handled empty input correctly", None
            else:
                return TestResult.PASS, f"Processed input: {result[:50]}...", None

        # For other result types, assume pass unless it's clearly an error
        return (
            TestResult.PASS,
            f"Processed input successfully: {type(result).__name__}",
            None,
        )

    def _calculate_performance_impact(self, result: Any) -> float:
        """Calculate performance impact of edge case."""
        # Simple heuristic based on result characteristics
        if isinstance(result, dict) and "error" in result:
            return 0.8  # High impact for errors
        elif result is None:
            return 0.3  # Low impact for null handling
        elif isinstance(result, str) and len(result) > 1000:
            return 0.5  # Medium impact for large responses
        else:
            return 0.1  # Low impact for normal processing

    def _calculate_robustness_score(self, test_results: List[EdgeCaseTest]) -> float:
        """Calculate overall robustness score."""
        if not test_results:
            return 0.0

        total_score = 0
        total_weight = 0

        for test in test_results:
            # Weight by severity
            severity_weights = {"critical": 3.0, "high": 2.0, "medium": 1.5, "low": 1.0}

            weight = severity_weights.get(test.edge_case.severity, 1.0)

            # Score based on result
            if test.result == TestResult.PASS:
                score = 100
            elif test.result == TestResult.WARNING:
                score = 70
            elif test.result == TestResult.FAIL:
                score = 30
            else:  # ERROR
                score = 0

            # Apply performance penalty
            score *= 1.0 - test.performance_impact * 0.3

            total_score += score * weight
            total_weight += weight

        return total_score / total_weight if total_weight > 0 else 0.0

    async def _generate_recommendations(
        self, test_results: List[EdgeCaseTest]
    ) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []

        # Analyze failure patterns
        failed_tests = [
            r for r in test_results if r.result in [TestResult.FAIL, TestResult.ERROR]
        ]

        if failed_tests:
            # Group failures by type
            failure_types = {}
            for test in failed_tests:
                edge_case_type = test.edge_case.edge_case_type.value
                failure_types[edge_case_type] = failure_types.get(edge_case_type, 0) + 1

            # Generate recommendations for common failure types
            most_common = max(failure_types.items(), key=lambda x: x[1])[0]
            recommendations.append(f"Improve handling of {most_common} edge cases")

            # Critical failures
            critical_failures = [
                r for r in failed_tests if r.edge_case.severity == "critical"
            ]
            if critical_failures:
                recommendations.append(
                    "Address critical security vulnerabilities immediately"
                )

        # Performance recommendations
        high_impact_tests = [r for r in test_results if r.performance_impact > 0.7]
        if high_impact_tests:
            recommendations.append("Optimize performance for edge case handling")

        # General recommendations
        recommendations.extend(
            [
                "Implement comprehensive input validation",
                "Add proper error handling and logging",
                "Create automated edge case testing in CI/CD pipeline",
                "Document edge case behavior for developers",
            ]
        )

        return recommendations[:6]  # Return top 6 recommendations

    def get_testing_stats(self, reports: List[EdgeCaseReport]) -> Dict[str, Any]:
        """Get statistics about edge case testing."""
        if not reports:
            return {}

        total_reports = len(reports)
        total_tests = sum(r.total_edge_cases for r in reports)
        total_passed = sum(r.passed_tests for r in reports)
        total_failed = sum(r.failed_tests for r in reports)
        total_errors = sum(r.error_tests for r in reports)
        total_critical = sum(r.critical_failures for r in reports)

        avg_robustness = sum(r.robustness_score for r in reports) / total_reports

        # Edge case type distribution
        type_counts = {}
        for report in reports:
            for test in report.test_results:
                case_type = test.edge_case.edge_case_type.value
                type_counts[case_type] = type_counts.get(case_type, 0) + 1

        return {
            "total_components_tested": total_reports,
            "total_edge_case_tests": total_tests,
            "pass_rate": total_passed / total_tests if total_tests > 0 else 0,
            "failure_rate": total_failed / total_tests if total_tests > 0 else 0,
            "error_rate": total_errors / total_tests if total_tests > 0 else 0,
            "critical_failure_rate": (
                total_critical / total_tests if total_tests > 0 else 0
            ),
            "average_robustness_score": avg_robustness,
            "edge_case_type_distribution": type_counts,
            "average_testing_time_ms": sum(r.testing_time_ms for r in reports)
            / total_reports,
        }
