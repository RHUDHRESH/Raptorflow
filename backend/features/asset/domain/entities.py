"""
Asset domain entities.

Pure Python business objects for asset management.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional
from enum import Enum


class AssetType(str, Enum):
    """Asset type enumeration."""

    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"


@dataclass
class Asset:
    """
    Asset domain entity.

    Represents a file uploaded to the system.
    """

    id: str
    workspace_id: str
    filename: str
    original_name: str
    mime_type: str
    size_bytes: int
    storage_path: str
    public_url: Optional[str] = None
    asset_type: AssetType = AssetType.DOCUMENT
    metadata: Dict[str, Any] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    @classmethod
    def infer_type(cls, mime_type: str) -> "AssetType":
        """Infer asset type from MIME type."""
        lower = mime_type.lower()
        if lower.startswith("image/"):
            return AssetType.IMAGE
        if lower.startswith("video/"):
            return AssetType.VIDEO
        if lower.startswith("audio/"):
            return AssetType.AUDIO
        return AssetType.DOCUMENT

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for persistence."""
        return {
            "id": self.id,
            "workspace_id": self.workspace_id,
            "filename": self.filename,
            "original_name": self.original_name,
            "mime_type": self.mime_type,
            "size_bytes": self.size_bytes,
            "storage_path": self.storage_path,
            "public_url": self.public_url,
            "asset_type": self.asset_type.value
            if isinstance(self.asset_type, AssetType)
            else self.asset_type,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Asset":
        """Create from dictionary (e.g., from database)."""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))

        updated_at = data.get("updated_at")
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))

        asset_type = data.get("asset_type", "document")
        if isinstance(asset_type, str):
            asset_type = AssetType(asset_type)

        return cls(
            id=data["id"],
            workspace_id=data["workspace_id"],
            filename=data["filename"],
            original_name=data["original_name"],
            mime_type=data["mime_type"],
            size_bytes=int(data["size_bytes"]),
            storage_path=data["storage_path"],
            public_url=data.get("public_url"),
            asset_type=asset_type,
            metadata=data.get("metadata") or {},
            created_at=created_at,
            updated_at=updated_at,
        )
