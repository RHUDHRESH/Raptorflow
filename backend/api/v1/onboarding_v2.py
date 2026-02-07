"""
Legacy onboarding v2 module.

Deprecated: use backend.api.v1.onboarding.router_v2 (canonical onboarding API).
"""

from .onboarding import router_v2 as router

__all__ = ["router"]
