"""Assets API for workspace-scoped uploads."""

from __future__ import annotations

import os
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, Query, Depends, status

from backend.config import settings
from backend.core.storage.manager import StorageManager
from backend.core.database.supabase import get_supabase_client
from backend.schemas.asset import (
    AssetConfirmUploadIn,
    AssetCreateSessionIn,
    AssetCreateSessionOut,
    AssetListOut,
    AssetRecordOut,
    AssetType,
)
from backend.services.asset import AssetService
from backend.api.dependencies.auth import get_current_user

router = APIRouter(prefix="/assets", tags=["assets"])


def _require_workspace_id(x_workspace_id: Optional[str]) -> str:
    if not x_workspace_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing X-Workspace-Id header",
        )
    try:
        UUID(x_workspace_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid X-Workspace-Id header (must be UUID)",
        )
    return x_workspace_id


def _service() -> AssetService:
    supabase_url = settings.SUPABASE_URL or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    service_key = (
        settings.SUPABASE_SERVICE_ROLE_KEY
        or os.getenv("SUPABASE_SERVICE_KEY")
        or os.getenv("SERVICE_ROLE_KEY")
    )
    if not supabase_url or not service_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Supabase storage is not configured. "
                "Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY."
            ),
        )

    bucket = settings.SUPABASE_STORAGE_BUCKET or "uploads"
    return AssetService(
        supabase_client=get_supabase_client(),
        storage_manager=StorageManager(
            supabase_url=supabase_url, service_key=service_key
        ),
        storage_bucket=bucket,
    )


def _is_assets_table_missing(exc: Exception) -> bool:
    msg = str(exc)
    return "public.assets" in msg and ("schema cache" in msg or "PGRST205" in msg)


@router.post(
    "/sessions",
    response_model=AssetCreateSessionOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_upload_session(
    payload: AssetCreateSessionIn,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> AssetCreateSessionOut:
    workspace_id = _require_workspace_id(x_workspace_id)
    service = _service()
    try:
        asset, upload = await service.create_upload_session(
            workspace_id=workspace_id,
            original_name=payload.original_name,
            mime_type=payload.mime_type,
            size_bytes=payload.size_bytes,
            metadata=payload.metadata,
        )
        return AssetCreateSessionOut(asset=asset, upload=upload)
    except Exception as exc:
        if _is_assets_table_missing(exc):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Assets table is missing. Apply migration `20260212000000_assets_table.sql`.",
            )
        raise


@router.post("/{asset_id}/confirm", response_model=AssetRecordOut)
async def confirm_upload(
    asset_id: str,
    payload: AssetConfirmUploadIn,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> AssetRecordOut:
    workspace_id = _require_workspace_id(x_workspace_id)
    service = _service()
    try:
        confirmed = await service.confirm_upload(
            workspace_id=workspace_id,
            asset_id=asset_id,
            metadata=payload.metadata,
        )
        if not confirmed:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found"
            )
        return confirmed
    except Exception as exc:
        if _is_assets_table_missing(exc):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Assets table is missing. Apply migration `20260212000000_assets_table.sql`.",
            )
        raise


@router.get("/", response_model=AssetListOut)
async def list_assets(
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    asset_type: Optional[AssetType] = Query(None),
) -> AssetListOut:
    workspace_id = _require_workspace_id(x_workspace_id)
    service = _service()
    try:
        assets, total = await service.list_workspace_assets(
            workspace_id=workspace_id,
            limit=limit,
            offset=offset,
            asset_type=asset_type,
        )
        return AssetListOut(assets=assets, total=total, offset=offset, limit=limit)
    except Exception as exc:
        if _is_assets_table_missing(exc):
            return AssetListOut(assets=[], total=0, offset=offset, limit=limit)
        raise


@router.get("/{asset_id}", response_model=AssetRecordOut)
async def get_asset(
    asset_id: str,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> AssetRecordOut:
    workspace_id = _require_workspace_id(x_workspace_id)
    service = _service()
    try:
        asset = await service.get_asset(workspace_id=workspace_id, asset_id=asset_id)
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found"
            )
        return asset
    except Exception as exc:
        if _is_assets_table_missing(exc):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Assets table is missing. Apply migration `20260212000000_assets_table.sql`.",
            )
        raise


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(
    asset_id: str,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> None:
    workspace_id = _require_workspace_id(x_workspace_id)
    service = _service()
    try:
        deleted = await service.delete_asset(
            workspace_id=workspace_id, asset_id=asset_id
        )
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found"
            )
    except Exception as exc:
        if _is_assets_table_missing(exc):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Assets table is missing. Apply migration `20260212000000_assets_table.sql`.",
            )
        raise
