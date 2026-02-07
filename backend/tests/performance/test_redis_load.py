"""
Redis Load Testing Script
Tests Redis performance under various load conditions
"""

import pytest

pytest.skip(
    "Archived script-style module; not collected in canonical suite.",
    allow_module_level=True,
)

import asyncio
import json
import statistics
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List

from ..redis_core.client import get_redis
from ..redis_core.rate_limit import RateLimitService
from ..redis_core.session import SessionService
from ..services.coordination import get_lock_manager
from ..services.llm_cache import get_semantic_cache


class RedisLoadTester:
    """Comprehensive load testing for Redis services"""

    def __init__(self):
        self.redis = get_redis()
        self.session_service = SessionService()
        self.rate_limiter = RateLimitService()
        self.semantic_cache = get_semantic_cache()
        self.lock_manager = get_lock_manager()
        self.results = {}

    async def run_all_tests(self):
        """Run all load tests"""
        print("🚀 Starting Redis Load Testing")
        print("=" * 50)

        await self.test_basic_operations_load()
        await self.test_session_management_load()
        await self.test_rate_limiting_load()
        await self.test_semantic_cache_load()
        await self.test_distributed_locks_load()
        await self.test_mixed_workload()

        self.generate_report()

    async def test_basic_operations_load(self):
        """Test basic Redis operations under load"""
        print("\n📊 Testing Basic Operations Load...")

        # Test SET/GET operations
        set_get_times = []
        num_operations = 1000

        for i in range(num_operations):
            start_time = time.time()

            # SET operation
            await self.redis.set(f"load_test:{i}", f"value:{i}", ex=300)

            # GET operation
            value = await self.redis.get(f"load_test:{i}")

            end_time = time.time()
            operation_time = (end_time - start_time) * 1000  # Convert to ms
            set_get_times.append(operation_time)

            if i % 100 == 0:
                print(f"  Progress: {i}/{num_operations} operations")

        # Cleanup
        cleanup_keys = [f"load_test:{i}" for i in range(num_operations)]
        if cleanup_keys:
            await self.redis.delete(*cleanup_keys)

        # Calculate metrics
        avg_time = statistics.mean(set_get_times)
        p95_time = statistics.quantiles(set_get_times, n=20)[18]  # 95th percentile
        ops_per_sec = num_operations / (sum(set_get_times) / 1000)

        self.results["basic_operations"] = {
            "operations": num_operations,
            "avg_time_ms": avg_time,
            "p95_time_ms": p95_time,
            "ops_per_second": ops_per_sec,
            "total_time_s": sum(set_get_times) / 1000,
        }

        print(f"  ✅ {num_operations} operations completed")
        print(f"  📈 Average: {avg_time:.2f}ms, P95: {p95_time:.2f}ms")
        print(f"  ⚡ Throughput: {ops_per_sec:.0f} ops/sec")

    async def test_session_management_load(self):
        """Test session management under load"""
        print("\n👥 Testing Session Management Load...")

        session_times = []
        num_sessions = 500

        for i in range(num_sessions):
            start_time = time.time()

            # Create session
            session = await self.session_service.create_session(
                f"user{i}", f"workspace{i}"
            )

            # Retrieve session
            retrieved = await self.session_service.get_session(session.id)

            # Update session
            await self.session_service.update_session(
                session.id, {"last_activity": datetime.now()}
            )

            end_time = time.time()
            operation_time = (end_time - start_time) * 1000
            session_times.append(operation_time)

            if i % 50 == 0:
                print(f"  Progress: {i}/{num_sessions} sessions")

        # Calculate metrics
        avg_time = statistics.mean(session_times)
        p95_time = statistics.quantiles(session_times, n=20)[18]
        sessions_per_sec = num_sessions / (sum(session_times) / 1000)

        self.results["session_management"] = {
            "sessions": num_sessions,
            "avg_time_ms": avg_time,
            "p95_time_ms": p95_time,
            "sessions_per_second": sessions_per_sec,
            "total_time_s": sum(session_times) / 1000,
        }

        print(f"  ✅ {num_sessions} sessions processed")
        print(f"  📈 Average: {avg_time:.2f}ms, P95: {p95_time:.2f}ms")
        print(f"  ⚡ Throughput: {sessions_per_sec:.0f} sessions/sec")

    async def test_rate_limiting_load(self):
        """Test rate limiting under load"""
        print("\n🚦 Testing Rate Limiting Load...")

        rate_limit_times = []
        num_checks = 1000

        for i in range(num_checks):
            start_time = time.time()

            # Check rate limit for different users and endpoints
            user_id = f"user{i % 100}"  # 100 different users
            endpoint = ["api", "auth", "search"][i % 3]

            allowed = await self.rate_limiter.check_limit(user_id, endpoint)

            end_time = time.time()
            operation_time = (end_time - start_time) * 1000
            rate_limit_times.append(operation_time)

            if i % 100 == 0:
                print(f"  Progress: {i}/{num_checks} checks")

        # Calculate metrics
        avg_time = statistics.mean(rate_limit_times)
        p95_time = statistics.quantiles(rate_limit_times, n=20)[18]
        checks_per_sec = num_checks / (sum(rate_limit_times) / 1000)

        self.results["rate_limiting"] = {
            "checks": num_checks,
            "avg_time_ms": avg_time,
            "p95_time_ms": p95_time,
            "checks_per_second": checks_per_sec,
            "total_time_s": sum(rate_limit_times) / 1000,
        }

        print(f"  ✅ {num_checks} rate limit checks completed")
        print(f"  📈 Average: {avg_time:.2f}ms, P95: {p95_time:.2f}ms")
        print(f"  ⚡ Throughput: {checks_per_sec:.0f} checks/sec")

    async def test_semantic_cache_load(self):
        """Test semantic cache under load"""
        print("\n🧠 Testing Semantic Cache Load...")

        cache_times = []
        num_operations = 200

        # Prepare test data
        queries = [
            f"What are the marketing strategies for company {i}?"
            for i in range(num_operations)
        ]

        responses = [
            {"answer": f"Marketing strategy {i}", "confidence": 0.9}
            for i in range(num_operations)
        ]

        # Cache all responses
        print("  📝 Caching responses...")
        cache_start = time.time()
        for query, response in zip(queries, responses):
            start_time = time.time()
            await self.semantic_cache.cache_response(query, response)
            end_time = time.time()
            cache_times.append((end_time - start_time) * 1000)

        cache_time_total = time.time() - cache_start

        # Test cache retrieval
        print("  🔍 Testing cache retrieval...")
        retrieval_times = []
        hit_count = 0

        for query in queries:
            start_time = time.time()
            result = await self.semantic_cache.get_cached_response(query)
            end_time = time.time()

            retrieval_times.append((end_time - start_time) * 1000)
            if result:
                hit_count += 1

        # Calculate metrics
        avg_cache_time = statistics.mean(cache_times)
        avg_retrieval_time = statistics.mean(retrieval_times)
        cache_ops_per_sec = num_operations / cache_time_total

        self.results["semantic_cache"] = {
            "operations": num_operations,
            "avg_cache_time_ms": avg_cache_time,
            "avg_retrieval_time_ms": avg_retrieval_time,
            "cache_ops_per_second": cache_ops_per_sec,
            "hit_rate": hit_count / num_operations,
            "total_time_s": cache_time_total,
        }

        print(f"  ✅ {num_operations} cache operations completed")
        print(f"  📝 Cache avg: {avg_cache_time:.2f}ms")
        print(f"  🔍 Retrieval avg: {avg_retrieval_time:.2f}ms")
        print(f"  🎯 Hit rate: {(hit_count/num_operations)*100:.1f}%")
        print(f"  ⚡ Throughput: {cache_ops_per_sec:.0f} ops/sec")

    async def test_distributed_locks_load(self):
        """Test distributed locks under contention"""
        print("\n🔒 Testing Distributed Locks Load...")

        lock_times = []
        num_locks = 200
        num_workers = 10

        async def lock_worker(worker_id: int):
            """Worker that acquires and releases locks"""
            worker_times = []

            for i in range(num_locks // num_workers):
                lock_id = f"load_test_lock:{worker_id}_{i}"

                start_time = time.time()
                lock = await self.lock_manager.create_lock(lock_id, timeout=5)

                acquired = await lock.acquire()
                if acquired:
                    # Simulate some work
                    await asyncio.sleep(0.01)
                    await lock.release()

                end_time = time.time()
                worker_times.append((end_time - start_time) * 1000)

            return worker_times

        # Run multiple workers concurrently
        print(f"  👥 Starting {num_workers} concurrent workers...")
        start_time = time.time()

        tasks = [lock_worker(i) for i in range(num_workers)]
        worker_results = await asyncio.gather(*tasks)

        total_time = time.time() - start_time

        # Flatten results
        all_lock_times = [
            time for worker_times in worker_results for time in worker_times
        ]

        # Calculate metrics
        avg_time = statistics.mean(all_lock_times)
        p95_time = statistics.quantiles(all_lock_times, n=20)[18]
        locks_per_sec = len(all_lock_times) / total_time

        self.results["distributed_locks"] = {
            "locks": len(all_lock_times),
            "workers": num_workers,
            "avg_time_ms": avg_time,
            "p95_time_ms": p95_time,
            "locks_per_second": locks_per_sec,
            "total_time_s": total_time,
        }

        print(f"  ✅ {len(all_lock_times)} lock operations completed")
        print(f"  📈 Average: {avg_time:.2f}ms, P95: {p95_time:.2f}ms")
        print(f"  ⚡ Throughput: {locks_per_sec:.0f} locks/sec")

    async def test_mixed_workload(self):
        """Test mixed workload simulating real usage"""
        print("\n🔄 Testing Mixed Workload...")

        async def mixed_worker(worker_id: int):
            """Worker performing mixed operations"""
            worker_times = []

            for i in range(50):
                start_time = time.time()

                operation = i % 5
                if operation == 0:
                    # Basic operation
                    await self.redis.set(f"mixed:{worker_id}:{i}", f"value:{i}")
                    await self.redis.get(f"mixed:{worker_id}:{i}")

                elif operation == 1:
                    # Session operation
                    session = await self.session_service.create_session(
                        f"user{worker_id}", f"workspace{worker_id}"
                    )
                    await self.session_service.get_session(session.id)

                elif operation == 2:
                    # Rate limit check
                    await self.rate_limiter.check_limit(f"user{worker_id}", "api")

                elif operation == 3:
                    # Cache operation
                    query = f"Mixed query {worker_id}_{i}"
                    await self.semantic_cache.cache_response(
                        query, {"answer": f"Response {i}"}
                    )
                    await self.semantic_cache.get_cached_response(query)

                elif operation == 4:
                    # Lock operation
                    lock = await self.lock_manager.create_lock(
                        f"mixed_lock:{worker_id}:{i}"
                    )
                    if await lock.acquire():
                        await lock.release()

                end_time = time.time()
                worker_times.append((end_time - start_time) * 1000)

            return worker_times

        # Run mixed workload
        num_workers = 20
        print(f"  👥 Starting {num_workers} mixed workload workers...")

        start_time = time.time()
        tasks = [mixed_worker(i) for i in range(num_workers)]
        worker_results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time

        # Flatten results
        all_times = [time for worker_times in worker_results for time in worker_times]

        # Calculate metrics
        avg_time = statistics.mean(all_times)
        p95_time = statistics.quantiles(all_times, n=20)[18]
        ops_per_sec = len(all_times) / total_time

        self.results["mixed_workload"] = {
            "operations": len(all_times),
            "workers": num_workers,
            "avg_time_ms": avg_time,
            "p95_time_ms": p95_time,
            "ops_per_second": ops_per_sec,
            "total_time_s": total_time,
        }

        print(f"  ✅ {len(all_times)} mixed operations completed")
        print(f"  📈 Average: {avg_time:.2f}ms, P95: {p95_time:.2f}ms")
        print(f"  ⚡ Throughput: {ops_per_sec:.0f} ops/sec")

    def generate_report(self):
        """Generate comprehensive load test report"""
        print("\n" + "=" * 50)
        print("📊 REDIS LOAD TEST REPORT")
        print("=" * 50)

        for test_name, results in self.results.items():
            print(f"\n🔸 {test_name.upper().replace('_', ' ')}")
            print("-" * 30)

            for key, value in results.items():
                if isinstance(value, float):
                    if "time" in key:
                        print(f"  {key}: {value:.2f}")
                    elif "rate" in key or "per_second" in key:
                        print(f"  {key}: {value:.0f}")
                    else:
                        print(f"  {key}: {value:.3f}")
                else:
                    print(f"  {key}: {value}")

        # Summary
        print(f"\n🎯 PERFORMANCE SUMMARY")
        print("-" * 30)

        if "basic_operations" in self.results:
            print(
                f"  Basic Ops: {self.results['basic_operations']['ops_per_second']:.0f} ops/sec"
            )
        if "session_management" in self.results:
            print(
                f"  Sessions: {self.results['session_management']['sessions_per_second']:.0f} sessions/sec"
            )
        if "rate_limiting" in self.results:
            print(
                f"  Rate Limits: {self.results['rate_limiting']['checks_per_second']:.0f} checks/sec"
            )
        if "semantic_cache" in self.results:
            print(
                f"  Cache: {self.results['semantic_cache']['cache_ops_per_second']:.0f} ops/sec"
            )
        if "distributed_locks" in self.results:
            print(
                f"  Locks: {self.results['distributed_locks']['locks_per_second']:.0f} locks/sec"
            )
        if "mixed_workload" in self.results:
            print(
                f"  Mixed: {self.results['mixed_workload']['ops_per_second']:.0f} ops/sec"
            )

        print(f"\n✅ Load testing completed at {datetime.now().isoformat()}")

        # Save report to file
        report_file = (
            f"redis_load_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_file, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"📄 Detailed report saved to: {report_file}")


async def main():
    """Main function to run load tests"""
    tester = RedisLoadTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    print("🚀 Redis Load Testing Tool")
    print("This will test Redis performance under various load conditions")
    print("Press Ctrl+C to stop\n")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Load testing stopped by user")
    except Exception as e:
        print(f"\n❌ Load testing failed: {e}")
        import traceback

        traceback.print_exc()
