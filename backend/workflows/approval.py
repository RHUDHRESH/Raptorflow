"""
ApprovalWorkflow - End-to-end approval orchestration.
Handles approval requests, processing, timeout handling, and HITL integration.
"""

import logging
import time
from typing import Any, Dict, List, Optional

from memory.controller import MemoryController

from cognitive import CognitiveEngine
from supabase import Client

from .agents.dispatcher import AgentDispatcher
from .agents.state import AgentState

logger = logging.getLogger(__name__)


class ApprovalWorkflow:
    """
    End-to-end approval workflow orchestrator.

    Handles the complete approval process from request creation
    through review, decision, timeout handling, and notification.
    """

    def __init__(
        self,
        db_client: Client,
        memory_controller: MemoryController,
        cognitive_engine: CognitiveEngine,
        agent_dispatcher: AgentDispatcher,
    ):
        self.db_client = db_client
        self.memory_controller = memory_controller
        self.cognitive_engine = cognitive_engine
        self.agent_dispatcher = agent_dispatcher

    async def submit_for_approval(
        self, output: Dict[str, Any], risk_level: str, reason: str = None
    ) -> Dict[str, Any]:
        """
        Submit output for approval with HITL integration.

        Args:
            output: Output to approve
            risk_level: Risk level (low, medium, high, critical)
            reason: Reason for approval request

        Returns:
            Approval submission result
        """
        try:
            logger.info(f"Submitting for approval: {risk_level} risk level")

            # Get workspace context
            context = await self._get_workspace_context(output.get("workspace_id"))

            # Step 1: Create approval gate
            gate_result = await self._create_approval_gate(
                output, risk_level, reason, context
            )

            if not gate_result["success"]:
                return gate_result

            # Step 2: Store approval request
            approval_record = {
                "gate_id": gate_result["gate_id"],
                "workspace_id": output.get("workspace_id"),
                "user_id": output.get("user_id"),
                "output": output,
                "risk_level": risk_level,
                "reason": reason,
                "status": "pending",
                "created_at": time.time(),
            }

            result = (
                self.db_client.table("approval_requests")
                .insert(approval_record)
                .execute()
            )

            if result.data:
                return {
                    "success": True,
                    "gate_id": gate_result["gate_id"],
                    "approval_id": result.data[0]["id"],
                    "status": "pending",
                    "created_at": time.time(),
                }
            else:
                return {"success": False, "error": "Failed to create approval request"}

        except Exception as e:
            logger.error(f"Error submitting for approval: {e}")
            return {"success": False, "error": str(e)}

    async def process_approval(
        self, gate_id: str, decision: str, feedback: str = None
    ) -> Dict[str, Any]:
        """
        Process approval decision.

        Args:
            gate_id: Approval gate ID
            decision: Approval decision (approved, rejected, needs_revision)
            feedback: Optional feedback for rejection/revision

        Returns:
            Approval processing result
        """
        try:
            logger.info(f"Processing approval: {decision} for gate {gate_id}")

            # Get approval request
            approval_result = (
                self.db_client.table("approval_requests")
                .select("*")
                .eq("gate_id", gate_id)
                .execute()
            )

            if not approval_result.data:
                return {"success": False, "error": "Approval request not found"}

            approval = approval_result.data[0]
            workspace_id = approval["workspace_id"]

            # Get workspace context
            context = await self._get_workspace_context(workspace_id)

            # Step 1: Validate decision
            if decision not in ["approved", "rejected", "needs_revision"]:
                return {"success": False, "error": f"Invalid decision: {decision}"}

            # Step 2: Process decision
            if decision == "approved":
                result = await self._process_approval_approved(approval, context)
            elif decision == "rejected":
                result = await self._process_approval_rejected(
                    approval, feedback, context
                )
            else:  # needs_revision
                result = await self._process_approval_needs_revision(
                    approval, feedback, context
                )

            # Step 3: Update approval record
            self.db_client.table("approval_requests").update(
                {
                    "status": decision,
                    "decision": decision,
                    "feedback": feedback,
                    "processed_at": time.time(),
                    "processor_id": context["user_id"],
                }
            ).eq("id", approval["id"]).execute()

            return result

        except Exception as e:
            logger.error(f"Error processing approval {gate_id}: {e}")
            return {"success": False, "error": str(e)}

    async def handle_timeout(self, gate_id: str) -> Dict[str, Any]:
        """
        Handle approval timeout with automatic processing.

        Args:
            gate_id: Approval gate ID that timed out

        Returns:
            Timeout handling result
        """
        try:
            logger.warning(f"Handling approval timeout for gate {gate_id}")

            # Get approval request
            approval_result = (
                self.db_client.table("approval_requests")
                .select("*")
                .eq("gate_id", gate_id)
                .execute()
            )

            if not approval_result.data:
                return {"success": false, "error": "Approval request not found"}

            approval = approval_result.data[0]
            workspace_id = approval["workspace_id"]

            # Get workspace context
            context = await self._get_workspace_context(workspace_id)

            # Step 1: Auto-assess risk level
            auto_assessment = await self._auto_assess_approval(approval, context)

            # Step 2: Make automatic decision
            if auto_assessment["auto_approve"]:
                result = await self._auto_approve_approval(
                    approval, auto_assessment, context
                )
            else:
                result = await self._auto_reject_approval(
                    approval, auto_assessment, context
                )

            # Step 3: Update approval record
            self.db_client.table("approval_requests").update(
                {
                    "status": result["decision"],
                    "decision": result["decision"],
                    "feedback": result.get("feedback"),
                    "processed_at": time.time(),
                    "processor_id": "system",
                    "timeout_handled": True,
                }
            ).eq("id", approval["id"]).execute()

            # Step 4: Notify about timeout handling
            await self._notify_timeout_handled(approval, result)

            return result

        except Exception as e:
            logger.error(f"Error handling timeout for gate {gate_id}: {e}")
            return {"success": False, "error": str(e)}

    async def _create_approval_gate(
        self,
        output: Dict[str, Any],
        risk_level: str,
        reason: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create approval gate using cognitive engine."""
        try:
            # Use HITL approval gate
            from cognitive.hitl.gate import ApprovalGate

            gate = ApprovalGate()

            # Create approval request
            gate_id = await gate.request_approval(
                workspace_id=output.get("workspace_id"),
                user_id=output.get("user_id"),
                output=output,
                risk_level=risk_level,
                reason=reason,
            )

            return {"success": True, "gate_id": gate_id}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _process_approval_approved(
        self, approval: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process approved approval."""
        try:
            # Update output status to approved
            if "output" in approval:
                output_type = approval["output"].get("type", "content")

                if output_type == "content":
                    # Update muse asset
                    self.db_client.table("muse_assets").update(
                        {"status": "approved", "approved_at": time.time()}
                    ).eq("id", approval["output"]["id"]).execute()
                elif output_type == "move":
                    # Update move
                    self.db_client.table("moves").update(
                        {"status": "approved", "approved_at": time.time()}
                    ).eq("id", approval["output"]["id"]).execute()
                elif output_type == "campaign":
                    # Update campaign
                    self.db_client.table("campaigns").update(
                        {"status": "approved", "approved_at": time.time()}
                    ).eq("id", approval["output"]["id"]).execute()

            # Store approval in memory
            await self._store_approval_in_memory(approval, "approved", context)

            # Send notification
            await self._send_approval_notification(approval, "approved")

            return {"success": True, "decision": "approved", "approved_at": time.time()}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _process_approval_rejected(
        self, approval: Dict[str, Any], feedback: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process rejected approval."""
        try:
            # Update output status to rejected
            if "output" in approval:
                output_type = approval["output"].get("type", "content")

                if output_type == "content":
                    # Update muse asset
                    self.db_client.table("muse_assets").update(
                        {
                            "status": "rejected",
                            "rejected_at": time.time(),
                            "rejection_reason": feedback,
                        }
                    ).eq("id", approval["output"]["id"]).execute()
                elif output_type == "move":
                    # Update move
                    self.db_client.table("moves").update(
                        {
                            "status": "rejected",
                            "rejected_at": time.time(),
                            "rejection_reason": feedback,
                        }
                    ).eq("id", approval["output"]["id"]).execute()
                elif output_type == "campaign":
                    # Update campaign
                    self.db_client.table("campaigns").update(
                        {
                            "status": "rejected",
                            "rejected_at": time.time(),
                            "rejection_reason": feedback,
                        }
                    ).eq("id", approval["output"]["id"]).execute()

            # Store approval in memory
            await self._store_approval_in_memory(approval, "rejected", context)

            # Send notification
            await self._send_approval_notification(approval, "rejected")

            return {
                "success": True,
                "decision": "rejected",
                "rejected_at": time.time(),
                "feedback": feedback,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _process_approval_needs_revision(
        self, revision: Dict[str, Any], feedback: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process approval that needs revision."""
        try:
            # Update output status to needs_revision
            if "output" in revision:
                output_type = revision["output"].get("type", "content")

                if output_type == "content":
                    # Update muse asset
                    self.db_client.table("muse_assets").update(
                        {
                            "status": "needs_revision",
                            "revision_requested_at": time.time(),
                            "revision_feedback": feedback,
                        }
                    ).eq("id", revision["output"]["id"]).execute()
                elif output_type == "move":
                    # Update move
                    self.db_client.table("moves").update(
                        {
                            "status": "needs_revision",
                            "revision_requested_at": time.time(),
                            "revision_feedback": feedback,
                        }
                    ).eq("id", revision["output"]["id"]).execute()
                elif output_type == "campaign":
                    # Update campaign
                    self.db_client.table("campaigns").update(
                        {
                            "status": "needs_revision",
                            "revision_requested_at": time.time(),
                            "revision_feedback": feedback,
                        }
                    ).eq("id", revision["output"]["id"]).execute()

            # Store approval in memory
            await self._store_approval_in_memory(revision, "needs_revision", context)

            # Send notification
            await self._send_approval_notification(revision, "needs_revision")

            return {
                "success": True,
                "decision": "needs_revision",
                "revision_requested_at": time.time(),
                "feedback": feedback,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _auto_assess_approval(
        self, approval: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Auto-assess approval for timeout handling."""
        try:
            # Use cognitive engine for risk assessment
            assessment = await self.cognitive_engine.critic.analyze(
                output=str(approval["output"]),
                context=context,
                analysis_type="approval_risk",
            )

            risk_score = assessment.get("risk_score", 0.5)

            # Determine if auto-approve based on risk
            auto_approve = risk_score <= 0.3  # Low risk threshold

            return {
                "risk_score": risk_score,
                "auto_approve": auto_approve,
                "confidence": assessment.get("confidence", 0.5),
                "assessment": assessment,
            }

        except Exception as e:
            return {"risk_score": 0.5, "auto_approve": False, "error": str(e)}

    async def _auto_approve_approval(
        self,
        approval: Dict[str, Any],
        assessment: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Auto-approve approval with low risk."""
        try:
            # Process as approved
            result = await self._process_approval_approved(approval, context)

            # Add auto-approval metadata
            result["auto_approved"] = True
            result["auto_assessment"] = assessment

            return result

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _auto_reject_approval(
        self,
        approval: Dict[str, Any],
        assessment: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Auto-reject approval with high risk."""
        try:
            # Generate auto-rejection feedback
            feedback = f"Auto-rejected due to high risk assessment (score: {assessment['risk_score']}). {assessment.get('feedback', '')}"

            # Process as rejected
            result = await self._process_approval_rejected(approval, feedback, context)

            # Add auto-rejection metadata
            result["auto_rejected"] = True
            result["auto_assessment"] = assessment

            return result

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _store_approval_in_memory(
        self, approval: Dict[str, Any], decision: str, context: Dict[str, Any]
    ):
        """Store approval in memory system."""
        try:
            content = f"""
            Approval Decision: {decision}
            Risk Level: {approval.get('risk_level')}
            Reason: {approval.get('reason')}
            Decision: {decision}
            Feedback: {approval.get('feedback', '')}
            """

            await self.memory_controller.store(
                workspace_id=approval["workspace_id"],
                memory_type="approval",
                content=content,
                metadata={
                    "approval_id": approval["id"],
                    "gate_id": approval["gate_id"],
                    "decision": decision,
                    "risk_level": approval.get("risk_level"),
                    "timestamp": time.time(),
                },
            )

        except Exception as e:
            logger.error(f"Error storing approval in memory: {e}")

    async def _send_approval_notification(
        self, approval: Dict[str, Any], decision: str
    ):
        """Send approval notification."""
        try:
            # This would integrate with notification system
            # For now, just log
            logger.info(
                f"Approval notification sent: {decision} for approval {approval['id']}"
            )

        except Exception as e:
            logger.error(f"Error sending approval notification: {e}")

    async def _notify_timeout_handled(
        self, approval: Dict[str, Any], result: Dict[str, Any]
    ):
        """Send timeout handling notification."""
        try:
            # This would integrate with notification system
            logger.warning(
                f"Approval timeout handled: {result['decision']} for approval {approval['id']}"
            )

        except Exception as e:
            logger.error(f"Error sending timeout notification: {e}")

    async def _get_workspace_context(self, workspace_id: str) -> Dict[str, Any]:
        """Get workspace context."""
        try:
            workspace_result = (
                self.db_client.table("workspaces")
                .select("*")
                .eq("id", workspace_id)
                .execute()
            )

            if workspace_result.data:
                workspace = workspace_result.data[0]
                return {
                    "workspace_id": workspace_id,
                    "user_id": workspace["user_id"],
                    "workspace": workspace,
                }
            else:
                return {"workspace_id": workspace_id, "user_id": None}

        except Exception as e:
            logger.error(f"Error getting workspace context: {e}")
            return {"workspace_id": workspace_id, "user_id": None}
