"""Storage manager for Supabase Storage operations."""

import logging
from typing import Any, Dict, Optional

from supabase import Client, create_client

logger = logging.getLogger(__name__)


class StorageManager:
    """Manages Supabase Storage operations."""

    def __init__(self, supabase_url: str, service_key: str):
        """Initialize storage manager."""
        self.supabase_url = supabase_url
        self.service_key = service_key
        self._client: Optional[Client] = None

    @property
    def client(self) -> Client:
        """Get or create Supabase client."""
        if self._client is None:
            self._client = create_client(self.supabase_url, self.service_key)
        return self._client

    async def create_bucket(self, name: str, public: bool = True) -> bool:
        """Create a storage bucket if it doesn't exist."""
        try:
            buckets = self.client.storage.list_buckets()
            for bucket in buckets:
                bucket_name = getattr(bucket, "name", None) or (
                    bucket.get("name") if isinstance(bucket, dict) else None
                )
                if bucket_name != name:
                    continue

                bucket_public = getattr(bucket, "public", None)
                if bucket_public is None and isinstance(bucket, dict):
                    bucket_public = bucket.get("public")

                if bucket_public is not None and bool(bucket_public) != bool(public):
                    self.client.storage.update_bucket(name, {"public": public})
                    logger.info("Updated bucket '%s' public=%s", name, public)
                else:
                    logger.info("Bucket '%s' already exists", name)
                return True

            self.client.storage.create_bucket(name, options={"public": public})
            logger.info(f"Created bucket '{name}' (public={public})")
            return True

        except Exception as e:
            logger.error(f"Failed to create bucket '{name}': {e}")
            return False

    async def create_signed_upload_url(
        self,
        bucket: str,
        path: str,
    ) -> Optional[Dict[str, str]]:
        """Create a signed URL for direct file upload."""
        try:
            result: Any = self.client.storage.from_(bucket).create_signed_upload_url(
                path=path
            )

            signed_url = None
            token = None

            if isinstance(result, dict):
                signed_url = result.get("signed_url") or result.get("signedUrl")
                token = result.get("token")
            else:
                signed_url = getattr(result, "signed_url", None) or getattr(
                    result, "signedUrl", None
                )
                token = getattr(result, "token", None)

            if not signed_url or not token:
                logger.error("Signed upload URL response missing url/token: %s", result)
                return None

            return {
                "signed_url": str(signed_url),
                "token": str(token),
                "path": path,
            }
        except Exception as e:
            logger.error(f"Failed to create signed upload URL: {e}")
            return None

    async def delete_object(self, bucket: str, path: str) -> bool:
        """Delete an object from storage."""
        try:
            self.client.storage.from_(bucket).remove([path])
            logger.info(f"Deleted object '{path}' from bucket '{bucket}'")
            return True

        except Exception as e:
            logger.error(f"Failed to delete object '{path}': {e}")
            return False

    def get_public_url(self, bucket: str, path: str) -> str:
        """Get the public URL for an object."""
        return f"{self.supabase_url}/storage/v1/object/public/{bucket}/{path}"

    async def file_exists(self, bucket: str, path: str) -> bool:
        """Check if a file exists in storage."""
        try:
            return bool(self.client.storage.from_(bucket).exists(path))
        except Exception:
            return False


_storage_manager: Optional[StorageManager] = None


def get_storage_manager() -> StorageManager:
    """Get the global storage manager instance."""
    global _storage_manager
    if _storage_manager is None:
        from backend.core.database.supabase import get_supabase_client

        client = get_supabase_client()
        _storage_manager = StorageManager(
            supabase_url=client.supabase_url, service_key=client.supabase_key
        )
    return _storage_manager
