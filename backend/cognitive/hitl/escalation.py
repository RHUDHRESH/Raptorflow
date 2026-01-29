"""
Escalation Manager - Handles approval escalation workflows

Manages multi-level approval processes, escalation chains,
and reviewer assignment for team workflows.
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ...redis.client import RedisClient
from ..models import ApprovalRequest, EscalationInfo

logger = logging.getLogger(__name__)


@dataclass
class EscalationRule:
    """Rule for approval escalation."""

    trigger_condition: str  # "timeout", "rejection", "high_risk"
    escalation_level: int
    escalate_to_role: str
    timeout_hours: int
    auto_approve_if_no_response: bool


class EscalationManager:
    """Manages approval escalation workflows."""

    def __init__(self, redis_client: Optional[RedisClient] = None):
        self.redis = redis_client or RedisClient()
        self.escalation_key_prefix = "approval_escalation:"
        self.rules_key_prefix = "escalation_rules:"
        self.default_rules = self._load_default_rules()

    async def escalate(
        self,
        gate_id: str,
        reason: str,
        escalate_to: Optional[str] = None,
        escalate_to_role: Optional[str] = None,
    ) -> bool:
        """
        Escalate an approval request.

        Args:
            gate_id: Approval gate identifier
            reason: Reason for escalation
            escalate_to: Specific user to escalate to
            escalate_to_role: Role to escalate to

        Returns:
            Success status
        """
        try:
            # Get original approval request
            gate_key = f"approval_gate:{gate_id}"
            request_data = await self.redis.get(gate_key)

            if not request_data:
                logger.error(f"Approval gate {gate_id} not found")
                return False

            request = json.loads(request_data)

            # Determine escalation target
            target_user = escalate_to
            if not target_user and escalate_to_role:
                target_user = await self._find_user_by_role(
                    request["workspace_id"], escalate_to_role
                )

            if not target_user:
                logger.error(f"No escalation target found for gate {gate_id}")
                return False

            # Create escalation record
            escalation_info = EscalationInfo(
                gate_id=gate_id,
                escalated_to=target_user,
                reason=reason,
                escalated_at=datetime.now(),
                original_approver=request["user_id"],
            )

            # Store escalation
            escalation_key = f"{self.escalation_key_prefix}{gate_id}"
            escalation_data = {
                "gate_id": gate_id,
                "escalated_to": target_user,
                "reason": reason,
                "escalated_at": escalation_info.escalated_at.isoformat(),
                "original_approver": request["user_id"],
                "status": "pending",
            }

            await self.redis.set(
                escalation_key,
                json.dumps(escalation_data),
                ex=86400 * 7,  # Keep for 7 days
            )

            # Update approval gate to show escalated
            request["escalated_to"] = target_user
            request["escalation_reason"] = reason
            await self.redis.set(gate_key, json.dumps(request))

            # Notify escalated user
            await self._notify_escalated_user(target_user, gate_id, reason)

            logger.info(f"Escalated gate {gate_id} to {target_user}")
            return True

        except Exception as e:
            logger.error(f"Failed to escalate approval: {e}")
            return False

    async def assign_reviewer(
        self, gate_id: str, reviewer_id: str, workspace_id: str
    ) -> bool:
        """
        Assign a specific reviewer for an approval.

        Args:
            gate_id: Approval gate identifier
            reviewer_id: Reviewer user ID
            workspace_id: Workspace identifier

        Returns:
            Success status
        """
        try:
            # Check if reviewer has permission
            if not await self._check_reviewer_permission(reviewer_id, workspace_id):
                logger.error(f"Reviewer {reviewer_id} lacks permission")
                return False

            # Update approval gate
            gate_key = f"approval_gate:{gate_id}"
            request_data = await self.redis.get(gate_key)

            if not request_data:
                logger.error(f"Approval gate {gate_id} not found")
                return False

            request = json.loads(request_data)
            request["assigned_reviewer"] = reviewer_id
            request["reviewer_assigned_at"] = datetime.now().isoformat()

            await self.redis.set(gate_key, json.dumps(request))

            # Notify reviewer
            await self._notify_reviewer_assigned(reviewer_id, gate_id)

            logger.info(f"Assigned reviewer {reviewer_id} to gate {gate_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to assign reviewer: {e}")
            return False

    async def check_escalation_rules(self, gate_id: str) -> List[str]:
        """
        Check if escalation rules should be triggered.

        Args:
            gate_id: Approval gate identifier

        Returns:
            List of triggered escalation actions
        """
        try:
            triggered_actions = []

            # Get approval request
            gate_key = f"approval_gate:{gate_id}"
            request_data = await self.redis.get(gate_key)

            if not request_data:
                return triggered_actions

            request = json.loads(request_data)
            workspace_id = request["workspace_id"]

            # Get workspace escalation rules
            rules = await self._get_workspace_rules(workspace_id)

            for rule in rules:
                if await self._evaluate_rule(rule, request):
                    action = await self._execute_rule(rule, gate_id, request)
                    if action:
                        triggered_actions.append(action)

            return triggered_actions

        except Exception as e:
            logger.error(f"Failed to check escalation rules: {e}")
            return []

    async def get_escalation_history(
        self, workspace_id: str, days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get escalation history for a workspace.

        Args:
            workspace_id: Workspace identifier
            days: Number of days to look back

        Returns:
            List of escalation records
        """
        try:
            # This would need to query escalation records by workspace and date
            # For now, return empty list
            return []

        except Exception as e:
            logger.error(f"Failed to get escalation history: {e}")
            return []

    async def _find_user_by_role(self, workspace_id: str, role: str) -> Optional[str]:
        """Find user by role in workspace."""
        try:
            # This would integrate with user management system
            # For now, return placeholder
            role_mappings = {
                "admin": "workspace_admin",
                "manager": "workspace_manager",
                "senior_reviewer": "senior_approver",
            }

            return role_mappings.get(role)

        except Exception as e:
            logger.error(f"Failed to find user by role: {e}")
            return None

    async def _check_reviewer_permission(
        self, reviewer_id: str, workspace_id: str
    ) -> bool:
        """Check if user has reviewer permission."""
        try:
            # This would integrate with permission system
            # For now, allow all users
            return True

        except Exception as e:
            logger.error(f"Failed to check reviewer permission: {e}")
            return False

    async def _notify_escalated_user(
        self, user_id: str, gate_id: str, reason: str
    ) -> None:
        """Notify user of escalation."""
        try:
            from notifications import ApprovalNotifier

            notifier = ApprovalNotifier(self.redis)

            await notifier.notify_escalation(
                user_id, gate_id, reason, "original_approver"  # Would be actual user ID
            )

        except Exception as e:
            logger.error(f"Failed to notify escalated user: {e}")

    async def _notify_reviewer_assigned(self, reviewer_id: str, gate_id: str) -> None:
        """Notify reviewer of assignment."""
        try:
            from notifications import ApprovalNotifier

            notifier = ApprovalNotifier(self.redis)

            await notifier.notify_pending(
                reviewer_id, gate_id, "You have been assigned as reviewer", "high"
            )

        except Exception as e:
            logger.error(f"Failed to notify reviewer: {e}")

    async def _get_workspace_rules(self, workspace_id: str) -> List[EscalationRule]:
        """Get escalation rules for workspace."""
        try:
            rules_key = f"{self.rules_key_prefix}{workspace_id}"
            rules_data = await self.redis.get(rules_key)

            if rules_data:
                rules_json = json.loads(rules_data)
                return [EscalationRule(**rule) for rule in rules_json]

            return self.default_rules

        except Exception as e:
            logger.error(f"Failed to get workspace rules: {e}")
            return self.default_rules

    async def _evaluate_rule(
        self, rule: EscalationRule, request: Dict[str, Any]
    ) -> bool:
        """Evaluate if rule should trigger."""
        try:
            if rule.trigger_condition == "timeout":
                # Check if approval is older than timeout
                created_at = datetime.fromisoformat(request["created_at"])
                timeout_hours = rule.timeout_hours
                return (datetime.now() - created_at).total_seconds() > (
                    timeout_hours * 3600
                )

            elif rule.trigger_condition == "high_risk":
                # Check if risk level meets threshold
                return request.get("risk_level", 0) >= 4  # Critical risk

            elif rule.trigger_condition == "rejection":
                # Check if approval was rejected
                return request.get("status") == "rejected"

            return False

        except Exception as e:
            logger.error(f"Failed to evaluate rule: {e}")
            return False

    async def _execute_rule(
        self, rule: EscalationRule, gate_id: str, request: Dict[str, Any]
    ) -> Optional[str]:
        """Execute escalation rule."""
        try:
            if rule.trigger_condition == "timeout":
                success = await self.escalate(
                    gate_id,
                    f"Automatic escalation due to {rule.timeout_hours}h timeout",
                    escalate_to_role=rule.escalate_to_role,
                )
                return f"Escalated due to timeout" if success else None

            elif rule.trigger_condition == "high_risk":
                success = await self.escalate(
                    gate_id,
                    "Automatic escalation for high-risk operation",
                    escalate_to_role=rule.escalate_to_role,
                )
                return f"Escalated due to high risk" if success else None

            return None

        except Exception as e:
            logger.error(f"Failed to execute rule: {e}")
            return None

    def _load_default_rules(self) -> List[EscalationRule]:
        """Load default escalation rules."""
        return [
            EscalationRule(
                trigger_condition="timeout",
                escalation_level=1,
                escalate_to_role="manager",
                timeout_hours=24,
                auto_approve_if_no_response=False,
            ),
            EscalationRule(
                trigger_condition="high_risk",
                escalation_level=1,
                escalate_to_role="manager",
                timeout_hours=4,
                auto_approve_if_no_response=False,
            ),
            EscalationRule(
                trigger_condition="rejection",
                escalation_level=1,
                escalate_to_role="senior_reviewer",
                timeout_hours=2,
                auto_approve_if_no_response=False,
            ),
        ]
