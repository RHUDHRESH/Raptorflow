"""
OCR Job Queue for asynchronous processing.
Integrates with the core Redis-based QueueService.
"""

import logging
from typing import Any, Dict, Optional

from ..redis_core.queue import QueueService
from ..redis_core.queue_models import JobPriority

logger = logging.getLogger(__name__)


class OCRQueue:
    """
    Queue service specifically for OCR tasks.
    """

    def __init__(self):
        self.queue_service = QueueService()
        self.queue_name = "ocr_tasks"

    async def enqueue_ocr_job(
        self,
        file_path: str,
        workspace_id: str,
        priority: int = JobPriority.NORMAL.value,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Add an OCR job to the queue.

        Args:
            file_path: Path to the file in storage (GCS/S3).
            workspace_id: Workspace ID the file belongs to.
            priority: Job priority.
            metadata: Additional metadata for the job.

        Returns:
            Job ID.
        """
        payload = {
            "file_path": file_path,
            "workspace_id": workspace_id,
            "metadata": metadata or {},
        }

        job_id = await self.queue_service.enqueue(
            queue_name=self.queue_name,
            job_type="ocr_extraction",
            payload=payload,
            priority=priority,
        )

        logger.info(f"Enqueued OCR job {job_id} for file {file_path}")
        return job_id

    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current status of an OCR job.
        """
        job = await self.queue_service.get_job(job_id)
        if not job:
            return None

        return {
            "job_id": job.job_id,
            "status": job.status.value,
            "job_type": job.job_type,
            "created_at": job.created_at.isoformat(),
            "updated_at": job.updated_at.isoformat() if job.updated_at else None,
            "error": job.error,
            "progress": job.metadata.get("progress", 0),
        }
