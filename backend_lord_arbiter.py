# backend/agents/council_of_lords/arbiter.py
# RaptorFlow Codex - Arbiter Lord Agent
# Phase 2A Week 6 - Conflict Resolution & Fair Arbitration

from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from abc import ABC
import uuid

from agents.base_agent import BaseAgent, AgentRole, AgentStatus, Capability, CapabilityHandler

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & DATA STRUCTURES
# ============================================================================

class ConflictType(Enum):
    """Types of conflicts"""
    RESOURCE_ALLOCATION = "resource_allocation"
    PRIORITY_DISPUTE = "priority_dispute"
    GOAL_CONFLICT = "goal_conflict"
    STAKEHOLDER_DISAGREEMENT = "stakeholder_disagreement"
    DECISION_CHALLENGE = "decision_challenge"


class ConflictSeverity(Enum):
    """Conflict severity levels"""
    CRITICAL = "critical"  # Blocks operations
    HIGH = "high"  # Significantly impacts
    MEDIUM = "medium"  # Moderate impact
    LOW = "low"  # Minor impact


class ResolutionStatus(Enum):
    """Resolution status"""
    PROPOSED = "proposed"
    PENDING_REVIEW = "pending_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    APPEALED = "appealed"
    FINAL = "final"


class FairnessMetric(Enum):
    """Fairness metrics"""
    EQUAL_TREATMENT = "equal_treatment"
    PROPORTIONAL_BENEFIT = "proportional_benefit"
    NEEDS_BASED = "needs_based"
    CONSENSUS_BASED = "consensus_based"


class ConflictCase:
    """Represents a conflict case"""

    def __init__(
        self,
        case_id: str,
        conflict_type: str,
        title: str,
        description: str,
        parties_involved: List[str],
        conflicting_goals: List[str],
        severity: str,
        impact_analysis: Dict[str, float],
    ):
        self.case_id = case_id
        self.conflict_type = conflict_type
        self.title = title
        self.description = description
        self.parties_involved = parties_involved
        self.conflicting_goals = conflicting_goals
        self.severity = severity
        self.impact_analysis = impact_analysis
        self.created_at = datetime.utcnow()
        self.status = "open"
        self.resolution_attempts = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "case_id": self.case_id,
            "conflict_type": self.conflict_type,
            "title": self.title,
            "description": self.description,
            "parties_involved": self.parties_involved,
            "conflicting_goals": self.conflicting_goals,
            "severity": self.severity,
            "impact_analysis": self.impact_analysis,
            "status": self.status,
            "resolution_attempts": len(self.resolution_attempts),
            "created_at": self.created_at.isoformat(),
        }


class ResolutionProposal:
    """Resolution proposal for a conflict"""

    def __init__(
        self,
        proposal_id: str,
        case_id: str,
        proposed_solution: str,
        winner_party: Optional[str],
        resource_allocation: Dict[str, float],
        trade_offs: List[str],
        fairness_score: float,
        implementation_steps: List[str],
    ):
        self.proposal_id = proposal_id
        self.case_id = case_id
        self.proposed_solution = proposed_solution
        self.winner_party = winner_party  # Can be None for split decisions
        self.resource_allocation = resource_allocation
        self.trade_offs = trade_offs
        self.fairness_score = min(100, max(0, fairness_score))
        self.implementation_steps = implementation_steps
        self.created_at = datetime.utcnow()
        self.status = ResolutionStatus.PROPOSED.value
        self.justification = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "proposal_id": self.proposal_id,
            "case_id": self.case_id,
            "proposed_solution": self.proposed_solution,
            "winner_party": self.winner_party,
            "resource_allocation": self.resource_allocation,
            "trade_offs": self.trade_offs,
            "fairness_score": self.fairness_score,
            "implementation_steps": self.implementation_steps,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }


class ArbitrationDecision:
    """Final arbitration decision"""

    def __init__(
        self,
        decision_id: str,
        case_id: str,
        proposal_id: str,
        ruling: str,
        enforcement_strategy: str,
        stakeholder_satisfaction: Dict[str, float],
        fairness_rationale: str,
    ):
        self.decision_id = decision_id
        self.case_id = case_id
        self.proposal_id = proposal_id
        self.ruling = ruling
        self.enforcement_strategy = enforcement_strategy
        self.stakeholder_satisfaction = stakeholder_satisfaction
        self.fairness_rationale = fairness_rationale
        self.created_at = datetime.utcnow()
        self.enforcement_status = "pending"
        self.appeal_window_closed = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "decision_id": self.decision_id,
            "case_id": self.case_id,
            "proposal_id": self.proposal_id,
            "ruling": self.ruling,
            "enforcement_strategy": self.enforcement_strategy,
            "stakeholder_satisfaction": self.stakeholder_satisfaction,
            "fairness_rationale": self.fairness_rationale,
            "enforcement_status": self.enforcement_status,
            "created_at": self.created_at.isoformat(),
        }


class Appeal:
    """Appeal of an arbitration decision"""

    def __init__(
        self,
        appeal_id: str,
        decision_id: str,
        appellant_party: str,
        appeal_grounds: List[str],
        requested_review_points: List[str],
    ):
        self.appeal_id = appeal_id
        self.decision_id = decision_id
        self.appellant_party = appellant_party
        self.appeal_grounds = appeal_grounds
        self.requested_review_points = requested_review_points
        self.created_at = datetime.utcnow()
        self.status = "pending"
        self.review_notes = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "appeal_id": self.appeal_id,
            "decision_id": self.decision_id,
            "appellant_party": self.appellant_party,
            "appeal_grounds": self.appeal_grounds,
            "requested_review_points": self.requested_review_points,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }


class FairnessReport:
    """Report on fairness of decisions"""

    def __init__(
        self,
        report_id: str,
        evaluation_period_days: int,
        total_cases_handled: int,
        average_fairness_score: float,
        stakeholder_satisfaction_average: float,
        bias_indicators: List[str],
        improvement_recommendations: List[str],
    ):
        self.report_id = report_id
        self.evaluation_period_days = evaluation_period_days
        self.total_cases_handled = total_cases_handled
        self.average_fairness_score = min(100, max(0, average_fairness_score))
        self.stakeholder_satisfaction_average = min(100, max(0, stakeholder_satisfaction_average))
        self.bias_indicators = bias_indicators
        self.improvement_recommendations = improvement_recommendations
        self.created_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "report_id": self.report_id,
            "evaluation_period_days": self.evaluation_period_days,
            "total_cases_handled": self.total_cases_handled,
            "average_fairness_score": self.average_fairness_score,
            "stakeholder_satisfaction_average": self.stakeholder_satisfaction_average,
            "bias_indicators": self.bias_indicators,
            "improvement_recommendations": self.improvement_recommendations,
            "created_at": self.created_at.isoformat(),
        }


# ============================================================================
# ARBITER LORD AGENT
# ============================================================================


class ArbiterLord(BaseAgent):
    """
    Arbiter Lord - Manages conflict resolution and fair arbitration.
    Ensures fairness in decision-making and resolves stakeholder conflicts.
    """

    def __init__(self):
        super().__init__()
        self.name = "Arbiter Lord"
        self.role = AgentRole.arbiter
        self.status = AgentStatus.idle

        # Register capabilities
        self.capabilities = [
            Capability(name="register_conflict", handler=self._register_conflict),
            Capability(name="analyze_conflict", handler=self._analyze_conflict),
            Capability(name="propose_resolution", handler=self._propose_resolution),
            Capability(name="make_arbitration_decision", handler=self._make_arbitration_decision),
            Capability(name="handle_appeal", handler=self._handle_appeal),
        ]

        # State storage
        self.conflict_cases: Dict[str, ConflictCase] = {}
        self.resolution_proposals: Dict[str, ResolutionProposal] = {}
        self.arbitration_decisions: Dict[str, ArbitrationDecision] = {}
        self.appeals: Dict[str, Appeal] = {}
        self.fairness_reports: Dict[str, FairnessReport] = {}

        # Performance metrics
        self.total_cases_handled = 0
        self.average_fairness_score = 0.0
        self.stakeholder_satisfaction_score = 0.0
        self.appeal_rate = 0.0
        self.resolution_success_rate = 0.0

    async def execute(self, task: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Arbiter capability"""
        logger.info(f"⚖️ Arbiter Lord executing: {task}")

        try:
            self.status = AgentStatus.active

            # Route to capability handler
            for capability in self.capabilities:
                if capability.name == task:
                    result = await capability.handler(**parameters)
                    self.status = AgentStatus.idle
                    return result

            raise ValueError(f"Unknown task: {task}")

        except Exception as e:
            logger.error(f"❌ Arbiter execution error: {e}")
            self.status = AgentStatus.error
            return {"success": False, "error": str(e)}

    async def _register_conflict(self, **kwargs) -> Dict[str, Any]:
        """Register a conflict case"""
        conflict_type = kwargs.get("conflict_type", "goal_conflict")
        title = kwargs.get("title", "Conflict")
        description = kwargs.get("description", "")
        parties_involved = kwargs.get("parties_involved", [])
        conflicting_goals = kwargs.get("conflicting_goals", [])

        case_id = f"case_{uuid.uuid4().hex[:8]}"

        try:
            # Assess severity based on parties and goals
            severity = ConflictSeverity.MEDIUM.value
            if len(parties_involved) >= 3 or len(conflicting_goals) >= 3:
                severity = ConflictSeverity.HIGH.value
            elif len(parties_involved) == 1:
                severity = ConflictSeverity.LOW.value

            # Create impact analysis
            impact_analysis = {
                "operational_impact": 0.5 + len(parties_involved) * 0.1,
                "stakeholder_impact": 0.6,
                "resource_impact": 0.5,
            }

            # Create case
            case = ConflictCase(
                case_id=case_id,
                conflict_type=conflict_type,
                title=title,
                description=description,
                parties_involved=parties_involved,
                conflicting_goals=conflicting_goals,
                severity=severity,
                impact_analysis=impact_analysis,
            )

            self.conflict_cases[case_id] = case
            self.total_cases_handled += 1

            logger.info(f"✅ Conflict registered: {title} ({case_id})")

            return {
                "success": True,
                "case_id": case_id,
                "title": title,
                "severity": severity,
                "parties_count": len(parties_involved),
                "impact_analysis": impact_analysis,
            }

        except Exception as e:
            logger.error(f"Conflict registration error: {e}")
            raise

    async def _analyze_conflict(self, **kwargs) -> Dict[str, Any]:
        """Analyze a conflict case"""
        case_id = kwargs.get("case_id")
        additional_context = kwargs.get("additional_context", {})

        if case_id not in self.conflict_cases:
            raise ValueError(f"Case {case_id} not found")

        try:
            case = self.conflict_cases[case_id]

            # Analyze root causes
            root_causes = [
                f"Goal conflict between {case.parties_involved[i % len(case.parties_involved)]}"
                for i in range(len(case.conflicting_goals))
            ]

            # Identify stakeholders
            stakeholders = case.parties_involved.copy()

            # Assess impacts
            impact_summary = {
                "operational": case.impact_analysis.get("operational_impact", 0.5),
                "stakeholder": case.impact_analysis.get("stakeholder_impact", 0.6),
                "resource": case.impact_analysis.get("resource_impact", 0.5),
            }

            logger.info(f"✅ Conflict analyzed: {case_id}")

            return {
                "success": True,
                "case_id": case_id,
                "root_causes": root_causes,
                "stakeholders": stakeholders,
                "impact_summary": impact_summary,
                "recommendations": [
                    "Consider negotiation between parties",
                    "Allocate mediator",
                    "Review organizational priorities",
                ],
            }

        except Exception as e:
            logger.error(f"Conflict analysis error: {e}")
            raise

    async def _propose_resolution(self, **kwargs) -> Dict[str, Any]:
        """Propose a resolution to conflict"""
        case_id = kwargs.get("case_id")
        proposed_solution = kwargs.get("proposed_solution", "Balanced approach")
        priority_adjustment = kwargs.get("priority_adjustment", {})

        if case_id not in self.conflict_cases:
            raise ValueError(f"Case {case_id} not found")

        try:
            case = self.conflict_cases[case_id]
            proposal_id = f"prop_{uuid.uuid4().hex[:8]}"

            # Determine winner or split decision
            winner_party = case.parties_involved[0] if len(case.parties_involved) == 1 else None

            # Create resource allocation
            resource_allocation = {}
            for party in case.parties_involved:
                resource_allocation[party] = 1.0 / len(case.parties_involved) if case.parties_involved else 0.5

            # Identify trade-offs
            trade_offs = [
                f"Party {case.parties_involved[i]} may need to adjust timeline"
                for i in range(min(2, len(case.parties_involved)))
            ]

            # Calculate fairness score
            fairness_score = 70 + (len(case.parties_involved) * 5)

            # Create proposal
            proposal = ResolutionProposal(
                proposal_id=proposal_id,
                case_id=case_id,
                proposed_solution=proposed_solution,
                winner_party=winner_party,
                resource_allocation=resource_allocation,
                trade_offs=trade_offs,
                fairness_score=fairness_score,
                implementation_steps=[
                    "Step 1: Communicate decision to all parties",
                    "Step 2: Adjust resource allocation",
                    "Step 3: Monitor compliance",
                    "Step 4: Review outcomes",
                ],
            )

            proposal.justification = f"Resolution balances interests of {len(case.parties_involved)} parties"

            self.resolution_proposals[proposal_id] = proposal
            case.resolution_attempts.append(proposal_id)

            logger.info(f"✅ Resolution proposed: {proposed_solution} ({proposal_id})")

            return {
                "success": True,
                "proposal_id": proposal_id,
                "case_id": case_id,
                "proposed_solution": proposed_solution,
                "winner_party": winner_party,
                "fairness_score": fairness_score,
                "resource_allocation": resource_allocation,
                "trade_offs": trade_offs,
            }

        except Exception as e:
            logger.error(f"Resolution proposal error: {e}")
            raise

    async def _make_arbitration_decision(self, **kwargs) -> Dict[str, Any]:
        """Make final arbitration decision"""
        case_id = kwargs.get("case_id")
        proposal_id = kwargs.get("proposal_id")
        enforcement_method = kwargs.get("enforcement_method", "standard")

        if case_id not in self.conflict_cases or proposal_id not in self.resolution_proposals:
            raise ValueError("Case or proposal not found")

        try:
            case = self.conflict_cases[case_id]
            proposal = self.resolution_proposals[proposal_id]

            decision_id = f"dec_{uuid.uuid4().hex[:8]}"

            # Create stakeholder satisfaction scores
            stakeholder_satisfaction = {}
            for party in case.parties_involved:
                # Satisfaction depends on whether they got their preference
                satisfaction = 50 + (25 if proposal.winner_party == party else 0)
                if proposal.winner_party is None:  # Split decision
                    satisfaction = 65
                stakeholder_satisfaction[party] = satisfaction

            # Develop enforcement strategy
            enforcement_strategy = f"Enforce via {enforcement_method} method with quarterly reviews"

            # Create decision
            decision = ArbitrationDecision(
                decision_id=decision_id,
                case_id=case_id,
                proposal_id=proposal_id,
                ruling=f"Approved: {proposal.proposed_solution}",
                enforcement_strategy=enforcement_strategy,
                stakeholder_satisfaction=stakeholder_satisfaction,
                fairness_rationale=proposal.justification,
            )

            self.arbitration_decisions[decision_id] = decision
            case.status = "resolved"

            # Update metrics
            avg_satisfaction = sum(stakeholder_satisfaction.values()) / len(stakeholder_satisfaction)
            self.stakeholder_satisfaction_score = (
                (self.stakeholder_satisfaction_score * (self.total_cases_handled - 1) + avg_satisfaction)
                / self.total_cases_handled
            )
            self.average_fairness_score = (
                (self.average_fairness_score * (self.total_cases_handled - 1) + proposal.fairness_score)
                / self.total_cases_handled
            )

            logger.info(f"✅ Decision made: {decision_id}")

            return {
                "success": True,
                "decision_id": decision_id,
                "ruling": decision.ruling,
                "enforcement_strategy": enforcement_strategy,
                "stakeholder_satisfaction": stakeholder_satisfaction,
                "fairness_score": proposal.fairness_score,
            }

        except Exception as e:
            logger.error(f"Arbitration decision error: {e}")
            raise

    async def _handle_appeal(self, **kwargs) -> Dict[str, Any]:
        """Handle appeal of arbitration decision"""
        decision_id = kwargs.get("decision_id")
        appellant_party = kwargs.get("appellant_party", "")
        appeal_grounds = kwargs.get("appeal_grounds", [])
        requested_review_points = kwargs.get("requested_review_points", [])

        if decision_id not in self.arbitration_decisions:
            raise ValueError(f"Decision {decision_id} not found")

        try:
            decision = self.arbitration_decisions[decision_id]
            appeal_id = f"app_{uuid.uuid4().hex[:8]}"

            # Check if appeal window is still open
            days_since_decision = (datetime.utcnow() - decision.created_at).days
            appeal_window_open = days_since_decision <= 14

            if not appeal_window_open:
                return {
                    "success": False,
                    "error": f"Appeal window closed (decision made {days_since_decision} days ago)",
                }

            # Create appeal
            appeal = Appeal(
                appeal_id=appeal_id,
                decision_id=decision_id,
                appellant_party=appellant_party,
                appeal_grounds=appeal_grounds,
                requested_review_points=requested_review_points,
            )

            # Assess appeal merit
            merit_score = min(100, len(appeal_grounds) * 20 + len(requested_review_points) * 10)

            if merit_score >= 50:
                appeal.status = "granted"
                appeal.review_notes = "Appeal accepted for review"
            else:
                appeal.status = "denied"
                appeal.review_notes = "Insufficient grounds for appeal"

            self.appeals[appeal_id] = appeal

            logger.info(f"✅ Appeal processed: {appeal_id}")

            return {
                "success": True,
                "appeal_id": appeal_id,
                "decision_id": decision_id,
                "status": appeal.status,
                "merit_score": merit_score,
                "review_notes": appeal.review_notes,
            }

        except Exception as e:
            logger.error(f"Appeal handling error: {e}")
            raise

    # ============================================================================
    # HELPER METHODS
    # ============================================================================

    async def get_recent_cases(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conflict cases"""
        cases = list(self.conflict_cases.values())[-limit:]
        return [c.to_dict() for c in cases]

    async def get_recent_decisions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent arbitration decisions"""
        decisions = list(self.arbitration_decisions.values())[-limit:]
        return [d.to_dict() for d in decisions]

    async def get_recent_appeals(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent appeals"""
        appeals = list(self.appeals.values())[-limit:]
        return [a.to_dict() for a in appeals]

    async def generate_fairness_report(
        self, evaluation_period_days: int = 30
    ) -> Dict[str, Any]:
        """Generate fairness report"""
        report_id = f"report_{uuid.uuid4().hex[:8]}"

        # Get cases from period
        cutoff_date = datetime.utcnow() - timedelta(days=evaluation_period_days)
        recent_cases = [c for c in self.conflict_cases.values() if c.created_at >= cutoff_date]

        # Identify potential biases
        bias_indicators = []
        if self.total_cases_handled > 0:
            satisfaction = self.stakeholder_satisfaction_score
            if satisfaction < 60:
                bias_indicators.append("Low stakeholder satisfaction - possible fairness concerns")
            if self.average_fairness_score < 70:
                bias_indicators.append("Fairness scores below optimal - review decision criteria")

        # Generate recommendations
        recommendations = [
            "Continue monitoring stakeholder satisfaction",
            "Review decision criteria for consistency",
            "Improve appeal documentation process",
        ]

        report = FairnessReport(
            report_id=report_id,
            evaluation_period_days=evaluation_period_days,
            total_cases_handled=len(recent_cases),
            average_fairness_score=self.average_fairness_score,
            stakeholder_satisfaction_average=self.stakeholder_satisfaction_score,
            bias_indicators=bias_indicators,
            improvement_recommendations=recommendations,
        )

        self.fairness_reports[report_id] = report

        return report.to_dict()

    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get Arbiter performance summary"""
        return {
            "cases_handled": self.total_cases_handled,
            "average_fairness_score": self.average_fairness_score,
            "stakeholder_satisfaction": self.stakeholder_satisfaction_score,
            "appeal_rate": self.appeal_rate,
            "resolution_success_rate": self.resolution_success_rate,
            "open_cases": sum(1 for c in self.conflict_cases.values() if c.status == "open"),
            "resolved_cases": sum(1 for c in self.conflict_cases.values() if c.status == "resolved"),
            "status": self.status.value,
        }
