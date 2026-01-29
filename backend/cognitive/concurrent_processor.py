"""
Concurrent Processing Engine
Replaces sequential blocking with true concurrent processing
"""

import asyncio
import logging
import time
import uuid
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from error_handling import ErrorHandler, with_error_handling
from interfaces import (
    IHumanLoopModule,
    IPerceptionModule,
    IPlanningModule,
    IReflectionModule,
)
from metrics import LLMProvider, ProcessingPhase, metrics_collector
from rate_limiter import RateLimitExceeded, rate_limiter
from resource_manager import resource_manager
from validation import ProcessingRequest, ValidationResult, validator

logger = logging.getLogger(__name__)


class RequestPriority(Enum):
    """Request priority levels"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class QueuedRequest:
    """Request in processing queue"""

    request_id: str
    request_data: ProcessingRequest
    priority: RequestPriority
    submitted_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def __lt__(self, other):
        # Higher priority requests come first
        return self.priority.value > other.priority.value


@dataclass
class ProcessingResult:
    """Result of concurrent processing"""

    request_id: str
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    processing_time_ms: int = 0
    phase: str = "completed"
    metrics: Dict[str, Any] = field(default_factory=dict)


class ConcurrentProcessor:
    """Concurrent request processor with queue management"""

    def __init__(
        self,
        max_concurrent_requests: int = 10,
        max_queue_size: int = 100,
        worker_threads: int = 5,
    ):
        self.max_concurrent_requests = max_concurrent_requests
        self.max_queue_size = max_queue_size
        self.worker_threads = worker_threads

        # Processing queue (priority queue)
        self.processing_queue: asyncio.PriorityQueue = asyncio.PriorityQueue(
            maxsize=max_queue_size
        )

        # Active requests tracking
        self.active_requests: Dict[str, asyncio.Task] = {}
        self.request_results: Dict[str, ProcessingResult] = {}

        # Worker pools
        self.thread_pool = ThreadPoolExecutor(max_workers=worker_threads)
        self.process_pool = ProcessPoolExecutor(max_workers=max_workers // 2)

        # Semaphore for concurrency control
        self.concurrency_semaphore = asyncio.Semaphore(max_concurrent_requests)

        # Module instances (injected via DI)
        self.perception_module: Optional[IPerceptionModule] = None
        self.planning_module: Optional[IPlanningModule] = None
        self.reflection_module: Optional[IReflectionModule] = None
        self.human_loop_module: Optional[IHumanLoopModule] = None

        # Error handler
        self.error_handler = ErrorHandler()

        # Processing stats
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "queue_size": 0,
            "active_requests": 0,
            "average_processing_time_ms": 0,
        }

        # Background tasks
        self.processor_task: Optional[asyncio.Task] = None
        self._running = False

    def set_modules(
        self,
        perception: IPerceptionModule,
        planning: IPlanningModule,
        reflection: IReflectionModule,
        human_loop: IHumanLoopModule,
    ):
        """Set cognitive modules"""
        self.perception_module = perception
        self.planning_module = planning
        self.reflection_module = reflection
        self.human_loop_module = human_loop

    async def start(self):
        """Start the concurrent processor"""
        self._running = True
        self.processor_task = asyncio.create_task(self._process_queue())
        logger.info("Concurrent processor started")

    async def stop(self):
        """Stop the concurrent processor"""
        self._running = False

        # Cancel processor task
        if self.processor_task:
            self.processor_task.cancel()
            try:
                await self.processor_task
            except asyncio.CancelledError:
                pass

        # Cancel all active requests
        for task in self.active_requests.values():
            task.cancel()

        # Wait for all tasks to complete
        if self.active_requests:
            await asyncio.gather(*self.active_requests.values(), return_exceptions=True)

        # Shutdown worker pools
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)

        logger.info("Concurrent processor stopped")

    async def submit_request(
        self,
        request_data: ProcessingRequest,
        priority: RequestPriority = RequestPriority.NORMAL,
    ) -> str:
        """Submit a request for processing"""

        # Check rate limiting
        client_id = request_data.user_context.user_id
        allowed, retry_after = await rate_limiter.check_rate_limit(
            client_id=client_id, user_tier=request_data.user_context.subscription_tier
        )

        if not allowed:
            raise RateLimitExceeded(
                f"Rate limit exceeded for user {client_id}", retry_after=retry_after
            )

        # Check queue capacity
        if self.processing_queue.qsize() >= self.max_queue_size:
            raise Exception("Processing queue is full")

        # Create queued request
        request_id = str(uuid.uuid4())
        queued_request = QueuedRequest(
            request_id=request_id,
            request_data=request_data,
            priority=priority,
            submitted_at=datetime.now(),
        )

        # Add to queue (negative priority for max-heap behavior)
        await self.processing_queue.put((-priority.value, queued_request))

        # Update stats
        self.stats["total_requests"] += 1
        self.stats["queue_size"] = self.processing_queue.qsize()

        logger.info(f"Submitted request {request_id} with priority {priority.name}")
        return request_id

    async def get_result(
        self, request_id: str, timeout: Optional[float] = None
    ) -> ProcessingResult:
        """Get result of a request"""
        start_time = time.time()

        while request_id not in self.request_results:
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(f"Request {request_id} not completed within timeout")

            await asyncio.sleep(0.1)

        return self.request_results.pop(request_id)

    async def cancel_request(self, request_id: str) -> bool:
        """Cancel a request"""
        if request_id in self.active_requests:
            task = self.active_requests[request_id]
            task.cancel()
            del self.active_requests[request_id]

            # Record cancellation
            self.request_results[request_id] = ProcessingResult(
                request_id=request_id, success=False, error="Request cancelled"
            )

            return True

        return False

    async def _process_queue(self):
        """Main queue processing loop"""
        while self._running:
            try:
                # Get next request from queue
                priority_item = await asyncio.processing_queue.get()
                _, queued_request = priority_item

                # Process with concurrency limit
                async with self.concurrency_semaphore:
                    task = asyncio.create_task(self._process_request(queued_request))
                    self.active_requests[queued_request.request_id] = task

                    # Update stats
                    self.stats["active_requests"] = len(self.active_requests)
                    self.stats["queue_size"] = self.processing_queue.qsize()

                # Clean up completed task
                task.add_done_callback(
                    lambda t: self._cleanup_task(queued_request.request_id)
                )

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Queue processing error: {e}")
                await asyncio.sleep(1)

    async def _process_request(self, queued_request: QueuedRequest) -> ProcessingResult:
        """Process a single request"""
        request_id = queued_request.request_id
        request_data = queued_request.request_data

        queued_request.started_at = datetime.now()
        start_time = time.time()

        try:
            # Validate request
            validation_result = validator.validate_request(request_data.dict())
            if not validation_result.is_valid:
                return ProcessingResult(
                    request_id=request_id,
                    success=False,
                    error=f"Validation failed: {', '.join(validation_result.errors)}",
                )

            # Process through cognitive pipeline concurrently
            result = await self._process_cognitive_pipeline(
                request_id, validation_result.sanitized_data
            )

            # Update stats
            processing_time = int((time.time() - start_time) * 1000)
            self.stats["successful_requests"] += 1
            self.stats["average_processing_time_ms"] = (
                self.stats["average_processing_time_ms"]
                * (self.stats["successful_requests"] - 1)
                + processing_time
            ) / self.stats["successful_requests"]

            return ProcessingResult(
                request_id=request_id,
                success=True,
                result=result,
                processing_time_ms=processing_time,
            )

        except Exception as e:
            # Handle error
            error_result = self.error_handler.handle_error(
                e=e,
                phase="processing",
                request_id=request_id,
                context={"request_data": request_data.dict()},
            )

            # Update stats
            self.stats["failed_requests"] += 1

            return ProcessingResult(
                request_id=request_id,
                success=False,
                error=error_result.get("error_message", str(e)),
                processing_time_ms=int((time.time() - start_time) * 1000),
            )

        finally:
            queued_request.completed_at = datetime.now()

    async def _process_cognitive_pipeline(
        self, request_id: str, request_data: Dict[str, Any]
    ) -> Any:
        """Process cognitive pipeline with concurrent phases"""

        # Extract request data
        request_text = request_data["request"]
        session_id = request_data["session_id"]
        workspace_id = request_data["workspace_id"]
        user_context = request_data["user_context"]

        # Phase 1: Perception
        perception_task = asyncio.create_task(
            self._run_perception_phase(request_id, request_text, user_context)
        )

        # Wait for perception to complete
        perceived_input = await perception_task

        # Phase 2: Planning (can run concurrently with some reflection prep)
        planning_task = asyncio.create_task(
            self._run_planning_phase(request_id, perceived_input, user_context)
        )

        # Wait for planning to complete
        execution_plan = await planning_task

        # Phase 3: Execution (if enabled)
        execution_result = None
        if request_data.get("auto_execute", False):
            execution_task = asyncio.create_task(
                self._run_execution_phase(request_id, execution_plan)
            )
            execution_result = await execution_task

        # Phase 4: Reflection (can run concurrently with execution if results available)
        reflection_input = execution_result or execution_plan
        reflection_task = asyncio.create_task(
            self._run_reflection_phase(
                request_id, request_text, reflection_input, user_context
            )
        )

        quality_score = await reflection_task

        # Phase 5: Self-correction (if needed)
        if quality_score and not quality_score.get("passes_quality", True):
            correction_task = asyncio.create_task(
                self._run_self_correction_phase(
                    request_id, reflection_input, quality_score, user_context
                )
            )
            correction_result = await correction_task
        else:
            correction_result = None

        # Phase 6: Human-in-the-loop (if needed)
        human_approval = None
        if request_data.get("enable_human_approval", True):
            human_task = asyncio.create_task(
                self._run_human_loop_phase(
                    request_id,
                    reflection_input,
                    execution_plan,
                    quality_score,
                    user_context,
                )
            )
            human_approval = await human_task

        return {
            "perceived_input": perceived_input,
            "execution_plan": execution_plan,
            "execution_result": execution_result,
            "quality_score": quality_score,
            "correction_result": correction_result,
            "human_approval": human_approval,
        }

    async def _run_perception_phase(
        self, request_id: str, request_text: str, user_context: Dict[str, Any]
    ) -> Any:
        """Run perception phase with metrics tracking"""
        start_time = time.time()

        try:
            if not self.perception_module:
                raise Exception("Perception module not configured")

            result = await self.perception_module.perceive(request_text, user_context)

            # Track metrics
            await metrics_collector.track_request(
                request_id=request_id,
                session_id=user_context.get("session_id", "unknown"),
                workspace_id=user_context.get("workspace_id", "unknown"),
                user_id=user_context.get("user_id", "unknown"),
                phase=ProcessingPhase.PERCEPTION,
                provider=LLMProvider.OPENAI,  # Should be configurable
                model="gpt-3.5-turbo",
                input_text=request_text,
                processing_time_ms=int((time.time() - start_time) * 1000),
                success=True,
            )

            return result

        except Exception as e:
            await metrics_collector.track_request(
                request_id=request_id,
                session_id=user_context.get("session_id", "unknown"),
                workspace_id=user_context.get("workspace_id", "unknown"),
                user_id=user_context.get("user_id", "unknown"),
                phase=ProcessingPhase.PERCEPTION,
                provider=LLMProvider.OPENAI,
                model="gpt-3.5-turbo",
                input_text=request_text,
                processing_time_ms=int((time.time() - start_time) * 1000),
                success=False,
                error_message=str(e),
            )
            raise

    async def _run_planning_phase(
        self, request_id: str, perceived_input: Any, user_context: Dict[str, Any]
    ) -> Any:
        """Run planning phase with metrics tracking"""
        start_time = time.time()

        try:
            if not self.planning_module:
                raise Exception("Planning module not configured")

            # Extract goal from perceived input
            goal = getattr(perceived_input, "primary_intent", "general_query")

            result = await self.planning_module.create_plan(goal, perceived_input)

            # Track metrics
            await metrics_collector.track_request(
                request_id=request_id,
                session_id=user_context.get("session_id", "unknown"),
                workspace_id=user_context.get("workspace_id", "unknown"),
                user_id=user_context.get("user_id", "unknown"),
                phase=ProcessingPhase.PLANNING,
                provider=LLMProvider.OPENAI,
                model="gpt-3.5-turbo",
                input_text=str(perceived_input),
                processing_time_ms=int((time.time() - start_time) * 1000),
                success=True,
            )

            return result

        except Exception as e:
            await metrics_collector.track_request(
                request_id=request_id,
                session_id=user_context.get("session_id", "unknown"),
                workspace_id=user_context.get("workspace_id", "unknown"),
                user_id=user_context.get("user_id", "unknown"),
                phase=ProcessingPhase.PLANNING,
                provider=LLMProvider.OPENAI,
                model="gpt-3.5-turbo",
                input_text=str(perceived_input),
                processing_time_ms=int((time.time() - start_time) * 1000),
                success=False,
                error_message=str(e),
            )
            raise

    async def _run_execution_phase(self, request_id: str, execution_plan: Any) -> Any:
        """Run execution phase"""
        # Placeholder for actual execution
        await asyncio.sleep(0.1)  # Simulate work
        return {"executed": True, "plan_id": getattr(execution_plan, "id", "unknown")}

    async def _run_reflection_phase(
        self,
        request_id: str,
        request_text: str,
        output: Any,
        user_context: Dict[str, Any],
    ) -> Any:
        """Run reflection phase with metrics tracking"""
        start_time = time.time()

        try:
            if not self.reflection_module:
                raise Exception("Reflection module not configured")

            result = await self.reflection_module.evaluate(
                request_text, output, user_context
            )

            # Track metrics
            await metrics_collector.track_request(
                request_id=request_id,
                session_id=user_context.get("session_id", "unknown"),
                workspace_id=user_context.get("workspace_id", "unknown"),
                user_id=user_context.get("user_id", "unknown"),
                phase=ProcessingPhase.REFLECTION,
                provider=LLMProvider.OPENAI,
                model="gpt-3.5-turbo",
                input_text=f"{request_text}\n\n{str(output)}",
                processing_time_ms=int((time.time() - start_time) * 1000),
                success=True,
            )

            return result

        except Exception as e:
            await metrics_collector.track_request(
                request_id=request_id,
                session_id=user_context.get("session_id", "unknown"),
                workspace_id=user_context.get("workspace_id", "unknown"),
                user_id=user_context.get("user_id", "unknown"),
                phase=ProcessingPhase.REFLECTION,
                provider=LLMProvider.OPENAI,
                model="gpt-3.5-turbo",
                input_text=f"{request_text}\n\n{str(output)}",
                processing_time_ms=int((time.time() - start_time) * 1000),
                success=False,
                error_message=str(e),
            )
            raise

    async def _run_self_correction_phase(
        self,
        request_id: str,
        output: Any,
        quality_score: Any,
        user_context: Dict[str, Any],
    ) -> Any:
        """Run self-correction phase"""
        # Placeholder for self-correction
        await asyncio.sleep(0.1)
        return {"corrected": True, "original_quality": quality_score}

    async def _run_human_loop_phase(
        self,
        request_id: str,
        content: Any,
        execution_plan: Any,
        quality_score: Any,
        user_context: Dict[str, Any],
    ) -> Any:
        """Run human-in-the-loop phase"""
        # Placeholder for human loop
        await asyncio.sleep(0.05)
        return {"approval_required": False, "status": "auto_approved"}

    def _cleanup_task(self, request_id: str):
        """Clean up completed task"""
        self.active_requests.pop(request_id, None)
        self.stats["active_requests"] = len(self.active_requests)

    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {
            **self.stats,
            "queue_size": self.processing_queue.qsize(),
            "active_requests": len(self.active_requests),
            "max_concurrent_requests": self.max_concurrent_requests,
            "max_queue_size": self.max_queue_size,
        }


# Global concurrent processor
concurrent_processor = ConcurrentProcessor()
