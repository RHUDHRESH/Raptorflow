"""
Part 27: API Gateway and Load Balancing
RaptorFlow Unified Search System - Industrial Grade AI Agent Search Infrastructure
===============================================================================
This module implements API gateway, load balancing, rate limiting, and
request routing for the unified search system.
"""

import asyncio
import hashlib
import json
import logging
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import aiohttp
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from core.unified_search_part1 import SearchMode, SearchQuery, SearchResult
from core.unified_search_part2 import SearchProvider

logger = logging.getLogger("raptorflow.unified_search.gateway")


class LoadBalancingAlgorithm(Enum):
    """Load balancing algorithms."""

    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    LEAST_RESPONSE_TIME = "least_response_time"
    HASH_BASED = "hash_based"
    RANDOM = "random"


class RateLimitStrategy(Enum):
    """Rate limiting strategies."""

    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"


class HealthStatus(Enum):
    """Health check status."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DRAINING = "draining"
    MAINTENANCE = "maintenance"


@dataclass
class BackendService:
    """Backend service configuration."""

    service_id: str
    name: str
    host: str
    port: int
    scheme: str = "http"
    weight: int = 1
    max_connections: int = 100
    current_connections: int = 0
    total_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    last_health_check: Optional[datetime] = None
    health_status: HealthStatus = HealthStatus.HEALTHY
    health_check_path: str = "/health"
    health_check_interval_seconds: int = 30
    circuit_breaker_threshold: float = 0.5
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "service_id": self.service_id,
            "name": self.name,
            "url": f"{self.scheme}://{self.host}:{self.port}",
            "weight": self.weight,
            "max_connections": self.max_connections,
            "current_connections": self.current_connections,
            "total_requests": self.total_requests,
            "failed_requests": self.failed_requests,
            "avg_response_time": self.avg_response_time,
            "health_status": self.health_status.value,
            "last_health_check": (
                self.last_health_check.isoformat() if self.last_health_check else None
            ),
            "metadata": self.metadata,
        }

    @property
    def is_healthy(self) -> bool:
        """Check if service is healthy."""
        return self.health_status == HealthStatus.HEALTHY

    @property
    def failure_rate(self) -> float:
        """Calculate failure rate."""
        return (
            self.failed_requests / self.total_requests
            if self.total_requests > 0
            else 0.0
        )

    @property
    def is_available(self) -> bool:
        """Check if service is available for requests."""
        return (
            self.is_healthy
            and self.current_connections < self.max_connections
            and self.failure_rate < self.circuit_breaker_threshold
        )


@dataclass
class RateLimitRule:
    """Rate limiting rule."""

    rule_id: str
    name: str
    strategy: RateLimitStrategy
    requests_per_window: int
    window_size_seconds: int
    key_extractor: str  # ip, user, api_key, custom
    enabled: bool = True
    priority: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "strategy": self.strategy.value,
            "requests_per_window": self.requests_per_window,
            "window_size_seconds": self.window_size_seconds,
            "key_extractor": self.key_extractor,
            "enabled": self.enabled,
            "priority": self.priority,
        }


@dataclass
class RoutingRule:
    """Request routing rule."""

    rule_id: str
    name: str
    condition: Dict[str, Any]  # path, method, headers, query params
    target_services: List[str]
    priority: int = 0
    enabled: bool = True
    weight_distribution: Optional[Dict[str, int]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "condition": self.condition,
            "target_services": self.target_services,
            "priority": self.priority,
            "enabled": self.enabled,
            "weight_distribution": self.weight_distribution,
        }


@dataclass
class RequestMetrics:
    """Request metrics."""

    request_id: str
    service_id: str
    method: str
    path: str
    status_code: int
    response_time_ms: float
    request_size_bytes: int
    response_size_bytes: int
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "request_id": self.request_id,
            "service_id": self.service_id,
            "method": self.method,
            "path": self.path,
            "status_code": self.status_code,
            "response_time_ms": self.response_time_ms,
            "request_size_bytes": self.request_size_bytes,
            "response_size_bytes": self.response_size_bytes,
            "timestamp": self.timestamp.isoformat(),
        }


class LoadBalancer:
    """Load balancer for backend services."""

    def __init__(self):
        self.services: Dict[str, BackendService] = {}
        self.algorithm = LoadBalancingAlgorithm.ROUND_ROBIN
        self.round_robin_index = 0
        self.request_history: deque = deque(maxlen=10000)
        self._lock = asyncio.Lock()

    def add_service(self, service: BackendService):
        """Add backend service."""
        self.services[service.service_id] = service
        logger.info(
            f"Added backend service: {service.name} ({service.host}:{service.port})"
        )

    def remove_service(self, service_id: str) -> bool:
        """Remove backend service."""
        if service_id in self.services:
            del self.services[service_id]
            logger.info(f"Removed backend service: {service_id}")
            return True
        return False

    def set_algorithm(self, algorithm: LoadBalancingAlgorithm):
        """Set load balancing algorithm."""
        self.algorithm = algorithm
        logger.info(f"Load balancing algorithm changed to: {algorithm.value}")

    async def select_service(
        self, request_path: str, request_method: str, client_ip: Optional[str] = None
    ) -> Optional[BackendService]:
        """Select backend service for request."""
        async with self._lock:
            # Get healthy services
            healthy_services = [
                service for service in self.services.values() if service.is_available
            ]

            if not healthy_services:
                logger.warning("No healthy backend services available")
                return None

            # Apply load balancing algorithm
            if self.algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
                service = self._round_robin_selection(healthy_services)
            elif self.algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
                service = self._weighted_round_robin_selection(healthy_services)
            elif self.algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
                service = self._least_connections_selection(healthy_services)
            elif self.algorithm == LoadBalancingAlgorithm.LEAST_RESPONSE_TIME:
                service = self._least_response_time_selection(healthy_services)
            elif self.algorithm == LoadBalancingAlgorithm.HASH_BASED:
                service = self._hash_based_selection(
                    healthy_services, request_path, client_ip
                )
            elif self.algorithm == LoadBalancingAlgorithm.RANDOM:
                service = self._random_selection(healthy_services)
            else:
                service = self._round_robin_selection(healthy_services)

            # Update connection count
            service.current_connections += 1

            return service

    def _round_robin_selection(self, services: List[BackendService]) -> BackendService:
        """Round-robin service selection."""
        service = services[self.round_robin_index % len(services)]
        self.round_robin_index += 1
        return service

    def _weighted_round_robin_selection(
        self, services: List[BackendService]
    ) -> BackendService:
        """Weighted round-robin service selection."""
        # Create weighted list
        weighted_services = []
        for service in services:
            weight = max(1, service.weight)
            weighted_services.extend([service] * weight)

        service = weighted_services[self.round_robin_index % len(weighted_services)]
        self.round_robin_index += 1
        return service

    def _least_connections_selection(
        self, services: List[BackendService]
    ) -> BackendService:
        """Select service with least connections."""
        return min(services, key=lambda s: s.current_connections)

    def _least_response_time_selection(
        self, services: List[BackendService]
    ) -> BackendService:
        """Select service with lowest response time."""
        return min(services, key=lambda s: s.avg_response_time)

    def _hash_based_selection(
        self, services: List[BackendService], path: str, client_ip: Optional[str]
    ) -> BackendService:
        """Hash-based service selection."""
        # Create hash from path and IP
        hash_input = f"{path}_{client_ip or 'unknown'}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)

        return services[hash_value % len(services)]

    def _random_selection(self, services: List[BackendService]) -> BackendService:
        """Random service selection."""
        import random

        return random.choice(services)

    def release_connection(self, service_id: str):
        """Release connection from service."""
        if service_id in self.services:
            self.services[service_id].current_connections = max(
                0, self.services[service_id].current_connections - 1
            )

    def update_service_metrics(
        self, service_id: str, response_time_ms: float, success: bool
    ):
        """Update service metrics."""
        if service_id not in self.services:
            return

        service = self.services[service_id]
        service.total_requests += 1

        if not success:
            service.failed_requests += 1

        # Update average response time
        if service.total_requests == 1:
            service.avg_response_time = response_time_ms
        else:
            service.avg_response_time = (
                service.avg_response_time * (service.total_requests - 1)
                + response_time_ms
            ) / service.total_requests

    def get_service_stats(self) -> Dict[str, Any]:
        """Get service statistics."""
        stats = {
            "total_services": len(self.services),
            "healthy_services": len(
                [s for s in self.services.values() if s.is_healthy]
            ),
            "algorithm": self.algorithm.value,
            "services": {},
        }

        for service_id, service in self.services.items():
            stats["services"][service_id] = service.to_dict()

        return stats


class RateLimiter:
    """Rate limiting implementation."""

    def __init__(self):
        self.rules: Dict[str, RateLimitRule] = {}
        self.fixed_windows: Dict[str, Dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        self.sliding_windows: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.token_buckets: Dict[str, Dict[str, float]] = defaultdict(
            lambda: defaultdict(float)
        )
        self.leaky_buckets: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start rate limiter."""
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("Rate limiter started")

    async def stop(self):
        """Stop rate limiter."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("Rate limiter stopped")

    def add_rule(self, rule: RateLimitRule):
        """Add rate limiting rule."""
        self.rules[rule.rule_id] = rule
        logger.info(f"Added rate limiting rule: {rule.name}")

    async def check_rate_limit(
        self, rule_id: str, key: str, current_time: Optional[datetime] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check if request is within rate limit."""
        if current_time is None:
            current_time = datetime.now()

        rule = self.rules.get(rule_id)
        if not rule or not rule.enabled:
            return True, {"allowed": True, "reason": "no_rule"}

        async with self._lock:
            if rule.strategy == RateLimitStrategy.FIXED_WINDOW:
                return await self._check_fixed_window(rule, key, current_time)
            elif rule.strategy == RateLimitStrategy.SLIDING_WINDOW:
                return await self._check_sliding_window(rule, key, current_time)
            elif rule.strategy == RateLimitStrategy.TOKEN_BUCKET:
                return await self._check_token_bucket(rule, key, current_time)
            elif rule.strategy == RateLimitStrategy.LEAKY_BUCKET:
                return await self._check_leaky_bucket(rule, key, current_time)
            else:
                return True, {"allowed": True, "reason": "unknown_strategy"}

    async def _check_fixed_window(
        self, rule: RateLimitRule, key: str, current_time: datetime
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check fixed window rate limit."""
        window_key = f"{rule_id}:{key}"
        current_window = current_time.timestamp() // rule.window_size_seconds

        # Reset if new window
        if (
            "window" not in self.fixed_windows[window_key]
            or self.fixed_windows[window_key]["window"] != current_window
        ):
            self.fixed_windows[window_key] = {"window": current_window, "count": 0}

        # Check limit
        self.fixed_windows[window_key]["count"] += 1
        count = self.fixed_windows[window_key]["count"]

        if count > rule.requests_per_window:
            return False, {
                "allowed": False,
                "strategy": "fixed_window",
                "count": count,
                "limit": rule.requests_per_window,
                "reset_time": (current_window + 1) * rule.window_size_seconds,
            }

        return True, {
            "allowed": True,
            "strategy": "fixed_window",
            "count": count,
            "limit": rule.requests_per_window,
            "remaining": rule.requests_per_window - count,
        }

    async def _check_sliding_window(
        self, rule: RateLimitRule, key: str, current_time: datetime
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check sliding window rate limit."""
        window_key = f"{rule_id}:{key}"
        window_start = current_time - timedelta(seconds=rule.window_size_seconds)

        # Remove old entries
        while (
            self.sliding_windows[window_key]
            and self.sliding_windows[window_key][0] < window_start
        ):
            self.sliding_windows[window_key].popleft()

        # Check limit
        current_count = len(self.sliding_windows[window_key])

        if current_count >= rule.requests_per_window:
            return False, {
                "allowed": False,
                "strategy": "sliding_window",
                "count": current_count,
                "limit": rule.requests_per_window,
                "retry_after": int(
                    (
                        self.sliding_windows[window_key][0]
                        + timedelta(seconds=rule.window_size_seconds)
                        - current_time
                    ).total_seconds()
                ),
            }

        # Add current request
        self.sliding_windows[window_key].append(current_time)

        return True, {
            "allowed": True,
            "strategy": "sliding_window",
            "count": current_count + 1,
            "limit": rule.requests_per_window,
            "remaining": rule.requests_per_window - current_count - 1,
        }

    async def _check_token_bucket(
        self, rule: RateLimitRule, key: str, current_time: datetime
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check token bucket rate limit."""
        bucket_key = f"{rule_id}:{key}"

        # Get current tokens
        tokens = self.token_buckets[bucket_key]["tokens"]
        last_refill = self.token_buckets[bucket_key]["last_refill"]

        # Refill tokens
        time_passed = (current_time - last_refill).total_seconds()
        tokens_to_add = time_passed * (
            rule.requests_per_window / rule.window_size_seconds
        )
        tokens = min(rule.requests_per_window, tokens + tokens_to_add)

        # Check if token available
        if tokens >= 1:
            tokens -= 1
            self.token_buckets[bucket_key] = {
                "tokens": tokens,
                "last_refill": current_time,
            }

            return True, {
                "allowed": True,
                "strategy": "token_bucket",
                "tokens": tokens,
                "max_tokens": rule.requests_per_window,
            }
        else:
            return False, {
                "allowed": False,
                "strategy": "token_bucket",
                "tokens": tokens,
                "max_tokens": rule.requests_per_window,
                "retry_after": int(
                    (1 - tokens) * (rule.window_size_seconds / rule.requests_per_window)
                ),
            }

    async def _check_leaky_bucket(
        self, rule: RateLimitRule, key: str, current_time: datetime
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check leaky bucket rate limit."""
        bucket_key = f"{rule_id}:{key}"
        leak_rate = rule.requests_per_window / rule.window_size_seconds

        # Process leaks
        bucket = self.leaky_buckets[bucket_key]
        while bucket and (current_time - bucket[0]).total_seconds() > (1 / leak_rate):
            bucket.popleft()

        # Check if bucket is full
        if len(bucket) >= rule.requests_per_window:
            oldest_request = bucket[0]
            retry_after = int(
                (
                    oldest_request + timedelta(seconds=1 / leak_rate) - current_time
                ).total_seconds()
            )

            return False, {
                "allowed": False,
                "strategy": "leaky_bucket",
                "bucket_size": len(bucket),
                "max_bucket_size": rule.requests_per_window,
                "retry_after": retry_after,
            }

        # Add current request to bucket
        bucket.append(current_time)

        return True, {
            "allowed": True,
            "strategy": "leaky_bucket",
            "bucket_size": len(bucket),
            "max_bucket_size": rule.requests_per_window,
        }

    async def _cleanup_loop(self):
        """Cleanup old rate limit data."""
        while True:
            try:
                await asyncio.sleep(300)  # Clean up every 5 minutes

                current_time = datetime.now()
                cutoff_time = current_time - timedelta(hours=1)

                # Clean up old sliding windows
                for key in list(self.sliding_windows.keys()):
                    while (
                        self.sliding_windows[key]
                        and self.sliding_windows[key][0] < cutoff_time
                    ):
                        self.sliding_windows[key].popleft()

                    if not self.sliding_windows[key]:
                        del self.sliding_windows[key]

                # Clean up old leaky buckets
                for key in list(self.leaky_buckets.keys()):
                    while (
                        self.leaky_buckets[key]
                        and self.leaky_buckets[key][0] < cutoff_time
                    ):
                        self.leaky_buckets[key].popleft()

                    if not self.leaky_buckets[key]:
                        del self.leaky_buckets[key]

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Rate limiter cleanup error: {e}")


class APIGateway:
    """Main API gateway."""

    def __init__(self):
        self.load_balancer = LoadBalancer()
        self.rate_limiter = RateLimiter()
        self.routing_rules: Dict[str, RoutingRule] = {}
        self.request_metrics: deque = deque(maxlen=10000)
        self.http_session: Optional[aiohttp.ClientSession] = None
        self._health_check_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start API gateway."""
        self.http_session = aiohttp.ClientSession()
        await self.rate_limiter.start()
        self._health_check_task = asyncio.create_task(self._health_check_loop())

        # Add default rate limiting rules
        self._add_default_rate_limits()

        logger.info("API gateway started")

    async def stop(self):
        """Stop API gateway."""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass

        await self.rate_limiter.stop()
        if self.http_session:
            await self.http_session.close()

        logger.info("API gateway stopped")

    def _add_default_rate_limits(self):
        """Add default rate limiting rules."""
        # Global rate limit
        global_rule = RateLimitRule(
            rule_id="global",
            name="Global Rate Limit",
            strategy=RateLimitStrategy.SLIDING_WINDOW,
            requests_per_window=1000,
            window_size_seconds=60,
            key_extractor="ip",
        )
        self.rate_limiter.add_rule(global_rule)

        # API rate limit
        api_rule = RateLimitRule(
            rule_id="api",
            name="API Rate Limit",
            strategy=RateLimitStrategy.TOKEN_BUCKET,
            requests_per_window=100,
            window_size_seconds=60,
            key_extractor="api_key",
        )
        self.rate_limiter.add_rule(api_rule)

    def add_routing_rule(self, rule: RoutingRule):
        """Add routing rule."""
        self.routing_rules[rule.rule_id] = rule
        logger.info(f"Added routing rule: {rule.name}")

    async def route_request(
        self,
        method: str,
        path: str,
        headers: Dict[str, str],
        query_params: Dict[str, str],
        body: Optional[bytes] = None,
    ) -> Tuple[Optional[BackendService], Dict[str, Any]]:
        """Route request to appropriate backend service."""
        # Find matching routing rule
        matching_rule = self._find_matching_rule(method, path, headers, query_params)

        if not matching_rule:
            return None, {"error": "No matching routing rule found"}

        # Select service from target services
        target_services = [
            self.load_balancer.services.get(service_id)
            for service_id in matching_rule.target_services
        ]
        target_services = [s for s in target_services if s is not None]

        if not target_services:
            return None, {"error": "No healthy target services available"}

        # Use load balancer to select service
        client_ip = headers.get("x-forwarded-for", headers.get("x-real-ip"))
        service = await self.load_balancer.select_service(path, method, client_ip)

        return service, {"rule": matching_rule.rule_id}

    def _find_matching_rule(
        self,
        method: str,
        path: str,
        headers: Dict[str, str],
        query_params: Dict[str, str],
    ) -> Optional[RoutingRule]:
        """Find matching routing rule."""
        matching_rules = []

        for rule in self.routing_rules.values():
            if not rule.enabled:
                continue

            # Check method
            if "method" in rule.condition and rule.condition["method"] != method:
                continue

            # Check path
            if "path" in rule.condition:
                path_pattern = rule.condition["path"]
                if not self._match_path(path, path_pattern):
                    continue

            # Check headers
            if "headers" in rule.condition:
                for header_name, header_value in rule.condition["headers"].items():
                    if headers.get(header_name) != header_value:
                        continue

            # Check query params
            if "query_params" in rule.condition:
                for param_name, param_value in rule.condition["query_params"].items():
                    if query_params.get(param_name) != param_value:
                        continue

            matching_rules.append(rule)

        # Return highest priority rule
        if matching_rules:
            return max(matching_rules, key=lambda r: r.priority)

        return None

    def _match_path(self, path: str, pattern: str) -> bool:
        """Check if path matches pattern."""
        # Simple pattern matching - in production use regex
        if "*" in pattern:
            # Wildcard matching
            pattern_parts = pattern.split("*")
            if len(pattern_parts) == 2:
                return path.startswith(pattern_parts[0]) and path.endswith(
                    pattern_parts[1]
                )

        return path == pattern

    async def forward_request(
        self,
        service: BackendService,
        method: str,
        path: str,
        headers: Dict[str, str],
        query_params: Dict[str, str],
        body: Optional[bytes] = None,
    ) -> Tuple[int, Dict[str, str], bytes, float]:
        """Forward request to backend service."""
        start_time = time.time()

        try:
            # Build URL
            url = f"{service.scheme}://{service.host}:{service.port}{path}"

            # Prepare headers
            forward_headers = headers.copy()
            forward_headers["X-Forwarded-For"] = headers.get(
                "x-forwarded-for", "unknown"
            )
            forward_headers["X-Forwarded-Proto"] = "https"
            forward_headers["X-Forwarded-Host"] = headers.get("host", "unknown")

            # Make request
            async with self.http_session.request(
                method=method,
                url=url,
                headers=forward_headers,
                params=query_params,
                data=body,
            ) as response:
                response_body = await response.read()
                response_headers = dict(response.headers)
                response_time = (time.time() - start_time) * 1000

                # Update metrics
                self.load_balancer.update_service_metrics(
                    service.service_id, response_time, response.status_code < 400
                )

                # Record request metrics
                request_id = str(uuid.uuid4())
                metrics = RequestMetrics(
                    request_id=request_id,
                    service_id=service.service_id,
                    method=method,
                    path=path,
                    status_code=response.status_code,
                    response_time_ms=response_time,
                    request_size_bytes=len(body) if body else 0,
                    response_size_bytes=len(response_body),
                )
                self.request_metrics.append(metrics)

                return (
                    response.status_code,
                    response_headers,
                    response_body,
                    response_time,
                )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000

            # Update metrics
            self.load_balancer.update_service_metrics(
                service.service_id, response_time, False
            )

            logger.error(f"Error forwarding request to {service.name}: {e}")
            raise

    async def check_rate_limits(
        self, rule_ids: List[str], request_context: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check multiple rate limiting rules."""
        for rule_id in rule_ids:
            # Extract key based on rule configuration
            rule = self.rate_limiter.rules.get(rule_id)
            if not rule:
                continue

            key = self._extract_rate_limit_key(rule.key_extractor, request_context)

            allowed, info = await self.rate_limiter.check_rate_limit(rule_id, key)

            if not allowed:
                return False, info

        return True, {"allowed": True}

    def _extract_rate_limit_key(self, extractor: str, context: Dict[str, Any]) -> str:
        """Extract rate limit key from request context."""
        if extractor == "ip":
            return context.get("client_ip", "unknown")
        elif extractor == "user":
            return context.get("user_id", "anonymous")
        elif extractor == "api_key":
            return context.get("api_key", "none")
        else:
            return context.get(extractor, "default")

    async def _health_check_loop(self):
        """Health check loop for backend services."""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds

                for service in self.load_balancer.services.values():
                    await self._check_service_health(service)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error: {e}")

    async def _check_service_health(self, service: BackendService):
        """Check individual service health."""
        try:
            url = f"{service.scheme}://{service.host}:{service.port}{service.health_check_path}"

            async with self.http_session.get(
                url, timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    service.health_status = HealthStatus.HEALTHY
                else:
                    service.health_status = HealthStatus.UNHEALTHY

                service.last_health_check = datetime.now()

        except Exception as e:
            service.health_status = HealthStatus.UNHEALTHY
            service.last_health_check = datetime.now()
            logger.warning(f"Health check failed for {service.name}: {e}")

    def get_gateway_stats(self) -> Dict[str, Any]:
        """Get gateway statistics."""
        recent_metrics = list(self.request_metrics)[-1000:]

        if recent_metrics:
            response_times = [m.response_time_ms for m in recent_metrics]
            status_codes = [m.status_code for m in recent_metrics]

            stats = {
                "total_requests": len(self.request_metrics),
                "recent_requests": len(recent_metrics),
                "avg_response_time_ms": statistics.mean(response_times),
                "p95_response_time_ms": self._percentile(response_times, 0.95),
                "success_rate": len([s for s in status_codes if s < 400])
                / len(status_codes),
                "requests_per_minute": len(recent_metrics)
                / 10,  # Assuming recent metrics cover last 10 minutes
            }
        else:
            stats = {
                "total_requests": 0,
                "recent_requests": 0,
                "avg_response_time_ms": 0,
                "p95_response_time_ms": 0,
                "success_rate": 0,
                "requests_per_minute": 0,
            }

        stats["load_balancer"] = self.load_balancer.get_service_stats()
        stats["rate_limiter"] = {
            "active_rules": len(
                [r for r in self.rate_limiter.rules.values() if r.enabled]
            ),
            "total_rules": len(self.rate_limiter.rules),
        }
        stats["routing_rules"] = len(self.routing_rules)

        return stats

    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile."""
        if not values:
            return 0.0

        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile)
        return sorted_values[min(index, len(sorted_values) - 1)]


# Global API gateway
api_gateway = APIGateway()
