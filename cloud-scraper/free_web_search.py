"""
Free & Unlimited Web Search Service
Integrates DuckDuckGo, Brave, and other free search engines
No API keys, no rate limits, completely free
"""

import asyncio
import html
import json
import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus, urlencode, urlparse

import httpx
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    source: str
    timestamp: str
    relevance_score: float


class FreeWebSearchEngine:
    """Free web search using multiple engines without API keys"""

    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            },
        )

        self.search_engines = {
            "duckduckgo": self._search_duckduckgo,
            "brave": self._search_brave,
            "searx": self._search_searx,
            "startpage": self._search_startpage,
            "qwant": self._search_qwant,
        }

    async def search(
        self, query: str, engines: List[str] = None, max_results: int = 20
    ) -> Dict[str, Any]:
        """
        Search across multiple free engines

        Args:
            query: Search query
            engines: List of engines to use (default: all)
            max_results: Maximum results per engine

        Returns:
            Combined search results with metadata
        """
        if not engines:
            engines = list(self.search_engines.keys())

        logger.info(
            f"Starting free web search",
            query=query,
            engines=engines,
            max_results=max_results,
        )

        start_time = datetime.now(timezone.utc)
        all_results = []
        engine_stats = {}

        # Search each engine concurrently
        tasks = []
        for engine in engines:
            if engine in self.search_engines:
                tasks.append(self._search_engine_safe(engine, query, max_results))

        if tasks:
            engine_results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, result in enumerate(engine_results):
                engine_name = engines[i]
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

        # Remove duplicates and rank
        unique_results = self._deduplicate_results(all_results)
        ranked_results = self._rank_results(unique_results, query)

        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()

        return {
            "query": query,
            "engines_used": engines,
            "total_results": len(ranked_results),
            "processing_time": processing_time,
            "engine_stats": engine_stats,
            "results": ranked_results[:max_results],
            "metadata": {
                "search_type": "free_web_search",
                "no_api_keys_required": True,
                "unlimited_requests": True,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        }

    async def _search_engine_safe(
        self, engine: str, query: str, max_results: int
    ) -> Dict[str, Any]:
        """Safely search a single engine with error handling"""
        try:
            return await self.search_engines[engine](query, max_results)
        except Exception as e:
            logger.error(f"Search engine {engine} failed", query=query, error=str(e))
            raise

    async def _search_duckduckgo(self, query: str, max_results: int) -> Dict[str, Any]:
        """Search DuckDuckGo (instant answers + web results)"""
        start_time = datetime.now(timezone.utc)

        # DuckDuckGo instant answer API (free, no key required)
        instant_url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json&no_html=1&skip_disambig=1"

        try:
            response = await self.client.get(instant_url)
            instant_data = response.json()

            results = []

            # Add instant answer if available
            if instant_data.get("Abstract") or instant_data.get("AbstractText"):
                results.append(
                    SearchResult(
                        title=instant_data.get("Heading", query),
                        url=instant_data.get("AbstractURL", ""),
                        snippet=instant_data.get(
                            "Abstract", instant_data.get("AbstractText", "")
                        ),
                        source="duckduckgo_instant",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        relevance_score=1.0,
                    )
                )

            # Get traditional web results via HTML parsing
            html_url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
            html_response = await self.client.get(html_url)
            soup = BeautifulSoup(html_response.text, "html.parser")

            # Parse web results
            web_results = soup.find_all("div", class_="result")
            for result in web_results[: max_results - len(results)]:
                title_tag = result.find("a", class_="result__a")
                snippet_tag = result.find("a", class_="result__snippet")

                if title_tag:
                    title = title_tag.get_text(strip=True)
                    url = title_tag.get("href", "")
                    snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""

                    results.append(
                        SearchResult(
                            title=self._clean_text(title),
                            url=self._clean_url(url),
                            snippet=self._clean_text(snippet),
                            source="duckduckgo_web",
                            timestamp=datetime.now(timezone.utc).isoformat(),
                            relevance_score=0.8,
                        )
                    )

            return {
                "results": [r.dict() for r in results],
                "response_time": (
                    datetime.now(timezone.utc) - start_time
                ).total_seconds(),
            }

        except Exception as e:
            logger.error("DuckDuckGo search failed", error=str(e))
            raise

    async def _search_brave(self, query: str, max_results: int) -> Dict[str, Any]:
        """Search Brave Search (free tier)"""
        start_time = datetime.now(timezone.utc)

        # Brave Search API (free tier, no key required for basic usage)
        url = f"https://search.brave.com/search?q={quote_plus(query)}&source=web"

        try:
            response = await self.client.get(url)
            soup = BeautifulSoup(response.text, "html.parser")

            results = []

            # Parse Brave search results
            web_results = soup.find_all("div", {"data-type": "web"})
            for result in web_results[:max_results]:
                title_tag = result.find("a")
                snippet_tag = result.find("div", class_="snippet-description")

                if title_tag:
                    title = title_tag.get_text(strip=True)
                    url = title_tag.get("href", "")
                    snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""

                    results.append(
                        SearchResult(
                            title=self._clean_text(title),
                            url=self._clean_url(url),
                            snippet=self._clean_text(snippet),
                            source="brave_search",
                            timestamp=datetime.now(timezone.utc).isoformat(),
                            relevance_score=0.85,
                        )
                    )

            return {
                "results": [r.dict() for r in results],
                "response_time": (
                    datetime.now(timezone.utc) - start_time
                ).total_seconds(),
            }

        except Exception as e:
            logger.error("Brave search failed", error=str(e))
            raise

    async def _search_searx(self, query: str, max_results: int) -> Dict[str, Any]:
        """Search using public SearX instances"""
        start_time = datetime.now(timezone.utc)

        # Use a public SearX instance
        searx_instances = [
            "https://searx.be",
            "https://searx.xyz",
            "https://searx.tiekoetter.com",
            "https://search.snopyta.org",
        ]

        for instance in searx_instances:
            try:
                url = f"{instance}/search"
                params = {
                    "q": query,
                    "format": "json",
                    "engines": "google,duckduckgo,bing,brave",
                }

                response = await self.client.get(url, params=params)
                data = response.json()

                results = []
                for item in data.get("results", [])[:max_results]:
                    results.append(
                        SearchResult(
                            title=self._clean_text(item.get("title", "")),
                            url=item.get("url", ""),
                            snippet=self._clean_text(item.get("content", "")),
                            source=f'searx_{instance.split("//")[1].split(".")[0]}',
                            timestamp=datetime.now(timezone.utc).isoformat(),
                            relevance_score=0.75,
                        )
                    )

                return {
                    "results": [r.dict() for r in results],
                    "response_time": (
                        datetime.now(timezone.utc) - start_time
                    ).total_seconds(),
                }

            except Exception as e:
                logger.warning(f"SearX instance {instance} failed", error=str(e))
                continue

        raise Exception("All SearX instances failed")

    async def _search_startpage(self, query: str, max_results: int) -> Dict[str, Any]:
        """Search StartPage (privacy-focused)"""
        start_time = datetime.now(timezone.utc)

        url = f"https://www.startpage.com/do/search"
        params = {"query": query, "cat": "web", "pl": "ext-ff", "extVersion": "1.3.0"}

        try:
            response = await self.client.get(url, params=params)
            soup = BeautifulSoup(response.text, "html.parser")

            results = []

            # Parse StartPage results
            result_divs = soup.find_all("div", class_="w-gl__result")
            for result_div in result_divs[:max_results]:
                title_tag = result_div.find("h3")
                link_tag = title_tag.find("a") if title_tag else None
                snippet_tag = result_div.find("p", class_="w-gl__description")

                if link_tag:
                    title = link_tag.get_text(strip=True)
                    url = link_tag.get("href", "")
                    snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""

                    results.append(
                        SearchResult(
                            title=self._clean_text(title),
                            url=self._clean_url(url),
                            snippet=self._clean_text(snippet),
                            source="startpage",
                            timestamp=datetime.now(timezone.utc).isoformat(),
                            relevance_score=0.8,
                        )
                    )

            return {
                "results": [r.dict() for r in results],
                "response_time": (
                    datetime.now(timezone.utc) - start_time
                ).total_seconds(),
            }

        except Exception as e:
            logger.error("StartPage search failed", error=str(e))
            raise

    async def _search_qwant(self, query: str, max_results: int) -> Dict[str, Any]:
        """Search Qwant (European search engine)"""
        start_time = datetime.now(timezone.utc)

        url = f"https://www.qwant.com/results/"
        params = {"q": query, "t": "web"}

        try:
            response = await self.client.get(url, params=params)
            soup = BeautifulSoup(response.text, "html.parser")

            results = []

            # Parse Qwant results
            result_divs = soup.find_all("div", class_="result")
            for result_div in result_divs[:max_results]:
                title_tag = result_div.find("a", class_="result--web")
                snippet_tag = result_div.find("p", class_="result__desc")

                if title_tag:
                    title = title_tag.get_text(strip=True)
                    url = title_tag.get("href", "")
                    snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""

                    results.append(
                        SearchResult(
                            title=self._clean_text(title),
                            url=self._clean_url(url),
                            snippet=self._clean_text(snippet),
                            source="qwant",
                            timestamp=datetime.now(timezone.utc).isoformat(),
                            relevance_score=0.75,
                        )
                    )

            return {
                "results": [r.dict() for r in results],
                "response_time": (
                    datetime.now(timezone.utc) - start_time
                ).total_seconds(),
            }

        except Exception as e:
            logger.error("Qwant search failed", error=str(e))
            raise

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
        """Rank results by relevance to query"""
        query_terms = set(query.lower().split())

        for result in results:
            title = result.get("title", "").lower()
            snippet = result.get("snippet", "").lower()

            # Calculate relevance score
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

        # Sort by relevance score
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

        # Remove special characters but keep basic punctuation
        text = re.sub(r"[^\w\s.,!?;:()-]", "", text)

        return text.strip()

    def _clean_url(self, url: str) -> str:
        """Clean and normalize URL"""
        if not url:
            return ""

        # Remove tracking parameters
        parsed = urlparse(url)

        # Common tracking parameters to remove
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

        query_params = []
        if parsed.query:
            for param in parsed.query.split("&"):
                if "=" in param:
                    key, value = param.split("=", 1)
                    if key not in tracking_params:
                        query_params.append(f"{key}={value}")

        # Rebuild URL
        clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if query_params:
            clean_url += "?" + "&".join(query_params)

        return clean_url

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Global search engine instance
free_search_engine = FreeWebSearchEngine()

# FastAPI app
app = FastAPI(title="Free Web Search API", version="1.0.0")


@app.get("/search")
async def search_web(
    q: str = Query(..., description="Search query"),
    engines: str = Query(
        "duckduckgo,brave,searx", description="Comma-separated list of engines"
    ),
    max_results: int = Query(
        20, ge=1, le=100, description="Maximum results per engine"
    ),
):
    """
    Free web search across multiple engines

    - **q**: Search query (required)
    - **engines**: Comma-separated list of engines (duckduckgo,brave,searx,startpage,qwant)
    - **max_results**: Maximum results per engine (1-100)

    Returns combined results from all specified engines with deduplication and ranking.
    """

    engine_list = [e.strip() for e in engines.split(",") if e.strip()]

    try:
        result = await free_search_engine.search(q, engine_list, max_results)
        return result
    except Exception as e:
        logger.error("Search failed", query=q, error=str(e))
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/search/engines")
async def list_engines():
    """List available search engines"""
    return {
        "engines": list(free_search_engine.search_engines.keys()),
        "description": {
            "duckduckgo": "Privacy-focused search with instant answers",
            "brave": "Privacy-focused search engine",
            "searx": "Meta-search engine (multiple instances)",
            "startpage": "Privacy-focused search using Google results",
            "qwant": "European search engine",
        },
        "features": {
            "free": True,
            "unlimited": True,
            "no_api_keys_required": True,
            "no_rate_limits": True,
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "engines_available": len(free_search_engine.search_engines),
        "features": [
            "free_web_search",
            "multiple_engines",
            "deduplication",
            "relevance_ranking",
            "no_api_keys",
            "unlimited_requests",
        ],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8084)
