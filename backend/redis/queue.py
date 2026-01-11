"""
Queue service for Redis-based background job processing.

Implements priority queues, job scheduling, and reliable processing
with retry logic and worker coordination.
"""

import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .client import get_redis
from .critical_fixes import JobPayloadValidator
from .queue_models import Job, JobPriority, JobResult, JobStatus, QueueStats, WorkerInfo


class QueueService:
    """Redis-based job queue service with priority support."""

    KEY_PREFIX = "queue:"
    PROCESSING_PREFIX = "processing:"
    STATS_PREFIX = "stats:"
    WORKER_PREFIX = "worker:"

    def __init__(self):
        self.redis = get_redis()
        self.payload_validator = JobPayloadValidator()

    def _get_queue_key(self, queue_name: str) -> str:
        """Get Redis key for queue."""
        return f"{self.KEY_PREFIX}{queue_name}"

    def _get_processing_key(self, queue_name: str) -> str:
        """Get Redis key for processing jobs."""
        return f"{self.PROCESSING_PREFIX}{queue_name}"

    def _get_job_key(self, job_id: str) -> str:
        """Get Redis key for individual job."""
        return f"job:{job_id}"

    def _get_stats_key(self, queue_name: str) -> str:
        """Get Redis key for queue stats."""
        return f"{self.STATS_PREFIX}{queue_name}"

    def _get_worker_key(self, worker_id: str) -> str:
        """Get Redis key for worker info."""
        return f"{self.WORKER_PREFIX}{worker_id}"

    async def enqueue(
        self,
        queue_name: str,
        job_type: str,
        payload: Dict[str, Any],
        priority: int = JobPriority.NORMAL.value,
        delay_until: Optional[datetime] = None,
        max_retries: int = 3,
        timeout_seconds: int = 300,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Add a job to queue with payload validation."""
        # Validate payload before enqueuing
        try:
            validated_payload = self.payload_validator.validate_payload(payload)
        except ValueError as e:
            raise ValueError(f"Invalid job payload: {e}")

        job_id = str(uuid.uuid4())

        job = Job(
            job_id=job_id,
            queue_name=queue_name,
            job_type=job_type,
            payload=validated_payload,
            priority=priority,
            delay_until=delay_until,
            max_retries=max_retries,
            timeout_seconds=timeout_seconds,
            metadata=metadata or {},
        )

        # Store job data
        job_key = self._get_job_key(job_id)
        await self.redis.set_json(job_key, job.to_dict())

        # Add to queue if ready, otherwise mark as delayed
        if job.is_ready():
            await self._add_to_queue(job)
        else:
            # Store delayed job
            delayed_key = f"delayed:{job_id}"
            await self.redis.set_json(
                delayed_key,
                job.to_dict(),
                ex=int((delay_until - datetime.now()).total_seconds()),
            )

        return job_id

    async def _add_to_queue(self, job: Job):
        """Add job to appropriate queue based on priority."""
        queue_key = self._get_queue_key(job.queue_name)

        # Use priority-based queue (higher priority = lower score)
        score = -job.priority  # Negative for descending order
        job_data = json.dumps({"job_id": job.job_id, "priority": job.priority})

        await self.redis.async_client.zadd(queue_key, {job_data: score})

    async def dequeue(
        self, queue_name: str, worker_id: Optional[str] = None
    ) -> Optional[Job]:
        """Get next job from queue."""
        queue_key = self._get_queue_key(queue_name)

        # Get highest priority job (lowest score)
        job_data_list = await self.redis.async_client.zrange(queue_key, 0, 0)

        if not job_data_list:
            return None

        job_data = json.loads(job_data_list[0])
        job_id = job_data["job_id"]

        # Remove from queue atomically
        removed = await self.redis.async_client.zrem(queue_key, job_data_list[0])
        if not removed:
            return None  # Another worker got it

        # Get full job data
        job_key = self._get_job_key(job_id)
        job_dict = await self.redis.get_json(job_key)
        if not job_dict:
            return None

        job = Job.from_dict(job_dict)

        # Mark as processing
        if worker_id:
            job.mark_processing(worker_id)
            await self.redis.set_json(job_key, job.to_dict())

            # Add to processing queue
            processing_key = self._get_processing_key(queue_name)
            await self.redis.async_client.zadd(
                processing_key, {job_id: datetime.now().timestamp()}
            )

        return job

    async def peek(self, queue_name: str) -> Optional[Job]:
        """Look at next job without removing it."""
        queue_key = self._get_queue_key(queue_name)

        # Get highest priority job
        job_data_list = await self.redis.async_client.zrange(queue_key, 0, 0)

        if not job_data_list:
            return None

        job_data = json.loads(job_data_list[0])
        job_id = job_data["job_id"]

        # Get full job data
        job_key = self._get_job_key(job_id)
        job_dict = await self.redis.get_json(job_key)
        if not job_dict:
            return None

        return Job.from_dict(job_dict)

    async def queue_length(self, queue_name: str) -> int:
        """Get number of jobs in queue."""
        queue_key = self._get_queue_key(queue_name)
        return await self.redis.async_client.zcard(queue_key)

    async def processing_count(self, queue_name: str) -> int:
        """Get number of jobs being processed."""
        processing_key = self._get_processing_key(queue_name)
        return await self.redis.async_client.zcard(processing_key)

    async def complete_job(
        self, job_id: str, result: JobResult, worker_id: Optional[str] = None
    ) -> bool:
        """Mark a job as completed."""
        job_key = self._get_job_key(job_id)
        job_dict = await self.redis.get_json(job_key)
        if not job_dict:
            return False

        job = Job.from_dict(job_dict)
        job.mark_completed(result)

        # Update job data
        await self.redis.set_json(job_key, job.to_dict())

        # Remove from processing queue
        processing_key = self._get_processing_key(job.queue_name)
        await self.redis.async_client.zrem(processing_key, job_id)

        # Update worker stats
        if worker_id:
            await self._update_worker_stats(worker_id, job.queue_name, completed=True)

        return True

    async def fail_job(
        self,
        job_id: str,
        error: str,
        error_details: Optional[Dict[str, Any]] = None,
        worker_id: Optional[str] = None,
    ) -> bool:
        """Mark a job as failed and retry if possible."""
        job_key = self._get_job_key(job_id)
        job_dict = await self.redis.get_json(job_key)
        if not job_dict:
            return False

        job = Job.from_dict(job_dict)
        job.mark_failed(error, error_details)

        # Remove from processing queue
        processing_key = self._get_processing_key(job.queue_name)
        await self.redis.async_client.zrem(processing_key, job_id)

        if job.can_retry():
            # Retry the job
            job.status = JobStatus.PENDING
            await self.redis.set_json(job_key, job.to_dict())
            await self._add_to_queue(job)
        else:
            # Mark as permanently failed
            await self.redis.set_json(job_key, job.to_dict())

        # Update worker stats
        if worker_id:
            await self._update_worker_stats(worker_id, job.queue_name, completed=False)

        return True

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending job."""
        job_key = self._get_job_key(job_id)
        job_dict = await self.redis.get_json(job_key)
        if not job_dict:
            return False

        job = Job.from_dict(job_dict)
        job.mark_cancelled()

        # Update job data
        await self.redis.set_json(job_key, job.to_dict())

        # Remove from queue if pending
        if job.status == JobStatus.CANCELLED:
            queue_key = self._get_queue_key(job.queue_name)
            job_data = json.dumps({"job_id": job_id, "priority": job.priority})
            await self.redis.async_client.zrem(queue_key, job_data)

        return True

    async def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID."""
        job_key = self._get_job_key(job_id)
        job_dict = await self.redis.get_json(job_key)
        if not job_dict:
            return None

        return Job.from_dict(job_dict)

    async def clear_queue(self, queue_name: str) -> int:
        """Clear all jobs from queue."""
        queue_key = self._get_queue_key(queue_name)
        count = await self.queue_length(queue_name)
        await self.redis.delete(queue_key)
        return count

    async def get_queue_stats(self, queue_name: str) -> QueueStats:
        """Get queue statistics."""
        # Count jobs by status
        total_jobs = 0
        pending_jobs = await self.queue_length(queue_name)
        processing_jobs = await self.processing_count(queue_name)

        # For completed/failed counts, we'd need to scan all jobs
        # For now, use placeholder values
        completed_jobs = 0
        failed_jobs = 0
        cancelled_jobs = 0

        return QueueStats(
            queue_name=queue_name,
            total_jobs=total_jobs,
            pending_jobs=pending_jobs,
            processing_jobs=processing_jobs,
            completed_jobs=completed_jobs,
            failed_jobs=failed_jobs,
            cancelled_jobs=cancelled_jobs,
            avg_runtime_seconds=0.0,
            success_rate=0.0,
        )

    async def cleanup_expired_jobs(
        self, queue_name: str, max_age_hours: int = 24
    ) -> int:
        """Clean up old completed/failed jobs."""
        cleaned = 0
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)

        # In production, this would scan job keys and clean old ones
        # For now, return placeholder
        return cleaned

    async def _update_worker_stats(
        self, worker_id: str, queue_name: str, completed: bool
    ):
        """Update worker statistics."""
        worker_key = self._get_worker_key(worker_id)
        worker_dict = await self.redis.get_json(worker_key)

        if worker_dict:
            worker = WorkerInfo.from_dict(worker_dict)
        else:
            worker = WorkerInfo(
                worker_id=worker_id, queue_name=queue_name, status="active"
            )

        worker.last_activity = datetime.now()
        if completed:
            worker.jobs_processed += 1

        await self.redis.set_json(
            worker_key, worker.to_dict(), ex=3600
        )  # 1 hour expiry

    async def register_worker(self, worker_id: str, queue_name: str) -> WorkerInfo:
        """Register a worker."""
        worker = WorkerInfo(worker_id=worker_id, queue_name=queue_name, status="active")

        worker_key = self._get_worker_key(worker_id)
        await self.redis.set_json(worker_key, worker.to_dict(), ex=3600)

        return worker

    async def get_workers(self, queue_name: str) -> List[WorkerInfo]:
        """Get active workers for queue."""
        # In production, maintain a worker index
        # For now, return empty list
        return []

    # Convenience methods for common job types
    async def enqueue_agent_task(
        self,
        workspace_id: str,
        task_data: Dict[str, Any],
        priority: int = JobPriority.NORMAL.value,
    ) -> str:
        """Queue an agent execution task."""
        return await self.enqueue(
            queue_name="agent_tasks",
            job_type=os.getenv("JOB_TYPE"),
            payload={"workspace_id": workspace_id, **task_data},
            priority=priority,
        )

    async def enqueue_webhook(self, webhook_type: str, payload: Dict[str, Any]) -> str:
        """Queue a webhook for processing."""
        return await self.enqueue(
            queue_name="webhooks", job_type=webhook_type, payload=payload
        )

    async def enqueue_email(
        self, to: str, subject: str, body: str, template: Optional[str] = None
    ) -> str:
        """Queue an email for sending."""
        return await self.enqueue(
            queue_name="emails",
            job_type="send_email",
            payload={"to": to, "subject": subject, "body": body, "template": template},
        )
