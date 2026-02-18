"""
Campaign adapters module.

Exports repository implementations.
"""

from backend.features.campaign.adapters.supabase_repo import SupabaseCampaignRepository

__all__ = [
    "SupabaseCampaignRepository",
]
