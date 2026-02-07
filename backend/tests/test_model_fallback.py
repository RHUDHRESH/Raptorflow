import sys
from unittest.mock import MagicMock, patch

import pytest

# SOTA Mocking: Prevent actual import of crashing modules
mock_vertex = MagicMock()
sys.modules["langchain_google_vertexai"] = mock_vertex

from inference import InferenceProvider


def test_inference_fallback_configuration():
    """
    Phase 33: Verify that fallback is configured for ultra/reasoning tiers.
    """
    # 1. Setup mock for 'ultra' tier (WITH fallback)
    mock_vertex.ChatVertexAI.reset_mock()
    primary_mock = MagicMock(name="primary_model")
    fallback_mock = MagicMock(name="fallback_model")
    runnable_with_fallbacks = MagicMock(name="runnable_with_fallbacks")

    # We need to handle multiple calls to ChatVertexAI
    # 1st call: primary, 2nd call: fallback
    mock_vertex.ChatVertexAI.side_effect = [primary_mock, fallback_mock]
    primary_mock.with_fallbacks.return_value = runnable_with_fallbacks

    model_ultra = InferenceProvider.get_model(model_tier="ultra")

    assert model_ultra == runnable_with_fallbacks
    assert mock_vertex.ChatVertexAI.call_count == 2
    primary_mock.with_fallbacks.assert_called_once_with([fallback_mock])

    # 2. Setup mock for 'driver' tier (WITHOUT fallback)
    mock_vertex.ChatVertexAI.reset_mock()
    mock_vertex.ChatVertexAI.side_effect = None
    driver_mock = MagicMock(name="driver_model")
    # Ensure it DOES NOT have 'with_fallbacks' called or doesn't return a fallback wrapper
    mock_vertex.ChatVertexAI.return_value = driver_mock

    model_driver = InferenceProvider.get_model(model_tier="driver")

    assert model_driver == driver_mock
    assert mock_vertex.ChatVertexAI.call_count == 1
    driver_mock.with_fallbacks.assert_not_called()
