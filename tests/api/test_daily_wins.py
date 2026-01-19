"""
Tests for Daily Wins API endpoints.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.agents.graphs.daily_wins import DailyWinsGraph, DailyWinState
from backend.api.v1.daily_wins import router as daily_wins_router
from backend.core.auth import get_current_user
from backend.core.database import get_db


@pytest.fixture
def mock_user():
    return {
        "id": "test-user-id",
        "email": "test@example.com",
        "workspace_id": "test-workspace-id",
    }


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def app(mock_user, mock_db):
    app = FastAPI()
    app.include_router(daily_wins_router)
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: mock_db
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


class TestDailyWinsLangGraph:
    """Test LangGraph-powered daily wins generation endpoint"""

    def test_generate_daily_wins_langgraph_success(self, client):
        """Test POST /daily_wins/generate-langgraph - success"""
        request_data = {
            "workspace_id": "test-workspace-id",
            "user_id": "test-user-id",
            "session_id": "test-session-id",
        }

        mock_final_win = {
            "topic": "Contrarian Take on SaaS",
            "hook": "Stop building features.",
            "content": "Focus on the problem instead.",
            "platform": "LinkedIn",
        }

        mock_result = {
            "success": True,
            "final_win": mock_final_win,
            "tokens_used": 1500,
            "cost_usd": 0.02,
            "iteration_count": 1,
        }

        with patch(
            "backend.agents.graphs.daily_wins.DailyWinsGraph.generate_win",
            new_callable=AsyncMock,
        ) as mock_generate:
            mock_generate.return_value = mock_result
            response = client.post("/daily_wins/generate-langgraph", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["win"]["topic"] == "Contrarian Take on SaaS"
        assert data["metadata"]["tokens_used"] == 1500
        assert data["session_id"] == "test-session-id"

    def test_generate_daily_wins_langgraph_failure(self, client):
        """Test POST /daily_wins/generate-langgraph - failure"""
        request_data = {"workspace_id": "test-workspace-id", "user_id": "test-user-id"}

        mock_result = {"success": False, "error": "Simulated graph failure"}

        with patch(
            "backend.agents.graphs.daily_wins.DailyWinsGraph.generate_win",
            new_callable=AsyncMock,
        ) as mock_generate:
            mock_generate.return_value = mock_result
            response = client.post("/daily_wins/generate-langgraph", json=request_data)

        assert response.status_code == 500
        assert "LangGraph generation failed" in response.json()["detail"]


class TestDailyWinsGraphUnit:
    """Unit tests for DailyWinsGraph and state"""

    def test_daily_win_state_initialization(self):
        """Test that DailyWinState can be instantiated with required fields"""
        state = DailyWinState(
            messages=[],
            workspace_id="ws-123",
            user_id="user-123",
            session_id="sess-123",
            current_agent="test",
            routing_path=[],
            memory_context={},
            foundation_summary=None,
            brand_voice=None,
            active_icps=[],
            pending_approval=False,
            approval_gate_id=None,
            output=None,
            error=None,
            tokens_used=0,
            cost_usd=0.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            internal_wins=[],
            recent_moves=[],
            active_campaigns=[],
            external_trends=[],
            synthesized_narrative=None,
            target_platform="LinkedIn",
            content_draft=None,
            hooks=[],
            visual_prompt=None,
            surprise_score=0.0,
            reflection_feedback=None,
            iteration_count=0,
            max_iterations=3,
            final_win=None,
        )
        assert state["workspace_id"] == "ws-123"
        assert state["target_platform"] == "LinkedIn"

    @pytest.mark.asyncio
    async def test_generate_win_placeholder(self):
        """Test generate_win runs through placeholders and returns success"""
        graph = DailyWinsGraph()
        # Mock the compiled graph to just return the state
        mock_compiled_graph = MagicMock()
        mock_compiled_graph.ainvoke = AsyncMock(
            return_value={
                "final_win": {"title": "Test Win"},
                "tokens_used": 100,
                "cost_usd": 0.01,
                "iteration_count": 1,
            }
        )

        with patch.object(
            DailyWinsGraph, "create_graph", return_value=mock_compiled_graph
        ):
            graph.graph = mock_compiled_graph
            result = await graph.generate_win("ws-1", "user-1", "sess-1")

        assert result["success"] is True
        assert result["final_win"]["title"] == "Test Win"
