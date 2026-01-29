"""
Comprehensive AI Inference API Testing Framework
=============================================

Complete testing suite for AI inference API with unit tests, integration tests,
performance tests, and load testing.

Features:
- Unit tests for all components
- Integration tests for API endpoints
- Performance and load testing
- Cache testing
- Error handling validation
- Security testing
- Cost optimization testing
- Provider failover testing
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
import pytest_asyncio

from .api.v1.ai_inference import (
    BatchInferenceRequestModel,
    BatchInferenceResponseModel,
    InferenceRequestModel,
    InferenceResponseModel,
)
from .core.batch_processor import InferenceRequest, RequestStatus
from .core.fallback_providers import FailoverStrategy, get_fallback_manager
from .core.inference_cache import CacheEntry, CacheLevel, get_inference_cache
from .core.inference_optimizer import OptimizationStrategy, get_cost_optimizer
from .core.inference_queue import QueuePriority, get_queue_manager
from .core.streaming_inference import get_streaming_manager


class TestInferenceAPI:
    """Test class for AI Inference API."""

    @pytest_asyncio.fixture
    async def setup_components(self):
        """Setup test components."""
        # Initialize components
        cache = await get_inference_cache()
        cost_optimizer = await get_cost_optimizer()
        queue_manager = await get_queue_manager()
        streaming_manager = await get_streaming_manager()
        fallback_manager = await get_fallback_manager()

        yield {
            "cache": cache,
            "cost_optimizer": cost_optimizer,
            "queue_manager": queue_manager,
            "streaming_manager": streaming_manager,
            "fallback_manager": fallback_manager,
        }

    @pytest_asyncio.fixture
    async def client(self):
        """Create test client."""
        async with httpx.AsyncClient(base_url="http://testserver") as client:
            yield client


class TestSingleInference(TestInferenceAPI):
    """Test single inference endpoint."""

    @pytest.mark.asyncio
    async def test_single_inference_success(self, setup_components):
        """Test successful single inference."""
        components = setup_components

        # Create test request
        request = InferenceRequestModel(
            prompt="What is the capital of France?",
            model_name="gpt-3.5-turbo",
            temperature=0.7,
            user_id="test_user",
            priority=5,
        )

        # Mock LLM response
        with patch("..llm.LLMManager.process_request") as mock_llm:
            mock_response = MagicMock()
            mock_response.content = "The capital of France is Paris."
            mock_llm.return_value = mock_response

            # Import and call the function
            from api.v1.ai_inference import single_inference
            from fastapi import BackgroundTasks

            response = await single_inference(request, BackgroundTasks(), components)

            # Validate response
            assert isinstance(response, InferenceResponseModel)
            assert response.response == "The capital of France is Paris."
            assert response.model_used == "gpt-3.5-turbo"
            assert response.cache_hit == False
            assert response.input_tokens > 0
            assert response.output_tokens > 0
            assert response.processing_time > 0

    @pytest.mark.asyncio
    async def test_single_inference_cache_hit(self, setup_components):
        """Test single inference with cache hit."""
        components = setup_components
        cache = components["cache"]

        # Pre-populate cache
        cache_key = cache._generate_cache_key(
            prompt="What is the capital of France?", model_name="gpt-3.5-turbo"
        )

        await cache.set(
            cache_key=cache_key,
            value="The capital of France is Paris.",
            model_name="gpt-3.5-turbo",
            cost_estimate=0.001,
            token_count=100,
            prompt="What is the capital of France?",
        )

        # Create request
        request = InferenceRequestModel(
            prompt="What is the capital of France?",
            model_name="gpt-3.5-turbo",
            use_cache=True,
        )

        # Call function
        from api.v1.ai_inference import single_inference
        from fastapi import BackgroundTasks

        response = await single_inference(request, BackgroundTasks(), components)

        # Validate cache hit
        assert response.cache_hit == True
        assert response.response == "The capital of France is Paris."
        assert response.provider_used == "cache"

    @pytest.mark.asyncio
    async def test_single_inference_cost_optimization(self, setup_components):
        """Test single inference with cost optimization."""
        components = setup_components

        request = InferenceRequestModel(
            prompt="Generate a short story",
            model_name="gpt-4",
            cost_optimize=True,
            strategy="lowest_cost",
        )

        # Mock LLM response
        with patch("..llm.LLMManager.process_request") as mock_llm:
            mock_response = MagicMock()
            mock_response.content = "Once upon a time..."
            mock_llm.return_value = mock_response

            from api.v1.ai_inference import single_inference
            from fastapi import BackgroundTasks

            response = await single_inference(request, BackgroundTasks(), components)

            # Should potentially select a cheaper model
            assert response.response == "Once upon a time..."
            assert response.estimated_cost > 0

    @pytest.mark.asyncio
    async def test_single_inference_error_handling(self, setup_components):
        """Test single inference error handling."""
        components = setup_components

        request = InferenceRequestModel(
            prompt="Test prompt",
            model_name="gpt-3.5-turbo",
        )

        # Mock LLM error
        with patch("..llm.LLMManager.process_request") as mock_llm:
            mock_llm.side_effect = Exception("LLM error")

            from api.v1.ai_inference import single_inference
            from fastapi import BackgroundTasks

            with pytest.raises(Exception):
                await single_inference(request, BackgroundTasks(), components)


class TestBatchInference(TestInferenceAPI):
    """Test batch inference endpoint."""

    @pytest.mark.asyncio
    async def test_batch_inference_success(self, setup_components):
        """Test successful batch inference."""
        components = setup_components

        # Create batch request
        requests = [
            InferenceRequestModel(
                prompt=f"What is {i} + {i}?",
                model_name="gpt-3.5-turbo",
                priority=5,
            )
            for i in range(3)
        ]

        batch_request = BatchInferenceRequestModel(
            requests=requests,
            parallel_processing=True,
        )

        # Mock LLM responses
        with patch("..llm.LLMManager.process_request") as mock_llm:
            mock_response = MagicMock()
            mock_response.content = "Result"
            mock_llm.return_value = mock_response

            from api.v1.ai_inference import batch_inference
            from fastapi import BackgroundTasks

            response = await batch_inference(
                batch_request, BackgroundTasks(), components
            )

            # Validate batch response
            assert isinstance(response, BatchInferenceResponseModel)
            assert len(response.responses) == 3
            assert response.total_requests == 3
            assert response.successful_requests == 3
            assert response.failed_requests == 0
            assert response.total_processing_time > 0

    @pytest.mark.asyncio
    async def test_batch_inference_deduplication(self, setup_components):
        """Test batch inference with deduplication."""
        components = setup_components

        # Create batch with duplicate requests
        requests = [
            InferenceRequestModel(
                prompt="What is 2 + 2?",
                model_name="gpt-3.5-turbo",
                priority=5,
            ),
            InferenceRequestModel(
                prompt="What is 2 + 2?",  # Duplicate
                model_name="gpt-3.5-turbo",
                priority=5,
            ),
        ]

        batch_request = BatchInferenceRequestModel(
            requests=requests,
            deduplicate=True,
        )

        # Mock LLM response
        with patch("..llm.LLMManager.process_request") as mock_llm:
            mock_response = MagicMock()
            mock_response.content = "4"
            mock_llm.return_value = mock_response

            from api.v1.ai_inference import batch_inference
            from fastapi import BackgroundTasks

            response = await batch_inference(
                batch_request, BackgroundTasks(), components
            )

            # Should have one duplicate
            assert response.duplicate_requests >= 1

    @pytest.mark.asyncio
    async def test_batch_inference_fail_fast(self, setup_components):
        """Test batch inference with fail_fast enabled."""
        components = setup_components

        requests = [
            InferenceRequestModel(
                prompt=f"Request {i}",
                model_name="gpt-3.5-turbo",
                priority=5,
            )
            for i in range(3)
        ]

        batch_request = BatchInferenceRequestModel(
            requests=requests,
            fail_fast=True,
        )

        # Mock LLM error for first request
        with patch("..llm.LLMManager.process_request") as mock_llm:
            mock_llm.side_effect = [
                Exception("Error"),
                MagicMock(content="Success"),
                MagicMock(content="Success"),
            ]

            from api.v1.ai_inference import batch_inference
            from fastapi import BackgroundTasks

            with pytest.raises(Exception):
                await batch_inference(batch_request, BackgroundTasks(), components)


class TestCacheSystem(TestInferenceAPI):
    """Test cache system functionality."""

    @pytest.mark.asyncio
    async def test_cache_l1_operations(self, setup_components):
        """Test L1 cache operations."""
        cache = setup_components["cache"]

        # Test cache set and get
        cache_key = "test_key"
        value = "test_value"

        await cache.l1_cache.set(
            CacheEntry(
                key=cache_key,
                value=value,
                level=CacheLevel.L1_MEMORY,
                created_at=datetime.utcnow(),
                last_accessed=datetime.utcnow(),
            )
        )

        retrieved_entry = await cache.l1_cache.get(cache_key)
        assert retrieved_entry is not None
        assert retrieved_entry.value == value

    @pytest.mark.asyncio
    async def test_cache_l2_operations(self, setup_components):
        """Test L2 cache operations."""
        cache = setup_components["cache"]

        # Test cache set and get
        cache_key = "test_key"
        value = "test_value"

        await cache.l2_cache.set(
            CacheEntry(
                key=cache_key,
                value=value,
                level=CacheLevel.L2_REDIS,
                created_at=datetime.utcnow(),
                last_accessed=datetime.utcnow(),
            )
        )

        retrieved_entry = await cache.l2_cache.get(cache_key)
        assert retrieved_entry is not None
        assert retrieved_entry.value == value

    @pytest.mark.asyncio
    async def test_cache_multi_level(self, setup_components):
        """Test multi-level cache hierarchy."""
        cache = setup_components["cache"]

        cache_key = "test_key"
        value = "test_value"

        # Set in L1
        await cache.set(
            cache_key=cache_key,
            value=value,
            model_name="gpt-3.5-turbo",
            cost_estimate=0.001,
            token_count=100,
            prompt="test prompt",
        )

        # Should get from L1
        entry = await cache.get(cache_key)
        assert entry is not None
        assert entry.value == value

        # Clear L1 and test L2
        await cache.l1_cache.clear()
        entry = await cache.get(cache_key)
        assert entry is not None  # Should get from L2

    @pytest.mark.asyncio
    async def test_cache_expiration(self, setup_components):
        """Test cache entry expiration."""
        cache = setup_components["cache"]

        cache_key = "test_key"
        value = "test_value"

        # Set with short TTL
        await cache.set(
            cache_key=cache_key,
            value=value,
            model_name="gpt-3.5-turbo",
            ttl_seconds=1,  # 1 second
            cost_estimate=0.001,
            token_count=100,
        )

        # Should be available immediately
        entry = await cache.get(cache_key)
        assert entry is not None

        # Wait for expiration
        await asyncio.sleep(2)

        # Should be expired
        entry = await cache.get(cache_key)
        assert entry is None


class TestCostOptimization(TestInferenceAPI):
    """Test cost optimization functionality."""

    @pytest.mark.asyncio
    async def test_token_counting(self, setup_components):
        """Test token counting accuracy."""
        cost_optimizer = setup_components["cost_optimizer"]

        # Test token counting
        prompt = "What is the meaning of life?"
        tokens = await cost_optimizer.token_counter.count_tokens(
            prompt, "gpt-3.5-turbo"
        )
        assert tokens > 0
        assert isinstance(tokens, int)

    @pytest.mark.asyncio
    async def test_cost_estimation(self, setup_components):
        """Test cost estimation."""
        cost_optimizer = setup_components["cost_optimizer"]

        input_tokens = 100
        output_tokens = 200
        model_name = "gpt-3.5-turbo"

        cost = await cost_optimizer.estimate_cost(
            input_tokens, output_tokens, model_name
        )
        assert cost > 0
        assert isinstance(cost, float)

    @pytest.mark.asyncio
    async def test_provider_selection(self, setup_components):
        """Test optimal provider selection."""
        cost_optimizer = setup_components["cost_optimizer"]

        input_tokens = 100
        output_tokens = 200

        provider, model, cost = await cost_optimizer.select_optimal_provider(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

        assert provider is not None
        assert model is not None
        assert cost >= 0

    @pytest.mark.asyncio
    async def test_usage_tracking(self, setup_components):
        """Test usage tracking."""
        cost_optimizer = setup_components["cost_optimizer"]

        await cost_optimizer.track_usage(
            input_tokens=100,
            output_tokens=200,
            actual_cost=0.01,
            response_time=1.5,
            model_used="gpt-3.5-turbo",
            provider_used="openai",
            request_id="test_request",
        )

        # Check if usage was tracked
        assert len(cost_optimizer.usage_history) > 0


class TestQueueManagement(TestInferenceAPI):
    """Test queue management functionality."""

    @pytest.mark.asyncio
    async def test_queue_operations(self, setup_components):
        """Test basic queue operations."""
        queue_manager = setup_components["queue_manager"]

        # Create test request
        request = InferenceRequest(
            id="test_request",
            prompt="Test prompt",
            model_name="gpt-3.5-turbo",
            priority=5,
        )

        # Test enqueue
        success = await queue_manager.enqueue_request(request)
        assert success == True

        # Test dequeue
        dequeued_request = await queue_manager.get_next_request("test_worker")
        assert dequeued_request is not None
        assert dequeued_request.id == "test_request"

    @pytest.mark.asyncio
    async def test_priority_handling(self, setup_components):
        """Test priority-based request handling."""
        queue_manager = setup_components["queue_manager"]

        # Create requests with different priorities
        low_priority = InferenceRequest(
            id="low_priority",
            prompt="Low priority",
            model_name="gpt-3.5-turbo",
            priority=2,
        )

        high_priority = InferenceRequest(
            id="high_priority",
            prompt="High priority",
            model_name="gpt-3.5-turbo",
            priority=8,
        )

        # Enqueue in order
        await queue_manager.enqueue_request(low_priority)
        await queue_manager.enqueue_request(high_priority)

        # Should get high priority first
        first_request = await queue_manager.get_next_request("test_worker")
        assert first_request.id == "high_priority"

        second_request = await queue_manager.get_next_request("test_worker")
        assert second_request.id == "low_priority"

    @pytest.mark.asyncio
    async def test_worker_management(self, setup_components):
        """Test worker management."""
        queue_manager = setup_components["queue_manager"]

        # Add worker
        success = await queue_manager.add_worker(
            worker_id="test_worker",
            provider="openai",
            model="gpt-3.5-turbo",
            max_concurrent=2,
        )
        assert success == True

        # Get available workers
        available_workers = await queue_manager.get_available_workers()
        assert len(available_workers) > 0
        assert any(w.id == "test_worker" for w in available_workers)


class TestFallbackProviders(TestInferenceAPI):
    """Test fallback provider functionality."""

    @pytest.mark.asyncio
    async def test_provider_registration(self, setup_components):
        """Test provider registration."""
        fallback_manager = setup_components["fallback_manager"]

        # Register new provider
        fallback_manager.register_provider(
            provider_id="test_provider",
            provider="test",
            model="test-model",
            priority=8,
        )

        assert "test_provider" in fallback_manager.providers

    @pytest.mark.asyncio
    async def test_failover_execution(self, setup_components):
        """Test failover execution."""
        fallback_manager = setup_components["fallback_manager"]

        # Mock provider execution
        with patch.object(fallback_manager, "_execute_provider") as mock_execute:
            # First provider fails, second succeeds
            mock_execute.side_effect = [
                Exception("Provider failed"),
                ("Success response", 1.0),
            ]

            response, provider_id, response_time = (
                await fallback_manager.execute_with_fallback(
                    model="gpt-3.5-turbo",
                    prompt="Test prompt",
                )
            )

            assert response == "Success response"
            assert response_time > 0

    @pytest.mark.asyncio
    async def test_circuit_breaker(self, setup_components):
        """Test circuit breaker functionality."""
        fallback_manager = setup_components["fallback_manager"]

        provider = fallback_manager.providers["openai-gpt-3.5-turbo"]

        # Simulate consecutive failures
        for _ in range(5):
            provider.update_health(False, 0.0)

        # Circuit breaker should be open
        assert provider.circuit_breaker_open == True
        assert provider.is_available() == False


class TestStreamingInference(TestInferenceAPI):
    """Test streaming inference functionality."""

    @pytest.mark.asyncio
    async def test_session_creation(self, setup_components):
        """Test streaming session creation."""
        streaming_manager = setup_components["streaming_manager"]

        # Mock WebSocket
        mock_websocket = MagicMock()

        session = await streaming_manager.create_session(
            request_id="test_request",
            websocket=mock_websocket,
        )

        assert session is not None
        assert session.request_id == "test_request"
        assert session.status == "connecting"

    @pytest.mark.asyncio
    async def test_chunk_sending(self, setup_components):
        """Test chunk sending to session."""
        streaming_manager = setup_components["streaming_manager"]

        # Mock WebSocket
        mock_websocket = MagicMock()
        mock_websocket.send_text = AsyncMock()

        session = await streaming_manager.create_session(
            request_id="test_request",
            websocket=mock_websocket,
        )

        # Send data chunk
        success = await streaming_manager.send_data(
            session_id=session.id,
            data="Test data",
        )

        assert success == True
        mock_websocket.send_text.assert_called()

    @pytest.mark.asyncio
    async def test_progress_tracking(self, setup_components):
        """Test progress tracking."""
        streaming_manager = setup_components["streaming_manager"]

        # Mock WebSocket
        mock_websocket = MagicMock()
        mock_websocket.send_text = AsyncMock()

        session = await streaming_manager.create_session(
            request_id="test_request",
            websocket=mock_websocket,
        )

        # Send progress update
        success = await streaming_manager.send_progress(
            session_id=session.id,
            current=50,
            total=100,
            message="Halfway there",
        )

        assert success == True
        assert session.progress_current == 50
        assert session.progress_total == 100
        assert session.get_progress_percentage() == 50.0


class TestPerformanceAndLoad:
    """Performance and load testing."""

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, setup_components):
        """Test handling concurrent requests."""
        components = setup_components

        # Create multiple concurrent requests
        async def make_request(i):
            request = InferenceRequestModel(
                prompt=f"Test request {i}",
                model_name="gpt-3.5-turbo",
                priority=5,
            )

            with patch("..llm.LLMManager.process_request") as mock_llm:
                mock_response = MagicMock()
                mock_response.content = f"Response {i}"
                mock_llm.return_value = mock_response

                from api.v1.ai_inference import single_inference
                from fastapi import BackgroundTasks

                return await single_inference(request, BackgroundTasks(), components)

        # Run 10 concurrent requests
        tasks = [make_request(i) for i in range(10)]
        responses = await asyncio.gather(*tasks)

        # Validate all responses
        assert len(responses) == 10
        for i, response in enumerate(responses):
            assert response.response == f"Response {i}"

    @pytest.mark.asyncio
    async def test_cache_performance(self, setup_components):
        """Test cache performance under load."""
        cache = setup_components["cache"]

        # Measure cache set performance
        start_time = time.time()

        tasks = []
        for i in range(100):
            task = cache.set(
                cache_key=f"test_key_{i}",
                value=f"test_value_{i}",
                model_name="gpt-3.5-turbo",
                cost_estimate=0.001,
                token_count=100,
                prompt=f"test prompt {i}",
            )
            tasks.append(task)

        await asyncio.gather(*tasks)
        set_time = time.time() - start_time

        # Measure cache get performance
        start_time = time.time()

        tasks = []
        for i in range(100):
            task = cache.get(f"test_key_{i}")
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        get_time = time.time() - start_time

        # Validate performance
        assert set_time < 5.0  # Should complete in under 5 seconds
        assert get_time < 2.0  # Should complete in under 2 seconds
        assert all(result is not None for result in results)

    @pytest.mark.asyncio
    async def test_memory_usage(self, setup_components):
        """Test memory usage under load."""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Create and process many requests
        components = setup_components

        for i in range(1000):
            request = InferenceRequestModel(
                prompt=f"Test request {i}",
                model_name="gpt-3.5-turbo",
                priority=5,
            )

            with patch("..llm.LLMManager.process_request") as mock_llm:
                mock_response = MagicMock()
                mock_response.content = f"Response {i}"
                mock_llm.return_value = mock_response

                from api.v1.ai_inference import single_inference
                from fastapi import BackgroundTasks

                await single_inference(request, BackgroundTasks(), components)

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024


class TestErrorHandling:
    """Test error handling and edge cases."""

    @pytest.mark.asyncio
    async def test_invalid_request_format(self, setup_components):
        """Test handling of invalid request formats."""
        components = setup_components

        # Test with invalid prompt
        with pytest.raises(Exception):
            request = InferenceRequestModel(
                prompt="",  # Empty prompt
                model_name="gpt-3.5-turbo",
            )

            from api.v1.ai_inference import single_inference
            from fastapi import BackgroundTasks

            await single_inference(request, BackgroundTasks(), components)

    @pytest.mark.asyncio
    async def test_timeout_handling(self, setup_components):
        """Test request timeout handling."""
        components = setup_components

        request = InferenceRequestModel(
            prompt="Test prompt",
            model_name="gpt-3.5-turbo",
            timeout_seconds=1,  # Very short timeout
        )

        # Mock slow LLM response
        with patch("..llm.LLMManager.process_request") as mock_llm:

            async def slow_response(*args, **kwargs):
                await asyncio.sleep(2)  # Longer than timeout
                return MagicMock(content="Response")

            mock_llm.side_effect = slow_response

            from api.v1.ai_inference import single_inference
            from fastapi import BackgroundTasks

            # Should handle timeout gracefully
            with pytest.raises(Exception):
                await single_inference(request, BackgroundTasks(), components)

    @pytest.mark.asyncio
    async def test_resource_exhaustion(self, setup_components):
        """Test handling of resource exhaustion."""
        queue_manager = setup_components["queue_manager"]

        # Fill queue to capacity
        requests = []
        for i in range(15000):  # Exceed default queue size
            request = InferenceRequest(
                id=f"request_{i}",
                prompt=f"Test prompt {i}",
                model_name="gpt-3.5-turbo",
                priority=5,
            )
            requests.append(request)

        # Should handle gracefully without crashing
        success_count = 0
        for request in requests:
            success = await queue_manager.enqueue_request(request)
            if success:
                success_count += 1
            else:
                break  # Stop when queue is full

        # Should have accepted some requests but not all
        assert success_count > 0
        assert success_count < len(requests)


# Integration Tests
class TestAPIIntegration:
    """Full API integration tests."""

    @pytest.mark.asyncio
    async def test_full_inference_flow(self, setup_components):
        """Test complete inference flow with all components."""
        components = setup_components

        # Create request
        request = InferenceRequestModel(
            prompt="Explain quantum computing in simple terms",
            model_name="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=500,
            user_id="test_user",
            priority=5,
            use_cache=True,
            cost_optimize=True,
        )

        # Mock LLM response
        with patch("..llm.LLMManager.process_request") as mock_llm:
            mock_response = MagicMock()
            mock_response.content = "Quantum computing is a revolutionary approach..."
            mock_llm.return_value = mock_response

            from api.v1.ai_inference import single_inference
            from fastapi import BackgroundTasks

            # Execute inference
            response = await single_inference(request, BackgroundTasks(), components)

            # Validate complete flow
            assert (
                response.response == "Quantum computing is a revolutionary approach..."
            )
            assert response.processing_time > 0
            assert response.input_tokens > 0
            assert response.output_tokens > 0
            assert response.estimated_cost > 0
            assert response.actual_cost > 0

            # Verify cache was populated
            cache_key = components["cache"]._generate_cache_key(
                prompt=request.prompt,
                model_name=request.model_name,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
            cache_entry = await components["cache"].get(cache_key)
            assert cache_entry is not None
            assert cache_entry.value == response.response

            # Verify usage was tracked
            assert len(components["cost_optimizer"].usage_history) > 0

    @pytest.mark.asyncio
    async def test_system_status_endpoint(self, setup_components):
        """Test system status endpoint."""
        from api.v1.ai_inference import get_status

        response = await get_status(setup_components)

        assert response.status == "healthy"
        assert response.pending_requests >= 0
        assert response.processing_requests >= 0
        assert "cache_stats" in response.__dict__
        assert "cost_stats" in response.__dict__
        assert "worker_stats" in response.__dict__


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
