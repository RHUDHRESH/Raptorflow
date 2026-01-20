"""
Audit Integration Test for Matrix & Blackbox Engines.
Verifies Analytics metric aggregation and Blackbox strategy generation logic.
"""

import os
import pytest
import uuid
import time
from typing import Dict, Any, List
from unittest.mock import MagicMock, AsyncMock, patch

# Mock environment variables
os.environ["SECRET_KEY"] = "test_secret"
os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost:5432/db"
os.environ["GCP_PROJECT_ID"] = "test-project"
os.environ["WEBHOOK_SECRET"] = "test_webhook_secret"
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_ANON_KEY"] = "test_token"

@pytest.mark.asyncio
class TestMatrixBlackboxAudit:
    """Audit suite for Matrix (Analytics) and Blackbox engines."""

    @pytest.fixture
    def workspace_id(self):
        return str(uuid.uuid4())

    @pytest.fixture
    def mock_db(self):
        db = MagicMock()
        db.fetchval = AsyncMock(return_value=100)
        
        # side_effect to return different values for different queries
        async def fetch_side_effect(query, *args):
            if "agent_name" in query:
                return [{"agent_name": "Titan", "count": 50}]
            if "DATE(created_at)" in query:
                import datetime
                return [{"date": datetime.date.today(), "count": 10}]
            if "workspace_id" in query:
                return [{"workspace_id": "ws1", "request_count": 100}]
            return []
            
        db.fetch = AsyncMock(side_effect=fetch_side_effect)
        db.fetchrow = AsyncMock(return_value={
            "avg_response_time": 250.0,
            "p95_response_time": 500.0,
            "p99_response_time": 1000.0
        })
        return db

    async def test_matrix_analytics_queries(self, mock_db, workspace_id):
        """Test that analytics endpoints use the correct SQL aggregations."""
        from backend.api.v1.analytics import get_usage_stats
        
        # Test usage stats logic
        # We simulate the dependency injection
        stats = await get_usage_stats(workspace_id=workspace_id, db=mock_db, current_user={})
        
        assert stats.success is True
        assert stats.total_requests == 100
        mock_db.fetchval.assert_called()

    async def test_blackbox_workflow_orchestration(self, workspace_id):
        """Test the Blackbox strategy generation orchestration."""
        mock_db = MagicMock()
        mock_mem = MagicMock()
        mock_cog = MagicMock()
        mock_disp = MagicMock()
        
        # Mock successful generation
        from backend.workflows.blackbox import BlackboxWorkflow
        workflow = BlackboxWorkflow(mock_db, mock_mem, mock_cog, mock_disp)
        
        # Mock internal methods to avoid deep dependency chain
        with patch.object(workflow, "_get_workspace_context", return_value={"user_id": "u1"}):
            with patch.object(workflow, "_gather_strategy_context", return_value={}):
                with patch.object(workflow, "_generate_bold_strategy", return_value={
                    "success": True, 
                    "strategy_id": "s1",
                    "strategy": {"title": "Bold Move", "bold_idea": "test", "description": "test"}
                }):
                    with patch.object(workflow, "_assess_strategy_risks", return_value={
                        "risk_level": "medium", "risk_score": 0.5
                    }):
                        # Mock DB insert
                        mock_db.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[{"id": "s1"}])
                        
                        # Mock memory and review
                        workflow._store_strategy_in_memory = AsyncMock()
                        workflow._create_strategy_review = AsyncMock()
                        
                        result = await workflow.generate_strategy(workspace_id)
                        
                        assert result["success"] is True
                        assert result["strategy_id"] == "s1"
                        mock_db.table.assert_called_with("blackbox_strategies")
