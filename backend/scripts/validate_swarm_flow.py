import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

from agents.memory_reflection import MemoryReflectionAgent
from agents.shared.agents import CostGovernor
from agents.supervisor import HandoffProtocol
from core.base_tool import BaseRaptorTool
from core.toolbelt import ToolbeltV2
from inference import InferenceProvider
from memory.swarm_l1 import SwarmL1MemoryManager
from models.swarm import SwarmTask, SwarmTaskStatus

logger = logging.getLogger("raptorflow.scripts.validate_swarm_flow")


class FakeAsyncRedis:
    def __init__(self):
        self._store: Dict[str, Any] = {}
        self._hashes: Dict[str, Dict[str, Any]] = {}

    async def set(self, key: str, value: Any, ex: Optional[int] = None):
        self._store[key] = value
        return True

    async def get(self, key: str):
        return self._store.get(key)

    async def delete(self, key: str):
        return self._store.pop(key, None) is not None

    async def incrby(self, key: str, amount: int = 1):
        current = int(self._store.get(key, 0))
        current += amount
        self._store[key] = current
        return current

    async def decrby(self, key: str, amount: int = 1):
        current = int(self._store.get(key, 0))
        current -= amount
        self._store[key] = current
        return current

    async def hset(self, key: str, field: str, value: Any):
        bucket = self._hashes.setdefault(key, {})
        bucket[field] = value
        return True

    async def hget(self, key: str, field: str):
        return self._hashes.get(key, {}).get(field)

    async def hgetall(self, key: str):
        return dict(self._hashes.get(key, {}))


@dataclass
class FakeLLMResponse:
    content: str


class FakeStructuredModel:
    def __init__(self, schema: Any, payload: Dict[str, Any]):
        self.schema = schema
        self.payload = payload

    async def ainvoke(self, _prompt: Any):
        if hasattr(self.schema, "model_validate"):
            return self.schema.model_validate(self.payload)
        return self.schema(**self.payload)


class FakeLLM:
    def __init__(self, content: str = "ok"):
        self.content = content

    def with_structured_output(self, schema: Any):
        payload = {
            "summary": "Swarm learning summary.",
            "learnings": [
                "Tool routing optimized",
                "Handoff latency reduced",
                "Budget checks enforced",
            ],
            "confidence": 0.91,
        }
        return FakeStructuredModel(schema, payload)

    async def ainvoke(self, _prompt: Any):
        return FakeLLMResponse(content=self.content)


class MockTool(BaseRaptorTool):
    @property
    def name(self) -> str:
        return "mock_search"

    @property
    def description(self) -> str:
        return "Mock search tool for swarm validation."

    async def _execute(self, **kwargs) -> Dict[str, Any]:
        query = kwargs.get("query", "")
        return {"query": query, "result": "mock-result"}


def require(condition: bool, message: str):
    if not condition:
        raise RuntimeError(f"Swarm validation failed: {message}")


async def run_swarm_flow():
    logger.info("Starting swarm flow validation.")

    InferenceProvider.get_model = staticmethod(lambda *args, **kwargs: FakeLLM())

    fake_redis = FakeAsyncRedis()
    memory = SwarmL1MemoryManager(thread_id="swarm_validation")
    memory.l1.client = fake_redis

    tasks = [
        SwarmTask(
            id="task_research",
            specialist_type="researcher",
            description="Gather competitive intel",
        ),
        SwarmTask(
            id="task_execution",
            specialist_type="executor",
            description="Run mock tool execution",
            status=SwarmTaskStatus.IN_PROGRESS,
        ),
    ]

    for task in tasks:
        await memory.update_task(task)

    await memory.update_knowledge("insight", {"summary": "Swarm insight logged"})

    stored_tasks = await memory.get_all_tasks()
    require(len(stored_tasks) == 2, "Expected two swarm tasks in L1 memory.")
    task_ids = {task.id for task in stored_tasks}
    require("task_research" in task_ids, "Missing research task in memory.")
    require("task_execution" in task_ids, "Missing execution task in memory.")

    insight = await memory.get_knowledge("insight")
    require(insight is not None, "Shared knowledge entry not found in memory.")
    require(
        insight.get("summary") == "Swarm insight logged",
        "Shared knowledge payload mismatch.",
    )

    handoff_packet = HandoffProtocol.create_packet(
        source="supervisor",
        target="executor",
        context={"task_id": "task_execution", "priority": "high"},
    )
    require(HandoffProtocol.validate(handoff_packet), "Invalid handoff packet.")

    toolbelt = ToolbeltV2()
    toolbelt.tools = {"mock_search": MockTool()}
    tool_response = await toolbelt.run_tool("mock_search", query="swarm query")
    require(tool_response.get("success"), "Tool call failed.")
    require(
        tool_response.get("data", {}).get("result") == "mock-result",
        "Tool response payload mismatch.",
    )

    governor = CostGovernor()
    estimated_tokens = governor.estimate_tokens(
        "Run swarm validation", target_length=120
    )
    budget_allowed = await governor.validate_run(
        estimated_tokens=estimated_tokens, plan_tier="starter"
    )
    require(budget_allowed, "Budget validation failed.")

    reflection_agent = MemoryReflectionAgent(model_tier="smart")
    reflection = await reflection_agent.reflect_on_traces(
        workspace_id="workspace_swarm",
        traces=[
            {"agent": "executor", "event": "tool_call", "success": True},
            {"agent": "supervisor", "event": "handoff", "success": True},
        ],
    )
    require(reflection.get("learnings"), "Learning updates missing.")
    require(reflection.get("confidence", 0.0) > 0.5, "Low learning confidence.")

    logger.info("Swarm flow validation complete.")


def main():
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(run_swarm_flow())
    except Exception as exc:
        logger.exception("Swarm flow validation failed.")
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
