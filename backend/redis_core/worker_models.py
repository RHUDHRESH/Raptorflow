"""
Worker models for Redis-based background job processing.

Provides data structures for worker state management, job execution,
and worker coordination.
"""

import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


class WorkerStatus(Enum):
    """Worker status enumeration."""

    IDLE = "idle"
    BUSY = "busy"
    PROCESSING = "processing"
    ERROR = "error"
    STOPPED = "stopped"
    STARTING = "starting"
    SHUTTING_DOWN = "shutting_down"


class WorkerType(Enum):
    """Worker type enumeration."""

    AGENT_PROCESSOR = os.getenv("AGENT_PROCESSOR")
    WEBHOOK_PROCESSOR = os.getenv("AGENT_PROCESSOR")
    USAGE_AGGREGATOR = os.getenv("AGENT_PROCESSOR")
    SESSION_CLEANER = os.getenv("AGENT_PROCESSOR")
    CACHE_INVALIDATOR = os.getenv("AGENT_PROCESSOR")
    NOTIFICATION_SENDER = os.getenv("AGENT_PROCESSOR")
    REPORT_GENERATOR = os.getenv("AGENT_PROCESSOR")
    DATA_EXPORTER = "data_exporter"
    BACKUP_WORKER = "backup_worker"
    HEALTH_CHECKER = "health_checker"


@dataclass
class WorkerMetrics:
    """Worker performance metrics."""

    worker_id: str
    jobs_processed: int = 0
    jobs_failed: int = 0
    jobs_completed: int = 0
    avg_processing_time_ms: float = 0.0
    total_processing_time_ms: float = 0.0
    last_job_completed_at: Optional[datetime] = None
    last_job_failed_at: Optional[datetime] = None
    error_rate: float = 0.0
    throughput_per_hour: float = 0.0

    # Resource usage metrics
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    network_io_mb: float = 0.0

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)
        if isinstance(self.last_job_completed_at, str):
            self.last_job_completed_at = datetime.fromisoformat(
                self.last_job_completed_at
            )
        if isinstance(self.last_job_failed_at, str):
            self.last_job_failed_at = datetime.fromisoformat(self.last_job_failed_at)

        # Calculate derived metrics
        self._calculate_metrics()

    def _calculate_metrics(self):
        """Calculate derived metrics."""
        total_jobs = self.jobs_processed
        if total_jobs > 0:
            self.error_rate = (self.jobs_failed / total_jobs) * 100
            self.avg_processing_time_ms = self.total_processing_time_ms / total_jobs

        # Calculate throughput (jobs per hour)
        if self.last_job_completed_at:
            time_diff = datetime.now() - self.last_job_completed_at
            hours = max(
                time_diff.total_seconds() / 3600, 0.001
            )  # Avoid division by zero
            self.throughput_per_hour = self.jobs_completed / hours

    def record_job_completed(self, processing_time_ms: float):
        """Record a completed job."""
        self.jobs_processed += 1
        self.jobs_completed += 1
        self.total_processing_time_ms += processing_time_ms
        self.last_job_completed_at = datetime.now()
        self.updated_at = datetime.now()
        self._calculate_metrics()

    def record_job_failed(self):
        """Record a failed job."""
        self.jobs_processed += 1
        self.jobs_failed += 1
        self.last_job_failed_at = datetime.now()
        self.updated_at = datetime.now()
        self._calculate_metrics()

    def update_resource_usage(
        self, cpu_percent: float, memory_mb: float, network_mb: float
    ):
        """Update resource usage metrics."""
        self.cpu_usage_percent = cpu_percent
        self.memory_usage_mb = memory_mb
        self.network_io_mb = network_mb
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)

        # Convert datetime objects to ISO strings
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        if self.last_job_completed_at:
            data["last_job_completed_at"] = self.last_job_completed_at.isoformat()
        if self.last_job_failed_at:
            data["last_job_failed_at"] = self.last_job_failed_at.isoformat()

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkerMetrics":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class WorkerState:
    """Worker state information."""

    worker_id: str
    worker_type: WorkerType
    status: WorkerStatus
    queue_name: str
    current_job_id: Optional[str] = None
    last_heartbeat: datetime = field(default_factory=datetime.now)
    started_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)

    # Worker configuration
    max_concurrent_jobs: int = 1
    job_timeout_seconds: int = 300
    retry_attempts: int = 3
    retry_delay_seconds: int = 60

    # Worker metadata
    hostname: str = ""
    pid: int = 0
    version: str = "1.0.0"
    capabilities: List[str] = field(default_factory=list)

    # Error handling
    last_error: Optional[str] = None
    error_count: int = 0
    consecutive_failures: int = 0

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.worker_type, str):
            self.worker_type = WorkerType(self.worker_type)
        if isinstance(self.status, str):
            self.status = WorkerStatus(self.status)
        if isinstance(self.started_at, str):
            self.started_at = datetime.fromisoformat(self.started_at)
        if isinstance(self.last_heartbeat, str):
            self.last_heartbeat = datetime.fromisoformat(self.last_heartbeat)
        if isinstance(self.last_activity, str):
            self.last_activity = datetime.fromisoformat(self.last_activity)

    def is_alive(self, timeout_seconds: int = 60) -> bool:
        """Check if worker is alive based on heartbeat."""
        time_diff = datetime.now() - self.last_heartbeat
        return time_diff.total_seconds() < timeout_seconds

    def is_healthy(self) -> bool:
        """Check if worker is healthy."""
        return (
            self.status != WorkerStatus.ERROR
            and self.status != WorkerStatus.STOPPED
            and self.consecutive_failures < 5
            and self.is_alive()
        )

    def can_process_job(self) -> bool:
        """Check if worker can process a new job."""
        return (
            self.status in [WorkerStatus.IDLE, WorkerStatus.BUSY]
            and self.is_healthy()
            and (self.current_job_id is None or self.max_concurrent_jobs > 1)
        )

    def update_heartbeat(self):
        """Update worker heartbeat."""
        self.last_heartbeat = datetime.now()
        self.last_activity = datetime.now()

    def set_status(self, status: WorkerStatus, error: Optional[str] = None):
        """Set worker status."""
        self.status = status
        self.last_activity = datetime.now()

        if status == WorkerStatus.ERROR:
            self.last_error = error
            self.error_count += 1
            self.consecutive_failures += 1
        elif status != WorkerStatus.ERROR:
            self.consecutive_failures = 0

    def assign_job(self, job_id: str):
        """Assign a job to the worker."""
        self.current_job_id = job_id
        self.status = WorkerStatus.PROCESSING
        self.last_activity = datetime.now()

    def complete_job(self):
        """Mark current job as completed."""
        self.current_job_id = None
        self.status = WorkerStatus.IDLE
        self.last_activity = datetime.now()
        self.consecutive_failures = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)

        # Convert enums to strings
        data["worker_type"] = self.worker_type.value
        data["status"] = self.status.value

        # Convert datetime objects to ISO strings
        data["started_at"] = self.started_at.isoformat()
        data["last_heartbeat"] = self.last_heartbeat.isoformat()
        data["last_activity"] = self.last_activity.isoformat()

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkerState":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class WorkerPool:
    """Worker pool management."""

    pool_name: str
    worker_type: WorkerType
    workers: Dict[str, WorkerState] = field(default_factory=dict)
    total_capacity: int = 0
    active_workers: int = 0
    idle_workers: int = 0

    # Pool configuration
    min_workers: int = 1
    max_workers: int = 10
    auto_scale: bool = True
    scale_up_threshold: float = 0.8  # 80% utilization
    scale_down_threshold: float = 0.2  # 20% utilization

    # Pool metrics
    jobs_processed_total: int = 0
    jobs_failed_total: int = 0
    avg_throughput: float = 0.0

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.worker_type, str):
            self.worker_type = WorkerType(self.worker_type)
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)

        self._update_metrics()

    def add_worker(self, worker: WorkerState):
        """Add a worker to the pool."""
        self.workers[worker.worker_id] = worker
        self.total_capacity = len(self.workers)
        self._update_metrics()
        self.updated_at = datetime.now()

    def remove_worker(self, worker_id: str):
        """Remove a worker from the pool."""
        if worker_id in self.workers:
            del self.workers[worker_id]
            self.total_capacity = len(self.workers)
            self._update_metrics()
            self.updated_at = datetime.now()

    def get_available_workers(self) -> List[WorkerState]:
        """Get list of available workers."""
        return [worker for worker in self.workers.values() if worker.can_process_job()]

    def get_healthy_workers(self) -> List[WorkerState]:
        """Get list of healthy workers."""
        return [worker for worker in self.workers.values() if worker.is_healthy()]

    def _update_metrics(self):
        """Update pool metrics."""
        self.active_workers = len(
            [
                worker
                for worker in self.workers.values()
                if worker.status in [WorkerStatus.BUSY, WorkerStatus.PROCESSING]
            ]
        )

        self.idle_workers = len(
            [
                worker
                for worker in self.workers.values()
                if worker.status == WorkerStatus.IDLE
            ]
        )

        # Calculate total metrics
        total_processed = sum(worker.jobs_processed for worker in self.workers.values())
        total_failed = sum(worker.jobs_failed for worker in self.workers.values())

        self.jobs_processed_total = total_processed
        self.jobs_failed_total = total_failed

        # Calculate average throughput
        if self.workers:
            self.avg_throughput = sum(
                worker.throughput_per_hour for worker in self.workers.values()
            ) / len(self.workers)

    def should_scale_up(self) -> bool:
        """Check if pool should scale up."""
        if not self.auto_scale or self.total_capacity >= self.max_workers:
            return False

        utilization = self.active_workers / max(self.total_capacity, 1)
        return utilization >= self.scale_up_threshold

    def should_scale_down(self) -> bool:
        """Check if pool should scale down."""
        if not self.auto_scale or self.total_capacity <= self.min_workers:
            return False

        utilization = self.active_workers / max(self.total_capacity, 1)
        return utilization <= self.scale_down_threshold

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)

        # Convert worker_type enum
        data["worker_type"] = self.worker_type.value

        # Convert datetime objects
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()

        # Convert workers dict
        data["workers"] = {
            worker_id: worker.to_dict() for worker_id, worker in self.workers.items()
        }

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkerPool":
        """Create from dictionary."""
        # Convert workers dict
        if "workers" in data:
            workers = {
                worker_id: WorkerState.from_dict(worker_data)
                for worker_id, worker_data in data["workers"].items()
            }
            data["workers"] = workers

        return cls(**data)


@dataclass
class WorkerRegistry:
    """Global worker registry."""

    workers: Dict[str, WorkerState] = field(default_factory=dict)
    pools: Dict[str, WorkerPool] = field(default_factory=dict)

    # Registry metrics
    total_workers: int = 0
    active_workers: int = 0
    idle_workers: int = 0
    error_workers: int = 0

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)

        self._update_metrics()

    def register_worker(self, worker: WorkerState):
        """Register a new worker."""
        self.workers[worker.worker_id] = worker
        self._update_metrics()
        self.updated_at = datetime.now()

    def unregister_worker(self, worker_id: str):
        """Unregister a worker."""
        if worker_id in self.workers:
            del self.workers[worker_id]
            self._update_metrics()
            self.updated_at = datetime.now()

    def get_worker(self, worker_id: str) -> Optional[WorkerState]:
        """Get worker by ID."""
        return self.workers.get(worker_id)

    def get_workers_by_type(self, worker_type: WorkerType) -> List[WorkerState]:
        """Get workers by type."""
        return [
            worker
            for worker in self.workers.values()
            if worker.worker_type == worker_type
        ]

    def get_workers_by_status(self, status: WorkerStatus) -> List[WorkerState]:
        """Get workers by status."""
        return [worker for worker in self.workers.values() if worker.status == status]

    def _update_metrics(self):
        """Update registry metrics."""
        self.total_workers = len(self.workers)
        self.active_workers = len(
            [
                worker
                for worker in self.workers.values()
                if worker.status in [WorkerStatus.BUSY, WorkerStatus.PROCESSING]
            ]
        )
        self.idle_workers = len(
            [
                worker
                for worker in self.workers.values()
                if worker.status == WorkerStatus.IDLE
            ]
        )
        self.error_workers = len(
            [
                worker
                for worker in self.workers.values()
                if worker.status == WorkerStatus.ERROR
            ]
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)

        # Convert datetime objects
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()

        # Convert workers and pools
        data["workers"] = {
            worker_id: worker.to_dict() for worker_id, worker in self.workers.items()
        }

        data["pools"] = {
            pool_name: pool.to_dict() for pool_name, pool in self.pools.items()
        }

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkerRegistry":
        """Create from dictionary."""
        # Convert workers and pools
        if "workers" in data:
            workers = {
                worker_id: WorkerState.from_dict(worker_data)
                for worker_id, worker_data in data["workers"].items()
            }
            data["workers"] = workers

        if "pools" in data:
            pools = {
                pool_name: WorkerPool.from_dict(pool_data)
                for pool_name, pool_data in data["pools"].items()
            }
            data["pools"] = pools

        return cls(**data)
