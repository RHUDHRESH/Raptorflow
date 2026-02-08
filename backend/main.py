"""
Canonical backend entrypoint.

Delegates all app configuration (middleware, routers, CORS, lifecycle)
to create_app() in backend.app_factory.  See ADR-0002 for rationale.

Usage:
    uvicorn backend.main:app          # production
    python -m backend.run_simple      # dev runner
"""

from backend.app_factory import create_app

app = create_app()
