"""Storage manager for Supabase Storage operations."""

import logging
from typing import Any, Dict, Optional

from supabase import Client, create_client

logger = logging.getLogger(__name__)


class StorageManager:
    """Manages Supabase Storage operations."""
    
    def __init__(self, supabase_url: str, service_key: str):
        """Initialize storage manager.
        
        Args:
            supabase_url: Supabase project URL
            service_key: Supabase service role key
        """
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
        """Create a storage bucket if it doesn't exist.
        
        Args:
            name: Bucket name
            public: Whether bucket should be publicly accessible
            
        Returns:
            True if bucket exists or was created successfully
        """
        try:
            # Check if bucket exists
            buckets = self.client.storage.list_buckets()
            if any(b.name == name for b in buckets):
                logger.info(f"Bucket '{name}' already exists")
                return True
            
            # Create bucket
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
        """Create a signed URL for direct file upload.
        
        Args:
            bucket: Target bucket name
            path: File path within bucket
            
        Returns:
            Dict containing signed URL, token, and path, or None if creation failed
        """
        try:
            result: Any = self.client.storage.from_(bucket).create_signed_upload_url(path=path)

            signed_url = None
            token = None

            if isinstance(result, dict):
                signed_url = result.get("signed_url") or result.get("signedUrl")
                token = result.get("token")
            else:
                signed_url = getattr(result, "signed_url", None) or getattr(result, "signedUrl", None)
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
        """Delete an object from storage.
        
        Args:
            bucket: Bucket name
            path: Object path within bucket
            
        Returns:
            True if deletion succeeded
        """
        try:
            self.client.storage.from_(bucket).remove([path])
            logger.info(f"Deleted object '{path}' from bucket '{bucket}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete object '{path}': {e}")
            return False
    
    def get_public_url(self, bucket: str, path: str) -> str:
        """Get the public URL for an object.
        
        Args:
            bucket: Bucket name
            path: Object path within bucket
            
        Returns:
            Public URL string
        """
        return f"{self.supabase_url}/storage/v1/object/public/{bucket}/{path}"
    
    async def file_exists(self, bucket: str, path: str) -> bool:
        """Check if a file exists in storage.
        
        Args:
            bucket: Bucket name
            path: Object path within bucket
            
        Returns:
            True if file exists
        """
        try:
            return bool(self.client.storage.from_(bucket).exists(path))
        except Exception:
            return False
