"""
Job scheduler for Raptorflow background jobs.

Provides job registration, scheduling, execution,
and management with support for multiple scheduling backends.
"""

import asyncio
import json
import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from ..infrastructure.cloud_tasks import get_cloud_tasks_client
from ..infrastructure.logging import get_cloud_logging
from .models import JobResult, JobStatus

logger = logging.getLogger(__name__)


class SchedulerBackend(Enum):
    """Available scheduler backends."""

    APSCHEDULER = "apscheduler"
    CLOUD_TASKS = "cloud_tasks"
    CELERY = "celery"
    REDIS_QUEUE = "redis_queue"


@dataclass
class JobConfig:
    """Job configuration."""

    name: str
    function: Callable
    schedule: str  # Cron expression
    queue: str = "default"
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

    def __post_init__(self):
        """Post-initialization processing."""
        if self.tags is None:
            self.tags = []


@dataclass
class JobExecution:
    """Job execution record."""

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

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.status, str):
            self.status = JobStatus(self.status)

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
        }


class JobScheduler:
    """Job scheduler for managing background jobs."""

    def __init__(self):
        self.logger = logging.getLogger("job_scheduler")
        self.logging = get_cloud_logging()

        # Configuration
        self.backend = SchedulerBackend(
            os.getenv("JOB_SCHEDULER_BACKEND", "cloud_tasks")
        )
        self.timezone = os.getenv("JOB_SCHEDULER_TIMEZONE", "UTC")
        self.max_workers = int(os.getenv("JOB_SCHEDULER_MAX_WORKERS", "10"))

        # Job registry
        self.jobs: Dict[str, JobConfig] = {}
        self.job_functions: Dict[str, Callable] = {}

        # Execution tracking
        self.active_jobs: Dict[str, JobExecution] = {}
        self.job_history: List[JobExecution] = []
        self.max_history_size = int(os.getenv("JOB_SCHEDULER_HISTORY_SIZE", "1000"))

        # Scheduler state
        self._running = False
        self._scheduler_task: Optional[asyncio.Task] = None
        self._scheduler_instance: Optional[Any] = None

        # Cloud Tasks client
        self.cloud_tasks = get_cloud_tasks_client()

        # Worker ID
        self.worker_id = f"worker-{uuid.uuid4().hex[:8]}"

    def register_job(
        self,
        name: str,
        function: Callable,
        schedule: str,
        queue: str = "default",
        retries: int = 3,
        timeout: int = 300,
        max_instances: int = 1,
        coalesce: bool = False,
        misfire_grace_time: int = 300,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        timezone: str = "UTC",
        enabled: bool = True,
        description: str = "",
        tags: List[str] = None,
    ):
        """Register a job with the scheduler."""
        config = JobConfig(
            name=name,
            function=function,
            schedule=schedule,
            queue=queue,
            retries=retries,
            timeout=timeout,
            max_instances=max_instances,
            coalesce=coalesce,
            misfire_grace_time=misfire_grace_time,
            start_date=start_date,
            end_date=end_date,
            timezone=timezone,
            enabled=enabled,
            description=description,
            tags=tags or [],
        )

        self.jobs[name] = config
        self.job_functions[name] = function

        self.logger.info(f"Registered job: {name} with schedule: {schedule}")

    def unregister_job(self, name: str):
        """Unregister a job from the scheduler."""
        if name in self.jobs:
            del self.jobs[name]
            del self.job_functions[name]
            self.logger.info(f"Unregistered job: {name}")

    def enable_job(self, name: str):
        """Enable a job."""
        if name in self.jobs:
            self.jobs[name].enabled = True
            self.logger.info(f"Enabled job: {name}")

    def disable_job(self, name: str):
        """Disable a job."""
        if name in self.jobs:
            self.jobs[name].enabled = False
            self.logger.info(f"Disabled job: {name}")

    def get_job(self, name: str) -> Optional[JobConfig]:
        """Get job configuration."""
        return self.jobs.get(name)

    def list_jobs(self) -> List[str]:
        """List all registered job names."""
        return list(self.jobs.keys())

    def get_enabled_jobs(self) -> List[str]:
        """List enabled job names."""
        return [name for name, config in self.jobs.items() if config.enabled]

    async def start(self):
        """Start the job scheduler."""
        if self._running:
            self.logger.warning("Job scheduler is already running")
            return

        try:
            self._running = True

            if self.backend == SchedulerBackend.CLOUD_TASKS:
                await self._start_cloud_tasks_scheduler()
            else:
                await self._start_apscheduler()

            self.logger.info(
                f"Job scheduler started with backend: {self.backend.value}"
            )

        except Exception as e:
            self.logger.error(f"Failed to start job scheduler: {e}")
            self._running = False
            raise

    async def stop(self):
        """Stop the job scheduler gracefully."""
        if not self._running:
            self.logger.warning("Job scheduler is not running")
            return

        try:
            self._running = False

            if self._scheduler_task:
                self._scheduler_task.cancel()
                self._scheduler_task = None

            if self._scheduler_instance:
                if hasattr(self._scheduler_instance, "shutdown"):
                    if asyncio.iscoroutinefunction(self._scheduler_instance.shutdown):
                        await self._scheduler_instance.shutdown()
                    else:
                        self._scheduler_instance.shutdown()

            # Wait for active jobs to complete (with timeout)
            if self.active_jobs:
                self.logger.info(
                    f"Waiting for {len(self.active_jobs)} active jobs to complete..."
                )

                timeout = 30  # 30 seconds
                start_time = datetime.now()

                while (
                    self.active_jobs
                    and (datetime.now() - start_time).total_seconds() < timeout
                ):
                    await asyncio.sleep(1)

                # Force cancel remaining jobs
                for job_id, execution in self.active_jobs.items():
                    self.logger.warning(f"Force cancelling job: {job_id}")
                    execution.status = JobStatus.CANCELLED
                    execution.completed_at = datetime.now()
                    execution.error = "Scheduler shutdown"

            self.logger.info("Job scheduler stopped")

        except Exception as e:
            self.logger.error(f"Error stopping job scheduler: {e}")

    async def _start_cloud_tasks_scheduler(self):
        """Start Cloud Tasks based scheduler."""
        # Create queues for different job priorities
        queues = set()
        for job_config in self.jobs.values():
            queues.add(job_config.queue)

        # Create queues
        for queue_name in queues:
            await self.cloud_tasks.create_queue(
                queue_name, max_concurrent_tasks=self.max_workers
            )

        # Start scheduler loop
        self._scheduler_task = asyncio.create_task(self._cloud_tasks_scheduler_loop())

        try:
            await self._scheduler_task
        except asyncio.CancelledError:
            pass
        finally:
            self._scheduler_task = None

    async def _cloud_tasks_scheduler_loop(self):
        """Cloud Tasks scheduler loop."""
        while self._running:
            try:
                # Check for scheduled jobs
                await self._check_scheduled_jobs()

                # Sleep for 1 minute
                await asyncio.sleep(60)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Cloud Tasks scheduler error: {e}")
                await asyncio.sleep(60)

    async def _start_apscheduler(self):
        """Start APScheduler based scheduler."""
        try:
            from apscheduler.executors.asyncio import AsyncIOExecutor
            from apscheduler.jobstores.redis import RedisJobStore
            from apscheduler.schedulers.asyncio import AsyncIOScheduler
            from apscheduler.triggers.cron import CronTrigger

            # Create job store
            job_store = RedisJobStore(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", "6379")),
                db=int(os.getenv("REDIS_DB", "0")),
                password=os.getenv("REDIS_PASSWORD"),
                prefix="apscheduler",
            )

            # Create scheduler
            self._scheduler_instance = AsyncIOScheduler(
                jobstore=job_store,
                timezone=self.timezone,
                executors={"default": AsyncIOExecutor(max_workers=self.max_workers)},
            )

            # Add jobs
            for job_config in self.jobs.values():
                if job_config.enabled:
                    trigger = CronTrigger.from_crontab(
                        job_config.schedule, timezone=self.timezone
                    )

                    self._scheduler_instance.add_job(
                        func=self._job_wrapper,
                        trigger=trigger,
                        id=job_config.name,
                        name=job_config.description or job_config.name,
                        max_instances=job_config.max_instances,
                        coalesce=job_config.coalesce,
                        misfire_grace_time=timedelta(
                            seconds=job_config.misfire_grace_time
                        ),
                        start_date=job_config.start_date,
                        end_date=job_config.end_date,
                        timezone=self.timezone,
                        replace_existing=True,
                    )

            # Start scheduler
            self._scheduler_instance.start()

            # Run scheduler loop
            while self._running:
                await asyncio.sleep(1)

        except ImportError:
            self.logger.error(
                "APScheduler not available. Install with: pip install apscheduler"
            )
            raise
        except Exception as e:
            self.logger.error(f"Failed to start APScheduler: {e}")
            raise

    async def _check_scheduled_jobs(self):
        """Check for scheduled jobs and execute them."""
        for job_config in self.jobs.values():
            if not job_config.enabled:
                continue

            # Check if job should run now (simplified)
            if self._should_run_job_now(job_config):
                await self.execute_job(job_config.name)

    def _should_run_now(self, job_config: JobConfig) -> bool:
        """Check if job should run now (simplified implementation)."""
        # This is a simplified check - in production, use proper cron parsing
        current_time = datetime.utcnow()

        # For now, just check if it's time to run (every hour)
        # In production, implement proper cron expression parsing
        return current_time.minute == 0

    async def execute_job(self, job_name: str) -> JobResult:
        """Execute a job."""
        job_config = self.jobs.get(job_name)
        if not job_config:
            return JobResult(
                job_id=str(uuid.uuid4()),
                job_name=job_name,
                status=JobStatus.FAILED,
                error=f"Job not found: {job_name}",
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
            )

        if not job_config.enabled:
            return JobResult(
                job_id=str(uuid.uuid4()),
                job_name=job_name,
                status=JobStatus.SKIPPED,
                error="Job is disabled",
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
            )

        # Check if job is already running
        active_executions = [
            exec
            for exec in self.active_jobs.values()
            if exec.job_name == job_name
            and exec.status in [JobStatus.PENDING, JobStatus.RUNNING]
        ]

        if len(active_executions) >= job_config.max_instances:
            return JobResult(
                job_id=str(uuid.uuid4()),
                job_name=job_name,
                status=JobStatus.SKIPPED,
                error=f"Job already running (max instances: {job_config.max_instances})",
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
            )

        # Create job execution
        execution = JobExecution(
            job_id=str(uuid.uuid4()),
            job_name=job_name,
            status=JobStatus.PENDING,
            started_at=datetime.utcnow(),
            max_retries=job_config.retries,
            worker_id=self.worker_id,
        )

        self.active_jobs[execution.job_id] = execution

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                f"Job started: {job_name}",
                {
                    "job_id": execution.job_id,
                    "job_name": job_name,
                    "worker_id": self.worker_id,
                    "queue": job_config.queue,
                    "retries": job_config.retries,
                    "timeout": job_config.timeout,
                },
            )

            # Execute job with timeout
            result = await asyncio.wait_for(
                self._execute_job_function(job_config, execution),
                timeout=job_config.timeout,
            )

            # Update execution
            execution.status = JobStatus.COMPLETED
            execution.completed_at = datetime.utcnow()
            execution.duration_seconds = (
                execution.completed_at - execution.started_at
            ).total_seconds()
            execution.result = result

            # Log job completion
            await self.logging.log_structured(
                "INFO",
                f"Job completed: {job_name}",
                {
                    "job_id": execution.job_id,
                    "job_name": job_name,
                    "duration_seconds": execution.duration_seconds,
                    "result": str(result)[:1000] if result else None,
                },
            )

            # Create result
            job_result = JobResult(
                job_id=execution.job_id,
                job_name=job_name,
                status=JobStatus.COMPLETED,
                result=result,
                started_at=execution.started_at,
                completed_at=execution.completed_at,
                duration_seconds=execution.duration_seconds,
                retry_count=execution.retry_count,
            )

        except asyncio.TimeoutError:
            execution.status = JobStatus.FAILED
            execution.completed_at = datetime.now()
            execution.error = f"Job timed out after {job_config.timeout} seconds"

            job_result = JobResult(
                job_id=execution.job_id,
                job_name=job_name,
                status=JobStatus.FAILED,
                error=execution.error,
                started_at=execution.started_at,
                completed_at=execution.completed_at,
                duration_seconds=execution.duration_seconds,
                retry_count=execution.retry_count,
            )

        except Exception as e:
            execution.status = JobStatus.FAILED
            execution.completed_at = datetime.now()
            execution.error = str(e)

            job_result = JobResult(
                job_id=execution.job_id,
                job_name=job_name,
                status=JobStatus.FAILED,
                error=str(e),
                started_at=execution.started_at,
                completed_at=execution.completed_at,
                duration_seconds=execution.duration_seconds,
                retry_count=execution.retry_count,
            )

        finally:
            # Remove from active jobs
            if execution.job_id in self.active_jobs:
                del self.active_jobs[execution.job_id]

            # Add to history
            self.job_history.append(execution)

            # Trim history if needed
            if len(self.job_history) > self.max_history_size:
                self.job_history = self.job_history[-self.max_history_size :]

            # Handle retries
            if (
                job_result.status == JobStatus.FAILED
                and execution.retry_count < execution.max_retries
            ):
                await self._schedule_retry(execution, job_config)

        return job_result

    async def _execute_job_function(
        self, job_config: JobConfig, execution: JobExecution
    ) -> Any:
        """Execute the actual job function."""
        if self.backend == SchedulerBackend.CLOUD_TASKS:
            return await self._execute_job_via_cloud_tasks(job_config, execution)
        else:
            return await job_config.function()

    async def _execute_job_via_cloud_tasks(
        self, job_config: JobConfig, execution: JobExecution
    ) -> Any:
        """Execute job via Cloud Tasks."""
        # Create task payload
        payload = {
            "job_id": execution.job_id,
            "job_name": job_config.name,
            "worker_id": self.worker_id,
            "retry_count": execution.retry_count,
        }

        # Create and submit task
        task_result = await self.cloud_tasks.create_task(
            handler_url=os.getenv(
                "JOB_HANDLER_URL", "https://your-app.com/jobs/handle"
            ),
            payload=payload,
            queue_name=job_config.queue,
            delay_seconds=0,
        )

        if task_result.success:
            # Wait for job completion (polling)
            return await self._wait_for_cloud_task_completion(execution.job_id)
        else:
            raise Exception(f"Failed to create Cloud Task: {task_result.error_message}")

    async def _wait_for_cloud_task_completion(self, job_id: str) -> Any:
        """Wait for Cloud Task completion."""
        max_wait_time = 300  # 5 minutes
        poll_interval = 10  # 10 seconds

        start_time = datetime.now()

        while (datetime.now() - start_time).total_seconds() < max_wait_time:
            # Get task status
            task_info = await self.cloud_tasks.get_task("default", job_id)

            if task_info and task_info.status in ["COMPLETED", "FAILED"]:
                if task_info.status == "FAILED":
                    raise Exception(f"Cloud Task failed: {task_info.error_message}")

                # Get result from task metadata
                if task_info.response_body:
                    return json.loads(task_info.response_body)

                return None

            await asyncio.sleep(poll_interval)

        raise TimeoutError(
            f"Cloud Task {job_id} did not complete within {max_wait_time} seconds"
        )

    async def _schedule_retry(self, execution: JobExecution, job_config: JobConfig):
        """Schedule a job retry."""
        # Calculate retry delay (exponential backoff)
        retry_delay = min(300, (2**execution.retry_count) * 60)  # Max 5 minutes

        execution.retry_count += 1
        execution.status = JobStatus.RETRYING

        # Schedule retry
        await asyncio.sleep(retry_delay)

        # Re-execute job
        await self.execute_job(execution.job_name)

    async def run_job_now(self, job_name: str) -> JobResult:
        """Run a job immediately."""
        return await self.execute_job(job_name)

    def get_active_jobs(self) -> Dict[str, JobExecution]:
        """Get currently active jobs."""
        return self.active_jobs.copy()

    def get_job_history(self, limit: int = 100) -> List[JobExecution]:
        """Get job execution history."""
        return self.job_history[-limit:]

    def get_job_stats(self) -> Dict[str, Any]:
        """Get job execution statistics."""
        total_jobs = len(self.job_history)

        status_counts = {}
        for execution in self.job_history:
            status = execution.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        job_counts = {}
        for execution in self.job_history:
            job_name = execution.job_name
            job_counts[job_name] = job_counts.get(job_name, 0) + 1

        return {
            "total_jobs": total_jobs,
            "active_jobs": len(self.active_jobs),
            "status_counts": status_counts,
            "job_counts": job_counts,
            "worker_id": self.worker_id,
            "backend": self.backend.value,
            "max_workers": self.max_workers,
        }

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel an active job."""
        if job_id not in self.active_jobs:
            return False

        execution = self.active_jobs[job_id]
        execution.status = JobStatus.CANCELLED
        execution.completed_at = datetime.now()
        execution.error = "Cancelled by user"

        # Remove from active jobs
        del self.active_jobs[job_id]

        # Add to history
        self.job_history.append(execution)

        self.logger.info(f"Cancelled job: {job_id}")
        return True

    async def cancel_all_jobs(self) -> int:
        """Cancel all active jobs."""
        cancelled_count = 0

        for job_id in list(self.active_jobs.keys()):
            if await self.cancel_job(job_id):
                cancelled_count += 1

        return cancelled_count

    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._running

    def get_backend(self) -> SchedulerBackend:
        """Get current scheduler backend."""
        return self.backend

    def get_worker_id(self) -> str:
        """Get worker ID."""
        return self.worker_id


# Global job scheduler instance
_job_scheduler: Optional[JobScheduler] = None


def get_job_scheduler() -> JobScheduler:
    """Get global job scheduler instance."""
    global _job_scheduler
    if _job_scheduler is None:
        _job_scheduler = JobScheduler()
    return _job_scheduler


def initialize_job_scheduler() -> JobScheduler:
    """Initialize global job scheduler."""
    global _job_scheduler
    _job_scheduler = JobScheduler()
    return _job_scheduler


# Convenience functions
def register_job(
    name: str,
    schedule: str,
    queue: str = "default",
    retries: int = 3,
    timeout: int = 300,
    **kwargs,
):
    """Decorator to register a job."""

    def decorator(func):
        scheduler = get_job_scheduler()
        scheduler.register_job(
            name=name,
            function=func,
            schedule=schedule,
            queue=queue,
            retries=retries,
            timeout=timeout,
            **kwargs,
        )
        return func

    return decorator


async def run_job(job_name: str) -> JobResult:
    """Run a job immediately."""
    scheduler = get_job_scheduler()
    return await scheduler.run_job_now(job_name)


async def get_job_stats() -> Dict[str, Any]:
    """Get job statistics."""
    scheduler = get_job_scheduler()
    return scheduler.get_job_stats()


async def start_scheduler():
    """Start the job scheduler."""
    scheduler = get_job_scheduler()
    await scheduler.start()


async def stop_scheduler():
    """Stop the job scheduler."""
    scheduler = get_job_scheduler()
    await scheduler.stop()
