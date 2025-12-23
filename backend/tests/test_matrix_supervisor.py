import pytest
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock
from backend.agents.supervisor import HierarchicalSupervisor
from langchain_core.messages import HumanMessage

@pytest.mark.asyncio

async def test_matrix_supervisor_delegation():

    """Test that the supervisor correctly delegates to a specialist."""

    

    # Mock LLM since it's passed to __init__

    mock_llm = MagicMock()

    

    supervisor = HierarchicalSupervisor(

        llm=mock_llm,

        team_members=["DriftAnalyzer", "Governor"],

        system_prompt="You are the Matrix Supervisor."

    )

    

    # Define response

    mock_response = MagicMock()

    mock_response.next_node = "DriftAnalyzer"

    mock_response.instructions = "Check GCS for drift"

    

    # Mock the chain property directly

    mock_chain = AsyncMock()

    mock_chain.ainvoke.return_value = mock_response

    

    with patch.object(HierarchicalSupervisor, "chain", new_callable=PropertyMock) as mock_chain_prop:

        mock_chain_prop.return_value = mock_chain

        

        state = {"messages": [HumanMessage(content="Is there data drift?")]}

        result = await supervisor(state)

        

        assert result["next"] == "DriftAnalyzer"

        assert result["instructions"] == "Check GCS for drift"








