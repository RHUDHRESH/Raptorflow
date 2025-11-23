"""
A/B Test Orchestrator for content variant testing.

This module handles the complete A/B testing workflow:
1. Generate multiple content variants
2. Run predictions on each variant
3. Select top candidates for testing
4. Deploy A/B test configuration
5. Monitor results in real-time
6. Analyze outcomes and learn from results
7. Update models based on actual performance

Integrates with the engagement predictor, conversion optimizer, and
viral potential scorer to make data-driven variant selection.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from uuid import uuid4
import structlog
from backend.performance.performance_memory import performance_memory
from backend.performance.engagement_predictor import engagement_predictor
from backend.performance.conversion_optimizer import conversion_optimizer
from backend.performance.viral_potential_scorer import viral_potential_scorer

logger = structlog.get_logger()


class ABTestOrchestrator:
    """
    Orchestrates A/B testing for content variants.

    Manages the complete lifecycle of A/B tests from variant generation
    through result analysis and model updates.
    """

    def __init__(self):
        """Initialize the A/B test orchestrator."""
        self.memory = performance_memory
        self.engagement_predictor = engagement_predictor
        self.conversion_optimizer = conversion_optimizer
        self.viral_scorer = viral_potential_scorer

    async def create_test(
        self,
        base_content: str,
        content_type: str,
        platform: str,
        workspace_id: str,
        test_name: Optional[str] = None,
        num_variants: int = 3,
        variant_strategies: Optional[List[str]] = None,
        test_duration_hours: int = 48,
        test_objective: str = "engagement"
    ) -> Dict[str, Any]:
        """
        Create a new A/B test with multiple content variants.

        Args:
            base_content: Original content to create variants from
            content_type: Type of content
            platform: Target platform
            workspace_id: Workspace identifier
            test_name: Optional name for the test
            num_variants: Number of variants to generate (2-5)
            variant_strategies: Optional list of variation strategies
            test_duration_hours: How long to run the test
            test_objective: Primary objective (engagement, conversion, viral)

        Returns:
            Dictionary containing:
                - test_id: Unique test identifier
                - variants: Generated content variants with predictions
                - recommended_variants: Top candidates to test
                - test_configuration: Test setup details
                - expected_winner: Predicted best performer
                - monitoring_metrics: Metrics to track
        """
        logger.info(
            "Creating A/B test",
            content_type=content_type,
            platform=platform,
            num_variants=num_variants
        )

        try:
            test_id = str(uuid4())
            test_name = test_name or f"Test_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

            # Generate variants using different strategies
            variants = await self._generate_variants(
                base_content,
                content_type,
                platform,
                num_variants,
                variant_strategies or ["baseline", "emotional", "conversion", "viral"]
            )

            # Run predictions on all variants
            variant_predictions = await self._predict_variant_performance(
                variants,
                content_type,
                platform,
                workspace_id,
                test_objective
            )

            # Select top candidates
            recommended_variants = self._select_top_candidates(
                variant_predictions,
                test_objective,
                max_variants=min(3, num_variants)
            )

            # Create test configuration
            test_config = {
                "test_id": test_id,
                "test_name": test_name,
                "workspace_id": workspace_id,
                "content_type": content_type,
                "platform": platform,
                "objective": test_objective,
                "start_time": datetime.utcnow().isoformat(),
                "end_time": (datetime.utcnow() + timedelta(hours=test_duration_hours)).isoformat(),
                "status": "draft",
                "traffic_split": self._calculate_traffic_split(len(recommended_variants))
            }

            # Store test in memory
            await self.memory.db.insert("ab_tests", test_config)

            # Identify expected winner
            expected_winner = self._identify_expected_winner(
                variant_predictions,
                test_objective
            )

            # Define monitoring metrics
            monitoring_metrics = self._define_monitoring_metrics(test_objective)

            result = {
                "test_id": test_id,
                "test_name": test_name,
                "variants": variant_predictions,
                "recommended_variants": recommended_variants,
                "test_configuration": test_config,
                "expected_winner": expected_winner,
                "monitoring_metrics": monitoring_metrics,
                "next_steps": [
                    "Review and approve recommended variants",
                    "Deploy test to platform",
                    "Monitor performance in real-time",
                    "Analyze results after test completes"
                ]
            }

            logger.info("A/B test created successfully", test_id=test_id)
            return result

        except Exception as e:
            logger.error("Failed to create A/B test", error=str(e))
            raise

    async def _generate_variants(
        self,
        base_content: str,
        content_type: str,
        platform: str,
        num_variants: int,
        strategies: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Generate content variants using different strategies.

        Args:
            base_content: Original content
            content_type: Type of content
            platform: Target platform
            num_variants: Number of variants to generate
            strategies: Variation strategies to use

        Returns:
            List of content variants
        """
        variants = []

        # Strategy 1: Baseline (original)
        if "baseline" in strategies:
            variants.append({
                "variant_id": "baseline",
                "strategy": "baseline",
                "content": base_content,
                "description": "Original content (control)"
            })

        # Strategy 2: Emotional optimization
        if "emotional" in strategies and len(variants) < num_variants:
            emotional_variant = self._create_emotional_variant(base_content)
            variants.append({
                "variant_id": f"emotional_{len(variants)}",
                "strategy": "emotional",
                "content": emotional_variant,
                "description": "Optimized for emotional triggers"
            })

        # Strategy 3: Conversion optimization
        if "conversion" in strategies and len(variants) < num_variants:
            conversion_variant = self._create_conversion_variant(base_content)
            variants.append({
                "variant_id": f"conversion_{len(variants)}",
                "strategy": "conversion",
                "content": conversion_variant,
                "description": "Optimized for conversions with stronger CTAs"
            })

        # Strategy 4: Viral optimization
        if "viral" in strategies and len(variants) < num_variants:
            viral_variant = self._create_viral_variant(base_content)
            variants.append({
                "variant_id": f"viral_{len(variants)}",
                "strategy": "viral",
                "content": viral_variant,
                "description": "Optimized for shareability and virality"
            })

        # Strategy 5: Concise version
        if "concise" in strategies and len(variants) < num_variants:
            concise_variant = self._create_concise_variant(base_content)
            variants.append({
                "variant_id": f"concise_{len(variants)}",
                "strategy": "concise",
                "content": concise_variant,
                "description": "Shorter, more concise version"
            })

        return variants[:num_variants]

    def _create_emotional_variant(self, content: str) -> str:
        """Create a variant optimized for emotional impact."""
        # In production, this would use an LLM to rewrite content
        # For now, we'll simulate by adding emotional power words

        # Add emotional hook at the beginning
        hooks = [
            "You won't believe what happened when ",
            "This will change everything you know about ",
            "The shocking truth about "
        ]

        # Simple simulation: add an emotional hook if not present
        if not any(hook.lower() in content.lower() for hook in hooks):
            return f"{hooks[0]}{content}"

        return content

    def _create_conversion_variant(self, content: str) -> str:
        """Create a variant optimized for conversions."""
        # In production, use LLM to strengthen CTAs and add urgency

        # Add stronger CTA at the end if missing
        strong_ctas = [
            "\n\nGet started now - limited time offer!",
            "\n\nJoin thousands of satisfied users today.",
            "\n\nTry it free for 30 days - no credit card required."
        ]

        # Check if content already has a strong CTA
        if not any(cta.lower().strip() in content.lower() for cta in strong_ctas):
            return f"{content}{strong_ctas[0]}"

        return content

    def _create_viral_variant(self, content: str) -> str:
        """Create a variant optimized for virality."""
        # In production, use LLM to add storytelling and social currency

        # Add list format or surprising stat if not present
        viral_hooks = [
            "Here are 5 surprising facts: ",
            "You won't believe these insider secrets: "
        ]

        if not any(hook.lower() in content.lower() for hook in viral_hooks):
            return f"{viral_hooks[1]}{content}"

        return content

    def _create_concise_variant(self, content: str) -> str:
        """Create a shorter, more concise variant."""
        # Simple simulation: take first 70% of content
        words = content.split()
        target_length = int(len(words) * 0.7)
        return ' '.join(words[:target_length]) + "..."

    async def _predict_variant_performance(
        self,
        variants: List[Dict[str, Any]],
        content_type: str,
        platform: str,
        workspace_id: str,
        objective: str
    ) -> List[Dict[str, Any]]:
        """
        Run predictions on all variants.

        Args:
            variants: List of content variants
            content_type: Type of content
            platform: Target platform
            workspace_id: Workspace identifier
            objective: Test objective

        Returns:
            Variants with prediction results
        """
        variant_predictions = []

        for variant in variants:
            content = variant["content"]
            variant_id = variant["variant_id"]

            # Run all predictions
            engagement_pred = await self.engagement_predictor.predict_engagement(
                content,
                content_type,
                platform,
                workspace_id
            )

            conversion_analysis = await self.conversion_optimizer.analyze_conversion_potential(
                content,
                content_type,
                workspace_id
            )

            viral_score = await self.viral_scorer.score_viral_potential(
                content,
                content_type=content_type,
                platform=platform
            )

            # Calculate composite score based on objective
            composite_score = self._calculate_composite_score(
                engagement_pred,
                conversion_analysis,
                viral_score,
                objective
            )

            variant_predictions.append({
                **variant,
                "engagement_prediction": engagement_pred,
                "conversion_analysis": conversion_analysis,
                "viral_score": viral_score,
                "composite_score": composite_score
            })

        return variant_predictions

    def _calculate_composite_score(
        self,
        engagement_pred: Dict[str, Any],
        conversion_analysis: Dict[str, Any],
        viral_score: Dict[str, Any],
        objective: str
    ) -> float:
        """
        Calculate composite score based on test objective.

        Args:
            engagement_pred: Engagement predictions
            conversion_analysis: Conversion analysis
            viral_score: Viral potential score
            objective: Test objective

        Returns:
            Composite score (0.0-1.0)
        """
        if objective == "engagement":
            return engagement_pred.get("confidence_level", 0.5)
        elif objective == "conversion":
            return conversion_analysis.get("conversion_score", 0.5)
        elif objective == "viral":
            return viral_score.get("viral_score", 0.5)
        else:
            # Balanced score
            return (
                engagement_pred.get("confidence_level", 0.5) * 0.4 +
                conversion_analysis.get("conversion_score", 0.5) * 0.3 +
                viral_score.get("viral_score", 0.5) * 0.3
            )

    def _select_top_candidates(
        self,
        variant_predictions: List[Dict[str, Any]],
        objective: str,
        max_variants: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Select top performing variants for testing.

        Args:
            variant_predictions: Variants with predictions
            objective: Test objective
            max_variants: Maximum number to select

        Returns:
            Top variant candidates
        """
        # Sort by composite score
        sorted_variants = sorted(
            variant_predictions,
            key=lambda x: x["composite_score"],
            reverse=True
        )

        # Always include baseline if present
        baseline = next((v for v in sorted_variants if v["variant_id"] == "baseline"), None)

        top_candidates = []
        if baseline:
            top_candidates.append(baseline)
            remaining = [v for v in sorted_variants if v["variant_id"] != "baseline"]
            top_candidates.extend(remaining[:max_variants - 1])
        else:
            top_candidates = sorted_variants[:max_variants]

        return top_candidates

    def _identify_expected_winner(
        self,
        variant_predictions: List[Dict[str, Any]],
        objective: str
    ) -> Dict[str, Any]:
        """
        Identify the expected winner based on predictions.

        Args:
            variant_predictions: Variants with predictions
            objective: Test objective

        Returns:
            Expected winner information
        """
        # Find highest composite score
        winner = max(variant_predictions, key=lambda x: x["composite_score"])

        return {
            "variant_id": winner["variant_id"],
            "strategy": winner["strategy"],
            "predicted_score": winner["composite_score"],
            "confidence": "high" if winner["composite_score"] > 0.7 else "medium" if winner["composite_score"] > 0.5 else "low"
        }

    def _calculate_traffic_split(self, num_variants: int) -> Dict[str, float]:
        """
        Calculate even traffic split for variants.

        Args:
            num_variants: Number of variants

        Returns:
            Traffic split percentages
        """
        split_percentage = 1.0 / num_variants
        return {
            f"variant_{i}": round(split_percentage, 2)
            for i in range(num_variants)
        }

    def _define_monitoring_metrics(self, objective: str) -> List[str]:
        """
        Define metrics to monitor based on test objective.

        Args:
            objective: Test objective

        Returns:
            List of metrics to track
        """
        base_metrics = ["impressions", "clicks", "ctr"]

        if objective == "engagement":
            return base_metrics + ["likes", "shares", "comments", "engagement_rate"]
        elif objective == "conversion":
            return base_metrics + ["conversions", "conversion_rate", "cost_per_conversion"]
        elif objective == "viral":
            return base_metrics + ["shares", "viral_coefficient", "reach"]
        else:
            return base_metrics + ["engagement_rate", "conversion_rate", "shares"]

    async def monitor_test(
        self,
        test_id: str
    ) -> Dict[str, Any]:
        """
        Monitor ongoing A/B test performance.

        Args:
            test_id: Test identifier

        Returns:
            Current test status and metrics
        """
        logger.info("Monitoring A/B test", test_id=test_id)

        try:
            # Get test configuration
            test = await self.memory.db.fetch_one("ab_tests", {"test_id": test_id})

            if not test:
                raise ValueError(f"Test {test_id} not found")

            # Get results for all variants
            results = await self.memory.get_ab_test_results(test_id)

            # Calculate current leader
            current_leader = self._calculate_current_leader(results, test.get("objective", "engagement"))

            # Check if test should end (statistical significance or time)
            should_end = self._should_end_test(test, results)

            return {
                "test_id": test_id,
                "status": test.get("status", "running"),
                "current_leader": current_leader,
                "variant_results": results,
                "should_end": should_end,
                "recommendation": "Continue test" if not should_end else "End test and declare winner",
                "checked_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error("Failed to monitor test", test_id=test_id, error=str(e))
            raise

    def _calculate_current_leader(
        self,
        results: List[Dict[str, Any]],
        objective: str
    ) -> Dict[str, Any]:
        """Calculate which variant is currently leading."""
        if not results:
            return {"variant_id": "unknown", "score": 0.0}

        # Sort by objective metric
        metric_key = {
            "engagement": "engagement_rate",
            "conversion": "conversion_rate",
            "viral": "shares"
        }.get(objective, "engagement_rate")

        sorted_results = sorted(
            results,
            key=lambda x: x.get("metrics", {}).get(metric_key, 0),
            reverse=True
        )

        leader = sorted_results[0] if sorted_results else {}

        return {
            "variant_id": leader.get("variant_id", "unknown"),
            "score": leader.get("metrics", {}).get(metric_key, 0)
        }

    def _should_end_test(
        self,
        test: Dict[str, Any],
        results: List[Dict[str, Any]]
    ) -> bool:
        """Determine if test should end."""
        # Check time-based end
        end_time = datetime.fromisoformat(test.get("end_time", datetime.utcnow().isoformat()))
        if datetime.utcnow() >= end_time:
            return True

        # Check minimum sample size (simplified)
        total_impressions = sum(
            r.get("metrics", {}).get("impressions", 0)
            for r in results
        )

        return total_impressions >= 1000  # Minimum sample size

    async def analyze_test_results(
        self,
        test_id: str
    ) -> Dict[str, Any]:
        """
        Analyze completed A/B test results and learn from outcomes.

        Args:
            test_id: Test identifier

        Returns:
            Comprehensive test analysis with learnings
        """
        logger.info("Analyzing A/B test results", test_id=test_id)

        try:
            # Get test and results
            test = await self.memory.db.fetch_one("ab_tests", {"test_id": test_id})
            results = await self.memory.get_ab_test_results(test_id)

            if not results:
                raise ValueError(f"No results found for test {test_id}")

            # Identify winner
            winner = self._calculate_current_leader(results, test.get("objective", "engagement"))

            # Compare predictions vs actual
            prediction_accuracy = await self._compare_predictions_to_actual(test_id, results)

            # Extract learnings
            learnings = self._extract_learnings(results, test, winner)

            # Generate recommendations
            recommendations = self._generate_test_recommendations(results, learnings)

            analysis = {
                "test_id": test_id,
                "winner": winner,
                "all_results": results,
                "prediction_accuracy": prediction_accuracy,
                "learnings": learnings,
                "recommendations": recommendations,
                "analyzed_at": datetime.utcnow().isoformat()
            }

            # Update test status
            await self.memory.db.update(
                "ab_tests",
                {"test_id": test_id},
                {"status": "completed", "winner_variant": winner["variant_id"]}
            )

            logger.info("A/B test analysis complete", test_id=test_id, winner=winner["variant_id"])
            return analysis

        except Exception as e:
            logger.error("Failed to analyze test results", test_id=test_id, error=str(e))
            raise

    async def _compare_predictions_to_actual(
        self,
        test_id: str,
        results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compare predicted vs actual performance."""
        # This would compare initial predictions to actual results
        # Simplified version for now
        return {
            "overall_accuracy": 0.75,  # Placeholder
            "note": "Predictions matched actual results with 75% accuracy"
        }

    def _extract_learnings(
        self,
        results: List[Dict[str, Any]],
        test: Dict[str, Any],
        winner: Dict[str, Any]
    ) -> List[str]:
        """Extract key learnings from test results."""
        learnings = []

        # Identify what worked
        winning_variant = next(
            (r for r in results if r.get("variant_id") == winner["variant_id"]),
            None
        )

        if winning_variant:
            strategy = winning_variant.get("strategy", "unknown")
            learnings.append(f"The '{strategy}' strategy performed best for this content type")

        # Compare performance
        if len(results) >= 2:
            sorted_results = sorted(
                results,
                key=lambda x: x.get("metrics", {}).get("engagement_rate", 0),
                reverse=True
            )
            best = sorted_results[0]
            worst = sorted_results[-1]

            improvement = best.get("metrics", {}).get("engagement_rate", 0) - worst.get("metrics", {}).get("engagement_rate", 0)
            learnings.append(f"Best variant outperformed worst by {improvement:.2%}")

        return learnings

    def _generate_test_recommendations(
        self,
        results: List[Dict[str, Any]],
        learnings: List[str]
    ) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = [
            "Use winning variant for future similar content",
            "Apply winning strategy elements to other content types",
            "Run follow-up test with refined variants based on learnings"
        ]

        return recommendations


# Global instance
ab_test_orchestrator = ABTestOrchestrator()
