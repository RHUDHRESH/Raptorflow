"""
Unified Search API
Consolidates: free_web_search.py, production_search_service.py
Single endpoint for web search with all production features.
"""

from __future__ import annotations

import asyncio
import hashlib
import html
import json
import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from urllib.parse import quote_plus, urlparse

import httpx
import structlog
from bs4 import BeautifulSoup
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.ai.application.terminal_adapter import terminal_adapter
from backend.agents.compat import optional_gateway
from backend.agents.runtime.profiles import (
    intensity_profile,
    normalize_execution_mode,
    normalize_intensity,
)
from backend.config import settings
from backend.services.exceptions import ServiceUnavailableError


def _get_redis_client():
    from backend.core.cache.redis import get_redis_client

    return get_redis_client()


# For production: use the actual function
# For testing: the public API module patches this
_get_redis_client_ref = _get_redis_client


def _lookup_redis_client():
    """Look up get_redis_client from the module namespace for testability.

    This allows tests to patch search_api.get_redis_client and have it
    take effect in the routes module.
    """
    import sys

    search_module = sys.modules.get("backend.api.v1.search")
    if search_module and hasattr(search_module, "get_redis_client"):
        patched = search_module.get_redis_client  # Don't call yet
        # Avoid infinite recursion: if the patched function is ourselves, use fallback
        if patched is not _lookup_redis_client:
            return patched()  # Now call it
    # Fallback to default implementation
    return _get_redis_client_ref()


# Use the lookup function for testability
get_redis_client = _lookup_redis_client


def _get_vertex_ai_service():
    """Get the vertex AI service for backward compatibility."""
    from backend.services.vertex_ai_service import vertex_ai_service

    return vertex_ai_service


_vertex_ai_service_ref = _get_vertex_ai_service


def _lookup_vertex_ai_service():
    """Look up vertex_ai_service from the module namespace for testability.

    This allows tests to patch backend.services.vertex_ai_service.vertex_ai_service
    and have it take effect in the routes module.
    """
    import sys

    vertex_module = sys.modules.get("backend.services.vertex_ai_service")
    if vertex_module and hasattr(vertex_module, "vertex_ai_service"):
        patched = vertex_module.vertex_ai_service
        # Avoid infinite recursion: if the patched function is ourselves, use fallback
        if patched is not _lookup_vertex_ai_service:
            return patched
    # Fallback to default implementation
    return _vertex_ai_service_ref()


# Use the lookup function for testability
get_vertex_ai_service = _lookup_vertex_ai_service


logger = structlog.get_logger()


logger = structlog.get_logger()

router = APIRouter(prefix="/search", tags=["search"])

# Search engines supported
SearchEngine = Literal["duckduckgo", "brave", "searx", "startpage", "qwant"]


def _redis_key_prefix() -> str:
    prefix = (settings.REDIS_KEY_PREFIX or "raptorflow:").strip()
    if prefix and not prefix.endswith(":"):
        prefix = f"{prefix}:"
    return prefix


class SearchResult(BaseModel):
    """Standardized search result"""

    title: str
    url: str
    snippet: str
    source: str
    timestamp: str
    relevance_score: float = 0.0


class UnifiedSearchEngine:
    """Unified search engine with all providers"""

    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "DNT": "1",
                "Connection": "keep-alive",
            },
        )

        self.search_engines = {
            "duckduckgo": self._search_duckduckgo,
            "brave": self._search_brave,
            "searx": self._search_searx,
            "startpage": self._search_startpage,
            "qwant": self._search_qwant,
        }

    def _build_cache_key(self, query: str, engines: List[str], max_results: int) -> str:
        payload = {
            "query": (query or "").strip().lower(),
            "engines": sorted(engines),
            "max_results": int(max_results),
            "schema": "search.v1",
        }
        digest = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        return f"{_redis_key_prefix()}search:results:{digest}"

    def _cache_ttl_seconds(self) -> int:
        return max(60, min(int(settings.REDIS_DEFAULT_TTL or 1800), 7200))

    def _get_cached_response(
        self,
        query: str,
        engines: List[str],
        max_results: int,
    ) -> Optional[Dict[str, Any]]:
        redis = get_redis_client()
        if not redis:
            return None

        cache_key = self._build_cache_key(query, engines, max_results)
        try:
            raw = redis.get(cache_key)
            if not raw:
                return None
            text = raw.decode("utf-8") if isinstance(raw, bytes) else str(raw)
            data = json.loads(text)
            if isinstance(data, dict) and isinstance(data.get("results"), list):
                data["cache"] = {"hit": True, "provider": "upstash_redis"}
                return data
        except Exception as exc:
            logger.warning("Search cache read failed", error=str(exc))
        return None

    def _set_cached_response(
        self,
        query: str,
        engines: List[str],
        max_results: int,
        payload: Dict[str, Any],
    ) -> None:
        redis = get_redis_client()
        if not redis:
            return

        cache_key = self._build_cache_key(query, engines, max_results)
        cache_payload = {k: v for k, v in payload.items() if k != "cache"}
        try:
            redis.set(
                cache_key,
                json.dumps(cache_payload, ensure_ascii=False, separators=(",", ":")),
                ex=self._cache_ttl_seconds(),
            )
        except Exception as exc:
            logger.warning("Search cache write failed", error=str(exc))

    async def search(
        self,
        query: str,
        engines: List[str],
        max_results: int = 20,
        enable_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Search across multiple engines with unified results

        Args:
            query: Search query
            engines: List of engine names to use
            max_results: Maximum results per engine
            enable_cache: Whether to cache results

        Returns:
            Combined search results with metadata
        """
        start_time = datetime.now(timezone.utc)

        logger.info(
            "Starting search", query=query, engines=engines, max_results=max_results
        )

        valid_engines = [e for e in engines if e in self.search_engines]
        if enable_cache and valid_engines:
            cached = self._get_cached_response(query, valid_engines, max_results)
            if cached:
                return cached

        all_results = []
        engine_stats = {}

        # Search each engine concurrently
        tasks = []
        for engine in valid_engines:
            tasks.append(self._search_engine_safe(engine, query, max_results))

        if tasks:
            engine_results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, result in enumerate(engine_results):
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
            "response_time": total_time,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cache": {
                "hit": False,
                "provider": "upstash_redis" if enable_cache else "disabled",
            },
        }
        if enable_cache and valid_engines:
            self._set_cached_response(query, valid_engines, max_results, response)
        return response

    async def _search_engine_safe(
        self, engine: str, query: str, max_results: int
    ) -> Dict[str, Any]:
        """Safely search with an engine, handling errors"""
        try:
            start_time = datetime.now(timezone.utc)
            results = await self.search_engines[engine](query, max_results)
            results["response_time"] = (
                datetime.now(timezone.utc) - start_time
            ).total_seconds()
            return results
        except Exception as e:
            logger.error(f"Search engine {engine} failed", error=str(e))
            raise

    async def _search_duckduckgo(self, query: str, max_results: int) -> Dict[str, Any]:
        """Search DuckDuckGo"""
        url = f"https://html.duckduckgo.com/html/"
        params = {"q": query}

        try:
            response = await self.client.get(url, params=params)
            soup = BeautifulSoup(response.text, "html.parser")

            results = []
            result_divs = soup.find_all("div", class_="result")

            for result_div in result_divs[:max_results]:
                title_tag = result_div.find("a", class_="result__a")
                snippet_tag = result_div.find("a", class_="result__snippet")

                if title_tag:
                    title = self._clean_text(title_tag.get_text(strip=True))
                    url = title_tag.get("href", "")
                    snippet = (
                        self._clean_text(snippet_tag.get_text(strip=True))
                        if snippet_tag
                        else ""
                    )

                    results.append(
                        {
                            "title": title,
                            "url": self._clean_url(url),
                            "snippet": snippet,
                            "source": "duckduckgo",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "relevance_score": 0.8,
                        }
                    )

            return {"results": results}

        except Exception as e:
            logger.error("DuckDuckGo search failed", error=str(e))
            return {"results": [], "error": str(e)}

    async def _search_brave(self, query: str, max_results: int) -> Dict[str, Any]:
        """Search Brave"""
        url = "https://search.brave.com/search"
        params = {"q": query}

        try:
            response = await self.client.get(url, params=params)
            soup = BeautifulSoup(response.text, "html.parser")

            results = []
            # Brave search results structure
            result_divs = soup.find_all("div", class_="snippet")

            for result_div in result_divs[:max_results]:
                title_tag = result_div.find("a")
                snippet_tag = result_div.find("span", class_="description")

                if title_tag:
                    title = self._clean_text(title_tag.get_text(strip=True))
                    url = title_tag.get("href", "")
                    snippet = (
                        self._clean_text(snippet_tag.get_text(strip=True))
                        if snippet_tag
                        else ""
                    )

                    results.append(
                        {
                            "title": title,
                            "url": self._clean_url(url),
                            "snippet": snippet,
                            "source": "brave",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "relevance_score": 0.75,
                        }
                    )

            return {"results": results}

        except Exception as e:
            logger.error("Brave search failed", error=str(e))
            return {"results": [], "error": str(e)}

    async def _search_searx(self, query: str, max_results: int) -> Dict[str, Any]:
        """Search Searx (meta-search)"""
        # Use a public Searx instance
        searx_instances = [
            "https://search.sapti.me",
            "https://search.bus-hit.me",
        ]

        for instance in searx_instances:
            try:
                url = f"{instance}/search"
                params = {"q": query, "format": "json"}

                response = await self.client.get(url, params=params, timeout=10.0)

                if response.status_code == 200:
                    data = response.json()
                    results = []

                    for result in data.get("results", [])[:max_results]:
                        results.append(
                            {
                                "title": self._clean_text(result.get("title", "")),
                                "url": self._clean_url(result.get("url", "")),
                                "snippet": self._clean_text(result.get("content", "")),
                                "source": "searx",
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                                "relevance_score": 0.85,
                            }
                        )

                    return {"results": results}

            except Exception as e:
                logger.warning(f"Searx instance {instance} failed", error=str(e))
                continue

        return {"results": [], "error": "All Searx instances failed"}

    async def _search_startpage(self, query: str, max_results: int) -> Dict[str, Any]:
        """Search Startpage"""
        url = "https://www.startpage.com/sp/search"
        params = {"query": query}

        try:
            response = await self.client.get(url, params=params)
            soup = BeautifulSoup(response.text, "html.parser")

            results = []
            result_divs = soup.find_all("div", class_="result")

            for result_div in result_divs[:max_results]:
                title_tag = result_div.find("a")
                snippet_tag = result_div.find("p", class_="text")

                if title_tag:
                    title = self._clean_text(title_tag.get_text(strip=True))
                    url = title_tag.get("href", "")
                    snippet = (
                        self._clean_text(snippet_tag.get_text(strip=True))
                        if snippet_tag
                        else ""
                    )

                    results.append(
                        {
                            "title": title,
                            "url": self._clean_url(url),
                            "snippet": snippet,
                            "source": "startpage",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "relevance_score": 0.8,
                        }
                    )

            return {"results": results}

        except Exception as e:
            logger.error("Startpage search failed", error=str(e))
            return {"results": [], "error": str(e)}

    async def _search_qwant(self, query: str, max_results: int) -> Dict[str, Any]:
        """Search Qwant"""
        url = "https://www.qwant.com/results"
        params = {"q": query, "t": "web"}

        try:
            response = await self.client.get(url, params=params)
            soup = BeautifulSoup(response.text, "html.parser")

            results = []
            result_divs = soup.find_all("div", class_="result")

            for result_div in result_divs[:max_results]:
                title_tag = result_div.find("a", class_="result--web")
                snippet_tag = result_div.find("p", class_="result__desc")

                if title_tag:
                    title = self._clean_text(title_tag.get_text(strip=True))
                    url = title_tag.get("href", "")
                    snippet = (
                        self._clean_text(snippet_tag.get_text(strip=True))
                        if snippet_tag
                        else ""
                    )

                    results.append(
                        {
                            "title": title,
                            "url": self._clean_url(url),
                            "snippet": snippet,
                            "source": "qwant",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "relevance_score": 0.75,
                        }
                    )

            return {"results": results}

        except Exception as e:
            logger.error("Qwant search failed", error=str(e))
            return {"results": [], "error": str(e)}

    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate results based on URL"""
        seen_urls = set()
        unique_results = []

        for result in results:
            url = result.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)

        return unique_results

    def _rank_results(self, results: List[Dict], query: str) -> List[Dict]:
        """Rank results by relevance"""
        query_terms = set(query.lower().split())

        for result in results:
            title = result.get("title", "").lower()
            snippet = result.get("snippet", "").lower()

            score = 0.0

            # Title matches
            title_terms = set(title.split())
            title_overlap = len(query_terms & title_terms)
            score += title_overlap * 0.3

            # Snippet matches
            snippet_terms = set(snippet.split())
            snippet_overlap = len(query_terms & snippet_terms)
            score += snippet_overlap * 0.1

            # Exact phrase match
            if query.lower() in title:
                score += 0.5
            elif query.lower() in snippet:
                score += 0.2

            result["relevance_score"] = min(score, 1.0)

        # Sort by relevance
        results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        return results

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""

        # Remove HTML entities
        text = html.unescape(text)

        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def _clean_url(self, url: str) -> str:
        """Clean URL by removing tracking parameters"""
        if not url:
            return ""

        try:
            parsed = urlparse(url)

            # Remove tracking parameters
            tracking_params = {
                "utm_source",
                "utm_medium",
                "utm_campaign",
                "utm_term",
                "utm_content",
                "fbclid",
                "gclid",
                "msclkid",
                "ref",
                "referrer",
                "source",
            }

            if parsed.query:
                query_params = []
                for param in parsed.query.split("&"):
                    if "=" in param:
                        key, value = param.split("=", 1)
                        if key not in tracking_params:
                            query_params.append(f"{key}={value}")

                clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                if query_params:
                    clean_url += "?" + "&".join(query_params)
                return clean_url

            return url
        except Exception:
            return url

    async def health_check(self) -> Dict[str, Any]:
        """Check health of all search engines"""
        health = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "engines": {},
        }

        for engine in self.search_engines.keys():
            try:
                # Quick test search
                start = datetime.now(timezone.utc)
                await self.search_engines[engine]("test", 1)
                duration = (datetime.now(timezone.utc) - start).total_seconds()

                health["engines"][engine] = {
                    "status": "healthy",
                    "response_time": duration,
                }
            except Exception as e:
                health["engines"][engine] = {"status": "unhealthy", "error": str(e)}

        # Overall status
        if any(e["status"] != "healthy" for e in health["engines"].values()):
            health["status"] = "degraded"

        return health


# Global search engine instance
search_engine = UnifiedSearchEngine()


async def _summarize_search_results(
    *,
    query: str,
    results: List[Dict[str, Any]],
    intensity: str,
    max_items: int,
) -> Dict[str, Any]:
    """Summarize search findings using AI when configured."""
    vertex_ai_service = get_vertex_ai_service()

    try:
        if hasattr(vertex_ai_service, "initialize"):
            await vertex_ai_service.initialize()
    except Exception:
        return {
            "status": "unavailable",
            "detail": "AI is not configured for summarization",
        }

    selected = results[:max_items]
    if not selected:
        return {"status": "empty", "detail": "No results to summarize"}

    compact_results = [
        {
            "title": item.get("title"),
            "url": item.get("url"),
            "snippet": item.get("snippet"),
            "source": item.get("source"),
            "relevance_score": item.get("relevance_score"),
        }
        for item in selected
    ]

    redis = get_redis_client()
    summary_cache_key: Optional[str] = None
    if redis:
        summary_payload = {
            "query": (query or "").strip().lower(),
            "intensity": intensity,
            "max_items": max_items,
            "results": [
                {
                    "url": item.get("url"),
                    "title": item.get("title"),
                    "snippet": item.get("snippet"),
                }
                for item in compact_results
            ],
            "schema": "search.summary.v1",
        }
        digest = hashlib.sha256(
            json.dumps(summary_payload, sort_keys=True, separators=(",", ":")).encode(
                "utf-8"
            )
        ).hexdigest()
        summary_cache_key = f"{_redis_key_prefix()}search:summary:{digest}"
        try:
            raw = redis.get(summary_cache_key)
            if raw:
                text = raw.decode("utf-8") if isinstance(raw, bytes) else str(raw)
                cached = json.loads(text)
                if isinstance(cached, dict):
                    cached["cache_hit"] = True
                    return cached
        except Exception as exc:
            logger.warning("Search summary cache read failed", error=str(exc))

    prompt = (
        "You are a research analyst.\n"
        f"Query: {query}\n"
        f"Intensity: {intensity}\n\n"
        "Using the search results below, produce:\n"
        "1) a 5-7 bullet summary,\n"
        "2) top risks or blind spots,\n"
        "3) three next queries.\n\n"
        f"Results JSON:\n{json.dumps(compact_results, ensure_ascii=False)}"
    )
    response = await vertex_ai_service.generate_text(
        prompt=prompt,
        workspace_id="search-system",
        user_id="search-summarizer",
        max_tokens=900,
        temperature=0.3,
    )
    if response.get("status") != "success":
        return {
            "status": "error",
            "detail": response.get("error", "Summarization failed"),
        }

    summary = {
        "status": "success",
        "text": response.get("text", ""),
        "model": response.get("model", "unknown"),
        "tokens_used": response.get("total_tokens", 0),
        "cost_usd": response.get("cost_usd", 0.0),
        "cache_hit": False,
    }
    if redis and summary_cache_key:
        try:
            cache_payload = {k: v for k, v in summary.items() if k != "cache_hit"}
            redis.set(
                summary_cache_key,
                json.dumps(cache_payload, ensure_ascii=False, separators=(",", ":")),
                ex=max(300, min(int(settings.REDIS_DEFAULT_TTL or 900), 3600)),
            )
        except Exception as exc:
            logger.warning("Search summary cache write failed", error=str(exc))
    return summary


# API Endpoints
@router.get("/")
async def search_endpoint(
    q: str = Query(..., description="Search query"),
    engines: Optional[str] = Query(None, description="Comma-separated list of engines"),
    max_results: Optional[int] = Query(
        None, ge=1, le=100, description="Maximum results per engine"
    ),
    intensity: Optional[Literal["low", "medium", "high"]] = Query(
        None, description="Search intensity profile"
    ),
    execution_mode: Optional[Literal["single", "council", "swarm"]] = Query(
        None, description="Execution mode metadata for optional graph orchestration"
    ),
    summarize: bool = Query(
        True, description="Generate a Vertex AI summary over top results"
    ),
    enable_cache: bool = Query(True, description="Enable result caching"),
):
    """
    Free web search across multiple engines

    - **q**: Search query (required)
    - **engines**: Comma-separated list of engines (duckduckgo,brave,searx,startpage,qwant)
    - **max_results**: Maximum results per engine (1-100)
    - **enable_cache**: Whether to cache results

    Returns combined results with deduplication and ranking.
    """
    runtime_intensity = normalize_intensity(intensity)
    runtime_execution_mode = normalize_execution_mode(execution_mode)
    profile = intensity_profile(runtime_intensity).get("search") or {}

    if engines:
        engine_list = [e.strip() for e in engines.split(",") if e.strip()]
    else:
        engine_list = list(profile.get("default_engines") or ["duckduckgo", "brave"])

    if max_results is None:
        max_results = int(profile.get("max_results") or 20)

    # Validate engines
    valid_engines = ["duckduckgo", "brave", "searx", "startpage", "qwant"]
    invalid = [e for e in engine_list if e not in valid_engines]
    if invalid:
        raise HTTPException(status_code=400, detail=f"Invalid engines: {invalid}")

    try:
        payload = {
            "q": q,
            "engines": engine_list,
            "max_results": max_results,
            "enable_cache": enable_cache,
            "intensity": runtime_intensity,
            "execution_mode": runtime_execution_mode,
        }
        result = await optional_gateway.run(
            operation="search",
            payload=payload,
            executor=lambda: search_engine.search(
                q, engine_list, max_results, enable_cache
            ),
        )
        hub = await terminal_adapter.run_optional_module(
            workspace_id="system",
            intent="search.query",
            payload=payload,
            precomputed_result=result,
        )
        result["hub"] = hub.to_dict()
        result["search_profile"] = {
            "intensity": runtime_intensity,
            "execution_mode": runtime_execution_mode,
            "engines": engine_list,
            "max_results": max_results,
        }
        if summarize:
            result["summary"] = await _summarize_search_results(
                query=q,
                results=result.get("results") or [],
                intensity=runtime_intensity,
                max_items=int(profile.get("summary_results") or 6),
            )
        return result
    except ServiceUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error("Search failed", query=q, error=str(e))
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/health")
async def search_health():
    """Health check for search engines"""
    return await search_engine.health_check()


@router.get("/engines")
async def list_engines():
    """List available search engines"""
    descriptions = {
        "duckduckgo": "Privacy-focused search with instant answers",
        "brave": "Privacy-focused search engine",
        "searx": "Meta-search engine (multiple instances)",
        "startpage": "Privacy-focused search using Google results",
        "qwant": "European search engine",
    }

    return {
        "engines": list(search_engine.search_engines.keys()),
        "descriptions": descriptions,
        "features": {
            "free": True,
            "unlimited": True,
            "no_api_keys_required": True,
            "multi_engine": True,
            "deduplication": True,
            "ranking": True,
            "intensity_profiles": ["low", "medium", "high"],
            "vertex_summary": True,
        },
    }


@router.get("/status")
async def search_status():
    """Service status and information"""
    return {
        "service": "Unified Web Search API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "engines_available": len(search_engine.search_engines),
        "features": [
            "free_web_search",
            "multiple_engines",
            "result_deduplication",
            "relevance_ranking",
            "no_api_keys",
            "privacy_focused",
            "intensity_profiles",
            "vertex_summary",
        ],
        "execution_modes": ["single", "council", "swarm"],
        "default_execution_mode": normalize_execution_mode(settings.AI_EXECUTION_MODE),
        "default_intensity": normalize_intensity(settings.AI_DEFAULT_INTENSITY),
    }
