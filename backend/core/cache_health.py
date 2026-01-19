"""
Cache Health Monitor with Redis Cluster Monitoring and Automatic Failover
Provides comprehensive health monitoring and automatic recovery for cache systems
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import threading
import socket

try:
    import redis.asyncio as redis
    import redis.cluster
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels."""
    
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class FailoverType(Enum):
    """Types of failover."""
    
    ACTIVE_PASSIVE = "active_passive"
    ACTIVE_ACTIVE = "active_active"
    GEOGRAPHIC = "geographic"
    CLUSTER_NODE = "cluster_node"


class RecoveryAction(Enum):
    """Recovery actions."""
    
    RESTART_CONNECTION = "restart_connection"
    FAILOVER_TO_BACKUP = "failover_to_backup"
    SWITCH_CLUSTER_NODE = "switch_cluster_node"
    CLEAR_CACHE = "clear_cache"
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"


@dataclass
class HealthCheck:
    """Health check result."""
    
    component: str
    status: HealthStatus
    timestamp: datetime
    response_time: float
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class FailoverEvent:
    """Failover event record."""
    
    id: str
    timestamp: datetime
    from_component: str
    to_component: str
    reason: str
    recovery_time: float
    successful: bool
    metadata: Dict[str, Any]
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ClusterNode:
    """Redis cluster node information."""
    
    node_id: str
    host: str
    port: int
    role: str  # master, slave
    status: HealthStatus
    last_check: datetime
    response_time: float
    memory_usage: float
    cpu_usage: float
    connected_clients: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class RedisHealthChecker:
    """Health checker for Redis instances."""
    
    def __init__(self, connection_config: Dict[str, Any]):
        self.connection_config = connection_config
        self.client = None
        self.last_health_check = None
        
        # Health check thresholds
        self.thresholds = {
            'response_time_warning': 0.1,  # 100ms
            'response_time_critical': 0.5,  # 500ms
            'memory_usage_warning': 0.8,   # 80%
            'memory_usage_critical': 0.95,  # 95%
            'cpu_usage_warning': 0.8,       # 80%
            'cpu_usage_critical': 0.95,     # 95%
            'connection_timeout': 5.0         # 5 seconds
        }
    
    async def initialize(self):
        """Initialize Redis connection."""
        try:
            if self.connection_config.get('cluster_mode', False):
                # Cluster mode
                self.client = redis.cluster.RedisCluster(
                    startup_nodes=self.connection_config.get('nodes', []),
                    decode_responses=False,
                    skip_full_coverage_check=True
                )
            else:
                # Single instance mode
                self.client = redis.from_url(
                    self.connection_config.get('url'),
                    encoding='utf-8',
                    decode_responses=False,
                    socket_connect_timeout=self.thresholds['connection_timeout'],
                    socket_timeout=self.thresholds['connection_timeout']
                )
            
            # Test connection
            await self.client.ping()
            logger.info("Redis health checker initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis health checker: {e}")
            raise
    
    async def check_health(self) -> HealthCheck:
        """Perform comprehensive health check."""
        start_time = time.time()
        
        try:
            if not self.client:
                return HealthCheck(
                    component="redis",
                    status=HealthStatus.CRITICAL,
                    timestamp=datetime.now(),
                    response_time=0,
                    error_message="Redis client not initialized"
                )
            
            # Basic connectivity test
            ping_start = time.time()
            await self.client.ping()
            ping_time = time.time() - ping_start
            
            # Get server info
            info = await self.client.info()
            
            # Extract metrics
            memory_usage = self._calculate_memory_usage(info)
            cpu_usage = self._calculate_cpu_usage(info)
            connected_clients = info.get('connected_clients', 0)
            
            # Determine overall status
            status = self._determine_status(ping_time, memory_usage, cpu_usage)
            
            # Create health check
            health_check = HealthCheck(
                component="redis",
                status=status,
                timestamp=datetime.now(),
                response_time=ping_time,
                metadata={
                    'memory_usage': memory_usage,
                    'cpu_usage': cpu_usage,
                    'connected_clients': connected_clients,
                    'redis_version': info.get('redis_version'),
                    'uptime_seconds': info.get('uptime_in_seconds'),
                    'used_memory': info.get('used_memory'),
                    'max_memory': info.get('maxmemory')
                }
            )
            
            self.last_health_check = health_check
            return health_check
            
        except Exception as e:
            return HealthCheck(
                component="redis",
                status=HealthStatus.CRITICAL,
                timestamp=datetime.now(),
                response_time=time.time() - start_time,
                error_message=str(e)
            )
    
    def _calculate_memory_usage(self, info: Dict[str, Any]) -> float:
        """Calculate memory usage percentage."""
        used_memory = info.get('used_memory', 0)
        max_memory = info.get('max_memory', 0)
        
        if max_memory == 0:
            # If max_memory is not set, estimate based on system memory
            return 0.5  # Assume 50% usage as default
        
        return used_memory / max_memory
    
    def _calculate_cpu_usage(self, info: Dict[str, Any]) -> float:
        """Calculate CPU usage (simplified)."""
        # Redis doesn't provide direct CPU usage
        # This is a simplified estimation based on operations per second
        instantaneous_ops_per_sec = info.get('instantaneous_ops_per_sec', 0)
        
        # Rough estimation (would need more sophisticated monitoring in production)
        return min(instantaneous_ops_per_sec / 10000, 1.0)
    
    def _determine_status(
        self,
        response_time: float,
        memory_usage: float,
        cpu_usage: float
    ) -> HealthStatus:
        """Determine overall health status."""
        # Check for critical issues
        if (response_time > self.thresholds['response_time_critical'] or
            memory_usage > self.thresholds['memory_usage_critical'] or
            cpu_usage > self.thresholds['cpu_usage_critical']):
            return HealthStatus.CRITICAL
        
        # Check for warning issues
        if (response_time > self.thresholds['response_time_warning'] or
            memory_usage > self.thresholds['memory_usage_warning'] or
            cpu_usage > self.thresholds['cpu_usage_warning']):
            return HealthStatus.DEGRADED
        
        return HealthStatus.HEALTHY


class ClusterMonitor:
    """Monitors Redis cluster health."""
    
    def __init__(self, cluster_config: Dict[str, Any]):
        self.cluster_config = cluster_config
        self.nodes: Dict[str, ClusterNode] = {}
        self.master_nodes: Set[str] = set()
        self.replica_nodes: Set[str] = set()
        
        # Cluster health thresholds
        self.thresholds = {
            'minimum_healthy_nodes': 2,
            'master_failover_threshold': 1,
            'replica_lag_threshold': 10  # seconds
        }
    
    async def initialize(self):
        """Initialize cluster monitoring."""
        try:
            # Connect to cluster
            client = redis.cluster.RedisCluster(
                startup_nodes=self.cluster_config.get('nodes', []),
                decode_responses=False
            )
            
            # Get cluster info
            cluster_info = await client.cluster_info()
            nodes_info = await client.cluster_nodes()
            
            # Parse node information
            for node_info in nodes_info:
                node_id = node_info.get('id', '')
                host = node_info.get('host', '')
                port = int(node_info.get('port', 6379))
                role = node_info.get('flags', '').lower()
                
                if 'master' in role:
                    self.master_nodes.add(node_id)
                elif 'slave' in role:
                    self.replica_nodes.add(node_id)
                
                # Create node object
                node = ClusterNode(
                    node_id=node_id,
                    host=host,
                    port=port,
                    role='master' if 'master' in role else 'replica',
                    status=HealthStatus.UNKNOWN,
                    last_check=datetime.now(),
                    response_time=0,
                    memory_usage=0,
                    cpu_usage=0,
                    connected_clients=0
                )
                
                self.nodes[node_id] = node
            
            logger.info(f"Cluster monitor initialized with {len(self.nodes)} nodes")
            
        except Exception as e:
            logger.error(f"Failed to initialize cluster monitor: {e}")
            raise
    
    async def check_cluster_health(self) -> List[HealthCheck]:
        """Check health of all cluster nodes."""
        health_checks = []
        
        for node_id, node in self.nodes.items():
            try:
                # Create connection to specific node
                client = redis.from_url(
                    f"redis://{node.host}:{node.port}",
                    socket_connect_timeout=5.0,
                    socket_timeout=5.0
                )
                
                # Perform health check
                start_time = time.time()
                await client.ping()
                response_time = time.time() - start_time
                
                # Get node info
                info = await client.info()
                
                # Update node metrics
                node.response_time = response_time
                node.memory_usage = self._calculate_memory_usage(info)
                node.cpu_usage = self._calculate_cpu_usage(info)
                node.connected_clients = info.get('connected_clients', 0)
                node.last_check = datetime.now()
                
                # Determine status
                status = self._determine_node_status(node)
                node.status = status
                
                # Create health check
                health_check = HealthCheck(
                    component=f"cluster_node_{node_id}",
                    status=status,
                    timestamp=datetime.now(),
                    response_time=response_time,
                    metadata={
                        'node_id': node_id,
                        'host': node.host,
                        'port': node.port,
                        'role': node.role,
                        'memory_usage': node.memory_usage,
                        'cpu_usage': node.cpu_usage,
                        'connected_clients': node.connected_clients
                    }
                )
                
                health_checks.append(health_check)
                
            except Exception as e:
                node.status = HealthStatus.CRITICAL
                
                health_check = HealthCheck(
                    component=f"cluster_node_{node_id}",
                    status=HealthStatus.CRITICAL,
                    timestamp=datetime.now(),
                    response_time=0,
                    error_message=str(e),
                    metadata={
                        'node_id': node_id,
                        'host': node.host,
                        'port': node.port,
                        'role': node.role
                    }
                )
                
                health_checks.append(health_check)
        
        return health_checks
    
    def _calculate_memory_usage(self, info: Dict[str, Any]) -> float:
        """Calculate memory usage percentage."""
        used_memory = info.get('used_memory', 0)
        max_memory = info.get('max_memory', 0)
        
        if max_memory == 0:
            return 0.5
        
        return used_memory / max_memory
    
    def _calculate_cpu_usage(self, info: Dict[str, Any]) -> float:
        """Calculate CPU usage (simplified)."""
        instantaneous_ops = info.get('instantaneous_ops_per_sec', 0)
        return min(instantaneous_ops / 10000, 1.0)
    
    def _determine_node_status(self, node: ClusterNode) -> HealthStatus:
        """Determine node health status."""
        if (node.response_time > 0.5 or
            node.memory_usage > 0.95 or
            node.cpu_usage > 0.95):
            return HealthStatus.CRITICAL
        
        if (node.response_time > 0.1 or
            node.memory_usage > 0.8 or
            node.cpu_usage > 0.8):
            return HealthStatus.DEGRADED
        
        return HealthStatus.HEALTHY
    
    def get_cluster_status(self) -> Dict[str, Any]:
        """Get overall cluster status."""
        healthy_nodes = sum(1 for node in self.nodes.values() 
                          if node.status == HealthStatus.HEALTHY)
        degraded_nodes = sum(1 for node in self.nodes.values() 
                           if node.status == HealthStatus.DEGRADED)
        critical_nodes = sum(1 for node in self.nodes.values() 
                           if node.status == HealthStatus.CRITICAL)
        
        total_nodes = len(self.nodes)
        
        # Determine overall status
        if healthy_nodes >= self.thresholds['minimum_healthy_nodes']:
            overall_status = HealthStatus.HEALTHY
        elif healthy_nodes > 0:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.CRITICAL
        
        return {
            'overall_status': overall_status.value,
            'total_nodes': total_nodes,
            'healthy_nodes': healthy_nodes,
            'degraded_nodes': degraded_nodes,
            'critical_nodes': critical_nodes,
            'master_nodes': len(self.master_nodes),
            'replica_nodes': len(self.replica_nodes),
            'nodes': {node_id: node.to_dict() for node_id, node in self.nodes.items()}
        }


class FailoverManager:
    """Manages automatic failover operations."""
    
    def __init__(self, failover_config: Dict[str, Any]):
        self.failover_config = failover_config
        self.backup_connections: Dict[str, Any] = {}
        self.current_primary = None
        self.failover_history: deque = deque(maxlen=100)
        
        # Failover settings
        self.failover_timeout = failover_config.get('timeout', 30)
        self.max_failover_attempts = failover_config.get('max_attempts', 3)
        self.failover_cooldown = failover_config.get('cooldown', 300)  # 5 minutes
        
        # State tracking
        self.last_failover_time = None
        self.failover_in_progress = False
    
    async def initialize(self):
        """Initialize failover manager."""
        # Initialize backup connections
        backup_configs = self.failover_config.get('backups', [])
        
        for i, backup_config in enumerate(backup_configs):
            try:
                client = redis.from_url(
                    backup_config['url'],
                    encoding='utf-8',
                    decode_responses=False
                )
                
                # Test connection
                await client.ping()
                
                self.backup_connections[f"backup_{i}"] = {
                    'client': client,
                    'config': backup_config,
                    'last_check': datetime.now(),
                    'status': HealthStatus.HEALTHY
                }
                
                logger.info(f"Backup connection {i} initialized")
                
            except Exception as e:
                logger.error(f"Failed to initialize backup {i}: {e}")
                self.backup_connections[f"backup_{i}"] = {
                    'client': None,
                    'config': backup_config,
                    'last_check': datetime.now(),
                    'status': HealthStatus.CRITICAL,
                    'error': str(e)
                }
    
    async def perform_failover(
        self,
        from_component: str,
        reason: str,
        health_checks: List[HealthCheck]
    ) -> Optional[FailoverEvent]:
        """Perform automatic failover."""
        if self.failover_in_progress:
            logger.warning("Failover already in progress")
            return None
        
        # Check cooldown period
        if (self.last_failover_time and 
            (datetime.now() - self.last_failover_time).total_seconds() < self.failover_cooldown):
            logger.warning("Failover cooldown period active")
            return None
        
        self.failover_in_progress = True
        start_time = time.time()
        
        try:
            # Find healthy backup
            healthy_backup = None
            for backup_id, backup_info in self.backup_connections.items():
                if backup_info['status'] == HealthStatus.HEALTHY:
                    healthy_backup = backup_id
                    break
            
            if not healthy_backup:
                logger.error("No healthy backup available for failover")
                return None
            
            # Perform failover
            backup_client = self.backup_connections[healthy_backup]['client']
            
            # Test backup connection
            await backup_client.ping()
            
            # Update primary
            old_primary = self.current_primary
            self.current_primary = healthy_backup
            
            # Record failover event
            failover_event = FailoverEvent(
                id=f"failover_{int(time.time())}",
                timestamp=datetime.now(),
                from_component=from_component,
                to_component=healthy_backup,
                reason=reason,
                recovery_time=time.time() - start_time,
                successful=True,
                metadata={
                    'old_primary': old_primary,
                    'new_primary': healthy_backup,
                    'health_checks': [hc.to_dict() for hc in health_checks]
                }
            )
            
            self.failover_history.append(failover_event)
            self.last_failover_time = datetime.now()
            
            logger.info(f"Failover completed: {from_component} -> {healthy_backup}")
            
            return failover_event
            
        except Exception as e:
            logger.error(f"Failover failed: {e}")
            
            failover_event = FailoverEvent(
                id=f"failover_failed_{int(time.time())}",
                timestamp=datetime.now(),
                from_component=from_component,
                to_component="unknown",
                reason=reason,
                recovery_time=time.time() - start_time,
                successful=False,
                metadata={'error': str(e)}
            )
            
            self.failover_history.append(failover_event)
            return failover_event
            
        finally:
            self.failover_in_progress = False
    
    async def check_backup_health(self) -> List[HealthCheck]:
        """Check health of backup connections."""
        health_checks = []
        
        for backup_id, backup_info in self.backup_connections.items():
            start_time = time.time()
            
            try:
                if backup_info['client']:
                    await backup_info['client'].ping()
                    response_time = time.time() - start_time
                    
                    backup_info['status'] = HealthStatus.HEALTHY
                    backup_info['last_check'] = datetime.now()
                    
                    health_check = HealthCheck(
                        component=f"backup_{backup_id}",
                        status=HealthStatus.HEALTHY,
                        timestamp=datetime.now(),
                        response_time=response_time,
                        metadata={'backup_id': backup_id}
                    )
                else:
                    health_check = HealthCheck(
                        component=f"backup_{backup_id}",
                        status=HealthStatus.CRITICAL,
                        timestamp=datetime.now(),
                        response_time=0,
                        error_message="No client connection"
                    )
                
            except Exception as e:
                backup_info['status'] = HealthStatus.CRITICAL
                backup_info['last_check'] = datetime.now()
                backup_info['error'] = str(e)
                
                health_check = HealthCheck(
                    component=f"backup_{backup_id}",
                    status=HealthStatus.CRITICAL,
                    timestamp=datetime.now(),
                    response_time=time.time() - start_time,
                    error_message=str(e),
                    metadata={'backup_id': backup_id}
                )
            
            health_checks.append(health_check)
        
        return health_checks


class CacheHealthMonitor:
    """Main cache health monitoring system."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Components
        self.redis_checker = None
        self.cluster_monitor = None
        self.failover_manager = None
        
        # Health tracking
        self.health_history: deque = deque(maxlen=1000)
        self.active_alerts: Dict[str, HealthCheck] = {}
        
        # Monitoring settings
        self.check_interval = config.get('check_interval', 60)  # 1 minute
        self.alert_thresholds = config.get('alert_thresholds', {
            'consecutive_failures': 3,
            'response_time_p95': 0.2,
            'memory_usage': 0.9
        })
        
        # State tracking
        self.consecutive_failures = 0
        self.last_healthy_time = datetime.now()
        
        # Background task
        self._monitoring_task = None
        self._running = False
        
        # Event handlers
        self.health_event_handlers: List[callable] = []
    
    async def initialize(self):
        """Initialize health monitoring system."""
        try:
            # Initialize Redis checker
            if self.config.get('redis_config'):
                self.redis_checker = RedisHealthChecker(self.config['redis_config'])
                await self.redis_checker.initialize()
            
            # Initialize cluster monitor
            if self.config.get('cluster_config'):
                self.cluster_monitor = ClusterMonitor(self.config['cluster_config'])
                await self.cluster_monitor.initialize()
            
            # Initialize failover manager
            if self.config.get('failover_config'):
                self.failover_manager = FailoverManager(self.config['failover_config'])
                await self.failover_manager.initialize()
            
            # Start background monitoring
            self._running = True
            self._monitoring_task = asyncio.create_task(self._background_monitoring())
            
            logger.info("Cache health monitor initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize health monitor: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown health monitoring system."""
        self._running = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
        
        logger.info("Cache health monitor shutdown")
    
    def add_health_event_handler(self, handler: callable):
        """Add health event handler."""
        self.health_event_handlers.append(handler)
    
    async def check_system_health(self) -> Dict[str, Any]:
        """Perform comprehensive system health check."""
        health_checks = []
        
        # Check Redis health
        if self.redis_checker:
            redis_health = await self.redis_checker.check_health()
            health_checks.append(redis_health)
        
        # Check cluster health
        if self.cluster_monitor:
            cluster_health = await self.cluster_monitor.check_cluster_health()
            health_checks.extend(cluster_health)
        
        # Check backup health
        if self.failover_manager:
            backup_health = await self.failover_manager.check_backup_health()
            health_checks.extend(backup_health)
        
        # Analyze overall health
        overall_status = self._analyze_overall_health(health_checks)
        
        # Create health snapshot
        health_snapshot = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': overall_status.value,
            'consecutive_failures': self.consecutive_failures,
            'time_since_healthy': (datetime.now() - self.last_healthy_time).total_seconds(),
            'health_checks': [hc.to_dict() for hc in health_checks],
            'cluster_status': self.cluster_monitor.get_cluster_status() if self.cluster_monitor else None,
            'failover_history': [fe.to_dict() for fe in self.failover_manager.failover_history] if self.failover_manager else []
        }
        
        # Add to history
        self.health_history.append(health_snapshot)
        
        # Update consecutive failures
        if overall_status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]:
            self.consecutive_failures = 0
            self.last_healthy_time = datetime.now()
        else:
            self.consecutive_failures += 1
        
        # Check for automatic failover
        await self._check_automatic_failover(health_checks, overall_status)
        
        # Notify handlers
        await self._notify_health_handlers(health_snapshot)
        
        return health_snapshot
    
    def _analyze_overall_health(self, health_checks: List[HealthCheck]) -> HealthStatus:
        """Analyze overall system health."""
        if not health_checks:
            return HealthStatus.UNKNOWN
        
        # Count statuses
        status_counts = defaultdict(int)
        for check in health_checks:
            status_counts[check.status] += 1
        
        # Determine overall status
        if status_counts[HealthStatus.CRITICAL] > 0:
            return HealthStatus.CRITICAL
        elif status_counts[HealthStatus.UNHEALTHY] > 0:
            return HealthStatus.UNHEALTHY
        elif status_counts[HealthStatus.DEGRADED] > 0:
            return HealthStatus.DEGRADED
        elif status_counts[HealthStatus.HEALTHY] == len(health_checks):
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.UNKNOWN
    
    async def _check_automatic_failover(
        self,
        health_checks: List[HealthCheck],
        overall_status: HealthStatus
    ):
        """Check if automatic failover is needed."""
        if not self.failover_manager:
            return
        
        # Check failover conditions
        need_failover = False
        failover_reason = ""
        
        # Consecutive failures
        if self.consecutive_failures >= self.alert_thresholds['consecutive_failures']:
            need_failover = True
            failover_reason = f"Consecutive failures: {self.consecutive_failures}"
        
        # Critical component failure
        critical_checks = [hc for hc in health_checks if hc.status == HealthStatus.CRITICAL]
        if critical_checks:
            need_failover = True
            failover_reason = f"Critical component failure: {critical_checks[0].component}"
        
        if need_failover:
            logger.warning(f"Automatic failover triggered: {failover_reason}")
            
            # Perform failover
            failover_event = await self.failover_manager.perform_failover(
                from_component="primary",
                reason=failover_reason,
                health_checks=health_checks
            )
            
            if failover_event:
                logger.info(f"Failover completed: {failover_event.to_dict()}")
            else:
                logger.error("Failover failed")
    
    async def _notify_health_handlers(self, health_snapshot: Dict[str, Any]):
        """Notify health event handlers."""
        for handler in self.health_event_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(health_snapshot)
                else:
                    handler(health_snapshot)
            except Exception as e:
                logger.error(f"Health handler error: {e}")
    
    async def _background_monitoring(self):
        """Background health monitoring task."""
        while self._running:
            try:
                await self.check_system_health()
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Background monitoring error: {e}")
                await asyncio.sleep(self.check_interval)
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health monitoring summary."""
        if not self.health_history:
            return {'status': 'no_data'}
        
        latest_health = self.health_history[-1]
        
        # Calculate uptime percentage
        healthy_checks = sum(1 for h in self.health_history 
                           if h['overall_status'] in ['healthy', 'degraded'])
        uptime_percentage = (healthy_checks / len(self.health_history)) * 100
        
        return {
            'current_status': latest_health['overall_status'],
            'uptime_percentage': uptime_percentage,
            'consecutive_failures': self.consecutive_failures,
            'time_since_healthy': latest_health['time_since_healthy'],
            'last_check': latest_health['timestamp'],
            'monitoring_active': self._running,
            'check_interval': self.check_interval,
            'total_health_checks': len(self.health_history)
        }


# Global health monitor instance
_health_monitor: Optional[CacheHealthMonitor] = None


async def get_health_monitor() -> CacheHealthMonitor:
    """Get the global health monitor."""
    global _health_monitor
    if _health_monitor is None:
        # Default configuration
        config = {
            'check_interval': 60,
            'alert_thresholds': {
                'consecutive_failures': 3,
                'response_time_p95': 0.2,
                'memory_usage': 0.9
            }
        }
        _health_monitor = CacheHealthMonitor(config)
        await _health_monitor.initialize()
    return _health_monitor


# Convenience functions
async def check_cache_health() -> Dict[str, Any]:
    """Check cache health (convenience function)."""
    monitor = await get_health_monitor()
    return await monitor.check_system_health()


async def get_health_summary() -> Dict[str, Any]:
    """Get health summary (convenience function)."""
    monitor = await get_health_monitor()
    return monitor.get_health_summary()
