import logging
from datetime import timedelta
from typing import Optional

from google.cloud import storage

logger = logging.getLogger(__name__)


class GCSLifecycleManager:
    """
    Industrial GCS Lifecycle Manager for automated object management.
    """

    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self._client: Optional[storage.Client] = None

    @property
    def client(self) -> storage.Client:
        if self._client is None:
            self._client = storage.Client()
        return self._client

    def set_lifecycle_rule(self, storage_class: str = "STANDARD", age_days: int = 30):
        """Set lifecycle rule for bucket objects."""
        bucket = self.client.bucket(self.bucket_name)
        lifecycle_rules = [
            {
                "action": {"type": "SetStorageClass", "storageClass": storage_class},
                "condition": {"age": age_days},
            }
        ]
        bucket.lifecycle_rules = lifecycle_rules
        bucket.patch()
        logger.info(f"Lifecycle rule set for bucket {self.bucket_name}")


class BrandAssetManager:
    """
    Industrial Manager for Brand Assets (Logos, Fonts, etc.).
    Handles uploads to GCS and public URL resolution.
    Enhanced with raw asset upload capabilities.
    """

    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self._client: Optional[storage.Client] = None

    @property
    def client(self) -> storage.Client:
        if self._client is None:
            self._client = storage.Client()
        return self._client

    def upload_logo(
        self, file_content: bytes, filename: str, content_type: str, tenant_id: str
    ) -> str:
        """
        Uploads a logo to GCS and returns the blob path.
        """
        try:
            bucket = self.client.get_bucket(self.bucket_name)
            # Isolated path: {tenant_id}/assets/logos/{filename}
            blob = bucket.blob(f"{tenant_id}/assets/logos/{filename}")

            blob.upload_from_string(file_content, content_type=content_type)

            logger.info(f"Successfully uploaded logo: {filename} to {self.bucket_name}")
            return blob.name
        except Exception as e:
            logger.error(f"Failed to upload logo: {e}")
            raise e

    def upload_raw_asset(
        self, file_content: bytes, filename: str, content_type: str, tenant_id: str
    ) -> str:
        """
        Uploads a raw asset (PDF, PPTX, DOCX) to GCS and returns the public URL.
        """
        try:
            bucket = self.client.get_bucket(self.bucket_name)
            blob = bucket.blob(f"{tenant_id}/assets/raw/{filename}")

            blob.upload_from_string(file_content, content_type=content_type)
            blob.make_public()

            logger.info(
                f"Successfully uploaded raw asset: {filename} to {self.bucket_name}"
            )
            return blob.public_url
        except Exception as e:
            logger.error(f"Failed to upload raw asset: {e}")
            raise e

    def generate_signed_url(self, blob_name: str, expiration_minutes: int = 15) -> str:
        """
        Generates a signed URL for a blob.
        """
        bucket = self.client.get_bucket(self.bucket_name)
        blob = bucket.blob(blob_name)
        return blob.generate_signed_url(
            expiration=timedelta(minutes=expiration_minutes),
            version="v4",
        )

    def make_blob_public(self, blob_name: str) -> str:
        """
        Makes a blob public and returns its public URL.
        """
        bucket = self.client.get_bucket(self.bucket_name)
        blob = bucket.blob(blob_name)
        blob.make_public()
        return blob.public_url
