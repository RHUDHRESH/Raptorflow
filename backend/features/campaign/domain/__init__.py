"""
Campaign domain module.

Exports domain entities and business rules.
"""

from backend.features.campaign.domain.entities import (
    Campaign,
    ALLOWED_OBJECTIVES,
    ALLOWED_STATUSES,
    DEFAULT_OBJECTIVE,
    DEFAULT_STATUS,
)

__all__ = [
    "Campaign",
    "ALLOWED_OBJECTIVES",
    "ALLOWED_STATUSES",
    "DEFAULT_OBJECTIVE",
    "DEFAULT_STATUS",
]
