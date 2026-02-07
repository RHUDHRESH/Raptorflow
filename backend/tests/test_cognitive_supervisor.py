from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import pytest

from agents.cognitive_supervisor import CognitiveSupervisor, SupervisorDecision
from models.cognitive import AgentMessage, CognitiveStatus


@pytest.mark.asyncio
async def test_supervisor_delegation_logic():
    """
    Phase 26: Verify that the supervisor delegates correctly based on state.
    """
    expected_decision = SupervisorDecision(
        next_action="researching",
        rationale="Plan exists, need data.",
        crew_instructions="Extract competitor pricing.",
    )

    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = expected_decision

    # We patch the property on the CLASS before instantiation or use
    with patch(
        "backend.agents.cognitive_supervisor.CognitiveSupervisor.chain",
        new_callable=PropertyMock,
    ) as mock_chain_prop:
        mock_chain_prop.return_value = mock_chain

        with patch("backend.agents.cognitive_supervisor.InferenceProvider"):
            supervisor = CognitiveSupervisor()

            state = {
                "tenant_id": "test-tenant",
                "status": CognitiveStatus.PLANNING,
                "quality_score": 0.8,
                "messages": [AgentMessage(role="system", content="Plan generated.")],
            }

            result = await supervisor(state)

            assert result["status"] == CognitiveStatus.RESEARCHING
            assert result["next_node"] == "researching"
            assert "DELEGATE: researching" in result["messages"][0].content
