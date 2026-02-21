"""
Services package for RaptorFlow.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

bcm_service = None
campaign_service = None
move_service = None
email_service = None
auth_service = None
bcm_cache = None
bcm_memory = None
bcm_generation_logger = None
cached_queries = None

try:
    from backend.services.bcm.service import bcm_service
except Exception as e:
    logger.warning(f"Failed to import bcm_service: {e}")

try:
    from backend.services.campaign.service import CampaignService

    campaign_service = CampaignService()
except Exception as e:
    logger.warning(f"Failed to import campaign_service: {e}")

try:
    from backend.services.move.service import MoveService

    move_service = MoveService()
except Exception as e:
    logger.warning(f"Failed to import move_service: {e}")

try:
    from backend.services.email.service import EmailService

    email_service = EmailService()
except Exception as e:
    logger.warning(f"Failed to import email_service: {e}")

try:
    from backend.services.auth.factory import get_auth_service

    auth_service = get_auth_service()
except Exception as e:
    logger.warning(f"Failed to import auth_service: {e}")
    auth_service = None

try:
    from backend.core.cache import get_cache_client

    bcm_cache = get_cache_client()
except Exception as e:
    logger.warning(f"Failed to import bcm_cache: {e}")

try:
    from backend.bcm.memory import get_memory_client

    bcm_memory = get_memory_client()
except Exception as e:
    logger.warning(f"Failed to import bcm_memory: {e}")

try:
    from backend.services.bcm import generation_logger as bcm_generation_logger
except Exception as e:
    logger.warning(f"Failed to import bcm_generation_logger: {e}")

try:
    import backend.services.cached_queries as cached_queries
except Exception as e:
    logger.warning(f"Failed to import cached_queries: {e}")

__all__ = [
    "bcm_service",
    "campaign_service",
    "move_service",
    "email_service",
    "auth_service",
    "bcm_cache",
    "bcm_memory",
    "bcm_generation_logger",
    "cached_queries",
]
