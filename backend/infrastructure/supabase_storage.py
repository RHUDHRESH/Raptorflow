"""
Supabase Storage integration for Raptorflow.

Provides file upload, download, and management capabilities
with workspace isolation and security features using Supabase Storage.
"""

import hashlib
import logging
import mimetypes
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, BinaryIO, Dict, List, Optional, Union

from ..services.supabase_storage_client import get_supabase_storage_client
from ..utils.storage_paths import (
    generate_intelligence_path,
    generate_user_path,
    generate_workspace_path,
    get_bucket_for_category,
    parse_storage_path,
)

logger = logging.getLogger(__name__)


class FileCategory(Enum):
    """File categories for organization."""

    UPLOADS = "uploads"
    EXPORTS = "exports"
    BACKUPS = "backups"
    LOGS = "logs"
    ASSETS = "assets"
    TEMP = "temp"
    DOCUMENTS = "documents"
    MEDIA = "media"
    INTELLIGENCE = "intelligence"


@dataclass
class StorageConfig:
    """Supabase Storage configuration."""

    default_bucket: str
    enable_versioning: bool = True
    enable_lifecycle: bool = True
    retention_days: int = 30

    # Performance settings
    chunk_size: int = 8 * 1024 * 1024  # 8MB
    max_file_size: int = 5 * 1024 * 1024 * 1024  # 5GB
    upload_timeout: int = 300  # 5 minutes
    download_timeout: int = 300  # 5 minutes

    # Security settings
    allowed_mime_types: List[str] = field(default_factory=list)
    blocked_mime_types: List[str] = field(default_factory=list)
    require_authentication: bool = True

    @classmethod
    def from_env(cls) -> "StorageConfig":
        """Create configuration from environment variables."""
        return cls(
            default_bucket=os.getenv("SUPABASE_STORAGE_BUCKET", "workspace-uploads"),
            enable_versioning=os.getenv("SUPABASE_STORAGE_VERSIONING", "true").lower()
            == "true",
            enable_lifecycle=os.getenv("SUPABASE_STORAGE_LIFECYCLE", "true").lower()
            == "true",
            retention_days=int(os.getenv("SUPABASE_STORAGE_RETENTION_DAYS", "30")),
            chunk_size=int(
                os.getenv("SUPABASE_STORAGE_CHUNK_SIZE", str(8 * 1024 * 1024))
            ),
            max_file_size=int(
                os.getenv("SUPABASE_STORAGE_MAX_FILE_SIZE", str(5 * 1024 * 1024 * 1024))
            ),
            upload_timeout=int(os.getenv("SUPABASE_STORAGE_UPLOAD_TIMEOUT", "300")),
            download_timeout=int(os.getenv("SUPABASE_STORAGE_DOWNLOAD_TIMEOUT", "300")),
            require_authentication=os.getenv(
                "SUPABASE_STORAGE_REQUIRE_AUTH", "true"
            ).lower()
            == "true",
        )


@dataclass
class FileMetadata:
    """File metadata."""

    file_id: str
    filename: str
    content_type: str
    size_bytes: int
    workspace_id: str
    user_id: str
    category: FileCategory

    # Storage details
    bucket_name: str
    object_path: str
    is_public: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

    # Additional metadata
    checksum: Optional[str] = None
    download_url: Optional[str] = None
    custom_metadata: Dict[str, str] = field(default_factory=dict)


# Result classes


@dataclass
class UploadResult:
    """Result of file upload."""

    success: bool
    file_id: Optional[str] = None
    object_path: Optional[str] = None
    download_url: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class DownloadResult:
    """Result of file download."""

    success: bool
    content: Optional[bytes] = None
    filename: Optional[str] = None
    content_type: Optional[str] = None
    size_bytes: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class SupabaseStorage:
    """Supabase Storage client for Raptorflow."""

    def __init__(self, config: Optional[StorageConfig] = None):
        self.config = config or StorageConfig.from_env()
        self.client = get_supabase_storage_client()
        self.logger = logging.getLogger("supabase_storage")

    def _calculate_checksum(self, content: bytes) -> str:
        """Calculate SHA256 checksum."""
        return hashlib.sha256(content).hexdigest()

    def _validate_file(
        self, filename: str, content_type: str, size_bytes: int
    ) -> List[str]:
        """Validate file against configuration."""
        errors = []

        # Check file size
        if size_bytes > self.config.max_file_size:
            errors.append(
                f"File size {size_bytes} exceeds maximum {self.config.max_file_size}"
            )

        # Check MIME type
        if (
            self.config.allowed_mime_types
            and content_type not in self.config.allowed_mime_types
        ):
            errors.append(f"MIME type {content_type} not in allowed list")

        if (
            self.config.blocked_mime_types
            and content_type in self.config.blocked_mime_types
        ):
            errors.append(f"MIME type {content_type} is blocked")

        return errors

    async def upload_file(
        self,
        content: Union[bytes, BinaryIO],
        filename: str,
        workspace_id: str,
        user_id: str,
        category: FileCategory = FileCategory.UPLOADS,
        content_type: Optional[str] = None,
        is_public: bool = False,
        expires_at: Optional[datetime] = None,
        custom_metadata: Optional[Dict[str, str]] = None,
    ) -> UploadResult:
        """Upload file to Supabase Storage."""
        try:
            # Convert bytes to bytes if needed
            if isinstance(content, str):
                content = content.encode("utf-8")

            # Detect content type if not provided
            if not content_type:
                content_type, _ = mimetypes.guess_type(filename)
                if not content_type:
                    content_type = "application/octet-stream"

            # Get file size
            if isinstance(content, bytes):
                size_bytes = len(content)
            else:
                # For file-like objects, get size
                current_pos = content.tell()
                content.seek(0, 2)  # Seek to end
                size_bytes = content.tell()
                content.seek(current_pos)  # Reset position

            # Validate file
            validation_errors = self._validate_file(filename, content_type, size_bytes)
            if validation_errors:
                return UploadResult(
                    success=False, error_message="; ".join(validation_errors)
                )

            # Generate file ID
            file_id = str(uuid.uuid4())

            # Calculate checksum
            if isinstance(content, bytes):
                checksum = self._calculate_checksum(content)
                file_content = content
            else:
                # For file-like objects, read content to calculate checksum
                current_pos = content.tell()
                file_content = content.read()
                checksum = self._calculate_checksum(file_content)
                content.seek(current_pos)  # Reset position

            # Prepare metadata
            metadata = {
                "file_id": file_id,
                "filename": filename,
                "content_type": content_type,
                "size_bytes": str(size_bytes),
                "workspace_id": workspace_id,
                "user_id": user_id,
                "category": category.value,
                "checksum": checksum,
                "is_public": str(is_public),
                "created_at": datetime.now().isoformat(),
            }

            if custom_metadata:
                metadata.update(custom_metadata)

            # Upload using appropriate method
            if category == FileCategory.INTELLIGENCE:
                query_hash = (
                    custom_metadata.get("query_hash", file_id)
                    if custom_metadata
                    else file_id
                )
                result = self.client.upload_intelligence_file(
                    query_hash, filename, file_content, content_type, metadata
                )
            elif workspace_id:
                # Workspace file
                workspace_slug = workspace_id  # Could be enhanced to fetch slug
                result = self.client.upload_workspace_file(
                    workspace_slug,
                    category.value,
                    filename,
                    file_content,
                    content_type,
                    metadata,
                )
            else:
                # User file
                result = self.client.upload_user_file(
                    user_id,
                    category.value,
                    filename,
                    file_content,
                    content_type,
                    metadata,
                )

            # Get download URL
            download_url = None
            if is_public:
                bucket = get_bucket_for_category(category.value)
                download_url = self.client.get_public_url(bucket, result["path"])

            self.logger.info(
                f"Successfully uploaded file: {filename} -> {result['path']}"
            )

            return UploadResult(
                success=True,
                file_id=file_id,
                object_path=result["path"],
                download_url=download_url,
                metadata=metadata,
            )

        except Exception as e:
            self.logger.error(f"Failed to upload file {filename}: {e}")
            return UploadResult(success=False, error_message=str(e))

    async def download_file(
        self, file_id: str, bucket: Optional[str] = None
    ) -> DownloadResult:
        """Download file from Supabase Storage."""
        try:
            if not bucket:
                # Try to infer bucket from file path
                parsed = parse_storage_path(file_id)
                if parsed:
                    bucket = get_bucket_for_category(parsed.category)
                else:
                    bucket = self.config.default_bucket

            content = self.client.download_file(bucket, file_id)

            # Get file info
            try:
                file_info = self.client.get_file_info(bucket, file_id)
                metadata = file_info.get("metadata", {})

                return DownloadResult(
                    success=True,
                    content=content,
                    filename=metadata.get("filename"),
                    content_type=metadata.get("content_type"),
                    size_bytes=len(content),
                    metadata=file_info,
                )
            except:
                # Fallback if metadata not available
                return DownloadResult(
                    success=True,
                    content=content,
                    size_bytes=len(content),
                )

        except Exception as e:
            self.logger.error(f"Failed to download file {file_id}: {e}")
            return DownloadResult(success=False, error_message=str(e))

    async def delete_file(self, file_id: str, bucket: Optional[str] = None) -> bool:
        """Delete file from Supabase Storage."""
        try:
            if not bucket:
                # Try to infer bucket from file path
                parsed = parse_storage_path(file_id)
                if parsed:
                    bucket = get_bucket_for_category(parsed.category)
                else:
                    bucket = self.config.default_bucket

            self.client.delete_file(bucket, file_id)
            self.logger.info(f"Successfully deleted file: {file_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to delete file {file_id}: {e}")
            return False

    def get_public_url(
        self, file_id: str, bucket: Optional[str] = None
    ) -> Optional[str]:
        """Get public URL for file."""
        try:
            if not bucket:
                # Try to infer bucket from file path
                parsed = parse_storage_path(file_id)
                if parsed:
                    bucket = get_bucket_for_category(parsed.category)
                else:
                    bucket = self.config.default_bucket

            return self.client.get_public_url(bucket, file_id)

        except Exception as e:
            self.logger.error(f"Failed to get public URL for {file_id}: {e}")
            return None

    def create_signed_url(
        self, file_id: str, bucket: Optional[str] = None, expires_in: int = 3600
    ) -> Optional[str]:
        """Create signed URL for file access."""
        try:
            if not bucket:
                # Try to infer bucket from file path
                parsed = parse_storage_path(file_id)
                if parsed:
                    bucket = get_bucket_for_category(parsed.category)
                else:
                    bucket = self.config.default_bucket

            result = self.client.create_signed_url(bucket, file_id, expires_in)
            return result.get("signedUrl")

        except Exception as e:
            self.logger.error(f"Failed to create signed URL for {file_id}: {e}")
            return None

    async def get_workspace_usage(self, workspace_id: str) -> Dict[str, Any]:
        """Get storage usage for workspace."""
        try:
            # List files in workspace folders
            total_size = 0
            file_count = 0

            for category in FileCategory:
                if category == FileCategory.INTELLIGENCE:
                    continue  # Skip intelligence for workspace usage

                bucket = get_bucket_for_category(category.value)
                prefix = f"workspace/{workspace_id}/{category.value}/"

                try:
                    files = self.client.list_files(bucket, prefix)
                    for file_info in files:
                        total_size += file_info.get("size", 0)
                        file_count += 1
                except:
                    # Skip if bucket doesn't exist or no access
                    continue

            return {
                "status": "success",
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "file_count": file_count,
                "workspace_id": workspace_id,
            }

        except Exception as e:
            self.logger.error(f"Failed to get workspace usage for {workspace_id}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "total_size_bytes": 0,
                "total_size_mb": 0,
                "file_count": 0,
            }

    async def cleanup_expired_files(self) -> int:
        """Clean up expired files."""
        try:
            cleaned_count = 0
            current_time = datetime.now()

            # This would require custom implementation as Supabase doesn't have built-in lifecycle
            # For now, return 0 as placeholder
            self.logger.info("Cleanup completed: 0 files (placeholder implementation)")
            return cleaned_count

        except Exception as e:
            self.logger.error(f"Failed to cleanup expired files: {e}")
            return 0


def get_supabase_storage() -> SupabaseStorage:
    """Get configured Supabase Storage instance."""
    return SupabaseStorage()
