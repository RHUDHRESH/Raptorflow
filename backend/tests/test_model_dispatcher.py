"""
Tests for the canonical ModelDispatcher service.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, patch
from decimal import Decimal

from backend.services.model_dispatcher import (
    ModelDispatcher,
    ModelDispatchRequest,
    ModelDispatchResponse,
    BudgetExceededError,
    MODEL_MAPPINGS,
    MONTHLY_WORKSPACE_BUDGET_USD,
)


class TestModelResolver:
    """Test model alias resolution."""

    @pytest.fixture
    def dispatcher(self):
        return ModelDispatcher()

    def test_resolve_model_fast(self, dispatcher):
        """Test 'fast' alias resolves correctly."""
        resolved = dispatcher._resolve_model("fast")
        assert resolved == MODEL_MAPPINGS["fast"]

    def test_resolve_model_standard(self, dispatcher):
        """Test 'standard' alias resolves correctly."""
        resolved = dispatcher._resolve_model("standard")
        assert resolved == MODEL_MAPPINGS["standard"]

    def test_resolve_model_heavy(self, dispatcher):
        """Test 'heavy' alias resolves correctly."""
        resolved = dispatcher._resolve_model("heavy")
        assert resolved == MODEL_MAPPINGS["heavy"]

    def test_resolve_full_model_path(self, dispatcher):
        """Test full model path passes through unchanged."""
        full_path = "gemini-1.5-pro"
        resolved = dispatcher._resolve_model(full_path)
        assert resolved == full_path

    def test_resolve_unknown_model(self, dispatcher):
        """Test unknown model raises ValueError."""
        with pytest.raises(ValueError, match="Unknown model"):
            dispatcher._resolve_model("unknown-model")


class TestBudgetChecking:
    """Test budget enforcement logic."""

    @pytest.fixture
    def dispatcher(self):
        return ModelDispatcher()

    @pytest.mark.asyncio
    async def test_budget_under_limit(self, dispatcher):
        """Test budget check passes when under limit."""
        dispatcher.supabase = AsyncMock()
        # Mock empty spend history
        mock_result = AsyncMock()
        mock_result.data = []
        dispatcher.supabase.client.table.return_value.select.return_value.eq.return_value.gte.return_value.execute = AsyncMock(return_value=mock_result)

        # Should not raise
        await dispatcher._check_budget("ws-123", 1.0)

    @pytest.mark.asyncio
    async def test_budget_over_limit(self, dispatcher):
        """Test budget check fails when over limit."""
        dispatcher.supabase = AsyncMock()
        # Mock existing spend near limit
        mock_result = AsyncMock()
        mock_result.data = [{"estimated_cost_usd": str(MONTHLY_WORKSPACE_BUDGET_USD - 1.0)}]
        dispatcher.supabase.client.table.return_value.select.return_value.eq.return_value.gte.return_value.execute = AsyncMock(return_value=mock_result)

        # Should raise BudgetExceededError
        with pytest.raises(BudgetExceededError) as exc_info:
            await dispatcher._check_budget("ws-123", 1.5)

        assert exc_info.value.workspace_id == "ws-123"
        assert abs(exc_info.value.current_spend - (MONTHLY_WORKSPACE_BUDGET_USD - 1.0)) < 0.01
        assert abs(exc_info.value.new_call_cost - 1.5) < 0.01

    @pytest.mark.asyncio
    async def test_budget_query_failure(self, dispatcher):
        """Test budget check assumes max spend on query failure."""
        dispatcher.supabase = AsyncMock()
        dispatcher.supabase.client.table.side_effect = Exception("DB error")

        # Should raise because we assume max spend
        with pytest.raises(BudgetExceededError):
            await dispatcher._check_budget("ws-123", 0.1)


class TestCaching:
    """Test caching behavior."""

    @pytest.fixture
    def dispatcher(self):
        return ModelDispatcher()

    @pytest.mark.asyncio
    async def test_no_cache_key_returns_none(self, dispatcher):
        """Test no caching when cache_key is None."""
        result = await dispatcher._maybe_get_cached(None)
        assert result is None

        await dispatcher._maybe_set_cached(None, None, 0)
        # Should not crash

    # TODO: Add Redis integration tests once caching is implemented


class TestDispatchIntegration:
    """Test full dispatch integration."""

    @pytest.fixture
    def dispatcher(self):
        return ModelDispatcher()

    @pytest.mark.asyncio
    async def test_dispatch_basic_flow(self, dispatcher):
        """Test complete dispatch flow with mocked dependencies."""
        # Mock dependencies
        dispatcher.supabase = AsyncMock()
        mock_budget_result = AsyncMock()
        mock_budget_result.data = []  # No existing spend
        dispatcher.supabase.client.table.return_value.select.return_value.eq.return_value.gte.return_value.execute = AsyncMock(return_value=mock_budget_result)

        # Mock vertex_ai_client
        with patch("backend.services.model_dispatcher.vertex_ai_client") as mock_client:
            mock_client.chat_completion = AsyncMock(return_value="Mocked response")

            # Mock cost logging
            with patch("backend.services.model_dispatcher.log_llm_call") as mock_log_call:
                # Make request
                request = ModelDispatchRequest(
                    workspace_id="ws-123",
                    model="fast",
                    messages=[{"role": "user", "content": "Test message"}],
                )

                response = await dispatcher.dispatch(request)

                # Verify vertex client was called
                mock_client.chat_completion.assert_called_once()
                call_kwargs = mock_client.chat_completion.call_args[1]
                assert call_kwargs["model_type"] == "fast"
                assert len(call_kwargs["messages"]) == 1

                # Verify cost logging was called
                mock_log_call.assert_called_once()
                cost_call_args = mock_log_call.call_args[1]
                assert cost_call_args["workspace_id"] == "ws-123"
                assert "gemini-2.5-flash-002" in cost_call_args["model"]
                assert cost_call_args["prompt_tokens"] > 0
                assert cost_call_args["completion_tokens"] > 0

                # Verify response structure
                assert response.raw_response == "Mocked response"
                assert response.model == MODEL_MAPPINGS["fast"]
                assert response.prompt_tokens > 0
                assert response.completion_tokens > 0
                assert response.total_tokens == response.prompt_tokens + response.completion_tokens
                assert response.estimated_cost_usd > 0
                assert not response.cached

    @pytest.mark.asyncio
    async def test_dispatch_with_agent_metadata(self, dispatcher):
        """Test dispatch includes agent metadata."""
        dispatcher.supabase = AsyncMock()
        mock_budget_result = AsyncMock()
        mock_budget_result.data = []
        dispatcher.supabase.client.table.return_value.select.return_value.eq.return_value.gte.return_value.execute = AsyncMock(return_value=mock_budget_result)

        with patch("backend.services.model_dispatcher.vertex_ai_client") as mock_client:
            mock_client.chat_completion = AsyncMock(return_value="Agent response")

            with patch("backend.services.model_dispatcher.log_llm_call") as mock_log_call:
                request = ModelDispatchRequest(
                    workspace_id="ws-123",
                    model="standard",
                    messages=[{"role": "user", "content": "Agent test"}],
                    agent_id="agent-456",
                    agent_run_id="run-789",
                )

                await dispatcher.dispatch(request)

                # Verify agent metadata passed to cost logging
                cost_call_args = mock_log_call.call_args[1]
                assert cost_call_args["agent_id"] == "agent-456"
                assert cost_call_args["agent_run_id"] == "run-789"

    @pytest.mark.asyncio
    async def test_dispatch_budget_exceeded(self, dispatcher):
        """Test dispatch fails when budget exceeded."""
        dispatcher.supabase = AsyncMock()
        # Mock high existing spend
        mock_result = AsyncMock()
        mock_result.data = [{"estimated_cost_usd": str(MONTHLY_WORKSPACE_BUDGET_USD)}]
        dispatcher.supabase.client.table.return_value.select.return_value.eq.return_value.gte.return_value.execute = AsyncMock(return_value=mock_result)

        request = ModelDispatchRequest(
            workspace_id="ws-123",
            model="fast",
            messages=[{"role": "user", "content": "Test"}],
        )

        # Should raise BudgetExceededError before calling Vertex AI
        with pytest.raises(BudgetExceededError):
            await dispatcher.dispatch(request)

    @pytest.mark.asyncio
    async def test_dispatch_model_resolution_error(self, dispatcher):
        """Test dispatch fails on invalid model."""
        request = ModelDispatchRequest(
            workspace_id="ws-123",
            model="invalid-model",
            messages=[{"role": "user", "content": "Test"}],
        )

        # Should raise ValueError before budget check
        with pytest.raises(ValueError, match="Unknown model"):
            await dispatcher.dispatch(request)


def test_model_mappings():
    """Test model mappings are properly configured."""
    assert len(MODEL_MAPPINGS) == 3
    assert "fast" in MODEL_MAPPINGS
    assert "standard" in MODEL_MAPPINGS
    assert "heavy" in MODEL_MAPPINGS

    for alias, model_id in MODEL_MAPPINGS.items():
        assert "gemini" in model_id.lower()


def test_budget_constants():
    """Test budget constants are reasonable."""
    assert MONTHLY_WORKSPACE_BUDGET_USD > 0
    assert MONTHLY_WORKSPACE_BUDGET_USD <= 100  # Reasonable upper bound


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
