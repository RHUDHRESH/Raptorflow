"""
Campaign application layer - Ports (Interfaces).

These define the contracts that adapters must implement.
"""

from typing import Protocol, Optional
from backend.features.campaign.domain.entities import Campaign


class CampaignRepository(Protocol):
    """
    Port for campaign persistence.

    Adapters implement this protocol to provide concrete storage.
    """

    async def get_by_id(
        self, campaign_id: str, workspace_id: str
    ) -> Optional[Campaign]:
        """Get a campaign by ID within a workspace."""
        ...

    async def list_by_workspace(self, workspace_id: str) -> list[Campaign]:
        """List all campaigns for a workspace."""
        ...

    async def save(self, campaign: Campaign) -> Campaign:
        """Save a campaign (create or update)."""
        ...

    async def delete(self, campaign_id: str, workspace_id: str) -> bool:
        """Delete a campaign. Returns True if deleted, False if not found."""
        ...
