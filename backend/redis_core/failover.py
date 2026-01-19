"""
Redis failover manager for high availability.

Provides automatic failover detection, node promotion,
and cluster recovery mechanisms.
"""

import asyncio
import logging
import random
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from .client import get_redis
from .cluster import ClusterNode, ClusterNodeStatus, ClusterRole, RedisClusterManager
from .critical_fixes import SecureErrorHandler


class FailoverType(Enum):
    """Failover type enumeration."""

    PRIMARY_FAILURE = "primary_failure"
    NETWORK_PARTITION = "network_partition"
    NODE_CRASH = "node_crash"
    MANUAL_FAILOVER = "manual_failover"
    HEALTH_DEGRADATION = "health_degradation"


class FailoverState(Enum):
    """Failover state enumeration."""

    NORMAL = "normal"
    DETECTING = "detecting"
    INITIATING = "initiating"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class FailoverEvent:
    """Failover event tracking."""

    event_id: str
    failover_type: FailoverType
    state: FailoverState
    cluster_id: str

    # Event details
    failed_node_id: Optional[str] = None
    new_primary_id: Optional[str] = None
    old_primary_id: Optional[str] = None

    # Timing
    detected_at: datetime
    initiated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None

    # Results
    success: bool = False
    error_message: Optional[str] = None
    affected_nodes: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.failover_type, str):
            self.failover_type = FailoverType(self.failover_type)
        if isinstance(self.state, str):
            self.state = FailoverState(self.state)
        if isinstance(self.detected_at, str):
            self.detected_at = datetime.fromisoformat(self.detected_at)
        if isinstance(self.initiated_at, str):
            self.initiated_at = datetime.fromisoformat(self.initiated_at)
        if isinstance(self.completed_at, str):
            self.completed_at = datetime.fromisoformat(self.completed_at)

    def mark_initiated(self):
        """Mark failover as initiated."""
        self.state = FailoverState.INITIATING
        self.initiated_at = datetime.now()

    def mark_in_progress(self):
        """Mark failover as in progress."""
        self.state = FailoverState.IN_PROGRESS

    def mark_completed(self, success: bool, error_message: str = None):
        """Mark failover as completed."""
        self.state = FailoverState.COMPLETED
        self.completed_at = datetime.now()
        self.success = success
        self.error_message = error_message

        if self.initiated_at and self.completed_at:
            self.duration_seconds = (
                self.completed_at - self.initiated_at
            ).total_seconds()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)

        # Convert enums to strings
        data["failover_type"] = self.failover_type.value
        data["state"] = self.state.value

        # Convert datetime objects
        data["detected_at"] = self.detected_at.isoformat()
        if self.initiated_at:
            data["initiated_at"] = self.initiated_at.isoformat()
        if self.completed_at:
            data["completed_at"] = self.completed_at.isoformat()

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FailoverEvent":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class FailoverConfig:
    """Failover configuration."""

    # Detection settings
    health_check_interval: int = 10  # seconds
    failure_threshold: int = 3  # consecutive failures
    network_timeout: int = 5  # seconds

    # Election settings
    election_timeout: int = 30  # seconds
    quorum_size: int = 2  # nodes required for quorum

    # Retry settings
    max_retry_attempts: int = 3
    retry_delay_seconds: int = 5

    # Timing settings
    failover_timeout: int = 60  # seconds
    stabilization_delay: int = 30  # seconds

    # Notification settings
    enable_notifications: bool = True
    notification_webhook: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FailoverConfig":
        """Create from dictionary."""
        return cls(**data)


class FailoverDetector:
    """Detects failover conditions."""

    def __init__(self, cluster_manager: RedisClusterManager, config: FailoverConfig):
        self.cluster_manager = cluster_manager
        self.config = config
        self.logger = logging.getLogger("failover_detector")

        # Detection state
        self._last_health_check = {}
        self._failure_counts = {}
        self._network_partitions = set()

    async def check_primary_health(self) -> bool:
        """Check if primary node is healthy."""
        if not self.cluster_manager.primary_node:
            return False

        primary = self.cluster_manager.nodes.get(self.cluster_manager.primary_node)
        if not primary:
            return False

        # Check consecutive failures
        failure_count = self._failure_counts.get(self.cluster_manager.primary_node, 0)

        if failure_count >= self.config.failure_threshold:
            return False

        # Check network partition
        if self.cluster_manager.primary_node in self._network_partitions:
            return False

        return primary.is_healthy()

    async def detect_network_partition(self) -> List[str]:
        """Detect network partitions."""
        partitions = []

        # Check connectivity between nodes
        online_nodes = [
            node_id
            for node_id, node in self.cluster_manager.nodes.items()
            if node.is_healthy()
        ]

        if len(online_nodes) < 2:
            return partitions

        # Test connectivity between nodes
        for i, node1_id in enumerate(online_nodes):
            for node2_id in online_nodes[i + 1 :]:
                if not await self._test_node_connectivity(node1_id, node2_id):
                    partitions.append(node1_id)
                    partitions.append(node2_id)

        # Update network partitions
        self._network_partitions = set(partitions)

        return partitions

    async def _test_node_connectivity(self, node1_id: str, node2_id: str) -> bool:
        """Test connectivity between two nodes."""
        try:
            # This would implement actual connectivity test
            # For now, simulate based on health status
            node1 = self.cluster_manager.nodes.get(node1_id)
            node2 = self.cluster_manager.nodes.get(node2_id)

            return node1 and node2 and node1.is_healthy() and node2.is_healthy()

        except Exception:
            return False

    def record_failure(self, node_id: str):
        """Record a node failure."""
        self._failure_counts[node_id] = self._failure_counts.get(node_id, 0) + 1
        self.logger.warning(
            f"Recorded failure for node {node_id} (count: {self._failure_counts[node_id]})"
        )

    def reset_failure_count(self, node_id: str):
        """Reset failure count for a node."""
        if node_id in self._failure_counts:
            del self._failure_counts[node_id]
        if node_id in self._network_partitions:
            self._network_partitions.discard(node_id)

        self.logger.info(f"Reset failure count for node {node_id}")


class FailoverManager:
    """Manages Redis cluster failover operations."""

    def __init__(self, cluster_manager: RedisClusterManager, config: FailoverConfig):
        self.cluster_manager = cluster_manager
        self.config = config
        self.detector = FailoverDetector(cluster_manager, config)
        self.error_handler = SecureErrorHandler()

        # Failover state
        self._current_failover: Optional[FailoverEvent] = None
        self._failover_history: List[FailoverEvent] = []
        self._is_failover_in_progress = False

        # Monitoring
        self.logger = logging.getLogger("failover_manager")

        # State tracking
        self._last_check = datetime.now()

    async def start_monitoring(self):
        """Start failover monitoring."""
        self.logger.info("Starting failover monitoring")

        while True:
            try:
                await self._check_failover_conditions()
                await asyncio.sleep(self.config.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Failover monitoring error: {e}")
                await asyncio.sleep(5)

    async def _check_failover_conditions(self):
        """Check for failover conditions."""
        current_time = datetime.now()

        # Check primary health
        if not await self.detector.check_primary_health():
            if not self._is_failover_in_progress:
                await self._initiate_failover(FailoverType.PRIMARY_FAILURE)

        # Check network partitions
        partitions = await self.detector.detect_network_partition()
        if partitions and not self._is_failover_in_progress:
            await self._initiate_failover(FailoverType.NETWORK_PARTITION)

        # Check for node crashes
        crashed_nodes = [
            node_id
            for node_id, node in self.cluster_manager.nodes.items()
            if node.status == ClusterNodeStatus.FAILED
        ]

        if crashed_nodes and not self._is_failover_in_progress:
            await self._initiate_failover(FailoverType.NODE_CRASH)

        self._last_check = current_time

    async def _initiate_failover(self, failover_type: FailoverType):
        """Initiate failover process."""
        if self._is_failover_in_progress:
            self.logger.warning("Failover already in progress, ignoring new request")
            return

        self._is_failover_in_progress = True

        # Create failover event
        event_id = f"failover_{int(time.time())}"
        event = FailoverEvent(
            event_id=event_id,
            failover_type=failover_type,
            state=FailoverState.DETECTING,
            cluster_id=self.cluster_manager.config.cluster_id,
            detected_at=datetime.now(),
            old_primary_id=self.cluster_manager.primary_node,
        )

        self._current_failover = event
        self._failover_history.append(event)

        try:
            # Log security event
            self.error_handler.log_security_event(
                event_type="failover_detected",
                severity="HIGH",
                description=f"Redis failover detected: {failover_type.value}",
                context={
                    "cluster_id": self.cluster_manager.config.cluster_id,
                    "failover_type": failover_type.value,
                    "primary_node": self.cluster_manager.primary_node,
                },
            )

            # Initiate failover
            await self._execute_failover(event)

        except Exception as e:
            self.logger.error(f"Failover execution failed: {e}")
            event.mark_completed(False, str(e))
            self._is_failover_in_progress = False
            self._current_failover = None

    async def _execute_failover(self, event: FailoverEvent):
        """Execute failover process."""
        self.logger.info(
            f"Executing failover {event.event_id} of type {event.failover_type.value}"
        )

        try:
            # Mark as initiated
            event.mark_initiated()
            await self._save_failover_event(event)

            # Mark as in progress
            event.mark_in_progress()
            await self._save_failover_event(event)

            # Execute failover based on type
            if event.failover_type == FailoverType.PRIMARY_FAILURE:
                await self._execute_primary_failover(event)
            elif event.failover_type == Failover.NETWORK_PARTITION:
                await self._execute_network_partition_failover(event)
            elif event.failover_type == Failover.NODE_CRASH:
                await self._execute_node_crash_failover(event)
            elif event.failover_type == Failover.MANUAL_FAILOVER:
                await self._execute_manual_failover(event)

            # Mark as completed
            event.mark_completed(True)
            self._is_failover_in_progress = False
            self._current_failover = None

            # Wait for stabilization
            await asyncio.sleep(self.config.stabilization_delay)

            # Verify cluster health
            await self._verify_cluster_health()

            # Send notification
            if self.config.enable_notifications:
                await self._send_failover_notification(event)

            self.logger.info(f"Failover {event.event_id} completed successfully")

        except Exception as e:
            self.logger.error(f"Failover execution failed: {e}")
            event.mark_completed(False, str(e))
            self._is_failover_in_progress = False
            self._current_failover = None

            # Log security event
            self.error_handler.log_security_event(
                event_type="failover_failed",
                severity="CRITICAL",
                description=f"Redis failover failed: {str(e)}",
                context={
                    "cluster_id": self.cluster_manager.config.cluster_id,
                    "failover_type": event.failover_type.value,
                    "event_id": event.event_id,
                },
            )

        finally:
            await self._save_failover_event(event)

    async def _execute_primary_failover(self, event: FailoverEvent):
        """Execute primary node failover."""
        self.logger.info("Executing primary node failover")

        # Record failed primary
        if self.cluster_manager.primary_node:
            event.failed_node_id = self.cluster_manager.primary_node
            self.detector.record_failure(self.cluster_manager.primary_node)

        # Elect new primary
        await self.cluster_manager._elect_primary()
        event.new_primary_id = self.cluster_manager.primary_node

        # Update replica configurations
        await self.cluster_manager._update_replica_configurations()

        # Update affected nodes
        event.affected_nodes = list(self.cluster_manager.nodes.keys())

    async def _execute_network_partition_failover(self, event: FailoverEvent):
        """Execute network partition failover."""
        self.logger.info("Executing network partition failover")

        # Get partitioned nodes
        partitions = self.detector._network_partitions

        # Isolate partitioned nodes
        for node_id in partitions:
            if node_id in self.cluster_manager.nodes:
                node = self.cluster_manager.nodes[node_id]
                node.status = ClusterNodeStatus.OFFLINE
                self.detector.record_failure(node_id)

        # Elect new primary from available nodes
        available_nodes = [
            node_id
            for node_id, node in self.cluster_manager.nodes.items()
            if node_id not in partitions and node.is_healthy()
        ]

        if available_nodes:
            # Select new primary
            new_primary = min(
                available_nodes,
                key=lambda nid: self.cluster_manager.nodes[nid].response_time_ms,
            )

            # Update roles
            for node_id, node in self.cluster_manager.nodes.items():
                if node_id == new_primary:
                    node.role = ClusterRole.PRIMARY
                    self.cluster_manager.primary_node = node_id
                    self.cluster_manager.replica_nodes.discard(node_id)
                else:
                    node.role = ClusterRole.REPLICA
                    self.cluster_manager.replica_nodes.add(node_id)

            event.new_primary_id = new_primary
            event.affected_nodes = partitions

        self.logger.info(
            f"Network partition failover completed. New primary: {new_primary}"
        )

    async def _execute_node_crash_failover(self, event: FailoverEvent):
        """Execute node crash failover."""
        self.logger.info("Executing node crash failover")

        # Remove crashed nodes
        crashed_nodes = [
            node_id
            for node_id, node in self.cluster_manager.nodes.items()
            if node.status == ClusterNodeStatus.FAILED
        ]

        for node_id in crashed_nodes:
            await self.cluster_manager.remove_node(node_id)
            event.affected_nodes.append(node_id)

        # If primary was crashed, elect new one
        if event.failed_node_id == self.cluster_manager.primary_node:
            await self.cluster_manager._elect_primary()
            event.new_primary_id = self.cluster_manager.primary_name
            await self.cluster_manager._update_replica_configurations()

        self.logger.info(
            f"Node crash failover completed. Removed nodes: {crashed_nodes}"
        )

    async def _execute_manual_failover(self, event: FailoverEvent):
        """Execute manual failover."""
        self.logger.info("Executing manual failover")

        # Force elect new primary
        await self.cluster_manager._elect_primary()
        event.new_primary_id = self.cluster_manager.primary_node
        await self.cluster_manager._update_replica_configurations()

        event.affected_nodes = list(self.cluster_manager.nodes.keys())

        self.logger.info(
            f"Manual failover completed. New primary: {event.new_primary_id}"
        )

    async def _verify_cluster_health(self):
        """Verify cluster health after failover."""
        self.logger.info("Verifying cluster health after failover")

        # Check if we have a healthy primary
        if not self.cluster_manager.primary_node:
            raise Exception("No primary node available after failover")

        primary = self.cluster_manager.nodes[self.cluster_manager.primary_node]
        if not primary.is_healthy():
            raise Exception(
                f"Primary node {self.cluster_manager.primary_node} is unhealthy after failover"
            )

        # Check if we have minimum required nodes
        min_nodes = self.cluster_manager.config.min_nodes
        online_nodes = len(
            [node for node in self.cluster_manager.nodes.values() if node.is_healthy()]
        )

        if online_nodes < min_nodes:
            raise Exception(f"Insufficient healthy nodes: {online_nodes}/{min_nodes}")

        self.logger.info(
            f"Cluster health verified. Primary: {self.cluster_manager.primary_node}, Online nodes: {online_nodes}"
        )

    async def _save_failover_event(self, event: FailoverEvent):
        """Save failover event to Redis."""
        event_key = (
            f"failover:{self.cluster_manager.config.cluster_id}:{event.event_id}"
        )
        await self.cluster_manager.redis.set_json(
            event_key, event.to_dict(), ex=86400 * 7
        )  # 7 days

    async def _send_failover_notification(self, event: FailoverEvent):
        """Send failover notification."""
        if not self.config.notification_webhook:
            return

        # This would integrate with the webhook service
        # For now, just log the notification
        self.logger.info(
            f"Failover notification would be sent to {self.config.notification_webhook}"
        )

        notification_data = {
            "event_type": "failover_completed",
            "cluster_id": event.cluster_id,
            "failover_type": event.failover_type.value,
            "success": event.success,
            "duration_seconds": event.duration_seconds,
            "old_primary_id": event.old_primary_id,
            "new_primary_id": event.new_primary_id,
            "affected_nodes": event.affected_nodes,
            "timestamp": event.completed_at.isoformat() if event.completed_at else None,
        }

        # Store notification for debugging
        notification_key = f"notification:{event.event_id}"
        await self.cluster_manager.redis.set_json(
            notification_key, notification_data, ex=3600
        )  # 1 hour

    async def get_failover_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get failover history."""
        pattern = f"failover:{self.cluster_manager.config.cluster_id}:*"
        keys = await self.cluster_manager.redis.keys(pattern)

        events = []
        for key in sorted(keys[:limit]):
            data = await self.cluster_manager.redis.get_json(key)
            if data:
                events.append(FailoverEvent.from_dict(data))

        return [event.to_dict() for event in events]

    async def get_current_failover(self) -> Optional[Dict[str, Any]]:
        """Get current failover event."""
        if not self._current_failover:
            return None

        return self._current_failover.to_dict()

    async def manual_failover(self, reason: str = "Manual failover requested"):
        """Initiate manual failover."""
        if self._is_failover_in_progress:
            raise Exception("Failover already in progress")

        await self._initiate_failover(FailoverType.MANUAL_FAILOVER)

        return await self.get_current_failover()

    async def get_failover_stats(self) -> Dict[str, Any]:
        """Get failover statistics."""
        history = await self.get_failover_history()

        stats = {
            "total_failovers": len(history),
            "successful_failovers": len(
                [e for e in history if e.get("success", False)]
            ),
            "failed_failovers": len([e for e in history if not e.get("success", True)]),
            "last_failover": history[-1] if history else None,
            "failover_types": {},
            "avg_duration_seconds": 0.0,
            "is_failover_in_progress": self._is_failover_in_progress,
        }

        # Calculate statistics
        if history:
            stats["failover_types"] = {}
            for event in history:
                failover_type = event.get("failover_type", "unknown")
                if failover_type not in stats["failover_types"]:
                    stats["failover_types"][failover_type] = 0
                stats["failover_types"][failover_type] += 1

            completed_failovers = [e for e in history if e.get("completed_at")]
            if completed_failovers:
                durations = [
                    e.get("duration_seconds", 0)
                    for e in completed_failovers
                    if e.get("duration_seconds") is not None
                ]
                if durations:
                    stats["avg_duration_seconds"] = sum(durations) / len(durations)

        return stats


class FailoverOrchestrator:
    """Orchestrates failover across multiple clusters."""

    def __init__(self):
        self.clusters: Dict[str, RedisClusterManager] = {}
        self.failover_managers: Dict[str, FailoverManager] = {}
        self.logger = logging.getLogger("failover_orchestrator")

    def add_cluster(
        self,
        cluster_manager: RedisClusterManager,
        config: Optional[FailoverConfig] = None,
    ):
        """Add a cluster to orchestration."""
        cluster_id = cluster_manager.config.cluster_id

        self.clusters[cluster_id] = cluster_manager

        if config:
            self.failover_managers[cluster_id] = FailoverManager(
                cluster_manager, config
            )
        else:
            # Use default config
            config = FailoverConfig()
            self.failover_managers[cluster_id] = FailoverManager(
                cluster_manager, config
            )

        self.logger.info(f"Added cluster {cluster_id} to failover orchestration")

    async def start_monitoring(self):
        """Start monitoring all clusters."""
        tasks = []

        for cluster_id, manager in self.failover_managers.items():
            task = asyncio.create_task(manager.start_monitoring())
            tasks.append((cluster_id, task))

        self.logger.info(f"Started failover monitoring for {len(tasks)} clusters")

        # Wait for all tasks to complete (they won't unless cancelled)
        await asyncio.gather(*[task for _, task in tasks])

    async def get_cluster_status(self, cluster_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific cluster."""
        if cluster_id not in self.clusters:
            return None

        return await self.clusters[cluster_id].get_cluster_status()

    async def get_all_cluster_status(self) -> Dict[str, Any]:
        """Get status of all clusters."""
        status = {}

        for cluster_id, cluster in self.clusters.items():
            try:
                status[cluster_id] = await cluster.get_cluster_status()
            except Exception as e:
                status[cluster_id] = {
                    "error": str(e),
                    "cluster_id": cluster_id,
                    "is_healthy": False,
                }

        return status

    async def manual_failover(
        self, cluster_id: str, reason: str = "Manual failover requested"
    ):
        """Initiate manual failover for a specific cluster."""
        if cluster_id not in self.failover_managers:
            raise ValueError(f"Cluster {cluster_id} not found")

        manager = self.failover_managers[cluster_id]
        return await manager.manual_failover(reason)

    async def get_failover_stats(self, cluster_id: str) -> Dict[str, Any]:
        """Get failover statistics for a specific cluster."""
        if cluster_id not in self.failover_managers:
            return {}

        return await self.failover_managers[cluster_id].get_failover_stats()

    async def get_all_failover_stats(self) -> Dict[str, Any]:
        """Get failover statistics for all clusters."""
        stats = {}

        for cluster_id, manager in self.failover_managers.items():
            try:
                stats[cluster_id] = await manager.get_failover_stats()
            except Exception as e:
                stats[cluster_id] = {"error": str(e)}

        return stats
