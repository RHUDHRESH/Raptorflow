import sys
from unittest.mock import MagicMock

import pytest

# Mock before import
mock_vertex = MagicMock()
sys.modules["langchain_google_vertexai"] = mock_vertex

from backend.core.vertex_setup import get_embedding_client


def test_vertex_embedding_client_setup():
    client = get_embedding_client()
    assert client is not None
    mock_vertex.VertexAIEmbeddings.assert_called_once_with(
        model_name="text-embedding-004"
    )
