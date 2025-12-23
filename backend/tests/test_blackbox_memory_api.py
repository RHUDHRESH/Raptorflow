import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from uuid import uuid4
from datetime import datetime
from backend.main import app
from backend.api.v1.blackbox_memory import get_blackbox_service

client = TestClient(app)

def test_search_memory_endpoint():
    mock_service = MagicMock()
    mock_service.search_strategic_memory.return_value = [{"content": "matched"}]
    app.dependency_overrides[get_blackbox_service] = lambda: mock_service
    
    response = client.get("/v1/blackbox/memory/search?query=test")
    assert response.status_code == 200
    assert response.json()[0]["content"] == "matched"
    mock_service.search_strategic_memory.assert_called_with(query="test", limit=5)
    
    app.dependency_overrides.clear()

def test_categorize_learning_endpoint():
    mock_service = MagicMock()
    mock_service.categorize_learning.return_value = "strategic"
    app.dependency_overrides[get_blackbox_service] = lambda: mock_service
    
    response = client.post("/v1/blackbox/memory/categorize", json={"content": "new learning"})
    assert response.status_code == 200
    assert response.json()["category"] == "strategic"
    mock_service.categorize_learning.assert_called_with("new learning")
    
    app.dependency_overrides.clear()

def test_prune_memory_endpoint():
    mock_service = MagicMock()
    app.dependency_overrides[get_blackbox_service] = lambda: mock_service
    
    response = client.delete("/v1/blackbox/memory/prune?learning_type=tactical")
    assert response.status_code == 200
    assert response.json()["status"] == "pruned"
    mock_service.prune_strategic_memory.assert_called_once()
    
    app.dependency_overrides.clear()