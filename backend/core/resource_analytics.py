"""
Resource usage analytics and optimization suggestions for Raptorflow backend.
Provides insights into resource patterns and recommends optimizations.
"""

import asyncio
import logging
import statistics
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from .resources import get_resource_manager, ResourceType, ResourceStatus
from .metrics_collector import get_metrics_collector

logger = logging.getLogger(__name__)


class OptimizationType(Enum):
    """Types of optimization recommendations."""
    
    CLEANUP = "cleanup"
    QUOTA_ADJUSTMENT = "quota_adjustment"
    SCHEDULING = "scheduling"
    CACHING = "caching"
    POOLING = "pooling"
    COMPRESSION = "compression"
    ARCHITECTURE = "architecture"


class OptimizationPriority(Enum):
    """Priority levels for optimization recommendations."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ResourcePattern:
    """Detected pattern in resource usage."""
    
    pattern_type: str
    description: str
    confidence: float  # 0.0 to 1.0
    resource_type: ResourceType
    time_window_start: datetime
    time_window_end: datetime
    metrics: Dict[str, float]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "pattern_type": self.pattern_type,
            "description": self.description,
            "confidence": self.confidence,
            "resource_type": self.resource_type.value,
            "time_window_start": self.time_window_start.isoformat(),
            "time_window_end": self.time_window_end.isoformat(),
            "metrics": self.metrics,
            "metadata": self.metadata,
        }


@dataclass
class OptimizationRecommendation:
    """Recommendation for resource optimization."""
    
    recommendation_id: str
    title: str
    description: str
    optimization_type: OptimizationType
    priority: OptimizationPriority
    estimated_savings: Optional[float] = None  # Estimated resource savings
    implementation_effort: str = "low"  # "low", "medium", "high"
    resource_type: Optional[ResourceType] = None
    current_state: Dict[str, Any] = field(default_factory=dict)
    recommended_state: Dict[str, Any] = field(default_factory=dict)
    steps: List[str] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "recommendation_id": self.recommendation_id,
            "title": self.title,
            "description": self.description,
            "optimization_type": self.optimization_type.value,
            "priority": self.priority.value,
            "estimated_savings": self.estimated_savings,
            "implementation_effort": self.implementation_effort,
            "resource_type": self.resource_type.value if self.resource_type else None,
            "current_state": self.current_state,
            "recommended_state": self.recommended_state,
            "steps": self.steps,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class ResourceUsageProfile:
    """Profile of resource usage patterns."""
    
    resource_type: ResourceType
    time_window_hours: int
    total_usage: float
    peak_usage: float
    average_usage: float
    usage_variance: float
    growth_rate: float  # Growth rate per hour
    efficiency_score: float  # 0.0 to 1.0
    waste_percentage: float
    patterns: List[ResourcePattern] = field(default_factory=list)
    recommendations: List[OptimizationRecommendation] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "resource_type": self.resource_type.value,
            "time_window_hours": self.time_window_hours,
            "total_usage": self.total_usage,
            "peak_usage": self.peak_usage,
            "average_usage": self.average_usage,
            "usage_variance": self.usage_variance,
            "growth_rate": self.growth_rate,
            "efficiency_score": self.efficiency_score,
            "waste_percentage": self.waste_percentage,
            "patterns": [p.to_dict() for p in self.patterns],
            "recommendations": [r.to_dict() for r in self.recommendations],
        }


class ResourceAnalyzer:
    """Analyzes resource usage patterns and generates optimization recommendations."""
    
    def __init__(self, analysis_interval: int = 300):  # 5 minutes
        self.analysis_interval = analysis_interval
        
        # Analysis data storage
        self.usage_profiles: Dict[ResourceType, ResourceUsageProfile] = {}
        self.detected_patterns: List[ResourcePattern] = []
        self.recommendations: List[OptimizationRecommendation] = []
        
        # Historical data for trend analysis
        self.historical_data: Dict[ResourceType, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Background tasks
        self._background_tasks: Set[asyncio.Task] = set()
        self._running = False
        
        # Analysis configuration
        self.analysis_config = {
            "pattern_detection_threshold": 0.7,  # Minimum confidence for patterns
            "recommendation_threshold": 0.6,  # Minimum priority for recommendations
            "trend_analysis_window": 24,  # Hours for trend analysis
            "efficiency_threshold": 0.8,  # Minimum efficiency score
            "waste_threshold": 20.0,  # Minimum waste percentage
        }
        
        logger.info(f"Resource analyzer initialized with analysis interval: {analysis_interval}s")
    
    async def start(self):
        """Start the resource analyzer."""
        if self._running:
            return
        
        self._running = True
        
        # Start background analysis
        self._background_tasks.add(asyncio.create_task(self._analysis_loop()))
        
        logger.info("Resource analyzer started")
    
    async def stop(self):
        """Stop the resource analyzer."""
        self._running = False
        
        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()
        
        await asyncio.gather(*self._background_tasks, return_exceptions=True)
        self._background_tasks.clear()
        
        logger.info("Resource analyzer stopped")
    
    async def _analysis_loop(self):
        """Background loop for resource analysis."""
        while self._running:
            try:
                await asyncio.sleep(self.analysis_interval)
                await self._perform_analysis()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Resource analysis loop error: {e}")
    
    async def _perform_analysis(self):
        """Perform comprehensive resource analysis."""
        try:
            # Get current resource data
            resource_manager = get_resource_manager()
            metrics_collector = get_metrics_collector()
            
            # Analyze each resource type
            for resource_type in ResourceType:
                await self._analyze_resource_type(resource_type, resource_manager, metrics_collector)
            
            # Detect patterns across all resources
            await self._detect_cross_resource_patterns()
            
            # Generate optimization recommendations
            await self._generate_recommendations()
            
            # Clean up old data
            self._cleanup_old_analysis_data()
            
        except Exception as e:
            logger.error(f"Resource analysis failed: {e}")
    
    async def _analyze_resource_type(
        self,
        resource_type: ResourceType,
        resource_manager,
        metrics_collector
    ):
        """Analyze a specific resource type."""
        try:
            # Get resource data
            resource_summary = resource_manager.get_resource_summary()
            current_count = resource_summary["resources_by_type"].get(resource_type.value, 0)
            
            # Get historical metrics
            metric_name = f"resource_count_{resource_type.value}"
            metric_values = metrics_collector.get_metric_values(metric_name, limit=100)
            
            if not metric_values:
                return
            
            # Extract usage data
            usage_data = [value["value"] for value in metric_values]
            timestamps = [datetime.fromisoformat(value["timestamp"]) for value in metric_values]
            
            # Calculate statistics
            if len(usage_data) < 2:
                return
            
            total_usage = sum(usage_data)
            peak_usage = max(usage_data)
            average_usage = statistics.mean(usage_data)
            usage_variance = statistics.variance(usage_data) if len(usage_data) > 1 else 0
            
            # Calculate growth rate
            time_span = (timestamps[-1] - timestamps[0]).total_seconds() / 3600  # Hours
            if time_span > 0:
                growth_rate = (usage_data[-1] - usage_data[0]) / time_span
            else:
                growth_rate = 0
            
            # Calculate efficiency and waste
            efficiency_score = self._calculate_efficiency_score(usage_data, peak_usage)
            waste_percentage = self._calculate_waste_percentage(usage_data, peak_usage)
            
            # Create usage profile
            profile = ResourceUsageProfile(
                resource_type=resource_type,
                time_window_hours=int(time_span),
                total_usage=total_usage,
                peak_usage=peak_usage,
                average_usage=average_usage,
                usage_variance=usage_variance,
                growth_rate=growth_rate,
                efficiency_score=efficiency_score,
                waste_percentage=waste_percentage,
            )
            
            self.usage_profiles[resource_type] = profile
            
            # Store historical data
            self.historical_data[resource_type].append({
                "timestamp": datetime.now(),
                "count": current_count,
                "average": average_usage,
                "peak": peak_usage,
                "efficiency": efficiency_score,
                "waste": waste_percentage,
            })
            
            # Detect patterns for this resource type
            await self._detect_resource_patterns(resource_type, usage_data, timestamps)
            
        except Exception as e:
            logger.error(f"Failed to analyze resource type {resource_type.value}: {e}")
    
    def _calculate_efficiency_score(self, usage_data: List[float], peak_usage: float) -> float:
        """Calculate efficiency score based on usage patterns."""
        if peak_usage == 0:
            return 1.0
        
        # Efficiency = average usage / peak usage
        # Higher efficiency means resources are well-utilized
        average_usage = statistics.mean(usage_data)
        efficiency = average_usage / peak_usage
        
        # Adjust for variance (high variance reduces efficiency)
        if len(usage_data) > 1:
            variance = statistics.variance(usage_data)
            variance_penalty = min(variance / (peak_usage ** 2), 0.5)
            efficiency -= variance_penalty
        
        return max(0.0, min(1.0, efficiency))
    
    def _calculate_waste_percentage(self, usage_data: List[float], peak_usage: float) -> float:
        """Calculate percentage of wasted resources."""
        if peak_usage == 0:
            return 0.0
        
        # Waste = (peak - average) / peak * 100
        average_usage = statistics.mean(usage_data)
        waste = ((peak_usage - average_usage) / peak_usage) * 100
        
        return max(0.0, waste)
    
    async def _detect_resource_patterns(
        self,
        resource_type: ResourceType,
        usage_data: List[float],
        timestamps: List[datetime]
    ):
        """Detect patterns in resource usage."""
        try:
            patterns = []
            
            # Pattern 1: Gradual growth trend
            if len(usage_data) >= 10:
                growth_pattern = self._detect_growth_pattern(usage_data, timestamps)
                if growth_pattern:
                    patterns.append(growth_pattern)
            
            # Pattern 2: Periodic spikes
            spike_pattern = self._detect_spike_pattern(usage_data, timestamps)
            if spike_pattern:
                patterns.append(spike_pattern)
            
            # Pattern 3: Memory leaks (continuous growth)
            leak_pattern = self._detect_leak_pattern(usage_data, timestamps)
            if leak_pattern:
                patterns.append(leak_pattern)
            
            # Pattern 4: Underutilization
            underutilization_pattern = self._detect_underutilization_pattern(usage_data)
            if underutilization_pattern:
                patterns.append(underutilization_pattern)
            
            # Store patterns
            for pattern in patterns:
                self.detected_patterns.append(pattern)
            
            # Keep only recent patterns
            if len(self.detected_patterns) > 100:
                self.detected_patterns = self.detected_patterns[-100:]
            
        except Exception as e:
            logger.error(f"Pattern detection failed for {resource_type.value}: {e}")
    
    def _detect_growth_pattern(
        self,
        usage_data: List[float],
        timestamps: List[datetime]
    ) -> Optional[ResourcePattern]:
        """Detect gradual growth pattern."""
        try:
            if len(usage_data) < 10:
                return None
            
            # Calculate linear regression
            x = list(range(len(usage_data)))
            y = usage_data
            
            # Simple linear regression
            n = len(x)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(x[i] * y[i] for i in range(n))
            sum_x2 = sum(x[i] ** 2 for i in range(n))
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
            
            # Calculate R-squared
            y_mean = sum_y / n
            ss_tot = sum((y[i] - y_mean) ** 2 for i in range(n))
            ss_res = sum((y[i] - (slope * x[i] + (sum_y - slope * sum_x) / n)) ** 2 for i in range(n))
            
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            # Check if there's significant positive growth
            if slope > 0.1 and r_squared > 0.7:
                confidence = min(r_squared, 0.95)
                
                return ResourcePattern(
                    pattern_type="gradual_growth",
                    description=f"Resource usage showing consistent growth trend (slope: {slope:.2f})",
                    confidence=confidence,
                    resource_type=ResourceType.MEMORY,  # This should be parameterized
                    time_window_start=timestamps[0],
                    time_window_end=timestamps[-1],
                    metrics={
                        "slope": slope,
                        "r_squared": r_squared,
                        "growth_rate_percent": (slope / usage_data[0]) * 100 if usage_data[0] > 0 else 0,
                    }
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Growth pattern detection failed: {e}")
            return None
    
    def _detect_spike_pattern(
        self,
        usage_data: List[float],
        timestamps: List[datetime]
    ) -> Optional[ResourcePattern]:
        """Detect periodic spike patterns."""
        try:
            if len(usage_data) < 20:
                return None
            
            # Find spikes (values > 2 standard deviations from mean)
            mean_usage = statistics.mean(usage_data)
            std_usage = statistics.stdev(usage_data) if len(usage_data) > 1 else 0
            threshold = mean_usage + 2 * std_usage
            
            spike_indices = [
                i for i, value in enumerate(usage_data)
                if value > threshold
            ]
            
            # Check if spikes are periodic
            if len(spike_indices) >= 3:
                # Calculate intervals between spikes
                intervals = [
                    spike_indices[i] - spike_indices[i-1]
                    for i in range(1, len(spike_indices))
                ]
                
                if intervals:
                    avg_interval = statistics.mean(intervals)
                    interval_variance = statistics.variance(intervals) if len(intervals) > 1 else 0
                    
                    # Check if intervals are consistent (low variance)
                    if interval_variance < avg_interval * 0.5:
                        confidence = 1.0 - (interval_variance / (avg_interval ** 2))
                        confidence = max(0.5, min(0.95, confidence))
                        
                        return ResourcePattern(
                            pattern_type="periodic_spikes",
                            description=f"Periodic resource spikes detected every {avg_interval:.1f} samples",
                            confidence=confidence,
                            resource_type=ResourceType.MEMORY,  # This should be parameterized
                            time_window_start=timestamps[0],
                            time_window_end=timestamps[-1],
                            metrics={
                                "spike_count": len(spike_indices),
                                "average_interval": avg_interval,
                                "spike_threshold": threshold,
                            }
                        )
            
            return None
            
        except Exception as e:
            logger.error(f"Spike pattern detection failed: {e}")
            return None
    
    def _detect_leak_pattern(
        self,
        usage_data: List[float],
        timestamps: List[datetime]
    ) -> Optional[ResourcePattern]:
        """Detect memory leak patterns (continuous growth without release)."""
        try:
            if len(usage_data) < 20:
                return None
            
            # Check for continuous growth with minimal decreases
            increases = 0
            decreases = 0
            total_change = 0
            
            for i in range(1, len(usage_data)):
                change = usage_data[i] - usage_data[i-1]
                total_change += change
                
                if change > 0:
                    increases += 1
                elif change < 0:
                    decreases += 1
            
            # Leak indicators: mostly increases, positive net change
            total_changes = increases + decreases
            if total_changes == 0:
                return None
            
            increase_ratio = increases / total_changes
            
            if increase_ratio > 0.8 and total_change > 0:
                confidence = min(increase_ratio, 0.95)
                
                return ResourcePattern(
                    pattern_type="memory_leak",
                    description=f"Potential memory leak detected: {increase_ratio:.1%} increases, net growth {total_change:.1f}",
                    confidence=confidence,
                    resource_type=ResourceType.MEMORY,
                    time_window_start=timestamps[0],
                    time_window_end=timestamps[-1],
                    metrics={
                        "increase_ratio": increase_ratio,
                        "net_change": total_change,
                        "increases": increases,
                        "decreases": decreases,
                    }
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Leak pattern detection failed: {e}")
            return None
    
    def _detect_underutilization_pattern(
        self,
        usage_data: List[float]
    ) -> Optional[ResourcePattern]:
        """Detect underutilization patterns."""
        try:
            if len(usage_data) < 10:
                return None
            
            peak_usage = max(usage_data)
            average_usage = statistics.mean(usage_data)
            
            # Underutilization: average usage is much lower than peak
            utilization_ratio = average_usage / peak_usage if peak_usage > 0 else 0
            
            if utilization_ratio < 0.3:  # Less than 30% utilization
                confidence = 1.0 - utilization_ratio
                
                return ResourcePattern(
                    pattern_type="underutilization",
                    description=f"Resource underutilized: {utilization_ratio:.1%} of peak capacity",
                    confidence=confidence,
                    resource_type=ResourceType.MEMORY,  # This should be parameterized
                    time_window_start=datetime.now() - timedelta(hours=len(usage_data)),
                    time_window_end=datetime.now(),
                    metrics={
                        "utilization_ratio": utilization_ratio,
                        "peak_usage": peak_usage,
                        "average_usage": average_usage,
                    }
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Underutilization pattern detection failed: {e}")
            return None
    
    async def _detect_cross_resource_patterns(self):
        """Detect patterns that span multiple resource types."""
        try:
            # This would analyze correlations between different resource types
            # For example: high memory usage correlates with high file handle count
            
            # Placeholder for cross-resource analysis
            pass
            
        except Exception as e:
            logger.error(f"Cross-resource pattern detection failed: {e}")
    
    async def _generate_recommendations(self):
        """Generate optimization recommendations based on analysis."""
        try:
            new_recommendations = []
            
            # Generate recommendations for each resource type
            for resource_type, profile in self.usage_profiles.items():
                recommendations = await self._generate_resource_recommendations(resource_type, profile)
                new_recommendations.extend(recommendations)
            
            # Add new recommendations (avoid duplicates)
            for rec in new_recommendations:
                if not self._recommendation_exists(rec):
                    self.recommendations.append(rec)
            
            # Keep only recent recommendations
            if len(self.recommendations) > 50:
                self.recommendations = self.recommendations[-50:]
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
    
    async def _generate_resource_recommendations(
        self,
        resource_type: ResourceType,
        profile: ResourceUsageProfile
    ) -> List[OptimizationRecommendation]:
        """Generate recommendations for a specific resource type."""
        recommendations = []
        
        # Recommendation 1: High waste percentage
        if profile.waste_percentage > self.analysis_config["waste_threshold"]:
            priority = OptimizationPriority.HIGH if profile.waste_percentage > 50 else OptimizationPriority.MEDIUM
            
            rec = OptimizationRecommendation(
                recommendation_id=f"reduce_waste_{resource_type.value}_{int(datetime.now().timestamp())}",
                title=f"Reduce {resource_type.value} waste",
                description=f"Resource waste is {profile.waste_percentage:.1f}%. Consider reducing allocated resources.",
                optimization_type=OptimizationType.QUOTA_ADJUSTMENT,
                priority=priority,
                estimated_savings=profile.waste_percentage,
                resource_type=resource_type,
                current_state={"waste_percentage": profile.waste_percentage},
                recommended_state={"target_waste_percentage": 10.0},
                steps=[
                    f"Analyze {resource_type.value} usage patterns",
                    "Reduce resource quotas",
                    "Implement better cleanup strategies",
                    "Monitor after changes",
                ],
            )
            recommendations.append(rec)
        
        # Recommendation 2: Low efficiency
        if profile.efficiency_score < self.analysis_config["efficiency_threshold"]:
            priority = OptimizationPriority.CRITICAL if profile.efficiency_score < 0.5 else OptimizationPriority.HIGH
            
            rec = OptimizationRecommendation(
                recommendation_id=f"improve_efficiency_{resource_type.value}_{int(datetime.now().timestamp())}",
                title=f"Improve {resource_type.value} efficiency",
                description=f"Resource efficiency is {profile.efficiency_score:.1%}. Implement optimization strategies.",
                optimization_type=OptimizationType.CACHING,
                priority=priority,
                estimated_savings=(1.0 - profile.efficiency_score) * 100,
                resource_type=resource_type,
                current_state={"efficiency_score": profile.efficiency_score},
                recommended_state={"target_efficiency_score": 0.9},
                steps=[
                    "Implement resource pooling",
                    "Add caching layers",
                    "Optimize resource allocation",
                    "Review usage patterns",
                ],
            )
            recommendations.append(rec)
        
        # Recommendation 3: High growth rate
        if profile.growth_rate > 0.1:  # 10% growth per hour
            priority = OptimizationPriority.CRITICAL if profile.growth_rate > 1.0 else OptimizationPriority.HIGH
            
            rec = OptimizationRecommendation(
                recommendation_id=f"address_growth_{resource_type.value}_{int(datetime.now().timestamp())}",
                title=f"Address {resource_type.value} growth rate",
                description=f"Resource usage growing at {profile.growth_rate:.1f} per hour. Potential leak or scaling issue.",
                optimization_type=OptimizationType.CLEANUP,
                priority=priority,
                resource_type=resource_type,
                current_state={"growth_rate": profile.growth_rate},
                recommended_state={"target_growth_rate": 0.01},
                steps=[
                    "Investigate resource leaks",
                    "Review cleanup strategies",
                    "Check for memory leaks",
                    "Implement automatic scaling",
                ],
            )
            recommendations.append(rec)
        
        # Recommendation 4: High variance
        if profile.usage_variance > profile.average_usage:
            priority = OptimizationPriority.MEDIUM
            
            rec = OptimizationRecommendation(
                recommendation_id=f"stabilize_usage_{resource_type.value}_{int(datetime.now().timestamp())}",
                title=f"Stabilize {resource_type.value} usage",
                description=f"High usage variance detected. Consider resource pooling or load balancing.",
                optimization_type=OptimizationType.POOLING,
                priority=priority,
                resource_type=resource_type,
                current_state={"usage_variance": profile.usage_variance},
                recommended_state={"target_variance": profile.average_usage * 0.5},
                steps=[
                    "Implement resource pooling",
                    "Add load balancing",
                    "Smooth out usage patterns",
                    "Consider predictive scaling",
                ],
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _recommendation_exists(self, new_rec: OptimizationRecommendation) -> bool:
        """Check if a similar recommendation already exists."""
        for existing_rec in self.recommendations:
            if (existing_rec.resource_type == new_rec.resource_type and
                existing_rec.optimization_type == new_rec.optimization_type and
                (datetime.now() - existing_rec.created_at).total_seconds() < 3600):  # Within 1 hour
                return True
        return False
    
    def _cleanup_old_analysis_data(self):
        """Clean up old analysis data."""
        cutoff_time = datetime.now() - timedelta(days=7)
        
        # Clean up old patterns
        self.detected_patterns = [
            pattern for pattern in self.detected_patterns
            if pattern.time_window_end >= cutoff_time
        ]
        
        # Clean up old recommendations
        self.recommendations = [
            rec for rec in self.recommendations
            if rec.created_at >= cutoff_time
        ]
    
    def get_usage_profiles(self) -> Dict[str, Any]:
        """Get all resource usage profiles."""
        return {
            resource_type.value: profile.to_dict()
            for resource_type, profile in self.usage_profiles.items()
        }
    
    def get_detected_patterns(
        self,
        resource_type: Optional[ResourceType] = None,
        pattern_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get detected patterns with optional filtering."""
        patterns = self.detected_patterns
        
        if resource_type:
            patterns = [p for p in patterns if p.resource_type == resource_type]
        
        if pattern_type:
            patterns = [p for p in patterns if p.pattern_type == pattern_type]
        
        # Sort by confidence (highest first)
        patterns.sort(key=lambda x: x.confidence, reverse=True)
        
        return [pattern.to_dict() for pattern in patterns[:limit]]
    
    def get_recommendations(
        self,
        priority: Optional[OptimizationPriority] = None,
        optimization_type: Optional[OptimizationType] = None,
        resource_type: Optional[ResourceType] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get optimization recommendations with optional filtering."""
        recommendations = self.recommendations
        
        if priority:
            recommendations = [r for r in recommendations if r.priority == priority]
        
        if optimization_type:
            recommendations = [r for r in recommendations if r.optimization_type == optimization_type]
        
        if resource_type:
            recommendations = [r for r in recommendations if r.resource_type == resource_type]
        
        # Sort by priority and creation time
        priority_order = {
            OptimizationPriority.CRITICAL: 4,
            OptimizationPriority.HIGH: 3,
            OptimizationPriority.MEDIUM: 2,
            OptimizationPriority.LOW: 1,
        }
        
        recommendations.sort(
            key=lambda x: (priority_order.get(x.priority, 0), x.created_at),
            reverse=True
        )
        
        return [rec.to_dict() for rec in recommendations[:limit]]
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get a summary of the analysis results."""
        return {
            "analyzed_resource_types": len(self.usage_profiles),
            "total_patterns_detected": len(self.detected_patterns),
            "total_recommendations": len(self.recommendations),
            "patterns_by_type": defaultdict(int),
            "recommendations_by_priority": defaultdict(int),
            "recommendations_by_type": defaultdict(int),
            "analysis_config": self.analysis_config,
        }


# Global resource analyzer instance
_resource_analyzer: Optional[ResourceAnalyzer] = None


def get_resource_analyzer() -> ResourceAnalyzer:
    """Get or create the global resource analyzer instance."""
    global _resource_analyzer
    if _resource_analyzer is None:
        _resource_analyzer = ResourceAnalyzer()
    return _resource_analyzer


async def start_resource_analyzer():
    """Start the global resource analyzer."""
    analyzer = get_resource_analyzer()
    await analyzer.start()


async def stop_resource_analyzer():
    """Stop the global resource analyzer."""
    analyzer = get_resource_analyzer()
    if analyzer:
        await analyzer.stop()
