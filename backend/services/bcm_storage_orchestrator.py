"""
BCM Storage Orchestrator Service

Coordinates BCM generation, storage, and retrieval operations across
Redis cache and Supabase database with intelligent fallback and error handling.
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from ..integration.bcm_reducer import BCMReducer
from ..redis.bcm_storage import BCMStorage
from ..services.bcm_database import BCMDatabaseStorage
from ..services.versioning import SemanticVersioning, VersionType


class BCMStorageOrchestrator:
    """
    Service layer orchestrating BCM storage operations.

    Provides end-to-end BCM creation, retrieval, and rebuild capabilities
    with intelligent caching, fallback, and comprehensive error handling.
    """

    def __init__(
        self,
        redis_url: str = None,
        supabase_url: str = None,
        supabase_key: str = None,
        max_connections: int = 10,
    ):
        """
        Initialize BCM storage orchestrator.

        Args:
            redis_url: Redis connection URL
            supabase_url: Supabase project URL
            supabase_key: Supabase service key
            max_connections: Maximum Redis connections
        """
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.reducer = BCMReducer()
        self.redis_storage = BCMStorage(redis_url, max_connections)
        self.database_storage = BCMDatabaseStorage(supabase_url, supabase_key)
        self.versioning = SemanticVersioning()

        # Service metrics
        self.metrics = {
            "total_operations": 0,
            "cache_hits": 0,
            "database_hits": 0,
            "cache_misses": 0,
            "database_misses": 0,
            "generation_errors": 0,
            "storage_errors": 0,
            "rebuilds": 0,
        }

        # Service configuration
        self.cache_first = True  # Try cache before database
        self.auto_compress = True  # Auto-compress if over token budget
        self.max_token_budget = 1200

        self.logger.info("BCM Storage Orchestrator initialized")

    async def create_bcm(
        self,
        raw_step_data: Dict[str, Any],
        workspace_id: str,
        user_id: str = None,
        force_rebuild: bool = False,
    ) -> Dict[str, Any]:
        """
        Create BCM from raw onboarding step data.

        Args:
            raw_step_data: Raw onboarding data from Redis session
            workspace_id: Workspace identifier
            user_id: User identifier
            force_rebuild: Force rebuild even if BCM exists

        Returns:
            Creation result with BCM and metadata
        """
        start_time = datetime.utcnow()
        self.metrics["total_operations"] += 1

        try:
            self.logger.info(f"Creating BCM for workspace {workspace_id}")

            # Reduce raw data to BCM
            bcm = await self.reducer.reduce(raw_step_data)

            # Add checksum to manifest
            bcm = self.reducer._add_checksum_to_manifest(bcm)

            # Apply compression if needed
            if self.auto_compress:
                current_tokens = self.reducer._count_tokens(bcm.dict())
                if current_tokens > self.max_token_budget:
                    self.logger.info(f"Compressing BCM from {current_tokens} tokens")
                    bcm = self.reducer._compress_to_budget(bcm)

            # Store in Redis (all tiers)
            redis_success = self.redis_storage.store_bcm(
                workspace_id, bcm, store_all_tiers=True
            )

            # Store in database with versioning
            db_result = self.database_storage.store_bcm_supabase(
                workspace_id, bcm, user_id, force_version=force_rebuild
            )

            if redis_success and db_result["success"]:
                self.metrics["cache_hits"] += 1
                self.metrics["database_hits"] += 1

                return {
                    "success": True,
                    "bcm": bcm,
                    "version": db_result["version"],
                    "version_type": db_result["version_type"],
                    "reason": db_result["reason"],
                    "stored_in_redis": True,
                    "stored_in_database": True,
                    "token_count": self.reducer._count_tokens(bcm.dict()),
                    "compression_applied": current_tokens > self.max_token_budget,
                    "generation_time_ms": (
                        datetime.utcnow() - start_time
                    ).total_seconds()
                    * 1000,
                    "workspace_id": workspace_id,
                    "user_id": user_id,
                }
            else:
                self.metrics["storage_errors"] += 1
                return {
                    "success": False,
                    "error": "Failed to store BCM",
                    "redis_success": redis_success,
                    "db_result": db_result,
                }

        except Exception as e:
            self.logger.error(f"Error creating BCM: {e}")
            self.metrics["generation_errors"] += 1
            return {"success": False, "error": str(e)}

    async def get_bcm(
        self, workspace_id: str, version: str = None, use_cache: bool = True
    ) -> Optional[BusinessContextManifest]:
        """
        Retrieve BCM with intelligent fallback.

        Args:
            workspace_id: Workspace identifier
            version: Specific version to retrieve
            use_cache: Whether to try cache first

        Returns:
            BCM if found, None otherwise
        """
        start_time = datetime.utcnow()

        try:
            self.logger.debug(
                f"Retrieving BCM for workspace {workspace_id} (cache: {use_cache})"
            )

            bcm = None
            source = "none"

            # Try cache first if enabled
            if use_cache and self.cache_first:
                bcm = self.redis_storage.get_bcm(workspace_id, use_fallback=True)
                if bcm:
                    source = "redis"
                    self.metrics["cache_hits"] += 1
                else:
                    self.metrics["cache_misses"] += 1

            # Fallback to database if cache miss or cache disabled
            if not bcm:
                bcm = self.database_storage.get_bcm_supabase(workspace_id, version)
                if bcm:
                    source = "database"
                    self.metrics["database_hits"] += 1
                else:
                    self.metrics["database_misses"] += 1

            if bcm:
                # Cache the retrieved BCM if it came from database
                if source == "database" and use_cache and self.cache_first:
                    self.redis_storage.store_bcm(
                        workspace_id, bcm, store_all_tiers=False
                    )

                access_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                self.logger.debug(f"BCM retrieved from {source} in {access_time:.2f}ms")

                return bcm
            else:
                self.logger.debug(f"No BCM found for workspace {workspace_id}")
                return None

        except Exception as e:
            self.logger.error(f"Error retrieving BCM: {e}")
            return None

    def get_service_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive service metrics.

        Returns:
            Service performance metrics
        """
        total_ops = self.metrics["total_operations"]

        metrics = self.metrics.copy()
        metrics.update(
            {
                "cache_hit_rate": (
                    (self.metrics["cache_hits"] / total_ops * 100)
                    if total_ops > 0
                    else 0
                ),
                "database_hit_rate": (
                    (self.metrics["database_hits"] / total_ops * 100)
                    if total_ops > 0
                    else 0
                ),
                "error_rate": (
                    (
                        (
                            self.metrics["generation_errors"]
                            + self.metrics["storage_errors"]
                        )
                        / total_ops
                        * 100
                    )
                    if total_ops > 0
                    else 0
                ),
            }
        )

        # Add component-specific metrics
        if self.redis_storage:
            redis_metrics = self.redis_storage.get_cache_stats()
            metrics["redis"] = redis_metrics

        if self.database_storage:
            db_metrics = self.database_storage.get_storage_stats()
            metrics["database"] = db_metrics

        return metrics

    def get_workspace_bcm_info(self, workspace_id: str) -> Dict[str, Any]:
        """
        Get comprehensive BCM information for a workspace.

        Args:
            workspace_id: Workspace identifier

        Returns:
            Workspace BCM information
        """
        try:
            # Get latest BCM
            bcm = self.get_bcm(workspace_id)

            # Get version history
            history = self.database_storage.get_bcm_history(workspace_id)

            # Get stats
            db_stats = self.database_storage.get_workspace_bcm_count(workspace_id)

            # Get cache stats
            cache_stats = self.redis_storage.get_cache_stats()

            return {
                "workspace_id": workspace_id,
                "has_bcm": bcm is not None,
                "latest_version": self.database_storage.get_latest_version(
                    workspace_id
                ),
                "version_count": db_stats,
                "cache_available": cache_stats.get("redis_available", False),
                "cache_hit_rate": cache_stats.get("hit_rate_percent", 0),
                "database_available": self.database_storage.client is not None,
                "token_count": self.reducer._count_tokens(bcm.dict()) if bcm else 0,
                "last_updated": bcm.generated_at if bcm else None,
            }

        except Exception as e:
            self.logger.error(f"Error getting workspace BCM info: {e}")
            return {"error": str(e)}

    def cleanup_workspace(
        self, workspace_id: str, keep_latest: int = 5
    ) -> Dict[str, Any]:
        """
        Clean up old BCM versions for a workspace.

        Args:
            workspace_id: Workspace identifier
            keep_latest: Number of latest versions to keep

        Returns:
            Cleanup result
        """
        try:
            # Clean up database
            db_deleted = self.database_storage.cleanup_old_versions(
                workspace_id, keep_latest
            )

            # Clean up Redis (all tiers)
            redis_invalidated = self.redis_storage.invalidate_bcm(workspace_id)

            return {
                "success": True,
                "database_deleted": db_deleted,
                "redis_invalidated": redis_invalidated,
                "total_deleted": db_deleted + redis_invalidated,
            }

        except Exception as e:
            self.logger.error(f"Error cleaning up workspace BCM data: {e}")
            return {"success": False, "error": str(e)}

    def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check on all components.

        Returns:
            Health check results
        """
        health = {
            "service": "healthy",
            "components": {},
            "metrics": self.get_service_metrics(),
        }

        # Check reducer
        try:
            health["components"]["reducer"] = "healthy"
        except Exception as e:
            health["components"]["reducer"] = f"error: {e}"

        # Check Redis storage
        redis_health = self.redis_storage.health_check()
        health["components"]["redis"] = redis_health

        # Check database storage
        db_stats = self.database_storage.get_storage_stats()
        health["components"]["database"] = {
            "available": db_stats.get("available", False),
            "error": db_stats.get("error"),
        }

        # Overall health status
        all_healthy = all(
            status == "healthy" or status == "connected"
            for status in [
                health["components"]["reducer"],
                health["components"]["redis"].get("redis_available", False),
                health["components"]["database"].get("available", False),
            ]
        )

        health["service"] = "healthy" if all_healthy else "degraded"

        return health

    def close(self) -> None:
        """Close all service connections."""
        try:
            if self.redis_storage:
                self.redis_storage.close()

            if self.database_storage:
                self.database_storage.close()

            self.logger.info("BCM Storage Orchestrator closed")

        except Exception as e:
            logging.error(f"Error closing service connections: {e}")

    def __del__(self):
        """Cleanup on deletion."""
        self.close()
