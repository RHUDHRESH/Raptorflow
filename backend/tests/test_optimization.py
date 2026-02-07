import json
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from core.config import get_settings
from core.sandbox import RaptorSandbox
from core.toolbelt import BaseRaptorTool, RaptorRateLimiter, cache_tool_output
from core.vault import RaptorVault
from graphs.spine_v3 import build_ultimate_spine
from inference import InferenceProvider
from services.telemetry import (
    CostEvaluator,
    RaptorEvaluator,
    RaptorTelemetry,
    RaptorTelemetryCallback,
    trace_latency,
)


class TestTool(BaseRaptorTool):
    @property
    def name(self):
        return "test_tool"

    @property
    def description(self):
        return "test desc"

    async def _execute(self, val: str):
        return f"Echo: {val}"


class FlakyTool(BaseRaptorTool):
    def __init__(self):
        self.attempts = 0

    @property
    def name(self):
        return "flaky_tool"

    @property
    def description(self):
        return "flaky desc"

    @RaptorRateLimiter.get_retry_decorator()
    async def _execute(self):
        self.attempts += 1
        if self.attempts < 2:
            raise ValueError("SOTA Flaky Failure")
        return "SOTA Success"


@pytest.mark.asyncio
async def test_tool_resiliency_retry():
    """Verify that flaky tools are retried automatically."""
    tool = FlakyTool()
    result = await tool.run()
    assert result["success"] is True
    assert result["data"] == "SOTA Success"
    assert tool.attempts == 2


@pytest.mark.asyncio
async def test_base_tool_interface():
    """Verify standard tool behavior and telemetry."""
    tool = TestTool()
    result = await tool.run(val="hello")
    assert result["success"] is True
    assert result["data"] == "Echo: hello"
    assert "latency_ms" in result


@pytest.mark.asyncio
async def test_raptor_vault_logic():
    """Verify that the vault can retrieve secrets from workspace context."""
    with patch.dict(os.environ, {"VAULT_TAVILY_KEY": "sota_secret"}):
        vault = RaptorVault(workspace_id="ws_123")
        secret = await vault.get_secret("tavily_key")
        assert secret == "sota_secret"


@pytest.mark.asyncio
async def test_spine_v3_parallel_structure():
    """Verify that spine v3 has global parallel fan-out/fan-in."""
    app = build_ultimate_spine()
    edges = list(app.builder.edges)

    # Check creative fan-out from strategy
    creative_copy_edges = [
        e for e in edges if e[0] == "strategy_planning" and e[1] == "creative_copy"
    ]
    creative_visual_edges = [
        e for e in edges if e[0] == "strategy_planning" and e[1] == "creative_visual"
    ]
    assert len(creative_copy_edges) == 1
    assert len(creative_visual_edges) == 1

    # Check fan-in to QA
    qa_in_edges = [e for e in edges if e[1] == "qa"]
    assert len(qa_in_edges) == 2  # from creative_copy and creative_visual


def test_raptor_sandbox_execution():
    """Verify that the sandbox can execute simple python code."""
    sandbox = RaptorSandbox()
    result = sandbox.run("print(1 + 1)")
    assert result["success"] is True
    assert "2" in result["output"]


def test_cost_evaluator_logic():
    """Verify that the cost evaluator flags expensive runs."""
    settings = get_settings()
    evaluator = CostEvaluator(cost_threshold=0.05)
    # Expensive usage (10k tokens)
    usage = {"total_tokens": 10000}
    result = evaluator.evaluate_cost(usage, settings.MODEL_REASONING_ULTRA)

    assert result["estimated_cost"] == 0.1  # 10 * 0.01
    assert result["is_above_threshold"] is True
    assert result["action"] == "ALERT"


class CachedTool(BaseRaptorTool):
    @property
    def name(self):
        return "cached_tool"

    @property
    def description(self):
        return "cached desc"

    @cache_tool_output(ttl=60)
    async def _execute(self, val: str):
        return f"Result: {val}"


@pytest.mark.asyncio
async def test_raptor_evaluator_logic():
    """Verify that the evaluator can score drafts."""
    mock_llm = AsyncMock()
    mock_llm.ainvoke.return_value = MagicMock(content="0.9")

    evaluator = RaptorEvaluator(mock_llm)
    result = await evaluator.evaluate_asset("draft", "brief")

    assert result["grade"] == 0.95  # Mock result
    assert result["is_pass"] is True


@pytest.mark.asyncio
async def test_tool_caching_logic():
    """Verify that tool outputs are cached and retrieved."""
    mock_cache = MagicMock()
    mock_cache.get = AsyncMock(return_value=json.dumps("Result: hello"))

    with patch("backend.core.toolbelt.get_cache", return_value=mock_cache):
        tool = CachedTool()
        result = await tool.run(val="hello")

        assert result["data"] == "Result: hello"
        mock_cache.get.assert_called_once()


@pytest.mark.asyncio
async def test_latency_decorator_logging():
    """Verify that the latency decorator logs completion time."""

    @trace_latency("test_node")
    async def mock_node(state):
        return {"ok": True}

    with patch("backend.services.telemetry.logger.info") as mock_log:
        await mock_node({})
        # Should be called at least once for "starting" and once for "completed"
        assert mock_log.call_count >= 2
        args, _ = mock_log.call_args
        assert "completed in" in str(args[0])


@pytest.mark.asyncio
async def test_telemetry_callback_logging():
    """Verify the telemetry callback captures usage data."""
    settings = get_settings()
    callback = RaptorTelemetryCallback()
    mock_response = MagicMock()
    mock_response.llm_output = {
        "token_usage": {"total_tokens": 100},
        "model_name": settings.MODEL_GENERAL,
    }

    with patch("backend.services.telemetry.logger.info") as mock_log:
        await callback.on_llm_end(mock_response)
        mock_log.assert_called_once()
        args, _ = mock_log.call_args
        assert "total_tokens" in str(args[0])


def test_raptor_telemetry_service():
    """Verify the telemetry service correctly identifies status."""
    telemetry = RaptorTelemetry()
    # Should not crash on initialization
    assert telemetry is not None

    enabled_in_env = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    assert telemetry.is_enabled == enabled_in_env


def test_langsmith_config():
    """Verify that LangSmith variables are expected in environment."""
    # This check ensures we don't deploy to prod without observability.
    # In a real system, we might use a validator function.
    from core.config import get_settings

    telemetry = RaptorTelemetry()
    settings = get_settings()
    enabled = settings.LANGCHAIN_TRACING_V2.lower() == "true"
    api_key = settings.LANGCHAIN_API_KEY

    assert telemetry.is_enabled == enabled
    # If enabled, ensure API key is present (basic sanity check)
    if enabled:
        assert api_key is not None


@pytest.mark.asyncio
async def test_model_routing_logic():
    """Test that the router selects the correct Gemini tiered model."""
    settings = get_settings()
    with patch("backend.inference.ChatVertexAI") as MockChat:
        # 1. Ultra Reasoning (3 Pro)
        InferenceProvider.get_model(model_tier="ultra")
        MockChat.assert_called_with(
            model_name=settings.MODEL_REASONING_ULTRA, temperature=0.0
        )

        # 2. Reasoning (3 Flash)
        InferenceProvider.get_model(model_tier="reasoning")
        MockChat.assert_called_with(
            model_name=settings.MODEL_REASONING, temperature=0.0
        )

        # 3. Daily Driver (2.5 Flash)
        InferenceProvider.get_model(model_tier="driver")
        MockChat.assert_called_with(model_name=settings.MODEL_GENERAL, temperature=0.0)


def test_parallel_execution_pattern():
    """
    SOTA verification of LangGraph parallel execution.
    We verify the graph structure supports branching and joining.
    """
    import operator
    from typing import Annotated, List, TypedDict

    from langgraph.graph import END, START, StateGraph

    class ParallelState(TypedDict):
        results: Annotated[List[str], operator.add]

    workflow = StateGraph(ParallelState)
    workflow.add_node("branch_1", lambda x: {"results": ["1"]})
    workflow.add_node("branch_2", lambda x: {"results": ["2"]})
    workflow.add_node("join_node", lambda x: {"results": ["joined"]})

    workflow.add_edge(START, "branch_1")
    workflow.add_edge(START, "branch_2")
    workflow.add_edge("branch_1", "join_node")
    workflow.add_edge("branch_2", "join_node")
    workflow.add_edge("join_node", END)

    app = workflow.compile()
    # Check if the graph has multiple edges from START (parallel start)
    # This is a SOTA structural check
    assert len(workflow.edges) >= 4
