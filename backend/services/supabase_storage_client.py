"""
Supabase Storage Client
Provides a Python client for Supabase Storage operations
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import httpx

from .utils.storage_paths import (
    generate_intelligence_path,
    generate_user_path,
    generate_workspace_path,
    get_bucket_for_category,
    parse_storage_path,
)

logger = logging.getLogger(__name__)


class SupabaseStorageClient:
    """Supabase Storage client for file operations"""

    def __init__(self, url: str, service_key: str):
        self.base_url = url.rstrip("/")
        self.service_key = service_key
        self.headers = {
            "Authorization": f"Bearer {service_key}",
            "apikey": service_key,
            "Content-Type": "application/json",
        }
        self.client = httpx.Client(timeout=30.0)

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to Supabase Storage API"""
        url = urljoin(self.base_url, endpoint)
        response = self.client.request(method, url, headers=self.headers, **kwargs)

        if response.status_code >= 400:
            error_data = response.json() if response.content else {}
            raise Exception(
                f"Supabase Storage error: {response.status_code} - {error_data}"
            )

        return response.json()

    def upload_file(
        self,
        bucket: str,
        path: str,
        file_content: Union[bytes, str],
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Upload file to Supabase Storage"""
        if isinstance(file_content, str):
            file_content = file_content.encode("utf-8")

        headers = {"Content-Type": content_type, **self.headers}

        # Add metadata as headers
        if metadata:
            for key, value in metadata.items():
                headers[f"x-supabase-{key}"] = value

        endpoint = f"/storage/v1/object/{bucket}/{path}"
        response = self.client.post(endpoint, content=file_content, headers=headers)

        if response.status_code >= 400:
            error_data = response.json() if response.content else {}
            raise Exception(f"Upload error: {response.status_code} - {error_data}")

        return {"success": True, "path": path}

    def download_file(self, bucket: str, path: str) -> bytes:
        """Download file from Supabase Storage"""
        endpoint = f"/storage/v1/object/{bucket}/{path}"
        response = self.client.get(endpoint, headers=self.headers)

        if response.status_code >= 400:
            error_data = response.json() if response.content else {}
            raise Exception(f"Download error: {response.status_code} - {error_data}")

        return response.content

    def delete_file(self, bucket: str, path: str) -> Dict[str, Any]:
        """Delete file from Supabase Storage"""
        endpoint = f"/storage/v1/object/{bucket}/{path}"
        response = self.client.delete(endpoint, headers=self.headers)

        if response.status_code >= 400:
            error_data = response.json() if response.content else {}
            raise Exception(f"Delete error: {response.status_code} - {error_data}")

        return {"success": True}

    def get_public_url(self, bucket: str, path: str) -> str:
        """Get public URL for file"""
        return f"{self.base_url}/storage/v1/object/public/{bucket}/{path}"

    def create_signed_url(
        self, bucket: str, path: str, expires_in: int = 3600
    ) -> Dict[str, Any]:
        """Create signed URL for file access"""
        endpoint = f"/storage/v1/object/{bucket}/{path}"
        params = {"expiresIn": str(expires_in)}

        response = self.client.post(
            f"{endpoint}/sign", headers=self.headers, params=params
        )

        if response.status_code >= 400:
            error_data = response.json() if response.content else {}
            raise Exception(f"Signed URL error: {response.status_code} - {error_data}")

        return response.json()

    def list_files(self, bucket: str, prefix: str = "") -> List[Dict[str, Any]]:
        """List files in bucket with optional prefix"""
        endpoint = f"/storage/v1/object/list/{bucket}"
        params = {"prefix": prefix} if prefix else {}

        response = self.client.post(endpoint, headers=self.headers, params=params)

        if response.status_code >= 400:
            error_data = response.json() if response.content else {}
            raise Exception(f"List error: {response.status_code} - {error_data}")

        return response.json()

    def get_file_info(self, bucket: str, path: str) -> Dict[str, Any]:
        """Get file metadata"""
        endpoint = f"/storage/v1/object/info/{bucket}/{path}"
        response = self.client.get(endpoint, headers=self.headers)

        if response.status_code >= 400:
            error_data = response.json() if response.content else {}
            raise Exception(f"File info error: {response.status_code} - {error_data}")

        return response.json()

    # Convenience methods for Raptorflow patterns

    def upload_workspace_file(
        self,
        workspace_slug: str,
        category: str,
        filename: str,
        file_content: Union[bytes, str],
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Upload workspace file with standardized path"""
        bucket = get_bucket_for_category(category)
        path = generate_workspace_path(workspace_slug, category, filename)

        # Add default metadata
        if metadata is None:
            metadata = {}

        metadata.update(
            {
                "workspace_slug": workspace_slug,
                "category": category,
                "original_filename": filename,
            }
        )

        return self.upload_file(bucket, path, file_content, content_type, metadata)

    def upload_user_file(
        self,
        user_id: str,
        category: str,
        filename: str,
        file_content: Union[bytes, str],
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Upload user file with standardized path"""
        bucket = get_bucket_for_category(category)
        path = generate_user_path(user_id, category, filename)

        # Add default metadata
        if metadata is None:
            metadata = {}

        metadata.update(
            {"user_id": user_id, "category": category, "original_filename": filename}
        )

        return self.upload_file(bucket, path, file_content, content_type, metadata)

    def upload_intelligence_file(
        self,
        query_hash: str,
        filename: str,
        file_content: Union[bytes, str],
        content_type: str = "application/json",
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Upload intelligence file with standardized path"""
        bucket = get_bucket_for_category("intelligence")
        path = generate_intelligence_path(query_hash, filename)

        # Add default metadata
        if metadata is None:
            metadata = {}

        metadata.update(
            {
                "query_hash": query_hash,
                "category": "intelligence",
                "original_filename": filename,
            }
        )

        return self.upload_file(bucket, path, file_content, content_type, metadata)


def get_supabase_storage_client() -> SupabaseStorageClient:
    """Get configured Supabase Storage client"""
    url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_KEY")

    if not url or not service_key:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")

    return SupabaseStorageClient(url, service_key)
