"""
PhonePe Payment Gateway Service
Handles payment processing, subscription management, and webhook validation.
"""

import hashlib
import base64
import json
import uuid
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Tuple
import httpx

from backend.config.settings import settings
from backend.utils.retry import async_retry
from backend.models.payment import (
    PhonePePaymentRequest,
    PhonePePaymentResponse,
    PaymentStatus,
    SubscriptionPlan
)

logger = logging.getLogger(__name__)


class PhonePeService:
    """Service class for PhonePe payment integration."""

    # PhonePe API endpoints
    PRODUCTION_URL = "https://api.phonepe.com/apis/hermes"
    SANDBOX_URL = "https://api-preprod.phonepe.com/apis/pg-sandbox"

    # Plan pricing (in rupees)
    PLAN_PRICES = {
        "ascent": {"monthly": 2499, "yearly": 24999},
        "glide": {"monthly": 6499, "yearly": 64999},
        "soar": {"monthly": 16499, "yearly": 164999}
    }

    # Plan features and limits
    PLAN_FEATURES = {
        "ascent": {
            "cohorts": 3,
            "moves": 1,
            "analytics": True,
            "integrations": ["linkedin", "twitter"],
            "support": "email"
        },
        "glide": {
            "cohorts": 6,
            "moves": 3,
            "analytics": True,
            "integrations": ["linkedin", "twitter", "instagram"],
            "support": "priority_email"
        },
        "soar": {
            "cohorts": 9,
            "moves": 10,
            "analytics": True,
            "integrations": ["linkedin", "twitter", "instagram", "facebook", "youtube"],
            "support": "priority_phone"
        }
    }

    def __init__(self):
        """Initialize PhonePe service with configuration."""
        self.merchant_id = settings.PHONEPE_MERCHANT_ID
        self.salt_key = settings.PHONEPE_SALT_KEY
        self.salt_index = settings.PHONEPE_SALT_INDEX
        self.is_production = settings.ENVIRONMENT == "production"
        self.base_url = self.PRODUCTION_URL if self.is_production else self.SANDBOX_URL

    def _generate_checksum(self, payload: str) -> str:
        """
        Generate X-VERIFY checksum for PhonePe API requests.

        Args:
            payload: Base64 encoded request payload

        Returns:
            SHA256 checksum string
        """
        checksum_string = f"{payload}/pg/v1/pay{self.salt_key}"
        checksum = hashlib.sha256(checksum_string.encode()).hexdigest()
        return f"{checksum}###{self.salt_index}"

    def _verify_webhook_checksum(self, payload: str, checksum: str) -> bool:
        """
        Verify webhook checksum from PhonePe.

        Args:
            payload: Base64 encoded webhook payload
            checksum: Received checksum to verify

        Returns:
            True if checksum is valid, False otherwise
        """
        calculated_checksum = hashlib.sha256(
            f"{payload}{self.salt_key}".encode()
        ).hexdigest()

        # Extract checksum without salt index
        received_checksum = checksum.split("###")[0] if "###" in checksum else checksum

        return calculated_checksum == received_checksum

    def _validate_plan_and_period(self, plan: str, billing_period: str) -> Tuple[bool, Optional[str]]:
        """
        Validate plan and billing period.

        Args:
            plan: Plan name
            billing_period: Billing period

        Returns:
            Tuple of (is_valid, error_message)
        """
        if plan not in self.PLAN_PRICES:
            return False, f"Invalid plan: {plan}. Allowed: {', '.join(self.PLAN_PRICES.keys())}"

        if billing_period not in self.PLAN_PRICES.get(plan, {}):
            return False, f"Invalid billing period for {plan}: {billing_period}. Allowed: {', '.join(self.PLAN_PRICES[plan].keys())}"

        return True, None

    def get_plan_price(self, plan: str, billing_period: str = "monthly") -> Tuple[int, Optional[str]]:
        """
        Get price for a plan in rupees with validation.

        Args:
            plan: Plan name (ascent, glide, soar)
            billing_period: Billing period (monthly, yearly)

        Returns:
            Tuple of (price_in_rupees, error_message)
        """
        is_valid, error = self._validate_plan_and_period(plan, billing_period)
        if not is_valid:
            return 0, error

        price = self.PLAN_PRICES[plan][billing_period]

        # Validate price
        if price <= 0:
            return 0, f"Invalid price for {plan}/{billing_period}: {price}"

        if price > 999999:  # Max 9,99,999 rupees
            return 0, f"Price exceeds maximum limit: {price}"

        return price, None

    def get_plan_details(self, plan: str) -> SubscriptionPlan:
        """
        Get complete plan details.

        Args:
            plan: Plan name (ascent, glide, soar)

        Returns:
            SubscriptionPlan object
        """
        return SubscriptionPlan(
            plan_id=f"plan_{plan}",
            name=plan,
            price_monthly=self.PLAN_PRICES[plan]["monthly"],
            price_yearly=self.PLAN_PRICES[plan]["yearly"],
            features=self.PLAN_FEATURES[plan],
            limits={
                "cohorts": self.PLAN_FEATURES[plan]["cohorts"],
                "moves_per_month": self.PLAN_FEATURES[plan]["moves"]
            }
        )

    @async_retry(max_attempts=3, initial_delay=1.0, max_delay=10.0, backoff_factor=2.0)
    async def _call_phonepe_create_payment(
        self,
        payload_base64: str,
        checksum: str,
        request_body: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Internal method to call PhonePe payment API with retry support.
        Raises exceptions on network errors for retry decorator to handle.
        """
        headers = {
            "Content-Type": "application/json",
            "X-VERIFY": checksum
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/pg/v1/pay",
                json=request_body,
                headers=headers
            )
            response.raise_for_status()  # Raise on HTTP errors
            return response.json()

    async def create_payment(
        self,
        request: PhonePePaymentRequest
    ) -> Tuple[PhonePePaymentResponse, Optional[str]]:
        """
        Create a new payment request with PhonePe.
        Uses exponential backoff retry for transient failures.

        Args:
            request: Payment request details

        Returns:
            Tuple of (PhonePePaymentResponse, error_message)
        """
        try:
            # Generate unique merchant transaction ID
            merchant_transaction_id = f"MT{uuid.uuid4().hex[:20].upper()}"

            # Calculate and validate amount in paise (PhonePe uses smallest currency unit)
            amount_rupees, amount_error = self.get_plan_price(request.plan, request.billing_period)
            if amount_error:
                logger.error(f"Amount validation failed: {amount_error}")
                return None, amount_error

            amount_paise = amount_rupees * 100

            # Prepare payment request payload
            payment_payload = {
                "merchantId": self.merchant_id,
                "merchantTransactionId": merchant_transaction_id,
                "merchantUserId": str(request.user_id),
                "amount": amount_paise,
                "redirectUrl": request.redirect_url,
                "redirectMode": "POST",
                "callbackUrl": request.callback_url,
                "mobileNumber": None,  # Optional: can be collected from user
                "paymentInstrument": {
                    "type": "PAY_PAGE"  # Shows all payment options to user
                }
            }

            # Base64 encode the payload
            payload_json = json.dumps(payment_payload)
            payload_base64 = base64.b64encode(payload_json.encode()).decode()

            # Generate checksum
            checksum = self._generate_checksum(payload_base64)

            request_body = {
                "request": payload_base64
            }

            # Make API request with retry logic
            response_data = await self._call_phonepe_create_payment(
                payload_base64,
                checksum,
                request_body
            )

            if response_data.get("success"):
                payment_data = response_data.get("data", {})

                return PhonePePaymentResponse(
                    transaction_id=payment_data.get("transactionId", ""),
                    merchant_transaction_id=merchant_transaction_id,
                    payment_url=payment_data.get("instrumentResponse", {}).get("redirectInfo", {}).get("url", ""),
                    amount=amount_paise,
                    status="pending"
                ), None
            else:
                error_msg = response_data.get("message", "Payment initiation failed")
                logger.error(f"PhonePe payment creation failed: {error_msg}")
                return None, error_msg

        except Exception as e:
            logger.error(f"Error creating PhonePe payment: {str(e)}", exc_info=True)
            return None, f"Payment service error: {str(e)}"

    @async_retry(max_attempts=3, initial_delay=1.0, max_delay=10.0, backoff_factor=2.0)
    async def _call_phonepe_check_status(
        self,
        checksum_header: str,
        merchant_transaction_id: str
    ) -> Dict[str, Any]:
        """
        Internal method to call PhonePe status check API with retry support.
        Raises exceptions on network errors for retry decorator to handle.
        """
        headers = {
            "Content-Type": "application/json",
            "X-VERIFY": checksum_header,
            "X-MERCHANT-ID": self.merchant_id
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/pg/v1/status/{self.merchant_id}/{merchant_transaction_id}",
                headers=headers
            )
            response.raise_for_status()  # Raise on HTTP errors
            return response.json()

    async def check_payment_status(
        self,
        merchant_transaction_id: str
    ) -> Tuple[Optional[PaymentStatus], Optional[str]]:
        """
        Check status of a payment transaction.
        Uses exponential backoff retry for transient failures.

        Args:
            merchant_transaction_id: Merchant transaction ID to check

        Returns:
            Tuple of (PaymentStatus, error_message)
        """
        try:
            # Prepare checksum for status check
            checksum_string = f"/pg/v1/status/{self.merchant_id}/{merchant_transaction_id}{self.salt_key}"
            checksum = hashlib.sha256(checksum_string.encode()).hexdigest()
            checksum_header = f"{checksum}###{self.salt_index}"

            # Make API request with retry logic
            response_data = await self._call_phonepe_check_status(
                checksum_header,
                merchant_transaction_id
            )

            if response_data.get("success"):
                data = response_data.get("data", {})

                # Map PhonePe status to our status
                phonepe_state = data.get("state", "").upper()
                if phonepe_state == "COMPLETED":
                    status = "success"
                elif phonepe_state == "FAILED":
                    status = "failed"
                elif phonepe_state == "PENDING":
                    status = "pending"
                else:
                    status = "cancelled"

                return PaymentStatus(
                    transaction_id=data.get("transactionId", ""),
                    merchant_transaction_id=merchant_transaction_id,
                    status=status,
                    amount=data.get("amount", 0),
                    payment_method=data.get("paymentInstrument", {}).get("type"),
                    response_code=data.get("responseCode"),
                    response_message=data.get("responseMessage"),
                    transaction_time=datetime.now(timezone.utc)
                ), None
            else:
                error_msg = response_data.get("message", "Status check failed")
                logger.error(f"PhonePe status check failed: {error_msg}")
                return None, error_msg

        except Exception as e:
            logger.error(f"Error checking payment status: {str(e)}", exc_info=True)
            return None, f"Status check error: {str(e)}"

    def verify_webhook_payload(
        self,
        payload_base64: str,
        checksum: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Verify and decode PhonePe webhook payload.

        Args:
            payload_base64: Base64 encoded webhook payload
            checksum: X-VERIFY checksum header

        Returns:
            Tuple of (decoded_payload, error_message)
        """
        try:
            # Verify checksum
            if not self._verify_webhook_checksum(payload_base64, checksum):
                return None, "Invalid webhook checksum"

            # Decode payload
            payload_json = base64.b64decode(payload_base64).decode()
            payload_data = json.loads(payload_json)

            return payload_data, None

        except Exception as e:
            logger.error(f"Error verifying webhook: {str(e)}", exc_info=True)
            return None, f"Webhook verification error: {str(e)}"

    def calculate_subscription_dates(
        self,
        billing_period: str
    ) -> Tuple[datetime, datetime]:
        """
        Calculate subscription start and end dates.

        Args:
            billing_period: monthly or yearly

        Returns:
            Tuple of (period_start, period_end)
        """
        now = datetime.now(timezone.utc)

        if billing_period == "monthly":
            period_end = now + timedelta(days=30)
        else:  # yearly
            period_end = now + timedelta(days=365)

        return now, period_end


# Global instance
phonepe_service = PhonePeService()
