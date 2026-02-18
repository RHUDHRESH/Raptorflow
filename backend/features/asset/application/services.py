"""
Asset application services.
"""

import re
import uuid
from typing import Any, Dict, Optional, Tuple

from backend.features.asset.application.ports import AssetRepository, StorageService
from backend.features.asset.domain.entities import Asset, AssetType


_INVALID_FILENAME = re.compile(r"[^a-zA-Z0-9._-]+")


class AssetService:
    """Application service for asset operations."""

    def __init__(
        self,
        repository: AssetRepository,
        storage: StorageService,
        storage_bucket: str = "uploads",
    ):
        self._repository = repository
        self._storage = storage
        self._bucket = storage_bucket

    async def create_upload_session(
        self,
        workspace_id: str,
        original_name: str,
        mime_type: str,
        size_bytes: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Asset, Dict[str, str]]:
        """Create an upload session and return asset record and upload info."""
        await self._ensure_bucket()

        filename, storage_path = self._build_storage_path(workspace_id, original_name)
        signed = await self._storage.create_signed_upload_url(
            self._bucket, storage_path
        )
        if not signed:
            raise RuntimeError("Failed to create signed upload URL")

        asset_type = Asset.infer_type(mime_type)

        asset = Asset(
            id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            filename=filename,
            original_name=original_name,
            mime_type=mime_type,
            size_bytes=size_bytes,
            storage_path=storage_path,
            public_url=self._storage.get_public_url(self._bucket, storage_path),
            asset_type=asset_type,
            metadata=self._merge_metadata(metadata, {"status": "pending"}),
        )

        saved_asset = await self._repository.save(asset)

        upload = {
            "signed_url": signed["signed_url"],
            "token": signed["token"],
            "path": signed["path"],
            "bucket": self._bucket,
        }

        return saved_asset, upload

    async def confirm_upload(
        self,
        workspace_id: str,
        asset_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Asset]:
        """Confirm an upload and update asset status."""
        asset = await self._repository.get_by_id(asset_id, workspace_id)
        if not asset:
            return None

        merged_metadata = self._merge_metadata(asset.metadata, metadata)
        merged_metadata["status"] = "uploaded"
        asset.metadata = merged_metadata

        return await self._repository.save(asset)

    async def list_assets(
        self,
        workspace_id: str,
        limit: int = 50,
        offset: int = 0,
        asset_type: Optional[AssetType] = None,
    ) -> Tuple[list[Asset], int]:
        """List assets for a workspace."""
        return await self._repository.list_by_workspace(
            workspace_id, limit, offset, asset_type
        )

    async def get_asset(self, workspace_id: str, asset_id: str) -> Optional[Asset]:
        """Get a specific asset."""
        return await self._repository.get_by_id(asset_id, workspace_id)

    async def delete_asset(self, workspace_id: str, asset_id: str) -> bool:
        """Delete an asset."""
        return await self._repository.delete(asset_id, workspace_id)

    async def _ensure_bucket(self) -> None:
        """Ensure the storage bucket exists."""
        if not await self._storage.create_bucket(self._bucket, public=True):
            raise RuntimeError(f"Failed to ensure storage bucket '{self._bucket}'")

    def _build_storage_path(
        self, workspace_id: str, original_name: str
    ) -> Tuple[str, str]:
        """Build the storage path for an asset."""
        safe_name = self._safe_filename(original_name)
        storage_path = f"{workspace_id}/{uuid.uuid4()}/{safe_name}"
        return safe_name, storage_path

    @staticmethod
    def _safe_filename(original_name: str) -> str:
        """Make a filename safe."""
        candidate = _INVALID_FILENAME.sub("_", original_name.strip())
        return candidate[:180] if candidate else f"asset_{uuid.uuid4().hex[:8]}"

    @staticmethod
    def _merge_metadata(
        base: Optional[Dict[str, Any]], patch: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Merge metadata dictionaries."""
        merged = dict(base or {})
        if patch:
            merged.update(patch)
        return merged
