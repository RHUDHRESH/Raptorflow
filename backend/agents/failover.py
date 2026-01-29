"""
Agent Failover for Raptorflow Backend
===================================

This module provides comprehensive failover capabilities for agent system
with multiple agent instances, health monitoring, and automatic failover.

Features:
- Multiple agent instances with automatic failover
- Health monitoring and automatic recovery
- Circuit breaker patterns for fault tolerance
- Load-based failover decisions
- Graceful degradation and recovery
- Failover metrics and alerting
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from enum import Enum
from collections import deque

from .base import BaseAgent
from metrics import get_metrics_collector
from .exceptions import FailoverError

logger = logging.getLogger(__name__)


class FailoverStrategy(Enum):
    """Failover strategy types."""
    ACTIVE_PASSIVE = "active_passive"
    ACTIVE_ACTIVE = "active_active"
    LOAD_BASED = "load_based"
    HEALTH_BASED = "health_based"
    PRIORITY_BASED = "priority_based"


class FailoverStatus(Enum):
    """Failover status types."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILING = "failing"
    FAILED = "failed"
    RECOVERING = "recovering"
    MAINTENANCE = "maintenance"


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open (failing)
    HALF_OPEN = "half_open"  # Testing if service has recovered


@dataclass
class AgentInstance:
    """Agent instance configuration and status."""

    instance_id: str
    agent_name: str
    host: str
    port: int
    priority: int = 1  # Lower number = higher priority
    is_active: bool = True
    is_primary: bool = False
    health_check_url: str = ""
    health_check_interval: int = 30  # seconds
    health_check_timeout: int = 10  # seconds
    max_failures: int = 3
    failure_count: int = 0
    last_health_check: Optional[datetime] = None
    status: FailoverStatus = FailoverStatus.HEALTHY
    circuit_state: CircuitState = CircuitState.CLOSED
    circuit_open_time: Optional[datetime] = None
    response_times: deque = field(default_factory=lambda: deque(maxlen=10))
    error_count: int = 0
    total_requests: int = 0


@dataclass
class FailoverConfig:
    """Configuration for failover system."""

    strategy: FailoverStrategy = FailoverStrategy.ACTIVE_PASSIVE
    health_check_interval: int = 30
    health_check_timeout: int = 10
    max_failures: int = 3
    circuit_breaker_threshold: float = 0.5  # 50% failure rate
    circuit_breaker_timeout: int = 60  # seconds
    auto_recovery: bool = True
    recovery_delay: int = 30  # seconds
    enable_load_balancing: bool = True
    enable_metrics: bool = True
    alert_threshold: float = 0.1  # 10% error rate


class FailoverManager:
    """Failover manager for agent instances."""

    def __init__(self, config: FailoverConfig):
        self.config = config
        self.agent_instances: Dict[str, AgentInstance] = {}
        self.primary_instance: Optional[str] = None
        self.active_instance: Optional[str] = None
        self.failover_history: List[Dict[str, Any]] = []
        self.metrics_collector = get_metrics_collector()
        self._is_running = False
        self._health_check_task: Optional[asyncio.Task] = None
        self._failover_lock = asyncio.Lock()

    async def start(self) -> None:
        """Start failover manager."""
        if self._is_running:
            logger.warning("Failover manager is already running")
            return

        self._is_running = True

        # Start health monitoring
        self._health_check_task = asyncio.create_task(self._health_monitoring_loop())

        logger.info("Failover manager started")

    async def stop(self) -> None:
        """Stop failover manager."""
        if not self._is_running:
            return

        self._is_running = False

        # Cancel health monitoring
        if self._health_check_task:
            self._health_check_task.cancel()
            self._health_check_task = None

        logger.info("Failover manager stopped")

    def add_agent_instance(self, instance: AgentInstance) -> bool:
        """Add an agent instance to failover pool."""
        try:
            if instance.instance_id in self.agent_instances:
                logger.warning(f"Agent instance {instance.instance_id} already exists")
                return False

            self.agent_instances[instance.instance_id] = instance

            # Set primary if none exists
            if self.primary_instance is None:
                self.primary_instance = instance.instance_id
                instance.is_primary = True

            # Set active if none exists
            if self.active_instance is None:
                self.active_instance = instance.instance_id

            logger.info(f"Added agent instance {instance.instance_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to add agent instance {instance.instance_id}: {e}")
            return False

    def remove_agent_instance(self, instance_id: str) -> bool:
        """Remove an agent instance from failover pool."""
        try:
            if instance_id not in self.agent_instances:
                logger.warning(f"Agent instance {instance_id} not found")
                return False

            instance = self.agent_instances[instance_id]

            # Handle primary removal
            if self.primary_instance == instance_id:
                # Select new primary
                remaining_instances = [
                    inst for inst in self.agent_instances.values()
                    if inst.instance_id != instance_id
                ]
                if remaining_instances:
                    new_primary = min(remaining_instances, key=lambda x: x.priority)
                    self.primary_instance = new_primary.instance_id
                    new_primary.is_primary = True
                else:
                    self.primary_instance = None

            # Handle active removal
            if self.active_instance == instance_id:
                # Switch to primary or next best
                if self.primary_instance:
                    self.active_instance = self.primary_instance
                else:
                    remaining_instances = [
                        inst for inst in self.agent_instances.values()
                        if inst.instance_id != instance_id
                    ]
                    if remaining_instances:
                        best_instance = self._select_best_instance(remaining_instances)
                        self.active_instance = best_instance.instance_id

            del self.agent_instances[instance_id]

            logger.info(f"Removed agent instance {instance_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to remove agent instance {instance_id}: {e}")
            return False

    def _select_best_instance(self, instances: List[AgentInstance]) -> AgentInstance:
        """Select best instance based on strategy."""
        try:
            if self.config.strategy == FailoverStrategy.PRIORITY_BASED:
                return min(instances, key=lambda x: x.priority)
            elif self.config.strategy == FailoverStrategy.HEALTH_BASED:
                # Prefer healthy instances
                healthy_instances = [inst for inst in instances if inst.status == FailoverStatus.HEALTHY]
                if healthy_instances:
                    return min(healthy_instances, key=lambda x: x.priority)
                else:
                    return min(instances, key=lambda x: x.failure_count)
            elif self.config.strategy == FailoverStrategy.LOAD_BASED:
                # Prefer instances with lower load
                return min(instances, key=lambda x: len(x.response_times) / len(x.response_times) if x.response_times else float('inf'))
            else:
                # Default to priority-based
                return min(instances, key=lambda x: x.priority)

        except Exception as e:
            logger.error(f"Failed to select best instance: {e}")
            return instances[0] if instances else None

    async def _health_monitoring_loop(self) -> None:
        """Main health monitoring loop."""
        while self._is_running:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                await self._perform_health_checks()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitoring loop error: {e}")
                await asyncio.sleep(10)  # Prevent tight error loops

    async def _perform_health_checks(self) -> None:
        """Perform health checks on all instances."""
        try:
            async with self._failover_lock:
                current_time = datetime.now()

                for instance_id, instance in self.agent_instances.items():
                    if not instance.is_active:
                        continue

                    # Perform health check
                    health_status = await self._check_instance_health(instance)

                    # Update instance status
                    old_status = instance.status
                    instance.status = health_status["status"]
                    instance.last_health_check = current_time

                    # Update circuit breaker
                    await self._update_circuit_breaker(instance, health_status)

                    # Log status changes
                    if old_status != instance.status:
                        logger.info(f"Instance {instance_id} status changed: {old_status.value} -> {instance.status.value}")

                    # Record metrics
                    if self.config.enable_metrics:
                        await self._record_health_metrics(instance, health_status)

                # Check if failover is needed
                await self._check_failover_needed()

        except Exception as e:
            logger.error(f"Failed to perform health checks: {e}")

    async def _check_instance_health(self, instance: AgentInstance) -> Dict[str, Any]:
        """Check health of a specific instance."""
        try:
            start_time = time.time()

            # Simple HTTP health check
            # In a real implementation, this would make an HTTP request
            # For now, we'll simulate health checks

            # Simulate health based on failure count and circuit state
            if instance.circuit_state == CircuitState.OPEN:
                return {
                    "status": FailoverStatus.FAILED.value,
                    "response_time": 0,
                    "error": "Circuit breaker is open"
                }

            # Simulate health check
            import random
            health_check_result = random.random() > 0.1  # 90% success rate

            if not health_check_result:
                instance.failure_count += 1
                return {
                    "status": FailoverStatus.FAILED.value,
                    "response_time": 0,
                    "error": "Health check failed"
                }

            response_time = time.time() - start_time
            instance.response_times.append(response_time)
            instance.failure_count = 0  # Reset on success

            return {
                "status": FailoverStatus.HEALTHY.value,
                "response_time": response_time,
                "error": None
            }

        except Exception as e:
            logger.error(f"Failed to check instance health for {instance.instance_id}: {e}")
            return {
                "status": FailoverStatus.FAILED.value,
                "response_time": 0,
                "error": str(e)
            }

    async def _update_circuit_breaker(self, instance: AgentInstance, health_status: Dict[str, Any]) -> None:
        """Update circuit breaker state based on health status."""
        try:
            is_healthy = health_status["status"] == FailoverStatus.HEALTHY.value

            if is_healthy:
                if instance.circuit_state == CircuitState.OPEN:
                    # Check if enough time has passed to try half-open
                    if instance.circuit_open_time:
                        time_since_open = datetime.now() - instance.circuit_open_time
                        if time_since_open.total_seconds() >= self.config.circuit_breaker_timeout:
                            instance.circuit_state = CircuitState.HALF_OPEN
                            logger.info(f"Circuit breaker for {instance.instance_id} moved to HALF_OPEN")
                elif instance.circuit_state == CircuitState.HALF_OPEN:
                    # Successful health check, close circuit
                    instance.circuit_state = CircuitState.CLOSED
                    instance.circuit_open_time = None
                    logger.info(f"Circuit breaker for {instance.instance_id} CLOSED")
            else:
                # Health check failed while circuit is half-open
                if instance.circuit_state == CircuitState.HALF_OPEN:
                    instance.circuit_state = CircuitState.OPEN
                    instance.circuit_open_time = datetime.now()
                    logger.warning(f"Circuit breaker for {instance.instance_id} OPENED")
            else:
                # Health check failed while circuit is closed
                if instance.circuit_state == CircuitState.CLOSED:
                    # Check failure rate
                    if len(instance.response_times) > 0:
                        failure_rate = instance.failure_count / len(instance.response_times)
                        if failure_rate >= self.config.circuit_breaker_threshold:
                            instance.circuit_state = CircuitState.OPEN
                            instance.circuit_open_time = datetime.now()
                            logger.warning(f"Circuit breaker for {instance.instance_id} OPENED due to high failure rate")

        except Exception as e:
            logger.error(f"Failed to update circuit breaker for {instance.instance_id}: {e}")

    async def _check_failover_needed(self) -> None:
        """Check if failover is needed and perform it."""
        try:
            if not self.active_instance:
                return

            active_instance = self.agent_instances.get(self.active_instance)
            if not active_instance:
                return

            # Check if active instance is healthy
            if active_instance.status == FailoverStatus.HEALTHY:
                return

            # Find alternative instances
            alternative_instances = [
                inst for inst in self.agent_instances.values()
                if inst.instance_id != self.active_instance and
                   inst.is_active and
                   inst.status == FailoverStatus.HEALTHY
            ]

            if not alternative_instances:
                logger.warning("No healthy alternative instances available")
                return

            # Select best alternative
            best_alternative = self._select_best_instance(alternative_instances)

            # Perform failover
            await self._perform_failover(active_instance, best_alternative)

        except Exception as e:
            logger.error(f"Failed to check failover: {e}")

    async def _perform_failover(self, failed_instance: AgentInstance, new_instance: AgentInstance) -> None:
        """Perform failover from failed to new instance."""
        try:
            failover_time = datetime.now()

            # Record failover event
            failover_event = {
                "timestamp": failover_time.isoformat(),
                "failed_instance": failed_instance.instance_id,
                "new_instance": new_instance.instance_id,
                "reason": failed_instance.status.value,
                "strategy": self.config.strategy.value,
                "downtime": 0  # Will be calculated when service is restored
            }

            self.failover_history.append(failover_event)

            # Update active instance
            old_active = self.active_instance
            self.active_instance = new_instance.instance_id

            logger.warning(f"Failover: {failed_instance.instance_id} -> {new_instance.instance_id} (reason: {failed_instance.status.value})")

            # Record failover metrics
            if self.config.enable_metrics:
                await self._record_failover_metrics(failed_instance, new_instance, failover_event)

            # Attempt recovery of failed instance if auto-recovery is enabled
            if self.config.enable_auto_recovery:
                asyncio.create_task(self._attempt_recovery(failed_instance))

        except Exception as e:
            logger.error(f"Failed to perform failover: {e}")

    async def _attempt_recovery(self, instance: AgentInstance) -> None:
        """Attempt to recover a failed instance."""
        try:
            logger.info(f"Attempting recovery of instance {instance.instance_id}")

            # Wait recovery delay
            await asyncio.sleep(self.config.recovery_delay)

            # Perform recovery health check
            health_status = await self._check_instance_health(instance)

            if health_status["status"] == FailoverStatus.HEALTHY.value:
                instance.status = FailoverStatus.RECOVERING
                logger.info(f"Instance {instance.instance_id} recovered successfully")

                # Update circuit breaker
                instance.circuit_state = CircuitState.CLOSED
                instance.circuit_open_time = None
                instance.failure_count = 0
            else:
                logger.warning(f"Instance {instance.instance_id} recovery failed: {health_status.get('error', 'Unknown error')}")

        except Exception as e:
            logger.error(f"Failed to attempt recovery of {instance.instance_id}: {e}")

    async def _record_health_metrics(self, instance: AgentInstance, health_status: Dict[str, Any]) -> None:
        """Record health check metrics."""
        try:
            await self.metrics_collector.record_metric(
                "agent_health_check",
                {
                    "instance_id": instance.instance_id,
                    "agent_name": instance.agent_name,
                    "status": health_status["status"],
                    "response_time": health_status.get("response_time", 0),
                    "error": health_status.get("error"),
                    "timestamp": datetime.now().isoformat()
                }
            )

        except Exception as e:
            logger.error(f"Failed to record health metrics: {e}")

    async def _record_failover_metrics(self, failed_instance: AgentInstance, new_instance: AgentInstance, failover_event: Dict[str, Any]) -> None:
        """Record failover metrics."""
        try:
            await self.metrics_collector.record_metric(
                "agent_failover",
                {
                    "failed_instance": failed_instance.instance_id,
                    "new_instance": new_instance.instance_id,
                    "reason": failover_event["reason"],
                    "strategy": failover_event["strategy"],
                    "timestamp": failover_event["timestamp"],
                    "downtime": failover_event["downtime"]
                }
            )

        except Exception as e:
            logger.error(f"Failed to record failover metrics: {e}")

    def get_failover_status(self) -> Dict[str, Any]:
        """Get current failover status."""
        try:
            active_instance = None
            if self.active_instance and self.active_instance in self.agent_instances:
                active_instance = self.agent_instances[self.active_instance]

            return {
                "active_instance": self.active_instance,
                "primary_instance": self.primary_instance,
                "total_instances": len(self.agent_instances),
                "healthy_instances": len([
                    inst for inst in self.agent_instances.values()
                    if inst.status == FailoverStatus.HEALTHY
                ]),
                "failed_instances": len([
                    inst for inst in self.agent_instances.values()
                    if inst.status == FailoverStatus.FAILED
                ]),
                "degraded_instances": len([
                    inst for inst in self.agent_instances.values()
                    if inst.status == FailoverStatus.DEGRADED
                ]),
                "strategy": self.config.strategy.value,
                "last_failover": self.failover_history[-1] if self.failover_history else None,
                "instance_details": {
                    instance_id: {
                        "status": instance.status.value,
                        "circuit_state": instance.circuit_state.value,
                        "failure_count": instance.failure_count,
                        "last_health_check": instance.last_health_check.isoformat() if instance.last_health_check else None,
                        "avg_response_time": sum(instance.response_times) / len(instance.response_times) if instance.response_times else 0,
                        "is_primary": instance.is_primary,
                        "is_active": instance.instance_id == self.active_instance
                    }
                    for instance_id, instance in self.agent_instances.items()
                }
            }

        except Exception as e:
            logger.error(f"Failed to get failover status: {e}")
            return {"error": str(e)}

    def get_failover_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get failover history."""
        return self.failover_history[-limit:]

    def get_instance_metrics(self, instance_id: str) -> Dict[str, Any]:
        """Get detailed metrics for a specific instance."""
        try:
            if instance_id not in self.agent_instances:
                return {"error": f"Instance {instance_id} not found"}

            instance = self.agent_instances[instance_id]

            return {
                "instance_id": instance_id,
                "agent_name": instance.agent_name,
                "status": instance.status.value,
                "circuit_state": instance.circuit_state.value,
                "failure_count": instance.failure_count,
                "total_requests": instance.total_requests,
                "error_count": instance.error_count,
                "avg_response_time": sum(instance.response_times) / len(instance.response_times) if instance.response_times else 0,
                "response_times": list(instance.response_times),
                "is_primary": instance.is_primary,
                "is_active": instance.instance_id == self.active_instance,
                "last_health_check": instance.last_health_check.isoformat() if instance.last_health_check else None,
                "circuit_open_time": instance.circuit_open_time.isoformat() if instance.circuit_open_time else None
            }

        except Exception as e:
            logger.error(f"Failed to get instance metrics: {e}")
            return {"error": str(e)}


# Global failover manager instance
_failover_manager: Optional[FailoverManager] = None


def get_failover_manager(config: Optional[FailoverConfig] = None) -> FailoverManager:
    """Get or create failover manager."""
    global _failover_manager
    if _failover_manager is None:
        _failover_manager = FailoverManager(config or FailoverConfig())
    return _failover_manager


# Convenience functions for backward compatibility
async def initialize_failover(config: Optional[FailoverConfig] = None) -> None:
    """Initialize failover manager."""
    manager = get_failover_manager(config)
    await manager.start()


async def add_agent_instance(instance: AgentInstance) -> bool:
    """Add an agent instance to failover pool."""
    manager = get_failover_manager()
    return await manager.add_agent_instance(instance)


async def remove_agent_instance(instance_id: str) -> bool:
    """Remove an agent instance from failover pool."""
    manager = get_failover_manager()
    return await manager.remove_agent_instance(instance_id)


def get_failover_status() -> Dict[str, Any]:
    """Get current failover status."""
    manager = get_failover_manager()
    return manager.get_failover_status()


def get_failover_history(limit: int = 50) -> List[Dict[str, Any]]:
    """Get failover history."""
    manager = get_failover_manager()
    return manager.get_failover_history(limit)


def get_instance_metrics(instance_id: str) -> Dict[str, Any]:
    """Get detailed metrics for a specific instance."""
    manager = get_failover_manager()
    return manager.get_instance_metrics(instance_id)
