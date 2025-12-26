from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from core.auth import get_current_user
from main import app


class MockUser:
    def __init__(self):
        self.id = uuid4()
        self.tenant_id = uuid4()
        self.email = "test@example.com"


def mock_get_current_user():
    return MockUser()


@pytest.fixture
def client():
    app.dependency_overrides[get_current_user] = mock_get_current_user
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_generate_soundbites_success(client):
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

    import json

    mock_response = AsyncMock()
    mock_response.content = json.dumps(mock_soundbites)

    with patch("inference.InferenceProvider.get_model") as mock_get_model:
        mock_model = AsyncMock()
        mock_model.ainvoke.return_value = mock_response
        mock_get_model.return_value = mock_model

        request_data = {
            "jtbd": {
                "workspace_id": str(uuid4()),
                "functional_job": "automate marketing",
                "emotional_job": "feel in control",
                "social_job": "be a leader",
            },
            "hierarchy": {
                "workspace_id": str(uuid4()),
                "essence": "unified ops",
                "core_message": "consolidate tools",
                "pillars": ["reliability", "speed"],
            },
            "awareness": {
                "workspace_id": str(uuid4()),
                "unaware": "reveal pain",
                "problem": "amplify pain",
                "solution": "show mechanism",
                "product": "handle doubt",
                "most": "give offer",
            },
            "proof_points": ["89% success rate", "14 day migration"],
        }

        response = client.post("/v1/synthesis/soundbites", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "soundbites" in data
        assert len(data["soundbites"]) == 7
        assert data["soundbites"][0]["type"] == "problem_revelation"
        assert "28 hours/week" in data["soundbites"][0]["content"]
