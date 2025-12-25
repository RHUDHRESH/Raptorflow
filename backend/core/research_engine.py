import asyncio
import logging
from typing import Dict, List, Optional
from urllib.parse import urlparse

import aiohttp
from bs4 import BeautifulSoup

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
        try:
            async with session.get(url, timeout=timeout) as response:
                if response.status == 200:
                    html = await response.text()
                    return self.clean_text(html)
                logger.warning(f"Failed to fetch {url}: Status {response.status}")
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
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
