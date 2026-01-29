"""
AI Inference API Endpoint
=========================

Comprehensive AI inference API with batch processing, intelligent caching,
cost optimization, and streaming capabilities.

Features:
- Single and batch inference requests
- Intelligent request deduplication
- Multi-level caching (L1/L2/L3)
- Cost optimization and provider selection
- Real-time streaming for long tasks
- Priority queue management
- Performance monitoring and analytics
- Automatic fallback and error handling
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import structlog
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ..core.batch_processor import (
    InferenceRequest,
    RequestStatus,
    get_batch_processor,
    get_request_deduplicator,
)
from ..core.inference_cache import get_inference_cache
from ..core.inference_optimizer import OptimizationStrategy, get_cost_optimizer
from ..core.inference_queue import QueuePriority, get_queue_manager
from ..core.streaming_inference import StreamingInferenceService, get_streaming_manager
from ..llm import LLMManager, LLMRequest, LLMResponse

logger = structlog.get_logger(__name__)

# Create router
router = APIRouter(prefix="/ai-inference", tags=["AI Inference"])


# Request/Response Models
class InferenceRequestModel(BaseModel):
    """Single inference request model."""

    prompt: str = Field(..., description="The prompt to process")
    model_name: str = Field(default="gpt-3.5-turbo", description="Model to use")
    temperature: float = Field(
        default=0.7, ge=0.0, le=2.0, description="Temperature for sampling"
    )
    max_tokens: Optional[int] = Field(
        default=None, ge=1, description="Maximum tokens to generate"
    )
    user_id: Optional[str] = Field(default=None, description="User ID for tracking")
    workspace_id: Optional[str] = Field(
        default=None, description="Workspace ID for tracking"
    )
    priority: int = Field(default=5, ge=1, le=10, description="Request priority (1-10)")
    stream: bool = Field(default=False, description="Enable streaming response")
    timeout_seconds: int = Field(
        default=300, ge=1, description="Request timeout in seconds"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    # Optimization options
    use_cache: bool = Field(default=True, description="Use cached responses")
    cost_optimize: bool = Field(default=True, description="Enable cost optimization")
    strategy: str = Field(default="balanced", description="Optimization strategy")
    budget_limit: Optional[float] = Field(
        default=None, description="Maximum cost limit"
    )


class BatchInferenceRequestModel(BaseModel):
    """Batch inference request model."""

    requests: List[InferenceRequestModel] = Field(
        ..., description="List of inference requests"
    )
    batch_id: Optional[str] = Field(default=None, description="Custom batch ID")
    max_batch_size: int = Field(
        default=10, ge=1, le=50, description="Maximum batch size"
    )
    timeout_seconds: int = Field(
        default=600, ge=1, description="Batch timeout in seconds"
    )

    # Batch processing options
    deduplicate: bool = Field(default=True, description="Deduplicate similar requests")
    parallel_processing: bool = Field(
        default=True, description="Process requests in parallel"
    )
    fail_fast: bool = Field(default=False, description="Stop on first error")


class InferenceResponseModel(BaseModel):
    """Inference response model."""

    request_id: str = Field(..., description="Unique request identifier")
    response: str = Field(..., description="Generated response")
    model_used: str = Field(..., description="Model that was used")
    provider_used: str = Field(..., description="Provider that was used")

    # Performance metrics
    processing_time: float = Field(..., description="Processing time in seconds")
    cache_hit: bool = Field(..., description="Whether response was from cache")

    # Cost information
    input_tokens: int = Field(..., description="Number of input tokens")
    output_tokens: int = Field(..., description="Number of output tokens")
    estimated_cost: float = Field(..., description="Estimated cost in USD")
    actual_cost: float = Field(..., description="Actual cost in USD")

    # Metadata
    timestamp: datetime = Field(..., description="Response timestamp")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class BatchInferenceResponseModel(BaseModel):
    """Batch inference response model."""

    batch_id: str = Field(..., description="Batch identifier")
    responses: List[InferenceResponseModel] = Field(
        ..., description="List of responses"
    )

    # Batch metrics
    total_requests: int = Field(..., description="Total requests in batch")
    successful_requests: int = Field(..., description="Successful requests")
    failed_requests: int = Field(..., description="Failed requests")
    duplicate_requests: int = Field(..., description="Duplicate requests removed")

    # Performance metrics
    total_processing_time: float = Field(..., description="Total processing time")
    avg_processing_time: float = Field(
        ..., description="Average processing time per request"
    )

    # Cost information
    total_estimated_cost: float = Field(..., description="Total estimated cost")
    total_actual_cost: float = Field(..., description="Total actual cost")

    # Cache statistics
    cache_hits: int = Field(..., description="Number of cache hits")
    cache_hit_rate: float = Field(..., description="Cache hit rate percentage")

    timestamp: datetime = Field(..., description="Response timestamp")


class StatusResponseModel(BaseModel):
    """Status response model."""

    status: str = Field(..., description="System status")
    timestamp: datetime = Field(..., description="Status timestamp")

    # Queue statistics
    pending_requests: int = Field(..., description="Number of pending requests")
    processing_requests: int = Field(..., description="Number of processing requests")

    # Cache statistics
    cache_stats: Dict[str, Any] = Field(..., description="Cache statistics")

    # Cost statistics
    cost_stats: Dict[str, Any] = Field(..., description="Cost statistics")

    # Worker statistics
    worker_stats: Dict[str, Any] = Field(..., description="Worker statistics")


# Dependencies
async def get_inference_components():
    """Get inference components."""
    cache = await get_inference_cache()
    deduplicator = await get_request_deduplicator()
    batch_processor = await get_batch_processor()
    queue_manager = await get_queue_manager()
    cost_optimizer = await get_cost_optimizer()
    streaming_manager = await get_streaming_manager()

    return {
        "cache": cache,
        "deduplicator": deduplicator,
        "batch_processor": batch_processor,
        "queue_manager": queue_manager,
        "cost_optimizer": cost_optimizer,
        "streaming_manager": streaming_manager,
    }


# API Endpoints
@router.post("/inference", response_model=InferenceResponseModel)
async def single_inference(
    request: InferenceRequestModel,
    background_tasks: BackgroundTasks,
    components: Dict[str, Any] = Depends(get_inference_components),
):
    """
    Process single inference request with intelligent optimization.

    This endpoint provides:
    - Intelligent caching to reduce costs
    - Request deduplication to avoid duplicate processing
    - Cost optimization with provider selection
    - Performance monitoring and analytics
    - Automatic error handling and retries
    """
    start_time = time.time()

    try:
        # Generate request ID
        request_id = str(uuid.uuid4())

        # Create inference request
        inference_req = InferenceRequest(
            id=request_id,
            prompt=request.prompt,
            model_name=request.model_name,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            user_id=request.user_id,
            workspace_id=request.workspace_id,
            priority=request.priority,
            timeout_seconds=request.timeout_seconds,
            metadata=request.metadata,
        )

        # Check cache first
        cache_key = components["cache"]._generate_cache_key(
            prompt=request.prompt,
            model_name=request.model_name,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        cache_entry = None
        if request.use_cache:
            cache_entry = await components["cache"].get(cache_key)

        if cache_entry:
            # Cache hit
            logger.info(f"Cache hit for request {request_id}")

            # Update usage tracking
            await components["cost_optimizer"].track_usage(
                input_tokens=cache_entry.token_count // 2,  # Estimate
                output_tokens=cache_entry.token_count // 2,
                actual_cost=cache_entry.cost_estimate,
                response_time=0.001,  # Very fast for cache
                model_used=cache_entry.model_name,
                provider_used="cache",
                request_id=request_id,
            )

            return InferenceResponseModel(
                request_id=request_id,
                response=cache_entry.value,
                model_used=cache_entry.model_name,
                provider_used="cache",
                processing_time=time.time() - start_time,
                cache_hit=True,
                input_tokens=cache_entry.token_count // 2,
                output_tokens=cache_entry.token_count // 2,
                estimated_cost=cache_entry.cost_estimate,
                actual_cost=cache_entry.cost_estimate,
                timestamp=datetime.utcnow(),
                metadata={"cache_hit": True, **cache_entry.metadata},
            )

        # Check for duplicates
        is_unique, duplicate = await components["deduplicator"].add_request(
            inference_req
        )
        if not is_unique and duplicate:
            # Duplicate request found
            logger.info(f"Duplicate request found for {request_id}: {duplicate.id}")

            # Wait for original request to complete
            max_wait = min(
                request.timeout_seconds, 60
            )  # Max 60 seconds for duplicate wait
            wait_start = time.time()

            while time.time() - wait_start < max_wait:
                duplicate_req = await components["deduplicator"].get_request(
                    duplicate.id
                )
                if duplicate_req and duplicate_req.status == RequestStatus.COMPLETED:
                    break
                await asyncio.sleep(0.5)

            if duplicate_req and duplicate_req.response:
                return InferenceResponseModel(
                    request_id=request_id,
                    response=duplicate_req.response,
                    model_used=duplicate_req.model_name,
                    provider_used="duplicate",
                    processing_time=time.time() - start_time,
                    cache_hit=False,
                    input_tokens=0,  # Will be filled by original request
                    output_tokens=0,
                    estimated_cost=0.0,
                    actual_cost=0.0,
                    timestamp=datetime.utcnow(),
                    metadata={"duplicate_request": duplicate.id},
                )

        # Estimate tokens and cost
        input_tokens = await components["cost_optimizer"].estimate_tokens(
            prompt=request.prompt, model_name=request.model_name
        )

        # Select optimal provider if cost optimization is enabled
        if request.cost_optimize:
            provider, model, cost = await components[
                "cost_optimizer"
            ].select_optimal_provider(
                input_tokens=input_tokens,
                output_tokens=request.max_tokens or 1000,
                requirements={"min_quality": 0.8},
                user_budget=request.budget_limit,
            )
            inference_req.model_name = model
        else:
            provider = "openai"  # Default
            cost = await components["cost_optimizer"].estimate_cost(
                input_tokens=input_tokens,
                output_tokens=request.max_tokens or 1000,
                model_name=request.model_name,
                provider=provider,
            )

        # Process the request
        try:
            # Mark as processing
            await components["deduplicator"].mark_processing(request_id)

            # Create LLM request
            llm_request = LLMRequest(
                prompt=request.prompt,
                model_name=inference_req.model_name,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )

            # Process with LLM manager
            llm_manager = LLMManager()
            llm_response = await llm_manager.process_request(llm_request)

            processing_time = time.time() - start_time

            # Calculate actual tokens and cost
            output_tokens = await components["cost_optimizer"].estimate_tokens(
                prompt=llm_response.content, model_name=inference_req.model_name
            )
            actual_cost = await components["cost_optimizer"].estimate_cost(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                model_name=inference_req.model_name,
                provider=provider,
            )

            # Cache the response
            if request.use_cache:
                await components["cache"].set(
                    cache_key=cache_key,
                    value=llm_response.content,
                    model_name=inference_req.model_name,
                    cost_estimate=actual_cost,
                    token_count=input_tokens + output_tokens,
                    ttl_seconds=3600,  # 1 hour
                    prompt=request.prompt,
                )

            # Mark as completed
            await components["deduplicator"].mark_completed(
                request_id, llm_response.content
            )

            # Track usage
            await components["cost_optimizer"].track_usage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                actual_cost=actual_cost,
                response_time=processing_time,
                model_used=inference_req.model_name,
                provider_used=provider,
                request_id=request_id,
            )

            return InferenceResponseModel(
                request_id=request_id,
                response=llm_response.content,
                model_used=inference_req.model_name,
                provider_used=provider,
                processing_time=processing_time,
                cache_hit=False,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                estimated_cost=cost,
                actual_cost=actual_cost,
                timestamp=datetime.utcnow(),
                metadata={
                    "strategy": request.strategy,
                    "optimization_enabled": request.cost_optimize,
                },
            )

        except Exception as e:
            # Mark as failed
            await components["deduplicator"].mark_completed(request_id, None, str(e))
            raise HTTPException(
                status_code=500, detail=f"Inference processing failed: {str(e)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in single inference: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/batch-inference", response_model=BatchInferenceResponseModel)
async def batch_inference(
    batch_request: BatchInferenceRequestModel,
    background_tasks: BackgroundTasks,
    components: Dict[str, Any] = Depends(get_inference_components),
):
    """
    Process batch inference requests with optimization.

    This endpoint provides:
    - Intelligent batching and deduplication
    - Parallel processing for improved throughput
    - Cost optimization across the batch
    - Comprehensive batch analytics
    - Error handling with fail-fast option
    """
    start_time = time.time()
    batch_id = batch_request.batch_id or str(uuid.uuid4())

    try:
        # Convert to inference requests
        inference_requests = []
        for req in batch_request.requests:
            inference_req = InferenceRequest(
                id=str(uuid.uuid4()),
                prompt=req.prompt,
                model_name=req.model_name,
                temperature=req.temperature,
                max_tokens=req.max_tokens,
                user_id=req.user_id,
                workspace_id=req.workspace_id,
                priority=req.priority,
                timeout_seconds=req.timeout_seconds,
                metadata=req.metadata,
            )
            inference_requests.append(inference_req)

        # Add to batch processor
        successful_requests = []
        failed_requests = []
        duplicate_requests = []
        responses = []

        for req in inference_requests:
            # Check for duplicates
            is_unique, duplicate = await components["deduplicator"].add_request(req)
            if not is_unique and duplicate:
                duplicate_requests.append(req.id)
                continue

            # Add to batch processor
            added, request_id = await components["batch_processor"].add_request(req)
            if added:
                successful_requests.append(req)
            else:
                failed_requests.append(req)

        # Process requests
        if batch_request.parallel_processing:
            # Process in parallel
            tasks = []
            for req in successful_requests:
                task = _process_single_request(req, batch_request, components)
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            # Process sequentially
            results = []
            for req in successful_requests:
                try:
                    result = await _process_single_request(
                        req, batch_request, components
                    )
                    results.append(result)
                except Exception as e:
                    results.append(e)

        # Process results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                if batch_request.fail_fast and i == 0:
                    raise result
                failed_requests.append(successful_requests[i])
            else:
                responses.append(result)

        # Calculate statistics
        total_processing_time = time.time() - start_time
        avg_processing_time = total_processing_time / len(responses) if responses else 0

        total_estimated_cost = sum(resp.estimated_cost for resp in responses)
        total_actual_cost = sum(resp.actual_cost for resp in responses)

        cache_hits = sum(1 for resp in responses if resp.cache_hit)
        cache_hit_rate = (cache_hits / len(responses)) * 100 if responses else 0

        return BatchInferenceResponseModel(
            batch_id=batch_id,
            responses=responses,
            total_requests=len(batch_request.requests),
            successful_requests=len(responses),
            failed_requests=len(failed_requests),
            duplicate_requests=len(duplicate_requests),
            total_processing_time=total_processing_time,
            avg_processing_time=avg_processing_time,
            total_estimated_cost=total_estimated_cost,
            total_actual_cost=total_actual_cost,
            cache_hits=cache_hits,
            cache_hit_rate=cache_hit_rate,
            timestamp=datetime.utcnow(),
        )

    except Exception as e:
        logger.error(f"Error in batch inference: {e}")
        raise HTTPException(status_code=500, detail=f"Batch inference failed: {str(e)}")


async def _process_single_request(
    request: InferenceRequest,
    batch_request: BatchInferenceRequestModel,
    components: Dict[str, Any],
) -> InferenceResponseModel:
    """Process a single request within a batch."""
    # Convert to single request model
    single_req = InferenceRequestModel(
        prompt=request.prompt,
        model_name=request.model_name,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        user_id=request.user_id,
        workspace_id=request.workspace_id,
        priority=request.priority,
        timeout_seconds=min(request.timeout_seconds, batch_request.timeout_seconds),
        metadata=request.metadata,
    )

    # Process as single request
    response = await single_inference(single_req, BackgroundTasks(), components)
    return response


@router.websocket("/stream/{request_id}")
async def stream_inference(
    websocket: WebSocket,
    request_id: str,
    components: Dict[str, Any] = Depends(get_inference_components),
):
    """
    Stream inference results for long-running tasks.

    This endpoint provides:
    - Real-time progress updates
    - Chunked response delivery
    - Connection management
    - Error handling and recovery
    """
    try:
        # Accept WebSocket connection
        await websocket.accept()

        # Create streaming service
        streaming_service = StreamingInferenceService(components["streaming_manager"])

        # Create inference generator
        async def inference_generator():
            # This would be your actual inference logic
            # For now, we'll simulate progress
            for i in range(10):
                yield {
                    "progress": {
                        "current": i + 1,
                        "total": 10,
                        "message": f"Processing step {i + 1}/10",
                    }
                }
                await asyncio.sleep(1)

            yield {
                "data": "This is the final inference result",
                "metadata": {"completed": True},
            }

        # Stream inference
        success = await streaming_service.stream_inference(
            request_id=request_id,
            websocket=websocket,
            inference_generator=inference_generator(),
        )

        if not success:
            await websocket.close(code=1000, reason="Stream completed")

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for request {request_id}")
    except Exception as e:
        logger.error(f"Error in streaming inference: {e}")
        await websocket.close(code=1011, reason=str(e))


@router.get("/status", response_model=StatusResponseModel)
async def get_status(components: Dict[str, Any] = Depends(get_inference_components)):
    """
    Get system status and statistics.

    This endpoint provides:
    - Current system status
    - Queue statistics
    - Cache performance
    - Cost analytics
    - Worker health
    """
    try:
        # Get queue stats
        queue_stats = await components["queue_manager"].get_system_stats()

        # Get cache stats
        cache_stats = await components["cache"].get_comprehensive_stats()

        # Get cost stats
        cost_stats = await components["cost_optimizer"].get_cost_analysis(days=7)

        # Get deduplicator stats
        deduplicator_stats = await components["deduplicator"].get_stats()

        # Get batch processor stats
        batch_stats = await components["batch_processor"].get_stats()

        # Calculate pending/processing requests
        pending_requests = sum(
            queue_stats["queue_stats"].get(q_id, {}).get("current_size", 0)
            for q_id in queue_stats["queue_stats"]
        )
        processing_requests = sum(
            queue_stats["queue_stats"].get(q_id, {}).get("processing_count", 0)
            for q_id in queue_stats["queue_stats"]
        )

        return StatusResponseModel(
            status="healthy",
            timestamp=datetime.utcnow(),
            pending_requests=pending_requests,
            processing_requests=processing_requests,
            cache_stats=cache_stats,
            cost_stats=cost_stats,
            worker_stats={
                "total_workers": queue_stats["manager_stats"]["total_workers"],
                "active_workers": queue_stats["manager_stats"]["active_workers"],
                "total_requests_processed": queue_stats["manager_stats"][
                    "total_requests_processed"
                ],
                "deduplicator": deduplicator_stats,
                "batch_processor": batch_stats,
            },
        )

    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.get("/providers")
async def get_providers(components: Dict[str, Any] = Depends(get_inference_components)):
    """
    Get available providers and recommendations.

    This endpoint provides:
    - List of available providers
    - Provider recommendations based on cost
    - Performance metrics for each provider
    - Pricing information
    """
    try:
        # Get provider recommendations
        recommendations = await components[
            "cost_optimizer"
        ].get_provider_recommendations(
            input_tokens=1000,
            output_tokens=1000,
        )

        return {
            "providers": recommendations,
            "timestamp": datetime.utcnow(),
        }

    except Exception as e:
        logger.error(f"Error getting providers: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get providers: {str(e)}"
        )


@router.post("/clear-cache")
async def clear_cache(
    level: str = "all",  # Options: l1, l2, l3, all
    components: Dict[str, Any] = Depends(get_inference_components),
):
    """
    Clear cache at specified level.

    This endpoint provides:
    - Cache clearing by level
    - Cache statistics before/after
    - Selective cache clearing
    """
    try:
        if level == "all":
            success = await components["cache"].clear_all()
        elif level == "l1":
            success = await components["cache"].l1_cache.clear()
        elif level == "l2":
            success = await components["cache"].l2_cache.clear()
        elif level == "l3":
            success = await components["cache"].l3_cache.clear()
        else:
            raise HTTPException(
                status_code=400, detail="Invalid cache level. Options: l1, l2, l3, all"
            )

        return {
            "success": success,
            "level": level,
            "timestamp": datetime.utcnow(),
        }

    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")


@router.get("/analytics")
async def get_analytics(
    days: int = 7, components: Dict[str, Any] = Depends(get_inference_components)
):
    """
    Get comprehensive analytics and insights.

    This endpoint provides:
    - Cost analysis over time
    - Performance metrics
    - Usage patterns
    - Provider comparisons
    - Cache efficiency
    """
    try:
        # Get cost analysis
        cost_analysis = await components["cost_optimizer"].get_cost_analysis(days=days)

        # Get cache stats
        cache_stats = await components["cache"].get_comprehensive_stats()

        # Get queue stats
        queue_stats = await components["queue_manager"].get_system_stats()

        return {
            "cost_analysis": cost_analysis,
            "cache_stats": cache_stats,
            "queue_stats": queue_stats,
            "period_days": days,
            "timestamp": datetime.utcnow(),
        }

    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get analytics: {str(e)}"
        )
