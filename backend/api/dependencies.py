"""
FastAPI dependencies for dependency injection.
Provides database, Redis, memory, and cognitive engine instances.
"""

from functools import lru_cache
from typing import Generator, Optional

from backend.core.auth import get_auth_context, get_current_user
from backend.core.redis import get_redis_client
from backend.core.supabase_mgr import get_supabase_client
from fastapi import Depends, HTTPException, status
from backend.memory.controller import MemoryController

from backend.cognitive import CognitiveEngine
from supabase import Client

from backend.agents.dispatcher import AgentDispatcher


@lru_cache()
def get_db() -> Client:
    """
    Get Supabase database client.

    Returns:
        Supabase client instance
    """
    client = get_supabase_client()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed",
        )
    return client


@lru_cache()
def get_redis():
    """
    Get Redis client.

    Returns:
        Redis client instance
    """
    client = get_redis_client()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Redis connection failed",
        )
    return client


@lru_cache()
def get_cognitive_engine() -> CognitiveEngine:
    """
    Get cognitive engine instance.

    Returns:
        Cognitive engine instance
    """
    return CognitiveEngine()


@lru_cache()
def get_memory_controller() -> MemoryController:
    """
    Get memory controller instance.

    Returns:
        Memory controller instance
    """
    return MemoryController()


@lru_cache()
def get_agent_dispatcher() -> AgentDispatcher:
    """
    Get agent dispatcher instance.

    Returns:
        Agent dispatcher instance
    """
    return AgentDispatcher()


# Export the auth functions for easier importing
__all__ = [
    "get_db",
    "get_redis",
    "get_cognitive_engine",
    "get_memory_controller",
    "get_agent_dispatcher",
    "get_current_user",
    "get_auth_context",
]
