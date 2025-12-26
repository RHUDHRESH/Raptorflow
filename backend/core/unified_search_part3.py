"""
Part 3: Advanced Web Crawling and Content Extraction
RaptorFlow Unified Search System - Industrial Grade AI Agent Search Infrastructure
===============================================================================
This module implements advanced web crawling with multi-tiered content extraction,
intelligent fallback mechanisms, and comprehensive content analysis.
"""

import asyncio
import hashlib
import json
import logging
import re
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse, urlunparse

import aiohttp
import httpx
import readability
from bs4 import BeautifulSoup, Comment
from readability import Document

from core.unified_search_part1 import (
    ContentType,
    RateLimiter,
    SearchProvider,
    SearchResult,
)

logger = logging.getLogger("raptorflow.unified_search.crawler")


@dataclass
class CrawlPolicy:
    """Advanced crawling policy with intelligent constraints."""

    max_concurrent: int = 5
    timeout: int = 30
    max_content_length: int = 50000
    min_content_length: int = 100
    max_depth: int = 3
    follow_redirects: bool = True
    respect_robots_txt: bool = True
    user_agent: str = "RaptorFlowResearch/3.0 (Industrial Grade)"
    allowed_mime_types: Set[str] = None
    blocked_mime_types: Set[str] = None
    allowed_domains: Set[str] = None
    blocked_domains: Set[str] = None
    blocked_patterns: List[str] = None
    rate_limit_delay: float = 1.0
    retry_attempts: int = 3
    retry_delay: float = 2.0
    enable_js_rendering: bool = True
    extract_images: bool = False
    extract_links: bool = True
    extract_metadata: bool = True

    def __post_init__(self):
        """Initialize default values."""
        if self.allowed_mime_types is None:
            self.allowed_mime_types = {
                "text/html",
                "text/plain",
                "application/xhtml+xml",
                "text/xml",
                "application/xml",
                "application/json",
            }

        if self.blocked_mime_types is None:
            self.blocked_mime_types = {
                "application/pdf",
                "application/zip",
                "application/octet-stream",
                "image/jpeg",
                "image/png",
                "image/gif",
                "video/mp4",
            }

        if self.blocked_patterns is None:
            self.blocked_patterns = [
                r".*\.pdf$",
                r".*\.zip$",
                r".*\.exe$",
                r".*\.dmg$",
                r".*/login.*",
                r".*/signup.*",
                r".*/cart.*",
                r".*/checkout.*",
            ]


@dataclass
class ExtractedContent:
    """Rich content extraction with comprehensive metadata."""

    title: str
    content: str
    cleaned_content: str
    summary: str
    language: str
    word_count: int
    reading_time: int
    headings: List[str]
    links: List[str]
    images: List[str]
    videos: List[str]
    metadata: Dict[str, Any]
    extraction_method: str
    quality_score: float
    timestamp: float


class RobotsTxtParser:
    """Robots.txt parser for respectful crawling."""

    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = 86400  # 24 hours

    async def can_crawl(self, url: str, user_agent: str) -> bool:
        """Check if URL can be crawled according to robots.txt."""
        try:
            parsed = urlparse(url)
            domain = f"{parsed.scheme}://{parsed.netloc}"

            # Check cache first
            if domain in self.cache:
                cached_data, timestamp = self.cache[domain]
                if time.time() - timestamp < self.cache_ttl:
                    return self._check_rules(cached_data, parsed.path, user_agent)

            # Fetch and parse robots.txt
            rules = await self._fetch_robots_txt(domain)
            self.cache[domain] = (rules, time.time())

            return self._check_rules(rules, parsed.path, user_agent)

        except Exception as e:
            logger.debug(f"Robots.txt check failed for {url}: {e}")
            return True  # Allow crawling if robots.txt is unavailable

    async def _fetch_robots_txt(self, domain: str) -> Dict[str, Any]:
        """Fetch and parse robots.txt."""
        robots_url = f"{domain}/robots.txt"

        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            ) as session:
                async with session.get(robots_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        return self._parse_robots_content(content)
        except Exception as e:
            logger.debug(f"Failed to fetch robots.txt from {robots_url}: {e}")

        return {"allow": ["/"], "disallow": []}

    def _parse_robots_content(self, content: str) -> Dict[str, Any]:
        """Parse robots.txt content."""
        rules = {"allow": ["/"], "disallow": []}
        current_agent = "*"

        for line in content.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if line.lower().startswith("user-agent:"):
                current_agent = line.split(":", 1)[1].strip()
            elif current_agent == "*" or "bot" in current_agent.lower():
                if line.lower().startswith("disallow:"):
                    path = line.split(":", 1)[1].strip()
                    if path:
                        rules["disallow"].append(path)
                elif line.lower().startswith("allow:"):
                    path = line.split(":", 1)[1].strip()
                    if path:
                        rules["allow"].append(path)

        return rules

    def _check_rules(self, rules: Dict[str, Any], path: str, user_agent: str) -> bool:
        """Check if path is allowed by rules."""
        # Check disallow rules first
        for disallow in rules.get("disallow", []):
            if self._path_matches(path, disallow):
                # Check if there's a more specific allow rule
                for allow in rules.get("allow", []):
                    if self._path_matches(path, allow) and len(allow) > len(disallow):
                        return True
                return False

        return True

    def _path_matches(self, path: str, pattern: str) -> bool:
        """Check if path matches robots.txt pattern."""
        if pattern == "/":
            return True
        if pattern.endswith("*"):
            return path.startswith(pattern[:-1])
        if pattern.startswith("/"):
            return path == pattern or path.startswith(pattern)
        return pattern in path


class ContentExtractor:
    """Advanced content extraction with multiple methods."""

    def __init__(self, policy: CrawlPolicy):
        self.policy = policy
        self.robots_parser = RobotsTxtParser()
        self.rate_limiter = RateLimiter(1.0 / policy.rate_limit_delay)

    async def extract_content(
        self, url: str, session: aiohttp.ClientSession
    ) -> Optional[ExtractedContent]:
        """Extract content using best available method."""
        # Check robots.txt
        if not await self.robots_parser.can_crawl(url, self.policy.user_agent):
            logger.debug(f"Robots.txt disallows crawling: {url}")
            return None

        await self.rate_limiter.wait_for_token()

        # Try extraction methods in order of preference
        methods = [
            self._extract_with_readability,
            self._extract_with_beautifulsoup,
            self._extract_with_jina_reader,
            self._extract_with_firecrawl,
        ]

        for method in methods:
            try:
                content = await method(url, session)
                if content and content.quality_score >= 0.3:
                    return content
            except Exception as e:
                logger.debug(
                    f"Extraction method {method.__name__} failed for {url}: {e}"
                )
                continue

        return None

    async def _extract_with_readability(
        self, url: str, session: aiohttp.ClientSession
    ) -> Optional[ExtractedContent]:
        """Extract content using readability algorithm."""
        try:
            async with session.get(url, timeout=self.policy.timeout) as response:
                if response.status != 200:
                    return None

                html = await response.text()

                # Check content type
                content_type = response.headers.get("content-type", "").lower()
                if not any(mt in content_type for mt in self.policy.allowed_mime_types):
                    return None

                # Extract main content
                doc = Document(html)
                title = doc.title()
                content = doc.summary()

                # Clean and analyze content
                cleaned_content = self._clean_html(content)
                summary = self._generate_summary(cleaned_content)
                language = self._detect_language(cleaned_content)

                # Extract metadata
                metadata = self._extract_metadata(html, url)
                headings = self._extract_headings(content)
                links = self._extract_links(content, url)
                images = self._extract_images(content, url)

                word_count = len(cleaned_content.split())
                reading_time = max(1, word_count // 200)

                return ExtractedContent(
                    title=title,
                    content=content,
                    cleaned_content=cleaned_content,
                    summary=summary,
                    language=language,
                    word_count=word_count,
                    reading_time=reading_time,
                    headings=headings,
                    links=links,
                    images=images,
                    videos=[],
                    metadata=metadata,
                    extraction_method="readability",
                    quality_score=self._calculate_quality_score(
                        cleaned_content, metadata
                    ),
                    timestamp=time.time(),
                )

        except Exception as e:
            logger.debug(f"Readability extraction failed for {url}: {e}")
            return None

    async def _extract_with_beautifulsoup(
        self, url: str, session: aiohttp.ClientSession
    ) -> Optional[ExtractedContent]:
        """Extract content using BeautifulSoup."""
        try:
            async with session.get(url, timeout=self.policy.timeout) as response:
                if response.status != 200:
                    return None

                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                # Remove unwanted elements
                for element in soup(
                    ["script", "style", "nav", "footer", "header", "aside", "ad"]
                ):
                    element.decompose()

                # Remove comments
                for comment in soup.find_all(
                    string=lambda text: isinstance(text, Comment)
                ):
                    comment.extract()

                # Extract title
                title_tag = soup.find("title")
                title = title_tag.get_text().strip() if title_tag else ""

                # Find main content
                main_content = self._find_main_content(soup)
                content = main_content.get_text() if main_content else soup.get_text()

                # Clean content
                cleaned_content = self._clean_text(content)

                if len(cleaned_content) < self.policy.min_content_length:
                    return None

                # Extract metadata and other elements
                metadata = self._extract_metadata(html, url)
                headings = self._extract_headings_from_soup(soup)
                links = self._extract_links_from_soup(soup, url)
                images = self._extract_images_from_soup(soup, url)

                word_count = len(cleaned_content.split())
                reading_time = max(1, word_count // 200)
                summary = self._generate_summary(cleaned_content)
                language = self._detect_language(cleaned_content)

                return ExtractedContent(
                    title=title,
                    content=cleaned_content,
                    cleaned_content=cleaned_content,
                    summary=summary,
                    language=language,
                    word_count=word_count,
                    reading_time=reading_time,
                    headings=headings,
                    links=links,
                    images=images,
                    videos=[],
                    metadata=metadata,
                    extraction_method="beautifulsoup",
                    quality_score=self._calculate_quality_score(
                        cleaned_content, metadata
                    ),
                    timestamp=time.time(),
                )

        except Exception as e:
            logger.debug(f"BeautifulSoup extraction failed for {url}: {e}")
            return None

    async def _extract_with_jina_reader(
        self, url: str, session: aiohttp.ClientSession
    ) -> Optional[ExtractedContent]:
        """Extract content using Jina Reader API."""
        try:
            jina_url = f"https://r.jina.ai/http://{url}"
            headers = {
                "User-Agent": self.policy.user_agent,
                "Accept": "application/json",
            }

            async with session.get(
                jina_url, headers=headers, timeout=self.policy.timeout
            ) as response:
                if response.status != 200:
                    return None

                data = await response.json()

                title = data.get("title", "")
                content = data.get("content", "")

                if len(content) < self.policy.min_content_length:
                    return None

                cleaned_content = self._clean_text(content)
                summary = self._generate_summary(cleaned_content)
                language = self._detect_language(cleaned_content)

                word_count = len(cleaned_content.split())
                reading_time = max(1, word_count // 200)

                metadata = {
                    "source": "jina_reader",
                    "url": url,
                    "extraction_time": time.time(),
                }

                return ExtractedContent(
                    title=title,
                    content=content,
                    cleaned_content=cleaned_content,
                    summary=summary,
                    language=language,
                    word_count=word_count,
                    reading_time=reading_time,
                    headings=[],
                    links=[],
                    images=[],
                    videos=[],
                    metadata=metadata,
                    extraction_method="jina_reader",
                    quality_score=0.8,  # Jina Reader typically provides high quality
                    timestamp=time.time(),
                )

        except Exception as e:
            logger.debug(f"Jina Reader extraction failed for {url}: {e}")
            return None

    async def _extract_with_firecrawl(
        self, url: str, session: aiohttp.ClientSession
    ) -> Optional[ExtractedContent]:
        """Extract content using Firecrawl API."""
        try:
            # This would require Firecrawl API key
            # For now, return None as placeholder
            return None

        except Exception as e:
            logger.debug(f"Firecrawl extraction failed for {url}: {e}")
            return None

    def _find_main_content(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Find the main content area of the page."""
        # Common selectors for main content
        content_selectors = [
            "main",
            "article",
            '[role="main"]',
            ".content",
            ".main-content",
            ".post-content",
            ".entry-content",
            ".article-content",
            "#content",
            ".story-body",
            ".post-body",
        ]

        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                return element

        # Fallback to largest text block
        text_blocks = soup.find_all(["p", "div"], string=True)
        if text_blocks:
            largest = max(text_blocks, key=lambda x: len(x.get_text()))
            return largest

        return soup

    def _clean_html(self, html: str) -> str:
        """Clean HTML content."""
        soup = BeautifulSoup(html, "html.parser")

        # Remove unwanted tags
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        # Get clean text
        text = soup.get_text()

        # Clean whitespace
        lines = [line.strip() for line in text.splitlines()]
        chunks = [phrase.strip() for line in lines for phrase in line.split("  ")]

        return "\n".join(chunk for chunk in chunks if chunk)

    def _clean_text(self, text: str) -> str:
        """Clean plain text content."""
        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove special characters but keep basic punctuation
        text = re.sub(r"[^\w\s\.\,\!\?\;\:\-\(\)\[\]\"\'\/\n]", "", text)

        # Remove multiple newlines
        text = re.sub(r"\n+", "\n", text)

        return text.strip()

    def _generate_summary(self, content: str, max_sentences: int = 3) -> str:
        """Generate a summary of the content."""
        sentences = re.split(r"[.!?]+", content)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) <= max_sentences:
            return ". ".join(sentences)

        # Take first, middle, and last sentences for a balanced summary
        summary_sentences = [
            sentences[0],
            sentences[len(sentences) // 2],
            sentences[-1],
        ]

        return ". ".join(summary_sentences)

    def _detect_language(self, text: str) -> str:
        """Detect content language."""
        # Simple language detection based on common words
        common_words = {
            "en": {"the", "and", "to", "of", "in", "is", "it", "you", "that", "he"},
            "es": {"el", "la", "de", "que", "y", "en", "un", "es", "se", "no"},
            "fr": {"le", "de", "et", "à", "un", "il", "être", "et", "en", "avoir"},
            "de": {"der", "die", "und", "in", "den", "von", "zu", "das", "mit", "sich"},
            "it": {"il", "di", "che", "e", "la", "un", "a", "per", "non", "in"},
        }

        text_lower = text.lower()
        words = set(text_lower.split())

        best_lang = "en"
        best_score = 0

        for lang, common_set in common_words.items():
            score = len(words.intersection(common_set))
            if score > best_score:
                best_score = score
                best_lang = lang

        return best_lang

    def _extract_metadata(self, html: str, url: str) -> Dict[str, Any]:
        """Extract metadata from HTML."""
        metadata = {"url": url}

        soup = BeautifulSoup(html, "html.parser")

        # Basic meta tags
        title_tag = soup.find("title")
        if title_tag:
            metadata["title"] = title_tag.get_text().strip()

        # Open Graph tags
        og_tags = ["og:title", "og:description", "og:image", "og:type", "og:site_name"]
        for tag in og_tags:
            element = soup.find("meta", property=tag)
            if element:
                metadata[tag.replace(":", "_")] = element.get("content", "")

        # Twitter Card tags
        twitter_tags = ["twitter:title", "twitter:description", "twitter:image"]
        for tag in twitter_tags:
            element = soup.find("meta", name=tag)
            if element:
                metadata[tag.replace(":", "_")] = element.get("content", "")

        # Description meta tag
        desc_tag = soup.find("meta", attrs={"name": "description"})
        if desc_tag:
            metadata["description"] = desc_tag.get("content", "")

        # Author
        author_tag = soup.find("meta", attrs={"name": "author"})
        if author_tag:
            metadata["author"] = author_tag.get("content", "")

        # Published time
        pub_time_tags = [
            "article:published_time",
            "published_time",
            "datePublished",
            "publication_date",
            "publish_date",
        ]
        for tag in pub_time_tags:
            element = soup.find("meta", property=tag) or soup.find("meta", name=tag)
            if element:
                metadata["published_time"] = element.get("content", "")
                break

        return metadata

    def _extract_headings(self, content: str) -> List[str]:
        """Extract headings from content."""
        soup = BeautifulSoup(content, "html.parser")
        headings = []

        for level in range(1, 7):
            for heading in soup.find_all(f"h{level}"):
                text = heading.get_text().strip()
                if text:
                    headings.append(text)

        return headings

    def _extract_headings_from_soup(self, soup: BeautifulSoup) -> List[str]:
        """Extract headings from BeautifulSoup object."""
        headings = []

        for level in range(1, 7):
            for heading in soup.find_all(f"h{level}"):
                text = heading.get_text().strip()
                if text:
                    headings.append(text)

        return headings

    def _extract_links(self, content: str, base_url: str) -> List[str]:
        """Extract links from content."""
        soup = BeautifulSoup(content, "html.parser")
        links = []

        for link in soup.find_all("a", href=True):
            href = link["href"]
            full_url = urljoin(base_url, href)

            # Filter out invalid links
            if full_url.startswith("http") and not any(
                skip in full_url for skip in ["#", "javascript:", "mailto:"]
            ):
                links.append(full_url)

        return list(set(links))  # Remove duplicates

    def _extract_links_from_soup(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract links from BeautifulSoup object."""
        links = []

        for link in soup.find_all("a", href=True):
            href = link["href"]
            full_url = urljoin(base_url, href)

            if full_url.startswith("http") and not any(
                skip in full_url for skip in ["#", "javascript:", "mailto:"]
            ):
                links.append(full_url)

        return list(set(links))

    def _extract_images(self, content: str, base_url: str) -> List[str]:
        """Extract image URLs from content."""
        soup = BeautifulSoup(content, "html.parser")
        images = []

        for img in soup.find_all("img", src=True):
            src = img["src"]
            full_url = urljoin(base_url, src)

            if full_url.startswith("http"):
                images.append(full_url)

        return list(set(images))

    def _extract_images_from_soup(
        self, soup: BeautifulSoup, base_url: str
    ) -> List[str]:
        """Extract image URLs from BeautifulSoup object."""
        images = []

        for img in soup.find_all("img", src=True):
            src = img["src"]
            full_url = urljoin(base_url, src)

            if full_url.startswith("http"):
                images.append(full_url)

        return list(set(images))

    def _calculate_quality_score(self, content: str, metadata: Dict[str, Any]) -> float:
        """Calculate quality score for extracted content."""
        score = 0.0

        # Length score
        word_count = len(content.split())
        if word_count > 100:
            score += 0.2
        if word_count > 500:
            score += 0.2
        if word_count > 1000:
            score += 0.1

        # Structure score
        if "\n" in content:  # Has paragraphs
            score += 0.1
        if any(punct in content for punct in ".!?"):  # Has sentences
            score += 0.1

        # Metadata score
        if metadata.get("title"):
            score += 0.1
        if metadata.get("description"):
            score += 0.1
        if metadata.get("author"):
            score += 0.1

        return min(1.0, score)


class AdvancedCrawler:
    """Industrial-grade web crawler with intelligent extraction."""

    def __init__(self, policy: Optional[CrawlPolicy] = None):
        self.policy = policy or CrawlPolicy()
        self.content_extractor = ContentExtractor(self.policy)
        self.session: Optional[aiohttp.ClientSession] = None
        self.crawled_urls: Set[str] = set()
        self.failed_urls: Set[str] = set()
        self.stats = {
            "total_requests": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
            "cache_hits": 0,
        }

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.policy.timeout),
            headers={"User-Agent": self.policy.user_agent},
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def crawl_urls(self, urls: List[str]) -> List[ExtractedContent]:
        """Crawl multiple URLs concurrently."""
        if not self.session:
            raise RuntimeError("Crawler must be used as async context manager")

        # Filter URLs
        valid_urls = []
        for url in urls:
            if (
                self._is_valid_url(url)
                and url not in self.crawled_urls
                and url not in self.failed_urls
            ):
                valid_urls.append(url)

        if not valid_urls:
            return []

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.policy.max_concurrent)

        async def crawl_single(url: str) -> Optional[ExtractedContent]:
            async with semaphore:
                return await self._crawl_single_url(url)

        # Execute crawling concurrently
        tasks = [crawl_single(url) for url in valid_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        extracted_contents = []
        for result in results:
            if isinstance(result, ExtractedContent):
                extracted_contents.append(result)
            elif isinstance(result, Exception):
                logger.debug(f"Crawling error: {result}")
                self.stats["failed_extractions"] += 1

        return extracted_contents

    async def _crawl_single_url(self, url: str) -> Optional[ExtractedContent]:
        """Crawl a single URL."""
        self.stats["total_requests"] += 1

        try:
            content = await self.content_extractor.extract_content(url, self.session)

            if content:
                self.crawled_urls.add(url)
                self.stats["successful_extractions"] += 1
                return content
            else:
                self.failed_urls.add(url)
                self.stats["failed_extractions"] += 1
                return None

        except Exception as e:
            logger.debug(f"Failed to crawl {url}: {e}")
            self.failed_urls.add(url)
            self.stats["failed_extractions"] += 1
            return None

    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid for crawling."""
        try:
            parsed = urlparse(url)

            # Basic validation
            if not parsed.scheme or not parsed.netloc:
                return False

            if parsed.scheme not in ["http", "https"]:
                return False

            # Domain filtering
            if (
                self.policy.allowed_domains
                and parsed.netloc not in self.policy.allowed_domains
            ):
                return False

            if (
                self.policy.blocked_domains
                and parsed.netloc in self.policy.blocked_domains
            ):
                return False

            # Pattern filtering
            for pattern in self.policy.blocked_patterns:
                if re.match(pattern, url):
                    return False

            return True

        except Exception:
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get crawling statistics."""
        total = self.stats["total_requests"]
        if total > 0:
            success_rate = self.stats["successful_extractions"] / total
        else:
            success_rate = 0.0

        return {
            **self.stats,
            "success_rate": success_rate,
            "crawled_urls_count": len(self.crawled_urls),
            "failed_urls_count": len(self.failed_urls),
        }
