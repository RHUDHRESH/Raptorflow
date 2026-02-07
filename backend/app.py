"""
Compatibility shim for the `app` package.

This module exists to allow legacy imports like `from app.auth_middleware import ...`
to continue working while the canonical FastAPI application lives in `backend.main`.
Do not use this file as an entrypoint.
"""

from pathlib import Path

# Treat this module as a package pointing at backend/app/
__path__ = [str(Path(__file__).with_name("app"))]

__all__ = ["__path__"]
