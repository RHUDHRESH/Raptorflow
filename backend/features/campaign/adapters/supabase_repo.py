"""
Campaign adapters - Supabase repository implementation.

This adapter implements the CampaignRepository port using Supabase.
"""

import logging
from typing import TYPE_CHECKING, Optional

from backend.core.exceptions import AdapterError, NotFoundError
from backend.features.campaign.application.ports import CampaignRepository
from backend.features.campaign.domain.entities import Campaign

if TYPE_CHECKING:
    from supabase import Client

logger = logging.getLogger(__name__)


class SupabaseCampaignRepository(CampaignRepository):
    """
    Supabase implementation of CampaignRepository.

    This adapter handles persistence to Supabase database.
    """

    def __init__(self, supabase_client: "Client") -> None:
        """
        Initialize with a Supabase client.

        Args:
            supabase_client: A Supabase client instance (from get_supabase_client())
        """
        self._client = supabase_client

    async def get_by_id(
        self, campaign_id: str, workspace_id: str
    ) -> Optional[Campaign]:
        """Get a campaign by ID within a workspace."""
        try:
            response = (
                self._client.table("campaigns")
                .select("*")
                .eq("id", campaign_id)
                .eq("workspace_id", workspace_id)
                .limit(1)
                .execute()
            )

            if not response.data:
                return None

            return Campaign.from_dict(response.data[0])
        except Exception as e:
            logger.error(f"Failed to get campaign {campaign_id}: {e}")
            raise AdapterError(f"Failed to retrieve campaign: {e}") from e

    async def list_by_workspace(self, workspace_id: str) -> list[Campaign]:
        """List all campaigns for a workspace."""
        try:
            response = (
                self._client.table("campaigns")
                .select("*")
                .eq("workspace_id", workspace_id)
                .order("created_at", desc=True)
                .execute()
            )

            return [Campaign.from_dict(row) for row in (response.data or [])]
        except Exception as e:
            logger.error(f"Failed to list campaigns for workspace {workspace_id}: {e}")
            raise AdapterError(f"Failed to list campaigns: {e}") from e

    async def save(self, campaign: Campaign) -> Campaign:
        """Save a campaign (create or update)."""
        data = campaign.to_dict()

        # Remove created_at/updated_at if they're None (let DB handle defaults)
        if data.get("created_at") is None:
            del data["created_at"]
        if data.get("updated_at") is None:
            del data["updated_at"]

        try:
            response = self._client.table("campaigns").upsert(data).execute()

            if not response.data:
                raise AdapterError("Failed to save campaign: no data returned")

            return Campaign.from_dict(response.data[0])
        except AdapterError:
            raise
        except Exception as e:
            logger.error(f"Failed to save campaign {campaign.id}: {e}")
            raise AdapterError(f"Failed to save campaign: {e}") from e

    async def delete(self, campaign_id: str, workspace_id: str) -> bool:
        """Delete a campaign. Returns True if deleted, False if not found."""
        try:
            response = (
                self._client.table("campaigns")
                .delete()
                .eq("id", campaign_id)
                .eq("workspace_id", workspace_id)
                .execute()
            )

            return response.data is not None and len(response.data) > 0
        except Exception as e:
            logger.error(f"Failed to delete campaign {campaign_id}: {e}")
            raise AdapterError(f"Failed to delete campaign: {e}") from e
