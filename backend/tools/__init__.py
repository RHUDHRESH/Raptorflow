"""
Raptorflow Tools Package
========================

Comprehensive tools package for the Raptorflow AI agent system.
Provides various tools for data processing, web scraping, content generation,
and other common tasks.

Features:
- Base tool classes and utilities
- Web scraping and data extraction tools
- Content generation and optimization tools
- Data analysis and visualization tools
- Communication and notification tools
- File processing and conversion tools
- Integration and API tools
- Utility and helper tools

Tool Categories:
- Data Processing: Data analysis, transformation, validation
- Web Tools: Scraping, search, API integration
- Content Tools: Generation, optimization, analysis
- Communication: Email, notifications, messaging
- File Tools: Processing, conversion, storage
- Integration: Third-party services, APIs
- Utilities: Helper functions, common operations
"""

# Tool registry and management
from typing import Any, Dict, List, Type

import structlog

from .base import BaseTool, ToolError, ToolResult, ToolStatus
# from .content_generator import ContentGeneratorTool
# from .export_tool import ExportTool
# from .feedback_tool import FeedbackTool
# from .template_tool import TemplateTool
from .web_scraper import WebScraperTool
from .web_search import WebSearchTool
from .reddit_scraper import RedditScraperTool

logger = structlog.get_logger(__name__)

# Tool registry
TOOL_REGISTRY: Dict[str, Type[BaseTool]] = {}

# Tool categories
TOOL_CATEGORIES = {
    "data_processing": [
        "DataAnalysisTool",
        "DataTransformerTool",
        "DataValidatorTool",
    ],
    "web_tools": [
        "WebSearchTool",
        "WebScraperTool",
        "RedditScraperTool",
        "APIClientTool",
    ],
    "content_tools": [
        "ContentGeneratorTool",
        "ContentOptimizerTool",
        "TemplateTool",
    ],
    "communication": [
        "EmailTool",
        "NotificationTool",
        "ChatTool",
    ],
    "file_tools": [
        "FileProcessorTool",
        "FileConverterTool",
        "StorageTool",
    ],
    "integration": [
        "CRMTool",
        "AnalyticsTool",
        "SocialMediaTool",
    ],
    "utilities": [
        "CalculatorTool",
        "FormatterTool",
        "ValidatorTool",
    ],
}


# Register all tools
def register_tool(tool_class: Type[BaseTool]):
    """Register a tool class in the registry."""
    tool_name = tool_class.__name__
    TOOL_REGISTRY[tool_name] = tool_class
    logger.debug("Tool registered", tool=tool_name)


# Auto-register all imported tools
register_tool(WebSearchTool)
register_tool(WebScraperTool)
register_tool(RedditScraperTool)
# register_tool(ContentGeneratorTool)
# register_tool(TemplateTool)
# register_tool(FeedbackTool)
# register_tool(ExportTool)


def get_tool(tool_name: str) -> Type[BaseTool]:
    """Get a tool class by name."""
    if tool_name not in TOOL_REGISTRY:
        raise ValueError(f"Tool not found: {tool_name}")
    return TOOL_REGISTRY[tool_name]


def list_tools(category: str = None) -> List[str]:
    """List all available tools, optionally filtered by category."""
    if category:
        return TOOL_CATEGORIES.get(category, [])
    return list(TOOL_REGISTRY.keys())


def get_tool_info(tool_name: str) -> Dict[str, Any]:
    """Get information about a tool."""
    tool_class = get_tool(tool_name)
    return {
        "name": tool_class.__name__,
        "description": tool_class.__doc__ or "",
        "category": getattr(tool_class, "CATEGORY", "unknown"),
        "version": getattr(tool_class, "VERSION", "1.0.0"),
        "author": getattr(tool_class, "AUTHOR", "Raptorflow Team"),
        "required_config": getattr(tool_class, "REQUIRED_CONFIG", []),
        "optional_config": getattr(tool_class, "OPTIONAL_CONFIG", []),
        "capabilities": getattr(tool_class, "CAPABILITIES", []),
    }


def get_all_tools_info() -> Dict[str, Dict[str, Any]]:
    """Get information about all tools."""
    return {tool_name: get_tool_info(tool_name) for tool_name in TOOL_REGISTRY}


# Tool factory
class ToolFactory:
    """Factory for creating tool instances."""

    @staticmethod
    def create_tool(tool_name: str, config: Dict[str, Any] = None) -> BaseTool:
        """Create a tool instance."""
        tool_class = get_tool(tool_name)
        return tool_class(config or {})

    @staticmethod
    def create_tools(tool_configs: Dict[str, Dict[str, Any]]) -> Dict[str, BaseTool]:
        """Create multiple tool instances."""
        tools = {}
        for tool_name, config in tool_configs.items():
            tools[tool_name] = ToolFactory.create_tool(tool_name, config)
        return tools


# Tool manager
class ToolManager:
    """Manager for tool instances and operations."""

    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self.tool_configs: Dict[str, Dict[str, Any]] = {}

    def add_tool(self, tool_name: str, config: Dict[str, Any] = None) -> BaseTool:
        """Add a tool instance."""
        tool = ToolFactory.create_tool(tool_name, config)
        self.tools[tool_name] = tool
        self.tool_configs[tool_name] = config or {}
        return tool

    def remove_tool(self, tool_name: str) -> bool:
        """Remove a tool instance."""
        if tool_name in self.tools:
            del self.tools[tool_name]
            del self.tool_configs[tool_name]
            return True
        return False

    def get_tool(self, tool_name: str) -> BaseTool:
        """Get a tool instance."""
        if tool_name not in self.tools:
            raise ValueError(f"Tool not found: {tool_name}")
        return self.tools[tool_name]

    def list_tools(self) -> List[str]:
        """List all tool instances."""
        return list(self.tools.keys())

    def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """Execute a tool."""
        tool = self.get_tool(tool_name)
        return tool.execute(**kwargs)

    def get_tool_status(self, tool_name: str) -> Dict[str, Any]:
        """Get tool status."""
        tool = self.get_tool(tool_name)
        return tool.get_status()

    def cleanup(self):
        """Cleanup all tools."""
        for tool in self.tools.values():
            if hasattr(tool, "cleanup"):
                tool.cleanup()
        self.tools.clear()
        self.tool_configs.clear()


# Global tool manager instance
tool_manager = ToolManager()


# Initialize default tools
def initialize_default_tools():
    """Initialize default tool instances."""
    default_tools = {
        "web_search": {},
        "web_scraper": {},
        # "content_generator": {},
        # "template_tool": {},
        # "feedback_tool": {},
        # "export_tool": {},
    }

    for tool_name, config in default_tools.items():
        try:
            tool_manager.add_tool(tool_name, config)
            logger.info("Default tool initialized", tool=tool_name)
        except Exception as e:
            logger.error(
                "Failed to initialize default tool", tool=tool_name, error=str(e)
            )


# Initialize default tools on import
initialize_default_tools()

# Export main components
__all__ = [
    # Base classes
    "BaseTool",
    "ToolResult",
    "ToolStatus",
    "ToolError",
    # Tool implementations
    "WebSearchTool",
    "WebScraperTool",
    "ContentGeneratorTool",
    "TemplateTool",
    "FeedbackTool",
    "ExportTool",
    # Registry and management
    "TOOL_REGISTRY",
    "TOOL_CATEGORIES",
    "register_tool",
    "get_tool",
    "list_tools",
    "get_tool_info",
    "get_all_tools_info",
    # Factory and manager
    "ToolFactory",
    "ToolManager",
    "tool_manager",
    # Initialization
    "initialize_default_tools",
]
