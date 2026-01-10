"""
FAST SCRAPING ARCHITECTURE
Ultra-fast, optimized scraping system - no bloat, maximum speed
"""

import asyncio
import hashlib
import json
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import aiohttp


class FastScraper:
    """Ultra-fast scraper with minimal overhead"""

    def __init__(self):
        self.session = None
        self.results = []
        self.start_time = None

    async def __aenter__(self):
        # Fast session setup
        timeout = aiohttp.ClientTimeout(total=10, connect=5)
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=20)

        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={"User-Agent": "FastScraper/1.0"},
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def fetch_fast(self, url: str) -> Optional[Dict[str, Any]]:
        """Ultra-fast fetch with minimal processing"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    return {
                        "url": url,
                        "status": response.status,
                        "content_length": len(content),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "response_time": 0,  # Will be set by caller
                    }
        except Exception as e:
            print(f"Error fetching {url}: {e}")
        return None

    async def scrape_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Scrape multiple URLs with maximum concurrency"""
        self.start_time = time.time()

        # Create semaphore to limit concurrency
        semaphore = asyncio.Semaphore(20)

        async def scrape_with_semaphore(url):
            async with semaphore:
                start = time.time()
                result = await self.fetch_fast(url)
                if result:
                    result["response_time"] = time.time() - start
                return result

        # Run all requests concurrently
        tasks = [scrape_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter successful results
        self.results = [r for r in results if r and isinstance(r, dict)]

        return self.results

    def get_stats(self):
        """Get fast performance stats"""
        if not self.start_time:
            return {}

        total_time = time.time() - self.start_time
        successful = len(self.results)
        total = len(self.results)

        return {
            "total_urls": total,
            "successful": successful,
            "failed": total - successful,
            "total_time": f"{total_time:.2f}s",
            "requests_per_second": f"{successful / total_time:.1f}",
            "avg_response_time": (
                f"{sum(r['response_time'] for r in self.results) / len(self.results):.3f}s"
                if self.results
                else "0s"
            ),
        }


async def main():
    """Fast scraping demo"""

    # Test URLs
    urls = [
        "https://www.reddit.com/r/python/hot.json",
        "https://www.reddit.com/r/coffee/hot.json",
        "https://www.reddit.com/r/minnesota/hot.json",
        "https://www.reddit.com/r/twincities/hot.json",
        "https://www.reddit.com/r/technology/hot.json",
    ]

    print("🚀 FAST SCRAPING DEMO")
    print("=" * 50)

    async with FastScraper() as scraper:
        results = await scraper.scrape_urls(urls)
        stats = scraper.get_stats()

        print(f"\n📊 RESULTS:")
        print(f"   Total URLs: {stats['total_urls']}")
        print(f"   Successful: {stats['successful']}")
        print(f"   Failed: {stats['failed']}")
        print(f"   Total Time: {stats['total_time']}")
        print(f"   Speed: {stats['requests_per_second']} req/s")
        print(f"   Avg Response: {stats['avg_response_time']}")

        print(f"\n🔍 SAMPLE RESULTS:")
        for i, result in enumerate(results[:3], 1):
            print(f"   {i}. {result['url']}")
            print(f"      Status: {result['status']}")
            print(f"      Size: {result['content_length']:,} bytes")
            print(f"      Time: {result['response_time']:.3f}s")

        print(f"\n✅ FAST SCRAPING COMPLETE!")


if __name__ == "__main__":
    asyncio.run(main())
