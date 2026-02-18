"""
Storage Infrastructure - File storage abstraction.
"""

from __future__ import annotations

import logging
from typing import Any, BinaryIO, Dict, Optional

logger = logging.getLogger(__name__)


class StorageClient:
    """
    File storage client wrapping Supabase Storage.

    Example:
        storage = StorageClient()

        # Upload a file
        url = await storage.upload("assets", "file.pdf", file_data)

        # Download a file
        data = await storage.download("assets", "file.pdf")
    """

    def __init__(self, bucket: Optional[str] = None):
        self._bucket = bucket
        self._client = None
        self._initialized = False

    def _get_client(self):
        if self._client is None:
            from backend.infrastructure.storage.manager import get_storage_manager

            self._client = get_storage_manager()
        return self._client

    async def initialize(self) -> None:
        """Initialize the storage client."""
        self._client = self._get_client()
        self._initialized = True
        logger.info("Storage client initialized")

    async def upload(
        self,
        bucket: str,
        path: str,
        file: BinaryIO,
        content_type: Optional[str] = None,
    ) -> str:
        """Upload a file and return its public URL."""
        client = self._get_client()
        result = client.storage.from_(bucket).upload(
            path, file, {"content_type": content_type}
        )
        if result.get("error"):
            raise RuntimeError(f"Upload failed: {result['error']}")
        return client.storage.from_(bucket).get_public_url(path)

    async def download(self, bucket: str, path: str) -> bytes:
        """Download a file."""
        client = self._get_client()
        result = client.storage.from_(bucket).download(path)
        return result

    async def delete(self, bucket: str, path: str) -> bool:
        """Delete a file."""
        client = self._get_client()
        result = client.storage.from_(bucket).remove([path])
        return len(result) > 0

    async def list_files(self, bucket: str, path: str = "") -> list:
        """List files in a bucket path."""
        client = self._get_client()
        result = client.storage.from_(bucket).list(path)
        return result

    async def health_check(self) -> dict:
        """Check storage health."""
        try:
            client = self._get_client()
            client.storage.from_(self._bucket or "default").list()
            return {"status": "healthy"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


_storage_client: Optional[StorageClient] = None


def get_storage_client() -> StorageClient:
    """Get the global storage client instance."""
    global _storage_client
    if _storage_client is None:
        _storage_client = StorageClient()
    return _storage_client


__all__ = ["StorageClient", "get_storage_client"]
