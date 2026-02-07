"""
Part 12: API Layer and External Interfaces
RaptorFlow Unified Search System - Industrial Grade AI Agent Search Infrastructure
===============================================================================
This module provides the REST API layer and external interfaces for the unified
search system, enabling integration with external applications and services.
"""

import asyncio
import json
import logging
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import uvicorn
from fastapi import BackgroundTasks, Body, Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator

from core.unified_search_part1 import ContentType, SearchMode
from core.unified_search_part7 import SimpleResearchRequest, SimpleSearchRequest
from core.unified_search_part10 import get_search_interface, unified_search_engine

logger = logging.getLogger("raptorflow.unified_search.api")


class APIResponse(BaseModel):
    """Standard API response format."""

    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: Optional[str] = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class SearchRequest(BaseModel):
    """Search request model."""

    query: str = Field(..., description="Search query text")
    mode: str = Field(
        default="standard",
        description="Search mode: lightning, standard, deep, exhaustive",
    )
    max_results: int = Field(
        default=10, ge=1, le=100, description="Maximum number of results"
    )
    content_types: List[str] = Field(
        default=["web"], description="Content types to search"
    )
    language: str = Field(default="en", description="Search language")
    region: str = Field(default="us", description="Search region")
    time_range: Optional[str] = Field(None, description="Time range: 1d, 1w, 1m, 1y")
    include_images: bool = Field(default=False, description="Include image results")
    include_videos: bool = Field(default=False, description="Include video results")
    safe_search: bool = Field(default=True, description="Enable safe search")

    @validator("mode")
    def validate_mode(cls, v):
        valid_modes = [mode.value for mode in SearchMode]
        if v not in valid_modes:
            raise ValueError(f"Invalid mode. Must be one of: {valid_modes}")
        return v

    @validator("content_types")
    def validate_content_types(cls, v):
        valid_types = [ct.value for ct in ContentType]
        for ct in v:
            if ct not in valid_types:
                raise ValueError(
                    f"Invalid content type: {ct}. Must be one of: {valid_types}"
                )
        return v

    def to_simple_request(self) -> SimpleSearchRequest:
        """Convert to SimpleSearchRequest."""
        return SimpleSearchRequest(
            query=self.query,
            mode=self.mode,
            max_results=self.max_results,
            content_types=self.content_types,
            language=self.language,
            region=self.region,
            time_range=self.time_range,
            include_images=self.include_images,
            include_videos=self.include_videos,
            safe_search=self.safe_search,
        )


class ResearchRequest(BaseModel):
    """Research request model."""

    topic: str = Field(..., description="Research topic")
    research_question: str = Field(..., description="Specific research question")
    depth: str = Field(
        default="moderate",
        description="Research depth: surface, moderate, deep, exhaustive",
    )
    max_sources: int = Field(
        default=20, ge=1, le=100, description="Maximum number of sources"
    )
    time_limit_minutes: int = Field(
        default=30, ge=5, le=120, description="Time limit in minutes"
    )
    content_types: List[str] = Field(
        default=["web"], description="Content types to research"
    )
    verification_required: bool = Field(
        default=True, description="Require content verification"
    )
    synthesis_format: str = Field(
        default="comprehensive", description="Synthesis format"
    )

    @validator("depth")
    def validate_depth(cls, v):
        valid_depths = ["surface", "moderate", "deep", "exhaustive"]
        if v not in valid_depths:
            raise ValueError(f"Invalid depth. Must be one of: {valid_depths}")
        return v

    def to_simple_request(self) -> SimpleResearchRequest:
        """Convert to SimpleResearchRequest."""
        return SimpleResearchRequest(
            topic=self.topic,
            research_question=self.research_question,
            depth=self.depth,
            max_sources=self.max_sources,
            time_limit_minutes=self.time_limit_minutes,
            content_types=self.content_types,
            verification_required=self.verification_required,
            synthesis_format=self.synthesis_format,
        )


class CrawlRequest(BaseModel):
    """Crawl request model."""

    urls: List[str] = Field(..., description="URLs to crawl")
    max_concurrent: int = Field(
        default=5, ge=1, le=20, description="Maximum concurrent crawls"
    )
    timeout_seconds: int = Field(
        default=30, ge=5, le=120, description="Timeout per URL"
    )
    extract_images: bool = Field(default=False, description="Extract images")
    extract_links: bool = Field(default=True, description="Extract links")
    respect_robots_txt: bool = Field(default=True, description="Respect robots.txt")


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    timestamp: datetime
    engine: Dict[str, Any]
    providers: Dict[str, Any]
    system: Dict[str, Any]
    stats: Dict[str, Any]


class StatsResponse(BaseModel):
    """Statistics response model."""

    total_searches: int
    successful_searches: int
    failed_searches: int
    total_research_requests: int
    successful_research: int
    failed_research: int
    total_crawls: int
    successful_crawls: int
    failed_crawls: int
    uptime_seconds: float
    avg_response_time_ms: float
    cache_hit_rate: float
    last_updated: datetime


class UnifiedSearchAPI:
    """Main API class for the unified search system."""

    def __init__(self):
        self.app = FastAPI(
            title="RaptorFlow Unified Search API",
            description="Industrial-grade AI agent search infrastructure",
            version="3.0.0",
            docs_url="/docs",
            redoc_url="/redoc",
        )
        self.setup_middleware()
        self.setup_routes()

    def setup_middleware(self):
        """Setup API middleware."""
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure based on security requirements
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["*"],
        )

        # GZip middleware
        self.app.add_middleware(GZipMiddleware, minimum_size=1000)

        # Request logging middleware
        @self.app.middleware("http")
        async def log_requests(request, call_next):
            start_time = datetime.now()

            response = await call_next(request)

            duration = (datetime.now() - start_time).total_seconds()

            logger.info(
                f"{request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Duration: {duration:.3f}s"
            )

            return response

    def setup_routes(self):
        """Setup API routes."""

        @self.app.get("/", response_model=Dict[str, str])
        async def root():
            """Root endpoint."""
            return {
                "name": "RaptorFlow Unified Search API",
                "version": "3.0.0",
                "status": "running",
                "docs": "/docs",
                "health": "/health",
            }

        @self.app.get("/health", response_model=HealthResponse)
        async def health_check():
            """Health check endpoint."""
            try:
                health_data = await unified_search_engine.health_check()
                return HealthResponse(**health_data)
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                raise HTTPException(status_code=500, detail="Health check failed")

        @self.app.get("/stats", response_model=StatsResponse)
        async def get_stats():
            """Get system statistics."""
            try:
                stats = unified_search_engine.get_stats()
                return StatsResponse(**asdict(stats))
            except Exception as e:
                logger.error(f"Stats retrieval failed: {e}")
                raise HTTPException(status_code=500, detail="Stats retrieval failed")

        @self.app.post("/search", response_model=APIResponse)
        async def search(request: SearchRequest, background_tasks: BackgroundTasks):
            """Search endpoint."""
            request_id = str(uuid.uuid4())

            try:
                # Log search request
                logger.info(f"Search request [{request_id}]: {request.query}")

                # Convert to simple request
                simple_request = request.to_simple_request()

                # Perform search
                interface = get_search_interface()
                results = await interface.search(simple_request)

                # Log search completion
                logger.info(f"Search completed [{request_id}]: {len(results)} results")

                # Record metrics in background
                background_tasks.add_task(
                    self._record_search_metrics, request_id, request.query, len(results)
                )

                return APIResponse(
                    success=True,
                    data=[asdict(result) for result in results],
                    request_id=request_id,
                )

            except Exception as e:
                logger.error(f"Search failed [{request_id}]: {e}")
                return APIResponse(success=False, error=str(e), request_id=request_id)

        @self.app.post("/search/quick", response_model=APIResponse)
        async def quick_search(
            query: str = Query(..., description="Search query"),
            max_results: int = Query(
                default=5, ge=1, le=20, description="Maximum results"
            ),
        ):
            """Quick search endpoint."""
            request_id = str(uuid.uuid4())

            try:
                interface = get_search_interface()
                results = await interface.quick_search(query, max_results)

                return APIResponse(
                    success=True,
                    data=[asdict(result) for result in results],
                    request_id=request_id,
                )

            except Exception as e:
                logger.error(f"Quick search failed [{request_id}]: {e}")
                return APIResponse(success=False, error=str(e), request_id=request_id)

        @self.app.post("/search/comprehensive", response_model=APIResponse)
        async def comprehensive_search(
            query: str = Query(..., description="Search query"),
            max_results: int = Query(
                default=20, ge=1, le=50, description="Maximum results"
            ),
        ):
            """Comprehensive search endpoint."""
            request_id = str(uuid.uuid4())

            try:
                interface = get_search_interface()
                results = await interface.comprehensive_search(query, max_results)

                return APIResponse(
                    success=True,
                    data=[asdict(result) for result in results],
                    request_id=request_id,
                )

            except Exception as e:
                logger.error(f"Comprehensive search failed [{request_id}]: {e}")
                return APIResponse(success=False, error=str(e), request_id=request_id)

        @self.app.post("/search/news", response_model=APIResponse)
        async def news_search(
            query: str = Query(..., description="Search query"),
            max_results: int = Query(
                default=10, ge=1, le=30, description="Maximum results"
            ),
            time_range: str = Query(default="1w", description="Time range"),
        ):
            """News search endpoint."""
            request_id = str(uuid.uuid4())

            try:
                interface = get_search_interface()
                results = await interface.news_search(query, max_results, time_range)

                return APIResponse(
                    success=True,
                    data=[asdict(result) for result in results],
                    request_id=request_id,
                )

            except Exception as e:
                logger.error(f"News search failed [{request_id}]: {e}")
                return APIResponse(success=False, error=str(e), request_id=request_id)

        @self.app.post("/search/academic", response_model=APIResponse)
        async def academic_search(
            query: str = Query(..., description="Search query"),
            max_results: int = Query(
                default=15, ge=1, le=40, description="Maximum results"
            ),
        ):
            """Academic search endpoint."""
            request_id = str(uuid.uuid4())

            try:
                interface = get_search_interface()
                results = await interface.academic_search(query, max_results)

                return APIResponse(
                    success=True,
                    data=[asdict(result) for result in results],
                    request_id=request_id,
                )

            except Exception as e:
                logger.error(f"Academic search failed [{request_id}]: {e}")
                return APIResponse(success=False, error=str(e), request_id=request_id)

        @self.app.post("/research", response_model=APIResponse)
        async def research(request: ResearchRequest, background_tasks: BackgroundTasks):
            """Research endpoint."""
            request_id = str(uuid.uuid4())

            try:
                # Log research request
                logger.info(f"Research request [{request_id}]: {request.topic}")

                # Convert to simple request
                simple_request = request.to_simple_request()

                # Perform research
                interface = get_search_interface()
                report = await interface.research(simple_request)

                # Log research completion
                logger.info(
                    f"Research completed [{request_id}]: {len(report.key_findings)} findings"
                )

                # Record metrics in background
                background_tasks.add_task(
                    self._record_research_metrics,
                    request_id,
                    request.topic,
                    len(report.key_findings),
                )

                return APIResponse(
                    success=True, data=asdict(report), request_id=request_id
                )

            except Exception as e:
                logger.error(f"Research failed [{request_id}]: {e}")
                return APIResponse(success=False, error=str(e), request_id=request_id)

        @self.app.post("/research/quick", response_model=APIResponse)
        async def quick_research(
            topic: str = Query(..., description="Research topic"),
            question: str = Query(..., description="Research question"),
        ):
            """Quick research endpoint."""
            request_id = str(uuid.uuid4())

            try:
                interface = get_search_interface()
                report = await interface.quick_research(topic, question)

                return APIResponse(
                    success=True, data=asdict(report), request_id=request_id
                )

            except Exception as e:
                logger.error(f"Quick research failed [{request_id}]: {e}")
                return APIResponse(success=False, error=str(e), request_id=request_id)

        @self.app.post("/research/deep", response_model=APIResponse)
        async def deep_research(
            topic: str = Query(..., description="Research topic"),
            question: str = Query(..., description="Research question"),
        ):
            """Deep research endpoint."""
            request_id = str(uuid.uuid4())

            try:
                interface = get_search_interface()
                report = await interface.deep_research(topic, question)

                return APIResponse(
                    success=True, data=asdict(report), request_id=request_id
                )

            except Exception as e:
                logger.error(f"Deep research failed [{request_id}]: {e}")
                return APIResponse(success=False, error=str(e), request_id=request_id)

        @self.app.post("/research/exhaustive", response_model=APIResponse)
        async def exhaustive_research(
            topic: str = Query(..., description="Research topic"),
            question: str = Query(..., description="Research question"),
        ):
            """Exhaustive research endpoint."""
            request_id = str(uuid.uuid4())

            try:
                interface = get_search_interface()
                report = await interface.exhaustive_research(topic, question)

                return APIResponse(
                    success=True, data=asdict(report), request_id=request_id
                )

            except Exception as e:
                logger.error(f"Exhaustive research failed [{request_id}]: {e}")
                return APIResponse(success=False, error=str(e), request_id=request_id)

        @self.app.post("/crawl", response_model=APIResponse)
        async def crawl_urls(request: CrawlRequest):
            """Crawl URLs endpoint."""
            request_id = str(uuid.uuid4())

            try:
                # Log crawl request
                logger.info(f"Crawl request [{request_id}]: {len(request.urls)} URLs")

                # Perform crawling
                results = await unified_search_engine.crawl_urls(request.urls)

                # Log crawl completion
                logger.info(f"Crawl completed [{request_id}]: {len(results)} contents")

                return APIResponse(
                    success=True,
                    data=[asdict(result) for result in results],
                    request_id=request_id,
                )

            except Exception as e:
                logger.error(f"Crawl failed [{request_id}]: {e}")
                return APIResponse(success=False, error=str(e), request_id=request_id)

        @self.app.get("/metrics", response_model=Dict[str, Any])
        async def get_metrics():
            """Get system metrics."""
            try:
                from core.unified_search_part8 import metrics_collector

                return metrics_collector.get_metrics_summary()
            except Exception as e:
                logger.error(f"Metrics retrieval failed: {e}")
                raise HTTPException(status_code=500, detail="Metrics retrieval failed")

        @self.app.get("/analytics", response_model=Dict[str, Any])
        async def get_analytics(
            time_range_hours: int = Query(
                default=24, ge=1, le=168, description="Time range in hours"
            )
        ):
            """Get analytics report."""
            try:
                from core.unified_search_part8 import analytics_engine

                return analytics_engine.generate_performance_report(time_range_hours)
            except Exception as e:
                logger.error(f"Analytics retrieval failed: {e}")
                raise HTTPException(
                    status_code=500, detail="Analytics retrieval failed"
                )

        @self.app.get("/config", response_model=Dict[str, Any])
        async def get_config():
            """Get current configuration."""
            try:
                from core.unified_search_part9 import config_manager

                return config_manager.get_config_summary()
            except Exception as e:
                logger.error(f"Config retrieval failed: {e}")
                raise HTTPException(status_code=500, detail="Config retrieval failed")

        @self.app.post("/reload-config", response_model=APIResponse)
        async def reload_config():
            """Reload configuration."""
            try:
                from core.unified_search_part9 import config_manager

                success = await config_manager.reload_config()

                return APIResponse(
                    success=success,
                    data={
                        "message": (
                            "Configuration reloaded successfully"
                            if success
                            else "Configuration reload failed"
                        )
                    },
                )
            except Exception as e:
                logger.error(f"Config reload failed: {e}")
                return APIResponse(success=False, error=str(e))

    async def _record_search_metrics(
        self, request_id: str, query: str, result_count: int
    ):
        """Record search metrics in background."""
        try:
            from core.unified_search_part8 import metrics_collector

            metrics_collector.increment_counter("api_search_requests_total")
            metrics_collector.record_histogram("api_search_results_count", result_count)
        except Exception as e:
            logger.error(f"Failed to record search metrics: {e}")

    async def _record_research_metrics(
        self, request_id: str, topic: str, finding_count: int
    ):
        """Record research metrics in background."""
        try:
            from core.unified_search_part8 import metrics_collector

            metrics_collector.increment_counter("api_research_requests_total")
            metrics_collector.record_histogram(
                "api_research_findings_count", finding_count
            )
        except Exception as e:
            logger.error(f"Failed to record research metrics: {e}")

    def get_app(self) -> FastAPI:
        """Get FastAPI application."""
        return self.app


# Global API instance
api = UnifiedSearchAPI()


# Convenience functions
def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    return api.get_app()


async def start_api_server(host: str = "0.0.0.0", port: int = 8000, **kwargs):
    """Start the API server."""
    app = create_app()

    config = uvicorn.Config(app=app, host=host, port=port, **kwargs)

    server = uvicorn.Server(config)
    await server.serve()


# Example usage
"""
# Create FastAPI app
app = create_app()

# Run with uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Or start programmatically
import asyncio
asyncio.run(start_api_server(host="0.0.0.0", port=8000))
"""
