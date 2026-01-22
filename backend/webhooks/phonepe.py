"""
PhonePe webhook handler for payment processing.
Handles payment callbacks, refunds, and other PhonePe events.
"""

import hashlib
import hmac
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from backend.config.settings import get_settings
from .handler import WebhookHandler
from .models import WebhookEvent
from .verification import verify_webhook
from backend.services.phonepe_webhook_service import PhonePeWebhookService
from backend.services.phonepe_auth import get_phonepe_auth_client

logger = logging.getLogger(__name__)

auth_client = get_phonepe_auth_client()
webhook_service = PhonePeWebhookService(auth_client)

class PhonePeWebhookHandler:
    """Handler for PhonePe webhooks."""

    def __init__(self):
        """Initialize PhonePe webhook handler."""
        self.settings = get_settings()
        self.webhook_handler = WebhookHandler()

        # Register event handlers
        self._register_handlers()

    def _register_handlers(self):
        """Register PhonePe event handlers."""
        self.webhook_handler.register_handler(
            "phonepe.payment_success", self.handle_payment_success
        )
        self.webhook_handler.register_handler(
            "phonepe.payment_failed", self.handle_payment_failed
        )
        self.webhook_handler.register_handler(
            "phonepe.payment_pending", self.handle_payment_pending
        )
        self.webhook_handler.register_handler(
            "phonepe.refund_initiated", self.handle_refund_initiated
        )
        self.webhook_handler.register_handler(
            "phonepe.refund_completed", self.handle_refund_completed
        )
        self.webhook_handler.register_handler(
            "phonepe.refund_failed", self.handle_refund_failed
        )
        self.webhook_handler.register_handler(
            "phonepe.settlement_completed", self.handle_settlement_completed
        )

    async def handle_webhook(
        self, payload: Dict[str, Any], signature: str
    ) -> Dict[str, Any]:
        """
        Handle incoming PhonePe webhook.

        Args:
            payload: Webhook payload
            signature: X-VERIFY signature header

        Returns:
            Response dict with status and details
        """
        try:
            # Verify webhook signature
            if not self._verify_signature(payload, signature):
                logger.error("PhonePe webhook signature verification failed")
                return {
                    "status": "error",
                    "message": "Invalid signature",
                    "code": "INVALID_SIGNATURE",
                }

            # Create webhook event
            event = self._create_webhook_event(payload)

            # Handle the event
            result = await webhook_service.process_webhook(payload, {"X-VERIFY": signature})

            logger.info(f"PhonePe webhook handled successfully: {event.event_id}")
            return {
                "status": "success",
                "message": "Webhook processed successfully",
                "event_id": event.event_id,
                "result": result,
            }

        except Exception as e:
            logger.error(f"Error handling PhonePe webhook: {e}")
            return {
                "status": "error",
                "message": "Internal server error",
                "code": "INTERNAL_ERROR",
            }

    def _verify_signature(self, payload: Dict[str, Any], signature: str) -> bool:
        """
        Verify PhonePe webhook signature.

        Args:
            payload: Webhook payload
            signature: X-VERIFY signature

        Returns:
            True if signature is valid
        """
        try:
            # Get the salt/index from payload
            salt = payload.get("data", {}).get("salt", "")
            index = payload.get("data", {}).get("index", "")

            # Get the checksum from payload
            checksum = payload.get("data", {}).get("checksum", "")

            if not salt or not index or not checksum:
                logger.error("Missing required fields for signature verification")
                return False

            # Get the PhonePe webhook secret
            webhook_secret = self.settings.PHONEPE_WEBHOOK_SECRET
            if not webhook_secret:
                logger.error("PhonePe webhook secret not configured")
                return False

            # Create the string to hash
            string_to_hash = f"{salt}{index}{webhook_secret}"

            # Generate SHA256 hash
            sha256_hash = hashlib.sha256(string_to_hash.encode()).hexdigest()

            # Compare with provided checksum
            return sha256_hash == checksum

        except Exception as e:
            logger.error(f"Error verifying PhonePe signature: {e}")
            return False

    def _create_webhook_event(self, payload: Dict[str, Any]) -> WebhookEvent:
        """Create webhook event from PhonePe payload."""
        data = payload.get("data", {})
        event_type = self._map_phonepe_event(data.get("code", ""))

        return WebhookEvent(
            event_id=data.get("transactionId", ""),
            event_type=event_type,
            payload=payload,
            timestamp=datetime.utcnow(),
            source="phonepe",
            user_id=data.get("merchantUserId"),
            workspace_id=data.get("merchantOrderId"),
            data={
                "transaction_id": data.get("transactionId"),
                "merchant_order_id": data.get("merchantOrderId"),
                "amount": data.get("amount"),
                "status": data.get("code"),
                "message": data.get("message"),
                "payment_instrument": data.get("paymentInstrument"),
                "payee_details": data.get("payeeDetails"),
                "payer_details": data.get("payerDetails"),
            },
        )

    def _map_phonepe_event(self, phonepe_code: str) -> str:
        """Map PhonePe status code to internal event type."""
        event_mapping = {
            "PAYMENT_SUCCESS": "phonepe.payment_success",
            "PAYMENT_FAILED": "phonepe.payment_failed",
            "PAYMENT_PENDING": "phonepe.payment_pending",
            "PAYMENT_DECLINED": "phonepe.payment_failed",
            "REFUND_INITIATED": "phonepe.refund_initiated",
            "REFUND_COMPLETED": "phonepe.refund_completed",
            "REFUND_FAILED": "phonepe.refund_failed",
            "SETTLEMENT_COMPLETED": "phonepe.settlement_completed",
            "SETTLEMENT_FAILED": "phonepe.settlement_failed",
        }

        return event_mapping.get(phonepe_code, "phonepe.unknown")

    async def handle_payment_success(self, event: WebhookEvent) -> Dict[str, Any]:
        """Handle successful payment."""
        try:
            payload = event.payload
            data = payload.get("data", {})

            transaction_id = data.get("transactionId")
            merchant_order_id = data.get("merchantOrderId")
            amount = data.get("amount")

            logger.info(
                f"Payment successful: {transaction_id} for order {merchant_order_id}"
            )

            # Update payment status in database
            await self._update_payment_status(
                transaction_id=transaction_id,
                order_id=merchant_order_id,
                status="completed",
                amount=amount,
                metadata=data,
            )

            # Grant access to user/workspace
            await self._grant_access(
                user_id=event.user_id,
                workspace_id=event.workspace_id,
                transaction_id=transaction_id,
                amount=amount,
            )

            # Send confirmation notification
            await self._send_payment_confirmation(
                user_id=event.user_id, transaction_id=transaction_id, amount=amount
            )

            return {
                "action": "payment_completed",
                "transaction_id": transaction_id,
                "order_id": merchant_order_id,
                "amount": amount,
                "status": "success",
            }

        except Exception as e:
            logger.error(f"Error handling payment success: {e}")
            raise

    async def handle_payment_failed(self, event: WebhookEvent) -> Dict[str, Any]:
        """Handle failed payment."""
        try:
            payload = event.payload
            data = payload.get("data", {})

            transaction_id = data.get("transactionId")
            merchant_order_id = data.get("merchantOrderId")
            failure_reason = data.get("message", "Unknown reason")

            logger.warning(
                f"Payment failed: {transaction_id} for order {merchant_order_id} - {failure_reason}"
            )

            # Update payment status in database
            await self._update_payment_status(
                transaction_id=transaction_id,
                order_id=merchant_order_id,
                status="failed",
                failure_reason=failure_reason,
                metadata=data,
            )

            # Send failure notification
            await self._send_payment_failure_notification(
                user_id=event.user_id,
                transaction_id=transaction_id,
                reason=failure_reason,
            )

            return {
                "action": "payment_failed",
                "transaction_id": transaction_id,
                "order_id": merchant_order_id,
                "reason": failure_reason,
                "status": "failed",
            }

        except Exception as e:
            logger.error(f"Error handling payment failure: {e}")
            raise

    async def handle_payment_pending(self, event: WebhookEvent) -> Dict[str, Any]:
        """Handle pending payment."""
        try:
            payload = event.payload
            data = payload.get("data", {})

            transaction_id = data.get("transactionId")
            merchant_order_id = data.get("merchantOrderId")

            logger.info(
                f"Payment pending: {transaction_id} for order {merchant_order_id}"
            )

            # Update payment status in database
            await self._update_payment_status(
                transaction_id=transaction_id,
                order_id=merchant_order_id,
                status="pending",
                metadata=data,
            )

            return {
                "action": "payment_pending",
                "transaction_id": transaction_id,
                "order_id": merchant_order_id,
                "status": "pending",
            }

        except Exception as e:
            logger.error(f"Error handling payment pending: {e}")
            raise

    async def handle_refund_initiated(self, event: WebhookEvent) -> Dict[str, Any]:
        """Handle refund initiation."""
        try:
            payload = event.payload
            data = payload.get("data", {})

            refund_id = data.get("refundId")
            transaction_id = data.get("transactionId")
            amount = data.get("amount")

            logger.info(
                f"Refund initiated: {refund_id} for transaction {transaction_id}"
            )

            # Update refund status in database
            await self._update_refund_status(
                refund_id=refund_id,
                transaction_id=transaction_id,
                status="initiated",
                amount=amount,
                metadata=data,
            )

            return {
                "action": "refund_initiated",
                "refund_id": refund_id,
                "transaction_id": transaction_id,
                "amount": amount,
                "status": "initiated",
            }

        except Exception as e:
            logger.error(f"Error handling refund initiation: {e}")
            raise

    async def handle_refund_completed(self, event: WebhookEvent) -> Dict[str, Any]:
        """Handle completed refund."""
        try:
            payload = event.payload
            data = payload.get("data", {})

            refund_id = data.get("refundId")
            transaction_id = data.get("transactionId")
            amount = data.get("amount")

            logger.info(
                f"Refund completed: {refund_id} for transaction {transaction_id}"
            )

            # Update refund status in database
            await self._update_refund_status(
                refund_id=refund_id,
                transaction_id=transaction_id,
                status="completed",
                amount=amount,
                metadata=data,
            )

            # Revoke access if applicable
            await self._revoke_access_if_needed(
                user_id=event.user_id,
                workspace_id=event.workspace_id,
                transaction_id=transaction_id,
            )

            # Send refund confirmation
            await self._send_refund_confirmation(
                user_id=event.user_id, refund_id=refund_id, amount=amount
            )

            return {
                "action": "refund_completed",
                "refund_id": refund_id,
                "transaction_id": transaction_id,
                "amount": amount,
                "status": "completed",
            }

        except Exception as e:
            logger.error(f"Error handling refund completion: {e}")
            raise

    async def handle_refund_failed(self, event: WebhookEvent) -> Dict[str, Any]:
        """Handle failed refund."""
        try:
            payload = event.payload
            data = payload.get("data", {})

            refund_id = data.get("refundId")
            transaction_id = data.get("transactionId")
            failure_reason = data.get("message", "Unknown reason")

            logger.warning(
                f"Refund failed: {refund_id} for transaction {transaction_id} - {failure_reason}"
            )

            # Update refund status in database
            await self._update_refund_status(
                refund_id=refund_id,
                transaction_id=transaction_id,
                status="failed",
                failure_reason=failure_reason,
                metadata=data,
            )

            return {
                "action": "refund_failed",
                "refund_id": refund_id,
                "transaction_id": transaction_id,
                "reason": failure_reason,
                "status": "failed",
            }

        except Exception as e:
            logger.error(f"Error handling refund failure: {e}")
            raise

    async def handle_settlement_completed(self, event: WebhookEvent) -> Dict[str, Any]:
        """Handle settlement completion."""
        try:
            payload = event.payload
            data = payload.get("data", {})

            settlement_id = data.get("settlementId")
            amount = data.get("amount")

            logger.info(f"Settlement completed: {settlement_id} for amount {amount}")

            # Update settlement records
            await self._update_settlement_status(
                settlement_id=settlement_id,
                status="completed",
                amount=amount,
                metadata=data,
            )

            return {
                "action": "settlement_completed",
                "settlement_id": settlement_id,
                "amount": amount,
                "status": "completed",
            }

        except Exception as e:
            logger.error(f"Error handling settlement completion: {e}")
            raise

    # Helper methods
    async def _update_payment_status(
        self,
        transaction_id: str,
        order_id: str,
        status: str,
        amount: int = None,
        failure_reason: str = None,
        metadata: dict = None,
    ):
        """Update payment status in database."""
        logger.info(f"Updating payment status: {transaction_id} -> {status}")
        try:
            from db.repositories.payment import PaymentRepository
            repo = PaymentRepository()
            await repo.update_status(
                transaction_id=transaction_id,
                status=status.upper(),
                payment_instrument=metadata.get("paymentInstrument") if metadata else None
            )
        except Exception as e:
            logger.error(f"Failed to update payment status in DB: {e}")

    async def _grant_access(
        self, user_id: str, workspace_id: str, transaction_id: str, amount: int
    ):
        """Grant access to user/workspace after successful payment."""
        logger.info(f"Granting access to user {user_id} for workspace {workspace_id}")
        try:
            from backend.core.supabase_mgr import get_supabase_client
            supabase = get_supabase_client()
            
            # 1. Update user onboarding status
            # Check both 'users' and 'profiles' tables for redundancy safety
            if user_id:
                supabase.table("users").update({"onboarding_status": "active"}).eq("id", user_id).execute()
                supabase.table("profiles").update({"onboarding_status": "active"}).eq("id", user_id).execute()
            
            # 2. Update subscription status
            if user_id:
                supabase.table("subscriptions").update({
                    "status": "active",
                    "current_period_start": datetime.utcnow().isoformat()
                }).eq("user_id", user_id).execute()
                
        except Exception as e:
            logger.error(f"Failed to grant access in DB: {e}")

    async def _revoke_access_if_needed(
        self, user_id: str, workspace_id: str, transaction_id: str
    ):
        """Revoke access if refund was processed."""
        # This would integrate with your access control service
        logger.info(
            f"Checking access revocation for user {user_id} workspace {workspace_id}"
        )
        pass

    async def _send_payment_confirmation(
        self, user_id: str, transaction_id: str, amount: int
    ):
        """Send payment confirmation notification."""
        # This would integrate with your notification service
        logger.info(f"Sending payment confirmation to user {user_id}")
        pass

    async def _send_payment_failure_notification(
        self, user_id: str, transaction_id: str, reason: str
    ):
        """Send payment failure notification."""
        # This would integrate with your notification service
        logger.info(f"Sending payment failure notification to user {user_id}")
        pass

    async def _send_refund_confirmation(
        self, user_id: str, refund_id: str, amount: int
    ):
        """Send refund confirmation notification."""
        # This would integrate with your notification service
        logger.info(f"Sending refund confirmation to user {user_id}")
        pass


# Global PhonePe webhook handler instance
_phonepe_handler: PhonePeWebhookHandler = None


def get_phonepe_webhook_handler() -> PhonePeWebhookHandler:
    """Get the global PhonePe webhook handler instance."""
    global _phonepe_handler
    if _phonepe_handler is None:
        _phonepe_handler = PhonePeWebhookHandler()
    return _phonepe_handler
