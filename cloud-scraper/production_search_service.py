"""
Production-Grade Free Web Search Service
Enterprise features: monitoring, caching, rate limiting, logging, health checks
"""

import asyncio
import json
import logging
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import httpx
import redis
import structlog
from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from free_web_search import FreeWebSearchEngine, SearchResult
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Prometheus Metrics
SEARCH_REQUESTS = Counter(
    "search_requests_total", "Total search requests", ["engine", "status"]
)
SEARCH_DURATION = Histogram("search_duration_seconds", "Search request duration")
ACTIVE_REQUESTS = Gauge("active_requests", "Active search requests")
CACHE_HITS = Counter("cache_hits_total", "Total cache hits")
CACHE_MISSES = Counter("cache_misses_total", "Total cache misses")
ENGINE_HEALTH = Gauge("engine_health", "Search engine health status", ["engine"])

# Configuration
CONFIG = {
    "max_concurrent_requests": int(os.getenv("MAX_CONCURRENT_REQUESTS", "20")),
    "rate_limit_per_minute": int(os.getenv("RATE_LIMIT_PER_MINUTE", "1000")),
    "request_timeout": int(os.getenv("REQUEST_TIMEOUT", "30")),
    "cache_ttl": int(os.getenv("CACHE_TTL", "300")),  # 5 minutes
    "enable_metrics": os.getenv("ENABLE_METRICS", "true").lower() == "true",
    "log_level": os.getenv("LOG_LEVEL", "INFO").upper(),
}

# Redis client for caching
redis_client = None


class ProductionSearchService:
    """Production-grade search service with enterprise features"""

    def __init__(self):
        self.search_engine = FreeWebSearchEngine()
        self.rate_limiter = RateLimiter(CONFIG["rate_limit_per_minute"])
        self.cache = SearchCache()
        self.health_checker = HealthChecker()
        self.active_requests = 0

    async def initialize(self):
        """Initialize production service"""
        await self.search_engine.initialize()
        await self.cache.initialize()
        await self.health_checker.initialize()

    async def search_with_monitoring(
        self, query: str, engines: List[str], max_results: int, client_ip: str
    ) -> Dict[str, Any]:
        """Search with full monitoring and caching"""

        # Rate limiting
        if not await self.rate_limiter.check_rate_limit(client_ip):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        # Check cache first
        cache_key = f"search:{hash(query)}:{','.join(engines)}:{max_results}"
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            CACHE_HITS.inc()
            logger.info("Cache hit", query=query, engines=engines)
            return cached_result

        CACHE_MISSES.inc()

        # Perform search with monitoring
        start_time = time.time()
        self.active_requests += 1
        ACTIVE_REQUESTS.set(self.active_requests)

        try:
            result = await self.search_engine.search(query, engines, max_results)

            # Add production metadata
            result.update(
                {
                    "production_metadata": {
                        "client_ip": client_ip,
                        "cache_hit": False,
                        "processing_time": time.time() - start_time,
                        "rate_limited": False,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                }
            )

            # Cache the result
            await self.cache.set(cache_key, result, CONFIG["cache_ttl"])

            # Update metrics
            SEARCH_REQUESTS.labels(engine="all", status="success").inc()
            SEARCH_DURATION.observe(time.time() - start_time)

            logger.info(
                "Search completed",
                query=query,
                engines=engines,
                results=result["total_results"],
                duration=time.time() - start_time,
            )

            return result

        except Exception as e:
            SEARCH_REQUESTS.labels(engine="all", status="error").inc()
            logger.error("Search failed", query=query, error=str(e))
            raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

        finally:
            self.active_requests -= 1
            ACTIVE_REQUESTS.set(self.active_requests)

    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        return await self.health_checker.check_health()

    async def close(self):
        """Cleanup resources"""
        await self.search_engine.close()
        await self.cache.close()


class RateLimiter:
    """Redis-based rate limiter"""

    def __init__(self, requests_per_minute: int):
        self.requests_per_minute = requests_per_minute
        self.redis = None

    async def initialize(self):
        self.redis = redis_client

    async def check_rate_limit(self, client_ip: str) -> bool:
        """Check if client is within rate limit"""
        if not self.redis:
            return True  # No rate limiting if Redis unavailable

        key = f"rate_limit:{client_ip}"
        current = self.redis.incr(key)

        if current == 1:
            self.redis.expire(key, 60)  # 1 minute window

        return current <= self.requests_per_minute


class SearchCache:
    """Redis-based search result cache"""

    def __init__(self):
        self.redis = None

    async def initialize(self):
        self.redis = redis_client

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached result"""
        if not self.redis:
            return None

        try:
            cached = self.redis.get(key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning("Cache get failed", key=key, error=str(e))

        return None

    async def set(self, key: str, value: Dict[str, Any], ttl: int):
        """Cache result"""
        if not self.redis:
            return

        try:
            self.redis.setex(key, ttl, json.dumps(value))
        except Exception as e:
            logger.warning("Cache set failed", key=key, error=str(e))

    async def close(self):
        """Cleanup cache resources"""
        pass


class HealthChecker:
    """Health checker for all components"""

    def __init__(self):
        self.search_engine = None

    async def initialize(self):
        from free_web_search import free_search_engine

        self.search_engine = free_search_engine

    async def check_health(self) -> Dict[str, Any]:
        """Check health of all components"""
        health = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0",
            "components": {},
        }

        # Check search engines
        engine_health = await self._check_search_engines()
        health["components"]["search_engines"] = engine_health

        # Check Redis
        redis_health = await self._check_redis()
        health["components"]["redis"] = redis_health

        # Check system resources
        system_health = await self._check_system_resources()
        health["components"]["system"] = system_health

        # Overall status
        if any(
            component["status"] != "healthy"
            for component in health["components"].values()
        ):
            health["status"] = "degraded"

        return health

    async def _check_search_engines(self) -> Dict[str, Any]:
        """Check search engine availability"""
        engines = ["duckduckgo", "brave", "searx"]
        results = {}

        for engine in engines:
            try:
                start_time = time.time()
                await self.search_engine.search("test", [engine], 1)
                duration = time.time() - start_time

                results[engine] = {
                    "status": "healthy",
                    "response_time": duration,
                    "last_check": datetime.now(timezone.utc).isoformat(),
                }

                ENGINE_HEALTH.labels(engine=engine).set(1)

            except Exception as e:
                results[engine] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "last_check": datetime.now(timezone.utc).isoformat(),
                }

                ENGINE_HEALTH.labels(engine=engine).set(0)

        return {
            "status": (
                "healthy"
                if all(r["status"] == "healthy" for r in results.values())
                else "degraded"
            ),
            "engines": results,
        }

    async def _check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity"""
        try:
            if redis_client:
                redis_client.ping()
                return {
                    "status": "healthy",
                    "last_check": datetime.now(timezone.utc).isoformat(),
                }
            else:
                return {"status": "disabled", "message": "Redis not configured"}
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.now(timezone.utc).isoformat(),
            }

    async def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resources"""
        try:
            import psutil

            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()

            # Disk usage
            disk = psutil.disk_usage("/")

            return {
                "status": "healthy",
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "last_check": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            return {
                "status": "unknown",
                "error": str(e),
                "last_check": datetime.now(timezone.utc).isoformat(),
            }


# Global service instance
production_service = ProductionSearchService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting production search service")
    await production_service.initialize()
    logger.info("Production search service started successfully")

    yield

    # Shutdown
    logger.info("Shutting down production search service")
    await production_service.close()
    logger.info("Production search service shut down")


# FastAPI app
app = FastAPI(
    title="Production Free Web Search API",
    version="1.0.0",
    description="Enterprise-grade free web search with monitoring and caching",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Get client IP
    client_ip = request.client.host
    if "x-forwarded-for" in request.headers:
        client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()

    # Log request
    logger.info(
        "Request started",
        method=request.method,
        url=str(request.url),
        client_ip=client_ip,
    )

    # Process request
    response = await call_next(request)

    # Log response
    duration = time.time() - start_time
    logger.info(
        "Request completed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        duration=duration,
    )

    # Add response headers
    response.headers["X-Response-Time"] = str(duration)
    response.headers["X-Request-ID"] = str(id(request))

    return response


def get_client_ip(request: Request) -> str:
    """Extract client IP from request"""
    client_ip = request.client.host
    if "x-forwarded-for" in request.headers:
        client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
    return client_ip


@app.get("/search")
async def search_web(
    request: Request,
    q: str = Query(..., description="Search query"),
    engines: str = Query(
        "duckduckgo,brave,searx", description="Comma-separated list of engines"
    ),
    max_results: int = Query(
        20, ge=1, le=100, description="Maximum results per engine"
    ),
    client_ip: str = Depends(get_client_ip),
):
    """
    Production-grade web search with monitoring and caching

    - **q**: Search query (required)
    - **engines**: Comma-separated list of engines
    - **max_results**: Maximum results per engine (1-100)

    Features:
    - Rate limiting
    - Result caching
    - Performance monitoring
    - Request logging
    - Health checks
    """

    engine_list = [e.strip() for e in engines.split(",") if e.strip()]

    try:
        result = await production_service.search_with_monitoring(
            query=q, engines=engine_list, max_results=max_results, client_ip=client_ip
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected search error", query=q, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    try:
        health = await production_service.health_check()

        # Return appropriate status code
        status_code = 200 if health["status"] == "healthy" else 503
        return JSONResponse(content=health, status_code=status_code)

    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return JSONResponse(
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            status_code=503,
        )


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    if not CONFIG["enable_metrics"]:
        raise HTTPException(status_code=404, detail="Metrics disabled")

    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/search/engines")
async def list_engines():
    """List available search engines with health status"""
    health = await production_service.health_check()
    engine_health = health["components"].get("search_engines", {}).get("engines", {})

    engines_info = {
        "engines": list(production_service.search_engine.search_engines.keys()),
        "health": engine_health,
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
            "cached": True,
            "monitored": True,
        },
    }

    return engines_info


@app.get("/status")
async def service_status():
    """Service status and configuration"""
    return {
        "service": "Production Free Web Search",
        "version": "1.0.0",
        "status": "running",
        "uptime": "N/A",  # Could be tracked
        "configuration": CONFIG,
        "features": [
            "rate_limiting",
            "result_caching",
            "performance_monitoring",
            "health_checks",
            "structured_logging",
            "prometheus_metrics",
            "load_balancing_ready",
        ],
        "endpoints": {
            "search": "/search",
            "health": "/health",
            "metrics": "/metrics",
            "engines": "/search/engines",
            "status": "/status",
        },
    }


# Initialize Redis if available
def initialize_redis():
    """Initialize Redis client"""
    global redis_client

    try:
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))
        redis_password = os.getenv("REDIS_PASSWORD", None)

        redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )

        # Test connection
        redis_client.ping()
        logger.info("Redis connected successfully")

    except Exception as e:
        logger.warning("Redis connection failed, running without cache", error=str(e))
        redis_client = None


# Initialize on startup
initialize_redis()

if __name__ == "__main__":
    import uvicorn

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, CONFIG["log_level"]),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8084,
        workers=1,  # Single worker for shared state
        access_log=True,
        log_config=None,  # Use our logging config
    )
