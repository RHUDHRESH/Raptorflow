import os

# Set dummy environment variables for Pydantic validation
os.environ["SECRET_KEY"] = "test-secret-key-at-least-32-chars-long-!!!123"
os.environ["DATABASE_URL"] = "sqlite:///test.db"
os.environ["GCP_PROJECT_ID"] = "test-project"
os.environ["WEBHOOK_SECRET"] = "test-webhook-secret"
os.environ["UPSTASH_REDIS_URL"] = "https://test.upstash.io"
os.environ["UPSTASH_REDIS_TOKEN"] = "test-token"
os.environ["VERTEX_AI_PROJECT_ID"] = "test-project"

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json
from datetime import datetime

from backend.agents.graphs.daily_wins import DailyWinState, skeptic_node

@pytest.mark.asyncio
async def test_skeptic_node_approval():
    """Test skeptic node when draft is approved."""
    state = DailyWinState(
        content_draft="A revolutionary contrarian take on marketing.",
        hooks=["Hook 1", "Hook 2"],
        visual_prompt="A futuristic office shot.",
        iteration_count=0,
        max_iterations=3,
        surprise_score=0.0,
        final_win=None
    )

    mock_llm_response = json.dumps({"score": 0.9, "feedback": "Excellent work."})
    
    with patch("backend.agents.specialists.daily_wins.DailyWinsGenerator._call_llm", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = mock_llm_response
        
        result = await skeptic_node(state)
        
        assert result["surprise_score"] == 0.9
        assert result["final_win"] is not None
        assert result["final_win"]["content"] == "A revolutionary contrarian take on marketing."
        assert result["final_win"]["score"] == 0.9

@pytest.mark.asyncio
async def test_skeptic_node_rejection():
    """Test skeptic node when draft is rejected."""
    state = DailyWinState(
        content_draft="A generic AI post.",
        hooks=["Generic Hook"],
        visual_prompt="Generic image.",
        iteration_count=0,
        max_iterations=3,
        surprise_score=0.0,
        final_win=None
    )

    mock_llm_response = json.dumps({"score": 0.4, "feedback": "Too generic. Needs more surprise."})
    
    with patch("backend.agents.specialists.daily_wins.DailyWinsGenerator._call_llm", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = mock_llm_response
        
        result = await skeptic_node(state)
        
        assert result["surprise_score"] == 0.4
        assert result["final_win"] is None
        assert result["reflection_feedback"] == "Too generic. Needs more surprise."
