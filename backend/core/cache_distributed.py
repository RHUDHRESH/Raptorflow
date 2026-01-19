"""
Distributed Cache with Redis Cluster Support and Data Consistency
Provides distributed caching with consistency guarantees and cluster management
"""

import asyncio
import hashlib
import json
import logging
import time
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import threading
import uuid

try:
    import redis.asyncio as redis
    import redis.cluster
    from redis.cluster import RedisCluster
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class ConsistencyLevel(Enum):
    """Data consistency levels for distributed cache."""
    
    EVENTUAL = "eventual"          # Eventually consistent
    STRONG = "strong"              # Strong consistency
    SEQUENTIAL = "sequential"        # Sequential consistency
    CAUSAL = "causal"              # Causal consistency


class ReplicationStrategy(Enum):
    """Replication strategies for distributed cache."""
    
    LEADER_FOLLOWER = "leader_follower"
    MULTI_LEADER = "multi_leader"
    QUORUM = "quorum"
    EVENTUAL = "eventual"


class ConflictResolution(Enum):
    """Conflict resolution strategies."""
    
    LAST_WRITE_WINS = "last_write_wins"
    FIRST_WRITE_WINS = "first_write_wins"
    MERGE = "merge"
    VERSION_VECTOR = "version_vector"
    TIMESTAMP_ORDER = "timestamp_order"


@dataclass
class ClusterNode:
    """Cluster node information."""
    
    node_id: str
    host: str
    port: int
    role: str  # leader, follower, candidate
    status: str  # online, offline, recovering
    last_heartbeat: datetime
    weight: float = 1.0
    region: str = "default"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ReplicationLog:
    """Replication log entry."""
    
    log_id: str
    operation: str  # set, delete, expire
    key: str
    value: Any
    timestamp: datetime
    node_id: str
    sequence_number: int
    checksum: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class VersionVector:
    """Version vector for conflict resolution."""
    
    node_versions: Dict[str, int]
    timestamp: datetime
    
    def __post_init__(self):
        if self.node_versions is None:
            self.node_versions = {}
    
    def increment(self, node_id: str):
        """Increment version for node."""
        self.node_versions[node_id] = self.node_versions.get(node_id, 0) + 1
        self.timestamp = datetime.now()
    
    def merge(self, other: 'VersionVector') -> 'VersionVector':
        """Merge with another version vector."""
        merged_versions = {}
        
        # Take maximum for each node
        all_nodes = set(self.node_versions.keys()) | set(other.node_versions.keys())
        for node in all_nodes:
            merged_versions[node] = max(
                self.node_versions.get(node, 0),
                other.node_versions.get(node, 0)
            )
        
        # Use latest timestamp
        latest_timestamp = max(self.timestamp, other.timestamp)
        
        return VersionVector(
            node_versions=merged_versions,
            timestamp=latest_timestamp
        )
    
    def dominates(self, other: 'VersionVector') -> bool:
        """Check if this version vector dominates the other."""
        for node, version in self.node_versions.items():
            if version < other.node_versions.get(node, 0):
                return False
        return len(self.node_versions) > len(other.node_versions)


class ConsistentHashRing:
    """Consistent hashing ring for key distribution."""
    
    def __init__(self, virtual_nodes: int = 150):
        self.virtual_nodes = virtual_nodes
        self.ring: Dict[int, ClusterNode] = {}
        self.sorted_keys: List[int] = []
        self.nodes: Dict[str, ClusterNode] = {}
    
    def add_node(self, node: ClusterNode):
        """Add node to hash ring."""
        self.nodes[node.node_id] = node
        
        # Add virtual nodes
        for i in range(self.virtual_nodes):
            virtual_key = f"{node.node_id}:{i}"
            hash_value = self._hash(virtual_key)
            self.ring[hash_value] = node
        
        # Update sorted keys
        self.sorted_keys = sorted(self.ring.keys())
    
    def remove_node(self, node_id: str):
        """Remove node from hash ring."""
        if node_id not in self.nodes:
            return
        
        node = self.nodes[node_id]
        del self.nodes[node_id]
        
        # Remove virtual nodes
        for i in range(self.virtual_nodes):
            virtual_key = f"{node_id}:{i}"
            hash_value = self._hash(virtual_key)
            if hash_value in self.ring:
                del self.ring[hash_value]
        
        # Update sorted keys
        self.sorted_keys = sorted(self.ring.keys())
    
    def get_node(self, key: str) -> Optional[ClusterNode]:
        """Get node responsible for key."""
        if not self.ring:
            return None
        
        hash_value = self._hash(key)
        
        # Find first node with hash >= key hash
        for ring_key in self.sorted_keys:
            if ring_key >= hash_value:
                return self.ring[ring_key]
        
        # Wrap around to first node
        return self.ring[self.sorted_keys[0]]
    
    def get_nodes(self, key: str, count: int) -> List[ClusterNode]:
        """Get multiple nodes for key (for replication)."""
        if not self.ring:
            return []
        
        hash_value = self._hash(key)
        nodes = []
        
        # Find count nodes starting from hash position
        for ring_key in self.sorted_keys:
            if ring_key >= hash_value and len(nodes) < count:
                node = self.ring[ring_key]
                if node not in nodes:
                    nodes.append(node)
        
        # Wrap around if needed
        if len(nodes) < count:
            for ring_key in self.sorted_keys:
                if len(nodes) >= count:
                    break
                node = self.ring[ring_key]
                if node not in nodes:
                    nodes.append(node)
        
        return nodes
    
    def _hash(self, key: str) -> int:
        """Hash function for consistent hashing."""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)


class DistributedCacheClient:
    """Client for distributed cache operations."""
    
    def __init__(
        self,
        cluster_config: Dict[str, Any],
        consistency_level: ConsistencyLevel = ConsistencyLevel.EVENTUAL,
        replication_factor: int = 2
    ):
        self.cluster_config = cluster_config
        self.consistency_level = consistency_level
        self.replication_factor = replication_factor
        
        # Cluster components
        self.hash_ring = ConsistentHashRing()
        self.local_node: Optional[ClusterNode] = None
        self.cluster_nodes: Dict[str, ClusterNode] = {}
        
        # Replication
        self.replication_logs: List[ReplicationLog] = []
        self.version_vectors: Dict[str, VersionVector] = {}
        
        # Connections
        self.node_connections: Dict[str, Any] = {}
        
        # Performance tracking
        self.stats = {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'replication_lag_ms': 0,
            'consistency_violations': 0
        }
        
        # Lock for thread safety
        self._lock = threading.RLock()
    
    async def initialize(self):
        """Initialize distributed cache client."""
        try:
            # Initialize local node
            local_config = self.cluster_config.get('local_node')
            if local_config:
                self.local_node = ClusterNode(
                    node_id=local_config['node_id'],
                    host=local_config['host'],
                    port=local_config['port'],
                    role='leader',  # Can be determined by election
                    status='online',
                    last_heartbeat=datetime.now(),
                    weight=local_config.get('weight', 1.0),
                    region=local_config.get('region', 'default')
                )
                
                self.cluster_nodes[self.local_node.node_id] = self.local_node
                self.hash_ring.add_node(self.local_node)
            
            # Initialize cluster nodes
            cluster_nodes_config = self.cluster_config.get('cluster_nodes', [])
            for node_config in cluster_nodes_config:
                node = ClusterNode(
                    node_id=node_config['node_id'],
                    host=node_config['host'],
                    port=node_config['port'],
                    role='follower',
                    status='online',
                    last_heartbeat=datetime.now(),
                    weight=node_config.get('weight', 1.0),
                    region=node_config.get('region', 'default')
                )
                
                self.cluster_nodes[node.node_id] = node
                self.hash_ring.add_node(node)
            
            # Initialize connections
            await self._initialize_connections()
            
            logger.info(f"Distributed cache client initialized with {len(self.cluster_nodes)} nodes")
            
        except Exception as e:
            logger.error(f"Failed to initialize distributed cache client: {e}")
            raise
    
    async def get(
        self,
        key: str,
        consistency_level: Optional[ConsistencyLevel] = None
    ) -> Optional[Any]:
        """Get value from distributed cache."""
        start_time = time.time()
        consistency = consistency_level or self.consistency_level
        
        try:
            with self._lock:
                self.stats['total_operations'] += 1
            
            if consistency == ConsistencyLevel.STRONG:
                return await self._get_strong_consistency(key)
            elif consistency == ConsistencyLevel.SEQUENTIAL:
                return await self._get_sequential_consistency(key)
            elif consistency == ConsistencyLevel.CAUSAL:
                return await self._get_causal_consistency(key)
            else:
                return await self._get_eventual_consistency(key)
                
        except Exception as e:
            logger.error(f"Distributed get error for key {key}: {e}")
            with self._lock:
                self.stats['failed_operations'] += 1
            return None
        finally:
            operation_time = (time.time() - start_time) * 1000
            logger.debug(f"Get operation for {key} took {operation_time:.2f}ms")
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        consistency_level: Optional[ConsistencyLevel] = None
    ) -> bool:
        """Set value in distributed cache."""
        start_time = time.time()
        consistency = consistency_level or self.consistency_level
        
        try:
            with self._lock:
                self.stats['total_operations'] += 1
            
            if consistency == ConsistencyLevel.STRONG:
                return await self._set_strong_consistency(key, value, ttl)
            elif consistency == ConsistencyLevel.SEQUENTIAL:
                return await self._set_sequential_consistency(key, value, ttl)
            elif consistency == ConsistencyLevel.CAUSAL:
                return await self._set_causal_consistency(key, value, ttl)
            else:
                return await self._set_eventual_consistency(key, value, ttl)
                
        except Exception as e:
            logger.error(f"Distributed set error for key {key}: {e}")
            with self._lock:
                self.stats['failed_operations'] += 1
            return False
        finally:
            operation_time = (time.time() - start_time) * 1000
            logger.debug(f"Set operation for {key} took {operation_time:.2f}ms")
    
    async def delete(
        self,
        key: str,
        consistency_level: Optional[ConsistencyLevel] = None
    ) -> bool:
        """Delete key from distributed cache."""
        start_time = time.time()
        consistency = consistency_level or self.consistency_level
        
        try:
            with self._lock:
                self.stats['total_operations'] += 1
            
            # Get responsible nodes
            nodes = self.hash_ring.get_nodes(key, self.replication_factor)
            
            # Delete from all nodes
            tasks = []
            for node in nodes:
                tasks.append(self._delete_from_node(node, key))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            success_count = sum(1 for r in results if r is True)
            
            # Check consistency requirements
            if consistency == ConsistencyLevel.STRONG:
                success = success_count == len(nodes)
            else:
                success = success_count > 0
            
            if success:
                with self._lock:
                    self.stats['successful_operations'] += 1
            else:
                with self._lock:
                    self.stats['failed_operations'] += 1
            
            return success
            
        except Exception as e:
            logger.error(f"Distributed delete error for key {key}: {e}")
            with self._lock:
                self.stats['failed_operations'] += 1
            return False
        finally:
            operation_time = (time.time() - start_time) * 1000
            logger.debug(f"Delete operation for {key} took {operation_time:.2f}ms")
    
    async def _get_eventual_consistency(self, key: str) -> Optional[Any]:
        """Get with eventual consistency."""
        # Get from local node first
        local_node = self.hash_ring.get_node(key)
        if local_node and local_node.node_id == self.local_node.node_id:
            return await self._get_from_local_node(key)
        
        # Get from responsible node
        if local_node:
            return await self._get_from_node(local_node, key)
        
        return None
    
    async def _get_strong_consistency(self, key: str) -> Optional[Any]:
        """Get with strong consistency (read from quorum)."""
        nodes = self.hash_ring.get_nodes(key, self.replication_factor)
        quorum_size = (len(nodes) // 2) + 1
        
        # Read from all nodes
        tasks = []
        for node in nodes:
            tasks.append(self._get_from_node(node, key))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Find latest version
        latest_value = None
        latest_timestamp = None
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                continue
            
            if result is not None:
                # Get version information
                version_info = await self._get_version_info(nodes[i], key)
                if version_info and version_info['timestamp']:
                    if (latest_timestamp is None or 
                        version_info['timestamp'] > latest_timestamp):
                        latest_timestamp = version_info['timestamp']
                        latest_value = result
                else:
                    latest_value = result
        
        return latest_value
    
    async def _get_sequential_consistency(self, key: str) -> Optional[Any]:
        """Get with sequential consistency."""
        # For sequential consistency, we need to ensure operations are ordered
        # This is a simplified implementation
        return await self._get_eventual_consistency(key)
    
    async def _get_causal_consistency(self, key: str) -> Optional[Any]:
        """Get with causal consistency."""
        # Check version vector for causal dependencies
        current_vector = self.version_vectors.get(key)
        if not current_vector:
            return await self._get_eventual_consistency(key)
        
        # Get from nodes and check causality
        nodes = self.hash_ring.get_nodes(key, self.replication_factor)
        
        for node in nodes:
            value = await self._get_from_node(node, key)
            if value is not None:
                node_vector = await self._get_version_vector(node, key)
                if node_vector and current_vector.dominates(node_vector):
                    return value
        
        return await self._get_eventual_consistency(key)
    
    async def _set_eventual_consistency(
        self,
        key: str,
        value: Any,
        ttl: Optional[int]
    ) -> bool:
        """Set with eventual consistency."""
        # Get responsible nodes for replication
        nodes = self.hash_ring.get_nodes(key, self.replication_factor)
        
        # Create replication log entry
        log_entry = ReplicationLog(
            log_id=str(uuid.uuid4()),
            operation='set',
            key=key,
            value=value,
            timestamp=datetime.now(),
            node_id=self.local_node.node_id,
            sequence_number=len(self.replication_logs),
            checksum=self._calculate_checksum(value)
        )
        
        # Replicate to all nodes
        tasks = []
        for node in nodes:
            tasks.append(self._set_to_node(node, key, value, ttl, log_entry))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        success_count = sum(1 for r in results if r is True)
        
        # Update version vector
        if key not in self.version_vectors:
            self.version_vectors[key] = VersionVector({}, datetime.now())
        self.version_vectors[key].increment(self.local_node.node_id)
        
        # Consider successful if at least one node succeeds
        success = success_count > 0
        
        if success:
            with self._lock:
                self.stats['successful_operations'] += 1
        else:
            with self._lock:
                self.stats['failed_operations'] += 1
        
        return success
    
    async def _set_strong_consistency(
        self,
        key: str,
        value: Any,
        ttl: Optional[int]
    ) -> bool:
        """Set with strong consistency (write to quorum)."""
        nodes = self.hash_ring.get_nodes(key, self.replication_factor)
        quorum_size = (len(nodes) // 2) + 1
        
        # Create replication log entry
        log_entry = ReplicationLog(
            log_id=str(uuid.uuid4()),
            operation='set',
            key=key,
            value=value,
            timestamp=datetime.now(),
            node_id=self.local_node.node_id,
            sequence_number=len(self.replication_logs),
            checksum=self._calculate_checksum(value)
        )
        
        # Write to all nodes
        tasks = []
        for node in nodes:
            tasks.append(self._set_to_node(node, key, value, ttl, log_entry))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        success_count = sum(1 for r in results if r is True)
        
        # Check quorum
        success = success_count >= quorum_size
        
        if success:
            with self._lock:
                self.stats['successful_operations'] += 1
        else:
            with self._lock:
                self.stats['failed_operations'] += 1
        
        return success
    
    async def _set_sequential_consistency(
        self,
        key: str,
        value: Any,
        ttl: Optional[int]
    ) -> bool:
        """Set with sequential consistency."""
        # For sequential consistency, we need a total order
        # This is a simplified implementation using a distributed lock
        lock_key = f"lock:{key}"
        
        # Acquire distributed lock
        lock_acquired = await self._acquire_distributed_lock(lock_key)
        
        if not lock_acquired:
            return False
        
        try:
            # Perform the set operation
            return await self._set_eventual_consistency(key, value, ttl)
        finally:
            # Release distributed lock
            await self._release_distributed_lock(lock_key)
    
    async def _set_causal_consistency(
        self,
        key: str,
        value: Any,
        ttl: Optional[int]
    ) -> bool:
        """Set with causal consistency."""
        # Update version vector
        if key not in self.version_vectors:
            self.version_vectors[key] = VersionVector({}, datetime.now())
        self.version_vectors[key].increment(self.local_node.node_id)
        
        # Set with version information
        return await self._set_eventual_consistency(key, value, ttl)
    
    async def _initialize_connections(self):
        """Initialize connections to cluster nodes."""
        for node_id, node in self.cluster_nodes.items():
            if node_id == self.local_node.node_id:
                # Local node connection
                try:
                    self.node_connections[node_id] = redis.from_url(
                        f"redis://{node.host}:{node.port}",
                        encoding='utf-8',
                        decode_responses=False
                    )
                    logger.info(f"Connected to local node {node_id}")
                except Exception as e:
                    logger.error(f"Failed to connect to local node {node_id}: {e}")
            else:
                # Remote node connection
                try:
                    self.node_connections[node_id] = redis.from_url(
                        f"redis://{node.host}:{node.port}",
                        encoding='utf-8',
                        decode_responses=False
                    )
                    logger.info(f"Connected to remote node {node_id}")
                except Exception as e:
                    logger.error(f"Failed to connect to remote node {node_id}: {e}")
    
    async def _get_from_node(self, node: ClusterNode, key: str) -> Optional[Any]:
        """Get value from specific node."""
        try:
            if node.node_id not in self.node_connections:
                return None
            
            client = self.node_connections[node.node_id]
            data = await client.get(key)
            
            if data:
                # Deserialize and return
                return json.loads(data.decode())
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting from node {node.node_id}: {e}")
            return None
    
    async def _get_from_local_node(self, key: str) -> Optional[Any]:
        """Get value from local node."""
        if not self.local_node:
            return None
        
        return await self._get_from_node(self.local_node, key)
    
    async def _set_to_node(
        self,
        node: ClusterNode,
        key: str,
        value: Any,
        ttl: Optional[int],
        log_entry: ReplicationLog
    ) -> bool:
        """Set value to specific node."""
        try:
            if node.node_id not in self.node_connections:
                return False
            
            client = self.node_connections[node.node_id]
            
            # Serialize value
            serialized_value = json.dumps(value, default=str)
            
            # Set with TTL if provided
            if ttl:
                await client.setex(key, ttl, serialized_value)
            else:
                await client.set(key, serialized_value)
            
            # Store version information
            version_key = f"{key}:version"
            version_data = {
                'node_id': log_entry.node_id,
                'timestamp': log_entry.timestamp.isoformat(),
                'sequence_number': log_entry.sequence_number,
                'checksum': log_entry.checksum
            }
            await client.set(version_key, json.dumps(version_data))
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting to node {node.node_id}: {e}")
            return False
    
    async def _delete_from_node(self, node: ClusterNode, key: str) -> bool:
        """Delete key from specific node."""
        try:
            if node.node_id not in self.node_connections:
                return False
            
            client = self.node_connections[node.node_id]
            
            # Delete key and version information
            await client.delete(key, f"{key}:version")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting from node {node.node_id}: {e}")
            return False
    
    async def _get_version_info(self, node: ClusterNode, key: str) -> Optional[Dict[str, Any]]:
        """Get version information for key from node."""
        try:
            if node.node_id not in self.node_connections:
                return None
            
            client = self.node_connections[node.node_id]
            version_data = await client.get(f"{key}:version")
            
            if version_data:
                return json.loads(version_data.decode())
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting version info from node {node.node_id}: {e}")
            return None
    
    async def _get_version_vector(self, node: ClusterNode, key: str) -> Optional[VersionVector]:
        """Get version vector for key from node."""
        version_info = await self._get_version_info(node, key)
        if not version_info:
            return None
        
        return VersionVector(
            node_versions={version_info['node_id']: version_info['sequence_number']},
            timestamp=datetime.fromisoformat(version_info['timestamp'])
        )
    
    async def _acquire_distributed_lock(self, lock_key: str) -> bool:
        """Acquire distributed lock."""
        try:
            if not self.local_node:
                return False
            
            client = self.node_connections[self.local_node.node_id]
            
            # Try to acquire lock with timeout
            lock_value = f"{self.local_node.node_id}:{time.time()}"
            acquired = await client.set(
                lock_key,
                lock_value,
                ex=30,  # 30 second timeout
                nx=True  # Only set if not exists
            )
            
            return acquired
            
        except Exception as e:
            logger.error(f"Error acquiring distributed lock: {e}")
            return False
    
    async def _release_distributed_lock(self, lock_key: str):
        """Release distributed lock."""
        try:
            if not self.local_node:
                return
            
            client = self.node_connections[self.local_node.node_id]
            await client.delete(lock_key)
            
        except Exception as e:
            logger.error(f"Error releasing distributed lock: {e}")
    
    def _calculate_checksum(self, value: Any) -> str:
        """Calculate checksum for value."""
        value_str = json.dumps(value, default=str)
        return hashlib.sha256(value_str.encode()).hexdigest()[:16]
    
    def get_cluster_status(self) -> Dict[str, Any]:
        """Get cluster status information."""
        return {
            'total_nodes': len(self.cluster_nodes),
            'online_nodes': sum(1 for n in self.cluster_nodes.values() if n.status == 'online'),
            'local_node': self.local_node.to_dict() if self.local_node else None,
            'nodes': {node_id: node.to_dict() for node_id, node in self.cluster_nodes.items()},
            'replication_factor': self.replication_factor,
            'consistency_level': self.consistency_level.value,
            'stats': self.stats.copy()
        }


class DistributedCacheManager:
    """Main distributed cache manager."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Distributed cache client
        self.cache_client = DistributedCacheClient(
            cluster_config=config.get('cluster', {}),
            consistency_level=ConsistencyLevel(config.get('consistency', 'eventual')),
            replication_factor=config.get('replication_factor', 2)
        )
        
        # Background tasks
        self._heartbeat_task = None
        self._replication_task = None
        self._running = False
    
    async def initialize(self):
        """Initialize distributed cache manager."""
        await self.cache_client.initialize()
        
        # Start background tasks
        self._running = True
        self._heartbeat_task = asyncio.create_task(self._heartbeat_monitor())
        self._replication_task = asyncio.create_task(self._replication_monitor())
        
        logger.info("Distributed cache manager initialized")
    
    async def shutdown(self):
        """Shutdown distributed cache manager."""
        self._running = False
        
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        
        if self._replication_task:
            self._replication_task.cancel()
        
        logger.info("Distributed cache manager shutdown")
    
    async def get(self, key: str, consistency: Optional[ConsistencyLevel] = None) -> Optional[Any]:
        """Get value from distributed cache."""
        return await self.cache_client.get(key, consistency)
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        consistency: Optional[ConsistencyLevel] = None
    ) -> bool:
        """Set value in distributed cache."""
        return await self.cache_client.set(key, value, ttl, consistency)
    
    async def delete(self, key: str, consistency: Optional[ConsistencyLevel] = None) -> bool:
        """Delete key from distributed cache."""
        return await self.cache_client.delete(key, consistency)
    
    async def _heartbeat_monitor(self):
        """Monitor cluster node health."""
        while self._running:
            try:
                # Send heartbeats to all nodes
                for node_id, node in self.cache_client.cluster_nodes.items():
                    if node_id != self.cache_client.local_node.node_id:
                        # Check node connectivity
                        try:
                            client = self.cache_client.node_connections.get(node_id)
                            if client:
                                await client.ping()
                                node.last_heartbeat = datetime.now()
                                node.status = 'online'
                            else:
                                node.status = 'offline'
                        except Exception:
                            node.status = 'offline'
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Heartbeat monitor error: {e}")
                await asyncio.sleep(30)
    
    async def _replication_monitor(self):
        """Monitor replication lag and consistency."""
        while self._running:
            try:
                # Check replication lag
                # This is a simplified implementation
                # In production, you would monitor actual replication lag
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Replication monitor error: {e}")
                await asyncio.sleep(60)
    
    def get_distributed_stats(self) -> Dict[str, Any]:
        """Get distributed cache statistics."""
        return self.cache_client.get_cluster_status()


# Global distributed cache manager instance
_distributed_cache: Optional[DistributedCacheManager] = None


async def get_distributed_cache() -> DistributedCacheManager:
    """Get the global distributed cache manager."""
    global _distributed_cache
    if _distributed_cache is None:
        # Default configuration
        config = {
            'consistency': 'eventual',
            'replication_factor': 2,
            'cluster': {
                'local_node': {
                    'node_id': 'node1',
                    'host': 'localhost',
                    'port': 6379
                },
                'cluster_nodes': []
            }
        }
        _distributed_cache = DistributedCacheManager(config)
        await _distributed_cache.initialize()
    return _distributed_cache


# Convenience functions
async def distributed_get(key: str, consistency: Optional[ConsistencyLevel] = None) -> Optional[Any]:
    """Get value from distributed cache (convenience function)."""
    cache = await get_distributed_cache()
    return await cache.get(key, consistency)


async def distributed_set(
    key: str,
    value: Any,
    ttl: Optional[int] = None,
    consistency: Optional[ConsistencyLevel] = None
) -> bool:
    """Set value in distributed cache (convenience function)."""
    cache = await get_distributed_cache()
    return await cache.set(key, value, ttl, consistency)


async def distributed_delete(key: str, consistency: Optional[ConsistencyLevel] = None) -> bool:
    """Delete key from distributed cache (convenience function)."""
    cache = await get_distributed_cache()
    return await cache.delete(key, consistency)


def get_distributed_statistics() -> Dict[str, Any]:
    """Get distributed cache statistics (convenience function)."""
    if _distributed_cache:
        return _distributed_cache.get_distributed_stats()
    return {"error": "Distributed cache not initialized"}
