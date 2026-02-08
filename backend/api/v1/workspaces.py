"""
Workspaces API (No-Auth Reconstruction Mode)

Canonical tenant identifier: workspace id (UUID).
Auth is intentionally not required; this is for scorched-earth reconstruction.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from backend.core.supabase_mgr import get_supabase_client
from backend.services.business_context_templates import (
    TemplateType,
    extract_foundation_data,
    get_template,
)
from backend.config.settings import get_settings
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/workspaces", tags=["workspaces"])

logger = logging.getLogger(__name__)


class WorkspaceCreate(BaseModel):
    name: str = Field(..., min_length=1)
    slug: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class WorkspaceResponse(BaseModel):
    id: str
    name: str
    slug: Optional[str] = None
    settings: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


_SLUG_RE = re.compile(r"[^a-z0-9-]+")


def _slugify(name: str) -> str:
    slug = name.strip().lower()
    slug = slug.replace("_", "-").replace(" ", "-")
    slug = _SLUG_RE.sub("", slug)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug or f"workspace-{uuid4().hex[:8]}"


def _is_slug_collision_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    # Supabase/Postgres uniqueness failures often mention 23505 or "duplicate key".
    # We only retry on likely slug uniqueness collisions; everything else must surface.
    return ("23505" in msg or "duplicate" in msg or "unique" in msg) and "slug" in msg


async def _insert_workspace(payload: Dict[str, Any]) -> Dict[str, Any]:
    supabase = get_supabase_client()
    result = supabase.table("workspaces").insert(payload).execute()
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create workspace",
        )
    return result.data[0]


@router.post("/", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(workspace: WorkspaceCreate) -> WorkspaceResponse:
    """
    Create a workspace with automatic foundation seeding.
    
    If DEFAULT_BUSINESS_TEMPLATE environment variable is set (saas, agency, or ecommerce),
    the workspace is automatically seeded with foundation data from that template.
    """
    base_slug = workspace.slug or _slugify(workspace.name)
    settings = workspace.settings or {}

    # Try to insert, retrying slug collisions with a suffix.
    last_error: Optional[Exception] = None
    created_workspace: Optional[Dict[str, Any]] = None
    
    for attempt in range(0, 6):
        slug = base_slug if attempt == 0 else f"{base_slug}-{uuid4().hex[:6]}"
        payload = {
            "id": str(uuid4()),
            "name": workspace.name,
            "slug": slug,
            "settings": settings,
        }
        try:
            created_workspace = await _insert_workspace(payload)
            break
        except Exception as e:
            last_error = e
            if _is_slug_collision_error(e):
                continue
            raise
    
    if not created_workspace:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create workspace (slug collision). Last error: {last_error}",
        )
    
    # Seed foundation data from default template if configured
    config = get_settings()
    if config.DEFAULT_BUSINESS_TEMPLATE:
        await _seed_workspace_foundation(
            workspace_id=created_workspace["id"],
            template_type=config.DEFAULT_BUSINESS_TEMPLATE
        )
    
    return WorkspaceResponse(**created_workspace)


async def _seed_workspace_foundation(
    workspace_id: str,
    template_type: TemplateType
) -> None:
    """Seed foundation data for a workspace from template."""
    try:
        supabase = get_supabase_client()
        
        # Load and extract template data
        template = get_template(template_type)
        foundation_data = extract_foundation_data(template)
        foundation_data["workspace_id"] = workspace_id
        
        # Insert into foundations table
        result = supabase.table("foundations").insert(foundation_data).execute()
        
        if result.data:
            logger.info(f"Seeded foundation for workspace {workspace_id} from {template_type} template")
        else:
            logger.warning(f"Failed to seed foundation for workspace {workspace_id}")
            
    except Exception as e:
        # Log error but don't fail workspace creation
        logger.error(f"Error seeding foundation for workspace {workspace_id}: {e}")


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(workspace_id: str) -> WorkspaceResponse:
    supabase = get_supabase_client()
    try:
        UUID(workspace_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid workspace_id"
        )

    result = (
        supabase.table("workspaces").select("*").eq("id", workspace_id).limit(1).execute()
    )
    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    return WorkspaceResponse(**result.data[0])


@router.patch("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(workspace_id: str, updates: WorkspaceUpdate) -> WorkspaceResponse:
    supabase = get_supabase_client()
    try:
        UUID(workspace_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid workspace_id"
        )

    update_data: Dict[str, Any] = {}
    if updates.name is not None:
        update_data["name"] = updates.name
    if updates.slug is not None:
        update_data["slug"] = updates.slug
    if updates.settings is not None:
        update_data["settings"] = updates.settings

    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    result = (
        supabase.table("workspaces").update(update_data).eq("id", workspace_id).execute()
    )
    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    return WorkspaceResponse(**result.data[0])
