import logging
import uuid
from typing import List, Literal, TypedDict, Dict, Any, Annotated, Optional
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from backend.inference import InferenceProvider
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
    next_node: str = Field(description="The next specialist crew to call, or 'FINISH' to deliver to user.")
    instructions: str = Field(description="Specific sub-task instructions for the specialist.")

class HierarchicalSupervisor:
    """
    SOTA Supervisor Node.
    Orchestrates specialized crews with surgical precision.
    """
    def __init__(self, llm: any, team_members: List[str], system_prompt: str):
        self.llm = llm
        self.team_members = team_members
        options = team_members + ["FINISH"]
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            (
                "system",
                "Given the conversation above, who should act next?"
                " Or should we FINISH? Select one of: {options}"
            ),
        ]).partial(options=str(options))
        
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

def create_team_supervisor(llm: any, team_members: List[str], system_prompt: str):
    """Factory function for the HierarchicalSupervisor."""
    return HierarchicalSupervisor(llm, team_members, system_prompt)
