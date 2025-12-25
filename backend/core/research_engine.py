import asyncio
import logging
from typing import Dict, List, Optional
from urllib.parse import urlparse

import aiohttp
from bs4 import BeautifulSoup

from backend.core.crawl_cache import CrawlCache
from backend.core.search_native import NativeSearch

logger = logging.getLogger("raptorflow.research_engine")


class ResearchEngine:
    """
    Industrial-grade Web Scraper and Search Orchestrator.
    Handles rate limiting, HTML cleaning, and semantic text extraction.
    """

    def __init__(self, user_agent: str = "RaptorFlowResearchBot/2.0"):
        self.headers = {"User-Agent": user_agent}
        self.session: Optional[aiohttp.ClientSession] = None

    async def get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.headers)
        return self.session

    def clean_text(self, html: str) -> str:
        """Surgically extracts text, removing scripts, styles, and junk."""
        soup = BeautifulSoup(html, "html.parser")

        # Remove noise
        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.decompose()

        # Get text and clean whitespace
        text = soup.get_text(separator="\n")
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        return "\n".join(chunk for chunk in chunks if chunk)

    async def fetch_page(self, url: str, timeout: int = 15) -> Optional[str]:
        """Fetches and cleans a single webpage."""
        session = await self.get_session()
        cache = CrawlCache()
        cached = cache.get(url)
        if cached.entry and cached.is_fresh:
            return cached.entry.get("content")

        conditional_headers = {}
        if cached.entry:
            conditional_headers = cache.build_revalidation_headers(cached.entry)
        try:
            headers = {**self.headers, **conditional_headers} if conditional_headers else None
            async with session.get(url, timeout=timeout, headers=headers) as response:
                if response.status == 304 and cached.entry:
                    cache.touch(cached.entry)
                    return cached.entry.get("content")
                if response.status == 200:
                    html = await response.text()
                    content = self.clean_text(html)
                    cache.set(
                        url,
                        content,
                        etag=response.headers.get("ETag"),
                        last_modified=response.headers.get("Last-Modified"),
                    )
                    return content
                logger.warning(f"Failed to fetch {url}: Status {response.status}")
                if cached.entry:
                    return cached.entry.get("content")
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            if cached.entry:
                return cached.entry.get("content")
        return None

    async def batch_fetch(self, urls: List[str]) -> List[Dict[str, str]]:
        """Concurrency-optimized batch fetch."""
        tasks = [self.fetch_page(url) for url in urls]
        results = await asyncio.gather(*tasks)

        valid_results = []
        for url, content in zip(urls, results):
            if content:
                valid_results.append(
                    {
                        "url": url,
                        "domain": urlparse(url).netloc,
                        "content": content[:10000],  # Cap content for LLM safety
                    }
                )
        return valid_results


class SearchProvider:
    """Abstraction for Native zero-cost Search."""

    def __init__(self, api_key: str = ""):
        # api_key is kept for backward compatibility but unused by NativeSearch
        self._native = NativeSearch()

    async def search(self, query: str, num_results: int = 5) -> List[str]:
        """Performs native search and returns links."""
        results = await self._native.query(query, limit=num_results)
        return [res["url"] for res in results]
