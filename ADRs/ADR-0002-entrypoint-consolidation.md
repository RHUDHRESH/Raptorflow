# ADR-0002: Consolidate Backend Entrypoint on app_factory.py

## Status
Accepted

## Date
2026-02-07

## Context

The backend has **two competing app objects**:

1. **`backend/main.py`** — a standalone `app = FastAPI(...)` with:
   - Its own middleware stack (SecurityHeaders, Compression, RateLimit, Tracing, Versioning, Metrics, CorrelationID, RequestLogging)
   - Its own CORS configuration (hardcoded origins list)
   - Its own router registrations (foundation, blackbox_*, campaigns, moves, matrix, payments, radar_*, synthesis, muse, assets, feedback)
   - Its own startup/shutdown lifecycle (task queue, metrics, tracing, degradation monitoring, rate limiting, pool monitoring)
   - Its own health check endpoint (`/health`) with internal-key gating
   - **This is what production uses** (`Dockerfile`: `CMD ["uvicorn", "main:app", ...]`; `run_simple.py`: `"backend.main:app"`)

2. **`backend/app_factory.py`** — a `create_app()` factory with:
   - Middleware via `backend/app/middleware.py` + explicit `JWTAuthMiddleware` + `WorkspaceContextMiddleware` + `RequestContextMiddleware`
   - CORS from `settings.get_cors_origins()`
   - Router registration via `backend/api/registry.py` (27+ routers)
   - Legacy path rewriting middleware
   - **Only used by `main_minimal.py`** (marked "deprecated")

These register **completely different sets of routers** and **different middleware stacks**. This violates AGENTS.md rule #3 ("No parallel API layers").

## Decision

**`backend/main.py` will delegate to `create_app()` from `backend/app_factory.py`.**

Update (Reconstruction Mode): routers are intentionally limited to the verified, minimal set
(`workspaces`, `campaigns`, `moves`, `foundation`, `muse`) as described in ADR-0004.

The standalone `app = FastAPI(...)` block in `main.py` is replaced with:

```python
from backend.app_factory import create_app
app = create_app()
```

All router registrations, middleware, CORS, and lifecycle management move into `app_factory.py` (or modules it calls). `main.py` becomes a thin module that only exports `app`.

### Router consolidation

The routers currently only in `main.py` (radar, assets, feedback, synthesis, blackbox_telemetry, blackbox_memory, blackbox_roi, blackbox_learning, matrix) must be added to `backend/api/registry.py`'s `UNIVERSAL_ROUTERS` list.

### Middleware consolidation

The middleware stacks from both files are merged. The `app_factory.py` stack (auth middleware, request context) takes precedence for ordering. Production middleware (compression, tracing, metrics) is added via `add_middleware()`.

### Lifecycle

Startup/shutdown hooks from `main.py` move into `backend/app/lifespan.py` (which `app_factory.py` already references).

## Alternatives Considered

1. **Keep main.py as-is, delete app_factory.py** — rejected; the factory pattern is cleaner and `app_factory.py` already has the correct auth middleware wiring.
2. **Two separate apps for different concerns** — rejected; violates single-entrypoint principle and makes deployment confusing.

## Consequences

- Single source of truth for app configuration.
- `main_minimal.py` can be deleted (it was the only consumer of `create_app()`; now `main.py` is too).
- `Dockerfile` and `run_simple.py` continue to reference `main:app` — no deployment change needed.
- Routers from both files are unified in `registry.py`.
- Risk: routers that exist only in `main.py` may have import-time side effects or depend on modules not available in the `app_factory` import path. These must be tested.
