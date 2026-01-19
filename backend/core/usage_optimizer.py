import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class OptimizationType(Enum):
    RATE_LIMIT = "rate_limit"
    RESOURCE_USAGE = "resource_usage"
    COST_EFFICIENCY = "cost_efficiency"
    PERFORMANCE = "performance"
    SCALABILITY = "scalability"

class RecommendationPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class OptimizationStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class OptimizationMetric:
    name: str
    current_value: float
    target_value: float
    improvement_percentage: float
    unit: str = ""
    description: str = ""

@dataclass
class OptimizationRecommendation:
    id: str
    type: OptimizationType
    priority: RecommendationPriority
    title: str
    description: str
    expected_impact: str
    implementation_effort: str
    metrics: List[OptimizationMetric]
    action_steps: List[str]
    created_at: datetime = field(default_factory=datetime.now)
    status: OptimizationStatus = OptimizationStatus.PENDING

@dataclass
class OptimizationPlan:
    id: str
    user_id: str
    recommendations: List[OptimizationRecommendation]
    total_expected_improvement: float
    implementation_timeline: str
    created_at: datetime = field(default_factory=datetime.now)
    status: OptimizationStatus = OptimizationStatus.PENDING

@dataclass
class UsagePattern:
    user_id: str
    endpoint: str
    hourly_usage: List[int]
    peak_hours: List[int]
    average_usage: float
    usage_variance: float
    efficiency_score: float
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class OptimizationResult:
    plan_id: str
    recommendations_implemented: int
    metrics_improved: List[str]
    actual_improvement: float
    cost_savings: float
    performance_gain: float
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class OptimizationConfig:
    analysis_interval: int = 300  # 5 minutes
    recommendation_threshold: float = 0.1  # 10% improvement threshold
    max_recommendations_per_plan: int = 10
    optimization_window: int = 24  # hours
    efficiency_target: float = 0.8
    cost_sensitivity: float = 0.7
    performance_weight: float = 0.6

class UsageOptimizer:
    def __init__(self, config: Optional[OptimizationConfig] = None):
        self.config = config or OptimizationConfig()
        self.is_running = False
        self.optimization_tasks: Dict[str, asyncio.Task] = {}
        self.usage_patterns: Dict[str, UsagePattern] = {}
        self.optimization_plans: Dict[str, OptimizationPlan] = {}
        self.optimization_results: List[OptimizationResult] = []
        self.recommendation_history: List[OptimizationRecommendation] = []
        
        # Performance tracking
        self.optimization_metrics = {
            "total_optimizations": 0,
            "successful_optimizations": 0,
            "average_improvement": 0.0,
            "total_cost_savings": 0.0,
            "active_plans": 0
        }
        
        logger.info("UsageOptimizer initialized")

    async def start(self):
        """Start the usage optimizer service"""
        if self.is_running:
            logger.warning("UsageOptimizer is already running")
            return
        
        self.is_running = True
        logger.info("Starting UsageOptimizer")
        
        # Start background optimization tasks
        self.optimization_tasks["analysis"] = asyncio.create_task(self._usage_analysis_loop())
        self.optimization_tasks["recommendation"] = asyncio.create_task(self._recommendation_generation_loop())
        self.optimization_tasks["cleanup"] = asyncio.create_task(self._cleanup_loop())

    async def stop(self):
        """Stop the usage optimizer service"""
        if not self.is_running:
            return
        
        self.is_running = False
        logger.info("Stopping UsageOptimizer")
        
        # Cancel all background tasks
        for task_name, task in self.optimization_tasks.items():
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    logger.info(f"Cancelled {task_name} task")
        
        self.optimization_tasks.clear()

    async def analyze_usage_patterns(self, user_id: str, usage_data: Dict[str, Any]) -> UsagePattern:
        """Analyze usage patterns for a specific user"""
        try:
            endpoint = usage_data.get("endpoint", "")
            hourly_data = usage_data.get("hourly_usage", [0] * 24)
            
            # Calculate pattern metrics
            average_usage = np.mean(hourly_data)
            usage_variance = np.var(hourly_data)
            
            # Identify peak hours
            peak_threshold = average_usage + np.std(hourly_data)
            peak_hours = [i for i, usage in enumerate(hourly_data) if usage > peak_threshold]
            
            # Calculate efficiency score
            total_requests = sum(hourly_data)
            efficient_requests = sum(usage for usage in hourly_data if usage <= average_usage + np.std(hourly_data))
            efficiency_score = efficient_requests / total_requests if total_requests > 0 else 0
            
            pattern = UsagePattern(
                user_id=user_id,
                endpoint=endpoint,
                hourly_usage=hourly_data,
                peak_hours=peak_hours,
                average_usage=average_usage,
                usage_variance=usage_variance,
                efficiency_score=efficiency_score
            )
            
            self.usage_patterns[f"{user_id}_{endpoint}"] = pattern
            logger.info(f"Analyzed usage pattern for user {user_id}, endpoint {endpoint}")
            
            return pattern
            
        except Exception as e:
            logger.error(f"Error analyzing usage patterns: {e}")
            raise

    async def generate_optimization_plan(self, user_id: str, optimization_types: List[OptimizationType] = None) -> OptimizationPlan:
        """Generate optimization plan for a user"""
        try:
            if optimization_types is None:
                optimization_types = list(OptimizationType)
            
            recommendations = []
            
            for opt_type in optimization_types:
                type_recommendations = await self._generate_recommendations_for_type(user_id, opt_type)
                recommendations.extend(type_recommendations)
            
            # Sort by priority and expected impact
            recommendations.sort(key=lambda r: (
                {"critical": 4, "high": 3, "medium": 2, "low": 1}[r.priority.value],
                r.metrics[0].improvement_percentage if r.metrics else 0
            ), reverse=True)
            
            # Limit recommendations
            recommendations = recommendations[:self.config.max_recommendations_per_plan]
            
            # Calculate total expected improvement
            total_improvement = sum(
                r.metrics[0].improvement_percentage 
                for r in recommendations if r.metrics
            ) / len(recommendations) if recommendations else 0
            
            plan = OptimizationPlan(
                id=f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}",
                user_id=user_id,
                recommendations=recommendations,
                total_expected_improvement=total_improvement,
                implementation_timeline=self._calculate_timeline(recommendations)
            )
            
            self.optimization_plans[plan.id] = plan
            self.optimization_metrics["active_plans"] += 1
            
            logger.info(f"Generated optimization plan {plan.id} for user {user_id}")
            return plan
            
        except Exception as e:
            logger.error(f"Error generating optimization plan: {e}")
            raise

    async def implement_optimization(self, plan_id: str, recommendation_ids: List[str] = None) -> OptimizationResult:
        """Implement optimization recommendations"""
        try:
            if plan_id not in self.optimization_plans:
                raise ValueError(f"Optimization plan {plan_id} not found")
            
            plan = self.optimization_plans[plan_id]
            plan.status = OptimizationStatus.IN_PROGRESS
            
            recommendations_to_implement = []
            if recommendation_ids:
                recommendations_to_implement = [
                    r for r in plan.recommendations if r.id in recommendation_ids
                ]
            else:
                recommendations_to_implement = plan.recommendations
            
            implemented_count = 0
            metrics_improved = []
            total_improvement = 0
            
            for recommendation in recommendations_to_implement:
                try:
                    success = await self._implement_recommendation(recommendation)
                    if success:
                        implemented_count += 1
                        recommendation.status = OptimizationStatus.COMPLETED
                        metrics_improved.extend([m.name for m in recommendation.metrics])
                        total_improvement += recommendation.metrics[0].improvement_percentage if recommendation.metrics else 0
                    else:
                        recommendation.status = OptimizationStatus.FAILED
                except Exception as e:
                    logger.error(f"Error implementing recommendation {recommendation.id}: {e}")
                    recommendation.status = OptimizationStatus.FAILED
            
            # Calculate results
            cost_savings = total_improvement * self.config.cost_sensitivity * 100  # Simplified calculation
            performance_gain = total_improvement * self.config.performance_weight
            
            result = OptimizationResult(
                plan_id=plan_id,
                recommendations_implemented=implemented_count,
                metrics_improved=list(set(metrics_improved)),
                actual_improvement=total_improvement / len(recommendations_to_implement) if recommendations_to_implement else 0,
                cost_savings=cost_savings,
                performance_gain=performance_gain
            )
            
            self.optimization_results.append(result)
            plan.status = OptimizationStatus.COMPLETED
            
            # Update metrics
            self.optimization_metrics["total_optimizations"] += 1
            self.optimization_metrics["successful_optimizations"] += 1
            self.optimization_metrics["total_cost_savings"] += cost_savings
            self.optimization_metrics["active_plans"] -= 1
            
            logger.info(f"Implemented optimization for plan {plan_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error implementing optimization: {e}")
            raise

    async def get_optimization_insights(self, user_id: str = None) -> Dict[str, Any]:
        """Get optimization insights and analytics"""
        try:
            insights = {
                "overall_metrics": self.optimization_metrics.copy(),
                "recent_results": [],
                "active_plans": [],
                "recommendation_trends": {},
                "efficiency_scores": {}
            }
            
            # Filter results by user if specified
            results = self.optimization_results
            if user_id:
                user_plans = [p for p in self.optimization_plans.values() if p.user_id == user_id]
                user_plan_ids = [p.id for p in user_plans]
                results = [r for r in results if r.plan_id in user_plan_ids]
            
            # Recent results
            insights["recent_results"] = [
                {
                    "plan_id": r.plan_id,
                    "recommendations_implemented": r.recommendations_implemented,
                    "actual_improvement": r.actual_improvement,
                    "cost_savings": r.cost_savings,
                    "timestamp": r.timestamp.isoformat()
                }
                for r in sorted(results, key=lambda x: x.timestamp, reverse=True)[:10]
            ]
            
            # Active plans
            insights["active_plans"] = [
                {
                    "plan_id": p.id,
                    "user_id": p.user_id,
                    "total_recommendations": len(p.recommendations),
                    "expected_improvement": p.total_expected_improvement,
                    "status": p.status.value
                }
                for p in self.optimization_plans.values() 
                if p.status in [OptimizationStatus.PENDING, OptimizationStatus.IN_PROGRESS]
            ]
            
            # Recommendation trends
            type_counts = defaultdict(int)
            for rec in self.recommendation_history:
                type_counts[rec.type.value] += 1
            insights["recommendation_trends"] = dict(type_counts)
            
            # Efficiency scores
            for pattern_key, pattern in self.usage_patterns.items():
                if not user_id or pattern.user_id == user_id:
                    insights["efficiency_scores"][pattern_key] = pattern.efficiency_score
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting optimization insights: {e}")
            raise

    async def _generate_recommendations_for_type(self, user_id: str, opt_type: OptimizationType) -> List[OptimizationRecommendation]:
        """Generate recommendations for a specific optimization type"""
        recommendations = []
        
        try:
            if opt_type == OptimizationType.RATE_LIMIT:
                recommendations.extend(await self._generate_rate_limit_recommendations(user_id))
            elif opt_type == OptimizationType.RESOURCE_USAGE:
                recommendations.extend(await self._generate_resource_usage_recommendations(user_id))
            elif opt_type == OptimizationType.COST_EFFICIENCY:
                recommendations.extend(await self._generate_cost_efficiency_recommendations(user_id))
            elif opt_type == OptimizationType.PERFORMANCE:
                recommendations.extend(await self._generate_performance_recommendations(user_id))
            elif opt_type == OptimizationType.SCALABILITY:
                recommendations.extend(await self._generate_scalability_recommendations(user_id))
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations for {opt_type}: {e}")
            return []

    async def _generate_rate_limit_recommendations(self, user_id: str) -> List[OptimizationRecommendation]:
        """Generate rate limit optimization recommendations"""
        recommendations = []
        
        # Analyze user's usage patterns
        user_patterns = [p for p in self.usage_patterns.values() if p.user_id == user_id]
        
        for pattern in user_patterns:
            if pattern.efficiency_score < self.config.efficiency_target:
                rec = OptimizationRecommendation(
                    id=f"rate_limit_{pattern.user_id}_{datetime.now().strftime('%H%M%S')}",
                    type=OptimizationType.RATE_LIMIT,
                    priority=RecommendationPriority.HIGH,
                    title="Optimize Rate Limit Configuration",
                    description=f"Improve efficiency score from {pattern.efficiency_score:.2f} to {self.config.efficiency_target:.2f}",
                    expected_impact=f"{(self.config.efficiency_target - pattern.efficiency_score) * 100:.1f}% efficiency improvement",
                    implementation_effort="Low",
                    metrics=[
                        OptimizationMetric(
                            name="efficiency_score",
                            current_value=pattern.efficiency_score,
                            target_value=self.config.efficiency_target,
                            improvement_percentage=(self.config.efficiency_target - pattern.efficiency_score) / pattern.efficiency_score * 100,
                            unit="score"
                        )
                    ],
                    action_steps=[
                        "Analyze peak usage patterns",
                        "Adjust rate limits based on usage variance",
                        "Implement adaptive throttling",
                        "Monitor efficiency improvements"
                    ]
                )
                recommendations.append(rec)
        
        return recommendations

    async def _generate_resource_usage_recommendations(self, user_id: str) -> List[OptimizationRecommendation]:
        """Generate resource usage optimization recommendations"""
        recommendations = []
        
        # Placeholder for resource usage analysis
        rec = OptimizationRecommendation(
            id=f"resource_{user_id}_{datetime.now().strftime('%H%M%S')}",
            type=OptimizationType.RESOURCE_USAGE,
            priority=RecommendationPriority.MEDIUM,
            title="Optimize Resource Allocation",
            description="Reduce resource waste and improve utilization",
            expected_impact="15-25% resource savings",
            implementation_effort="Medium",
            metrics=[
                OptimizationMetric(
                    name="resource_utilization",
                    current_value=0.65,
                    target_value=0.85,
                    improvement_percentage=30.8,
                    unit="percentage"
                )
            ],
            action_steps=[
                "Analyze current resource usage patterns",
                "Identify underutilized resources",
                "Implement resource pooling",
                "Set up automated scaling"
            ]
        )
        recommendations.append(rec)
        
        return recommendations

    async def _generate_cost_efficiency_recommendations(self, user_id: str) -> List[OptimizationRecommendation]:
        """Generate cost efficiency optimization recommendations"""
        recommendations = []
        
        # Placeholder for cost efficiency analysis
        rec = OptimizationRecommendation(
            id=f"cost_{user_id}_{datetime.now().strftime('%H%M%S')}",
            type=OptimizationType.COST_EFFICIENCY,
            priority=RecommendationPriority.HIGH,
            title="Improve Cost Efficiency",
            description="Optimize spending while maintaining performance",
            expected_impact="20-30% cost reduction",
            implementation_effort="Medium",
            metrics=[
                OptimizationMetric(
                    name="cost_per_request",
                    current_value=0.05,
                    target_value=0.035,
                    improvement_percentage=30.0,
                    unit="USD"
                )
            ],
            action_steps=[
                "Review current spending patterns",
                "Identify cost optimization opportunities",
                "Implement cost-aware routing",
                "Set up budget alerts"
            ]
        )
        recommendations.append(rec)
        
        return recommendations

    async def _generate_performance_recommendations(self, user_id: str) -> List[OptimizationRecommendation]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        # Placeholder for performance analysis
        rec = OptimizationRecommendation(
            id=f"performance_{user_id}_{datetime.now().strftime('%H%M%S')}",
            type=OptimizationType.PERFORMANCE,
            priority=RecommendationPriority.HIGH,
            title="Enhance Performance",
            description="Improve response times and throughput",
            expected_impact="25-40% performance improvement",
            implementation_effort="High",
            metrics=[
                OptimizationMetric(
                    name="response_time",
                    current_value=250,
                    target_value=150,
                    improvement_percentage=40.0,
                    unit="ms"
                )
            ],
            action_steps=[
                "Profile current performance bottlenecks",
                "Implement caching strategies",
                "Optimize database queries",
                "Add performance monitoring"
            ]
        )
        recommendations.append(rec)
        
        return recommendations

    async def _generate_scalability_recommendations(self, user_id: str) -> List[OptimizationRecommendation]:
        """Generate scalability optimization recommendations"""
        recommendations = []
        
        # Placeholder for scalability analysis
        rec = OptimizationRecommendation(
            id=f"scalability_{user_id}_{datetime.now().strftime('%H%M%S')}",
            type=OptimizationType.SCALABILITY,
            priority=RecommendationPriority.MEDIUM,
            title="Improve Scalability",
            description="Enhance system capacity to handle growth",
            expected_impact="50-100% capacity increase",
            implementation_effort="High",
            metrics=[
                OptimizationMetric(
                    name="max_concurrent_users",
                    current_value=1000,
                    target_value=2000,
                    improvement_percentage=100.0,
                    unit="users"
                )
            ],
            action_steps=[
                "Analyze current scalability limits",
                "Design horizontal scaling strategy",
                "Implement load balancing",
                "Set up auto-scaling policies"
            ]
        )
        recommendations.append(rec)
        
        return recommendations

    async def _implement_recommendation(self, recommendation: OptimizationRecommendation) -> bool:
        """Implement a single optimization recommendation"""
        try:
            # Placeholder implementation
            # In a real system, this would interact with various services
            # to implement the actual optimization
            
            logger.info(f"Implementing recommendation {recommendation.id}: {recommendation.title}")
            
            # Simulate implementation time
            await asyncio.sleep(1)
            
            # Store in history
            self.recommendation_history.append(recommendation)
            
            return True
            
        except Exception as e:
            logger.error(f"Error implementing recommendation {recommendation.id}: {e}")
            return False

    def _calculate_timeline(self, recommendations: List[OptimizationRecommendation]) -> str:
        """Calculate implementation timeline for recommendations"""
        effort_mapping = {
            "Low": 1,
            "Medium": 3,
            "High": 7
        }
        
        total_days = sum(effort_mapping.get(r.implementation_effort, 3) for r in recommendations)
        
        if total_days <= 7:
            return f"{total_days} days"
        elif total_days <= 30:
            return f"{total_days // 7} weeks"
        else:
            return f"{total_days // 30} months"

    async def _usage_analysis_loop(self):
        """Background loop for usage pattern analysis"""
        while self.is_running:
            try:
                # Analyze usage patterns for all users
                # This would integrate with actual usage data sources
                await asyncio.sleep(self.config.analysis_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in usage analysis loop: {e}")
                await asyncio.sleep(60)

    async def _recommendation_generation_loop(self):
        """Background loop for generating recommendations"""
        while self.is_running:
            try:
                # Generate recommendations for users with low efficiency
                for pattern in self.usage_patterns.values():
                    if pattern.efficiency_score < self.config.efficiency_target:
                        await self.generate_optimization_plan(pattern.user_id)
                
                await asyncio.sleep(self.config.analysis_interval * 2)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in recommendation generation loop: {e}")
                await asyncio.sleep(60)

    async def _cleanup_loop(self):
        """Background loop for cleanup operations"""
        while self.is_running:
            try:
                # Clean up old data
                cutoff_time = datetime.now() - timedelta(days=30)
                
                # Clean up old results
                self.optimization_results = [
                    r for r in self.optimization_results 
                    if r.timestamp > cutoff_time
                ]
                
                # Clean up old patterns
                self.usage_patterns = {
                    k: v for k, v in self.usage_patterns.items()
                    if v.last_updated > cutoff_time
                }
                
                await asyncio.sleep(3600)  # Run cleanup every hour
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(300)

# Global instance
_usage_optimizer_instance: Optional[UsageOptimizer] = None

def get_usage_optimizer() -> UsageOptimizer:
    """Get the global usage optimizer instance"""
    global _usage_optimizer_instance
    if _usage_optimizer_instance is None:
        _usage_optimizer_instance = UsageOptimizer()
    return _usage_optimizer_instance

# Utility functions
async def analyze_user_usage(user_id: str, usage_data: Dict[str, Any]) -> UsagePattern:
    """Analyze usage patterns for a user"""
    optimizer = get_usage_optimizer()
    return await optimizer.analyze_usage_patterns(user_id, usage_data)

async def create_optimization_plan(user_id: str, optimization_types: List[OptimizationType] = None) -> OptimizationPlan:
    """Create optimization plan for a user"""
    optimizer = get_usage_optimizer()
    return await optimizer.generate_optimization_plan(user_id, optimization_types)

async def implement_optimization_plan(plan_id: str, recommendation_ids: List[str] = None) -> OptimizationResult:
    """Implement optimization plan"""
    optimizer = get_usage_optimizer()
    return await optimizer.implement_optimization(plan_id, recommendation_ids)

async def get_optimization_dashboard(user_id: str = None) -> Dict[str, Any]:
    """Get optimization dashboard data"""
    optimizer = get_usage_optimizer()
    return await optimizer.get_optimization_insights(user_id)
