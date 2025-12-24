import logging
from typing import Any, Dict, List

from backend.core.base_tool import BaseRaptorTool, RaptorRateLimiter
from backend.core.search_native import NativeSearch

logger = logging.getLogger("raptorflow.tools.search")


class TavilyMultiHopTool(BaseRaptorTool):
    """
    SOTA Multi-hop Search Tool (Native Replacement).
    Performs deep research using RaptorFlow's zero-cost native engine.
    """

    def __init__(self):
        self._search = NativeSearch()

    @property
    def name(self) -> str:
        return "tavily_search"

    @property
    def description(self) -> str:
        return (
            "A SOTA multi-hop search engine. Use this for deep factual research, "
            "competitive intelligence, and finding specific evidence. "
            "Input should be a detailed search query."
        )

    @RaptorRateLimiter.get_retry_decorator()
    async def _execute(
        self, query: str, search_depth: str = "advanced"
    ) -> List[Dict[str, Any]]:
        """
        Executes the search using the native engine.
        """
        logger.info(f"Executing native multi-hop search: {query}")
        results = await self._search.query(query, limit=5)
        return results


class PerplexitySearchTool(BaseRaptorTool):
    """
    SOTA Real-time Search Tool (Native Replacement).
    Uses RaptorFlow's native engine for high-velocity trend extraction.
    """

    def __init__(self):
        self._search = NativeSearch()

    @property
    def name(self) -> str:
        return "perplexity_search"

    @property
    def description(self) -> str:
        return (
            "A SOTA real-time search engine. Use this for trending news, "
            "up-to-the-minute market shifts, and verifying recent facts. "
            "Input should be a factual query."
        )

    @RaptorRateLimiter.get_retry_decorator()
    async def _execute(self, query: str) -> str:
        """
        Executes search via the native engine.
        """
        logger.info(f"Executing native real-time search: {query}")
        results = await self._search.query(query, limit=3)

        if not results:
            return "No recent data found for the query."

        # Format results as a readable string to mimic Perplexity output
        formatted = "Recent findings from native search:\n"
        for i, res in enumerate(results, 1):
            formatted += (
                f"{i}. {res['title']}: {res['snippet']} (Source: {res['url']})\n"
            )

        return formatted
