"""
Backward compatibility shim for bcm_memory.

This module provides the legacy import path for memory client,
redirecting to the new modular location.
"""

from backend.bcm.memory import get_memory_client

bcm_memory = get_memory_client()


def get_relevant_memories(workspace_id: str, limit: int = 10):
    """Backward compatible alias for get_relevant."""
    return bcm_memory.get_relevant(workspace_id=workspace_id, limit=limit)


__all__ = ["bcm_memory", "get_memory_client", "get_relevant_memories"]
