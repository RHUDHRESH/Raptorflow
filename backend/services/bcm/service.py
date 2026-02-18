"""
BCM Service: Supabase CRUD for Business Context Manifests.

Provides both sync (static reducer) and async (AI synthesizer) paths.
Integrates Upstash Redis cache for fast reads.
"""

from __future__ import annotations

import logging
import asyncio
from typing import Any, Dict, List, Optional

from backend.infrastructure.database.supabase import get_supabase_client
from backend.services.base_service import BaseService
from backend.services.registry import registry
from backend.services.bcm.reducer import reduce_business_context
from backend.services import bcm_cache
from backend.services.exceptions import ServiceError, ResourceNotFoundError

logger = logging.getLogger(__name__)

TABLE = "business_context_manifests"


class BCMService(BaseService):
    def __init__(self):
        super().__init__("bcm_service")

    async def check_health(self) -> Dict[str, Any]:
        """Check connection to Supabase table."""
        try:
            client = get_supabase_client()
            client.table(TABLE).select("count", count="exact").limit(0).execute()
            return {"status": "healthy"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def _next_version(self, workspace_id: str) -> int:
        """Get the next version number for a workspace."""
        client = get_supabase_client()
        result = (
            client.table(TABLE)
            .select("version")
            .eq("workspace_id", workspace_id)
            .order("version", desc=True)
            .limit(1)
            .execute()
        )
        if result.data:
            return result.data[0]["version"] + 1
        return 1

    def store_manifest(
        self,
        workspace_id: str,
        manifest: Dict[str, Any],
        source_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Store a BCM manifest in Supabase with write-through cache."""

        def _execute():
            client = get_supabase_client()
            version = manifest.get("version", self._next_version(workspace_id))

            row = {
                "workspace_id": workspace_id,
                "version": version,
                "manifest": manifest,
                "source_context": source_context,
                "checksum": manifest.get("checksum", ""),
                "token_estimate": manifest.get("meta", {}).get("token_estimate", 0),
            }

            result = client.table(TABLE).insert(row).execute()
            if result.data:
                logger.info("Stored BCM v%d for workspace %s", version, workspace_id)
                # Write-through: update cache with new manifest
                bcm_cache.set_manifest(workspace_id, manifest)
                return result.data[0]
            raise ServiceError(f"Failed to store BCM manifest: {result}")

        # Currently synchronous wrapper for now, can be made async later if needed
        # But BaseService execute_with_retry handles both sync and async
        # However, for now we keep it simple as the original was sync
        return _execute()

    def get_latest(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Get the latest BCM manifest row for a workspace."""

        def _execute():
            client = get_supabase_client()
            result = (
                client.table(TABLE)
                .select("*")
                .eq("workspace_id", workspace_id)
                .order("version", desc=True)
                .limit(1)
                .execute()
            )
            if result.data:
                row = result.data[0]
                if row.get("manifest"):
                    bcm_cache.set_manifest(workspace_id, row["manifest"])
                return row
            return None

        return _execute()

    def get_manifest_fast(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Get just the BCM manifest dict (cache-first, no source_context)."""
        cached = bcm_cache.get_manifest(workspace_id)
        if cached:
            return cached

        row = self.get_latest(workspace_id)
        return row["manifest"] if row else None

    def get_by_version(
        self, workspace_id: str, version: int
    ) -> Optional[Dict[str, Any]]:
        """Get a specific BCM version."""

        def _execute():
            client = get_supabase_client()
            result = (
                client.table(TABLE)
                .select("*")
                .eq("workspace_id", workspace_id)
                .eq("version", version)
                .limit(1)
                .execute()
            )
            return result.data[0] if result.data else None

        return _execute()

    def list_versions(self, workspace_id: str) -> List[Dict[str, Any]]:
        """List all BCM versions for a workspace (summary only)."""

        def _execute():
            client = get_supabase_client()
            result = (
                client.table(TABLE)
                .select(
                    "id, workspace_id, version, checksum, token_estimate, created_at"
                )
                .eq("workspace_id", workspace_id)
                .order("version", desc=True)
                .execute()
            )
            return result.data or []

        return _execute()

    def rebuild(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Rebuild BCM from the latest stored source_context (sync/static)."""
        latest = self.get_latest(workspace_id)
        if not latest or not latest.get("source_context"):
            logger.warning("No source_context found for workspace %s", workspace_id)
            return None

        source = latest["source_context"]
        new_version = latest["version"] + 1

        manifest = reduce_business_context(
            business_context=source,
            workspace_id=workspace_id,
            version=new_version,
            source="rebuild",
        )

        bcm_cache.invalidate(workspace_id)
        return self.store_manifest(workspace_id, manifest, source)

    async def rebuild_async(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Rebuild BCM with AI synthesis from the latest stored source_context."""
        from backend.services.bcm.synthesizer import synthesize_business_context

        # Use execute_with_retry for the async operation
        async def _execute():
            latest = self.get_latest(workspace_id)
            if not latest or not latest.get("source_context"):
                logger.warning("No source_context found for workspace %s", workspace_id)
                return None

            source = latest["source_context"]
            new_version = latest["version"] + 1

            manifest = await synthesize_business_context(
                business_context=source,
                workspace_id=workspace_id,
                version=new_version,
                source="rebuild",
            )

            bcm_cache.invalidate(workspace_id)
            return self.store_manifest(workspace_id, manifest, source)

        return await self.execute_with_retry(_execute)

    def seed_from_business_context(
        self,
        workspace_id: str,
        business_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Seed a BCM from a raw business_context.json (sync/static)."""
        version = self._next_version(workspace_id)

        manifest = reduce_business_context(
            business_context=business_context,
            workspace_id=workspace_id,
            version=version,
            source="seed",
        )

        return self.store_manifest(workspace_id, manifest, business_context)

    async def seed_from_business_context_async(
        self,
        workspace_id: str,
        business_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Seed a BCM with AI synthesis from a raw business_context.json."""
        from backend.services.bcm.synthesizer import synthesize_business_context

        async def _execute():
            version = self._next_version(workspace_id)

            manifest = await synthesize_business_context(
                business_context=business_context,
                workspace_id=workspace_id,
                version=version,
                source="seed",
            )

            return self.store_manifest(workspace_id, manifest, business_context)

        return await self.execute_with_retry(_execute)

    def clear_all(self, workspace_id: str) -> int:
        """Delete all BCM manifests for a workspace."""

        def _execute():
            client = get_supabase_client()
            result = (
                client.table(TABLE).delete().eq("workspace_id", workspace_id).execute()
            )
            deleted_count = len(result.data) if result.data else 0
            logger.info(
                "Cleared %d BCM manifests for workspace %s", deleted_count, workspace_id
            )
            bcm_cache.invalidate(workspace_id)
            return deleted_count

        return _execute()


# Singleton instance
bcm_service = BCMService()
registry.register(bcm_service)


# Backward compatibility functions
def _next_version(workspace_id: str) -> int:
    return bcm_service._next_version(workspace_id)


def store_manifest(
    workspace_id: str,
    manifest: Dict[str, Any],
    source_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return bcm_service.store_manifest(workspace_id, manifest, source_context)


def get_latest(workspace_id: str) -> Optional[Dict[str, Any]]:
    return bcm_service.get_latest(workspace_id)


def get_manifest_fast(workspace_id: str) -> Optional[Dict[str, Any]]:
    return bcm_service.get_manifest_fast(workspace_id)


def get_by_version(workspace_id: str, version: int) -> Optional[Dict[str, Any]]:
    return bcm_service.get_by_version(workspace_id, version)


def list_versions(workspace_id: str) -> List[Dict[str, Any]]:
    return bcm_service.list_versions(workspace_id)


def rebuild(workspace_id: str) -> Optional[Dict[str, Any]]:
    return bcm_service.rebuild(workspace_id)


async def rebuild_async(workspace_id: str) -> Optional[Dict[str, Any]]:
    return await bcm_service.rebuild_async(workspace_id)


def seed_from_business_context(
    workspace_id: str, business_context: Dict[str, Any]
) -> Dict[str, Any]:
    return bcm_service.seed_from_business_context(workspace_id, business_context)


async def seed_from_business_context_async(
    workspace_id: str, business_context: Dict[str, Any]
) -> Dict[str, Any]:
    return await bcm_service.seed_from_business_context_async(
        workspace_id, business_context
    )


def clear_all(workspace_id: str) -> int:
    return bcm_service.clear_all(workspace_id)
