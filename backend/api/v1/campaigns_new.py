"""
Legacy campaigns module.

Deprecated: use backend.api.v1.campaigns.router (canonical campaigns API).
"""

from .campaigns import router

__all__ = ["router"]
