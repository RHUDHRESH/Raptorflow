"""
PostHog analytics integration for RaptorFlow
Provides comprehensive user behavior tracking and product analytics
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from fastapi import Request, Response

logger = logging.getLogger(__name__)


class PostHogClient:
    """PostHog analytics client for RaptorFlow"""

    def __init__(self):
        self.api_key = os.getenv("POSTHOG_API_KEY")
        self.host = os.getenv("POSTHOG_HOST", "https://app.posthog.com")
        self.enabled = bool(self.api_key)

        if self.enabled:
            logger.info("PostHog analytics initialized")
        else:
            logger.warning("POSTHOG_API_KEY not configured, analytics disabled")

    async def _make_request(self, endpoint: str, data: Dict[str, Any]) -> bool:
        """Make request to PostHog API"""
        if not self.enabled:
            return False

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.host}{endpoint}",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}",
                    },
                    json=data,
                    timeout=10.0,
                )

                if response.status_code == 200:
                    return True
                else:
                    logger.error(
                        f"PostHog API error: {response.status_code} - {response.text}"
                    )
                    return False

        except Exception as e:
            logger.error(f"Failed to send data to PostHog: {e}")
            return False

    async def capture_event(
        self,
        distinct_id: str,
        event_name: str,
        properties: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
    ) -> bool:
        """Capture an event"""
        if not self.enabled:
            return False

        data = {
            "api_key": self.api_key,
            "distinct_id": distinct_id,
            "event": event_name,
            "properties": properties or {},
            "timestamp": (
                timestamp.isoformat() if timestamp else datetime.utcnow().isoformat()
            ),
        }

        return await self._make_request("/capture", data)

    async def identify_user(
        self, distinct_id: str, properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Identify a user with properties"""
        if not self.enabled:
            return False

        data = {
            "api_key": self.api_key,
            "distinct_id": distinct_id,
            "properties": properties or {},
            "event": "$identify",
        }

        return await self._make_request("/capture", data)

    async def alias_user(self, distinct_id: str, alias: str) -> bool:
        """Create an alias for a user"""
        if not self.enabled:
            return False

        data = {
            "api_key": self.api_key,
            "distinct_id": distinct_id,
            "alias": alias,
            "event": "$create_alias",
        }

        return await self._make_request("/capture", data)

    async def set_group_properties(
        self, group_type: str, group_key: str, properties: Dict[str, Any]
    ) -> bool:
        """Set properties for a group (e.g., workspace)"""
        if not self.enabled:
            return False

        data = {
            "api_key": self.api_key,
            "event": "$groupidentify",
            "properties": {
                "$group_type": group_type,
                "$group_key": group_key,
                "$group_set": properties,
            },
        }

        return await self._make_request("/capture", data)


# Global PostHog client instance
_posthog_client: Optional[PostHogClient] = None


def get_posthog_client() -> PostHogClient:
    """Get global PostHog client instance"""
    global _posthog_client
    if _posthog_client is None:
        _posthog_client = PostHogClient()
    return _posthog_client


# Convenience functions for common events
async def track_onboarding_completed(
    user_id: str, properties: Optional[Dict[str, Any]] = None
) -> bool:
    """Track onboarding completion"""
    client = get_posthog_client()
    return await client.capture_event(
        distinct_id=user_id, event_name="ONBOARDING_COMPLETED", properties=properties
    )


async def track_payment_initiated(
    user_id: str, properties: Optional[Dict[str, Any]] = None
) -> bool:
    """Track payment initiation"""
    client = get_posthog_client()
    return await client.capture_event(
        distinct_id=user_id, event_name="PAYMENT_INITIATED", properties=properties
    )


async def track_payment_completed(
    user_id: str, properties: Optional[Dict[str, Any]] = None
) -> bool:
    """Track payment completion"""
    client = get_posthog_client()
    return await client.capture_event(
        distinct_id=user_id, event_name="PAYMENT_COMPLETED", properties=properties
    )


async def track_icp_created(
    user_id: str, properties: Optional[Dict[str, Any]] = None
) -> bool:
    """Track ICP creation"""
    client = get_posthog_client()
    return await client.capture_event(
        distinct_id=user_id, event_name="ICP_CREATED", properties=properties
    )


async def track_campaign_created(
    user_id: str, properties: Optional[Dict[str, Any]] = None
) -> bool:
    """Track campaign creation"""
    client = get_posthog_client()
    return await client.capture_event(
        distinct_id=user_id, event_name="CAMPAIGN_CREATED", properties=properties
    )


async def track_agent_used(
    user_id: str, agent_name: str, properties: Optional[Dict[str, Any]] = None
) -> bool:
    """Track agent usage"""
    client = get_posthog_client()
    event_properties = {"agent_name": agent_name}
    if properties:
        event_properties.update(properties)

    return await client.capture_event(
        distinct_id=user_id, event_name="AGENT_USED", properties=event_properties
    )


async def track_feature_used(
    user_id: str, feature_name: str, properties: Optional[Dict[str, Any]] = None
) -> bool:
    """Track feature usage"""
    client = get_posthog_client()
    event_properties = {"feature_name": feature_name}
    if properties:
        event_properties.update(properties)

    return await client.capture_event(
        distinct_id=user_id, event_name="FEATURE_USED", properties=event_properties
    )


async def track_page_view(
    user_id: str, page_name: str, properties: Optional[Dict[str, Any]] = None
) -> bool:
    """Track page view"""
    client = get_posthog_client()
    event_properties = {"page_name": page_name}
    if properties:
        event_properties.update(properties)

    return await client.capture_event(
        distinct_id=user_id, event_name="PAGE_VIEW", properties=event_properties
    )


async def track_error(
    user_id: str,
    error_type: str,
    error_message: str,
    properties: Optional[Dict[str, Any]] = None,
) -> bool:
    """Track error occurrence"""
    client = get_posthog_client()
    event_properties = {"error_type": error_type, "error_message": error_message}
    if properties:
        event_properties.update(properties)

    return await client.capture_event(
        distinct_id=user_id, event_name="ERROR_OCCURRED", properties=event_properties
    )


# Middleware for automatic tracking
class PostHogMiddleware:
    """PostHog analytics middleware for FastAPI"""

    def __init__(self, app):
        self.app = app
        self.client = get_posthog_client()

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Create request object
        request = Request(scope, receive)

        # Extract user info from request state (set by auth middleware)
        user_id = None
        if hasattr(request.state, "user") and request.state.user:
            user_id = request.state.user.get("id")

        workspace_id = None
        if hasattr(request.state, "workspace") and request.state.workspace:
            workspace_id = request.state.workspace.get("id")

        # Track page view for GET requests
        if request.method == "GET" and user_id:
            page_name = f"{request.method} {request.url.path}"
            properties = {}

            if workspace_id:
                properties["workspace_id"] = workspace_id

            await self.client.capture_event(
                distinct_id=user_id,
                event_name="PAGE_VIEW",
                properties={
                    "page_name": page_name,
                    "method": request.method,
                    "path": request.url.path,
                    **properties,
                },
            )

        await self.app(scope, receive, send)


def add_posthog_middleware(app):
    """Add PostHog middleware to FastAPI app"""
    if get_posthog_client().enabled:
        app.add_middleware(PostHogMiddleware)
        logger.info("PostHog middleware added")
    else:
        logger.info("PostHog middleware not added (disabled)")


# Health check
def get_health_status() -> Dict[str, Any]:
    """Get PostHog health status"""
    client = get_posthog_client()

    return {
        "status": "healthy" if client.enabled else "disabled",
        "api_key_configured": client.enabled,
        "host": client.host,
    }
