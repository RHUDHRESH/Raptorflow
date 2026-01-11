"""
Human-in-the-Loop (HITL) workflow graph for approval gates and human feedback.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Literal, Optional, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from ..state import AgentState


class ApprovalState(AgentState):
    """Extended state for approval workflow."""

    pending_output: str
    risk_level: Literal["low", "medium", "high", "critical"]
    gate_id: str
    approval_type: Literal["content", "strategy", "action", "financial"]
    approval_request: Dict[str, Any]
    approval_status: Literal["pending", "approved", "rejected", "timeout"]
    approver_id: Optional[str]
    approval_reason: Optional[str]
    approval_timestamp: Optional[str]
    timeout_duration: int  # in hours
    reminder_sent: bool
    escalation_level: int


class ApprovalGate:
    """Manages approval gates and human feedback."""

    def __init__(self):
        self.active_gates = {}  # gate_id -> ApprovalState
        self.approval_history = {}  # user_id -> List[ApprovalState]

    def create_gate_id(self, session_id: str, user_id: str, output_hash: str) -> str:
        """Create unique gate ID."""
        return f"gate_{session_id}_{user_id}_{output_hash[:8]}"

    def assess_risk_level(
        self, output: str, context: Dict[str, Any]
    ) -> Literal["low", "medium", "high", "critical"]:
        """Assess risk level of output requiring approval."""
        # Simple risk assessment based on content and context
        risk_score = 0

        # Check for high-risk keywords
        high_risk_keywords = [
            "legal",
            "lawsuit",
            "contract",
            "agreement",
            "financial",
            "money",
            "payment",
            "investment",
            "guarantee",
            "promise",
            "commitment",
            "public",
            "release",
            "launch",
            "announcement",
            "official",
        ]

        medium_risk_keywords = [
            "customer",
            "client",
            "partner",
            "collaboration",
            "campaign",
            "marketing",
            "promotion",
            "advertisement",
            "content",
            "publish",
        ]

        output_lower = output.lower()

        for keyword in high_risk_keywords:
            if keyword in output_lower:
                risk_score += 2

        for keyword in medium_risk_keywords:
            if keyword in output_lower:
                risk_score += 1

        # Check context risk factors
        if context.get("is_public", False):
            risk_score += 2

        if context.get("involves_money", False):
            risk_score += 2

        if context.get("legal_implications", False):
            risk_score += 3

        # Determine risk level
        if risk_score >= 5:
            return "critical"
        elif risk_score >= 3:
            return "high"
        elif risk_score >= 1:
            return "medium"
        else:
            return "low"

    def determine_approval_type(
        self, output: str, context: Dict[str, Any]
    ) -> Literal["content", "strategy", "action", "financial"]:
        """Determine type of approval needed."""
        content_keywords = ["blog", "post", "article", "email", "newsletter", "social"]
        strategy_keywords = ["strategy", "plan", "approach", "roadmap", "initiative"]
        action_keywords = ["execute", "implement", "launch", "release", "deploy"]
        financial_keywords = ["budget", "cost", "investment", "revenue", "pricing"]

        output_lower = output.lower()

        if any(keyword in output_lower for keyword in financial_keywords):
            return "financial"
        elif any(keyword in output_lower for keyword in action_keywords):
            return "action"
        elif any(keyword in output_lower for keyword in strategy_keywords):
            return "strategy"
        else:
            return "content"

    def calculate_timeout_duration(
        self, risk_level: Literal["low", "medium", "high", "critical"]
    ) -> int:
        """Calculate timeout duration based on risk level."""
        timeouts = {
            "low": 24,  # 24 hours
            "medium": 12,  # 12 hours
            "high": 6,  # 6 hours
            "critical": 2,  # 2 hours
        }
        return timeouts.get(risk_level, 12)


async def request_approval(state: ApprovalState) -> ApprovalState:
    """Request human approval for output."""
    try:
        output = state.get("pending_output", "")
        context = state.get("memory_context", {})

        # Assess risk and determine approval type
        gate = ApprovalGate()
        risk_level = gate.assess_risk_level(output, context)
        approval_type = gate.determine_approval_type(output, context)
        timeout_duration = gate.calculate_timeout_duration(risk_level)

        # Create gate ID
        gate_id = gate.create_gate_id(
            state.get("session_id", ""), state.get("user_id", ""), str(hash(output))
        )

        # Create approval request
        approval_request = {
            "gate_id": gate_id,
            "output": output,
            "risk_level": risk_level,
            "approval_type": approval_type,
            "context": context,
            "requested_at": datetime.now().isoformat(),
            "timeout_at": (
                datetime.now() + timedelta(hours=timeout_duration)
            ).isoformat(),
            "requested_by": state.get("user_id"),
            "workspace_id": state.get("workspace_id"),
            "session_id": state.get("session_id"),
        }

        # Update state
        state["gate_id"] = gate_id
        state["risk_level"] = risk_level
        state["approval_type"] = approval_type
        state["approval_request"] = approval_request
        state["approval_status"] = "pending"
        state["timeout_duration"] = timeout_duration
        state["reminder_sent"] = False
        state["escalation_level"] = 0
        state["pending_approval"] = True

        # Store in active gates
        gate.active_gates[gate_id] = state

        return state
    except Exception as e:
        state["error"] = f"Approval request failed: {str(e)}"
        return state


async def wait_for_response(state: ApprovalState) -> ApprovalState:
    """Wait for human response (interrupt point)."""
    try:
        # This is where the workflow pauses and waits for human input
        # The actual waiting is handled by the interrupt mechanism
        state["approval_status"] = "pending"

        return state
    except Exception as e:
        state["error"] = f"Wait for response failed: {str(e)}"
        return state


async def handle_timeout(state: ApprovalState) -> ApprovalState:
    """Handle approval timeout."""
    try:
        gate_id = state.get("gate_id", "")
        risk_level = state.get("risk_level", "medium")
        escalation_level = state.get("escalation_level", 0)

        # Check if we should escalate or auto-approve
        if risk_level == "critical" and escalation_level < 2:
            # Escalate to higher authority
            state["escalation_level"] += 1
            state["approval_status"] = "pending"
            state["timeout_duration"] = 2  # 2 more hours
            # TODO: Send escalation notification
        elif risk_level in ["high", "critical"] and escalation_level >= 2:
            # Auto-reject for high-risk items
            state["approval_status"] = "rejected"
            state["approval_reason"] = "Auto-rejected due to timeout and high risk"
        else:
            # Auto-approve for lower risk items
            state["approval_status"] = "approved"
            state["approval_reason"] = "Auto-approved due to timeout"

        return state
    except Exception as e:
        state["error"] = f"Timeout handling failed: {str(e)}"
        return state


async def process_approval(state: ApprovalState) -> ApprovalState:
    """Process approval decision."""
    try:
        approval_status = state.get("approval_status", "pending")

        if approval_status == "approved":
            state["pending_approval"] = False
            state["approval_timestamp"] = datetime.now().isoformat()
        elif approval_status == "rejected":
            state["pending_approval"] = False
            state["approval_timestamp"] = datetime.now().isoformat()
        elif approval_status == "timeout":
            await handle_timeout(state)

        return state
    except Exception as e:
        state["error"] = f"Approval processing failed: {str(e)}"
        return state


async def send_reminder(state: ApprovalState) -> ApprovalState:
    """Send reminder for pending approval."""
    try:
        if state.get("reminder_sent", False):
            return state

        gate_id = state.get("gate_id", "")
        risk_level = state.get("risk_level", "medium")

        # TODO: Implement actual reminder sending
        reminder_message = {
            "gate_id": gate_id,
            "risk_level": risk_level,
            "message": f"Reminder: Approval required for {risk_level} risk item",
            "sent_at": datetime.now().isoformat(),
        }

        state["reminder_sent"] = True

        return state
    except Exception as e:
        state["error"] = f"Reminder sending failed: {str(e)}"
        return state


async def check_approval_status(state: ApprovalState) -> ApprovalState:
    """Check current approval status."""
    try:
        gate_id = state.get("gate_id", "")

        # TODO: Check actual approval status from database/API
        # For now, simulate status check

        # If status has changed from pending, process it
        if state.get("approval_status") != "pending":
            await process_approval(state)

        return state
    except Exception as e:
        state["error"] = f"Status check failed: {str(e)}"
        return state


def should_continue_approval(state: ApprovalState) -> str:
    """Determine next step in approval workflow."""
    if state.get("error"):
        return END

    approval_status = state.get("approval_status", "pending")

    if approval_status == "pending":
        # Check if timeout has been reached
        timeout_at = state.get("approval_request", {}).get("timeout_at")
        if timeout_at and datetime.now() > datetime.fromisoformat(timeout_at):
            return "handle_timeout"

        # Send reminder if needed
        if not state.get("reminder_sent", False):
            return "send_reminder"

        # Continue waiting
        return "wait"
    elif approval_status in ["approved", "rejected"]:
        return "process"
    else:
        return END


class HITLGraph:
    """Human-in-the-Loop workflow graph."""

    def __init__(self):
        self.graph = None
        self.approval_gate = ApprovalGate()

    def create_graph(self) -> StateGraph:
        """Create the HITL workflow graph."""
        workflow = StateGraph(ApprovalState)

        # Add nodes
        workflow.add_node("request_approval", request_approval)
        workflow.add_node("wait_for_response", wait_for_response)
        workflow.add_node("send_reminder", send_reminder)
        workflow.add_node("check_status", check_approval_status)
        workflow.add_node("process_approval", process_approval)
        workflow.add_node("handle_timeout", handle_timeout)

        # Set entry point
        workflow.set_entry_point("request_approval")

        # Add conditional edges
        workflow.add_conditional_edges(
            "request_approval",
            should_continue_approval,
            {"wait": "wait_for_response", END: END},
        )
        workflow.add_conditional_edges(
            "wait_for_response",
            should_continue_approval,
            {
                "send_reminder": "send_reminder",
                "handle_timeout": "handle_timeout",
                "process": "process_approval",
                END: END,
            },
        )
        workflow.add_conditional_edges(
            "send_reminder",
            should_continue_approval,
            {
                "wait": "wait_for_response",
                "handle_timeout": "handle_timeout",
                "process": "process_approval",
                END: END,
            },
        )
        workflow.add_conditional_edges(
            "check_status",
            should_continue_approval,
            {
                "wait": "wait_for_response",
                "handle_timeout": "handle_timeout",
                "process": "process_approval",
                END: END,
            },
        )
        workflow.add_edge("process_approval", END)
        workflow.add_edge("handle_timeout", END)

        # Add memory checkpointing
        memory = MemorySaver()

        # Compile the graph with interrupt before waiting
        self.graph = workflow.compile(
            checkpointer=memory, interrupt_before=["wait_for_response"]
        )
        return self.graph

    async def create_approval_gate(
        self,
        output: str,
        workspace_id: str,
        user_id: str,
        session_id: str,
        context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Create an approval gate."""
        if not self.graph:
            self.create_graph()

        if context is None:
            context = {}

        # Create initial state
        initial_state = ApprovalState(
            pending_output=output,
            risk_level="medium",
            gate_id="",
            approval_type="content",
            approval_request={},
            approval_status="pending",
            approver_id=None,
            approval_reason=None,
            approval_timestamp=None,
            timeout_duration=12,
            reminder_sent=False,
            escalation_level=0,
            workspace_id=workspace_id,
            user_id=user_id,
            session_id=session_id,
            memory_context=context,
            messages=[],
            routing_path=[],
            foundation_summary={},
            active_icps=[],
            pending_approval=True,
            error=None,
            output=None,
            tokens_used=0,
            cost_usd=0.0,
        )

        # Configure execution
        thread_config = {
            "configurable": {
                "thread_id": f"approval_{session_id}",
                "checkpoint_ns": f"approval_{workspace_id}",
            }
        }

        try:
            result = await self.graph.ainvoke(initial_state, config=thread_config)

            return {
                "success": True,
                "gate_id": result.get("gate_id"),
                "risk_level": result.get("risk_level"),
                "approval_type": result.get("approval_type"),
                "approval_status": result.get("approval_status"),
                "timeout_duration": result.get("timeout_duration"),
                "approval_request": result.get("approval_request"),
                "pending_approval": result.get("pending_approval"),
                "error": result.get("error"),
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Approval gate creation failed: {str(e)}",
            }

    async def process_approval_response(
        self,
        gate_id: str,
        workspace_id: str,
        session_id: str,
        approved: bool,
        reason: str = "",
        approver_id: str = "",
    ) -> Dict[str, Any]:
        """Process human approval response."""
        if not self.graph:
            self.create_graph()

        # Load existing state
        thread_config = {
            "configurable": {
                "thread_id": f"approval_{session_id}",
                "checkpoint_ns": f"approval_{workspace_id}",
            }
        }

        try:
            # Get current checkpoint
            checkpoint = await self.graph.aget_state(thread_config)
            if not checkpoint:
                return {"success": False, "error": "No approval session found"}

            # Update state with approval response
            current_state = checkpoint.values
            current_state["approval_status"] = "approved" if approved else "rejected"
            current_state["approval_reason"] = reason
            current_state["approver_id"] = approver_id

            # Continue execution
            result = await self.graph.ainvoke(current_state, config=thread_config)

            return {
                "success": True,
                "gate_id": gate_id,
                "approval_status": result.get("approval_status"),
                "approval_reason": result.get("approval_reason"),
                "approval_timestamp": result.get("approval_timestamp"),
                "pending_approval": result.get("pending_approval"),
                "error": result.get("error"),
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Approval response processing failed: {str(e)}",
            }

    async def get_pending_approvals(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Get all pending approvals for a workspace."""
        pending_approvals = []

        for gate_id, state in self.approval_gate.active_gates.items():
            if (
                state.get("workspace_id") == workspace_id
                and state.get("approval_status") == "pending"
            ):

                pending_approvals.append(
                    {
                        "gate_id": gate_id,
                        "risk_level": state.get("risk_level"),
                        "approval_type": state.get("approval_type"),
                        "requested_at": state.get("approval_request", {}).get(
                            "requested_at"
                        ),
                        "timeout_at": state.get("approval_request", {}).get(
                            "timeout_at"
                        ),
                        "pending_output_preview": state.get("pending_output", "")[:200]
                        + "...",
                    }
                )

        return pending_approvals
