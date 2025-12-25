from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import pytest
from langchain_core.messages import HumanMessage

from backend.graphs.swarm_orchestrator import (
    SwarmController,
    SwarmIntent,
    SwarmRouteDecision,
)


@pytest.mark.asyncio
async def test_matrix_supervisor_delegation():
    """Test that the supervisor correctly delegates to a specialist."""
    # Mock LLM since it's passed to __init__
    mock_llm = MagicMock()
    supervisor = SwarmController(
        supervisor_llm=mock_llm,
        team_members=["DriftAnalyzer", "Governor"],
        system_prompt="You are the Matrix Supervisor.",
    )
    # Define response
    mock_response = SwarmRouteDecision(
        next_node="DriftAnalyzer", instructions="Check GCS for drift"
    )
    # Mock the chain property directly
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = mock_response

    with patch.object(
        SwarmController, "supervisor_chain", new_callable=PropertyMock
    ) as mock_chain_prop:
        mock_chain_prop.return_value = mock_chain
        state = {"messages": [HumanMessage(content="Is there data drift?")]}
        result = await supervisor(state)
        assert result["next"] == "DriftAnalyzer"
        assert result["instructions"] == "Check GCS for drift"


@pytest.mark.asyncio
async def test_matrix_supervisor_route_intent_drift():
    """Test that the supervisor routes to DriftAnalyzer for drift-related queries."""
    mock_llm = MagicMock()
    mock_intent = SwarmIntent(
        asset_type="strategy",
        confidence=0.9,
        extracted_goal="Drift check",
        entities=[],
    )
    mock_llm.with_structured_output.return_value = AsyncMock(
        ainvoke=AsyncMock(return_value=mock_intent)
    )

    supervisor = SwarmController(intent_llm=mock_llm)
    intent = await supervisor.route_intent("Is there any data drift?")
    assert intent.asset_type == "strategy"


@pytest.mark.asyncio
async def test_matrix_supervisor_route_intent_unknown():
    """Test that the supervisor routes to FINISH for unknown intents."""
    mock_llm = MagicMock()
    mock_intent = SwarmIntent(
        asset_type="strategy",
        confidence=0.4,
        extracted_goal="Unknown",
        entities=[],
    )
    mock_llm.with_structured_output.return_value = AsyncMock(
        ainvoke=AsyncMock(return_value=mock_intent)
    )

    supervisor = SwarmController(intent_llm=mock_llm)
    intent = await supervisor.route_intent("Tell me a joke")
    assert intent.asset_type == "strategy"


@pytest.mark.asyncio
async def test_matrix_supervisor_execute_loop_success():
    """Test that the supervisor can execute a full multi-turn loop."""
    mock_llm = MagicMock()
    supervisor = SwarmController(
        supervisor_llm=mock_llm, team_members=["DriftAnalyzer"], system_prompt="..."
    )

    # Mock chain returns DriftAnalyzer then FINISH
    mock_resp1 = MagicMock(next_node="DriftAnalyzer", instructions="Run check")
    mock_resp2 = MagicMock(next_node="FINISH", instructions="All clear")

    mock_chain = AsyncMock()
    mock_chain.ainvoke.side_effect = [mock_resp1, mock_resp2]

    # Mock DriftAnalyzer node
    mock_drift = AsyncMock(return_value={"analysis_summary": "No drift"})
    nodes = {"DriftAnalyzer": mock_drift}

    with patch.object(
        SwarmController, "supervisor_chain", new_callable=PropertyMock
    ) as mock_chain_prop:
        mock_chain_prop.return_value = mock_chain

        initial_state = {"messages": [HumanMessage(content="Analyze system")]}
        final_result = await supervisor.execute_loop(initial_state, nodes)

        assert final_result["next"] == "FINISH"
        assert len(final_result["messages"]) > 1
        assert mock_drift.called
