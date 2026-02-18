"""
Asset application layer - Ports.
"""

from typing import Protocol, Optional, Tuple
from backend.features.asset.domain.entities import Asset, AssetType


class AssetRepository(Protocol):
    """Port for asset persistence."""

    async def get_by_id(self, asset_id: str, workspace_id: str) -> Optional[Asset]: ...

    async def list_by_workspace(
        self,
        workspace_id: str,
        limit: int = 50,
        offset: int = 0,
        asset_type: Optional[AssetType] = None,
    ) -> Tuple[list[Asset], int]: ...

    async def save(self, asset: Asset) -> Asset: ...

    async def delete(self, asset_id: str, workspace_id: str) -> bool: ...


class StorageService(Protocol):
    """Port for file storage operations."""

    async def create_signed_upload_url(
        self, bucket: str, path: str
    ) -> Optional[dict]: ...

    async def delete_object(self, bucket: str, path: str) -> bool: ...

    def get_public_url(self, bucket: str, path: str) -> str: ...

    async def create_bucket(self, bucket: str, public: bool = True) -> bool: ...
