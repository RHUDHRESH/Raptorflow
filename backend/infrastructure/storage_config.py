"""
Storage bucket configurations for Raptorflow.

Defines bucket names, configurations, and access patterns
for different types of stored data.
"""

import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

from .gcp import StorageClass


class BucketType(Enum):
    """Bucket types for different storage needs."""

    EVIDENCE = "evidence"
    EXPORTS = "exports"
    ASSETS = "assets"
    BACKUPS = "backups"
    LOGS = "logs"
    TEMP = "temp"
    DOCUMENTS = "documents"
    MEDIA = "media"


@dataclass
class BucketConfig:
    """Configuration for a storage bucket."""

    bucket_name: str
    bucket_type: BucketType
    storage_class: StorageClass
    retention_days: int
    enable_versioning: bool
    enable_lifecycle: bool
    public_access: bool = False

    # Access control
    allowed_roles: list[str] = None
    blocked_roles: list[str] = None

    # Performance settings
    chunk_size: int = 8 * 1024 * 1024  # 8MB
    max_file_size: int = 5 * 1024 * 1024 * 1024  # 5GB

    # Security settings
    allowed_mime_types: list[str] = None
    blocked_mime_types: list[str] = None
    require_authentication: bool = True

    # Lifecycle rules
    auto_delete_days: Optional[int] = None
    transition_to_nearline_days: Optional[int] = None
    transition_to_coldline_days: Optional[int] = None
    transition_to_archive_days: Optional[int] = None

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.bucket_type, str):
            self.bucket_type = BucketType(self.bucket_type)
        if isinstance(self.storage_class, str):
            self.storage_class = StorageClass(self.storage_class)

        if self.allowed_roles is None:
            self.allowed_roles = []
        if self.blocked_roles is None:
            self.blocked_roles = []
        if self.allowed_mime_types is None:
            self.allowed_mime_types = []
        if self.blocked_mime_types is None:
            self.blocked_mime_types = []


class StorageBucketConfig:
    """Storage bucket configuration manager."""

    def __init__(self):
        self.project_id = os.getenv("GCP_PROJECT_ID", "")
        self.region = os.getenv("GCP_REGION", "us-central1")

        # Bucket configurations
        self.buckets: Dict[str, BucketConfig] = {}
        self._setup_default_buckets()

    def _setup_default_buckets(self):
        """Setup default bucket configurations."""

        # Evidence bucket - for user uploaded files
        self.buckets["evidence"] = BucketConfig(
            bucket_name=os.getenv("EVIDENCE_BUCKET", f"{self.project_id}-evidence"),
            bucket_type=BucketType.EVIDENCE,
            storage_class=StorageClass.STANDARD,
            retention_days=365,  # 1 year retention
            enable_versioning=True,
            enable_lifecycle=True,
            public_access=False,
            allowed_roles=["user", "admin", "agent"],
            blocked_roles=[],
            require_authentication=True,
            auto_delete_days=365,
            transition_to_nearline_days=30,
            transition_to_coldline_days=90,
            transition_to_archive_days=365,
        )

        # Exports bucket - for generated exports
        self.buckets["exports"] = BucketConfig(
            bucket_name=os.getenv("EXPORTS_BUCKET", f"{self.project_id}-exports"),
            bucket_type=BucketType.EXPORTS,
            storage_class=StorageClass.STANDARD,
            retention_days=90,  # 90 days retention
            enable_versioning=True,
            enable_lifecycle=True,
            public_access=False,
            allowed_roles=["user", "admin", "agent"],
            blocked_roles=[],
            require_authentication=True,
            auto_delete_days=90,
            transition_to_nearline_days=7,
            transition_to_coldline_days=30,
            transition_to_archive_days=90,
        )

        # Assets bucket - for muse assets and static content
        self.buckets["assets"] = BucketConfig(
            bucket_name=os.getenv("ASSETS_BUCKET", f"{self.project_id}-assets"),
            bucket_type=BucketType.ASSETS,
            storage_class=StorageClass.STANDARD,
            retention_days=-1,  # Permanent
            enable_versioning=True,
            enable_lifecycle=False,
            public_access=True,  # Public for CDN access
            allowed_roles=["user", "admin", "agent", "public"],
            blocked_roles=[],
            require_authentication=False,
            auto_delete_days=None,
            transition_to_nearline_days=90,
            transition_to_coldline_days=365,
            transition_to_archive_days=None,
        )

        # Backups bucket - for database and Redis backups
        self.buckets["backups"] = BucketConfig(
            bucket_name=os.getenv("BACKUPS_BUCKET", f"{self.project_id}-backups"),
            bucket_type=BucketType.BACKUPS,
            storage_class=StorageClass.NEARLINE,
            retention_days=365,  # 1 year retention
            enable_versioning=True,
            enable_lifecycle=True,
            public_access=False,
            allowed_roles=["admin", "system"],
            blocked_roles=["user"],
            require_authentication=True,
            auto_delete_days=365,
            transition_to_coldline_days=30,
            transition_to_archive_days=90,
            allowed_mime_types=[
                "application/gzip",
                "application/json",
                "application/sql",
            ],
        )

        # Logs bucket - for application logs
        self.buckets["logs"] = BucketConfig(
            bucket_name=os.getenv("LOGS_BUCKET", f"{self.project_id}-logs"),
            bucket_type=BucketType.LOGS,
            storage_class=StorageClass.COLDLINE,
            retention_days=90,  # 90 days retention
            enable_versioning=False,
            enable_lifecycle=True,
            public_access=False,
            allowed_roles=["admin", "system"],
            blocked_roles=["user"],
            require_authentication=True,
            auto_delete_days=90,
            transition_to_archive_days=30,
            allowed_mime_types=["text/plain", "application/json", "application/gzip"],
        )

        # Temp bucket - for temporary files
        self.buckets["temp"] = BucketConfig(
            bucket_name=os.getenv("TEMP_BUCKET", f"{self.project_id}-temp"),
            bucket_type=BucketType.TEMP,
            storage_class=StorageClass.STANDARD,
            retention_days=1,  # 1 day retention
            enable_versioning=False,
            enable_lifecycle=True,
            public_access=False,
            allowed_roles=["user", "admin", "agent", "system"],
            blocked_roles=[],
            require_authentication=True,
            auto_delete_days=1,
            max_file_size=100 * 1024 * 1024,  # 100MB limit for temp files
        )

        # Documents bucket - for user documents
        self.buckets["documents"] = BucketConfig(
            bucket_name=os.getenv("DOCUMENTS_BUCKET", f"{self.project_id}-documents"),
            bucket_type=BucketType.DOCUMENTS,
            storage_class=StorageClass.STANDARD,
            retention_days=365,  # 1 year retention
            enable_versioning=True,
            enable_lifecycle=True,
            public_access=False,
            allowed_roles=["user", "admin", "agent"],
            blocked_roles=[],
            require_authentication=True,
            auto_delete_days=365,
            transition_to_nearline_days=30,
            transition_to_coldline_days=90,
            transition_to_archive_days=365,
            allowed_mime_types=[
                "application/pdf",
                "application/msword",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "application/vnd.ms-excel",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/vnd.ms-powerpoint",
                "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                "text/plain",
                "text/csv",
                "image/jpeg",
                "image/png",
                "image/gif",
                "image/webp",
            ],
        )

        # Media bucket - for media files
        self.buckets["media"] = BucketConfig(
            bucket_name=os.getenv("MEDIA_BUCKET", f"{self.project_id}-media"),
            bucket_type=BucketType.MEDIA,
            storage_class=StorageClass.STANDARD,
            retention_days=365,  # 1 year retention
            enable_versioning=True,
            enable_lifecycle=True,
            public_access=False,
            allowed_roles=["user", "admin", "agent"],
            blocked_roles=[],
            require_authentication=True,
            auto_delete_days=365,
            transition_to_nearline_days=7,
            transition_to_coldline_days=30,
            transition_to_archive_days=365,
            allowed_mime_types=[
                "image/jpeg",
                "image/png",
                "image/gif",
                "image/webp",
                "image/svg+xml",
                "video/mp4",
                "video/webm",
                "video/quicktime",
                "audio/mpeg",
                "audio/wav",
                "audio/ogg",
                "audio/mp4",
            ],
        )

    def get_bucket_config(self, bucket_type: str) -> Optional[BucketConfig]:
        """Get bucket configuration by type."""
        return self.buckets.get(bucket_type)

    def get_bucket_name(self, bucket_type: str) -> Optional[str]:
        """Get bucket name by type."""
        config = self.get_bucket_config(bucket_type)
        return config.bucket_name if config else None

    def get_all_bucket_configs(self) -> Dict[str, BucketConfig]:
        """Get all bucket configurations."""
        return self.buckets.copy()

    def get_public_buckets(self) -> Dict[str, BucketConfig]:
        """Get all public buckets."""
        return {k: v for k, v in self.buckets.items() if v.public_access}

    def get_private_buckets(self) -> Dict[str, BucketConfig]:
        """Get all private buckets."""
        return {k: v for k, v in self.buckets.items() if not v.public_access}

    def get_buckets_by_role(self, role: str) -> Dict[str, BucketConfig]:
        """Get buckets accessible by role."""
        accessible = {}

        for bucket_type, config in self.buckets.items():
            if role in config.allowed_roles and role not in config.blocked_roles:
                accessible[bucket_type] = config

        return accessible

    def validate_bucket_access(self, bucket_type: str, role: str) -> bool:
        """Validate if role can access bucket type."""
        config = self.get_bucket_config(bucket_type)

        if not config:
            return False

        if role in config.blocked_roles:
            return False

        if role in config.allowed_roles:
            return True

        return False

    def get_bucket_for_file_type(self, mime_type: str) -> Optional[str]:
        """Get appropriate bucket type for file MIME type."""
        for bucket_type, config in self.buckets.items():
            if config.allowed_mime_types:
                if mime_type in config.allowed_mime_types:
                    return bucket_type

        # Default to evidence bucket
        return "evidence"

    def get_storage_class_for_bucket(self, bucket_type: str) -> Optional[StorageClass]:
        """Get storage class for bucket type."""
        config = self.get_bucket_config(bucket_type)
        return config.storage_class if config else None

    def get_retention_days_for_bucket(self, bucket_type: str) -> int:
        """Get retention days for bucket type."""
        config = self.get_bucket_config(bucket_type)
        return config.retention_days if config else 0

    def add_bucket_config(self, bucket_type: str, config: BucketConfig):
        """Add or update bucket configuration."""
        self.buckets[bucket_type] = config

    def remove_bucket_config(self, bucket_type: str):
        """Remove bucket configuration."""
        if bucket_type in self.buckets:
            del self.buckets[bucket_type]

    def update_bucket_config(self, bucket_type: str, **kwargs):
        """Update bucket configuration."""
        config = self.get_bucket_config(bucket_type)
        if config:
            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)

    def export_config(self) -> Dict[str, Any]:
        """Export all bucket configurations."""
        return {
            bucket_type: {
                "bucket_name": config.bucket_name,
                "bucket_type": config.bucket_type.value,
                "storage_class": config.storage_class.value,
                "retention_days": config.retention_days,
                "enable_versioning": config.enable_versioning,
                "enable_lifecycle": config.enable_lifecycle,
                "public_access": config.public_access,
                "allowed_roles": config.allowed_roles,
                "blocked_roles": config.blocked_roles,
                "chunk_size": config.chunk_size,
                "max_file_size": config.max_file_size,
                "allowed_mime_types": config.allowed_mime_types,
                "blocked_mime_types": config.blocked_mime_types,
                "require_authentication": config.require_authentication,
                "auto_delete_days": config.auto_delete_days,
                "transition_to_nearline_days": config.transition_to_nearline_days,
                "transition_to_coldline_days": config.transition_to_coldline_days,
                "transition_to_archive_days": config.transition_to_archive_days,
            }
            for bucket_type, config in self.buckets.items()
        }

    def import_config(self, config_data: Dict[str, Any]):
        """Import bucket configurations."""
        for bucket_type, data in config_data.items():
            config = BucketConfig(
                bucket_name=data["bucket_name"],
                bucket_type=BucketType(data["bucket_type"]),
                storage_class=StorageClass(data["storage_class"]),
                retention_days=data["retention_days"],
                enable_versioning=data["enable_versioning"],
                enable_lifecycle=data["enable_lifecycle"],
                public_access=data["public_access"],
                allowed_roles=data["allowed_roles"],
                blocked_roles=data["blocked_roles"],
                chunk_size=data["chunk_size"],
                max_file_size=data["max_file_size"],
                allowed_mime_types=data["allowed_mime_types"],
                blocked_mime_types=data["blocked_mime_types"],
                require_authentication=data["require_authentication"],
                auto_delete_days=data["auto_delete_days"],
                transition_to_nearline_days=data["transition_to_nearline_days"],
                transition_to_coldline_days=data["transition_to_coldline_days"],
                transition_to_archive_days=data["transition_to_archive_days"],
            )
            self.buckets[bucket_type] = config

    def validate_config(self) -> list[str]:
        """Validate bucket configurations."""
        errors = []

        for bucket_type, config in self.buckets.items():
            # Check bucket name
            if not config.bucket_name:
                errors.append(f"Bucket {bucket_type}: bucket_name is required")

            # Check retention days
            if config.retention_days < -1:
                errors.append(f"Bucket {bucket_type}: retention_days must be >= -1")

            # Check file size
            if config.max_file_size <= 0:
                errors.append(f"Bucket {bucket_type}: max_file_size must be > 0")

            # Check chunk size
            if config.chunk_size <= 0:
                errors.append(f"Bucket {bucket_type}: chunk_size must be > 0")

            # Check lifecycle rules
            if (
                config.enable_lifecycle
                and not config.auto_delete_days
                and not any(
                    [
                        config.transition_to_nearline_days,
                        config.transition_to_coldline_days,
                        config.transition_to_archive_days,
                    ]
                )
            ):
                errors.append(
                    f"Bucket {bucket_type}: lifecycle enabled but no rules defined"
                )

        return errors

    def get_bucket_summary(self) -> Dict[str, Any]:
        """Get summary of all buckets."""
        summary = {
            "total_buckets": len(self.buckets),
            "public_buckets": len(self.get_public_buckets()),
            "private_buckets": len(self.get_private_buckets()),
            "buckets_by_type": {},
            "storage_classes": {},
            "retention_periods": {},
        }

        for bucket_type, config in self.buckets.items():
            # Count by bucket type
            bucket_type_name = config.bucket_type.value
            summary["buckets_by_type"][bucket_type_name] = (
                summary["buckets_by_type"].get(bucket_type_name, 0) + 1
            )

            # Count by storage class
            storage_class = config.storage_class.value
            summary["storage_classes"][storage_class] = (
                summary["storage_classes"].get(storage_class, 0) + 1
            )

            # Count by retention period
            retention = config.retention_days
            if retention == -1:
                retention_key = "permanent"
            elif retention == 0:
                retention_key = "no_retention"
            elif retention < 30:
                retention_key = "short_term"
            elif retention < 365:
                retention_key = "medium_term"
            else:
                retention_key = "long_term"

            summary["retention_periods"][retention_key] = (
                summary["retention_periods"].get(retention_key, 0) + 1
            )

        return summary


# Global bucket configuration instance
_bucket_config: Optional[StorageBucketConfig] = None


def get_bucket_config() -> StorageBucketConfig:
    """Get global bucket configuration instance."""
    global _bucket_config
    if _bucket_config is None:
        _bucket_config = StorageBucketConfig()
    return _bucket_config


def initialize_bucket_config(project_id: str, region: str) -> StorageBucketConfig:
    """Initialize bucket configuration with project details."""
    global _bucket_config
    _bucket_config = StorageBucketConfig()
    _bucket_config.project_id = project_id
    _bucket_config.region = region
    return _bucket_config


# Convenience functions
def get_evidence_bucket() -> str:
    """Get evidence bucket name."""
    return get_bucket_config().get_bucket_name("evidence")


def get_exports_bucket() -> str:
    """Get exports bucket name."""
    return get_bucket_config().get_bucket_name("exports")


def get_assets_bucket() -> str:
    """Get assets bucket name."""
    return get_bucket_config().get_bucket_name("assets")


def get_backups_bucket() -> str:
    """Get backups bucket name."""
    return get_bucket_config().get_bucket_name("backups")


def get_logs_bucket() -> str:
    """Get logs bucket name."""
    return get_bucket_config().get_bucket_name("logs")


def get_temp_bucket() -> str:
    """Get temp bucket name."""
    return get_bucket_config().get_bucket_name("temp")


def get_documents_bucket() -> str:
    """Get documents bucket name."""
    return get_bucket_config().get_bucket_name("documents")


def get_media_bucket() -> str:
    """Get media bucket name."""
    return get_bucket_config().get_bucket_name("media")


def validate_bucket_access(bucket_type: str, role: str) -> bool:
    """Validate bucket access for role."""
    return get_bucket_config().validate_bucket_access(bucket_type, role)


def get_bucket_for_file_type(mime_type: str) -> Optional[str]:
    """Get appropriate bucket for file type."""
    return get_bucket_config().get_bucket_for_file_type(mime_type)
