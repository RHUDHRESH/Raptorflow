"""
Asset adapters - Storage implementation.
"""

from typing import TYPE_CHECKING, Optional

from backend.features.asset.application.ports import StorageService

if TYPE_CHECKING:
    from backend.infrastructure.storage.manager import StorageManager


class SupabaseStorageService(StorageService):
    """Supabase storage implementation of StorageService."""

    def __init__(self, storage_manager: "StorageManager") -> None:
        self._storage = storage_manager

    async def create_signed_upload_url(self, bucket: str, path: str) -> Optional[dict]:
        """Create a signed upload URL."""
        return await self._storage.create_signed_upload_url(bucket, path)

    async def delete_object(self, bucket: str, path: str) -> bool:
        """Delete an object from storage."""
        return await self._storage.delete_object(bucket, path)

    def get_public_url(self, bucket: str, path: str) -> str:
        """Get the public URL for an object."""
        return self._storage.get_public_url(bucket, path)

    async def create_bucket(self, bucket: str, public: bool = True) -> bool:
        """Create a storage bucket."""
        return await self._storage.create_bucket(bucket, public=public)
