"""
Raptorflow agents package.

Keep this module lightweight: importing `agents` must not trigger heavy SDK
initialization (Vertex AI, Redis, etc). Most exports are provided lazily via
`__getattr__`.
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "ModelTier",
    "AgentConfig",
    "get_config",
    "estimate_cost",
    "AgentState",
    "WorkspaceContext",
    "ExecutionTrace",
    "create_initial_state",
    "update_state",
    "add_message",
    "get_last_message",
    "get_recent_context",
    "calculate_total_cost",
    "get_agent_summary",
    "BaseAgent",
    "VertexAILLM",
    "get_llm",
    "quick_generate",
    "quick_generate_structured",
    # Exceptions
    "RaptorflowError",
    "ConfigurationError",
    "ValidationError",
    "DatabaseError",
    "LLMError",
    "RoutingError",
    "ToolError",
    "WorkspaceError",
    "CostError",
    "AuthenticationError",
    "TimeoutError",
    "RateLimitError",
    "MemoryError",
    "NetworkError",
    "SecurityError",
    # Tools
    "get_tool_registry",
    "register_tool",
    "get_tool",
    "list_tools",
    "get_tools_for_agent",
    # Skills
    "get_skills_registry",
    "get_skill",
    "list_skills",
    "Skill",
    "SkillLevel",
    "SkillCategory",
    # Specialist Agents
    "OnboardingOrchestrator",
    "EvidenceProcessor",
    "FactExtractor",
    "ICPArchitect",
    "MoveStrategist",
    "ContentCreator",
    "BlackboxStrategist",
    "MarketResearch",
    "AnalyticsAgent",
    "DailyWinsGenerator",
    "EmailSpecialist",
    "CampaignPlanner",
    "BlogWriter",
    "QualityChecker",
    "RevisionAgent",
    "CompetitorIntelAgent",
    "TrendAnalyzer",
    "PersonaSimulator",
    "SocialMediaAgent",
    # Core Components
    "AgentDispatcher",
    "AgentRegistry",
    "RoutingPipeline",
    "RoutingDecision",
    "RequestPreprocessor",
    "create_raptorflow_graph",
    "execute_workflow",
]


_EXCEPTION_NAMES = {
    "AuthenticationError",
    "ConfigurationError",
    "CostError",
    "DatabaseError",
    "LLMError",
    "MemoryError",
    "NetworkError",
    "RaptorflowError",
    "RateLimitError",
    "RoutingError",
    "SecurityError",
    "TimeoutError",
    "ToolError",
    "ValidationError",
    "WorkspaceError",
}

_CONFIG_NAMES = {
    "ModelTier",
    "SimplifiedConfig",
    "estimate_cost",
    "get_config",
    "validate_config",
}

_STATE_NAMES = {
    "AgentState",
    "WorkspaceContext",
    "ExecutionTrace",
    "add_message",
    "calculate_total_cost",
    "create_initial_state",
    "get_agent_summary",
    "get_last_message",
    "get_recent_context",
    "update_state",
}

_TOOLS_NAMES = {
    "get_tool",
    "get_tool_registry",
    "get_tools_for_agent",
    "list_tools",
    "register_tool",
}

_SKILLS_NAMES = {
    "Skill",
    "SkillCategory",
    "SkillLevel",
    "get_skill",
    "get_skills_registry",
    "list_skills",
}

_SPECIALIST_NAMES = {
    "AnalyticsAgent",
    "BlackboxStrategist",
    "BlogWriter",
    "CampaignPlanner",
    "CompetitorIntelAgent",
    "ContentCreator",
    "DailyWinsGenerator",
    "EmailSpecialist",
    "EvidenceProcessor",
    "FactExtractor",
    "ICPArchitect",
    "MarketResearch",
    "MoveStrategist",
    "OnboardingOrchestrator",
    "PersonaSimulator",
    "QualityChecker",
    "RevisionAgent",
    "SocialMediaAgent",
    "TrendAnalyzer",
}


def __getattr__(name: str) -> Any:  # noqa: C901 - intentional lazy export router
    if name == "AgentConfig":
        from backend.config.agent_config import AgentConfig  # noqa: PLC0415

        return AgentConfig

    if name == "BaseAgent":
        from .base import BaseAgent  # noqa: PLC0415

        return BaseAgent

    if name in _CONFIG_NAMES:
        from . import config as _config  # noqa: PLC0415

        return getattr(_config, name)

    if name in _EXCEPTION_NAMES:
        from . import exceptions as _exceptions  # noqa: PLC0415

        return getattr(_exceptions, name)

    if name in _STATE_NAMES:
        from . import state as _state  # noqa: PLC0415

        return getattr(_state, name)

    if name in {
        "VertexAILLM",
        "get_llm",
        "quick_generate",
        "quick_generate_structured",
    }:
        from . import llm as _llm  # noqa: PLC0415

        return getattr(_llm, name)

    if name in _TOOLS_NAMES:
        from .tools import registry as _tools_registry  # noqa: PLC0415

        return getattr(_tools_registry, name)

    if name in _SKILLS_NAMES:
        from .skills import registry as _skills_registry  # noqa: PLC0415

        return getattr(_skills_registry, name)

    if name in {"AgentDispatcher", "AgentRegistry"}:
        from .dispatcher import AgentDispatcher, AgentRegistry  # noqa: PLC0415

        return AgentDispatcher if name == "AgentDispatcher" else AgentRegistry

    if name in {"RoutingPipeline", "RoutingDecision"}:
        from .routing.pipeline import RoutingDecision, RoutingPipeline  # noqa: PLC0415

        return RoutingPipeline if name == "RoutingPipeline" else RoutingDecision

    if name == "RequestPreprocessor":
        from .preprocessing import RequestPreprocessor  # noqa: PLC0415

        return RequestPreprocessor

    if name in {"create_raptorflow_graph", "execute_workflow"}:
        from .graphs.main import (  # noqa: PLC0415
            create_raptorflow_graph,
            execute_workflow,
        )

        return (
            create_raptorflow_graph
            if name == "create_raptorflow_graph"
            else execute_workflow
        )

    if name in _SPECIALIST_NAMES:
        from . import specialists as _specialists  # noqa: PLC0415

        return getattr(_specialists, name)

    raise AttributeError(name)


def __dir__() -> list[str]:
    return sorted(set(__all__) | set(globals().keys()))
