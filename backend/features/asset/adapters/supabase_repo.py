"""
Asset adapters - Supabase implementation.
"""

import logging
from typing import TYPE_CHECKING, Optional, Tuple

from backend.core.exceptions import AdapterError
from backend.features.asset.application.ports import AssetRepository
from backend.features.asset.domain.entities import Asset, AssetType

if TYPE_CHECKING:
    from supabase import Client

logger = logging.getLogger(__name__)


class SupabaseAssetRepository(AssetRepository):
    """Supabase implementation of AssetRepository."""

    def __init__(self, supabase_client: "Client") -> None:
        self._client = supabase_client

    async def get_by_id(self, asset_id: str, workspace_id: str) -> Optional[Asset]:
        """Get an asset by ID."""
        try:
            result = (
                self._client.table("assets")
                .select("*")
                .eq("id", asset_id)
                .eq("workspace_id", workspace_id)
                .limit(1)
                .execute()
            )

            if not result.data:
                return None

            return Asset.from_dict(result.data[0])
        except Exception as e:
            logger.error(f"Failed to get asset {asset_id}: {e}")
            raise AdapterError(f"Failed to retrieve asset: {e}") from e

    async def list_by_workspace(
        self,
        workspace_id: str,
        limit: int = 50,
        offset: int = 0,
        asset_type: Optional[AssetType] = None,
    ) -> Tuple[list[Asset], int]:
        """List assets for a workspace."""
        try:
            count_query = (
                self._client.table("assets")
                .select("id", count="exact")
                .eq("workspace_id", workspace_id)
            )
            if asset_type:
                count_query = count_query.eq("asset_type", asset_type.value)

            count_result = count_query.execute()
            total = int(getattr(count_result, "count", 0) or 0)

            query = (
                self._client.table("assets")
                .select("*")
                .eq("workspace_id", workspace_id)
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
            )
            if asset_type:
                query = query.eq("asset_type", asset_type.value)

            result = query.execute()
            rows = result.data or []

            return [Asset.from_dict(row) for row in rows], total
        except Exception as e:
            logger.error(f"Failed to list assets for workspace {workspace_id}: {e}")
            raise AdapterError(f"Failed to list assets: {e}") from e

    async def save(self, asset: Asset) -> Asset:
        """Save an asset."""
        data = asset.to_dict()

        if data.get("created_at") is None:
            del data["created_at"]
        if data.get("updated_at") is None:
            del data["updated_at"]

        try:
            result = self._client.table("assets").upsert(data).execute()

            if not result.data:
                raise AdapterError("Failed to save asset: no data returned")

            return Asset.from_dict(result.data[0])
        except AdapterError:
            raise
        except Exception as e:
            logger.error(f"Failed to save asset {asset.id}: {e}")
            raise AdapterError(f"Failed to save asset: {e}") from e

    async def delete(self, asset_id: str, workspace_id: str) -> bool:
        """Delete an asset."""
        try:
            result = (
                self._client.table("assets")
                .delete()
                .eq("id", asset_id)
                .eq("workspace_id", workspace_id)
                .execute()
            )

            return result.data is not None and len(result.data) > 0
        except Exception as e:
            logger.error(f"Failed to delete asset {asset_id}: {e}")
            raise AdapterError(f"Failed to delete asset: {e}") from e
