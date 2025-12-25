import asyncio
from typing import Dict, List, Optional

from backend.core.crawler_pipeline import (
    CrawlPolicy,
    ExtractStage,
    FetchStage,
    NormalizeStage,
)


class AdvancedCrawler:
    """
    Industrial-grade Research Engine with Asset Parsing.
    Uses Firecrawl and Jina for surgical extraction, with BeautifulSoup fallback.
    Enhanced with asset type detection and storage capabilities.
    """

    def __init__(self, max_concurrent: int = 5):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.extract_stage = ExtractStage()
        self.fetch_stage = FetchStage()
        self.normalize_stage = NormalizeStage()
        self.firecrawl = self.extract_stage.firecrawl
        self.jina = self.extract_stage.jina
        self.policy = CrawlPolicy(max_concurrent=max_concurrent)

    async def scrape_semantic(self, url: str) -> Optional[Dict[str, str]]:
        """SOTA Extraction using tiered tools."""
        result = await self.extract_stage.extract(
            url,
            await self._get_session(),
            self.policy,
            self.fetch_stage,
            self.normalize_stage,
            self.semaphore,
        )
        if not result:
            return None
        return {
            "url": result.url,
            "title": result.title,
            "content": result.content,
            "source": result.source,
        }

    async def _get_session(self):
        import aiohttp

        if not hasattr(self, "_session") or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={"User-Agent": self.policy.user_agent}
            )
        return self._session

    async def batch_crawl(self, urls: List[str]) -> List[Dict[str, str]]:
        """Parallel industrial research."""
        tasks = [self.scrape_semantic(url) for url in urls]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r]
