import pytest

from backend.agents.specialists.governor import GovernorAgent


@pytest.mark.asyncio
async def test_governor_audit_logic():
    """Test the logic of the financial governor specialist."""
    agent = GovernorAgent()

    state = {"instructions": "Audit budget for tenant_123", "messages": []}

    result = await agent(state)
    assert "burn_rate" in result
    assert "budget_remaining" in result
    assert "risk_level" in result
    assert result["risk_level"] in ["low", "medium", "high", "critical"]


@pytest.mark.asyncio
async def test_governor_risk_levels():
    """Test the risk level logic in GovernorAgent."""
    from unittest.mock import patch

    agent = GovernorAgent()

    # Test High Risk (Budget low)
    with patch("random.uniform") as mock_rand:
        mock_stats = [10.0, 100.0]  # burn_rate, budget_remaining
        mock_rand.side_effect = mock_stats
        result = await agent({})
        assert result["risk_level"] == "high"

    # Test Medium Risk (Burn high)
    with patch("random.uniform") as mock_rand:
        mock_stats = [45.0, 1000.0]
        mock_rand.side_effect = mock_stats
        result = await agent({})
        assert result["risk_level"] == "medium"

    # Test Low Risk
    with patch("random.uniform") as mock_rand:
        mock_stats = [5.0, 2000.0]
        mock_rand.side_effect = mock_stats
        result = await agent({})
        assert result["risk_level"] == "low"
