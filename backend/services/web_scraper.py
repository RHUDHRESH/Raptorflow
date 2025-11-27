"""
Web Scraping Service

Fetches and extracts textual content from web pages using open-source libraries.
Provides clean, parsed text suitable for analysis and natural language processing.
"""

import structlog
from typing import Optional, List
from urllib.parse import urlparse, urljoin
import re

import httpx
from bs4 import BeautifulSoup

logger = structlog.get_logger(__name__)


class WebScraperService:
    """
    Service for scraping and extracting textual content from web pages.

    This service uses httpx for async HTTP requests and BeautifulSoup4 for HTML parsing.
    It extracts only the main textual content while ignoring navigation, footers, and scripts.

    Features:
    - Async HTTP requests with proper user-agent headers
    - Intelligent text extraction focused on main content
    - Error handling for network and parsing issues
    """

    def __init__(self, timeout: float = 30.0):
        """
        Initialize the web scraper service.

        Args:
            timeout: Request timeout in seconds (default: 30.0)
        """
        self.timeout = timeout
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

    async def get_page_content(self, url: str) -> Optional[str]:
        """
        Fetch and extract textual content from a web page.

        This method:
        1. Validates the URL
        2. Makes an async HTTP GET request with proper headers
        3. Parses the HTML with BeautifulSoup4
        4. Extracts main textual content from relevant tags
        5. Cleans and normalizes the text

        Args:
            url: The URL to scrape

        Returns:
            Clean textual content from the page, or None if extraction fails

        Raises:
            ValueError: If the URL is invalid
        """
        try:
            # Validate URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValueError(f"Invalid URL format: {url}")

            logger.info("Fetching content from URL", url=url)

            # Set up headers to be a good web citizen
            headers = {
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "DNT": "1",  # Do Not Track
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }

            # Make async HTTP request
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)

                # Check response status
                response.raise_for_status()

                # Get content type to ensure it's HTML
                content_type = response.headers.get("content-type", "")
                if "text/html" not in content_type.lower():
                    logger.warning(
                        "Content type is not HTML, skipping extraction",
                        url=url,
                        content_type=content_type
                    )
                    return None

                # Parse HTML with BeautifulSoup
                html_content = response.text
                soup = BeautifulSoup(html_content, "html.parser")

                # Extract main textual content
                text_content = self._extract_text_content(soup)

                logger.info(
                    "Successfully extracted content from URL",
                    url=url,
                    content_length=len(text_content) if text_content else 0
                )

                return text_content

        except httpx.RequestError as e:
            logger.error(
                "Network error while fetching URL",
                url=url,
                error=str(e)
            )
            return None

        except httpx.HTTPStatusError as e:
            logger.error(
                "HTTP error while fetching URL",
                url=url,
                status_code=e.response.status_code,
                error=str(e)
            )
            return None

        except Exception as e:
            logger.error(
                "Unexpected error while scraping URL",
                url=url,
                error=str(e)
            )
            return None

    def _extract_text_content(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract main textual content from BeautifulSoup parsed HTML.

        This method extracts text from main content tags while ignoring
        navigation, script, and footer elements. It concatenates all relevant
        text and cleans it up for analysis.

        Args:
            soup: BeautifulSoup object containing parsed HTML

        Returns:
            Cleaned and concatenated textual content, or None if no content found
        """

        # Remove script, style, nav, and footer elements
        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.decompose()

        # Tags that are likely to contain main textual content
        content_tags = ["p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "article", "section", "main"]

        # Extract text from relevant tags
        text_parts: List[str] = []

        for tag_name in content_tags:
            elements = soup.find_all(tag_name)
            for element in elements:
                # Get text content, stripped of extra whitespace
                text = element.get_text(strip=True)
                if text and len(text) > 10:  # Filter out very short text fragments
                    text_parts.append(text)

        # Concatenate all text parts
        if not text_parts:
            return None

        full_text = " ".join(text_parts)

        # Clean up the text
        cleaned_text = self._clean_text(full_text)

        return cleaned_text if cleaned_text else None

    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.

        Performs various text cleaning operations:
        - Normalize whitespace (convert multiple spaces/tabs/newlines to single space)
        - Remove excessive punctuation
        - Trim leading/trailing whitespace

        Args:
            text: Raw text to clean

        Returns:
            Cleaned and normalized text
        """

        if not text:
            return ""

        # Normalize whitespace - convert multiple spaces, tabs, newlines to single spaces
        text = re.sub(r'\s+', ' ', text)

        # Remove excessive punctuation (more than 3 consecutive punctuation marks)
        text = re.sub(r'[^\w\s]{4,}', '...', text)

        # Trim leading/trailing whitespace
        text = text.strip()

        return text


# Global service instance
web_scraper = WebScraperService()
