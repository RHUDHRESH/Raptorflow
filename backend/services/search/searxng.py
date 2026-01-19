import httpx
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("raptorflow.services.search.searxng")

class SearXNGClient:
    """
    Native Client for self-hosted SearXNG aggregator.
    """
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=10.0)

    async def query(self, text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Queries SearXNG and returns structured results.
        """
        url = f"{self.base_url}/search"
        params = {
            "q": text,
            "format": "json",
            "engines": "google,bing,duckduckgo"
        }
        
        try:
            response = await self.client.get(url, params=params)
            if response.status_code != 200:
                logger.error(f"SearXNG returned {response.status_code}: {response.text}")
                return []
            
            data = response.json()
            results = []
            for item in data.get("results", []):
                results.append({
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "snippet": item.get("content"),
                    "source": f"native_{item.get('engine', 'aggregator')}",
                    "confidence": 0.9
                })
                if len(results) >= limit:
                    break
            return results
            
        except httpx.TimeoutException:
            logger.warning("SearXNG query timed out")
            return []
        except Exception as e:
            logger.error(f"SearXNG query failed: {e}")
            return []

    async def close(self):
        await self.client.aclose()
