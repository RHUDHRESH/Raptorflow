"""
Campaign application services (Use Cases).

These contain the business logic orchestration.
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from backend.core.exceptions import NotFoundError, ValidationError
from backend.features.campaign.application.ports import CampaignRepository
from backend.features.campaign.domain.entities import (
    Campaign,
    ALLOWED_OBJECTIVES,
    ALLOWED_STATUSES,
    DEFAULT_OBJECTIVE,
    DEFAULT_STATUS,
)


class CampaignService:
    """
    Application service for campaign operations.

    This is the use case layer - it orchestrates business logic
    but delegates persistence to the injected repository.
    """

    def __init__(self, repository: CampaignRepository):
        self._repository = repository

    async def list_campaigns(self, workspace_id: str) -> list[Campaign]:
        """List all campaigns for a workspace."""
        return await self._repository.list_by_workspace(workspace_id)

    async def get_campaign(
        self, workspace_id: str, campaign_id: str
    ) -> Optional[Campaign]:
        """Get a specific campaign."""
        return await self._repository.get_by_id(campaign_id, workspace_id)

    async def create_campaign(
        self,
        workspace_id: str,
        title: str,
        description: Optional[str] = None,
        objective: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Campaign:
        """
        Create a new campaign.

        Validates input and delegates to repository.
        """
        # Normalize objective
        normalized_objective = self._normalize_objective(objective)

        # Normalize status
        normalized_status = self._normalize_status(status)

        # Create domain entity
        campaign = Campaign(
            id=str(uuid4()),
            workspace_id=workspace_id,
            title=title.strip(),
            description=description,
            objective=normalized_objective,
            status=normalized_status,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Persist
        return await self._repository.save(campaign)

    async def update_campaign(
        self,
        workspace_id: str,
        campaign_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        objective: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Campaign:
        """
        Update an existing campaign.

        Validates input and applies business rules.
        """
        # Get existing campaign
        campaign = await self._repository.get_by_id(campaign_id, workspace_id)
        if not campaign:
            raise NotFoundError(f"Campaign {campaign_id} not found")

        # Apply updates
        if title is not None:
            campaign.update_title(title)

        if description is not None:
            campaign.description = description
            campaign.updated_at = datetime.utcnow()

        if objective is not None:
            campaign.update_objective(objective)

        if status is not None:
            normalized_status = self._normalize_status(status)
            campaign.status = normalized_status
            campaign.updated_at = datetime.utcnow()

        # Persist
        return await self._repository.save(campaign)

    async def delete_campaign(self, workspace_id: str, campaign_id: str) -> bool:
        """Delete a campaign."""
        return await self._repository.delete(campaign_id, workspace_id)

    def _normalize_objective(self, objective: Optional[str]) -> str:
        """Normalize objective value."""
        if not objective:
            return DEFAULT_OBJECTIVE

        normalized = objective.strip().lower()
        if normalized not in ALLOWED_OBJECTIVES:
            raise ValidationError(
                f"Invalid objective '{objective}'. Allowed: {', '.join(sorted(ALLOWED_OBJECTIVES))}"
            )
        return normalized

    def _normalize_status(self, status: Optional[str]) -> str:
        """Normalize status value."""
        if not status:
            return DEFAULT_STATUS

        normalized = status.strip().lower()
        if normalized not in ALLOWED_STATUSES:
            raise ValidationError(
                f"Invalid status '{status}'. Allowed: {', '.join(sorted(ALLOWED_STATUSES))}"
            )
        return normalized
