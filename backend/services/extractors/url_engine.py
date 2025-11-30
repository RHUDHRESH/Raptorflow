import asyncio
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class URLExtractorV2:
    """
    Use tools built for the job, not DIY garbage.
    Uses trafilatura for fast extraction.
    """
    
    async def extract(self, url: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        return await asyncio.to_thread(self._extract_sync, url)
    
    def _extract_sync(self, url: str) -> Dict[str, Any]:
        try:
            from trafilatura import fetch_url, extract
            
            downloaded = fetch_url(url)
            if downloaded is None:
                return {"error": "Failed to fetch URL", "raw_text": ""}
                
            content = extract(
                downloaded,
                include_comments=False,
                include_tables=True,
                include_links=True
            )
            
            return {
                "content_type": "url",
                "raw_text": content or "",
                "structured_data": {
                    "url": url
                }
            }
        except ImportError:
            logger.error("trafilatura not installed")
            return {"error": "trafilatura not installed", "raw_text": ""}
        except Exception as e:
            logger.error(f"URL extraction failed: {e}")
            return {"error": str(e), "raw_text": ""}
