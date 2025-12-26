"""
Part 30: Final Integration and System Orchestration
RaptorFlow Unified Search System - Industrial Grade AI Agent Search Infrastructure
===============================================================================
This module provides the final integration, system orchestration, and unified
interface for the complete unified search system.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
from collections import defaultdict

# Import all unified search components
from core.unified_search_part1 import SearchQuery, SearchResult, SearchMode, ContentType
from core.unified_search_part2 import SearchProvider
from core.unified_search_part3 import AdvancedCrawler, CrawlPolicy
from core.unified_search_part4 import ResultConsolidator, ResultRanker
from core.unified_search_part5 import FaultTolerantExecutor, CircuitBreaker
from core.unified_search_part6 import DeepResearchAgent, ResearchPlan, ResearchDepth
from core.unified_search_part7 import UnifiedSearchInterface
from core.unified_search_part8 import analytics_engine, metrics_collector, performance_tracker
from core.unified_search_part9 import UnifiedSearchConfig, config_manager
from core.unified_search_part10 import unified_search_engine
from core.unified_search_part11 import UnifiedSearchTestSuite
from core.unified_search_part12 import UnifiedSearchAPI
from core.unified_search_part13 import MemoryCache, DistributedCache
from core.unified_search_part14 import AuthenticationManager, RateLimiter
from core.unified_search_part15 import AnalyticsEngine, InsightsGenerator
from core.unified_search_part16 import QueryAnalyzer, QueryOptimizer, SearchOrchestrator
from core.unified_search_part17 import MLManager, FeatureExtractor, RankingModel
from core.unified_search_part18 import RealTimeSearchManager, StreamingManager
from core.unified_search_part19 import ContentProcessor, NLPProcessor
from core.unified_search_part20 import MultiModalProcessor, MediaAnalyzer
from core.unified_search_part21 import DistributedSearchCoordinator, NodeRegistry
from core.unified_search_part22 import QueryPlanner, CostEstimator, PlanExecutor
from core.unified_search_part23 import QualityAssuranceEngine, ValidationRuleEngine
from core.unified_search_part24 import ResourceMonitor, OptimizationEngine, PerformanceTuner
from core.unified_search_part25 import metrics_collector as monitoring_metrics, alert_manager, observability_dashboard
from core.unified_search_part26 import analytics_dashboard, DataAggregator, DashboardRenderer
from core.unified_search_part27 import api_gateway, LoadBalancer, RateLimiter as GatewayRateLimiter
from core.unified_search_part28 import search_federation_manager, FederationRegistry, FederationQueryRouter
from core.unified_search_part29 import cache_manager, HybridCache

logger = logging.getLogger("raptorflow.unified_search.orchestrator")


class SystemStatus(Enum):
    """System status levels."""
    INITIALIZING = "initializing"
    RUNNING = "running"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    SHUTTING_DOWN = "shutting_down"


class ComponentType(Enum):
    """Component types for orchestration."""
    CORE = "core"
    CACHE = "cache"
    ANALYTICS = "analytics"
    MONITORING = "monitoring"
    SECURITY = "security"
    ML = "ml"
    DISTRIBUTED = "distributed"
    FEDERATION = "federation"
    API = "api"
    GATEWAY = "gateway"


@dataclass
class SystemComponent:
    """System component definition."""
    component_id: str
    name: str
    component_type: ComponentType
    status: SystemStatus = SystemStatus.INITIALIZING
    priority: int = 0
    dependencies: Set[str] = field(default_factory=set)
    health_check_interval_seconds: int = 30
    last_health_check: Optional[datetime] = None
    error_count: int = 0
    max_errors: int = 5
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'component_id': self.component_id,
            'name': self.name,
            'component_type': self.component_type.value,
            'status': self.status.value,
            'priority': self.priority,
            'dependencies': list(self.dependencies),
            'health_check_interval_seconds': self.health_check_interval_seconds,
            'last_health_check': self.last_health_check.isoformat() if self.last_health_check else None,
            'error_count': self.error_count,
            'max_errors': self.max_errors,
            'metadata': self.metadata
        }
    
    @property
    def is_healthy(self) -> bool:
        """Check if component is healthy."""
        return self.status == SystemStatus.RUNNING and self.error_count < self.max_errors


@dataclass
class SystemMetrics:
    """System-wide metrics."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time_ms: float = 0.0
    cache_hit_rate: float = 0.0
    system_load: float = 0.0
    memory_usage_mb: float = 0.0
    active_components: int = 0
    healthy_components: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'success_rate': self.successful_requests / self.total_requests if self.total_requests > 0 else 0,
            'avg_response_time_ms': self.avg_response_time_ms,
            'cache_hit_rate': self.cache_hit_rate,
            'system_load': self.system_load,
            'memory_usage_mb': self.memory_usage_mb,
            'active_components': self.active_components,
            'healthy_components': self.healthy_components,
            'health_rate': self.healthy_components / self.active_components if self.active_components > 0 else 0,
            'timestamp': self.timestamp.isoformat()
        }


class SystemOrchestrator:
    """Main system orchestrator for unified search."""
    
    def __init__(self):
        self.components: Dict[str, SystemComponent] = {}
        self.metrics = SystemMetrics()
        self.config: Optional[UnifiedSearchConfig] = None
        self._status = SystemStatus.INITIALIZING
        self._startup_time: Optional[datetime] = None
        self._shutdown_time: Optional[datetime] = None
        self._health_check_task: Optional[asyncio.Task] = None
        self._metrics_collection_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
        
        # Initialize component registry
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize system components."""
        # Core components
        self.components['search_engine'] = SystemComponent(
            component_id='search_engine',
            name='Unified Search Engine',
            component_type=ComponentType.CORE,
            priority=100
        )
        
        self.components['crawler'] = SystemComponent(
            component_id='crawler',
            name='Advanced Crawler',
            component_type=ComponentType.CORE,
            priority=90,
            dependencies={'search_engine'}
        )
        
        self.components['consolidator'] = SystemComponent(
            component_id='consolidator',
            name='Result Consolidator',
            component_type=ComponentType.CORE,
            priority=85,
            dependencies={'search_engine'}
        )
        
        # Cache components
        self.components['memory_cache'] = SystemComponent(
            component_id='memory_cache',
            name='Memory Cache',
            component_type=ComponentType.CACHE,
            priority=80
        )
        
        self.components['disk_cache'] = SystemComponent(
            component_id='disk_cache',
            name='Disk Cache',
            component_type=ComponentType.CACHE,
            priority=75,
            dependencies={'memory_cache'}
        )
        
        self.components['distributed_cache'] = SystemComponent(
            component_id='distributed_cache',
            name='Distributed Cache',
            component_type=ComponentType.CACHE,
            priority=70,
            dependencies={'memory_cache'}
        )
        
        # Analytics components
        self.components['analytics_engine'] = SystemComponent(
            component_id='analytics_engine',
            name='Analytics Engine',
            component_type=ComponentType.ANALYTICS,
            priority=65,
            dependencies={'search_engine'}
        )
        
        self.components['dashboard'] = SystemComponent(
            component_id='dashboard',
            name='Analytics Dashboard',
            component_type=ComponentType.ANALYTICS,
            priority=60,
            dependencies={'analytics_engine'}
        )
        
        # Monitoring components
        self.components['metrics_collector'] = SystemComponent(
            component_id='metrics_collector',
            name='Metrics Collector',
            component_type=ComponentType.MONITORING,
            priority=55
        )
        
        self.components['alert_manager'] = SystemComponent(
            component_id='alert_manager',
            name='Alert Manager',
            component_type=ComponentType.MONITORING,
            priority=50,
            dependencies={'metrics_collector'}
        )
        
        # Security components
        self.components['auth_manager'] = SystemComponent(
            component_id='auth_manager',
            name='Authentication Manager',
            component_type=ComponentType.SECURITY,
            priority=45
        )
        
        self.components['rate_limiter'] = SystemComponent(
            component_id='rate_limiter',
            name='Rate Limiter',
            component_type=ComponentType.SECURITY,
            priority=40,
            dependencies={'auth_manager'}
        )
        
        # ML components
        self.components['ml_manager'] = SystemComponent(
            component_id='ml_manager',
            name='ML Manager',
            component_type=ComponentType.ML,
            priority=35,
            dependencies={'search_engine'}
        )
        
        self.components['query_analyzer'] = SystemComponent(
            component_id='query_analyzer',
            name='Query Analyzer',
            component_type=ComponentType.ML,
            priority=30,
            dependencies={'ml_manager'}
        )
        
        # Distributed components
        self.components['distributed_coordinator'] = SystemComponent(
            component_id='distributed_coordinator',
            name='Distributed Coordinator',
            component_type=ComponentType.DISTRIBUTED,
            priority=25,
            dependencies={'search_engine'}
        )
        
        # Federation components
        self.components['federation_manager'] = SystemComponent(
            component_id='federation_manager',
            name='Search Federation Manager',
            component_type=ComponentType.FEDERATION,
            priority=20,
            dependencies={'search_engine'}
        )
        
        # API components
        self.components['api'] = SystemComponent(
            component_id='api',
            name='Unified Search API',
            component_type=ComponentType.API,
            priority=15,
            dependencies={'search_engine', 'auth_manager', 'rate_limiter'}
        )
        
        # Gateway components
        self.components['gateway'] = SystemComponent(
            component_id='gateway',
            name='API Gateway',
            component_type=ComponentType.GATEWAY,
            priority=10,
            dependencies={'api', 'rate_limiter'}
        )
    
    async def initialize(self, config: Optional[UnifiedSearchConfig] = None):
        """Initialize the entire system."""
        self._startup_time = datetime.now()
        self.config = config or UnifiedSearchConfig()
        
        logger.info("Initializing RaptorFlow Unified Search System...")
        
        try:
            # Initialize components in dependency order
            await self._initialize_components_by_priority()
            
            # Start background tasks
            await self._start_background_tasks()
            
            # Update system status
            self._status = SystemStatus.RUNNING
            
            logger.info(f"System initialized successfully in {(datetime.now() - self._startup_time).total_seconds():.2f} seconds")
            
        except Exception as e:
            logger.error(f"System initialization failed: {e}")
            self._status = SystemStatus.ERROR
            raise
    
    async def _initialize_components_by_priority(self):
        """Initialize components in priority order."""
        # Sort components by priority (highest first)
        sorted_components = sorted(
            self.components.values(),
            key=lambda c: c.priority,
            reverse=True
        )
        
        for component in sorted_components:
            try:
                await self._initialize_component(component)
            except Exception as e:
                logger.error(f"Failed to initialize component {component.name}: {e}")
                component.status = SystemStatus.ERROR
                component.error_count += 1
    
    async def _initialize_component(self, component: SystemComponent):
        """Initialize individual component."""
        logger.info(f"Initializing component: {component.name}")
        
        # Check dependencies
        for dep_id in component.dependencies:
            dep_component = self.components.get(dep_id)
            if not dep_component or dep_component.status != SystemStatus.RUNNING:
                raise Exception(f"Dependency {dep_id} not ready")
        
        # Initialize based on component type
        if component.component_id == 'search_engine':
            # Search engine is already initialized
            component.status = SystemStatus.RUNNING
        
        elif component.component_id == 'memory_cache':
            await cache_manager.initialize()
            component.status = SystemStatus.RUNNING
        
        elif component.component_id == 'disk_cache':
            # Disk cache is initialized with cache manager
            component.status = SystemStatus.RUNNING
        
        elif component.component_id == 'distributed_cache':
            # Distributed cache initialization
            component.status = SystemStatus.RUNNING
        
        elif component.component_id == 'analytics_engine':
            # Analytics engine is already initialized
            component.status = SystemStatus.RUNNING
        
        elif component.component_id == 'dashboard':
            # Dashboard is already initialized
            component.status = SystemStatus.RUNNING
        
        elif component.component_id == 'metrics_collector':
            # Metrics collector is already initialized
            component.status = SystemStatus.RUNNING
        
        elif component.component_id == 'alert_manager':
            await alert_manager.start_evaluation()
            component.status = SystemStatus.RUNNING
        
        elif component.component_id == 'api_gateway':
            await api_gateway.start()
            component.status = SystemStatus.RUNNING
        
        elif component.component_id == 'federation_manager':
            await search_federation_manager.start()
            component.status = SystemStatus.RUNNING
        
        else:
            # Default initialization for other components
            component.status = SystemStatus.RUNNING
        
        component.last_health_check = datetime.now()
        logger.info(f"Component {component.name} initialized successfully")
    
    async def _start_background_tasks(self):
        """Start background monitoring and metrics collection."""
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        self._metrics_collection_task = asyncio.create_task(self._metrics_collection_loop())
    
    async def _health_check_loop(self):
        """Background health check loop."""
        while self._status in [SystemStatus.RUNNING, SystemStatus.DEGRADED]:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                for component in self.components.values():
                    await self._check_component_health(component)
                
                # Update system metrics
                await self._update_system_metrics()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error: {e}")
    
    async def _check_component_health(self, component: SystemComponent):
        """Check health of individual component."""
        try:
            # Perform health check based on component type
            is_healthy = await self._perform_component_health_check(component)
            
            if is_healthy:
                if component.status == SystemStatus.ERROR:
                    component.error_count = 0
                
                component.status = SystemStatus.RUNNING
            else:
                component.error_count += 1
                
                if component.error_count >= component.max_errors:
                    component.status = SystemStatus.ERROR
                else:
                    component.status = SystemStatus.DEGRADED
            
            component.last_health_check = datetime.now()
            
        except Exception as e:
            logger.error(f"Health check failed for {component.name}: {e}")
            component.error_count += 1
            component.status = SystemStatus.ERROR
    
    async def _perform_component_health_check(self, component: SystemComponent) -> bool:
        """Perform specific health check for component."""
        # Mock health checks - in production, implement actual checks
        if component.component_type == ComponentType.CACHE:
            # Check cache performance
            cache_stats = cache_manager.get_cache_performance_report()
            return cache_stats['performance_metrics']['overall_hit_rate'] > 0.5
        
        elif component.component_type == ComponentType.ANALYTICS:
            # Check analytics engine
            return True  # Mock
        
        elif component.component_type == ComponentType.MONITORING:
            # Check monitoring systems
            return True  # Mock
        
        else:
            # Default health check
            return component.status != SystemStatus.ERROR
    
    async def _metrics_collection_loop(self):
        """Background metrics collection loop."""
        while self._status in [SystemStatus.RUNNING, SystemStatus.DEGRADED]:
            try:
                await asyncio.sleep(60)  # Collect every minute
                
                await self._collect_system_metrics()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
    
    async def _collect_system_metrics(self):
        """Collect system-wide metrics."""
        # Update component counts
        self.metrics.active_components = len(self.components)
        self.metrics.healthy_components = len([c for c in self.components.values() if c.is_healthy])
        
        # Collect cache metrics
        cache_report = cache_manager.get_cache_performance_report()
        self.metrics.cache_hit_rate = cache_report['performance_metrics']['overall_hit_rate']
        
        # Collect system load (mock)
        import psutil
        self.metrics.system_load = psutil.cpu_percent() / 100.0
        self.metrics.memory_usage_mb = psutil.virtual_memory().used / (1024 * 1024)
        
        self.metrics.timestamp = datetime.now()
    
    async def _update_system_metrics(self):
        """Update system metrics."""
        await self._collect_system_metrics()
        
        # Update system status based on component health
        healthy_rate = self.metrics.healthy_components / self.metrics.active_components
        
        if healthy_rate >= 0.9:
            self._status = SystemStatus.RUNNING
        elif healthy_rate >= 0.7:
            self._status = SystemStatus.DEGRADED
        else:
            self._status = SystemStatus.ERROR
    
    async def shutdown(self):
        """Shutdown the system gracefully."""
        self._status = SystemStatus.SHUTTING_DOWN
        self._shutdown_time = datetime.now()
        
        logger.info("Shutting down RaptorFlow Unified Search System...")
        
        try:
            # Cancel background tasks
            if self._health_check_task:
                self._health_check_task.cancel()
                try:
                    await self._health_check_task
                except asyncio.CancelledError:
                    pass
            
            if self._metrics_collection_task:
                self._metrics_collection_task.cancel()
                try:
                    await self._metrics_collection_task
                except asyncio.CancelledError:
                    pass
            
            # Shutdown components in reverse priority order
            sorted_components = sorted(
                self.components.values(),
                key=lambda c: c.priority
            )
            
            for component in sorted_components:
                await self._shutdown_component(component)
            
            logger.info(f"System shutdown completed in {(datetime.now() - self._shutdown_time).total_seconds():.2f} seconds")
            
        except Exception as e:
            logger.error(f"System shutdown failed: {e}")
            raise
    
    async def _shutdown_component(self, component: SystemComponent):
        """Shutdown individual component."""
        try:
            logger.info(f"Shutting down component: {component.name}")
            
            if component.component_id == 'alert_manager':
                await alert_manager.stop_evaluation()
            elif component.component_id == 'api_gateway':
                await api_gateway.stop()
            elif component.component_id == 'federation_manager':
                await search_federation_manager.stop()
            elif component.component_id == 'distributed_cache':
                await cache_manager.shutdown()
            
            component.status = SystemStatus.SHUTTING_DOWN
            
        except Exception as e:
            logger.error(f"Error shutting down component {component.name}: {e}")
    
    async def search(
        self,
        query: str,
        mode: SearchMode = SearchMode.UNIFIED,
        max_results: int = 10,
        content_types: Optional[List[ContentType]] = None,
        use_federation: bool = False,
        use_cache: bool = True
    ) -> Tuple[List[SearchResult], Dict[str, Any]]:
        """Perform unified search with all system capabilities."""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Update metrics
            self.metrics.total_requests += 1
            
            # Create search query
            search_query = SearchQuery(
                text=query,
                mode=mode,
                max_results=max_results,
                content_types=content_types or [ContentType.TEXT]
            )
            
            # Check cache first
            if use_cache:
                cached_results = await cache_manager.get_cached_search_results(search_query)
                if cached_results:
                    self.metrics.successful_requests += 1
                    response_time = (asyncio.get_event_loop().time() - start_time) * 1000
                    self.metrics.avg_response_time_ms = (
                        (self.metrics.avg_response_time_ms * (self.metrics.total_requests - 1) + response_time) /
                        self.metrics.total_requests
                    )
                    
                    return cached_results, {
                        'source': 'cache',
                        'response_time_ms': response_time,
                        'result_count': len(cached_results)
                    }
            
            # Perform search
            if use_federation:
                results, metadata = await search_federation_manager.search_federated(search_query)
            else:
                results, metadata = await unified_search_engine.search(search_query)
            
            # Cache results
            if use_cache and results:
                await cache_manager.cache_search_results(search_query, results)
            
            # Update metrics
            self.metrics.successful_requests += 1
            response_time = (asyncio.get_event_loop().time() - start_time) * 1000
            self.metrics.avg_response_time_ms = (
                (self.metrics.avg_response_time_ms * (self.metrics.total_requests - 1) + response_time) /
                self.metrics.total_requests
            )
            
            metadata.update({
                'source': 'search_engine',
                'response_time_ms': response_time,
                'result_count': len(results),
                'system_status': self._status.value
            })
            
            return results, metadata
            
        except Exception as e:
            self.metrics.failed_requests += 1
            logger.error(f"Search failed: {e}")
            return [], {'error': str(e)}
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            'system': {
                'status': self._status.value,
                'startup_time': self._startup_time.isoformat() if self._startup_time else None,
                'uptime_seconds': (datetime.now() - self._startup_time).total_seconds() if self._startup_time else 0,
                'total_components': len(self.components),
                'healthy_components': len([c for c in self.components.values() if c.is_healthy])
            },
            'components': {
                comp_id: comp.to_dict()
                for comp_id, comp in self.components.items()
            },
            'metrics': self.metrics.to_dict(),
            'cache_performance': cache_manager.get_cache_performance_report(),
            'federation_stats': search_federation_manager.get_federation_stats(),
            'api_gateway_stats': api_gateway.get_gateway_stats()
        }
    
    def get_component_status(self, component_id: str) -> Optional[Dict[str, Any]]:
        """Get status of specific component."""
        component = self.components.get(component_id)
        return component.to_dict() if component else None
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        health_status = {
            'overall': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'components': {},
            'checks': {}
        }
        
        # Check each component
        unhealthy_components = []
        
        for component_id, component in self.components.items():
            is_healthy = component.is_healthy
            health_status['components'][component_id] = {
                'status': 'healthy' if is_healthy else 'unhealthy',
                'error_count': component.error_count,
                'last_check': component.last_health_check.isoformat() if component.last_health_check else None
            }
            
            if not is_healthy:
                unhealthy_components.append(component_id)
        
        # Determine overall health
        if len(unhealthy_components) == 0:
            health_status['overall'] = 'healthy'
        elif len(unhealthy_components) <= len(self.components) * 0.2:  # Up to 20% unhealthy
            health_status['overall'] = 'degraded'
        else:
            health_status['overall'] = 'unhealthy'
        
        # Additional health checks
        health_status['checks'] = {
            'cache_hit_rate': cache_manager.get_cache_performance_report()['performance_metrics']['overall_hit_rate'],
            'system_load': self.metrics.system_load,
            'memory_usage': self.metrics.memory_usage_mb,
            'active_components': self.metrics.active_components,
            'healthy_components': self.metrics.healthy_components
        }
        
        return health_status


# Global system orchestrator
system_orchestrator = SystemOrchestrator()


class UnifiedSearchSystem:
    """Main interface for the complete unified search system."""
    
    def __init__(self):
        self.orchestrator = system_orchestrator
        self._initialized = False
    
    async def initialize(self, config: Optional[UnifiedSearchConfig] = None):
        """Initialize the complete system."""
        if self._initialized:
            return
        
        await self.orchestrator.initialize(config)
        self._initialized = True
        
        logger.info("RaptorFlow Unified Search System is ready!")
    
    async def shutdown(self):
        """Shutdown the complete system."""
        if not self._initialized:
            return
        
        await self.orchestrator.shutdown()
        self._initialized = False
        
        logger.info("RaptorFlow Unified Search System shutdown complete")
    
    async def search(
        self,
        query: str,
        mode: SearchMode = SearchMode.UNIFIED,
        max_results: int = 10,
        content_types: Optional[List[ContentType]] = None,
        **kwargs
    ) -> Tuple[List[SearchResult], Dict[str, Any]]:
        """Perform search with the complete system."""
        if not self._initialized:
            raise RuntimeError("System not initialized. Call initialize() first.")
        
        return await self.orchestrator.search(
            query=query,
            mode=mode,
            max_results=max_results,
            content_types=content_types,
            **kwargs
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status."""
        return self.orchestrator.get_system_status()
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        return await self.orchestrator.health_check()
    
    def is_healthy(self) -> bool:
        """Check if system is healthy."""
        return self.orchestrator._status == SystemStatus.RUNNING
    
    @property
    def initialized(self) -> bool:
        """Check if system is initialized."""
        return self._initialized


# Global unified search system instance
unified_search_system = UnifiedSearchSystem()


# Convenience functions for external use
async def initialize_search_system(config: Optional[UnifiedSearchConfig] = None):
    """Initialize the unified search system."""
    await unified_search_system.initialize(config)


async def shutdown_search_system():
    """Shutdown the unified search system."""
    await unified_search_system.shutdown()


async def search_unified(
    query: str,
    mode: SearchMode = SearchMode.UNIFIED,
    max_results: int = 10,
    content_types: Optional[List[ContentType]] = None,
    **kwargs
) -> Tuple[List[SearchResult], Dict[str, Any]]:
    """Perform unified search."""
    return await unified_search_system.search(
        query=query,
        mode=mode,
        max_results=max_results,
        content_types=content_types,
        **kwargs
    )


def get_system_status() -> Dict[str, Any]:
    """Get system status."""
    return unified_search_system.get_status()


async def system_health_check() -> Dict[str, Any]:
    """Perform system health check."""
    return await unified_search_system.health_check()


# System information
def get_system_info() -> Dict[str, Any]:
    """Get comprehensive system information."""
    return {
        'name': 'RaptorFlow Unified Search System',
        'version': '1.0.0',
        'description': 'Industrial Grade AI Agent Search Infrastructure',
        'components': 30,
        'capabilities': [
            'Unified Search',
            'Advanced Caching',
            'Real-time Analytics',
            'Machine Learning Integration',
            'Multi-modal Search',
            'Distributed Architecture',
            'Search Federation',
            'API Gateway',
            'Monitoring & Alerting',
            'Quality Assurance',
            'Performance Optimization'
        ],
        'status': unified_search_system.get_status()
    }


# Export main interfaces
__all__ = [
    'UnifiedSearchSystem',
    'unified_search_system',
    'initialize_search_system',
    'shutdown_search_system',
    'search_unified',
    'get_system_status',
    'system_health_check',
    'get_system_info'
]
