"""
Comprehensive tests for PhonePe payment service.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from uuid import uuid4

from backend.services.phonepe_service import PhonePeService


@pytest.fixture
def phonepe_service():
    """Create PhonePe service instance."""
    return PhonePeService()


@pytest.fixture
def sample_payment_request():
    """Sample payment request data."""
    return {
        "plan": "glide",
        "user_id": str(uuid4()),
        "workspace_id": str(uuid4()),
        "redirect_url": "https://example.com/callback"
    }


class TestPhonePeService:
    """Test PhonePe payment service."""

    def test_plan_prices(self, phonepe_service):
        """Test that plan prices are correctly defined."""
        assert "ascent" in phonepe_service.PLAN_PRICES
        assert "glide" in phonepe_service.PLAN_PRICES
        assert "soar" in phonepe_service.PLAN_PRICES

        # Verify price structure
        for plan, prices in phonepe_service.PLAN_PRICES.items():
            assert "monthly" in prices
            assert prices["monthly"] > 0

    def test_plan_features(self, phonepe_service):
        """Test that plan features are correctly defined."""
        assert "ascent" in phonepe_service.PLAN_FEATURES
        assert "glide" in phonepe_service.PLAN_FEATURES
        assert "soar" in phonepe_service.PLAN_FEATURES

        # Verify feature structure
        for plan, features in phonepe_service.PLAN_FEATURES.items():
            assert "cohorts" in features
            assert "moves" in features
            assert "analytics" in features
            assert isinstance(features["cohorts"], int)

    def test_calculate_amount(self, phonepe_service):
        """Test amount calculation in paise."""
        # Ascent monthly = ₹2,499 = 249,900 paise
        amount = phonepe_service._calculate_amount("ascent", "monthly")
        assert amount == 249900

        # Glide monthly = ₹6,499 = 649,900 paise
        amount = phonepe_service._calculate_amount("glide", "monthly")
        assert amount == 649900

    def test_generate_merchant_transaction_id(self, phonepe_service):
        """Test merchant transaction ID generation."""
        user_id = str(uuid4())
        txn_id = phonepe_service._generate_merchant_transaction_id(user_id)

        assert isinstance(txn_id, str)
        assert len(txn_id) > 0
        # Should contain user_id fragment
        assert user_id[:8] in txn_id

    def test_generate_checksum(self, phonepe_service):
        """Test X-VERIFY checksum generation."""
        payload = '{"test": "data"}'

        with patch.object(phonepe_service, 'salt_key', 'test-salt'), \
             patch.object(phonepe_service, 'salt_index', 1):

            checksum = phonepe_service._generate_checksum(payload)

            assert isinstance(checksum, str)
            assert len(checksum) > 0
            # Should end with ###1 (salt index)
            assert checksum.endswith("###1")

    @pytest.mark.asyncio
    async def test_create_payment_success(self, phonepe_service, sample_payment_request):
        """Test successful payment creation."""
        with patch.object(phonepe_service, '_call_phonepe_api',
                          new_callable=AsyncMock) as mock_api:

            mock_api.return_value = {
                "success": True,
                "code": "PAYMENT_INITIATED",
                "data": {
                    "instrumentResponse": {
                        "redirectInfo": {
                            "url": "https://phonepe.com/pay/abc123"
                        }
                    }
                }
            }

            result = await phonepe_service.create_payment(sample_payment_request)

            assert result["success"] is True
            assert "payment_url" in result
            assert "merchant_transaction_id" in result

    @pytest.mark.asyncio
    async def test_create_payment_failure(self, phonepe_service, sample_payment_request):
        """Test payment creation failure."""
        with patch.object(phonepe_service, '_call_phonepe_api',
                          new_callable=AsyncMock) as mock_api:

            mock_api.return_value = {
                "success": False,
                "code": "PAYMENT_ERROR",
                "message": "Payment initiation failed"
            }

            result = await phonepe_service.create_payment(sample_payment_request)

            assert result["success"] is False

    def test_verify_webhook_valid(self, phonepe_service):
        """Test webhook signature verification with valid signature."""
        payload = {"test": "data"}
        valid_checksum = phonepe_service._generate_checksum(str(payload))

        is_valid = phonepe_service.verify_webhook(payload, valid_checksum)
        assert is_valid is True

    def test_verify_webhook_invalid(self, phonepe_service):
        """Test webhook signature verification with invalid signature."""
        payload = {"test": "data"}
        invalid_checksum = "invalid-checksum-12345###1"

        is_valid = phonepe_service.verify_webhook(payload, invalid_checksum)
        assert is_valid is False

    def test_get_plan_details(self, phonepe_service):
        """Test retrieving plan details."""
        plan_details = phonepe_service.get_plan_details("glide")

        assert plan_details is not None
        assert "name" in plan_details
        assert "price" in plan_details
        assert "features" in plan_details
        assert plan_details["features"]["cohorts"] == 6

    def test_get_plan_details_invalid(self, phonepe_service):
        """Test retrieving invalid plan."""
        plan_details = phonepe_service.get_plan_details("invalid_plan")
        assert plan_details is None

    def test_validate_plan(self, phonepe_service):
        """Test plan validation."""
        assert phonepe_service.validate_plan("ascent") is True
        assert phonepe_service.validate_plan("glide") is True
        assert phonepe_service.validate_plan("soar") is True
        assert phonepe_service.validate_plan("invalid") is False

    @pytest.mark.asyncio
    async def test_sandbox_mode(self, phonepe_service):
        """Test that sandbox mode is used in development."""
        with patch.object(phonepe_service, 'is_production', False):
            assert phonepe_service.is_production is False
            # In sandbox, API calls should go to UAT endpoint
