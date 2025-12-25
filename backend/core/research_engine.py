import logging
from typing import Dict, List, Optional

from backend.core.crawler_pipeline import CrawlerPipeline, CrawlPolicy, NormalizeStage
from backend.core.search_native import NativeSearch

logger = logging.getLogger("raptorflow.research_engine")


class ResearchEngine:
    """
    Industrial-grade Web Scraper and Search Orchestrator.
    Handles rate limiting, HTML cleaning, and semantic text extraction.
    """

    def __init__(self, user_agent: str = "RaptorFlowResearchBot/2.0"):
        self._policy = CrawlPolicy(user_agent=user_agent)
        self._pipeline = CrawlerPipeline()
        self._normalizer = NormalizeStage()

    def clean_text(self, html: str) -> str:
        """Deprecated: use CrawlerPipeline NormalizeStage instead."""
        return self._normalizer.normalize_html(html, self._policy).content

    async def fetch_page(self, url: str, timeout: int = 15) -> Optional[str]:
        """Deprecated: use CrawlerPipeline.fetch instead."""
        policy = CrawlPolicy(
            max_concurrent=self._policy.max_concurrent,
            timeout=timeout,
            max_content_length=self._policy.max_content_length,
            user_agent=self._policy.user_agent,
        )
        results = await self._pipeline.fetch([url], policy)
        if not results:
            return None
        return results[0].content

    async def batch_fetch(self, urls: List[str]) -> List[Dict[str, str]]:
        """Compatibility shim for legacy callers."""
        logger.warning("ResearchEngine.batch_fetch is deprecated; use CrawlerPipeline.")
        results = await self._pipeline.fetch(urls, self._policy)
        return [
            {"url": result.url, "domain": result.domain, "content": result.content}
            for result in results
        ]


class SearchProvider:
    """Abstraction for Native zero-cost Search."""

    def __init__(self, api_key: str = ""):
        # api_key is kept for backward compatibility but unused by NativeSearch
        self._native = NativeSearch()

    async def search(self, query: str, num_results: int = 5) -> List[str]:
        """Performs native search and returns links."""
        results = await self._native.query(query, limit=num_results)
        return [res["url"] for res in results]
