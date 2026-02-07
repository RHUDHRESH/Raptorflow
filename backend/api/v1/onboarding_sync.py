"""
Legacy onboarding module.

Deprecated: use backend.api.v1.onboarding.router (canonical onboarding API).
"""

from .onboarding import router

__all__ = ["router"]
