"""
Context API — BCM manifest endpoints.

Provides access to the Business Context Manifest for a workspace.
All operations scoped by X-Workspace-Id header.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field

from backend.services import bcm_service

router = APIRouter(prefix="/context", tags=["context"])


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


class BCMResponse(BaseModel):
    manifest: Dict[str, Any]
    version: int
    checksum: str
    token_estimate: int = 0
    created_at: Optional[str] = None
    completion_pct: int = 0


class SeedRequest(BaseModel):
    business_context: Dict[str, Any] = Field(..., description="Full business_context.json")


class VersionSummary(BaseModel):
    id: str
    version: int
    checksum: str
    token_estimate: int = 0
    created_at: Optional[str] = None


def _compute_completion(manifest: Dict[str, Any]) -> int:
    """Compute completion percentage based on populated BCM sections."""
    sections = ["foundation", "icps", "competitive", "messaging", "channels", "market"]
    filled = 0
    for section in sections:
        val = manifest.get(section)
        if val:
            if isinstance(val, list) and len(val) > 0:
                filled += 1
            elif isinstance(val, dict) and any(v for v in val.values() if v):
                filled += 1
    return int((filled / len(sections)) * 100)


@router.get("/", response_model=BCMResponse)
async def get_latest_bcm(
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> BCMResponse:
    """Get the latest BCM manifest for the workspace."""
    workspace_id = _require_workspace_id(x_workspace_id)
    row = bcm_service.get_latest(workspace_id)

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No BCM manifest found. Seed business context first.",
        )

    manifest = row["manifest"]
    return BCMResponse(
        manifest=manifest,
        version=row["version"],
        checksum=row.get("checksum", ""),
        token_estimate=row.get("token_estimate", 0),
        created_at=row.get("created_at"),
        completion_pct=_compute_completion(manifest),
    )


@router.post("/rebuild", response_model=BCMResponse)
async def rebuild_bcm(
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> BCMResponse:
    """Rebuild BCM from the latest stored source business context."""
    workspace_id = _require_workspace_id(x_workspace_id)
    row = bcm_service.rebuild(workspace_id)

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No source business context found to rebuild from.",
        )

    manifest = row["manifest"]
    return BCMResponse(
        manifest=manifest,
        version=row["version"],
        checksum=row.get("checksum", ""),
        token_estimate=row.get("token_estimate", 0),
        created_at=row.get("created_at"),
        completion_pct=_compute_completion(manifest),
    )


@router.post("/seed", response_model=BCMResponse)
async def seed_bcm(
    payload: SeedRequest,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> BCMResponse:
    """Seed a BCM from a raw business_context.json (dev/test use)."""
    workspace_id = _require_workspace_id(x_workspace_id)
    row = bcm_service.seed_from_business_context(workspace_id, payload.business_context)

    manifest = row["manifest"]
    return BCMResponse(
        manifest=manifest,
        version=row["version"],
        checksum=row.get("checksum", ""),
        token_estimate=row.get("token_estimate", 0),
        created_at=row.get("created_at"),
        completion_pct=_compute_completion(manifest),
    )


@router.get("/versions", response_model=List[VersionSummary])
async def list_bcm_versions(
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> List[VersionSummary]:
    """List all BCM versions for the workspace."""
    workspace_id = _require_workspace_id(x_workspace_id)
    rows = bcm_service.list_versions(workspace_id)
    return [
        VersionSummary(
            id=r["id"],
            version=r["version"],
            checksum=r.get("checksum", ""),
            token_estimate=r.get("token_estimate", 0),
            created_at=r.get("created_at"),
        )
        for r in rows
    ]
