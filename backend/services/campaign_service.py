"""
Campaign Service Compatibility Shim.

This module provides backward compatibility for code importing
from backend.services.campaign_service.

The correct import path is:
    from backend.services import campaign_service

This shim exists for legacy code that uses:
    from backend.services.campaign_service import campaign_service
"""

from backend.services import campaign_service

__all__ = ["campaign_service"]
