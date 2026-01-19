import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio
import os
import sys

# Mock modules before any backend imports
sys.modules['redis'] = MagicMock()
sys.modules['backend.services.upstash_client'] = MagicMock()

# Mock dependencies before importing anything from backend
with patch.dict(os.environ, {
    "PHONEPE_CLIENT_ID": "TEST_ID",
    "PHONEPE_SALT_KEY": "TEST_KEY",
    "PHONEPE_ENV": "UAT",
    "SECRET_KEY": "test_secret",
    "DATABASE_URL": "postgresql://test:test@localhost:5432/test",
    "GCP_PROJECT_ID": "test-project",
    "WEBHOOK_SECRET": "test_webhook_secret"
}):
    # Mock the settings object entirely to avoid Pydantic validation
    mock_settings = MagicMock()
    # Mock audit_logger with async methods
    mock_audit_logger = MagicMock()
    mock_audit_logger.log_event = AsyncMock()
    mock_audit_logger.log_security_violation = AsyncMock()
    
    with patch('backend.config.get_settings', return_value=mock_settings), \
         patch('backend.core.audit_logger.audit_logger', mock_audit_logger), \
         patch('backend.core.idempotency_manager.idempotency_manager'), \
         patch('backend.core.circuit_breaker.circuit_breaker_protected', lambda **kwargs: lambda f: f):
        from backend.services.phonepe_sdk_gateway import PhonePeSDKGateway, PaymentRequest

class TestPhonePeSDKGateway(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        with patch.dict(os.environ, {
            "PHONEPE_CLIENT_ID": "TEST_ID",
            "PHONEPE_SALT_KEY": "TEST_KEY",
            "PHONEPE_ENV": "UAT"
        }):
            self.gateway = PhonePeSDKGateway()

    @patch('phonepe.sdk.pg.payments.v2.standard_checkout_client.StandardCheckoutClient')
    async def test_initiate_payment_success(self, MockClient):
        # Setup mock client and response
        mock_client_instance = MockClient.return_value
        mock_response = MagicMock()
        mock_response.code = "PAYMENT_INITIATED"
        mock_response.data.instrument_response.redirect_info.url = "https://checkout.phonepe.com/test"
        mock_response.data.merchant_transaction_id = "MT123"
        
        mock_client_instance.pay.return_value = mock_response
        
        # Test request
        request = PaymentRequest(
            amount=1000,
            merchant_order_id="MT123",
            redirect_url="https://app.com/status",
            callback_url="https://app.com/api/webhook"
        )
        
        # We need to bypass the _get_client singleton check or ensure it returns our mock
        with patch.object(self.gateway, '_get_client', return_value=mock_client_instance):
            response = await self.gateway.initiate_payment(request)
            
        self.assertTrue(response.success)
        self.assertEqual(response.checkout_url, "https://checkout.phonepe.com/test")
        self.assertEqual(response.status, "PAYMENT_INITIATED")

    @patch('phonepe.sdk.pg.payments.v2.standard_checkout_client.StandardCheckoutClient')
    async def test_check_status_success(self, MockClient):
        mock_client_instance = MockClient.return_value
        mock_response = MagicMock()
        mock_response.code = "SUCCESS"
        mock_response.data.transaction_id = "T12345"
        
        mock_client_instance.get_order_status.return_value = mock_response
        
        with patch.object(self.gateway, '_get_client', return_value=mock_client_instance):
            response = await self.gateway.check_payment_status("MT123")
            
        self.assertTrue(response.success)
        self.assertEqual(response.status, "SUCCESS")
        self.assertEqual(response.phonepe_transaction_id, "T12345")

    @patch('phonepe.sdk.pg.payments.v2.standard_checkout_client.StandardCheckoutClient')
    async def test_validate_webhook_success(self, MockClient):
        mock_client_instance = MockClient.return_value
        mock_callback_response = MagicMock()
        mock_callback_response.merchant_transaction_id = "MT123"
        mock_callback_response.code = "PAYMENT_SUCCESS"
        
        mock_client_instance.validate_callback.return_value = mock_callback_response
        
        with patch.object(self.gateway, '_get_client', return_value=mock_client_instance):
            response = await self.gateway.validate_webhook("header", "body")
            
        self.assertTrue(response['success'])
        self.assertTrue(response['valid'])
        self.assertEqual(response['callback'].code, "PAYMENT_SUCCESS")

if __name__ == "__main__":
    unittest.main()
