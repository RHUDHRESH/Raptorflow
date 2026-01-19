"""
Workspace management functions
Handles workspace resolution and validation
"""

from typing import Optional

from fastapi import HTTPException

from .models import Workspace
from .supabase_mgr import get_supabase_client


async def get_workspace_for_user(
    workspace_id: str, user_id: str
) -> Optional[Workspace]:
    """Get workspace details for user"""
    try:
        supabase = get_supabase_client()
        result = (
            supabase.table("workspaces")
            .select("*")
            .eq("id", workspace_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )

        if not result.data:
            return None

        workspace_data = result.data
        return Workspace(
            id=workspace_data["id"],
            user_id=workspace_data["user_id"],
            name=workspace_data["name"],
            slug=workspace_data.get("slug"),
            settings=workspace_data.get("settings", {}),
            created_at=workspace_data.get("created_at"),
            updated_at=workspace_data.get("updated_at"),
        )

    except Exception:
        return None


async def validate_workspace_access(workspace_id: str, user_id: str) -> bool:
    """Validate that user has access to workspace"""
    try:
        supabase = get_supabase_client()
        result = (
            supabase.table("workspaces")
            .select("id")
            .eq("id", workspace_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )
        return result.data is not None
    except Exception:
        return False


async def get_user_workspaces(user_id: str) -> list[Workspace]:
    """Get all workspaces for a user"""
    try:
        supabase = get_supabase_client()
        result = (
            supabase.table("workspaces")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )

        workspaces = []
        if result.data:
            for workspace_data in result.data:
                workspaces.append(
                    Workspace(
                        id=workspace_data["id"],
                        user_id=workspace_data["user_id"],
                        name=workspace_data["name"],
                        slug=workspace_data.get("slug"),
                        settings=workspace_data.get("settings", {}),
                        created_at=workspace_data.get("created_at"),
                        updated_at=workspace_data.get("updated_at"),
                    )
                )

        return workspaces

    except Exception:
        return []


async def create_workspace_for_user(user_id: str, name: str) -> Optional[Workspace]:
    """Create a new workspace for user"""
    try:
        import uuid

        workspace_id = str(uuid.uuid4())
        slug = f"ws-{workspace_id[:8]}"

        supabase = get_supabase_client()
        result = (
            supabase.table("workspaces")
            .insert(
                {"id": workspace_id, "user_id": user_id, "name": name, "slug": slug}
            )
            .single()
            .execute()
        )

        if result.data:
            return Workspace(
                id=result.data["id"],
                user_id=result.data["user_id"],
                name=result.data["name"],
                slug=result.data.get("slug"),
                settings=result.data.get("settings", {}),
                created_at=result.data.get("created_at"),
                updated_at=result.data.get("updated_at"),
            )

        return None

    except Exception:
        return None
