import asyncio
import logging
import re
from typing import Any, Dict, List, Optional

import aiohttp
from bs4 import BeautifulSoup

from backend.core.config import get_settings
from backend.core.parsers import detect_asset_type, parse_asset
from backend.services.storage_service import BrandAssetManager
from backend.tools.scraper import FirecrawlScraperTool, JinaReaderTool


class AdvancedCrawler:
    """
    Industrial-grade Research Engine.
    Uses Firecrawl and Jina for surgical extraction, with BeautifulSoup fallback.
    """

    def __init__(self, max_concurrent: int = 5):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.firecrawl = FirecrawlScraperTool()
        self.jina = JinaReaderTool()
        self.headers = {"User-Agent": "RaptorFlowResearch/3.0 (Industrial grade)"}
        settings = get_settings()
        self._asset_manager = BrandAssetManager(bucket_name=settings.GCS_INGEST_BUCKET)
        self._default_tenant_id = settings.DEFAULT_TENANT_ID

    async def scrape_semantic(self, url: str) -> Optional[Dict[str, Any]]:
        """SOTA Extraction using tiered tools."""
        async with self.semaphore:
            asset_result = await self._scrape_asset(url)
            if asset_result:
                return asset_result

            # Tier 1: Firecrawl (Best for structured/JS-heavy sites)
            try:
                data = await self.firecrawl._execute(url)
                if data and (data.get("markdown") or data.get("content")):
                    return self._normalize_result(
                        url=url,
                        title=data.get("metadata", {}).get("title", ""),
                        content=data.get("markdown") or data.get("content"),
                        source="firecrawl",
                        metadata={"asset_type": "html"},
                    )
            except Exception as e:
                logging.warning(f"Firecrawl failed for {url}, trying Jina: {e}")

            # Tier 2: Jina Reader (Excellent for long-form/blogs)
            try:
                data = await self.jina._execute(url)
                if data and data.get("content"):
                    return self._normalize_result(
                        url=url,
                        title=data.get("title", ""),
                        content=data.get("content"),
                        source="jina",
                        metadata={"asset_type": "html"},
                    )
            except Exception as e:
                logging.warning(
                    f"Jina failed for {url}, falling back to BeautifulSoup: {e}"
                )

            # Tier 3: Local BeautifulSoup Fallback (Reliable but messy)
            return await self._fallback_scrape(url)

    async def _fallback_scrape(self, url: str) -> Optional[Dict[str, Any]]:
        """Classic extraction as a last resort."""
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url, timeout=15) as response:
                    if response.status != 200:
                        return None
                    html = await response.text()

                    soup = BeautifulSoup(html, "html.parser")
                    title = soup.title.string if soup.title else ""

                    # Clean junk
                    for junk in soup(["script", "style", "nav", "footer", "aside"]):
                        junk.decompose()

                    text = re.sub(r"\n+", "\n", soup.get_text(separator=" ")).strip()

                    return self._normalize_result(
                        url=url,
                        title=title,
                        content=text[:10000],
                        source="fallback_bs4",
                        metadata={"asset_type": "html"},
                    )
        except Exception as e:
            logging.error(f"Fallback scrape failed for {url}: {e}")
            return None

    async def batch_crawl(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Parallel industrial research."""
        tasks = [self.scrape_semantic(url) for url in urls]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r]

    async def _scrape_asset(self, url: str) -> Optional[Dict[str, Any]]:
        asset_type = detect_asset_type(url)
        headers = {"User-Agent": self.headers["User-Agent"]}
        content_type = None

        async with aiohttp.ClientSession(headers=headers) as session:
            try:
                async with session.head(url, timeout=10, allow_redirects=True) as resp:
                    content_type = resp.headers.get("Content-Type")
                    asset_type = asset_type or detect_asset_type(url, content_type)
            except Exception:
                content_type = None

            if not asset_type:
                return None

            try:
                async with session.get(url, timeout=20) as resp:
                    if resp.status != 200:
                        return None
                    content_type = resp.headers.get("Content-Type", content_type)
                    asset_type = asset_type or detect_asset_type(url, content_type)
                    if not asset_type:
                        return None
                    asset_bytes = await resp.read()
            except Exception as e:
                logging.warning(f"Failed to fetch asset {url}: {e}")
                return None

        try:
            parsed = parse_asset(asset_type, asset_bytes)
        except Exception as e:
            logging.warning(f"Failed to parse asset {url}: {e}")
            return None
        storage_url = await self._store_raw_asset(
            url=url,
            asset_bytes=asset_bytes,
            asset_type=asset_type,
            content_type=content_type or "application/octet-stream",
        )
        metadata = {
            "asset_type": asset_type,
            "storage_url": storage_url,
            **parsed.metadata,
        }
        title = parsed.title or metadata.get("document_title", "") or ""
        return self._normalize_result(
            url=url,
            title=title,
            content=parsed.text,
            source=f"asset_{asset_type}",
            metadata=metadata,
        )

    async def _store_raw_asset(
        self,
        url: str,
        asset_bytes: bytes,
        asset_type: str,
        content_type: str,
    ) -> Optional[str]:
        filename = url.split("/")[-1] or f"asset.{asset_type}"
        if "." not in filename:
            filename = f"{filename}.{asset_type}"
        try:
            return await asyncio.to_thread(
                self._asset_manager.upload_raw_asset,
                file_content=asset_bytes,
                filename=filename,
                content_type=content_type,
                tenant_id=self._default_tenant_id,
            )
        except Exception as e:
            logging.warning(f"Failed to store raw asset {url}: {e}")
            return None

    def _normalize_result(
        self,
        url: str,
        title: str,
        content: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return {
            "url": url,
            "title": title,
            "content": content,
            "source": source,
            "metadata": metadata or {},
        }
