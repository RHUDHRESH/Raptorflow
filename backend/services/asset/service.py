"""Asset service for Supabase-backed upload metadata and storage paths."""

from __future__ import annotations

import re
from typing import Any, Dict, Optional, Tuple
from uuid import uuid4

from supabase import Client

from backend.infrastructure.storage.manager import StorageManager
from backend.schemas.asset import AssetRecordOut, AssetType

_INVALID_FILENAME = re.compile(r"[^a-zA-Z0-9._-]+")


class AssetService:
    def __init__(
        self,
        supabase_client: Client,
        storage_manager: StorageManager,
        storage_bucket: str = "uploads",
    ) -> None:
        self.supabase = supabase_client
        self.storage = storage_manager
        self.bucket = storage_bucket

    @staticmethod
    def _safe_filename(original_name: str) -> str:
        candidate = _INVALID_FILENAME.sub("_", original_name.strip())
        return candidate[:180] if candidate else f"asset_{uuid4().hex[:8]}"

    @staticmethod
    def _infer_asset_type(mime_type: str) -> AssetType:
        lower = mime_type.lower()
        if lower.startswith("image/"):
            return "image"
        if lower.startswith("video/"):
            return "video"
        if lower.startswith("audio/"):
            return "audio"
        return "document"

    @staticmethod
    def _merge_metadata(
        base: Optional[Dict[str, Any]], patch: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        merged: Dict[str, Any] = dict(base or {})
        if patch:
            merged.update(patch)
        return merged

    def _build_storage_path(
        self, workspace_id: str, original_name: str
    ) -> Tuple[str, str]:
        safe_name = self._safe_filename(original_name)
        storage_path = f"{workspace_id}/{uuid4()}/{safe_name}"
        return safe_name, storage_path

    @staticmethod
    def _to_record(row: Dict[str, Any]) -> AssetRecordOut:
        return AssetRecordOut(
            id=str(row["id"]),
            workspace_id=str(row["workspace_id"]),
            filename=row["filename"],
            original_name=row["original_name"],
            mime_type=row["mime_type"],
            size_bytes=int(row["size_bytes"]),
            storage_path=row["storage_path"],
            public_url=row.get("public_url"),
            asset_type=row["asset_type"],
            metadata=row.get("metadata") or {},
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
        )

    async def _ensure_bucket(self) -> None:
        # Frontend renders image previews from `public_url`, so bucket must be public.
        if not await self.storage.create_bucket(self.bucket, public=True):
            raise RuntimeError(f"Failed to ensure storage bucket '{self.bucket}'")

    async def create_upload_session(
        self,
        workspace_id: str,
        original_name: str,
        mime_type: str,
        size_bytes: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Tuple[AssetRecordOut, Dict[str, str]]:
        await self._ensure_bucket()

        filename, storage_path = self._build_storage_path(workspace_id, original_name)
        signed = await self.storage.create_signed_upload_url(self.bucket, storage_path)
        if not signed:
            raise RuntimeError("Failed to create signed upload URL")

        row = {
            "workspace_id": workspace_id,
            "filename": filename,
            "original_name": original_name,
            "mime_type": mime_type,
            "size_bytes": size_bytes,
            "storage_path": storage_path,
            "public_url": self.storage.get_public_url(self.bucket, storage_path),
            "asset_type": self._infer_asset_type(mime_type),
            "metadata": self._merge_metadata(metadata, {"status": "pending"}),
        }

        result = self.supabase.table("assets").insert(row).execute()
        if not result.data:
            raise RuntimeError("Failed to persist asset metadata")

        record = self._to_record(result.data[0])
        upload = {
            "signed_url": signed["signed_url"],
            "token": signed["token"],
            "path": signed["path"],
            "bucket": self.bucket,
        }
        return record, upload

    async def confirm_upload(
        self,
        workspace_id: str,
        asset_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[AssetRecordOut]:
        existing = (
            self.supabase.table("assets")
            .select("*")
            .eq("id", asset_id)
            .eq("workspace_id", workspace_id)
            .limit(1)
            .execute()
        )
        if not existing.data:
            return None

        current = existing.data[0]
        merged_metadata = self._merge_metadata(current.get("metadata"), metadata)
        merged_metadata["status"] = "uploaded"

        updated = (
            self.supabase.table("assets")
            .update({"metadata": merged_metadata})
            .eq("id", asset_id)
            .eq("workspace_id", workspace_id)
            .execute()
        )
        if not updated.data:
            return None
        return self._to_record(updated.data[0])

    async def list_workspace_assets(
        self,
        workspace_id: str,
        limit: int = 50,
        offset: int = 0,
        asset_type: Optional[str] = None,
    ) -> Tuple[list[AssetRecordOut], int]:
        count_query = (
            self.supabase.table("assets")
            .select("id", count="exact")
            .eq("workspace_id", workspace_id)
        )
        if asset_type:
            count_query = count_query.eq("asset_type", asset_type)
        count_result = count_query.execute()
        total = int(getattr(count_result, "count", 0) or 0)

        query = (
            self.supabase.table("assets")
            .select("*")
            .eq("workspace_id", workspace_id)
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
        )
        if asset_type:
            query = query.eq("asset_type", asset_type)

        result = query.execute()
        rows = result.data or []
        return [self._to_record(row) for row in rows], total

    async def get_asset(
        self, workspace_id: str, asset_id: str
    ) -> Optional[AssetRecordOut]:
        result = (
            self.supabase.table("assets")
            .select("*")
            .eq("id", asset_id)
            .eq("workspace_id", workspace_id)
            .limit(1)
            .execute()
        )
        if not result.data:
            return None
        return self._to_record(result.data[0])

    async def delete_asset(self, workspace_id: str, asset_id: str) -> bool:
        existing = (
            self.supabase.table("assets")
            .select("id, storage_path")
            .eq("id", asset_id)
            .eq("workspace_id", workspace_id)
            .limit(1)
            .execute()
        )
        if not existing.data:
            return False

        storage_path = existing.data[0]["storage_path"]
        await self.storage.delete_object(self.bucket, storage_path)

        self.supabase.table("assets").delete().eq("id", asset_id).eq(
            "workspace_id", workspace_id
        ).execute()
        return True
