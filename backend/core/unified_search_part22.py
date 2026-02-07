"""
Part 22: Advanced Query Planning and Optimization
RaptorFlow Unified Search System - Industrial Grade AI Agent Search Infrastructure
===============================================================================
This module implements advanced query planning, optimization strategies, and
intelligent query execution for maximum search performance and relevance.
"""

import asyncio
import json
import logging
import math
import statistics
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from core.unified_search_part1 import ContentType, SearchMode, SearchQuery, SearchResult
from core.unified_search_part2 import SearchProvider
from core.unified_search_part16 import (
    QueryAnalysis,
    QueryAnalyzer,
    QueryOptimizer,
    SearchPlan,
)
from core.unified_search_part17 import ml_manager

logger = logging.getLogger("raptorflow.unified_search.planning")


class PlanningStrategy(Enum):
    """Query planning strategies."""

    CONSERVATIVE = "conservative"
    AGGRESSIVE = "aggressive"
    BALANCED = "balanced"
    ADAPTIVE = "adaptive"
    COST_OPTIMIZED = "cost_optimized"
    LATENCY_OPTIMIZED = "latency_optimized"
    QUALITY_OPTIMIZED = "quality_optimized"


class ExecutionPhase(Enum):
    """Query execution phases."""

    PLANNING = "planning"
    PREPARATION = "preparation"
    EXECUTION = "execution"
    CONSOLIDATION = "consolidation"
    POST_PROCESSING = "post_processing"
    COMPLETION = "completion"


@dataclass
class QueryCost:
    """Query execution cost estimation."""

    cpu_cost: float
    memory_cost: float
    network_cost: float
    api_cost: float
    time_cost_ms: float
    confidence: float
    factors: Dict[str, float] = field(default_factory=dict)

    def total_cost(self) -> float:
        """Calculate total cost."""
        return self.cpu_cost + self.memory_cost + self.network_cost + self.api_cost

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "cpu_cost": self.cpu_cost,
            "memory_cost": self.memory_cost,
            "network_cost": self.network_cost,
            "api_cost": self.api_cost,
            "time_cost_ms": self.time_cost_ms,
            "total_cost": self.total_cost(),
            "confidence": self.confidence,
            "factors": self.factors,
        }


@dataclass
class ExecutionStep:
    """Single step in query execution plan."""

    step_id: str
    phase: ExecutionPhase
    operation: str
    parameters: Dict[str, Any]
    dependencies: List[str]
    estimated_cost: QueryCost
    parallelizable: bool
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: float = 30.0
    status: str = "pending"
    result: Optional[Any] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "step_id": self.step_id,
            "phase": self.phase.value,
            "operation": self.operation,
            "parameters": self.parameters,
            "dependencies": self.dependencies,
            "estimated_cost": self.estimated_cost.to_dict(),
            "parallelizable": self.parallelizable,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "timeout_seconds": self.timeout_seconds,
            "status": self.status,
            "error": self.error,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
        }

    @property
    def duration_ms(self) -> Optional[float]:
        """Get step duration in milliseconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return None

    @property
    def is_completed(self) -> bool:
        """Check if step is completed."""
        return self.status in ["completed", "failed"]

    @property
    def can_execute(self) -> bool:
        """Check if step can be executed."""
        return self.status == "pending" and self.retry_count < self.max_retries


@dataclass
class ExecutionPlan:
    """Complete query execution plan."""

    plan_id: str
    query: SearchQuery
    analysis: Optional[QueryAnalysis]
    strategy: PlanningStrategy
    steps: List[ExecutionStep]
    total_estimated_cost: QueryCost
    estimated_duration_ms: float
    confidence_score: float
    optimization_applied: List[str]
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "plan_id": self.plan_id,
            "query": {
                "text": self.query.text,
                "mode": self.query.mode.value,
                "max_results": self.query.max_results,
            },
            "analysis": self.analysis.to_dict() if self.analysis else None,
            "strategy": self.strategy.value,
            "steps": [step.to_dict() for step in self.steps],
            "total_estimated_cost": self.total_estimated_cost.to_dict(),
            "estimated_duration_ms": self.estimated_duration_ms,
            "confidence_score": self.confidence_score,
            "optimization_applied": self.optimization_applied,
            "created_at": self.created_at.isoformat(),
        }

    def get_steps_by_phase(self, phase: ExecutionPhase) -> List[ExecutionStep]:
        """Get steps by execution phase."""
        return [step for step in self.steps if step.phase == phase]

    def get_ready_steps(self) -> List[ExecutionStep]:
        """Get steps ready for execution."""
        ready_steps = []

        for step in self.steps:
            if not step.can_execute:
                continue

            # Check if dependencies are completed
            dependencies_met = True
            for dep_id in step.dependencies:
                dep_step = self._find_step(dep_id)
                if not dep_step or dep_step.status != "completed":
                    dependencies_met = False
                    break

            if dependencies_met:
                ready_steps.append(step)

        return ready_steps

    def _find_step(self, step_id: str) -> Optional[ExecutionStep]:
        """Find step by ID."""
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None


class CostEstimator:
    """Estimates query execution costs."""

    def __init__(self):
        self.base_costs = {
            "search_query": {"cpu": 0.1, "memory": 0.05, "network": 0.02, "time": 500},
            "result_processing": {
                "cpu": 0.05,
                "memory": 0.1,
                "network": 0.01,
                "time": 200,
            },
            "content_extraction": {
                "cpu": 0.2,
                "memory": 0.15,
                "network": 0.1,
                "time": 1000,
            },
            "result_ranking": {
                "cpu": 0.15,
                "memory": 0.08,
                "network": 0.01,
                "time": 300,
            },
            "cache_lookup": {"cpu": 0.01, "memory": 0.02, "network": 0.005, "time": 50},
            "ml_inference": {"cpu": 0.3, "memory": 0.2, "network": 0.05, "time": 800},
        }

        self.provider_costs = {
            SearchProvider.NATIVE: {"api": 0.0, "network": 0.01},
            SearchProvider.SERPER: {"api": 0.002, "network": 0.02},
            SearchProvider.BRAVE: {"api": 0.001, "network": 0.015},
            SearchProvider.DUCKDUCKGO: {"api": 0.0, "network": 0.01},
        }

        self.mode_multipliers = {
            SearchMode.LIGHTNING: 0.5,
            SearchMode.STANDARD: 1.0,
            SearchMode.DEEP: 2.0,
            SearchMode.EXHAUSTIVE: 4.0,
        }

    def estimate_step_cost(
        self, operation: str, parameters: Dict[str, Any]
    ) -> QueryCost:
        """Estimate cost for execution step."""
        base_cost = self.base_costs.get(operation, self.base_costs["search_query"])

        # Apply multipliers based on parameters
        cpu_cost = base_cost["cpu"]
        memory_cost = base_cost["memory"]
        network_cost = base_cost["network"]
        time_cost = base_cost["time"]

        # Mode multiplier
        mode = parameters.get("mode", SearchMode.STANDARD)
        mode_multiplier = self.mode_multipliers.get(mode, 1.0)

        cpu_cost *= mode_multiplier
        memory_cost *= mode_multiplier
        time_cost *= mode_multiplier

        # Result count multiplier
        max_results = parameters.get("max_results", 10)
        result_multiplier = min(2.0, max_results / 10.0)

        cpu_cost *= result_multiplier
        memory_cost *= result_multiplier
        network_cost *= result_multiplier

        # Provider costs
        providers = parameters.get("providers", [SearchProvider.NATIVE])
        api_cost = 0.0
        for provider in providers:
            provider_cost = self.provider_costs.get(
                provider, {"api": 0.0, "network": 0.0}
            )
            api_cost += provider_cost["api"]
            network_cost += provider_cost["network"]

        # Content type costs
        content_types = parameters.get("content_types", [ContentType.WEB])
        if ContentType.ACADEMIC in content_types:
            cpu_cost *= 1.2
            time_cost *= 1.3
        if ContentType.NEWS in content_types:
            network_cost *= 1.1

        # Calculate confidence based on operation complexity
        confidence = 0.8
        if operation in ["ml_inference", "content_extraction"]:
            confidence = 0.6
        elif operation in ["cache_lookup", "search_query"]:
            confidence = 0.9

        return QueryCost(
            cpu_cost=cpu_cost,
            memory_cost=memory_cost,
            network_cost=network_cost,
            api_cost=api_cost,
            time_cost_ms=time_cost,
            confidence=confidence,
            factors={
                "mode_multiplier": mode_multiplier,
                "result_multiplier": result_multiplier,
                "provider_count": len(providers),
            },
        )

    def estimate_plan_cost(self, steps: List[ExecutionStep]) -> Tuple[QueryCost, float]:
        """Estimate total cost for execution plan."""
        total_cpu = 0.0
        total_memory = 0.0
        total_network = 0.0
        total_api = 0.0
        total_time = 0.0
        confidence_sum = 0.0

        for step in steps:
            cost = step.estimated_cost
            total_cpu += cost.cpu_cost
            total_memory += cost.memory_cost
            total_network += cost.network_cost
            total_api += cost.api_cost
            total_time += cost.time_cost_ms
            confidence_sum += cost.confidence

        # Adjust for parallel execution
        parallel_steps = [step for step in steps if step.parallelizable]
        if parallel_steps:
            # Parallel steps can overlap in time
            parallel_time = max(
                step.estimated_cost.time_cost_ms for step in parallel_steps
            )
            sequential_steps = [step for step in steps if not step.parallelizable]
            sequential_time = sum(
                step.estimated_cost.time_cost_ms for step in sequential_steps
            )
            total_time = parallel_time + sequential_time

        avg_confidence = confidence_sum / len(steps) if steps else 0.0

        total_cost = QueryCost(
            cpu_cost=total_cpu,
            memory_cost=total_memory,
            network_cost=total_network,
            api_cost=total_api,
            time_cost_ms=total_time,
            confidence=avg_confidence,
        )

        return total_cost, total_time


class QueryPlanner:
    """Advanced query planner."""

    def __init__(self):
        self.query_analyzer = QueryAnalyzer()
        self.query_optimizer = QueryOptimizer()
        self.cost_estimator = CostEstimator()
        self.ml_manager = ml_manager
        self.planning_history = deque(maxlen=1000)

    async def create_execution_plan(
        self,
        query: SearchQuery,
        strategy: PlanningStrategy = PlanningStrategy.ADAPTIVE,
        constraints: Optional[Dict[str, Any]] = None,
    ) -> ExecutionPlan:
        """Create optimized execution plan."""
        plan_id = str(uuid.uuid4())

        # Analyze query
        analysis = await self.query_analyzer.analyze_query(query)

        # Generate base plan steps
        steps = await self._generate_plan_steps(query, analysis, strategy, constraints)

        # Estimate costs
        total_cost, estimated_duration = self.cost_estimator.estimate_plan_cost(steps)

        # Apply optimizations
        optimizations = await self._apply_optimizations(steps, strategy, constraints)

        # Calculate confidence score
        confidence_score = self._calculate_plan_confidence(steps, analysis)

        plan = ExecutionPlan(
            plan_id=plan_id,
            query=query,
            analysis=analysis,
            strategy=strategy,
            steps=steps,
            total_estimated_cost=total_cost,
            estimated_duration_ms=estimated_duration,
            confidence_score=confidence_score,
            optimization_applied=optimizations,
        )

        # Record planning history
        self.planning_history.append(
            {
                "timestamp": datetime.now(),
                "plan_id": plan_id,
                "query_text": query.text,
                "strategy": strategy.value,
                "estimated_cost": total_cost.total_cost(),
                "estimated_duration": estimated_duration,
                "confidence": confidence_score,
            }
        )

        logger.info(f"Created execution plan {plan_id} with {len(steps)} steps")
        return plan

    async def _generate_plan_steps(
        self,
        query: SearchQuery,
        analysis: QueryAnalysis,
        strategy: PlanningStrategy,
        constraints: Optional[Dict[str, Any]],
    ) -> List[ExecutionStep]:
        """Generate base execution steps."""
        steps = []
        step_counter = 0

        def create_step_id() -> str:
            nonlocal step_counter
            step_counter += 1
            return f"step_{step_counter}"

        # Step 1: Cache lookup
        cache_step = ExecutionStep(
            step_id=create_step_id(),
            phase=ExecutionPhase.PREPARATION,
            operation="cache_lookup",
            parameters={
                "query_text": query.text,
                "mode": query.mode,
                "content_types": query.content_types,
            },
            dependencies=[],
            estimated_cost=self.cost_estimator.estimate_step_cost(
                "cache_lookup", {"mode": query.mode, "max_results": query.max_results}
            ),
            parallelizable=False,
        )
        steps.append(cache_step)

        # Step 2: Query optimization (if needed)
        if analysis.complexity > 0.5 or strategy in [
            PlanningStrategy.QUALITY_OPTIMIZED,
            PlanningStrategy.AGGRESSIVE,
        ]:
            optimize_step = ExecutionStep(
                step_id=create_step_id(),
                phase=ExecutionPhase.PLANNING,
                operation="query_optimization",
                parameters={
                    "query_text": query.text,
                    "analysis": analysis.to_dict(),
                    "strategy": strategy.value,
                },
                dependencies=[cache_step.step_id],
                estimated_cost=self.cost_estimator.estimate_step_cost(
                    "result_processing",
                    {"mode": query.mode, "max_results": query.max_results},
                ),
                parallelizable=False,
            )
            steps.append(optimize_step)

        # Step 3: Primary search execution
        search_step = ExecutionStep(
            step_id=create_step_id(),
            phase=ExecutionPhase.EXECUTION,
            operation="search_query",
            parameters={
                "query_text": query.text,
                "mode": query.mode,
                "max_results": query.max_results,
                "content_types": query.content_types,
                "providers": self._select_providers(query, analysis, strategy),
            },
            dependencies=[cache_step.step_id],
            estimated_cost=self.cost_estimator.estimate_step_cost(
                "search_query",
                {
                    "mode": query.mode,
                    "max_results": query.max_results,
                    "providers": self._select_providers(query, analysis, strategy),
                },
            ),
            parallelizable=True,
        )
        steps.append(search_step)

        # Step 4: Content extraction (if deep search)
        if query.mode in [SearchMode.DEEP, SearchMode.EXHAUSTIVE]:
            extract_step = ExecutionStep(
                step_id=create_step_id(),
                phase=ExecutionPhase.EXECUTION,
                operation="content_extraction",
                parameters={
                    "max_urls": min(20, query.max_results * 2),
                    "depth": 2 if query.mode == SearchMode.EXHAUSTIVE else 1,
                },
                dependencies=[search_step.step_id],
                estimated_cost=self.cost_estimator.estimate_step_cost(
                    "content_extraction",
                    {"mode": query.mode, "max_results": query.max_results},
                ),
                parallelizable=True,
            )
            steps.append(extract_step)

        # Step 5: ML inference (if available and beneficial)
        if (
            self.ml_manager.get_model_status()
            .get("ranking_model", {})
            .get("is_trained", False)
        ):
            ml_step = ExecutionStep(
                step_id=create_step_id(),
                phase=ExecutionPhase.POST_PROCESSING,
                operation="ml_inference",
                parameters={
                    "model_type": "ranking_model",
                    "features": "query_and_results",
                },
                dependencies=[search_step.step_id],
                estimated_cost=self.cost_estimator.estimate_step_cost(
                    "ml_inference",
                    {"mode": query.mode, "max_results": query.max_results},
                ),
                parallelizable=False,
            )
            steps.append(ml_step)

        # Step 6: Result consolidation
        consolidate_step = ExecutionStep(
            step_id=create_step_id(),
            phase=ExecutionPhase.CONSOLIDATION,
            operation="result_processing",
            parameters={
                "deduplication": True,
                "ranking": True,
                "max_results": query.max_results,
            },
            dependencies=[search_step.step_id],
            estimated_cost=self.cost_estimator.estimate_step_cost(
                "result_processing",
                {"mode": query.mode, "max_results": query.max_results},
            ),
            parallelizable=False,
        )
        steps.append(consolidate_step)

        # Step 7: Final result processing
        final_step = ExecutionStep(
            step_id=create_step_id(),
            phase=ExecutionPhase.POST_PROCESSING,
            operation="result_processing",
            parameters={"formatting": True, "metadata_enrichment": True},
            dependencies=[consolidate_step.step_id],
            estimated_cost=self.cost_estimator.estimate_step_cost(
                "result_processing",
                {"mode": query.mode, "max_results": query.max_results},
            ),
            parallelizable=False,
        )
        steps.append(final_step)

        return steps

    def _select_providers(
        self, query: SearchQuery, analysis: QueryAnalysis, strategy: PlanningStrategy
    ) -> List[SearchProvider]:
        """Select optimal providers for query."""
        providers = [SearchProvider.NATIVE]  # Always include native

        # Strategy-based selection
        if strategy == PlanningStrategy.COST_OPTIMIZED:
            # Use only free providers
            providers.extend([SearchProvider.DUCKDUCKGO])
        elif strategy == PlanningStrategy.QUALITY_OPTIMIZED:
            # Use all available providers
            providers.extend(
                [SearchProvider.SERPER, SearchProvider.BRAVE, SearchProvider.DUCKDUCKGO]
            )
        elif strategy == PlanningStrategy.LATENCY_OPTIMIZED:
            # Use fastest providers
            providers.extend([SearchProvider.NATIVE, SearchProvider.DUCKDUCKGO])
        else:
            # Balanced approach
            providers.extend([SearchProvider.SERPER, SearchProvider.BRAVE])

        # Intent-based selection
        if analysis.intent.value in ["research", "academic"]:
            if SearchProvider.SERPER not in providers:
                providers.append(SearchProvider.SERPER)

        return providers

    async def _apply_optimizations(
        self,
        steps: List[ExecutionStep],
        strategy: PlanningStrategy,
        constraints: Optional[Dict[str, Any]],
    ) -> List[str]:
        """Apply optimizations to execution plan."""
        optimizations = []

        # Parallel optimization
        parallelizable_steps = [step for step in steps if step.parallelizable]
        if len(parallelizable_steps) > 1:
            # Can run parallel steps concurrently
            optimizations.append("parallel_execution")

        # Cost optimization
        if strategy == PlanningStrategy.COST_OPTIMIZED:
            # Remove expensive steps
            expensive_steps = [
                step for step in steps if step.estimated_cost.total_cost() > 0.5
            ]
            for step in expensive_steps:
                if step.operation in ["ml_inference", "content_extraction"]:
                    steps.remove(step)
                    optimizations.append(f"removed_expensive_step_{step.operation}")

        # Latency optimization
        if strategy == PlanningStrategy.LATENCY_OPTIMIZED:
            # Prioritize fast steps
            for step in steps:
                if step.estimated_cost.time_cost_ms > 2000:
                    step.timeout_seconds = min(step.timeout_seconds, 5.0)
            optimizations.append("reduced_timeouts")

        # Quality optimization
        if strategy == PlanningStrategy.QUALITY_OPTIMIZED:
            # Add quality-focused steps
            if not any(step.operation == "ml_inference" for step in steps):
                ml_step = ExecutionStep(
                    step_id=f"ml_step_{uuid.uuid4().hex[:8]}",
                    phase=ExecutionPhase.POST_PROCESSING,
                    operation="ml_inference",
                    parameters={"model_type": "ranking_model"},
                    dependencies=[steps[0].step_id],  # After cache lookup
                    estimated_cost=self.cost_estimator.estimate_step_cost(
                        "ml_inference", {}
                    ),
                    parallelizable=False,
                )
                steps.append(ml_step)
                optimizations.append("added_ml_ranking")

        # Constraint-based optimization
        if constraints:
            max_cost = constraints.get("max_cost")
            if max_cost:
                total_cost = sum(step.estimated_cost.total_cost() for step in steps)
                if total_cost > max_cost:
                    # Remove least important steps
                    steps.sort(
                        key=lambda s: s.estimated_cost.total_cost(), reverse=True
                    )
                    while total_cost > max_cost and steps:
                        removed = steps.pop()
                        total_cost -= removed.estimated_cost.total_cost()
                        optimizations.append(
                            f"removed_step_for_cost_{removed.operation}"
                        )

        return optimizations

    def _calculate_plan_confidence(
        self, steps: List[ExecutionStep], analysis: QueryAnalysis
    ) -> float:
        """Calculate confidence score for execution plan."""
        confidence_factors = []

        # Step confidence
        step_confidences = [step.estimated_cost.confidence for step in steps]
        avg_step_confidence = (
            statistics.mean(step_confidences) if step_confidences else 0.5
        )
        confidence_factors.append(avg_step_confidence)

        # Analysis confidence
        if analysis:
            confidence_factors.append(analysis.confidence)

        # Historical performance
        if self.planning_history:
            recent_plans = list(self.planning_history)[-10:]
            success_rate = 0.8  # Mock success rate
            confidence_factors.append(success_rate)

        # Plan complexity
        complexity_penalty = min(0.2, len(steps) / 50.0)
        confidence_factors.append(1.0 - complexity_penalty)

        # Weighted average
        weights = [0.4, 0.3, 0.2, 0.1]  # Step confidence, analysis, history, complexity
        weighted_confidence = sum(w * c for w, c in zip(weights, confidence_factors))

        return max(0.0, min(1.0, weighted_confidence))

    def get_planning_stats(self) -> Dict[str, Any]:
        """Get planning statistics."""
        if not self.planning_history:
            return {"message": "No planning history available"}

        recent_plans = list(self.planning_history)[-100:]

        strategy_counts = defaultdict(int)
        avg_costs = []
        avg_durations = []
        avg_confidences = []

        for plan in recent_plans:
            strategy_counts[plan["strategy"]] += 1
            avg_costs.append(plan["estimated_cost"])
            avg_durations.append(plan["estimated_duration"])
            avg_confidences.append(plan["confidence"])

        return {
            "total_plans": len(recent_plans),
            "strategy_distribution": dict(strategy_counts),
            "avg_estimated_cost": statistics.mean(avg_costs) if avg_costs else 0,
            "avg_estimated_duration": (
                statistics.mean(avg_durations) if avg_durations else 0
            ),
            "avg_confidence": (
                statistics.mean(avg_confidences) if avg_confidences else 0
            ),
            "planning_frequency": len(recent_plans) / 24,  # Plans per hour (last 24h)
        }


class PlanExecutor:
    """Executes query execution plans."""

    def __init__(self):
        self.active_plans: Dict[str, ExecutionPlan] = {}
        self.execution_history = deque(maxlen=1000)
        self.max_concurrent_steps = 10
        self._execution_semaphore = asyncio.Semaphore(self.max_concurrent_steps)

    async def execute_plan(self, plan: ExecutionPlan) -> List[SearchResult]:
        """Execute execution plan and return results."""
        self.active_plans[plan.plan_id] = plan

        try:
            results = await self._execute_plan_steps(plan)

            # Record execution
            self.execution_history.append(
                {
                    "timestamp": datetime.now(),
                    "plan_id": plan.plan_id,
                    "query_text": plan.query.text,
                    "strategy": plan.strategy.value,
                    "success": True,
                    "duration_ms": sum(step.duration_ms or 0 for step in plan.steps),
                    "steps_completed": len(
                        [s for s in plan.steps if s.status == "completed"]
                    ),
                }
            )

            return results

        except Exception as e:
            # Record failure
            self.execution_history.append(
                {
                    "timestamp": datetime.now(),
                    "plan_id": plan.plan_id,
                    "query_text": plan.query.text,
                    "strategy": plan.strategy.value,
                    "success": False,
                    "error": str(e),
                }
            )

            raise

        finally:
            self.active_plans.pop(plan.plan_id, None)

    async def _execute_plan_steps(self, plan: ExecutionPlan) -> List[SearchResult]:
        """Execute all steps in the plan."""
        completed_steps = 0
        total_steps = len(plan.steps)

        while completed_steps < total_steps:
            # Get ready steps
            ready_steps = plan.get_ready_steps()

            if not ready_steps:
                # Check for deadlocks
                pending_steps = [
                    step for step in plan.steps if step.status == "pending"
                ]
                if pending_steps:
                    raise RuntimeError(
                        f"Execution deadlock: {len(pending_steps)} pending steps"
                    )
                break

            # Execute ready steps (parallel if possible)
            parallel_groups = self._group_parallel_steps(ready_steps)

            for group in parallel_groups:
                if len(group) == 1:
                    await self._execute_step(plan, group[0])
                else:
                    await asyncio.gather(
                        *[self._execute_step(plan, step) for step in group]
                    )

            completed_steps = len(
                [step for step in plan.steps if step.status == "completed"]
            )

        # Collect final results
        final_step = None
        for step in reversed(plan.steps):
            if step.status == "completed" and step.result:
                final_step = step
                break

        if final_step and final_step.result:
            return final_step.result

        return []

    def _group_parallel_steps(
        self, steps: List[ExecutionStep]
    ) -> List[List[ExecutionStep]]:
        """Group steps that can be executed in parallel."""
        groups = []
        remaining_steps = steps.copy()

        while remaining_steps:
            current_group = []
            step_iter = remaining_steps.copy()

            for step in step_iter:
                # Check if step can run with current group
                can_parallel = True

                for group_step in current_group:
                    if not step.parallelizable or not group_step.parallelizable:
                        can_parallel = False
                        break

                    # Check for dependency conflicts
                    if (
                        group_step.step_id in step.dependencies
                        or step.step_id in group_step.dependencies
                    ):
                        can_parallel = False
                        break

                if can_parallel:
                    current_group.append(step)
                    remaining_steps.remove(step)

            if current_group:
                groups.append(current_group)
            else:
                # No more parallel grouping possible
                groups.append([remaining_steps.pop(0)])

        return groups

    async def _execute_step(self, plan: ExecutionPlan, step: ExecutionStep):
        """Execute individual step."""
        async with self._execution_semaphore:
            step.status = "running"
            step.start_time = datetime.now()

            try:
                # Execute step based on operation
                if step.operation == "cache_lookup":
                    step.result = await self._execute_cache_lookup(step)
                elif step.operation == "search_query":
                    step.result = await self._execute_search_query(step, plan.query)
                elif step.operation == "content_extraction":
                    step.result = await self._execute_content_extraction(step)
                elif step.operation == "ml_inference":
                    step.result = await self._execute_ml_inference(step, plan.query)
                elif step.operation == "result_processing":
                    step.result = await self._execute_result_processing(step)
                else:
                    raise ValueError(f"Unknown operation: {step.operation}")

                step.status = "completed"
                step.end_time = datetime.now()

            except Exception as e:
                step.error = str(e)
                step.status = "failed"
                step.end_time = datetime.now()
                step.retry_count += 1

                # Retry if possible
                if step.retry_count < step.max_retries:
                    step.status = "pending"
                    logger.warning(f"Step {step.step_id} failed, retrying: {e}")
                else:
                    logger.error(f"Step {step.step_id} failed permanently: {e}")
                    raise

    async def _execute_cache_lookup(
        self, step: ExecutionStep
    ) -> Optional[List[SearchResult]]:
        """Execute cache lookup step."""
        # Mock cache lookup
        await asyncio.sleep(0.01)  # Simulate cache access time
        return None  # Cache miss

    async def _execute_search_query(
        self, step: ExecutionStep, query: SearchQuery
    ) -> List[SearchResult]:
        """Execute search query step."""
        # Mock search execution
        await asyncio.sleep(0.5)  # Simulate search time

        # Generate mock results
        results = []
        for i in range(min(query.max_results, 10)):
            result = SearchResult(
                url=f"https://example.com/result{i+1}",
                title=f"Result {i+1} for: {query.text}",
                content=f"Mock content for {query.text}",
                snippet=f"Mock snippet for {query.text}",
                provider=SearchProvider.NATIVE,
                relevance_score=0.9 - (i * 0.1),
            )
            results.append(result)

        return results

    async def _execute_content_extraction(
        self, step: ExecutionStep
    ) -> List[Dict[str, Any]]:
        """Execute content extraction step."""
        # Mock content extraction
        await asyncio.sleep(1.0)  # Simulate extraction time

        return [{"url": "https://example.com", "content": "Extracted content"}]

    async def _execute_ml_inference(
        self, step: ExecutionStep, query: SearchQuery
    ) -> List[float]:
        """Execute ML inference step."""
        # Mock ML inference
        await asyncio.sleep(0.2)  # Simulate inference time

        return [0.9, 0.8, 0.7, 0.6, 0.5]  # Mock relevance scores

    async def _execute_result_processing(
        self, step: ExecutionStep
    ) -> List[SearchResult]:
        """Execute result processing step."""
        # Mock result processing
        await asyncio.sleep(0.1)  # Simulate processing time

        # Return processed results (would get from previous steps)
        return []

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        if not self.execution_history:
            return {"message": "No execution history available"}

        recent_executions = list(self.execution_history)[-100:]

        success_count = sum(1 for exec_ in recent_executions if exec_["success"])
        strategy_counts = defaultdict(int)
        avg_durations = []

        for exec_ in recent_executions:
            strategy_counts[exec_["strategy"]] += 1
            if exec_["success"] and "duration_ms" in exec_:
                avg_durations.append(exec_["duration_ms"])

        return {
            "total_executions": len(recent_executions),
            "success_rate": (
                success_count / len(recent_executions) if recent_executions else 0
            ),
            "strategy_distribution": dict(strategy_counts),
            "avg_duration_ms": statistics.mean(avg_durations) if avg_durations else 0,
            "active_plans": len(self.active_plans),
        }


# Global components
query_planner = QueryPlanner()
plan_executor = PlanExecutor()
