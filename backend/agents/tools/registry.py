"""
Tool registry for managing Raptorflow agent tools.
"""

import logging
import threading
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

from .base import RaptorflowTool, ToolResult
from .database import DatabaseTool
from .web_search import WebSearchTool

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Thread-safe singleton registry for managing tools."""

    _instance: Optional["ToolRegistry"] = None
    _lock: threading.Lock = threading.Lock()
    _tools: Dict[str, RaptorflowTool] = {}
    _categories: Dict[str, List[str]] = {}
    _tools_lock: threading.RLock = threading.RLock()

    def __new__(cls) -> "ToolRegistry":
        """Implement thread-safe singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    @contextmanager
    def _tools_context(self):
        """Context manager for thread-safe tool operations."""
        with self._tools_lock:
            yield

    def _initialize(self):
        """Initialize the registry with default tools."""
        self._tools = {}
        self._categories = {
            "search": ["web_search"],
            "database": ["database"],
            "content": [],
            "utility": [],
            "integration": [],
        }

        # Register Database Tool
        self.register(DatabaseTool(), "database")
        
        # Register Titan as the primary web_search tool
        try:
            from backend.services.titan.tool import TitanIntelligenceTool
            titan = TitanIntelligenceTool()
            titan.name = "web_search" # Alias Titan as 'web_search' for agents
            self.register(titan, "search")
            logger.info("Titan SOTA Engine registered as primary 'web_search' tool.")
        except Exception as e:
            logger.error(f"Failed to register Titan tool as web_search: {e}")
            # Fallback to legacy search only if Titan fails
            self.register(WebSearchTool(), "search")

    def register(self, tool: RaptorflowTool, category: str = "utility"):
        """Register a tool in the registry (thread-safe)."""
        with self._tools_context():
            if tool.name in self._tools:
                logger.warning(f"Tool '{tool.name}' already registered, overwriting")

            self._tools[tool.name] = tool

            # Add to category
            if category not in self._categories:
                self._categories[category] = []

            if tool.name not in self._categories[category]:
                self._categories[category].append(tool.name)

            logger.info(f"Registered tool '{tool.name}' in category '{category}'")

    def get(self, name: str) -> Optional[RaptorflowTool]:
        """Get a tool by name (thread-safe)."""
        with self._tools_context():
            return self._tools.get(name)

    def get_by_category(self, category: str) -> List[RaptorflowTool]:
        """Get all tools in a category (thread-safe)."""
        with self._tools_context():
            tool_names = self._categories.get(category, [])
            return [self._tools[name] for name in tool_names if name in self._tools]

    def get_all(self) -> Dict[str, RaptorflowTool]:
        """Get all registered tools (thread-safe)."""
        with self._tools_context():
            return self._tools.copy()

    def list_tools(self) -> List[str]:
        """List all tool names (thread-safe)."""
        with self._tools_context():
            return list(self._tools.keys())

    def list_categories(self) -> List[str]:
        """List all categories."""
        return list(self._categories.keys())

    def get_tools_for_agent(self, categories: List[str]) -> List[RaptorflowTool]:
        """Get tools appropriate for an agent based on categories."""
        tools = []

        for category in categories:
            if category in self._categories:
                category_tools = self.get_by_category(category)
                tools.extend(category_tools)

        # Remove duplicates while preserving order
        seen = set()
        unique_tools = []
        for tool in tools:
            if tool.name not in seen:
                seen.add(tool.name)
                unique_tools.append(tool)

        return unique_tools

    def unregister(self, name: str) -> bool:
        """Unregister a tool."""
        if name not in self._tools:
            logger.warning(f"Tool '{name}' not found in registry")
            return False

        tool = self._tools[name]
        del self._tools[name]

        # Remove from categories
        for category, tools in self._categories.items():
            if name in tools:
                tools.remove(name)

        logger.info(f"Unregistered tool '{name}'")
        return True

    def get_tool_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a tool."""
        tool = self.get(name)
        if not tool:
            return None

        # Find which category the tool belongs to
        tool_category = None
        for category, tools in self._categories.items():
            if name in tools:
                tool_category = category
                break

        return {
            **tool.get_info(),
            "category": tool_category,
            "registered_at": datetime.now().isoformat(),
        }

    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        return {
            "total_tools": len(self._tools),
            "total_categories": len(self._categories),
            "tools_by_category": {
                cat: len(tools) for cat, tools in self._categories.items()
            },
            "last_updated": datetime.now().isoformat(),
        }

    def validate_tool(self, tool: RaptorflowTool) -> bool:
        """Validate that a tool meets requirements."""
        # Check required attributes
        if not hasattr(tool, "name") or not tool.name:
            logger.error("Tool missing required 'name' attribute")
            return False

        if not hasattr(tool, "description") or not tool.description:
            logger.error("Tool missing required 'description' attribute")
            return False

        if not hasattr(tool, "_arun") or not callable(tool._arun):
            logger.error("Tool missing required '_arun' method")
            return False

        if not hasattr(tool, "arun") or not callable(tool.arun):
            logger.error("Tool missing required 'arun' method")
            return False

        return True

    def hot_reload(self, tool_name: str, new_tool: RaptorflowTool) -> bool:
        """Hot reload a tool."""
        if tool_name not in self._tools:
            logger.error(f"Cannot hot reload: tool '{tool_name}' not found")
            return False

        # Find the category of the existing tool
        old_tool = self._tools[tool_name]
        old_category = None
        for category, tools in self._categories.items():
            if tool_name in tools:
                old_category = category
                break

        # Validate new tool
        if not self.validate_tool(new_tool):
            logger.error(f"Cannot hot reload: new tool validation failed")
            return False

        # Unregister old tool
        self.unregister(tool_name)

        # Register new tool
        self.register(new_tool, old_category or "utility")

        logger.info(f"Hot reloaded tool '{tool_name}'")
        return True

    def search_tools(self, query: str) -> List[RaptorflowTool]:
        """Search tools by name or description."""
        query_lower = query.lower()
        matching_tools = []

        for tool in self._tools.values():
            # Search in name
            if query_lower in tool.name.lower():
                matching_tools.append(tool)
                continue

            # Search in description
            if query_lower in tool.description.lower():
                matching_tools.append(tool)

        return matching_tools

    def initialize_default_tools(self):
        """Initialize default tools (called during startup)."""
        # Clear existing tools
        self._tools.clear()
        self._categories.clear()

        # Re-initialize
        self._initialize()

        logger.info("Initialized default tools in registry")


# Global registry instance
def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance."""
    return ToolRegistry()


# Convenience functions
def register_tool(tool: RaptorflowTool, category: str = "utility"):
    """Register a tool in the global registry."""
    registry = get_tool_registry()
    registry.register(tool, category)


def get_tool(name: str) -> Optional[RaptorflowTool]:
    """Get a tool from the global registry."""
    registry = get_tool_registry()
    return registry.get(name)


def list_tools() -> List[str]:
    """List all tools in the global registry."""
    registry = get_tool_registry()
    return registry.list_tools()


def get_tools_for_agent(categories: List[str]) -> List[RaptorflowTool]:
    """Get tools for an agent from the global registry."""
    registry = get_tool_registry()
    return registry.get_tools_for_agent(categories)
