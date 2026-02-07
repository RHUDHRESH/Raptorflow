"""
Legacy onboarding migration module.

Deprecated: use backend.api.v1.onboarding.router_migration (canonical onboarding API).
"""

from .onboarding import router_migration as router

__all__ = ["router"]
