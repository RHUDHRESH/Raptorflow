"""
Legacy moves module.

Deprecated: use backend.api.v1.moves.router (canonical moves API).
"""

from .moves import router

__all__ = ["router"]
