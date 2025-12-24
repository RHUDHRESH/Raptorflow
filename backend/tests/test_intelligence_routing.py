import sys
from unittest.mock import MagicMock, patch

# Prevent real imports that cause crashes
sys.modules["langchain_google_vertexai"] = MagicMock()

from backend.inference import InferenceProvider  # noqa: E402


def test_intelligence_mapping_ultra():
    """Verify 'ultra' tier maps to high-end model and has fallbacks."""
    with patch("backend.inference.ChatVertexAI") as mock_chat:
        InferenceProvider.get_model(model_tier="ultra")

        # ultra tier should call ChatVertexAI multiple times (primary + fallbacks)
        calls = mock_chat.call_args_list

        # Primary
        assert calls[0].kwargs["model_name"] == "gemini-3-flash-preview"

        # Fallbacks
        fallback_names = [c.kwargs["model_name"] for c in calls[1:]]
        assert "gemini-2.5-flash" in fallback_names
        assert "gemini-2.0-flash" in fallback_names


def test_intelligence_mapping_mundane():
    """Verify 'mundane' tier maps to base model."""
    with patch("backend.inference.ChatVertexAI") as mock_chat:
        InferenceProvider.get_model(model_tier="mundane")
        args, kwargs = mock_chat.call_args
        assert kwargs["model_name"] == "gemini-1.5-flash"


def test_intelligence_mapping_default():
    """Verify default tier maps to driver model."""
    with patch("backend.inference.ChatVertexAI") as mock_chat:
        InferenceProvider.get_model()
        args, kwargs = mock_chat.call_args
        assert kwargs["model_name"] == "gemini-2.0-flash"
