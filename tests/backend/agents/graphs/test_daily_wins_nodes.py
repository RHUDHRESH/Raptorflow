"""
Tests for Daily Wins LangGraph Nodes.
"""

from unittest.mock import AsyncMock, patch, MagicMock
import pytest
from datetime import datetime

from backend.agents.graphs.daily_wins import (
    DailyWinState, 
    context_miner_node, 
    trend_mapper_node,
    synthesizer_node,
    voice_architect_node,
    hook_specialist_node,
    visualist_node,
    skeptic_node
)

@pytest.fixture
def initial_state():
    return DailyWinState(
        messages=[],
        workspace_id="test-workspace",
        user_id="test-user",
        session_id="test-session",
        current_agent="DailyWinsGraph",
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
        bcm_manifest=None,
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
        final_win=None
    )

class TestDailyWinsNodes:
    """Test individual nodes in the Daily Wins graph"""

    @pytest.mark.asyncio
    async def test_context_miner_node(self, initial_state):
        """Test that context_miner fetches internal BCM context manifest"""
        mock_manifest = {
            "content": {
                "current_moves": [{"id": "move-1", "title": "Move 1"}],
                "active_campaigns": [{"id": "camp-1", "name": "Campaign 1"}],
                "foundation": {"industry": "SaaS"}
            }
        }

        with patch("backend.integration.context_builder.build_business_context_manifest", new_callable=AsyncMock) as mock_bcm:
            mock_bcm.return_value = mock_manifest
            
            with patch("backend.core.supabase_mgr.get_supabase_client") as mock_supabase:
                # Node will also fetch past wins
                mock_supabase.return_value.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = []
                
                updated_state = await context_miner_node(initial_state)
                
                assert updated_state["bcm_manifest"] is not None
                assert len(updated_state["recent_moves"]) == 1
                assert len(updated_state["active_campaigns"]) == 1

    @pytest.mark.asyncio
    async def test_trend_mapper_node(self, initial_state):
        """Test that trend_mapper fetches external trends via Titan"""
        from backend.agents.tools.base import ToolResult
        mock_trends = [{"title": "SaaS Trend 2026", "source": "Titan"}]
        
        # Mock Titan tool
        with patch("backend.services.titan.tool.TitanIntelligenceTool._arun", new_callable=AsyncMock) as mock_titan:
            mock_titan.return_value = ToolResult(success=True, data=mock_trends)
            updated_state = await trend_mapper_node(initial_state)
            assert len(updated_state["external_trends"]) == 1
            assert updated_state["external_trends"][0]["title"] == "SaaS Trend 2026"

    @pytest.mark.asyncio
    async def test_synthesizer_node(self, initial_state):
        """Test that synthesizer merges internal and external data"""
        initial_state["recent_moves"] = [{"title": "Launch AI Beta"}]
        initial_state["external_trends"] = [{"title": "AI fatigue in SaaS"}]
        
        # Mock LLM generation
        with patch("backend.agents.base.BaseAgent._call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "A contrarian take on AI Beta vs SaaS fatigue."
            updated_state = await synthesizer_node(initial_state)
            assert updated_state["synthesized_narrative"] is not None
            assert "contrarian" in updated_state["synthesized_narrative"].lower()

    @pytest.mark.asyncio
    async def test_voice_architect_node(self, initial_state):
        """Test that voice_architect enforces tone"""
        initial_state["synthesized_narrative"] = "Raw content about AI"
        
        with patch("backend.agents.base.BaseAgent._call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "Surgical, expensive, and decisive insight."
            updated_state = await voice_architect_node(initial_state)
            assert updated_state["content_draft"] is not None
            assert updated_state["target_platform"] == "LinkedIn" # Default

    @pytest.mark.asyncio
    async def test_hook_specialist_node(self, initial_state):
        """Test that hook_specialist generates headlines"""
        initial_state["content_draft"] = "Full post about SaaS"
        
        with patch("backend.agents.base.BaseAgent._call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = '["Hook 1", "Hook 2"]'
            updated_state = await hook_specialist_node(initial_state)
            assert len(updated_state["hooks"]) >= 1

    @pytest.mark.asyncio
    async def test_visualist_node(self, initial_state):
        """Test that visualist generates image prompts"""
        initial_state["content_draft"] = "Full post content"
        
        with patch("backend.agents.base.BaseAgent._call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "A cinematic shot of a workspace"
            updated_state = await visualist_node(initial_state)
            assert updated_state["visual_prompt"] is not None

    @pytest.mark.asyncio
    async def test_skeptic_node(self, initial_state):
        """Test that skeptic evaluates surprise score"""
        initial_state["content_draft"] = "Full post content"
        
        # Mock LLM returning score and feedback
        with patch("backend.agents.base.BaseAgent._call_llm", new_callable=AsyncMock) as mock_llm:
            # First call: generic content -> low score
            mock_llm.return_value = '{"score": 0.4, "feedback": "Too generic."}'
            updated_state = await skeptic_node(initial_state)
            assert updated_state["surprise_score"] == 0.4
            assert updated_state["reflection_feedback"] == "Too generic."
            
            # Second call: high score -> final_win populated
            mock_llm.return_value = '{"score": 0.9, "feedback": "Exceptional."}'
            updated_state = await skeptic_node(initial_state)
            assert updated_state["surprise_score"] == 0.9
            assert updated_state["final_win"] is not None
