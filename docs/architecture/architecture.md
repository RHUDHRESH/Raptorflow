# Architecture Overview

## Canonical Entry Point
- `backend/main.py` exposes the single FastAPI app.
- `backend/app_factory.py` owns app construction, middleware ordering, and router wiring.

## Routing
- Canonical routers are registered in `backend/api/registry.py` and mounted at `/api`.
- Optional legacy v1 prefix is mounted at `/api/v1` when `ENABLE_LEGACY_V1=true`.
- Legacy/experimental routers are centralized in `backend/api/legacy_registry.py` and mounted at `/api/legacy` when `ENABLE_LEGACY_EXPERIMENTAL_ROUTES=true`.

## Target Layering
Routes → Controllers → Services → Repositories → Models

## Infrastructure
- Middleware, auth, logging, error handling, rate limiting are wired in `backend/app_factory.py`.
- Shared infrastructure modules live under `backend/infrastructure/` and `backend/core/`.

## Diagram

```text
Clients
  |
  v
Routes (FastAPI routers) -> Controllers -> Services -> Repositories -> DB
  |
  v
Infrastructure (auth, logging, error handling, rate limiting, caching)
  |
  v
Integrations (PhonePe, GCP, Redis, Vertex AI, SearxNG)
```
