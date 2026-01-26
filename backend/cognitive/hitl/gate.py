"""
Approval Gate - Core HITL approval management

Handles approval requests, status checking, and response waiting.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from backend.config import CognitiveConfig

from ...redis.client import RedisClient
from .models import (
    ApprovalRequest,
    ApprovalResponse,
    ApprovalStatus,
    RequestType,
    RiskLevel,
)

logger = logging.getLogger(__name__)


class ApprovalGate:
    """Manages human approval gates for critical operations."""

    def __init__(
        self,
        redis_client: Optional[RedisClient] = None,
        config: Optional[CognitiveConfig] = None,
    ):
        self.redis = redis_client or RedisClient()
        self.config = config or CognitiveConfig()
        self.approval_timeout = self.config.approval_timeout_seconds

    async def request_approval(
        self,
        workspace_id: str,
        user_id: str,
        output: str,
        risk_level: RiskLevel,
        reason: str,
        request_type: RequestType = RequestType.CONTENT_GENERATION,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Request human approval for an operation.

        Args:
            workspace_id: Workspace identifier
            user_id: User requesting approval
            output: Output preview for approval
            risk_level: Risk level of the operation
            reason: Reason for approval requirement
            request_type: Type of operation requiring approval
            metadata: Additional metadata

        Returns:
            Gate ID for tracking
        """
        try:
            gate_id = str(uuid.uuid4())
            created_at = datetime.now()
            expires_at = created_at + timedelta(seconds=self.approval_timeout)

            request = ApprovalRequest(
                gate_id=gate_id,
                workspace_id=workspace_id,
                user_id=user_id,
                request_type=request_type,
                output_preview=output[:1000],  # Limit preview length
                risk_level=risk_level,
                reason=reason,
                created_at=created_at,
                expires_at=expires_at,
                metadata=metadata,
            )

            # Store in Redis
            key = f"approval_gate:{gate_id}"
            await self.redis.set(
                key,
                json.dumps(self._serialize_request(request)),
                ex=self.approval_timeout,
            )

            # Add to pending queue
            pending_key = f"approval_pending:{workspace_id}"
            await self.redis.lpush(pending_key, gate_id)
            await self.redis.expire(pending_key, self.approval_timeout)

            logger.info(f"Created approval gate {gate_id} for user {user_id}")
            return gate_id

        except Exception as e:
            logger.error(f"Failed to request approval: {e}")
            raise

    async def check_status(self, gate_id: str) -> ApprovalStatus:
        """
        Check approval status.

        Args:
            gate_id: Gate identifier

        Returns:
            Current approval status
        """
        try:
            key = f"approval_gate:{gate_id}"
            data = await self.redis.get(key)

            if not data:
                return ApprovalStatus.EXPIRED

            request_data = json.loads(data)
            return ApprovalStatus(request_data.get("status", "pending"))

        except Exception as e:
            logger.error(f"Failed to check approval status: {e}")
            return ApprovalStatus.EXPIRED

    async def wait_for_approval(
        self, gate_id: str, timeout: Optional[int] = None
    ) -> ApprovalResponse:
        """
        Wait for approval response.

        Args:
            gate_id: Gate identifier
            timeout: Maximum time to wait (seconds)

        Returns:
            Approval response
        """
        try:
            timeout = timeout or self.approval_timeout
            start_time = datetime.now()

            while (datetime.now() - start_time).total_seconds() < timeout:
                status = await self.check_status(gate_id)

                if status in [ApprovalStatus.APPROVED, ApprovalStatus.REJECTED]:
                    return await self._get_response(gate_id)

                if status == ApprovalStatus.EXPIRED:
                    raise TimeoutError(f"Approval gate {gate_id} expired")

                await asyncio.sleep(2)  # Poll every 2 seconds

            # Timeout reached
            await self._handle_timeout(gate_id)
            raise TimeoutError(f"Approval timeout for gate {gate_id}")

        except Exception as e:
            logger.error(f"Failed to wait for approval: {e}")
            raise

    async def approve(
        self,
        gate_id: str,
        feedback: Optional[str] = None,
        responded_by: Optional[str] = None,
    ) -> bool:
        """
        Approve an approval request.

        Args:
            gate_id: Gate identifier
            feedback: Optional feedback
            responded_by: User who approved

        Returns:
            Success status
        """
        try:
            response = ApprovalResponse(
                gate_id=gate_id,
                approved=True,
                feedback=feedback,
                responded_by=responded_by,
            )

            return await self._record_response(gate_id, response)

        except Exception as e:
            logger.error(f"Failed to approve gate {gate_id}: {e}")
            return False

    async def reject(
        self,
        gate_id: str,
        feedback: Optional[str] = None,
        modified_output: Optional[str] = None,
        responded_by: Optional[str] = None,
    ) -> bool:
        """
        Reject an approval request.

        Args:
            gate_id: Gate identifier
            feedback: Rejection feedback
            modified_output: Modified output if provided
            responded_by: User who rejected

        Returns:
            Success status
        """
        try:
            response = ApprovalResponse(
                gate_id=gate_id,
                approved=False,
                feedback=feedback,
                modified_output=modified_output,
                responded_by=responded_by,
            )

            return await self._record_response(gate_id, response)

        except Exception as e:
            logger.error(f"Failed to reject gate {gate_id}: {e}")
            return False

    async def get_pending_approvals(self, workspace_id: str) -> List[ApprovalRequest]:
        """
        Get pending approvals for a workspace.

        Args:
            workspace_id: Workspace identifier

        Returns:
            List of pending approval requests
        """
        try:
            pending_key = f"approval_pending:{workspace_id}"
            gate_ids = await self.redis.lrange(pending_key, 0, -1)

            pending_requests = []
            for gate_id in gate_ids:
                key = f"approval_gate:{gate_id}"
                data = await self.redis.get(key)

                if data:
                    request_data = json.loads(data)
                    if request_data.get("status") == "pending":
                        pending_requests.append(self._deserialize_request(request_data))

            return pending_requests

        except Exception as e:
            logger.error(f"Failed to get pending approvals: {e}")
            return []

    async def _record_response(self, gate_id: str, response: ApprovalResponse) -> bool:
        """Record approval response."""
        try:
            key = f"approval_gate:{gate_id}"
            data = await self.redis.get(key)

            if not data:
                return False

            request_data = json.loads(data)

            # Update request with response
            request_data["status"] = "approved" if response.approved else "rejected"
            request_data["response_feedback"] = response.feedback
            request_data["responded_at"] = response.responded_at.isoformat()

            # Store updated request
            await self.redis.set(key, json.dumps(request_data))

            # Store response separately
            response_key = f"approval_response:{gate_id}"
            await self.redis.set(
                response_key,
                json.dumps(self._serialize_response(response)),
                ex=86400 * 7,  # Keep for 7 days
            )

            # Remove from pending queue
            pending_key = f"approval_pending:{request_data['workspace_id']}"
            await self.redis.lrem(pending_key, 0, gate_id)

            logger.info(
                f"Recorded {'approval' if response.approved else 'rejection'} for gate {gate_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to record response: {e}")
            return False

    async def _get_response(self, gate_id: str) -> ApprovalResponse:
        """Get approval response."""
        try:
            response_key = f"approval_response:{gate_id}"
            data = await self.redis.get(response_key)

            if not data:
                # Fallback to request data
                key = f"approval_gate:{gate_id}"
                request_data = await self.redis.get(key)
                if request_data:
                    req_data = json.loads(request_data)
                    return ApprovalResponse(
                        gate_id=gate_id,
                        approved=req_data.get("status") == "approved",
                        feedback=req_data.get("response_feedback"),
                        responded_at=(
                            datetime.fromisoformat(req_data["responded_at"])
                            if req_data.get("responded_at")
                            else None
                        ),
                    )

            return self._deserialize_response(json.loads(data))

        except Exception as e:
            logger.error(f"Failed to get response: {e}")
            raise

    async def _handle_timeout(self, gate_id: str):
        """Handle approval timeout."""
        try:
            key = f"approval_gate:{gate_id}"
            data = await self.redis.get(key)

            if data:
                request_data = json.loads(data)
                request_data["status"] = "expired"
                await self.redis.set(key, json.dumps(request_data))

                # Remove from pending queue
                pending_key = f"approval_pending:{request_data['workspace_id']}"
                await self.redis.lrem(pending_key, 0, gate_id)

            logger.info(f"Approval gate {gate_id} timed out")

        except Exception as e:
            logger.error(f"Failed to handle timeout: {e}")

    def _serialize_request(self, request: ApprovalRequest) -> Dict[str, Any]:
        """Serialize approval request for storage."""
        return {
            "gate_id": request.gate_id,
            "workspace_id": request.workspace_id,
            "user_id": request.user_id,
            "request_type": request.request_type.value,
            "output_preview": request.output_preview,
            "risk_level": request.risk_level.value,
            "reason": request.reason,
            "created_at": request.created_at.isoformat(),
            "expires_at": request.expires_at.isoformat(),
            "status": request.status.value,
            "response_feedback": request.response_feedback,
            "responded_at": (
                request.responded_at.isoformat() if request.responded_at else None
            ),
            "metadata": request.metadata,
        }

    def _deserialize_request(self, data: Dict[str, Any]) -> ApprovalRequest:
        """Deserialize approval request from storage."""
        return ApprovalRequest(
            gate_id=data["gate_id"],
            workspace_id=data["workspace_id"],
            user_id=data["user_id"],
            request_type=RequestType(data["request_type"]),
            output_preview=data["output_preview"],
            risk_level=RiskLevel(data["risk_level"]),
            reason=data["reason"],
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]),
            status=ApprovalStatus(data["status"]),
            response_feedback=data.get("response_feedback"),
            responded_at=(
                datetime.fromisoformat(data["responded_at"])
                if data.get("responded_at")
                else None
            ),
            metadata=data.get("metadata"),
        )

    def _serialize_response(self, response: ApprovalResponse) -> Dict[str, Any]:
        """Serialize approval response for storage."""
        return {
            "gate_id": response.gate_id,
            "approved": response.approved,
            "feedback": response.feedback,
            "modified_output": response.modified_output,
            "responded_by": response.responded_by,
            "responded_at": response.responded_at.isoformat(),
        }

    def _deserialize_response(self, data: Dict[str, Any]) -> ApprovalResponse:
        """Deserialize approval response from storage."""
        return ApprovalResponse(
            gate_id=data["gate_id"],
            approved=data["approved"],
            feedback=data.get("feedback"),
            modified_output=data.get("modified_output"),
            responded_by=data.get("responded_by"),
            responded_at=datetime.fromisoformat(data["responded_at"]),
        )
