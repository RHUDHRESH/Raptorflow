from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from uuid import uuid4
from datetime import datetime
from backend.main import app

client = TestClient(app)

def test_upsert_learning_endpoint():
    with patch("backend.api.v1.blackbox_memory.get_blackbox_service") as mock_get_service:
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        
        payload = {
            "content": "LinkedIn engagement high at 9am",
            "learning_type": "tactical",
            "source_ids": [str(uuid4())]
        }
        
        response = client.post("/v1/blackbox/memory/upsert", json=payload)
        
        assert response.status_code == 201
        assert response.json() == {"status": "persisted"}
        mock_service.upsert_learning_embedding.assert_called_once()

def test_search_memory_endpoint():
    with patch("backend.api.v1.blackbox_memory.get_blackbox_service") as mock_get_service:
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.search_strategic_memory.return_value = [
            {"content": "found insight", "similarity": 0.9}
        ]
        
        response = client.get("/v1/blackbox/memory/search?query=test")
        
        assert response.status_code == 200
        assert len(response.json()) == 1
        mock_service.search_strategic_memory.assert_called_once_with(query="test", limit=5)

def test_link_evidence_endpoint():
    with patch("backend.api.v1.blackbox_memory.get_blackbox_service") as mock_get_service:
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        
        payload = {
            "learning_id": str(uuid4()),
            "trace_ids": [str(uuid4())]
        }
        
        response = client.post("/v1/blackbox/memory/link-evidence", json=payload)
        
        assert response.status_code == 200
        assert response.json() == {"status": "linked"}
        mock_service.link_learning_to_evidence.assert_called_once()

def test_get_planner_context_endpoint():
    with patch("backend.api.v1.blackbox_memory.get_blackbox_service") as mock_get_service:
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.get_memory_context_for_planner.return_value = "Formatted context"
        
        response = client.get("/v1/blackbox/memory/planner-context?move_type=linkedin")
        
        assert response.status_code == 200
        assert response.json() == {"context": "Formatted context"}
        mock_service.get_memory_context_for_planner.assert_called_once_with(move_type="linkedin", limit=5)

def test_prune_memory_endpoint():
    with patch("backend.api.v1.blackbox_memory.get_blackbox_service") as mock_get_service:
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        
        before_date = "2023-01-01T00:00:00"
        response = client.delete(f"/v1/blackbox/memory/prune?learning_type=tactical&before={before_date}")
        
        assert response.status_code == 200
        assert response.json() == {"status": "pruned"}
        mock_service.prune_strategic_memory.assert_called_once()
