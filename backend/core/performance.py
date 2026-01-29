"""
Agent performance optimization system.
Provides performance monitoring, optimization strategies, and execution improvements.
"""

import asyncio
import gc
import hashlib
import json
import logging
import statistics
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

import psutil

logger = logging.getLogger(__name__)


class OptimizationLevel(Enum):
    """Performance optimization levels."""

    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    MAXIMUM = "maximum"


@dataclass
class PerformanceMetrics:
    """Performance metrics for agent execution."""

    agent_name: str
    execution_time: float
    memory_usage_mb: float
    cpu_usage_percent: float
    tokens_used: int
    cache_hits: int
    cache_misses: int
    tool_calls: int
    skill_calls: int
    error_count: int
    timestamp: datetime
    optimization_level: OptimizationLevel

    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0

    @property
    def tokens_per_second(self) -> float:
        """Calculate tokens per second."""
        return (
            self.tokens_used / self.execution_time if self.execution_time > 0 else 0.0
        )

    @property
    def efficiency_score(self) -> float:
        """Calculate overall efficiency score."""
        # Weighted score based on multiple factors
        time_score = max(0, 1 - (self.execution_time / 10.0))  # 10s = 0 score
        cache_score = self.cache_hit_rate
        error_score = max(0, 1 - (self.error_count / 10.0))  # 10 errors = 0 score

        return time_score * 0.4 + cache_score * 0.3 + error_score * 0.3


@dataclass
class OptimizationConfig:
    """Configuration for performance optimization."""

    enable_caching: bool = True
    enable_connection_pooling: bool = True
    enable_batch_processing: bool = True
    enable_async_execution: bool = True
    enable_memory_optimization: bool = True
    enable_cpu_optimization: bool = True

    # Performance thresholds
    max_execution_time: float = 30.0  # seconds
    max_memory_usage_mb: float = 512.0  # MB
    max_cpu_usage_percent: float = 80.0  # %
    max_concurrent_agents: int = 10

    # Optimization parameters
    cache_ttl: int = 3600  # seconds
    batch_size: int = 5
    gc_threshold: int = 100  # executions
    memory_cleanup_interval: int = 300  # seconds

    # Adaptive optimization
    enable_adaptive_optimization: bool = True
    performance_history_size: int = 1000
    optimization_adjustment_threshold: float = 0.1


class PerformanceOptimizer:
    """Performance optimization system for agent execution."""

    def __init__(self, config: Optional[OptimizationConfig] = None):
        self.config = config or OptimizationConfig()
        self.metrics_history: List[PerformanceMetrics] = []
        self.optimization_level = OptimizationLevel.BALANCED
        self.execution_count = 0
        self.last_gc_time = time.time()
        self.last_memory_cleanup = time.time()

        # Performance monitoring
        self._monitoring_enabled = True
        self._current_executions: Dict[str, Dict[str, Any]] = {}
        self._performance_lock = threading.Lock()

        # Optimization strategies
        self._optimization_strategies = {
            OptimizationLevel.CONSERVATIVE: self._conservative_optimization,
            OptimizationLevel.BALANCED: self._balanced_optimization,
            OptimizationLevel.AGGRESSIVE: self._aggressive_optimization,
            OptimizationLevel.MAXIMUM: self._maximum_optimization,
        }

        # Start background tasks
        self._start_background_tasks()

    def _start_background_tasks(self):
        """Start background optimization tasks."""
        if self.config.enable_memory_optimization:
            asyncio.create_task(self._memory_cleanup_loop())

        if self.config.enable_adaptive_optimization:
            asyncio.create_task(self._adaptive_optimization_loop())

    async def optimize_agent_execution(
        self, agent_name: str, execution_func: Callable, *args, **kwargs
    ) -> Any:
        """Optimize and execute agent function."""
        execution_start = time.time()
        process = psutil.Process()

        # Record initial metrics
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        initial_cpu = process.cpu_percent()

        try:
            # Apply optimization strategy
            optimization_func = self._optimization_strategies[self.optimization_level]

            # Execute with optimization
            if self.config.enable_async_execution and asyncio.iscoroutinefunction(
                execution_func
            ):
                result = await optimization_func(
                    agent_name, execution_func, *args, **kwargs
                )
            else:
                result = optimization_func(agent_name, execution_func, *args, **kwargs)

            # Record final metrics
            execution_time = time.time() - execution_start
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            final_cpu = process.cpu_percent()

            # Create performance metrics
            metrics = PerformanceMetrics(
                agent_name=agent_name,
                execution_time=execution_time,
                memory_usage_mb=final_memory - initial_memory,
                cpu_usage_percent=final_cpu - initial_cpu,
                tokens_used=self._extract_token_usage(result),
                cache_hits=self._get_cache_hits(agent_name),
                cache_misses=self._get_cache_misses(agent_name),
                tool_calls=self._count_tool_calls(result),
                skill_calls=self._count_skill_calls(result),
                error_count=self._count_errors(result),
                timestamp=datetime.now(),
                optimization_level=self.optimization_level,
            )

            # Store metrics
            self._store_metrics(metrics)

            # Trigger optimizations if needed
            await self._trigger_optimizations(metrics)

            return result

        except Exception as e:
            # Record error metrics
            execution_time = time.time() - execution_start
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            final_cpu = process.cpu_percent()

            error_metrics = PerformanceMetrics(
                agent_name=agent_name,
                execution_time=execution_time,
                memory_usage_mb=final_memory - initial_memory,
                cpu_usage_percent=final_cpu - initial_cpu,
                tokens_used=0,
                cache_hits=0,
                cache_misses=0,
                tool_calls=0,
                skill_calls=0,
                error_count=1,
                timestamp=datetime.now(),
                optimization_level=self.optimization_level,
            )

            self._store_metrics(error_metrics)
            raise

    def _conservative_optimization(
        self, agent_name: str, func: Callable, *args, **kwargs
    ):
        """Conservative optimization strategy."""
        # Basic optimization with minimal risk
        if self.config.enable_caching:
            # Check cache first
            cached_result = self._check_cache(agent_name, args, kwargs)
            if cached_result is not None:
                return cached_result

        # Execute function
        result = func(*args, **kwargs)

        # Cache result if enabled
        if self.config.enable_caching and self._should_cache_result(result):
            self._cache_result(agent_name, args, kwargs, result)

        return result

    def _balanced_optimization(self, agent_name: str, func: Callable, *args, **kwargs):
        """Balanced optimization strategy."""
        # Check cache
        if self.config.enable_caching:
            cached_result = self._check_cache(agent_name, args, kwargs)
            if cached_result is not None:
                return cached_result

        # Pre-allocate resources if needed
        if self.config.enable_memory_optimization:
            self._preallocate_resources(agent_name)

        # Execute with monitoring
        with self._monitor_execution(agent_name):
            result = func(*args, **kwargs)

        # Post-process result
        if self.config.enable_caching and self._should_cache_result(result):
            self._cache_result(agent_name, args, kwargs, result)

        return result

    def _aggressive_optimization(
        self, agent_name: str, func: Callable, *args, **kwargs
    ):
        """Aggressive optimization strategy."""
        # Aggressive caching
        if self.config.enable_caching:
            cached_result = self._check_cache(agent_name, args, kwargs)
            if cached_result is not None:
                return cached_result

        # Batch processing if enabled
        if self.config.enable_batch_processing and self._can_batch_process(
            args, kwargs
        ):
            return self._batch_execute(agent_name, func, *args, **kwargs)

        # Parallel execution
        if self.config.enable_async_execution and self._can_parallel_execute(func):
            return self._parallel_execute(agent_name, func, *args, **kwargs)

        # Optimized execution
        with self._monitor_execution(agent_name):
            result = func(*args, **kwargs)

        # Aggressive caching
        if self.config.enable_caching:
            self._cache_result(
                agent_name, args, kwargs, result, ttl=self.config.cache_ttl * 2
            )

        return result

    def _maximum_optimization(self, agent_name: str, func: Callable, *args, **kwargs):
        """Maximum optimization strategy."""
        # Maximum caching
        if self.config.enable_caching:
            cached_result = self._check_cache(agent_name, args, kwargs)
            if cached_result is not None:
                return cached_result

        # Pre-optimization
        self._preoptimize_execution(agent_name, func, args, kwargs)

        # Maximum parallel execution
        if self.config.enable_async_execution:
            return self._max_parallel_execute(agent_name, func, *args, **kwargs)

        # Execute with maximum monitoring
        with self._monitor_execution(agent_name):
            result = func(*args, **kwargs)

        # Post-optimization
        self._postoptimize_result(agent_name, result)

        # Maximum caching
        if self.config.enable_caching:
            self._cache_result(
                agent_name, args, kwargs, result, ttl=self.config.cache_ttl * 3
            )

        return result

    def _monitor_execution(self, agent_name: str):
        """Context manager for monitoring execution."""
        return ExecutionMonitor(self, agent_name)

    def _check_cache(self, agent_name: str, args: tuple, kwargs: dict) -> Optional[Any]:
        """Check if result is cached."""
        try:
            from cache import get_cached_response

            # Create cache key from args and kwargs
            cache_key = self._create_cache_key(agent_name, args, kwargs)

            # Try to get cached response
            cached = get_cached_response(agent_name, cache_key)
            return cached
        except Exception as e:
            logger.error(f"Cache check failed: {e}")
            return None

    def _cache_result(
        self,
        agent_name: str,
        args: tuple,
        kwargs: dict,
        result: Any,
        ttl: Optional[int] = None,
    ):
        """Cache execution result."""
        try:
            from cache import cache_agent_response

            cache_key = self._create_cache_key(agent_name, args, kwargs)
            cache_agent_response(
                agent_name, cache_key, result, ttl or self.config.cache_ttl
            )
        except Exception as e:
            logger.error(f"Cache storage failed: {e}")

    def _create_cache_key(self, agent_name: str, args: tuple, kwargs: dict) -> str:
        """Create cache key from arguments."""
        import hashlib
        import json

        # Create normalized key
        key_data = {
            "agent": agent_name,
            "args": str(args),
            "kwargs": {k: str(v) for k, v in kwargs.items()},
        }

        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()

    def _should_cache_result(self, result: Any) -> bool:
        """Determine if result should be cached."""
        # Don't cache errors
        if isinstance(result, dict) and result.get("error"):
            return False

        # Don't cache very large results
        if isinstance(result, str) and len(result) > 10000:
            return False

        return True

    def _preallocate_resources(self, agent_name: str):
        """Pre-allocate resources for better performance."""
        # This could pre-allocate memory, connections, etc.
        pass

    def _can_batch_process(self, args: tuple, kwargs: dict) -> bool:
        """Check if execution can be batched."""
        # Implement batch processing logic
        return False

    def _batch_execute(self, agent_name: str, func: Callable, *args, **kwargs):
        """Execute in batches for better performance."""
        # Implement batch execution
        return func(*args, **kwargs)

    def _can_parallel_execute(self, func: Callable) -> bool:
        """Check if function can be executed in parallel."""
        # Check if function supports async execution
        return asyncio.iscoroutinefunction(func) or hasattr(func, "parallel")

    def _parallel_execute(self, agent_name: str, func: Callable, *args, **kwargs):
        """Execute in parallel for better performance."""
        # Implement parallel execution
        return func(*args, **kwargs)

    def _max_parallel_execute(self, agent_name: str, func: Callable, *args, **kwargs):
        """Execute with maximum parallelization."""
        # Implement maximum parallel execution
        return func(*args, **kwargs)

    def _preoptimize_execution(
        self, agent_name: str, func: Callable, args: tuple, kwargs: dict
    ):
        """Pre-optimize execution."""
        # Implement pre-optimization logic
        pass

    def _postoptimize_result(self, agent_name: str, result: Any):
        """Post-optimize result."""
        # Implement post-optimization logic
        pass

    def _extract_token_usage(self, result: Any) -> int:
        """Extract token usage from result."""
        if isinstance(result, dict):
            return result.get("tokens_used", 0)
        return 0

    def _get_cache_hits(self, agent_name: str) -> int:
        """Get cache hit count for agent."""
        try:
            from cache import get_cache_stats

            stats = get_cache_stats()
            return stats.get("stats", {}).get("hits", 0)
        except:
            return 0

    def _get_cache_misses(self, agent_name: str) -> int:
        """Get cache miss count for agent."""
        try:
            from cache import get_cache_stats

            stats = get_cache_stats()
            return stats.get("stats", {}).get("misses", 0)
        except:
            return 0

    def _count_tool_calls(self, result: Any) -> int:
        """Count tool calls in result."""
        if isinstance(result, dict):
            return result.get("tool_calls", 0)
        return 0

    def _count_skill_calls(self, result: Any) -> int:
        """Count skill calls in result."""
        if isinstance(result, dict):
            return result.get("skill_calls", 0)
        return 0

    def _count_errors(self, result: Any) -> int:
        """Count errors in result."""
        if isinstance(result, dict):
            return 1 if result.get("error") else 0
        return 1 if isinstance(result, Exception) else 0

    def _store_metrics(self, metrics: PerformanceMetrics):
        """Store performance metrics."""
        with self._performance_lock:
            self.metrics_history.append(metrics)

            # Limit history size
            if len(self.metrics_history) > self.config.performance_history_size:
                self.metrics_history = self.metrics_history[
                    -self.config.performance_history_size :
                ]

            self.execution_count += 1

    async def _trigger_optimizations(self, metrics: PerformanceMetrics):
        """Trigger optimizations based on metrics."""
        # Check if garbage collection is needed
        if self.execution_count % self.config.gc_threshold == 0:
            await self._trigger_gc()

        # Check if memory cleanup is needed
        if time.time() - self.last_memory_cleanup > self.config.memory_cleanup_interval:
            await self._memory_cleanup()

        # Adaptive optimization
        if self.config.enable_adaptive_optimization:
            await self._adjust_optimization_level(metrics)

    async def _trigger_gc(self):
        """Trigger garbage collection."""
        try:
            gc.collect()
            self.last_gc_time = time.time()
            logger.debug("Garbage collection triggered")
        except Exception as e:
            logger.error(f"Garbage collection failed: {e}")

    async def _memory_cleanup(self):
        """Trigger memory cleanup."""
        try:
            # Clear old metrics
            cutoff = datetime.now() - timedelta(hours=1)
            with self._performance_lock:
                old_count = len(self.metrics_history)
                self.metrics_history = [
                    m for m in self.metrics_history if m.timestamp >= cutoff
                ]
                cleared = old_count - len(self.metrics_history)

            self.last_memory_cleanup = time.time()
            logger.debug(f"Memory cleanup: cleared {cleared} old metrics")
        except Exception as e:
            logger.error(f"Memory cleanup failed: {e}")

    async def _adjust_optimization_level(self, metrics: PerformanceMetrics):
        """Adjust optimization level based on performance."""
        # Calculate average performance for recent executions
        recent_metrics = [
            m for m in self.metrics_history[-50:] if m.agent_name == metrics.agent_name
        ]

        if len(recent_metrics) < 10:
            return  # Not enough data

        avg_efficiency = sum(m.efficiency_score for m in recent_metrics) / len(
            recent_metrics
        )

        # Adjust optimization level
        if (
            avg_efficiency < 0.3
            and self.optimization_level != OptimizationLevel.MAXIMUM
        ):
            self.optimization_level = OptimizationLevel.MAXIMUM
            logger.info(
                f"Upgraded optimization to {self.optimization_level.value} for {metrics.agent_name}"
            )
        elif (
            avg_efficiency < 0.6
            and self.optimization_level == OptimizationLevel.CONSERVATIVE
        ):
            self.optimization_level = OptimizationLevel.BALANCED
            logger.info(
                f"Upgraded optimization to {self.optimization_level.value} for {metrics.agent_name}"
            )
        elif (
            avg_efficiency > 0.8
            and self.optimization_level == OptimizationLevel.MAXIMUM
        ):
            self.optimization_level = OptimizationLevel.AGGRESSIVE
            logger.info(
                f"Downgraded optimization to {self.optimization_level.value} for {metrics.agent_name}"
            )
        elif (
            avg_efficiency > 0.9
            and self.optimization_level != OptimizationLevel.CONSERVATIVE
        ):
            self.optimization_level = OptimizationLevel.CONSERVATIVE
            logger.info(
                f"Downgraded optimization to {self.optimization_level.value} for {metrics.agent_name}"
            )

    async def _memory_cleanup_loop(self):
        """Background memory cleanup loop."""
        while True:
            try:
                await asyncio.sleep(self.config.memory_cleanup_interval)
                await self._memory_cleanup()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Memory cleanup loop error: {e}")

    async def _adaptive_optimization_loop(self):
        """Background adaptive optimization loop."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                # Analyze performance and adjust optimizations
                await self._analyze_and_adjust()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Adaptive optimization loop error: {e}")

    async def _analyze_and_adjust(self):
        """Analyze performance and adjust optimizations."""
        with self._performance_lock:
            if len(self.metrics_history) < 100:
                return

            # Analyze overall performance
            recent_metrics = self.metrics_history[-100:]
            avg_efficiency = sum(m.efficiency_score for m in recent_metrics) / len(
                recent_metrics
            )

            # Adjust global optimization level
            current_level = self.optimization_level

            if avg_efficiency < 0.4 and current_level != OptimizationLevel.MAXIMUM:
                self.optimization_level = OptimizationLevel.MAXIMUM
                logger.info(
                    f"Global optimization upgraded to {self.optimization_level.value}"
                )
            elif (
                avg_efficiency > 0.85
                and current_level != OptimizationLevel.CONSERVATIVE
            ):
                self.optimization_level = OptimizationLevel.CONSERVATIVE
                logger.info(
                    f"Global optimization downgraded to {self.optimization_level.value}"
                )

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        with self._performance_lock:
            if not self.metrics_history:
                return {"error": "No performance data available"}

            recent_metrics = self.metrics_history[-100:]

            # Calculate statistics
            avg_execution_time = sum(m.execution_time for m in recent_metrics) / len(
                recent_metrics
            )
            avg_memory_usage = sum(m.memory_usage_mb for m in recent_metrics) / len(
                recent_metrics
            )
            avg_cpu_usage = sum(m.cpu_usage_percent for m in recent_metrics) / len(
                recent_metrics
            )
            avg_efficiency = sum(m.efficiency_score for m in recent_metrics) / len(
                recent_metrics
            )
            avg_cache_hit_rate = sum(m.cache_hit_rate for m in recent_metrics) / len(
                recent_metrics
            )

            # Agent-specific stats
            agent_stats = {}
            for metrics in recent_metrics:
                if metrics.agent_name not in agent_stats:
                    agent_stats[metrics.agent_name] = []
                agent_stats[metrics.agent_name].append(metrics)

            agent_performance = {}
            for agent_name, agent_metrics in agent_stats.items():
                if agent_metrics:
                    agent_performance[agent_name] = {
                        "avg_execution_time": sum(
                            m.execution_time for m in agent_metrics
                        )
                        / len(agent_metrics),
                        "avg_efficiency": sum(m.efficiency_score for m in agent_metrics)
                        / len(agent_metrics),
                        "cache_hit_rate": sum(m.cache_hit_rate for m in agent_metrics)
                        / len(agent_metrics),
                        "total_executions": len(agent_metrics),
                    }

            return {
                "total_executions": self.execution_count,
                "optimization_level": self.optimization_level.value,
                "recent_performance": {
                    "avg_execution_time": avg_execution_time,
                    "avg_memory_usage_mb": avg_memory_usage,
                    "avg_cpu_usage_percent": avg_cpu_usage,
                    "avg_efficiency_score": avg_efficiency,
                    "avg_cache_hit_rate": avg_cache_hit_rate,
                },
                "agent_performance": agent_performance,
                "config": {
                    "enable_caching": self.config.enable_caching,
                    "enable_async_execution": self.config.enable_async_execution,
                    "max_execution_time": self.config.max_execution_time,
                    "max_memory_usage_mb": self.config.max_memory_usage_mb,
                },
            }


class ExecutionMonitor:
    """Context manager for monitoring execution."""

    def __init__(self, optimizer: PerformanceOptimizer, agent_name: str):
        self.optimizer = optimizer
        self.agent_name = agent_name
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()

        # Record execution start
        with self.optimizer._performance_lock:
            self.optimizer._current_executions[self.agent_name] = {
                "start_time": self.start_time,
                "status": "running",
            }

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        execution_time = time.time() - self.start_time if self.start_time else 0

        # Record execution end
        with self.optimizer._performance_lock:
            if self.agent_name in self.optimizer._current_executions:
                self.optimizer._current_executions[self.agent_name].update(
                    {
                        "end_time": time.time(),
                        "execution_time": execution_time,
                        "status": "completed" if exc_type is None else "error",
                        "error": str(exc_val) if exc_val else None,
                    }
                )


# Global performance optimizer instance
_performance_optimizer: Optional[PerformanceOptimizer] = None


def get_performance_optimizer() -> PerformanceOptimizer:
    """Get the global performance optimizer instance."""
    global _performance_optimizer
    if _performance_optimizer is None:
        _performance_optimizer = PerformanceOptimizer()
    return _performance_optimizer


async def optimize_agent_execution(
    agent_name: str, execution_func: Callable, *args, **kwargs
) -> Any:
    """Optimize agent execution (convenience function)."""
    optimizer = get_performance_optimizer()
    return await optimizer.optimize_agent_execution(
        agent_name, execution_func, *args, **kwargs
    )


def get_performance_stats() -> Dict[str, Any]:
    """Get performance statistics (convenience function)."""
    optimizer = get_performance_optimizer()
    return optimizer.get_performance_stats()
