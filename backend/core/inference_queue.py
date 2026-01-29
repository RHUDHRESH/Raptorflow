"""
AI Inference Queue Management System
===================================

Advanced queue management for AI inference with priority handling, worker management,
and intelligent load balancing.

Features:
- Priority-based request queuing
- Dynamic worker pool management
- Load balancing across providers
- Queue monitoring and analytics
- Automatic scaling and optimization
- Dead letter queue handling
- Performance metrics and alerts
"""

import asyncio
import json
import logging
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import weakref

import numpy as np
import structlog

from batch_processor import InferenceRequest, RequestStatus
from inference_optimizer import get_cost_optimizer

logger = structlog.get_logger(__name__)


class QueuePriority(str, Enum):
    """Queue priority levels."""

    CRITICAL = "critical"  # 9-10
    HIGH = "high"  # 7-8
    MEDIUM = "medium"  # 5-6
    LOW = "low"  # 3-4
    BACKGROUND = "background"  # 1-2


class WorkerStatus(str, Enum):
    """Worker status types."""

    IDLE = "idle"
    BUSY = "busy"
    STARTING = "starting"
    STOPPING = "stopping"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class QueueType(str, Enum):
    """Queue types."""

    PRIORITY = "priority"
    FIFO = "fifo"
    LIFO = "lifo"
    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"


@dataclass
class QueueMetrics:
    """Queue performance metrics."""

    queue_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Queue statistics
    total_requests: int = 0
    pending_requests: int = 0
    processing_requests: int = 0
    completed_requests: int = 0
    failed_requests: int = 0

    # Performance metrics
    avg_wait_time: float = 0.0
    avg_processing_time: float = 0.0
    avg_total_time: float = 0.0
    throughput: float = 0.0  # requests per second

    # Priority distribution
    priority_distribution: Dict[str, int] = field(default_factory=dict)

    # Time-based metrics
    requests_per_minute: float = 0.0
    requests_per_hour: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "queue_id": self.queue_id,
            "timestamp": self.timestamp.isoformat(),
            "total_requests": self.total_requests,
            "pending_requests": self.pending_requests,
            "processing_requests": self.processing_requests,
            "completed_requests": self.completed_requests,
            "failed_requests": self.failed_requests,
            "avg_wait_time": self.avg_wait_time,
            "avg_processing_time": self.avg_processing_time,
            "avg_total_time": self.avg_total_time,
            "throughput": self.throughput,
            "priority_distribution": self.priority_distribution,
            "requests_per_minute": self.requests_per_minute,
            "requests_per_hour": self.requests_per_hour,
        }


@dataclass
class WorkerInfo:
    """Worker information and status."""

    id: str
    provider: str
    model: str
    max_concurrent: int = 1
    current_load: int = 0
    status: WorkerStatus = WorkerStatus.IDLE

    # Performance tracking
    total_processed: int = 0
    avg_processing_time: float = 0.0
    success_rate: float = 1.0
    last_activity: datetime = field(default_factory=datetime.utcnow)

    # Health monitoring
    error_count: int = 0
    max_errors: int = 5
    health_score: float = 1.0

    # Configuration
    supported_priorities: List[QueuePriority] = field(
        default_factory=lambda: list(QueuePriority)
    )
    cost_per_request: float = 0.0

    def is_available(self) -> bool:
        """Check if worker is available for new requests."""
        return (
            self.status == WorkerStatus.IDLE
            and self.current_load < self.max_concurrent
            and self.health_score > 0.5
        )

    def get_load_percentage(self) -> float:
        """Get current load as percentage."""
        return (
            (self.current_load / self.max_concurrent) * 100
            if self.max_concurrent > 0
            else 0
        )

    def update_health(self):
        """Update health score based on performance."""
        # Health score based on success rate and error count
        success_factor = self.success_rate
        error_factor = max(0, 1.0 - (self.error_count / self.max_errors))
        self.health_score = (success_factor + error_factor) / 2

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "provider": self.provider,
            "model": self.model,
            "max_concurrent": self.max_concurrent,
            "current_load": self.current_load,
            "load_percentage": self.get_load_percentage(),
            "status": self.status.value,
            "total_processed": self.total_processed,
            "avg_processing_time": self.avg_processing_time,
            "success_rate": self.success_rate,
            "last_activity": self.last_activity.isoformat(),
            "error_count": self.error_count,
            "max_errors": self.max_errors,
            "health_score": self.health_score,
            "supported_priorities": [p.value for p in self.supported_priorities],
            "cost_per_request": self.cost_per_request,
        }


class InferenceQueue:
    """Individual inference queue with priority handling."""

    def __init__(
        self,
        queue_id: str,
        queue_type: QueueType = QueueType.PRIORITY,
        max_size: int = 10000,
        priority_weights: Optional[Dict[QueuePriority, float]] = None,
    ):
        self.queue_id = queue_id
        self.queue_type = queue_type
        self.max_size = max_size
        self.priority_weights = priority_weights or {
            QueuePriority.CRITICAL: 10.0,
            QueuePriority.HIGH: 5.0,
            QueuePriority.MEDIUM: 2.0,
            QueuePriority.LOW: 1.0,
            QueuePriority.BACKGROUND: 0.5,
        }

        # Queue storage
        self.queues: Dict[QueuePriority, deque] = {p: deque() for p in QueuePriority}
        self.processing: Dict[str, InferenceRequest] = {}  # request_id -> request

        # Metrics tracking
        self.metrics = QueueMetrics(queue_id=queue_id)
        self.request_history: List[Tuple[datetime, InferenceRequest]] = []

        # Lock for thread safety
        self._lock = asyncio.Lock()

        # Statistics
        self.stats = {
            "total_enqueued": 0,
            "total_dequeued": 0,
            "total_completed": 0,
            "total_failed": 0,
            "queue_full_drops": 0,
        }

    def _get_priority_from_request(self, request: InferenceRequest) -> QueuePriority:
        """Get queue priority from request priority."""
        if request.priority >= 9:
            return QueuePriority.CRITICAL
        elif request.priority >= 7:
            return QueuePriority.HIGH
        elif request.priority >= 5:
            return QueuePriority.MEDIUM
        elif request.priority >= 3:
            return QueuePriority.LOW
        else:
            return QueuePriority.BACKGROUND

    async def enqueue(self, request: InferenceRequest) -> bool:
        """Add request to queue."""
        async with self._lock:
            # Check queue capacity
            total_queued = sum(len(queue) for queue in self.queues.values())
            if total_queued >= self.max_size:
                self.stats["queue_full_drops"] += 1
                logger.warning(
                    f"Queue {self.queue_id} is full, dropping request {request.id}"
                )
                return False

            # Add to appropriate priority queue
            priority = self._get_priority_from_request(request)
            self.queues[priority].append(request)

            # Update statistics
            self.stats["total_enqueued"] += 1
            self.metrics.total_requests += 1
            self.metrics.pending_requests += 1

            # Update priority distribution
            priority_str = priority.value
            self.metrics.priority_distribution[priority_str] = (
                self.metrics.priority_distribution.get(priority_str, 0) + 1
            )

            # Add to history
            self.request_history.append((datetime.utcnow(), request))

            # Keep history manageable
            if len(self.request_history) > 10000:
                self.request_history = self.request_history[-5000:]

            logger.debug(
                f"Enqueued request {request.id} with priority {priority.value}"
            )
            return True

    async def dequeue(self) -> Optional[InferenceRequest]:
        """Get next request from queue."""
        async with self._lock:
            # Get next request based on queue type
            request = None

            if self.queue_type == QueueType.PRIORITY:
                # Check queues in priority order
                for priority in QueuePriority:
                    if self.queues[priority]:
                        request = self.queues[priority].popleft()
                        break

            elif self.queue_type == QueueType.FIFO:
                # Get oldest request across all priorities
                oldest_request = None
                oldest_time = None

                for priority, queue in self.queues.items():
                    if queue and (
                        oldest_time is None or queue[0].created_at < oldest_time
                    ):
                        oldest_request = queue[0]
                        oldest_time = queue[0].created_at

                if oldest_request:
                    request = self.queues[
                        self._get_priority_from_request(oldest_request)
                    ].popleft()

            elif self.queue_type == QueueType.WEIGHTED:
                # Weighted random selection based on priority weights
                available_requests = []
                weights = []

                for priority, queue in self.queues.items():
                    for _ in range(len(queue)):
                        available_requests.append(queue[0])
                        weights.append(self.priority_weights[priority])

                if available_requests:
                    # Weighted selection
                    total_weight = sum(weights)
                    if total_weight > 0:
                        probabilities = [w / total_weight for w in weights]
                        selected_idx = np.random.choice(
                            len(available_requests), p=probabilities
                        )
                        selected_request = available_requests[selected_idx]
                        priority = self._get_priority_from_request(selected_request)
                        request = self.queues[priority].popleft()

            if request:
                # Move to processing
                self.processing[request.id] = request
                request.status = RequestStatus.PROCESSING
                request.started_at = datetime.utcnow()

                # Update statistics
                self.stats["total_dequeued"] += 1
                self.metrics.pending_requests -= 1
                self.metrics.processing_requests += 1

                logger.debug(f"Dequeued request {request.id}")
                return request

            return None

    async def complete_request(self, request_id: str, success: bool = True):
        """Mark request as completed."""
        async with self._lock:
            if request_id in self.processing:
                request = self.processing[request_id]
                request.completed_at = datetime.utcnow()
                request.status = (
                    RequestStatus.COMPLETED if success else RequestStatus.FAILED
                )

                # Remove from processing
                del self.processing[request_id]

                # Update statistics
                self.metrics.processing_requests -= 1
                if success:
                    self.metrics.completed_requests += 1
                    self.stats["total_completed"] += 1
                else:
                    self.metrics.failed_requests += 1
                    self.stats["total_failed"] += 1

                # Update metrics
                self._update_metrics()

                logger.debug(f"Completed request {request_id} (success: {success})")

    async def get_queue_size(self) -> int:
        """Get total queue size."""
        async with self._lock:
            return sum(len(queue) for queue in self.queues.values())

    async def get_priority_sizes(self) -> Dict[str, int]:
        """Get queue sizes by priority."""
        async with self._lock:
            return {
                priority.value: len(queue) for priority, queue in self.queues.items()
            }

    def _update_metrics(self):
        """Update queue metrics."""
        # Calculate average times
        completed_requests = [
            req
            for _, req in self.request_history
            if req.status in [RequestStatus.COMPLETED, RequestStatus.FAILED]
            and req.started_at
            and req.completed_at
        ]

        if completed_requests:
            wait_times = []
            processing_times = []
            total_times = []

            for req in completed_requests[-1000:]:  # Last 1000 requests
                wait_time = (req.started_at - req.created_at).total_seconds()
                processing_time = (req.completed_at - req.started_at).total_seconds()
                total_time = wait_time + processing_time

                wait_times.append(wait_time)
                processing_times.append(processing_time)
                total_times.append(total_time)

            self.metrics.avg_wait_time = np.mean(wait_times) if wait_times else 0
            self.metrics.avg_processing_time = (
                np.mean(processing_times) if processing_times else 0
            )
            self.metrics.avg_total_time = np.mean(total_times) if total_times else 0

            # Calculate throughput (requests per second in last minute)
            now = datetime.utcnow()
            recent_requests = [
                req
                for _, req in self.request_history
                if (now - req.created_at).total_seconds() <= 60
            ]
            self.metrics.throughput = len(recent_requests) / 60.0

            # Calculate requests per minute/hour
            self.metrics.requests_per_minute = len(recent_requests)
            self.metrics.requests_per_hour = len(
                [
                    req
                    for _, req in self.request_history
                    if (now - req.created_at).total_seconds() <= 3600
                ]
            )

    async def get_metrics(self) -> QueueMetrics:
        """Get current queue metrics."""
        async with self._lock:
            self._update_metrics()

            # Update current counts
            self.metrics.pending_requests = sum(
                len(queue) for queue in self.queues.values()
            )
            self.metrics.processing_requests = len(self.processing)

            return self.metrics

    async def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        async with self._lock:
            return {
                "queue_id": self.queue_id,
                "queue_type": self.queue_type.value,
                "max_size": self.max_size,
                "current_size": await self.get_queue_size(),
                "priority_sizes": await self.get_priority_sizes(),
                "processing_count": len(self.processing),
                "stats": self.stats,
                "metrics": self.metrics.to_dict(),
            }


class InferenceQueueManager:
    """Manages multiple inference queues and workers."""

    def __init__(
        self,
        max_workers: int = 10,
        auto_scale: bool = True,
        scale_up_threshold: float = 0.8,
        scale_down_threshold: float = 0.2,
    ):
        self.max_workers = max_workers
        self.auto_scale = auto_scale
        self.scale_up_threshold = scale_up_threshold
        self.scale_down_threshold = scale_down_threshold

        # Queue management
        self.queues: Dict[str, InferenceQueue] = {}
        self.default_queue_id = "default"

        # Worker management
        self.workers: Dict[str, WorkerInfo] = {}
        self.worker_assignments: Dict[str, str] = {}  # worker_id -> queue_id

        # Load balancing
        self.load_balancer = LoadBalancer()

        # Background tasks
        self._scaling_task = None
        self._metrics_task = None
        self._running = False

        # Lock for thread safety
        self._lock = asyncio.Lock()

        # Statistics
        self.stats = {
            "total_queues": 0,
            "total_workers": 0,
            "active_workers": 0,
            "total_requests_processed": 0,
            "avg_queue_wait_time": 0.0,
            "system_throughput": 0.0,
        }

    async def start(self):
        """Start queue manager."""
        if self._running:
            return

        self._running = True

        # Create default queue
        await self.create_queue(self.default_queue_id)

        # Start background tasks
        self._scaling_task = asyncio.create_task(self._auto_scale_workers())
        self._metrics_task = asyncio.create_task(self._update_metrics())

        logger.info("Inference queue manager started")

    async def stop(self):
        """Stop queue manager."""
        self._running = False

        if self._scaling_task:
            self._scaling_task.cancel()
            try:
                await self._scaling_task
            except asyncio.CancelledError:
                pass

        if self._metrics_task:
            self._metrics_task.cancel()
            try:
                await self._metrics_task
            except asyncio.CancelledError:
                pass

        logger.info("Inference queue manager stopped")

    async def create_queue(
        self,
        queue_id: str,
        queue_type: QueueType = QueueType.PRIORITY,
        max_size: int = 10000,
        priority_weights: Optional[Dict[QueuePriority, float]] = None,
    ) -> bool:
        """Create new inference queue."""
        async with self._lock:
            if queue_id in self.queues:
                logger.warning(f"Queue {queue_id} already exists")
                return False

            queue = InferenceQueue(
                queue_id=queue_id,
                queue_type=queue_type,
                max_size=max_size,
                priority_weights=priority_weights,
            )

            self.queues[queue_id] = queue
            self.stats["total_queues"] += 1

            logger.info(f"Created queue {queue_id}")
            return True

    async def add_worker(
        self,
        worker_id: str,
        provider: str,
        model: str,
        max_concurrent: int = 1,
        queue_id: Optional[str] = None,
    ) -> bool:
        """Add worker to system."""
        async with self._lock:
            if worker_id in self.workers:
                logger.warning(f"Worker {worker_id} already exists")
                return False

            if len(self.workers) >= self.max_workers:
                logger.warning(f"Maximum workers ({self.max_workers}) reached")
                return False

            # Assign to queue (default if not specified)
            if queue_id is None:
                queue_id = self.default_queue_id

            if queue_id not in self.queues:
                await self.create_queue(queue_id)

            worker = WorkerInfo(
                id=worker_id,
                provider=provider,
                model=model,
                max_concurrent=max_concurrent,
            )

            self.workers[worker_id] = worker
            self.worker_assignments[worker_id] = queue_id
            self.stats["total_workers"] += 1

            logger.info(f"Added worker {worker_id} to queue {queue_id}")
            return True

    async def enqueue_request(
        self,
        request: InferenceRequest,
        queue_id: Optional[str] = None,
    ) -> bool:
        """Enqueue request for processing."""
        if queue_id is None:
            queue_id = self.default_queue_id

        if queue_id not in self.queues:
            logger.error(f"Queue {queue_id} not found")
            return False

        queue = self.queues[queue_id]
        return await queue.enqueue(request)

    async def get_next_request(self, worker_id: str) -> Optional[InferenceRequest]:
        """Get next request for worker."""
        async with self._lock:
            if worker_id not in self.workers:
                logger.error(f"Worker {worker_id} not found")
                return None

            worker = self.workers[worker_id]
            queue_id = self.worker_assignments.get(worker_id, self.default_queue_id)

            if queue_id not in self.queues:
                logger.error(f"Queue {queue_id} not found for worker {worker_id}")
                return None

            queue = self.queues[queue_id]
            request = await queue.dequeue()

            if request:
                worker.current_load += 1
                worker.status = WorkerStatus.BUSY
                worker.last_activity = datetime.utcnow()

            return request

    async def complete_request(
        self,
        worker_id: str,
        request_id: str,
        success: bool = True,
        processing_time: Optional[float] = None,
    ):
        """Complete request processing."""
        async with self._lock:
            if worker_id not in self.workers:
                return

            worker = self.workers[worker_id]
            queue_id = self.worker_assignments.get(worker_id, self.default_queue_id)

            if queue_id in self.queues:
                await self.queues[queue_id].complete_request(request_id, success)

            # Update worker stats
            worker.current_load = max(0, worker.current_load - 1)
            worker.total_processed += 1

            if processing_time:
                # Update average processing time
                total_processed = worker.total_processed
                current_avg = worker.avg_processing_time
                worker.avg_processing_time = (
                    current_avg * (total_processed - 1) + processing_time
                ) / total_processed

            if success:
                worker.success_rate = min(1.0, worker.success_rate * 0.95 + 0.05)
            else:
                worker.success_rate = max(0.0, worker.success_rate * 0.95)
                worker.error_count += 1

            worker.update_health()

            # Update status
            if worker.current_load == 0:
                worker.status = WorkerStatus.IDLE

            # Update global stats
            self.stats["total_requests_processed"] += 1

    async def get_available_workers(
        self, queue_id: Optional[str] = None
    ) -> List[WorkerInfo]:
        """Get list of available workers."""
        async with self._lock:
            available_workers = []

            for worker_id, worker in self.workers.items():
                if worker.is_available():
                    if (
                        queue_id is None
                        or self.worker_assignments.get(worker_id) == queue_id
                    ):
                        available_workers.append(worker)

            return available_workers

    async def _auto_scale_workers(self):
        """Background task for automatic worker scaling."""
        while self._running:
            try:
                if not self.auto_scale:
                    await asyncio.sleep(30)
                    continue

                # Calculate system load
                total_capacity = sum(w.max_concurrent for w in self.workers.values())
                current_load = sum(w.current_load for w in self.workers.values())
                system_load = current_load / total_capacity if total_capacity > 0 else 0

                # Check queues for pending requests
                total_pending = sum(
                    await queue.get_queue_size() for queue in self.queues.values()
                )

                # Scale up if needed
                if (
                    system_load > self.scale_up_threshold or total_pending > 10
                ) and len(self.workers) < self.max_workers:
                    await self._scale_up()

                # Scale down if needed
                elif (
                    system_load < self.scale_down_threshold
                    and total_pending == 0
                    and len(self.workers) > 1
                ):
                    await self._scale_down()

                await asyncio.sleep(30)  # Check every 30 seconds

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in auto-scaling: {e}")
                await asyncio.sleep(30)

    async def _scale_up(self):
        """Scale up workers."""
        # This would integrate with your infrastructure to add more workers
        logger.info("Scaling up workers")
        # Implementation depends on your deployment environment

    async def _scale_down(self):
        """Scale down workers."""
        # Remove idle workers
        idle_workers = [
            w
            for w in self.workers.values()
            if w.status == WorkerStatus.IDLE and w.current_load == 0
        ]

        if idle_workers and len(self.workers) > 1:
            # Remove the most idle worker
            worker_to_remove = max(
                idle_workers,
                key=lambda w: (datetime.utcnow() - w.last_activity).total_seconds(),
            )
            await self.remove_worker(worker_to_remove.id)

    async def remove_worker(self, worker_id: str) -> bool:
        """Remove worker from system."""
        async with self._lock:
            if worker_id not in self.workers:
                return False

            worker = self.workers[worker_id]

            # Don't remove if worker has active requests
            if worker.current_load > 0:
                logger.warning(f"Cannot remove worker {worker_id}: has active requests")
                return False

            del self.workers[worker_id]
            del self.worker_assignments[worker_id]
            self.stats["total_workers"] -= 1

            logger.info(f"Removed worker {worker_id}")
            return True

    async def _update_metrics(self):
        """Background task to update system metrics."""
        while self._running:
            try:
                async with self._lock:
                    # Update active workers count
                    self.stats["active_workers"] = sum(
                        1
                        for w in self.workers.values()
                        if w.status == WorkerStatus.BUSY
                    )

                    # Calculate average queue wait time
                    if self.queues:
                        wait_times = [
                            queue.metrics.avg_wait_time
                            for queue in self.queues.values()
                        ]
                        self.stats["avg_queue_wait_time"] = (
                            np.mean(wait_times) if wait_times else 0
                        )

                    # Calculate system throughput
                    total_processed = sum(
                        queue.metrics.completed_requests
                        for queue in self.queues.values()
                    )
                    self.stats["system_throughput"] = total_processed / 3600  # per hour

                await asyncio.sleep(60)  # Update every minute

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error updating metrics: {e}")
                await asyncio.sleep(60)

    async def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        async with self._lock:
            queue_stats = {}
            for queue_id, queue in self.queues.items():
                queue_stats[queue_id] = await queue.get_stats()

            worker_stats = {
                worker_id: worker.to_dict()
                for worker_id, worker in self.workers.items()
            }

            return {
                "manager_stats": self.stats,
                "queue_stats": queue_stats,
                "worker_stats": worker_stats,
                "load_balancer_stats": self.load_balancer.get_stats(),
            }


class LoadBalancer:
    """Load balancer for distributing requests across workers."""

    def __init__(self):
        self.strategy = "least_loaded"  # Options: round_robin, least_loaded, weighted
        self.round_robin_counter = 0

    def select_worker(self, workers: List[WorkerInfo]) -> Optional[WorkerInfo]:
        """Select best worker for request."""
        if not workers:
            return None

        if self.strategy == "round_robin":
            worker = workers[self.round_robin_counter % len(workers)]
            self.round_robin_counter += 1
            return worker

        elif self.strategy == "least_loaded":
            return min(workers, key=lambda w: w.get_load_percentage())

        elif self.strategy == "weighted":
            # Weight by health score and availability
            weights = [
                w.health_score * (1 - w.get_load_percentage() / 100) for w in workers
            ]
            total_weight = sum(weights)
            if total_weight > 0:
                probabilities = [w / total_weight for w in weights]
                selected_idx = np.random.choice(len(workers), p=probabilities)
                return workers[selected_idx]

        return workers[0]

    def get_stats(self) -> Dict[str, Any]:
        """Get load balancer statistics."""
        return {
            "strategy": self.strategy,
            "round_robin_counter": self.round_robin_counter,
        }


# Global queue manager
_queue_manager: Optional[InferenceQueueManager] = None


async def get_queue_manager() -> InferenceQueueManager:
    """Get or create global queue manager."""
    global _queue_manager
    if _queue_manager is None:
        _queue_manager = InferenceQueueManager()
        await _queue_manager.start()
    return _queue_manager


async def shutdown_queue_manager():
    """Shutdown queue manager."""
    global _queue_manager
    if _queue_manager:
        await _queue_manager.stop()
        _queue_manager = None
