import logging
from typing import Any, Dict

from core.tool_registry import BaseRaptorTool, RaptorRateLimiter
from core.config import get_settings

logger = logging.getLogger("raptorflow.tools.scraper")


class FirecrawlScraperTool(BaseRaptorTool):
    """
    SOTA Web Scraper Tool.
    Uses Firecrawl to surgically extract content from any URL.
    """

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.FIRECRAWL_API_KEY
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
        if not self.api_key:
            return {"error": "Firecrawl API key not configured."}
        import aiohttp

        logger.info(f"Surgical scraping via Firecrawl: {url}")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "url": url,
            "formats": ["markdown"],  # Return markdown for SOTA agent readability
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, json=payload, headers=headers) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise ValueError(f"Firecrawl failed ({resp.status}): {text}")
                data = await resp.json()
                return data.get("data", {})


class JinaReaderTool(BaseRaptorTool):
    """
    SOTA Reader Tool using Jina.ai.
    Converts any URL to LLM-friendly markdown.
    """

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.JINA_API_KEY
        self.base_url = "https://r.jina.ai/"

    @property
    def name(self) -> str:
        return "jina_reader"

    @property
    def description(self) -> str:
        return (
            "Converts any URL to clean, agent-readable markdown using Jina Reader."
            "Excellent for long-form content and documentation."
        )

    async def _execute(self, url: str) -> Dict[str, Any]:
        import aiohttp

        logger.info(f"Extracting markdown via Jina: {url}")

        headers = {"Accept": "application/json", "X-Target-Selector": "body"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        full_url = f"{self.base_url}{url}"

        async with aiohttp.ClientSession() as session:
            async with session.get(full_url, headers=headers) as resp:
                if resp.status != 200:
                    return {"error": f"Jina failed with status {resp.status}"}
                data = await resp.json()
                return {
                    "content": data.get("data", {}).get("content", ""),
                    "title": data.get("data", {}).get("title", ""),
                    "url": url,
                }
