"""
Stripe webhook handlers for Raptorflow.

Handles Stripe payment events, subscription events,
and billing events with proper processing and error handling.
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..infrastructure.cloud_monitoring import get_cloud_monitoring
from ..infrastructure.logging import get_cloud_logging
from .handler import WebhookHandler, get_webhook_handler
from .models import WebhookEvent, WebhookResponse

logger = logging.getLogger(__name__)


@dataclass
class StripePaymentEvent:
    """Stripe payment event data."""

    payment_intent_id: str
    customer_id: str
    amount: int
    currency: str
    status: str
    metadata: Dict[str, Any]
    timestamp: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "payment_intent_id": self.payment_intent_id,
            "customer_id": self.customer_id,
            "amount": self.amount,
            "currency": self.currency,
            "status": self.status,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class StripeSubscriptionEvent:
    """Stripe subscription event data."""

    subscription_id: str
    customer_id: str
    status: str
    price_id: str
    quantity: int
    metadata: Dict[str, Any]
    timestamp: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "subscription_id": self.subscription_id,
            "customer_id": self.customer_id,
            "status": self.status,
            "price_id": self.price_id,
            "quantity": self.quantity,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class StripeInvoiceEvent:
    """Stripe invoice event data."""

    invoice_id: str
    customer_id: str
    subscription_id: Optional[str]
    amount_due: int
    currency: str
    status: str
    metadata: Dict[str, Any]
    timestamp: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "invoice_id": self.invoice_id,
            "customer_id": self.customer_id,
            "subscription_id": self.subscription_id,
            "amount_due": self.amount_due,
            "currency": self.currency,
            "status": self.status,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }


class StripeWebhookHandler:
    """Stripe webhook event handler."""

    def __init__(self):
        self.logger = logging.getLogger("stripe_webhook_handler")
        self.logging = get_cloud_logging()
        self.monitoring = get_cloud_monitoring()

        # Register handlers with main webhook handler
        self._register_handlers()

    def _register_handlers(self):
        """Register Stripe event handlers."""
        webhook_handler = get_webhook_handler()

        # Payment events
        webhook_handler.register_handler(
            "stripe.payment_intent.succeeded", self.handle_payment_succeeded
        )
        webhook_handler.register_handler(
            "stripe.payment_intent.payment_failed", self.handle_payment_failed
        )
        webhook_handler.register_handler(
            "stripe.payment_intent.canceled", self.handle_payment_canceled
        )
        webhook_handler.register_handler(
            "stripe.payment_intent.requires_action", self.handle_payment_requires_action
        )

        # Charge events
        webhook_handler.register_handler(
            "stripe.charge.succeeded", self.handle_charge_succeeded
        )
        webhook_handler.register_handler(
            "stripe.charge.failed", self.handle_charge_failed
        )
        webhook_handler.register_handler(
            "stripe.charge.dispute.created", self.handle_charge_dispute_created
        )

        # Subscription events
        webhook_handler.register_handler(
            "stripe.customer.subscription.created", self.handle_subscription_created
        )
        webhook_handler.register_handler(
            "stripe.customer.subscription.updated", self.handle_subscription_updated
        )
        webhook_handler.register_handler(
            "stripe.customer.subscription.deleted", self.handle_subscription_deleted
        )
        webhook_handler.register_handler(
            "stripe.customer.subscription.trial_will_end",
            self.handle_subscription_trial_will_end,
        )

        # Invoice events
        webhook_handler.register_handler(
            "stripe.invoice.created", self.handle_invoice_created
        )
        webhook_handler.register_handler(
            "stripe.invoice.finalized", self.handle_invoice_finalized
        )
        webhook_handler.register_handler(
            "stripe.invoice.payment_succeeded", self.handle_invoice_payment_succeeded
        )
        webhook_handler.register_handler(
            "stripe.invoice.payment_failed", self.handle_invoice_payment_failed
        )
        webhook_handler.register_handler(
            "stripe.invoice.voided", self.handle_invoice_voided
        )

        # Customer events
        webhook_handler.register_handler(
            "stripe.customer.created", self.handle_customer_created
        )
        webhook_handler.register_handler(
            "stripe.customer.updated", self.handle_customer_updated
        )
        webhook_handler.register_handler(
            "stripe.customer.deleted", self.handle_customer_deleted
        )

        # Payment method events
        webhook_handler.register_handler(
            "stripe.payment_method.attached", self.handle_payment_method_attached
        )
        webhook_handler.register_handler(
            "stripe.payment_method.detached", self.handle_payment_method_detached
        )
        webhook_handler.register_handler(
            "stripe.payment_method.updated", self.handle_payment_method_updated
        )

    async def handle_payment_succeeded(self, event: WebhookEvent) -> Dict[str, Any]:
        """Handle payment succeeded event."""
        try:
            payment_event = self._parse_payment_event(event.data)

            # Log event
            await self.logging.log_structured(
                "INFO",
                f"Stripe payment succeeded: {payment_event.payment_intent_id}",
                {
                    "payment_intent_id": payment_event.payment_intent_id,
                    "customer_id": payment_event.customer_id,
                    "amount": payment_event.amount,
                    "currency": payment_event.currency,
                },
            )

            # Update payment status
            from ..billing.stripe_service import get_stripe_service

            stripe_service = get_stripe_service()

            await stripe_service.update_payment_status(
                payment_event.payment_intent_id, "succeeded", payment_event.metadata
            )

            # Process successful payment
            await self._process_successful_payment(payment_event)

            # Record metrics
            await self.monitoring.record_metric(
                "stripe_payment_succeeded",
                payment_event.amount,
                {"currency": payment_event.currency},
            )

            return {
                "status": "success",
                "payment_intent_id": payment_event.payment_intent_id,
                "customer_id": payment_event.customer_id,
                "amount": payment_event.amount,
                "action": "payment_processed",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle payment succeeded: {e}")
            return {"status": "error", "error": str(e)}

    async def handle_payment_failed(self, event: WebhookEvent) -> Dict[str, Any]:
        """Handle payment failed event."""
        try:
            payment_event = self._parse_payment_event(event.data)

            # Log event
            await self.logging.log_structured(
                "WARNING",
                f"Stripe payment failed: {payment_event.payment_intent_id}",
                {
                    "payment_intent_id": payment_event.payment_intent_id,
                    "customer_id": payment_event.customer_id,
                    "amount": payment_event.amount,
                    "currency": payment_event.currency,
                },
            )

            # Update payment status
            from ..billing.stripe_service import get_stripe_service

            stripe_service = get_stripe_service()

            await stripe_service.update_payment_status(
                payment_event.payment_intent_id, "failed", payment_event.metadata
            )

            # Process failed payment
            await self._process_failed_payment(payment_event)

            # Record metrics
            await self.monitoring.record_metric(
                "stripe_payment_failed",
                payment_event.amount,
                {"currency": payment_event.currency},
            )

            return {
                "status": "success",
                "payment_intent_id": payment_event.payment_intent_id,
                "customer_id": payment_event.customer_id,
                "action": "payment_failure_processed",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle payment failed: {e}")
            return {"status": "error", "error": str(e)}

    async def handle_payment_canceled(self, event: WebhookEvent) -> Dict[str, Any]:
        """Handle payment canceled event."""
        try:
            payment_event = self._parse_payment_event(event.data)

            # Update payment status
            from ..billing.stripe_service import get_stripe_service

            stripe_service = get_stripe_service()

            await stripe_service.update_payment_status(
                payment_event.payment_intent_id, "canceled", payment_event.metadata
            )

            return {
                "status": "success",
                "payment_intent_id": payment_event.payment_intent_id,
                "action": "payment_canceled",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle payment canceled: {e}")
            return {"status": "error", "error": str(e)}

    async def handle_payment_requires_action(
        self, event: WebhookEvent
    ) -> Dict[str, Any]:
        """Handle payment requires action event."""
        try:
            payment_event = self._parse_payment_event(event.data)

            # Update payment status
            from ..billing.stripe_service import get_stripe_service

            stripe_service = get_stripe_service()

            await stripe_service.update_payment_status(
                payment_event.payment_intent_id,
                "requires_action",
                payment_event.metadata,
            )

            # Send notification to user
            await self._send_payment_action_notification(payment_event)

            return {
                "status": "success",
                "payment_intent_id": payment_event.payment_intent_id,
                "action": "payment_action_required",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle payment requires action: {e}")
            return {"status": "error", "error": str(e)}

    async def handle_charge_succeeded(self, event: WebhookEvent) -> Dict[str, Any]:
        """Handle charge succeeded event."""
        try:
            charge_data = event.data.get("object", {})

            # Update charge status
            from ..billing.stripe_service import get_stripe_service

            stripe_service = get_stripe_service()

            await stripe_service.update_charge_status(
                charge_data.get("id"), "succeeded", charge_data
            )

            return {
                "status": "success",
                "charge_id": charge_data.get("id"),
                "action": "charge_processed",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle charge succeeded: {e}")
            return {"status": "error", "error": str(e)}

    async def handle_charge_failed(self, event: WebhookEvent) -> Dict[str, Any]:
        """Handle charge failed event."""
        try:
            charge_data = event.data.get("object", {})

            # Update charge status
            from ..billing.stripe_service import get_stripe_service

            stripe_service = get_stripe_service()

            await stripe_service.update_charge_status(
                charge_data.get("id"), "failed", charge_data
            )

            return {
                "status": "success",
                "charge_id": charge_data.get("id"),
                "action": "charge_failure_processed",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle charge failed: {e}")
            return {"status": "error", "error": str(e)}

    async def handle_charge_dispute_created(
        self, event: WebhookEvent
    ) -> Dict[str, Any]:
        """Handle charge dispute created event."""
        try:
            dispute_data = event.data.get("object", {})

            # Create dispute record
            from ..billing.stripe_service import get_stripe_service

            stripe_service = get_stripe_service()

            await stripe_service.create_dispute_record(dispute_data)

            # Send alert notification
            await self._send_dispute_alert(dispute_data)

            return {
                "status": "success",
                "dispute_id": dispute_data.get("id"),
                "action": "dispute_created",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle charge dispute created: {e}")
            return {"status": "error", "error": str(e)}

    async def handle_subscription_created(self, event: WebhookEvent) -> Dict[str, Any]:
        """Handle subscription created event."""
        try:
            subscription_event = self._parse_subscription_event(event.data)

            # Create subscription in local system
            from ..billing.stripe_service import get_stripe_service

            stripe_service = get_stripe_service()

            await stripe_service.create_subscription_from_stripe(subscription_event)

            # Send welcome notification
            await self._send_subscription_welcome_notification(subscription_event)

            # Record metrics
            await self.monitoring.record_metric(
                "stripe_subscription_created",
                1,
                {"price_id": subscription_event.price_id},
            )

            return {
                "status": "success",
                "subscription_id": subscription_event.subscription_id,
                "customer_id": subscription_event.customer_id,
                "action": "subscription_created",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle subscription created: {e}")
            return {"status": "error", "error": str(e)}

    async def handle_subscription_updated(self, event: WebhookEvent) -> Dict[str, Any]:
        """Handle subscription updated event."""
        try:
            subscription_event = self._parse_subscription_event(event.data)

            # Update subscription in local system
            from ..billing.stripe_service import get_stripe_service

            stripe_service = get_stripe_service()

            await stripe_service.update_subscription_from_stripe(subscription_event)

            return {
                "status": "success",
                "subscription_id": subscription_event.subscription_id,
                "action": "subscription_updated",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle subscription updated: {e}")
            return {"status": "error", "error": str(e)}

    async def handle_subscription_deleted(self, event: WebhookEvent) -> Dict[str, Any]:
        """Handle subscription deleted event."""
        try:
            subscription_event = self._parse_subscription_event(event.data)

            # Delete subscription from local system
            from ..billing.stripe_service import get_stripe_service

            stripe_service = get_stripe_service()

            await stripe_service.delete_subscription_from_stripe(
                subscription_event.subscription_id
            )

            # Send cancellation notification
            await self._send_subscription_cancellation_notification(subscription_event)

            # Record metrics
            await self.monitoring.record_metric(
                "stripe_subscription_deleted",
                1,
                {"customer_id": subscription_event.customer_id},
            )

            return {
                "status": "success",
                "subscription_id": subscription_event.subscription_id,
                "action": "subscription_deleted",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle subscription deleted: {e}")
            return {"status": "error", "error": str(e)}

    async def handle_subscription_trial_will_end(
        self, event: WebhookEvent
    ) -> Dict[str, Any]:
        """Handle subscription trial will end event."""
        try:
            subscription_event = self._parse_subscription_event(event.data)

            # Send trial ending notification
            await self._send_trial_ending_notification(subscription_event)

            return {
                "status": "success",
                "subscription_id": subscription_event.subscription_id,
                "action": "trial_ending_notification_sent",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle subscription trial will end: {e}")
            return {"status": "error", "error": str(e)}

    async def handle_invoice_created(self, event: WebhookEvent) -> Dict[str, Any]:
        """Handle invoice created event."""
        try:
            invoice_event = self._parse_invoice_event(event.data)

            # Create invoice in local system
            from ..billing.stripe_service import get_stripe_service

            stripe_service = get_stripe_service()

            await stripe_service.create_invoice_from_stripe(invoice_event)

            return {
                "status": "success",
                "invoice_id": invoice_event.invoice_id,
                "action": "invoice_created",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle invoice created: {e}")
            return {"status": "error", "error": str(e)}

    async def handle_invoice_finalized(self, event: WebhookEvent) -> Dict[str, Any]:
        """Handle invoice finalized event."""
        try:
            invoice_event = self._parse_invoice_event(event.data)

            # Update invoice status
            from ..billing.stripe_service import get_stripe_service

            stripe_service = get_stripe_service()

            await stripe_service.finalize_invoice_from_stripe(invoice_event.invoice_id)

            return {
                "status": "success",
                "invoice_id": invoice_event.invoice_id,
                "action": "invoice_finalized",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle invoice finalized: {e}")
            return {"status": "error", "error": str(e)}

    async def handle_invoice_payment_succeeded(
        self, event: WebhookEvent
    ) -> Dict[str, Any]:
        """Handle invoice payment succeeded event."""
        try:
            invoice_event = self._parse_invoice_event(event.data)

            # Update invoice payment status
            from ..billing.stripe_service import get_stripe_service

            stripe_service = get_stripe_service()

            await stripe_service.update_invoice_payment_status(
                invoice_event.invoice_id, "succeeded"
            )

            # Send payment confirmation
            await self._send_invoice_payment_confirmation(invoice_event)

            # Record metrics
            await self.monitoring.record_metric(
                "stripe_invoice_payment_succeeded",
                invoice_event.amount_due,
                {"currency": invoice_event.currency},
            )

            return {
                "status": "success",
                "invoice_id": invoice_event.invoice_id,
                "action": "invoice_payment_processed",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle invoice payment succeeded: {e}")
            return {"status": "error", "error": str(e)}

    async def handle_invoice_payment_failed(
        self, event: WebhookEvent
    ) -> Dict[str, Any]:
        """Handle invoice payment failed event."""
        try:
            invoice_event = self._parse_invoice_event(event.data)

            # Update invoice payment status
            from ..billing.stripe_service import get_stripe_service

            stripe_service = get_stripe_service()

            await stripe_service.update_invoice_payment_status(
                invoice_event.invoice_id, "failed"
            )

            # Send payment failure notification
            await self._send_invoice_payment_failure_notification(invoice_event)

            return {
                "status": "success",
                "invoice_id": invoice_event.invoice_id,
                "action": "invoice_payment_failure_processed",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle invoice payment failed: {e}")
            return {"status": "error", "error": str(e)}

    async def handle_invoice_voided(self, event: WebhookEvent) -> Dict[str, Any]:
        """Handle invoice voided event."""
        try:
            invoice_event = self._parse_invoice_event(event.data)

            # Update invoice status
            from ..billing.stripe_service import get_stripe_service

            stripe_service = get_stripe_service()

            await stripe_service.update_invoice_status(
                invoice_event.invoice_id, "voided"
            )

            return {
                "status": "success",
                "invoice_id": invoice_event.invoice_id,
                "action": "invoice_voided",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle invoice voided: {e}")
            return {"status": "error", "error": str(e)}

    async def handle_customer_created(self, event: WebhookEvent) -> Dict[str, Any]:
        """Handle customer created event."""
        try:
            customer_data = event.data.get("object", {})

            # Create customer in local system
            from ..billing.stripe_service import get_stripe_service

            stripe_service = get_stripe_service()

            await stripe_service.create_customer_from_stripe(customer_data)

            return {
                "status": "success",
                "customer_id": customer_data.get("id"),
                "action": "customer_created",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle customer created: {e}")
            return {"status": "error", "error": str(e)}

    async def handle_customer_updated(self, event: WebhookEvent) -> Dict[str, Any]:
        """Handle customer updated event."""
        try:
            customer_data = event.data.get("object", {})

            # Update customer in local system
            from ..billing.stripe_service import get_stripe_service

            stripe_service = get_stripe_service()

            await stripe_service.update_customer_from_stripe(customer_data)

            return {
                "status": "success",
                "customer_id": customer_data.get("id"),
                "action": "customer_updated",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle customer updated: {e}")
            return {"status": "error", "error": str(e)}

    async def handle_customer_deleted(self, event: WebhookEvent) -> Dict[str, Any]:
        """Handle customer deleted event."""
        try:
            customer_data = event.data.get("object", {})

            # Delete customer from local system
            from ..billing.stripe_service import get_stripe_service

            stripe_service = get_stripe_service()

            await stripe_service.delete_customer_from_stripe(customer_data.get("id"))

            return {
                "status": "success",
                "customer_id": customer_data.get("id"),
                "action": "customer_deleted",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle customer deleted: {e}")
            return {"status": "error", "error": str(e)}

    async def handle_payment_method_attached(
        self, event: WebhookEvent
    ) -> Dict[str, Any]:
        """Handle payment method attached event."""
        try:
            payment_method_data = event.data.get("object", {})

            # Update customer payment methods
            from ..billing.stripe_service import get_stripe_service

            stripe_service = get_stripe_service()

            await stripe_service.attach_payment_method_to_customer(payment_method_data)

            return {
                "status": "success",
                "payment_method_id": payment_method_data.get("id"),
                "action": "payment_method_attached",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle payment method attached: {e}")
            return {"status": "error", "error": str(e)}

    async def handle_payment_method_detached(
        self, event: WebhookEvent
    ) -> Dict[str, Any]:
        """Handle payment method detached event."""
        try:
            payment_method_data = event.data.get("object", {})

            # Remove payment method from customer
            from ..billing.stripe_service import get_stripe_service

            stripe_service = get_stripe_service()

            await stripe_service.detach_payment_method_from_customer(
                payment_method_data
            )

            return {
                "status": "success",
                "payment_method_id": payment_method_data.get("id"),
                "action": "payment_method_detached",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle payment method detached: {e}")
            return {"status": "error", "error": str(e)}

    async def handle_payment_method_updated(
        self, event: WebhookEvent
    ) -> Dict[str, Any]:
        """Handle payment method updated event."""
        try:
            payment_method_data = event.data.get("object", {})

            # Update payment method
            from ..billing.stripe_service import get_stripe_service

            stripe_service = get_stripe_service()

            await stripe_service.update_payment_method_from_stripe(payment_method_data)

            return {
                "status": "success",
                "payment_method_id": payment_method_data.get("id"),
                "action": "payment_method_updated",
            }

        except Exception as e:
            self.logger.error(f"Failed to handle payment method updated: {e}")
            return {"status": "error", "error": str(e)}

    def _parse_payment_event(self, data: Dict[str, Any]) -> StripePaymentEvent:
        """Parse Stripe payment event."""
        payment_intent = data.get("object", {})

        return StripePaymentEvent(
            payment_intent_id=payment_intent.get("id"),
            customer_id=payment_intent.get("customer"),
            amount=payment_intent.get("amount", 0),
            currency=payment_intent.get("currency", ""),
            status=payment_intent.get("status", ""),
            metadata=payment_intent.get("metadata", {}),
            timestamp=datetime.utcnow(),
        )

    def _parse_subscription_event(
        self, data: Dict[str, Any]
    ) -> StripeSubscriptionEvent:
        """Parse Stripe subscription event."""
        subscription = data.get("object", {})

        # Get price info from items
        price_id = ""
        quantity = 1
        items = subscription.get("items", {}).get("data", [])
        if items:
            first_item = items[0]
            price_id = first_item.get("price", {}).get("id", "")
            quantity = first_item.get("quantity", 1)

        return StripeSubscriptionEvent(
            subscription_id=subscription.get("id"),
            customer_id=subscription.get("customer"),
            status=subscription.get("status", ""),
            price_id=price_id,
            quantity=quantity,
            metadata=subscription.get("metadata", {}),
            timestamp=datetime.utcnow(),
        )

    def _parse_invoice_event(self, data: Dict[str, Any]) -> StripeInvoiceEvent:
        """Parse Stripe invoice event."""
        invoice = data.get("object", {})

        return StripeInvoiceEvent(
            invoice_id=invoice.get("id"),
            customer_id=invoice.get("customer"),
            subscription_id=invoice.get("subscription"),
            amount_due=invoice.get("amount_due", 0),
            currency=invoice.get("currency", ""),
            status=invoice.get("status", ""),
            metadata=invoice.get("metadata", {}),
            timestamp=datetime.utcnow(),
        )

    async def _process_successful_payment(self, payment_event: StripePaymentEvent):
        """Process successful payment."""
        try:
            # Get workspace from metadata
            workspace_id = payment_event.metadata.get("workspace_id")

            if workspace_id:
                # Update workspace usage
                from ..billing.billing_service import get_billing_service

                billing_service = get_billing_service()

                await billing_service.record_payment(
                    workspace_id,
                    payment_event.payment_intent_id,
                    payment_event.amount,
                    payment_event.currency,
                )

                # Check usage limits
                await billing_service.check_usage_limits(workspace_id)

        except Exception as e:
            self.logger.error(f"Failed to process successful payment: {e}")

    async def _process_failed_payment(self, payment_event: StripePaymentEvent):
        """Process failed payment."""
        try:
            # Get workspace from metadata
            workspace_id = payment_event.metadata.get("workspace_id")

            if workspace_id:
                # Handle payment failure
                from ..billing.billing_service import get_billing_service

                billing_service = get_billing_service()

                await billing_service.handle_payment_failure(
                    workspace_id, payment_event.payment_intent_id
                )

                # Send failure notification
                from ..notifications.notification_service import (
                    get_notification_service,
                )

                notification_service = get_notification_service()

                await notification_service.send_payment_failure_notification(
                    workspace_id, payment_event.payment_intent_id
                )

        except Exception as e:
            self.logger.error(f"Failed to process failed payment: {e}")

    async def _send_payment_action_notification(
        self, payment_event: StripePaymentEvent
    ):
        """Send payment action required notification."""
        try:
            workspace_id = payment_event.metadata.get("workspace_id")

            if workspace_id:
                from ..notifications.notification_service import (
                    get_notification_service,
                )

                notification_service = get_notification_service()

                await notification_service.send_payment_action_notification(
                    workspace_id, payment_event.payment_intent_id
                )

        except Exception as e:
            self.logger.error(f"Failed to send payment action notification: {e}")

    async def _send_dispute_alert(self, dispute_data: Dict[str, Any]):
        """Send dispute alert to administrators."""
        try:
            from ..notifications.notification_service import get_notification_service

            notification_service = get_notification_service()

            await notification_service.send_dispute_alert(dispute_data)

        except Exception as e:
            self.logger.error(f"Failed to send dispute alert: {e}")

    async def _send_subscription_welcome_notification(
        self, subscription_event: StripeSubscriptionEvent
    ):
        """Send subscription welcome notification."""
        try:
            from ..notifications.notification_service import get_notification_service

            notification_service = get_notification_service()

            await notification_service.send_subscription_welcome_notification(
                subscription_event.customer_id, subscription_event.subscription_id
            )

        except Exception as e:
            self.logger.error(f"Failed to send subscription welcome notification: {e}")

    async def _send_subscription_cancellation_notification(
        self, subscription_event: StripeSubscriptionEvent
    ):
        """Send subscription cancellation notification."""
        try:
            from ..notifications.notification_service import get_notification_service

            notification_service = get_notification_service()

            await notification_service.send_subscription_cancellation_notification(
                subscription_event.customer_id, subscription_event.subscription_id
            )

        except Exception as e:
            self.logger.error(
                f"Failed to send subscription cancellation notification: {e}"
            )

    async def _send_trial_ending_notification(
        self, subscription_event: StripeSubscriptionEvent
    ):
        """Send trial ending notification."""
        try:
            from ..notifications.notification_service import get_notification_service

            notification_service = get_notification_service()

            await notification_service.send_trial_ending_notification(
                subscription_event.customer_id, subscription_event.subscription_id
            )

        except Exception as e:
            self.logger.error(f"Failed to send trial ending notification: {e}")

    async def _send_invoice_payment_confirmation(
        self, invoice_event: StripeInvoiceEvent
    ):
        """Send invoice payment confirmation."""
        try:
            from ..notifications.notification_service import get_notification_service

            notification_service = get_notification_service()

            await notification_service.send_invoice_payment_confirmation(
                invoice_event.customer_id,
                invoice_event.invoice_id,
                invoice_event.amount_due,
                invoice_event.currency,
            )

        except Exception as e:
            self.logger.error(f"Failed to send invoice payment confirmation: {e}")

    async def _send_invoice_payment_failure_notification(
        self, invoice_event: StripeInvoiceEvent
    ):
        """Send invoice payment failure notification."""
        try:
            from ..notifications.notification_service import get_notification_service

            notification_service = get_notification_service()

            await notification_service.send_invoice_payment_failure_notification(
                invoice_event.customer_id, invoice_event.invoice_id
            )

        except Exception as e:
            self.logger.error(
                f"Failed to send invoice payment failure notification: {e}"
            )


# Global Stripe webhook handler instance
_stripe_webhook_handler: Optional[StripeWebhookHandler] = None


def get_stripe_webhook_handler() -> StripeWebhookHandler:
    """Get the global Stripe webhook handler instance."""
    global _stripe_webhook_handler
    if _stripe_webhook_handler is None:
        _stripe_webhook_handler = StripeWebhookHandler()
    return _stripe_webhook_handler


# Export all components
__all__ = [
    "StripeWebhookHandler",
    "StripePaymentEvent",
    "StripeSubscriptionEvent",
    "StripeInvoiceEvent",
    "get_stripe_webhook_handler",
]
