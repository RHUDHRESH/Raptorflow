"""
Backward compatibility shim for bcm_reflector.

This module provides the legacy import path for reflection functions,
redirecting to the new modular location.
"""

from backend.bcm.reflection import get_reflection_client

_reflection_client = None


def get_client():
    """Get the reflection client instance."""
    global _reflection_client
    if _reflection_client is None:
        _reflection_client = get_reflection_client()
    return _reflection_client


async def reflect(workspace_id: str):
    """
    Run a reflection cycle for a workspace.

    Args:
        workspace_id: Workspace identifier

    Returns:
        Summary of what was learned
    """
    client = get_client()
    return await client.reflect(workspace_id)


def should_auto_reflect(workspace_id: str) -> bool:
    """
    Check if a workspace should automatically trigger reflection.

    Args:
        workspace_id: Workspace identifier

    Returns:
        True if reflection should run automatically
    """
    client = get_client()
    return client.should_reflect(workspace_id)


__all__ = ["reflect", "should_auto_reflect", "get_client"]
