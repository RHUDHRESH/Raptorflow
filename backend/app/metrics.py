try:
    from prometheus_client import (
        Counter,
        Histogram,
        Gauge,
        generate_latest,
        CONTENT_TYPE_LATEST,
    )
except ImportError:
    from backend.vendor.prometheus_client import (
        Counter,
        Histogram,
        Gauge,
        generate_latest,
        CONTENT_TYPE_LATEST,
    )
from fastapi import FastAPI, Request, Response
from fastapi.responses import Response
import time

auth_attempts = Counter(
    "auth_attempts_total", "Total authentication attempts", ["type", "status"]
)

auth_latency = Histogram(
    "auth_latency_seconds", "Authentication endpoint latency", ["endpoint"]
)

active_sessions = Gauge("active_sessions", "Number of active user sessions")

rate_limit_hits = Counter("rate_limit_hits_total", "Rate limit hits", ["endpoint"])

request_duration = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint", "status_code"],
)


def setup_metrics(app: FastAPI):
    @app.middleware("http")
    async def prometheus_metrics(request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        duration = time.time() - start_time
        request_duration.labels(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
        ).observe(duration)

        return response

    @app.get("/metrics")
    async def metrics():
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

    return app
