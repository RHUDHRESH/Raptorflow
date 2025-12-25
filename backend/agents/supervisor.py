import logging
from datetime import datetime
from typing import Annotated, Any, Dict, List, Optional, TypedDict

from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field

from backend.graphs.swarm_orchestrator import SwarmOrchestrator

logger = logging.getLogger("raptorflow.supervisor")


class MatrixState(TypedDict):
    """Real-time state for the Matrix Supervisor orchestration."""

    messages: Annotated[List[BaseMessage], "The conversation messages"]
    next: str
    instructions: str
    system_health: Dict[str, Any]
    active_agent_id: Optional[str]


class RouterOutput(BaseModel):
    """SOTA Structured output for the Supervisor router."""

    next_node: str = Field(
        description="The next specialist crew to call, or 'FINISH' to deliver to user."
    )
    instructions: str = Field(
        description="Specific sub-task instructions for the specialist."
    )


class HierarchicalSupervisor(SwarmOrchestrator):
    """
    Compatibility wrapper around the Swarm Orchestrator.
    Orchestrates specialized crews with surgical precision.
    """

    def __init__(self, llm: any, team_members: List[str], system_prompt: str):
        super().__init__(
            llm=llm,
            team_members=team_members,
            system_prompt=system_prompt,
            output_model=RouterOutput,
        )

    def aggregate_findings(self, findings: List[Dict[str, Any]]) -> str:
        """
        Summarizes outputs from multiple specialists into a unified boardroom brief.
        """
        logger.info(f"Aggregating {len(findings)} specialist findings...")

        summary_parts = ["### MATRIX BOARDROOM SUMMARY ###"]
        for i, finding in enumerate(findings):
            source = finding.get("source", f"Specialist {i+1}")
            text = finding.get("analysis_summary", "No summary provided.")
            summary_parts.append(f"- [{source}]: {text}")

        return "\n".join(summary_parts)


class HandoffProtocol:
    """
    Standardized protocol for agent-to-agent communication and context transfer.
    """

    @staticmethod
    def create_packet(
        source: str, target: str, context: Dict[str, Any], priority: str = "normal"
    ) -> Dict[str, Any]:
        """
        Creates a standardized handoff packet.
        """
        return {
            "source": source,
            "target": target,
            "context": context,
            "priority": priority,
            "timestamp": datetime.now().isoformat(),
        }

    @staticmethod
    def validate(packet: Dict[str, Any]) -> bool:
        """
        Validates the structure of a handoff packet.
        """
        required_keys = ["source", "target", "context", "priority"]
        return all(key in packet for key in required_keys)


class HumanInTheLoopNode:
    """
    Interrupt node for handling manual human approvals in critical workflows.
    """

    async def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Requests human intervention or processes a human response.
        """
        human_response = state.get("human_response")
        instructions = state.get("instructions", "No instructions provided.")

        if not human_response:
            logger.info("HITL: Awaiting human approval...")
            return {
                "approval_required": True,
                "approval_prompt": f"ACTION REQUIRED: {instructions}. Do you approve? (YES/NO)",
                "status": "AWAITING_HUMAN",
            }

        approved = human_response.strip().upper() == "YES"
        logger.info(
            f"HITL: Human response received: {human_response} (Approved: {approved})"
        )

        return {
            "approved": approved,
            "status": "APPROVED" if approved else "REJECTED",
            "analysis_summary": f"Human intervention complete. Approved: {approved}.",
        }


def create_team_supervisor(llm: any, team_members: List[str], system_prompt: str):
    """Factory function for the HierarchicalSupervisor."""
    return HierarchicalSupervisor(llm, team_members, system_prompt)
