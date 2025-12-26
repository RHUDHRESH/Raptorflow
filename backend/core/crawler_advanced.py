import asyncio
import logging
import re
from typing import Dict, List, Optional

import aiohttp
from bs4 import BeautifulSoup

from core.config import get_settings
from core.renderers.playwright import PlaywrightRenderer, should_render
from tools.scraper import FirecrawlScraperTool, JinaReaderTool


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
            # Tier 1: Firecrawl (Best for structured/JS-heavy sites)
            try:
                data = await self.firecrawl._execute(url)
                if data and (data.get("markdown") or data.get("content")):
                    return {
                        "url": url,
                        "title": data.get("metadata", {}).get("title", ""),
                        "content": data.get("markdown") or data.get("content"),
                        "source": "firecrawl",
                    }
            except Exception as e:
                logging.warning(f"Firecrawl failed for {url}, trying Jina: {e}")

            # Tier 2: Jina Reader (Excellent for long-form/blogs)
            try:
                data = await self.jina._execute(url)
                if data and data.get("content"):
                    return {
                        "url": url,
                        "title": data.get("title", ""),
                        "content": data.get("content"),
                        "source": "jina",
                    }
            except Exception as e:
                logging.warning(
                    f"Jina failed for {url}, falling back to BeautifulSoup: {e}"
                )

            # Tier 3: Local BeautifulSoup Fallback (Reliable but messy)
            return await self._fallback_scrape(url)

    async def _fallback_scrape(self, url: str) -> Optional[Dict[str, str]]:
        """Classic extraction as a last resort."""
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url, timeout=15) as response:
                    if response.status != 200:
                        return None
                    html = await response.text()
                    settings = get_settings()
                    if settings.JS_RENDERING_ENABLED and should_render(html):
                        renderer = PlaywrightRenderer(
                            timeout_s=settings.JS_RENDERING_TIMEOUT_S,
                            user_agent=self.headers.get("User-Agent"),
                        )
                        try:
                            html = await renderer.render(url)
                        except Exception as e:
                            logging.warning(
                                "JS rendering failed for %s, using static HTML: %s",
                                url,
                                e,
                            )

                    soup = BeautifulSoup(html, "html.parser")
                    title = soup.title.string if soup.title else ""

                    # Clean junk
                    for junk in soup(["script", "style", "nav", "footer", "aside"]):
                        junk.decompose()

                    text = re.sub(r"\n+", "\n", soup.get_text(separator=" ")).strip()

                    return {
                        "url": url,
                        "title": title,
                        "content": text[:10000],
                        "source": "fallback_bs4",
                    }
        except Exception as e:
            logging.error(f"Fallback scrape failed for {url}: {e}")
            return None

    async def batch_crawl(self, urls: List[str]) -> List[Dict[str, str]]:
        """Parallel industrial research."""
        tasks = [self.scrape_semantic(url) for url in urls]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r]
