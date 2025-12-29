import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from api.v1.campaigns import router as campaigns_router
from api.v1.council import router as council_router
from models.api_models import (
    CampaignCreateRequest,
    CampaignUpdateRequest,
    CouncilCampaignCreateRequest,
    CouncilCampaignPayload,
    CouncilMovePayload,
)
from services.campaign_service import CampaignService


class TestCampaignCRUD:
    """Test suite for Campaign CRUD operations."""

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

    @pytest.fixture
    def sample_move_data(self):
        """Sample move data for testing."""
        return {
            "id": str(uuid4()),
            "title": "Test Move",
            "description": "Test move description",
            "status": "pending",
            "priority": 3,
            "move_type": "content",
            "campaign_id": str(uuid4()),
            "workspace_id": str(uuid4()),
            "campaign_name": "Test Campaign",
            "tool_requirements": ["tool1", "tool2"],
            "refinement_data": {"muse_prompt": "Test prompt"},
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
    async def test_create_campaign_with_moves_transactional(
        self, sample_campaign_data, sample_move_data
    ):
        """Test successful campaign creation with associated moves using transactions."""
        campaign_payload = CouncilCampaignPayload(
            title=sample_campaign_data["title"],
            objective=sample_campaign_data["objective"],
            arc_data=sample_campaign_data["arc_data"],
        )

        move_payload = CouncilMovePayload(
            title=sample_move_data["title"],
            description=sample_move_data["description"],
            move_type=sample_move_data["move_type"],
            priority=sample_move_data["priority"],
            tool_requirements=sample_move_data["tool_requirements"],
            refinement_data=sample_move_data["refinement_data"],
        )

        request = CouncilCampaignCreateRequest(
            workspace_id=sample_campaign_data["workspace_id"],
            campaign_data=campaign_payload,
            moves=[move_payload],
        )

        # Mock the transaction context manager
        with patch("db.get_db_transaction") as mock_transaction:
            mock_conn = AsyncMock()
            mock_cur = AsyncMock()
            # Make cursor properly support async context manager
            mock_cur.__aenter__ = AsyncMock(return_value=mock_cur)
            mock_cur.__aexit__ = AsyncMock(return_value=None)
            # cursor() returns a coroutine that resolves to the cursor context manager
            mock_conn.cursor.return_value = mock_cur
            mock_conn.cursor = AsyncMock(return_value=mock_cur)
            mock_transaction.return_value.__aenter__.return_value = mock_conn

            # Mock campaign creation
            mock_cur.fetchone.return_value = [sample_campaign_data["id"]]

            # Mock move creation
            move_results = [[sample_move_data["id"]]]
            mock_cur.fetchone.side_effect = move_results

            from api.v1.council import persist_campaign_with_moves

            result = await persist_campaign_with_moves(
                payload=request, _current_user={"id": "test_user"}
            )

            assert result["success"] is True
            assert result["campaign_id"] == sample_campaign_data["id"]
            assert result["move_ids"] == [sample_move_data["id"]]
            assert "campaign_tag" in result
            assert result["move_count"] == 1

            # Verify transaction was used
            mock_transaction.assert_called_once()
            assert mock_cur.execute.call_count >= 2  # One for campaign, one for move

    @pytest.mark.asyncio
    async def test_create_campaign_with_moves_transaction_rollback(
        self, sample_campaign_data, sample_move_data
    ):
        """Test transaction rollback on campaign creation failure."""
        campaign_payload = CouncilCampaignPayload(
            title=sample_campaign_data["title"],
            objective=sample_campaign_data["objective"],
            arc_data=sample_campaign_data["arc_data"],
        )

        move_payload = CouncilMovePayload(
            title=sample_move_data["title"],
            description=sample_move_data["description"],
            move_type=sample_move_data["move_type"],
        )

        request = CouncilCampaignCreateRequest(
            workspace_id=sample_campaign_data["workspace_id"],
            campaign_data=campaign_payload,
            moves=[move_payload],
        )

        # Mock transaction failure
        with patch("db.get_db_transaction") as mock_transaction:
            mock_transaction.side_effect = Exception("Database error")

            from fastapi import HTTPException

            from api.v1.council import persist_campaign_with_moves

            with pytest.raises(HTTPException) as exc_info:
                await persist_campaign_with_moves(
                    payload=request, _current_user={"id": "test_user"}
                )

            assert exc_info.value.status_code == 500
            assert "Transaction rolled back" in str(exc_info.value.detail)

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
        self, mock_campaign_service, sample_campaign_data, sample_move_data
    ):
        """Test successful campaign detail retrieval."""
        campaign_with_moves = {**sample_campaign_data, "moves": [sample_move_data]}
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
            assert (
                result.data["campaign"]["moves"][0]["title"]
                == sample_move_data["title"]
            )

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
    async def test_moves_filtering_by_campaign_and_status(
        self, mock_campaign_service, sample_move_data
    ):
        """Test moves filtering by campaign_id and status."""
        # This test would be for the moves API endpoint
        with patch("api.v1.moves.get_move_service") as mock_get_service:
            mock_move_service = AsyncMock()
            mock_get_service.return_value = mock_move_service
            mock_move_service.list_moves.return_value = [sample_move_data]

            from api.v1.moves import list_moves

            workspace_id = uuid4()
            result = await list_moves(
                campaign_id=sample_move_data["campaign_id"],
                status="pending",
                limit=10,
                offset=0,
                tenant_id=workspace_id,
                _current_user={"id": "test_user"},
                service=mock_move_service,
            )

            assert result.success is True
            assert len(result.data["moves"]) == 1
            mock_move_service.list_moves.assert_called_once_with(
                str(workspace_id),
                campaign_id=sample_move_data["campaign_id"],
                status="pending",
                limit=10,
                offset=0,
            )

    @pytest.mark.asyncio
    async def test_campaign_move_association_consistency(self):
        """Test that moves are properly associated with campaigns."""
        campaign_id = str(uuid4())
        workspace_id = str(uuid4())

        campaign_payload = CouncilCampaignPayload(
            title="Test Campaign", objective="Test objective", arc_data={}
        )

        move_payload = CouncilMovePayload(
            title="Test Move", description="Test description", move_type="content"
        )

        request = CouncilCampaignCreateRequest(
            workspace_id=workspace_id,
            campaign_data=campaign_payload,
            moves=[move_payload],
        )

        with patch("db.get_db_transaction") as mock_transaction:
            mock_conn = AsyncMock()
            mock_cur = AsyncMock()
            # Make cursor properly support async context manager
            mock_cur.__aenter__ = AsyncMock(return_value=mock_cur)
            mock_cur.__aexit__ = AsyncMock(return_value=None)
            # cursor() returns a coroutine that resolves to the cursor context manager
            mock_conn.cursor = AsyncMock(return_value=mock_cur)
            mock_transaction.return_value.__aenter__.return_value = mock_conn

            # Mock campaign creation
            campaign_result = [campaign_id]
            # Mock move creation
            move_result = [str(uuid4())]

            mock_cur.fetchone.side_effect = [campaign_result, move_result]

            from api.v1.council import persist_campaign_with_moves

            result = await persist_campaign_with_moves(
                payload=request, _current_user={"id": "test_user"}
            )

            # Verify the move was created with the correct campaign_id
            move_execute_call = mock_cur.execute.call_args_list[1]
            move_args = move_execute_call[0][1]  # Second argument (the tuple of values)

            assert move_args[0] == campaign_id  # campaign_id should match
            assert move_args[1] == workspace_id  # workspace_id should match

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
