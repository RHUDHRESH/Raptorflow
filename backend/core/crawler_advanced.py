import asyncio
import logging
import re
from typing import Dict, List, Optional

import aiohttp
from bs4 import BeautifulSoup

from backend.core.crawl_cache import CrawlCache
from backend.tools.scraper import FirecrawlScraperTool, JinaReaderTool


class AdvancedCrawler:
    """
    Industrial-grade Research Engine.
    Uses Firecrawl and Jina for surgical extraction, with BeautifulSoup fallback.
    """

    def __init__(self, max_concurrent: int = 5):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.firecrawl = FirecrawlScraperTool()
        self.jina = JinaReaderTool()
        self.headers = {"User-Agent": "RaptorFlowResearch/3.0 (Industrial grade)"}

    async def scrape_semantic(self, url: str) -> Optional[Dict[str, str]]:
        """SOTA Extraction using tiered tools."""
        async with self.semaphore:
            cache = CrawlCache()
            cached = cache.get(url)
            if cached.entry and cached.is_fresh:
                return {
                    "url": url,
                    "title": cached.entry.get("title", ""),
                    "content": cached.entry.get("content", ""),
                    "source": cached.entry.get("source", "cache"),
                }

            # Tier 1: Firecrawl (Best for structured/JS-heavy sites)
            try:
                data = await self.firecrawl._execute(url)
                if data and (data.get("markdown") or data.get("content")):
                    result = {
                        "url": url,
                        "title": data.get("metadata", {}).get("title", ""),
                        "content": data.get("markdown") or data.get("content"),
                        "source": "firecrawl",
                    }
                    cache.set(
                        url,
                        result["content"],
                        metadata={"title": result["title"], "source": result["source"]},
                    )
                    return result
            except Exception as e:
                logging.warning(f"Firecrawl failed for {url}, trying Jina: {e}")

            # Tier 2: Jina Reader (Excellent for long-form/blogs)
            try:
                data = await self.jina._execute(url)
                if data and data.get("content"):
                    result = {
                        "url": url,
                        "title": data.get("title", ""),
                        "content": data.get("content"),
                        "source": "jina",
                    }
                    cache.set(
                        url,
                        result["content"],
                        metadata={"title": result["title"], "source": result["source"]},
                    )
                    return result
            except Exception as e:
                logging.warning(
                    f"Jina failed for {url}, falling back to BeautifulSoup: {e}"
                )

            # Tier 3: Local BeautifulSoup Fallback (Reliable but messy)
            return await self._fallback_scrape(url)

    async def _fallback_scrape(self, url: str) -> Optional[Dict[str, str]]:
        """Classic extraction as a last resort."""
        cache = CrawlCache()
        cached = cache.get(url)
        if cached.entry and cached.is_fresh:
            return {
                "url": url,
                "title": cached.entry.get("title", ""),
                "content": cached.entry.get("content", ""),
                "source": cached.entry.get("source", "cache"),
            }

        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                headers = {}
                if cached.entry:
                    headers = cache.build_revalidation_headers(cached.entry)
                async with session.get(
                    url, timeout=15, headers=headers or None
                ) as response:
                    if response.status == 304 and cached.entry:
                        cache.touch(cached.entry)
                        return {
                            "url": url,
                            "title": cached.entry.get("title", ""),
                            "content": cached.entry.get("content", ""),
                            "source": cached.entry.get("source", "cache"),
                        }
                    if response.status != 200:
                        return None
                    html = await response.text()

                    soup = BeautifulSoup(html, "html.parser")
                    title = soup.title.string if soup.title else ""

                    # Clean junk
                    for junk in soup(["script", "style", "nav", "footer", "aside"]):
                        junk.decompose()

                    text = re.sub(r"\n+", "\n", soup.get_text(separator=" ")).strip()

                    result = {
                        "url": url,
                        "title": title,
                        "content": text[:10000],
                        "source": "fallback_bs4",
                    }
                    cache.set(
                        url,
                        result["content"],
                        etag=response.headers.get("ETag"),
                        last_modified=response.headers.get("Last-Modified"),
                        metadata={"title": result["title"], "source": result["source"]},
                    )
                    return result
        except Exception as e:
            logging.error(f"Fallback scrape failed for {url}: {e}")
            return None

    async def batch_crawl(self, urls: List[str]) -> List[Dict[str, str]]:
        """Parallel industrial research."""
        tasks = [self.scrape_semantic(url) for url in urls]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r]
