"""
Workspace application services.
"""

from typing import Any, Dict, Optional
from uuid import uuid4

from backend.features.workspace.application.ports import (
    WorkspaceRepository,
    OnboardingRepository,
)
from backend.features.workspace.domain.entities import Workspace, OnboardingStatus


class WorkspaceService:
    """Application service for workspace operations."""

    def __init__(
        self,
        repository: WorkspaceRepository,
        onboarding_repo: Optional[OnboardingRepository] = None,
    ):
        self._repository = repository
        self._onboarding_repo = onboarding_repo

    async def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        """Get a workspace by ID."""
        return await self._repository.get_by_id(workspace_id)

    async def list_workspaces(self, owner_id: str) -> list[Workspace]:
        """List workspaces for an owner."""
        return await self._repository.list_by_owner(owner_id)

    async def create_workspace(
        self,
        name: str,
        slug: str,
        owner_id: Optional[str] = None,
    ) -> Workspace:
        """Create a new workspace."""
        workspace = Workspace(
            id=str(uuid4()),
            name=name,
            slug=slug,
            owner_id=owner_id,
        )
        return await self._repository.save(workspace)

    async def update_workspace(
        self,
        workspace_id: str,
        name: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None,
    ) -> Optional[Workspace]:
        """Update a workspace."""
        workspace = await self._repository.get_by_id(workspace_id)
        if not workspace:
            return None

        if name is not None:
            workspace.name = name
        if settings is not None:
            workspace.settings = settings

        return await self._repository.save(workspace)

    async def delete_workspace(self, workspace_id: str) -> bool:
        """Delete a workspace."""
        return await self._repository.delete(workspace_id)

    async def get_onboarding_status(
        self, workspace_id: str
    ) -> Optional[OnboardingStatus]:
        """Get onboarding status for a workspace."""
        if self._onboarding_repo:
            return await self._onboarding_repo.get_status(workspace_id)
        return None

    async def update_onboarding_status(
        self,
        workspace_id: str,
        completed_steps: list[str],
        current_step: Optional[str] = None,
    ) -> OnboardingStatus:
        """Update onboarding status."""
        status = OnboardingStatus(
            workspace_id=workspace_id,
            completed_steps=completed_steps,
            current_step=current_step,
        )

        if self._onboarding_repo:
            return await self._onboarding_repo.save_status(status)

        return status
