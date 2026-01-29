"""
Webhook service for Redis-based webhook handling.

Provides webhook endpoint management, event delivery,
batching, and retry logic with security features.
import asyncio
import hashlib
import hmac
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import aiohttp
from .client import get_redis
from .critical_fixes import SecureErrorHandler
from .webhook_models import (
    WebhookBatch,
    WebhookDelivery,
    WebhookDeliveryStatus,
    WebhookEndpoint,
    WebhookEvent,
    WebhookEventType,
    WebhookRetryPolicy,
    WebhookStats,
    WebhookStatus,
)
class WebhookService:
    """Redis-based webhook service with secure delivery."""
    KEY_PREFIX = "webhook:"
    ENDPOINT_PREFIX = "endpoint:"
    EVENT_PREFIX = "event:"
    DELIVERY_PREFIX = "delivery:"
    BATCH_PREFIX = "batch:"
    STATS_PREFIX = "stats:"
    def __init__(self):
        self.redis = get_redis()
        self.error_handler = SecureErrorHandler()
        self.logger = logging.getLogger("webhook_service")
        # HTTP session for webhook delivery
        self._session = None
    async def get_session(self):
        """Get or create HTTP session."""
        if self._session is None:
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session
    async def close_session(self):
        """Close HTTP session."""
        if self._session:
            await self._session.close()
            self._session = None
    def _get_endpoint_key(self, endpoint_id: str) -> str:
        """Get Redis key for webhook endpoint."""
        return f"{self.KEY_PREFIX}{self.ENDPOINT_PREFIX}{endpoint_id}"
    def _get_event_key(self, event_id: str) -> str:
        """Get Redis key for webhook event."""
        return f"{self.KEY_PREFIX}{self.EVENT_PREFIX}{event_id}"
    def _get_delivery_key(self, delivery_id: str) -> str:
        """Get Redis key for webhook delivery."""
        return f"{self.KEY_PREFIX}{self.DELIVERY_PREFIX}{delivery_id}"
    def _get_batch_key(self, batch_id: str) -> str:
        """Get Redis key for webhook batch."""
        return f"{self.KEY_PREFIX}{self.BATCH_PREFIX}{batch_id}"
    def _get_stats_key(self, webhook_id: str, period: str = "daily") -> str:
        """Get Redis key for webhook statistics."""
        return f"{self.KEY_PREFIX}{self.STATS_PREFIX}{webhook_id}:{period}"
    async def create_endpoint(
        self,
        workspace_id: str,
        url: str,
        events: List[WebhookEventType],
        secret: Optional[str] = None,
        **kwargs,
    ) -> str:
        """Create a webhook endpoint."""
        endpoint_id = str(uuid.uuid4())
        if not secret:
            secret = secrets.token_urlsafe(32)
        endpoint = WebhookEndpoint(
            endpoint_id=endpoint_id,
            workspace_id=workspace_id,
            url=url,
            secret=secret,
            events=events,
            **kwargs,
        )
        # Store endpoint
        endpoint_key = self._get_endpoint_key(endpoint_id)
        await self.redis.set_json(endpoint_key, endpoint.to_dict())
        # Add to workspace index
        workspace_key = f"{self.KEY_PREFIX}workspace:{workspace_id}"
        await self.redis.sadd(workspace_key, endpoint_id)
        self.logger.info(
            f"Created webhook endpoint {endpoint_id} for workspace {workspace_id}"
        return endpoint_id
    async def get_endpoint(self, endpoint_id: str) -> Optional[WebhookEndpoint]:
        """Get webhook endpoint by ID."""
        data = await self.redis.get_json(endpoint_key)
        if data:
            return WebhookEndpoint.from_dict(data)
        return None
    async def update_endpoint(self, endpoint_id: str, updates: Dict[str, Any]) -> bool:
        """Update webhook endpoint."""
        endpoint = await self.get_endpoint(endpoint_id)
        if not endpoint:
            return False
        # Update fields
        for key, value in updates.items():
            if hasattr(endpoint, key):
                setattr(endpoint, key, value)
        endpoint.updated_at = datetime.now()
        # Store updated endpoint
        self.logger.info(f"Updated webhook endpoint {endpoint_id}")
        return True
    async def delete_endpoint(self, endpoint_id: str) -> bool:
        """Delete webhook endpoint."""
        # Remove from workspace index
        workspace_key = f"{self.KEY_PREFIX}workspace:{endpoint.workspace_id}"
        await self.redis.srem(workspace_key, endpoint_id)
        # Delete endpoint
        await self.redis.delete(endpoint_key)
        self.logger.info(f"Deleted webhook endpoint {endpoint_id}")
    async def list_endpoints(self, workspace_id: str) -> List[WebhookEndpoint]:
        """List all webhook endpoints for a workspace."""
        endpoint_ids = await self.redis.smembers(workspace_key)
        endpoints = []
        for endpoint_id in endpoint_ids:
            endpoint = await self.get_endpoint(endpoint_id)
            if endpoint:
                endpoints.append(endpoint)
        return endpoints
    async def trigger_event(
        event_type: WebhookEventType,
        payload: Dict[str, Any],
        source: str = "system",
        """Trigger a webhook event."""
        event_id = str(uuid.uuid4())
        event = WebhookEvent(
            event_id=event_id,
            event_type=event_type,
            payload=payload,
            source=source,
        # Store event
        event_key = self._get_event_key(event_id)
        await self.redis.set_json(event_key, event.to_dict(), ex=86400)  # 24 hours
        # Get matching endpoints
        endpoints = await self.list_endpoints(workspace_id)
        # Create deliveries for matching endpoints
        for endpoint in endpoints:
            if endpoint.should_deliver_event(event_type, payload):
                await self._create_delivery(endpoint.endpoint_id, event_id)
            f"Triggered webhook event {event_id} of type {event_type.value}"
        return event_id
    async def _create_delivery(self, endpoint_id: str, event_id: str) -> str:
        """Create a webhook delivery."""
        delivery_id = str(uuid.uuid4())
        # Get endpoint and event
        event_data = await self.redis.get_json(event_key)
        if not endpoint or not event_data:
            return delivery_id
        event = WebhookEvent.from_dict(event_data)
        payload = json.dumps(event.to_dict())
        delivery = WebhookDelivery(
            delivery_id=delivery_id,
            webhook_id=endpoint.webhook_id,
            status=WebhookDeliveryStatus.PENDING,
            url=endpoint.url,
            max_retries=endpoint.max_retries,
        # Store delivery
        delivery_key = self._get_delivery_key(delivery_id)
        await self.redis.set_json(delivery_key, delivery.to_dict())
        # Add to processing queue
        queue_key = f"{self.KEY_PREFIX}delivery_queue"
        await self.redis.lpush(queue_key, delivery_id)
        return delivery_id
    async def process_deliveries(self, batch_size: int = 10) -> int:
        """Process pending webhook deliveries."""
        processed = 0
        for _ in range(batch_size):
            delivery_id = await self.redis.rpop(queue_key)
            if not delivery_id:
                break
            await self._deliver_webhook(delivery_id)
            processed += 1
        return processed
    async def _deliver_webhook(self, delivery_id: str):
        """Deliver a single webhook."""
        delivery_data = await self.redis.get_json(delivery_key)
        if not delivery_data:
            return
        delivery = WebhookDelivery.from_dict(delivery_data)
        try:
            # Check if delivery can be retried
            if (
                delivery.status == WebhookDeliveryStatus.RETRYING
                and not delivery.can_retry()
            ):
                delivery.status = WebhookDeliveryStatus.EXPIRED
                await self.redis.set_json(delivery_key, delivery.to_dict())
                return
            # Get endpoint
            endpoint = await self.get_endpoint(delivery.endpoint_id)
            if not endpoint or not endpoint.is_active():
                delivery.status = WebhookDeliveryStatus.FAILED
                delivery.error_message = "Endpoint not found or inactive"
            # Mark as sending
            delivery.mark_sent()
            await self.redis.set_json(delivery_key, delivery.to_dict())
            # Prepare request
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Raptorflow-Webhooks/1.0",
                endpoint.signature_header: endpoint.generate_signature(
                    delivery.payload
                ),
            }
            # Add custom headers
            headers.update(endpoint.headers)
            session = await self.get_session()
            # Make request
            async with session.post(
                delivery.url,
                data=delivery.payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=endpoint.timeout_seconds),
            ) as response:
                response_body = await response.text()
                response_headers = dict(response.headers)
                # Mark as completed
                delivery.mark_completed(
                    status_code=response.status,
                    response_body=response_body,
                    response_headers=response_headers,
                )
                # Update statistics
                await self._update_stats(
                    endpoint.webhook_id, endpoint.endpoint_id, delivery
                # Update event delivery status
                await self._update_event_delivery_status(delivery.event_id, True)
        except asyncio.TimeoutError:
            delivery.mark_failed("Request timeout", "timeout")
        except aiohttp.ClientError as e:
            delivery.mark_failed(f"HTTP error: {str(e)}", "http_error")
        except Exception as e:
            delivery.mark_failed(f"Unexpected error: {str(e)}", "unexpected_error")
            # Log security event if suspicious
            if any(
                keyword in str(e).lower() for keyword in ["injection", "xss", "sql"]
                self.error_handler.log_security_event(
                    event_type="webhook_delivery_error",
                    severity="MEDIUM",
                    description=f"Suspicious error in webhook delivery: {str(e)}",
                    context={"delivery_id": delivery_id, "url": delivery.url},
                    workspace_id=endpoint.workspace_id if endpoint else None,
        # Handle retries
        if delivery.is_failed() and delivery.can_retry():
            delivery.schedule_retry(endpoint.retry_policy)
        elif delivery.is_failed():
            # Update event delivery status
            await self._update_event_delivery_status(delivery.event_id, False)
        # Store updated delivery
    async def _update_stats(
        self, webhook_id: str, endpoint_id: str, delivery: WebhookDelivery
    ):
        """Update webhook statistics."""
        stats_key = self._get_stats_key(webhook_id, "daily")
        stats_data = await self.redis.get_json(stats_key)
        if stats_data:
            stats = WebhookStats.from_dict(stats_data)
        else:
            stats = WebhookStats(
                webhook_id=webhook_id,
                endpoint_id=endpoint_id,
                workspace_id="",  # Would be populated from endpoint
            )
        stats.record_delivery(delivery)
        # Store stats
        await self.redis.set_json(stats_key, stats.to_dict(), ex=86400 * 7)  # 7 days
    async def _update_event_delivery_status(self, event_id: str, delivered: bool):
        """Update event delivery status."""
        if event_data:
            event = WebhookEvent.from_dict(event_data)
            event.delivered = delivered
            event.last_delivery_attempt = datetime.now()
            await self.redis.set_json(event_key, event.to_dict())
    async def get_delivery(self, delivery_id: str) -> Optional[WebhookDelivery]:
        """Get webhook delivery by ID."""
        data = await self.redis.get_json(delivery_key)
            return WebhookDelivery.from_dict(data)
    async def get_deliveries(
        webhook_id: Optional[str] = None,
        status: Optional[WebhookDeliveryStatus] = None,
        limit: int = 100,
    ) -> List[WebhookDelivery]:
        """Get webhook deliveries with optional filtering."""
        deliveries = []
        # This would be more efficient with a proper index
        # For now, we'll use a simple approach
        pattern = f"{self.KEY_PREFIX}{self.DELIVERY_PREFIX}*"
        keys = await self.redis.keys(pattern)
        for key in keys[:limit]:
            data = await self.redis.get_json(key)
            if data:
                delivery = WebhookDelivery.from_dict(data)
                # Apply filters
                if webhook_id and delivery.webhook_id != webhook_id:
                    continue
                if status and delivery.status != status:
                deliveries.append(delivery)
        return deliveries
    async def get_stats(
        self, webhook_id: str, period: str = "daily"
    ) -> Optional[WebhookStats]:
        """Get webhook statistics."""
        stats_key = self._get_stats_key(webhook_id, period)
        data = await self.redis.get_json(stats_key)
            return WebhookStats.from_dict(data)
    async def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old webhook data."""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        # Clean up old events
        event_pattern = f"{self.KEY_PREFIX}{self.EVENT_PREFIX}*"
        event_keys = await self.redis.keys(event_pattern)
        for key in event_keys:
                event = WebhookEvent.from_dict(data)
                if event.timestamp < cutoff_date:
                    await self.redis.delete(key)
        # Clean up old deliveries
        delivery_pattern = f"{self.KEY_PREFIX}{self.DELIVERY_PREFIX}*"
        delivery_keys = await self.redis.keys(delivery_pattern)
        for key in delivery_keys:
                if delivery.created_at < cutoff_date:
        self.logger.info(f"Cleaned up webhook data older than {days_to_keep} days")
    async def verify_webhook_signature(
        self, payload: str, signature: str, secret: str, algorithm: str = "sha256"
    ) -> bool:
        """Verify webhook signature."""
            expected_signature = hmac.new(
                secret.encode(), payload.encode(), getattr(hashlib, algorithm)
            ).hexdigest()
            return hmac.compare_digest(expected_signature, signature)
            self.logger.error(f"Signature verification failed: {e}")
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close_session()
