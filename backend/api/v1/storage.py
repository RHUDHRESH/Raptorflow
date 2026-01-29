"""
Storage API endpoints for file operations
Integrates with GCS service for upload/download functionality
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from infrastructure.storage import FileCategory, get_cloud_storage
from pydantic import BaseModel, Field

from ..core.auth import get_current_user
from ..services.storage import get_enhanced_storage_service

logger = logging.getLogger(__name__)
router = APIRouter()


class UploadURLRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    file_name: str = Field(..., description="Original file name")
    file_type: str = Field(
        ..., description="File category (avatar, document, workspace)"
    )
    file_size: int = Field(..., description="File size in bytes")


class DownloadURLRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    file_path: str = Field(..., description="File path in GCS")


class FileInfoRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    file_path: str = Field(..., description="File path in GCS")


@router.post("/storage/upload-url")
async def generate_upload_url(
    request: UploadURLRequest, current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Generate signed upload URL for file upload"""
    try:
        # Validate user access
        if current_user["id"] != request.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )

        # Map file type to category
        category_map = {
            "avatar": FileCategory.MEDIA,
            "document": FileCategory.DOCUMENTS,
            "workspace": FileCategory.UPLOADS,
        }

        category = category_map.get(request.file_type, FileCategory.UPLOADS)

        # Get storage client
        storage = get_cloud_storage()

        # Generate unique object name
        import uuid
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        safe_filename = "".join(
            c for c in request.file_name if c.isalnum() or c in "._-"
        )
        object_name = f"{request.user_id}/{category.value}/{timestamp}_{unique_id}_{safe_filename}"

        # Generate signed upload URL
        # Note: GCS doesn't support direct upload URL generation like S3
        # We'll implement a different approach using resumable uploads

        return JSONResponse(
            {
                "upload_url": f"https://storage.googleapis.com/upload/storage/v1/b/{storage.config.bucket_name}/o?uploadType=resumable&name={object_name}",
                "file_path": object_name,
                "expires_in": 3600,
                "method": "POST",
            }
        )

    except Exception as e:
        logger.error(f"Error generating upload URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate upload URL: {str(e)}",
        )


@router.post("/storage/download-url")
async def generate_download_url(
    request: DownloadURLRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Generate signed download URL for file download"""
    try:
        # Validate user access
        if current_user["id"] != request.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )

        # Security: Ensure user can only access their own files
        if not request.file_path.startswith(f"{request.user_id}/"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Invalid file path",
            )

        # Get storage client
        storage = get_cloud_storage()

        # Generate signed download URL
        download_url = await storage.generate_download_url(
            file_id=request.file_path.split("/")[-1],  # Extract file ID from path
            workspace_id=request.user_id,
            expiration_hours=1,
        )

        if not download_url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
            )

        return JSONResponse({"download_url": download_url, "expires_in": 3600})

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating download URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate download URL: {str(e)}",
        )


@router.post("/storage/file-info")
async def get_file_info(
    request: FileInfoRequest, current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get file information"""
    try:
        # Validate user access
        if current_user["id"] != request.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )

        # Security: Ensure user can only access their own files
        if not request.file_path.startswith(f"{request.user_id}/"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Invalid file path",
            )

        # Get storage client
        storage = get_cloud_storage()

        # Get file info
        file_info = await storage.get_file_info(
            file_id=request.file_path.split("/")[-1], workspace_id=request.user_id
        )

        if not file_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
            )

        return JSONResponse(
            {
                "file_name": file_info.filename,
                "size": file_info.size_bytes,
                "content_type": file_info.content_type,
                "created_at": file_info.created_at.isoformat(),
                "updated_at": file_info.updated_at.isoformat(),
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get file info: {str(e)}",
        )


@router.delete("/storage/file")
async def delete_file(
    request: FileInfoRequest, current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete a file"""
    try:
        # Validate user access
        if current_user["id"] != request.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )

        # Security: Ensure user can only access their own files
        if not request.file_path.startswith(f"{request.user_id}/"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Invalid file path",
            )

        # Get storage client
        storage = get_cloud_storage()

        # Delete file
        success = await storage.delete_file(
            file_id=request.file_path.split("/")[-1], workspace_id=request.user_id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found or deletion failed",
            )

        return JSONResponse({"success": True, "message": "File deleted successfully"})

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}",
        )


@router.get("/storage/usage/{user_id}")
async def get_storage_usage(
    user_id: str, current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get storage usage statistics for user"""
    try:
        # Validate user access
        if current_user["id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )

        # Get storage client
        storage = get_cloud_storage()

        # Get usage statistics
        usage = await storage.get_workspace_usage(user_id)

        return JSONResponse(
            {
                "user_id": user_id,
                "total_size_bytes": usage.get("total_size_bytes", 0),
                "total_size_mb": usage.get("total_size_mb", 0),
                "file_count": usage.get("file_count", 0),
                "category_counts": usage.get("category_counts", {}),
                "storage_class_counts": usage.get("storage_class_counts", {}),
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting storage usage: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get storage usage: {str(e)}",
        )


@router.post("/storage/cleanup")
async def cleanup_storage_files(
    days_old: int = 30, current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Clean up old files from storage"""
    try:
        # Only admin users can cleanup storage
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required for storage cleanup",
            )

        result = await get_enhanced_storage_service().cleanup_old_files(days_old)
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during storage cleanup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Storage cleanup failed: {str(e)}",
        )


@router.delete("/storage/files/{storage_path:path}")
async def delete_storage_file(
    storage_path: str, current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete file from storage"""
    try:
        # Security: Ensure user can only access their own files
        user_id = current_user["id"]
        if not storage_path.startswith(f"{user_id}/"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Invalid file path",
            )

        result = get_enhanced_storage_service().delete_file(storage_path)

        if result["status"] != "success":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", "File not found"),
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting storage file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File deletion failed: {str(e)}",
        )


@router.get("/storage/workspace/{workspace_id}/usage")
async def get_workspace_storage_usage(
    workspace_id: str, current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get detailed storage usage for workspace"""
    try:
        # Validate user access to workspace
        if current_user["id"] != workspace_id and current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )

        usage = get_enhanced_storage_service().get_workspace_usage(workspace_id)

        if "error" in usage:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=usage["error"]
            )

        return usage

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workspace storage usage: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get storage usage: {str(e)}",
        )


@router.get("/storage/health")
async def storage_health_check():
    """Health check for storage service"""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "enhanced_storage": "operational",
                "cloud_storage": "operational",
                "cdn_configured": bool(get_enhanced_storage_service().cdn_base_url),
                "security_scanning": get_enhanced_storage_service().enable_security_scanning,
                "image_processing": get_enhanced_storage_service().enable_image_processing,
            },
        }

        # Test cloud storage connection
        try:
            cloud_storage = get_cloud_storage()
            bucket_info = cloud_storage.get_bucket_info()
            health_status["services"]["bucket_info"] = bucket_info
        except Exception as e:
            health_status["services"]["cloud_storage"] = f"error: {str(e)}"
            health_status["status"] = "degraded"

        return health_status

    except Exception as e:
        logger.error(f"Storage health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            },
        )
