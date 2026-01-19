"""
Production-ready API key management for RaptorFlow
Secure generation, storage, and validation of API keys
"""

import logging
import secrets
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from .security import hash_api_key, verify_api_key
from .supabase_mgr import get_supabase_client

logger = logging.getLogger(__name__)


@dataclass
class APIKeyInfo:
    """API key information"""

    id: str
    workspace_id: str
    name: str
    permissions: List[str]
    key_hash: str
    key_prefix: str  # First few characters for identification
    created_at: datetime
    last_used_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_active: bool = True
    usage_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data


class APIKeyManager:
    """Production-ready API key management"""

    def __init__(self):
        self.supabase = get_supabase_client()
        self.key_length = 32  # Length of the raw key
        self.prefix_length = 8  # Length of the prefix shown to users

    def generate_api_key(self) -> str:
        """
        Generate a cryptographically secure API key

        Returns:
            New API key string
        """
        return f"raptorf_{secrets.token_urlsafe(self.key_length)}"

    async def create_api_key(
        self,
        workspace_id: str,
        name: str,
        permissions: List[str],
        expires_in_days: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new API key

        Args:
            workspace_id: Workspace ID
            name: Key name/description
            permissions: List of permissions
            expires_in_days: Optional expiration in days

        Returns:
            API key info with the actual key (only returned once)
        """
        try:
            # Generate the key
            api_key = self.generate_api_key()
            key_hash = hash_api_key(api_key)
            key_prefix = api_key[: self.prefix_length]

            # Calculate expiration
            expires_at = None
            if expires_in_days:
                expires_at = datetime.now(timezone.utc) + timedelta(
                    days=expires_in_days
                )

            # Create API key record
            key_data = {
                "workspace_id": workspace_id,
                "name": name,
                "permissions": permissions,
                "key_hash": key_hash,
                "key_prefix": key_prefix,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "expires_at": expires_at.isoformat() if expires_at else None,
                "is_active": True,
                "usage_count": 0,
            }

            result = self.supabase.table("api_keys").insert(key_data).execute()

            if result.data:
                created_key = result.data[0]
                logger.info(
                    f"API key created for workspace {workspace_id}: {key_prefix}"
                )

                # Return key info with the actual key (only time it's shown)
                return {
                    "id": created_key["id"],
                    "workspace_id": created_key["workspace_id"],
                    "name": created_key["name"],
                    "permissions": created_key["permissions"],
                    "key": api_key,  # Only returned once
                    "key_prefix": created_key["key_prefix"],
                    "created_at": created_key["created_at"],
                    "expires_at": created_key["expires_at"],
                    "is_active": created_key["is_active"],
                }
            else:
                logger.error("Failed to create API key: No data returned")
                return None

        except Exception as e:
            logger.error(f"Error creating API key: {e}")
            return None

    async def validate_api_key(self, api_key: str) -> Optional[APIKeyInfo]:
        """
        Validate an API key and return its information

        Args:
            api_key: API key to validate

        Returns:
            APIKeyInfo if valid, None otherwise
        """
        try:
            # Get all active API keys (we need to check hash)
            result = (
                self.supabase.table("api_keys")
                .select("*")
                .eq("is_active", True)
                .execute()
            )

            if not result.data:
                return None

            # Check each key hash
            for key_record in result.data:
                if verify_api_key(api_key, key_record["key_hash"]):
                    # Check if expired
                    if key_record.get("expires_at"):
                        expires_at = datetime.fromisoformat(key_record["expires_at"])
                        if datetime.now(timezone.utc) > expires_at:
                            logger.warning(
                                f"Expired API key used: {key_record['key_prefix']}"
                            )
                            return None

                    # Update usage
                    await self._update_key_usage(key_record["id"])

                    # Return API key info
                    return APIKeyInfo(
                        id=key_record["id"],
                        workspace_id=key_record["workspace_id"],
                        name=key_record["name"],
                        permissions=key_record["permissions"],
                        key_hash=key_record["key_hash"],
                        key_prefix=key_record["key_prefix"],
                        created_at=datetime.fromisoformat(key_record["created_at"]),
                        last_used_at=(
                            datetime.fromisoformat(key_record["last_used_at"])
                            if key_record.get("last_used_at")
                            else None
                        ),
                        expires_at=(
                            datetime.fromisoformat(key_record["expires_at"])
                            if key_record.get("expires_at")
                            else None
                        ),
                        is_active=key_record["is_active"],
                        usage_count=key_record["usage_count"],
                    )

            # No matching key found
            logger.warning("Invalid API key provided")
            return None

        except Exception as e:
            logger.error(f"Error validating API key: {e}")
            return None

    async def _update_key_usage(self, key_id: str) -> None:
        """
        Update key usage statistics

        Args:
            key_id: API key ID
        """
        try:
            update_data = {
                "last_used_at": datetime.now(timezone.utc).isoformat(),
                "usage_count": self.supabase.rpc("increment", {"x": 1}).execute(),
            }

            # For simplicity, just update last_used_at
            self.supabase.table("api_keys").update(
                {"last_used_at": datetime.now(timezone.utc).isoformat()}
            ).eq("id", key_id).execute()

        except Exception as e:
            logger.error(f"Error updating key usage: {e}")

    async def list_api_keys(self, workspace_id: str) -> List[Dict[str, Any]]:
        """
        List all API keys for a workspace

        Args:
            workspace_id: Workspace ID

        Returns:
            List of API key information (without actual keys)
        """
        try:
            result = (
                self.supabase.table("api_keys")
                .select("*")
                .eq("workspace_id", workspace_id)
                .execute()
            )

            keys = []
            for key_record in result.data or []:
                # Exclude the actual key hash
                key_info = {
                    "id": key_record["id"],
                    "workspace_id": key_record["workspace_id"],
                    "name": key_record["name"],
                    "permissions": key_record["permissions"],
                    "key_prefix": key_record["key_prefix"],
                    "created_at": key_record["created_at"],
                    "last_used_at": key_record["last_used_at"],
                    "expires_at": key_record["expires_at"],
                    "is_active": key_record["is_active"],
                    "usage_count": key_record["usage_count"],
                }
                keys.append(key_info)

            return keys

        except Exception as e:
            logger.error(f"Error listing API keys: {e}")
            return []

    async def revoke_api_key(self, key_id: str, workspace_id: str) -> bool:
        """
        Revoke an API key

        Args:
            key_id: API key ID
            workspace_id: Workspace ID

        Returns:
            True if revoked successfully, False otherwise
        """
        try:
            result = (
                self.supabase.table("api_keys")
                .update({"is_active": False})
                .eq("id", key_id)
                .eq("workspace_id", workspace_id)
                .execute()
            )

            if result.data:
                logger.info(f"API key revoked: {key_id}")
                return True
            else:
                logger.warning(f"API key not found for revocation: {key_id}")
                return False

        except Exception as e:
            logger.error(f"Error revoking API key: {e}")
            return False

    async def delete_api_key(self, key_id: str, workspace_id: str) -> bool:
        """
        Delete an API key permanently

        Args:
            key_id: API key ID
            workspace_id: Workspace ID

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            result = (
                self.supabase.table("api_keys")
                .delete()
                .eq("id", key_id)
                .eq("workspace_id", workspace_id)
                .execute()
            )

            if result.data:
                logger.info(f"API key deleted: {key_id}")
                return True
            else:
                logger.warning(f"API key not found for deletion: {key_id}")
                return False

        except Exception as e:
            logger.error(f"Error deleting API key: {e}")
            return False

    async def update_api_key(
        self,
        key_id: str,
        workspace_id: str,
        name: Optional[str] = None,
        permissions: Optional[List[str]] = None,
        expires_in_days: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Update API key properties

        Args:
            key_id: API key ID
            workspace_id: Workspace ID
            name: New name (optional)
            permissions: New permissions (optional)
            expires_in_days: New expiration in days (optional)

        Returns:
            Updated API key info or None
        """
        try:
            update_data = {}

            if name is not None:
                update_data["name"] = name

            if permissions is not None:
                update_data["permissions"] = permissions

            if expires_in_days is not None:
                expires_at = datetime.now(timezone.utc) + timedelta(
                    days=expires_in_days
                )
                update_data["expires_at"] = expires_at.isoformat()

            if not update_data:
                logger.warning("No update data provided for API key")
                return None

            result = (
                self.supabase.table("api_keys")
                .update(update_data)
                .eq("id", key_id)
                .eq("workspace_id", workspace_id)
                .execute()
            )

            if result.data:
                updated_key = result.data[0]
                logger.info(f"API key updated: {key_id}")

                # Return updated key info
                return {
                    "id": updated_key["id"],
                    "workspace_id": updated_key["workspace_id"],
                    "name": updated_key["name"],
                    "permissions": updated_key["permissions"],
                    "key_prefix": updated_key["key_prefix"],
                    "created_at": updated_key["created_at"],
                    "last_used_at": updated_key["last_used_at"],
                    "expires_at": updated_key["expires_at"],
                    "is_active": updated_key["is_active"],
                    "usage_count": updated_key["usage_count"],
                }
            else:
                logger.warning(f"API key not found for update: {key_id}")
                return None

        except Exception as e:
            logger.error(f"Error updating API key: {e}")
            return None

    async def cleanup_expired_keys(self) -> int:
        """
        Clean up expired API keys

        Returns:
            Number of keys cleaned up
        """
        try:
            current_time = datetime.now(timezone.utc).isoformat()

            result = (
                self.supabase.table("api_keys")
                .update({"is_active": False})
                .lt("expires_at", current_time)
                .execute()
            )

            cleaned_count = len(result.data) if result.data else 0
            logger.info(f"Cleaned up {cleaned_count} expired API keys")

            return cleaned_count

        except Exception as e:
            logger.error(f"Error cleaning up expired keys: {e}")
            return 0


# Global API key manager instance
_api_key_manager: Optional[APIKeyManager] = None


def get_api_key_manager() -> APIKeyManager:
    """Get global API key manager singleton"""
    global _api_key_manager
    if _api_key_manager is None:
        _api_key_manager = APIKeyManager()
    return _api_key_manager


# Convenience functions
async def create_api_key(
    workspace_id: str,
    name: str,
    permissions: List[str],
    expires_in_days: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    """Create a new API key"""
    return await get_api_key_manager().create_api_key(
        workspace_id, name, permissions, expires_in_days
    )


async def validate_api_key(api_key: str) -> Optional[APIKeyInfo]:
    """Validate an API key"""
    return await get_api_key_manager().validate_api_key(api_key)
