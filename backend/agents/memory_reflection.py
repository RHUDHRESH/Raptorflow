import json
import logging
from typing import Any, Dict, List, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from backend.inference import InferenceProvider
from backend.memory.swarm_learning import SwarmLearningMemory

logger = logging.getLogger("raptorflow.agents.memory_reflection")


class DailyReflection(BaseModel):
    summary: str = Field(
        description="High-level narrative of the day's agentic activity."
    )
    learnings: List[str] = Field(
        description="Surgical learnings extracted from successes and failures."
    )
    confidence: float = Field(
        description="Score indicating how well the data supports these learnings."
    )


class MemoryReflectionAgent:
    """
    SOTA Memory Self-Reflection Agent.
    Periodically analyzes agent traces and episodic memories to extract high-level patterns.
    Functions as the 'System Conscience' that learns from historical activity.
    """

    def __init__(self, model_tier: str = "smart"):
        self.llm = InferenceProvider.get_model(
            model_tier=model_tier
        ).with_structured_output(DailyReflection)

    async def reflect_on_traces(
        self,
        workspace_id: str,
        traces: List[Dict[str, Any]],
        swarm_scope: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Analyzes a batch of traces to generate a daily summary and learnings."""
        if not traces:
            return {
                "summary": "No activity detected.",
                "learnings": [],
                "confidence": 1.0,
            }

        logger.info(
            f"MemoryReflectionAgent: Analyzing {len(traces)} traces for workspace {workspace_id}"
        )

        system_msg = SystemMessage(
            content="""
            You are the Cognitive Reflection Engine for RaptorFlow.
            Analyze the provided agent traces.
            Identify patterns, systemic bottlenecks, and successful strategies.
            Be surgical and professional. Avoid hype.
        """
        )

        traces_str = json.dumps(traces[:20])  # Limit context for SOTA efficiency

        try:
            reflection = await self.llm.ainvoke(
                [
                    system_msg,
                    HumanMessage(content=f"TRACES for analysis:\n{traces_str}"),
                ]
            )
            result = reflection.model_dump()

            if result.get("learnings"):
                swarm_memory = SwarmLearningMemory()
                for learning in result["learnings"]:
                    await swarm_memory.record_learning(
                        workspace_id=workspace_id,
                        content=learning,
                        source="high_confidence_outcome",
                        confidence=result.get("confidence", 0.0),
                        swarm_scope=swarm_scope,
                        metadata={"reflection_summary": result.get("summary", "")},
                    )

            return result
        except Exception as e:
            logger.error(f"Memory reflection failed: {e}")
            return {
                "summary": "Reflection failed due to internal error.",
                "learnings": [],
                "confidence": 0.0,
            }
