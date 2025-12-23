import logging
from typing import Optional
from google.cloud import storage

logger = logging.getLogger("raptorflow.services.storage")

class GCSLifecycleManager:
    """
    Manager for GCS object lifecycle and archival.
    Moves data between raw, gold, and archival zones.
    """

    def __init__(self, source_bucket: str, target_bucket: str):
        self.source_bucket_name = source_bucket
        self.target_bucket_name = target_bucket
        self._client: Optional[storage.Client] = None

    @property
    def client(self) -> storage.Client:
        if self._client is None:
            self._client = storage.Client()
        return self._client

    def archive_logs(self, prefix: str) -> bool:
        """
        Moves blobs from source bucket to target bucket under the same prefix.
        """
        try:
            source_bucket = self.client.get_bucket(self.source_bucket_name)
            target_bucket = self.client.get_bucket(self.target_bucket_name)
            
            blobs = source_bucket.list_blobs(prefix=prefix)
            
            count = 0
            for blob in blobs:
                # Copy to target
                source_bucket.copy_blob(blob, target_bucket, blob.name)
                # Delete from source
                source_bucket.delete_blob(blob.name)
                count += 1
            
            logger.info(f"Archived {count} blobs from {self.source_bucket_name} to {self.target_bucket_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to archive logs: {e}")
            return False
