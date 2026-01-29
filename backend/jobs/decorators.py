"""
Job decorators for Raptorflow background jobs.

Provides @job decorator for converting functions
into schedulable jobs with retry logic and error handling.
"""

import asyncio
import functools
import inspect
import logging
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union

from scheduler import get_job_scheduler

from .models import JobConfig, JobResult, JobStatus

logger = logging.getLogger(__name__)


def job(
    name: Optional[str] = None,
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
    tags: Optional[list] = None,
):
    """Decorator to convert a function into a schedulable job.

    Args:
        name: Job name (auto-generated if not provided)
        queue: Queue name for job execution
        retries: Number of retry attempts
        timeout: Timeout in seconds
        max_instances: Maximum concurrent instances
        coalesce: Whether to coalesce multiple instances
        misfire_grace_time: Grace period for misfired jobs
        start_date: When to start scheduling
        end_date: When to stop scheduling
        timezone: Timezone for scheduling
        enabled: Whether job is enabled
        description: Job description
        tags: Job tags for filtering

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        """Decorator implementation."""
        # Auto-generate job name if not provided
        job_name = name or f"{func.__module__}.{func.__name__}"

        # Store original function for execution
        original_func = func

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            """Wrapper function for job execution."""
            # Get scheduler
            scheduler = get_job_scheduler()

            # Check if job exists
            job_config = scheduler.get_job(job_name)

            if not job_config:
                # Auto-register job if not exists
                scheduler.register_job(
                    name=job_name,
                    function=original_func,
                    schedule="0 0 * * *",  # Default to manual execution only
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
                    tags=tags,
                )
                job_config = scheduler.get_job(job_name)

            # Execute job
            result = await scheduler.run_job_now(job_name)

            return result

        # Set metadata on wrapper function
        wrapper._job_name = job_name
        wrapper._job_config = job_config

        return wrapper

    return decorator


def cron_job(
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
    tags: Optional[list] = None,
):
    """Decorator to create a cron-based scheduled job.

    Args:
        schedule: Cron expression for scheduling
        queue: Queue name for job execution
        retries: Number of retry attempts
        timeout: Timeout in seconds
        max_instances: Maximum concurrent instances
        coalesce: Whether to coalesce multiple instances
        misfire_grace_time: Grace period for misfired jobs
        start_date: When to start scheduling
        end_date: When to stop scheduling
        timezone: Timezone for scheduling
        enabled: Whether job is enabled
        description: Job description
        tags: Job tags for filtering

    Returns:
        Decorated function
    """
    return job(
        name=None,
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
        tags=tags,
    )


def interval_job(
    seconds: int,
    queue: str = "default",
    retries: int = 3,
    timeout: int = 300,
    max_instances: int = 1,
    coalesce: bool = False,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    timezone: str = "UTC",
    enabled: bool = True,
    description: str = "",
    tags: Optional[list] = None,
):
    """Decorator to create an interval-based scheduled job.

    Args:
        seconds: Interval in seconds between executions
        queue: Queue name for job execution
        retries: Number of retry attempts
        timeout: Timeout in seconds
        max_instances: Maximum concurrent instances
        coalesce: Whether to coalesce multiple instances
        start_date: When to start scheduling
        end_date: When to stop scheduling
        timezone: Timezone for scheduling
        enabled: Whether job is enabled
        description: Job description
        tags: Job tags for filtering

    Returns:
        Decorated function
    """
    # Convert seconds to cron expression (simplified)
    minutes = seconds // 60
    remaining_seconds = seconds % 60

    if minutes == 0:
        cron_expr = f"* * * * * *"
    else:
        cron_expr = f"* * * * * */{minutes} *"

    return cron_job(
        schedule=cron_expr,
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
        tags=tags,
    )


def daily_job(
    hour: int = 0,
    minute: int = 0,
    queue: str = "default",
    retries: int = 3,
    timeout: int = 300,
    max_instances: int = 1,
    coalesce: bool = False,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    timezone: str = "UTC",
    enabled: bool = True,
    description: str = "",
    tags: Optional[list] = None,
):
    """Decorator to create a daily scheduled job.

    Args:
        hour: Hour of day (0-23)
        minute: Minute of hour (0-59)
        queue: Queue name for job execution
        retries: Number of retry attempts
        timeout: Timeout in seconds
        max_instances: Maximum concurrent instances
        coalesce: Whether to coalesce multiple instances
        start_date: When to start scheduling
        end_date: When to stop scheduling
        timezone: Timezone for scheduling
        enabled: Whether job is enabled
        description: Job description
        tags: Job tags for filtering

    Returns:
        Decorated function
    """
    cron_expr = f"{minute} {hour} * * *"

    return cron_job(
        schedule=cron_expr,
        queue=queue,
        retries=retries,
        timeout=timeout,
        max_instances=max_instances,
        coalesce=coalesce,
        start_date=start_date,
        end_date=end_date,
        timezone=timezone,
        enabled=enabled,
        description=description,
        tags=tags,
    )


def hourly_job(
    minute: int = 0,
    queue: str = "default",
    retries: int = 3,
    timeout: int = 300,
    max_instances: int = 1,
    coalesce: bool = False,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    timezone: str = "UTC",
    enabled: bool = True,
    description: str = "",
    tags: Optional[list] = None,
):
    """Decorator to create an hourly scheduled job.

    Args:
        minute: Minute of hour (0-59)
        queue: Queue name for job execution
        retries: Number of retry attempts
        timeout: Timeout in seconds
        max_instances: Maximum concurrent instances
        coalesce: Whether to coalesce multiple instances
        start_date: When to start scheduling
        end_date: When to stop scheduling
        timezone: Timezone for scheduling
        enabled: Whether job is enabled
        description: Job description
        tags: Job tags for filtering

    Returns:
        Decorated function
    """
    cron_expr = f"{minute} * * * *"

    return cron_job(
        schedule=cron_expr,
        queue=queue,
        retries=retries,
        timeout=timeout,
        max_instances=max_instances,
        coalesce=coalesce,
        start_date=start_date,
        end_date=end_date,
        timezone=timezone,
        enabled=enabled,
        description=description,
        tags=tags,
    )


def weekly_job(
    day_of_week: int = 0,  # 0=Monday, 6=Sunday
    hour: int = 0,
    minute: int = 0,
    queue: str = "default",
    retries: int = 3,
    timeout: int = 300,
    max_instances: int = 1,
    coalesce: bool = False,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    timezone: str = "UTC",
    enabled: bool = True,
    description: str = "",
    tags: Optional[list] = None,
):
    """Decorator to create a weekly scheduled job.

    Args:
        day_of_week: Day of week (0=Monday, 6=Sunday)
        hour: Hour of day (0-23)
        minute: Minute of hour (0-59)
        queue: Queue name for job execution
        retries: Number of retry attempts
        timeout: Timeout in seconds
        max_instances: Maximum concurrent instances
        coalesce: Whether to coalesce multiple instances
        start_date: When to start scheduling
        end_date: When to stop scheduling
        timezone: Timezone for scheduling
        enabled: Whether job is enabled
        description: Job description
        tags: Job tags for filtering

    Returns:
        Decorated function
    """
    # Convert day of week to cron day of week (0=Sunday, 6=Saturday)
    cron_day = (day_of_week + 1) % 7

    cron_expr = f"{minute} {hour} * * {cron_day}"

    return cron_job(
        schedule=cron_expr,
        queue=queue,
        retries=retries,
        timeout=timeout,
        max_instances=max_instances,
        coalesce=coalesce,
        start_date=start_date,
        end_date=end_date,
        timezone=timezone,
        enabled=enabled,
        description=description,
        tags=tags,
    )


def monthly_job(
    day: int = 1,
    hour: int = 0,
    minute: int = 0,
    queue: str = "default",
    retries: int = 3,
    timeout: int = 300,
    max_instances: int = 1,
    coalesce: bool = False,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    timezone: str = "UTC",
    enabled: bool = True,
    description: str = "",
    tags: Optional[list] = None,
):
    """Decorator to create a monthly scheduled job.

    Args:
        day: Day of month (1-31)
        hour: Hour of day (0-23)
        minute: Minute of hour (0-59)
        queue: Queue name for job execution
        retries: Number of retry attempts
        timeout: Timeout in seconds
        max_instances: Maximum concurrent instances
        coalesce: Whether to coalesce multiple instances
        start_date: When to start scheduling
        end_date: When to stop scheduling
        timezone: Timezone for scheduling
        enabled: Whether job is enabled
        description: Job description
        tags: Job tags for filtering

    Returns:
        Decorated function
    """
    cron_expr = f"{minute} {hour} {day} * *"

    return cron_job(
        schedule=cron_expr,
        queue=queue,
        retries=retries,
        timeout=timeout,
        max_instances=max_instances,
        coalesce=coalesce,
        start_date=start_date,
        end_date=end_date,
        timezone=timezone,
        enabled=enabled,
        description=description,
        tags=tags,
    )


def background_job(
    queue: str = "background",
    retries: int = 1,
    timeout: int = 600,
    max_instances: int = 1,
    coalesce: bool = False,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    timezone: str = "UTC",
    enabled: bool = True,
    description: str = "",
    tags: Optional[list] = None,
):
    """Decorator for long-running background jobs.

    Args:
        queue: Queue name for job execution
        retries: Number of retry attempts
        timeout: Timeout in seconds
        max_instances: Maximum concurrent instances
        coalesce: Whether to coalesce multiple instances
        start_date: When to start scheduling
        end_date: When to stop scheduling
        timezone: Timezone for scheduling
        enabled: Whether job is enabled
        description: Job description
        tags: Job tags for filtering

    Returns:
        Decorated function
    """
    return job(
        name=None,
        queue=queue,
        retries=retries,
        timeout=timeout,
        max_instances=max_instances,
        coalesce=coalesce,
        start_date=start_date,
        end_date=end_date,
        timezone=timezone,
        enabled=enabled,
        description=description,
        tags=tags,
    )


def critical_job(
    queue: str = "critical",
    retries: int = 5,
    timeout: int = 600,
    max_instances: int = 1,
    coalesce: bool = False,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    timezone: str = "UTC",
    enabled: bool = True,
    description: str = "",
    tags: Optional[list] = None,
):
    """Decorator for critical system jobs.

    Args:
        queue: Queue name for job execution
        retries: Number of retry attempts
        timeout: Timeout in seconds
        max_instances: Maximum concurrent instances
        coalesce: Whether to coalesce multiple instances
        start_date: When to start scheduling
        end_date: When to stop scheduling
        timezone: Timezone for scheduling
        enabled: Whether job is enabled
        description: Job description
        tags: Job tags for filtering

    Returns:
        Decorated function
    """
    return job(
        name=None,
        queue=queue,
        retries=retries,
        timeout=timeout,
        max_instances=max_instances,
        coalesce=coalesce,
        start_date=start_date,
        end_date=end_date,
        timezone=timezone,
        enabled=enabled,
        description=description,
        tags=tags,
    )


def user_job(
    user_id: Optional[str] = None,
    queue: str = "user",
    retries: int = 2,
    timeout: int = 300,
    max_instances: int = 1,
    coalesce: bool = False,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    timezone: str = "UTC",
    enabled: bool = True,
    description: str = "",
    tags: Optional[list] = None,
):
    """Decorator for user-specific jobs.

    Args:
        user_id: User ID for job context
        queue: Queue name for job execution
        retries: Number of retry attempts
        timeout: Timeout in seconds
        max_instances: Maximum concurrent instances
        coalesce: Whether to coalesce multiple instances
        start_date: When to start scheduling
        end_date: When to stop scheduling
        timezone: Timezone for scheduling
        enabled: Whether job is enabled
        description: Job description
        tags: Job tags for filtering

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        """Decorator implementation."""

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Add user_id to kwargs if not present
            if user_id and "user_id" not in kwargs:
                kwargs["user_id"] = user_id

            # Execute original function
            result = await func(*args, **kwargs)
            return result

        # Set metadata on wrapper function
        wrapper._job_user_id = user_id

        return wrapper

    return decorator


def workspace_job(
    workspace_id: Optional[str] = None,
    queue: str = "workspace",
    retries: int = 2,
    timeout: int = 300,
    max_instances: int = 1,
    coalesce: bool = False,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    timezone: str = "UTC",
    enabled: bool = True,
    description: str = "",
    tags: Optional[list] = None,
):
    """Decorator for workspace-specific jobs.

    Args:
        workspace_id: Workspace ID for job context
        queue: Queue name for job execution
        retries: Number of retry attempts
        timeout: Timeout in seconds
        max_instances: Maximum concurrent instances
        coalesce: Whether to coalesce multiple instances
        start_date: When to start scheduling
        end_date: When to stop scheduling
        timezone: Timezone for scheduling
        enabled: Whether job is enabled
        description: Job description
        tags: Job tags for filtering

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        """Decorator implementation."""

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Add workspace_id to kwargs if not present
            if workspace_id and "workspace_id" not in kwargs:
                kwargs["workspace_id"] = workspace_id

            # Execute original function
            result = await func(*args, **kwargs)
            return result

        # Set metadata on wrapper function
        wrapper._job_workspace_id = workspace_id

        return wrapper

    return decorator


# Convenience function for manual job execution
async def execute_job(job_name: str, *args, **kwargs) -> JobResult:
    """Execute a job manually."""
    scheduler = get_job_scheduler()
    return await scheduler.run_job_now(job_name)


# Job execution context manager
class JobContext:
    """Context manager for job execution."""

    def __init__(self, job_name: str, job_id: str, **context):
        self.job_name = job_name
        self.job_id = job_id
        self.context = context
        self.start_time = datetime.utcnow()

    def get_duration(self) -> float:
        """Get job execution duration in seconds."""
        return (datetime.utcnow() - self.start_time).total_seconds()

    def add_context(self, **kwargs):
        """Add context information."""
        self.context.update(kwargs)

    def get_context(self) -> Dict[str, Any]:
        """Get current context."""
        return self.context.copy()


# Job execution context manager (thread-local)
_job_context = None


def get_job_context() -> Optional[JobContext]:
    """Get current job execution context."""
    return _job_context


def set_job_context(context: JobContext):
    """Set job execution context."""
    global _job_context
    _job_context = context


@contextmanager
def job_context(job_name: str, job_id: str, **context):
    """Context manager for job execution."""
    context = JobContext(job_name, job_id, **context)

    try:
        set_job_context(context)
        yield context
    finally:
        set_job_context(None)


# Error handling decorator
def handle_errors(
    default_error: str = "Unknown error occurred",
    retry_on: List[Exception] = None,
    log_errors: bool = True,
):
    """Decorator to handle job errors with retry logic."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            context = get_job_context()

            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # Check if error should be retried
                should_retry = False
                if retry_on:
                    should_retry = any(
                        isinstance(e, error_type) for error_type in retry_on
                    )

                if should_retry:
                    context.add_context(
                        error_type=type(e).__name__,
                        error_message=str(e),
                        retry_count=context.get("retry_count", 0) + 1,
                    )
                    raise  # Re-raise to trigger retry
                else:
                    context.add_context(
                        error_type=type(e).__name__, error_message=str(e)
                    )

                # Log error if enabled
                if log_errors:
                    logger.error(f"Job {context.job_name} failed: {e}")

                # Return error result
                return JobResult(
                    job_id=context.job_id,
                    job_name=context.job_name,
                    status=JobStatus.FAILED,
                    error=str(e),
                    started_at=context.start_time,
                    completed_at=datetime.utcnow(),
                    retry_count=context.get("retry_count", 0),
                )

        return wrapper

    return decorator


# Timeout handling decorator
def timeout_handler(default_timeout: int = 300, on_timeout: Optional[Callable] = None):
    """Decorator to handle job timeouts."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            context = get_job_context()

            try:
                # Execute with timeout
                result = await asyncio.wait_for(
                    func(*args, **kwargs), timeout=default_timeout
                )
                return result
            except asyncio.TimeoutError:
                context.add_context(
                    error_type="TimeoutError",
                    error_message=f"Job timed out after {default_timeout} seconds",
                )

                if on_timeout:
                    await on_timeout(context)

                # Return timeout result
                return JobResult(
                    job_id=context.job_id,
                    job_name=context.job_name,
                    status=JobStatus.FAILED,
                    error=f"Job timed out after {default_timeout} seconds",
                    started_at=context.start_time,
                    completed_at=datetime.utcnow(),
                    retry_count=context.get("retry_count", 0),
                )

        return wrapper

    return decorator


# Resource cleanup decorator
def cleanup_resources(
    resources: List[str] = None, cleanup_func: Optional[Callable] = None
):
    """Decorator to cleanup resources after job execution."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            context = get_job_context()

            try:
                return await func(*args, **kwargs)
            finally:
                # Cleanup resources
                if cleanup_func:
                    await cleanup_func(context)
                elif resources:
                    # Basic resource cleanup
                    for resource in resources:
                        if hasattr(resource, "close"):
                            try:
                                await resource.close()
                            except Exception:
                                logger.warning(f"Failed to close resource: {resource}")

                # Clear context
                set_job_context(None)

        return wrapper

    return decorator


# Progress tracking decorator
def track_progress(
    total_steps: int, step_description: str = "Processing", log_progress: bool = True
):
    """Decorator to track job progress."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            context = get_job_context()

            # Initialize progress tracking
            current_step = 0
            context.add_context(
                total_steps=total_steps,
                current_step=current_step,
                step_description=step_description,
                progress_percentage=0.0,
            )

            try:
                # Execute function
                result = await func(*args, **kwargs)

                # Mark as completed
                current_step = total_steps
                context.add_context(
                    total_steps=total_steps,
                    current_step=current_step,
                    step_description="Completed",
                    progress_percentage=100.0,
                )

                return result

            except Exception as e:
                # Mark as failed
                context.add_context(
                    total_steps=total_steps,
                    current_step=current_step,
                    step_description=f"Failed: {str(e)}",
                    progress_percentage=(current_step / total_steps) * 100,
                )
                raise

        return wrapper

    return decorator


# Retry decorator with exponential backoff
def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
):
    """Decorator to retry failed operations with exponential backoff."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            context = get_job_context()

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        # Last attempt failed, raise
                        raise e

                    # Calculate delay with jitter
                    delay = base_delay * (backoff_factor**attempt)
                    if jitter:
                        delay *= 0.5 + (hash(str(attempt)) % 100) / 100

                    context.add_context(
                        retry_count=attempt + 1, last_error=str(e), retry_delay=delay
                    )

                    # Log retry attempt
                    logger.warning(
                        f"Job {context.job_name} attempt {attempt + 1}/{max_attempts} failed, "
                        f"retrying in {delay:.2f} seconds"
                    )

                    await asyncio.sleep(delay)

            # All attempts failed
            raise Exception(f"All {max_attempts} attempts failed")

        return wrapper


# Batch job decorator
def batch_job(
    batch_size: int = 100,
    queue: str = "batch",
    retries: int = 3,
    timeout: int = 600,
    max_instances: int = 1,
):
    """Decorator for batch processing jobs."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            context = get_job_context()

            # Handle batch processing
            if len(args) > 1 and isinstance(args[0], (list, tuple)):
                items = args[0]
                results = []

                for i in range(0, len(items), batch_size):
                    batch = items[i : i + batch_size]

                    context.add_context(
                        batch_number=i // batch_size + 1,
                        total_batches=(len(items) + batch_size - 1) // batch_size,
                        current_item=i,
                        items_in_batch=len(batch),
                    )

                    # Execute batch
                    batch_result = await func(batch, **kwargs)
                    results.extend(batch_result)

                return results
            else:
                # Single item execution
                return await func(*args, **kwargs)

        return wrapper

    return decorator


# Priority job decorator
def priority_job(
    priority: str = "normal",
    queue: str = "priority",
    retries: int = 3,
    timeout: int = 300,
    max_instances: int = 1,
):
    """Decorator for priority jobs."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            context = get_job_context()
            context.add_context(priority=priority)
            return await func(*args, **kwargs)

        return wrapper


# Conditional job decorator
def conditional_job(
    condition: Union[bool, Callable],
    queue: str = "conditional",
    retries: int = 1,
    timeout: int = 300,
    max_instances: int = 1,
):
    """Decorator for conditional job execution."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Check condition
            should_run = (
                condition(*args, **kwargs) if callable(condition) else condition
            )

            if not should_run:
                return JobResult(
                    job_id=str(uuid.uuid4()),
                    job_name=wrapper._job_name,
                    status=JobStatus.SKIPPED,
                    error="Condition not met",
                    started_at=datetime.utcnow(),
                    completed_at=datetime.utcnow(),
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


# Global job registry for manual job management
class JobRegistry:
    """Global job registry for managing jobs."""

    def __init__(self):
        self.scheduler = get_job_scheduler()
        self.logger = logging.getLogger("job_registry")

    def register(self, name: str, **kwargs):
        """Register a job with the scheduler."""
        self.scheduler.register_job(name, **kwargs)

    def unregister(self, name: str):
        """Unregister a job from the scheduler."""
        self.scheduler.unregister_job(name)

    def enable(self, name: str):
        """Enable a job."""
        self.scheduler.enable_job(name)

    def disable(self, name: str):
        """Disable a job."""
        self.scheduler.disable_job(name)

    async def execute(self, name: str, *args, **kwargs) -> JobResult:
        """Execute a job manually."""
        return await self.scheduler.run_job_now(name, *args, **kwargs)

    def list_jobs(self) -> List[str]:
        """List all registered jobs."""
        return self.scheduler.list_jobs()

    def get_job(self, name: str) -> Optional[JobConfig]:
        """Get job configuration."""
        return self.scheduler.get_job(name)

    def get_stats(self) -> Dict[str, Any]:
        """Get job statistics."""
        return self.scheduler.get_job_stats()


# Global job registry
_job_registry = JobRegistry()


# Convenience functions
def register_job(name: str, **kwargs):
    """Register a job with the global registry."""
    _job_registry.register(name, **kwargs)


def unregister_job(name: str):
    """Unregister a job from the global registry."""
    _job_registry.unregister_job(name)


async def execute_job(name: str, *args, **kwargs) -> JobResult:
    """Execute a job using the global registry."""
    return await _job_registry.execute(name, *args, **kwargs)


def list_jobs() -> List[str]:
    """List all jobs in the global registry."""
    return _job_registry.list_jobs()


def get_job_stats() -> Dict[str, Any]:
    """Get job statistics from the global registry."""
    return _job_registry.get_stats()


def enable_job(name: str):
    """Enable a job in the global registry."""
    _job_registry.enable_job(name)


def disable_job(name: str):
    """Disable a job in the global registry."""
    _job_registry.disable_job(name)
