"""
Campaign feature module.

A vertical slice containing domain, application, and adapter layers
following hexagonal architecture principles.
"""

from backend.features.campaign.domain import Campaign
from backend.features.campaign.application import CampaignRepository, CampaignService
from backend.features.campaign.adapters import SupabaseCampaignRepository

__all__ = [
    "Campaign",
    "CampaignRepository",
    "CampaignService",
    "SupabaseCampaignRepository",
]
