import logging
from datetime import datetime
from typing import Annotated, Any, Dict, List, Optional, TypedDict

from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field

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


class HierarchicalSupervisor:
    """
    SOTA Supervisor Node.
    Orchestrates specialized crews with surgical precision.
    """

    def __init__(self, llm: any, team_members: List[str], system_prompt: str):
        self.llm = llm
        self.team_members = team_members
        options = team_members + ["FINISH"]

        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="messages"),
                (
                    "system",
                    "Given the conversation above, who should act next?"
                    " Or should we FINISH? Select one of: {options}",
                ),
            ]
        ).partial(options=str(options))

        # We don't pre-build the chain to allow easier mocking of llm
        self._chain = None

    @property
    def chain(self):
        if self._chain is None:
            self._chain = self.prompt | self.llm.with_structured_output(RouterOutput)
        return self._chain

    async def __call__(self, state: TypedDict):
        """The actual node logic, callable for LangGraph."""
        logger.info("Supervisor evaluating state...")
        # In a real SOTA system, we handle retry logic and JSON repair here
        response = await self.chain.ainvoke(state)

        # Check if it's a dict or model
        if hasattr(response, "next_node"):
            next_node = response.next_node
            instructions = response.instructions
        else:
            next_node = response.get("next_node")
            instructions = response.get("instructions")

        logger.info(f"Supervisor delegated to: {next_node}")
        return {"next": str(next_node), "instructions": str(instructions)}

    async def route_intent(self, query: str) -> str:
        """
        Determines the appropriate specialist crew based on a raw user query.
        """
        from langchain_core.messages import HumanMessage

        state = {"messages": [HumanMessage(content=query)]}
        response = await self.chain.ainvoke(state)

        if hasattr(response, "next_node"):
            return str(response.next_node)
        return str(response.get("next_node", "FINISH"))

    async def execute_loop(
        self, initial_state: Dict[str, Any], nodes: Dict[str, any]
    ) -> Dict[str, Any]:
        """
        Manages a multi-turn agentic loop between specialists.
        """
        from langchain_core.messages import AIMessage

        current_state = initial_state.copy()
        if "messages" not in current_state:
            current_state["messages"] = []

        loop_count = 0
        max_loops = 10

        while loop_count < max_loops:
            # 1. Ask supervisor who goes next
            decision = await self.__call__(current_state)
            next_node = decision["next"]
            instructions = decision["instructions"]

            if next_node == "FINISH":
                break

            # 2. Call specialist
            if next_node in nodes:
                specialist_node = nodes[next_node]
                # Inject instructions into state for the specialist
                current_state["instructions"] = instructions
                result = await self.delegate_to_specialist(
                    next_node, current_state, specialist_node
                )

                # 3. Update state with specialist finding
                summary = result.get("analysis_summary", "Task completed.")
                current_state["messages"].append(
                    AIMessage(content=f"[{next_node}]: {summary}")
                )
            else:
                logger.error(f"Specialist {next_node} not found in nodes.")
                break

            loop_count += 1

        current_state["next"] = "FINISH"
        from backend.services.evaluation import EvaluationService

        evaluator = EvaluationService()
        evaluation = evaluator.evaluate_run(
            telemetry_events=current_state.get("telemetry_events", []),
            output_summary=current_state.get("final_output")
            or current_state.get("summary")
            or current_state.get("instructions"),
            user_feedback=current_state.get("user_feedback"),
            run_id=current_state.get("thread_id") or current_state.get("run_id"),
            tenant_id=current_state.get("tenant_id") or current_state.get("workspace_id"),
        )
        current_state["evaluation"] = evaluation
        return current_state

    async def delegate_to_specialist(
        self, specialist_name: str, state: Dict[str, Any], specialist_node: any
    ) -> Dict[str, Any]:
        """
        Executes a specialist node with the given instructions.
        """
        logger.info(f"Delegating task to specialist: {specialist_name}")
        # specialist_node is typically a LangGraph node or callable
        # We pass the state containing instructions
        result = await specialist_node(state)
        return result

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
