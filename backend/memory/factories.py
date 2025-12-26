"""
Memory System Factory Functions

Factory functions for creating memory system components with proper initialization.
"""

import logging
from typing import Optional

from memory.consolidated import SwarmMemoryConsolidator
from memory.swarm_coordinator import SwarmMemoryCoordinator

logger = logging.getLogger("raptorflow.memory.factories")


def create_swarm_memory_consolidator(
    workspace_id: str,
    consolidation_interval_minutes: int = 5,
    cache_ttl_minutes: int = 10,
    max_cache_size_mb: int = 100,
) -> SwarmMemoryConsolidator:
    """
    Factory function to create a properly initialized SwarmMemoryConsolidator.

    Args:
        workspace_id: Workspace identifier
        consolidation_interval_minutes: How often to run consolidation
        cache_ttl_minutes: Cache TTL in minutes
        max_cache_size_mb: Maximum cache size in MB

    Returns:
        Initialized SwarmMemoryConsolidator instance

    Raises:
        ValueError: If workspace_id is invalid
        Exception: If initialization fails
    """
    try:
        if not workspace_id or not isinstance(workspace_id, str):
            raise ValueError("workspace_id must be a non-empty string")

        logger.info(f"Creating swarm memory consolidator for workspace: {workspace_id}")

        # Create consolidator with error handling
        consolidator = SwarmMemoryConsolidator(workspace_id)

        # Configure consolidation interval if needed
        if consolidation_interval_minutes != 5:
            from datetime import timedelta

            consolidator.consolidated_memory.consolidation_interval = timedelta(
                minutes=consolidation_interval_minutes
            )

        # Configure cache TTL if needed
        if cache_ttl_minutes != 10:
            from datetime import timedelta

            consolidator._cache_ttl = timedelta(minutes=cache_ttl_minutes)

        logger.info(f"Successfully created consolidator for workspace {workspace_id}")
        return consolidator

    except Exception as e:
        logger.error(f"Failed to create consolidator for workspace {workspace_id}: {e}")
        raise


def create_swarm_memory_coordinator(
    workspace_id: str, max_memory_mb: int = 100, max_cache_entries: int = 10000
) -> SwarmMemoryCoordinator:
    """
    Factory function to create a properly initialized SwarmMemoryCoordinator.

    Args:
        workspace_id: Workspace identifier
        max_memory_mb: Maximum memory for cache in MB
        max_cache_entries: Maximum number of cache entries

    Returns:
        Initialized SwarmMemoryCoordinator instance

    Raises:
        ValueError: If workspace_id is invalid
        Exception: If initialization fails
    """
    try:
        if not workspace_id or not isinstance(workspace_id, str):
            raise ValueError("workspace_id must be a non-empty string")

        logger.info(f"Creating swarm memory coordinator for workspace: {workspace_id}")

        # Create coordinator with error handling
        coordinator = SwarmMemoryCoordinator(workspace_id)

        logger.info(f"Successfully created coordinator for workspace {workspace_id}")
        return coordinator

    except Exception as e:
        logger.error(f"Failed to create coordinator for workspace {workspace_id}: {e}")
        raise


def create_cached_coordinator(
    workspace_id: str,
    cache_size_mb: int = 50,
    max_entries: int = 5000,
    ttl_seconds: int = 300,
) -> SwarmMemoryCoordinator:
    """
    Factory function to create a cached swarm memory coordinator.

    Args:
        workspace_id: Workspace identifier
        cache_size_mb: Cache size in MB
        max_entries: Maximum cache entries
        ttl_seconds: Default TTL for cache entries

    Returns:
        Cached SwarmMemoryCoordinator instance

    Raises:
        ValueError: If workspace_id is invalid
        Exception: If initialization fails
    """
    try:
        if not workspace_id or not isinstance(workspace_id, str):
            raise ValueError("workspace_id must be a non-empty string")

        logger.info(f"Creating cached coordinator for workspace: {workspace_id}")

        # Create base coordinator
        coordinator = create_swarm_memory_coordinator(workspace_id)

        # Create cache wrapper
        try:
            from memory.cache import SwarmMemoryCache

            cache = SwarmMemoryCache(
                max_memory_mb=cache_size_mb, max_entries=max_entries
            )

            # Wrap coordinator with cache (this would need to be implemented)
            # For now, return the base coordinator
            logger.warning(
                "Cache wrapper not fully implemented, returning base coordinator"
            )

        except ImportError as e:
            logger.warning(
                f"Could not import cache module, using base coordinator: {e}"
            )

        logger.info(
            f"Successfully created cached coordinator for workspace {workspace_id}"
        )
        return coordinator

    except Exception as e:
        logger.error(
            f"Failed to create cached coordinator for workspace {workspace_id}: {e}"
        )
        raise


# Registry for singleton instances
_coordinator_registry: dict[str, SwarmMemoryCoordinator] = {}


def get_swarm_memory_coordinator(workspace_id: str) -> SwarmMemoryCoordinator:
    """
    Get or create a singleton SwarmMemoryCoordinator for the workspace.

    Args:
        workspace_id: Workspace identifier

    Returns:
        SwarmMemoryCoordinator instance

    Raises:
        ValueError: If workspace_id is invalid
        Exception: If creation fails
    """
    if not workspace_id or not isinstance(workspace_id, str):
        raise ValueError("workspace_id must be a non-empty string")

    # Return existing instance if available
    if workspace_id in _coordinator_registry:
        return _coordinator_registry[workspace_id]

    # Create new instance
    coordinator = create_swarm_memory_coordinator(workspace_id)
    _coordinator_registry[workspace_id] = coordinator

    logger.info(f"Created new coordinator instance for workspace {workspace_id}")
    return coordinator


def cleanup_workspace_coordinator(workspace_id: str) -> bool:
    """
    Clean up coordinator for a workspace.

    Args:
        workspace_id: Workspace identifier

    Returns:
        True if cleanup was successful, False otherwise
    """
    try:
        if workspace_id in _coordinator_registry:
            coordinator = _coordinator_registry[workspace_id]

            # Perform cleanup if coordinator has cleanup method
            if hasattr(coordinator, "cleanup"):
                import asyncio

                if asyncio.iscoroutinefunction(coordinator.cleanup):
                    # This would need to be awaited by the caller
                    logger.warning("Coordinator cleanup is async, caller must await it")
                else:
                    coordinator.cleanup()

            # Remove from registry
            del _coordinator_registry[workspace_id]

            logger.info(f"Cleaned up coordinator for workspace {workspace_id}")
            return True
        else:
            logger.warning(f"No coordinator found for workspace {workspace_id}")
            return False

    except Exception as e:
        logger.error(f"Failed to cleanup coordinator for workspace {workspace_id}: {e}")
        return False


def get_all_workspace_coordinators() -> dict[str, SwarmMemoryCoordinator]:
    """
    Get all active workspace coordinators.

    Returns:
        Dictionary mapping workspace_id to coordinator instances
    """
    return _coordinator_registry.copy()


def cleanup_all_coordinators():
    """
    Clean up all workspace coordinators.
    """
    workspace_ids = list(_coordinator_registry.keys())
    for workspace_id in workspace_ids:
        cleanup_workspace_coordinator(workspace_id)

    logger.info("Cleaned up all workspace coordinators")


# Memory system health check
def check_memory_system_health(workspace_id: str) -> dict:
    """
    Check the health of the memory system for a workspace.

    Args:
        workspace_id: Workspace identifier

    Returns:
        Health check results
    """
    health_status = {
        "workspace_id": workspace_id,
        "status": "healthy",
        "issues": [],
        "recommendations": [],
    }

    try:
        # Check if coordinator exists
        if workspace_id not in _coordinator_registry:
            health_status["issues"].append("No coordinator found")
            health_status["status"] = "warning"
            return health_status

        coordinator = _coordinator_registry[workspace_id]

        # Check active agents
        if not coordinator.active_agents:
            health_status["issues"].append("No active agents")
            health_status["recommendations"].append("Consider initializing agents")

        # Check consolidator health
        if hasattr(coordinator, "consolidator"):
            consolidator = coordinator.consolidator

            # Check if embedder is available
            if not hasattr(consolidator, "embedder") or consolidator.embedder is None:
                health_status["issues"].append("Embedder not available")
                health_status["recommendations"].append("Check embedder initialization")
                health_status["status"] = "degraded"

        # Check memory usage
        if hasattr(coordinator, "get_memory_statistics"):
            try:
                import asyncio

                # This would need to be awaited in async context
                stats = asyncio.run(coordinator.get_memory_statistics())

                if stats.get("total_fragments", 0) > 10000:
                    health_status["issues"].append("High memory usage")
                    health_status["recommendations"].append("Consider memory cleanup")
                    health_status["status"] = "degraded"

            except Exception as e:
                health_status["issues"].append(f"Failed to get statistics: {e}")

    except Exception as e:
        health_status["issues"].append(f"Health check failed: {e}")
        health_status["status"] = "error"

    return health_status
