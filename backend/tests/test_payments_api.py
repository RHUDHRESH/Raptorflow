import os
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.services.payment_service import PhonePeCallbackError

os.environ.setdefault("PHONEPE_CLIENT_ID", "client-id")
os.environ.setdefault("PHONEPE_CLIENT_SECRET", "client-secret")
os.environ.setdefault("PHONEPE_CLIENT_VERSION", "1")
os.environ.setdefault("PHONEPE_ENV", "SANDBOX")
os.environ.setdefault("PHONEPE_WEBHOOK_USERNAME", "webhook-user")
os.environ.setdefault("PHONEPE_WEBHOOK_PASSWORD", "webhook-pass")

from backend.main import app  # noqa: E402

client = TestClient(app)


def test_initiate_payment_api():
    """Test the payment initiation endpoint."""
    with patch("backend.api.v1.payments.payment_service") as service:
        service.initiate_payment.return_value = {
            "url": "https://phonepe.com/checkout",
            "merchantOrderId": "tx789",
        }
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
    assert data["url"] == "https://phonepe.com/checkout"
    assert data["merchantOrderId"] == "tx789"


def test_webhook_api_missing_header():
    """Test webhook fails without Authorization header."""
    response = client.post("/v1/payments/webhook", json={"response": "..."})
    assert response.status_code == 400
    assert response.json()["detail"] == "Missing Authorization header"


def test_webhook_api_invalid_callback():
    """Test webhook fails with invalid callback authentication."""
    with patch("backend.api.v1.payments.payment_service") as service:
        service.handle_webhook.side_effect = PhonePeCallbackError("Invalid callback")
        response = client.post(
            "/v1/payments/webhook",
            headers={"Authorization": "invalid"},
            json={"response": "..."},
        )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid callback"
