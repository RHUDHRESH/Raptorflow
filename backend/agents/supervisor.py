from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from typing import List, Literal
from inference import InferenceProvider

class TaskStep(BaseModel):
    agent: str = Field(description="The specialist to call (email, social, meme, strategy)")
    instruction: str = Field(description="Specific instruction for this step")

class MissionPlan(BaseModel):
    steps: List[TaskStep]
    rationale: str

class SupervisorAgent:
    def __init__(self):
        self.llm = InferenceProvider.get_model(model_tier="smart").with_structured_output(MissionPlan)

    async def create_plan(self, brief: dict) -> MissionPlan:
        system_msg = SystemMessage(content="""
            You are the RaptorFlow Mission Supervisor. 
            Break down the marketing goal into a sequence of agent calls.
            Available Agents: email, social, meme, strategy.
            Be surgical. Do not add unnecessary steps.
        """)
        
        return await self.llm.ainvoke([system_msg, HumanMessage(content=f"BRIEF: {brief}")])
