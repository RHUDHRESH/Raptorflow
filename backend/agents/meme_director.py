from typing import List

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel

from inference import InferenceProvider


class CanvasElement(BaseModel):
    id: str
    type: str = "text"
    x: int
    y: int
    text: str
    fontSize: int = 40
    fill: str = "#000000"


class MemePlan(BaseModel):
    concept: str
    elements: List[CanvasElement]


class MemeDirectorAgent:
    def __init__(self):
        self.llm = InferenceProvider.get_model(
            model_tier="smart"
        ).with_structured_output(MemePlan)

    async def design(self, prompt: str) -> MemePlan:
        system_msg = SystemMessage(
            content="""
            You are the Meme Director. Generate a layout plan for a high-quality industry meme.
            Return exactly what the Konva canvas needs to render.
            Standard canvas size is 600x600.
        """
        )

        return await self.llm.ainvoke([system_msg, HumanMessage(content=prompt)])
