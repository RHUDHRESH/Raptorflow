"""
LangGraph-based agent orchestration package.

This package is intentionally minimal:
- one orchestration standard (`langgraph`)
- one canonical content-generation graph for Muse
"""

from backend.agents.langgraph_muse_orchestrator import (
    REASONING_DEPTH_PROFILES,
    langgraph_muse_orchestrator,
)

__all__ = ["langgraph_muse_orchestrator", "REASONING_DEPTH_PROFILES"]

