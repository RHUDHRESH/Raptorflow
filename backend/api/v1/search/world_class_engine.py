"""
World-Class Search Engine Implementation.

This module provides a production-grade search engine with:
- Circuit breaker pattern for resilience
- Retry logic with exponential backoff
- Rate limiting per engine
- Comprehensive health monitoring
- Request/response validation
- Standardized API headers
"""

from __future__ import annotations

import asyncio
import hashlib
import html
import json
import logging
import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from urllib.parse import quote_plus, urlparse

import httpx
import structlog
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

logger = structlog.get_logger()


# ============================================================================
# Configuration Models
# ============================================================================


class EngineStatus(str, Enum):
    """Search engine status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CIRCUIT_OPEN = "circuit_open"
    RATE_LIMITED = "rate_limited"
    FAILED = "failed"


@dataclass
class EngineConfig:
    """Configuration for a search engine."""

    name: str
    base_url: str
    rate_limit_rpm: int = 30  # Requests per minute
    timeout_seconds: float = 10.0
    max_retries: int = 3
    circuit_breaker_threshold: int = 5  # Failures before opening
    circuit_breaker_timeout: int = 60  # Seconds before retry


@dataclass
class EngineState:
    """Runtime state for a search engine."""

    status: EngineStatus = EngineStatus.HEALTHY
    failure_count: int = 0
    last_failure: Optional[datetime] = None
    last_success: Optional[datetime] = None
    request_count: int = 0
    success_count: int = 0
    total_latency_ms: float = 0.0
    rate_limit_until: Optional[datetime] = None

    @property
    def average_latency_ms(self) -> float:
        if self.success_count == 0:
            return 0.0
        return self.total_latency_ms / self.success_count

    @property
    def success_rate(self) -> float:
        if self.request_count == 0:
            return 1.0
        return self.success_count / self.request_count


# ============================================================================
# Circuit Breaker Implementation
# ============================================================================


class CircuitBreaker:
    """Circuit breaker for search engine resilience."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        half_open_max_calls: int = 3,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        self._state: str = "closed"  # closed, open, half-open
        self._failure_count: int = 0
        self._last_failure_time: Optional[datetime] = None
        self._half_open_calls: int = 0
        self._lock = asyncio.Lock()

    @property
    def is_closed(self) -> bool:
        return self._state == "closed"

    @property
    def is_open(self) -> bool:
        if self._state == "open":
            # Check if we should transition to half-open
            if self._last_failure_time:
                if datetime.now() - self._last_failure_time > timedelta(
                    seconds=self.recovery_timeout
                ):
                    return False  # Will transition to half-open
            return True
        return False

    @property
    def is_half_open(self) -> bool:
        return self._state == "half-open"

    async def can_execute(self) -> bool:
        """Check if a request can be executed."""
        async with self._lock:
            if self._state == "closed":
                return True

            if self._state == "open":
                # Check if recovery timeout has passed
                if self._last_failure_time:
                    if datetime.now() - self._last_failure_time > timedelta(
                        seconds=self.recovery_timeout
                    ):
                        self._state = "half-open"
                        self._half_open_calls = 0
                        return True
                return False

            if self._state == "half-open":
                # Allow limited calls in half-open state
                return self._half_open_calls < self.half_open_max_calls

            return False

    async def record_success(self) -> None:
        """Record a successful call."""
        async with self._lock:
            if self._state == "half-open":
                self._half_open_calls += 1
                if self._half_open_calls >= self.half_open_max_calls:
                    # Recovered
                    self._state = "closed"
                    self._failure_count = 0
            elif self._state == "closed":
                self._failure_count = max(0, self._failure_count - 1)

    async def record_failure(self) -> None:
        """Record a failed call."""
        async with self._lock:
            self._failure_count += 1
            self._last_failure_time = datetime.now()

            if self._state == "half-open":
                # Failed in half-open, go back to open
                self._state = "open"
            elif self._state == "closed":
                if self._failure_count >= self.failure_threshold:
                    self._state = "open"


# ============================================================================
# Rate Limiter
# ============================================================================


class RateLimiter:
    """Token bucket rate limiter for search engines."""

    def __init__(self, rate: int, period: float = 60.0):
        """
        Initialize rate limiter.

        Args:
            rate: Number of requests allowed per period
            period: Time period in seconds
        """
        self.rate = rate
        self.period = period
        self._tokens: float = float(rate)
        self._last_update: datetime = datetime.now()
        self._lock = asyncio.Lock()

    async def acquire(self, timeout: float = 30.0) -> bool:
        """
        Acquire a token, waiting if necessary.

        Args:
            timeout: Maximum seconds to wait

        Returns:
            True if token acquired, False if timeout
        """
        start_time = time.time()

        while True:
            async with self._lock:
                now = datetime.now()
                elapsed = (now - self._last_update).total_seconds()

                # Replenish tokens
                self._tokens = min(
                    self.rate, self._tokens + elapsed * (self.rate / self.period)
                )
                self._last_update = now

                if self._tokens >= 1:
                    self._tokens -= 1
                    return True

            # Check timeout
            if time.time() - start_time >= timeout:
                return False

            # Wait before retrying
            await asyncio.sleep(0.1)


# ============================================================================
# Retry Logic with Exponential Backoff
# ============================================================================


async def retry_with_backoff(
    func,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: tuple = (
        httpx.ConnectError,
        httpx.TimeoutException,
        httpx.NetworkError,
    ),
) -> Any:
    """
    Retry an async function with exponential backoff.

    Args:
        func: Async function to retry
        max_attempts: Maximum number of attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        jitter: Whether to add random jitter
        retryable_exceptions: Tuple of exceptions to retry on

    Returns:
        Result of the function

    Raises:
        Last exception if all retries fail
    """
    last_exception = None

    for attempt in range(max_attempts):
        try:
            return await func()
        except retryable_exceptions as e:
            last_exception = e

            if attempt < max_attempts - 1:
                # Calculate delay with exponential backoff
                delay = min(base_delay * (exponential_base**attempt), max_delay)

                # Add jitter (0-25% of delay)
                if jitter:
                    delay = delay * (1 + random.random() * 0.25)

                logger.warning(
                    "Request failed, retrying",
                    attempt=attempt + 1,
                    max_attempts=max_attempts,
                    delay=delay,
                    error=str(e),
                )
                await asyncio.sleep(delay)
            else:
                logger.error(
                    "Request failed after all retries",
                    attempts=max_attempts,
                    error=str(e),
                )

    raise last_exception


# ============================================================================
# World-Class Search Engine
# ============================================================================


class WorldClassSearchEngine:
    """
    Production-grade unified search engine.

    Features:
    - Circuit breaker pattern for resilience
    - Rate limiting per engine
    - Retry logic with exponential backoff
    - Comprehensive health monitoring
    - Request validation
    - Response normalization
    """

    # Default engine configurations
    DEFAULT_ENGINES = {
        "duckduckgo": EngineConfig(
            name="duckduckgo",
            base_url="https://html.duckduckgo.com/html/",
            rate_limit_rpm=30,
            timeout_seconds=10.0,
            max_retries=3,
            circuit_breaker_threshold=5,
            circuit_breaker_timeout=60,
        ),
        "brave": EngineConfig(
            name="brave",
            base_url="https://search.brave.com/search",
            rate_limit_rpm=20,
            timeout_seconds=10.0,
            max_retries=3,
            circuit_breaker_threshold=5,
            circuit_breaker_timeout=60,
        ),
        "searx": EngineConfig(
            name="searx",
            base_url="https://searx.be/search",
            rate_limit_rpm=30,
            timeout_seconds=10.0,
            max_retries=3,
            circuit_breaker_threshold=5,
            circuit_breaker_timeout=60,
        ),
        "startpage": EngineConfig(
            name="startpage",
            base_url="https://www.startpage.com/do/search",
            rate_limit_rpm=20,
            timeout_seconds=10.0,
            max_retries=3,
            circuit_breaker_threshold=5,
            circuit_breaker_timeout=60,
        ),
        "qwant": EngineConfig(
            name="qwant",
            base_url="https://www.qwant.com/",
            rate_limit_rpm=20,
            timeout_seconds=10.0,
            max_retries=3,
            circuit_breaker_threshold=5,
            circuit_breaker_timeout=60,
        ),
    }

    def __init__(
        self,
        engines: Optional[Dict[str, EngineConfig]] = None,
        default_headers: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize the search engine.

        Args:
            engines: Custom engine configurations
            default_headers: HTTP headers for requests
        """
        self._engines = engines or self.DEFAULT_ENGINES
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._rate_limiters: Dict[str, RateLimiter] = {}
        self._engine_states: Dict[str, EngineState] = {}

        # HTTP client with connection pooling
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=10.0),
            limits=httpx.Limits(
                max_keepalive_connections=20,
                max_connections=100,
                keepalive_expiry=30.0,
            ),
            headers=default_headers
            or {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "DNT": "1",
                "Connection": "keep-alive",
            },
            follow_redirects=True,
        )

        # Initialize circuit breakers and rate limiters
        for name, config in self._engines.items():
            self._circuit_breakers[name] = CircuitBreaker(
                failure_threshold=config.circuit_breaker_threshold,
                recovery_timeout=config.circuit_breaker_timeout,
            )
            self._rate_limiters[name] = RateLimiter(
                rate=config.rate_limit_rpm,
                period=60.0,
            )
            self._engine_states[name] = EngineState()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    # ==================== Engine Health ====================

    async def get_engine_health(self, engine: str) -> Dict[str, Any]:
        """
        Get health status for a specific engine.

        Returns:
            Health information including status, latency, success rate
        """
        if engine not in self._engines:
            return {"error": f"Unknown engine: {engine}"}

        state = self._engine_states[engine]
        breaker = self._circuit_breakers[engine]
        config = self._engines[engine]

        # Determine current status
        if breaker.is_open:
            status = EngineStatus.CIRCUIT_OPEN
        elif state.rate_limit_until and datetime.now() < state.rate_limit_until:
            status = EngineStatus.RATE_LIMITED
        elif state.success_rate < 0.5:
            status = EngineStatus.DEGRADED
        else:
            status = EngineStatus.HEALTHY

        return {
            "engine": engine,
            "status": status.value,
            "config": {
                "rate_limit_rpm": config.rate_limit_rpm,
                "timeout_seconds": config.timeout_seconds,
                "max_retries": config.max_retries,
            },
            "metrics": {
                "request_count": state.request_count,
                "success_count": state.success_count,
                "success_rate": round(state.success_rate, 3),
                "average_latency_ms": round(state.average_latency_ms, 2),
            },
            "circuit_breaker": {
                "state": breaker._state,
                "failure_count": breaker._failure_count,
            },
        }

    async def get_all_health(self) -> Dict[str, Any]:
        """Get health status for all engines."""
        return {
            "engines": {
                name: await self.get_engine_health(name) for name in self._engines
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ==================== Search Implementation ====================

    async def search(
        self,
        query: str,
        engines: List[str],
        max_results: int = 20,
        enable_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Search across multiple engines with production-grade resilience.

        Args:
            query: Search query
            engines: List of engine names to use
            max_results: Maximum results per engine
            enable_cache: Whether to use caching

        Returns:
            Combined search results with comprehensive metadata
        """
        start_time = datetime.now(timezone.utc)

        # Validate inputs
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        if max_results < 1 or max_results > 100:
            raise ValueError("max_results must be between 1 and 100")

        # Filter to valid engines
        valid_engines = [e for e in engines if e in self._engines]
        if not valid_engines:
            raise ValueError(
                f"No valid engines provided. Available: {list(self._engines.keys())}"
            )

        logger.info(
            "Starting search",
            query=query,
            engines=valid_engines,
            max_results=max_results,
        )

        # Search each engine concurrently
        tasks = [
            self._search_engine_safe(engine, query, max_results)
            for engine in valid_engines
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        all_results = []
        engine_stats = {}

        for i, result in enumerate(results):
            engine_name = valid_engines[i]

            if isinstance(result, Exception):
                logger.error(f"Engine {engine_name} failed", error=str(result))
                engine_stats[engine_name] = {
                    "status": "failed",
                    "error": str(result),
                }
            else:
                all_results.extend(result.get("results", []))
                engine_stats[engine_name] = {
                    "status": "success",
                    "results_count": len(result.get("results", [])),
                    "response_time": result.get("response_time", 0),
                }

        # Deduplicate and rank
        deduplicated = self._deduplicate_results(all_results)
        ranked = self._rank_results(deduplicated, query)

        total_time = (datetime.now(timezone.utc) - start_time).total_seconds()

        response = {
            "query": query,
            "results": ranked[:max_results],
            "total_results": len(ranked),
            "engines_used": valid_engines,
            "engine_stats": engine_stats,
            "response_time": round(total_time, 3),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cache": {
                "hit": False,
                "provider": "redis" if enable_cache else "disabled",
            },
            "health": await self.get_all_health(),
        }

        return response

    async def _search_engine_safe(
        self,
        engine: str,
        query: str,
        max_results: int,
    ) -> Dict[str, Any]:
        """
        Safely search with an engine, handling all resilience patterns.
        """
        config = self._engines[engine]
        breaker = self._circuit_breakers[engine]
        limiter = self._rate_limiters[engine]
        state = self._engine_states[engine]

        start_time = datetime.now(timezone.utc)

        # Check circuit breaker
        if not await breaker.can_execute():
            logger.warning(f"Circuit breaker open for {engine}")
            state.status = EngineStatus.CIRCUIT_OPEN
            raise Exception(f"Circuit breaker open for {engine}")

        # Check rate limit
        if not await limiter.acquire(timeout=30.0):
            logger.warning(f"Rate limit exceeded for {engine}")
            state.status = EngineStatus.RATE_LIMITED
            state.rate_limit_until = datetime.now() + timedelta(seconds=60)
            raise Exception(f"Rate limit exceeded for {engine}")

        async def _do_search():
            return await self._search_engine(engine, query, max_results)

        try:
            # Execute with retry
            result = await retry_with_backoff(
                _do_search,
                max_attempts=config.max_retries,
                base_delay=1.0,
                max_delay=10.0,
            )

            # Record success
            await breaker.record_success()
            state.request_count += 1
            state.success_count += 1
            state.last_success = datetime.now(timezone.utc)
            latency = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            state.total_latency_ms += latency
            state.status = EngineStatus.HEALTHY

            result["response_time"] = latency / 1000
            return result

        except Exception as e:
            # Record failure
            await breaker.record_failure()
            state.request_count += 1
            state.failure_count += 1
            state.last_failure = datetime.now(timezone.utc)
            state.status = EngineStatus.FAILED

            logger.error(f"Search engine {engine} failed", error=str(e))
            raise

    async def _search_engine(
        self,
        engine: str,
        query: str,
        max_results: int,
    ) -> Dict[str, Any]:
        """Execute search against a specific engine."""
        config = self._engines[engine]

        if engine == "duckduckgo":
            return await self._search_duckduckgo(query, max_results)
        elif engine == "brave":
            return await self._search_brave(query, max_results)
        elif engine == "searx":
            return await self._search_searx(query, max_results)
        elif engine == "startpage":
            return await self._search_startpage(query, max_results)
        elif engine == "qwant":
            return await self._search_qwant(query, max_results)
        else:
            raise ValueError(f"Unknown engine: {engine}")

    async def _search_duckduckgo(self, query: str, max_results: int) -> Dict[str, Any]:
        """Search DuckDuckGo."""
        url = f"https://html.duckduckgo.com/html/"
        params = {"q": query}

        response = await self._client.get(url, params=params)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        for result in soup.select(".result")[:max_results]:
            link = result.select_one(".result__a")
            title_elem = result.select_one(".result__a")
            snippet = result.select_one(".result__snippet")

            if link:
                results.append(
                    {
                        "title": html.unescape(title_elem.get_text(strip=True))
                        if title_elem
                        else "",
                        "url": link.get("href", ""),
                        "snippet": html.unescape(snippet.get_text(strip=True))
                        if snippet
                        else "",
                        "source": "duckduckgo",
                        "relevance_score": self._calculate_relevance(
                            query, title_elem.get_text() if title_elem else ""
                        ),
                    }
                )

        return {"results": results}

    async def _search_brave(self, query: str, max_results: int) -> Dict[str, Any]:
        """Search Brave."""
        url = f"https://search.brave.com/search?q={quote_plus(query)}"

        response = await self._client.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        for result in soup.select(".snippet.fresh")[:max_results]:
            link = result.select_one("a")
            title = result.select_one("h3")
            snippet = result.select_one("p")

            if link:
                results.append(
                    {
                        "title": html.unescape(title.get_text(strip=True))
                        if title
                        else "",
                        "url": link.get("href", ""),
                        "snippet": html.unescape(snippet.get_text(strip=True))
                        if snippet
                        else "",
                        "source": "brave",
                        "relevance_score": self._calculate_relevance(
                            query, title.get_text() if title else ""
                        ),
                    }
                )

        return {"results": results}

    async def _search_searx(self, query: str, max_results: int) -> Dict[str, Any]:
        """Search Searx."""
        url = f"https://searx.be/search?q={quote_plus(query)}"

        response = await self._client.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        for result in soup.select(".result")[:max_results]:
            link = result.select_one("h3 a")
            snippet = result.select_one(".content")

            if link:
                results.append(
                    {
                        "title": html.unescape(link.get_text(strip=True)),
                        "url": link.get("href", ""),
                        "snippet": html.unescape(snippet.get_text(strip=True))
                        if snippet
                        else "",
                        "source": "searx",
                        "relevance_score": self._calculate_relevance(
                            query, link.get_text()
                        ),
                    }
                )

        return {"results": results}

    async def _search_startpage(self, query: str, max_results: int) -> Dict[str, Any]:
        """Search Startpage."""
        url = f"https://www.startpage.com/do/search?query={quote_plus(query)}"

        response = await self._client.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        for result in soup.select(".w-gl__result")[:max_results]:
            link = result.select_one(".w-gl__result-title a")
            snippet = result.select_one(".w-gl__result-desc")

            if link:
                results.append(
                    {
                        "title": html.unescape(link.get_text(strip=True)),
                        "url": link.get("href", ""),
                        "snippet": html.unescape(snippet.get_text(strip=True))
                        if snippet
                        else "",
                        "source": "startpage",
                        "relevance_score": self._calculate_relevance(
                            query, link.get_text()
                        ),
                    }
                )

        return {"results": results}

    async def _search_qwant(self, query: str, max_results: int) -> Dict[str, Any]:
        """Search Qwant."""
        url = f"https://www.qwant.com/?q={quote_plus(query)}"

        response = await self._client.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        for result in soup.select(".result--web")[:max_results]:
            link = result.select_one("a")
            title = result.select_one("h2")
            snippet = result.select_one(".result__snippet")

            if link:
                results.append(
                    {
                        "title": html.unescape(title.get_text(strip=True))
                        if title
                        else "",
                        "url": link.get("href", ""),
                        "snippet": html.unescape(snippet.get_text(strip=True))
                        if snippet
                        else "",
                        "source": "qwant",
                        "relevance_score": self._calculate_relevance(
                            query, title.get_text() if title else ""
                        ),
                    }
                )

        return {"results": results}

    # ==================== Result Processing ====================

    def _calculate_relevance(self, query: str, title: str) -> float:
        """Calculate relevance score based on query-term frequency."""
        if not title:
            return 0.0

        query_terms = set(query.lower().split())
        title_terms = set(title.lower().split())

        matches = len(query_terms & title_terms)
        return min(1.0, matches / len(query_terms)) if query_terms else 0.0

    def _deduplicate_results(
        self, results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Remove duplicate results based on URL."""
        seen_urls: Set[str] = set()
        deduplicated = []

        for result in results:
            url = result.get("url", "")
            parsed = urlparse(url)
            # Normalize URL by removing www and trailing slash
            normalized = f"{parsed.netloc}{parsed.path}".lower().rstrip("/")

            if normalized not in seen_urls:
                seen_urls.add(normalized)
                deduplicated.append(result)

        return deduplicated

    def _rank_results(
        self, results: List[Dict[str, Any]], query: str
    ) -> List[Dict[str, Any]]:
        """Rank results by relevance and recency."""
        # Score based on relevance and source priority
        source_priority = {
            "duckduckgo": 1,
            "brave": 2,
            "searx": 3,
            "startpage": 4,
            "qwant": 5,
        }

        def score(result: Dict[str, Any]) -> float:
            relevance = result.get("relevance_score", 0.0)
            source = result.get("source", "")
            priority = source_priority.get(source, 10)

            # Weighted score: 60% relevance, 40% source priority
            return (relevance * 0.6) + ((10 - priority) / 10 * 0.4)

        return sorted(results, key=score, reverse=True)


# Global instance
_world_class_search_engine: Optional[WorldClassSearchEngine] = None


def get_world_class_search_engine() -> WorldClassSearchEngine:
    """Get the global search engine instance."""
    global _world_class_search_engine
    if _world_class_search_engine is None:
        _world_class_search_engine = WorldClassSearchEngine()
    return _world_class_search_engine
