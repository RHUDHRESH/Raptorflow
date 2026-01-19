"""
Raptorflow Web Search Machine
=============================

Sole source of web intelligence for the Raptorflow AI system.
Powered by the Raptorflow Native Search Cluster.
No external API dependencies.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from .base import WebTool, ToolResult, ToolCategory
from backend.services.search.orchestrator import SOTASearchOrchestrator

logger = logging.getLogger(__name__)

class WebSearchTool(WebTool):
    """
    High-throughput Web Search Machine implementation.
    Aggregates native search results with zero external API cost.
    """

    NAME = "web_search"
    DESCRIPTION = "Execute high-accuracy web search via the native Raptorflow cluster."
    CATEGORY = ToolCategory.WEB_TOOLS
    VERSION = "2.0.0"
    AUTHOR = "Raptorflow Machine Division"

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self._orchestrator = None

    def _get_orchestrator(self) -> SOTASearchOrchestrator:
        """Lazy init for the SOTA orchestrator."""
        if self._orchestrator is None:
            self._orchestrator = SOTASearchOrchestrator()
        return self._orchestrator

    async def _execute(self, **kwargs) -> Dict[str, Any]:
        """Execute search through the native machine."""
        query = kwargs.get("query", "")
        limit = min(kwargs.get("num_results", 10), 50)

        if not query:
            return {
                "success": False,
                "error": "Empty search query"
            }

        logger.info(f"Machine Search: '{query}' (limit={limit})")
        
        orchestrator = self._get_orchestrator()
        results = await orchestrator.query(query, limit=limit)

        return {
            "query": query,
            "results": results,
            "total_results": len(results),
            "engine": "Raptorflow Native Cluster",
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "machine_id": "RF-SEARCH-SOTA-01",
                "processed_at": datetime.now().isoformat()
            }
        }

    async def search_multiple_engines(self, query: str, **kwargs) -> Dict[str, Any]:
        """Compatibility method for multi-engine calls - redirects to native cluster."""
        return await self._execute(query=query, **kwargs)

    async def cleanup(self):
        """Cleanup orchestrator resources."""
        if self._orchestrator:
            await self._orchestrator.close()

# Export for dynamic loading
__all__ = ["WebSearchTool"]