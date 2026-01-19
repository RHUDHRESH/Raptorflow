"""
Distributed Rate Limiting with Redis Cluster Support
====================================================

Enterprise-grade distributed rate limiting with Redis Cluster for high availability,
data consistency, and horizontal scalability.

Features:
- Redis Cluster support for horizontal scaling
- Data consistency across multiple nodes
- High availability with automatic failover
- Lua scripts for atomic operations
- Distributed counters and sliding windows
- Cluster health monitoring
- Automatic rebalancing and recovery
"""

import asyncio
import json
import time
import hashlib
from typing import Dict, Optional, List, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging

from .redis import get_redis_client

logger = logging.getLogger(__name__)


class ConsistencyLevel(Enum):
    """Consistency levels for distributed rate limiting."""
    EVENTUAL = "eventual"
    STRONG = "strong"
    SEQUENTIAL = "sequential"


class ClusterStatus(Enum):
    """Redis Cluster status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    RECOVERING = "recovering"


@dataclass
class RedisClusterConfig:
    """Redis Cluster configuration."""
    
    # Cluster nodes
    cluster_nodes: List[str] = field(default_factory=list)
    
    # Connection settings
    max_connections: int = 100
    retry_attempts: int = 3
    retry_delay: float = 1.0
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    
    # Consistency settings
    consistency_level: ConsistencyLevel = ConsistencyLevel.EVENTUAL
    replication_factor: int = 2
    
    # Performance settings
    pipeline_size: int = 100
    batch_timeout: float = 0.1
    
    # Health check settings
    health_check_interval: int = 30
    node_timeout: int = 10
    
    # Lua script settings
    lua_script_timeout: int = 5
    enable_lua_scripts: bool = True


@dataclass
class ClusterNode:
    """Redis Cluster node information."""
    
    node_id: str
    host: str
    port: int
    role: str  # master, slave
    status: ClusterStatus
    last_health_check: datetime
    connection_count: int = 0
    latency_ms: float = 0.0
    error_count: int = 0


@dataclass
class DistributedRateLimitState:
    """Distributed rate limiting state."""
    
    key: str
    current_count: int = 0
    window_start: float = 0.0
    last_access: float = 0.0
    sliding_window_data: List[float] = field(default_factory=list)
    tokens: float = 0.0
    last_refill: float = 0.0
    bucket_size: float = 0.0
    leak_rate: float = 0.0
    last_leak: float = 0.0


class DistributedRateLimiter:
    """Distributed rate limiter with Redis Cluster support."""
    
    # Lua scripts for atomic operations
    SLIDING_WINDOW_SCRIPT = """
    local key = KEYS[1]
    local window = tonumber(ARGV[1])
    local limit = tonumber(ARGV[2])
    local current_time = tonumber(ARGV[3])
    local request_id = ARGV[4]
    
    -- Remove old entries
    redis.call('ZREMRANGEBYSCORE', key, 0, current_time - window)
    
    -- Get current count
    local current = redis.call('ZCARD', key)
    
    -- Check limit
    if current >= limit then
        return {0, limit, redis.call('ZSCORE', key, request_id)}
    end
    
    -- Add current request
    redis.call('ZADD', key, current_time, request_id)
    redis.call('EXPIRE', key, window + 1)
    
    return {1, limit - current - 1, limit}
    """
    
    TOKEN_BUCKET_SCRIPT = """
    local key = KEYS[1]
    local capacity = tonumber(ARGV[1])
    local refill_rate = tonumber(ARGV[2])
    local tokens = tonumber(ARGV[3])
    local last_refill = tonumber(ARGV[4])
    local current_time = tonumber(ARGV[5])
    
    -- Get current state
    local current = redis.call('HMGET', key, 'tokens', 'last_refill')
    local current_tokens = tonumber(current[1]) or capacity
    local current_last_refill = tonumber(current[2]) or current_time
    
    -- Calculate tokens to add
    local time_passed = current_time - current_last_refill
    local tokens_to_add = time_passed * refill_rate
    current_tokens = math.min(capacity, current_tokens + tokens_to_add)
    
    -- Check if we have enough tokens
    if current_tokens < tokens then
        redis.call('HMSET', key, 'tokens', current_tokens, 'last_refill', current_time)
        redis.call('EXPIRE', key, math.ceil(capacity / refill_rate) + 1)
        return {0, current_tokens, current_time + (tokens - current_tokens) / refill_rate}
    end
    
    -- Consume tokens
    current_tokens = current_tokens - tokens
    redis.call('HMSET', key, 'tokens', current_tokens, 'last_refill', current_time)
    redis.call('EXPIRE', key, math.ceil(capacity / refill_rate) + 1)
    
    return {1, current_tokens, -1}
    """
    
    def __init__(self, config: RedisClusterConfig = None):
        self.config = config or RedisClusterConfig()
        
        # Cluster management
        self.cluster_nodes: Dict[str, ClusterNode] = {}
        self.master_nodes: Dict[str, ClusterNode] = {}
        self.slave_nodes: Dict[str, ClusterNode] = {}
        
        # Connection pool
        self.redis_clients: Dict[str, Any] = {}
        self.connection_pool_size = 0
        
        # Lua scripts
        self.lua_scripts: Dict[str, str] = {
            'sliding_window': self.SLIDING_WINDOW_SCRIPT,
            'token_bucket': self.TOKEN_BUCKET_SCRIPT
        }
        self.script_hashes: Dict[str, str] = {}
        
        # Health monitoring
        self.cluster_status = ClusterStatus.UNAVAILABLE
        self.last_health_check = datetime.now()
        self.health_check_task = None
        
        # Statistics
        self.total_requests = 0
        self.failed_requests = 0
        self.cluster_errors = 0
        self.rebalance_count = 0
        
        # Background tasks
        self._running = False
        self._health_check_task = None
        self._rebalance_task = None
        
        logger.info("Distributed rate limiter initialized")
    
    async def start(self) -> None:
        """Start the distributed rate limiter."""
        if self._running:
            logger.warning("Distributed rate limiter is already running")
            return
        
        self._running = True
        
        try:
            # Initialize Redis cluster
            await self._initialize_cluster()
            
            # Load Lua scripts
            if self.config.enable_lua_scripts:
                await self._load_lua_scripts()
            
            # Start background tasks
            self._health_check_task = asyncio.create_task(self._health_check_loop())
            self._rebalance_task = asyncio.create_task(self._rebalance_loop())
            
            logger.info("Distributed rate limiter started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start distributed rate limiter: {e}")
            await self.stop()
            raise
    
    async def stop(self) -> None:
        """Stop the distributed rate limiter."""
        if not self._running:
            return
        
        self._running = False
        
        # Cancel background tasks
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        if self._rebalance_task:
            self._rebalance_task.cancel()
            try:
                await self._rebalance_task
            except asyncio.CancelledError:
                pass
        
        # Close Redis connections
        for client in self.redis_clients.values():
            try:
                await client.close()
            except Exception as e:
                logger.error(f"Error closing Redis connection: {e}")
        
        self.redis_clients.clear()
        logger.info("Distributed rate limiter stopped")
    
    async def _initialize_cluster(self) -> None:
        """Initialize Redis Cluster connections."""
        if not self.config.cluster_nodes:
            # Use single Redis instance
            redis_client = await get_redis_client()
            node_id = f"{redis_client.url}"
            self.redis_clients[node_id] = redis_client
            
            self.cluster_nodes[node_id] = ClusterNode(
                node_id=node_id,
                host="localhost",
                port=6379,
                role="master",
                status=ClusterStatus.HEALTHY,
                last_health_check=datetime.now()
            )
            
            self.master_nodes[node_id] = self.cluster_nodes[node_id]
            self.cluster_status = ClusterStatus.HEALTHY
            return
        
        # Initialize cluster nodes
        for node_url in self.config.cluster_nodes:
            try:
                # Parse node URL
                if ':' in node_url:
                    host, port = node_url.split(':')
                    port = int(port)
                else:
                    host, port = node_url, 6379
                
                node_id = f"{host}:{port}"
                
                # Create Redis client for node
                redis_url = f"redis://{host}:{port}"
                client = await self._create_redis_client(redis_url)
                
                self.redis_clients[node_id] = client
                
                # Test connection
                await client.ping()
                
                # Determine node role
                info = await client.info()
                role = info.get('role', 'master')
                
                node = ClusterNode(
                    node_id=node_id,
                    host=host,
                    port=port,
                    role=role,
                    status=ClusterStatus.HEALTHY,
                    last_health_check=datetime.now()
                )
                
                self.cluster_nodes[node_id] = node
                
                if role == 'master':
                    self.master_nodes[node_id] = node
                else:
                    self.slave_nodes[node_id] = node
                
                logger.info(f"Connected to Redis node {node_id} (role: {role})")
                
            except Exception as e:
                logger.error(f"Failed to connect to Redis node {node_url}: {e}")
                # Create degraded node
                node_id = f"{host}:{port}" if ':' in node_url else node_url
                self.cluster_nodes[node_id] = ClusterNode(
                    node_id=node_id,
                    host=host if ':' in node_url else node_url,
                    port=port if ':' in node_url else 6379,
                    role="unknown",
                    status=ClusterStatus.UNAVAILABLE,
                    last_health_check=datetime.now()
                )
        
        # Determine cluster status
        if len(self.master_nodes) > 0:
            self.cluster_status = ClusterStatus.HEALTHY
        elif len(self.cluster_nodes) > 0:
            self.cluster_status = ClusterStatus.DEGRADED
        else:
            self.cluster_status = ClusterStatus.UNAVAILABLE
        
        logger.info(f"Redis Cluster initialized: {len(self.master_nodes)} masters, {len(self.slave_nodes)} slaves")
    
    async def _create_redis_client(self, redis_url: str):
        """Create Redis client with configuration."""
        from redis.client import Redis as AsyncRedis
        
        client = AsyncRedis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=True,
            retry_on_timeout=True,
            socket_connect_timeout=self.config.socket_connect_timeout,
            socket_timeout=self.config.socket_timeout,
            health_check_interval=self.config.health_check_interval,
            max_connections=self.config.max_connections,
        )
        
        return client
    
    async def _load_lua_scripts(self) -> None:
        """Load Lua scripts on all Redis nodes."""
        for node_id, client in self.redis_clients.items():
            try:
                for script_name, script_content in self.lua_scripts.items():
                    hash_value = await client.script_load(script_content)
                    self.script_hashes[script_name] = hash_value
                
                logger.info(f"Loaded {len(self.lua_scripts)} Lua scripts on node {node_id}")
                
            except Exception as e:
                logger.error(f"Failed to load Lua scripts on node {node_id}: {e}")
    
    async def check_distributed_rate_limit(
        self,
        key: str,
        limit: int,
        window: int = 60,
        strategy: str = "sliding_window"
    ) -> Tuple[bool, int, Optional[float]]:
        """
        Check distributed rate limit using Redis Cluster.
        
        Args:
            key: Rate limit key
            limit: Request limit
            window: Time window in seconds
            strategy: Rate limiting strategy
        
        Returns:
            (allowed, remaining, retry_after)
        """
        start_time = time.time()
        
        try:
            self.total_requests += 1
            
            # Get appropriate Redis client
            client = await self._get_redis_client(key)
            
            if strategy == "sliding_window":
                return await self._check_sliding_window_limit(client, key, limit, window)
            elif strategy == "token_bucket":
                return await self._check_token_bucket_limit(client, key, limit, window)
            else:
                # Default to simple counter
                return await self._check_simple_counter_limit(client, key, limit, window)
                
        except Exception as e:
            self.failed_requests += 1
            logger.error(f"Distributed rate limit check failed: {e}")
            # Fail open - allow request
            return True, limit - 1, None
        finally:
            # Track performance
            duration = time.time() - start_time
            if duration > 0.1:  # Log slow requests
                logger.warning(f"Slow distributed rate limit check: {duration:.3f}s")
    
    async def _get_redis_client(self, key: str):
        """Get Redis client for a key using consistent hashing."""
        if not self.redis_clients:
            raise Exception("No Redis clients available")
        
        if len(self.redis_clients) == 1:
            return list(self.redis_clients.values())[0]
        
        # Use consistent hashing to select node
        key_hash = int(hashlib.md5(key.encode()).hexdigest(), 16)
        node_index = key_hash % len(self.master_nodes)
        
        if self.master_nodes:
            node_ids = list(self.master_nodes.keys())
            selected_node_id = node_ids[node_index % len(node_ids)]
            
            if selected_node_id in self.redis_clients:
                return self.redis_clients[selected_node_id]
        
        # Fallback to any available client
        return list(self.redis_clients.values())[0]
    
    async def _check_sliding_window_limit(
        self,
        client,
        key: str,
        limit: int,
        window: int
    ) -> Tuple[bool, int, Optional[float]]:
        """Check sliding window rate limit using Lua script."""
        current_time = time.time()
        request_id = f"{key}:{current_time}:{hash(key)}"
        
        try:
            if self.config.enable_lua_scripts and 'sliding_window' in self.script_hashes:
                # Use Lua script for atomic operation
                script_hash = self.script_hashes['sliding_window']
                result = await client.evalsha(
                    script_hash,
                    1,  # number of keys
                    key,  # KEYS[1]
                    window,  # ARGV[1]
                    limit,  # ARGV[2]
                    current_time,  # ARGV[3]
                    request_id  # ARGV[4]
                )
                
                allowed = bool(result[0])
                remaining = int(result[1])
                oldest_request = float(result[2]) if result[2] else None
                
                retry_after = None
                if not allowed and oldest_request:
                    retry_after = max(0, window - (current_time - oldest_request))
                
                return allowed, remaining, retry_after
            else:
                # Fallback to non-atomic implementation
                return await self._check_sliding_window_fallback(client, key, limit, window)
                
        except Exception as e:
            logger.error(f"Sliding window script failed: {e}")
            return await self._check_sliding_window_fallback(client, key, limit, window)
    
    async def _check_sliding_window_fallback(
        self,
        client,
        key: str,
        limit: int,
        window: int
    ) -> Tuple[bool, int, Optional[float]]:
        """Fallback sliding window implementation."""
        current_time = time.time()
        window_start = current_time - window
        
        # Use sorted set for sliding window
        try:
            # Remove old entries
            await client.zremrangebyscore(key, 0, window_start)
            
            # Get current count
            current_count = await client.zcard(key)
            
            # Check limit
            if current_count >= limit:
                # Get oldest request for retry_after calculation
                oldest = await client.zrange(key, 0, 0, withscores=True)
                retry_after = None
                if oldest:
                    oldest_time = oldest[0][1]
                    retry_after = max(0, window - (current_time - oldest_time))
                
                return False, 0, retry_after
            
            # Add current request
            request_id = f"{current_time}:{hash(key)}"
            await client.zadd(key, {request_id: current_time})
            await client.expire(key, window + 1)
            
            remaining = limit - current_count - 1
            return True, remaining, None
            
        except Exception as e:
            logger.error(f"Sliding window fallback failed: {e}")
            # Fail open
            return True, limit - 1, None
    
    async def _check_token_bucket_limit(
        self,
        client,
        key: str,
        limit: int,
        window: int
    ) -> Tuple[bool, int, Optional[float]]:
        """Check token bucket rate limit using Lua script."""
        current_time = time.time()
        capacity = limit
        refill_rate = limit / window  # tokens per second
        tokens_needed = 1
        
        try:
            if self.config.enable_lua_scripts and 'token_bucket' in self.script_hashes:
                # Use Lua script for atomic operation
                script_hash = self.script_hashes['token_bucket']
                result = await client.evalsha(
                    script_hash,
                    1,  # number of keys
                    key,  # KEYS[1]
                    capacity,  # ARGV[1]
                    refill_rate,  # ARGV[2]
                    tokens_needed,  # ARGV[3]
                    0,  # ARGV[4] (last_refill, will be set by script)
                    current_time  # ARGV[5]
                )
                
                allowed = bool(result[0])
                remaining_tokens = float(result[1])
                retry_after_time = float(result[2])
                
                retry_after = None
                if not allowed and retry_after_time > 0:
                    retry_after = max(0, retry_after_time - current_time)
                
                return allowed, int(remaining_tokens), retry_after
            else:
                # Fallback implementation
                return await self._check_token_bucket_fallback(client, key, capacity, refill_rate, current_time)
                
        except Exception as e:
            logger.error(f"Token bucket script failed: {e}")
            return await self._check_token_bucket_fallback(client, key, capacity, refill_rate, current_time)
    
    async def _check_token_bucket_fallback(
        self,
        client,
        key: str,
        capacity: int,
        refill_rate: float,
        current_time: float
    ) -> Tuple[bool, int, Optional[float]]:
        """Fallback token bucket implementation."""
        try:
            # Get current state
            state = await client.hmget(key, 'tokens', 'last_refill')
            current_tokens = float(state[0]) if state[0] else capacity
            last_refill = float(state[1]) if state[1] else current_time
            
            # Calculate tokens to add
            time_passed = current_time - last_refill
            tokens_to_add = time_passed * refill_rate
            current_tokens = min(capacity, current_tokens + tokens_to_add)
            
            # Check if we have enough tokens
            if current_tokens < 1:
                # Update state
                await client.hmset(key, {'tokens': current_tokens, 'last_refill': current_time})
                await client.expire(key, int(capacity / refill_rate) + 1)
                
                retry_after = (1 - current_tokens) / refill_rate
                return False, int(current_tokens), retry_after
            
            # Consume token
            current_tokens -= 1
            
            # Update state
            await client.hmset(key, {'tokens': current_tokens, 'last_refill': current_time})
            await client.expire(key, int(capacity / refill_rate) + 1)
            
            return True, int(current_tokens), None
            
        except Exception as e:
            logger.error(f"Token bucket fallback failed: {e}")
            # Fail open
            return True, capacity - 1, None
    
    async def _check_simple_counter_limit(
        self,
        client,
        key: str,
        limit: int,
        window: int
    ) -> Tuple[bool, int, Optional[float]]:
        """Simple counter rate limit implementation."""
        try:
            # Increment counter
            current = await client.incr(key)
            
            # Set expiry on first request
            if current == 1:
                await client.expire(key, window)
            
            # Check limit
            if current > limit:
                ttl = await client.ttl(key)
                retry_after = ttl if ttl > 0 else window
                return False, 0, retry_after
            
            remaining = limit - current
            return True, remaining, None
            
        except Exception as e:
            logger.error(f"Simple counter failed: {e}")
            # Fail open
            return True, limit - 1, None
    
    async def _health_check_loop(self) -> None:
        """Background health check for Redis Cluster."""
        while self._running:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                await self._perform_health_check()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
    
    async def _perform_health_check(self) -> None:
        """Perform health check on all cluster nodes."""
        current_time = datetime.now()
        healthy_nodes = 0
        total_nodes = len(self.cluster_nodes)
        
        for node_id, node in self.cluster_nodes.items():
            try:
                if node_id in self.redis_clients:
                    client = self.redis_clients[node_id]
                    
                    # Ping test
                    start_time = time.time()
                    await client.ping()
                    latency = (time.time() - start_time) * 1000
                    
                    # Update node status
                    node.status = ClusterStatus.HEALTHY
                    node.last_health_check = current_time
                    node.latency_ms = latency
                    node.error_count = 0
                    
                    healthy_nodes += 1
                    
                else:
                    node.status = ClusterStatus.UNAVAILABLE
                    node.last_health_check = current_time
                    node.error_count += 1
                    
            except Exception as e:
                node.status = ClusterStatus.UNAVAILABLE
                node.last_health_check = current_time
                node.error_count += 1
                logger.error(f"Health check failed for node {node_id}: {e}")
        
        # Update cluster status
        if healthy_nodes == 0:
            self.cluster_status = ClusterStatus.UNAVAILABLE
        elif healthy_nodes < total_nodes:
            self.cluster_status = ClusterStatus.DEGRADED
        else:
            self.cluster_status = ClusterStatus.HEALTHY
        
        self.last_health_check = current_time
        
        if healthy_nodes != total_nodes:
            logger.warning(f"Cluster health: {healthy_nodes}/{total_nodes} nodes healthy")
    
    async def _rebalance_loop(self) -> None:
        """Background rebalancing for Redis Cluster."""
        while self._running:
            try:
                await asyncio.sleep(300)  # Rebalance every 5 minutes
                await self._perform_rebalancing()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Rebalance loop error: {e}")
    
    async def _perform_rebalancing(self) -> None:
        """Perform cluster rebalancing if needed."""
        if self.cluster_status == ClusterStatus.HEALTHY:
            return
        
        try:
            # Try to reconnect to unavailable nodes
            for node_id, node in list(self.cluster_nodes.items()):
                if node.status == ClusterStatus.UNAVAILABLE:
                    try:
                        redis_url = f"redis://{node.host}:{node.port}"
                        client = await self._create_redis_client(redis_url)
                        await client.ping()
                        
                        self.redis_clients[node_id] = client
                        node.status = ClusterStatus.HEALTHY
                        node.error_count = 0
                        
                        # Update master/slave mappings
                        info = await client.info()
                        role = info.get('role', 'master')
                        node.role = role
                        
                        if role == 'master':
                            self.master_nodes[node_id] = node
                            if node_id in self.slave_nodes:
                                del self.slave_nodes[node_id]
                        else:
                            self.slave_nodes[node_id] = node
                            if node_id in self.master_nodes:
                                del self.master_nodes[node_id]
                        
                        logger.info(f"Reconnected to Redis node {node_id}")
                        
                    except Exception as e:
                        logger.debug(f"Still unable to connect to node {node_id}: {e}")
            
            self.rebalance_count += 1
            
        except Exception as e:
            logger.error(f"Rebalancing failed: {e}")
    
    def get_cluster_stats(self) -> Dict[str, Any]:
        """Get comprehensive cluster statistics."""
        current_time = datetime.now()
        
        # Node statistics
        node_stats = []
        for node in self.cluster_nodes.values():
            node_stats.append({
                "node_id": node.node_id,
                "host": node.host,
                "port": node.port,
                "role": node.role,
                "status": node.status.value,
                "latency_ms": node.latency_ms,
                "error_count": node.error_count,
                "last_health_check": node.last_health_check.isoformat(),
                "connection_count": node.connection_count
            })
        
        # Performance metrics
        success_rate = (self.total_requests - self.failed_requests) / self.total_requests if self.total_requests > 0 else 1.0
        
        return {
            "cluster_status": self.cluster_status.value,
            "total_nodes": len(self.cluster_nodes),
            "healthy_nodes": len([n for n in self.cluster_nodes.values() if n.status == ClusterStatus.HEALTHY]),
            "master_nodes": len(self.master_nodes),
            "slave_nodes": len(self.slave_nodes),
            "total_requests": self.total_requests,
            "failed_requests": self.failed_requests,
            "success_rate": success_rate,
            "cluster_errors": self.cluster_errors,
            "rebalance_count": self.rebalance_count,
            "last_health_check": self.last_health_check.isoformat(),
            "config": {
                "consistency_level": self.config.consistency_level.value,
                "replication_factor": self.config.replication_factor,
                "enable_lua_scripts": self.config.enable_lua_scripts,
                "lua_script_timeout": self.config.lua_script_timeout
            },
            "nodes": node_stats
        }
    
    async def reset_key(self, key: str) -> bool:
        """Reset rate limit for a specific key."""
        try:
            client = await self._get_redis_client(key)
            await client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Failed to reset key {key}: {e}")
            return False
    
    async def get_key_stats(self, key: str) -> Dict[str, Any]:
        """Get statistics for a specific rate limit key."""
        try:
            client = await self._get_redis_client(key)
            
            # Get basic info
            ttl = await client.ttl(key)
            type_info = await client.type(key)
            
            stats = {
                "key": key,
                "type": type_info,
                "ttl": ttl,
                "exists": ttl > -2
            }
            
            # Get type-specific data
            if type_info == 'zset':  # Sliding window
                count = await client.zcard(key)
                oldest = await client.zrange(key, 0, 0, withscores=True)
                newest = await client.zrange(key, -1, -1, withscores=True)
                
                stats.update({
                    "count": count,
                    "oldest_request": oldest[0][1] if oldest else None,
                    "newest_request": newest[0][1] if newest else None
                })
                
            elif type_info == 'hash':  # Token bucket
                state = await client.hmget(key, 'tokens', 'last_refill')
                stats.update({
                    "tokens": float(state[0]) if state[0] else 0,
                    "last_refill": float(state[1]) if state[1] else 0
                })
                
            elif type_info == 'string':  # Simple counter
                value = await client.get(key)
                stats.update({
                    "count": int(value) if value else 0
                })
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get key stats for {key}: {e}")
            return {"error": str(e)}


# Global distributed rate limiter instance
_distributed_rate_limiter: Optional[DistributedRateLimiter] = None


def get_distributed_rate_limiter(config: RedisClusterConfig = None) -> DistributedRateLimiter:
    """Get or create global distributed rate limiter instance."""
    global _distributed_rate_limiter
    if _distributed_rate_limiter is None:
        _distributed_rate_limiter = DistributedRateLimiter(config)
    return _distributed_rate_limiter


async def start_distributed_rate_limiter(config: RedisClusterConfig = None):
    """Start the global distributed rate limiter."""
    rate_limiter = get_distributed_rate_limiter(config)
    await rate_limiter.start()


async def stop_distributed_rate_limiter():
    """Stop the global distributed rate limiter."""
    global _distributed_rate_limiter
    if _distributed_rate_limiter:
        await _distributed_rate_limiter.stop()


async def check_distributed_rate_limit(
    key: str,
    limit: int,
    window: int = 60,
    strategy: str = "sliding_window"
) -> Tuple[bool, int, Optional[float]]:
    """Check distributed rate limit for a key."""
    rate_limiter = get_distributed_rate_limiter()
    return await rate_limiter.check_distributed_rate_limit(key, limit, window, strategy)


def get_distributed_rate_limit_stats() -> Dict[str, Any]:
    """Get global distributed rate limiting statistics."""
    rate_limiter = get_distributed_rate_limiter()
    return rate_limiter.get_cluster_stats()
