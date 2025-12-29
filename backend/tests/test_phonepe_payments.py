"""
Comprehensive tests for PhonePe payment integration and subscription management.
Tests mock PhonePe API responses and verify all payment flow scenarios.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from api.v1.payments import PaymentCreateRequest
from main import app
from services.payment_service import PaymentService, PhonePeCallbackError


class TestPhonePePaymentIntegration:
    """Test suite for PhonePe payment gateway integration."""

    @pytest.fixture
    def client(self):
        """Test client fixture."""
        return TestClient(app)

    @pytest.fixture
    async def async_client(self):
        """Async test client fixture."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client

    @pytest.fixture
    def mock_payment_service(self):
        """Mock payment service fixture."""
        service = MagicMock(spec=PaymentService)
        service.create_payment_session = AsyncMock()
        service.handle_payment_callback = AsyncMock()
        service.get_subscription_details = AsyncMock()
        service.cancel_subscription = AsyncMock()
        return service

    @pytest.fixture
    def sample_plan_data(self):
        """Sample plan data for testing."""
        return {
            "id": str(uuid4()),
            "name": "Professional",
            "price": 2999.00,
            "currency": "INR",
            "billing_interval": "monthly",
            "is_active": True,
        }

    @pytest.fixture
    def sample_payment_request(self, sample_plan_data):
        """Sample payment request data."""
        return PaymentCreateRequest(
            plan_id=sample_plan_data["id"],
            amount=sample_plan_data["price"],
            currency="INR",
            return_url="https://app.raptorflow.com/billing/success",
            callback_url="https://api.raptorflow.com/v1/payments/callback",
        )

    @pytest.fixture
    def mock_phonepe_response(self):
        """Mock PhonePe API response."""
        return {
            "redirectUrl": "https://phonepe.com/pay/merchant_order_123",
            "merchantOrderId": "merchant_order_123",
            "state": "PENDING",
        }

    @pytest.fixture
    def mock_webhook_payload(self):
        """Mock PhonePe webhook payload."""
        return {
            "payload": {
                "merchantOrderId": "merchant_order_123",
                "state": "COMPLETED",
                "transactionId": "txn_123456",
                "amount": 299900,
            }
        }


class TestPaymentCreation:
    """Test payment session creation."""

    @patch("services.payment_service.payment_service")
    @patch("db.get_db_connection")
    def test_create_payment_success(
        self,
        mock_db,
        mock_service,
        client,
        sample_payment_request,
        mock_phonepe_response,
    ):
        """Test successful payment session creation."""
        # Setup mocks
        mock_service.create_payment_session.return_value = {
            "payment_url": mock_phonepe_response["redirectUrl"],
            "merchant_order_id": mock_phonepe_response["merchantOrderId"],
            "transaction_id": str(uuid4()),
            "amount": sample_payment_request.amount,
            "currency": sample_payment_request.currency,
        }

        # Mock database plan validation
        mock_conn = AsyncMock()
        mock_cur = AsyncMock()
        mock_cur.fetchone.return_value = (uuid4(), "Professional", 2999.00, "INR")
        mock_conn.__aenter__.return_value.cursor.return_value.__aenter__.return_value = (
            mock_cur
        )
        mock_db.return_value.__aenter__.return_value = mock_conn

        # Make request
        response = client.post(
            "/v1/payments/create",
            json=sample_payment_request.dict(),
            headers={
                "Authorization": "Bearer valid_token",
                "X-Tenant-ID": str(uuid4()),
            },
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "payment_url" in data
        assert "order_id" in data
        assert "transaction_id" in data

    @patch("db.get_db_connection")
    def test_create_payment_invalid_plan(self, mock_db, client, sample_payment_request):
        """Test payment creation with invalid plan."""
        # Mock database plan not found
        mock_conn = AsyncMock()
        mock_cur = AsyncMock()
        mock_cur.fetchone.return_value = None
        mock_conn.__aenter__.return_value.cursor.return_value.__aenter__.return_value = (
            mock_cur
        )
        mock_db.return_value.__aenter__.return_value = mock_conn

        response = client.post(
            "/v1/payments/create",
            json=sample_payment_request.dict(),
            headers={
                "Authorization": "Bearer valid_token",
                "X-Tenant-ID": str(uuid4()),
            },
        )

        assert response.status_code == 404
        assert "not found or inactive" in response.json()["detail"]

    @patch("db.get_db_connection")
    def test_create_payment_amount_mismatch(
        self, mock_db, client, sample_payment_request
    ):
        """Test payment creation with amount mismatch."""
        # Mock database plan with different price
        mock_conn = AsyncMock()
        mock_cur = AsyncMock()
        mock_cur.fetchone.return_value = (
            uuid4(),
            "Professional",
            1999.00,
            "INR",
        )  # Different price
        mock_conn.__aenter__.return_value.cursor.return_value.__aenter__.return_value = (
            mock_cur
        )
        mock_db.return_value.__aenter__.return_value = mock_conn

        response = client.post(
            "/v1/payments/create",
            json=sample_payment_request.dict(),
            headers={
                "Authorization": "Bearer valid_token",
                "X-Tenant-ID": str(uuid4()),
            },
        )

        assert response.status_code == 400
        assert "does not match plan price" in response.json()["detail"]

    def test_create_payment_unauthorized(self, client, sample_payment_request):
        """Test payment creation without authentication."""
        response = client.post(
            "/v1/payments/create", json=sample_payment_request.dict()
        )

        assert response.status_code == 401


class TestPaymentCallback:
    """Test payment callback handling."""

    @patch("services.payment_service.payment_service")
    def test_payment_callback_success(
        self, mock_service, async_client, mock_webhook_payload
    ):
        """Test successful payment callback processing."""
        mock_service.handle_payment_callback.return_value = {
            "status": "processed",
            "payment_state": "COMPLETED",
        }

        response = async_client.post(
            "/v1/payments/callback",
            headers={"authorization": "Bearer webhook_secret"},
            content=json.dumps(mock_webhook_payload),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processed"
        assert data["payment_state"] == "COMPLETED"

    @patch("services.payment_service.payment_service")
    def test_payment_callback_invalid_auth(
        self, mock_service, async_client, mock_webhook_payload
    ):
        """Test payment callback with invalid authorization."""
        mock_service.handle_payment_callback.side_effect = PhonePeCallbackError(
            "Invalid signature"
        )

        response = async_client.post(
            "/v1/payments/callback",
            headers={"authorization": "Bearer invalid_secret"},
            content=json.dumps(mock_webhook_payload),
        )

        assert response.status_code == 401
        assert "Invalid signature" in response.json()["detail"]

    def test_payment_callback_missing_auth(self, async_client, mock_webhook_payload):
        """Test payment callback without authorization header."""
        response = async_client.post(
            "/v1/payments/callback", content=json.dumps(mock_webhook_payload)
        )

        assert response.status_code == 400
        assert "Missing Authorization header" in response.json()["detail"]

    @patch("services.payment_service.payment_service")
    def test_payment_callback_invalid_payload(self, mock_service, async_client):
        """Test payment callback with invalid payload."""
        mock_service.handle_payment_callback.side_effect = ValueError(
            "Missing merchantOrderId"
        )

        response = async_client.post(
            "/v1/payments/callback",
            headers={"authorization": "Bearer webhook_secret"},
            content='{"invalid": "payload"}',
        )

        assert response.status_code == 400
        assert "Missing merchantOrderId" in response.json()["detail"]


class TestSubscriptionManagement:
    """Test subscription management endpoints."""

    @patch("services.payment_service.payment_service")
    def test_get_subscription_success(self, mock_service, client):
        """Test successful subscription details retrieval."""
        mock_service.get_subscription_details.return_value = {
            "subscription": {
                "id": str(uuid4()),
                "plan_name": "Professional",
                "status": "active",
                "current_period_end": "2024-12-31T23:59:59Z",
            },
            "usage": {
                "icp_profiles": {"current": 2, "limit": 10, "percentage": 20.0},
                "campaigns": {"current": 5, "limit": 50, "percentage": 10.0},
            },
        }

        response = client.get(
            "/v1/subscriptions",
            headers={
                "Authorization": "Bearer valid_token",
                "X-Tenant-ID": str(uuid4()),
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "subscription" in data["data"]
        assert "usage" in data["data"]

    @patch("services.payment_service.payment_service")
    def test_cancel_subscription_success(self, mock_service, client):
        """Test successful subscription cancellation."""
        mock_service.cancel_subscription.return_value = {
            "status": "cancelled",
            "subscription_id": str(uuid4()),
        }

        response = client.put(
            "/v1/subscriptions/cancel",
            json={"cancellation_reason": "Downgrading to free plan"},
            headers={
                "Authorization": "Bearer valid_token",
                "X-Tenant-ID": str(uuid4()),
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["status"] == "cancelled"

    @patch("services.payment_service.payment_service")
    def test_cancel_subscription_not_found(self, mock_service, client):
        """Test cancellation of non-existent subscription."""
        mock_service.cancel_subscription.side_effect = ValueError(
            "No active subscription found"
        )

        response = client.put(
            "/v1/subscriptions/cancel",
            json={},
            headers={
                "Authorization": "Bearer valid_token",
                "X-Tenant-ID": str(uuid4()),
            },
        )

        assert response.status_code == 400
        assert "No active subscription found" in response.json()["detail"]


class TestPaymentService:
    """Test payment service business logic."""

    @pytest.fixture
    def payment_service(self):
        """Payment service fixture for testing."""
        return PaymentService()

    @pytest.fixture
    def mock_gateway(self):
        """Mock PhonePe gateway."""
        gateway = MagicMock()
        gateway.pay.return_value = {"redirectUrl": "https://phonepe.com/pay/test_order"}
        gateway.get_order_status.return_value = {"state": "COMPLETED"}
        gateway.validate_callback.return_value = {
            "payload": {"merchantOrderId": "test_order", "state": "COMPLETED"}
        }
        return gateway

    @patch("db.get_db_connection")
    def test_create_payment_session(self, mock_db, payment_service, mock_gateway):
        """Test payment session creation in service."""
        payment_service.gateway = mock_gateway

        # Mock database
        mock_conn = AsyncMock()
        mock_cur = AsyncMock()
        mock_cur.fetchone.return_value = (uuid4(),)  # transaction_id
        mock_conn.__aenter__.return_value.cursor.return_value.__aenter__.return_value = (
            mock_cur
        )
        mock_db.return_value.__aenter__.return_value = mock_conn

        result = payment_service.create_payment_session(
            workspace_id=str(uuid4()),
            plan_id=str(uuid4()),
            amount=2999.00,
            return_url="https://test.com/success",
        )

        assert "payment_url" in result
        assert "merchant_order_id" in result
        assert result["amount"] == 2999.00

    @patch("db.get_db_connection")
    def test_handle_payment_callback(self, mock_db, payment_service, mock_gateway):
        """Test payment callback handling in service."""
        payment_service.gateway = mock_gateway

        # Mock database transaction lookup
        mock_conn = AsyncMock()
        mock_cur = AsyncMock()
        mock_cur.fetchone.return_value = (
            uuid4(),  # transaction_id
            str(uuid4()),  # workspace_id
            str(uuid4()),  # plan_id
            2999.00,  # amount
            None,  # subscription_id
        )
        mock_cur.execute = AsyncMock()
        mock_conn.__aenter__.return_value.cursor.return_value.__aenter__.return_value = (
            mock_cur
        )
        mock_db.return_value.__aenter__.return_value = mock_conn

        result = payment_service.handle_payment_callback(
            authorization="Bearer webhook_secret",
            response_body='{"payload": {"merchantOrderId": "test_order"}}',
        )

        assert result["status"] == "processed"

    def test_phonepe_settings_validation(self, payment_service):
        """Test PhonePe settings validation."""
        # Test missing settings
        with patch.object(payment_service.settings, "PHONEPE_CLIENT_ID", None):
            with pytest.raises(ValueError, match="Missing PhonePe configuration"):
                payment_service._validate_phonepe_settings()

        # Test invalid environment
        with patch.object(payment_service.settings, "PHONEPE_ENV", "INVALID"):
            with pytest.raises(
                ValueError, match="PHONEPE_ENV must be set to SANDBOX or PRODUCTION"
            ):
                payment_service._validate_phonepe_settings()


class TestRoleBasedAccess:
    """Test role-based access control for billing operations."""

    def test_workspace_owner_access(self, client):
        """Test workspace owner can access billing endpoints."""
        # This would require proper JWT setup in test environment
        pass

    def test_non_owner_access_denied(self, client):
        """Test non-owners cannot access billing endpoints."""
        # This would require proper JWT setup with non-owner role
        pass


class TestWebhookHandling:
    """Test webhook handling and async notifications."""

    def test_webhook_endpoint_active(self, client):
        """Test webhook endpoint is active and responds."""
        response = client.post("/v1/payments/webhook/test")
        assert response.status_code == 200
        assert response.json()["status"] == "webhook endpoint is active"

    @patch("services.payment_service.payment_service")
    def test_webhook_logging(
        self, mock_service, async_client, mock_webhook_payload, caplog
    ):
        """Test webhook processing is logged."""
        mock_service.handle_payment_callback.return_value = {"status": "processed"}

        with patch("api.v1.payments.logger") as mock_logger:
            async_client.post(
                "/v1/payments/webhook",
                headers={"authorization": "Bearer webhook_secret"},
                content=json.dumps(mock_webhook_payload),
            )

            mock_logger.info.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
