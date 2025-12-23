import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from backend.main import app

client = TestClient(app)

def test_upload_logo_success():
    """Tests successful logo upload with mocking GCS."""
    file_content = b"fake-image-content"
    file_name = "test_logo.png"
    
    # Mock BrandAssetManager.upload_logo
    with patch("backend.api.v1.assets.BrandAssetManager.upload_logo") as mock_upload:
        mock_upload.return_value = "https://storage.googleapis.com/test-bucket/assets/logos/test_logo.png"
        
        response = client.post(
            "/v1/assets/upload-logo",
            files={"file": (file_name, file_content, "image/png")}
        )
        
        assert response.status_code == 200
        assert response.json()["url"] == mock_upload.return_value
        assert response.json()["status"] == "success"
        mock_upload.assert_called_once()

def test_upload_logo_invalid_type():
    """Tests rejection of invalid file types."""
    response = client.post(
        "/v1/assets/upload-logo",
        files={"file": ("test.txt", b"hello", "text/plain")}
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]
