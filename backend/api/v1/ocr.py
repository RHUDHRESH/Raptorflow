"""
API endpoints for OCR job management and status tracking.
"""

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from backend.services.ocr.queue import OCRQueue

logger = logging.getLogger(__name__)
router = APIRouter()
ocr_queue = OCRQueue()


class OCRJobStatusResponse(BaseModel):
    """Response model for OCR job status."""

    job_id: str
    status: str
    job_type: str
    created_at: str
    updated_at: Optional[str] = None
    error: Optional[str] = None
    progress: int = 0


class OCRJobEnqueuedResponse(BaseModel):
    """Response model for newly enqueued OCR job."""

    job_id: str
    status: str = "enqueued"


@router.get("/ocr/jobs/{job_id}", response_model=OCRJobStatusResponse)
async def get_ocr_job_status(job_id: str):
    """
    Retrieve the current status of an OCR background job.
    """
    try:
        status_info = await ocr_queue.get_job_status(job_id)
        
        if not status_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"OCR job {job_id} not found"
            )
            
        return status_info

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving OCR job status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving job status"
        )


@router.post("/ocr/jobs/clear", status_code=status.HTTP_204_NO_CONTENT)
async def clear_ocr_queue():
    """
    Clear all pending OCR jobs from the queue.
    """
    try:
        await ocr_queue.queue_service.clear_queue(ocr_queue.queue_name)
        return None
    except Exception as e:
        logger.error(f"Error clearing OCR queue: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error clearing OCR queue"
        )
