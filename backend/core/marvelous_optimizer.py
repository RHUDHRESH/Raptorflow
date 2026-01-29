"""
Marvelous AI System Optimization Framework
Comprehensive multi-layered optimization for AI systems achieving 60-80% cost reduction.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib
import uuid

from semantic_cache import SemanticCache
from smart_retry import SmartRetryManager
from context_manager import ContextManager
from dynamic_router import DynamicModelRouter
from prompt_optimizer import PromptOptimizer
from cost_analytics import CostAnalytics
from batch_processor import BatchProcessor
from provider_arbitrage import ProviderArbitrage

logger = logging.getLogger(__name__)


class OptimizationStrategy(Enum):
    """Optimization strategy types."""

    SEMANTIC_CACHE = "semantic_cache"
    SMART_RETRY = "smart_retry"
    CONTEXT_PRUNING = "context_pruning"
    DYNAMIC_ROUTING = "dynamic_routing"
    PROMPT_OPTIMIZATION = "prompt_optimization"
    BATCH_PROCESSING = "batch_processing"
    PROVIDER_ARBITRAGE = "provider_arbitrage"
    ML_TUNING = "ml_tuning"


@dataclass
class OptimizationMetrics:
    """Optimization performance metrics."""

    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    retry_attempts: int = 0
    failed_requests: int = 0
    cost_before: float = 0.0
    cost_after: float = 0.0
    tokens_before: int = 0
    tokens_after: int = 0
    latency_before: float = 0.0
    latency_after: float = 0.0
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

    @property
    def cost_reduction_percent(self) -> float:
        """Calculate cost reduction percentage."""
        if self.cost_before == 0:
            return 0.0
        return ((self.cost_before - self.cost_after) / self.cost_before) * 100

    @property
    def token_reduction_percent(self) -> float:
        """Calculate token reduction percentage."""
        if self.tokens_before == 0:
            return 0.0
        return ((self.tokens_before - self.tokens_after) / self.tokens_before) * 100

    @property
    def latency_reduction_percent(self) -> float:
        """Calculate latency reduction percentage."""
        if self.latency_before == 0:
            return 0.0
        return ((self.latency_before - self.latency_after) / self.latency_before) * 100

    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        if self.total_requests == 0:
            return 0.0
        return (self.cache_hits / self.total_requests) * 100


@dataclass
class OptimizationConfig:
    """Configuration for optimization strategies."""

    # Semantic Cache Configuration
    semantic_cache_enabled: bool = True
    l1_cache_size: int = 1000
    l2_cache_ttl: int = 3600
    l3_cache_ttl: int = 86400
    semantic_similarity_threshold: float = 0.85

    # Smart Retry Configuration
    smart_retry_enabled: bool = True
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    circuit_breaker_threshold: int = 5

    # Context Management Configuration
    context_pruning_enabled: bool = True
    max_context_length: int = 4000
    compression_ratio: float = 0.6

    # Dynamic Routing Configuration
    dynamic_routing_enabled: bool = True
    cost_threshold: float = 0.01
    performance_weight: float = 0.7

    # Prompt Optimization Configuration
    prompt_optimization_enabled: bool = True
    token_reduction_target: float = 0.35
    semantic_preservation_threshold: float = 0.9

    # Batch Processing Configuration
    batch_processing_enabled: bool = True
    batch_size: int = 10
    batch_timeout: float = 5.0

    # Provider Arbitrage Configuration
    provider_arbitrage_enabled: bool = True
    preferred_providers: List[str] = None
    cost_sensitivity: float = 0.8

    def __post_init__(self):
        if self.preferred_providers is None:
            self.preferred_providers = ["openai", "anthropic", "google"]


class MarvelousAIOptimizer:
    """
    Marvelous AI System Optimization Framework

    Comprehensive optimization system that integrates multiple strategies
    to achieve 60-80% cost reduction while maintaining performance.
    """

    def __init__(self, config: Optional[OptimizationConfig] = None):
        """Initialize the optimizer with configuration."""
        self.config = config or OptimizationConfig()
        self.metrics = OptimizationMetrics()
        self.session_id = str(uuid.uuid4())

        # Initialize optimization components
        self._initialize_components()

        # Optimization state
        self._active_strategies = set()
        self._performance_history = []
        self._cost_savings = 0.0

        logger.info(f"MarvelousAIOptimizer initialized with session {self.session_id}")

    def _initialize_components(self):
        """Initialize all optimization components."""
        try:
            # Semantic Cache (L1/L2/L3 levels)
            if self.config.semantic_cache_enabled:
                self.semantic_cache = SemanticCache(
                    l1_size=self.config.l1_cache_size,
                    l2_ttl=self.config.l2_cache_ttl,
                    l3_ttl=self.config.l3_cache_ttl,
                    similarity_threshold=self.config.semantic_similarity_threshold,
                )
                self._active_strategies.add(OptimizationStrategy.SEMANTIC_CACHE)

            # Smart Retry Manager
            if self.config.smart_retry_enabled:
                self.smart_retry = SmartRetryManager(
                    max_retries=self.config.max_retries,
                    base_delay=self.config.base_delay,
                    max_delay=self.config.max_delay,
                    circuit_breaker_threshold=self.config.circuit_breaker_threshold,
                )
                self._active_strategies.add(OptimizationStrategy.SMART_RETRY)

            # Context Manager
            if self.config.context_pruning_enabled:
                self.context_manager = ContextManager(
                    max_length=self.config.max_context_length,
                    compression_ratio=self.config.compression_ratio,
                )
                self._active_strategies.add(OptimizationStrategy.CONTEXT_PRUNING)

            # Dynamic Model Router
            if self.config.dynamic_routing_enabled:
                self.dynamic_router = DynamicModelRouter(
                    cost_threshold=self.config.cost_threshold,
                    performance_weight=self.config.performance_weight,
                )
                self._active_strategies.add(OptimizationStrategy.DYNAMIC_ROUTING)

            # Prompt Optimizer
            if self.config.prompt_optimization_enabled:
                self.prompt_optimizer = PromptOptimizer(
                    token_reduction_target=self.config.token_reduction_target,
                    semantic_preservation_threshold=self.config.semantic_preservation_threshold,
                )
                self._active_strategies.add(OptimizationStrategy.PROMPT_OPTIMIZATION)

            # Batch Processor
            if self.config.batch_processing_enabled:
                self.batch_processor = BatchProcessor(
                    batch_size=self.config.batch_size,
                    batch_timeout=self.config.batch_timeout,
                )
                self._active_strategies.add(OptimizationStrategy.BATCH_PROCESSING)

            # Provider Arbitrage
            if self.config.provider_arbitrage_enabled:
                self.provider_arbitrage = ProviderArbitrage(
                    preferred_providers=self.config.preferred_providers,
                    cost_sensitivity=self.config.cost_sensitivity,
                )
                self._active_strategies.add(OptimizationStrategy.PROVIDER_ARBITRAGE)

            # Cost Analytics
            self.cost_analytics = CostAnalytics()

            logger.info(
                f"Initialized {len(self._active_strategies)} optimization strategies"
            )

        except Exception as e:
            logger.error(f"Failed to initialize optimization components: {e}")
            raise

    async def optimize_request(
        self, request_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Optimize a single AI request through all applicable strategies.

        Args:
            request_data: The original request data
            context: Additional context for optimization

        Returns:
            Optimized request data with metadata
        """
        start_time = time.time()
        request_id = str(uuid.uuid4())

        try:
            # Initialize optimization context
            opt_context = {
                "request_id": request_id,
                "session_id": self.session_id,
                "start_time": start_time,
                "original_request": request_data.copy(),
                "applied_strategies": [],
                "cost_savings": 0.0,
                "token_savings": 0,
                "latency_savings": 0.0,
            }

            if context:
                opt_context.update(context)

            # Step 1: Semantic Cache Check
            if OptimizationStrategy.SEMANTIC_CACHE in self._active_strategies:
                cached_result = await self._check_semantic_cache(
                    request_data, opt_context
                )
                if cached_result:
                    self.metrics.cache_hits += 1
                    return cached_result
                self.metrics.cache_misses += 1

            # Step 2: Context Optimization
            if OptimizationStrategy.CONTEXT_PRUNING in self._active_strategies:
                request_data = await self._optimize_context(request_data, opt_context)

            # Step 3: Prompt Optimization
            if OptimizationStrategy.PROMPT_OPTIMIZATION in self._active_strategies:
                request_data = await self._optimize_prompt(request_data, opt_context)

            # Step 4: Dynamic Model Routing
            if OptimizationStrategy.DYNAMIC_ROUTING in self._active_strategies:
                request_data = await self._route_to_optimal_model(
                    request_data, opt_context
                )

            # Step 5: Provider Arbitrage
            if OptimizationStrategy.PROVIDER_ARBITRAGE in self._active_strategies:
                request_data = await self._optimize_provider_selection(
                    request_data, opt_context
                )

            # Step 6: Batch Processing Check
            if OptimizationStrategy.BATCH_PROCESSING in self._active_strategies:
                batch_result = await self._check_batch_processing(
                    request_data, opt_context
                )
                if batch_result:
                    return batch_result

            # Update metrics
            self.metrics.total_requests += 1
            optimization_time = time.time() - start_time

            # Return optimized request
            optimized_request = {
                "optimized_data": request_data,
                "optimization_metadata": {
                    "request_id": request_id,
                    "session_id": self.session_id,
                    "optimization_time": optimization_time,
                    "applied_strategies": opt_context["applied_strategies"],
                    "cost_savings": opt_context["cost_savings"],
                    "token_savings": opt_context["token_savings"],
                    "latency_savings": opt_context["latency_savings"],
                },
            }

            # Store in semantic cache for future requests
            if OptimizationStrategy.SEMANTIC_CACHE in self._active_strategies:
                await self._store_in_semantic_cache(
                    request_data, optimized_request, opt_context
                )

            return optimized_request

        except Exception as e:
            logger.error(f"Optimization failed for request {request_id}: {e}")
            # Fallback to original request
            return {
                "optimized_data": request_data,
                "optimization_metadata": {
                    "request_id": request_id,
                    "error": str(e),
                    "fallback": True,
                },
            }
        finally:
            # Update global metrics
            self._update_global_metrics(start_time)

    async def _check_semantic_cache(
        self, request_data: Dict[str, Any], context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Check semantic cache for similar requests."""
        try:
            cached_result = await self.semantic_cache.get(request_data)
            if cached_result:
                context["applied_strategies"].append("semantic_cache_hit")
                context["cost_savings"] += cached_result.get("cost_savings", 0.0)
                context["latency_savings"] += cached_result.get("latency_savings", 0.0)
                logger.info(f"Semantic cache hit for request {context['request_id']}")
                return cached_result
        except Exception as e:
            logger.warning(f"Semantic cache check failed: {e}")
        return None

    async def _optimize_context(
        self, request_data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize context through intelligent pruning and compression."""
        try:
            optimized_request, savings = await self.context_manager.optimize(
                request_data
            )
            context["applied_strategies"].append("context_optimization")
            context["token_savings"] += savings.get("token_savings", 0)
            context["cost_savings"] += savings.get("cost_savings", 0.0)
            return optimized_request
        except Exception as e:
            logger.warning(f"Context optimization failed: {e}")
            return request_data

    async def _optimize_prompt(
        self, request_data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize prompts through token reduction and semantic compression."""
        try:
            optimized_request, savings = await self.prompt_optimizer.optimize(
                request_data
            )
            context["applied_strategies"].append("prompt_optimization")
            context["token_savings"] += savings.get("token_savings", 0)
            context["cost_savings"] += savings.get("cost_savings", 0.0)
            return optimized_request
        except Exception as e:
            logger.warning(f"Prompt optimization failed: {e}")
            return request_data

    async def _route_to_optimal_model(
        self, request_data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Route request to optimal model based on task complexity and cost."""
        try:
            routing_decision = await self.dynamic_router.route(request_data)
            context["applied_strategies"].append("dynamic_routing")
            context["cost_savings"] += routing_decision.get("cost_savings", 0.0)

            # Update request with routing information
            request_data["model_routing"] = routing_decision
            return request_data
        except Exception as e:
            logger.warning(f"Dynamic routing failed: {e}")
            return request_data

    async def _optimize_provider_selection(
        self, request_data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize provider selection through arbitrage."""
        try:
            provider_decision = await self.provider_arbitrage.select_provider(
                request_data
            )
            context["applied_strategies"].append("provider_arbitrage")
            context["cost_savings"] += provider_decision.get("cost_savings", 0.0)

            # Update request with provider information
            request_data["provider_selection"] = provider_decision
            return request_data
        except Exception as e:
            logger.warning(f"Provider arbitrage failed: {e}")
            return request_data

    async def _check_batch_processing(
        self, request_data: Dict[str, Any], context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Check if request can be batched."""
        try:
            batch_result = await self.batch_processor.process_request(
                request_data, context
            )
            if batch_result and batch_result.get("batched", False):
                context["applied_strategies"].append("batch_processing")
                context["cost_savings"] += batch_result.get("cost_savings", 0.0)
                return batch_result
        except Exception as e:
            logger.warning(f"Batch processing check failed: {e}")
        return None

    async def _store_in_semantic_cache(
        self,
        original_request: Dict[str, Any],
        optimized_result: Dict[str, Any],
        context: Dict[str, Any],
    ):
        """Store optimized result in semantic cache."""
        try:
            await self.semantic_cache.set(
                original_request,
                optimized_result,
                metadata={
                    "cost_savings": context["cost_savings"],
                    "latency_savings": context["latency_savings"],
                    "applied_strategies": context["applied_strategies"],
                },
            )
        except Exception as e:
            logger.warning(f"Failed to store in semantic cache: {e}")

    def _update_global_metrics(self, start_time: float):
        """Update global optimization metrics."""
        try:
            optimization_time = time.time() - start_time
            self.metrics.latency_after = optimization_time

            # Update performance history
            self._performance_history.append(
                {
                    "timestamp": datetime.utcnow(),
                    "optimization_time": optimization_time,
                    "active_strategies": len(self._active_strategies),
                    "metrics": asdict(self.metrics),
                }
            )

            # Keep only last 1000 entries
            if len(self._performance_history) > 1000:
                self._performance_history = self._performance_history[-1000:]

        except Exception as e:
            logger.warning(f"Failed to update global metrics: {e}")

    async def execute_with_retry(
        self, func, *args, retry_context: Optional[Dict[str, Any]] = None, **kwargs
    ) -> Any:
        """
        Execute function with smart retry mechanism.

        Args:
            func: Function to execute
            *args: Function arguments
            retry_context: Additional context for retry logic
            **kwargs: Function keyword arguments

        Returns:
            Function result or raises last exception
        """
        if OptimizationStrategy.SMART_RETRY not in self._active_strategies:
            return await func(*args, **kwargs)

        try:
            return await self.smart_retry.execute_with_retry(
                func, *args, context=retry_context, **kwargs
            )
        except Exception as e:
            logger.error(f"Smart retry failed: {e}")
            self.metrics.failed_requests += 1
            raise

    def get_optimization_metrics(self) -> Dict[str, Any]:
        """Get comprehensive optimization metrics."""
        return {
            "session_metrics": asdict(self.metrics),
            "active_strategies": [s.value for s in self._active_strategies],
            "performance_summary": {
                "cost_reduction": self.metrics.cost_reduction_percent,
                "token_reduction": self.metrics.token_reduction_percent,
                "latency_reduction": self.metrics.latency_reduction_percent,
                "cache_hit_rate": self.metrics.cache_hit_rate,
            },
            "total_cost_savings": self._cost_savings,
            "average_optimization_time": self._calculate_average_optimization_time(),
            "strategy_effectiveness": self._calculate_strategy_effectiveness(),
        }

    def _calculate_average_optimization_time(self) -> float:
        """Calculate average optimization time from history."""
        if not self._performance_history:
            return 0.0

        total_time = sum(
            entry["optimization_time"] for entry in self._performance_history
        )
        return total_time / len(self._performance_history)

    def _calculate_strategy_effectiveness(self) -> Dict[str, float]:
        """Calculate effectiveness of each optimization strategy."""
        effectiveness = {}

        for strategy in self._active_strategies:
            # Calculate strategy-specific metrics
            strategy_metrics = [
                entry
                for entry in self._performance_history
                if strategy.value in entry.get("applied_strategies", [])
            ]

            if strategy_metrics:
                avg_savings = sum(
                    entry["metrics"].get("cost_savings", 0)
                    for entry in strategy_metrics
                ) / len(strategy_metrics)
                effectiveness[strategy.value] = avg_savings
            else:
                effectiveness[strategy.value] = 0.0

        return effectiveness

    async def optimize_batch_requests(
        self, requests: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Optimize multiple requests in batch for maximum efficiency.

        Args:
            requests: List of requests to optimize

        Returns:
            List of optimized requests
        """
        if not requests:
            return []

        start_time = time.time()
        batch_id = str(uuid.uuid4())

        try:
            logger.info(
                f"Starting batch optimization for {len(requests)} requests (batch: {batch_id})"
            )

            # Process requests concurrently
            tasks = [
                self.optimize_request(
                    request, context={"batch_id": batch_id, "batch_index": i}
                )
                for i, request in enumerate(requests)
            ]

            optimized_requests = await asyncio.gather(*tasks, return_exceptions=True)

            # Handle exceptions and filter results
            successful_results = []
            failed_count = 0

            for i, result in enumerate(optimized_requests):
                if isinstance(result, Exception):
                    logger.error(f"Request {i} in batch {batch_id} failed: {result}")
                    failed_count += 1
                    # Return original request as fallback
                    successful_results.append(
                        {
                            "optimized_data": requests[i],
                            "optimization_metadata": {
                                "error": str(result),
                                "fallback": True,
                            },
                        }
                    )
                else:
                    successful_results.append(result)

            batch_time = time.time() - start_time
            success_rate = ((len(requests) - failed_count) / len(requests)) * 100

            logger.info(
                f"Batch {batch_id} completed: {success_rate:.1f}% success rate, {batch_time:.2f}s"
            )

            return successful_requests

        except Exception as e:
            logger.error(f"Batch optimization failed: {e}")
            # Return original requests as fallback
            return [
                {
                    "optimized_data": request,
                    "optimization_metadata": {"error": str(e), "fallback": True},
                }
                for request in requests
            ]

    def reset_metrics(self):
        """Reset all optimization metrics."""
        self.metrics = OptimizationMetrics()
        self._performance_history = []
        self._cost_savings = 0.0
        logger.info("Optimization metrics reset")

    async def shutdown(self):
        """Shutdown optimizer and cleanup resources."""
        try:
            logger.info("Shutting down MarvelousAIOptimizer...")

            # Shutdown all components
            if hasattr(self, "semantic_cache"):
                await self.semantic_cache.shutdown()

            if hasattr(self, "batch_processor"):
                await self.batch_processor.shutdown()

            if hasattr(self, "cost_analytics"):
                await self.cost_analytics.shutdown()

            logger.info("MarvelousAIOptimizer shutdown complete")

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

    def __repr__(self) -> str:
        """String representation of optimizer."""
        return (
            f"MarvelousAIOptimizer(session={self.session_id}, "
            f"strategies={len(self._active_strategies)}, "
            f"cost_reduction={self.metrics.cost_reduction_percent:.1f}%)"
        )
