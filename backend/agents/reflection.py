from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from typing import List
from inference import InferenceProvider

class Critique(BaseModel):
    is_premium: bool = Field(description="Does it meet MasterClass/Surgical standards?")
    flaws: List[str] = Field(description="List of specific flaws (cringe, hype, vague, off-brand)")
    fixes: List[str] = Field(description="Step-by-step instructions to fix")
    score: int = Field(description="0-100 quality score")

class ReflectionAgent:
    def __init__(self):
        self.llm = InferenceProvider.get_model(model_tier="smart").with_structured_output(Critique)

    async def critique(self, content: str, brief: dict) -> Critique:
        system_msg = SystemMessage(content=f"""
            You are the Surgical Critic. Your standards are impossibly high.
            Audit the following content against the RaptorFlow Brand Kit and User Brief.
            
            BRAND KIT: {brief.get('tone', 'Surgical, Calm, Professional')}
            
            If it sounds like a basic AI wrote it, fail it.
            If it uses 'unlock', 'game-changer', or 'journey', fail it.
        """)
        
        return await self.llm.ainvoke([system_msg, HumanMessage(content=content)])
