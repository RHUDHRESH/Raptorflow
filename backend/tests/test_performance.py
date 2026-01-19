"""
Enhanced performance tests for RaptorFlow backend.
Tests session management, performance optimization, and resource pooling under load.
"""

import asyncio
import statistics
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timedelta
import pytest
import psutil
import gc

from backend.core.sessions import RedisSessionManager, SessionType
from backend.core.performance import PerformanceOptimizer, ResourceMonitor
from backend.core.resource_pool import ConnectionPool, MemoryBufferPool
from backend.core.metrics import MetricsCollector, MetricType

# Performance test configuration
PERFORMANCE_CONFIG = {
    "load_test_users": 100,
    "stress_test_duration": 60,  # seconds
    "response_time_threshold": 2.0,  # seconds
    "memory_threshold_mb": 512,  # MB
    "cpu_threshold_percent": 80,
}



class TestSessionPerformance:
    """Test session management performance."""
    
    @pytest.mark.asyncio
    async def test_concurrent_session_creation(self):
        """Test concurrent session creation performance."""
        with patch('core.sessions.redis.from_url') as mock_redis:
            mock_client = AsyncMock()
            mock_client.ping.return_value = True
            mock_client.setex.return_value = True
            mock_redis.return_value = mock_client
            
            session_manager = RedisSessionManager(
                redis_url="redis://localhost:6379",
                secret_key="test-secret"
            )
            await session_manager.initialize()
            
            # Create many sessions concurrently
            start_time = time.time()
            
            tasks = []
            for i in range(100):
                task = asyncio.create_task(
                    session_manager.create_session(
                        user_id=f"user-{i}",
                        workspace_id="test-workspace"
                    )
                )
                tasks.append(task)
            
            session_ids = await asyncio.gather(*tasks)
            end_time = time.time()
            
            # Verify all sessions were created
            assert len([sid for sid in session_ids if sid is not None]) == 100
            
            # Check performance (should be under 5 seconds for 100 sessions)
            creation_time = end_time - start_time
            assert creation_time < 5.0
            
            await session_manager.stop()
    
    @pytest.mark.asyncio
    async def test_session_memory_efficiency(self):
        """Test session memory usage under load."""
        with patch('core.sessions.redis.from_url') as mock_redis:
            mock_client = AsyncMock()
            mock_client.ping.return_value = True
            mock_redis.return_value = mock_client
            
            session_manager = RedisSessionManager(
                redis_url="redis://localhost:6379",
                secret_key="test-secret"
            )
            await session_manager.initialize()
            
            # Get initial memory
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Create many sessions
            for i in range(1000):
                await session_manager.create_session(
                    user_id=f"user-{i}",
                    workspace_id="test-workspace"
                )
                
                if i % 100 == 0:
                    gc.collect()  # Force garbage collection
            
            # Get final memory
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            # Memory increase should be reasonable (< 100MB for 1000 sessions)
            assert memory_increase < 100
            
            await session_manager.stop()


class TestResourcePoolingPerformance:
    """Test resource pooling performance."""
    
    @pytest.mark.asyncio
    async def test_pool_performance_under_load(self):
        """Test pool performance under high load."""
        pool = ConnectionPool(
            pool_name="load-test-pool",
            connection_factory=lambda: {"id": str(uuid.uuid4())},
            max_size=20
        )
        
        await pool.start()
        
        # Acquire and release many connections concurrently
        async def acquire_release_cycle():
            conn = pool.acquire(timeout=1.0)
            await asyncio.sleep(0.01)  # Simulate work
            pool.release(conn)
        
        # Run many cycles concurrently
        tasks = [acquire_release_cycle() for _ in range(100)]
        start_time = time.time()
        
        await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Check performance
        execution_time = end_time - start_time
        assert execution_time < 5.0  # Should complete quickly
        
        # Check pool statistics
        stats = pool.get_statistics()
        assert stats.total_acquisitions == 100
        assert stats.total_releases == 100
        assert stats.peak_usage <= pool.max_size
        
        await pool.stop()
    
    @pytest.mark.asyncio
    async def test_memory_pool_efficiency(self):
        """Test memory pool efficiency."""
        pool = MemoryBufferPool(
            pool_name="memory-efficiency-test",
            buffer_size=1024,
            max_size=10
        )
        
        await pool.start()
        
        # Get initial memory
        process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform many acquire/release cycles
        for i in range(500):
            buffer = pool.acquire()
            # Use buffer
            buffer[0:100] = bytes(range(100))
            
            pooled_buffer = pool._in_use.pop()
            pool.release(pooled_buffer)
            
            if i % 50 == 0:
                gc.collect()
        
        # Check memory efficiency
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be minimal for efficient pooling
        assert memory_increase < 20  # Less than 20MB for 500 cycles
        
        await pool.stop()


class TestPerformanceOptimization:
    """Test performance optimization under load."""
    
    @pytest.mark.asyncio
    async def test_concurrent_optimization(self):
        """Test concurrent optimization requests."""
        optimizer = PerformanceOptimizer()
        
        async def mock_execution(agent_id):
            await asyncio.sleep(0.1)
            return {"agent_id": agent_id, "tokens_used": 50}
        
        # Run many optimizations concurrently
        tasks = []
        start_time = time.time()
        
        for i in range(50):
            task = optimizer.optimize_agent_execution(
                f"agent-{i}", mock_execution, i
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Verify all executions completed
        assert len(results) == 50
        assert all(r["agent_id"] == f"agent-{i}" for i, r in enumerate(results))
        
        # Check performance (should be reasonable)
        execution_time = end_time - start_time
        assert execution_time < 10.0  # Should complete in under 10 seconds
        
        # Check metrics were collected
        assert len(optimizer.metrics_history) == 50
    
    @pytest.mark.asyncio
    async def test_adaptive_optimization(self):
        """Test adaptive optimization level adjustment."""
        optimizer = PerformanceOptimizer()
        
        # Simulate poor performance metrics
        for i in range(20):
            from core.performance import PerformanceMetrics, OptimizationLevel
            
            # Poor performance metrics
            poor_metrics = PerformanceMetrics(
                agent_name="test-agent",
                execution_time=10.0 + i,  # Slow
                memory_usage_mb=800.0,  # High memory
                cpu_usage_percent=90.0,  # High CPU
                tokens_used=50,
                cache_hits=10,  # Poor cache
                cache_misses=90,
                tool_calls=5,
                skill_calls=3,
                error_count=i % 3,  # Some errors
                timestamp=datetime.utcnow(),
                optimization_level=OptimizationLevel.BALANCED
            )
            optimizer.metrics_history.append(poor_metrics)
        
        # Trigger adaptive optimization
        await optimizer._analyze_and_adjust()
        
        # Should upgrade optimization level due to poor performance
        assert optimizer.optimization_level == OptimizationLevel.MAXIMUM


class TestResourceMonitoring:
    """Test resource monitoring performance."""
    
    @pytest.mark.asyncio
    async def test_monitor_overhead(self):
        """Test resource monitoring overhead."""
        monitor = ResourceMonitor(update_interval=0.01)  # Very fast updates
        
        # Get initial CPU usage
        initial_cpu = psutil.cpu_percent(interval=0.1)
        
        monitor.start()
        
        # Let monitor run for a short period
        await asyncio.sleep(0.1)
        
        # Get monitoring overhead
        final_cpu = psutil.cpu_percent(interval=0.1)
        monitor.stop()
        
        # Monitor overhead should be minimal
        cpu_overhead = abs(final_cpu - initial_cpu)
        assert cpu_overhead < 5.0  # Less than 5% CPU overhead
    
    @pytest.mark.asyncio
    async def test_monitor_accuracy(self):
        """Test resource monitoring accuracy."""
        monitor = ResourceMonitor(update_interval=0.05)
        
        monitor.start()
        
        # Wait for multiple updates
        await asyncio.sleep(0.2)
        
        # Get monitored values
        monitored_metrics = monitor.get_current_metrics()
        
        # Get actual system metrics
        actual_cpu = psutil.cpu_percent()
        actual_memory = psutil.virtual_memory().percent
        
        monitor.stop()
        
        # Monitored values should be close to actual values
        assert abs(monitored_metrics["cpu_percent"] - actual_cpu) < 10.0
        assert abs(monitored_metrics["memory_percent"] - actual_memory) < 10.0


class TestIntegrationPerformance:
    """Test integration performance between components."""
    
    @pytest.mark.asyncio
    async def test_session_performance_integration(self):
        """Test session and performance system integration."""
        with patch('core.sessions.redis.from_url') as mock_redis:
            mock_client = AsyncMock()
            mock_client.ping.return_value = True
            mock_redis.return_value = mock_client
            
            # Create components
            session_manager = RedisSessionManager(
                redis_url="redis://localhost:6379",
                secret_key="test-secret"
            )
            optimizer = PerformanceOptimizer()
            metrics_collector = MetricsCollector()
            
            await session_manager.initialize()
            
            # Simulate integrated workflow
            start_time = time.time()
            
            tasks = []
            for i in range(20):
                # Create session
                session_id = await session_manager.create_session(
                    user_id=f"user-{i}",
                    workspace_id="test-workspace"
                )
                
                # Start performance tracking
                execution_id = optimizer.start_tracking(
                    f"execution-{i}", f"agent-{i}", session_id
                )
                
                # Record metrics
                await metrics_collector.record_metric(
                    MetricType.PERFORMANCE,
                    "response_time",
                    0.1 + (i * 0.01),
                    "seconds",
                    agent_name=f"agent-{i}"
                )
                
                # End tracking
                await optimizer.end_tracking(
                    execution_id, f"agent-{i}", session_id
                )
                
                tasks.append(session_id)
            
            await asyncio.gather(*tasks)
            end_time = time.time()
            
            # Verify integration performance
            integration_time = end_time - start_time
            assert integration_time < 5.0  # Should complete quickly
            
            # Verify all components have data
            assert len(optimizer.metrics_history) == 20
            assert len(metrics_collector.metrics_buffer) == 20
            
            await session_manager.stop()

        return {
            "db_client": db_client,
            "redis_client": redis_client,
            "memory_controller": memory_controller,
            "cognitive_engine": cognitive_engine,
            "agent_dispatcher": agent_dispatcher,
        }

    @pytest.mark.asyncio
    async def test_database_performance(self, mock_performance_dependencies):
        """Test database performance under load."""
        db_client = mock_performance_dependencies["db_client"]

        # Measure database query performance
        query_times = []

        for i in range(100):
            start_time = time.time()

            # Simulate database query
            result = db_client.table("test_table").select("*").execute()

            end_time = time.time()
            query_time = end_time - start_time
            query_times.append(query_time)

        # Calculate performance metrics
        avg_query_time = statistics.mean(query_times)
        max_query_time = max(query_times)
        min_query_time = min(query_times)
        p95_query_time = statistics.quantiles(query_times, n=20)[18]  # 95th percentile

        # Assert performance thresholds
        assert (
            avg_query_time < 0.1
        ), f"Average query time {avg_query_time:.3f}s exceeds threshold"
        assert (
            max_query_time < 0.5
        ), f"Max query time {max_query_time:.3f}s exceeds threshold"
        assert (
            p95_query_time < 0.2
        ), f"95th percentile query time {p95_query_time:.3f}s exceeds threshold"

        print(f"Database Performance:")
        print(f"  Average: {avg_query_time:.3f}s")
        print(f"  Min: {min_query_time:.3f}s")
        print(f"  Max: {max_query_time:.3f}s")
        print(f"  95th percentile: {p95_query_time:.3f}s")

    @pytest.mark.asyncio
    async def test_redis_performance(self, mock_performance_dependencies):
        """Test Redis performance under load."""
        redis_client = mock_performance_dependencies["redis_client"]

        # Measure Redis operations performance
        set_times = []
        get_times = []

        for i in range(100):
            # Test SET operation
            start_time = time.time()
            await redis_client.setex(f"test_key_{i}", 3600, f"test_value_{i}")
            end_time = time.time()
            set_times.append(end_time - start_time)

            # Test GET operation
            start_time = time.time()
            await redis_client.get(f"test_key_{i}")
            end_time = time.time()
            get_times.append(end_time - start_time)

        # Calculate performance metrics
        avg_set_time = statistics.mean(set_times)
        avg_get_time = statistics.mean(get_times)

        # Assert performance thresholds
        assert (
            avg_set_time < 0.01
        ), f"Average SET time {avg_set_time:.3f}s exceeds threshold"
        assert (
            avg_get_time < 0.005
        ), f"Average GET time {avg_get_time:.3f}s exceeds threshold"

        print(f"Redis Performance:")
        print(f"  Average SET: {avg_set_time:.3f}s")
        print(f"  Average GET: {avg_get_time:.3f}s")

    @pytest.mark.asyncio
    async def test_memory_search_performance(self, mock_performance_dependencies):
        """Test memory search performance."""
        memory_controller = mock_performance_dependencies["memory_controller"]

        # Measure memory search performance
        search_times = []

        for i in range(50):
            start_time = time.time()

            result = await memory_controller.search(
                workspace_id=f"test_workspace_{i}",
                query=f"test query {i}",
                memory_types=["foundation", "icp"],
                limit=10,
            )

            end_time = time.time()
            search_times.append(end_time - start_time)

        # Calculate performance metrics
        avg_search_time = statistics.mean(search_times)
        max_search_time = max(search_times)

        # Assert performance thresholds
        assert (
            avg_search_time < 0.5
        ), f"Average search time {avg_search_time:.3f}s exceeds threshold"
        assert (
            max_search_time < 1.0
        ), f"Max search time {max_search_time:.3f}s exceeds threshold"

        print(f"Memory Search Performance:")
        print(f"  Average: {avg_search_time:.3f}s")
        print(f"  Max: {max_search_time:.3f}s")

    @pytest.mark.asyncio
    async def test_cognitive_engine_performance(self, mock_performance_dependencies):
        """Test cognitive engine performance."""
        cognitive_engine = mock_performance_dependencies["cognitive_engine"]

        # Measure cognitive operations performance
        perception_times = []
        planning_times = []
        reflection_times = []

        for i in range(20):
            # Test perception
            start_time = time.time()
            await cognitive_engine.perception.perceive(
                text=f"Test text {i}", history=[]
            )
            end_time = time.time()
            perception_times.append(end_time - start_time)

            # Test planning
            start_time = time.time()
            await cognitive_engine.planning.plan(
                goal=f"Test goal {i}", perceived=None, context={}
            )
            end_time = time.time()
            planning_times.append(end_time - start_time)

            # Test reflection
            start_time = time.time()
            await cognitive_engine.reflection.reflect(
                output=f"Test output {i}",
                goal="Test goal",
                context={},
                max_iterations=1,
            )
            end_time = time.time()
            reflection_times.append(end_time - start_time)

        # Calculate performance metrics
        avg_perception_time = statistics.mean(perception_times)
        avg_planning_time = statistics.mean(planning_times)
        avg_reflection_time = statistics.mean(reflection_times)

        # Assert performance thresholds
        assert (
            avg_perception_time < 0.3
        ), f"Average perception time {avg_perception_time:.3f}s exceeds threshold"
        assert (
            avg_planning_time < 0.5
        ), f"Average planning time {avg_planning_time:.3f}s exceeds threshold"
        assert (
            avg_reflection_time < 0.4
        ), f"Average reflection time {avg_reflection_time:.3f}s exceeds threshold"

        print(f"Cognitive Engine Performance:")
        print(f"  Perception: {avg_perception_time:.3f}s")
        print(f"  Planning: {avg_planning_time:.3f}s")
        print(f"  Reflection: {avg_reflection_time:.3f}s")

    @pytest.mark.asyncio
    async def test_agent_execution_performance(self, mock_performance_dependencies):
        """Test agent execution performance."""
        agent_dispatcher = mock_performance_dependencies["agent_dispatcher"]

        # Measure agent execution performance
        execution_times = []

        for i in range(30):
            agent = agent_dispatcher.get_agent("test_agent")

            start_time = time.time()
            await agent.execute(
                {
                    "workspace_id": f"test_workspace_{i}",
                    "user_id": f"test_user_{i}",
                    "input": f"test input {i}",
                }
            )
            end_time = time.time()
            execution_times.append(end_time - start_time)

        # Calculate performance metrics
        avg_execution_time = statistics.mean(execution_times)
        max_execution_time = max(execution_times)

        # Assert performance thresholds
        assert (
            avg_execution_time < 1.0
        ), f"Average execution time {avg_execution_time:.3f}s exceeds threshold"
        assert (
            max_execution_time < 2.0
        ), f"Max execution time {max_execution_time:.3f}s exceeds threshold"

        print(f"Agent Execution Performance:")
        print(f"  Average: {avg_execution_time:.3f}s")
        print(f"  Max: {max_execution_time:.3f}s")

    @pytest.mark.asyncio
    async def test_concurrent_load(self, mock_performance_dependencies):
        """Test system performance under concurrent load."""

        async def simulate_user_request(user_id: int):
            """Simulate a single user request."""
            # Simulate database query
            db_client = mock_performance_dependencies["db_client"]
            await asyncio.sleep(0.01)  # Simulate network latency
            db_result = db_client.table("users").select("*").eq("id", user_id).execute()

            # Simulate memory search
            memory_controller = mock_performance_dependencies["memory_controller"]
            memory_result = await memory_controller.search(
                workspace_id=f"workspace_{user_id}",
                query="test query",
                memory_types=["foundation"],
                limit=5,
            )

            # Simulate agent execution
            agent_dispatcher = mock_performance_dependencies["agent_dispatcher"]
            agent = agent_dispatcher.get_agent("test_agent")
            agent_result = await agent.execute(
                {"user_id": user_id, "input": "test input"}
            )

            return {
                "user_id": user_id,
                "db_result": len(db_result.data),
                "memory_result": len(memory_result),
                "agent_result": agent_result["success"],
            }

        # Run concurrent requests
        start_time = time.time()

        tasks = [
            simulate_user_request(i)
            for i in range(PERFORMANCE_CONFIG["load_test_users"])
        ]
        results = await asyncio.gather(*tasks)

        end_time = time.time()
        total_time = end_time - start_time

        # Calculate performance metrics
        successful_requests = sum(1 for r in results if r["agent_result"])
        requests_per_second = PERFORMANCE_CONFIG["load_test_users"] / total_time
        avg_response_time = total_time / PERFORMANCE_CONFIG["load_test_users"]

        # Assert performance thresholds
        assert (
            successful_requests == PERFORMANCE_CONFIG["load_test_users"]
        ), "Not all requests succeeded"
        assert (
            requests_per_second > 50
        ), f"Requests per second {requests_per_second:.1f} below threshold"
        assert (
            avg_response_time < PERFORMANCE_CONFIG["response_time_threshold"]
        ), f"Average response time {avg_response_time:.3f}s exceeds threshold"

        print(f"Concurrent Load Performance:")
        print(f"  Total requests: {PERFORMANCE_CONFIG['load_test_users']}")
        print(f"  Successful requests: {successful_requests}")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Requests per second: {requests_per_second:.1f}")
        print(f"  Average response time: {avg_response_time:.3f}s")

    @pytest.mark.asyncio
    async def test_memory_usage(self, mock_performance_dependencies):
        """Test memory usage under load."""
        import os

        import psutil

        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Simulate memory-intensive operations
        large_data = []
        for i in range(1000):
            large_data.append(
                {
                    "id": i,
                    "content": "x" * 1000,  # 1KB per item
                    "metadata": {"key": f"value_{i}"},
                }
            )

        # Get peak memory usage
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - initial_memory

        # Assert memory usage thresholds
        assert (
            memory_increase < PERFORMANCE_CONFIG["memory_threshold_mb"]
        ), f"Memory increase {memory_increase:.1f}MB exceeds threshold"

        print(f"Memory Usage Performance:")
        print(f"  Initial memory: {initial_memory:.1f}MB")
        print(f"  Peak memory: {peak_memory:.1f}MB")
        print(f"  Memory increase: {memory_increase:.1f}MB")

        # Clean up
        del large_data

    @pytest.mark.asyncio
    async def test_stress_test(self, mock_performance_dependencies):
        """Test system stability under stress."""
        stress_duration = PERFORMANCE_CONFIG["stress_test_duration"]

        async def stress_worker(worker_id: int):
            """Stress test worker."""
            start_time = time.time()
            operations = 0
            errors = 0

            while time.time() - start_time < stress_duration:
                try:
                    # Perform various operations
                    db_client = mock_performance_dependencies["db_client"]
                    db_client.table("test").select("*").execute()

                    memory_controller = mock_performance_dependencies[
                        "memory_controller"
                    ]
                    await memory_controller.search(
                        workspace_id=f"stress_{worker_id}",
                        query="stress test",
                        memory_types=["test"],
                        limit=5,
                    )

                    operations += 1

                    # Small delay to prevent CPU overload
                    await asyncio.sleep(0.01)

                except Exception:
                    errors += 1

            return {
                "worker_id": worker_id,
                "operations": operations,
                "errors": errors,
                "duration": time.time() - start_time,
            }

        # Run stress test with multiple workers
        num_workers = 10
        start_time = time.time()

        tasks = [stress_worker(i) for i in range(num_workers)]
        results = await asyncio.gather(*tasks)

        end_time = time.time()
        total_duration = end_time - start_time

        # Calculate stress test metrics
        total_operations = sum(r["operations"] for r in results)
        total_errors = sum(r["errors"] for r in results)
        operations_per_second = total_operations / total_duration
        error_rate = (
            (total_errors / total_operations) * 100 if total_operations > 0 else 0
        )

        # Assert stress test thresholds
        assert error_rate < 1.0, f"Error rate {error_rate:.1f}% exceeds threshold"
        assert (
            operations_per_second > 100
        ), f"Operations per second {operations_per_second:.1f} below threshold"

        print(f"Stress Test Results:")
        print(f"  Duration: {total_duration:.1f}s")
        print(f"  Workers: {num_workers}")
        print(f"  Total operations: {total_operations}")
        print(f"  Total errors: {total_errors}")
        print(f"  Operations per second: {operations_per_second:.1f}")
        print(f"  Error rate: {error_rate:.2f}%")


class TestScalability:
    """Test suite for scalability benchmarks."""

    @pytest.mark.asyncio
    async def test_horizontal_scalability(self):
        """Test horizontal scalability."""
        # Test with increasing concurrent users
        user_counts = [10, 50, 100, 200]
        performance_metrics = []

        async def simulate_load(user_count: int):
            """Simulate load with specified user count."""

            async def user_request(user_id: int):
                await asyncio.sleep(0.01)  # Simulate processing time
                return {"user_id": user_id, "success": True}

            start_time = time.time()
            tasks = [user_request(i) for i in range(user_count)]
            results = await asyncio.gather(*tasks)
            end_time = time.time()

            return {
                "user_count": user_count,
                "duration": end_time - start_time,
                "success_rate": sum(1 for r in results if r["success"]) / len(results),
                "throughput": user_count / (end_time - start_time),
            }

        for user_count in user_counts:
            metrics = await simulate_load(user_count)
            performance_metrics.append(metrics)

            # Assert scalability
            assert (
                metrics["success_rate"] > 0.95
            ), f"Success rate {metrics['success_rate']:.2f} too low at {user_count} users"

        # Analyze scalability
        throughputs = [m["throughput"] for m in performance_metrics]
        scalability_factor = (
            throughputs[-1] / throughputs[0]
        )  # Final throughput / Initial throughput

        print(f"Horizontal Scalability Results:")
        for metrics in performance_metrics:
            print(
                f"  {metrics['user_count']} users: {metrics['throughput']:.1f} req/s, {metrics['success_rate']:.2f}% success"
            )
        print(f"  Scalability factor: {scalability_factor:.2f}")

        # Assert reasonable scalability
        assert (
            scalability_factor > 0.5
        ), f"Scalability factor {scalability_factor:.2f} too low"

    @pytest.mark.asyncio
    async def test_vertical_scalability(self):
        """Test vertical scalability with increasing complexity."""
        complexity_levels = [
            {"name": "simple", "operations": 1},
            {"name": "medium", "operations": 5},
            {"name": "complex", "operations": 10},
            {"name": "very_complex", "operations": 20},
        ]

        performance_metrics = []

        async def simulate_complexity(level: Dict[str, Any]):
            """Simulate workload with specified complexity."""
            operations = level["operations"]

            start_time = time.time()

            # Simulate operations
            for i in range(operations):
                await asyncio.sleep(0.01)  # Simulate operation time

            end_time = time.time()

            return {
                "level": level["name"],
                "operations": operations,
                "duration": end_time - start_time,
                "avg_operation_time": (end_time - start_time) / operations,
            }

        for level in complexity_levels:
            metrics = await simulate_complexity(level)
            performance_metrics.append(metrics)

        # Analyze vertical scalability
        avg_times = [m["avg_operation_time"] for m in performance_metrics]

        print(f"Vertical Scalability Results:")
        for metrics in performance_metrics:
            print(
                f"  {metrics['level']}: {metrics['operations']} ops, {metrics['avg_operation_time']:.3f}s avg"
            )

        # Assert reasonable performance degradation
        assert avg_times[-1] < avg_times[0] * 3, "Performance degradation too severe"


if __name__ == "__main__":
    # Run performance tests
    pytest.main([__file__, "-v", "-s"])
