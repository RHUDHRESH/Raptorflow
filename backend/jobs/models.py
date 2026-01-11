"""
Job models for Raptorflow background jobs.

Defines data structures for job results, status,
and execution tracking.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class JobStatus(Enum):
    """Job execution status."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    RETRYING = "RETRYING"
    SKIPPED = "SKIPPED"
    TIMEOUT = "TIMEOUT"


class JobPriority(Enum):
    """Job priority levels."""

    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    URGENT = "URGENT"


class JobType(Enum):
    """Job types."""

    ONE_TIME = "ONE_TIME"
    SCHEDULED = "SCHEDULED"
    RECURRING = "RECURRING"
    DEPENDENT = "DEPENDENT"
    BATCH = "BATCH"


@dataclass
class JobResult:
    """Result of a job execution."""

    job_id: str
    job_name: str
    status: JobStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 0
    worker_id: Optional[str] = None
    queue: Optional[str] = None
    priority: JobPriority = JobPriority.NORMAL
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.status, str):
            self.status = JobStatus(self.status)
        if isinstance(self.priority, str):
            self.priority = JobPriority(self.priority)

        # Calculate duration if not provided
        if self.completed_at and self.duration_seconds is None:
            self.duration_seconds = (
                self.completed_at - self.started_at
            ).total_seconds()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "job_id": self.job_id,
            "job_name": self.job_name,
            "status": self.status.value,
            "started_at": self.started_at.isoformat(),
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "duration_seconds": self.duration_seconds,
            "result": self.result,
            "error": self.error,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "worker_id": self.worker_id,
            "queue": self.queue,
            "priority": self.priority.value,
            "metadata": self.metadata,
        }

    def is_success(self) -> bool:
        """Check if job was successful."""
        return self.status == JobStatus.COMPLETED

    def is_failed(self) -> bool:
        """Check if job failed."""
        return self.status in [JobStatus.FAILED, JobStatus.TIMEOUT, JobStatus.CANCELLED]

    def is_running(self) -> bool:
        """Check if job is currently running."""
        return self.status in [JobStatus.PENDING, JobStatus.RUNNING, JobStatus.RETRYING]

    def can_retry(self) -> bool:
        """Check if job can be retried."""
        return self.is_failed() and self.retry_count < self.max_retries

    def get_progress(self) -> Optional[float]:
        """Get job progress from metadata."""
        return self.metadata.get("progress_percentage")

    def set_progress(self, percentage: float):
        """Set job progress in metadata."""
        self.metadata["progress_percentage"] = min(100.0, max(0.0, percentage))

    def add_metadata(self, **kwargs):
        """Add metadata to job result."""
        self.metadata.update(kwargs)

    def get_error_summary(self) -> Optional[str]:
        """Get error summary."""
        if not self.error:
            return None

        # Truncate long errors
        if len(self.error) > 200:
            return self.error[:200] + "..."

        return self.error


@dataclass
class JobConfig:
    """Job configuration."""

    name: str
    function: str  # Function name or reference
    schedule: Optional[str] = None
    queue: str = "default"
    priority: JobPriority = JobPriority.NORMAL
    type: JobType = JobType.ONE_TIME
    retries: int = 3
    timeout: int = 300  # seconds
    max_instances: int = 1
    coalesce: bool = False
    misfire_grace_time: int = 300  # seconds
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    timezone: str = "UTC"
    enabled: bool = True
    description: str = ""
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.priority, str):
            self.priority = JobPriority(self.priority)
        if isinstance(self.type, str):
            self.type = JobType(self.type)

        if self.tags is None:
            self.tags = []
        if self.dependencies is None:
            self.dependencies = []
        if self.parameters is None:
            self.parameters = {}
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "function": self.function,
            "schedule": self.schedule,
            "queue": self.queue,
            "priority": self.priority.value,
            "type": self.type.value,
            "retries": self.retries,
            "timeout": self.timeout,
            "max_instances": self.max_instances,
            "coalesce": self.coalesce,
            "misfire_grace_time": self.misfire_grace_time,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "timezone": self.timezone,
            "enabled": self.enabled,
            "description": self.description,
            "tags": self.tags,
            "dependencies": self.dependencies,
            "parameters": self.parameters,
            "metadata": self.metadata,
        }

    def is_enabled(self) -> bool:
        """Check if job is enabled."""
        return self.enabled

    def is_scheduled(self) -> bool:
        """Check if job has a schedule."""
        return self.schedule is not None

    def is_recurring(self) -> bool:
        """Check if job is recurring."""
        return self.type in [JobType.SCHEDULED, JobType.RECURRING]

    def has_dependencies(self) -> bool:
        """Check if job has dependencies."""
        return len(self.dependencies) > 0

    def get_timeout_seconds(self) -> int:
        """Get timeout in seconds."""
        return self.timeout

    def get_retry_count(self) -> int:
        """Get retry count."""
        return self.retries

    def add_tag(self, tag: str):
        """Add a tag to the job."""
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str):
        """Remove a tag from the job."""
        if tag in self.tags:
            self.tags.remove(tag)

    def add_dependency(self, dependency: str):
        """Add a dependency to the job."""
        if dependency not in self.dependencies:
            self.dependencies.append(dependency)

    def remove_dependency(self, dependency: str):
        """Remove a dependency from the job."""
        if dependency in self.dependencies:
            self.dependencies.remove(dependency)

    def set_parameter(self, key: str, value: Any):
        """Set a job parameter."""
        self.parameters[key] = value

    def get_parameter(self, key: str, default: Any = None) -> Any:
        """Get a job parameter."""
        return self.parameters.get(key, default)

    def add_metadata(self, **kwargs):
        """Add metadata to the job."""
        self.metadata.update(kwargs)

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value."""
        return self.metadata.get(key, default)


@dataclass
class JobExecution:
    """Job execution record."""

    execution_id: str
    job_name: str
    job_id: str
    status: JobStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 0
    worker_id: Optional[str] = None
    queue: Optional[str] = None
    priority: JobPriority = JobPriority.NORMAL
    parent_execution_id: Optional[str] = None
    child_execution_ids: List[str] = field(default_factory=list)
    progress_percentage: float = 0.0
    progress_message: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.status, str):
            self.status = JobStatus(self.status)
        if isinstance(self.priority, str):
            self.priority = JobPriority(self.priority)

        if self.child_execution_ids is None:
            self.child_execution_ids = []
        if self.context is None:
            self.context = {}
        if self.metrics is None:
            self.metrics = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "execution_id": self.execution_id,
            "job_name": self.job_name,
            "job_id": self.job_id,
            "status": self.status.value,
            "started_at": self.started_at.isoformat(),
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "duration_seconds": self.duration_seconds,
            "result": self.result,
            "error": self.error,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "worker_id": self.worker_id,
            "queue": self.queue,
            "priority": self.priority.value,
            "parent_execution_id": self.parent_execution_id,
            "child_execution_ids": self.child_execution_ids,
            "progress_percentage": self.progress_percentage,
            "progress_message": self.progress_message,
            "context": self.context,
            "metrics": self.metrics,
        }

    def update_progress(self, percentage: float, message: str = ""):
        """Update job progress."""
        self.progress_percentage = min(100.0, max(0.0, percentage))
        if message:
            self.progress_message = message

    def add_context(self, **kwargs):
        """Add context information."""
        self.context.update(kwargs)

    def add_metric(self, key: str, value: Any):
        """Add a metric."""
        self.metrics[key] = value

    def get_metric(self, key: str, default: Any = None) -> Any:
        """Get a metric value."""
        return self.metrics.get(key, default)

    def add_child_execution(self, execution_id: str):
        """Add a child execution."""
        if execution_id not in self.child_execution_ids:
            self.child_execution_ids.append(execution_id)

    def remove_child_execution(self, execution_id: str):
        """Remove a child execution."""
        if execution_id in self.child_execution_ids:
            self.child_execution_ids.remove(execution_id)

    def has_children(self) -> bool:
        """Check if execution has children."""
        return len(self.child_execution_ids) > 0

    def get_child_count(self) -> int:
        """Get number of child executions."""
        return len(self.child_execution_ids)

    def is_complete(self) -> bool:
        """Check if execution is complete."""
        return self.status in [
            JobStatus.COMPLETED,
            JobStatus.FAILED,
            JobStatus.CANCELLED,
            JobStatus.TIMEOUT,
        ]

    def is_running(self) -> bool:
        """Check if execution is running."""
        return self.status in [JobStatus.PENDING, JobStatus.RUNNING, JobStatus.RETRYING]

    def can_retry(self) -> bool:
        """Check if execution can be retried."""
        return (
            self.status in [JobStatus.FAILED, JobStatus.TIMEOUT]
            and self.retry_count < self.max_retries
        )

    def get_duration(self) -> Optional[float]:
        """Get execution duration in seconds."""
        if self.duration_seconds:
            return self.duration_seconds

        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()

        return None


@dataclass
class JobQueue:
    """Job queue information."""

    name: str
    max_workers: int = 10
    current_workers: int = 0
    pending_jobs: int = 0
    running_jobs: int = 0
    completed_jobs: int = 0
    failed_jobs: int = 0
    total_jobs: int = 0
    priority: JobPriority = JobPriority.NORMAL
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.priority, str):
            self.priority = JobPriority(self.priority)

        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "max_workers": self.max_workers,
            "current_workers": self.current_workers,
            "pending_jobs": self.pending_jobs,
            "running_jobs": self.running_jobs,
            "completed_jobs": self.completed_jobs,
            "failed_jobs": self.failed_jobs,
            "total_jobs": self.total_jobs,
            "priority": self.priority.value,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
        }

    def get_success_rate(self) -> float:
        """Get success rate as percentage."""
        if self.total_jobs == 0:
            return 0.0

        return (self.completed_jobs / self.total_jobs) * 100

    def get_failure_rate(self) -> float:
        """Get failure rate as percentage."""
        if self.total_jobs == 0:
            return 0.0

        return (self.failed_jobs / self.total_jobs) * 100

    def is_busy(self) -> bool:
        """Check if queue is busy."""
        return self.current_workers >= self.max_workers

    def is_idle(self) -> bool:
        """Check if queue is idle."""
        return self.running_jobs == 0 and self.pending_jobs == 0

    def get_utilization(self) -> float:
        """Get queue utilization as percentage."""
        if self.max_workers == 0:
            return 0.0

        return (self.current_workers / self.max_workers) * 100

    def update_stats(self, **kwargs):
        """Update queue statistics."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        # Update timestamp
        self.updated_at = datetime.utcnow()

        # Update total jobs
        self.total_jobs = (
            self.pending_jobs
            + self.running_jobs
            + self.completed_jobs
            + self.failed_jobs
        )

    def add_metadata(self, **kwargs):
        """Add metadata to the queue."""
        self.metadata.update(kwargs)

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value."""
        return self.metadata.get(key, default)


@dataclass
class JobDependency:
    """Job dependency information."""

    job_name: str
    depends_on: str
    dependency_type: str = "SUCCESS"  # SUCCESS, COMPLETION, FAILURE
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "job_name": self.job_name,
            "depends_on": self.depends_on,
            "dependency_type": self.dependency_type,
            "created_at": self.created_at.isoformat(),
        }

    def is_success_dependency(self) -> bool:
        """Check if dependency is on success."""
        return self.dependency_type == "SUCCESS"

    def is_completion_dependency(self) -> bool:
        """Check if dependency is on completion."""
        return self.dependency_type == "COMPLETION"

    def is_failure_dependency(self) -> bool:
        """Check if dependency is on failure."""
        return self.dependency_type == "FAILURE"


@dataclass
class JobMetrics:
    """Job execution metrics."""

    job_name: str
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    cancelled_executions: int = 0
    timeout_executions: int = 0
    total_duration: float = 0.0
    min_duration: Optional[float] = None
    max_duration: Optional[float] = None
    avg_duration: float = 0.0
    last_execution: Optional[datetime] = None
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "job_name": self.job_name,
            "total_executions": self.total_executions,
            "successful_executions": self.successful_executions,
            "failed_executions": self.failed_executions,
            "cancelled_executions": self.cancelled_executions,
            "timeout_executions": self.timeout_executions,
            "total_duration": self.total_duration,
            "min_duration": self.min_duration,
            "max_duration": self.max_duration,
            "avg_duration": self.avg_duration,
            "last_execution": (
                self.last_execution.isoformat() if self.last_execution else None
            ),
            "last_success": (
                self.last_success.isoformat() if self.last_success else None
            ),
            "last_failure": (
                self.last_failure.isoformat() if self.last_failure else None
            ),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def get_success_rate(self) -> float:
        """Get success rate as percentage."""
        if self.total_executions == 0:
            return 0.0

        return (self.successful_executions / self.total_executions) * 100

    def get_failure_rate(self) -> float:
        """Get failure rate as percentage."""
        if self.total_executions == 0:
            return 0.0

        return (self.failed_executions / self.total_executions) * 100

    def update_execution(self, execution: JobExecution):
        """Update metrics with execution data."""
        self.total_executions += 1

        # Update status counts
        if execution.status == JobStatus.COMPLETED:
            self.successful_executions += 1
            self.last_success = execution.completed_at
        elif execution.status == JobStatus.FAILED:
            self.failed_executions += 1
            self.last_failure = execution.completed_at
        elif execution.status == JobStatus.CANCELLED:
            self.cancelled_executions += 1
        elif execution.status == JobStatus.TIMEOUT:
            self.timeout_executions += 1
            self.last_failure = execution.completed_at

        # Update duration metrics
        if execution.duration_seconds:
            self.total_duration += execution.duration_seconds

            if (
                self.min_duration is None
                or execution.duration_seconds < self.min_duration
            ):
                self.min_duration = execution.duration_seconds

            if (
                self.max_duration is None
                or execution.duration_seconds > self.max_duration
            ):
                self.max_duration = execution.duration_seconds

            self.avg_duration = self.total_duration / self.total_executions

        # Update timestamps
        self.last_execution = execution.completed_at or execution.started_at
        self.updated_at = datetime.utcnow()

    def reset_metrics(self):
        """Reset all metrics."""
        self.total_executions = 0
        self.successful_executions = 0
        self.failed_executions = 0
        self.cancelled_executions = 0
        self.timeout_executions = 0
        self.total_duration = 0.0
        self.min_duration = None
        self.max_duration = None
        self.avg_duration = 0.0
        self.last_execution = None
        self.last_success = None
        self.last_failure = None
        self.updated_at = datetime.utcnow()


# Utility functions
def create_job_result(
    job_name: str, status: JobStatus, started_at: Optional[datetime] = None, **kwargs
) -> JobResult:
    """Create a job result."""
    return JobResult(
        job_id=str(uuid.uuid4()),
        job_name=job_name,
        status=status,
        started_at=started_at or datetime.utcnow(),
        **kwargs
    )


def create_job_execution(
    job_name: str, job_id: str, status: JobStatus, **kwargs
) -> JobExecution:
    """Create a job execution."""
    return JobExecution(
        execution_id=str(uuid.uuid4()),
        job_name=job_name,
        job_id=job_id,
        status=status,
        started_at=datetime.utcnow(),
        **kwargs
    )


def create_job_queue(name: str, max_workers: int = 10, **kwargs) -> JobQueue:
    """Create a job queue."""
    return JobQueue(name=name, max_workers=max_workers, **kwargs)


def create_job_dependency(
    job_name: str, depends_on: str, dependency_type: str = "SUCCESS"
) -> JobDependency:
    """Create a job dependency."""
    return JobDependency(
        job_name=job_name, depends_on=depends_on, dependency_type=dependency_type
    )


def create_job_metrics(job_name: str) -> JobMetrics:
    """Create job metrics."""
    return JobMetrics(job_name=job_name)


# Serialization helpers
def serialize_job_result(result: JobResult) -> str:
    """Serialize job result to JSON string."""
    import json

    return json.dumps(result.to_dict(), default=str)


def deserialize_job_result(data: str) -> JobResult:
    """Deserialize job result from JSON string."""
    import json
    from datetime import datetime

    data_dict = json.loads(data)

    # Parse datetime fields
    if data_dict.get("started_at"):
        data_dict["started_at"] = datetime.fromisoformat(data_dict["started_at"])

    if data_dict.get("completed_at"):
        data_dict["completed_at"] = datetime.fromisoformat(data_dict["completed_at"])

    return JobResult(**data_dict)


def serialize_job_execution(execution: JobExecution) -> str:
    """Serialize job execution to JSON string."""
    import json

    return json.dumps(execution.to_dict(), default=str)


def deserialize_job_execution(data: str) -> JobExecution:
    """Deserialize job execution from JSON string."""
    import json
    from datetime import datetime

    data_dict = json.loads(data)

    # Parse datetime fields
    if data_dict.get("started_at"):
        data_dict["started_at"] = datetime.fromisoformat(data_dict["started_at"])

    if data_dict.get("completed_at"):
        data_dict["completed_at"] = datetime.fromisoformat(data_dict["completed_at"])

    return JobExecution(**data_dict)


# Validation functions
def validate_job_result(result: JobResult) -> List[str]:
    """Validate job result data."""
    errors = []

    if not result.job_id:
        errors.append("Job ID is required")

    if not result.job_name:
        errors.append("Job name is required")

    if not result.started_at:
        errors.append("Started at time is required")

    if result.completed_at and result.started_at > result.completed_at:
        errors.append("Completed time must be after started time")

    if result.duration_seconds and result.duration_seconds < 0:
        errors.append("Duration must be non-negative")

    if result.retry_count < 0:
        errors.append("Retry count must be non-negative")

    if result.max_retries < 0:
        errors.append("Max retries must be non-negative")

    return errors


def validate_job_config(config: JobConfig) -> List[str]:
    """Validate job configuration."""
    errors = []

    if not config.name:
        errors.append("Job name is required")

    if not config.function:
        errors.append("Job function is required")

    if config.timeout <= 0:
        errors.append("Timeout must be positive")

    if config.max_instances <= 0:
        errors.append("Max instances must be positive")

    if config.retries < 0:
        errors.append("Retries must be non-negative")

    if config.misfire_grace_time < 0:
        errors.append("Misfire grace time must be non-negative")

    if config.start_date and config.end_date and config.start_date > config.end_date:
        errors.append("Start date must be before end date")

    return errors


# Status transition helpers
def can_transition_status(from_status: JobStatus, to_status: JobStatus) -> bool:
    """Check if status transition is valid."""
    valid_transitions = {
        JobStatus.PENDING: [JobStatus.RUNNING, JobStatus.CANCELLED, JobStatus.SKIPPED],
        JobStatus.RUNNING: [
            JobStatus.COMPLETED,
            JobStatus.FAILED,
            JobStatus.CANCELLED,
            JobStatus.TIMEOUT,
        ],
        JobStatus.RETRYING: [JobStatus.RUNNING, JobStatus.FAILED, JobStatus.CANCELLED],
        JobStatus.COMPLETED: [],  # Terminal state
        JobStatus.FAILED: [JobStatus.RETRYING],  # Can retry
        JobStatus.CANCELLED: [],  # Terminal state
        JobStatus.TIMEOUT: [JobStatus.RETRYING],  # Can retry
        JobStatus.SKIPPED: [],  # Terminal state
    }

    return to_status in valid_transitions.get(from_status, [])


def get_terminal_statuses() -> List[JobStatus]:
    """Get list of terminal job statuses."""
    return [
        JobStatus.COMPLETED,
        JobStatus.FAILED,
        JobStatus.CANCELLED,
        JobStatus.TIMEOUT,
        JobStatus.SKIPPED,
    ]


def get_active_statuses() -> List[JobStatus]:
    """Get list of active job statuses."""
    return [JobStatus.PENDING, JobStatus.RUNNING, JobStatus.RETRYING]


def get_retryable_statuses() -> List[JobStatus]:
    """Get list of retryable job statuses."""
    return [JobStatus.FAILED, JobStatus.TIMEOUT]


# Priority helpers
def compare_priority(priority1: JobPriority, priority2: JobPriority) -> int:
    """Compare two job priorities."""
    priority_order = {
        JobPriority.URGENT: 5,
        JobPriority.CRITICAL: 4,
        JobPriority.HIGH: 3,
        JobPriority.NORMAL: 2,
        JobPriority.LOW: 1,
    }

    return priority_order[priority1] - priority_order[priority2]


def get_priority_value(priority: JobPriority) -> int:
    """Get numeric value for priority."""
    priority_values = {
        JobPriority.URGENT: 5,
        JobPriority.CRITICAL: 4,
        JobPriority.HIGH: 3,
        JobPriority.NORMAL: 2,
        JobPriority.LOW: 1,
    }

    return priority_values.get(priority, 2)


# Type helpers
def is_job_type_scheduled(job_type: JobType) -> bool:
    """Check if job type is scheduled."""
    return job_type in [JobType.SCHEDULED, JobType.RECURRING]


def is_job_type_terminal(job_type: JobType) -> bool:
    """Check if job type is terminal (one-time)."""
    return job_type == JobType.ONE_TIME


# Constants
DEFAULT_JOB_TIMEOUT = 300  # 5 minutes
DEFAULT_JOB_RETRIES = 3
DEFAULT_MAX_INSTANCES = 1
DEFAULT_MISFIRE_GRACE_TIME = 300  # 5 minutes
DEFAULT_QUEUE_MAX_WORKERS = 10

# Export all classes and functions
__all__ = [
    "JobStatus",
    "JobPriority",
    "JobType",
    "JobResult",
    "JobConfig",
    "JobExecution",
    "JobQueue",
    "JobDependency",
    "JobMetrics",
    "create_job_result",
    "create_job_execution",
    "create_job_queue",
    "create_job_dependency",
    "create_job_metrics",
    "serialize_job_result",
    "deserialize_job_result",
    "serialize_job_execution",
    "deserialize_job_execution",
    "validate_job_result",
    "validate_job_config",
    "can_transition_status",
    "get_terminal_statuses",
    "get_active_statuses",
    "get_retryable_statuses",
    "compare_priority",
    "get_priority_value",
    "is_job_type_scheduled",
    "is_job_type_terminal",
    "DEFAULT_JOB_TIMEOUT",
    "DEFAULT_JOB_RETRIES",
    "DEFAULT_MAX_INSTANCES",
    "DEFAULT_MISFIRE_GRACE_TIME",
    "DEFAULT_QUEUE_MAX_WORKERS",
]
