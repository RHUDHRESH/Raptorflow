"""
Workspace adapters - Supabase implementation.
"""

import logging
from typing import TYPE_CHECKING, Optional

from backend.services.workspace.application.ports import WorkspaceRepository
from backend.services.workspace.domain.entities import Workspace

if TYPE_CHECKING:
    from supabase import Client

logger = logging.getLogger(__name__)


class SupabaseWorkspaceRepository(WorkspaceRepository):
    """Supabase implementation of WorkspaceRepository."""

    def __init__(self, supabase_client: "Client") -> None:
        self._client = supabase_client

    async def get_by_id(self, workspace_id: str) -> Optional[Workspace]:
        """Get a workspace by ID."""
        result = (
            self._client.table("workspaces")
            .select("*")
            .eq("id", workspace_id)
            .limit(1)
            .execute()
        )

        if not result.data:
            return None

        return Workspace.from_dict(result.data[0])

    async def list_by_owner(self, owner_id: str) -> list[Workspace]:
        """List workspaces for an owner."""
        result = (
            self._client.table("workspaces")
            .select("*")
            .eq("owner_id", owner_id)
            .order("created_at", desc=True)
            .execute()
        )

        return [Workspace.from_dict(row) for row in (result.data or [])]

    async def save(self, workspace: Workspace) -> Workspace:
        """Save a workspace."""
        data = workspace.to_dict()

        if data.get("created_at") is None:
            del data["created_at"]
        if data.get("updated_at") is None:
            del data["updated_at"]

        result = self._client.table("workspaces").upsert(data).execute()

        if not result.data:
            raise RuntimeError("Failed to save workspace")

        return Workspace.from_dict(result.data[0])

    async def delete(self, workspace_id: str) -> bool:
        """Delete a workspace."""
        result = (
            self._client.table("workspaces").delete().eq("id", workspace_id).execute()
        )

        return result.data is not None and len(result.data) > 0
