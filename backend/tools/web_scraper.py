"""
Raptorflow Web Scraper Tool
=============================

Comprehensive web scraping tool for the Raptorflow AI agent system.
Supports multiple scraping methods, content extraction, and data processing.

Features:
- Multiple scraping methods (HTTP requests, browser automation)
- Content extraction and parsing
- JavaScript rendering support
- Rate limiting and politeness policies
- Data cleaning and normalization
- Export to multiple formats
- Proxy and user agent rotation
- Error handling and retry logic
- Scraping session management
"""

import asyncio
import json
import re
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union
from urllib.parse import urljoin, urlparse

# External imports
import httpx
import structlog
from bs4 import BeautifulSoup, SoupStrainer
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ..config import settings

# Local imports
from .base import ToolError, ToolResult, ToolStatus, ToolTimeoutError, WebTool

logger = structlog.get_logger(__name__)


class ScrapingMethod(str, Enum):
    """Scraping methods."""

    HTTP = "http"
    SELENIUM = "selenium"
    PLAYWRIGHT = "playwright"
    CUSTOM = "custom"


class ContentType(str, Enum):
    """Content types to extract."""

    TEXT = "text"
    HTML = "html"
    LINKS = "links"
    IMAGES = "images"
    TABLES = "tables"
    FORMS = "forms"
    METADATA = "metadata"
    CUSTOM = "custom"


class OutputFormat(str, Enum):
    """Output formats."""

    JSON = "json"
    CSV = "csv"
    XML = "xml"
    TXT = "txt"
    XLSX = "xlsx"
    HTML = "html"


@dataclass
class ScrapingRequest:
    """Scraping request configuration."""

    url: str
    method: ScrapingMethod = ScrapingMethod.HTTP
    content_types: List[ContentType] = field(default_factory=lambda: [ContentType.TEXT])
    output_format: OutputFormat = OutputFormat.JSON
    timeout: int = 30
    max_pages: int = 1
    follow_links: bool = False
    link_selector: str = "a[href]"
    wait_for: Optional[str] = None
    wait_timeout: int = 10
    user_agent: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    cookies: Dict[str, str] = field(default_factory=dict)
    proxy: Optional[str] = None
    javascript: bool = False
    screenshots: bool = False
    respect_robots: bool = True
    delay_between_requests: float = 1.0
    max_retries: int = 3
    custom_selectors: Dict[str, str] = field(default_factory=dict)
    exclude_selectors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScrapedContent:
    """Scraped content data."""

    url: str
    content_type: ContentType
    data: Any
    timestamp: datetime = field(default_factory=datetime.now)
    size: int = 0
    encoding: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "url": self.url,
            "content_type": self.content_type.value,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "size": self.size,
            "encoding": self.encoding,
            "metadata": self.metadata,
        }


@dataclass
class ScrapingResult:
    """Complete scraping result."""

    request: ScrapingRequest
    content: List[ScrapedContent]
    urls_scraped: List[str]
    urls_failed: List[str]
    total_pages: int
    scraping_time: float
    scraping_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "request": self.request.__dict__,
            "content": [content.to_dict() for content in self.content],
            "urls_scraped": self.urls_scraped,
            "urls_failed": self.urls_failed,
            "total_pages": self.total_pages,
            "scraping_time": self.scraping_time,
            "scraping_id": self.scraping_id,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


class HTTPScraper:
    """HTTP-based scraper using requests and BeautifulSoup."""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
        self.session = httpx.AsyncClient(timeout=timeout)

    async def scrape(self, request: ScrapingRequest) -> ScrapingResult:
        """Scrape using HTTP requests."""
        start_time = time.time()
        scraping_id = str(uuid.uuid4())

        content = []
        urls_scraped = []
        urls_failed = []
        pages_scraped = 0

        try:
            # Prepare headers
            headers = {
                "User-Agent": request.user_agent or "Raptorflow-Scraper/1.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            }
            headers.update(request.headers)

            # Scrape initial page
            page_content = await self._scrape_page(request.url, request, headers)
            if page_content:
                content.append(page_content)
                urls_scraped.append(request.url)
                pages_scraped += 1

            # Follow links if requested
            if request.follow_links and pages_scraped < request.max_pages:
                links = self._extract_links(page_content.data, request.link_selector)

                for link in links[: request.max_pages - pages_scraped]:
                    try:
                        # Add delay between requests
                        await asyncio.sleep(request.delay_between_requests)

                        link_content = await self._scrape_page(link, request, headers)
                        if link_content:
                            content.append(link_content)
                            urls_scraped.append(link)
                            pages_scraped += 1

                    except Exception as e:
                        urls_failed.append(link)
                        logger.warning(f"Failed to scrape link: {link}", error=str(e))

            scraping_time = time.time() - start_time

            return ScrapingResult(
                request=request,
                content=content,
                urls_scraped=urls_scraped,
                urls_failed=urls_failed,
                total_pages=pages_scraped,
                scraping_time=scraping_time,
                scraping_id=scraping_id,
                metadata={
                    "method": "http",
                },
            )

        except Exception as e:
            logger.error("HTTP scraping failed", error=str(e), url=request.url)
            raise ToolError(f"HTTP scraping failed: {e}", tool_name="WebScraperTool")

    async def _scrape_page(
        self, url: str, request: ScrapingRequest, headers: Dict[str, str]
    ) -> Optional[ScrapedContent]:
        """Scrape a single page."""
        try:
            # Make HTTP request
            response = await self.client.get(url, headers=headers)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract content based on requested types
            extracted_content = {}

            for content_type in request.content_types:
                if content_type == ContentType.TEXT:
                    extracted_content["text"] = soup.get_text(strip=True)
                elif content_type == ContentType.HTML:
                    extracted_content["html"] = response.text
                elif content_type == ContentType.LINKS:
                    extracted_content["links"] = self._extract_links(
                        soup, request.link_selector
                    )
                elif content_type == ContentType.IMAGES:
                    extracted_content["images"] = self._extract_images(soup)
                elif content_type == ContentType.TABLES:
                    extracted_content["tables"] = self._extract_tables(soup)
                elif content_type == ContentType.FORMS:
                    extracted_content["forms"] = self._extract_forms(soup)
                elif content_type == ContentType.METADATA:
                    extracted_content["metadata"] = self._extract_metadata(
                        soup, response
                    )
                elif content_type == ContentType.CUSTOM:
                    for selector_name, selector in request.custom_selectors.items():
                        extracted_content[selector_name] = self._extract_custom(
                            soup, selector
                        )

            # Create scraped content
            scraped_content = ScrapedContent(
                url=url,
                content_type=(
                    ContentType.CUSTOM
                    if len(request.content_types) > 1
                    else request.content_types[0]
                ),
                data=extracted_content,
                size=len(response.text),
                encoding=response.encoding,
                metadata={
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "content_type": response.headers.get("content-type"),
                },
            )

            return scraped_content

        except Exception as e:
            logger.error("Failed to scrape page", error=str(e), url=url)
            return None

    def _extract_links(
        self, soup: BeautifulSoup, selector: str = "a[href]"
    ) -> List[str]:
        """Extract links from page."""
        links = []
        for link in soup.select(selector):
            href = link.get("href")
            if href:
                # Convert relative URLs to absolute
                if href.startswith("/"):
                    base_url = soup.find("base")
                    if base_url:
                        base_href = base_url.get("href", "")
                    else:
                        # Assume same domain
                        base_href = f"{soup.find('meta', property='og:url') or soup.find('link', rel='canonical') or ''}"
                    links.append(urljoin(base_href, href))
                elif href.startswith("http"):
                    links.append(href)
        return links

    def _extract_images(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract image information."""
        images = []
        for img in soup.find_all("img"):
            images.append(
                {
                    "src": img.get("src", ""),
                    "alt": img.get("alt", ""),
                    "title": img.get("title", ""),
                    "width": img.get("width", ""),
                    "height": img.get("height", ""),
                }
            )
        return images

    def _extract_tables(self, soup: BeautifulSoup) -> List[List[List[str]]]:
        """Extract table data."""
        tables = []
        for table in soup.find_all("table"):
            table_data = []
            for row in table.find_all("tr"):
                row_data = []
                for cell in row.find_all(["td", "th"]):
                    row_data.append(cell.get_text(strip=True))
                if row_data:
                    table_data.append(row_data)
            if table_data:
                tables.append(table_data)
        return tables

    def _extract_forms(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract form information."""
        forms = []
        for form in soup.find_all("form"):
            form_data = {
                "action": form.get("action", ""),
                "method": form.get("method", "GET"),
                "fields": [],
            }

            for field in form.find_all(["input", "select", "textarea"]):
                field_data = {
                    "name": field.get("name", ""),
                    "type": field.get("type", field.name),
                    "value": field.get("value", ""),
                    "placeholder": field.get("placeholder", ""),
                    "required": field.has_attr("required"),
                }
                form_data["fields"].append(field_data)

            forms.append(form_data)
        return forms

    def _extract_metadata(
        self, soup: BeautifulSoup, response: httpx.Response
    ) -> Dict[str, Any]:
        """Extract page metadata."""
        metadata = {
            "title": soup.title.string.strip() if soup.title else "",
            "description": "",
            "keywords": "",
            "author": "",
            "language": "",
        }

        # Meta tags
        for meta in soup.find_all("meta"):
            name = meta.get("name", "").lower()
            property = meta.get("property", "").lower()
            content = meta.get("content", "")

            if name == "description":
                metadata["description"] = content
            elif name == "keywords":
                metadata["keywords"] = content
            elif name == "author":
                metadata["author"] = content
            elif name == "language":
                metadata["language"] = content
            elif property == "og:title":
                metadata["og_title"] = content
            elif property == "og:description":
                metadata["og_description"] = content
            elif property == "og:image":
                metadata["og_image"] = content

        return metadata

    def _extract_custom(self, soup: BeautifulSoup, selector: str) -> List[str]:
        """Extract custom selector content."""
        elements = soup.select(selector)
        return [elem.get_text(strip=True) for elem in elements]

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
        await self.session.aclose()


class SeleniumScraper:
    """Selenium-based scraper for JavaScript rendering."""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.driver = None
        self._initialized = False

    async def initialize(self):
        """Initialize Selenium driver."""
        if self._initialized:
            return

        try:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")

            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(self.timeout)
            self._initialized = True

            logger.info("Selenium driver initialized")

        except Exception as e:
            logger.error("Failed to initialize Selenium driver", error=str(e))
            raise ToolError(
                f"Selenium initialization failed: {e}", tool_name="WebScraperTool"
            )

    async def scrape(self, request: ScrapingRequest) -> ScrapingResult:
        """Scrape using Selenium."""
        await self.initialize()

        start_time = time.time()
        scraping_id = str(uuid.uuid4())

        content = []
        urls_scraped = []
        urls_failed = []
        pages_scraped = 0

        try:
            # Scrape initial page
            page_content = await self._scrape_page(request.url, request)
            if page_content:
                content.append(page_content)
                urls_scraped.append(request.url)
                pages_scraped += 1

            # Follow links if requested
            if request.follow_links and pages_scraped < request.max_pages:
                links = self._extract_links(page_content.data, request.link_selector)

                for link in links[: request.max_pages - pages_scraped]:
                    try:
                        # Add delay between requests
                        await asyncio.sleep(request.delay_between_requests)

                        link_content = await self._scrape_page(link, request)
                        if link_content:
                            content.append(link_content)
                            urls_scraped.append(link)
                            pages_scraped += 1

                    except Exception as e:
                        urls_failed.append(link)
                        logger.warning(f"Failed to scrape link: {link}", error=str(e))

            scraping_time = time.time() - start_time

            return ScrapingResult(
                request=request,
                content=content,
                urls_scraped=urls_scraped,
                urls_failed=urls_failed,
                total_pages=pages_scraped,
                scraping_time=scraping_time,
                scraping_id=scraping_id,
                metadata={
                    "method": "selenium",
                    "screenshots": request.screenshots,
                },
            )

        except Exception as e:
            logger.error("Selenium scraping failed", error=str(e), url=request.url)
            raise ToolError(
                f"Selenium scraping failed: {e}", tool_name="WebScraperTool"
            )

    async def _scrape_page(
        self, url: str, request: ScrapingRequest
    ) -> Optional[ScrapedContent]:
        """Scrape a single page with Selenium."""
        try:
            # Navigate to page
            self.driver.get(url)

            # Wait for page to load
            if request.wait_for:
                try:
                    WebDriverWait(self.driver, request.wait_timeout).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, request.wait_for)
                        )
                    )
                except TimeoutException:
                    logger.warning(f"Wait condition not met: {request.wait_for}")

            # Wait for JavaScript to execute
            if request.javascript:
                await asyncio.sleep(2)

            # Get page source
            page_source = self.driver.page_source

            # Parse HTML
            soup = BeautifulSoup(page_source, "html.parser")

            # Extract content (similar to HTTP scraper)
            extracted_content = {}

            for content_type in request.content_types:
                if content_type == ContentType.TEXT:
                    extracted_content["text"] = soup.get_text(strip=True)
                elif content_type == ContentType.HTML:
                    extracted_content["html"] = page_source
                elif content_type == ContentType.LINKS:
                    extracted_content["links"] = self._extract_links(
                        soup, request.link_selector
                    )
                elif content_type == ContentType.IMAGES:
                    extracted_content["images"] = self._extract_images(soup)
                elif content_type == ContentType.TABLES:
                    extracted_content["tables"] = self._extract_tables(soup)
                elif content_type == ContentType.FORMS:
                    extracted_content["forms"] = self._extract_forms(soup)
                elif content_type == ContentType.METADATA:
                    extracted_content["metadata"] = self._extract_metadata(soup)
                elif content_type == ContentType.CUSTOM:
                    for selector_name, selector in request.custom_selectors.items():
                        extracted_content[selector_name] = self._extract_custom(
                            soup, selector
                        )

            # Take screenshot if requested
            screenshot_data = None
            if request.screenshots:
                try:
                    screenshot_data = self.driver.get_screenshot_as_base64()
                except Exception as e:
                    logger.warning("Failed to take screenshot", error=str(e))

            # Create scraped content
            scraped_content = ScrapedContent(
                url=url,
                content_type=(
                    ContentType.CUSTOM
                    if len(request.content_types) > 1
                    else request.content_types[0]
                ),
                data=extracted_content,
                size=len(page_source),
                metadata={
                    "screenshot": screenshot_data,
                    "current_url": self.driver.current_url,
                    "title": self.driver.title,
                },
            )

            return scraped_content

        except Exception as e:
            logger.error("Failed to scrape page with Selenium", error=str(e), url=url)
            return None

    def _extract_links(
        self, soup: BeautifulSoup, selector: str = "a[href]"
    ) -> List[str]:
        """Extract links from page."""
        links = []
        for link in soup.select(selector):
            href = link.get("href")
            if href:
                links.append(href)
        return links

    def _extract_images(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract image information."""
        images = []
        for img in soup.find_all("img"):
            images.append(
                {
                    "src": img.get("src", ""),
                    "alt": img.get("alt", ""),
                    "title": img.get("title", ""),
                    "width": img.get("width", ""),
                    "height": img.get("height", ""),
                }
            )
        return images

    def _extract_tables(self, soup: BeautifulSoup) -> List[List[List[str]]]:
        """Extract table data."""
        tables = []
        for table in soup.find_all("table"):
            table_data = []
            for row in table.find_all("tr"):
                row_data = []
                for cell in row.find_all(["td", "th"]):
                    row_data.append(cell.get_text(strip=True))
                if row_data:
                    table_data.append(row_data)
            if table_data:
                tables.append(table_data)
        return tables

    def _extract_forms(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract form information."""
        forms = []
        for form in soup.find_all("form"):
            form_data = {
                "action": form.get("action", ""),
                "method": form.get("method", "GET"),
                "fields": [],
            }

            for field in form.find_all(["input", "select", "textarea"]):
                field_data = {
                    "name": field.get("name", ""),
                    "type": field.get("type", field.name),
                    "value": field.get("value", ""),
                    "placeholder": field.get("placeholder", ""),
                    "required": field.has_attr("required"),
                }
                form_data["fields"].append(field_data)

            forms.append(form_data)
        return forms

    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract page metadata."""
        metadata = {
            "title": soup.title.string.strip() if soup.title else "",
            "description": "",
            "keywords": "",
            "author": "",
            "language": "",
        }

        # Meta tags
        for meta in soup.find_all("meta"):
            name = meta.get("name", "").lower()
            property = meta.get("property", "").lower()
            content = meta.get("content", "")

            if name == "description":
                metadata["description"] = content
            elif name == "keywords":
                metadata["keywords"] = content
            elif name == "author":
                metadata["author"] = content
            elif name == "language":
                metadata["language"] = content
            elif property == "og:title":
                metadata["og_title"] = content
            elif property == "og:description":
                metadata["og_description"] = content
            elif property == "og:image":
                metadata["og_image"] = content

        return metadata

    def _extract_custom(self, soup: BeautifulSoup, selector: str) -> List[str]:
        """Extract custom selector content."""
        elements = soup.select(selector)
        return [elem.get_text(strip=True) for elem in elements]

    async def close(self):
        """Close Selenium driver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
        self._initialized = False


class WebScraperTool(WebTool):
    """Web scraper tool implementation."""

    NAME = "web_scraper"
    DESCRIPTION = "Scrape web pages and extract content"
    CATEGORY = ToolCategory.WEB_TOOLS
    VERSION = "1.0.0"
    AUTHOR = "Raptorflow Team"

    REQUIRED_CONFIG = []
    OPTIONAL_CONFIG = [
        "default_method",
        "timeout",
        "max_pages",
        "delay_between_requests",
        "respect_robots",
        "user_agent",
        "selenium_driver_path",
    ]

    CAPABILITIES = [
        "web_scraping",
        "content_extraction",
        "javascript_rendering",
        "multi_page_scraping",
        "data_export",
    ]

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)

        # Scraping methods
        self.http_scraper = HTTPScraper(timeout=self.timeout)
        self.selenium_scraper = SeleniumScraper(timeout=self.timeout)

        # Default settings
        self.default_method = ScrapingMethod(self.config.get("default_method", "http"))
        self.max_pages = self.config.get("max_pages", 10)
        self.delay_between_requests = self.config.get("delay_between_requests", 1.0)
        self.respect_robots = self.config.get("respect_robots", True)

    async def _on_initialize(self):
        """Initialize the tool."""
        # Validate scraping method
        if self.default_method == ScrapingMethod.SELENIUM:
            await self.selenium_scraper.initialize()

    async def _execute(self, **kwargs) -> Dict[str, Any]:
        """Execute web scraping."""
        # Parse scraping request
        request = self._parse_scraping_request(kwargs)

        # Validate URL
        if not self._is_valid_url(request.url):
            raise ToolValidationError(
                f"Invalid URL: {request.url}", tool_name=self.NAME
            )

        # Check robots.txt if respect_robots is enabled
        if self.respect_robots:
            if not await self._check_robots_txt(request.url):
                raise ToolValidationError(
                    f"Scraping not allowed by robots.txt: {request.url}",
                    tool_name=self.NAME,
                )

        # Select scraper method
        scraper = self._get_scraper(request.method)

        # Execute scraping
        result = await scraper.scrape(request)

        # Convert to requested output format
        formatted_result = self._format_output(result, request.output_format)

        return {
            "scraping_id": result.scraping_id,
            "request": result.request.__dict__,
            "content": formatted_result,
            "urls_scraped": result.urls_scraped,
            "urls_failed": result.urls_failed,
            "total_pages": result.total_pages,
            "scraping_time": result.scraping_time,
            "method": result.request.method.value,
            "timestamp": result.timestamp.isoformat(),
            "metadata": result.metadata,
        }

    def _parse_scraping_request(self, kwargs: Dict[str, Any]) -> ScrapingRequest:
        """Parse scraping request from kwargs."""
        return ScrapingRequest(
            url=kwargs.get("url", ""),
            method=ScrapingMethod(kwargs.get("method", self.default_method.value)),
            content_types=[
                ContentType(ct) for ct in kwargs.get("content_types", ["text"])
            ],
            output_format=OutputFormat(kwargs.get("output_format", "json")),
            timeout=kwargs.get("timeout", self.timeout),
            max_pages=min(kwargs.get("max_pages", self.max_pages), 50),
            follow_links=kwargs.get("follow_links", False),
            link_selector=kwargs.get("link_selector", "a[href]"),
            wait_for=kwargs.get("wait_for"),
            wait_timeout=kwargs.get("wait_timeout", 10),
            user_agent=kwargs.get("user_agent"),
            headers=kwargs.get("headers", {}),
            cookies=kwargs.get("cookies", {}),
            proxy=kwargs.get("proxy"),
            javascript=kwargs.get("javascript", False),
            screenshots=kwargs.get("screenshots", False),
            respect_robots=kwargs.get("respect_robots", self.respect_robots),
            delay_between_requests=kwargs.get(
                "delay_between_requests", self.delay_between_requests
            ),
            max_retries=kwargs.get("max_retries", 3),
            custom_selectors=kwargs.get("custom_selectors", {}),
            exclude_selectors=kwargs.get("exclude_selectors", []),
            metadata=kwargs.get("metadata", {}),
        )

    def _get_scraper(self, method: ScrapingMethod):
        """Get appropriate scraper instance."""
        if method == ScrapingMethod.HTTP:
            return self.http_scraper
        elif method == ScrapingMethod.SELENIUM:
            return self.selenium_scraper
        else:
            raise ToolValidationError(
                f"Unsupported scraping method: {method}", tool_name=self.NAME
            )

    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    async def _check_robots_txt(self, url: str) -> bool:
        """Check robots.txt for scraping permissions (simplified)."""
        # This is a simplified implementation
        # In production, you would want to use a proper robots.txt parser
        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"

            async with httpx.AsyncClient() as client:
                response = await client.get(robots_url)
                if response.status_code == 200:
                    # Simple check - allow scraping if no explicit disallow
                    content = response.text.lower()
                    return "disallow" not in content or f"disallow: /" not in content

            return True  # Allow if robots.txt not found

        except Exception:
            return True  # Allow if error checking robots.txt

    def _format_output(
        self, result: ScrapingResult, output_format: OutputFormat
    ) -> Any:
        """Format output according to requested format."""
        if output_format == OutputFormat.JSON:
            return result.to_dict()
        elif output_format == OutputFormat.CSV:
            return self._to_csv(result)
        elif output_format == OutputFormat.TXT:
            return self._to_txt(result)
        elif output_format == OutputFormat.HTML:
            return self._to_html(result)
        else:
            return result.to_dict()

    def _to_csv(self, result: ScrapingResult) -> str:
        """Convert result to CSV format."""
        import csv
        import io

        output = io.StringIO()

        if result.content:
            # Get all possible keys from content
            all_keys = set()
            for content in result.content:
                if isinstance(content.data, dict):
                    all_keys.update(content.data.keys())

            writer = csv.DictWriter(output, fieldnames=list(all_keys))
            writer.writeheader()

            for content in result.content:
                if isinstance(content.data, dict):
                    writer.writerow(content.data)

        return output.getvalue()

    def _to_txt(self, result: ScrapingResult) -> str:
        """Convert result to text format."""
        output = []

        for content in result.content:
            output.append(f"URL: {content.url}")
            output.append(f"Content Type: {content.content_type.value}")
            output.append(f"Timestamp: {content.timestamp}")
            output.append(f"Size: {content.size} bytes")
            output.append("")

            if isinstance(content.data, dict):
                for key, value in content.data.items():
                    output.append(f"{key}: {value}")
            else:
                output.append(str(content.data))

            output.append("-" * 50)

        return "\n".join(output)

    def _to_html(self, result: ScrapingResult) -> str:
        """Convert result to HTML format."""
        html = [
            "<html>",
            "<head>",
            "<title>Scraping Results</title>",
            "</head>",
            "<body>",
        ]

        for content in result.content:
            html.append(f"<h2>{content.url}</h2>")
            html.append(
                f"<p><strong>Content Type:</strong> {content.content_type.value}</p>"
            )
            html.append(f"<p><strong>Timestamp:</strong> {content.timestamp}</p>")
            html.append(f"<p><strong>Size:</strong> {content.size} bytes</p>")

            if isinstance(content.data, dict):
                html.append("<pre>")
                html.append(json.dumps(content.data, indent=2))
                html.append("</pre>")
            else:
                html.append(f"<pre>{content.data}</pre>")

            html.append("<hr>")

        html.append("</body>", "</html>")

        return "\n".join(html)

    def _validate_input(self, input_data: Dict[str, Any]):
        """Validate input data."""
        super()._validate_input(input_data)

        url = input_data.get("url", "")
        if not url.strip():
            raise ToolValidationError("URL cannot be empty", tool_name=self.NAME)

        max_pages = input_data.get("max_pages", self.max_pages)
        if max_pages < 1 or max_pages > 100:
            raise ToolValidationError(
                "max_pages must be between 1 and 100", tool_name=self.NAME
            )

    async def cleanup(self):
        """Cleanup tool resources."""
        await self.http_scraper.close()
        await self.selenium_scraper.close()


# Export main components
__all__ = [
    "WebScraperTool",
    "ScrapingRequest",
    "ScrapedContent",
    "ScrapingResult",
    "ScrapingMethod",
    "ContentType",
    "OutputFormat",
    "HTTPScraper",
    "SeleniumScraper",
]
