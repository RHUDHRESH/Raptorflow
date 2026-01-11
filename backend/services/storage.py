"""
Google Cloud Storage Service
Handles file uploads and signed URLs
"""

import logging
import os
from datetime import timedelta
from typing import Optional, Union

from google.cloud import storage

# Configure logging
logger = logging.getLogger(__name__)


class GCSStorageService:
    """
    Google Cloud Storage Service
    Uses Application Default Credentials (ADC) or explicit credentials
    """

    def __init__(self):
        self.bucket_name = os.getenv("GCS_BUCKET_NAME", "raptorflow-uploads")
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.client = None

        # Initialize client lazily to avoid startup errors if creds missing
        self._check_config()

    def _check_config(self):
        """Check if configuration is present"""
        if not self.bucket_name:
            logger.warning("GCS_BUCKET_NAME not set for GCSStorageService")

    def _get_client(self) -> Optional[storage.Client]:
        """Get or create storage client"""
        if self.client:
            return self.client

        try:
            # Tries to use ADC or credentials from env
            self.client = storage.Client(project=self.project_id)
            return self.client
        except Exception as e:
            logger.error(f"Failed to initialize GCS client: {e}")
            return None

    def upload_file(
        self,
        file_obj,
        destination_blob_name: str,
        content_type: str = "application/octet-stream",
    ) -> Optional[str]:
        """
        Uploads a file-like object to the bucket.
        Returns the public URL or gs:// URI.
        """
        client = self._get_client()
        if not client:
            return None

        try:
            bucket = client.bucket(self.bucket_name)
            blob = bucket.blob(destination_blob_name)

            # Reset file pointer if needed
            if hasattr(file_obj, "seek"):
                file_obj.seek(0)

            blob.upload_from_file(file_obj, content_type=content_type)

            logger.info(f"File uploaded to {self.bucket_name}/{destination_blob_name}")

            # Return a useful identifier
            # If bucket is public: blob.public_url
            # For now, let's return the GS URI which is unambiguous
            return f"gs://{self.bucket_name}/{destination_blob_name}"

        except Exception as e:
            logger.error(f"Failed to upload file to GCS: {e}")
            return None

    def generate_signed_url(self, blob_name: str, expiration=3600) -> Optional[str]:
        """Generate a signed URL for reading a blob"""
        client = self._get_client()
        if not client:
            return None

        try:
            bucket = client.bucket(self.bucket_name)
            blob = bucket.blob(blob_name)

            url = blob.generate_signed_url(
                version="v4", expiration=timedelta(seconds=expiration), method="GET"
            )
            return url
        except Exception as e:
            logger.error(f"Failed to generate signed URL: {e}")
            return None


# Singleton
storage_service = GCSStorageService()
