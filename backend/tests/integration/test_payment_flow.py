"""Integration tests for complete payment flow"""

import json
import os

# Import payment service components
import sys
from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from services.payment_service import PaymentError, PaymentRequest, PaymentService


class TestPaymentFlowIntegration:
    """Integration tests for complete payment flow"""

    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client"""
        mock_client = Mock()

        # Mock transaction insertion
        mock_client.table.return_value.insert.return_value.select.return_value.single.return_value.execute.return_value.data = {
            "id": "test-transaction-id",
            "workspace_id": "test-workspace-id",
            "merchant_order_id": "ORD20240128123456ABCDEF",
            "amount": 4900,
            "status": "pending",
        }

        # Mock subscription creation
        mock_client.rpc.return_value.execute.return_value.data = "subscription-id"

        return mock_client

    @pytest.fixture
    def payment_service_instance(self, mock_supabase):
        """Create PaymentService instance with mocked dependencies"""
        with patch(
            "services.payment_service.get_supabase_admin", return_value=mock_supabase
        ):
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

    @pytest.mark.asyncio
    async def test_complete_payment_flow_success(self, payment_service_instance):
        """Test complete payment flow from initiation to activation"""

        # Mock PhonePe API responses
        with patch("httpx.Client") as mock_httpx:
            # Mock payment initiation
            mock_initiate_response = Mock()
            mock_initiate_response.status_code = 200
            mock_initiate_response.json.return_value = {
                "success": True,
                "data": {
                    "instrumentResponse": {
                        "redirectInfo": {"url": "https://api.phonepe.com/checkout"}
                    },
                    "merchantTransactionId": "TXN123456789",
                },
            }

            # Mock status check
            mock_status_response = Mock()
            mock_status_response.status_code = 200
            mock_status_response.json.return_value = {
                "success": True,
                "data": {"state": "COMPLETED", "transactionId": "TXN123456789"},
            }

            mock_httpx.return_value.__enter__.return_value.post.return_value = (
                mock_initiate_response
            )
            mock_httpx.return_value.__enter__.return_value.get.return_value = (
                mock_status_response
            )

            # Step 1: Initiate payment
            request = PaymentRequest(
                workspace_id="test-workspace-id",
                plan="starter",
                amount=4900,
                customer_email="test@example.com",
                customer_name="Test User",
            )

            result = payment_service_instance.initiate_payment(request)

            assert result.success is True
            assert result.payment_url == "https://api.phonepe.com/checkout"
            assert result.phonepe_transaction_id == "TXN123456789"
            assert result.status == "pending"

            # Step 2: Check payment status
            status_result = payment_service_instance.check_payment_status(
                result.merchant_order_id
            )

            assert status_result.success is True
            assert status_result.status == "completed"
            assert status_result.phonepe_transaction_id == "TXN123456789"

    @pytest.mark.asyncio
    async def test_payment_flow_with_webhook(self, payment_service_instance):
        """Test payment flow with webhook processing"""

        webhook_data = {
            "merchantTransactionId": "ORD20240128123456ABCDEF",
            "code": "PAYMENT_SUCCESS",
            "data": {
                "state": "COMPLETED",
                "transactionId": "TXN123456789",
                "amount": 4900,
            },
        }

        # Mock webhook validation
        with patch.object(
            payment_service_instance, "validate_webhook"
        ) as mock_validate:
            mock_validate.return_value = {"valid": True, "data": webhook_data}

        # Mock payment success processing
        with patch.object(
            payment_service_instance, "_process_payment_success"
        ) as mock_process:
            mock_process.return_value = True

        # Process webhook
        result = payment_service_instance.process_webhook_callback(webhook_data)

        assert result is True
        mock_validate.assert_called_once()
        mock_process.assert_called_once()

    @pytest.mark.asyncio
    async def test_payment_flow_failure_handling(self, payment_service_instance):
        """Test payment flow with failure scenarios"""

        # Mock PhonePe API failure
        with patch("httpx.Client") as mock_httpx:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.json.return_value = {
                "success": False,
                "message": "Payment failed",
            }
            mock_httpx.return_value.__enter__.return_value.post.return_value = (
                mock_response
            )

            request = PaymentRequest(
                workspace_id="test-workspace-id",
                plan="starter",
                amount=4900,
                customer_email="test@example.com",
            )

            result = payment_service_instance.initiate_payment(request)

            assert result.success is False
            assert result.error == "Payment failed"

    def test_webhook_signature_validation(self, payment_service_instance):
        """Test webhook signature validation"""

        # Test valid signature
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

    def test_webhook_signature_invalid(self, payment_service_instance):
        """Test webhook signature validation with invalid signature"""

        body = '{"test": "data"}'
        invalid_signature = "invalid-signature###1"

        with pytest.raises(PaymentError) as exc_info:
            payment_service_instance.validate_webhook(
                f"X-VERIFY {invalid_signature}", body
            )

        assert exc_info.value.error_type == "WEBHOOK_SIGNATURE_MISMATCH"

    def test_subscription_activation(self, payment_service_instance):
        """Test subscription activation"""

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

    def test_plan_validation(self, payment_service_instance):
        """Test plan validation"""

        # Test valid plans
        valid_plans = ["starter", "growth", "enterprise"]
        for plan in valid_plans:
            assert plan in payment_service_instance.PLANS

        # Test invalid plan
        request = PaymentRequest(
            workspace_id="test-workspace-id",
            plan="invalid-plan",
            amount=4900,
            customer_email="test@example.com",
        )

        with pytest.raises(PaymentError) as exc_info:
            payment_service_instance.initiate_payment(request)

        assert exc_info.value.error_type == "INVALID_PLAN"

    def test_amount_validation(self, payment_service_instance):
        """Test amount validation"""

        # Test amount mismatch
        request = PaymentRequest(
            workspace_id="test-workspace-id",
            plan="starter",  # Starter plan is ₹49 (4900 paise)
            amount=9900,  # But trying to pay ₹99
            customer_email="test@example.com",
        )

        with pytest.raises(PaymentError) as exc_info:
            payment_service_instance.initiate_payment(request)

        assert exc_info.value.error_type == "AMOUNT_MISMATCH"

    def test_payment_plans_structure(self, payment_service_instance):
        """Test payment plans structure and consistency"""

        plans = payment_service_instance.get_payment_plans()

        assert len(plans) == 3

        for plan in plans:
            # Check required fields
            assert "name" in plan
            assert "amount" in plan
            assert "currency" in plan
            assert "interval" in plan
            assert "trial_days" in plan
            assert "display_amount" in plan

            # Check constraints
            assert plan["amount"] > 0
            assert plan["currency"] == "INR"
            assert 0 <= plan["trial_days"] <= 30
            assert plan["interval"] == "month"

    def test_error_handling_patterns(self, payment_service_instance):
        """Test error handling patterns"""

        # Test PaymentError structure
        try:
            raise PaymentError("Test error", "TEST_ERROR", {"context": "test"})
        except PaymentError as e:
            assert e.error_type == "TEST_ERROR"
            assert e.context == {"context": "test"}
            assert str(e) == "Test error"

    def test_utility_functions(self, payment_service_instance):
        """Test utility functions"""

        # Test base64 encoding
        data = "test string"
        encoded = payment_service_instance._encode_base64(data)

        import base64

        expected = base64.b64encode(data.encode()).decode()
        assert encoded == expected

        # Test SHA256 checksum
        data = "test string"
        checksum = payment_service_instance._generate_sha256_checksum(data)

        import hashlib

        expected = hashlib.sha256(data.encode()).hexdigest()
        assert checksum == expected


if __name__ == "__main__":
    pytest.main([__file__])
