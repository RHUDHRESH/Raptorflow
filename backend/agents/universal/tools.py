import logging
from typing import Any, Dict, List, Optional, Callable, Awaitable
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """Base class for all agent tools."""

    @abstractmethod
    async def run(self, **kwargs) -> Any:
        """Execute the tool with given arguments."""
        pass


class OCRMockTool(BaseTool):
    """Mock tool for OCR processing."""

    async def run(self, file_content: bytes, filename: str) -> str:
        logger.info(f"Mock OCR processing for {filename}")
        return f"[Mock Extracted Text for {filename}] This is a high-quality transcription of your business document."


class ScraperMockTool(BaseTool):
    """Mock tool for web scraping."""

    async def run(self, url: str) -> Dict[str, Any]:
        logger.info(f"Mock scraping for {url}")
        return {
            "title": "Mock Website",
            "content": f"This is mock content scraped from {url}. It contains valuable business insights.",
            "url": url,
        }


class SearchMockTool(BaseTool):
    """Mock tool for web search."""

    async def run(self, query: str) -> List[Dict[str, Any]]:
        logger.info(f"Mock search for: {query}")
        return [
            {
                "title": f"Result 1 for {query}",
                "snippet": "Interesting business data point.",
                "url": "https://example.com/1",
            },
            {
                "title": f"Result 2 for {query}",
                "snippet": "Another relevant piece of information.",
                "url": "https://example.com/2",
            },
        ]


class CachePurgeTool(BaseTool):
    """Tool for surgical cache purging."""

    async def run(
        self, workspace_id: str, pattern: Optional[str] = None
    ) -> Dict[str, Any]:
        from redis_core.cache import CacheService

        cache = CacheService()

        if pattern:
            count = await cache.invalidate_pattern(workspace_id, pattern)
            return {
                "success": True,
                "action": "invalidate_pattern",
                "count": count,
                "pattern": pattern,
            }
        else:
            count = await cache.clear_workspace(workspace_id)
            return {"success": True, "action": "clear_workspace", "count": count}


class ToolRegistry:
    """Registry for managing and accessing agent tools."""

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._register_defaults()

    def _register_defaults(self):
        """Register default mock tools."""
        self.register_tool("ocr", OCRMockTool())
        self.register_tool("web_scraper", ScraperMockTool())
        self.register_tool("market_search", SearchMockTool())
        self.register_tool("cache_purge", CachePurgeTool())

    def register_tool(self, name: str, tool: BaseTool):
        """Register a new tool."""
        self._tools[name] = tool
        logger.info(f"Registered tool: {name}")

    def get_tool(self, name: str) -> BaseTool:
        """Get a tool by name."""
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' not found in registry")
        return self._tools[name]

    def list_tools(self) -> List[str]:
        """List all registered tools."""
        return list(self._tools.keys())


# Global registry instance
tool_registry = ToolRegistry()
