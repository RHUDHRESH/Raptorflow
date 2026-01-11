"""
Web scraper tool for Raptorflow agents.
"""

import asyncio
import logging
import re
from typing import Any, Dict, Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel

from .base import RaptorflowTool, ToolError, ToolResult

logger = logging.getLogger(__name__)


class WebScraperInput(BaseModel):
    """Input schema for web scraping."""

    url: str
    extract_text: bool = True
    max_length: int = 5000


class ScrapedContent(BaseModel):
    """Scraped content model."""

    url: str
    title: str
    text: str
    metadata: Dict[str, Any] = {}
    word_count: int = 0
    extraction_time_ms: int = 0


class WebScraperTool(RaptorflowTool):
    """Web scraper tool using httpx and BeautifulSoup."""

    def __init__(self):
        super().__init__(
            name="web_scraper", description="Scrape web pages and extract text content"
        )
        self.session = None
        self.user_agent = "Raptorflow Web Scraper 1.0"

    async def _arun(
        self, url: str, extract_text: bool = True, max_length: int = 5000
    ) -> ToolResult:
        """Execute web scraping."""
        try:
            # Validate URL
            if not self._validate_url(url):
                return ToolResult(success=False, error="Invalid URL provided")

            # Create HTTP session if needed
            if not self.session:
                self.session = httpx.AsyncClient(
                    timeout=30.0, headers={"User-Agent": self.user_agent}
                )

            # Scrape the page
            start_time = asyncio.get_event_loop().time()

            try:
                response = await self.session.get(url)
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                return ToolResult(
                    success=False,
                    error=f"HTTP error {e.response.status_code}: {e.response.status_code}",
                )
            except httpx.RequestError as e:
                return ToolResult(success=False, error=f"Request error: {str(e)}")

            # Parse HTML
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract content
            title = self._extract_title(soup)
            text = self._extract_text(soup, max_length) if extract_text else ""
            metadata = self._extract_metadata(soup, response)

            # Create output
            extraction_time_ms = int(
                (asyncio.get_event_loop().time() - start_time) * 1000
            )

            output = ScrapedContent(
                url=url,
                title=title,
                text=text,
                metadata=metadata,
                word_count=len(text.split()) if text else 0,
                extraction_time_ms=extraction_time_ms,
            )

            return ToolResult(success=True, data=output.model_dump())

        except Exception as e:
            return ToolResult(success=False, error=str(e))

    def _validate_url(self, url: str) -> bool:
        """Validate URL format."""
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except Exception:
            return False

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        title_tag = soup.find("title")
        if title_tag:
            return title_tag.get_text().strip()
        return ""

    def _extract_text(self, soup: BeautifulSoup, max_length: int) -> str:
        """Extract clean text from HTML."""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text from body
        body = soup.find("body")
        if not body:
            return ""

        text = body.get_text()

        # Clean up text
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove leading/trailing whitespace
        text = text.strip()

        # Truncate if needed
        if len(text) > max_length:
            text = text[:max_length].rstrip() + "..."

        return text

    def _extract_metadata(
        self, soup: BeautifulSoup, response: httpx.Response
    ) -> Dict[str, Any]:
        """Extract metadata from the page."""
        metadata = {}

        # HTTP headers
        metadata["status_code"] = response.status_code
        metadata["content_type"] = response.headers.get("content-type", "")
        metadata["content_length"] = len(response.content)

        # Meta tags
        meta_tags = soup.find_all("meta")
        for tag in meta_tags:
            name = tag.get("name") or tag.get("property")
            content = tag.get("content")
            if name and content:
                metadata[f"meta_{name}"] = content

        # Language
        html_tag = soup.find("html")
        if html_tag and html_tag.get("lang"):
            metadata["language"] = html_tag.get("lang")

        # Links
        links = soup.find_all("a", href=True)
        metadata["link_count"] = len(links)
        metadata["internal_links"] = len(
            [
                link
                for link in links
                if self._is_internal_link(link["href"], response.url)
            ]
        )
        metadata["external_links"] = metadata["link_count"] - metadata["internal_links"]

        # Images
        images = soup.find_all("img", src=True)
        metadata["image_count"] = len(images)

        return metadata

    def _is_internal_link(self, href: str, base_url: str) -> bool:
        """Check if link is internal to the same domain."""
        try:
            base_domain = urlparse(base_url).netloc
            link_domain = urlparse(urljoin(base_url, href)).netloc
            return base_domain == link_domain
        except Exception:
            return False

    async def scrape_multiple_urls(
        self, urls: list[str], extract_text: bool = True, max_length: int = 5000
    ) -> list[ToolResult]:
        """Scrape multiple URLs concurrently."""
        tasks = []
        for url in urls:
            task = self.arun(url, extract_text, max_length)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to ToolResults
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(
                    ToolResult(
                        success=False,
                        error=f"Failed to scrape {urls[i]}: {str(result)}",
                    )
                )
            else:
                processed_results.append(result)

        return processed_results

    def get_supported_formats(self) -> list[str]:
        """Get list of supported content formats."""
        return ["html", "text"]

    async def cleanup(self):
        """Clean up resources."""
        if self.session:
            await self.session.aclose()
            self.session = None
