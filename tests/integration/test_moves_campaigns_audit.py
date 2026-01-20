"""
Audit Integration Test for Moves & Campaigns Services.
Verifies Move generation, Campaign orchestration, and ROI calculation logic.
"""

import os
import pytest
import uuid
from typing import Dict, Any, List
from unittest.mock import MagicMock, AsyncMock, patch

# Mock environment variables
os.environ["SECRET_KEY"] = "test_secret"
os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost:5432/db"
os.environ["GCP_PROJECT_ID"] = "test-project"
os.environ["WEBHOOK_SECRET"] = "test_webhook_secret"
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_ANON_KEY"] = "test_token"

from backend.core.models import ValidationError

@pytest.mark.asyncio
class TestMovesCampaignsAudit:
    """Audit suite for Moves and Campaigns services."""

    @pytest.fixture
    def workspace_id(self):
        return str(uuid.uuid4())

    @pytest.fixture
    def mock_supabase(self):
        client = MagicMock()
        return client

    async def test_move_lifecycle(self, workspace_id, mock_supabase):
        """Test the lifecycle of a marketing move."""
        with patch("backend.core.supabase_mgr.get_supabase_client", return_value=mock_supabase):
            from backend.services.move import MoveService
            move_service = MoveService()
            
            # Mock repository
            move_service.repository.create = AsyncMock(return_value={
                "id": "move-123",
                "name": "Audit Move",
                "status": "draft",
                "category": "ignite"
            })
            move_service.repository.get_by_id = AsyncMock(return_value={
                "id": "move-123",
                "name": "Audit Move",
                "status": "draft"
            })
            move_service.repository.start_move = AsyncMock(return_value={
                "id": "move-123",
                "status": "active"
            })
            
            # 1. Create Move
            move = await move_service.create_move(workspace_id, {"name": "Audit Move", "category": "ignite"})
            assert move["id"] == "move-123"
            
            # 2. Start Move
            started = await move_service.start_move("move-123", workspace_id)
            assert started["status"] == "active"

    async def test_campaign_orchestration(self, workspace_id, mock_supabase):
        """Test campaign creation and ROI logic."""
        with patch("backend.core.supabase_mgr.get_supabase_client", return_value=mock_supabase):
            from backend.services.campaign import CampaignService
            campaign_service = CampaignService()
            
            # Mock repository
            campaign_service.repository.create = AsyncMock(return_value={
                "id": "camp-123",
                "name": "Audit Campaign",
                "budget_usd": 1000
            })
            campaign_service.repository.get_with_moves = AsyncMock(return_value={
                "id": "camp-123",
                "name": "Audit Campaign",
                "budget_usd": 1000,
                "moves": [
                    {"id": "m1", "status": "completed", "results": {"revenue": 5000}}
                ]
            })
            
            # 1. Create Campaign
            camp = await campaign_service.create_campaign(workspace_id, {"name": "Audit Campaign", "budget_usd": 1000})
            assert camp["id"] == "camp-123"
            
            # 2. Calculate ROI
            roi_data = await campaign_service.calculate_roi("camp-123", workspace_id)
            assert roi_data["revenue_usd"] == 5000
            assert roi_data["roi_percentage"] == 400.0
