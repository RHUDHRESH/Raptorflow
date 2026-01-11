"""
Failure Mode Analyzer for Adversarial Critic

Analyzes potential failure modes in plans and content.
Implements PROMPT 57 from STREAM_3_COGNITIVE_ENGINE.
"""

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from ..models import ExecutionPlan, PlanStep, RiskLevel


class FailureModeCategory(Enum):
    """Categories of failure modes."""

    TECHNICAL = "technical"
    OPERATIONAL = "operational"
    EXTERNAL = "external"
    HUMAN = "human"
    RESOURCE = "resource"
    QUALITY = "quality"
    SECURITY = "security"
    COMPLIANCE = "compliance"


class FailureSeverity(Enum):
    """Severity levels for failures."""

    NEGLIGIBLE = "negligible"
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"
    CATASTROPHIC = "catastrophic"


class FailureProbability(Enum):
    """Probability levels for failures."""

    RARE = "rare"  # < 1%
    UNLIKELY = "unlikely"  # 1-10%
    OCCASIONAL = "occasional"  # 10-30%
    LIKELY = "likely"  # 30-60%
    ALMOST_CERTAIN = "almost_certain"  # > 60%


@dataclass
class FailureMode:
    """A potential failure mode."""

    id: str
    name: str
    description: str
    category: FailureModeCategory
    severity: FailureSeverity
    probability: FailureProbability
    impact_description: str
    triggers: List[str]
    warning_signs: List[str]
    affected_components: List[str]
    risk_score: float  # severity x probability (1-10 scale)


@dataclass
class MitigationStrategy:
    """Strategy to mitigate a failure mode."""

    failure_mode_id: str
    strategy_type: str  # "prevention", "detection", "recovery"
    description: str
    implementation_steps: List[str]
    effectiveness: float  # 0-1 scale
    cost: float  # relative cost 1-10
    timeline: str  # implementation timeline
    owner: str  # responsible party


@dataclass
class FailureModeAnalysis:
    """Complete failure mode analysis."""

    plan_id: str
    analysis_date: datetime
    total_failure_modes: int
    high_risk_failures: int
    failure_modes: List[FailureMode]
    mitigation_strategies: List[MitigationStrategy]
    overall_risk_score: float
    recommendations: List[str]
    analysis_time_ms: int


class FailureModeAnalyzer:
    """
    Analyzes potential failure modes in plans and content.

    Uses FMEA (Failure Mode and Effects Analysis) methodology.
    """

    def __init__(self, llm_client=None):
        """
        Initialize the failure mode analyzer.

        Args:
            llm_client: LLM client for intelligent analysis
        """
        self.llm_client = llm_client

        # Common failure mode patterns
        self.failure_patterns = {
            FailureModeCategory.TECHNICAL: [
                "System crashes or freezes",
                "Data corruption or loss",
                "Network connectivity failures",
                "Software bugs or glitches",
                "Hardware malfunctions",
                "Integration failures",
                "Performance degradation",
                "Scalability issues",
            ],
            FailureModeCategory.OPERATIONAL: [
                "Process breakdowns",
                "Workflow interruptions",
                "Resource shortages",
                "Communication failures",
                "Coordination problems",
                "Quality control failures",
                "Documentation gaps",
                "Training deficiencies",
            ],
            FailureModeCategory.EXTERNAL: [
                "Third-party service outages",
                "API rate limiting",
                "Vendor changes",
                "Market conditions",
                "Regulatory changes",
                "Competitor actions",
                "Customer behavior changes",
                "Economic factors",
            ],
            FailureModeCategory.HUMAN: [
                "Human error",
                "Miscommunication",
                "Lack of expertise",
                "Fatigue or burnout",
                "Resistance to change",
                "Poor decision making",
                "Insufficient training",
                "Turnover or absence",
            ],
            FailureModeCategory.RESOURCE: [
                "Budget overruns",
                "Staffing shortages",
                "Equipment failures",
                "Supply chain disruptions",
                "Infrastructure limitations",
                "Time constraints",
                "Skill gaps",
                "Tool limitations",
            ],
            FailureModeCategory.QUALITY: [
                "Quality standards not met",
                "Customer dissatisfaction",
                "Defects or errors",
                "Performance issues",
                "Usability problems",
                "Security vulnerabilities",
                "Compliance violations",
                "Reputation damage",
            ],
            FailureModeCategory.SECURITY: [
                "Data breaches",
                "Unauthorized access",
                "Malware attacks",
                "Social engineering",
                "Insider threats",
                "System vulnerabilities",
                "Compliance violations",
                "Privacy violations",
            ],
            FailureModeCategory.COMPLIANCE: [
                "Regulatory violations",
                "Legal issues",
                "Contract breaches",
                "License violations",
                "Privacy violations",
                "Industry non-compliance",
                "Documentation failures",
                "Audit failures",
            ],
        }

        # Severity and probability mappings
        self.severity_scores = {
            FailureSeverity.NEGILIGIBLE: 1,
            FailureSeverity.MINOR: 2,
            FailureSeverity.MODERATE: 4,
            FailureSeverity.MAJOR: 7,
            FailureSeverity.CRITICAL: 9,
            FailureSeverity.CATASTROPHIC: 10,
        }

        self.probability_scores = {
            FailureProbability.RARE: 1,
            FailureProbability.UNLIKELY: 2,
            FailureProbability.OCCASIONAL: 4,
            FailureProbability.LIKELY: 6,
            FailureProbability.ALMOST_CERTAIN: 8,
        }

    async def analyze(self, plan: ExecutionPlan) -> FailureModeAnalysis:
        """
        Analyze failure modes for an execution plan.

        Args:
            plan: Execution plan to analyze

        Returns:
            Complete failure mode analysis
        """
        import time

        start_time = time.time()

        # Identify potential failure modes
        failure_modes = await self._identify_failure_modes(plan)

        # Calculate risk scores
        for failure_mode in failure_modes:
            failure_mode.risk_score = self._calculate_risk_score(failure_mode)

        # Generate mitigation strategies
        mitigation_strategies = await self._generate_mitigation_strategies(
            failure_modes
        )

        # Calculate overall risk
        overall_risk_score = self._calculate_overall_risk(failure_modes)

        # Generate recommendations
        recommendations = await self._generate_recommendations(
            failure_modes, mitigation_strategies
        )

        # Identify high-risk failures
        high_risk_failures = len([f for f in failure_modes if f.risk_score >= 7])

        analysis_time_ms = int((time.time() - start_time) * 1000)

        return FailureModeAnalysis(
            plan_id=plan.metadata.get("plan_id", "unknown"),
            analysis_date=datetime.now(),
            total_failure_modes=len(failure_modes),
            high_risk_failures=high_risk_failures,
            failure_modes=failure_modes,
            mitigation_strategies=mitigation_strategies,
            overall_risk_score=overall_risk_score,
            recommendations=recommendations,
            analysis_time_ms=analysis_time_ms,
        )

    async def _identify_failure_modes(self, plan: ExecutionPlan) -> List[FailureMode]:
        """Identify potential failure modes for the plan."""
        failure_modes = []

        # Analyze each step for failure modes
        for step in plan.steps:
            step_failures = await self._analyze_step_failures(step)
            failure_modes.extend(step_failures)

        # Analyze plan-level failure modes
        plan_failures = await self._analyze_plan_failures(plan)
        failure_modes.extend(plan_failures)

        # Remove duplicates and merge similar failures
        failure_modes = self._deduplicate_failure_modes(failure_modes)

        return failure_modes

    async def _analyze_step_failures(self, step: PlanStep) -> List[FailureMode]:
        """Analyze failure modes for a specific step."""
        failures = []

        # Technical failures
        if any(tool in ["api", "database", "external_service"] for tool in step.tools):
            failures.extend(self._create_technical_failures(step))

        # Operational failures
        if step.estimated_time_seconds > 3600:  # More than 1 hour
            failures.append(self._create_operational_failure(step, "timeout"))

        # Resource failures
        if step.estimated_cost > 1.0:  # High cost
            failures.append(self._create_resource_failure(step, "budget_overrun"))

        # Human failures
        if "manual" in step.tools or step.agent == "human_agent":
            failures.extend(self._create_human_failures(step))

        # Quality failures
        if step.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            failures.append(self._create_quality_failure(step))

        return failures

    async def _analyze_plan_failures(self, plan: ExecutionPlan) -> List[FailureMode]:
        """Analyze plan-level failure modes."""
        failures = []

        # Dependency failures
        if len(plan.steps) > 5:
            failures.append(self._create_dependency_failure(plan))

        # Integration failures
        agents = set(step.agent for step in plan.steps)
        if len(agents) > 3:
            failures.append(self._create_integration_failure(plan))

        # Timeline failures
        if plan.total_time_seconds > 7200:  # More than 2 hours
            failures.append(self._create_timeline_failure(plan))

        # Cost failures
        if plan.total_cost.total_cost_usd > 5.0:
            failures.append(self._create_cost_failure(plan))

        return failures

    def _create_technical_failures(self, step: PlanStep) -> List[FailureMode]:
        """Create technical failure modes for a step."""
        failures = []

        failure_id = f"tech_failure_{step.id}"
        failures.append(
            FailureMode(
                id=failure_id,
                name="Technical System Failure",
                description=f"Technical failure in {step.description}",
                category=FailureModeCategory.TECHNICAL,
                severity=FailureSeverity.MAJOR,
                probability=FailureProbability.OCCASIONAL,
                impact_description="Step execution fails, causing plan delay or failure",
                triggers=[
                    "System overload",
                    "Network connectivity issues",
                    "Software bugs",
                    "Hardware failures",
                ],
                warning_signs=[
                    "Increased error rates",
                    "Performance degradation",
                    "System warnings",
                    "Timeout indicators",
                ],
                affected_components=[step.id, step.agent],
                risk_score=0.0,
            )
        )

        return failures

    def _create_operational_failure(
        self, step: PlanStep, failure_type: str
    ) -> FailureMode:
        """Create operational failure mode."""
        if failure_type == "timeout":
            return FailureMode(
                id=f"timeout_failure_{step.id}",
                name="Step Timeout",
                description=f"Step {step.description} exceeds time limit",
                category=FailureModeCategory.OPERATIONAL,
                severity=FailureSeverity.MODERATE,
                probability=FailureProbability.LIKELY,
                impact_description="Step fails to complete in allocated time",
                triggers=[
                    "Complexity underestimation",
                    "Resource constraints",
                    "External dependencies",
                    "Performance issues",
                ],
                warning_signs=[
                    "Progress slowdown",
                    "Resource utilization spikes",
                    "Extended processing time",
                    "Queue buildup",
                ],
                affected_components=[step.id],
                risk_score=0.0,
            )

        return None

    def _create_resource_failure(
        self, step: PlanStep, failure_type: str
    ) -> FailureMode:
        """Create resource failure mode."""
        if failure_type == "budget_overrun":
            return FailureMode(
                id=f"budget_failure_{step.id}",
                name="Budget Overrun",
                description=f"Step {step.description} exceeds budget allocation",
                category=FailureModeCategory.RESOURCE,
                severity=FailureSeverity.MAJOR,
                probability=FailureProbability.OCCASIONAL,
                impact_description="Insufficient funds to complete step",
                triggers=[
                    "Cost underestimation",
                    "Price changes",
                    "Scope creep",
                    "Inefficiencies",
                ],
                warning_signs=[
                    "Cost tracking alerts",
                    "Budget consumption rate",
                    "Resource utilization",
                    "Vendor price changes",
                ],
                affected_components=[step.id, "budget"],
                risk_score=0.0,
            )

        return None

    def _create_human_failures(self, step: PlanStep) -> List[FailureMode]:
        """Create human-related failure modes."""
        failures = []

        failure_id = f"human_error_{step.id}"
        failures.append(
            FailureMode(
                id=failure_id,
                name="Human Error",
                description=f"Human error in executing {step.description}",
                category=FailureModeCategory.HUMAN,
                severity=FailureSeverity.MODERATE,
                probability=FailureProbability.OCCASIONAL,
                impact_description="Errors in manual execution or judgment",
                triggers=[
                    "Insufficient training",
                    "Fatigue or stress",
                    "Complexity",
                    "Time pressure",
                ],
                warning_signs=[
                    "Quality issues",
                    "Rework requirements",
                    "Error reports",
                    "Performance variations",
                ],
                affected_components=[step.id, step.agent],
                risk_score=0.0,
            )
        )

        return failures

    def _create_quality_failure(self, step: PlanStep) -> FailureMode:
        """Create quality-related failure mode."""
        return FailureMode(
            id=f"quality_failure_{step.id}",
            name="Quality Failure",
            description=f"Quality standards not met in {step.description}",
            category=FailureModeCategory.QUALITY,
            severity=FailureSeverity.MAJOR,
            probability=FailureProbability.UNLIKELY,
            impact_description="Output fails to meet quality requirements",
            triggers=[
                "Insufficient oversight",
                "Process gaps",
                "Resource constraints",
                "Complexity",
            ],
            warning_signs=[
                "Quality metrics decline",
                "Customer complaints",
                "Rework increases",
                "Audit failures",
            ],
            affected_components=[step.id, "quality_system"],
            risk_score=0.0,
        )

    def _create_dependency_failure(self, plan: ExecutionPlan) -> FailureMode:
        """Create dependency-related failure mode."""
        return FailureMode(
            id="dependency_failure",
            name="Dependency Chain Failure",
            description="Failure in dependency chain causing cascade failures",
            category=FailureModeCategory.OPERATIONAL,
            severity=FailureSeverity.CRITICAL,
            probability=FailureProbability.OCCASIONAL,
            impact_description="Multiple steps fail due to dependency issues",
            triggers=[
                "Upstream failures",
                "Integration issues",
                "Communication breakdowns",
                "Resource conflicts",
            ],
            warning_signs=[
                "Step delays",
                "Error propagation",
                "Resource bottlenecks",
                "Communication gaps",
            ],
            affected_components=[step.id for step in plan.steps],
            risk_score=0.0,
        )

    def _create_integration_failure(self, plan: ExecutionPlan) -> FailureMode:
        """Create integration-related failure mode."""
        return FailureMode(
            id="integration_failure",
            name="Multi-Agent Integration Failure",
            description="Failure in coordinating multiple agents",
            category=FailureModeCategory.TECHNICAL,
            severity=FailureSeverity.MAJOR,
            probability=FailureProbability.OCCASIONAL,
            impact_description="Poor coordination between different agents",
            triggers=[
                "Protocol mismatches",
                "Communication failures",
                "Data format issues",
                "Timing problems",
            ],
            warning_signs=[
                "Agent communication errors",
                "Data synchronization issues",
                "Performance bottlenecks",
                "Coordination delays",
            ],
            affected_components=[step.agent for step in plan.steps],
            risk_score=0.0,
        )

    def _create_timeline_failure(self, plan: ExecutionPlan) -> FailureMode:
        """Create timeline-related failure mode."""
        return FailureMode(
            id="timeline_failure",
            name="Timeline Overrun",
            description="Plan exceeds allocated timeline",
            category=FailureModeCategory.RESOURCE,
            severity=FailureSeverity.MODERATE,
            probability=FailureProbability.LIKELY,
            impact_description="Plan completion delayed beyond deadline",
            triggers=[
                "Complexity underestimation",
                "Resource constraints",
                "External dependencies",
                "Scope changes",
            ],
            warning_signs=[
                "Schedule slippage",
                "Resource utilization",
                "Progress tracking",
                "Milestone delays",
            ],
            affected_components=["timeline", "schedule"],
            risk_score=0.0,
        )

    def _create_cost_failure(self, plan: ExecutionPlan) -> FailureMode:
        """Create cost-related failure mode."""
        return FailureMode(
            id="cost_failure",
            name="Cost Overrun",
            description="Plan exceeds budget allocation",
            category=FailureModeCategory.RESOURCE,
            severity=FailureSeverity.MAJOR,
            probability=FailureProbability.OCCASIONAL,
            impact_description="Insufficient funds to complete plan",
            triggers=[
                "Cost underestimation",
                "Price changes",
                "Scope creep",
                "Inefficiencies",
            ],
            warning_signs=[
                "Budget consumption rate",
                "Cost tracking alerts",
                "Vendor price changes",
                "Resource costs",
            ],
            affected_components=["budget", "financial"],
            risk_score=0.0,
        )

    def _deduplicate_failure_modes(
        self, failure_modes: List[FailureMode]
    ) -> List[FailureMode]:
        """Remove duplicate failure modes and merge similar ones."""
        seen = set()
        unique_failures = []

        for failure in failure_modes:
            # Create a signature based on category and key characteristics
            signature = (failure.category.value, failure.name[:20])

            if signature not in seen:
                seen.add(signature)
                unique_failures.append(failure)

        return unique_failures

    def _calculate_risk_score(self, failure_mode: FailureMode) -> float:
        """Calculate risk score for a failure mode."""
        severity_score = self.severity_scores.get(failure_mode.severity, 5)
        probability_score = self.probability_scores.get(failure_mode.probability, 5)

        # Risk score = severity x probability (normalized to 1-10 scale)
        risk_score = (severity_score * probability_score) / 10

        return min(10.0, max(1.0, risk_score))

    async def _generate_mitigation_strategies(
        self, failure_modes: List[FailureMode]
    ) -> List[MitigationStrategy]:
        """Generate mitigation strategies for failure modes."""
        strategies = []

        for failure_mode in failure_modes:
            # Generate strategies based on failure mode
            mode_strategies = await self._create_mitigation_strategies(failure_mode)
            strategies.extend(mode_strategies)

        return strategies

    async def _create_mitigation_strategies(
        self, failure_mode: FailureMode
    ) -> List[MitigationStrategy]:
        """Create mitigation strategies for a specific failure mode."""
        strategies = []

        # Prevention strategy
        prevention = MitigationStrategy(
            failure_mode_id=failure_mode.id,
            strategy_type="prevention",
            description=f"Prevent {failure_mode.name} from occurring",
            implementation_steps=self._get_prevention_steps(failure_mode),
            effectiveness=0.8,
            cost=5.0,
            timeline="2-4 weeks",
            owner="team_lead",
        )
        strategies.append(prevention)

        # Detection strategy
        detection = MitigationStrategy(
            failure_mode_id=failure_mode.id,
            strategy_type="detection",
            description=f"Early detection of {failure_mode.name}",
            implementation_steps=self._get_detection_steps(failure_mode),
            effectiveness=0.7,
            cost=3.0,
            timeline="1-2 weeks",
            owner="quality_team",
        )
        strategies.append(detection)

        # Recovery strategy (for high-risk failures)
        if failure_mode.risk_score >= 7:
            recovery = MitigationStrategy(
                failure_mode_id=failure_mode.id,
                strategy_type="recovery",
                description=f"Recovery plan for {failure_mode.name}",
                implementation_steps=self._get_recovery_steps(failure_mode),
                effectiveness=0.6,
                cost=4.0,
                timeline="1-3 weeks",
                owner="operations_team",
            )
            strategies.append(recovery)

        return strategies

    def _get_prevention_steps(self, failure_mode: FailureMode) -> List[str]:
        """Get prevention steps for a failure mode."""
        common_steps = [
            "Conduct risk assessment",
            "Implement quality controls",
            "Provide training and documentation",
            "Establish clear procedures",
        ]

        category_specific = {
            FailureModeCategory.TECHNICAL: [
                "Implement system monitoring",
                "Add redundancy and failover",
                "Conduct regular testing",
                "Update systems and patches",
            ],
            FailureModeCategory.OPERATIONAL: [
                "Standardize processes",
                "Improve communication channels",
                "Implement checklists",
                "Conduct regular reviews",
            ],
            FailureModeCategory.HUMAN: [
                "Provide comprehensive training",
                "Implement peer review",
                "Create clear guidelines",
                "Reduce complexity",
            ],
        }

        steps = common_steps + category_specific.get(failure_mode.category, [])
        return steps[:4]  # Return top 4 steps

    def _get_detection_steps(self, failure_mode: FailureMode) -> List[str]:
        """Get detection steps for a failure mode."""
        return [
            f"Monitor for {failure_mode.name} indicators",
            "Implement early warning systems",
            "Conduct regular inspections",
            "Track performance metrics",
        ]

    def _get_recovery_steps(self, failure_mode: FailureMode) -> List[str]:
        """Get recovery steps for a failure mode."""
        return [
            f"Develop {failure_mode.name} response plan",
            "Establish recovery procedures",
            "Create backup systems",
            "Test recovery processes",
        ]

    def _calculate_overall_risk(self, failure_modes: List[FailureMode]) -> float:
        """Calculate overall risk score for all failure modes."""
        if not failure_modes:
            return 0.0

        # Weighted average of risk scores
        total_weight = 0
        weighted_sum = 0

        for failure in failure_modes:
            weight = 1.0  # Equal weighting for now
            weighted_sum += failure.risk_score * weight
            total_weight += weight

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    async def _generate_recommendations(
        self,
        failure_modes: List[FailureMode],
        mitigation_strategies: List[MitigationStrategy],
    ) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []

        # High-risk failure recommendations
        high_risk_failures = [f for f in failure_modes if f.risk_score >= 7]
        if high_risk_failures:
            recommendations.append(
                f"Priority: Address {len(high_risk_failures)} high-risk failure modes immediately"
            )

        # Category-based recommendations
        category_counts = {}
        for failure in failure_modes:
            category_counts[failure.category.value] = (
                category_counts.get(failure.category.value, 0) + 1
            )

        most_common_category = (
            max(category_counts.items(), key=lambda x: x[1])[0]
            if category_counts
            else None
        )
        if most_common_category:
            recommendations.append(
                f"Focus on {most_common_category} failures ({category_counts[most_common_category]} occurrences)"
            )

        # Mitigation strategy recommendations
        if mitigation_strategies:
            avg_effectiveness = sum(
                s.effectiveness for s in mitigation_strategies
            ) / len(mitigation_strategies)
            if avg_effectiveness < 0.7:
                recommendations.append(
                    "Improve mitigation strategy effectiveness through better planning"
                )

        # General recommendations
        recommendations.extend(
            [
                "Implement continuous monitoring and early warning systems",
                "Conduct regular failure mode reviews and updates",
                "Establish clear ownership and accountability for risk mitigation",
                "Document and communicate failure mode analysis to all stakeholders",
            ]
        )

        return recommendations[:6]  # Return top 6 recommendations

    def get_analysis_stats(self, analyses: List[FailureModeAnalysis]) -> Dict[str, Any]:
        """Get statistics about failure mode analyses."""
        if not analyses:
            return {}

        total_analyses = len(analyses)
        total_failures = sum(a.total_failure_modes for a in analyses)
        total_high_risk = sum(a.high_risk_failures for a in analyses)
        avg_risk_score = sum(a.overall_risk_score for a in analyses) / total_analyses

        # Category distribution
        category_counts = {}
        for analysis in analyses:
            for failure in analysis.failure_modes:
                category = failure.category.value
                category_counts[category] = category_counts.get(category, 0) + 1

        # Severity distribution
        severity_counts = {}
        for analysis in analyses:
            for failure in analysis.failure_modes:
                severity = failure.severity.value
                severity_counts[severity] = severity_counts.get(severity, 0) + 1

        return {
            "total_analyses": total_analyses,
            "total_failures_identified": total_failures,
            "total_high_risk_failures": total_high_risk,
            "average_risk_score": avg_risk_score,
            "failure_category_distribution": category_counts,
            "failure_severity_distribution": severity_counts,
            "average_analysis_time_ms": sum(a.analysis_time_ms for a in analyses)
            / total_analyses,
        }
