"""
Raptorflow Web Search Tool
===========================

Comprehensive web search tool for the Raptorflow AI agent system.
Supports multiple search engines, advanced filtering, and result processing.

Features:
- Multiple search engine support (Google, Bing, DuckDuckGo)
- Advanced search filtering and options
- Result ranking and relevance scoring
- Search history and caching
- Rate limiting and API management
- Result summarization and analysis
- Safe search and content filtering
- Custom search parameters
"""

import asyncio
import json
import re
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from urllib.parse import parse_qs, urlencode, urlparse

# External imports
import httpx
import structlog
from bs4 import BeautifulSoup

from ..config import settings

# Local imports
from .base import ToolError, ToolResult, ToolStatus, ToolTimeoutError, WebTool

logger = structlog.get_logger(__name__)


class SearchEngine(str, Enum):
    """Supported search engines."""

    GOOGLE = "google"
    BING = "bing"
    DUCKDUCKGO = "duckduckgo"
    CUSTOM = "custom"


class SearchType(str, Enum):
    """Search types."""

    WEB = "web"
    NEWS = "news"
    IMAGES = "images"
    VIDEOS = "videos"
    SHOPPING = "shopping"
    BOOKS = "books"
    MAPS = "maps"


class SafeSearchLevel(str, Enum):
    """Safe search levels."""

    OFF = "off"
    MEDIUM = "medium"
    STRICT = "strict"


@dataclass
class SearchQuery:
    """Search query configuration."""

    query: str
    engine: SearchEngine = SearchEngine.GOOGLE
    search_type: SearchType = SearchType.WEB
    language: str = "en"
    region: str = "us"
    num_results: int = 10
    safe_search: SafeSearchLevel = SafeSearchLevel.MEDIUM
    date_range: Optional[str] = None  # e.g., "d7" (last 7 days), "m1" (last month)
    site_filter: Optional[str] = None  # e.g., "site:example.com"
    file_type: Optional[str] = None  # e.g., "pdf", "doc"
    exclude_terms: List[str] = field(default_factory=list)
    include_terms: List[str] = field(default_factory=list)
    exact_phrase: Optional[str] = None
    custom_params: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResult:
    """Individual search result."""

    title: str
    url: str
    snippet: str
    position: int
    engine: SearchEngine
    relevance_score: float = 0.0
    published_date: Optional[datetime] = None
    author: Optional[str] = None
    language: Optional[str] = None
    file_type: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "position": self.position,
            "engine": self.engine.value,
            "relevance_score": self.relevance_score,
            "published_date": (
                self.published_date.isoformat() if self.published_date else None
            ),
            "author": self.author,
            "language": self.language,
            "file_type": self.file_type,
            "metadata": self.metadata,
        }


@dataclass
class SearchResponse:
    """Complete search response."""

    query: SearchQuery
    results: List[SearchResult]
    total_results: int
    search_time: float
    engine: SearchEngine
    search_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {
            "query": self.query.__dict__,
            "results": [result.to_dict() for result in self.results],
            "total_results": self.total_results,
            "search_time": self.search_time,
            "engine": self.engine.value,
            "search_id": self.search_id,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


class SearchEngineClient:
    """Base class for search engine clients."""

    def __init__(self, api_key: str = None, timeout: int = 30):
        self.api_key = api_key
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
        self.rate_limit_delay = 1.0

    async def search(self, query: SearchQuery) -> SearchResponse:
        """Execute search query."""
        raise NotImplementedError

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


class GoogleSearchClient(SearchEngineClient):
    """Google Custom Search API client."""

    def __init__(self, api_key: str, search_engine_id: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.search_engine_id = search_engine_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"

    async def search(self, query: SearchQuery) -> SearchResponse:
        """Execute Google search."""
        start_time = time.time()
        search_id = str(uuid.uuid4())

        try:
            # Build search parameters
            params = {
                "key": self.api_key,
                "cx": self.search_engine_id,
                "q": self._build_query_string(query),
                "num": min(query.num_results, 10),  # Google API limit
                "start": 0,
                "lr": f"lang_{query.language}",
                "gl": query.region,
                "safe": query.safe_search.value,
                "filter": "1" if query.date_range else "0",
            }

            # Add custom parameters
            params.update(query.custom_params)

            # Make API request
            response = await self.client.get(self.base_url, params=params)
            response.raise_for_status()

            data = response.json()

            # Parse results
            results = []
            for i, item in enumerate(data.get("items", []), 1):
                result = SearchResult(
                    title=item.get("title", ""),
                    url=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                    position=i,
                    engine=SearchEngine.GOOGLE,
                    relevance_score=self._calculate_relevance(item, query),
                    published_date=self._parse_date(
                        item.get("pagemap", {})
                        .get("metatags", [{}])[0]
                        .get("article:published_time")
                    ),
                    author=item.get("pagemap", {})
                    .get("metatags", [{}])[0]
                    .get("author"),
                    language=item.get("pagemap", {})
                    .get("metatags", [{}])[0]
                    .get("language"),
                    metadata={
                        "cache_id": item.get("cacheId"),
                        "formatted_url": item.get("formattedUrl"),
                        "html_title": item.get("htmlTitle"),
                        "html_snippet": item.get("htmlSnippet"),
                    },
                )
                results.append(result)

            search_time = time.time() - start_time

            return SearchResponse(
                query=query,
                results=results,
                total_results=data.get("searchInformation", {}).get("totalResults", 0),
                search_time=search_time,
                engine=SearchEngine.GOOGLE,
                search_id=search_id,
                metadata={
                    "search_information": data.get("searchInformation", {}),
                    "context": data.get("context", {}),
                },
            )

        except Exception as e:
            logger.error("Google search failed", error=str(e), query=query.query)
            raise ToolError(f"Google search failed: {e}", tool_name="WebSearchTool")

    def _build_query_string(self, query: SearchQuery) -> str:
        """Build Google search query string."""
        query_parts = [query.query]

        # Add exact phrase
        if query.exact_phrase:
            query_parts.append(f'"{query.exact_phrase}"')

        # Add site filter
        if query.site_filter:
            query_parts.append(query.site_filter)

        # Add include terms
        for term in query.include_terms:
            query_parts.append(term)

        # Add exclude terms
        for term in query.exclude_terms:
            query_parts.append(f"-{term}")

        # Add file type
        if query.file_type:
            query_parts.append(f"filetype:{query.file_type}")

        # Add date range
        if query.date_range:
            query_parts.append(f"after:{query.date_range}")

        return " ".join(query_parts)

    def _calculate_relevance(self, item: Dict[str, Any], query: SearchQuery) -> float:
        """Calculate relevance score for a result."""
        score = 0.0

        # Title relevance
        title = item.get("title", "").lower()
        query_terms = query.query.lower().split()

        for term in query_terms:
            if term in title:
                score += 0.3

        # Snippet relevance
        snippet = item.get("snippet", "").lower()
        for term in query_terms:
            if term in snippet:
                score += 0.2

        # Exact phrase bonus
        if query.exact_phrase:
            exact_phrase = query.exact_phrase.lower()
            if exact_phrase in title:
                score += 0.5
            if exact_phrase in snippet:
                score += 0.3

        return min(score, 1.0)

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string."""
        if not date_str:
            return None

        try:
            # Try ISO format first
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except:
            # Try other formats
            try:
                return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
            except:
                return None


class BingSearchClient(SearchEngineClient):
    """Bing Search API client."""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.base_url = "https://api.bing.microsoft.com/v7.0/search"

    async def search(self, query: SearchQuery) -> SearchResponse:
        """Execute Bing search."""
        start_time = time.time()
        search_id = str(uuid.uuid4())

        try:
            # Build search parameters
            params = {
                "q": self._build_query_string(query),
                "count": min(query.num_results, 50),  # Bing API limit
                "offset": 0,
                "mkt": query.region,
                "safeSearch": query.safe_search.value,
                "textFormat": "HTML",
                "setLang": query.language,
            }

            # Add custom parameters
            params.update(query.custom_params)

            # Make API request
            headers = {"Ocp-Apim-Subscription-Key": self.api_key}
            response = await self.client.get(
                self.base_url, params=params, headers=headers
            )
            response.raise_for_status()

            data = response.json()

            # Parse results
            results = []
            for i, item in enumerate(data.get("webPages", {}).get("value", []), 1):
                result = SearchResult(
                    title=item.get("name", ""),
                    url=item.get("url", ""),
                    snippet=item.get("snippet", ""),
                    position=i,
                    engine=SearchEngine.BING,
                    relevance_score=self._calculate_relevance(item, query),
                    published_date=self._parse_date(item.get("datePublished")),
                    author=item.get("author"),
                    language=item.get("language"),
                    metadata={
                        "display_url": item.get("displayUrl"),
                        "is_crawled": item.get("isCrawled"),
                        "is_family_friendly": item.get("isFamilyFriendly"),
                        "date_last_crawled": item.get("dateLastCrawled"),
                    },
                )
                results.append(result)

            search_time = time.time() - start_time

            return SearchResponse(
                query=query,
                results=results,
                total_results=data.get("webPages", {}).get("totalEstimatedMatches", 0),
                search_time=search_time,
                engine=SearchEngine.BING,
                search_id=search_id,
                metadata={
                    "ranking_rules": data.get("rankingRules", {}),
                    "query_context": data.get("queryContext", {}),
                },
            )

        except Exception as e:
            logger.error("Bing search failed", error=str(e), query=query.query)
            raise ToolError(f"Bing search failed: {e}", tool_name="WebSearchTool")

    def _build_query_string(self, query: SearchQuery) -> str:
        """Build Bing search query string."""
        query_parts = [query.query]

        # Add exact phrase
        if query.exact_phrase:
            query_parts.append(f'"{query.exact_phrase}"')

        # Add site filter
        if query.site_filter:
            query_parts.append(query.site_filter)

        # Add include terms
        for term in query.include_terms:
            query_parts.append(term)

        # Add exclude terms
        for term in query.exclude_terms:
            query_parts.append(f"-{term}")

        # Add file type
        if query.file_type:
            query_parts.append(f"filetype:{query.file_type}")

        # Add date range
        if query.date_range:
            query_parts.append(f"after:{query.date_range}")

        return " ".join(query_parts)

    def _calculate_relevance(self, item: Dict[str, Any], query: SearchQuery) -> float:
        """Calculate relevance score for a result."""
        score = 0.0

        # Title relevance
        title = item.get("name", "").lower()
        query_terms = query.query.lower().split()

        for term in query_terms:
            if term in title:
                score += 0.3

        # Snippet relevance
        snippet = item.get("snippet", "").lower()
        for term in query_terms:
            if term in snippet:
                score += 0.2

        # Exact phrase bonus
        if query.exact_phrase:
            exact_phrase = query.exact_phrase.lower()
            if exact_phrase in title:
                score += 0.5
            if exact_phrase in snippet:
                score += 0.3

        return min(score, 1.0)

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string."""
        if not date_str:
            return None

        try:
            # Try ISO format first
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except:
            # Try other formats
            try:
                return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
            except:
                return None


class DuckDuckGoSearchClient(SearchEngineClient):
    """DuckDuckGo search client (HTML parsing)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_url = "https://html.duckduckgo.com/html/"

    async def search(self, query: SearchQuery) -> SearchResponse:
        """Execute DuckDuckGo search."""
        start_time = time.time()
        search_id = str(uuid.uuid4())

        try:
            # Build search parameters
            params = {
                "q": self._build_query_string(query),
                "kl": query.region,
                "dl": query.language,
                "safe": query.safe_search.value,
            }

            # Add custom parameters
            params.update(query.custom_params)

            # Make request
            response = await self.client.get(self.base_url, params=params)
            response.raise_for_status()

            # Parse HTML results
            soup = BeautifulSoup(response.text, "html.parser")
            results = []

            # Find result divs
            result_divs = soup.find_all("div", class_="result")

            for i, div in enumerate(result_divs[: query.num_results], 1):
                title_tag = div.find("a", class_="result__a")
                snippet_tag = div.find("a", class_="result__snippet")

                if title_tag:
                    title = title_tag.get_text(strip=True)
                    url = title_tag.get("href", "")
                    snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""

                    result = SearchResult(
                        title=title,
                        url=url,
                        snippet=snippet,
                        position=i,
                        engine=SearchEngine.DUCKDUCKGO,
                        relevance_score=self._calculate_relevance(
                            title, snippet, query
                        ),
                        metadata={
                            "raw_html": str(div),
                        },
                    )
                    results.append(result)

            search_time = time.time() - start_time

            return SearchResponse(
                query=query,
                results=results,
                total_results=len(results),  # DuckDuckGo doesn't provide total count
                search_time=search_time,
                engine=SearchEngine.DUCKDUCKGO,
                search_id=search_id,
                metadata={
                    "html_source": response.text,
                },
            )

        except Exception as e:
            logger.error("DuckDuckGo search failed", error=str(e), query=query.query)
            raise ToolError(f"DuckDuckGo search failed: {e}", tool_name="WebSearchTool")

    def _build_query_string(self, query: SearchQuery) -> str:
        """Build DuckDuckGo search query string."""
        query_parts = [query.query]

        # Add exact phrase
        if query.exact_phrase:
            query_parts.append(f'"{query.exact_phrase}"')

        # Add site filter
        if query.site_filter:
            query_parts.append(query.site_filter)

        # Add include terms
        for term in query.include_terms:
            query_parts.append(term)

        # Add exclude terms
        for term in query.exclude_terms:
            query_parts.append(f"-{term}")

        # Add file type
        if query.file_type:
            query_parts.append(f"filetype:{query.file_type}")

        # Add date range
        if query.date_range:
            query_parts.append(f"after:{query.date_range}")

        return " ".join(query_parts)

    def _calculate_relevance(
        self, title: str, snippet: str, query: SearchQuery
    ) -> float:
        """Calculate relevance score for a result."""
        score = 0.0

        query_terms = query.query.lower().split()

        # Title relevance
        title_lower = title.lower()
        for term in query_terms:
            if term in title_lower:
                score += 0.3

        # Snippet relevance
        snippet_lower = snippet.lower()
        for term in query_terms:
            if term in snippet_lower:
                score += 0.2

        # Exact phrase bonus
        if query.exact_phrase:
            exact_phrase = query.exact_phrase.lower()
            if exact_phrase in title_lower:
                score += 0.5
            if exact_phrase in snippet_lower:
                score += 0.3

        return min(score, 1.0)


class WebSearchTool(WebTool):
    """Web search tool implementation."""

    NAME = "web_search"
    DESCRIPTION = "Search the web for information using multiple search engines"
    CATEGORY = ToolCategory.WEB_TOOLS
    VERSION = "1.0.0"
    AUTHOR = "Raptorflow Team"

    REQUIRED_CONFIG = []
    OPTIONAL_CONFIG = [
        "google_api_key",
        "google_search_engine_id",
        "bing_api_key",
        "default_engine",
        "max_results",
        "timeout",
        "rate_limit_delay",
    ]

    CAPABILITIES = [
        "web_search",
        "multi_engine",
        "advanced_filtering",
        "result_ranking",
        "search_history",
    ]

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)

        # Search engine clients
        self.clients = {}
        self.default_engine = SearchEngine(self.config.get("default_engine", "google"))
        self.max_results = self.config.get("max_results", 10)
        self.rate_limit_delay = self.config.get("rate_limit_delay", 1.0)

        # Initialize search engine clients
        self._initialize_clients()

    def _initialize_clients(self):
        """Initialize search engine clients."""
        # Google Search
        google_api_key = self.config.get("google_api_key")
        google_search_engine_id = self.config.get("google_search_engine_id")
        if google_api_key and google_search_engine_id:
            self.clients[SearchEngine.GOOGLE] = GoogleSearchClient(
                google_api_key, google_search_engine_id, timeout=self.timeout
            )

        # Bing Search
        bing_api_key = self.config.get("bing_api_key")
        if bing_api_key:
            self.clients[SearchEngine.BING] = BingSearchClient(
                bing_api_key, timeout=self.timeout
            )

        # DuckDuckGo (no API key required)
        self.clients[SearchEngine.DUCKDUCKGO] = DuckDuckGoSearchClient(
            timeout=self.timeout
        )

        logger.info(
            "Search engine clients initialized", engines=list(self.clients.keys())
        )

    async def _on_initialize(self):
        """Initialize the tool."""
        # Validate that at least one search engine is available
        if not self.clients:
            raise ToolConfigError("No search engines configured", tool_name=self.NAME)

        # Validate default engine
        if self.default_engine not in self.clients:
            logger.warning(
                f"Default engine {self.default_engine} not available, using fallback"
            )
            self.default_engine = list(self.clients.keys())[0]

    async def _execute(self, **kwargs) -> Dict[str, Any]:
        """Execute web search."""
        # Parse search query
        query = self._parse_search_query(kwargs)

        # Check if requested engine is available
        if query.engine not in self.clients:
            available_engines = list(self.clients.keys())
            raise ToolError(
                f"Search engine {query.engine} not available. Available: {available_engines}"
            )

        # Execute search with rate limiting
        await asyncio.sleep(self.rate_limit_delay)

        client = self.clients[query.engine]
        response = await client.search(query)

        # Process results
        processed_results = self._process_results(response)

        return {
            "search_id": response.search_id,
            "query": response.query.__dict__,
            "results": [result.to_dict() for result in processed_results],
            "total_results": response.total_results,
            "search_time": response.search_time,
            "engine": response.engine.value,
            "timestamp": response.timestamp.isoformat(),
            "metadata": response.metadata,
        }

    def _parse_search_query(self, kwargs: Dict[str, Any]) -> SearchQuery:
        """Parse search query from kwargs."""
        return SearchQuery(
            query=kwargs.get("query", ""),
            engine=SearchEngine(kwargs.get("engine", self.default_engine.value)),
            search_type=SearchType(kwargs.get("search_type", "web")),
            language=kwargs.get("language", "en"),
            region=kwargs.get("region", "us"),
            num_results=min(kwargs.get("num_results", self.max_results), 50),
            safe_search=SafeSearchLevel(kwargs.get("safe_search", "medium")),
            date_range=kwargs.get("date_range"),
            site_filter=kwargs.get("site_filter"),
            file_type=kwargs.get("file_type"),
            exclude_terms=kwargs.get("exclude_terms", []),
            include_terms=kwargs.get("include_terms", []),
            exact_phrase=kwargs.get("exact_phrase"),
            custom_params=kwargs.get("custom_params", {}),
            metadata=kwargs.get("metadata", {}),
        )

    def _process_results(self, response: SearchResponse) -> List[SearchResult]:
        """Process and rank search results."""
        results = response.results

        # Sort by relevance score
        results.sort(key=lambda x: x.relevance_score, reverse=True)

        # Update positions
        for i, result in enumerate(results, 1):
            result.position = i

        return results

    def _validate_input(self, input_data: Dict[str, Any]):
        """Validate input data."""
        super()._validate_input(input_data)

        query = input_data.get("query", "")
        if not query.strip():
            raise ToolValidationError(
                "Search query cannot be empty", tool_name=self.NAME
            )

        if len(query) > 1000:
            raise ToolValidationError(
                "Search query too long (max 1000 characters)", tool_name=self.NAME
            )

    async def search_multiple_engines(
        self, query: str, engines: List[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """Search across multiple engines and combine results."""
        engines = engines or [engine.value for engine in self.clients.keys()]

        all_results = []
        engine_responses = {}

        for engine_name in engines:
            try:
                engine = SearchEngine(engine_name)
                if engine in self.clients:
                    # Create query for this engine
                    search_query = SearchQuery(query=query, engine=engine, **kwargs)

                    # Execute search
                    client = self.clients[engine]
                    response = await client.search(search_query)

                    # Store response
                    engine_responses[engine_name] = response

                    # Add results with engine prefix
                    for result in response.results:
                        result.title = f"[{engine_name.upper()}] {result.title}"
                        all_results.append(result)

                    # Rate limiting between engines
                    await asyncio.sleep(self.rate_limit_delay)

            except Exception as e:
                logger.error(f"Search failed for engine {engine_name}", error=str(e))
                continue

        # Sort combined results by relevance
        all_results.sort(key=lambda x: x.relevance_score, reverse=True)

        # Update positions
        for i, result in enumerate(all_results[: self.max_results], 1):
            result.position = i

        return {
            "query": query,
            "engines": engines,
            "results": [result.to_dict() for result in all_results[: self.max_results]],
            "total_results": len(all_results),
            "engine_responses": {
                name: resp.to_dict() for name, resp in engine_responses.items()
            },
            "metadata": {
                "combined_search": True,
                "engines_searched": list(engine_responses.keys()),
            },
        }

    async def get_search_suggestions(self, query: str, engine: str = None) -> List[str]:
        """Get search suggestions (placeholder implementation)."""
        # This would require additional API integration
        # For now, return empty list
        return []

    async def cleanup(self):
        """Cleanup tool resources."""
        for client in self.clients.values():
            await client.close()
        self.clients.clear()


# Export main components
__all__ = [
    "WebSearchTool",
    "SearchQuery",
    "SearchResult",
    "SearchResponse",
    "SearchEngine",
    "SearchType",
    "SafeSearchLevel",
    "GoogleSearchClient",
    "BingSearchClient",
    "DuckDuckGoSearchClient",
]
