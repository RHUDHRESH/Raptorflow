import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from api.v1.campaigns import router as campaigns_router
from models.api_models import CampaignCreateRequest, CampaignUpdateRequest
from services.campaign_service import CampaignService


class TestCampaignCRUDSimple:
    """Simplified test suite for Campaign CRUD operations."""

    @pytest.fixture
    def mock_campaign_service(self):
        """Mock campaign service for testing."""
        service = AsyncMock(spec=CampaignService)
        return service

    @pytest.fixture
    def sample_campaign_data(self):
        """Sample campaign data for testing."""
        return {
            "id": str(uuid4()),
            "title": "Test Campaign",
            "objective": "Test objective for campaign",
            "status": "draft",
            "workspace_id": str(uuid4()),
            "campaign_tag": "test-campaign-abc123",
            "arc_data": {"phases": ["Phase 1", "Phase 2"]},
            "phase_order": ["Phase 1", "Phase 2"],
            "milestones": [{"title": "Milestone 1", "due_date": "2024-01-01"}],
            "kpi_targets": {"leads": 100, "conversions": 10},
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }

    @pytest.mark.asyncio
    async def test_create_campaign_success(
        self, mock_campaign_service, sample_campaign_data
    ):
        """Test successful campaign creation."""
        # Setup mock
        mock_campaign_service.create_campaign.return_value = sample_campaign_data

        with patch(
            "api.v1.campaigns.get_campaign_service", return_value=mock_campaign_service
        ):
            from api.v1.campaigns import create_campaign

            request = CampaignCreateRequest(
                title=sample_campaign_data["title"],
                objective=sample_campaign_data["objective"],
                status=sample_campaign_data["status"],
            )

            result = await create_campaign(
                campaign_data=request,
                workspace_id=uuid4(),
                _current_user={"id": "test_user"},
                service=mock_campaign_service,
            )

            assert result.success is True
            assert result.data["title"] == sample_campaign_data["title"]
            assert result.data["objective"] == sample_campaign_data["objective"]
            mock_campaign_service.create_campaign.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_campaigns_success(
        self, mock_campaign_service, sample_campaign_data
    ):
        """Test successful campaign listing."""
        mock_campaign_service.list_campaigns.return_value = [sample_campaign_data]

        with patch(
            "api.v1.campaigns.get_campaign_service", return_value=mock_campaign_service
        ):
            from api.v1.campaigns import list_campaigns

            result = await list_campaigns(
                status="draft",
                search="test",
                limit=10,
                offset=0,
                workspace_id=uuid4(),
                _current_user={"id": "test_user"},
                service=mock_campaign_service,
            )

            assert result.success is True
            assert len(result.data["campaigns"]) == 1
            assert result.data["campaigns"][0]["title"] == sample_campaign_data["title"]
            mock_campaign_service.list_campaigns.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_campaign_detail_success(
        self, mock_campaign_service, sample_campaign_data
    ):
        """Test successful campaign detail retrieval."""
        campaign_with_moves = {
            **sample_campaign_data,
            "moves": [{"id": str(uuid4()), "title": "Test Move", "status": "pending"}],
        }
        mock_campaign_service.get_campaign_with_moves.return_value = campaign_with_moves

        with patch(
            "api.v1.campaigns.get_campaign_service", return_value=mock_campaign_service
        ):
            from api.v1.campaigns import get_campaign_detail

            result = await get_campaign_detail(
                campaign_id=sample_campaign_data["id"],
                workspace_id=uuid4(),
                _current_user={"id": "test_user"},
                service=mock_campaign_service,
            )

            assert result.success is True
            assert result.data["campaign"]["id"] == sample_campaign_data["id"]
            assert len(result.data["campaign"]["moves"]) == 1
            assert result.data["campaign"]["moves"][0]["title"] == "Test Move"

    @pytest.mark.asyncio
    async def test_get_campaign_detail_not_found(self, mock_campaign_service):
        """Test campaign detail retrieval when campaign not found."""
        mock_campaign_service.get_campaign_with_moves.return_value = None

        with patch(
            "api.v1.campaigns.get_campaign_service", return_value=mock_campaign_service
        ):
            from fastapi import HTTPException

            from api.v1.campaigns import get_campaign_detail

            with pytest.raises(HTTPException) as exc_info:
                await get_campaign_detail(
                    campaign_id=str(uuid4()),
                    workspace_id=uuid4(),
                    _current_user={"id": "test_user"},
                    service=mock_campaign_service,
                )

            assert exc_info.value.status_code == 404
            assert "Campaign not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_update_campaign_success(
        self, mock_campaign_service, sample_campaign_data
    ):
        """Test successful campaign update."""
        updated_data = {**sample_campaign_data, "title": "Updated Campaign"}
        mock_campaign_service.update_campaign.return_value = updated_data

        with patch(
            "api.v1.campaigns.get_campaign_service", return_value=mock_campaign_service
        ):
            from api.v1.campaigns import update_campaign

            request = CampaignUpdateRequest(title="Updated Campaign")

            result = await update_campaign(
                campaign_id=sample_campaign_data["id"],
                payload=request,
                workspace_id=uuid4(),
                _current_user={"id": "test_user"},
                service=mock_campaign_service,
            )

            assert result.success is True
            assert result.data["campaign"]["title"] == "Updated Campaign"
            mock_campaign_service.update_campaign.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_campaign_not_found(self, mock_campaign_service):
        """Test campaign update when campaign not found."""
        mock_campaign_service.update_campaign.return_value = None

        with patch(
            "api.v1.campaigns.get_campaign_service", return_value=mock_campaign_service
        ):
            from fastapi import HTTPException

            from api.v1.campaigns import update_campaign

            with pytest.raises(HTTPException) as exc_info:
                await update_campaign(
                    campaign_id=str(uuid4()),
                    payload=CampaignUpdateRequest(title="Updated"),
                    workspace_id=uuid4(),
                    _current_user={"id": "test_user"},
                    service=mock_campaign_service,
                )

            assert exc_info.value.status_code == 404
            assert "not found or not writable" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_soft_delete_campaign_success(self, mock_campaign_service):
        """Test successful campaign soft delete."""
        mock_campaign_service.soft_delete_campaign.return_value = None

        with patch(
            "api.v1.campaigns.get_campaign_service", return_value=mock_campaign_service
        ):
            from api.v1.campaigns import delete_campaign

            result = await delete_campaign(
                campaign_id=str(uuid4()),
                workspace_id=uuid4(),
                _current_user={"id": "test_user"},
                service=mock_campaign_service,
            )

            assert result.success is True
            assert result.data["status"] == "archived"
            mock_campaign_service.soft_delete_campaign.assert_called_once()

    @pytest.mark.asyncio
    async def test_campaign_tag_generation(self):
        """Test campaign tag generation uniqueness."""
        from api.v1.council import _slugify_campaign_title

        title = "Test Campaign Title"
        tag1 = _slugify_campaign_title(title)
        tag2 = _slugify_campaign_title(title)

        # Tags should be unique due to UUID suffix
        assert tag1 != tag2
        assert tag1.startswith("test-campaign-title-")
        assert tag2.startswith("test-campaign-title-")
        assert len(tag1.split("-")[-1]) == 6  # UUID hex part

    @pytest.mark.asyncio
    async def test_campaign_service_error_handling(self, mock_campaign_service):
        """Test proper error handling in campaign operations."""
        mock_campaign_service.create_campaign.side_effect = Exception("Service error")

        with patch(
            "api.v1.campaigns.get_campaign_service", return_value=mock_campaign_service
        ):
            from fastapi import HTTPException

            from api.v1.campaigns import create_campaign

            with pytest.raises(HTTPException) as exc_info:
                await create_campaign(
                    campaign_data=CampaignCreateRequest(
                        title="Test", objective="Test objective"
                    ),
                    workspace_id=uuid4(),
                    _current_user={"id": "test_user"},
                    service=mock_campaign_service,
                )

            assert exc_info.value.status_code == 500
            assert "Internal server error" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_campaign_move_association_data_structure(self):
        """Test that campaign and move data structures are compatible."""
        from models.api_models import (
            CouncilCampaignCreateRequest,
            CouncilCampaignPayload,
            CouncilMovePayload,
        )

        # Test campaign payload structure
        campaign_payload = CouncilCampaignPayload(
            title="Test Campaign",
            objective="Test objective",
            arc_data={"phases": ["Phase 1", "Phase 2"]},
        )

        # Test move payload structure
        move_payload = CouncilMovePayload(
            title="Test Move",
            description="Test move description",
            move_type="content",
            priority=3,
            tool_requirements=["tool1", "tool2"],
            refinement_data={"muse_prompt": "Test prompt"},
        )

        # Test request structure
        request = CouncilCampaignCreateRequest(
            workspace_id=str(uuid4()),
            campaign_data=campaign_payload,
            moves=[move_payload],
        )

        assert request.campaign_data.title == "Test Campaign"
        assert len(request.moves) == 1
        assert request.moves[0].title == "Test Move"
        assert request.moves[0].move_type == "content"
