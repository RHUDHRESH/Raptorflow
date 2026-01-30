"""
Package initialization for Raptorflow agents.
"""

import os

from backend.config.agent_config import AgentConfig

from .base import BaseAgent
from .config import ModelTier, SimplifiedConfig, estimate_cost, get_config

# Import core components
from .dispatcher import AgentDispatcher, AgentRegistry
from .exceptions import (
    AuthenticationError,
    ConfigurationError,
    CostError,
    DatabaseError,
    LLMError,
    MemoryError,
    NetworkError,
    RaptorflowError,
    RateLimitError,
    RoutingError,
    SecurityError,
    TimeoutError,
    ToolError,
    ValidationError,
    WorkspaceError,
)
from .graphs.main import create_raptorflow_graph, execute_workflow
from .llm import VertexAILLM, get_llm, quick_generate, quick_generate_structured
from .preprocessing import RequestPreprocessor
from .routing.pipeline import RoutingDecision, RoutingPipeline
from .skills.registry import (
    Skill,
    SkillCategory,
    SkillLevel,
    get_skill,
    get_skills_registry,
    list_skills,
)

# Import specialist agents only if not skipping init
if os.getenv("RAPTORFLOW_SKIP_INIT", "false").lower() != "true":
    from .specialists import (
        AnalyticsAgent,
        BlackboxStrategist,
        BlogWriter,
        CampaignPlanner,
        CompetitorIntelAgent,
        ContentCreator,
        DailyWinsGenerator,
        EmailSpecialist,
        EvidenceProcessor,
        FactExtractor,
        ICPArchitect,
        MarketResearch,
        MoveStrategist,
        OnboardingOrchestrator,
        PersonaSimulator,
        QualityChecker,
        RevisionAgent,
        SocialMediaAgent,
        TrendAnalyzer,
    )
else:
    # define dummy or None for these if needed, or just relying on direct imports for tests
    pass

from .state import (
    AgentState,
    add_message,
    calculate_total_cost,
    create_initial_state,
    get_agent_summary,
    get_last_message,
    get_recent_context,
    update_state,
)
from .tools.registry import (
    get_tool,
    get_tool_registry,
    get_tools_for_agent,
    list_tools,
    register_tool,
)

# Export main classes
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
