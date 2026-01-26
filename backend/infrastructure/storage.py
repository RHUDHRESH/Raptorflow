"""
Google Cloud Storage integration for Raptorflow.

Provides file upload, download, and management capabilities
with workspace isolation and security features.
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

from google.api_core import exceptions
from google.api_core.retry import Retry
from google.cloud import storage

from .gcp import get_gcp_client

logger = logging.getLogger(__name__)


class StorageClass(Enum):
    """Google Cloud Storage storage classes."""

    STANDARD = "STANDARD"
    NEARLINE = "NEARLINE"
    COLDLINE = "COLDLINE"
    ARCHIVE = "ARCHIVE"


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


class CloudStorage:
    """Google Cloud Storage client for Raptorflow."""

    def __init__(self, config: Optional[StorageConfig] = None):
        self.config = config or StorageConfig.from_env()
        self.gcp_client = get_gcp_client()
        self.logger = logging.getLogger("cloud_storage")

        # Get storage client
        self.client = self.gcp_client.get_storage_client()

        if not self.client:
            raise RuntimeError("Storage client not available")

        # Get bucket
        self.bucket = self.client.bucket(self.config.bucket_name)

        # Initialize bucket if needed
        self._ensure_bucket_exists()
        self._configure_bucket()

    def _ensure_bucket_exists(self):
        """Ensure bucket exists."""
        try:
            self.bucket.reload()
            self.logger.info(f"Using existing bucket: {self.config.bucket_name}")
        except exceptions.NotFound:
            try:
                # Create bucket
                self.bucket = self.client.create_bucket(
                    self.config.bucket_name, location=self.gcp_client.get_region()
                )
                self.logger.info(f"Created new bucket: {self.config.bucket_name}")
            except Exception as e:
                self.logger.error(f"Failed to create bucket: {e}")
                raise

    def _configure_bucket(self):
        """Configure bucket settings."""
        try:
            # Enable versioning
            if self.config.enable_versioning:
                self.bucket.versioning_enabled = True
                self.bucket.patch()

            # Set lifecycle rules
            if self.config.enable_lifecycle:
                self._set_lifecycle_rules()

        except Exception as e:
            self.logger.warning(f"Failed to configure bucket: {e}")

    def _set_lifecycle_rules(self):
        """Set bucket lifecycle rules."""
        try:
            # Add rule to delete objects after retention period
            lifecycle_rule = {
                "action": {"type": "Delete"},
                "condition": {"age": self.config.retention_days},
            }

            lifecycle_rules = [lifecycle_rule]
            self.bucket.lifecycle_rules = lifecycle_rules
            self.bucket.patch()

            self.logger.info(
                f"Set lifecycle rule: delete after {self.config.retention_days} days"
            )

        except Exception as e:
            self.logger.warning(f"Failed to set lifecycle rules: {e}")

    def _generate_object_name(
        self, workspace_id: str, category: FileCategory, filename: str
    ) -> str:
        """Generate object name for storage."""
        # Sanitize filename
        safe_filename = "".join(c for c in filename if c.isalnum() or c in "._-")

        # Generate unique ID
        unique_id = str(uuid.uuid4())

        # Create object path
        object_name = f"{workspace_id}/{category.value}/{unique_id}_{safe_filename}"

        return object_name

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
        storage_class: Optional[StorageClass] = None,
        is_public: bool = False,
        expires_at: Optional[datetime] = None,
        custom_metadata: Optional[Dict[str, str]] = None,
    ) -> UploadResult:
        """Upload file to Cloud Storage."""
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

            # Generate file ID and object name
            file_id = str(uuid.uuid4())
            object_name = self._generate_object_name(workspace_id, category, filename)

            # Calculate checksum
            if isinstance(content, bytes):
                checksum = self._calculate_checksum(content)
            else:
                # For file-like objects, read content to calculate checksum
                current_pos = content.tell()
                content_bytes = content.read()
                checksum = self._calculate_checksum(content_bytes)
                content.seek(current_pos)  # Reset position

            # Create blob
            blob = self.bucket.blob(object_name)

            # Set storage class
            if storage_class:
                blob.storage_class = storage_class.value
            else:
                blob.storage_class = self.config.default_storage_class.value

            # Set metadata
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

            blob.metadata = metadata

            # Upload file
            retry = Retry(initial=1.0, maximum=3.0, multiplier=2.0)

            if isinstance(content, bytes):
                blob.upload_from_string(
                    content,
                    content_type=content_type,
                    timeout=self.config.upload_timeout,
                    retry=retry,
                )
            else:
                blob.upload_from_file(
                    content,
                    content_type=content_type,
                    timeout=self.config.upload_timeout,
                    retry=retry,
                )

            # Get generation
            generation = blob.generation

            # Create download URL
            download_url = None
            if is_public:
                blob.make_public()
                download_url = blob.public_url
            else:
                # Generate signed URL
                download_url = blob.generate_signed_url(
                    version="v4", expiration=timedelta(hours=1), method="GET"
                )

            # Create metadata object
            file_metadata = FileMetadata(
                file_id=file_id,
                filename=filename,
                content_type=content_type,
                size_bytes=size_bytes,
                workspace_id=workspace_id,
                user_id=user_id,
                category=category,
                bucket_name=self.config.bucket_name,
                object_name=object_name,
                storage_class=storage_class or self.config.default_storage_class,
                generation=generation,
                expires_at=expires_at,
                checksum=checksum,
                is_public=is_public,
                download_url=download_url,
                custom_metadata=custom_metadata or {},
            )

            self.logger.info(
                f"Uploaded file: {filename} ({size_bytes} bytes) to {object_name}"
            )

            return UploadResult(
                success=True,
                file_id=file_id,
                object_name=object_name,
                size_bytes=size_bytes,
                download_url=download_url,
                metadata=file_metadata,
            )

        except Exception as e:
            self.logger.error(f"Failed to upload file {filename}: {e}")
            return UploadResult(success=False, error_message=str(e))

    async def download_file(
        self, file_id: str, workspace_id: Optional[str] = None
    ) -> DownloadResult:
        """Download file from Cloud Storage."""
        try:
            # Find file by file_id
            blob = self._find_blob_by_file_id(file_id, workspace_id)

            if not blob:
                return DownloadResult(
                    success=False, error_message=f"File {file_id} not found"
                )

            # Download content
            retry = Retry(initial=1.0, maximum=3.0, multiplier=2.0)
            content = blob.download_as_bytes(
                timeout=self.config.download_timeout, retry=retry
            )

            # Get metadata
            metadata = blob.metadata or {}

            # Create file metadata object
            file_metadata = FileMetadata(
                file_id=metadata.get("file_id", file_id),
                filename=metadata.get("filename", ""),
                content_type=metadata.get("content_type", ""),
                size_bytes=int(metadata.get("size_bytes", 0)),
                workspace_id=metadata.get("workspace_id", ""),
                user_id=metadata.get("user_id", ""),
                category=FileCategory(metadata.get("category", "uploads")),
                bucket_name=self.config.bucket_name,
                object_name=blob.name,
                storage_class=(
                    StorageClass(blob.storage_class)
                    if blob.storage_class
                    else StorageClass.STANDARD
                ),
                generation=str(blob.generation) if blob.generation else None,
                checksum=metadata.get("checksum"),
                is_public=metadata.get("is_public", "false").lower() == "true",
                download_url=blob.public_url if blob.public_url else None,
                custom_metadata={
                    k: v
                    for k, v in metadata.items()
                    if k
                    not in [
                        "file_id",
                        "filename",
                        "content_type",
                        "size_bytes",
                        "workspace_id",
                        "user_id",
                        "category",
                        "checksum",
                        "is_public",
                    ]
                },
            )

            # Verify checksum if available
            if file_metadata.checksum:
                calculated_checksum = self._calculate_checksum(content)
                if calculated_checksum != file_metadata.checksum:
                    self.logger.warning(f"Checksum mismatch for file {file_id}")

            self.logger.info(
                f"Downloaded file: {file_metadata.filename} ({len(content)} bytes)"
            )

            return DownloadResult(
                success=True,
                content=content,
                filename=file_metadata.filename,
                content_type=file_metadata.content_type,
                size_bytes=len(content),
                metadata=file_metadata,
            )

        except Exception as e:
            self.logger.error(f"Failed to download file {file_id}: {e}")
            return DownloadResult(success=False, error_message=str(e))

    def _find_blob_by_file_id(
        self, file_id: str, workspace_id: Optional[str] = None
    ) -> Optional[storage.Blob]:
        """Find blob by file ID."""
        try:
            # Search for blob with matching metadata
            prefix = f"{workspace_id}/" if workspace_id else ""

            for blob in self.client.list_blobs(self.bucket, prefix=prefix):
                if blob.metadata and blob.metadata.get("file_id") == file_id:
                    return blob

            return None

        except Exception as e:
            self.logger.error(f"Failed to find blob by file_id {file_id}: {e}")
            return None

    async def delete_file(
        self, file_id: str, workspace_id: Optional[str] = None
    ) -> bool:
        """Delete file from Cloud Storage."""
        try:
            # Find blob by file_id
            blob = self._find_blob_by_file_id(file_id, workspace_id)

            if not blob:
                self.logger.warning(f"File {file_id} not found for deletion")
                return False

            # Delete blob
            blob.delete()

            self.logger.info(f"Deleted file: {file_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to delete file {file_id}: {e}")
            return False

    async def list_files(
        self,
        workspace_id: str,
        category: Optional[FileCategory] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[FileMetadata]:
        """List files in workspace."""
        try:
            # Build prefix
            prefix = f"{workspace_id}/"
            if category:
                prefix += f"{category.value}/"

            # List blobs
            blobs = list(
                self.client.list_blobs(
                    self.bucket, prefix=prefix, max_results=limit + offset
                )
            )

            # Convert to metadata objects
            files = []
            for blob in blobs[offset:]:
                if blob.metadata:
                    metadata = FileMetadata(
                        file_id=blob.metadata.get("file_id", ""),
                        filename=blob.metadata.get("filename", ""),
                        content_type=blob.metadata.get("content_type", ""),
                        size_bytes=int(blob.metadata.get("size_bytes", 0)),
                        workspace_id=blob.metadata.get("workspace_id", ""),
                        user_id=blob.metadata.get("user_id", ""),
                        category=FileCategory(blob.metadata.get("category", "uploads")),
                        bucket_name=self.config.bucket_name,
                        object_name=blob.name,
                        storage_class=(
                            StorageClass(blob.storage_class)
                            if blob.storage_class
                            else StorageClass.STANDARD
                        ),
                        generation=str(blob.generation) if blob.generation else None,
                        checksum=blob.metadata.get("checksum"),
                        is_public=blob.metadata.get("is_public", "false").lower()
                        == "true",
                        download_url=blob.public_url if blob.public_url else None,
                        custom_metadata={
                            k: v
                            for k, v in (blob.metadata or {}).items()
                            if k
                            not in [
                                "file_id",
                                "filename",
                                "content_type",
                                "size_bytes",
                                "workspace_id",
                                "user_id",
                                "category",
                                "checksum",
                                "is_public",
                            ]
                        },
                    )
                    files.append(metadata)

            return files

        except Exception as e:
            self.logger.error(f"Failed to list files for workspace {workspace_id}: {e}")
            return []

    async def get_file_info(
        self, file_id: str, workspace_id: Optional[str] = None
    ) -> Optional[FileMetadata]:
        """Get file information."""
        try:
            # Find blob by file_id
            blob = self._find_blob_by_file_id(file_id, workspace_id)

            if not blob:
                return None

            # Get metadata
            metadata = blob.metadata or {}

            return FileMetadata(
                file_id=metadata.get("file_id", file_id),
                filename=metadata.get("filename", ""),
                content_type=metadata.get("content_type", ""),
                size_bytes=int(metadata.get("size_bytes", 0)),
                workspace_id=metadata.get("workspace_id", ""),
                user_id=metadata.get("user_id", ""),
                category=FileCategory(metadata.get("category", "uploads")),
                bucket_name=self.config.bucket_name,
                object_name=blob.name,
                storage_class=(
                    StorageClass(blob.storage_class)
                    if blob.storage_class
                    else StorageClass.STANDARD
                ),
                generation=str(blob.generation) if blob.generation else None,
                checksum=metadata.get("checksum"),
                is_public=metadata.get("is_public", "false").lower() == "true",
                download_url=blob.public_url if blob.public_url else None,
                custom_metadata={
                    k: v
                    for k, v in metadata.items()
                    if k
                    not in [
                        "file_id",
                        "filename",
                        "content_type",
                        "size_bytes",
                        "workspace_id",
                        "user_id",
                        "category",
                        "checksum",
                        "is_public",
                    ]
                },
            )

        except Exception as e:
            self.logger.error(f"Failed to get file info {file_id}: {e}")
            return None

    async def generate_download_url(
        self,
        file_id: str,
        workspace_id: Optional[str] = None,
        expiration_hours: int = 1,
    ) -> Optional[str]:
        """Generate signed download URL."""
        try:
            # Find blob by file_id
            blob = self._find_blob_by_file_id(file_id, workspace_id)

            if not blob:
                return None

            # Generate signed URL
            url = blob.generate_signed_url(
                version="v4", expiration=timedelta(hours=expiration_hours), method="GET"
            )

            return url

        except Exception as e:
            self.logger.error(f"Failed to generate download URL for {file_id}: {e}")
            return None

    async def get_workspace_usage(self, workspace_id: str) -> Dict[str, Any]:
        """Get storage usage statistics for workspace."""
        try:
            # List all blobs in workspace
            prefix = f"{workspace_id}/"
            blobs = list(self.client.list_blobs(self.bucket, prefix=prefix))

            total_size = 0
            file_count = 0
            category_counts = {}
            storage_class_counts = {}

            for blob in blobs:
                if blob.metadata:
                    file_count += 1
                    total_size += blob.size or 0

                    # Count by category
                    category = blob.metadata.get("category", "uploads")
                    category_counts[category] = category_counts.get(category, 0) + 1

                    # Count by storage class
                    storage_class = blob.storage_class or "STANDARD"
                    storage_class_counts[storage_class] = (
                        storage_class_counts.get(storage_class, 0) + 1
                    )

            return {
                "workspace_id": workspace_id,
                "total_size_bytes": total_size,
                "total_size_mb": total_size / (1024 * 1024),
                "file_count": file_count,
                "category_counts": category_counts,
                "storage_class_counts": storage_class_counts,
            }

        except Exception as e:
            self.logger.error(f"Failed to get workspace usage for {workspace_id}: {e}")
            return {}

    async def cleanup_expired_files(self) -> int:
        """Clean up expired files."""
        try:
            cleaned_count = 0

            # List all blobs
            for blob in self.client.list_blobs(self.bucket):
                if blob.metadata:
                    expires_at_str = blob.metadata.get("expires_at")
                    if expires_at_str:
                        expires_at = datetime.fromisoformat(expires_at_str)
                        if expires_at < datetime.now():
                            blob.delete()
                            cleaned_count += 1

            self.logger.info(f"Cleaned up {cleaned_count} expired files")
            return cleaned_count

        except Exception as e:
            self.logger.error(f"Failed to cleanup expired files: {e}")
            return 0

    def get_bucket_info(self) -> Dict[str, Any]:
        """Get bucket information."""
        try:
            self.bucket.reload()

            return {
                "name": self.bucket.name,
                "location": self.bucket.location,
                "storage_class": self.bucket.storage_class,
                "versioning_enabled": self.bucket.versioning_enabled,
                "lifecycle_rules": (
                    len(self.bucket.lifecycle_rules)
                    if self.bucket.lifecycle_rules
                    else 0
                ),
                "time_created": (
                    self.bucket.time_created.isoformat()
                    if self.bucket.time_created
                    else None
                ),
            }

        except Exception as e:
            self.logger.error(f"Failed to get bucket info: {e}")
            return {}


# Global storage instance
_cloud_storage: Optional[CloudStorage] = None


def get_cloud_storage(config: Optional[StorageConfig] = None) -> CloudStorage:
    """Get global Cloud Storage instance."""
    global _cloud_storage
    if _cloud_storage is None:
        _cloud_storage = CloudStorage(config)
    return _cloud_storage


def initialize_cloud_storage(config: StorageConfig) -> CloudStorage:
    """Initialize Cloud Storage with configuration."""
    global _cloud_storage
    _cloud_storage = CloudStorage(config)
    return _cloud_storage


# Convenience functions
async def upload_file(
    content: Union[bytes, BinaryIO],
    filename: str,
    workspace_id: str,
    user_id: str,
    category: FileCategory = FileCategory.UPLOADS,
    **kwargs,
) -> UploadResult:
    """Upload file to Cloud Storage."""
    storage = get_cloud_storage()
    return await storage.upload_file(
        content, filename, workspace_id, user_id, category, **kwargs
    )


async def download_file(
    file_id: str, workspace_id: Optional[str] = None
) -> DownloadResult:
    """Download file from Cloud Storage."""
    storage = get_cloud_storage()
    return await storage.download_file(file_id, workspace_id)


async def delete_file(file_id: str, workspace_id: Optional[str] = None) -> bool:
    """Delete file from Cloud Storage."""
    storage = get_cloud_storage()
    return await storage.delete_file(file_id, workspace_id)


async def list_files(
    workspace_id: str,
    category: Optional[FileCategory] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[FileMetadata]:
    """List files in workspace."""
    storage = get_cloud_storage()
    return await storage.list_files(workspace_id, category, limit, offset)
