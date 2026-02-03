"""
Payments Domain - Service
PhonePe payment processing and subscription management
"""

import hashlib
import hmac
import json
import logging
import os
from typing import Any, Dict, Optional

import httpx
from infrastructure.database import get_supabase

from .models import Payment, PaymentStatus, Subscription, SubscriptionStatus

logger = logging.getLogger(__name__)


class PaymentService:
    """Payment service for PhonePe integration"""

    def __init__(self):
        self.db = get_supabase()
        self.merchant_id = os.getenv("PHONEPE_MERCHANT_ID", "")
        self.salt_key = os.getenv("PHONEPE_SALT_KEY", "")
        self.env = os.getenv("PHONEPE_ENV", "sandbox")

        self.base_url = (
            "https://api.phonepe.com/apis/hermes"
            if self.env == "production"
            else "https://api-preprod.phonepe.com/apis/hermes"
        )

    def _generate_checksum(self, payload: str) -> str:
        """Generate PhonePe checksum"""
        data = payload + "/pg/v1/pay" + self.salt_key
        return hashlib.sha256(data.encode()).hexdigest()

    async def create_payment(
        self,
        workspace_id: str,
        plan: str,
        amount: int,
        customer_email: str,
        customer_name: Optional[str] = None,
        redirect_url: Optional[str] = None,
    ) -> Optional[Payment]:
        """Create a new payment"""
        try:
            # Generate merchant order ID
            merchant_order_id = f"ORD_{workspace_id}_{int(os.times().system * 1000)}"

            # Create payment in database
            payment_data = {
                "workspace_id": workspace_id,
                "merchant_order_id": merchant_order_id,
                "amount": amount,
                "currency": "INR",
                "status": PaymentStatus.PENDING,
                "plan": plan,
                "customer_email": customer_email,
                "customer_name": customer_name,
            }

            result = await self.db.insert("payments", payment_data)
            if not result.data:
                return None

            payment = Payment(**result.data[0])

            # Generate PhonePe payment request
            payload = {
                "merchantId": self.merchant_id,
                "merchantTransactionId": merchant_order_id,
                "merchantUserId": workspace_id,
                "amount": amount,
                "redirectUrl": redirect_url or "https://raptorflow.in/payment/callback",
                "redirectMode": "REDIRECT",
                "callbackUrl": "https://api.raptorflow.in/api/v1/payments/webhook",
                "paymentInstrument": {"type": "PAY_PAGE"},
            }

            payload_json = json.dumps(payload)
            payload_base64 = payload_json.encode().decode()

            checksum = self._generate_checksum(payload_base64)

            # Call PhonePe API
            headers = {
                "Content-Type": "application/json",
                "X-VERIFY": f"{checksum}###1",
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/pg/v1/pay",
                    headers=headers,
                    json={"request": payload_base64},
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        payment_url = data["data"]["instrumentResponse"][
                            "redirectInfo"
                        ]["url"]

                        # Update payment with URL
                        await self.db.update(
                            "payments", {"payment_url": payment_url}, {"id": payment.id}
                        )
                        payment.payment_url = payment_url

                        return payment

            return payment

        except Exception as e:
            logger.error(f"Failed to create payment: {e}")
            return None

    async def verify_payment(self, merchant_order_id: str) -> Optional[Payment]:
        """Verify payment status with PhonePe"""
        try:
            # Get payment from database
            result = await self.db.select(
                "payments", {"merchant_order_id": merchant_order_id}
            )
            if not result.data:
                return None

            payment = Payment(**result.data[0])

            # Check status with PhonePe
            endpoint = f"/pg/v1/status/{self.merchant_id}/{merchant_order_id}"
            checksum = hashlib.sha256((endpoint + self.salt_key).encode()).hexdigest()

            headers = {
                "Content-Type": "application/json",
                "X-VERIFY": f"{checksum}###1",
                "X-MERCHANT-ID": self.merchant_id,
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}{endpoint}",
                    headers=headers,
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        status = data["data"]["state"]

                        # Map PhonePe status to our status
                        if status == "COMPLETED":
                            payment.status = PaymentStatus.SUCCESS
                        elif status == "FAILED":
                            payment.status = PaymentStatus.FAILED

                        # Update in database
                        await self.db.update(
                            "payments", {"status": payment.status}, {"id": payment.id}
                        )

            return payment

        except Exception as e:
            logger.error(f"Failed to verify payment: {e}")
            return None

    async def handle_webhook(self, payload: Dict[str, Any]) -> bool:
        """Handle PhonePe webhook"""
        try:
            merchant_order_id = payload.get("merchantTransactionId")
            status = payload.get("status")

            # Find payment
            result = await self.db.select(
                "payments", {"merchant_order_id": merchant_order_id}
            )
            if not result.data:
                return False

            payment = Payment(**result.data[0])

            # Update status
            if status == "SUCCESS":
                payment.status = PaymentStatus.SUCCESS
            elif status == "FAILED":
                payment.status = PaymentStatus.FAILED

            await self.db.update(
                "payments", {"status": payment.status}, {"id": payment.id}
            )

            # Create subscription if payment successful
            if payment.status == PaymentStatus.SUCCESS:
                await self._create_subscription(payment)

            return True

        except Exception as e:
            logger.error(f"Failed to handle webhook: {e}")
            return False

    async def _create_subscription(self, payment: Payment) -> Optional[Subscription]:
        """Create subscription after successful payment"""
        try:
            # Calculate period end
            from datetime import datetime, timedelta

            current_period_end = datetime.utcnow() + timedelta(days=30)

            subscription_data = {
                "workspace_id": payment.workspace_id,
                "payment_id": payment.id,
                "plan": payment.plan,
                "status": SubscriptionStatus.ACTIVE,
                "amount": payment.amount,
                "currency": payment.currency,
                "interval": "month",
                "current_period_end": current_period_end.isoformat(),
            }

            result = await self.db.insert("subscriptions", subscription_data)
            if result.data:
                return Subscription(**result.data[0])
            return None

        except Exception as e:
            logger.error(f"Failed to create subscription: {e}")
            return None


# Global instance
payment_service = PaymentService()


def get_payment_service() -> PaymentService:
    """Get payment service instance"""
    return payment_service
