"""
LangGraph Tooling Package for RaptorFlow Agent Society

This package provides the integration layer between LangGraph and RaptorFlow's
backend infrastructure, enabling clean agent graph creation with full audit,
cost, and correlation tracking.
"""

from .contracts import ToolContext, from_request_data, bind_context_to_logger
from .langgraph_integration import (
    make_model_dispatch_tool,
    make_bus_publish_tool,
    start_agent_run,
    complete_agent_run,
    build_tool_context_from_run,
    get_default_toolset,
    langgraph_available,
)

__all__ = [
    # Contracts
    "ToolContext",
    "from_request_data",
    "bind_context_to_logger",

    # Tool factories
    "make_model_dispatch_tool",
    "make_bus_publish_tool",

    # Agent run management
    "start_agent_run",
    "complete_agent_run",
    "build_tool_context_from_run",

    # Utilities
    "get_default_toolset",
    "langgraph_available",
]
