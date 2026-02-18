"""
LangGraph-based agent orchestration package.

This package is intentionally minimal:
- one orchestration standard (`langgraph`)
- one canonical content-generation graph for Muse
"""

from backend.agents.muse.orchestrator import (
    REASONING_DEPTH_PROFILES,
    langgraph_muse_orchestrator,
)
from backend.agents.context.orchestrator import (
    format_bcm_row,
    langgraph_context_orchestrator,
)
from backend.agents.campaign_moves.orchestrator import (
    langgraph_campaign_moves_orchestrator,
)
from backend.agents.optional.orchestrator import (
    langgraph_optional_orchestrator,
)
from backend.agents.runtime.profiles import (
    EXECUTION_MODES,
    INTENSITY_PROFILES,
    intensity_profile,
    normalize_execution_mode,
    normalize_intensity,
)

__all__ = [
    "REASONING_DEPTH_PROFILES",
    "format_bcm_row",
    "EXECUTION_MODES",
    "INTENSITY_PROFILES",
    "intensity_profile",
    "normalize_execution_mode",
    "normalize_intensity",
    "langgraph_muse_orchestrator",
    "langgraph_context_orchestrator",
    "langgraph_campaign_moves_orchestrator",
    "langgraph_optional_orchestrator",
]
