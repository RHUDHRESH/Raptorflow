import inspect
import logging
from typing import Any, Callable, Dict, List, Optional, Tuple

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field

from backend.agents.router import IntentRouterAgent
from backend.models.cognitive import (
    ResourceBudget,
    RoutingMetadata,
    SharedMemoryHandles,
)

logger = logging.getLogger("raptorflow.swarm_orchestrator")


class SwarmRoutingDecision(BaseModel):
    """Structured output for the Swarm Controller router."""

    next_node: str = Field(
        description="The next swarm to call, or 'FINISH' to terminate."
    )
    instructions: str = Field(description="Instructions for the delegated swarm.")
    rationale: Optional[str] = Field(default=None, description="Routing rationale.")


class SwarmOrchestrator:
    """
    Top-level Swarm Controller coordinating specialized sub-swarms.
    Replaces ad-hoc routing and loop logic with a consistent orchestration layer.
    """

    def __init__(
        self,
        llm: Any,
        team_members: Optional[List[str]] = None,
        system_prompt: str = "",
        sub_swarms: Optional[Dict[str, Any]] = None,
        router_agent: Optional[IntentRouterAgent] = None,
        output_model: type[BaseModel] = SwarmRoutingDecision,
    ):
        self.llm = llm
        self.team_members = team_members or [
            "strategists",
            "researchers",
            "creatives",
            "quality",
        ]
        options = self.team_members + ["FINISH"]

        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt or "You are the Swarm Controller."),
                MessagesPlaceholder(variable_name="messages"),
                (
                    "system",
                    "Given the conversation above, who should act next?"
                    " Or should we FINISH? Select one of: {options}",
                ),
            ]
        ).partial(options=str(options))

        self.output_model = output_model
        self._chain = None
        self.router_agent = router_agent or IntentRouterAgent()
        self.sub_swarms = sub_swarms or {}
        self.swarm_tree = self._build_swarm_tree()

    @property
    def chain(self):
        if self._chain is None:
            self._chain = self.prompt | self.llm.with_structured_output(
                self.output_model
            )
        return self._chain

    def _build_swarm_tree(self) -> Dict[str, Tuple[str, ...]]:
        return {
            "controller": tuple(self.team_members),
            "strategists": ("researchers", "creatives", "quality"),
            "researchers": ("strategists", "quality"),
            "creatives": ("quality",),
            "quality": ("strategists", "creatives"),
        }

    def _ensure_metadata(self, state: Dict[str, Any]) -> Dict[str, Any]:
        state = state.copy()
        state.setdefault("routing_metadata", RoutingMetadata())
        state.setdefault("shared_memory_handles", SharedMemoryHandles())
        state.setdefault("resource_budget", ResourceBudget())
        state.setdefault("delegation_history", [])
        state.setdefault("shared_knowledge", {})
        state.setdefault("swarm_tasks", [])
        return state

    async def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Swarm Controller evaluating state...")
        state = self._ensure_metadata(state)

        response = await self.chain.ainvoke(state)
        next_node = getattr(response, "next_node", None) or response.get("next_node")
        instructions = getattr(response, "instructions", None) or response.get(
            "instructions"
        )
        rationale = getattr(response, "rationale", None) or response.get("rationale")

        routing_metadata = state["routing_metadata"]
        routing_metadata.update(
            {
                "current_node": "controller",
                "next_node": str(next_node),
                "instructions": str(instructions),
                "rationale": rationale,
            }
        )
        routing_metadata.setdefault("route_history", []).append(
            {"from": "controller", "to": str(next_node), "reason": rationale}
        )

        logger.info("Swarm Controller delegated to: %s", next_node)
        return {
            "next": str(next_node),
            "instructions": str(instructions),
            "routing_metadata": routing_metadata,
        }

    async def route_intent(self, query: str) -> str:
        state = {"messages": [HumanMessage(content=query)]}
        response = await self.chain.ainvoke(state)
        if hasattr(response, "next_node"):
            return str(response.next_node)
        return str(response.get("next_node", "FINISH"))

    async def execute_loop(
        self, initial_state: Dict[str, Any], nodes: Dict[str, Any]
    ) -> Dict[str, Any]:
        current_state = self._ensure_metadata(initial_state)
        current_state.setdefault("messages", [])

        await self._maybe_capture_intent(current_state)

        max_loops = self._resolve_budget(current_state).get("max_rounds", 10)
        loop_count = 0

        while loop_count < max_loops:
            decision = await self.__call__(current_state)
            next_node = decision["next"]
            instructions = decision["instructions"]

            if next_node == "FINISH":
                break

            if next_node in nodes:
                current_state["instructions"] = instructions
                specialist_node = nodes[next_node]
                result = await self.delegate_to_specialist(
                    next_node, current_state, specialist_node
                )

                summary = result.get("analysis_summary", "Task completed.")
                current_state["messages"].append(
                    AIMessage(content=f"[{next_node}]: {summary}")
                )
                current_state["delegation_history"].append(
                    {
                        "node": next_node,
                        "summary": summary,
                        "instructions": instructions,
                    }
                )
            else:
                logger.error("Specialist %s not found in nodes.", next_node)
                break

            loop_count += 1

        current_state["next"] = "FINISH"
        return current_state

    async def delegate_to_specialist(
        self, specialist_name: str, state: Dict[str, Any], specialist_node: Any
    ) -> Dict[str, Any]:
        logger.info("Delegating task to specialist: %s", specialist_name)
        adapter = self._adapt_node(specialist_node)
        result = await adapter(state)
        if isinstance(result, dict):
            return result
        return {"analysis_summary": str(result)}

    async def _maybe_capture_intent(self, state: Dict[str, Any]) -> None:
        if not self.router_agent:
            return
        routing_metadata = state.get("routing_metadata", {})
        if routing_metadata.get("intent"):
            return
        prompt = state.get("raw_prompt") or state.get("prompt")
        if not prompt:
            return
        try:
            intent = await self.router_agent.route(prompt)
        except Exception as exc:
            logger.warning("Intent routing failed: %s", exc)
            return
        routing_metadata["intent"] = intent.model_dump()

    def _resolve_budget(self, state: Dict[str, Any]) -> Dict[str, Any]:
        budget = state.get("resource_budget") or {}
        return {
            "max_rounds": budget.get("max_rounds", 10),
            "max_tokens": budget.get("max_tokens"),
            "max_cost": budget.get("max_cost"),
        }

    def _adapt_node(self, node: Any) -> Callable[[Dict[str, Any]], Any]:
        async def _invoke(state: Dict[str, Any]) -> Any:
            callable_target = node
            if hasattr(node, "__call__"):
                callable_target = node

            try:
                signature = inspect.signature(callable_target)
            except (TypeError, ValueError):
                signature = None

            if signature is None:
                result = callable_target()
                return await result if inspect.isawaitable(result) else result

            params = list(signature.parameters.values())
            if not params:
                result = callable_target()
                return await result if inspect.isawaitable(result) else result

            param_names = {param.name for param in params}
            if any(param.kind == param.VAR_KEYWORD for param in params):
                result = callable_target(**state)
                return await result if inspect.isawaitable(result) else result

            if "state" in param_names:
                arg = state
            elif "prompt" in param_names:
                arg = state.get("raw_prompt") or state.get("prompt")
            elif "query" in param_names:
                arg = state.get("raw_prompt") or state.get("prompt")
            elif "brief" in param_names:
                arg = state.get("brief")
            else:
                arg = state

            result = callable_target(arg)
            return await result if inspect.isawaitable(result) else result

        return _invoke
