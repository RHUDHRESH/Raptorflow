"""
Part 1: Core Unified Search Architecture
RaptorFlow Unified Search System - Industrial Grade AI Agent Search Infrastructure
===============================================================================
This is the foundation module that establishes the core architecture for the unified
search system, consolidating all existing search capabilities into a single, AI agent-
friendly interface with fault tolerance, result consolidation, and deep research.
"""

import asyncio
import hashlib
import json
import logging
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from urllib.parse import urlparse

import aiohttp
import httpx
import pydantic
from bs4 import BeautifulSoup

# Configure industrial logging
logger = logging.getLogger("raptorflow.unified_search")
logger.setLevel(logging.INFO)


class SearchMode(Enum):
    """Search operation modes for different use cases."""

    LIGHTNING = "lightning"  # Fast, shallow search for quick answers
    STANDARD = "standard"  # Balanced search for general research
    DEEP = "deep"  # Comprehensive multi-layered research
    EXHAUSTIVE = "exhaustive"  # Maximum depth research with cross-verification


class SearchProvider(Enum):
    """Available search providers."""

    NATIVE = "native"
    SERPER = "serper"
    BRAVE = "brave"
    DUCKDUCKGO = "duckduckgo"
    FIRECRAWL = "firecrawl"
    JINA = "jina"
    BEAUTIFULSOUP = "beautifulsoup"


class ContentType(Enum):
    """Content types for specialized search."""

    WEB = "web"
    ACADEMIC = "academic"
    NEWS = "news"
    SOCIAL = "social"
    FORUM = "forum"
    DOCUMENTATION = "documentation"
    ECOMMERCE = "ecommerce"
    VIDEO = "video"


@dataclass
class SearchQuery:
    """Enhanced search query with context and preferences."""

    text: str
    mode: SearchMode = SearchMode.STANDARD
    content_types: List[ContentType] = field(default_factory=lambda: [ContentType.WEB])
    max_results: int = 10
    max_depth: int = 3
    time_range: Optional[str] = None  # "1d", "1w", "1m", "1y"
    language: str = "en"
    region: str = "us"
    safe_search: bool = True
    include_images: bool = False
    include_videos: bool = False
    require_https: bool = True
    exclude_domains: Set[str] = field(default_factory=set)
    prefer_domains: Set[str] = field(default_factory=set)
    user_agent: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate and normalize query parameters."""
        if not self.text or len(self.text.strip()) < 2:
            raise ValueError("Search query text must be at least 2 characters")
        self.text = self.text.strip()
        self.max_results = min(max(1, self.max_results), 100)
        self.max_depth = min(max(1, self.max_depth), 10)


@dataclass
class SearchResult:
    """Unified search result with rich metadata."""

    url: str
    title: str
    content: str
    snippet: str = ""
    provider: SearchProvider = SearchProvider.NATIVE
    content_type: ContentType = ContentType.WEB
    relevance_score: float = 0.0
    trust_score: float = 0.0
    freshness_score: float = 0.0
    domain_authority: float = 0.0
    page_rank: float = 0.0
    publish_date: Optional[datetime] = None
    last_modified: Optional[datetime] = None
    word_count: int = 0
    reading_time_minutes: int = 0
    language: str = "en"
    region: str = "us"
    is_https: bool = True
    domain: str = ""
    subdomain: str = ""
    tld: str = ""
    image_urls: List[str] = field(default_factory=list)
    video_urls: List[str] = field(default_factory=list)
    external_links: List[str] = field(default_factory=list)
    internal_links: List[str] = field(default_factory=list)
    headings: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    entities: List[Dict[str, Any]] = field(default_factory=list)
    sentiment: Optional[str] = None
    bias_score: float = 0.0
    factual_accuracy: float = 0.0
    source_credibility: float = 0.0
    extraction_timestamp: datetime = field(default_factory=datetime.now)
    processing_time_ms: int = 0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Post-processing for result normalization."""
        if self.url:
            parsed = urlparse(self.url)
            self.domain = parsed.netloc.lower()
            self.subdomain = parsed.hostname.split(".")[0] if parsed.hostname else ""
            self.tld = (
                parsed.hostname.split(".")[-1]
                if parsed.hostname and "." in parsed.hostname
                else ""
            )
            self.is_https = parsed.scheme == "https"

        self.word_count = len(self.content.split()) if self.content else 0
        self.reading_time_minutes = max(1, self.word_count // 200)  # Average 200 WPM


@dataclass
class SearchSession:
    """Search session for tracking and optimization."""

    session_id: str
    query: SearchQuery
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    status: str = "initialized"
    total_results_found: int = 0
    total_results_processed: int = 0
    providers_used: List[SearchProvider] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    cost_metrics: Dict[str, float] = field(default_factory=dict)
    cache_hits: int = 0
    cache_misses: int = 0
    retry_count: int = 0
    fallback_count: int = 0

    def __post_init__(self):
        """Generate session ID if not provided."""
        if not self.session_id:
            self.session_id = hashlib.md5(
                f"{self.query.text}_{time.time()}_{random.random()}".encode()
            ).hexdigest()[:16]


@dataclass
class SearchMetrics:
    """Comprehensive search performance metrics."""

    total_queries: int = 0
    successful_queries: int = 0
    failed_queries: int = 0
    average_response_time_ms: float = 0.0
    average_results_per_query: float = 0.0
    provider_success_rates: Dict[SearchProvider, float] = field(default_factory=dict)
    content_type_distribution: Dict[ContentType, float] = field(default_factory=dict)
    error_rates: Dict[str, float] = field(default_factory=dict)
    cache_hit_rate: float = 0.0
    cost_per_query: float = 0.0
    total_cost: float = 0.0
    uptime_percentage: float = 100.0
    last_updated: datetime = field(default_factory=datetime.now)


class BaseSearchProvider(ABC):
    """Abstract base class for all search providers."""

    def __init__(self, name: SearchProvider, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.is_available = True
        self.rate_limit_remaining = 1000
        self.rate_limit_reset_time = datetime.now()
        self.last_success_time = None
        self.last_error_time = None
        self.consecutive_failures = 0
        self.total_requests = 0
        self.successful_requests = 0

    @abstractmethod
    async def search(self, query: SearchQuery) -> List[SearchResult]:
        """Execute search query and return results."""
        pass

    @abstractmethod
    async def is_healthy(self) -> bool:
        """Check if provider is healthy and available."""
        pass

    @abstractmethod
    def get_cost_per_request(self) -> float:
        """Get cost per request for this provider."""
        pass

    def can_handle_query(self, query: SearchQuery) -> bool:
        """Check if provider can handle the specific query."""
        return self.is_available and self.rate_limit_remaining > 0

    def update_metrics(self, success: bool, response_time_ms: float):
        """Update provider performance metrics."""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
            self.last_success_time = datetime.now()
            self.consecutive_failures = 0
        else:
            self.last_error_time = datetime.now()
            self.consecutive_failures += 1

        # Disable provider after too many consecutive failures
        if self.consecutive_failures >= 5:
            self.is_available = False
            logger.warning(
                f"Provider {self.name} disabled after {self.consecutive_failures} failures"
            )

    def get_success_rate(self) -> float:
        """Get provider success rate."""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests


class SearchCache:
    """Intelligent search result caching system."""

    def __init__(self, max_size: int = 10000, ttl_hours: int = 24):
        self.max_size = max_size
        self.ttl = timedelta(hours=ttl_hours)
        self.cache: Dict[str, Tuple[SearchResult, datetime]] = {}
        self.query_cache: Dict[str, Tuple[List[SearchResult], datetime]] = {}
        self.access_times: Dict[str, datetime] = {}
        self.hit_count = 0
        self.miss_count = 0

    def _generate_key(self, query: SearchQuery) -> str:
        """Generate cache key for query."""
        key_data = {
            "text": query.text.lower(),
            "content_types": sorted([ct.value for ct in query.content_types]),
            "max_results": query.max_results,
            "time_range": query.time_range,
            "language": query.language,
            "region": query.region,
        }
        return hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()

    def get(self, query: SearchQuery) -> Optional[List[SearchResult]]:
        """Get cached results for query."""
        key = self._generate_key(query)
        if key in self.query_cache:
            results, timestamp = self.query_cache[key]
            if datetime.now() - timestamp < self.ttl:
                self.access_times[key] = datetime.now()
                self.hit_count += 1
                return results
            else:
                # Expired entry
                del self.query_cache[key]
                if key in self.access_times:
                    del self.access_times[key]

        self.miss_count += 1
        return None

    def put(self, query: SearchQuery, results: List[SearchResult]):
        """Cache results for query."""
        key = self._generate_key(query)

        # Remove old entries if cache is full
        if len(self.query_cache) >= self.max_size:
            self._evict_oldest()

        self.query_cache[key] = (results, datetime.now())
        self.access_times[key] = datetime.now()

    def _evict_oldest(self):
        """Evict oldest entries from cache."""
        if not self.access_times:
            return

        oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        del self.query_cache[oldest_key]
        del self.access_times[oldest_key]

    def get_hit_rate(self) -> float:
        """Get cache hit rate."""
        total = self.hit_count + self.miss_count
        return self.hit_count / total if total > 0 else 0.0

    def clear(self):
        """Clear all cache entries."""
        self.cache.clear()
        self.query_cache.clear()
        self.access_times.clear()
        self.hit_count = 0
        self.miss_count = 0


class RateLimiter:
    """Advanced rate limiting for search providers."""

    def __init__(self, requests_per_second: float, burst_size: int = 10):
        self.requests_per_second = requests_per_second
        self.burst_size = burst_size
        self.tokens = burst_size
        self.last_update = time.time()
        self.lock = asyncio.Lock()

    async def acquire(self) -> bool:
        """Acquire token for request."""
        async with self.lock:
            now = time.time()
            time_passed = now - self.last_update
            self.tokens = min(
                self.burst_size, self.tokens + time_passed * self.requests_per_second
            )
            self.last_update = now

            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False

    async def wait_for_token(self):
        """Wait until token is available."""
        while not await self.acquire():
            await asyncio.sleep(0.1)


# Initialize global components
search_cache = SearchCache()
global_metrics = SearchMetrics()
