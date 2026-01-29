"""Tests for PhonePe Official Gateway."""

import json
import time
from datetime import datetime, timezone
from unittest.mock import MagicMock, Mock, patch

import pytest
from services.phonepe_official_gateway import (
    PaymentError,
    PaymentRequest,
    PaymentResponse,
    PaymentStatus,
    PhonePeOfficialGateway,
    phonepe_gateway,
)


class TestPhonePeOfficialGateway:
    """Test cases for PhonePeOfficialGateway."""

    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client."""
        mock_client = Mock()
        mock_client.table.return_value.insert.return_value.select.return_value.single.return_value.execute.return_value.data = {
            "id": "test-transaction-id",
            "workspace_id": "test-workspace-id",
            "merchant_order_id": "ORD20240128123456ABCDEF",
            "amount": 4900,
            "status": "pending"
        }
        return mock_client

    @pytest.fixture
    def mock_phonepe_sdk(self):
        """Mock PhonePe SDK."""
        mock_sdk = Mock()
        return mock_sdk

    @pytest.fixture
    def gateway_instance(self, mock_supabase, mock_phonepe_sdk):
        """Create PhonePe gateway instance with mocked dependencies."""
        with patch('services.phonepe_official_gateway.get_supabase_admin', return_value=mock_supabase):
            with patch('services.phonepe_official_gateway.PhonePePayments', return_value=mock_phonepe_sdk):
                # Mock environment variables
                with patch.dict('os.environ', {
                    'PHONEPE_MERCHANT_ID': 'test-merchant-id',
                    'PHONEPE_SALT_KEY': 'test-salt-key',
                    'PHONEPE_SALT_INDEX': '1',
                    'PHONEPE_ENVIRONMENT': 'sandbox'
                }):
                    return PhonePeOfficialGateway()

    def test_init_missing_credentials(self):
        """Test gateway initialization with missing credentials."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(PaymentError) as exc_info:
                PhonePeOfficialGateway()

            assert exc_info.value.error_type == "MISSING_CREDENTIALS"

    def test_init_success(self):
        """Test successful gateway initialization."""
        with patch.dict('os.environ', {
            'PHONEPE_MERCHANT_ID': 'test-merchant-id',
            'PHONEPE_SALT_KEY': 'test-salt-key',
            'PHONEPE_SALT_INDEX': '1',
            'PHONEPE_ENVIRONMENT': 'sandbox'
        }):
            with patch('services.phonepe_official_gateway.get_supabase_admin'):
                with patch('services.phonepe_official_gateway.PhonePePayments'):
                    gateway = PhonePeOfficialGateway()
                    assert gateway.merchant_id == 'test-merchant-id'
                    assert gateway.salt_key == 'test-salt-key'
                    assert gateway.salt_index == '1'
                    assert gateway.environment == 'sandbox'

    def test_get_payment_plans(self, gateway_instance):
        """Test getting payment plans."""
        plans = gateway_instance.get_payment_plans()

        assert len(plans) == 3
        plan_names = [plan['name'] for plan in plans]
        assert 'starter' in plan_names
        assert 'growth' in plan_names
        assert 'enterprise' in plan_names

        # Check plan structure
        starter_plan = next(p for p in plans if p['name'] == 'starter')
        assert starter_plan['amount'] == 4900  # ₹49
        assert starter_plan['currency'] == 'INR'
        assert starter_plan['interval'] == 'month'
        assert starter_plan['trial_days'] == 14

    def test_validate_payment_request_success(self, gateway_instance):
        """Test successful payment request validation."""
        request = PaymentRequest(
            workspace_id="test-workspace-id",
            plan="starter",
            amount=4900,
            customer_email="test@example.com",
            customer_name="Test User"
        )

        # Should not raise any exception
        gateway_instance._validate_payment_request(request)

    def test_validate_payment_request_invalid_plan(self, gateway_instance):
        """Test payment request validation with invalid plan."""
        request = PaymentRequest(
            workspace_id="test-workspace-id",
            plan="invalid-plan",
            amount=4900,
            customer_email="test@example.com"
        )

        with pytest.raises(PaymentError) as exc_info:
            gateway_instance._validate_payment_request(request)

        assert exc_info.value.error_type == "INVALID_PLAN"

    def test_validate_payment_request_amount_mismatch(self, gateway_instance):
        """Test payment request validation with amount mismatch."""
        request = PaymentRequest(
            workspace_id="test-workspace-id",
            plan="starter",  # Starter plan is ₹49 (4900 paise)
            amount=9900,     # But trying to pay ₹99
            customer_email="test@example.com"
        )

        with pytest.raises(PaymentError) as exc_info:
            gateway_instance._validate_payment_request(request)

        assert exc_info.value.error_type == "AMOUNT_MISMATCH"

    def test_validate_payment_request_amount_too_low(self, gateway_instance):
        """Test payment request validation with amount too low."""
        request = PaymentRequest(
            workspace_id="test-workspace-id",
            plan="starter",
            amount=50,  # Less than ₹1 (100 paise)
            customer_email="test@example.com"
        )

        with pytest.raises(PaymentError) as exc_info:
            gateway_instance._validate_payment_request(request)

        assert exc_info.value.error_type == "AMOUNT_TOO_LOW"

    def test_validate_payment_request_amount_too_high(self, gateway_instance):
        """Test payment request validation with amount too high."""
        request = PaymentRequest(
            workspace_id="test-workspace-id",
            plan="starter",
            amount=10000001,  # More than ₹1,00,000
            customer_email="test@example.com"
        )

        with pytest.raises(PaymentError) as exc_info:
            gateway_instance._validate_payment_request(request)

        assert exc_info.value.error_type == "AMOUNT_TOO_HIGH"

    def test_generate_order_id(self, gateway_instance):
        """Test order ID generation."""
        order_id1 = gateway_instance._generate_order_id()
        order_id2 = gateway_instance._generate_order_id()

        # Should be different
        assert order_id1 != order_id2

        # Should start with "ORD"
        assert order_id1.startswith("ORD")
        assert order_id2.startswith("ORD")

        # Should be reasonable length
        assert len(order_id1) > 10
        assert len(order_id2) > 10

    def test_map_phonepe_status(self, gateway_instance):
        """Test PhonePe status mapping."""
        test_cases = [
            ("COMPLETED", "completed"),
            ("FAILED", "failed"),
            ("PENDING", "pending"),
            ("USER_NOT_LOGGED_IN", "failed"),
            ("AUTHORIZATION_FAILED", "failed"),
            ("TRANSACTION_NOT_FOUND", "pending"),
            ("UNKNOWN_STATUS", "pending")
        ]

        for phonepe_status, expected_status in test_cases:
            result = gateway_instance._map_phonepe_status(phonepe_status)
            assert result == expected_status

    @patch('services.phonepe_official_gateway.time.time')
    def test_initiate_payment_success(self, mock_time, gateway_instance):
        """Test successful payment initiation."""
        # Mock time for consistent order ID
        mock_time.return_value = 1640995200  # Fixed timestamp

        # Mock PhonePe SDK response
        mock_response = Mock()
        mock_response.success = True
        mock_response.data.merchantTransactionId = "TXN123456789"
        mock_response.data.instrumentResponse.redirectInfo.url = "https://api.phonepe.com/apis/pg-sandbox/checkout"

        gateway_instance.phonepe.pay.return_value = mock_response

        # Create payment request
        request = PaymentRequest(
            workspace_id="test-workspace-id",
            plan="starter",
            amount=4900,
            customer_email="test@example.com",
            customer_name="Test User"
        )

        # Test payment initiation
        result = gateway_instance.initiate_payment(request)

        assert result.success is True
        assert result.payment_url is not None
        assert result.phonepe_transaction_id == "TXN123456789"
        assert result.status == "pending"

    @patch('services.phonepe_official_gateway.time.time')
    def test_initiate_payment_phonepe_failure(self, mock_time, gateway_instance):
        """Test payment initiation when PhonePe SDK fails."""
        mock_time.return_value = 1640995200

        # Mock PhonePe SDK failure
        mock_response = Mock()
        mock_response.success = False
        mock_response.message = "Invalid request"

        gateway_instance.phonepe.pay.return_value = mock_response

        request = PaymentRequest(
            workspace_id="test-workspace-id",
            plan="starter",
            amount=4900,
            customer_email="test@example.com"
        )

        with pytest.raises(PaymentError) as exc_info:
            gateway_instance.initiate_payment(request)

        assert exc_info.value.error_type == "PHONEPE_API_ERROR"

    @patch('services.phonepe_official_gateway.time.time')
    def test_initiate_payment_sdk_exception(self, mock_time, gateway_instance):
        """Test payment initiation when SDK raises exception."""
        mock_time.return_value = 1640995200

        # Mock SDK exception
        gateway_instance.phonepe.pay.side_effect = Exception("SDK Error")

        request = PaymentRequest(
            workspace_id="test-workspace-id",
            plan="starter",
            amount=4900,
            customer_email="test@example.com"
        )

        with pytest.raises(PaymentError) as exc_info:
            gateway_instance.initiate_payment(request)

        assert exc_info.value.error_type == "PAYMENT_INITIATION_FAILED"

    def test_check_payment_status_completed(self, gateway_instance):
        """Test checking payment status when completed."""
        # Mock PhonePe SDK response
        mock_response = Mock()
        mock_response.success = True
        mock_response.data.state = "COMPLETED"
        mock_response.data.transactionId = "TXN123456789"
        mock_response.data.amount = 4900

        gateway_instance.phonepe.get_transaction_status.return_value = mock_response

        # Mock database transaction
        with patch.object(gateway_instance, '_get_transaction') as mock_get_tx:
            mock_get_tx.return_value = {
                "id": "test-transaction-id",
                "workspace_id": "test-workspace-id",
                "plan": "starter",
                "status": "pending"
            }

            # Mock subscription activation
            with patch.object(gateway_instance, '_activate_subscription') as mock_activate:
                with patch.object(gateway_instance, '_send_confirmation_email') as mock_email:
                    result = gateway_instance.check_payment_status("ORD20240128123456ABCDEF")

                    assert result.success is True
                    assert result.status == "completed"
                    assert result.phonepe_transaction_id == "TXN123456789"
                    assert result.amount == 4900
                    mock_activate.assert_called_once_with("test-workspace-id", "starter")
                    mock_email.assert_called_once()

    def test_check_payment_status_failed(self, gateway_instance):
        """Test checking payment status when failed."""
        mock_response = Mock()
        mock_response.success = True
        mock_response.data.state = "FAILED"
        mock_response.data.transactionId = "TXN123456789"
        mock_response.data.amount = 4900

        gateway_instance.phonepe.get_transaction_status.return_value = mock_response

        with patch.object(gateway_instance, '_get_transaction') as mock_get_tx:
            mock_get_tx.return_value = {
                "id": "test-transaction-id",
                "workspace_id": "test-workspace-id",
                "plan": "starter",
                "status": "pending"
            }

            result = gateway_instance.check_payment_status("ORD20240128123456ABCDEF")

            assert result.success is True
            assert result.status == "failed"
            assert result.phonepe_transaction_id == "TXN123456789"

    def test_check_payment_status_cached(self, gateway_instance):
        """Test checking payment status from cache."""
        with patch.object(gateway_instance, '_get_transaction') as mock_get_tx:
            mock_get_tx.return_value = {
                "id": "test-transaction-id",
                "workspace_id": "test-workspace-id",
                "status": "completed",  # Already completed
                "phonepe_transaction_id": "TXN123456789",
                "completed_at": datetime.now(timezone.utc).isoformat()
            }

            result = gateway_instance.check_payment_status("ORD20240128123456ABCDEF")

            assert result.success is True
            assert result.status == "completed"

            # SDK should not be called for cached status
            gateway_instance.phonepe.get_transaction_status.assert_not_called()

    def test_check_payment_status_transaction_not_found(self, gateway_instance):
        """Test checking payment status for non-existent transaction."""
        with patch.object(gateway_instance, '_get_transaction') as mock_get_tx:
            mock_get_tx.return_value = None  # Transaction not found

        with pytest.raises(PaymentError) as exc_info:
            gateway_instance.check_payment_status("NONEXISTENT")

        assert exc_info.value.error_type == "TRANSACTION_NOT_FOUND"

    def test_process_webhook_success(self, gateway_instance):
        """Test processing successful webhook."""
        webhook_data = {
            "merchantTransactionId": "ORD20240128123456ABCDEF",
            "code": "PAYMENT_SUCCESS",
            "data": {
                "state": "COMPLETED",
                "transactionId": "TXN123456789"
            }
        }

        with patch.object(gateway_instance, '_validate_webhook_signature') as mock_validate:
            mock_validate.return_value = True

            with patch.object(gateway_instance, '_is_webhook_processed') as mock_processed:
                mock_processed.return_value False

                with patch.object(gateway_instance, '_mark_webhook_processed') as mock_mark:
                    with patch.object(gateway_instance, '_activate_subscription') as mock_activate:
                        with patch.object(gateway_instance, '_send_confirmation_email') as mock_email:
                            # Mock database update
                            mock_supabase = Mock()
                            gateway_instance.supabase = mock_supabase

                            result = gateway_instance.process_webhook(webhook_data)

                            assert result is True
                            mock_validate.assert_called_once()
                            mock_activate.assert_called_once()
                            mock_email.assert_called_once()

    def test_process_webhook_failure(self, gateway_instance):
        """Test processing failed webhook."""
        webhook_data = {
            "merchantTransactionId": "ORD20240128123456ABCDEF",
            "code": "PAYMENT_FAILED",
            "data": {
                "state": "FAILED",
                "responseMessage": "Payment failed"
            }
        }

        with patch.object(gateway_instance, '_validate_webhook_signature') as mock_validate:
            mock_validate.return_value = True

            with patch.object(gateway_instance, '_is_webhook_processed') as mock_processed:
                mock_processed.return_value False

                with patch.object(gateway_instance, '_mark_webhook_processed') as mock_mark:
                    with patch.object(gateway_instance, '_send_failure_email') as mock_email:
                        # Mock database update
                        mock_supabase = Mock()
                        gateway_instance.supabase = mock_supabase

                        result = gateway_instance.process_webhook(webhook_data)

                        assert result is True
                        mock_validate.assert_called_once()
                        mock_email.assert_called_once()

    def test_process_webhook_invalid_signature(self, gateway_instance):
        """Test processing webhook with invalid signature."""
        webhook_data = {
            "merchantTransactionId": "ORD20240128123456ABCDEF",
            "code": "PAYMENT_SUCCESS"
        }

        with patch.object(gateway_instance, '_validate_webhook_signature') as mock_validate:
            mock_validate.side_effect = PaymentError("Invalid signature", "WEBHOOK_SIGNATURE_INVALID")

            with pytest.raises(PaymentError) as exc_info:
                gateway_instance.process_webhook(webhook_data)

            assert exc_info.value.error_type == "WEBHOOK_SIGNATURE_INVALID"

    def test_process_webhook_duplicate(self, gateway_instance):
        """Test processing duplicate webhook (replay attack)."""
        webhook_data = {
            "merchantTransactionId": "ORD20240128123456ABCDEF",
            "code": "PAYMENT_SUCCESS"
        }

        with patch.object(gateway_instance, '_validate_webhook_signature') as mock_validate:
            mock_validate.return_value = True

            with patch.object(gateway_instance, '_is_webhook_processed') as mock_processed:
                mock_processed.return_value True  # Already processed

                result = gateway_instance.process_webhook(webhook_data)

                # Should return success for idempotency
                assert result is True

    def test_activate_subscription(self, gateway_instance):
        """Test subscription activation."""
        mock_supabase = Mock()
        mock_supabase.rpc.return_value.execute.return_value.data = "subscription-id"
        gateway_instance.supabase = mock_supabase

        result = gateway_instance._activate_subscription("workspace-id", "starter")

        assert result is True
        mock_supabase.rpc.assert_called_once_with("upsert_subscription", {
            "workspace_id": "workspace-id",
            "plan": "starter",
            "status": "active",
            "current_period_start": mock_supabase.rpc.call_args[0][1]["current_period_start"],
            "current_period_end": mock_supabase.rpc.call_args[0][1]["current_period_end"]
        })

    def test_activate_subscription_failure(self, gateway_instance):
        """Test subscription activation failure."""
        mock_supabase = Mock()
        mock_supabase.rpc.return_value.execute.side_effect = Exception("Database error")
        gateway_instance.supabase = mock_supabase

        # Should not raise exception, but return False
        result = gateway_instance._activate_subscription("workspace-id", "starter")
        assert result is False

    def test_send_confirmation_email(self, gateway_instance):
        """Test sending confirmation email."""
        transaction = {
            "plan": "starter",
            "amount": 4900,
            "phonepe_transaction_id": "TXN123456789",
            "merchant_order_id": "ORD20240128123456ABCDEF",
            "workspace_id": "test-workspace-id",
            "customer_email": "test@example.com",
            "customer_name": "Test User"
        }

        mock_email_service = Mock()
        gateway_instance.email_service = mock_email_service

        gateway_instance._send_confirmation_email(transaction)

        mock_email_service.send_email.assert_called_once()

    def test_send_failure_email(self, gateway_instance):
        """Test sending failure email."""
        transaction = {
            "merchant_order_id": "ORD20240128123456ABCDEF",
            "workspace_id": "test-workspace-id",
            "customer_email": "test@example.com",
            "customer_name": "Test User",
            "error_message": "Payment failed"
        }

        mock_email_service = Mock()
        gateway_instance.email_service = mock_email_service

        gateway_instance._send_failure_email(transaction)

        mock_email_service.send_email.assert_called_once()

    def test_validate_webhook_signature_success(self, gateway_instance):
        """Test successful webhook signature validation."""
        # Mock webhook security manager
        mock_webhook_security = Mock()
        mock_webhook_security.validate_webhook.return_value = True
        gateway_instance.webhook_security = mock_webhook_security

        webhook_data = {"test": "data"}
        result = gateway_instance._validate_webhook_signature(webhook_data)

        assert result is True
        mock_webhook_security.validate_webhook.assert_called_once()

    def test_validate_webhook_signature_failure(self, gateway_instance):
        """Test webhook signature validation failure."""
        # Mock webhook security manager
        mock_webhook_security = Mock()
        mock_webhook_security.validate_webhook.side_effect = Exception("Invalid signature")
        gateway_instance.webhook_security = mock_webhook_security

        webhook_data = {"test": "data"}
        result = gateway_instance._validate_webhook_signature(webhook_data)

        assert result is False

    def test_idempotency_check(self, gateway_instance):
        """Test idempotency key checking."""
        # For now, this should return None (not implemented)
        result = gateway_instance._check_idempotency("test-key")
        assert result is None

    def test_store_idempotency_response(self, gateway_instance):
        """Test storing idempotency response."""
        response = PaymentResponse(
            success=True,
            merchant_order_id="ORD123",
            status="pending"
        )

        # Should not raise exception (even though not implemented)
        gateway_instance._store_idempotency_response("test-key", response)

    def test_webhook_replay_protection(self, gateway_instance):
        """Test webhook replay protection."""
        # For now, these should return default values (not implemented)
        assert gateway_instance._is_webhook_processed({"test": "data"}) is False
        gateway_instance._mark_webhook_processed({"test": "data"})  # Should not raise


class TestPhonePeGatewayIntegration:
    """Integration tests for PhonePe gateway."""

    def test_singleton_instance(self):
        """Test that phonepe_gateway is a singleton."""
        from services.phonepe_official_gateway import phonepe_gateway as gateway1
        from services.phonepe_official_gateway import phonepe_gateway as gateway2

        assert gateway1 is gateway2

    def test_plan_configuration_consistency(self):
        """Test plan configuration consistency across gateway."""
        plans = phonepe_gateway.get_payment_plans()

        # Verify all plans have required fields
        for plan in plans:
            assert 'name' in plan
            assert 'display_name' in plan
            assert 'amount' in plan
            assert 'currency' in plan
            assert 'interval' in plan
            assert 'trial_days' in plan
            assert 'display_amount' in plan

            # Verify amounts are positive
            assert plan['amount'] > 0

            # Verify currency is INR
            assert plan['currency'] == 'INR'

            # Verify trial days are reasonable
            assert 0 <= plan['trial_days'] <= 30

    def test_error_handling_patterns(self):
        """Test error handling patterns."""
        # Test that all errors are PaymentError instances
        try:
            phonepe_gateway._validate_payment_request(PaymentRequest(
                workspace_id="test",
                plan="invalid",
                amount=100,
                customer_email="test@example.com"
            ))
        except PaymentError as e:
            assert e.error_type is not None
            assert hasattr(e, 'context')
        except Exception:
            pytest.fail("Expected PaymentError")

    @patch.dict('os.environ', {
        'PHONEPE_MERCHANT_ID': 'test-merchant-id',
        'PHONEPE_SALT_KEY': 'test-salt-key',
        'PHONEPE_SALT_INDEX': '1',
        'PHONEPE_ENVIRONMENT': 'sandbox'
    })
    def test_environment_configuration(self):
        """Test environment configuration."""
        with patch('services.phonepe_official_gateway.get_supabase_admin'):
            with patch('services.phonepe_official_gateway.PhonePePayments'):
                gateway = PhonePeOfficialGateway()

                assert gateway.merchant_id == 'test-merchant-id'
                assert gateway.salt_key == 'test-salt-key'
                assert gateway.environment == 'sandbox'
