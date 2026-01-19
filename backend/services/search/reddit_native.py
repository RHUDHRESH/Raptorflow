import httpx
import logging
import asyncio
import random
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus

from backend.services.search.fingerprint import FingerprintGenerator

logger = logging.getLogger("raptorflow.services.search.reddit")

class RedditNativeScraper:
    """
    Native Scraper for Reddit using the .json backdoor.
    No API key required. Scalable with jitter and proper headers.
    """
    def __init__(self):
        self.fingerprints = FingerprintGenerator()
        self.client = httpx.AsyncClient(
            timeout=15.0,
            headers=self.fingerprints.get_headers()
        )

    async def query(self, text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Performs a Reddit search using the .json endpoint.
        """
        # Add jitter to avoid being flagged as a bot
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        # Rotate headers for each query to increase stealth
        headers = self.fingerprints.get_headers()
        headers["Accept"] = "application/json"
        
        url = f"https://www.reddit.com/search.json?q={quote_plus(text)}&limit={limit}&sort=relevance"
        
        try:
            response = await self.client.get(url, headers=headers)
            if response.status_code != 200:
                logger.warning(f"Reddit returned status {response.status_code}")
                return []
            
            data = response.json()
            results = []
            
            for post in data.get("data", {}).get("children", []):
                post_data = post.get("data", {})
                permalink = post_data.get("permalink", "")
                
                results.append({
                    "title": post_data.get("title"),
                    "url": f"https://www.reddit.com{permalink}",
                    "snippet": post_data.get("selftext", "")[:300],
                    "source": "native_reddit",
                    "metadata": {
                        "subreddit": post_data.get("subreddit"),
                        "ups": post_data.get("ups"),
                        "num_comments": post_data.get("num_comments")
                    }
                })
                
            return results
            
        except Exception as e:
            logger.error(f"Reddit scrape failed: {e}")
            return []

    async def close(self):
        await self.client.aclose()
