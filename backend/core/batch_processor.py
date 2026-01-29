"""
AI Inference Batch Processor and Request Deduplicator
====================================================

Intelligent batch processing and request deduplication system for AI inference.
Optimizes LLM calls by grouping similar requests and preventing duplicate processing.

Features:
- Semantic request deduplication
- Batch processing with optimal grouping
- Request queuing and priority handling
- Similarity-based request merging
- Real-time request tracking
- Performance optimization
"""

import asyncio
import hashlib
import json
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import uuid

import numpy as np
import structlog
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from inference_cache import get_inference_cache

logger = structlog.get_logger(__name__)


class RequestStatus(str, Enum):
    """Request status types."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    MERGED = "merged"


class BatchStrategy(str, Enum):
    """Batch processing strategies."""

    SEMANTIC_SIMILARITY = "semantic_similarity"
    MODEL_SPECIFIC = "model_specific"
    PRIORITY_BASED = "priority_based"
    COST_OPTIMIZED = "cost_optimized"
    TIME_BASED = "time_based"


@dataclass
class InferenceRequest:
    """Individual inference request."""

    id: str
    prompt: str
    model_name: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    user_id: Optional[str] = None
    workspace_id: Optional[str] = None
    priority: int = 5  # 1-10, 10 being highest
    created_at: datetime = field(default_factory=datetime.utcnow)
    timeout_seconds: int = 300
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Deduplication fields
    semantic_hash: str = ""
    content_hash: str = ""
    similarity_threshold: float = 0.9

    # Batch processing fields
    batch_id: Optional[str] = None
    batch_position: int = 0

    # Response tracking
    response: Optional[Any] = None
    error: Optional[str] = None
    status: RequestStatus = RequestStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        """Initialize hashes after creation."""
        if not self.content_hash:
            self.content_hash = self._generate_content_hash()
        if not self.semantic_hash:
            self.semantic_hash = self._generate_semantic_hash()

    def _generate_content_hash(self) -> str:
        """Generate content-based hash for exact deduplication."""
        content = {
            "prompt": self.prompt,
            "model": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        content_str = json.dumps(content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()

    def _generate_semantic_hash(self) -> str:
        """Generate semantic hash for similarity matching."""
        normalized_prompt = self.prompt.lower().strip()
        return hashlib.md5(normalized_prompt.encode()).hexdigest()

    def is_expired(self) -> bool:
        """Check if request has expired."""
        if self.status in [
            RequestStatus.COMPLETED,
            RequestStatus.FAILED,
            RequestStatus.CANCELLED,
        ]:
            return False
        return datetime.utcnow() > self.created_at + timedelta(
            seconds=self.timeout_seconds
        )

    def get_processing_time(self) -> Optional[float]:
        """Get processing time in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "prompt": self.prompt,
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "user_id": self.user_id,
            "workspace_id": self.workspace_id,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "timeout_seconds": self.timeout_seconds,
            "metadata": self.metadata,
            "semantic_hash": self.semantic_hash,
            "content_hash": self.content_hash,
            "similarity_threshold": self.similarity_threshold,
            "batch_id": self.batch_id,
            "batch_position": self.batch_position,
            "response": self.response,
            "error": self.error,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
        }


@dataclass
class BatchRequest:
    """Batch of inference requests."""

    id: str
    requests: List[InferenceRequest]
    model_name: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    max_batch_size: int = 10
    processing_timeout: int = 600

    # Batch processing fields
    status: RequestStatus = RequestStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Response fields
    responses: List[Any] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Initialize batch after creation."""
        if not self.requests:
            raise ValueError("Batch must contain at least one request")

    @property
    def size(self) -> int:
        """Get batch size."""
        return len(self.requests)

    @property
    def is_full(self) -> bool:
        """Check if batch is full."""
        return len(self.requests) >= self.max_batch_size

    def add_request(self, request: InferenceRequest) -> bool:
        """Add request to batch."""
        if self.is_full:
            return False

        if request.model_name != self.model_name:
            return False

        request.batch_id = self.id
        request.batch_position = len(self.requests)
        self.requests.append(request)
        return True

    def get_processing_time(self) -> Optional[float]:
        """Get batch processing time."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "requests": [req.to_dict() for req in self.requests],
            "model_name": self.model_name,
            "created_at": self.created_at.isoformat(),
            "max_batch_size": self.max_batch_size,
            "processing_timeout": self.processing_timeout,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "responses": self.responses,
            "errors": self.errors,
        }


class RequestDeduplicator:
    """Intelligent request deduplication system."""

    def __init__(
        self,
        similarity_threshold: float = 0.9,
        deduplication_window: int = 300,  # 5 minutes
        max_pending_requests: int = 1000,
    ):
        self.similarity_threshold = similarity_threshold
        self.deduplication_window = deduplication_window
        self.max_pending_requests = max_pending_requests

        # Request tracking
        self.pending_requests: Dict[str, InferenceRequest] = {}
        self.processing_requests: Dict[str, InferenceRequest] = {}
        self.completed_requests: Dict[str, InferenceRequest] = {}

        # Deduplication indexes
        self.content_hash_index: Dict[str, Set[str]] = defaultdict(
            set
        )  # content_hash -> request_ids
        self.semantic_hash_index: Dict[str, Set[str]] = defaultdict(
            set
        )  # semantic_hash -> request_ids

        # Similarity matching
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words="english")
        self.prompt_vectors: Dict[str, np.ndarray] = {}

        # Lock for thread safety
        self._lock = asyncio.Lock()

        # Statistics
        self.stats = {
            "total_requests": 0,
            "exact_duplicates": 0,
            "semantic_duplicates": 0,
            "unique_requests": 0,
            "deduplication_rate": 0.0,
        }

    async def add_request(
        self, request: InferenceRequest
    ) -> Tuple[bool, Optional[InferenceRequest]]:
        """Add request and check for duplicates."""
        async with self._lock:
            self.stats["total_requests"] += 1

            # Check exact duplicates first
            exact_duplicate = await self._find_exact_duplicate(request)
            if exact_duplicate:
                self.stats["exact_duplicates"] += 1
                logger.info(
                    f"Found exact duplicate for request {request.id}: {exact_duplicate.id}"
                )
                return False, exact_duplicate

            # Check semantic duplicates
            semantic_duplicate = await self._find_semantic_duplicate(request)
            if semantic_duplicate:
                self.stats["semantic_duplicates"] += 1
                logger.info(
                    f"Found semantic duplicate for request {request.id}: {semantic_duplicate.id}"
                )
                return False, semantic_duplicate

            # Add as unique request
            await self._add_unique_request(request)
            self.stats["unique_requests"] += 1

            # Update deduplication rate
            total_duplicates = (
                self.stats["exact_duplicates"] + self.stats["semantic_duplicates"]
            )
            self.stats["deduplication_rate"] = (
                total_duplicates / self.stats["total_requests"]
            )

            return True, None

    async def _find_exact_duplicate(
        self, request: InferenceRequest
    ) -> Optional[InferenceRequest]:
        """Find exact duplicate by content hash."""
        duplicate_ids = self.content_hash_index.get(request.content_hash, set())

        for req_id in duplicate_ids:
            if req_id in self.pending_requests:
                duplicate = self.pending_requests[req_id]
                if not duplicate.is_expired():
                    return duplicate

        return None

    async def _find_semantic_duplicate(
        self, request: InferenceRequest
    ) -> Optional[InferenceRequest]:
        """Find semantic duplicate by similarity."""
        similar_ids = self.semantic_hash_index.get(request.semantic_hash, set())

        for req_id in similar_ids:
            if req_id in self.pending_requests:
                similar_request = self.pending_requests[req_id]
                if not similar_request.is_expired():
                    # Calculate actual similarity
                    similarity = await self._calculate_similarity(
                        request.prompt, similar_request.prompt
                    )
                    if similarity >= request.similarity_threshold:
                        return similar_request

        return None

    async def _calculate_similarity(self, prompt1: str, prompt2: str) -> float:
        """Calculate semantic similarity between prompts."""
        try:
            # Use TF-IDF vectorization for similarity
            corpus = [prompt1, prompt2]
            tfidf_matrix = self.vectorizer.fit_transform(corpus)
            similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            return float(similarity_matrix[0][0])
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0

    async def _add_unique_request(self, request: InferenceRequest):
        """Add unique request to tracking."""
        # Check capacity
        if len(self.pending_requests) >= self.max_pending_requests:
            await self._cleanup_expired_requests()

        # Add to tracking
        self.pending_requests[request.id] = request

        # Update indexes
        self.content_hash_index[request.content_hash].add(request.id)
        self.semantic_hash_index[request.semantic_hash].add(request.id)

        # Update prompt vectors for similarity matching
        try:
            vector = self.vectorizer.fit_transform([request.prompt]).toarray()[0]
            self.prompt_vectors[request.id] = vector
        except Exception as e:
            logger.error(f"Error creating prompt vector: {e}")

    async def _cleanup_expired_requests(self):
        """Clean up expired requests."""
        current_time = datetime.utcnow()
        expired_requests = []

        for req_id, request in self.pending_requests.items():
            if request.is_expired():
                expired_requests.append(req_id)

        for req_id in expired_requests:
            await self._remove_request(req_id)
            logger.debug(f"Removed expired request: {req_id}")

    async def _remove_request(self, request_id: str):
        """Remove request from tracking."""
        if request_id in self.pending_requests:
            request = self.pending_requests[request_id]

            # Remove from indexes
            self.content_hash_index[request.content_hash].discard(request_id)
            self.semantic_hash_index[request.semantic_hash].discard(request_id)

            # Remove from tracking
            del self.pending_requests[request_id]

            # Clean up prompt vectors
            if request_id in self.prompt_vectors:
                del self.prompt_vectors[request_id]

    async def mark_processing(self, request_id: str):
        """Mark request as processing."""
        async with self._lock:
            if request_id in self.pending_requests:
                request = self.pending_requests[request_id]
                request.status = RequestStatus.PROCESSING
                request.started_at = datetime.utcnow()

                # Move to processing
                self.processing_requests[request_id] = request
                del self.pending_requests[request_id]

    async def mark_completed(
        self, request_id: str, response: Any, error: Optional[str] = None
    ):
        """Mark request as completed."""
        async with self._lock:
            if request_id in self.processing_requests:
                request = self.processing_requests[request_id]
                request.completed_at = datetime.utcnow()
                request.response = response
                request.error = error
                request.status = (
                    RequestStatus.COMPLETED if error is None else RequestStatus.FAILED
                )

                # Move to completed
                self.completed_requests[request_id] = request
                del self.processing_requests[request_id]

                # Remove from indexes
                self.content_hash_index[request.content_hash].discard(request_id)
                self.semantic_hash_index[request.semantic_hash].discard(request_id)

                # Clean up prompt vectors
                if request_id in self.prompt_vectors:
                    del self.prompt_vectors[request_id]

    async def get_request(self, request_id: str) -> Optional[InferenceRequest]:
        """Get request by ID."""
        async with self._lock:
            return (
                self.pending_requests.get(request_id)
                or self.processing_requests.get(request_id)
                or self.completed_requests.get(request_id)
            )

    async def get_pending_requests(
        self, model_name: Optional[str] = None
    ) -> List[InferenceRequest]:
        """Get pending requests, optionally filtered by model."""
        async with self._lock:
            requests = list(self.pending_requests.values())
            if model_name:
                requests = [req for req in requests if req.model_name == model_name]

            # Sort by priority (higher first) and creation time (earlier first)
            requests.sort(key=lambda x: (-x.priority, x.created_at))
            return requests

    async def get_stats(self) -> Dict[str, Any]:
        """Get deduplication statistics."""
        async with self._lock:
            return {
                **self.stats,
                "pending_requests": len(self.pending_requests),
                "processing_requests": len(self.processing_requests),
                "completed_requests": len(self.completed_requests),
                "content_hash_index_size": len(self.content_hash_index),
                "semantic_hash_index_size": len(self.semantic_hash_index),
                "prompt_vectors_size": len(self.prompt_vectors),
            }


class BatchProcessor:
    """Intelligent batch processing system."""

    def __init__(
        self,
        deduplicator: RequestDeduplicator,
        max_batch_size: int = 10,
        batch_timeout: int = 30,  # seconds
        strategy: BatchStrategy = BatchStrategy.SEMANTIC_SIMILARITY,
    ):
        self.deduplicator = deduplicator
        self.max_batch_size = max_batch_size
        self.batch_timeout = batch_timeout
        self.strategy = strategy

        # Batch management
        self.pending_batches: Dict[str, BatchRequest] = {}
        self.processing_batches: Dict[str, BatchRequest] = {}
        self.completed_batches: Dict[str, BatchRequest] = {}

        # Batch queues by model
        self.model_queues: Dict[str, deque] = defaultdict(deque)

        # Lock for thread safety
        self._lock = asyncio.Lock()

        # Statistics
        self.stats = {
            "total_batches": 0,
            "successful_batches": 0,
            "failed_batches": 0,
            "average_batch_size": 0.0,
            "total_requests_processed": 0,
            "batch_efficiency": 0.0,
        }

        # Background processing
        self._processing_task = None
        self._running = False

    async def start(self):
        """Start batch processing."""
        if self._running:
            return

        self._running = True
        self._processing_task = asyncio.create_task(self._process_batches())
        logger.info("Batch processor started")

    async def stop(self):
        """Stop batch processing."""
        self._running = False
        if self._processing_task:
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass
        logger.info("Batch processor stopped")

    async def add_request(
        self, request: InferenceRequest
    ) -> Tuple[bool, Optional[str]]:
        """Add request to batch processing."""
        # Check for duplicates first
        is_unique, duplicate = await self.deduplicator.add_request(request)

        if not is_unique and duplicate:
            # Request is a duplicate, attach to existing request
            return False, duplicate.id

        # Add to model queue
        async with self._lock:
            self.model_queues[request.model_name].append(request)

        logger.debug(f"Added request {request.id} to batch processing")
        return True, request.id

    async def _process_batches(self):
        """Background batch processing loop."""
        while self._running:
            try:
                await self._create_batches()
                await self._process_ready_batches()
                await asyncio.sleep(1)  # Process every second
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in batch processing: {e}")
                await asyncio.sleep(5)

    async def _create_batches(self):
        """Create batches from queued requests."""
        async with self._lock:
            for model_name, queue in self.model_queues.items():
                if not queue:
                    continue

                # Get requests for batching
                requests_to_batch = []

                while queue and len(requests_to_batch) < self.max_batch_size:
                    request = queue.popleft()

                    # Check if request is still valid
                    if request.is_expired():
                        await self.deduplicator._remove_request(request.id)
                        continue

                    requests_to_batch.append(request)

                if (
                    len(requests_to_batch) >= 2
                ):  # Only batch if we have multiple requests
                    await self._create_batch(requests_to_batch)
                elif len(requests_to_batch) == 1:
                    # Single request goes back to queue for individual processing
                    queue.appendleft(requests_to_batch[0])

    async def _create_batch(self, requests: List[InferenceRequest]):
        """Create a batch from requests."""
        batch_id = str(uuid.uuid4())
        model_name = requests[0].model_name

        batch = BatchRequest(
            id=batch_id,
            requests=requests,
            model_name=model_name,
            max_batch_size=self.max_batch_size,
        )

        self.pending_batches[batch_id] = batch
        self.stats["total_batches"] += 1

        logger.debug(f"Created batch {batch_id} with {len(requests)} requests")

    async def _process_ready_batches(self):
        """Process batches that are ready."""
        current_time = datetime.utcnow()
        ready_batches = []

        async with self._lock:
            for batch_id, batch in self.pending_batches.items():
                # Check if batch is ready (timeout or full)
                time_since_creation = (current_time - batch.created_at).total_seconds()
                if batch.is_full or time_since_creation >= self.batch_timeout:
                    ready_batches.append(batch)

        # Process ready batches
        for batch in ready_batches:
            await self._process_batch(batch)

    async def _process_batch(self, batch: BatchRequest):
        """Process a single batch."""
        async with self._lock:
            if batch.id in self.pending_batches:
                del self.pending_batches[batch.id]

            batch.status = RequestStatus.PROCESSING
            batch.started_at = datetime.utcnow()
            self.processing_batches[batch.id] = batch

        try:
            # Mark all requests as processing
            for request in batch.requests:
                await self.deduplicator.mark_processing(request.id)

            # Process the batch (this would be implemented by the calling service)
            logger.info(f"Processing batch {batch.id} with {batch.size} requests")

            # The actual processing would be handled by the inference service
            # For now, we'll just mark it as completed
            await self._complete_batch(batch, success=True)

        except Exception as e:
            logger.error(f"Error processing batch {batch.id}: {e}")
            await self._complete_batch(batch, success=False, error=str(e))

    async def _complete_batch(
        self, batch: BatchRequest, success: bool, error: Optional[str] = None
    ):
        """Complete batch processing."""
        async with self._lock:
            batch.completed_at = datetime.utcnow()
            batch.status = RequestStatus.COMPLETED if success else RequestStatus.FAILED

            if batch.id in self.processing_batches:
                del self.processing_batches[batch.id]

            self.completed_batches[batch.id] = batch

            # Update statistics
            if success:
                self.stats["successful_batches"] += 1
            else:
                self.stats["failed_batches"] += 1

            self.stats["total_requests_processed"] += batch.size

            # Update average batch size
            total_batches = self.stats["total_batches"]
            if total_batches > 0:
                self.stats["average_batch_size"] = (
                    self.stats["total_requests_processed"] / total_batches
                )

            # Calculate batch efficiency (requests per batch)
            if self.stats["successful_batches"] > 0:
                self.stats["batch_efficiency"] = (
                    self.stats["total_requests_processed"]
                    / self.stats["successful_batches"]
                )

            # Mark individual requests as completed
            for i, request in enumerate(batch.requests):
                response = batch.responses[i] if i < len(batch.responses) else None
                req_error = batch.errors[i] if i < len(batch.errors) else error
                await self.deduplicator.mark_completed(request.id, response, req_error)

    async def get_batch(self, batch_id: str) -> Optional[BatchRequest]:
        """Get batch by ID."""
        async with self._lock:
            return (
                self.pending_batches.get(batch_id)
                or self.processing_batches.get(batch_id)
                or self.completed_batches.get(batch_id)
            )

    async def get_stats(self) -> Dict[str, Any]:
        """Get batch processing statistics."""
        async with self._lock:
            dedup_stats = await self.deduplicator.get_stats()

            return {
                "batch_processor": {
                    **self.stats,
                    "pending_batches": len(self.pending_batches),
                    "processing_batches": len(self.processing_batches),
                    "completed_batches": len(self.completed_batches),
                    "model_queues": {
                        model: len(queue) for model, queue in self.model_queues.items()
                    },
                },
                "deduplicator": dedup_stats,
            }


# Global instances
_request_deduplicator: Optional[RequestDeduplicator] = None
_batch_processor: Optional[BatchProcessor] = None


async def get_request_deduplicator() -> RequestDeduplicator:
    """Get or create global request deduplicator."""
    global _request_deduplicator
    if _request_deduplicator is None:
        _request_deduplicator = RequestDeduplicator()
    return _request_deduplicator


async def get_batch_processor() -> BatchProcessor:
    """Get or create global batch processor."""
    global _batch_processor
    if _batch_processor is None:
        deduplicator = await get_request_deduplicator()
        _batch_processor = BatchProcessor(deduplicator)
        await _batch_processor.start()
    return _batch_processor


async def shutdown_batch_processor():
    """Shutdown batch processor."""
    global _batch_processor
    if _batch_processor:
        await _batch_processor.stop()
        _batch_processor = None
