"""Supabase Storage manager.

Canonical file storage using Supabase Storage buckets.
Replaces the removed GCS integration.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def _get_storage():
    """Get the Supabase storage client from the canonical supabase_mgr."""
    from backend.core.supabase_mgr import get_supabase_client

    client = get_supabase_client()
    return client.storage


def _get_bucket() -> str:
    """Get the configured storage bucket name."""
    from backend.config.settings import get_settings

    return get_settings().SUPABASE_STORAGE_BUCKET


def upload_file(
    file_data: bytes,
    path: str,
    content_type: str = "application/octet-stream",
    bucket: Optional[str] = None,
) -> Dict[str, Any]:
    """Upload a file to Supabase Storage.

    Args:
        file_data: Raw file bytes.
        path: Storage path (e.g. "workspace-id/reports/file.pdf").
        content_type: MIME type.
        bucket: Override bucket name (defaults to SUPABASE_STORAGE_BUCKET).

    Returns:
        Dict with status and path or error.
    """
    bucket = bucket or _get_bucket()
    try:
        storage = _get_storage()
        result = storage.from_(bucket).upload(
            path,
            file_data,
            file_options={"content-type": content_type},
        )
        logger.info("Uploaded %s to %s/%s", content_type, bucket, path)
        return {"status": "success", "path": path, "bucket": bucket}
    except Exception as exc:
        logger.error("Upload failed (%s/%s): %s", bucket, path, exc)
        return {"status": "error", "error": str(exc)}


def get_public_url(path: str, bucket: Optional[str] = None) -> str:
    """Get a public URL for a stored file."""
    bucket = bucket or _get_bucket()
    try:
        storage = _get_storage()
        result = storage.from_(bucket).get_public_url(path)
        return result
    except Exception as exc:
        logger.error("Failed to get public URL (%s/%s): %s", bucket, path, exc)
        return ""


def get_signed_url(
    path: str, expires_in: int = 3600, bucket: Optional[str] = None
) -> str:
    """Get a signed (temporary) URL for a stored file."""
    bucket = bucket or _get_bucket()
    try:
        storage = _get_storage()
        result = storage.from_(bucket).create_signed_url(path, expires_in)
        return result.get("signedURL", "")
    except Exception as exc:
        logger.error("Failed to get signed URL (%s/%s): %s", bucket, path, exc)
        return ""


def delete_file(path: str, bucket: Optional[str] = None) -> Dict[str, Any]:
    """Delete a file from Supabase Storage."""
    bucket = bucket or _get_bucket()
    try:
        storage = _get_storage()
        storage.from_(bucket).remove([path])
        logger.info("Deleted %s/%s", bucket, path)
        return {"status": "success", "path": path}
    except Exception as exc:
        logger.error("Delete failed (%s/%s): %s", bucket, path, exc)
        return {"status": "error", "error": str(exc)}


def list_files(
    prefix: str = "", bucket: Optional[str] = None
) -> List[Dict[str, Any]]:
    """List files in a bucket path."""
    bucket = bucket or _get_bucket()
    try:
        storage = _get_storage()
        result = storage.from_(bucket).list(prefix)
        return result if isinstance(result, list) else []
    except Exception as exc:
        logger.error("List failed (%s/%s): %s", bucket, prefix, exc)
        return []
