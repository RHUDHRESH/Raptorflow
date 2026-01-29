"""
Agent Testing Suite for Raptorflow Backend
=====================================

This module provides comprehensive testing suite for agent system
with unit tests, integration tests, performance tests, and load tests.

Features:
- Unit tests for individual agent components
- Integration tests for agent workflows
- Performance tests for response time and throughput
- Load tests for scalability validation
- Automated test execution and reporting
- Test data management and fixtures
"""

import asyncio
import json
import logging
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from metrics import get_metrics_collector
from registry import get_agent_registry

from .base import BaseAgent
from .exceptions import TestingError

logger = logging.getLogger(__name__)


class TestType(Enum):
    """Test types."""

    UNIT = "unit"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"
    LOAD = "load"
    END_TO_END = "end_to_end"
    REGRESSION = "regression"


class TestStatus(Enum):
    """Test status types."""

    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class TestPriority(Enum):
    """Test priority levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class TestCase:
    """Test case definition."""

    test_id: str
    name: str
    description: str
    test_type: TestType
    priority: TestPriority
    agent_name: Optional[str] = None
    test_data: Dict[str, Any] = field(default_factory=dict)
    expected_result: Any = None
    timeout: int = 30
    tags: List[str] = field(default_factory=list)
    setup_function: Optional[str] = None
    teardown_function: Optional[str] = None


@dataclass
class TestResult:
    """Test result data."""

    test_id: str
    status: TestStatus
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration: float = 0.0
    actual_result: Any = None
    expected_result: Any = None
    error_message: str = ""
    stack_trace: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)
    assertions: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TestSuite:
    """Test suite configuration."""

    suite_id: str
    name: str
    description: str
    test_cases: List[TestCase] = field(default_factory=list)
    setup_function: Optional[str] = None
    teardown_function: Optional[str] = None
    parallel_execution: bool = True
    max_workers: int = 4


@dataclass
class LoadTestConfig:
    """Load test configuration."""

    concurrent_users: int = 10
    ramp_up_time: int = 30  # seconds
    test_duration: int = 300  # seconds
    requests_per_second: int = 5
    max_response_time: float = 5.0  # seconds
    max_error_rate: float = 0.05  # 5%


@dataclass
class PerformanceTestConfig:
    """Performance test configuration."""

    warmup_requests: int = 10
    test_requests: int = 100
    concurrent_requests: int = 1
    response_time_percentiles: List[float] = field(
        default_factory=lambda: [50, 90, 95, 99]
    )
    max_response_time: float = 2.0  # seconds
    min_throughput: float = 10.0  # requests per second


class AgentTestSuite:
    """Comprehensive testing suite for agent system."""

    def __init__(self, storage_path: str = "./data/tests"):
        self.storage_path = storage_path
        self.test_suites: Dict[str, TestSuite] = {}
        self.test_results: List[TestResult] = []
        self.metrics_collector = get_metrics_collector()
        self._load_test_suites()

    def _load_test_suites(self) -> None:
        """Load test suites from storage."""
        try:
            import os

            os.makedirs(self.storage_path, exist_ok=True)

            suites_file = os.path.join(self.storage_path, "test_suites.json")
            if os.path.exists(suites_file):
                with open(suites_file, "r") as f:
                    data = json.load(f)
                    for suite_id, suite_data in data.items():
                        self.test_suites[suite_id] = TestSuite(**suite_data)

            results_file = os.path.join(self.storage_path, "test_results.json")
            if os.path.exists(results_file):
                with open(results_file, "r") as f:
                    data = json.load(f)
                    for result_data in data:
                        self.test_results.append(TestResult(**result_data))

            logger.info(
                f"Loaded {len(self.test_suites)} test suites and {len(self.test_results)} test results"
            )

        except Exception as e:
            logger.error(f"Failed to load test data: {e}")

    def _save_test_results(self) -> None:
        """Save test results to storage."""
        try:
            import os

            os.makedirs(self.storage_path, exist_ok=True)

            results_file = os.path.join(self.storage_path, "test_results.json")
            results_data = [
                {
                    "test_id": result.test_id,
                    "status": result.status.value,
                    "start_time": result.start_time.isoformat(),
                    "end_time": (
                        result.end_time.isoformat() if result.end_time else None
                    ),
                    "duration": result.duration,
                    "actual_result": result.actual_result,
                    "expected_result": result.expected_result,
                    "error_message": result.error_message,
                    "stack_trace": result.stack_trace,
                    "metrics": result.metrics,
                    "assertions": result.assertions,
                }
                for result in self.test_results
            ]

            with open(results_file, "w") as f:
                json.dump(results_data, f, indent=2)

            logger.info("Test results saved successfully")

        except Exception as e:
            logger.error(f"Failed to save test results: {e}")
            raise TestingError(f"Failed to save test results: {e}")

    def create_test_suite(
        self,
        suite_id: str,
        name: str,
        description: str,
        test_cases: List[TestCase],
        parallel_execution: bool = True,
        max_workers: int = 4,
    ) -> bool:
        """Create a new test suite."""
        try:
            suite = TestSuite(
                suite_id=suite_id,
                name=name,
                description=description,
                test_cases=test_cases,
                parallel_execution=parallel_execution,
                max_workers=max_workers,
            )

            self.test_suites[suite_id] = suite
            self._save_test_suites()

            logger.info(f"Created test suite {suite_id}: {name}")
            return True

        except Exception as e:
            logger.error(f"Failed to create test suite {suite_id}: {e}")
            return False

    async def run_test_suite(
        self, suite_id: str, test_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """Run a test suite."""
        try:
            if suite_id not in self.test_suites:
                return {"error": f"Test suite {suite_id} not found"}

            suite = self.test_suites[suite_id]
            logger.info(f"Running test suite {suite_id}: {suite.name}")

            # Filter test cases if needed
            test_cases = suite.test_cases
            if test_filter:
                test_cases = [tc for tc in test_cases if test_filter in tc.tags]

            # Run setup function if exists
            if suite.setup_function:
                await self._execute_setup_function(suite.setup_function)

            # Execute tests
            if suite.parallel_execution:
                results = await self._run_tests_parallel(test_cases, suite.max_workers)
            else:
                results = await self._run_tests_sequential(test_cases)

            # Run teardown function if exists
            if suite.teardown_function:
                await self._execute_teardown_function(suite.teardown_function)

            # Calculate summary
            summary = self._calculate_test_summary(results)

            # Save results
            self.test_results.extend(results)
            self._save_test_results()

            logger.info(
                f"Test suite {suite_id} completed: {summary['total_passed']}/{summary['total_tests']} passed"
            )

            return {
                "suite_id": suite_id,
                "suite_name": suite.name,
                "summary": summary,
                "results": [
                    {
                        "test_id": result.test_id,
                        "name": result.test_id,
                        "status": result.status.value,
                        "duration": result.duration,
                        "error_message": result.error_message,
                    }
                    for result in results
                ],
            }

        except Exception as e:
            logger.error(f"Failed to run test suite {suite_id}: {e}")
            return {"error": str(e)}

    async def _run_tests_parallel(
        self, test_cases: List[TestCase], max_workers: int
    ) -> List[TestResult]:
        """Run tests in parallel."""
        try:
            semaphore = asyncio.Semaphore(max_workers)

            async def run_single_test(test_case: TestCase) -> TestResult:
                async with semaphore:
                    return await self._run_single_test(test_case)

            tasks = [run_single_test(tc) for tc in test_cases]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Convert exceptions to failed results
            final_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    final_results.append(
                        TestResult(
                            test_id=test_cases[i].test_id,
                            status=TestStatus.ERROR,
                            error_message=str(result),
                            stack_trace="",
                        )
                    )
                else:
                    final_results.append(result)

            return final_results

        except Exception as e:
            logger.error(f"Failed to run tests in parallel: {e}")
            return []

    async def _run_tests_sequential(
        self, test_cases: List[TestCase]
    ) -> List[TestResult]:
        """Run tests sequentially."""
        results = []
        for test_case in test_cases:
            result = await self._run_single_test(test_case)
            results.append(result)
        return results

    async def _run_single_test(self, test_case: TestCase) -> TestResult:
        """Run a single test case."""
        start_time = datetime.now()

        try:
            logger.debug(f"Running test {test_case.test_id}: {test_case.name}")

            # Run setup function if exists
            if test_case.setup_function:
                await self._execute_setup_function(test_case.setup_function)

            # Execute test based on type
            if test_case.test_type == TestType.UNIT:
                result = await self._run_unit_test(test_case)
            elif test_case.test_type == TestType.INTEGRATION:
                result = await self._run_integration_test(test_case)
            elif test_case.test_type == TestType.PERFORMANCE:
                result = await self._run_performance_test(test_case)
            elif test_case.test_type == TestType.LOAD:
                result = await self._run_load_test(test_case)
            else:
                result = await self._run_end_to_end_test(test_case)

            # Run teardown function if exists
            if test_case.teardown_function:
                await self._execute_teardown_function(test_case.teardown_function)

            end_time = datetime.now()
            result.duration = (end_time - start_time).total_seconds()
            result.start_time = start_time
            result.end_time = end_time

            return result

        except Exception as e:
            end_time = datetime.now()
            return TestResult(
                test_id=test_case.test_id,
                status=TestStatus.ERROR,
                start_time=start_time,
                end_time=end_time,
                duration=(end_time - start_time).total_seconds(),
                error_message=str(e),
                stack_trace="",
            )

    async def _run_unit_test(self, test_case: TestCase) -> TestResult:
        """Run a unit test."""
        try:
            # Get agent instance
            if not test_case.agent_name:
                return TestResult(
                    test_id=test_case.test_id,
                    status=TestStatus.SKIPPED,
                    error_message="No agent specified for unit test",
                )

            agent_registry = get_agent_registry()
            agent = agent_registry.get_agent(test_case.agent_name)

            if not agent:
                return TestResult(
                    test_id=test_case.test_id,
                    status=TestStatus.SKIPPED,
                    error_message=f"Agent {test_case.agent_name} not found",
                )

            # Test agent instantiation
            actual_result = agent is not None

            return TestResult(
                test_id=test_case.test_id,
                status=TestStatus.PASSED if actual_result else TestStatus.FAILED,
                actual_result=actual_result,
                expected_result=True,
                error_message=(
                    ""
                    if actual_result
                    else f"Agent {test_case.agent_name} instantiation failed"
                ),
            )

        except Exception as e:
            return TestResult(
                test_id=test_case.test_id, status=TestStatus.ERROR, error_message=str(e)
            )

    async def _run_integration_test(self, test_case: TestCase) -> TestResult:
        """Run an integration test."""
        try:
            # Test agent execution with sample data
            if not test_case.agent_name:
                return TestResult(
                    test_id=test_case.test_id,
                    status=TestStatus.SKIPPED,
                    error_message="No agent specified for integration test",
                )

            agent_registry = get_agent_registry()
            agent = agent_registry.get_agent(test_case.agent_name)

            if not agent:
                return TestResult(
                    test_id=test_case.test_id,
                    status=TestStatus.SKIPPED,
                    error_message=f"Agent {test_case.agent_name} not found",
                )

            # Execute agent with test data
            start_time = time.time()
            result = await agent.execute(test_case.test_data)
            execution_time = time.time() - start_time

            # Basic validation
            success = result is not None and "error" not in str(result).lower()

            return TestResult(
                test_id=test_case.test_id,
                status=TestStatus.PASSED if success else TestStatus.FAILED,
                actual_result=result,
                expected_result=test_case.expected_result,
                error_message="" if success else "Agent execution failed",
                metrics={"execution_time": execution_time, "success": success},
            )

        except Exception as e:
            return TestResult(
                test_id=test_case.test_id, status=TestStatus.ERROR, error_message=str(e)
            )

    async def _run_performance_test(self, test_case: TestCase) -> TestResult:
        """Run a performance test."""
        try:
            config = PerformanceTestConfig(**test_case.test_data.get("config", {}))

            if not test_case.agent_name:
                return TestResult(
                    test_id=test_case.test_id,
                    status=TestStatus.SKIPPED,
                    error_message="No agent specified for performance test",
                )

            agent_registry = get_agent_registry()
            agent = agent_registry.get_agent(test_case.agent_name)

            if not agent:
                return TestResult(
                    test_id=test_case.test_id,
                    status=TestStatus.SKIPPED,
                    error_message=f"Agent {test_case.agent_name} not found",
                )

            # Warmup requests
            logger.info(f"Running {config.warmup_requests} warmup requests...")
            for i in range(config.warmup_requests):
                await agent.execute({"test": "warmup", "iteration": i})

            # Performance test
            logger.info(f"Running {config.test_requests} performance test requests...")
            response_times = []

            for i in range(config.test_requests):
                start_time = time.time()
                await agent.execute({"test": "performance", "iteration": i})
                response_time = time.time() - start_time
                response_times.append(response_time)

            # Calculate metrics
            avg_response_time = sum(response_times) / len(response_times)
            response_times.sort()
            percentiles = {}

            for percentile in config.response_time_percentiles:
                index = int(len(response_times) * percentile / 100)
                percentiles[f"p{percentile}"] = response_times[
                    min(index, len(response_times) - 1)
                ]

            throughput = (
                config.test_requests / sum(response_times)
                if sum(response_times) > 0
                else 0
            )

            # Check performance criteria
            passed = (
                avg_response_time <= config.max_response_time
                and throughput >= config.min_throughput
            )

            return TestResult(
                test_id=test_case.test_id,
                status=TestStatus.PASSED if passed else TestStatus.FAILED,
                metrics={
                    "avg_response_time": avg_response_time,
                    "percentiles": percentiles,
                    "throughput": throughput,
                    "total_requests": config.test_requests,
                    "passed": passed,
                },
            )

        except Exception as e:
            return TestResult(
                test_id=test_case.test_id, status=TestStatus.ERROR, error_message=str(e)
            )

    async def _run_load_test(self, test_case: TestCase) -> TestResult:
        """Run a load test."""
        try:
            config = LoadTestConfig(**test_case.test_data.get("config", {}))

            if not test_case.agent_name:
                return TestResult(
                    test_id=test_case.test_id,
                    status=TestStatus.SKIPPED,
                    error_message="No agent specified for load test",
                )

            agent_registry = get_agent_registry()
            agent = agent_registry.get_agent(test_case.agent_name)

            if not agent:
                return TestResult(
                    test_id=test_case.test_id,
                    status=TestStatus.SKIPPED,
                    error_message=f"Agent {test_case.agent_name} not found",
                )

            # Load test execution
            logger.info(
                f"Starting load test: {config.concurrent_users} concurrent users, {config.test_duration}s duration"
            )

            start_time = time.time()
            response_times = []
            errors = 0
            total_requests = 0

            # Create concurrent tasks
            async def load_task(user_id: int) -> Tuple[float, bool]:
                try:
                    task_start = time.time()
                    result = await agent.execute(
                        {
                            "test": "load",
                            "user_id": user_id,
                            "request_id": str(uuid.uuid4()),
                        }
                    )
                    task_time = time.time() - task_start
                    success = result is not None and "error" not in str(result).lower()

                    return task_time, success

                except Exception as e:
                    logger.error(f"Load task error: {e}")
                    return 0.0, False

            # Execute load test
            tasks = []
            for i in range(config.concurrent_users):
                for j in range(config.requests_per_second):
                    tasks.append(load_task(i))

            # Run for specified duration
            end_time = start_time + config.test_duration
            while time.time() < end_time:
                batch_tasks = tasks[: config.requests_per_second]
                results = await asyncio.gather(*batch_tasks, return_exceptions=True)

                for result in results:
                    if isinstance(result, Exception):
                        errors += 1
                    else:
                        response_time, success = result
                        if success:
                            response_times.append(response_time)
                        else:
                            errors += 1

                total_requests += len(batch_tasks)

                # Wait for next second
                await asyncio.sleep(1)

            # Calculate metrics
            avg_response_time = (
                sum(response_times) / len(response_times) if response_times else 0
            )
            error_rate = errors / total_requests if total_requests > 0 else 0
            throughput = total_requests / config.test_duration

            # Check load test criteria
            passed = (
                avg_response_time <= config.max_response_time
                and error_rate <= config.max_error_rate
            )

            return TestResult(
                test_id=test_case.test_id,
                status=TestStatus.PASSED if passed else TestStatus.FAILED,
                metrics={
                    "avg_response_time": avg_response_time,
                    "error_rate": error_rate,
                    "throughput": throughput,
                    "total_requests": total_requests,
                    "total_errors": errors,
                    "duration": config.test_duration,
                    "concurrent_users": config.concurrent_users,
                    "passed": passed,
                },
            )

        except Exception as e:
            return TestResult(
                test_id=test_case.test_id, status=TestStatus.ERROR, error_message=str(e)
            )

    async def _run_end_to_end_test(self, test_case: TestCase) -> TestResult:
        """Run an end-to-end test."""
        try:
            # Test complete workflow
            if not test_case.agent_name:
                return TestResult(
                    test_id=test_case.test_id,
                    status=TestStatus.SKIPPED,
                    error_message="No agent specified for end-to-end test",
                )

            agent_registry = get_agent_registry()
            agent = agent_registry.get_agent(test_case.agent_name)

            if not agent:
                return TestResult(
                    test_id=test_case.test_id,
                    status=TestStatus.SKIPPED,
                    error_message=f"Agent {test_case.agent_name} not found",
                )

            # Execute complete workflow
            workflow_steps = test_case.test_data.get("workflow", [])
            results = []

            for step in workflow_steps:
                step_start = time.time()
                step_result = await agent.execute(step)
                step_time = time.time() - step_start
                step_success = (
                    step_result is not None and "error" not in str(step_result).lower()
                )

                results.append(
                    {
                        "step": step.get("name", "unknown"),
                        "success": step_success,
                        "time": step_time,
                        "result": step_result,
                    }
                )

            # Overall success
            overall_success = all(r["success"] for r in results)

            return TestResult(
                test_id=test_case.test_id,
                status=TestStatus.PASSED if overall_success else TestStatus.FAILED,
                actual_result=results,
                expected_result=test_case.expected_result,
                error_message=(
                    ""
                    if overall_success
                    else "Workflow failed at step: " + str(len(results))
                ),
                metrics={
                    "total_steps": len(workflow_steps),
                    "successful_steps": sum(1 for r in results if r["success"]),
                    "workflow_results": results,
                },
            )

        except Exception as e:
            return TestResult(
                test_id=test_case.test_id, status=TestStatus.ERROR, error_message=str(e)
            )

    async def _execute_setup_function(self, function_name: str) -> None:
        """Execute a setup function."""
        try:
            # In a real implementation, this would dynamically load and execute setup functions
            logger.info(f"Executing setup function: {function_name}")
            # Placeholder for setup execution

        except Exception as e:
            logger.error(f"Setup function {function_name} failed: {e}")

    async def _execute_teardown_function(self, function_name: str) -> None:
        """Execute a teardown function."""
        try:
            # In a real implementation, this would dynamically load and execute teardown functions
            logger.info(f"Executing teardown function: {function_name}")
            # Placeholder for teardown execution

        except Exception as e:
            logger.error(f"Teardown function {function_name} failed: {e}")

    def _calculate_test_summary(self, results: List[TestResult]) -> Dict[str, Any]:
        """Calculate test summary statistics."""
        try:
            total_tests = len(results)
            passed_tests = len([r for r in results if r.status == TestStatus.PASSED])
            failed_tests = len([r for r in results if r.status == TestStatus.FAILED])
            error_tests = len([r for r in results if r.status == TestStatus.ERROR])
            skipped_tests = len([r for r in results if r.status == TestStatus.SKIPPED])

            total_duration = sum(r.duration for r in results)
            avg_duration = total_duration / total_tests if total_tests > 0 else 0

            return {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "error_tests": error_tests,
                "skipped_tests": skipped_tests,
                "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
                "total_duration": total_duration,
                "avg_duration": avg_duration,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to calculate test summary: {e}")
            return {"error": str(e)}

    def get_test_results(
        self,
        suite_id: Optional[str] = None,
        test_type: Optional[TestType] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """Get test results."""
        try:
            results = self.test_results

            # Filter by suite
            if suite_id:
                # In a real implementation, this would filter by suite
                pass

            # Filter by test type
            if test_type:
                results = [r for r in results if r.test_id.startswith(test_type.value)]

            # Sort by timestamp (most recent first)
            results.sort(key=lambda x: x.start_time, reverse=True)

            return {
                "total_results": len(results),
                "results": [
                    {
                        "test_id": result.test_id,
                        "status": result.status.value,
                        "duration": result.duration,
                        "error_message": result.error_message,
                        "timestamp": result.start_time.isoformat(),
                        "metrics": result.metrics,
                    }
                    for result in results[:limit]
                ],
            }

        except Exception as e:
            logger.error(f"Failed to get test results: {e}")
            return {"error": str(e)}

    def generate_test_report(self, suite_id: str, format: str = "json") -> str:
        """Generate test report."""
        try:
            if suite_id not in self.test_suites:
                return f"Test suite {suite_id} not found"

            suite = self.test_suites[suite_id]

            # Get results for this suite
            results = [
                r
                for r in self.test_results
                if r.test_id in [tc.test_id for tc in suite.test_cases]
            ]

            summary = self._calculate_test_summary(results)

            report_data = {
                "suite": {
                    "id": suite_id,
                    "name": suite.name,
                    "description": suite.description,
                    "total_test_cases": len(suite.test_cases),
                },
                "summary": summary,
                "results": [
                    {
                        "test_id": result.test_id,
                        "status": result.status.value,
                        "duration": result.duration,
                        "error_message": result.error_message,
                        "timestamp": result.start_time.isoformat(),
                        "metrics": result.metrics,
                    }
                    for result in results
                ],
            }

            if format.lower() == "json":
                return json.dumps(report_data, indent=2)
            elif format.lower() == "html":
                return self._generate_html_report(report_data)
            else:
                return "Unsupported format"

        except Exception as e:
            logger.error(f"Failed to generate test report: {e}")
            return f"Error generating report: {e}"

    def _generate_html_report(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML test report."""
        try:
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Test Report: {report_data['suite']['name']}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background: #f4f4f4; padding: 20px; border-radius: 5px; }}
                    .summary {{ margin: 20px 0; }}
                    .test-case {{ margin: 10px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                    .passed {{ border-left: 5px solid #28a745; }}
                    .failed {{ border-left: 5px solid #dc3545; }}
                    .error {{ border-left: 5px solid #ffc107; }}
                    .skipped {{ border-left: 5px solid #6c757d; }}
                    .metrics {{ margin-top: 10px; font-size: 0.9em; color: #666; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>{report_data['suite']['name']}</h1>
                    <p>{report_data['suite']['description']}</p>
                </div>

                <div class="summary">
                    <h2>Test Summary</h2>
                    <p>Total Tests: {report_data['summary']['total_tests']}</p>
                    <p>Passed: {report_data['summary']['passed_tests']}</p>
                    <p>Failed: {report_data['summary']['failed_tests']}</p>
                    <p>Success Rate: {report_data['summary']['success_rate']:.2%}</p>
                    <p>Total Duration: {report_data['summary']['total_duration']:.2f}s</p>
                </div>

                <h2>Test Results</h2>
            """

            for result in report_data["results"]:
                status_class = result["status"].lower()
                html += f"""
                <div class="test-case {status_class}">
                    <h3>Test: {result['test_id']}</h3>
                    <p>Status: {result['status'].upper()}</p>
                    <p>Duration: {result['duration']:.2f}s</p>
                    {f"<p>Error: {result['error_message']}</p>" if result['error_message'] else ""}
                    {f"<div class='metrics'>Metrics: {json.dumps(result['metrics'], indent=2)}</div>" if result['metrics'] else ""}
                </div>
                """

            html += """
            </body>
            </html>
            """

            return html

        except Exception as e:
            logger.error(f"Failed to generate HTML report: {e}")
            return f"Error generating HTML report: {e}"


# Global test suite instance
_agent_test_suite: Optional[AgentTestSuite] = None


def get_agent_test_suite(storage_path: Optional[str] = None) -> AgentTestSuite:
    """Get or create agent test suite."""
    global _agent_test_suite
    if _agent_test_suite is None:
        _agent_test_suite = AgentTestSuite(storage_path)
    return _agent_test_suite


# Convenience functions for backward compatibility
async def run_test_suite(
    suite_id: str, test_filter: Optional[str] = None
) -> Dict[str, Any]:
    """Run a test suite."""
    suite = get_agent_test_suite()
    return await suite.run_test_suite(suite_id, test_filter)


def get_test_results(
    suite_id: Optional[str] = None,
    test_type: Optional[TestType] = None,
    limit: int = 100,
) -> Dict[str, Any]:
    """Get test results."""
    suite = get_agent_test_suite()
    return suite.get_test_results(suite_id, test_type, limit)


def generate_test_report(suite_id: str, format: str = "json") -> str:
    """Generate test report."""
    suite = get_agent_test_suite()
    return suite.generate_test_report(suite_id, format)
