"""
Agent Handoff for Protocol Standardization

Standardized handoff protocol between cognitive agents.
Implements PROMPT 73 from STREAM_3_COGNITIVE_ENGINE.
"""

import asyncio
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

from .messages import AgentMessage, MessageFormat, MessageType


class HandoffType(Enum):
    """Types of agent handoffs."""

    FORWARD = "forward"
    BACKWARD = "backward"
    LATERAL = "lateral"
    ESCALATION = "escalation"
    DELEGATION = "delegation"
    COLLABORATION = "collaboration"


class HandoffStatus(Enum):
    """Status of handoff operations."""

    INITIATED = "initiated"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class HandoffReason(Enum):
    """Reasons for agent handoffs."""

    CAPABILITY_MISMATCH = "capability_mismatch"
    RESOURCE_CONSTRAINT = "resource_constraint"
    EXPERTISE_REQUIRED = "expertise_required"
    AUTHORIZATION_NEEDED = "authorization_needed"
    WORKLOAD_BALANCE = "workload_balance"
    ERROR_RECOVERY = "error_recovery"
    COLLABORATION_NEEDED = "collaboration_needed"
    ESCALATION_REQUIRED = "escalation_required"


@dataclass
class HandoffContext:
    """Context information for handoff."""

    handoff_id: str
    from_agent: str
    to_agent: str
    handoff_type: HandoffType
    reason: HandoffReason
    priority: str  # "low", "medium", "high", "critical"
    task_data: Dict[str, Any]
    session_data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize handoff ID."""
        if not self.handoff_id:
            self.handoff_id = str(uuid.uuid4())


@dataclass
class HandoffRequest:
    """Request for agent handoff."""

    handoff_id: str
    from_agent: str
    to_agent: str
    handoff_type: HandoffType
    reason: HandoffReason
    task_data: Dict[str, Any]
    session_data: Dict[str, Any]
    deadline: Optional[datetime]
    requirements: List[str]
    constraints: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HandoffResponse:
    """Response to handoff request."""

    handoff_id: str
    from_agent: str
    to_agent: str
    status: HandoffStatus
    response: str
    conditions: List[str]
    estimated_time: Optional[int]
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentHandoff:
    """
    Standardized handoff protocol between cognitive agents.

    Manages secure and efficient agent-to-agent transitions.
    """

    def __init__(self, message_broker=None, timeout_seconds: int = 300):
        """
        Initialize the agent handoff system.

        Args:
            message_broker: Message broker for communication
            timeout_seconds: Default timeout for handoff operations
        """
        self.message_broker = message_broker
        self.timeout_seconds = timeout_seconds

        # Handoff tracking
        self.active_handoffs: Dict[str, HandoffContext] = {}
        self.handoff_history: List[Dict[str, Any]] = []

        # Agent capabilities registry
        self.agent_capabilities: Dict[str, Set[str]] = {}
        self.agent_workloads: Dict[str, Dict[str, Any]] = {}

        # Handoff rules
        self.handoff_rules: List[Dict[str, Any]] = []

        # Statistics
        self.stats = {
            "total_handoffs": 0,
            "successful_handoffs": 0,
            "failed_handoffs": 0,
            "timeout_handoffs": 0,
            "handoffs_by_type": {},
            "handoffs_by_reason": {},
            "average_handoff_time_seconds": 0.0,
        }

        # Setup default handoff rules
        self._setup_default_rules()

    async def initiate_handoff(
        self,
        from_agent: str,
        to_agent: str,
        handoff_type: HandoffType,
        reason: HandoffReason,
        task_data: Dict[str, Any],
        session_data: Dict[str, Any] = None,
        requirements: List[str] = None,
        constraints: List[str] = None,
        deadline: datetime = None,
    ) -> HandoffResponse:
        """
        Initiate a handoff between agents.

        Args:
            from_agent: Agent initiating handoff
            to_agent: Target agent
            handoff_type: Type of handoff
            reason: Reason for handoff
            task_data: Task data to transfer
            session_data: Session context data
            requirements: Requirements for handoff
            constraints: Constraints on handoff
            deadline: Deadline for handoff completion

        Returns:
            Handoff response
        """
        handoff_id = str(uuid.uuid4())

        # Create handoff context
        context = HandoffContext(
            handoff_id=handoff_id,
            from_agent=from_agent,
            to_agent=to_agent,
            handoff_type=handoff_type,
            reason=reason,
            priority=self._determine_priority(reason, task_data),
            task_data=task_data,
            session_data=session_data or {},
        )

        # Store active handoff
        self.active_handoffs[handoff_id] = context

        try:
            # Validate handoff
            validation_result = await self._validate_handoff(context)
            if not validation_result.valid:
                return HandoffResponse(
                    handoff_id=handoff_id,
                    from_agent=from_agent,
                    to_agent=to_agent,
                    status=HandoffStatus.REJECTED,
                    response=validation_result.reason,
                    conditions=[],
                    estimated_time=None,
                    metadata={"validation_failed": True},
                )

            # Create handoff request
            request = HandoffRequest(
                handoff_id=handoff_id,
                from_agent=from_agent,
                to_agent=to_agent,
                handoff_type=handoff_type,
                reason=reason,
                task_data=task_data,
                session_data=session_data or {},
                deadline=deadline,
                requirements=requirements or [],
                constraints=constraints or [],
            )

            # Send handoff request
            await self._send_handoff_request(request)

            # Wait for response
            response = await self._wait_for_response(handoff_id)

            if response.status == HandoffStatus.ACCEPTED:
                # Complete handoff
                await self._complete_handoff(context, response)
                self.stats["successful_handoffs"] += 1
            else:
                self.stats["failed_handoffs"] += 1

            # Update statistics
            self._update_handoff_stats(context, response)

            return response

        except asyncio.TimeoutError:
            self.stats["timeout_handoffs"] += 1
            return HandoffResponse(
                handoff_id=handoff_id,
                from_agent=from_agent,
                to_agent=to_agent,
                status=HandoffStatus.TIMEOUT,
                response="Handoff request timed out",
                conditions=[],
                estimated_time=None,
                metadata={"timeout": True},
            )

        except Exception as e:
            self.stats["failed_handoffs"] += 1
            return HandoffResponse(
                handoff_id=handoff_id,
                from_agent=from_agent,
                to_agent=to_agent,
                status=HandoffStatus.FAILED,
                response=f"Handoff failed: {str(e)}",
                conditions=[],
                estimated_time=None,
                metadata={"error": str(e)},
            )

        finally:
            # Clean up active handoff
            self.active_handoffs.pop(handoff_id, None)

    async def accept_handoff(
        self, handoff_id: str, conditions: List[str] = None, estimated_time: int = None
    ) -> HandoffResponse:
        """Accept a handoff request."""
        context = self.active_handoffs.get(handoff_id)
        if not context:
            raise ValueError(f"Handoff {handoff_id} not found")

        response = HandoffResponse(
            handoff_id=handoff_id,
            from_agent=context.from_agent,
            to_agent=context.to_agent,
            status=HandoffStatus.ACCEPTED,
            response="Handoff accepted",
            conditions=conditions or [],
            estimated_time=estimated_time,
            metadata={"accepted_at": datetime.now().isoformat()},
        )

        # Send response
        await self._send_handoff_response(response)

        return response

    async def reject_handoff(
        self, handoff_id: str, reason: str, conditions: List[str] = None
    ) -> HandoffResponse:
        """Reject a handoff request."""
        context = self.active_handoffs.get(handoff_id)
        if not context:
            raise ValueError(f"Handoff {handoff_id} not found")

        response = HandoffResponse(
            handoff_id=handoff_id,
            from_agent=context.from_agent,
            to_agent=context.to_agent,
            status=HandoffStatus.REJECTED,
            response=reason,
            conditions=conditions or [],
            estimated_time=None,
            metadata={"rejected_at": datetime.now().isoformat()},
        )

        # Send response
        await self._send_handoff_response(response)

        return response

    async def complete_handoff(self, handoff_id: str, result: Dict[str, Any]) -> None:
        """Complete a handoff operation."""
        context = self.active_handoffs.get(handoff_id)
        if not context:
            raise ValueError(f"Handoff {handoff_id} not found")

        # Mark as completed
        await self._mark_handoff_completed(context, result)

        # Notify completion
        await self._notify_handoff_completion(context, result)

    def register_agent_capabilities(
        self, agent_id: str, capabilities: Set[str]
    ) -> None:
        """Register agent capabilities."""
        self.agent_capabilities[agent_id] = capabilities

    def update_agent_workload(self, agent_id: str, workload: Dict[str, Any]) -> None:
        """Update agent workload information."""
        self.agent_workloads[agent_id] = workload

    def find_suitable_agents(
        self, required_capabilities: Set[str], exclude_agents: Set[str] = None
    ) -> List[str]:
        """Find agents with required capabilities."""
        suitable_agents = []

        for agent_id, capabilities in self.agent_capabilities.items():
            if exclude_agents and agent_id in exclude_agents:
                continue

            if required_capabilities.issubset(capabilities):
                suitable_agents.append(agent_id)

        # Sort by workload (least loaded first)
        suitable_agents.sort(
            key=lambda agent_id: self.agent_workloads.get(agent_id, {}).get(
                "current_load", 0
            )
        )

        return suitable_agents

    async def auto_handoff(
        self,
        from_agent: str,
        reason: HandoffReason,
        task_data: Dict[str, Any],
        session_data: Dict[str, Any] = None,
    ) -> HandoffResponse:
        """Automatically find and handoff to suitable agent."""
        # Determine required capabilities from task data
        required_capabilities = self._extract_required_capabilities(task_data, reason)

        # Find suitable agents
        exclude_agents = {from_agent}
        suitable_agents = self.find_suitable_agents(
            required_capabilities, exclude_agents
        )

        if not suitable_agents:
            return HandoffResponse(
                handoff_id="",
                from_agent=from_agent,
                to_agent="",
                status=HandoffStatus.FAILED,
                response="No suitable agents found",
                conditions=[],
                estimated_time=None,
                metadata={"no_suitable_agents": True},
            )

        # Try first suitable agent
        to_agent = suitable_agents[0]

        return await self.initiate_handoff(
            from_agent=from_agent,
            to_agent=to_agent,
            handoff_type=HandoffType.FORWARD,
            reason=reason,
            task_data=task_data,
            session_data=session_data,
        )

    def get_handoff_status(self, handoff_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a handoff."""
        context = self.active_handoffs.get(handoff_id)
        if not context:
            return None

        return {
            "handoff_id": handoff_id,
            "from_agent": context.from_agent,
            "to_agent": context.to_agent,
            "handoff_type": context.handoff_type.value,
            "reason": context.reason.value,
            "priority": context.priority,
            "status": "active",
            "metadata": context.metadata,
        }

    def get_handoff_history(
        self, agent_id: str = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get handoff history."""
        history = self.handoff_history

        if agent_id:
            history = [
                entry
                for entry in history
                if entry.get("from_agent") == agent_id
                or entry.get("to_agent") == agent_id
            ]

        return history[-limit:]

    def get_handoff_stats(self) -> Dict[str, Any]:
        """Get handoff statistics."""
        return self.stats

    def _determine_priority(
        self, reason: HandoffReason, task_data: Dict[str, Any]
    ) -> str:
        """Determine handoff priority."""
        high_priority_reasons = [
            HandoffReason.ESCALATION_REQUIRED,
            HandoffReason.ERROR_RECOVERY,
            HandoffReason.AUTHORIZATION_NEEDED,
        ]

        if reason in high_priority_reasons:
            return "high"

        # Check task data for priority indicators
        if task_data.get("urgent", False):
            return "high"
        elif task_data.get("important", False):
            return "medium"
        else:
            return "low"

    async def _validate_handoff(self, context: HandoffContext) -> HandoffResponse:
        """Validate handoff request."""
        # Check if target agent exists
        if context.to_agent not in self.agent_capabilities:
            return HandoffResponse(
                handoff_id=context.handoff_id,
                from_agent=context.from_agent,
                to_agent=context.to_agent,
                status=HandoffStatus.REJECTED,
                response="Target agent not found",
                conditions=[],
                estimated_time=None,
                metadata={"validation_failed": True},
            )

        # Check handoff rules
        for rule in self.handoff_rules:
            if self._matches_rule(context, rule):
                if rule.get("action") == "reject":
                    return HandoffResponse(
                        handoff_id=context.handoff_id,
                        from_agent=context.from_agent,
                        to_agent=context.to_agent,
                        status=HandoffStatus.REJECTED,
                        response=rule.get("reason", "Handoff rejected by rule"),
                        conditions=rule.get("conditions", []),
                        estimated_time=None,
                        metadata={"rule_rejection": True},
                    )

        return HandoffResponse(
            handoff_id=context.handoff_id,
            from_agent=context.from_agent,
            to_agent=context.to_agent,
            status=HandoffStatus.ACCEPTED,
            response="Handoff validated",
            conditions=[],
            estimated_time=None,
            metadata={"validation_passed": True},
        )

    def _matches_rule(self, context: HandoffContext, rule: Dict[str, Any]) -> bool:
        """Check if handoff matches a rule."""
        # Check agent patterns
        from_pattern = rule.get("from_agent_pattern")
        to_pattern = rule.get("to_agent_pattern")

        if from_pattern and not self._matches_pattern(context.from_agent, from_pattern):
            return False

        if to_pattern and not self._matches_pattern(context.to_agent, to_pattern):
            return False

        # Check handoff type
        if (
            "handoff_type" in rule
            and rule["handoff_type"] != context.handoff_type.value
        ):
            return False

        # Check reason
        if "reason" in rule and rule["reason"] != context.reason.value:
            return False

        return True

    def _matches_pattern(self, value: str, pattern: str) -> bool:
        """Check if value matches pattern."""
        # Simple pattern matching (in production, use regex)
        if pattern == "*":
            return True
        elif pattern.startswith("*") and pattern.endswith("*"):
            return pattern[1:-1] in value
        elif pattern.startswith("*"):
            return value.endswith(pattern[1:])
        elif pattern.endswith("*"):
            return value.startswith(pattern[:-1])
        else:
            return value == pattern

    async def _send_handoff_request(self, request: HandoffRequest) -> None:
        """Send handoff request to target agent."""
        message = MessageFormat.create_request(
            from_agent=request.from_agent,
            to_agent=request.to_agent,
            payload={
                "handoff_id": request.handoff_id,
                "handoff_type": request.handoff_type.value,
                "reason": request.reason.value,
                "task_data": request.task_data,
                "session_data": request.session_data,
                "requirements": request.requirements,
                "constraints": request.constraints,
                "deadline": request.deadline.isoformat() if request.deadline else None,
            },
            priority=MessagePriority.NORMAL,
            correlation_id=request.handoff_id,
        )

        if self.message_broker:
            await self.message_broker.send_to_agent(request.to_agent, message)

    async def _send_handoff_response(self, response: HandoffResponse) -> None:
        """Send handoff response to requesting agent."""
        message = MessageFormat.create_response(
            from_agent=response.to_agent,
            to_agent=response.from_agent,
            payload={
                "handoff_id": response.handoff_id,
                "status": response.status.value,
                "response": response.response,
                "conditions": response.conditions,
                "estimated_time": response.estimated_time,
            },
            correlation_id=response.handoff_id,
        )

        if self.message_broker:
            await self.message_broker.send_to_agent(response.from_agent, message)

    async def _wait_for_response(self, handoff_id: str) -> HandoffResponse:
        """Wait for handoff response."""
        # This would integrate with message broker to wait for response
        # For now, simulate response
        await asyncio.sleep(0.1)

        # Create mock response
        return HandoffResponse(
            handoff_id=handoff_id,
            from_agent="",
            to_agent="",
            status=HandoffStatus.ACCEPTED,
            response="Handoff accepted",
            conditions=[],
            estimated_time=60,
            metadata={"simulated": True},
        )

    async def _complete_handoff(
        self, context: HandoffContext, response: HandoffResponse
    ) -> None:
        """Complete handoff operation."""
        # Transfer task data
        await self._transfer_task_data(context, response)

        # Update agent workloads
        await self._update_workloads(context)

        # Record handoff completion
        await self._record_handoff_completion(context, response)

    async def _transfer_task_data(
        self, context: HandoffContext, response: HandoffResponse
    ) -> None:
        """Transfer task data to target agent."""
        # This would integrate with the target agent to accept task data
        pass

    async def _update_workloads(self, context: HandoffContext) -> None:
        """Update agent workloads after handoff."""
        # Decrease workload for source agent
        from_workload = self.agent_workloads.get(context.from_agent, {})
        from_workload["current_load"] = from_workload.get("current_load", 0) - 1
        self.agent_workloads[context.from_agent] = from_workload

        # Increase workload for target agent
        to_workload = self.agent_workloads.get(context.to_agent, {})
        to_workload["current_load"] = to_workload.get("current_load", 0) + 1
        self.agent_workloads[context.to_agent] = to_workload

    async def _record_handoff_completion(
        self, context: HandoffContext, response: HandoffResponse
    ) -> None:
        """Record handoff completion."""
        completion_record = {
            "handoff_id": context.handoff_id,
            "from_agent": context.from_agent,
            "to_agent": context.to_agent,
            "handoff_type": context.handoff_type.value,
            "reason": context.reason.value,
            "status": response.status.value,
            "response": response.response,
            "completed_at": datetime.now().isoformat(),
            "metadata": {
                "priority": context.priority,
                "conditions": response.conditions,
                "estimated_time": response.estimated_time,
            },
        }

        self.handoff_history.append(completion_record)

    async def _notify_handoff_completion(
        self, context: HandoffContext, result: Dict[str, Any]
    ) -> None:
        """Notify agents of handoff completion."""
        # Send completion notification
        message = MessageFormat.create_notification(
            from_agent="handoff_system",
            to_agent=context.from_agent,
            title="Handoff Completed",
            message=f"Handoff {context.handoff_id} to {context.to_agent} completed",
            priority=MessagePriority.NORMAL,
        )

        if self.message_broker:
            await self.message_broker.send_to_agent(context.from_agent, message)

    async def _mark_handoff_completed(
        self, context: HandoffContext, result: Dict[str, Any]
    ) -> None:
        """Mark handoff as completed."""
        # Update context status
        context.metadata["completed_at"] = datetime.now().isoformat()
        context.metadata["result"] = result

    def _extract_required_capabilities(
        self, task_data: Dict[str, Any], reason: HandoffReason
    ) -> Set[str]:
        """Extract required capabilities from task data."""
        capabilities = set()

        # Extract from task data
        if "required_capabilities" in task_data:
            capabilities.update(task_data["required_capabilities"])

        # Add capabilities based on reason
        reason_capabilities = {
            HandoffReason.CAPABILITY_MISMATCH: {"general_processing"},
            HandoffReason.EXPERTISE_REQUIRED: {"expert_analysis"},
            HandoffReason.AUTHORIZATION_NEEDED: {"authorization"},
            HandoffReason.ESCALATION_REQUIRED: {"escalation_handling"},
            HandoffReason.COLLABORATION_NEEDED: {"collaboration"},
        }

        capabilities.update(reason_capabilities.get(reason, set()))

        return capabilities

    def _update_handoff_stats(
        self, context: HandoffContext, response: HandoffResponse
    ) -> None:
        """Update handoff statistics."""
        self.stats["total_handoffs"] += 1

        # Type statistics
        handoff_type = context.handoff_type.value
        self.stats["handoffs_by_type"][handoff_type] = (
            self.stats["handoffs_by_type"].get(handoff_type, 0) + 1
        )

        # Reason statistics
        reason = context.reason.value
        self.stats["handoffs_by_reason"][reason] = (
            self.stats["handoffs_by_reason"].get(reason, 0) + 1
        )

    def _setup_default_rules(self) -> None:
        """Setup default handoff rules."""
        # Reject handoffs to overloaded agents
        self.handoff_rules.append(
            {
                "to_agent_pattern": "*",
                "action": "reject",
                "reason": "Target agent is overloaded",
                "condition": "workload > 0.8",
            }
        )

        # Require authorization for certain handoff types
        self.handoff_rules.append(
            {
                "handoff_type": "escalation",
                "action": "require_approval",
                "reason": "Escalation requires approval",
            }
        )

    def add_handoff_rule(self, rule: Dict[str, Any]) -> None:
        """Add a custom handoff rule."""
        self.handoff_rules.append(rule)

    def remove_handoff_rule(self, rule_index: int) -> bool:
        """Remove a handoff rule."""
        if 0 <= rule_index < len(self.handoff_rules):
            self.handoff_rules.pop(rule_index)
            return True
        return False

    def get_agent_capabilities(self, agent_id: str) -> Set[str]:
        """Get capabilities for an agent."""
        return self.agent_capabilities.get(agent_id, set())

    def get_agent_workload(self, agent_id: str) -> Dict[str, Any]:
        """Get workload information for an agent."""
        return self.agent_workloads.get(agent_id, {})
