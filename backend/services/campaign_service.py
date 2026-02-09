"""
Campaign Service: Supabase CRUD for Campaigns.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from uuid import uuid4

from backend.core.supabase_mgr import get_supabase_client
from backend.services.base_service import BaseService
from backend.services.registry import registry
from backend.services.exceptions import ResourceNotFoundError, ServiceError

logger = logging.getLogger(__name__)

class CampaignService(BaseService):
    def __init__(self):
        super().__init__("campaign_service")

    async def check_health(self) -> Dict[str, Any]:
        """Check connection to Supabase table."""
        try:
            client = get_supabase_client()
            client.table("campaigns").select("count", count="exact").limit(0).execute()
            return {"status": "healthy"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def list_campaigns(self, workspace_id: str) -> List[Dict[str, Any]]:
        """List all campaigns for a workspace."""
        def _execute():
            client = get_supabase_client()
            result = (
                client.table("campaigns")
                .select("*")
                .eq("workspace_id", workspace_id)
                .order("created_at", desc=True)
                .execute()
            )
            return result.data or []
        return _execute()

    def create_campaign(self, workspace_id: str, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new campaign."""
        def _execute():
            client = get_supabase_client()
            
            # Ensure ID is present
            if "id" not in campaign_data:
                campaign_data["id"] = str(uuid4())
            
            campaign_data["workspace_id"] = workspace_id
            
            result = client.table("campaigns").insert(campaign_data).execute()
            if not result.data:
                raise ServiceError("Failed to create campaign")
            
            return result.data[0]
        return _execute()

    def get_campaign(self, workspace_id: str, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get a campaign by ID."""
        def _execute():
            client = get_supabase_client()
            result = (
                client.table("campaigns")
                .select("*")
                .eq("id", campaign_id)
                .eq("workspace_id", workspace_id)
                .limit(1)
                .execute()
            )
            if not result.data:
                return None
            return result.data[0]
        return _execute()

    def update_campaign(self, workspace_id: str, campaign_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a campaign."""
        def _execute():
            client = get_supabase_client()
            result = (
                client.table("campaigns")
                .update(updates)
                .eq("id", campaign_id)
                .eq("workspace_id", workspace_id)
                .execute()
            )
            if not result.data:
                return None
            return result.data[0]
        return _execute()

    def delete_campaign(self, workspace_id: str, campaign_id: str) -> bool:
        """Delete a campaign. Returns True if found and deleted, False otherwise."""
        def _execute():
            client = get_supabase_client()
            result = (
                client.table("campaigns")
                .delete()
                .eq("id", campaign_id)
                .eq("workspace_id", workspace_id)
                .execute()
            )
            return result.data is not None and len(result.data) > 0
        return _execute()

# Global instance
campaign_service = CampaignService()
registry.register(campaign_service)
