import logging
from typing import Any

from core.search_native import NativeSearch
from core.tool_registry import BaseRaptorTool, RaptorRateLimiter

logger = logging.getLogger("raptorflow.tools.search")


class RaptorSearchTool(BaseRaptorTool):
    """
    RaptorFlow Unified Search Tool.
    Consolidates multiple search providers into a single industrial-grade interface.
    Uses NativeSearch (Brave/DuckDuckGo) for high-velocity, low-cost research.
    """

    def __init__(self):
        self._search = NativeSearch()

    @property
    def name(self) -> str:
        return "raptor_search"

    @property
    def description(self) -> str:
        return (
            "A unified industrial search engine. Use this for all web research, "
            "competitive intelligence, trend extraction, and fact-checking. "
            "Input is a search query. Supports depth and limit parameters."
        )

    @RaptorRateLimiter.get_retry_decorator()
    async def _execute(
        self, query: str, limit: int = 5, format: str = "structured"
    ) -> Any:
        """
        Executes search via the native engine.
        """
        logger.info(f"Executing RaptorSearch for query: {query}")
        results = await self._search.query(query, limit=limit)

        if format == "text":
            if not results:
                return "No findings for this query."

            formatted = f"Search results for: {query}\n"
            for i, res in enumerate(results, 1):
                formatted += (
                    f"{i}. {res['title']} - {res['url']}\n   {res['snippet']}\n"
                )
            return formatted

        return results


# Legacy Aliases for Backward Compatibility
class TavilyMultiHopTool(RaptorSearchTool):
    @property
    def name(self) -> str:
        return "tavily_search"


class PerplexitySearchTool(RaptorSearchTool):
    @property
    def name(self) -> str:
        return "perplexity_search"

    async def _execute(self, query: str) -> str:
        # Perplexity-style always returns text
        return await super()._execute(query, limit=3, format="text")
