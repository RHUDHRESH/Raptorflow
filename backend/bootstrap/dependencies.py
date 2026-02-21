"""
Bootstrap - Dependency Injection providers.

This module provides pure dependency providers WITHOUT FastAPI integration.
For FastAPI Depends() integration, use backend/api/dependencies.py instead.

This separation maintains hexagonal architecture:
- bootstrap/providers.py - Pure Python, no framework dependencies
- api/dependencies.py - FastAPI-specific wiring
"""

from functools import lru_cache
from typing import TYPE_CHECKING

from backend.core.database.supabase import get_supabase_client
from backend.services.campaign.adapters import SupabaseCampaignRepository
from backend.services.campaign.application import CampaignService
from backend.services.asset.adapters import (
    SupabaseAssetRepository,
    SupabaseStorageService,
)
from backend.services.asset.application import AssetService

if TYPE_CHECKING:
    from supabase import Client


# =============================================================================
# Infrastructure Providers
# =============================================================================


@lru_cache
def _get_supabase_client() -> "Client":
    """Get the Supabase client instance."""
    return get_supabase_client()


# =============================================================================
# Campaign Feature Providers
# =============================================================================


def get_campaign_repository() -> SupabaseCampaignRepository:
    """
    Get a Supabase campaign repository.

    Returns a new instance each time (not cached) to avoid
    shared state issues.
    """
    client = _get_supabase_client()
    return SupabaseCampaignRepository(client)


def get_campaign_service(repository: SupabaseCampaignRepository) -> CampaignService:
    """
    Get a CampaignService with injected repository.

    This is a pure function that can be used without FastAPI.
    For FastAPI integration, use backend.api.dependencies.CampaignServiceDep.
    """
    return CampaignService(repository)


# =============================================================================
# Asset Feature Providers
# =============================================================================


def get_asset_repository() -> SupabaseAssetRepository:
    """Get a Supabase asset repository."""
    client = _get_supabase_client()
    return SupabaseAssetRepository(client)


def get_storage_service() -> SupabaseStorageService:
    """Get a Supabase storage service."""
    from backend.core.storage.manager import StorageManager

    storage = StorageManager()
    return SupabaseStorageService(storage)


def get_asset_service(
    repository: SupabaseAssetRepository,
    storage: SupabaseStorageService,
) -> AssetService:
    """Get an AssetService with injected dependencies."""
    from backend.core.config import get_settings

    settings = get_settings()
    return AssetService(repository, storage, settings.SUPABASE_STORAGE_BUCKET)


# =============================================================================
# Auth Feature Providers
# =============================================================================


def get_auth_service():
    """Get the configured auth service based on AUTH_MODE."""
    from backend.services.auth.factory import get_auth_service as _get_auth_service

    return _get_auth_service()


def get_authentication_service(auth_service):
    """Get an AuthenticationService with injected dependencies."""
    from backend.services.auth.application import AuthenticationService

    return AuthenticationService(auth_service)
