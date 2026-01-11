"""
Web search tool for Raptorflow agents.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel

from .base import RaptorflowTool, ToolError, ToolResult

logger = logging.getLogger(__name__)


class WebSearchInput(BaseModel):
    """Input schema for web search."""

    query: str
    max_results: int = 10
    engines: List[str] = ["google", "bing"]


class SearchResult(BaseModel):
    """Individual search result."""

    title: str
    url: str
    snippet: str
    engine: str
    relevance_score: float = 0.0


class WebSearchOutput(BaseModel):
    """Output schema for web search."""

    query: str
    results: List[SearchResult]
    total_results: int
    search_time_ms: int


class WebSearchTool(RaptorflowTool):
    """Web search tool using FreeWebSearchEngine."""

    def __init__(self):
        super().__init__(
            name="web_search",
            description="Search the web for information using multiple search engines",
        )
        self.search_engines = {
            "google": "https://www.google.com/search",
            "bing": "https://www.bing.com/search",
            "duckduckgo": "https://duckduckgo.com/html",
        }

    async def _arun(
        self, query: str, max_results: int = 10, engines: List[str] = None
    ) -> ToolResult:
        """Execute web search."""
        if engines is None:
            engines = ["google"]

        try:
            # Validate inputs
            if not query or len(query.strip()) < 3:
                return ToolResult(
                    success=False, error="Query must be at least 3 characters long"
                )

            # Search across engines
            all_results = []
            search_start = asyncio.get_event_loop().time()

            for engine in engines:
                if engine in self.search_engines:
                    results = await self._search_engine(
                        engine, query, max_results // len(engines)
                    )
                    all_results.extend(results)

            # Sort by relevance and limit
            all_results.sort(key=lambda x: x.relevance_score, reverse=True)
            final_results = all_results[:max_results]

            # Create output
            output = WebSearchOutput(
                query=query,
                results=final_results,
                total_results=len(final_results),
                search_time_ms=int(
                    (asyncio.get_event_loop().time() - search_start) * 1000
                ),
            )

            return ToolResult(success=True, data=output.model_dump())

        except Exception as e:
            return ToolResult(success=False, error=str(e))

    async def _search_engine(
        self, engine: str, query: str, max_results: int
    ) -> List[SearchResult]:
        """Search a specific engine."""
        try:
            if engine == "google":
                return await self._search_google(query, max_results)
            elif engine == "bing":
                return await self._search_bing(query, max_results)
            elif engine == "duckduckgo":
                return await self._search_duckduckgo(query, max_results)
            else:
                logger.warning(f"Unknown search engine: {engine}")
                return []
        except Exception as e:
            logger.error(f"Error searching {engine}: {e}")
            return []

    async def _search_google(self, query: str, max_results: int) -> List[SearchResult]:
        """Search Google (mock implementation for now)."""
        # In a real implementation, this would use Google Custom Search API
        # For now, return mock results to demonstrate the structure

        mock_results = [
            SearchResult(
                title=f"Google result for: {query}",
                url="https://example.com/google-result",
                snippet=f"This is a mock search result for the query: {query}",
                engine="google",
                relevance_score=0.9,
            ),
            SearchResult(
                title=f"Another Google result for: {query}",
                url="https://example.com/another-google-result",
                snippet=f"Additional information about {query}",
                engine="google",
                relevance_score=0.8,
            ),
        ]

        return mock_results[:max_results]

    async def _search_bing(self, query: str, max_results: int) -> List[SearchResult]:
        """Search Bing (mock implementation for now)."""
        mock_results = [
            SearchResult(
                title=f"Bing result for: {query}",
                url="https://example.com/bing-result",
                snippet=f"Bing search result for: {query}",
                engine="bing",
                relevance_score=0.85,
            )
        ]

        return mock_results[:max_results]

    async def _search_duckduckgo(
        self, query: str, max_results: int
    ) -> List[SearchResult]:
        """Search DuckDuckGo (mock implementation for now)."""
        mock_results = [
            SearchResult(
                title=f"DuckDuckGo result for: {query}",
                url="https://example.com/ddg-result",
                snippet=f"Privacy-focused search result for: {query}",
                engine="duckduckgo",
                relevance_score=0.75,
            )
        ]

        return mock_results[:max_results]

    def get_available_engines(self) -> List[str]:
        """Get list of available search engines."""
        return list(self.search_engines.keys())

    async def validate_query(self, query: str) -> bool:
        """Validate search query."""
        if not query or len(query.strip()) < 3:
            return False

        # Check for potentially problematic queries
        problematic_terms = ["site:", "inurl:", "filetype:", "intitle:"]
        query_lower = query.lower()

        for term in problematic_terms:
            if term in query_lower:
                logger.warning(f"Advanced search operator detected: {term}")

        return True
