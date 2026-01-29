"""
Timeout Handler - Manages approval timeout scenarios

Handles timeout scenarios with configurable actions like
auto-rejection, auto-approval, or notification extension.
"""

import json
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, Optional

from ...redis.client import RedisClient
from ..models import ApprovalRequest, ApprovalStatus

logger = logging.getLogger(__name__)


class TimeoutAction(str, Enum):
    AUTO_REJECT = "auto_reject"
    AUTO_APPROVE = "auto_approve"
    NOTIFY_AND_EXTEND = "notify_and_extend"
    ESCALATE = "escalate"


class TimeoutHandler:
    """Manages approval timeout scenarios."""

    def __init__(self, redis_client: Optional[RedisClient] = None):
        self.redis = redis_client or RedisClient()
        self.timeout_config_prefix = "timeout_config:"

    async def handle_timeout(self, gate_id: str) -> bool:
        """
        Handle approval timeout based on configuration.

        Args:
            gate_id: Approval gate identifier

        Returns:
            Success status
        """
        try:
            # Get approval request
            gate_key = f"approval_gate:{gate_id}"
            request_data = await self.redis.get(gate_key)

            if not request_data:
                logger.error(f"Approval gate {gate_id} not found")
                return False

            request = json.loads(request_data)
            workspace_id = request["workspace_id"]

            # Get timeout configuration
            timeout_config = await self._get_timeout_config(workspace_id)

            # Determine action based on risk level and configuration
            action = await self._determine_timeout_action(request, timeout_config)

            # Execute timeout action
            success = await self._execute_timeout_action(gate_id, action, request)

            if success:
                # Log timeout action
                await self._log_timeout_action(gate_id, action, request)

            return success

        except Exception as e:
            logger.error(f"Failed to handle timeout: {e}")
            return False

    async def configure_timeout_handling(
        self, workspace_id: str, config: Dict[str, Any]
    ) -> bool:
        """
        Configure timeout handling for workspace.

        Args:
            workspace_id: Workspace identifier
            config: Timeout configuration

        Returns:
            Success status
        """
        try:
            default_config = {
                "default_action": "auto_reject",
                "low_risk_action": "notify_and_extend",
                "medium_risk_action": "auto_reject",
                "high_risk_action": "escalate",
                "extension_hours": 24,
                "max_extensions": 2,
                "escalation_role": "manager",
            }

            # Merge with provided config
            final_config = {**default_config, **config}

            # Store configuration
            config_key = f"{self.timeout_config_prefix}{workspace_id}"
            await self.redis.set(
                config_key, json.dumps(final_config), ex=86400 * 365  # Keep for 1 year
            )

            logger.info(f"Updated timeout config for workspace {workspace_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to configure timeout handling: {e}")
            return False

    async def get_timeout_status(self, gate_id: str) -> Dict[str, Any]:
        """
        Get timeout status for an approval gate.

        Args:
            gate_id: Approval gate identifier

        Returns:
            Timeout status information
        """
        try:
            gate_key = f"approval_gate:{gate_id}"
            request_data = await self.redis.get(gate_key)

            if not request_data:
                return {"status": "not_found"}

            request = json.loads(request_data)

            created_at = datetime.fromisoformat(request["created_at"])
            expires_at = datetime.fromisoformat(request["expires_at"])
            now = datetime.now()

            time_remaining = (expires_at - now).total_seconds()
            is_expired = time_remaining <= 0

            status = {
                "gate_id": gate_id,
                "status": "expired" if is_expired else "pending",
                "time_remaining_seconds": max(0, time_remaining),
                "time_remaining_hours": max(0, time_remaining / 3600),
                "expires_at": expires_at.isoformat(),
                "created_at": created_at.isoformat(),
                "risk_level": request.get("risk_level"),
                "request_type": request.get("request_type"),
            }

            return status

        except Exception as e:
            logger.error(f"Failed to get timeout status: {e}")
            return {"status": "error", "error": str(e)}

    async def extend_timeout(
        self, gate_id: str, extend_hours: int, extended_by: str
    ) -> bool:
        """
        Extend timeout for an approval gate.

        Args:
            gate_id: Approval gate identifier
            extend_hours: Hours to extend
            extended_by: User extending

        Returns:
            Success status
        """
        try:
            gate_key = f"approval_gate:{gate_id}"
            request_data = await self.redis.get(gate_key)

            if not request_data:
                logger.error(f"Approval gate {gate_id} not found")
                return False

            request = json.loads(request_data)

            # Check extension limit
            extension_count = request.get("extension_count", 0)
            workspace_id = request["workspace_id"]
            timeout_config = await self._get_timeout_config(workspace_id)
            max_extensions = timeout_config.get("max_extensions", 2)

            if extension_count >= max_extensions:
                logger.error(f"Maximum extensions reached for gate {gate_id}")
                return False

            # Extend expiration
            current_expires = datetime.fromisoformat(request["expires_at"])
            new_expires = current_expires + timedelta(hours=extend_hours)

            request["expires_at"] = new_expires.isoformat()
            request["extension_count"] = extension_count + 1
            request["last_extended_by"] = extended_by
            request["last_extended_at"] = datetime.now().isoformat()

            # Update request
            await self.redis.set(gate_key, json.dumps(request))

            # Update Redis TTL
            time_to_live = int((new_expires - datetime.now()).total_seconds())
            await self.redis.expire(gate_key, time_to_live)

            logger.info(f"Extended timeout for gate {gate_id} by {extend_hours} hours")
            return True

        except Exception as e:
            logger.error(f"Failed to extend timeout: {e}")
            return False

    async def _get_timeout_config(self, workspace_id: str) -> Dict[str, Any]:
        """Get timeout configuration for workspace."""
        try:
            config_key = f"{self.timeout_config_prefix}{workspace_id}"
            config_data = await self.redis.get(config_key)

            if config_data:
                return json.loads(config_data)

            # Default configuration
            return {
                "default_action": "auto_reject",
                "low_risk_action": "notify_and_extend",
                "medium_risk_action": "auto_reject",
                "high_risk_action": "escalate",
                "extension_hours": 24,
                "max_extensions": 2,
                "escalation_role": "manager",
            }

        except Exception as e:
            logger.error(f"Failed to get timeout config: {e}")
            return {}

    async def _determine_timeout_action(
        self, request: Dict[str, Any], config: Dict[str, Any]
    ) -> TimeoutAction:
        """Determine timeout action based on request and config."""
        try:
            risk_level = request.get("risk_level", 1)

            if risk_level <= 2:  # Low risk
                return TimeoutAction(config.get("low_risk_action", "notify_and_extend"))
            elif risk_level == 3:  # Medium risk
                return TimeoutAction(config.get("medium_risk_action", "auto_reject"))
            else:  # High risk
                return TimeoutAction(config.get("high_risk_action", "escalate"))

        except Exception as e:
            logger.error(f"Failed to determine timeout action: {e}")
            return TimeoutAction.AUTO_REJECT

    async def _execute_timeout_action(
        self, gate_id: str, action: TimeoutAction, request: Dict[str, Any]
    ) -> bool:
        """Execute the determined timeout action."""
        try:
            if action == TimeoutAction.AUTO_REJECT:
                return await self._auto_reject(gate_id, request)
            elif action == TimeoutAction.AUTO_APPROVE:
                return await self._auto_approve(gate_id, request)
            elif action == TimeoutAction.NOTIFY_AND_EXTEND:
                return await self._notify_and_extend(gate_id, request)
            elif action == TimeoutAction.ESCALATE:
                return await self._escalate(gate_id, request)

            return False

        except Exception as e:
            logger.error(f"Failed to execute timeout action: {e}")
            return False

    async def _auto_reject(self, gate_id: str, request: Dict[str, Any]) -> bool:
        """Auto-reject approval on timeout."""
        try:
            from gate import ApprovalGate

            gate = ApprovalGate(self.redis)

            return await gate.reject(
                gate_id, "Auto-rejected due to timeout", responded_by="system"
            )

        except Exception as e:
            logger.error(f"Failed to auto-reject: {e}")
            return False

    async def _auto_approve(self, gate_id: str, request: Dict[str, Any]) -> bool:
        """Auto-approve approval on timeout."""
        try:
            from gate import ApprovalGate

            gate = ApprovalGate(self.redis)

            return await gate.approve(
                gate_id,
                "Auto-approved due to timeout (low risk)",
                responded_by="system",
            )

        except Exception as e:
            logger.error(f"Failed to auto-approve: {e}")
            return False

    async def _notify_and_extend(self, gate_id: str, request: Dict[str, Any]) -> bool:
        """Send notification and extend timeout."""
        try:
            workspace_id = request["workspace_id"]
            config = await self._get_timeout_config(workspace_id)
            extend_hours = config.get("extension_hours", 24)

            # Send notification
            from notifications import ApprovalNotifier

            notifier = ApprovalNotifier(self.redis)

            await notifier.notify_expiring(
                request["user_id"], gate_id, extend_hours * 3600
            )

            # Extend timeout
            return await self.extend_timeout(gate_id, extend_hours, "system")

        except Exception as e:
            logger.error(f"Failed to notify and extend: {e}")
            return False

    async def _escalate(self, gate_id: str, request: Dict[str, Any]) -> bool:
        """Escalate approval on timeout."""
        try:
            from escalation import EscalationManager

            escalation = EscalationManager(self.redis)

            workspace_id = request["workspace_id"]
            config = await self._get_timeout_config(workspace_id)
            escalation_role = config.get("escalation_role", "manager")

            return await escalation.escalate(
                gate_id, "Escalated due to timeout", escalate_to_role=escalation_role
            )

        except Exception as e:
            logger.error(f"Failed to escalate: {e}")
            return False

    async def _log_timeout_action(
        self, gate_id: str, action: TimeoutAction, request: Dict[str, Any]
    ) -> None:
        """Log timeout action for audit."""
        try:
            from audit import ApprovalAudit

            audit = ApprovalAudit(self.redis)

            await audit.log_decision(
                gate_id,
                f"timeout_{action.value}",
                f"Automatic action due to timeout: {action.value}",
            )

        except Exception as e:
            logger.error(f"Failed to log timeout action: {e}")
