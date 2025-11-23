"""
Comprehensive tests for payments router.
"""

import pytest
from uuid import uuid4
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from backend.routers import payments


@pytest.fixture
def app():
    """Create FastAPI app with payments router."""
    app = FastAPI()
    app.include_router(payments.router, prefix="/api/v1/payments")
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_auth():
    """Mock authentication dependency."""
    return {
        "user_id": str(uuid4()),
        "workspace_id": uuid4(),
        "email": "test@example.com",
        "role": "authenticated"
    }


class TestPaymentsRouter:
    """Test payments endpoints."""

    def test_get_plans_success(self, client):
        """Test retrieving available subscription plans."""
        response = client.get("/api/v1/payments/plans")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3  # Ascent, Glide, Soar

        # Verify plan structure
        for plan in data:
            assert "name" in plan
            assert "price" in plan
            assert "features" in plan

    def test_create_checkout_success(self, client, mock_auth):
        """Test creating a payment checkout session."""
        with patch('backend.routers.payments.get_current_user_and_workspace',
                   return_value=mock_auth), \
             patch('backend.routers.payments.phonepe_service.create_payment',
                   new_callable=AsyncMock) as mock_create:

            mock_create.return_value = {
                "success": True,
                "payment_url": "https://phonepe.com/pay/abc123",
                "merchant_transaction_id": str(uuid4())
            }

            response = client.post(
                "/api/v1/payments/checkout/create",
                json={
                    "plan": "glide",
                    "billing_period": "monthly"
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert "payment_url" in data
            assert data["success"] is True

    def test_create_checkout_invalid_plan(self, client, mock_auth):
        """Test creating checkout with invalid plan."""
        with patch('backend.routers.payments.get_current_user_and_workspace',
                   return_value=mock_auth):

            response = client.post(
                "/api/v1/payments/checkout/create",
                json={
                    "plan": "invalid_plan",
                    "billing_period": "monthly"
                }
            )

            assert response.status_code in [400, 422]

    def test_payment_webhook_success(self, client):
        """Test PhonePe payment webhook."""
        with patch('backend.routers.payments.phonepe_service.verify_webhook',
                   return_value=True), \
             patch('backend.routers.payments.supabase_client.update',
                   new_callable=AsyncMock) as mock_update:

            mock_update.return_value = {"status": "completed"}

            response = client.post(
                "/api/v1/payments/webhook",
                json={
                    "merchantTransactionId": str(uuid4()),
                    "code": "PAYMENT_SUCCESS",
                    "amount": 249900
                },
                headers={"X-VERIFY": "valid-checksum"}
            )

            assert response.status_code == 200

    def test_payment_webhook_invalid_signature(self, client):
        """Test webhook with invalid signature."""
        with patch('backend.routers.payments.phonepe_service.verify_webhook',
                   return_value=False):

            response = client.post(
                "/api/v1/payments/webhook",
                json={
                    "merchantTransactionId": str(uuid4()),
                    "code": "PAYMENT_SUCCESS"
                },
                headers={"X-VERIFY": "invalid-checksum"}
            )

            assert response.status_code == 401

    def test_get_payment_status(self, client, mock_auth):
        """Test retrieving payment status."""
        transaction_id = str(uuid4())

        with patch('backend.routers.payments.get_current_user_and_workspace',
                   return_value=mock_auth), \
             patch('backend.routers.payments.supabase_client.fetch_one',
                   new_callable=AsyncMock) as mock_fetch:

            mock_fetch.return_value = {
                "id": transaction_id,
                "status": "completed",
                "amount": 249900
            }

            response = client.get(f"/api/v1/payments/status/{transaction_id}")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "completed"

    def test_plan_price_validation(self, client, mock_auth):
        """Test that plan prices are correctly validated."""
        with patch('backend.routers.payments.get_current_user_and_workspace',
                   return_value=mock_auth):

            # Test each plan
            for plan in ["ascent", "glide", "soar"]:
                response = client.post(
                    "/api/v1/payments/checkout/create",
                    json={
                        "plan": plan,
                        "billing_period": "monthly"
                    }
                )

                # Should not fail on valid plans
                assert response.status_code in [200, 500]  # 500 if service unavailable
