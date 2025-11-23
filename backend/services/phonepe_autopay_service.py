"""
PhonePe Autopay Service
Handles recurring payment subscriptions using PhonePe Python SDK.
"""

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Tuple

from phonepe_sdk.autopay.autopay_client import AutopayClient
from phonepe_sdk.autopay.models.autopay_request import AutopayRequest
from phonepe_sdk.autopay.models.subscription_request import SubscriptionRequest
from phonepe_sdk.autopay.models.autopay_constants import AutopayConstants
from phonepe_sdk.autopay.env import Env

from backend.config.settings import settings
from backend.models.payment import (
    AutopaySubscriptionRequest,
    AutopaySubscriptionResponse,
    AutopaySubscriptionStatus,
    SubscriptionPlan
)

logger = logging.getLogger(__name__)


class PhonePeAutopayService:
    """Service class for PhonePe Autopay (recurring payments) integration."""

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
        """Initialize PhonePe Autopay service with SDK configuration."""
        self.client_id = settings.PHONEPE_AUTOPAY_CLIENT_ID
        self.client_secret = settings.PHONEPE_AUTOPAY_CLIENT_SECRET
        self.client_version = settings.PHONEPE_AUTOPAY_CLIENT_VERSION
        self.is_production = settings.ENVIRONMENT == "production"

        # Initialize PhonePe Autopay Client
        self.env = Env.PROD if self.is_production else Env.UAT

        try:
            self.autopay_client = AutopayClient(
                client_id=self.client_id,
                client_secret=self.client_secret,
                client_version=self.client_version,
                env=self.env
            )
            logger.info(f"PhonePe Autopay client initialized in {self.env.name} mode")
        except Exception as e:
            logger.error(f"Failed to initialize PhonePe Autopay client: {e}")
            self.autopay_client = None

    def _calculate_subscription_amount(self, plan: str, billing_period: str) -> int:
        """
        Calculate subscription amount in paise.

        Args:
            plan: Plan name (ascent, glide, soar)
            billing_period: Billing period (monthly, yearly)

        Returns:
            Amount in paise (smallest currency unit)
        """
        amount_rupees = self.PLAN_PRICES.get(plan, {}).get(billing_period, 0)
        return amount_rupees * 100  # Convert to paise

    def _calculate_subscription_dates(
        self,
        billing_period: str
    ) -> Tuple[datetime, datetime]:
        """
        Calculate subscription start and end dates.

        Args:
            billing_period: monthly or yearly

        Returns:
            Tuple of (start_date, end_date)
        """
        start_date = datetime.now(timezone.utc)

        if billing_period == "monthly":
            end_date = start_date + timedelta(days=30)
        else:  # yearly
            end_date = start_date + timedelta(days=365)

        return start_date, end_date

    def _get_billing_frequency(self, billing_period: str) -> str:
        """
        Get PhonePe billing frequency constant.

        Args:
            billing_period: monthly or yearly

        Returns:
            PhonePe frequency constant
        """
        if billing_period == "monthly":
            return AutopayConstants.FREQUENCY_MONTHLY
        elif billing_period == "yearly":
            return AutopayConstants.FREQUENCY_YEARLY
        else:
            return AutopayConstants.FREQUENCY_MONTHLY

    async def create_subscription(
        self,
        request: AutopaySubscriptionRequest
    ) -> Tuple[Optional[AutopaySubscriptionResponse], Optional[str]]:
        """
        Create a new autopay subscription.

        Args:
            request: Autopay subscription request details

        Returns:
            Tuple of (AutopaySubscriptionResponse, error_message)
        """
        try:
            if not self.autopay_client:
                return None, "Autopay client not initialized"

            # Generate unique merchant subscription ID
            merchant_subscription_id = f"SUB{uuid.uuid4().hex[:20].upper()}"
            merchant_user_id = str(request.user_id)

            # Calculate amount and dates
            amount_paise = self._calculate_subscription_amount(
                request.plan,
                request.billing_period
            )
            start_date, end_date = self._calculate_subscription_dates(
                request.billing_period
            )
            billing_frequency = self._get_billing_frequency(request.billing_period)

            # Create subscription request using PhonePe SDK
            subscription_request = SubscriptionRequest(
                merchant_subscription_id=merchant_subscription_id,
                merchant_user_id=merchant_user_id,
                amount=amount_paise,
                mobile_number=request.mobile_number,
                billing_frequency=billing_frequency,
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                autopay_type=AutopayConstants.AUTOPAY_TYPE_MANDATE,
                callback_url=request.callback_url,
                redirect_url=request.redirect_url,
                redirect_mode="POST"
            )

            # Create autopay subscription
            autopay_response = self.autopay_client.create_subscription(
                subscription_request
            )

            if autopay_response and autopay_response.success:
                data = autopay_response.data

                return AutopaySubscriptionResponse(
                    subscription_id=data.get("subscriptionId", ""),
                    merchant_subscription_id=merchant_subscription_id,
                    authorization_url=data.get("instrumentResponse", {}).get("redirectInfo", {}).get("url", ""),
                    amount=amount_paise,
                    status="pending",
                    start_date=start_date,
                    end_date=end_date,
                    billing_frequency=billing_frequency
                ), None
            else:
                error_msg = autopay_response.message if autopay_response else "Subscription creation failed"
                logger.error(f"PhonePe autopay subscription creation failed: {error_msg}")
                return None, error_msg

        except Exception as e:
            logger.error(f"Error creating autopay subscription: {str(e)}", exc_info=True)
            return None, f"Subscription creation error: {str(e)}"

    async def check_subscription_status(
        self,
        merchant_subscription_id: str
    ) -> Tuple[Optional[AutopaySubscriptionStatus], Optional[str]]:
        """
        Check status of an autopay subscription.

        Args:
            merchant_subscription_id: Merchant subscription ID to check

        Returns:
            Tuple of (AutopaySubscriptionStatus, error_message)
        """
        try:
            if not self.autopay_client:
                return None, "Autopay client not initialized"

            # Check subscription status using SDK
            status_response = self.autopay_client.check_subscription_status(
                merchant_subscription_id
            )

            if status_response and status_response.success:
                data = status_response.data

                # Map PhonePe status to our status
                phonepe_state = data.get("state", "").upper()
                if phonepe_state == "ACTIVE":
                    status = "active"
                elif phonepe_state == "PAUSED":
                    status = "paused"
                elif phonepe_state == "CANCELLED":
                    status = "cancelled"
                elif phonepe_state == "EXPIRED":
                    status = "expired"
                elif phonepe_state == "PENDING":
                    status = "pending"
                else:
                    status = "unknown"

                return AutopaySubscriptionStatus(
                    subscription_id=data.get("subscriptionId", ""),
                    merchant_subscription_id=merchant_subscription_id,
                    status=status,
                    amount=data.get("amount", 0),
                    start_date=datetime.fromisoformat(data.get("startDate", "")),
                    end_date=datetime.fromisoformat(data.get("endDate", "")),
                    billing_frequency=data.get("billingFrequency"),
                    next_billing_date=datetime.fromisoformat(data.get("nextBillingDate", "")) if data.get("nextBillingDate") else None,
                    total_payments=data.get("totalPayments", 0),
                    successful_payments=data.get("successfulPayments", 0),
                    failed_payments=data.get("failedPayments", 0)
                ), None
            else:
                error_msg = status_response.message if status_response else "Status check failed"
                logger.error(f"PhonePe autopay status check failed: {error_msg}")
                return None, error_msg

        except Exception as e:
            logger.error(f"Error checking subscription status: {str(e)}", exc_info=True)
            return None, f"Status check error: {str(e)}"

    async def cancel_subscription(
        self,
        merchant_subscription_id: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Cancel an active autopay subscription.

        Args:
            merchant_subscription_id: Merchant subscription ID to cancel

        Returns:
            Tuple of (success, error_message)
        """
        try:
            if not self.autopay_client:
                return False, "Autopay client not initialized"

            # Cancel subscription using SDK
            cancel_response = self.autopay_client.cancel_subscription(
                merchant_subscription_id
            )

            if cancel_response and cancel_response.success:
                logger.info(f"Successfully cancelled subscription {merchant_subscription_id}")
                return True, None
            else:
                error_msg = cancel_response.message if cancel_response else "Cancellation failed"
                logger.error(f"PhonePe autopay cancellation failed: {error_msg}")
                return False, error_msg

        except Exception as e:
            logger.error(f"Error cancelling subscription: {str(e)}", exc_info=True)
            return False, f"Cancellation error: {str(e)}"

    async def pause_subscription(
        self,
        merchant_subscription_id: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Pause an active autopay subscription.

        Args:
            merchant_subscription_id: Merchant subscription ID to pause

        Returns:
            Tuple of (success, error_message)
        """
        try:
            if not self.autopay_client:
                return False, "Autopay client not initialized"

            # Pause subscription using SDK
            pause_response = self.autopay_client.pause_subscription(
                merchant_subscription_id
            )

            if pause_response and pause_response.success:
                logger.info(f"Successfully paused subscription {merchant_subscription_id}")
                return True, None
            else:
                error_msg = pause_response.message if pause_response else "Pause failed"
                logger.error(f"PhonePe autopay pause failed: {error_msg}")
                return False, error_msg

        except Exception as e:
            logger.error(f"Error pausing subscription: {str(e)}", exc_info=True)
            return False, f"Pause error: {str(e)}"

    async def resume_subscription(
        self,
        merchant_subscription_id: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Resume a paused autopay subscription.

        Args:
            merchant_subscription_id: Merchant subscription ID to resume

        Returns:
            Tuple of (success, error_message)
        """
        try:
            if not self.autopay_client:
                return False, "Autopay client not initialized"

            # Resume subscription using SDK
            resume_response = self.autopay_client.resume_subscription(
                merchant_subscription_id
            )

            if resume_response and resume_response.success:
                logger.info(f"Successfully resumed subscription {merchant_subscription_id}")
                return True, None
            else:
                error_msg = resume_response.message if resume_response else "Resume failed"
                logger.error(f"PhonePe autopay resume failed: {error_msg}")
                return False, error_msg

        except Exception as e:
            logger.error(f"Error resuming subscription: {str(e)}", exc_info=True)
            return False, f"Resume error: {str(e)}"

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


# Global instance
phonepe_autopay_service = PhonePeAutopayService()
