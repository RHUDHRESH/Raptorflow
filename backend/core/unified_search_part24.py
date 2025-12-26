"""
Part 24: Performance Optimization and Tuning
RaptorFlow Unified Search System - Industrial Grade AI Agent Search Infrastructure
===============================================================================
This module implements advanced performance optimization, auto-tuning, and
resource management for maximum search system efficiency.
"""

import asyncio
import json
import logging
import statistics
import threading
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import psutil

from core.unified_search_part1 import SearchMode, SearchQuery, SearchResult
from core.unified_search_part2 import SearchProvider

logger = logging.getLogger("raptorflow.unified_search.optimization")


class OptimizationStrategy(Enum):
    """Performance optimization strategies."""

    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    ADAPTIVE = "adaptive"
    LATENCY_FOCUSED = "latency_focused"
    THROUGHPUT_FOCUSED = "throughput_focused"
    QUALITY_FOCUSED = "quality_focused"


class ResourceType(Enum):
    """Types of system resources."""

    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    CACHE = "cache"
    CONNECTIONS = "connections"


@dataclass
class ResourceMetrics:
    """System resource metrics."""

    resource_type: ResourceType
    current_usage: float
    max_capacity: float
    utilization_percentage: float
    trend: str  # increasing, decreasing, stable
    alert_threshold: float = 0.8
    critical_threshold: float = 0.9
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "resource_type": self.resource_type.value,
            "current_usage": self.current_usage,
            "max_capacity": self.max_capacity,
            "utilization_percentage": self.utilization_percentage,
            "trend": self.trend,
            "alert_threshold": self.alert_threshold,
            "critical_threshold": self.critical_threshold,
            "timestamp": self.timestamp.isoformat(),
        }

    @property
    def is_alert(self) -> bool:
        """Check if resource usage is at alert level."""
        return self.utilization_percentage >= self.alert_threshold

    @property
    def is_critical(self) -> bool:
        """Check if resource usage is at critical level."""
        return self.utilization_percentage >= self.critical_threshold


@dataclass
class OptimizationAction:
    """Optimization action."""

    action_id: str
    name: str
    description: str
    resource_type: ResourceType
    impact_score: float
    confidence: float
    parameters: Dict[str, Any]
    estimated_improvement: float
    execution_time_ms: float
    rollback_possible: bool = True
    applied_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "action_id": self.action_id,
            "name": self.name,
            "description": self.description,
            "resource_type": self.resource_type.value,
            "impact_score": self.impact_score,
            "confidence": self.confidence,
            "parameters": self.parameters,
            "estimated_improvement": self.estimated_improvement,
            "execution_time_ms": self.execution_time_ms,
            "rollback_possible": self.rollback_possible,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "result": self.result,
        }


@dataclass
class PerformanceProfile:
    """Performance configuration profile."""

    profile_id: str
    name: str
    strategy: OptimizationStrategy
    target_metrics: Dict[str, float]
    resource_limits: Dict[ResourceType, float]
    optimization_settings: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    active: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "profile_id": self.profile_id,
            "name": self.name,
            "strategy": self.strategy.value,
            "target_metrics": self.target_metrics,
            "resource_limits": {
                rt.value: limit for rt, limit in self.resource_limits.items()
            },
            "optimization_settings": self.optimization_settings,
            "created_at": self.created_at.isoformat(),
            "active": self.active,
        }


class ResourceMonitor:
    """Monitors system resources and performance metrics."""

    def __init__(self):
        self.monitoring_enabled = False
        self.monitoring_interval = 5.0  # seconds
        self.resource_history: Dict[ResourceType, deque] = defaultdict(
            lambda: deque(maxlen=100)
        )
        self.current_metrics: Dict[ResourceType, ResourceMetrics] = {}
        self.alert_thresholds = {
            ResourceType.CPU: 0.8,
            ResourceType.MEMORY: 0.85,
            ResourceType.DISK: 0.9,
            ResourceType.NETWORK: 0.8,
            ResourceType.CACHE: 0.9,
            ResourceType.CONNECTIONS: 0.8,
        }
        self._monitoring_task: Optional[asyncio.Task] = None
        self._lock = threading.Lock()

    async def start_monitoring(self):
        """Start resource monitoring."""
        self.monitoring_enabled = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Resource monitoring started")

    async def stop_monitoring(self):
        """Stop resource monitoring."""
        self.monitoring_enabled = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("Resource monitoring stopped")

    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring_enabled:
            try:
                await self._collect_metrics()
                await asyncio.sleep(self.monitoring_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Resource monitoring error: {e}")
                await asyncio.sleep(10)  # Wait before retry

    async def _collect_metrics(self):
        """Collect current resource metrics."""
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_metrics = ResourceMetrics(
            resource_type=ResourceType.CPU,
            current_usage=cpu_percent,
            max_capacity=100.0,
            utilization_percentage=cpu_percent,
            trend=self._calculate_trend(ResourceType.CPU, cpu_percent),
            alert_threshold=self.alert_thresholds[ResourceType.CPU],
        )

        # Memory metrics
        memory = psutil.virtual_memory()
        memory_metrics = ResourceMetrics(
            resource_type=ResourceType.MEMORY,
            current_usage=memory.used,
            max_capacity=memory.total,
            utilization_percentage=memory.percent,
            trend=self._calculate_trend(ResourceType.MEMORY, memory.percent),
            alert_threshold=self.alert_thresholds[ResourceType.MEMORY],
        )

        # Disk metrics
        disk = psutil.disk_usage("/")
        disk_metrics = ResourceMetrics(
            resource_type=ResourceType.DISK,
            current_usage=disk.used,
            max_capacity=disk.total,
            utilization_percentage=(disk.used / disk.total) * 100,
            trend=self._calculate_trend(
                ResourceType.DISK, (disk.used / disk.total) * 100
            ),
            alert_threshold=self.alert_thresholds[ResourceType.DISK],
        )

        # Network metrics (simplified)
        network = psutil.net_io_counters()
        network_metrics = ResourceMetrics(
            resource_type=ResourceType.NETWORK,
            current_usage=network.bytes_sent + network.bytes_recv,
            max_capacity=1_000_000_000,  # 1GB baseline
            utilization_percentage=0.1,  # Simplified
            trend="stable",
            alert_threshold=self.alert_thresholds[ResourceType.NETWORK],
        )

        # Update current metrics
        with self._lock:
            self.current_metrics = {
                ResourceType.CPU: cpu_metrics,
                ResourceType.MEMORY: memory_metrics,
                ResourceType.DISK: disk_metrics,
                ResourceType.NETWORK: network_metrics,
            }

            # Store in history
            for resource_type, metrics in self.current_metrics.items():
                self.resource_history[resource_type].append(metrics)

    def _calculate_trend(
        self, resource_type: ResourceType, current_value: float
    ) -> str:
        """Calculate resource usage trend."""
        history = self.resource_history[resource_type]
        if len(history) < 3:
            return "stable"

        recent_values = [m.utilization_percentage for m in list(history)[-3:]]
        recent_values.append(current_value)

        # Simple trend calculation
        if len(recent_values) >= 3:
            if all(
                recent_values[i] <= recent_values[i + 1]
                for i in range(len(recent_values) - 1)
            ):
                return "increasing"
            elif all(
                recent_values[i] >= recent_values[i + 1]
                for i in range(len(recent_values) - 1)
            ):
                return "decreasing"

        return "stable"

    def get_current_metrics(self) -> Dict[ResourceType, ResourceMetrics]:
        """Get current resource metrics."""
        with self._lock:
            return self.current_metrics.copy()

    def get_resource_alerts(self) -> List[ResourceMetrics]:
        """Get resources at alert or critical levels."""
        with self._lock:
            return [
                metrics
                for metrics in self.current_metrics.values()
                if metrics.is_alert or metrics.is_critical
            ]

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        with self._lock:
            if not self.current_metrics:
                return {"status": "no_data"}

            summary = {
                "timestamp": datetime.now().isoformat(),
                "overall_health": "good",
                "alerts": [],
                "critical_alerts": [],
            }

            for resource_type, metrics in self.current_metrics.items():
                resource_data = metrics.to_dict()
                summary[resource_type.value] = resource_data

                if metrics.is_critical:
                    summary["critical_alerts"].append(resource_data)
                    summary["overall_health"] = "critical"
                elif metrics.is_alert:
                    summary["alerts"].append(resource_data)
                    if summary["overall_health"] == "good":
                        summary["overall_health"] = "warning"

            return summary


class OptimizationEngine:
    """Performance optimization engine."""

    def __init__(self, resource_monitor: ResourceMonitor):
        self.resource_monitor = resource_monitor
        self.active_profile: Optional[PerformanceProfile] = None
        self.optimization_history: deque = deque(maxlen=1000)
        self.applied_actions: Dict[str, OptimizationAction] = {}
        self.optimization_rules = self._create_optimization_rules()
        self._optimization_task: Optional[asyncio.Task] = None

    def _create_optimization_rules(self) -> List[Dict[str, Any]]:
        """Create optimization rules."""
        return [
            {
                "name": "increase_cache_size",
                "description": "Increase cache size when memory is available",
                "resource_type": ResourceType.MEMORY,
                "condition": lambda metrics: metrics.utilization_percentage < 0.7,
                "action": self._increase_cache_size,
                "impact": 0.6,
                "confidence": 0.8,
            },
            {
                "name": "reduce_cache_size",
                "description": "Reduce cache size when memory is constrained",
                "resource_type": ResourceType.MEMORY,
                "condition": lambda metrics: metrics.utilization_percentage > 0.85,
                "action": self._reduce_cache_size,
                "impact": 0.5,
                "confidence": 0.9,
            },
            {
                "name": "adjust_concurrency",
                "description": "Adjust concurrency based on CPU usage",
                "resource_type": ResourceType.CPU,
                "condition": lambda metrics: metrics.utilization_percentage > 0.8,
                "action": self._reduce_concurrency,
                "impact": 0.7,
                "confidence": 0.8,
            },
            {
                "name": "enable_aggressive_caching",
                "description": "Enable aggressive caching during low load",
                "resource_type": ResourceType.CPU,
                "condition": lambda metrics: metrics.utilization_percentage < 0.5,
                "action": self._enable_aggressive_caching,
                "impact": 0.4,
                "confidence": 0.7,
            },
            {
                "name": "optimize_network_connections",
                "description": "Optimize network connection pool",
                "resource_type": ResourceType.NETWORK,
                "condition": lambda metrics: metrics.utilization_percentage > 0.8,
                "action": self._optimize_network_connections,
                "impact": 0.6,
                "confidence": 0.7,
            },
        ]

    async def start_optimization(self):
        """Start automatic optimization."""
        self._optimization_task = asyncio.create_task(self._optimization_loop())
        logger.info("Performance optimization started")

    async def stop_optimization(self):
        """Stop automatic optimization."""
        if self._optimization_task:
            self._optimization_task.cancel()
            try:
                await self._optimization_task
            except asyncio.CancelledError:
                pass
        logger.info("Performance optimization stopped")

    async def _optimization_loop(self):
        """Main optimization loop."""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds

                # Get current metrics
                current_metrics = self.resource_monitor.get_current_metrics()

                if not current_metrics:
                    continue

                # Find optimization opportunities
                actions = await self._identify_optimization_actions(current_metrics)

                # Apply optimizations
                for action in actions:
                    await self._apply_optimization_action(action)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Optimization loop error: {e}")
                await asyncio.sleep(60)  # Wait before retry

    async def _identify_optimization_actions(
        self, current_metrics: Dict[ResourceType, ResourceMetrics]
    ) -> List[OptimizationAction]:
        """Identify optimization opportunities."""
        actions = []

        for rule in self.optimization_rules:
            resource_type = rule["resource_type"]
            metrics = current_metrics.get(resource_type)

            if not metrics:
                continue

            # Check if condition is met
            if rule["condition"](metrics):
                # Check if action was recently applied
                if self._was_recently_applied(rule["name"]):
                    continue

                # Create optimization action
                action = OptimizationAction(
                    action_id=str(uuid.uuid4()),
                    name=rule["name"],
                    description=rule["description"],
                    resource_type=resource_type,
                    impact_score=rule["impact"],
                    confidence=rule["confidence"],
                    parameters={"metrics": metrics.to_dict()},
                    estimated_improvement=rule["impact"] * 0.1,  # 10% of impact score
                    execution_time_ms=100.0,
                )

                actions.append(action)

        return actions

    def _was_recently_applied(self, action_name: str, minutes: int = 10) -> bool:
        """Check if action was recently applied."""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)

        for action in self.applied_actions.values():
            if (
                action.name == action_name
                and action.applied_at
                and action.applied_at > cutoff_time
            ):
                return True

        return False

    async def _apply_optimization_action(self, action: OptimizationAction) -> bool:
        """Apply optimization action."""
        start_time = time.time()

        try:
            # Find and execute the action
            rule = next(
                (r for r in self.optimization_rules if r["name"] == action.name), None
            )
            if not rule:
                logger.error(f"Unknown optimization action: {action.name}")
                return False

            # Execute the action
            result = await rule["action"](action.parameters)

            # Update action
            action.applied_at = datetime.now()
            action.result = result
            action.execution_time_ms = (time.time() - start_time) * 1000

            # Store applied action
            self.applied_actions[action.action_id] = action
            self.optimization_history.append(action)

            logger.info(f"Applied optimization: {action.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to apply optimization {action.name}: {e}")
            return False

    async def _increase_cache_size(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Increase cache size."""
        # Mock implementation - would integrate with actual cache system
        current_size = 1000  # MB
        new_size = int(current_size * 1.2)  # Increase by 20%

        return {
            "previous_size_mb": current_size,
            "new_size_mb": new_size,
            "increase_percentage": 20.0,
        }

    async def _reduce_cache_size(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Reduce cache size."""
        # Mock implementation
        current_size = 1000  # MB
        new_size = int(current_size * 0.8)  # Reduce by 20%

        return {
            "previous_size_mb": current_size,
            "new_size_mb": new_size,
            "reduction_percentage": 20.0,
        }

    async def _reduce_concurrency(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Reduce concurrency limits."""
        # Mock implementation
        current_concurrency = 50
        new_concurrency = max(10, int(current_concurrency * 0.7))  # Reduce by 30%

        return {
            "previous_concurrency": current_concurrency,
            "new_concurrency": new_concurrency,
            "reduction_percentage": 30.0,
        }

    async def _enable_aggressive_caching(
        self, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enable aggressive caching."""
        return {"aggressive_caching_enabled": True, "cache_ttl_multiplier": 2.0}

    async def _optimize_network_connections(
        self, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize network connection pool."""
        return {
            "connection_pool_size": 20,
            "keep_alive_enabled": True,
            "timeout_seconds": 30,
        }

    def set_performance_profile(self, profile: PerformanceProfile):
        """Set active performance profile."""
        # Deactivate previous profile
        if self.active_profile:
            self.active_profile.active = False

        # Activate new profile
        self.active_profile = profile
        profile.active = True

        logger.info(f"Activated performance profile: {profile.name}")

    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics."""
        recent_actions = list(self.optimization_history)[-50:]  # Last 50 actions

        action_counts = defaultdict(int)
        impact_scores = []
        execution_times = []

        for action in recent_actions:
            action_counts[action.name] += 1
            impact_scores.append(action.impact_score)
            if action.execution_time_ms:
                execution_times.append(action.execution_time_ms)

        return {
            "total_actions": len(self.optimization_history),
            "recent_actions": len(recent_actions),
            "action_distribution": dict(action_counts),
            "avg_impact_score": statistics.mean(impact_scores) if impact_scores else 0,
            "avg_execution_time_ms": (
                statistics.mean(execution_times) if execution_times else 0
            ),
            "active_profile": (
                self.active_profile.to_dict() if self.active_profile else None
            ),
            "applied_actions_count": len(self.applied_actions),
        }


class PerformanceTuner:
    """Advanced performance tuning and auto-configuration."""

    def __init__(
        self, resource_monitor: ResourceMonitor, optimization_engine: OptimizationEngine
    ):
        self.resource_monitor = resource_monitor
        self.optimization_engine = optimization_engine
        self.tuning_history: deque = deque(maxlen=500)
        self.performance_targets = self._create_default_targets()
        self.tuning_models = {}  # ML models for performance prediction

    def _create_default_targets(self) -> Dict[str, float]:
        """Create default performance targets."""
        return {
            "avg_response_time_ms": 500.0,
            "p95_response_time_ms": 1000.0,
            "success_rate": 0.95,
            "throughput_rps": 100.0,
            "cpu_utilization": 0.7,
            "memory_utilization": 0.8,
        }

    async def auto_tune(
        self, strategy: OptimizationStrategy = OptimizationStrategy.ADAPTIVE
    ) -> Dict[str, Any]:
        """Perform automatic performance tuning."""
        tuning_id = str(uuid.uuid4())
        start_time = time.time()

        try:
            # Collect current performance data
            current_metrics = self.resource_monitor.get_current_metrics()
            performance_summary = self.resource_monitor.get_performance_summary()

            # Identify performance gaps
            gaps = self._identify_performance_gaps(current_metrics, performance_summary)

            # Generate tuning recommendations
            recommendations = await self._generate_tuning_recommendations(
                gaps, strategy
            )

            # Apply tuning changes
            applied_changes = []
            for recommendation in recommendations:
                if await self._apply_tuning_change(recommendation):
                    applied_changes.append(recommendation)

            # Record tuning session
            tuning_result = {
                "tuning_id": tuning_id,
                "strategy": strategy.value,
                "duration_ms": (time.time() - start_time) * 1000,
                "performance_gaps": gaps,
                "recommendations_count": len(recommendations),
                "applied_changes_count": len(applied_changes),
                "applied_changes": applied_changes,
                "timestamp": datetime.now().isoformat(),
            }

            self.tuning_history.append(tuning_result)

            logger.info(
                f"Auto-tuning completed: {len(applied_changes)} changes applied"
            )

            return tuning_result

        except Exception as e:
            logger.error(f"Auto-tuning failed: {e}")
            return {
                "tuning_id": tuning_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _identify_performance_gaps(
        self,
        current_metrics: Dict[ResourceType, ResourceMetrics],
        performance_summary: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Identify performance gaps."""
        gaps = []

        # Check resource utilization gaps
        for resource_type, metrics in current_metrics.items():
            target = self.performance_targets.get(
                f"{resource_type.value}_utilization", 0.7
            )

            if metrics.utilization_percentage > target + 0.1:
                gaps.append(
                    {
                        "type": "resource_overutilization",
                        "resource": resource_type.value,
                        "current": metrics.utilization_percentage,
                        "target": target,
                        "severity": (
                            "high" if metrics.utilization_percentage > 0.9 else "medium"
                        ),
                    }
                )
            elif metrics.utilization_percentage < target - 0.2:
                gaps.append(
                    {
                        "type": "resource_underutilization",
                        "resource": resource_type.value,
                        "current": metrics.utilization_percentage,
                        "target": target,
                        "severity": "low",
                    }
                )

        # Check overall health
        if performance_summary.get("overall_health") == "critical":
            gaps.append(
                {
                    "type": "system_health",
                    "severity": "critical",
                    "description": "System in critical state",
                }
            )
        elif performance_summary.get("overall_health") == "warning":
            gaps.append(
                {
                    "type": "system_health",
                    "severity": "medium",
                    "description": "System performance degraded",
                }
            )

        return gaps

    async def _generate_tuning_recommendations(
        self, gaps: List[Dict[str, Any]], strategy: OptimizationStrategy
    ) -> List[Dict[str, Any]]:
        """Generate tuning recommendations based on gaps."""
        recommendations = []

        for gap in gaps:
            if gap["type"] == "resource_overutilization":
                resource = gap["resource"]
                severity = gap["severity"]

                if resource == "cpu":
                    recommendations.extend(
                        [
                            {
                                "action": "reduce_concurrency",
                                "parameters": {"reduction_factor": 0.2},
                                "expected_improvement": 0.3,
                                "confidence": 0.8,
                            },
                            {
                                "action": "enable_result_caching",
                                "parameters": {"cache_ttl": 300},
                                "expected_improvement": 0.2,
                                "confidence": 0.7,
                            },
                        ]
                    )
                elif resource == "memory":
                    recommendations.extend(
                        [
                            {
                                "action": "reduce_cache_size",
                                "parameters": {"reduction_factor": 0.3},
                                "expected_improvement": 0.4,
                                "confidence": 0.9,
                            },
                            {
                                "action": "enable_memory_optimization",
                                "parameters": {"gc_frequency": "high"},
                                "expected_improvement": 0.2,
                                "confidence": 0.8,
                            },
                        ]
                    )

            elif gap["type"] == "resource_underutilization":
                resource = gap["resource"]

                if resource == "cpu":
                    recommendations.append(
                        {
                            "action": "increase_concurrency",
                            "parameters": {"increase_factor": 1.3},
                            "expected_improvement": 0.4,
                            "confidence": 0.7,
                        }
                    )
                elif resource == "memory":
                    recommendations.append(
                        {
                            "action": "increase_cache_size",
                            "parameters": {"increase_factor": 1.5},
                            "expected_improvement": 0.3,
                            "confidence": 0.8,
                        }
                    )

        # Filter recommendations based on strategy
        if strategy == OptimizationStrategy.CONSERVATIVE:
            recommendations = [r for r in recommendations if r["confidence"] >= 0.8]
        elif strategy == OptimizationStrategy.AGGRESSIVE:
            recommendations = [
                r for r in recommendations if r["expected_improvement"] >= 0.3
            ]
        elif strategy == OptimizationStrategy.LATENCY_FOCUSED:
            recommendations = [
                r
                for r in recommendations
                if r["action"] in ["enable_result_caching", "increase_concurrency"]
            ]
        elif strategy == OptimizationStrategy.THROUGHPUT_FOCUSED:
            recommendations = [
                r
                for r in recommendations
                if r["action"] in ["increase_concurrency", "reduce_cache_size"]
            ]

        return recommendations

    async def _apply_tuning_change(self, recommendation: Dict[str, Any]) -> bool:
        """Apply a tuning change."""
        action = recommendation["action"]
        parameters = recommendation["parameters"]

        try:
            if action == "reduce_concurrency":
                # Apply concurrency reduction
                return await self._apply_concurrency_change(
                    "reduce", parameters.get("reduction_factor", 0.2)
                )
            elif action == "increase_concurrency":
                # Apply concurrency increase
                return await self._apply_concurrency_change(
                    "increase", parameters.get("increase_factor", 1.3)
                )
            elif action == "reduce_cache_size":
                # Apply cache size reduction
                return await self._apply_cache_size_change(
                    "reduce", parameters.get("reduction_factor", 0.3)
                )
            elif action == "increase_cache_size":
                # Apply cache size increase
                return await self._apply_cache_size_change(
                    "increase", parameters.get("increase_factor", 1.5)
                )
            elif action == "enable_result_caching":
                # Enable result caching
                return await self._enable_result_caching(parameters)
            elif action == "enable_memory_optimization":
                # Enable memory optimization
                return await self._enable_memory_optimization(parameters)

            return False

        except Exception as e:
            logger.error(f"Failed to apply tuning change {action}: {e}")
            return False

    async def _apply_concurrency_change(self, direction: str, factor: float) -> bool:
        """Apply concurrency change."""
        # Mock implementation
        logger.info(f"Applying concurrency {direction} with factor {factor}")
        return True

    async def _apply_cache_size_change(self, direction: str, factor: float) -> bool:
        """Apply cache size change."""
        # Mock implementation
        logger.info(f"Applying cache size {direction} with factor {factor}")
        return True

    async def _enable_result_caching(self, parameters: Dict[str, Any]) -> bool:
        """Enable result caching."""
        # Mock implementation
        logger.info(
            f"Enabling result caching with TTL {parameters.get('cache_ttl', 300)}"
        )
        return True

    async def _enable_memory_optimization(self, parameters: Dict[str, Any]) -> bool:
        """Enable memory optimization."""
        # Mock implementation
        logger.info(
            f"Enabling memory optimization with GC frequency {parameters.get('gc_frequency', 'normal')}"
        )
        return True

    def get_tuning_report(self, days: int = 7) -> Dict[str, Any]:
        """Generate tuning report."""
        cutoff_time = datetime.now() - timedelta(days=days)
        recent_tuning = [
            session
            for session in self.tuning_history
            if datetime.fromisoformat(session["timestamp"]) >= cutoff_time
        ]

        if not recent_tuning:
            return {"message": f"No tuning sessions in last {days} days"}

        # Calculate statistics
        total_sessions = len(recent_tuning)
        successful_sessions = sum(1 for s in recent_tuning if "error" not in s)
        avg_duration = statistics.mean([s["duration_ms"] for s in recent_tuning])
        total_changes = sum(s["applied_changes_count"] for s in recent_tuning)

        # Strategy distribution
        strategy_counts = defaultdict(int)
        for session in recent_tuning:
            strategy_counts[session["strategy"]] += 1

        # Common changes
        change_counts = defaultdict(int)
        for session in recent_tuning:
            for change in session.get("applied_changes", []):
                change_counts[change.get("action", "unknown")] += 1

        return {
            "period_days": days,
            "total_sessions": total_sessions,
            "successful_sessions": successful_sessions,
            "success_rate": (
                successful_sessions / total_sessions if total_sessions > 0 else 0
            ),
            "avg_duration_ms": avg_duration,
            "total_changes_applied": total_changes,
            "strategy_distribution": dict(strategy_counts),
            "common_changes": dict(change_counts),
            "performance_targets": self.performance_targets,
        }


# Global performance optimization components
resource_monitor = ResourceMonitor()
optimization_engine = OptimizationEngine(resource_monitor)
performance_tuner = PerformanceTuner(resource_monitor, optimization_engine)
