"""
Test suite for Cost Tracking functionality

Tests the core cost tracking service, models, and API endpoints.
Ensures accurate cost logging and retrieval across workspaces.
"""

import pytest
from uuid import UUID, uuid4
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from backend.models.cost import CostLog
from backend.services.cost_tracker import CostTrackerService


class TestCostLog:
    """Test CostLog model functionality"""

    def test_create_log_calculates_cost(self):
        """Test that CostLog factory method calculates cost correctly"""
        workspace_id = uuid4()
        correlation_id = uuid4()

        log = CostLog.create_log(
            workspace_id=workspace_id,
            correlation_id=correlation_id,
            agent_name="test_agent",
            action_name="test_action",
            input_tokens=1000,
            output_tokens=500,
        )

        # Check cost calculation: (1000 * 0.0000001) + (500 * 0.0000003) = 0.0001 + 0.00015 = 0.00025
        expected_cost = Decimal("0.00025")
        assert log.estimated_cost_usd == expected_cost
        assert log.agent_name == "test_agent"
        assert log.action_name == "test_action"
        assert log.input_tokens == 1000
        assert log.output_tokens == 500

    def test_calculate_cost_method(self):
        """Test the cost calculation method directly"""
        log = CostLog(
            workspace_id=uuid4(),
            correlation_id=uuid4(),
            agent_name="test",
            action_name="test",
            input_tokens=2000,
            output_tokens=1000,
        )

        cost = log.calculate_cost()
        # (2000 * 0.0000001) + (1000 * 0.0000003) = 0.0002 + 0.0003 = 0.0005
        assert cost == Decimal("0.0005")


@pytest.mark.asyncio
class TestCostTrackerService:
    """Test CostTrackerService functionality"""

    @pytest.fixture
    def mock_db(self):
        """Mock Supabase client"""
        mock_client = AsyncMock()
        return mock_client

    @pytest.fixture
    def service(self, mock_db):
        """Create service with mocked database"""
        service = CostTrackerService()
        service.db = mock_db
        return service

    async def test_log_cost_success(self, service, mock_db):
        """Test successful cost logging"""
        workspace_id = uuid4()
        correlation_id = uuid4()

        # Mock the insert operation
        mock_db.insert.return_value = {}

        result = await service.log_cost(
            workspace_id=workspace_id,
            correlation_id=correlation_id,
            agent_name="test_agent",
            action_name="content_generation",
            input_tokens=1500,
            output_tokens=750,
        )

        # Verify the result
        assert isinstance(result, CostLog)
        assert result.workspace_id == workspace_id
        assert result.correlation_id == correlation_id
        assert result.agent_name == "test_agent"
        assert result.action_name == "content_generation"
        assert result.input_tokens == 1500
        assert result.output_tokens == 750
        # (1500 * 0.0000001) + (750 * 0.0000003) = 0.00015 + 0.000225 = 0.000375
        assert result.estimated_cost_usd == Decimal("0.000375")

        # Verify database was called
        mock_db.insert.assert_called_once()
        call_args = mock_db.insert.call_args[0]
        assert call_args[0] == "cost_logs"
        data = call_args[1]
        assert data["workspace_id"] == str(workspace_id)
        assert data["correlation_id"] == str(correlation_id)
        assert data["agent_name"] == "test_agent"
        assert data["action_name"] == "content_generation"
        assert data["input_tokens"] == 1500
        assert data["output_tokens"] == 750
        assert data["estimated_cost_usd"] == "0.000375"

    async def test_log_cost_database_error(self, service, mock_db):
        """Test cost logging with database error"""
        mock_db.insert.side_effect = Exception("Database connection failed")

        with pytest.raises(Exception, match="Database connection failed"):
            await service.log_cost(
                workspace_id=uuid4(),
                correlation_id=uuid4(),
                agent_name="test_agent",
                action_name="test_action",
                input_tokens=1000,
                output_tokens=500,
            )

    async def test_get_costs_for_workspace(self, service, mock_db):
        """Test retrieving costs for a workspace"""
        workspace_id = uuid4()

        # Mock database response
        mock_costs_data = [
            {
                "id": str(uuid4()),
                "workspace_id": str(workspace_id),
                "correlation_id": str(uuid4()),
                "agent_name": "agent1",
                "action_name": "task1",
                "input_tokens": 1000,
                "output_tokens": 500,
                "estimated_cost_usd": "0.00025",
                "created_at": "2025-01-27T12:00:00Z",
            },
            {
                "id": str(uuid4()),
                "workspace_id": str(workspace_id),
                "correlation_id": str(uuid4()),
                "agent_name": "agent2",
                "action_name": "task2",
                "input_tokens": 2000,
                "output_tokens": 1000,
                "estimated_cost_usd": "0.0005",
                "created_at": "2025-01-27T12:01:00Z",
            }
        ]

        mock_db.client.table.return_value.select.return_value.order.return_value.limit.return_value.range.return_value.execute.return_value = MagicMock(data=mock_costs_data)

        results = await service.get_costs_for_workspace(workspace_id)

        assert len(results) == 2
        assert all(isinstance(cost, CostLog) for cost in results)
        assert results[0].agent_name == "agent1"
        assert results[1].agent_name == "agent2"
        assert results[0].estimated_cost_usd == Decimal("0.00025")
        assert results[1].estimated_cost_usd == Decimal("0.0005")

    async def test_get_costs_for_workspace_pagination(self, service, mock_db):
        """Test cost retrieval with pagination"""
        workspace_id = uuid4()

        mock_db.client.table.return_value.select.return_value.order.return_value.limit.return_value.range.return_value.execute.return_value = MagicMock(data=[])

        await service.get_costs_for_workspace(workspace_id, limit=50, offset=100)

        # Verify pagination parameters were used
        query_mock = mock_db.client.table.return_value.select.return_value.order.return_value.limit.return_value.range
        query_mock.assert_called_once()

    async def test_get_total_cost_for_workspace(self, service, mock_db):
        """Test calculating total cost for a workspace"""
        workspace_id = uuid4()

        # Create mock cost logs
        mock_logs = [
            CostLog(
                id=uuid4(),
                workspace_id=workspace_id,
                correlation_id=uuid4(),
                agent_name="agent1",
                action_name="task1",
                input_tokens=1000,
                output_tokens=500,
                estimated_cost_usd=Decimal("0.00025"),
            ),
            CostLog(
                id=uuid4(),
                workspace_id=workspace_id,
                correlation_id=uuid4(),
                agent_name="agent2",
                action_name="task2",
                input_tokens=2000,
                output_tokens=1000,
                estimated_cost_usd=Decimal("0.0005"),
            )
        ]

        # Mock get_costs_for_workspace
        service.get_costs_for_workspace = AsyncMock(return_value=mock_logs)

        total_cost = await service.get_total_cost_for_workspace(workspace_id)

        expected_total = Decimal("0.00025") + Decimal("0.0005")  # 0.00075
        assert total_cost == expected_total

    async def test_get_total_cost_for_workspace_empty(self, service, mock_db):
        """Test total cost calculation for workspace with no costs"""
        workspace_id = uuid4()

        service.get_costs_for_workspace = AsyncMock(return_value=[])

        total_cost = await service.get_total_cost_for_workspace(workspace_id)

        assert total_cost == Decimal("0")


class TestCostTrackerIntegration:
    """Integration tests for cost tracking end-to-end"""

    @pytest.mark.asyncio
    async def test_cost_lifecycle(self, service, mock_db):
        """Test complete cost tracking lifecycle"""
        workspace_id = uuid4()
        correlation_id = uuid4()

        # Mock database operations
        mock_db.insert.return_value = {}
        mock_logs_data = [{
            "id": str(uuid4()),
            "workspace_id": str(workspace_id),
            "correlation_id": str(correlation_id),
            "agent_name": "integration_agent",
            "action_name": "integration_test",
            "input_tokens": 1000,
            "output_tokens": 500,
            "estimated_cost_usd": "0.00025",
            "created_at": "2025-01-27T12:00:00Z",
        }]
        mock_db.client.table.return_value.select.return_value.order.return_value.limit.return_value.range.return_value.execute.return_value = MagicMock(data=mock_logs_data)

        # 1. Log a cost
        logged_cost = await service.log_cost(
            workspace_id=workspace_id,
            correlation_id=correlation_id,
            agent_name="integration_agent",
            action_name="integration_test",
            input_tokens=1000,
            output_tokens=500,
        )

        # 2. Retrieve costs for workspace
        costs = await service.get_costs_for_workspace(workspace_id)

        # 3. Calculate total cost
        total_cost = await service.get_total_cost_for_workspace(workspace_id)

        # Verify integration
        assert len(costs) == 1
        assert costs[0].agent_name == "integration_agent"
        assert total_cost == logged_cost.estimated_cost_usd
