import asyncio

import pytest

from agents.swarm_controller import SwarmOrchestrator


@pytest.mark.asyncio
async def test_swarm_mission_initialization():
    """Verifies that the SwarmOrchestrator can initialize and run a basic mission."""
    orchestrator = SwarmOrchestrator()

    workspace_id = "test-workspace-swarm"
    prompt = "I need a marketing email for a luxury watch brand."

    # We'll use a mocked client or just verify the structure
    # Since swarm is installed, we can try a dry run if API key is present
    # or mock the client.run call.

    from unittest.mock import MagicMock

    orchestrator.client.run = MagicMock()

    # Mock response
    mock_response = MagicMock()
    mock_response.messages = [{"role": "assistant", "content": "Brief complete."}]
    mock_response.context_variables = {
        "workspace_id": workspace_id,
        "brief_ready": True,
    }
    mock_response.agent.name = "Brief Builder"

    orchestrator.client.run.return_value = mock_response

    result = await orchestrator.run_mission(prompt, workspace_id)

    assert "messages" in result
    assert result["last_agent"] == "Brief Builder"
    assert result["context_variables"]["brief_ready"] is True
    print(f"\nSwarm Mission Result: {result['messages'][-1].content}")


@pytest.mark.asyncio
async def test_swarm_streaming_utility():
    """Verifies the swarm streaming processor logic."""
    from unittest.mock import MagicMock

    from agents.swarm_streaming import swarm_stream_processor

    client = MagicMock()
    agent = MagicMock()
    agent.name = "Test Agent"

    # Mock stream generator
    def mock_stream():
        yield {"content": "Hello"}
        yield {"content": " World"}
        yield {"sender": "Test Agent", "recipient": "Next Agent"}
        yield {"delim": "end"}

    client.run.return_value = mock_stream()

    events = []
    async for event in swarm_stream_processor(client, agent, [], {}):
        events.append(event)

    assert events[0]["type"] == "content"
    assert events[0]["delta"] == "Hello"
    assert events[2]["type"] == "handoff"
    assert events[3]["type"] == "end"
