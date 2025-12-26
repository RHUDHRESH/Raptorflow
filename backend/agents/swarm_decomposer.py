import logging
from typing import Any, List, TypedDict

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from inference import InferenceProvider
from models.swarm import SwarmSubtaskSpec, SwarmTask

logger = logging.getLogger("raptorflow.agents.swarm_decomposer")


class SwarmDecompositionPlan(BaseModel):
    """Structured decomposition plan for a swarm mission."""

    subtasks: List[SwarmSubtaskSpec] = Field(
        description="Ordered list of subtasks the swarm should execute."
    )


class SwarmTaskDecomposer:
    """
    Swarm-focused decomposition agent.
    Breaks a large goal into specialist-ready subtask specifications.
    """

    def __init__(self, llm: Any | None = None):
        self.llm = llm or InferenceProvider.get_model(model_tier="reasoning")
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are the Swarm Decomposition Agent for RaptorFlow. "
                    "Break the user's mission into concise, specialist-owned subtasks. "
                    "Use specialist types like research, strategy, creative, operator, or qa. "
                    "Each subtask must be independently executable with clear success criteria.",
                ),
                ("user", "{goal}"),
            ]
        )
        self.chain = self.prompt | self.llm.with_structured_output(SwarmDecompositionPlan)

    async def __call__(self, state: TypedDict) -> dict:
        """Generate swarm subtask specs from the incoming state."""
        goal = state.get("raw_prompt") or state.get("prompt") or "No goal provided"
        logger.info("Decomposing swarm goal into subtasks.")

        plan = await self.chain.ainvoke({"goal": goal})
        specs = plan.subtasks
        tasks = [
            SwarmTask(
                id=spec.id,
                specialist_type=spec.specialist_type,
                description=spec.objective,
                metadata={
                    "success_criteria": spec.success_criteria,
                    "dependencies": spec.dependencies,
                    "inputs": spec.inputs,
                },
            )
            for spec in specs
        ]

        return {"subtask_specs": specs, "swarm_tasks": tasks}


def create_swarm_decomposer(llm: Any | None = None) -> SwarmTaskDecomposer:
    return SwarmTaskDecomposer(llm=llm)
