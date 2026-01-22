"""
Human Override - Handles user modifications and overrides

Allows users to modify outputs and override automated decisions
with proper tracking and audit trails.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from ...redis.client import RedisClient
from .models import ApprovalResponse

logger = logging.getLogger(__name__)


class HumanOverride:
    """Manages human overrides and modifications."""

    def __init__(self, redis_client: Optional[RedisClient] = None):
        self.redis = redis_client or RedisClient()
        self.override_key_prefix = "human_override:"

    async def apply_override(
        self,
        gate_id: str,
        modified_output: str,
        reason: Optional[str] = None,
        override_by: Optional[str] = None,
    ) -> bool:
        """
        Apply human override to modify output.

        Args:
            gate_id: Approval gate identifier
            modified_output: Modified content
            reason: Reason for override
            override_by: User applying override

        Returns:
            Success status
        """
        try:
            override_data = {
                "gate_id": gate_id,
                "modified_output": modified_output,
                "reason": reason,
                "override_by": override_by,
                "timestamp": datetime.now().isoformat(),
                "type": "modification",
            }

            # Store override
            key = f"{self.override_key_prefix}{gate_id}"
            await self.redis.set(key, json.dumps(override_data), ex=86400 * 30)

            # Update approval response with modified output
            response_key = f"approval_response:{gate_id}"
            response_data = await self.redis.get(response_key)

            if response_data:
                response = json.loads(response_data)
                response["modified_output"] = modified_output
                response["feedback"] = (
                    f"Human override: {reason}" if reason else "Human override applied"
                )
                await self.redis.set(response_key, json.dumps(response))

            logger.info(f"Applied human override for gate {gate_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to apply override: {e}")
            return False

    async def reject_with_instructions(
        self, gate_id: str, instructions: str, reject_by: Optional[str] = None
    ) -> bool:
        """
        Reject with specific instructions for improvement.

        Args:
            gate_id: Approval gate identifier
            instructions: Instructions for improvement
            reject_by: User rejecting

        Returns:
            Success status
        """
        try:
            override_data = {
                "gate_id": gate_id,
                "instructions": instructions,
                "reject_by": reject_by,
                "timestamp": datetime.now().isoformat(),
                "type": "rejection_with_instructions",
            }

            # Store override
            key = f"{self.override_key_prefix}{gate_id}"
            await self.redis.set(key, json.dumps(override_data), ex=86400 * 30)

            # Update approval response
            response_key = f"approval_response:{gate_id}"
            response_data = await self.redis.get(response_key)

            if response_data:
                response = json.loads(response_data)
                response["approved"] = False
                response["feedback"] = instructions
                await self.redis.set(response_key, json.dumps(response))

            logger.info(f"Recorded rejection with instructions for gate {gate_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to reject with instructions: {e}")
            return False

    async def get_override_history(
        self, workspace_id: str, days: int = 30
    ) -> list[Dict[str, Any]]:
        """
        Get override history for a workspace.

        Args:
            workspace_id: Workspace identifier
            days: Number of days to look back

        Returns:
            List of override records
        """
        try:
            # This would need to query by workspace_id and date range
            # For now, return empty list
            return []

        except Exception as e:
            logger.error(f"Failed to get override history: {e}")
            return []

    async def get_override_for_gate(self, gate_id: str) -> Optional[Dict[str, Any]]:
        """
        Get override data for a specific gate.

        Args:
            gate_id: Gate identifier

        Returns:
            Override data or None
        """
        try:
            key = f"{self.override_key_prefix}{gate_id}"
            data = await self.redis.get(key)

            if data:
                return json.loads(data)

            return None

        except Exception as e:
            logger.error(f"Failed to get override for gate {gate_id}: {e}")
            return None

    async def validate_override_permissions(
        self, gate_id: str, user_id: str, workspace_id: str
    ) -> bool:
        """
        Validate if user has permission to override.

        Args:
            gate_id: Gate identifier
            user_id: User attempting override
            workspace_id: Workspace identifier

        Returns:
            True if user has permission
        """
        try:
            # Check if user is workspace admin or has override permissions
            # This would integrate with user management system
            # For now, allow all users

            # TODO: Implement actual permission checking
            # 1. Check user role in workspace
            # 2. Check if user has specific override permissions
            # 3. Check if gate is still modifiable (not expired)

            return True

        except Exception as e:
            logger.error(f"Failed to validate override permissions: {e}")
            return False

    async def create_override_template(
        self, gate_id: str, template_type: str, parameters: Dict[str, Any]
    ) -> bool:
        """
        Create override template for common scenarios.

        Args:
            gate_id: Gate identifier
            template_type: Type of template
            parameters: Template parameters

        Returns:
            Success status
        """
        try:
            templates = {
                "brand_voice_fix": {
                    "reason": "Adjust brand voice to match guidelines",
                    "modifications": ["tone", "terminology", "style"],
                },
                "fact_correction": {
                    "reason": "Correct factual inaccuracies",
                    "modifications": ["facts", "data", "claims"],
                },
                "content_expansion": {
                    "reason": "Expand content for completeness",
                    "modifications": ["add_details", "examples", "context"],
                },
                "simplification": {
                    "reason": "Simplify for better readability",
                    "modifications": ["language", "structure", "complexity"],
                },
            }

            template = templates.get(template_type)
            if not template:
                logger.warning(f"Unknown template type: {template_type}")
                return False

            # Apply template
            modified_output = self._apply_template_modifications(
                gate_id, template, parameters
            )

            return await self.apply_override(
                gate_id, modified_output, template["reason"]
            )

        except Exception as e:
            logger.error(f"Failed to create override template: {e}")
            return False

    def _apply_template_modifications(
        self, gate_id: str, template: Dict[str, Any], parameters: Dict[str, Any]
    ) -> str:
        """
        Apply template modifications to content.

        Args:
            gate_id: Gate identifier
            template: Template definition
            parameters: Modification parameters

        Returns:
            Modified content
        """
        # This would integrate with content modification logic
        # For now, return placeholder
        return f"Modified content using {template['reason']}"
