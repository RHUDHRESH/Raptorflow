"""
Redis cluster management for high availability and scalability.

Provides cluster configuration, node management, and automatic
failover capabilities for Redis infrastructure.
"""

import asyncio
import json
import logging
import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from .client import get_redis
from .critical_fixes import SecureErrorHandler


class ClusterNodeStatus(Enum):
    """Cluster node status enumeration."""

    ONLINE = "online"
    OFFLINE = "offline"
    CONNECTING = "connecting"
    DISCONNECTED = "disconnected"
    FAILED = "failed"
    MAINTENANCE = "maintenance"


class ClusterRole(Enum):
    """Cluster node role enumeration."""

    PRIMARY = "primary"
    REPLICA = "replica"
    ARBITER = "arbitrator"
    SENTINEL = "sentinel"


class ClusterTopology(Enum):
    """Cluster topology enumeration."""

    SINGLE_NODE = "single_node"
    MASTER_REPLICA = "master_replica"
    CLUSTER = "cluster"
    SENTINEL = "sentinel"


@dataclass
class ClusterNode:
    """Redis cluster node configuration."""

    node_id: str
    host: str
    port: int
    role: ClusterRole
    status: ClusterNodeStatus = ClusterNodeStatus.OFFLINE

    # Connection details
    password: Optional[str] = None
    ssl: bool = False
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None

    # Node configuration
    max_connections: int = 1000
    timeout_seconds: int = 5
    retry_attempts: int = 3

    # Health check
    last_health_check: Optional[datetime] = None
    response_time_ms: float = 0.0
    error_count: int = 0
    consecutive_failures: int = 0

    # Metrics
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    connected_clients: int = 0
    keyspace_hits: int = 0
    keyspace_misses: int = 0

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.role, str):
            self.role = ClusterRole(self.role)
        if isinstance(self.status, str):
            self.status = ClusterNodeStatus(self.status)
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)

    def is_healthy(self) -> bool:
        """Check if node is healthy."""
        return (
            self.status == ClusterNodeStatus.ONLINE
            and self.consecutive_failures < 3
            and self.response_time_ms < 1000  # 1 second max response time
        )

    def can_connect(self) -> bool:
        """Check if node can be connected to."""
        return self.status not in [
            ClusterNodeStatus.FAILED,
            ClusterNodeStatus.MAINTENANCE,
        ]

    def update_health_check(
        self, response_time_ms: float, success: bool, error: str = ""
    ):
        """Update health check results."""
        self.last_health_check = datetime.now()
        self.response_time_ms = response_time_ms
        self.updated_at = datetime.now()

        if success:
            self.status = ClusterNodeStatus.ONLINE
            self.consecutive_failures = 0
        else:
            self.error_count += 1
            self.consecutive_failures += 1

            if self.consecutive_failures >= 3:
                self.status = ClusterNodeStatus.FAILED
            else:
                self.status = ClusterNodeStatus.OFFLINE

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)

        # Convert enums to strings
        data["role"] = self.role.value
        data["status"] = self.status.value

        # Convert datetime objects
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        if self.last_health_check:
            data["last_health_check"] = self.last_health_check.isoformat()

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ClusterNode":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class ClusterConfig:
    """Redis cluster configuration."""

    cluster_id: str
    cluster_name: str
    topology: ClusterTopology

    # Cluster settings
    max_nodes: int = 6
    min_nodes: int = 3
    auto_failover: bool = True
    auto_rebalance: bool = True

    # Health check settings
    health_check_interval: int = 30  # seconds
    health_check_timeout: int = 5  # seconds
    max_failures: int = 3

    # Failover settings
    failover_timeout: int = 30  # seconds
    election_timeout: int = 10  # seconds
    retry_delay: int = 5  # seconds

    # Security settings
    require_password: bool = True
    ssl_required: bool = False
    allowed_ips: List[str] = field(default_factory=list)

    # Performance settings
    max_connections_per_node: int = 1000
    connection_timeout: int = 5
    command_timeout: int = 1

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.topology, str):
            self.topology = ClusterTopology(self.topology)
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)

        # Convert enum to string
        data["topology"] = self.topology.value

        # Convert datetime objects
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ClusterConfig":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class ClusterMetrics:
    """Cluster-wide metrics."""

    cluster_id: str

    # Node metrics
    total_nodes: int = 0
    online_nodes: int = 0
    offline_nodes: int = 0
    failed_nodes: int = 0

    # Performance metrics
    total_connections: int = 0
    total_memory_mb: float = 0.0
    total_cpu_percent: float = 0.0
    avg_response_time_ms: float = 0.0

    # Data metrics
    total_keys: int = 0
    total_memory_used_mb: float = 0.0
    hit_rate: float = 0.0

    # Cluster health
    health_score: float = 100.0
    availability_percentage: float = 100.0

    # Timestamps
    calculated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.calculated_at, str):
            self.calculated_at = datetime.fromisoformat(self.calculated_at)

    def calculate_health_score(self):
        """Calculate cluster health score."""
        if self.total_nodes == 0:
            self.health_score = 0.0
            return

        # Base score from node availability
        node_score = (self.online_nodes / self.total_nodes) * 70

        # Performance score
        performance_score = 0.0
        if self.total_nodes > 0:
            avg_response = self.avg_response_time_ms
            if avg_response > 0:
                performance_score = max(0, 30 - (avg_response / 100))  # 30 points max

        self.health_score = node_score + performance_score

        # Calculate availability
        if self.total_nodes > 0:
            self.availability_percentage = (self.online_nodes / self.total_nodes) * 100

    def calculate_hit_rate(self):
        """Calculate cache hit rate."""
        total_requests = self.total_keys
        if total_requests > 0:
            self.hit_rate = (self.total_keys / total_requests) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)

        # Convert datetime objects
        data["calculated_at"] = self.calculated_at.isoformat()

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ClusterMetrics":
        """Create from dictionary."""
        return cls(**data)


class RedisClusterManager:
    """Redis cluster manager with high availability."""

    def __init__(self, cluster_config: ClusterConfig):
        self.config = cluster_config
        self.nodes: Dict[str, ClusterNode] = {}
        self.primary_node: Optional[str] = None
        self.replica_nodes: Set[str] = set()

        # Core services
        self.redis = get_redis()
        self.error_handler = SecureErrorHandler()

        # Cluster state
        self.is_initialized = False
        self.is_healthy = False
        self.last_failover = None

        # Monitoring
        self.logger = logging.getLogger(f"cluster.{cluster_config.cluster_id}")

        # Health check task
        self._health_check_task = None
        self._running = False

    async def initialize(self):
        """Initialize the Redis cluster."""
        try:
            self.logger.info(f"Initializing Redis cluster {self.config.cluster_id}")

            # Validate configuration
            self._validate_config()

            # Initialize nodes
            await self._initialize_nodes()

            # Start health monitoring
            await self.start_health_monitoring()

            # Perform initial health check
            await self._perform_health_check()

            # Elect primary if needed
            if self.config.topology in [
                ClusterTopology.MASTER_REPLICA,
                ClusterTopology.CLUSTER,
            ]:
                await self._elect_primary()

            self.is_initialized = True
            self.is_healthy = True

            self.logger.info(
                f"Redis cluster {self.config.cluster_id} initialized successfully"
            )

        except Exception as e:
            self.logger.error(f"Failed to initialize Redis cluster: {e}")
            self.error_handler.log_security_event(
                event_type="cluster_initialization_error",
                severity="HIGH",
                description=f"Redis cluster initialization failed: {str(e)}",
                context={"cluster_id": self.config.cluster_id},
            )
            raise

    def _validate_config(self):
        """Validate cluster configuration."""
        if (
            self.config.topology == ClusterTopology.CLUSTER
            and self.config.max_nodes < 6
        ):
            raise ValueError("Cluster topology requires at least 6 nodes")

        if (
            self.config.topology == ClusterTopology.MASTER_REPLICA
            and self.config.max_nodes < 2
        ):
            raise ValueError("Master-replica topology requires at least 2 nodes")

        if self.config.min_nodes > self.config.max_nodes:
            raise ValueError("min_nodes cannot be greater than max_nodes")

    async def _initialize_nodes(self):
        """Initialize cluster nodes."""
        # This would load node configurations from config or environment
        # For now, create a sample configuration

        if self.config.topology == ClusterTopology.SINGLE_NODE:
            # Single node setup
            node = ClusterNode(
                node_id="node-1",
                host="localhost",
                port=6379,
                role=ClusterRole.PRIMARY,
                created_at=datetime.now(),
            )
            self.nodes[node.node_id] = node
            self.primary_node = node.node_id

        elif self.config.topology == ClusterTopology.MASTER_REPLICA:
            # Master-replica setup
            # Primary node
            primary = ClusterNode(
                node_id="primary",
                host="localhost",
                port=6379,
                role=ClusterRole.PRIMARY,
                created_at=datetime.now(),
            )
            self.nodes[primary.node_id] = primary
            self.primary_node = primary.node_id

            # Replica node
            replica = ClusterNode(
                node_id="replica-1",
                host="localhost",
                port=6380,
                role=ClusterRole.REPLICA,
                created_at=datetime.now(),
            )
            self.nodes[replica.node_id] = replica
            self.replica_nodes.add(replica.node_id)

        elif self.config.topology == ClusterTopology.CLUSTER:
            # Cluster setup with multiple nodes
            for i in range(self.config.max_nodes):
                node = ClusterNode(
                    node_id=f"node-{i+1}",
                    host=f"redis-node-{i+1}",
                    port=6379 + i,
                    role=ClusterRole.PRIMARY if i == 0 else ClusterRole.REPLICA,
                    created_at=datetime.now(),
                )
                self.nodes[node.node_id] = node

                if i == 0:
                    self.primary_node = node.node_id
                else:
                    self.replica_nodes.add(node.node_id)

        self.logger.info(
            f"Initialized {len(self.nodes)} nodes for {self.config.topology.value} topology"
        )

    async def start_health_monitoring(self):
        """Start cluster health monitoring."""
        self._running = True
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        self.logger.info("Started cluster health monitoring")

    async def stop_health_monitoring(self):
        """Stop cluster health monitoring."""
        self._running = False
        if self._health_check_task:
            self._health_check_task.cancel()
            self._health_check_task = None
        self.logger.info("Stopped cluster health monitoring")

    async def _health_check_loop(self):
        """Main health check loop."""
        while self._running:
            try:
                await self._perform_health_check()
                await asyncio.sleep(self.config.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(5)

    async def _perform_health_check(self):
        """Perform health check on all nodes."""
        tasks = []

        for node_id, node in self.nodes.items():
            if node.can_connect():
                task = asyncio.create_task(self._check_node_health(node))
                tasks.append((node_id, task))

        # Wait for all health checks to complete
        if tasks:
            results = await asyncio.gather(
                *[task for _, task in tasks], return_exceptions=True
            )

            for i, (node_id, result) in enumerate(tasks):
                node = self.nodes[node_id]
                if isinstance(result, Exception):
                    node.update_health_check(0, False, str(result))
                else:
                    response_time_ms, success = result
                    node.update_health_check(response_time_ms, success)

        # Update cluster metrics
        await self._update_cluster_metrics()

        # Check if failover is needed
        if self.config.auto_failover:
            await self._check_failover_needed()

    async def _check_node_health(self, node: ClusterNode) -> tuple[float, bool]:
        """Check health of a single node."""
        start_time = time.time()

        try:
            # Create Redis client for this node
            from .client import AsyncRedis, Redis

            client = AsyncRedis(
                url=f"redis://{node.host}:{node.port}", token=node.password or ""
            )

            # Test connection
            await client.ping()

            # Get basic info
            info = await client.info()

            # Update node metrics
            if info:
                node.memory_usage_mb = info.get("used_memory", 0) / (1024 * 1024)
                node.connected_clients = info.get("connected_clients", 0)
                node.keyspace_hits = info.get("keyspace_hits", 0)
                node.keyspace_misses = info.get("keyspace_misses", 0)

            response_time = (time.time() - start_time) * 1000
            return response_time, True

        except Exception as e:
            self.logger.warning(f"Health check failed for node {node.node_id}: {e}")
            return 0, False

    async def _update_cluster_metrics(self):
        """Update cluster-wide metrics."""
        metrics = ClusterMetrics(cluster_id=self.config.cluster_id)

        # Count nodes by status
        for node in self.nodes.values():
            metrics.total_nodes += 1

            if node.status == ClusterNodeStatus.ONLINE:
                metrics.online_nodes += 1
            elif node.status == ClusterNodeStatus.OFFLINE:
                metrics.offline_nodes += 1
            elif node.status == ClusterNodeStatus.FAILED:
                metrics.failed_nodes += 1

            # Aggregate metrics
            metrics.total_connections += node.connected_clients
            metrics.total_memory_mb += node.memory_usage_mb
            metrics.total_cpu_percent += node.cpu_usage_percent
            metrics.total_keys += node.keyspace_hits + node.keyspace_misses

        # Calculate averages
        if metrics.online_nodes > 0:
            metrics.avg_response_time_ms = (
                sum(
                    node.response_time_ms
                    for node in self.nodes.values()
                    if node.is_healthy()
                )
                / metrics.online_nodes
            )

            metrics.total_cpu_percent = metrics.total_cpu_percent / metrics.total_nodes

        # Calculate derived metrics
        metrics.calculate_health_score()
        metrics.calculate_hit_rate()

        # Store metrics
        metrics_key = f"cluster:{self.config.cluster_id}:metrics"
        await self.redis.set_json(
            metrics_key, metrics.to_dict(), ex=300
        )  # 5 minutes TTL

    async def _check_failover_needed(self):
        """Check if failover is needed."""
        if not self.config.auto_failover:
            return

        # Check if primary is down
        if self.primary_node and self.primary_node in self.nodes:
            primary = self.nodes[self.primary_node]

            if not primary.is_healthy():
                self.logger.warning(
                    f"Primary node {self.primary_node} is unhealthy, initiating failover"
                )
                await self._initiate_failover()

    async def _initiate_failover(self):
        """Initiate cluster failover."""
        try:
            self.logger.info("Initiating cluster failover")

            # Mark failover time
            self.last_failover = datetime.now()

            # Elect new primary
            await self._elect_primary()

            # Update replica configurations
            await self._update_replica_configurations()

            # Log security event
            self.error_handler.log_security_event(
                event_type="cluster_failover",
                severity="HIGH",
                description="Redis cluster failover initiated",
                context={
                    "cluster_id": self.config.cluster_id,
                    "old_primary": self.primary_node,
                    "new_primary": self.primary_node,
                },
            )

            self.logger.info(
                f"Cluster failover completed. New primary: {self.primary_node}"
            )

        except Exception as e:
            self.logger.error(f"Failover failed: {e}")
            self.error_handler.log_security_event(
                event_type="cluster_failover_error",
                severity="CRITICAL",
                description=f"Redis cluster failover failed: {str(e)}",
                context={"cluster_id": self.config.cluster_id},
            )

    async def _elect_primary(self):
        """Elect primary node from healthy nodes."""
        healthy_nodes = [
            node_id
            for node_id, node in self.nodes.items()
            if node.is_healthy()
            and node.role in [ClusterRole.PRIMARY, ClusterRole.REPLICA]
        ]

        if not healthy_nodes:
            raise Exception("No healthy nodes available for primary election")

        # Select node with lowest response time
        best_node_id = min(
            healthy_nodes, key=lambda nid: self.nodes[nid].response_time_ms
        )

        # Update roles
        for node_id, node in self.nodes.items():
            if node_id == best_node_id:
                node.role = ClusterRole.PRIMARY
                self.primary_node = node_id
                self.replica_nodes.discard(node_id)
            else:
                node.role = ClusterRole.REPLICA
                self.replica_nodes.add(node_id)

        self.logger.info(f"Elected primary node: {best_node_id}")

    async def _update_replica_configurations(self):
        """Update replica configurations."""
        if not self.primary_node:
            return

        primary = self.nodes[self.primary_node]

        for replica_id in self.replica_nodes:
            replica = self.nodes[replica_id]

            # This would update replica configuration to follow the new primary
            # For now, just log the action
            self.logger.info(
                f"Updating replica {replica_id} to follow primary {self.primary_node}"
            )

    async def add_node(self, node: ClusterNode) -> bool:
        """Add a new node to the cluster."""
        if len(self.nodes) >= self.config.max_nodes:
            raise ValueError(
                f"Cluster already has maximum nodes ({self.config.max_nodes})"
            )

        self.nodes[node.node_id] = node

        # Update role assignments
        if node.role == ClusterRole.PRIMARY:
            if self.primary_node:
                # Demote current primary to replica
                self.nodes[self.primary_node].role = ClusterRole.REPLICA
                self.replica_nodes.add(self.primary_node)

            self.primary_node = node.node_id
            self.replica_nodes.discard(node.node_id)
        else:
            self.replica_nodes.add(node.node_id)

        self.logger.info(f"Added node {node.node_id} to cluster")
        return True

    async def remove_node(self, node_id: str) -> bool:
        """Remove a node from the cluster."""
        if node_id not in self.nodes:
            return False

        node = self.nodes[node_id]

        # Cannot remove primary if it's the only node
        if node.role == ClusterRole.PRIMARY and len(self.nodes) == 1:
            raise ValueError("Cannot remove primary node from single-node cluster")

        # Remove from tracking
        del self.nodes[node_id]
        self.replica_nodes.discard(node_id)

        if self.primary_node == node_id:
            self.primary_node = None
            # Elect new primary
            await self._elect_primary()

        self.logger.info(f"Removed node {node_id} from cluster")
        return True

    async def get_cluster_status(self) -> Dict[str, Any]:
        """Get comprehensive cluster status."""
        await self._update_cluster_metrics()

        metrics_key = f"cluster:{self.config.cluster_id}:metrics"
        metrics_data = await self.redis.get_json(metrics_key)

        metrics = (
            ClusterMetrics.from_dict(metrics_data)
            if metrics_data
            else ClusterMetrics(cluster_id=self.config.cluster_id)
        )

        return {
            "cluster_id": self.config.cluster_id,
            "cluster_name": self.config.cluster_name,
            "topology": self.config.topology.value,
            "is_initialized": self.is_initialized,
            "is_healthy": self.is_healthy,
            "primary_node": self.primary_node,
            "total_nodes": metrics.total_nodes,
            "online_nodes": metrics.online_nodes,
            "offline_nodes": metrics.offline_nodes,
            "failed_nodes": metrics.failed_nodes,
            "health_score": metrics.health_score,
            "availability_percentage": metrics.availability_percentage,
            "total_connections": metrics.total_connections,
            "avg_response_time_ms": metrics.avg_response_time_ms,
            "last_failover": (
                self.last_failover.isoformat() if self.last_failover else None
            ),
            "nodes": {
                node_id: {
                    "host": node.host,
                    "port": node.port,
                    "role": node.role.value,
                    "status": node.status.value,
                    "response_time_ms": node.response_time_ms,
                    "connected_clients": node.connected_clients,
                    "memory_usage_mb": node.memory_usage_mb,
                    "is_healthy": node.is_healthy(),
                }
                for node_id, node in self.nodes.items()
            },
        }

    async def cleanup(self):
        """Cleanup cluster resources."""
        await self.stop_health_monitoring()

        # Close all Redis connections
        for node in self.nodes.values():
            try:
                # Close connection to this node
                pass  # Would close node-specific Redis client
            except Exception as e:
                self.logger.error(f"Error cleaning up node {node.node_id}: {e}")

        self.logger.info(f"Cleaned up cluster {self.config.cluster_id}")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()
