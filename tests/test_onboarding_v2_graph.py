import os
import pytest

# Mock required settings before importing backend modules
os.environ["SECRET_KEY"] = "test_secret"
os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost:5432/db"
os.environ["GCP_PROJECT_ID"] = "test-project"
os.environ["WEBHOOK_SECRET"] = "test_webhook"

from backend.agents.graphs.onboarding_v2 import OnboardingGraphV2, OnboardingStateV2

@pytest.mark.asyncio
async def test_onboarding_graph_v2_initialization():
    """Test that the updated onboarding graph can be initialized with the correct state."""
    graph_manager = OnboardingGraphV2()
    graph = graph_manager.create_graph()
    
    assert graph is not None
    
    initial_state = {
        "business_context": {},
        "bcm_state": {},
        "current_step": "evidence_vault",
        "completed_steps": [],
        "evidence": [],
        "step_data": {},
        "onboarding_progress": 0.0,
        "needs_user_input": False,
        "user_input_request": None,
        "messages": [],
        "ucid": "RF-2026-TEST"
    }
    
    # We can't easily run the graph without a mock orchestrator, 
    # but we can check if it exists and has the expected nodes.
    assert "handle_evidence_vault" in graph.nodes
    assert "handle_auto_extraction" in graph.nodes
