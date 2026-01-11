"""
Tests for database repositories
"""

from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from ...db.filters import Filter
from ...db.pagination import PaginatedResult, Pagination
from ...db.repositories import (
    AgentExecutionRepository,
    BlackboxRepository,
    CampaignRepository,
    DailyWinsRepository,
    FoundationRepository,
    ICPRepository,
    MoveRepository,
    MuseAssetRepository,
)


class TestFoundationRepository:
    """Test FoundationRepository"""

    @pytest.fixture
    def repository(self, mock_supabase_client):
        return FoundationRepository()

    @pytest.fixture
    def mock_supabase_client(self):
        client = AsyncMock()
        client.table = MagicMock()
        client.table.return_value.select.return_value.execute.return_value = AsyncMock(
            return_value={"data": []}
        )
        client.table.return_value.insert.return_value.execute.return_value = AsyncMock(
            return_value={"data": [{"id": "test-id"}]}
        )
        client.table.return_value.update.return_value.execute.return_value = AsyncMock(
            return_value={"data": [{"id": "test-id"}]}
        )
        client.table.return_value.delete.return_value.execute.return_value = AsyncMock(
            return_value={"data": [{"id": "test-id"}]}
        )
        client.rpc = MagicMock()
        client.rpc.return_value.execute.return_value = AsyncMock(
            return_value={"data": []}
        )
        return client

    @pytest.mark.asyncio
    async def test_get_by_workspace(
        self, repository, mock_supabase_client, sample_foundation
    ):
        """Test getting foundation by workspace"""
        # Setup mock
        mock_supabase_client.table.return_value.select.return_value.execute.return_value = AsyncMock(
            return_value={"data": [sample_foundation]}
        )

        # Execute
        result = await repository.get_by_workspace("test-workspace-id")

        # Assert
        assert isinstance(result, dict)
        assert result["id"] == "test-foundation-id"
        assert result["workspace_id"] == "test-workspace-id"
        mock_supabase_client.table.assert_called_with("foundations")

    @pytest.mark.asyncio
    async def test_upsert_new(
        self, repository, mock_supabase_client, sample_foundation
    ):
        """Test upserting new foundation"""
        # Setup mock
        mock_supabase_client.table.return_value.select.return_value.execute.return_value = AsyncMock(
            return_value={"data": []}  # No existing foundation
        )
        mock_supabase_client.table.return_value.upsert.return_value.execute.return_value = AsyncMock(
            return_value={"data": [sample_foundation]}
        )

        # Execute
        result = await repository.upsert("test-workspace-id", sample_foundation)

        # Assert
        assert result["id"] == "test-foundation-id"
        mock_supabase_client.table.return_value.upsert.assert_called_once()

    @pytest.mark.asyncio
    async def test_upsert_existing(
        self, repository, mock_supabase_client, sample_foundation
    ):
        """Test upserting existing foundation"""
        # Setup mock
        mock_supabase_client.table.return_value.select.return_value.execute.return_value = AsyncMock(
            return_value={"data": [sample_foundation]}  # Existing foundation
        )
        mock_supabase_client.table.return_value.update.return_value.execute.return_value = AsyncMock(
            return_value={"data": [sample_foundation]}
        )

        # Execute
        result = await repository.upsert("test-workspace-id", sample_foundation)

        # Assert
        assert result["id"] == "test-foundation-id"
        mock_supabase_client.table.return_value.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_summary(
        self, repository, mock_supabase_client, sample_foundation
    ):
        """Test generating foundation summary"""
        # Setup mock
        mock_supabase_client.table.return_value.update.return_value.execute.return_value = AsyncMock(
            return_value={"data": [sample_foundation]}
        )

        # Execute
        result = await repository.generate_summary("test-workspace-id")

        # Assert
        assert result is not None
        mock_supabase_client.table.return_value.update.assert_called_once()


class TestICPRepository:
    """Test ICPRepository"""

    @pytest.fixture
    def repository(self, mock_supabase_client):
        return ICPRepository()

    @pytest.fixture
    def mock_supabase_client(self):
        client = AsyncMock()
        client.table = MagicMock()
        client.table.return_value.select.return_value.execute.return_value = AsyncMock(
            return_value={"data": []}
        )
        client.table.return_value.insert.return_value.execute.return_value = AsyncMock(
            return_value={"data": [{"id": "test-id"}]}
        )
        client.table.return_value.update.return_value.execute.return_value = AsyncMock(
            return_value={"data": [{"id": "test-id"}]}
        )
        client.table.return_value.delete.return_value.execute.return_value = AsyncMock(
            return_value={"data": [{"id": "test-id"}]}
        )
        client.rpc = MagicMock()
        client.rpc.return_value.execute.return_value = AsyncMock(
            return_value={"data": []}
        )
        return client

    @pytest.mark.asyncio
    async def test_list_by_workspace(
        self, repository, mock_supabase_client, sample_icp
    ):
        """Test listing ICPs by workspace"""
        # Setup mock
        mock_supabase_client.table.return_value.select.return_value.execute.return_value = AsyncMock(
            return_value={"data": [sample_icp]}
        )

        # Execute
        result = await repository.list_by_workspace("test-workspace-id")

        # Assert
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["id"] == "test-icp-id"
        mock_supabase_client.table.assert_called_with("icp_profiles")

    @pytest.mark.asyncio
    async def test_get_primary(self, repository, mock_supabase_client, sample_icp):
        """Test getting primary ICP"""
        # Setup mock
        mock_supabase_client.table.return_value.select.return_value.execute.return_value = AsyncMock(
            return_value={"data": [sample_icp]}
        )

        # Execute
        result = await repository.get_primary("test-workspace-id")

        # Assert
        assert result["id"] == "test-icp-id"
        assert result["is_primary"] is True

    @pytest.mark.asyncio
    async def test_set_primary(self, repository, mock_supabase_client, sample_icp):
        """Test setting primary ICP"""
        # Setup mock
        mock_supabase_client.table.return_value.update.return_value.execute.return_value = AsyncMock(
            return_value={"data": [{"id": "test-id"}]}
        )

        # Execute
        result = await repository.set_primary("test-workspace-id", "test-icp-id")

        # Assert
        assert result is True
        mock_supabase_client.table.return_value.update.assert_called()

    @pytest.mark.asyncio
    async def test_count_by_workspace(self, repository, mock_supabase_client):
        """Test counting ICPs by workspace"""
        # Setup mock
        mock_supabase_client.table.return_value.select.return_value.execute.return_value = AsyncMock(
            return_value={"data": [{"count": 3}]}
        )

        # Execute
        result = await repository.count_by_workspace("test-workspace-id")

        # Assert
        assert result == 3
        mock_supabase_client.table.assert_called_with("icp_profiles")

    @pytest.mark.asyncio
    async def test_create_icp_validation(self, repository, mock_supabase_client):
        """Test ICP creation validation"""
        # Test invalid market sophistication
        invalid_icp = {
            "name": "Test ICP",
            "market_sophistication": 6,  # Invalid (should be 1-5)
            "fit_score": 105,  # Invalid (should be 0-100)
        }

        with pytest.raises(
            ValueError, match="Market sophistication must be between 1 and 5"
        ):
            await repository.create("test-workspace-id", invalid_icp)


class TestMoveRepository:
    """Test MoveRepository"""

    @pytest.fixture
    def repository(self, mock_supabase_client):
        return MoveRepository()

    @pytest.fixture
    def mock_supabase_client(self):
        client = AsyncMock()
        client.table = MagicMock()
        client.table.return_value.select.return_value.execute.return_value = AsyncMock(
            return_value={"data": []}
        )
        client.table.return_value.insert.return_value.execute.return_value = AsyncMock(
            return_value={"data": [{"id": "test-id"}]}
        )
        client.table.return_value.update.return_value.execute.return_value = AsyncMock(
            return_value={"data": [{"id": "test-id"}]}
        )
        client.table.return_value.delete.return_value.execute.return_value = AsyncMock(
            return_value={"data": [{"id": "test-id"}]}
        )
        return client

    @pytest.mark.asyncio
    async def test_list_by_campaign(
        self, repository, mock_supabase_client, sample_move
    ):
        """Test listing moves by campaign"""
        # Setup mock
        mock_supabase_client.table.return_value.select.return_value.execute.return_value = AsyncMock(
            return_value={"data": [sample_move]}
        )

        # Execute
        result = await repository.list_by_campaign("test-campaign-id")

        # Assert
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["id"] == "test-move-id"
        mock_supabase_client.table.assert_called_with("moves")

    @pytest.mark.asyncio
    async def test_list_active(self, repository, mock_supabase_client, sample_move):
        """Test listing active moves"""
        # Setup mock
        mock_supabase_client.table.return_value.select.return_value.execute.return_value = AsyncMock(
            return_value={"data": [sample_move]}
        )

        # Execute
        result = await repository.list_active("test-workspace-id")

        # Assert
        assert isinstance(result, list)
        assert len(result) == 1
        mock_supabase_client.table.assert_called_with("moves")

    @pytest.mark.asyncio
    async def test_update_status(self, repository, mock_supabase_client, sample_move):
        """Test updating move status"""
        # Setup mock
        mock_supabase_client.table.return_value.update.return_value.execute.return_value = AsyncMock(
            return_value={"data": [sample_move]}
        )

        # Execute
        result = await repository.update_status("test-move-id", "active")

        # Assert
        assert result["id"] == "test-move-id"
        assert result["status"] == "active"
        mock_supabase_client.table.return_value.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_with_tasks(self, repository, mock_supabase_client, sample_move):
        """Test getting move with tasks"""
        # Setup mock
        mock_supabase_client.table.return_value.select.return_value.execute.return_value = AsyncMock(
            return_value={"data": [sample_move]}
        )

        # Execute
        result = await repository.get_with_tasks("test-move-id")

        # Assert
        assert result["id"] == "test-move-id"
        mock_supabase_client.table.assert_called_with("moves")


class TestPagination:
    """Test pagination functionality"""

    @pytest.mark.asyncio
    async def test_pagination_creation(self):
        """Test pagination object creation"""
        pagination = Pagination(
            page=1, page_size=20, sort_by="created_at", sort_order="desc"
        )

        assert pagination.page == 1
        assert pagination.page_size == 20
        assert pagination.sort_by == "created_at"
        assert pagination.sort_order == "desc"

    @pytest.mark.asyncio
    async def test_paginated_result_creation(self):
        """Test paginated result creation"""
        items = [{"id": "1"}, {"id": "2"}]
        result = PaginatedResult(
            items=items, total=10, page=1, page_size=2, total_pages=5
        )

        assert result.items == items
        assert result.total == 10
        assert result.page == 1
        assert result.page_size == 2
        assert result.total_pages == 5

    @pytest.mark.asyncio
    async def test_paginated_result_calculation(self):
        """Test paginated result calculations"""
        # Test total pages calculation
        result = PaginatedResult(
            items=[{"id": "1"}], total=5, page=1, page_size=2, total_pages=3
        )

        assert result.total_pages == 3  # 5 items / 2 per page = 3 pages


class TestFilters:
    """Test filter functionality"""

    def test_filter_creation(self):
        """Test filter object creation"""
        filter_obj = Filter(field="name", operator="eq", value="test")

        assert filter_obj.field == "name"
        assert filter_obj.operator == "eq"
        assert filter_obj.value == "test"

    def test_filter_validation(self):
        """Test filter validation"""
        # Valid operators
        valid_operators = ["eq", "neq", "gt", "gte", "lt", "lte", "like", "in"]

        for op in valid_operators:
            filter_obj = Filter(field="name", operator=op, value="test")
            assert filter_obj.operator == op

        # Invalid operator
        with pytest.raises(ValueError):
            Filter(field="name", operator="invalid", value="test")


class TestCampaignRepository:
    """Test CampaignRepository"""

    @pytest.fixture
    def repository(self, mock_supabase_client):
        return CampaignRepository()

    @pytest.fixture
    def mock_supabase_client(self):
        client = AsyncMock()
        client.table = MagicMock()
        client.table.return_value.select.return_value.execute.return_value = AsyncMock(
            return_value={"data": []}
        )
        client.table.return_value.insert.return_value.execute.return_value = AsyncMock(
            return_value={"data": [{"id": "test-id"}]}
        )
        client.table.return_value.update.return_value.execute.return_value = AsyncMock(
            return_value={"data": [{"id": "test-id"}]}
        )
        client.table.return_value.delete.return_value.execute.return_value = AsyncMock(
            return_value={"data": [{"id": "test-id"}]}
        )
        return client

    @pytest.mark.asyncio
    async def test_get_with_moves(
        self, repository, mock_supabase_client, sample_campaign, sample_move
    ):
        """Test getting campaign with moves"""
        # Setup mock
        mock_supabase_client.table.return_value.select.return_value.execute.return_value = AsyncMock(
            return_value={"data": [sample_campaign]}
        )

        # Mock moves query
        mock_supabase_client.table.return_value.select.return_value.execute.return_value = AsyncMock(
            return_value={"data": [sample_move]}
        )

        # Execute
        result = await repository.get_with_moves("test-campaign-id")

        # Assert
        assert result["id"] == "test-campaign-id"
        assert "moves" in result
        assert len(result["moves"]) == 1

    @pytest.mark.asyncio
    async def test_update_status(
        self, repository, mock_supabase_client, sample_campaign
    ):
        """Test updating campaign status"""
        # Setup mock
        mock_supabase_client.table.return_value.update.return_value.execute.return_value = AsyncMock(
            return_value={"data": [sample_campaign]}
        )

        # Execute
        result = await repository.update_status("test-campaign-id", "active")

        # Assert
        assert result["id"] == "test-campaign-id"
        assert result["status"] == "active"

    @pytest.mark.asyncio
    async def test_add_move(self, repository, mock_supabase_client):
        """Test adding move to campaign"""
        # Setup mock
        mock_supabase_client.table.return_value.update.return_value.execute.return_value = AsyncMock(
            return_value={"data": [{"id": "test-move-id"}]}
        )

        # Execute
        result = await repository.add_move("test-campaign-id", "test-move-id")

        # Assert
        assert result is True
        mock_supabase_client.table.assert_called_with("moves")

    @pytest.mark.asyncio
    async def test_calculate_roi(
        self, repository, mock_supabase_client, sample_campaign
    ):
        """Test calculating campaign ROI"""
        # Setup mock
        mock_supabase_client.table.return_value.select.return_value.execute.return_value = AsyncMock(
            return_value={"data": [sample_campaign]}
        )

        # Execute
        result = await repository.calculate_roi("test-campaign-id")

        # Assert
        assert "campaign_id" in result
        assert "total_cost" in result
        assert "roi_percentage" in result


# Integration tests
class TestRepositoryIntegration:
    """Integration tests for repositories"""

    @pytest.mark.asyncio
    async def test_foundation_icp_relationship(
        self, mock_supabase_client, sample_foundation, sample_icp
    ):
        """Test foundation-ICP relationship"""
        foundation_repo = FoundationRepository()
        icp_repo = ICPRepository()

        # Setup mocks
        mock_supabase_client.table.return_value.select.return_value.execute.return_value = AsyncMock(
            return_value={"data": [sample_foundation]}
        )

        # Get foundation
        foundation = await foundation_repo.get_by_workspace("test-workspace-id")

        # Get ICPs for same workspace
        mock_supabase_client.table.return_value.select.return_value.execute.return_value = AsyncMock(
            return_value={"data": [sample_icp]}
        )

        icps = await icp_repo.list_by_workspace("test-workspace-id")

        # Assert relationship
        assert foundation["workspace_id"] == icps[0]["workspace_id"]
        assert len(icps) == 1

    @pytest.mark.asyncio
    async def test_campaign_move_relationship(
        self, mock_supabase_client, sample_campaign, sample_move
    ):
        """Test campaign-move relationship"""
        campaign_repo = CampaignRepository()
        move_repo = MoveRepository()

        # Setup mocks
        mock_supabase_client.table.return_value.select.return_value.execute.return_value = AsyncMock(
            return_value={"data": [sample_campaign]}
        )

        # Get campaign
        campaign = await campaign_repo.get("test-campaign-id")

        # Get moves for campaign
        mock_supabase_client.table.return_value.select.return_value.execute.return_value = AsyncMock(
            return_value={"data": [sample_move]}
        )

        moves = await move_repo.list_by_campaign("test-campaign-id")

        # Assert relationship
        assert len(moves) == 1
        assert moves[0]["campaign_id"] == "test-campaign-id"
