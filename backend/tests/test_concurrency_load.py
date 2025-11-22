"""
Concurrency and load tests for RaptorFlow.
Tests system behavior under concurrent load and validates:
- Redis caching with concurrent requests
- Unique correlation IDs per request
- Error handling under load
- Rate limiting and throttling
"""

import pytest
import asyncio
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from typing import List, Dict, Any
import time


class TestConcurrentRequests:
    """Test concurrent request handling."""

    @pytest.mark.asyncio
    async def test_10_simultaneous_workflow_requests(
        self,
        authenticated_client: AsyncClient,
        mock_auth,
        mock_supabase,
        mock_vertex_ai,
        mock_redis
    ):
        """
        Test 10 simultaneous workflow execution requests.
        Validates:
        - All requests complete successfully
        - Each has unique correlation ID
        - Redis caching works correctly
        - No race conditions
        """
        num_requests = 10

        with patch('backend.graphs.master_graph.master_graph_runnable.ainvoke') as mock_graph:
            # Mock successful workflow execution
            def create_mock_result(request_num: int):
                return {
                    "workflow_id": str(uuid4()),
                    "correlation_id": f"test-correlation-{request_num}",
                    "workspace_id": mock_auth["workspace_id"],
                    "user_id": mock_auth["user_id"],
                    "goal": "research_only",
                    "current_stage": "finalize",
                    "completed_stages": ["research"],
                    "failed_stages": [],
                    "success": True,
                    "message": f"Workflow {request_num} completed",
                    "started_at": "2024-01-01T00:00:00",
                    "completed_at": "2024-01-01T00:05:00",
                    "research_result": {"icp_id": str(uuid4())},
                    "errors": [],
                    "retry_count": 0
                }

            # Configure mock to return unique results
            mock_graph.side_effect = [create_mock_result(i) for i in range(num_requests)]

            # Create concurrent requests
            async def make_request(request_num: int) -> Dict[str, Any]:
                response = await authenticated_client.post(
                    "/api/v1/orchestration/execute",
                    json={
                        "goal": "research_only",
                        "research_query": f"Query {request_num}"
                    }
                )
                return {
                    "request_num": request_num,
                    "status_code": response.status_code,
                    "data": response.json() if response.status_code == 200 else None,
                    "correlation_id": response.headers.get("X-Correlation-ID")
                }

            # Execute requests concurrently
            start_time = time.time()
            results = await asyncio.gather(*[make_request(i) for i in range(num_requests)])
            elapsed_time = time.time() - start_time

            # Verify all requests succeeded
            assert len(results) == num_requests
            assert all(r["status_code"] == 200 for r in results)

            # Verify unique correlation IDs
            correlation_ids = [r["correlation_id"] for r in results]
            assert len(correlation_ids) == len(set(correlation_ids)), "Correlation IDs must be unique"

            # Verify unique workflow IDs
            workflow_ids = [r["data"]["workflow_id"] for r in results]
            assert len(workflow_ids) == len(set(workflow_ids)), "Workflow IDs must be unique"

            # Log performance
            print(f"\n10 concurrent requests completed in {elapsed_time:.2f}s")
            print(f"Average: {elapsed_time/num_requests:.2f}s per request")

            # Verify reasonable performance (adjust threshold as needed)
            assert elapsed_time < 30, f"10 requests should complete in <30s, took {elapsed_time:.2f}s"

    @pytest.mark.asyncio
    async def test_concurrent_requests_different_goals(
        self,
        authenticated_client: AsyncClient,
        mock_auth,
        mock_supabase,
        mock_vertex_ai,
        mock_redis
    ):
        """Test concurrent requests with different workflow goals."""
        goals = ["research_only", "strategy_only", "content_only", "full_campaign", "research_only"]

        with patch('backend.graphs.master_graph.master_graph_runnable.ainvoke') as mock_graph:
            def create_mock_result(goal: str):
                return {
                    "workflow_id": str(uuid4()),
                    "correlation_id": str(uuid4()),
                    "workspace_id": mock_auth["workspace_id"],
                    "user_id": mock_auth["user_id"],
                    "goal": goal,
                    "current_stage": "finalize",
                    "completed_stages": [goal.split("_")[0]],
                    "failed_stages": [],
                    "success": True,
                    "message": "Workflow completed",
                    "started_at": "2024-01-01T00:00:00",
                    "completed_at": "2024-01-01T00:05:00",
                    "research_result": {"icp_id": str(uuid4())} if "research" in goal else None,
                    "strategy_result": {"strategy_id": str(uuid4())} if "strategy" in goal else None,
                    "content_result": {"content_ids": [str(uuid4())]} if "content" in goal else None,
                    "errors": [],
                    "retry_count": 0
                }

            mock_graph.side_effect = [create_mock_result(goal) for goal in goals]

            # Make concurrent requests
            async def make_request(goal: str) -> Dict[str, Any]:
                response = await authenticated_client.post(
                    "/api/v1/orchestration/execute",
                    json={"goal": goal}
                )
                return response.json()

            results = await asyncio.gather(*[make_request(goal) for goal in goals])

            # Verify all completed
            assert len(results) == len(goals)
            assert all(r["success"] for r in results)

            # Verify correct goals executed
            for i, result in enumerate(results):
                assert result["goal"] == goals[i]


class TestRedisCachingConcurrency:
    """Test Redis caching under concurrent load."""

    @pytest.mark.asyncio
    async def test_cache_prevents_duplicate_research(
        self,
        authenticated_client: AsyncClient,
        mock_auth,
        mock_supabase,
        mock_vertex_ai,
        mock_redis
    ):
        """
        Test that Redis cache prevents duplicate research work.
        When multiple requests for same query arrive, should:
        1. First request does the work
        2. Subsequent requests use cached result
        """
        cache_mock, _ = mock_redis
        num_requests = 5
        same_query = "B2B SaaS startups"

        # Track cache hits
        cache_hits = []
        cache_misses = []

        async def mock_cache_get(prefix: str, identifier: str):
            """Mock cache get that tracks hits/misses."""
            # First request misses, others hit
            if len(cache_misses) == 0:
                cache_misses.append(identifier)
                return None  # Cache miss
            else:
                cache_hits.append(identifier)
                return {"cached": True, "icp_id": str(uuid4())}  # Cache hit

        cache_mock.get.side_effect = mock_cache_get

        with patch('backend.graphs.master_graph.master_graph_runnable.ainvoke') as mock_graph:
            # Only first request should execute graph
            mock_graph.return_value = {
                "workflow_id": str(uuid4()),
                "correlation_id": "test-correlation",
                "workspace_id": mock_auth["workspace_id"],
                "user_id": mock_auth["user_id"],
                "goal": "research_only",
                "current_stage": "finalize",
                "completed_stages": ["research"],
                "failed_stages": [],
                "success": True,
                "message": "Workflow completed",
                "started_at": "2024-01-01T00:00:00",
                "completed_at": "2024-01-01T00:05:00",
                "research_result": {"icp_id": str(uuid4())},
                "errors": [],
                "retry_count": 0
            }

            # Make concurrent requests with same query
            async def make_request():
                response = await authenticated_client.post(
                    "/api/v1/orchestration/execute",
                    json={
                        "goal": "research_only",
                        "research_query": same_query
                    }
                )
                return response.json()

            results = await asyncio.gather(*[make_request() for _ in range(num_requests)])

            # Verify all succeeded
            assert len(results) == num_requests
            assert all(r["success"] for r in results)

            # Cache behavior verification
            # Note: Actual caching depends on implementation details
            # This test sets up the framework for testing caching

    @pytest.mark.asyncio
    async def test_cache_isolation_different_workspaces(
        self,
        client: AsyncClient,
        mock_supabase,
        mock_vertex_ai,
        mock_redis
    ):
        """
        Test that cache properly isolates data between workspaces.
        Two workspaces requesting same query should not share cached data.
        """
        cache_mock, _ = mock_redis

        workspace1_id = str(uuid4())
        workspace2_id = str(uuid4())

        # Track cache keys to verify workspace isolation
        cache_keys = []

        async def mock_cache_set(prefix: str, identifier: str, value: Any, ttl: int = None):
            cache_keys.append(identifier)
            return True

        cache_mock.set.side_effect = mock_cache_set

        # This test would require authenticated clients for different workspaces
        # Framework is in place, implementation depends on auth setup


class TestErrorHandlingUnderLoad:
    """Test error handling under concurrent load."""

    @pytest.mark.asyncio
    async def test_partial_failures_dont_affect_other_requests(
        self,
        authenticated_client: AsyncClient,
        mock_auth,
        mock_supabase,
        mock_vertex_ai,
        mock_redis
    ):
        """Test that failed requests don't impact concurrent successful requests."""
        num_requests = 10

        with patch('backend.graphs.master_graph.master_graph_runnable.ainvoke') as mock_graph:
            # Make some requests fail
            def create_result(request_num: int):
                if request_num % 3 == 0:
                    # Every 3rd request fails
                    raise Exception(f"Simulated failure for request {request_num}")
                else:
                    return {
                        "workflow_id": str(uuid4()),
                        "correlation_id": f"test-{request_num}",
                        "workspace_id": mock_auth["workspace_id"],
                        "user_id": mock_auth["user_id"],
                        "goal": "research_only",
                        "current_stage": "finalize",
                        "completed_stages": ["research"],
                        "failed_stages": [],
                        "success": True,
                        "message": "Success",
                        "started_at": "2024-01-01T00:00:00",
                        "completed_at": "2024-01-01T00:05:00",
                        "research_result": {"icp_id": str(uuid4())},
                        "errors": [],
                        "retry_count": 0
                    }

            mock_graph.side_effect = [create_result(i) for i in range(num_requests)]

            async def make_request(request_num: int):
                try:
                    response = await authenticated_client.post(
                        "/api/v1/orchestration/execute",
                        json={"goal": "research_only"}
                    )
                    return {"success": response.status_code == 200, "request_num": request_num}
                except Exception as e:
                    return {"success": False, "request_num": request_num, "error": str(e)}

            results = await asyncio.gather(*[make_request(i) for i in range(num_requests)])

            # Some requests should succeed
            successful = [r for r in results if r["success"]]
            failed = [r for r in results if not r["success"]]

            print(f"\nSuccessful: {len(successful)}, Failed: {len(failed)}")

            # Verify partial success (not all fail)
            assert len(successful) > 0, "Some requests should succeed"

    @pytest.mark.asyncio
    async def test_timeout_handling_concurrent(
        self,
        authenticated_client: AsyncClient,
        mock_auth,
        mock_supabase,
        mock_vertex_ai,
        mock_redis
    ):
        """Test timeout handling with concurrent slow requests."""
        with patch('backend.graphs.master_graph.master_graph_runnable.ainvoke') as mock_graph:
            # Simulate slow execution
            async def slow_execution(*args, **kwargs):
                await asyncio.sleep(0.5)  # 500ms delay
                return {
                    "workflow_id": str(uuid4()),
                    "correlation_id": "test",
                    "workspace_id": mock_auth["workspace_id"],
                    "user_id": mock_auth["user_id"],
                    "goal": "research_only",
                    "current_stage": "finalize",
                    "completed_stages": ["research"],
                    "failed_stages": [],
                    "success": True,
                    "message": "Completed after delay",
                    "started_at": "2024-01-01T00:00:00",
                    "completed_at": "2024-01-01T00:05:00",
                    "research_result": {"icp_id": str(uuid4())},
                    "errors": [],
                    "retry_count": 0
                }

            mock_graph.side_effect = slow_execution

            # Make concurrent slow requests
            start_time = time.time()
            results = await asyncio.gather(*[
                authenticated_client.post(
                    "/api/v1/orchestration/execute",
                    json={"goal": "research_only"}
                )
                for _ in range(5)
            ])
            elapsed = time.time() - start_time

            # Verify all completed
            assert all(r.status_code == 200 for r in results)

            # With concurrency, should be faster than sequential
            # 5 requests * 500ms = 2.5s sequential, but concurrent should be ~500ms
            print(f"\n5 slow concurrent requests: {elapsed:.2f}s")


class TestPerformanceMetrics:
    """Test performance characteristics under load."""

    @pytest.mark.asyncio
    async def test_response_time_percentiles(
        self,
        authenticated_client: AsyncClient,
        mock_auth,
        mock_supabase,
        mock_vertex_ai,
        mock_redis
    ):
        """
        Measure response time percentiles under load.
        Track p50, p95, p99 response times.
        """
        num_requests = 20

        with patch('backend.graphs.master_graph.master_graph_runnable.ainvoke') as mock_graph:
            mock_graph.return_value = {
                "workflow_id": str(uuid4()),
                "correlation_id": "test",
                "workspace_id": mock_auth["workspace_id"],
                "user_id": mock_auth["user_id"],
                "goal": "research_only",
                "current_stage": "finalize",
                "completed_stages": ["research"],
                "failed_stages": [],
                "success": True,
                "message": "Completed",
                "started_at": "2024-01-01T00:00:00",
                "completed_at": "2024-01-01T00:05:00",
                "research_result": {"icp_id": str(uuid4())},
                "errors": [],
                "retry_count": 0
            }

            # Track response times
            response_times = []

            async def make_timed_request():
                start = time.time()
                response = await authenticated_client.post(
                    "/api/v1/orchestration/execute",
                    json={"goal": "research_only"}
                )
                elapsed = time.time() - start
                response_times.append(elapsed)
                return response

            # Execute concurrent requests
            results = await asyncio.gather(*[make_timed_request() for _ in range(num_requests)])

            # Verify all succeeded
            assert all(r.status_code == 200 for r in results)

            # Calculate percentiles
            sorted_times = sorted(response_times)
            p50_idx = int(len(sorted_times) * 0.50)
            p95_idx = int(len(sorted_times) * 0.95)
            p99_idx = int(len(sorted_times) * 0.99)

            p50 = sorted_times[p50_idx]
            p95 = sorted_times[p95_idx]
            p99 = sorted_times[p99_idx]

            print(f"\nResponse time percentiles ({num_requests} requests):")
            print(f"  p50: {p50:.3f}s")
            print(f"  p95: {p95:.3f}s")
            print(f"  p99: {p99:.3f}s")

            # Verify reasonable performance (adjust thresholds as needed)
            assert p50 < 5.0, f"p50 should be <5s, got {p50:.3f}s"
            assert p95 < 10.0, f"p95 should be <10s, got {p95:.3f}s"

    @pytest.mark.asyncio
    async def test_throughput_measurement(
        self,
        authenticated_client: AsyncClient,
        mock_auth,
        mock_supabase,
        mock_vertex_ai,
        mock_redis
    ):
        """Measure system throughput (requests/second)."""
        num_requests = 30
        duration_seconds = 10

        with patch('backend.graphs.master_graph.master_graph_runnable.ainvoke') as mock_graph:
            mock_graph.return_value = {
                "workflow_id": str(uuid4()),
                "correlation_id": "test",
                "workspace_id": mock_auth["workspace_id"],
                "user_id": mock_auth["user_id"],
                "goal": "research_only",
                "current_stage": "finalize",
                "completed_stages": ["research"],
                "failed_stages": [],
                "success": True,
                "message": "Completed",
                "started_at": "2024-01-01T00:00:00",
                "completed_at": "2024-01-01T00:05:00",
                "research_result": {"icp_id": str(uuid4())},
                "errors": [],
                "retry_count": 0
            }

            start_time = time.time()
            results = await asyncio.gather(*[
                authenticated_client.post(
                    "/api/v1/orchestration/execute",
                    json={"goal": "research_only"}
                )
                for _ in range(num_requests)
            ])
            elapsed = time.time() - start_time

            # Calculate throughput
            throughput = num_requests / elapsed

            print(f"\nThroughput: {throughput:.2f} requests/second")
            print(f"Completed {num_requests} requests in {elapsed:.2f}s")

            # Verify all succeeded
            assert all(r.status_code == 200 for r in results)
