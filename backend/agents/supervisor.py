import logging
from typing import List, Literal, TypedDict
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field

logger = logging.getLogger("raptorflow.supervisor")

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
        
        self.chain = self.prompt | llm.with_structured_output(RouterOutput)

    async def __call__(self, state: TypedDict):
        """The actual node logic, callable for LangGraph."""
        logger.info("Supervisor evaluating state...")
        # In a real SOTA system, we handle retry logic and JSON repair here
        response = await self.chain.ainvoke(state)
        logger.info(f"Supervisor delegated to: {response.next_node}")
        return {"next": response.next_node, "instructions": response.instructions}

def create_team_supervisor(llm: any, team_members: List[str], system_prompt: str):
    """Factory function for the HierarchicalSupervisor."""
    return HierarchicalSupervisor(llm, team_members, system_prompt)
