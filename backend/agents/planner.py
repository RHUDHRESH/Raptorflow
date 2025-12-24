import logging
from typing import List, TypedDict

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from backend.models.fortress import FortressTask

logger = logging.getLogger("raptorflow.planner")


class Plan(BaseModel):
    """Structured plan composed of multiple tasks."""

    tasks: List[FortressTask] = Field(description="The list of tasks to execute.")


class TaskDecomposer:
    """
    SOTA Task Decomposition Node.
    Breaks massive marketing goals into a surgical task queue.
    """

    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a master marketing project manager. "
                    "Decompose the user's goal into a logical sequence of sub-tasks "
                    "for the following crews: research, strategy, creative, operator.",
                ),
                ("user", "{goal}"),
            ]
        )
        self.chain = self.prompt | llm.with_structured_output(Plan)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        goal = state.get("raw_prompt", "No goal provided")
        logger.info(f"Decomposing goal: {goal[:50]}...")

        plan = await self.chain.ainvoke({"goal": goal})
        logger.info(f"Decomposition complete. Created {len(plan.tasks)} tasks.")

        return {"task_queue": plan.tasks, "current_brief": plan.model_dump()}


def create_task_decomposer(llm: any):
    return TaskDecomposer(llm)
