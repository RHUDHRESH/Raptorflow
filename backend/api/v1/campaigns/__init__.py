# Campaign API router
# Uses orchestrator for backward compatibility
# TODO: Migrate to modular router.py after adding missing endpoints
from backend.api.v1.campaigns.routes import router

__all__ = ["router"]
