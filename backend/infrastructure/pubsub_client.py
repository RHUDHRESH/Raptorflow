"""
Google Pub/Sub client for Raptorflow event processing.

Provides asynchronous message publishing and subscription
capabilities for distributed event handling.
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from google.api_core import exceptions
from google.api_core.retry import Retry
from google.cloud import pubsub_v1

from gcp import get_gcp_client

logger = logging.getLogger(__name__)


class MessageStatus(Enum):
    """Message processing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"


@dataclass
class PubSubMessage:
    """Pub/Sub message wrapper."""

    message_id: str
    data: bytes
    attributes: Dict[str, str]
    publish_time: datetime
    ordering_key: Optional[str] = None
    delivery_attempt: int = 1

    def decode_data(self) -> str:
        """Decode message data from bytes to string."""
        return self.data.decode("utf-8")

    def decode_json(self) -> Dict[str, Any]:
        """Decode message data as JSON."""
        try:
            return json.loads(self.decode_data())
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}


@dataclass
class PublishResult:
    """Result of message publishing."""

    success: bool
    message_id: Optional[str] = None
    error_message: Optional[str] = None
    publish_time: Optional[datetime] = None


@dataclass
class SubscriptionConfig:
    """Subscription configuration."""

    subscription_id: str
    topic_id: str
    ack_deadline_seconds: int = 60
    retain_acked_messages: bool = False
    message_retention_duration: Optional[str] = None
    enable_message_ordering: bool = False
    filter_expression: Optional[str] = None
    dead_letter_policy: Optional[Dict[str, Any]] = None
    retry_policy: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Post-initialization processing."""
        if self.message_retention_duration is None:
            self.message_retention_duration = "604800s"  # 7 days


class PubSubClient:
    """Google Pub/Sub client for Raptorflow."""

    def __init__(self):
        self.gcp_client = get_gcp_client()
        self.logger = logging.getLogger("pubsub_client")

        # Get Pub/Sub clients
        self.publisher = self.gcp_client.get_pubsub_client()
        self.subscriber = pubsub_v1.SubscriberClient(
            credentials=self.gcp_client.get_credentials()
        )

        if not self.publisher:
            raise RuntimeError("Pub/Sub publisher not available")

        # Project ID
        self.project_id = self.gcp_client.get_project_id()

        # Active subscriptions
        self.active_subscriptions: Dict[str, asyncio.Task] = {}
        self.subscription_handlers: Dict[str, Callable] = {}

        # Default topic prefix
        self.topic_prefix = os.getenv("PUBSUB_TOPIC_PREFIX", "raptorflow")

    def _get_topic_path(self, topic_id: str) -> str:
        """Get full topic path."""
        return f"projects/{self.project_id}/topics/{self.topic_prefix}-{topic_id}"

    def _get_subscription_path(self, subscription_id: str) -> str:
        """Get full subscription path."""
        return f"projects/{self.project_id}/subscriptions/{self.topic_prefix}-{subscription_id}"

    async def create_topic(self, topic_id: str) -> bool:
        """Create a Pub/Sub topic."""
        try:
            topic_path = self._get_topic_path(topic_id)

            try:
                # Check if topic exists
                self.publisher.get_topic(topic_path)
                self.logger.info(f"Topic {topic_id} already exists")
                return True
            except exceptions.NotFound:
                pass

            # Create topic
            topic = pubsub_v1.types.Topic(name=topic_path)
            self.publisher.create_topic(topic)

            self.logger.info(f"Created topic: {topic_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to create topic {topic_id}: {e}")
            return False

    async def delete_topic(self, topic_id: str) -> bool:
        """Delete a Pub/Sub topic."""
        try:
            topic_path = self._get_topic_path(topic_id)
            self.publisher.delete_topic(topic_path)

            self.logger.info(f"Deleted topic: {topic_id}")
            return True

        except exceptions.NotFound:
            self.logger.warning(f"Topic {topic_id} not found for deletion")
            return False
        except Exception as e:
            self.logger.error(f"Failed to delete topic {topic_id}: {e}")
            return False

    async def list_topics(self) -> List[str]:
        """List all topics."""
        try:
            project_path = f"projects/{self.project_id}"

            topics = []
            for topic in self.publisher.list_topics(project_path):
                # Extract topic ID from full path
                topic_name = topic.name.split("/")[-1]
                if topic_name.startswith(f"{self.topic_prefix}-"):
                    topic_id = topic_name[len(f"{self.topic_prefix}-") :]
                    topics.append(topic_id)

            return topics

        except Exception as e:
            self.logger.error(f"Failed to list topics: {e}")
            return []

    async def publish_message(
        self,
        topic_id: str,
        message: Union[str, Dict[str, Any], bytes],
        attributes: Optional[Dict[str, str]] = None,
        ordering_key: Optional[str] = None,
    ) -> PublishResult:
        """Publish a message to a topic."""
        try:
            topic_path = self._get_topic_path(topic_id)

            # Prepare message data
            if isinstance(message, dict):
                data = json.dumps(message).encode("utf-8")
            elif isinstance(message, str):
                data = message.encode("utf-8")
            elif isinstance(message, bytes):
                data = message
            else:
                raise ValueError("Message must be string, dict, or bytes")

            # Prepare message
            pubsub_message = pubsub_v1.types.PubsubMessage(
                data=data, attributes=attributes or {}, ordering_key=ordering_key
            )

            # Publish message
            future = self.publisher.publish(topic_path, pubsub_message)
            message_id = future.result()

            self.logger.info(f"Published message to topic {topic_id}: {message_id}")

            return PublishResult(
                success=True, message_id=message_id, publish_time=datetime.now()
            )

        except Exception as e:
            self.logger.error(f"Failed to publish message to topic {topic_id}: {e}")
            return PublishResult(success=False, error_message=str(e))

    async def publish_batch(
        self,
        topic_id: str,
        messages: List[Union[str, Dict[str, Any], bytes]],
        attributes: Optional[Dict[str, str]] = None,
        ordering_key: Optional[str] = None,
    ) -> List[PublishResult]:
        """Publish multiple messages to a topic."""
        results = []

        for message in messages:
            result = await self.publish_message(
                topic_id, message, attributes, ordering_key
            )
            results.append(result)

        return results

    async def create_subscription(
        self, subscription_config: SubscriptionConfig
    ) -> bool:
        """Create a subscription."""
        try:
            topic_path = self._get_topic_path(subscription_config.topic_id)
            subscription_path = self._get_subscription_path(
                subscription_config.subscription_id
            )

            try:
                # Check if subscription exists
                self.subscriber.get_subscription(subscription_path)
                self.logger.info(
                    f"Subscription {subscription_config.subscription_id} already exists"
                )
                return True
            except exceptions.NotFound:
                pass

            # Create subscription config
            sub_config = pubsub_v1.types.Subscription(
                name=subscription_path,
                topic=topic_path,
                ack_deadline_seconds=subscription_config.ack_deadline_seconds,
                retain_acked_messages=subscription_config.retain_acked_messages,
                message_retention_duration={
                    "seconds": int(
                        subscription_config.message_retention_duration.rstrip("s")
                    )
                },
                enable_message_ordering=subscription_config.enable_message_ordering,
            )

            # Add filter if provided
            if subscription_config.filter_expression:
                sub_config.filter = subscription_config.filter_expression

            # Add dead letter policy if provided
            if subscription_config.dead_letter_policy:
                sub_config.dead_letter_policy = pubsub_v1.types.DeadLetterPolicy(
                    dead_letter_topic=subscription_config.dead_letter_policy["topic"],
                    max_delivery_attempts=subscription_config.dead_letter_policy.get(
                        "max_attempts", 5
                    ),
                )

            # Add retry policy if provided
            if subscription_config.retry_policy:
                sub_config.retry_policy = pubsub_v1.types.RetryPolicy(
                    minimum_backoff=subscription_config.retry_policy.get(
                        "minimum_backoff", "10s"
                    ),
                    maximum_backoff=subscription_config.retry_policy.get(
                        "maximum_backoff", "600s"
                    ),
                )

            # Create subscription
            self.subscriber.create_subscription(sub_config)

            self.logger.info(
                f"Created subscription: {subscription_config.subscription_id}"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Failed to create subscription {subscription_config.subscription_id}: {e}"
            )
            return False

    async def delete_subscription(self, subscription_id: str) -> bool:
        """Delete a subscription."""
        try:
            subscription_path = self._get_subscription_path(subscription_id)

            # Stop active subscription if running
            if subscription_id in self.active_subscriptions:
                self.active_subscriptions[subscription_id].cancel()
                del self.active_subscriptions[subscription_id]

            self.subscriber.delete_subscription(subscription_path)

            self.logger.info(f"Deleted subscription: {subscription_id}")
            return True

        except exceptions.NotFound:
            self.logger.warning(
                f"Subscription {subscription_id} not found for deletion"
            )
            return False
        except Exception as e:
            self.logger.error(f"Failed to delete subscription {subscription_id}: {e}")
            return False

    async def list_subscriptions(self) -> List[str]:
        """List all subscriptions."""
        try:
            project_path = f"projects/{self.project_id}"

            subscriptions = []
            for subscription in self.subscriber.list_subscriptions(project_path):
                # Extract subscription ID from full path
                sub_name = subscription.name.split("/")[-1]
                if sub_name.startswith(f"{self.topic_prefix}-"):
                    sub_id = sub_name[len(f"{self.topic_prefix}-") :]
                    subscriptions.append(sub_id)

            return subscriptions

        except Exception as e:
            self.logger.error(f"Failed to list subscriptions: {e}")
            return []

    async def subscribe(
        self,
        subscription_id: str,
        topic_id: str,
        handler: Callable[[PubSubMessage], None],
        config: Optional[SubscriptionConfig] = None,
    ) -> bool:
        """Subscribe to a topic with a message handler."""
        try:
            # Create subscription if needed
            if config:
                await self.create_subscription(config)
            else:
                # Create default subscription
                default_config = SubscriptionConfig(
                    subscription_id=subscription_id, topic_id=topic_id
                )
                await self.create_subscription(default_config)

            # Store handler
            self.subscription_handlers[subscription_id] = handler

            # Create subscription path
            subscription_path = self._get_subscription_path(subscription_id)

            # Define message callback
            def callback(message: pubsub_v1.subscriber.message.Message) -> None:
                try:
                    # Create PubSubMessage wrapper
                    pubsub_message = PubSubMessage(
                        message_id=message.message_id,
                        data=message.data,
                        attributes=dict(message.attributes),
                        publish_time=message.publish_time,
                        ordering_key=message.ordering_key,
                        delivery_attempt=message.delivery_attempt,
                    )

                    # Call handler
                    handler(pubsub_message)

                    # Acknowledge message
                    message.ack()

                except Exception as e:
                    self.logger.error(
                        f"Error handling message {message.message_id}: {e}"
                    )
                    # Don't acknowledge - message will be redelivered
                    message.nack()

            # Start subscription
            flow_control = pubsub_v1.types.FlowControl(max_messages=100)
            subscription_future = self.subscriber.subscribe(
                subscription_path,
                callback=callback,
                flow_control=flow_control,
                await_result_on_timeout=False,
            )

            # Store subscription task
            self.active_subscriptions[subscription_id] = subscription_future

            self.logger.info(
                f"Subscribed to topic {topic_id} with subscription {subscription_id}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to subscribe to topic {topic_id}: {e}")
            return False

    async def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from a topic."""
        try:
            if subscription_id in self.active_subscriptions:
                # Cancel subscription
                self.active_subscriptions[subscription_id].cancel()
                del self.active_subscriptions[subscription_id]

            # Remove handler
            if subscription_id in self.subscription_handlers:
                del self.subscription_handlers[subscription_id]

            self.logger.info(f"Unsubscribed from subscription: {subscription_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to unsubscribe from {subscription_id}: {e}")
            return False

    async def pull_messages(
        self, subscription_id: str, max_messages: int = 10, timeout_seconds: int = 10
    ) -> List[PubSubMessage]:
        """Pull messages from a subscription (synchronous)."""
        try:
            subscription_path = self._get_subscription_path(subscription_id)

            # Pull messages
            response = self.subscriber.pull(
                request={
                    "subscription": subscription_path,
                    "max_messages": max_messages,
                    "return_immediately": True,
                },
                timeout=timeout_seconds,
            )

            messages = []
            for received_message in response.received_messages:
                pubsub_message = PubSubMessage(
                    message_id=received_message.message.message_id,
                    data=received_message.message.data,
                    attributes=dict(received_message.message.attributes),
                    publish_time=received_message.message.publish_time,
                    ordering_key=received_message.message.ordering_key,
                    delivery_attempt=received_message.delivery_attempt,
                )
                messages.append(pubsub_message)

            # Acknowledge messages
            if messages:
                ack_ids = [msg.ack_id for msg in response.received_messages]
                self.subscriber.acknowledge(
                    request={"subscription": subscription_path, "ack_ids": ack_ids}
                )

            return messages

        except exceptions.NotFound:
            self.logger.warning(f"Subscription {subscription_id} not found")
            return []
        except Exception as e:
            self.logger.error(f"Failed to pull messages from {subscription_id}: {e}")
            return []

    async def acknowledge_message(self, subscription_id: str, ack_id: str) -> bool:
        """Acknowledge a message."""
        try:
            subscription_path = self._get_subscription_path(subscription_id)

            self.subscriber.acknowledge(
                request={"subscription": subscription_path, "ack_ids": [ack_id]}
            )

            return True

        except Exception as e:
            self.logger.error(f"Failed to acknowledge message {ack_id}: {e}")
            return False

    async def get_subscription_stats(self, subscription_id: str) -> Dict[str, Any]:
        """Get subscription statistics."""
        try:
            subscription_path = self._get_subscription_path(subscription_id)
            subscription = self.subscriber.get_subscription(subscription_path)

            return {
                "subscription_id": subscription_id,
                "topic": subscription.topic.split("/")[-1],
                "ack_deadline_seconds": subscription.ack_deadline_seconds,
                "retain_acked_messages": subscription.retain_acked_messages,
                "message_retention_duration": subscription.message_retention_duration.seconds,
                "enable_message_ordering": subscription.enable_message_ordering,
                "filter": subscription.filter,
                "active": subscription_id in self.active_subscriptions,
            }

        except Exception as e:
            self.logger.error(
                f"Failed to get subscription stats for {subscription_id}: {e}"
            )
            return {}

    async def get_topic_stats(self, topic_id: str) -> Dict[str, Any]:
        """Get topic statistics."""
        try:
            topic_path = self._get_topic_path(topic_id)
            topic = self.publisher.get_topic(topic_path)

            # Get subscriptions for this topic
            project_path = f"projects/{self.project_id}"
            subscriptions = []
            for sub in self.subscriber.list_subscriptions(project_path):
                if sub.topic == topic_path:
                    sub_id = sub.name.split("/")[-1]
                    if sub_id.startswith(f"{self.topic_prefix}-"):
                        subscriptions.append(sub_id[len(f"{self.topic_prefix}-") :])

            return {
                "topic_id": topic_id,
                "name": topic.name,
                "subscriptions": subscriptions,
                "subscription_count": len(subscriptions),
            }

        except Exception as e:
            self.logger.error(f"Failed to get topic stats for {topic_id}: {e}")
            return {}

    async def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all topics and subscriptions."""
        try:
            topics = await self.list_topics()
            subscriptions = await self.list_subscriptions()

            topic_stats = {}
            for topic_id in topics:
                topic_stats[topic_id] = await self.get_topic_stats(topic_id)

            subscription_stats = {}
            for sub_id in subscriptions:
                subscription_stats[sub_id] = await self.get_subscription_stats(sub_id)

            return {
                "project_id": self.project_id,
                "topic_prefix": self.topic_prefix,
                "total_topics": len(topics),
                "total_subscriptions": len(subscriptions),
                "active_subscriptions": len(self.active_subscriptions),
                "topics": topic_stats,
                "subscriptions": subscription_stats,
            }

        except Exception as e:
            self.logger.error(f"Failed to get all stats: {e}")
            return {}

    async def cleanup(self):
        """Cleanup resources and stop all subscriptions."""
        try:
            # Cancel all active subscriptions
            for subscription_id, task in self.active_subscriptions.items():
                task.cancel()
                self.logger.info(f"Stopped subscription: {subscription_id}")

            self.active_subscriptions.clear()
            self.subscription_handlers.clear()

            self.logger.info("Pub/Sub client cleanup completed")

        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def is_subscription_active(self, subscription_id: str) -> bool:
        """Check if subscription is active."""
        return subscription_id in self.active_subscriptions

    def get_active_subscriptions(self) -> List[str]:
        """Get list of active subscriptions."""
        return list(self.active_subscriptions.keys())


# Global Pub/Sub client instance
_pubsub_client: Optional[PubSubClient] = None


def get_pubsub_client() -> PubSubClient:
    """Get global Pub/Sub client instance."""
    global _pubsub_client
    if _pubsub_client is None:
        _pubsub_client = PubSubClient()
    return _pubsub_client


# Convenience functions
async def publish_message(
    topic_id: str,
    message: Union[str, Dict[str, Any], bytes],
    attributes: Optional[Dict[str, str]] = None,
) -> PublishResult:
    """Publish message to topic."""
    client = get_pubsub_client()
    return await client.publish_message(topic_id, message, attributes)


async def subscribe(
    subscription_id: str, topic_id: str, handler: Callable[[PubSubMessage], None]
) -> bool:
    """Subscribe to topic with handler."""
    client = get_pubsub_client()
    return await client.subscribe(subscription_id, topic_id, handler)


async def create_topic(topic_id: str) -> bool:
    """Create Pub/Sub topic."""
    client = get_pubsub_client()
    return await client.create_topic(topic_id)


async def create_subscription(config: SubscriptionConfig) -> bool:
    """Create subscription."""
    client = get_pubsub_client()
    return await client.create_subscription(config)


# Event handler decorators
def event_handler(topic_id: str, subscription_id: Optional[str] = None):
    """Decorator for event handlers."""

    def decorator(func: Callable[[PubSubMessage], None]):
        async def wrapper():
            client = get_pubsub_client()
            sub_id = subscription_id or f"{topic_id}_handler"
            await client.subscribe(sub_id, topic_id, func)

        # Store wrapper for later initialization
        func._pubsub_wrapper = wrapper
        func._topic_id = topic_id
        func._subscription_id = subscription_id or f"{topic_id}_handler"
        return func

    return decorator


# Initialize all event handlers
async def initialize_event_handlers():
    """Initialize all decorated event handlers."""
    import sys

    client = get_pubsub_client()

    # Find all decorated functions
    for name, obj in sys.modules.items():
        if hasattr(obj, "__dict__"):
            for attr_name, attr_value in obj.__dict__.items():
                if hasattr(attr_value, "_pubsub_wrapper"):
                    await attr_value._pubsub_wrapper()
