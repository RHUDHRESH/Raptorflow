from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_initiate_payment_api():
    """Test the payment initiation endpoint."""
    response = client.post(
        "/v1/payments/initiate",
        params={
            "user_id": "user1",
            "amount": 10.5,
            "transaction_id": "tx789",
            "redirect_url": "http://localhost:3000/success",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "url" in data
    assert "payload" in data
    assert "checksum" in data


def test_webhook_api_missing_header():
    """Test webhook fails without X-VERIFY header."""
    response = client.post("/v1/payments/webhook", json={"response": "..."})
    assert response.status_code == 400
    assert response.json()["detail"] == "Missing X-VERIFY header"


def test_webhook_api_invalid_checksum():
    """Test webhook fails with invalid checksum."""
    response = client.post(
        "/v1/payments/webhook",
        headers={"X-VERIFY": "invalid"},
        json={"response": "..."},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid checksum"
