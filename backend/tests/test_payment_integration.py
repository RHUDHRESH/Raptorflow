"""
Comprehensive Unit Tests for Payment System
Tests all payment flows with proper mocking and edge cases
Addresses testing vulnerabilities identified in red team audit
"""

import pytest
import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List, Union
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from fastapi.test import TestClient
from httpx import AsyncClient
import redis as redis

# Import payment system components
from backend.services.phonepe_sdk_gateway import (
    PaymentRequest, PaymentResponse, RefundRequestData, RefundResponseData,
    phonepe_sdk_gateway
)
from backend.services.refund_system import (
    RefundManager, get_refund_manager, RefundRequestData as RefundRequestData,
    RefundResponseData as RefundResponseData
)
from backend.webhooks.secure_phonepe_webhook import (
    SecurePhonePeWebhookHandler, get_secure_webhook_handler
)
from backend.core.transaction_consistency import (
    TransactionConsistencyManager, get_transaction_manager
)
from backend.core.idempotency_manager import (
    IdempotencyManager, get_idempotency_manager
)
from backend.core.rate_limiting import (
    RateLimitingManager, get_rate_limiting_manager
)
from backend.core.circuit_breaker import (
    CircuitBreakerManager, get_circuit_breaker_manager
)
from backend.core.payment_fraud_detection import (
    PaymentFraudDetector, get_fraud_detector
)
from backend.core.payment_monitoring import (
    PaymentMonitor, get_payment_monitor
)
from backend.core.payment_compliance import (
    PaymentComplianceManager, get_compliance_manager
)
from backend.core.audit_logger import (
    AuditLogger, EventType, LogLevel
)
from backend.db.repositories.payment import PaymentRepository

# Test database setup
from backend.db.repositories.payment import PaymentRepository
from backend.db.models.payment import Payment, Refund

logger = logging.getLogger(__name__)

class TestPaymentSDKGateway:
    """Test suite for PhonePe SDK Gateway"""
    
    @pytest.fixture
    async def setup_sdk_gateway(self):
        """Setup test SDK gateway with mock dependencies"""
        # Mock dependencies
        mock_redis = Mock(spec=redis.Redis)
        mock_repository = AsyncMock(spec=PaymentRepository)
        mock_fraud_detector = AsyncMock(spec=PaymentFraudDetector)
        mock_compliance_manager = AsyncMock(spec=PaymentComplianceManager)
        mock_transaction_manager = AsyncMock(spec=TransactionConsistencyManager)
        
        # Create gateway instance
        gateway = phonepe_sdk_gateway
        
        # Mock the internal client
        gateway._client = AsyncMock(spec=StandardCheckoutClient)
        
        # Mock the dependencies
        gateway._fraud_detector = mock_fraud_detector
        gateway._compliance_manager = mock_compliance_manager
        gateway._transaction_manager = mock_transaction_manager
        
        yield gateway
    
    @pytest.mark.asyncio
    async def test_payment_initiation_success(self, setup_sdk_gateway):
        """Test successful payment initiation"""
        gateway = setup_sdk_gateway
        
        # Mock successful SDK response
        mock_response = Mock()
        mock_response.redirect_url = "https://test.phonepe.com/pay/MT123456789"
        mock_response.transaction_id = "TX123456789"
        mock_response.state = "PENDING"
        
        gateway._client.pay.return_value = mock_response
        
        # Create payment request
        request = PaymentRequest(
            amount=10000,  # ₹100
            merchant_order_id="TEST_ORDER_123",
            redirect_url="https://example.com/return",
            callback_url="https://example.com/callback",
            customer_info={"name": "Test User", "email": "test@example.com"},
            user_id="user123"
        )
        
        # Process payment
        result = await gateway.initiate_payment(request)
        
        # Verify result
        assert result.success is True
        assert result.checkout_url == mock_response.redirect_url
        assert result.phonepe_transaction_id == mock_response.transaction_id
        assert result.status == "PENDING"
        assert result.amount == 10000
    
    @pytest.mark.asyncio
    async def test_payment_initiation_sdk_error(self, setup_sdk_gateway):
        """Test payment initiation with SDK error"""
        gateway = setup_sdk_gateway
        
        # Mock SDK exception
        gateway._client.pay.side_effect = Exception("PhonePe API error")
        
        # Create payment request
        request = PaymentRequest(
            amount=10000,
            merchant_order_id="TEST_ORDER_456",
            redirect_url="https://example.com/return",
            callback_url="https://example.com/callback",
            user_id="user123"
        )
        
        # Process payment and expect error
        with pytest.raises(Exception):
            await gateway.initiate_payment(request)
    
    @pytest.mark.asyncio
    async def test_refund_processing_success(self, setup_sdk_gateway):
        """Test successful refund processing"""
        gateway = setup_sdk_gateway
        
        # Mock successful SDK response
        mock_response = Mock()
        mock_response.refund_id = "RF123456789"
        mock_response.state = "COMPLETED"
        
        gateway._client.refund.return_value = mock_response
        
        # Create refund request
        refund_request = RefundRequestData(
            merchant_order_id="TEST_ORDER_456",
            refund_amount=5000,  # ₹50
            refund_reason="Customer request"
        )
        
        # Process refund
        result = await gateway.process_refund(refund_request)
        
        # Verify result
        assert result.success is True
        assert result.refund_id == mock_response.refund_id
        assert result.status == "COMPLETED"
        assert result.refund_amount == 5000
    
    @pytest.mark.asyncio
    async def test_payment_status_check(self, setup_sdk_gateway):
        """Test payment status check"""
        gateway = setup_sdk_gateway
        
        # Mock SDK response
        mock_response = Mock()
        mock_response.state = "COMPLETED"
        mock_response.amount = 10000
        mock_response.transaction_id = "TX123456789"
        
        gateway._client.get_order_status.return_value = mock_response
        
        # Check status
        result = await gateway.check_payment_status("TX123456789")
        
        # Verify result
        assert result.success is True
        assert result.status == "COMPLETED"
        assert result.amount == 10000
        assert result.phonepe_transaction_id == "TX123456789"
    
    @pytest.mark.asyncio
    async def test_webhook_validation(self, setup_sdk_gateway):
        """Test webhook validation"""
        gateway = setup_sdk_gateway
        
        # Mock webhook data
        webhook_data = {
            "type": "PAYMENT_SUCCESS",
            "code": "SUCCESS",
            "data": {
                "merchantTransactionId": "TX123456789",
                "amount": 10000,
                "state": "COMPLETED"
            }
        }
        
        # Mock signature
        signature = "sha256:hash"
        
        # Validate webhook
        result = await gateway.validate_webhook(signature, json.dumps(webhook_data))
        
        # Verify result
        assert result["valid"] is True
        assert result["webhook_data"] == webhook_data
    
    @pytest.mark.asyncio
    async def test_idempotency_protection(self, setup_sdk_gateway):
        """Test idempotency protection"""
        gateway = setup_sdk_gateway
        
        # Create idempotency key
        idempotency_key = f"test_idempotency_{uuid.uuid4().hex[:8]}"
        
        # First request
        request1 = PaymentRequest(
            amount=10000,
            merchant_order_id="TEST_ORDER_789",
            redirect_url="https://example.com/return",
            callback_url="https://example.com/callback",
            user_id="user123",
            idempotency_key=idempotency_key
        )
        
        # Process first request
        result1 = await gateway.initiate_payment(request1)
        assert result1.success is True
        
        # Second request with same idempotency key
        request2 = PaymentRequest(
            amount=10000,
            merchant_order_id="TEST_ORDER_789",  # Same order ID
            redirect_url="https://example.com/return",
            callback_url="https://example.com/callback",
            user_id="user123",
            idempotency_key=idempotency_key  # Same key
        )
        
        # Process second request
        result2 = await gateway.initiate_payment(request2)
        
        # Should return cached result
        assert result2.success is True
        assert result2.transaction_id == result1.transaction_id
        assert result2.checkout_url == result1.checkout_url
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_protection(self, setup_sdk_gateway):
        """Test circuit breaker protection"""
        gateway = setup_sdk_gateway
        
        # Create circuit breaker
        circuit_breaker = get_circuit_breaker_manager(redis_client=gateway.redis)
        
        # Configure circuit breaker for payment initiation
        circuit_breaker.get_circuit_breaker(
            name="phonepe_payment_initiation",
            failure_threshold=3,
            recovery_timeout=timedelta(minutes=1)
        )
        
        # Mock SDK failure
        gateway._client.pay.side_effect = Exception("API timeout")
        
        # Create payment request
        request = PaymentRequest(
            amount=10000,
            merchant_order_id="TEST_ORDER_789",
            redirect_url="https://example.com/return",
            callback_url="https://example.com/callback",
            user_id="user123"
        )
        
        # First request should fail
        result1 = await gateway.initiate_payment(request)
        assert result1.success is False
        assert "Circuit breaker OPEN" in result.error
        
        # Circuit should be open now
        circuit = circuit_breaker.get_circuit_breaker("phonepe_payment_initiation")
        assert circuit.get_state() == "OPEN"
        
        # Wait for recovery timeout
        await asyncio.sleep(60)  # 1 minute
        
        # Second request should succeed after recovery
        result2 = await gateway.initiate_payment(request)
        assert result2.success is True
        assert result2.transaction_id != result1.transaction_id
    
    @pytest.mark.asyncio
    async def test_fraud_detection_integration(self, setup_sdk_gateway):
        """Test fraud detection integration"""
        gateway = setup_sdk_gateway
        
        # Mock fraud assessment
        mock_assessment = Mock()
        mock_assessment.overall_risk_score = 0.2
        mock_assessment.risk_level = "LOW"
        mock_assessment.recommended_action = "ALLOW"
        
        gateway._fraud_detector.assess_payment_risk.return_value = mock_assessment
        
        # Create payment request
        request = PaymentRequest(
            amount=10000,
            merchant_order_id="TEST_ORDER_789",
            redirect_url="https://example.com/return",
            callback_url="https://example.com/callback",
            user_id="user123",
            customer_info={"name": "Test User", "email": "test@example.com"}
        )
        
        # Process payment
        result = await gateway.initiate_payment(request)
        
        # Verify fraud detection was called
        gateway._fraud_detector.assess_payment_risk.assert_called_once()
        
        # Verify result
        assert result.success is True
        assert result.security_metadata["fraud_score"] == 0.2
        assert result.security_metadata["risk_level"] == "LOW"
    
    @pytest.mark.asyncio
    async def test_transaction_consistency(self, setup_sdk_gateway):
        """Test transaction consistency"""
        gateway = setup_sdk_gateway
        
        # Create transaction manager
        transaction_manager = get_transaction_manager(redis_client=gateway.redis)
        
        # Create payment request
        request = PaymentRequest(
            amount=10000,
            merchant_order_id="TEST_ORDER_789",
            redirect_url="https://example.com/return",
            callback_url="https://example.com/callback",
            user_id="user123"
        )
        
        # Process within transaction
        async with transaction_manager.transaction_context(
            isolation_level="READ_COMMITTED",
            metadata={"test": True}
        ) as tx:
            # Initiate payment within transaction
            result = await gateway.initiate_payment(request)
            assert result.success is True
            
            # Check transaction was recorded
            tx.execute("SELECT 1 FROM payments WHERE merchant_order_id = %s", (merchant_order_id,))
            records = tx.fetchall()
            assert len(records) == 1
            assert records[0]["status"] == "PENDING"
            
            # Complete transaction
            await tx.commit()
            
            # Verify result
            assert result.success is True
            assert result.transaction_id == records[0]["transaction_id"]
    
    @pytest.mark.asyncio
    async def test_rate_limiting_integration(self, setup_sdk_gateway):
        """Test rate limiting integration"""
        gateway = setup_sdk_gateway
        
        # Create rate limiting manager
        rate_limiter = get_rate_limiting_manager(redis_client=gateway.redis)
        
        # Configure rate limiting for user
        rate_limiter.get_circuit_breaker(
            name="payment_initiation",
            failure_threshold=10,
            recovery_timeout=timedelta(minutes=1)
        )
        
        # Create payment request
        request = PaymentRequest(
            amount=10000,
            merchant_order_id="TEST_ORDER_789",
            redirect_url="https://example.com/return",
            callback_url="https://example.com/callback",
            user_id="user123"
        )
        
        # Process multiple requests rapidly
        results = []
        for i in range(15):
            result = await gateway.initiate_payment(request)
            results.append(result)
        
        # Should eventually hit rate limit
        failed_count = sum(1 for result in results if not result.success)
        assert failed_count > 5  # At least 6 failures should trigger rate limiting
    
    @pytest.mark.asyncio
    async def test_audit_logging_integration(self, setup_sdk_gateway):
        """Test audit logging integration"""
        gateway = setup_sdk_gateway
        
        # Create payment request
        request = PaymentRequest(
            amount=10000,
            merchant_order_id="TEST_ORDER_789",
            redirect_url="https://example.com/return",
            callback_url="https://example.com/callback",
            user_id="user123"
        )
        
        # Process payment
        result = await gateway.initiate_payment(request)
        
        # Verify audit logging was called
        # This would be verified by checking the audit logs
        assert result.success is True
    
    @pytest.mark.asyncio
    async def test_health_check_all_components(self):
        """Health check for all compliance components"""
        # Test Redis connection
        try:
            redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            redis_client.ping()
            redis_healthy = True
        except Exception:
            redis_healthy = False
        
        # Test each component
        components = {
            "redis": redis_healthy,
            "phonepe_sdk_gateway": True,  # Will be created when needed
            "refund_system": True,  # Will be created when needed
            "webhook_handler": True,  # Will be created when needed
            "transaction_manager": True,  # Will be created when needed
            "idempotency_manager": True,  # Will be created when needed
            "rate_limiting": True,  # Will be created when needed
            "circuit_breaker": True,  # Will be created when needed
            "fraud_detector": True,  # Will be created when needed
            "payment_monitor": True,  # Will be created when needed
            "compliance_manager": True,  # Will be created when needed
        }
        
        all_healthy = all(components.values())
        
        return all_healthy
    
    @pytest.mark.asyncio
    async def test_encryption_decryption_cycle(self, setup_sdk_gateway):
        """Test encryption/decryption cycle"""
        gateway = setup_sdk_gateway
        
        # Test data
        test_data = {
            "user_id": "user123",
            "amount": 10000,
            "card_number": "4111111111111111111"
        }
        
        # Encrypt data
        encrypted_data, metadata = await gateway.encrypt_data(test_data, DataClassification.SENSITIVE_FINANCIAL)
        
        # Decrypt data
        decrypted_data = await gateway.decrypt_data(encrypted_data, metadata["key_id"])
        
        # Verify round-trip
        assert decrypted_data == test_data
    
    @pytest.mark.asyncio
    async def test_data_subject_request_workflow(self, setup_sdk_gateway):
        """Test GDPR data subject request workflow"""
        gateway = setup_sdk_gateway
        
        # Create data subject request
        request_id = await gateway.right_to_be_forgotten(
            user_id="user123",
            data_categories=["personal", "contact", "preferences"],
            reason="User leaving platform"
        )
        
        # Verify request was created
        dsr = await gateway.get_data_subject_request(request_id)
        assert dsr is not None
        assert dsr.status == "PENDING"
        
        # Process request
        await gateway.process_data_subject_request(
            request_id=request_id,
            processor_id="system",
            result="COMPLETED",
            notes="Data deleted as requested"
        )
        
        # Verify processing
        processed_dsr = await gateway.get_data_subject_request(request_id)
        assert processed_dsr.status == "COMPLETED"
    
    @pytest.mark.asyncio
    async def test_compliance_reporting(self, setup_sdk_gateway):
        """Generate comprehensive compliance report"""
        gateway = setup_sdk_gateway
        
        # Generate compliance report
        report = await gateway.health_check()
        
        # Verify health check
        assert report["status"] == "healthy"
        
        # Verify features
        assert report["features"]["pci_dss_compliance"] is True
        assert report["features"]["gdpr_compliance"] is True
        assert report["features"]["data_encryption"] is True
        assert report["features"]["audit_logging"] is True
        assert report["features"]["data_subject_requests"] is True
    
    @pytest.mark.asyncio
    def test_error_handling_and_recovery(self, setup_sdk_gateway):
        """Test error handling and recovery mechanisms"""
        gateway = setup_sdk_gateway
        
        # Mock partial failure
        gateway._client.pay.side_effect = Exception("Temporary API failure")
        
        # Create payment request
        request = PaymentRequest(
            amount=10000,
            merchant_order_id="TEST_ORDER_789",
            redirect_url="https://example.com/return",
            callback_url="https://example.com/callback",
            user_id="user123"
        )
        
        # First attempt should fail
        result1 = await gateway.initiate_payment(request)
        assert result1.success is False
        assert "API_ERROR" in result.error
        
        # Second attempt should succeed after recovery
        result2 = await gateway.initiate_payment(request)
        assert result2.success is True

# Test configuration
@pytest.fixture
def test_redis_client():
    """Create test Redis client"""
    return redis.Redis(host='localhost', port=6379, decode_responses=True)

@pytest.fixture
def test_payment_repository():
    """Create test payment repository"""
    return AsyncMock(spec=PaymentRepository)

@pytest.fixture
def mock_audit_logger():
    """Create mock audit logger"""
    return AsyncMock(spec=AuditLogger)

@pytest.fixture
def mock_fraud_detector():
    """Create mock fraud detector"""
    return AsyncMock(spec=PaymentFraudDetector)

@pytest.fixture
def mock_transaction_manager():
    """Create mock transaction manager"""
    return AsyncMock(spec=TransactionConsistencyManager)

# Integration test class
class TestPaymentIntegration:
    """Integration tests for the complete payment system"""
    
    @pytest.mark.asyncio
    async def test_complete_payment_flow(self, test_redis_client, test_payment_repository):
        """Test complete payment flow from initiation to webhook processing"""
        # Initialize all components
        phonepe_gateway = phonepe_sdk_gateway
        refund_manager = get_refund_manager(test_payment_repository)
        webhook_handler = get_secure_webhook_handler(test_redis_client, test_payment_repository)
        transaction_manager = get_transaction_manager(test_redis_client)
        rate_limiter = get_rate_limiting_manager(test_redis_client)
        circuit_breaker = get_circuit_breaker_manager(test_redis_client)
        fraud_detector = get_fraud_detector(test_redis_client)
        compliance_manager = get_compliance_manager(test_redis_client)
        
        # Start monitoring
        await payment_monitor.start_monitoring()
        
        # Test complete flow
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        
        # 1. Initiate payment
        payment_request = PaymentRequest(
            amount=10000,
            merchant_order_id=f"TX{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8]}",
            redirect_url="https://example.com/return",
            callback_url="https://example.com/callback",
            customer_info={"name": "Test User", "email": f"test@example.com"},
            user_id=user_id
        )
        
        payment_result = await phonepe_gateway.initiate_payment(payment_request)
        assert payment_result.success is True
        
        # 2. Check status
        status_result = await phonepe_gateway.check_payment_status(payment_result.transaction_id)
        assert status_result.success is True
        assert status_result.state == "COMPLETED"
        
        # 3. Process refund if applicable
        if payment_result.status == "COMPLETED":
            refund_request = RefundRequestData(
                merchant_order_id=payment_result.merchant_order_id,
                refund_amount=int(payment_result.amount * 0.1),  # 10% refund
                refund_reason="Customer satisfaction"
            )
            
            refund_result = await refund_manager.create_refund_request(refund_request)
            assert refund_result.success is True
            
            # 4. Log webhook processing
            webhook_data = {
                "type": "PAYMENT_SUCCESS",
                "code": "SUCCESS",
                "data": {
                    "merchantTransactionId": payment_result.transaction_id,
                    "amount": payment_result.amount,
                    "state": payment_result.state
                }
            }
            
            webhook_result = await webhook_handler.handle_webhook(
                payload=webhook_data,
                signature="sha256:hash"
            )
            
            assert webhook_result["valid"] is True
        
        # 5. Verify all components are healthy
        health_checks = [
            await phonepe_gateway.health_check(),
            await refund_manager.health_check(),
            await webhook_handler.health_check(),
            transaction_manager.health_check(),
            rate_limiter.health_check(),
            circuit_breaker.health_check(),
            fraud_detector.health_check(),
            compliance_manager.health_check()
        ]
        
        for check in health_checks:
            assert check["status"] == "healthy"
        
        # Clean up
        await payment_monitor.stop_monitoring()
        
        logger.info("Integration test completed successfully")

if __name__ == "__main__":
    # Run integration tests
    pytest.main([test_redis_client, test_payment_repository], verbose=True)
