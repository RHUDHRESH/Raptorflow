import json
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from api.v1.synthesis import SynthesisRequest, generate_soundbites
from models.foundation import JTBD, AwarenessMatrix, MessageHierarchy


@pytest.mark.asyncio
async def test_generate_soundbites_logic():
    mock_soundbites = [
        {
            "type": "problem_revelation",
            "content": "Your team loses 28 hours/week to manual tasks.",
        },
        {
            "type": "agitation",
            "content": "That is strategic time you will never get back.",
        },
        {
            "type": "mechanism",
            "content": "We unified the architecture so data flows once.",
        },
        {
            "type": "objection_handling",
            "content": "Migration takes 14 days, guaranteed.",
        },
        {
            "type": "transformation",
            "content": "By Q2, your campaigns run on autopilot.",
        },
        {"type": "positioning", "content": "Built for teams that think in systems."},
        {"type": "urgency", "content": "Sign by Dec 31st for 3 months free."},
    ]

    mock_response = AsyncMock()
    mock_response.content = json.dumps(mock_soundbites)

    tenant_id = uuid4()

    with patch("api.v1.synthesis.InferenceProvider.get_model") as mock_get_model:
        mock_model = AsyncMock()
        mock_model.ainvoke.return_value = mock_response
        mock_get_model.return_value = mock_model

        request = SynthesisRequest(
            jtbd=JTBD(
                workspace_id=tenant_id,
                functional_job="automate marketing",
                emotional_job="feel in control",
                social_job="be a leader",
            ),
            hierarchy=MessageHierarchy(
                workspace_id=tenant_id,
                essence="unified ops",
                core_message="consolidate tools",
                pillars=["reliability", "speed"],
            ),
            awareness=AwarenessMatrix(
                workspace_id=tenant_id,
                unaware_strategy="reveal pain",
                problem_aware_strategy="amplify pain",
                solution_aware_strategy="show mechanism",
                product_aware_strategy="handle doubt",
                most_aware_strategy="give offer",
            ),
            proof_points=["89% success rate", "14 day migration"],
        )

        response = await generate_soundbites(request, tenant_id=tenant_id)

        assert len(response.soundbites) == 7
        assert response.soundbites[0].type == "problem_revelation"
        assert "28 hours/week" in response.soundbites[0].content
        assert response.soundbites[0].workspace_id == tenant_id
