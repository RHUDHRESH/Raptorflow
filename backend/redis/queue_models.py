"""
Queue data models for Redis-based job queue system.
"""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class JobStatus(Enum):
    """Job status enumeration."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class JobPriority(Enum):
    """Job priority levels."""

    LOW = 1
    NORMAL = 3
    HIGH = 5
    CRITICAL = 10


@dataclass
class JobResult:
    """Result of a job execution."""

    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    execution_time_ms: Optional[int] = None
    retry_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        return data


@dataclass
class Job:
    """Background job representation."""

    job_id: str
    queue_name: str
    job_type: str
    payload: Dict[str, Any]

    # Priority and scheduling
    priority: int = JobPriority.NORMAL.value
    delay_until: Optional[datetime] = None
    max_retries: int = 3
    timeout_seconds: int = 300

    # Status tracking
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Execution context
    worker_id: Optional[str] = None
    attempt_count: int = 0
    last_error: Optional[str] = None

    # Result
    result: Optional[JobResult] = None

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Post-initialization processing."""
        # Convert string timestamps to datetime if needed
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.started_at, str):
            self.started_at = datetime.fromisoformat(self.started_at)
        if isinstance(self.completed_at, str):
            self.completed_at = datetime.fromisoformat(self.completed_at)
        if isinstance(self.delay_until, str):
            self.delay_until = datetime.fromisoformat(self.delay_until)

        # Ensure status is JobStatus enum
        if isinstance(self.status, str):
            self.status = JobStatus(self.status)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)

        # Convert datetime objects to ISO strings
        data["created_at"] = self.created_at.isoformat()
        if self.started_at:
            data["started_at"] = self.started_at.isoformat()
        if self.completed_at:
            data["completed_at"] = self.completed_at.isoformat()
        if self.delay_until:
            data["delay_until"] = self.delay_until.isoformat()

        # Convert enums to strings
        data["status"] = self.status.value

        # Convert result if present
        if self.result:
            data["result"] = self.result.to_dict()

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Job":
        """Create from dictionary."""
        return cls(**data)

    def is_ready(self) -> bool:
        """Check if job is ready for processing."""
        if self.status != JobStatus.PENDING:
            return False

        if self.delay_until and datetime.now() < self.delay_until:
            return False

        return True

    def can_retry(self) -> bool:
        """Check if job can be retried."""
        return self.status == JobStatus.FAILED and self.attempt_count < self.max_retries

    def mark_processing(self, worker_id: str):
        """Mark job as being processed."""
        self.status = JobStatus.PROCESSING
        self.started_at = datetime.now()
        self.worker_id = worker_id
        self.attempt_count += 1

    def mark_completed(self, result: JobResult):
        """Mark job as completed."""
        self.status = JobStatus.COMPLETED
        self.completed_at = datetime.now()
        self.result = result

    def mark_failed(self, error: str, error_details: Optional[Dict[str, Any]] = None):
        """Mark job as failed."""
        self.status = JobStatus.FAILED
        self.completed_at = datetime.now()
        self.last_error = error

        if error_details:
            self.result = JobResult(
                success=False, error=error, error_details=error_details
            )

    def mark_cancelled(self):
        """Mark job as cancelled."""
        self.status = JobStatus.CANCELLED
        self.completed_at = datetime.now()

    def get_age_seconds(self) -> int:
        """Get job age in seconds."""
        return int((datetime.now() - self.created_at).total_seconds())

    def get_runtime_seconds(self) -> Optional[int]:
        """Get job runtime in seconds."""
        if not self.started_at:
            return None

        end_time = self.completed_at or datetime.now()
        return int((end_time - self.started_at).total_seconds())

    def is_expired(self) -> bool:
        """Check if job has exceeded timeout."""
        if not self.started_at or self.status != JobStatus.PROCESSING:
            return False

        runtime = self.get_runtime_seconds()
        return runtime > self.timeout_seconds if runtime else False

    def get_summary(self) -> Dict[str, Any]:
        """Get job summary for debugging."""
        return {
            "job_id": self.job_id,
            "queue_name": self.queue_name,
            "job_type": self.job_type,
            "status": self.status.value,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "attempt_count": self.attempt_count,
            "max_retries": self.max_retries,
            "age_seconds": self.get_age_seconds(),
            "runtime_seconds": self.get_runtime_seconds(),
            "is_ready": self.is_ready(),
            "can_retry": self.can_retry(),
            "is_expired": self.is_expired(),
            "last_error": self.last_error,
        }


@dataclass
class QueueStats:
    """Queue statistics."""

    queue_name: str
    total_jobs: int
    pending_jobs: int
    processing_jobs: int
    completed_jobs: int
    failed_jobs: int
    cancelled_jobs: int

    # Performance metrics
    avg_runtime_seconds: float
    success_rate: float

    # Timestamps
    calculated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["calculated_at"] = self.calculated_at.isoformat()
        return data


@dataclass
class WorkerInfo:
    """Worker information."""

    worker_id: str
    queue_name: str
    status: str  # "active", "idle", "stopped"
    current_job_id: Optional[str] = None
    jobs_processed: int = 0
    last_activity: datetime = field(default_factory=datetime.now)
    started_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["last_activity"] = self.last_activity.isoformat()
        data["started_at"] = self.started_at.isoformat()
        return data
