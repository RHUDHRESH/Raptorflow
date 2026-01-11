"""
Google Secret Manager integration for Raptorflow.

Provides secure storage and retrieval of sensitive data
like API keys, passwords, and configuration secrets.
"""

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from google.api_core import exceptions
from google.cloud import secretmanager

from .gcp import get_gcp_client

logger = logging.getLogger(__name__)


class SecretType(Enum):
    """Secret types."""

    API_KEY = "api_key"
    PASSWORD = "password"
    CERTIFICATE = "certificate"
    CONFIGURATION = "configuration"
    DATABASE = "database"
    ENCRYPTION_KEY = "encryption_key"
    TOKEN = "token"
    WEBHOOK = "webhook"


@dataclass
class SecretMetadata:
    """Secret metadata."""

    secret_id: str
    name: str
    secret_type: SecretType
    description: str
    workspace_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    version_count: int = 0
    labels: Dict[str, str] = None

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.secret_type, str):
            self.secret_type = SecretType(self.secret_type)

        if self.labels is None:
            self.labels = {}


@dataclass
class SecretVersion:
    """Secret version information."""

    secret_id: str
    version_id: str
    state: str
    created_at: datetime
    destroyed_at: Optional[datetime] = None
    is_destroyed: bool = False


class SecretsManager:
    """Google Secret Manager client for Raptorflow."""

    def __init__(self):
        self.gcp_client = get_gcp_client()
        self.logger = logging.getLogger("secrets_manager")

        # Get Secret Manager client
        self.client = secretmanager.SecretManagerServiceClient(
            credentials=self.gcp_client.get_credentials()
        )

        if not self.client:
            raise RuntimeError("Secret Manager client not available")

        # Project ID
        self.project_id = self.gcp_client.get_project_id()

        # Default secret prefix
        self.secret_prefix = os.getenv("SECRETS_PREFIX", "raptorflow")

        # Cache for frequently accessed secrets
        self._secret_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = int(os.getenv("SECRETS_CACHE_TTL", "300"))  # 5 minutes

    def _get_secret_path(self, secret_id: str) -> str:
        """Get full secret path."""
        return f"projects/{self.project_id}/secrets/{self.secret_prefix}-{secret_id}"

    def _get_version_path(self, secret_id: str, version_id: str = "latest") -> str:
        """Get full secret version path."""
        secret_path = self._get_secret_path(secret_id)
        return f"{secret_path}/versions/{version_id}"

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached secret is still valid."""
        if cache_key not in self._secret_cache:
            return False

        cached_time = self._secret_cache[cache_key].get("cached_at")
        if not cached_time:
            return False

        age_seconds = (datetime.now() - cached_time).total_seconds()
        return age_seconds < self._cache_ttl

    def _update_cache(
        self, secret_id: str, value: str, metadata: Optional[Dict[str, Any]] = None
    ):
        """Update secret cache."""
        cache_key = f"{self.secret_prefix}-{secret_id}"
        self._secret_cache[cache_key] = {
            "value": value,
            "metadata": metadata or {},
            "cached_at": datetime.now(),
        }

    def _clear_cache(self, secret_id: Optional[str] = None):
        """Clear secret cache."""
        if secret_id:
            cache_key = f"{self.secret_prefix}-{secret_id}"
            if cache_key in self._secret_cache:
                del self._secret_cache[cache_key]
        else:
            self._secret_cache.clear()

    async def create_secret(
        self,
        secret_id: str,
        secret_value: str,
        secret_type: SecretType = SecretType.CONFIGURATION,
        description: str = "",
        workspace_id: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
    ) -> bool:
        """Create a new secret."""
        try:
            secret_path = self._get_secret_path(secret_id)

            # Check if secret already exists
            try:
                self.client.get_secret(name=secret_path)
                self.logger.warning(f"Secret {secret_id} already exists")
                return False
            except exceptions.NotFound:
                pass

            # Prepare secret
            secret = secretmanager.Secret(
                name=secret_path,
                replication=secretmanager.Replication(
                    automatic=secretmanager.Replication.Automatic()
                ),
                labels=labels or {},
            )

            # Add metadata labels
            if secret_type:
                secret.labels["secret_type"] = secret_type.value

            if workspace_id:
                secret.labels["workspace_id"] = workspace_id

            # Create secret
            created_secret = self.client.create_secret(
                request={"parent": f"projects/{self.project_id}", "secret": secret}
            )

            # Add secret value
            await self.set_secret(secret_id, secret_value)

            self.logger.info(f"Created secret: {secret_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to create secret {secret_id}: {e}")
            return False

    async def set_secret(
        self, secret_id: str, secret_value: str, version_id: Optional[str] = None
    ) -> bool:
        """Set secret value (create new version)."""
        try:
            secret_path = self._get_secret_path(secret_id)
            version_path = self._get_version_path(secret_id, version_id or "latest")

            # Prepare secret payload
            payload = secret_value.encode("UTF-8")

            # Add secret version
            response = self.client.add_secret_version(
                request={"parent": secret_path, "payload": {"data": payload}}
            )

            # Update cache
            self._update_cache(secret_id, secret_value)

            self.logger.info(f"Set secret value for: {secret_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to set secret value for {secret_id}: {e}")
            return False

    async def get_secret(
        self, secret_id: str, version_id: str = "latest", use_cache: bool = True
    ) -> Optional[str]:
        """Get secret value."""
        try:
            # Check cache first
            if use_cache and version_id == "latest":
                cache_key = f"{self.secret_prefix}-{secret_id}"
                if self._is_cache_valid(cache_key):
                    return self._secret_cache[cache_key]["value"]

            version_path = self._get_version_path(secret_id, version_id)

            # Access secret version
            response = self.client.access_secret_version(name=version_path)

            # Decode secret value
            secret_value = response.payload.data.decode("UTF-8")

            # Update cache if latest version
            if use_cache and version_id == "latest":
                self._update_cache(secret_id, secret_value)

            return secret_value

        except exceptions.NotFound:
            self.logger.warning(f"Secret {secret_id} version {version_id} not found")
            return None
        except Exception as e:
            self.logger.error(f"Failed to get secret {secret_id}: {e}")
            return None

    async def get_secret_json(
        self, secret_id: str, version_id: str = "latest", use_cache: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Get secret value as JSON."""
        try:
            secret_value = await self.get_secret(secret_id, version_id, use_cache)

            if secret_value:
                return json.loads(secret_value)

            return None

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse secret {secret_id} as JSON: {e}")
            return None

    async def update_secret(
        self,
        secret_id: str,
        secret_value: str,
        description: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
    ) -> bool:
        """Update secret metadata and create new version."""
        try:
            secret_path = self._get_secret_path(secret_id)

            # Get existing secret
            secret = self.client.get_secret(name=secret_path)

            # Update fields
            update_mask = []

            if description is not None:
                secret.description = description
                update_mask.append("description")

            if labels is not None:
                secret.labels.update(labels)
                update_mask.append("labels")

            # Update secret if needed
            if update_mask:
                self.client.update_secret(
                    request={"secret": secret, "update_mask": {"paths": update_mask}}
                )

            # Add new version
            await self.set_secret(secret_id, secret_value)

            # Clear cache
            self._clear_cache(secret_id)

            self.logger.info(f"Updated secret: {secret_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to update secret {secret_id}: {e}")
            return False

    async def delete_secret(self, secret_id: str) -> bool:
        """Delete a secret."""
        try:
            secret_path = self._get_secret_path(secret_id)

            # Clear cache
            self._clear_cache(secret_id)

            # Delete secret
            self.client.delete_secret(name=secret_path)

            self.logger.info(f"Deleted secret: {secret_id}")
            return True

        except exceptions.NotFound:
            self.logger.warning(f"Secret {secret_id} not found for deletion")
            return False
        except Exception as e:
            self.logger.error(f"Failed to delete secret {secret_id}: {e}")
            return False

    async def destroy_secret_version(self, secret_id: str, version_id: str) -> bool:
        """Destroy a specific secret version."""
        try:
            version_path = self._get_version_path(secret_id, version_id)

            # Destroy version
            self.client.destroy_secret_version(name=version_path)

            # Clear cache if latest version
            if version_id == "latest":
                self._clear_cache(secret_id)

            self.logger.info(f"Destroyed secret version: {secret_id}/{version_id}")
            return True

        except Exception as e:
            self.logger.error(
                f"Failed to destroy secret version {secret_id}/{version_id}: {e}"
            )
            return False

    async def enable_secret_version(self, secret_id: str, version_id: str) -> bool:
        """Enable a secret version."""
        try:
            version_path = self._get_version_path(secret_id, version_id)

            # Enable version
            self.client.enable_secret_version(name=version_path)

            self.logger.info(f"Enabled secret version: {secret_id}/{version_id}")
            return True

        except Exception as e:
            self.logger.error(
                f"Failed to enable secret version {secret_id}/{version_id}: {e}"
            )
            return False

    async def disable_secret_version(self, secret_id: str, version_id: str) -> bool:
        """Disable a secret version."""
        try:
            version_path = self._get_version_path(secret_id, version_id)

            # Disable version
            self.client.disable_secret_version(name=version_path)

            # Clear cache if latest version
            if version_id == "latest":
                self._clear_cache(secret_id)

            self.logger.info(f"Disabled secret version: {secret_id}/{version_id}")
            return True

        except Exception as e:
            self.logger.error(
                f"Failed to disable secret version {secret_id}/{version_id}: {e}"
            )
            return False

    async def list_secrets(
        self,
        filter_expression: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> List[SecretMetadata]:
        """List secrets."""
        try:
            parent = f"projects/{self.project_id}"

            # Build filter
            if workspace_id:
                filter_expr = f"labels.workspace_id={workspace_id}"
                if filter_expression:
                    filter_expr += f" AND {filter_expression}"
            elif filter_expression:
                filter_expr = filter_expression
            else:
                filter_expr = None

            # List secrets
            secrets = []
            for secret in self.client.list_secrets(
                request={"parent": parent, "filter": filter_expr}
            ):
                # Extract secret ID from full path
                secret_name = secret.name.split("/")[-1]
                if secret_name.startswith(f"{self.secret_prefix}-"):
                    secret_id = secret_name[len(f"{self.secret_prefix}-") :]

                    # Get version count
                    version_count = 0
                    try:
                        versions = list(
                            self.client.list_secret_versions(
                                request={"parent": secret.name}
                            )
                        )
                        version_count = len(versions)
                    except:
                        pass

                    # Create metadata
                    metadata = SecretMetadata(
                        secret_id=secret_id,
                        name=secret.name,
                        secret_type=SecretType(
                            secret.labels.get("secret_type", "configuration")
                        ),
                        description=secret.description or "",
                        workspace_id=secret.labels.get("workspace_id"),
                        created_at=(
                            secret.create_time.ToDatetime()
                            if secret.create_time
                            else None
                        ),
                        updated_at=None,  # Not available in list response
                        version_count=version_count,
                        labels=dict(secret.labels),
                    )

                    secrets.append(metadata)

            return secrets

        except Exception as e:
            self.logger.error(f"Failed to list secrets: {e}")
            return []

    async def list_secret_versions(self, secret_id: str) -> List[SecretVersion]:
        """List versions of a secret."""
        try:
            secret_path = self._get_secret_path(secret_id)

            versions = []
            for version in self.client.list_secret_versions(
                request={"parent": secret_path}
            ):
                # Extract version ID from full path
                version_id = version.name.split("/")[-1]

                secret_version = SecretVersion(
                    secret_id=secret_id,
                    version_id=version_id,
                    state=version.state.name,
                    created_at=(
                        version.create_time.ToDatetime()
                        if version.create_time
                        else datetime.now()
                    ),
                    destroyed_at=(
                        version.destroy_time.ToDatetime()
                        if version.destroy_time
                        else None
                    ),
                    is_destroyed=version.state
                    == secretmanager.SecretVersion.State.DESTROYED,
                )

                versions.append(secret_version)

            return versions

        except Exception as e:
            self.logger.error(f"Failed to list secret versions for {secret_id}: {e}")
            return []

    async def get_secret_metadata(self, secret_id: str) -> Optional[SecretMetadata]:
        """Get secret metadata."""
        try:
            secret_path = self._get_secret_path(secret_id)
            secret = self.client.get_secret(name=secret_path)

            # Get version count
            version_count = 0
            try:
                versions = list(
                    self.client.list_secret_versions(request={"parent": secret.name})
                )
                version_count = len(versions)
            except:
                pass

            return SecretMetadata(
                secret_id=secret_id,
                name=secret.name,
                secret_type=SecretType(
                    secret.labels.get("secret_type", "configuration")
                ),
                description=secret.description or "",
                workspace_id=secret.labels.get("workspace_id"),
                created_at=(
                    secret.create_time.ToDatetime() if secret.create_time else None
                ),
                updated_at=None,  # Not available in get response
                version_count=version_count,
                labels=dict(secret.labels),
            )

        except exceptions.NotFound:
            self.logger.warning(f"Secret {secret_id} not found")
            return None
        except Exception as e:
            self.logger.error(f"Failed to get secret metadata for {secret_id}: {e}")
            return None

    async def rotate_secret(
        self, secret_id: str, new_value: str, keep_old_versions: int = 2
    ) -> bool:
        """Rotate a secret (create new version and clean up old ones)."""
        try:
            # Add new version
            await self.set_secret(secret_id, new_value)

            # Get all versions
            versions = await self.list_secret_versions(secret_id)

            # Sort by creation time (newest first)
            versions.sort(key=lambda v: v.created_at, reverse=True)

            # Keep only the specified number of enabled versions
            enabled_versions = [v for v in versions if not v.is_destroyed]

            if len(enabled_versions) > keep_old_versions:
                # Destroy old versions
                for old_version in enabled_versions[keep_old_versions:]:
                    await self.destroy_secret_version(secret_id, old_version.version_id)

            self.logger.info(f"Rotated secret: {secret_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to rotate secret {secret_id}: {e}")
            return False

    async def get_workspace_secrets(self, workspace_id: str) -> List[SecretMetadata]:
        """Get all secrets for a workspace."""
        return await self.list_secrets(workspace_id=workspace_id)

    async def create_workspace_secret(
        self,
        workspace_id: str,
        secret_id: str,
        secret_value: str,
        secret_type: SecretType = SecretType.CONFIGURATION,
        description: str = "",
    ) -> bool:
        """Create a workspace-specific secret."""
        labels = {"workspace_id": workspace_id}
        return await self.create_secret(
            secret_id, secret_value, secret_type, description, workspace_id, labels
        )

    def clear_cache(self, secret_id: Optional[str] = None):
        """Clear secret cache."""
        self._clear_cache(secret_id)

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "cache_size": len(self._secret_cache),
            "cache_ttl_seconds": self._cache_ttl,
            "cached_secrets": list(self._secret_cache.keys()),
        }


# Global Secrets Manager instance
_secrets_manager: Optional[SecretsManager] = None


def get_secrets_manager() -> SecretsManager:
    """Get global Secrets Manager instance."""
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
    return _secrets_manager


# Convenience functions
async def get_secret(secret_id: str, version_id: str = "latest") -> Optional[str]:
    """Get secret value."""
    manager = get_secrets_manager()
    return await manager.get_secret(secret_id, version_id)


async def set_secret(secret_id: str, secret_value: str) -> bool:
    """Set secret value."""
    manager = get_secrets_manager()
    return await manager.set_secret(secret_id, secret_value)


async def create_secret(
    secret_id: str,
    secret_value: str,
    secret_type: SecretType = SecretType.CONFIGURATION,
    description: str = "",
) -> bool:
    """Create a new secret."""
    manager = get_secrets_manager()
    return await manager.create_secret(
        secret_id, secret_value, secret_type, description
    )


async def delete_secret(secret_id: str) -> bool:
    """Delete a secret."""
    manager = get_secrets_manager()
    return await manager.delete_secret(secret_id)


async def get_secret_json(secret_id: str) -> Optional[Dict[str, Any]]:
    """Get secret value as JSON."""
    manager = get_secrets_manager()
    return await manager.get_secret_json(secret_id)


async def create_workspace_secret(
    workspace_id: str,
    secret_id: str,
    secret_value: str,
    secret_type: SecretType = SecretType.CONFIGURATION,
    description: str = "",
) -> bool:
    """Create a workspace-specific secret."""
    manager = get_secrets_manager()
    return await manager.create_workspace_secret(
        workspace_id, secret_id, secret_value, secret_type, description
    )


async def get_workspace_secrets(workspace_id: str) -> List[SecretMetadata]:
    """Get all secrets for a workspace."""
    manager = get_secrets_manager()
    return await manager.get_workspace_secrets(workspace_id)


# Environment variable fallback
class SecretEnvVar:
    """Environment variable that falls back to Secret Manager."""

    def __init__(
        self,
        secret_id: str,
        env_var: Optional[str] = None,
        default: Optional[str] = None,
    ):
        self.secret_id = secret_id
        self.env_var = env_var or secret_id.upper()
        self.default = default
        self._value = None

    async def get_value(self) -> Optional[str]:
        """Get secret value with fallback."""
        if self._value is not None:
            return self._value

        # Try environment variable first
        env_value = os.getenv(self.env_var)
        if env_value:
            self._value = env_value
            return env_value

        # Try Secret Manager
        manager = get_secrets_manager()
        secret_value = await manager.get_secret(self.secret_id)
        if secret_value:
            self._value = secret_value
            return secret_value

        # Return default
        return self.default

    async def get_json(self) -> Optional[Dict[str, Any]]:
        """Get secret value as JSON."""
        value = await self.get_value()
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass
        return None


# Common secret getters
async def get_database_url() -> Optional[str]:
    """Get database URL from secrets."""
    return await get_secret("database_url")


async def get_redis_url() -> Optional[str]:
    """Get Redis URL from secrets."""
    return await get_secret("redis_url")


async def get_api_key(service_name: str) -> Optional[str]:
    """Get API key for a service."""
    return await get_secret(f"{service_name}_api_key")


async def get_encryption_key() -> Optional[str]:
    """Get encryption key."""
    return await get_secret("encryption_key")
