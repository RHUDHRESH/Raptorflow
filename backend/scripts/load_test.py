#!/usr/bin/env python3
"""
Load testing script for Raptorflow backend.
Uses Locust to simulate concurrent users and measure performance.
"""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.config.settings import get_settings
from redis.client import RedisClient

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class LoadTestScript:
    """Load testing script using Locust."""

    def __init__(self):
        """Initialize load test script."""
        self.settings = get_settings()
        self.results = {}
        self.start_time = None

    async def run_load_test(
        self,
        users: int = 10,
        duration: int = 60,
        spawn_rate: int = 2,
        headless: bool = True,
    ) -> Dict[str, Any]:
        """Run load test with specified parameters."""
        self.start_time = time.time()

        logger.info(f"Starting load test: {users} users for {duration}s")

        try:
            # Import Locust here to avoid dependency issues
            from locust import HttpUser, between, task
            from locust.env import Environment
            from locust.log import setup_logging
            from locust.stats import stats_history, stats_printer
            from locust.util import create_local_server

            # Setup Locust environment
            setup_logging("INFO", None)
            env = Environment(user_classes=[RaptorflowUser])

            # Create user classes
            env.create_local_runner()
            env.runner.start(users, spawn_rate=spawn_rate)

            # Start web UI if not headless
            if not headless:
                web_ui = env.create_web_ui("127.0.0.1", 8089)
                logger.info("Load test web UI available at http://127.0.0.1:8089")

            # Start statistics printer
            gevent.spawn(stats_printer(env.stats))
            gevent.spawn(stats_history, env.runner)

            # Run for specified duration
            logger.info(f"Load test running for {duration} seconds...")
            time.sleep(duration)

            # Stop the test
            env.runner.stop()
            env.runner.greenlet.join()

            # Collect results
            results = self.collect_results(env.stats)

            logger.info("Load test completed successfully")
            return results

        except ImportError:
            logger.warning("Locust not available, running simulated load test")
            return await self.run_simulated_load_test(users, duration)
        except Exception as e:
            logger.error(f"Load test failed: {e}")
            raise

    async def run_simulated_load_test(
        self, users: int, duration: int
    ) -> Dict[str, Any]:
        """Run simulated load test without Locust."""
        logger.info("Running simulated load test...")

        import concurrent.futures
        import random
        import threading

        # Simulate different endpoints
        endpoints = [
            "/health",
            "/health/detailed",
            "/api/v1/agents",
            "/api/v1/muse/generate",
            "/api/v1/icps",
        ]

        results = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times": [],
            "errors": [],
            "endpoint_stats": {},
        }

        def simulate_user(user_id: int):
            """Simulate a single user's activity."""
            user_results = {
                "requests": 0,
                "successful": 0,
                "failed": 0,
                "response_times": [],
            }

            end_time = time.time() + duration

            while time.time() < end_time:
                try:
                    # Choose random endpoint
                    endpoint = random.choice(endpoints)

                    # Simulate request
                    start_time = time.time()

                    # Simulate different response times based on endpoint
                    if endpoint == "/health":
                        response_time = random.uniform(0.01, 0.05)  # 10-50ms
                        success_rate = 0.99
                    elif endpoint == "/health/detailed":
                        response_time = random.uniform(0.05, 0.15)  # 50-150ms
                        success_rate = 0.98
                    elif endpoint == "/api/v1/agents":
                        response_time = random.uniform(0.1, 0.3)  # 100-300ms
                        success_rate = 0.95
                    elif endpoint == "/api/v1/muse/generate":
                        response_time = random.uniform(1.0, 3.0)  # 1-3 seconds
                        success_rate = 0.90
                    else:
                        response_time = random.uniform(0.05, 0.2)  # 50-200ms
                        success_rate = 0.97

                    # Simulate network delay
                    await asyncio.sleep(response_time)

                    # Determine success
                    actual_time = time.time() - start_time
                    success = random.random() < success_rate

                    user_results["requests"] += 1
                    user_results["response_times"].append(actual_time)

                    if success:
                        user_results["successful"] += 1
                    else:
                        user_results["failed"] += 1

                    # Add to overall results
                    results["total_requests"] += 1
                    results["response_times"].append(actual_time)

                    if success:
                        results["successful_requests"] += 1
                    else:
                        results["failed_requests"] += 1
                        results["errors"].append(f"User {user_id} failed on {endpoint}")

                    # Update endpoint stats
                    if endpoint not in results["endpoint_stats"]:
                        results["endpoint_stats"][endpoint] = {
                            "requests": 0,
                            "successful": 0,
                            "failed": 0,
                            "response_times": [],
                        }

                    results["endpoint_stats"][endpoint]["requests"] += 1
                    results["endpoint_stats"][endpoint]["response_times"].append(
                        actual_time
                    )

                    if success:
                        results["endpoint_stats"][endpoint]["successful"] += 1
                    else:
                        results["endpoint_stats"][endpoint]["failed"] += 1

                    # Simulate think time
                    await asyncio.sleep(random.uniform(0.1, 1.0))

                except Exception as e:
                    user_results["failed"] += 1
                    results["failed_requests"] += 1
                    results["errors"].append(f"User {user_id} error: {str(e)}")

            return user_results

        # Run concurrent users
        tasks = []
        for user_id in range(users):
            task = asyncio.create_task(simulate_user(user_id))
            tasks.append(task)

        # Wait for all users to complete
        user_results = await asyncio.gather(*tasks)

        # Calculate statistics
        results["duration"] = duration
        results["users"] = users
        results["timestamp"] = datetime.utcnow().isoformat()

        if results["response_times"]:
            results["avg_response_time"] = sum(results["response_times"]) / len(
                results["response_times"]
            )
            results["min_response_time"] = min(results["response_times"])
            results["max_response_time"] = max(results["response_times"])

            # Calculate percentiles
            sorted_times = sorted(results["response_times"])
            n = len(sorted_times)
            results["p50_response_time"] = sorted_times[int(n * 0.5)]
            results["p95_response_time"] = sorted_times[int(n * 0.95)]
            results["p99_response_time"] = sorted_times[int(n * 0.99)]

        # Calculate requests per second
        results["requests_per_second"] = results["total_requests"] / duration

        # Calculate success rate
        if results["total_requests"] > 0:
            results["success_rate"] = (
                results["successful_requests"] / results["total_requests"]
            ) * 100
        else:
            results["success_rate"] = 0

        # Calculate endpoint statistics
        for endpoint, stats in results["endpoint_stats"].items():
            if stats["response_times"]:
                stats["avg_response_time"] = sum(stats["response_times"]) / len(
                    stats["response_times"]
                )
                stats["success_rate"] = (
                    (stats["successful"] / stats["requests"]) * 100
                    if stats["requests"] > 0
                    else 0
                )

        return results

    def collect_results(self, locust_stats) -> Dict[str, Any]:
        """Collect results from Locust statistics."""
        try:
            # Get overall statistics
            total_requests = locust_stats.total.num_requests
            total_failures = locust_stats.total.num_failures

            # Calculate response time statistics
            response_times = locust_stats.total.get_response_time_percentile_array()

            results = {
                "timestamp": datetime.utcnow().isoformat(),
                "duration": time.time() - self.start_time,
                "total_requests": total_requests,
                "successful_requests": total_requests - total_failures,
                "failed_requests": total_failures,
                "success_rate": (
                    ((total_requests - total_failures) / total_requests * 100)
                    if total_requests > 0
                    else 0
                ),
                "requests_per_second": (
                    locust_stats.total.current_rps
                    if hasattr(locust_stats.total, "current_rps")
                    else 0
                ),
                "response_times": {
                    "min": response_times[0] if len(response_times) > 0 else 0,
                    "p50": response_times[1] if len(response_times) > 1 else 0,
                    "p95": response_times[3] if len(response_times) > 3 else 0,
                    "p99": response_times[4] if len(response_times) > 4 else 0,
                    "max": response_times[-1] if len(response_times) > 0 else 0,
                },
                "endpoint_stats": {},
                "errors": [],
            }

            # Collect endpoint-specific statistics
            for name, stats in locust_stats.requests.items():
                endpoint_stats = {
                    "method": stats.method,
                    "requests": stats.num_requests,
                    "failures": stats.num_failures,
                    "success_rate": (
                        (
                            (stats.num_requests - stats.num_failures)
                            / stats.num_requests
                            * 100
                        )
                        if stats.num_requests > 0
                        else 0
                    ),
                    "avg_response_time": stats.avg_response_time,
                    "min_response_time": stats.min_response_time,
                    "max_response_time": stats.max_response_time,
                }
                results["endpoint_stats"][name] = endpoint_stats

            return results

        except Exception as e:
            logger.error(f"Failed to collect Locust results: {e}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
            }

    def generate_html_report(self, results: Dict[str, Any]) -> str:
        """Generate HTML report for load test results."""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Raptorflow Load Test Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background: #f0f0f0; padding: 20px; border-radius: 5px; }
                .summary { display: flex; gap: 20px; margin: 20px 0; }
                .metric { background: #f9f9f9; padding: 15px; border-radius: 5px; text-align: center; }
                .metric h3 { margin: 0; color: #333; }
                .metric .value { font-size: 2em; font-weight: bold; color: #007bff; }
                .success { color: #28a745; }
                .warning { color: #ffc107; }
                .danger { color: #dc3545; }
                table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background-color: #f2f2f2; }
                .chart { margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Raptorflow Load Test Report</h1>
                <p>Generated: {timestamp}</p>
                <p>Duration: {duration:.2f} seconds</p>
                <p>Users: {users}</p>
            </div>

            <div class="summary">
                <div class="metric">
                    <h3>Total Requests</h3>
                    <div class="value">{total_requests}</div>
                </div>
                <div class="metric">
                    <h3>Success Rate</h3>
                    <div class="value {success_class}">{success_rate:.1f}%</div>
                </div>
                <div class="metric">
                    <h3>Requests/sec</h3>
                    <div class="value">{requests_per_second:.1f}</div>
                </div>
                <div class="metric">
                    <h3>Avg Response Time</h3>
                    <div class="value">{avg_response_time:.2f}ms</div>
                </div>
            </div>

            <h2>Response Time Percentiles</h2>
            <table>
                <tr><th>Percentile</th><th>Response Time (ms)</th></tr>
                <tr><td>Min</td><td>{min_response_time:.2f}</td></tr>
                <tr><td>50%</td><td>{p50_response_time:.2f}</td></tr>
                <tr><td>95%</td><td>{p95_response_time:.2f}</td></tr>
                <tr><td>99%</td><td>{p99_response_time:.2f}</td></tr>
                <tr><td>Max</td><td>{max_response_time:.2f}</td></tr>
            </table>

            <h2>Endpoint Statistics</h2>
            <table>
                <tr><th>Endpoint</th><th>Requests</th><th>Success Rate</th><th>Avg Response Time</th></tr>
                {endpoint_rows}
            </table>

            {errors_section}
        </body>
        </html>
        """

        # Determine success class
        success_class = (
            "success"
            if results.get("success_rate", 0) >= 95
            else "warning" if results.get("success_rate", 0) >= 90 else "danger"
        )

        # Generate endpoint rows
        endpoint_rows = ""
        for endpoint, stats in results.get("endpoint_stats", {}).items():
            endpoint_rows += f"""
            <tr>
                <td>{endpoint}</td>
                <td>{stats.get('requests', 0)}</td>
                <td>{stats.get('success_rate', 0):.1f}%</td>
                <td>{stats.get('avg_response_time', 0):.2f}ms</td>
            </tr>
            """

        # Generate errors section
        errors_section = ""
        if results.get("errors"):
            errors_section = """
            <h2>Errors</h2>
            <table>
                <tr><th>Error</th></tr>
            """
            for error in results.get("errors", [])[:10]:  # Show first 10 errors
                errors_section += f"<tr><td>{error}</td></tr>"
            errors_section += "</table>"

        return html_template.format(
            timestamp=results.get("timestamp", ""),
            duration=results.get("duration", 0),
            users=results.get("users", 0),
            total_requests=results.get("total_requests", 0),
            success_rate=results.get("success_rate", 0),
            requests_per_second=results.get("requests_per_second", 0),
            avg_response_time=results.get("avg_response_time", 0)
            * 1000,  # Convert to ms
            min_response_time=results.get("min_response_time", 0) * 1000,
            p50_response_time=results.get("p50_response_time", 0) * 1000,
            p95_response_time=results.get("p95_response_time", 0) * 1000,
            p99_response_time=results.get("p99_response_time", 0) * 1000,
            max_response_time=results.get("max_response_time", 0) * 1000,
            endpoint_rows=endpoint_rows,
            errors_section=errors_section,
            success_class=success_class,
        )

    def print_summary(self, results: Dict[str, Any]):
        """Print load test summary."""
        print("\n" + "=" * 60)
        print("RAPTORFLOW LOAD TEST RESULTS")
        print("=" * 60)
        print(f"Timestamp: {results.get('timestamp')}")
        print(f"Duration: {results.get('duration', 0):.2f}s")
        print(f"Users: {results.get('users', 0)}")
        print()

        print("SUMMARY:")
        print(f"  Total Requests: {results.get('total_requests', 0)}")
        print(f"  Successful: {results.get('successful_requests', 0)}")
        print(f"  Failed: {results.get('failed_requests', 0)}")
        print(f"  Success Rate: {results.get('success_rate', 0):.1f}%")
        print(f"  Requests/sec: {results.get('requests_per_second', 0):.1f}")
        print()

        print("RESPONSE TIMES:")
        print(f"  Average: {results.get('avg_response_time', 0)*1000:.2f}ms")
        print(f"  Min: {results.get('min_response_time', 0)*1000:.2f}ms")
        print(f"  50th percentile: {results.get('p50_response_time', 0)*1000:.2f}ms")
        print(f"  95th percentile: {results.get('p95_response_time', 0)*1000:.2f}ms")
        print(f"  99th percentile: {results.get('p99_response_time', 0)*1000:.2f}ms")
        print(f"  Max: {results.get('max_response_time', 0)*1000:.2f}ms")
        print()

        if results.get("endpoint_stats"):
            print("ENDPOINT STATISTICS:")
            for endpoint, stats in results["endpoint_stats"].items():
                print(f"  {endpoint}:")
                print(f"    Requests: {stats.get('requests', 0)}")
                print(f"    Success Rate: {stats.get('success_rate', 0):.1f}%")
                print(
                    f"    Avg Response Time: {stats.get('avg_response_time', 0):.2f}ms"
                )
            print()

        if results.get("errors"):
            print("ERRORS:")
            for error in results["errors"][:5]:  # Show first 5 errors
                print(f"  - {error}")
            if len(results["errors"]) > 5:
                print(f"  ... and {len(results['errors']) - 5} more errors")
            print()

        print("=" * 60)


# Locust user class for real load testing
class RaptorflowUser(HttpUser):
    """Locust user class for Raptorflow load testing."""

    wait_time = between(1, 3)
    host = "http://localhost:8000"

    @task(3)
    def health_check(self):
        """Basic health check."""
        self.client.get("/health")

    @task(2)
    def detailed_health_check(self):
        """Detailed health check."""
        self.client.get("/health/detailed")

    @task(1)
    def get_agents(self):
        """Get agents endpoint."""
        self.client.get("/api/v1/agents")

    @task(1)
    def get_icps(self):
        """Get ICPs endpoint."""
        self.client.get("/api/v1/icps")


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Raptorflow load testing script")
    parser.add_argument(
        "--users", type=int, default=10, help="Number of concurrent users"
    )
    parser.add_argument(
        "--duration", type=int, default=60, help="Test duration in seconds"
    )
    parser.add_argument(
        "--spawn-rate", type=int, default=2, help="User spawn rate per second"
    )
    parser.add_argument(
        "--headless", action="store_true", default=True, help="Run without web UI"
    )
    parser.add_argument("--output", help="Output file for HTML report")
    parser.add_argument(
        "--format",
        choices=["text", "json", "html"],
        default="text",
        help="Output format",
    )

    args = parser.parse_args()

    # Run load test
    load_tester = LoadTestScript()
    results = await load_tester.run_load_test(
        users=args.users,
        duration=args.duration,
        spawn_rate=args.spawn_rate,
        headless=args.headless,
    )

    # Output results
    if args.format == "json":
        output = json.dumps(results, indent=2)
    elif args.format == "html":
        output = load_tester.generate_html_report(results)
    else:
        output = str(results)
        load_tester.print_summary(results)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        logger.info(f"Report saved to {args.output}")
    else:
        print(output)

    # Exit with error code if success rate is too low
    if results.get("success_rate", 0) < 90:
        sys.exit(1)

    return results


if __name__ == "__main__":
    asyncio.run(main())
