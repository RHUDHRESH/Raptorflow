"""
Part 28: Search Federation and Cross-System Integration
RaptorFlow Unified Search System - Industrial Grade AI Agent Search Infrastructure
===============================================================================
This module implements search federation, cross-system integration, and
distributed search coordination across multiple search systems.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
from collections import defaultdict, deque
import aiohttp
import hashlib

from core.unified_search_part1 import SearchQuery, SearchResult, SearchMode, ContentType
from core.unified_search_part2 import SearchProvider

logger = logging.getLogger("raptorflow.unified_search.federation")


class FederationStrategy(Enum):
    """Search federation strategies."""
    BROADCAST = "broadcast"
    SELECTIVE = "selective"
    HIERARCHICAL = "hierarchical"
    ADAPTIVE = "adaptive"
    LOAD_BALANCED = "load_balanced"
    GEOGRAPHIC = "geographic"


class FederationProtocol(Enum):
    """Federation protocols."""
    REST_API = "rest_api"
    GRPC = "grpc"
    MESSAGE_QUEUE = "message_queue"
    WEBSOCKET = "websocket"
    CUSTOM = "custom"


class FederationStatus(Enum):
    """Federation member status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"


@dataclass
class FederationMember:
    """Federation member configuration."""
    member_id: str
    name: str
    endpoint_url: str
    protocol: FederationProtocol
    capabilities: Set[str]
    priority: int = 0
    max_concurrent_requests: int = 50
    timeout_seconds: int = 30
    retry_attempts: int = 3
    authentication: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: FederationStatus = FederationStatus.ACTIVE
    last_health_check: Optional[datetime] = None
    response_time_ms: float = 0.0
    success_rate: float = 1.0
    total_requests: int = 0
    failed_requests: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'member_id': self.member_id,
            'name': self.name,
            'endpoint_url': self.endpoint_url,
            'protocol': self.protocol.value,
            'capabilities': list(self.capabilities),
            'priority': self.priority,
            'status': self.status.value,
            'last_health_check': self.last_health_check.isoformat() if self.last_health_check else None,
            'response_time_ms': self.response_time_ms,
            'success_rate': self.success_rate,
            'total_requests': self.total_requests,
            'failed_requests': self.failed_requests,
            'metadata': self.metadata
        }
    
    @property
    def is_available(self) -> bool:
        """Check if member is available."""
        return (
            self.status == FederationStatus.ACTIVE and
            self.success_rate >= 0.8 and
            self.response_time_ms < 5000
        )


@dataclass
class FederationQuery:
    """Federated search query."""
    query_id: str
    original_query: SearchQuery
    target_members: List[str]
    strategy: FederationStrategy
    timeout_seconds: int
    merge_strategy: str = "relevance_weighted"
    include_metadata: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'query_id': self.query_id,
            'original_query': {
                'text': self.original_query.text,
                'mode': self.original_query.mode.value,
                'max_results': self.original_query.max_results
            },
            'target_members': self.target_members,
            'strategy': self.strategy.value,
            'timeout_seconds': self.timeout_seconds,
            'merge_strategy': self.merge_strategy,
            'include_metadata': self.include_metadata,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class FederationResponse:
    """Federation member response."""
    response_id: str
    query_id: str
    member_id: str
    results: List[SearchResult]
    response_time_ms: float
    success: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    received_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'response_id': self.response_id,
            'query_id': self.query_id,
            'member_id': self.member_id,
            'results_count': len(self.results),
            'response_time_ms': self.response_time_ms,
            'success': self.success,
            'error_message': self.error_message,
            'metadata': self.metadata,
            'received_at': self.received_at.isoformat()
        }


@dataclass
class FederationMetrics:
    """Federation metrics."""
    total_queries: int = 0
    successful_queries: int = 0
    failed_queries: int = 0
    avg_response_time_ms: float = 0.0
    member_utilization: Dict[str, float] = field(default_factory=dict)
    query_distribution: Dict[str, int] = field(default_factory=dict)
    error_types: Dict[str, int] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'total_queries': self.total_queries,
            'successful_queries': self.successful_queries,
            'failed_queries': self.failed_queries,
            'success_rate': self.successful_queries / self.total_queries if self.total_queries > 0 else 0,
            'avg_response_time_ms': self.avg_response_time_ms,
            'member_utilization': self.member_utilization,
            'query_distribution': self.query_distribution,
            'error_types': self.error_types,
            'timestamp': self.timestamp.isoformat()
        }


class FederationRegistry:
    """Registry for federation members."""
    
    def __init__(self):
        self.members: Dict[str, FederationMember] = {}
        self.capabilities_index: Dict[str, Set[str]] = defaultdict(set)
        self._lock = asyncio.Lock()
    
    async def register_member(self, member: FederationMember) -> bool:
        """Register a federation member."""
        async with self._lock:
            self.members[member.member_id] = member
            
            # Update capabilities index
            for capability in member.capabilities:
                self.capabilities_index[capability].add(member.member_id)
            
            logger.info(f"Registered federation member: {member.name}")
            return True
    
    async def unregister_member(self, member_id: str) -> bool:
        """Unregister a federation member."""
        async with self._lock:
            if member_id not in self.members:
                return False
            
            member = self.members[member_id]
            
            # Remove from capabilities index
            for capability in member.capabilities:
                self.capabilities_index[capability].discard(member_id)
                if not self.capabilities_index[capability]:
                    del self.capabilities_index[capability]
            
            del self.members[member_id]
            
            logger.info(f"Unregistered federation member: {member_id}")
            return True
    
    async def get_members_by_capability(self, capability: str) -> List[FederationMember]:
        """Get members that support a specific capability."""
        async with self._lock:
            member_ids = self.capabilities_index.get(capability, set())
            return [self.members[mid] for mid in member_ids if mid in self.members]
    
    async def get_available_members(self) -> List[FederationMember]:
        """Get all available members."""
        async with self._lock:
            return [member for member in self.members.values() if member.is_available]
    
    async def get_member(self, member_id: str) -> Optional[FederationMember]:
        """Get member by ID."""
        async with self._lock:
            return self.members.get(member_id)
    
    async def update_member_status(self, member_id: str, status: FederationStatus):
        """Update member status."""
        async with self._lock:
            if member_id in self.members:
                self.members[member_id].status = status
                logger.info(f"Updated member {member_id} status to {status.value}")
    
    async def update_member_metrics(self, member_id: str, response_time_ms: float, success: bool):
        """Update member performance metrics."""
        async with self._lock:
            if member_id not in self.members:
                return
            
            member = self.members[member_id]
            member.total_requests += 1
            
            if not success:
                member.failed_requests += 1
            
            # Update success rate
            member.success_rate = (member.total_requests - member.failed_requests) / member.total_requests
            
            # Update response time (exponential moving average)
            if member.response_time_ms == 0:
                member.response_time_ms = response_time_ms
            else:
                member.response_time_ms = (member.response_time_ms * 0.8) + (response_time_ms * 0.2)
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        total_members = len(self.members)
        active_members = len([m for m in self.members.values() if m.status == FederationStatus.ACTIVE])
        available_members = len([m for m in self.members.values() if m.is_available])
        
        capability_counts = {cap: len(members) for cap, members in self.capabilities_index.items()}
        
        return {
            'total_members': total_members,
            'active_members': active_members,
            'available_members': available_members,
            'capabilities': capability_counts,
            'protocols': {
                protocol.value: len([m for m in self.members.values() if m.protocol == protocol])
                for protocol in FederationProtocol
            }
        }


class FederationQueryRouter:
    """Routes federated queries to appropriate members."""
    
    def __init__(self, registry: FederationRegistry):
        self.registry = registry
        self.query_history: deque = deque(maxlen=1000)
        self.routing_strategies = {
            FederationStrategy.BROADCAST: self._route_broadcast,
            FederationStrategy.SELECTIVE: self._route_selective,
            FederationStrategy.HIERARCHICAL: self._route_hierarchical,
            FederationStrategy.ADAPTIVE: self._route_adaptive,
            FederationStrategy.LOAD_BALANCED: self._route_load_balanced,
            FederationStrategy.GEOGRAPHIC: self._route_geographic
        }
    
    async def route_query(
        self,
        query: SearchQuery,
        strategy: FederationStrategy,
        target_capabilities: Optional[Set[str]] = None,
        max_members: Optional[int] = None
    ) -> List[FederationMember]:
        """Route query to appropriate federation members."""
        router = self.routing_strategies.get(strategy, self._route_broadcast)
        
        try:
            members = await router(query, target_capabilities, max_members)
            
            # Record routing decision
            self.query_history.append({
                'query_text': query.text,
                'strategy': strategy.value,
                'selected_members': [m.member_id for m in members],
                'timestamp': datetime.now()
            })
            
            return members
            
        except Exception as e:
            logger.error(f"Error routing query: {e}")
            return []
    
    async def _route_broadcast(
        self,
        query: SearchQuery,
        target_capabilities: Optional[Set[str]],
        max_members: Optional[int]
    ) -> List[FederationMember]:
        """Broadcast to all available members."""
        members = await self.registry.get_available_members()
        
        if target_capabilities:
            # Filter by capabilities
            capable_members = []
            for capability in target_capabilities:
                capable_members.extend(await self.registry.get_members_by_capability(capability))
            
            # Remove duplicates while preserving order
            seen = set()
            members = []
            for member in capable_members:
                if member.member_id not in seen and member.is_available:
                    seen.add(member.member_id)
                    members.append(member)
        
        if max_members:
            members = members[:max_members]
        
        return members
    
    async def _route_selective(
        self,
        query: SearchQuery,
        target_capabilities: Optional[Set[str]],
        max_members: Optional[int]
    ) -> List[FederationMember]:
        """Selectively route based on query characteristics."""
        members = await self.registry.get_available_members()
        
        # Analyze query to determine best members
        query_lower = query.text.lower()
        
        # Priority based on query type
        if 'academic' in query_lower or 'research' in query_lower:
            target_capabilities = target_capabilities or {'academic_search', 'scholarly_content'}
        elif 'news' in query_lower or 'recent' in query_lower:
            target_capabilities = target_capabilities or {'news_search', 'real_time'}
        elif 'image' in query_lower or 'video' in query_lower:
            target_capabilities = target_capabilities or {'multimedia_search'}
        
        if target_capabilities:
            # Get members with required capabilities
            capable_members = []
            for capability in target_capabilities:
                capable_members.extend(await self.registry.get_members_by_capability(capability))
            
            # Remove duplicates and filter by availability
            seen = set()
            members = []
            for member in capable_members:
                if member.member_id not in seen and member.is_available:
                    seen.add(member.member_id)
                    members.append(member)
        
        # Sort by priority and success rate
        members.sort(key=lambda m: (m.priority, m.success_rate), reverse=True)
        
        if max_members:
            members = members[:max_members]
        
        return members
    
    async def _route_hierarchical(
        self,
        query: SearchQuery,
        target_capabilities: Optional[Set[str]],
        max_members: Optional[int]
    ) -> List[FederationMember]:
        """Hierarchical routing based on member priority."""
        members = await self.registry.get_available_members()
        
        # Sort by priority (higher first)
        members.sort(key=lambda m: m.priority, reverse=True)
        
        if max_members:
            members = members[:max_members]
        
        return members
    
    async def _route_adaptive(
        self,
        query: SearchQuery,
        target_capabilities: Optional[Set[str]],
        max_members: Optional[int]
    ) -> List[FederationMember]:
        """Adaptive routing based on performance history."""
        members = await self.registry.get_available_members()
        
        # Score members based on multiple factors
        scored_members = []
        for member in members:
            score = 0.0
            
            # Success rate (40% weight)
            score += member.success_rate * 0.4
            
            # Response time (30% weight, lower is better)
            time_score = max(0, 1 - (member.response_time_ms / 5000))  # Normalize to 0-1
            score += time_score * 0.3
            
            # Priority (20% weight)
            priority_score = min(1.0, member.priority / 10.0)  # Normalize priority
            score += priority_score * 0.2
            
            # Recent performance (10% weight)
            recent_performance = 1.0  # Could be calculated from recent queries
            score += recent_performance * 0.1
            
            scored_members.append((member, score))
        
        # Sort by score (highest first)
        scored_members.sort(key=lambda x: x[1], reverse=True)
        members = [member for member, score in scored_members]
        
        if max_members:
            members = members[:max_members]
        
        return members
    
    async def _route_load_balanced(
        self,
        query: SearchQuery,
        target_capabilities: Optional[Set[str]],
        max_members: Optional[int]
    ) -> List[FederationMember]:
        """Load-balanced routing."""
        members = await self.registry.get_available_members()
        
        # Sort by current load (fewer requests first)
        members.sort(key=lambda m: m.total_requests)
        
        if max_members:
            members = members[:max_members]
        
        return members
    
    async def _route_geographic(
        self,
        query: SearchQuery,
        target_capabilities: Optional[Set[str]],
        max_members: Optional[int]
    ) -> List[FederationMember]:
        """Geographic routing (mock implementation)."""
        members = await self.registry.get_available_members()
        
        # In a real implementation, this would consider geographic proximity
        # For now, just use member metadata to simulate geographic distribution
        geo_groups = defaultdict(list)
        for member in members:
            region = member.metadata.get('region', 'unknown')
            geo_groups[region].append(member)
        
        # Select from the largest region (load balancing)
        if geo_groups:
            largest_region = max(geo_groups.keys(), key=lambda r: len(geo_groups[r]))
            members = geo_groups[largest_region]
        
        if max_members:
            members = members[:max_members]
        
        return members


class FederationExecutor:
    """Executes federated search queries."""
    
    def __init__(self, registry: FederationRegistry, router: FederationQueryRouter):
        self.registry = registry
        self.router = router
        self.active_queries: Dict[str, FederationQuery] = {}
        self.query_responses: Dict[str, List[FederationResponse]] = defaultdict(list)
        self.http_session: Optional[aiohttp.ClientSession] = None
        self._lock = asyncio.Lock()
    
    async def start(self):
        """Start federation executor."""
        self.http_session = aiohttp.ClientSession()
        logger.info("Federation executor started")
    
    async def stop(self):
        """Stop federation executor."""
        if self.http_session:
            await self.http_session.close()
        logger.info("Federation executor stopped")
    
    async def execute_federated_search(
        self,
        query: SearchQuery,
        strategy: FederationStrategy = FederationStrategy.ADAPTIVE,
        target_capabilities: Optional[Set[str]] = None,
        max_members: Optional[int] = None,
        timeout_seconds: int = 30
    ) -> Tuple[List[SearchResult], Dict[str, Any]]:
        """Execute federated search query."""
        query_id = str(uuid.uuid4())
        
        # Create federation query
        fed_query = FederationQuery(
            query_id=query_id,
            original_query=query,
            target_members=[],
            strategy=strategy,
            timeout_seconds=timeout_seconds
        )
        
        # Route query to members
        target_members = await self.router.route_query(
            query, strategy, target_capabilities, max_members
        )
        
        if not target_members:
            return [], {'error': 'No available federation members'}
        
        fed_query.target_members = [m.member_id for m in target_members]
        
        async with self._lock:
            self.active_queries[query_id] = fed_query
        
        try:
            # Execute queries in parallel
            tasks = [
                self._execute_member_query(member, fed_query)
                for member in target_members
            ]
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process responses
            successful_responses = []
            failed_responses = []
            
            for response in responses:
                if isinstance(response, Exception):
                    failed_responses.append(str(response))
                elif response and response.success:
                    successful_responses.append(response)
                else:
                    failed_responses.append(response.error_message if response else "Unknown error")
            
            # Merge results
            merged_results = await self._merge_results(successful_responses, fed_query.merge_strategy)
            
            # Update member metrics
            for response in successful_responses:
                await self.registry.update_member_metrics(
                    response.member_id,
                    response.response_time_ms,
                    True
                )
            
            # Record failed requests
            for member in target_members:
                if not any(r.member_id == member.member_id for r in successful_responses):
                    await self.registry.update_member_metrics(member.member_id, timeout_seconds * 1000, False)
            
            metadata = {
                'query_id': query_id,
                'strategy': strategy.value,
                'target_members': len(target_members),
                'successful_members': len(successful_responses),
                'failed_members': len(failed_responses),
                'total_results': len(merged_results),
                'responses': [r.to_dict() for r in successful_responses],
                'errors': failed_responses
            }
            
            return merged_results, metadata
            
        finally:
            async with self._lock:
                self.active_queries.pop(query_id, None)
                self.query_responses.pop(query_id, None)
    
    async def _execute_member_query(
        self,
        member: FederationMember,
        fed_query: FederationQuery
    ) -> Optional[FederationResponse]:
        """Execute query on individual federation member."""
        response_id = str(uuid.uuid4())
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Prepare request based on protocol
            if member.protocol == FederationProtocol.REST_API:
                results, response_time = await self._execute_rest_query(member, fed_query)
            elif member.protocol == FederationProtocol.GRPC:
                results, response_time = await self._execute_grpc_query(member, fed_query)
            else:
                raise ValueError(f"Unsupported protocol: {member.protocol}")
            
            response = FederationResponse(
                response_id=response_id,
                query_id=fed_query.query_id,
                member_id=member.member_id,
                results=results,
                response_time_ms=response_time,
                success=True
            )
            
            return response
            
        except Exception as e:
            response_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            response = FederationResponse(
                response_id=response_id,
                query_id=fed_query.query_id,
                member_id=member.member_id,
                results=[],
                response_time_ms=response_time,
                success=False,
                error_message=str(e)
            )
            
            return response
    
    async def _execute_rest_query(
        self,
        member: FederationMember,
        fed_query: FederationQuery
    ) -> Tuple[List[SearchResult], float]:
        """Execute REST API query."""
        start_time = asyncio.get_event_loop().time()
        
        # Prepare request
        url = f"{member.endpoint_url}/search"
        payload = {
            'query': fed_query.original_query.text,
            'mode': fed_query.original_query.mode.value,
            'max_results': fed_query.original_query.max_results,
            'content_types': [ct.value for ct in fed_query.original_query.content_types]
        }
        
        headers = {'Content-Type': 'application/json'}
        
        # Add authentication if configured
        if member.authentication:
            auth_type = member.authentication.get('type')
            if auth_type == 'api_key':
                headers['Authorization'] = f"Bearer {member.authentication.get('api_key')}"
            elif auth_type == 'basic':
                import base64
                credentials = f"{member.authentication.get('username')}:{member.authentication.get('password')}"
                headers['Authorization'] = f"Basic {base64.b64encode(credentials.encode()).decode()}"
        
        # Make request
        async with self.http_session.post(
            url,
            json=payload,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=member.timeout_seconds)
        ) as response:
            if response.status != 200:
                raise Exception(f"HTTP {response.status}: {await response.text()}")
            
            data = await response.json()
            
            # Convert to SearchResult objects
            results = []
            for item in data.get('results', []):
                result = SearchResult(
                    url=item.get('url', ''),
                    title=item.get('title', ''),
                    content=item.get('content', ''),
                    snippet=item.get('snippet', ''),
                    provider=SearchProvider.NATIVE,  # Default
                    relevance_score=item.get('relevance_score', 0.0)
                )
                results.append(result)
            
            response_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return results, response_time
    
    async def _execute_grpc_query(
        self,
        member: FederationMember,
        fed_query: FederationQuery
    ) -> Tuple[List[SearchResult], float]:
        """Execute gRPC query (mock implementation)."""
        # Mock gRPC implementation
        await asyncio.sleep(0.5)  # Simulate network latency
        
        # Mock results
        results = []
        for i in range(min(5, fed_query.original_query.max_results)):
            result = SearchResult(
                url=f"https://grpc-member.com/result{i+1}",
                title=f"GRPC Result {i+1}",
                content=f"Content from {member.name}",
                snippet=f"Snippet from {member.name}",
                provider=SearchProvider.NATIVE,
                relevance_score=0.8 - (i * 0.1)
            )
            results.append(result)
        
        return results, 500.0  # 500ms response time
    
    async def _merge_results(
        self,
        responses: List[FederationResponse],
        merge_strategy: str
    ) -> List[SearchResult]:
        """Merge results from multiple federation members."""
        if not responses:
            return []
        
        all_results = []
        result_sources = {}  # Track which member provided each result
        
        for response in responses:
            for result in response.results:
                all_results.append(result)
                result_sources[result.url] = response.member_id
        
        if merge_strategy == "relevance_weighted":
            # Weight by member success rate and relevance
            for response in responses:
                member = await self.registry.get_member(response.member_id)
                if member:
                    weight = member.success_rate
                    for result in response.results:
                        result.relevance_score *= weight
        
        # Deduplicate results
        seen_urls = set()
        deduplicated_results = []
        
        for result in all_results:
            if result.url not in seen_urls:
                seen_urls.add(result.url)
                deduplicated_results.append(result)
        
        # Sort by relevance score
        deduplicated_results.sort(key=lambda r: r.relevance_score, reverse=True)
        
        return deduplicated_results
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        total_queries = len(self.query_history)
        
        if total_queries > 0:
            strategy_counts = defaultdict(int)
            for query in self.query_history:
                strategy_counts[query['strategy']] += 1
            
            return {
                'total_queries': total_queries,
                'active_queries': len(self.active_queries),
                'strategy_distribution': dict(strategy_counts),
                'avg_members_per_query': sum(len(q['selected_members']) for q in self.query_history) / total_queries
            }
        else:
            return {
                'total_queries': 0,
                'active_queries': 0,
                'strategy_distribution': {},
                'avg_members_per_query': 0
            }


class SearchFederationManager:
    """Main search federation manager."""
    
    def __init__(self):
        self.registry = FederationRegistry()
        self.router = FederationQueryRouter(self.registry)
        self.executor = FederationExecutor(self.registry, self.router)
        self.metrics = FederationMetrics()
        self._health_check_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start federation manager."""
        await self.executor.start()
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        
        # Add default federation members (mock)
        await self._add_default_members()
        
        logger.info("Search federation manager started")
    
    async def stop(self):
        """Stop federation manager."""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        await self.executor.stop()
        logger.info("Search federation manager stopped")
    
    async def _add_default_members(self):
        """Add default federation members."""
        # Academic search member
        academic_member = FederationMember(
            member_id="academic_search",
            name="Academic Search Service",
            endpoint_url="https://academic-search.example.com",
            protocol=FederationProtocol.REST_API,
            capabilities={"academic_search", "scholarly_content", "citation_analysis"},
            priority=8,
            metadata={'region': 'us-east', 'type': 'academic'}
        )
        await self.registry.register_member(academic_member)
        
        # News search member
        news_member = FederationMember(
            member_id="news_search",
            name="Real-time News Service",
            endpoint_url="https://news-search.example.com",
            protocol=FederationProtocol.REST_API,
            capabilities={"news_search", "real_time", "breaking_news"},
            priority=7,
            metadata={'region': 'us-west', 'type': 'news'}
        )
        await self.registry.register_member(news_member)
        
        # Multimedia search member
        multimedia_member = FederationMember(
            member_id="multimedia_search",
            name="Multimedia Search Service",
            endpoint_url="https://multimedia-search.example.com",
            protocol=FederationProtocol.GRPC,
            capabilities={"multimedia_search", "image_search", "video_search"},
            priority=6,
            metadata={'region': 'eu-central', 'type': 'multimedia'}
        )
        await self.registry.register_member(multimedia_member)
    
    async def search_federated(
        self,
        query: SearchQuery,
        strategy: FederationStrategy = FederationStrategy.ADAPTIVE,
        target_capabilities: Optional[Set[str]] = None,
        max_members: Optional[int] = None
    ) -> Tuple[List[SearchResult], Dict[str, Any]]:
        """Execute federated search."""
        start_time = asyncio.get_event_loop().time()
        
        try:
            results, metadata = await self.executor.execute_federated_search(
                query, strategy, target_capabilities, max_members
            )
            
            # Update metrics
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            self.metrics.total_queries += 1
            
            if results:
                self.metrics.successful_queries += 1
            
            self.metrics.avg_response_time_ms = (
                (self.metrics.avg_response_time_ms * (self.metrics.total_queries - 1) + execution_time) /
                self.metrics.total_queries
            )
            
            # Update member utilization
            for member_id in metadata.get('target_members', []):
                self.metrics.member_utilization[member_id] = self.metrics.member_utilization.get(member_id, 0) + 1
            
            return results, metadata
            
        except Exception as e:
            self.metrics.failed_queries += 1
            self.metrics.error_types['execution_error'] = self.metrics.error_types.get('execution_error', 0) + 1
            
            logger.error(f"Federated search failed: {e}")
            return [], {'error': str(e)}
    
    async def _health_check_loop(self):
        """Health check loop for federation members."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                for member in self.registry.members.values():
                    await self._check_member_health(member)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Federation health check error: {e}")
    
    async def _check_member_health(self, member: FederationMember):
        """Check individual member health."""
        try:
            if member.protocol == FederationProtocol.REST_API:
                # Simple health check via REST API
                url = f"{member.endpoint_url}/health"
                
                async with self.executor.http_session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        await self.registry.update_member_status(member.member_id, FederationStatus.ACTIVE)
                    else:
                        await self.registry.update_member_status(member.member_id, FederationStatus.ERROR)
            
            elif member.protocol == FederationProtocol.GRPC:
                # Mock gRPC health check
                await asyncio.sleep(0.1)
                await self.registry.update_member_status(member.member_id, FederationStatus.ACTIVE)
            
            member.last_health_check = datetime.now()
            
        except Exception as e:
            await self.registry.update_member_status(member.member_id, FederationStatus.ERROR)
            logger.warning(f"Health check failed for {member.name}: {e}")
    
    def get_federation_stats(self) -> Dict[str, Any]:
        """Get federation statistics."""
        return {
            'registry': self.registry.get_registry_stats(),
            'execution': self.executor.get_execution_stats(),
            'metrics': self.metrics.to_dict()
        }


# Global search federation manager
search_federation_manager = SearchFederationManager()
