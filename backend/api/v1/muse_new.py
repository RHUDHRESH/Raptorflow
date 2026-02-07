"""
Legacy muse module.

Deprecated: use backend.api.v1.muse.router (canonical muse API).
"""

from .muse import router

__all__ = ["router"]
