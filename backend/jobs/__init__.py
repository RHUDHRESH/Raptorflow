"""
Background jobs system for Raptorflow.

Provides job scheduling, execution, and management
with support for retries, timeouts, and monitoring.
"""

from .decorators import job
from .models import JobResult, JobStatus

__all__ = ["JobScheduler", "JobResult", "JobStatus", "job"]


def __getattr__(name: str):
    # Keep package import lightweight; scheduler pulls in optional cloud deps.
    if name == "JobScheduler":
        from .scheduler import JobScheduler  # noqa: PLC0415

        return JobScheduler
    raise AttributeError(name)
