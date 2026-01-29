"""Tests for payment service."""

import json
from datetime import datetime, timezone
from unittest.mock import MagicMock, Mock, patch

import pytest
from services.payment_service import (
    PaymentError,
    PaymentRequest,
    PaymentResponse,
    PaymentService,
    payment_service,
)


class TestPaymentService:
    """Test cases for PaymentService."""

    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client."""
        mock_client = Mock()
        mock_client.table.return_value.insert.return_value.select.return_value.single.return_value.execute.return_value.data = {
            "id": "test-transaction-id",
            "workspace_id": "test-workspace-id",
            "merchant_order_id": "ORD20240128123456ABCDEF",
            "amount": 4900,
            "status": "pending",
        }
        return mock_client

    @pytest.fixture
    def payment_service_instance(self, mock_supabase):
        """Create PaymentService instance with mocked dependencies."""
        with patch(
            "services.payment_service.get_supabase_admin", return_value=mock_supabase
        ):
            # Mock environment variables
            with patch.dict(
                "os.environ",
                {
                    "PHONEPE_MERCHANT_ID": "test-merchant-id",
                    "PHONEPE_SALT_KEY": "test-salt-key",
                    "PHONEPE_SALT_INDEX": "1",
                    "PHONEPE_ENVIRONMENT": "sandbox",
                },
            ):
                return PaymentService()

    def test_init_missing_credentials(self):
        """Test PaymentService initialization with missing credentials."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(PaymentError) as exc_info:
                PaymentService()

            assert exc_info.value.error_type == "MISSING_CREDENTIALS"

    def test_get_payment_plans(self, payment_service_instance):
        """Test getting payment plans."""
        plans = payment_service_instance.get_payment_plans()

        assert len(plans) == 3
        plan_names = [plan["name"] for plan in plans]
        assert "starter" in plan_names
        assert "growth" in plan_names
        assert "enterprise" in plan_names

        # Check plan structure
        starter_plan = next(p for p in plans if p["name"] == "starter")
        assert starter_plan["amount"] == 4900  # ₹49
        assert starter_plan["currency"] == "INR"
        assert starter_plan["trial_days"] == 7

    @patch("httpx.Client")
    def test_initiate_payment_success(self, mock_httpx, payment_service_instance):
        """Test successful payment initiation."""
        # Mock PhonePe API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "instrumentResponse": {
                    "redirectInfo": {
                        "url": "https://api.phonepe.com/apis/pg-sandbox/checkout"
                    }
                },
                "merchantTransactionId": "TXN123456789",
            },
        }
        mock_httpx.return_value.__enter__.return_value.post.return_value = mock_response

        # Create payment request
        request = PaymentRequest(
            workspace_id="test-workspace-id",
            plan="starter",
            amount=4900,
            customer_email="test@example.com",
            customer_name="Test User",
        )

        # Test payment initiation
        result = payment_service_instance.initiate_payment(request)

        assert result.success is True
        assert result.payment_url is not None
        assert result.phonepe_transaction_id == "TXN123456789"
        assert result.status == "pending"

    @patch("httpx.Client")
    def test_initiate_payment_phonepe_failure(
        self, mock_httpx, payment_service_instance
    ):
        """Test payment initiation when PhonePe API fails."""
        # Mock PhonePe API failure response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "success": False,
            "message": "Invalid request",
        }
        mock_httpx.return_value.__enter__.return_value.post.return_value = mock_response

        request = PaymentRequest(
            workspace_id="test-workspace-id",
            plan="starter",
            amount=4900,
            customer_email="test@example.com",
        )

        result = payment_service_instance.initiate_payment(request)

        assert result.success is False
        assert result.error == "Invalid request"

    def test_initiate_payment_invalid_plan(self, payment_service_instance):
        """Test payment initiation with invalid plan."""
        request = PaymentRequest(
            workspace_id="test-workspace-id",
            plan="invalid-plan",
            amount=4900,
            customer_email="test@example.com",
        )

        with pytest.raises(PaymentError) as exc_info:
            payment_service_instance.initiate_payment(request)

        assert exc_info.value.error_type == "INVALID_PLAN"

    def test_initiate_payment_amount_mismatch(self, payment_service_instance):
        """Test payment initiation with amount mismatch."""
        request = PaymentRequest(
            workspace_id="test-workspace-id",
            plan="starter",  # Starter plan is ₹49 (4900 paise)
            amount=9900,  # But trying to pay ₹99
            customer_email="test@example.com",
        )

        with pytest.raises(PaymentError) as exc_info:
            payment_service_instance.initiate_payment(request)

        assert exc_info.value.error_type == "AMOUNT_MISMATCH"

    @patch("httpx.Client")
    def test_check_payment_status_completed(self, mock_httpx, payment_service_instance):
        """Test checking payment status when completed."""
        # Mock PhonePe API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {"state": "COMPLETED", "transactionId": "TXN123456789"},
        }
        mock_httpx.return_value.__enter__.return_value.get.return_value = mock_response

        # Mock database transaction
        with patch.object(payment_service_instance, "_get_transaction") as mock_get_tx:
            mock_get_tx.return_value = {
                "id": "test-transaction-id",
                "workspace_id": "test-workspace-id",
                "status": "pending",
            }

            # Mock subscription activation
            with patch.object(
                payment_service_instance, "_activate_subscription"
            ) as mock_activate:
                mock_activate.return_value = True

                result = payment_service_instance.check_payment_status(
                    "ORD20240128123456ABCDEF"
                )

                assert result.success is True
                assert result.status == "completed"
                assert result.phonepe_transaction_id == "TXN123456789"
                mock_activate.assert_called_once_with("test-workspace-id", "starter")

    @patch("httpx.Client")
    def test_check_payment_status_failed(self, mock_httpx, payment_service_instance):
        """Test checking payment status when failed."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {"state": "FAILED", "transactionId": "TXN123456789"},
        }
        mock_httpx.return_value.__enter__.return_value.get.return_value = mock_response

        with patch.object(payment_service_instance, "_get_transaction") as mock_get_tx:
            mock_get_tx.return_value = {
                "id": "test-transaction-id",
                "workspace_id": "test-workspace-id",
                "status": "pending",
            }

            result = payment_service_instance.check_payment_status(
                "ORD20240128123456ABCDEF"
            )

            assert result.success is True
            assert result.status == "failed"

    def test_validate_webhook_success(self, payment_service_instance):
        """Test successful webhook validation."""
        # Generate valid signature
        body = '{"test": "data"}'
        salt_key = "test-salt-key"
        expected_signature = (
            payment_service_instance._generate_sha256_checksum(f"{body}{salt_key}")
            + "###1"
        )

        result = payment_service_instance.validate_webhook(
            f"X-VERIFY {expected_signature}", body
        )

        assert result["valid"] is True
        assert result["data"] == {"test": "data"}

    def test_validate_webhook_invalid_signature(self, payment_service_instance):
        """Test webhook validation with invalid signature."""
        body = '{"test": "data"}'
        invalid_signature = "invalid-signature###1"

        with pytest.raises(PaymentError) as exc_info:
            payment_service_instance.validate_webhook(
                f"X-VERIFY {invalid_signature}", body
            )

        assert exc_info.value.error_type == "WEBHOOK_SIGNATURE_MISMATCH"

    def test_validate_webhook_invalid_format(self, payment_service_instance):
        """Test webhook validation with invalid header format."""
        with pytest.raises(PaymentError) as exc_info:
            payment_service_instance.validate_webhook(
                "invalid-header", '{"test": "data"}'
            )

        assert exc_info.value.error_type == "INVALID_WEBHOOK_HEADER"

    def test_process_webhook_callback_success(self, payment_service_instance):
        """Test processing successful webhook callback."""
        webhook_data = {
            "merchantTransactionId": "ORD20240128123456ABCDEF",
            "code": "PAYMENT_SUCCESS",
            "data": {"state": "COMPLETED", "transactionId": "TXN123456789"},
        }

        with patch.object(
            payment_service_instance, "_process_payment_success"
        ) as mock_process:
            mock_process.return_value = True

            result = payment_service_instance.process_webhook_callback(webhook_data)

            assert result is True
            mock_process.assert_called_once()

    def test_process_webhook_callback_failure(self, payment_service_instance):
        """Test processing failed webhook callback."""
        webhook_data = {
            "merchantTransactionId": "ORD20240128123456ABCDEF",
            "code": "PAYMENT_ERROR",
            "data": {"state": "FAILED"},
        }

        with patch.object(
            payment_service_instance, "_process_payment_failure"
        ) as mock_process:
            mock_process.return_value = True

            result = payment_service_instance.process_webhook_callback(webhook_data)

            assert result is True
            mock_process.assert_called_once()

    def test_encode_base64(self, payment_service_instance):
        """Test base64 encoding."""
        data = "test string"
        result = payment_service_instance._encode_base64(data)

        import base64

        expected = base64.b64encode(data.encode()).decode()
        assert result == expected

    def test_generate_sha256_checksum(self, payment_service_instance):
        """Test SHA256 checksum generation."""
        data = "test string"
        result = payment_service_instance._generate_sha256_checksum(data)

        import hashlib

        expected = hashlib.sha256(data.encode()).hexdigest()
        assert result == expected

    @patch("services.email_service.email_service")
    def test_activate_subscription(self, mock_email_service, payment_service_instance):
        """Test subscription activation."""
        with patch.object(payment_service_instance.supabase, "rpc") as mock_rpc:
            mock_rpc.return_value.execute.return_value.data = "subscription-id"

            result = payment_service_instance._activate_subscription(
                "workspace-id", "starter"
            )

            assert result is True
            mock_rpc.assert_called_once_with(
                "upsert_subscription",
                {
                    "workspace_id": "workspace-id",
                    "plan": "starter",
                    "status": "active",
                    "current_period_start": mock_rpc.call_args[0][1][
                        "current_period_start"
                    ],
                    "current_period_end": mock_rpc.call_args[0][1][
                        "current_period_end"
                    ],
                },
            )


class TestPaymentServiceIntegration:
    """Integration tests for payment service."""

    def test_singleton_instance(self):
        """Test that payment_service is a singleton."""
        from services.payment_service import payment_service as service1
        from services.payment_service import payment_service as service2

        assert service1 is service2

    def test_plan_configuration(self):
        """Test plan configuration consistency."""
        plans = payment_service.get_payment_plans()

        # Verify all plans have required fields
        for plan in plans:
            assert "name" in plan
            assert "amount" in plan
            assert "currency" in plan
            assert "interval" in plan
            assert "trial_days" in plan
            assert "display_amount" in plan

            # Verify amounts are positive
            assert plan["amount"] > 0

            # Verify currency is INR
            assert plan["currency"] == "INR"

            # Verify trial days are reasonable
            assert 0 <= plan["trial_days"] <= 30

    def test_error_handling(self):
        """Test error handling patterns."""
        # Test that all errors are PaymentError instances
        try:
            payment_service.validate_webhook("invalid", "{}")
        except PaymentError as e:
            assert e.error_type is not None
            assert isinstance(e.context, dict)
        except Exception:
            pytest.fail("Expected PaymentError")
