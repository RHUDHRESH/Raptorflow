from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.specialists.icp_architect import (
    ICPArchitectAgent,
    ICPOutput,
    ICPPersona,
)
from models.cognitive import AgentMessage


@pytest.mark.asyncio
async def test_icp_intelligence_logic():
    """
    Phase 43/44: Verify that the ICPArchitectAgent profiles cohorts with demographics/psychographics.
    """
    expected_icp = ICPOutput(
        personas=[
            ICPPersona(
                name="Solo Founder",
                demographics={"job_title": "Founder", "industry": "SaaS"},
                psychographics={"values": ["Efficiency"], "status_games": "Competence"},
                pain_points=["No time"],
                buying_triggers=["Launch day"],
            )
        ],
        summary="Targeting busy founders.",
    )

    mock_runnable = AsyncMock()
    mock_runnable.ainvoke.return_value = expected_icp

    with patch("backend.agents.base.InferenceProvider") as mock_inference:
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_runnable
        mock_inference.get_model.return_value = mock_llm

        agent = ICPArchitectAgent()
        state = {
            "tenant_id": "test-tenant",
            "messages": [],
            "raw_prompt": "Profile our target audience.",
        }

        result = await agent(state)

        assert result["last_agent"] == "ICPArchitect"
        assert "Solo Founder" in result["messages"][0].content
