"""
AgentGateway for Raptorflow agent system.
Provides secure access control and request validation for agent operations.
"""

import asyncio
import hashlib
import logging
import secrets
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from ..base import BaseAgent
from ..config import ModelTier
from ..dispatcher import AgentDispatcher, DispatchRequest, DispatchResult
from ..exceptions import AuthenticationError, AuthorizationError, ValidationError
from ..state import AgentState
from .metrics import AgentMetricsCollector
from .registry import AgentRegistry

logger = logging.getLogger(__name__)


class AccessLevel(Enum):
    """Access levels for agent operations."""

    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    SYSTEM = "system"


class RequestType(Enum):
    """Request types for gateway validation."""

    EXECUTE = "execute"
    STREAM = "stream"
    STATUS = "status"
    METRICS = "metrics"
    CONFIG = "config"


@dataclass
class GatewayRequest:
    """Gateway request wrapper."""

    request_id: str
    request_type: RequestType
    user_id: str
    workspace_id: str
    agent_name: Optional[str]
    payload: Dict[str, Any]
    access_level: AccessLevel
    timestamp: datetime
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None
    api_key: Optional[str] = None
    session_token: Optional[str] = None


@dataclass
class GatewayResponse:
    """Gateway response wrapper."""

    request_id: str
    success: bool
    data: Optional[Dict[str, Any]]
    error: Optional[str]
    processing_time: float
    access_granted: bool
    timestamp: datetime
    metadata: Dict[str, Any]


@dataclass
class RateLimit:
    """Rate limit configuration."""

    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int
    burst_allowance: int


@dataclass
class SecurityPolicy:
    """Security policy for gateway."""

    allowed_origins: List[str]
    rate_limits: Dict[AccessLevel, RateLimit]
    require_auth: bool
    require_workspace: bool
    max_payload_size: int
    timeout_seconds: int
    retry_attempts: int


class AgentGateway:
    """Secure gateway for agent operations with access control and validation."""

    def __init__(
        self,
        dispatcher: AgentDispatcher,
        registry: AgentRegistry,
        metrics: AgentMetricsCollector,
    ):
        self.dispatcher = dispatcher
        self.registry = registry
        self.metrics = metrics

        # Security configuration
        self.security_policy = SecurityPolicy(
            allowed_origins=["*"],  # Configure based on deployment
            rate_limits={
                AccessLevel.READ: RateLimit(100, 1000, 10000, 20),
                AccessLevel.WRITE: RateLimit(50, 500, 5000, 10),
                AccessLevel.ADMIN: RateLimit(20, 200, 2000, 5),
                AccessLevel.SYSTEM: RateLimit(10, 100, 1000, 2),
            },
            require_auth=True,
            require_workspace=True,
            max_payload_size=10 * 1024 * 1024,  # 10MB
            timeout_seconds=300,  # 5 minutes
            retry_attempts=3,
        )

        # Rate limiting
        self._rate_limit_store: Dict[str, Dict[str, Any]] = {}
        self._rate_limit_lock = asyncio.Lock()

        # Session management
        self._session_store: Dict[str, Dict[str, Any]] = {}
        self._session_lock = asyncio.Lock()

        # Request logging
        self._request_log: List[GatewayRequest] = []
        self._log_lock = asyncio.Lock()

        # Authentication providers
        self._auth_providers: Dict[str, Callable] = {}

        # Middleware chain
        self._middleware: List[Callable] = []

    def register_auth_provider(self, name: str, provider: Callable):
        """Register authentication provider."""
        self._auth_providers[name] = provider

    def add_middleware(self, middleware: Callable):
        """Add middleware to gateway chain."""
        self._middleware.append(middleware)

    @asynccontextmanager
    async def request_context(self, request: GatewayRequest):
        """Context manager for request processing."""
        start_time = datetime.now()

        try:
            # Log request
            await self._log_request(request)

            # Process request
            yield request

            # Record metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            await self.metrics.record_gateway_request(request, processing_time, True)

        except Exception as e:
            # Record error metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            await self.metrics.record_gateway_request(request, processing_time, False)
            raise

    async def process_request(self, request: GatewayRequest) -> GatewayResponse:
        """Process gateway request with full security pipeline."""
        start_time = datetime.now()

        try:
            # Validate request
            await self._validate_request(request)

            # Apply middleware
            for middleware in self._middleware:
                request = await middleware(request)

            # Check rate limits
            await self._check_rate_limits(request)

            # Authenticate
            if self.security_policy.require_auth:
                await self._authenticate(request)

            # Authorize
            await self._authorize(request)

            # Route to appropriate handler
            response_data = await self._route_request(request)

            # Create success response
            response = GatewayResponse(
                request_id=request.request_id,
                success=True,
                data=response_data,
                error=None,
                processing_time=(datetime.now() - start_time).total_seconds(),
                access_granted=True,
                timestamp=datetime.now(),
                metadata={
                    "agent_name": request.agent_name,
                    "request_type": request.request_type.value,
                    "access_level": request.access_level.value,
                },
            )

            return response

        except Exception as e:
            # Create error response
            return GatewayResponse(
                request_id=request.request_id,
                success=False,
                data=None,
                error=str(e),
                processing_time=(datetime.now() - start_time).total_seconds(),
                access_granted=False,
                timestamp=datetime.now(),
                metadata={
                    "error_type": type(e).__name__,
                    "request_type": request.request_type.value,
                },
            )

    async def _validate_request(self, request: GatewayRequest):
        """Validate gateway request."""
        # Check required fields
        if not request.request_id:
            raise ValidationError("Request ID is required")

        if not request.user_id:
            raise ValidationError("User ID is required")

        if self.security_policy.require_workspace and not request.workspace_id:
            raise ValidationError("Workspace ID is required")

        # Check payload size
        payload_size = len(str(request.payload))
        if payload_size > self.security_policy.max_payload_size:
            raise ValidationError(f"Payload too large: {payload_size} bytes")

        # Check request type
        if not isinstance(request.request_type, RequestType):
            raise ValidationError("Invalid request type")

        # Check access level
        if not isinstance(request.access_level, AccessLevel):
            raise ValidationError("Invalid access level")

        # Validate timestamp
        if abs((datetime.now() - request.timestamp).total_seconds()) > 300:  # 5 minutes
            raise ValidationError("Request timestamp too old")

    async def _check_rate_limits(self, request: GatewayRequest):
        """Check rate limits for request."""
        async with self._rate_limit_lock:
            key = f"{request.user_id}:{request.workspace_id}"
            now = datetime.now()

            # Initialize rate limit tracking
            if key not in self._rate_limit_store:
                self._rate_limit_store[key] = {"requests": [], "last_reset": now}

            store = self._rate_limit_store[key]

            # Clean old requests (older than 24 hours)
            cutoff = now - timedelta(hours=24)
            store["requests"] = [
                req_time for req_time in store["requests"] if req_time > cutoff
            ]

            # Add current request
            store["requests"].append(now)

            # Get rate limits for access level
            rate_limit = self.security_policy.rate_limits[request.access_level]

            # Check per-minute limit
            minute_ago = now - timedelta(minutes=1)
            minute_requests = len(
                [req_time for req_time in store["requests"] if req_time > minute_ago]
            )
            if minute_requests > rate_limit.requests_per_minute:
                raise ValidationError(
                    f"Rate limit exceeded: {minute_requests} requests per minute"
                )

            # Check per-hour limit
            hour_ago = now - timedelta(hours=1)
            hour_requests = len(
                [req_time for req_time in store["requests"] if req_time > hour_ago]
            )
            if hour_requests > rate_limit.requests_per_hour:
                raise ValidationError(
                    f"Rate limit exceeded: {hour_requests} requests per hour"
                )

            # Check per-day limit
            day_requests = len(store["requests"])
            if day_requests > rate_limit.requests_per_day:
                raise ValidationError(
                    f"Rate limit exceeded: {day_requests} requests per day"
                )

    async def _authenticate(self, request: GatewayRequest):
        """Authenticate request."""
        # Check API key
        if request.api_key:
            if not await self._validate_api_key(request.api_key, request.user_id):
                raise AuthenticationError("Invalid API key")
            return

        # Check session token
        if request.session_token:
            if not await self._validate_session_token(
                request.session_token, request.user_id
            ):
                raise AuthenticationError("Invalid session token")
            return

        # Try auth providers
        for provider_name, provider in self._auth_providers.items():
            try:
                if await provider(request):
                    return
            except Exception as e:
                logger.warning(f"Auth provider {provider_name} failed: {e}")

        raise AuthenticationError("No valid authentication provided")

    async def _validate_api_key(self, api_key: str, user_id: str) -> bool:
        """Validate API key."""
        # In production, this would check against a database
        # For now, use a simple hash-based validation
        expected_key = hashlib.sha256(
            f"{user_id}:raptorflow_api_key".encode()
        ).hexdigest()
        return secrets.compare_digest(api_key, expected_key)

    async def _validate_session_token(self, token: str, user_id: str) -> bool:
        """Validate session token."""
        async with self._session_lock:
            if token not in self._session_store:
                return False

            session = self._session_store[token]

            # Check if session is expired
            if datetime.now() > session["expires_at"]:
                del self._session_store[token]
                return False

            # Check if session belongs to user
            if session["user_id"] != user_id:
                return False

            # Update last activity
            session["last_activity"] = datetime.now()

            return True

    async def _authorize(self, request: GatewayRequest):
        """Authorize request based on access level and permissions."""
        # Check if user has required access level for workspace
        if not await self._check_workspace_permission(
            request.user_id, request.workspace_id, request.access_level
        ):
            raise AuthorizationError("Insufficient workspace permissions")

        # Check if user can access specific agent
        if request.agent_name and not await self._check_agent_permission(
            request.user_id, request.agent_name, request.access_level
        ):
            raise AuthorizationError("Insufficient agent permissions")

        # Check request type permissions
        if not await self._check_request_type_permission(
            request.access_level, request.request_type
        ):
            raise AuthorizationError("Insufficient request type permissions")

    async def _check_workspace_permission(
        self, user_id: str, workspace_id: str, access_level: AccessLevel
    ) -> bool:
        """Check workspace permissions."""
        # In production, this would check against a database
        # For now, assume all users have read access, owners have admin access
        if access_level == AccessLevel.READ:
            return True
        elif access_level in [AccessLevel.WRITE, AccessLevel.ADMIN]:
            # Check if user is workspace owner
            return await self._is_workspace_owner(user_id, workspace_id)
        else:
            # System access requires special permissions
            return await self._is_system_admin(user_id)

    async def _check_agent_permission(
        self, user_id: str, agent_name: str, access_level: AccessLevel
    ) -> bool:
        """Check agent-specific permissions."""
        # In production, this would check against agent configuration
        # For now, allow all agents for read/write, restrict system agents
        if access_level in [AccessLevel.READ, AccessLevel.WRITE]:
            return True
        elif access_level == AccessLevel.ADMIN:
            return not agent_name.startswith("system_")
        else:
            return False

    async def _check_request_type_permission(
        self, access_level: AccessLevel, request_type: RequestType
    ) -> bool:
        """Check request type permissions."""
        permissions = {
            AccessLevel.READ: [RequestType.STATUS, RequestType.METRICS],
            AccessLevel.WRITE: [RequestType.EXECUTE, RequestType.STREAM],
            AccessLevel.ADMIN: [RequestType.CONFIG],
            AccessLevel.SYSTEM: list(RequestType),
        }

        return request_type in permissions.get(access_level, [])

    async def _is_workspace_owner(self, user_id: str, workspace_id: str) -> bool:
        """Check if user is workspace owner."""
        # In production, this would check against a database
        # For now, use a simple heuristic
        return user_id.startswith("owner_")

    async def _is_system_admin(self, user_id: str) -> bool:
        """Check if user is system admin."""
        # In production, this would check against a database
        # For now, use a simple heuristic
        return user_id.startswith("admin_")

    async def _route_request(self, request: GatewayRequest) -> Dict[str, Any]:
        """Route request to appropriate handler."""
        if request.request_type == RequestType.EXECUTE:
            return await self._handle_execute(request)
        elif request.request_type == RequestType.STREAM:
            return await self._handle_stream(request)
        elif request.request_type == RequestType.STATUS:
            return await self._handle_status(request)
        elif request.request_type == RequestType.METRICS:
            return await self._handle_metrics(request)
        elif request.request_type == RequestType.CONFIG:
            return await self._handle_config(request)
        else:
            raise ValidationError(f"Unsupported request type: {request.request_type}")

    async def _handle_execute(self, request: GatewayRequest) -> Dict[str, Any]:
        """Handle execute request."""
        if not request.agent_name:
            raise ValidationError("Agent name is required for execute request")

        # Create dispatch request
        dispatch_request = DispatchRequest(
            request_type=request.payload.get("request_type", "general"),
            request_data=request.payload.get("request_data", {}),
            workspace_id=request.workspace_id,
            user_id=request.user_id,
            priority=request.payload.get("priority", "normal"),
            strategy=request.payload.get("strategy", "capability_match"),
            constraints=request.payload.get("constraints"),
            metadata=request.payload.get("metadata"),
        )

        # Dispatch to agent
        dispatch_result = await self.dispatcher.dispatch(dispatch_request)

        return {
            "execution_id": dispatch_result.execution_id,
            "agent_name": dispatch_result.agent_name,
            "strategy_used": dispatch_result.strategy_used,
            "estimated_duration": dispatch_result.estimated_duration,
            "confidence_score": dispatch_result.confidence_score,
        }

    async def _handle_stream(self, request: GatewayRequest) -> Dict[str, Any]:
        """Handle stream request."""
        return {
            "stream_url": f"/api/agents/stream/{request.request_id}",
            "stream_type": "sse",
            "supports_backpressure": True,
        }

    async def _handle_status(self, request: GatewayRequest) -> Dict[str, Any]:
        """Handle status request."""
        if request.agent_name:
            # Get specific agent status
            agent_info = await self.registry.get_agent_info(request.agent_name)
            return agent_info
        else:
            # Get all agents status
            agents_info = await self.registry.list_agents()
            return {"agents": agents_info}

    async def _handle_metrics(self, request: GatewayRequest) -> Dict[str, Any]:
        """Handle metrics request."""
        return await self.metrics.get_metrics(request.workspace_id)

    async def _handle_config(self, request: GatewayRequest) -> Dict[str, Any]:
        """Handle config request."""
        if request.agent_name:
            # Get agent config
            agent_config = await self.registry.get_agent_config(request.agent_name)
            return agent_config
        else:
            # Get gateway config
            return {
                "security_policy": {
                    "rate_limits": {
                        level.value: {
                            "requests_per_minute": limit.requests_per_minute,
                            "requests_per_hour": limit.requests_per_hour,
                            "requests_per_day": limit.requests_per_day,
                        }
                        for level, limit in self.security_policy.rate_limits.items()
                    },
                    "require_auth": self.security_policy.require_auth,
                    "require_workspace": self.security_policy.require_workspace,
                    "max_payload_size": self.security_policy.max_payload_size,
                    "timeout_seconds": self.security_policy.timeout_seconds,
                }
            }

    async def _log_request(self, request: GatewayRequest):
        """Log gateway request."""
        async with self._log_lock:
            self._request_log.append(request)

            # Keep only last 1000 requests
            if len(self._request_log) > 1000:
                self._request_log = self._request_log[-1000:]

    async def create_session_token(
        self, user_id: str, expires_in_hours: int = 24
    ) -> str:
        """Create session token for user."""
        token = secrets.token_urlsafe(32)

        async with self._session_lock:
            self._session_store[token] = {
                "user_id": user_id,
                "created_at": datetime.now(),
                "last_activity": datetime.now(),
                "expires_at": datetime.now() + timedelta(hours=expires_in_hours),
            }

        return token

    async def revoke_session_token(self, token: str):
        """Revoke session token."""
        async with self._session_lock:
            if token in self._session_store:
                del self._session_store[token]

    async def get_gateway_stats(self) -> Dict[str, Any]:
        """Get gateway statistics."""
        recent_requests = [
            req
            for req in self._request_log
            if (datetime.now() - req.timestamp).total_seconds() < 3600
        ]

        request_type_counts = {}
        access_level_counts = {}

        for request in recent_requests:
            request_type_counts[request.request_type.value] = (
                request_type_counts.get(request.request_type.value, 0) + 1
            )
            access_level_counts[request.access_level.value] = (
                access_level_counts.get(request.access_level.value, 0) + 1
            )

        return {
            "total_requests": len(self._request_log),
            "recent_requests": len(recent_requests),
            "active_sessions": len(self._session_store),
            "rate_limit_entries": len(self._rate_limit_store),
            "request_types": request_type_counts,
            "access_levels": access_level_counts,
            "middleware_count": len(self._middleware),
            "auth_providers": len(self._auth_providers),
        }
