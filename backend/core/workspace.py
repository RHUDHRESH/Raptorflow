"""
Workspace management functions
Handles workspace resolution and validation
"""

from typing import Any, Dict, List, Optional

from fastapi import HTTPException

from .models import Workspace
from .supabase_mgr import get_supabase_client


async def get_workspace_for_user(
    workspace_id: str, user_id: str
) -> Optional[Workspace]:
    """Get workspace details for user"""
    try:
        supabase = get_supabase_client()
        workspace_data = _load_workspace_record(supabase, workspace_id)
        if not workspace_data:
            return None

        # Enforce owner_id + workspace_members schema
        if workspace_data.get("owner_id") == user_id or await _user_in_workspace(
            workspace_id, user_id
        ):
            return Workspace(
                id=workspace_data["id"],
                user_id=workspace_data.get("owner_id"),  # Only use owner_id
                name=workspace_data["name"],
                slug=workspace_data.get("slug"),
                settings=workspace_data.get("settings", {}),
                created_at=workspace_data.get("created_at"),
                updated_at=workspace_data.get("updated_at"),
            )
        return None

    except Exception:
        return None


def _load_workspace_record(supabase, workspace_id: str) -> Optional[Dict[str, Any]]:
    try:
        result = (
            supabase.table("workspaces")
            .select("*")
            .eq("id", workspace_id)
            .single()
            .execute()
        )
        return result.data
    except Exception:
        return None


async def _user_in_workspace(workspace_id: str, user_id: str) -> bool:
    try:
        supabase = get_supabase_client()
        workspace_record = _load_workspace_record(supabase, workspace_id)
        if not workspace_record:
            return False

        # Enforce owner_id schema - no fallback to user_id
        owner_id = workspace_record.get("owner_id")
        if owner_id == user_id:
            return True

        # Check workspace_members table
        membership = (
            supabase.table("workspace_members")
            .select("id")
            .eq("workspace_id", workspace_id)
            .eq("user_id", user_id)
            .eq("is_active", True)
            .single()
            .execute()
        )
        return membership.data is not None
    except Exception:
        return False


async def validate_workspace_access(workspace_id: str, user_id: str) -> bool:
    """Validate that user has access to workspace"""
    try:
        supabase = get_supabase_client()
        workspace = _load_workspace_record(supabase, workspace_id)
        if not workspace:
            return False

        # Enforce owner_id schema - no fallback to user_id
        owner_id = workspace.get("owner_id")
        if owner_id == user_id:
            return True
        return await _user_in_workspace(workspace_id, user_id)
    except Exception:
        return False


async def get_user_workspaces(user_id: str) -> list[Workspace]:
    """Get all workspaces for a user"""
    try:
        supabase = get_supabase_client()
        workspaces: List[Workspace] = []

        # Get owned workspaces using owner_id only
        owned = (
            supabase.table("workspaces")
            .select("*")
            .eq("owner_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        workspace_records = {w["id"]: w for w in (owned.data or [])}

        # Get workspaces through membership
        memberships = (
            supabase.table("workspace_members")
            .select("workspace_id")
            .eq("user_id", user_id)
            .eq("is_active", True)
            .execute()
        )
        member_workspace_ids = [
            entry["workspace_id"] for entry in memberships.data or []
        ]

        if member_workspace_ids:
            member_records = (
                supabase.table("workspaces")
                .select("*")
                .in_("id", member_workspace_ids)
                .execute()
            )
            for record in member_records.data or []:
                workspace_records.setdefault(record["id"], record)

        for workspace_data in workspace_records.values():
            # Enforce owner_id schema only
            owner_id = workspace_data.get("owner_id")
            workspaces.append(
                Workspace(
                    id=workspace_data["id"],
                    user_id=owner_id,
                    name=workspace_data["name"],
                    slug=workspace_data.get("slug"),
                    settings=workspace_data.get("settings", {}),
                    created_at=workspace_data.get("created_at"),
                    updated_at=workspace_data.get("updated_at"),
                )
            )

        return sorted(workspaces, key=lambda ws: ws.created_at or "", reverse=True)

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
                {"id": workspace_id, "owner_id": user_id, "name": name, "slug": slug}
            )
            .single()
            .execute()
        )

        if result.data:
            return Workspace(
                id=result.data["id"],
                user_id=result.data["owner_id"],  # Only use owner_id
                name=result.data["name"],
                slug=result.data.get("slug"),
                settings=result.data.get("settings", {}),
                created_at=result.data.get("created_at"),
                updated_at=result.data.get("updated_at"),
            )

        return None

    except Exception:
        return None
