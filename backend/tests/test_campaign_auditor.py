from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.graphs.moves_campaigns_orchestrator import moves_campaigns_orchestrator


@pytest.fixture
def mock_auditor_agents():
    with patch(
        "backend.graphs.moves_campaigns_orchestrator.SemanticMemory",
        new_callable=MagicMock,
    ) as mock_semantic, patch(
        "backend.graphs.moves_campaigns_orchestrator.LongTermMemory",
        new_callable=MagicMock,
    ) as mock_ltm, patch(
        "backend.graphs.moves_campaigns_orchestrator.BrandVoiceAligner",
        new_callable=MagicMock,
    ) as mock_aligner, patch(
        "backend.graphs.moves_campaigns_orchestrator.InferenceProvider",
        new_callable=MagicMock,
    ) as mock_inf:

        sem_instance = mock_semantic.return_value
        sem_instance.search = AsyncMock(return_value=[{"content": "mocked"}])

        ltm_instance = mock_ltm.return_value
        ltm_instance.log_decision = AsyncMock()

        aligner_instance = mock_aligner.return_value
        aligner_instance.side_effect = AsyncMock(
            return_value={"context_brief": {"brand_alignment": {"score": 0.9}}}
        )

        mock_inf.get_model.return_value = MagicMock()

        yield sem_instance, ltm_instance, aligner_instance


@pytest.mark.asyncio
async def test_campaign_auditor_node_integration(mock_auditor_agents):
    _, _, mock_aligner = mock_auditor_agents
    config = {"configurable": {"thread_id": "audit-test"}}

    # Run the graph until the point where Campaign Auditor should trigger
    # In our proposed flow: plan_campaign -> campaign_auditor -> approve_campaign

    await moves_campaigns_orchestrator.ainvoke(
        {"tenant_id": "test-tenant", "status": "new", "messages": []}, config
    )

    # Verify aligner was called
    mock_aligner.assert_called()

    state = await moves_campaigns_orchestrator.aget_state(config)
    assert "brand_alignment" in state.values.get("context_brief", {})


@pytest.mark.asyncio
async def test_campaign_auditor_node_direct():
    from backend.graphs.moves_campaigns_orchestrator import campaign_auditor

    mock_llm = MagicMock()

    with patch(
        "backend.graphs.moves_campaigns_orchestrator.InferenceProvider.get_model",
        return_value=mock_llm,
    ), patch(
        "backend.graphs.moves_campaigns_orchestrator.BrandVoiceAligner",
        new_callable=MagicMock,
    ) as mock_aligner:

        mock_aligner.return_value.side_effect = AsyncMock(
            return_value={"context_brief": {"brand_alignment": {"score": 0.9}}}
        )

        state = {"context_brief": {}, "messages": []}
        result = await campaign_auditor(state)

        assert "brand_alignment" in result["context_brief"]


@pytest.mark.asyncio
async def test_handle_error_node():
    from backend.graphs.moves_campaigns_orchestrator import handle_error

    state = {"error": "Test Error", "messages": []}
    result = await handle_error(state)
    assert result["status"] == "error"
    assert "CRITICAL ERROR: Test Error" in result["messages"]
    assert result["error"] is None


def test_get_checkpointer_dev():
    from langgraph.checkpoint.memory import MemorySaver

    from backend.graphs.moves_campaigns_orchestrator import get_checkpointer

    with patch("os.getenv", return_value=None):
        cp = get_checkpointer()
        assert isinstance(cp, MemorySaver)


def test_router_logic():
    from backend.graphs.moves_campaigns_orchestrator import END, router

    assert router({"status": "planning"}) == "campaign"
    assert router({"status": "monitoring"}) == "moves"
    assert router({"error": "broken"}) == "error"
    assert router({"status": "complete"}) == END
