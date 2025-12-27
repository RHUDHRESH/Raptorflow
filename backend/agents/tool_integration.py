"""
Comprehensive Tool Integration for RaptorFlow Agents.
This module provides centralized access to all 10 integrated tools for agents.
"""

import logging
from typing import Any, Dict, List, Optional

from langchain_core.tools import BaseTool

from core.base_tool import BaseRaptorTool
from tools.registry import UnifiedToolRegistry

logger = logging.getLogger("raptorflow.agents.tool_integration")


class AgentToolIntegration:
    """
    Centralized tool integration manager for all agents.
    Provides access to all 10 registered tools with proper filtering and configuration.
    """

    def __init__(self):
        self.registry = UnifiedToolRegistry.get_instance()
        self._tool_cache = {}
        self._langchain_tools_cache = {}

    def get_all_tools(self) -> List[BaseRaptorTool]:
        """Get all registered tools."""
        return [entry.implementation for entry in self.registry.list_tools()]

    def get_langchain_tools(self) -> List[BaseTool]:
        """Get all tools converted to LangChain format."""
        if not self._langchain_tools_cache:
            self._langchain_tools_cache = [
                self._convert_to_langchain_tool(tool) for tool in self.get_all_tools()
            ]
        return self._langchain_tools_cache

    def get_tools_by_category(self, category: str) -> List[BaseRaptorTool]:
        """Get tools filtered by category."""
        tool_categories = {
            "content_creation": ["image_gen"],
            "marketing_ops": [
                "email_automation",
                "social_media_manager",
                "content_scheduler",
            ],
            "analytics": ["analytics", "seo_optimization"],
            "data_management": ["data_export", "crm_integration"],
            "communication": ["notification_system"],
            "research": [
                "raptor_search",
                "perplexity_search",
                "tavily_multihop_search",
            ],
        }

        category_tools = tool_categories.get(category, [])
        return [
            entry.implementation
            for entry in self.registry.list_tools()
            if entry.name in category_tools
        ]

    def get_tools_for_agent_role(self, agent_role: str) -> List[BaseTool]:
        """Get tools specifically suited for agent roles."""
        role_tool_mapping = {
            "strategist": [
                "analytics",
                "crm_integration",
                "raptor_search",
                "perplexity_search",
            ],
            "creator": ["image_gen", "content_scheduler"],
            "analyst": [
                "analytics",
                "data_export",
                "seo_optimization",
                "tavily_multihop_search",
            ],
            "coordinator": [
                "notification_system",
                "email_automation",
                "social_media_manager",
            ],
            "researcher": [
                "raptor_search",
                "perplexity_search",
                "tavily_multihop_search",
            ],
            "operator": ["data_export", "crm_integration", "notification_system"],
            "supervisor": [
                "analytics",
                "data_export",
                "notification_system",
                "perplexity_search",
            ],
            "direct_response": [
                "conversion_optimization",
                "blackbox_roi_history",
                "analytics",
                "raptor_search",
            ],
            "viral_alchemist": [
                "radar_trend_analyzer",
                "raptor_search",
                "perplexity_search",
            ],
            "brand_philosopher": [
                "style_guide_enforcer",
                "foundation_brandkit",
                "raptor_search",
                "perplexity_search",
            ],
            "data_quant": [
                "bigquery_query_engine",
                "bayesian_confidence_scorer",
                "matrix_kpi_stream",
                "analytics",
            ],
            "community_catalyst": [
                "sentiment_analysis",
                "supabase_user_logs",
                "raptor_search",
                "perplexity_search",
            ],
            "media_buyer": [
                "budget_pacing_simulator",
                "ad_platform_mocks",
                "analytics",
                "raptor_search",
            ],
            "seo_moat": [
                "semantic_cluster_generator",
                "radar_keywords",
                "seo_optimization",
                "raptor_search",
            ],
            "pr_specialist": [
                "journalist_pitch_architect",
                "radar_events",
                "raptor_search",
                "perplexity_search",
            ],
            "psychologist": [
                "jtbd_framework_analyzer",
                "cohorts_intelligence",
                "raptor_search",
                "perplexity_search",
            ],
            "product_lead": [
                "benefit_to_feature_mapper",
                "muse_asset_archive",
                "raptor_search",
                "perplexity_search",
            ],
        }

        allowed_tools = role_tool_mapping.get(agent_role, [])
        return [
            self._convert_to_langchain_tool(entry.implementation)
            for entry in self.registry.list_tools()
            if entry.name in allowed_tools
        ]

    def get_tool_by_name(self, tool_name: str) -> Optional[BaseRaptorTool]:
        """Get a specific tool by name."""
        for entry in self.registry.list_tools():
            if entry.name == tool_name:
                return entry.implementation
        return None

    def _convert_to_langchain_tool(self, raptor_tool: BaseRaptorTool) -> BaseTool:
        """Convert RaptorTool to LangChain BaseTool format."""

        class LangChainToolAdapter(BaseTool):
            name: str = raptor_tool.name
            description: str = raptor_tool.description

            def _run(self, *args, **kwargs) -> Any:
                raise NotImplementedError("Use async _arun method")

            async def _arun(self, action: str = None, **kwargs) -> Any:
                # Extract action and parameters from kwargs
                action = action or kwargs.pop("action", "execute")
                return await raptor_tool._execute(action, **kwargs)

        return LangChainToolAdapter()

    def get_tool_descriptions(self) -> Dict[str, str]:
        """Get descriptions of all available tools."""
        return {entry.name: entry.description for entry in self.registry.list_tools()}

    def validate_tool_integration(self) -> Dict[str, Any]:
        """Validate that all tools are properly integrated."""
        validation_results = {
            "total_tools_registered": len(self.registry.list_tools()),
            "expected_tools": 12,
            "registered_tools": [],
            "missing_tools": [],
            "tool_health": {},
            "integration_status": "incomplete",
        }

        expected_tools = [
            "raptor_search",
            "perplexity_search",
            "tavily_multihop_search",
            "image_gen",
            "analytics",
            "crm_integration",
            "content_scheduler",
            "email_automation",
            "social_media_manager",
            "seo_optimization",
            "data_export",
            "notification_system",
        ]

        registered_names = [entry.name for entry in self.registry.list_tools()]
        validation_results["registered_tools"] = registered_names

        # Check for missing tools
        for expected in expected_tools:
            if expected not in registered_names:
                validation_results["missing_tools"].append(expected)

        # Test tool health
        for entry in self.registry.list_tools():
            try:
                tool = entry.implementation
                validation_results["tool_health"][entry.name] = {
                    "name": tool.name,
                    "description": tool.description,
                    "status": "healthy",
                }
            except Exception as e:
                validation_results["tool_health"][entry.name] = {
                    "status": "unhealthy",
                    "error": str(e),
                }

        # Determine overall status
        if (
            len(validation_results["registered_tools"]) >= 10
            and len(validation_results["missing_tools"]) == 0
        ):
            validation_results["integration_status"] = "complete"

        return validation_results


# Global instance for agent access
agent_tool_integration = AgentToolIntegration()


def get_agent_tools(
    agent_role: str, specific_tools: Optional[List[str]] = None
) -> List[BaseTool]:
    """
    Convenience function to get tools for an agent.

    Args:
        agent_role: The role of the agent (strategist, creator, analyst, etc.)
        specific_tools: Optional list of specific tool names to include

    Returns:
        List of LangChain-compatible tools
    """
    if specific_tools:
        tools = []
        for tool_name in specific_tools:
            tool = agent_tool_integration.get_tool_by_name(tool_name)
            if tool:
                tools.append(agent_tool_integration._convert_to_langchain_tool(tool))
        return tools

    return agent_tool_integration.get_tools_for_agent_role(agent_role)


def get_all_available_tools() -> List[BaseTool]:
    """Get all available tools for agents."""
    return agent_tool_integration.get_langchain_tools()


def validate_agent_tool_integration() -> Dict[str, Any]:
    """Validate the complete tool integration for agents."""
    return agent_tool_integration.validate_tool_integration()
