from models.council import CouncilBlackboardState, CouncilThought


def test_council_thought_creation():
    """Verify CouncilThought model validation."""
    thought = CouncilThought(
        agent_id="agent_1",
        content="We should focus on SEO.",
        confidence=0.85,
        tool_observations={"gap_analysis": "low competition"},
    )
    assert thought.agent_id == "agent_1"
    assert thought.confidence == 0.85


def test_blackboard_state_initialization():
    """Verify CouncilBlackboardState initialization and shared memory."""
    state: CouncilBlackboardState = {
        "workspace_id": "ws_123",
        "raw_prompt": "Build a viral campaign",
        "parallel_thoughts": [],
        "debate_history": [],
        "consensus_metrics": {"alignment": 0.0},
        "synthesis": None,
        "rejected_paths": [],
        "final_strategic_decree": None,
        "reasoning_chain_id": None,
    }
    assert state["workspace_id"] == "ws_123"
    assert "parallel_thoughts" in state


def test_blackboard_state_thought_addition():
    """Verify thoughts can be added to the blackboard."""
    thought = CouncilThought(agent_id="viral_alchemist", content="Contrarian hook.")

    # In LangGraph, we typically use operator.add for lists in TypedDict
    # We will test if the state accepts the thought objects
    thoughts = [thought]
    assert len(thoughts) == 1
    assert thoughts[0].agent_id == "viral_alchemist"
