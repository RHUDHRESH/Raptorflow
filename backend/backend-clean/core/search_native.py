import asyncio
import logging
import random
from typing import Any, Dict, List, Optional

import httpx
from core.config import get_settings

logger = logging.getLogger("raptorflow.core.search")


class NativeSearch:
    """
    Economical Native Search Engine.
    Provides free search capabilities using Brave Search Free Tier
    with DuckDuckGo fallbacks.
    """

    def __init__(self):
        self.settings = get_settings()
        # Brave Search API Key (Free tier allows 2k/mo)
        # If not provided, it falls back to basic scrapers
        self.brave_key = getattr(self.settings, "BRAVE_SEARCH_API_KEY", None)
        self.client = httpx.AsyncClient(timeout=10.0)

    async def query(
        self, text: str, limit: int = 5, site: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Performs a web search and returns structured results.
        Supports site-specific filtering (linkedin, x, reddit).
        """
        if not text:
            return []

        search_query = text
        if site:
            if site.lower() == "linkedin":
                search_query = f"site:linkedin.com {text}"
            elif site.lower() == "x" or site.lower() == "twitter":
                search_query = f"site:x.com {text}"
            elif site.lower() == "reddit":
                search_query = f"site:reddit.com {text}"

        try:
            if self.brave_key:
                return await self._brave_search(search_query, limit)
            else:
                return await self._duckduckgo_search(search_query, limit)
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    async def _brave_search(self, text: str, limit: int) -> List[Dict[str, Any]]:
        """Queries Brave Search API."""
        headers = {"X-Subscription-Token": self.brave_key, "Accept": "application/json"}
        url = f"https://api.search.brave.com/res/v1/web/search?q={text}&count={limit}"

        response = await self.client.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            results = []
            for item in data.get("web", {}).get("results", []):
                results.append(
                    {
                        "title": item.get("title"),
                        "url": item.get("url"),
                        "snippet": item.get("description"),
                        "source": "brave",
                    }
                )
            return results

        logger.warning(
            f"Brave Search failed ({response.status_code}). Falling back to DDG."
        )
        return await self._duckduckgo_search(text, limit)

    async def _duckduckgo_search(self, text: str, limit: int) -> List[Dict[str, Any]]:
        """
        Queries DuckDuckGo using the duckduckgo_search library.
        Includes industrial jitter and a custom scraping fallback for robustness.
        """
        # Add random jitter to avoid fingerprinting (Industrial standard)
        await asyncio.sleep(random.uniform(1.0, 2.5))

        try:
            from duckduckgo_search import DDGS

            def _sync_search():
                # Randomize user agent via DDGS internals if possible or rely on library defaults
                with DDGS() as ddgs:
                    results = []
                    # Use the library's built-in text search
                    search_results = ddgs.text(text, max_results=limit)
                    if search_results:
                        for r in search_results:
                            results.append(
                                {
                                    "title": r.get("title"),
                                    "url": r.get("href"),
                                    "snippet": r.get("body"),
                                    "source": "duckduckgo",
                                }
                            )
                    return results

            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, _sync_search)

        except Exception as e:
            logger.warning(
                f"DDGS Library failed (Rate limit or structure change): {e}. Trying custom fallback."
            )
            return await self._custom_html_fallback(text, limit)

    async def _custom_html_fallback(
        self, text: str, limit: int
    ) -> List[Dict[str, Any]]:
        """
        Industrial Fallback: Directly scrapes the DDG HTML endpoint.
        Uses randomized headers and additional jitter to bypass blocks.
        """
        from bs4 import BeautifulSoup

        await asyncio.sleep(random.uniform(2.0, 4.0))  # Heavier jitter for fallback

        headers = {
            "User-Agent": random.choice(
                [
                    (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    ),
                    (
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/121.0.0.0 Safari/537.36"
                    ),
                    (
                        "Mozilla/5.0 (X11; Linux x86_64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    ),
                    (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) "
                        "Gecko/20100101 Firefox/121.0"
                    ),
                ]
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://duckduckgo.com/",
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1",
        }

        # Use the 'html' endpoint which is more stable for scraping than the JS one
        url = f"https://html.duckduckgo.com/html/?q={text}"

        try:
            # We use the existing self.client (httpx)
            response = await self.client.get(url, headers=headers)

            # If we get a 202 or 403, we are blocked/limited
            if response.status_code != 200:
                logger.error(f"DDG HTML endpoint returned {response.status_code}")
                return []

            soup = BeautifulSoup(response.text, "html.parser")
            results = []

            # Extract from the .results_links_deep container in the HTML version
            # The structure is often .result or .links_main
            items = soup.select(".result")
            if not items:
                items = soup.select(".links_main")

            for item in items[:limit]:
                title_link = item.select_one(".result__a") or item.select_one(
                    "a.result__a"
                )
                snippet = item.select_one(".result__snippet") or item.select_one(
                    ".snippet"
                )

                if title_link:
                    results.append(
                        {
                            "title": title_link.get_text(strip=True),
                            "url": title_link.get("href"),
                            "snippet": snippet.get_text(strip=True) if snippet else "",
                            "source": "ddg_html_fallback",
                        }
                    )
            return results
        except Exception as e:
            logger.error(f"Custom HTML fallback failed: {e}")
            return []

    async def close(self):
        await self.client.aclose()
