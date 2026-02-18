"""
Workspace application layer - Ports.
"""

from typing import Protocol, Optional
from backend.features.workspace.domain.entities import Workspace, OnboardingStatus


class WorkspaceRepository(Protocol):
    """Port for workspace persistence."""

    async def get_by_id(self, workspace_id: str) -> Optional[Workspace]: ...

    async def list_by_owner(self, owner_id: str) -> list[Workspace]: ...

    async def save(self, workspace: Workspace) -> Workspace: ...

    async def delete(self, workspace_id: str) -> bool: ...


class OnboardingRepository(Protocol):
    """Port for onboarding status persistence."""

    async def get_status(self, workspace_id: str) -> Optional[OnboardingStatus]: ...

    async def save_status(self, status: OnboardingStatus) -> OnboardingStatus: ...
