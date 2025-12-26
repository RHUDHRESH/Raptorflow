"""
Part 21: Distributed Search Architecture
RaptorFlow Unified Search System - Industrial Grade AI Agent Search Infrastructure
===============================================================================
This module implements distributed search architecture, load balancing, and
horizontal scaling capabilities for the unified search system.
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import hashlib
from collections import defaultdict, deque
import aiohttp
import aiofiles

from core.unified_search_part1 import SearchQuery, SearchResult, SearchMode
from core.unified_search_part2 import SearchProvider
from core.unified_search_part10 import unified_search_engine

logger = logging.getLogger("raptorflow.unified_search.distributed")


class NodeStatus(Enum):
    """Node status types."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    FAILED = "failed"
    STARTING = "starting"
    STOPPING = "stopping"


class LoadBalancingStrategy(Enum):
    """Load balancing strategies."""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    HASH_BASED = "hash_based"
    ADAPTIVE = "adaptive"


@dataclass
class SearchNode:
    """Distributed search node."""
    node_id: str
    host: str
    port: int
    status: NodeStatus
    capabilities: Set[str]
    max_concurrent_searches: int
    current_searches: int = 0
    total_searches: int = 0
    failed_searches: int = 0
    avg_response_time_ms: float = 0.0
    last_health_check: datetime = field(default_factory=datetime.now)
    last_heartbeat: datetime = field(default_factory=datetime.now)
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'node_id': self.node_id,
            'host': self.host,
            'port': self.port,
            'status': self.status.value,
            'capabilities': list(self.capabilities),
            'max_concurrent_searches': self.max_concurrent_searches,
            'current_searches': self.current_searches,
            'total_searches': self.total_searches,
            'failed_searches': self.failed_searches,
            'avg_response_time_ms': self.avg_response_time_ms,
            'last_health_check': self.last_health_check.isoformat(),
            'last_heartbeat': self.last_heartbeat.isoformat(),
            'weight': self.weight,
            'metadata': self.metadata
        }
    
    @property
    def is_healthy(self) -> bool:
        """Check if node is healthy."""
        return (
            self.status == NodeStatus.ACTIVE and
            (datetime.now() - self.last_heartbeat).total_seconds() < 60
        )
    
    @property
    def load_ratio(self) -> float:
        """Get current load ratio."""
        return self.current_searches / self.max_concurrent_searches if self.max_concurrent_searches > 0 else 1.0
    
    @property
    def failure_rate(self) -> float:
        """Get failure rate."""
        return self.failed_searches / self.total_searches if self.total_searches > 0 else 0.0


@dataclass
class DistributedSearchRequest:
    """Distributed search request."""
    request_id: str
    query: SearchQuery
    originating_node: str
    target_nodes: List[str]
    strategy: str
    timeout_seconds: int
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'request_id': self.request_id,
            'query': {
                'text': self.query.text,
                'mode': self.query.mode.value,
                'max_results': self.query.max_results
            },
            'originating_node': self.originating_node,
            'target_nodes': self.target_nodes,
            'strategy': self.strategy,
            'timeout_seconds': self.timeout_seconds,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class DistributedSearchResult:
    """Distributed search result."""
    request_id: str
    node_id: str
    results: List[SearchResult]
    execution_time_ms: float
    success: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'request_id': self.request_id,
            'node_id': self.node_id,
            'results': [result.to_dict() for result in self.results],
            'execution_time_ms': self.execution_time_ms,
            'success': self.success,
            'error_message': self.error_message,
            'metadata': self.metadata
        }


class NodeRegistry:
    """Registry for managing search nodes."""
    
    def __init__(self):
        self.nodes: Dict[str, SearchNode] = {}
        self.capabilities_index: Dict[str, Set[str]] = defaultdict(set)
        self._lock = asyncio.Lock()
    
    async def register_node(self, node: SearchNode) -> bool:
        """Register a new search node."""
        async with self._lock:
            # Check if node already exists
            if node.node_id in self.nodes:
                existing_node = self.nodes[node.node_id]
                if existing_node.status != NodeStatus.FAILED:
                    logger.warning(f"Node {node.node_id} already registered")
                    return False
            
            # Register node
            self.nodes[node.node_id] = node
            
            # Update capabilities index
            for capability in node.capabilities:
                self.capabilities_index[capability].add(node.node_id)
            
            logger.info(f"Registered node: {node.node_id} at {node.host}:{node.port}")
            return True
    
    async def unregister_node(self, node_id: str) -> bool:
        """Unregister a search node."""
        async with self._lock:
            node = self.nodes.get(node_id)
            if not node:
                return False
            
            # Remove from capabilities index
            for capability in node.capabilities:
                self.capabilities_index[capability].discard(node_id)
            
            # Remove node
            del self.nodes[node_id]
            
            logger.info(f"Unregistered node: {node_id}")
            return True
    
    async def update_node_status(self, node_id: str, status: NodeStatus) -> bool:
        """Update node status."""
        async with self._lock:
            node = self.nodes.get(node_id)
            if not node:
                return False
            
            old_status = node.status
            node.status = status
            node.last_heartbeat = datetime.now()
            
            if old_status != status:
                logger.info(f"Node {node_id} status changed: {old_status.value} -> {status.value}")
            
            return True
    
    async def update_node_metrics(self, node_id: str, metrics: Dict[str, Any]) -> bool:
        """Update node metrics."""
        async with self._lock:
            node = self.nodes.get(node_id)
            if not node:
                return False
            
            node.current_searches = metrics.get('current_searches', node.current_searches)
            node.total_searches = metrics.get('total_searches', node.total_searches)
            node.failed_searches = metrics.get('failed_searches', node.failed_searches)
            node.avg_response_time_ms = metrics.get('avg_response_time_ms', node.avg_response_time_ms)
            node.last_heartbeat = datetime.now()
            
            return True
    
    def get_healthy_nodes(self) -> List[SearchNode]:
        """Get all healthy nodes."""
        return [node for node in self.nodes.values() if node.is_healthy]
    
    def get_nodes_by_capability(self, capability: str) -> List[SearchNode]:
        """Get nodes with specific capability."""
        node_ids = self.capabilities_index.get(capability, set())
        return [self.nodes[node_id] for node_id in node_ids if node_id in self.nodes]
    
    def get_node(self, node_id: str) -> Optional[SearchNode]:
        """Get node by ID."""
        return self.nodes.get(node_id)
    
    def get_all_nodes(self) -> List[SearchNode]:
        """Get all nodes."""
        return list(self.nodes.values())
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        total_nodes = len(self.nodes)
        healthy_nodes = len(self.get_healthy_nodes())
        
        status_counts = defaultdict(int)
        for node in self.nodes.values():
            status_counts[node.status.value] += 1
        
        capability_counts = {cap: len(nodes) for cap, nodes in self.capabilities_index.items()}
        
        return {
            'total_nodes': total_nodes,
            'healthy_nodes': healthy_nodes,
            'unhealthy_nodes': total_nodes - healthy_nodes,
            'status_distribution': dict(status_counts),
            'capability_distribution': capability_counts,
            'avg_load_ratio': sum(node.load_ratio for node in self.get_healthy_nodes()) / healthy_nodes if healthy_nodes > 0 else 0
        }


class LoadBalancer:
    """Load balancer for distributing search requests."""
    
    def __init__(self, node_registry: NodeRegistry):
        self.node_registry = node_registry
        self.strategy = LoadBalancingStrategy.ROUND_ROBIN
        self.round_robin_index = 0
        self.request_history = deque(maxlen=1000)
    
    def set_strategy(self, strategy: LoadBalancingStrategy):
        """Set load balancing strategy."""
        self.strategy = strategy
        logger.info(f"Load balancing strategy changed to: {strategy.value}")
    
    def select_nodes(
        self,
        request: DistributedSearchRequest,
        count: int = 3,
        required_capabilities: Optional[Set[str]] = None
    ) -> List[SearchNode]:
        """Select nodes for search request."""
        healthy_nodes = self.node_registry.get_healthy_nodes()
        
        # Filter by capabilities if required
        if required_capabilities:
            capable_nodes = []
            for node in healthy_nodes:
                if required_capabilities.issubset(node.capabilities):
                    capable_nodes.append(node)
            healthy_nodes = capable_nodes
        
        if not healthy_nodes:
            logger.warning("No healthy nodes available")
            return []
        
        # Apply load balancing strategy
        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            selected = self._round_robin_selection(healthy_nodes, count)
        elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            selected = self._least_connections_selection(healthy_nodes, count)
        elif self.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            selected = self._weighted_round_robin_selection(healthy_nodes, count)
        elif self.strategy == LoadBalancingStrategy.HASH_BASED:
            selected = self._hash_based_selection(healthy_nodes, request, count)
        elif self.strategy == LoadBalancingStrategy.ADAPTIVE:
            selected = self._adaptive_selection(healthy_nodes, request, count)
        else:
            selected = self._round_robin_selection(healthy_nodes, count)
        
        # Record selection
        self.request_history.append({
            'timestamp': datetime.now(),
            'strategy': self.strategy.value,
            'selected_nodes': [node.node_id for node in selected],
            'request_id': request.request_id
        })
        
        return selected
    
    def _round_robin_selection(self, nodes: List[SearchNode], count: int) -> List[SearchNode]:
        """Round-robin node selection."""
        if not nodes:
            return []
        
        selected = []
        for i in range(count):
            node = nodes[self.round_robin_index % len(nodes)]
            selected.append(node)
            self.round_robin_index += 1
        
        return selected
    
    def _least_connections_selection(self, nodes: List[SearchNode], count: int) -> List[SearchNode]:
        """Select nodes with least connections."""
        sorted_nodes = sorted(nodes, key=lambda n: n.current_searches)
        return sorted_nodes[:count]
    
    def _weighted_round_robin_selection(self, nodes: List[SearchNode], count: int) -> List[SearchNode]:
        """Weighted round-robin selection."""
        # Create weighted list
        weighted_nodes = []
        for node in nodes:
            weight = int(node.weight * 10)  # Scale weight
            weighted_nodes.extend([node] * weight)
        
        if not weighted_nodes:
            return []
        
        selected = []
        for i in range(count):
            node = weighted_nodes[self.round_robin_index % len(weighted_nodes)]
            selected.append(node)
            self.round_robin_index += 1
        
        return selected
    
    def _hash_based_selection(self, nodes: List[SearchNode], request: DistributedSearchRequest, count: int) -> List[SearchNode]:
        """Hash-based node selection."""
        # Create hash from request
        hash_input = f"{request.query.text}_{request.query.mode.value}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        
        # Select nodes based on hash
        selected = []
        for i in range(count):
            node_index = hash_value % len(nodes)
            selected.append(nodes[node_index])
            hash_value = hash_value // len(nodes) + 1  # Modify hash for next selection
        
        return selected
    
    def _adaptive_selection(self, nodes: List[SearchNode], request: DistributedSearchRequest, count: int) -> List[SearchNode]:
        """Adaptive node selection based on performance."""
        # Score nodes based on multiple factors
        scored_nodes = []
        for node in nodes:
            score = 0.0
            
            # Load factor (lower is better)
            load_score = 1.0 - node.load_ratio
            score += load_score * 0.4
            
            # Response time (lower is better)
            response_score = 1.0 / (1.0 + node.avg_response_time_ms / 1000.0)
            score += response_score * 0.3
            
            # Success rate (higher is better)
            success_score = 1.0 - node.failure_rate
            score += success_score * 0.2
            
            # Weight factor
            score += node.weight * 0.1
            
            scored_nodes.append((node, score))
        
        # Sort by score and select top nodes
        scored_nodes.sort(key=lambda x: x[1], reverse=True)
        return [node for node, score in scored_nodes[:count]]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get load balancer statistics."""
        recent_requests = list(self.request_history)[-100:]  # Last 100 requests
        
        node_usage = defaultdict(int)
        for req in recent_requests:
            for node_id in req['selected_nodes']:
                node_usage[node_id] += 1
        
        return {
            'strategy': self.strategy.value,
            'recent_requests': len(recent_requests),
            'node_usage_distribution': dict(node_usage),
            'round_robin_index': self.round_robin_index
        }


class DistributedSearchCoordinator:
    """Coordinates distributed search operations."""
    
    def __init__(self, node_registry: NodeRegistry, load_balancer: LoadBalancer):
        self.node_registry = node_registry
        self.load_balancer = load_balancer
        self.active_requests: Dict[str, DistributedSearchRequest] = {}
        self.request_results: Dict[str, List[DistributedSearchResult]] = {}
        self.http_session: Optional[aiohttp.ClientSession] = None
        self.request_timeout = 30.0
        self.max_concurrent_requests = 100
        self._cleanup_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the distributed search coordinator."""
        self.http_session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.request_timeout)
        )
        
        # Start cleanup task
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info("Distributed search coordinator started")
    
    async def stop(self):
        """Stop the distributed search coordinator."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        if self.http_session:
            await self.http_session.close()
        
        logger.info("Distributed search coordinator stopped")
    
    async def execute_distributed_search(
        self,
        query: SearchQuery,
        node_count: int = 3,
        required_capabilities: Optional[Set[str]] = None,
        strategy: str = "adaptive"
    ) -> List[SearchResult]:
        """Execute distributed search."""
        request_id = str(uuid.uuid4())
        
        # Create distributed request
        request = DistributedSearchRequest(
            request_id=request_id,
            query=query,
            originating_node="coordinator",
            target_nodes=[],
            strategy=strategy,
            timeout_seconds=int(self.request_timeout)
        )
        
        # Select target nodes
        target_nodes = self.load_balancer.select_nodes(
            request, node_count, required_capabilities
        )
        
        if not target_nodes:
            logger.error("No nodes available for distributed search")
            return []
        
        request.target_nodes = [node.node_id for node in target_nodes]
        self.active_requests[request_id] = request
        self.request_results[request_id] = []
        
        logger.info(f"Executing distributed search {request_id} on {len(target_nodes)} nodes")
        
        try:
            # Execute search on selected nodes
            tasks = []
            for node in target_nodes:
                task = self._execute_node_search(node, request)
                tasks.append(task)
            
            # Wait for all searches to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            all_results = []
            successful_nodes = 0
            
            for result in results:
                if isinstance(result, DistributedSearchResult):
                    self.request_results[request_id].append(result)
                    
                    if result.success:
                        all_results.extend(result.results)
                        successful_nodes += 1
                    else:
                        logger.warning(f"Node {result.node_id} failed: {result.error_message}")
                elif isinstance(result, Exception):
                    logger.error(f"Search execution error: {result}")
            
            logger.info(f"Distributed search {request_id} completed: {successful_nodes}/{len(target_nodes)} nodes successful")
            
            # Consolidate and deduplicate results
            consolidated_results = self._consolidate_results(all_results, query)
            
            return consolidated_results[:query.max_results]
            
        finally:
            # Clean up request
            self.active_requests.pop(request_id, None)
            # Keep results for a while for debugging
            asyncio.create_task(self._cleanup_request_results(request_id))
    
    async def _execute_node_search(self, node: SearchNode, request: DistributedSearchRequest) -> DistributedSearchResult:
        """Execute search on a specific node."""
        start_time = time.time()
        
        try:
            # Update node metrics
            node.current_searches += 1
            
            # Make HTTP request to node
            url = f"http://{node.host}:{node.port}/api/search"
            
            payload = {
                'query': request.query.text,
                'mode': request.query.mode.value,
                'max_results': request.query.max_results,
                'content_types': [ct.value for ct in request.query.content_types],
                'request_id': request.request_id
            }
            
            async with self.http_session.post(url, json=payload) as response:
                if response.status == 200:
                    response_data = await response.json()
                    
                    # Convert to SearchResult objects
                    results = []
                    for result_data in response_data.get('results', []):
                        result = SearchResult(
                            url=result_data['url'],
                            title=result_data['title'],
                            content=result_data.get('content'),
                            snippet=result_data.get('snippet'),
                            provider=SearchProvider(result_data.get('provider', 'native')),
                            relevance_score=result_data.get('relevance_score', 0.0)
                        )
                        results.append(result)
                    
                    execution_time = (time.time() - start_time) * 1000
                    
                    # Update node metrics
                    node.total_searches += 1
                    node.avg_response_time_ms = (node.avg_response_time_ms * (node.total_searches - 1) + execution_time) / node.total_searches
                    
                    return DistributedSearchResult(
                        request_id=request.request_id,
                        node_id=node.node_id,
                        results=results,
                        execution_time_ms=execution_time,
                        success=True
                    )
                else:
                    error_text = await response.text()
                    raise Exception(f"HTTP {response.status}: {error_text}")
        
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            
            # Update node metrics
            node.failed_searches += 1
            node.total_searches += 1
            
            return DistributedSearchResult(
                request_id=request.request_id,
                node_id=node.node_id,
                results=[],
                execution_time_ms=execution_time,
                success=False,
                error_message=str(e)
            )
        
        finally:
            node.current_searches -= 1
    
    def _consolidate_results(self, results: List[SearchResult], query: SearchQuery) -> List[SearchResult]:
        """Consolidate results from multiple nodes."""
        # Simple consolidation - in production, use sophisticated deduplication
        seen_urls = set()
        consolidated = []
        
        for result in results:
            if result.url not in seen_urls:
                seen_urls.add(result.url)
                consolidated.append(result)
        
        # Sort by relevance score
        consolidated.sort(key=lambda r: r.relevance_score, reverse=True)
        
        return consolidated
    
    async def _cleanup_request_results(self, request_id: str):
        """Clean up request results after delay."""
        await asyncio.sleep(300)  # Keep for 5 minutes
        self.request_results.pop(request_id, None)
    
    async def _cleanup_loop(self):
        """Cleanup old requests and maintain health."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                # Clean up old requests
                cutoff_time = datetime.now() - timedelta(minutes=10)
                old_requests = [
                    req_id for req_id, req in self.active_requests.items()
                    if req.created_at < cutoff_time
                ]
                
                for req_id in old_requests:
                    self.active_requests.pop(req_id, None)
                    self.request_results.pop(req_id, None)
                
                if old_requests:
                    logger.info(f"Cleaned up {len(old_requests)} old requests")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get coordinator statistics."""
        return {
            'active_requests': len(self.active_requests),
            'pending_results': len(self.request_results),
            'node_registry_stats': self.node_registry.get_stats(),
            'load_balancer_stats': self.load_balancer.get_stats()
        }


class DistributedSearchManager:
    """Manages the entire distributed search system."""
    
    def __init__(self):
        self.node_registry = NodeRegistry()
        self.load_balancer = LoadBalancer(self.node_registry)
        self.coordinator = DistributedSearchCoordinator(self.node_registry, self.load_balancer)
        self.is_running = False
    
    async def start(self):
        """Start the distributed search system."""
        await self.coordinator.start()
        self.is_running = True
        logger.info("Distributed search system started")
    
    async def stop(self):
        """Stop the distributed search system."""
        await self.coordinator.stop()
        self.is_running = False
        logger.info("Distributed search system stopped")
    
    async def add_node(
        self,
        host: str,
        port: int,
        capabilities: Set[str],
        max_concurrent_searches: int = 10,
        weight: float = 1.0
    ) -> str:
        """Add a new search node."""
        node_id = str(uuid.uuid4())
        
        node = SearchNode(
            node_id=node_id,
            host=host,
            port=port,
            status=NodeStatus.STARTING,
            capabilities=capabilities,
            max_concurrent_searches=max_concurrent_searches,
            weight=weight
        )
        
        success = await self.node_registry.register_node(node)
        if success:
            # Try to health check the node
            await self._health_check_node(node)
        
        return node_id if success else ""
    
    async def remove_node(self, node_id: str) -> bool:
        """Remove a search node."""
        return await self.node_registry.unregister_node(node_id)
    
    async def search(
        self,
        query: SearchQuery,
        node_count: int = 3,
        required_capabilities: Optional[Set[str]] = None
    ) -> List[SearchResult]:
        """Execute distributed search."""
        if not self.is_running:
            raise RuntimeError("Distributed search system not running")
        
        return await self.coordinator.execute_distributed_search(
            query, node_count, required_capabilities
        )
    
    async def _health_check_node(self, node: SearchNode):
        """Perform health check on node."""
        try:
            # Simple health check - in production, implement proper health check
            await asyncio.sleep(0.1)  # Simulate network delay
            
            # Update node status to active
            await self.node_registry.update_node_status(node.node_id, NodeStatus.ACTIVE)
            
        except Exception as e:
            logger.error(f"Health check failed for node {node.node_id}: {e}")
            await self.node_registry.update_node_status(node.node_id, NodeStatus.FAILED)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        return {
            'is_running': self.is_running,
            'coordinator_stats': self.coordinator.get_stats(),
            'timestamp': datetime.now().isoformat()
        }


# Global distributed search manager
distributed_search_manager = DistributedSearchManager()
