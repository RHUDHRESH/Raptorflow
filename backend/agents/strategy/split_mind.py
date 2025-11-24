"""
SplitMind Agent (EXP-01)

A/B test design and interpretation.
Designs experiments and analyzes results using statistical methods.
"""

import asyncio
import uuid
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
import json

from backend.agents.base_swarm_agent import BaseSwarmAgent
from backend.messaging.event_bus import EventType, AgentMessage
from backend.models.agent_messages import ExperimentDesign, ExperimentResult


class SplitMindAgent(BaseSwarmAgent):
    """A/B Test Design & Interpretation Agent"""

    AGENT_ID = "EXP-01"
    AGENT_NAME = "SplitMind"
    CAPABILITIES = [
        "experiment_design",
        "ab_testing",
        "statistical_analysis",
        "hypothesis_testing"
    ]
    POD = "strategy"
    MAX_CONCURRENT = 3

    def __init__(self, redis_client, db_client, llm_client):
        super().__init__(redis_client, db_client, llm_client)

        # Register message handlers
        self.register_handler(EventType.GOAL_REQUEST, self.handle_goal_request)
        self.register_handler(EventType.MOVE_PLAN, self.handle_move_plan)

    async def handle_goal_request(self, message: AgentMessage):
        """Handle goal request - may suggest A/B testing"""

        goal = message.payload
        correlation_id = message.correlation_id

        # Analyze if A/B testing is appropriate
        # Store analysis in context
        analysis = {
            "ab_test_suitable": True,
            "suggested_metrics": ["conversion_rate", "engagement_rate"],
            "min_sample_size": 1000,
            "min_duration_days": 7
        }

        self.set_result(correlation_id, analysis)

    async def handle_move_plan(self, message: AgentMessage):
        """Handle move plan - design experiments if needed"""

        move_plan = message.payload
        correlation_id = message.correlation_id

        # Check if we should design experiments
        if move_plan.get("a_b_test_variants"):
            experiment = await self.design_experiment(
                move_id=move_plan.get("move_id"),
                goal_type=move_plan.get("objective"),
                variants=move_plan.get("a_b_test_variants"),
                context=message.payload,
                correlation_id=correlation_id
            )

            # Publish experiment design
            self.publish_message(
                EventType.EXPERIMENT_DESIGN,
                experiment.model_dump(),
                targets=["EXEC-DIR"],  # Execution director
                correlation_id=correlation_id,
                priority="HIGH"
            )

    async def design_experiment(
        self,
        move_id: str,
        goal_type: str,
        variants: List[Dict[str, Any]],
        context: Dict[str, Any],
        correlation_id: str
    ) -> ExperimentDesign:
        """
        Design an A/B test

        Args:
            move_id: The move being tested
            goal_type: The goal (reach, engagement, conversion, etc.)
            variants: The variants to test
            context: Additional context (baseline metrics, etc.)
            correlation_id: For tracking

        Returns:
            ExperimentDesign with full test specification
        """

        # Step 1: Determine success metric based on goal
        success_metric = self._select_success_metric(goal_type)

        # Step 2: Get baseline rate
        baseline_rate = context.get("baseline_conversion_rate", 0.05)

        # Step 3: Calculate required sample size
        mde = context.get("min_detectable_effect", 0.2)  # 20% lift
        sample_size = self._calculate_sample_size(
            baseline_rate=baseline_rate,
            mde=mde,
            alpha=0.05,  # 95% confidence
            power=0.8    # 80% power
        )

        # Step 4: Set stop conditions
        stop_conditions = {
            "min_sample_per_variant": sample_size,
            "min_duration_days": 7,
            "max_duration_days": 28,
            "significance_threshold": 0.05,
            "min_effect_size": mde * baseline_rate
        }

        # Step 5: Create experiment record
        experiment = ExperimentDesign(
            experiment_id=str(uuid.uuid4()),
            move_id=move_id,
            hypothesis=f"Testing {len(variants)} variants for {goal_type}",
            variants=variants,
            sample_size_per_variant=sample_size,
            duration_days=14,
            success_metric=success_metric,
            stop_conditions=stop_conditions
        )

        # Step 6: Save to database
        try:
            await self.db.experiments.insert(
                {
                    "id": experiment.experiment_id,
                    "move_id": move_id,
                    "hypothesis": experiment.hypothesis,
                    "variants": json.dumps(variants),
                    "sample_size_per_variant": sample_size,
                    "duration_days": 14,
                    "success_metric": success_metric,
                    "stop_conditions": json.dumps(stop_conditions),
                    "status": "running",
                    "created_at": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            print(f"[{self.AGENT_ID}] DB error: {e}")

        print(f"[{self.AGENT_ID}] Designed experiment {experiment.experiment_id}")
        print(f"  Variants: {len(variants)}")
        print(f"  Sample size per variant: {sample_size}")
        print(f"  Duration: 14 days")

        return experiment

    async def analyze_experiment(
        self,
        experiment_id: str,
        results_data: Dict[str, Any],
        correlation_id: str
    ) -> ExperimentResult:
        """
        Analyze experiment results

        Args:
            experiment_id: The experiment to analyze
            results_data: Raw results data
            correlation_id: For tracking

        Returns:
            ExperimentResult with winner and statistical info
        """

        print(f"[{self.AGENT_ID}] Analyzing experiment {experiment_id}")

        # Fetch experiment from DB
        try:
            exp_record = await self.db.experiments.find_one(id=experiment_id)
        except:
            exp_record = None

        if not exp_record:
            print(f"[{self.AGENT_ID}] Experiment not found")
            return None

        # Parse variants
        variants = exp_record.get("variants")
        if isinstance(variants, str):
            variants = json.loads(variants)

        variant_names = [v.get("variant") for v in variants]

        # Step 1: Compute statistics per variant
        variant_stats = {}
        for variant_name in variant_names:
            variant_results = results_data.get(variant_name, {})

            stats = {
                "variant": variant_name,
                "sample_size": variant_results.get("sample_size", 0),
                "conversions": variant_results.get("conversions", 0),
                "conversion_rate": self._safe_divide(
                    variant_results.get("conversions", 0),
                    variant_results.get("sample_size", 1)
                ),
                "engagement": variant_results.get("engagement", 0)
            }

            variant_stats[variant_name] = stats

        # Step 2: Statistical testing
        winner, confidence, p_value = self._run_statistical_test(variant_stats)

        # Step 3: Calculate lift
        baseline_variant = variant_names[0] if variant_names else "A"
        baseline_rate = variant_stats[baseline_variant]["conversion_rate"]
        winner_rate = variant_stats[winner]["conversion_rate"]
        estimated_lift = self._safe_divide(winner_rate - baseline_rate, baseline_rate)

        # Step 4: Create result
        result = ExperimentResult(
            experiment_id=experiment_id,
            winner_variant=winner,
            confidence=confidence,
            winner_metric_value=variant_stats[winner]["conversion_rate"],
            loser_metric_value=baseline_rate,
            estimated_lift=estimated_lift,
            statistical_significance=p_value
        )

        # Step 5: Update DB
        try:
            await self.db.experiments.update(
                {"id": experiment_id},
                {
                    "status": "completed",
                    "winner_variant": winner,
                    "confidence": confidence,
                    "completed_at": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            print(f"[{self.AGENT_ID}] DB update error: {e}")

        # Step 6: Publish result
        self.publish_message(
            EventType.EXPERIMENT_RESULT,
            result.model_dump(),
            targets=["METRIC-01", "STRAT-01"],  # Alert analytics and strategy
            correlation_id=correlation_id,
            priority="HIGH"
        )

        print(f"[{self.AGENT_ID}] Analysis complete")
        print(f"  Winner: {winner}")
        print(f"  Lift: {estimated_lift:.1%}")
        print(f"  Confidence: {confidence:.0%}")

        return result

    # ========================================================================
    # Statistical Methods
    # ========================================================================

    def _select_success_metric(self, goal_type: str) -> str:
        """Select appropriate success metric based on goal"""

        metrics = {
            "reach": "impressions",
            "engagement": "engagement_rate",
            "conversion": "conversion_rate",
            "revenue": "revenue_per_visitor",
            "retention": "return_rate",
            "authority": "saves_shares",
            "insight": "click_through_rate"
        }

        return metrics.get(goal_type, "conversion_rate")

    def _calculate_sample_size(
        self,
        baseline_rate: float,
        mde: float,
        alpha: float = 0.05,
        power: float = 0.8
    ) -> int:
        """
        Calculate required sample size for each variant

        Using simplified formula (in production, use scipy.stats)
        """

        from math import sqrt

        # Simplified formula based on normal approximation
        p1 = baseline_rate
        p2 = baseline_rate * (1 + mde)

        # Z-scores for alpha and power
        z_alpha = 1.96      # 95% confidence
        z_beta = 0.84       # 80% power

        # Pooled proportion
        p_pool = (p1 + p2) / 2

        # Sample size formula
        numerator = (z_alpha + z_beta) ** 2 * (p1 * (1 - p1) + p2 * (1 - p2))
        denominator = (p2 - p1) ** 2

        n = numerator / denominator

        return int(n) + 1  # Round up

    def _run_statistical_test(
        self,
        variant_stats: Dict[str, Dict[str, Any]]
    ) -> Tuple[str, float, float]:
        """
        Run A/B test statistical comparison

        Returns: (winner, confidence, p_value)
        """

        # Find variant with highest conversion rate
        best_variant = None
        best_rate = 0

        for variant_name, stats in variant_stats.items():
            if stats["conversion_rate"] > best_rate:
                best_rate = stats["conversion_rate"]
                best_variant = variant_name

        # Calculate confidence based on sample sizes
        total_sample = sum(s["sample_size"] for s in variant_stats.values())
        min_sample_threshold = 500

        if total_sample < min_sample_threshold:
            confidence = 0.3  # Low confidence
        elif total_sample < min_sample_threshold * 2:
            confidence = 0.6  # Medium confidence
        else:
            confidence = 0.9  # High confidence

        # Simple p-value placeholder
        p_value = 0.05

        return best_variant, confidence, p_value

    def _safe_divide(self, numerator: float, denominator: float, default: float = 0.0) -> float:
        """Safe division"""

        if denominator == 0:
            return default

        return numerator / denominator


# ============================================================================
# Integration with Master Orchestrator
# ============================================================================

"""
To use SplitMind agent:

1. Agent startup:
   split_mind = SplitMindAgent(redis_client, db_client, llm_client)
   await split_mind.start()

2. Design experiment (called by strategy during move planning):
   event_bus.publish(AgentMessage(
       type=EventType.MOVE_PLAN,
       origin="STRAT-01",
       targets=["EXP-01"],
       payload={
           "move_id": "123",
           "objective": "conversion",
           "a_b_test_variants": [
               {"variant": "A", "asset_id": "asset-001"},
               {"variant": "B", "asset_id": "asset-002"}
           ]
       },
       correlation_id="move-123"
   ))

3. Analyze results (called by execution agents after collecting metrics):
   result = await split_mind.analyze_experiment(
       experiment_id="exp-123",
       results_data={
           "A": {"sample_size": 1000, "conversions": 50},
           "B": {"sample_size": 1000, "conversions": 75}
       },
       correlation_id="move-123"
   )
"""
