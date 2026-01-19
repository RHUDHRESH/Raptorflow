"""
Unit and Integration tests for Business Context LangGraph
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from backend.services.business_context_graph import get_business_context_graph, create_initial_workflow_state
from backend.schemas import CompanyProfile, MarketAnalysis, RICP, MessagingStrategy, StoryBrand

@pytest.mark.asyncio
async def test_create_initial_workflow_state():
    """Test that the workflow state is initialized correctly."""
    foundation_data = {"company_name": "Test Co", "industry": "AI"}
    state = create_initial_workflow_state(
        workspace_id="ws-123",
        user_id="user-456",
        foundation_data=foundation_data
    )
    
    assert state["workspace_id"] == "ws-123"
    assert state["foundation_data"] == foundation_data
    assert state["context_data"].company_profile is None

@pytest.mark.asyncio
async def test_safe_generate_success():
    """Test safe_generate with successful AI response."""
    graph = get_business_context_graph()
    foundation_data = {"company_name": "Test Co"}
    state = create_initial_workflow_state("ws", "user", foundation_data)
    
    # Mock Vertex AI client
    with patch.object(graph.vertex_ai_client, 'generate_text', new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = '{"overview": "Positive market outlook", "size": "$1B", "trends": ["AI adoption"], "opportunities": ["New niches"]}'
        
        result = await graph._safe_generate("prompt", MarketAnalysis, "node", state)
        
        assert isinstance(result, MarketAnalysis)
        assert result.size == "$1B"

@pytest.mark.asyncio
async def test_safe_generate_retry_then_success():
    """Test that safe_generate retries on failure and then succeeds."""
    graph = get_business_context_graph()
    state = create_initial_workflow_state("ws", "user", {})
    
    with patch.object(graph.vertex_ai_client, 'generate_text', new_callable=AsyncMock) as mock_gen:
        # First call fails, second succeeds
        mock_gen.side_effect = [None, '{"overview": "Success after retry", "size": "N/A", "trends": [], "opportunities": []}']
        
        result = await graph._safe_generate("prompt", MarketAnalysis, "node", state)
        
        assert result.overview == "Success after retry"
        assert mock_gen.call_count == 2

@pytest.mark.asyncio
async def test_generate_profile_node():
    """Test the generate_profile node logic."""
    graph = get_business_context_graph()
    state = create_initial_workflow_state("ws", "user", {"company_name": "Node Co"})
    
    mock_response = '{"name": "Node Co", "mission": "Mission", "vision": "Vision", "market_position": "Pos"}'
    
    with patch.object(graph, '_safe_generate', new_callable=AsyncMock) as mock_safe:
        mock_safe.return_value = CompanyProfile(**json.loads(mock_response))
        
        result_state = await graph.generate_profile_node(state)
        
        assert result_state["context_data"].company_profile.name == "Node Co"
        assert "generated_at" in result_state["context_data"].metadata

@pytest.mark.asyncio
async def test_enhance_icp_node_ricp():
    """Test the enhance_icp node generating unified RICP."""
    graph = get_business_context_graph()
    state = create_initial_workflow_state("ws", "user", {"company_name": "Test"}, icp_list=[{"id": "c1", "name": "Founders"}])
    
    with patch.object(graph, '_safe_generate', new_callable=AsyncMock) as mock_safe:
        # Mock RICP generation
        mock_safe.return_value = RICP(name="Ambitious Founder", persona_name="Sarah")
        
        result_state = await graph.enhance_icp_node(state)
        
        assert len(result_state["context_data"].ricps) > 0
        assert result_state["context_data"].ricps[0].name == "Ambitious Founder"
        assert result_state["context_data"].ricps[0].persona_name == "Sarah"

@pytest.mark.asyncio
async def test_generate_messaging_node_storybrand():
    """Test generate_messaging node with StoryBrand."""
    graph = get_business_context_graph()
    state = create_initial_workflow_state("ws", "user", {"company_name": "Test"})
    state["context_data"].ricps = [RICP(name="Founder", persona_name="Sarah")]
    
    with patch.object(graph, '_safe_generate', new_callable=AsyncMock) as mock_safe:
        mock_safe.return_value = MessagingStrategy(
            story_brand=StoryBrand(character="Sarah", guide="RaptorFlow"),
            confidence=90
        )
        
        result_state = await graph.generate_messaging_node(state)
        
        assert result_state["context_data"].messaging_strategy.story_brand.character == "Sarah"
        assert result_state["context_data"].messaging_strategy.confidence == 85