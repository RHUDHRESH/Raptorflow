"""
Approval Risk Rules - Determines when approval is required

Defines business rules for when human approval is needed based on
operation type, risk level, cost, and other factors.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

from .models import RequestType, RiskLevel

logger = logging.getLogger(__name__)


@dataclass
class ApprovalRule:
    """Rule for determining approval requirements."""

    request_type: RequestType
    min_risk_level: RiskLevel
    max_cost: Optional[float] = None
    requires_approval: bool = True
    description: str = ""


class ApprovalRiskRules:
    """Manages approval risk rules and requirements."""

    def __init__(self, workspace_config: Optional[Dict[str, Any]] = None):
        self.workspace_config = workspace_config or {}
        self.rules = self._load_default_rules()
        self._apply_workspace_overrides()

    def requires_approval(
        self,
        action_type: RequestType,
        risk_level: RiskLevel,
        cost: float,
        user_tier: str = "basic",
    ) -> bool:
        """
        Determine if approval is required.

        Args:
            action_type: Type of operation
            risk_level: Risk level (1-4)
            cost: Estimated cost in USD
            user_tier: User's subscription tier

        Returns:
            True if approval required
        """
        try:
            # Check specific rules first
            for rule in self.rules:
                if (
                    rule.request_type == action_type
                    and risk_level.value >= rule.min_risk_level.value
                ):

                    # Check cost threshold if specified
                    if rule.max_cost is not None and cost > rule.max_cost:
                        return True

                    return rule.requires_approval

            # Default rules based on thresholds
            if cost > self._get_cost_threshold(user_tier):
                return True

            if risk_level.value >= RiskLevel.HIGH.value:
                return True

            # Special cases
            if action_type in [RequestType.EXTERNAL_POST, RequestType.DATA_DELETION]:
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to check approval requirement: {e}")
            # Default to requiring approval on error
            return True

    def get_approval_reason(
        self,
        action_type: RequestType,
        risk_level: RiskLevel,
        cost: float,
        user_tier: str = "basic",
    ) -> str:
        """
        Get reason for approval requirement.

        Args:
            action_type: Type of operation
            risk_level: Risk level
            cost: Estimated cost
            user_tier: User's tier

        Returns:
            Human-readable reason
        """
        reasons = []

        # Check specific rules
        for rule in self.rules:
            if (
                rule.request_type == action_type
                and risk_level.value >= rule.min_risk_level.value
            ):

                if rule.max_cost is not None and cost > rule.max_cost:
                    reasons.append(
                        f"Cost ${cost:.2f} exceeds threshold ${rule.max_cost:.2f}"
                    )

                if rule.requires_approval:
                    reasons.append(rule.description)

        # Default reasons
        if cost > self._get_cost_threshold(user_tier):
            reasons.append(f"Cost ${cost:.2f} exceeds tier limit")

        if risk_level.value >= RiskLevel.HIGH.value:
            reasons.append(f"High risk operation (level {risk_level.value})")

        if action_type == RequestType.EXTERNAL_POST:
            reasons.append("External content posting requires review")

        if action_type == RequestType.DATA_DELETION:
            reasons.append("Data deletion is irreversible")

        return "; ".join(reasons) if reasons else "Standard approval requirement"

    def _load_default_rules(self) -> list[ApprovalRule]:
        """Load default approval rules."""
        return [
            # Content generation rules
            ApprovalRule(
                request_type=RequestType.CONTENT_GENERATION,
                min_risk_level=RiskLevel.HIGH,
                max_cost=0.50,
                requires_approval=True,
                description="High-risk content generation requires approval",
            ),
            # External posting rules
            ApprovalRule(
                request_type=RequestType.EXTERNAL_POST,
                min_risk_level=RiskLevel.LOW,
                requires_approval=True,
                description="All external posts require approval",
            ),
            # Data deletion rules
            ApprovalRule(
                request_type=RequestType.DATA_DELETION,
                min_risk_level=RiskLevel.LOW,
                requires_approval=True,
                description="Data deletion operations require approval",
            ),
            # High cost operations
            ApprovalRule(
                request_type=RequestType.HIGH_COST_OPERATION,
                min_risk_level=RiskLevel.MEDIUM,
                max_cost=1.00,
                requires_approval=True,
                description="High-cost operations require approval",
            ),
            # Sensitive access rules
            ApprovalRule(
                request_type=RequestType.SENSITIVE_ACCESS,
                min_risk_level=RiskLevel.MEDIUM,
                requires_approval=True,
                description="Sensitive system access requires approval",
            ),
            # System changes
            ApprovalRule(
                request_type=RequestType.SYSTEM_CHANGE,
                min_risk_level=RiskLevel.HIGH,
                requires_approval=True,
                description="System changes require approval",
            ),
        ]

    def _apply_workspace_overrides(self):
        """Apply workspace-specific rule overrides."""
        if not self.workspace_config:
            return

        # Override cost thresholds by tier
        tier_thresholds = self.workspace_config.get("approval_cost_thresholds", {})
        if tier_thresholds:
            self.cost_thresholds.update(tier_thresholds)

        # Override specific rules
        rule_overrides = self.workspace_config.get("approval_rule_overrides", [])
        for override in rule_overrides:
            try:
                rule = ApprovalRule(
                    request_type=RequestType(override["request_type"]),
                    min_risk_level=RiskLevel(override["min_risk_level"]),
                    max_cost=override.get("max_cost"),
                    requires_approval=override.get("requires_approval", True),
                    description=override.get("description", ""),
                )
                self.rules.append(rule)
            except Exception as e:
                logger.warning(f"Invalid rule override: {e}")

    def _get_cost_threshold(self, user_tier: str) -> float:
        """Get cost threshold for user tier."""
        thresholds = {"basic": 0.25, "pro": 0.50, "enterprise": 1.00, "unlimited": 5.00}
        return thresholds.get(user_tier, 0.25)

    # Default cost thresholds by tier
    cost_thresholds = {
        "basic": 0.25,
        "pro": 0.50,
        "enterprise": 1.00,
        "unlimited": 5.00,
    }
