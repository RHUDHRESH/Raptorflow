"""
Unit tests for Campaign domain entities.
"""

import pytest
from datetime import datetime

from backend.features.campaign.domain.entities import (
    Campaign,
    ALLOWED_OBJECTIVES,
    ALLOWED_STATUSES,
    DEFAULT_OBJECTIVE,
    DEFAULT_STATUS,
)
from backend.core.exceptions import ValidationError


class TestCampaign:
    """Tests for Campaign domain entity."""

    def test_create_campaign_with_defaults(self):
        """Test creating a campaign with default values."""
        campaign = Campaign(
            id="test-123",
            workspace_id="ws-456",
            title="Test Campaign",
        )

        assert campaign.id == "test-123"
        assert campaign.workspace_id == "ws-456"
        assert campaign.title == "Test Campaign"
        assert campaign.objective == DEFAULT_OBJECTIVE
        assert campaign.status == DEFAULT_STATUS

    def test_create_campaign_with_all_fields(self):
        """Test creating a campaign with all fields."""
        campaign = Campaign(
            id="test-123",
            workspace_id="ws-456",
            title="Test Campaign",
            description="A test campaign",
            objective="convert",
            status="active",
        )

        assert campaign.description == "A test campaign"
        assert campaign.objective == "convert"
        assert campaign.status == "active"

    def test_validate_rejects_empty_title(self):
        """Test that empty title raises ValidationError."""
        with pytest.raises(ValidationError):
            Campaign(
                id="test-123",
                workspace_id="ws-456",
                title="",
            )

    def test_validate_rejects_invalid_objective(self):
        """Test that invalid objective raises ValidationError."""
        with pytest.raises(ValidationError):
            Campaign(
                id="test-123",
                workspace_id="ws-456",
                title="Test",
                objective="invalid",
            )

    def test_validate_rejects_invalid_status(self):
        """Test that invalid status raises ValidationError."""
        with pytest.raises(ValidationError):
            Campaign(
                id="test-123",
                workspace_id="ws-456",
                title="Test",
                status="invalid",
            )

    def test_activate_campaign(self):
        """Test activating a campaign."""
        campaign = Campaign(
            id="test-123",
            workspace_id="ws-456",
            title="Test Campaign",
            status="planned",
        )
        campaign.activate()

        assert campaign.status == "active"
        assert campaign.updated_at is not None

    def test_cannot_activate_archived_campaign(self):
        """Test that archived campaigns cannot be activated."""
        campaign = Campaign(
            id="test-123",
            workspace_id="ws-456",
            title="Test Campaign",
            status="archived",
        )

        with pytest.raises(ValidationError):
            campaign.activate()

    def test_archive_campaign(self):
        """Test archiving a campaign."""
        campaign = Campaign(
            id="test-123",
            workspace_id="ws-456",
            title="Test Campaign",
            status="active",
        )
        campaign.archive()

        assert campaign.status == "archived"

    def test_update_title(self):
        """Test updating campaign title."""
        campaign = Campaign(
            id="test-123",
            workspace_id="ws-456",
            title="Old Title",
        )
        campaign.update_title("New Title")

        assert campaign.title == "New Title"

    def test_update_objective(self):
        """Test updating campaign objective."""
        campaign = Campaign(
            id="test-123",
            workspace_id="ws-456",
            title="Test",
            objective="acquire",
        )
        campaign.update_objective("convert")

        assert campaign.objective == "convert"

    def test_to_dict(self):
        """Test converting campaign to dictionary."""
        campaign = Campaign(
            id="test-123",
            workspace_id="ws-456",
            title="Test Campaign",
            description="Description",
            objective="acquire",
            status="active",
        )

        data = campaign.to_dict()

        assert data["id"] == "test-123"
        assert data["workspace_id"] == "ws-456"
        assert data["title"] == "Test Campaign"
        assert data["description"] == "Description"
        assert data["objective"] == "acquire"
        assert data["status"] == "active"

    def test_from_dict(self):
        """Test creating campaign from dictionary."""
        data = {
            "id": "test-123",
            "workspace_id": "ws-456",
            "title": "Test Campaign",
            "description": "Description",
            "objective": "acquire",
            "status": "active",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }

        campaign = Campaign.from_dict(data)

        assert campaign.id == "test-123"
        assert campaign.workspace_id == "ws-456"
        assert campaign.title == "Test Campaign"
        assert campaign.description == "Description"
        assert campaign.objective == "acquire"
        assert campaign.status == "active"


class TestCampaignConstants:
    """Tests for campaign constants."""

    def test_allowed_objectives(self):
        """Test allowed objectives."""
        assert "acquire" in ALLOWED_OBJECTIVES
        assert "convert" in ALLOWED_OBJECTIVES
        assert "launch" in ALLOWED_OBJECTIVES
        assert "proof" in ALLOWED_OBJECTIVES
        assert "retain" in ALLOWED_OBJECTIVES
        assert "reposition" in ALLOWED_OBJECTIVES

    def test_allowed_statuses(self):
        """Test allowed statuses."""
        assert "planned" in ALLOWED_STATUSES
        assert "active" in ALLOWED_STATUSES
        assert "paused" in ALLOWED_STATUSES
        assert "wrapup" in ALLOWED_STATUSES
        assert "archived" in ALLOWED_STATUSES

    def test_default_values(self):
        """Test default values."""
        assert DEFAULT_OBJECTIVE == "acquire"
        assert DEFAULT_STATUS == "active"
