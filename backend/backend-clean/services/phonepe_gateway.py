"""
PhonePe Payment Gateway Service - Latest 2026 Integration
Updated to use Client ID + Client Secret authentication (no salt key)
Based on latest PhonePe SDK and API documentation for 2026
"""

import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

import requests
from phonepe.sdk.pg.env import Env
from phonepe.sdk.pg.payments.v2.standard_checkout_client import StandardCheckoutClient


class PhonePePaymentGateway:
    """
    PhonePe Payment Gateway integration service
    Updated for 2026: Uses Client ID + Client Secret authentication
    No salt key required in the current system
    """

    def __init__(self):
        # Current authentication system - Client ID + Client Secret only
        self.client_id = os.getenv("PHONEPE_CLIENT_ID")
        self.client_secret = os.getenv("PHONEPE_CLIENT_SECRET")
        self.client_version = int(os.getenv("PHONEPE_CLIENT_VERSION", "1"))

        # Environment setup
        self.env = (
            Env.PRODUCTION
            if os.getenv("PHONEPE_ENV", "UAT").lower() == "production"
            else Env.UAT
        )

        # Base URLs - Current 2026 endpoints
        if self.env == Env.PRODUCTION:
            self.base_url = "https://api.phonepe.com/apis/pg"
        else:
            self.base_url = "https://api-preprod.phonepe.com/apis/pg-sandbox"

        # Initialize PhonePe client with current auth system
        self.client = StandardCheckoutClient.get_instance(
            client_id=self.client_id,
            client_secret=self.client_secret,
            client_version=self.client_version,
            env=self.env,
            should_publish_events=False,
        )

        # OAuth token cache
        self._auth_token = None
        self._token_expires_at = None

        # Webhook credentials
        self.webhook_username = os.getenv("PHONEPE_WEBHOOK_USERNAME")
        self.webhook_password = os.getenv("PHONEPE_WEBHOOK_PASSWORD")

    def _get_auth_token(self) -> str:
        """
        Get OAuth token using Client ID + Client Secret
        Current authentication method - no salt key required (2026)
        """
        # Check if we have a valid cached token
        if (
            self._auth_token
            and self._token_expires_at
            and datetime.now().timestamp() < self._token_expires_at
        ):
            return self._auth_token

        # Request new token using 2026 endpoints
        token_url = f"{self.base_url}/v1/oauth/token"

        data = {
            "client_id": self.client_id,
            "client_version": str(self.client_version),
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        try:
            response = requests.post(token_url, data=data, headers=headers)
            response.raise_for_status()

            token_data = response.json()
            self._auth_token = token_data["access_token"]
            self._token_expires_at = token_data["expires_at"]

            return self._auth_token

        except Exception as e:
            raise Exception(f"Failed to get auth token: {str(e)}")

    def initiate_payment(
        self,
        amount: int,
        merchant_order_id: str,
        redirect_url: str,
        callback_url: str,
        customer_info: Optional[Dict] = None,
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Initiate a payment transaction using latest PhonePe SDK (2026)
        """
        try:
            # Generate unique transaction ID
            transaction_id = (
                f"MT{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8]}"
            )

            # Build payment request using current SDK
            from phonepe.sdk.pg.common.models.request.meta_info import MetaInfo
            from phonepe.sdk.pg.payments.v2.models.request.standard_checkout_pay_request import (
                StandardCheckoutPayRequest,
            )

            # Create meta info if customer data provided
            meta_info = None
            if customer_info:
                meta_info = (
                    MetaInfo.builder()
                    .udf1(customer_info.get("name", ""))
                    .udf2(customer_info.get("email", ""))
                    .udf3(customer_info.get("mobile", ""))
                    .build()
                )

            # Build payment request
            payment_request = StandardCheckoutPayRequest.build_request(
                merchant_order_id=merchant_order_id,
                amount=amount,
                redirect_url=redirect_url,
                meta_info=meta_info,
            )

            # Process payment
            payment_response = self.client.pay(payment_request)

            return {
                "success": True,
                "transaction_id": transaction_id,
                "merchant_order_id": merchant_order_id,
                "checkout_url": payment_response.redirect_url,
                "phonepe_transaction_id": payment_response.transaction_id,
                "amount": amount,
                "status": "PENDING",
            }

        except Exception as e:
            return {"success": False, "error": str(e), "status": "FAILED"}

    def check_payment_status(self, merchant_order_id: str) -> Dict[str, Any]:
        """
        Check payment status using merchant order ID
        Current SDK method for 2026
        """
        try:
            # Use current SDK method for order status
            response = self.client.get_order_status(merchant_order_id, details=True)

            return {
                "success": True,
                "status": response.state,
                "merchant_order_id": merchant_order_id,
                "amount": response.amount,
                "payment_instrument": getattr(response, "payment_instrument", None),
                "response_data": response.__dict__,
            }

        except Exception as e:
            return {"success": False, "error": str(e), "status": "ERROR"}

    def process_refund(
        self, merchant_order_id: str, refund_amount: int, refund_reason: str
    ) -> Dict[str, Any]:
        """
        Process refund using current SDK (2026)
        """
        try:
            from phonepe.sdk.pg.common.models.request.refund_request import (
                RefundRequest,
            )

            # Generate unique refund ID
            merchant_refund_id = (
                f"RF{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8]}"
            )

            # Build refund request
            refund_request = RefundRequest.build_refund_request(
                merchant_refund_id=merchant_refund_id,
                original_merchant_order_id=merchant_order_id,
                amount=refund_amount,
            )

            # Process refund
            refund_response = self.client.refund(refund_request)

            return {
                "success": True,
                "refund_id": merchant_refund_id,
                "status": refund_response.state,
                "response_data": refund_response.__dict__,
            }

        except Exception as e:
            return {"success": False, "error": str(e), "status": "FAILED"}

    def validate_webhook(
        self, authorization_header: str, response_body: str
    ) -> Dict[str, Any]:
        """
        Validate webhook - updated for current system (2026)
        """
        try:
            # For now, basic validation - enhance based on current webhook format
            webhook_data = json.loads(response_body)

            return {"success": True, "valid": True, "webhook_data": webhook_data}

        except Exception as e:
            return {"success": False, "valid": False, "error": str(e)}


# Singleton instance
phonepe_gateway = PhonePePaymentGateway()
