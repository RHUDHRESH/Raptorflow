"""
Integration tests for Business Context LangGraph with real/semi-real AI calls.
"""

import os
import pytest
import asyncio
from typing import Dict, Any
from backend.services.business_context_graph import get_business_context_graph, create_initial_workflow_state
from backend.services.vertex_ai_client import get_vertex_ai_client

# Skip tests in this module if Vertex AI is not configured
pytestmark = pytest.mark.skipif(
    not os.getenv("VERTEX_AI_PROJECT_ID"),
    reason="Vertex AI not configured. Set VERTEX_AI_PROJECT_ID to run integration tests."
)

@pytest.mark.asyncio
async def test_full_graph_integration():
    """Test the full Business Context Graph workflow."""
    # 1. Initialize Graph and Client
    graph = get_business_context_graph()
    client = get_vertex_ai_client()
    
    # Check health first
    health = await client.health_check()
    if health["status"] != "healthy":
        pytest.skip(f"Vertex AI health check failed: {health['message']}")
    
    # 2. Prepare mock foundation data
    foundation_data = {
        "company_name": "RaptorFlow",
        "industry": "Marketing Technology",
        "description": "A comprehensive marketing operating system for founders and lean teams. It converts messy business context into clear positioning, 90-day war plans, and tracked execution moves.",
        "stage": "Seed",
        "target_market": "SaaS and D2C startups",
        "workspace_id": "test-ws-integration",
        "user_id": "test-user-integration"
    }
    
    # 3. Create initial state
    state = create_initial_workflow_state(
        workspace_id=foundation_data["workspace_id"],
        user_id=foundation_data["user_id"],
        foundation_data=foundation_data
    )
    
    # 4. Run the workflow
    print("\n🚀 Starting Full Business Context Graph Integration Test...")
    print("This may take 1-2 minutes as it calls real Vertex AI endpoints.")
    
    try:
        # We'll run the full graph
        result = await graph.workflow.ainvoke(state)
        
        # 5. Verify results
        context = result["context_data"]
        
        assert context is not None
        assert context.company_profile.name == "RaptorFlow"
        assert context.market_analysis.overview != ""
        assert context.competitive_landscape.overview != ""
        assert context.swot_analysis.strengths != []
        assert context.pestel_analysis.political != []
        assert context.value_chain.primary_activities != []
        assert context.brand_archetypes.primary != ""
        
        print("✅ Full graph integration successful!")
        print(f"📊 Company Profile: {context.company_profile.mission[:100]}...")
        print(f"📊 Primary Archetype: {context.brand_archetypes.primary}")
        
    except Exception as e:
        pytest.fail(f"Graph execution failed: {e}")

@pytest.mark.asyncio
async def test_icp_enhancement_integration():
    """Test the ICP enhancement node integration."""
    graph = get_business_context_graph()
    
    foundation_data = {"company_name": "RaptorFlow", "industry": "MarTech"}
    icp_data = {
        "id": "founder-segment",
        "name": "Solo Founders",
        "description": "Early stage tech founders who are overwhelmed by marketing options and need a system."
    }
    
    state = create_initial_workflow_state(
        workspace_id="test-ws",
        user_id="test-user",
        foundation_data=foundation_data,
        icp_list=[icp_data]
    )
    
    print("\n🚀 Testing ICP Enhancement Node...")
    
    try:
        # Run just the ICP enhancement node
        result = await graph.enhance_icp_node(state)
        
        enhancements = result["context_data"].icp_enhancements
        assert "founder-segment" in enhancements
        
        founder_enhanced = enhancements["founder-segment"]
        assert founder_enhanced.archetype_name != ""
        assert founder_enhanced.psychographics.motivations != []
        
        print(f"✅ ICP Enhancement successful for: {founder_enhanced.archetype_name}")
        
    except Exception as e:
        pytest.fail(f"ICP enhancement failed: {e}")

if __name__ == "__main__":
    # Allow running directly for quick testing
    asyncio.run(test_full_graph_integration())
    asyncio.run(test_icp_enhancement_integration())
