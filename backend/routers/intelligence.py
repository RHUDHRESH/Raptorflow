from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import Dict, Any
from backend.core.security import verify_token
from backend.utils.queue import redis_queue, Priority
from backend.services.task_tracker import update_task_status, get_task_status
from uuid import uuid4
import logging
import shutil
import tempfile
import os

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/task/{task_id}")
async def get_intelligence_task_status(
    task_id: str,
    auth: Dict[str, str] = Depends(verify_token)
):
    """
    Get the status of an intelligence task.
    """
    status = await get_task_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    return status

@router.post("/upload")
async def upload_intelligence(
    file: UploadFile = File(...),
    auth: Dict[str, str] = Depends(verify_token)
):
    """
    Universal Upload Endpoint: Accepts any file, queues it for processing.
    Sub-Layer 2: Upload API Gateway (Zero-Copy Optimization)
    """
    session_id = str(uuid4())
    task_id = str(uuid4())
    
    # 1. Validation
    
    try:
        # 1. Streaming Save (Zero RAM Overhead)
        suffix = os.path.splitext(file.filename)[1] if file.filename else ""
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            file_path = tmp.name
            
        # Check size after save
        file_size = os.path.getsize(file_path)
        if file_size > 50 * 1024 * 1024: # 50MB limit
            os.remove(file_path)
            raise HTTPException(status_code=413, detail="File too large (Max 50MB)")
            
        # 2. Type Detection & Priority Assignment
        content_type = file.content_type
        filename = file.filename
        
        if "pdf" in content_type or filename.endswith(".pdf"):
            upload_type = "pdf"
            priority = Priority.HIGH
        elif "image" in content_type or filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            upload_type = "image"
            priority = Priority.HIGH
        elif "video" in content_type:
            upload_type = "video"
            priority = Priority.LOW
        else:
            upload_type = "text" # Default/Fallback
            priority = Priority.MEDIUM
            
        # 3. Payload Construction (Pass Path, Not Blob)
        payload = {
            "session_id": session_id,
            "task_id": task_id,
            "upload_type": upload_type,
            "filename": filename,
            "content_type": content_type,
            "file_path": file_path, # CRITICAL: Passing path
            "file_size": file_size
        }

        # 4. Update Status & Enqueue Task
        await update_task_status(
            task_id, 
            "queued", 
            {
                "upload_type": upload_type,
                "filename": filename,
                "progress": 0,
                "message": "Queued for processing"
            }
        )

        await redis_queue.enqueue(
            task_type="process_upload",
            payload=payload,
            priority=priority,
            correlation_id=task_id
        )
        
        logger.info(f"Upload enqueued: {task_id} ({upload_type})")
        
        return {
            "task_id": task_id,
            "session_id": session_id,
            "status": "queued",
            "estimated_time": 30 if upload_type in ["pdf", "image"] else 10
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-url")
async def analyze_url(
    payload: Dict[str, str],
    auth: Dict[str, str] = Depends(verify_token)
):
    """
    Analyze a URL for intelligence.
    """
    url = payload.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL required")
        
    session_id = str(uuid4())
    task_id = str(uuid4())
    
    try:
        task_payload = {
            "session_id": session_id,
            "task_id": task_id,
            "upload_type": "url",
            "url": url
        }
        
        await update_task_status(
            task_id, 
            "queued", 
            {
                "upload_type": "url", 
                "url": url,
                "progress": 0,
                "message": "Queued for analysis"
            }
        )

        await redis_queue.enqueue(
            task_type="process_upload",
            payload=task_payload,
            priority=Priority.MEDIUM,
            correlation_id=task_id
        )
        
        return {
            "task_id": task_id,
            "session_id": session_id,
            "status": "queued",
            "estimated_time": 15
        }
    except Exception as e:
        logger.error(f"URL analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
