import os
import logging
from typing import Dict, Any
from backend.core.toolbelt import BaseRaptorTool, RaptorRateLimiter

logger = logging.getLogger("raptorflow.tools.scraper")

class FirecrawlScraperTool(BaseRaptorTool):
    """
    SOTA Web Scraper Tool.
    Uses Firecrawl to surgically extract content from any URL.
    """
    def __init__(self):
        self.api_key = os.getenv("FIRECRAWL_API_KEY")
        self.url = "https://api.firecrawl.dev/v1/scrape"

    @property
    def name(self) -> str:
        return "firecrawl_scraper"

    @property
    def description(self) -> str:
        return (
            "A SOTA web scraper. Use this to extract clean text and data from "
            "competitor websites, blogs, or landing pages. Input is a valid URL."
        )

    @RaptorRateLimiter.get_retry_decorator()
    async def _execute(self, url: str) -> Dict[str, Any]:
        """
        Executes surgical scraping.
        """
        import aiohttp
        logger.info(f"Surgical scraping via Firecrawl: {url}")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "url": url,
            "formats": ["markdown"] # Return markdown for SOTA agent readability
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, json=payload, headers=headers) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise ValueError(f"Firecrawl failed ({resp.status}): {text}")
                data = await resp.json()
                return data.get("data", {})
