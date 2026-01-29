"""
BCM Database Storage Service

Provides Supabase database operations for Business Context Manifests
with versioning, conflict resolution, and data integrity checks.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID

try:
    from supabase import create_client, Client
    from postgrest import APIResponse

    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logging.warning("Supabase not available - database storage will be disabled")

from ..integration.bcm_reducer import BusinessContextManifest
from ..services.versioning import SemanticVersioning, Version, VersionType


class BCMDatabaseStorage:
    """
    Database storage service for Business Context Manifests using Supabase.

    Provides persistent storage with versioning, conflict resolution, and
    comprehensive error handling.
    """

    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """
        Initialize BCM database storage client.

        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase service key
        """
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.client: Optional[Client] = None
        self.versioning = SemanticVersioning()

        # Initialize Supabase client
        self._initialize_supabase()

    def _initialize_supabase(self) -> bool:
        """
        Initialize Supabase client.

        Returns:
            True if initialization successful, False otherwise
        """
        if not SUPABASE_AVAILABLE:
            logging.error("Supabase not available - cannot initialize database storage")
            return False

        try:
            self.client = create_client(self.supababase_url, self.supababse_key)

            # Test connection
            self.client.table("business_context_manifests").select("count").execute()

            logging.info("BCM database storage initialized successfully")
            return True

        except Exception as e:
            logging.error(f"Failed to initialize Supabase client: {e}")
            self.client = None
            return False

    def store_bcm_supabase(
        self,
        workspace_id: str,
        bcm: BusinessContextManifest,
        user_id: str = None,
        force_version: bool = False,
    ) -> Dict[str, Any]:
        """
        Store BCM in Supabase database with versioning.

        Args:
            workspace_id: Workspace identifier
            bcm: Business Context Manifest to store
            user_id: User identifier
            force_version: Force version increment even if no changes

        Returns:
            Storage result with version information
        """
        if not self.client:
            return {"success": False, "error": "Database not available"}

        try:
            # Get current version if BCM exists
            current_version = self.versioning.get_current_version(bcm)

            # Check if BCM already exists
            existing_bcm = self.get_bcm_supabase(workspace_id)
            version_type = VersionType.PATCH
            reason = "Initial creation"

            if existing_bcm and not force_version:
                # Determine version change type
                version_type, reason = self.versioning.determine_version_change(
                    existing_bcm, bcm
                )

            # Increment version
            new_version = self.versioning.increment_version(
                current_version, version_type
            )

            # Prepare BCM data for storage
            bcm_dict = bcm.dict()

            # Add version and metadata
            bcm_dict.update(
                {
                    "version_major": new_version.major,
                    "version_minor": new_version.minor,
                    "version_patch": new_version.patch,
                    "version_string": str(new_version),
                    "token_count": self._count_tokens(bcm_dict),
                    "checksum": self._compute_checksum(bcm_dict),
                    "compression_applied": False,  # Would be set by compression logic
                    "compression_ratio": 0.0,
                    "original_token_count": self._count_tokens(bcm_dict),
                }
            )

            # Store in database
            result = (
                self.client.table("business_context_manifests")
                .upsert(bcm_dict, {"workspace_id": workspace_id, "user_id": user_id})
                .execute()
            )

            if result.data:
                stored_bcm = result.data[0]
                return {
                    "success": True,
                    "version": str(new_version),
                    "version_type": version_type.value,
                    "reason": reason,
                    "stored_bcm": stored_bcm,
                    "id": stored_bcm.get("id"),
                }
            else:
                return {"success": False, "error": "Failed to store BCM"}

        except Exception as e:
            logging.error(f"Error storing BCM in database: {e}")
            return {"success": False, "error": str(e)}

    def get_bcm_supabase(
        self, workspace_id: str, version: str = None
    ) -> Optional[BusinessContextManifest]:
        """
        Retrieve BCM from Supabase database.

        Args:
            workspace_id: Workspace identifier
            version: Specific version to retrieve (optional)

        Returns:
            BCM if found, None otherwise
        """
        if not self.client:
            logging.warning("Database not available - cannot retrieve BCM")
            return None

        try:
            query = self.client.table("business_context_manifests").select("*")

            if version:
                # Get specific version
                query = query.eq("version_string", version)

            query = (
                query.eq("workspace_id", workspace_id)
                .order("created_at", desc=True)
                .limit(1)
            )

            result = query.execute()

            if result.data:
                bcm_data = result.data[0]
                return self._dict_to_bcm(bcm_data)
            else:
                return None

        except Exception as e:
            logging.error(f"Error retrieving BCM from database: {e}")
            return None

    def get_bcm_history(
        self, workspace_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get version history for a workspace's BCM.

        Args:
            workspace_id: Workspace identifier
            limit: Maximum number of versions to return

        Returns:
            List of version history records
        """
        if not self.client:
            logging.warning("Database not available - cannot get version history")
            return []

        try:
            result = (
                self.client.table("bcm_version_history")
                .select("*")
                .eq("workspace_id", workspace_id)
                .order("changed_at", desc)
                .limit(limit)
                .execute()
            )

            return result.data if result.data else []

        except Exception as e:
            logging.error(f"Error getting BCM version history: {e}")
            return []

    def get_latest_version(self, workspace_id: str) -> Optional[str]:
        """
        Get the latest version string for a workspace's BCM.

        Args:
            workspace_id: Workspace identifier

        Returns:
            Latest version string or None
        """
        try:
            result = (
                self.client.table("business_context_manifests")
                .select("version_string")
                .eq("workspace_id", workspace_id)
                .order("created_at", desc)
                .limit(1)
                .execute()
            )

            if result.data:
                return result.data[0]["version_string"]
            else:
                return None

        except Exception as e:
            logging.error(f"Error getting latest version: {e}")
            return None

    def delete_bcm(self, workspace_id: str, version: str = None) -> bool:
        """
        Delete BCM from database.

        Args:
            workspace_id: Workspace identifier
            version: Specific version to delete (optional)

        Returns:
            True if deletion successful, False otherwise
        """
        if not self.client:
            logging.warning("Database not available - cannot delete BCM")
            return False

        try:
            query = self.client.table("business_context_manifests").delete()

            if version:
                query = query.eq("version_string", version)

            query = query.eq("workspace_id", workspace_id)

            result = query.execute()

            return result.data is not None

        except Exception as e:
            logging.error(f"Error deleting BCM from database: {e}")
            return False

    def list_workspaces_with_bcm(self) -> List[str]:
        """
        List all workspaces that have BCMs stored.

        Returns:
            List of workspace IDs
        """
        if not self.client:
            logging.warning("Database not available - cannot list workspaces")
            return []

        try:
            result = (
                self.client.table("business_context_manifests")
                .select("workspace_id")
                .execute()
            )

            return [item["workspace_id"] for item in result.data] if result.data else []

        except Exception as e:
            logging.error(f"Error listing workspaces with BCM: {e}")
            return []

    def get_workspace_bcm_count(self, workspace_id: str) -> int:
        """
        Get the number of BCM versions for a workspace.

        Args:
            workspace_id: Workspace identifier

        Returns:
            Number of BCM versions
        """
        if not self.client:
            return 0

        try:
            result = (
                self.client.table("business_context_manifests")
                .select("count", count="*")
                .eq("workspace_id", workspace_id)
                .execute()
            )

            return result.count if result.data else 0

        except Exception as e:
            logging.error(f"Error getting BCM count: {e}")
            return 0

    def cleanup_old_versions(self, workspace_id: str, keep_latest: int = 5) -> int:
        """
        Clean up old BCM versions, keeping only the latest N versions.

        Args:
            workspace_id: Workspace identifier
            keep_latest: Number of latest versions to keep

        Returns:
            Number of versions deleted
        """
        if not self.client:
            logging.warning("Database not available - cannot cleanup versions")
            return 0

        try:
            # Get all versions for workspace
            result = (
                self.client.table("business_context_manifests")
                .select("id", "version_string", "created_at")
                .eq("workspace_id", workspace_id)
                .order("created_at", desc)
                .execute()
            )

            if not result.data or len(result.data) <= keep_latest:
                return 0

            # Delete old versions (keep only the latest N)
            versions_to_delete = result.data[keep_latest:]
            deleted_count = 0

            for version in versions_to_delete:
                delete_result = (
                    self.client.table("business_context_manifestes")
                    .delete()
                    .eq("id", version["id"])
                    .execute()
                )

                if delete_result.data is not None:
                    deleted_count += 1

            logging.info(
                f"Cleaned up {deleted_count} old BCM versions for workspace {workspace_id}"
            )
            return deleted_count

        except Exception as e:
            logging.error(f"Error cleaning up old BCM versions: {e}")
            return 0

    def verify_data_integrity(self, workspace_id: str) -> Dict[str, Any]:
        """
        Verify data integrity for all BCM versions in a workspace.

        Args:
            workspace_id: Workspace identifier

        Returns:
            Integrity verification results
        """
        if not self.client:
            return {"success": False, "error": "Database not available"}

        try:
            # Get all BCMs for workspace
            result = (
                self.client.table("business_context_manifests")
                .select("*")
                .eq("workspace_id", workspace_id)
                .order("created_at", desc)
                .execute()
            )

            if not result.data:
                return {"success": True, "verified_count": 0, "issues": []}

            verified_count = 0
            issues = []

            for bcm_record in result.data:
                # Verify checksum
                stored_checksum = bcm_record.get("checksum")
                bcm_data = {k: v for k, v in bcm_record.items() if k != "checksum"}

                computed_checksum = self._compute_checksum(bcm_data)

                if stored_checksum == computed_checksum:
                    verified_count += 1
                else:
                    issues.append(
                        {
                            "version": bcm_record.get("version_string"),
                            "id": bcm_record.get("id"),
                            "issue": "Checksum mismatch",
                            "stored": stored_checksum[:16] + "...",
                            "computed": computed_checksum[:16] + "...",
                        }
                    )

            return {
                "success": len(issues) == 0,
                "verified_count": verified_count,
                "total_count": len(result.data),
                "issues": issues,
            }

        except Exception as e:
            logging.error(f"Error verifying data integrity: {e}")
            return {"success": False, "error": str(e)}

    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get database storage statistics.

        Returns:
            Storage statistics
        """
        if not self.client:
            return {"available": False, "error": "Database not available"}

        try:
            # Get total BCM count
            total_result = (
                self.client.table("business_context_manifests")
                .select("count", count="*")
                .execute()
            )

            # Get workspace count
            workspace_result = (
                self.client.table("business_context_manifests")
                .select("workspace_id", count="*")
                .execute()
            )

            # Get version history count
            history_result = (
                self.client.table("bcm_version_history")
                .select("count", count="*")
                .execute()
            )

            # Get access logs count
            logs_result = (
                self.client.table("bcm_access_logs")
                .select("count", count="*")
                .execute()
            )

            return {
                "available": True,
                "total_bcms": total_result.count if total_result.data else 0,
                "workspaces_with_bcms": (
                    workspace_result.count if workspace_result.data else 0
                ),
                "version_history_entries": (
                    history_result.count if history_result.data else 0
                ),
                "access_log_entries": logs_result.count if logs_result.data else 0,
            }

        except Exception as e:
            logging.error(f"Error getting storage stats: {e}")
            return {"available": False, "error": str(e)}

    def _dict_to_bcm(self, bcm_dict: Dict[str, Any]) -> BusinessContextManifest:
        """
        Convert dictionary back to BusinessContextManifest.

        Args:
            bcm_dict: BCM dictionary

        Returns:
            BusinessContextManifest object
        """
        try:
            # Extract version information
            version_info = {"version": bcm_dict.get("version_string", "2.0.0")}

            # Remove database-specific fields
            clean_dict = {
                k: v
                for k, v in bcm_dict.items()
                if k
                not in [
                    "id",
                    "created_at",
                    "updated_at",
                    "version_major",
                    "version_minor",
                    "version_patch",
                    "version_string",
                    "token_count",
                    "checksum",
                    "compression_applied",
                    "compression_ratio",
                    "original_token_count",
                    "validation_warnings",
                    "missing_fields",
                    "evidence_count",
                ]
            }

            # Convert back to BCM
            return BusinessContextManifest(**clean_dict)

        except Exception as e:
            logging.error(f"Error converting dict to BCM: {e}")
            # Return a minimal BCM as fallback
            return BusinessContextManifest(
                version="2.0.0",
                generated_at=bcm_dict.get(
                    "generated_at", datetime.utcnow().isoformat()
                ),
                workspace_id=bcm_dict.get("workspace_id", "unknown"),
                user_id=bcm_dict.get("user_id"),
            )

    def _count_tokens(self, bcm_dict: Dict[str, Any]) -> int:
        """
        Count tokens in BCM dictionary.

        Args:
            bcm_dict: BCM dictionary

        Returns:
            Estimated token count
        """
        try:
            # Simple estimation: ~4 characters per token
            json_str = json.dumps(bcm_dict, separators=(",", ":"))
            return len(json_str) // 4
        except Exception:
            return 0

    def _compute_checksum(self, bcm_dict: Dict[str, Any]) -> str:
        """
        Compute SHA-256 checksum of BCM dictionary.

        Args:
            bcm_dict: BCM dictionary

        Returns:
            SHA-256 checksum as hex string
        """
        try:
            import hashlib

            # Create normalized JSON for consistent hashing
            json_str = json.dumps(bcm_dict, sort_keys=True, separators=(",", ":"))
            return hashlib.sha256(json_str.encode("utf-8")).hexdigest()
        except Exception as e:
            logging.error(f"Error computing checksum: {e}")
            return ""

    def close(self) -> None:
        """Close database connection."""
        try:
            if self.client:
                self.client = None
                logging.info("BCM database storage connection closed")
        except Exception as e:
            logging.error(f"Error closing database connection: {e}")

    def __del__(self):
        """Cleanup on deletion."""
        self.close()
