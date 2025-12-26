"""
RaptorFlow API Integration Client
Provides robust HTTP client with timeout, retry, and rate limiting handling.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import httpx
from httpx import AsyncClient, ConnectError, NetworkError, Response, TimeoutException

from core.enhanced_exceptions import ExternalServiceError
from core.enhanced_exceptions import NetworkError as RaptorNetworkError
from core.enhanced_exceptions import RateLimitError
from core.enhanced_exceptions import TimeoutError as RaptorTimeoutError
from core.enhanced_exceptions import (
    handle_external_service_error,
    handle_network_error,
    handle_rate_limit_error,
    handle_timeout_error,
)

logger = logging.getLogger("raptorflow.api_client")


class ClientStatus(Enum):
    """API client status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    RATE_LIMITED = "rate_limited"
    UNHEALTHY = "unhealthy"
    FAILED = "failed"


@dataclass
class RateLimitInfo:
    """Rate limit information."""

    limit: int
    remaining: int
    reset_time: datetime
    retry_after: int

    @classmethod
    def from_headers(cls, headers: Dict[str, str]) -> Optional["RateLimitInfo"]:
        """Create RateLimitInfo from response headers."""
        try:
            limit = int(headers.get("X-RateLimit-Limit", 0))
            remaining = int(headers.get("X-RateLimit-Remaining", 0))
            reset_time = int(headers.get("X-RateLimit-Reset", 0))
            retry_after = int(headers.get("Retry-After", 0))

            if limit > 0:
                return cls(
                    limit=limit,
                    remaining=remaining,
                    reset_time=(
                        datetime.fromtimestamp(reset_time)
                        if reset_time > 0
                        else datetime.utcnow() + timedelta(seconds=retry_after)
                    ),
                    retry_after=retry_after,
                )
        except (ValueError, TypeError):
            pass
        return None


@dataclass
class ClientMetrics:
    """API client metrics."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    timeout_requests: int = 0
    rate_limited_requests: int = 0
    connection_errors: int = 0
    total_response_time: float = 0.0
    last_request_time: Optional[datetime] = None
    last_error: Optional[str] = None
    last_error_time: Optional[datetime] = None
    rate_limit_info: Optional[RateLimitInfo] = None


@dataclass
class ClientConfig:
    """API client configuration."""

    base_url: str
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_backoff_factor: float = 2.0
    max_connections: int = 100
    connection_timeout: float = 10.0

    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds

    # Circuit breaker
    circuit_breaker_enabled: bool = True
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 300

    # Headers
    default_headers: Dict[str, str] = field(default_factory=dict)

    # Authentication
    api_key: Optional[str] = None
    auth_type: str = "bearer"  # bearer, basic, custom


class APIIntegrationClient:
    """
    Enhanced API client with timeout, retry, and rate limiting handling.
    """

    def __init__(self, config: ClientConfig):
        self.config = config
        self.client: Optional[AsyncClient] = None
        self.status = ClientStatus.HEALTHY
        self.metrics = ClientMetrics()
        self._circuit_breaker_open = False
        self._circuit_breaker_time: Optional[datetime] = None
        self._rate_limit_reset_time: Optional[datetime] = None
        self._request_times: List[float] = []

    async def initialize(self) -> bool:
        """Initialize the HTTP client."""
        try:
            # Prepare headers
            headers = self.config.default_headers.copy()
            if self.config.api_key:
                if self.config.auth_type == "bearer":
                    headers["Authorization"] = f"Bearer {self.config.api_key}"
                elif self.config.auth_type == "custom":
                    headers["X-API-Key"] = self.config.api_key

            # Create HTTP client
            self.client = AsyncClient(
                base_url=self.config.base_url,
                timeout=httpx.Timeout(
                    connect=self.config.connection_timeout, read=self.config.timeout
                ),
                limits=httpx.Limits(
                    max_connections=self.config.max_connections,
                    max_keepalive_connections=self.config.max_connections // 2,
                ),
                headers=headers,
            )

            logger.info(f"API client initialized for {self.config.base_url}")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize API client: {e}")
            self.status = ClientStatus.FAILED
            await self._handle_client_error("initialization", e)
            return False

    async def close(self):
        """Close the HTTP client."""
        if self.client:
            await self.client.aclose()
            self.client = None
            logger.info("API client closed")

    async def request(self, method: str, endpoint: str, **kwargs) -> Response:
        """Make HTTP request with retry and error handling."""
        if self.client is None:
            raise ExternalServiceError(
                "API client not initialized", service=self.config.base_url
            )

        # Check circuit breaker
        if self._is_circuit_breaker_open():
            raise ExternalServiceError(
                "API client circuit breaker is open",
                service=self.config.base_url,
                retry_after=self._get_circuit_breaker_retry_after(),
            )

        # Check rate limiting
        if self._is_rate_limited():
            retry_after = self._get_rate_limit_retry_after()
            raise RateLimitError(
                "API rate limit exceeded",
                limit=self.config.rate_limit_requests,
                window=self.config.rate_limit_window,
                retry_after=retry_after,
            )

        # Update request metrics
        self.metrics.total_requests += 1
        request_start_time = time.time()

        last_error = None

        for attempt in range(self.config.max_retries):
            try:
                # Make request
                response = await self._make_request(method, endpoint, **kwargs)

                # Update metrics
                request_time = time.time() - request_start_time
                self.metrics.total_response_time += request_time
                self.metrics.successful_requests += 1
                self.metrics.last_request_time = datetime.utcnow()

                # Check rate limit headers
                if self.config.rate_limit_enabled:
                    rate_limit_info = RateLimitInfo.from_headers(dict(response.headers))
                    if rate_limit_info:
                        self.metrics.rate_limit_info = rate_limit_info
                        if rate_limit_info.remaining == 0:
                            self._rate_limit_reset_time = rate_limit_info.reset_time
                            self.status = ClientStatus.RATE_LIMITED

                # Reset circuit breaker on success
                if self._circuit_breaker_open:
                    self._circuit_breaker_open = False
                    self._circuit_breaker_time = None
                    self.status = ClientStatus.HEALTHY

                return response

            except TimeoutException as e:
                last_error = e
                self.metrics.timeout_requests += 1
                logger.warning(
                    f"Request timeout (attempt {attempt + 1}/{self.config.max_retries}): {method} {endpoint}"
                )

                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(
                        self.config.retry_delay
                        * (self.config.retry_backoff_factor**attempt)
                    )
                    continue
                break

            except ConnectError as e:
                last_error = e
                self.metrics.connection_errors += 1
                logger.warning(
                    f"Connection error (attempt {attempt + 1}/{self.config.max_retries}): {method} {endpoint}"
                )

                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(
                        self.config.retry_delay
                        * (self.config.retry_backoff_factor**attempt)
                    )
                    continue
                break

            except NetworkError as e:
                last_error = e
                self.metrics.connection_errors += 1
                logger.warning(
                    f"Network error (attempt {attempt + 1}/{self.config.max_retries}): {method} {endpoint}"
                )

                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(
                        self.config.retry_delay
                        * (self.config.retry_backoff_factor**attempt)
                    )
                    continue
                break

            except httpx.HTTPStatusError as e:
                last_error = e
                response = e.response

                # Handle rate limiting
                if response.status_code == 429:
                    self.metrics.rate_limited_requests += 1
                    rate_limit_info = RateLimitInfo.from_headers(dict(response.headers))
                    if rate_limit_info:
                        self._rate_limit_reset_time = rate_limit_info.reset_time
                        self.metrics.rate_limit_info = rate_limit_info

                    retry_after = int(
                        response.headers.get("Retry-After", self.config.retry_delay)
                    )
                    if attempt < self.config.max_retries - 1:
                        logger.warning(
                            f"Rate limited (attempt {attempt + 1}/{self.config.max_retries}): {method} {endpoint}"
                        )
                        await asyncio.sleep(retry_after)
                        continue
                    break

                # Don't retry client errors (4xx)
                if 400 <= response.status_code < 500:
                    break

                # Retry server errors (5xx)
                if attempt < self.config.max_retries - 1:
                    logger.warning(
                        f"Server error (attempt {attempt + 1}/{self.config.max_retries}): {method} {endpoint} - {response.status_code}"
                    )
                    await asyncio.sleep(
                        self.config.retry_delay
                        * (self.config.retry_backoff_factor**attempt)
                    )
                    continue
                break

        # Handle final error
        self.metrics.failed_requests += 1
        self.metrics.last_error = str(last_error)
        self.metrics.last_error_time = datetime.utcnow()

        await self._handle_client_error("request_failed", last_error)

        # Convert to appropriate exception
        if isinstance(last_error, TimeoutException):
            raise handle_timeout_error(
                f"API request timeout after {self.config.timeout}s",
                timeout_seconds=self.config.timeout,
                service=self.config.base_url,
                endpoint=endpoint,
            )
        elif isinstance(last_error, (ConnectError, NetworkError)):
            raise handle_network_error(
                f"API connection error: {str(last_error)}",
                host=self.config.base_url,
                service=self.config.base_url,
                original_error=str(last_error),
            )
        elif isinstance(last_error, httpx.HTTPStatusError):
            if last_error.response.status_code == 429:
                retry_after = int(
                    last_error.response.headers.get(
                        "Retry-After", self.config.retry_delay
                    )
                )
                raise handle_rate_limit_error(
                    f"API rate limit exceeded: {last_error.response.status_code}",
                    limit=(
                        self.metrics.rate_limit_info.limit
                        if self.metrics.rate_limit_info
                        else self.config.rate_limit_requests
                    ),
                    window=self.config.rate_limit_window,
                    retry_after=retry_after,
                )
            else:
                raise handle_external_service_error(
                    f"API request failed: {last_error.response.status_code}",
                    service=self.config.base_url,
                    status_code=last_error.response.status_code,
                    endpoint=endpoint,
                    original_error=str(last_error),
                )
        else:
            raise handle_external_service_error(
                f"API request failed: {str(last_error)}",
                service=self.config.base_url,
                endpoint=endpoint,
                original_error=str(last_error),
            )

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Response:
        """Make the actual HTTP request."""
        url = (
            endpoint
            if endpoint.startswith("http")
            else f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        )
        return await self.client.request(method, url, **kwargs)

    async def _handle_client_error(self, error_type: str, error: Exception):
        """Handle client errors and update status."""
        # Update status based on error type
        if error_type in ["timeout", "connection_error", "network_error"]:
            if self.status == ClientStatus.HEALTHY:
                self.status = ClientStatus.DEGRADED
            elif self.status == ClientStatus.DEGRADED:
                self.status = ClientStatus.UNHEALTHY

        # Check circuit breaker
        if self.config.circuit_breaker_enabled:
            error_count = (
                self.metrics.timeout_requests
                + self.metrics.connection_errors
                + self.metrics.failed_requests
            )

            if error_count >= self.config.circuit_breaker_threshold:
                self._open_circuit_breaker()

        logger.warning(f"Client error handled: {error_type} - {error}")

    def _is_circuit_breaker_open(self) -> bool:
        """Check if circuit breaker is open."""
        if not self.config.circuit_breaker_enabled or not self._circuit_breaker_open:
            return False

        if self._circuit_breaker_time is None:
            return True

        # Check if circuit breaker timeout has passed
        time_since_open = datetime.utcnow() - self._circuit_breaker_time
        if time_since_open.total_seconds() > self.config.circuit_breaker_timeout:
            return False

        return True

    def _get_circuit_breaker_retry_after(self) -> int:
        """Get retry after seconds for circuit breaker."""
        if not self._circuit_breaker_open or self._circuit_breaker_time is None:
            return 0

        time_since_open = datetime.utcnow() - self._circuit_breaker_time
        retry_after = self.config.circuit_breaker_timeout - int(
            time_since_open.total_seconds()
        )
        return max(0, retry_after)

    def _open_circuit_breaker(self):
        """Open the circuit breaker."""
        if not self._circuit_breaker_open:
            self._circuit_breaker_open = True
            self._circuit_breaker_time = datetime.utcnow()
            self.status = ClientStatus.FAILED
            logger.warning("API client circuit breaker opened")

    def _is_rate_limited(self) -> bool:
        """Check if currently rate limited."""
        if not self.config.rate_limit_enabled or self._rate_limit_reset_time is None:
            return False

        return datetime.utcnow() < self._rate_limit_reset_time

    def _get_rate_limit_retry_after(self) -> int:
        """Get retry after seconds for rate limiting."""
        if not self._rate_limit_reset_time:
            return 0

        time_until_reset = self._rate_limit_reset_time - datetime.utcnow()
        return max(0, int(time_until_reset.total_seconds()))

    def get_client_status(self) -> Dict[str, Any]:
        """Get current client status and metrics."""
        success_rate = (
            (self.metrics.successful_requests / self.metrics.total_requests * 100)
            if self.metrics.total_requests > 0
            else 0
        )

        avg_response_time = (
            (self.metrics.total_response_time / self.metrics.successful_requests)
            if self.metrics.successful_requests > 0
            else 0
        )

        return {
            "status": self.status.value,
            "circuit_breaker_open": self._circuit_breaker_open,
            "circuit_breaker_retry_after": self._get_circuit_breaker_retry_after(),
            "rate_limited": self._is_rate_limited(),
            "rate_limit_retry_after": self._get_rate_limit_retry_after(),
            "metrics": {
                "total_requests": self.metrics.total_requests,
                "successful_requests": self.metrics.successful_requests,
                "failed_requests": self.metrics.failed_requests,
                "timeout_requests": self.metrics.timeout_requests,
                "rate_limited_requests": self.metrics.rate_limited_requests,
                "connection_errors": self.metrics.connection_errors,
                "success_rate": round(success_rate, 2),
                "avg_response_time": round(avg_response_time, 3),
                "last_request_time": (
                    self.metrics.last_request_time.isoformat()
                    if self.metrics.last_request_time
                    else None
                ),
                "last_error": self.metrics.last_error,
                "last_error_time": (
                    self.metrics.last_error_time.isoformat()
                    if self.metrics.last_error_time
                    else None
                ),
            },
            "rate_limit_info": (
                {
                    "limit": self.metrics.rate_limit_info.limit,
                    "remaining": self.metrics.rate_limit_info.remaining,
                    "reset_time": self.metrics.rate_limit_info.reset_time.isoformat(),
                    "retry_after": self.metrics.rate_limit_info.retry_after,
                }
                if self.metrics.rate_limit_info
                else None
            ),
            "config": {
                "base_url": self.config.base_url,
                "timeout": self.config.timeout,
                "max_retries": self.config.max_retries,
                "max_connections": self.config.max_connections,
                "rate_limit_enabled": self.config.rate_limit_enabled,
                "rate_limit_requests": self.config.rate_limit_requests,
                "rate_limit_window": self.config.rate_limit_window,
                "circuit_breaker_enabled": self.config.circuit_breaker_enabled,
                "circuit_breaker_threshold": self.config.circuit_breaker_threshold,
            },
        }


# Utility functions
async def create_api_client(
    base_url: str, api_key: Optional[str] = None, **kwargs
) -> APIIntegrationClient:
    """Create and initialize an API client."""
    config = ClientConfig(base_url=base_url, api_key=api_key, **kwargs)
    client = APIIntegrationClient(config)
    await client.initialize()
    return client


if __name__ == "__main__":
    # Test API client
    async def test_client():
        config = ClientConfig(
            base_url="https://api.example.com",
            api_key="test-key",
            timeout=10.0,
            max_retries=3,
        )

        client = APIIntegrationClient(config)
        await client.initialize()

        try:
            response = await client.request("GET", "/test")
            print(f"Response status: {response.status_code}")
        except Exception as e:
            print(f"Request failed: {e}")

        print(client.get_client_status())
        await client.close()

    asyncio.run(test_client())
