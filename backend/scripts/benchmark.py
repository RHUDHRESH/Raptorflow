#!/usr/bin/env python3
"""
Benchmark script for Raptorflow backend.
Tests key operations and measures performance.
"""

import asyncio
import json
import logging
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from .redis.cache import CacheService
from .redis.client import RedisClient
from .redis.locks import DistributedLock
from .redis.queue import QueueService
from .redis.rate_limit import RateLimitService
from .redis.session import SessionService

from .config.settings import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class BenchmarkScript:
    """Benchmark script for backend performance testing."""

    def __init__(self):
        """Initialize benchmark script."""
        self.settings = get_settings()
        self.results = {}
        self.start_time = None

    async def run_benchmarks(self) -> Dict[str, Any]:
        """Run all benchmark tests."""
        self.start_time = time.time()

        logger.info("Starting benchmark suite...")

        benchmarks = [
            ("redis_operations", self.benchmark_redis_operations),
            ("cache_performance", self.benchmark_cache_performance),
            ("session_performance", self.benchmark_session_performance),
            ("rate_limit_performance", self.benchmark_rate_limit_performance),
            ("queue_performance", self.benchmark_queue_performance),
            ("lock_performance", self.benchmark_lock_performance),
            ("concurrent_operations", self.benchmark_concurrent_operations),
            ("memory_operations", self.benchmark_memory_operations),
        ]

        overall_status = "success"

        for benchmark_name, benchmark_func in benchmarks:
            try:
                logger.info(f"Running benchmark: {benchmark_name}")
                result = await benchmark_func()
                self.results[benchmark_name] = result

                if result["status"] != "success":
                    overall_status = "partial"
                    logger.warning(f"Benchmark {benchmark_name} had issues")

            except Exception as e:
                logger.error(f"Benchmark {benchmark_name} failed: {e}")
                self.results[benchmark_name] = {
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }
                overall_status = "failed"

        duration = time.time() - self.start_time

        final_report = {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "duration_seconds": duration,
            "benchmarks": self.results,
            "summary": self.generate_summary(),
        }

        logger.info(
            f"Benchmark suite completed in {duration:.2f}s - Status: {overall_status}"
        )
        return final_report

    async def benchmark_redis_operations(self) -> Dict[str, Any]:
        """Benchmark basic Redis operations."""
        try:
            redis_client = RedisClient()
            operations = {}

            # Benchmark SET operation
            set_times = []
            for i in range(1000):
                start = time.time()
                await redis_client.set(f"benchmark:set:{i}", f"value_{i}")
                set_times.append((time.time() - start) * 1000)

            operations["set"] = {
                "operations": 1000,
                "avg_ms": statistics.mean(set_times),
                "min_ms": min(set_times),
                "max_ms": max(set_times),
                "p95_ms": self.percentile(set_times, 95),
                "ops_per_second": 1000 / sum(set_times) * 1000,
            }

            # Benchmark GET operation
            get_times = []
            for i in range(1000):
                start = time.time()
                await redis_client.get(f"benchmark:set:{i}")
                get_times.append((time.time() - start) * 1000)

            operations["get"] = {
                "operations": 1000,
                "avg_ms": statistics.mean(get_times),
                "min_ms": min(get_times),
                "max_ms": max(get_times),
                "p95_ms": self.percentile(get_times, 95),
                "ops_per_second": 1000 / sum(get_times) * 1000,
            }

            # Benchmark MGET operation
            mget_times = []
            keys = [f"benchmark:set:{i}" for i in range(100)]

            for _ in range(100):
                start = time.time()
                await redis_client.mget(*keys)
                mget_times.append((time.time() - start) * 1000)

            operations["mget"] = {
                "operations": 100,
                "avg_ms": statistics.mean(mget_times),
                "min_ms": min(mget_times),
                "max_ms": max(mget_times),
                "p95_ms": self.percentile(mget_times, 95),
                "ops_per_second": 100 / sum(mget_times) * 1000,
            }

            # Cleanup
            for i in range(1000):
                await redis_client.delete(f"benchmark:set:{i}")

            return {
                "status": "success",
                "operations": operations,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def benchmark_cache_performance(self) -> Dict[str, Any]:
        """Benchmark cache service performance."""
        try:
            cache_service = CacheService()
            operations = {}

            # Benchmark cache SET
            set_times = []
            test_data = {"key": "value", "nested": {"data": "test"}}

            for i in range(500):
                start = time.time()
                await cache_service.set("benchmark", f"cache_key_{i}", test_data)
                set_times.append((time.time() - start) * 1000)

            operations["set"] = {
                "operations": 500,
                "avg_ms": statistics.mean(set_times),
                "min_ms": min(set_times),
                "max_ms": max(set_times),
                "p95_ms": self.percentile(set_times, 95),
                "ops_per_second": 500 / sum(set_times) * 1000,
            }

            # Benchmark cache GET
            get_times = []
            for i in range(500):
                start = time.time()
                await cache_service.get("benchmark", f"cache_key_{i}")
                get_times.append((time.time() - start) * 1000)

            operations["get"] = {
                "operations": 500,
                "avg_ms": statistics.mean(get_times),
                "min_ms": min(get_times),
                "max_ms": max(get_times),
                "p95_ms": self.percentile(get_times, 95),
                "ops_per_second": 500 / sum(get_times) * 1000,
            }

            # Benchmark get_or_set (cache hit)
            hit_times = []
            for i in range(100):
                start = time.time()
                await cache_service.get_or_set(
                    "benchmark", f"cache_key_{i}", lambda: test_data
                )
                hit_times.append((time.time() - start) * 1000)

            operations["get_or_set_hit"] = {
                "operations": 100,
                "avg_ms": statistics.mean(hit_times),
                "min_ms": min(hit_times),
                "max_ms": max(hit_times),
                "p95_ms": self.percentile(hit_times, 95),
                "ops_per_second": 100 / sum(hit_times) * 1000,
            }

            # Cleanup
            for i in range(500):
                await cache_service.delete("benchmark", f"cache_key_{i}")

            return {
                "status": "success",
                "operations": operations,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def benchmark_session_performance(self) -> Dict[str, Any]:
        """Benchmark session service performance."""
        try:
            session_service = SessionService()
            operations = {}

            # Benchmark session creation
            create_times = []
            session_ids = []

            for i in range(100):
                start = time.time()
                session_id = await session_service.create_session(
                    user_id=f"user_{i}",
                    workspace_id=f"workspace_{i}",
                    metadata={"benchmark": True},
                )
                create_times.append((time.time() - start) * 1000)
                session_ids.append(session_id)

            operations["create"] = {
                "operations": 100,
                "avg_ms": statistics.mean(create_times),
                "min_ms": min(create_times),
                "max_ms": max(create_times),
                "p95_ms": self.percentile(create_times, 95),
                "ops_per_second": 100 / sum(create_times) * 1000,
            }

            # Benchmark session retrieval
            get_times = []
            for session_id in session_ids:
                start = time.time()
                await session_service.get_session(session_id)
                get_times.append((time.time() - start) * 1000)

            operations["get"] = {
                "operations": 100,
                "avg_ms": statistics.mean(get_times),
                "min_ms": min(get_times),
                "max_ms": max(get_times),
                "p95_ms": self.percentile(get_times, 95),
                "ops_per_second": 100 / sum(get_times) * 1000,
            }

            # Benchmark session update
            update_times = []
            for session_id in session_ids[:50]:
                start = time.time()
                await session_service.update_session(
                    session_id, {"last_activity": datetime.utcnow().isoformat()}
                )
                update_times.append((time.time() - start) * 1000)

            operations["update"] = {
                "operations": 50,
                "avg_ms": statistics.mean(update_times),
                "min_ms": min(update_times),
                "max_ms": max(update_times),
                "p95_ms": self.percentile(update_times, 95),
                "ops_per_second": 50 / sum(update_times) * 1000,
            }

            # Cleanup
            for session_id in session_ids:
                await session_service.delete_session(session_id)

            return {
                "status": "success",
                "operations": operations,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def benchmark_rate_limit_performance(self) -> Dict[str, Any]:
        """Benchmark rate limiting performance."""
        try:
            rate_limit_service = RateLimitService()
            operations = {}

            # Benchmark rate limit check
            check_times = []
            for i in range(1000):
                start = time.time()
                await rate_limit_service.check_limit(f"user_{i}", "/test", 100, 60)
                check_times.append((time.time() - start) * 1000)

            operations["check_limit"] = {
                "operations": 1000,
                "avg_ms": statistics.mean(check_times),
                "min_ms": min(check_times),
                "max_ms": max(check_times),
                "p95_ms": self.percentile(check_times, 95),
                "ops_per_second": 1000 / sum(check_times) * 1000,
            }

            # Benchmark rate limit record
            record_times = []
            for i in range(1000):
                start = time.time()
                await rate_limit_service.record_request(f"user_{i}", "/test")
                record_times.append((time.time() - start) * 1000)

            operations["record_request"] = {
                "operations": 1000,
                "avg_ms": statistics.mean(record_times),
                "min_ms": min(record_times),
                "max_ms": max(record_times),
                "p95_ms": self.percentile(record_times, 95),
                "ops_per_second": 1000 / sum(record_times) * 1000,
            }

            return {
                "status": "success",
                "operations": operations,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def benchmark_queue_performance(self) -> Dict[str, Any]:
        """Benchmark queue service performance."""
        try:
            queue_service = QueueService()
            operations = {}

            # Benchmark enqueue
            enqueue_times = []
            job_ids = []

            for i in range(500):
                start = time.time()
                job_id = await queue_service.enqueue(
                    "benchmark_queue", {"data": f"test_{i}"}
                )
                enqueue_times.append((time.time() - start) * 1000)
                job_ids.append(job_id)

            operations["enqueue"] = {
                "operations": 500,
                "avg_ms": statistics.mean(enqueue_times),
                "min_ms": min(enqueue_times),
                "max_ms": max(enqueue_times),
                "p95_ms": self.percentile(enqueue_times, 95),
                "ops_per_second": 500 / sum(enqueue_times) * 1000,
            }

            # Benchmark dequeue
            dequeue_times = []
            for _ in range(500):
                start = time.time()
                await queue_service.dequeue("benchmark_queue")
                dequeue_times.append((time.time() - start) * 1000)

            operations["dequeue"] = {
                "operations": 500,
                "avg_ms": statistics.mean(dequeue_times),
                "min_ms": min(dequeue_times),
                "max_ms": max(dequeue_times),
                "p95_ms": self.percentile(dequeue_times, 95),
                "ops_per_second": 500 / sum(dequeue_times) * 1000,
            }

            # Benchmark peek
            peek_times = []
            for _ in range(100):
                start = time.time()
                await queue_service.peek("benchmark_queue")
                peek_times.append((time.time() - start) * 1000)

            operations["peek"] = {
                "operations": 100,
                "avg_ms": statistics.mean(peek_times),
                "min_ms": min(peek_times),
                "max_ms": max(peek_times),
                "p95_ms": self.percentile(peek_times, 95),
                "ops_per_second": 100 / sum(peek_times) * 1000,
            }

            # Cleanup
            await queue_service.clear_queue("benchmark_queue")

            return {
                "status": "success",
                "operations": operations,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def benchmark_lock_performance(self) -> Dict[str, Any]:
        """Benchmark distributed lock performance."""
        try:
            distributed_lock = DistributedLock()
            operations = {}

            # Benchmark lock acquisition
            acquire_times = []
            resources = [f"resource_{i}" for i in range(100)]

            for resource in resources:
                start = time.time()
                await distributed_lock.acquire(resource, timeout=30)
                acquire_times.append((time.time() - start) * 1000)

            operations["acquire"] = {
                "operations": 100,
                "avg_ms": statistics.mean(acquire_times),
                "min_ms": min(acquire_times),
                "max_ms": max(acquire_times),
                "p95_ms": self.percentile(acquire_times, 95),
                "ops_per_second": 100 / sum(acquire_times) * 1000,
            }

            # Benchmark lock release
            release_times = []
            for resource in resources:
                start = time.time()
                await distributed_lock.release(resource)
                release_times.append((time.time() - start) * 1000)

            operations["release"] = {
                "operations": 100,
                "avg_ms": statistics.mean(release_times),
                "min_ms": min(release_times),
                "max_ms": max(release_times),
                "p95_ms": self.percentile(release_times, 95),
                "ops_per_second": 100 / sum(release_times) * 1000,
            }

            # Benchmark context manager
            context_times = []
            for i in range(50):
                start = time.time()
                async with distributed_lock(f"context_resource_{i}"):
                    pass
                context_times.append((time.time() - start) * 1000)

            operations["context_manager"] = {
                "operations": 50,
                "avg_ms": statistics.mean(context_times),
                "min_ms": min(context_times),
                "max_ms": max(context_times),
                "p95_ms": self.percentile(context_times, 95),
                "ops_per_second": 50 / sum(context_times) * 1000,
            }

            return {
                "status": "success",
                "operations": operations,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def benchmark_concurrent_operations(self) -> Dict[str, Any]:
        """Benchmark concurrent operations."""
        try:
            redis_client = RedisClient()
            operations = {}

            # Concurrent SET operations
            async def concurrent_set(start_id: int, count: int):
                times = []
                for i in range(start_id, start_id + count):
                    start = time.time()
                    await redis_client.set(f"concurrent:{i}", f"value_{i}")
                    times.append((time.time() - start) * 1000)
                return times

            # Run 10 concurrent SET operations, each with 100 operations
            tasks = []
            for i in range(10):
                task = asyncio.create_task(concurrent_set(i * 100, 100))
                tasks.append(task)

            all_times = await asyncio.gather(*tasks)
            flat_times = [time for sublist in all_times for time in sublist]

            operations["concurrent_set"] = {
                "operations": 1000,
                "avg_ms": statistics.mean(flat_times),
                "min_ms": min(flat_times),
                "max_ms": max(flat_times),
                "p95_ms": self.percentile(flat_times, 95),
                "ops_per_second": 1000 / sum(flat_times) * 1000,
                "concurrency": 10,
            }

            # Cleanup
            for i in range(1000):
                await redis_client.delete(f"concurrent:{i}")

            return {
                "status": "success",
                "operations": operations,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def benchmark_memory_operations(self) -> Dict[str, Any]:
        """Benchmark memory operations."""
        try:
            operations = {}

            # Benchmark JSON serialization/deserialization
            import json

            test_data = {
                "users": [
                    {"id": i, "name": f"user_{i}", "data": "x" * 100}
                    for i in range(100)
                ],
                "metadata": {"timestamp": datetime.utcnow().isoformat(), "version": 1},
            }

            serialize_times = []
            for _ in range(1000):
                start = time.time()
                json.dumps(test_data)
                serialize_times.append((time.time() - start) * 1000)

            operations["json_serialize"] = {
                "operations": 1000,
                "avg_ms": statistics.mean(serialize_times),
                "min_ms": min(serialize_times),
                "max_ms": max(serialize_times),
                "p95_ms": self.percentile(serialize_times, 95),
                "ops_per_second": 1000 / sum(serialize_times) * 1000,
            }

            # Benchmark JSON deserialization
            json_str = json.dumps(test_data)
            deserialize_times = []
            for _ in range(1000):
                start = time.time()
                json.loads(json_str)
                deserialize_times.append((time.time() - start) * 1000)

            operations["json_deserialize"] = {
                "operations": 1000,
                "avg_ms": statistics.mean(deserialize_times),
                "min_ms": min(deserialize_times),
                "max_ms": max(deserialize_times),
                "p95_ms": self.percentile(deserialize_times, 95),
                "ops_per_second": 1000 / sum(deserialize_times) * 1000,
            }

            return {
                "status": "success",
                "operations": operations,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    def percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]

    def generate_summary(self) -> Dict[str, Any]:
        """Generate benchmark summary."""
        summary = {
            "total_benchmarks": len(self.results),
            "successful": 0,
            "failed": 0,
            "performance_metrics": {},
            "slowest_operations": [],
        }

        all_operations = []

        for benchmark_name, result in self.results.items():
            status = result.get("status", "unknown")
            summary[status] = summary.get(status, 0) + 1

            if status == "success" and "operations" in result:
                for op_name, op_data in result["operations"].items():
                    if isinstance(op_data, dict) and "avg_ms" in op_data:
                        all_operations.append(
                            {
                                "benchmark": benchmark_name,
                                "operation": op_name,
                                "avg_ms": op_data["avg_ms"],
                                "ops_per_second": op_data.get("ops_per_second", 0),
                            }
                        )

        # Sort by slowest operations
        all_operations.sort(key=lambda x: x["avg_ms"], reverse=True)
        summary["slowest_operations"] = all_operations[:10]

        # Calculate overall performance metrics
        if all_operations:
            summary["performance_metrics"] = {
                "total_operations_tested": len(all_operations),
                "avg_response_time_ms": statistics.mean(
                    [op["avg_ms"] for op in all_operations]
                ),
                "max_ops_per_second": max(
                    [op["ops_per_second"] for op in all_operations]
                ),
                "min_ops_per_second": min(
                    [op["ops_per_second"] for op in all_operations]
                ),
            }

        return summary

    def print_report(self, report: Dict[str, Any]):
        """Print formatted benchmark report."""
        print("\n" + "=" * 60)
        print("RAPTORFLOW BENCHMARK REPORT")
        print("=" * 60)
        print(f"Status: {report['status'].upper()}")
        print(f"Timestamp: {report['timestamp']}")
        print(f"Duration: {report['duration_seconds']:.2f}s")
        print()

        # Summary
        summary = report["summary"]
        print("SUMMARY:")
        print(f"  Total benchmarks: {summary['total_benchmarks']}")
        print(f"  Successful: {summary['successful']}")
        print(f"  Failed: {summary['failed']}")
        print()

        # Performance metrics
        if "performance_metrics" in summary:
            metrics = summary["performance_metrics"]
            print("PERFORMANCE METRICS:")
            print(f"  Total operations tested: {metrics['total_operations_tested']}")
            print(f"  Average response time: {metrics['avg_response_time_ms']:.2f}ms")
            print(f"  Max ops/sec: {metrics['max_ops_per_second']:.0f}")
            print(f"  Min ops/sec: {metrics['min_ops_per_second']:.0f}")
            print()

        # Slowest operations
        if summary["slowest_operations"]:
            print("SLOWEST OPERATIONS:")
            for i, op in enumerate(summary["slowest_operations"][:5], 1):
                print(
                    f"  {i}. {op['benchmark']}.{op['operation']}: {op['avg_ms']:.2f}ms"
                )
            print()

        # Individual benchmarks
        print("DETAILED BENCHMARKS:")
        for benchmark_name, result in report["benchmarks"].items():
            status_icon = {
                "success": "Γ£à",
                "partial": "ΓÜá∩╕Å",
                "failed": "Γ¥î",
            }.get(result["status"], "Γ¥ô")

            print(f"  {status_icon} {benchmark_name.upper()}: {result['status']}")

            if result["status"] == "success" and "operations" in result:
                for op_name, op_data in result["operations"].items():
                    if isinstance(op_data, dict) and "avg_ms" in op_data:
                        print(
                            f"    {op_name}: {op_data['avg_ms']:.2f}ms avg, {op_data.get('ops_per_second', 0):.0f} ops/sec"
                        )

            if "error" in result:
                print(f"    Error: {result['error']}")

        print()
        print("=" * 60)


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Raptorflow benchmark script")
    parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="Output format"
    )
    parser.add_argument("--output", help="Output file (default: stdout)")
    parser.add_argument(
        "--compare", help="Compare with previous benchmark results file"
    )

    args = parser.parse_args()

    # Run benchmarks
    benchmark_script = BenchmarkScript()
    report = await benchmark_script.run_benchmarks()

    # Compare with previous results if requested
    if args.compare:
        try:
            with open(args.compare, "r") as f:
                previous_report = json.load(f)
            report["comparison"] = benchmark_script.compare_results(
                previous_report, report
            )
        except Exception as e:
            logger.warning(f"Could not compare with previous results: {e}")

    # Output results
    if args.format == "json":
        output = json.dumps(report, indent=2)
    else:
        output = str(report)
        benchmark_script.print_report(report)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        logger.info(f"Benchmark results saved to {args.output}")
    else:
        print(output)

    return report["status"]

    def compare_results(
        self, previous: Dict[str, Any], current: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare benchmark results with previous run."""
        comparison = {
            "timestamp_previous": previous["timestamp"],
            "timestamp_current": current["timestamp"],
            "improvements": [],
            "regressions": [],
            "unchanged": [],
        }

        for benchmark_name in current["benchmarks"]:
            if benchmark_name in previous["benchmarks"]:
                prev_result = previous["benchmarks"][benchmark_name]
                curr_result = current["benchmarks"][benchmark_name]

                if (
                    prev_result["status"] == "success"
                    and curr_result["status"] == "success"
                ):
                    for op_name in curr_result["operations"]:
                        if op_name in prev_result["operations"]:
                            prev_ops = prev_result["operations"][op_name]
                            curr_ops = curr_result["operations"][op_name]

                            if isinstance(prev_ops, dict) and isinstance(
                                curr_ops, dict
                            ):
                                prev_avg = prev_ops.get("avg_ms", 0)
                                curr_avg = curr_ops.get("avg_ms", 0)

                                change_pct = (
                                    ((prev_avg - curr_avg) / prev_avg) * 100
                                    if prev_avg > 0
                                    else 0
                                )

                                if abs(change_pct) > 5:  # Only show significant changes
                                    change_info = {
                                        "benchmark": benchmark_name,
                                        "operation": op_name,
                                        "previous_ms": prev_avg,
                                        "current_ms": curr_avg,
                                        "change_percent": change_pct,
                                    }

                                    if change_pct > 0:
                                        comparison["improvements"].append(change_info)
                                    elif change_pct < 0:
                                        comparison["regressions"].append(change_info)
                                    else:
                                        comparison["unchanged"].append(change_info)

        return comparison


if __name__ == "__main__":
    asyncio.run(main())
