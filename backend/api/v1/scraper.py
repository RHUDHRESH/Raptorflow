"""
Unified Scraper API
Consolidates: production_service.py, ultra_fast_scraper.py, scraper_service.py
Single endpoint for all scraping strategies with unified configuration.
"""

from __future__ import annotations

import asyncio
import hashlib
import io
import json
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from multiprocessing import cpu_count
from typing import Any, Dict, List, Literal, Optional
from urllib.parse import urlparse

import httpx
import structlog
from bs4 import BeautifulSoup, SoupStrainer
from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
from playwright.async_api import async_playwright

logger = structlog.get_logger()

router = APIRouter(prefix="/scraper", tags=["scraper"])

# Unified strategy enum - merges all strategies from 3 services
class ScrapingStrategy(str, Enum):
    """All available scraping strategies"""
    # From production_service.py
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    ADAPTIVE = "adaptive"
    # From ultra_fast_scraper.py
    TURBO = "turbo"
    OPTIMIZED = "optimized"
    PARALLEL = "parallel"
    ASYNC = "async"


@dataclass
class ScrapingConfig:
    """Unified configuration for all scraping operations"""
    strategy: ScrapingStrategy
    timeout: int = 30
    max_workers: int = min(cpu_count(), 8)
    enable_cache: bool = True
    enable_ocr: bool = True
    enable_screenshot: bool = True
    connection_pool_size: int = 100
    request_timeout: float = 10.0


class UnifiedScraper:
    """Unified scraper with all strategies from 3 services"""
    
    def __init__(self):
        self.current_strategy = ScrapingStrategy.OPTIMIZED
        self.content_cache: Dict[str, Any] = {}
        self.session_cache: Dict[str, Any] = {}
        self.metrics_history: List[Dict] = []
        
        # Performance settings from ultra_fast
        self.max_workers = min(cpu_count(), 8)
        self.cpu_executor = ThreadPoolExecutor(max_workers=self.max_workers)
        
        # Initialize optimized parsers
        self._init_parsers()
        
        # Initialize HTTP session pool
        self.http_sessions: List[httpx.AsyncClient] = []
        self._init_sessions()
    
    def _init_parsers(self):
        """Initialize optimized parsers with SoupStrainer"""
        self.title_parser = SoupStrainer("title")
        self.content_parser = SoupStrainer(["div", "article", "main", "section"])
        self.link_parser = SoupStrainer("a")
        self.text_parser = SoupStrainer(["p", "span", "h1", "h2", "h3", "h4", "h5", "h6"])
    
    def _init_sessions(self):
        """Initialize HTTP session pool"""
        for _ in range(min(10, self.max_workers)):
            session = httpx.AsyncClient(
                timeout=30.0,
                limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                }
            )
            self.http_sessions.append(session)
    
    async def scrape(self, url: str, user_id: str, strategy: ScrapingStrategy, 
                     legal_basis: str = "user_request") -> Dict[str, Any]:
        """Unified scrape method with all strategies"""
        start_time = datetime.now(timezone.utc)
        
        try:
            # Validate URL
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError("Invalid URL")
            
            logger.info("Starting scrape", url=url, user_id=user_id, strategy=strategy.value)
            
            # Select scraping method based on strategy
            if strategy in [ScrapingStrategy.TURBO, ScrapingStrategy.OPTIMIZED, 
                           ScrapingStrategy.PARALLEL, ScrapingStrategy.ASYNC]:
                result = await self._scrape_ultra_fast(url, user_id, strategy)
            elif strategy == ScrapingStrategy.CONSERVATIVE:
                result = await self._scrape_conservative(url, user_id, legal_basis)
            elif strategy == ScrapingStrategy.AGGRESSIVE:
                result = await self._scrape_aggressive(url, user_id, legal_basis)
            else:
                result = await self._scrape_balanced(url, user_id, legal_basis)
            
            # Add metadata
            result.update({
                "timestamp": start_time.isoformat(),
                "processing_time": (datetime.now(timezone.utc) - start_time).total_seconds(),
                "strategy": strategy.value,
                "status": "success"
            })
            
            # Track metrics
            self.metrics_history.append({
                "timestamp": start_time.isoformat(),
                "strategy": strategy.value,
                "processing_time": result["processing_time"],
                "url": url
            })
            
            return result
            
        except Exception as e:
            logger.error("Scraping failed", url=url, user_id=user_id, error=str(e))
            return {
                "url": url,
                "user_id": user_id,
                "timestamp": start_time.isoformat(),
                "status": "error",
                "error": str(e),
                "strategy": strategy.value,
                "processing_time": (datetime.now(timezone.utc) - start_time).total_seconds()
            }
    
    async def _scrape_ultra_fast(self, url: str, user_id: str, 
                                 strategy: ScrapingStrategy) -> Dict[str, Any]:
        """Ultra-fast scraping with Playwright"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            try:
                page = await browser.new_page()
                await page.goto(url, timeout=30000)
                
                # Extract content
                title = await page.title()
                content = await page.content()
                
                # Take screenshot if enabled
                screenshot = await page.screenshot() if self.current_strategy in [
                    ScrapingStrategy.TURBO, ScrapingStrategy.OPTIMIZED
                ] else None
                
                await browser.close()
                
                # Parse content with BeautifulSoup
                soup = BeautifulSoup(content, "html.parser", parse_only=self.content_parser)
                readable_text = soup.get_text(separator="\n", strip=True)
                
                return {
                    "title": title,
                    "content": content[:10000],  # Truncate for storage
                    "readable_text": readable_text[:5000],
                    "screenshot": screenshot is not None,
                    "content_length": len(content)
                }
            except Exception:
                await browser.close()
                raise
    
    async def _scrape_conservative(self, url: str, user_id: str, legal_basis: str) -> Dict[str, Any]:
        """Conservative scraping - slow but reliable"""
        # From production_service.py
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                slow_mo=100  # Slow down for reliability
            )
            try:
                page = await browser.new_page()
                await page.goto(url, wait_until="networkidle", timeout=60000)
                
                title = await page.title()
                content = await page.content()
                
                # Extract structured data
                structured_data = await page.evaluate("""() => {
                    return {
                        title: document.title,
                        meta: Array.from(document.querySelectorAll('meta')).map(m => ({
                            name: m.getAttribute('name'),
                            content: m.getAttribute('content')
                        })),
                        links: Array.from(document.querySelectorAll('a')).slice(0, 50).map(a => ({
                            href: a.href,
                            text: a.textContent?.trim()
                        }))
                    }
                }""")
                
                await browser.close()
                
                return {
                    "title": title,
                    "content": content[:5000],
                    "structured_data": structured_data,
                    "legal_basis": legal_basis
                }
            except Exception:
                await browser.close()
                raise
    
    async def _scrape_aggressive(self, url: str, user_id: str, legal_basis: str) -> Dict[str, Any]:
        """Aggressive scraping - fast, parallel requests"""
        # Parallel HTTP requests
        tasks = [
            self._fetch_with_session(url),
            self._fetch_metadata(url)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        content_result = results[0] if not isinstance(results[0], Exception) else {}
        metadata_result = results[1] if not isinstance(results[1], Exception) else {}
        
        return {
            **content_result,
            **metadata_result,
            "parallel": True
        }
    
    async def _scrape_balanced(self, url: str, user_id: str, legal_basis: str) -> Dict[str, Any]:
        """Balanced approach - moderate speed with good reliability"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            try:
                page = await browser.new_page()
                await page.goto(url, timeout=30000)
                
                title = await page.title()
                content = await page.content()
                
                # Extract readable text
                soup = BeautifulSoup(content, "html.parser")
                for script in soup(["script", "style"]):
                    script.decompose()
                readable_text = soup.get_text(separator="\n", strip=True)
                
                await browser.close()
                
                return {
                    "title": title,
                    "content": content[:8000],
                    "readable_text": readable_text[:3000],
                    "legal_basis": legal_basis
                }
            except Exception:
                await browser.close()
                raise
    
    async def _fetch_with_session(self, url: str) -> Dict[str, Any]:
        """Fetch content using HTTP session"""
        session = self.http_sessions[0]  # Use first available session
        try:
            response = await session.get(url, follow_redirects=True)
            content = response.text
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(content, "html.parser", parse_only=self.title_parser)
            title = soup.title.string if soup.title else ""
            
            return {
                "title": title,
                "content": content[:5000],
                "status_code": response.status_code
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _fetch_metadata(self, url: str) -> Dict[str, Any]:
        """Fetch metadata about the URL"""
        try:
            parsed = urlparse(url)
            return {
                "domain": parsed.netloc,
                "scheme": parsed.scheme,
                "path": parsed.path
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Get scraping analytics"""
        recent_metrics = [
            m for m in self.metrics_history 
            if (datetime.now(timezone.utc) - datetime.fromisoformat(m["timestamp"])).days <= days
        ]
        
        if not recent_metrics:
            return {"message": "No data available", "total_scrapes": 0}
        
        # Calculate averages
        avg_processing_time = sum(m["processing_time"] for m in recent_metrics) / len(recent_metrics)
        
        # Strategy performance
        strategy_performance: Dict[str, List] = {}
        for m in recent_metrics:
            strategy = m["strategy"]
            if strategy not in strategy_performance:
                strategy_performance[strategy] = []
            strategy_performance[strategy].append(m)
        
        return {
            "period_days": days,
            "total_scrapes": len(recent_metrics),
            "avg_processing_time": avg_processing_time,
            "strategy_performance": {
                strategy: {
                    "count": len(metrics),
                    "avg_processing_time": sum(m["processing_time"] for m in metrics) / len(metrics)
                }
                for strategy, metrics in strategy_performance.items()
            },
            "current_strategy": self.current_strategy.value
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get basic statistics"""
        return {
            "total_scrapes": len(self.metrics_history),
            "cache_size": len(self.content_cache),
            "current_strategy": self.current_strategy.value,
            "available_strategies": [s.value for s in ScrapingStrategy],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# Global scraper instance
unified_scraper = UnifiedScraper()


# API Endpoints
@router.post("/")
async def scrape_endpoint(request: Dict[str, Any], background_tasks: BackgroundTasks):
    """
    Main scraping endpoint - unified interface for all strategies
    
    - **url**: Target URL to scrape
    - **user_id**: User identifier
    - **strategy**: One of [conservative, balanced, aggressive, adaptive, turbo, optimized, parallel, async]
    - **legal_basis**: Legal basis for scraping (default: user_request)
    """
    url = request.get("url")
    user_id = request.get("user_id")
    strategy_str = request.get("strategy", "optimized")
    legal_basis = request.get("legal_basis", "user_request")
    
    if not url or not user_id:
        raise HTTPException(status_code=400, detail="URL and user_id are required")
    
    # Validate strategy
    try:
        strategy = ScrapingStrategy(strategy_str.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid strategy. Choose from: {[s.value for s in ScrapingStrategy]}"
        )
    
    # Validate URL
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise HTTPException(status_code=400, detail="Invalid URL")
    
    logger.info("Scraping request", url=url, user_id=user_id, strategy=strategy.value)
    
    # Perform scraping
    result = await unified_scraper.scrape(url, user_id, strategy, legal_basis)
    
    return JSONResponse(content=result)


@router.get("/health")
async def scraper_health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "current_strategy": unified_scraper.current_strategy.value,
        "cache_size": len(unified_scraper.content_cache)
    }


@router.get("/analytics")
async def scraper_analytics(days: int = 7):
    """Get scraping analytics"""
    try:
        analytics = unified_scraper.get_analytics(days)
        return analytics
    except Exception as e:
        logger.error("Analytics failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics")


@router.get("/stats")
async def scraper_stats():
    """Get scraping statistics"""
    return unified_scraper.get_stats()


@router.get("/strategies")
async def list_strategies():
    """List available scraping strategies"""
    descriptions = {
        ScrapingStrategy.CONSERVATIVE: "Low risk, slow pace - ideal for sensitive sites",
        ScrapingStrategy.BALANCED: "Moderate risk, good pace - balanced approach",
        ScrapingStrategy.AGGRESSIVE: "High risk, fast pace - maximum speed",
        ScrapingStrategy.ADAPTIVE: "AI-driven, dynamic adjustment - smart optimization",
        ScrapingStrategy.TURBO: "Maximum speed, minimal safety - ideal for fast, simple sites",
        ScrapingStrategy.OPTIMIZED: "Balanced speed and reliability - best for most sites",
        ScrapingStrategy.PARALLEL: "Multi-core processing - best for CPU-intensive tasks",
        ScrapingStrategy.ASYNC: "Async I/O optimization - best for I/O-bound tasks",
    }
    
    return {
        "strategies": [
            {
                "name": strategy.value,
                "description": descriptions.get(strategy, "Unknown strategy")
            }
            for strategy in ScrapingStrategy
        ],
        "current_strategy": unified_scraper.current_strategy.value
    }


@router.post("/strategy")
async def update_strategy(request: Dict[str, Any]):
    """Update current scraping strategy"""
    strategy_str = request.get("strategy")
    
    if not strategy_str:
        raise HTTPException(status_code=400, detail="Strategy is required")
    
    try:
        new_strategy = ScrapingStrategy(strategy_str.lower())
        old_strategy = unified_scraper.current_strategy
        unified_scraper.current_strategy = new_strategy
        
        logger.info("Strategy updated", new_strategy=new_strategy.value)
        
        return {
            "status": "updated",
            "previous_strategy": old_strategy.value,
            "new_strategy": new_strategy.value
        }
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid strategy. Choose from: {[s.value for s in ScrapingStrategy]}"
        )
