"""
Asset adapters module.
"""

from backend.features.asset.adapters.supabase_repo import SupabaseAssetRepository
from backend.features.asset.adapters.storage import SupabaseStorageService

__all__ = ["SupabaseAssetRepository", "SupabaseStorageService"]
