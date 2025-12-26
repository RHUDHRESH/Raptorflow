import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pytest

logger = logging.getLogger("raptorflow.testing.load")


@dataclass
class LoadTestConfig:
    """Load test configuration."""

    concurrent_users: int = 100
    ramp_up_time: int = 60  # seconds
    test_duration: int = 300  # seconds
    requests_per_second: int = 50
    endpoints: List[str] = None
    timeout: int = 30
    think_time: float = 1.0  # seconds between requests

    def __post_init__(self):
        if self.endpoints is None:
            self.endpoints = [
                "/health",
                "/metrics",
                "/api/v1/campaigns",
                "/api/v1/moves",
            ]


@dataclass
class LoadTestResult:
    """Load test result."""

    endpoint: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time_ms: float
    min_response_time_ms: float
    max_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    requests_per_second: float
    error_rate: float
    duration_seconds: int


class LoadTestRunner:
    """Load test runner for performance benchmarking."""

    def __init__(self, config: LoadTestConfig, base_url: str = "http://localhost:8000"):
        self.config = config
        self.base_url = base_url
        self.results: List[LoadTestResult] = []

    async def run_load_tests(self) -> List[LoadTestResult]:
        """Run load tests for all endpoints."""
        logger.info(
            f"Starting load tests: {self.config.concurrent_users} users, {self.config.requests_per_second} RPS"
        )

        for endpoint in self.config.endpoints:
            result = await self._test_endpoint(endpoint)
            self.results.append(result)

            logger.info(
                f"Endpoint {endpoint}: {result.successful_requests}/{result.total_requests} successful, "
                f"avg response time: {result.average_response_time_ms:.1f}ms"
            )

        return self.results

    async def _test_endpoint(self, endpoint: str) -> LoadTestResult:
        """Test a single endpoint."""
        import statistics
        import time

        from httpx import AsyncClient

        response_times = []
        successful_requests = 0
        failed_requests = 0
        start_time = time.time()

        # Create concurrent users
        semaphore = asyncio.Semaphore(self.config.concurrent_users)

        async def make_request():
            nonlocal successful_requests, failed_requests
            async with semaphore:
                async with AsyncClient(
                    base_url=self.base_url, timeout=self.config.timeout
                ) as client:
                    request_start = time.time()
                    try:
                        response = await client.get(endpoint)
                        request_time = (time.time() - request_start) * 1000
                        response_times.append(request_time)

                        if response.status_code < 400:
                            successful_requests += 1
                        else:
                            failed_requests += 1

                    except Exception:
                        failed_requests += 1
                        request_time = (time.time() - request_start) * 1000
                        response_times.append(request_time)

                    # Think time between requests
                    await asyncio.sleep(self.config.think_time)

        # Calculate total requests needed
        total_requests = self.config.requests_per_second * self.config.test_duration

        # Create tasks for all requests
        tasks = []
        for i in range(total_requests):
            task = asyncio.create_task(make_request())
            tasks.append(task)

            # Ramp up - stagger task creation
            if i < self.config.concurrent_users:
                await asyncio.sleep(
                    self.config.ramp_up_time / self.config.concurrent_users
                )

        # Wait for all tasks to complete
        await asyncio.gather(*tasks, return_exceptions=True)

        # Calculate statistics
        duration = time.time() - start_time

        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            p95_response_time = (
                statistics.quantiles(response_times, n=20)[18]
                if len(response_times) > 20
                else max(response_times)
            )
            p99_response_time = (
                statistics.quantiles(response_times, n=100)[98]
                if len(response_times) > 100
                else max(response_times)
            )
        else:
            avg_response_time = min_response_time = max_response_time = (
                p95_response_time
            ) = p99_response_time = 0

        actual_rps = successful_requests / duration if duration > 0 else 0
        error_rate = (
            failed_requests / (successful_requests + failed_requests)
            if (successful_requests + failed_requests) > 0
            else 0
        )

        return LoadTestResult(
            endpoint=endpoint,
            total_requests=successful_requests + failed_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            average_response_time_ms=avg_response_time,
            min_response_time_ms=min_response_time,
            max_response_time_ms=max_response_time,
            p95_response_time_ms=p95_response_time,
            p99_response_time_ms=p99_response_time,
            requests_per_second=actual_rps,
            error_rate=error_rate,
            duration_seconds=int(duration),
        )

    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate performance benchmark report."""
        if not self.results:
            return {"error": "No test results available"}

        # Calculate overall statistics
        total_requests = sum(r.total_requests for r in self.results)
        total_successful = sum(r.successful_requests for r in self.results)
        total_failed = sum(r.failed_requests for r in self.results)

        overall_avg_response_time = sum(
            r.average_response_time_ms for r in self.results
        ) / len(self.results)
        overall_p95_response_time = sum(
            r.p95_response_time_ms for r in self.results
        ) / len(self.results)
        overall_rps = sum(r.requests_per_second for r in self.results)
        overall_error_rate = total_failed / total_requests if total_requests > 0 else 0

        # Performance thresholds
        performance_grade = self._calculate_performance_grade(
            overall_avg_response_time, overall_p95_response_time, overall_error_rate
        )

        return {
            "test_config": {
                "concurrent_users": self.config.concurrent_users,
                "requests_per_second": self.config.requests_per_second,
                "test_duration": self.config.test_duration,
                "endpoints_tested": self.config.endpoints,
            },
            "overall_performance": {
                "total_requests": total_requests,
                "successful_requests": total_successful,
                "failed_requests": total_failed,
                "success_rate": (
                    (total_successful / total_requests * 100)
                    if total_requests > 0
                    else 0
                ),
                "average_response_time_ms": overall_avg_response_time,
                "p95_response_time_ms": overall_p95_response_time,
                "requests_per_second": overall_rps,
                "error_rate": overall_error_rate,
                "performance_grade": performance_grade,
            },
            "endpoint_performance": [
                {
                    "endpoint": r.endpoint,
                    "total_requests": r.total_requests,
                    "success_rate": (
                        (r.successful_requests / r.total_requests * 100)
                        if r.total_requests > 0
                        else 0
                    ),
                    "average_response_time_ms": r.average_response_time_ms,
                    "p95_response_time_ms": r.p95_response_time_ms,
                    "requests_per_second": r.requests_per_second,
                    "error_rate": r.error_rate,
                    "grade": self._calculate_endpoint_grade(r),
                }
                for r in self.results
            ],
            "recommendations": self._generate_recommendations(),
            "generated_at": datetime.utcnow().isoformat(),
        }

    def _calculate_performance_grade(
        self, avg_response_time: float, p95_response_time: float, error_rate: float
    ) -> str:
        """Calculate overall performance grade."""
        if error_rate > 0.05:  # > 5% error rate
            return "F"
        elif avg_response_time > 1000:  # > 1s average
            return "D"
        elif avg_response_time > 500:  # > 500ms average
            return "C"
        elif p95_response_time > 1000:  # > 1s p95
            return "B"
        else:
            return "A"

    def _calculate_endpoint_grade(self, result: LoadTestResult) -> str:
        """Calculate grade for individual endpoint."""
        if result.error_rate > 0.05:
            return "F"
        elif result.average_response_time_ms > 1000:
            return "D"
        elif result.average_response_time_ms > 500:
            return "C"
        elif result.p95_response_time_ms > 1000:
            return "B"
        else:
            return "A"

    def _generate_recommendations(self) -> List[str]:
        """Generate performance recommendations."""
        recommendations = []

        for result in self.results:
            if result.error_rate > 0.05:
                recommendations.append(
                    f"High error rate ({result.error_rate:.1%}) on {result.endpoint} - check error handling"
                )

            if result.average_response_time_ms > 500:
                recommendations.append(
                    f"Slow response time ({result.average_response_time_ms:.1f}ms) on {result.endpoint} - consider optimization"
                )

            if result.p95_response_time_ms > 1000:
                recommendations.append(
                    f"High P95 response time ({result.p95_response_time_ms:.1f}ms) on {result.endpoint} - investigate outliers"
                )

        if not recommendations:
            recommendations.append(
                "All endpoints performing well within acceptable thresholds"
            )

        return recommendations


# Pytest fixtures and test functions
@pytest.fixture
def load_test_config():
    """Pytest fixture for load test configuration."""
    return LoadTestConfig(
        concurrent_users=10, ramp_up_time=5, test_duration=30, requests_per_second=5
    )


@pytest.mark.asyncio
async def test_load_performance(load_test_config):
    """Test load performance."""
    runner = LoadTestRunner(load_test_config)
    results = await runner.run_load_tests()

    # Assert that all endpoints had some success
    for result in results:
        assert (
            result.successful_requests > 0
        ), f"No successful requests for {result.endpoint}"
        assert (
            result.error_rate < 0.1
        ), f"High error rate ({result.error_rate:.1%}) for {result.endpoint}"

    # Generate report
    report = runner.generate_performance_report()
    assert report["overall_performance"]["success_rate"] > 90


if __name__ == "__main__":
    # Run load tests when executed directly
    async def main():
        config = LoadTestConfig(
            concurrent_users=50,
            ramp_up_time=30,
            test_duration=120,
            requests_per_second=25,
        )

        runner = LoadTestRunner(config)
        results = await runner.run_load_tests()
        report = runner.generate_performance_report()

        print(f"\nLoad Test Results:")
        print(f"Overall Grade: {report['overall_performance']['performance_grade']}")
        print(f"Success Rate: {report['overall_performance']['success_rate']:.1f}%")
        print(
            f"Average Response Time: {report['overall_performance']['average_response_time_ms']:.1f}ms"
        )
        print(
            f"P95 Response Time: {report['overall_performance']['p95_response_time_ms']:.1f}ms"
        )
        print(
            f"Requests Per Second: {report['overall_performance']['requests_per_second']:.1f}"
        )

        print(f"\nRecommendations:")
        for rec in report["recommendations"]:
            print(f"- {rec}")

    asyncio.run(main())
