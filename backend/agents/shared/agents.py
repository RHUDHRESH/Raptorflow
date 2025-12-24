from typing import List

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from backend.inference import InferenceProvider


# --- A00: Intent Router ---
class Intent(BaseModel):
    asset_family: str = Field(description="email | social | meme | text | strategy")
    confidence: float
    entities: List[str] = Field(description="@mentions found")
    goal: str


class IntentRouter:
    def __init__(self):
        self.llm = InferenceProvider.get_model(
            model_tier="fast"
        ).with_structured_output(Intent)

    async def execute(self, prompt: str) -> Intent:
        return await self.llm.ainvoke(
            [
                SystemMessage(
                    content="Route intent surgically. Classify into family and extract entities."
                ),
                HumanMessage(content=prompt),
            ]
        )


# --- A05: Quality Gate (SOTA version) ---
class QualityCheck(BaseModel):
    pass_gate: bool
    score: int
    critical_fixes: List[str]
    brand_alignment: float


class QualityGate:
    def __init__(self):
        self.llm = InferenceProvider.get_model(
            model_tier="smart"
        ).with_structured_output(QualityCheck)

    async def audit(self, content: str, brief: dict) -> QualityCheck:
        return await self.llm.ainvoke(
            [
                SystemMessage(
                    content=f"You are the RaptorFlow Quality Gate. Audit against brief: {brief}. Be brutal."
                ),
                HumanMessage(content=content),
            ]
        )


# --- A08: Cost Governor ---
class CostGovernor:
    """Calculates and enforces per-run budgets."""

    def estimate_tokens(self, prompt: str, target_length: int) -> int:
        return len(prompt.split()) + target_length * 2

    async def validate_run(self, estimated_tokens: int, plan_tier: str) -> bool:
        # Business logic for tiers
        limits = {"starter": 10000, "pro": 50000, "founder": 200000}
        return estimated_tokens < limits.get(plan_tier, 5000)


# --- A10: Telemetry ---
class Telemetry:
    """Emits production logs for monitoring."""

    @staticmethod
    def log_run(thread_id: str, agent_id: str, cost: float, success: bool):
        # In prod, send to Datadog/CloudWatch
        print(
            f"[TELEMETRY] Thread: {thread_id} | Agent: {agent_id} | Cost: ${cost:.4f} | Success: {success}"
        )
