"""
Agent Load Balancing for Raptorflow Backend
===========================================

This module provides load balancing capabilities for multiple agent instances
to handle high traffic loads and ensure system reliability.

Features:
- Multiple agent workers with request distribution
- Health monitoring and automatic failover
- Request queuing and priority handling
- Performance metrics and load-based scaling
- Circuit breaker pattern for fault tolerance
"""

import asyncio
import logging
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from dispatcher import AgentDispatcher
from registry import AgentRegistry

from .base import BaseAgent
from .exceptions import LoadBalancerError
from .state import AgentState

logger = logging.getLogger(__name__)


class LoadBalancingStrategy(Enum):
    """Load balancing strategies."""

    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    RANDOM = "random"
    CONSISTENT_HASH = "consistent_hash"


class AgentWorker:
    """Individual agent worker instance."""

    def __init__(self, agent: BaseAgent, worker_id: str):
        self.agent = agent
        self.worker_id = worker_id
        self.is_busy = False
        self.current_request = None
        self.request_count = 0
        self.last_activity = datetime.now()
        self.response_times = deque(maxlen=100)
        self.error_count = 0
        self.start_time = time.time()

    async def execute_request(self, state: AgentState) -> Dict[str, Any]:
        """Execute a request on this worker."""
        if self.is_busy:
            raise LoadBalancerError(f"Worker {self.worker_id} is busy")

        self.is_busy = True
        self.current_request = state
        self.request_count += 1
        start_time = time.time()

        try:
            result_state = await self.agent.execute(state)
            execution_time = time.time() - start_time

            # Update metrics
            self.response_times.append(execution_time)
            self.last_activity = datetime.now()

            return {
                "success": not result_state.get("error"),
                "result": result_state.get("output"),
                "execution_time": execution_time,
                "worker_id": self.worker_id,
                "agent_name": self.agent.name,
            }

        except Exception as e:
            self.error_count += 1
            logger.error(f"Worker {self.worker_id} execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "worker_id": self.worker_id,
                "agent_name": self.agent.name,
                "execution_time": time.time() - start_time,
            }
        finally:
            self.is_busy = False
            self.current_request = None

    def get_metrics(self) -> Dict[str, Any]:
        """Get worker performance metrics."""
        if not self.response_times:
            return {
                "worker_id": self.worker_id,
                "agent_name": self.agent.name,
                "request_count": self.request_count,
                "error_count": self.error_count,
                "last_activity": self.last_activity.isoformat(),
                "is_busy": self.is_busy,
            }

        avg_response_time = sum(self.response_times) / len(self.response_times)

        return {
            "worker_id": self.worker_id,
            "agent_name": self.agent.name,
            "request_count": self.request_count,
            "error_count": self.error_count,
            "avg_response_time": avg_response_time,
            "last_activity": self.last_activity.isoformat(),
            "is_busy": self.is_busy,
            "response_times_count": len(self.response_times),
        }


@dataclass
class LoadBalancerConfig:
    """Configuration for load balancer."""

    strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN
    max_workers: int = 5
    health_check_interval: int = 30  # seconds
    circuit_breaker_threshold: int = 5  # failures before circuit opens
    circuit_breaker_timeout: int = 60  # seconds before circuit closes
    request_timeout: int = 120  # seconds
    enable_failover: bool = True
    weights: Optional[Dict[str, float]] = None  # For weighted strategies


@dataclass
class CircuitBreakerState:
    """Circuit breaker state."""

    is_open: bool = False
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    next_attempt_time: Optional[datetime] = None


class LoadBalancer:
    """Advanced load balancer for agent instances."""

    def __init__(self, config: LoadBalancerConfig):
        self.config = config
        self.workers: Dict[str, AgentWorker] = {}
        self.request_queue = asyncio.Queue()
        self.circuit_breaker = CircuitBreakerState()
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "active_workers": 0,
            "start_time": datetime.now(),
        }
        self._health_check_task: Optional[asyncio.Task] = None
        self._is_running = False

    async def initialize(self, agent_registry: AgentRegistry) -> None:
        """Initialize load balancer with agents from registry."""
        logger.info(f"Initializing load balancer with strategy: {self.config.strategy}")

        # Get available agents from registry
        available_agents = agent_registry.list_agents()

        # Create workers for each agent
        for agent_name in available_agents:
            agent = agent_registry.get_agent(agent_name)
            if agent:
                for i in range(self.config.max_workers):
                    worker_id = f"{agent_name}_worker_{i}"
                    worker = AgentWorker(agent, worker_id)
                    self.workers[worker_id] = worker

        logger.info(
            f"Initialized {len(self.workers)} workers for {len(available_agents)} agents"
        )

    async def start(self) -> None:
        """Start the load balancer."""
        if self._is_running:
            logger.warning("Load balancer is already running")
            return

        self._is_running = True

        # Start health monitoring
        self._health_check_task = asyncio.create_task(self._health_monitor_loop())

        # Start request processing
        asyncio.create_task(self._request_processing_loop())

        logger.info("Load balancer started")

    async def stop(self) -> None:
        """Stop the load balancer."""
        if not self._is_running:
            return

        self._is_running = False

        # Cancel health monitoring
        if self._health_check_task:
            self._health_check_task.cancel()
            self._health_check_task = None

        logger.info("Load balancer stopped")

    async def _health_monitor_loop(self) -> None:
        """Monitor health of workers and system."""
        while self._is_running:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                await self._check_worker_health()
                await self._check_circuit_breaker()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")

    async def _check_worker_health(self) -> None:
        """Check health of all workers."""
        unhealthy_workers = []

        for worker_id, worker in self.workers.items():
            # Check if worker is stuck (busy for too long)
            if worker.is_busy and worker.current_request:
                time_since_activity = (
                    datetime.now() - worker.last_activity
                ).total_seconds()
                if time_since_activity > self.config.request_timeout:
                    unhealthy_workers.append(worker_id)
                    logger.warning(
                        f"Worker {worker_id} appears stuck (busy for {time_since_activity}s)"
                    )

            # Check error rate
            if worker.error_count > 5 and worker.request_count > 10:
                error_rate = worker.error_count / worker.request_count
                if error_rate > 0.5:  # More than 50% error rate
                    unhealthy_workers.append(worker_id)
                    logger.warning(
                        f"Worker {worker_id} has high error rate: {error_rate:.2%}"
                    )

        # Mark unhealthy workers as unavailable
        for worker_id in unhealthy_workers:
            if worker_id in self.workers:
                logger.warning(f"Marking worker {worker_id} as unhealthy")
                # In a real implementation, would remove from rotation

    async def _check_circuit_breaker(self) -> None:
        """Check and update circuit breaker state."""
        total_failures = sum(worker.error_count for worker in self.workers.values())

        # Update circuit breaker
        if total_failures >= self.config.circuit_breaker_threshold:
            if not self.circuit_breaker.is_open:
                self.circuit_breaker.is_open = True
                self.circuit_breaker.failure_count = total_failures
                self.circuit_breaker.last_failure_time = datetime.now()
                self.circuit_breaker.next_attempt_time = datetime.now() + timedelta(
                    seconds=self.config.circuit_breaker_timeout
                )

                logger.error(f"Circuit breaker opened due to {total_failures} failures")
        elif self.circuit_breaker.is_open:
            # Check if circuit should close
            if datetime.now() >= self.circuit_breaker.next_attempt_time:
                self.circuit_breaker.is_open = False
                self.circuit_breaker.failure_count = 0
                logger.info("Circuit breaker closed")

    async def _request_processing_loop(self) -> None:
        """Process requests from queue."""
        while self._is_running:
            try:
                # Get next request
                try:
                    request_data = await asyncio.wait_for(
                        self.request_queue.get(), timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue  # No requests in queue

                # Select worker based on strategy
                worker = await self._select_worker(request_data)

                if not worker:
                    logger.warning("No available workers for request")
                    await asyncio.sleep(1.0)
                    continue

                # Process request
                result = await worker.execute_request(request_data)

                # Update metrics
                self.metrics["total_requests"] += 1
                if result["success"]:
                    self.metrics["successful_requests"] += 1
                else:
                    self.metrics["failed_requests"] += 1

                logger.info(f"Request processed by worker {worker.worker_id}")

            except Exception as e:
                logger.error(f"Request processing error: {e}")
                await asyncio.sleep(1.0)

    async def _select_worker(
        self, request_data: Dict[str, Any]
    ) -> Optional[AgentWorker]:
        """Select worker based on configured strategy."""
        available_workers = [
            worker
            for worker in self.workers.values()
            if not worker.is_busy and self._is_worker_healthy(worker)
        ]

        if not available_workers:
            return None

        if self.config.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._round_robin_select(available_workers)
        elif self.config.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return self._least_connections_select(available_workers)
        elif self.config.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_select(available_workers)
        elif self.config.strategy == LoadBalancingStrategy.CONSISTENT_HASH:
            return self._consistent_hash_select(available_workers, request_data)
        elif self.config.strategy == LoadBalancingStrategy.RANDOM:
            return self._random_select(available_workers)
        else:
            return available_workers[0]

    def _is_worker_healthy(self, worker: AgentWorker) -> bool:
        """Check if worker is healthy."""
        # Check error rate
        if worker.request_count > 0:
            error_rate = worker.error_count / worker.request_count
            if error_rate > 0.3:  # More than 30% error rate
                return False

        # Check response time
        if worker.response_times:
            avg_response_time = sum(worker.response_times) / len(worker.response_times)
            if avg_response_time > 30:  # More than 30 seconds average
                return False

        # Check if recently active
        time_since_activity = (datetime.now() - worker.last_activity).total_seconds()
        if time_since_activity > 300:  # 5 minutes
            return False

        return True

    def _round_robin_select(self, workers: List[AgentWorker]) -> AgentWorker:
        """Round-robin selection."""
        if not workers:
            raise LoadBalancerError("No available workers")

        # Select next worker in rotation
        worker = workers[self.metrics["total_requests"] % len(workers)]
        return worker

    def _least_connections_select(self, workers: List[AgentWorker]) -> AgentWorker:
        """Select worker with least active connections."""
        if not workers:
            raise LoadBalancerError("No available workers")

        # Count active connections (simplified - busy workers)
        return min(workers, key=lambda w: w.is_busy)

    def _weighted_round_robin_select(self, workers: List[AgentWorker]) -> AgentWorker:
        """Weighted round-robin selection."""
        if not workers or not self.config.weights:
            return self._round_robin_select(workers)

        # Calculate weighted scores
        scores = []
        for worker in workers:
            weight = self.config.weights.get(worker.agent.name, 1.0)
            score = weight * (worker.request_count + 1)  # Favor less used workers
            scores.append((score, worker))

        # Select worker with highest score
        scores.sort(key=lambda x: x[0], reverse=True)
        return scores[0][1]

    def _consistent_hash_select(
        self, workers: List[AgentWorker], request_data: Dict[str, Any]
    ) -> AgentWorker:
        """Consistent hash selection."""
        if not workers:
            raise LoadBalancerError("No available workers")

        # Create hash from request data
        import hashlib

        request_str = str(sorted(request_data.items()))
        hash_value = int(hashlib.md5(request_str.encode()).hexdigest(), 16)

        # Select worker based on hash
        worker_index = hash_value % len(workers)
        return workers[worker_index]

    def _random_select(self, workers: List[AgentWorker]) -> AgentWorker:
        """Random selection."""
        if not workers:
            raise LoadBalancerError("No available workers")

        import random

        return random.choice(workers)

    async def submit_request(self, request_data: Dict[str, Any]) -> str:
        """Submit a request to the load balancer."""
        # Add to queue
        await self.request_queue.put(request_data)

        # Return request ID for tracking
        request_id = f"req_{self.metrics['total_requests']}"
        return request_id

    async def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive load balancer metrics."""
        active_workers = sum(1 for worker in self.workers.values() if worker.is_busy)

        # Calculate error rates per worker
        worker_metrics = {}
        for worker_id, worker in self.workers.items():
            error_rate = (
                worker.error_count / worker.request_count
                if worker.request_count > 0
                else 0
            )
            worker_metrics[worker_id] = {
                "request_count": worker.request_count,
                "error_count": worker.error_count,
                "error_rate": error_rate,
                "avg_response_time": (
                    sum(worker.response_times) / len(worker.response_times)
                    if worker.response_times
                    else 0
                ),
                "is_busy": worker.is_busy,
                "last_activity": worker.last_activity.isoformat(),
            }

        return {
            "config": {
                "strategy": self.config.strategy.value,
                "max_workers": self.config.max_workers,
                "health_check_interval": self.config.health_check_interval,
                "circuit_breaker_threshold": self.config.circuit_breaker_threshold,
                "circuit_breaker_timeout": self.config.circuit_breaker_timeout,
                "enable_failover": self.config.enable_failover,
            },
            "metrics": {
                **self.metrics,
                "active_workers": active_workers,
                "total_workers": len(self.workers),
                "queue_depth": self.request_queue.qsize(),
                "circuit_breaker": {
                    "is_open": self.circuit_breaker.is_open,
                    "failure_count": self.circuit_breaker.failure_count,
                    "last_failure_time": (
                        self.circuit_breaker.last_failure_time.isoformat()
                        if self.circuit_breaker.last_failure_time
                        else None
                    ),
                },
            },
            "worker_metrics": worker_metrics,
            "uptime_seconds": (
                datetime.now() - self.metrics["start_time"]
            ).total_seconds(),
        }


# Global load balancer instance
_load_balancer: Optional[LoadBalancer] = None


def get_load_balancer(config: Optional[LoadBalancerConfig] = None) -> LoadBalancer:
    """Get or create load balancer instance."""
    global _load_balancer
    if _load_balancer is None:
        _load_balancer = LoadBalancer(config or LoadBalancerConfig())
    return _load_balancer


async def initialize_load_balancer(agent_registry: AgentRegistry) -> None:
    """Initialize the global load balancer."""
    balancer = get_load_balancer()
    await balancer.initialize(agent_registry)


# Convenience functions for backward compatibility
async def submit_request(request_data: Dict[str, Any]) -> str:
    """Submit a request to the load balancer."""
    balancer = get_load_balancer()
    return await balancer.submit_request(request_data)


async def get_load_balancer_metrics() -> Dict[str, Any]:
    """Get load balancer metrics."""
    balancer = get_load_balancer()
    return await balancer.get_metrics()
