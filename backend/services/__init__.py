"""
Services package for RaptorFlow.

Imports all services to ensure they register with the ServiceRegistry.
Services with missing dependencies are skipped gracefully.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Import services to trigger registration with ServiceRegistry
# These imports have side effects (registering with registry)

bcm_service = None
campaign_service = None
move_service = None
muse_service = None
email_service = None
vertex_ai_service = None

try:
    from backend.services.bcm_service import bcm_service
except Exception as e:
    logger.warning(f"Failed to import bcm_service: {e}")

try:
    from backend.services.campaign_service import campaign_service
except Exception as e:
    logger.warning(f"Failed to import campaign_service: {e}")

try:
    from backend.services.move_service import move_service
except Exception as e:
    logger.warning(f"Failed to import move_service: {e}")

try:
    from backend.services.muse_service import muse_service
except Exception as e:
    logger.warning(f"Failed to import muse_service: {e}")

try:
    from backend.services.email_service import email_service
except Exception as e:
    logger.warning(f"Failed to import email_service: {e}")

try:
    from backend.services.vertex_ai_service import vertex_ai_service
except Exception as e:
    logger.warning(f"Failed to import vertex_ai_service: {e}")

__all__ = [
    "bcm_service",
    "campaign_service", 
    "move_service",
    "muse_service",
    "email_service",
    "vertex_ai_service",
]


