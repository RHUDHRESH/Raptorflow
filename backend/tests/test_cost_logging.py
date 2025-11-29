"""
Tests for the canonical cost logging service.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from decimal import Decimal
from backend.services.cost_logging import CostLoggingService, MODEL_PRICING


class TestCostLoggingService:
    """Test the cost logging service"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        return CostLoggingService()

    def test_estimate_cost_usd_known_model(self, service):
        """Test cost calculation for known model"""
        model = "gemini-1.5-flash"
        total_tokens = 2000  # 1000 input + 1000 output

        cost = service.estimate_cost_usd(model, total_tokens)

        # Expected: (1000 * 0.000075) + (1000 * 0.0003) = 0.075 + 0.3 = 0.375
        expected = Decimal("0.375000")
        assert cost == expected

    def test_estimate_cost_usd_unknown_model(self, service):
        """Test cost calculation falls back to highest tier for unknown model"""
        model = "unknown-model"
        total_tokens = 2000

        cost = service.estimate_cost_usd(model, total_tokens)

        # Should use "unknown" pricing (1.25 per 1000 input + 5 per 1000 output)
        # (1000 * 0.00125) + (1000 * 0.005) = 1.25 + 5 = 6.25
        expected = Decimal("6.250000")
        assert cost == expected

    def test_estimate_cost_usd_zero_tokens(self, service):
        """Test cost calculation with zero tokens"""
        cost = service.estimate_cost_usd("gemini-1.5-flash", 0)
        assert cost == Decimal("0.000000")

    @pytest.mark.asyncio
    async def test_log_llm_call_basic(self, service):
        """Test basic LLM call logging"""
        # Mock the database
        service.db = AsyncMock()
        service.db.insert = AsyncMock()

        await service.log_llm_call(
            workspace_id="ws-123",
            model="gemini-1.5-flash",
            prompt_tokens=100,
            completion_tokens=50,
        )

        # Verify DB was called
        assert service.db.insert.called
        call_args = service.db.insert.call_args
        assert call_args[0][0] == "cost_logs"

        data = call_args[0][1]
        assert data["workspace_id"] == "ws-123"
        assert data["model"] == "gemini-1.5-flash"
        assert data["prompt_tokens"] == 100
        assert data["completion_tokens"] == 50
        assert data["total_tokens"] == 150
        assert isinstance(data["estimated_cost_usd"], float)
        assert data["estimated_cost_usd"] > 0
        assert data["agent_id"] is None
        assert data["agent_run_id"] is None

    @pytest.mark.asyncio
    async def test_log_llm_call_with_agent(self, service):
        """Test LLM call logging with agent linkage"""
        service.db = AsyncMock()
        service.db.insert = AsyncMock()

        agent_id = "agent-456"
        agent_run_id = "run-789"

        await service.log_llm_call(
            workspace_id="ws-123",
            model="gemini-1.5-pro",
            prompt_tokens=200,
            completion_tokens=100,
            agent_id=agent_id,
            agent_run_id=agent_run_id,
        )

        # Verify agent linkage
        call_args = service.db.insert.call_args
        data = call_args[0][1]
        assert data["agent_id"] == agent_id
        assert data["agent_run_id"] == agent_run_id

    @pytest.mark.asyncio
    async def test_log_llm_call_total_tokens_calculation(self, service):
        """Test that total_tokens is correctly calculated"""
        service.db = AsyncMock()
        service.db.insert = AsyncMock()

        prompt_tokens = 175
        completion_tokens = 89

        await service.log_llm_call(
            workspace_id="ws-123",
            model="gemini-1.5-flash",
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )

        call_args = service.db.insert.call_args
        data = call_args[0][1]
        assert data["total_tokens"] == prompt_tokens + completion_tokens

    @pytest.mark.asyncio
    async def test_log_llm_call_db_error_handling(self, service):
        """Test that DB errors are handled gracefully"""
        service.db = AsyncMock()
        service.db.insert = AsyncMock(side_effect=Exception("DB error"))

        # Should not raise - logging failures shouldn't crash the app
        await service.log_llm_call(
            workspace_id="ws-123",
            model="gemini-1.5-flash",
            prompt_tokens=100,
            completion_tokens=50,
        )

        # Ensure insert was attempted
        assert service.db.insert.called

    @pytest.mark.asyncio
    async def test_log_llm_call_from_response_stub(self, service):
        """Test the convenience wrapper (currently stub)"""
        # Currently just logs a warning, doesn't crash
        await service.log_llm_call_from_response(
            workspace_id="ws-123",
            model="test-model",
        )

        # No assertions needed - just verifies it doesn't crash


def test_model_pricing_configuration():
    """Test that pricing config is properly structured"""
    assert "gemini-1.5-flash" in MODEL_PRICING
    assert "gemini-1.5-pro" in MODEL_PRICING
    assert "unknown" in MODEL_PRICING

    for model, pricing in MODEL_PRICING.items():
        assert "input" in pricing
        assert "output" in pricing
        assert pricing["input"] > 0
        assert pricing["output"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
