from models.swarm import SwarmState


def test_swarm_state_schema():
    """Verify that SwarmState correctly extends CognitiveIntelligenceState and handles sub-tasks."""

    # This should fail initially because SwarmState is not yet defined in backend.models.swarm
    state: SwarmState = {
        "tenant_id": "tenant_123",
        "raw_prompt": "Generate a 90-day campaign for a new SaaS tool.",
        "brief": {},
        "research_bundle": {},
        "current_plan": [],
        "generated_assets": [],
        "messages": [],
        "last_agent": "supervisor",
        "reflection_log": [],
        "status": "planning",
        "quality_score": 0.0,
        "cost_accumulator": 0.0,
        "token_usage": {},
        "error": None,
        "next_node": None,
        # Swarm-specific fields
        "swarm_tasks": [
            {
                "id": "task_1",
                "specialist_type": "researcher",
                "description": "Research competitor pricing",
                "status": "pending",
            }
        ],
        "shared_knowledge": {"competitors": []},
        "delegation_history": [],
        "hierarchy": {"lead": "supervisor", "roles": ["researcher"]},
        "budgets": {"token_budget": 10000.0},
        "shared_memory_handles": {"swarm_cache": "swarm:thread_1"},
        "learning_artifacts": [{"type": "summary", "content": "Initial learnings"}],
    }

    assert state["swarm_tasks"][0]["id"] == "task_1"
    assert "competitors" in state["shared_knowledge"]
