"""
SOTA Web Search Tool for Raptorflow
===================================

This tool utilizes the self-hosted native search cluster (SearXNG aggregator + IP rotation)
as the sole source of web intelligence. No external paid APIs (Brave, Google, Serper) are used.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

from pydantic import BaseModel
from .base import RaptorflowTool, ToolResult
from backend.services.search.orchestrator import SOTASearchOrchestrator

logger = logging.getLogger(__name__)

class SearchResult(BaseModel):
    """Individual search result from the native cluster."""
    title: str
    url: str
    snippet: str
    source: str
    relevance_score: float = 0.8
    position: int

class WebSearchTool(RaptorflowTool):
    """
    Industrial-grade Web Search tool powered by the Raptorflow Native Search Machine.
    Aggregates results from 70+ engines through a self-hosted cluster.
    """

    def __init__(self):
        super().__init__(
            name="web_search",
            description="Perform high-accuracy web search using the Raptorflow native cluster.",
        )
        self._orchestrator = None
        self.metrics = {
            "total_searches": 0,
            "failed_searches": 0,
            "total_latency_ms": 0,
            "avg_latency_ms": 0
        }

    def _get_orchestrator(self) -> SOTASearchOrchestrator:
        """Lazy initialization of the SOTA orchestrator."""
        if self._orchestrator is None:
            self._orchestrator = SOTASearchOrchestrator()
        return self._orchestrator

    async def _arun(
        self, query: str, max_results: int = 10, **kwargs
    ) -> ToolResult:
        """Execute search via the SOTA orchestrator machine."""
        start_time = time.time()
        self.metrics["total_searches"] += 1
        
        try:
            # 1. Validation
            if not query or len(query.strip()) < 3:
                return ToolResult(
                    success=False, 
                    error="Search query too short. Minimum 3 characters."
                )

            # 2. Native Cluster Execution
            orchestrator = self._get_orchestrator()
            raw_results = await orchestrator.query(query, limit=max_results)
            
            # 3. Processing and Normalization
            results = []
            for idx, res in enumerate(raw_results):
                results.append({
                    "title": res.get("title", "Untitled"),
                    "url": res.get("url", ""),
                    "snippet": res.get("snippet", ""),
                    "source": res.get("source", "native_cluster"),
                    "relevance_score": res.get("confidence", 0.85),
                    "position": idx + 1
                })

            latency_ms = int((time.time() - start_time) * 1000)
            self.metrics["total_latency_ms"] += latency_ms
            self.metrics["avg_latency_ms"] = self.metrics["total_latency_ms"] // self.metrics["total_searches"]

            output = {
                "query": query,
                "results": results,
                "total_results": len(results),
                "latency_ms": latency_ms,
                "engine": "Raptorflow SOTA Native Cluster"
            }

            logger.info(f"Native Search Machine: '{query}' returned {len(results)} results in {latency_ms}ms")

            return ToolResult(
                success=True,
                data=output,
                latency_ms=latency_ms
            )

        except Exception as e:
            self.metrics["failed_searches"] += 1
            logger.error(f"Native Search Machine Failure: {str(e)}")
            return ToolResult(
                success=False,
                error=f"Search machine error: {str(e)}",
                latency_ms=int((time.time() - start_time) * 1000)
            )

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get machine performance metrics."""
        return self.metrics
