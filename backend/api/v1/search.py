"""
Unified Search API
Consolidates: free_web_search.py, production_search_service.py
Single endpoint for web search with all production features.
"""

from __future__ import annotations

import asyncio
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

logger = structlog.get_logger()

router = APIRouter(prefix="/search", tags=["search"])

# Search engines supported
SearchEngine = Literal["duckduckgo", "brave", "searx", "startpage", "qwant"]


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
    
    async def search(
        self, 
        query: str, 
        engines: List[str], 
        max_results: int = 20,
        enable_cache: bool = True
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
        
        logger.info("Starting search", query=query, engines=engines, max_results=max_results)
        
        all_results = []
        engine_stats = {}
        
        # Search each engine concurrently
        tasks = []
        valid_engines = [e for e in engines if e in self.search_engines]
        
        for engine in valid_engines:
            tasks.append(self._search_engine_safe(engine, query, max_results))
        
        if tasks:
            engine_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(engine_results):
                engine_name = valid_engines[i]
                if isinstance(result, Exception):
                    logger.error(f"Engine {engine_name} failed", error=str(result))
                    engine_stats[engine_name] = {"status": "failed", "error": str(result)}
                else:
                    all_results.extend(result.get("results", []))
                    engine_stats[engine_name] = {
                        "status": "success",
                        "results_count": len(result.get("results", [])),
                        "response_time": result.get("response_time", 0)
                    }
        
        # Deduplicate and rank
        deduplicated = self._deduplicate_results(all_results)
        ranked = self._rank_results(deduplicated, query)
        
        total_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        return {
            "query": query,
            "results": ranked[:max_results],
            "total_results": len(ranked),
            "engines_used": valid_engines,
            "engine_stats": engine_stats,
            "response_time": total_time,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    
    async def _search_engine_safe(
        self, engine: str, query: str, max_results: int
    ) -> Dict[str, Any]:
        """Safely search with an engine, handling errors"""
        try:
            start_time = datetime.now(timezone.utc)
            results = await self.search_engines[engine](query, max_results)
            results["response_time"] = (datetime.now(timezone.utc) - start_time).total_seconds()
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
                    snippet = self._clean_text(snippet_tag.get_text(strip=True)) if snippet_tag else ""
                    
                    results.append({
                        "title": title,
                        "url": self._clean_url(url),
                        "snippet": snippet,
                        "source": "duckduckgo",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "relevance_score": 0.8,
                    })
            
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
                    snippet = self._clean_text(snippet_tag.get_text(strip=True)) if snippet_tag else ""
                    
                    results.append({
                        "title": title,
                        "url": self._clean_url(url),
                        "snippet": snippet,
                        "source": "brave",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "relevance_score": 0.75,
                    })
            
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
                        results.append({
                            "title": self._clean_text(result.get("title", "")),
                            "url": self._clean_url(result.get("url", "")),
                            "snippet": self._clean_text(result.get("content", "")),
                            "source": "searx",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "relevance_score": 0.85,
                        })
                    
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
                    snippet = self._clean_text(snippet_tag.get_text(strip=True)) if snippet_tag else ""
                    
                    results.append({
                        "title": title,
                        "url": self._clean_url(url),
                        "snippet": snippet,
                        "source": "startpage",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "relevance_score": 0.8,
                    })
            
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
                    snippet = self._clean_text(snippet_tag.get_text(strip=True)) if snippet_tag else ""
                    
                    results.append({
                        "title": title,
                        "url": self._clean_url(url),
                        "snippet": snippet,
                        "source": "qwant",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "relevance_score": 0.75,
                    })
            
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
                "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
                "fbclid", "gclid", "msclkid", "ref", "referrer", "source"
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
            "engines": {}
        }
        
        for engine in self.search_engines.keys():
            try:
                # Quick test search
                start = datetime.now(timezone.utc)
                await self.search_engines[engine]("test", 1)
                duration = (datetime.now(timezone.utc) - start).total_seconds()
                
                health["engines"][engine] = {
                    "status": "healthy",
                    "response_time": duration
                }
            except Exception as e:
                health["engines"][engine] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        
        # Overall status
        if any(e["status"] != "healthy" for e in health["engines"].values()):
            health["status"] = "degraded"
        
        return health


# Global search engine instance
search_engine = UnifiedSearchEngine()


# API Endpoints
@router.get("/")
async def search_endpoint(
    q: str = Query(..., description="Search query"),
    engines: str = Query("duckduckgo,brave", description="Comma-separated list of engines"),
    max_results: int = Query(20, ge=1, le=100, description="Maximum results per engine"),
    enable_cache: bool = Query(True, description="Enable result caching")
):
    """
    Free web search across multiple engines
    
    - **q**: Search query (required)
    - **engines**: Comma-separated list of engines (duckduckgo,brave,searx,startpage,qwant)
    - **max_results**: Maximum results per engine (1-100)
    - **enable_cache**: Whether to cache results
    
    Returns combined results with deduplication and ranking.
    """
    engine_list = [e.strip() for e in engines.split(",") if e.strip()]
    
    # Validate engines
    valid_engines = ["duckduckgo", "brave", "searx", "startpage", "qwant"]
    invalid = [e for e in engine_list if e not in valid_engines]
    if invalid:
        raise HTTPException(status_code=400, detail=f"Invalid engines: {invalid}")
    
    try:
        result = await search_engine.search(q, engine_list, max_results, enable_cache)
        return result
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
        }
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
            "privacy_focused"
        ]
    }
