"""
Reddit Scraper Tool
Uses Titan Sorter multiplexer to find and scrape high-leverage verbatims.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from services.search.reddit_native import RedditNativeScraper
from services.titan.multiplexer import SearchMultiplexer

from .base import BaseTool

logger = logging.getLogger("raptorflow.tools.reddit_scraper")


class RedditScraperTool(BaseTool):
    """
    Tool for high-speed parallel scraping of Reddit verbatims.
    """

    def __init__(self):
        super().__init__(
            name="reddit_scraper",
            description="Scrapes Reddit for customer verbatims, pain points, and objections.",
        )
        self.multiplexer = SearchMultiplexer()
        self.reddit = RedditNativeScraper()

    async def _run(
        self, query: str, subreddits: Optional[List[str]] = None, limit: int = 10
    ) -> Dict[str, Any]:
        """
        Executes parallel Reddit scraping.
        """
        logger.info(f"RedditScraper: Starting research for '{query}'")

        # 1. Subreddit Discovery / Thread Discovery via Multiplexer
        # We search specifically for reddit results
        variations = await self.multiplexer.generate_variations(
            f"reddit {query}", count=3
        )

        discovery_tasks = [self.reddit.query(v, limit=5) for v in variations]
        discovery_results = await asyncio.gather(*discovery_tasks)

        # Flatten and unique URLs
        seen_urls = set()
        thread_urls = []
        for res_list in discovery_results:
            for item in res_list:
                url = item.get("url")
                if url and url not in seen_urls and "reddit.com/r/" in url:
                    thread_urls.append(url)
                    seen_urls.add(url)

        # 2. Parallel Scraping of Threads
        logger.info(
            f"RedditScraper: Found {len(thread_urls)} threads. Scraping top {limit}..."
        )

        thread_urls = thread_urls[:limit]
        scrape_tasks = [self.reddit.get_thread(url) for url in thread_urls]

        scraped_threads = await asyncio.gather(*scrape_tasks)

        # Filter out empty results
        threads = [t for t in scraped_threads if t and t.get("title")]

        return {
            "success": True,
            "query": query,
            "threads_count": len(threads),
            "threads": threads,
            "summary": f"Analyzed {len(threads)} Reddit threads for '{query}'.",
        }

    async def cleanup(self):
        await self.reddit.close()
