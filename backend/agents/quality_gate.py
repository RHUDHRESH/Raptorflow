from inference import InferenceProvider
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from typing import List

class QualityReport(BaseModel):
    score: int = Field(description="Score from 0-100")
    passed: bool = Field(description="Whether the asset passes the quality gate")
    violations: List[str] = Field(description="Specific brand or quality violations")
    suggestions: List[str] = Field(description="Actionable fixes")

class QualityGateAgent:
    def __init__(self):
        # Use 'smart' tier for high-fidelity QA
        self.llm = InferenceProvider.get_model(model_tier="smart", temperature=0.0).with_structured_output(QualityReport)

    async def check(self, content: str, brief: dict) -> QualityReport:
        system_msg = SystemMessage(content=f"""
            You are the Quality Gate for RaptorFlow.
            Audit the following content against the provided brief.
            
            BRIEF: {brief}
            
            CHECKLIST:
            1. Tone: Is it surgical and professional? (No hype)
            2. Clarity: Is the goal immediate clear?
            3. Constraints: Are all constraints followed?
            4. Effectiveness: Is the CTA strong?
        """)
        
        return await self.llm.ainvoke([system_msg, HumanMessage(content=content)])
