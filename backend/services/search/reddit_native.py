import asyncio
import logging
import random
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

import httpx
from services.search.fingerprint import FingerprintGenerator

logger = logging.getLogger("raptorflow.services.search.reddit")


class RedditNativeScraper:
    """
    Native Scraper for Reddit using the .json backdoor.
    No API key required. Scalable with jitter and proper headers.
    """

    def __init__(self):
        self.fingerprints = FingerprintGenerator()
        self.client = httpx.AsyncClient(
            timeout=15.0, headers=self.fingerprints.get_headers()
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

                results.append(
                    {
                        "title": post_data.get("title"),
                        "url": f"https://www.reddit.com{permalink}",
                        "snippet": post_data.get("selftext", "")[:300],
                        "source": "native_reddit",
                        "metadata": {
                            "subreddit": post_data.get("subreddit"),
                            "ups": post_data.get("ups"),
                            "num_comments": post_data.get("num_comments"),
                        },
                    }
                )

            return results

        except Exception as e:
            logger.error(f"Reddit scrape failed: {e}")
            return []

    async def get_thread(self, thread_url: str) -> Dict[str, Any]:
        """
        Fetches a single Reddit thread including comments.
        Expects a URL like https://www.reddit.com/r/subreddit/comments/id/title/
        """
        if not thread_url.endswith(".json"):
            # Ensure we use the .json endpoint
            json_url = thread_url.rstrip("/") + ".json"
        else:
            json_url = thread_url

        headers = self.fingerprints.get_headers()
        headers["Accept"] = "application/json"

        try:
            response = await self.client.get(json_url, headers=headers)
            if response.status_code != 200:
                logger.warning(f"Reddit thread fetch failed: {response.status_code}")
                return {}

            data = response.json()
            # Reddit returns a list: [post_data, comments_data]
            if not isinstance(data, list) or len(data) < 2:
                return {}

            post_info = data[0].get("data", {}).get("children", [{}])[0].get("data", {})
            comments_data = data[1].get("data", {}).get("children", [])

            comments = []
            for comment in comments_data:
                c_data = comment.get("data", {})
                if c_data.get("body"):
                    comments.append(
                        {
                            "author": c_data.get("author"),
                            "body": c_data.get("body"),
                            "ups": c_data.get("ups"),
                            "created_utc": c_data.get("created_utc"),
                        }
                    )

            return {
                "title": post_info.get("title"),
                "selftext": post_info.get("selftext"),
                "subreddit": post_info.get("subreddit"),
                "url": thread_url,
                "comments": comments[:20],  # Limit to top 20 comments for verbatims
            }

        except Exception as e:
            logger.error(f"Reddit thread fetch failed for {thread_url}: {e}")
            return {}

    async def close(self):
        await self.client.aclose()
