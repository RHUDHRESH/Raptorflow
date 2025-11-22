"""
Experiment engine for continuous A/B testing and optimization.

This module enables data-driven experimentation in RaptorFlow:
- Running A/B tests on content strategies, prompts, and tactics
- Multi-armed bandit algorithms for dynamic optimization
- Statistical significance testing and early stopping
- Experiment tracking and result analysis
- Feedback loop to training pipelines

Key Features:
- A/B and multivariate testing
- Thompson sampling and UCB algorithms
- Bayesian inference for significance testing
- Experiment versioning and reproducibility
- Automatic winner selection and rollout

Usage:
    engine = ExperimentEngine()
    experiment = await engine.create_experiment(
        name="hook_style_test",
        variants=["casual", "professional", "provocative"],
        metric="engagement_rate"
    )
    await engine.record_outcome(experiment_id, variant="casual", outcome=0.12)
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

import numpy as np
from pydantic import BaseModel, Field
from scipy import stats


class ExperimentStatus(str, Enum):
    """Status of an experiment."""

    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ExperimentType(str, Enum):
    """Type of experiment."""

    AB_TEST = "ab_test"  # Classic A/B test
    MULTIVARIATE = "multivariate"  # Multiple variables
    MULTI_ARMED_BANDIT = "multi_armed_bandit"  # Dynamic allocation
    SEQUENTIAL = "sequential"  # Sequential testing with early stopping


class VariantAllocation(str, Enum):
    """How to allocate traffic to variants."""

    EQUAL = "equal"  # Equal split
    WEIGHTED = "weighted"  # Custom weights
    THOMPSON = "thompson_sampling"  # Thompson sampling (bandit)
    UCB = "ucb"  # Upper confidence bound (bandit)


class ExperimentVariant(BaseModel):
    """
    A variant in an experiment.

    Attributes:
        variant_id: Unique identifier
        name: Human-readable name
        description: What this variant does
        config: Configuration/parameters for this variant
        traffic_allocation: Percentage of traffic (0.0-1.0)
        sample_count: Number of samples observed
        sum_outcomes: Sum of all outcomes (for mean calculation)
        sum_squared_outcomes: Sum of squared outcomes (for variance)
    """

    variant_id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    config: Dict[str, Any] = Field(default_factory=dict)
    traffic_allocation: float = Field(default=0.5, ge=0.0, le=1.0)
    sample_count: int = 0
    sum_outcomes: float = 0.0
    sum_squared_outcomes: float = 0.0

    @property
    def mean(self) -> float:
        """Calculate mean outcome."""
        return (
            self.sum_outcomes / self.sample_count if self.sample_count > 0 else 0.0
        )

    @property
    def variance(self) -> float:
        """Calculate variance of outcomes."""
        if self.sample_count < 2:
            return 0.0
        mean_of_squares = self.sum_squared_outcomes / self.sample_count
        square_of_mean = self.mean**2
        return max(0.0, mean_of_squares - square_of_mean)

    @property
    def std_dev(self) -> float:
        """Calculate standard deviation."""
        return np.sqrt(self.variance)


class Experiment(BaseModel):
    """
    Represents an A/B test or experiment.

    Attributes:
        experiment_id: Unique identifier
        name: Experiment name
        description: What this experiment tests
        workspace_id: Workspace running the experiment
        experiment_type: Type of experiment
        allocation_strategy: How to allocate traffic
        metric_name: Primary metric being optimized
        variants: List of experiment variants
        status: Current status
        min_sample_size: Minimum samples before concluding
        confidence_level: Required confidence (e.g., 0.95 for 95%)
        created_at: When experiment was created
        started_at: When experiment started running
        completed_at: When experiment completed
        winner: Winning variant (if determined)
        metadata: Additional experiment metadata
    """

    experiment_id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    workspace_id: UUID
    experiment_type: ExperimentType = ExperimentType.AB_TEST
    allocation_strategy: VariantAllocation = VariantAllocation.EQUAL
    metric_name: str
    variants: List[ExperimentVariant]
    status: ExperimentStatus = ExperimentStatus.DRAFT
    min_sample_size: int = 100
    confidence_level: float = 0.95
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    winner: Optional[str] = None  # variant_id of winner
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExperimentResult(BaseModel):
    """
    Results of an experiment.

    Attributes:
        experiment_id: Experiment identifier
        winner: Winning variant name
        confidence: Statistical confidence in winner
        lift: Performance lift over baseline (e.g., 0.15 = 15% improvement)
        p_value: Statistical significance p-value
        sample_counts: Samples per variant
        means: Mean outcome per variant
        recommendation: Recommended action
        statistical_power: Statistical power of the test
    """

    experiment_id: str
    winner: str
    confidence: float
    lift: float
    p_value: float
    sample_counts: Dict[str, int]
    means: Dict[str, float]
    recommendation: str
    statistical_power: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExperimentEngine:
    """
    Orchestrates continuous experimentation and A/B testing.

    This engine enables:
    1. Creating and managing experiments
    2. Allocating traffic to variants (static or dynamic)
    3. Recording outcomes and updating statistics
    4. Detecting statistical significance
    5. Automatically selecting winners

    Methods:
        create_experiment: Create a new experiment
        start_experiment: Start running an experiment
        assign_variant: Assign a user/request to a variant
        record_outcome: Record an outcome for a variant
        analyze_experiment: Analyze current results
        check_significance: Check if results are significant
        complete_experiment: Mark experiment as complete
    """

    def __init__(
        self,
        default_confidence: float = 0.95,
        min_effect_size: float = 0.05,
    ):
        """
        Initialize the experiment engine.

        Args:
            default_confidence: Default confidence level (e.g., 0.95)
            min_effect_size: Minimum detectable effect (e.g., 0.05 = 5%)
        """
        self.default_confidence = default_confidence
        self.min_effect_size = min_effect_size
        self.logger = logging.getLogger(__name__)

        # In-memory experiment store (would be database in production)
        self.experiments: Dict[str, Experiment] = {}

    async def create_experiment(
        self,
        name: str,
        workspace_id: UUID,
        variants: List[Dict[str, Any]],
        metric_name: str,
        description: str = "",
        experiment_type: ExperimentType = ExperimentType.AB_TEST,
        allocation_strategy: VariantAllocation = VariantAllocation.EQUAL,
        min_sample_size: int = 100,
        confidence_level: Optional[float] = None,
    ) -> Experiment:
        """
        Create a new experiment.

        Args:
            name: Experiment name
            workspace_id: Workspace ID
            variants: List of variant definitions
            metric_name: Metric to optimize (e.g., "engagement_rate")
            description: What this experiment tests
            experiment_type: Type of experiment
            allocation_strategy: Traffic allocation method
            min_sample_size: Minimum samples before concluding
            confidence_level: Required confidence level

        Returns:
            Created Experiment object

        Example:
            variants = [
                {"name": "control", "description": "Current approach"},
                {"name": "variant_a", "description": "New hook style"},
            ]
            exp = await engine.create_experiment(
                name="hook_style_test",
                workspace_id=workspace_id,
                variants=variants,
                metric_name="engagement_rate"
            )
        """
        # Create variant objects
        variant_objects = []
        num_variants = len(variants)

        for i, variant_def in enumerate(variants):
            # Equal allocation by default
            traffic_allocation = 1.0 / num_variants

            variant = ExperimentVariant(
                name=variant_def["name"],
                description=variant_def.get("description", ""),
                config=variant_def.get("config", {}),
                traffic_allocation=traffic_allocation,
            )
            variant_objects.append(variant)

        # Create experiment
        experiment = Experiment(
            name=name,
            description=description,
            workspace_id=workspace_id,
            experiment_type=experiment_type,
            allocation_strategy=allocation_strategy,
            metric_name=metric_name,
            variants=variant_objects,
            min_sample_size=min_sample_size,
            confidence_level=confidence_level or self.default_confidence,
        )

        # Store experiment
        self.experiments[experiment.experiment_id] = experiment

        self.logger.info(
            f"Created experiment '{name}' with {len(variants)} variants"
        )

        return experiment

    async def start_experiment(self, experiment_id: str) -> Experiment:
        """
        Start running an experiment.

        Args:
            experiment_id: ID of experiment to start

        Returns:
            Updated experiment object

        Raises:
            ValueError: If experiment doesn't exist or is not in draft status
        """
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            raise ValueError(f"Experiment {experiment_id} not found")

        if experiment.status != ExperimentStatus.DRAFT:
            raise ValueError(
                f"Cannot start experiment in status {experiment.status}"
            )

        experiment.status = ExperimentStatus.RUNNING
        experiment.started_at = datetime.now(timezone.utc)

        self.logger.info(f"Started experiment '{experiment.name}'")

        return experiment

    async def assign_variant(
        self,
        experiment_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Assign a variant to a user/request.

        Uses the experiment's allocation strategy to select a variant.
        For bandit algorithms, this implements exploration vs exploitation.

        Args:
            experiment_id: ID of experiment
            context: Optional context for assignment (user_id, etc.)

        Returns:
            Variant ID assigned

        Raises:
            ValueError: If experiment doesn't exist or is not running
        """
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            raise ValueError(f"Experiment {experiment_id} not found")

        if experiment.status != ExperimentStatus.RUNNING:
            raise ValueError(
                f"Cannot assign variant for experiment in status {experiment.status}"
            )

        # Select variant based on allocation strategy
        if experiment.allocation_strategy == VariantAllocation.EQUAL:
            variant = self._assign_equal(experiment)
        elif experiment.allocation_strategy == VariantAllocation.WEIGHTED:
            variant = self._assign_weighted(experiment)
        elif experiment.allocation_strategy == VariantAllocation.THOMPSON:
            variant = self._assign_thompson_sampling(experiment)
        elif experiment.allocation_strategy == VariantAllocation.UCB:
            variant = self._assign_ucb(experiment)
        else:
            variant = self._assign_equal(experiment)

        return variant.variant_id

    async def record_outcome(
        self,
        experiment_id: str,
        variant_id: str,
        outcome: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Record an outcome for a variant.

        Updates the variant's statistics and checks for significance.

        Args:
            experiment_id: ID of experiment
            variant_id: ID of variant that was shown
            outcome: Outcome value (e.g., 1.0 for conversion, 0.15 for engagement)
            metadata: Optional metadata about this outcome

        Raises:
            ValueError: If experiment or variant doesn't exist
        """
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Find variant
        variant = next(
            (v for v in experiment.variants if v.variant_id == variant_id),
            None,
        )
        if not variant:
            raise ValueError(f"Variant {variant_id} not found")

        # Update statistics
        variant.sample_count += 1
        variant.sum_outcomes += outcome
        variant.sum_squared_outcomes += outcome**2

        # Check if we should auto-complete the experiment
        total_samples = sum(v.sample_count for v in experiment.variants)
        if (
            total_samples >= experiment.min_sample_size
            and experiment.status == ExperimentStatus.RUNNING
        ):
            # Check for significance
            is_significant, winner = await self.check_significance(experiment_id)
            if is_significant:
                await self.complete_experiment(
                    experiment_id, winner=winner, reason="statistical_significance"
                )

    async def analyze_experiment(
        self, experiment_id: str
    ) -> ExperimentResult:
        """
        Analyze current experiment results.

        Performs statistical analysis to determine if there's a winner
        and calculates confidence, lift, and other metrics.

        Args:
            experiment_id: ID of experiment to analyze

        Returns:
            ExperimentResult with analysis

        Raises:
            ValueError: If experiment doesn't exist
        """
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Get variant statistics
        variants = experiment.variants
        if len(variants) < 2:
            raise ValueError("Need at least 2 variants to analyze")

        # Assume first variant is control
        control = variants[0]
        treatment = variants[1] if len(variants) == 2 else max(
            variants[1:], key=lambda v: v.mean
        )

        # Perform t-test
        if control.sample_count >= 2 and treatment.sample_count >= 2:
            t_stat, p_value = self._two_sample_t_test(control, treatment)
            is_significant = p_value < (1 - experiment.confidence_level)
        else:
            t_stat, p_value = 0.0, 1.0
            is_significant = False

        # Calculate lift
        if control.mean > 0:
            lift = (treatment.mean - control.mean) / control.mean
        else:
            lift = 0.0

        # Determine winner
        if is_significant and treatment.mean > control.mean:
            winner = treatment.name
            confidence = 1 - p_value
        elif is_significant and control.mean > treatment.mean:
            winner = control.name
            confidence = 1 - p_value
        else:
            winner = "inconclusive"
            confidence = 0.5

        # Calculate statistical power (simplified)
        total_samples = control.sample_count + treatment.sample_count
        statistical_power = min(
            0.99, total_samples / (experiment.min_sample_size * 2)
        )

        # Generate recommendation
        if is_significant:
            recommendation = f"Deploy '{winner}' - statistically significant improvement"
        elif total_samples < experiment.min_sample_size:
            recommendation = f"Continue collecting data ({total_samples}/{experiment.min_sample_size} samples)"
        else:
            recommendation = "No significant difference detected - use business judgment"

        return ExperimentResult(
            experiment_id=experiment_id,
            winner=winner,
            confidence=float(confidence),
            lift=float(lift),
            p_value=float(p_value),
            sample_counts={v.name: v.sample_count for v in variants},
            means={v.name: v.mean for v in variants},
            recommendation=recommendation,
            statistical_power=float(statistical_power),
            metadata={
                "t_statistic": float(t_stat),
                "total_samples": total_samples,
                "control_std": float(control.std_dev),
                "treatment_std": float(treatment.std_dev),
            },
        )

    async def check_significance(
        self, experiment_id: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if experiment has reached statistical significance.

        Args:
            experiment_id: ID of experiment

        Returns:
            Tuple of (is_significant, winner_variant_name)
        """
        result = await self.analyze_experiment(experiment_id)
        is_significant = (
            result.confidence >= self.default_confidence
            and result.winner != "inconclusive"
        )
        winner = result.winner if is_significant else None
        return is_significant, winner

    async def complete_experiment(
        self,
        experiment_id: str,
        winner: Optional[str] = None,
        reason: str = "manual",
    ) -> ExperimentResult:
        """
        Complete an experiment and declare a winner.

        Args:
            experiment_id: ID of experiment
            winner: Optional winner variant name
            reason: Reason for completion

        Returns:
            Final experiment results

        Raises:
            ValueError: If experiment doesn't exist
        """
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            raise ValueError(f"Experiment {experiment_id} not found")

        # Analyze final results
        result = await self.analyze_experiment(experiment_id)

        # Update experiment
        experiment.status = ExperimentStatus.COMPLETED
        experiment.completed_at = datetime.now(timezone.utc)
        experiment.winner = winner or result.winner
        experiment.metadata["completion_reason"] = reason
        experiment.metadata["final_results"] = result.model_dump()

        self.logger.info(
            f"Completed experiment '{experiment.name}': "
            f"winner={experiment.winner}, lift={result.lift:.1%}"
        )

        return result

    def _assign_equal(self, experiment: Experiment) -> ExperimentVariant:
        """Assign variant with equal probability."""
        return np.random.choice(experiment.variants)

    def _assign_weighted(self, experiment: Experiment) -> ExperimentVariant:
        """Assign variant based on traffic allocation weights."""
        weights = [v.traffic_allocation for v in experiment.variants]
        weights_sum = sum(weights)
        normalized_weights = [w / weights_sum for w in weights]
        return np.random.choice(experiment.variants, p=normalized_weights)

    def _assign_thompson_sampling(
        self, experiment: Experiment
    ) -> ExperimentVariant:
        """
        Assign variant using Thompson sampling.

        Samples from posterior distribution (Beta for conversion rates).
        """
        samples = []
        for variant in experiment.variants:
            # Beta prior: Beta(1, 1) = Uniform(0, 1)
            # Posterior: Beta(1 + successes, 1 + failures)
            # Assume outcomes are binary (0 or 1)
            alpha = 1 + variant.sum_outcomes
            beta_param = 1 + variant.sample_count - variant.sum_outcomes
            sample = np.random.beta(alpha, beta_param)
            samples.append(sample)

        # Select variant with highest sample
        best_idx = np.argmax(samples)
        return experiment.variants[best_idx]

    def _assign_ucb(self, experiment: Experiment) -> ExperimentVariant:
        """
        Assign variant using Upper Confidence Bound (UCB1).

        Balances exploration and exploitation by selecting variant
        with highest upper confidence bound.
        """
        total_samples = sum(v.sample_count for v in experiment.variants)

        if total_samples == 0:
            # First assignment - random
            return np.random.choice(experiment.variants)

        ucb_scores = []
        for variant in experiment.variants:
            if variant.sample_count == 0:
                # Unseen variants get infinite score (explore first)
                ucb_scores.append(float("inf"))
            else:
                # UCB1 formula
                exploitation = variant.mean
                exploration = np.sqrt(
                    (2 * np.log(total_samples)) / variant.sample_count
                )
                ucb = exploitation + exploration
                ucb_scores.append(ucb)

        # Select variant with highest UCB
        best_idx = np.argmax(ucb_scores)
        return experiment.variants[best_idx]

    def _two_sample_t_test(
        self, variant_a: ExperimentVariant, variant_b: ExperimentVariant
    ) -> Tuple[float, float]:
        """
        Perform Welch's t-test for two independent samples.

        Args:
            variant_a: First variant
            variant_b: Second variant

        Returns:
            Tuple of (t_statistic, p_value)
        """
        mean_a = variant_a.mean
        mean_b = variant_b.mean
        var_a = variant_a.variance
        var_b = variant_b.variance
        n_a = variant_a.sample_count
        n_b = variant_b.sample_count

        if n_a < 2 or n_b < 2:
            return 0.0, 1.0

        # Welch's t-test (doesn't assume equal variances)
        se = np.sqrt(var_a / n_a + var_b / n_b)
        if se == 0:
            return 0.0, 1.0

        t_stat = (mean_a - mean_b) / se

        # Degrees of freedom (Welch-Satterthwaite equation)
        numerator = (var_a / n_a + var_b / n_b) ** 2
        denominator = (var_a / n_a) ** 2 / (n_a - 1) + (
            var_b / n_b
        ) ** 2 / (n_b - 1)
        df = numerator / denominator if denominator > 0 else 1

        # Two-tailed p-value
        p_value = 2 * stats.t.sf(abs(t_stat), df=df)

        return float(t_stat), float(p_value)

    async def get_experiment_status(
        self, experiment_id: str
    ) -> Dict[str, Any]:
        """
        Get current status and statistics for an experiment.

        Args:
            experiment_id: ID of experiment

        Returns:
            Dictionary with experiment status and statistics
        """
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            raise ValueError(f"Experiment {experiment_id} not found")

        total_samples = sum(v.sample_count for v in experiment.variants)

        return {
            "experiment_id": experiment_id,
            "name": experiment.name,
            "status": experiment.status.value,
            "total_samples": total_samples,
            "progress": min(1.0, total_samples / experiment.min_sample_size),
            "variants": [
                {
                    "name": v.name,
                    "samples": v.sample_count,
                    "mean": v.mean,
                    "std_dev": v.std_dev,
                }
                for v in experiment.variants
            ],
            "started_at": experiment.started_at.isoformat()
            if experiment.started_at
            else None,
            "runtime_hours": (
                (datetime.now(timezone.utc) - experiment.started_at).total_seconds()
                / 3600
                if experiment.started_at
                else 0
            ),
        }
