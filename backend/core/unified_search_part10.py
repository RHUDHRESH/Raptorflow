"""
Part 10: Main Unified Search Engine Integration
RaptorFlow Unified Search System - Industrial Grade AI Agent Search Infrastructure
===============================================================================
This module integrates all components into the main unified search engine, providing
the primary entry point and orchestrating all subsystems.
"""

import asyncio
import logging
import uuid
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import json

from backend.core.unified_search_part1 import (
    SearchQuery, SearchResult, SearchSession, SearchMode, ContentType, SearchMetrics
)
from backend.core.unified_search_part2 import create_search_provider, SearchProvider
from backend.core.unified_search_part3 import AdvancedCrawler, CrawlPolicy
from backend.core.unified_search_part4 import ResultConsolidator
from backend.core.unified_search_part5 import FaultTolerantExecutor, HealthChecker
from backend.core.unified_search_part6 import DeepResearchAgent, ResearchPlan, ResearchDepth
from backend.core.unified_search_part7 import UnifiedSearchInterface, SimpleSearchRequest, SimpleResearchRequest
from backend.core.unified_search_part8 import (
    metrics_collector, performance_tracker, system_monitor, analytics_engine
)
from backend.core.unified_search_part9 import config_manager, UnifiedSearchConfig

logger = logging.getLogger("raptorflow.unified_search.engine")


@dataclass
class SearchEngineStats:
    """Search engine statistics."""
    total_searches: int = 0
    successful_searches: int = 0
    failed_searches: int = 0
    total_research_requests: int = 0
    successful_research: int = 0
    failed_research: int = 0
    total_crawls: int = 0
    successful_crawls: int = 0
    failed_crawls: int = 0
    uptime_seconds: float = 0.0
    avg_response_time_ms: float = 0.0
    cache_hit_rate: float = 0.0
    last_updated: datetime = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'total_searches': self.total_searches,
            'successful_searches': self.successful_searches,
            'failed_searches': self.failed_searches,
            'total_research_requests': self.total_research_requests,
            'successful_research': self.successful_research,
            'failed_research': self.failed_research,
            'total_crawls': self.total_crawls,
            'successful_crawls': self.successful_crawls,
            'failed_crawls': self.failed_crawls,
            'uptime_seconds': self.uptime_seconds,
            'avg_response_time_ms': self.avg_response_time_ms,
            'cache_hit_rate': self.cache_hit_rate,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }


class UnifiedSearchEngine:
    """Main unified search engine that orchestrates all components."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.config: Optional[UnifiedSearchConfig] = None
        self.is_initialized = False
        self.start_time: Optional[datetime] = None
        
        # Core components
        self.providers: Dict[SearchProvider, Any] = {}
        self.consolidator: Optional[ResultConsolidator] = None
        self.fault_executor: Optional[FaultTolerantExecutor] = None
        self.health_checker: Optional[HealthChecker] = None
        self.crawler: Optional[AdvancedCrawler] = None
        self.deep_research_agent: Optional[DeepResearchAgent] = None
        self.interface: Optional[UnifiedSearchInterface] = None
        
        # Statistics
        self.stats = SearchEngineStats()
        
        # Event callbacks
        self.search_callbacks: List[callable] = []
        self.research_callbacks: List[callable] = []
        self.error_callbacks: List[callable] = []
    
    async def initialize(self, config_path: Optional[str] = None) -> bool:
        """Initialize the search engine."""
        try:
            logger.info("Initializing Unified Search Engine...")
            
            # Load configuration
            await self._load_configuration(config_path)
            
            # Initialize core components
            await self._initialize_providers()
            await self._initialize_consolidator()
            await self._initialize_fault_executor()
            await self._initialize_health_checker()
            await self._initialize_crawler()
            await self._initialize_deep_research_agent()
            await self._initialize_interface()
            
            # Start monitoring
            if self.config.monitoring.enabled:
                await system_monitor.start_monitoring(self.config.monitoring.monitoring_interval_seconds)
            
            # Set start time
            self.start_time = datetime.now()
            self.is_initialized = True
            
            logger.info(f"Unified Search Engine initialized successfully. Version: {self.config.version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Unified Search Engine: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown the search engine gracefully."""
        try:
            logger.info("Shutting down Unified Search Engine...")
            
            # Stop monitoring
            await system_monitor.stop_monitoring()
            
            # Close provider connections
            for provider in self.providers.values():
                if hasattr(provider, 'close'):
                    await provider.close()
            
            # Close crawler
            if self.crawler:
                await self.crawler.__aexit__(None, None, None)
            
            self.is_initialized = False
            logger.info("Unified Search Engine shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    async def _load_configuration(self, config_path: Optional[str] = None):
        """Load and validate configuration."""
        path = config_path or self.config_path
        self.config = await config_manager.load_config(path)
        
        # Add configuration watcher
        config_manager.add_watcher(self._on_config_changed)
        
        logger.info(f"Configuration loaded: {self.config.system_name} v{self.config.version}")
    
    async def _initialize_providers(self):
        """Initialize search providers."""
        self.providers = {}
        
        for provider_name, provider_config in self.config.providers.items():
            if not provider_config.enabled:
                continue
            
            try:
                provider_type = SearchProvider(provider_name)
                provider = create_search_provider(provider_type, {
                    'brave_api_key': provider_config.api_key,
                    'serper_api_key': provider_config.api_key
                })
                
                self.providers[provider_type] = provider
                logger.info(f"Initialized provider: {provider_name}")
                
            except Exception as e:
                logger.error(f"Failed to initialize provider {provider_name}: {e}")
    
    async def _initialize_consolidator(self):
        """Initialize result consolidator."""
        self.consolidator = ResultConsolidator()
        logger.info("Result consolidator initialized")
    
    async def _initialize_fault_executor(self):
        """Initialize fault-tolerant executor."""
        self.fault_executor = FaultTolerantExecutor()
        logger.info("Fault-tolerant executor initialized")
    
    async def _initialize_health_checker(self):
        """Initialize health checker."""
        self.health_checker = HealthChecker()
        logger.info("Health checker initialized")
    
    async def _initialize_crawler(self):
        """Initialize web crawler."""
        if self.config.crawler.enabled:
            policy = CrawlPolicy(
                max_concurrent=self.config.crawler.max_concurrent,
                timeout=self.config.crawler.timeout_seconds,
                max_content_length=self.config.crawler.max_content_length,
                min_content_length=self.config.crawler.min_content_length,
                max_depth=self.config.crawler.max_depth,
                follow_redirects=self.config.crawler.follow_redirects,
                respect_robots_txt=self.config.crawler.respect_robots_txt,
                user_agent=self.config.crawler.user_agent,
                rate_limit_delay=self.config.crawler.rate_limit_delay,
                retry_attempts=self.config.crawler.retry_attempts,
                retry_delay=self.config.crawler.retry_delay,
                enable_js_rendering=self.config.crawler.enable_js_rendering,
                extract_images=self.config.crawler.extract_images,
                extract_links=self.config.crawler.extract_links,
                extract_metadata=self.config.crawler.extract_metadata
            )
            
            self.crawler = AdvancedCrawler(policy)
            logger.info("Web crawler initialized")
        else:
            logger.info("Web crawler disabled")
    
    async def _initialize_deep_research_agent(self):
        """Initialize deep research agent."""
        if self.config.research.enabled:
            self.deep_research_agent = DeepResearchAgent()
            logger.info("Deep research agent initialized")
        else:
            logger.info("Deep research agent disabled")
    
    async def _initialize_interface(self):
        """Initialize AI agent interface."""
        self.interface = UnifiedSearchInterface({
            'brave_api_key': self.config.providers.get('brave', ProviderConfig()).api_key,
            'serper_api_key': self.config.providers.get('serper', ProviderConfig()).api_key
        })
        logger.info("AI agent interface initialized")
    
    async def search(self, query: SearchQuery) -> List[SearchResult]:
        """Perform search using the unified engine."""
        if not self.is_initialized:
            raise RuntimeError("Search engine not initialized")
        
        operation_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        # Start performance tracking
        metrics = performance_tracker.start_operation(
            operation_id=operation_id,
            operation_type="search",
            query=query.text
        )
        
        try:
            # Execute search across providers
            provider_results = {}
            
            for provider_type, provider in self.providers.items():
                try:
                    results = await self.fault_executor.execute_with_fault_tolerance(
                        provider_type, provider.search, query
                    )
                    provider_results[provider_type] = results
                    
                except Exception as e:
                    logger.warning(f"Provider {provider_type.value} failed: {e}")
                    continue
            
            # Consolidate results
            if provider_results:
                consolidated_results = self.consolidator.consolidate_results(provider_results, query)
            else:
                consolidated_results = []
            
            # Update statistics
            self.stats.total_searches += 1
            self.stats.successful_searches += 1
            
            # End performance tracking
            performance_tracker.end_operation(
                operation_id=operation_id,
                success=True,
                results_count=len(consolidated_results)
            )
            
            # Record metrics
            metrics_collector.increment_counter('search_requests_total')
            metrics_collector.record_histogram('search_results_count', len(consolidated_results))
            
            # Notify callbacks
            await self._notify_search_callbacks(query, consolidated_results)
            
            logger.info(f"Search completed: {len(consolidated_results)} results for query: {query.text}")
            return consolidated_results
            
        except Exception as e:
            # Update statistics
            self.stats.total_searches += 1
            self.stats.failed_searches += 1
            
            # End performance tracking
            performance_tracker.end_operation(
                operation_id=operation_id,
                success=False,
                error_message=str(e)
            )
            
            # Record metrics
            metrics_collector.increment_counter('search_errors_total')
            
            # Notify error callbacks
            await self._notify_error_callbacks("search", e, query)
            
            logger.error(f"Search failed: {e}")
            raise
    
    async def research(self, plan: ResearchPlan) -> Any:
        """Perform deep research using the unified engine."""
        if not self.is_initialized:
            raise RuntimeError("Search engine not initialized")
        
        if not self.deep_research_agent:
            raise RuntimeError("Deep research agent not enabled")
        
        operation_id = str(uuid.uuid4())
        
        try:
            # Update statistics
            self.stats.total_research_requests += 1
            
            # Conduct research
            report = await self.deep_research_agent.conduct_research(plan)
            
            # Update statistics
            self.stats.successful_research += 1
            
            # Record metrics
            metrics_collector.increment_counter('research_requests_total')
            metrics_collector.record_histogram('research_findings_count', len(report.key_findings))
            
            # Notify callbacks
            await self._notify_research_callbacks(plan, report)
            
            logger.info(f"Research completed: {len(report.key_findings)} findings for topic: {plan.topic}")
            return report
            
        except Exception as e:
            # Update statistics
            self.stats.failed_research += 1
            
            # Record metrics
            metrics_collector.increment_counter('research_errors_total')
            
            # Notify error callbacks
            await self._notify_error_callbacks("research", e, plan)
            
            logger.error(f"Research failed: {e}")
            raise
    
    async def crawl_urls(self, urls: List[str]) -> List[Any]:
        """Crawl URLs using the unified engine."""
        if not self.is_initialized:
            raise RuntimeError("Search engine not initialized")
        
        if not self.crawler:
            raise RuntimeError("Web crawler not enabled")
        
        operation_id = str(uuid.uuid4())
        
        try:
            # Update statistics
            self.stats.total_crawls += 1
            
            # Crawl URLs
            async with self.crawler as crawler:
                extracted_contents = await crawler.crawl_urls(urls)
            
            # Update statistics
            self.stats.successful_crawls += 1
            
            # Record metrics
            metrics_collector.increment_counter('crawl_requests_total')
            metrics_collector.record_histogram('crawl_content_count', len(extracted_contents))
            
            logger.info(f"Crawl completed: {len(extracted_contents)} contents from {len(urls)} URLs")
            return extracted_contents
            
        except Exception as e:
            # Update statistics
            self.stats.failed_crawls += 1
            
            # Record metrics
            metrics_collector.increment_counter('crawl_errors_total')
            
            logger.error(f"Crawl failed: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        if not self.is_initialized:
            return {
                'status': 'uninitialized',
                'timestamp': datetime.now().isoformat()
            }
        
        health = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'engine': {
                'initialized': self.is_initialized,
                'uptime_seconds': (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
                'version': self.config.version
            },
            'providers': {},
            'system': {},
            'stats': self.stats.to_dict()
        }
        
        # Check providers
        if self.providers:
            provider_health = await self.health_checker.check_all_providers_health(list(self.providers.keys()))
            health['providers'] = provider_health
            
            # Check if any providers are unhealthy
            unhealthy_providers = [
                name for name, info in provider_health.items()
                if info.get('status') == 'unhealthy'
            ]
            
            if unhealthy_providers:
                health['status'] = 'degraded'
                health['unhealthy_providers'] = unhealthy_providers
        
        # Get system health
        system_health = system_monitor.get_system_health()
        health['system'] = system_health
        
        # Overall status determination
        if system_health['status'] == 'critical':
            health['status'] = 'critical'
        elif system_health['status'] == 'degraded':
            health['status'] = 'degraded'
        
        return health
    
    def get_stats(self) -> SearchEngineStats:
        """Get current engine statistics."""
        # Update uptime
        if self.start_time:
            self.stats.uptime_seconds = (datetime.now() - self.start_time).total_seconds()
        
        # Update cache hit rate
        cache_stats = metrics_collector.get_metrics_summary()
        cache_metrics = cache_stats.get('counters', {})
        cache_hits = cache_metrics.get('cache_hits', 0)
        total_requests = cache_metrics.get('search_requests_total', 0)
        
        if total_requests > 0:
            self.stats.cache_hit_rate = cache_hits / total_requests
        
        # Update average response time
        operation_stats = performance_tracker.get_operation_stats()
        self.stats.avg_response_time_ms = operation_stats.get('avg_duration_ms', 0)
        
        # Update timestamp
        self.stats.last_updated = datetime.now()
        
        return self.stats
    
    def get_interface(self) -> UnifiedSearchInterface:
        """Get AI agent interface."""
        if not self.interface:
            raise RuntimeError("Interface not initialized")
        return self.interface
    
    def add_search_callback(self, callback: callable):
        """Add search completion callback."""
        self.search_callbacks.append(callback)
    
    def add_research_callback(self, callback: callable):
        """Add research completion callback."""
        self.research_callbacks.append(callback)
    
    def add_error_callback(self, callback: callable):
        """Add error callback."""
        self.error_callbacks.append(callback)
    
    async def _notify_search_callbacks(self, query: SearchQuery, results: List[SearchResult]):
        """Notify search callbacks."""
        for callback in self.search_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(query, results)
                else:
                    callback(query, results)
            except Exception as e:
                logger.error(f"Search callback failed: {e}")
    
    async def _notify_research_callbacks(self, plan: ResearchPlan, report: Any):
        """Notify research callbacks."""
        for callback in self.research_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(plan, report)
                else:
                    callback(plan, report)
            except Exception as e:
                logger.error(f"Research callback failed: {e}")
    
    async def _notify_error_callbacks(self, operation: str, error: Exception, context: Any):
        """Notify error callbacks."""
        for callback in self.error_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(operation, error, context)
                else:
                    callback(operation, error, context)
            except Exception as e:
                logger.error(f"Error callback failed: {e}")
    
    async def _on_config_changed(self, new_config: UnifiedSearchConfig):
        """Handle configuration changes."""
        logger.info("Configuration changed, reinitializing components...")
        
        # Reinitialize affected components
        await self._initialize_providers()
        
        if self.config.crawler.enabled != new_config.crawler.enabled:
            await self._initialize_crawler()
        
        if self.config.research.enabled != new_config.research.enabled:
            await self._initialize_deep_research_agent()
        
        # Update monitoring
        if self.config.monitoring.enabled != new_config.monitoring.enabled:
            if new_config.monitoring.enabled:
                await system_monitor.start_monitoring(new_config.monitoring.monitoring_interval_seconds)
            else:
                await system_monitor.stop_monitoring()
        
        self.config = new_config
        logger.info("Configuration update completed")


# Global search engine instance
unified_search_engine = UnifiedSearchEngine()


# Convenience functions for direct usage
async def initialize_search_engine(config_path: Optional[str] = None) -> bool:
    """Initialize the global search engine."""
    return await unified_search_engine.initialize(config_path)


async def shutdown_search_engine():
    """Shutdown the global search engine."""
    await unified_search_engine.shutdown()


async def search(query: Union[str, SearchQuery], mode: str = "standard", max_results: int = 10) -> List[SearchResult]:
    """Simple search function."""
    if isinstance(query, str):
        search_query = SearchQuery(
            text=query,
            mode=SearchMode(mode.lower()) if mode.lower() in [m.value for m in SearchMode] else SearchMode.STANDARD,
            max_results=max_results
        )
    else:
        search_query = query
    
    return await unified_search_engine.search(search_query)


async def research(topic: str, question: str, depth: str = "moderate") -> Any:
    """Simple research function."""
    from backend.core.unified_search_part6 import ResearchPlan, ResearchDepth
    
    plan = ResearchPlan(
        topic=topic,
        research_question=question,
        depth=ResearchDepth(depth.lower()) if depth.lower() in [d.value for d in ResearchDepth] else ResearchDepth.MODERATE,
        phases=["planning", "discovery", "extraction", "verification", "synthesis"],
        max_sources=20,
        time_limit_minutes=30,
        content_types=[ContentType.WEB],
        quality_threshold=0.6,
        verification_required=True
    )
    
    return await unified_search_engine.research(plan)


async def get_search_engine_health() -> Dict[str, Any]:
    """Get search engine health status."""
    return await unified_search_engine.health_check()


def get_search_engine_stats() -> SearchEngineStats:
    """Get search engine statistics."""
    return unified_search_engine.get_stats()


def get_search_interface() -> UnifiedSearchInterface:
    """Get AI agent interface."""
    return unified_search_engine.get_interface()


# Example usage
"""
# Initialize the search engine
await initialize_search_engine("config/unified_search.json")

# Perform searches
results = await search("artificial intelligence trends", mode="deep", max_results=20)

# Perform research
report = await research("renewable energy", "What are the latest developments in solar power?")

# Get health status
health = await get_search_engine_health()

# Get statistics
stats = get_search_engine_stats()

# Get AI agent interface
interface = get_search_interface()
simple_results = await interface.quick_search("machine learning")

# Shutdown
await shutdown_search_engine()
"""
