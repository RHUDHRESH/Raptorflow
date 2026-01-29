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


class JobPriority(Enum):
    """Job priority enumeration."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class JobResult:
    """Job execution result."""

    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    worker_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JobResult":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class Job:
    """Job data model."""

    job_id: str
    queue_name: str
    job_type: str
    payload: Dict[str, Any]
    priority: int = JobPriority.NORMAL.value
    status: JobStatus = JobStatus.PENDING
    delay_until: Optional[datetime] = None
    max_retries: int = 3
    retry_count: int = 0
    timeout_seconds: int = 300
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    worker_id: Optional[str] = None
    result: Optional[JobResult] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_ready(self) -> bool:
        """Check if job is ready for processing."""
        if self.status not in [JobStatus.PENDING, JobStatus.FAILED]:
            return False

        if self.delay_until and self.delay_until > datetime.now():
            return False

        return True

    def can_retry(self) -> bool:
        """Check if job can be retried."""
        return self.status == JobStatus.FAILED and self.retry_count < self.max_retries

    def mark_processing(self, worker_id: str):
        """Mark job as being processed."""
        self.status = JobStatus.PROCESSING
        self.worker_id = worker_id
        self.started_at = datetime.now()

    def mark_completed(self, result: JobResult):
        """Mark job as completed."""
        self.status = JobStatus.COMPLETED
        self.result = result
        self.completed_at = datetime.now()

    def mark_failed(
        self, error: str, error_details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Mark job as failed and return if it should be retried."""
        self.status = JobStatus.FAILED
        self.error = error
        self.retry_count += 1
        self.completed_at = datetime.now()

        if error_details:
            self.metadata.update(error_details)

        return self.can_retry()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)

        # Convert datetime objects to ISO strings
        if self.delay_until:
            data["delay_until"] = self.delay_until.isoformat()
        if self.created_at:
            data["created_at"] = self.created_at.isoformat()
        if self.started_at:
            data["started_at"] = self.started_at.isoformat()
        if self.completed_at:
            data["completed_at"] = self.completed_at.isoformat()

        # Convert enums to strings
        data["status"] = self.status.value

        # Convert result to dict if present
        if self.result:
            data["result"] = self.result.to_dict()

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Job":
        """Create job from dictionary."""
        # Convert ISO strings back to datetime objects
        if data.get("delay_until"):
            data["delay_until"] = datetime.fromisoformat(
                data["delay_until"].replace("Z", "+00:00")
            )
        if data.get("created_at"):
            data["created_at"] = datetime.fromisoformat(
                data["created_at"].replace("Z", "+00:00")
            )
        if data.get("started_at"):
            data["started_at"] = datetime.fromisoformat(
                data["started_at"].replace("Z", "+00:00")
            )
        if data.get("completed_at"):
            data["completed_at"] = datetime.fromisoformat(
                data["completed_at"].replace("Z", "+00:00")
            )

        # Convert status string back to enum
        if isinstance(data.get("status"), str):
            data["status"] = JobStatus(data["status"])

        # Convert result dict back to JobResult
        if data.get("result"):
            data["result"] = JobResult.from_dict(data["result"])

        return cls(**data)


@dataclass
class QueueStats:
    """Queue statistics."""

    queue_name: str
    pending_jobs: int = 0
    processing_jobs: int = 0
    completed_jobs: int = 0
    failed_jobs: int = 0
    total_jobs: int = 0
    avg_processing_time: float = 0.0
    last_activity: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        if self.last_activity:
            data["last_activity"] = self.last_activity.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QueueStats":
        """Create from dictionary."""
        if data.get("last_activity"):
            data["last_activity"] = datetime.fromisoformat(
                data["last_activity"].replace("Z", "+00:00")
            )
        return cls(**data)


@dataclass
class WorkerInfo:
    """Worker information."""

    worker_id: str
    queue_name: str
    status: str = "active"
    completed_jobs: int = 0
    failed_jobs: int = 0
    current_job_id: Optional[str] = None
    last_activity: datetime = field(default_factory=datetime.now)
    started_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["last_activity"] = self.last_activity.isoformat()
        data["started_at"] = self.started_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkerInfo":
        """Create from dictionary."""
        if data.get("last_activity"):
            data["last_activity"] = datetime.fromisoformat(
                data["last_activity"].replace("Z", "+00:00")
            )
        if data.get("started_at"):
            data["started_at"] = datetime.fromisoformat(
                data["started_at"].replace("Z", "+00:00")
            )
        return cls(**data)
