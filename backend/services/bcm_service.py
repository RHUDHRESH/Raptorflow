"""
BCM Service - Orchestrates BCM generation, storage, and retrieval
Integrates reducer, Redis tiers, and Supabase persistence
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..integration.bcm_reducer import BCMReducer
from ..redis.bcm_storage import BCMStorage
from ..schemas.bcm_schema import BusinessContextManifest
from ..services.supabase_client import get_supabase_admin

logger = logging.getLogger(__name__)


class BCMService:
    """
    Service for managing Business Context Manifest lifecycle
    Handles generation, storage, retrieval, and versioning
    """

    def __init__(self, db_client=None, redis_url: str = None):
        self.db = db_client or get_supabase_admin()
        self.reducer = BCMReducer()
        self.redis_storage = BCMStorage(redis_url=redis_url)

    async def generate_from_onboarding(
        self, session_id: str, workspace_id: str, user_id: str = None
    ) -> Dict[str, Any]:
        """
        Generate BCM from onboarding session data

        Args:
            session_id: Onboarding session ID
            workspace_id: Workspace identifier
            user_id: User ID (optional)

        Returns:
            Generated BCM with metadata
        """
        try:
            # Get onboarding session data from Redis
            from ..redis.session_manager import get_onboarding_session_manager

            session_manager = get_onboarding_session_manager()

            all_steps = await session_manager.get_all_steps(session_id)
            if not all_steps:
                raise ValueError(f"No step data found for session {session_id}")

            metadata = await session_manager.get_metadata(session_id)
            progress = await session_manager.get_progress(session_id)

            # Build business context
            business_context_data = {
                "version": "2.0",
                "generated_at": datetime.utcnow().isoformat(),
                "session_id": session_id,
                "metadata": metadata,
                "progress": progress,
                "steps": all_steps,
            }

            # Generate BCM using reducer
            bcm = await self.reducer.reduce(business_context_data)

            # Store in Redis tiers and database
            await self.store_manifest(workspace_id, bcm.dict(), user_id)

            logger.info(f"BCM generated and stored for workspace {workspace_id}")

            return {
                "success": True,
                "bcm": bcm.dict(),
                "workspace_id": workspace_id,
                "generated_at": bcm.generated_at,
                "checksum": getattr(bcm, "checksum", None),
                "token_count": self._count_tokens(bcm.dict()),
            }

        except Exception as e:
            logger.error(f"Error generating BCM for session {session_id}: {e}")
            raise

    async def store_manifest(
        self,
        workspace_id: str,
        manifest: Dict[str, Any],
        user_id: str = None,
        version: str = "1.0.0",
    ) -> bool:
        """
        Store BCM manifest in Redis tiers and Supabase

        Args:
            workspace_id: Workspace identifier
            manifest: BCM manifest data
            user_id: User ID (optional)
            version: Semantic version

        Returns:
            True if storage successful
        """
        try:
            # Store in Redis tiers
            bcm_obj = BusinessContextManifest(**manifest)
            redis_success = self.redis_storage.store_bcm(workspace_id, bcm_obj)

            # Store in Supabase
            db_success = await self._store_in_database(
                workspace_id, manifest, user_id, version
            )

            if redis_success and db_success:
                logger.info(f"BCM stored successfully for workspace {workspace_id}")
                return True
            else:
                logger.warning(
                    f"Partial BCM storage for workspace {workspace_id}: Redis={redis_success}, DB={db_success}"
                )
                return False

        except Exception as e:
            logger.error(f"Error storing BCM for workspace {workspace_id}: {e}")
            return False

    async def get_latest_manifest(
        self, workspace_id: str, use_fallback: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Get latest BCM manifest with Redis fallback to database

        Args:
            workspace_id: Workspace identifier
            use_fallback: Whether to fallback to database on Redis miss

        Returns:
            BCM manifest data or None
        """
        try:
            # Try Redis first
            bcm = self.redis_storage.get_bcm(workspace_id, use_fallback)
            if bcm:
                return bcm.dict()

            # Fallback to database if requested
            if use_fallback:
                return await self._get_from_database(workspace_id)

            return None

        except Exception as e:
            logger.error(f"Error retrieving BCM for workspace {workspace_id}: {e}")
            return None

    async def rebuild_manifest(
        self, workspace_id: str, force: bool = False
    ) -> Dict[str, Any]:
        """
        Rebuild BCM from latest onboarding data

        Args:
            workspace_id: Workspace identifier
            force: Force rebuild even if recent

        Returns:
            Rebuild result
        """
        try:
            # Check if rebuild is needed
            latest = await self.get_latest_manifest(workspace_id)
            if latest and not force:
                generated_at = datetime.fromisoformat(latest.get("generated_at"))
                if datetime.utcnow() - generated_at < timedelta(hours=1):
                    return {
                        "success": False,
                        "reason": "Recent BCM exists, use force=true to override",
                    }

            # Get workspace info to find user
            workspace = (
                self.db.table("workspaces")
                .select("owner_id")
                .eq("id", workspace_id)
                .single()
                .execute()
            )
            if not workspace.data:
                raise ValueError(f"Workspace {workspace_id} not found")

            user_id = workspace.data["owner_id"]

            # Find latest onboarding session
            # This would need to be implemented based on your session tracking
            # For now, we'll create a placeholder
            session_id = f"rebuild_{workspace_id}_{int(datetime.utcnow().timestamp())}"

            # Generate new BCM
            result = await self.generate_from_onboarding(
                session_id, workspace_id, user_id
            )

            # Invalidate old cache
            self.redis_storage.invalidate_bcm(workspace_id)

            return result

        except Exception as e:
            logger.error(f"Error rebuilding BCM for workspace {workspace_id}: {e}")
            raise

    async def get_version_history(
        self, workspace_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get version history for workspace

        Args:
            workspace_id: Workspace identifier
            limit: Maximum number of versions to return

        Returns:
            List of version history
        """
        try:
            result = (
                self.db.table("business_context_manifests")
                .select("*")
                .eq("workspace_id", workspace_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            return result.data or []

        except Exception as e:
            logger.error(
                f"Error getting version history for workspace {workspace_id}: {e}"
            )
            return []

    async def export_manifest(self, workspace_id: str, format: str = "json") -> bytes:
        """
        Export BCM in specified format

        Args:
            workspace_id: Workspace identifier
            format: Export format ('json' or 'markdown')

        Returns:
            Exported data as bytes
        """
        try:
            manifest = await self.get_latest_manifest(workspace_id)
            if not manifest:
                raise ValueError(f"No BCM found for workspace {workspace_id}")

            if format.lower() == "json":
                return json.dumps(manifest, indent=2).encode("utf-8")
            elif format.lower() == "markdown":
                return self._convert_to_markdown(manifest).encode("utf-8")
            else:
                raise ValueError(f"Unsupported export format: {format}")

        except Exception as e:
            logger.error(f"Error exporting BCM for workspace {workspace_id}: {e}")
            raise

    async def _store_in_database(
        self,
        workspace_id: str,
        manifest: Dict[str, Any],
        user_id: str = None,
        version: str = "1.0.0",
    ) -> bool:
        """Store manifest in Supabase database"""
        try:
            # Parse version
            version_parts = version.split(".")
            major, minor, patch = (
                int(version_parts[0]),
                int(version_parts[1]),
                int(version_parts[2]),
            )

            # Prepare database record
            record = {
                "workspace_id": workspace_id,
                "user_id": user_id,
                "version_major": major,
                "version_minor": minor,
                "version_patch": patch,
                "version_string": version,
                "company_info": manifest.get("company"),
                "icps": manifest.get("icps"),
                "competitors": manifest.get("competitors"),
                "brand_data": {
                    "brand": manifest.get("brand"),
                    "values": manifest.get("values"),
                    "personality": manifest.get("personality"),
                    "tone": manifest.get("tone"),
                    "positioning": manifest.get("positioning"),
                },
                "market_data": {
                    "market": manifest.get("market"),
                    "verticals": manifest.get("verticals"),
                    "geography": manifest.get("geography"),
                },
                "messaging_data": {
                    "messaging": manifest.get("messaging"),
                    "value_prop": manifest.get("value_prop"),
                    "taglines": manifest.get("taglines"),
                    "key_messages": manifest.get("key_messages"),
                    "soundbites": manifest.get("soundbites"),
                },
                "channels_data": {
                    "channels": manifest.get("channels"),
                    "primary_channels": manifest.get("primary_channels"),
                    "secondary_channels": manifest.get("secondary_channels"),
                    "strategy_summary": manifest.get("strategy_summary"),
                },
                "goals_data": {
                    "goals": manifest.get("goals"),
                    "short_term_goals": manifest.get("short_term_goals"),
                    "long_term_goals": manifest.get("long_term_goals"),
                    "kpis": manifest.get("kpis"),
                },
                "completion_percentage": manifest.get("completion_percentage", 0),
                "checksum": manifest.get("checksum"),
                "generated_at": manifest.get("generated_at"),
                "raw_step_ids": manifest.get("raw_step_ids", []),
            }

            result = (
                self.db.table("business_context_manifests").insert(record).execute()
            )
            return len(result.data) > 0

        except Exception as e:
            logger.error(f"Error storing BCM in database: {e}")
            return False

    async def _get_from_database(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Get latest manifest from database"""
        try:
            result = (
                self.db.table("business_context_manifests")
                .select("*")
                .eq("workspace_id", workspace_id)
                .order("created_at", desc=True)
                .limit(1)
                .single()
                .execute()
            )

            if result.data:
                # Reconstruct manifest from database fields
                record = result.data
                manifest = {
                    "version": f"{record['version_major']}.{record['version_minor']}.{record['version_patch']}",
                    "generated_at": record["generated_at"],
                    "workspace_id": workspace_id,
                    "user_id": record["user_id"],
                    "company": record["company_info"],
                    "icps": record["icps"],
                    "competitors": record["competitors"],
                    "brand": record["brand_data"]["brand"],
                    "values": record["brand_data"]["values"],
                    "personality": record["brand_data"]["personality"],
                    "tone": record["brand_data"]["tone"],
                    "positioning": record["brand_data"]["positioning"],
                    "market": record["market_data"]["market"],
                    "verticals": record["market_data"]["verticals"],
                    "geography": record["market_data"]["geography"],
                    "messaging": record["messaging_data"]["messaging"],
                    "value_prop": record["messaging_data"]["value_prop"],
                    "taglines": record["messaging_data"]["taglines"],
                    "key_messages": record["messaging_data"]["key_messages"],
                    "soundbites": record["messaging_data"]["soundbites"],
                    "channels": record["channels_data"]["channels"],
                    "primary_channels": record["channels_data"]["primary_channels"],
                    "secondary_channels": record["channels_data"]["secondary_channels"],
                    "strategy_summary": record["channels_data"]["strategy_summary"],
                    "goals": record["goals_data"]["goals"],
                    "short_term_goals": record["goals_data"]["short_term_goals"],
                    "long_term_goals": record["goals_data"]["long_term_goals"],
                    "kpis": record["goals_data"]["kpis"],
                    "completion_percentage": record["completion_percentage"],
                    "checksum": record["checksum"],
                    "raw_step_ids": record["raw_step_ids"],
                }
                return manifest

            return None

        except Exception as e:
            logger.error(f"Error getting BCM from database: {e}")
            return None

    def _convert_to_markdown(self, manifest: Dict[str, Any]) -> str:
        """Convert BCM manifest to markdown format"""
        md = []
        md.append(f"# Business Context Manifest")
        md.append(f"**Generated:** {manifest.get('generated_at', 'Unknown')}")
        md.append(f"**Workspace:** {manifest.get('workspace_id', 'Unknown')}")
        md.append(f"**Completion:** {manifest.get('completion_percentage', 0):.1f}%")
        md.append("")

        # Company Info
        if manifest.get("company"):
            md.append("## Company Information")
            company = manifest["company"]
            md.append(f"- **Name:** {company.get('name', 'N/A')}")
            md.append(f"- **Industry:** {company.get('industry', 'N/A')}")
            md.append(f"- **Stage:** {company.get('stage', 'N/A')}")
            md.append("")

        # ICPs
        if manifest.get("icps"):
            md.append("## Ideal Customer Profiles")
            for i, icp in enumerate(manifest["icps"], 1):
                md.append(f"### ICP {i}")
                md.append(f"- **Name:** {icp.get('name', 'N/A')}")
                md.append(f"- **Description:** {icp.get('description', 'N/A')}")
                md.append("")

        # Competitors
        if manifest.get("competitors"):
            md.append("## Competitive Analysis")
            md.append(f"- **Competitors:** {len(manifest['competitors'])} identified")
            md.append("")

        # Messaging
        if manifest.get("value_prop"):
            md.append("## Value Proposition")
            md.append(f"{manifest['value_prop'].get('primary', 'N/A')}")
            md.append("")

        return "\n".join(md)

    def _count_tokens(self, data: Dict[str, Any]) -> int:
        """Count tokens in data using tiktoken if available"""
        try:
            import tiktoken

            tokenizer = tiktoken.get_encoding("cl100k_base")
            text = json.dumps(data, separators=(",", ":"))
            return len(tokenizer.encode(text))
        except ImportError:
            # Fallback to character count approximation
            return len(json.dumps(data)) // 4

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get Redis cache statistics"""
        return self.redis_storage.get_cache_stats()

    def health_check(self) -> Dict[str, Any]:
        """Perform health check on all components"""
        return {
            "redis": self.redis_storage.health_check(),
            "database": "connected" if self.db else "disconnected",
        }
