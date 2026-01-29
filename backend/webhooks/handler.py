"""
Webhook handler for Raptorflow.

Provides webhook event processing, routing, and delivery
for external integrations like Supabase, Stripe, and PhonePe.
"""

import asyncio
import hashlib
import hmac
import json
import logging
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Union

from infrastructure.cloud_monitoring import get_cloud_monitoring
from infrastructure.logging import get_cloud_logging
from .models import (
    WebhookConfig,
    WebhookDelivery,
    WebhookEvent,
    WebhookEventType,
    WebhookResponse,
    WebhookRetry,
    WebhookSignature,
)
from verification import WebhookVerifier, get_webhook_verifier

logger = logging.getLogger(__name__)


@dataclass
class WebhookProcessingResult:
    """Result of webhook processing."""

    event_id: str
    processed: bool
    response_status: int
    response_body: str
    processing_time_ms: float
    error: Optional[str] = None
    retry_scheduled: bool = False
    retry_count: int = 0


class WebhookHandler:
    """Main webhook handler for processing incoming webhook events."""

    def __init__(self):
        self.logger = logging.getLogger("webhook_handler")
        self.logging = get_cloud_logging()
        self.monitoring = get_cloud_monitoring()
        self.verifier = get_webhook_verifier()

        # Event handlers registry
        self.event_handlers: Dict[str, List[Callable]] = {}

        # Webhook configurations
        self.webhook_configs: Dict[str, WebhookConfig] = {}

        # Delivery tracking
        self.delivery_attempts: Dict[str, int] = {}

        # Initialize default handlers
        self._initialize_default_handlers()

    def _initialize_default_handlers(self):
        """Initialize default webhook handlers."""
        # Supabase handlers
        self.register_handler(
            "supabase.user.created", self._handle_supabase_user_created
        )
        self.register_handler(
            "supabase.user.updated", self._handle_supabase_user_updated
        )
        self.register_handler(
            "supabase.user.deleted", self._handle_supabase_user_deleted
        )
        self.register_handler("supabase.auth.login", self._handle_supabase_auth_login)
        self.register_handler("supabase.auth.logout", self._handle_supabase_auth_logout)

        # Stripe handlers
        self.register_handler(
            "stripe.payment_intent.succeeded", self._handle_stripe_payment_succeeded
        )
        self.register_handler(
            "stripe.payment_intent.failed", self._handle_stripe_payment_failed
        )
        self.register_handler(
            "stripe.invoice.created", self._handle_stripe_invoice_created
        )
        self.register_handler(
            "stripe.invoice.payment_succeeded",
            self._handle_stripe_invoice_payment_succeeded,
        )
        self.register_handler(
            "stripe.subscription.created", self._handle_stripe_subscription_created
        )
        self.register_handler(
            "stripe.subscription.updated", self._handle_stripe_subscription_updated
        )
        self.register_handler(
            "stripe.subscription.deleted", self._handle_stripe_subscription_deleted
        )

        # PhonePe handlers
        self.register_handler(
            "phonepe.payment.initiated", self._handle_phonepe_payment_initiated
        )
        self.register_handler(
            "phonepe.payment.success", self._handle_phonepe_payment_success
        )
        self.register_handler(
            "phonepe.payment.failed", self._handle_phonepe_payment_failed
        )
        self.register_handler(
            "phonepe.refund.processed", self._handle_phonepe_refund_processed
        )

    def register_handler(self, event_type: str, handler: Callable):
        """Register a webhook event handler."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []

        self.event_handlers[event_type].append(handler)
        self.logger.info(f"Registered handler for event type: {event_type}")

    def unregister_handler(self, event_type: str, handler: Callable):
        """Unregister a webhook event handler."""
        if event_type in self.event_handlers:
            try:
                self.event_handlers[event_type].remove(handler)
                self.logger.info(f"Unregistered handler for event type: {event_type}")
            except ValueError:
                self.logger.warning(f"Handler not found for event type: {event_type}")

    def register_webhook_config(self, config: WebhookConfig):
        """Register a webhook configuration."""
        self.webhook_configs[config.source] = config
        self.logger.info(f"Registered webhook config for source: {config.source}")

    async def handle_webhook(
        self, source: str, headers: Dict[str, str], body: bytes
    ) -> WebhookResponse:
        """Handle incoming webhook request."""
        start_time = datetime.utcnow()

        try:
            # Get webhook configuration
            config = self.webhook_configs.get(source)
            if not config:
                return WebhookResponse(
                    status_code=404,
                    body={
                        "error": f"Webhook configuration not found for source: {source}"
                    },
                    headers={"Content-Type": "application/json"},
                )

            # Verify webhook signature
            if not await self._verify_webhook_signature(source, headers, body, config):
                return WebhookResponse(
                    status_code=401,
                    body={"error": "Invalid webhook signature"},
                    headers={"Content-Type": "application/json"},
                )

            # Parse webhook event
            try:
                event_data = json.loads(body.decode("utf-8"))
                event = self._parse_webhook_event(source, event_data, headers)
            except Exception as e:
                self.logger.error(f"Failed to parse webhook event: {e}")
                return WebhookResponse(
                    status_code=400,
                    body={"error": "Invalid webhook payload"},
                    headers={"Content-Type": "application/json"},
                )

            # Process webhook event
            result = await self._process_webhook_event(event)

            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            # Record metrics
            await self.monitoring.record_metric(
                "webhook_processing_time",
                processing_time,
                {"source": source, "event_type": event.event_type},
            )

            await self.monitoring.record_metric(
                "webhook_processed",
                1 if result.processed else 0,
                {"source": source, "event_type": event.event_type},
            )

            # Log webhook processing
            await self.logging.log_structured(
                "INFO",
                f"Webhook processed: {event.event_type}",
                {
                    "source": source,
                    "event_type": event.event_type,
                    "event_id": event.event_id,
                    "processed": result.processed,
                    "processing_time_ms": processing_time,
                    "response_status": result.response_status,
                },
            )

            # Return response
            return WebhookResponse(
                status_code=result.response_status,
                body=json.loads(result.response_body) if result.response_body else {},
                headers={"Content-Type": "application/json"},
            )

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            self.logger.error(f"Webhook handling failed: {e}")

            await self.logging.log_structured(
                "ERROR",
                f"Webhook handling failed for source: {source}",
                {
                    "source": source,
                    "error": str(e),
                    "processing_time_ms": processing_time,
                },
            )

            return WebhookResponse(
                status_code=500,
                body={"error": "Internal server error"},
                headers={"Content-Type": "application/json"},
            )

    async def _verify_webhook_signature(
        self, source: str, headers: Dict[str, str], body: bytes, config: WebhookConfig
    ) -> bool:
        """Verify webhook signature."""
        try:
            return await self.verifier.verify_signature(source, headers, body, config)
        except Exception as e:
            self.logger.error(f"Webhook signature verification failed: {e}")
            return False

    def _parse_webhook_event(
        self, source: str, event_data: Dict[str, Any], headers: Dict[str, str]
    ) -> WebhookEvent:
        """Parse webhook event from raw data."""
        event_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()

        # Extract event type based on source
        if source == "supabase":
            event_type = event_data.get("type", "unknown")
        elif source == "stripe":
            event_type = event_data.get("type", "unknown")
        elif source == "phonepe":
            event_type = event_data.get("event", "unknown")
        else:
            event_type = "unknown"

        return WebhookEvent(
            event_id=event_id,
            source=source,
            event_type=event_type,
            data=event_data,
            timestamp=timestamp,
            headers=headers,
        )

    async def _process_webhook_event(
        self, event: WebhookEvent
    ) -> WebhookProcessingResult:
        """Process webhook event."""
        start_time = datetime.utcnow()

        try:
            # Get handlers for this event type
            handlers = self.event_handlers.get(event.event_type, [])

            if not handlers:
                return WebhookProcessingResult(
                    event_id=event.event_id,
                    processed=False,
                    response_status=200,
                    response_body='{"message": "No handlers registered for this event type"}',
                    processing_time_ms=0,
                )

            # Execute all handlers
            handler_results = []
            for handler in handlers:
                try:
                    result = await handler(event)
                    handler_results.append(result)
                except Exception as e:
                    self.logger.error(
                        f"Handler failed for event {event.event_type}: {e}"
                    )
                    handler_results.append({"error": str(e)})

            # Check if any handler failed
            failed_handlers = [r for r in handler_results if "error" in r]

            if failed_handlers:
                # Schedule retry if configured
                retry_scheduled = await self._schedule_retry_if_needed(event)

                return WebhookProcessingResult(
                    event_id=event.event_id,
                    processed=False,
                    response_status=500,
                    response_body=json.dumps({"error": "Some handlers failed"}),
                    processing_time_ms=(datetime.utcnow() - start_time).total_seconds()
                    * 1000,
                    error=f"{len(failed_handlers)} handlers failed",
                    retry_scheduled=retry_scheduled,
                    retry_count=self.delivery_attempts.get(event.event_id, 0),
                )

            # All handlers succeeded
            return WebhookProcessingResult(
                event_id=event.event_id,
                processed=True,
                response_status=200,
                response_body='{"message": "Webhook processed successfully"}',
                processing_time_ms=(datetime.utcnow() - start_time).total_seconds()
                * 1000,
            )

        except Exception as e:
            return WebhookProcessingResult(
                event_id=event.event_id,
                processed=False,
                response_status=500,
                response_body=json.dumps({"error": str(e)}),
                processing_time_ms=(datetime.utcnow() - start_time).total_seconds()
                * 1000,
                error=str(e),
            )

    async def _schedule_retry_if_needed(self, event: WebhookEvent) -> bool:
        """Schedule webhook retry if needed."""
        try:
            # Get retry configuration
            config = self.webhook_configs.get(event.source)
            if not config or not config.retry_config:
                return False

            retry_config = config.retry_config
            current_attempts = self.delivery_attempts.get(event.event_id, 0)

            if current_attempts >= retry_config.max_retries:
                return False

            # Calculate retry delay
            retry_delay = self._calculate_retry_delay(current_attempts, retry_config)

            # Schedule retry
            retry = WebhookRetry(
                event_id=event.event_id,
                attempt=current_attempts + 1,
                scheduled_at=datetime.utcnow() + timedelta(seconds=retry_delay),
                max_attempts=retry_config.max_retries,
            )

            # Store retry (in a real implementation, this would go to a database)
            self.delivery_attempts[event.event_id] = current_attempts + 1

            self.logger.info(
                f"Scheduled webhook retry for event {event.event_id} in {retry_delay} seconds"
            )

            return True

        except Exception as e:
            self.logger.error(f"Failed to schedule webhook retry: {e}")
            return False

    def _calculate_retry_delay(self, attempt: int, retry_config) -> float:
        """Calculate retry delay based on configuration."""
        if retry_config.strategy == "exponential":
            return retry_config.base_delay * (2**attempt)
        elif retry_config.strategy == "linear":
            return retry_config.base_delay * (attempt + 1)
        else:  # fixed
            return retry_config.base_delay

    # Supabase event handlers
    async def _handle_supabase_user_created(
        self, event: WebhookEvent
    ) -> Dict[str, Any]:
        """Handle Supabase user created event."""
        try:
            user_data = event.data.get("record", {})

            # Process user creation
            from core.user import get_user_service

            user_service = get_user_service()

            await user_service.handle_supabase_user_created(user_data)

            return {"status": "success", "user_id": user_data.get("id")}

        except Exception as e:
            self.logger.error(f"Failed to handle Supabase user created: {e}")
            return {"error": str(e)}

    async def _handle_supabase_user_updated(
        self, event: WebhookEvent
    ) -> Dict[str, Any]:
        """Handle Supabase user updated event."""
        try:
            user_data = event.data.get("record", {})

            # Process user update
            from core.user import get_user_service

            user_service = get_user_service()

            await user_service.handle_supabase_user_updated(user_data)

            return {"status": "success", "user_id": user_data.get("id")}

        except Exception as e:
            self.logger.error(f"Failed to handle Supabase user updated: {e}")
            return {"error": str(e)}

    async def _handle_supabase_user_deleted(
        self, event: WebhookEvent
    ) -> Dict[str, Any]:
        """Handle Supabase user deleted event."""
        try:
            user_data = event.data.get("record", {})

            # Process user deletion
            from core.user import get_user_service

            user_service = get_user_service()

            await user_service.handle_supabase_user_deleted(user_data)

            return {"status": "success", "user_id": user_data.get("id")}

        except Exception as e:
            self.logger.error(f"Failed to handle Supabase user deleted: {e}")
            return {"error": str(e)}

    async def _handle_supabase_auth_login(self, event: WebhookEvent) -> Dict[str, Any]:
        """Handle Supabase auth login event."""
        try:
            auth_data = event.data.get("user", {})

            # Process login
            from core.auth import get_auth_service

            auth_service = get_auth_service()

            await auth_service.handle_supabase_login(auth_data)

            return {"status": "success", "user_id": auth_data.get("id")}

        except Exception as e:
            self.logger.error(f"Failed to handle Supabase auth login: {e}")
            return {"error": str(e)}

    async def _handle_supabase_auth_logout(self, event: WebhookEvent) -> Dict[str, Any]:
        """Handle Supabase auth logout event."""
        try:
            auth_data = event.data.get("user", {})

            # Process logout
            from core.auth import get_auth_service

            auth_service = get_auth_service()

            await auth_service.handle_supabase_logout(auth_data)

            return {"status": "success", "user_id": auth_data.get("id")}

        except Exception as e:
            self.logger.error(f"Failed to handle Supabase auth logout: {e}")
            return {"error": str(e)}

    # Stripe event handlers
    async def _handle_stripe_payment_succeeded(
        self, event: WebhookEvent
    ) -> Dict[str, Any]:
        """Handle Stripe payment succeeded event."""
        try:
            payment_data = event.data.get("object", {})

            # Process payment success
            from billing.stripe_service import get_stripe_service

            stripe_service = get_stripe_service()

            await stripe_service.handle_payment_succeeded(payment_data)

            return {"status": "success", "payment_id": payment_data.get("id")}

        except Exception as e:
            self.logger.error(f"Failed to handle Stripe payment succeeded: {e}")
            return {"error": str(e)}

    async def _handle_stripe_payment_failed(
        self, event: WebhookEvent
    ) -> Dict[str, Any]:
        """Handle Stripe payment failed event."""
        try:
            payment_data = event.data.get("object", {})

            # Process payment failure
            from billing.stripe_service import get_stripe_service

            stripe_service = get_stripe_service()

            await stripe_service.handle_payment_failed(payment_data)

            return {"status": "success", "payment_id": payment_data.get("id")}

        except Exception as e:
            self.logger.error(f"Failed to handle Stripe payment failed: {e}")
            return {"error": str(e)}

    async def _handle_stripe_invoice_created(
        self, event: WebhookEvent
    ) -> Dict[str, Any]:
        """Handle Stripe invoice created event."""
        try:
            invoice_data = event.data.get("object", {})

            # Process invoice creation
            from billing.stripe_service import get_stripe_service

            stripe_service = get_stripe_service()

            await stripe_service.handle_invoice_created(invoice_data)

            return {"status": "success", "invoice_id": invoice_data.get("id")}

        except Exception as e:
            self.logger.error(f"Failed to handle Stripe invoice created: {e}")
            return {"error": str(e)}

    async def _handle_stripe_invoice_payment_succeeded(
        self, event: WebhookEvent
    ) -> Dict[str, Any]:
        """Handle Stripe invoice payment succeeded event."""
        try:
            invoice_data = event.data.get("object", {})

            # Process invoice payment success
            from billing.stripe_service import get_stripe_service

            stripe_service = get_stripe_service()

            await stripe_service.handle_invoice_payment_succeeded(invoice_data)

            return {"status": "success", "invoice_id": invoice_data.get("id")}

        except Exception as e:
            self.logger.error(f"Failed to handle Stripe invoice payment succeeded: {e}")
            return {"error": str(e)}

    async def _handle_stripe_subscription_created(
        self, event: WebhookEvent
    ) -> Dict[str, Any]:
        """Handle Stripe subscription created event."""
        try:
            subscription_data = event.data.get("object", {})

            # Process subscription creation
            from billing.stripe_service import get_stripe_service

            stripe_service = get_stripe_service()

            await stripe_service.handle_subscription_created(subscription_data)

            return {"status": "success", "subscription_id": subscription_data.get("id")}

        except Exception as e:
            self.logger.error(f"Failed to handle Stripe subscription created: {e}")
            return {"error": str(e)}

    async def _handle_stripe_subscription_updated(
        self, event: WebhookEvent
    ) -> Dict[str, Any]:
        """Handle Stripe subscription updated event."""
        try:
            subscription_data = event.data.get("object", {})

            # Process subscription update
            from billing.stripe_service import get_stripe_service

            stripe_service = get_stripe_service()

            await stripe_service.handle_subscription_updated(subscription_data)

            return {"status": "success", "subscription_id": subscription_data.get("id")}

        except Exception as e:
            self.logger.error(f"Failed to handle Stripe subscription updated: {e}")
            return {"error": str(e)}

    async def _handle_stripe_subscription_deleted(
        self, event: WebhookEvent
    ) -> Dict[str, Any]:
        """Handle Stripe subscription deleted event."""
        try:
            subscription_data = event.data.get("object", {})

            # Process subscription deletion
            from billing.stripe_service import get_stripe_service

            stripe_service = get_stripe_service()

            await stripe_service.handle_subscription_deleted(subscription_data)

            return {"status": "success", "subscription_id": subscription_data.get("id")}

        except Exception as e:
            self.logger.error(f"Failed to handle Stripe subscription deleted: {e}")
            return {"error": str(e)}

    # PhonePe event handlers
    async def _handle_phonepe_payment_initiated(
        self, event: WebhookEvent
    ) -> Dict[str, Any]:
        """Handle PhonePe payment initiated event."""
        try:
            payment_data = event.data.get("payment", {})

            # Process payment initiation
            from billing.phonepe_service import get_phonepe_service

            phonepe_service = get_phonepe_service()

            await phonepe_service.handle_payment_initiated(payment_data)

            return {"status": "success", "payment_id": payment_data.get("id")}

        except Exception as e:
            self.logger.error(f"Failed to handle PhonePe payment initiated: {e}")
            return {"error": str(e)}

    async def _handle_phonepe_payment_success(
        self, event: WebhookEvent
    ) -> Dict[str, Any]:
        """Handle PhonePe payment success event."""
        try:
            payment_data = event.data.get("payment", {})

            # Process payment success
            from billing.phonepe_service import get_phonepe_service

            phonepe_service = get_phonepe_service()

            await phonepe_service.handle_payment_success(payment_data)

            return {"status": "success", "payment_id": payment_data.get("id")}

        except Exception as e:
            self.logger.error(f"Failed to handle PhonePe payment success: {e}")
            return {"error": str(e)}

    async def _handle_phonepe_payment_failed(
        self, event: WebhookEvent
    ) -> Dict[str, Any]:
        """Handle PhonePe payment failed event."""
        try:
            payment_data = event.data.get("payment", {})

            # Process payment failure
            from billing.phonepe_service import get_phonepe_service

            phonepe_service = get_phonepe_service()

            await phonepe_service.handle_payment_failed(payment_data)

            return {"status": "success", "payment_id": payment_data.get("id")}

        except Exception as e:
            self.logger.error(f"Failed to handle PhonePe payment failed: {e}")
            return {"error": str(e)}

    async def _handle_phonepe_refund_processed(
        self, event: WebhookEvent
    ) -> Dict[str, Any]:
        """Handle PhonePe refund processed event."""
        try:
            refund_data = event.data.get("refund", {})

            # Process refund
            from billing.phonepe_service import get_phonepe_service

            phonepe_service = get_phonepe_service()

            await phonepe_service.handle_refund_processed(refund_data)

            return {"status": "success", "refund_id": refund_data.get("id")}

        except Exception as e:
            self.logger.error(f"Failed to handle PhonePe refund processed: {e}")
            return {"error": str(e)}


# Global webhook handler instance
_webhook_handler: Optional[WebhookHandler] = None


def get_webhook_handler() -> WebhookHandler:
    """Get the global webhook handler instance."""
    global _webhook_handler
    if _webhook_handler is None:
        _webhook_handler = WebhookHandler()
    return _webhook_handler


# Export all components
__all__ = ["WebhookHandler", "WebhookProcessingResult", "get_webhook_handler"]
