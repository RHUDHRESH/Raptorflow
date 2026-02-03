"""
Workspaces API endpoints
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr

from ..core.supabase_mgr import get_supabase_client
from ..core.workspace import get_workspace_for_user

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


# Pydantic models for request/response
class WorkspaceCreate(BaseModel):
    name: str
    slug: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class WorkspaceResponse(BaseModel):
    id: str
    user_id: str
    name: str
    slug: Optional[str]
    settings: Dict[str, Any]
    created_at: str
    updated_at: str


@router.get("/", response_model=List[WorkspaceResponse])
async def list_workspaces(user_id: str = Query(..., description="User ID")):
    """
    List all workspaces for the authenticated user
    """
    supabase = get_supabase_client()

    result = (
        supabase.table("workspaces")
        .select("*")
        .eq("user_id", current_user.id)
        .order("created_at", desc=True)
        .execute()
    )

    return result.data or []


@router.post("/", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    workspace_data: WorkspaceCreate, user_id: str = Query(..., description="User ID")
):
    """
    Create a new workspace
    """
    supabase = get_supabase_client()

    # Check if user has reached workspace limit for their subscription tier
    current_workspaces_result = (
        supabase.table("workspaces")
        .select("id")
        .eq("user_id", current_user.id)
        .execute()
    )
    current_count = len(current_workspaces_result.data or [])

    # Define workspace limits by subscription tier
    workspace_limits = {
        "free": 1,
        "starter": 3,
        "pro": 10,
        "growth": 10,
        "enterprise": 50,
    }

    max_workspaces = workspace_limits.get(current_user.subscription_tier, 1)

    if current_count >= max_workspaces:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Workspace limit of {max_workspaces} reached for {current_user.subscription_tier} tier",
        )

    # Prepare workspace data
    workspace_insert = {
        "user_id": current_user.id,
        "name": workspace_data.name,
        "settings": workspace_data.settings
        or {"timezone": "Asia/Kolkata", "currency": "INR", "language": "en"},
    }

    # Generate slug if not provided
    if workspace_data.slug:
        workspace_insert["slug"] = workspace_data.slug
    else:
        # Generate unique slug
        slug_result = supabase.rpc(
            "generate_unique_slug", {"base_name": workspace_data.name}
        ).execute()
        workspace_insert["slug"] = slug_result.data

    # Create workspace
    result = supabase.table("workspaces").insert(workspace_insert).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create workspace",
        )

    return result.data[0]


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: str, user_id: str = Query(..., description="User ID")
):
    """
    Get a specific workspace by ID
    """
    if not auth_context.workspace or auth_context.workspace.id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found or access denied",
        )

    return auth_context.workspace


@router.put("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: str,
    workspace_data: WorkspaceUpdate,
    user_id: str = Query(..., description="User ID"),
):
    """
    Update a workspace
    """
    if not auth_context.workspace or auth_context.workspace.id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found or access denied",
        )

    supabase = get_supabase_client()

    # Prepare update data (only include non-None values)
    update_data = {}
    if workspace_data.name is not None:
        update_data["name"] = workspace_data.name
    if workspace_data.slug is not None:
        update_data["slug"] = workspace_data.slug
    if workspace_data.settings is not None:
        update_data["settings"] = workspace_data.settings

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update"
        )

    # Update workspace
    result = (
        supabase.table("workspaces")
        .update(update_data)
        .eq("id", workspace_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update workspace",
        )

    return result.data[0]


@router.delete("/{workspace_id}")
async def delete_workspace(
    workspace_id: str, user_id: str = Query(..., description="User ID")
):
    """
    Delete a workspace and all associated data
    """
    if not auth_context.workspace or auth_context.workspace.id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found or access denied",
        )

    supabase = get_supabase_client()

    # In a real implementation, you might want to:
    # 1. Archive data instead of deleting
    # 2. Send confirmation email
    # 3. Add cooldown period

    # Delete workspace (cascade deletes should handle related data)
    result = supabase.table("workspaces").delete().eq("id", workspace_id).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete workspace",
        )

    return {"message": "Workspace deleted successfully", "workspace_id": workspace_id}


@router.get("/{workspace_id}/settings")
async def get_workspace_settings(
    workspace_id: str, user_id: str = Query(..., description="User ID")
):
    """
    Get workspace settings
    """
    if not auth_context.workspace or auth_context.workspace.id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found or access denied",
        )

    return {"settings": auth_context.workspace.settings, "workspace_id": workspace_id}


@router.put("/{workspace_id}/settings")
async def update_workspace_settings(
    workspace_id: str,
    settings: Dict[str, Any],
    user_id: str = Query(..., description="User ID"),
):
    """
    Update workspace settings
    """
    if not auth_context.workspace or auth_context.workspace.id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found or access denied",
        )

    supabase = get_supabase_client()

    result = (
        supabase.table("workspaces")
        .update({"settings": settings})
        .eq("id", workspace_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update workspace settings",
        )

    return {"message": "Settings updated successfully", "settings": settings}


@router.get("/{workspace_id}/stats")
async def get_workspace_stats(
    workspace_id: str, user_id: str = Query(..., description="User ID")
):
    """
    Get workspace statistics
    """
    if not auth_context.workspace or auth_context.workspace.id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found or access denied",
        )

    supabase = get_supabase_client()

    # Get workspace statistics
    stats_result = supabase.rpc(
        "get_workspace_stats", {"workspace_id": workspace_id}
    ).execute()

    return {"workspace_id": workspace_id, "stats": stats_result.data or []}


@router.post("/{workspace_id}/duplicate")
async def duplicate_workspace(
    workspace_id: str, new_name: str, user_id: str = Query(..., description="User ID")
):
    """
    Duplicate a workspace (structure only, not the data)
    """
    supabase = get_supabase_client()

    # Verify ownership
    original_result = (
        supabase.table("workspaces")
        .select("*")
        .eq("id", workspace_id)
        .eq("user_id", current_user.id)
        .single()
        .execute()
    )

    if not original_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found or access denied",
        )

    original = original_result.data

    # Check workspace limits
    current_workspaces_result = (
        supabase.table("workspaces")
        .select("id")
        .eq("user_id", current_user.id)
        .execute()
    )
    current_count = len(current_workspaces_result.data or [])

    workspace_limits = {
        "free": 1,
        "starter": 3,
        "pro": 10,
        "growth": 10,
        "enterprise": 50,
    }

    max_workspaces = workspace_limits.get(current_user.subscription_tier, 1)

    if current_count >= max_workspaces:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Workspace limit of {max_workspaces} reached for {current_user.subscription_tier} tier",
        )

    # Create new workspace with same settings
    new_workspace_data = {
        "user_id": current_user.id,
        "name": new_name,
        "settings": original["settings"],
    }

    # Generate unique slug
    slug_result = supabase.rpc(
        "generate_unique_slug", {"base_name": new_name}
    ).execute()
    new_workspace_data["slug"] = slug_result.data

    result = supabase.table("workspaces").insert(new_workspace_data).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to duplicate workspace",
        )

    return {
        "message": "Workspace duplicated successfully",
        "original_workspace_id": workspace_id,
        "new_workspace": result.data[0],
    }


@router.post("/{workspace_id}/export")
async def export_workspace_data(
    workspace_id: str,
    format: str = "json",
    user_id: str = Query(..., description="User ID"),
):
    """
    Export all workspace data
    """
    if not auth_context.workspace or auth_context.workspace.id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found or access denied",
        )

    if format not in ["json", "csv"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format must be 'json' or 'csv'",
        )

    # In a real implementation, you would:
    # 1. Collect all data from all tables
    # 2. Format according to requested format
    # 3. Return downloadable file or data

    return {
        "message": f"Workspace export in {format} format",
        "workspace_id": workspace_id,
        "note": "This would export all workspace data",
        "format": format,
    }


@router.get("/{workspace_id}/activity")
async def get_workspace_activity(
    workspace_id: str,
    days: int = 30,
    user_id: str = Query(..., description="User ID"),
):
    """
    Get recent workspace activity
    """
    if not auth_context.workspace or auth_context.workspace.id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found or access denied",
        )

    supabase = get_supabase_client()

    # Get recent activity from audit logs
    from datetime import datetime, timedelta

    cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

    audit_result = (
        supabase.table("audit_logs")
        .select("*")
        .eq("workspace_id", workspace_id)
        .gte("created_at", cutoff_date)
        .order("created_at", desc=True)
        .limit(100)
        .execute()
    )

    return {
        "workspace_id": workspace_id,
        "days": days,
        "activities": audit_result.data or [],
        "total_activities": len(audit_result.data or []),
    }
