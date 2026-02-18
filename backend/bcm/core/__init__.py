"""
BCM Client - Main interface for BCM operations.

Provides CRUD operations, caching, and AI synthesis for Business Context Manifests.
"""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any, Dict, List, Optional

from backend.bcm.core.types import BCMManifest, BCMIdentity, BCMPromptKit, BCMGuardrails
from backend.bcm.core.reducer import reduce_business_context

logger = logging.getLogger(__name__)

TABLE = "business_context_manifests"


class BCMClient:
    """
    Client for managing Business Context Manifests.

    Handles:
    - CRUD operations with Supabase
    - Redis caching for fast reads
    - AI synthesis for identity enrichment
    - Version tracking

    Example:
        client = BCMClient()

        # Seed from business context
        manifest = await client.seed(workspace_id="ws_123", business_context=data)

        # Get latest manifest
        manifest = await client.get_manifest(workspace_id="ws_123")

        # Trigger reflection cycle
        result = await client.reflect(workspace_id="ws_123")
    """

    def __init__(
        self,
        cache_client: Optional[Any] = None,
        db_client: Optional[Any] = None,
    ):
        self._cache = cache_client
        self._db = db_client
        self._initialized = False

    def _get_db(self):
        """Get database client (lazy initialization)."""
        if self._db is None:
            from backend.infrastructure.database.supabase import get_supabase_client

            self._db = get_supabase_client()
        return self._db

    def _get_cache(self):
        """Get cache client (lazy initialization)."""
        if self._cache is None:
            from backend.services import bcm_cache

            self._cache = bcm_cache
        return self._cache

    async def initialize(self) -> None:
        """Initialize the BCM client."""
        self._initialized = True
        logger.info("BCM client initialized")

    def _next_version(self, workspace_id: str) -> int:
        """Get the next version number for a workspace."""
        db = self._get_db()
        result = (
            db.table(TABLE)
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
        """
        Store a BCM manifest with write-through cache.

        Args:
            workspace_id: Workspace identifier
            manifest: BCM manifest dictionary
            source_context: Original business context (for rebuilds)

        Returns:
            Stored row data
        """
        db = self._get_db()
        cache = self._get_cache()
        version = manifest.get("version", self._next_version(workspace_id))

        row = {
            "workspace_id": workspace_id,
            "version": version,
            "manifest": manifest,
            "source_context": source_context,
            "checksum": manifest.get("checksum", ""),
            "token_estimate": manifest.get("meta", {}).get("token_estimate", 0),
        }

        result = db.table(TABLE).insert(row).execute()
        if result.data:
            logger.info("Stored BCM v%d for workspace %s", version, workspace_id)
            cache.set_manifest(workspace_id, manifest)
            return result.data[0]
        raise RuntimeError(f"Failed to store BCM manifest: {result}")

    def get_latest(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Get the latest BCM manifest row for a workspace."""
        db = self._get_db()
        cache = self._get_cache()

        result = (
            db.table(TABLE)
            .select("*")
            .eq("workspace_id", workspace_id)
            .order("version", desc=True)
            .limit(1)
            .execute()
        )
        if result.data:
            row = result.data[0]
            if row.get("manifest"):
                cache.set_manifest(workspace_id, row["manifest"])
            return row
        return None

    def get_manifest(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Get just the BCM manifest dict (cache-first, no source_context)."""
        cache = self._get_cache()
        cached = cache.get_manifest(workspace_id)
        if cached:
            return cached

        row = self.get_latest(workspace_id)
        return row["manifest"] if row else None

    def get_by_version(
        self, workspace_id: str, version: int
    ) -> Optional[Dict[str, Any]]:
        """Get a specific BCM version."""
        db = self._get_db()
        result = (
            db.table(TABLE)
            .select("*")
            .eq("workspace_id", workspace_id)
            .eq("version", version)
            .limit(1)
            .execute()
        )
        return result.data[0] if result.data else None

    def list_versions(self, workspace_id: str) -> List[Dict[str, Any]]:
        """List all BCM versions for a workspace (summary only)."""
        db = self._get_db()
        result = (
            db.table(TABLE)
            .select("id, workspace_id, version, checksum, token_estimate, created_at")
            .eq("workspace_id", workspace_id)
            .order("version", desc=True)
            .execute()
        )
        return result.data or []

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

        cache = self._get_cache()
        cache.invalidate(workspace_id)
        return self.store_manifest(workspace_id, manifest, source)

    async def rebuild_async(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Rebuild BCM with AI synthesis from the latest stored source_context."""
        latest = self.get_latest(workspace_id)
        if not latest or not latest.get("source_context"):
            logger.warning("No source_context found for workspace %s", workspace_id)
            return None

        source = latest["source_context"]
        new_version = latest["version"] + 1

        manifest = await self._synthesize(
            business_context=source,
            workspace_id=workspace_id,
            version=new_version,
            source="rebuild",
        )

        cache = self._get_cache()
        cache.invalidate(workspace_id)
        return self.store_manifest(workspace_id, manifest, source)

    def seed(
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

    async def seed_async(
        self,
        workspace_id: str,
        business_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Seed a BCM with AI synthesis from a raw business_context.json."""
        version = self._next_version(workspace_id)

        manifest = await self._synthesize(
            business_context=business_context,
            workspace_id=workspace_id,
            version=version,
            source="seed",
        )

        return self.store_manifest(workspace_id, manifest, business_context)

    async def _synthesize(
        self,
        business_context: Dict[str, Any],
        workspace_id: str,
        version: int,
        source: str,
    ) -> Dict[str, Any]:
        """Run static reduction + AI synthesis."""
        manifest = reduce_business_context(
            business_context=business_context,
            workspace_id=workspace_id,
            version=version,
            source=source,
        )

        try:
            from backend.ai import get_client

            client = get_client()
            await client.initialize()

            synthesis = await self._synthesize_identity(business_context, client)

            if synthesis:
                manifest["identity"] = synthesis.get("identity", {})
                manifest["prompt_kit"] = synthesis.get("prompt_kit", {})
                manifest["guardrails_v2"] = synthesis.get("guardrails_v2", {})
                manifest["meta"]["synthesized"] = True

                manifest["checksum"] = ""
                manifest_json = json.dumps(
                    manifest, sort_keys=True, separators=(",", ":")
                )
                manifest["checksum"] = hashlib.sha256(
                    manifest_json.encode()
                ).hexdigest()[:16]
                manifest["meta"]["token_estimate"] = len(manifest_json) // 4
            else:
                manifest["meta"]["synthesized"] = False
        except Exception as exc:
            logger.warning("AI synthesis failed, using static manifest: %s", exc)
            manifest["meta"]["synthesized"] = False

        return manifest

    async def _synthesize_identity(
        self,
        business_context: Dict[str, Any],
        ai_client: Any,
    ) -> Optional[Dict[str, Any]]:
        """Use AI to synthesize brand identity from business context."""
        from backend.bcm.prompts import SYNTHESIS_PROMPT

        prompt = SYNTHESIS_PROMPT + json.dumps(business_context, indent=2)

        result = await ai_client.generate(
            prompt=prompt,
            workspace_id="system",
            user_id="bcm_synthesizer",
            max_tokens=4000,
            temperature=0.4,
        )

        if not result.success:
            logger.error("Synthesis generation failed: %s", result.error)
            return None

        return self._parse_synthesis_response(result.text)

    def _parse_synthesis_response(self, raw_text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from model response."""
        text = raw_text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            start = 1
            end = len(lines) - 1
            if lines[0].startswith("```json"):
                start = 1
            for i in range(len(lines) - 1, 0, -1):
                if lines[i].strip() == "```":
                    end = i
                    break
            text = "\n".join(lines[start:end])

        try:
            parsed = json.loads(text)
            expected_keys = {"identity", "prompt_kit", "guardrails_v2"}
            if not expected_keys.issubset(parsed.keys()):
                missing = expected_keys - parsed.keys()
                logger.error("Synthesis response missing keys: %s", missing)
                return None
            return parsed
        except json.JSONDecodeError:
            brace_start = text.find("{")
            brace_end = text.rfind("}")
            if brace_start != -1 and brace_end != -1:
                try:
                    return json.loads(text[brace_start : brace_end + 1])
                except json.JSONDecodeError:
                    pass
            return None

    def clear_all(self, workspace_id: str) -> int:
        """Delete all BCM manifests for a workspace."""
        db = self._get_db()
        cache = self._get_cache()
        result = db.table(TABLE).delete().eq("workspace_id", workspace_id).execute()
        deleted_count = len(result.data) if result.data else 0
        logger.info(
            "Cleared %d BCM manifests for workspace %s", deleted_count, workspace_id
        )
        cache.invalidate(workspace_id)
        return deleted_count


_bcm_client: Optional[BCMClient] = None


def get_bcm_client() -> BCMClient:
    """Get the global BCM client instance."""
    global _bcm_client
    if _bcm_client is None:
        _bcm_client = BCMClient()
    return _bcm_client


__all__ = [
    "BCMClient",
    "BCMManifest",
    "BCMIdentity",
    "BCMPromptKit",
    "BCMGuardrails",
    "get_bcm_client",
]
