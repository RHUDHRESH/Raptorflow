"""
Part 2: Enhanced Search Providers Implementation
RaptorFlow Unified Search System - Industrial Grade AI Agent Search Infrastructure
===============================================================================
This module implements the enhanced search providers with advanced capabilities,
fault tolerance, and intelligent fallback mechanisms.
"""

import asyncio
import logging
import random
import re
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode, urlparse
import json

import aiohttp
import httpx
from bs4 import BeautifulSoup

from backend.core.unified_search_part1 import (
    BaseSearchProvider, SearchQuery, SearchResult, SearchProvider, ContentType,
    SearchMode, search_cache, RateLimiter
)

logger = logging.getLogger("raptorflow.unified_search.providers")


class EnhancedNativeSearchProvider(BaseSearchProvider):
    """Enhanced Native Search with multiple fallback mechanisms."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(SearchProvider.NATIVE, config)
        self.brave_api_key = config.get("brave_api_key")
        self.serper_api_key = config.get("serper_api_key")
        self.client = httpx.AsyncClient(timeout=15.0)
        self.rate_limiter = RateLimiter(requests_per_second=2.0)
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
        ]
        
    async def search(self, query: SearchQuery) -> List[SearchResult]:
        """Execute search with intelligent provider selection."""
        await self.rate_limiter.wait_for_token()
        start_time = time.time()
        
        try:
            # Try Brave first if available
            if self.brave_api_key and query.mode != SearchMode.LIGHTNING:
                results = await self._brave_search(query)
                if results:
                    self.update_metrics(True, (time.time() - start_time) * 1000)
                    return results
            
            # Fallback to DuckDuckGo
            results = await self._duckduckgo_search(query)
            if results:
                self.update_metrics(True, (time.time() - start_time) * 1000)
                return results
            
            # Final fallback to custom HTML scraping
            results = await self._html_fallback_search(query)
            self.update_metrics(bool(results), (time.time() - start_time) * 1000)
            return results
            
        except Exception as e:
            logger.error(f"Native search failed: {e}")
            self.update_metrics(False, (time.time() - start_time) * 1000)
            return []
    
    async def _brave_search(self, query: SearchQuery) -> List[SearchResult]:
        """Search using Brave Search API."""
        headers = {
            "X-Subscription-Token": self.brave_api_key,
            "Accept": "application/json"
        }
        
        params = {
            "q": query.text,
            "count": min(query.max_results, 20),
            "text_decorations": "false",
            "safesearch": "moderate" if query.safe_search else "off",
            "freshness": query.time_range or "pd"
        }
        
        if query.language != "en":
            params["search_lang"] = query.language
        if query.region != "us":
            params["country"] = query.region.upper()
        
        try:
            response = await self.client.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers=headers,
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get("web", {}).get("results", []):
                    result = SearchResult(
                        url=item.get("url", ""),
                        title=item.get("title", ""),
                        content=item.get("description", ""),
                        snippet=item.get("description", ""),
                        provider=SearchProvider.BRAVE,
                        relevance_score=float(item.get("score", 0.5)),
                        domain_authority=self._estimate_domain_authority(item.get("url", "")),
                        metadata={"brave_rank": item.get("rank", 0)}
                    )
                    
                    # Parse age if available
                    if "age" in item:
                        result.freshness_score = self._parse_freshness(item["age"])
                    
                    results.append(result)
                
                return results[:query.max_results]
            
            elif response.status_code == 429:
                logger.warning("Brave Search rate limited, falling back")
                self.rate_limit_remaining = 0
                return []
            
            else:
                logger.warning(f"Brave Search failed: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Brave Search error: {e}")
            return []
    
    async def _duckduckgo_search(self, query: SearchQuery) -> List[SearchResult]:
        """Search using DuckDuckGo with multiple fallback methods."""
        # Add jitter to avoid fingerprinting
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        try:
            # Try DDGS library first
            results = await self._ddgs_library_search(query)
            if results:
                return results
        except Exception as e:
            logger.debug(f"DDGS library failed: {e}")
        
        # Fallback to direct HTML scraping
        return await self._ddgs_html_search(query)
    
    async def _ddgs_library_search(self, query: SearchQuery) -> List[SearchResult]:
        """Search using DuckDuckGo library."""
        try:
            from duckduckgo_search import DDGS
            
            def _sync_search():
                with DDGS() as ddgs:
                    search_results = ddgs.text(
                        query.text,
                        region=query.region,
                        safesearch="moderate" if query.safe_search else "off",
                        timelimit=query.time_range or "y",
                        max_results=query.max_results
                    )
                    
                    results = []
                    for r in search_results:
                        result = SearchResult(
                            url=r.get("href", ""),
                            title=r.get("title", ""),
                            content=r.get("body", ""),
                            snippet=r.get("body", ""),
                            provider=SearchProvider.DUCKDUCKGO,
                            relevance_score=0.7,  # DDGS typically provides good results
                            domain_authority=self._estimate_domain_authority(r.get("href", ""))
                        )
                        results.append(result)
                    
                    return results
            
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, _sync_search)
            
        except Exception as e:
            logger.error(f"DDGS library search failed: {e}")
            return []
    
    async def _ddgs_html_search(self, query: SearchQuery) -> List[SearchResult]:
        """Search using direct DuckDuckGo HTML scraping."""
        await asyncio.sleep(random.uniform(1.0, 2.0))
        
        headers = {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": f"{query.language}-{query.region.upper()},en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        
        params = {
            "q": query.text,
            "kl": f"{query.language}-{query.region.upper()}",
            "safe": "1" if query.safe_search else "0"
        }
        
        if query.time_range:
            params["df"] = query.time_range
        
        try:
            response = await self.client.get(
                "https://html.duckduckgo.com/html/",
                headers=headers,
                params=params
            )
            
            if response.status_code != 200:
                logger.error(f"DDG HTML search failed: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.text, "html.parser")
            results = []
            
            # Extract results from DDG HTML structure
            result_items = soup.select(".result")
            if not result_items:
                result_items = soup.select(".web-result")
            
            for item in result_items[:query.max_results]:
                title_link = item.select_one(".result__a") or item.select_one("a")
                snippet = item.select_one(".result__snippet") or item.select_one(".snippet")
                
                if title_link and title_link.get("href"):
                    result = SearchResult(
                        url=title_link.get("href"),
                        title=title_link.get_text(strip=True),
                        content=snippet.get_text(strip=True) if snippet else "",
                        snippet=snippet.get_text(strip=True) if snippet else "",
                        provider=SearchProvider.DUCKDUCKGO,
                        relevance_score=0.6,
                        domain_authority=self._estimate_domain_authority(title_link.get("href"))
                    )
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"DDG HTML search error: {e}")
            return []
    
    async def _html_fallback_search(self, query: SearchQuery) -> List[SearchResult]:
        """Ultimate fallback using multiple search engines."""
        fallback_engines = [
            ("https://html.startpage.com/html/", {"query": query.text}),
            ("https://search.brave.com/search", {"q": query.text}),
            ("https://www.qwant.com/", {"q": query.text})
        ]
        
        for engine_url, params in fallback_engines:
            try:
                results = await self._generic_html_search(engine_url, params, query)
                if results:
                    return results
            except Exception as e:
                logger.debug(f"Fallback engine {engine_url} failed: {e}")
                continue
        
        return []
    
    async def _generic_html_search(self, url: str, params: Dict[str, str], query: SearchQuery) -> List[SearchResult]:
        """Generic HTML search for unknown engines."""
        headers = {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": f"{query.language}-{query.region.upper()},en;q=0.5"
        }
        
        response = await self.client.get(url, headers=headers, params=params)
        if response.status_code != 200:
            return []
        
        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        
        # Generic link extraction
        links = soup.find_all("a", href=True)
        for link in links[:query.max_results]:
            href = link.get("href")
            if href and href.startswith("http") and not any(skip in href for skip in ["javascript:", "#", "mailto:"]):
                title = link.get_text(strip=True)
                if title and len(title) > 10:  # Filter out short/noise titles
                    result = SearchResult(
                        url=href,
                        title=title,
                        content="",  # No content available from generic search
                        snippet="",
                        provider=SearchProvider.NATIVE,
                        relevance_score=0.3,
                        domain_authority=self._estimate_domain_authority(href)
                    )
                    results.append(result)
        
        return results
    
    def _estimate_domain_authority(self, url: str) -> float:
        """Estimate domain authority based on domain characteristics."""
        try:
            domain = urlparse(url).netloc.lower()
            
            # High authority domains
            high_authority = {
                "wikipedia.org", "github.com", "stackoverflow.com", "medium.com",
                "nytimes.com", "washingtonpost.com", "bbc.com", "cnn.com",
                "reuters.com", "ap.org", "nature.com", "science.org", "arxiv.org"
            }
            
            # Medium authority domains
            medium_authority = {
                "linkedin.com", "twitter.com", "facebook.com", "youtube.com",
                "reddit.com", "hackernews.com", "techcrunch.com", "venturebeat.com"
            }
            
            if any(ha in domain for ha in high_authority):
                return 0.9
            elif any(ma in domain for ma in medium_authority):
                return 0.7
            elif len(domain.split('.')) <= 2:  # Likely primary domain
                return 0.6
            else:
                return 0.4
                
        except Exception:
            return 0.5
    
    def _parse_freshness(self, age_str: str) -> float:
        """Parse freshness score from age string."""
        try:
            if "day" in age_str.lower():
                days = int(re.search(r'(\d+)', age_str).group(1))
                return max(0.0, 1.0 - (days / 30))
            elif "hour" in age_str.lower():
                hours = int(re.search(r'(\d+)', age_str).group(1))
                return max(0.0, 1.0 - (hours / 720))
            elif "month" in age_str.lower():
                months = int(re.search(r'(\d+)', age_str).group(1))
                return max(0.0, 1.0 - (months / 12))
            else:
                return 0.5
        except Exception:
            return 0.5
    
    async def is_healthy(self) -> bool:
        """Check provider health."""
        if self.consecutive_failures >= 5:
            return False
        
        # Test with a simple query
        try:
            test_query = SearchQuery(text="test", max_results=1)
            results = await self._duckduckgo_search(test_query)
            return len(results) > 0
        except Exception:
            return False
    
    def get_cost_per_request(self) -> float:
        """Get cost per request."""
        if self.brave_api_key:
            return 0.001  # Brave Search paid tier
        return 0.0  # Free DuckDuckGo


class EnhancedSerperSearchProvider(BaseSearchProvider):
    """Enhanced Serper Search with advanced features."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(SearchProvider.SERPER, config)
        self.api_key = config.get("serper_api_key")
        self.client = httpx.AsyncClient(timeout=15.0)
        self.rate_limiter = RateLimiter(requests_per_second=5.0)
        self.base_url = "https://google.serper.dev/search"
        
    async def search(self, query: SearchQuery) -> List[SearchResult]:
        """Execute search using Serper API."""
        if not self.api_key:
            logger.warning("Serper API key not configured")
            return []
        
        await self.rate_limiter.wait_for_token()
        start_time = time.time()
        
        try:
            payload = self._build_payload(query)
            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }
            
            response = await self.client.post(self.base_url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                results = self._parse_response(data, query)
                self.update_metrics(True, (time.time() - start_time) * 1000)
                return results
            elif response.status_code == 429:
                logger.warning("Serper rate limited")
                self.rate_limit_remaining = 0
                return []
            else:
                logger.error(f"Serper search failed: {response.status_code}")
                self.update_metrics(False, (time.time() - start_time) * 1000)
                return []
                
        except Exception as e:
            logger.error(f"Serper search error: {e}")
            self.update_metrics(False, (time.time() - start_time) * 1000)
            return []
    
    def _build_payload(self, query: SearchQuery) -> Dict[str, Any]:
        """Build Serper API payload."""
        payload = {
            "q": query.text,
            "num": min(query.max_results, 100)
        }
        
        # Add search parameters
        if query.language != "en":
            payload["hl"] = query.language
        if query.region != "us":
            payload["gl"] = query.region.upper()
        if query.safe_search:
            payload["safe"] = "active"
        
        # Time range filtering
        time_mapping = {
            "1d": "d",
            "1w": "w", 
            "1m": "m",
            "1y": "y"
        }
        if query.time_range in time_mapping:
            payload["tbs"] = f"qdr:{time_mapping[query.time_range]}"
        
        # Content type filtering
        if ContentType.NEWS in query.content_types:
            payload["tbm"] = "nws"
        elif ContentType.VIDEO in query.content_types:
            payload["tbm"] = "vid"
        elif ContentType.IMAGE in query.content_types:
            payload["tbm"] = "isch"
        
        # Domain filtering
        if query.prefer_domains:
            payload["site"] = " OR ".join(query.prefer_domains)
        
        return payload
    
    def _parse_response(self, data: Dict[str, Any], query: SearchQuery) -> List[SearchResult]:
        """Parse Serper API response."""
        results = []
        
        # Organic results
        for item in data.get("organic", [])[:query.max_results]:
            result = SearchResult(
                url=item.get("link", ""),
                title=item.get("title", ""),
                content=item.get("snippet", ""),
                snippet=item.get("snippet", ""),
                provider=SearchProvider.SERPER,
                relevance_score=self._calculate_relevance(item, query),
                domain_authority=self._estimate_domain_authority(item.get("link", "")),
                metadata={
                    "position": item.get("position", 0),
                    "displayed_link": item.get("displayedLink", "")
                }
            )
            
            # Extract additional metadata
            if "snippet" in item and len(item["snippet"]) > 200:
                result.content = item["snippet"][:10000]
            
            results.append(result)
        
        # Knowledge graph results if available
        for item in data.get("knowledgeGraph", []):
            if item.get("description"):
                result = SearchResult(
                    url=item.get("descriptionLink", ""),
                    title=item.get("title", ""),
                    content=item.get("description", ""),
                    snippet=item.get("description", ""),
                    provider=SearchProvider.SERPER,
                    relevance_score=0.95,  # Knowledge graph results are high quality
                    content_type=ContentType.WEB,
                    metadata={"type": "knowledge_graph"}
                )
                results.append(result)
        
        return results[:query.max_results]
    
    def _calculate_relevance(self, item: Dict[str, Any], query: SearchQuery) -> float:
        """Calculate relevance score for result."""
        title = item.get("title", "").lower()
        snippet = item.get("snippet", "").lower()
        query_terms = query.text.lower().split()
        
        relevance = 0.0
        
        # Title matches
        for term in query_terms:
            if term in title:
                relevance += 0.3
            if term in snippet:
                relevance += 0.2
        
        # Position bonus
        position = item.get("position", 10)
        relevance += max(0, (10 - position) * 0.05)
        
        return min(1.0, relevance)
    
    def _estimate_domain_authority(self, url: str) -> float:
        """Estimate domain authority (reuse from Native provider)."""
        # Reuse the same logic as Native provider
        try:
            domain = urlparse(url).netloc.lower()
            
            high_authority = {
                "wikipedia.org", "github.com", "stackoverflow.com", "medium.com",
                "nytimes.com", "washingtonpost.com", "bbc.com", "cnn.com",
                "reuters.com", "ap.org", "nature.com", "science.org", "arxiv.org"
            }
            
            medium_authority = {
                "linkedin.com", "twitter.com", "facebook.com", "youtube.com",
                "reddit.com", "hackernews.com", "techcrunch.com", "venturebeat.com"
            }
            
            if any(ha in domain for ha in high_authority):
                return 0.9
            elif any(ma in domain for ma in medium_authority):
                return 0.7
            elif len(domain.split('.')) <= 2:
                return 0.6
            else:
                return 0.4
                
        except Exception:
            return 0.5
    
    async def is_healthy(self) -> bool:
        """Check Serper API health."""
        if not self.api_key:
            return False
        
        try:
            payload = {"q": "test", "num": 1}
            headers = {"X-API-KEY": self.api_key, "Content-Type": "application/json"}
            
            response = await self.client.post(self.base_url, json=payload, headers=headers)
            return response.status_code == 200
            
        except Exception:
            return False
    
    def get_cost_per_request(self) -> float:
        """Get cost per request."""
        return 0.0025  # Serper typical cost


# Provider factory
def create_search_provider(provider: SearchProvider, config: Dict[str, Any]) -> BaseSearchProvider:
    """Factory function to create search providers."""
    providers = {
        SearchProvider.NATIVE: EnhancedNativeSearchProvider,
        SearchProvider.SERPER: EnhancedSerperSearchProvider,
    }
    
    provider_class = providers.get(provider)
    if not provider_class:
        raise ValueError(f"Unknown provider: {provider}")
    
    return provider_class(config)
